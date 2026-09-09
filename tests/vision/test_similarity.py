from PIL import Image
import pytest

from ai.vision.preprocessing import ImageLoadError
from ai.vision.similarity import SimilarityConfig, compare_images


def test_identical_images_are_similar():
    image = Image.new("RGB", (40, 40), "red")
    result = compare_images(image, image)
    assert result == {"similarity_score": 1.0, "is_similar": True}


def test_different_images_produce_valid_result():
    result = compare_images(Image.new("RGB", (40, 40), "black"), Image.new("RGB", (40, 40), "white"))
    assert 0.0 <= result["similarity_score"] <= 1.0
    assert isinstance(result["is_similar"], bool)


def test_threshold_is_independent_from_score():
    image = Image.new("RGB", (40, 40), "blue")
    assert compare_images(image, image, SimilarityConfig(threshold=1.0))["is_similar"]
    with pytest.raises(ValueError):
        compare_images(image, image, SimilarityConfig(threshold=1.1))


def test_invalid_image_raises_controlled_error():
    with pytest.raises(ImageLoadError):
        compare_images(b"not an image", b"also not an image")
