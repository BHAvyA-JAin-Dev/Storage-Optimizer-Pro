import os
import shutil
import send2trash
import logging
from typing import List, Callable, Optional
import threading

class FileDeleter:
    """Handles file deletion using send2trash for safety."""
    
    def __init__(self, callback: Optional[Callable[[str, bool], None]] = None):
        """
        Initializes the FileDeleter.
        
        Args:
            callback: Optional callback function (path, success) to notify UI.
        """
        self.callback = callback
        self._stop_requested = False
        self._is_deleting = False
        self._lock = threading.Lock()
        
    def delete_files(self, file_paths: List[str]):
        """Starts a background deletion process for a list of file paths."""
        self._is_deleting = True
        self._stop_requested = False
        
        delete_thread = threading.Thread(target=self._run_deletion, args=(file_paths,))
        delete_thread.daemon = True
        delete_thread.start()
        
    def _run_deletion(self, file_paths: List[str]):
        """Internal deletion logic using send2trash."""
        try:
            logging.info(f"Starting deletion of {len(file_paths)} files.")
            
            for path in file_paths:
                if self._stop_requested: break
                
                success = False
                try:
                    if os.path.exists(path):
                        send2trash.send2trash(path)
                        success = True
                        logging.info(f"Successfully moved to Recycle Bin: {path}")
                    else:
                        logging.warning(f"File not found during deletion: {path}")
                except Exception as e:
                    logging.error(f"Error deleting file {path}: {str(e)}")
                
                if self.callback:
                    self.callback(path, success)
                    
            logging.info("Deletion process completed.")
        except Exception as e:
            logging.error(f"Error during deletion process: {str(e)}")
        finally:
            self._is_deleting = False
            
    def stop(self):
        """Request the deletion process to stop."""
        self._stop_requested = True
        
    def is_deleting(self) -> bool:
        """Returns True if a deletion is currently running."""
        return self._is_deleting
