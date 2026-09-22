# Detection_Model

## AI Multi-Hazard Drone Detection Model (SIH 2026)

An Edge AI computer vision pipeline for **Autonomous Disaster Response Drones**. The project uses **YOLO11n** to detect multiple disaster hazards from aerial drone footage and generates geo-tagged rescue events on a Raspberry Pi 4B.

### Project Objective

Instead of only streaming live video, the drone understands the scene in real time by detecting:

* 🌊 Flood

* 🔥 Fire

* 🌫 Smoke

* 🧱 Debris

* ⛰ Landslide

* 👤 Person (Survivor)

The final goal is onboard AI inference → event generation → telemetry → ground station dashboard.

---

## Current Status

| Module                     | Status        |
| -------------------------- | ------------- |
| Dataset preparation        | ✅ Completed   |
| YOLO11n training           | ✅ Completed   |
| 6-class detection model    | ✅ Completed   |
| Event Engine               | ✅ Completed   |
| Multi-hazard visualization | ✅ Completed   |
| Raspberry Pi inference     | 🚧 Next Phase |
| Telemetry → Ground Station | 🚧 Next Phase |
| Dashboard integration      | 🚧 Next Phase |

---

## Project Structure

```
Detection_Model/
│
├── datasets/
│   ├── flood/
│   ├── fire/
│   ├── smoke/
│   ├── debris/
│   ├── landslide/
│   ├── person/
│   └── final_v3/
│
├── raspberry_pi/
│   ├── inference/
│   ├── event_engine/
│   ├── config/
│   ├── communication/
│   └── storage/
│
├── scripts/
│   ├── build_final_dataset.py
│   ├── clean_*.py
│   └── visualize_final_dataset.py
│
├── runs/
│   └── detect/
│       └── disaster_6class_v3-4/
│           └── weights/
│               ├── best.pt
│               └── last.pt
│
└── README.md
```

---

## Tech Stack

### AI & Machine Learning

* YOLO11n (Ultralytics)

* PyTorch

* OpenCV

* NumPy

### Backend / Edge AI

* Python 3.11

* FastAPI

* JSON Event Engine

### Hardware

* Raspberry Pi 4 Model B

* RGB Camera

* GPS Module

* Telemetry (LoRa/Wi-Fi planned)

---

## Model Information

**Architecture:** YOLO11n

**Classes**

| ID | Class     |
| -- | --------- |
| 0  | Flood     |
| 1  | Smoke     |
| 2  | Fire      |
| 3  | Debris    |
| 4  | Landslide |
| 5  | Person    |

The model is trained using a **custom merged aerial disaster dataset** created from multiple public datasets.

---

## Dataset Pipeline

1. Collect aerial disaster datasets

2. Clean annotations

3. Remove corrupt & duplicate labels

4. Remap all class IDs

5. Merge into `final_v3`

6. Train YOLO11n

7. Validate using mAP, Precision & Recall

---

## Edge AI Workflow

```
Drone Camera
      │
      ▼
 Raspberry Pi
      │
      ▼
 YOLO11n Inference
      │
      ▼
 Hazard Detection
      │
      ▼
 Event Engine
      │
      ▼
 GPS + Timestamp
      │
      ▼
 Telemetry
      │
      ▼
 Ground Station
```

---

## Event Generation

Every important detection becomes a structured JSON event.

```json
{
  "event_id": "EVT_00001",
  "hazard": "person",
  "confidence": 0.91,
  "priority": "CRITICAL",
  "latitude": 18.5204,
  "longitude": 73.8567,
  "altitude": 112.4,
  "timestamp": "2026-09-19T12:30:00Z",
  "image_path": "storage/events/EVT_00001/frame.jpg"
}
```

---

## Priority Rules

| Hazard    | Priority |
| --------- | -------- |
| Person    | CRITICAL |
| Fire      | HIGH     |
| Flood     | HIGH     |
| Landslide | HIGH     |
| Smoke     | MEDIUM   |
| Debris    | LOW      |

Additional anti-false-positive logic is defined inside:

```
raspberry_pi/docs/event_rules.md
```

---

## Raspberry Pi Deployment (Next Developer)

### Copy these folders to Raspberry Pi

```
raspberry_pi/
best.pt
config/
```

### Install dependencies

```bash
pip install ultralytics opencv-python numpy fastapi
```

### Run live inference

```bash
python raspberry_pi/inference/live_inference.py
```

### Generate rescue events

```bash
python raspberry_pi/event_engine/event_manager.py
```

---

## Future Roadmap

* RGB + Thermal camera fusion

* Real-time LoRa telemetry

* Multi-drone coordination

* SLAM-based GPS-denied navigation

* Automatic rescue route recommendation

---

## Author

**Sohel Tamboli**

AI • Backend • Edge Intelligence

Smart India Hackathon 2026
