import psutil
from typing import List, Dict
import os

class DriveManager:
    """Manages drive detection and information gathering."""
    
    @staticmethod
    def get_all_drives() -> List[Dict[str, any]]:
        """
        Detects all local drives and returns their details.
        
        Returns:
            List[Dict]: A list of dictionaries containing drive info:
                - device: Drive name/letter (e.g., 'C:\\')
                - mountpoint: Mount point path
                - fstype: File system type (e.g., 'NTFS')
                - total: Total capacity in bytes
                - used: Used space in bytes
                - free: Free space in bytes
                - percent: Percentage of space used
        """
        drives = []
        partitions = psutil.disk_partitions(all=False)
        
        for partition in partitions:
            # Filter for local fixed drives (skip CD-ROMs, etc. if possible)
            if os.name == 'nt':
                if 'cdrom' in partition.opts or partition.fstype == '':
                    continue
            
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                drive_info = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
                drives.append(drive_info)
            except (PermissionError, OSError):
                # Skip drives that are not accessible (e.g., empty SD card slots)
                continue
                
        return drives

    @staticmethod
    def get_drive_usage(path: str) -> Dict[str, any]:
        """Gets current usage for a specific path."""
        try:
            usage = psutil.disk_usage(path)
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
        except Exception:
            return None
