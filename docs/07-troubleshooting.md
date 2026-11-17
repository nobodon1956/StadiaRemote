# 07 - Troubleshooting

Most problems are diagnosed from the receiver log, not by guessing.
Logs are in `<project>\logs\autostart\server.jsonl` (one JSON object per line).

---

## First, split the problem into layers

Check these in order:

```cmd
ping <controller-ip>
```

- If the ping fails, it is a network/Wi-Fi problem.
- If the ping works, the network is fine and the issue is in the session layer.

Then check the receiver:

```
GET http://<pc-ip>/_status
```

- No response: receiver is not running. Restart it.
- `dtls-connected` and `gamepad_created` present: the controller is connected. If a game
  still sees nothing, the problem is the virtual gamepad or the game, not the link.

---

## Controller will not connect

| Symptom | Cause / Fix |
|---|---|
| No `tcp_accept` from controller in log | DNS override not reaching the controller. Check the MAC in the router rule; power-cycle the controller so it renews its DHCP lease. |
| `tls_alert UNKNOWN_CA` | A self-signed certificate is being used. Use the built-in credential (the default). |
| White light steady, no `StartGame` | Firewall blocking UDP 40000+. Allow the ports in `05-receiver.md`. |
| Controller powers off after a few seconds | `--preset live` was removed. Put it back. |
| `STATE -> 0x4f` during Wi-Fi pairing | AP is not WPA2-Personal/AES, or PMF is enabled. Fix the AP settings. |
| `scan` finds nothing during pairing | Controller not in pairing mode (orange blinking light), Bluetooth off on the PC, or controller too far away. |

---

## Controller disconnects by itself

Look for these lines in the log:

```
rpc_in ... "variant": "disconnect"
dtls_closed_by_peer
boot_state_reset, reason: "the controller closed the link"
```

If a `press` of the Stadia button appears a few seconds before the disconnect,
the cause is a **long press of the Stadia button**. The controller treats it as a
power-off/disconnect command. This is firmware behaviour; the receiver has no setting
to disable it. Just avoid holding that button.

Two real disconnects were confirmed this way: 12:11:14 Stadia pressed -> 12:11:18
disconnect, and 14:07:10 pressed -> 14:07:14 disconnect.

If there is no Stadia press, check:

- Wi-Fi signal quality and interference.
- Whether the receiver restarted (`ready` event) just before the disconnect.
- Whether the controller's battery is low.

After a disconnect the controller does not always reconnect by itself. Short-press the
Stadia button to trigger a new handshake.

---

## No sound from the headset

1. Check `http://<pc-ip>/_audio`. If `playing` is false, click start or restart the
   receiver.
2. If a hot-start attempt returns `ffmpeg not found on PATH (a build with libopus is
   required)`, install ffmpeg with libopus into `<project>\tools\ffmpeg\bin` and
   restart the receiver.
3. Confirm `--audio-source system` is in the receiver command line.
4. If the source is a test tone but not system audio, the source is fixed at startup;
   a runtime API cannot switch it. Restart with `--audio-source system`.
5. Remember the microphone is not supported at all.

---

## SNTP error in the log

On Windows the SNTP helper can exit with an error because `w32time` occupies UDP 123.
**Ignore it.** A fully working session has been observed with zero SNTP queries from
the controller; it uses HTTP Date headers for time.

---

## Backup fails

- `Could not find stadia controller`: wrong cable/port, or missing WinUSB driver.
  Try another data cable and another USB port.
- `Access denied`: driver permission issue. Install WinUSB with Zadig for the device.
- Dumped file contains repeating address values: the restricted flashloader rejected
  the bulk read. Use the patched `stadiatool.py` from `04-tools-and-backup.md`
  (`setupFlashRegs` plus `IPRXFCR` rewrite before each read).
- Dump interrupted: delete the partial file, re-enter flashloader mode, and start again.

---

## Flasher button does nothing

The `Revert to Wi-Fi mode (Dogfood only)` button requires the fixed `app.js` included
with this kit. If it still does nothing, hard-refresh Chrome with Ctrl+Shift+R and
make sure you are using Chrome (WebHID is required).

---

## How to ask for help effectively

Include all of these:

- The exact command and its full error output.
- The controller LED state (color, steady or blinking).
- Which document and which step you were on.
- The relevant lines from `server.jsonl`.
- Your firmware build number.

Do not repeatedly retry or press random button combinations while waiting for help.
