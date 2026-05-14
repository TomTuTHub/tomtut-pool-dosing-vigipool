"""Config flow for Orpheo VP integration — lokal-only, keine Cloud-Felder."""
from __future__ import annotations

import ipaddress
import logging
import re
import socket
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback

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
from .discovery import async_discover

_LOGGER = logging.getLogger(__name__)


def _step_user_schema(
    name: str = DEFAULT_NAME,
    host: str = DEFAULT_HOST,
    port: int = MQTT_DEFAULT_PORT,
) -> vol.Schema:
    """First step: Name + Verbindung (Host, Port). Keine Cloud-Felder."""
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=name): str,
            vol.Required(CONF_HOST, default=host): str,
            vol.Required(CONF_PORT, default=port): int,
        }
    )


def _step_devices_schema(phileo_id: str = "", oxeo_id: str = "") -> vol.Schema:
    """Second step: device IDs (auto-prefilled from MQTT discovery)."""
    return vol.Schema(
        {
            vol.Required(CONF_PHILEO_ID, default=phileo_id): str,
            vol.Required(CONF_OXEO_ID, default=oxeo_id): str,
        }
    )


def _normalize_device_id(value: str | None) -> str:
    """MAC mit oder ohne Trennzeichen → 12 Hex-Zeichen uppercase."""
    if not value:
        return ""
    return re.sub(r"[\s:.\-]", "", value).upper()


def _is_valid_device_id(device_id: str) -> bool:
    if not device_id or len(device_id) != 12:
        return False
    try:
        int(device_id, 16)
        return True
    except ValueError:
        return False


def _is_valid_host(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return bool(host) and all(c.isalnum() or c in ".-_" for c in host)


def _test_mqtt_port(host: str, port: int) -> bool:
    s = socket.socket()
    s.settimeout(5)
    try:
        s.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


class OrpheoVPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Two-step config flow: connection + auto-discovered device IDs."""

    VERSION = 4

    def __init__(self) -> None:
        self._user_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            name = (user_input.get(CONF_NAME) or "").strip() or DEFAULT_NAME
            host = (user_input.get(CONF_HOST) or "").strip()
            port = user_input.get(CONF_PORT, MQTT_DEFAULT_PORT)

            if not host or not _is_valid_host(host):
                errors["base"] = "invalid_ip"

            if not errors:
                reachable = await self.hass.async_add_executor_job(_test_mqtt_port, host, port)
                if not reachable:
                    errors["base"] = "cannot_connect"

            if not errors:
                self._user_data = {
                    CONF_NAME: name,
                    CONF_HOST: host,
                    CONF_PORT: port,
                }
                return await self.async_step_devices()

            return self.async_show_form(
                step_id="user",
                data_schema=_step_user_schema(name=name, host=host or DEFAULT_HOST, port=port),
                errors=errors,
            )

        return self.async_show_form(step_id="user", data_schema=_step_user_schema())

    async def async_step_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}
        host = self._user_data[CONF_HOST]
        port = self._user_data[CONF_PORT]

        if user_input is None:
            # Auto-discovery on entering the step (~6s subscribed to '#')
            discovered = await async_discover(self.hass, host, port)
            phileo_found = discovered.get("phileo_id", "")
            oxeo_found = discovered.get("oxeo_id", "")
            _LOGGER.info(
                "Auto-discovery on %s:%s — phileo=%s oxeo=%s",
                host, port, phileo_found or "—", oxeo_found or "—",
            )

            def _fmt(mac: str) -> str:
                return ":".join(mac[i:i + 2] for i in range(0, 12, 2))

            return self.async_show_form(
                step_id="devices",
                data_schema=_step_devices_schema(phileo_found, oxeo_found),
                description_placeholders={
                    "phileo_status": (
                        f"✅ erkannt (`{_fmt(phileo_found)}`)"
                        if phileo_found
                        else "❌ nicht erkannt — bitte unten manuell eingeben"
                    ),
                    "oxeo_status": (
                        f"✅ erkannt (`{_fmt(oxeo_found)}`)"
                        if oxeo_found
                        else "❌ nicht erkannt — bitte unten manuell eingeben"
                    ),
                },
            )

        phileo_id = _normalize_device_id(user_input.get(CONF_PHILEO_ID))
        oxeo_id = _normalize_device_id(user_input.get(CONF_OXEO_ID))

        if not _is_valid_device_id(phileo_id) or not _is_valid_device_id(oxeo_id):
            errors["base"] = "invalid_device_id"
            return self.async_show_form(
                step_id="devices",
                data_schema=_step_devices_schema(phileo_id, oxeo_id),
                errors=errors,
                description_placeholders={
                    "phileo_status": "⚠️ bitte korrigieren",
                    "oxeo_status": "⚠️ bitte korrigieren",
                },
            )

        await self.async_set_unique_id(phileo_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=self._user_data[CONF_NAME],
            data={
                CONF_NAME: self._user_data[CONF_NAME],
                CONF_HOST: host,
                CONF_PORT: port,
                CONF_PHILEO_ID: phileo_id,
                CONF_OXEO_ID: oxeo_id,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> "OrpheoVPOptionsFlow":
        return OrpheoVPOptionsFlow()


class OrpheoVPOptionsFlow(config_entries.OptionsFlow):
    """Reconfigure host, port and device-IDs (lokal-only)."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}
        entry = self.config_entry

        def _current(key: str, default: Any) -> Any:
            return entry.options.get(key, entry.data.get(key, default))

        if user_input is not None:
            host = (user_input.get(CONF_HOST) or "").strip()
            port = user_input.get(CONF_PORT, MQTT_DEFAULT_PORT)

            if not _is_valid_host(host):
                errors["base"] = "invalid_ip"
            else:
                reachable = await self.hass.async_add_executor_job(_test_mqtt_port, host, port)
                if not reachable:
                    errors["base"] = "cannot_connect"

            if not errors:
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_PHILEO_ID: _normalize_device_id(user_input.get(CONF_PHILEO_ID)),
                        CONF_OXEO_ID: _normalize_device_id(user_input.get(CONF_OXEO_ID)),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=_current(CONF_HOST, DEFAULT_HOST)): str,
                vol.Required(CONF_PORT, default=_current(CONF_PORT, MQTT_DEFAULT_PORT)): int,
                vol.Required(CONF_PHILEO_ID, default=_current(CONF_PHILEO_ID, DEFAULT_PHILEO_ID)): str,
                vol.Required(CONF_OXEO_ID, default=_current(CONF_OXEO_ID, DEFAULT_OXEO_ID)): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
