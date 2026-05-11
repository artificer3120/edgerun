---
project: edgeRun
brief_by: goddet (recon)
date: 2026-05-10
length: 1 page
---

# edgeRun — recon brief

edgeRun is a physical-sensor recon tool. Rocky probes Wi-Fi APs, Bluetooth (LE + classic), LAN, USB, mDNS/SSDP, and tailnet peers; renders the result as a live d3-force mesh on neonforge with a timelapse scrubber. Mode 3 adds Pebble as a walking probe — tap a Termux widget, the phone scans Wi-Fi every 30 seconds and pushes to the public ingest endpoint.

**Status: live.** Pebble has been pushing scans every ~10s since ~18:05 EDT today. The pipeline — Rocky probe → /edgerun/upload → /edgerun/latest.json → public viewer — is end-to-end. Patched live server at neonforge.untitledprojects.io.

**Open threads.** Recon-hub viewer mocks (3 concepts staged, no pick yet). Two probe instances running on Pebble — cosmetic double-tap. Pebble /data at 98% with unbounded log writes. "The run" newsletter template (4 variants drafted, none locked). Monitor-mode Wi-Fi card ($30) pitched but unapproved. Pebble probe source lives only on-device — not pulled back to soundings.

**Posture.** Ingest is open by design — "data is data." Don't fence it. Vault-first for tokens. The local neonforge clone is unpatched; the live server diverges via patch-server-edgerun.py.

**Codebase.** `.artificer\.soundings\edgerun-mesh-map\`. Full link index at `dev\edgeRun\INDEX.md`.
