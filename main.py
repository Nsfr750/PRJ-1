#!/usr/bin/env python3
"""
Main entry point for Project Browser application.
This module serves as the primary entry point for the application.
"""

import sys
import os
import logging
from pathlib import Path

# Add the script directory to the Python path
script_dir = Path(__file__).parent / "script"
sys.path.insert(0, str(script_dir))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPixmap, QPainter, QPalette, QIcon
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
        
        # Set application icon
        self.set_app_icon()
        
        # Set background image
        self.set_background_image()
        
        # Create central widget
        central_widget = QMainWindow()
        central_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(central_widget)
        
        # Create menu bar using AppMenuBar
        self.menu_bar = AppMenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # Connect language change signal
        self.menu_bar.language_changed.connect(self.on_language_changed)
        
        # Create status bar
        self.statusBar().showMessage("Ready")
    
    def closeEvent(self, event):
        """Handle the close event."""
        logger.info("Main window closing")
        event.accept()
    
    def on_language_changed(self):
        """Handle language change event."""
        # Update window title
        from script.lang.lang_mgr import get_text
        self.setWindowTitle(get_text('app.title', 'Project Browser'))
        
        # Update status bar
        self.statusBar().showMessage(get_text('app.ready', 'Ready'))
    
    def set_background_image(self):
        """Set the background image for the main window."""
        try:
            # Load the background image
            background_path = Path(__file__).parent / "assets" / "background.png"
            if background_path.exists():
                self.background_pixmap = QPixmap(str(background_path))
                
                # Create a palette with the background image
                palette = self.palette()
                palette.setBrush(QPalette.Window, self.background_pixmap)
                self.setPalette(palette)
                
                # Enable auto-fill background
                self.setAutoFillBackground(True)
                
                logger.info(f"Background image loaded from: {background_path}")
            else:
                logger.warning(f"Background image not found at: {background_path}")
        except Exception as e:
            logger.error(f"Failed to load background image: {e}")
    
    def paintEvent(self, event):
        """Paint the background image."""
        if hasattr(self, 'background_pixmap'):
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self.background_pixmap)
            painter.end()
        super().paintEvent(event)
    
    def set_app_icon(self):
        """Set the application icon."""
        try:
            # Load the logo image
            logo_path = Path(__file__).parent / "assets" / "logo.png"
            if logo_path.exists():
                app_icon = QIcon(str(logo_path))
                self.setWindowIcon(app_icon)
                
                # Also set the application icon
                QApplication.instance().setWindowIcon(app_icon)
                
                logger.info(f"Application icon loaded from: {logo_path}")
            else:
                logger.warning(f"Logo image not found at: {logo_path}")
        except Exception as e:
            logger.error(f"Failed to load application icon: {e}")


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
