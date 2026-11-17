# 10 - The Controller's Wi-Fi MAC and IP (detected automatically)

**You do not need to find or type the controller's MAC or IP address.** The configurator
has no field for them. They are detected for you after pairing, and fed back into the
generator automatically. This page explains how that works and what to do if detection
fails.

The short version:

1. First generation: fill in only your PC IP, router IP, Wi-Fi and paths. Generate.
2. Pair the controller (`provision-wifi.bat`) and wake it so it joins Wi-Fi.
3. Run `find-controller-mac.bat`. It detects the controller and writes
   **`detected-values.txt`**.
4. In `configurator.html`, load that file (or let your AI assistant apply the values),
   then click **Generate** again. The real MAC and IP are now baked into every script.
5. Install the router rule and start the receiver.

---

## Read this first: it is NOT the Bluetooth address

This is the single most common mistake.

| | Bluetooth (BLE) address | Wi-Fi MAC address |
|---|---|---|
| What it looks like | e.g. `D4:F5:47:1A:FA:04` | e.g. `d4:f5:47:1a:fa:05` |
| When you can see it | Only while the controller is in **pairing / setup mode** (LED blinking orange) | After the controller has **joined your Wi-Fi** |
| Where you read it | `stadiacast-provision scan` | Your **router's DHCP lease/client list** |
| What it is used for | Sending the Wi-Fi name + password **once**, during pairing | The dnsmasq DNS rule and the static IP reservation |

These are two different identifiers for two different radios in the same controller.
They are often similar (and may differ by only the last digit), but **they are not the
same value**. The address printed by `stadiacast-provision scan` is the BLE address and
must **not** be pasted into the `dhcp-mac=` rule - the rule simply will not match, and the
controller will never receive your PC as its DNS server.

> The LED clue: orange blinking = Bluetooth setup mode (you are looking at the BLE address).
> White blinking / steady = the controller is on Wi-Fi (now a Wi-Fi MAC exists in your router).

---

## Why the MAC is needed at all

The DNS override in `04-router-and-dns.md` must apply **only** to the controller - not to
the whole network. The router identifies "the controller" by its Wi-Fi MAC. With the wrong
MAC, either nothing happens or (worse) other devices get the rewritten DNS and lose access
to Google services.

So the MAC has to be the real Wi-Fi MAC that the router sees.

---

## When it becomes available (the ordering trap)

There is a chicken-and-egg detail that trips people up:

1. Before pairing, the controller has not joined your Wi-Fi, so **no Wi-Fi MAC appears in
   the router**.
2. You pair it over Bluetooth (`provision-wifi.bat`) - this step does **not** need the MAC.
3. The controller joins your Wi-Fi and gets a DHCP lease. **Only now** does the Wi-Fi MAC
   show up in the router's client list.
4. Run `find-controller-mac.bat` on the PC - it detects the MAC and IP and writes
   `detected-values.txt`. Load that file in `configurator.html` and regenerate.

In other words: **pair first, detect second, finalize the DNS rule third.** Before
detection the generator uses a default IP and a placeholder MAC - the pairing and
detection scripts work fine, but do not install the router rule until you have
regenerated with detected values.

---

## Do I need my router's admin password?

**Not necessarily.** There are two routes:

- **Method A (router DHCP list)** needs router admin access (SSH or web UI login).
- **Method B (scan from this PC)** needs **no router login at all** - just the PC and the
  controller on the same network. It is generated for you as `find-controller-mac.bat`.

Start with Method B. If it cannot see the controller, fall back to Method A.

---

## Method B: scan from the PC, no router login (try this first)

The configurator generates a file called **`find-controller-mac.bat`**. It works like this:

1. Wake the controller with a short Stadia-button press so it joins Wi-Fi.
2. Double-click `find-controller-mac.bat` on the PC that runs the receiver.
3. It pings every address on your subnet to fill Windows' ARP cache, then finds the device
   whose Wi-Fi MAC begins with the Google OUI **`d4-f5-47`**.
4. It writes a file called **`detected-values.txt`** into your project folder:

```
# Stadia WiFi Kit - detected controller values
CONTROLLER_MAC=d4:f5:47:1a:fa:05
CONTROLLER_IP=192.168.1.155
```

5. Go back to `configurator.html`, click **Load detected-values.txt** and pick that file
   (or let your AI assistant enter the two values). The MAC and IP fill themselves in -
   you never type them. Click **Generate** again to bake them into every script.

If you are working with an AI assistant, it can simply read `detected-values.txt` and
enter the values for you through the "AI assistant / manual override" section.

**Requirements and limits - read these:**

- The controller must already be on Wi-Fi and on the **same subnet** as the PC. A guest
  network, AP isolation, or a second router doing its own NAT will hide it from ARP.
- Because it relies on ARP, it only works on your own LAN segment - which is exactly the
  situation this kit targets.
- Some networks have several Google devices (Chromecast, etc.). The controller is the one
  whose MAC belongs to a device you just woke up; if unsure, power the controller off,
  run the scan, then wake it and run again - the new `d4-f5-47...` entry is the controller.
- If no `d4-f5-47` line appears and you only have one such device, compare against the
  full ARP table the script also prints. If still nothing, use Method A.

This is the "detect it for me" path: you never type a router password, and you never
guess. The script does the discovery on the PC.

---

## Method A: the router's DHCP client list (most reliable, needs router login)

Every router that hands out DHCP addresses keeps a list of clients with their hostname,
IP and MAC. Look for a device whose hostname starts with **`Stadia-`** (for example
`Stadia-cd1e`). That entry is your controller. You need your router admin credentials
for this method.

### Padavan / ASUS RT-N56U based firmware

SSH into the router and run:

```sh
cat /tmp/dnsmasq.leases
```

Each line looks like:

```
<lease-expiry> d4:f5:47:1a:fa:05 Stadia-cd1e 192.168.1.155 *
```

The second field is the MAC, the third the hostname, the fourth the IP.

### OpenWrt / iStoreOS

Either SSH:

```sh
cat /tmp/dnsmasq.leases
```

or use the web UI: **Status -> DHCP Leases** (or `Network -> DHCP and DNS -> Leases`).
Find the `Stadia-...` hostname and copy its MAC and IP.

### Other routers

Look for a page named something like **Attached Devices**, **DHCP Client List**,
**Connected Devices**, or **LAN Clients**. Find the `Stadia-...` device and copy its MAC.

> Tip: if several devices are listed and you are not sure which one is the controller,
> wake the controller (short press of the Stadia button) and watch which lease/IP appears
> or refreshes. The hostname almost always begins with `Stadia-`.

---

## Fallback: from the receiver log (after the first connection)

Once the controller talks to the receiver, its IP appears in `server.jsonl` and in the
`/_input` endpoint. You can then find the matching MAC with `arp -a` on the PC:

```cmd
arp -a | findstr 192.168.1.155
```

This works only after the controller has communicated with the PC at least once, so it is
a verification aid. If you use Method A, enter the MAC and IP you find through the
configurator's "AI assistant / manual override" section - you still never edit any script
by hand.

---

## Fallback: the physical label (last resort)

Some controllers have a label with a MAC address. This is usually the **Bluetooth**
address, not necessarily the Wi-Fi MAC. Use it only as a hint to help you spot the right
entry in the router list - do not use it unless it matches what the router or the PC scan
reports.

---

## How to tell you got the right one

- The hostname next to it begins with `Stadia-`.
- Rebooting the controller makes that same MAC reappear with a fresh lease.
- After you install the rule and power-cycle the controller, the receiver log shows DNS
  queries from that controller's IP being redirected to your PC, followed by TLS
  connections. If you see no `tcp_accept`, the MAC in the rule is probably wrong - see
  `07-troubleshooting.md`.

---

## Common mistakes

- **Pasting the Bluetooth address from `stadiacast-provision scan` into the rule.** Wrong
  radio, wrong address, no connection.
- **Copying the PC's own MAC or the router's MAC** by accident from the client list.
- **Reading the lease list before pairing** - the controller is not on Wi-Fi yet, so there
  is nothing to find. Pair first.
- **Two routers doing DHCP.** In a main-router + side-router setup, read the lease table on
  the router that actually hands out addresses. This also breaks the PC ARP scan if the PC
  and controller end up on different subnets - use the router list that actually serves the
  controller.
- **Expecting the scan to work before pairing.** The controller has no Wi-Fi MAC on the LAN
  until it joins Wi-Fi. Pair first, then scan.

---

## Next step

Load `detected-values.txt` in `configurator.html` (or have your AI assistant apply the
values), click **Generate** again, and continue with `04-router-and-dns.md`. Do not install
the router rule while the summary still says the MAC is a placeholder.
