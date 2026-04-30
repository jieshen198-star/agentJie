from __future__ import annotations

import re


def sanitize_filename(value: str) -> str:
    value = value.strip().replace(" ", "_")
    value = re.sub(r"[^a-zA-Z0-9_.-]", "", value)
    return value.lower()
