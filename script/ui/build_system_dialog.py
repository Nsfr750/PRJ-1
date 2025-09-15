#!/usr/bin/env python3
"""
Build System and Dependency Management Dialog
Provides UI for managing build systems and project dependencies.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QLabel, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QComboBox, QLineEdit, QSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QMessageBox, QProgressBar, QSplitter,
    QTreeWidget, QTreeWidgetItem, QFileDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QIcon, QFont

from script.build_system import BuildSystemDetector
from script.dependency_manager import DependencyManager
from script.backup_system import BackupSystem
from script.file_watcher import FileSystemWatcher
from script.lang.lang_mgr import get_text


class BuildSystemTab(QWidget):
    """Tab for displaying and managing build system information."""
    
    def __init__(self, project_path: str, build_system_info: Dict[str, Any], lang='en'):
        super().__init__()
        self.project_path = project_path
        self.build_system_info = build_system_info
        self.lang = lang
        self.build_detector = BuildSystemDetector()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Build system info group
        info_group = QGroupBox(get_text('build_system.info', 'Build System Information', lang=self.lang))
        info_layout = QFormLayout()
        
        # Build system type
        self.type_label = QLabel(self.build_system_info.get('type', 'Unknown'))
        info_layout.addRow(get_text('build_system.type', 'Type:', lang=self.lang), self.type_label)
        
        # Description
        self.desc_label = QLabel(self.build_system_info.get('description', 'No description'))
        self.desc_label.setWordWrap(True)
        info_layout.addRow(get_text('build_system.description', 'Description:', lang=self.lang), self.desc_label)
        
        # Files
        files = self.build_system_info.get('files', [])
        self.files_text = QTextEdit()
        self.files_text.setPlainText('\n'.join(files) if files else 'No files found')
        self.files_text.setMaximumHeight(100)
        self.files_text.setReadOnly(True)
        info_layout.addRow(get_text('build_system.files', 'Files:', lang=self.lang), self.files_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Build commands group
        commands_group = QGroupBox(get_text('build_system.commands', 'Build Commands', lang=self.lang))
        commands_layout = QVBoxLayout()
        
        self.commands_table = QTableWidget()
        self.commands_table.setColumnCount(2)
        self.commands_table.setHorizontalHeaderLabels([
            get_text('build_system.command', 'Command', lang=self.lang),
            get_text('build_system.description', 'Description', lang=self.lang)
        ])
        self.commands_table.horizontalHeader().setStretchLastSection(True)
        
        # Populate commands
        commands = self.build_system_info.get('build_commands', [])
        self.commands_table.setRowCount(len(commands))
        for i, command in enumerate(commands):
            self.commands_table.setItem(i, 0, QTableWidgetItem(command))
            self.commands_table.setItem(i, 1, QTableWidgetItem(f"Build command {i+1}"))
        
        commands_layout.addWidget(self.commands_table)
        commands_group.setLayout(commands_layout)
        layout.addWidget(commands_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton(get_text('build_system.refresh', 'Refresh', lang=self.lang))
        self.refresh_btn.clicked.connect(self.refresh_build_system)
        button_layout.addWidget(self.refresh_btn)
        
        self.copy_command_btn = QPushButton(get_text('build_system.copy_command', 'Copy Command', lang=self.lang))
        self.copy_command_btn.clicked.connect(self.copy_selected_command)
        button_layout.addWidget(self.copy_command_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def refresh_build_system(self):
        """Refresh build system information."""
        try:
            new_info = self.build_detector.detect_build_system(self.project_path)
            self.build_system_info = new_info
            
            # Update UI
            self.type_label.setText(new_info.get('type', 'Unknown'))
            self.desc_label.setText(new_info.get('description', 'No description'))
            
            files = new_info.get('files', [])
            self.files_text.setPlainText('\n'.join(files) if files else 'No files found')
            
            # Update commands table
            commands = new_info.get('build_commands', [])
            self.commands_table.setRowCount(len(commands))
            for i, command in enumerate(commands):
                self.commands_table.setItem(i, 0, QTableWidgetItem(command))
                self.commands_table.setItem(i, 1, QTableWidgetItem(f"Build command {i+1}"))
            
            QMessageBox.information(self, get_text('build_system.refresh_success', 'Success', lang=self.lang),
                                  get_text('build_system.refreshed', 'Build system information refreshed', lang=self.lang))
        except Exception as e:
            QMessageBox.warning(self, get_text('build_system.refresh_error', 'Error', lang=self.lang),
                              f"Failed to refresh build system: {str(e)}")
    
    def copy_selected_command(self):
        """Copy selected command to clipboard."""
        current_row = self.commands_table.currentRow()
        if current_row >= 0:
            command_item = self.commands_table.item(current_row, 0)
            if command_item:
                command = command_item.text()
                clipboard = self.commands_table.clipboard()
                clipboard.setText(command)
                QMessageBox.information(self, get_text('build_system.copied', 'Copied', lang=self.lang),
                                      get_text('build_system.command_copied', 'Command copied to clipboard', lang=self.lang))


class DependenciesTab(QWidget):
    """Tab for displaying and managing project dependencies."""
    
    def __init__(self, project_path: str, lang='en'):
        super().__init__()
        self.project_path = project_path
        self.lang = lang
        self.dependency_manager = DependencyManager()
        self.current_analysis = {}
        self.init_ui()
        
        # Load dependencies asynchronously
        QTimer.singleShot(100, self.load_dependencies)
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Progress bar for loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Dependencies tree
        self.dependencies_tree = QTreeWidget()
        self.dependencies_tree.setHeaderLabels([
            get_text('dependencies.package', 'Package', lang=self.lang),
            get_text('dependencies.version', 'Version:', lang=self.lang),
            get_text('dependencies.type', 'Type', lang=self.lang),
            get_text('dependencies.status', 'Status', lang=self.lang)
        ])
        self.dependencies_tree.setColumnWidth(0, 200)
        self.dependencies_tree.setColumnWidth(1, 150)
        self.dependencies_tree.setColumnWidth(2, 100)
        self.dependencies_tree.setColumnWidth(3, 100)
        
        layout.addWidget(self.dependencies_tree)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton(get_text('dependencies.refresh', 'Refresh', lang=self.lang))
        self.refresh_btn.clicked.connect(self.load_dependencies)
        button_layout.addWidget(self.refresh_btn)
        
        self.update_btn = QPushButton(get_text('dependencies.update', 'Update Selected', lang=self.lang))
        self.update_btn.clicked.connect(self.update_selected_dependencies)
        button_layout.addWidget(self.update_btn)
        
        self.install_btn = QPushButton(get_text('dependencies.install', 'Install New', lang=self.lang))
        self.install_btn.clicked.connect(self.install_new_dependency)
        button_layout.addWidget(self.install_btn)
        
        self.remove_btn = QPushButton(get_text('dependencies.remove', 'Remove Selected', lang=self.lang))
        self.remove_btn.clicked.connect(self.remove_selected_dependencies)
        button_layout.addWidget(self.remove_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Statistics label
        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def load_dependencies(self):
        """Load dependency analysis."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Disable buttons during loading
        self.refresh_btn.setEnabled(False)
        self.update_btn.setEnabled(False)
        self.install_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        
        # Load in a separate thread to avoid blocking UI
        self.dependency_thread = DependencyAnalysisThread(self.project_path, self.dependency_manager)
        self.dependency_thread.analysis_complete.connect(self.on_analysis_complete)
        self.dependency_thread.analysis_error.connect(self.on_analysis_error)
        self.dependency_thread.start()
    
    def on_analysis_complete(self, analysis: Dict[str, Any]):
        """Handle completed dependency analysis."""
        self.current_analysis = analysis
        self.populate_dependencies_tree(analysis)
        self.update_statistics(analysis)
        
        self.progress_bar.setVisible(False)
        self.refresh_btn.setEnabled(True)
        self.update_btn.setEnabled(True)
        self.install_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
    
    def on_analysis_error(self, error: str):
        """Handle dependency analysis error."""
        self.progress_bar.setVisible(False)
        self.refresh_btn.setEnabled(True)
        self.update_btn.setEnabled(True)
        self.install_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
        
        QMessageBox.warning(self, get_text('dependencies.analysis_error', 'Analysis Error', lang=self.lang),
                          f"Failed to analyze dependencies: {error}")
    
    def populate_dependencies_tree(self, analysis: Dict[str, Any]):
        """Populate the dependencies tree with analysis results."""
        self.dependencies_tree.clear()
        
        dependencies = analysis.get('dependencies', {})
        outdated_deps = analysis.get('outdated_dependencies', [])
        vulnerabilities = analysis.get('vulnerabilities', [])
        
        for pm_name, pm_deps in dependencies.items():
            # Create package manager item
            pm_item = QTreeWidgetItem(self.dependencies_tree)
            pm_item.setText(0, pm_name.upper())
            pm_item.setText(1, f"{len(pm_deps)} packages")
            pm_item.setExpanded(True)
            
            # Add dependencies
            for dep in pm_deps:
                dep_item = QTreeWidgetItem(pm_item)
                dep_item.setText(0, dep.get('name', 'Unknown'))
                dep_item.setText(1, dep.get('current_version', dep.get('version_spec', '')))
                dep_item.setText(2, dep.get('type', 'Unknown'))
                
                # Determine status
                status = "Up to date"
                if dep in outdated_deps:
                    status = "Outdated"
                    dep_item.setForeground(3, Qt.red)
                elif any(vuln['dependency'] == dep['name'] for vuln in vulnerabilities):
                    status = "Vulnerable"
                    dep_item.setForeground(3, Qt.darkRed)
                
                dep_item.setText(3, status)
                
                # Store dependency data for later use
                dep_item.setData(0, Qt.UserRole, dep)
    
    def update_statistics(self, analysis: Dict[str, Any]):
        """Update statistics label."""
        total_deps = analysis.get('total_dependencies', 0)
        outdated_count = len(analysis.get('outdated_dependencies', []))
        vuln_count = len(analysis.get('vulnerabilities', []))
        
        stats_text = get_text('dependencies.stats', 'Total: {total} | Outdated: {outdated} | Vulnerabilities: {vuln}', lang=self.lang).format(
            total=total_deps, outdated=outdated_count, vuln=vuln_count)
        self.stats_label.setText(stats_text)
    
    def update_selected_dependencies(self):
        """Update selected dependencies."""
        selected_items = self.dependencies_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, get_text('dependencies.no_selection', 'No Selection', lang=self.lang),
                              get_text('dependencies.select_deps', 'Please select dependencies to update', lang=self.lang))
            return
        
        dependencies = []
        package_manager = None
        
        for item in selected_items:
            dep_data = item.data(0, Qt.UserRole)
            if dep_data:
                dependencies.append(dep_data['name'])
                package_manager = dep_data.get('package_manager')
        
        if not package_manager:
            QMessageBox.warning(self, get_text('dependencies.no_pm', 'No Package Manager', lang=self.lang),
                              get_text('dependencies.cannot_determine_pm', 'Cannot determine package manager', lang=self.lang))
            return
        
        # Confirm update
        reply = QMessageBox.question(self, get_text('dependencies.confirm_update', 'Confirm Update', lang=self.lang),
                                   f"Update {len(dependencies)} dependencies using {package_manager}?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = self.dependency_manager.update_dependencies(
                self.project_path, package_manager, dependencies)
            
            if success:
                QMessageBox.information(self, get_text('dependencies.update_success', 'Success', lang=self.lang),
                                      get_text('dependencies.updated', 'Dependencies updated successfully', lang=self.lang))
                self.load_dependencies()  # Refresh
            else:
                QMessageBox.warning(self, get_text('dependencies.update_error', 'Error', lang=self.lang),
                                  get_text('dependencies.update_failed', 'Failed to update dependencies', lang=self.lang))
    
    def install_new_dependency(self):
        """Install a new dependency."""
        # Simple dialog for dependency name input
        dialog = QDialog(self)
        dialog.setWindowTitle(get_text('dependencies.install_dep', 'Install Dependency', lang=self.lang))
        layout = QFormLayout()
        
        name_input = QLineEdit()
        version_input = QLineEdit()
        pm_combo = QComboBox()
        
        # Add supported package managers
        supported_pms = self.dependency_manager.get_supported_package_managers()
        for pm_name, pm_desc in supported_pms.items():
            pm_combo.addItem(pm_desc, pm_name)
        
        layout.addRow(get_text('dependencies.name', 'Name:', lang=self.lang), name_input)
        layout.addRow(get_text('dependencies.version', 'Version:', lang=self.lang), version_input)
        layout.addRow(get_text('dependencies.package_manager', 'Package Manager:', lang=self.lang), pm_combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.Accepted:
            name = name_input.text().strip()
            version = version_input.text().strip()
            pm_name = pm_combo.currentData()
            
            if not name:
                QMessageBox.warning(self, get_text('dependencies.no_name', 'No Name', lang=self.lang),
                                  get_text('dependencies.enter_name', 'Please enter dependency name', lang=self.lang))
                return
            
            dep_spec = name
            if version:
                dep_spec = f"{name}{version}"
            
            success = self.dependency_manager.install_dependencies(
                self.project_path, pm_name, [dep_spec])
            
            if success:
                QMessageBox.information(self, get_text('dependencies.install_success', 'Success', lang=self.lang),
                                      get_text('dependencies.installed', 'Dependency installed successfully', lang=self.lang))
                self.load_dependencies()  # Refresh
            else:
                QMessageBox.warning(self, get_text('dependencies.install_error', 'Error', lang=self.lang),
                                  get_text('dependencies.install_failed', 'Failed to install dependency', lang=self.lang))
    
    def remove_selected_dependencies(self):
        """Remove selected dependencies."""
        selected_items = self.dependencies_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, get_text('dependencies.no_selection', 'No Selection', lang=self.lang),
                              get_text('dependencies.select_deps', 'Please select dependencies to remove', lang=self.lang))
            return
        
        dependencies = []
        package_manager = None
        
        for item in selected_items:
            dep_data = item.data(0, Qt.UserRole)
            if dep_data:
                dependencies.append(dep_data['name'])
                package_manager = dep_data.get('package_manager')
        
        if not package_manager:
            QMessageBox.warning(self, get_text('dependencies.no_pm', 'No Package Manager', lang=self.lang),
                              get_text('dependencies.cannot_determine_pm', 'Cannot determine package manager', lang=self.lang))
            return
        
        # Confirm removal
        reply = QMessageBox.question(self, get_text('dependencies.confirm_remove', 'Confirm Remove', lang=self.lang),
                                   f"Remove {len(dependencies)} dependencies using {package_manager}?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = self.dependency_manager.remove_dependencies(
                self.project_path, package_manager, dependencies)
            
            if success:
                QMessageBox.information(self, get_text('dependencies.remove_success', 'Success', lang=self.lang),
                                      get_text('dependencies.removed', 'Dependencies removed successfully', lang=self.lang))
                self.load_dependencies()  # Refresh
            else:
                QMessageBox.warning(self, get_text('dependencies.remove_error', 'Error', lang=self.lang),
                                  get_text('dependencies.remove_failed', 'Failed to remove dependencies', lang=self.lang))


class BackupTab(QWidget):
    """Tab for managing project backups."""
    
    def __init__(self, project_path: str, lang='en'):
        super().__init__()
        self.project_path = project_path
        self.lang = lang
        self.backup_system = BackupSystem()
        self.init_ui()
        
        # Load backup list
        self.load_backup_list()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Backup configuration group
        config_group = QGroupBox(get_text('backup.configuration', 'Backup Configuration', lang=self.lang))
        config_layout = QFormLayout()
        
        self.auto_backup_cb = QCheckBox()
        self.auto_backup_cb.setChecked(self.backup_system.config.get('auto_backup', True))
        config_layout.addRow(get_text('backup.auto_backup', 'Automatic Backup:', lang=self.lang), self.auto_backup_cb)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 168)  # 1 hour to 1 week
        self.interval_spin.setValue(self.backup_system.config.get('backup_interval_hours', 24))
        self.interval_spin.setSuffix(get_text('backup.hours', ' hours', lang=self.lang))
        config_layout.addRow(get_text('backup.interval', 'Backup Interval:', lang=self.lang), self.interval_spin)
        
        self.max_backups_spin = QSpinBox()
        self.max_backups_spin.setRange(1, 100)
        self.max_backups_spin.setValue(self.backup_system.config.get('max_backups', 10))
        config_layout.addRow(get_text('backup.max_backups', 'Maximum Backups:', lang=self.lang), self.max_backups_spin)
        
        self.compress_cb = QCheckBox()
        self.compress_cb.setChecked(self.backup_system.config.get('compress_backups', True))
        config_layout.addRow(get_text('backup.compress', 'Compress Backups:', lang=self.lang), self.compress_cb)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Backup list
        list_group = QGroupBox(get_text('backup.existing_backups', 'Existing Backups', lang=self.lang))
        list_layout = QVBoxLayout()
        
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(4)
        self.backup_table.setHorizontalHeaderLabels([
            get_text('backup.name', 'Name', lang=self.lang),
            get_text('backup.date', 'Date', lang=self.lang),
            get_text('backup.size', 'Size', lang=self.lang),
            get_text('backup.compressed', 'Compressed', lang=self.lang)
        ])
        self.backup_table.horizontalHeader().setStretchLastSection(True)
        
        list_layout.addWidget(self.backup_table)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.create_btn = QPushButton(get_text('backup.create', 'Create Backup', lang=self.lang))
        self.create_btn.clicked.connect(self.create_backup)
        button_layout.addWidget(self.create_btn)
        
        self.restore_btn = QPushButton(get_text('backup.restore', 'Restore Selected', lang=self.lang))
        self.restore_btn.clicked.connect(self.restore_selected_backup)
        button_layout.addWidget(self.restore_btn)
        
        self.delete_btn = QPushButton(get_text('backup.delete', 'Delete Selected', lang=self.lang))
        self.delete_btn.clicked.connect(self.delete_selected_backup)
        button_layout.addWidget(self.delete_btn)
        
        self.save_config_btn = QPushButton(get_text('backup.save_config', 'Save Config', lang=self.lang))
        self.save_config_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_config_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def load_backup_list(self):
        """Load the list of existing backups."""
        backups = self.backup_system.list_backups()
        
        self.backup_table.setRowCount(len(backups))
        for i, backup in enumerate(backups):
            self.backup_table.setItem(i, 0, QTableWidgetItem(backup.get('name', '')))
            self.backup_table.setItem(i, 1, QTableWidgetItem(backup.get('created', '')))
            
            size_bytes = backup.get('size', 0)
            size_mb = size_bytes / (1024 * 1024)
            self.backup_table.setItem(i, 2, QTableWidgetItem(f"{size_mb:.2f} MB"))
            
            compressed = backup.get('compressed', False)
            self.backup_table.setItem(i, 3, QTableWidgetItem("Yes" if compressed else "No"))
    
    def create_backup(self):
        """Create a new backup."""
        try:
            backup_file = self.backup_system.create_backup()
            if backup_file:
                QMessageBox.information(self, get_text('backup.create_success', 'Success', lang=self.lang),
                                      get_text('backup.created', 'Backup created successfully', lang=self.lang))
                self.load_backup_list()  # Refresh
            else:
                QMessageBox.warning(self, get_text('backup.create_error', 'Error', lang=self.lang),
                                  get_text('backup.create_failed', 'Failed to create backup', lang=self.lang))
        except Exception as e:
            QMessageBox.warning(self, get_text('backup.create_error', 'Error', lang=self.lang),
                              f"Failed to create backup: {str(e)}")
    
    def restore_selected_backup(self):
        """Restore the selected backup."""
        current_row = self.backup_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, get_text('backup.no_selection', 'No Selection', lang=self.lang),
                              get_text('backup.select_backup', 'Please select a backup to restore', lang=self.lang))
            return
        
        backup_name = self.backup_table.item(current_row, 0).text()
        
        # Confirm restore
        reply = QMessageBox.question(self, get_text('backup.confirm_restore', 'Confirm Restore', lang=self.lang),
                                   f"Restore backup '{backup_name}'? This will overwrite current data.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Get restore path
            restore_path = QFileDialog.getExistingDirectory(self, get_text('backup.select_restore_path', 'Select Restore Path', lang=self.lang))
            if restore_path:
                success = self.backup_system.restore_backup(backup_name, restore_path)
                if success:
                    QMessageBox.information(self, get_text('backup.restore_success', 'Success', lang=self.lang),
                                          get_text('backup.restored', 'Backup restored successfully', lang=self.lang))
                else:
                    QMessageBox.warning(self, get_text('backup.restore_error', 'Error', lang=self.lang),
                                      get_text('backup.restore_failed', 'Failed to restore backup', lang=self.lang))
    
    def delete_selected_backup(self):
        """Delete the selected backup."""
        current_row = self.backup_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, get_text('backup.no_selection', 'No Selection', lang=self.lang),
                              get_text('backup.select_backup', 'Please select a backup to delete', lang=self.lang))
            return
        
        backup_name = self.backup_table.item(current_row, 0).text()
        
        # Confirm deletion
        reply = QMessageBox.question(self, get_text('backup.confirm_delete', 'Confirm Delete', lang=self.lang),
                                   f"Delete backup '{backup_name}'? This action cannot be undone.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = self.backup_system.delete_backup(backup_name)
            if success:
                QMessageBox.information(self, get_text('backup.delete_success', 'Success', lang=self.lang),
                                      get_text('backup.deleted', 'Backup deleted successfully', lang=self.lang))
                self.load_backup_list()  # Refresh
            else:
                QMessageBox.warning(self, get_text('backup.delete_error', 'Error', lang=self.lang),
                                  get_text('backup.delete_failed', 'Failed to delete backup', lang=self.lang))
    
    def save_config(self):
        """Save backup configuration."""
        config = {
            'auto_backup': self.auto_backup_cb.isChecked(),
            'backup_interval_hours': self.interval_spin.value(),
            'max_backups': self.max_backups_spin.value(),
            'compress_backups': self.compress_cb.isChecked()
        }
        
        success = self.backup_system.update_config(config)
        if success:
            QMessageBox.information(self, get_text('backup.config_saved', 'Success', lang=self.lang),
                                  get_text('backup.config_updated', 'Backup configuration updated', lang=self.lang))
        else:
            QMessageBox.warning(self, get_text('backup.config_error', 'Error', lang=self.lang),
                              get_text('backup.config_failed', 'Failed to update backup configuration', lang=self.lang))


class DependencyAnalysisThread(QThread):
    """Thread for analyzing dependencies without blocking the UI."""
    
    analysis_complete = Signal(dict)
    analysis_error = Signal(str)
    
    def __init__(self, project_path: str, dependency_manager: DependencyManager):
        super().__init__()
        self.project_path = project_path
        self.dependency_manager = dependency_manager
    
    def run(self):
        """Run the dependency analysis."""
        try:
            analysis = self.dependency_manager.analyze_project_dependencies(self.project_path)
            self.analysis_complete.emit(analysis)
        except Exception as e:
            self.analysis_error.emit(str(e))


class BuildSystemDialog(QDialog):
    """Main dialog for build system and dependency management."""
    
    def __init__(self, project_path: str, project_info: Dict[str, Any], parent=None, lang='en'):
        super().__init__(parent)
        self.project_path = project_path
        self.project_info = project_info
        self.lang = lang
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(get_text('build_system_dialog.title', 'Build System & Dependencies', lang=self.lang))
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        
        # Project info
        info_label = QLabel(f"Project: {self.project_info.get('name', 'Unknown')}")
        info_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(info_label)
        
        path_label = QLabel(f"Path: {self.project_path}")
        path_label.setStyleSheet("color: gray;")
        layout.addWidget(path_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Build system tab
        build_system_info = self.project_info.get('build_system', {})
        self.build_system_tab = BuildSystemTab(self.project_path, build_system_info)
        self.tab_widget.addTab(self.build_system_tab, get_text('build_system_dialog.build_tab', 'Build System', lang=self.lang))
        
        # Dependencies tab
        self.dependencies_tab = DependenciesTab(self.project_path)
        self.tab_widget.addTab(self.dependencies_tab, get_text('build_system_dialog.deps_tab', 'Dependencies', lang=self.lang))
        
        # Backup tab
        self.backup_tab = BackupTab(self.project_path, self.lang)
        self.tab_widget.addTab(self.backup_tab, get_text('build_system_dialog.backup_tab', 'Backup', lang=self.lang))
        
        layout.addWidget(self.tab_widget)
        
        # Close button
        close_btn = QPushButton(get_text('common.close', 'Close', lang=self.lang))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
