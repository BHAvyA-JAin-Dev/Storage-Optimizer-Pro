import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable
from core.drive_manager import DriveManager
from utils.storage_utils import StorageUtils

class DriveSelector(tk.Frame):
    """Panel for drive selection and information display."""
    
    def __init__(self, parent, on_drive_selected: Callable[[str], None], **kwargs):
        super().__init__(parent, bg="#F0F0F0", **kwargs)
        self.on_drive_selected = on_drive_selected
        self.drives: List[Dict] = []
        self.selected_drive = tk.StringVar()
        
        self._init_ui()
        self.refresh_drives()
        
    def _init_ui(self):
        """Initializes the drive selector UI components."""
        # Header
        header = tk.Label(self, text="Select a Drive", font=("Segoe UI", 12, "bold"), bg="#F0F0F0", fg="#333333")
        header.pack(pady=(10, 5), anchor="w", padx=10)
        
        # Container for drive list
        self.drive_list_container = tk.Frame(self, bg="#F0F0F0")
        self.drive_list_container.pack(fill="both", expand=True, padx=10, pady=5)
        
    def refresh_drives(self):
        """Refreshes the list of detected drives."""
        # Clear existing drives
        for widget in self.drive_list_container.winfo_children():
            widget.destroy()
            
        self.drives = DriveManager.get_all_drives()
        
        if not self.drives:
            empty_label = tk.Label(self.drive_list_container, text="No drives detected", bg="#F0F0F0", fg="#757575")
            empty_label.pack(pady=20)
            return
            
        for drive in self.drives:
            self._create_drive_item(drive)
            
    def _create_drive_item(self, drive: Dict):
        """Creates a UI element for a single drive."""
        # Main Frame
        frame = tk.Frame(self.drive_list_container, bg="white", relief="flat", highlightthickness=1, highlightbackground="#DDDDDD", cursor="hand2")
        frame.pack(fill="x", pady=5)
        
        # Drive Letter/Icon
        icon_label = tk.Label(frame, text="🖴", font=("Segoe UI", 24), bg="white", fg="#2196F3")
        icon_label.pack(side="left", padx=10, pady=10)
        
        # Drive Info
        info_frame = tk.Frame(frame, bg="white")
        info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=10)
        
        name_label = tk.Label(info_frame, text=f"{drive['device']} ({drive['fstype']})", font=("Segoe UI", 10, "bold"), bg="white", fg="#333333")
        name_label.pack(anchor="w")
        
        usage_text = f"{StorageUtils.format_size(drive['used'])} / {StorageUtils.format_size(drive['total'])} used ({drive['percent']}%)"
        usage_label = tk.Label(info_frame, text=usage_text, font=("Segoe UI", 9), bg="white", fg="#757575")
        usage_label.pack(anchor="w")
        
        # Progress Bar
        progress_canvas = tk.Canvas(info_frame, height=5, bg="#E0E0E0", highlightthickness=0)
        progress_canvas.pack(fill="x", pady=(5, 0))
        
        # Draw usage bar
        bar_color = StorageUtils.get_color_for_usage(drive['percent'])
        bar_width = (drive['percent'] / 100.0) * 200 # Fixed width for bar
        progress_canvas.create_rectangle(0, 0, bar_width, 5, fill=bar_color, outline="")
        
        # Event bindings
        for widget in (frame, icon_label, info_frame, name_label, usage_label):
            widget.bind("<Button-1>", lambda e, d=drive['mountpoint']: self._on_item_click(d))
            widget.bind("<Enter>", lambda e, f=frame: f.config(bg="#F5F5F5"))
            widget.bind("<Leave>", lambda e, f=frame: f.config(bg="white"))
            
    def _on_item_click(self, mountpoint: str):
        """Callback when a drive is selected."""
        self.selected_drive.set(mountpoint)
        self.on_drive_selected(mountpoint)
