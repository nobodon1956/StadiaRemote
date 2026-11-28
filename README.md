# StadiaRemote

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

## What's New in StadiaRemote v1.4.0 (Based on stadiacast 1.4.0)

1. **20 Hz → 125 Hz Polling Rate & 50 ms → 8 ms Latency Upgrade**
   - Stock `stadiacast` sends `DisplayToController #8` (`StartGame`) when the controller connects, but never sends `DisplayToController #4` (`focus_game`), leaving the firmware in `FOCUS_MENU` (`20 Hz / 50 ms`).
   - `tools/stadiacast-125hz` patches the launcher at runtime to send `focus_game` once `StartGame` succeeds (`code == 0`), switching the controller firmware to `FOCUS_GAME` (`125 Hz / 8 ms` over the game UDP link), while deduplicating replayed history frames (`t_us`), preserving sparse `GamepadMessage_V2` axes via `HasField()`, and prioritizing 125 Hz game-link input on ViGEm.
   - Verified at **~125 Hz / ~8 ms** in **ControllerMeta**.

2. **Microphone Support (VB-CABLE + ffmpeg)**
   - Uses **VB-CABLE** and portable **ffmpeg** (`libopus`) to route the controller microphone to Windows as **`CABLE Output (VB-Audio Virtual Cable)`**.
   - **Default off on connect**: Starts with `--mic off` (solid white LED).
   - **Assistant button (0.6 s hold)**: Hold **Assistant** for **0.6 s** to turn the microphone on (slow pulsing white LED); hold **0.6 s** again to turn it off (solid white LED). Short presses (< 0.6 s) are ignored to avoid accidental activation.
   - **Usage tip**: Set **`CABLE Output (VB-Audio Virtual Cable)`** as the default Windows input (microphone) device, and keep your physical speakers/monitor as the default Windows output device (do **not** set VB-Audio as the default output).

3. **Capture Button Restored (Screenshot & Screen Recording)**
   - **Short press (< 0.6 s)**: Takes a screenshot (`Win + PrtScn`), saved to `%USERPROFILE%\Pictures\Screenshots`.
   - **Long press (≥ 0.6 s)**: Toggles screen recording (`Win + Alt + R`), saved to `%USERPROFILE%\Videos\Captures`.
   - **Usage tip**: Xbox Game Bar recording only works when a game or application window is focused (Windows blocks recording on the bare desktop).

4. **Multi-Controller & Automatic IP / Gateway Detection**
   - Refactored the launch scripts to remove hardcoded single-controller `--controller-ip` and static network addresses. Multiple controllers (`c0`, `c1`, ...) connect automatically via `--gamepad vigem`, and the scripts auto-detect the local LAN IP (`--advertise-ip`) and default gateway (`--dns-upstream`) via WMI.

5. **Silent Bilingual One-Click Scripts & Autostart**
   - Rebuilt the scripts in `scripts/` with **bilingual (English / Chinese) filenames, comments, and status dialogs**, running `stadiacast.exe` silently in the background with no console window.
   - **Desktop shortcut**: Places the one-click **Restart** shortcut on the Desktop; **Start** and **Stop** shortcuts live inside `scripts/`.
   - **Logon autostart**: Registers Windows logon autostart with `/silent` (no startup popup dialog).

### Acknowledgements

- Thanks to **jkfran** for the [stadiacast](https://github.com/jkfran/stadiacast) project updates.
- Thanks to **Bilibili 无需多言1221** for the support.


## Why this controller?

Google launched its Stadia cloud-gaming service in November 2019, and with it a controller
unlike any other: a PlayStation-style layout, a 3.5 mm headset jack, a microphone, rumble,
a huge 2000 mAh battery, Bluetooth 4.2 (used **only** to pair Wi-Fi, never to play), and —
unusually — **Wi-Fi, including the 5 GHz band**.

The original idea was that the controller talked to Google's cloud through your home
router, with your inputs showing up on a Google TV. When Stadia shut down in 2023, Google
released a web tool that turned the controller into a plain Bluetooth gamepad (with rumble
broken), and by 2026 even that page was gone. Factory-sealed, never-opened controllers now
sell for about ¥39–50 — the starting point of this whole project.

### How stadiacast brings it back

[stadiacast](https://github.com/jkfran/stadiacast) hijacks the controller's requests to
Google's domains on your router and redirects them to your PC. The PC then impersonates the
old Stadia cloud, so the controller keeps using its original Wi-Fi protocol while your game
sees a standard virtual gamepad.

### Why it is the best fit for LAN streaming

Suppose your PC is in the bedroom and your TV is in the living room:

- **Gamepad connected to the TV:** the TV sits next to the router, whose 2.4 GHz signal
  (and other gear such as Switch controllers) interferes. The path is long — controller →
  TV → stream back to the PC → image back to the TV — so latency stacks up.
- **Gamepad connected to the PC over Bluetooth:** Bluetooth is 2.4 GHz and does not pass
  through walls well. Fine for music, not for a game that needs instant feedback.
- **Gamepad connected over Wi-Fi:** 5 GHz means wide bandwidth, and mesh access points
  cover the whole home. As long as you are inside your Wi-Fi coverage, latency stays low.

This also means **whole-home roaming**: start a game on the living-room TV, then pick up a
tablet and carry the controller to the bathroom — with Bluetooth you would have to re-pair
it to a new device, but a Wi-Fi Stadia controller is already talking to the PC, so nothing
needs to change.

### Advantages at a glance

1. Wi-Fi mode keeps rumble; the Bluetooth-conversion firmware loses it.
2. Wi-Fi bandwidth is ample, so the 3.5 mm headset works (wired audio sounds especially
   good). The microphone does not work with stadiacast.
3. Works with **any** streaming stack — Sunshine + Moonlight, RustDesk, UU Remote, even
   tools with no gamepad mapping — because the gamepad never goes through the streaming
   app at all.
4. Connects on 5 GHz Wi-Fi; with good coverage it stays stable, unlike Bluetooth or
   2.4 GHz dongles that drop out.
5. A 2000 mAh battery — one of the largest ever put in a controller.
6. Wired (USB) play still works after flashing the Wi-Fi firmware.
7. Solid build quality for the price.
8. stadiacast itself supports Windows, macOS and Linux (this kit's scripts are Windows-only).

---

## Buying a controller today

Two production runs exist, told apart by the box label (model + MFG date) — no need to open the box:

| Box model | Made | Out of the box | Path |
| --- | --- | --- | --- |
| GA00303-US | 11/2019 | Factory firmware 169429 | Back up, then flash 316382 (docs/02) |
| GA00827-US | 4/2025 | Bluetooth-mode firmware | Flash back to Wi-Fi firmware 316382 the same way |

Yes, the 4/2025 run is real: Google kept manufacturing controllers years after the Stadia service shut down in 2023, and sealed units ship with the Bluetooth conversion already applied. Both revisions end up on 316382 and work with this kit. If you have the choice, buy the newer (2025) unit — it has spent far less time in storage, so its 2000 mAh battery is usually in much better shape.

Two controllers at once also work: one receiver serves up to 8 controllers (sessions c0, c1, ...), each as its own virtual Xbox 360 pad — verified with two controllers in It Takes Two and Split Fiction. The configurator generates the per-controller dnsmasq rules for two controllers; never overwrite the first controller's rule when adding the second.

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
- Wi-Fi SSID (the password is never entered in the configurator — the provision tool asks for it in its own prompt)
- Project folder and Python path

You do **not** enter the controller's IP or MAC - there are no fields for them. After
pairing, run the generated `find-controller-mac.bat`; it detects both values and writes
`detected-values.txt`. Load that file back into the page (or let your AI assistant apply
the values), then click **Generate** again. Full walkthrough: `docs/10`.

Click **Generate everything**. It produces, offline:

- `start-receiver.vbs`
- `stop-receiver.vbs`
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
| Receiver | stadiacast 1.4.0 + `tools/stadiacast-125hz` patch (`--preset live --gamepad vigem --mic off`) |
| Connection | Wi-Fi (native controller protocol), not Bluetooth |
| Polling rate & latency | **125 Hz / 8.0 ms** over Wi-Fi with `focus_game` patch (unpatched defaults to 20 Hz / 50 ms) |
| Dual controllers | Two at once verified (`c0` + `c1`) with automatic IP/gateway detection |
| Extra buttons | Capture: short press screenshot / 0.6 s hold record; Assistant: 0.6 s hold mic toggle |
| Microphone & headset | Mic supported via VB-CABLE (`CABLE Output`) + ffmpeg; 3.5 mm playback works when system output is not VB-Audio |
| Wired mode | 125 Hz / 8.0 ms over USB after flashing (stop receiver first before switching to wired) |

---

## Credits and license

- **Forked from [stadiacast](https://github.com/jkfran/stadiacast)** - jkfran and contributors, MIT.
- **stadiatool** - GaryOderNichts, MIT.
- **0x-dogfood flasher** - community WebHID tool.
- **ffmpeg** - ffmpeg.org, LGPL/GPL depending on build.
- **VB-CABLE** - VB-Audio Software, Donationware (used for controller microphone routing).
- Special thanks to **jkfran** for the `stadiacast` updates and **Bilibili 无需多言1221** for the support.

See `NOTICE.md` for details. This kit's own files are MIT licensed (`LICENSE`).

**Legal:** Flashing carries risk. Use at your own responsibility. The firmware image is a
Google OTA package intended here for restoring your own device. No warranty is provided.
