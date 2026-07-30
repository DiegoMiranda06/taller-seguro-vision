"""Plays back an existing video file as a `CameraSource`.

Used to test the pipeline end-to-end without a real camera — including in
this repo's own test suite, against a short synthetic video generated with
`cv2.VideoWriter` in `tests/conftest.py` (no real webcam or footage needed).
"""

from __future__ import annotations

import cv2
import numpy as np

from src.capture.base import CameraSource

_DEFAULT_FPS_FALLBACK = 20.0


class VideoFileSource(CameraSource):
    """Reads frames sequentially from a video file on disk.

    `path` comes from `StationConfig.camera_index_or_path` when
    `camera_source == "video_file"`. If `loop` is True, restarts from frame
    0 instead of signaling end-of-stream — useful for long-running demos,
    off by default so tests see a clean end-of-video `None`.
    """

    def __init__(self, path: str, loop: bool = False) -> None:
        self._path = path
        self._loop = loop
        self._cap: cv2.VideoCapture | None = None

    def open(self) -> None:
        self._cap = cv2.VideoCapture(self._path)
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open video file: {self._path!r}")

    def read_frame(self) -> np.ndarray | None:
        if self._cap is None:
            raise RuntimeError("VideoFileSource.open() must be called before read_frame()")

        ok, frame = self._cap.read()
        if not ok:
            if self._loop:
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, frame = self._cap.read()
                if ok:
                    return frame
            return None
        return frame

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def get_fps(self) -> float:
        if self._cap is None:
            return _DEFAULT_FPS_FALLBACK
        fps = self._cap.get(cv2.CAP_PROP_FPS)
        return fps if fps and fps > 0 else _DEFAULT_FPS_FALLBACK
