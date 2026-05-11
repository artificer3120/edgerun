# edgerun walk — operator guide

> One-sheet for taking Pebble out as a walking RF probe. You walk, it scans, the viewer renders a timelapse of your route and the radio terrain you passed through.

**Walked-through:** 2026-05-10
**Written by:** christemio (recon)

---

## What you're doing

Pebble is now a **probe**. When you tap the `edgerun-walk` widget on your homescreen, it starts a background loop:

- every 30 seconds, scans wifi neighbors (BSSID, SSID, RSSI, channel)
- POSTs the scan to `neonforge.untitledprojects.io/edgerun/upload`
- a CPU wake-lock keeps it alive while screen is off
- a brief toast pops on each push so you know it's working

Tap the widget again to stop. Source-filter the viewer to `100.126.74.43` and scrub the time slider to replay your walk.

This is fundamentally different from just opening the viewer. The viewer **reads** data; the probe **writes** it. Without you walking, the map shows nothing new.

---

## One-time setup (do once, lasts forever)

You did most of this already today. Final step:

**Add the Termux:Widget to your homescreen.**

1. Long-press an empty spot on your homescreen
2. Tap "Widgets" (or whatever your Samsung launcher calls the widget picker)
3. Scroll to find **Termux:Widget**
4. Drag the 1×1 widget onto your homescreen
5. A list pops up — pick **edgerun-walk**
6. Done. The widget is now a button.

If the list is empty: ssh-driven scripts in `~/.shortcuts/` populate it. There should be one entry: `edgerun-walk`. If not, tell christemio (or any recon agent) — likely the script needs to be re-pushed.

---

## The walk

### before you leave
- Wifi or cellular: ON (probe pushes over either)
- Battery: above 30% recommended (~14%/hr drain under continuous probe load)
- Phone in pocket: fine, no screen needed

### going
1. **Tap** the `edgerun-walk` widget. Toast: `edgerun: started (every 30s)`
2. Pocket the phone. Walk.
3. Every ~30 sec, a toast flashes: `edgerun: pushed N nodes (#K)` — that's your N wifi neighbors at scan #K landing on the server.

### stopping
4. **Tap** the widget again. Toast: `edgerun: stopped`. Wake-lock released.

That's it. Two taps, bookending the walk.

---

## Watching it live

While walking (or after):

- Open `https://neonforge.untitledprojects.io/?p=edgerun-app` in any browser
- In the source-filter dropdown, pick **`100.126.74.43`** — that's your tailnet IP, isolates your walk's track
- Live mode shows current state; **time slider** at the bottom scrubs through history
- Speed selector (0.5×–4×) controls timelapse playback rate

If you walked for 20 min at 30s intervals, you'll have ~40 scan beats to scrub through. Each beat shows what your phone heard at that moment in space and time.

---

## Troubleshooting

### no toasts in 60 sec
Open Termux on Pebble, run:
```
bash ~/.shortcuts/edgerun-walk
```
This stops the loop (since marker exists from the first tap) AND should clear stuck state.
Then tap the widget again.

### "edgerun: push failed (http XXX)"
Server reachability problem. Check:
- Wifi/cellular still on?
- `curl https://neonforge.untitledprojects.io/edgerun/latest.json` from any device — should return JSON
- If reachable but probe still failing: the probe's curl is blocked at app-level. Restart Termux.

### scans show 0 nodes
Real possibilities, in order of likelihood:
- You're somewhere with no wifi APs in range (rare in NYC)
- Wifi scan throttling kicked in (Android limits to 4 scans / 2 min on some versions). Probe defaults to 30s interval, well under throttle.
- Termux:API lost background-location permission. Verify: Settings → Apps → Termux:API → Permissions → Location → "Allow all the time"

### widget not on homescreen / can't find it
Long-press home → Widgets → search "Termux". The 1×1 widget is what you want.

---

## What's stored, where

**On Pebble:**
- Probe script: `~/.shortcuts/edgerun-walk`
- Marker (running indicator): `~/.edgerun.pid`
- Local log: `~/.edgerun.log` (every push attempt: timestamp, node count, http code)
- Wake-lock state: managed by termux-wake-lock binary

**On the server:**
- Latest scan: `https://neonforge.untitledprojects.io/edgerun/latest.json`
- Historical scans: queryable from the viewer's time slider
- Source IP `100.126.74.43` (your tailnet) tags every push

**Privacy note:** the probe captures **broadcast frames** — wifi APs are publicly broadcasting their BSSIDs continuously, the same way Wigle.net catalogs them. No GPS pairing is included unless explicitly requested. Per ork3120's lineage notes, the artificer holds a no-GPS-coupling line; honor it.

---

## Quick reference card

| action | how |
|---|---|
| start walk | tap `edgerun-walk` widget |
| stop walk | tap `edgerun-walk` widget again |
| watch live | viewer URL + filter source `100.126.74.43` |
| replay walk | viewer time slider |
| check log | `ssh -p 8022 u0_a312@100.126.74.43 'tail ~/.edgerun.log'` |
| kill stuck probe | `ssh ... 'pkill -f edgerun-walk'` |

---

## What's open

- The probe currently captures **wifi only**. BLE/bluetooth scanning is a known follow-on — would add a second `medium: btle` layer.
- Step counter / accelerometer integration could mark "walking" vs "stationary" segments. Not wired.
- Monitor-mode wifi card (the $30 hardware ork3120 pitched) would unlock probe-request capture — sees devices around you, not just APs.
- Recon hub at `?p=recon` (mocks pending operator review).

— christemio
