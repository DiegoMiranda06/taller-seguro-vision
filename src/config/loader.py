"""Loads and validates a station's JSON config into a `StationConfig`."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from src.config.schema import StationConfig


class ConfigError(Exception):
    """Raised when a station config file is missing or fails validation."""


def load_station_config(path: str | Path) -> StationConfig:
    """Read the JSON file at `path` and validate it into a `StationConfig`.

    Raises `ConfigError` if the file doesn't exist, isn't valid JSON, or
    doesn't match the schema — callers (e.g. app.py) should let this
    propagate as a fatal startup error rather than run with a bad config.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Station config not found: {config_path}")

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {config_path}: {exc}") from exc

    try:
        return StationConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(f"Invalid station config in {config_path}:\n{exc}") from exc
