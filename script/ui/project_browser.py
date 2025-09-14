#!/usr/bin/env python3
"""
Project Browser Dialog
Provides a browsable interface for projects found in the GitHub folder.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any

from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtGui import QFont, QIcon, QDesktopServices
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QProgressBar, QDialogButtonBox, QMessageBox, QHeaderView, QFrame,
    QSplitter, QTextBrowser, QGroupBox
)

from ..project_scanner import ProjectScanner


class ScanThread(QThread):
    """Thread for scanning projects to avoid blocking the UI."""
    
    finished = Signal(list)
    progress = Signal(int)
    status = Signal(str)
    
    def __init__(self, scanner: ProjectScanner):
        super().__init__()
        self.scanner = scanner
    
    def run(self):
        """Run the scanning process."""
        try:
            self.status.emit("Scanning projects...")
            projects = self.scanner.scan_projects()
            self.finished.emit(projects)
            self.status.emit(f"Found {len(projects)} projects")
        except Exception as e:
            self.status.emit(f"Error scanning: {str(e)}")
            self.finished.emit([])


class ProjectBrowserDialog(QDialog):
    """Dialog for browsing and managing GitHub projects."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scanner = ProjectScanner()
        self.projects: List[Dict[str, Any]] = []
        self.filtered_projects: List[Dict[str, Any]] = []
        self.current_project: Dict[str, Any] = None
        
        self.setWindowTitle("Project Browser")
        self.setMinimumSize(1200, 800)
        self.setup_ui()
        
        # Start scanning projects
        self.scan_projects()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Project list
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Project details
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter sizes
        splitter.setSizes([600, 600])
        
        # Bottom buttons
        button_box = self.create_button_box()
        layout.addWidget(button_box)
    
    def create_left_panel(self) -> QFrame:
        """Create the left panel with project list and controls."""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Search and filter controls
        controls_group = QGroupBox("Search & Filter")
        controls_layout = QGridLayout(controls_group)
        
        # Search box
        controls_layout.addWidget(QLabel("Search:"), 0, 0)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search projects...")
        self.search_box.textChanged.connect(self.filter_projects)
        controls_layout.addWidget(self.search_box, 0, 1)
        
        # Language filter
        controls_layout.addWidget(QLabel("Language:"), 1, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItem("All")
        self.language_combo.currentTextChanged.connect(self.filter_projects)
        controls_layout.addWidget(self.language_combo, 1, 1)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.scan_projects)
        controls_layout.addWidget(self.refresh_button, 2, 0, 1, 2)
        
        layout.addWidget(controls_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Project table
        self.project_table = QTableWidget()
        self.project_table.setColumnCount(6)
        self.project_table.setHorizontalHeaderLabels([
            "Name", "Language", "Version", "Size", "Modified", "Git"
        ])
        self.project_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.project_table.setSelectionMode(QTableWidget.SingleSelection)
        self.project_table.itemSelectionChanged.connect(self.on_project_selected)
        self.project_table.itemDoubleClicked.connect(self.on_project_double_clicked)
        
        # Set column widths
        header = self.project_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.project_table)
        
        return panel
    
    def create_right_panel(self) -> QFrame:
        """Create the right panel with project details."""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Project details group
        details_group = QGroupBox("Project Details")
        details_layout = QGridLayout(details_group)
        
        # Project name
        details_layout.addWidget(QLabel("Name:"), 0, 0)
        self.name_label = QLabel("No project selected")
        self.name_label.setFont(QFont("", 12, QFont.Bold))
        details_layout.addWidget(self.name_label, 0, 1)
        
        # Project path
        details_layout.addWidget(QLabel("Path:"), 1, 0)
        self.path_label = QLabel("-")
        self.path_label.setWordWrap(True)
        details_layout.addWidget(self.path_label, 1, 1)
        
        # Language
        details_layout.addWidget(QLabel("Language:"), 2, 0)
        self.language_label = QLabel("-")
        details_layout.addWidget(self.language_label, 2, 1)
        
        # Version
        details_layout.addWidget(QLabel("Version:"), 3, 0)
        self.version_label = QLabel("-")
        details_layout.addWidget(self.version_label, 3, 1)
        
        # Size
        details_layout.addWidget(QLabel("Size:"), 4, 0)
        self.size_label = QLabel("-")
        details_layout.addWidget(self.size_label, 4, 1)
        
        # Modified
        details_layout.addWidget(QLabel("Modified:"), 5, 0)
        self.modified_label = QLabel("-")
        details_layout.addWidget(self.modified_label, 5, 1)
        
        # Git status
        details_layout.addWidget(QLabel("Git Repository:"), 6, 0)
        self.git_label = QLabel("-")
        details_layout.addWidget(self.git_label, 6, 1)
        
        layout.addWidget(details_group)
        
        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout(desc_group)
        self.description_text = QTextBrowser()
        self.description_text.setMaximumHeight(100)
        desc_layout.addWidget(self.description_text)
        layout.addWidget(desc_group)
        
        # Project files info
        files_group = QGroupBox("Project Files")
        files_layout = QGridLayout(files_group)
        
        files_layout.addWidget(QLabel("README:"), 0, 0)
        self.readme_label = QLabel("-")
        files_layout.addWidget(self.readme_label, 0, 1)
        
        files_layout.addWidget(QLabel("Requirements:"), 1, 0)
        self.requirements_label = QLabel("-")
        files_layout.addWidget(self.requirements_label, 1, 1)
        
        files_layout.addWidget(QLabel("Setup:"), 2, 0)
        self.setup_label = QLabel("-")
        files_layout.addWidget(self.setup_label, 2, 1)
        
        files_layout.addWidget(QLabel("Main File:"), 3, 0)
        self.main_file_label = QLabel("-")
        files_layout.addWidget(self.main_file_label, 3, 1)
        
        layout.addWidget(files_group)
        
        # Action buttons
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.clicked.connect(self.open_project_folder)
        self.open_folder_button.setEnabled(False)
        actions_layout.addWidget(self.open_folder_button)
        
        self.open_terminal_button = QPushButton("Open Terminal")
        self.open_terminal_button.clicked.connect(self.open_terminal)
        self.open_terminal_button.setEnabled(False)
        actions_layout.addWidget(self.open_terminal_button)
        
        self.open_editor_button = QPushButton("Open in Editor")
        self.open_editor_button.clicked.connect(self.open_in_editor)
        self.open_editor_button.setEnabled(False)
        actions_layout.addWidget(self.open_editor_button)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        return panel
    
    def create_button_box(self) -> QDialogButtonBox:
        """Create the button box for the dialog."""
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        return button_box
    
    def scan_projects(self):
        """Start scanning projects in a separate thread."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Scanning projects...")
        self.refresh_button.setEnabled(False)
        
        # Create and start scan thread
        self.scan_thread = ScanThread(self.scanner)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.progress.connect(self.progress_bar.setValue)
        self.scan_thread.status.connect(self.status_label.setText)
        self.scan_thread.start()
    
    def on_scan_finished(self, projects: List[Dict[str, Any]]):
        """Handle completion of project scanning."""
        self.projects = projects
        self.filtered_projects = projects
        
        self.progress_bar.setVisible(False)
        self.refresh_button.setEnabled(True)
        
        # Update language combo box
        self.update_language_combo()
        
        # Populate project table
        self.populate_project_table()
        
        self.status_label.setText(f"Found {len(projects)} projects")
    
    def update_language_combo(self):
        """Update the language filter combo box."""
        current_language = self.language_combo.currentText()
        self.language_combo.clear()
        
        languages = self.scanner.get_languages()
        for language in languages:
            self.language_combo.addItem(language)
        
        # Restore previous selection
        index = self.language_combo.findText(current_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
    
    def populate_project_table(self):
        """Populate the project table with filtered projects."""
        self.project_table.setRowCount(len(self.filtered_projects))
        
        for row, project in enumerate(self.filtered_projects):
            # Name
            name_item = QTableWidgetItem(project['name'])
            name_item.setData(Qt.UserRole, project)  # Store full project data
            self.project_table.setItem(row, 0, name_item)
            
            # Language
            lang_item = QTableWidgetItem(project['language'])
            self.project_table.setItem(row, 1, lang_item)
            
            # Version
            version_item = QTableWidgetItem(project['version'])
            self.project_table.setItem(row, 2, version_item)
            
            # Size
            size_text = self.format_size(project['size'])
            size_item = QTableWidgetItem(size_text)
            self.project_table.setItem(row, 3, size_item)
            
            # Modified
            modified_text = project['modified'].strftime("%Y-%m-%d %H:%M")
            modified_item = QTableWidgetItem(modified_text)
            self.project_table.setItem(row, 4, modified_item)
            
            # Git status
            git_text = "✓" if project['has_git'] else "✗"
            git_item = QTableWidgetItem(git_text)
            git_item.setTextAlignment(Qt.AlignCenter)
            self.project_table.setItem(row, 5, git_item)
    
    def format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def filter_projects(self):
        """Filter projects based on search text and language."""
        search_text = self.search_box.text().strip()
        language = self.language_combo.currentText()
        
        self.filtered_projects = self.scanner.filter_projects(search_text, language)
        self.populate_project_table()
        
        self.status_label.setText(f"Showing {len(self.filtered_projects)} of {len(self.projects)} projects")
    
    def on_project_selected(self):
        """Handle project selection in the table."""
        selected_items = self.project_table.selectedItems()
        if not selected_items:
            return
        
        # Get the selected row
        row = selected_items[0].row()
        name_item = self.project_table.item(row, 0)
        self.current_project = name_item.data(Qt.UserRole)
        
        # Update details panel
        self.update_project_details()
        
        # Enable action buttons
        self.open_folder_button.setEnabled(True)
        self.open_terminal_button.setEnabled(True)
        self.open_editor_button.setEnabled(True)
    
    def on_project_double_clicked(self, item):
        """Handle double-click on a project."""
        self.on_project_selected()
        self.open_project_folder()
    
    def update_project_details(self):
        """Update the project details panel with current project info."""
        if not self.current_project:
            return
        
        project = self.current_project
        
        # Update labels
        self.name_label.setText(project['name'])
        self.path_label.setText(project['path'])
        self.language_label.setText(project['language'])
        self.version_label.setText(project['version'])
        self.size_label.setText(self.format_size(project['size']))
        self.modified_label.setText(project['modified'].strftime("%Y-%m-%d %H:%M:%S"))
        self.git_label.setText("Yes" if project['has_git'] else "No")
        
        # Update description
        self.description_text.setText(project['description'] or "No description available")
        
        # Update file info
        self.readme_label.setText("✓" if project['has_readme'] else "✗")
        self.requirements_label.setText("✓" if project['has_requirements'] else "✗")
        self.setup_label.setText("✓" if project['has_setup'] else "✗")
        self.main_file_label.setText(project['main_file'] or "None")
    
    def open_project_folder(self):
        """Open the selected project folder in file explorer."""
        if not self.current_project:
            return
        
        project_path = Path(self.current_project['path'])
        if project_path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(project_path)))
        else:
            QMessageBox.warning(self, "Error", "Project folder not found")
    
    def open_terminal(self):
        """Open terminal in the project folder."""
        if not self.current_project:
            return
        
        project_path = self.current_project['path']
        try:
            # Open Windows Terminal or Command Prompt in the project directory
            subprocess.Popen(['wt', '-d', project_path], shell=True)
        except Exception:
            try:
                # Fallback to Command Prompt
                subprocess.Popen(['cmd', '/k', 'cd', '/d', project_path], shell=True)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open terminal: {str(e)}")
    
    def open_in_editor(self):
        """Open the project in the default editor."""
        if not self.current_project:
            return
        
        project_path = Path(self.current_project['path'])
        
        # Try to open main file if exists
        if self.current_project['main_file']:
            main_file_path = project_path / self.current_project['main_file']
            if main_file_path.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(main_file_path)))
                return
        
        # Otherwise open the folder
        self.open_project_folder()


def show_project_browser(parent=None):
    """Show the project browser dialog."""
    dialog = ProjectBrowserDialog(parent)
    dialog.setModal(True)
    dialog.exec()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication([])
    dialog = ProjectBrowserDialog()
    dialog.show()
    app.exec()
