class Constants:
    """App-wide constants and configurations."""
    
    # App Information
    APP_NAME = "Storage Optimizer Pro"
    APP_VERSION = "1.0.0"
    
    # UI Dimensions
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700
    
    # Glassmorphism Colors
    GLASS_BG = "#FFFFFF" # Base background (e.g., white)
    GLASS_TRANSPARENCY = 0.8
    GLASS_BLUR = 20 # Note: Blur in Tkinter is tricky, but we'll try
    
    # Theme Colors
    PRIMARY_COLOR = "#3F51B5" # Indigo
    ACCENT_COLOR = "#00BCD4" # Cyan
    TEXT_COLOR = "#212121" # Dark Grey
    TEXT_COLOR_SECONDARY = "#757575" # Medium Grey
    
    # File Categories
    CATEGORIES = {
        'Temporary Files': '#FF9800', # Orange
        'Logs': '#9C27B0', # Purple
        'Cache': '#2196F3', # Blue
        'Recycle Bin': '#F44336' # Red
    }
    
    # Scan Interval (ms)
    SCAN_UI_UPDATE_INTERVAL = 100
    
    # File size limits (if any)
    MAX_FILE_SIZE_DISPLAY = 10 * 1024 * 1024 * 1024 # 10 GB
