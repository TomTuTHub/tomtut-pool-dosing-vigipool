"""Direkter MQTT-Client fuer die Orpheo VP (Geraet = Broker).

Laeuft in einem Hintergrund-Thread (paho-mqtt loop_start) und pflegt einen
in-memory Cache aller zuletzt empfangenen Werte. Der Coordinator pollt den
Cache periodisch und wird ausserdem bei jeder eingehenden Nachricht via
`async_set_updated_data` gepusht.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Callable, Optional

import paho.mqtt.client as mqtt

from .const import (
    MQTT_DEFAULT_PORT,
    OXEO_POINTS,
    OXEO_PREFIX,
    PHILEO_POINTS,
    PHILEO_PREFIX,
    oxeo_sub_filter,
    oxeo_topic,
    phileo_sub_filter,
    phileo_topic,
)

_LOGGER = logging.getLogger(__name__)


class OrpheoMqttClient:
    """Thread-basierter paho-mqtt Client mit async-Bridge."""

    def __init__(
        self,
        hass,
        host: str,
        port: int,
        phileo_id: str,
        oxeo_id: str,
    ) -> None:
        self.hass = hass
        self._host = host
        self._port = port
        self._phileo_id = phileo_id
        self._oxeo_id = oxeo_id

        # Raw-Cache: short_name -> (raw_int, timestamp)
        self._values: dict[str, tuple[int, float]] = {}
        self._last_message_ts: float = 0.0
        self._connected: bool = False

        self._client = mqtt.Client(
            client_id=f"ha_orpheo_vp_{phileo_id[-6:]}",
            clean_session=True,
        )
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

        self._update_callback: Optional[Callable[[], None]] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    # ---------- Lifecycle ----------

    def set_update_callback(self, cb: Callable[[], None]) -> None:
        """Registriert einen Callback, der bei jeder neuen Nachricht gefeuert wird.
        Muss thread-safe sein (wird aus dem paho-Thread aufgerufen).
        """
        self._update_callback = cb

    async def async_start(self) -> None:
        self._loop = asyncio.get_running_loop()
        await self.hass.async_add_executor_job(self._connect)

    async def async_stop(self) -> None:
        await self.hass.async_add_executor_job(self._disconnect)

    def _connect(self) -> None:
        _LOGGER.info("Verbinde mit Orpheo-Broker %s:%s", self._host, self._port)
        self._client.connect(self._host, self._port, keepalive=60)
        self._client.loop_start()

    def _disconnect(self) -> None:
        try:
            self._client.loop_stop()
            self._client.disconnect()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Disconnect error: %s", err)

    # ---------- paho callbacks (Thread-Kontext!) ----------

    def _on_connect(self, client, userdata, flags, rc):  # noqa: ARG002
        if rc != 0:
            _LOGGER.error("MQTT connect failed (rc=%s)", rc)
            return
        self._connected = True
        filters = [
            (phileo_sub_filter(self._phileo_id), 0),
            (oxeo_sub_filter(self._oxeo_id), 0),
        ]
        client.subscribe(filters)
        _LOGGER.info("Subscribed: %s", [f[0] for f in filters])

    def _on_disconnect(self, client, userdata, rc):  # noqa: ARG002
        self._connected = False
        if rc != 0:
            _LOGGER.warning("MQTT unexpected disconnect rc=%s — paho reconnects automatisch", rc)

    def _on_message(self, client, userdata, msg):  # noqa: ARG002
        topic = msg.topic
        try:
            payload = msg.payload.decode("utf-8", errors="replace").strip()
        except Exception:  # noqa: BLE001
            return

        # Parse topic: <prefix><id>/<dtype>/<name>/<subtype>/<direction>
        parts = topic.split("/")
        if len(parts) != 5:
            return
        root, dtype, name, subtype, direction = parts
        if direction != "reported":
            return  # Nur reported in den Cache

        if root.startswith(PHILEO_PREFIX):
            points = PHILEO_POINTS
        elif root.startswith(OXEO_PREFIX):
            points = OXEO_POINTS
        else:
            return

        short_name = None
        for key, (kt, kn, ks, _scale, _w) in points.items():
            if kt == dtype and kn == name and ks == subtype:
                short_name = key
                break
        if short_name is None:
            return

        try:
            raw = int(payload)
        except ValueError:
            try:
                raw = int(float(payload))
            except ValueError:
                _LOGGER.debug("Non-numeric payload on %s: %r", topic, payload)
                return

        self._values[short_name] = (raw, time.time())
        self._last_message_ts = time.time()

        if self._update_callback is not None:
            self._update_callback()

    # ---------- Public read API ----------

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def last_message_ts(self) -> float:
        return self._last_message_ts

    def get(self, short_name: str) -> Optional[float]:
        """Liefert den skalierten Wert oder None."""
        entry = self._values.get(short_name)
        if entry is None:
            return None
        raw, _ts = entry

        if short_name in PHILEO_POINTS:
            scale = PHILEO_POINTS[short_name][3]
        elif short_name in OXEO_POINTS:
            scale = OXEO_POINTS[short_name][3]
        else:
            scale = None

        if scale is None:
            return float(raw)
        return raw / scale

    def get_raw(self, short_name: str) -> Optional[int]:
        entry = self._values.get(short_name)
        return entry[0] if entry else None

    def has_any_data(self) -> bool:
        return bool(self._values)

    # ---------- Public write API ----------

    async def async_write(self, short_name: str, value: float) -> bool:
        """Schreibt einen Wert auf den entsprechenden `desired` Topic.
        Rueckgabe: True bei Publish-Erfolg.
        """
        if short_name in PHILEO_POINTS:
            dtype, name, subtype, scale, writable = PHILEO_POINTS[short_name]
            topic_fn = phileo_topic
            device_id = self._phileo_id
        elif short_name in OXEO_POINTS:
            dtype, name, subtype, scale, writable = OXEO_POINTS[short_name]
            topic_fn = oxeo_topic
            device_id = self._oxeo_id
        else:
            _LOGGER.error("Unbekannter short_name: %s", short_name)
            return False

        if not writable:
            _LOGGER.error("Topic %s ist nicht schreibbar", short_name)
            return False

        raw = int(round(value * scale)) if scale else int(round(value))
        topic = topic_fn(device_id, dtype, name, subtype, "desired")
        payload = str(raw)

        def _publish() -> bool:
            result = self._client.publish(topic, payload, qos=0, retain=False)
            result.wait_for_publish(timeout=5)
            return result.rc == mqtt.MQTT_ERR_SUCCESS

        ok = await self.hass.async_add_executor_job(_publish)
        if ok:
            _LOGGER.info("MQTT write %s -> %s (raw=%s)", short_name, value, raw)
            # Optimistisch in den Cache legen damit UI direkt reagiert
            self._values[short_name] = (raw, time.time())
            if self._update_callback is not None:
                self._update_callback()
        else:
            _LOGGER.error("MQTT write failed: %s", topic)
        return ok
