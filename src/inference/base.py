"""Abstract interface every detector implements.

`pipeline.py` only ever talks to this interface — it decides which concrete
detector to instantiate based on `StationConfig.inference_backend`, never
its own hardware-detection logic. `Detector.detect()` returns
`list[core.rules_engine.Detection]`, the shared, hardware-agnostic value
object rules_engine and inference/ both understand — inference/ depends on
core/, never the reverse.

**Deliberately out of scope here (per this build's Step 8-9 boundary)**:
no trained custom model exists yet for `no_glasses` / `glove_on_lathe` /
`hand_in_red_zone` / `chuck_key_visible`. Concrete detectors below are
generic Ultralytics-API wrappers that load whatever `model_path` a config
points at — they are not blocked on real weights, and are exercised in
tests exclusively through `FakeDetector` test doubles, never by loading an
actual model.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from src.core.rules_engine import Detection


class Detector(ABC):
    """Runs object detection on a single frame."""

    @abstractmethod
    def detect(self, frame: np.ndarray) -> list[Detection]:
        """Return all detections found in `frame`, in normalized (0-1)
        bbox coordinates, with `class_name` matching one of the raw
        classes `rules_engine` understands (`no_glasses`,
        `glove_on_lathe`, `chuck_key_visible`, `hand`)."""


def ultralytics_result_to_detections(result) -> list[Detection]:
    """Shared parsing helper for Ultralytics-API-based detectors
    (`YoloPtDetector`, `YoloOpenVINODetector`): turns one `ultralytics`
    `Results` object into `list[Detection]` with normalized bbox
    coordinates. Not a Detector implementation itself — just avoids
    duplicating this parsing between the two adapters that share the same
    result format.
    """
    detections: list[Detection] = []
    boxes = getattr(result, "boxes", None)
    if boxes is None:
        return detections

    names = result.names
    # xyxyn = boxes normalized to [0, 1], exactly the coordinate space
    # zone.py / rules_engine.py expect.
    for xyxyn, conf, cls in zip(
        boxes.xyxyn.tolist(), boxes.conf.tolist(), boxes.cls.tolist(), strict=True
    ):
        class_name = names[int(cls)]
        x1, y1, x2, y2 = xyxyn
        detections.append(
            Detection(class_name=class_name, bbox=(x1, y1, x2, y2), confidence=float(conf))
        )
    return detections
