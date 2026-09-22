"""
test_parser.py — Unit tests for yolo_parser.parse_yolo().

Uses a synthetic Ultralytics-like fixture to avoid requiring a GPU or camera.
"""
import pytest
from types import SimpleNamespace
import torch


class _FakeBox:
    """Mimics a single Ultralytics bounding box."""
    def __init__(self, cls_id, conf, x1, y1, x2, y2):
        self.cls  = torch.tensor([float(cls_id)])
        self.conf = torch.tensor([conf])
        self.xyxy = torch.tensor([[float(x1), float(y1), float(x2), float(y2)]])


class _FakeResults:
    """Mimics an Ultralytics Results object."""
    def __init__(self, boxes_data, names):
        self.boxes = [_FakeBox(*b) for b in boxes_data]
        self.names = names


NAMES = {0: "flood", 1: "smoke", 2: "fire", 3: "debris", 4: "landslide", 5: "person"}


def make_results(boxes):
    return _FakeResults(boxes, NAMES)


from raspberry_pi.inference.yolo_parser import parse_yolo


def test_empty_detections():
    results = make_results([])
    assert parse_yolo(results) == []


def test_single_detection_keys():
    results = make_results([(2, 0.91, 120, 80, 250, 320)])
    dets = parse_yolo(results)
    assert len(dets) == 1
    d = dets[0]
    assert "class_id" in d
    assert "class" in d
    assert "confidence" in d
    assert "box" in d


def test_single_detection_values():
    results = make_results([(5, 0.88, 340, 190, 390, 320)])
    d = parse_yolo(results)[0]
    assert d["class_id"] == 5
    assert d["class"] == "person"
    assert abs(d["confidence"] - 0.88) < 0.001
    assert d["box"] == [340, 190, 390, 320]


def test_multi_detection():
    results = make_results([
        (2, 0.91, 120,  80, 250, 320),
        (1, 0.84,  80,  20, 300, 180),
        (5, 0.88, 340, 190, 390, 320),
    ])
    dets = parse_yolo(results)
    assert len(dets) == 3
    classes = [d["class"] for d in dets]
    assert "fire" in classes
    assert "smoke" in classes
    assert "person" in classes


def test_confidence_threshold_filters():
    results = make_results([
        (2, 0.91, 120, 80, 250, 320),
        (3, 0.10,  40, 40, 100, 100),  # Below threshold
    ])
    dets = parse_yolo(results, conf_threshold=0.50)
    assert len(dets) == 1
    assert dets[0]["class"] == "fire"


def test_box_is_list_of_four_ints():
    results = make_results([(0, 0.75, 10, 20, 50, 80)])
    d = parse_yolo(results)[0]
    assert len(d["box"]) == 4
    assert all(isinstance(v, int) for v in d["box"])
