"""Switch platform for Orpheo VP (Spa- und Winter-Modus)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_PHILEO_ID, DOMAIN, MANUFACTURER, MODEL_COMBINED
from .coordinator import OrpheoVPCoordinator


@dataclass(frozen=True, kw_only=True)
class OrpheoSwitchEntityDescription(SwitchEntityDescription):
    data_key: str
    writable_keys: tuple[str, ...]  # Beide Geraete parallel setzen (Phileo + Oxeo)


SWITCH_DESCRIPTIONS: tuple[OrpheoSwitchEntityDescription, ...] = (
    OrpheoSwitchEntityDescription(
        key="spa_mode",
        name="Spa-Modus",
        icon="mdi:hot-tub",
        device_class=SwitchDeviceClass.SWITCH,
        data_key="ph_spa_mode",
        writable_keys=("ph_spa_mode", "orp_spa_mode"),
    ),
    OrpheoSwitchEntityDescription(
        key="winter_mode",
        name="Winter-Modus",
        icon="mdi:snowflake",
        device_class=SwitchDeviceClass.SWITCH,
        data_key="ph_winter_mode",
        writable_keys=("ph_winter_mode", "orp_winter_mode"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: OrpheoVPCoordinator = hass.data[DOMAIN][entry.entry_id]
    pool_id = entry.data[CONF_PHILEO_ID]

    async_add_entities(
        OrpheoVPSwitch(coordinator, description, pool_id)
        for description in SWITCH_DESCRIPTIONS
    )


class OrpheoVPSwitch(CoordinatorEntity[OrpheoVPCoordinator], SwitchEntity):
    entity_description: OrpheoSwitchEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OrpheoVPCoordinator,
        description: OrpheoSwitchEntityDescription,
        pool_id: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._pool_id = pool_id
        self._attr_unique_id = f"{pool_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, pool_id)},
            name=coordinator.device_name,
            manufacturer=MANUFACTURER,
            model=MODEL_COMBINED,
        )

    @property
    def is_on(self) -> Optional[bool]:
        if self.coordinator.data is None:
            return None
        val = self.coordinator.data.get(self.entity_description.data_key)
        return bool(val) if val is not None else None

    async def async_turn_on(self, **kwargs) -> None:
        for key in self.entity_description.writable_keys:
            await self.coordinator.mqtt.async_write(key, 1)

    async def async_turn_off(self, **kwargs) -> None:
        for key in self.entity_description.writable_keys:
            await self.coordinator.mqtt.async_write(key, 0)
