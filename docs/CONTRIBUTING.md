# Contributing to PRJ-1

Thank you for your interest in contributing to PRJ-1! This document provides guidelines and instructions for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Project Structure](#project-structure)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- Basic knowledge of Python and PySide6

### First Steps

1. **Fork the Repository**

   ```bash
   # Fork the repository on GitHub
   # Clone your fork locally
   git clone https://github.com/YOUR_USERNAME/PRJ-1.git
   cd PRJ-1
   ```

2. **Set Up Development Environment**

   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Set Up Git Configuration**

   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   
   # Add upstream remote
   git remote add upstream https://github.com/Nsfr750/PRJ-1.git
   ```

## Development Setup

### Branch Strategy

- **main**: Stable production code
- **develop**: Development branch
- **feature/***: Feature branches
- **bugfix/***: Bug fix branches
- **hotfix/***: Critical fixes

### Creating a Feature Branch

```bash
# Sync with upstream
git fetch upstream
git checkout develop
git merge upstream/develop

# Create feature branch
git checkout -b feature/your-feature-name
```

### Development Workflow

```bash
# Make your changes
# Test your changes
# Commit your changes
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name
```

## Code Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Maximum line length: 88 characters
- Use type hints where appropriate
- Write docstrings for all public methods and classes

### Code Formatting

```bash
# Format code with Black
black .

# Check formatting
black --check .

# Sort imports
isort .

# Lint code
flake8 .
pylint script/
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `MainWindow`, `ProjectScanner`)
- **Functions**: snake_case (e.g., `scan_projects`, `load_settings`)
- **Variables**: snake_case (e.g., `project_list`, `current_language`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`, `DEFAULT_LANGUAGE`)
- **Private members**: Leading underscore (e.g., `_private_method`)

### Docstring Format

Use Google-style docstrings:

```python
def scan_directory(self, directory_path: str) -> List[Dict[str, Any]]:
    """Scan a directory for projects.
    
    Args:
        directory_path: Path to directory to scan.
        
    Returns:
        List of discovered project dictionaries.
        
    Raises:
        FileNotFoundError: If directory doesn't exist.
        PermissionError: If directory cannot be accessed.
    """
```

### Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

**Examples:**
```
feat(project-browser): add advanced search functionality
fix(main-dialog): correct centering on window resize
docs(api): update ProjectScanner documentation
style: format code with Black
test(project-scanner): add unit tests for language detection
```

## Project Structure

```
PRJ-1/
├── main.py                 # Application entry point
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── README.md              # Project README
├── LICENSE                # License file
├── CHANGELOG.md           # Change log
├── TO_DO.md              # Task list
│
├── script/               # Application code
│   ├── ui/              # UI components
│   │   ├── main_dialog.py
│   │   ├── project_browser.py
│   │   ├── menu.py
│   │   ├── about.py
│   │   ├── sponsor.py
│   │   └── help.py
│   ├── lang/            # Language system
│   │   ├── lang_mgr.py
│   │   └── translations.py
│   ├── utils/           # Utility modules
│   │   ├── logger.py
│   │   ├── settings.py
│   │   └── version.py
│   ├── project_scanner.py
│   └── __init__.py
│
├── assets/              # Static assets
│   ├── background.png
│   ├── icon.ico
│   ├── logo.png
│   └── main.png
│
├── config/              # Configuration files
│   ├── settings.json
│   └── version.json
│
├── data/                # Data files
│   ├── projects.json
│   ├── tags.json
│   └── favorites.json
│
├── logs/                # Log files
├── docs/                # Documentation
└── tests/               # Test files
```

## Contributing Guidelines

### Before Contributing

1. **Check Existing Issues**: Search for existing issues or pull requests
2. **Discuss Changes**: Open an issue to discuss significant changes
3. **Start Small**: Begin with small, manageable contributions
4. **Follow Standards**: Adhere to the project's code standards

### What to Contribute

- **Bug Fixes**: Help fix reported issues
- **Features**: Add new functionality
- **Documentation**: Improve documentation
- **Tests**: Add or improve tests
- **Translations**: Add new language support
- **Performance**: Optimize code performance

### What Not to Contribute

- **Breaking Changes**: Without proper discussion
- **Large Refactoring**: Without approval
- **Dependencies**: Adding unnecessary dependencies
- **Code Style**: Deviating from established standards

## Pull Request Process

### Creating a Pull Request

1. **Update Your Branch**

   ```bash
   git fetch upstream
   git rebase upstream/develop
   ```

2. **Push Changes**

   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill in the PR template
   - Submit the PR

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] I have tested my changes
- [ ] I have added/updated tests as needed
- [ ] All tests pass

## Checklist
- [ ] My code follows the project's code style
- [ ] I have updated documentation as needed
- [ ] I have read the CONTRIBUTING.md document
- [ ] I have signed-off on my commits (DCO)
```

### Pull Request Review Process

1. **Automated Checks**: Code style, tests, and build checks
2. **Peer Review**: At least one maintainer review
3. **Feedback**: Address review comments
4. **Approval**: Final approval from maintainers
5. **Merge**: Merge into develop branch

### Sign-off Requirements

All commits must be signed off using the Developer Certificate of Origin (DCO):

```bash
git commit -s -m "feat: add your feature"
```

## Testing

### Test Framework

- **pytest**: Primary testing framework
- **pytest-cov**: Coverage reporting
- **unittest**: Built-in Python testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=script

# Run specific test file
pytest tests/test_project_scanner.py

# Run specific test
pytest tests/test_project_scanner.py::test_scan_directory
```

### Test Structure

```
tests/
├── __init__.py
├── test_project_scanner.py
├── test_main_dialog.py
├── test_settings.py
├── test_language_manager.py
└── conftest.py
```

### Writing Tests

```python
import pytest
from script.project_scanner import ProjectScanner

def test_scan_directory(tmp_path):
    """Test scanning a directory with projects."""
    # Setup
    scanner = ProjectScanner()
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()
    
    # Create test files
    (test_dir / "main.py").write_text("print('Hello')")
    
    # Test
    projects = scanner.scan_directory(str(test_dir))
    
    # Assert
    assert len(projects) == 1
    assert projects[0]["name"] == "test_project"
    assert projects[0]["language"] == "Python"
```

### Test Coverage

- Aim for 80%+ code coverage
- Add tests for new features
- Update tests for bug fixes
- Run tests before submitting PR

## Documentation

### Documentation Standards

- Use Markdown format
- Follow existing documentation style
- Include code examples
- Keep documentation up-to-date

### Documentation Files

- **User_Guide.md**: End-user documentation
- **API.md**: Technical API documentation
- **CONTRIBUTING.md**: Contributor guidelines
- **PREREQUISITES.md**: System requirements
- **INDEX.md**: Documentation index

### Updating Documentation

- Update documentation when adding features
- Include API documentation for new classes/methods
- Update user guide for user-facing changes
- Add examples for complex functionality

### Docstring Requirements

- All public classes and methods must have docstrings
- Include parameter types and descriptions
- Include return value descriptions
- Include exception information
- Provide usage examples for complex methods

## Reporting Issues

### Issue Template

```markdown
## Bug Description
A clear and concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
A clear and concise description of what actually happened.

## Screenshots
If applicable, add screenshots to help explain your problem.

## Environment
- OS: [e.g. Windows 10, Ubuntu 20.04]
- Python Version: [e.g. 3.9.0]
- PRJ-1 Version: [e.g. 0.1.5]
- PySide6 Version: [e.g. 6.2.0]

## Additional Context
Add any other context about the problem here.
```

### Issue Guidelines

- **Search First**: Check for existing issues
- **Be Specific**: Provide detailed information
- **Include Environment**: Specify your environment
- **Use Template**: Follow the issue template
- **One Issue Per Report**: Don't combine multiple issues

## Feature Requests

### Feature Request Template

```markdown
## Feature Description
A clear and concise description of the feature you'd like to see.

## Problem Statement

What problem would this feature solve?

## Proposed Solution

How do you envision this feature working?

## Alternatives Considered

What alternative solutions have you considered?

## Additional Context

Add any other context or screenshots about the feature request here.
```

### Feature Request Guidelines

- **Discuss First**: Open an issue to discuss before implementing
- **Provide Context**: Explain the use case and problem
- **Be Realistic**: Consider project scope and goals
- **Break Down**: Large features should be broken into smaller pieces

## Community Guidelines

### Communication

- Be respectful and constructive
- Focus on technical discussions
- Help newcomers and answer questions
- Share knowledge and experience

### Code of Conduct

- Follow the project's Code of Conduct
- Be inclusive and welcoming
- Respect different opinions and approaches
- Focus on collaboration and improvement

### Recognition

- Contributors will be recognized in the project documentation
- Significant contributors may be invited to become maintainers
- All contributions are valued and appreciated

---

Thank you for contributing to PRJ-1! Your help makes this project better for everyone.

© Copyright 2025 Nsfr750 - All rights reserved
