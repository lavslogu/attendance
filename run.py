"""Bootstrap dependencies on first run, then start the attendance app."""
from __future__ import annotations

import importlib.util
import logging as _stdlib_logging  # Protect stdlib from the project's src/logging folder.
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = {
    "insightface": "insightface",
    "onnxruntime": "onnxruntime",
    "cv2": "opencv-python",
    "numpy": "numpy",
    "openpyxl": "openpyxl",
    "PIL": "Pillow",
}


def main() -> int:
    missing = [package for module, package in REQUIRED.items()
               if importlib.util.find_spec(module) is None]
    if missing:
        print("Installing missing packages:", ", ".join(missing))
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])
        except subprocess.CalledProcessError:
            print("Dependency installation failed. Use Python 3.10–3.12 and see README.md.", file=sys.stderr)
            return 1
    sys.path.insert(0, str(ROOT / "src"))
    from attendance_app import main as app_main
    return app_main()


if __name__ == "__main__":
    raise SystemExit(main())
