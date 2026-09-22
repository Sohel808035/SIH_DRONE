# Contributing to Detection_Model

Thank you for your interest in contributing!

---

## Where to Add New Features

### GPS Integration
- File: `raspberry_pi/communication/gps_provider.py`
- Create a class inheriting `GPSProvider`
- Implement `get_position() -> (lat, lon, alt)`
- Recommended: `pyserial` + `pynmea2` for UART GPS (NEO-M8N)
- Register in `raspberry_pi/main.py`

### LoRa Telemetry
- File: `raspberry_pi/communication/interface.py`
- Implement `LoRaTransport(CommunicationTransport)`
- Implement `send_event(event: dict)`
- Keep payload compact — LoRa bandwidth is limited (~250 bytes/packet)

### MAVLink Flight Controller
- File: `raspberry_pi/communication/interface.py`
- Implement `MAVLinkTransport(CommunicationTransport)`
- Recommended library: `pymavlink`

### Thermal Camera Fusion
- Create: `raspberry_pi/inference/thermal_fusion.py`
- Combine RGB + thermal bounding boxes before passing to EventManager

### Ground Station Dashboard
- This is a separate project
- Consume events from `raspberry_pi/storage/events/`
- Or receive them over the communication transport

---

## Code Style
- PEP 8
- Type hints on all new public functions
- Docstrings on all new public classes and functions
- No hardcoded absolute paths

## Testing
- Add tests to `tests/` for any new module
- Run: `python -m pytest tests/ -v`
- All 35 existing tests must continue to pass

## Pull Request Checklist
- [ ] Tests pass
- [ ] No hardcoded machine-specific paths
- [ ] Docstrings present
- [ ] `CHANGELOG.md` updated
- [ ] Hardware status documented honestly
