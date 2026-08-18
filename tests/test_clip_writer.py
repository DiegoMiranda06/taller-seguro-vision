"""RingBuffer + ClipWriter, exercised against frames read from a synthetic
test video (generated with cv2.VideoWriter in conftest.py) — no real
webcam or torno footage involved.
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from src.core.event import Event, EventType
from src.recorder.clip_writer import ClipWriter
from src.recorder.ring_buffer import RingBuffer


def _read_all_frames(video_path: Path) -> list[np.ndarray]:
    cap = cv2.VideoCapture(str(video_path))
    frames = []
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frames.append(frame)
    finally:
        cap.release()
    return frames


# ---------------------------------------------------------------------------
# RingBuffer
# ---------------------------------------------------------------------------


def test_ring_buffer_keeps_frames_within_window():
    buffer = RingBuffer(max_seconds=2.0)
    buffer.append(np.zeros((2, 2, 3), dtype=np.uint8), timestamp=0.0)
    buffer.append(np.zeros((2, 2, 3), dtype=np.uint8), timestamp=1.0)
    buffer.append(np.zeros((2, 2, 3), dtype=np.uint8), timestamp=2.0)
    assert len(buffer) == 3


def test_ring_buffer_evicts_frames_older_than_max_seconds():
    buffer = RingBuffer(max_seconds=2.0)
    buffer.append(np.zeros((2, 2, 3), dtype=np.uint8), timestamp=0.0)
    buffer.append(np.zeros((2, 2, 3), dtype=np.uint8), timestamp=1.0)
    buffer.append(np.zeros((2, 2, 3), dtype=np.uint8), timestamp=5.0)  # now 5.0 - 0.0 > 2.0
    remaining_timestamps = [ts for ts, _ in buffer.get_frames()]
    assert 0.0 not in remaining_timestamps
    assert 5.0 in remaining_timestamps


def test_ring_buffer_get_frames_is_oldest_first():
    buffer = RingBuffer(max_seconds=10.0)
    for ts in (1.0, 2.0, 3.0):
        buffer.append(np.zeros((2, 2, 3), dtype=np.uint8), timestamp=ts)
    timestamps = [ts for ts, _ in buffer.get_frames()]
    assert timestamps == [1.0, 2.0, 3.0]


def test_ring_buffer_rejects_non_positive_max_seconds():
    with pytest.raises(ValueError):
        RingBuffer(max_seconds=0)


# ---------------------------------------------------------------------------
# ClipWriter
# ---------------------------------------------------------------------------


def test_clip_writer_flush_creates_clip_and_sidecar(tmp_path, synthetic_video_path):
    frames = _read_all_frames(synthetic_video_path)
    assert len(frames) > 0, "synthetic fixture video must decode at least one frame"

    pre_frames = [(float(i), frame) for i, frame in enumerate(frames[: len(frames) // 2])]
    post_frames = [
        (float(i + len(pre_frames)), frame) for i, frame in enumerate(frames[len(frames) // 2 :])
    ]

    event = Event(
        station_id="torno_test",
        event_type=EventType.NO_GLASSES,
        confidence=0.87,
        duration_pre_s=7.0,
        duration_post_s=8.0,
    )

    writer = ClipWriter(output_root=tmp_path / "clips", fps=10.0)
    result = writer.flush(event, pre_frames, post_frames)

    assert result is event  # mutated in place and returned
    assert event.clip_path is not None

    clip_full_path = (tmp_path / "clips") / event.clip_path
    assert clip_full_path.exists()
    assert clip_full_path.suffix == ".mp4"

    sidecar_path = clip_full_path.with_suffix(".json")
    assert sidecar_path.exists()


def test_clip_writer_sidecar_has_required_stps_fields(tmp_path, synthetic_video_path):
    frames = _read_all_frames(synthetic_video_path)
    pre_frames = [(0.0, frames[0])]
    post_frames = [(1.0, frames[-1])]

    event = Event(
        station_id="torno_test",
        event_type=EventType.NO_HELMET,
        confidence=0.66,
    )
    writer = ClipWriter(output_root=tmp_path / "clips", fps=10.0)
    writer.flush(event, pre_frames, post_frames)

    clip_full_path = (tmp_path / "clips") / event.clip_path
    sidecar_path = clip_full_path.with_suffix(".json")
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))

    # Reglas No Negociables #5 (CLAUDE.md): the STPS report contract.
    for required_field in ("station_id", "timestamp_utc", "event_type", "confidence"):
        assert required_field in sidecar, f"missing required sidecar field: {required_field}"

    assert sidecar["station_id"] == "torno_test"
    assert sidecar["event_type"] == "no_helmet"
    assert sidecar["confidence"] == 0.66
    assert sidecar["clip_path"] == event.clip_path
    assert sidecar["resolved"] is False


def test_clip_writer_produces_playable_video_with_expected_frame_count(
    tmp_path, synthetic_video_path
):
    frames = _read_all_frames(synthetic_video_path)
    pre_frames = [(float(i), f) for i, f in enumerate(frames[:5])]
    post_frames = [(float(i + 5), f) for i, f in enumerate(frames[5:10])]

    event = Event(station_id="torno_test", event_type=EventType.NO_GLASSES, confidence=0.5)
    writer = ClipWriter(output_root=tmp_path / "clips", fps=10.0)
    writer.flush(event, pre_frames, post_frames)

    clip_full_path = (tmp_path / "clips") / event.clip_path
    cap = cv2.VideoCapture(str(clip_full_path))
    try:
        written_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    finally:
        cap.release()

    assert written_frame_count == len(pre_frames) + len(post_frames)


def test_clip_writer_raises_on_zero_frames(tmp_path):
    event = Event(station_id="torno_test", event_type=EventType.NO_GLASSES, confidence=0.5)
    writer = ClipWriter(output_root=tmp_path / "clips")
    with pytest.raises(ValueError):
        writer.flush(event, [], [])
