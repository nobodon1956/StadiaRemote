# 02 - Upgrade from 169429 (Backup First, Then Flash)

**This document is only for controllers on firmware 169429.**

Read the whole thing before you start. There is one rule that overrides everything else:

> **NEVER FLASH BEFORE THE BACKUP IS VERIFIED.**
> The backup is the only way back if the flash goes wrong.

---

## Why this is necessary

169429 is a factory FSI (Field/Factory System Image) build compiled on 2019-08-16,
three months before Stadia launched. At boot it detects the FSI flag and enters a
setup/OOBE branch that waits for production-line tools. In a normal home network it
hangs there forever and never registers with a receiver.

The retail firmware (316382) removes that branch and connects directly.
Flashing is the only reliable fix. Three independent controllers have been confirmed
to work after flashing to 316382.

---

## Before you begin

- A full USB **data** cable.
- The controller charged to at least 80%.
- A PC that will not sleep during the backup. Go to Power Options and set sleep to **Never**,
  keep the power adapter plugged in.
- Python 3.11+, `stadiatool`, and the local flasher page (see `04-tools-and-backup.md`).
- About 4 to 5 hours for the backup. Start when you can leave it alone.

---

## Step 1 - Confirm the connection (read only, safe)

```cmd
cd /d "<your-project>\tools\stadiatool\stadiatool"
python stadiatool.py info
```

You must see `Current firmware is gotham build 169429` and a healthy battery level.
If not, stop and fix the connection first.

---

## Step 2 - Enter SDP mode

1. Turn the controller off: hold the **Stadia button** about 4 seconds until the light goes out.
2. Unplug the USB cable.
3. Hold the **Options** button (three-dot button) down, and while holding it, plug the
   USB cable back into the PC. The light should stay off. If it lights up, unplug and retry.
4. Still holding Options, also hold **Assistant + A + Y** (four buttons total).
   No light or rumble feedback is normal at this point.
5. Load the flashloader:

```cmd
python stadiatool.py flashloader
```

Expected:

```
Found: 1fc9:0135 (...)
flashloader image is 100672 bytes
SDP load result: 0x00000000
```

The controller is now in flashloader mode (USB ID `15a2:0073`).

If the device is not found or you get a permission error, stop. On Windows you may
need a WinUSB driver for the SDP device (VID `1fc9`).

---

## Step 3 - Back up the firmware (4 to 5 hours)

Use the generated `backup-169429.bat` from the configurator, or run the two dumps manually:

```cmd
:: Part 1 - head / IVT region, about 9 minutes
python stadiatool.py dump 0 0x40000 "<your-project>\firmware\backup-169429-part1-head.bin"

:: Part 2 - App B slot, about 4 hours
python stadiatool.py dump 0x840000 0x1000000 "<your-project>\firmware\backup-169429-part2-appb.bin"
```

Why only these two ranges? A full 16 MB dump reads 4 million+ 4-byte chunks and can take
over 20 hours. The flasher only writes the App B slot, so the head region plus App B
are the parts that actually change. This gives you a real recovery path in a fraction of the time.

While it runs:

- The screen scrolls with addresses. That is normal.
- `Failed to read ... trying again` is automatic retry. Normal.
- Do not touch the controller, unplug the cable, or let the PC sleep.

Note on the stadiatool patch: the original bulk-read command is rejected by the restricted
flashloader. This kit uses a modified `stadiatool.py` with register setup (`setupFlashRegs`)
and a rewritten `IPRXFCR` (0xB8) before every read. Without that patch the dumped data
comes back as repeated address values instead of real flash contents.

---

## Step 4 - Verify the backup

Check file sizes:

```
backup-169429-part1-head.bin    262,144 bytes
backup-169429-part2-appb.bin  8,126,464 bytes
```

Hash them:

```cmd
certutil -hashfile backup-169429-part1-head.bin SHA256
certutil -hashfile backup-169429-part2-appb.bin SHA256
```

Confirm the dump is real, not zeros or repeated addresses:

```cmd
findstr /C:"169429" backup-169429-part2-appb.bin
```

You should see `169429`, plus strings such as `gotham`, `pvt`, and `fsi_build`.
Hashes differ from controller to controller; size and readable strings are the real
checks.

Then copy **both** files to a USB stick and to a cloud drive. Read them back and
compare hashes. Only after this is done are you allowed to flash.

---

## Step 5 - Return the controller to normal mode

After the dump the controller is still in flashloader mode with no light. Soft-reset it:

```cmd
python stadiatool.py reset
```

Then unplug, hold the Stadia button 10 seconds for a hard reset, and plug it back in.
Confirm the USB ID is back to `18d1:9400` and the light behaves normally.

---

## Step 6 - Flash 316382

1. Run the generated `start-flasher.bat` (or manually start a local HTTP server in the
   flasher's `src` directory on port 5000).
2. Open **Google Chrome** at `http://localhost:5000`. Chrome is required for WebHID.
3. Follow the on-screen instructions to put the controller into flashing mode.
4. When the page detects the controller in **Wi-Fi mode**, a button appears:

   ```
   Revert to Wi-Fi mode (Dogfood only)
   ```

   **Click this button.** Do not click "Switch to Bluetooth mode".

   This button skips the Verify step that hangs on FSI controllers and writes 316382
   directly. If clicking it does nothing, hard-refresh Chrome with Ctrl+Shift+R - the
   flasher included here has the button-argument bug fixed.

5. Do not touch the controller or interrupt power until it finishes.

The firmware file used is:

```
ota.316382.stable-channel.gotham-pvt-b.da986392604309ea67eab5fa84f747e955f2875c.bin
SHA1: da986392604309ea67eab5fa84f747e955f2875c
```

---

## Step 7 - Verify the flash

Turn the controller on in Wi-Fi mode and start the receiver (`05-receiver.md`).
Success looks like:

- Log contains `play.googleapis.com`, `firmware=316382`, and `gamepad_created`.
- `joy.cpl` shows an Xbox 360 Controller and buttons respond.

If it fails, do not panic. Your factory backup is safe. See `07-troubleshooting.md`.

---

## If something goes wrong

Stop. Do not repeatedly retry or press random button combinations.
Note down the exact error text, the LED state (color, steady or blinking), and the step
number you were on. That information is what makes recovery possible.
