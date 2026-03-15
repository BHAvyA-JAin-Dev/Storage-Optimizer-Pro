import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Dict, Optional
import logging
import os
from .drive_selector import DriveSelector
from .file_viewer import FileViewer
from .progress_indicator import ProgressIndicator
from .app_uninstaller import AppUninstaller
from core.scanner import FileScanner, ScannedFile
from core.deleter import FileDeleter
from core.drive_manager import DriveManager
from utils.storage_utils import StorageUtils

class MainWindow(tk.Tk):
    """Main application window for Storage Optimizer Pro."""
    
    def __init__(self):
        super().__init__()
        self.title("Storage Optimizer Pro")
        self.geometry("1000x750")
        self.configure(bg="#F0F0F0")
        
        # Core Components
        self.scanner = FileScanner(callback=self._on_file_found)
        self.deleter = FileDeleter(callback=self._on_file_deleted)
        
        # State
        self.selected_drive: Optional[str] = None
        self.found_files: List[ScannedFile] = []
        self.selected_count: int = 0
        self.selected_size: int = 0
        self.initial_drive_usage: Optional[Dict] = None
        
        self._init_ui()
        
    def _init_ui(self):
        """Initializes the main window UI components."""
        # Top Header (Glass-like)
        header_frame = tk.Frame(self, bg="#FFFFFF", height=80, highlightthickness=1, highlightbackground="#DDDDDD")
        header_frame.pack(fill="x", side="top")
        
        tk.Label(header_frame, text="Storage Optimizer Pro", font=("Segoe UI", 18, "bold"), bg="#FFFFFF", fg="#2196F3").pack(side="left", padx=20, pady=20)
        
        # Selection Summary
        self.summary_label = tk.Label(header_frame, text="0 files selected (0 B)", font=("Segoe UI", 10), bg="#FFFFFF", fg="#757575")
        self.summary_label.pack(side="right", padx=20)
        
        # Tabbed Layout
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- TAB 1: Disk Cleanup ---
        cleanup_tab = tk.Frame(self.tabs, bg="#F0F0F0")
        self.tabs.add(cleanup_tab, text="Disk Cleanup")
        
        # Left Panel (Drive Selection)
        self.drive_selector = DriveSelector(cleanup_tab, on_drive_selected=self._on_drive_selected, width=250)
        self.drive_selector.pack(side="left", fill="y", padx=(0, 20))
        
        # Right Panel (File Viewer)
        right_panel = tk.Frame(cleanup_tab, bg="#F0F0F0")
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Control Buttons
        btn_frame = tk.Frame(right_panel, bg="#F0F0F0")
        btn_frame.pack(fill="x", pady=(0, 10))
        
        self.scan_btn = tk.Button(
            btn_frame, text="🔍 Scan Now", font=("Segoe UI", 10, "bold"), 
            bg="#2196F3", fg="white", padx=20, pady=10, relief="flat",
            command=self._start_scan, state="disabled"
        )
        self.scan_btn.pack(side="left")
        
        self.delete_btn = tk.Button(
            btn_frame, text="🗑️ Clean Selected", font=("Segoe UI", 10, "bold"), 
            bg="#F44336", fg="white", padx=20, pady=10, relief="flat",
            command=self._confirm_deletion, state="disabled"
        )
        self.delete_btn.pack(side="left", padx=10)
        
        # File Viewer
        self.file_viewer = FileViewer(right_panel, on_selection_changed=self._on_selection_changed)
        self.file_viewer.pack(fill="both", expand=True)
        
        # --- TAB 2: App Uninstaller ---
        app_tab = tk.Frame(self.tabs, bg="#F0F0F0")
        self.tabs.add(app_tab, text="App Uninstaller")
        
        self.app_uninstaller = AppUninstaller(app_tab)
        self.app_uninstaller.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- OVERLAYS ---
        # Combined Progress Overlay
        self.overlay = tk.Frame(self, bg="white")
        self.progress_indicator = ProgressIndicator(self.overlay, size=200)
        self.progress_indicator.pack(pady=40)
        self.status_label = tk.Label(self.overlay, text="Initializing...", font=("Segoe UI", 12, "bold"), bg="white", fg="#333333")
        self.status_label.pack()
        
    def _on_drive_selected(self, mountpoint: str):
        """Callback when a drive is selected."""
        self.selected_drive = mountpoint
        self.scan_btn.config(state="normal")
        # Capture current usage for before/after comparison
        self.initial_drive_usage = DriveManager.get_drive_usage(mountpoint)
        logging.info(f"Drive selected: {mountpoint} (Used: {StorageUtils.format_size(self.initial_drive_usage['used'])})")
        
    def _start_scan(self):
        """Starts the scanning process."""
        if not self.selected_drive: return
        
        self._show_overlay("Scanning Drive...")
        self.found_files = []
        self.scanner.scan(self.selected_drive)
        self._update_scan_progress()
        
    def _update_scan_progress(self):
        """Updates the progress bar during scan (Indeterminate for scan)."""
        if self.scanner.is_scanning():
            # For scanning we just show indeterminate spin since total files unknown
            self.progress_indicator.start()
            self.after(100, self._update_scan_progress)
        else:
            self.progress_indicator.stop()
            self._hide_overlay()
            self.found_files = self.scanner.scanned_files
            self.file_viewer.set_files(self.found_files)
            if self.found_files:
                self.delete_btn.config(state="normal")
            else:
                messagebox.showinfo("Scan Complete", "No useless files found on this drive.")
                
    def _on_file_found(self, file: ScannedFile):
        """Callback from scanner when a file is found."""
        pass
        
    def _on_selection_changed(self, count: int, size: int):
        """Callback from file viewer when selection changes."""
        self.selected_count = count
        self.selected_size = size
        self.summary_label.config(text=f"{count} files selected ({StorageUtils.format_size(size)})")
        self.delete_btn.config(state="normal" if count > 0 else "disabled")
        
    def _confirm_deletion(self):
        """Shows a confirmation dialog before deleting files."""
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to move {self.selected_count} files ({StorageUtils.format_size(self.selected_size)}) to the Recycle Bin?"):
            self._start_deletion()
            
    def _start_deletion(self):
        """Starts the deletion process."""
        selected_files = self.file_viewer.get_selected_files()
        self.paths_to_delete = [f.path for f in selected_files]
        self.total_to_delete = len(self.paths_to_delete)
        self.deleted_count = 0
        
        self._show_overlay("Recycling Files...")
        self.progress_indicator.stop() # Stop spin
        self.progress_indicator.set_progress(0) # Switch to determinate
        
        self.deleter.delete_files(self.paths_to_delete)
        self._update_deletion_progress()
        
    def _update_deletion_progress(self):
        """Updates the progress bar during deletion."""
        if self.deleter.is_deleting():
            percent = (self.deleted_count / self.total_to_delete) * 100 if self.total_to_delete > 0 else 0
            self.progress_indicator.set_progress(percent, f"{self.deleted_count}/{self.total_to_delete}")
            self.after(100, self._update_deletion_progress)
        else:
            self.progress_indicator.show_success()
            self.after(1000, self._show_cleanup_summary)
            
    def _show_cleanup_summary(self):
        """Shows final success summary with storage comparison."""
        self._hide_overlay()
        
        current_usage = DriveManager.get_drive_usage(self.selected_drive)
        recovered = self.initial_drive_usage['used'] - current_usage['used']
        
        summary = (
            f"Successfully cleaned up files!\n\n"
            f"Before: {StorageUtils.format_size(self.initial_drive_usage['used'])} used\n"
            f"After: {StorageUtils.format_size(current_usage['used'])} used\n"
            f"Recovered: {StorageUtils.format_size(max(0, recovered))}"
        )
        
        messagebox.showinfo("Cleanup Complete", summary)
        
        # Refresh drive info and clear file list
        self.drive_selector.refresh_drives()
        self.file_viewer.set_files([])
        self.delete_btn.config(state="disabled")
        self.summary_label.config(text="0 files selected (0 B)")
            
    def _on_file_deleted(self, path: str, success: bool):
        """Callback from deleter for each file."""
        self.deleted_count += 1
        
    def _show_overlay(self, message: str):
        """Shows the progress overlay."""
        self.status_label.config(text=message)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.update()
        
    def _hide_overlay(self):
        """Hides the progress overlay."""
        self.progress_indicator.stop()
        self.overlay.place_forget()
        self.update()
