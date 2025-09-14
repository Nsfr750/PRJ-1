# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2025-09-15

### Added (0.1.3)

- Custom title bar with window control buttons (minimize, maximize/restore, close)
- Window state management with maximize/restore toggle functionality
- Enhanced UI styling with consistent dark theme across title bar and main interface
- Improved window layout with proper margins and spacing
- Interactive window control buttons with hover effects and tooltips
- Responsive title bar design that adapts to window state changes

### Changed (0.1.3)

- Restructured main layout to accommodate custom title bar
- Updated window flags to support custom title bar functionality
- Enhanced styling system with title bar specific CSS rules
- Improved layout management with content widget separation
- Updated button styling for window controls with consistent theme

### Fixed (0.1.3)

- Fixed KeyError: 'language' errors in project details display
- Fixed NoneType object is not subscriptable errors in project selection
- Enhanced error handling for missing project data with safe dictionary access
- Improved null checking in project selection and favorite management
- Added default values for all project fields to prevent display errors
- Enhanced robustness of UI updates when no project is selected

## [0.1.2] - 2025-09-14

### Added (0.1.2)

- Enhanced version.py with comprehensive functionality and metadata support
- Directory selection functionality for flexible project scanning
- Directory path persistence (save/load last used directory)
- Recursive version scanning in all subdirectories
- Comprehensive documentation system with docs/ folder integration
- Enhanced help system with real documentation file loading
- Advanced project metadata extraction including version information
- Improved logging system with better configuration
- Enhanced update checking system with proper PRJ-1 branding

### Changed (0.1.2)

- Updated help.py content from Neural Network Creator to PRJ-1 Project Browser
- Fixed import paths in updates.py to use correct script.version module
- Enhanced ProjectScanner with recursive directory scanning
- Improved user interface with better directory selection
- Updated all documentation to reflect PRJ-1 functionality
- Enhanced error handling and logging throughout the application
- Improved version detection and parsing from version.py files

### Fixed (0.1.2)

- Fixed version import issues in updates.py
- Corrected application branding in help and update systems
- Improved directory scanning performance and reliability
- Enhanced error handling for file operations
- Fixed various UI layout and styling issues

## [0.1.0] - 2025-09-14

### Added (0.1.0)

- Project Scanner with automatic detection of projects in GitHub folder
- Project Browser with search and filter functionality
- Data persistence system with automatic save/load to data/projects.json
- Multi-language support (English and Italian)
- Log Viewer for browsing application logs
- Update Checker for application updates
- About Dialog with application information
- Sponsor Dialog for supporting the developer
- Comprehensive README.md documentation

### Changed (0.1.0)

- Improved user interface with better organization
- Enhanced project metadata extraction including language detection, version extraction, and git repository detection
- Added background scanning for better user experience

### Fixed (0.1.0)

- Fixed various UI layout issues
- Improved error handling and logging

## [0.0.1] - 2025-09-14

### Added (0.0.1)

- Initial release of PRJ-1 Project Manager
- Basic project scanning functionality
- Simple project browser interface
- Multi-language support framework
- Basic logging system
- Menu system with tools and help options

### Key Features (0.0.1)

- Scan X:\GitHub folder for projects
- Extract basic project information (name, path, language)
- Simple project browsing with basic filtering
- English and Italian language support
- Basic logging for debugging and monitoring

---

© Copyright 2025 Nsfr750 - All rights reserved
