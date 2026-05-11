#!/data/data/com.termux/files/usr/bin/bash
# edgerun-walk : tap to start a walk-probe, tap again to stop
# Pushes wifi scans to neonforge every INTERVAL seconds.
# Wake-lock keeps the CPU alive while screen is off.

set +e

ENDPOINT="https://neonforge.untitledprojects.io/edgerun/upload"
HUB="pebble-walk"
INTERVAL=30
MARKER="$HOME/.edgerun.pid"
LOG="$HOME/.edgerun.log"

# --- TOGGLE: stop if already running ---
if [ -f "$MARKER" ]; then
    PID=$(cat "$MARKER" 2>/dev/null)
    if [ -n "$PID" ]; then
        kill "$PID" 2>/dev/null
    fi
    rm -f "$MARKER"
    termux-wake-unlock 2>/dev/null
    termux-toast "edgerun: stopped"
    echo "$(date -u +%FT%TZ) stopped pid=$PID" >> "$LOG"
    exit 0
fi

# --- START ---
termux-wake-lock 2>/dev/null

# Fork loop in background
(
    SCAN_NUM=0
    while true; do
        SCAN_NUM=$((SCAN_NUM + 1))
        TS=$(date -u +%FT%TZ)
        SCAN_ID="walk-$(date +%s)-$SCAN_NUM"

        # Acquire wifi scan
        SCAN=$(termux-wifi-scaninfo 2>/dev/null)
        if [ -z "$SCAN" ] || [ "$SCAN" = "null" ]; then
            SCAN="[]"
        fi

        # Transform termux-wifi-scaninfo output -> edgerun node spec
        NODES=$(echo "$SCAN" | jq -c --arg ts "$TS" '
          if type == "array" then
            [ .[] | {
                id: ("wifi-" + (.bssid // "unknown")),
                bssid: (.bssid // ""),
                rssi: (.rssi // 0),
                label: ((.ssid // "<hidden>") | if . == "" then "<hidden>" else . end),
                signal: (.rssi // 0),
                radio: "802.11",
                channel: (
                    if .frequency_mhz < 2500 then (((.frequency_mhz - 2407) / 5) | floor)
                    elif .frequency_mhz < 5950 then (((.frequency_mhz - 5000) / 5) | floor)
                    else ((((.frequency_mhz - 5945) / 5) | floor) + 1)
                    end
                ),
                medium: "wifi-neighbor",
                vendor: null,
                first_seen: $ts,
                last_seen: $ts,
                scan_count: 1,
                is_new: true
              } ]
          else [] end
        ')

        N=$(echo "$NODES" | jq length)

        # Build top-level payload
        PAYLOAD=$(jq -nc \
            --arg hub "$HUB" \
            --arg ts "$TS" \
            --arg sid "$SCAN_ID" \
            --argjson nodes "$NODES" \
            '{
                hub: $hub,
                layers_present: ["wifi-neighbor"],
                generated: $ts,
                scan_id: $sid,
                nodes: $nodes,
                departed_recent: [],
                scan_history: []
            }')

        # POST
        RESP_CODE=$(curl -sS -o /tmp/edgerun_resp.txt -w "%{http_code}" \
            -X POST -H "Content-Type: application/json" \
            -d "$PAYLOAD" "$ENDPOINT" 2>&1)

        echo "$(date -u +%FT%TZ) scan=$SCAN_NUM nodes=$N http=$RESP_CODE" >> "$LOG"

        # Toast feedback
        if [ "$RESP_CODE" = "200" ] || [ "$RESP_CODE" = "201" ] || [ "$RESP_CODE" = "204" ]; then
            termux-toast "edgerun: pushed $N nodes (#$SCAN_NUM)"
        else
            termux-toast "edgerun: push failed (http $RESP_CODE)"
        fi

        sleep "$INTERVAL"
    done
) >> "$LOG" 2>&1 &

LOOP_PID=$!
echo "$LOOP_PID" > "$MARKER"
echo "$(date -u +%FT%TZ) started pid=$LOOP_PID interval=${INTERVAL}s" >> "$LOG"
termux-toast "edgerun: started (every ${INTERVAL}s)"
