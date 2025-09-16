# PRJ-1 Project Structure Documentation

This document provides a detailed explanation of the PRJ-1 project structure, including the purpose of each directory and file, and how they interact with each other.

## Overview

PRJ-1 is organized into a modular structure that separates concerns and promotes maintainability. The project follows Python best practices and uses a clear directory hierarchy.

## Current Version: 0.1.5

The current version (0.1.5) includes comprehensive translation system integration for the dashboard module, providing full multilingual support with runtime language switching capabilities across all UI components.

## Root Directory Structure

```text
PRJ-1/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── CHANGELOG.md                # Version history
├── TO_DO.md                    # Task management
├── LICENSE                     # GPL v3.0 license
├── INFO.txt                    # Project information
├── nuitka_compiler.py          # Standalone executable compiler
├── main.spec                   # Nuitka build specification
├── .gitattributes              # Git configuration
├── .gitignore                  # Git ignore rules
├── data/                       # Persistent data storage
│   ├── projects.json           # Scanned project data
│   ├── categories.json         # Project categories
│   ├── favorites.json          # Favorite projects
│   ├── notes.json              # Project notes
│   ├── tags.json               # Project tags
│   ├── recent.json             # Recent projects
│   ├── dependency_cache.json   # Dependency cache
│   ├── dependency_stats.json   # Dependency statistics
│   ├── settings.json           # Application settings
│   └── updates.json            # Update information
├── config/                     # Configuration files
│   ├── settings.json           # User settings
│   ├── updates.json            # Update configuration
│   └── version.json            # Version tracking
├── script/                     # Application modules
│   ├── __init__.py             # Package initialization
│   ├── project_scanner.py      # Project scanning logic
│   ├── menu.py                 # Application menu
│   ├── help.py                 # Help system
│   ├── sponsor.py              # Sponsor dialog
│   ├── view_log.py             # Log viewer
│   ├── update.py               # Update system
│   ├── logger.py               # Logging system
│   ├── settings.py             # Settings management
│   ├── ui/                     # User interface components
│   │   ├── __init__.py         # UI package initialization
│   │   ├── menu.py             # Application menu
│   │   ├── project_browser.py  # Main project browser dialog
│   │   ├── about.py            # About dialog
│   │   ├── help.py             # Help dialog
│   │   ├── sponsor.py          # Sponsor dialog
│   │   ├── view_log.py         # Log viewer
│   │   ├── advanced_search.py  # Advanced search dialog
│   │   └── dashboard.py        # Project statistics dashboard
│   ├── lang/                   # Language management
│   │   ├── __init__.py         # Language package initialization
│   │   ├── lang_mgr.py         # Language manager
│   │   └── translations.py     # Translation strings
│   └── utils/                  # Utility modules
│       ├── __init__.py         # Utils package initialization
│       ├── logger.py           # Logging configuration
│       ├── settings.py         # Settings management
│       ├── updates.py          # Update checking
│       └── version.py          # Version information
├── assets/                     # Application assets
│   ├── icon.ico                # Application icon
│   ├── logo.png                # Application logo
│   ├── main.png                # Main application image
│   └── background.png          # Background images
├── docs/                       # Documentation
│   ├── User_Guide.md           # User guide
│   ├── API.md                  # API documentation
│   ├── CONTRIBUTING.md         # Contributing guide
│   ├── CODE_OF_CONDUCT.md      # Code of conduct
│   ├── PREREQUISITES.md        # Prerequisites
│   ├── INDEX.md                # Documentation index
│   ├── STRUCT.md               # This structure documentation
│   ├── ROADMAP.md              # Development roadmap
│   ├── SECURITY.md             # Security policy
│   └── app_list.md             # Application list
├── logs/                       # Application logs
│   ├── prj_2025-09-15.log      # Application log
│   ├── prj_2025-09-16.log      # Application log
│   ├── prj_errors_2025-09-15.log # Error log
│   └── prj_errors_2025-09-16.log # Error log
├── backups/                    # Backup files
│   └── backup_config.json      # Configuration backup
├── dist/                       # Distribution files
├── venv/                       # Virtual environment
└── .github/                    # GitHub configuration
    ├── CODEOWNERS              # Code ownership rules
    └── FUNDING.yml             # Funding configuration
```

### Root Files

#### `main.py`

- **Purpose**: Application entry point and main window setup
- **Responsibilities**:
  - Initialize the Qt application
  - Create the main window
  - Set up the menu system
  - Handle application lifecycle events
- **Dependencies**: PySide6, script modules

#### `requirements.txt`

- **Purpose**: Python package dependencies specification
- **Contents**: Package names and versions for pip installation
- **Key Dependencies**: PySide6, requests, packaging, qrcode, Wand

#### `README.md`

- **Purpose**: Project documentation and usage instructions
- **Contents**: Installation instructions, usage guide, feature descriptions, and project information

#### `CHANGELOG.md`

- **Purpose**: Version history and change tracking
- **Format**: Follows Keep a Changelog format with Semantic Versioning

#### `INFO.txt`

- **Purpose**: Basic project information and metadata
- **Contents**: Project name, version, description, and other identifying information

#### `.gitattributes`

- **Purpose**: Git configuration for file handling
- **Contents**: Settings for line endings, file types, and other Git behaviors

## Directory Structure Details

### `data/` - Persistent Data Storage

```text
data/
└── projects.json          # Scanned project data
```

#### `projects.json`

- **Purpose**: Persistent storage for scanned project data
- **Contents**: JSON-formatted project information including:
  - Project metadata (name, path, language, version)
  - Scan timestamps
  - Project statistics
- **Format**: JSON array of project objects
- **Auto-generated**: Created and updated by the ProjectScanner

### `script/` - Application Modules

```text
script/
├── __init__.py            # Package initialization
├── project_scanner.py     # Project scanning logic
├── ui/                    # User interface components
├── lang/                  # Language management
└── utils/                 # Utility modules
```

#### Core Script Files

**`__init__.py`**

- **Purpose**: Python package initialization
- **Contents**: Package metadata and imports

**`project_scanner.py`**

- **Purpose**: Core project scanning and data management
- **Key Classes**: `ProjectScanner`
- **Responsibilities**:
  - Scan GitHub folder for projects
  - Extract project metadata
  - Save/load project data
  - Language detection
  - Version extraction
  - Git repository detection
- **Dependencies**: pathlib, json, os, datetime

### `script/ui/` - User Interface Components

```text
script/ui/
├── __init__.py            # UI package initialization
├── menu.py                # Application menu
├── project_browser.py     # Project browser dialog
├── about.py               # About dialog
├── help.py                # Help dialog
├── sponsor.py             # Sponsor dialog
└── view_log.py            # Log viewer dialog
```

#### UI Components

**`menu.py`**

- **Purpose**: Application menu bar and menu actions
- **Key Classes**: `MainMenu`
- **Responsibilities**:
  - Create menu bar structure
  - Handle menu actions
  - Connect to dialog windows
  - Manage application-wide actions

**`project_browser.py`**

- **Purpose**: Main project browsing interface
- **Key Classes**: `ProjectBrowserDialog`
- **Responsibilities**:
  - Display project list
  - Handle search and filtering
  - Show project details
  - Manage project actions (open folder, terminal, editor)
  - Coordinate with ProjectScanner

**`about.py`**

- **Purpose**: About dialog with application information
- **Key Classes**: `AboutDialog`
- **Responsibilities**:
  - Display application version and information
  - Show author and contact details
  - Display license information

**`help.py`**

- **Purpose**: Help dialog with usage instructions
- **Key Classes**: `HelpDialog`
- **Responsibilities**:
  - Display help content
  - Provide usage instructions
  - Show feature descriptions

**`sponsor.py`**

- **Purpose**: Sponsor dialog for developer support
- **Key Classes**: `SponsorDialog`
- **Responsibilities**:
  - Display sponsorship options
  - Show QR codes for payment
  - Provide support links

**`view_log.py`**

- **Purpose**: Log viewer for application logs
- **Key Classes**: `LogViewerDialog`
- **Responsibilities**:
  - Display log files
  - Provide log filtering
  - Handle log file navigation

### `script/lang/` - Language Management

```text
script/lang/
├── __init__.py            # Language package initialization
├── lang_mgr.py            # Language manager
└── translations.py        # Translation strings
```

#### Language Components

**`lang_mgr.py`**

- **Purpose**: Language management and switching
- **Key Classes**: `LanguageManager`
- **Responsibilities**:
  - Manage available languages
  - Handle language switching
  - Provide translation lookup
  - Store current language preference

**`translations.py`**

- **Purpose**: Translation string definitions
- **Contents**: Dictionary of translations for all UI text
- **Languages**: English and Italian
- **Structure**: Nested dictionaries organized by UI component

### `script/utils/` - Utility Modules

```text
script/utils/
├── __init__.py            # Utils package initialization
├── logger.py              # Logging configuration
├── updates.py             # Update checking
└── version.py             # Version information
```

#### Utility Components

**`logger.py`**

- **Purpose**: Application logging configuration
- **Key Classes**: `AppLogger`
- **Responsibilities**:
  - Set up logging configuration
  - Create log files
  - Handle log rotation
  - Provide logging utilities

**`updates.py`**

- **Purpose**: Application update checking
- **Key Classes**: `UpdateChecker`
- **Responsibilities**:
  - Check for application updates
  - Compare version numbers
  - Handle update notifications
  - Manage update downloads

**`version.py`**

- **Purpose**: Version information management
- **Contents**: Version constants and version-related functions
- **Responsibilities**:
  - Define current version
  - Provide version comparison utilities
  - Handle version formatting

### `assets/` - Static Assets

```text
assets/
├── icon.ico               # Application icon
└── logo.png               # Application logo
```

#### Asset Files

**`icon.ico`**

- **Purpose**: Application icon for window and taskbar
- **Format**: Windows ICO format with multiple sizes
- **Usage**: Set as window icon in main application

**`logo.png`**

- **Purpose**: Application logo for dialogs and about screen
- **Format**: PNG format
- **Usage**: Displayed in about dialog and other UI elements

### `config/` - Configuration Files

```text
config/
```

#### Configuration Purpose

- **Storage**: Application configuration files
- **Contents**: Currently empty, reserved for future configuration needs
- **Planned Use**: User preferences, settings, and configuration data

### `docs/` - Documentation

```text
docs/
├── User_Guide.md           # User guide and manual
├── API.md                  # API documentation
├── CONTRIBUTING.md         # Contributing guidelines
├── CODE_OF_CONDUCT.md      # Code of conduct
├── PREREQUISITES.md        # System prerequisites
├── INDEX.md                # Documentation index
├── STRUCT.md               # This structure documentation
├── ROADMAP.md              # Development roadmap
├── SECURITY.md             # Security policy
└── app_list.md             # Application list
```

#### Documentation Files

**`User_Guide.md`**

- **Purpose**: Complete user manual and usage instructions
- **Contents**: Installation guide, feature overview, tutorials, troubleshooting
- **Audience**: End users and new contributors

**`API.md`**

- **Purpose**: Technical API reference for developers
- **Contents**: Core classes, UI components, utility modules, data structures
- **Audience**: Developers and contributors

**`CONTRIBUTING.md`**

- **Purpose**: Contribution guidelines and development workflow
- **Contents**: Development setup, code standards, pull request process, testing
- **Audience**: Contributors and developers

**`CODE_OF_CONDUCT.md`**

- **Purpose**: Community guidelines and code of conduct
- **Contents**: Community pledge, standards of behavior, enforcement guidelines
- **Audience**: All community members

**`PREREQUISITES.md`**

- **Purpose**: System requirements and setup instructions
- **Contents**: System requirements, software dependencies, installation steps
- **Audience**: Users and developers setting up the environment

**`INDEX.md`**

- **Purpose**: Documentation hub and navigation guide
- **Contents**: Overview of all documentation, quick navigation by role
- **Audience**: All users seeking documentation

**`STRUCT.md`**

- **Purpose**: Project structure documentation
- **Contents**: Detailed explanation of project organization and file purposes
- **Audience**: Developers and maintainers

**`ROADMAP.md`**

- **Purpose**: Development roadmap and future plans
- **Contents**: Planned features, release timeline, project vision
- **Audience**: Contributors and stakeholders

**`SECURITY.md`**

- **Purpose**: Security policy and vulnerability reporting
- **Contents**: Security guidelines, vulnerability reporting process
- **Audience**: Security researchers and contributors

**`app_list.md`**

- **Purpose**: List of applications and tools
- **Contents**: Application inventory with descriptions
- **Audience**: Users and developers

## Data Flow Architecture

### Project Scanning Flow

1. **User Action** → `main.py` → `ProjectBrowserDialog`

2. **Scan Request** → `ProjectScanner.scan_projects()`

3. **File System Scan** → Extract project metadata

4. **Data Storage** → Save to `data/projects.json`

5. **UI Update** → Refresh project list display

### Language Management Flow

1. **Language Selection** → `LanguageManager`

2. **Translation Lookup** → `translations.py`

3. **UI Update** → Update all UI text elements

4. **Preference Storage** → Save language preference

### Logging Flow

1. **Log Event** → `AppLogger`

2. **Log Processing** → Format and timestamp

3. **File Storage** → Write to `logs/` directory

4. **Log Viewing** → `LogViewerDialog` for display

## Module Dependencies

### Core Dependencies

```python
main.py
├── script.ui.menu
├── script.lang.lang_mgr
├── script.utils.logger
└── script.utils.version
```

### UI Dependencies

```python
script.ui.project_browser
├── script.project_scanner
├── script.lang.lang_mgr
└── script.utils.logger
```

### Scanner Dependencies

```python
script.project_scanner
├── script.utils.logger
└── script.utils.version
```

### Language Dependencies

```text
script.lang.lang_mgr
└── script.lang.translations
```

## Extension Points

### Adding New UI Components

1. Create new file in `script/ui/`

2. Inherit from appropriate Qt base class

3. Add translations to `script/lang/translations.py`

4. Add menu item in `script/ui/menu.py`

### Adding New Utilities

1. Create new file in `script/utils/`

2. Implement utility functions/classes

3. Add logging as needed

4. Import and use in other modules

### Adding New Languages

1. Add translations to `script/lang/translations.py`

2. Update `script/lang/lang_mgr.py` if needed

3. Test all UI components with new language

## Best Practices

### File Organization

- Keep related functionality together

- Use clear, descriptive file names

- Follow Python package structure

- Separate UI logic from business logic

### Code Structure

- Use classes for major components

- Implement proper error handling

- Add comprehensive docstrings

- Follow PEP 8 style guidelines

### Data Management

- Use JSON for configuration and data storage

- Implement proper file handling with error checking

- Provide data validation and sanitization

- Include backup and recovery mechanisms

### UI Development

- Use Qt Designer for complex layouts when possible

- Implement responsive design principles

- Provide keyboard shortcuts for common actions

- Ensure accessibility compliance

---

This structure documentation provides a comprehensive overview of the PRJ-1 project organization. For specific implementation details, refer to the individual file documentation and code comments.

© Copyright 2025 Nsfr750 - All rights reserved
