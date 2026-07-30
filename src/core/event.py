"""Event: the single data contract this whole device produces.

Every risk detected by `rules_engine.evaluate()` becomes one `Event`. Once
`ClipWriter.flush()` writes the video clip, it fills in `clip_path` and
writes this same data as a JSON sidecar next to the clip
(`clips/<station_id>/<fecha>/<timestamp>_<event_type>.json`) — that JSON is
the contract for the STPS report (Reglas No Negociables #5 en CLAUDE.md), so
no field here is optional to omit from the sidecar.

Zero imports from capture/, inference/ or alert/ — this is pure data.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path


class EventType(StrEnum):
    NO_GLASSES = "no_glasses"
    GLOVE_ON_LATHE = "glove_on_lathe"
    HAND_IN_RED_ZONE = "hand_in_red_zone"
    CHUCK_KEY_VISIBLE = "chuck_key_visible"


@dataclass
class Event:
    station_id: str
    event_type: EventType
    confidence: float
    duration_pre_s: float = 7.0
    duration_post_s: float = 8.0
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_utc: datetime = field(default_factory=lambda: datetime.now(UTC))
    clip_path: str | None = None
    resolved: bool = False

    def to_dict(self) -> dict:
        """Serialize to the exact field set defined in blueprint Section 4."""
        return {
            "event_id": self.event_id,
            "station_id": self.station_id,
            "event_type": (
                self.event_type.value
                if isinstance(self.event_type, EventType)
                else self.event_type
            ),
            "timestamp_utc": self.timestamp_utc.astimezone(UTC)
            .isoformat()
            .replace("+00:00", "Z"),
            "confidence": self.confidence,
            "clip_path": self.clip_path,
            "duration_pre_s": self.duration_pre_s,
            "duration_post_s": self.duration_post_s,
            "resolved": self.resolved,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def write_sidecar(self, path: str | Path) -> Path:
        """Write this event as the JSON sidecar file. Returns the path written."""
        sidecar_path = Path(path)
        sidecar_path.parent.mkdir(parents=True, exist_ok=True)
        sidecar_path.write_text(self.to_json(), encoding="utf-8")
        return sidecar_path
