"""
class_config.py — Single authoritative runtime class mapping.

Loaded from raspberry_pi/config/classes.json.
All other modules must import from here instead of defining their own class lists.
"""
import json
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "classes.json"


def _load() -> dict:
    if not _CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Class config not found: {_CONFIG_PATH}\n"
            "Expected: raspberry_pi/config/classes.json"
        )
    with open(_CONFIG_PATH, "r") as f:
        data = json.load(f)
    return data


_data = _load()

# Integer-keyed mapping:  {0: 'flood', 1: 'smoke', ...}
CLASS_NAMES: dict[int, str] = {int(k): v for k, v in _data["classes"].items()}

# Reverse mapping:  {'flood': 0, 'smoke': 1, ...}
CLASS_IDS: dict[str, int] = {v: k for k, v in CLASS_NAMES.items()}

NUM_CLASSES: int = _data["num_classes"]


def validate():
    """Raise ValueError if class config is inconsistent."""
    assert NUM_CLASSES == 6, f"Expected 6 classes, got {NUM_CLASSES}"
    assert len(CLASS_NAMES) == 6, f"Expected 6 class names, got {len(CLASS_NAMES)}"
    expected = {0: "flood", 1: "smoke", 2: "fire", 3: "debris", 4: "landslide", 5: "person"}
    for cid, name in expected.items():
        if CLASS_NAMES.get(cid) != name:
            raise ValueError(
                f"Class ID {cid}: expected '{name}', got '{CLASS_NAMES.get(cid)}'"
            )


validate()
