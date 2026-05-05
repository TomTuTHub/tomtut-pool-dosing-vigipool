# TomTuT Pool Dosing Vigipool

Community Home Assistant integration for **Vigipool Orpheo VP** pool dosing systems (Phileo VP + Oxeo VP) via **local MQTT** (LAN), with optional cloud fallback.

➡️ **More info & guides (German):** https://www.tomtut.de/

---

## Disclaimer

This integration is an independent community project and is **not** commissioned, endorsed, affiliated with, or supported by **Vigipool / CCEI / Poolsana**.
Use at your own risk.

---

## Features

- **Local push via MQTT** — the device is its own broker on port 1883 (no external broker required, no auth needed)
- **Cloud fallback** — falls back to `supervision.vigipool.com` when local MQTT is stale
- Sensors for **pH**, **Redox/ORP**, **flow**, **dosing pumps**, **daily/total injected volume**, **WiFi signal**, **firmware**, **errors**
- Read/write entities for **setpoints** (pH, ORP), **container size**, **daily max dose**, **spa-mode**, **winter-mode**
- **Restmenge tracking** (canister fill level) — auto-decrements based on injected volume, persists across restarts
- Companion **custom Lovelace card** available as a separate repository: [`tomtut-pool-dosing-vigipool-card`](https://github.com/TomTuTHub/tomtut-pool-dosing-vigipool-card)

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
   - Optionally: Vigipool cloud credentials for fallback

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
- Did you watch the Blogarticle / YouTube video at https://tomtut.de/ ?

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

## Ueber den Autor

Ich bin ausgebildeter Fachinformatiker fuer Systemintegration mit langjaehriger IT-Erfahrung. Frueher war es der MCSE — heute ist es Vibe Coding. Diese Integration wurde mit Hilfe von Claude gebaut. Ohne KI-Unterstuetzung haette ich das nebenbei nie in dieser Form hinbekommen. Der Code wurde von mir getestet und laeuft in meinem eigenen Produktiv-Setup.

Mehr auf [thomasbase.de](https://thomasbase.de) und [YouTube @TomTuT](https://www.youtube.com/@TomTuT).

---

Das war TomTuT, bleib hart am Gas.
