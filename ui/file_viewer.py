import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable, Optional
from core.scanner import ScannedFile
from utils.storage_utils import StorageUtils

class FileViewer(tk.Frame):
    """Component for displaying and selecting scanned files using Treeview for performance."""
    
    def __init__(self, parent, on_selection_changed: Callable[[int, int], None], **kwargs):
        super().__init__(parent, bg="white", highlightthickness=1, highlightbackground="#DDDDDD", **kwargs)
        self.on_selection_changed = on_selection_changed
        self.files: List[ScannedFile] = []
        self.selected_indices: set = set()
        
        self._init_ui()
        
    def _init_ui(self):
        """Initializes the file viewer UI components."""
        # Selection Summary / Header
        self.header_frame = tk.Frame(self, bg="#F5F5F5", height=40)
        self.header_frame.pack(fill="x")
        
        # Check All / Uncheck All buttons
        self.btn_select_all = tk.Button(self.header_frame, text="Select All", command=self._select_all, bg="#F5F5F5", relief="flat", font=("Segoe UI", 9))
        self.btn_select_all.pack(side="left", padx=5)
        
        self.btn_deselect_all = tk.Button(self.header_frame, text="Deselect All", command=self._deselect_all, bg="#F5F5F5", relief="flat", font=("Segoe UI", 9))
        self.btn_deselect_all.pack(side="left", padx=5)
        
        # Treeview for file list
        columns = ("selected", "name", "size", "category", "path")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="extended")
        
        # Define headings
        self.tree.heading("selected", text="[x]", anchor="center")
        self.tree.heading("name", text="Name", anchor="w")
        self.tree.heading("size", text="Size", anchor="w")
        self.tree.heading("category", text="Category", anchor="w")
        self.tree.heading("path", text="Path", anchor="w")
        
        # Define column widths
        self.tree.column("selected", width=40, anchor="center")
        self.tree.column("name", width=200, anchor="w")
        self.tree.column("size", width=80, anchor="w")
        self.tree.column("category", width=120, anchor="w")
        self.tree.column("path", width=400, anchor="w")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bindings
        self.tree.bind("<ButtonRelease-1>", self._on_click)
        
    def set_files(self, files: List[ScannedFile]):
        """Populates the list with scanned files."""
        self.files = files
        self.selected_indices = set()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.files:
            return
            
        # Add files to treeview
        for i, file in enumerate(self.files):
            # Using unicode characters for checkbox
            self.tree.insert("", "end", iid=str(i), values=(
                "☐", # Unchecked by default
                file.name,
                StorageUtils.format_size(file.size),
                file.category,
                file.path
            ))
            
        self._notify_selection()
            
    def _on_click(self, event):
        """Handle clicking on an item to toggle selection."""
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
            
        column = self.tree.identify_column(event.x)
        
        # Toggle selection for the clicked row
        idx = int(item_id)
        if idx in self.selected_indices:
            self.selected_indices.remove(idx)
            self.tree.set(item_id, "selected", "☐")
        else:
            self.selected_indices.add(idx)
            self.tree.set(item_id, "selected", "☑")
            
        self._notify_selection()
            
    def _select_all(self):
        """Selects all files in the list."""
        self.selected_indices = set(range(len(self.files)))
        for i in range(len(self.files)):
            self.tree.set(str(i), "selected", "☑")
        self._notify_selection()
        
    def _deselect_all(self):
        """Deselects all files in the list."""
        self.selected_indices = set()
        for i in range(len(self.files)):
            self.tree.set(str(i), "selected", "☐")
        self._notify_selection()
        
    def _notify_selection(self):
        """Notifies the parent about selection changes."""
        count = len(self.selected_indices)
        size = sum(self.files[i].size for i in self.selected_indices)
        self.on_selection_changed(count, size)

    def get_selected_files(self) -> List[ScannedFile]:
        """Returns the list of currently selected files."""
        return [self.files[i] for i in self.selected_indices]
