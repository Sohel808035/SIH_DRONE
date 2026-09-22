# Architecture

## System Overview

```mermaid
flowchart TD
    A["Drone Camera / USB Camera<br/>raspberry_pi/config/camera.json"] -->|OpenCV VideoCapture| B[Raw Frame]
    B --> C["YOLO11n Inference<br/>models/best.pt<br/>conf=0.20 · iou=0.45 · imgsz=640"]
    C --> D["yolo_parser.parse_yolo()<br/>class_id · class · confidence · box"]
    D --> E["draw_multihazard.draw_detections()<br/>Annotated Frame"]
    D --> F["DetectionTracker.update()<br/>Consecutive-frame filter<br/>Cooldown suppression"]
    F --> G{Threshold met?}
    G -->|No — continue| B
    G -->|Yes| H["EventManager.create_event()<br/>Multi-hazard JSON event<br/>event_id · timestamp · priority<br/>detections list · people_count"]
    H --> I["GPSProvider.get_position()<br/>latitude · longitude · altitude"]
    I --> J["storage/events/EVT_XXXXXX/<br/>metadata.json<br/>frame.jpg"]
    H --> K["CommunicationTransport.send_event()"]
    K --> L["NullTransport ✅ / ConsoleTransport ✅<br/>LoRaTransport 🔜 / MAVLinkTransport 🔜"]

    style L fill:#fff3cd,stroke:#ffc107
    style I fill:#d4edda,stroke:#28a745
```

---

## Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `raspberry_pi/main.py` | CLI, config loading, wiring all components |
| `inference/live_inference.py` | Camera/video loop, model predict() |
| `inference/yolo_parser.py` | Ultralytics → clean detection dicts |
| `inference/draw_multihazard.py` | OpenCV annotation |
| `inference/class_config.py` | Authoritative class map (loads classes.json) |
| `inference/class_colors.py` | BGR colors per class |
| `event_engine/event_manager.py` | Multi-detection event creation + JSON storage |
| `event_engine/tracker.py` | Consecutive-frame threshold + cooldown |
| `communication/interface.py` | Transport abstraction |
| `communication/gps_provider.py` | GPS abstraction |

---

## Data Flow — Single Frame

```
Camera frame (BGR numpy array)
    │
    ▼ YOLO11n predict()
[{class_id:2, class:'fire', conf:0.91, box:[...]},
 {class_id:5, class:'person', conf:0.88, box:[...]}]
    │
    ▼ DetectionTracker.update()
Filtered list (only classes that met consecutive-frame threshold)
    │
    ▼ EventManager.create_event()
{
  "event_id": "EVT_000001",
  "priority": "CRITICAL",
  "detections": [...],
  "people_count": 1,
  "latitude": null, "longitude": null, "altitude": null,
  "image_path": "...frame.jpg"
}
    │
    ├─▶ Written to storage/events/EVT_000001/metadata.json
    └─▶ CommunicationTransport.send_event()
```

---

## What Is and Is Not Implemented

```mermaid
flowchart LR
    subgraph "✅ Implemented"
        I1[YOLO11n Inference]
        I2[Multi-Hazard Event Engine]
        I3[JSON Storage]
        I4[CLI Entry Point]
        I5[Config System]
        I6[Tracker / FP Filter]
    end

    subgraph "🔜 Not Yet Implemented"
        N1[GPS Hardware]
        N2[LoRa Transport]
        N3[MAVLink]
        N4[Thermal Fusion]
        N5[SLAM]
        N6[Ground Station Dashboard]
    end
```
