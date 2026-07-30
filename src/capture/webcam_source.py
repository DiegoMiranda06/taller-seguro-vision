"""Live webcam capture via OpenCV — the camera source used in `mode: demo`.

Only imports `cv2` (a base dependency, not a Pi/hardware-only one) — safe to
run on any laptop.
"""

from __future__ import annotations

import sys

import cv2
import numpy as np

from src.capture.base import CameraSource

_DEFAULT_FPS_FALLBACK = 20.0


class WebcamSource(CameraSource):
    """Captures frames from a local webcam via `cv2.VideoCapture`.

    `camera_index` comes straight from `StationConfig.camera_index_or_path`
    — never hardcoded (Reglas No Negociables #4 en CLAUDE.md).
    """

    def __init__(self, camera_index: int | str = 0) -> None:
        self._camera_index = camera_index
        self._cap: cv2.VideoCapture | None = None

    def open(self) -> None:
        # Nota Windows (blueprint Section 10): en el ThinkPad T480, forzar
        # el backend DirectShow evita timeouts al abrir la webcam.
        if sys.platform.startswith("win"):
            self._cap = cv2.VideoCapture(self._camera_index, cv2.CAP_DSHOW)
        else:
            self._cap = cv2.VideoCapture(self._camera_index)

        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open webcam at index/path: {self._camera_index!r}")

    def read_frame(self) -> np.ndarray | None:
        if self._cap is None:
            raise RuntimeError("WebcamSource.open() must be called before read_frame()")
        ok, frame = self._cap.read()
        if not ok:
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
