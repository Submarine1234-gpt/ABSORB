"""
Calculation execution service
Manages background calculation tasks
"""
import threading
import subprocess
import sys
import os
from datetime import datetime


class CalculationService:
    """
    Manages calculation execution in background threads
    """
    
    def __init__(self, logger, file_service, session_service):
        """
        Initialize calculation service
        
        Args:
            logger: Logger instance
            file_service: FileService instance
            session_service: SessionService instance
        """
        self.logger = logger
        self.file_service = file_service
        self.session_service = session_service
    
    def run_calculation_async(self, session_id, params, surface_axis):
        """
        Run calculation in background thread
        
        Args:
            session_id: Session identifier
            params: Calculation parameters
            surface_axis: Surface axis value
        """
        thread = threading.Thread(
            target=self._background_calculation_task,
            args=(session_id, params, surface_axis)
        )
        thread.start()
    
    def _background_calculation_task(self, session_id, params, surface_axis):
        """
        Background task for running calculations
        
        Args:
            session_id: Session identifier
            params: Calculation parameters
            surface_axis: Surface axis value
        """
        result_dir = self.file_service.get_user_path('results', session_id)
        log_file = self.file_service.get_log_file_path(session_id)
        
        try:
            # Write initial log
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[SYSTEM] Starting calculation at {datetime.now()}\n")
                f.write(f"[SYSTEM] Session ID: {session_id}\n\n")
            
            # Run core calculation workflow
            self._run_workflow(params, log_file)
            
            # Create result ZIP
            zip_path, zip_name = self.file_service.create_result_zip(session_id, result_dir)
            
            # Add to session history
            self.session_service.add_result(session_id, {
                'session_id': session_id,
                'filename': zip_name,
                'surface_axis': surface_axis
            })
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n[SYSTEM] Results packaged successfully: {zip_name}\n")
            
            self.logger.info(f"Calculation {session_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Calculation {session_id} failed: {e}", exc_info=True)
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n[ERROR] Calculation failed: {str(e)}\n")
        
        finally:
            # Mark calculation as done
            self.file_service.mark_calculation_done(session_id)
    
    def _run_workflow(self, params, log_file):
        """
        Execute the workflow using workflow module
        
        Args:
            params: Calculation parameters
            log_file: Path to log file
        """
        # Import here to avoid circular dependencies
        from core import SurfaceAdsorptionWorkflow
        
        # Add session_id to params for logging
        workflow = SurfaceAdsorptionWorkflow(**params)
        
        # Redirect workflow output to log file
        # The workflow already logs to its own logger which writes to the log file
        workflow.run(
            substrate_path=params['substrate'],
            adsorbate_path=params['adsorbate']
        )
    
    def _run_core_script(self, params, log_file):
        """
        Alternative: Run calculation via external Python script (legacy method)
        
        Args:
            params: Calculation parameters
            log_file: Path to log file
        """
        python = sys.executable
        core_py = os.path.join(os.path.dirname(__file__), '..', '..', 'core.py')
        
        if not os.path.exists(core_py):
            # Use new workflow module instead
            return self._run_workflow(params, log_file)
        
        cmd = [python, core_py]
        
        # Convert parameters to command line arguments
        for k, v in params.items():
            if isinstance(v, bool):
                if v:
                    cmd.append(f'--{k}')
            elif v is not None:
                cmd.extend([f'--{k}', str(v)])
        
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[SYSTEM] Executing: {' '.join(cmd)}\n\n")
            f.flush()
            
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                env=env
            )
            
            for line in iter(proc.stdout.readline, ''):
                f.write(line)
                f.flush()
            
            proc.stdout.close()
            return_code = proc.wait()
            
            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, cmd)
