"""
test_paths.py — Verify that all critical paths resolve correctly
regardless of working directory.
"""
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_model_weights_exist():
    p = PROJECT_ROOT / "models" / "best.pt"
    assert p.exists(), f"models/best.pt not found at {p}"


def test_model_metadata_exists():
    p = PROJECT_ROOT / "models" / "model_metadata.json"
    assert p.exists(), f"models/model_metadata.json not found at {p}"


def test_config_dir_has_all_required_files():
    config = PROJECT_ROOT / "raspberry_pi" / "config"
    required = ["classes.json", "priorities.json", "event_schema.json",
                "model.json", "camera.json", "telemetry.json"]
    for fname in required:
        p = config / fname
        assert p.exists(), f"Config file missing: raspberry_pi/config/{fname}"


def test_inference_modules_exist():
    base = PROJECT_ROOT / "raspberry_pi" / "inference"
    for fname in ["class_config.py", "class_colors.py", "yolo_parser.py",
                  "draw_multihazard.py", "live_inference.py"]:
        p = base / fname
        assert p.exists(), f"Inference module missing: {fname}"


def test_event_engine_modules_exist():
    base = PROJECT_ROOT / "raspberry_pi" / "event_engine"
    for fname in ["event_manager.py", "tracker.py"]:
        assert (base / fname).exists()


def test_communication_modules_exist():
    base = PROJECT_ROOT / "raspberry_pi" / "communication"
    for fname in ["interface.py", "gps_provider.py"]:
        assert (base / fname).exists()


def test_main_entry_point_exists():
    assert (PROJECT_ROOT / "raspberry_pi" / "main.py").exists()
