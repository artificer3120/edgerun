#!/usr/bin/env python3
"""patch neonforge server.py to add /edgerun/upload (POST) + /edgerun/* (GET) routes."""
import re, time, shutil, os

p = "/home/ubuntu/neonforge/server.py"
shutil.copy(p, p + ".bak.preEdgerun." + str(int(time.time())))
src = open(p).read()

# 1. Add EDGERUN_DIR constant after MEECH_DIR
if "EDGERUN_DIR" not in src:
    src = src.replace(
        "MEECH_DIR = os.path.expanduser('~/.meech/output')",
        "MEECH_DIR = os.path.expanduser('~/.meech/output')\nEDGERUN_DIR = os.path.join(BASE_DIR, 'edgerun')\nos.makedirs(os.path.join(EDGERUN_DIR, 'scans'), exist_ok=True)",
    )

# 2. Add do_POST + edgerun GET routes BEFORE the existing 'def do_GET(self):'
edgerun_block = '''    # ============================================================
    # EDGERUN — open ingest endpoint, public read
    # ============================================================
    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/edgerun/upload':
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if length <= 0 or length > 5_000_000:
                    self.send_response(413); self.end_headers()
                    self.wfile.write(b'payload size out of bounds')
                    return
                body = self.rfile.read(length)
                mesh = json.loads(body.decode('utf-8', errors='replace'))
                if not isinstance(mesh, dict) or 'nodes' not in mesh:
                    self.send_response(400); self.end_headers()
                    self.wfile.write(b'mesh.json must be object with nodes[]')
                    return
                ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
                src_ip = self.headers.get('X-Real-IP') or self.client_address[0]
                # tag the scan
                mesh.setdefault('received', ts)
                mesh.setdefault('source_ip', src_ip)
                scan_id = ts + '-' + re.sub(r'[^a-zA-Z0-9]', '-', src_ip)[:16]
                mesh['scan_id_server'] = scan_id
                # write per-scan file + latest pointer
                scan_path = os.path.join(EDGERUN_DIR, 'scans', scan_id + '.json')
                with open(scan_path, 'w', encoding='utf-8') as f:
                    json.dump(mesh, f, indent=2)
                with open(os.path.join(EDGERUN_DIR, 'latest.json'), 'w', encoding='utf-8') as f:
                    json.dump(mesh, f, indent=2)
                # append to index
                idx_path = os.path.join(EDGERUN_DIR, 'index.json')
                idx = []
                if os.path.exists(idx_path):
                    try: idx = json.load(open(idx_path))
                    except: idx = []
                idx.insert(0, {
                    'id': scan_id,
                    'received': ts,
                    'source_ip': src_ip,
                    'node_count': len(mesh.get('nodes', [])),
                    'hub': (mesh.get('hub') or {}).get('label'),
                })
                idx = idx[:500]  # cap memory
                with open(idx_path, 'w', encoding='utf-8') as f:
                    json.dump(idx, f, indent=2)
                resp = json.dumps({'ok': True, 'scan_id': scan_id, 'received': ts}).encode()
                self.send_response(201)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(resp)
                return
            except Exception as e:
                self.send_response(500); self.end_headers()
                self.wfile.write(('upload error: ' + str(e)).encode())
                return
        self.send_response(404); self.end_headers()

    def do_OPTIONS(self):
        # CORS preflight for browser uploads
        if self.path.startswith('/edgerun/'):
            self.send_response(204)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            return
        self.send_response(404); self.end_headers()

    def _serve_edgerun_get(self, parsed):
        if parsed.path == '/edgerun/latest.json':
            fp = os.path.join(EDGERUN_DIR, 'latest.json')
        elif parsed.path == '/edgerun/index.json':
            fp = os.path.join(EDGERUN_DIR, 'index.json')
        elif parsed.path.startswith('/edgerun/scans/'):
            name = parsed.path[len('/edgerun/scans/'):]
            if '..' in name or '/' in name or not name.endswith('.json'):
                self.send_response(400); self.end_headers(); return True
            fp = os.path.join(EDGERUN_DIR, 'scans', name)
        else:
            return False
        if not os.path.exists(fp):
            self.send_response(404); self.end_headers()
            return True
        with open(fp, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(data)
        return True

    def do_GET(self):'''

# replace 'def do_GET(self):' with the block (but only once, at the first match)
if 'def do_POST' not in src:
    src = src.replace('    def do_GET(self):', edgerun_block, 1)

# 3. Inside do_GET, add an early-return for /edgerun/* GET routes.
# Insert right after 'parsed = urlparse(self.path)' (the FIRST one inside do_GET)
needle = "    def do_GET(self):\n        parsed = urlparse(self.path)\n"
inject = needle + "\n        if parsed.path.startswith('/edgerun/'):\n            if self._serve_edgerun_get(parsed):\n                return\n"
if "/edgerun/" not in src.split("def do_GET(self):", 1)[1][:500]:
    src = src.replace(needle, inject, 1)

open(p, 'w').write(src)
print("patched server.py — backup at", p + ".bak.preEdgerun.<ts>")
