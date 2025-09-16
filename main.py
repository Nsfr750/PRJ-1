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
from script.ui.main_dialog import MainDialog
from script.utils.version import __version__, save_version_data_to_json
from script.utils.logger import setup_logger, get_logger
from script.utils.settings import load_settings, save_settings, get_language, get_window_geometry, set_window_geometry

# Setup logging
logger = setup_logger('prj1', logging.INFO)
logger.info("Starting PRJ-1 application")

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, lang='en'):
        super().__init__()
        self.lang = lang
        self.init_ui()
        self.load_and_apply_settings()
    
    def load_and_apply_settings(self):
        """Load and apply settings to the main window."""
        try:
            # Load window geometry settings
            geometry = get_window_geometry()
            
            # Apply window geometry
            self.setGeometry(geometry['x'], geometry['y'], geometry['width'], geometry['height'])
            
            # Apply window state
            if geometry.get('maximized', False):
                self.showMaximized()
            elif geometry.get('fullscreen', False):
                self.showFullScreen()
            else:
                self.showNormal()
            
            logger.info(f"Applied window geometry: {geometry['width']}x{geometry['height']} at ({geometry['x']}, {geometry['y']})")
            
        except Exception as e:
            logger.error(f"Error applying settings: {e}")
            # Use default geometry if settings fail
            self.setGeometry(100, 100, 1200, 800)
    
    def save_window_settings(self):
        """Save current window settings."""
        try:
            # Get current window geometry
            if self.isMaximized():
                # If maximized, save the normal geometry (before maximization)
                geometry = self.normalGeometry()
                x, y, width, height = geometry.x(), geometry.y(), geometry.width(), geometry.height()
                maximized = True
                fullscreen = False
            elif self.isFullScreen():
                geometry = self.normalGeometry()
                x, y, width, height = geometry.x(), geometry.y(), geometry.width(), geometry.height()
                maximized = False
                fullscreen = True
            else:
                geometry = self.geometry()
                x, y, width, height = geometry.x(), geometry.y(), geometry.width(), geometry.height()
                maximized = False
                fullscreen = False
            
            # Save window geometry
            set_window_geometry(x, y, width, height, maximized, fullscreen)
            
            # Save all settings
            save_settings()
            
            logger.info(f"Saved window settings: {width}x{height} at ({x}, {y})")
            
        except Exception as e:
            logger.error(f"Error saving window settings: {e}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        logger.info("Main window closing")
        
        # Save window settings
        self.save_window_settings()
        
        # Accept the close event
        event.accept()
    
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
        self.menu_bar = AppMenuBar(self, lang=self.lang)
        self.setMenuBar(self.menu_bar)
        
        # Connect language change signal
        self.menu_bar.language_changed.connect(self.on_language_changed)
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Show MainDialog centered over background
        self.show_main_dialog()
    
    def show_main_dialog(self):
        """Show MainDialog centered over the main window background."""
        try:
            # Create and show MainDialog with self as parent
            self.main_dialog = MainDialog(self)
            self.main_dialog.show()
            logger.info("MainDialog displayed centered over background")
        except Exception as e:
            logger.error(f"Error showing MainDialog: {e}")
    
    def closeEvent(self, event):
        """Handle the close event."""
        logger.info("Main window closing")
        
        # Close MainDialog if it exists
        if hasattr(self, 'main_dialog') and self.main_dialog:
            self.main_dialog.close()
        
        event.accept()
    
    def on_language_changed(self):
        """Handle language change event."""
        # Update window title
        from script.lang.lang_mgr import get_text
        self.setWindowTitle(get_text('app.title', 'Project Browser'))
        
        # Update status bar
        self.statusBar().showMessage(get_text('app.ready', 'Ready'))
    
    # background image
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
        
        # Save version data to config/version.json
        logger.info("Saving version data to config/version.json")
        save_version_data_to_json()
        
        # Save settings to config/settings.json
        logger.info("Saving settings to config/settings.json")
        save_settings()
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show main window
        logger.info("Creating main window")
        
        # Get language from settings
        app_language = get_language()
        logger.info(f"Using language from settings: {app_language}")
        
        window = MainWindow(lang=app_language)
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
