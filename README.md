# TomTuT Pool Dosing Vigipool

Community Home Assistant integration for **Vigipool Orpheo VP** pool dosing systems (Phileo VP + Oxeo VP) via **local MQTT** (LAN). Local-only — no cloud account, no external server.

- 🌐 **Übersicht zu Vigipool (alle Beiträge, deutsch):** https://www.tomtut.de/vigipool
- 📖 **Diese Integration — Schritt-für-Schritt-Anleitung mit Video (deutsch):** https://www.tomtut.de/tomtut-pool-dosieranlage-homeassistant-vigipool-integration/

---

## Disclaimer

This integration is an independent community project and is **not** commissioned, endorsed, affiliated with, or supported by **Vigipool / CCEI / Poolsana**.
Use at your own risk.

---

## Features

- **Local push via MQTT** — the device is its own broker on port 1883 (no external broker required, no auth needed)
- **Fully local** — no cloud login required; no traffic to `supervision.vigipool.com`. You can block the device from the internet entirely.
- **Self-healing connection** — if the device goes offline (network outage, reboot, blocked at firewall), entities go `unavailable` within ~30 s; once the device returns, the integration reconnects automatically — no manual re-add.
- Sensors for **pH**, **Redox/ORP**, **flow**, **dosing pumps**, **daily/total injected volume**, **WiFi signal**, **firmware**, **errors**, plus live status of the device's manufacturer-cloud uplink (`mqtt_connected`)
- Read/write entities for **setpoints** (pH, ORP), **container size**, **daily max dose**, **spa-mode**, **winter-mode**
- **Restmenge tracking** (canister fill level) — auto-decrements based on injected volume, persists across restarts
- **Readable error codes** (v2.4.6) — the raw error bitmask is additionally exposed as a human-readable German text sensor (`sensor.*_fehler`), plus a **"Tageslimit erreicht" binary sensor** per channel (daily max dose reached) for automations. Container-size / max-dose config values are **debounced** against device value bursts.
- Companion **custom Lovelace card** available as a separate repository: [`tomtut-pool-dosing-vigipool-card`](https://github.com/TomTuTHub/tomtut-pool-dosing-vigipool-card) — with prominent offline banner when the device drops off

---

## Compatibility

| Device | Notes |
|---|---|
| Vigipool Orpheo VP | Confirmed (Phileo VP + Oxeo VP combo) |
| CCEI Phileo VP / Oxeo VP | Same firmware family — should work |
| Poolsana branded variant | Same hardware |

The device must be on a network reachable from Home Assistant (typically your IoT VLAN). MQTT broker port 1883 is hosted directly on the device.

---

## Installation

### HACS (Custom repository)

1. HACS → **Integrations**
2. Menu (⋮) → **Custom repositories**
3. Add repository URL: `https://github.com/TomTuTHub/tomtut-pool-dosing-vigipool`
4. Category: **Integration**
5. Install → **Restart Home Assistant**

### Manual

1. Copy `custom_components/tomtut_pool_dosing_vigipool` to:
   - `<config>/custom_components/tomtut_pool_dosing_vigipool`
2. Restart Home Assistant

---

## Configuration

1. Settings → **Devices & Services**
2. **Add Integration**
3. Search for **TomTuT Pool Dosing Vigipool**
4. Enter:
   - **IP address** of the device (the device itself is the MQTT broker)
   - **Phileo VP Device-ID** (12 hex chars — the WiFi MAC without separators, e.g. `08D1F9976534`)
   - **Oxeo VP Device-ID** (12 hex chars)

   No cloud credentials required — this integration is local-only.

### Finding the Device-IDs

The Device-IDs are the WiFi MAC addresses of the two internal modules (Phileo + Oxeo), each written **without colons** (12 hex characters). Both modules are based on Espressif (ESP32) chips with these OUI prefixes:

| Module | OUI prefix | Example full ID | On WiFi? |
|---|---|---|---|
| Phileo VP (pH) | `08:D1:F9` → `08D1F9...` | `08D1F9976534` | yes — has its own LAN IP |
| Oxeo VP (Redox) | `B0:B2:1C` → `B0B21C...` | `B0B21C023368` | **no** — paired to the Phileo over short-range RF (BLE / Sub-GHz) |

> **Important:** only the **Phileo VP** is on your WiFi. The Oxeo VP is paired to the Phileo over a short-range radio link (typical RSSI around -8 dBm, i.e. right next to it), and its readings/topics are relayed through the Phileo's MQTT broker. So you will see the Phileo on your router — but **not** the Oxeo.

The most reliable way to grab both IDs at once is to listen to the MQTT broker that the Phileo VP runs (port 1883, no auth):

1. **MQTT sniffing (recommended — finds both at once).**
   Subscribe to topic `#` on the Phileo's IP and watch for the topic prefixes:
   - `phileox_<MAC12>/...` → that's your **Phileo VP Device-ID**
   - `oxeox_<MAC12>/...` → that's your **Oxeo VP Device-ID**

   Quick one-liner from any Linux/Mac box:
   ```bash
   mosquitto_sub -h <PHILEO_IP> -t '#' -v | head
   ```

2. **Vigipool / Poolsana app.**
   Open the device detail screen in the app — the hardware identifier (often labelled "ID", "Serial", "MAC" or shown beneath the firmware version) is the same MAC as above. Phileo and Oxeo show up as separate devices in the app, each with its own ID.

3. **Sticker on the device.**
   Open the housing — the WiFi MAC is usually printed on a sticker on the inside cover or directly on the ESP module of each board.

4. **Router / DHCP lease list — Phileo only.**
   Your router will show the Phileo VP (OUI `08:D1:F9`) but **not** the Oxeo VP. Useful to confirm the Phileo's IP and MAC quickly, but you still need one of the methods above to get the Oxeo.

Since version 2.2.1 the integration accepts the IDs in any common formatting:

```
08D1F9976534          08:D1:F9:97:65:34          08-D1-F9-97-65-34
08 D1 F9 97 65 34     08.D1.F9.97.65.34          (case-insensitive)
```

Separators (`:`, `-`, `.`, spaces) are stripped automatically.

---

## Woher kommen die Fehlercode-Texte?

Die Anlage meldet Fehler als **u32-Bitmaske** auf dem MQTT-Topic `.../error/info/reported`.
Seit v2.4.6 gibt es je Kanal zusaetzlich einen **lesbaren Fehler-Sensor** (`sensor.*_fehler`) und
einen **binary_sensor "Tageslimit erreicht"**. Der rohe Fehlercode-Sensor bleibt erhalten; der
lesbare Sensor zeigt Rohwert und gesetzte Bits zusaetzlich als Attribute — es geht also **keine
Information verloren**.

**Konservatives Mapping:** Nur Bits mit belegter Bedeutung bekommen einen Klartext; alle anderen
werden weiterhin als `Bit N` angezeigt.

- **Bit 31 (0x80000000) = „Tagesmaximaldosis erreicht“** — die einzige empirisch bestaetigte
  Zuordnung: am **2026-07-14** an einer realen Anlage beobachtet (pH-Fehlercode `2147483648` exakt
  zeitgleich mit App-Push **E24** „Maximalvolumen injiziert“ + Pumpe ausser Betrieb). Der
  deutsche Text folgt dem CCEI-Uebersetzungs-Key `V_MAX_INJECTED`.
- **Bit 24 (ORP)** bleibt bewusst **„Bit 24“ (unbekannt):** trat nur in den ersten drei
  Tagen nach Inbetriebnahme (12.–14.05.2026) auf, meist zusammen mit Bit 31, bei
  unauffaelligen ORP-Messwerten (584–624 mV) — also **kein** Messfehler; vermutlich ein
  Inbetriebnahme-/Kalibrier-Flag (unbewiesen). Quelle: HA-Export ka-147, Analyse 2026-07-14.

**Quelle der Texte:** offizielles CCEI-Jeedom-Plugin
[`developer-ccei-pool/jeedom-vigipool`](https://github.com/developer-ccei-pool/jeedom-vigipool),
Datei `core/template/js/language_german.js`, Commit `51d6d5c9` (2024-08-09), abgerufen 2026-07-14.

> **Wichtig:** Das CCEI-Plugin dekodiert die Fehler-Bitmaske **nicht** selbst — die App-Fehlercodes
> (E24/E27/E29/E9 …) werden von der Hersteller-Cloud als fertige Meldung gepusht. Es existiert also
> keine offizielle Bit→Text-Tabelle. Deshalb ist bewusst **nur Bit 31** zugeordnet; weitere
> Bedeutungen werden erst nach eigener empirischer Bestaetigung ergaenzt (der Kommentar in `const.py`
> fuehrt die uebrigen CCEI-Texte — pH-/ORP-Messfehler, RS485, Temperatur — als dokumentierte
> Referenz, aber ohne Bit-Bindung). Aendert CCEI Bedeutungen per Firmware, bleibt die Herkunft so
> nachvollziehbar.

---

## Companion Lovelace Card

A custom Lovelace card that visualises this integration lives in its own repository:

➡️ https://github.com/TomTuTHub/tomtut-pool-dosing-vigipool-card

Features: live pump animations, animated water waves (gated by flow sensor), pH/Redox value badges, settings overlay (setpoints / container / refill / modes), dual plug toggles, cloud / firmware status badges.

---

## Support / Issues

Please open a **GitHub Issue** in this repository and include:

- Home Assistant version
- Integration version
- Device model (Vigipool Orpheo VP / CCEI / Poolsana)
- Relevant logs (**Settings → System → Logs**)
- Steps to reproduce (what you did, what you expected, what happened)
- Did you watch the Blogarticle / YouTube video at https://www.tomtut.de/tomtut-pool-dosieranlage-homeassistant-vigipool-integration/ ?

---

## Contributing

Contributions are welcome!

1. Fork the repo
2. Create a feature branch
3. Commit with a clear message
4. Open a Pull Request

---

## License

MIT

---

## Über den Autor

Ich bin ausgebildeter Fachinformatiker für Systemintegration mit langjähriger IT-Erfahrung. Früher war es der MCSE — heute ist es Vibe Coding. Diese Integration wurde mit Hilfe von Claude gebaut. Ohne KI-Unterstützung hätte ich das nebenbei nie in dieser Form hinbekommen. Der Code wurde von mir getestet und läuft in meinem eigenen Produktiv-Setup.

Mehr auf [tomtut.de](https://tomtut.de) und [YouTube @TomTuT](https://www.youtube.com/@TomTuT).

---

Das war TomTuT, bleib hart am Gas.
