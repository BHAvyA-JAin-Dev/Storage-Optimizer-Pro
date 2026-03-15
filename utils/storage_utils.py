from typing import Tuple

class StorageUtils:
    """Utilities for storage-related calculations and formatting."""
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Formats bytes into a human-readable string (e.g., GB, MB)."""
        if size_bytes == 0:
            return "0 B"
        
        # Binary prefixes
        suffixes = ("B", "KB", "MB", "GB", "TB", "PB")
        i = 0
        while size_bytes >= 1024 and i < len(suffixes) - 1:
            size_bytes /= 1024.0
            i += 1
            
        f = ("%.2f" % size_bytes).rstrip('0').rstrip('.')
        return "%s %s" % (f, suffixes[i])

    @staticmethod
    def calculate_percentage(used: int, total: int) -> float:
        """Calculates percentage of used space."""
        if total == 0:
            return 0.0
        return (used / total) * 100.0

    @staticmethod
    def get_color_for_usage(percent: float) -> str:
        """Returns a color based on storage usage percentage."""
        if percent < 70:
            return "#4CAF50" # Green
        elif percent < 90:
            return "#FFC107" # Amber
        else:
            return "#F44336" # Red
