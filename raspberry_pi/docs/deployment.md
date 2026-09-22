# Raspberry Pi Deployment Guide

## 1. Prepare Raspberry Pi OS

- Use **Raspberry Pi OS 64-bit** (Bullseye or Bookworm)
- Python 3.11+ (comes with Bookworm)
- Enable camera interface if using CSI camera:
  ```bash
  sudo raspi-config  # Interface Options → Camera
  ```

---

## 2. Clone Repository

```bash
git clone https://github.com/Sohel808035/Detection_Model.git
cd Detection_Model
```

---

## 3. Create Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements-rpi.txt
```

> First install may take 10–20 minutes on Raspberry Pi 4B (PyTorch build).

---

## 5. Verify Model

```bash
python3 -c "
from ultralytics import YOLO
m = YOLO('models/best.pt')
print(m.names)
"
```

**Expected output:**
```
{0: 'flood', 1: 'smoke', 2: 'fire', 3: 'debris', 4: 'landslide', 5: 'person'}
```

---

## 6. Configure Model

Edit `raspberry_pi/config/model.json`:

```json
{
  "weights": "models/best.pt",
  "backend": "auto",
  "imgsz": 320,
  "confidence": 0.25,
  "iou": 0.45,
  "device": "cpu"
}
```

> **Tip:** Use `imgsz: 320` on Raspberry Pi for better performance.

---

## 7. Configure Camera

Edit `raspberry_pi/config/camera.json`:

```json
{
  "source": 0,
  "width": 640,
  "height": 480,
  "fps": 30,
  "display": false,
  "save_output": false
}
```

- `"source": 0` — first USB camera
- `"source": "/dev/video0"` — explicit camera device
- `"source": "path/to/video.mp4"` — video file for testing

---

## 8. Test with a Video File (No Camera Required)

```bash
python -m raspberry_pi.main --source /path/to/test_video.mp4 --device cpu --max-frames 50
```

---

## 9. Run with USB Camera (Headless)

```bash
python -m raspberry_pi.main --source 0 --device cpu
```

Events are saved to `raspberry_pi/storage/events/`.

---

## 10. Run with Display (Requires Monitor)

```bash
python -m raspberry_pi.main --source 0 --device cpu --show
```

Press `q` to quit.

---

## 11. Enable Console Telemetry (for debugging)

Edit `raspberry_pi/config/telemetry.json`:

```json
{
  "enabled": true,
  "transport": "console"
}
```

Events will be printed to stdout as JSON.

---

## 12. View Generated Events

```bash
ls raspberry_pi/storage/events/
cat raspberry_pi/storage/events/EVT_000001/metadata.json
```

---

## 13. Next: GPS Integration

See `raspberry_pi/docs/hardware_integration.md` → GPS section.

## 14. Next: Telemetry Integration

See `raspberry_pi/docs/hardware_integration.md` → Telemetry section.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: ultralytics` | Run `pip install -r requirements-rpi.txt` |
| Inference is very slow | Set `imgsz: 320` in `model.json` |
| Camera not opening | Check `source` in `camera.json`; try `ls /dev/video*` |
| `libGL` error on headless Pi | Install `opencv-python-headless` instead of `opencv-python` |
