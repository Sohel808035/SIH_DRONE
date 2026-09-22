"""
raspberry_pi/main.py — Raspberry Pi Edge AI Entry Point

AI Multi-Hazard Disaster Detection System
Smart India Hackathon 2026

Usage:
    python -m raspberry_pi.main --help
    python -m raspberry_pi.main --source 0 --device cpu --show
    python -m raspberry_pi.main --source path/to/video.mp4 --save
    python -m raspberry_pi.main --source path/to/image.jpg
"""
import argparse
import json
import sys
from pathlib import Path

# ── Project root (two levels up from this file: raspberry_pi/main.py) ─────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_config(name: str) -> dict:
    """Load a JSON config from raspberry_pi/config/."""
    path = PROJECT_ROOT / "raspberry_pi" / "config" / name
    if not path.exists():
        print(f"[ERROR] Config file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def _resolve_model_path(model_arg: str | None, model_cfg: dict) -> Path:
    """Resolve model weights path — CLI arg > config > default."""
    raw = model_arg or model_cfg.get("weights", "models/best.pt")
    p = Path(raw)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    return p


def _select_device(device_arg: str, model_cfg: dict) -> str:
    """Resolve compute device — CLI arg overrides config."""
    device = device_arg or model_cfg.get("device", "auto")
    if device == "auto":
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"
    return device


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m raspberry_pi.main",
        description=(
            "AI Multi-Hazard Drone Detection System — YOLO11n Edge Inference\n"
            "Detects: flood, smoke, fire, debris, landslide, person"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--source",
        default=None,
        help="Camera index (e.g. 0), video file, or image path. "
             "Overrides camera.json source if provided.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Path to model weights (.pt or .onnx). Default: models/best.pt",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=None,
        help="Confidence threshold (0–1). Default from model.json.",
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=None,
        help="IoU threshold for NMS (0–1). Default from model.json.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=None,
        help="Inference image size. Default from model.json.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Compute device: 'cpu', 'cuda', '0', or 'auto'. Default from model.json.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display annotated frames in a window (requires display/GUI).",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save annotated output video/images.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Stop after N frames (useful for testing). Default: run until stream ends.",
    )
    return parser


def main():
    parser = build_argparser()
    args = parser.parse_args()

    # ── Load config ────────────────────────────────────────────────────────────
    model_cfg = _load_config("model.json")
    camera_cfg = _load_config("camera.json")
    telemetry_cfg = _load_config("telemetry.json")

    # ── Validate class mapping ─────────────────────────────────────────────────
    print("[INFO] Validating class configuration...")
    try:
        from raspberry_pi.inference.class_config import validate, CLASS_NAMES
        validate()
        print(f"[INFO] Class mapping OK: {CLASS_NAMES}")
    except Exception as e:
        print(f"[ERROR] Class config validation failed: {e}", file=sys.stderr)
        sys.exit(1)

    # ── Resolve model path ─────────────────────────────────────────────────────
    model_path = _resolve_model_path(args.model, model_cfg)
    if not model_path.exists():
        print(
            f"[ERROR] Model not found: {model_path}\n"
            "  → Place models/best.pt in the repository root.\n"
            "  → Or set 'weights' in raspberry_pi/config/model.json.",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"[INFO] Model: {model_path}")

    # ── Resolve inference parameters ───────────────────────────────────────────
    conf  = args.conf   if args.conf   is not None else model_cfg.get("confidence", 0.20)
    iou   = args.iou    if args.iou    is not None else model_cfg.get("iou",        0.45)
    imgsz = args.imgsz  if args.imgsz  is not None else model_cfg.get("imgsz",      640)
    device = _select_device(args.device or "", model_cfg)
    show  = args.show  or camera_cfg.get("display", False)
    save  = args.save  or camera_cfg.get("save_output", False)

    # ── Resolve source ─────────────────────────────────────────────────────────
    raw_source = args.source
    if raw_source is None:
        raw_source = camera_cfg.get("source", 0)
    # If it's a digit string, convert to int for OpenCV camera index
    if isinstance(raw_source, str) and raw_source.isdigit():
        raw_source = int(raw_source)
    elif isinstance(raw_source, str):
        p = Path(raw_source)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        raw_source = str(p)

    print(f"[INFO] Source : {raw_source}")
    print(f"[INFO] Device : {device}   Conf: {conf}   IoU: {iou}   imgsz: {imgsz}")

    # ── Load model ─────────────────────────────────────────────────────────────
    print("[INFO] Loading model...")
    from raspberry_pi.inference.live_inference import load_model, run_inference_loop
    model = load_model(model_path, device=device)
    print("[INFO] Model loaded.")

    # ── Initialise components ──────────────────────────────────────────────────
    from raspberry_pi.event_engine.event_manager import EventManager
    from raspberry_pi.event_engine.tracker import DetectionTracker
    from raspberry_pi.communication.interface import ConsoleTransport, NullTransport
    from raspberry_pi.communication.gps_provider import NullGPSProvider

    event_manager = EventManager()
    tracker = DetectionTracker()
    gps = NullGPSProvider()

    # Choose transport
    transport_name = telemetry_cfg.get("transport", "null")
    transport = ConsoleTransport() if transport_name == "console" else NullTransport()
    telemetry_enabled = telemetry_cfg.get("enabled", False)

    print(f"[INFO] Telemetry: {'console' if telemetry_enabled and transport_name == 'console' else 'disabled'}")
    print("[INFO] Starting inference loop — press Ctrl+C to stop.\n")

    # ── Inference callback ─────────────────────────────────────────────────────
    def on_detections(frame, detections):
        if not detections:
            return

        ready = tracker.update(detections)
        if not ready:
            return

        lat, lon, alt = gps.get_position()
        event = event_manager.create_event(
            detections=ready,
            frame=frame,
            latitude=lat,
            longitude=lon,
            altitude=alt,
        )
        if event:
            print(f"[EVENT] {event['event_id']} | {event['priority']} | "
                  f"{len(event['detections'])} detection(s)")
            if telemetry_enabled:
                transport.send_event(event)

    # ── Run ────────────────────────────────────────────────────────────────────
    try:
        run_inference_loop(
            model=model,
            source=raw_source,
            conf=conf,
            iou=iou,
            imgsz=imgsz,
            device=device,
            show=show,
            save=save,
            on_detections=on_detections,
            max_frames=args.max_frames,
        )
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        transport.close()

    print("[INFO] Done.")


if __name__ == "__main__":
    main()
