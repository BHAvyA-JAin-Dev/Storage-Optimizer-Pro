import os
import winreg
import logging
from typing import List, Dict, Optional
import shutil
import send2trash
import threading

class AppInfo:
    """Stores information about an installed application."""
    def __init__(self, name: str, icon: str = "📦", install_location: str = "", size: int = 0, publisher: str = ""):
        self.name = name
        self.icon = icon
        self.install_location = install_location
        self.size = size
        self.publisher = publisher

class AppManager:
    """Detects installed applications and handles their deep deletion."""
    
    def __init__(self):
        self.installed_apps: List[AppInfo] = []

    def get_installed_apps(self) -> List[AppInfo]:
        """Scans Windows Registry for installed applications."""
        self.installed_apps = []
        # Common registry keys for installed apps
        keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
        ]

        for hkey, subkey in keys:
            try:
                with winreg.OpenKey(hkey, subkey) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            app_subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, app_subkey_name) as app_key:
                                try:
                                    name = winreg.QueryValueEx(app_key, "DisplayName")[0]
                                    install_loc = winreg.QueryValueEx(app_key, "InstallLocation")[0]
                                    publisher = winreg.QueryValueEx(app_key, "Publisher")[0] if "Publisher" in self._get_values(app_key) else ""
                                    
                                    # Skip system updates and small components
                                    if not name or "Update" in name or name.startswith("Windows"):
                                        continue
                                        
                                    size = self._calculate_folder_size(install_loc) if install_loc and os.path.exists(install_loc) else 0
                                    
                                    self.installed_apps.append(AppInfo(name, "📦", install_loc, size, publisher))
                                except (OSError, IndexError):
                                    continue
                        except OSError:
                            continue
            except OSError:
                continue

        # Sort by name
        self.installed_apps.sort(key=lambda x: x.name)
        return self.installed_apps

    def _get_values(self, key) -> List[str]:
        """Helper to get all value names for a registry key."""
        values = []
        try:
            for i in range(winreg.QueryInfoKey(key)[1]):
                values.append(winreg.EnumValue(key, i)[0])
        except OSError:
            pass
        return values

    def _calculate_folder_size(self, path: str) -> int:
        """Calculates total size of a directory in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
        except (OSError, PermissionError):
            pass
        return total_size

    def deep_delete_app(self, app: AppInfo, callback: Optional[threading.Thread] = None):
        """
        Performs deep deletion of an application including its install folder and AppData.
        This is a background operation.
        """
        def _run_deep_delete():
            try:
                # 1. Delete main install location
                if app.install_location and os.path.exists(app.install_location):
                    logging.info(f"Deleting main folder: {app.install_location}")
                    send2trash.send2trash(app.install_location)

                # 2. Delete AppData remnants (common locations)
                app_name_slug = app.name.lower().replace(" ", "")
                app_data_locations = [
                    os.path.join(os.path.expandvars('%LOCALAPPDATA%'), app.name),
                    os.path.join(os.path.expandvars('%APPDATA%'), app.name),
                    os.path.join(os.path.expandvars('%LOCALAPPDATA%'), app_name_slug),
                    os.path.join(os.path.expandvars('%APPDATA%'), app_name_slug),
                ]

                for loc in app_data_locations:
                    if os.path.exists(loc):
                        logging.info(f"Deleting AppData remnant: {loc}")
                        send2trash.send2trash(loc)
                
                logging.info(f"Deep deletion of {app.name} completed.")
            except Exception as e:
                logging.error(f"Error during deep deletion of {app.name}: {str(e)}")

        thread = threading.Thread(target=_run_deep_delete)
        thread.daemon = True
        thread.start()
        return thread
