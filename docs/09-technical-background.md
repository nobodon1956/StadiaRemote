# 09 - Technical Background: Why 169429 Cannot Work

This document records the analysis behind this kit. It is optional reading, but it
explains why the flash step is unavoidable.

Method: static string-table comparison of three firmware images. No disassembly, no
image modification. See the reproduction steps at the end.

---

## Summary

169429 is not simply an old version. It is a **factory trial (FSI) build** from
2019-08-16, three months before Stadia launched. At boot it detects the FSI flag and
enters a setup/OOBE branch that waits for production-line tools. In a home network
nothing ever satisfies that branch, so the controller hangs forever and never registers.

Retail builds remove that branch and go straight to Wi-Fi checks and registration.

---

## Build comparison

| Field | 169429 | 282115 | 316382 |
|---|---|---|---|
| Build time | 2019-08-16 | 2021-11-19 | 2022-09-06 |
| User-Agent | `StadiaController/1.0b169429` | `.../1.0b282115` | `.../1.0b316382` |
| Image name | `GothamFsi_b_img` | `GothamYeti_a_img` | `GothamYeti_b_img` |
| Branch | FSI (factory trial) | Yeti (retail) | Yeti (retail) |

The image name alone is decisive: factory builds come from `GothamFsi`, retail builds
from `GothamYeti`. Even the code branch changed.

282115 and 316382 are essentially the same code compiled twice. After removing random
byte noise, the meaningful differences are only the version number, build time, build
path, and image name. The real gap is 169429 -> 282115.

---

## Decisive evidence: the FSI branch

Strings found **only in 169429**:

| String | Meaning |
|---|---|
| `Requesting setup due to boot into FSI!` | Boot requests setup because of FSI flag |
| `FSI build entering setup.` | FSI build enters setup |
| `Going into setup mode due to connection error.` | Connection errors also fall back to setup |
| `vendor_usb_fsi_events.cc` | FSI-only event module, absent from retail |
| `SetupWebRtcChannel` | WebRTC channel used by setup mode |
| `GET /setup/eureka_info?params=build_info,name HTTP/1.1` | Chromecast device discovery in setup |
| `SNTP_FSI` / `Should not block on SNTP in the FSI` | FSI-only SNTP branch |
| `OTA_MISSING_FOR_FSI` | FSI-only OTA error code |

Strings present in retail builds at the corresponding point:

| String | Meaning |
|---|---|
| `non-FSI` | Retail value of the `fsi_build` field |
| `Entering WIFI_CHECKS_BEFORE_CONNECTING directly!` | Go straight to Wi-Fi checks |
| `Entering WIFI_CONNECTING directly!` | Go straight to connecting |
| `Connection reset requested` | Active connection reset |
| `Display disconnection error, code = %d` | Disconnect error handling |
| `Skipping update check; found no update earlier` | Update result caching |

So the two boot paths are:

```
169429: boot -> provision check -> FSI detected -> Requesting setup
        -> setup/OOBE (waits for factory tools) -> never returns

316382: boot -> provision check -> Entering WIFI_CHECKS_BEFORE_CONNECTING directly
        -> Wi-Fi connect -> register -> connected
```

---

## Why the packet capture looked confusing

Before flashing, the controller completed the `stadiaconfig` request and two Omaha
`update2` requests, then made no further requests. This was initially read as a bad
Omaha response. The real explanation:

- `update_checker` runs **before** the setup branch, so those requests succeed normally.
- After the branch, the state machine enters setup mode and makes no further cloud
  requests. It is waiting for factory provisioning data, not for Google services.

The problem is therefore the state chosen after Omaha, not the Omaha response itself.

---

## An untested alternative: official OTA self-update

169429 contains a complete `update_checker.cc`, `update_task.cc`, `http_flash_writer.h`
and `partition_table.h`. The controller can download an OTA, verify its hash, write a
partition, switch slots and roll back on failure.

In principle, a receiver could answer the Omaha request with "an update is available"
and let the controller upgrade itself to 316382 - no hardware handling, no WebHID.

Unknowns that block recommending this:

1. `OTA_MISSING_FOR_FSI` is an FSI-only error code. It may impose extra checks on FSI builds.
2. Bootloader OTA and app OTA are two separate checks in 169429 and may both need answers.
3. Writing to slot B from `image="a"` matches the flasher's observed behaviour but is unproven here.
4. Signature verification must accept the official OTA package.

This kit uses the proven WebHID method. The OTA idea is left here for someone who wants
to explore a safer, hardware-free future path.

---

## Reproduction

```bash
# Extract printable strings (>= 6 chars)
python -c "
import re
b=open('image.bin','rb').read()
s=set(m.group().decode() for m in re.finditer(rb'[\x20-\x7e]{6,}', b))
open('str.txt','w').write('\n'.join(sorted(s)))
"

# Compare the two tables
comm -23 <(sort str-169429.txt) <(sort str-316382.txt)
```

Then narrow by keywords: `FSI`, `setup`, `OTA`, `gotham_task`, `update_checker`.
