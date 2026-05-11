# Pebble — Full Physical
**Patient:** Pebble (Galaxy S22+, SM-S906U)
**Examined:** 2026-05-10, 13:47–13:53 EDT
**Examiner:** christemio (recon)
**Method:** SSH (Termux context) + adb shell (system context), parallel passes
**Raw artifacts:** `termux-context.txt`, `system-context.txt` in this folder

---

## Identity

| field | value |
|---|---|
| manufacturer / brand | samsung / samsung |
| model | SM-S906U (Galaxy S22+) |
| internal codename | g0q (g0qsqw variant) |
| serialno | (redacted by Samsung — `ro.serialno` empty) |
| build fingerprint | samsung/g0qsqw/g0q:16/BP2A.250605.031.A3/S906USQS9GZB4:user/release-keys |
| Android | **16** (API 36, OneUI Korea-built `dpi@SWDK3718`) |
| security patch | 2026-02-05 |
| build date | Fri Feb 13 2026 (Korea) |
| build type | user (release-keys, official firmware) |
| device name | Pebble |
| Bluetooth name | Pebble |
| android_id | 8ecd23232aae9ff8 |

## Hardware

| field | value |
|---|---|
| CPU | aarch64 (arm64-v8a), 8 cores, ARMv8.6, BogoMIPS 38.40, part 0xd46 (Cortex-X3) |
| features | aes pmull sha1/2/3/512 sm3/sm4 fp16 dotprod bf16 i8mm pacga bti |
| RAM | 7.1 GiB total, 2.1 GiB available, ~4.6 GiB resident |
| Swap | 8.0 GiB total, 3.5 GiB used (45% — phone is hot) |
| Display | 1080×2340 @ 450 dpi (≈393 ppi) |
| Storage `/data` | **104 GB total, 101 GB used, 2.6 GB free → 98% full** ⚠️ |
| Battery | Li-ion, level 73%, voltage 3.94 V, temp 30.1°C, health "good", **discharging** (no charger) |
| Battery cycle count | 0 (unreported by Samsung — could be early-life or stripped from API) |
| Discharge rate today | 81% → 73% in ~35 min (~14% / hr — heavy load: Discord + Termux + adb session) |
| Uptime | 1 day 3:30 (since 2026-05-09 ~10:23 EDT) |
| Load avg | 3.93 / 3.35 / 4.20 (high — multitasking pressure) |

## Sensors (the impressive part)

**40+ named sensors.** Highlights:

| sensor | vendor | rate cap |
|---|---|---|
| Accelerometer (LSM6DSO) | STMicro | 416 Hz |
| Gyroscope (LSM6DSO) | STMicro | 416 Hz |
| Magnetometer (AK09918) | AKM | 100 Hz |
| Pressure (LPS22HH) | STMicro | 25 Hz |
| Ambient Light (STK33915) | sensortek | on-change |
| Proximity (palm + IR) | Samsung | wake-up |
| Step counter / detector | Samsung | activity-recog perm |
| Pick-up / Tilt / Flip cover | Samsung | wake gestures |
| Pocket / Pocket-position mode | Samsung | wake |
| Grip sensor (ISG6320) | IMAGIS | wake |
| Hall IC (magnetic switch) | Samsung | non-wake |
| Rear ALS (TSL2510) | AMS | 100 Hz, biometric perm |
| 9-axis fusion (rotation, gravity, linear-accel, game-rot) | QTI | 200 Hz |

Value masked on Rear ALS (HRM_EXT permission gate). Most sensors are accessible to apps that hold standard sensor permission. Step counter requires `ACTIVITY_RECOGNITION`.

## Network

### Wi-Fi (active default route)
- **SSID:** `Verizon_Z4KL4X` (Verizon FiOS / G3100 router, domain `mynetworksettings.com`)
- **BSSID:** 78:67:0e:e6:a1:0a
- **Pebble's MAC (randomized per-network):** 72:a3:80:22:26:bc
- **IPv4:** 192.168.1.153 / gw 192.168.1.1
- **IPv6:** 2600:4041:536a:4000:70a3:80ff:fe22:26bc/64 + privacy address
- **Wi-Fi 6 (11ax)**, 5500 MHz (5 GHz channel 100), RSSI **-46 dBm** (excellent)
- Negotiated link: **1134 Mbps tx / 1200 Mbps rx**
- Country code: US

**Wi-Fi feature set:** WPA3-SAE/SAE-PK/SAE-H2E, OWE, FILS, WPA-Personal, MAC randomization, scan randomization, hotspot/AP-STA, P2P, Aware, Passpoint, RTT (D2D & D2AP), TDLS, MBO, DPP enrollee/responder, WFD R2, Wi-Fi Direct, WEP (legacy).

### Cellular (backup)
- **Carrier:** T-Mobile (MCC 310 / MNC 260)
- **Tech:** **5G NR Standalone**, band **n71** (low band 600 MHz)
- **Cell:** PCI 215, NRARFCN 124570, TAC redacted
- **Signal:** SS-RSRP -87 dBm, SS-RSRQ -11, SS-SINR 6 → level 2 of 5 (decent)
- IMS over NR active (T-Mobile IMS APN connected)
- IPv6 only on rmnet_data1: 2607:fc20:5512:296a:ad3:a0c:af6d:cc11/64
- Mobile data state: **on** (not the active default — wifi wins)
- 2nd SIM slot: OUT_OF_SERVICE / unconfigured

### Public
- Public IP from Termux: **100.2.119.55** (this is in Verizon FiOS Boston/NYC consumer space — note: looks like a CGNAT block; 100.64.0.0/10 is RFC 6598 carrier-grade NAT, but 100.2.x.x is general Verizon allocation. It's not the home WAN if FiOS gives a public — could be carrier NAT or just the actual WAN)

### Tailscale
- Tailnet IP `100.126.74.43` confirmed reachable (we ssh'd in over it)
- `ip addr show tailscale0` returned empty from Termux's untrusted_app context — SELinux blocks the read, not absence. Tailscale IS up; you can verify from Rocky with `tailscale ping pebble`.

### Bluetooth
- **enabled, state ON**, name `Pebble`, address ends `:F3:66`
- 5 BLE app subscribers (Samsung MDX/beacon/MCF + android system)
- 27h30m since enabled (matches uptime)

## Storage Map

```
/data            104G  101G used  2.6G free  98%  ⚠️
/cache           779M   16M used                3%
/dev/block/dm-6  6.4G  6.4G       100%  /  (system)
/storage/emulated/0  fuse mount of /data  (same partition)
```

**Termux home:** 22 KB (basically empty — fresh install)

## Apps (third-party only, 144 packages)

### Recon-relevant / mesh
| package | what |
|---|---|
| `com.termux` | Termux (Google Play, v2026.02.11) |
| `com.tailscale.ipn` | **Tailscale (yes, installed)** — that's how the tailnet IP works |
| `com.anthropic.claude` | Claude app |
| `com.openai.chatgpt` | ChatGPT |
| `ai.x.grok` | Grok |
| `com.ai.venice` | Venice AI |
| `io.elevenlabs.coreapp` | ElevenLabs |

### Auth/2FA stack (overlapping — operator runs many)
- Google Authenticator, Microsoft Authenticator, Duo, Okta, Authy-style (`authenticator.passkey...`), `com.authenticator.app.starnest`, Oracle IDM, Azure Authenticator
- ProtonMail, ProtonVPN

### Messaging
- Discord, Slack, Telegram, WhatsApp, Signal (`org.thoughtcrime.securesms`), Bluesky, Twitter/X, Instagram, Threads (`com.instagram.barcelona`), Facebook, Messenger, WeChat (`com.tencent.mm`), Snapchat, TikTok (`com.zhiliaoapp.musically`)

### Finance/identity stack
- Capital One, Wells Fargo, Chime, PayPal, Venmo, Cash App, Coinbase, Brigit, Cleo, Dave, Square, Geico, Walgreens/CVS, Walmart

### Food/delivery
- DoorDash, Uber Eats, Uber, Lyft, McDonald's, Burger King, Popeyes, Shake Shack, Slice, Yelp, Seamless, TGTG, Drink Water Reminder

### Gaming
- Hearthstone, MTGA, Pokemon Go, FF7 Ever Crisis, Last War, Idle Apocalypse, Potions & Spells, PSX (PS Remote), Roll20, Twilight (Oculus Quest companion)

### Photo / camera / scan
- Google Photos, Scaniverse (Niantic 3D scanning), Zhiyun cama, Foxit PDF

### Notable absent (per ork3120's Mode 3 questions)
- **F-Droid: NOT in third-party list** (couldn't find by string — would need a separate `pm list packages | grep -i fdroid` to be conclusive)
- **Termux:API: NOT installed** (com.termux.api would appear; only com.termux is present)
- **Termux:Widget: NOT installed**
- **No Tasker / MacroDroid / Automate / KDE Connect**

## Termux Environment

| field | value |
|---|---|
| Termux version | googleplay.2026.02.11 |
| user | u0_a21 (uid 10021) — **this is the SSH username** |
| home | /data/data/com.termux/files/home (22 KB used) |
| PREFIX | /data/data/com.termux/files/usr |
| bash | 5.3.9 |
| openssh | 10.3p1 |
| apt | 3.1.15 |
| sshd | running (PIDs 4425, 4428, 8460) on **port 8022** |
| ~/.ssh/authorized_keys | 101 bytes — Rocky's `id_ed25519.pub` (installed by christemio 2026-05-10 13:48) |
| ~/.termux/termux.properties | absent |
| ~/.shortcuts/ | absent |
| ~/storage/ symlinks | absent (termux-setup-storage never run) |

### Termux pkg list-installed (curated)
core: bash 5.3.9, coreutils 9.9, util-linux, sed, gawk, grep, findutils, less, nano, ed, tar, unzip, dpkg, apt
net: openssh 10.3p1, openssh-sftp-server, curl 8.18.0, libcurl, libssh2, krb5, ldns, libnghttp2/3, libngtcp2, openssl 3.6.1, ca-certificates
crypto: gpgv, libgcrypt, libgpg-error, libassuan, libnpth, ncurses, readline
proc: procps, psmisc, net-tools, inetutils, dos2unix
termux integration: termux-am 0.8.0, termux-auth 1.5.0, termux-exec 1.8, termux-keyring 3.15, termux-tools 3.0.9, termux-licenses 2.1

24 packages have upgrades available (curl 8.18 → 8.20, ca-certs, openssl 3.6.1 → 3.6.2, etc.) — `pkg upgrade` is on the table when you want.

## Security Posture

| field | value |
|---|---|
| SELinux | **enforcing** |
| verified boot | **green** (locked, official firmware) |
| bootloader locked | **yes** (`ro.boot.flash.locked = 1`) |
| build tags | release-keys |
| storage encryption | **encrypted** (file-based encryption) |
| /system/bin/su | absent — **not rooted** |
| dev settings enabled | yes |
| adb_enabled | yes |
| adb_wifi_enabled | yes (that's what we paired through) |
| install_non_market_apps | **1** (sideloading allowed) |
| airplane mode | off |
| location services | on (no provider list returned — Samsung gates `location_providers_allowed` to null in API 36) |

## What This Means for Mode 3

### Confirmed reachable
- Probe runner (Termux + bash + curl) → ✓ all installed
- POST to neonforge ingest → ✓ curl 8.18 over wifi/cellular
- SSH-driven script delivery → ✓ pubkey installed, port 8022 open
- Tailscale-bound traffic → ✓ Tailscale app installed, tailnet reachable
- Movement detection (accelerometer + step counter) → ✓ sensors present and rate-capped at 416 Hz

### Blocked without operator action
- **Wi-Fi scan / BSSID enumeration** — needs `Termux:API` APK installed AND `ACCESS_FINE_LOCATION` granted to it. Without API APK, no `termux-wifi-scaninfo` binary.
- **GPS / location** — same gate (Termux:API APK + permission)
- **Sensor stream (accel for "is moving")** — same gate
- **Tap-to-launch widget** — needs `Termux:Widget` APK + populated `~/.shortcuts/`
- **Camera, mic, SMS, contacts** — Termux:API gates each

### Reachable now via SSH (no APK needed)
- BSSID of currently-connected AP only (one entry, via `ip` / `dumpsys wifi` from system shell — not from Termux untrusted_app)
- Public IP (curl ipify)
- Cell tower info (via dumpsys from adb shell — not Termux)
- Battery state (via dumpsys from adb shell)

### Recommendation track
Mode 3 needs the Termux:API + Termux:Widget APKs on Pebble. Both are dead apps on Google Play (Termux org pulled them years ago). They have to come from F-Droid OR direct GitHub APK download. **F-Droid is not installed and direct APK install needs operator tap on the install popup.** This is the operator-tap moment ork3120 flagged.

## Anomalies

1. **/data is 98% full (2.6 GB free).** Some apps will start misbehaving below ~5%. Cleanup target: 144 third-party apps, lots of games. Not urgent but worth noting.
2. **Swap is 45% used (3.5 GB).** Memory pressure consistent with running Discord + Termux + multiple session tabs.
3. **Discharge rate ~14%/hr.** With current load. Untethered Mode 3 needs to plan for this — plug in or limit session length.
4. **No GPS in standby.** location_providers_allowed returned null from settings — could be deprecated API on A16, not literal "off". Operator can verify in Settings → Location.
5. **Tailscale interface invisible to Termux.** Not a fault — SELinux gates `tailscale0` from untrusted_app. Tailscale IS up. If a probe in Termux needs to detect "am I on tailnet right now," it should `curl http://100.83.251.119` or similar reachability test rather than `ip addr`.

---

## Source files

- `system-context.txt` — adb shell pass (96 KB) — full dumpsys, getprop, settings, sensors, packages
- `termux-context.txt` — ssh-from-Termux pass (13 KB) — env, pkg list, .ssh state, bash version
- `d.sh`, `install.sh` — diagnostic scripts pushed to Pebble (also persist on the device at `/storage/emulated/0/Android/data/com.termux/files/`)
