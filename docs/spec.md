# edgerun — recon handoff

> Audience: any recon agent picking this up. Generalized — no descendant
> assumptions. If you're recon and the artificer mentions edgerun, mesh
> mapping, sensor probes, or "the network around me," start here.

## TL;DR

edgerun is a physical-sensor recon tool. It probes everything Rocky can
see — Wi-Fi APs (own + neighbors), Bluetooth (live LE + paired classic),
LAN hosts, USB devices, mDNS/SSDP services, tailnet peers — and renders
the result as a floating d3-force nodal graph. Live ingest is wired:
probe POSTs to neonforge, viewer auto-fetches.

**Live now:**
- Viewer (live data): https://neonforge.untitledprojects.io/?p=edgerun-app
- Spec doc: https://neonforge.untitledprojects.io/?p=edgerun
- Raw scan API: https://neonforge.untitledprojects.io/edgerun/latest.json

## Where everything is

### On Rocky (working dir)
`C:\Users\ctgau\.artificer\.soundings\edgerun-mesh-map\`

| File | Purpose |
|------|---------|
| `probe-mesh.ps1` | Master probe. Runs all stages, writes mesh.json, POSTs to neonforge. Re-runnable. |
| `ble-probe.py` | Live BLE scan via bleak (WinRT under the hood). Called by probe-mesh.ps1. |
| `mdns-probe.py` | mDNS + SSDP scan via zeroconf + raw UDP. Called by probe-mesh.ps1. |
| `temporal-log.py` | sqlite log of every scan, enriches nodes with `first_seen`/`last_seen`/`is_new`. |
| `oui.csv` | IEEE vendor database (~6 MB, 39k prefixes). Loaded by probe-mesh.ps1 for vendor lookup. |
| `mesh.json` / `mesh-data.js` | Latest scan output. Viewer reads `mesh-data.js` (script tag) for offline-friendly load. |
| `mesh-viewer.html` | Local d3-force viewer. Uses baked `mesh-data.js`. |
| `edgerun-public.html` | Public viewer (deployed to neonforge as `edgerun-app.html`). Live-fetches from `/edgerun/latest.json`. |
| `edgerun-doc.html` | Spec page (deployed as `edgerun.html`). Matrix-green styling, embeds the viewer. |
| `edgerun-probe.sh` | Termux mobile probe. Downloadable from neonforge. |
| `edgerun.db` | Local sqlite — historical scan archive. |
| `patch-server-edgerun.py` | Patches `neonforge/server.py` to add `/edgerun/upload` POST + GET routes. Already applied; keep for reference. |

### On Rocky (frozen cache, deliverable snapshot)
`C:\Users\ctgau\.artificer\.sessions\09-May-26\!caches\edgerun-mesh-map\`
- Mirrored copy of the working dir at the time the build wrapped.
- `README.md` in there explains the heist.
- `edgerunMeshMap1.json` — processFlow schema of the build pipeline.
- `ork-watching-bots.png` — picass0 of the build.
- `briefing.mp3` + `.txt` — meech voice briefing.

### On neonforge (questboard-ec2: 100.83.251.119, ubuntu)
- `/home/ubuntu/neonforge/pages/edgerun.html` — spec doc page
- `/home/ubuntu/neonforge/pages/edgerun-app.html` — viewer page
- `/home/ubuntu/neonforge/media/edgerun-probe.sh` — termux script download
- `/home/ubuntu/neonforge/edgerun/` — live data store
  - `latest.json` — most recent scan
  - `scans/<id>.json` — historical scans
  - `index.json` — scan history (last 500)
- `/home/ubuntu/neonforge/server.py` — patched with `/edgerun/upload` (POST) + `/edgerun/*` (GET) routes
  - Backups at `server.py.bak.preEdgerun.<ts>`
- `/home/ubuntu/neonforge/pages/_meta.json` — has `edgerun` (docs) and `edgerun-app` (tools) entries
- `/home/ubuntu/neonforge/pages/home.html` — has both linked, count adjusted

### processFlow
`C:\Users\ctgau\forge3\processFlow\schemas\edgerunMeshMap1.json`

### Soundings manifest
`C:\Users\ctgau\.artificer\.soundings\_manifest.md` — has edgerun-mesh-map row.

## Architecture

```
ROCKY                       NEONFORGE                       VIEWER
probe-mesh.ps1
 ├─ wifi (WlanScan P/Invoke + netsh)
 ├─ ble (bleak/WinRT)
 ├─ bt-paired (Get-PnpDevice)
 ├─ lan (Get-NetNeighbor)
 ├─ usb (Get-PnpDevice)
 ├─ mdns/ssdp (python zeroconf + UDP M-SEARCH)
 ├─ tailnet (tailscale status --json)
 ├─ vendor lookup (IEEE OUI database)
 └─ temporal log (sqlite enrich)
        │
        │ POST /edgerun/upload
        ▼
                            server.py do_POST
                            → writes scans/<id>.json
                            → writes latest.json
                            → appends to index.json
                                  │
                                  │ GET /edgerun/latest.json
                                  ▼
                                                          edgerun-app.html
                                                          (auto-fetch on load
                                                           + 30s poll button)
```

## What ships in a scan

A `mesh.json` is `{generated, hub, nodes[], scan_history?, departed_recent?}`.
Each node carries: `id, label, medium, vendor?, rssi?, first_seen?, last_seen?, scan_count?, is_new?` — plus medium-specific fields (`bssid` for wifi, `addr` for BT, `ip`/`mac` for LAN, etc.).

Mediums currently emitted: `wifi-own`, `wifi-neighbor`, `btle`, `btclassic`, `lan`, `usb`, `mdns`, `tailnet`. Viewer has a layer toggle per medium.

## Operator's posture (read this)

The artificer has explicit views on this work that I learned the hard way:

- **Data is data.** Wi-Fi beacons and BLE advertisements are broadcast frames, designed to be received by anyone in range. The artificer treats this like a CO2 sensor or a security camera observing his own apartment — passive observation of a public physical channel. Wigle.net publishes 1B+ APs publicly and is fine. Don't reflexively gate the data.
- **Public ingest is the design, not a bug.** The `/edgerun/upload` endpoint is open. Any device can push. The artificer wants this — wigle-but-personal. If you find yourself building auth or rate-limit-by-IP gates, stop and ask first.
- **He'll push back if you over-fence.** I rebuilt the same fence three times before he called it out. If you catch yourself adding "but only for tailnet" or "but only signed payloads" — stop. The artificer's frame is "data is data, like a camera."
- **Ethics line that DOES hold:** don't aggregate to track individuals across observations, don't pair MACs to people, don't probe/attack discovered networks. Listen, never poke. But that's a *use* constraint, not a *collection* constraint.

## Open items (priority order)

1. **Push the upgraded probe + viewer to a publicly-discoverable place.** Right now `probe-mesh.ps1` lives only on Rocky. The Termux mobile probe is downloadable, but the desktop probe isn't yet. Could go to GitHub or to a `/media/` URL on neonforge.
2. **Monitor-mode wifi card.** ~$30 USB Alfa AWUS036ACH. Operator pre-authorized for <$10/30-day so this needs explicit approval. Unlocks **probe requests** — see who's looking for which SSID, when. Flatland-tier signal. Ticket worthy.
3. **Newsletter "the run" — template lock-in.** A separate work item; 4 versions of template A drafted (white+red, burnt orange, dark+full picass0 palette, cream-headlines+profile-block+after-a-run-photo). Operator hasn't locked one yet. The newsletter is meant to be NYC ridealong reports paired with edgerun field notes.
4. **Source-filter UI.** Now that ingest is open, the viewer should support filtering by `source_ip` or by individual `scan_id` from `index.json`. Currently it just shows `latest.json`.
5. **Live BLE on Android.** Termux probe currently does wifi only. Real BLE on Android needs a tiny APK — operator's call whether to spend the time.

## How to run a scan right now

```powershell
& "C:\Users\ctgau\.artificer\.soundings\edgerun-mesh-map\probe-mesh.ps1"
```

That:
1. Loads OUI database
2. Triggers WlanScan + reads results (~12s)
3. Live BLE scan via bleak (~8s)
4. Reads PnP/Neighbor/USB tables (instant)
5. Runs mDNS/SSDP scan (~6s)
6. Reads tailscale status (instant)
7. Writes mesh.json + mesh-data.js
8. Logs to sqlite, enriches with temporal fields
9. POSTs to neonforge live ingest

Whole thing takes ~30-40s. After it returns, the public viewer reflects the new scan within seconds.

## Known sharp edges

- **PowerShell 5.1 cannot subscribe to WinRT events.** That's why BLE shells out to python+bleak. If you ever feel the urge to "do it natively in PS," stop — that path is a dead end.
- **`netsh wlan show networks` doesn't trigger a scan** — it reads cache. The probe uses P/Invoke `WlanScan` to force a fresh scan, then reads the cache.
- **mDNS responses can be noisy** — the OpenWRT router advertised ~14 SSDP services, all the same device. The probe dedupes SSDP by IP. If you see one IP showing up as 14 nodes, the dedupe broke.
- **server.py had a stray cp1252 em-dash** on line 421 that broke parse on first systemctl restart this session. Fixed in place. If you `systemctl restart neonforge` and it 502s, check syntax.
- **Modern phones randomize BLE MACs every ~15 min** — most of your "btle" nodes will turn over scan-to-scan. That's privacy by design, not a bug. The temporal log will show the rotation.

## Things to know about the operator

(General recon-relevant context, not edgerun-specific)
- Address as **artificer** (or boss). Lowercase by default.
- He's pre-authorized for under $10 / 30-day decisions.
- Always push after commit (when auth allows).
- He prefers `/savepoint` for continuity; reserve `/dumpshock` for actual pre-restart teardown.
- Don't argue when he says there's a better way. Stop, ask, reconsider.
- "Look at my screen" means take a screenshot.
- Native stack first (PowerShell, AHK, Python+pywin32, Win32) before reaching for Electron/Flask.

## Nodes on the mesh

| Node | IP | Role |
|------|-----|------|
| Rocky | 100.101.108.7 | Operator's home desktop, Windows 11. Where the probe lives. |
| questboard-ec2 | 100.83.251.119 | Ubuntu, always-on. Runs neonforge (port 8080), questboard, brick-email. SSH key: `~/forge3/questboard-key.pem`. |
| picass0 | 100.127.18.29 | Ubuntu, GPU (g4dn.xlarge), on-demand. Auto-stops after 10 min idle. |
| Pebble | 100.126.74.43 | Operator's Android phone. Termux probe target. |
| Aqua | (mesh) | ONN 8" Android tablet. PIN 3120. Could also run the termux probe. |

## Last build state at handoff

- Most recent live scan: 93 nodes (39 wifi + 34 BLE + 5 mDNS + 5 LAN + 6 tailnet + 2 USB + 2 BT-paired)
- Live pipe: ✓
- Public viewer: ✓ (auto-fetches latest)
- Public spec doc: ✓ (linked from neonforge home, "tools" + "docs" sections)
- Termux probe: ✓ downloadable, untested on actual Pebble (operator hasn't installed it yet)
- Newsletter "the run": 4 template variants drafted, none locked
- Free wins: all 4 shipped (OUI lookup · mDNS/SSDP · live BLE · temporal log)

## If you need credentials

Use the vault. `google_artificer3120_*` for gmail. The boot config token in `_tunnelTime/launch/config/gmail-oauth.md` was expired during this session — vault had a fresh one. If gmail throws `invalid_grant`, hit the vault first before flagging it.

```python
import os, requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def vault(name):
    return requests.post('http://100.83.251.119:8120/credential',
        json={'name': name},
        headers={'X-Vault-Key': os.environ.get('VAULT_KEY','')}, timeout=5).json()['value']

creds = Credentials(
    token=None,
    refresh_token=vault('google_artificer3120_refresh_token'),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=vault('google_artificer3120_client_id'),
    client_secret=vault('google_artificer3120_client_secret'),
)
gmail = build('gmail', 'v1', credentials=creds)
```

## Quick verify it's alive

```bash
curl -sS https://neonforge.untitledprojects.io/edgerun/latest.json | python -c "import sys,json;d=json.load(sys.stdin);print(f'{len(d[\"nodes\"])} nodes, source: {d.get(\"source_ip\")}, received: {d.get(\"received\")}')"
```

If that returns recent data, the pipe is alive. If it returns stale data, run the probe on Rocky to refresh. If it 404s or 500s, check `sudo systemctl status neonforge` on questboard-ec2.

— end handoff
