#!/usr/bin/env python3
"""
Dependency Management System
Provides comprehensive tracking and management of project dependencies.
"""

import os
import json
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
import logging
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class DependencyManager:
    """Manages project dependencies with tracking, analysis, and update capabilities."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.dependency_cache_file = self.data_dir / "dependency_cache.json"
        self.dependency_stats_file = self.data_dir / "dependency_stats.json"
        
        # Dependency cache for performance
        self.dependency_cache: Dict[str, Dict[str, Any]] = {}
        self.dependency_stats: Dict[str, Any] = {}
        
        # Thread safety
        self._cache_lock = threading.Lock()
        self._stats_lock = threading.Lock()
        
        # Supported package managers and their commands
        self.package_managers = {
            'pip': {
                'install': 'pip install',
                'update': 'pip install --upgrade',
                'remove': 'pip uninstall -y',
                'list': 'pip list',
                'freeze': 'pip freeze',
                'check': 'pip check',
                'files': ['requirements.txt', 'setup.py', 'pyproject.toml']
            },
            'npm': {
                'install': 'npm install',
                'update': 'npm update',
                'remove': 'npm uninstall',
                'list': 'npm list',
                'outdated': 'npm outdated',
                'audit': 'npm audit',
                'files': ['package.json', 'package-lock.json']
            },
            'maven': {
                'install': 'mvn install',
                'update': 'mvn dependency:updates',
                'list': 'mvn dependency:list',
                'tree': 'mvn dependency:tree',
                'files': ['pom.xml']
            },
            'gradle': {
                'build': './gradlew build',
                'dependencies': './gradlew dependencies',
                'refresh': './gradlew --refresh-dependencies',
                'files': ['build.gradle', 'build.gradle.kts', 'settings.gradle']
            },
            'cargo': {
                'build': 'cargo build',
                'update': 'cargo update',
                'check': 'cargo check',
                'tree': 'cargo tree',
                'files': ['Cargo.toml', 'Cargo.lock']
            },
            'go': {
                'build': 'go build',
                'download': 'go mod download',
                'tidy': 'go mod tidy',
                'graph': 'go mod graph',
                'files': ['go.mod', 'go.sum']
            }
        }
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # Load cached data
        self._load_cache()
        self._load_stats()
    
    def _load_cache(self) -> None:
        """Load dependency cache from file."""
        if self.dependency_cache_file.exists():
            try:
                with open(self.dependency_cache_file, 'r') as f:
                    self.dependency_cache = json.load(f)
                logger.info(f"Loaded dependency cache with {len(self.dependency_cache)} entries")
            except Exception as e:
                logger.error(f"Error loading dependency cache: {e}")
                self.dependency_cache = {}
    
    def _save_cache(self) -> None:
        """Save dependency cache to file."""
        try:
            with open(self.dependency_cache_file, 'w') as f:
                json.dump(self.dependency_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving dependency cache: {e}")
    
    def _load_stats(self) -> None:
        """Load dependency statistics from file."""
        if self.dependency_stats_file.exists():
            try:
                with open(self.dependency_stats_file, 'r') as f:
                    self.dependency_stats = json.load(f)
            except Exception as e:
                logger.error(f"Error loading dependency stats: {e}")
                self.dependency_stats = {}
    
    def _save_stats(self) -> None:
        """Save dependency statistics to file."""
        try:
            with open(self.dependency_stats_file, 'w') as f:
                json.dump(self.dependency_stats, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving dependency stats: {e}")
    
    def analyze_project_dependencies(self, project_path: str) -> Dict[str, Any]:
        """Analyze dependencies for a project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dictionary containing dependency analysis results
        """
        path = Path(project_path)
        if not path.exists() or not path.is_dir():
            return {'error': 'Invalid project path'}
        
        cache_key = self._get_cache_key(project_path)
        
        # Check cache first
        with self._cache_lock:
            if cache_key in self.dependency_cache:
                cached_data = self.dependency_cache[cache_key]
                # Check if cache is still valid (less than 24 hours old)
                cache_time = datetime.fromisoformat(cached_data.get('cached_at', '2000-01-01'))
                if datetime.now() - cache_time < timedelta(hours=24):
                    return cached_data
        
        # Analyze dependencies
        analysis = {
            'project_path': project_path,
            'package_managers': [],
            'dependencies': {},
            'total_dependencies': 0,
            'outdated_dependencies': [],
            'vulnerabilities': [],
            'dependency_tree': {},
            'analysis_time': datetime.now().isoformat(),
            'cached_at': datetime.now().isoformat()
        }
        
        # Detect package managers and analyze dependencies
        for pm_name, pm_info in self.package_managers.items():
            if self._has_package_manager_files(path, pm_info['files']):
                analysis['package_managers'].append(pm_name)
                deps = self._analyze_package_manager_dependencies(path, pm_name)
                if deps:
                    analysis['dependencies'][pm_name] = deps
                    analysis['total_dependencies'] += len(deps)
        
        # Check for outdated dependencies
        analysis['outdated_dependencies'] = self._check_outdated_dependencies(project_path, analysis['dependencies'])
        
        # Check for vulnerabilities (basic check)
        analysis['vulnerabilities'] = self._check_vulnerabilities(analysis['dependencies'])
        
        # Build dependency tree
        analysis['dependency_tree'] = self._build_dependency_tree(analysis['dependencies'])
        
        # Update cache
        with self._cache_lock:
            self.dependency_cache[cache_key] = analysis
            self._save_cache()
        
        # Update statistics
        self._update_stats(analysis)
        
        return analysis
    
    def _get_cache_key(self, project_path: str) -> str:
        """Generate a cache key for a project."""
        return hashlib.md5(project_path.encode()).hexdigest()
    
    def _has_package_manager_files(self, project_path: Path, files: List[str]) -> bool:
        """Check if project has files for a specific package manager."""
        for file_pattern in files:
            if '*' in file_pattern:
                # Handle wildcards
                if any(project_path.glob(file_pattern)):
                    return True
            else:
                # Handle exact filenames
                if (project_path / file_pattern).exists():
                    return True
        return False
    
    def _analyze_package_manager_dependencies(self, project_path: Path, package_manager: str) -> List[Dict[str, Any]]:
        """Analyze dependencies for a specific package manager."""
        dependencies = []
        
        if package_manager == 'pip':
            dependencies.extend(self._analyze_python_dependencies(project_path))
        elif package_manager == 'npm':
            dependencies.extend(self._analyze_npm_dependencies(project_path))
        elif package_manager == 'maven':
            dependencies.extend(self._analyze_maven_dependencies(project_path))
        elif package_manager == 'gradle':
            dependencies.extend(self._analyze_gradle_dependencies(project_path))
        elif package_manager == 'cargo':
            dependencies.extend(self._analyze_cargo_dependencies(project_path))
        elif package_manager == 'go':
            dependencies.extend(self._analyze_go_dependencies(project_path))
        
        return dependencies
    
    def _analyze_python_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Analyze Python dependencies."""
        dependencies = []
        
        # Check requirements.txt
        req_file = project_path / 'requirements.txt'
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            dep = self._parse_python_dependency(line)
                            dep['source_file'] = 'requirements.txt'
                            dep['source_line'] = line_num
                            dependencies.append(dep)
            except Exception as e:
                logger.warning(f"Could not read requirements.txt: {e}")
        
        # Check pyproject.toml
        pyproject_file = project_path / 'pyproject.toml'
        if pyproject_file.exists():
            try:
                with open(pyproject_file, 'r') as f:
                    content = f.read()
                    deps = self._parse_pyproject_dependencies(content)
                    for dep in deps:
                        dep['source_file'] = 'pyproject.toml'
                        dependencies.append(dep)
            except Exception as e:
                logger.warning(f"Could not parse pyproject.toml: {e}")
        
        # Check setup.py
        setup_file = project_path / 'setup.py'
        if setup_file.exists():
            try:
                with open(setup_file, 'r') as f:
                    content = f.read()
                    deps = self._parse_setup_py_dependencies(content)
                    for dep in deps:
                        dep['source_file'] = 'setup.py'
                        dependencies.append(dep)
            except Exception as e:
                logger.warning(f"Could not parse setup.py: {e}")
        
        return dependencies
    
    def _parse_python_dependency(self, line: str) -> Dict[str, Any]:
        """Parse a Python dependency line."""
        # Parse version specifiers
        match = re.match(r'^([a-zA-Z0-9\-_.]+)([><=!~]+.*)?$', line)
        if match:
            name, version_spec = match.groups()
            return {
                'name': name,
                'version_spec': version_spec or '',
                'current_version': '',
                'latest_version': '',
                'is_outdated': False,
                'type': 'python',
                'package_manager': 'pip'
            }
        else:
            return {
                'name': line,
                'version_spec': '',
                'current_version': '',
                'latest_version': '',
                'is_outdated': False,
                'type': 'python',
                'package_manager': 'pip'
            }
    
    def _parse_pyproject_dependencies(self, content: str) -> List[Dict[str, Any]]:
        """Parse dependencies from pyproject.toml."""
        dependencies = []
        
        # Extract dependencies from [project.dependencies]
        match = re.search(r'\[project\.dependencies\](.*?)(?=\[|$)', content, re.DOTALL)
        if match:
            deps_section = match.group(1)
            for dep in re.findall(r'[\'\"](.*?)[\'\"]', deps_section):
                dep = dep.strip()
                if dep:
                    parsed = self._parse_python_dependency(dep)
                    dependencies.append(parsed)
        
        return dependencies
    
    def _parse_setup_py_dependencies(self, content: str) -> List[Dict[str, Any]]:
        """Parse dependencies from setup.py."""
        dependencies = []
        
        # Extract install_requires
        match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if match:
            reqs_str = match.group(1)
            for req in re.findall(r'[\'\"](.*?)[\'\"]', reqs_str):
                req = req.strip()
                if req:
                    parsed = self._parse_python_dependency(req)
                    dependencies.append(parsed)
        
        return dependencies
    
    def _analyze_npm_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Analyze NPM dependencies."""
        dependencies = []
        
        package_file = project_path / 'package.json'
        if package_file.exists():
            try:
                with open(package_file, 'r') as f:
                    content = f.read()
                    
                    # Extract dependencies
                    deps_match = re.search(r'"dependencies"\s*:\s*\{(.*?)\}', content, re.DOTALL)
                    if deps_match:
                        deps_section = deps_match.group(1)
                        for dep in re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', deps_section):
                            name, version = dep
                            dependencies.append({
                                'name': name,
                                'version_spec': version,
                                'current_version': version,
                                'latest_version': '',
                                'is_outdated': False,
                                'type': 'npm',
                                'package_manager': 'npm',
                                'dev_dependency': False
                            })
                    
                    # Extract devDependencies
                    dev_deps_match = re.search(r'"devDependencies"\s*:\s*\{(.*?)\}', content, re.DOTALL)
                    if dev_deps_match:
                        deps_section = dev_deps_match.group(1)
                        for dep in re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', deps_section):
                            name, version = dep
                            dependencies.append({
                                'name': name,
                                'version_spec': version,
                                'current_version': version,
                                'latest_version': '',
                                'is_outdated': False,
                                'type': 'npm-dev',
                                'package_manager': 'npm',
                                'dev_dependency': True
                            })
            except Exception as e:
                logger.warning(f"Could not parse package.json: {e}")
        
        return dependencies
    
    def _analyze_maven_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Analyze Maven dependencies."""
        dependencies = []
        
        pom_file = project_path / 'pom.xml'
        if pom_file.exists():
            try:
                with open(pom_file, 'r') as f:
                    content = f.read()
                    
                    # Extract dependencies
                    deps_section = re.search(r'<dependencies>(.*?)</dependencies>', content, re.DOTALL)
                    if deps_section:
                        deps_content = deps_section.group(1)
                        for dep in re.findall(r'<dependency>(.*?)</dependency>', deps_content, re.DOTALL):
                            group_id = re.search(r'<groupId>(.*?)</groupId>', dep)
                            artifact_id = re.search(r'<artifactId>(.*?)</artifactId>', dep)
                            version = re.search(r'<version>(.*?)</version>', dep)
                            scope = re.search(r'<scope>(.*?)</scope>', dep)
                            
                            if group_id and artifact_id:
                                dependencies.append({
                                    'name': f"{group_id.group(1)}:{artifact_id.group(1)}",
                                    'version_spec': version.group(1) if version else '',
                                    'current_version': version.group(1) if version else '',
                                    'latest_version': '',
                                    'is_outdated': False,
                                    'type': 'maven',
                                    'package_manager': 'maven',
                                    'scope': scope.group(1) if scope else 'compile'
                                })
            except Exception as e:
                logger.warning(f"Could not parse pom.xml: {e}")
        
        return dependencies
    
    def _analyze_gradle_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Analyze Gradle dependencies."""
        dependencies = []
        
        for gradle_file in project_path.glob('build.gradle*'):
            try:
                with open(gradle_file, 'r') as f:
                    content = f.read()
                    
                    # Extract implementation dependencies
                    for match in re.finditer(r'implementation\s+[\'"](.*?)[\'"]', content):
                        dependencies.append({
                            'name': match.group(1),
                            'version_spec': '',
                            'current_version': '',
                            'latest_version': '',
                            'is_outdated': False,
                            'type': 'gradle',
                            'package_manager': 'gradle',
                            'configuration': 'implementation'
                        })
                    
                    # Extract api dependencies
                    for match in re.finditer(r'api\s+[\'"](.*?)[\'"]', content):
                        dependencies.append({
                            'name': match.group(1),
                            'version_spec': '',
                            'current_version': '',
                            'latest_version': '',
                            'is_outdated': False,
                            'type': 'gradle-api',
                            'package_manager': 'gradle',
                            'configuration': 'api'
                        })
            except Exception as e:
                logger.warning(f"Could not parse {gradle_file}: {e}")
        
        return dependencies
    
    def _analyze_cargo_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Analyze Cargo dependencies."""
        dependencies = []
        
        cargo_file = project_path / 'Cargo.toml'
        if cargo_file.exists():
            try:
                with open(cargo_file, 'r') as f:
                    content = f.read()
                    
                    # Extract dependencies
                    deps_section = re.search(r'\[dependencies\](.*?)(?=\[|$)', content, re.DOTALL)
                    if deps_section:
                        deps_content = deps_section.group(1)
                        for dep in re.findall(r'([a-zA-Z0-9\-_]+)\s*=\s*[\'"](.*?)[\'"]', deps_content):
                            name, version = dep
                            dependencies.append({
                                'name': name,
                                'version_spec': version,
                                'current_version': version,
                                'latest_version': '',
                                'is_outdated': False,
                                'type': 'cargo',
                                'package_manager': 'cargo'
                            })
            except Exception as e:
                logger.warning(f"Could not parse Cargo.toml: {e}")
        
        return dependencies
    
    def _analyze_go_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Analyze Go dependencies."""
        dependencies = []
        
        go_mod_file = project_path / 'go.mod'
        if go_mod_file.exists():
            try:
                with open(go_mod_file, 'r') as f:
                    content = f.read()
                    
                    # Extract require statements
                    for match in re.finditer(r'require\s+([^\s]+)\s+([^\s]+)', content):
                        name, version = match.groups()
                        dependencies.append({
                            'name': name,
                            'version_spec': version,
                            'current_version': version,
                            'latest_version': '',
                            'is_outdated': False,
                            'type': 'go',
                            'package_manager': 'go'
                        })
            except Exception as e:
                logger.warning(f"Could not parse go.mod: {e}")
        
        return dependencies
    
    def _check_outdated_dependencies(self, project_path: str, dependencies: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Check for outdated dependencies."""
        outdated = []
        
        # This is a simplified check - in a real implementation, you would
        # query package repositories for the latest versions
        for pm_name, pm_deps in dependencies.items():
            for dep in pm_deps:
                # For now, just mark dependencies without version specs as potentially outdated
                if not dep.get('version_spec'):
                    dep['is_outdated'] = True
                    outdated.append(dep)
        
        return outdated
    
    def _check_vulnerabilities(self, dependencies: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Check for known vulnerabilities in dependencies."""
        vulnerabilities = []
        
        # This is a placeholder - in a real implementation, you would
        # query vulnerability databases like CVE, Snyk, etc.
        for pm_name, pm_deps in dependencies.items():
            for dep in pm_deps:
                # Example: Check for known vulnerable versions
                if dep['name'] in ['requests', 'urllib3'] and dep.get('current_version', '').startswith('2.'):
                    # This is just an example - not real vulnerability data
                    vulnerabilities.append({
                        'dependency': dep['name'],
                        'current_version': dep.get('current_version', ''),
                        'vulnerability_id': 'CVE-2023-XXXXX',
                        'severity': 'high',
                        'description': 'Example vulnerability check'
                    })
        
        return vulnerabilities
    
    def _build_dependency_tree(self, dependencies: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Build a dependency tree structure."""
        tree = {}
        
        for pm_name, pm_deps in dependencies.items():
            tree[pm_name] = {
                'dependencies': pm_deps,
                'count': len(pm_deps),
                'types': list(set(dep['type'] for dep in pm_deps))
            }
        
        return tree
    
    def _update_stats(self, analysis: Dict[str, Any]) -> None:
        """Update dependency statistics."""
        with self._stats_lock:
            self.dependency_stats['last_analysis'] = datetime.now().isoformat()
            self.dependency_stats['total_projects_analyzed'] = self.dependency_stats.get('total_projects_analyzed', 0) + 1
            self.dependency_stats['total_dependencies'] = self.dependency_stats.get('total_dependencies', 0) + analysis['total_dependencies']
            self.dependency_stats['total_outdated'] = self.dependency_stats.get('total_outdated', 0) + len(analysis['outdated_dependencies'])
            self.dependency_stats['total_vulnerabilities'] = self.dependency_stats.get('total_vulnerabilities', 0) + len(analysis['vulnerabilities'])
            
            # Update package manager stats
            for pm_name in analysis['package_managers']:
                self.dependency_stats.setdefault('package_managers', {})[pm_name] = \
                    self.dependency_stats.get('package_managers', {}).get(pm_name, 0) + 1
            
            self._save_stats()
    
    def get_dependency_stats(self) -> Dict[str, Any]:
        """Get dependency management statistics."""
        with self._stats_lock:
            return self.dependency_stats.copy()
    
    def clear_cache(self) -> None:
        """Clear the dependency cache."""
        with self._cache_lock:
            self.dependency_cache.clear()
            if self.dependency_cache_file.exists():
                self.dependency_cache_file.unlink()
            logger.info("Dependency cache cleared")
    
    def get_project_dependencies(self, project_path: str) -> Optional[Dict[str, Any]]:
        """Get cached dependency analysis for a project."""
        cache_key = self._get_cache_key(project_path)
        with self._cache_lock:
            return self.dependency_cache.get(cache_key)
    
    def update_dependencies(self, project_path: str, package_manager: str, dependencies: List[str]) -> bool:
        """Update dependencies for a project.
        
        Args:
            project_path: Path to the project directory
            package_manager: Package manager to use
            dependencies: List of dependencies to update
            
        Returns:
            True if update was successful, False otherwise
        """
        if package_manager not in self.package_managers:
            logger.error(f"Unsupported package manager: {package_manager}")
            return False
        
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_path)
            
            # Update dependencies
            for dep in dependencies:
                cmd = f"{self.package_managers[package_manager]['update']} {dep}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Failed to update {dep}: {result.stderr}")
                    return False
            
            # Clear cache for this project
            cache_key = self._get_cache_key(project_path)
            with self._cache_lock:
                if cache_key in self.dependency_cache:
                    del self.dependency_cache[cache_key]
                    self._save_cache()
            
            logger.info(f"Successfully updated dependencies for {project_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating dependencies: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def install_dependencies(self, project_path: str, package_manager: str, dependencies: List[str]) -> bool:
        """Install dependencies for a project.
        
        Args:
            project_path: Path to the project directory
            package_manager: Package manager to use
            dependencies: List of dependencies to install
            
        Returns:
            True if installation was successful, False otherwise
        """
        if package_manager not in self.package_managers:
            logger.error(f"Unsupported package manager: {package_manager}")
            return False
        
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_path)
            
            # Install dependencies
            for dep in dependencies:
                cmd = f"{self.package_managers[package_manager]['install']} {dep}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Failed to install {dep}: {result.stderr}")
                    return False
            
            # Clear cache for this project
            cache_key = self._get_cache_key(project_path)
            with self._cache_lock:
                if cache_key in self.dependency_cache:
                    del self.dependency_cache[cache_key]
                    self._save_cache()
            
            logger.info(f"Successfully installed dependencies for {project_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error installing dependencies: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def remove_dependencies(self, project_path: str, package_manager: str, dependencies: List[str]) -> bool:
        """Remove dependencies from a project.
        
        Args:
            project_path: Path to the project directory
            package_manager: Package manager to use
            dependencies: List of dependencies to remove
            
        Returns:
            True if removal was successful, False otherwise
        """
        if package_manager not in self.package_managers:
            logger.error(f"Unsupported package manager: {package_manager}")
            return False
        
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_path)
            
            # Remove dependencies
            for dep in dependencies:
                cmd = f"{self.package_managers[package_manager]['remove']} {dep}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Failed to remove {dep}: {result.stderr}")
                    return False
            
            # Clear cache for this project
            cache_key = self._get_cache_key(project_path)
            with self._cache_lock:
                if cache_key in self.dependency_cache:
                    del self.dependency_cache[cache_key]
                    self._save_cache()
            
            logger.info(f"Successfully removed dependencies for {project_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing dependencies: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def get_supported_package_managers(self) -> Dict[str, str]:
        """Get list of supported package managers."""
        return {pm: info.get('description', pm) for pm, info in self.package_managers.items()}
    
    def is_package_manager_supported(self, package_manager: str) -> bool:
        """Check if a package manager is supported."""
        return package_manager in self.package_managers
