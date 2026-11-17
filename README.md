# Stadia WiFi Kit

**Turn a factory-firmware Google Stadia controller into a Wi-Fi gamepad for your PC.**

> **Platform: Windows only.** This kit's generated scripts (`.vbs`, `.bat`), driver and
> setup steps are written specifically for Windows. It does not support macOS or Linux.

> **Forked from [stadiacast](https://github.com/jkfran/stadiacast)** by jkfran (MIT).
> Huge thanks to the original author and contributors - without their work this kit would not exist.
> This repository is a documentation-and-tooling kit built on top of that project.

> **Project status:** This is a personal, one-off kit. It is **not maintained** and will
> **not receive updates** - it only solves the specific problems I ran into. If you need
> ongoing support, newer features, or builds for other platforms, please follow the
> original **[stadiacast](https://github.com/jkfran/stadiacast)** project, which ships
> versions for **Windows, macOS and Linux**. Thanks again to the original author for
> their work.

---

## Start here

Pick the line that matches you:

| Your situation | Go to |
|---|---|
| I do not know my firmware version | `docs/01-know-your-firmware.md` |
| I have **169429** (factory build) | `docs/02-upgrade-from-169429.md` - back up, then flash |
| I already have **316382** or **282115** | `docs/03-retail-firmware.md` - skip flashing |
| I just want the scripts and IPs configured | Open **`configurator.html`** in a browser |
| I don't know my controller's WiFi MAC address | `docs/10-find-the-controller-mac.md` |
| I want an AI assistant to guide me | Read **`PROMPT.md`** below |

**Small by design.** This kit holds the documentation, the config generator, scripts and
the 316382 firmware - not the large third-party installers. An AI assistant (or
`docs/08-tools-and-offline.md` if you are on your own) walks you through downloading each
tool from its official source and verifying it. The configurator itself makes no network
requests and works in any browser.

---

## What this solves

Stadia shut down in 2023 and the official controller-unpairing web tool is gone.
A brand-new controller still has factory firmware **169429**, a factory trial build that
hangs in a setup routine and never connects to anything.

stadiacast lets a PC pretend to be the old Stadia cloud on your LAN, so the controller
works over its original Wi-Fi protocol as a virtual Xbox 360 controller. The catch:
169429 must be replaced with retail firmware **316382** first.

This kit documents the complete, tested path:

1. Identify your firmware.
2. Back up 169429 safely (two-region dump, ~4.5 h).
3. Flash 316382 with the WebHID flasher and the Dogfood button.
4. Pair the controller to Wi-Fi.
5. Set a router DNS rule for the controller only.
6. Run, restart and auto-start the receiver.
7. Get headset audio working.
8. Diagnose disconnects and other failures from the log.

---

## Three things to know up front

1. **Never flash before the backup is verified.** The backup is the only way back.
2. **Long-pressing the Stadia button disconnects the controller.** Wake it with a short press.
3. **The microphone does not work.** stadiacast supports one-way audio (PC -> headset) only.
4. **You never type the controller MAC or IP.** They are auto-detected after pairing by
   `find-controller-mac.bat` and loaded back into the configurator - see `docs/10`. The
   Bluetooth address is not the WiFi MAC.

---

## Using the configurator

Open `configurator.html` in any browser, fill in:

- PC IP address
- Router IP address
- Wi-Fi SSID and password
- Project folder and Python path

You do **not** enter the controller's IP or MAC - there are no fields for them. After
pairing, run the generated `find-controller-mac.bat`; it detects both values and writes
`detected-values.txt`. Load that file back into the page (or let your AI assistant apply
the values), then click **Generate** again. Full walkthrough: `docs/10`.

Click **Generate everything**. It produces, offline:

- `start-receiver.vbs`
- `restart-receiver.vbs`
- `autostart-receiver.vbs`
- `dnsmasq-stadia.conf`
- `provision-wifi.bat`
- `find-controller-mac.bat` (discovers the real WiFi MAC from the PC - no router login)
- `start-flasher.bat`
- `backup-169429.bat`
- `MY-SETUP.txt` with your personal checklist

You can copy each file or download them all as a ZIP. Nothing is uploaded; the page has
no network calls at all.

---

## Using an AI assistant

This project follows the pattern made popular by
[cleanyourtv](https://github.com/Gathin23/cleanyourtv): give the repository to a coding
assistant and let it drive the process with `PROMPT.md`.

See **`PROMPT.md`** for the full instruction set. In short:

1. Clone or download this repository.
2. Open the folder in your AI agent (Claude Code, Codex, Gemini CLI, etc.).
3. Paste `PROMPT.md` to the assistant and answer its questions.
4. The assistant identifies your firmware, guides you to download and verify each tool
   from its official source, generates the scripts with the configurator, and walks you
   through backup, flash, router and receiver step by step.

The assistant must use the scripts in this repository rather than inventing its own,
because the safety rules (backup before flash, MAC-scoped DNS, no long Stadia press)
live here.

---

## Documentation index

| File | Subject |
|---|---|
| `PROMPT.md` | Instructions for an AI agent helping a user |
| `docs/01-know-your-firmware.md` | Identify 169429 vs retail |
| `docs/02-upgrade-from-169429.md` | Backup + flash, with safety rules |
| `docs/03-retail-firmware.md` | Using an already-flashed controller |
| `docs/04-router-and-dns.md` | MAC-scoped DNS override |
| `docs/05-receiver.md` | Start, restart, autostart, driver |
| `docs/06-audio-and-daily-use.md` | Headset audio, wired mode, battery, latency |
| `docs/07-troubleshooting.md` | Log-driven diagnosis of common failures |
| `docs/08-tools-and-offline.md` | Official download links, checksums, AI-guided install |
| `docs/09-technical-background.md` | Why 169429 hangs, full string analysis |
| `docs/10-find-the-controller-mac.md` | Find the real WiFi MAC (not the Bluetooth address) |

---

## Verified results

| Item | Result |
|---|---|
| Factory firmware | 169429 (`GothamFsi_b_img`) - hangs in setup, cannot connect |
| Flashed firmware | 316382 (`GothamYeti_b_img`) - connects successfully |
| Receiver | stadiacast 1.2.0, `--preset live --gamepad vigem` |
| Connection | Wi-Fi (native controller protocol), not Bluetooth |
| Headset | 3.5 mm playback works; microphone unsupported |
| Wired mode | Still works after flashing |
| Input latency | p50 about 16 ms; usual bottleneck is video decode/display |

---

## Credits and license

- **Forked from [stadiacast](https://github.com/jkfran/stadiacast)** - jkfran and contributors, MIT.
- **stadiatool** - GaryOderNichts, MIT.
- **0x-dogfood flasher** - community WebHID tool.
- **ffmpeg** - ffmpeg.org, LGPL/GPL depending on build.

See `NOTICE.md` for details. This kit's own files are MIT licensed (`LICENSE`).

**Legal:** Flashing carries risk. Use at your own responsibility. The firmware image is a
Google OTA package intended here for restoring your own device. No warranty is provided.
