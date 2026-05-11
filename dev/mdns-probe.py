"""
mdns-probe.py — discover services via mDNS/Bonjour and SSDP/UPnP
emits JSON array of nodes to stdout (consumable by probe-mesh.ps1)

usage: python mdns-probe.py [seconds]   default 6s scan
"""
import sys, json, time, socket, threading
from collections import defaultdict

SCAN_SECONDS = int(sys.argv[1]) if len(sys.argv) > 1 else 6
nodes = []
seen_keys = set()

# ============================================================
# mDNS via zeroconf — service discovery
# ============================================================
def mdns_scan():
    try:
        from zeroconf import Zeroconf, ServiceBrowser, ServiceListener, ZeroconfServiceTypes
    except ImportError:
        print("[mdns] zeroconf not installed", file=sys.stderr)
        return

    discovered = {}

    class L(ServiceListener):
        def add_service(self, zc, type_, name):
            try:
                info = zc.get_service_info(type_, name, timeout=1500)
                if not info: return
                key = f"{type_}::{name}"
                if key in discovered: return
                addrs = []
                try:
                    addrs = [socket.inet_ntoa(a) for a in info.addresses if len(a) == 4]
                except Exception:
                    pass
                props = {}
                if info.properties:
                    for k, v in info.properties.items():
                        try:
                            kk = k.decode('utf-8', 'replace') if isinstance(k, bytes) else str(k)
                            vv = v.decode('utf-8', 'replace') if isinstance(v, bytes) else str(v)
                            props[kk] = vv
                        except Exception:
                            pass
                discovered[key] = {
                    'service_type': type_,
                    'service_name': name,
                    'host': info.server.rstrip('.') if info.server else None,
                    'port': info.port,
                    'addresses': addrs,
                    'properties': props,
                }
            except Exception as e:
                pass

        def remove_service(self, *a, **kw): pass
        def update_service(self, *a, **kw): pass

    try:
        zc = Zeroconf()
        # discover all service types in the first chunk
        types = []
        try:
            types = list(ZeroconfServiceTypes.find(zc=zc, timeout=2.0))
        except Exception:
            pass
        if not types:
            # fallback to common types
            types = [
                '_googlecast._tcp.local.', '_airplay._tcp.local.', '_raop._tcp.local.',
                '_ipp._tcp.local.', '_ipps._tcp.local.', '_pdl-datastream._tcp.local.',
                '_http._tcp.local.', '_https._tcp.local.',
                '_workstation._tcp.local.', '_companion-link._tcp.local.',
                '_homekit._tcp.local.', '_hap._tcp.local.',
                '_smb._tcp.local.', '_afpovertcp._tcp.local.',
                '_spotify-connect._tcp.local.', '_sonos._tcp.local.',
                '_hue._tcp.local.', '_nut._tcp.local.',
            ]
        listener = L()
        browsers = [ServiceBrowser(zc, t, listener) for t in types]
        time.sleep(SCAN_SECONDS)
        zc.close()
    except Exception as e:
        print(f"[mdns] error: {e}", file=sys.stderr)

    for k, info in discovered.items():
        host = info['host'] or info['service_name']
        # collapse multi-service same-host into per-(host,service) nodes
        node_id = f"mdns-{host}-{info['service_type'].rstrip('.')}".replace('.', '-')
        if node_id in seen_keys: continue
        seen_keys.add(node_id)
        label = host
        if info['service_type']:
            short_type = info['service_type'].rstrip('.').lstrip('_').split('.')[0]
            label = f"{host} ({short_type})"
        nodes.append({
            'id': node_id,
            'label': label,
            'medium': 'mdns',
            'service': info['service_type'].rstrip('.'),
            'host': host,
            'port': info['port'],
            'ip': info['addresses'][0] if info['addresses'] else None,
            'properties': info['properties'] or None,
        })

# ============================================================
# SSDP / UPnP via UDP M-SEARCH
# ============================================================
def ssdp_scan():
    addr = ('239.255.255.250', 1900)
    msg = (
        'M-SEARCH * HTTP/1.1\r\n'
        'HOST:239.255.255.250:1900\r\n'
        'MAN:"ssdp:discover"\r\n'
        'MX:2\r\n'
        'ST:ssdp:all\r\n\r\n'
    ).encode()
    discovered = {}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.settimeout(2.0)
        sock.sendto(msg, addr)
        deadline = time.time() + SCAN_SECONDS
        while time.time() < deadline:
            try:
                data, src = sock.recvfrom(2048)
                txt = data.decode('utf-8', 'replace')
                hdrs = {}
                for line in txt.split('\r\n')[1:]:
                    if ':' in line:
                        k, v = line.split(':', 1)
                        hdrs[k.strip().lower()] = v.strip()
                key = (src[0], hdrs.get('usn', ''), hdrs.get('st', ''))
                if key in discovered: continue
                discovered[key] = (src, hdrs)
            except socket.timeout:
                continue
            except Exception:
                break
        sock.close()
    except Exception as e:
        print(f"[ssdp] error: {e}", file=sys.stderr)

    # consolidate SSDP by IP — one node per device, services listed
    by_ip = defaultdict(lambda: {'services': set(), 'server': '', 'location': ''})
    for (src, hdrs) in discovered.values():
        ip = src[0]
        st = hdrs.get('st', '')
        if st: by_ip[ip]['services'].add(st)
        if hdrs.get('server'): by_ip[ip]['server'] = hdrs['server']
        if hdrs.get('location'): by_ip[ip]['location'] = hdrs['location']

    for ip, info in by_ip.items():
        node_id = f"ssdp-{ip}".replace('.', '-')
        if node_id in seen_keys: continue
        seen_keys.add(node_id)
        # short label from server brand
        server = info['server']
        brand = server.split('/')[0].split(',')[0] if server else 'upnp'
        if 'OpenWRT' in server: brand = 'OpenWRT (router)'
        elif 'Chromecast' in server: brand = 'Chromecast'
        elif 'MiniDLNA' in server: brand = 'MiniDLNA'
        elif 'Roku' in server: brand = 'Roku'
        nodes.append({
            'id': node_id,
            'label': f"{ip} · {brand}",
            'medium': 'mdns',
            'protocol': 'ssdp',
            'ip': ip,
            'server': server,
            'location': info['location'],
            'service_types': sorted(info['services']),
        })

# run both
t1 = threading.Thread(target=mdns_scan, daemon=True)
t2 = threading.Thread(target=ssdp_scan, daemon=True)
t1.start(); t2.start()
t1.join(timeout=SCAN_SECONDS + 4)
t2.join(timeout=SCAN_SECONDS + 4)

print(json.dumps(nodes, indent=2))
