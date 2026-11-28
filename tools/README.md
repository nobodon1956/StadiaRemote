# tools/

This folder holds the third-party tools the kit depends on. They are **not** bundled
here (except the flasher page) because of size and licensing. Download them while
online, place them as shown below, and the whole kit works offline afterwards.

See `../docs/08-tools-and-offline.md` for download links and checksums.

## Expected layout

```
tools/
├── README.md              <- this file
├── stadiacast/            <- stadiacast-provision.exe (+ the receiver lives in ../stadiacast/)
├── stadiacast-125hz/      <- zero-dependency 125 Hz (8 ms) patch for stadiacast.exe 1.2.0
├── stadiatool/
│   └── stadiatool/
│       ├── stadiatool.py  <- patched read path
│       ├── stadia_hid.py  <- hidapi backend
│       ├── hid_pyusb.py   <- original backend, kept for reference
│       ├── flashloader.py
│       ├── sdp.py
│       └── data/
├── flasher/
│   └── src/               <- WebHID flasher with the fixed app.js
└── ffmpeg/
    └── bin/
        ├── ffmpeg.exe     <- build with libopus
        └── ffprobe.exe
```

## stadiacast

- https://github.com/jkfran/stadiacast
- MIT, jkfran and contributors.
- This project is Forked from stadiacast. Without it none of this exists.

## stadiacast-125hz

- Zero-dependency patcher (`patch-stadiacast.bat` / `patch-stadiacast.ps1`) + auditable
  source (`launcher_125hz.py`) for `stadiacast.exe` 1.2.0.
- Sends `DisplayToController #4` (`focus_game`) after `StartGame`, deduplicates history
  replays, and preserves sparse axes, raising Wi-Fi polling from 20 Hz to **125 Hz (8 ms)**.

## stadiatool

- https://github.com/GaryOderNichts/stadiatool
- MIT, GaryOderNichts.
- Requires Python 3.11+ with `pyusb` and `libusb-package`.

## flasher

- Community 0x WebHID page. The included `app.js` adds the Dogfood button and fixes
  its click handler.

## ffmpeg

- https://ffmpeg.org/ - gyan.dev essentials build with libopus.
- Only needed for headset audio.
