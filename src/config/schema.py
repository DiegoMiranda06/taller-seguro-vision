"""Pydantic schema for per-station configuration.

This is the ONLY source of variation between stations (Reglas No
Negociables #4 en CLAUDE.md): no camera index, GPIO pin, or confidence
threshold is ever hardcoded in the application code — it all lives in a
`config/torno_XX.json` file validated against `StationConfig`.

Mirrors exactly the schema defined in Section 4 de
docs/taller-seguro-vision-blueprint.md.

Alcance actual (v1): solo EPP (`no_glasses`, `no_helmet`) — no depende de
una zona roja calibrada por estación. `ZoneConfig` se conserva para cuando
vuelvan las reglas de near-miss basadas en proximidad (guante en torno,
mano en zona roja, llave de mandril — ver roadmap en el blueprint).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ZoneConfig(BaseModel):
    """Normalized (0-1) polygon describing a danger zone (ej. alrededor del
    mandril), producido por `calibrate_zone.py`. No usado por el alcance v1
    (solo EPP) — reservado para las reglas de near-miss del roadmap."""

    red_zone_polygon: list[tuple[float, float]]


class StationConfig(BaseModel):
    """Full configuration for one physical station (one torno/fresadora)."""

    station_id: str
    mode: Literal["demo", "production"]
    # Independiente de `mode`. "pt" corre en cualquier CPU, incluida la ARM
    # de una Raspberry Pi — es el backend recomendado ahí. "openvino" es
    # exclusivo de CPU/iGPU Intel x86 (ej. el T480) y NO corre en la Pi.
    # "edgetpu" requiere el Coral USB Accelerator (todavía no comprado).
    inference_backend: Literal["pt", "openvino", "edgetpu"] = "pt"
    camera_source: Literal["webcam", "picamera", "video_file"]
    camera_index_or_path: str | int | None = None
    zone: ZoneConfig | None = None
    classes_enabled: list[Literal["no_glasses", "no_helmet"]]
    confidence_thresholds: dict[str, float] = Field(default_factory=dict)
    alert_output: Literal["mock", "gpio"]
    gpio_pin: int | None = None
    buffer_pre_seconds: float = 7.0
    buffer_post_seconds: float = 8.0
    usb_mount_path: str = "/media/usb0"
