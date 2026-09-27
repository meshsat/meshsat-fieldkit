# USB 2.0: the clauses the layer 5 closer cites (27 September 2026)

**What this file is.** A word-for-word transcription of the USB 2.0 clauses that `v2/docs/HW-FW-CONTRACT.md` (SC-HF-06,
HF-F06, V-B19) and `pcb_interfaces.yaml` IF-MON cite, and that the tree's own transcription
(`v2/vendor/standards/usb-2-0-specification-2024-09-27.md`) does not carry. It is filed here, not added to that file,
because `rules_status.py` records that file by sha as an input of `edge_length.py` (SI-001), and an edit to it would move
every board's SI-001 reading for no change in what SI-001 reads.

| | |
|---|---|
| document | Universal Serial Bus Specification, Revision 2.0 (`usb_20.pdf`), the same package the tree's transcription names |
| source | `https://www.usb.org/sites/default/files/usb_20_20250603.zip`, fetched again 27 September 2026 |
| sha256 of the package | `5fe9c53c04033818af396e8852b3acbca5c3a76ba92fab549fd81cd0ea7b3692` (the same as the tree's transcription) |
| sha256 of `usb_20.pdf` | `d39698a33486c399124af92bd02e4f978fd9a836b5cf4e52e6e4633eb1d89f61` (the same) |

## Chapter 7, its opening

> The USB 2.0 specification requires hubs to support high-speed mode. USB 2.0 devices are not required to support
> high-speed mode. A high-speed capable upstream facing transceiver must not support low-speed signaling mode.

## Table 7-1, the pull-up resistor row

> Pull-up Resistor (RPU): This resistor is required only in upstream facing transceivers and is used to indicate
> signaling speed capability. A high-speed capable device is required to initially attach as a full-speed device and
> must transition to high-speed as described in this specification.

Read for SC-HF-06: the monitor's touch controller, whatever its speed, attaches to board D's full-speed TUSB2046I hub at
full speed. That its HID function then works at full speed is INFERRED (interrupt transfers are defined for full-speed
devices, section 5.7), and V-B19 checks it.

## 7.2.1 Classes of devices

> A unit load is defined to be 100 mA. The number of unit loads a device can draw is an absolute maximum, not an average
> over time. A device may be either low-power at one unit load or high-power, consuming up to five unit loads. All devices
> default to low-power.

> High-power bus-powered functions: All power to these devices comes from VBUS. They must draw no more than one unit load
> upon power-up and may draw up to five unit loads after being configured.

Read for HF-F06: the bound on the touch controller's VBUS draw until V-B19 measures it (board D budgets J_USB3 at 0.05 A).
