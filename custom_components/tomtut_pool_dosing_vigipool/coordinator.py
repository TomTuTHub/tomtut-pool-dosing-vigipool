"""DataUpdateCoordinator fuer Orpheo VP — ausschließlich lokales MQTT.

Verhalten:
- MQTT-Push (`_handle_mqtt_push`) → `async_set_updated_data` → `last_update_success = True`
- Periodischer Heartbeat (`_async_update_data`) prüft `mqtt.connected`. Wenn die
  TCP-Connection zur Anlage tot ist, wird `UpdateFailed` geworfen → Coordinator
  setzt `last_update_success = False` → alle CoordinatorEntity sind `unavailable`.
- Auf Anlagen-Seite genügt das, weil die Anlage selbst der MQTT-Broker ist:
  TCP-Connection lebt = Anlage erreichbar; TCP-Connection tot = Anlage offline.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_NAME, DOMAIN, OXEO_POINTS, PHILEO_POINTS, SCAN_INTERVAL
from .mqtt_client import OrpheoMqttClient

_LOGGER = logging.getLogger(__name__)


@dataclass
class OrpheoData:
    """Zusammengefuehrte Sicht auf alle Datenpunkte."""

    source: str = "init"                # "mqtt" oder "init"
    values: dict[str, float] = field(default_factory=dict)
    last_mqtt_ts: float = 0.0

    def get(self, key: str) -> Optional[float]:
        return self.values.get(key)


class OrpheoVPCoordinator(DataUpdateCoordinator[OrpheoData]):
    """Lokaler MQTT-Coordinator. Keine Cloud."""

    def __init__(
        self,
        hass: HomeAssistant,
        mqtt_client: OrpheoMqttClient,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.mqtt = mqtt_client
        self.device_name: str = DEFAULT_NAME

        mqtt_client.set_update_callback(self._mqtt_push_callback)

    # ------------------------------------------------------------------
    # MQTT push → Coordinator
    # ------------------------------------------------------------------

    def _mqtt_push_callback(self) -> None:
        """Aus dem paho-Thread. Thread-safe via call_soon_threadsafe."""
        if self.hass.loop.is_closed():
            return
        self.hass.loop.call_soon_threadsafe(self._handle_mqtt_push)

    @callback
    def _handle_mqtt_push(self) -> None:
        data = self._build_from_mqtt()
        if data is not None:
            self.async_set_updated_data(data)

    def _build_from_mqtt(self) -> Optional[OrpheoData]:
        if not self.mqtt.has_any_data():
            return None
        values: dict[str, float] = {}
        for key in list(PHILEO_POINTS.keys()) + list(OXEO_POINTS.keys()):
            val = self.mqtt.get(key)
            if val is not None:
                values[key] = val
        return OrpheoData(
            source="mqtt",
            values=values,
            last_mqtt_ts=self.mqtt.last_message_ts,
        )

    # ------------------------------------------------------------------
    # Heartbeat: erkennt MQTT-Disconnect zur Anlage
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> OrpheoData:
        # Wenn der lokale Broker (= Anlage) per paho-mqtt nicht verbunden ist,
        # gilt die Anlage als offline → UpdateFailed → Entities werden unavailable.
        if not self.mqtt.connected:
            age = (
                time.time() - self.mqtt.last_message_ts
                if self.mqtt.last_message_ts
                else float("inf")
            )
            raise UpdateFailed(
                f"Anlage nicht erreichbar (MQTT disconnected, letzte Nachricht vor {age:.0f}s)"
            )

        # Verbindung steht → Snapshot aus dem MQTT-Cache liefern. Auch wenn die
        # Anlage seit Stunden keine neuen Werte publisht (sie publisht nur bei
        # Änderung), bleibt der Zustand verfügbar: TCP-Connection lebt =
        # Anlage erreichbar.
        data = self._build_from_mqtt()
        if data is not None:
            return data

        # Verbunden, aber noch nie Daten empfangen (frischer Start) — vorhandenen
        # State beibehalten, kein UpdateFailed werfen.
        if self.data is not None:
            return self.data
        raise UpdateFailed("Verbunden, aber noch keine MQTT-Daten empfangen")
