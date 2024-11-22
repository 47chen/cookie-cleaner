import sys
import os
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QVBoxLayout, QWidget, QLabel, QTextEdit)
from PyQt6.QtCore import Qt
import time
import shutil

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.FileHandler('cookie_cleaner.log'),
                           logging.StreamHandler()])

class BrowserCleaner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Browser Cookie Cleaner")
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
        
        self.display_firefox_button = QPushButton("Display Firefox Cookies")
        self.display_firefox_button.clicked.connect(self.display_firefox_data)
        
        self.clean_firefox_button = QPushButton("Clean Firefox Cookies")
        self.clean_firefox_button.clicked.connect(self.clean_firefox_data)
        
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
        layout.insertWidget(1, self.display_firefox_button)
        layout.insertWidget(3, self.clean_firefox_button)

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

    def get_firefox_cookie_path(self):
        """Get Firefox cookie path based on operating system"""
        home = str(Path.home())
        if sys.platform == "win32":
            return f"{home}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"
        elif sys.platform == "darwin":
            return f"{home}/Library/Application Support/Firefox/Profiles"
        elif sys.platform.startswith("linux"):
            return f"{home}/.mozilla/firefox"
        else:
            logging.error(f"Unsupported operating system: {sys.platform}")
            return None

    def get_firefox_profile_path(self):
        """Get the default Firefox profile path"""
        base_path = self.get_firefox_cookie_path()
        if not base_path or not os.path.exists(base_path):
            return None
            
        try:
            # Find the default profile (ends with .default-release)
            for folder in os.listdir(base_path):
                if folder.endswith('.default-release'):
                    return os.path.join(base_path, folder)
            return None
        except Exception as e:
            logging.error(f"Error finding Firefox profile: {str(e)}")
            return None

    def get_firefox_cookie_details(self, max_retries=3):
        """Retrieve cookie details from Firefox's database with retry mechanism"""
        profile_path = self.get_firefox_profile_path()
        if not profile_path:
            logging.error("Could not find Firefox profile")
            return []

        cookie_path = os.path.join(profile_path, 'cookies.sqlite')
        if not os.path.exists(cookie_path):
            logging.error("Firefox cookie file not found")
            return []

        # Create a temporary copy of the database to avoid locks
        temp_db = os.path.join(os.path.dirname(cookie_path), 'cookies_temp.sqlite')
        
        for attempt in range(max_retries):
            try:
                # Copy the database file
                shutil.copy2(cookie_path, temp_db)
                
                conn = sqlite3.connect(temp_db)
                c = conn.cursor()
                c.execute("""
                    SELECT host, name, path, value, expiry 
                    FROM moz_cookies 
                    ORDER BY host LIMIT 100
                """)
                cookies = c.fetchall()
                conn.close()
                
                # Clean up temporary file
                os.remove(temp_db)
                return cookies

            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    logging.warning(f"Database locked, attempt {attempt + 1} of {max_retries}")
                    time.sleep(1)  # Wait before retry
                else:
                    logging.error(f"SQLite error: {str(e)}")
                    break
            except Exception as e:
                logging.error(f"Error reading Firefox cookies: {str(e)}")
                break
            finally:
                # Ensure temp file is removed
                if os.path.exists(temp_db):
                    try:
                        os.remove(temp_db)
                    except:
                        pass
                        
        return []

    def display_firefox_data(self):
        """Display current Firefox cookies"""
        self.log_display.clear()
        
        cookies = self.get_firefox_cookie_details()
        
        log_text = "=== Current Firefox Cookies ===\n\n"
        log_text += f"Total Cookies: {len(cookies)}\n\n"
        log_text += "=== Cookies (showing first 100) ===\n"
        
        for cookie in cookies:
            log_text += f"\nHost: {cookie[0]}\n"
            log_text += f"Cookie Name: {cookie[1]}\n"
            log_text += f"Path: {cookie[2]}\n"
            log_text += "-" * 50
        
        self.log_display.setText(log_text)
        self.status_label.setText("Firefox cookie data displayed successfully")

    def clean_firefox_data(self, max_retries=3):
        """Clean Firefox cookies with retry mechanism"""
        try:
            # Debug Point 1: Profile and Cookie Path Verification
            profile_path = self.get_firefox_profile_path()
            cookie_path = os.path.join(profile_path, 'cookies.sqlite')
            logging.info("=== Debug Point 1 ===")
            logging.info(f"Profile path exists: {os.path.exists(profile_path)}")
            logging.info(f"Cookie path exists: {os.path.exists(cookie_path)}")

            if not os.path.exists(cookie_path):
                raise FileNotFoundError(f"Cookie file not found at: {cookie_path}")

            # Debug Point 2: Firefox Process Check
            logging.info("=== Debug Point 2 ===")
            if self.is_firefox_running():
                self.status_label.setText("Please close Firefox before cleaning!")
                return

            # Debug Point 3: Database Operations
            logging.info("=== Debug Point 3 ===")
            
            # Create backup
            backup_path = cookie_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(cookie_path, backup_path)
            logging.info(f"Created backup at: {backup_path}")

            # Get initial count
            conn = sqlite3.connect(cookie_path)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM moz_cookies")
            initial_count = c.fetchone()[0]
            logging.info(f"Initial cookie count: {initial_count}")

            # Delete all cookies
            c.execute("DELETE FROM moz_cookies")
            conn.commit()

            # Verify deletion
            c.execute("SELECT COUNT(*) FROM moz_cookies")
            final_count = c.fetchone()[0]
            logging.info(f"Final cookie count: {final_count}")

            conn.close()

            # Update UI
            self.status_label.setText(f"Firefox cookies cleaned! ({initial_count} cookies removed)")
            self.display_firefox_data()  # Refresh the display

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                self.status_label.setText("Error: Firefox database is locked. Please close Firefox.")
            else:
                self.status_label.setText("Error: Database operation failed")
            logging.error(f"SQLite error: {str(e)}")
        except Exception as e:
            self.status_label.setText("Error during cleaning! See log for details.")
            logging.error(f"Error cleaning Firefox cookies: {str(e)}")

    def is_firefox_running(self):
        """Check if Firefox is running"""
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                try:
                    # Check for Firefox process names on different platforms
                    process_name = proc.info['name'].lower()
                    if 'firefox' in process_name or 'firefox-bin' in process_name:
                        logging.info("Firefox process found running")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            return False
        except ImportError:
            logging.warning("psutil not installed, cannot check if Firefox is running")
            return False

def main():
    app = QApplication(sys.argv)
    window = BrowserCleaner()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()