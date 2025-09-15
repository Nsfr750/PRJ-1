import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QDialogButtonBox, QTextBrowser)

# Local imports
from script.utils.version import __version__
from script.lang.lang_mgr import get_text

class AboutDialog(QDialog):
    """Custom about dialog with close button."""
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.text_browser = None  # Will be set in setup_ui
        self.setup_ui()
        self.retranslate_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create horizontal layout for logo and content
        header_layout = QHBoxLayout()
        
        # Add logo to the left
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'assets', 'logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        # Create text browser for the about content
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setReadOnly(True)
        
        
        # Add close button with blue background and white text
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_button = button_box.button(QDialogButtonBox.StandardButton.Close)
        if close_button:
            close_button.setStyleSheet("background-color: #0078d4; color: white; padding: 5px 15px; border: none; border-radius: 3px;")
        button_box.rejected.connect(self.close)
        
        # Add widgets to header layout
        header_layout.addWidget(logo_label)
        header_layout.addWidget(self.text_browser, 1)  # 1 = stretch factor
        
        # Add layouts to main layout
        layout.addLayout(header_layout)
        layout.addWidget(button_box)
        
        # Set layout
        self.setLayout(layout)
    
    def retranslate_ui(self):
        """Update the UI translations when language changes."""
        self.setWindowTitle(get_text('about.title', 'About', lang=self.lang))
        
        # Create text browser for the about content
        app_title = get_text('app.title', 'Application List', lang=self.lang)
        version_text = get_text('about.version', 'Version: {version}', lang=self.lang, version=__version__)
        author_text = get_text('about.author', '© {year} Nsfr750 - All rights reserved', lang=self.lang, year=2025)
        description_text = get_text('about.description', 'A comprehensive project management tool helps you discover, organize, and manage your development projects with ease.', lang=self.lang)
        github_text = get_text('about.github', 'GitHub Repository', lang=self.lang)
        
        about_text = f"""
        <h2 style='text-align: center;'>{app_title}</h2>
        <p style='text-align: center;'>{version_text}</p>
        <p style='text-align: center;'>{author_text}</p>
        <p style='text-align: justify;'>{description_text}</p>
        """
        
        if self.text_browser:
            self.text_browser.setHtml(about_text)
    
    def set_language(self, lang):
        """Set the language and update translations."""
        self.lang = lang
        self.retranslate_ui()


def show_about(parent=None, lang='en'):
    """Show the about dialog.
    
    Args:
        parent: Parent widget for the dialog
        lang: Language code for translations (e.g., 'en', 'it')
    """
    dialog = AboutDialog(parent, lang)
    dialog.setModal(True)
    dialog.exec()
