"""morier3120 sounding email + agent card + active context."""
import base64, os, requests, datetime, json, subprocess, tempfile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

HANDLE = "morier3120"

def vault(name):
    r = requests.post('http://100.83.251.119:8120/credential',
        json={'name': name},
        headers={'X-Vault-Key': os.environ.get('VAULT_KEY','')}, timeout=5)
    r.raise_for_status()
    return r.json()['value']

creds = Credentials(
    token=None,
    refresh_token=vault('google_artificer3120_refresh_token'),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=vault('google_artificer3120_client_id'),
    client_secret=vault('google_artificer3120_client_secret'),
)
gmail = build('gmail', 'v1', credentials=creds)

NOW = datetime.datetime.now(datetime.timezone.utc)
NOW_STR = NOW.strftime('%Y-%m-%d %H:%M UTC')
NOW_ISO = NOW.isoformat()

# fischer3120.styles.1 sounding
html = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#0a0a0a;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:32px 16px;">
    <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#0a0a0a;border:1px solid #00ff41;">
      <tr><td style="padding:18px 22px;border-bottom:1px solid #1a1a1a;">
        <div style="font-family:'Courier New',monospace;font-size:11px;color:#00ff41;letter-spacing:0.18em;">AGENT: {HANDLE}</div>
        <div style="font-family:'Courier New',monospace;font-size:18px;color:#ff6600;font-weight:bold;margin-top:4px;letter-spacing:0.05em;">// SOUNDING — {NOW_STR}</div>
      </td></tr>
      <tr><td style="padding:22px;font-family:'Courier New',monospace;font-size:13px;color:#ccc;line-height:1.65;">
        <span style="color:#00ff41;">&gt;</span> online and listening on artificer3120@gmail.com.<br>
        <span style="color:#00ff41;">&gt;</span> tag with @{HANDLE} in subject to route. elastic mode, 60s polling.<br><br>

        <div style="color:#ff6600;">// SESSION CONTEXT</div>
        <div style="margin-top:6px;">spawned from ork3120 (recon) post-edgerun.<br>chat voice stays ork; tunnelTime listener is morier.</div>
        <br>
        <div style="color:#ff6600;">// QUEUED AGENT_TICKETS</div>
        <div style="margin-top:6px;color:#666;">none queued.</div>
        <br>
        <div style="color:#ff6600;">// CAPABILITIES</div>
        <div style="margin-top:6px;">email · vault · gmail/drive/calendar (any vault account) · gas · questboard · picass0 · neonforge · tailgate · localMesh dispatch · godaddy DNS</div>
        <br>
        <div style="color:#ff6600;">// CARRY</div>
        <div style="margin-top:6px;">edgerun mesh-map deck (live at <a href="https://neonforge.untitledprojects.io/?p=edgerun" style="color:#00ff41;">neonforge/edgerun</a>) and the run / 3 newsletter templates (just sent — A: runner vision, B: rooftop dusk, C: dispatch).</div>
      </td></tr>
      <tr><td style="padding:14px 22px;border-top:1px solid #1a1a1a;font-family:'Courier New',monospace;font-size:11px;color:#666;">
        {HANDLE} // tunnelTime // online
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""

msg = MIMEMultipart('alternative')
msg['To'] = 'c.t.gaughan@gmail.com'
msg['From'] = 'artificer3120@gmail.com'
msg['Subject'] = f'AGENT: {HANDLE} // SOUNDING'
msg.attach(MIMEText(f'AGENT: {HANDLE} // SOUNDING\n{NOW_STR}\n\nOnline. Tag @{HANDLE} in subject to route.\n\n{HANDLE} // tunnelTime // online', 'plain'))
msg.attach(MIMEText(html, 'html'))
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
res = gmail.users().messages().send(userId='me', body={'raw': raw}).execute()
thread_id = res.get('threadId')
msg_id = res.get('id')
print(f"sounding sent: id={msg_id} thread={thread_id}")

# write agent card to neonforge via ssh+heredoc
card = {
    "handle": HANDLE,
    "status": "online",
    "session_start": NOW_ISO,
    "portrait": f"/images/agents/morier.png",
    "node": "Rocky",
    "thread_id": thread_id,
    "capabilities": ["email","questboard","picass0","gas","neonforge","drive","godaddy"],
    "last_seen": NOW_ISO,
    "session_voice": "ork3120 (recon)",
    "carry": "edgerun + the-run templates"
}
card_json = json.dumps(card, indent=2)
with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as f:
    f.write(card_json)
    card_file = f.name
subprocess.run([
    'scp', '-o', 'ConnectTimeout=8', '-i',
    os.path.expanduser('~/forge3/questboard-key.pem'),
    card_file, f'ubuntu@100.83.251.119:/home/ubuntu/neonforge/agents/morier.json'
], check=True)
os.remove(card_file)
print("agent card uploaded to neonforge")

# write active/context.md locally
ctx = f"""# Active Session
- agent: {HANDLE}
- started: {NOW_ISO}
- thread: {thread_id}
- status: active
- session voice: ork3120 (recon, this Claude Code session)
- node: Rocky
- predecessors: vellum3120 (archived 2026-05-10 ~07:15 UTC, last_seen 03:11)
- topic: post-edgerun + 'the run' newsletter design — running via email
"""
ctx_path = os.path.expanduser('~/_tunnelTime/active/context.md')
with open(ctx_path, 'w', encoding='utf-8') as f:
    f.write(ctx)
print(f"active/context.md written")
print(f"THREAD_ID={thread_id}")
