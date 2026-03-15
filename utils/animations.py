import tkinter as tk
import time
import math
from typing import Callable, Any

class UIAnimations:
    """Animation helpers for Tkinter UI components."""
    
    @staticmethod
    def animate_fade_in(widget: tk.Widget, duration_ms: int = 500, start_alpha: float = 0.0, end_alpha: float = 1.0):
        """Animates a fade-in effect (only works on Windows with transparency)."""
        if not widget.winfo_exists():
            return
            
        def _fade(current_alpha: float):
            if current_alpha >= end_alpha:
                widget.attributes("-alpha", end_alpha)
                return
            
            widget.attributes("-alpha", current_alpha)
            widget.after(20, _fade, current_alpha + 0.05)
            
        _fade(start_alpha)

    @staticmethod
    def animate_progress_spinner(canvas: tk.Canvas, center_x: int, center_y: int, radius: int, color: str = "#2196F3"):
        """Animates a simple circular progress spinner on a canvas."""
        if not canvas.winfo_exists():
            return
            
        def _spin(angle: float):
            canvas.delete("spinner")
            
            # Draw a rotating arc
            canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=angle, extent=60,
                outline=color, width=3, style=tk.ARC, tags="spinner"
            )
            
            canvas.after(20, _spin, (angle + 10) % 360)
            
        _spin(0)

    @staticmethod
    def animate_bar_chart(canvas: tk.Canvas, x: int, y: int, width: int, height: int, target_percent: float, color: str = "#2196F3"):
        """Animates a horizontal bar chart growing to a target percentage."""
        if not canvas.winfo_exists():
            return
            
        def _grow(current_percent: float):
            if current_percent >= target_percent:
                current_percent = target_percent
            
            canvas.delete("bar")
            
            # Background
            canvas.create_rectangle(x, y, x + width, y + height, fill="#E0E0E0", outline="", tags="bar_bg")
            
            # Progress bar
            bar_width = (current_percent / 100.0) * width
            canvas.create_rectangle(x, y, x + bar_width, y + height, fill=color, outline="", tags="bar")
            
            if current_percent < target_percent:
                canvas.after(10, _grow, current_percent + 2.0)
                
        _grow(0.0)
