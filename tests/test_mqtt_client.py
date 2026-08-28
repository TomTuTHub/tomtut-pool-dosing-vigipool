#!/usr/bin/env python3
"""Standalone-Tests fuer den MQTT-Client der Orpheo-VP-Integration.

Laeuft OHNE Home Assistant und ohne pytest:

    python3 tests/test_mqtt_client.py

Getestet werden die echten Modul-Funktionen (`const.py`, `mqtt_client.py`)
gegen synthetische MQTT-Nachrichten. Nur die paho-Client-Klasse wird durch
einen Dummy ersetzt, damit kein Netzwerk noetig ist und die Tests unabhaengig
von der installierten paho-Major-Version laufen.

Abgedeckt (v2.4.7):
  * Sollwert aus zwei Quellen (retained Snapshot + Aenderungs-Echo)
  * Sentinel-Filter auf Config-/Sollwert-Punkten
  * Regressionsschutz: Lebensdauer-Zaehler bleiben ungefiltert
  * Regressionsschutz: Config-Debounce funktioniert weiter
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import types

BASE = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "tomtut_pool_dosing_vigipool"

# Die Integration als eigenstaendiges Paket laden, ohne ihr __init__.py
# auszufuehren (das wuerde Home Assistant importieren).
_pkg = types.ModuleType("vigi")
_pkg.__path__ = [str(BASE)]
sys.modules["vigi"] = _pkg


def _load(name):
    spec = importlib.util.spec_from_file_location(f"vigi.{name}", BASE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"vigi.{name}"] = mod
    spec.loader.exec_module(mod)
    return mod


const = _load("const")

# paho-Client neutralisieren (kein Netz, keine API-Versions-Abhaengigkeit)
import paho.mqtt.client as _paho


class _DummyPahoClient:
    def __init__(self, *a, **kw):
        self.on_connect = self.on_disconnect = self.on_message = None


_paho.Client = _DummyPahoClient

mqtt_client = _load("mqtt_client")

PH = "AABBCCDDEEFF"   # Platzhalter — keine echte Geraete-MAC im Repo
OX = "112233445566"   # dito


class _Msg:
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = str(payload).encode()


def new_client():
    return mqtt_client.OrpheoMqttClient(
        hass=None, host="192.0.2.1", port=1883, phileo_id=PH, oxeo_id=OX
    )


def send(cl, topic, payload):
    cl._on_message(None, None, _Msg(topic, payload))


# Topic-Kurzschreibweisen
def ph_t(name, sub):
    return f"phileox_{PH}/{name}/{sub}/reported"


def ox_t(name, sub):
    return f"oxeox_{OX}/{name}/{sub}/reported"


SETPOINT_SNAPSHOT = ph_t("u16_w/consigne_ph", "consigne")
SETPOINT_LIVE = ph_t("u16_w/consigne_ph", "info")

_results: list[tuple[bool, str, str]] = []


def check(name, got, want):
    ok = got == want
    _results.append((ok, name, "" if ok else f"erwartet {want!r}, bekommen {got!r}"))


# ---------------------------------------------------------------------------
# FIX 1 — Sollwert aus zwei Quellen
# ---------------------------------------------------------------------------

def t_snapshot_only():
    """HA-Neustart bei laufender Anlage: nur der retained Snapshot kommt an."""
    cl = new_client()
    send(cl, SETPOINT_SNAPSHOT, 740)
    check("1a Snapshot allein -> Sollwert sofort da", cl.get("ph_setpoint"), 7.4)


def t_live_only():
    """Sollwert wird geaendert, waehrend HA laeuft: nur das Aenderungs-Echo."""
    cl = new_client()
    send(cl, SETPOINT_LIVE, 720)
    check("1b Live-Echo allein", cl.get("ph_setpoint"), 7.2)


def t_snapshot_then_live():
    """Normalfall: erst Snapshot beim Connect, dann eine echte Aenderung."""
    cl = new_client()
    send(cl, SETPOINT_SNAPSHOT, 740)
    send(cl, SETPOINT_LIVE, 720)
    check("1c Snapshot dann Live -> Live gewinnt", cl.get("ph_setpoint"), 7.2)


def t_stale_snapshot_after_live():
    """KERN-REGRESSION: Nach einer Aenderung liefert ein MQTT-Reconnect den
    retained Snapshot erneut aus — mit dem ALTEN Wert. Er darf den frisch
    gesetzten Sollwert nicht zurueckdrehen."""
    cl = new_client()
    send(cl, SETPOINT_LIVE, 720)
    send(cl, SETPOINT_SNAPSHOT, 740)  # veralteter Retain nach Reconnect
    check("1d Veralteter Snapshot nach Live -> ignoriert", cl.get("ph_setpoint"), 7.2)


def t_nothing():
    """Weder Snapshot noch Echo: Cache leer, Entity faellt auf RestoreState."""
    cl = new_client()
    check("1e Keine Quelle -> None (RestoreState greift)", cl.get("ph_setpoint"), None)


def t_orp_snapshot():
    """Gleicher Mechanismus am ORP-Kanal (scale=None, Rohwert in mV)."""
    cl = new_client()
    send(cl, ox_t("u16_w/consigne_orp", "consigne"), 690)
    check("1f ORP-Snapshot", cl.get("orp_setpoint"), 690.0)


def t_orp_stale_snapshot():
    cl = new_client()
    send(cl, ox_t("u16_w/consigne_orp", "info"), 670)
    send(cl, ox_t("u16_w/consigne_orp", "consigne"), 690)
    check("1g ORP: veralteter Snapshot ignoriert", cl.get("orp_setpoint"), 670.0)


def t_live_after_live():
    """Innerhalb der Live-Quelle gewinnt weiterhin die juengste Nachricht."""
    cl = new_client()
    send(cl, SETPOINT_LIVE, 720)
    send(cl, SETPOINT_LIVE, 730)
    check("1h Zwei Live-Werte -> juengster gewinnt", cl.get("ph_setpoint"), 7.3)


# ---------------------------------------------------------------------------
# FIX 2 — Sentinel-Filter auf Config-/Sollwert-Punkten
# ---------------------------------------------------------------------------

def t_sentinel_vol_bac():
    """65535 auf vol_bac = 'nie konfiguriert' -> verwerfen (war: 655,35 L)."""
    cl = new_client()
    send(cl, ph_t("u16_w/vol_bac", "info"), 65535)
    check("2a vol_bac 65535 -> kein Wert", cl.get("ph_vol_bac"), None)
    check("2b vol_bac 65535 -> nicht im Debounce-Pending",
          "ph_vol_bac" in cl._pending_config, False)
    cl.settle_config(now=1e12)  # auch nach Ablauf darf nichts einrasten
    check("2c vol_bac 65535 -> settlet auch spaeter nicht", cl.get("ph_vol_bac"), None)


def t_sentinel_vol_bac_orp():
    cl = new_client()
    send(cl, ox_t("u16_w/vol_bac", "info"), 65534)
    check("2d ORP vol_bac 65534 -> kein Wert", cl.get("orp_vol_bac"), None)


def t_sentinel_vol_max():
    cl = new_client()
    send(cl, ph_t("u16_w/vol_max_24h", "info"), 65535)
    check("2e vol_max_24h 65535 -> kein Wert", cl.get("ph_vol_max_24h"), None)


def t_sentinel_setpoint():
    cl = new_client()
    send(cl, SETPOINT_SNAPSHOT, 65535)
    check("2f Sollwert 65535 -> kein Wert", cl.get("ph_setpoint"), None)


def t_vol_total_not_filtered():
    """REGRESSIONSSCHUTZ: Der Lebensdauer-Zaehler laeuft in Hundertstel-Litern
    und erreicht 65535 nach ~6,4 Jahren regulaer — hier darf NICHT gefiltert
    werden, sonst ist es Datenverlust."""
    cl = new_client()
    send(cl, ph_t("u16_r/vol_tot_inject", "value"), 65535)
    check("2g vol_total 65535 -> NICHT gefiltert", cl.get("ph_vol_total"), 65535.0)
    cl2 = new_client()
    send(cl2, ox_t("u16_r/vol_tot_inject", "value"), 65534)
    check("2h ORP vol_total 65534 -> NICHT gefiltert", cl2.get("orp_vol_total"), 65534.0)


def t_measurement_sentinel_still_works():
    """Bestandsverhalten aus v2.4.5 bleibt erhalten."""
    cl = new_client()
    send(cl, ph_t("u16_r/value_ph", "value"), 731)
    send(cl, ph_t("u16_r/value_ph", "value"), 65534)
    check("2i Messwert-Sentinel -> letzter gueltiger Wert bleibt", cl.get("ph"), 7.31)


def t_debounce_still_works():
    """Gueltige Config-Werte werden weiterhin entprellt (v2.4.5/2.4.6)."""
    cl = new_client()
    send(cl, ph_t("u16_w/vol_bac", "info"), 1500)
    check("2j Gueltiger vol_bac -> erst pending", cl.get("ph_vol_bac"), None)
    check("2k ... und steht im Pending", "ph_vol_bac" in cl._pending_config, True)
    cl.settle_config(now=1e12)
    check("2l ... nach Ruhephase uebernommen", cl.get("ph_vol_bac"), 15.0)


def main():
    for fn in (
        t_snapshot_only, t_live_only, t_snapshot_then_live,
        t_stale_snapshot_after_live, t_nothing, t_orp_snapshot,
        t_orp_stale_snapshot, t_live_after_live,
        t_sentinel_vol_bac, t_sentinel_vol_bac_orp, t_sentinel_vol_max,
        t_sentinel_setpoint, t_vol_total_not_filtered,
        t_measurement_sentinel_still_works, t_debounce_still_works,
    ):
        fn()

    failed = 0
    for ok, name, detail in _results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ""))
        failed += 0 if ok else 1
    total = len(_results)
    print(f"\n{total - failed}/{total} Checks bestanden")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
