"""Config flow for Orpheo VP integration."""
from __future__ import annotations

import ipaddress
import logging
import socket
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .cloud_api import OrpheoVPApi, VigiPoolApiError, VigiPoolAuthError
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

_LOGGER = logging.getLogger(__name__)


def _user_schema(
    name: str = DEFAULT_NAME,
    host: str = DEFAULT_HOST,
    port: int = MQTT_DEFAULT_PORT,
    phileo_id: str = DEFAULT_PHILEO_ID,
    oxeo_id: str = DEFAULT_OXEO_ID,
    cloud_enabled: bool = False,
    email: str = "",
    password: str = "",
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=name): str,
            vol.Required(CONF_HOST, default=host): str,
            vol.Required(CONF_PORT, default=port): int,
            vol.Required(CONF_PHILEO_ID, default=phileo_id): str,
            vol.Required(CONF_OXEO_ID, default=oxeo_id): str,
            vol.Optional(CONF_CLOUD_ENABLED, default=cloud_enabled): bool,
            vol.Optional(CONF_EMAIL, default=email): str,
            vol.Optional(CONF_PASSWORD, default=password): str,
        }
    )


def _is_valid_device_id(device_id: str) -> bool:
    """Phileo/Oxeo IDs sind die WLAN-MAC ohne Trennzeichen (12 Hex-Zeichen)."""
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
    """Handle the config flow for Orpheo VP."""

    VERSION = 3

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            name = (user_input.get(CONF_NAME) or "").strip() or DEFAULT_NAME
            host = (user_input.get(CONF_HOST) or "").strip()
            port = user_input.get(CONF_PORT, MQTT_DEFAULT_PORT)
            phileo_id = (user_input.get(CONF_PHILEO_ID) or "").strip()
            oxeo_id = (user_input.get(CONF_OXEO_ID) or "").strip()
            cloud_enabled = bool(user_input.get(CONF_CLOUD_ENABLED))
            email = (user_input.get(CONF_EMAIL) or "").strip()
            password = user_input.get(CONF_PASSWORD) or ""

            if not host or not _is_valid_host(host):
                errors["base"] = "invalid_ip"
            elif not _is_valid_device_id(phileo_id) or not _is_valid_device_id(oxeo_id):
                errors["base"] = "invalid_device_id"

            if not errors:
                reachable = await self.hass.async_add_executor_job(_test_mqtt_port, host, port)
                if not reachable:
                    errors["base"] = "cannot_connect"

            cloud_pool_id: str | None = None
            if not errors and cloud_enabled:
                if not email or not password:
                    errors["base"] = "cloud_credentials_required"
                else:
                    session = async_get_clientsession(self.hass)
                    api = OrpheoVPApi(session, email, password)
                    try:
                        await api.login()
                        cloud_pool_id = await api.get_pool_id()
                    except VigiPoolAuthError:
                        errors["base"] = "invalid_auth"
                    except (VigiPoolApiError, aiohttp.ClientError) as err:
                        _LOGGER.error("Cloud check failed: %s", err)
                        errors["base"] = "cannot_connect"

            if not errors:
                await self.async_set_unique_id(phileo_id)
                self._abort_if_unique_id_configured()

                data = {
                    CONF_NAME: name,
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_PHILEO_ID: phileo_id,
                    CONF_OXEO_ID: oxeo_id,
                    CONF_CLOUD_ENABLED: cloud_enabled,
                }
                if cloud_enabled:
                    data[CONF_EMAIL] = email
                    data[CONF_PASSWORD] = password
                    data[CONF_POOL_ID] = cloud_pool_id or phileo_id

                return self.async_create_entry(title=name, data=data)

            return self.async_show_form(
                step_id="user",
                data_schema=_user_schema(
                    name=name,
                    host=host or DEFAULT_HOST,
                    port=port,
                    phileo_id=phileo_id or DEFAULT_PHILEO_ID,
                    oxeo_id=oxeo_id or DEFAULT_OXEO_ID,
                    cloud_enabled=cloud_enabled,
                    email=email,
                    password=password,
                ),
                errors=errors,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> "OrpheoVPOptionsFlow":
        return OrpheoVPOptionsFlow()


class OrpheoVPOptionsFlow(config_entries.OptionsFlow):
    """Reconfigure host, device-IDs and cloud credentials."""

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
                        CONF_PHILEO_ID: (user_input.get(CONF_PHILEO_ID) or "").strip(),
                        CONF_OXEO_ID: (user_input.get(CONF_OXEO_ID) or "").strip(),
                        CONF_CLOUD_ENABLED: bool(user_input.get(CONF_CLOUD_ENABLED)),
                        CONF_EMAIL: (user_input.get(CONF_EMAIL) or "").strip(),
                        CONF_PASSWORD: user_input.get(CONF_PASSWORD) or "",
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=_current(CONF_HOST, DEFAULT_HOST)): str,
                vol.Required(CONF_PORT, default=_current(CONF_PORT, MQTT_DEFAULT_PORT)): int,
                vol.Required(CONF_PHILEO_ID, default=_current(CONF_PHILEO_ID, DEFAULT_PHILEO_ID)): str,
                vol.Required(CONF_OXEO_ID, default=_current(CONF_OXEO_ID, DEFAULT_OXEO_ID)): str,
                vol.Optional(CONF_CLOUD_ENABLED, default=_current(CONF_CLOUD_ENABLED, False)): bool,
                vol.Optional(CONF_EMAIL, default=_current(CONF_EMAIL, "")): str,
                vol.Optional(CONF_PASSWORD, default=_current(CONF_PASSWORD, "")): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
