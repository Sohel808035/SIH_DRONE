"""
draw_multihazard.py — Draw all hazard detections onto a frame.

Draws bounding boxes and labels for every detection in the list.
Uses class_colors.py as the single authoritative colour source.
"""
import cv2
from raspberry_pi.inference.class_colors import CLASS_COLORS, DEFAULT_COLOR


def draw_detections(frame, detections: list[dict]):
    """
    Draw all detections on a copy of the given frame.

    Args:
        frame: OpenCV BGR image (numpy array).
        detections: List of detection dicts with keys:
                    class_id, class, confidence, box [x1, y1, x2, y2].

    Returns:
        Annotated frame (same array, modified in place).
    """
    for det in detections:
        x1, y1, x2, y2 = det["box"]
        cls = det["class"]
        conf = det["confidence"]

        color = CLASS_COLORS.get(cls, DEFAULT_COLOR)

        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Draw label background + text
        label = f"{cls} {conf:.2f}"
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        label_y = max(th + baseline + 4, y1 - 4)
        cv2.rectangle(frame, (x1, label_y - th - baseline - 4), (x1 + tw, label_y), color, -1)
        cv2.putText(
            frame,
            label,
            (x1, label_y - baseline),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 0),   # Black text on coloured background
            2,
            cv2.LINE_AA,
        )

    return frame