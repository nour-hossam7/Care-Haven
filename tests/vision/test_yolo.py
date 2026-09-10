from PIL import Image
import pytest

from ai.vision.preprocessing import ImageLoadError
from ai.vision.yolo import YoloDetector, visualize_detections


class FakeBox:
    conf, cls = [0.91], [0]
    class XYXY:
        def tolist(self): return [1, 2, 20, 22]
    xyxy = [XYXY()]


class FakeResult:
    names, boxes = {0: "person"}, [FakeBox()]


class FakeModel:
    def __call__(self, image, **kwargs):
        assert kwargs["conf"] == 0.25
        return [FakeResult()]


class EmptyResult:
    names, boxes = {}, []


class EmptyModel:
    def __call__(self, image, **kwargs):
        return [EmptyResult()]


def test_detection_result_is_model_neutral():
    result = YoloDetector(model=FakeModel()).detect(Image.new("RGB", (30, 30)))
    assert result["num_detections"] == 1
    assert result["detections"][0] == {"class_name": "person", "confidence": 0.91, "bbox": [1.0, 2.0, 20.0, 22.0]}


def test_invalid_input_is_controlled():
    with pytest.raises(ImageLoadError):
        YoloDetector(model=FakeModel()).detect(b"invalid")


def test_empty_model_result_returns_no_detections():
    result = YoloDetector(model=EmptyModel()).detect(Image.new("RGB", (30, 30)))
    assert result == {"detections": [], "num_detections": 0}


def test_visualization_returns_copy():
    source = Image.new("RGB", (30, 30), "white")
    visual = visualize_detections(source, [{"class_name": "person", "confidence": 0.9, "bbox": [1, 1, 20, 20]}])
    assert visual is not source
    assert visual.getpixel((1, 1)) != source.getpixel((1, 1))
