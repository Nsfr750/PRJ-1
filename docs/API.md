# API Documentation

## Table of Contents

- [Overview](#overview)
- [Core Classes](#core-classes)
- [UI Components](#ui-components)
- [Utility Modules](#utility-modules)
- [Data Structures](#data-structures)
- [Event System](#event-system)
- [Language System](#language-system)
- [Project Scanner](#project-scanner)
- [Settings Management](#settings-management)
- [Logging System](#logging-system)

## Overview

PRJ-1 is built with a modular architecture using PySide6 for the GUI. The API is organized into several key modules that provide different functionalities for project management, UI components, and system utilities.

## Core Classes

### MainWindow

**File**: `main.py`

The main application window that serves as the primary interface.

```python
class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, lang=None):
        """Initialize the main window.
        
        Args:
            lang (str, optional): Language code for the interface.
        """
    
    def init_ui(self):
        """Initialize the user interface."""
    
    def show_main_dialog(self):
        """Show MainDialog centered over the main window background."""
    
    def closeEvent(self, event):
        """Handle the close event."""
    
    def on_language_changed(self):
        """Handle language change event."""
```

### MainDialog

**File**: `script/ui/main_dialog.py`

A transparent dialog that displays the main logo and follows window resizing.

```python
class MainDialog(QDialog):
    """Transparent dialog displaying main.png centered over background."""
    
    def __init__(self, parent=None):
        """Initialize the main dialog.
        
        Args:
            parent (QMainWindow, optional): Parent window.
        """
    
    def setup_ui(self):
        """Set up the dialog UI."""
    
    def center_dialog(self):
        """Center the dialog over the parent window or screen."""
    
    def eventFilter(self, obj, event):
        """Event filter to track parent window resize events."""
    
    def keyPressEvent(self, event):
        """Handle key press events."""
```

## UI Components

### ProjectBrowserDialog

**File**: `script/ui/project_browser.py`

The main project browser interface for managing and viewing projects.

```python
class ProjectBrowserDialog(QDialog):
    """Dialog for browsing and managing projects."""
    
    def __init__(self, parent=None, lang=None):
        """Initialize the project browser.
        
        Args:
            parent (QWidget, optional): Parent widget.
            lang (str, optional): Language code.
        """
    
    def load_projects(self):
        """Load projects from cache or scanner."""
    
    def on_project_selected(self):
        """Handle project selection in the table."""
    
    def update_project_details(self):
        """Update the project details panel."""
    
    def scan_projects(self):
        """Scan for projects in configured directories."""
    
    def filter_projects(self):
        """Filter projects based on search criteria."""
```

### AppMenuBar

**File**: `script/ui/menu.py`

Application menu bar with language support and various actions.

```python
class AppMenuBar(QMenuBar):
    """Application menu bar with language support."""
    
    def __init__(self, parent=None, lang=None):
        """Initialize the menu bar.
        
        Args:
            parent (QWidget, optional): Parent widget.
            lang (str, optional): Language code.
        """
    
    def retranslate_ui(self):
        """Update menu texts for current language."""
    
    def set_language(self, lang):
        """Set the interface language.
        
        Args:
            lang (str): Language code.
        """
```

### AboutDialog, SponsorDialog, HelpDialog

**File**: `script/ui/about.py`, `script/ui/sponsor.py`, `script/ui/help.py`

Information dialogs with language support.

```python
class AboutDialog(QDialog):
    """About dialog with application information."""
    
    def __init__(self, parent=None, lang=None):
        """Initialize the about dialog."""
    
    def retranslate_ui(self):
        """Update dialog texts for current language."""
    
    def set_language(self, lang):
        """Set the dialog language."""
```

## Utility Modules

### ProjectScanner

**File**: `script/project_scanner.py`

Core project scanning and analysis functionality.

```python
class ProjectScanner:
    """Scanner for discovering and analyzing projects."""
    
    def __init__(self):
        """Initialize the project scanner."""
    
    def scan_directory(self, directory_path):
        """Scan a directory for projects.
        
        Args:
            directory_path (str): Path to directory to scan.
            
        Returns:
            list: List of discovered projects.
        """
    
    def _analyze_project(self, project_path):
        """Analyze a project and extract information.
        
        Args:
            project_path (Path): Path to the project.
            
        Returns:
            dict: Project information dictionary.
        """
    
    def _detect_language(self, project_path):
        """Detect the programming language of a project.
        
        Args:
            project_path (Path): Path to the project.
            
        Returns:
            str: Detected language name.
        """
    
    def load_projects(self):
        """Load projects from cache file.
        
        Returns:
            list: List of cached projects.
        """
    
    def save_projects(self, projects):
        """Save projects to cache file.
        
        Args:
            projects (list): List of projects to save.
        """
```

### LanguageManager

**File**: `script/lang/lang_mgr.py`

Language translation and management system.

```python
def get_text(key, default_text="", **kwargs):
    """Get translated text for a key.
    
    Args:
        key (str): Translation key.
        default_text (str, optional): Default text if key not found.
        **kwargs: Format parameters for the text.
        
    Returns:
        str: Translated and formatted text.
    """

def get_language():
    """Get the current language setting.
    
    Returns:
        str: Current language code.
    """

def set_language(lang):
    """Set the current language.
    
    Args:
        lang (str): Language code to set.
    """
```

### SettingsManager

**File**: `script/utils/settings.py`

Application settings and configuration management.

```python
def load_settings():
    """Load application settings from file.
    
    Returns:
        dict: Settings dictionary.
    """

def save_settings():
    """Save current settings to file."""

def get_setting(key, default=None):
    """Get a specific setting value.
    
    Args:
        key (str): Setting key.
        default: Default value if key not found.
        
    Returns:
        Setting value or default.
    """

def set_setting(key, value):
    """Set a specific setting value.
    
    Args:
        key (str): Setting key.
        value: Value to set.
    """
```

### Logger

**File**: `script/utils/logger.py`

Logging system for application events and errors.

```python
def setup_logger(name, level=logging.INFO):
    """Set up a logger with the specified name and level.
    
    Args:
        name (str): Logger name.
        level (int): Logging level.
        
    Returns:
        Logger: Configured logger instance.
    """

def get_logger():
    """Get the application logger.
    
    Returns:
        Logger: Application logger instance.
    """
```

## Data Structures

### Project Data Structure

```python
{
    "name": str,           # Project name
    "path": str,           # Full path to project
    "language": str,       # Detected programming language
    "version": str,        # Project version
    "size": int,           # Project size in bytes
    "modified": datetime,  # Last modification date
    "has_git": bool,       # Whether project has git repository
    "category": str,       # Project category
    "tags": list,          # List of tags
    "notes": str,          # Project notes
    "favorite": bool       # Whether project is favorited
}
```

### Settings Data Structure

```python
{
    "language": str,           # Interface language
    "window_geometry": {       # Window position and size
        "x": int,
        "y": int,
        "width": int,
        "height": int
    },
    "scan_directories": list,  # Directories to scan
    "cache_enabled": bool,     # Whether caching is enabled
    "last_scan": datetime,     # Last scan timestamp
    "ui_settings": {           # UI-specific settings
        "theme": str,
        "font_size": int,
        "table_columns": list
    }
}
```

## Event System

### Signals

The application uses Qt's signal-slot mechanism for event handling:

#### MainWindow Signals

- `language_changed`: Emitted when interface language changes

#### ProjectBrowserDialog Signals

- `project_selected`: Emitted when a project is selected
- `projects_updated`: Emitted when project list is updated

#### AppMenuBar Signals

- `language_changed`: Emitted when language is changed from menu

### Event Handling

```python
# Connect signals to slots
self.menu_bar.language_changed.connect(self.on_language_changed)
self.project_table.itemSelectionChanged.connect(self.on_project_selected)

# Emit signals
self.language_changed.emit(new_language)
self.project_selected.emit(project_data)
```

## Language System

### Translation Structure

```python
translations = {
    "en": {
        "app.title": "Project Browser",
        "app.ready": "Ready",
        "menu.file": "File",
        # ... more translations
    },
    "it": {
        "app.title": "Browser Progetti",
        "app.ready": "Pronto",
        "menu.file": "File",
        # ... more translations
    }
}
```

### Usage

```python
from script.lang.lang_mgr import get_text

# Get translated text
title = get_text("app.title", "Project Browser")
welcome = get_text("messages.welcome", "Welcome {name}!", name="User")

# Change language
from script.lang.lang_mgr import set_language
set_language("it")
```

## Project Scanner

### Scanning Process

1. **Directory Discovery**: Recursively scan configured directories
2. **Project Identification**: Identify project directories based on file patterns
3. **Language Detection**: Analyze file extensions to detect programming languages
4. **Metadata Extraction**: Extract version, size, modification date, etc.
5. **Caching**: Store results in JSON files for faster loading

### Supported Languages

- Python (.py)
- JavaScript (.js, .jsx, .ts, .tsx)
- Java (.java)
- C/C++ (.c, .cpp, .h, .hpp)
- HTML/CSS (.html, .css, .scss)
- And more...

### API Usage

```python
from script.project_scanner import ProjectScanner

# Create scanner
scanner = ProjectScanner()

# Scan directory
projects = scanner.scan_directory("/path/to/projects")

# Load from cache
cached_projects = scanner.load_projects()

# Save to cache
scanner.save_projects(projects)
```

## Settings Management

### Configuration Files

- `config/settings.json`: Main settings file
- `config/version.json`: Version information
- `data/projects.json`: Project cache
- `data/tags.json`: Tag definitions
- `data/favorites.json`: Favorite projects

### API Usage

```python
from script.utils.settings import load_settings, save_settings, get_setting, set_setting

# Load all settings
settings = load_settings()

# Get specific setting
language = get_setting("language", "en")

# Set specific setting
set_setting("language", "it")

# Save all settings
save_settings()
```

## Logging System

### Log Levels

- `DEBUG`: Detailed debugging information
- `INFO`: General application information
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### Log Files

- `logs/prj_YYYY-MM-DD.log`: Daily application logs
- `logs/prj_errors_YYYY-MM-DD.log`: Daily error logs

### API Usage

```python
from script.utils.logger import setup_logger, get_logger

# Setup logger
logger = setup_logger("my_module", logging.INFO)

# Get logger
logger = get_logger()

# Log messages
logger.info("Application started")
logger.error("Something went wrong", exc_info=True)
logger.debug("Debug information")
```

---

© Copyright 2025 Nsfr750 - All rights reserved
