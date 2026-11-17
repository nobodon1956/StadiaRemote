# 04 - Router and DNS Setup

This is the step people most often get wrong. Read it carefully.

---

## How it works

A Stadia controller wakes up and tries to reach Google endpoints such as
`play.googleapis.com`, `clients3.google.com`, and `time.google.com`. Google shut those
services down, so normally the controller never finds anything.

This kit runs a receiver on your PC that pretends to be those servers. For that to work,
the controller must resolve those domain names to your PC's IP. We do that with a DNS
override on the router, applied **only** to the controller's MAC address.

```
controller wakes up
  -> asks router: where is play.googleapis.com?
  -> router sees controller's MAC, answers: <your PC IP>
  -> controller connects to the receiver on the PC
  -> receiver creates a virtual Xbox 360 controller
```

Other devices keep using your normal DNS. Nothing else on the network is affected.

---

## Prerequisites

- A router where you can edit dnsmasq config (Padavan, OpenWrt, iStoreOS, etc.).
- Your PC has a **static IP** on the LAN. If the PC's IP changes later, everything breaks.
- The controller's **Wi-Fi MAC and IP** - detected automatically after pairing by
  `find-controller-mac.bat` and loaded into the configurator (see
  `10-find-the-controller-mac.md`). You never type them. This is NOT the Bluetooth address.
- It is recommended to bind the controller to a fixed IP as well.

---

## The config file

The configurator generates `dnsmasq-stadia.conf` with your values filled in. It looks like:

```
dhcp-mac=set:stadia,aa:bb:cc:dd:ee:ff
dhcp-option=tag:stadia,option:dns-server,192.168.1.100
dhcp-host=aa:bb:cc:dd:ee:ff,192.168.1.155
```

Line by line:

| Line | Meaning |
|---|---|
| `dhcp-mac=set:stadia,<mac>` | Tag DHCP requests coming from the controller |
| `dhcp-option=tag:stadia,option:dns-server,<pc-ip>` | Give only tagged devices your PC as DNS |
| `dhcp-host=<mac>,<ip>` | Reserve a fixed IP for the controller (optional but recommended) |

---

## Where to put it

| Router firmware | Path |
|---|---|
| Padavan (ASUS RT-N56U based) | `/etc/storage/dnsmasq/dnsmasq.d/stadiacast.conf` |
| OpenWrt / iStoreOS | `/etc/dnsmasq.d/stadiacast.conf` |
| Others | Look for the dnsmasq config directory in the router UI |

On Padavan, files under `/etc/storage/` survive a reboot. Remember to save the
configuration in the web UI as well.

---

## Apply it

```sh
dnsmasq --test          # should report syntax OK
/etc/init.d/dnsmasq restart    # or use the router web UI
```

Some routers accept a HUP reload instead of a full restart.

---

## Verify it

1. Power the controller off and on so it gets a fresh DHCP lease.
2. On the router, confirm the controller got the IP you reserved.
3. Start the receiver and watch its log. You should see DNS queries from the
   controller's IP being redirected to the PC, followed by TLS connections.

If the log shows no `tcp_accept` from the controller:

- The MAC in the rule does not match the actual controller MAC (check the lease table).
- The controller did not renew its lease after the rule was added. Power-cycle it.
- The router's DHCP server is not the one you edited (some setups have a second router
  running DHCP).

---

## Common mistakes

- **Editing the wrong router.** In a main-router + side-router setup, check which one
  actually hands out DHCP leases.
- **Setting DNS globally** instead of by MAC. This can break other devices and is
  unnecessary.
- **PC IP changed** after a router reboot. Set a static IP or a DHCP reservation for the PC.
- **Wi-Fi is WPA3.** Stadia only supports WPA2-Personal/AES. Change the AP settings.

---

## Reverting

Delete the config file and restart dnsmasq. The controller will go back to the
router's normal DNS and will no longer connect to the receiver.
