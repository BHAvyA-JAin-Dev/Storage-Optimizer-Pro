import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable, Optional
from core.app_manager import AppManager, AppInfo
from utils.storage_utils import StorageUtils

class AppUninstaller(tk.Frame):
    """Component for listing and deep deleting installed applications."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="white", highlightthickness=1, highlightbackground="#DDDDDD", **kwargs)
        self.app_manager = AppManager()
        self.apps: List[AppInfo] = []
        
        self._init_ui()
        self.refresh_apps()
        
    def _init_ui(self):
        """Initializes the app uninstaller UI components."""
        # Header / Refresh
        header_frame = tk.Frame(self, bg="#F5F5F5", height=40)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="Installed Applications", font=("Segoe UI", 10, "bold"), bg="#F5F5F5").pack(side="left", padx=10)
        
        self.refresh_btn = tk.Button(header_frame, text="🔄 Refresh List", command=self.refresh_apps, bg="#F5F5F5", relief="flat", font=("Segoe UI", 9))
        self.refresh_btn.pack(side="right", padx=10)
        
        # Treeview for app list
        columns = ("icon", "name", "size", "publisher", "delete")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="extended")
        
        # Define headings
        self.tree.heading("icon", text="", anchor="center")
        self.tree.heading("name", text="Name", anchor="w")
        self.tree.heading("size", text="Size", anchor="w")
        self.tree.heading("publisher", text="Publisher", anchor="w")
        self.tree.heading("delete", text="Action", anchor="center")
        
        # Define column widths
        self.tree.column("icon", width=40, anchor="center")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("size", width=100, anchor="w")
        self.tree.column("publisher", width=150, anchor="w")
        self.tree.column("delete", width=100, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bindings
        self.tree.bind("<ButtonRelease-1>", self._on_click)
        
    def refresh_apps(self):
        """Refreshes the list of installed apps."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.apps = self.app_manager.get_installed_apps()
        
        # Add apps to treeview
        for i, app in enumerate(self.apps):
            self.tree.insert("", "end", iid=str(i), values=(
                app.icon,
                app.name,
                StorageUtils.format_size(app.size) if app.size > 0 else "Unknown",
                app.publisher,
                "🗑️ Delete"
            ))
            
    def _on_click(self, event):
        """Handle clicking on the 'Delete' column."""
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
            
        column = self.tree.identify_column(event.x)
        if column == "#5": # 'delete' column
            idx = int(item_id)
            app = self.apps[idx]
            self._confirm_deep_delete(app, item_id)
            
    def _confirm_deep_delete(self, app: AppInfo, item_id: str):
        """Shows a confirmation dialog for deep deletion of an app."""
        from tkinter import messagebox
        if messagebox.askyesno("Deep Uninstall", f"Are you sure you want to deep delete '{app.name}'?\n\nThis will remove the application folder and its AppData remnants."):
            self.app_manager.deep_delete_app(app)
            # Optimistically remove from list
            self.tree.delete(item_id)
            messagebox.showinfo("Uninstall Started", f"The deep cleanup for '{app.name}' has started in the background.")
