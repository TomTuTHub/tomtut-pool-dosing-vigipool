# TomTuT Orpheo VP

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
- Companion **custom Lovelace card** (`tomtut-orpheo-vp-card`) included in `lovelace/`

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
3. Add repository URL: `https://github.com/TomTuTHub/tomtut-orpheo-vp`
4. Category: **Integration**
5. Install → **Restart Home Assistant**

### Manual

1. Copy `custom_components/orpheo_vp` to:
   - `<config>/custom_components/orpheo_vp`
2. Restart Home Assistant

---

## Configuration

1. Settings → **Devices & Services**
2. **Add Integration**
3. Search for **TomTuT Orpheo VP**
4. Enter:
   - **IP address** of the device (the device itself is the MQTT broker)
   - **Phileo VP Device-ID** (12 hex chars — the WiFi MAC without separators, e.g. `08D1F9976534`)
   - **Oxeo VP Device-ID** (12 hex chars)
   - Optionally: Vigipool cloud credentials for fallback

### Finding the Device-IDs

The Device-IDs are the WiFi MAC addresses of the two internal modules (Phileo + Oxeo), each without colons. You can find them by:

- Listening on MQTT topic `#` for the IP and noting the `phileox_<MAC>` / `oxeox_<MAC>` topic prefixes, **or**
- Reading them from the Vigipool / Poolsana app device info

---

## Companion Lovelace Card

A custom card matching this integration is shipped under `lovelace/orpheo-vp-card.js`. After deploying it to `<config>/www/orpheo_vp/orpheo-vp-card.js` and registering it as a Lovelace resource, you can use:

```yaml
type: custom:orpheo-vp-card
device_name: Orpheo VP Pool Dosieranlage
```

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

## Transparency

I'm a trained IT systems specialist with many years of experience. I use **Claude** and **ChatGPT** as development assistants when building these integrations. The code runs in my own production Home Assistant environment.
