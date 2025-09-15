from PySide6.QtCore import Qt, QProcess, Signal
from PySide6.QtWidgets import QMenuBar, QMenu, QMessageBox
from PySide6.QtGui import QAction, QActionGroup
import webbrowser
import os
import sys

# Local imports
from .about import show_about
from .sponsor import show_sponsor
from .help import show_help
from script.lang.lang_mgr import get_language_manager, get_text, set_language

class AppMenuBar(QMenuBar):
    """Custom menu bar for the Neural Network Creator application."""
    
    # Signal emitted when language is changed
    language_changed = Signal()
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.parent = parent
        self.lang = lang
        self.lang_manager = get_language_manager()
        self.setup_menus()
    
    def setup_menus(self):
        """Set up the application menus."""
        # File Menu
        file_menu = self.addMenu(get_text('menu.file', '&File'))
        
        # New Action
        new_action = file_menu.addAction(get_text('menu.new', 'New'))
        new_action.setShortcut('Ctrl+N')
        
        # Open Action
        open_action = file_menu.addAction(get_text('menu.open', 'Open...'))
        open_action.setShortcut('Ctrl+O')
        
        # Save Action
        save_action = file_menu.addAction(get_text('menu.save', 'Save'))
        save_action.setShortcut('Ctrl+S')
        
        # Save As Action
        save_as_action = file_menu.addAction(get_text('menu.save_as', 'Save As...'))
        save_as_action.setShortcut('Ctrl+Shift+S')
        
        file_menu.addSeparator()
        
        # Exit Action
        exit_action = file_menu.addAction(get_text('menu.exit', 'Exit'))
        exit_action.setShortcut('Alt+F4')
        exit_action.triggered.connect(self.close_application)
        
        # Edit Menu
        edit_menu = self.addMenu(get_text('menu.edit', '&Edit'))
        
        # Undo Action
        undo_action = edit_menu.addAction(get_text('menu.undo', 'Undo'))
        undo_action.setShortcut('Ctrl+Z')
        
        # Redo Action
        redo_action = edit_menu.addAction(get_text('menu.redo', 'Redo'))
        redo_action.setShortcut('Ctrl+Y')
        
        edit_menu.addSeparator()
        
        # Cut Action
        cut_action = edit_menu.addAction(get_text('menu.cut', 'Cut'))
        cut_action.setShortcut('Ctrl+X')
        
        # Copy Action
        copy_action = edit_menu.addAction(get_text('menu.copy', 'Copy'))
        copy_action.setShortcut('Ctrl+C')
        
        # Paste Action
        paste_action = edit_menu.addAction(get_text('menu.paste', 'Paste'))
        paste_action.setShortcut('Ctrl+V')
        
        # Delete Action
        delete_action = edit_menu.addAction(get_text('menu.delete', 'Delete'))
        delete_action.setShortcut('Del')
        
        edit_menu.addSeparator()
        
        # Select All Action
        select_all_action = edit_menu.addAction(get_text('menu.select_all', 'Select All'))
        select_all_action.setShortcut('Ctrl+A')
        
        # Language Menu
        language_menu = self.addMenu(get_text('menu.language', '&Language'))
        
        # Language Actions
        self.language_group = QActionGroup(self)
        self.language_group.setExclusive(True)
        
        # English
        en_action = QAction(get_text('menu.english', 'English', lang=self.lang), self)
        en_action.setCheckable(True)
        en_action.setChecked(True)  # Default
        en_action.triggered.connect(lambda: self.change_language('en'))
        language_menu.addAction(en_action)
        self.language_group.addAction(en_action)
        
        # Italian
        it_action = QAction(get_text('menu.italian', 'Italiano', lang=self.lang), self)
        it_action.setCheckable(True)
        it_action.triggered.connect(lambda: self.change_language('it'))
        language_menu.addAction(it_action)
        self.language_group.addAction(it_action)
        
        language_menu.addSeparator()
        
        # Tools Menu
        tools_menu = self.addMenu(get_text('menu.tools', '&Tools'))
        
        # Project Browser Action
        project_browser_action = tools_menu.addAction(get_text('menu.project_browser', 'Project Browser'))
        project_browser_action.triggered.connect(self.show_project_browser)
        
        # View Logs Action
        view_logs_action = tools_menu.addAction(get_text('menu.view_logs', 'View Logs'))
        view_logs_action.triggered.connect(self.view_logs)
        
        # Check for Updates Action
        check_updates_action = tools_menu.addAction(get_text('menu.check_updates', 'Check for Updates'))
        check_updates_action.triggered.connect(self.check_for_updates)

        tools_menu.addSeparator()
        
        # Help Menu
        help_menu = self.addMenu(get_text('menu.help', '&Help'))
        
        # Help Action
        help_action = help_menu.addAction(get_text('menu.help', 'Help'))
        help_action.setShortcut('F1')
        help_action.triggered.connect(self.show_help)
        
        # Wiki Action
        wiki_action = help_menu.addAction(get_text('menu.documentation', 'Documentation (Wiki)'))
        wiki_action.triggered.connect(self.open_wiki)
        
        # Add separator
        help_menu.addSeparator()
        
        # About Action
        about_action = help_menu.addAction(get_text('menu.about', 'About'))
        about_action.triggered.connect(self.show_about)
        
        # Sponsor Action
        sponsor_action = help_menu.addAction(get_text('menu.sponsor', 'Sponsor'))
        sponsor_action.triggered.connect(self.show_sponsor)
    
    def change_language(self, lang_code):
        """Change the application language."""
        try:
            # Set the new language
            set_language(lang_code)
            
            # Update the UI
            self.retranslate_ui()
            
            # Emit signal to notify parent of language change
            self.language_changed.emit()
            
        except Exception as e:
            error_msg = f"Failed to change language: {str(e)}"
            QMessageBox.critical(
                self,
                get_text('app.error', 'Error'),
                error_msg
            )
    
    def retranslate_ui(self):
        """Retranslate the UI elements."""
        try:
            # Get all menu bar actions safely
            menu_actions = self.actions()
            if not menu_actions:
                return
            
            # File menu (index 0)
            if len(menu_actions) > 0:
                file_menu = menu_actions[0].menu()
                if file_menu:
                    file_menu.setTitle(get_text('menu.file', '&File', lang=self.lang))
                    # Update File menu actions
                    actions = file_menu.actions()
                    action_index = 0
                    for action in actions:
                        if not action.isSeparator():
                            if action_index == 0:
                                action.setText(get_text('menu.new', 'New', lang=self.lang))
                            elif action_index == 1:
                                action.setText(get_text('menu.open', 'Open...', lang=self.lang))
                            elif action_index == 2:
                                action.setText(get_text('menu.save', 'Save', lang=self.lang))
                            elif action_index == 3:
                                action.setText(get_text('menu.save_as', 'Save As...', lang=self.lang))
                            elif action_index == 4:
                                action.setText(get_text('menu.exit', 'Exit', lang=self.lang))
                            action_index += 1
            
            # Edit menu (index 1)
            if len(menu_actions) > 1:
                edit_menu = menu_actions[1].menu()
                if edit_menu:
                    edit_menu.setTitle(get_text('menu.edit', '&Edit', lang=self.lang))
                    # Update Edit menu actions
                    actions = edit_menu.actions()
                    action_index = 0
                    for action in actions:
                        if not action.isSeparator():
                            if action_index == 0:
                                action.setText(get_text('menu.undo', 'Undo', lang=self.lang))
                            elif action_index == 1:
                                action.setText(get_text('menu.redo', 'Redo', lang=self.lang))
                            elif action_index == 2:
                                action.setText(get_text('menu.cut', 'Cut', lang=self.lang))
                            elif action_index == 3:
                                action.setText(get_text('menu.copy', 'Copy', lang=self.lang))
                            elif action_index == 4:
                                action.setText(get_text('menu.paste', 'Paste', lang=self.lang))
                            elif action_index == 5:
                                action.setText(get_text('menu.delete', 'Delete', lang=self.lang))
                            elif action_index == 6:
                                action.setText(get_text('menu.select_all', 'Select All', lang=self.lang))
                            action_index += 1
            
            # Language menu (index 2)
            if len(menu_actions) > 2:
                lang_menu = menu_actions[2].menu()
                if lang_menu:
                    lang_menu.setTitle(get_text('menu.language', '&Language', lang=self.lang))
                    lang_actions = lang_menu.actions()
                    if len(lang_actions) > 0: lang_actions[0].setText(get_text('menu.english', 'English', lang=self.lang))
                    if len(lang_actions) > 1: lang_actions[1].setText(get_text('menu.italian', 'Italiano', lang=self.lang))

            # Tools menu (index 3)
            if len(menu_actions) > 3:
                tools_menu = menu_actions[3].menu()
                if tools_menu:
                    tools_menu.setTitle(get_text('menu.tools', '&Tools', lang=self.lang))
                    # Update Tools menu actions
                    actions = tools_menu.actions()
                    action_index = 0
                    for action in actions:
                        if not action.isSeparator():
                            if action_index == 0:
                                action.setText(get_text('menu.project_browser', 'Project Browser', lang=self.lang))
                            elif action_index == 1:
                                action.setText(get_text('menu.view_logs', 'View Logs', lang=self.lang))
                            elif action_index == 2:
                                action.setText(get_text('menu.check_updates', 'Check for Updates', lang=self.lang))
                            action_index += 1
            
            # Help menu (index 4)
            if len(menu_actions) > 4:
                help_menu = menu_actions[4].menu()
                if help_menu:
                    help_menu.setTitle(get_text('menu.help', '&Help', lang=self.lang))
                    # Update Help menu actions
                    actions = help_menu.actions()
                    action_index = 0
                    for action in actions:
                        if not action.isSeparator():
                            if action_index == 0:
                                action.setText(get_text('menu.help', 'Help', lang=self.lang))
                            elif action_index == 1:
                                action.setText(get_text('menu.documentation', 'Documentation (Wiki)', lang=self.lang))
                            elif action_index == 2:
                                action.setText(get_text('menu.about', 'About', lang=self.lang))
                            elif action_index == 3:
                                action.setText(get_text('menu.sponsor', 'Sponsor', lang=self.lang))
                            action_index += 1
        except Exception as e:
            # Silently handle retranslation errors to avoid crashes
            import logging
            logging.getLogger(__name__).warning(f"Retranslation error: {e}")
    
    def close_application(self):
        """Close the application."""
        reply = QMessageBox.question(
            self,
            get_text('app.confirm_exit', 'Confirm Exit'),
            get_text('app.confirm_exit_text', 'Are you sure you want to exit?'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.parent.close()
    
    def show_about(self):
        """Show the about dialog."""
        show_about(self.parent, self.lang)
    
    def show_sponsor(self):
        """Show the sponsor dialog."""
        show_sponsor(self.parent, self.lang)
    
    def show_help(self):
        """Show the help dialog."""
        show_help(self.parent, self.lang)
    
    def show_project_browser(self):
        """Show the project browser dialog."""
        try:
            from .project_browser import show_project_browser
            show_project_browser(self.parent)
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Error",
                f"Failed to open project browser: {str(e)}"
            )
    
    def open_wiki(self):
        """Open the project wiki in the default web browser."""
        webbrowser.open("https://github.com/Nsfr750/PRJ-1/wiki")
    
    def view_logs(self):
        """Open the log viewer dialog."""
        try:
            from .view_log import LogViewer
            log_viewer = LogViewer(self.parent)
            log_viewer.language_changed.connect(self.retranslate_ui)
            log_viewer.exec_()
        except Exception as e:
            # Fallback to opening in a separate process if in-process fails
            current_dir = os.path.dirname(os.path.abspath(__file__))
            log_script = os.path.join(current_dir, 'view_log.py')
            
            if os.path.exists(log_script):
                python = sys.executable
                QProcess.startDetached(python, [log_script])
            else:
                QMessageBox.critical(
                    self,
                    get_text('app.error', 'Error'),
                    get_text('app.log_viewer_error', 'Failed to open log viewer')
                )
                QMessageBox.warning(
                    self.parent,
                    "Log Viewer Not Found",
                    f"Could not find log viewer at: {log_script}"
                )
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Error",
                f"Failed to open log viewer: {str(e)}"
            )
    
    def check_for_updates(self):
        """Check for application updates."""
        try:
            # Import here to avoid circular imports
            from script.utils.updates import check_for_updates as show_update_dialog
            show_update_dialog(self.parent)
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Update Check Error",
                f"Failed to check for updates: {str(e)}"
            )
