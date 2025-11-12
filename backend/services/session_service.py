"""
Session management service
Handles user sessions and result history
"""
import threading
from collections import deque
from datetime import datetime


class SessionService:
    """
    Manages user sessions and calculation history
    """
    
    def __init__(self, max_results_per_user=10):
        """
        Initialize session service
        
        Args:
            max_results_per_user: Maximum number of results to keep per user
        """
        self.max_results_per_user = max_results_per_user
        self.user_results = {}
        self.lock = threading.Lock()
    
    def add_result(self, session_id, result_data):
        """
        Add a result to session history
        
        Args:
            session_id: Session identifier
            result_data: Dictionary containing result information
        """
        with self.lock:
            if session_id not in self.user_results:
                self.user_results[session_id] = deque(
                    maxlen=self.max_results_per_user + 1
                )
            
            # Add timestamp if not present
            if 'timestamp' not in result_data:
                result_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.user_results[session_id].append(result_data)
    
    def get_results(self, session_id=None):
        """
        Get results for a specific session or all sessions
        
        Args:
            session_id: Optional session identifier
            
        Returns:
            List of results
        """
        with self.lock:
            if session_id:
                return list(self.user_results.get(session_id, []))
            else:
                # Return all results from all sessions
                all_results = []
                for results in self.user_results.values():
                    all_results.extend(list(results))
                return list(reversed(all_results))
    
    def clear_session(self, session_id):
        """
        Clear results for a specific session
        
        Args:
            session_id: Session identifier
        """
        with self.lock:
            if session_id in self.user_results:
                del self.user_results[session_id]
    
    def get_session_count(self):
        """
        Get number of active sessions
        
        Returns:
            Number of sessions
        """
        with self.lock:
            return len(self.user_results)
