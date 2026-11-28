# 06 - Audio and Daily Use

---

## Controller microphone & headset audio (Wi-Fi mode)

`stadiacast 1.4.0` supports both **controller microphone input** (`--mic`, `--mic-device`) and **3.5 mm headset audio output** (`--audio-source system`).

### Microphone setup (VB-CABLE + ffmpeg)

1. Install **VB-CABLE Virtual Audio Device** (`drivers\VBCABLE\VBCABLE_Setup_x64.exe`).
2. Put **ffmpeg** (essentials build with `libopus`, e.g. 9.1) in `<project>\tools\ffmpeg\bin` and next to `stadiacast.exe`.
3. In Windows Sound settings, keep your physical speakers/monitor as the **default output** (do **not** leave VB-Audio as default output) and set **`CABLE Output (VB-Audio Virtual Cable)`** as the **default input (microphone)**.
4. Pass `--mic off --mic-device "<VB-Audio speaker endpoint>"` (already configured in `scripts/start-stadiaremote-启动.vbs`).
5. On the controller: starts muted (solid white LED). Hold **Assistant** for **0.6 s** to toggle the microphone on (slow pulsing white LED) or off again.

### Extra buttons on Windows (Capture & Assistant)

- **Capture** short press (< 0.6 s): screenshot (`Win + PrtScn`) → `%USERPROFILE%\Pictures\Screenshots`
- **Capture** long press (≥ 0.6 s): toggle Xbox Game Bar screen recording (`Win + Alt + R`) → `%USERPROFILE%\Videos\Captures` (requires a focused game or app window)
- **Assistant** long press (≥ 0.6 s): toggles the controller microphone (or triggers `Win + H` voice typing when no mic device is enabled)

### Headset audio (optional)

### Enable it

1. Install an **ffmpeg build with libopus**. A portable essentials build works.
2. Put `ffmpeg.exe` and `ffprobe.exe` in `<project>\tools\ffmpeg\bin`.
3. Make sure the generated `start-receiver.vbs` includes `--audio-source system`
   (checkbox in the configurator).
4. Restart the receiver.

Check the status:

```
GET http://<pc-ip>/_audio
```

You should see `"playing": true` and a source description.

`/_status` also reports the stream under `playback`.

### Why both the PC speakers and the headset make sound

`--audio-source system` captures a **loopback copy** of whatever the PC is playing.
It does not mute or take over the speakers. The PC keeps playing normally and the
receiver sends a copy to the controller. That is expected behaviour, not a bug.

If you want only the headset to make sound, an advanced option is to add
`--audio-follow-volume off` to the receiver command and mute the PC system volume.
The headset then keeps its own volume. This kit does not enable it by default.

### Test tone

To prove the audio path without configuring system audio:

```
stadiacast.exe --audio-source tone ...
```

A 440 Hz tone confirms the link works.

---

## Wired mode (USB)

After flashing to a retail Wi-Fi firmware, the controller **still works over USB**.
Plug in a data cable and Windows sees a standard Xbox-compatible gamepad. No receiver,
no Wi-Fi and no driver setup beyond the normal HID driver are needed.

With a headset plugged in, wired mode behaves differently:

- Windows detects the controller as a **USB sound card** and switches the default
  audio output to it.
- The PC speakers go silent and only the headset makes sound.

This is normal Windows audio-device switching. In Wi-Fi mode the behaviour is different
because stadiacast is copying the speaker output rather than replacing it.

Microphone: still not available.

---

## Everyday operation

A typical session:

1. Receiver starts automatically at logon (if you installed the autostart script),
   or double-click `start-receiver.vbs`.
2. Short-press the Stadia button to connect. Wait for a steady white light.
3. Play. The controller is a normal Xbox 360 gamepad to Windows and to any streaming
   app (Sunshine/Moonlight, RustDesk, etc.).
4. Long-press the Stadia button about 4 seconds to power off when done.

Important: **do not hold the Stadia button down.** A long press powers the controller off
and disconnects the session. Two confirmed disconnects were caused by someone holding
the Stadia button for about four seconds. Wake/connect with a short press only.

---

## Battery and sleep

The controller has a 2000 mAh battery, much larger than typical gamepads. The firmware
powers the controller down after roughly six minutes of inactivity. That is normal
power saving - just wake it again.

Keep the controller charged before a long session.

---

## Latency notes

With the included `tools/stadiacast-125hz` patch (`focus_game` + `InputDecoder` dedup/sparse-axis
fixes), the controller runs in native game mode over Wi-Fi at **125 Hz (8.0 ms interval)** —
matching USB wired mode (compared to **20 Hz / 50 ms** on unpatched `stadiacast 1.2.0`).

In practice, the limiting factor for streaming feel is usually the **video decode and
display path** on the client device, not the controller. A low-powered old tablet or
TV can add far more lag than the controller ever does.
