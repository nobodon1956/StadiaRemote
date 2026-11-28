param(
    [string]$ExePath = "",
    [switch]$Restore
)

$ErrorActionPreference = "Stop"

# Precompiled zlib-compressed Python 3.13 marshal payload from launcher_125hz.py
$PatchedUlen = 20103
$PatchedSha256 = "367f11b104b3652d9bea5b08814925b94634d6982a125ec8f35510b4db1ed0f1"
$PatchedB64 = "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"

function Read-UInt32BE([byte[]]$buf, [int]$off) {
    return ([uint32]$buf[$off] -shl 24) -bor ([uint32]$buf[$off+1] -shl 16) -bor ([uint32]$buf[$off+2] -shl 8) -bor [uint32]$buf[$off+3]
}

function Write-UInt32BE([byte[]]$buf, [int]$off, [uint32]$val) {
    $buf[$off]   = [byte](($val -shr 24) -band 0xFF)
    $buf[$off+1] = [byte](($val -shr 16) -band 0xFF)
    $buf[$off+2] = [byte](($val -shr 8) -band 0xFF)
    $buf[$off+3] = [byte]($val -band 0xFF)
}

if ([string]::IsNullOrWhiteSpace($ExePath)) {
    $kitRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    $v140 = Join-Path $kitRoot "stadiacast\stadiacast-1.4.0-windows-x86_64\stadiacast.exe"
    $v120 = Join-Path $kitRoot "stadiacast\stadiacast-1.2.0-windows-x86_64\stadiacast.exe"
    $ExePath = if (Test-Path -LiteralPath $v140) { $v140 } else { $v120 }
}

if (-not (Test-Path -LiteralPath $ExePath)) {
    throw "stadiacast.exe not found: $ExePath"
}

$ExePath = (Resolve-Path -LiteralPath $ExePath).Path
$OrigPath = "$ExePath.orig"

$running = Get-Process -Name ([System.IO.Path]::GetFileNameWithoutExtension($ExePath)) -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -eq $ExePath }
if ($running) {
    throw "stadiacast.exe is currently running ($($running.Count) processes). Stop it first before patching/restoring."
}

if ($Restore) {
    if (-not (Test-Path -LiteralPath $OrigPath)) {
        throw "Backup not found: $OrigPath"
    }
    Copy-Item -LiteralPath $OrigPath -Destination $ExePath -Force
    Write-Host "Restored original stadiacast.exe from $OrigPath"
    exit 0
}

$patchBytes = [Convert]::FromBase64String($PatchedB64)
$sha = [System.Security.Cryptography.SHA256]::Create()
$actualSha = ([BitConverter]::ToString($sha.ComputeHash($patchBytes)) -replace "-", "").ToLowerInvariant()
if ($actualSha -ne $PatchedSha256) {
    throw "Embedded patch payload checksum mismatch."
}

if (-not (Test-Path -LiteralPath $OrigPath)) {
    Copy-Item -LiteralPath $ExePath -Destination $OrigPath -Force
    Write-Host "Saved original backup: $OrigPath"
} else {
    Write-Host "Using existing original backup: $OrigPath"
}

[byte[]]$exe = [System.IO.File]::ReadAllBytes($OrigPath)
[byte[]]$magic = 0x4D, 0x45, 0x49, 0x0C, 0x0B, 0x0A, 0x0B, 0x0E

$cookieIdx = -1
for ($i = $exe.Length - 88; $i -ge 0; $i--) {
    if ($exe[$i] -eq 0x4D -and $exe[$i+1] -eq 0x45 -and $exe[$i+2] -eq 0x49 -and
        $exe[$i+3] -eq 0x0C -and $exe[$i+4] -eq 0x0B -and $exe[$i+5] -eq 0x0A -and
        $exe[$i+6] -eq 0x0B -and $exe[$i+7] -eq 0x0E) {
        $cookieIdx = $i
        break
    }
}
if ($cookieIdx -lt 0) {
    throw "PyInstaller CArchive cookie not found in $OrigPath"
}

$pkgLen = [int](Read-UInt32BE $exe ($cookieIdx + 8))
$tocOff = [int](Read-UInt32BE $exe ($cookieIdx + 12))
$tocLen = [int](Read-UInt32BE $exe ($cookieIdx + 16))
$pyVer  = [int](Read-UInt32BE $exe ($cookieIdx + 20))
if ($pyVer -ne 313) {
    throw "Expected Python 3.13 frozen stadiacast 1.2.0/1.4.0 (got pyver=$pyVer)."
}

$pkgStart = $cookieIdx + 88 - $pkgLen
$pos = $pkgStart + $tocOff
$end = $pos + $tocLen

$entries = New-Object System.Collections.Generic.List[object]
$foundLauncher = $false

while ($pos -lt $end) {
    $entryLen = [int](Read-UInt32BE $exe $pos)
    $dpos     = [int](Read-UInt32BE $exe ($pos + 4))
    $dlen     = [int](Read-UInt32BE $exe ($pos + 8))
    $ulen     = [int](Read-UInt32BE $exe ($pos + 12))
    $cflag    = $exe[$pos + 16]
    $tflag    = $exe[$pos + 17]

    $nameEnd = $pos + 18
    while ($nameEnd -lt ($pos + $entryLen) -and $exe[$nameEnd] -ne 0) {
        $nameEnd++
    }
    $nameLen = $nameEnd - ($pos + 18)
    $nameBytes = New-Object byte[] $nameLen
    [Array]::Copy($exe, $pos + 18, $nameBytes, 0, $nameLen)
    $nameStr = [System.Text.Encoding]::UTF8.GetString($nameBytes)

    if ($nameStr -eq "launcher") {
        $blob = $patchBytes
        $ulen = $PatchedUlen
        $cflag = [byte]1
        $foundLauncher = $true
    } else {
        $blob = New-Object byte[] $dlen
        if ($dlen -gt 0) {
            [Array]::Copy($exe, $pkgStart + $dpos, $blob, 0, $dlen)
        }
    }

    $entries.Add([PSCustomObject]@{
        NameBytes = $nameBytes
        Blob      = $blob
        Ulen      = $ulen
        Cflag     = $cflag
        Tflag     = $tflag
    })
    $pos += $entryLen
}

if (-not $foundLauncher) {
    throw "launcher entry not found in CArchive."
}

$dataLen = 0
$tocOutLen = 0
foreach ($e in $entries) {
    $dataLen += $e.Blob.Length
    $rawLen = 18 + $e.NameBytes.Length + 1
    $tocOutLen += [int]([Math]::Floor(($rawLen + 15) / 16) * 16)
}

$tmpPath = "$ExePath.tmp"
$outLen = $pkgStart + $dataLen + $tocOutLen + 88
$out = New-Object byte[] $outLen
[Array]::Copy($exe, 0, $out, 0, $pkgStart)

$curData = $pkgStart
$curToc  = $pkgStart + $dataLen
$dposOut = 0

foreach ($e in $entries) {
    $blen = $e.Blob.Length
    if ($blen -gt 0) {
        [Array]::Copy($e.Blob, 0, $out, $curData, $blen)
        $curData += $blen
    }
    $rawLen = 18 + $e.NameBytes.Length + 1
    $entryLen = [int]([Math]::Floor(($rawLen + 15) / 16) * 16)
    Write-UInt32BE $out $curToc ([uint32]$entryLen)
    Write-UInt32BE $out ($curToc + 4) ([uint32]$dposOut)
    Write-UInt32BE $out ($curToc + 8) ([uint32]$blen)
    Write-UInt32BE $out ($curToc + 12) ([uint32]$e.Ulen)
    $out[$curToc + 16] = $e.Cflag
    $out[$curToc + 17] = $e.Tflag
    [Array]::Copy($e.NameBytes, 0, $out, $curToc + 18, $e.NameBytes.Length)
    $curToc += $entryLen
    $dposOut += $blen
}

$newCookieOff = $pkgStart + $dataLen + $tocOutLen
[Array]::Copy($exe, $cookieIdx, $out, $newCookieOff, 88)
$newPkgLen = [uint32]($dataLen + $tocOutLen + 88)
Write-UInt32BE $out ($newCookieOff + 8)  $newPkgLen
Write-UInt32BE $out ($newCookieOff + 12) ([uint32]$dataLen)
Write-UInt32BE $out ($newCookieOff + 16) ([uint32]$tocOutLen)

[System.IO.File]::WriteAllBytes($tmpPath, $out)
Move-Item -LiteralPath $tmpPath -Destination $ExePath -Force
Write-Host "Patched $ExePath successfully (125 Hz focus_game + Capture/Assistant patch enabled)."
