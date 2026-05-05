"""Number platform for Orpheo VP (Sollwerte, Behaeltergroesse)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
    RestoreNumber,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_PHILEO_ID, DOMAIN, MANUFACTURER, MODEL_COMBINED
from .coordinator import OrpheoVPCoordinator


@dataclass(frozen=True, kw_only=True)
class OrpheoNumberEntityDescription(NumberEntityDescription):
    data_key: str
    writable_key: str


NUMBER_DESCRIPTIONS: tuple[OrpheoNumberEntityDescription, ...] = (
    OrpheoNumberEntityDescription(
        key="ph_setpoint_write",
        name="pH Sollwert",
        icon="mdi:ph",
        # Limits wie in der Poolsana-App: 6.8 - 7.6 in 0.1 Schritten
        native_min_value=6.8,
        native_max_value=7.6,
        native_step=0.1,
        mode=NumberMode.BOX,
        data_key="ph_setpoint",
        writable_key="ph_setpoint",
    ),
    OrpheoNumberEntityDescription(
        key="orp_setpoint_write",
        name="ORP Sollwert",
        icon="mdi:water-check",
        native_unit_of_measurement="mV",
        native_min_value=500,
        native_max_value=750,
        native_step=10,
        mode=NumberMode.BOX,
        data_key="orp_setpoint",
        writable_key="orp_setpoint",
    ),
    OrpheoNumberEntityDescription(
        key="ph_vol_bac_write",
        name="pH Behaeltergroesse",
        icon="mdi:barrel",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        native_min_value=1,
        native_max_value=60,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        data_key="ph_vol_bac",
        writable_key="ph_vol_bac",
    ),
    OrpheoNumberEntityDescription(
        key="orp_vol_bac_write",
        name="Chlor Behaeltergroesse",
        icon="mdi:barrel",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        native_min_value=1,
        native_max_value=60,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        data_key="orp_vol_bac",
        writable_key="orp_vol_bac",
    ),
    OrpheoNumberEntityDescription(
        key="ph_vol_max_24h_write",
        name="pH Maximaldosis / Tag",
        icon="mdi:speedometer",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        # 0 = Deaktivieren (wie in der Poolsana-App), sonst 0.1 - 3.0 L/Tag
        native_min_value=0,
        native_max_value=3.0,
        native_step=0.1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        data_key="ph_vol_max_24h",
        writable_key="ph_vol_max_24h",
    ),
    OrpheoNumberEntityDescription(
        key="orp_vol_max_24h_write",
        name="Chlor Maximaldosis / Tag",
        icon="mdi:speedometer",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        # 0 = Deaktivieren (wie in der Poolsana-App), sonst 0.1 - 5.0 L/Tag
        native_min_value=0,
        native_max_value=5.0,
        native_step=0.1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        data_key="orp_vol_max_24h",
        writable_key="orp_vol_max_24h",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: OrpheoVPCoordinator = hass.data[DOMAIN][entry.entry_id]
    pool_id = entry.data[CONF_PHILEO_ID]

    entities: list = [
        OrpheoVPNumber(coordinator, description, pool_id)
        for description in NUMBER_DESCRIPTIONS
    ]
    entities.append(
        OrpheoRestmengeNumber(
            coordinator, pool_id,
            key="ph_restmenge",
            name="pH Restmenge",
            delta_key="ph_vol_total",
            capacity_key="ph_vol_bac",
        )
    )
    entities.append(
        OrpheoRestmengeNumber(
            coordinator, pool_id,
            key="chlor_restmenge",
            name="Chlor Restmenge",
            delta_key="orp_vol_total",
            capacity_key="orp_vol_bac",
        )
    )
    async_add_entities(entities)


class OrpheoVPNumber(CoordinatorEntity[OrpheoVPCoordinator], NumberEntity):
    entity_description: OrpheoNumberEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OrpheoVPCoordinator,
        description: OrpheoNumberEntityDescription,
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
    def native_value(self) -> Optional[float]:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.data_key)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.mqtt.async_write(self.entity_description.writable_key, value)


class OrpheoRestmengeNumber(CoordinatorEntity[OrpheoVPCoordinator], RestoreNumber):
    """Restmenge im Kanister — HA-seitig persistiert, auto-dekrementiert.

    Das Geraet liefert nur `vol_tot_inject` (Lebensdauer-Gesamtverbrauch) und
    `vol_bac` (konfigurierte Behaeltergroesse). "Wieviel ist noch drin" ist
    daher nur berechenbar wenn wir wissen wann zuletzt nachgefuellt wurde.

    Diese Entity merkt sich den Restfuellstand persistent (RestoreNumber).
    Bei jedem Coordinator-Update ziehen wir die Differenz zum letzten
    beobachteten `vol_tot_inject` ab. Wenn der User physikalisch nachfuellt,
    setzt er den Wert manuell hoch (z.B. auf die Behaeltergroesse).
    """

    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX
    _attr_native_unit_of_measurement = UnitOfVolume.LITERS
    _attr_native_step = 0.1
    _attr_native_min_value = 0.0
    _attr_icon = "mdi:water-percent"

    def __init__(
        self,
        coordinator: OrpheoVPCoordinator,
        pool_id: str,
        key: str,
        name: str,
        delta_key: str,
        capacity_key: str,
    ) -> None:
        super().__init__(coordinator)
        self._pool_id = pool_id
        self._attr_unique_id = f"{pool_id}_{key}"
        self._attr_name = name
        self._attr_translation_key = key
        self._delta_key = delta_key
        self._capacity_key = capacity_key
        self._last_total: Optional[float] = None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, pool_id)},
            name=coordinator.device_name,
            manufacturer=MANUFACTURER,
            model=MODEL_COMBINED,
        )

    @property
    def native_max_value(self) -> float:
        """Dynamischer Max-Wert = aktuelle Behaeltergroesse (fallback 60L)."""
        if self.coordinator.data is None:
            return 60.0
        cap = self.coordinator.data.get(self._capacity_key)
        return float(cap) if cap and cap > 0 else 60.0

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_number_data()
        if last is not None and last.native_value is not None:
            self._attr_native_value = float(last.native_value)
        # Baseline fuer Delta-Berechnung: aktueller vol_total-Wert als Startpunkt
        if self.coordinator.data is not None:
            cur = self.coordinator.data.get(self._delta_key)
            if cur is not None:
                self._last_total = float(cur)

    async def async_set_native_value(self, value: float) -> None:
        """User setzt den Fuellstand manuell (z.B. nach Nachfuellen)."""
        self._attr_native_value = max(0.0, float(value))
        self.async_write_ha_state()

    def _handle_coordinator_update(self) -> None:
        """Bei jedem Coordinator-Update: Delta gegen letzten vol_total ausrechnen."""
        if self.coordinator.data is None:
            return
        cur = self.coordinator.data.get(self._delta_key)
        if cur is None:
            return
        cur = float(cur)

        if self._last_total is None:
            # Erst-Init — nur Baseline merken, nicht dekrementieren
            self._last_total = cur
            self.async_write_ha_state()
            return

        delta = cur - self._last_total
        self._last_total = cur

        # Negativ-Deltas (Device-Reboot, Counter-Reset) ignorieren
        if delta <= 0:
            self.async_write_ha_state()
            return

        if self._attr_native_value is not None:
            self._attr_native_value = max(0.0, self._attr_native_value - delta)

        self.async_write_ha_state()
