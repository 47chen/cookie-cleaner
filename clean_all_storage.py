import sys
import os
import sqlite3
import shutil
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
        self.setWindowTitle("Chrome Cookie & Cache Cleaner")
        self.setMinimumSize(600, 500)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create display button
        self.display_button = QPushButton("Display Cookies and Cache")
        self.display_button.clicked.connect(self.display_data)
        
        # Create clean button
        self.clean_button = QPushButton("Clean Cookies and Cache")
        self.clean_button.clicked.connect(self.clean_data)
        
        # Create verify button
        self.verify_button = QPushButton("Verify Cleaning")
        self.verify_button.clicked.connect(self.verify_cleaning)
        
        # Create instructions label
        self.instructions_label = QLabel(
            "How to verify cleaning:\n"
            "1. Before cleaning: Visit and login to Facebook\n"
            "2. Click 'Clean Cookies and Cache'\n"
            "3. Go back to Facebook and refresh the page\n"
            "4. If cleaning was successful, you should be logged out"
        )
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Create status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        # Add widgets to layout
        layout.addWidget(self.display_button)
        layout.addWidget(self.clean_button)
        layout.addWidget(self.verify_button)
        layout.addWidget(self.instructions_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.log_display)

    def get_chrome_paths(self):
        """Get Chrome data paths based on operating system"""
        home = str(Path.home())
        if sys.platform == "win32":  # Windows
            profile_path = f"{home}\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
            return {
                'cookie_path': f"{profile_path}\\Cookies",
                'cache_path': f"{profile_path}\\Cache",
                'local_storage': f"{profile_path}\\Local Storage\\leveldb",
                'session_storage': f"{profile_path}\\Session Storage",
                'login_data': f"{profile_path}\\Login Data",
                'web_data': f"{profile_path}\\Web Data"
            }
        elif sys.platform == "darwin":  # macOS
            profile_path = f"{home}/Library/Application Support/Google/Chrome/Default"
            return {
                'cookie_path': f"{profile_path}/Cookies",
                'cache_path': f"{profile_path}/Cache",
                'local_storage': f"{profile_path}/Local Storage/leveldb",
                'session_storage': f"{profile_path}/Session Storage",
                'login_data': f"{profile_path}/Login Data",
                'web_data': f"{profile_path}/Web Data"
            }
        elif sys.platform.startswith("linux"):  # Linux
            profile_path = f"{home}/.config/google-chrome/Default"
            return {
                'cookie_path': f"{profile_path}/Cookies",
                'cache_path': f"{profile_path}/Cache",
                'local_storage': f"{profile_path}/Local Storage/leveldb",
                'session_storage': f"{profile_path}/Session Storage",
                'login_data': f"{profile_path}/Login Data",
                'web_data': f"{profile_path}/Web Data"
            }
        else:
            logging.error(f"Unsupported operating system: {sys.platform}")
            return None

    def get_cookie_details(self):
        paths = self.get_chrome_paths()
        if not paths:
            logging.error("Could not determine Chrome paths")
            return []
            
        try:
            cookie_path = paths['cookie_path']
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

    def get_cache_size(self):
        paths = self.get_chrome_paths()
        try:
            total_size = 0
            if os.path.exists(paths['cache_path']):
                for path, dirs, files in os.walk(paths['cache_path']):
                    for f in files:
                        fp = os.path.join(path, f)
                        total_size += os.path.getsize(fp)
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception as e:
            logging.error(f"Error calculating cache size: {str(e)}")
            return 0

    def display_data(self):
        self.log_display.clear()
        
        # Display cookies
        cookies = self.get_cookie_details()
        cache_size = self.get_cache_size()
        
        log_text = "=== Current Chrome Data ===\n\n"
        log_text += f"Total Cache Size: {cache_size:.2f} MB\n\n"
        log_text += "=== Cookies (showing first 100) ===\n"
        
        for cookie in cookies:
            log_text += f"\nHost: {cookie[0]}\n"
            log_text += f"Cookie Name: {cookie[1]}\n"
            log_text += f"Path: {cookie[2]}\n"
            log_text += "-" * 50
        
        self.log_display.setText(log_text)
        self.status_label.setText("Data displayed successfully")

    def clean_data(self):
        chrome_paths = self.get_chrome_paths()
        
        try:
            # Check if Chrome is running
            if self.is_chrome_running():
                self.status_label.setText("Please close ALL Chrome processes before cleaning!")
                return

            # Clean cookies
            if os.path.exists(chrome_paths['cookie_path']):
                conn = sqlite3.connect(chrome_paths['cookie_path'])
                c = conn.cursor()
                c.execute("DELETE FROM cookies")
                conn.commit()
                conn.close()
                logging.info("Cookies cleaned successfully")
            
            # Clean local storage
            if os.path.exists(chrome_paths['local_storage']):
                shutil.rmtree(chrome_paths['local_storage'], ignore_errors=True)
                os.makedirs(chrome_paths['local_storage'], exist_ok=True)
                logging.info("Local Storage cleaned successfully")
            
            # Clean session storage
            if os.path.exists(chrome_paths['session_storage']):
                shutil.rmtree(chrome_paths['session_storage'], ignore_errors=True)
                os.makedirs(chrome_paths['session_storage'], exist_ok=True)
                logging.info("Session Storage cleaned successfully")
            
            # Clean cache
            if os.path.exists(chrome_paths['cache_path']):
                shutil.rmtree(chrome_paths['cache_path'], ignore_errors=True)
                os.makedirs(chrome_paths['cache_path'], exist_ok=True)
                logging.info("Cache cleaned successfully")
            
            self.status_label.setText("Cleaning completed! Please verify by checking Facebook login.")
            self.display_data()

        except Exception as e:
            logging.error(f"Error during cleaning: {str(e)}")
            self.status_label.setText("Error during cleaning! See log for details.")

    def verify_cleaning(self):
        cookies = self.get_cookie_details()
        cache_size = self.get_cache_size()
        
        verification_text = "=== Verification Results ===\n\n"
        verification_text += f"Current Cache Size: {cache_size:.2f} MB\n"
        verification_text += f"Current Cookie Count: {len(cookies)}\n\n"
        verification_text += "To verify:\n"
        verification_text += "1. Try accessing Facebook - you should be logged out\n"
        verification_text += "2. Check if your saved passwords are cleared\n"
        verification_text += "3. Websites should treat you as a new visitor"
        
        self.log_display.setText(verification_text)

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