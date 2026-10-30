"""Build script for creating a Windows executable using PyInstaller.

Usage (run from project root)::

    python build_installer.py

The script invokes ``pyinstaller`` to create a single‑file executable named
``PantherApp.exe`` from the package entry point ``src/panther/main.py``.  After a
successful build it places the executable in ``dist/`` and prints the path.
"""

import subprocess
import sys
from pathlib import Path

def main() -> None:
    project_root = Path(__file__).resolve().parent
    entry_point = project_root / "src" / "panther" / "main.py"
    if not entry_point.is_file():
        sys.exit(f"Entry point not found: {entry_point}")

    # Run PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        "PantherApp",
        str(entry_point),
    ]
    print("Running PyInstaller …")
    result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"PyInstaller failed:\n{result.stdout}\n{result.stderr}")

    exe_path = project_root / "dist" / "PantherApp.exe"
    if exe_path.is_file():
        print(f"✅ Installer built: {exe_path}")
    else:
        sys.exit("Executable not found after build")

if __name__ == "__main__":
    main()
