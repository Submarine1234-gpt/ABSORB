"""
Validation utilities for input parameters and files
"""
import os
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions={'cif'}):
    """
    Check if file has an allowed extension
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions
        
    Returns:
        Boolean indicating if file is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_file_upload(file_obj):
    """
    Validate uploaded file
    
    Args:
        file_obj: File object from Flask request
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_obj:
        return False, "No file provided"
    
    if file_obj.filename == '':
        return False, "No file selected"
    
    if not allowed_file(file_obj.filename):
        return False, "Invalid file type. Only CIF files are allowed"
    
    return True, None


def validate_calculation_params(params):
    """
    Validate calculation parameters
    
    Args:
        params: Dictionary of calculation parameters
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_params = ['substrate', 'adsorbate', 'output_folder']
    
    for param in required_params:
        if param not in params or not params[param]:
            return False, f"Missing required parameter: {param}"
    
    # Validate numeric parameters
    numeric_validations = {
        'adsorption_height': (0.1, 10.0),
        'vacuum_thickness': (5.0, 50.0),
        'surface_search_depth': (0.5, 10.0),
        'collision_threshold': (0.5, 3.0),
        'knn_neighbors': (1, 10),
        'hollow_site_deduplication_distance': (0.1, 5.0),
        'rotation_count': (10, 200),
        'rotation_step': (1, 90)
    }
    
    for param, (min_val, max_val) in numeric_validations.items():
        if param in params:
            try:
                value = float(params[param])
                if not (min_val <= value <= max_val):
                    return False, f"{param} must be between {min_val} and {max_val}"
            except (ValueError, TypeError):
                return False, f"{param} must be a valid number"
    
    # Validate surface_axis
    if 'surface_axis' in params:
        try:
            axis = int(params['surface_axis'])
            if axis not in [0, 1, 2]:
                return False, "surface_axis must be 0, 1, or 2"
        except (ValueError, TypeError):
            return False, "surface_axis must be an integer"
    
    # Validate rotation_method
    if 'rotation_method' in params:
        if params['rotation_method'] not in ['normal', 'sphere']:
            return False, "rotation_method must be 'normal' or 'sphere'"
    
    return True, None


def sanitize_filename(filename):
    """
    Sanitize filename for security
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    return secure_filename(filename)
