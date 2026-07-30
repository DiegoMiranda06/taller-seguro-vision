"""Ultralytics `.pt` (PyTorch) detector — portable fallback for any laptop,
CPU or CUDA. Used when `StationConfig.inference_backend == "pt"`.

Generic against whatever `model_path` config points to — it does not
assume the custom multi-class model (Steps 8-9) exists yet. `ultralytics`
is imported at module level since it's a base dependency (not
hardware-restricted like `picamera2`/`gpiozero`/`pycoral`), but no model
weights are loaded until a `YoloPtDetector` is actually instantiated.
"""

from __future__ import annotations

import numpy as np
from ultralytics import YOLO

from src.core.rules_engine import Detection
from src.inference.base import Detector, ultralytics_result_to_detections


class YoloPtDetector(Detector):
    """Runs a `.pt` Ultralytics model on CPU or CUDA (if available)."""

    def __init__(self, model_path: str, device: str = "cpu", confidence: float = 0.25) -> None:
        self._model = YOLO(model_path)
        self._device = device
        self._confidence = confidence

    def detect(self, frame: np.ndarray) -> list[Detection]:
        results = self._model.predict(
            source=frame, device=self._device, conf=self._confidence, verbose=False
        )
        if not results:
            return []
        return ultralytics_result_to_detections(results[0])
