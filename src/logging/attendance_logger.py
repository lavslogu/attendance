from __future__ import annotations

from datetime import datetime
from pathlib import Path
import cv2
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


class AttendanceLogger:
    def __init__(self, workbook_path: Path, captures_dir: Path) -> None:
        self.path, self.captures_dir = workbook_path, captures_dir
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.captures_dir.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            self.book = load_workbook(self.path)
            self.sheet = self.book.active
        else:
            self.book = Workbook()
            self.sheet = self.book.active
            self.sheet.title = "Attendance"
            self.sheet.append(["Captured face", "Name", "Status", "Date", "Time"])
            for cell in self.sheet[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="245A81")
            for col, width in {"A": 18, "B": 24, "C": 18, "D": 14, "E": 14}.items():
                self.sheet.column_dimensions[col].width = width
            self.sheet.freeze_panes = "A2"
            self.book.save(self.path)

    def record(self, frame, box: tuple[int, int, int, int], name: str | None) -> None:
        now = datetime.now()
        x1, y1, x2, y2 = box
        height, width = frame.shape[:2]
        pad = max(12, (x2 - x1) // 5)
        crop = frame[max(0, y1-pad):min(height, y2+pad), max(0, x1-pad):min(width, x2+pad)]
        stamp = now.strftime("%Y%m%d_%H%M%S_%f")
        image_path = self.captures_dir / f"{stamp}_{name or 'unregistered'}.jpg"
        cv2.imwrite(str(image_path), crop)
        row = self.sheet.max_row + 1
        self.sheet.cell(row, 1, str(image_path.relative_to(self.path.parent)))
        self.sheet.cell(row, 2, name or "User not registered")
        self.sheet.cell(row, 3, "Present" if name else "Unregistered")
        self.sheet.cell(row, 4, now.strftime("%Y-%m-%d"))
        self.sheet.cell(row, 5, now.strftime("%H:%M:%S"))
        try:
            picture = XLImage(str(image_path))
            picture.width, picture.height = 96, 72
            self.sheet.add_image(picture, f"A{row}")
            self.sheet.row_dimensions[row].height = 56
        except Exception as exc:
            print(f"Could not embed image in workbook: {exc}")
        self.book.save(self.path)
