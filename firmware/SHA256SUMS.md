# Firmware checksums

File: `ota.316382.stable-channel.gotham-pvt-b.da986392604309ea67eab5fa84f747e955f2875c.bin`

| Algorithm | Expected value |
|---|---|
| SHA1 | `da986392604309ea67eab5fa84f747e955f2875c` |
| SHA256 | `4545a7bcc889b911f19409ae363586806922c1423ca519ccdb44c595c1d9c261` |
| Size | `4163944` bytes |

Verify on Windows:

```cmd
certutil -hashfile ota.316382...bin SHA1
certutil -hashfile ota.316382...bin SHA256
```

Verify on Linux/macOS:

```sh
shasum -a 1 ota.316382*.bin
shasum -a 256 ota.316382*.bin
```

Do not flash unless both hashes match.

This is a Google OTA image. It is shipped inside the bundled WebHID flasher at
`../tools/flasher/src/data/` so the flasher works out of the box; the standalone
`firmware/` folder holds checksums only. If you need a separate copy, obtain it from a
community source and verify the hashes above before use. Use it only for restoring your
own controller. See `../NOTICE.md` for attribution and legal notes.
