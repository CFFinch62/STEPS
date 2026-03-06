from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CONTENT_DIR = Path(__file__).resolve().parents[2] / "content"


def _load_json(filename: str) -> list[dict[str, Any]]:
    path = CONTENT_DIR / filename
    return json.loads(path.read_text(encoding="utf-8"))


def load_examples() -> list[dict[str, Any]]:
    return _load_json("examples.json")


def load_tutorials() -> list[dict[str, Any]]:
    return _load_json("tutorials.json")