"""Constants for the Orpheo VP integration (lokales MQTT, kein Cloud-Pfad)."""

DOMAIN = "tomtut_pool_dosing_vigipool"

# Polling / Health-Intervalle
SCAN_INTERVAL = 30                  # Coordinator-Heartbeat (s): erkennt
                                    # MQTT-Disconnect innerhalb von ~30s.
MQTT_KEEPALIVE = 15                 # paho-mqtt Keepalive (s): Anlage als
                                    # offline markieren wenn 3 Keepalives
                                    # ohne PINGRESP — also ~45s.
MQTT_DEFAULT_PORT = 1883

# Grace-Period (s) nach einem MQTT-Disconnect: solange die letzte
# Verbindung nicht laenger als DISCONNECT_GRACE her ist UND gecachte
# Werte vorliegen, behaelt der Coordinator die letzten Werte bei
# (Entities bleiben verfuegbar), statt bei jedem kurzen WLAN-Schluckauf
# auf unavailable zu springen. Die Anlage betreibt ihren MQTT-Broker
# selbst (oft schwaches WLAN) und reconnectet via paho automatisch; erst
# wenn sie laenger als DISCONNECT_GRACE weg ist, gelten die Entities als
# unavailable.
DISCONNECT_GRACE = 180

# Geraete-Sentinels auf u16-Messwerten: die Rohwerte 0xFFFE/0xFFFF
# signalisieren einen Messfehler / ungueltigen Wert (beobachtet:
# sensor.ph zeigte 655.34 = Rohwert 65534). Solche Rohwerte werden auf
# den Messpunkten verworfen; der Cache behaelt den letzten gueltigen Wert.
SENTINEL_RAW_VALUES = frozenset({0xFFFE, 0xFFFF})   # 65534, 65535
# NUR echte Live-Messwerte filtern — NICHT Zaehler (vol_*), Config/
# Behaeltergroesse oder Firmware-Version (dort sind hohe Werte legitim).
SENTINEL_FILTER_KEYS = frozenset({"ph", "orp"})

# ---------------------------------------------------------------------------
# Fehlercode-Bitmaske -> Klartext (v2.4.6)
#
# Die Anlage publiziert auf .../error/info/reported eine u32-Bitmaske. Die
# Bedeutung EINZELNER Bits ist bewusst konservativ gemappt: nur was belegt
# ist, bekommt Text - alle anderen Bits bleiben als "Bit N" sichtbar (nie
# verschlucken).
#
# HERKUNFT DER ZUORDNUNG (Doku-Pflicht, Thomas 2026-07-14):
# - Bit 31 (0x80000000) = "Tagesmaximaldosis erreicht":
#   * EMPIRISCH BEWIESEN an Thomas' Anlage 2026-07-14: pH-Fehlercode
#     2147483648 exakt zeitgleich mit App-Push "E24" + Pumpe ausser Betrieb
#     (HA-Aktivitaet 09:04:53). Gilt fuer beide Kanaele (ORP-Fehlercode
#     2147483648 ebenfalls in den HA-Exportdaten beobachtet).
#   * Text nach CCEI-Key V_MAX_INJECTED ("Das Maximalvolumen des injizierten
#     Produkts wurde erreicht" / EN "Max volume of injected product in 24h
#     reached"). Quelle: github.com/developer-ccei-pool/jeedom-vigipool
#     @ 51d6d5c9 (2024-08-09), core/template/js/language_german.js:398,
#     abgerufen 2026-07-14.
#
# WEITERE CCEI-FEHLERTEXTE (Referenz, bewusst NICHT bit-gebunden): der
# CCEI-Code dekodiert die Bitmaske NICHT client-seitig - die E-Codes kommen
# als Cloud-Push, die Bit-Positionen sind unbelegt. Daher hier nur als
# dokumentierte Referenz (Quelle jeweils language_german.js @ 51d6d5c9),
# bis eine Zuordnung empirisch bestaetigt ist:
#   PH_ERROR_MESURE_29 (Z.399) "Es werden Fehler bei den pH-Messungen
#     festgestellt, die Injektion wird gestoppt, bitte ueberpruefen Sie Ihre
#     Anlage und die Sonden."
#   ORP_ERROR_MESURE_27 (Z.401) analog fuer ORP-Messungen.
#   RS485_ERROR / code_E9 (Z.407) "... Kommunikationsfehler (RS485) ..."
#   TEMP_HIGH (Z.385) / TEMP_LOW (Z.386) Temperatur-Messfehler.
# Beobachtet, Bedeutung unbelegt: ORP-Bit 24 (0x01000000), Mai/Juni 2026.
# ---------------------------------------------------------------------------
ERROR_MAX_DOSE_BIT = 31  # V_MAX_INJECTED / E24 - Tagesmaximaldosis (bewiesen)

ERROR_BIT_TEXTS: dict[int, str] = {
    ERROR_MAX_DOSE_BIT: "Tagesmaximaldosis erreicht",
}


def format_error_bitmask(raw) -> str:
    """u32-Fehler-Bitmaske -> lesbarer deutscher Text. Bekannte Bits als
    Klartext, unbekannte Bits als 'Bit N' (nie verschlucken). 0 -> 'OK'."""
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return "unbekannt"
    if value == 0:
        return "OK"
    parts: list[str] = []
    for bit in range(32):
        if value & (1 << bit):
            parts.append(ERROR_BIT_TEXTS.get(bit, f"Bit {bit}"))
    return ", ".join(parts)


# Config-Werte (Behaeltergroesse, Maximaldosis/Tag) kommen vom Geraet in
# kurzen Bursts von Zwischenwerten (empirisch: vol_bac springt
# 26->30->36->44->48->57->60 in ~0,11 s, HA-Export 2026-05-14 14:53:41) -
# App-Slider-/Streaming-Artefakte, KEIN Integrations-Bug (Topic/Subtype/Scale
# sind identisch zu CCEIs Installer-Template daisyph.yaml/daisyox.yaml,
# vol_bac/info, value_template *0.01). Darum werden diese Werte entprellt:
# erst nach CONFIG_DEBOUNCE Sekunden Ruhe (kein neuer Wert) uebernimmt
# settle_config() den zuletzt gesehenen Wert. Messwerte/Zaehler sind NICHT
# betroffen.
CONFIG_DEBOUNCE = 12  # s
CONFIG_DEBOUNCE_KEYS = frozenset({
    "ph_vol_bac", "orp_vol_bac", "ph_vol_max_24h", "orp_vol_max_24h",
})

# Config entry keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_NAME = "name"
CONF_PHILEO_ID = "phileo_id"
CONF_OXEO_ID = "oxeo_id"

# Defaults — nur generisch. Geraetespezifische Werte (IP, MACs) muss der
# User selbst eintragen, damit die Integration HACS-tauglich bleibt.
DEFAULT_NAME = "Orpheo VP Pool Dosieranlage"
DEFAULT_HOST = ""
DEFAULT_PHILEO_ID = ""
DEFAULT_OXEO_ID = ""

# MQTT-Attribute-Namen
ATTR_ORP = "value_orp"
ATTR_PH = "value_ph"
ATTR_INJECT_ON = "inject_on"

# Device model names
MODEL_PHILEO_VP = "Phileo VP"
MODEL_OXEO_VP = "Oxeo VP"
MODEL_COMBINED = "Vigipool Orpheo VP"
MANUFACTURER = "Vigipool / Poolsana"

# ---------------------------------------------------------------------------
# MQTT Topic-Schema
#
# Geraet = Broker, liefert Topics wie:
#   phileox_<MAC>/u16_r/value_ph/value/reported
#   phileox_<MAC>/u16_w/consigne_ph/consigne/desired
#
# Fuer Schreibzugriffe publishen wir den Rohwert (int als string) auf
# den `.../desired` Topic.
# ---------------------------------------------------------------------------

PHILEO_PREFIX = "phileox_"
OXEO_PREFIX = "oxeox_"


def phileo_topic(device_id: str, dtype: str, name: str, subtype: str, direction: str) -> str:
    return f"{PHILEO_PREFIX}{device_id}/{dtype}/{name}/{subtype}/{direction}"


def oxeo_topic(device_id: str, dtype: str, name: str, subtype: str, direction: str) -> str:
    return f"{OXEO_PREFIX}{device_id}/{dtype}/{name}/{subtype}/{direction}"


def phileo_sub_filter(device_id: str) -> str:
    return f"{PHILEO_PREFIX}{device_id}/#"


def oxeo_sub_filter(device_id: str) -> str:
    return f"{OXEO_PREFIX}{device_id}/#"


# Namensraum fuer den internen MQTT-Cache (Key = Kurzname):
#
# Jeder Eintrag:
#   short_name -> (dtype, name, subtype, scale, writable)
#
# `reported` wird gelesen, `desired` geschrieben (falls writable=True).
# `scale` ist der Faktor, um den der Rohwert beim Lesen geteilt wird
# (bzw. beim Schreiben multipliziert).

# scale = None bedeutet "kein Scaling" (Rohwert 1:1).
# subtype: str fuer identische Read/Write-Subtypes; tuple[str,str] fuer
# asymmetrische — (read_subtype, write_subtype). Hintergrund siehe
# `_split_subtype` in mqtt_client.py.
PHILEO_POINTS: dict[str, tuple[str, str, str | tuple[str, str], float | None, bool]] = {
    "ph":                 ("u16_r", "value_ph",              "value",    100.0, False),
    # consigne_ph: Geraet echo't den Live-Wert auf `info/reported`, nicht auf
    # `consigne/reported` (das traegt einen stehengebliebenen Absolutwert).
    # Schreibwege gehen weiterhin auf `consigne/desired`.
    "ph_setpoint":        ("u16_w", "consigne_ph",           ("info", "consigne"), 100.0, True),
    "ph_inject_on":       ("u8_r",  "inject_on",             "value",    None,  False),
    "ph_flow_on":         ("u8_r",  "flow_on",               "value",    None,  False),
    "ph_vol_24h":         ("u16_r", "vol_24h_inject",        "info",     100.0, False),
    "ph_vol_total":       ("u16_r", "vol_tot_inject",        "value",    None,  False),
    "ph_vol_bac":         ("u16_w", "vol_bac",               "info",     100.0, True),
    "ph_vol_max_24h":     ("u16_w", "vol_max_24h",           "info",     100.0, True),
    "ph_mode":            ("u8_r",  "mode_ph",               "info",     None,  False),
    "ph_spa_mode":        ("u8_w",  "spa_mode",              "info",     None,  True),
    "ph_winter_mode":     ("u8_w",  "winter_mode",           "info",     None,  True),
    # Echter Live-Status der Cloud-Verbindung der Anlage:
    "ph_mqtt_connected":  ("u8_r",  "mqtt_connected",        "info",     None,  False),
    "ph_rssi":            ("i8_r",  "rssi",                  "info",     None,  False),
    "ph_error":           ("u32_r", "error",                 "info",     None,  False),
    "ph_state":           ("u32_r", "state",                 "info",     None,  False),
    "ph_sw_vers":         ("u16_r", "sw_vers",               "info",     None,  False),
}

OXEO_POINTS: dict[str, tuple[str, str, str | tuple[str, str], float | None, bool]] = {
    "orp":                ("u16_r", "value_orp",             "value",    None,  False),
    # consigne_orp: gleiches Muster wie consigne_ph — Echo auf `info/reported`,
    # Schreiben auf `consigne/desired`. Live verifiziert via MQTT-Probe 2026-05-14.
    "orp_setpoint":       ("u16_w", "consigne_orp",          ("info", "consigne"), None, True),
    "orp_inject_on":      ("u8_r",  "inject_on",             "value",    None,  False),
    "orp_vol_24h":        ("u16_r", "vol_24h_inject",        "info",     100.0, False),
    "orp_vol_total":      ("u16_r", "vol_tot_inject",        "value",    None,  False),
    "orp_vol_bac":        ("u16_w", "vol_bac",               "info",     100.0, True),
    "orp_vol_max_24h":    ("u16_w", "vol_max_24h",           "info",     100.0, True),
    "orp_mode":           ("u8_r",  "mode_orp",              "info",     None,  False),
    "orp_spa_mode":       ("u8_w",  "spa_mode",              "info",     None,  True),
    "orp_winter_mode":    ("u8_w",  "winter_mode",           "info",     None,  True),
    "orp_rssi":           ("i8_r",  "rssi",                  "info",     None,  False),
    "orp_error":          ("u32_r", "error",                 "info",     None,  False),
    "orp_sw_vers":        ("u16_r", "sw_vers",               "info",     None,  False),
}
