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

from .const import (
    CONF_PHILEO_ID,
    DOMAIN,
    ERROR_MAX_DOSE_BIT,
    MANUFACTURER,
    MODEL_COMBINED,
)
from .coordinator import OrpheoVPCoordinator


@dataclass(frozen=True, kw_only=True)
class OrpheoBinarySensorEntityDescription(BinarySensorEntityDescription):
    data_key: str
    # Wenn gesetzt: is_on = (Rohwert & (1<<bit)) statt bool(Rohwert).
    bit: Optional[int] = None


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
        # Echter Live-Status der Hersteller-Cloud-Verbindung. `mqtt_connected`
        # flippt auf 0, sobald die Anlage merkt, dass sie ihre Cloud nicht mehr
        # erreicht; `server_on` (vorher genutzt) ist nur ein Modus-Flag.
        key="ph_mqtt_connected",
        name="Cloud-Verbindung",
        icon="mdi:cloud-check",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="ph_mqtt_connected",
    ),
    # Tageslimit erreicht je Kanal (v2.4.6) = Fehler-Bit 31 (E24,
    # V_MAX_INJECTED) - fuer Automationen/Benachrichtigungen.
    OrpheoBinarySensorEntityDescription(
        key="ph_tageslimit",
        name="pH Tageslimit erreicht",
        icon="mdi:cup-water",
        device_class=BinarySensorDeviceClass.PROBLEM,
        data_key="ph_error",
        bit=ERROR_MAX_DOSE_BIT,
    ),
    OrpheoBinarySensorEntityDescription(
        key="orp_tageslimit",
        name="Chlor Tageslimit erreicht",
        icon="mdi:cup-water",
        device_class=BinarySensorDeviceClass.PROBLEM,
        data_key="orp_error",
        bit=ERROR_MAX_DOSE_BIT,
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
        if self.entity_description.bit is not None:
            return bool(int(val) & (1 << self.entity_description.bit))
        return bool(val)
