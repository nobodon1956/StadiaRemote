# NOTICE - Third-Party Components

This kit is **Forked from [stadiacast](https://github.com/jkfran/stadiacast)** and
bundles/references several open-source projects. All credits and licenses below belong
to their respective authors.

## stadiacast (core receiver)

- Repository: https://github.com/jkfran/stadiacast
- Authors: Francisco Jimenez Cabrera and the Stadiacast contributors
- License: MIT License
- Version used: 1.2.0 Windows x86_64
- Copyright (c) 2026 Francisco Jimenez Cabrera and the Stadiacast contributors
- Role: LAN-side receiver that impersonates the retired Stadia cloud, turns controller
  input into a virtual Xbox 360 gamepad, and streams audio to the headset jack.

> The original MIT notice is reproduced here:
>
> Permission is hereby granted, free of charge, to any person obtaining a copy of this
> software and associated documentation files (the "Software"), to deal in the Software
> without restriction, including without limitation the rights to use, copy, modify,
> merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
> permit persons to whom the Software is furnished to do so, subject to the following
> conditions: the above copyright notice and this permission notice shall be included
> in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS",
> WITHOUT WARRANTY OF ANY KIND.

## stadiatool (backup / flash utility)

- Repository: https://github.com/GaryOderNichts/stadiatool
- Author: GaryOderNichts
- License: MIT License
- Copyright (c) 2023 GaryOderNichts
- Role: USB-based firmware dump, flashloader loading and soft reset.
- Modifications in this kit: patched read path for the restricted flashloader
  (`setupFlashRegs`, `IPRXFCR` rewrite before each read), hidapi backend to avoid
  Windows HID conflicts.

## 0x-dogfood flasher (WebHID web flasher)

- Source: community 0x flashing page, localised in this kit
- Role: writes 316382 through Chrome WebHID.
- Modification in this kit: added the `Revert to Wi-Fi mode (Dogfood only)` button and
  fixed the argument-count bug that made it unclickable.

## ffmpeg (optional, headset audio)

- Repository: https://ffmpeg.org/
- License: LGPL or GPL depending on build
- Build used: gyan.dev essentials, libopus enabled
- Role: Opus encoder for `--audio-source system`.

## Google firmware image

- File: `ota.316382.stable-channel.gotham-pvt-b.da986392604309ea67eab5fa84f747e955f2875c.bin`
- Origin: Google official OTA package
- Role: restoring an own device to a working retail firmware.
- Note: the binary ships with the bundled WebHID flasher under
  `tools/flasher/src/data/` so it works out of the box; the standalone `firmware/`
  folder contains checksums only. Evaluate applicable terms before any redistribution.

---

The documentation, configurator and glue scripts added by this kit are MIT licensed
(see `LICENSE`). Special thanks again to jkfran - this project is Forked from stadiacast.
