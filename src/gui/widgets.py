from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer

class LoadingWidget(QWidget):
    """Widget to show loading status"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Loading label
        self.label = QLabel("Processing...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Infinite progress
        layout.addWidget(self.progress)
        
    def start(self):
        """Show the loading widget"""
        self.show()
        
    def stop(self):
        """Hide the loading widget"""
        self.hide()

class StatusWidget(QLabel):
    """Widget for displaying status messages"""
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide()
        
    def show_message(self, message: str, color: str, duration: int = 5000):
        """Show a message with specified color for duration milliseconds"""
        self.setText(message)
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background-color: rgba(0, 0, 0, 0.1);
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }}
        """)
        self.show()
        QTimer.singleShot(duration, self.hide)

    def show_success(self, message: str):
        """Show success message"""
        self.show_message(message, "#28a745")  # Green

    def show_error(self, message: str):
        """Show error message"""
        self.show_message(message, "#dc3545")  # Red

    def show_info(self, message: str):
        """Show info message"""
        self.show_message(message, "#17a2b8")  # Blue