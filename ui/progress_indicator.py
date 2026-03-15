import tkinter as tk
import math
from typing import Optional

class ProgressIndicator(tk.Canvas):
    """Circular progress indicator with percentage display in the center."""
    
    def __init__(self, parent, size: int = 150, color: str = "#2196F3", bg_color: str = "#E0E0E0", **kwargs):
        super().__init__(parent, width=size, height=size, bg="white", highlightthickness=0, **kwargs)
        self.size = size
        self.color = color
        self.bg_color = bg_color
        self.percent = 0
        self._is_running = False
        self.angle = 0
        
        self.center = size // 2
        self.radius = (size // 2) - 15
        
    def start(self):
        """Starts the spinning animation (for indeterminate state)."""
        if self._is_running:
            return
        self._is_running = True
        self._animate_spin()
        
    def stop(self):
        """Stops the animation."""
        self._is_running = False
        self.delete("all")
        
    def set_progress(self, percent: float, status_text: str = ""):
        """Updates the progress percentage and redraws the circle."""
        self.percent = max(0, min(100, percent))
        self.delete("all")
        
        # Draw background circle
        self.create_oval(
            self.center - self.radius, self.center - self.radius,
            self.center + self.radius, self.center + self.radius,
            outline=self.bg_color, width=8
        )
        
        # Draw progress arc
        extent = -(self.percent / 100.0) * 359.9 # Use 359.9 to avoid full circle disappearing
        self.create_arc(
            self.center - self.radius, self.center - self.radius,
            self.center + self.radius, self.center + self.radius,
            start=90, extent=extent,
            outline=self.color, width=8, style=tk.ARC
        )
        
        # Draw percentage text
        self.create_text(
            self.center, self.center,
            text=f"{int(self.percent)}%",
            font=("Segoe UI", 18, "bold"),
            fill=self.color
        )

        if status_text:
            self.create_text(
                self.center, self.center + 25,
                text=status_text,
                font=("Segoe UI", 8),
                fill="#757575"
            )
            
    def show_success(self):
        """Shows a success state (100% and green color)."""
        self.color = "#4CAF50" # Green
        self.set_progress(100, "Success!")

    def _animate_spin(self):
        """Internal spinning animation for indeterminate progress."""
        if not self._is_running:
            return
            
        self.delete("all")
        
        # Draw spinning arc
        self.create_arc(
            self.center - self.radius, self.center - self.radius,
            self.center + self.radius, self.center + self.radius,
            start=self.angle, extent=120,
            outline=self.color, width=8, style=tk.ARC
        )
        
        self.angle = (self.angle + 8) % 360
        self.after(20, self._animate_spin)
