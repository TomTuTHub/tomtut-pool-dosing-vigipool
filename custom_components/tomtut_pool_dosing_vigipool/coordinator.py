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

from .const import (
    DEFAULT_NAME,
    DISCONNECT_GRACE,
    DOMAIN,
    OXEO_POINTS,
    PHILEO_POINTS,
    SCAN_INTERVAL,
)
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
        # Merkt sich, ob die ">DISCONNECT_GRACE nicht erreichbar"-Warnung
        # fuer die laufende Offline-Phase schon geloggt wurde (einmal pro
        # Episode, kein Log-Spam pro 30-s-Tick). Reset sobald wieder verbunden.
        self._offline_logged = False

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
        # Entprellte Config-Werte auch im Push-Pfad uebernehmen: unter Dauer-
        # Push (Messwerte alle paar s) terminiert async_set_updated_data den
        # 30-s-Heartbeat staendig neu, sodass _async_update_data kaum feuert -
        # settle_config() muss daher auch hier laufen, sonst settelt
        # vol_bac/vol_max_24h nie.
        self.mqtt.settle_config()
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
        # Entprellte Config-Werte (Behaeltergroesse/Maximaldosis) uebernehmen,
        # sobald sie lange genug stabil sind (Debounce gegen Geraete-Bursts,
        # s. const.py). Laeuft bei jedem Heartbeat-Tick.
        self.mqtt.settle_config()
        # Broker (= Anlage) per paho-mqtt nicht verbunden? Nicht sofort alles
        # auf unavailable werfen: die Anlage betreibt ihren MQTT-Broker selbst
        # auf oft schwachem WLAN und reconnectet via paho automatisch. Solange
        # der Disconnect juenger als DISCONNECT_GRACE ist UND gecachte Werte
        # vorliegen → letzte Werte weiterreichen (Entities bleiben mit dem Stand
        # von eben verfuegbar, kurzer WLAN-Schluckauf bleibt unsichtbar). Erst
        # wenn die Grace abgelaufen ist — oder es nie Daten gab (frischer
        # HA-Start, Anlage aus) — → UpdateFailed → Entities unavailable.
        if not self.mqtt.connected:
            disc_since = self.mqtt.disconnected_since
            cached = self._build_from_mqtt()
            if disc_since and cached is not None:
                if (time.time() - disc_since) < DISCONNECT_GRACE:
                    # Innerhalb der Grace: kurzer Aussetzer. Letzte Werte halten,
                    # kein eigenes Log (paho hat den Disconnect bereits geloggt).
                    return cached
                # Grace gerade abgelaufen → genau EINMAL warnen (beim Uebergang),
                # danach still bis zur Wiederverbindung.
                if not self._offline_logged:
                    _LOGGER.warning(
                        "Anlage seit >%ss nicht erreichbar — Entitaeten gehen auf unavailable",
                        DISCONNECT_GRACE,
                    )
                    self._offline_logged = True
            age = (
                time.time() - self.mqtt.last_message_ts
                if self.mqtt.last_message_ts
                else float("inf")
            )
            raise UpdateFailed(
                f"Anlage nicht erreichbar (MQTT disconnected, letzte Nachricht vor {age:.0f}s)"
            )

        # Verbindung steht → Offline-Warnungs-Flag zuruecksetzen, damit ein
        # spaeterer Ausfall erneut (einmal) warnt.
        self._offline_logged = False

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
