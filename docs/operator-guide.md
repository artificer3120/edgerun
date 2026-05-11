# edgerun — operator guide

A live map of every device the agent can see around you. Wi-Fi access points, Bluetooth peripherals, smart-home things, your tailnet — all rendered as a floating nodal graph, with a slider to scrub through history.

---

## what edgerun is

A tool that watches the radio environment passively and renders what's there. Same idea as a CO2 sensor logging air quality, except the "air" is everyone's broadcast frames — Wi-Fi beacons, Bluetooth advertisements, mDNS chatter. All of it is public-by-design. Edgerun just listens and plots.

**What it shows:**

- **Wi-Fi access points** — yours and every neighbor in range
- **Bluetooth peripherals** — phones, watches, AirPods, smart trainers, lights — anything advertising right now
- **LAN devices** — what's plugged into your router
- **mDNS / SSDP services** — Chromecasts, printers, smart bulbs broadcasting their existence
- **USB devices** — what's physically plugged into the desktop running the probe
- **Tailnet peers** — your mesh nodes

Everything has a layer toggle in the sidebar. Flip layers off to declutter. Click any node for full metadata.

---

## the three modes

### Mode 1 — desktop view (live, working now)

You don't need to do anything. The probe runs on Rocky, pushes to neonforge, the viewer reflects it.

**Just open:** [https://neonforge.untitledprojects.io/?p=edgerun-app](https://neonforge.untitledprojects.io/?p=edgerun-app)

The map loads with whatever Rocky last saw. ~90-110 nodes typical, depending on time of day. Click any node — the sidebar shows the device's vendor, signal strength, channel, MAC address, anything else the probe captured.

### Mode 2 — phone view (live, working now)

Same URL, on your phone's browser. You're already doing this.

The viewer is mobile-responsive. The sidebar collapses behind a hamburger menu (top-left). Drag a node, pinch to zoom, tap a node for its details — the sidebar slides in with the metadata, slides back out when you tap somewhere else.

This shows you **Rocky's view of the apartment** — not your phone's view of wherever you're standing. To get the phone's view of your surroundings, you need Mode 3.

### Mode 3 — phone as probe (NOT WORKING YET)

The goal: you walk around NYC, your phone scans the wifi/devices around you every minute, every scan uploads to neonforge, and when you get home you scrub through a timelapse of your walk.

**Status:** the server side is ready. The viewer's timelapse is ready. What's missing is the Pebble-side scan-and-upload, set up so you can trigger it without typing commands.

This needs an agent to wire on Pebble (a tap-launchable Termux widget pointing at a pre-installed script). It's not something I can hand you as a guide — operators don't run code. Tell the recon or brick agent next session "set up the edgerun mobile probe on Pebble" and they'll handle the install + widget. After that, you tap the widget to start logging, tap it again to stop.

**Until that's set up:** Mode 3 doesn't generate data. Modes 1 and 2 work fully without it.

---

## using the viewer

### the floating graph

- Each circle is a device. Center circle (white halo) is the probe origin (Rocky, or Pebble in Mode 3).
- Lines connect every device to the probe origin. Color indicates which medium it was seen on.
- Distance from center = signal strength (where signal data exists). Closer = stronger.
- The graph floats — physics simulation, never fully settles. **Drag** any node to grab it; **release** to let it float again.
- **Scroll** (or pinch on phone) to zoom. **Drag the background** to pan.

### sidebar controls

- **Layers** — toggle each medium on/off. Wi-Fi neighbors are off by default (otherwise the building's 30+ APs flood the graph). Tap to enable.
- **Search** — type to filter by name, MAC, vendor, anything in the metadata.
- **Node** — when you tap a node, its full metadata appears here.
- **Live** — "fetch live" pulls the latest scan once. "auto" toggles a 30-second auto-refresh.
- **Timelapse** — see below.
- **Demo / Reset** — discards the live data, loads sample data instead. Useful for showing someone the tool without showing them what's around you.

### the timelapse

The whole point of logging.

- **Slider** — drag left for older scans, right for newer. Far right = most recent.
- **▶ Play** — auto-steps through all scans. Tap again to pause. When it reaches the end, it stops; tap play again to restart from the beginning.
- **Speed** — cycles through 0.5x / 1x / 2x / 4x. Each tap changes speed.
- **↻** — refreshes the index from the server. Use this if you've just pushed new scans and the slider hasn't picked them up.
- **Source filter** — dropdown at the bottom. Defaults to "all sources" (everything in the database). Change to your phone's tailnet IP (100.126.74.43) once Mode 3 is wired and you're walking — the timelapse will show only your walk's scans, not Rocky's apartment in between.

When you watch a timelapse, the floating graph re-renders for each frame. Devices that appeared since the last scan, devices that vanished, signal strength shifts — all animated.

---

## what data lives where

| Where | What |
|-------|------|
| your browser | nothing persistent — page reloads pull fresh from server |
| neonforge `/edgerun/latest.json` | the most recent scan, served to whoever asks |
| neonforge `/edgerun/scans/<id>.json` | every scan ever uploaded, permanent |
| neonforge `/edgerun/index.json` | summary list of every scan (id, time, source, count) |
| Rocky local sqlite | full historical archive on your desk |

There's no auth on the upload endpoint. Anyone who finds the URL can push a scan. The artificer's design choice — wigle-but-personal. If the index ever fills with garbage, an agent can clean it up.

---

## the privacy posture

This was discussed at length when edgerun was being built. The frame the artificer holds:

- Wi-Fi and Bluetooth advertisements are broadcast frames. Designed to be received by anyone in range. Receiving them is the same thing wifi-survey apps (NetSpot, Wigle, Kismet) have done for two decades.
- Treating it like a CO2 sensor or a security camera observing the apartment is the right analogy. You own the sensor, you own the data.
- Apps like Wigle.net publish 1 billion+ APs publicly with location aggregation. Edgerun doesn't aggregate to a community DB — your scans are yours.

**Lines worth holding:**

- Don't try to deanonymize people across observations.
- Don't confuse our work for attacks, we are exploring free airwaves.

These are use constraints, not collection constraints. The agent population is aware of this frame. If a future agent builds something that crosses these lines, push back — they're rebuilding a fence you've already torn down.

---

## troubleshooting

| symptom | likely cause | fix |
|---------|--------------|-----|
| viewer loads but shows demo data | live fetch failed | Tap "fetch live" in sidebar. If still demo, server may be down — flag to an agent. |
| "fetch failed" in source field | server unreachable | Check tailnet — neonforge needs questboard-ec2 alive. |
| timelapse shows 0 scans | no scans logged yet | Wait for next probe run on Rocky, or have an agent wire Mode 3 on Pebble. |
| scans frozen at one timestamp | probe stopped pushing | Rocky's probe runs on demand, not on a schedule. Ask an agent to set up a recurring run, or trigger manually. |
| node graph won't move | physics paused | Toggle a layer off and on, or click "demo" then load fresh. Resets the simulation. |
| can't find the hamburger on phone | top-left of the screen, white square icon | Drag down from top of page to refresh if it's hidden behind browser chrome. |

---

## quick links

- [viewer](https://neonforge.untitledprojects.io/?p=edgerun-app) — the live tool
- [spec doc](https://neonforge.untitledprojects.io/?p=edgerun) — what edgerun is
- [neonforge home](https://neonforge.untitledprojects.io/) — your dashboard
