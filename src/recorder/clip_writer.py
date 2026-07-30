"""Writes pre+post-roll frames to a video clip + JSON sidecar on Event.

`ClipWriter.flush()` takes already-collected pre/post frame lists (rather
than reaching into a live capture loop itself) specifically so it's
testable in isolation, with fabricated numpy frames, no camera/model
required (see tests/test_clip_writer.py).
"""

from __future__ import annotations

from pathlib import Path

import cv2

from src.core.event import Event
from src.recorder.ring_buffer import TimedFrame

_DEFAULT_FPS = 20.0
_DEFAULT_FOURCC = "mp4v"


class ClipWriter:
    """Writes a `clips/<station_id>/<fecha>/<HHMMSS>_<event_type>.mp4` +
    matching `.json` sidecar for each `Event`.

    `output_root` should be `StationConfig.usb_mount_path` when that path
    exists, falling back to a local `clips/` directory otherwise (the
    fallback decision belongs to the caller, e.g. `pipeline.py` /
    `app.py` — this class just writes wherever it's told to).
    """

    def __init__(
        self,
        output_root: str | Path = "clips",
        fps: float = _DEFAULT_FPS,
        fourcc: str = _DEFAULT_FOURCC,
    ) -> None:
        self.output_root = Path(output_root)
        self.fps = fps if fps and fps > 0 else _DEFAULT_FPS
        self.fourcc = fourcc

    def flush(
        self,
        event: Event,
        pre_frames: list[TimedFrame],
        post_frames: list[TimedFrame],
    ) -> Event:
        """Write the clip + JSON sidecar for `event`, fill in
        `event.clip_path`, and return the (mutated) event."""
        all_frames = [*pre_frames, *post_frames]
        if not all_frames:
            raise ValueError("Cannot write a clip with zero frames")

        station_dir = (
            self.output_root / event.station_id / event.timestamp_utc.strftime("%Y-%m-%d")
        )
        station_dir.mkdir(parents=True, exist_ok=True)

        base_name = f"{event.timestamp_utc.strftime('%H%M%S')}_{event.event_type.value}"
        clip_path = station_dir / f"{base_name}.mp4"
        sidecar_path = station_dir / f"{base_name}.json"

        self._write_clip(clip_path, all_frames)

        event.clip_path = str(clip_path.relative_to(self.output_root))
        event.write_sidecar(sidecar_path)
        return event

    def _write_clip(self, clip_path: Path, frames: list[TimedFrame]) -> None:
        first_frame = frames[0][1]
        height, width = first_frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*self.fourcc)
        writer = cv2.VideoWriter(str(clip_path), fourcc, self.fps, (width, height))
        if not writer.isOpened():
            raise RuntimeError(f"Could not open VideoWriter for {clip_path}")
        try:
            for _, frame in frames:
                writer.write(frame)
        finally:
            writer.release()
