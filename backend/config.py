"""
Configuration module for ABSORB backend
Centralizes all configuration parameters to avoid hardcoding
"""
import os

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'user_uploads')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Application settings
MAX_RESULTS_PER_USER = 10
ALLOWED_EXTENSIONS = {'cif'}

# Calculation default parameters
DEFAULT_PARAMS = {
    'surface_axis': 2,
    'place_on_bottom': False,
    'adsorption_height': 2.0,
    'vacuum_thickness': 20.0,
    'surface_search_depth': 3.5,
    'collision_threshold': 1.2,
    'hollow_sites_enabled': True,
    'knn_neighbors': 2,
    'hollow_site_deduplication_distance': 1.5,
    'on_top_sites_enabled': True,
    'on_top_target_atom': 'O',
    'rotation_count': 50,
    'rotation_step': 30,
    'rotation_method': 'normal'  # String value: 'normal' or 'sphere'
}

# Flask settings
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
FLASK_DEBUG = True

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
