# USB 2.0 Specification, the signalling edges this project declares from it

**What this file is.** A transcription of the three rows and one clause this project CITES, not a copy of the
specification. The document is published free of charge by USB-IF on usb.org and is fetched, never
redistributed here.

| | |
|---|---|
| document | Universal Serial Bus Specification, Revision 2.0, with its errata and ECN package |
| issuer | USB Implementers Forum (Compaq, Hewlett-Packard, Intel, Lucent, Microsoft, NEC, Philips) |
| package | `usb_20_20250603.zip`, the 3 June 2025 collection of the 27 September 2024 release |
| source | `https://www.usb.org/sites/default/files/usb_20_20250603.zip` |
| fetched | 16 September 2026 |
| sha256 of the package | `5fe9c53c04033818af396e8852b3acbca5c3a76ba92fab549fd81cd0ea7b3692` |
| sha256 of `usb_20.pdf` inside it | `d39698a33486c399124af92bd02e4f978fd9a836b5cf4e52e6e4633eb1d89f61` |
| size of `usb_20.pdf` | 5,983,789 bytes |
| clauses transcribed | 7.1.2.1, 7.1.2.2, Table 7-9 (full speed), Table 7-10 (low speed) |

## Why this project reads a specification for a rise time

An edge rate belongs to the DRIVER, and this project checked what its own drivers publish before coming here:
the RP2040 datasheet documents a slew-rate control bit and no number, and the 74LVC family datasheets from
both TI and Nexperia specify only the INPUT transition rate they tolerate (10 to 20 ns/V), not the output edge
they produce. A USB transceiver is the exception in this kit: its edge is not a vendor's private business but
a conformance requirement, stated as a MINIMUM, which is exactly the number a transmission-line criterion
needs, because the fastest edge the specification allows is the worst case a board has to be designed for.

## 7.1.2.2 High-speed signalling rise and fall times

> The transition time of a high-speed driver must not be less than the specified minimum allowable
> differential rise and fall time (THSR and THSF). Transition times are measured when driving a reference load
> of 45 Ohm to ground on D+ and D-. ... For a hub, or for a device with detachable cable, the 10% to 90%
> high-speed differential rise and fall times must be 500 ps or longer when measured at the A or B receptacles
> (respectively).

**0.5 ns** is therefore the fastest edge a conforming USB 2.0 high-speed driver presents to a board, and it is
the number this project declares for every 480 Mbit/s data line.

## Table 7-9, full-speed source electrical characteristics

| parameter | symbol | conditions | min | max | unit |
|---|---|---|---|---|---|
| Rise time | TFR | Figure 7-8, Figure 7-9 | 4 | 20 | ns |
| Fall time | TFF | Figure 7-8, Figure 7-9 | 4 | 20 | ns |
| Differential rise and fall time matching | TFRFM | TFR/TFF | 90 | 111.11 | % |

**4 ns** is the fastest edge a conforming full-speed (12 Mbit/s) driver presents, and it is what this project
declares for the RP2040's own USB port on boards C and E. The bit rate is 40 times slower than high speed and
the edge is only 8 times slower: a full-speed line is a fast net.

## Table 7-10, low-speed source electrical characteristics

| parameter | symbol | conditions | min | max | unit |
|---|---|---|---|---|---|
| Rise time | TLR | Figure 7-8 | 75 | 300 | ns |
| Fall time | TLF | | 75 | 300 | ns |

No line in this kit is low speed; the row is here because it is the third of the set and its absence would
read as an omission.

## 7.1.2.1, how the numbers are measured, which decides what they may be used for

> For low-speed and full-speed, the output rise time and fall times are measured between 10% and 90% of the
> signal ... The rise and fall times for full-speed buffers are measured with the load shown in Figure 7-9.

They are 10 to 90 percent transition times at a stated load, which is the same definition the critical-length
arithmetic uses. They are not slew rates and not 20-80 figures, and they are minimums: a particular
transceiver may be slower and no conforming one is faster.

## What this specification does NOT cover here

* **USB 3.x SuperSpeed.** Board B's 5 Gbit/s lanes are governed by the USB 3.2 specification, a separate
  document that is not in this tree, so those nets carry no declared edge and are named as undeclared rather
  than given this one.
* **Any non-USB net.** The 0.5 ns and 4 ns figures are properties of a USB transceiver and of nothing else.
