"""Picamera2 + Arducam IMX477 capture — `mode: production` only.

`picamera2` is imported ONLY inside this module (Reglas No Negociables #1 en
CLAUDE.md / regla "Imports de hardware son locales al adapter"): this file
is never imported by `pipeline.py` unless `StationConfig.camera_source ==
"picamera"`, so the demo/laptop install never needs this dependency
installed. Not runnable or testable in this sandbox — no Raspberry Pi or
CSI camera hardware available here; verify on-device per blueprint Step 10.
"""

from __future__ import annotations

import numpy as np

from src.capture.base import CameraSource

_DEFAULT_FPS_FALLBACK = 20.0


class PicameraSource(CameraSource):
    """Captures frames from the Arducam IMX477 via `Picamera2`."""

    def __init__(self, fps_hint: float = _DEFAULT_FPS_FALLBACK) -> None:
        self._fps_hint = fps_hint
        self._picam2 = None

    def open(self) -> None:
        from picamera2 import Picamera2  # local import: Pi-only dependency

        self._picam2 = Picamera2()
        config = self._picam2.create_video_configuration(main={"format": "BGR888"})
        self._picam2.configure(config)
        self._picam2.start()

    def read_frame(self) -> np.ndarray | None:
        if self._picam2 is None:
            raise RuntimeError("PicameraSource.open() must be called before read_frame()")
        return self._picam2.capture_array()

    def close(self) -> None:
        if self._picam2 is not None:
            self._picam2.stop()
            self._picam2 = None

    def get_fps(self) -> float:
        return self._fps_hint
