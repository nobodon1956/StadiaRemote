# 08 - Tools, Firmware and Downloads

This kit is intentionally **small**. It contains only documentation, the offline config
generator, scripts and checksums. It does **not** bundle large third-party installers
(the receiver, driver, Python, ffmpeg). Instead, your **AI assistant walks you through
downloading each one from its official source and verifying it** before you use it.

If you are following this with an AI assistant, it will handle this page. If you are on
your own, the steps below are written for you too.

---

## Download and verification checklist

The assistant should guide you through these one at a time, in order. After each download,
verify it before moving on. Never skip verification of the firmware.

### 1. stadiacast 1.2.0 (the receiver)

- Official source: `https://github.com/jkfran/stadiacast/releases`
- File: the `stadiacast-1.2.0-windows-x86_64` folder (or matching release asset).
- Extract it, then copy the folder into `<project>\stadiacast\`.
- It contains `stadiacast.exe`, `stadiacast-provision.exe`, and the ViGEmBus driver
  installer under `drivers\`.
- This project is **Forked from stadiacast** by jkfran, MIT licensed.

### 2. ViGEmBus virtual gamepad driver

- Included inside the stadiacast folder above (`drivers\ViGEmBus_*.exe`).
  If it is missing, get it from `https://github.com/ViGEm/ViGEmBus/releases`.
- Install once, as administrator. The receiver uses it to expose an Xbox 360 controller.

### 3. stadiatool (backup / flashloader utility) - only for firmware 169429

- Official source: `https://github.com/GaryOderNichts/stadiatool`
- MIT License, author GaryOderNichts.
- Copy it into `<project>\tools\stadiatool\`.
- Requires Python 3.11+ with `pyusb` and `libusb-package`:

```cmd
python -m pip install pyusb libusb-package
```

Note: this kit provides a **patched** `stadiatool.py`. The original bulk-read command is
refused by the restricted flashloader on this controller. The patch adds register setup
(`setupFlashRegs`) and rewrites the `IPRXFCR` register (0xB8) before every read; without
it the dump returns repeated address values instead of real data. Also included are
`stadia_hid.py` (hidapi backend, to avoid Windows HID conflicts) and the original
pyusb-based file kept as `hid_pyusb.py`. Copy these into the stadiatool folder you
downloaded.

### 4. 0x-dogfood WebHID flasher - only for firmware 169429

- Community flasher page; a localised copy is in this kit under `tools/flasher/`.
- No download needed - just open it with Chrome, which must support WebHID.
- The included `app.js` adds the `Revert to Wi-Fi mode (Dogfood only)` button and fixes
  the argument-count bug that made the button unclickable.

### 5. ffmpeg with libopus - only for headset audio

- Suggested: gyan.dev essentials build, for example `ffmpeg-9.0.2-essentials_build.zip`.
- Source: `https://www.gyan.dev/ffmpeg/builds/`
- Extract `ffmpeg.exe` and `ffprobe.exe` into `<project>\tools\ffmpeg\bin`, and also copy
  them next to `stadiacast.exe` (Windows searches the exe's own folder first).
- Verify libopus is present:

```cmd
ffmpeg -hide_banner -encoders | findstr opus
```

You should see `libopus`. If you do not plan to use headset audio, you can skip ffmpeg
entirely.

### 6. Python 3.11+ - only for firmware 169429

- From `https://www.python.org/downloads/`, or a portable copy.
- Put `python` on PATH, or enter the full path in the configurator's **Python path** field.
- Needed only for stadiatool (backup and flashing).

### 7. Chrome

- Required for the WebHID flasher (step 4). Any recent Chrome with WebHID support works.

---

## Firmware - where it comes from, and how to verify it

There are two ways to get the 316382 firmware, and you do **not** need to hunt for a
separate file in most cases:

1. **Already inside the flasher (easiest).** The local flasher in `tools/flasher/src/data/`
   ships the exact 316382 image it flashes. If you use this kit's flasher, the firmware is
   already there - nothing else to download. This is how the kit is designed to be used.
2. **From the community / original source (if you need a standalone copy).** The image is
   a Google OTA package originally published at
   `https://edgedl.me.gvt1.com/edgedl/googletv-eureka/stable-channel/` (the hash in the
   filename is its SHA1). Community archives preserve it, for example:
   - `https://github.com/AlexDev404/Stadia-Controller-Bluetooth-Firmware-Bin`
   - `https://github.com/vouiren/StadiaFW`

   An AI assistant can locate one of these from the filename and checksums below.

The standalone `firmware/` folder in this repository contains **checksums only**, not the
binary (to avoid redistributing a Google OTA image). Verify whichever copy you use:

Expected file:

```
ota.316382.stable-channel.gotham-pvt-b.da986392604309ea67eab5fa84f747e955f2875c.bin
```

| Algorithm | Value |
|---|---|
| SHA1 | `da986392604309ea67eab5fa84f747e955f2875c` |
| SHA256 | `4545a7bcc889b911f19409ae363586806922c1423ca519ccdb44c595c1d9c261` |
| Size | 4,163,944 bytes |

Place the downloaded file in `firmware/`, then verify before flashing:

```cmd
certutil -hashfile ota.316382...bin SHA1
certutil -hashfile ota.316382...bin SHA256
```

**Do not flash a file whose hashes do not match.** Your AI assistant should check these
values for you. `firmware/SHA256SUMS.md` repeats the checksums for reference.

Note: the factory 169429 backup is also not included - it must be dumped from your own
controller, because it is unique to your device and is your only way back.

---

## What the assistant does for you

With `PROMPT.md`, the assistant will:

1. Tell you which of the tools above apply to your case (169429 vs retail firmware).
2. Give you the exact download link and destination folder, one at a time.
3. Run the checksum commands and confirm each file is genuine.
4. Only then guide you into backup, flashing, pairing and receiver setup.

This keeps the kit small while still letting a beginner complete the whole process with
internet access available.

---

## If you must work offline

The config generator and all documentation work with no internet. The only things that
need a connection are the one-time tool downloads above. If you expect to be offline
later, download these files while you still can and keep them together in the project
folder:

- [ ] stadiacast 1.2.0 folder (includes the receiver and ViGEmBus driver)
- [ ] stadiatool + Python + `pyusb` + `libusb-package`
- [ ] flasher page (`tools/flasher`, already in this kit)
- [ ] 316382 firmware (obtained from a community source + verified against the hashes above)
- [ ] ffmpeg with libopus (for audio)
- [ ] Chrome with WebHID

Note: the controller still needs a working Wi-Fi network with your SSID and password,
which you set during pairing. That is local network access, not internet access.

---

## Legal and attribution

See `NOTICE.md` for third-party authors and licenses.
The receiver is **Forked from stadiacast** by jkfran, MIT licensed.
The firmware is a Google OTA image; use it for restoring your own device.
