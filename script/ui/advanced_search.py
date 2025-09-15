"""Advanced Search Dialog for Project Browser.

This module provides a comprehensive advanced search interface with multiple
criteria including tags, categories, file types, and other project attributes.
"""

import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QCheckBox, QGroupBox,
    QFrame, QSpinBox, QDateEdit, QScrollArea, QMessageBox,
    QDialogButtonBox, QTabWidget, QWidget
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from script.lang.lang_mgr import get_text


class AdvancedSearchDialog(QDialog):
    """Advanced search dialog for projects."""
    
    def __init__(self, scanner, parent=None, lang='en'):
        super().__init__(parent)
        self.scanner = scanner
        self.search_results = []
        self.lang = lang
        self.setWindowTitle(get_text('advanced_search.title', 'Advanced Project Search'))
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
        self.load_available_data()
    
    def setup_ui(self):
        """Set up the advanced search UI."""
        layout = QVBoxLayout(self)
        
        # Create tabs for different search categories
        self.tab_widget = QTabWidget()
        
        # Basic search tab
        self.basic_tab = self.create_basic_search_tab()
        self.tab_widget.addTab(self.basic_tab, get_text('advanced_search.tabs.basic', 'Basic'))
        
        # Advanced filters tab
        self.advanced_tab = self.create_advanced_filters_tab()
        self.tab_widget.addTab(self.advanced_tab, get_text('advanced_search.tabs.advanced', 'Advanced Filters'))
        
        # Date filters tab
        self.date_tab = self.create_date_filters_tab()
        self.tab_widget.addTab(self.date_tab, get_text('advanced_search.tabs.date', 'Date Filters'))
        
        layout.addWidget(self.tab_widget)
        
        # Search and clear buttons
        button_layout = QHBoxLayout()
        
        self.search_button = QPushButton(get_text('advanced_search.buttons.search', 'Search'))
        self.search_button.clicked.connect(self.perform_search)
        self.search_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px 16px;")
        button_layout.addWidget(self.search_button)
        
        self.clear_button = QPushButton(get_text('advanced_search.buttons.clear', 'Clear'))
        self.clear_button.clicked.connect(self.clear_search)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        
        # Dialog buttons
        dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)
        
        button_layout.addWidget(dialog_buttons)
        
        layout.addLayout(button_layout)
    
    def create_basic_search_tab(self) -> QWidget:
        """Create the basic search tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Name search
        name_group = QGroupBox(get_text('advanced_search.basic.name', 'Project Name'))
        name_layout = QVBoxLayout(name_group)
        
        self.name_search = QLineEdit()
        self.name_search.setPlaceholderText(get_text('advanced_search.basic.name_placeholder', 'Enter project name (supports wildcards: *, ?)', lang=self.lang))
        name_layout.addWidget(self.name_search)
        
        # Name search options
        name_options_layout = QHBoxLayout()
        
        self.name_exact_match = QCheckBox(get_text('advanced_search.basic.exact_match', 'Exact match'))
        name_options_layout.addWidget(self.name_exact_match)
        
        self.name_case_sensitive = QCheckBox(get_text('advanced_search.basic.case_sensitive', 'Case sensitive'))
        name_options_layout.addWidget(self.name_case_sensitive)
        
        name_options_layout.addStretch()
        name_layout.addLayout(name_options_layout)
        
        layout.addWidget(name_group)
        
        # Language search
        lang_group = QGroupBox(get_text('advanced_search.basic.language', 'Programming Language'))
        lang_layout = QVBoxLayout(lang_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItem(get_text('advanced_search.basic.any_language', 'Any Language', lang=self.lang), "")
        lang_layout.addWidget(self.language_combo)
        
        layout.addWidget(lang_group)
        
        # Category search
        category_group = QGroupBox(get_text('advanced_search.basic.category', 'Category'))
        category_layout = QVBoxLayout(category_group)
        
        self.category_combo = QComboBox()
        self.category_combo.addItem(get_text('advanced_search.basic.any_category', 'Any Category', lang=self.lang), "")
        category_layout.addWidget(self.category_combo)
        
        layout.addWidget(category_group)
        
        # Tags search
        tags_group = QGroupBox(get_text('advanced_search.basic.tags', 'Tags'))
        tags_layout = QVBoxLayout(tags_group)
        
        self.tags_search = QLineEdit()
        self.tags_search.setPlaceholderText(get_text('advanced_search.basic.tags_placeholder', 'Enter tags (comma-separated, supports AND/OR)', lang=self.lang))
        tags_layout.addWidget(self.tags_search)
        
        # Tags search options
        tags_options_layout = QHBoxLayout()
        
        self.tags_match_all = QCheckBox(get_text('advanced_search.basic.match_all_tags', 'Match all tags (AND)'))
        self.tags_match_all.setChecked(True)
        tags_options_layout.addWidget(self.tags_match_all)
        
        tags_options_layout.addStretch()
        tags_layout.addLayout(tags_options_layout)
        
        layout.addWidget(tags_group)
        
        layout.addStretch()
        
        return tab
    
    def create_advanced_filters_tab(self) -> QWidget:
        """Create the advanced filters tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File types filter
        files_group = QGroupBox(get_text('advanced_search.advanced.file_types', 'File Types'))
        files_layout = QVBoxLayout(files_group)
        
        self.file_types_search = QLineEdit()
        self.file_types_search.setPlaceholderText(get_text('advanced_search.advanced.file_types_placeholder', 'Enter file extensions (comma-separated, e.g., .py,.js,.cpp)', lang=self.lang))
        files_layout.addWidget(self.file_types_search)
        
        # File types options
        files_options_layout = QHBoxLayout()
        
        self.files_match_any = QCheckBox(get_text('advanced_search.advanced.match_any_file_type', 'Match any file type'))
        self.files_match_any.setChecked(True)
        files_options_layout.addWidget(self.files_match_any)
        
        files_options_layout.addStretch()
        files_layout.addLayout(files_options_layout)
        
        layout.addWidget(files_group)
        
        # Size filters
        size_group = QGroupBox(get_text('advanced_search.advanced.project_size', 'Project Size'))
        size_layout = QGridLayout(size_group)
        
        size_layout.addWidget(QLabel(get_text('advanced_search.advanced.min_size', 'Min size (KB):', lang=self.lang)), 0, 0)
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(0, 1000000)
        self.min_size_spin.setValue(0)
        size_layout.addWidget(self.min_size_spin, 0, 1)
        
        size_layout.addWidget(QLabel(get_text('advanced_search.advanced.max_size', 'Max size (KB):', lang=self.lang)), 1, 0)
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(0, 1000000)
        self.max_size_spin.setValue(1000000)
        size_layout.addWidget(self.max_size_spin, 1, 1)
        
        layout.addWidget(size_group)
        
        # Project properties
        props_group = QGroupBox(get_text('advanced_search.advanced.project_properties', 'Project Properties'))
        props_layout = QVBoxLayout(props_group)
        
        self.has_git_repo = QCheckBox(get_text('advanced_search.advanced.has_git_repo', 'Has Git repository'))
        props_layout.addWidget(self.has_git_repo)
        
        self.is_favorite = QCheckBox(get_text('advanced_search.advanced.is_favorite', 'Is favorite'))
        props_layout.addWidget(self.is_favorite)
        
        self.has_notes = QCheckBox(get_text('advanced_search.advanced.has_notes', 'Has notes'))
        props_layout.addWidget(self.has_notes)
        
        layout.addWidget(props_group)
        
        layout.addStretch()
        
        return tab
    
    def create_date_filters_tab(self) -> QWidget:
        """Create the date filters tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Modified date filters
        modified_group = QGroupBox(get_text('advanced_search.date.last_modified', 'Last Modified'))
        modified_layout = QGridLayout(modified_group)
        
        modified_layout.addWidget(QLabel(get_text('advanced_search.date.from', 'From:', lang=self.lang)), 0, 0)
        self.modified_from_date = QDateEdit()
        self.modified_from_date.setCalendarPopup(True)
        self.modified_from_date.setDate(QDate.currentDate().addMonths(-1))
        modified_layout.addWidget(self.modified_from_date, 0, 1)
        
        modified_layout.addWidget(QLabel(get_text('advanced_search.date.to', 'To:', lang=self.lang)), 1, 0)
        self.modified_to_date = QDateEdit()
        self.modified_to_date.setCalendarPopup(True)
        self.modified_to_date.setDate(QDate.currentDate())
        modified_layout.addWidget(self.modified_to_date, 1, 1)
        
        layout.addWidget(modified_group)
        
        # Created date filters (if available)
        created_group = QGroupBox(get_text('advanced_search.date.created_date', 'Created Date'))
        created_layout = QGridLayout(created_group)
        
        created_layout.addWidget(QLabel(get_text('advanced_search.date.from', 'From:', lang=self.lang)), 0, 0)
        self.created_from_date = QDateEdit()
        self.created_from_date.setCalendarPopup(True)
        self.created_from_date.setDate(QDate.currentDate().addYears(-1))
        created_layout.addWidget(self.created_from_date, 0, 1)
        
        created_layout.addWidget(QLabel(get_text('advanced_search.date.to', 'To:', lang=self.lang)), 1, 0)
        self.created_to_date = QDateEdit()
        self.created_to_date.setCalendarPopup(True)
        self.created_to_date.setDate(QDate.currentDate())
        created_layout.addWidget(self.created_to_date, 1, 1)
        
        layout.addWidget(created_group)
        
        # Quick date presets
        presets_group = QGroupBox(get_text('advanced_search.date.quick_presets', 'Quick Presets'))
        presets_layout = QHBoxLayout(presets_group)
        
        self.today_button = QPushButton(get_text('advanced_search.date.today', 'Today'))
        self.today_button.clicked.connect(lambda: self.set_date_preset("today"))
        presets_layout.addWidget(self.today_button)
        
        self.this_week_button = QPushButton(get_text('advanced_search.date.this_week', 'This Week'))
        self.this_week_button.clicked.connect(lambda: self.set_date_preset("this_week"))
        presets_layout.addWidget(self.this_week_button)
        
        self.this_month_button = QPushButton(get_text('advanced_search.date.this_month', 'This Month'))
        self.this_month_button.clicked.connect(lambda: self.set_date_preset("this_month"))
        presets_layout.addWidget(self.this_month_button)
        
        self.this_year_button = QPushButton(get_text('advanced_search.date.this_year', 'This Year'))
        self.this_year_button.clicked.connect(lambda: self.set_date_preset("this_year"))
        presets_layout.addWidget(self.this_year_button)
        
        layout.addWidget(presets_group)
        
        layout.addStretch()
        
        return tab
    
    def load_available_data(self):
        """Load available data for dropdowns."""
        projects = self.scanner.get_projects()
        
        # Load languages
        languages = sorted(set(p.get('language', 'Unknown') for p in projects))
        for lang in languages:
            self.language_combo.addItem(lang, lang)
        
        # Load categories
        categories = sorted(set(p.get('category', 'Uncategorized') for p in projects))
        for cat in categories:
            self.category_combo.addItem(cat, cat)
    
    def set_date_preset(self, preset: str):
        """Set date filter based on preset."""
        today = QDate.currentDate()
        
        if preset == "today":
            self.modified_from_date.setDate(today)
            self.modified_to_date.setDate(today)
        elif preset == "this_week":
            self.modified_from_date.setDate(today.addDays(-today.dayOfWeek() + 1))
            self.modified_to_date.setDate(today)
        elif preset == "this_month":
            self.modified_from_date.setDate(today.addDays(-today.day() + 1))
            self.modified_to_date.setDate(today)
        elif preset == "this_year":
            self.modified_from_date.setDate(today.addDays(-today.dayOfYear() + 1))
            self.modified_to_date.setDate(today)
    
    def clear_search(self):
        """Clear all search fields."""
        # Basic search
        self.name_search.clear()
        self.name_exact_match.setChecked(False)
        self.name_case_sensitive.setChecked(False)
        self.language_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
        self.tags_search.clear()
        self.tags_match_all.setChecked(True)
        
        # Advanced filters
        self.file_types_search.clear()
        self.files_match_any.setChecked(True)
        self.min_size_spin.setValue(0)
        self.max_size_spin.setValue(1000000)
        self.has_git_repo.setChecked(False)
        self.is_favorite.setChecked(False)
        self.has_notes.setChecked(False)
        
        # Date filters
        self.modified_from_date.setDate(QDate.currentDate().addMonths(-1))
        self.modified_to_date.setDate(QDate.currentDate())
        self.created_from_date.setDate(QDate.currentDate().addYears(-1))
        self.created_to_date.setDate(QDate.currentDate())
    
    def perform_search(self):
        """Perform the advanced search."""
        projects = self.scanner.get_projects()
        self.search_results = []
        
        for project in projects:
            if self.matches_search_criteria(project):
                self.search_results.append(project)
        
        # Show results count
        QMessageBox.information(
            self, "Search Results",
            f"Found {len(self.search_results)} projects matching your criteria."
        )
    
    def matches_search_criteria(self, project: Dict[str, Any]) -> bool:
        """Check if a project matches all search criteria."""
        # Name search
        if self.name_search.text():
            if not self.matches_name_criteria(project):
                return False
        
        # Language search
        if self.language_combo.currentData():
            if project.get('language', '').lower() != self.language_combo.currentData().lower():
                return False
        
        # Category search
        if self.category_combo.currentData():
            if project.get('category', '').lower() != self.category_combo.currentData().lower():
                return False
        
        # Tags search
        if self.tags_search.text():
            if not self.matches_tags_criteria(project):
                return False
        
        # File types search
        if self.file_types_search.text():
            if not self.matches_file_types_criteria(project):
                return False
        
        # Size filters
        if not self.matches_size_criteria(project):
            return False
        
        # Project properties
        if self.has_git_repo.isChecked():
            if not project.get('has_git', False):
                return False
        
        if self.is_favorite.isChecked():
            if not project.get('is_favorite', False):
                return False
        
        if self.has_notes.isChecked():
            if not project.get('note'):
                return False
        
        # Date filters
        if not self.matches_date_criteria(project):
            return False
        
        return True
    
    def matches_name_criteria(self, project: Dict[str, Any]) -> bool:
        """Check if project matches name criteria."""
        search_text = self.name_search.text()
        project_name = project.get('name', '')
        
        if self.name_exact_match.isChecked():
            if self.name_case_sensitive.isChecked():
                return project_name == search_text
            else:
                return project_name.lower() == search_text.lower()
        else:
            # Pattern matching with wildcards
            pattern = search_text.replace('*', '.*').replace('?', '.')
            if self.name_case_sensitive.isChecked():
                return re.match(f'^{pattern}$', project_name) is not None
            else:
                return re.match(f'^{pattern}$', project_name, re.IGNORECASE) is not None
    
    def matches_tags_criteria(self, project: Dict[str, Any]) -> bool:
        """Check if project matches tags criteria."""
        search_tags = [tag.strip() for tag in self.tags_search.text().split(',') if tag.strip()]
        project_tags = project.get('tags', [])
        
        if not search_tags:
            return True
        
        if self.tags_match_all.isChecked():
            # All tags must be present (AND)
            return all(tag.lower() in [pt.lower() for pt in project_tags] for tag in search_tags)
        else:
            # Any tag must be present (OR)
            return any(tag.lower() in [pt.lower() for pt in project_tags] for tag in search_tags)
    
    def matches_file_types_criteria(self, project: Dict[str, Any]) -> bool:
        """Check if project matches file types criteria."""
        search_extensions = [ext.strip() for ext in self.file_types_search.text().split(',') if ext.strip()]
        
        if not search_extensions:
            return True
        
        project_path = Path(project.get('path', ''))
        if not project_path.exists():
            return False
        
        found_files = []
        for ext in search_extensions:
            if not ext.startswith('.'):
                ext = '.' + ext
            
            files = list(project_path.rglob(f'*{ext}'))
            found_files.extend(files)
        
        if self.files_match_any.isChecked():
            # Any file type must be present
            return len(found_files) > 0
        else:
            # All file types must be present
            return all(len(list(project_path.rglob(f'*{ext}' if ext.startswith('.') else f'*.{ext}'))) > 0 
                      for ext in search_extensions)
    
    def matches_size_criteria(self, project: Dict[str, Any]) -> bool:
        """Check if project matches size criteria."""
        size_kb = project.get('size', 0) / 1024
        
        min_size = self.min_size_spin.value()
        max_size = self.max_size_spin.value()
        
        return min_size <= size_kb <= max_size
    
    def matches_date_criteria(self, project: Dict[str, Any]) -> bool:
        """Check if project matches date criteria."""
        modified_date = project.get('modified')
        
        if modified_date:
            mod_date = datetime.fromisoformat(modified_date).date()
            
            from_date = self.modified_from_date.date().toPyDate()
            to_date = self.modified_to_date.date().toPyDate()
            
            if not (from_date <= mod_date <= to_date):
                return False
        
        return True
    
    def get_search_results(self) -> List[Dict[str, Any]]:
        """Get the search results."""
        return self.search_results


def show_advanced_search(scanner, parent=None, lang='en') -> Optional[List[Dict[str, Any]]]:
    """Show the advanced search dialog and return results."""
    dialog = AdvancedSearchDialog(scanner, parent, lang)
    if dialog.exec() == QDialog.Accepted:
        return dialog.get_search_results()
    return None
