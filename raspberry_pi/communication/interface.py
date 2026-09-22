"""
interface.py — Communication transport abstraction.

Provides a base interface and two ready-to-use implementations:
  - NullTransport     : silently drops all events (safe default)
  - ConsoleTransport  : prints event JSON to stdout

Future transports (NOT YET IMPLEMENTED):
  - LoRaTransport     : send compact telemetry over LoRa radio
  - MAVLinkTransport  : integrate with flight controller via MAVLink

To add a new transport:
1. Create a class that inherits from CommunicationTransport.
2. Implement send_event(event: dict) and close().
3. Register it in main.py's transport selection logic.
"""
import json


class CommunicationTransport:
    """Base interface for all communication transports."""

    def send_event(self, event: dict) -> None:
        """Send a structured event dict over the transport."""
        raise NotImplementedError

    def close(self) -> None:
        """Release any resources held by the transport."""
        pass


class NullTransport(CommunicationTransport):
    """
    Silently discards all events.
    Use as a safe default when no telemetry hardware is connected.
    """

    def send_event(self, event: dict) -> None:
        pass  # Intentionally silent


class ConsoleTransport(CommunicationTransport):
    """
    Prints event JSON to stdout.
    Useful for local development and debugging.
    """

    def send_event(self, event: dict) -> None:
        print("[TELEMETRY]", json.dumps(event, indent=2))


# ── NOT YET IMPLEMENTED ───────────────────────────────────────────────────────

class LoRaTransport(CommunicationTransport):
    """
    LoRa radio telemetry transport.

    STATUS: NOT YET IMPLEMENTED
    This class is a placeholder for future LoRa integration.
    Hardware required: SX1276/SX1262-based LoRa module connected via SPI/UART.
    """

    def send_event(self, event: dict) -> None:
        raise NotImplementedError(
            "LoRaTransport is not yet implemented. "
            "See raspberry_pi/docs/hardware_integration.md for integration instructions."
        )


class MAVLinkTransport(CommunicationTransport):
    """
    MAVLink telemetry transport for flight controller integration.

    STATUS: NOT YET IMPLEMENTED
    Hardware required: Flight controller with MAVLink support (e.g., Pixhawk).
    """

    def send_event(self, event: dict) -> None:
        raise NotImplementedError(
            "MAVLinkTransport is not yet implemented. "
            "See raspberry_pi/docs/hardware_integration.md for integration instructions."
        )
