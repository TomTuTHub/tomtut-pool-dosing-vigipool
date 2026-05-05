"""Vigipool supervision.vigipool.com API client."""
from __future__ import annotations

import csv
import io
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

import aiohttp

from .const import (
    ATTR_INJECT_ON,
    ATTR_ORP,
    ATTR_PH,
    BASE_URL,
    DASHBOARD_URL,
    LOGIN_URL,
    POOL_DETAIL_URL,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    device_id: str
    model: str


@dataclass
class PoolData:
    ph: Optional[float] = None
    orp: Optional[float] = None
    ph_inject_on: Optional[bool] = None
    orp_inject_on: Optional[bool] = None
    ph_device_id: Optional[str] = None
    orp_device_id: Optional[str] = None
    # Setpoints from page
    ph_setpoint: Optional[float] = None
    orp_setpoint: Optional[float] = None


class VigiPoolApiError(Exception):
    """Raised when the API returns an error."""


class VigiPoolAuthError(VigiPoolApiError):
    """Raised when authentication fails."""


class OrpheoVPApi:
    """Client for the Vigipool supervision portal."""

    def __init__(self, session: aiohttp.ClientSession, email: str, password: str) -> None:
        self._session = session
        self._email = email
        self._password = password
        self._csrf_token: str | None = None

    async def _get_csrf_token(self) -> str:
        """Fetch the login page and extract the CSRF token."""
        async with self._session.get(LOGIN_URL) as resp:
            if resp.status != 200:
                raise VigiPoolApiError(f"Login page returned {resp.status}")
            html = await resp.text()

        match = re.search(r'name="_token"\s+value="([^"]+)"', html)
        if not match:
            raise VigiPoolApiError("Could not find CSRF token on login page")
        return match.group(1)

    async def login(self) -> None:
        """Authenticate with the supervision portal."""
        token = await self._get_csrf_token()

        data = {
            "_token": token,
            "email": self._email,
            "password": self._password,
        }

        async with self._session.post(LOGIN_URL, data=data, allow_redirects=True) as resp:
            final_url = str(resp.url)
            if "account_login" in final_url or resp.status in (401, 403):
                raise VigiPoolAuthError("Login failed — check email/password")
            if "dashboard" not in final_url:
                raise VigiPoolApiError(f"Unexpected redirect after login: {final_url}")

        _LOGGER.debug("Logged in to supervision.vigipool.com")

    async def get_pool_id(self) -> str:
        """Fetch dashboard and extract the main pool device ID."""
        async with self._session.get(DASHBOARD_URL) as resp:
            if resp.status == 401 or resp.status == 403:
                raise VigiPoolAuthError("Session expired")
            html = await resp.text()

        # The dashboard lists devices with data-deviceid attribute
        match = re.search(r'data-deviceid="([0-9A-F]{12})"', html)
        if not match:
            raise VigiPoolApiError("Could not find pool device ID on dashboard")
        pool_id = match.group(1)
        _LOGGER.debug("Found pool_id: %s", pool_id)
        return pool_id

    async def get_pool_devices(self, pool_id: str) -> dict[str, DeviceInfo]:
        """
        Fetch pool detail page and extract all connected device IDs and models.
        Returns dict: {device_id: DeviceInfo}
        """
        url = f"{POOL_DETAIL_URL}/{pool_id}"
        async with self._session.get(url) as resp:
            if resp.status in (401, 403):
                raise VigiPoolAuthError("Session expired")
            if resp.status != 200:
                raise VigiPoolApiError(f"pool_detail returned {resp.status}")
            html = await resp.text()

        devices: dict[str, DeviceInfo] = {}

        # Extract all device IDs and their inject_on values (which reveals device roles)
        # Format: {"deviceId":"08D1F9976534","attribute":"inject_on","label":"..."}
        for match in re.finditer(
            r'\{"deviceId":"([0-9A-F]{12})","attribute":"inject_on","label":"([^"]+)"\}', html
        ):
            device_id = match.group(1)
            label = match.group(2)
            # Extract model name from label (e.g. "Phileo VP - Injection en cours")
            model = label.split(" - ")[0].strip()
            devices[device_id] = DeviceInfo(device_id=device_id, model=model)

        # Also extract ph_devices and orp_devices from JS
        ph_match = re.search(r'let ph_devices\s*=\s*\[([^\]]+)\]', html)
        orp_match = re.search(r'let orp_devices\s*=\s*\[([^\]]+)\]', html)

        ph_devices = re.findall(r'"([0-9A-F]{12})"', ph_match.group(1)) if ph_match else []
        orp_devices = re.findall(r'"([0-9A-F]{12})"', orp_match.group(1)) if orp_match else []

        _LOGGER.debug("pH devices: %s, ORP devices: %s", ph_devices, orp_devices)

        return devices, ph_devices, orp_devices

    async def _fetch_graph_csv(self, device_id: str, attribute: str) -> list[str]:
        """
        Fetch the latest value via the multi_graph endpoint.
        Returns list of CSV rows (excluding header).
        """
        # Use inject_on as secondary attribute (it's always available)
        url = f"{POOL_DETAIL_URL}/multi_graph/{device_id}/{attribute}/{device_id}/{ATTR_INJECT_ON}/0"
        async with self._session.get(url) as resp:
            if resp.status in (401, 403):
                raise VigiPoolAuthError("Session expired")
            if resp.status != 200:
                raise VigiPoolApiError(f"multi_graph returned {resp.status}")
            text = await resp.text()

        lines = [line for line in text.strip().splitlines() if line.strip()]
        return lines  # First line is header

    async def get_pool_data(
        self,
        pool_id: str,
        ph_device_id: str | None = None,
        orp_device_id: str | None = None,
    ) -> PoolData:
        """Poll current sensor values from the supervision portal."""
        data = PoolData(ph_device_id=ph_device_id or pool_id, orp_device_id=orp_device_id or pool_id)

        # Fetch pH
        if data.ph_device_id:
            try:
                rows = await self._fetch_graph_csv(data.ph_device_id, ATTR_PH)
                if len(rows) > 1:
                    reader = csv.DictReader(io.StringIO("\n".join(rows)))
                    for row in reader:
                        ph_val = row.get("value_ph", "").strip()
                        inject = row.get(ATTR_INJECT_ON, "").strip()
                        if ph_val:
                            data.ph = float(ph_val)
                        if inject:
                            data.ph_inject_on = inject == "1"
            except Exception as err:
                _LOGGER.warning("Failed to fetch pH: %s", err)

        # Fetch ORP
        if data.orp_device_id:
            try:
                rows = await self._fetch_graph_csv(data.orp_device_id, ATTR_ORP)
                if len(rows) > 1:
                    reader = csv.DictReader(io.StringIO("\n".join(rows)))
                    for row in reader:
                        orp_val = row.get("value_orp", "").strip()
                        inject = row.get(ATTR_INJECT_ON, "").strip()
                        if orp_val:
                            data.orp = float(orp_val)
                        if inject:
                            data.orp_inject_on = inject == "1"
            except Exception as err:
                _LOGGER.warning("Failed to fetch ORP: %s", err)

        # Also get setpoints from pool detail page
        try:
            url = f"{POOL_DETAIL_URL}/{pool_id}"
            async with self._session.get(url) as resp:
                html = await resp.text()

            ph_setpoint_match = re.search(r'Consigne pH</th>\s*<td[^>]*>([\d.]+)</td>', html)
            orp_setpoint_match = re.search(r'Consigne Orp</th>\s*<td[^>]*>(\d+)</td>', html)
            ph_tbl_match = re.search(r'<th>pH</th>\s*<td[^>]*>([\d.]+)</td>', html)
            orp_tbl_match = re.search(r'<th>ORP</th>\s*<td[^>]*>(\d+)</td>', html)

            if ph_setpoint_match:
                data.ph_setpoint = float(ph_setpoint_match.group(1))
            if orp_setpoint_match:
                data.orp_setpoint = float(orp_setpoint_match.group(1))
            # Fallback: use table values if graph CSV had no data
            if data.ph is None and ph_tbl_match:
                data.ph = float(ph_tbl_match.group(1))
            if data.orp is None and orp_tbl_match:
                data.orp = float(orp_tbl_match.group(1))
        except Exception as err:
            _LOGGER.warning("Failed to parse pool detail HTML: %s", err)

        _LOGGER.debug("Pool data: %s", data)
        return data
