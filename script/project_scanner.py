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

from .tag_manager import TagManager


class ProjectScanner:
    """Scans and manages project information from GitHub folder."""
    
    def __init__(self, github_path: str = "X:\\GitHub", data_path: str = "data"):
        self.github_path = Path(github_path)
        self.data_path = Path(data_path)
        self.projects: List[Dict[str, Any]] = []
        self.last_scan: Optional[datetime] = None
        
        # Initialize tag manager
        self.tag_manager = TagManager(data_path)
        
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
                'version': 'Unknown',
                'tags': [],
                'category': None,
                'note': '',
                'is_favorite': False
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
                    # Language detection - collect all languages found
                    file_ext = file.suffix.lower()
                    file_name = file.name.lower()
                    
                    # Initialize language set if not exists
                    if 'detected_languages' not in project_info:
                        project_info['detected_languages'] = set()
                    
                    # Detect language based on file extension
                    if file_ext == '.py':
                        project_info['detected_languages'].add('Python')
                    elif file_ext in ('.js', '.mjs', '.cjs'):
                        project_info['detected_languages'].add('JavaScript')
                    elif file_ext in ('.ts', '.tsx'):
                        project_info['detected_languages'].add('TypeScript')
                    elif file_ext in ('.jsx',) :
                        project_info['detected_languages'].add('React/JSX')
                    elif file_ext in ('.html', '.htm'):
                        project_info['detected_languages'].add('HTML')
                    elif file_ext in ('.css', '.scss', '.sass', '.less'):
                        project_info['detected_languages'].add('CSS')
                    elif file_ext == '.java':
                        project_info['detected_languages'].add('Java')
                    elif file_ext == '.kt':
                        project_info['detected_languages'].add('Kotlin')
                    elif file_ext == '.scala':
                        project_info['detected_languages'].add('Scala')
                    elif file_ext in ('.cpp', '.cc', '.cxx'):
                        project_info['detected_languages'].add('C++')
                    elif file_ext in ('.c', '.h'):
                        project_info['detected_languages'].add('C')
                    elif file_ext == '.go':
                        project_info['detected_languages'].add('Go')
                    elif file_ext == '.rs':
                        project_info['detected_languages'].add('Rust')
                    elif file_ext == '.rb':
                        project_info['detected_languages'].add('Ruby')
                    elif file_ext in ('.php', '.php3', '.php4', '.php5'):
                        project_info['detected_languages'].add('PHP')
                    elif file_ext == '.swift':
                        project_info['detected_languages'].add('Swift')
                    elif file_ext == '.dart':
                        project_info['detected_languages'].add('Dart')
                    elif file_ext in ('.sh', '.bash', '.zsh'):
                        project_info['detected_languages'].add('Shell')
                    elif file_ext == '.r':
                        project_info['detected_languages'].add('R')
                    elif file_ext == '.m':
                        project_info['detected_languages'].add('Objective-C')
                    elif file_ext == '.lua':
                        project_info['detected_languages'].add('Lua')
                    elif file_ext in ('.pl', '.pm'):
                        project_info['detected_languages'].add('Perl')
                    elif file_ext in ('.cs', '.csx'):
                        project_info['detected_languages'].add('C#')
                    elif file_ext == '.vb':
                        project_info['detected_languages'].add('Visual Basic')
                    elif file_ext == '.f90':
                        project_info['detected_languages'].add('Fortran')
                    elif file_ext == '.asm':
                        project_info['detected_languages'].add('Assembly')
                    elif file_ext == '.sql':
                        project_info['detected_languages'].add('SQL')
                    elif file_ext in ('.dockerfile', '.dockerignore'):
                        project_info['detected_languages'].add('Docker')
                    elif file_ext in ('.yaml', '.yml'):
                        project_info['detected_languages'].add('YAML')
                    elif file_ext == '.json':
                        project_info['detected_languages'].add('JSON')
                    elif file_ext == '.xml':
                        project_info['detected_languages'].add('XML')
                    elif file_ext == '.md':
                        project_info['detected_languages'].add('Markdown')
                    elif file_ext in ('.txt', '.log', '.conf', '.ini', '.cfg'):
                        project_info['detected_languages'].add('Text/Config')
            
            # Determine primary language from detected languages
            if 'detected_languages' in project_info:
                project_info['language'] = self._determine_primary_language(project_info['detected_languages'])
                # Remove temporary field
                del project_info['detected_languages']
            
            # Extract version
            project_info['version'] = self._extract_version(project_path)
            
            # Load tags, category, notes, and favorites from tag manager
            project_info['tags'] = self.tag_manager.get_project_tags(str(project_path))
            project_info['category'] = self.tag_manager.get_project_category(str(project_path))
            project_info['note'] = self.tag_manager.get_project_note(str(project_path))
            project_info['is_favorite'] = self.tag_manager.is_favorite_project(str(project_path))
            
            # Auto-suggest category if not set
            if not project_info['category']:
                suggested_category = self.tag_manager.suggest_category_for_project(project_info)
                if suggested_category:
                    project_info['category'] = suggested_category
                    self.tag_manager.set_project_category(str(project_path), suggested_category)
            
            return project_info
        except Exception as e:
            print(f"Error analyzing project {project_path}: {e}")
            return None
    
    def _determine_primary_language(self, detected_languages: set) -> str:
        """Determine the primary language from a set of detected languages.
        
        Args:
            detected_languages: Set of detected language names
            
        Returns:
            str: The primary language name
        """
        if not detected_languages:
            return 'Unknown'
        
        # Priority order for primary languages (most important first)
        language_priority = [
            'Python', 'JavaScript', 'TypeScript', 'React/JSX', 'Java', 'C++', 'C',
            'Go', 'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'C#',
            'Visual Basic', 'Objective-C', 'Dart', 'Lua', 'Perl', 'R', 'Fortran',
            'Assembly', 'SQL', 'Shell'
        ]
        
        # Secondary/supporting languages (lower priority)
        supporting_languages = ['HTML', 'CSS', 'JSON', 'XML', 'YAML', 'Markdown', 'Text/Config', 'Docker']
        
        # Convert to list for processing
        languages = list(detected_languages)
        
        # If only one language, return it
        if len(languages) == 1:
            return languages[0]
        
        # Separate primary and supporting languages
        primary_found = []
        supporting_found = []
        
        for lang in languages:
            if lang in language_priority:
                primary_found.append(lang)
            elif lang in supporting_languages:
                supporting_found.append(lang)
            else:
                # Unknown language, treat as primary
                primary_found.append(lang)
        
        # If we have primary languages, return the highest priority one
        if primary_found:
            for priority_lang in language_priority:
                if priority_lang in primary_found:
                    return priority_lang
            # If no priority match, return first primary language
            return primary_found[0]
        
        # If only supporting languages, try to determine context
        if supporting_found:
            if 'HTML' in supporting_found and 'CSS' in supporting_found:
                return 'Web'
            elif 'HTML' in supporting_found:
                return 'HTML'
            elif 'CSS' in supporting_found:
                return 'CSS'
            else:
                return supporting_found[0]
        
        return 'Unknown'
    
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
            'pyproject.toml',
            'package.json',
            'pom.xml',
            'Cargo.toml',
            'go.mod',
            'composer.json',
            'Gemfile',
            'build.gradle',
            'build.sbt',
            'pubspec.yaml',
            'project.clj',
            'mix.exs',
            'dune-project',
            'stack.yaml',
            'cabal.project',
            'shard.yml',
            'meson.build',
            'CMakeLists.txt'
        ]
        
        # First check root directory
        for version_file in version_files:
            file_path = project_path / version_file
            if file_path.exists():
                try:
                    if version_file.endswith('.py'):
                        version = self._extract_version_from_python(file_path)
                    elif version_file.endswith('.toml'):
                        version = self._extract_version_from_toml(file_path)
                    elif version_file.endswith('.json'):
                        version = self._extract_version_from_json(file_path)
                    elif version_file.endswith('.xml'):
                        version = self._extract_version_from_xml(file_path)
                    elif version_file == 'go.mod':
                        version = self._extract_version_from_go_mod(file_path)
                    elif version_file == 'Cargo.toml':
                        version = self._extract_version_from_cargo_toml(file_path)
                    elif version_file == 'Gemfile':
                        version = self._extract_version_from_gemfile(file_path)
                    elif version_file in ('build.gradle', 'build.sbt'):
                        version = self._extract_version_from_gradle_sbt(file_path)
                    elif version_file.endswith(('.yaml', '.yml')):
                        version = self._extract_version_from_yaml(file_path)
                    elif version_file in ('mix.exs', 'project.clj', 'shard.yml'):
                        version = self._extract_version_from_lang_file(file_path)
                    else:
                        version = self._extract_version_generic(file_path)
                    
                    if version and version != 'Unknown':
                        return version
                except Exception:
                    continue
        
        # If not found in root, recursively search for common version files
        for version_file in ['version.py', '__version__.py']:
            for file_path in project_path.rglob(version_file):
                try:
                    version = self._extract_version_from_python(file_path)
                    if version and version != 'Unknown':
                        return version
                except Exception:
                    continue
        
        # Try to find version in git tags as last resort
        try:
            version = self._extract_version_from_git(project_path)
            if version and version != 'Unknown':
                return version
        except Exception:
            pass
        
        return 'Unknown'
    
    def _extract_version_from_python(self, file_path: Path) -> str:
        """Extract version from Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                import re
                
                # Pattern 1: __version__ = "x.x.x" or __version__ = 'x.x.x'
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
                
                # Pattern 2: VERSION = "x.x.x" or VERSION = 'x.x.x'
                match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
                
                # Pattern 3: version = "x.x.x" or version = 'x.x.x'
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
                
                # Pattern 4: setup.py with version parameter
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
                
                # Pattern 5: Semantic versioning pattern (x.x.x)
                match = re.search(r'(\d+\.\d+\.\d+(?:-[\w.]+)?)', content)
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
                import re
                
                # Pattern 1: version = "x.x.x" or version = 'x.x.x'
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
                
                # Pattern 2: [project] version = "x.x.x"
                match = re.search(r'\[project\][^\[]*version\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
                if match:
                    return match.group(1)
                
                # Pattern 3: [tool.poetry] version = "x.x.x"
                match = re.search(r'\[tool\.poetry\][^\[]*version\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
                if match:
                    return match.group(1)
                
                # Pattern 4: [package] version = "x.x.x"
                match = re.search(r'\[package\][^\[]*version\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
                if match:
                    return match.group(1)
                
                # Pattern 5: Generic semantic version
                match = re.search(r'(\d+\.\d+\.\d+(?:-[\w.]+)?)', content)
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
                
                # Try different common version keys
                version_keys = ['version', 'Version', 'VERSION', 'appVersion', 'apiVersion']
                for key in version_keys:
                    if key in data and data[key]:
                        return str(data[key])
                
                # Try nested version (common in package.json)
                if 'package' in data and isinstance(data['package'], dict):
                    for key in version_keys:
                        if key in data['package'] and data['package'][key]:
                            return str(data['package'][key])
                
                # Try semantic version pattern in stringified content
                with open(file_path, 'r', encoding='utf-8') as f2:
                    content = f2.read()
                    import re
                    match = re.search(r'(\d+\.\d+\.\d+(?:-[\w.]+)?)', content)
                    if match:
                        return match.group(1)
        except Exception:
            pass
        return 'Unknown'
    
    def _extract_version_from_xml(self, file_path: Path) -> str:
        """Extract version from XML file (e.g., pom.xml)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                import re
                
                # Pattern 1: <version>x.x.x</version>
                match = re.search(r'<version[^>]*>([^<]+)</version>', content)
                if match:
                    return match.group(1)
                
                # Pattern 2: <project><version>x.x.x</version></project>
                match = re.search(r'<project[^>]*>.*?<version[^>]*>([^<]+)</version>', content, re.DOTALL)
                if match:
                    return match.group(1)
                
                # Pattern 3: version="x.x.x" attribute
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
                
                # Pattern 4: Generic semantic version
                match = re.search(r'(\d+\.\d+\.\d+(?:-[\w.]+)?)', content)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return 'Unknown'
    
    def _extract_version_from_go_mod(self, file_path: Path) -> str:
        """Extract version from go.mod file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                import re
                
                # Pattern: go x.xx or module version
                match = re.search(r'go\s+(\d+\.\d+(?:\.\d+)?)', content)
                if match:
                    return match.group(1)
                
                # Pattern: semantic version in module path
                match = re.search(r'(\d+\.\d+\.\d+(?:-[\w.]+)?)', content)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return 'Unknown'
    
    def _extract_version_from_cargo_toml(self, file_path: Path) -> str:
        """Extract version from Cargo.toml file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                import re
                
                # Pattern: [package] version = "x.x.x"
                match = re.search(r'\[package\][^\[]*version\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
                if match:
                    return match.group(1)
                
                # Pattern: version = "x.x.x"
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return 'Unknown'
    
    def _extract_version_from_gemfile(self, file_path: Path) -> str:
        """Extract version from Gemfile."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                import re
                
                # Pattern: gem 'name', 'x.x.x'
                match = re.search(r'gem\s+[\'\"]\w+[\'\"],\s*[\'\"]([^\'\"]+)[\'\"]', content)
                if match:
                    return match.group(1)
                
                # Pattern: ruby 'x.x.x'
                match = re.search(r'ruby\s+[\'\"]([^\'\"]+)[\'\"]', content)
                if match:
                    return match.group(1)
                
                # Pattern: semantic version
                match = re.search(r'(\d+\.\d+\.\d+(?:-[\w.]+)?)', content)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return 'Unknown'
    
    def _extract_version_from_gradle_sbt(self, file_path: Path) -> str:
        """Extract version from build.gradle or build.sbt file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                import re
                
                # Pattern: version 'x.x.x' or version "x.x.x"
                match = re.search(r'version\s+["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
                
                # Pattern: version = 'x.x.x' or version = "x.x.x"
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
                
                # Pattern: semantic version
                match = re.search(r'(\d+\.\d+\.\d+(?:-[\w.]+)?)', content)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return 'Unknown'
    
    def _extract_version_from_yaml(self, file_path: Path) -> str:
        """Extract version from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                import re
                
                # Pattern: version: x.x.x
                match = re.search(r'version:\s*([^\n\s]+)', content)
                if match:
                    return match.group(1)
                
                # Pattern: version: "x.x.x" or version: 'x.x.x'
                match = re.search(r'version:\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
                
                # Pattern: semantic version
                match = re.search(r'(\d+\.\d+\.\d+(?:-[\w.]+)?)', content)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return 'Unknown'
    
    def _extract_version_from_lang_file(self, file_path: Path) -> str:
        """Extract version from language-specific files (mix.exs, project.clj, etc.)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                import re
                
                # Generic version patterns
                patterns = [
                    r'version:\s*["\']([^"\']+)["\']',
                    r'version\s*["\']([^"\']+)["\']',
                    r':version\s*["\']([^"\']+)["\']',
                    r'defversion\s+["\']([^"\']+)["\']'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content)
                    if match:
                        return match.group(1)
                
                # Semantic version pattern
                match = re.search(r'(\d+\.\d+\.\d+(?:-[\w.]+)?)', content)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return 'Unknown'
    
    def _extract_version_generic(self, file_path: Path) -> str:
        """Extract version using generic patterns from any file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                import re
                
                # Common version patterns
                patterns = [
                    r'version\s*[=:]\s*["\']([^"\']+)["\']',
                    r'VERSION\s*[=:]\s*["\']([^"\']+)["\']',
                    r'__version__\s*[=:]\s*["\']([^"\']+)["\']',
                    r'Application\.version\s*[=:]\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        return match.group(1)
                
                # Semantic version pattern
                match = re.search(r'(\d+\.\d+\.\d+(?:-[\w.]+)?)', content)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return 'Unknown'
    
    def _extract_version_from_git(self, project_path: Path) -> str:
        """Extract version from git tags."""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                # Remove 'v' prefix if present
                if version.startswith('v'):
                    version = version[1:]
                return version
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
