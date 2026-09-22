"""
test_event_manager.py — Unit tests for EventManager.
"""
import json
import pytest
from pathlib import Path
import tempfile

from raspberry_pi.event_engine.event_manager import EventManager


@pytest.fixture
def tmp_manager(tmp_path):
    """EventManager using a temporary directory for clean test isolation."""
    return EventManager(storage_dir=tmp_path)


SINGLE_DETECTION = [
    {"class_id": 2, "class": "fire", "confidence": 0.91, "box": [120, 80, 250, 320]},
]

MULTI_DETECTIONS = [
    {"class_id": 2, "class": "fire",   "confidence": 0.91, "box": [120,  80, 250, 320]},
    {"class_id": 1, "class": "smoke",  "confidence": 0.84, "box": [ 80,  20, 300, 180]},
    {"class_id": 5, "class": "person", "confidence": 0.88, "box": [340, 190, 390, 320]},
]


def test_empty_detections_returns_none(tmp_manager):
    assert tmp_manager.create_event([]) is None


def test_single_event_has_event_id(tmp_manager):
    event = tmp_manager.create_event(SINGLE_DETECTION)
    assert event["event_id"].startswith("EVT_")


def test_single_event_metadata_file_created(tmp_manager):
    event = tmp_manager.create_event(SINGLE_DETECTION)
    folder = Path(event["image_path"]).parent
    meta = folder / "metadata.json"
    assert meta.exists()


def test_single_event_metadata_json_valid(tmp_manager):
    event = tmp_manager.create_event(SINGLE_DETECTION)
    folder = Path(event["image_path"]).parent
    with open(folder / "metadata.json") as f:
        loaded = json.load(f)
    assert loaded["event_id"] == event["event_id"]
    assert len(loaded["detections"]) == 1


def test_multi_detection_event_preserves_all(tmp_manager):
    event = tmp_manager.create_event(MULTI_DETECTIONS)
    assert len(event["detections"]) == 3
    classes = [d["class"] for d in event["detections"]]
    assert "fire" in classes
    assert "smoke" in classes
    assert "person" in classes


def test_multi_detection_priority_is_critical(tmp_manager):
    """Person is CRITICAL — event priority should be CRITICAL."""
    event = tmp_manager.create_event(MULTI_DETECTIONS)
    assert event["priority"] == "CRITICAL"


def test_people_count_correct(tmp_manager):
    event = tmp_manager.create_event(MULTI_DETECTIONS)
    assert event["people_count"] == 1


def test_no_people_count_zero(tmp_manager):
    det = [{"class_id": 2, "class": "fire", "confidence": 0.9, "box": [0,0,10,10]}]
    event = tmp_manager.create_event(det)
    assert event["people_count"] == 0


def test_gps_null_by_default(tmp_manager):
    event = tmp_manager.create_event(SINGLE_DETECTION)
    assert event["latitude"] is None
    assert event["longitude"] is None
    assert event["altitude"] is None


def test_event_counter_increments(tmp_manager):
    e1 = tmp_manager.create_event(SINGLE_DETECTION)
    e2 = tmp_manager.create_event(SINGLE_DETECTION)
    id1 = int(e1["event_id"].split("_")[1])
    id2 = int(e2["event_id"].split("_")[1])
    assert id2 == id1 + 1


def test_timestamp_present(tmp_manager):
    event = tmp_manager.create_event(SINGLE_DETECTION)
    assert "timestamp" in event
    assert len(event["timestamp"]) > 0
