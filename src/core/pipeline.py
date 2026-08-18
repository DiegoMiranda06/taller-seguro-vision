"""Orchestrator: capture -> detect -> rules -> alert + recorder.

Same `Pipeline` class runs in `mode: demo` (laptop/webcam/mock) and
`mode: production` (Pi/Picamera/GPIO) — only the concrete `CameraSource` /
`Detector` / `AlertOutput` instances handed to it differ, chosen by the
`build_*` factory functions below based on `StationConfig` fields. Nothing
here branches on "is this a Raspberry Pi" (Reglas No Negociables #1 en
CLAUDE.md).

Hardware-specific adapter modules (`picamera_source`, `gpio_alert`,
`yolo_edgetpu_detector`) are imported lazily, inside the `build_*`
functions, and only on the branch that actually selects them — so
importing `src.core.pipeline` itself never requires picamera2/gpiozero/
pycoral/tflite-runtime to be installed, and neither do
ultralytics-optional extras like openvino unless that backend is chosen.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from src.alert.base import AlertOutput
from src.capture.base import CameraSource
from src.config.schema import StationConfig
from src.core.rules_engine import evaluate
from src.inference.base import Detector
from src.recorder.clip_writer import ClipWriter
from src.recorder.ring_buffer import RingBuffer

logger = logging.getLogger(__name__)


def build_camera_source(config: StationConfig) -> CameraSource:
    if config.camera_source == "webcam":
        from src.capture.webcam_source import WebcamSource

        index = config.camera_index_or_path if config.camera_index_or_path is not None else 0
        return WebcamSource(index)
    if config.camera_source == "video_file":
        from src.capture.video_file_source import VideoFileSource

        return VideoFileSource(str(config.camera_index_or_path))
    if config.camera_source == "picamera":
        from src.capture.picamera_source import PicameraSource

        return PicameraSource()
    raise ValueError(f"Unknown camera_source: {config.camera_source}")


def build_detector(config: StationConfig, models_dir: str | Path = "models") -> Detector:
    models_dir = Path(models_dir)
    if config.inference_backend == "pt":
        from src.inference.yolo_pt_detector import YoloPtDetector

        return YoloPtDetector(model_path=str(models_dir / "best.pt"))
    if config.inference_backend == "openvino":
        from src.inference.yolo_openvino_detector import YoloOpenVINODetector

        return YoloOpenVINODetector(model_path=str(models_dir / "best_openvino_model"))
    if config.inference_backend == "edgetpu":
        from src.inference.yolo_edgetpu_detector import YoloEdgeTPUDetector

        labels = {
            0: "no_glasses",
            1: "no_helmet",
        }
        return YoloEdgeTPUDetector(
            model_path=str(models_dir / "best_edgetpu.tflite"), labels=labels
        )
    raise ValueError(f"Unknown inference_backend: {config.inference_backend}")


def build_alert_output(config: StationConfig) -> AlertOutput:
    if config.alert_output == "mock":
        from src.alert.mock_alert import MockAlertOutput

        return MockAlertOutput()
    if config.alert_output == "gpio":
        from src.alert.gpio_alert import GpioAlertOutput

        if config.gpio_pin is None:
            raise ValueError("gpio_pin is required in config when alert_output == 'gpio'")
        return GpioAlertOutput(pin=config.gpio_pin)
    raise ValueError(f"Unknown alert_output: {config.alert_output}")


def resolve_clip_output_root(config: StationConfig) -> Path:
    """`usb_mount_path` with a fallback to a local `clips/` directory if the
    USB drive isn't mounted (blueprint Section 4)."""
    usb_path = Path(config.usb_mount_path)
    if usb_path.exists():
        return usb_path
    logger.warning(
        "usb_mount_path %s not found — falling back to local ./clips directory", usb_path
    )
    return Path("clips")


class Pipeline:
    """Runs the capture -> detect -> rules -> alert/recorder loop for one station.

    `camera`, `detector`, `alert`, `clip_writer` and `ring_buffer` are all
    injected so tests can supply fakes/doubles (e.g. `FakeDetector`,
    `VideoFileSource` against a synthetic video) without touching real
    hardware or model weights.
    """

    def __init__(
        self,
        config: StationConfig,
        camera: CameraSource,
        detector: Detector,
        alert: AlertOutput,
        clip_writer: ClipWriter,
        ring_buffer: RingBuffer | None = None,
    ) -> None:
        self.config = config
        self.camera = camera
        self.detector = detector
        self.alert = alert
        self.clip_writer = clip_writer
        self.ring_buffer = ring_buffer or RingBuffer(max_seconds=config.buffer_pre_seconds)

    def run(self) -> None:
        """Main loop. On any uncaught exception, calls `alert.fail_safe()`
        before re-raising — Reglas No Negociables #4/#5: the alert output
        must fail toward a visible failing state, never silent green."""
        self.camera.open()
        try:
            self._loop()
        except Exception:
            logger.exception("Pipeline crashed — forcing alert into fail-safe state")
            self.alert.fail_safe()
            raise
        finally:
            self.camera.close()

    def _loop(self) -> None:
        pending_event = None
        pending_event_epoch: float | None = None
        post_roll_frames: list[tuple[float, object]] = []
        post_roll_deadline: float | None = None

        while True:
            frame = self.camera.read_frame()
            if frame is None:
                break  # end of video file, or camera read failure

            now = time.time()
            self.ring_buffer.append(frame, now)

            if pending_event is not None:
                post_roll_frames.append((now, frame))
                if post_roll_deadline is not None and now >= post_roll_deadline:
                    self._flush_event(pending_event, pending_event_epoch, post_roll_frames)
                    pending_event = None
                    pending_event_epoch = None
                    post_roll_frames = []
                    post_roll_deadline = None
                continue

            detections = self.detector.detect(frame)
            event = evaluate(detections, self.config)
            if event is not None:
                logger.warning(
                    "Event detected: %s (confidence=%.2f)", event.event_type.value, event.confidence
                )
                self.alert.trigger(event.event_type.value)
                pending_event = event
                pending_event_epoch = now
                post_roll_frames = []
                post_roll_deadline = now + self.config.buffer_post_seconds

        # Video file ended mid post-roll: flush what we have rather than
        # dropping the event entirely.
        if pending_event is not None:
            self._flush_event(pending_event, pending_event_epoch, post_roll_frames)

    def _flush_event(self, event, event_epoch: float, post_roll_frames: list) -> None:
        # `event_epoch` is the time.time() value captured when this event was
        # detected — used only to split the ring buffer's own time.time()
        # timestamps into pre-roll. `event.timestamp_utc` (a datetime, used
        # for the JSON sidecar / STPS contract) is a separate, wall-clock
        # concept and intentionally not reused for this comparison.
        pre_frames = [tf for tf in self.ring_buffer.get_frames() if tf[0] <= event_epoch]
        self.clip_writer.flush(event, pre_frames, post_roll_frames)
        self.alert.clear()
