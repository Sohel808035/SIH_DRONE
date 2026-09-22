"""
tracker.py — Temporal persistence and false-positive reduction.

This is a deterministic frame-count–based tracker. It is an engineering
heuristic — it does NOT guarantee zero false positives.

Rules are loaded from raspberry_pi/config/priorities.json and the
hard-coded trigger_frames table (which mirrors event_rules.md).
"""
from pathlib import Path
import json
import time

# Default consecutive-frame requirement before an event fires
_TRIGGER_FRAMES: dict[str, int] = {
    "flood":     2,
    "fire":      3,
    "smoke":     5,
    "debris":    3,
    "landslide": 2,
    "person":    1,  # person triggers immediately
}

# Cooldown in seconds — suppress duplicate events for the same class
_COOLDOWN_SECONDS: dict[str, float] = {
    "flood":     10.0,
    "fire":       8.0,
    "smoke":     15.0,
    "debris":    20.0,
    "landslide": 10.0,
    "person":     5.0,
}


class DetectionTracker:
    """
    Tracks consecutive detections per class and suppresses duplicate events.

    Usage:
        tracker = DetectionTracker()
        for each frame:
            ready = tracker.update(detections)
            if ready:
                event_manager.create_event(ready)
    """

    def __init__(self):
        self._counts: dict[str, int] = {}
        self._last_event_time: dict[str, float] = {}

    def update(self, detections: list[dict]) -> list[dict]:
        """
        Accept raw detections from one frame and return only those that
        have met their consecutive-frame threshold AND are not in cooldown.

        Args:
            detections: Output of yolo_parser.parse_yolo().

        Returns:
            Filtered list of detections ready to generate an event.
            May be empty (frame does not yet trigger an event).
        """
        detected_classes = {d["class"] for d in detections}

        # Increment counters for detected classes; reset others
        all_classes = set(_TRIGGER_FRAMES.keys())
        for cls in all_classes:
            if cls in detected_classes:
                self._counts[cls] = self._counts.get(cls, 0) + 1
            else:
                self._counts[cls] = 0  # Reset streak

        now = time.monotonic()
        ready: list[dict] = []

        for det in detections:
            cls = det["class"]
            threshold = _TRIGGER_FRAMES.get(cls, 3)
            cooldown = _COOLDOWN_SECONDS.get(cls, 10.0)
            last_time = self._last_event_time.get(cls, 0.0)

            streak = self._counts.get(cls, 0)
            elapsed = now - last_time

            if streak >= threshold and elapsed >= cooldown:
                ready.append(det)
                self._last_event_time[cls] = now  # Reset cooldown

        return ready

    def reset(self):
        """Reset all counters and cooldowns."""
        self._counts.clear()
        self._last_event_time.clear()
