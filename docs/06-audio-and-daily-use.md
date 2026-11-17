# 06 - Audio and Daily Use

---

## Headset audio (Wi-Fi mode)

The receiver can send the PC's sound to a 3.5 mm headset plugged into the controller.
It is **one-way only**: PC audio goes to the headset. The controller microphone is
not supported by stadiacast at all, in either Wi-Fi or USB mode.

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

Input is delivered synchronously in the WebRTC data channel; there is no extra queue.
Measured median input latency in this setup was about 16 ms, with PC-to-gateway around
0-1 ms and PC-to-controller around 6 ms average (peak ~82 ms).

In practice, the limiting factor for streaming feel is usually the **video decode and
display path** on the client device, not the controller. A low-powered old tablet or
TV can add far more lag than the controller ever does.
