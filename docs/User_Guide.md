# User Guide

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Main Features](#main-features)
- [Using the Project Browser](#using-the-project-browser)
- [Main Dialog](#main-dialog)
- [Settings and Configuration](#settings-and-configuration)
- [Language Support](#language-support)
- [Troubleshooting](#troubleshooting)

## Introduction

PRJ-1 is a comprehensive project browser application designed to help you manage and organize your development projects efficiently. Built with PySide6, it provides a user-friendly interface for browsing, categorizing, and analyzing your code projects.

## Installation

### Prerequisites

- Python 3.8 or higher
- PySide6 library
- Required Python packages (see `requirements.txt`)

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/Nsfr750/PRJ-1.git
   cd PRJ-1
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   python main.py
   ```

## Getting Started

When you first launch PRJ-1, you'll see:

- A main window with a background image

- A centered main dialog displaying the project logo

- A menu bar with various options

- A status bar at the bottom

The application will automatically scan your project directories and populate the project browser with discovered projects.

## Main Features

### Project Browser

- **Project Discovery**: Automatically scans directories for projects
- **Project Details**: Displays comprehensive information about each project
- **Categorization**: Organize projects by categories
- **Tagging System**: Add custom tags to projects
- **Favorites**: Mark frequently used projects as favorites
- **Advanced Search**: Find projects using various criteria

### Main Dialog

- **Transparent Overlay**: Displays a centered dialog over the main background
- **Dynamic Resizing**: Automatically follows main window resizing
- **Logo Display**: Shows the main project logo
- **ESC Key Support**: Close the dialog with the ESC key

### Language Support

- **Multi-language Interface**: Support for multiple languages
- **Dynamic Language Switching**: Change languages without restarting
- **Translation System**: Extensible translation framework

## Using the Project Browser

### Navigation

1. **Project List**: View all discovered projects in a table format
2. **Project Details**: Select a project to see detailed information
3. **Search**: Use the search functionality to find specific projects
4. **Filters**: Apply filters based on language, category, or tags

### Project Information

For each project, you can view:

- **Name**: Project name
- **Language**: Programming language detected
- **Version**: Project version (if available)
- **Size**: Project directory size
- **Modified**: Last modification date
- **Category**: Project category
- **Tags**: Associated tags
- **Notes**: Project notes

### Managing Projects

- **Scan for Projects**: Use the menu to scan specific directories
- **Refresh**: Update the project list
- **Add to Favorites**: Mark important projects
- **Edit Details**: Modify project information
- **Remove Projects**: Delete projects from the browser

## Main Dialog

The main dialog is a transparent overlay that appears when the application starts:

### Features

- **Centered Positioning**: Automatically centered over the main window
- **Transparent Background**: Maintains visibility of the main background
- **Dynamic Resizing**: Follows main window resizing automatically
- **Keyboard Control**: Press ESC to close the dialog

### Behavior

- The dialog appears automatically when the application starts
- It stays on top of other windows
- It can be closed and reopened through the menu
- It properly centers itself when the main window is resized

## Settings and Configuration

### Application Settings

- **Window Geometry**: Saves and restores window position and size
- **Language**: Preferred interface language
- **Scan Directories**: Directories to monitor for projects
- **Cache Settings**: Configure project data caching

### Configuration Files

- `config/settings.json`: Application settings
- `config/version.json`: Version information
- `data/projects.json`: Cached project data
- `data/tags.json`: Tag definitions
- `data/favorites.json`: Favorite projects

## Language Support

### Available Languages

- English (en)
- Italian (it)
- More languages can be added through the translation system

### Changing Language

1. Go to the menu bar
2. Select "Language" or "Lingua"
3. Choose your preferred language from the dropdown
4. The interface will update immediately

### Adding New Languages

1. Create translation files in the `lang/translations.py` module
2. Add language support to the language manager
3. Update the menu to include the new language

## Troubleshooting

### Common Issues

#### Application Won't Start

- **Problem**: Application crashes on startup
- **Solution**: Check if PySide6 is installed correctly
- **Command**: `pip install PySide6`

#### Projects Not Loading

- **Problem**: No projects appear in the browser
- **Solution**: 
  - Ensure scan directories are configured correctly
  - Check file permissions
  - Verify that project directories exist

#### Main Dialog Not Showing

- **Problem**: The main dialog doesn't appear
- **Solution**: 
  - Check if `assets/main.png` exists
  - Verify dialog initialization in `main.py`
  - Check for error messages in logs

#### Language Changes Not Applied

- **Problem**: Interface language doesn't change
- **Solution**: 
  - Verify translation files are complete
  - Check language manager configuration
  - Restart the application

### Log Files

The application creates log files in the `logs/` directory:
- `prj_YYYY-MM-DD.log`: General application logs
- `prj_errors_YYYY-MM-DD.log`: Error logs

### Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discord**: Join the community server for support
- **Documentation**: Check the `docs/` folder for detailed information

---

© Copyright 2025 Nsfr750 - All rights reserved
