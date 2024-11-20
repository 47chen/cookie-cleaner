import sys
import os
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QVBoxLayout, QWidget, QLabel, QTextEdit)
from PyQt6.QtCore import Qt

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.FileHandler('cookie_cleaner.log'),
                           logging.StreamHandler()])

class ChromeCleaner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chrome Cookie Cleaner")
        self.setMinimumSize(600, 500)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create buttons
        self.display_button = QPushButton("Display Cookies")
        self.display_button.clicked.connect(self.display_data)
        
        self.clean_button = QPushButton("Clean Cookies")
        self.clean_button.clicked.connect(self.clean_data)
        
        self.verify_button = QPushButton("Verify Cleaning")
        self.verify_button.clicked.connect(self.verify_cleaning)
        
        self.cookie_info_button = QPushButton("Show Cookie Details")
        self.cookie_info_button.clicked.connect(self.show_cookie_info)
        
        # Create labels and text display
        self.instructions_label = QLabel(
            "How to verify cleaning:\n"
            "1. Before cleaning: Visit and login to Facebook\n"
            "2. Click 'Clean Cookies'\n"
            "3. Go back to Facebook and refresh the page\n"
            "4. If cleaning was successful, you should be logged out"
        )
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        # Add widgets to layout
        layout.addWidget(self.display_button)
        layout.addWidget(self.clean_button)
        layout.addWidget(self.verify_button)
        layout.addWidget(self.cookie_info_button)
        layout.addWidget(self.instructions_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.log_display)

    def get_cookie_path(self):
        """Get Chrome cookie path based on operating system"""
        home = str(Path.home())
        if sys.platform == "win32":  # Windows
            return f"{home}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies"
        elif sys.platform == "darwin":  # macOS
            return f"{home}/Library/Application Support/Google/Chrome/Default/Cookies"
        elif sys.platform.startswith("linux"):  # Linux
            return f"{home}/.config/google-chrome/Default/Cookies"
        else:
            logging.error(f"Unsupported operating system: {sys.platform}")
            return None

    def get_cookie_details(self):
        """Retrieve cookie details from Chrome's database"""
        cookie_path = self.get_cookie_path()
        if not cookie_path:
            logging.error("Could not determine Chrome cookie path")
            return []
            
        try:
            if os.path.exists(cookie_path):
                conn = sqlite3.connect(cookie_path)
                c = conn.cursor()
                c.execute("""
                    SELECT host_key, name, path, value, expires_utc 
                    FROM cookies 
                    ORDER BY host_key LIMIT 100
                """)
                cookies = c.fetchall()
                conn.close()
                return cookies
            return []
        except Exception as e:
            logging.error(f"Error reading cookies: {str(e)}")
            return []

    def display_data(self):
        """Display current cookies"""
        self.log_display.clear()
        
        cookies = self.get_cookie_details()
        
        log_text = "=== Current Chrome Cookies ===\n\n"
        log_text += f"Total Cookies: {len(cookies)}\n\n"
        log_text += "=== Cookies (showing first 100) ===\n"
        
        for cookie in cookies:
            log_text += f"\nHost: {cookie[0]}\n"
            log_text += f"Cookie Name: {cookie[1]}\n"
            log_text += f"Path: {cookie[2]}\n"
            log_text += "-" * 50
        
        self.log_display.setText(log_text)
        self.status_label.setText("Cookie data displayed successfully")

    def clean_data(self):
        """Clean cookies"""
        cookie_path = self.get_cookie_path()
        
        try:
            if self.is_chrome_running():
                self.status_label.setText("Please close Chrome before cleaning!")
                return

            if os.path.exists(cookie_path):
                conn = sqlite3.connect(cookie_path)
                c = conn.cursor()
                c.execute("DELETE FROM cookies")
                conn.commit()
                conn.close()
                logging.info("Cookies cleaned successfully")
                self.status_label.setText("Cookies cleaned! Please verify by checking Facebook login.")
                self.display_data()
            else:
                self.status_label.setText("Cookie file not found!")

        except Exception as e:
            logging.error(f"Error during cleaning: {str(e)}")
            self.status_label.setText("Error during cleaning! See log for details.")

    def verify_cleaning(self):
        """Verify the cleaning process by checking cookies"""
        cookies = self.get_cookie_details()
        
        verification_text = "=== Verification Results ===\n\n"
        verification_text += f"Current Cookie Count: {len(cookies)}\n\n"
        verification_text += "To verify:\n"
        verification_text += "1. Try accessing Facebook - you should be logged out\n"
        verification_text += "2. Websites should treat you as a new visitor\n"
        
        self.log_display.setText(verification_text)
        self.status_label.setText("Verification complete")

    def show_cookie_info(self):
        """Show detailed cookie information"""
        cookies = self.get_cookie_details()
        cookie_info_text = "=== Detailed Cookie Information ===\n\n"
        cookie_info_text += f"Total Cookies Found: {len(cookies)}\n\n"
        
        for i, cookie in enumerate(cookies, 1):
            cookie_info_text += f"Cookie #{i}:\n"
            cookie_info_text += f"Host: {cookie[0]}\n"
            cookie_info_text += f"Name: {cookie[1]}\n"
            cookie_info_text += f"Path: {cookie[2]}\n"
            cookie_info_text += "-" * 50 + "\n"
        
        self.log_display.setText(cookie_info_text)
        self.status_label.setText("Cookie details displayed")

    def is_chrome_running(self):
        """Check if Chrome is running"""
        if sys.platform == "darwin":
            import psutil
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    return True
        else:
            # Add similar checks for Windows and Linux
            pass
        return False

def main():
    app = QApplication(sys.argv)
    window = ChromeCleaner()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()