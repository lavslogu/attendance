from __future__ import annotations

from datetime import datetime
from pathlib import Path
from threading import Lock


class TechnicalLogger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = Lock()

    def log(self, event: str, details: str = "") -> None:
        line = f"{datetime.now().astimezone().isoformat(timespec='seconds')}\t{event}\t{details}\n"
        with self.lock, self.path.open("a", encoding="utf-8") as stream:
            stream.write(line)
