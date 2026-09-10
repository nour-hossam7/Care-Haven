from __future__ import annotations

from io import BytesIO

from PIL import Image

from ai.vision.preprocessing import ImageLoadError, load_image, prepare_image
from ai.vision.quality import QualityConfig, assess_image_quality


def _png_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_preprocessing_loads_valid_image_and_normalizes():
    image = load_image(_png_bytes(Image.new("RGB", (20, 10), "red")))
    normalized = prepare_image(image, size=(10, 5), normalize=True)
    assert image.mode == "RGB"
    assert normalized.shape == (5, 10, 3)


def test_preprocessing_rejects_corrupted_and_unsupported_input():
    for source in (b"corrupted", object()):
        try:
            load_image(source)
        except ImageLoadError:
            continue
        raise AssertionError("Invalid input should raise ImageLoadError")


def test_quality_accepts_detailed_image_and_rejects_low_quality_image():
    detailed = Image.effect_noise((400, 300), 100).convert("RGB")
    acceptable = assess_image_quality(_png_bytes(detailed))
    poor = assess_image_quality(_png_bytes(Image.new("RGB", (20, 20), "white")))
    assert acceptable["is_acceptable"] is True
    assert poor["is_acceptable"] is False


def test_quality_handles_corrupted_image_without_raising():
    result = assess_image_quality(b"corrupted", QualityConfig())
    assert result["is_acceptable"] is False
    assert result["quality_score"] == 0.0
