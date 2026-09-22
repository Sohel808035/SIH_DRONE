"""
gps_provider.py — GPS position provider abstraction.

STATUS: GPS hardware integration is NOT YET IMPLEMENTED.

This module defines a clean interface so the rest of the codebase
can query GPS without needing to know the hardware details.

When actual GPS hardware (e.g., NEO-M8N via UART) is available:
1. Create a class inheriting from GPSProvider.
2. Implement get_position() to read from the hardware.
3. Pass it to main.py's provider selection logic.
"""


class GPSProvider:
    """Base interface for all GPS providers."""

    def get_position(self) -> tuple[float | None, float | None, float | None]:
        """
        Returns:
            (latitude, longitude, altitude) — all may be None if unavailable.
        """
        raise NotImplementedError


class NullGPSProvider(GPSProvider):
    """
    Returns (None, None, None) for all position queries.

    Use as the safe default when no GPS hardware is connected.
    """

    def get_position(self):
        return None, None, None


class SimulatorGPSProvider(GPSProvider):
    """
    Returns a fixed test position.
    Useful for development and testing without real GPS hardware.
    """

    def __init__(self, lat: float = 18.5204, lon: float = 73.8567, alt: float = 100.0):
        self._lat = lat
        self._lon = lon
        self._alt = alt

    def get_position(self):
        return self._lat, self._lon, self._alt


# ── NOT YET IMPLEMENTED ──────────────────────────────────────────────────────

class SerialGPSProvider(GPSProvider):
    """
    Reads NMEA sentences from a UART-connected GPS module (e.g., NEO-M8N).

    STATUS: NOT YET IMPLEMENTED
    Hardware required: GPS module connected via /dev/ttyS0 or /dev/ttyUSB0.
    Library required: pip install pyserial pynmea2
    """

    def get_position(self):
        raise NotImplementedError(
            "SerialGPSProvider is not yet implemented. "
            "See raspberry_pi/docs/hardware_integration.md for wiring and integration guide."
        )
