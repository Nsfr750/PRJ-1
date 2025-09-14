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
from script.utils.logger import setup_logger, get_logger

# Setup logging
logger = setup_logger('prj1', logging.INFO)
logger.info("Starting PRJ-1 application")

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, lang='en'):
        super().__init__()
        self.lang = lang
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("Project Browser")
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
        logger.info("Main window closing")
        event.accept()


def main():
    """Main entry point for the application."""
    logger.info("Initializing application")
    
    try:
        # Create application
        app = QApplication(sys.argv)
        
        # Set application information
        app.setApplicationName("Project Browser")
        app.setApplicationVersion(__version__)
        app.setOrganizationName("Tuxxle")
        
        logger.info(f"Application info: {app.applicationName()} v{app.applicationVersion()}")
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show main window
        logger.info("Creating main window")
        window = MainWindow(lang='en')  # Default to English, can be changed
        window.show()
        
        logger.info("Starting application event loop")
        # Execute the application
        result = app.exec()
        logger.info(f"Application exited with code: {result}")
        sys.exit(result)
        
    except Exception as e:
        logger.error(f"Application crashed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
