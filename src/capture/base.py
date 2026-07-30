"""Abstract interface every camera source implements.

`pipeline.py` only ever talks to this interface — it decides which concrete
adapter to instantiate based on `StationConfig.camera_source`, and never
branches its own logic on "am I on a Pi" (Reglas No Negociables #1 en
CLAUDE.md).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class CameraSource(ABC):
    """A source of video frames — webcam, video file, or Picamera2."""

    @abstractmethod
    def open(self) -> None:
        """Acquire the underlying device/file. Must be safe to call once
        before the first `read_frame()`."""

    @abstractmethod
    def read_frame(self) -> np.ndarray | None:
        """Return the next frame (BGR, HxWx3 uint8), or `None` when the
        source is exhausted (end of video file) or a frame couldn't be
        read (camera error)."""

    @abstractmethod
    def close(self) -> None:
        """Release the underlying device/file. Must be safe to call even
        if `open()` was never called or already failed."""

    @abstractmethod
    def get_fps(self) -> float:
        """Nominal frames-per-second of this source, used by `ClipWriter`
        to write clips back at a sensible playback speed. Implementations
        should return a sane fallback (e.g. 20.0) if the underlying source
        doesn't report one."""
