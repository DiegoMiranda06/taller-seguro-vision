"""TFLite + Coral Edge TPU detector — `mode: production` only, used when
`StationConfig.inference_backend == "edgetpu"`.

`pycoral` / `tflite_runtime` are imported ONLY inside this module (regla
"Imports de hardware son locales al adapter" en CLAUDE.md): this file is
never imported by `pipeline.py` unless a config actually selects the
`edgetpu` backend, so the demo/laptop install never needs these installed.
Not runnable or testable in this sandbox — no Coral USB Accelerator or
compiled `edgetpu.tflite` model available here; verify on-device per
blueprint Steps 10-11.

`labels` maps the int8 model's output class indices to the raw class names
`rules_engine` understands (`no_glasses`, `glove_on_lathe`,
`chuck_key_visible`, `hand`) — supplied by the caller (pipeline.py), never
hardcoded here, since the label order depends on how Step 9's training
dataset was structured.
"""

from __future__ import annotations

import numpy as np

from src.core.rules_engine import Detection
from src.inference.base import Detector


class YoloEdgeTPUDetector(Detector):
    """Runs a TFLite int8 model compiled for the Edge TPU via `pycoral`."""

    def __init__(self, model_path: str, labels: dict[int, str], confidence: float = 0.25) -> None:
        # Local imports: Pi/Coral-only dependencies, never required for demo mode.
        from pycoral.adapters import common, detect
        from pycoral.utils.edgetpu import make_interpreter

        self._common = common
        self._detect = detect
        self._labels = labels
        self._confidence = confidence

        self._interpreter = make_interpreter(model_path)
        self._interpreter.allocate_tensors()

    def detect(self, frame: np.ndarray) -> list[Detection]:
        height, width = frame.shape[:2]
        _, scale = self._common.set_resized_input(
            self._interpreter,
            (width, height),
            lambda size: self._resize(frame, size),
        )
        self._interpreter.invoke()
        objects = self._detect.get_objects(
            self._interpreter, score_threshold=self._confidence, image_scale=scale
        )

        detections: list[Detection] = []
        for obj in objects:
            class_name = self._labels.get(obj.id, str(obj.id))
            bbox = (
                obj.bbox.xmin / width,
                obj.bbox.ymin / height,
                obj.bbox.xmax / width,
                obj.bbox.ymax / height,
            )
            detections.append(
                Detection(class_name=class_name, bbox=bbox, confidence=float(obj.score))
            )
        return detections

    @staticmethod
    def _resize(frame: np.ndarray, size: tuple[int, int]) -> np.ndarray:
        import cv2

        return cv2.resize(frame, size)
