#!/usr/bin/env python3
"""
Main Dialog Module
Creates a transparent dialog window displaying main.png centered over the main background.
"""

import os
from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication
from PySide6.QtGui import QPixmap, QPainter, QBrush, QColor
from PySide6.QtCore import Qt, QSize, QPoint, QEvent


class MainDialog(QDialog):
    """Transparent dialog displaying main.png centered over background."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set dialog properties
        self.setWindowTitle("Main Dialog")
        self.resize(400, 400)
        
        # Make dialog transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        
        # Set up UI
        self.setup_ui()
        
        # Center dialog over parent or screen
        self.center_dialog()
        
        # Install event filter to track parent window resize events
        if self.parent():
            self.parent().installEventFilter(self)
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create label for main.png
        self.main_label = QLabel()
        self.main_label.setAlignment(Qt.AlignCenter)
        self.main_label.setStyleSheet("background: transparent;")
        
        # Load and set main.png
        main_image_path = Path(__file__).parent.parent.parent / "assets" / "main.png"
        if main_image_path.exists():
            pixmap = QPixmap(str(main_image_path))
            if not pixmap.isNull():
                # Scale pixmap to fit within 400x400 while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(380, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.main_label.setPixmap(scaled_pixmap)
            else:
                self.main_label.setText("main.png not found")
                self.main_label.setStyleSheet("color: red; font-size: 16px;")
        else:
            self.main_label.setText("main.png not found")
            self.main_label.setStyleSheet("color: red; font-size: 16px;")
        
        layout.addWidget(self.main_label)
    
    def center_dialog(self):
        """Center the dialog over the parent window or screen."""
        if self.parent():
            # Center over parent window
            parent_geometry = self.parent().geometry()
            parent_center = parent_geometry.center()
            
            # Calculate dialog position to center it over parent
            dialog_x = parent_center.x() - (self.width() // 2)
            dialog_y = parent_center.y() - (self.height() // 2)
            
            # Move dialog to new position
            self.move(dialog_x, dialog_y)
        else:
            # Center on screen if no parent
            screen_geometry = QApplication.primaryScreen().geometry()
            screen_center = screen_geometry.center()
            
            # Calculate dialog position to center it on screen
            dialog_x = screen_center.x() - (self.width() // 2)
            dialog_y = screen_center.y() - (self.height() // 2)
            
            # Move dialog to new position
            self.move(dialog_x, dialog_y)
    
    def paintEvent(self, event):
        """Override paint event to ensure transparency."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill with transparent background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
        
        super().paintEvent(event)
    
    def eventFilter(self, obj, event):
        """Event filter to track parent window resize events."""
        if obj == self.parent() and event.type() == QEvent.Resize:
            # Re-center dialog when parent window is resized
            self.center_dialog()
        return super().eventFilter(obj, event)
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test the dialog
    dialog = MainDialog()
    dialog.show()
    
    sys.exit(app.exec())
