"""Shared fixtures and test doubles.

No real webcam, torno, or trained model is used anywhere in this test
suite — `synthetic_video_path` generates a short synthetic clip with
`cv2.VideoWriter` (solid-color frames + a moving rectangle), and
`FakeDetector` returns scripted detections instead of loading a real
Ultralytics model.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from src.config.schema import StationConfig
from src.core.rules_engine import Detection
from src.inference.base import Detector

FRAME_WIDTH = 64
FRAME_HEIGHT = 48
FPS = 10.0
FRAME_COUNT = 30  # 3 seconds at 10 fps


def _write_synthetic_video(path: Path) -> None:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))
    if not writer.isOpened():
        raise RuntimeError("Could not open cv2.VideoWriter for synthetic test fixture video")
    try:
        for i in range(FRAME_COUNT):
            frame = np.full((FRAME_HEIGHT, FRAME_WIDTH, 3), 40, dtype=np.uint8)
            x = int((i / FRAME_COUNT) * (FRAME_WIDTH - 10))
            cv2.rectangle(frame, (x, 15), (x + 10, 30), (0, 0, 255), thickness=-1)
            writer.write(frame)
    finally:
        writer.release()


@pytest.fixture
def synthetic_video_path(tmp_path: Path) -> Path:
    """A short (3s, 10fps, 64x48) synthetic .mp4 — moving rectangle over a
    solid background — generated purely with OpenCV, standing in for real
    webcam/torno footage that doesn't exist in this sandbox."""
    video_path = tmp_path / "synthetic_test_video.mp4"
    _write_synthetic_video(video_path)
    return video_path


@pytest.fixture
def sample_station_config() -> StationConfig:
    return StationConfig(
        station_id="torno_test",
        mode="demo",
        inference_backend="pt",
        camera_source="video_file",
        camera_index_or_path=None,
        classes_enabled=["no_glasses", "no_helmet"],
        confidence_thresholds={},
        alert_output="mock",
        gpio_pin=None,
        buffer_pre_seconds=1.0,
        buffer_post_seconds=0.5,
        # Deliberately a path that won't exist on any dev machine or CI
        # runner, to exercise ClipWriter's local-fallback behavior.
        usb_mount_path="/this/path/should/not/exist/on/this/machine",
    )


class FakeDetector(Detector):
    """Test double for `Detector`: returns scripted detections per call
    (one list per frame, in order), never loads a real model or weights.
    """

    def __init__(self, scripted_detections: list[list[Detection]]) -> None:
        self._script = scripted_detections
        self.call_count = 0

    def detect(self, frame: np.ndarray) -> list[Detection]:
        result = self._script[self.call_count] if self.call_count < len(self._script) else []
        self.call_count += 1
        return result
