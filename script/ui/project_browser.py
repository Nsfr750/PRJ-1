#!/usr/bin/env python3
"""
Project Browser Dialog
Provides a browsable interface for projects found in the GitHub folder.
"""

import os
import sys
import subprocess
import json
import gc
import weakref
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Set

from PySide6.QtCore import Qt, QThread, Signal, QUrl, QSettings, QTimer, QSize, QSortFilterProxyModel
from PySide6.QtGui import QFont, QIcon, QDesktopServices, QPalette, QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QProgressBar, QDialogButtonBox, QMessageBox, QHeaderView, QFrame,
    QSplitter, QTextBrowser, QGroupBox, QFileDialog, QListWidget, QCheckBox, QListWidgetItem,
    QScrollArea, QWidget, QSizePolicy
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
        
        # Memory optimization attributes
        self._max_visible_projects = 1000  # Limit visible projects
        self._project_cache = weakref.WeakValueDictionary()  # Weak reference cache
        self._table_items_cache = {}  # Cache for table items
        self._memory_cleanup_timer = QTimer()
        self._memory_cleanup_timer.timeout.connect(self._cleanup_memory)
        self._memory_cleanup_timer.start(30000)  # Cleanup every 30 seconds
        
        # UI responsiveness attributes
        self._lazy_load_batch_size = 50  # Number of projects to load at once
        self._lazy_load_delay = 10  # Milliseconds between batches
        self._lazy_load_timer = QTimer()
        self._lazy_load_timer.timeout.connect(self._lazy_load_next_batch)
        self._current_lazy_load_row = 0
        self._is_lazy_loading = False
        self._ui_update_queue = []
        self._ui_update_timer = QTimer()
        self._ui_update_timer.timeout.connect(self._process_ui_update_queue)
        self._ui_update_timer.start(100)  # Process UI updates every 100ms
        
        # Initialize scanner
        self.scanner = ProjectScanner()
        self.projects: List[Dict[str, Any]] = []
        self.filtered_projects: List[Dict[str, Any]] = []
        self.current_project: Optional[Dict[str, Any]] = None
        
        # Set up UI
        self.setup_modern_styling()
        self.setup_ui()
        self.setup_keyboard_shortcuts()
        
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
    
    def setup_modern_styling(self):
        """Set up dark theme styling for the application."""
        # Set application style
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #444444;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #3c3c3c;
                color: #e0e0e0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QPushButton[class="primary"] {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton[class="primary"]:hover {
                background-color: #218838;
            }
            QPushButton[class="primary"]:pressed {
                background-color: #1e7e34;
            }
            QPushButton[class="danger"] {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton[class="danger"]:hover {
                background-color: #c82333;
            }
            QPushButton[class="danger"]:pressed {
                background-color: #bd2130;
            }
            QPushButton[class="info"] {
                background-color: #17a2b8;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton[class="info"]:hover {
                background-color: #138496;
            }
            QPushButton[class="info"]:pressed {
                background-color: #117a8b;
            }
            QPushButton[class="warning"] {
                background-color: #ffc107;
                color: #212529;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton[class="warning"]:hover {
                background-color: #e0a800;
            }
            QPushButton[class="warning"]:pressed {
                background-color: #d39e00;
            }
            QPushButton[class="success"] {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton[class="success"]:hover {
                background-color: #218838;
            }
            QPushButton[class="success"]:pressed {
                background-color: #1e7e34;
            }
            QLineEdit {
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 8px;
                background-color: #3c3c3c;
                color: #e0e0e0;
                selection-background-color: #007acc;
                selection-color: white;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
            QComboBox {
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 6px;
                background-color: #3c3c3c;
                color: #e0e0e0;
                min-width: 100px;
            }
            QComboBox:focus {
                border-color: #007acc;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #e0e0e0;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #e0e0e0;
                border: 2px solid #555555;
                selection-background-color: #007acc;
                selection-color: white;
            }
            QTableWidget {
                border: 2px solid #555555;
                border-radius: 8px;
                background-color: #3c3c3c;
                alternate-background-color: #444444;
                gridline-color: #555555;
                color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
                color: white;
            }
            QHeaderView::section {
                background-color: #4a4a4a;
                padding: 8px;
                border: 1px solid #555555;
                font-weight: bold;
                color: #ffffff;
            }
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 6px;
                text-align: center;
                background-color: #3c3c3c;
                color: #e0e0e0;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 4px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QListWidget {
                border: 2px solid #555555;
                border-radius: 8px;
                background-color: #3c3c3c;
                color: #e0e0e0;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: white;
            }
            QTextBrowser {
                border: 2px solid #555555;
                border-radius: 8px;
                background-color: #3c3c3c;
                color: #e0e0e0;
                padding: 10px;
            }
            QTextBrowser::selected {
                background-color: #007acc;
                color: white;
            }
            QCheckBox {
                color: #e0e0e0;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border-color: #007acc;
            }
            QCheckBox::indicator:hover {
                border-color: #007acc;
            }
            QScrollBar:vertical {
                border: none;
                background: #3c3c3c;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #666666;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #777777;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #3c3c3c;
                height: 12px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #666666;
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #777777;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        # Set modern font
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        
        # Set window icon if available
        try:
            icon_path = Path(__file__).parent.parent.parent / "assets" / "logo.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass
    
    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for common actions."""
        # Search shortcuts
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.focus_search_box)
        
        adv_search_shortcut = QShortcut(QKeySequence("Ctrl+Shift+F"), self)
        adv_search_shortcut.activated.connect(self.show_advanced_search)
        
        # Scan shortcuts
        scan_shortcut = QShortcut(QKeySequence("F5"), self)
        scan_shortcut.activated.connect(self.scan_projects)
        
        # Navigation shortcuts
        dashboard_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        dashboard_shortcut.activated.connect(self.show_dashboard)
        
        # Project selection shortcuts
        select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        select_all_shortcut.activated.connect(self.select_all_projects)
        
        select_none_shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
        select_none_shortcut.activated.connect(self.select_none_projects)
        
        # Project action shortcuts
        open_shortcut = QShortcut(QKeySequence("Enter"), self)
        open_shortcut.activated.connect(self.open_project_folder)
        
        open_shortcut_alt = QShortcut(QKeySequence("Ctrl+O"), self)
        open_shortcut_alt.activated.connect(self.open_project_folder)
        
        favorite_shortcut = QShortcut(QKeySequence("Ctrl+*"), self)
        favorite_shortcut.activated.connect(self.toggle_favorite_project)
        
        favorite_shortcut_alt = QShortcut(QKeySequence("F2"), self)
        favorite_shortcut_alt.activated.connect(self.toggle_favorite_project)
        
        # Batch operation shortcuts
        batch_open_shortcut = QShortcut(QKeySequence("Ctrl+Enter"), self)
        batch_open_shortcut.activated.connect(self.batch_open_projects)
        
        batch_favorite_shortcut = QShortcut(QKeySequence("Ctrl+Shift+F"), self)
        batch_favorite_shortcut.activated.connect(self.batch_toggle_favorite)
        
        # Export shortcuts
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self.export_to_markdown)
        
        # Window management shortcuts
        close_shortcut = QShortcut(QKeySequence("Escape"), self)
        close_shortcut.activated.connect(self.close)
        
        # Help shortcut
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self.show_help)
        
        # Filter shortcuts
        clear_filter_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        clear_filter_shortcut.activated.connect(self.clear_filters)
        
        # Browse directory shortcut
        browse_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        browse_shortcut.activated.connect(self.browse_directory)
        
        # Notes shortcuts
        edit_notes_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        edit_notes_shortcut.activated.connect(self.edit_notes)
    
    def clear_filters(self):
        """Clear all search and filter fields."""
        self.search_box.clear()
        self.language_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
        self.tag_filter_box.clear()
        self.favorite_combo.setCurrentIndex(0)
        self.filter_projects()
    
    def show_help(self):
        """Show keyboard shortcuts help."""
        help_text = """<h2>Keyboard Shortcuts</h2>
        <h3>Search & Navigation</h3>
        <ul>
        <li><b>Ctrl+F</b> - Focus search box</li>
        <li><b>Ctrl+Shift+F</b> - Advanced search</li>
        <li><b>Ctrl+R</b> - Clear all filters</li>
        <li><b>Ctrl+B</b> - Browse directory</li>
        </ul>
        
        <h3>Project Actions</h3>
        <ul>
        <li><b>Enter</b> or <b>Ctrl+O</b> - Open selected project</li>
        <li><b>Ctrl+*</b> or <b>F2</b> - Toggle favorite</li>
        <li><b>Ctrl+N</b> - Edit project notes</li>
        </ul>
        
        <h3>Selection & Batch Operations</h3>
        <ul>
        <li><b>Ctrl+A</b> - Select all projects</li>
        <li><b>Ctrl+Shift+A</b> - Select none</li>
        <li><b>Ctrl+Enter</b> - Open selected projects</li>
        <li><b>Ctrl+Shift+F</b> - Toggle favorite for selected</li>
        </ul>
        
        <h3>System Actions</h3>
        <ul>
        <li><b>F5</b> - Start/refresh scan</li>
        <li><b>Ctrl+D</b> - Show dashboard</li>
        <li><b>Ctrl+E</b> - Export to markdown</li>
        <li><b>F1</b> - Show this help</li>
        <li><b>Escape</b> - Close window</li>
        </ul>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Keyboard Shortcuts")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.exec_()
    
    def focus_search_box(self):
        """Focus the search box."""
        self.search_box.setFocus()
        self.search_box.selectAll()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create custom title bar with window controls
        title_bar = self.create_title_bar()
        layout.addWidget(title_bar)
        
        # Create content widget with margins
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        content_layout.addWidget(splitter)
        
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
        content_layout.addWidget(button_box)
        
        # Add content widget to main layout
        layout.addWidget(content_widget)
        
        # Set window flags for custom title bar
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setWindowTitle("PRJ-1 - Project Browser")
    
    def create_title_bar(self) -> QFrame:
        """Create custom title bar with window controls."""
        title_bar = QFrame()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QFrame#titleBar {
                background-color: #1e1e1e;
                border-bottom: 1px solid #444444;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #e0e0e0;
                padding: 8px;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
            QLabel#titleLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }
        """)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(10, 0, 10, 0)
        
        # Title label
        title_label = QLabel("PRJ-1 - Project Browser")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Minimize button
        self.minimize_button = QPushButton("−")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setToolTip("Minimize")
        self.minimize_button.clicked.connect(self.showMinimized)
        layout.addWidget(self.minimize_button)
        
        # Maximize/Restore button
        self.maximize_button = QPushButton("□")
        self.maximize_button.setFixedSize(30, 30)
        self.maximize_button.setToolTip("Maximize")
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)
        layout.addWidget(self.maximize_button)
        
        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setToolTip("Close")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)
        
        return title_bar
    
    def toggle_maximize_restore(self):
        """Toggle between maximized and normal window state."""
        if self.isMaximized():
            self.showNormal()
            self.maximize_button.setText("□")
            self.maximize_button.setToolTip("Maximize")
        else:
            self.showMaximized()
            self.maximize_button.setText("❐")
            self.maximize_button.setToolTip("Restore")
    
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
        
        self.start_scan_button = QPushButton("▶ Start Scan")
        self.start_scan_button.clicked.connect(self.start_scanning)
        self.start_scan_button.setProperty("class", "primary")
        scan_buttons_layout.addWidget(self.start_scan_button)
        
        self.stop_scan_button = QPushButton("⏹ Stop Scan")
        self.stop_scan_button.clicked.connect(self.stop_scanning)
        self.stop_scan_button.setEnabled(False)  # Disabled initially
        self.stop_scan_button.setProperty("class", "danger")
        scan_buttons_layout.addWidget(self.stop_scan_button)
        
        # Export button
        self.export_button = QPushButton("📊 Export")
        self.export_button.clicked.connect(self.export_to_markdown)
        self.export_button.setProperty("class", "info")
        scan_buttons_layout.addWidget(self.export_button)
        
        # Dashboard button
        self.dashboard_button = QPushButton("📈 Dashboard")
        self.dashboard_button.clicked.connect(self.show_dashboard)
        self.dashboard_button.setProperty("class", "warning")
        scan_buttons_layout.addWidget(self.dashboard_button)
        
        # Advanced search button
        self.advanced_search_button = QPushButton("🔍 Advanced Search")
        self.advanced_search_button.clicked.connect(self.show_advanced_search)
        self.advanced_search_button.setProperty("class", "success")
        scan_buttons_layout.addWidget(self.advanced_search_button)
        
        controls_layout.addLayout(scan_buttons_layout, 7, 0, 1, 2)
        
        # Batch operations layout
        batch_layout = QHBoxLayout()
        
        # Select all/none buttons
        self.select_all_button = QPushButton("☑ Select All")
        self.select_all_button.clicked.connect(self.select_all_projects)
        self.select_all_button.setProperty("class", "info")
        self.select_all_button.setMaximumWidth(120)
        batch_layout.addWidget(self.select_all_button)
        
        self.select_none_button = QPushButton("☐ Select None")
        self.select_none_button.clicked.connect(self.select_none_projects)
        self.select_none_button.setProperty("class", "info")
        self.select_none_button.setMaximumWidth(120)
        batch_layout.addWidget(self.select_none_button)
        
        batch_layout.addWidget(QLabel("|"))
        
        # Batch operation buttons
        self.batch_open_button = QPushButton("📂 Open Selected")
        self.batch_open_button.clicked.connect(self.batch_open_projects)
        self.batch_open_button.setProperty("class", "primary")
        batch_layout.addWidget(self.batch_open_button)
        
        self.batch_favorite_button = QPushButton("⭐ Toggle Favorite")
        self.batch_favorite_button.clicked.connect(self.batch_toggle_favorite)
        self.batch_favorite_button.setProperty("class", "warning")
        batch_layout.addWidget(self.batch_favorite_button)
        
        self.batch_tag_button = QPushButton("🏷️ Add Tags")
        self.batch_tag_button.clicked.connect(self.batch_add_tags)
        self.batch_tag_button.setProperty("class", "success")
        batch_layout.addWidget(self.batch_tag_button)
        
        self.batch_category_button = QPushButton("📁 Set Category")
        self.batch_category_button.clicked.connect(self.batch_set_category)
        self.batch_category_button.setProperty("class", "primary")
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
            "☑", "📁 Name", "🐍 Language", "📦 Version", "📂 Category", "🏷️ Tags", "📏 Size", "📅 Modified", "🔀 Git", "📝 Notes", "⭐ Favorite"
        ])
        
        # Set table properties for better appearance
        self.project_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.project_table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.project_table.setAlternatingRowColors(True)
        self.project_table.setShowGrid(True)
        self.project_table.verticalHeader().setVisible(False)
        self.project_table.horizontalHeader().setStretchLastSection(False)
        
        # Set column widths for better readability
        self.project_table.setColumnWidth(0, 30)   # Checkbox
        self.project_table.setColumnWidth(1, 200)  # Name
        self.project_table.setColumnWidth(2, 100)  # Language
        self.project_table.setColumnWidth(3, 80)   # Version
        self.project_table.setColumnWidth(4, 100)  # Category
        self.project_table.setColumnWidth(5, 150)  # Tags
        self.project_table.setColumnWidth(6, 80)   # Size
        self.project_table.setColumnWidth(7, 120)  # Modified
        self.project_table.setColumnWidth(8, 50)   # Git
        self.project_table.setColumnWidth(9, 50)   # Notes
        self.project_table.setColumnWidth(10, 60)  # Favorite
        
        # Enable sorting
        self.project_table.setSortingEnabled(True)
        
        # Connect signals
        self.project_table.itemClicked.connect(self.on_project_selected)
        self.project_table.itemSelectionChanged.connect(self.on_project_selection_changed)
        self.project_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.project_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Set column resize modes for better layout
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
        """Handle completion of project scanning with memory optimization."""
        # Clear existing data and caches
        self.projects.clear()
        self.filtered_projects.clear()
        self._table_items_cache.clear()
        self._project_cache.clear()
        
        # Store projects with memory optimization
        self.projects = projects
        
        # Optimize project data for memory usage
        for project in self.projects:
            # Convert datetime objects to strings for storage
            if isinstance(project.get('modified'), datetime):
                project['modified_str'] = project['modified'].strftime("%Y-%m-%d %H:%M")
            
            # Limit tags to prevent memory bloat
            if 'tags' in project and len(project['tags']) > 10:
                project['tags'] = project['tags'][:10]
            
            # Truncate long descriptions
            if 'description' in project and len(project['description']) > 200:
                project['description'] = project['description'][:200] + '...'
            
            # Truncate long notes
            if 'note' in project and len(project['note']) > 500:
                project['note'] = project['note'][:500] + '...'
        
        # Apply initial filter
        self.filter_projects()
        
        # Update UI components
        self.progress_bar.setVisible(False)
        self.start_scan_button.setEnabled(True)
        self.stop_scan_button.setEnabled(False)
        
        # Update language combo box
        self.update_language_combo()
        
        # Update category combo box
        self.update_category_combo()
        
        # Populate project table
        self.populate_project_table()
        
        # Force garbage collection after loading projects
        gc.collect()
        
        # Update status with memory info
        total_projects = len(projects)
        visible_projects = min(len(self.filtered_projects), self._max_visible_projects)
        if total_projects > self._max_visible_projects:
            self.status_label.setText(
                f"Loaded {total_projects} projects, showing {visible_projects} "
                f"(limited for memory/performance)"
            )
        else:
            self.status_label.setText(f"Found {total_projects} projects")
    
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
    
    def _cleanup_memory(self):
        """Clean up memory to prevent memory bloat."""
        try:
            # Clear table items cache if it's too large
            if len(self._table_items_cache) > 5000:
                self._table_items_cache.clear()
            
            # Force garbage collection
            gc.collect()
            
            # Optimize filtered projects list if too large
            if len(self.filtered_projects) > self._max_visible_projects:
                self.filtered_projects = self.filtered_projects[:self._max_visible_projects]
                self.status_label.setText(f"Showing first {self._max_visible_projects} projects (filtered)")
        except Exception as e:
            print(f"Memory cleanup error: {e}")
    
    def _lazy_load_next_batch(self):
        """Load the next batch of projects for lazy loading."""
        if not self._is_lazy_loading:
            self._lazy_load_timer.stop()
            return
        
        try:
            # Calculate batch range
            start_row = self._current_lazy_load_row
            end_row = min(start_row + self._lazy_load_batch_size, len(self.filtered_projects))
            
            if start_row >= len(self.filtered_projects):
                # Finished loading all projects
                self._is_lazy_loading = False
                self._lazy_load_timer.stop()
                self.status_label.setText(f"Loaded {len(self.filtered_projects)} projects")
                return
            
            # Load current batch
            self._load_project_batch(start_row, end_row)
            
            # Update progress
            self._current_lazy_load_row = end_row
            progress = int((end_row / len(self.filtered_projects)) * 100)
            self.status_label.setText(f"Loading projects... {progress}%")
            
            # Schedule next batch
            self._lazy_load_timer.start(self._lazy_load_delay)
            
        except Exception as e:
            print(f"Lazy loading error: {e}")
            self._is_lazy_loading = False
            self._lazy_load_timer.stop()
    
    def _load_project_batch(self, start_row: int, end_row: int):
        """Load a batch of projects into the table."""
        visible_projects = self.filtered_projects[:self._max_visible_projects]
        
        for row in range(start_row, min(end_row, len(visible_projects))):
            project = visible_projects[row]
            
            # Use cached items when possible
            cache_key = f"{project['path']}_{row}"
            
            # Checkbox for batch selection
            if cache_key not in self._table_items_cache:
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(checkbox_item.flags() | Qt.ItemIsUserCheckable)
                checkbox_item.setCheckState(Qt.Unchecked)
                self._table_items_cache[cache_key + '_checkbox'] = checkbox_item
            else:
                checkbox_item = self._table_items_cache[cache_key + '_checkbox']
            
            self.project_table.setItem(row, 0, checkbox_item)
            
            # Name (with minimized data storage)
            if cache_key not in self._table_items_cache:
                name_item = QTableWidgetItem(project['name'])
                # Store only essential data, not full project dict
                minimal_data = {
                    'path': project['path'],
                    'name': project['name']
                }
                name_item.setData(Qt.UserRole, minimal_data)
                self._table_items_cache[cache_key + '_name'] = name_item
            else:
                name_item = self._table_items_cache[cache_key + '_name']
            
            self.project_table.setItem(row, 1, name_item)
            
            # Language
            if cache_key not in self._table_items_cache:
                lang_item = QTableWidgetItem(project['language'])
                self._table_items_cache[cache_key + '_lang'] = lang_item
            else:
                lang_item = self._table_items_cache[cache_key + '_lang']
            
            self.project_table.setItem(row, 2, lang_item)
            
            # Version
            if cache_key not in self._table_items_cache:
                version_item = QTableWidgetItem(project['version'])
                self._table_items_cache[cache_key + '_version'] = version_item
            else:
                version_item = self._table_items_cache[cache_key + '_version']
            
            self.project_table.setItem(row, 3, version_item)
            
            # Category
            category_text = project.get('category', 'None') or 'None'
            if cache_key not in self._table_items_cache:
                category_item = QTableWidgetItem(category_text)
                self._table_items_cache[cache_key + '_category'] = category_item
            else:
                category_item = self._table_items_cache[cache_key + '_category']
            
            self.project_table.setItem(row, 4, category_item)
            
            # Tags
            tags = project.get('tags', [])
            tags_text = ', '.join(tags[:5]) if tags else 'None'  # Limit to 5 tags
            if len(tags) > 5:
                tags_text += '...'
            
            if cache_key not in self._table_items_cache:
                tags_item = QTableWidgetItem(tags_text)
                self._table_items_cache[cache_key + '_tags'] = tags_item
            else:
                tags_item = self._table_items_cache[cache_key + '_tags']
            
            self.project_table.setItem(row, 5, tags_item)
            
            # Size
            size_text = self.format_size(project['size'])
            if cache_key not in self._table_items_cache:
                size_item = QTableWidgetItem(size_text)
                self._table_items_cache[cache_key + '_size'] = size_item
            else:
                size_item = self._table_items_cache[cache_key + '_size']
            
            self.project_table.setItem(row, 6, size_item)
            
            # Modified
            modified_text = project.get('modified_str', project['modified'].strftime("%Y-%m-%d %H:%M") if isinstance(project.get('modified'), datetime) else "Unknown")
            if cache_key not in self._table_items_cache:
                modified_item = QTableWidgetItem(modified_text)
                self._table_items_cache[cache_key + '_modified'] = modified_item
            else:
                modified_item = self._table_items_cache[cache_key + '_modified']
            
            self.project_table.setItem(row, 7, modified_item)
            
            # Git status
            git_text = "✓" if project['has_git'] else "✗"
            if cache_key not in self._table_items_cache:
                git_item = QTableWidgetItem(git_text)
                git_item.setTextAlignment(Qt.AlignCenter)
                self._table_items_cache[cache_key + '_git'] = git_item
            else:
                git_item = self._table_items_cache[cache_key + '_git']
            
            self.project_table.setItem(row, 8, git_item)
            
            # Notes
            note = project.get('note', '')
            note_text = "✓" if note else "✗"
            if cache_key not in self._table_items_cache:
                note_item = QTableWidgetItem(note_text)
                note_item.setTextAlignment(Qt.AlignCenter)
                note_item.setToolTip(note[:50] + "..." if len(note) > 50 else note or "No notes")
                self._table_items_cache[cache_key + '_note'] = note_item
            else:
                note_item = self._table_items_cache[cache_key + '_note']
            
            self.project_table.setItem(row, 9, note_item)
            
            # Favorite status
            is_favorite = project.get('is_favorite', False)
            favorite_text = "★" if is_favorite else "☆"
            if cache_key not in self._table_items_cache:
                favorite_item = QTableWidgetItem(favorite_text)
                favorite_item.setTextAlignment(Qt.AlignCenter)
                favorite_item.setForeground(QColor(255, 215, 0) if is_favorite else QColor(128, 128, 128))
                favorite_item.setToolTip("Favorite project" if is_favorite else "Not a favorite")
                self._table_items_cache[cache_key + '_favorite'] = favorite_item
            else:
                favorite_item = self._table_items_cache[cache_key + '_favorite']
            
            self.project_table.setItem(row, 10, favorite_item)
    
    def _process_ui_update_queue(self):
        """Process queued UI updates to improve responsiveness."""
        if not self._ui_update_queue:
            return
        
        # Process a batch of updates
        batch_size = 5  # Process 5 updates at a time
        processed_updates = []
        
        for _ in range(min(batch_size, len(self._ui_update_queue))):
            if self._ui_update_queue:
                update_func = self._ui_update_queue.pop(0)
                try:
                    update_func()
                    processed_updates.append(update_func)
                except Exception as e:
                    print(f"UI update error: {e}")
        
        # If there are still updates, schedule next processing
        if self._ui_update_queue:
            self._ui_update_timer.start(50)  # Process next batch in 50ms
    
    def queue_ui_update(self, update_func):
        """Queue a UI update for processing."""
        self._ui_update_queue.append(update_func)
        if not self._ui_update_timer.isActive():
            self._ui_update_timer.start(50)
    
    def populate_project_table(self):
        """Populate the project table with filtered projects using lazy loading."""
        # Stop any existing lazy loading
        self._is_lazy_loading = False
        self._lazy_load_timer.stop()
        
        # Limit the number of visible projects for performance
        visible_projects = self.filtered_projects[:self._max_visible_projects]
        
        # Clear table efficiently
        self.project_table.setRowCount(0)
        self.project_table.setRowCount(len(visible_projects))
        
        # Clear cache if it's too large
        if len(self._table_items_cache) > 2000:
            self._table_items_cache.clear()
        
        # If we have a small number of projects, load them all at once
        if len(visible_projects) <= 100:
            self._load_project_batch(0, len(visible_projects))
            self.status_label.setText(f"Loaded {len(visible_projects)} projects")
        else:
            # Start lazy loading for large datasets
            self._is_lazy_loading = True
            self._current_lazy_load_row = 0
            self.status_label.setText(f"Loading {len(visible_projects)} projects...")
            
            # Load first batch immediately
            self._load_project_batch(0, min(self._lazy_load_batch_size, len(visible_projects)))
            self._current_lazy_load_row = min(self._lazy_load_batch_size, len(visible_projects))
            
            # Schedule remaining batches
            if self._current_lazy_load_row < len(visible_projects):
                self._lazy_load_timer.start(self._lazy_load_delay)
        
        # Update status if we're limiting projects
        if len(self.filtered_projects) > self._max_visible_projects:
            self.status_label.setText(
                f"Showing {len(visible_projects)} of {len(self.filtered_projects)} projects "
                f"(limited for performance)"
            )
        elif len(visible_projects) <= 100:
            self.status_label.setText(f"Found {len(self.filtered_projects)} projects")
    
    def closeEvent(self, event):
        """Handle dialog close event with proper cleanup."""
        # Stop all timers
        self._memory_cleanup_timer.stop()
        self._lazy_load_timer.stop()
        self._ui_update_timer.stop()
        
        # Clear caches
        self._table_items_cache.clear()
        self._project_cache.clear()
        self._ui_update_queue.clear()
        
        # Force garbage collection
        gc.collect()
        
        # Call parent close event
        super().closeEvent(event)
    
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
        """Filter projects based on search text, language, category, tags, and favorites (optimized)."""
        search_text = self.search_box.text().strip()
        language = self.language_combo.currentText()
        category = self.category_combo.currentText()
        tag_filter_text = self.tag_filter_box.text().strip()
        favorite_filter = self.favorite_combo.currentText()
        
        # Early return if no filters applied
        if (not search_text and language == "All" and category == "All" and 
            not tag_filter_text and favorite_filter == "All"):
            self.filtered_projects = self.projects
            self.populate_project_table()
            self.status_label.setText(f"Showing {len(self.projects)} projects")
            return
        
        # Start with all projects but limit initial set for performance
        filtered = self.projects[:]
        
        # Apply filters in order of most restrictive first for performance
        
        # Filter by favorites (usually most restrictive)
        if favorite_filter == "Favorites Only":
            filtered = [p for p in filtered if p.get('is_favorite', False)]
        elif favorite_filter == "Non-Favorites Only":
            filtered = [p for p in filtered if not p.get('is_favorite', False)]
        
        # Filter by language (often restrictive)
        if language != "All":
            filtered = [p for p in filtered if p['language'] == language]
        
        # Filter by category
        if category != "All":
            filtered = [p for p in filtered if p.get('category') == category]
        
        # Filter by search text (most expensive, do last)
        if search_text:
            search_lower = search_text.lower()
            filtered = [p for p in filtered if (
                search_lower in p['name'].lower() or
                (p.get('description') and search_lower in p['description'].lower())
            )]
        
        # Filter by tags
        if tag_filter_text:
            # Split comma-separated tags and normalize
            filter_tags = [tag.strip().lower() for tag in tag_filter_text.split(',') if tag.strip()]
            if filter_tags:
                filtered = [p for p in filtered if (
                    p.get('tags') and
                    any(filter_tag in [project_tag.lower() for project_tag in p['tags']] for filter_tag in filter_tags)
                )]
        
        # Limit filtered results for performance
        if len(filtered) > self._max_visible_projects:
            self.filtered_projects = filtered[:self._max_visible_projects]
            self.populate_project_table()
            self.status_label.setText(
                f"Showing {len(self.filtered_projects)} of {len(filtered)} matching projects "
                f"(limited for performance)"
            )
        else:
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
        self.current_project = name_item.data(Qt.UserRole) if name_item else None
        
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
    
    def on_project_selection_changed(self):
        """Handle project selection changes in the table."""
        # This method is called when the selection changes
        # We can use it to update UI elements that depend on selection state
        selected_items = self.project_table.selectedItems()
        has_selection = len(selected_items) > 0
        
        # Update button states based on selection
        self.open_folder_button.setEnabled(has_selection)
        self.open_terminal_button.setEnabled(has_selection)
        self.open_editor_button.setEnabled(has_selection)
        self.manage_tags_button.setEnabled(has_selection)
        self.set_category_button.setEnabled(has_selection)
        self.edit_notes_button.setEnabled(has_selection)
        self.clear_notes_button.setEnabled(has_selection)
        self.favorite_button.setEnabled(has_selection)
        
        # If there's a selection, update the current project and details
        if has_selection:
            self.on_project_selected()
        else:
            self.current_project = None
            self.update_project_details()
    
    def on_project_double_clicked(self, item):
        """Handle double-click on a project."""
        self.on_project_selected()
        self.open_project_folder()
    
    def update_project_details(self):
        """Update the project details panel with current project info."""
        if not self.current_project:
            # Clear all labels when no project is selected
            self.name_label.setText('No project selected')
            self.path_label.setText('')
            self.language_label.setText('')
            self.version_label.setText('')
            self.size_label.setText('')
            self.modified_label.setText('')
            self.git_label.setText('')
            self.description_text.setText('Select a project to view details')
            self.readme_label.setText('')
            self.requirements_label.setText('')
            self.setup_label.setText('')
            self.main_file_label.setText('')
            self.category_label.setText('')
            self.tags_label.setText('')
            self.notes_text.setText('')
            return
        
        project = self.current_project
        
        # Update labels with default values for missing keys
        self.name_label.setText(project.get('name', 'Unknown'))
        self.path_label.setText(project.get('path', ''))
        self.language_label.setText(project.get('language', 'Unknown'))
        self.version_label.setText(project.get('version', 'N/A'))
        self.size_label.setText(self.format_size(project.get('size', 0)))
        
        # Handle modified date safely
        modified = project.get('modified')
        if modified:
            self.modified_label.setText(modified.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            self.modified_label.setText('N/A')
        
        self.git_label.setText("Yes" if project.get('has_git', False) else "No")
        
        # Update description
        self.description_text.setText(project.get('description', '') or "No description available")
        
        # Update file info
        self.readme_label.setText("✓" if project.get('has_readme', False) else "✗")
        self.requirements_label.setText("✓" if project.get('has_requirements', False) else "✗")
        self.setup_label.setText("✓" if project.get('has_setup', False) else "✗")
        self.main_file_label.setText(project.get('main_file', '') or "None")
        
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
            if category:
                # Check if category exists (predefined or custom)
                all_categories = self.scanner.tag_manager.get_all_categories()
                if category not in all_categories:
                    # Add as custom category
                    # Use the category name as both key and display name
                    category_key = category.lower().replace(" ", "_").replace("-", "_")
                    success = self.scanner.tag_manager.add_custom_category(
                        key=category_key,
                        name=category,
                        description=f"Custom category: {category}",
                        keywords=[]
                    )
                    if not success:
                        QMessageBox.warning(dialog, "Error", f"Could not create custom category '{category}'")
                        return
                    # Use the category key for setting
                    category = category_key
                
                # Set the category
                success = self.scanner.tag_manager.set_project_category(project_path, category)
                if not success:
                    QMessageBox.warning(dialog, "Error", f"Could not set category '{category}'")
                    return
            else:
                # Set to None (remove category)
                self.scanner.tag_manager.set_project_category(project_path, None)
            
            # Refresh current project data
            self.current_project['category'] = self.scanner.tag_manager.get_project_category(project_path)
            # Update UI
            self.update_project_details()
            self.populate_project_table()
            display_category = self.scanner.tag_manager.get_all_categories().get(category, {}).get('name', category) if category else 'None'
            QMessageBox.information(dialog, "Success", f"Category set to '{display_category}'")
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
    
    def toggle_favorite_project(self):
        """Toggle favorite status for the current project (keyboard shortcut handler)."""
        self.toggle_favorite()
    
    def toggle_favorite(self):
        """Toggle project favorite status."""
        if not self.current_project:
            return
        
        try:
            project_path = self.current_project.get('path')
            if not project_path:
                return
                
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
        
        project_path = self.current_project.get('path')
        if not project_path:
            return
        
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
        self.populate_project_table()
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
        
        self.populate_project_table()
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
            
            self.populate_project_table()
            QMessageBox.information(self, "Success", f"Added tags to {len(selected_projects)} projects.")
    
    def batch_set_category(self):
        """Set category for selected projects."""
        selected_projects = self.get_selected_projects()
        if not selected_projects:
            QMessageBox.warning(self, "No Selection", "Please select at least one project.")
            return
        
        # Get available categories
        all_categories_dict = self.scanner.tag_manager.get_all_categories()
        categories = ["None"] + list(all_categories_dict.keys())
        
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
            
            if selected_category == "None":
                selected_category = None
            
            try:
                if selected_category:
                    # Check if category exists (predefined or custom)
                    if selected_category not in all_categories_dict:
                        # Add as custom category
                        category_key = selected_category.lower().replace(" ", "_").replace("-", "_")
                        success = self.scanner.tag_manager.add_custom_category(
                            key=category_key,
                            name=selected_category,
                            description=f"Custom category: {selected_category}",
                            keywords=[]
                        )
                        if not success:
                            QMessageBox.warning(self, "Error", f"Could not create custom category '{selected_category}'")
                            return
                        # Use the category key for setting
                        selected_category = category_key
                    
                    # Set the category for all selected projects
                    for project in selected_projects:
                        project_path = project.get('path', '')
                        if project_path:
                            success = self.scanner.tag_manager.set_project_category(project_path, selected_category)
                            if success:
                                project['category'] = selected_category
                            else:
                                QMessageBox.warning(self, "Error", f"Could not set category for project: {project.get('name', 'Unknown')}")
                                return
                else:
                    # Set to None (remove category)
                    for project in selected_projects:
                        project_path = project.get('path', '')
                        if project_path:
                            self.scanner.tag_manager.set_project_category(project_path, None)
                            project['category'] = None
                
                self.populate_project_table()
                display_category = all_categories_dict.get(selected_category, {}).get('name', selected_category) if selected_category else 'None'
                QMessageBox.information(self, "Success", f"Set category to '{display_category}' for {len(selected_projects)} projects.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not set category: {str(e)}")
    
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
