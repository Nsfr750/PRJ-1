#!/usr/bin/env python3
"""
File System Watcher Module
Provides real-time monitoring of project changes for automatic updates.
"""

import os
import time
import threading
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Callable
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent, DirModifiedEvent, DirCreatedEvent, DirDeletedEvent

logger = logging.getLogger(__name__)


class ProjectEventHandler(FileSystemEventHandler):
    """Event handler for file system changes in projects."""
    
    def __init__(self, callback: Callable[[str, str, str], None]):
        self.callback = callback
        self.ignore_patterns = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules', 
            '.vscode', '.idea', 'build', 'dist', '*.pyc', '*.pyo', '*.pyd'
        }
    
    def _should_ignore(self, path: str) -> bool:
        """Check if a path should be ignored."""
        path_obj = Path(path)
        
        # Check if any part of the path matches ignore patterns
        for part in path_obj.parts:
            if part in self.ignore_patterns:
                return True
        
        # Check file extensions
        if path_obj.suffix in ['.pyc', '.pyo', '.pyd']:
            return True
        
        return False
    
    def _get_event_type(self, event: FileSystemEvent) -> str:
        """Get the type of file system event."""
        if isinstance(event, FileCreatedEvent):
            return 'file_created'
        elif isinstance(event, FileModifiedEvent):
            return 'file_modified'
        elif isinstance(event, FileDeletedEvent):
            return 'file_deleted'
        elif isinstance(event, DirCreatedEvent):
            return 'dir_created'
        elif isinstance(event, DirModifiedEvent):
            return 'dir_modified'
        elif isinstance(event, DirDeletedEvent):
            return 'dir_deleted'
        else:
            return 'unknown'
    
    def on_any_event(self, event: FileSystemEvent):
        """Handle any file system event."""
        if self._should_ignore(event.src_path):
            return
        
        event_type = self._get_event_type(event)
        
        # Only process relevant events
        if event_type in ['file_created', 'file_modified', 'file_deleted', 'dir_created', 'dir_deleted']:
            try:
                self.callback(event.src_path, event_type, str(event.event_type))
            except Exception as e:
                logger.error(f"Error in file system event callback: {e}")


class FileSystemWatcher:
    """Monitors file system changes in project directories."""
    
    def __init__(self, scan_callback: Optional[Callable[[str], None]] = None):
        self.observer = Observer()
        self.watched_projects: Dict[str, Dict[str, Any]] = {}
        self.scan_callback = scan_callback
        self.event_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        self.change_callbacks: List[Callable[[str, str, str], None]] = []
        self._lock = threading.Lock()
        self._debounce_timers: Dict[str, threading.Timer] = {}
        self.debounce_delay = 1.0  # seconds
        
        # Statistics
        self.stats = {
            'events_processed': 0,
            'projects_watched': 0,
            'scan_triggers': 0,
            'start_time': datetime.now()
        }
    
    def add_change_callback(self, callback: Callable[[str, str, str], None]) -> None:
        """Add a callback to be called when file changes occur."""
        self.change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[str, str, str], None]) -> None:
        """Remove a change callback."""
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
    
    def _handle_file_change(self, path: str, event_type: str, raw_event_type: str) -> None:
        """Handle a file system change event."""
        with self._lock:
            self.stats['events_processed'] += 1
            
            # Add to event history
            event_info = {
                'path': path,
                'event_type': event_type,
                'raw_event_type': raw_event_type,
                'timestamp': datetime.now().isoformat()
            }
            
            self.event_history.append(event_info)
            
            # Limit history size
            if len(self.event_history) > self.max_history_size:
                self.event_history.pop(0)
            
            # Call all registered callbacks
            for callback in self.change_callbacks:
                try:
                    callback(path, event_type, raw_event_type)
                except Exception as e:
                    logger.error(f"Error in change callback: {e}")
    
    def _debounced_scan_trigger(self, project_path: str) -> None:
        """Trigger a project scan with debouncing."""
        # Cancel any existing timer for this project
        if project_path in self._debounce_timers:
            self._debounce_timers[project_path].cancel()
        
        # Create new timer
        def trigger_scan():
            with self._lock:
                if project_path in self._debounce_timers:
                    del self._debounce_timers[project_path]
            
            logger.info(f"Triggering scan for project: {project_path}")
            self.stats['scan_triggers'] += 1
            
            if self.scan_callback:
                try:
                    self.scan_callback(project_path)
                except Exception as e:
                    logger.error(f"Error in scan callback: {e}")
        
        timer = threading.Timer(self.debounce_delay, trigger_scan)
        self._debounce_timers[project_path] = timer
        timer.start()
    
    def watch_project(self, project_path: str, project_info: Optional[Dict[str, Any]] = None) -> bool:
        """Start watching a project directory for changes.
        
        Args:
            project_path: Path to the project directory
            project_info: Optional project information dictionary
            
        Returns:
            True if watching started successfully, False otherwise
        """
        path = Path(project_path)
        if not path.exists() or not path.is_dir():
            logger.error(f"Project path does not exist or is not a directory: {project_path}")
            return False
        
        with self._lock:
            # Check if already watching
            if project_path in self.watched_projects:
                logger.warning(f"Already watching project: {project_path}")
                return True
            
            try:
                # Create event handler
                event_handler = ProjectEventHandler(self._handle_file_change)
                
                # Add watch
                watch = self.observer.schedule(event_handler, project_path, recursive=True)
                
                # Store watch information
                self.watched_projects[project_path] = {
                    'watch': watch,
                    'project_info': project_info or {},
                    'start_time': datetime.now().isoformat(),
                    'event_count': 0
                }
                
                self.stats['projects_watched'] = len(self.watched_projects)
                logger.info(f"Started watching project: {project_path}")
                return True
                
            except Exception as e:
                logger.error(f"Error watching project {project_path}: {e}")
                return False
    
    def unwatch_project(self, project_path: str) -> bool:
        """Stop watching a project directory.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            True if unwatching was successful, False otherwise
        """
        with self._lock:
            if project_path not in self.watched_projects:
                logger.warning(f"Project not being watched: {project_path}")
                return False
            
            try:
                # Get watch information
                watch_info = self.watched_projects[project_path]
                watch = watch_info['watch']
                
                # Remove watch
                self.observer.remove_watch(watch)
                
                # Cancel any debounce timer
                if project_path in self._debounce_timers:
                    self._debounce_timers[project_path].cancel()
                    del self._debounce_timers[project_path]
                
                # Remove from watched projects
                del self.watched_projects[project_path]
                
                self.stats['projects_watched'] = len(self.watched_projects)
                logger.info(f"Stopped watching project: {project_path}")
                return True
                
            except Exception as e:
                logger.error(f"Error unwatching project {project_path}: {e}")
                return False
    
    def start(self) -> bool:
        """Start the file system watcher."""
        try:
            if not self.observer.is_alive():
                self.observer.start()
                logger.info("File system watcher started")
                return True
            else:
                logger.warning("File system watcher already running")
                return True
        except Exception as e:
            logger.error(f"Error starting file system watcher: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the file system watcher."""
        try:
            if self.observer.is_alive():
                # Cancel all debounce timers
                with self._lock:
                    for timer in self._debounce_timers.values():
                        timer.cancel()
                    self._debounce_timers.clear()
                
                self.observer.stop()
                self.observer.join()
                logger.info("File system watcher stopped")
                return True
            else:
                logger.warning("File system watcher not running")
                return True
        except Exception as e:
            logger.error(f"Error stopping file system watcher: {e}")
            return False
    
    def is_watching(self, project_path: str) -> bool:
        """Check if a project is being watched.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            True if project is being watched, False otherwise
        """
        return project_path in self.watched_projects
    
    def get_watched_projects(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all watched projects."""
        with self._lock:
            return self.watched_projects.copy()
    
    def get_recent_events(self, project_path: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent file system events.
        
        Args:
            project_path: Optional project path to filter events
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        with self._lock:
            events = self.event_history.copy()
            
            # Filter by project path if specified
            if project_path:
                events = [e for e in events if e['path'].startswith(project_path)]
            
            # Return most recent events first
            return events[-limit:][::-1]
    
    def get_project_events(self, project_path: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events for a specific project.
        
        Args:
            project_path: Path to the project directory
            limit: Maximum number of events to return
            
        Returns:
            List of recent events for the project
        """
        return self.get_recent_events(project_path, limit)
    
    def clear_event_history(self) -> None:
        """Clear the event history."""
        with self._lock:
            self.event_history.clear()
            logger.info("Event history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get watcher statistics."""
        with self._lock:
            uptime = datetime.now() - self.stats['start_time']
            return {
                **self.stats,
                'uptime_seconds': uptime.total_seconds(),
                'uptime_formatted': str(uptime).split('.')[0],
                'watcher_running': self.observer.is_alive(),
                'debounce_timers_active': len(self._debounce_timers),
                'event_history_size': len(self.event_history)
            }
    
    def configure_debounce(self, delay_seconds: float) -> None:
        """Configure the debounce delay for scan triggers.
        
        Args:
            delay_seconds: Delay in seconds before triggering a scan
        """
        self.debounce_delay = max(0.1, delay_seconds)  # Minimum 0.1 seconds
        logger.info(f"Debounce delay configured to {self.debounce_delay} seconds")
    
    def set_ignore_patterns(self, patterns: Set[str]) -> None:
        """Set the patterns to ignore when watching files.
        
        Args:
            patterns: Set of patterns to ignore
        """
        # Update all existing event handlers
        for watch_info in self.watched_projects.values():
            watch = watch_info['watch']
            if hasattr(watch, '_handler'):
                watch._handler.ignore_patterns = patterns
        
        logger.info(f"Ignore patterns updated: {patterns}")
    
    def trigger_scan_for_project(self, project_path: str) -> None:
        """Manually trigger a scan for a specific project.
        
        Args:
            project_path: Path to the project directory
        """
        if project_path in self.watched_projects:
            self._debounced_scan_trigger(project_path)
        else:
            logger.warning(f"Project not being watched: {project_path}")
    
    def restart_watching(self) -> bool:
        """Restart watching all projects.
        
        Returns:
            True if restart was successful, False otherwise
        """
        logger.info("Restarting file system watcher...")
        
        # Stop current watcher
        if not self.stop():
            return False
        
        # Get list of watched projects
        with self._lock:
            projects_to_watch = list(self.watched_projects.keys())
            project_infos = {path: info['project_info'] for path, info in self.watched_projects.items()}
        
        # Clear watched projects
        self.watched_projects.clear()
        
        # Start watcher again
        if not self.start():
            return False
        
        # Restart watching all projects
        success = True
        for project_path in projects_to_watch:
            if not self.watch_project(project_path, project_infos.get(project_path)):
                success = False
        
        return success
