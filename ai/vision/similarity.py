"""Deterministic perceptual image similarity utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .preprocessing import ImageSource, load_image


@dataclass(frozen=True)
class SimilarityConfig:
    """Perceptual-vector settings and decision threshold (separate from the score)."""
    threshold: float = 0.85
    image_size: tuple[int, int] = (32, 32)


def _embedding(source: ImageSource, size: tuple[int, int]) -> np.ndarray:
    image = load_image(source).convert("L").resize(size)
    return np.asarray(image, dtype=np.float64).reshape(-1) / 255.0


def compare_images(image1: ImageSource, image2: ImageSource, config: SimilarityConfig | None = None) -> dict[str, float | bool]:
    """Compare two images using normalized grayscale perceptual vectors.

    The 0--1 score is one minus normalized mean absolute pixel distance after
    resizing; callers can set the documented ``threshold`` independently.
    """
    config = config or SimilarityConfig()
    if not 0.0 <= config.threshold <= 1.0:
        raise ValueError("Similarity threshold must be between 0 and 1.")
    first, second = _embedding(image1, config.image_size), _embedding(image2, config.image_size)
    similarity = float(np.clip(1.0 - np.mean(np.abs(first - second)), 0.0, 1.0))
    return {"similarity_score": round(similarity, 4), "is_similar": similarity >= config.threshold}
