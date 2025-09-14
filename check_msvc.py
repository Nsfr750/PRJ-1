#!/usr/bin/env python3
"""
Check MSVC installation and provide compilation guidance for PRJ-1
"""

import os
import sys
import subprocess
from pathlib import Path

def check_msvc_installation():
    """Check if MSVC is installed and available."""
    print("🔍 Checking MSVC installation...")
    
    # Check common Visual Studio installation paths
    vs_paths = [
        r"C:\Program Files\Microsoft Visual Studio",
        r"C:\Program Files (x86)\Microsoft Visual Studio",
        r"C:\Program Files\Microsoft Visual C++ Build Tools",
    ]
    
    vs_found = False
    vs_versions = []
    
    for vs_path in vs_paths:
        if Path(vs_path).exists():
            print(f"✓ Found Visual Studio installation at: {vs_path}")
            vs_found = True
            # Check for specific versions
            for item in Path(vs_path).iterdir():
                if item.is_dir() and any(year in item.name for year in ["2022", "2019", "2017"]):
                    vs_versions.append(item.name)
    
    if vs_versions:
        print(f"✓ Available Visual Studio versions: {', '.join(vs_versions)}")
    
    # Check if cl.exe is available in PATH
    try:
        result = subprocess.run(['cl.exe', '/?'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ MSVC compiler (cl.exe) is available in PATH")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Check if cl.exe is in Visual Studio directories
    program_files = os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')
    program_files_x64 = os.environ.get('ProgramFiles', r'C:\Program Files')
    
    cl_paths = [
        rf"{program_files}\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\*\bin\Hostx64\x64\cl.exe",
        rf"{program_files}\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\*\bin\Hostx64\x64\cl.exe",
        rf"{program_files}\Microsoft Visual Studio\2022\Professional\VC\Tools\MSVC\*\bin\Hostx64\x64\cl.exe",
        rf"{program_files}\Microsoft Visual Studio\2022\Enterprise\VC\Tools\MSVC\*\bin\Hostx64\x64\cl.exe",
        rf"{program_files_x64}\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\*\bin\Hostx64\x64\cl.exe",
        rf"{program_files_x64}\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\*\bin\Hostx64\x64\cl.exe",
    ]
    
    import glob
    cl_found = False
    for cl_path in cl_paths:
        matches = glob.glob(cl_path)
        if matches:
            print(f"✓ Found cl.exe at: {matches[0]}")
            cl_found = True
            break
    
    if not cl_found:
        print("❌ MSVC compiler (cl.exe) not found")
    
    return vs_found or cl_found

def check_python_version():
    """Check Python version and provide recommendations."""
    print(f"\n🐍 Python version: {sys.version}")
    
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor == 13:
        print("⚠️  Python 3.13 detected - requires MSVC for compilation")
        return "3.13"
    elif python_version.major == 3 and python_version.minor == 12:
        print("✓ Python 3.12 detected - can use MinGW64 (recommended)")
        return "3.12"
    else:
        print(f"ℹ️  Python {python_version.major}.{python_version.minor} detected")
        return f"{python_version.major}.{python_version.minor}"

def provide_recommendations(python_version, msvc_available):
    """Provide compilation recommendations."""
    print("\n📋 Compilation Recommendations:")
    
    if python_version == "3.13":
        print("\n🔧 For Python 3.13:")
        if msvc_available:
            print("✓ MSVC is available - compilation should work")
            print("   Run: python nuitka_compiler.py")
        else:
            print("❌ MSVC not available - choose one of these options:")
            print("   1. Install Visual Studio Build Tools:")
            print("      https://visualstudio.microsoft.com/visual-cpp-build-tools/")
            print("   2. Install Visual Studio Community:")
            print("      https://visualstudio.microsoft.com/vs/community/")
            print("      (Select 'Desktop development with C++' workload)")
            print("   3. Use Python 3.12 instead:")
            print("      - Download Python 3.12 from python.org")
            print("      - Create new virtual environment with Python 3.12")
            print("      - Reinstall requirements")
    
    elif python_version == "3.12":
        print("\n🔧 For Python 3.12:")
        print("✓ Recommended: Use MinGW64 (automatic download)")
        print("   Run: python nuitka_compiler.py")
        print("   This will automatically download MinGW64 on first run")
    
    else:
        print(f"\n🔧 For Python {python_version}:")
        print("✓ Can use MinGW64 (automatic download)")
        print("   Run: python nuitka_compiler.py")

def main():
    """Main function."""
    print("🚀 PRJ-1 MSVC Installation Checker")
    print("=" * 40)
    
    python_version = check_python_version()
    msvc_available = check_msvc_installation()
    provide_recommendations(python_version, msvc_available)
    
    print("\n" + "=" * 40)
    print("💡 Additional Tips:")
    print("- If you have network issues, install Visual Studio Build Tools manually")
    print("- Python 3.12 + MinGW64 is the most reliable combination")
    print("- Ensure you have sufficient disk space for compilation (~500MB)")

if __name__ == "__main__":
    main()
