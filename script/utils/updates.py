#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Update checking utility for Project Browser.
Provides functionality to check for updates and display them in an independent dialog.
"""

import os
import sys
import json
import requests
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import packaging.version

# Try to import PySide6 for GUI availability check
try:
    import PySide6
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

# Add the root directory to the path to import version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from script.utils.version import __version__
from script.lang.lang_mgr import get_text
from script.ui.update_dialog import UpdateDialog

class UpdateChecker:
    """Handles update checking and notification."""
    
    def __init__(self):
        self.current_version = __version__
        self.github_api_url = "https://api.github.com/repos/Nsfr750/PRJ-1/releases/latest"
        self.github_repo_url = "https://github.com/Nsfr750/PRJ-1"
        self.cache_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "updates.json")
        self.cache_duration = timedelta(hours=24)  # Check for updates once per day
        
    def get_cached_update_info(self) -> Optional[Dict[str, Any]]:
        """Get cached update information if it's still valid."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    
                cached_time = datetime.fromisoformat(cached_data.get('cached_time', ''))
                if datetime.now() - cached_time < self.cache_duration:
                    return cached_data
        except (json.JSONDecodeError, ValueError, OSError):
            pass
        
        return None
    
    def cache_update_info(self, update_info: Dict[str, Any]) -> None:
        """Cache update information."""
        try:
            # Ensure config directory exists
            config_dir = os.path.dirname(self.cache_file)
            os.makedirs(config_dir, exist_ok=True)
            
            update_info['cached_time'] = datetime.now().isoformat()
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(update_info, f, indent=2)
        except OSError:
            pass
    
    def fetch_latest_release(self) -> Optional[Dict[str, Any]]:
        """Fetch the latest release information from GitHub."""
        try:
            response = requests.get(self.github_api_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, json.JSONDecodeError):
            return None
    
    def check_for_updates(self, force_check: bool = False) -> Optional[Dict[str, Any]]:
        """Check for updates, using cache if available."""
        if not force_check:
            cached_info = self.get_cached_update_info()
            if cached_info:
                return cached_info
        
        release_info = self.fetch_latest_release()
        if release_info:
            update_info = {
                'version': release_info.get('tag_name', '').lstrip('v'),
                'name': release_info.get('name', ''),
                'body': release_info.get('body', ''),
                'html_url': release_info.get('html_url', ''),
                'published_at': release_info.get('published_at', ''),
                'is_newer': False
            }
            
            # Check if the new version is actually newer
            try:
                latest_version = packaging.version.parse(update_info['version'])
                current_version = packaging.version.parse(self.current_version)
                update_info['is_newer'] = latest_version > current_version
            except (packaging.version.InvalidVersion, ValueError):
                # If version parsing fails, assume it's not newer
                update_info['is_newer'] = False
            
            self.cache_update_info(update_info)
            return update_info
        
        return None
    
    def is_update_available(self, force_check: bool = False) -> bool:
        """Check if an update is available."""
        update_info = self.check_for_updates(force_check)
        return update_info and update_info.get('is_newer', False)



def check_for_updates(parent=None, force_check: bool = False) -> None:
    """
    Check for updates and show the update dialog.
    
    Args:
        parent: Parent window for the dialog (optional)
        force_check: Force check ignoring cache (default: False)
    """
    if GUI_AVAILABLE:
        dialog = UpdateDialog(parent)
        dialog.show_update_dialog(force_check)
    else:
        # Console fallback
        checker = UpdateChecker()
        console_dialog = UpdateDialog(parent)
        console_dialog._show_console_dialog(force_check)


def is_update_available(force_check: bool = False) -> bool:
    """
    Check if an update is available without showing dialog.
    
    Args:
        force_check: Force check ignoring cache (default: False)
    
    Returns:
        bool: True if update is available, False otherwise
    """
    checker = UpdateChecker()
    return checker.is_update_available(force_check)


if __name__ == "__main__":
    # Test the update checker
    check_for_updates()
