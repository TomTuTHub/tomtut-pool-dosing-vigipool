"""Constants for the Orpheo VP integration."""

DOMAIN = "tomtut_pool_dosing_vigipool"

# Cloud API (Fallback)
BASE_URL = "https://supervision.vigipool.com"
LOGIN_URL = f"{BASE_URL}/account_login"
DASHBOARD_URL = f"{BASE_URL}/dashboard"
POOL_DETAIL_URL = f"{BASE_URL}/pool_detail"

# Polling intervals
SCAN_INTERVAL = 120                 # Cloud fallback poll interval (s)
MQTT_STALE_AFTER = 300              # MQTT-Daten gelten nach X s als veraltet
MQTT_DEFAULT_PORT = 1883

# Config entry keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_NAME = "name"
CONF_PHILEO_ID = "phileo_id"
CONF_OXEO_ID = "oxeo_id"
CONF_CLOUD_ENABLED = "cloud_enabled"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_POOL_ID = "pool_id"

# Defaults — nur generisch. Geraetespezifische Werte (IP, MACs) muss der
# User selbst eintragen, damit die Integration HACS-tauglich bleibt.
DEFAULT_NAME = "Orpheo VP Pool Dosieranlage"
DEFAULT_HOST = ""
DEFAULT_PHILEO_ID = ""
DEFAULT_OXEO_ID = ""

# Data attributes (Cloud-API Legacy)
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
    "ph_vol_24h":         ("u16_r", "vol_24h_inject",        "value",    100.0, False),
    "ph_vol_total":       ("u16_r", "vol_tot_inject",        "value",    100.0, False),
    "ph_vol_bac":         ("u16_w", "vol_bac",               "info",     100.0, True),
    "ph_vol_max_24h":     ("u16_w", "vol_max_24h",           "info",     100.0, True),
    "ph_mode":            ("u8_r",  "mode_ph",               "info",     None,  False),
    "ph_spa_mode":        ("u8_w",  "spa_mode",              "info",     None,  True),
    "ph_winter_mode":     ("u8_w",  "winter_mode",           "info",     None,  True),
    "ph_server_on":       ("u8_r",  "server_on",             "info",     None,  False),
    "ph_rssi":            ("i8_r",  "rssi",                  "info",     None,  False),
    "ph_error":           ("u32_r", "error",                 "info",     None,  False),
    "ph_state":           ("u32_r", "state",                 "info",     None,  False),
    "ph_sw_vers":         ("u16_r", "sw_vers",               "info",     None,  False),
}

OXEO_POINTS: dict[str, tuple[str, str, str | tuple[str, str], float | None, bool]] = {
    "orp":                ("u16_r", "value_orp",             "value",    None,  False),
    "orp_setpoint":       ("u16_w", "consigne_orp",          "consigne", None,  True),
    "orp_inject_on":      ("u8_r",  "inject_on",             "value",    None,  False),
    "orp_vol_24h":        ("u16_r", "vol_24h_inject",        "value",    100.0, False),
    "orp_vol_total":      ("u16_r", "vol_tot_inject",        "value",    100.0, False),
    "orp_vol_bac":        ("u16_w", "vol_bac",               "info",     100.0, True),
    "orp_vol_max_24h":    ("u16_w", "vol_max_24h",           "info",     100.0, True),
    "orp_mode":           ("u8_r",  "mode_orp",              "info",     None,  False),
    "orp_spa_mode":       ("u8_w",  "spa_mode",              "info",     None,  True),
    "orp_winter_mode":    ("u8_w",  "winter_mode",           "info",     None,  True),
    "orp_rssi":           ("i8_r",  "rssi",                  "info",     None,  False),
    "orp_error":          ("u32_r", "error",                 "info",     None,  False),
    "orp_sw_vers":        ("u16_r", "sw_vers",               "info",     None,  False),
}
