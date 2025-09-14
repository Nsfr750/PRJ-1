# PRJ-1 - Project Manager

A comprehensive project management application that scans, browses, and manages projects in your GitHub folder.

## Features

### 📁 Project Scanner

- **Automatic Detection**: Scans the `X:\GitHub` folder for projects
- **Metadata Extraction**: Extracts project information including:
  - Project name and path
  - Programming language detection
  - Version extraction from common files
  - Project size and modification date
  - Git repository detection
  - README and requirements file detection

### 🔍 Project Browser

- **Interactive Interface**: Browse projects with a user-friendly dialog
- **Search & Filter**: Search by project name/description and filter by language
- **Project Details**: View comprehensive project information
- **Quick Actions**: Open project folder, terminal, or editor directly
- **Background Scanning**: Non-blocking project scanning for better UX

### 💾 Data Persistence

- **Automatic Save**: Project data is automatically saved to the `data/` folder
- **Fast Loading**: Previously scanned projects load instantly on startup
- **JSON Format**: Human-readable data storage in `data/projects.json`

### 🌍 Multi-language Support

- **Bilingual Interface**: Full support for English and Italian
- **Dynamic Translation**: Language can be changed on-the-fly
- **Localized UI**: All interface elements are translated

### 🛠️ Additional Tools

- **Log Viewer**: Browse and filter application logs
- **Update Checker**: Check for application updates
- **About Dialog**: Application information and credits
- **Sponsor Dialog**: Support the project developer

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
2. The browser will automatically scan your `X:\GitHub` folder
3. Use the search box to filter projects by name or description
4. Use the language dropdown to filter by programming language
5. Click on any project to view detailed information
6. Use the action buttons to:
   - **Open Folder**: Open the project directory in file explorer
   - **Open Terminal**: Open a terminal in the project directory
   - **Open in Editor**: Open the project in your default editor

### Managing Projects

- **Refresh**: Click the refresh button to rescan for new projects
- **Clear Data**: Use the clear button to remove saved project data
- **Statistics**: View project statistics in the browser sidebar

## Configuration

### GitHub Path

By default, the application scans `X:\GitHub`. You can modify this by:

- Editing the `github_path` parameter in `ProjectScanner` class
- Or modifying the scanner initialization in the project browser

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
