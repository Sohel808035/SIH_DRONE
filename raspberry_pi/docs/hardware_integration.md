# Hardware Integration Guide

This document describes the hardware integration status for each component.

---

## Camera

| Item | Status |
|------|--------|
| USB webcam (UVC) | ✅ Supported |
| Video file (testing) | ✅ Supported |
| Raspberry Pi Camera Module (CSI) | ⚠️ Enable via raspi-config, use `source: 0` or libcamera |
| Thermal camera | 🔜 Not Implemented |

**To configure camera source:**  
Edit `raspberry_pi/config/camera.json` → `"source"` field.

---

## GPS

| Item | Status |
|------|--------|
| NullGPSProvider (no hardware) | ✅ Implemented — safe default |
| SimulatorGPSProvider (fixed test position) | ✅ Implemented |
| SerialGPSProvider (UART hardware) | 🔜 Not Implemented |

**To integrate a real GPS module (e.g., NEO-M8N):**

1. Wire GPS module TX → Raspberry Pi RX (GPIO 15 / `/dev/ttyS0`)
2. Install libraries:
   ```bash
   pip install pyserial pynmea2
   ```
3. Implement `SerialGPSProvider` in `raspberry_pi/communication/gps_provider.py`:
   ```python
   class SerialGPSProvider(GPSProvider):
       def __init__(self, port="/dev/ttyS0", baudrate=9600):
           import serial
           self._ser = serial.Serial(port, baudrate, timeout=1)
       
       def get_position(self):
           import pynmea2
           line = self._ser.readline().decode("ascii", errors="replace")
           if line.startswith("$GPGGA"):
               msg = pynmea2.parse(line)
               return msg.latitude, msg.longitude, msg.altitude
           return None, None, None
   ```
4. Register in `raspberry_pi/main.py` → replace `NullGPSProvider()` with `SerialGPSProvider()`

---

## Telemetry

| Item | Status |
|------|--------|
| NullTransport | ✅ Implemented |
| ConsoleTransport | ✅ Implemented |
| LoRaTransport (SX1276/SX1262 SPI) | 🔜 Not Implemented |
| MAVLinkTransport (Pixhawk) | 🔜 Not Implemented |
| HTTP/MQTT | 🔜 Not Implemented |

**To add LoRa:**  
Implement `LoRaTransport` in `raspberry_pi/communication/interface.py`.  
See `raspberry_pi/docs/telemetry.md` for packet design.

---

## Thermal Camera

| Item | Status |
|------|--------|
| FLIR Lepton / MLX90640 | 🔜 Not Implemented |
| RGB + Thermal fusion | 🔜 Future Work |

Thermal fusion should be implemented in `raspberry_pi/inference/thermal_fusion.py`.  
The fused bounding boxes should be passed to `EventManager` in the same format as YOLO detections.

---

## Flight Controller (MAVLink)

| Item | Status |
|------|--------|
| Pixhawk / ArduPilot integration | 🔜 Not Implemented |
| Autonomous waypoint control | 🔜 Out of scope for this repository |

This repository handles **AI perception** only. Flight control integration is a separate system.

---

## SLAM / GPS-Denied Navigation

| Item | Status |
|------|--------|
| ORB-SLAM3 / RTAB-Map | 🔜 Out of scope |
| VIO (Visual-Inertial Odometry) | 🔜 Out of scope |

SLAM is a separate research module. This repository does not implement navigation.
