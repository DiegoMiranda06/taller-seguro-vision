"""End-to-end Pipeline integration test: VideoFileSource (synthetic video)
-> FakeDetector (scripted, no real model) -> rules_engine -> MockAlertOutput
+ real RingBuffer/ClipWriter -> real clip + JSON sidecar on disk.

Exercises rules_engine, ring_buffer, clip_writer and pipeline together
without any camera, GPIO, or trained model weights.
"""

from __future__ import annotations

import json

import numpy as np

from src.alert.mock_alert import MockAlertOutput
from src.capture.video_file_source import VideoFileSource
from src.core.pipeline import Pipeline
from src.core.rules_engine import Detection
from src.recorder.clip_writer import ClipWriter
from src.recorder.ring_buffer import RingBuffer
from tests.conftest import FRAME_COUNT, FakeDetector


def test_pipeline_end_to_end_writes_clip_and_sidecar_on_event(
    tmp_path, synthetic_video_path, sample_station_config
):
    camera = VideoFileSource(str(synthetic_video_path))

    # No detections at all until frame index 5, where a confident
    # "no_glasses" detection fires — everything else is empty (no risk).
    scripted: list[list[Detection]] = [[] for _ in range(FRAME_COUNT)]
    scripted[5] = [Detection(class_name="no_glasses", bbox=(0.1, 0.1, 0.3, 0.3), confidence=0.9)]
    detector = FakeDetector(scripted)

    alert = MockAlertOutput()
    clip_writer = ClipWriter(output_root=tmp_path / "clips", fps=10.0)
    ring_buffer = RingBuffer(max_seconds=sample_station_config.buffer_pre_seconds)

    pipeline = Pipeline(
        config=sample_station_config,
        camera=camera,
        detector=detector,
        alert=alert,
        clip_writer=clip_writer,
        ring_buffer=ring_buffer,
    )

    pipeline.run()

    station_dir = tmp_path / "clips" / sample_station_config.station_id
    assert station_dir.exists(), "expected an event to have written a clip directory"

    clip_files = list(station_dir.rglob("*.mp4"))
    sidecar_files = list(station_dir.rglob("*.json"))
    assert len(clip_files) == 1
    assert len(sidecar_files) == 1

    sidecar = json.loads(sidecar_files[0].read_text(encoding="utf-8"))
    assert sidecar["event_type"] == "no_glasses"
    assert sidecar["station_id"] == sample_station_config.station_id
    assert sidecar["confidence"] == 0.9


def test_pipeline_with_no_risk_detections_writes_nothing(
    tmp_path, synthetic_video_path, sample_station_config
):
    camera = VideoFileSource(str(synthetic_video_path))
    detector = FakeDetector([[] for _ in range(FRAME_COUNT)])  # never any risk
    alert = MockAlertOutput()
    clip_writer = ClipWriter(output_root=tmp_path / "clips", fps=10.0)
    ring_buffer = RingBuffer(max_seconds=sample_station_config.buffer_pre_seconds)

    pipeline = Pipeline(
        config=sample_station_config,
        camera=camera,
        detector=detector,
        alert=alert,
        clip_writer=clip_writer,
        ring_buffer=ring_buffer,
    )
    pipeline.run()

    assert not (tmp_path / "clips").exists()


def test_pipeline_fail_safe_called_on_uncaught_exception(sample_station_config):
    class ExplodingDetector(FakeDetector):
        def detect(self, frame):
            raise RuntimeError("simulated model crash")

    class CountingCamera:
        def __init__(self):
            self.closed = False

        def open(self):
            pass

        def read_frame(self):
            return np.zeros((4, 4, 3), dtype=np.uint8)

        def close(self):
            self.closed = True

        def get_fps(self):
            return 10.0

    class RecordingAlert(MockAlertOutput):
        def __init__(self):
            self.fail_safe_called = False

        def fail_safe(self):
            self.fail_safe_called = True

    alert = RecordingAlert()
    pipeline = Pipeline(
        config=sample_station_config,
        camera=CountingCamera(),
        detector=ExplodingDetector([]),
        alert=alert,
        clip_writer=ClipWriter(output_root="unused"),
        ring_buffer=RingBuffer(max_seconds=1.0),
    )

    try:
        pipeline.run()
        raised = False
    except RuntimeError:
        raised = True

    assert raised, "pipeline.run() must re-raise after failing safe"
    assert alert.fail_safe_called, "AlertOutput.fail_safe() must be called before re-raising"
    assert pipeline.camera.closed, "camera must still be closed even after a crash"
