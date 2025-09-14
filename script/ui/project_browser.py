#!/usr/bin/env python3
"""
Project Browser Dialog
Provides a browsable interface for projects found in the GitHub folder.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtGui import QFont, QIcon, QDesktopServices
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QProgressBar, QDialogButtonBox, QMessageBox, QHeaderView, QFrame,
    QSplitter, QTextBrowser, QGroupBox, QFileDialog, QListWidget, QCheckBox, QListWidgetItem
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
        
        # Initialize recent projects list
        self.update_recent_projects_list()
        
        # Don't start scanning automatically - user must click "Start Scan" button
        self.status_label.setText("Ready - Click 'Start Scan' to begin scanning projects")
    
    def closeEvent(self, event):
        """Handle dialog close event to properly clean up threads."""
        # Wait for scan thread to finish if it's running
        if hasattr(self, 'scan_thread') and self.scan_thread.isRunning():
            self.scan_thread.quit()
            self.scan_thread.wait(1000)  # Wait up to 1 second
            if self.scan_thread.isRunning():
                self.scan_thread.terminate()
                self.scan_thread.wait(500)  # Wait another 0.5 seconds
        
        super().closeEvent(event)
    
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
        
        # Directory selection controls
        directory_group = QGroupBox("Scan Directory")
        directory_layout = QGridLayout(directory_group)
        
        # Current directory display
        directory_layout.addWidget(QLabel("Current Directory:"), 0, 0)
        self.directory_label = QLabel(self.scanner.get_scan_directory())
        self.directory_label.setWordWrap(True)
        directory_layout.addWidget(self.directory_label, 0, 1)
        
        # Browse button
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_directory)
        directory_layout.addWidget(self.browse_button, 0, 2)
        
        layout.addWidget(directory_group)
        
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
        
        # Category filter
        controls_layout.addWidget(QLabel("Category:"), 2, 0)
        self.category_combo = QComboBox()
        self.category_combo.addItem("All")
        self.category_combo.currentTextChanged.connect(self.filter_projects)
        controls_layout.addWidget(self.category_combo, 2, 1)
        
        # Tag filter
        controls_layout.addWidget(QLabel("Tags:"), 3, 0)
        self.tag_filter_box = QLineEdit()
        self.tag_filter_box.setPlaceholderText("Filter by tags (comma-separated)...")
        self.tag_filter_box.textChanged.connect(self.filter_projects)
        controls_layout.addWidget(self.tag_filter_box, 3, 1)
        
        # Favorite filter
        controls_layout.addWidget(QLabel("Favorites:"), 4, 0)
        self.favorite_combo = QComboBox()
        self.favorite_combo.addItem("All")
        self.favorite_combo.addItem("Favorites Only")
        self.favorite_combo.addItem("Non-Favorites Only")
        self.favorite_combo.currentTextChanged.connect(self.filter_projects)
        controls_layout.addWidget(self.favorite_combo, 4, 1)
        
        # Recent projects section
        recent_group = QGroupBox("Recent Projects")
        recent_layout = QVBoxLayout(recent_group)
        
        # Recent projects list
        self.recent_projects_list = QListWidget()
        self.recent_projects_list.setMaximumHeight(150)  # Limit height
        self.recent_projects_list.itemClicked.connect(self.on_recent_project_clicked)
        recent_layout.addWidget(self.recent_projects_list)
        
        # Recent projects buttons
        recent_buttons_layout = QHBoxLayout()
        
        self.clear_recent_button = QPushButton("Clear")
        self.clear_recent_button.clicked.connect(self.clear_recent_projects)
        self.clear_recent_button.setMaximumWidth(60)
        recent_buttons_layout.addWidget(self.clear_recent_button)
        
        recent_buttons_layout.addStretch()
        
        recent_layout.addLayout(recent_buttons_layout)
        
        controls_layout.addWidget(recent_group, 6, 0, 1, 2)
        
        # Scan control buttons
        scan_buttons_layout = QHBoxLayout()
        
        self.start_scan_button = QPushButton("Start Scan")
        self.start_scan_button.clicked.connect(self.start_scanning)
        # Style start button: green background with white text
        self.start_scan_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px 15px; border: none; border-radius: 3px;")
        scan_buttons_layout.addWidget(self.start_scan_button)
        
        self.stop_scan_button = QPushButton("Stop Scan")
        self.stop_scan_button.clicked.connect(self.stop_scanning)
        self.stop_scan_button.setEnabled(False)  # Disabled initially
        # Style stop button: red background with white text
        self.stop_scan_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 5px 15px; border: none; border-radius: 3px;")
        scan_buttons_layout.addWidget(self.stop_scan_button)
        
        # Export button
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_to_markdown)
        # Style export button: blue background with white text
        self.export_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 5px 15px; border: none; border-radius: 3px;")
        scan_buttons_layout.addWidget(self.export_button)
        
        # Dashboard button
        self.dashboard_button = QPushButton("Dashboard")
        self.dashboard_button.clicked.connect(self.show_dashboard)
        # Style dashboard button: purple background with white text
        self.dashboard_button.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold; padding: 5px 15px; border: none; border-radius: 3px;")
        scan_buttons_layout.addWidget(self.dashboard_button)
        
        # Advanced search button
        self.advanced_search_button = QPushButton("Advanced Search")
        self.advanced_search_button.clicked.connect(self.show_advanced_search)
        # Style advanced search button: teal background with white text
        self.advanced_search_button.setStyleSheet("background-color: #009688; color: white; font-weight: bold; padding: 5px 15px; border: none; border-radius: 3px;")
        scan_buttons_layout.addWidget(self.advanced_search_button)
        
        controls_layout.addLayout(scan_buttons_layout, 7, 0, 1, 2)
        
        # Batch operations layout
        batch_layout = QHBoxLayout()
        
        # Select all/none buttons
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all_projects)
        self.select_all_button.setMaximumWidth(80)
        batch_layout.addWidget(self.select_all_button)
        
        self.select_none_button = QPushButton("Select None")
        self.select_none_button.clicked.connect(self.select_none_projects)
        self.select_none_button.setMaximumWidth(80)
        batch_layout.addWidget(self.select_none_button)
        
        batch_layout.addWidget(QLabel("|"))
        
        # Batch operation buttons
        self.batch_open_button = QPushButton("Open Selected")
        self.batch_open_button.clicked.connect(self.batch_open_projects)
        batch_layout.addWidget(self.batch_open_button)
        
        self.batch_favorite_button = QPushButton("Toggle Favorite")
        self.batch_favorite_button.clicked.connect(self.batch_toggle_favorite)
        batch_layout.addWidget(self.batch_favorite_button)
        
        self.batch_tag_button = QPushButton("Add Tags")
        self.batch_tag_button.clicked.connect(self.batch_add_tags)
        batch_layout.addWidget(self.batch_tag_button)
        
        self.batch_category_button = QPushButton("Set Category")
        self.batch_category_button.clicked.connect(self.batch_set_category)
        batch_layout.addWidget(self.batch_category_button)
        
        batch_layout.addStretch()
        
        controls_layout.addLayout(batch_layout, 8, 0, 1, 2)
        
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
        self.project_table.setColumnCount(11)
        self.project_table.setHorizontalHeaderLabels([
            "", "Name", "Language", "Version", "Category", "Tags", "Size", "Modified", "Git", "Notes", "Favorite"
        ])
        self.project_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.project_table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.project_table.itemSelectionChanged.connect(self.on_project_selected)
        self.project_table.itemDoubleClicked.connect(self.on_project_double_clicked)
        self.project_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.project_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Enable batch selection with checkboxes
        self.project_table.setColumnWidth(0, 30)  # Checkbox column
        
        # Set column widths
        header = self.project_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name column
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Language
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Version
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Tags
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Size
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Modified
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Git
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Notes
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents)  # Favorite
        
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
        
        # Category
        details_layout.addWidget(QLabel("Category:"), 7, 0)
        self.category_label = QLabel("-")
        details_layout.addWidget(self.category_label, 7, 1)
        
        # Tags
        details_layout.addWidget(QLabel("Tags:"), 8, 0)
        self.tags_label = QLabel("-")
        self.tags_label.setWordWrap(True)
        details_layout.addWidget(self.tags_label, 8, 1)
        
        layout.addWidget(details_group)
        
        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout(desc_group)
        self.description_text = QTextBrowser()
        self.description_text.setMaximumHeight(100)
        desc_layout.addWidget(self.description_text)
        layout.addWidget(desc_group)
        
        # Project notes
        notes_group = QGroupBox("Project Notes")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_text = QTextBrowser()
        self.notes_text.setMaximumHeight(100)
        self.notes_text.setPlaceholderText("No notes added yet...")
        notes_layout.addWidget(self.notes_text)
        
        notes_buttons_layout = QHBoxLayout()
        
        self.edit_notes_button = QPushButton("Edit Notes")
        self.edit_notes_button.clicked.connect(self.edit_notes)
        self.edit_notes_button.setEnabled(False)
        notes_buttons_layout.addWidget(self.edit_notes_button)
        
        self.clear_notes_button = QPushButton("Clear Notes")
        self.clear_notes_button.clicked.connect(self.clear_notes)
        self.clear_notes_button.setEnabled(False)
        notes_buttons_layout.addWidget(self.clear_notes_button)
        
        notes_layout.addLayout(notes_buttons_layout)
        layout.addWidget(notes_group)
        
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
        
        self.manage_tags_button = QPushButton("Manage Tags")
        self.manage_tags_button.clicked.connect(self.manage_tags)
        self.manage_tags_button.setEnabled(False)
        actions_layout.addWidget(self.manage_tags_button)
        
        self.set_category_button = QPushButton("Set Category")
        self.set_category_button.clicked.connect(self.set_category)
        self.set_category_button.setEnabled(False)
        actions_layout.addWidget(self.set_category_button)
        
        self.favorite_button = QPushButton("Add to Favorites")
        self.favorite_button.clicked.connect(self.toggle_favorite)
        self.favorite_button.setEnabled(False)
        actions_layout.addWidget(self.favorite_button)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        return panel
    
    def create_button_box(self) -> QDialogButtonBox:
        """Create the button box with dialog buttons."""
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        return button_box
    
    def browse_directory(self):
        """Open directory selection dialog to choose scan directory."""
        current_dir = self.scanner.get_scan_directory()
        
        # Open directory selection dialog
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Scan",
            current_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if selected_dir:
            # Update the scanner with new directory
            if self.scanner.set_scan_directory(selected_dir):
                self.directory_label.setText(selected_dir)
                self.status_label.setText(f"Directory changed to: {selected_dir}")
                # Automatically start scanning the new directory
                self.scan_projects()
            else:
                QMessageBox.warning(
                    self,
                    "Invalid Directory",
                    "The selected directory is not valid. Please choose a different directory."
                )
    
    def start_scanning(self):
        """Start scanning projects in a separate thread."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Update button states
        self.start_scan_button.setEnabled(False)
        self.stop_scan_button.setEnabled(True)
        
        # Create and start scan thread
        self.scan_thread = ScanThread(self.scanner)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.status.connect(self.status_label.setText)
        self.scan_thread.start()
    
    def stop_scanning(self):
        """Stop the currently running scan."""
        if hasattr(self, 'scan_thread') and self.scan_thread.isRunning():
            self.scan_thread.quit()
            self.scan_thread.wait(1000)  # Wait up to 1 second
            if self.scan_thread.isRunning():
                self.scan_thread.terminate()
                self.scan_thread.wait(500)  # Wait another 0.5 seconds
        
        # Update UI
        self.progress_bar.setVisible(False)
        self.start_scan_button.setEnabled(True)
        self.stop_scan_button.setEnabled(False)
        self.status_label.setText("Scan stopped by user")
    
    def export_to_markdown(self):
        """Export project results to Markdown format and save to data folder."""
        if not self.projects:
            QMessageBox.warning(
                self,
                "No Projects",
                "No projects to export. Please scan for projects first."
            )
            return
        
        try:
            # Generate markdown content
            markdown_content = self._generate_markdown_content()
            
            # Create data directory if it doesn't exist
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"projects_export_{timestamp}.md"
            filepath = data_dir / filename
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Show success message
            QMessageBox.information(
                self,
                "Export Successful",
                f"Project results exported successfully to:\n{filepath}"
            )
            
            self.status_label.setText(f"Exported to {filename}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export projects: {str(e)}"
            )
    
    def _generate_markdown_content(self) -> str:
        """Generate Markdown content for project export."""
        from datetime import datetime
        
        # Header
        content = []
        content.append("# Project Browser Export\n")
        content.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        content.append(f"**Total Projects:** {len(self.projects)}\n")
        content.append(f"**Scan Directory:** {self.scanner.get_scan_directory()}\n")
        
        if self.scanner.last_scan:
            content.append(f"**Last Scan:** {self.scanner.last_scan.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        content.append("---\n\n")
        
        # Summary statistics
        languages = {}
        git_projects = 0
        readme_projects = 0
        requirements_projects = 0
        
        for project in self.projects:
            lang = project.get('language', 'Unknown')
            languages[lang] = languages.get(lang, 0) + 1
            if project.get('has_git', False):
                git_projects += 1
            if project.get('has_readme', False):
                readme_projects += 1
            if project.get('has_requirements', False):
                requirements_projects += 1
        
        content.append("## Summary\n\n")
        content.append(f"- **Projects with Git:** {git_projects}/{len(self.projects)}\n")
        content.append(f"- **Projects with README:** {readme_projects}/{len(self.projects)}\n")
        content.append(f"- **Projects with Requirements:** {requirements_projects}/{len(self.projects)}\n\n")
        
        content.append("### Languages\n\n")
        content.append("| Language | Count |\n")
        content.append("|----------|-------|\n")
        for lang, count in sorted(languages.items()):
            content.append(f"| {lang} | {count} |\n")
        content.append("\n")
        
        # Project details
        content.append("## Project Details\n\n")
        
        for i, project in enumerate(self.projects, 1):
            content.append(f"### {i}. {project.get('name', 'Unknown')}\n\n")
            
            # Basic info
            content.append(f"- **Path:** `{project.get('path', 'N/A')}`\n")
            content.append(f"- **Language:** {project.get('language', 'Unknown')}\n")
            content.append(f"- **Version:** {project.get('version', 'Unknown')}\n")
            content.append(f"- **Size:** {self._format_size(project.get('size', 0))}\n")
            
            # Modified date
            modified = project.get('modified')
            if modified:
                if isinstance(modified, str):
                    try:
                        modified = datetime.fromisoformat(modified)
                    except ValueError:
                        modified = None
                if modified:
                    content.append(f"- **Modified:** {modified.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Features
            features = []
            if project.get('has_git', False):
                features.append("✅ Git")
            else:
                features.append("❌ Git")
            
            if project.get('has_readme', False):
                features.append("✅ README")
            else:
                features.append("❌ README")
            
            if project.get('has_requirements', False):
                features.append("✅ Requirements")
            else:
                features.append("❌ Requirements")
            
            if project.get('has_setup', False):
                features.append("✅ Setup")
            else:
                features.append("❌ Setup")
            
            content.append(f"- **Features:** {' | '.join(features)}\n")
            
            # Main file
            if project.get('main_file'):
                content.append(f"- **Main File:** `{project.get('main_file')}`\n")
            
            # Description
            description = project.get('description', '')
            if description and description.strip():
                content.append(f"\n**Description:**\n{description}\n")
            
            content.append("\n---\n\n")
        
        # Footer
        content.append("\n---\n")
        content.append(f"\n*Generated by Project Browser v{self._get_app_version()}*\n")
        
        return "".join(content)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _get_app_version(self) -> str:
        """Get the application version."""
        try:
            from ..utils.version import __version__
            return __version__
        except ImportError:
            return "Unknown"
    
    def scan_projects(self):
        """Legacy method for backward compatibility."""
        self.start_scanning()
    
    def on_scan_finished(self, projects: List[Dict[str, Any]]):
        """Handle completion of project scanning."""
        self.projects = projects
        self.filtered_projects = projects
        
        self.progress_bar.setVisible(False)
        self.start_scan_button.setEnabled(True)
        self.stop_scan_button.setEnabled(False)
        
        # Update language combo box
        self.update_language_combo()
        
        # Update category combo box
        self.update_category_combo()
        
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
    
    def update_category_combo(self):
        """Update the category filter combo box."""
        current_category = self.category_combo.currentText()
        self.category_combo.clear()
        
        # Add "All" option
        self.category_combo.addItem("All")
        
        # Get all categories from projects
        categories = set()
        for project in self.projects:
            category = project.get('category')
            if category:
                categories.add(category)
        
        # Add categories to combo box
        for category in sorted(categories):
            self.category_combo.addItem(category)
        
        # Restore previous selection
        index = self.category_combo.findText(current_category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
    
    def populate_project_table(self):
        """Populate the project table with filtered projects."""
        self.project_table.setRowCount(len(self.filtered_projects))
        
        for row, project in enumerate(self.filtered_projects):
            # Checkbox for batch selection
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(checkbox_item.flags() | Qt.ItemIsUserCheckable)
            checkbox_item.setCheckState(Qt.Unchecked)
            self.project_table.setItem(row, 0, checkbox_item)
            
            # Name
            name_item = QTableWidgetItem(project['name'])
            name_item.setData(Qt.UserRole, project)  # Store full project data
            self.project_table.setItem(row, 1, name_item)
            
            # Language
            lang_item = QTableWidgetItem(project['language'])
            self.project_table.setItem(row, 2, lang_item)
            
            # Version
            version_item = QTableWidgetItem(project['version'])
            self.project_table.setItem(row, 3, version_item)
            
            # Category
            category_text = project.get('category', 'None') or 'None'
            category_item = QTableWidgetItem(category_text)
            self.project_table.setItem(row, 4, category_item)
            
            # Tags
            tags = project.get('tags', [])
            tags_text = ', '.join(tags) if tags else 'None'
            tags_item = QTableWidgetItem(tags_text)
            self.project_table.setItem(row, 5, tags_item)
            
            # Size
            size_text = self.format_size(project['size'])
            size_item = QTableWidgetItem(size_text)
            self.project_table.setItem(row, 6, size_item)
            
            # Modified
            modified_text = project['modified'].strftime("%Y-%m-%d %H:%M")
            modified_item = QTableWidgetItem(modified_text)
            self.project_table.setItem(row, 7, modified_item)
            
            # Git status
            git_text = "✓" if project['has_git'] else "✗"
            git_item = QTableWidgetItem(git_text)
            git_item.setTextAlignment(Qt.AlignCenter)
            self.project_table.setItem(row, 8, git_item)
            
            # Notes
            note = project.get('note', '')
            note_text = "✓" if note else "✗"
            note_item = QTableWidgetItem(note_text)
            note_item.setTextAlignment(Qt.AlignCenter)
            note_item.setToolTip(note[:100] + "..." if len(note) > 100 else note or "No notes")
            self.project_table.setItem(row, 9, note_item)
            
            # Favorite status
            is_favorite = project.get('is_favorite', False)
            favorite_text = "★" if is_favorite else "☆"
            favorite_item = QTableWidgetItem(favorite_text)
            favorite_item.setTextAlignment(Qt.AlignCenter)
            favorite_item.setForeground(Qt.yellow if is_favorite else Qt.gray)
            favorite_item.setToolTip("Favorite project" if is_favorite else "Not a favorite")
            self.project_table.setItem(row, 10, favorite_item)
    
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
        """Filter projects based on search text, language, category, tags, and favorites."""
        search_text = self.search_box.text().strip()
        language = self.language_combo.currentText()
        category = self.category_combo.currentText()
        tag_filter_text = self.tag_filter_box.text().strip()
        favorite_filter = self.favorite_combo.currentText()
        
        # Start with all projects
        filtered = self.projects
        
        # Filter by search text
        if search_text:
            search_lower = search_text.lower()
            filtered = [p for p in filtered if (
                search_lower in p['name'].lower() or
                (p.get('description') and search_lower in p['description'].lower())
            )]
        
        # Filter by language
        if language != "All":
            filtered = [p for p in filtered if p['language'] == language]
        
        # Filter by category
        if category != "All":
            filtered = [p for p in filtered if p.get('category') == category]
        
        # Filter by tags
        if tag_filter_text:
            # Split comma-separated tags and normalize
            filter_tags = [tag.strip().lower() for tag in tag_filter_text.split(',') if tag.strip()]
            if filter_tags:
                filtered = [p for p in filtered if (
                    p.get('tags') and
                    any(filter_tag in [project_tag.lower() for project_tag in p['tags']] for filter_tag in filter_tags)
                )]
        
        # Filter by favorites
        if favorite_filter == "Favorites Only":
            filtered = [p for p in filtered if p.get('is_favorite', False)]
        elif favorite_filter == "Non-Favorites Only":
            filtered = [p for p in filtered if not p.get('is_favorite', False)]
        
        self.filtered_projects = filtered
        self.populate_project_table()
        
        self.status_label.setText(f"Showing {len(self.filtered_projects)} of {len(self.projects)} projects")
    
    def on_project_selected(self):
        """Handle project selection in the table."""
        selected_items = self.project_table.selectedItems()
        if not selected_items:
            return
        
        # Get the selected row
        row = selected_items[0].row()
        name_item = self.project_table.item(row, 1)  # Name is now in column 1
        self.current_project = name_item.data(Qt.UserRole)
        
        # Track project access for recent projects
        if self.current_project and self.current_project.get('path'):
            self.scanner.tag_manager.track_project_access(self.current_project['path'])
            self.update_recent_projects_list()
        
        # Update UI
        self.update_project_details()
        self.enable_project_controls(True)
        self.open_folder_button.setEnabled(True)
        self.open_terminal_button.setEnabled(True)
        self.open_editor_button.setEnabled(True)
        self.manage_tags_button.setEnabled(True)
        self.set_category_button.setEnabled(True)
        self.edit_notes_button.setEnabled(True)
        self.clear_notes_button.setEnabled(True)
        self.favorite_button.setEnabled(True)
        self.update_favorite_button()
    
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
        
        # Update category and tags
        self.category_label.setText(project.get('category', 'None') or 'None')
        tags = project.get('tags', [])
        self.tags_label.setText(', '.join(tags) if tags else 'None')
        
        # Update notes
        note = project.get('note', '')
        self.notes_text.setText(note or "No notes added yet...")
        
        # Update favorite status
        is_favorite = project.get('is_favorite', False)
        self.update_favorite_button()
    
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
        
        import platform
        system = platform.system().lower()
        
        try:
            if system == 'linux':
                # Use xterm on Linux
                subprocess.Popen(['xterm', '-e', f'cd "{project_path}"; bash'], shell=False)
            elif system == 'windows':
                # Try Windows Terminal first
                try:
                    subprocess.Popen(['wt', '-d', project_path], shell=True)
                except Exception:
                    # Fallback to Command Prompt
                    subprocess.Popen(['cmd', '/k', 'cd', '/d', project_path], shell=True)
            else:
                # Fallback for other systems
                subprocess.Popen(['cmd', '/k', 'cd', '/d', project_path], shell=True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open terminal: {str(e)}")
    
    def open_in_editor(self):
        """Open the project in the system's default text editor."""
        if not self.current_project:
            return
        
        project_path = Path(self.current_project['path'])
        
        import platform
        system = platform.system().lower()
        
        try:
            if system == 'windows':
                # On Windows, try to open with notepad.exe or the system's default text editor
                if self.current_project['main_file']:
                    main_file_path = project_path / self.current_project['main_file']
                    if main_file_path.exists():
                        # Open the main file with the default text editor
                        subprocess.Popen(['notepad.exe', str(main_file_path)], shell=True)
                    else:
                        # Open the project folder with the default editor
                        subprocess.Popen(['notepad.exe', str(project_path)], shell=True)
                else:
                    # Open the project folder with the default editor
                    subprocess.Popen(['notepad.exe', str(project_path)], shell=True)
            elif system == 'linux':
                # On Linux, try to open with gedit or the system's default text editor
                if self.current_project['main_file']:
                    main_file_path = project_path / self.current_project['main_file']
                    if main_file_path.exists():
                        # Try gedit first, then fallback to xdg-open
                        try:
                            subprocess.Popen(['gedit', str(main_file_path)], shell=False)
                        except Exception:
                            subprocess.Popen(['xdg-open', str(main_file_path)], shell=False)
                    else:
                        # Open the project folder
                        try:
                            subprocess.Popen(['gedit', str(project_path)], shell=False)
                        except Exception:
                            subprocess.Popen(['xdg-open', str(project_path)], shell=False)
                else:
                    # Open the project folder
                    try:
                        subprocess.Popen(['gedit', str(project_path)], shell=False)
                    except Exception:
                        subprocess.Popen(['xdg-open', str(project_path)], shell=False)
            else:
                # For other systems, use the system's default application
                if self.current_project['main_file']:
                    main_file_path = project_path / self.current_project['main_file']
                    if main_file_path.exists():
                        QDesktopServices.openUrl(QUrl.fromLocalFile(str(main_file_path)))
                    else:
                        QDesktopServices.openUrl(QUrl.fromLocalFile(str(project_path)))
                else:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(project_path)))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open editor: {str(e)}")
    
    def manage_tags(self):
        """Open dialog to manage project tags."""
        if not self.current_project:
            return
        
        project_path = self.current_project['path']
        current_tags = self.current_project.get('tags', [])
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Tags")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Current tags display
        current_tags_label = QLabel("Current Tags:")
        layout.addWidget(current_tags_label)
        
        current_tags_text = QLabel(', '.join(current_tags) if current_tags else 'No tags')
        current_tags_text.setWordWrap(True)
        layout.addWidget(current_tags_text)
        
        # Add tag section
        add_group = QGroupBox("Add Tag")
        add_layout = QHBoxLayout(add_group)
        
        self.new_tag_input = QLineEdit()
        self.new_tag_input.setPlaceholderText("Enter new tag...")
        add_layout.addWidget(self.new_tag_input)
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.add_tag(project_path, self.new_tag_input.text().strip(), dialog))
        add_layout.addWidget(add_button)
        
        layout.addWidget(add_group)
        
        # Remove tag section
        remove_group = QGroupBox("Remove Tag")
        remove_layout = QHBoxLayout(remove_group)
        
        self.remove_tag_combo = QComboBox()
        self.remove_tag_combo.addItem("Select tag to remove...")
        for tag in current_tags:
            self.remove_tag_combo.addItem(tag)
        remove_layout.addWidget(self.remove_tag_combo)
        
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_tag(project_path, self.remove_tag_combo.currentText(), dialog))
        remove_layout.addWidget(remove_button)
        
        layout.addWidget(remove_group)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.exec()
    
    def add_tag(self, project_path: str, tag: str, dialog: QDialog):
        """Add a tag to a project."""
        if not tag:
            QMessageBox.warning(dialog, "Error", "Please enter a tag name")
            return
        
        try:
            self.scanner.tag_manager.add_tag_to_project(project_path, tag)
            # Refresh current project data
            self.current_project['tags'] = self.scanner.tag_manager.get_project_tags(project_path)
            # Update UI
            self.update_project_details()
            self.populate_project_table()
            # Clear input
            self.new_tag_input.clear()
            QMessageBox.information(dialog, "Success", f"Tag '{tag}' added successfully")
        except Exception as e:
            QMessageBox.warning(dialog, "Error", f"Could not add tag: {str(e)}")
    
    def remove_tag(self, project_path: str, tag: str, dialog: QDialog):
        """Remove a tag from a project."""
        if tag == "Select tag to remove...":
            QMessageBox.warning(dialog, "Error", "Please select a tag to remove")
            return
        
        try:
            self.scanner.tag_manager.remove_tag_from_project(project_path, tag)
            # Refresh current project data
            self.current_project['tags'] = self.scanner.tag_manager.get_project_tags(project_path)
            # Update UI
            self.update_project_details()
            self.populate_project_table()
            # Update combo box
            self.remove_tag_combo.clear()
            self.remove_tag_combo.addItem("Select tag to remove...")
            for tag in self.current_project['tags']:
                self.remove_tag_combo.addItem(tag)
            QMessageBox.information(dialog, "Success", f"Tag '{tag}' removed successfully")
        except Exception as e:
            QMessageBox.warning(dialog, "Error", f"Could not remove tag: {str(e)}")
    
    def set_category(self):
        """Open dialog to set project category."""
        if not self.current_project:
            return
        
        project_path = self.current_project['path']
        current_category = self.current_project.get('category')
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Set Category")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # Current category display
        layout.addWidget(QLabel("Current Category:"))
        current_label = QLabel(current_category or "None")
        layout.addWidget(current_label)
        
        # Category selection
        layout.addWidget(QLabel("Select Category:"))
        category_combo = QComboBox()
        category_combo.addItem("None")
        
        # Add predefined categories
        predefined_categories = self.scanner.tag_manager.get_predefined_categories()
        for category in predefined_categories:
            category_combo.addItem(category)
        
        # Add custom categories
        custom_categories = self.scanner.tag_manager.get_custom_categories()
        for category in custom_categories:
            category_combo.addItem(category)
        
        # Set current selection
        if current_category:
            index = category_combo.findText(current_category)
            if index >= 0:
                category_combo.setCurrentIndex(index)
        
        layout.addWidget(category_combo)
        
        # Custom category input
        custom_group = QGroupBox("Or Create Custom Category")
        custom_layout = QHBoxLayout(custom_group)
        
        custom_input = QLineEdit()
        custom_input.setPlaceholderText("Enter custom category...")
        custom_layout.addWidget(custom_input)
        
        layout.addWidget(custom_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("Set Category")
        ok_button.clicked.connect(lambda: self._set_category_action(project_path, category_combo.currentText(), custom_input.text().strip(), dialog))
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _set_category_action(self, project_path: str, selected_category: str, custom_category: str, dialog: QDialog):
        """Set the category for a project."""
        # Use custom category if provided, otherwise use selected
        category = custom_category if custom_category else selected_category
        
        if category == "None":
            category = None
        
        try:
            self.scanner.tag_manager.set_project_category(project_path, category)
            # Refresh current project data
            self.current_project['category'] = self.scanner.tag_manager.get_project_category(project_path)
            # Update UI
            self.update_project_details()
            self.populate_project_table()
            QMessageBox.information(dialog, "Success", f"Category set to '{category or 'None'}'")
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(dialog, "Error", f"Could not set category: {str(e)}")
    
    def edit_notes(self):
        """Open dialog to edit project notes."""
        if not self.current_project:
            return
        
        project_path = self.current_project['path']
        current_note = self.current_project.get('note', '')
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Project Notes")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(300)
        
        layout = QVBoxLayout(dialog)
        
        # Project info
        info_label = QLabel(f"Project: {self.current_project['name']}")
        info_label.setFont(QFont("", 10, QFont.Bold))
        layout.addWidget(info_label)
        
        # Notes input
        layout.addWidget(QLabel("Notes:"))
        notes_input = QTextBrowser()
        notes_input.setHtml(current_note)
        notes_input.setPlaceholderText("Enter your notes about this project...")
        layout.addWidget(notes_input)
        
        # Edit button
        edit_button = QPushButton("Edit Notes")
        edit_layout = QHBoxLayout()
        edit_layout.addStretch()
        edit_layout.addWidget(edit_button)
        layout.addLayout(edit_layout)
        
        # Make notes input editable when edit button is clicked
        def make_editable():
            notes_input.setReadOnly(False)
            notes_input.setFocus()
            edit_button.setText("Save Notes")
            edit_button.clicked.disconnect()
            edit_button.clicked.connect(lambda: save_notes(notes_input.toHtml(), dialog))
        
        edit_button.clicked.connect(make_editable)
        
        # Save function
        def save_notes(notes_html: str, dialog: QDialog):
            try:
                self.scanner.tag_manager.set_project_note(project_path, notes_html)
                # Refresh current project data
                self.current_project['note'] = self.scanner.tag_manager.get_project_note(project_path)
                # Update UI
                self.update_project_details()
                self.populate_project_table()
                QMessageBox.information(dialog, "Success", "Notes saved successfully")
                dialog.accept()
            except Exception as e:
                QMessageBox.warning(dialog, "Error", f"Could not save notes: {str(e)}")
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        layout.addWidget(cancel_button)
        
        dialog.exec()
    
    def clear_notes(self):
        """Clear project notes."""
        if not self.current_project:
            return
        
        reply = QMessageBox.question(
            self, "Clear Notes", 
            "Are you sure you want to clear the notes for this project?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                project_path = self.current_project['path']
                self.scanner.tag_manager.delete_project_note(project_path)
                # Refresh current project data
                self.current_project['note'] = ''
                # Update UI
                self.update_project_details()
                self.populate_project_table()
                QMessageBox.information(self, "Success", "Notes cleared successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not clear notes: {str(e)}")
    
    def toggle_favorite(self):
        """Toggle project favorite status."""
        if not self.current_project:
            return
        
        try:
            project_path = self.current_project['path']
            is_favorite = self.current_project.get('is_favorite', False)
            
            # Toggle favorite status
            self.scanner.tag_manager.toggle_favorite_project(project_path)
            
            # Refresh current project data
            self.current_project['is_favorite'] = self.scanner.tag_manager.is_favorite_project(project_path)
            
            # Update UI
            self.update_project_details()
            self.populate_project_table()
            self.update_favorite_button()
            
            status = "added to" if self.current_project['is_favorite'] else "removed from"
            QMessageBox.information(self, "Success", f"Project {status} favorites successfully")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not update favorite status: {str(e)}")
    
    def update_favorite_button(self):
        """Update the favorite button appearance based on project status."""
        if not self.current_project:
            return
        
        project_path = self.current_project['path']
        is_favorite = self.scanner.tag_manager.is_favorite_project(project_path)
        
        if is_favorite:
            self.favorite_button.setText("Remove from Favorites")
            self.favorite_button.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold; padding: 5px 15px; border: none; border-radius: 3px;")
        else:
            self.favorite_button.setText("Add to Favorites")
            self.favorite_button.setStyleSheet("")
    
    def update_recent_projects_list(self):
        """Update the recent projects list widget."""
        self.recent_projects_list.clear()
        
        recent_projects = self.scanner.tag_manager.get_recent_projects()
        if not recent_projects:
            self.recent_projects_list.addItem("No recent projects")
            self.recent_projects_list.item(0).setFlags(Qt.NoItemFlags)  # Make non-selectable
            return
        
        for recent_project in recent_projects:
            # Format: "Project Name - 2 hours ago"
            project_name = recent_project['name']
            try:
                accessed_time = datetime.fromisoformat(recent_project['accessed_at'])
                time_diff = datetime.now() - accessed_time
                
                # Format time difference
                if time_diff.days > 0:
                    time_str = f"{time_diff.days} days ago"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    time_str = f"{hours} hours ago"
                elif time_diff.seconds > 60:
                    minutes = time_diff.seconds // 60
                    time_str = f"{minutes} minutes ago"
                else:
                    time_str = "Just now"
            except (ValueError, TypeError, AttributeError):
                # Fallback if there's an issue with the time format
                time_str = "Unknown time"
            
            item_text = f"{project_name} - {time_str}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, recent_project['path'])  # Store project path
            self.recent_projects_list.addItem(item)
    
    def on_recent_project_clicked(self, item):
        """Handle clicking on a recent project in the list."""
        if not item or not item.data(Qt.UserRole):
            return
        
        project_path = item.data(Qt.UserRole)
        # Find and select the project in the main table
        for row in range(self.project_table.rowCount()):
            path_item = self.project_table.item(row, 0)  # Path is in column 0
            if path_item and path_item.data(Qt.UserRole) == project_path:
                self.project_table.selectRow(row)
                self.on_project_selected()
                # Track this access
                self.track_project_access(project_path)
                break
    
    def clear_recent_projects(self):
        """Clear all recent projects."""
        reply = QMessageBox.question(
            self, "Clear Recent Projects",
            "Are you sure you want to clear all recent projects?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.scanner.tag_manager.clear_recent_projects():
                self.update_recent_projects_list()
                QMessageBox.information(self, "Success", "Recent projects cleared successfully")
            else:
                QMessageBox.warning(self, "Error", "Could not clear recent projects")
    
    def track_project_access(self, project_path: str):
        """Track when a project is accessed for recent projects list."""
        if not project_path:
            return
        
        # Find the project data
        project_data = None
        for project in self.projects:
            if project['path'] == project_path:
                project_data = project
                break
        
        if project_data:
            self.scanner.tag_manager.add_recent_project(
                project_path, 
                project_data['name'], 
                project_data
            )
            self.update_recent_projects_list()
    
    def show_dashboard(self):
        """Show the project statistics dashboard."""
        try:
            from .dashboard import show_dashboard
            show_dashboard(self.scanner, self)
        except ImportError as e:
            QMessageBox.warning(
                self, "Dashboard Error",
                f"Could not load dashboard: {str(e)}\n\n"
                "Make sure matplotlib is installed:\n"
                "pip install matplotlib>=3.5.0"
            )
        except Exception as e:
            QMessageBox.warning(
                self, "Dashboard Error",
                f"Could not show dashboard: {str(e)}"
            )
    
    def show_advanced_search(self):
        """Show the advanced search dialog."""
        try:
            from .advanced_search import show_advanced_search
            results = show_advanced_search(self.scanner, self)
            if results:
                self.display_search_results(results)
        except ImportError as e:
            QMessageBox.warning(
                self, "Advanced Search Error",
                f"Could not load advanced search: {str(e)}"
            )
        except Exception as e:
            QMessageBox.warning(
                self, "Advanced Search Error",
                f"Could not show advanced search: {str(e)}"
            )
    
    def display_search_results(self, results: List[Dict[str, Any]]):
        """Display search results in the project table."""
        self.projects = results
        self.update_project_table()
        self.status_label.setText(f"Showing {len(results)} search results")
    
    def select_all_projects(self):
        """Select all projects in the table."""
        for row in range(self.project_table.rowCount()):
            checkbox_item = self.project_table.item(row, 0)
            if checkbox_item:
                checkbox_item.setCheckState(Qt.Checked)
    
    def select_none_projects(self):
        """Deselect all projects in the table."""
        for row in range(self.project_table.rowCount()):
            checkbox_item = self.project_table.item(row, 0)
            if checkbox_item:
                checkbox_item.setCheckState(Qt.Unchecked)
    
    def get_selected_projects(self) -> List[Dict[str, Any]]:
        """Get list of selected projects."""
        selected_projects = []
        for row in range(self.project_table.rowCount()):
            checkbox_item = self.project_table.item(row, 0)
            if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                if row < len(self.projects):
                    selected_projects.append(self.projects[row])
        return selected_projects
    
    def batch_open_projects(self):
        """Open all selected projects."""
        selected_projects = self.get_selected_projects()
        if not selected_projects:
            QMessageBox.warning(self, "No Selection", "Please select at least one project to open.")
            return
        
        for project in selected_projects:
            project_path = project.get('path', '')
            if project_path and os.path.exists(project_path):
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(project_path)
                    elif os.name == 'posix':  # macOS/Linux
                        subprocess.run(['open', project_path] if sys.platform == 'darwin' else ['xdg-open', project_path])
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not open project {project.get('name', '')}: {str(e)}")
    
    def batch_toggle_favorite(self):
        """Toggle favorite status for selected projects."""
        selected_projects = self.get_selected_projects()
        if not selected_projects:
            QMessageBox.warning(self, "No Selection", "Please select at least one project.")
            return
        
        for project in selected_projects:
            project_path = project.get('path', '')
            if project_path:
                current_favorite = project.get('is_favorite', False)
                self.scanner.tag_manager.set_favorite(project_path, not current_favorite)
                project['is_favorite'] = not current_favorite
        
        self.update_project_table()
        QMessageBox.information(self, "Success", f"Updated favorite status for {len(selected_projects)} projects.")
    
    def batch_add_tags(self):
        """Add tags to selected projects."""
        selected_projects = self.get_selected_projects()
        if not selected_projects:
            QMessageBox.warning(self, "No Selection", "Please select at least one project.")
            return
        
        # Ask user for tags
        tags_input, ok = QMessageBox.getText(
            self, "Add Tags", 
            "Enter tags (comma-separated):",
            QLineEdit.Normal, ""
        )
        
        if ok and tags_input:
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            
            for project in selected_projects:
                project_path = project.get('path', '')
                if project_path:
                    existing_tags = project.get('tags', [])
                    for tag in tags:
                        if tag not in existing_tags:
                            existing_tags.append(tag)
                    self.scanner.tag_manager.add_tags(project_path, existing_tags)
                    project['tags'] = existing_tags
            
            self.update_project_table()
            QMessageBox.information(self, "Success", f"Added tags to {len(selected_projects)} projects.")
    
    def batch_set_category(self):
        """Set category for selected projects."""
        selected_projects = self.get_selected_projects()
        if not selected_projects:
            QMessageBox.warning(self, "No Selection", "Please select at least one project.")
            return
        
        # Get available categories
        all_projects = self.scanner.get_projects()
        categories = sorted(set(p.get('category', 'Uncategorized') for p in all_projects))
        
        # Create category selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Set Category")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Select category:"))
        
        category_combo = QComboBox()
        category_combo.addItems(categories)
        category_combo.setEditable(True)
        layout.addWidget(category_combo)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.Accepted:
            selected_category = category_combo.currentText()
            
            for project in selected_projects:
                project_path = project.get('path', '')
                if project_path:
                    self.scanner.tag_manager.set_category(project_path, selected_category)
                    project['category'] = selected_category
            
            self.update_project_table()
            QMessageBox.information(self, "Success", f"Set category for {len(selected_projects)} projects.")
    
    def show_context_menu(self, position):
        """Show context menu for batch operations."""
        from PySide6.QtGui import QMenu
        
        menu = QMenu(self)
        
        # Get selected rows
        selected_rows = set()
        for item in self.project_table.selectedItems():
            selected_rows.add(item.row())
        
        has_selection = len(selected_rows) > 0
        
        # Single project actions
        if len(selected_rows) == 1:
            open_action = menu.addAction("Open Project")
            open_action.triggered.connect(self.open_project_folder)
            
            menu.addSeparator()
        
        # Batch selection actions
        if has_selection:
            # Selection actions
            select_action = menu.addAction("Select All")
            select_action.triggered.connect(self.select_all_projects)
            
            deselect_action = menu.addAction("Deselect All")
            deselect_action.triggered.connect(self.select_none_projects)
            
            menu.addSeparator()
            
            # Batch operations
            open_batch_action = menu.addAction("Open Selected Projects")
            open_batch_action.triggered.connect(self.batch_open_projects)
            
            favorite_batch_action = menu.addAction("Toggle Favorite Status")
            favorite_batch_action.triggered.connect(self.batch_toggle_favorite)
            
            tags_batch_action = menu.addAction("Add Tags to Selected")
            tags_batch_action.triggered.connect(self.batch_add_tags)
            
            category_batch_action = menu.addAction("Set Category for Selected")
            category_batch_action.triggered.connect(self.batch_set_category)
            
            menu.addSeparator()
        
        # Global actions
        scan_action = menu.addAction("Rescan Projects")
        scan_action.triggered.connect(self.scan_projects)
        
        search_action = menu.addAction("Advanced Search")
        search_action.triggered.connect(self.show_advanced_search)
        
        dashboard_action = menu.addAction("Show Dashboard")
        dashboard_action.triggered.connect(self.show_dashboard)
        
        # Show the menu
        menu.exec_(self.project_table.viewport().mapToGlobal(position))


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
