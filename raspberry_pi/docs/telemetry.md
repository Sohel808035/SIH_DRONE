# Telemetry Documentation

## Overview

The telemetry system transmits hazard event data from the Raspberry Pi to a ground station.

**Current status: Telemetry transport is NOT YET IMPLEMENTED beyond console logging.**

---

## Event Telemetry Packet

The recommended compact telemetry packet (for low-bandwidth transport like LoRa):

```json
{
  "id": "EVT_000001",
  "t": "2026-09-19T07:00:00Z",
  "p": "CRITICAL",
  "lat": null,
  "lon": null,
  "alt": null,
  "hz": ["fire", "smoke", "person"],
  "ppl": 1
}
```

> Do NOT transmit full images over LoRa — bandwidth is ~250 bytes/packet at typical settings.
> Images should be stored locally in `storage/events/` and retrieved separately if needed.

---

## Transport Options

| Transport | Status | Notes |
|-----------|--------|-------|
| NullTransport | ✅ Implemented | Silently drops events (safe default) |
| ConsoleTransport | ✅ Implemented | Prints JSON to stdout |
| LoRaTransport | 🔜 Not Implemented | See integration notes below |
| MAVLinkTransport | 🔜 Not Implemented | See integration notes below |

---

## LoRa Integration (Future)

LoRa is suitable for long-range, low-bandwidth telemetry in GPS-denied or network-denied disaster zones.

**To implement:**
1. Connect a LoRa module (e.g., SX1276) via SPI to Raspberry Pi
2. Install driver library (e.g., `lora-from-scratch` or `RPi-LoRa`)
3. Implement `LoRaTransport` in `raspberry_pi/communication/interface.py`
4. Enable in `telemetry.json`:
   ```json
   {"enabled": true, "transport": "lora"}
   ```

**Bandwidth considerations:**
- LoRa at SF7/BW125: ~5–6 kbps
- Compact JSON packet: ~100–200 bytes → acceptable
- Full event JSON: ~500+ bytes → too large for single packet without fragmentation

---

## WiFi / HTTP Integration (Future)

For deployments with WiFi coverage:
- POST event JSON to a REST endpoint
- Or publish via MQTT to a broker

Implement as a `HTTPTransport` or `MQTTTransport` in `interface.py`.

---

## MAVLink Integration (Future)

For integration with a flight controller (Pixhawk):
- Use `pymavlink` library
- Send custom MAVLink messages or write to `STATUSTEXT`
- See `raspberry_pi/docs/hardware_integration.md`

---

## Enabling Telemetry

Edit `raspberry_pi/config/telemetry.json`:

```json
{
  "enabled": true,
  "transport": "console"
}
```

Available values for `transport`: `"null"`, `"console"` (implemented)  
Future values: `"lora"`, `"mavlink"`, `"http"`, `"mqtt"`
