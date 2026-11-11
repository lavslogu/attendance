from __future__ import annotations

import sys
import importlib.util
import logging as _stdlib_logging  # Load stdlib before src/logging is on sys.path.
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from face.recognizer import FaceRecognizer
from face.webcam import run_camera
from storage.technical_logger import TechnicalLogger

# The requested source folder is named ``logging``, which is also Python's
# standard library package. Load this project module by path to avoid collision.
_logger_spec = importlib.util.spec_from_file_location(
    "attendance_logger", ROOT / "src" / "logging" / "attendance_logger.py"
)
if _logger_spec is None or _logger_spec.loader is None:
    raise ImportError("Could not load src/logging/attendance_logger.py")
_logger_module = importlib.util.module_from_spec(_logger_spec)
_logger_spec.loader.exec_module(_logger_module)
AttendanceLogger = _logger_module.AttendanceLogger


def main() -> int:
    technical = TechnicalLogger(ROOT / "data" / "technical.log")
    technical.log("PROGRAM_START", f"Python {sys.version.split()[0]}")
    try:
        recognizer = FaceRecognizer(ROOT / "photos")
        attendance = AttendanceLogger(ROOT / "data" / "attendance.xlsx", ROOT / "data" / "captures")
        run_camera(recognizer, attendance, technical)
    except KeyboardInterrupt:
        print("\nAttendance stopped.")
    except Exception as exc:
        technical.log("ERROR", f"{type(exc).__name__}: {exc}")
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        technical.log("PROGRAM_STOP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
