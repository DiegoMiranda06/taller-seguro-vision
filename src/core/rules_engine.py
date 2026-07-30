"""Combines raw detections with station config into an `Event | None`.

Zero imports from capture/, inference/ or alert/ (Reglas No Negociables #3
en CLAUDE.md) — `evaluate()` receives already-extracted detections (class
name, bbox, confidence) and a `StationConfig`, and is fully testable with
synthetic data, no camera/model/GPIO required.

`Detection` lives here (not in inference/) on purpose: inference/base.py's
`Detector.detect()` returns `list[Detection]`, so inference/ depends on
core/, never the other way around — the dependency arrow that keeps this
module hardware-free.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.config.schema import StationConfig
from src.core.event import Event, EventType
from src.core.zone import BBox, bbox_in_zone

DEFAULT_CONFIDENCE_THRESHOLD = 0.5

# Event types the detector is expected to emit directly as a class label.
_DIRECT_EVENT_TYPES = frozenset({"no_glasses", "glove_on_lathe", "chuck_key_visible"})

# "hand_in_red_zone" is special: the detector emits a generic "hand" class,
# and rules_engine (not the model) decides whether it's a risk, based on
# the station's red_zone_polygon. This is what "rules_engine combina
# detecciones + red_zone_polygon del config" (blueprint Section 6) means.
_ZONE_EVENT_TYPE = "hand_in_red_zone"
_ZONE_DETECTOR_CLASS = "hand"


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
        event_type = _match_event_type(det, config)
        if event_type is None:
            continue

        threshold = config.confidence_thresholds.get(event_type, DEFAULT_CONFIDENCE_THRESHOLD)
        if det.confidence < threshold:
            continue

        if det.confidence > best_confidence:
            best_confidence = det.confidence
            best_event = Event(
                station_id=config.station_id,
                event_type=EventType(event_type),
                confidence=det.confidence,
                duration_pre_s=config.buffer_pre_seconds,
                duration_post_s=config.buffer_post_seconds,
            )

    return best_event


def _match_event_type(det: Detection, config: StationConfig) -> str | None:
    """Map one raw detection to an enabled event_type, or None if it doesn't
    correspond to any enabled risk for this station."""
    if det.class_name in _DIRECT_EVENT_TYPES and det.class_name in config.classes_enabled:
        return det.class_name

    if (
        det.class_name == _ZONE_DETECTOR_CLASS
        and _ZONE_EVENT_TYPE in config.classes_enabled
        and bbox_in_zone(det.bbox, config.zone.red_zone_polygon)
    ):
        return _ZONE_EVENT_TYPE

    return None
