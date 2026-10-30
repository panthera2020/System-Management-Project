# run_panther.py
import sys
import os
from pathlib import Path

# Ensure src is on sys.path for development and execution
src_path = str(Path(__file__).resolve().parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from panther.main import main

if __name__ == "__main__":
    sys.exit(main())
