"""
test_config.py — Validate all JSON configuration files.
"""
import json
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "raspberry_pi" / "config"


def load(name):
    with open(CONFIG_DIR / name) as f:
        return json.load(f)


def test_classes_has_six_entries():
    data = load("classes.json")
    assert data["num_classes"] == 6
    assert len(data["classes"]) == 6


def test_class_ids_are_0_to_5():
    data = load("classes.json")
    ids = sorted(int(k) for k in data["classes"])
    assert ids == [0, 1, 2, 3, 4, 5]


def test_class_names_match_expected():
    expected = {"0": "flood", "1": "smoke", "2": "fire",
                "3": "debris", "4": "landslide", "5": "person"}
    data = load("classes.json")
    assert data["classes"] == expected


def test_priorities_has_all_classes():
    pdata = load("priorities.json")
    for cls in ["flood", "smoke", "fire", "debris", "landslide", "person"]:
        assert cls in pdata, f"Class '{cls}' missing from priorities.json"


def test_priorities_are_valid_levels():
    valid = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    pdata = load("priorities.json")
    for cls, level in pdata.items():
        assert level in valid, f"Invalid priority '{level}' for '{cls}'"


def test_person_is_critical():
    assert load("priorities.json")["person"] == "CRITICAL"


def test_model_json_has_required_keys():
    data = load("model.json")
    for k in ["weights", "backend", "imgsz", "confidence", "iou", "device"]:
        assert k in data, f"model.json missing key: {k}"


def test_model_json_no_absolute_paths():
    data = load("model.json")
    weights = data["weights"]
    for bad in ["D:\\", "C:\\", "C:/", "D:/", "/home", "Users"]:
        assert bad not in weights, f"Absolute path in model.json weights: {weights}"


def test_camera_json_has_required_keys():
    data = load("camera.json")
    for k in ["source", "width", "height", "fps"]:
        assert k in data


def test_telemetry_json_has_required_keys():
    data = load("telemetry.json")
    assert "enabled" in data
    assert "transport" in data


def test_class_config_module_validates():
    from raspberry_pi.inference.class_config import validate
    validate()  # Should not raise
