import sys
import logging
import os
from ui.main_window import MainWindow

def setup_logging():
    """Configures application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("storage_optimizer.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main application entry point. This is the central controller for the app."""
    # Ensure working directory is correct
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Initialize logging
    setup_logging()
    logging.info("Starting Storage Optimizer Pro...")
    
    try:
        # Create and run the main window
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        logging.error(f"Critical error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
