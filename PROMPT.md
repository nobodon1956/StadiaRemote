# PROMPT.md - For AI Assistants

> Copy the text in the section "The prompt" below into a coding agent
> (Claude Code, Codex, Gemini CLI, or similar) with this repository folder open.
> The user does not need to understand the technical details. You do the work,
> ask the right questions, and use the files in this repository.

---

## Ground rules for the assistant

Read these before doing anything.

1. **This kit is Windows-only.** The generated scripts (`.vbs`, `.bat`), driver and setup
   steps target Windows. If the user is on macOS or Linux, stop and point them to the
   original stadiacast project, which has builds for those platforms.
2. **Use this repository's files.** Do not write your own scripts from scratch.
   The safety rules are embedded in `docs/` and in the generated scripts.
3. **Back up before flashing. Always.** If the firmware is 169429 and the backup is not
   verified, do not proceed to the flash step under any circumstances.
4. **Ask before acting on hardware.** Never start a flash while the user is unclear or
   unprepared. Confirm each stage out loud.
5. **Do not expose private data.** WiFi passwords, router admin passwords and serial
   numbers must not be written into files that will be shared publicly.
6. **Guide me through downloading and verifying tools.** This kit is intentionally small
   and does NOT bundle the large installers (receiver, driver, Python, ffmpeg). Use
   `docs/08-tools-and-offline.md` to tell me exactly what to download, from which official
   source, and to verify each file with the checksum commands before I use it. The 316382 firmware IS bundled in this kit under tools/flasher/src/data/ - use that bundled
file and verify its hashes against firmware/SHA256SUMS.md before flashing. Never skip firmware
checksum verification, and never substitute a firmware file downloaded from an unknown source.
7. **Be honest about limits.** The controller microphone is not supported by stadiacast.
   Do not promise it will work.
8. **Never confuse the Bluetooth address with the Wi-Fi MAC.** The address shown by
   `stadiacast-provision scan` is a BLE address used only to deliver Wi-Fi credentials.
   The MAC used in the dnsmasq rule is a different value that appears in the router's DHCP
   client list only AFTER the controller has joined Wi-Fi. See `docs/10-find-the-controller-mac.md`.
   Pair first, then read the MAC, then generate the DNS rule. If the user does not know the
   MAC, this is expected - guide them, do not let them guess.
9. **Never run long-running or resident scripts inside your own tool calls.** backup-169429.bat
runs for about 4.5 hours and start-flasher.bat / the receiver stay resident; agent shell tools have
timeouts of minutes and will kill the process, wasting the backup or breaking USB communication.
The user must launch such scripts themselves in a separate terminal window; you may only monitor
progress by reading the log files (for example backup-progress.log).
10. **Backup verification is a machine-checked gate, not a conversation.** Before any flash step,
you must yourself read the two backup files' sizes (262144 and 8126464 bytes) and the generated
backup-169429-SHA256.txt, and state them back to the user. A user saying "it looks done" is NOT
verification.
11. **Two controllers are supported; never overwrite the first one's config.** One receiver serves up to 8 controllers (c0, c1, ...). Each controller needs its OWN MAC-scoped dnsmasq stanza — when adding a second controller, append its rule, never replace the first controller's. Controller Wi-Fi MACs may start with d4:f5:47 or f0:ef:86; accept both.
---

## The prompt

```text
You are helping me set up a Google Stadia controller as a Wi-Fi gamepad for my Windows PC.
This folder is a kit built on top of jkfran's stadiacast project.

Follow these rules:
- Read README.md first, then only the docs I need.
- Use the scripts and configurator in this repository. Do not invent your own.
- Never flash firmware before the 169429 backup is verified.
- Ask me before each action that changes my controller or my router.
- Tell me plainly what to press and what to look for (LED color, rumble, log lines).
- Keep my WiFi password and router password out of any file I might share.

Start by asking me these questions, one group at a time:

1. What Windows PC are you using, and what is its LAN IP address?
   (If you don't know, guide me to find it with ipconfig.)
2. What is your router's LAN IP address?
3. Do you know your controller's firmware number? If not, we will find it together
   using docs/01-know-your-firmware.md - walk me through Method A.
4. Do you have a USB data cable, and is Bluetooth available on the PC?
   (Do NOT ask for the controller MAC here - it does not exist yet. It is read later.)

Then set up the tools BEFORE touching hardware:
  * Open docs/08-tools-and-offline.md. This kit does NOT bundle the big installers, so
    guide me to download them one at a time from the official links, into the folders the
    doc names. After EACH download, give me the checksum command and have me paste the
    output; confirm it matches before we continue.
  * Only these apply to my case - skip the rest:
      - Always: stadiacast 1.2.0 (receiver + ViGEmBus driver) and Chrome with WebHID.
      - Only for 169429: Python 3.11+ with pyusb + libusb-package, stadiatool (and copy
        the patched stadiatool.py / stadia_hid.py from this kit into it), and the flasher.
      - Only if I want headset audio: ffmpeg with libopus.
  * The 316382 firmware is bundled in this repo under tools/flasher/src/data/. Use that file; verify
its SHA1 and SHA256 against firmware/SHA256SUMS.md and docs/08 before flashing. Do not
download a replacement firmware from a community source.

Then branch:

CASE A - firmware is 169429:
  * Open docs/02-upgrade-from-169429.md and follow it strictly in order.
  * Explain that the backup takes about 4.5 hours and why it cannot be skipped.
  * Have me run the stadiatool info command first and paste the output.
  * Generate my backup script with configurator.html, or fill in the placeholders
    in scripts/backup-169429.bat.example together.
  * Only after I confirm both backup files exist with the correct sizes AND hashes
    were copied to a USB stick, move on to flashing.
  * Walk me through SDP mode step by step. After each key combination, ask me what
    the LED is doing before continuing.
  * Verify 316382's SHA1 before flashing.
  * Start the local flasher, have me open Chrome, and guide me to click
    "Revert to Wi-Fi mode (Dogfood only)". If it does nothing, tell me to hard-refresh.
  * After flashing, verify with stadiatool info that the build is 316382.

CASE B - firmware is 316382 or 282115:
  * Open docs/03-retail-firmware.md. Skip all backup and flash steps.
  * Go straight to Wi-Fi pairing.

FOR BOTH CASES:
  * Open configurator.html with me. The page has NO field for the controller MAC or IP -
    I never type those. Fill in only PC IP, router IP, WiFi SSID and paths (never the WiFi password — it is typed only into the provision tool's own prompt),
    then generate. Tell me this first pass is for the pairing/detection scripts.
  * Guide me through Wi-Fi pairing with provision-wifi.bat. Remind me that Bluetooth is
    used only to deliver WiFi credentials; the gamepad itself runs over WiFi. Explain that
    the Bluetooth address from `scan` is NOT the WiFi MAC.
  * Then open docs/10-find-the-controller-mac.md. Have me run the generated
    find-controller-mac.bat on the PC. It scans the LAN for Google-OUI (d4-f5-47)
    devices and writes detected-values.txt containing the REAL WiFi MAC and IP.
    I do NOT need to give you my router password. Only if that scan fails, guide me to
    my router's DHCP client list (hostname starting with Stadia-) - login done by me,
    never shared with you. Do NOT accept the BLE address as the MAC.
  * Read detected-values.txt yourself if you have terminal access, or have me load that
    file in configurator.html (Load detected-values.txt). Either way the MAC and IP are
    applied without me typing them. Click Generate again - now every script, including
    the dnsmasq rule, has the detected values baked in.
  * Open docs/04-router-and-dns.md and help me install the regenerated dnsmasq rule
    on the correct router. Stress that the rule must apply only to the controller MAC.
  * Open docs/05-receiver.md. Check the ViGEmBus driver is installed, then start the
    receiver with the generated script.
  * Ask me to short-press the Stadia button (~1 second, release at first rumble).
    Warn me NOT to hold it down, because a long press powers the controller off.
  * Verify success with /_status and joy.cpl.
  * Offer headset audio setup from docs/06-audio-and-daily-use.md if I want it.
  * Offer to install the autostart script into my Startup folder.

If anything fails:
  * Open docs/07-troubleshooting.md and diagnose from the log, not by guessing.
  * Ask me for the exact error text, the LED state and the relevant log lines.
  * Never tell me to repeatedly retry or press random button combinations.

Finally, remind me that this project is Forked from stadiacast and thank the original
author. Also tell me this kit is a personal, one-off project that is not maintained and
will not be updated - for ongoing support, new features, or Windows/macOS/Linux versions,
I should follow the original stadiacast project.
```

---

## What a good assistant session looks like

- It asks about your firmware before suggesting any download or script.
- It walks you through downloading each tool from its official source and verifies
  checksums before use - it does not assume the big installers are already present.
- It refuses to flash until the backup is verified.
- It tells you the expected LED state before asking you to press buttons.
- It uses `configurator.html` instead of hand-editing IP addresses into scripts.
- It never asks the user to type the controller MAC or IP: the configurator has no fields
  for them. It runs find-controller-mac.bat, reads detected-values.txt, and applies the
  values through the page - never the Bluetooth scan, never shared router/WiFi passwords.
- It scopes the DNS rule to the controller MAC and checks the right router.
- It explains that the receiver runs as four processes and that the SNTP error is harmless.
- It never claims the microphone will work.

---

## If the assistant has no terminal access

Some assistants can only read files and answer questions. That still works:

1. Ask it to read the specific doc from this folder for each step.
2. Run the commands yourself and paste the output back.
3. Open `configurator.html` locally and download the generated scripts yourself.

The assistant's value is in ordering the steps, interpreting logs and catching mistakes -
not in running commands for you.

---

## Supporting material for the assistant

| File | Use |
|---|---|
| `README.md` | Overview and routing table |
| `docs/01-know-your-firmware.md` | Firmware identification |
| `docs/02-upgrade-from-169429.md` | Backup and flash procedure |
| `docs/03-retail-firmware.md` | Path for already-flashed controllers |
| `docs/04-router-and-dns.md` | DNS override details |
| `docs/05-receiver.md` | Receiver start/restart/autostart |
| `docs/06-audio-and-daily-use.md` | Audio, wired mode, battery, latency |
| `docs/07-troubleshooting.md` | Log diagnosis |
| `docs/08-tools-and-offline.md` | Official download links, checksums, AI-guided install |
| `docs/09-technical-background.md` | Why 169429 hangs (background only) |
| `docs/10-find-the-controller-mac.md` | Get the real WiFi MAC (not the BLE address) |
| `configurator.html` | Generates all IP-specific files offline |
