"""The Orpheo VP integration (MQTT lokal + Cloud Fallback)."""
from __future__ import annotations

import logging
from typing import Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .cloud_api import OrpheoVPApi
from .const import (
    CONF_CLOUD_ENABLED,
    CONF_EMAIL,
    CONF_HOST,
    CONF_NAME,
    CONF_OXEO_ID,
    CONF_PASSWORD,
    CONF_PHILEO_ID,
    CONF_POOL_ID,
    CONF_PORT,
    DEFAULT_HOST,
    DEFAULT_NAME,
    DEFAULT_OXEO_ID,
    DEFAULT_PHILEO_ID,
    DOMAIN,
    MQTT_DEFAULT_PORT,
)
from .coordinator import OrpheoVPCoordinator
from .mqtt_client import OrpheoMqttClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Orpheo VP from a config entry."""
    # OptionsFlow-Werte haben Vorrang vor initialen data-Werten
    def _cfg(key: str, default):
        return entry.options.get(key, entry.data.get(key, default))

    device_name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    host = _cfg(CONF_HOST, DEFAULT_HOST)
    port = _cfg(CONF_PORT, MQTT_DEFAULT_PORT)
    phileo_id = _cfg(CONF_PHILEO_ID, DEFAULT_PHILEO_ID)
    oxeo_id = _cfg(CONF_OXEO_ID, DEFAULT_OXEO_ID)

    mqtt_client = OrpheoMqttClient(hass, host, port, phileo_id, oxeo_id)

    cloud_api: Optional[OrpheoVPApi] = None
    cloud_pool_id: Optional[str] = None
    if _cfg(CONF_CLOUD_ENABLED, False) and _cfg(CONF_EMAIL, ""):
        session = async_get_clientsession(hass)
        cloud_api = OrpheoVPApi(
            session,
            _cfg(CONF_EMAIL, ""),
            _cfg(CONF_PASSWORD, ""),
        )
        cloud_pool_id = _cfg(CONF_POOL_ID, "") or phileo_id

    coordinator = OrpheoVPCoordinator(hass, mqtt_client, cloud_api, cloud_pool_id)
    coordinator.device_name = device_name

    await mqtt_client.async_start()

    # Erst-Refresh: MQTT braucht eventuell ein paar Sekunden bis Daten reinkommen;
    # _async_update_data faellt auf Cloud zurueck oder liefert leere Daten.
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Erst-Refresh fehlgeschlagen (wird spaeter erneut versucht): %s", err)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    entry.async_on_unload(_make_unload_hook(mqtt_client))
    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload integration when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)


def _make_unload_hook(mqtt_client: OrpheoMqttClient):
    async def _unload() -> None:
        await mqtt_client.async_stop()
    return _unload


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migriert alte Config-Entries: V1 (Cloud-only) -> V2 (MQTT) -> V3 (+ CONF_NAME)."""
    _LOGGER.info("Orpheo VP Config-Entry Migration: aktuelle Version=%s", entry.version)
    data = dict(entry.data)

    if entry.version < 2:
        data = {
            CONF_HOST: DEFAULT_HOST,
            CONF_PORT: MQTT_DEFAULT_PORT,
            CONF_PHILEO_ID: data.get(CONF_POOL_ID) or DEFAULT_PHILEO_ID,
            CONF_OXEO_ID: DEFAULT_OXEO_ID,
            CONF_CLOUD_ENABLED: bool(data.get(CONF_EMAIL)),
            **({CONF_EMAIL: data[CONF_EMAIL], CONF_PASSWORD: data.get(CONF_PASSWORD, ""),
                CONF_POOL_ID: data.get(CONF_POOL_ID) or DEFAULT_PHILEO_ID}
               if data.get(CONF_EMAIL) else {}),
        }

    if entry.version < 3 and CONF_NAME not in data:
        data[CONF_NAME] = DEFAULT_NAME

    hass.config_entries.async_update_entry(
        entry, data=data, title=data.get(CONF_NAME, entry.title), version=3
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
