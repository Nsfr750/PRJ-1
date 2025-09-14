#!/usr/bin/env python3
"""
Project Scanner Module
Scans the X:\\GitHub folder for projects and provides browsing functionality.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class ProjectScanner:
    """Scans and manages project information from GitHub folder."""
    
    def __init__(self, github_path: str = "X:\\GitHub", data_path: str = "data"):
        self.github_path = Path(github_path)
        self.data_path = Path(data_path)
        self.projects: List[Dict[str, Any]] = []
        self.last_scan: Optional[datetime] = None
        
        # Ensure data directory exists
        self.data_path.mkdir(exist_ok=True)
        
        # Load saved data if available
        self.load_projects()
    
    def set_scan_directory(self, directory_path: str) -> bool:
        """Set the directory to scan for projects.
        
        Args:
            directory_path: Path to the directory to scan
            
        Returns:
            bool: True if directory exists and was set, False otherwise
        """
        path = Path(directory_path)
        if path.exists() and path.is_dir():
            self.github_path = path
            # Clear existing projects when changing directory
            self.projects = []
            self.last_scan = None
            return True
        return False
    
    def get_scan_directory(self) -> str:
        """Get the current scan directory path.
        
        Returns:
            str: Current scan directory path
        """
        return str(self.github_path)
    
    def scan_projects(self) -> List[Dict[str, Any]]:
        """Scan the GitHub folder for projects."""
        self.projects = []
        
        if not self.github_path.exists():
            print(f"GitHub path not found: {self.github_path}")
            return self.projects
        
        # Scan all directories in the GitHub folder
        for item in self.github_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                project_info = self._analyze_project(item)
                if project_info:
                    self.projects.append(project_info)
        
        self.last_scan = datetime.now()
        
        # Save the scanned data
        self.save_projects()
        
        return self.projects
    
    def save_projects(self) -> bool:
        """Save project data to JSON file in data/ folder."""
        try:
            data_file = self.data_path / "projects.json"
            
            # Prepare data for serialization (convert datetime objects to strings)
            serializable_data = {
                'projects': [],
                'last_scan': self.last_scan.isoformat() if self.last_scan else None,
                'scan_directory': str(self.github_path)
            }
            
            for project in self.projects:
                project_copy = project.copy()
                # Convert datetime objects to strings for JSON serialization
                if 'modified' in project_copy and isinstance(project_copy['modified'], datetime):
                    project_copy['modified'] = project_copy['modified'].isoformat()
                serializable_data['projects'].append(project_copy)
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving projects: {e}")
            return False
    
    def load_projects(self) -> bool:
        """Load project data from JSON file in data/ folder."""
        try:
            data_file = self.data_path / "projects.json"
            
            if not data_file.exists():
                return False
            
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load scan directory if available
            scan_directory = data.get('scan_directory')
            if scan_directory:
                self.github_path = Path(scan_directory)
            
            # Load projects
            self.projects = data.get('projects', [])
            
            # Convert string dates back to datetime objects
            for project in self.projects:
                if 'modified' in project and isinstance(project['modified'], str):
                    try:
                        project['modified'] = datetime.fromisoformat(project['modified'])
                    except ValueError:
                        # If parsing fails, use current time
                        project['modified'] = datetime.now()
            
            # Load last scan time
            last_scan_str = data.get('last_scan')
            if last_scan_str:
                try:
                    self.last_scan = datetime.fromisoformat(last_scan_str)
                except ValueError:
                    self.last_scan = None
            
            return True
        except Exception as e:
            print(f"Error loading projects: {e}")
            return False
    
    def clear_saved_data(self) -> bool:
        """Clear saved project data."""
        try:
            data_file = self.data_path / "projects.json"
            if data_file.exists():
                data_file.unlink()
            self.projects = []
            self.last_scan = None
            return True
        except Exception as e:
            print(f"Error clearing saved data: {e}")
            return False
    
    def _analyze_project(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single project folder and extract information."""
        try:
            project_info = {
                'name': project_path.name,
                'path': str(project_path),
                'size': self._get_folder_size(project_path),
                'modified': datetime.fromtimestamp(project_path.stat().st_mtime),
                'has_git': (project_path / '.git').exists(),
                'has_readme': False,
                'has_requirements': False,
                'has_setup': False,
                'main_file': None,
                'description': '',
                'language': 'Unknown',
                'version': 'Unknown'
            }
            
            # Check for common files
            for file in project_path.iterdir():
                if file.is_file():
                    if file.name.lower().startswith('readme'):
                        project_info['has_readme'] = True
                        project_info['description'] = self._extract_readme_description(file)
                    elif file.name.lower() in ['requirements.txt', 'pyproject.toml', 'environment.yml']:
                        project_info['has_requirements'] = True
                    elif file.name.lower() in ['setup.py', 'setup.cfg', 'pyproject.toml']:
                        project_info['has_setup'] = True
                    elif file.name.lower() in ['main.py', 'app.py', 'index.py', '__init__.py']:
                        project_info['main_file'] = file.name
                    elif file.name.lower().endswith('.py'):
                        project_info['language'] = 'Python'
                    elif file.name.lower().endswith(('.js', '.ts', '.jsx', '.tsx')):
                        project_info['language'] = 'JavaScript/TypeScript'
                    elif file.name.lower().endswith(('.html', '.css', '.scss')):
                        project_info['language'] = 'Web'
                    elif file.name.lower().endswith(('.java', '.kt', '.scala')):
                        project_info['language'] = 'Java/JVM'
                    elif file.name.lower().endswith(('.cpp', '.c', '.h', '.hpp')):
                        project_info['language'] = 'C/C++'
                    elif file.name.lower().endswith(('.go', '.rs')):
                        project_info['language'] = f"{file.suffix[1:].upper()}"
            
            # Try to extract version from setup files or version files
            project_info['version'] = self._extract_version(project_path)
            
            return project_info
            
        except Exception as e:
            print(f"Error analyzing project {project_path}: {e}")
            return None
    
    def _get_folder_size(self, path: Path) -> int:
        """Calculate the total size of a folder in bytes."""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
            return total_size
        except (OSError, IOError):
            return 0
    
    def _extract_readme_description(self, readme_path: Path) -> str:
        """Extract the first line from README as description."""
        try:
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip()
                # Remove markdown formatting
                if first_line.startswith('#'):
                    first_line = first_line[1:].strip()
                return first_line[:100]  # Limit to 100 characters
        except Exception:
            return ''
    
    def _extract_version(self, project_path: Path) -> str:
        """Extract version from common version files, searching recursively in all subdirectories."""
        version_files = [
            'version.py',
            '__version__.py',
            'setup.py',
            'pyproject.toml',
            'package.json',
            'pom.xml'
        ]
        
        # First check root directory
        for version_file in version_files:
            file_path = project_path / version_file
            if file_path.exists():
                try:
                    if version_file.endswith('.py'):
                        return self._extract_version_from_python(file_path)
                    elif version_file.endswith('.toml'):
                        return self._extract_version_from_toml(file_path)
                    elif version_file.endswith('.json'):
                        return self._extract_version_from_json(file_path)
                except Exception:
                    continue
        
        # If not found in root, recursively search for version.py files in subdirectories
        for version_file in version_files:
            if version_file.endswith('.py'):  # Only search recursively for Python version files
                for file_path in project_path.rglob(version_file):
                    try:
                        version = self._extract_version_from_python(file_path)
                        if version and version != 'Unknown':
                            return version
                    except Exception:
                        continue
        
        return 'Unknown'
    
    def _extract_version_from_python(self, file_path: Path) -> str:
        """Extract version from Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for __version__ = "x.x.x" or __version__ = 'x.x.x'
                import re
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return 'Unknown'
    
    def _extract_version_from_toml(self, file_path: Path) -> str:
        """Extract version from TOML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple regex for version in TOML
                import re
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return 'Unknown'
    
    def _extract_version_from_json(self, file_path: Path) -> str:
        """Extract version from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', 'Unknown')
        except Exception:
            pass
        return 'Unknown'
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get the list of scanned projects."""
        return self.projects
    
    def filter_projects(self, filter_text: str = '', language: str = '') -> List[Dict[str, Any]]:
        """Filter projects based on search text and language."""
        filtered = self.projects
        
        if filter_text:
            filter_text = filter_text.lower()
            filtered = [
                p for p in filtered 
                if filter_text in p['name'].lower() or 
                   filter_text in p['description'].lower()
            ]
        
        if language and language != 'All':
            filtered = [p for p in filtered if p['language'] == language]
        
        return filtered
    
    def get_languages(self) -> List[str]:
        """Get list of available languages."""
        languages = set(p['language'] for p in self.projects)
        return sorted(['All'] + list(languages))
    
    def get_project_stats(self) -> Dict[str, Any]:
        """Get statistics about the scanned projects."""
        if not self.projects:
            return {}
        
        languages = {}
        total_size = 0
        git_projects = 0
        
        for project in self.projects:
            lang = project['language']
            languages[lang] = languages.get(lang, 0) + 1
            total_size += project['size']
            if project['has_git']:
                git_projects += 1
        
        return {
            'total_projects': len(self.projects),
            'total_size': total_size,
            'git_projects': git_projects,
            'languages': languages,
            'last_scan': self.last_scan
        }


def main():
    """Test function for the project scanner."""
    scanner = ProjectScanner()
    print("Scanning projects...")
    projects = scanner.scan_projects()
    
    print(f"\nFound {len(projects)} projects:")
    for project in projects:
        print(f"- {project['name']} ({project['language']}) - {project['version']}")
    
    stats = scanner.get_project_stats()
    print(f"\nStatistics: {stats}")


if __name__ == "__main__":
    main()
