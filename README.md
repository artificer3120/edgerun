---
project: edgerun
coordinate: 1.5
domain: 1-source
locus: .L .H
status: active
created: 2026-05-10
---

# edgerun

A physical-sensor recon tool. Probes the radio environment around a host (Wi-Fi APs, Bluetooth LE + classic, LAN ARP, USB, mDNS/SSDP services, tailnet peers) and renders the result as a live d3-force nodal graph on neonforge, with a timelapse scrubber. Mode 3 adds a phone as a walking probe.

Same idea as a CO2 sensor logging air quality, except the "air" is everyone's broadcast frames. Public-by-design — edgerun listens and plots.

## Live URLs

- Viewer (live + timelapse): https://neonforge.untitledprojects.io/?p=edgerun-app
- Spec (rendered): https://neonforge.untitledprojects.io/?p=edgerun
- Ingest endpoint: `POST https://neonforge.untitledprojects.io/edgerun/upload` (open, no auth)
- Latest snapshot: https://neonforge.untitledprojects.io/edgerun/latest.json

## Layout

```
edgerun/
├── README.md                — this file
├── docs/                     — documentation
│   ├── spec.md               — canonical spec (ork3120 handoff)
│   ├── brief.md              — 1-page operator brief
│   ├── operator-guide.md     — viewer / mode 1 + 2
│   ├── walk-guide.md         — Pebble mode 3 walking probe
│   ├── mocks/                — viewer concept mocks (recon-hub)
│   └── diagnostics/          — device baselines (e.g. Pebble physical)
├── dev/                      — development heads (mutable)
├── test/                     — testing heads (pinned to release tags; do NOT edit)
└── archive/                  — historical / superseded / runtime captures
    └── runtime/              — runtime data snapshots
```

## Release model

This repo follows a release model: edits land in `dev/`. When a `dev/` version is verified, it gets tagged via `/release edgerun@vN` and `test/` is updated to match the tag. Never edit `test/` directly. Archive holds anything that's been retired.

## Predecessors

This project consolidates work originally scattered across:
- `~/.artificer/.soundings/edgerun-mesh-map/` — primary working area before consolidation
- `~/.artificer/.sessions/10-May-26/dev/edgeRun/` — operator's session index + brief
- `~/.artificer/.sessions/10-May-26/.artificer/!coms/` — operator-facing guides
- `~/.artificer/.sessions/10-May-26/!agents/!recon/!christemio/caches/` — Pebble diag + viewer mocks
- `~/.artificer/.sessions/drafting/10-May-26-old/!handoffs/edgerun.md` — canonical spec

Recon lineage today (2026-05-10): ork3120 → brunet → christemio → planchette → goddet.

## Status snapshot at consolidation

- Mode 1 (Rocky full sensor sweep): working, pushes to neonforge live.
- Mode 2 (manual Termux→browser-upload variant): superseded by Mode 3; in `archive/`.
- Mode 3 (Pebble walking probe): working as of 2026-05-10. Pebble probe currently killed (operator-stopped after a server-side push regression — see `archive/runtime/edgerun-walk.log`).
- Open: HTTP 500 / curl-23 push regression to diagnose; recon-hub viewer pick (mocks in `docs/mocks/`); monitor-mode wifi card pitched; "the run" newsletter template lock-in.
