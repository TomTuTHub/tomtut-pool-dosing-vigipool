"""The Orpheo VP integration — ausschließlich lokales MQTT, keine Cloud."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.instance_id import async_get as async_get_instance_id

from .const import (
    CONF_HOST,
    CONF_NAME,
    CONF_OXEO_ID,
    CONF_PHILEO_ID,
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

STATIC_URL_PATH = "/api/tomtut_pool_dosing_vigipool/static"
STATIC_REGISTRATION_KEY = "static_path_registered"

# Legacy keys aus früheren Versionen (V1–V3). Bei Migration entfernt.
_LEGACY_CLOUD_KEYS = ("cloud_enabled", "email", "password", "pool_id")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Orpheo VP from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})

    if not domain_data.get(STATIC_REGISTRATION_KEY):
        static_dir = Path(__file__).parent / "static"
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    STATIC_URL_PATH,
                    str(static_dir),
                    cache_headers=False,
                ),
            ]
        )
        domain_data[STATIC_REGISTRATION_KEY] = True

    # OptionsFlow-Werte haben Vorrang vor initialen data-Werten
    def _cfg(key: str, default):
        return entry.options.get(key, entry.data.get(key, default))

    device_name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    host = _cfg(CONF_HOST, DEFAULT_HOST)
    port = _cfg(CONF_PORT, MQTT_DEFAULT_PORT)
    phileo_id = _cfg(CONF_PHILEO_ID, DEFAULT_PHILEO_ID)
    oxeo_id = _cfg(CONF_OXEO_ID, DEFAULT_OXEO_ID)

    instance_id = await async_get_instance_id(hass)
    mqtt_client = OrpheoMqttClient(
        hass, host, port, phileo_id, oxeo_id,
        instance_suffix=instance_id[:8],
    )

    coordinator = OrpheoVPCoordinator(hass, mqtt_client)
    coordinator.device_name = device_name

    await mqtt_client.async_start()

    # Erst-Refresh: wenn MQTT noch keine Daten liefert, läuft der Coordinator
    # mit `last_update_success=False` weiter — Entities sind dann unavailable
    # bis das erste reported reinkommt. Bewusst kein blockierender Wait.
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning(
            "Erst-Refresh fehlgeschlagen (Anlage offline?). "
            "Coordinator versucht weiter, Entities zeigen 'nicht verfügbar': %s",
            err,
        )

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
    """Config-Entry Migration.

    V1 (Cloud-only) → V2 (MQTT lokal + optionaler Cloud-Fallback) → V3 (CONF_NAME)
    V3 → V4 (Cloud-Pfad komplett entfernt — ab v2.4.0 nur noch lokales MQTT).
    Legacy Cloud-Felder werden aus data/options entfernt.
    """
    _LOGGER.info("Orpheo VP Config-Entry Migration: aktuelle Version=%s", entry.version)
    data = dict(entry.data)
    options = dict(entry.options or {})

    if entry.version < 2:
        # V1 → V2: pool_id wurde zur phileo_id, Cloud-Fallback war optional
        data = {
            CONF_HOST: DEFAULT_HOST,
            CONF_PORT: MQTT_DEFAULT_PORT,
            CONF_PHILEO_ID: data.get("pool_id") or DEFAULT_PHILEO_ID,
            CONF_OXEO_ID: DEFAULT_OXEO_ID,
        }

    if entry.version < 3 and CONF_NAME not in data:
        data[CONF_NAME] = DEFAULT_NAME

    if entry.version < 4:
        # V4: alle Cloud-Reste raus
        for k in _LEGACY_CLOUD_KEYS:
            data.pop(k, None)
            options.pop(k, None)

    hass.config_entries.async_update_entry(
        entry,
        data=data,
        options=options,
        title=data.get(CONF_NAME, entry.title),
        version=4,
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
