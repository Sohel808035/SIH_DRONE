"""
class_colors.py — BGR color palette for bounding box visualization.

Colours are in OpenCV BGR format.
Single authoritative definition — import from here only.
"""

CLASS_COLORS: dict[str, tuple[int, int, int]] = {
    "flood":     (255,  50,  50),   # Blue
    "smoke":     (180, 180, 180),   # Gray
    "fire":      (0,    60, 255),   # Red-Orange
    "debris":    (0,   200,   0),   # Green
    "landslide": (42,   42, 165),   # Brown
    "person":    (0,   255, 255),   # Yellow
}

DEFAULT_COLOR: tuple[int, int, int] = (255, 255, 255)  # White for unknown class