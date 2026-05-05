"""MQTT-based auto-discovery of Phileo VP / Oxeo VP modules.

The Phileo VP runs an unauthenticated MQTT broker on port 1883 and publishes
its own data under `phileox_<MAC12>/...`. The Oxeo VP is paired to the Phileo
over short-range RF (BLE / Sub-GHz) and its data is relayed onto the same
broker under `oxeox_<MAC12>/...`. Subscribing to `#` for a few seconds
collects both topic prefixes and lets the config flow fill the MAC fields
automatically.
"""
from __future__ import annotations

import logging
import time

import paho.mqtt.client as mqtt

_LOGGER = logging.getLogger(__name__)

# Topic-prefix → integration field name (extend if Vigipool ships more module types)
_TYPE_TO_FIELD: dict[str, str] = {
    "phileox": "phileo_id",
    "oxeox": "oxeo_id",
}


def _is_hex12(mac: str) -> bool:
    if len(mac) != 12:
        return False
    try:
        int(mac, 16)
    except ValueError:
        return False
    return True


def _discover_sync(host: str, port: int, timeout: float) -> dict[str, str]:
    """Subscribe `#` for `timeout` seconds and collect MACs from topic prefixes."""
    found: dict[str, str] = {}
    seen: set[str] = set()

    def _on_message(_c, _u, msg) -> None:
        prefix = msg.topic.split("/", 1)[0]
        if prefix in seen or "_" not in prefix:
            return
        seen.add(prefix)
        typ, mac = prefix.split("_", 1)
        field = _TYPE_TO_FIELD.get(typ)
        if field and _is_hex12(mac):
            found[field] = mac.upper()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ha_orpheo_discover")
    client.on_message = _on_message
    try:
        client.connect(host, port, 10)
        client.subscribe("#")
        client.loop_start()
        time.sleep(timeout)
        client.loop_stop()
        client.disconnect()
    except OSError as err:
        _LOGGER.warning("Auto-discovery: broker not reachable on %s:%s — %s", host, port, err)
    return found


async def async_discover(hass, host: str, port: int = 1883, timeout: float = 6.0) -> dict[str, str]:
    """Run MQTT auto-discovery in an executor.

    Returns a dict that may contain `phileo_id` and/or `oxeo_id`. Empty if
    nothing was found within the timeout window (or the broker was unreachable).
    """
    return await hass.async_add_executor_job(_discover_sync, host, port, timeout)
