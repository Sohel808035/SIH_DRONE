# Changelog

All notable changes to this project will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-09-22

### Added
- YOLO11n 6-class disaster detection model (`models/best.pt`)
- Complete inference pipeline: camera → YOLO → parser → visualizer
- Multi-hazard event engine: multiple detections per frame → one JSON event
- Temporal tracker for false-positive reduction (consecutive-frame logic)
- JSON configuration system: `model.json`, `camera.json`, `telemetry.json`, `classes.json`, `priorities.json`
- CLI entry point: `python -m raspberry_pi.main` with `--source`, `--device`, `--conf`, etc.
- Communication transport interface: NullTransport, ConsoleTransport; stubs for LoRa and MAVLink
- GPS provider interface: NullGPSProvider, SimulatorGPSProvider; stub for SerialGPSProvider
- Full test suite: 35 tests across paths, config, parser, and event manager
- Documentation: deployment, architecture, event engine, telemetry, hardware integration

### Model
- Architecture: YOLO11n
- Classes: flood (0), smoke (1), fire (2), debris (3), landslide (4), person (5)
- Training: 100 epochs, custom merged aerial disaster dataset
- SHA256: `B5F505A1BD476E83B18638285FA8D5346D74CD3996BE7D31BF2B17D77E462ACA`

### Not Yet Implemented
- Real GPS hardware integration (SerialGPSProvider)
- LoRa telemetry (LoRaTransport)
- MAVLink flight controller integration (MAVLinkTransport)
- Thermal camera fusion
- Autonomous navigation / SLAM
