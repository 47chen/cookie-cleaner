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

class StatusWidget(QWidget):
    """Widget to show operation status"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Status label
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
    def show_success(self, message, duration=3000):
        """Show success message"""
        self.label.setStyleSheet("color: green;")
        self.label.setText(message)
        self.show()
        QTimer.singleShot(duration, self.hide)
        
    def show_error(self, message, duration=3000):
        """Show error message"""
        self.label.setStyleSheet("color: red;")
        self.label.setText(message)
        self.show()
        QTimer.singleShot(duration, self.hide)