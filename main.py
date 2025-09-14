#!/usr/bin/env python3
"""
Main entry point for PRJ-1 application.
This module serves as the primary entry point for the application.
"""

import sys
import os
from pathlib import Path

# Add the script directory to the Python path
script_dir = Path(__file__).parent / "script"
sys.path.insert(0, str(script_dir))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
    from PySide6.QtCore import Qt
except ImportError:
    print("PySide6 is not installed. Please install it using:")
    print("pip install PySide6")
    sys.exit(1)

# Import application modules
from script.ui.menu import AppMenuBar
from script.utils.version import __version__

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, lang='en'):
        super().__init__()
        self.lang = lang
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("Application List")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QMainWindow()
        self.setCentralWidget(central_widget)
        
        # Create menu bar using AppMenuBar
        self.menu_bar = AppMenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # Create status bar
        self.statusBar().showMessage("Ready")
    
    def closeEvent(self, event):
        """Handle the close event."""
        event.accept()


def main():
    """Main entry point for the application."""
    # Create application
    app = QApplication(sys.argv)
    
    # Set application information
    app.setApplicationName("Project List")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Tuxxle")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow(lang='en')  # Default to English, can be changed
    window.show()
    
    # Execute the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
