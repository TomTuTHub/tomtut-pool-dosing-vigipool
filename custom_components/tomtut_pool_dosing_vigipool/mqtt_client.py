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
    CONFIG_DEBOUNCE,
    CONFIG_DEBOUNCE_KEYS,
    MQTT_DEFAULT_PORT,
    MQTT_KEEPALIVE,
    OXEO_POINTS,
    OXEO_PREFIX,
    PHILEO_POINTS,
    PHILEO_PREFIX,
    SENTINEL_FILTER_KEYS,
    SENTINEL_RAW_VALUES,
    oxeo_sub_filter,
    oxeo_topic,
    phileo_sub_filter,
    phileo_topic,
)

_LOGGER = logging.getLogger(__name__)


def _split_subtype(s) -> tuple[str, str]:
    """Return (read_subtype, write_subtype). When the points table uses a
    single string, both are the same. When it uses a 2-tuple the device
    publishes its current value on a different subtype than it accepts
    writes on (observed for `consigne_ph` on the Phileo VP: writes on
    `consigne/desired`, current value echoed back on `info/reported`)."""
    if isinstance(s, tuple):
        return s[0], s[1]
    return s, s


class OrpheoMqttClient:
    """Thread-basierter paho-mqtt Client mit async-Bridge."""

    def __init__(
        self,
        hass,
        host: str,
        port: int,
        phileo_id: str,
        oxeo_id: str,
        instance_suffix: str = "",
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
        # Merkt pro Messpunkt, ob der Sentinel-Verwurf schon geloggt wurde
        # (einmalige Info-Zeile statt Spam bei wiederholtem Messfehler).
        self._sentinel_logged: set[str] = set()
        # Zeitstempel (time.time()) des letzten unerwarteten Disconnects;
        # 0.0 solange verbunden. Basis fuer die Grace-Period im Coordinator.
        self._disconnected_ts: float = 0.0
        # Entprellte Config-Werte (Behaeltergroesse/Maximaldosis):
        # short_name -> (raw, seit_ts). settle_config() uebernimmt sie
        # nach einer Ruhephase in _values (s. const.py CONFIG_DEBOUNCE).
        self._pending_config: dict[str, tuple[int, float]] = {}

        # MQTT broker (= Phileo VP itself) enforces uniqueness on client_id:
        # a second client with the same ID kicks the first off. When multiple
        # HA instances point at the same device (prod + dev1 + dev2, or two
        # users with the same hardware), a deterministic id derived only from
        # the device MAC causes an endless reconnect loop. Mix in the HA
        # instance UUID so each HA gets its own slot.
        cid = f"ha_orpheo_vp_{phileo_id[-6:]}"
        if instance_suffix:
            cid = f"{cid}_{instance_suffix}"
        self._client = mqtt.Client(
            client_id=cid,
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
        """Non-blocking connect: paho's I/O-Thread versucht im Hintergrund
        endlos zu connecten/reconnecten.

        Wichtig: NICHT `connect()` benutzen — das ist synchron blockierend
        und wirft bei offline Anlage eine Exception, was den Config-Entry-
        Setup in `setup_error` schickt. Daraus kommt HA auch nach Reboot
        nicht selbst raus; User müsste die Integration neu hinzufügen.
        `connect_async()` setzt nur die Connection-Intention, `loop_start()`
        läuft den I/O-Loop, der bei Connection-Loss automatisch retried.
        Sobald die Anlage online ist, wird `_on_connect` gefeuert und die
        Subscribes laufen wie gewohnt.
        """
        _LOGGER.info("Initialisiere MQTT-Loop fuer Orpheo-Broker %s:%s (non-blocking)", self._host, self._port)
        self._client.connect_async(self._host, self._port, keepalive=MQTT_KEEPALIVE)
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
        self._disconnected_ts = 0.0
        filters = [
            (phileo_sub_filter(self._phileo_id), 0),
            (oxeo_sub_filter(self._oxeo_id), 0),
        ]
        client.subscribe(filters)
        _LOGGER.info("Subscribed: %s", [f[0] for f in filters])

    def _on_disconnect(self, client, userdata, rc):  # noqa: ARG002
        # paho ruft diesen Callback bei EINEM einzigen unerwarteten Disconnect
        # aus mehreren Loop-Pfaden auf (loop_read + _loop_rc_handle), µs
        # auseinander im selben Thread — ohne interne Deduplizierung. Ohne
        # Guard erzeugt das zwei identische WARNING-Zeilen. Idempotent machen:
        # war die Verbindung schon als weg markiert, nichts doppelt tun
        # (kein zweites WARNING, Disconnect-Zeitstempel der ERSTEN Meldung
        # behalten — die Grace-Period rechnet ab dem ersten Ausfall).
        if not self._connected:
            return
        self._connected = False
        self._disconnected_ts = time.time()
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
            read_sub, _write_sub = _split_subtype(ks)
            if kt == dtype and kn == name and read_sub == subtype:
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

        # Sentinel (0xFFFE/0xFFFF) auf einem Live-Messwert = Geraete-
        # Messfehler: verwerfen, letzten gueltigen Cache-Wert behalten.
        # Einmal pro Punkt loggen, kein Spam.
        if short_name in SENTINEL_FILTER_KEYS and raw in SENTINEL_RAW_VALUES:
            if short_name not in self._sentinel_logged:
                _LOGGER.info(
                    "Sentinel-Rohwert %s auf %s verworfen (Geraete-Messfehler-Marker) "
                    "— behalte letzten gueltigen Wert",
                    raw, short_name,
                )
                self._sentinel_logged.add(short_name)
            return

        now = time.time()
        self._last_message_ts = now

        # Config-Werte entprellen: die Anlage streamt hier Bursts von
        # Zwischenwerten (s. const.py). Nur als pending vormerken; erst
        # settle_config() uebernimmt den stabilen Wert in den Cache.
        if short_name in CONFIG_DEBOUNCE_KEYS:
            committed = self._values.get(short_name)
            if committed is None or committed[0] != raw:
                self._pending_config[short_name] = (raw, now)
            else:
                self._pending_config.pop(short_name, None)
            return

        self._values[short_name] = (raw, now)
        if self._update_callback is not None:
            self._update_callback()

    # ---------- Public read API ----------

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def disconnected_since(self) -> float:
        """time.time()-Zeitstempel des letzten unerwarteten Disconnects.
        0.0 wenn verbunden oder noch nie verbunden gewesen."""
        return self._disconnected_ts

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

    def settle_config(self, now: Optional[float] = None) -> bool:
        """Uebernimmt entprellte Config-Werte, die lange genug stabil sind.
        Wird vom Coordinator-Tick aufgerufen. Rueckgabe: True wenn etwas
        uebernommen wurde."""
        if not self._pending_config:
            return False
        if now is None:
            now = time.time()
        changed = False
        for key, (raw, ts) in list(self._pending_config.items()):
            if now - ts >= CONFIG_DEBOUNCE:
                self._values[key] = (raw, now)
                self._pending_config.pop(key, None)
                changed = True
        return changed

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
        _read_sub, write_sub = _split_subtype(subtype)
        topic = topic_fn(device_id, dtype, name, write_sub, "desired")
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
