"""
live_inference.py — Inference loop for running YOLO11n on a camera, video, or image.

This module provides the core inference loop. It is called by main.py.
"""
import cv2
from pathlib import Path
from ultralytics import YOLO

from raspberry_pi.inference.yolo_parser import parse_yolo
from raspberry_pi.inference.draw_multihazard import draw_detections


def load_model(weights_path: str | Path, device: str = "cpu"):
    """
    Load a YOLO model from a .pt or .onnx weights file.

    Args:
        weights_path: Relative or absolute path to weights file.
        device: 'cpu', 'cuda', '0', or 'auto'.

    Returns:
        Loaded YOLO model.
    """
    weights_path = Path(weights_path)
    if not weights_path.exists():
        raise FileNotFoundError(
            f"Model weights not found: {weights_path}\n"
            "Place models/best.pt in the repository root or update raspberry_pi/config/model.json."
        )
    model = YOLO(str(weights_path))
    return model


def run_inference_loop(
    model,
    source,
    conf: float = 0.20,
    iou: float = 0.45,
    imgsz: int = 640,
    device: str = "cpu",
    show: bool = False,
    save: bool = False,
    on_detections=None,
    max_frames: int = None,
):
    """
    Run the real-time inference loop.

    Args:
        model: Loaded YOLO model.
        source: Camera index (int), video path (str/Path), or image path.
        conf: Confidence threshold.
        iou: IoU threshold for NMS.
        imgsz: Inference image size.
        device: Compute device.
        show: Whether to display the annotated frame in a window.
        save: Whether to save annotated output.
        on_detections: Optional callback(frame, detections) called for each frame.
        max_frames: Stop after this many frames (None = run until stream ends or user stops).

    Returns:
        None
    """
    cap = None
    is_camera = isinstance(source, int)
    is_video = isinstance(source, (str, Path)) and Path(str(source)).suffix.lower() in (
        ".mp4", ".avi", ".mov", ".mkv"
    )

    if is_camera or is_video:
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            if is_camera:
                raise RuntimeError(
                    f"Cannot open camera index {source}.\n"
                    "Check that a camera is connected and not in use by another application."
                )
            else:
                raise RuntimeError(f"Cannot open video file: {source}")

    frame_count = 0
    try:
        while True:
            if cap is not None:
                ret, frame = cap.read()
                if not ret:
                    break
            else:
                # Single image mode
                frame = cv2.imread(str(source))
                if frame is None:
                    raise RuntimeError(f"Cannot read image: {source}")

            # Run YOLO inference
            results_list = model.predict(
                frame,
                conf=conf,
                iou=iou,
                imgsz=imgsz,
                device=device,
                verbose=False,
            )

            # Parse detections from the first (only) result
            detections = parse_yolo(results_list[0])

            # Annotate frame
            annotated = draw_detections(frame.copy(), detections)

            # Deliver to callback (event engine, main loop)
            if on_detections:
                on_detections(annotated, detections)

            if show:
                cv2.imshow("Detection_Model — Multi-Hazard", annotated)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                break

            # Single image: process once and stop
            if not is_camera and not is_video:
                break

    finally:
        if cap is not None:
            cap.release()
        if show:
            cv2.destroyAllWindows()
