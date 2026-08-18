"""Combines raw detections with station config into an `Event | None`.

Zero imports from capture/, inference/ or alert/ (Reglas No Negociables #3
en CLAUDE.md) — `evaluate()` receives already-extracted detections (class
name, bbox, confidence) and a `StationConfig`, and is fully testable with
synthetic data, no camera/model/GPIO required.

`Detection` lives here (not in inference/) on purpose: inference/base.py's
`Detector.detect()` returns `list[Detection]`, so inference/ depends on
core/, never the other way around — the dependency arrow that keeps this
module hardware-free.

Alcance actual (v1): el detector emite directamente las clases de EPP que
`rules_engine` evalúa (`no_glasses`, `no_helmet`) — no hay lógica de zona.
Las reglas de near-miss basadas en proximidad (guante en torno, mano en
zona roja, llave de mandril) son roadmap y volverían a apoyarse en
`src/core/zone.py`, que se mantiene puro y probado para cuando se
reintroduzcan.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.config.schema import StationConfig
from src.core.event import Event, EventType
from src.core.zone import BBox

DEFAULT_CONFIDENCE_THRESHOLD = 0.5


@dataclass(frozen=True)
class Detection:
    """One raw detection from a `Detector`, in normalized (0-1) coordinates."""

    class_name: str
    bbox: BBox
    confidence: float


def evaluate(detections: list[Detection], config: StationConfig) -> Event | None:
    """Return the highest-confidence risk `Event` found in this frame's
    detections, honoring `config.classes_enabled` and
    `config.confidence_thresholds`, or `None` if nothing qualifies.

    Only one `Event` is ever returned per call — `pipeline.py` calls this
    once per frame, so simultaneous risks are broken by confidence.
    """
    best_event: Event | None = None
    best_confidence = -1.0

    for det in detections:
        if det.class_name not in config.classes_enabled:
            continue

        threshold = config.confidence_thresholds.get(
            det.class_name, DEFAULT_CONFIDENCE_THRESHOLD
        )
        if det.confidence < threshold:
            continue

        if det.confidence > best_confidence:
            best_confidence = det.confidence
            best_event = Event(
                station_id=config.station_id,
                event_type=EventType(det.class_name),
                confidence=det.confidence,
                duration_pre_s=config.buffer_pre_seconds,
                duration_post_s=config.buffer_post_seconds,
            )

    return best_event
