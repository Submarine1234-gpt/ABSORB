"""
File management service
Handles file uploads, downloads, and packaging
"""
import os
import zipfile
from werkzeug.utils import secure_filename


class FileService:
    """
    Manages file operations for the application
    """
    
    def __init__(self, base_upload_folder):
        """
        Initialize file service
        
        Args:
            base_upload_folder: Base directory for file uploads
        """
        self.base_upload_folder = base_upload_folder
        os.makedirs(base_upload_folder, exist_ok=True)
    
    def get_user_path(self, subfolder, session_id=None):
        """
        Get path for user-specific folder
        
        Args:
            subfolder: Subfolder name ('results', 'zips', etc.)
            session_id: Optional session identifier
            
        Returns:
            Path to folder
        """
        if session_id:
            path = os.path.join(self.base_upload_folder, subfolder, session_id)
        else:
            path = os.path.join(self.base_upload_folder, subfolder)
        
        os.makedirs(path, exist_ok=True)
        return path
    
    def save_uploaded_file(self, file_obj, destination_path):
        """
        Save uploaded file to destination
        
        Args:
            file_obj: File object from Flask request
            destination_path: Destination path
            
        Returns:
            Path to saved file
        """
        filename = secure_filename(file_obj.filename)
        file_path = os.path.join(destination_path, filename)
        file_obj.save(file_path)
        return file_path
    
    def create_result_zip(self, session_id, result_dir):
        """
        Create a ZIP archive of calculation results
        
        Args:
            session_id: Session identifier
            result_dir: Directory containing results
            
        Returns:
            Path to created ZIP file
        """
        zip_dir = self.get_user_path('zips')
        zip_name = f"results_{session_id}.zip"
        zip_path = os.path.join(zip_dir, zip_name)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(result_dir):
                for file in files:
                    # Skip marker files
                    if file.endswith('.done'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, result_dir)
                    zipf.write(file_path, arcname)
        
        return zip_path, zip_name
    
    def check_calculation_done(self, session_id):
        """
        Check if calculation is complete
        
        Args:
            session_id: Session identifier
            
        Returns:
            Boolean indicating completion status
        """
        result_dir = self.get_user_path('results', session_id)
        done_file = os.path.join(result_dir, '.done')
        return os.path.exists(done_file)
    
    def mark_calculation_done(self, session_id):
        """
        Mark calculation as complete
        
        Args:
            session_id: Session identifier
        """
        result_dir = self.get_user_path('results', session_id)
        done_file = os.path.join(result_dir, '.done')
        with open(done_file, 'w') as f:
            f.write('done')
    
    def get_log_file_path(self, session_id):
        """
        Get path to calculation log file
        
        Args:
            session_id: Session identifier
            
        Returns:
            Path to log file
        """
        result_dir = self.get_user_path('results', session_id)
        return os.path.join(result_dir, 'calculation.log')
    
    def get_visualization_file_path(self, session_id, filename):
        """
        Get path to visualization data file
        
        Args:
            session_id: Session identifier
            filename: Name of visualization file
            
        Returns:
            Path to file
        """
        result_dir = self.get_user_path('results', session_id)
        return os.path.join(result_dir, filename)
