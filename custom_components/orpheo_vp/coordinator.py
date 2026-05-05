"""DataUpdateCoordinator fuer Orpheo VP.

Primaer: MQTT push (Geraet = Broker, IP konfigurierbar).
Fallback: Cloud-Polling auf supervision.vigipool.com wenn MQTT-Daten veraltet sind.
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .cloud_api import OrpheoVPApi, PoolData as CloudPoolData, VigiPoolApiError, VigiPoolAuthError
from .const import DEFAULT_NAME, DOMAIN, MQTT_STALE_AFTER, OXEO_POINTS, PHILEO_POINTS, SCAN_INTERVAL
from .mqtt_client import OrpheoMqttClient

_LOGGER = logging.getLogger(__name__)


@dataclass
class OrpheoData:
    """Zusammengefuehrte Sicht auf alle Datenpunkte."""

    source: str = "init"                # "mqtt", "cloud", "init"
    values: dict[str, float] = field(default_factory=dict)
    last_mqtt_ts: float = 0.0

    def get(self, key: str) -> Optional[float]:
        return self.values.get(key)


class OrpheoVPCoordinator(DataUpdateCoordinator[OrpheoData]):
    """Haelt MQTT + Cloud-Fallback zusammen."""

    def __init__(
        self,
        hass: HomeAssistant,
        mqtt_client: OrpheoMqttClient,
        cloud_api: Optional[OrpheoVPApi],
        cloud_pool_id: Optional[str],
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.mqtt = mqtt_client
        self._cloud_api = cloud_api
        self._cloud_pool_id = cloud_pool_id
        self._cloud_session_valid = False
        self.device_name: str = DEFAULT_NAME

        mqtt_client.set_update_callback(self._mqtt_push_callback)

    # ------------------------------------------------------------------
    # MQTT push -> Coordinator
    # ------------------------------------------------------------------

    def _mqtt_push_callback(self) -> None:
        """Wird aus dem paho-Thread aufgerufen. Thread-safe via call_soon_threadsafe."""
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
    # Periodic poll (Cloud-Fallback)
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> OrpheoData:
        # 1. Wenn MQTT frisch: MQTT-Snapshot liefern.
        now = time.time()
        mqtt_age = now - self.mqtt.last_message_ts if self.mqtt.last_message_ts else float("inf")

        if self.mqtt.has_any_data() and mqtt_age < MQTT_STALE_AFTER:
            data = self._build_from_mqtt()
            if data is not None:
                return data

        # 2. MQTT ist stale oder leer -> Cloud-Fallback versuchen.
        if self._cloud_api is None or self._cloud_pool_id is None:
            # Kein Cloud-Fallback konfiguriert — vorhandene Daten beibehalten
            if self.data is not None:
                _LOGGER.debug("MQTT stale (age=%.0fs) — kein Cloud-Fallback, alten State halten", mqtt_age)
                return self.data
            raise UpdateFailed("Keine MQTT-Daten und kein Cloud-Fallback konfiguriert")

        try:
            if not self._cloud_session_valid:
                await self._cloud_api.login()
                self._cloud_session_valid = True
            cloud_data: CloudPoolData = await self._cloud_api.get_pool_data(self._cloud_pool_id)
        except VigiPoolAuthError:
            self._cloud_session_valid = False
            raise UpdateFailed("Vigipool-Session abgelaufen")
        except VigiPoolApiError as err:
            raise UpdateFailed(f"Vigipool API error: {err}") from err

        # Cloud -> OrpheoData mappen
        values: dict[str, float] = {}
        if cloud_data.ph is not None:
            values["ph"] = cloud_data.ph
        if cloud_data.orp is not None:
            values["orp"] = cloud_data.orp
        if cloud_data.ph_inject_on is not None:
            values["ph_inject_on"] = 1.0 if cloud_data.ph_inject_on else 0.0
        if cloud_data.orp_inject_on is not None:
            values["orp_inject_on"] = 1.0 if cloud_data.orp_inject_on else 0.0
        if cloud_data.ph_setpoint is not None:
            values["ph_setpoint"] = cloud_data.ph_setpoint
        if cloud_data.orp_setpoint is not None:
            values["orp_setpoint"] = cloud_data.orp_setpoint

        return OrpheoData(source="cloud", values=values, last_mqtt_ts=self.mqtt.last_message_ts)
