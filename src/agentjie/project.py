from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from .tasks import Task


class ProjectWriter:
    def __init__(self, output_dir: str = "generated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_task_output(self, task: Task) -> str:
        filename = self._extract_filename(task.output) or task.filename or f"{task.id}.txt"
        content = self._extract_content(task.output) or task.output
        target_file = self.output_dir / filename
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(content, encoding="utf-8")
        return str(target_file)

    def _extract_filename(self, output: str) -> Optional[str]:
        for line in output.splitlines():
            if line.startswith("FILE:"):
                return line.split("FILE:", 1)[1].strip()
        return None

    def _extract_content(self, output: str) -> str:
        lines = output.splitlines()
        if lines and lines[0].startswith("FILE:"):
            return "\n".join(lines[1:]).lstrip("\n")
        return output
