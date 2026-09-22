"""
event_manager.py — Generate and persist structured multi-hazard event records.

Each event can contain multiple detections from a single frame.
Priority is determined by the highest-priority hazard in the detections list.
"""
import json
from pathlib import Path
from datetime import datetime

# ── Path resolution (project-root independent) ───────────────────────────────
_THIS_DIR = Path(__file__).resolve().parent
_CONFIG_DIR = _THIS_DIR.parent / "config"
_STORAGE_DIR = _THIS_DIR.parent / "storage" / "events"

_PRIORITY_FILE = _CONFIG_DIR / "priorities.json"

# Priority ordering (higher index = higher priority)
_PRIORITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


def _load_priorities() -> dict[str, str]:
    if not _PRIORITY_FILE.exists():
        raise FileNotFoundError(f"Priority config not found: {_PRIORITY_FILE}")
    with open(_PRIORITY_FILE) as f:
        return json.load(f)


PRIORITY: dict[str, str] = _load_priorities()


def _highest_priority(detections: list[dict]) -> str:
    """Return the highest priority level across all detections."""
    best = "LOW"
    for det in detections:
        hazard = det.get("class", "")
        p = PRIORITY.get(hazard, "LOW")
        if _PRIORITY_ORDER.get(p, 0) > _PRIORITY_ORDER.get(best, 0):
            best = p
    return best


class EventManager:
    """
    Creates, saves, and manages hazard detection events.

    Each call to create_event() with detections from one frame generates
    a single event containing all detections from that frame.
    """

    def __init__(self, storage_dir: Path | None = None):
        self._storage_dir = Path(storage_dir) if storage_dir else _STORAGE_DIR
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._counter = self._load_counter()

    def _load_counter(self) -> int:
        """Start counter after the highest existing EVT_ folder."""
        existing = sorted(self._storage_dir.glob("EVT_*"))
        if not existing:
            return 1
        last = existing[-1].name  # e.g. EVT_000005
        try:
            return int(last.split("_")[1]) + 1
        except (IndexError, ValueError):
            return len(existing) + 1

    def create_event(
        self,
        detections: list[dict],
        frame=None,
        latitude=None,
        longitude=None,
        altitude=None,
    ) -> dict | None:
        """
        Create a structured multi-hazard event from a list of detections.

        Args:
            detections: List of dicts from yolo_parser.parse_yolo().
            frame: Optional numpy array — saved as evidence frame.jpg.
            latitude: GPS latitude (float or None).
            longitude: GPS longitude (float or None).
            altitude: GPS altitude (float or None).

        Returns:
            Event metadata dict, or None if detections is empty.
        """
        if not detections:
            return None

        event_id = f"EVT_{self._counter:06d}"
        self._counter += 1

        folder = self._storage_dir / event_id
        folder.mkdir(parents=True, exist_ok=True)

        priority = _highest_priority(detections)
        people_count = sum(1 for d in detections if d.get("class") == "person")

        image_path = str(folder / "frame.jpg")

        metadata = {
            "event_id": event_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "priority": priority,
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "detections": [
                {
                    "class_id": d.get("class_id", -1),
                    "class": d.get("class", ""),
                    "confidence": d.get("confidence", 0.0),
                    "box": d.get("box", []),
                }
                for d in detections
            ],
            "people_count": people_count,
            "image_path": image_path,
        }

        # Save metadata JSON
        with open(folder / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)

        # Optionally save the annotated evidence frame
        if frame is not None:
            try:
                import cv2
                cv2.imwrite(image_path, frame)
            except Exception as e:
                print(f"[EventManager] Warning: could not save frame: {e}")

        return metadata


# ── CLI smoke test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    manager = EventManager()
    event = manager.create_event(
        detections=[
            {"class_id": 2, "class": "fire",   "confidence": 0.91, "box": [120,  80, 250, 320]},
            {"class_id": 1, "class": "smoke",  "confidence": 0.84, "box": [ 80,  20, 300, 180]},
            {"class_id": 5, "class": "person", "confidence": 0.88, "box": [340, 190, 390, 320]},
        ]
    )
    print(json.dumps(event, indent=4))