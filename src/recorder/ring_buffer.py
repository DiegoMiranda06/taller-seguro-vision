"""Circular in-RAM frame buffer — the pre-roll source for `ClipWriter`.

Always running while the pipeline is up; only ever read out to disk when
`rules_engine.evaluate()` produces an `Event`. Timestamp-based (not a fixed
frame count) so it stays correct regardless of the actual capture FPS.
"""

from __future__ import annotations

from collections import deque

import numpy as np

TimedFrame = tuple[float, np.ndarray]


class RingBuffer:
    """Keeps the last `max_seconds` worth of frames, evicting older ones as
    new frames arrive."""

    def __init__(self, max_seconds: float) -> None:
        if max_seconds <= 0:
            raise ValueError("max_seconds must be > 0")
        self._max_seconds = max_seconds
        self._frames: deque[TimedFrame] = deque()

    def append(self, frame: np.ndarray, timestamp: float) -> None:
        self._frames.append((timestamp, frame))
        self._trim(timestamp)

    def _trim(self, now: float) -> None:
        while self._frames and (now - self._frames[0][0]) > self._max_seconds:
            self._frames.popleft()

    def get_frames(self) -> list[TimedFrame]:
        """Snapshot of currently buffered (timestamp, frame) pairs, oldest first."""
        return list(self._frames)

    def __len__(self) -> int:
        return len(self._frames)
