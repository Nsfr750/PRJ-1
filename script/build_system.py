#!/usr/bin/env python3
"""
Build System Detection and Management Module
Detects and manages various build systems (Makefile, CMake, etc.) and project dependencies.
"""

import os
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BuildSystemDetector:
    """Detects and analyzes build systems in projects."""
    
    # Common build system files and patterns
    BUILD_SYSTEMS = {
        'makefile': {
            'files': ['Makefile', 'makefile', 'GNUmakefile'],
            'patterns': [r'^\w+\s*:', r'^\.PHONY:', r'^all\s*:'],
            'description': 'Makefile-based build system'
        },
        'cmake': {
            'files': ['CMakeLists.txt', '*.cmake'],
            'patterns': [r'cmake_minimum_required', r'project\s*\(', r'add_executable', r'add_library'],
            'description': 'CMake build system'
        },
        'meson': {
            'files': ['meson.build', 'meson.options'],
            'patterns': [r'project\s*\(', r'executable\s*\(', r'library\s*\('],
            'description': 'Meson build system'
        },
        'ninja': {
            'files': ['build.ninja'],
            'patterns': [r'^rule\s+', r'^build\s+'],
            'description': 'Ninja build system'
        },
        'autotools': {
            'files': ['configure.ac', 'configure.in', 'Makefile.am'],
            'patterns': [r'AC_INIT', r'AM_INIT_AUTOMAKE', r'AC_PROG_CC'],
            'description': 'GNU Autotools'
        },
        'scons': {
            'files': ['SConstruct', 'SConscript'],
            'patterns': [r'Program\s*\(', r'Library\s*\(', r'Environment\s*\('],
            'description': 'SCons build system'
        },
        'bazel': {
            'files': ['WORKSPACE', 'BUILD', 'BUILD.bazel'],
            'patterns': [r'package\s*\(', r'cc_binary\s*\(', r'py_library\s*\('],
            'description': 'Bazel build system'
        },
        'gradle': {
            'files': ['build.gradle', 'build.gradle.kts', 'settings.gradle'],
            'patterns': [r'plugins\s*\{', r'dependencies\s*\{', r'android\s*\{'],
            'description': 'Gradle build system'
        },
        'maven': {
            'files': ['pom.xml'],
            'patterns': [r'<project>', r'<dependencies>', r'<groupId>'],
            'description': 'Maven build system'
        },
        'npm': {
            'files': ['package.json', 'package-lock.json'],
            'patterns': [r'"name":', r'"dependencies":', r'"scripts":'],
            'description': 'NPM/Node.js build system'
        },
        'pip': {
            'files': ['requirements.txt', 'setup.py', 'pyproject.toml'],
            'patterns': [r'install_requires', r'dependencies', r'\[build-system\]'],
            'description': 'Python pip build system'
        },
        'cargo': {
            'files': ['Cargo.toml', 'Cargo.lock'],
            'patterns': [r'\[package\]', r'\[dependencies\]', r'name\s*='],
            'description': 'Rust Cargo build system'
        },
        'go': {
            'files': ['go.mod', 'go.sum'],
            'patterns': [r'module\s+', r'require\s+', r'go\s+'],
            'description': 'Go modules build system'
        },
        'dotnet': {
            'files': ['*.csproj', '*.fsproj', '*.vbproj'],
            'patterns': [r'<Project>', r'<PackageReference', r'<TargetFramework>'],
            'description': '.NET build system'
        }
    }
    
    def __init__(self):
        self.detected_systems: Dict[str, Dict[str, Any]] = {}
        self.dependency_cache: Dict[str, List[Dict[str, Any]]] = {}
    
    def detect_build_system(self, project_path: str) -> Dict[str, Any]:
        """Detect build system in a project directory.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dictionary containing build system information
        """
        path = Path(project_path)
        if not path.exists() or not path.is_dir():
            return {'type': 'unknown', 'description': 'Invalid project path'}
        
        result = {
            'type': 'unknown',
            'description': 'No build system detected',
            'files': [],
            'dependencies': [],
            'build_commands': [],
            'detected_at': datetime.now().isoformat()
        }
        
        # Check for each build system
        for system_name, system_info in self.BUILD_SYSTEMS.items():
            detected_files = []
            patterns_matched = []
            
            # Check for build system files
            for file_pattern in system_info['files']:
                if '*' in file_pattern:
                    # Handle wildcards
                    for file_path in path.glob(file_pattern):
                        if file_path.is_file():
                            detected_files.append(file_path.name)
                else:
                    # Handle exact filenames
                    file_path = path / file_pattern
                    if file_path.is_file():
                        detected_files.append(file_path.name)
            
            # Check for patterns in detected files
            if detected_files:
                for file_name in detected_files:
                    file_path = path / file_name
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for pattern in system_info['patterns']:
                                if re.search(pattern, content, re.MULTILINE):
                                    patterns_matched.append(pattern)
                    except Exception as e:
                        logger.warning(f"Could not read {file_path}: {e}")
            
            # If we found files and/or patterns, this is our build system
            if detected_files or patterns_matched:
                result = {
                    'type': system_name,
                    'description': system_info['description'],
                    'files': detected_files,
                    'patterns_matched': patterns_matched,
                    'dependencies': self._extract_dependencies(path, system_name),
                    'build_commands': self._get_build_commands(system_name),
                    'detected_at': datetime.now().isoformat()
                }
                break
        
        return result
    
    def _extract_dependencies(self, project_path: Path, build_system: str) -> List[Dict[str, Any]]:
        """Extract dependencies from build system files.
        
        Args:
            project_path: Path to the project directory
            build_system: Type of build system
            
        Returns:
            List of dependency dictionaries
        """
        dependencies = []
        
        if build_system == 'pip':
            dependencies.extend(self._extract_python_dependencies(project_path))
        elif build_system == 'npm':
            dependencies.extend(self._extract_npm_dependencies(project_path))
        elif build_system == 'maven':
            dependencies.extend(self._extract_maven_dependencies(project_path))
        elif build_system == 'gradle':
            dependencies.extend(self._extract_gradle_dependencies(project_path))
        elif build_system == 'cargo':
            dependencies.extend(self._extract_cargo_dependencies(project_path))
        elif build_system == 'go':
            dependencies.extend(self._extract_go_dependencies(project_path))
        elif build_system == 'cmake':
            dependencies.extend(self._extract_cmake_dependencies(project_path))
        elif build_system == 'makefile':
            dependencies.extend(self._extract_makefile_dependencies(project_path))
        
        return dependencies
    
    def _extract_python_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Extract Python dependencies from various files."""
        dependencies = []
        
        # Check requirements.txt
        req_file = project_path / 'requirements.txt'
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Parse version specifiers
                            match = re.match(r'^([a-zA-Z0-9\-_.]+)([><=!~]+.*)?$', line)
                            if match:
                                name, version_spec = match.groups()
                                dependencies.append({
                                    'name': name,
                                    'version_spec': version_spec or '',
                                    'type': 'python',
                                    'source': 'requirements.txt'
                                })
            except Exception as e:
                logger.warning(f"Could not read requirements.txt: {e}")
        
        # Check setup.py
        setup_file = project_path / 'setup.py'
        if setup_file.exists():
            try:
                with open(setup_file, 'r') as f:
                    content = f.read()
                    # Extract install_requires
                    match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
                    if match:
                        reqs_str = match.group(1)
                        # Parse individual requirements
                        for req in re.findall(r'[\'\"](.*?)[\'\"]', reqs_str):
                            req = req.strip()
                            if req:
                                match = re.match(r'^([a-zA-Z0-9\-_.]+)([><=!~]+.*)?$', req)
                                if match:
                                    name, version_spec = match.groups()
                                    dependencies.append({
                                        'name': name,
                                        'version_spec': version_spec or '',
                                        'type': 'python',
                                        'source': 'setup.py'
                                    })
            except Exception as e:
                logger.warning(f"Could not parse setup.py: {e}")
        
        # Check pyproject.toml
        pyproject_file = project_path / 'pyproject.toml'
        if pyproject_file.exists():
            try:
                with open(pyproject_file, 'r') as f:
                    content = f.read()
                    # Extract dependencies from [project.dependencies]
                    match = re.search(r'\[project\.dependencies\](.*?)(?=\[|$)', content, re.DOTALL)
                    if match:
                        deps_section = match.group(1)
                        for dep in re.findall(r'[\'\"](.*?)[\'\"]', deps_section):
                            dep = dep.strip()
                            if dep:
                                match = re.match(r'^([a-zA-Z0-9\-_.]+)([><=!~]+.*)?$', dep)
                                if match:
                                    name, version_spec = match.groups()
                                    dependencies.append({
                                        'name': name,
                                        'version_spec': version_spec or '',
                                        'type': 'python',
                                        'source': 'pyproject.toml'
                                    })
            except Exception as e:
                logger.warning(f"Could not parse pyproject.toml: {e}")
        
        return dependencies
    
    def _extract_npm_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Extract NPM dependencies from package.json."""
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
                                'type': 'npm',
                                'source': 'package.json'
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
                                'type': 'npm-dev',
                                'source': 'package.json'
                            })
            except Exception as e:
                logger.warning(f"Could not parse package.json: {e}")
        
        return dependencies
    
    def _extract_maven_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Extract Maven dependencies from pom.xml."""
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
                            
                            if group_id and artifact_id:
                                dependencies.append({
                                    'name': f"{group_id.group(1)}:{artifact_id.group(1)}",
                                    'version_spec': version.group(1) if version else '',
                                    'type': 'maven',
                                    'source': 'pom.xml'
                                })
            except Exception as e:
                logger.warning(f"Could not parse pom.xml: {e}")
        
        return dependencies
    
    def _extract_gradle_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Extract Gradle dependencies from build.gradle files."""
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
                            'type': 'gradle',
                            'source': gradle_file.name
                        })
                    
                    # Extract api dependencies
                    for match in re.finditer(r'api\s+[\'"](.*?)[\'"]', content):
                        dependencies.append({
                            'name': match.group(1),
                            'version_spec': '',
                            'type': 'gradle-api',
                            'source': gradle_file.name
                        })
            except Exception as e:
                logger.warning(f"Could not parse {gradle_file}: {e}")
        
        return dependencies
    
    def _extract_cargo_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Extract Cargo dependencies from Cargo.toml."""
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
                                'type': 'cargo',
                                'source': 'Cargo.toml'
                            })
            except Exception as e:
                logger.warning(f"Could not parse Cargo.toml: {e}")
        
        return dependencies
    
    def _extract_go_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Extract Go dependencies from go.mod."""
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
                            'type': 'go',
                            'source': 'go.mod'
                        })
            except Exception as e:
                logger.warning(f"Could not parse go.mod: {e}")
        
        return dependencies
    
    def _extract_cmake_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Extract CMake dependencies from CMakeLists.txt."""
        dependencies = []
        
        cmake_file = project_path / 'CMakeLists.txt'
        if cmake_file.exists():
            try:
                with open(cmake_file, 'r') as f:
                    content = f.read()
                    # Extract find_package calls
                    for match in re.finditer(r'find_package\s*\(\s*([^\s]+)', content):
                        dependencies.append({
                            'name': match.group(1),
                            'version_spec': '',
                            'type': 'cmake',
                            'source': 'CMakeLists.txt'
                        })
                    
                    # Extract include directories
                    for match in re.finditer(r'include_directories\s*\(\s*([^\s\)]+)', content):
                        dependencies.append({
                            'name': match.group(1),
                            'version_spec': '',
                            'type': 'cmake-include',
                            'source': 'CMakeLists.txt'
                        })
            except Exception as e:
                logger.warning(f"Could not parse CMakeLists.txt: {e}")
        
        return dependencies
    
    def _extract_makefile_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Extract Makefile dependencies."""
        dependencies = []
        
        for makefile in project_path.glob('*akefile*'):
            try:
                with open(makefile, 'r') as f:
                    content = f.read()
                    # Extract include statements
                    for match in re.finditer(r'include\s+([^\s]+)', content):
                        dependencies.append({
                            'name': match.group(1),
                            'version_spec': '',
                            'type': 'makefile-include',
                            'source': makefile.name
                        })
                    
                    # Extract library dependencies
                    for match in re.finditer(r'-l([^\s]+)', content):
                        dependencies.append({
                            'name': match.group(1),
                            'version_spec': '',
                            'type': 'makefile-lib',
                            'source': makefile.name
                        })
            except Exception as e:
                logger.warning(f"Could not parse {makefile}: {e}")
        
        return dependencies
    
    def _get_build_commands(self, build_system: str) -> List[str]:
        """Get common build commands for a build system."""
        commands = {
            'makefile': ['make', 'make clean', 'make install'],
            'cmake': ['mkdir build && cd build && cmake ..', 'cd build && make', 'cd build && make install'],
            'meson': ['meson setup build', 'meson compile -C build', 'meson install -C build'],
            'ninja': ['ninja', 'ninja clean'],
            'autotools': ['./configure', 'make', 'make install'],
            'scons': ['scons', 'scons -c'],
            'bazel': ['bazel build', 'bazel test'],
            'gradle': ['./gradlew build', './gradlew test', './gradlew clean'],
            'maven': ['mvn compile', 'mvn test', 'mvn clean'],
            'npm': ['npm install', 'npm run build', 'npm test'],
            'pip': ['pip install -r requirements.txt', 'pip install -e .', 'python setup.py build'],
            'cargo': ['cargo build', 'cargo test', 'cargo check'],
            'go': ['go build', 'go test', 'go mod tidy'],
            'dotnet': ['dotnet build', 'dotnet test', 'dotnet clean']
        }
        
        return commands.get(build_system, [])
    
    def get_supported_build_systems(self) -> Dict[str, str]:
        """Get list of supported build systems."""
        return {name: info['description'] for name, info in self.BUILD_SYSTEMS.items()}
    
    def is_build_system_supported(self, build_system: str) -> bool:
        """Check if a build system is supported."""
        return build_system in self.BUILD_SYSTEMS
