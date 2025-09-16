"""
Version information and utilities for Project Browser application.

This module provides version information following Semantic Versioning 2.0.0
and utility functions for version comparison, validation, and history tracking.
"""

import re
import json
import os
from datetime import datetime
from typing import Tuple, Union, Optional, Dict, List

# Version as a string (PEP 440 compliant, Semantic Versioning 2.0.0)
__version__ = "0.1.5"

# Version components
MAJOR = 0
MINOR = 1
PATCH = 5

# Additional version metadata
VERSION_SUFFIX = ""  # e.g., "-alpha.1", "-beta.2", "-rc.1"
VERSION_METADATA = ""  # e.g., "+build.123"

# Version as a tuple for comparisons (major, minor, patch)
version_info = (MAJOR, MINOR, PATCH)

# Full version string with suffix and metadata
__full_version__ = f"{__version__}{VERSION_SUFFIX}{VERSION_METADATA}"

# Application information
__app_name__ = "PRJ-1"
__app_title__ = "Project Browser"
__author__ = "Nsfr750"
__copyright__ = " 2025 Nsfr750 - All rights reserved"
__license__ = "GPLv3"
__organization__ = "Tuxxle"
__description__ = "A comprehensive project browser and management tool"

# Version history configuration
VERSION_HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "version_history.json")
VERSION_JSON_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "version.json")

# Default version history (initial versions)
DEFAULT_VERSION_HISTORY = [
    {
        "version": "0.1.0",
        "date": "2025-09-01",
        "changes": [
            "Initial release",
            "Basic project browsing functionality",
            "Simple UI with project list"
        ],
        "type": "initial"
    },
    {
        "version": "0.1.1",
        "date": "2025-09-05",
        "changes": [
            "Added project search functionality",
            "Improved UI responsiveness",
            "Fixed memory leaks"
        ],
        "type": "patch"
    },
    {
        "version": "0.1.2",
        "date": "2025-09-08",
        "changes": [
            "Added project categorization",
            "Implemented favorites system",
            "Added project tags support"
        ],
        "type": "minor"
    },
    {
        "version": "0.1.3",
        "date": "2025-09-10",
        "changes": [
            "Added build system integration",
            "Improved error handling",
            "Added project statistics"
        ],
        "type": "minor"
    },
    {
        "version": "0.1.4",
        "date": "2025-09-12",
        "changes": [
            "Added multi-language support",
            "Implemented translation system",
            "Added Italian language support"
        ],
        "type": "minor"
    },
    {
        "version": "0.1.5",
        "date": "2025-09-16",
        "changes": [
            "Refactored update dialog to separate UI component",
            "Added version history tracking",
            "Improved translation system for update checker"
        ],
        "type": "patch"
    }
]


def get_version_string(include_metadata: bool = False) -> str:
    """
    Get the version string with optional metadata.
    
    Args:
        include_metadata: Whether to include version metadata
        
    Returns:
        Version string
    """
    if include_metadata:
        return __full_version__
    return __version__


def parse_version(version_string: str) -> Tuple[int, int, int, str, str]:
    """
    Parse a version string into its components.
    
    Args:
        version_string: Version string to parse (e.g., "1.2.3-alpha.1+build.123")
        
    Returns:
        Tuple of (major, minor, patch, suffix, metadata)
        
    Raises:
        ValueError: If version string is invalid
    """
    # Pattern to match semantic versioning
    pattern = r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<suffix>[0-9A-Za-z-]+))?(?:\+(?P<metadata>[0-9A-Za-z-]+))?$"
    
    match = re.match(pattern, version_string)
    if not match:
        raise ValueError(f"Invalid version string: {version_string}")
    
    groups = match.groupdict()
    major = int(groups['major'])
    minor = int(groups['minor'])
    patch = int(groups['patch'])
    suffix = groups['suffix'] or ""
    metadata = groups['metadata'] or ""
    
    return (major, minor, patch, suffix, metadata)


def compare_versions(version1: Union[str, Tuple[int, int, int]], 
                    version2: Union[str, Tuple[int, int, int]]) -> int:
    """
    Compare two versions.
    
    Args:
        version1: First version (string or tuple)
        version2: Second version (string or tuple)
        
    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    def normalize_version(version):
        if isinstance(version, str):
            if '.' in version:
                return tuple(int(part) for part in version.split('.')[:3] if part.isdigit())
            else:
                return (int(version), 0, 0)
        elif isinstance(version, tuple):
            return version[:3] if len(version) >= 3 else version + (0,) * (3 - len(version))
        else:
            return (0, 0, 0)
    
    v1 = normalize_version(version1)
    v2 = normalize_version(version2)
    
    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    else:
        return 0


def is_compatible_version(version: Union[str, Tuple[int, int, int]], 
                         required_version: Union[str, Tuple[int, int, int]]) -> bool:
    """
    Check if a version is compatible with a required version.
    Uses semantic versioning compatibility rules.
    
    Args:
        version: Version to check
        required_version: Required version
        
    Returns:
        True if compatible, False otherwise
    """
    try:
        if isinstance(required_version, str):
            req_tuple = tuple(int(part) for part in required_version.split('.')[:3] if part.isdigit())
        else:
            req_tuple = required_version[:3]
            
        if isinstance(version, str):
            ver_tuple = tuple(int(part) for part in version.split('.')[:3] if part.isdigit())
        else:
            ver_tuple = version[:3]
            
        # Major version must match exactly
        if ver_tuple[0] != req_tuple[0]:
            return False
            
        # Minor version must be >= required
        if ver_tuple[1] < req_tuple[1]:
            return False
            
        # Patch version can be anything if minor matches
        if ver_tuple[1] == req_tuple[1] and ver_tuple[2] < req_tuple[2]:
            return False
            
        return True
        
    except (ValueError, IndexError, TypeError):
        return False


def get_version_info() -> dict:
    """
    Get comprehensive version information as a dictionary.
    
    Returns:
        Dictionary containing all version-related information
    """
    return {
        'version': __version__,
        'full_version': __full_version__,
        'version_info': version_info,
        'major': MAJOR,
        'minor': MINOR,
        'patch': PATCH,
        'suffix': VERSION_SUFFIX,
        'metadata': VERSION_METADATA,
        'app_name': __app_name__,
        'app_title': __app_title__,
        'author': __author__,
        'copyright': __copyright__,
        'license': __license__,
        'organization': __organization__,
        'description': __description__
    }


def validate_version(version_string: str) -> bool:
    """
    Validate if a version string follows semantic versioning.
    
    Args:
        version_string: Version string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        parse_version(version_string)
        return True
    except ValueError:
        return False


def load_version_history() -> List[Dict]:
    """
    Load version history from file or return default history.
    
    Returns:
        List of version history entries
    """
    try:
        if os.path.exists(VERSION_HISTORY_FILE):
            with open(VERSION_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create default version history file
            save_version_history(DEFAULT_VERSION_HISTORY)
            return DEFAULT_VERSION_HISTORY.copy()
    except (json.JSONDecodeError, IOError, OSError):
        return DEFAULT_VERSION_HISTORY.copy()


def save_version_history(history: List[Dict]) -> bool:
    """
    Save version history to file.
    
    Args:
        history: List of version history entries
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(VERSION_HISTORY_FILE), exist_ok=True)
        
        with open(VERSION_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError):
        return False


def add_version_entry(version: str, changes: List[str], version_type: str = "patch") -> bool:
    """
    Add a new version entry to the version history.
    
    Args:
        version: Version string (e.g., "0.1.6")
        changes: List of changes for this version
        version_type: Type of version change ("major", "minor", "patch", "initial")
        
    Returns:
        True if successful, False otherwise
    """
    try:
        history = load_version_history()
        
        # Check if version already exists
        for entry in history:
            if entry['version'] == version:
                # Update existing entry
                entry['changes'] = changes
                entry['type'] = version_type
                entry['date'] = datetime.now().strftime('%Y-%m-%d')
                return save_version_history(history)
        
        # Add new entry
        new_entry = {
            "version": version,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "changes": changes,
            "type": version_type
        }
        
        history.append(new_entry)
        return save_version_history(history)
    except Exception:
        return False


def get_version_history(limit: Optional[int] = None) -> List[Dict]:
    """
    Get version history, optionally limited to the most recent entries.
    
    Args:
        limit: Maximum number of entries to return (None for all)
        
    Returns:
        List of version history entries, sorted by date (newest first)
    """
    history = load_version_history()
    
    # Sort by date (newest first)
    history.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    if limit is not None:
        return history[:limit]
    return history


def get_version_changes(version: str) -> Optional[Dict]:
    """
    Get changes for a specific version.
    
    Args:
        version: Version string to look up
        
    Returns:
        Version entry dict if found, None otherwise
    """
    history = load_version_history()
    
    for entry in history:
        if entry['version'] == version:
            return entry
    return None


def get_latest_version_info() -> Optional[Dict]:
    """
    Get information about the latest version.
    
    Returns:
        Latest version entry dict if available, None otherwise
    """
    history = get_version_history(limit=1)
    return history[0] if history else None


def get_version_statistics() -> Dict[str, Union[int, List[str]]]:
    """
    Get statistics about version history.
    
    Returns:
        Dictionary containing version statistics
    """
    history = load_version_history()
    
    stats = {
        "total_versions": len(history),
        "major_versions": 0,
        "minor_versions": 0,
        "patch_versions": 0,
        "initial_versions": 0,
        "all_versions": []
    }
    
    for entry in history:
        version_type = entry.get('type', 'patch')
        stats["all_versions"].append(entry['version'])
        
        if version_type == "major":
            stats["major_versions"] += 1
        elif version_type == "minor":
            stats["minor_versions"] += 1
        elif version_type == "patch":
            stats["patch_versions"] += 1
        elif version_type == "initial":
            stats["initial_versions"] += 1
    
    return stats


def format_version_history(history: Optional[List[Dict]] = None, 
                          include_date: bool = True, 
                          include_type: bool = True) -> str:
    """
    Format version history as a human-readable string.
    
    Args:
        history: Version history to format (None to load from file)
        include_date: Whether to include release dates
        include_type: Whether to include version types
        
    Returns:
        Formatted version history string
    """
    if history is None:
        history = get_version_history()
    
    if not history:
        return "No version history available."
    
    formatted_lines = []
    formatted_lines.append("Version History:")
    formatted_lines.append("=" * 50)
    
    for entry in history:
        line_parts = [f"Version {entry['version']}"]
        
        if include_date and 'date' in entry:
            line_parts.append(f"({entry['date']})")
        
        if include_type and 'type' in entry:
            line_parts.append(f"[{entry['type'].upper()}]")
        
        formatted_lines.append(" ".join(line_parts))
        formatted_lines.append("-" * 30)
        
        for change in entry.get('changes', []):
            formatted_lines.append(f"  • {change}")
        
        formatted_lines.append("")
    
    return "\n".join(formatted_lines)


def is_newer_version(version1: str, version2: str) -> bool:
    """
    Check if version1 is newer than version2.
    
    Args:
        version1: First version string
        version2: Second version string
        
    Returns:
        True if version1 is newer than version2
    """
    return compare_versions(version1, version2) > 0


def get_version_timeline(start_version: Optional[str] = None, 
                        end_version: Optional[str] = None) -> List[Dict]:
    """
    Get version history within a version range.
    
    Args:
        start_version: Starting version (inclusive)
        end_version: Ending version (inclusive)
        
    Returns:
        List of version entries within the specified range
    """
    history = load_version_history()
    
    if start_version is None and end_version is None:
        return history
    
    filtered_history = []
    
    for entry in history:
        version = entry['version']
        
        # Check if version is within range
        if start_version and compare_versions(version, start_version) < 0:
            continue
        
        if end_version and compare_versions(version, end_version) > 0:
            continue
        
        filtered_history.append(entry)
    
    # Sort by version (newest first)
    filtered_history.sort(key=lambda x: compare_versions(x['version'], '0.0.0'), reverse=True)
    return filtered_history


def save_version_data_to_json() -> bool:
    """
    Save all public symbols data to config/version.json.
    This function should be called at application startup.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Collect all public symbols data
        version_data = {
            'version_info': {
                'version': __version__,
                'full_version': __full_version__,
                'version_info': list(version_info),
                'major': MAJOR,
                'minor': MINOR,
                'patch': PATCH,
                'suffix': VERSION_SUFFIX,
                'metadata': VERSION_METADATA
            },
            'app_info': {
                'app_name': __app_name__,
                'app_title': __app_title__,
                'author': __author__,
                'copyright': __copyright__,
                'license': __license__,
                'organization': __organization__,
                'description': __description__
            },
            'version_history': {
                'file_path': VERSION_HISTORY_FILE,
                'json_file_path': VERSION_JSON_FILE,
                'history': get_version_history()
            },
            'statistics': get_version_statistics(),
            'latest_version': get_latest_version_info(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Ensure config directory exists
        config_dir = os.path.dirname(VERSION_JSON_FILE)
        os.makedirs(config_dir, exist_ok=True)
        
        # Save to JSON file
        with open(VERSION_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2, ensure_ascii=False)
        
        return True
    except (OSError, json.JSONEncodeError, TypeError):
        return False


def load_version_data_from_json() -> Optional[Dict]:
    """
    Load version data from config/version.json.
    
    Returns:
        Version data dictionary if successful, None otherwise
    """
    try:
        if os.path.exists(VERSION_JSON_FILE):
            with open(VERSION_JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except (json.JSONDecodeError, OSError):
        return None


# Export all public symbols
__all__ = [
    '__version__', '__full_version__', 'version_info',
    'MAJOR', 'MINOR', 'PATCH', 'VERSION_SUFFIX', 'VERSION_METADATA',
    '__app_name__', '__app_title__', '__author__', '__copyright__',
    '__license__', '__organization__', '__description__',
    'get_version_string', 'parse_version', 'compare_versions',
    'is_compatible_version', 'get_version_info', 'validate_version',
    'load_version_history', 'save_version_history', 'add_version_entry',
    'get_version_history', 'get_version_changes', 'get_latest_version_info',
    'get_version_statistics', 'format_version_history', 'is_newer_version',
    'get_version_timeline', 'save_version_data_to_json', 'load_version_data_from_json'
]
