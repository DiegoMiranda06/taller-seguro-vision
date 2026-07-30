"""OpenVINO detector — the recommended backend on Intel laptops without a
dedicated GPU (e.g. the ThinkPad T480, i7-8650U + UHD 620). Used when
`StationConfig.inference_backend == "openvino"` (the default).

Ultralytics loads an OpenVINO-exported model directory transparently
through the same `YOLO(...)` API used by `YoloPtDetector` — this adapter
only differs in what kind of `model_path` it expects (an
`*_openvino_model/` directory produced by `model.export(format="openvino")`,
not a `.pt` file). `openvino` itself is an extra dependency
(`pip install .[intel]`); Ultralytics imports it lazily only when it
detects an OpenVINO model is being loaded, so this module can still import
cleanly (via `ultralytics`, a base dependency) even without the `[intel]`
extra installed — it will only fail at `YoloOpenVINODetector(...)`
construction time if `openvino` truly isn't installed and an OpenVINO
model is loaded.
"""

from __future__ import annotations

import numpy as np
from ultralytics import YOLO

from src.core.rules_engine import Detection
from src.inference.base import Detector, ultralytics_result_to_detections


class YoloOpenVINODetector(Detector):
    """Runs an Ultralytics model exported to OpenVINO IR format."""

    def __init__(self, model_path: str, confidence: float = 0.25) -> None:
        self._model = YOLO(model_path, task="detect")
        self._confidence = confidence

    def detect(self, frame: np.ndarray) -> list[Detection]:
        results = self._model.predict(source=frame, conf=self._confidence, verbose=False)
        if not results:
            return []
        return ultralytics_result_to_detections(results[0])
