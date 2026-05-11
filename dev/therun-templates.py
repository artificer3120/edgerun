"""
the run / newsletter template proposals — 3 designs, sent as separate emails.

A — runner vision     : stark white + bold red accent. mirror's edge interior.
B — rooftop dusk      : dusk blue + warm peach. lyrical, atmospheric.
C — dispatch          : black + mono red. mission-briefing comm intercept.

All carry the same dummy content (issue 001 / edgerun) so they're comparable.
"""
import base64, os, requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def vault_get(name):
    r = requests.post(
        os.environ.get('VAULT_URL', 'http://100.83.251.119:8120') + '/credential',
        json={'name': name},
        headers={'X-Vault-Key': os.environ.get('VAULT_KEY', '')},
        timeout=5,
    )
    r.raise_for_status()
    return r.json()['value']

creds = Credentials(
    token=None,
    refresh_token=vault_get('google_artificer3120_refresh_token'),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=vault_get('google_artificer3120_client_id'),
    client_secret=vault_get('google_artificer3120_client_secret'),
)
gmail = build('gmail', 'v1', credentials=creds)

TO = "c.t.gaughan@gmail.com"
FROM = "artificer3120@gmail.com"

# -------- shared dummy content (issue 001) --------
ISSUE_NUMBER = "001"
ISSUE_DATE = "10 may 2026"
HIGHLIGHTS = [
    {
        "n": "01",
        "title": "WlanScan via P/Invoke",
        "body": "Windows caches its wifi scan and refuses to refresh on demand. Reaching into wlanapi.dll directly with a 30-line C# inline-compile turned a stale 1-AP cache into 37 visible neighbors. Native Windows isn't dead — it's hidden behind a friendlier wrapper that lies to you.",
    },
    {
        "n": "02",
        "title": "Termux pocket scanner",
        "body": "Android can run the same probe over termux-api. Output goes to your downloads folder, viewer loads it via file picker. No upload, no aggregation, no GPS pairing. iOS does not get a runner badge — Apple does not expose any wifi scan API to user-space.",
    },
    {
        "n": "03",
        "title": "d3-force as Obsidian-style mesh map",
        "body": "processFlow is for static. cytoscape settles. d3-force keeps gentle motion forever — drag to grab, release to float. Real-world recon plotted as a living graph reads better than any table ever will.",
    },
]
LINK_HREF = "https://neonforge.untitledprojects.io/?p=edgerun"
LINK_LABEL = "open the edgerun map →"

# ===================================================================
# DESIGN A — RUNNER VISION
# stark white, bold red accent, generous whitespace, clean architectural sans
# ===================================================================
def design_a():
    rows = ""
    for h in HIGHLIGHTS:
        rows += f"""
        <tr><td style="padding:36px 0 0 0;">
          <div style="font-family:'Helvetica Neue',Arial,sans-serif;font-size:11px;color:#FF1F1F;letter-spacing:0.3em;font-weight:700;">// {h['n']}</div>
          <div style="font-family:'Helvetica Neue',Arial,sans-serif;font-size:24px;color:#0a0a0a;font-weight:700;line-height:1.15;margin-top:6px;letter-spacing:-0.01em;">{h['title']}</div>
          <div style="font-family:Georgia,serif;font-size:15px;color:#3a3a3a;line-height:1.55;margin-top:10px;">{h['body']}</div>
        </td></tr>"""
    return f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#ffffff;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;">
  <tr><td align="center" style="padding:64px 24px;">
    <table role="presentation" width="540" cellpadding="0" cellspacing="0" style="max-width:540px;width:100%;">

      <tr><td>
        <div style="font-family:'Helvetica Neue',Arial,sans-serif;font-size:11px;color:#FF1F1F;letter-spacing:0.4em;font-weight:700;">// THE RUN — ISSUE {ISSUE_NUMBER}</div>
        <div style="font-family:'Helvetica Neue',Arial,sans-serif;font-size:11px;color:#999;letter-spacing:0.2em;margin-top:6px;">{ISSUE_DATE.upper()}</div>
      </td></tr>

      <tr><td style="padding-top:48px;">
        <div style="font-family:'Helvetica Neue',Arial,sans-serif;font-size:42px;color:#0a0a0a;font-weight:900;line-height:1.05;letter-spacing:-0.02em;">field notes from the<br><span style="color:#FF1F1F;">edge of the network.</span></div>
      </td></tr>

      <tr><td style="padding-top:36px;">
        <div style="height:1px;background:#FF1F1F;width:48px;"></div>
      </td></tr>

      {rows}

      <tr><td style="padding:48px 0 24px 0;">
        <div style="height:1px;background:#FF1F1F;width:48px;"></div>
        <a href="{LINK_HREF}" style="display:inline-block;margin-top:24px;font-family:'Helvetica Neue',Arial,sans-serif;font-size:14px;color:#FF1F1F;text-decoration:none;font-weight:700;letter-spacing:0.02em;border-bottom:2px solid #FF1F1F;padding-bottom:2px;">{LINK_LABEL}</a>
      </td></tr>

      <tr><td style="padding-top:64px;">
        <div style="font-family:'Helvetica Neue',Arial,sans-serif;font-size:11px;color:#999;letter-spacing:0.2em;">— ORK3120 / RECON</div>
      </td></tr>

    </table>
  </td></tr>
</table>
</body></html>"""

# ===================================================================
# DESIGN B — ROOFTOP DUSK
# deep dusk blue + warm peach, slightly serif, atmospheric
# ===================================================================
def design_b():
    rows = ""
    for h in HIGHLIGHTS:
        rows += f"""
        <tr><td style="padding:32px 0 0 0;">
          <div style="font-family:'Iowan Old Style','Palatino Linotype',Georgia,serif;font-size:12px;color:#ff9c7a;letter-spacing:0.18em;font-style:italic;">no. {h['n']}</div>
          <div style="font-family:'Iowan Old Style','Palatino Linotype',Georgia,serif;font-size:26px;color:#f4ecdf;font-weight:600;line-height:1.2;margin-top:8px;">{h['title']}</div>
          <div style="font-family:'Helvetica Neue',Arial,sans-serif;font-size:14px;color:#c4b8a3;line-height:1.65;margin-top:12px;">{h['body']}</div>
        </td></tr>"""
    # subtle skyline divider via inline svg-ish ascii
    skyline = '<div style="font-family:monospace;color:#3a4358;letter-spacing:0;font-size:14px;line-height:1;">▁▁▃▁▂▅▂▁▃▁▆▁▂▁▄▂▁▃▆▂▁▁▂▃▁▂▆▁▃▁▂▁▅▂▁▃</div>'
    return f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#1a2438;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(180deg,#1a2438 0%,#2c3651 100%);background-color:#1a2438;">
  <tr><td align="center" style="padding:56px 24px;">
    <table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

      <tr><td>
        <div style="font-family:'Iowan Old Style','Palatino Linotype',Georgia,serif;font-size:14px;color:#ff9c7a;letter-spacing:0.3em;font-style:italic;">the run</div>
        <div style="font-family:'Helvetica Neue',Arial,sans-serif;font-size:11px;color:#7d8aa0;letter-spacing:0.18em;margin-top:6px;text-transform:uppercase;">issue {ISSUE_NUMBER} · {ISSUE_DATE}</div>
      </td></tr>

      <tr><td style="padding-top:40px;">
        <div style="font-family:'Iowan Old Style','Palatino Linotype',Georgia,serif;font-size:36px;color:#f4ecdf;font-weight:600;line-height:1.15;letter-spacing:-0.005em;">field notes from the rooftops.</div>
        <div style="font-family:'Iowan Old Style','Palatino Linotype',Georgia,serif;font-size:15px;color:#a8b3c7;font-style:italic;margin-top:14px;line-height:1.55;">what we found out there this week, the cleanest way to use it, and what's next.</div>
      </td></tr>

      <tr><td style="padding:32px 0 0 0;">{skyline}</td></tr>

      {rows}

      <tr><td style="padding:40px 0 0 0;">{skyline}</td></tr>

      <tr><td style="padding-top:28px;">
        <a href="{LINK_HREF}" style="display:inline-block;font-family:'Helvetica Neue',Arial,sans-serif;font-size:13px;color:#1a2438;background:#ff9c7a;text-decoration:none;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:12px 22px;border-radius:2px;">{LINK_LABEL}</a>
      </td></tr>

      <tr><td style="padding-top:48px;">
        <div style="font-family:'Iowan Old Style','Palatino Linotype',Georgia,serif;font-size:13px;color:#7d8aa0;font-style:italic;">— ork3120, on the rooftops</div>
      </td></tr>

    </table>
  </td></tr>
</table>
</body></html>"""

# ===================================================================
# DESIGN C — DISPATCH
# pure black, mono, red key lines, like a runner's mission briefing intercept
# ===================================================================
def design_c():
    rows = ""
    for h in HIGHLIGHTS:
        rows += f"""
        <tr><td style="padding:28px 0 0 0;">
          <div style="font-family:'JetBrains Mono','Cascadia Mono','Courier New',monospace;font-size:11px;color:#ff2e2e;letter-spacing:0.12em;">// HIGHLIGHT_{h['n']}</div>
          <div style="font-family:'JetBrains Mono','Cascadia Mono','Courier New',monospace;font-size:18px;color:#f5f5f5;font-weight:700;margin-top:10px;letter-spacing:-0.005em;">{h['title']}</div>
          <div style="font-family:'JetBrains Mono','Cascadia Mono','Courier New',monospace;font-size:13px;color:#9a9a9a;line-height:1.65;margin-top:10px;">{h['body']}</div>
        </td></tr>"""
    return f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#0a0a0a;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;">
  <tr><td align="center" style="padding:48px 24px;">
    <table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background:#0a0a0a;">

      <tr><td style="border:1px solid #ff2e2e;padding:18px 20px;">
        <div style="font-family:'JetBrains Mono','Cascadia Mono','Courier New',monospace;font-size:11px;color:#ff2e2e;letter-spacing:0.18em;">// DISPATCH</div>
        <div style="font-family:'JetBrains Mono','Cascadia Mono','Courier New',monospace;font-size:22px;color:#f5f5f5;font-weight:700;margin-top:8px;letter-spacing:-0.005em;">the run / {ISSUE_NUMBER}</div>
        <div style="font-family:'JetBrains Mono','Cascadia Mono','Courier New',monospace;font-size:11px;color:#666;letter-spacing:0.12em;margin-top:6px;">TIMESTAMP: {ISSUE_DATE.upper()} · CHANNEL: edge.recon</div>
      </td></tr>

      <tr><td style="padding-top:32px;">
        <div style="font-family:'JetBrains Mono','Cascadia Mono','Courier New',monospace;font-size:13px;color:#9a9a9a;line-height:1.65;">
          <span style="color:#ff2e2e;">&gt;</span> intercept follows. three highlights from this run. read the briefing, walk the path, run yours.
        </div>
      </td></tr>

      {rows}

      <tr><td style="padding:36px 0 0 0;">
        <div style="font-family:'JetBrains Mono','Cascadia Mono','Courier New',monospace;font-size:11px;color:#ff2e2e;letter-spacing:0.12em;">// PAYLOAD_LIVE</div>
        <a href="{LINK_HREF}" style="display:inline-block;margin-top:10px;font-family:'JetBrains Mono','Cascadia Mono','Courier New',monospace;font-size:13px;color:#0a0a0a;background:#ff2e2e;text-decoration:none;font-weight:700;padding:10px 16px;letter-spacing:0.04em;">{LINK_LABEL}</a>
      </td></tr>

      <tr><td style="padding-top:48px;">
        <div style="font-family:'JetBrains Mono','Cascadia Mono','Courier New',monospace;font-size:11px;color:#444;letter-spacing:0.12em;">// END_DISPATCH · ork3120 · recon</div>
      </td></tr>

    </table>
  </td></tr>
</table>
</body></html>"""

TEMPLATES = [
    ("the run / template A — runner vision",  design_a()),
    ("the run / template B — rooftop dusk",   design_b()),
    ("the run / template C — dispatch",       design_c()),
]

def send(subject, html_body):
    msg = MIMEMultipart('alternative')
    msg['To'] = TO
    msg['From'] = FROM
    msg['Subject'] = subject
    plain_fallback = f"{subject}\n\n(HTML preview only. View in a client that renders HTML.)\n\nLink: {LINK_HREF}"
    msg.attach(MIMEText(plain_fallback, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    res = gmail.users().messages().send(userId='me', body={'raw': raw}).execute()
    return res.get('id')

for subj, html in TEMPLATES:
    mid = send(subj, html)
    print(f"sent: {subj} (id: {mid})")
