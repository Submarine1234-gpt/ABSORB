"""
ABSORB - Surface Adsorption Calculation Platform
Main Flask application
"""
import sys
import os
from pathlib import Path

# Add project backend directory to Python path
backend_dir = Path(__file__).parent.absolute()
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import uuid
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file, Response

from config import (
    BASE_DIR, UPLOAD_FOLDER, LOG_DIR, MAX_RESULTS_PER_USER,
    DEFAULT_PARAMS, FLASK_HOST, FLASK_PORT, FLASK_DEBUG
)
from utils import setup_logger, validate_file_upload, validate_calculation_params
from services import CalculationService, FileService, SessionService


# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Set up application logger
app_logger = setup_logger('ABSORB', os.path.join(LOG_DIR, 'app.log'))

# Initialize services
file_service = FileService(UPLOAD_FOLDER)
session_service = SessionService(MAX_RESULTS_PER_USER)
calculation_service = CalculationService(app_logger, file_service, session_service)


@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')


@app.route('/run-calculation', methods=['POST'])
def run_calculation():
    """
    Start a new calculation
    
    Request must include:
        - Files: substrate_file, adsorbate_file
        - Form data: calculation parameters
        
    Returns:
        JSON with success status and session_id
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        result_dir = file_service.get_user_path('results', session_id)
        log_file = file_service.get_log_file_path(session_id)
        
        # Initialize log file
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"[SYSTEM] Calculation session starting: {datetime.now()}\n")
            f.write(f"[SYSTEM] Session ID: {session_id}\n\n")
        
        # Validate and save uploaded files
        substrate_file = request.files.get('substrate_file')
        adsorbate_file = request.files.get('adsorbate_file')
        
        is_valid, error = validate_file_upload(substrate_file)
        if not is_valid:
            return jsonify({'success': False, 'message': f"Substrate file: {error}"}), 400
        
        is_valid, error = validate_file_upload(adsorbate_file)
        if not is_valid:
            return jsonify({'success': False, 'message': f"Adsorbate file: {error}"}), 400
        
        substrate_path = file_service.save_uploaded_file(substrate_file, result_dir)
        adsorbate_path = file_service.save_uploaded_file(adsorbate_file, result_dir)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[SYSTEM] Saved substrate to: {substrate_path}\n")
            f.write(f"[SYSTEM] Saved adsorbate to: {adsorbate_path}\n\n")
        
        # Build calculation parameters
        params = dict(DEFAULT_PARAMS)  # Start with defaults
        
        # Update with form parameters
        for key in request.form:
            value = request.form.get(key)
            if key in params:
                # Convert to appropriate type
                param_type = type(params[key])
                if param_type == bool:
                    params[key] = value.lower() in ('true', '1', 'yes')
                elif param_type == int:
                    params[key] = int(value)
                elif param_type == float:
                    params[key] = float(value)
                else:
                    params[key] = value
        
        # Handle checkbox parameters (present = True, absent = False)
        params['hollow_sites_enabled'] = 'hollow_sites_enabled' in request.form
        params['on_top_sites_enabled'] = 'on_top_sites_enabled' in request.form
        params['place_on_bottom'] = 'place_on_bottom' in request.form
        params['rotation_method'] = 'rotation_method' in request.form
        
        # Add file paths and output folder
        params.update({
            'substrate': substrate_path,
            'adsorbate': adsorbate_path,
            'output_folder': result_dir,
            'session_id': session_id
        })
        
        # Validate parameters
        is_valid, error = validate_calculation_params(params)
        if not is_valid:
            return jsonify({'success': False, 'message': error}), 400
        
        surface_axis = params.get('surface_axis', 2)
        
        # Start background calculation
        calculation_service.run_calculation_async(session_id, params, surface_axis)
        
        app_logger.info(f"Started calculation for session {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'surface_axis': surface_axis
        })
        
    except Exception as e:
        app_logger.error(f"Failed to start calculation: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/check-status/<session_id>')
def check_status(session_id):
    """
    Check calculation status
    
    Args:
        session_id: Session identifier
        
    Returns:
        JSON with status ('running' or 'complete')
    """
    is_done = file_service.check_calculation_done(session_id)
    status = 'complete' if is_done else 'running'
    return jsonify({'status': status})


@app.route('/stream-logs/<session_id>')
def stream_logs(session_id):
    """
    Stream calculation logs using Server-Sent Events
    
    Args:
        session_id: Session identifier
        
    Returns:
        SSE stream of log lines
    """
    log_file = file_service.get_log_file_path(session_id)
    
    def generate():
        # Wait for log file to exist
        while not os.path.exists(log_file):
            yield "data: [SYSTEM] Waiting for log file to be created...\n\n"
            time.sleep(1)
        
        # Stream log file contents
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            while True:
                line = f.readline()
                if not line:
                    # Check if calculation is done
                    if file_service.check_calculation_done(session_id):
                        yield "data: [SYSTEM] Log stream finished.\n\n"
                        break
                    time.sleep(0.2)
                    continue
                
                yield f"data: {line.strip()}\n\n"
    
    return Response(generate(), content_type='text/event-stream; charset=utf-8')


@app.route('/get-viz-data/<session_id>/<filename>')
def get_viz_data(session_id, filename):
    """
    Get visualization data file
    
    Args:
        session_id: Session identifier
        filename: Name of data file
        
    Returns:
        JSON file or error
    """
    # Whitelist allowed files
    allowed_files = ['adsorption_sites.json', 'surface_atoms.json']
    
    if filename not in allowed_files:
        return jsonify({'error': 'Invalid data file requested'}), 400
    
    file_path = file_service.get_visualization_file_path(session_id, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': f'{filename} not available or still generating'}), 404
    
    try:
        return send_file(file_path)
    except Exception as e:
        app_logger.error(f"Failed to serve {file_path}: {e}", exc_info=True)
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/get-results')
def get_results():
    """
    Get all calculation results
    
    Returns:
        JSON list of results
    """
    results = session_service.get_results()
    return jsonify(results)


@app.route('/download-result/<session_id>')
def download_result(session_id):
    """
    Download calculation results as ZIP
    
    Args:
        session_id: Session identifier
        
    Returns:
        ZIP file download
    """
    zip_path = os.path.join(file_service.get_user_path('zips'), f"results_{session_id}.zip")
    
    if not os.path.exists(zip_path):
        return "Result file not found.", 404
    
    return send_file(zip_path, as_attachment=True)


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ABSORB',
        'active_sessions': session_service.get_session_count()
    })


@app.route('/api/visualization/<session_id>/surface_mesh.json')
def get_surface_mesh(session_id):
    """
    Get surface mesh data for 3D visualization
    
    Args:
        session_id: Session identifier
        
    Returns:
        JSON mesh data or error
    """
    try:
        result_dir = file_service.get_user_path('results', session_id)
        mesh_file = os.path.join(result_dir, 'surface_mesh.json')
        
        # Check if mesh file exists
        if os.path.exists(mesh_file):
            return send_file(mesh_file, mimetype='application/json')
        
        # Try to generate mesh if it doesn't exist
        from core.surface_mesh import generate_surface_mesh_from_results
        
        # Get surface axis from session (default to 2/Z-axis)
        surface_axis = 2  # Could be stored with session data
        
        mesh_data = generate_surface_mesh_from_results(result_dir, surface_axis)
        
        if mesh_data is None:
            return jsonify({'error': 'Unable to generate surface mesh'}), 404
        
        return jsonify(mesh_data)
        
    except Exception as e:
        app_logger.error(f"Failed to get surface mesh for {session_id}: {e}", exc_info=True)
        return jsonify({'error': f'Failed to get surface mesh: {str(e)}'}), 500


@app.route('/api/mesh/generate', methods=['POST'])
def generate_mesh():
    """
    Generate surface mesh for a session
    
    Request body:
        - session_id: Session identifier
        - surface_axis: Surface axis (optional, default 2)
        - max_edge_length: Maximum edge length (optional)
        
    Returns:
        JSON with mesh generation status
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        surface_axis = data.get('surface_axis', 2)
        max_edge_length = data.get('max_edge_length', 10.0)
        
        if not session_id:
            return jsonify({'success': False, 'message': 'session_id required'}), 400
        
        result_dir = file_service.get_user_path('results', session_id)
        
        if not os.path.exists(result_dir):
            return jsonify({'success': False, 'message': 'Session not found'}), 404
        
        from core.surface_mesh import generate_surface_mesh_from_results
        
        mesh_data = generate_surface_mesh_from_results(result_dir, surface_axis)
        
        if mesh_data is None:
            return jsonify({
                'success': False,
                'message': 'Failed to generate mesh - insufficient data'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Mesh generated successfully',
            'mesh_stats': {
                'vertices': mesh_data['metadata']['vertex_count'],
                'triangles': mesh_data['metadata']['triangle_count']
            }
        })
        
    except Exception as e:
        app_logger.error(f"Mesh generation failed: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Run Flask app
    app_logger.info(f"Starting ABSORB server on {FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG, threaded=True)
