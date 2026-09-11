#!/usr/bin/env python3
"""Which land a 2.54 mm IDC header gets, for the four boards that carry one.

11 September 2026 measured the channel between the two columns of a 2.54 mm header: 2.54 pitch less a 1.70 mm
pad is 0.84 mm, and a 0.30/0.20/0.30 pair with 0.127 clearance needs 1.054, on every layer, the pins being
through-hole (decision 6 of `v2/docs/OWNER-DECISIONS-2026-09-11.md`). The two answers are the END row, which
escapes past the end of the connector, and a NARROWER pad: 1.40 mm on a 1.00 mm drill keeps a 0.20 mm annular
ring and opens the channel to 1.14 mm.

The narrow land is not free. It is one land pattern for every header on a board, so it changes every escape on
every one of them, and on B19 it is worth minus seven pairs of 113 (57 with the stock land, 50 with the narrow
one, 12 September 2026). A carries three ribbon pairs that have nowhere else to go and lays 3 of 3 with it; B's
only header pair is J_PANEL's USB_PNL, which `pair-header-allow.txt` already declares as one this tree does not
fix. So the land is a per-board measurement and each board declares the one it was measured best at, in
`boards/<letter>.json` as `gen_env: {"IDC_PADS": ...}`, with the number beside it.

IDC_PADS=narrow (the default) or stock. Nothing else is accepted: a typo silently reverting a board to the
0.84 mm channel is exactly the class of defect this tree keeps finding."""
import os

MODE = os.environ.get("IDC_PADS", "narrow")
if MODE not in ("narrow", "stock"): raise SystemExit("IDC_PADS is %r; it is 'narrow' or 'stock'" % MODE)


def idc(rows):
    """The footprint key for a 2xNN 2.54 mm vertical IDC header, e.g. idc("2x13")."""
    if MODE == "stock": return "Connector_IDC:IDC-Header_%s_P2.54mm_Vertical" % rows
    return "meshsat:IDC-Header_%s_P2.54mm_Vertical_NarrowPad" % rows
