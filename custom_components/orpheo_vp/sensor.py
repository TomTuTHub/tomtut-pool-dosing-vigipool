"""Sensor platform for Orpheo VP."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_PHILEO_ID, DOMAIN, MANUFACTURER, MODEL_COMBINED
from .coordinator import OrpheoVPCoordinator


@dataclass(frozen=True, kw_only=True)
class OrpheoSensorEntityDescription(SensorEntityDescription):
    data_key: str


SENSOR_DESCRIPTIONS: tuple[OrpheoSensorEntityDescription, ...] = (
    OrpheoSensorEntityDescription(
        key="ph",
        name="pH",
        icon="mdi:ph",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        data_key="ph",
    ),
    OrpheoSensorEntityDescription(
        key="orp",
        name="ORP (Redox)",
        icon="mdi:water-check",
        native_unit_of_measurement="mV",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        data_key="orp",
    ),
    OrpheoSensorEntityDescription(
        key="ph_setpoint",
        name="pH Sollwert",
        icon="mdi:ph",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        data_key="ph_setpoint",
    ),
    OrpheoSensorEntityDescription(
        key="orp_setpoint",
        name="ORP Sollwert",
        icon="mdi:water-check",
        native_unit_of_measurement="mV",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        data_key="orp_setpoint",
    ),
    OrpheoSensorEntityDescription(
        key="ph_vol_24h",
        name="pH Dosierung heute",
        icon="mdi:water-pump",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        device_class=SensorDeviceClass.VOLUME,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        data_key="ph_vol_24h",
    ),
    OrpheoSensorEntityDescription(
        key="orp_vol_24h",
        name="Chlor Dosierung heute",
        icon="mdi:water-pump",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        device_class=SensorDeviceClass.VOLUME,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        data_key="orp_vol_24h",
    ),
    OrpheoSensorEntityDescription(
        key="ph_vol_total",
        name="pH Dosierung gesamt",
        icon="mdi:counter",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        device_class=SensorDeviceClass.VOLUME,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        data_key="ph_vol_total",
    ),
    OrpheoSensorEntityDescription(
        key="orp_vol_total",
        name="Chlor Dosierung gesamt",
        icon="mdi:counter",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        device_class=SensorDeviceClass.VOLUME,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        data_key="orp_vol_total",
    ),
    OrpheoSensorEntityDescription(
        key="ph_rssi",
        name="pH WLAN Signal",
        icon="mdi:wifi",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="ph_rssi",
    ),
    OrpheoSensorEntityDescription(
        key="orp_rssi",
        name="ORP WLAN Signal",
        icon="mdi:wifi",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="orp_rssi",
    ),
    OrpheoSensorEntityDescription(
        key="ph_sw_vers",
        name="pH Firmware",
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="ph_sw_vers",
    ),
    OrpheoSensorEntityDescription(
        key="orp_sw_vers",
        name="ORP Firmware",
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="orp_sw_vers",
    ),
    OrpheoSensorEntityDescription(
        key="ph_error",
        name="pH Fehlercode",
        icon="mdi:alert-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="ph_error",
    ),
    OrpheoSensorEntityDescription(
        key="orp_error",
        name="ORP Fehlercode",
        icon="mdi:alert-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="orp_error",
    ),
    OrpheoSensorEntityDescription(
        key="ph_state",
        name="pH State",
        icon="mdi:state-machine",
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="ph_state",
    ),
    OrpheoSensorEntityDescription(
        key="ph_mode",
        name="pH Mode",
        icon="mdi:cog-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="ph_mode",
    ),
    OrpheoSensorEntityDescription(
        key="orp_mode",
        name="ORP Mode",
        icon="mdi:cog-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="orp_mode",
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
        OrpheoVPSensor(coordinator, description, pool_id)
        for description in SENSOR_DESCRIPTIONS
    )


class OrpheoVPSensor(CoordinatorEntity[OrpheoVPCoordinator], SensorEntity):
    entity_description: OrpheoSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OrpheoVPCoordinator,
        description: OrpheoSensorEntityDescription,
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
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.data_key)
