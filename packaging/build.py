#!/usr/bin/env python3
"""
Build script for YouTube Converter
Creates a standalone .exe file using PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Ensure console output can handle non-ASCII characters on Windows (cp1252).
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# Always operate from the project root (this script lives in packaging/).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

SPEC = "packaging/youtube_converter.spec"


def print_header(text):
    """Print a formatted header."""
    print()
    print("=" * 60)
    print(text)
    print("=" * 60)
    print()


def print_step(step_num, total, text):
    """Print a formatted step."""
    print(f"[{step_num}/{total}] {text}")


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    if description:
        print(f"  -> {description}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return False


def check_pyinstaller():
    """Check if PyInstaller is installed, install if not."""
    try:
        import PyInstaller
        return True
    except ImportError:
        print("[WARNING] PyInstaller not found. Installing...")
        return run_command("pip install pyinstaller", "Installing PyInstaller")


def clean_build_dirs():
    """Remove old build directories."""
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  -> Removed {dir_name}/")


def get_file_size(filepath):
    """Get formatted file size."""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"


def main():
    """Main build process."""
    print_header("YouTube Converter - Build Script")

    # Step 1: Check PyInstaller
    print_step(1, 4, "Checking PyInstaller...")
    if not check_pyinstaller():
        print("[ERROR] Failed to install PyInstaller.")
        return 1
    print("[OK] PyInstaller ready.")

    # Step 2: Clean old builds
    print()
    print_step(2, 4, "Cleaning old builds...")
    clean_build_dirs()
    print("[OK] Cleanup complete.")

    # Step 3: Install dependencies
    print()
    print_step(3, 4, "Verifying dependencies...")
    if not run_command("pip install -r requirements.txt --quiet", "Installing requirements"):
        print("[WARNING] Some dependencies may not have installed correctly.")
    print("[OK] Dependencies verified.")

    # Step 4: Build with PyInstaller
    print()
    print_step(4, 4, "Building executable with PyInstaller...")
    print("  -> This may take a few minutes...")

    if not run_command(f"pyinstaller --clean --noconfirm {SPEC}", "Compiling"):
        print()
        print("[ERROR] Build failed.")
        return 1

    print("[OK] Build successful.")

    # Verify executable
    print()
    exe_path = Path("dist/YouTubeConverter.exe")
    if exe_path.exists():
        print_header("Build Complete!")
        print(f"Executable created: {exe_path}")
        print(f"File size: {get_file_size(exe_path)}")
        print()
        print("You can now run: dist\\YouTubeConverter.exe")
        print()
        return 0
    else:
        print("[ERROR] Executable was not created.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        input("\nPress Enter to exit...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Build interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
