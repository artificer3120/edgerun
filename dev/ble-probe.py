"""
ble-probe.py — live BLE advertisement scan via bleak (uses WinRT under the hood).
emits JSON array of nodes to stdout (consumable by probe-mesh.ps1)

usage: python ble-probe.py [seconds]   default 8s
"""
import sys, json, asyncio
from bleak import BleakScanner

SCAN_SECONDS = int(sys.argv[1]) if len(sys.argv) > 1 else 8

# Bluetooth SIG Company Identifiers — common subset
COMPANY_IDS = {
    6: "Microsoft", 76: "Apple", 117: "Samsung Electronics",
    101: "Hewlett-Packard", 224: "Google", 343: "Sony",
    411: "Bose", 137: "Plantronics/Poly", 305: "Bose Corp",
    1447: "Samsung", 65535: "internal/test",
    220: "Plantronics", 70: "TI", 89: "Nordic Semiconductor",
    301: "Logitech", 12: "Digianswer", 224: "Google",
    528: "Samsung Electronics Co.", 91: "TI",
    144: "Bose", 477: "Roku", 720: "GoPro",
    832: "Garmin", 224: "Google", 76: "Apple",
}

async def main():
    devices = await BleakScanner.discover(timeout=SCAN_SECONDS, return_adv=True)
    nodes = []
    for addr, (dev, adv) in devices.items():
        mac = addr.lower()
        name = dev.name or adv.local_name or "<unnamed>"
        mfr_ids = sorted(adv.manufacturer_data.keys()) if adv.manufacturer_data else []
        mfr_names = [COMPANY_IDS.get(i, f"id:{i}") for i in mfr_ids]
        svc_uuids = list(adv.service_uuids or [])
        nodes.append({
            'id': 'btle-' + mac.replace(':', ''),
            'label': name,
            'medium': 'btle',
            'addr': mac,
            'rssi': adv.rssi,
            'manufacturer_ids': mfr_ids,
            'manufacturer': mfr_names[0] if mfr_names else None,
            'service_uuids': svc_uuids[:6],
            'tx_power': adv.tx_power,
        })
    print(json.dumps(nodes, indent=2))

asyncio.run(main())
