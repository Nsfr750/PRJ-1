#!/usr/bin/env python3
"""
Tag Manager Module
Provides tagging and categorization functionality for projects.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from datetime import datetime
import re


def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class TagManager:
    """Manages project tags, categories, notes, and favorites."""
    
    # Predefined project categories
    PREDEFINED_CATEGORIES = {
        "web": {
            "name": "Web",
            "description": "Web applications and websites",
            "keywords": ["web", "website", "http", "html", "css", "javascript", "react", "vue", "angular", "django", "flask", "fastapi"]
        },
        "desktop": {
            "name": "Desktop", 
            "description": "Desktop applications",
            "keywords": ["desktop", "gui", "pyside", "pyqt", "tkinter", "wx", "electron", "winforms", "wpf"]
        },
        "mobile": {
            "name": "Mobile",
            "description": "Mobile applications",
            "keywords": ["mobile", "android", "ios", "flutter", "react-native", "kotlin", "swift", "cordova"]
        },
        "library": {
            "name": "Library",
            "description": "Libraries and frameworks",
            "keywords": ["library", "framework", "sdk", "api", "package", "module", "lib"]
        },
        "tool": {
            "name": "Tool",
            "description": "Command-line tools and utilities",
            "keywords": ["tool", "utility", "cli", "script", "automation", "batch", "shell"]
        },
        "game": {
            "name": "Game",
            "description": "Games and game development",
            "keywords": ["game", "pygame", "unity", "unreal", "godot", "engine", "gaming"]
        },
        "data": {
            "name": "Data",
            "description": "Data science and machine learning",
            "keywords": ["data", "ml", "ai", "machine", "learning", "pandas", "numpy", "tensorflow", "pytorch", "scikit"]
        },
        "devops": {
            "name": "DevOps",
            "description": "DevOps and infrastructure",
            "keywords": ["devops", "docker", "kubernetes", "ci", "cd", "jenkins", "github-actions", "terraform"]
        },
        "system": {
            "name": "System",
            "description": "System programming and low-level tools",
            "keywords": ["system", "kernel", "driver", "embedded", "firmware", "os", "operating", "system"]
        },
        "other": {
            "name": "Other",
            "description": "Other project types",
            "keywords": []
        }
    }
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.tags_file = self.data_path / "tags.json"
        self.categories_file = self.data_path / "categories.json"
        self.notes_file = self.data_path / "notes.json"
        self.favorites_file = self.data_path / "favorites.json"
        self.recent_projects_file = self.data_path / "recent_projects.json"
        
        # Ensure data directory exists
        self.data_path.mkdir(exist_ok=True)
        
        # Initialize data structures
        self.project_tags: Dict[str, Set[str]] = {}  # project_path -> set of tags
        self.project_categories: Dict[str, str] = {}  # project_path -> category_key
        self.all_tags: Set[str] = set()
        self.custom_categories: Dict[str, Dict[str, Any]] = {}
        self.project_notes: Dict[str, str] = {}  # project_path -> note content
        self.favorite_projects: Set[str] = set()  # set of project paths
        self.recent_projects: List[Dict[str, Any]] = []  # list of recent project access records
        self.max_recent_projects = 20  # maximum number of recent projects to track
        
        # Load existing data
        self.load_data()
    
    def load_data(self) -> None:
        """Load tags, categories, notes, favorites, and recent projects from files."""
        try:
            # Load tags
            if self.tags_file.exists():
                with open(self.tags_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.project_tags = {k: set(v) for k, v in data.get('project_tags', {}).items()}
                    self.all_tags = set(data.get('all_tags', []))
            
            # Load categories
            if self.categories_file.exists():
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.project_categories = data.get('project_categories', {})
                    self.custom_categories = data.get('custom_categories', {})
            
            # Load notes
            if self.notes_file.exists():
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.project_notes = data.get('project_notes', {})
            
            # Load favorites
            if self.favorites_file.exists():
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.favorite_projects = set(data.get('favorite_projects', []))
            
            # Load recent projects
            if self.recent_projects_file.exists():
                with open(self.recent_projects_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.recent_projects = data.get('recent_projects', [])
        except Exception as e:
            print(f"Error loading tag data: {e}")
            # Initialize with empty data
            self.project_tags = {}
            self.project_categories = {}
            self.all_tags = set()
            self.custom_categories = {}
            self.project_notes = {}
            self.favorite_projects = set()
            self.recent_projects = []
    
    def save_data(self) -> bool:
        """Save tags, categories, notes, favorites, and recent projects to files."""
        try:
            # Save tags
            tags_data = {
                'project_tags': {k: list(v) for k, v in self.project_tags.items()},
                'all_tags': list(self.all_tags),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.tags_file, 'w', encoding='utf-8') as f:
                json.dump(tags_data, f, indent=2, ensure_ascii=False)
            
            # Save categories
            categories_data = {
                'project_categories': self.project_categories,
                'custom_categories': self.custom_categories,
                'predefined_categories': self.PREDEFINED_CATEGORIES,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(categories_data, f, indent=2, ensure_ascii=False)
            
            # Save notes
            notes_data = {
                'project_notes': self.project_notes,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump(notes_data, f, indent=2, ensure_ascii=False)
            
            # Save favorites
            favorites_data = {
                'favorite_projects': list(self.favorite_projects),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(favorites_data, f, indent=2, ensure_ascii=False)
            
            # Save recent projects
            recent_projects_data = {
                'recent_projects': self.recent_projects,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.recent_projects_file, 'w', encoding='utf-8') as f:
                json.dump(recent_projects_data, f, indent=2, ensure_ascii=False, default=json_serializer)
            
            return True
        except Exception as e:
            print(f"Error saving tag data: {e}")
            return False
    
    def add_tag_to_project(self, project_path: str, tag: str) -> bool:
        """Add a tag to a project."""
        if not project_path or not tag:
            return False
        
        # Clean and validate tag
        tag = self._clean_tag(tag)
        if not tag:
            return False
        
        # Add tag to project
        if project_path not in self.project_tags:
            self.project_tags[project_path] = set()
        
        self.project_tags[project_path].add(tag)
        self.all_tags.add(tag)
        
        return self.save_data()
    
    def remove_tag_from_project(self, project_path: str, tag: str) -> bool:
        """Remove a tag from a project."""
        if project_path not in self.project_tags:
            return True
        
        tag = self._clean_tag(tag)
        if tag in self.project_tags[project_path]:
            self.project_tags[project_path].remove(tag)
            
            # Remove from all_tags if no longer used
            if not any(tag in tags for tags in self.project_tags.values()):
                self.all_tags.discard(tag)
            
            return self.save_data()
        
        return True
    
    def set_project_tags(self, project_path: str, tags: List[str]) -> bool:
        """Set all tags for a project (replaces existing tags)."""
        if not project_path:
            return False
        
        # Clean and validate tags
        cleaned_tags = [self._clean_tag(tag) for tag in tags if self._clean_tag(tag)]
        
        # Remove old tags from global set
        if project_path in self.project_tags:
            for old_tag in self.project_tags[project_path]:
                if not any(old_tag in tags for tags in self.project_tags.values() if tags != self.project_tags[project_path]):
                    self.all_tags.discard(old_tag)
        
        # Set new tags
        self.project_tags[project_path] = set(cleaned_tags)
        self.all_tags.update(cleaned_tags)
        
        return self.save_data()
    
    def get_project_tags(self, project_path: str) -> List[str]:
        """Get all tags for a project."""
        return list(self.project_tags.get(project_path, set()))
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        return sorted(list(self.all_tags))
    
    def get_projects_by_tag(self, tag: str) -> List[str]:
        """Get all projects that have a specific tag."""
        tag = self._clean_tag(tag)
        return [path for path, tags in self.project_tags.items() if tag in tags]
    
    def set_project_category(self, project_path: str, category_key: str) -> bool:
        """Set the category for a project."""
        if not project_path:
            return False
        
        # Validate category
        if category_key not in self.get_all_categories():
            return False
        
        self.project_categories[project_path] = category_key
        return self.save_data()
    
    def get_project_category(self, project_path: str) -> Optional[str]:
        """Get the category for a project."""
        return self.project_categories.get(project_path)
    
    def get_all_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get all available categories (predefined + custom)."""
        categories = self.PREDEFINED_CATEGORIES.copy()
        categories.update(self.custom_categories)
        return categories
    
    def get_predefined_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get only the predefined categories."""
        return self.PREDEFINED_CATEGORIES.copy()
    
    def get_custom_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get only the custom categories."""
        return self.custom_categories.copy()
    
    def add_custom_category(self, key: str, name: str, description: str = "", keywords: List[str] = None) -> bool:
        """Add a custom category."""
        if not key or not name:
            return False
        
        if keywords is None:
            keywords = []
        
        self.custom_categories[key] = {
            "name": name,
            "description": description,
            "keywords": keywords
        }
        
        return self.save_data()
    
    def remove_custom_category(self, key: str) -> bool:
        """Remove a custom category."""
        if key not in self.custom_categories:
            return True
        
        # Remove category from projects
        projects_to_update = [path for path, cat in self.project_categories.items() if cat == key]
        for project_path in projects_to_update:
            del self.project_categories[project_path]
        
        # Remove custom category
        del self.custom_categories[key]
        
        return self.save_data()
    
    def get_projects_by_category(self, category_key: str) -> List[str]:
        """Get all projects in a specific category."""
        return [path for path, cat in self.project_categories.items() if cat == category_key]
    
    def suggest_category_for_project(self, project_info: Dict[str, Any]) -> Optional[str]:
        """Suggest a category for a project based on its information."""
        name = project_info.get('name', '').lower()
        description = project_info.get('description', '').lower()
        language = project_info.get('language', '').lower()
        
        # Combine all text for analysis
        text = f"{name} {description} {language}"
        
        # Score each category based on keyword matches
        category_scores = {}
        for cat_key, cat_info in self.get_all_categories().items():
            score = 0
            for keyword in cat_info.get('keywords', []):
                if keyword.lower() in text:
                    score += 1
            
            # Bonus for language matches
            if language and language in cat_info.get('keywords', []):
                score += 2
            
            if score > 0:
                category_scores[cat_key] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return None
    
    def _clean_tag(self, tag: str) -> Optional[str]:
        """Clean and validate a tag."""
        if not tag:
            return None
        
        # Remove leading/trailing whitespace
        tag = tag.strip()
        
        # Convert to lowercase for consistency
        tag = tag.lower()
        
        # Remove special characters (keep alphanumeric, spaces, hyphens, underscores)
        tag = re.sub(r'[^\w\s-]', '', tag)
        
        # Replace multiple spaces with single space
        tag = re.sub(r'\s+', ' ', tag)
        
        # Limit length
        if len(tag) > 50:
            tag = tag[:50]
        
        return tag if tag else None
    
    def get_tag_statistics(self) -> Dict[str, Any]:
        """Get statistics about tags and categories."""
        stats = {
            'total_tags': len(self.all_tags),
            'total_projects_with_tags': len(self.project_tags),
            'total_projects_with_categories': len(self.project_categories),
            'most_used_tags': [],
            'category_distribution': {}
        }
        
        # Most used tags
        tag_counts = {}
        for tags in self.project_tags.values():
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        stats['most_used_tags'] = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Category distribution
        cat_counts = {}
        for category in self.project_categories.values():
            cat_counts[category] = cat_counts.get(category, 0) + 1
        
        stats['category_distribution'] = cat_counts
        
        return stats
    
    def search_projects_by_tags(self, tags: List[str], match_all: bool = False) -> List[str]:
        """Search for projects by tags."""
        if not tags:
            return []
        
        cleaned_tags = [self._clean_tag(tag) for tag in tags if self._clean_tag(tag)]
        if not cleaned_tags:
            return []
        
        matching_projects = []
        for project_path, project_tags in self.project_tags.items():
            if match_all:
                # All tags must be present
                if all(tag in project_tags for tag in cleaned_tags):
                    matching_projects.append(project_path)
            else:
                # Any tag can be present
                if any(tag in project_tags for tag in cleaned_tags):
                    matching_projects.append(project_path)
        
        return matching_projects
    
    # Project Notes Methods
    def set_project_note(self, project_path: str, note: str) -> bool:
        """Set or update a note for a project."""
        if not project_path:
            return False
        
        self.project_notes[project_path] = note
        return self.save_data()
    
    def get_project_note(self, project_path: str) -> str:
        """Get the note for a project."""
        return self.project_notes.get(project_path, "")
    
    def delete_project_note(self, project_path: str) -> bool:
        """Delete the note for a project."""
        if project_path in self.project_notes:
            del self.project_notes[project_path]
            return self.save_data()
        return True
    
    def get_all_projects_with_notes(self) -> List[str]:
        """Get all projects that have notes."""
        return list(self.project_notes.keys())
    
    def search_projects_by_notes(self, search_text: str) -> List[str]:
        """Search for projects by note content."""
        if not search_text:
            return []
        
        search_lower = search_text.lower()
        matching_projects = []
        
        for project_path, note in self.project_notes.items():
            if search_lower in note.lower():
                matching_projects.append(project_path)
        
        return matching_projects
    
    # Favorite Projects Methods
    def add_favorite_project(self, project_path: str) -> bool:
        """Add a project to favorites."""
        if not project_path:
            return False
        if project_path not in self.favorite_projects:
            self.favorite_projects.add(project_path)
            return self.save_data()
        return True
    
    def remove_favorite_project(self, project_path: str) -> bool:
        """Remove a project from favorites."""
        if not project_path:
            return False
        if project_path in self.favorite_projects:
            self.favorite_projects.remove(project_path)
            return self.save_data()
        return True
    
    def is_favorite_project(self, project_path: str) -> bool:
        """Check if a project is in favorites."""
        if not project_path:
            return False
        return project_path in self.favorite_projects
    
    def toggle_favorite_project(self, project_path: str) -> bool:
        """Toggle a project's favorite status."""
        if self.is_favorite_project(project_path):
            return self.remove_favorite_project(project_path)
        else:
            return self.add_favorite_project(project_path)
    
    def get_all_favorite_projects(self) -> List[str]:
        """Get all favorite projects."""
        return list(self.favorite_projects)
    
    def get_favorite_count(self) -> int:
        """Get the number of favorite projects."""
        return len(self.favorite_projects)
    
    def add_recent_project(self, project_path: str, project_name: str, project_data: Dict[str, Any] = None) -> bool:
        """Add a project to the recent projects list."""
        if not project_path or not project_name:
            return False
        
        # Create recent project record
        recent_record = {
            'path': project_path,
            'name': project_name,
            'accessed_at': datetime.now().isoformat(),
            'project_data': project_data or {}
        }
        
        # Remove existing entry for the same project (if any)
        self.recent_projects = [r for r in self.recent_projects if r['path'] != project_path]
        
        # Add to the beginning of the list
        self.recent_projects.insert(0, recent_record)
        
        # Limit to maximum number of recent projects
        if len(self.recent_projects) > self.max_recent_projects:
            self.recent_projects = self.recent_projects[:self.max_recent_projects]
        
        return self.save_data()
    
    def get_recent_projects(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get the list of recent projects."""
        if limit is None:
            return self.recent_projects.copy()
        else:
            return self.recent_projects[:limit]
    
    def clear_recent_projects(self) -> bool:
        """Clear all recent projects."""
        self.recent_projects = []
        return self.save_data()
    
    def remove_recent_project(self, project_path: str) -> bool:
        """Remove a specific project from recent projects."""
        original_length = len(self.recent_projects)
        self.recent_projects = [r for r in self.recent_projects if r['path'] != project_path]
        
        if len(self.recent_projects) < original_length:
            return self.save_data()
        return True  # Project wasn't in the list, but that's not an error
    
    def is_recent_project(self, project_path: str) -> bool:
        """Check if a project is in the recent projects list."""
        return any(r['path'] == project_path for r in self.recent_projects)
    
    def get_recent_project_count(self) -> int:
        """Get the number of recent projects."""
        return len(self.recent_projects)
    
    def track_project_access(self, project_path: str, project_name: str = None, project_data: Dict[str, Any] = None) -> bool:
        """Track when a project is accessed for recent projects list."""
        if not project_path:
            return False
        
        # If project name not provided, try to extract from path
        if project_name is None:
            project_name = Path(project_path).name
        
        return self.add_recent_project(project_path, project_name, project_data)
