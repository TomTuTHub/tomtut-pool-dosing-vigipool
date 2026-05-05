# Deploy auf tomtut.local (Dev-HA, 192.168.16.124)

> Dokumentiert den Weg aus einem LXC-Container (ohne vorinstallierten SSH-Key)
> auf den Dev-HA zu deployen. Erprobt 2026-04-14.

## Ausgangslage

- Dev-HA: `tomtut.local` / `192.168.16.124`, VM auf DS718+
- SSH Port **2242** (Terminal & SSH Add-on, Slug `core_ssh`)
- **Nur Publickey-Auth**, User `root`
- Fremd-LXCs haben **keinen** lokalen SSH-Key fuer tomtut.local
- `rsync` ist im LXC nicht installiert, `apt` geht nicht (kein root)
- NAS-Mount `/mnt/nas` zeigt auf DS923+, **nicht** auf DS718+ — Files-Upload via NAS-Share ist nicht moeglich
- HA Dev API Token (user token) kommt **nicht** an `/api/hassio/*` REST-Endpoints (401) — aber die **HA WebSocket API** akzeptiert `supervisor/api` Befehle von Admin-Usern

## Strategie: WebSocket + Supervisor API + ephemerer Deploy-Key

1. HA Dev API Token aus 1Password holen
2. Ephemeres SSH-Keypair lokal generieren (`/tmp/orpheo_deploy`)
3. Via HA WebSocket Supervisor-API den Public-Key in die `core_ssh` Add-on Options (`authorized_keys`) injecten
4. SSH Add-on restart → Key ist live
5. `tar` + `scp` die Integration, entpacken nach `/config/custom_components/<domain>/`
6. `ha core restart`
7. Deploy-Key wieder aus `authorized_keys` entfernen, Add-on restart, lokale Key-Dateien loeschen

## Einzelne Schritte (copy-pasteable)

### 1. 1Password Login + Token holen

```bash
export OP_SESSION_G7HBTRSAPJHKDMH3NEMRXEKJDA=$(echo 'PASSWORT' | op signin --account my --raw)
export HA_TOKEN=$(op item get "HA Dev: API Token — tomtut.local" --vault Claude --fields "API Token" --reveal)
```

### 2. Ephemeren Deploy-Key erzeugen

```bash
ssh-keygen -t ed25519 -f /tmp/orpheo_deploy -N "" -C "orpheo_deploy_$(date +%s)" -q
DEPLOY_KEY="$(cat /tmp/orpheo_deploy.pub)"
```

### 3. Key in SSH Add-on injecten + Add-on restart

```python
# python3 script (braucht `websockets` package: pip install --break-system-packages websockets)
import asyncio, json, os, websockets

TOKEN = os.environ["HA_TOKEN"]
DEPLOY_KEY = os.environ["DEPLOY_KEY"].strip()

async def main():
    async with websockets.connect("ws://192.168.16.124:8123/api/websocket") as ws:
        await ws.recv()  # auth_required
        await ws.send(json.dumps({"type":"auth","access_token":TOKEN}))
        await ws.recv()  # auth_ok

        # aktuelle Addon-Options lesen
        await ws.send(json.dumps({
            "id": 1, "type": "supervisor/api",
            "endpoint": "/addons/core_ssh/info", "method": "get"
        }))
        cur = json.loads(await ws.recv())["result"]["options"]
        keys = list(cur.get("authorized_keys") or [])
        if DEPLOY_KEY not in keys:
            keys.append(DEPLOY_KEY)
        new_opts = {
            "authorized_keys": keys,
            "password": cur.get("password",""),
            "apks": cur.get("apks", []),
            "server": cur.get("server", {"tcp_forwarding": False}),
        }

        # Options schreiben
        await ws.send(json.dumps({
            "id": 2, "type": "supervisor/api",
            "endpoint": "/addons/core_ssh/options", "method": "post",
            "data": {"options": new_opts}
        }))
        print("set_options:", await ws.recv())

        # Addon restart (damit Options greifen)
        await ws.send(json.dumps({
            "id": 3, "type": "supervisor/api",
            "endpoint": "/addons/core_ssh/restart", "method": "post",
            "timeout": 90
        }))
        print("restart:", await ws.recv())

asyncio.run(main())
```

### 4. Deploy via tar + scp (rsync fehlt im LXC)

```bash
cd /mnt/nas/Git-Repos/tomtut-Dosieranlage-Orpheo-VP/custom_components/orpheo_vp
tar czf /tmp/orpheo_vp.tgz .

SSH_OPTS="-i /tmp/orpheo_deploy -p 2242 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/tmp/orpheo_known_hosts"
scp $SSH_OPTS /tmp/orpheo_vp.tgz root@192.168.16.124:/tmp/ # Achtung: scp nutzt -P 2242 (gross)
# Korrekt fuer scp:
scp -i /tmp/orpheo_deploy -P 2242 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/tmp/orpheo_known_hosts /tmp/orpheo_vp.tgz root@192.168.16.124:/tmp/

ssh -i /tmp/orpheo_deploy -p 2242 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/tmp/orpheo_known_hosts root@192.168.16.124 "
  set -e
  rm -rf /config/custom_components/orpheo_vp
  mkdir -p /config/custom_components/orpheo_vp
  tar xzf /tmp/orpheo_vp.tgz -C /config/custom_components/orpheo_vp
  rm /tmp/orpheo_vp.tgz
  ha core restart
"
```

### 5. Cleanup — Deploy-Key entfernen, lokale Dateien loeschen

```python
# Gleicher Python-Block wie Schritt 3, aber keys filtern:
#   keys = [k for k in (cur.get("authorized_keys") or []) if k.strip() != DEPLOY_KEY]
# Danach addon/options POST + addon restart.
```

```bash
rm -f /tmp/orpheo_deploy /tmp/orpheo_deploy.pub /tmp/orpheo_known_hosts /tmp/orpheo_vp.tgz
```

## Post-Deploy Checks

```bash
# HA Core wieder oben?
curl -s -o /dev/null -w '%{http_code}\n' http://192.168.16.124:8123/

# Config-Entry Status
curl -s -H "Authorization: Bearer $HA_TOKEN" http://192.168.16.124:8123/api/config/config_entries/entry \
  | python3 -c "import json,sys; [print(e['domain'], e['state'], e['title']) for e in json.load(sys.stdin) if e['domain']=='orpheo_vp']"

# Alle Orpheo-Entities + States
curl -s -H "Authorization: Bearer $HA_TOKEN" http://192.168.16.124:8123/api/states \
  | python3 -c "import json,sys; [print(f\"{s['entity_id']:60s} = {s['state']}\") for s in sorted(json.load(sys.stdin), key=lambda x:x['entity_id']) if 'orpheo' in s['entity_id']]"

# Fehler im HA Log
ssh $SSH_OPTS root@192.168.16.124 "ha core logs 2>/dev/null | grep -i orpheo | tail -40"
```

## Gotchas

- **`entity_registry_enabled_default=False` → True umstellen reicht nicht.** Bestehende Registry-Eintraege behalten ihren `disabled_by`. Nach Deploy via WebSocket `config/entity_registry/update` (Feld `disabled_by: null`) pro Entity-ID patchen, dann Config-Entry reloaden.
- **`ha` CLI braucht keinen `thomas`-User** — der User im 1P-Eintrag ist **`root`**, obwohl das Projekt-CLAUDE.md noch `thomas@` dokumentiert. CLAUDE.md ist bzgl. User **falsch**, 1P ist autoritativ.
- **`apks`, `server`, `password`** muessen beim POST auf `/addons/core_ssh/options` mitgeschickt werden — sonst wirft HA die Werte weg (Options werden vollstaendig ueberschrieben, nicht gemerged).
- **Entity-Reload nach Registry-Patch** via `POST /api/config/config_entries/entry/<entry_id>/reload` — spart einen Core-Restart.

## Referenzen

- 1Password Item: `HA Dev: SSH Login — tomtut.local (192.168.16.124)` (Vault "Claude")
- 1Password Item: `HA Dev: API Token — tomtut.local` (Feld "API Token")
- Shared-Base Workflow: `/mnt/nas/_shared-base/1password-workflow.md`
