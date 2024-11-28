import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.gui.app import BrowserCleanerGUI
from src.utils.logger import setup_logger
import logging

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def handle_high_dpi():
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions"""
    logging.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

def main():
    try:
        # Set up exception handling
        sys.excepthook = handle_exception
        
        # Set up logging to both file and console
        logs_path = os.path.join(os.path.expanduser('~'), 'CookieCleaner_logs')
        os.makedirs(logs_path, exist_ok=True)
        log_file = os.path.join(logs_path, 'cookiecleaner.log')
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logging.info("Starting application...")
        logging.info(f"Python version: {sys.version}")
        logging.info(f"Platform: {sys.platform}")
        logging.info("Initializing QApplication...")
        
        # Handle high DPI
        handle_high_dpi()
        
        # Create application
        app = QApplication(sys.argv)
        logging.info("QApplication created successfully")
        
        # Create main window
        logging.info("Creating main window...")
        window = BrowserCleanerGUI()
        logging.info("Main window created successfully")
        
        # Show window
        window.show()
        logging.info("Window displayed")
        
        # Start event loop
        logging.info("Starting application event loop")
        return app.exec()
    
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        logging.error(traceback.format_exc())
        return 1

if __name__ == '__main__':
    sys.exit(main())