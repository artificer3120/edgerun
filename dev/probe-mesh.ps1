# probe-mesh.ps1 — physical sensor probe for rocky
# emits mesh.json consumable by mesh-viewer.html
# author: ork3120 (recon), 2026-05-10

$ErrorActionPreference = "Continue"
$Out = Join-Path $PSScriptRoot "mesh.json"
$Now = (Get-Date).ToUniversalTime().ToString("o")
$nodes = New-Object System.Collections.ArrayList

# ============================================================
# OUI LOOKUP — load IEEE database once, share across all probes
# ============================================================
$OuiPath = Join-Path $PSScriptRoot "oui.csv"
$script:OuiMap = @{}
if (Test-Path $OuiPath) {
    Write-Host "[oui] loading IEEE database..." -ForegroundColor DarkCyan
    $ouiCount = 0
    foreach ($line in [System.IO.File]::ReadAllLines($OuiPath)) {
        if ($line.StartsWith('Registry,')) { continue }
        $parts = $line -split ',', 4
        if ($parts.Count -ge 3) {
            $assign = $parts[1].Trim()
            if ($assign.Length -eq 6 -and $assign -match '^[0-9A-Fa-f]+$') {
                $org = $parts[2].Trim().Trim('"').Trim()
                $script:OuiMap[$assign.ToUpper()] = $org
                $ouiCount++
            }
        }
    }
    Write-Host "[oui] $ouiCount vendor prefixes loaded" -ForegroundColor DarkCyan
} else {
    Write-Host "[oui] not found at $OuiPath - vendor lookup disabled" -ForegroundColor Yellow
}

function Get-Vendor([string]$mac) {
    if (-not $mac) { return $null }
    # strip separators, uppercase
    $clean = ($mac -replace '[^0-9A-Fa-f]', '').ToUpper()
    if ($clean.Length -lt 6) { return $null }
    $prefix = $clean.Substring(0, 6)
    # locally-administered (bit 1 of first byte set) → random MAC, no useful vendor
    $firstByte = [Convert]::ToInt32($prefix.Substring(0, 2), 16)
    if (($firstByte -band 0x02) -ne 0) { return "(random/local)" }
    if ($script:OuiMap.ContainsKey($prefix)) { return $script:OuiMap[$prefix] }
    return $null
}

function Add-Node($n) { [void]$nodes.Add($n) }

# ============================================================
# WI-FI — own AP + neighbors
# ============================================================
# trigger an active WlanScan via P/Invoke so neighbor APs aren't stale
Write-Host "[wifi] triggering active scan..." -ForegroundColor Cyan
try {
    if (-not ('NativeWlan' -as [type])) {
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class NativeWlan {
    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
    public struct WLAN_INTERFACE_INFO {
        public Guid InterfaceGuid;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst=256)]
        public string strInterfaceDescription;
        public uint isState;
    }
    [DllImport("wlanapi.dll")]
    public static extern uint WlanOpenHandle(uint dwClientVersion, IntPtr pReserved, out uint pdwNegotiatedVersion, out IntPtr phClientHandle);
    [DllImport("wlanapi.dll")]
    public static extern uint WlanCloseHandle(IntPtr hClientHandle, IntPtr pReserved);
    [DllImport("wlanapi.dll")]
    public static extern uint WlanEnumInterfaces(IntPtr hClientHandle, IntPtr pReserved, out IntPtr ppInterfaceList);
    [DllImport("wlanapi.dll")]
    public static extern uint WlanScan(IntPtr hClientHandle, ref Guid pInterfaceGuid, IntPtr pDot11Ssid, IntPtr pIeData, IntPtr pReserved);
    [DllImport("wlanapi.dll")]
    public static extern void WlanFreeMemory(IntPtr p);
}
"@
    }
    $clientVer = 2
    $negotiated = 0
    $clientHandle = [IntPtr]::Zero
    $r = [NativeWlan]::WlanOpenHandle($clientVer, [IntPtr]::Zero, [ref]$negotiated, [ref]$clientHandle)
    if ($r -eq 0) {
        $listPtr = [IntPtr]::Zero
        if ([NativeWlan]::WlanEnumInterfaces($clientHandle, [IntPtr]::Zero, [ref]$listPtr) -eq 0 -and $listPtr -ne [IntPtr]::Zero) {
            $count = [Runtime.InteropServices.Marshal]::ReadInt32($listPtr)
            $infoSize = [Runtime.InteropServices.Marshal]::SizeOf([type][NativeWlan+WLAN_INTERFACE_INFO])
            for ($i = 0; $i -lt $count; $i++) {
                $itemPtr = [IntPtr]::Add($listPtr, 8 + ($i * $infoSize))
                $info = [Runtime.InteropServices.Marshal]::PtrToStructure($itemPtr, [type][NativeWlan+WLAN_INTERFACE_INFO])
                $g = $info.InterfaceGuid
                [void][NativeWlan]::WlanScan($clientHandle, [ref]$g, [IntPtr]::Zero, [IntPtr]::Zero, [IntPtr]::Zero)
            }
            [NativeWlan]::WlanFreeMemory($listPtr)
        }
        [void][NativeWlan]::WlanCloseHandle($clientHandle, [IntPtr]::Zero)
        Start-Sleep -Seconds 4   # let driver populate scan results
    }
} catch { Write-Host "[wifi] scan trigger failed: $_" -ForegroundColor Yellow }

Write-Host "[wifi] reading scan results..." -ForegroundColor Cyan
try {
    # own connection
    $iface = & netsh wlan show interfaces 2>$null | Out-String
    $ownBssid = $null; $ownSsid = $null
    if ($iface -match 'BSSID\s+:\s+([0-9a-fA-F:]{17})') { $ownBssid = $matches[1].ToLower() }
    if ($iface -match '(?m)^\s*SSID\s+:\s+(.+)$')      { $ownSsid  = $matches[1].Trim() }

    # all visible networks with BSSIDs
    $raw = & netsh wlan show networks mode=bssid 2>$null | Out-String
    # split on SSID header — use [ \t]* to NOT consume the trailing newline (else hidden SSIDs eat the next line as their name)
    $blocks = [regex]::Split($raw, '(?m)^SSID \d+[ \t]*:[ \t]*')
    $apIdx = 0
    foreach ($b in $blocks) {
        if ([string]::IsNullOrWhiteSpace($b)) { continue }
        $lines = $b -split "`r?`n"
        $ssid = ($lines[0] -replace '^\s+|\s+$','')
        if (-not $ssid) { $ssid = "<hidden>" }
        # one SSID may have multiple BSSIDs — find each
        $bssidMatches = [regex]::Matches($b, 'BSSID \d+\s*:\s*([0-9a-fA-F:]{17})')
        $sigMatches   = [regex]::Matches($b, 'Signal\s*:\s*(\d+)%')
        $chMatches    = [regex]::Matches($b, '(?m)^\s*Channel\s*:\s*(\d+)')
        $radioMatches = [regex]::Matches($b, '(?m)^\s*Radio type\s*:\s*(.+)')

        for ($i = 0; $i -lt $bssidMatches.Count; $i++) {
            $bssid = $bssidMatches[$i].Groups[1].Value.ToLower()
            $sigPct = if ($i -lt $sigMatches.Count) { [int]$sigMatches[$i].Groups[1].Value } else { 0 }
            # convert % to RSSI estimate: 100% ≈ -40, 0% ≈ -100
            $rssi = -100 + [int]($sigPct * 0.6)
            $ch   = if ($i -lt $chMatches.Count) { [int]$chMatches[$i].Groups[1].Value } else { 0 }
            $radio= if ($i -lt $radioMatches.Count) { $radioMatches[$i].Groups[1].Value.Trim() } else { "" }
            $isOwn = ($bssid -eq $ownBssid)
            Add-Node @{
                id     = "wifi-$bssid"
                label  = $ssid
                medium = if ($isOwn) { "wifi-own" } else { "wifi-neighbor" }
                bssid  = $bssid
                rssi   = $rssi
                signal = $sigPct
                channel= $ch
                radio  = $radio
                vendor = Get-Vendor $bssid
            }
            $apIdx++
        }
    }
    Write-Host "[wifi] $apIdx APs" -ForegroundColor Green
} catch { Write-Host "[wifi] error: $_" -ForegroundColor Red }

# ============================================================
# BLUETOOTH LE — live advertisement scan
# (PS5.1 can't subscribe to WinRT events directly, so shell out
#  to bleak/python which uses the WinRT API under the hood)
# ============================================================
Write-Host "[btle] live scan via bleak/WinRT..." -ForegroundColor Cyan
try {
    $bleProbe = Join-Path $PSScriptRoot "ble-probe.py"
    if (Test-Path $bleProbe) {
        $bleJson = & python $bleProbe 8 2>$null | Out-String
        $bleJson = $bleJson.Trim()
        if ($bleJson.StartsWith('[')) {
            $bleNodes = $bleJson | ConvertFrom-Json
            foreach ($b in $bleNodes) {
                $h = @{}
                $b.PSObject.Properties | ForEach-Object { $h[$_.Name] = $_.Value }
                Add-Node $h
            }
            Write-Host "[btle] $($bleNodes.Count) live peripherals" -ForegroundColor Green
        } else {
            Write-Host "[btle] no JSON returned from ble-probe.py" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[btle] ble-probe.py not found - skipping" -ForegroundColor Yellow
    }
} catch { Write-Host "[btle] error: $_" -ForegroundColor Red }

# ============================================================
# BLUETOOTH — paired/cached devices via PnP
# ============================================================
Write-Host "[bluetooth] enumerating..." -ForegroundColor Cyan
try {
    $bt = Get-PnpDevice -Class Bluetooth -PresentOnly -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FriendlyName -and
            $_.FriendlyName -notmatch 'Generic|Microsoft|Enumerator|Adapter|Radio|Device$' -and
            $_.InstanceId -match 'BTHENUM\\Dev'
        }
    $btCount = 0
    foreach ($d in $bt) {
        $addr = $null
        if ($d.InstanceId -match '_([0-9a-fA-F]{12})') {
            $raw = $matches[1].ToLower()
            $addr = ($raw -split '(.{2})' | Where-Object { $_ }) -join ':'
        }
        $idTail = if ($addr) { ($addr -replace ':','') } else { ($d.InstanceId -replace '[^A-Za-z0-9]','-').Substring(0,[Math]::Min(20,$d.InstanceId.Length)) }
        Add-Node @{
            id     = "bt-$idTail"
            label  = $d.FriendlyName
            medium = "btclassic"
            addr   = $addr
            status = $d.Status
            vendor = Get-Vendor $addr
        }
        $btCount++
    }
    Write-Host "[bluetooth] $btCount paired" -ForegroundColor Green
} catch { Write-Host "[bluetooth] error: $_" -ForegroundColor Red }

# ============================================================
# LAN — neighbor table (ARP) for own subnet
# ============================================================
Write-Host "[lan] reading neighbor table..." -ForegroundColor Cyan
try {
    # active default route gives our subnet
    $route = Get-NetRoute -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue | Sort-Object RouteMetric | Select-Object -First 1
    $gatewayIf = $null
    if ($route) { $gatewayIf = $route.InterfaceIndex }

    $nbrs = Get-NetNeighbor -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.State -in 'Reachable','Stale','Permanent' -and
            $_.LinkLayerAddress -and
            $_.LinkLayerAddress -ne '00-00-00-00-00-00' -and
            $_.IPAddress -notmatch '^(0\.|169\.254\.|22[4-9]\.|23[0-9]\.|24[0-9]\.|25[0-5]\.|255\.)'
        }
    if ($gatewayIf) { $nbrs = $nbrs | Where-Object { $_.InterfaceIndex -eq $gatewayIf } }

    $lanCount = 0
    foreach ($n in $nbrs) {
        $mac = $n.LinkLayerAddress.ToLower() -replace '-',':'
        Add-Node @{
            id     = "lan-$mac"
            label  = $n.IPAddress
            medium = "lan"
            ip     = $n.IPAddress
            mac    = $mac
            state  = $n.State.ToString()
            vendor = Get-Vendor $mac
        }
        $lanCount++
    }
    Write-Host "[lan] $lanCount hosts" -ForegroundColor Green
} catch { Write-Host "[lan] error: $_" -ForegroundColor Red }

# ============================================================
# USB — present USB devices (filter Hubs/Roots)
# ============================================================
Write-Host "[usb] enumerating..." -ForegroundColor Cyan
try {
    $usb = Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue |
        Where-Object {
            $_.InstanceId -match '^USB\\VID_' -and
            $_.FriendlyName -and
            $_.Class -notin @('USB','HIDClass') -and
            $_.FriendlyName -notmatch 'Hub|Composite|Root|Generic USB'
        }
    $usbCount = 0
    foreach ($d in $usb) {
        $vid = $null; $devPid = $null
        if ($d.InstanceId -match 'VID_([0-9A-F]{4})&PID_([0-9A-F]{4})') {
            $vid = $matches[1]; $devPid = $matches[2]
        }
        $idKey = if ($vid -and $devPid) { "$vid-$devPid" } else { ($d.InstanceId -replace '[^A-Za-z0-9]','-').Substring(0,[Math]::Min(20,$d.InstanceId.Length)) }
        Add-Node @{
            id     = "usb-$idKey"
            label  = $d.FriendlyName
            medium = "usb"
            vid    = $vid
            pid    = $devPid
            class  = $d.Class
        }
        $usbCount++
    }
    Write-Host "[usb] $usbCount devices" -ForegroundColor Green
} catch { Write-Host "[usb] error: $_" -ForegroundColor Red }

# ============================================================
# mDNS / SSDP — service discovery (chromecasts, printers, smart bulbs, routers)
# ============================================================
Write-Host "[mdns] scanning service discovery..." -ForegroundColor Cyan
try {
    $mdnsProbe = Join-Path $PSScriptRoot "mdns-probe.py"
    if (Test-Path $mdnsProbe) {
        $mdnsJson = & python $mdnsProbe 6 2>$null | Out-String
        $mdnsJson = $mdnsJson.Trim()
        if ($mdnsJson.StartsWith('[')) {
            $mdnsNodes = $mdnsJson | ConvertFrom-Json
            foreach ($m in $mdnsNodes) {
                $h = @{}
                $m.PSObject.Properties | ForEach-Object { $h[$_.Name] = $_.Value }
                Add-Node $h
            }
            Write-Host "[mdns] $($mdnsNodes.Count) services" -ForegroundColor Green
        } else {
            Write-Host "[mdns] no JSON returned from mdns-probe.py" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[mdns] mdns-probe.py not found - skipping" -ForegroundColor Yellow
    }
} catch { Write-Host "[mdns] error: $_" -ForegroundColor Red }

# ============================================================
# TAILNET — tailscale peers (logical mesh layer)
# ============================================================
Write-Host "[tailnet] enumerating peers..." -ForegroundColor Cyan
try {
    $tsRaw = & tailscale status --json 2>$null | Out-String
    if ($tsRaw -and $tsRaw.Trim().StartsWith("{")) {
        $ts = $tsRaw | ConvertFrom-Json
        $peerCount = 0
        if ($ts.Peer) {
            $ts.Peer.PSObject.Properties | ForEach-Object {
                $p = $_.Value
                $ip = if ($p.TailscaleIPs -and $p.TailscaleIPs.Count -gt 0) { $p.TailscaleIPs[0] } else { $null }
                $idTail = if ($ip) { $ip -replace '\.','-' } else { ($p.HostName -replace '[^A-Za-z0-9]','-') }
                Add-Node @{
                    id     = "tail-$idTail"
                    label  = $p.HostName
                    medium = "tailnet"
                    ip     = $ip
                    dns    = $p.DNSName
                    os     = $p.OS
                    online = [bool]$p.Online
                    relay  = $p.Relay
                    active = [bool]$p.Active
                }
                $peerCount++
            }
        }
        Write-Host "[tailnet] $peerCount peers" -ForegroundColor Green
    } else {
        Write-Host "[tailnet] tailscale not running or no JSON" -ForegroundColor Yellow
    }
} catch { Write-Host "[tailnet] error: $_" -ForegroundColor Red }

# ============================================================
# emit
# ============================================================
$mesh = @{
    generated = $Now
    hub = @{ id = "rocky"; label = "rocky"; note = "Windows 11 desktop · ctgau · physical sensor probe" }
    nodes = $nodes.ToArray()
    layers_present = ($nodes.medium | Sort-Object -Unique)
}

$json = $mesh | ConvertTo-Json -Depth 8
# write UTF-8 without BOM so the JSON parses cleanly downstream
[System.IO.File]::WriteAllText($Out, $json, (New-Object System.Text.UTF8Encoding $false))

# also emit mesh-data.js so the viewer can auto-load it without a server
$jsOut = Join-Path $PSScriptRoot "mesh-data.js"
$jsBody = "window.MESH_DATA = " + $json + ";"
[System.IO.File]::WriteAllText($jsOut, $jsBody, (New-Object System.Text.UTF8Encoding $false))

# ============================================================
# TEMPORAL LOG — log scan to sqlite, enrich with first_seen/last_seen/is_new
# (overwrites mesh.json + mesh-data.js with enriched fields)
# ============================================================
$temporalProbe = Join-Path $PSScriptRoot "temporal-log.py"
if (Test-Path $temporalProbe) {
    & python $temporalProbe $Out
}

# ============================================================
# LIVE SYNC — push to neonforge for the public viewer
# ============================================================
Write-Host "[push] uploading scan to neonforge..." -ForegroundColor Cyan
try {
    $uploadResp = Invoke-RestMethod -Method Post -Uri "https://neonforge.untitledprojects.io/edgerun/upload" -ContentType "application/json" -InFile $Out -TimeoutSec 15
    Write-Host "[push] scan_id=$($uploadResp.scan_id)" -ForegroundColor Green
} catch {
    Write-Host "[push] upload failed: $_" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "[done] $($nodes.Count) nodes -> $Out" -ForegroundColor Yellow
