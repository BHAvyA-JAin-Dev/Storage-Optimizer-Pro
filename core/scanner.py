import os
import pathlib
import threading
import logging
from typing import List, Dict, Set, Callable
from dataclasses import dataclass

@dataclass
class ScannedFile:
    """Represents a file found during scanning."""
    path: str
    name: str
    size: int
    category: str
    last_modified: float

class FileScanner:
    """Scans drives for useless files and categorizes them."""
    
    def __init__(self, callback: Callable[[ScannedFile], None] = None):
        self.callback = callback
        self.scanned_files: List[ScannedFile] = []
        self._stop_requested = False
        self._is_scanning = False
        self._lock = threading.Lock()
        
        # Patterns for common junk files
        self.junk_patterns = {
            '*.tmp': 'Temporary Files',
            '*.temp': 'Temporary Files',
            '*.log': 'Logs',
            '*.old': 'System Junk',
            '*.bak': 'System Junk',
            '*.chk': 'System Junk',
            'thumbs.db': 'Cache',
            'desktop.ini': 'System Junk',
        }
        
        # Directories that typically contain junk
        self.junk_dir_names = {'temp', 'tmp', 'cache', 'logs', 'prefetch', 'minidump', '$recycle.bin'}

    def stop(self):
        """Request the scanner to stop."""
        self._stop_requested = True
        
    def is_scanning(self) -> bool:
        """Returns True if a scan is currently running."""
        return self._is_scanning
        
    def scan(self, drive_path: str):
        """Starts a background scan of the specified drive."""
        self._is_scanning = True
        self._stop_requested = False
        self.scanned_files = []
        
        scan_thread = threading.Thread(target=self._run_scan, args=(drive_path,))
        scan_thread.daemon = True
        scan_thread.start()
        
    def _run_scan(self, drive_path: str):
        """Internal scan logic."""
        try:
            logging.info(f"Starting scan on drive: {drive_path}")
            
            # Use os.walk to find junk across the entire drive
            for root, dirs, files in os.walk(drive_path):
                if self._stop_requested: break
                
                # Check if current directory is a known junk directory
                current_dir_name = os.path.basename(root).lower()
                is_junk_dir = current_dir_name in self.junk_dir_names
                
                for file_name in files:
                    if self._stop_requested: break
                    
                    file_lower = file_name.lower()
                    category = None
                    
                    # Match by pattern
                    import fnmatch
                    for pattern, cat in self.junk_patterns.items():
                        if fnmatch.fnmatch(file_lower, pattern):
                            category = cat
                            break
                    
                    # If in a junk dir, categorize it even if no pattern matches
                    if not category and is_junk_dir:
                        if 'temp' in current_dir_name or 'tmp' in current_dir_name:
                            category = 'Temporary Files'
                        elif 'cache' in current_dir_name:
                            category = 'Cache'
                        elif 'log' in current_dir_name:
                            category = 'Logs'
                        elif '$recycle.bin' in current_dir_name:
                            category = 'Recycle Bin'
                        else:
                            category = 'System Junk'
                    
                    if category:
                        file_path = os.path.join(root, file_name)
                        try:
                            # Basic check to avoid system critical files if scanning C:\
                            if drive_path.upper().startswith('C:'):
                                if 'Windows\\System32' in file_path or 'Windows\\WinSxS' in file_path:
                                    continue

                            file_stat = os.stat(file_path)
                            scanned_file = ScannedFile(
                                path=file_path,
                                name=file_name,
                                size=file_stat.st_size,
                                category=category,
                                last_modified=file_stat.st_mtime
                            )
                            
                            with self._lock:
                                self.scanned_files.append(scanned_file)
                            
                            if self.callback:
                                self.callback(scanned_file)
                                
                        except (PermissionError, OSError):
                            continue
            
            logging.info(f"Scan completed. Found {len(self.scanned_files)} files.")
        except Exception as e:
            logging.error(f"Error during scan: {str(e)}")
        finally:
            self._is_scanning = False
            
    def _scan_directory(self, directory: str, category: str):
        """Scans a directory for files in a specific category."""
        try:
            patterns = self.categories[category].get('patterns', [])
            
            for root, dirs, files in os.walk(directory):
                if self._stop_requested: return
                
                for file_name in files:
                    if self._stop_requested: return
                    
                    # Filter by patterns if any
                    match = False
                    if not patterns:
                        match = True
                    else:
                        import fnmatch
                        for pattern in patterns:
                            if fnmatch.fnmatch(file_name.lower(), pattern.lower()):
                                match = True
                                break
                    
                    if not match:
                        continue
                        
                    file_path = os.path.join(root, file_name)
                    try:
                        file_stat = os.stat(file_path)
                        scanned_file = ScannedFile(
                            path=file_path,
                            name=file_name,
                            size=file_stat.st_size,
                            category=category,
                            last_modified=file_stat.st_mtime
                        )
                        
                        with self._lock:
                            self.scanned_files.append(scanned_file)
                        
                        if self.callback:
                            self.callback(scanned_file)
                            
                    except (PermissionError, OSError):
                        # Skip files we can't access
                        continue
                        
        except Exception as e:
            logging.error(f"Error scanning directory {directory}: {str(e)}")
