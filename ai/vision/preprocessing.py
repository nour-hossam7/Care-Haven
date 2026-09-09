"""Safe, model-agnostic image loading and preparation helpers."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO, TypeAlias

import numpy as np
from PIL import Image, UnidentifiedImageError

ImageSource: TypeAlias = str | Path | bytes | BinaryIO | Image.Image
SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}


class ImageLoadError(ValueError):
    """Raised when a supplied image cannot be opened safely."""


def load_image(source: ImageSource) -> Image.Image:
    """Load *source* as an independent RGB image without altering the source."""
    try:
        if isinstance(source, Image.Image):
            image = source.copy()
        elif isinstance(source, (str, Path)):
            path = Path(source)
            if not path.is_file():
                raise ImageLoadError(f"Image file does not exist: {path}")
            with Image.open(path) as opened:
                opened.verify()
            image = Image.open(path)
        elif isinstance(source, bytes):
            image = Image.open(BytesIO(source))
        else:
            image = Image.open(source)
        image.load()
        if image.format and image.format.upper() not in SUPPORTED_FORMATS:
            raise ImageLoadError("Unsupported image format. Use JPG, PNG, or WEBP.")
        if image.width < 1 or image.height < 1:
            raise ImageLoadError("Image dimensions must be positive.")
        image_format = image.format
        rgb = image.convert("RGB")
        rgb.format = image_format
        return rgb
    except ImageLoadError:
        raise
    except (OSError, UnidentifiedImageError, ValueError) as exc:
        raise ImageLoadError("The uploaded file is not a readable image.") from exc


def prepare_image(source: ImageSource, size: tuple[int, int] | None = None, normalize: bool = False) -> Image.Image | np.ndarray:
    """Return RGB image resized to *size*, or a 0--1 float array when normalized."""
    image = load_image(source)
    if size is not None:
        if size[0] < 1 or size[1] < 1:
            raise ValueError("Image dimensions must be positive.")
        image = image.resize(size, Image.Resampling.LANCZOS)
    if normalize:
        return np.asarray(image, dtype=np.float32) / 255.0
    return image


def get_image_metadata(source: ImageSource) -> dict[str, int | str | None]:
    """Return display-safe image metadata, including file size when known."""
    image = load_image(source)
    file_size: int | None = None
    image_format = image.format or "Unknown"
    if isinstance(source, (str, Path)):
        file_size = Path(source).stat().st_size
    elif isinstance(source, bytes):
        file_size = len(source)
    return {"width": image.width, "height": image.height, "format": image_format, "channels": len(image.getbands()), "file_size": file_size}
