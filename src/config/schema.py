"""Pydantic schema for per-station configuration.

This is the ONLY source of variation between stations (Reglas No
Negociables #4 en CLAUDE.md): no camera index, GPIO pin, or confidence
threshold is ever hardcoded in the application code — it all lives in a
`config/torno_XX.json` file validated against `StationConfig`.

Mirrors exactly the schema defined in Section 4 of
docs/taller-seguro-vision-blueprint.md.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ZoneConfig(BaseModel):
    """Normalized (0-1) polygon describing the danger zone around the chuck,
    as produced by `calibrate_zone.py`."""

    red_zone_polygon: list[tuple[float, float]]


class StationConfig(BaseModel):
    """Full configuration for one physical station (one torno/fresadora)."""

    station_id: str
    mode: Literal["demo", "production"]
    # Independiente de `mode`: en el T480 (Intel, sin GPU dedicada) usar
    # "openvino"; con GPU NVIDIA, "pt"; en el Pi siempre "edgetpu".
    inference_backend: Literal["pt", "openvino", "edgetpu"] = "openvino"
    camera_source: Literal["webcam", "picamera", "video_file"]
    camera_index_or_path: str | int | None = None
    zone: ZoneConfig
    classes_enabled: list[
        Literal["no_glasses", "glove_on_lathe", "hand_in_red_zone", "chuck_key_visible"]
    ]
    confidence_thresholds: dict[str, float] = Field(default_factory=dict)
    alert_output: Literal["mock", "gpio"]
    gpio_pin: int | None = None
    buffer_pre_seconds: float = 7.0
    buffer_post_seconds: float = 8.0
    usb_mount_path: str = "/media/usb0"
