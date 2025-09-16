#!/usr/bin/env python3
"""
Settings management module for PRJ-1 Project Browser.
This module provides functionality for saving and loading application settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

# Default settings
DEFAULT_SETTINGS = {
    "language": "en",
    "window": {
        "x": 100,
        "y": 100,
        "width": 1200,
        "height": 800,
        "maximized": False,
        "fullscreen": False
    },
    "ui": {
        "theme": "default",
        "font_size": 10,
        "font_family": "Segoe UI",
        "show_toolbar": True,
        "show_statusbar": True,
        "sidebar_width": 250,
        "project_table_column_widths": {},
        "project_table_column_order": [],
        "project_table_column_visibility": {}
    },
    "project_browser": {
        "scan_on_startup": True,
        "scan_recursive": True,
        "show_hidden_files": False,
        "cache_enabled": True,
        "cache_duration": 3600,  # 1 hour in seconds
        "last_directory": "",
        "recent_directories": [],
        "max_recent_directories": 10
    },
    "updates": {
        "check_on_startup": True,
        "auto_check": True,
        "check_frequency": 86400,  # 24 hours in seconds
        "last_check": None,
        "beta_updates": False
    },
    "logging": {
        "level": "INFO",
        "file_logging": True,
        "console_logging": True,
        "max_log_size": 10485760,  # 10MB
        "backup_count": 5
    },
    "advanced": {
        "debug_mode": False,
        "developer_mode": False,
        "performance_mode": False,
        "memory_limit": 512,  # MB
        "thread_pool_size": 4
    }
}

# Settings file path
SETTINGS_FILE = Path(__file__).parent.parent.parent / "config" / "settings.json"

# Global settings cache
_settings_cache: Optional[Dict[str, Any]] = None
_settings_modified: bool = False

# Setup logger
logger = logging.getLogger(__name__)


def get_settings_file_path() -> Path:
    """Get the path to the settings file."""
    return SETTINGS_FILE


def ensure_config_directory() -> None:
    """Ensure the config directory exists."""
    config_dir = SETTINGS_FILE.parent
    config_dir.mkdir(parents=True, exist_ok=True)


def get_default_settings() -> Dict[str, Any]:
    """Get the default settings dictionary."""
    return DEFAULT_SETTINGS.copy()


def load_settings() -> Dict[str, Any]:
    """Load settings from the settings file.
    
    Returns:
        Dictionary containing the loaded settings or default settings if file doesn't exist.
    """
    global _settings_cache, _settings_modified
    
    # Return cached settings if available
    if _settings_cache is not None and not _settings_modified:
        return _settings_cache
    
    ensure_config_directory()
    
    try:
        if SETTINGS_FILE.exists():
            logger.info(f"Loading settings from {SETTINGS_FILE}")
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
            
            # Merge with default settings to ensure all keys exist
            merged_settings = get_default_settings()
            merged_settings.update(loaded_settings)
            
            _settings_cache = merged_settings
            _settings_modified = False
            logger.info("Settings loaded successfully")
            return merged_settings
        else:
            logger.info("Settings file not found, using default settings")
            _settings_cache = get_default_settings()
            _settings_modified = False
            return _settings_cache
            
    except (json.JSONDecodeError, IOError, OSError) as e:
        logger.error(f"Error loading settings: {e}")
        logger.info("Using default settings")
        _settings_cache = get_default_settings()
        _settings_modified = False
        return _settings_cache


def save_settings(settings: Optional[Dict[str, Any]] = None) -> bool:
    """Save settings to the settings file.
    
    Args:
        settings: Settings dictionary to save. If None, uses cached settings.
        
    Returns:
        True if successful, False otherwise.
    """
    global _settings_cache, _settings_modified
    
    ensure_config_directory()
    
    try:
        if settings is None:
            settings = _settings_cache
        
        if settings is None:
            logger.error("No settings to save")
            return False
        
        logger.info(f"Saving settings to {SETTINGS_FILE}")
        
        # Create a backup of the existing file
        if SETTINGS_FILE.exists():
            backup_file = SETTINGS_FILE.with_suffix('.json.backup')
            try:
                backup_file.write_text(SETTINGS_FILE.read_text(encoding='utf-8'), encoding='utf-8')
            except Exception as e:
                logger.warning(f"Could not create backup: {e}")
        
        # Save the new settings
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        
        _settings_cache = settings.copy()
        _settings_modified = False
        logger.info("Settings saved successfully")
        return True
        
    except (IOError, OSError) as e:
        logger.error(f"Error saving settings: {e}")
        return False


def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific setting value.
    
    Args:
        key: The setting key (can use dot notation, e.g., 'window.width')
        default: Default value if key not found
        
    Returns:
        The setting value or default if not found.
    """
    settings = load_settings()
    
    # Handle dot notation
    keys = key.split('.')
    value = settings
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value


def set_setting(key: str, value: Any) -> bool:
    """Set a specific setting value.
    
    Args:
        key: The setting key (can use dot notation, e.g., 'window.width')
        value: The value to set
        
    Returns:
        True if successful, False otherwise.
    """
    global _settings_cache, _settings_modified
    
    settings = load_settings()
    
    # Handle dot notation
    keys = key.split('.')
    current = settings
    
    # Navigate to the parent of the target key
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        elif not isinstance(current[k], dict):
            # If the path exists but isn't a dict, replace it
            current[k] = {}
        current = current[k]
    
    # Set the value
    current[keys[-1]] = value
    _settings_cache = settings
    _settings_modified = True
    
    logger.debug(f"Setting {key} = {value}")
    return True


def get_language() -> str:
    """Get the current language setting."""
    return get_setting('language', 'en')


def set_language(language: str) -> bool:
    """Set the language setting.
    
    Args:
        language: Language code (e.g., 'en', 'it', 'es')
        
    Returns:
        True if successful, False otherwise.
    """
    return set_setting('language', language)


def get_window_geometry() -> Dict[str, Union[int, bool]]:
    """Get the window geometry settings.
    
    Returns:
        Dictionary containing window position and size information.
    """
    return get_setting('window', DEFAULT_SETTINGS['window'])


def set_window_geometry(x: int, y: int, width: int, height: int, 
                       maximized: bool = False, fullscreen: bool = False) -> bool:
    """Set the window geometry settings.
    
    Args:
        x: Window X position
        y: Window Y position
        width: Window width
        height: Window height
        maximized: Whether window is maximized
        fullscreen: Whether window is fullscreen
        
    Returns:
        True if successful, False otherwise.
    """
    geometry = {
        'x': x, 'y': y, 'width': width, 'height': height,
        'maximized': maximized, 'fullscreen': fullscreen
    }
    return set_setting('window', geometry)


def get_ui_settings() -> Dict[str, Any]:
    """Get the UI settings.
    
    Returns:
        Dictionary containing UI configuration.
    """
    return get_setting('ui', DEFAULT_SETTINGS['ui'])


def set_ui_settings(ui_settings: Dict[str, Any]) -> bool:
    """Set the UI settings.
    
    Args:
        ui_settings: Dictionary containing UI configuration
        
    Returns:
        True if successful, False otherwise.
    """
    return set_setting('ui', ui_settings)


def get_project_browser_settings() -> Dict[str, Any]:
    """Get the project browser settings.
    
    Returns:
        Dictionary containing project browser configuration.
    """
    return get_setting('project_browser', DEFAULT_SETTINGS['project_browser'])


def set_project_browser_settings(pb_settings: Dict[str, Any]) -> bool:
    """Set the project browser settings.
    
    Args:
        pb_settings: Dictionary containing project browser configuration
        
    Returns:
        True if successful, False otherwise.
    """
    return set_setting('project_browser', pb_settings)


def get_update_settings() -> Dict[str, Any]:
    """Get the update settings.
    
    Returns:
        Dictionary containing update configuration.
    """
    return get_setting('updates', DEFAULT_SETTINGS['updates'])


def set_update_settings(update_settings: Dict[str, Any]) -> bool:
    """Set the update settings.
    
    Args:
        update_settings: Dictionary containing update configuration
        
    Returns:
        True if successful, False otherwise.
    """
    return set_setting('updates', update_settings)


def reset_settings() -> bool:
    """Reset settings to default values.
    
    Returns:
        True if successful, False otherwise.
    """
    global _settings_cache, _settings_modified
    
    logger.info("Resetting settings to default values")
    _settings_cache = get_default_settings()
    _settings_modified = True
    return save_settings()


def export_settings(file_path: Union[str, Path]) -> bool:
    """Export settings to a file.
    
    Args:
        file_path: Path to export file
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        settings = load_settings()
        file_path = Path(file_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Settings exported to {file_path}")
        return True
        
    except (IOError, OSError) as e:
        logger.error(f"Error exporting settings: {e}")
        return False


def import_settings(file_path: Union[str, Path]) -> bool:
    """Import settings from a file.
    
    Args:
        file_path: Path to import file
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"Import file not found: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            imported_settings = json.load(f)
        
        # Merge with default settings to ensure all keys exist
        merged_settings = get_default_settings()
        merged_settings.update(imported_settings)
        
        global _settings_cache, _settings_modified
        _settings_cache = merged_settings
        _settings_modified = True
        
        logger.info(f"Settings imported from {file_path}")
        return save_settings()
        
    except (json.JSONDecodeError, IOError, OSError) as e:
        logger.error(f"Error importing settings: {e}")
        return False


def validate_settings(settings: Dict[str, Any]) -> bool:
    """Validate settings structure and values.
    
    Args:
        settings: Settings dictionary to validate
        
    Returns:
        True if valid, False otherwise.
    """
    try:
        # Check required top-level keys
        required_keys = ['language', 'window', 'ui', 'project_browser', 'updates', 'logging', 'advanced']
        for key in required_keys:
            if key not in settings:
                logger.error(f"Missing required settings key: {key}")
                return False
        
        # Validate language
        if not isinstance(settings['language'], str):
            logger.error("Language must be a string")
            return False
        
        # Validate window geometry
        window = settings['window']
        required_window_keys = ['x', 'y', 'width', 'height', 'maximized', 'fullscreen']
        for key in required_window_keys:
            if key not in window:
                logger.error(f"Missing window setting: {key}")
                return False
        
        # Validate numeric window values
        for key in ['x', 'y', 'width', 'height']:
            if not isinstance(window[key], int) or window[key] < 0:
                logger.error(f"Window {key} must be a non-negative integer")
                return False
        
        # Validate boolean window values
        for key in ['maximized', 'fullscreen']:
            if not isinstance(window[key], bool):
                logger.error(f"Window {key} must be a boolean")
                return False
        
        logger.info("Settings validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Error validating settings: {e}")
        return False


def get_settings_summary() -> Dict[str, Any]:
    """Get a summary of current settings.
    
    Returns:
        Dictionary containing settings summary.
    """
    settings = load_settings()
    
    summary = {
        'language': settings['language'],
        'window_size': f"{settings['window']['width']}x{settings['window']['height']}",
        'window_position': f"{settings['window']['x']},{settings['window']['y']}",
        'maximized': settings['window']['maximized'],
        'theme': settings['ui']['theme'],
        'scan_on_startup': settings['project_browser']['scan_on_startup'],
        'check_updates_on_startup': settings['updates']['check_on_startup'],
        'debug_mode': settings['advanced']['debug_mode']
    }
    
    return summary


# Initialize settings on module import
load_settings()

# Export all public symbols
__all__ = [
    'get_settings_file_path', 'ensure_config_directory', 'get_default_settings',
    'load_settings', 'save_settings', 'get_setting', 'set_setting',
    'get_language', 'set_language', 'get_window_geometry', 'set_window_geometry',
    'get_ui_settings', 'set_ui_settings', 'get_project_browser_settings',
    'set_project_browser_settings', 'get_update_settings', 'set_update_settings',
    'reset_settings', 'export_settings', 'import_settings', 'validate_settings',
    'get_settings_summary'
]
