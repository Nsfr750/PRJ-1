#!/usr/bin/env python3
"""
Nuitka Compiler Script for PRJ-1 Project Browser
This script compiles the PRJ-1 application into standalone executables using Nuitka.
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
import argparse

# Import version information
try:
    from script.utils.version import __version__
except ImportError:
    __version__ = "0.1.2"  # Fallback version


class NuitkaCompiler:
    """Handles Nuitka compilation for PRJ-1 Project Browser."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.main_script = self.project_root / "main.py"
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.icon_path = self.project_root / "assets" / "icon.ico"
        
        # Platform-specific settings
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        
        # Nuitka command base
        self.nuitka_cmd = ["python", "-m", "nuitka"]
        
        # Common Nuitka options
        self.common_options = [
            "--standalone",
            "--onefile",
            "--follow-imports",
            "--include-package=PySide6",
            "--include-package=script",
            "--plugin-enable=pyside6",
            "--windows-disable-console" if self.is_windows else "",
            "--output-dir=" + str(self.dist_dir),
            "--remove-output",
        ]
        
        # Remove empty strings from options
        self.common_options = [opt for opt in self.common_options if opt]
        
    def check_dependencies(self):
        """Check if required dependencies are installed."""
        print("Checking dependencies...")
        
        # Check if Nuitka is installed
        try:
            subprocess.run([sys.executable, "-c", "import nuitka"], 
                         check=True, capture_output=True)
            print("✓ Nuitka is installed")
        except subprocess.CalledProcessError:
            print("❌ Nuitka is not installed. Please install it:")
            print("pip install nuitka")
            return False
        
        # Check if project files exist
        if not self.main_script.exists():
            print(f"❌ Main script not found: {self.main_script}")
            return False
            
        if not self.icon_path.exists():
            print(f"⚠️  Icon file not found: {self.icon_path}")
            self.icon_path = None
        
        print("✓ All dependencies checked")
        return True
    
    def get_data_files(self):
        """Get list of data files to include in the compilation."""
        data_files = []
        
        # Include assets directory
        assets_dir = self.project_root / "assets"
        if assets_dir.exists():
            for asset_file in assets_dir.rglob("*"):
                if asset_file.is_file():
                    rel_path = asset_file.relative_to(self.project_root)
                    data_files.append(f"--include-data-files={asset_file}={rel_path}")
        
        # Include config directory
        config_dir = self.project_root / "config"
        if config_dir.exists():
            for config_file in config_dir.rglob("*"):
                if config_file.is_file():
                    rel_path = config_file.relative_to(self.project_root)
                    data_files.append(f"--include-data-files={config_file}={rel_path}")
        
        return data_files
    
    def get_platform_specific_options(self):
        """Get platform-specific compilation options."""
        options = []
        
        if self.is_windows:
            # Windows-specific options
            options.extend([
                "--windows-icon-from-ico=" + str(self.icon_path) if self.icon_path else "",
                '--windows-console-mode=disable',
                "--output-filename=PRJ-1",
                "--company-name=Tuxxle",
                "--product-name=PRJ-1",
                f"--file-version={__version__}.0",
                f"--product-version={__version__}.0",
                "--file-description=Project Browser",
                "--copyright=© Copyright 2025 Nsfr750 - All rights reserved",
                "--mingw64",  # Download MinGW64 automatically for compilation
            ])
        elif self.is_macos:
            # macOS-specific options
            options.extend([
                "--macos-create-app-bundle",
                "--macos-app-icon=" + str(self.icon_path) if self.icon_path else "",
            ])
        elif self.is_linux:
            # Linux-specific options
            options.extend([
                "--linux-icon=" + str(self.icon_path) if self.icon_path else "",
            ])
        
        # Remove empty strings
        return [opt for opt in options if opt]
    
    def build_command(self, debug=False, profile=False):
        """Build the Nuitka compilation command."""
        cmd = self.nuitka_cmd.copy()
        cmd.extend(self.common_options)
        cmd.extend(self.get_platform_specific_options())
        cmd.extend(self.get_data_files())
        
        # Add debug options if requested
        if debug:
            cmd.extend([
                "--debug",
                "--no-remove-output",
                "--python-debug",
            ])
        
        # Add profiling options if requested
        if profile:
            cmd.extend([
                "--profile",
            ])
        
        # Add main script
        cmd.append(str(self.main_script))
        
        return cmd
    
    def clean_build_dirs(self):
        """Clean previous build directories."""
        print("Cleaning previous build directories...")
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print("✓ Removed build directory")
        
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            print("✓ Removed dist directory")
    
    def compile(self, debug=False, profile=False, clean=True):
        """Compile the application using Nuitka."""
        print("Starting Nuitka compilation for PRJ-1 Project Browser...")
        print(f"Platform: {platform.system()}")
        print(f"Python version: {sys.version}")
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Clean build directories if requested
        if clean:
            self.clean_build_dirs()
        
        # Create directories
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
        # Build command
        cmd = self.build_command(debug, profile)
        
        print(f"Compilation command: {' '.join(cmd)}")
        print("Starting compilation...")
        
        try:
            # Run Nuitka
            result = subprocess.run(cmd, check=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✓ Compilation completed successfully!")
                
                # Find the compiled executable
                executable_name = "main.exe" if self.is_windows else "main.bin"
                if self.is_macos:
                    # On macOS, check for app bundle
                    app_bundle = self.dist_dir / "main.app"
                    if app_bundle.exists():
                        print(f"✓ Executable created: {app_bundle}")
                        return True
                
                executable_path = self.dist_dir / executable_name
                if executable_path.exists():
                    print(f"✓ Executable created: {executable_path}")
                    return True
                else:
                    print("❌ Executable not found in dist directory")
                    return False
            else:
                print("❌ Compilation failed")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Compilation failed with error: {e}")
            return False
        except KeyboardInterrupt:
            print("❌ Compilation interrupted by user")
            return False
    
    def create_installer(self):
        """Create a simple installer script."""
        print("Creating installer script...")
        
        installer_script = self.dist_dir / "install.py"
        installer_content = '''#!/usr/bin/env python3
"""
Simple installer script for PRJ-1 Project Browser
"""

import os
import sys
import shutil
from pathlib import Path

def install_prj1():
    """Install PRJ-1 Project Browser."""
    print("Installing PRJ-1 Project Browser...")
    
    # Get installation directory
    if len(sys.argv) > 1:
        install_dir = Path(sys.argv[1])
    else:
        # Default installation directory
        if sys.platform == "win32":
            install_dir = Path(os.path.expanduser("~/AppData/Local/PRJ-1"))
        elif sys.platform == "darwin":
            install_dir = Path(os.path.expanduser("~/Applications/PRJ-1"))
        else:
            install_dir = Path(os.path.expanduser("~/.local/bin/PRJ-1"))
    
    # Create installation directory
    install_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executable
    source_dir = Path(__file__).parent
    executable_name = "main.exe" if sys.platform == "win32" else "main.bin"
    
    if sys.platform == "darwin":
        # Handle macOS app bundle
        app_bundle = source_dir / "main.app"
        if app_bundle.exists():
            dest_app = install_dir / "PRJ-1.app"
            if dest_app.exists():
                shutil.rmtree(dest_app)
            shutil.copytree(app_bundle, dest_app)
            print(f"✓ Installed app bundle: {dest_app}")
            return True
    
    executable = source_dir / executable_name
    if executable.exists():
        dest_executable = install_dir / executable_name
        shutil.copy2(executable, dest_executable)
        print(f"✓ Installed executable: {dest_executable}")
        
        # Make executable on Unix systems
        if sys.platform != "win32":
            dest_executable.chmod(0o755)
        
        return True
    else:
        print("❌ Executable not found")
        return False

if __name__ == "__main__":
    if install_prj1():
        print("✓ Installation completed successfully!")
    else:
        print("❌ Installation failed")
        sys.exit(1)
'''
        
        with open(installer_script, 'w', encoding='utf-8') as f:
            f.write(installer_content)
        
        # Make installer executable on Unix systems
        if not self.is_windows:
            installer_script.chmod(0o755)
        
        print(f"✓ Installer script created: {installer_script}")
        return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Compile PRJ-1 Project Browser using Nuitka")
    parser.add_argument("--debug", action="store_true", help="Build debug version")
    parser.add_argument("--profile", action="store_true", help="Build with profiling")
    parser.add_argument("--no-clean", action="store_true", help="Don't clean build directories")
    parser.add_argument("--installer", action="store_true", help="Create installer script")
    parser.add_argument("--check-only", action="store_true", help="Only check dependencies")
    
    args = parser.parse_args()
    
    compiler = NuitkaCompiler()
    
    if args.check_only:
        success = compiler.check_dependencies()
        sys.exit(0 if success else 1)
    
    # Compile the application
    success = compiler.compile(
        debug=args.debug,
        profile=args.profile,
        clean=not args.no_clean
    )
    
    if success and args.installer:
        compiler.create_installer()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
