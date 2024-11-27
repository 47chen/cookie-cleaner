import sys
from PyQt6.QtWidgets import QApplication
from src.gui.app import BrowserCleanerGUI
from src.utils.logger import setup_logger

def main():
    # Set up logging
    setup_logger()
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = BrowserCleanerGUI()
    window.show()
    
    # Start application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()