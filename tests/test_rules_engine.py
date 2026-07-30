"""rules_engine.evaluate() tested with synthetic detections — no camera,
model, or GPIO involved.
"""

from __future__ import annotations

from src.config.schema import StationConfig
from src.core.event import EventType
from src.core.rules_engine import Detection, evaluate


def test_direct_event_type_above_threshold_produces_event(sample_station_config: StationConfig):
    detections = [Detection(class_name="no_glasses", bbox=(0, 0, 0.1, 0.1), confidence=0.9)]
    event = evaluate(detections, sample_station_config)
    assert event is not None
    assert event.event_type == EventType.NO_GLASSES
    assert event.confidence == 0.9
    assert event.station_id == sample_station_config.station_id


def test_below_threshold_produces_no_event(sample_station_config: StationConfig):
    config = sample_station_config.model_copy(
        update={"confidence_thresholds": {"no_glasses": 0.8}}
    )
    detections = [Detection(class_name="no_glasses", bbox=(0, 0, 0.1, 0.1), confidence=0.5)]
    assert evaluate(detections, config) is None


def test_class_not_enabled_produces_no_event(sample_station_config: StationConfig):
    config = sample_station_config.model_copy(update={"classes_enabled": ["glove_on_lathe"]})
    detections = [Detection(class_name="no_glasses", bbox=(0, 0, 0.1, 0.1), confidence=0.99)]
    assert evaluate(detections, config) is None


def test_hand_inside_red_zone_produces_hand_in_red_zone_event(
    sample_station_config: StationConfig,
):
    # sample_station_config.zone.red_zone_polygon covers (0.3,0.3)-(0.7,0.8)
    hand_bbox = (0.45, 0.45, 0.55, 0.55)  # center (0.5, 0.5) — inside
    detections = [Detection(class_name="hand", bbox=hand_bbox, confidence=0.7)]
    event = evaluate(detections, sample_station_config)
    assert event is not None
    assert event.event_type == EventType.HAND_IN_RED_ZONE


def test_hand_outside_red_zone_produces_no_event(sample_station_config: StationConfig):
    hand_bbox = (0.0, 0.0, 0.05, 0.05)  # center (0.025, 0.025) — outside
    detections = [Detection(class_name="hand", bbox=hand_bbox, confidence=0.99)]
    assert evaluate(detections, sample_station_config) is None


def test_hand_in_red_zone_ignored_when_class_disabled(sample_station_config: StationConfig):
    config = sample_station_config.model_copy(
        update={"classes_enabled": ["no_glasses", "glove_on_lathe", "chuck_key_visible"]}
    )
    hand_bbox = (0.45, 0.45, 0.55, 0.55)
    detections = [Detection(class_name="hand", bbox=hand_bbox, confidence=0.9)]
    assert evaluate(detections, config) is None


def test_unrecognized_class_name_produces_no_event(sample_station_config: StationConfig):
    detections = [Detection(class_name="something_else", bbox=(0, 0, 0.1, 0.1), confidence=0.99)]
    assert evaluate(detections, sample_station_config) is None


def test_no_detections_produces_no_event(sample_station_config: StationConfig):
    assert evaluate([], sample_station_config) is None


def test_multiple_detections_returns_highest_confidence(sample_station_config: StationConfig):
    detections = [
        Detection(class_name="no_glasses", bbox=(0, 0, 0.1, 0.1), confidence=0.6),
        Detection(class_name="glove_on_lathe", bbox=(0, 0, 0.1, 0.1), confidence=0.95),
        Detection(class_name="chuck_key_visible", bbox=(0, 0, 0.1, 0.1), confidence=0.7),
    ]
    event = evaluate(detections, sample_station_config)
    assert event is not None
    assert event.event_type == EventType.GLOVE_ON_LATHE
    assert event.confidence == 0.95


def test_event_carries_buffer_durations_from_config(sample_station_config: StationConfig):
    detections = [Detection(class_name="no_glasses", bbox=(0, 0, 0.1, 0.1), confidence=0.9)]
    event = evaluate(detections, sample_station_config)
    assert event is not None
    assert event.duration_pre_s == sample_station_config.buffer_pre_seconds
    assert event.duration_post_s == sample_station_config.buffer_post_seconds
