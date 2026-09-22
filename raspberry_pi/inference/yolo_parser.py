"""
yolo_parser.py — Convert raw Ultralytics YOLO results into a clean list of detection dicts.

Each detection:
    {
        "class_id": int,
        "class": str,
        "confidence": float,
        "box": [x1, y1, x2, y2]
    }
"""


def parse_yolo(results, conf_threshold: float = 0.0) -> list[dict]:
    """
    Parse Ultralytics detection results into a common format.

    Args:
        results: A single Ultralytics Results object (not a list).
        conf_threshold: Minimum confidence to include a detection (0.0 = all).

    Returns:
        List of detection dicts.
    """
    detections = []
    names = results.names  # {0: 'flood', 1: 'smoke', ...}

    if results.boxes is None:
        return detections

    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])

        if conf < conf_threshold:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        detections.append({
            "class_id": cls_id,
            "class": names[cls_id],
            "confidence": round(conf, 4),
            "box": [x1, y1, x2, y2],
        })

    return detections