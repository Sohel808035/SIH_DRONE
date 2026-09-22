# Communication Module

## Status

| Transport | Status |
|-----------|--------|
| NullTransport | ✅ Implemented |
| ConsoleTransport | ✅ Implemented |
| LoRaTransport | 🔜 Not Yet Implemented |
| MAVLinkTransport | 🔜 Not Yet Implemented |

| GPS Provider | Status |
|-------------|--------|
| NullGPSProvider | ✅ Implemented |
| SimulatorGPSProvider | ✅ Implemented |
| SerialGPSProvider | 🔜 Not Yet Implemented |

## Adding a New Transport

1. Open `interface.py`
2. Create a class inheriting `CommunicationTransport`
3. Implement `send_event(event: dict)`
4. Register in `raspberry_pi/main.py`

## Adding GPS Hardware

See `raspberry_pi/docs/hardware_integration.md` → GPS section.
