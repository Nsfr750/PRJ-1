import os
import sys
import threading
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QProgressBar, QTextEdit)

# Local imports
from script.lang.lang_mgr import get_text

# Add the root directory to the path to import version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from script.utils.version import __version__


class UpdateDialog:
    """Independent dialog for displaying update information."""
    
    def __init__(self, parent=None):
        self.parent = parent
        # Import UpdateChecker locally to avoid circular import
        from script.utils.updates import UpdateChecker
        self.update_checker = UpdateChecker()
        
    def show_update_dialog(self, force_check: bool = False) -> None:
        """Show the update dialog."""
        self._show_gui_dialog(force_check)
    
    def _show_gui_dialog(self, force_check: bool = False) -> None:
        """Show GUI dialog for updates."""
        dialog = QDialog(self.parent)
        dialog.setWindowTitle(get_text("update_checker.window_title"))
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        # Main layout
        layout = QVBoxLayout(dialog)
        
        # Title
        title_label = QLabel(get_text("update_checker.title"))
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Current version
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel(get_text("update_checker.current_version")))
        current_version_label = QLabel(self.update_checker.current_version)
        version_layout.addWidget(current_version_label)
        version_layout.addStretch()
        layout.addLayout(version_layout)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel(get_text("update_checker.status")))
        self.status_label = QLabel(get_text("update_checker.checking"))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress)
        
        # Release notes
        layout.addWidget(QLabel(get_text("update_checker.release_notes")))
        self.release_notes = QTextEdit()
        self.release_notes.setReadOnly(True)
        layout.addWidget(self.release_notes)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.download_button = QPushButton(get_text("update_checker.download_update"))
        self.download_button.clicked.connect(lambda: self._open_download_page(dialog))
        self.download_button.setEnabled(False)
        
        check_again_button = QPushButton(get_text("update_checker.check_again"))
        check_again_button.clicked.connect(lambda: self._refresh_updates())
        
        close_button = QPushButton(get_text("update_checker.close"))
        close_button.clicked.connect(dialog.accept)
        
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(check_again_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        # Check for updates in a separate thread
        def check_updates_thread():
            update_info = self.update_checker.check_for_updates(force_check)
            
            # Update GUI in main thread
            QTimer.singleShot(0, lambda: self._update_gui_with_results(update_info))
        
        threading.Thread(target=check_updates_thread, daemon=True).start()
        
        # Show the dialog
        dialog.exec_()
    
    def retranslate_ui(self):
        """Retranslate all UI elements with current language."""
        # This method will be called when language changes
        # All UI elements are already using get_text() so they will be updated
        # when the dialog is recreated
        pass
    
    def set_language(self, language: str):
        """Set the language for the dialog.
        
        Args:
            language: Language code (e.g., 'en', 'it')
        """
        # Store language preference if needed
        # The actual language change is handled by the global language manager
        self.retranslate_ui()
    
    def _update_gui_with_results(self, update_info):
        """Update the GUI with update check results."""
        self.progress.setRange(0, 100)  # Stop indeterminate progress
        self.progress.setValue(100)
        
        if not update_info:
            self.status_label.setText(get_text("update_checker.failed_to_check"))
            self.status_label.setStyleSheet("color: red;")
            self.release_notes.setText(get_text("update_checker.connection_error"))
            self.download_button.setEnabled(False)
            return
        
        latest_version = update_info.get('version', 'Unknown')
        is_newer = update_info.get('is_newer', False)
        
        if is_newer:
            self.status_label.setText(get_text("update_checker.update_available", version=latest_version))
            self.status_label.setStyleSheet("color: green;")
            release_text = get_text("update_checker.version_info", version=latest_version, name=update_info.get('name', '')) + "\n"
            release_text += "="*50 + "\n\n"
            release_text += update_info.get('body', get_text("update_checker.no_release_notes"))
            self.release_notes.setText(release_text)
            self.download_button.setEnabled(True)
        else:
            self.status_label.setText(get_text("update_checker.latest_version", version=latest_version))
            self.status_label.setStyleSheet("color: blue;")
            release_text = get_text("update_checker.already_latest", version=latest_version) + "\n\n"
            if update_info.get('body'):
                release_text += get_text("update_checker.latest_release_notes") + "\n"
                release_text += "="*50 + "\n\n"
                release_text += update_info.get('body', '')
            self.release_notes.setText(release_text)
            self.download_button.setEnabled(False)
    
    def _refresh_updates(self):
        """Refresh update information."""
        self.status_label.setText(get_text("update_checker.checking"))
        self.status_label.setStyleSheet("")
        self.release_notes.clear()
        self.progress.setRange(0, 0)  # Indeterminate progress
        self.download_button.setEnabled(False)
        
        def check_updates_thread():
            update_info = self.update_checker.check_for_updates(force_check=True)
            QTimer.singleShot(0, lambda: self._update_gui_with_results(update_info))
        
        threading.Thread(target=check_updates_thread, daemon=True).start()
    
    def _open_download_page(self, dialog):
        """Open the download page in the default browser."""
        import webbrowser
        webbrowser.open(self.update_checker.github_repo_url + "/releases/latest")
    
    def _show_console_dialog(self, force_check: bool = False) -> None:
        """Show console-based update information."""
        print(get_text("update_checker.console_title"))
        print("=" * 40)
        print(get_text("update_checker.console_current_version", version=self.update_checker.current_version))
        print(get_text("update_checker.console_checking"))
        
        update_info = self.update_checker.check_for_updates(force_check)
        
        if not update_info:
            print(get_text("update_checker.console_failed"))
            return
        
        latest_version = update_info.get('version', 'Unknown')
        is_newer = update_info.get('is_newer', False)
        
        print(get_text("update_checker.console_latest_version", version=latest_version))
        
        if is_newer:
            print(get_text("update_checker.console_update_available", version=latest_version))
            print(get_text("update_checker.console_release_notes"))
            print(update_info.get('body', get_text("update_checker.console_no_release_notes")))
            print(get_text("update_checker.console_download", url=f"{self.update_checker.github_repo_url}/releases/latest"))
        else:
            print(get_text("update_checker.console_latest"))
        
        input(get_text("update_checker.console_press_enter"))
