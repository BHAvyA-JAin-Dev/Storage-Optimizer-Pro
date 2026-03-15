from typing import List, Dict, Set
import logging
from .scanner import ScannedFile

class FileAnalyzer:
    """Categorizes scanned files and calculates statistics."""
    
    @staticmethod
    def categorize_files(files: List[ScannedFile]) -> Dict[str, List[ScannedFile]]:
        """Groups scanned files by their category."""
        categorized = {}
        for file in files:
            if file.category not in categorized:
                categorized[file.category] = []
            categorized[file.category].append(file)
        return categorized

    @staticmethod
    def calculate_stats(files: List[ScannedFile]) -> Dict[str, any]:
        """Calculates total size and count for a list of files."""
        total_size = sum(file.size for file in files)
        count = len(files)
        
        # Breakdown by category
        categories = FileAnalyzer.categorize_files(files)
        category_stats = {}
        for cat, cat_files in categories.items():
            category_stats[cat] = {
                'size': sum(f.size for f in cat_files),
                'count': len(cat_files)
            }
            
        return {
            'total_size': total_size,
            'total_count': count,
            'category_stats': category_stats
        }

    @staticmethod
    def filter_by_size(files: List[ScannedFile], min_size_bytes: int) -> List[ScannedFile]:
        """Filters files that are larger than the specified minimum size."""
        return [f for f in files if f.size >= min_size_bytes]

    @staticmethod
    def sort_by_size(files: List[ScannedFile], reverse: bool = True) -> List[ScannedFile]:
        """Sorts files by size."""
        return sorted(files, key=lambda f: f.size, reverse=reverse)
