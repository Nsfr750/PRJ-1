#!/usr/bin/env python3
"""
Backup System Module
Provides automatic backup functionality for project data and configurations.
"""

import os
import json
import shutil
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class BackupSystem:
    """Manages automatic backup of project data and configurations."""
    
    def __init__(self, backup_dir: str = "backups", data_dir: str = "data"):
        self.backup_dir = Path(backup_dir)
        self.data_dir = Path(data_dir)
        self.backup_config_file = self.backup_dir / "backup_config.json"
        self.backup_metadata_file = self.backup_dir / "backup_metadata.json"
        
        # Ensure backup directory exists before loading config
        self.backup_dir.mkdir(exist_ok=True)
        
        # Default backup configuration
        self.default_config = {
            'auto_backup': True,
            'backup_interval_hours': 24,
            'max_backups': 10,
            'compress_backups': True,
            'include_project_data': True,
            'include_config_files': True,
            'include_logs': False,
            'backup_on_scan': True,
            'backup_on_exit': False,
            'notification_enabled': True
        }
        
        # Load or create backup configuration
        self.config = self._load_config()
        
        # Backup metadata tracking
        self.metadata = self._load_metadata()
        
        # Threading for backup operations
        self._backup_lock = threading.Lock()
        self._backup_in_progress = False
        
        # Initialize backup scheduler
        self._last_backup = self.metadata.get('last_backup')
        if self._last_backup:
            self._last_backup = datetime.fromisoformat(self._last_backup)
        else:
            self._last_backup = datetime.now() - timedelta(hours=self.config['backup_interval_hours'])
    
    def _load_config(self) -> Dict[str, Any]:
        """Load backup configuration from file or create default."""
        if self.backup_config_file.exists():
            try:
                with open(self.backup_config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    merged_config = self.default_config.copy()
                    merged_config.update(config)
                    return merged_config
            except Exception as e:
                logger.error(f"Error loading backup config: {e}")
                return self.default_config.copy()
        else:
            # Create default config file
            self._save_config(self.default_config)
            return self.default_config.copy()
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save backup configuration to file."""
        try:
            with open(self.backup_config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving backup config: {e}")
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load backup metadata from file or create default."""
        if self.backup_metadata_file.exists():
            try:
                with open(self.backup_metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading backup metadata: {e}")
                return {'backups': [], 'last_backup': None}
        else:
            return {'backups': [], 'last_backup': None}
    
    def _save_metadata(self) -> None:
        """Save backup metadata to file."""
        try:
            with open(self.backup_metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving backup metadata: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current backup configuration."""
        return self.config.copy()
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update backup configuration."""
        try:
            # Merge with existing config
            merged_config = self.config.copy()
            merged_config.update(new_config)
            self.config = merged_config
            self._save_config(self.config)
            logger.info("Backup configuration updated")
            return True
        except Exception as e:
            logger.error(f"Error updating backup config: {e}")
            return False
    
    def create_backup(self, backup_name: Optional[str] = None) -> Optional[str]:
        """Create a backup of project data and configurations.
        
        Args:
            backup_name: Optional name for the backup. If None, uses timestamp.
            
        Returns:
            Path to the created backup file, or None if failed.
        """
        with self._backup_lock:
            if self._backup_in_progress:
                logger.warning("Backup already in progress")
                return None
            
            self._backup_in_progress = True
        
        try:
            # Generate backup name
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            # Create backup file path
            if self.config['compress_backups']:
                backup_file = self.backup_dir / f"{backup_name}.zip"
            else:
                backup_dir = self.backup_dir / backup_name
                backup_dir.mkdir(exist_ok=True)
                backup_file = backup_dir
            
            logger.info(f"Creating backup: {backup_file}")
            
            if self.config['compress_backups']:
                # Create compressed backup
                with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add data files
                    if self.config['include_project_data'] and self.data_dir.exists():
                        for file_path in self.data_dir.rglob('*'):
                            if file_path.is_file():
                                arcname = f"data/{file_path.relative_to(self.data_dir)}"
                                zipf.write(file_path, arcname)
                    
                    # Add config files
                    if self.config['include_config_files']:
                        config_files = [
                            'README.md', 'LICENSE', 'requirements.txt', 
                            'CHANGELOG.md', 'TO_DO.md', 'INFO.txt'
                        ]
                        for config_file in config_files:
                            file_path = Path(config_file)
                            if file_path.exists():
                                zipf.write(file_path, file_path.name)
                    
                    # Add logs if enabled
                    if self.config['include_logs']:
                        logs_dir = Path("logs")
                        if logs_dir.exists():
                            for file_path in logs_dir.rglob('*'):
                                if file_path.is_file():
                                    arcname = f"logs/{file_path.relative_to(logs_dir)}"
                                    zipf.write(file_path, arcname)
            else:
                # Create uncompressed backup (directory structure)
                if self.config['include_project_data'] and self.data_dir.exists():
                    shutil.copytree(self.data_dir, backup_file / "data")
                
                if self.config['include_config_files']:
                    config_files = [
                        'README.md', 'LICENSE', 'requirements.txt', 
                        'CHANGELOG.md', 'TO_DO.md', 'INFO.txt'
                    ]
                    for config_file in config_files:
                        file_path = Path(config_file)
                        if file_path.exists():
                            shutil.copy2(file_path, backup_file / file_path.name)
                
                if self.config['include_logs']:
                    logs_dir = Path("logs")
                    if logs_dir.exists():
                        shutil.copytree(logs_dir, backup_file / "logs")
            
            # Calculate backup hash for integrity checking
            backup_hash = self._calculate_file_hash(backup_file)
            
            # Update metadata
            backup_info = {
                'name': backup_name,
                'file': str(backup_file),
                'created': datetime.now().isoformat(),
                'size': backup_file.stat().st_size if backup_file.exists() else 0,
                'hash': backup_hash,
                'compressed': self.config['compress_backups'],
                'config': self.config.copy()
            }
            
            self.metadata['backups'].append(backup_info)
            self.metadata['last_backup'] = datetime.now().isoformat()
            self._last_backup = datetime.now()
            
            # Clean up old backups if needed
            self._cleanup_old_backups()
            
            # Save metadata
            self._save_metadata()
            
            logger.info(f"Backup created successfully: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
        finally:
            self._backup_in_progress = False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        if file_path.is_file():
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        elif file_path.is_dir():
            # For directories, calculate hash of all files
            sha256_hash = hashlib.sha256()
            for file_path in file_path.rglob('*'):
                if file_path.is_file():
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        return ""
    
    def _cleanup_old_backups(self) -> None:
        """Remove old backups if we exceed the maximum number."""
        if len(self.metadata['backups']) > self.config['max_backups']:
            # Sort by creation date (oldest first)
            sorted_backups = sorted(
                self.metadata['backups'], 
                key=lambda x: x['created']
            )
            
            # Remove oldest backups
            to_remove = len(self.metadata['backups']) - self.config['max_backups']
            for i in range(to_remove):
                backup_info = sorted_backups[i]
                backup_path = Path(backup_info['file'])
                
                try:
                    if backup_path.exists():
                        if backup_path.is_file():
                            backup_path.unlink()
                        elif backup_path.is_dir():
                            shutil.rmtree(backup_path)
                    
                    # Remove from metadata
                    self.metadata['backups'].remove(backup_info)
                    logger.info(f"Removed old backup: {backup_path}")
                    
                except Exception as e:
                    logger.error(f"Error removing old backup {backup_path}: {e}")
    
    def restore_backup(self, backup_file: str, restore_path: Optional[str] = None) -> bool:
        """Restore a backup from file.
        
        Args:
            backup_file: Path to the backup file or directory
            restore_path: Optional path to restore to. If None, restores to original locations.
            
        Returns:
            True if restore was successful, False otherwise.
        """
        backup_path = Path(backup_file)
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_file}")
            return False
        
        try:
            logger.info(f"Restoring backup: {backup_file}")
            
            if restore_path:
                restore_base = Path(restore_path)
                restore_base.mkdir(parents=True, exist_ok=True)
            else:
                restore_base = Path.cwd()
            
            if backup_path.is_file() and backup_path.suffix == '.zip':
                # Extract from zip file
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(restore_base)
            elif backup_path.is_dir():
                # Copy from directory
                shutil.copytree(backup_path, restore_base, dirs_exist_ok=True)
            else:
                logger.error(f"Invalid backup format: {backup_file}")
                return False
            
            logger.info(f"Backup restored successfully to: {restore_base}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        return self.metadata.get('backups', []).copy()
    
    def delete_backup(self, backup_name: str) -> bool:
        """Delete a specific backup.
        
        Args:
            backup_name: Name of the backup to delete
            
        Returns:
            True if deletion was successful, False otherwise.
        """
        # Find backup in metadata
        backup_info = None
        for backup in self.metadata['backups']:
            if backup['name'] == backup_name:
                backup_info = backup
                break
        
        if not backup_info:
            logger.error(f"Backup not found: {backup_name}")
            return False
        
        try:
            # Delete backup file
            backup_path = Path(backup_info['file'])
            if backup_path.exists():
                if backup_path.is_file():
                    backup_path.unlink()
                elif backup_path.is_dir():
                    shutil.rmtree(backup_path)
            
            # Remove from metadata
            self.metadata['backups'].remove(backup_info)
            self._save_metadata()
            
            logger.info(f"Backup deleted: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting backup {backup_name}: {e}")
            return False
    
    def check_backup_needed(self) -> bool:
        """Check if a backup is needed based on configuration."""
        if not self.config['auto_backup']:
            return False
        
        if not self._last_backup:
            return True
        
        time_since_last_backup = datetime.now() - self._last_backup
        hours_since_last = time_since_last_backup.total_seconds() / 3600
        
        return hours_since_last >= self.config['backup_interval_hours']
    
    def auto_backup_if_needed(self) -> Optional[str]:
        """Create automatic backup if needed based on configuration."""
        if self.check_backup_needed():
            logger.info("Automatic backup needed, creating backup...")
            return self.create_backup()
        else:
            logger.debug("No automatic backup needed")
            return None
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup statistics."""
        backups = self.metadata.get('backups', [])
        
        total_size = sum(backup.get('size', 0) for backup in backups)
        total_count = len(backups)
        
        oldest_backup = None
        newest_backup = None
        
        if backups:
            sorted_backups = sorted(backups, key=lambda x: x['created'])
            oldest_backup = sorted_backups[0]['created']
            newest_backup = sorted_backups[-1]['created']
        
        return {
            'total_backups': total_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'oldest_backup': oldest_backup,
            'newest_backup': newest_backup,
            'last_backup': self.metadata.get('last_backup'),
            'auto_backup_enabled': self.config['auto_backup'],
            'backup_interval_hours': self.config['backup_interval_hours'],
            'max_backups': self.config['max_backups']
        }
    
    def verify_backup_integrity(self, backup_name: str) -> bool:
        """Verify the integrity of a backup.
        
        Args:
            backup_name: Name of the backup to verify
            
        Returns:
            True if backup is valid, False otherwise.
        """
        # Find backup in metadata
        backup_info = None
        for backup in self.metadata['backups']:
            if backup['name'] == backup_name:
                backup_info = backup
                break
        
        if not backup_info:
            logger.error(f"Backup not found: {backup_name}")
            return False
        
        try:
            backup_path = Path(backup_info['file'])
            if not backup_path.exists():
                logger.error(f"Backup file missing: {backup_path}")
                return False
            
            # Recalculate hash and compare
            current_hash = self._calculate_file_hash(backup_path)
            stored_hash = backup_info.get('hash', '')
            
            if current_hash == stored_hash:
                logger.info(f"Backup integrity verified: {backup_name}")
                return True
            else:
                logger.warning(f"Backup integrity check failed: {backup_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying backup integrity: {e}")
            return False
