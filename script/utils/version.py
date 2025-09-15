"""
Version information and utilities for Project Browser application.

This module provides version information following Semantic Versioning 2.0.0
and utility functions for version comparison and validation.
"""

import re
from typing import Tuple, Union, Optional

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
__copyright__ = "© Copyright 2025 Nsfr750 - All rights reserved"
__license__ = "GPLv3"
__organization__ = "Tuxxle"
__description__ = "A comprehensive project browser and management tool"


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


# Export all public symbols
__all__ = [
    '__version__', '__full_version__', 'version_info',
    'MAJOR', 'MINOR', 'PATCH', 'VERSION_SUFFIX', 'VERSION_METADATA',
    '__app_name__', '__app_title__', '__author__', '__copyright__',
    '__license__', '__organization__', '__description__',
    'get_version_string', 'parse_version', 'compare_versions',
    'is_compatible_version', 'get_version_info', 'validate_version'
]
