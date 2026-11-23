# 01 - Know Your Firmware

Before doing anything, find out which firmware your controller is running.
The whole procedure depends on this one answer.

There are two cases:

| Firmware you have | What to do |
|---|---|
| **169429** (factory FSI build) | You must back up, then flash. Go to `02-upgrade-from-169429.md`. |
| **316382** or **282115** (retail build) | No flashing needed. Go straight to `03-retail-firmware.md`. |

---

## Method A: read it over USB (most reliable)

You need:

- A **data** USB-C cable (charge-only cables will not work)
- Python 3.11+ with `pyusb` and `libusb-package` installed
- The `stadiatool` utility (see `tools/README.md`)

Steps:

1. Turn the controller on normally (do not hold any button).
2. Plug the USB-C cable into the PC.
3. Run:

```cmd
cd /d "<your-project>\tools\stadiatool\stadiatool"
python stadiatool.py info
```

Expected output:

```
Found: 18d1:9400 (Google Inc. Stadia Controller)
Controller serial number: XXXXXXXXXXXX
Controller is a pvt device
Current firmware is gotham build 169429
Current battery level: xx%
```

The line **`Current firmware is gotham build <number>`** is your answer.

If you see `Could not find stadia controller` or `Access denied`:

- Try a different USB data cable and a different USB port.
- On Windows you may need to install a WinUSB driver with Zadig for the device.
- Do not force anything. Stop and get help.

---

## Method B: read it from the WebHID flasher page

If you already have the local flasher running (see `04-tools-and-backup.md`):

1. Open Chrome and go to `http://localhost:5000`.
2. Put the controller into flashing mode as the page instructs.
3. The page displays the detected firmware build on screen.

This method also tells you whether the controller is in Wi-Fi mode or Bluetooth mode.

---

## Method C: judge by history (least reliable)

Use this only if you cannot use A or B:

- **Brand new, never paired, bought as "original/unflashed"** from a seller: very likely **169429**.
- **Seller flashed it to Bluetooth** for you: it is a Bluetooth firmware, NOT usable with this kit's Wi-Fi
  receiver. You would need to restore a retail Wi-Fi image first.
- **Already used with stadiacast successfully**: it is 316382 or 282115.

Method C is a guess. Confirm with A or B before flashing anything.

---

## What the number means

| Build | Image name | Branch | Usable with this kit? |
|---|---|---|---|
| 169429 | `GothamFsi_b_img` | FSI (factory trial, built 2019-08) | **No** - must flash |
| 282115 | `GothamYeti_a_img` | Retail (built 2021-11) | Yes |
| 316382 | `GothamYeti_b_img` | Retail (built 2022-09) | **Yes - recommended** |

Why 169429 cannot work: it is a factory trial build that branches into a setup/OOBE
routine at boot and waits forever for production-line tools. It never registers with
a receiver. See `08-technical-background.md` for the full analysis.

---

## Next step

- Have **169429**? Continue to `02-upgrade-from-169429.md`. Read it fully before touching the controller.
- Have **316382 / 282115**? Skip to `03-retail-firmware.md`.
## Note: the 2025 production run (GA00827-US)

Sealed controllers made in 4/2025 (box model GA00827-US) ship with the Bluetooth-mode firmware already applied — they were manufactured years after the Stadia service shut down. This is not a different or incompatible controller: it can be flashed to the 316382 Wi-Fi firmware with the same procedure as a 169429 unit, and from that point everything in this kit applies unchanged. When buying, prefer the 2025 unit if prices are close — less storage time means a healthier battery.