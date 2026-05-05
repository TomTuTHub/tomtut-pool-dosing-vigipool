"""Binary sensor platform for Orpheo VP."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_PHILEO_ID, DOMAIN, MANUFACTURER, MODEL_COMBINED
from .coordinator import OrpheoVPCoordinator


@dataclass(frozen=True, kw_only=True)
class OrpheoBinarySensorEntityDescription(BinarySensorEntityDescription):
    data_key: str


BINARY_SENSOR_DESCRIPTIONS: tuple[OrpheoBinarySensorEntityDescription, ...] = (
    OrpheoBinarySensorEntityDescription(
        key="ph_inject_on",
        name="pH Dosierpumpe",
        icon="mdi:pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        data_key="ph_inject_on",
    ),
    OrpheoBinarySensorEntityDescription(
        key="orp_inject_on",
        name="Chlor Dosierpumpe",
        icon="mdi:pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        data_key="orp_inject_on",
    ),
    OrpheoBinarySensorEntityDescription(
        key="ph_flow_on",
        name="Durchfluss",
        icon="mdi:waves",
        device_class=BinarySensorDeviceClass.MOVING,
        data_key="ph_flow_on",
    ),
    OrpheoBinarySensorEntityDescription(
        key="ph_server_on",
        name="Cloud-Verbindung",
        icon="mdi:cloud-check",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="ph_server_on",
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
        OrpheoVPBinarySensor(coordinator, description, pool_id)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class OrpheoVPBinarySensor(CoordinatorEntity[OrpheoVPCoordinator], BinarySensorEntity):
    entity_description: OrpheoBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OrpheoVPCoordinator,
        description: OrpheoBinarySensorEntityDescription,
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
        if val is None:
            return None
        return bool(val)
