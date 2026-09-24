#!/usr/bin/env python3
"""Regressionstest v2.4.9: Restore der Tageszaehler "Dosierung heute".

Laeuft OHNE Home Assistant und ohne pytest (HA-Module werden minimal gestubbt):

    python3 -W error::DeprecationWarning tests/test_restore_daily.py

Prueft die echte `sensor.py`-Logik (async_added_to_hass + native_value):
  * gleicher lokaler Kalendertag -> letzter Wert wird uebernommen
  * Vortag -> NICHT uebernommen (bleibt unknown/None)
  * Tagesgrenze in LOKALER Zeit (Europe/Berlin), nicht UTC
  * Live-Wert vom Coordinator ueberschreibt den restaurierten Wert
  * Sollwert-Restore (v2.4.7) unveraendert, Gesamtzaehler restaurieren nicht
  * state_class / Einheit der betroffenen Sensoren unveraendert
"""
from __future__ import annotations

import asyncio
import enum
import importlib.util
import pathlib
import sys
import types
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

warnings.simplefilter("error", DeprecationWarning)

BASE = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "tomtut_pool_dosing_vigipool"
TZ = ZoneInfo("Europe/Berlin")


# ---- minimale HA-Stubs ----------------------------------------------------
def _mod(name, **attrs):
    m = types.ModuleType(name)
    m.__dict__.update(attrs)
    sys.modules[name] = m
    return m


class SensorDeviceClass(str, enum.Enum):
    VOLUME = "volume"
    SIGNAL_STRENGTH = "signal_strength"


class SensorStateClass(str, enum.Enum):
    MEASUREMENT = "measurement"
    TOTAL_INCREASING = "total_increasing"


@dataclass(frozen=True, kw_only=True)
class SensorEntityDescription:
    key: str
    name: str | None = None
    icon: str | None = None
    native_unit_of_measurement: str | None = None
    device_class: object = None
    state_class: object = None
    suggested_display_precision: int | None = None
    entity_category: object = None


class _Stored:
    def __init__(self, native_value):
        self.native_value = native_value


class _State:
    def __init__(self, state, last_updated):
        self.state = state
        self.last_updated = last_updated


class SensorEntity:
    pass


class RestoreSensor(SensorEntity):
    # vom Test pro Entity gesetzt: (native_value, last_updated) oder None
    _test_last = None
    writes = 0

    async def async_added_to_hass(self):
        pass

    async def async_get_last_state(self):
        if self._test_last is None:
            return None
        return _State(str(self._test_last[0]), self._test_last[1])

    async def async_get_last_sensor_data(self):
        if self._test_last is None:
            return None
        return _Stored(self._test_last[0])

    def async_write_ha_state(self):
        self.writes += 1


class CoordinatorEntity:
    def __class_getitem__(cls, item):
        return cls

    def __init__(self, coordinator):
        self.coordinator = coordinator

    async def async_added_to_hass(self):
        await super().async_added_to_hass()


class UnitOfVolume(str, enum.Enum):
    LITERS = "L"


class EntityCategory(str, enum.Enum):
    DIAGNOSTIC = "diagnostic"


_NOW = [datetime(2026, 9, 24, 8, 0, tzinfo=TZ)]

_mod("homeassistant")
_mod("homeassistant.components")
_mod("homeassistant.components.sensor", RestoreSensor=RestoreSensor, SensorDeviceClass=SensorDeviceClass,
     SensorEntity=SensorEntity, SensorEntityDescription=SensorEntityDescription, SensorStateClass=SensorStateClass)
_mod("homeassistant.config_entries", ConfigEntry=object)
_mod("homeassistant.const", PERCENTAGE="%", SIGNAL_STRENGTH_DECIBELS_MILLIWATT="dBm", UnitOfVolume=UnitOfVolume)
_mod("homeassistant.core", HomeAssistant=object)
_mod("homeassistant.helpers")
_mod("homeassistant.helpers.entity", DeviceInfo=dict, EntityCategory=EntityCategory)
_mod("homeassistant.helpers.entity_platform", AddEntitiesCallback=object)
_mod("homeassistant.helpers.update_coordinator", CoordinatorEntity=CoordinatorEntity)
_mod("homeassistant.util", dt=_mod("homeassistant.util.dt", now=lambda: _NOW[0]))

# Integration als Paket laden, ohne __init__.py / coordinator.py (HA, paho)
_pkg = types.ModuleType("vigi"); _pkg.__path__ = [str(BASE)]; sys.modules["vigi"] = _pkg
_mod("vigi.coordinator", OrpheoVPCoordinator=object)


def _load(name):
    spec = importlib.util.spec_from_file_location(f"vigi.{name}", BASE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"vigi.{name}"] = mod
    spec.loader.exec_module(mod)
    return mod


const = _load("const")
sensor = _load("sensor")

DESC = {d.key: d for d in sensor.SENSOR_DESCRIPTIONS}


class FakeCoordinator:
    device_name = "Test"

    def __init__(self, data=None):
        self.data = data


def make(key, last=None, data=None):
    ent = sensor.OrpheoVPSensor(FakeCoordinator(data), DESC[key], "AABBCCDDEEFF")
    ent._test_last = last
    asyncio.run(ent.async_added_to_hass())
    return ent


ok = 0


def check(cond, text):
    global ok
    print(("PASS " if cond else "FAIL ") + text)
    assert cond, text
    ok += 1


# ---- Beschreibungen ---------------------------------------------------------
flagged = {k for k, d in DESC.items() if d.restore_same_day}
check(flagged == {"ph_vol_24h", "orp_vol_24h"}, "nur ph_vol_24h + orp_vol_24h tragen restore_same_day")
for k in ("ph_vol_24h", "orp_vol_24h"):
    d = DESC[k]
    check(d.state_class == SensorStateClass.TOTAL_INCREASING and d.native_unit_of_measurement == UnitOfVolume.LITERS
          and d.device_class == SensorDeviceClass.VOLUME and not d.restore,
          f"{k}: state_class/Einheit/device_class unveraendert, kein Sollwert-Restore")

# ---- Helfer (reine Funktion) -------------------------------------------------
now = datetime(2026, 9, 24, 8, 0, tzinfo=TZ)
f = const.restored_daily_value_is_current
check(f(datetime(2026, 9, 24, 5, 0, tzinfo=timezone.utc), now), "Helfer: heute (UTC-Stempel) -> True")
check(not f(datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc), now), "Helfer: gestern -> False")
check(f(datetime(2026, 9, 23, 22, 30, tzinfo=timezone.utc), now), "Helfer: 22:30 UTC = 00:30 lokal heute -> True (lokale Tagesgrenze)")
check(not f(datetime(2026, 9, 23, 21, 30, tzinfo=timezone.utc), now), "Helfer: 21:30 UTC = 23:30 lokal gestern -> False")
check(not f(None, now) and not f(datetime(2026, 9, 24, 5, 0), now), "Helfer: fehlender/naiver Zeitstempel -> False")

# ---- Entity: Restore-Pfad ----------------------------------------------------
_NOW[0] = now
for k in ("ph_vol_24h", "orp_vol_24h"):
    e = make(k, last=(0.61, datetime(2026, 9, 24, 6, 15, tzinfo=timezone.utc)))
    check(e.native_value == 0.61 and e.writes == 1, f"{k}: gleicher Tag -> 0.61 uebernommen + State geschrieben")

    e = make(k, last=(0.88, datetime(2026, 9, 23, 18, 0, tzinfo=timezone.utc)))
    check(e.native_value is None and e.writes == 0, f"{k}: Vortag -> NICHT uebernommen (unknown)")

    e = make(k, last=(0.88, datetime(2026, 9, 23, 21, 59, tzinfo=timezone.utc)))
    check(e.native_value is None, f"{k}: 23:59 lokal gestern -> NICHT uebernommen")

    e = make(k, last=None)
    check(e.native_value is None and e.writes == 0, f"{k}: kein gespeicherter State -> unknown, kein Crash")

    e = make(k, last=(0.61, datetime(2026, 9, 24, 6, 15, tzinfo=timezone.utc)), data={k: 0.95})
    check(e.native_value == 0.95, f"{k}: Live-Wert ueberschreibt restaurierten Wert")

    e = make(k, last=(0.61, datetime(2026, 9, 24, 6, 15, tzinfo=timezone.utc)), data={})
    e.coordinator.data = {k: 0.0}
    check(e.native_value == 0.0, f"{k}: spaeterer Live-Wert 0.0 (Tagesreset) gewinnt gegen Restore")

# ---- Regressionsschutz -------------------------------------------------------
e = make("ph_setpoint", last=(7.2, datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)))
check(e.native_value == 7.2, "Sollwert-Restore (v2.4.7) weiterhin tagesunabhaengig")
e = make("ph_vol_total", last=(25.0, datetime(2026, 9, 24, 6, 0, tzinfo=timezone.utc)))
check(e.native_value is None and e.writes == 0, "Gesamtzaehler restauriert NICHT (unveraendert)")
e = make("ph", last=(7.1, datetime(2026, 9, 24, 6, 0, tzinfo=timezone.utc)))
check(e.native_value is None, "Messwert pH restauriert NICHT (unveraendert)")

print(f"{ok}/{ok} Checks bestanden, keine DeprecationWarning")
