import tkinter as tk
from tkinter import ttk

class GlassStyles:
    """Styling utilities for glassmorphism effect in Tkinter."""
    
    # Colors
    GLASS_BG = "#F0F0F0" # Light grey background
    GLASS_OVERLAY = "#FFFFFF" # White for overlay
    GLASS_ACCENT = "#2196F3" # Blue accent
    TEXT_COLOR = "#333333" # Dark text
    
    @staticmethod
    def apply_styles():
        """Initializes and applies global ttk styles."""
        style = ttk.Style()
        
        # Main Window
        style.configure("TFrame", background=GlassStyles.GLASS_BG)
        style.configure("TLabel", background=GlassStyles.GLASS_BG, foreground=GlassStyles.TEXT_COLOR, font=("Segoe UI", 10))
        
        # Glass Frame Style
        style.configure("Glass.TFrame", background=GlassStyles.GLASS_OVERLAY, relief="flat")
        
        # Header Style
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=GlassStyles.GLASS_ACCENT)
        
        # Button Style
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=10)
        
        # List Style
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    @staticmethod
    def create_glass_frame(parent, **kwargs) -> tk.Frame:
        """Creates a frame that looks like a glass pane."""
        frame = tk.Frame(parent, bg=GlassStyles.GLASS_OVERLAY, bd=0, highlightthickness=1, highlightbackground="#DDDDDD", **kwargs)
        return frame
