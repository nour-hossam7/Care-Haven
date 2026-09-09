"""A replaceable adapter around optional Ultralytics YOLO inference."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any, Protocol

from PIL import Image, ImageDraw

from .preprocessing import ImageSource, load_image


@dataclass(frozen=True)
class Detection:
    """Model-neutral representation of one object detection."""
    class_name: str
    confidence: float
    bbox: list[float]


class InferenceModel(Protocol):
    def __call__(self, image: Image.Image, **kwargs: Any) -> Any: ...


class YoloDetector:
    """Lazy YOLO adapter that keeps Ultralytics result objects out of callers."""
    def __init__(self, model_path: str | None = None, confidence_threshold: float | None = None, iou_threshold: float | None = None, model: InferenceModel | None = None) -> None:
        self.model_path = model_path or os.getenv("YOLO_MODEL_PATH", "yolo11n.pt")
        self.confidence_threshold = confidence_threshold if confidence_threshold is not None else float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", "0.25"))
        self.iou_threshold = iou_threshold if iou_threshold is not None else float(os.getenv("YOLO_IOU_THRESHOLD", "0.45"))
        self._model = model

    def _get_model(self) -> InferenceModel:
        if self._model is None:
            try:
                from ultralytics import YOLO
            except ImportError as exc:
                raise RuntimeError("YOLO inference requires the optional 'ultralytics' dependency.") from exc
            self._model = YOLO(self.model_path)
        return self._model

    def detect(self, source: ImageSource) -> dict[str, list[dict[str, str | float | list[float]]] | int]:
        """Run configured inference and return a stable, JSON-ready detection payload."""
        image = load_image(source)
        results = self._get_model()(image, conf=self.confidence_threshold, iou=self.iou_threshold)
        detections: list[Detection] = []
        for result in results:
            names = result.names
            for box in result.boxes:
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                name = names[class_id] if isinstance(names, (list, tuple)) else names.get(class_id, str(class_id))
                detections.append(Detection(str(name), confidence, [float(item) for item in box.xyxy[0].tolist()]))
        return {"detections": [asdict(item) for item in detections], "num_detections": len(detections)}


def visualize_detections(source: ImageSource, detections: list[Detection | dict[str, Any]]) -> Image.Image:
    """Draw supplied detections on an image copy and return it for any UI framework."""
    image = load_image(source).copy()
    draw = ImageDraw.Draw(image)
    for raw in detections:
        item = raw if isinstance(raw, Detection) else Detection(**raw)
        x1, y1, x2, y2 = item.bbox
        draw.rectangle((x1, y1, x2, y2), outline="#dc2626", width=3)
        draw.text((x1 + 3, max(0, y1 - 14)), f"{item.class_name} {item.confidence:.0%}", fill="#dc2626")
    return image
