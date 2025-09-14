# Project Browser

A comprehensive project management application that scans, browses, and manages development projects with advanced version detection and directory selection capabilities.

## Features

### 📁 Project Scanner

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

### 🔍 Project Browser

- **Interactive Interface**: Browse projects with a user-friendly dialog
- **Search & Filter**: Search by project name/description and filter by language
- **Project Details**: View comprehensive project information including version details
- **Quick Actions**: Open project folder, terminal, or editor directly
- **Background Scanning**: Non-blocking project scanning for better UX
- **Version Display**: Shows project versions with semantic versioning format
- **Directory Navigation**: Easy navigation through project directories

### 💾 Data Persistence

- **Automatic Save**: Project data is automatically saved to the `data/` folder
- **Fast Loading**: Previously scanned projects load instantly on startup
- **JSON Format**: Human-readable data storage in `data/projects.json`

### 🌍 Multi-language Support

- **Bilingual Interface**: Full support for English and Italian
- **Dynamic Translation**: Language can be changed on-the-fly
- **Localized UI**: All interface elements are translated

### 🎨 User Interface

- **Custom Title Bar**: Professional title bar with window control buttons
- **Window Management**: Minimize, maximize/restore, and close functionality
- **Dark Theme**: Consistent dark theme across entire interface
- **Responsive Design**: Adaptive layout with proper margins and spacing
- **Interactive Controls**: Hover effects and tooltips for better UX
- **Error-Free Interface**: Robust error handling prevents crashes and display issues
- **Graceful Degradation**: Handles missing or incomplete project data gracefully

### 🛠️ Additional Tools

- **Log Viewer**: Browse and filter application logs
- **Update Checker**: Check for application updates with GitHub integration
- **About Dialog**: Application information and credits
- **Sponsor Dialog**: Support the project developer
- **Comprehensive Help System**: Integrated documentation with real-time file loading
- **Enhanced Version Management**: Advanced version parsing and display functionality

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

## Recent Bug Fixes

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
├── data/                       # Persistent data storage
│   └── projects.json           # Scanned project data
├── script/                     # Application modules
│   ├── project_scanner.py      # Project scanning logic
│   ├── ui/                     # User interface components
│   │   ├── menu.py             # Application menu
│   │   ├── project_browser.py  # Project browser dialog
│   │   ├── about.py            # About dialog
│   │   ├── help.py             # Help dialog
│   │   ├── sponsor.py          # Sponsor dialog
│   │   └── view_log.py         # Log viewer
│   ├── lang/                   # Language management
│   │   ├── lang_mgr.py         # Language manager
│   │   └── translations.py     # Translation strings
│   └── utils/                  # Utility modules
│       ├── logger.py           # Logging configuration
│       ├── updates.py          # Update checking
│       └── version.py          # Version information
├── assets/                     # Application assets
├── config/                     # Configuration files
├── docs/                       # Documentation
└── logs/                       # Application logs
```

## Usage

### Starting the Application

Run `python main.py` to launch the application. The main window will appear with a menu bar.

### Using the Project Browser

1. Go to **Tools → Project Browser** in the menu
2. **Select Directory**: Choose the directory you want to scan for projects
3. **Recursive Scan**: The browser will automatically scan the selected directory and all subdirectories
4. **Search & Filter**: Use the search box to filter projects by name or description
5. **Language Filter**: Use the language dropdown to filter by programming language
6. **View Details**: Click on any project to view detailed information including version
7. **Quick Actions**: Use the action buttons to:
   - **Open Folder**: Open the project directory in file explorer
   - **Open Terminal**: Open a terminal in the project directory
   - **Open in Editor**: Open the project in your default editor

### Managing Projects

- **Refresh**: Click the refresh button to rescan for new projects
- **Change Directory**: Use the directory selection button to scan a different location
- **Clear Data**: Use the clear button to remove saved project data
- **Statistics**: View project statistics in the browser sidebar
- **Version Info**: View detailed version information for each project

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

Project data is stored in `data/projects.json` in JSON format. The file contains:

- List of all scanned projects with metadata
- Last scan timestamp
- Project statistics

## Development

### Adding New Features

1. Create new modules in the appropriate subdirectory under `script/`
2. Follow the existing code structure and patterns
3. Add translations to `script/lang/translations.py`
4. Update the menu in `script/ui/menu.py` if needed
5. Add dependencies to `requirements.txt`

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all public methods
- Use the existing logging system for debugging

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
