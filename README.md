# PRJ-1 Project Browser

A comprehensive project management application that scans, browses, and manages development projects with advanced version detection, multilingual support, and complete documentation system.

## ✨ Key Features

### 📁 Advanced Project Scanner

- **Flexible Directory Selection**: Choose any directory to scan for projects
- **Recursive Scanning**: Automatically searches all subdirectories for projects
- **Advanced Version Detection**: Extracts version information from `version.py` files
- **Metadata Extraction**: Extracts comprehensive project information including:
  - Project name and path
  - Programming language detection
  - Version extraction from version.py files with semantic versioning support
  - Project size and modification date
  - Git repository detection
  - README and requirements file detection
- **Directory Persistence**: Remembers last used directory for convenience

### 🔍 Intelligent Project Browser

- **Interactive Interface**: Browse projects with a user-friendly dialog
- **Search & Filter**: Search by project name/description and filter by language
- **Project Details**: View comprehensive project information including version details
- **Quick Actions**: Open project folder, terminal, or editor directly
- **Background Scanning**: Non-blocking project scanning for better UX
- **Version Display**: Shows project versions with semantic versioning format
- **Directory Navigation**: Easy navigation through project directories

### 🌍 Complete Multilingual System

- **Multi-language Support**: Full support for English and Italian with runtime switching
- **Dynamic Translation**: Language can be changed on-the-fly
- **Localized UI**: All interface elements are translated
- **Translation Parameter Propagation**: Consistent language support across all modules
- **Centralized Translation Keys**: All UI strings use get_text() with proper language parameter

### 🎨 Professional User Interface

- **Custom Title Bar**: Professional title bar with window control buttons
- **Window Management**: Minimize, maximize/restore, and close functionality
- **Dark Theme**: Consistent dark theme across entire interface
- **Responsive Design**: Adaptive layout with proper margins and spacing
- **Interactive Controls**: Hover effects and tooltips for better UX
- **Error-Free Interface**: Robust error handling prevents crashes and display issues
- **Graceful Degradation**: Handles missing or incomplete project data gracefully

### 📚 Comprehensive Documentation System

- **User Guide**: Complete installation, usage, and troubleshooting guide
- **API Documentation**: Technical reference for developers
- **Contributing Guide**: Development workflow and contribution guidelines
- **Code of Conduct**: Community guidelines and standards
- **Prerequisites**: System requirements and setup instructions
- **Documentation Index**: Centralized documentation hub with role-based navigation
- **Project Structure**: Detailed project organization and file purposes
- **Security Policy**: Comprehensive security features and vulnerability reporting
- **Development Roadmap**: Current status and future plans

### 🛠️ Advanced Tools & Features

- **Log Viewer**: Browse and filter application logs
- **Update Checker**: Check for application updates with GitHub integration
- **About Dialog**: Application information and credits
- **Sponsor Dialog**: Support the project developer
- **Comprehensive Help System**: Integrated documentation with real-time file loading
- **Enhanced Version Management**: Advanced version parsing and display functionality
- **Project Tagging System**: Add custom tags to projects for better organization
- **Project Categories**: Organize projects into custom categories
- **Project Notes**: Add personal notes and descriptions to projects
- **Favorite Projects**: Mark frequently used projects as favorites
- **Recent Projects**: Track and display recently accessed projects
- **Git Integration**: Enhanced Git repository management and status tracking
- **Build System Integration**: Support for various build systems
- **Dependency Management**: Track and manage project dependencies
- **Automated Backups**: Automatic backup of project data and configurations
- **Export/Import**: Export project data to various formats (CSV, JSON, XML)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Nsfr750/PRJ-1.git
cd PRJ-1
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Run the application:

```bash
python main.py
```

## Recent Updates & Bug Fixes

### Version 0.1.5 (2025-09-16)

#### 📚 Complete Documentation System

- **Comprehensive Documentation**: Added complete documentation system with user guide, API docs, contributing guide, and more
- **User Guide**: Complete installation, usage, and troubleshooting documentation
- **API Documentation**: Technical reference for developers with detailed endpoints and usage
- **Contributing Guide**: Development workflow and contribution guidelines
- **Code of Conduct**: Community guidelines and standards
- **Prerequisites**: System requirements and setup instructions
- **Documentation Index**: Centralized documentation hub with role-based navigation
- **Project Structure**: Detailed project organization and file purposes
- **Security Policy**: Enhanced security documentation with vulnerability reporting
- **Development Roadmap**: Updated roadmap with current status and future plans

#### 🌍 Enhanced Translation System

- **Complete Translation System Integration**: Added multilingual support for dashboard module with centralized translation keys
- **Enhanced Multilingual Support**: Updated all dashboard UI components to support runtime language switching
- **Fixed Translation Parameter Issues**: Resolved missing language parameters in dashboard translation calls
- **Improved Error Messages**: Enhanced user feedback messages with proper translation support
- **Dynamic Language Support**: All dialogs (About, Sponsor, Help) now support dynamic language changes

#### 🔧 Security & Performance

- **Enhanced Security Documentation**: Updated security policy with latest features and best practices
- **Automated Backups**: Automatic backup of project data and configurations
- **Git Integration**: Enhanced Git repository management and status tracking
- **Export/Import**: Export project data to various formats (CSV, JSON, XML)

### Version 0.1.3 (2025-09-15)

- **Fixed KeyError: 'language' errors**: Enhanced error handling for missing project data with safe dictionary access
- **Fixed NoneType object is not subscriptable errors**: Improved null checking in project selection and favorite management
- **Enhanced robustness**: Added default values for all project fields to prevent display errors
- **Improved UI stability**: Enhanced robustness of UI updates when no project is selected
- **Better error handling**: Comprehensive error prevention throughout the application

## Dependencies

- **PySide6** - GUI framework
- **requests** - HTTP requests for update checking
- **packaging** - Package version parsing
- **qrcode** - QR code generation
- **Wand** - Image processing (ImageMagick binding)

## Project Structure

```markdown
PRJ-1/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── CHANGELOG.md                # Version history and changes
├── TO_DO.md                    # Project tasks and roadmap
├── LICENSE                     # GPLv3 license
├── .gitignore                  # Git ignore rules
├── .gitattributes              # Git attributes
├── .github/                    # GitHub configuration
│   ├── CODEOWNERS             # Code ownership rules
│   └── FUNDING.yml            # Funding configuration
├── data/                       # Persistent data storage
│   ├── projects.json           # Scanned project data
│   ├── categories.json         # Project categories
│   ├── favorites.json          # Favorite projects
│   ├── dependency_cache.json   # Dependency cache
│   ├── dependency_stats.json   # Dependency statistics
│   └── recent_projects.json    # Recent projects data
├── script/                     # Application modules
│   ├── __init__.py             # Package initialization
│   ├── project_scanner.py      # Project scanning logic
│   ├── ui/                     # User interface components
│   │   ├── __init__.py         # Package initialization
│   │   ├── menu.py             # Application menu
│   │   ├── project_browser.py  # Project browser dialog
│   │   ├── about.py            # About dialog
│   │   ├── help.py             # Help dialog
│   │   ├── sponsor.py          # Sponsor dialog
│   │   ├── view_log.py         # Log viewer
│   │   ├── advanced_search.py  # Advanced search functionality
│   │   ├── dashboard.py        # Main dashboard
│   │   └── settings.py         # Settings management
│   ├── lang/                   # Language management
│   │   ├── __init__.py         # Package initialization
│   │   ├── lang_mgr.py         # Language manager
│   │   └── translations.py     # Translation strings
│   ├── utils/                  # Utility modules
│   │   ├── __init__.py         # Package initialization
│   │   ├── logger.py           # Logging configuration
│   │   ├── settings.py         # Settings management
│   │   ├── updates.py          # Update checking
│   │   └── version.py          # Version information
│   ├── menu.py                 # Menu system
│   ├── help.py                 # Help system
│   ├── sponsor.py              # Sponsor system
│   ├── logger.py               # Logging system
│   ├── update.py               # Update system
│   └── version.py              # Version management
├── assets/                     # Application assets
│   ├── icon.ico                # Application icon
│   ├── logo.png                # Application logo
│   ├── main.png                # Main application image
│   └── background.png          # Background images
├── config/                     # Configuration files
│   ├── settings.json           # Application settings
│   ├── updates.json            # Update configuration
│   └── version.json            # Version configuration
├── docs/                       # Documentation
│   ├── User_Guide.md           # User guide
│   ├── API.md                  # API documentation
│   ├── CONTRIBUTING.md         # Contributing guide
│   ├── CODE_OF_CONDUCT.md      # Code of conduct
│   ├── PREREQUISITES.md        # Prerequisites
│   ├── INDEX.md                # Documentation index
│   ├── STRUCT.md               # Project structure
│   ├── SECURITY.md             # Security policy
│   └── ROADMAP.md              # Development roadmap
├── logs/                       # Application logs
│   ├── prj_*.log               # Application logs
│   └── prj_errors_*.log        # Error logs
└── backups/                    # Backup files
    └── backup_config.json      # Backup configuration
```

## Usage

### Starting the Application

Run `python main.py` to launch the application. The main window will appear with a menu bar and comprehensive user interface.

### Key Features & Usage

#### 📁 Project Management

1. **Project Browser**: Go to **Tools → Project Browser** in the menu
2. **Directory Selection**: Choose the directory you want to scan for projects
3. **Recursive Scan**: The browser will automatically scan the selected directory and all subdirectories
4. **Search & Filter**: Use the search box to filter projects by name or description
5. **Language Filter**: Use the language dropdown to filter by programming language
6. **View Details**: Click on any project to view detailed information including version
7. **Quick Actions**: Use the action buttons to:
   - **Open Folder**: Open the project directory in file explorer
   - **Open Terminal**: Open a terminal in the project directory
   - **Open in Editor**: Open the project in your default editor

#### 🏷️ Project Organization

- **Project Categories**: Organize projects into custom categories (Web, Desktop, Mobile, Library, etc.)
- **Project Tags**: Add custom tags to projects for better organization
- **Project Notes**: Add personal notes and descriptions to projects
- **Favorite Projects**: Mark frequently used projects as favorites
- **Recent Projects**: Track and display recently accessed projects

#### 🌍 Language Support

- **Dynamic Language Switching**: Change language on-the-fly from the menu
- **Complete Translation**: All interface elements support English and Italian
- **Consistent Experience**: All dialogs and UI components update immediately

#### 📚 Documentation Access

- **Integrated Help System**: Access comprehensive documentation from the Help menu
- **Role-Based Documentation**: Different documentation for users, developers, and contributors
- **Real-Time Updates**: Documentation loads dynamically and stays current

#### 🔧 Advanced Tools

- **Log Viewer**: Browse and filter application logs for debugging
- **Update Checker**: Check for application updates with GitHub integration
- **Settings Management**: Configure application preferences and behavior
- **Backup System**: Automated backup of project data and configurations
- **Export/Import**: Export project data to various formats (CSV, JSON, XML)

### Managing Projects

- **Refresh**: Click the refresh button to rescan for new projects
- **Change Directory**: Use the directory selection button to scan a different location
- **Clear Data**: Use the clear button to remove saved project data
- **Statistics**: View project statistics in the browser sidebar
- **Version Info**: View detailed version information for each project
- **Git Integration**: View Git repository status and information

## Configuration

### Directory Selection

The application allows flexible directory selection:

- **Interactive Selection**: Use the directory dialog in the Project Browser
- **Directory Persistence**: The last used directory is automatically saved and restored
- **Recursive Scanning**: All subdirectories are automatically scanned
- **Multiple Locations**: Easily switch between different project directories

### Version Detection

Projects are detected by looking for `version.py` files:

- **Required Format**: `__version__ = "x.y.z"` (semantic versioning)
- **Optional**: `VERSION = (x, y, z)` tuple for programmatic access
- **Metadata**: Additional fields like author, description, license are supported
- **Recursive Search**: Version.py files are searched in all subdirectories

### Data Storage

Project data is stored in the `data/` directory with multiple JSON files:

- **projects.json**: List of all scanned projects with metadata
- **categories.json**: Project categories and organization
- **favorites.json**: Favorite projects configuration
- **dependency_cache.json**: Cached dependency information
- **dependency_stats.json**: Dependency statistics
- **recent_projects.json**: Recently accessed projects

### Settings Management

Application settings are stored in `config/settings.json`:

- **Language Preference**: Selected language (English/Italian)
- **Directory History**: Last used directories
- **Window Settings**: Window size and position
- **UI Preferences**: Theme and display options
- **Update Settings**: Automatic update checking configuration

### Backup System

Automated backup system in `backups/` directory:

- **Automatic Backups**: Regular backups of project data and configurations
- **Backup Configuration**: Customizable backup settings and schedules
- **Restore Functionality**: Restore from previous backups when needed

## Development

### Getting Started

1. **Fork and Clone**:

   ```bash
   git clone https://github.com/Nsfr750/PRJ-1.git
   cd PRJ-1
   pip install -r requirements.txt
   ```

2. **Set Up Development Environment**:
   - Install Python 3.8+
   - Install required dependencies from `requirements.txt`
   - Review the development guidelines in `docs/CONTRIBUTING.md`
   - Check the prerequisites in `docs/PREREQUISITES.md`

### Adding New Features

1. **Create New Modules**: Create new modules in the appropriate subdirectory under `script/`
2. **Follow Patterns**: Follow the existing code structure and patterns
3. **Add Translations**: Add translations to `script/lang/translations.py` with proper language parameters
4. **Update Menu**: Update the menu in `script/ui/menu.py` if needed
5. **Add Dependencies**: Add dependencies to `requirements.txt`
6. **Update Documentation**: Update relevant documentation files in `docs/`
7. **Add Tests**: Add unit tests for new functionality

### Code Standards

- **Code Style**: Follow PEP 8 guidelines (using Black formatter)
- **Type Hints**: Use type hints where appropriate
- **Docstrings**: Add docstrings to all public methods and functions
- **Logging**: Use the existing logging system in `script/utils/logger.py`
- **Translation**: Use the translation system with proper language parameter propagation
- **Error Handling**: Implement comprehensive error handling

### Translation System

The project uses a comprehensive translation system:

- **Language Manager**: `script/lang/lang_mgr.py` handles language switching
- **Translation Keys**: `script/lang/translations.py` contains all translation strings
- **Parameter Passing**: Always pass language parameter to `get_text()` function
- **Dynamic Updates**: All UI components support runtime language changes
- **Consistent Pattern**: Use `retranslate_ui()` and `set_language()` methods in dialogs

### Testing

- **Unit Tests**: Use pytest for unit testing (see `tests/` directory)
- **Integration Tests**: Test UI components and user interactions
- **Translation Tests**: Verify all translations work correctly
- **Error Handling**: Test error scenarios and edge cases

### Documentation

Maintain comprehensive documentation:

- **User Documentation**: Update `docs/User_Guide.md` for user-facing changes
- **API Documentation**: Update `docs/API.md` for API changes
- **Development Docs**: Update `docs/CONTRIBUTING.md` for development guidelines
- **Project Structure**: Update `docs/STRUCT.md` for structural changes
- **Security**: Update `docs/SECURITY.md` for security-related changes
- **Roadmap**: Update `docs/ROADMAP.md` for planning changes

### Git Workflow

1. **Create Feature Branch**: `git checkout -b feature/your-feature-name`
2. **Make Changes**: Implement your feature following the coding standards
3. **Test Thoroughly**: Ensure all tests pass and functionality works
4. **Update Documentation**: Update relevant documentation files
5. **Commit Changes**: `git commit -m "feat: add your feature description"`
6. **Push Branch**: `git push origin feature/your-feature-name`
7. **Create Pull Request**: Submit a PR with detailed description
8. **Code Review**: Address review feedback and make necessary changes

## License

This project is licensed under GPLv3. See the license file for details.

## Author

### Nsfr750

- Email: [Nsfr750](mailto:nsfr750@yandex.com)
- GitHub: [https://github.com/Nsfr750](https://github.com/Nsfr750)
- Discord: [https://discord.gg/ryqNeuRYjD](https://discord.gg/ryqNeuRYjD)

## Support

If you find this project useful, please consider supporting the developer:

- **GitHub Sponsors**: [https://github.com/sponsors/Nsfr750](https://github.com/sponsors/Nsfr750)
- **Patreon**: [https://www.patreon.com/Nsfr750](https://www.patreon.com/Nsfr750)
- **PayPal**: [https://paypal.me/3dmega](https://paypal.me/3dmega)
- **Monero**: `47Jc6MC47WJVFhiQFYwHyBNQP5BEsjUPG6tc8R37FwcTY8K5Y3LvFzveSXoGiaDQSxDrnCUBJ5WBj6Fgmsfix8VPD4w3gXF`

## Changelog

See `CHANGELOG.md` for detailed version history.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Issues

Report bugs or request features on the GitHub Issues page.

---

© Copyright 2025 Nsfr750 - All rights reserved.
