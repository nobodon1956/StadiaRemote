# 03 - Using a Retail Firmware Controller (316382 / 282115)

**This document is for controllers already on 316382 or 282115.**

If you are on 169429, go back to `02-upgrade-from-169429.md`. Do not continue here.

---

## Good news

You can skip the entire backup and flash section. The controller is already able to
register with a receiver. What remains is:

1. Pair the controller to your Wi-Fi (once).
2. Configure your router so only the controller resolves Google domains to your PC.
3. Run the receiver on the PC.
4. Optionally enable headset audio and autostart.

---

## Step 1 - Pair the controller to Wi-Fi

The Stadia controller uses Bluetooth **only** to receive Wi-Fi credentials. It never
acts as a Bluetooth gamepad for this kit.

Requirements:

- The PC has Bluetooth enabled (for this one-time step).
- Your Wi-Fi is **WPA2-Personal / AES (CCMP)**. WPA3 is not supported.
- PMF / 802.11w must be off or optional.
- 5 GHz works and is recommended.

Put the controller in pairing mode:

- If it has never been paired: short-press the Stadia button once. The LED blinks orange.
- Otherwise: hold Stadia about 4 seconds to power off, then hold **Y** and short-press Stadia.

Then run the generated `provision-wifi.bat`, or manually:

```cmd
cd /d "<your-project>\tools\stadiacast"
stadiacast-provision.exe scan
stadiacast-provision.exe provision --address <address-from-scan> --ssid <your-wifi-ssid>
```

If pairing fails with `STATE -> 0x4f` or the controller will not join:

- Confirm the AP is WPA2-PSK/AES with PMF disabled.
- Check the SSID and password carefully.
- Keep the controller close to the PC during pairing.

---

## Step 2 - Detect the controller's MAC and IP (automatic)

You do not look up or type these values. After the controller has joined Wi-Fi:

1. Double-click the generated `find-controller-mac.bat` on the PC. It scans the LAN for
   the Google-OUI device (`d4-f5-47...`) and writes `detected-values.txt`.
2. In `configurator.html`, click **Load detected-values.txt** and pick that file (or let
   your AI assistant apply the two values), then click **Generate** again.

The regenerated `dnsmasq-stadia.conf` and receiver script now contain the real **Wi-Fi
MAC** and IP. This is the Wi-Fi MAC, not the Bluetooth address from `stadiacast-provision
scan`. The values exist only after pairing. Full walkthrough: `10-find-the-controller-mac.md`.

If the PC scan cannot see the controller, read the router's DHCP lease list instead:

```sh
cat /tmp/dnsmasq.leases      # Padavan / OpenWrt; find hostname Stadia-...
```

and enter those two values through the configurator's "AI assistant / manual override"
section. Never edit a script by hand.

---

## Step 3 - Router DNS override

See `04-router-and-dns.md` for the full explanation. In short, add a rule that applies
**only to the controller's MAC**, telling it to use your PC as DNS:

```
dhcp-mac=set:stadia,<controller-mac>
dhcp-option=tag:stadia,option:dns-server,<pc-ip>
dhcp-host=<controller-mac>,<controller-ip>
```

Test and reload:

```sh
dnsmasq --test
# then restart dnsmasq on your router
```

Other devices on the network are unaffected.

---

## Step 4 - Run the receiver

See `05-receiver.md`. The short version:

1. Install the ViGEmBus virtual gamepad driver (once).
2. Double-click `start-receiver.vbs`.
3. Short-press the Stadia button on the controller (~1 second, release at first rumble).
4. Within seconds the LED goes steady and `joy.cpl` shows an Xbox 360 Controller.

Note: the first boot after pairing often only registers; it may not connect immediately.
Let it sit about a minute, power off with a long press, then wake it again with a short press.

---

## Step 5 - Optional extras

- **Headset audio**: see `06-audio-and-daily-use.md`. Requires ffmpeg with libopus.
- **Autostart**: copy `autostart-receiver.vbs` into your Windows Startup folder.
- **Restart helper**: double-click `restart-receiver.vbs` whenever the receiver misbehaves.

---

## A note about 282115 vs 316382

These two builds are essentially the same code compiled at different times. The
retail branch is `GothamYeti`. 316382 is the version confirmed working by multiple
people, so it is the one this kit recommends (see `docs/08` for how to obtain and verify
it). If you already have 282115 and it works, there is no reason to change it.
