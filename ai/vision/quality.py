"""Configurable, lightweight image quality checks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image

from .preprocessing import ImageSource, load_image


@dataclass(frozen=True)
class QualityConfig:
    """Thresholds for acceptable evidence images; values are intentionally conservative."""
    min_width: int = 320
    min_height: int = 240
    min_laplacian_variance: float = 20.0
    min_mean_brightness: float = 25.0
    max_mean_brightness: float = 235.0


def _blur_score(gray: np.ndarray) -> float:
    """Approximate Laplacian variance using NumPy, without requiring OpenCV."""
    center = gray[1:-1, 1:-1]
    laplacian = -4 * center + gray[:-2, 1:-1] + gray[2:, 1:-1] + gray[1:-1, :-2] + gray[1:-1, 2:]
    return float(np.var(laplacian))


def assess_image_quality(source: ImageSource, config: QualityConfig | None = None) -> dict[str, bool | float | list[str]]:
    """Assess resolution, brightness, and blur, returning reasons without raising on invalid input."""
    config = config or QualityConfig()
    try:
        image: Image.Image = load_image(source)
    except ValueError as exc:
        return {"is_acceptable": False, "quality_score": 0.0, "issues": [str(exc)]}
    gray = np.asarray(image.convert("L"), dtype=np.float32)
    issues: list[str] = []
    if image.width < config.min_width or image.height < config.min_height:
        issues.append("Image resolution is too low")
    brightness = float(gray.mean())
    if brightness < config.min_mean_brightness:
        issues.append("Image is too dark")
    elif brightness > config.max_mean_brightness:
        issues.append("Image is too bright")
    blur = _blur_score(gray) if min(gray.shape) >= 3 else 0.0
    if blur < config.min_laplacian_variance:
        issues.append("Image is heavily blurred or lacks visible detail")
    score = max(0.0, 1.0 - 0.25 * len(issues))
    return {"is_acceptable": not issues, "quality_score": round(score, 3), "issues": issues}
