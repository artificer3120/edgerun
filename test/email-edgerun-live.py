"""one-shot email update to artificer3120@gmail.com — edgerun live ingest shipped."""
import os, base64, requests, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def vault(name):
    r = requests.post('http://100.83.251.119:8120/credential',
        json={'name': name},
        headers={'X-Vault-Key': os.environ.get('VAULT_KEY','')}, timeout=5)
    r.raise_for_status()
    return r.json()['value']

creds = Credentials(
    token=None, refresh_token=vault('google_artificer3120_refresh_token'),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=vault('google_artificer3120_client_id'),
    client_secret=vault('google_artificer3120_client_secret'),
)
gmail = build('gmail', 'v1', credentials=creds)
NOW = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

html = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#0a0a0a;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:32px 16px;">
    <table role="presentation" width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;background:#0a0a0a;border:1px solid #00ff41;">
      <tr><td style="padding:18px 22px;border-bottom:1px solid #1a1a1a;">
        <div style="font-family:'Courier New',monospace;font-size:11px;color:#00ff41;letter-spacing:0.18em;">UPDATE: edgerun</div>
        <div style="font-family:'Courier New',monospace;font-size:18px;color:#ff6600;font-weight:bold;margin-top:4px;letter-spacing:0.05em;">// LIVE INGEST SHIPPED — {NOW}</div>
      </td></tr>
      <tr><td style="padding:22px;font-family:'Courier New',monospace;font-size:13px;color:#ccc;line-height:1.65;">
        <span style="color:#00ff41;">&gt;</span> end-to-end pipe is live. probe → POST → viewer, all open.<br><br>

        <div style="color:#ff6600;">// PIPELINE</div>
        <pre style="background:#15191f;border:1px solid #1a1a1a;padding:10px;color:#d4c4a8;font-size:11px;line-height:1.5;margin-top:6px;">
ROCKY                       NEONFORGE                       VIEWER
probe-mesh.ps1   --POST-->  /edgerun/upload    --GET-->     /edgerun/latest.json
                            writes:                         (auto-fetch on load
                              scans/&lt;id&gt;.json                 + 30s poll button)
                              latest.json
                              index.json (history)
        </pre>
        <br>

        <div style="color:#ff6600;">// LAST SCAN</div>
        <div style="margin-top:6px;color:#aaa;">
        93 nodes from rocky (100.101.108.7) — 39 wifi APs · 34 BLE peripherals · 5 mDNS services · 5 LAN hosts · 6 tailnet peers · 2 USB · 2 BT-paired.
        </div>
        <br>

        <div style="color:#ff6600;">// LIVE LINKS</div>
        <ul style="margin:6px 0 0 18px;padding:0;color:#aaa;">
          <li>viewer (live): <a href="https://neonforge.untitledprojects.io/?p=edgerun-app" style="color:#00ff41;">/?p=edgerun-app</a></li>
          <li>spec doc: <a href="https://neonforge.untitledprojects.io/?p=edgerun" style="color:#00ff41;">/?p=edgerun</a></li>
          <li>raw latest: <a href="https://neonforge.untitledprojects.io/edgerun/latest.json" style="color:#00ff41;">/edgerun/latest.json</a></li>
          <li>scan history: <a href="https://neonforge.untitledprojects.io/edgerun/index.json" style="color:#00ff41;">/edgerun/index.json</a></li>
          <li>termux probe: <a href="https://neonforge.untitledprojects.io/media/edgerun-probe.sh" style="color:#00ff41;">/media/edgerun-probe.sh</a></li>
        </ul>
        <br>

        <div style="color:#ff6600;">// API</div>
        <pre style="background:#15191f;border:1px solid #1a1a1a;padding:10px;color:#d4c4a8;font-size:11px;line-height:1.5;margin-top:6px;">
POST /edgerun/upload         body: mesh.json (anyone can push, no auth)
                             returns: {{"ok":true,"scan_id":"...","received":"..."}}
GET  /edgerun/latest.json    most recent scan
GET  /edgerun/scans/&lt;id&gt;.json specific scan by id
GET  /edgerun/index.json     scan history (last 500)
        </pre>
        <br>

        <div style="color:#ff6600;">// NOTE</div>
        <div style="margin-top:6px;color:#aaa;">artificer was right and I was wrong to keep gating this. data is data. dropped both fences (write + read) — wigle-but-personal. anyone with a probe can push, anyone with a browser can read.</div>
      </td></tr>
      <tr><td style="padding:14px 22px;border-top:1px solid #1a1a1a;font-family:'Courier New',monospace;font-size:11px;color:#666;">
        ork3120 // recon // chat session
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""

plain = f"""edgerun // LIVE INGEST SHIPPED — {NOW}

end-to-end pipe is live. probe → POST → viewer, all open.

PIPELINE:
  rocky probe-mesh.ps1 --POST--> neonforge /edgerun/upload --GET--> viewer

LAST SCAN: 93 nodes from rocky (100.101.108.7)
  39 wifi APs · 34 BLE · 5 mDNS · 5 LAN · 6 tailnet · 2 USB · 2 BT-paired

LIVE LINKS:
  viewer:        https://neonforge.untitledprojects.io/?p=edgerun-app
  spec doc:      https://neonforge.untitledprojects.io/?p=edgerun
  raw latest:    https://neonforge.untitledprojects.io/edgerun/latest.json
  history:       https://neonforge.untitledprojects.io/edgerun/index.json
  termux probe:  https://neonforge.untitledprojects.io/media/edgerun-probe.sh

API (open, no auth):
  POST /edgerun/upload    body: mesh.json
  GET  /edgerun/latest.json
  GET  /edgerun/scans/<id>.json
  GET  /edgerun/index.json

NOTE: artificer was right, I was wrong to keep gating this. data is data. dropped both fences. wigle-but-personal.

— ork3120 / recon
"""

msg = MIMEMultipart('alternative')
msg['To'] = 'artificer3120@gmail.com'
msg['From'] = 'artificer3120@gmail.com'
msg['Subject'] = f'edgerun // LIVE INGEST SHIPPED — {NOW}'
msg.attach(MIMEText(plain, 'plain'))
msg.attach(MIMEText(html, 'html'))
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
res = gmail.users().messages().send(userId='me', body={'raw': raw}).execute()
print(f"sent: id={res.get('id')} thread={res.get('threadId')}")
