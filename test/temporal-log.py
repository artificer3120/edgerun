"""
temporal-log.py — log each scan into sqlite, enrich nodes with first_seen / last_seen / scan_count.

usage: python temporal-log.py <mesh.json>
       overwrites mesh.json in place with enriched fields.
       maintains sqlite db at edgerun.db in same dir.
"""
import sys, os, json, sqlite3, datetime

if len(sys.argv) < 2:
    print("usage: temporal-log.py <mesh.json>", file=sys.stderr); sys.exit(1)

mesh_path = sys.argv[1]
db_path = os.path.join(os.path.dirname(mesh_path), 'edgerun.db')

with open(mesh_path, 'r', encoding='utf-8') as f:
    mesh = json.load(f)

con = sqlite3.connect(db_path)
con.execute("""CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    node_count INTEGER
)""")
con.execute("""CREATE TABLE IF NOT EXISTS observations (
    scan_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    medium TEXT,
    label TEXT,
    rssi INTEGER,
    raw TEXT,
    FOREIGN KEY(scan_id) REFERENCES scans(id)
)""")
con.execute("CREATE INDEX IF NOT EXISTS idx_obs_node ON observations(node_id)")
con.execute("CREATE INDEX IF NOT EXISTS idx_obs_scan ON observations(scan_id)")

# write this scan
ts = mesh.get('generated') or datetime.datetime.now(datetime.timezone.utc).isoformat()
cur = con.execute("INSERT INTO scans (ts, node_count) VALUES (?, ?)", (ts, len(mesh['nodes'])))
scan_id = cur.lastrowid
for n in mesh['nodes']:
    con.execute("INSERT INTO observations (scan_id, node_id, medium, label, rssi, raw) VALUES (?,?,?,?,?,?)",
                (scan_id, n.get('id'), n.get('medium'), n.get('label'),
                 n.get('rssi') if isinstance(n.get('rssi'), (int, float)) else None,
                 json.dumps(n)))

# enrich each node with temporal fields
node_ids = [n.get('id') for n in mesh['nodes'] if n.get('id')]
if node_ids:
    placeholders = ','.join('?' * len(node_ids))
    rows = con.execute(f"""
        SELECT o.node_id,
               MIN(s.ts) AS first_seen,
               MAX(s.ts) AS last_seen,
               COUNT(DISTINCT s.id) AS scan_count
        FROM observations o
        JOIN scans s ON s.id = o.scan_id
        WHERE o.node_id IN ({placeholders})
        GROUP BY o.node_id
    """, node_ids).fetchall()
    seen_map = {r[0]: {'first_seen': r[1], 'last_seen': r[2], 'scan_count': r[3]} for r in rows}
    for n in mesh['nodes']:
        m = seen_map.get(n.get('id'))
        if m:
            n.update(m)
            # is_new flag — first_seen equals current scan's ts (within 5s tolerance)
            n['is_new'] = (m['first_seen'] == ts)

# also gather: nodes that appeared in last 5 scans but NOT this one (departed)
prev_scans = con.execute("""
    SELECT id FROM scans WHERE id < ? ORDER BY id DESC LIMIT 5
""", (scan_id,)).fetchall()
departed = []
if prev_scans:
    prev_ids = tuple(r[0] for r in prev_scans)
    placeholders = ','.join('?' * len(prev_ids))
    cur_set = set(node_ids)
    rows = con.execute(f"""
        SELECT o.node_id, MAX(o.label), MAX(o.medium), MAX(s.ts)
        FROM observations o
        JOIN scans s ON s.id = o.scan_id
        WHERE o.scan_id IN ({placeholders})
        GROUP BY o.node_id
    """, prev_ids).fetchall()
    for nid, lbl, med, last in rows:
        if nid not in cur_set:
            departed.append({'id': nid, 'label': lbl, 'medium': med, 'last_seen': last, 'departed': True})

mesh['scan_id'] = scan_id
mesh['departed_recent'] = departed

# overall scan history summary
total_scans = con.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
mesh['scan_history'] = {'total_scans': total_scans, 'this_scan_id': scan_id}

con.commit()
con.close()

with open(mesh_path, 'w', encoding='utf-8') as f:
    json.dump(mesh, f, indent=2)

# also rewrite mesh-data.js
js_path = os.path.join(os.path.dirname(mesh_path), 'mesh-data.js')
with open(js_path, 'w', encoding='utf-8') as f:
    f.write('window.MESH_DATA = ')
    json.dump(mesh, f, indent=2)
    f.write(';')

print(f"[temporal] scan #{scan_id} logged · {len(mesh['nodes'])} nodes · {len(departed)} departed-recent · total scans: {total_scans}")
