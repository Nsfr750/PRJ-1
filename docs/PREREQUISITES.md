# Prerequisites

This document outlines the system requirements and dependencies needed to run and develop PRJ-1.

## Table of Contents
- [System Requirements](#system-requirements)
- [Software Dependencies](#software-dependencies)
- [Python Requirements](#python-requirements)
- [Development Dependencies](#development-dependencies)
- [Optional Dependencies](#optional-dependencies)
- [Installation Instructions](#installation-instructions)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 or later, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 500 MB free space for installation
- **Processor**: 64-bit processor with at least 2 cores

### Recommended Requirements
- **Operating System**: Windows 11, macOS 12+, or Linux (Ubuntu 22.04+)
- **RAM**: 16 GB or more
- **Storage**: 1 GB free space for installation and data
- **Processor**: 64-bit processor with 4+ cores
- **Graphics**: GPU with OpenGL 3.3+ support for better UI rendering

## Software Dependencies

### Required Software
- **Python 3.8+**: Core programming language
- **Git**: Version control system
- **Virtual Environment Tool**: venv (built-in) or conda

### Optional Software
- **Visual Studio Code**: Recommended IDE for development
- **PyCharm**: Alternative IDE with excellent Python support
- **Git GUI**: SourceTree, GitKraken, or similar (optional)
- **Image Editor**: For modifying assets (GIMP, Photoshop, etc.)

## Python Requirements

### Core Dependencies
The following Python packages are required for PRJ-1 to function:

```txt
PySide6>=6.2.0
```

### Development Dependencies
For development and testing, additional packages are recommended:

```txt
# Code formatting and linting
black>=22.0.0
isort>=5.10.0
flake8>=4.0.0
pylint>=2.12.0

# Testing
pytest>=7.0.0
pytest-cov>=3.0.0
pytest-mock>=3.6.0

# Documentation
sphinx>=4.5.0
sphinx-rtd-theme>=1.0.0

# Development tools
pre-commit>=2.17.0
mypy>=0.910
```

### Version Compatibility
| PRJ-1 Version | Python Version | PySide6 Version |
|---------------|----------------|-----------------|
| 0.1.x         | 3.8+          | 6.2.0+         |
| 0.2.x         | 3.9+          | 6.3.0+         |
| 1.0.x         | 3.10+         | 6.4.0+         |

## Installation Instructions

### Step 1: Install Python
#### Windows
1. Download Python from [python.org](https://python.org)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### macOS
1. Install Homebrew (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```bash
   brew install python
   ```
3. Verify installation:
   ```bash
   python3 --version
   pip3 --version
   ```

#### Linux (Ubuntu/Debian)
1. Update package list:
   ```bash
   sudo apt update
   ```
2. Install Python:
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```
3. Verify installation:
   ```bash
   python3 --version
   pip3 --version
   ```

### Step 2: Install Git
#### Windows
1. Download Git from [git-scm.com](https://git-scm.com)
2. Run the installer with default settings
3. Verify installation:
   ```cmd
   git --version
   ```

#### macOS
```bash
brew install git
```

#### Linux
```bash
sudo apt install git
```

### Step 3: Clone the Repository
```bash
git clone https://github.com/Nsfr750/PRJ-1.git
cd PRJ-1
```

### Step 4: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 5: Install Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

## Verification

### Verify Python Environment
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check PySide6 installation
python -c "import PySide6; print('PySide6 version:', PySide6.__version__)"
```

### Verify Application Startup
```bash
# Run the application
python main.py
```

The application should start successfully and display the main window with the centered dialog.

### Verify Development Setup
```bash
# Run tests (if development dependencies are installed)
pytest

# Check code formatting
black --check .

# Check import sorting
isort --check-only .
```

## Troubleshooting

### Common Issues

#### Python Not Found in PATH
**Symptoms**: `python: command not found`

**Solution**:
1. **Windows**: Reinstall Python and ensure "Add Python to PATH" is checked
2. **macOS/Linux**: Use `python3` instead of `python`, or create an alias:
   ```bash
   alias python=python3
   alias pip=pip3
   ```

#### PySide6 Installation Issues
**Symptoms**: Import errors, missing Qt libraries

**Solutions**:
1. **Clean reinstall**:
   ```bash
   pip uninstall PySide6
   pip install --no-cache-dir PySide6
   ```

2. **Install specific version**:
   ```bash
   pip install PySide6==6.2.0
   ```

3. **Check system compatibility**:
   - Ensure your system meets the minimum requirements
   - Update graphics drivers
   - Check for conflicting Qt installations

#### Virtual Environment Issues
**Symptoms**: Activation fails, packages not found

**Solutions**:
1. **Recreate virtual environment**:
   ```bash
   # Remove old environment
   rm -rf venv
   
   # Create new environment
   python -m venv venv
   
   # Activate and reinstall
   source venv/bin/activate  # or venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Check activation**:
   ```bash
   # Verify virtual environment is active
   which python  # macOS/Linux
   where python  # Windows
   ```

#### Permission Issues
**Symptoms**: Permission denied errors during installation

**Solutions**:
1. **Use virtual environment** (recommended)
2. **User-specific installation**:
   ```bash
   pip install --user PySide6
   ```
3. **Administrator privileges** (last resort):
   ```bash
   sudo pip install PySide6  # macOS/Linux
   # Run as Administrator on Windows
   ```

#### Display Issues
**Symptoms**: Application doesn't show, GUI errors

**Solutions**:
1. **Check display environment** (Linux):
   ```bash
   echo $DISPLAY
   export DISPLAY=:0
   ```

2. **Run with verbose output**:
   ```bash
   python main.py --verbose
   ```

3. **Check graphics drivers**:
   - Update GPU drivers
   - Try software rendering if available

#### Memory Issues
**Symptoms**: Application crashes, out of memory errors

**Solutions**:
1. **Increase system memory**
2. **Close other applications**
3. **Check for memory leaks**:
   ```bash
   # Monitor memory usage
   python -m memory_profiler main.py
   ```

### Platform-Specific Issues

#### Windows
- **DLL Errors**: Install Microsoft Visual C++ Redistributable
- **UAC Issues**: Run application as administrator if needed
- **Antivirus**: Add application to antivirus exceptions

#### macOS
- **Gatekeeper**: Allow application from unidentified developer
- **Xcode Command Line Tools**: Install if missing:
  ```bash
  xcode-select --install
  ```

#### Linux
- **Missing system packages**: Install required system libraries:
  ```bash
  # Ubuntu/Debian
  sudo apt install libgl1-mesa-glx libxcb-cursor0
  
  # Fedora
  sudo dnf install mesa-libGL libxcb-cursor
  
  # Arch
  sudo pacman -S mesa libxcb-cursor
  ```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Look in the `logs/` directory for error messages
2. **Search existing issues**: Check GitHub issues for similar problems
3. **Create a new issue**: Provide detailed information about your system and the error
4. **Join the community**: Get help on Discord or other community channels

---

© Copyright 2025 Nsfr750 - All rights reserved
