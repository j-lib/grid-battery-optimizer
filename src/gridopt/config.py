"""Load project settings from a YAML file."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "default.yaml"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Read a YAML config. Falls back to config/default.yaml."""
    path = Path(path) if path else DEFAULT_CONFIG
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
