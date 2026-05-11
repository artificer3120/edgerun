#!/data/data/com.termux/files/usr/bin/bash
# edgerun mobile probe — Termux + termux-api
# Author: ork3120 (recon), 2026-05-10
#
# Output: ~/storage/downloads/edgerun-mesh.json
# Then: open https://neonforge.untitledprojects.io/edgerun and tap "load mesh.json"
#
# Setup (one-time):
#   1. Install Termux + Termux:API from F-Droid (NOT the Play Store version)
#   2. pkg install termux-api python
#   3. termux-setup-storage   (grants Downloads access)

set -u
OUT="$HOME/storage/downloads/edgerun-mesh.json"
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

mkdir -p "$(dirname "$OUT")" 2>/dev/null

if ! command -v termux-wifi-scaninfo >/dev/null 2>&1; then
  echo "termux-api not installed. run: pkg install termux-api"
  echo "you also need the Termux:API app from F-Droid"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
  echo "python not installed. run: pkg install python"
  exit 1
fi
PY=$(command -v python3 || command -v python)

echo "[wifi] scanning..."
WIFI_SCAN=$(termux-wifi-scaninfo 2>/dev/null || echo "[]")
WIFI_CONN=$(termux-wifi-connectioninfo 2>/dev/null || echo "{}")

# write JSON via python so we don't have to bash-escape the scan payload
SCAN_FILE=$(mktemp)
CONN_FILE=$(mktemp)
printf '%s' "$WIFI_SCAN" > "$SCAN_FILE"
printf '%s' "$WIFI_CONN" > "$CONN_FILE"

"$PY" - "$SCAN_FILE" "$CONN_FILE" "$NOW" "$OUT" <<'PYEOF'
import json, sys, os
scan_path, conn_path, now, out_path = sys.argv[1:5]

def safe_load(p, fallback):
    try:
        with open(p, 'r') as f:
            return json.load(f)
    except Exception:
        return fallback

scan = safe_load(scan_path, [])
conn = safe_load(conn_path, {})

own_bssid = (conn.get("bssid") or "").lower().strip('"').strip()

nodes = []
for ap in scan if isinstance(scan, list) else []:
    bssid = (ap.get("bssid") or "").lower()
    if not bssid:
        continue
    rssi = ap.get("rssi")
    nodes.append({
        "id": "wifi-" + bssid,
        "label": ap.get("ssid") or "<hidden>",
        "medium": "wifi-own" if bssid == own_bssid else "wifi-neighbor",
        "bssid": bssid,
        "rssi": rssi,
        "frequency": ap.get("frequency"),
        "channel_bandwidth_mhz": ap.get("channel_bandwidth_mhz"),
        "capabilities": ap.get("capabilities"),
    })

mesh = {
    "generated": now,
    "hub": {
        "id": "phone",
        "label": conn.get("ssid", "phone").strip('"') or "phone",
        "note": "Termux mobile probe · " + now,
    },
    "nodes": nodes,
}

with open(out_path, 'w') as f:
    json.dump(mesh, f, indent=2)

print(f"[wifi] {len(nodes)} APs")
print(f"[done] wrote {out_path}")
PYEOF

rm -f "$SCAN_FILE" "$CONN_FILE"

echo ""
echo "next: open https://neonforge.untitledprojects.io/edgerun"
echo "      tap 'load mesh.json' and pick edgerun-mesh.json from Downloads"
