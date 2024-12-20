from PyQt6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, 
                           QWidget, QLabel, QTextEdit)
from PyQt6.QtCore import Qt
import logging
from ..browsers.chrome import ChromeBrowser
from ..browsers.firefox import FirefoxBrowser
from ..browsers.edge import EdgeBrowser
from .widgets import LoadingWidget, StatusWidget

class BrowserCleanerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chrome = ChromeBrowser()
        self.firefox = FirefoxBrowser()
        self.edge = EdgeBrowser()
        self.setup_ui()

    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Browser Cookie Cleaner")
        self.setMinimumSize(600, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create buttons
        self.create_buttons(layout)
        
        # Create labels and display
        self.create_labels_and_display(layout)

        # Add status widget
        self.status_widget = StatusWidget()
        layout.addWidget(self.status_widget)
        self.status_widget.hide()
    
        # Add loading widget
        self.loading_widget = LoadingWidget()
        layout.addWidget(self.loading_widget)
        self.loading_widget.hide()

    def handle_cleaning_result(self, browser_name, success, initial, final):
        if success:
            self.status_widget.show_success(
                f"{browser_name} cookies cleaned! ({initial} cookies removed)"
            )
        else:
            self.status_widget.show_error(
            f"Error cleaning {browser_name} cookies!"
            )

    def create_buttons(self, layout):
        """Create and add buttons to layout"""
        # Create clean all button with special styling
        clean_all_button = QPushButton("Clean All Browsers' Cookies")
        clean_all_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        clean_all_button.clicked.connect(self.clean_all_browsers)
        layout.addWidget(clean_all_button)
        
        # Add spacing between the special button and regular buttons
        layout.addSpacing(20)
        
        # Regular buttons
        buttons = [
            ("Show Cookie Details", self.show_cookie_info),
            ("Clean Chrome Cookies", self.clean_chrome_data),
            ("Clean Firefox Cookies", self.clean_firefox_data),
            ("Clean Edge Cookies", self.clean_edge_data),
            ("Verify Cleaning", self.verify_cleaning)
        ]

        for text, slot in buttons:
            button = QPushButton(text)
            button.setMinimumHeight(30)  # Set minimum height for regular buttons
            button.clicked.connect(slot)
            layout.addWidget(button)

    def create_labels_and_display(self, layout):
        """Create and add labels and text display to layout"""
        self.instructions_label = QLabel(
            "How to verify cleaning:\n"
            "1. Before cleaning: Visit and login to a website\n"
            "2. Click 'Show Cookies Details' to see current cookies\n"
            "3. Click 'Clean All Browsers' Cookies\n"
            "4. Go back to the website and refresh\n"
            "5. If cleaning was successful, you should be logged out"
        )
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        layout.addWidget(self.instructions_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.log_display)

    # Browser-specific methods
    def display_chrome_data(self):
        cookies = self.chrome.get_cookie_details()
        self.display_cookies("Chrome", cookies)

    def display_firefox_data(self):
        cookies = self.firefox.get_cookie_details()
        self.display_cookies("Firefox", cookies)

    def clean_chrome_data(self):
        """Clean Chrome cookies with enhanced process handling"""
        try:
            self.loading_widget.start()
        
            if self.chrome.is_running():
                self.status_label.setText ("Chrome is running. Attempting to force quit...")
                if not self.chrome.force_quit_chrome():
                    self.status_label.setText("Unable to close Chrome. Please close it manually.")
                    return

            success, initial, final = self.chrome.clean_cookies()
            self.handle_cleaning_result("Chrome", success, initial, final)

        except Exception as e:
            logging.error(f"Error cleaning Chrome cookies: {str(e)}")
            self.status_label.setText("Error during cleaning! See log for details.")
        finally:
            self.loading_widget.stop()

    def clean_firefox_data(self):
        success, initial, final = self.firefox.clean_cookies()
        self.handle_cleaning_result("Firefox", success, initial, final)

    def display_edge_data(self):
        """Display Edge cookie data"""
        cookies = self.edge.get_cookie_details()
        self.display_cookies("Edge", cookies)

    def clean_edge_data(self):
        """Clean Edge cookies"""
        try:
            if self.edge.is_running():
                self.status_widget.show_error("Please close Edge before cleaning!")
                return

            success, initial, final = self.edge.clean_cookies()
            self.handle_cleaning_result("Edge", success, initial, final)

        except Exception as e:
            logging.error(f"Error cleaning Edge cookies: {str(e)}")
            self.status_widget.show_error("Error during cleaning! See log for details.")

    # Helper methods
    def display_cookies(self, browser_name, cookies):
        """Display cookie information in the log"""
        self.log_display.clear()
        log_text = f"=== Current {browser_name} Cookies ===\n\n"
        log_text += f"Total Cookies: {len(cookies)}\n\n"
        
        for cookie in cookies:
            log_text += f"\nHost: {cookie[0]}\n"
            log_text += f"Cookie Name: {cookie[1]}\n"
            log_text += f"Path: {cookie[2]}\n"
            log_text += "-" * 50
        
        self.log_display.setText(log_text)
        self.status_label.setText(f"{browser_name} cookie data displayed")

    def handle_cleaning_result(self, browser_name, success, initial, final):
        """Handle the result of cookie cleaning"""
        if success:
            msg = f"{browser_name} cookies cleaned! ({initial} cookies removed)"
            self.status_label.setText(msg)
            if browser_name == "Chrome":
                self.display_chrome_data()
            elif browser_name == "Firefox":
                self.display_firefox_data()
            else:
                self.display_edge_data()
        else:
            self.status_label.setText(f"Error cleaning {browser_name} cookies!")

    def verify_cleaning(self):
        """Verify the cleaning process"""
        chrome_count = self.chrome.get_cookie_count()
        firefox_count = self.firefox.get_cookie_count()
        edge_cookies = self.edge.get_cookie_details()
        
        verification_text = "=== Verification Results ===\n\n"
        verification_text += f"Chrome Cookies: {chrome_count}\n"
        verification_text += f"Firefox Cookies: {firefox_count}\n"
        verification_text += f"Edge Cookies: {len(edge_cookies)}\n\n"
        verification_text += "To verify:\n"
        verification_text += "1. Try accessing previous websites - you should be logged out\n"
        verification_text += "2. Websites should treat you as a new visitor\n"
        
        self.log_display.setText(verification_text)
        self.status_label.setText("Verification complete")

    def show_cookie_info(self):
        """Show detailed cookie information for all browsers"""
        chrome_cookies = self.chrome.get_cookie_details()
        firefox_cookies = self.firefox.get_cookie_details()
        edge_cookies = self.edge.get_cookie_details()
    
        info_text = "=== Detailed Cookie Information ===\n\n"
        info_text += f"Chrome Cookies: {len(chrome_cookies)}\n"
        info_text += f"Firefox Cookies: {len(firefox_cookies)}\n"
        info_text += f"Edge Cookies: {len(edge_cookies)}\n\n"
        
        info_text += "=== Chrome Cookies ===\n"
        for i, cookie in enumerate(chrome_cookies, 1):
            info_text += f"\nCookie #{i}:\n"
            info_text += f"Host: {cookie[0]}\n"
            info_text += f"Name: {cookie[1]}\n"
            info_text += f"Path: {cookie[2]}\n"
            info_text += "-" * 50 + "\n"
    
        info_text += "\n=== Firefox Cookies ===\n"
        for i, cookie in enumerate(firefox_cookies, 1):
            info_text += f"\nCookie #{i}:\n"
            info_text += f"Host: {cookie[0]}\n"
            info_text += f"Name: {cookie[1]}\n"
            info_text += f"Path: {cookie[2]}\n"
            info_text += "-" * 50 + "\n"
    
        info_text += "\n=== Edge Cookies ===\n"
        for i, cookie in enumerate(edge_cookies, 1):
            info_text += f"\nCookie #{i}:\n"
            info_text += f"Host: {cookie[0]}\n"
            info_text += f"Name: {cookie[1]}\n"
            info_text += f"Path: {cookie[2]}\n"
            info_text += "-" * 50 + "\n"
    
        self.log_display.setText(info_text)
        self.status_label.setText("Cookie details displayed")

    def closeEvent(self, event):
        """Handle application closing"""
        try:
            # Clean up old log files
            from ..utils.logger import cleanup_old_logs
            cleanup_old_logs("logs")
            
            logging.info("Application closing")
            event.accept()
        except Exception as e:
            logging.error(f"Error during application cleanup: {str(e)}")
            event.accept()

    def clean_all_browsers(self):
        """Clean cookies from all browsers"""
        try:
            self.loading_widget.start()
            
            # Store results for each browser
            results = []
            
            # Clean Chrome
            if self.chrome.is_running():
                self.status_label.setText("Chrome is running. Attempting to force quit...")
                if not self.chrome.force_quit_chrome():
                    self.status_label.setText("Unable to close Chrome. Please close it manually.")
                else:
                    success, initial, final = self.chrome.clean_cookies()
                    results.append(("Chrome", success, initial, final))
            else:
                success, initial, final = self.chrome.clean_cookies()
                results.append(("Chrome", success, initial, final))
                
            # Clean Firefox
            if not self.firefox.is_running():
                success, initial, final = self.firefox.clean_cookies()
                results.append(("Firefox", success, initial, final))
            else:
                self.status_widget.show_error("Please close Firefox before cleaning!")
                
            # Clean Edge
            if not self.edge.is_running():
                success, initial, final = self.edge.clean_cookies()
                results.append(("Edge", success, initial, final))
            else:
                self.status_widget.show_error("Please close Edge before cleaning!")
            
            # Display results
            total_cleaned = sum(initial - final for _, success, initial, final in results if success)
            success_count = sum(1 for result in results if result[1])
            
            if success_count > 0:
                self.status_widget.show_success(
                    f"Cleaned {total_cleaned} cookies from {success_count} browsers!"
                )
            else:
                self.status_widget.show_error("Failed to clean any browsers!")
                
            # Update display
            self.verify_cleaning()
            
        except Exception as e:
            logging.error(f"Error cleaning all browsers: {str(e)}")
            self.status_widget.show_error("Error cleaning browsers!")
        finally:
            self.loading_widget.stop()