#!/usr/bin/env python3
"""A banded schematic page must never separate a part from its own wires and labels (MESHSAT-862, 15 September 2026,
appendix 32.194 and its correction).

`kisch.reband` folds the row of 92 mm columns into bands under one user page. Its first version assigned every ITEM to
a band by the item's own first coordinate. A wide symbol whose labels and wires reach past the band seam (x0 + 2024)
then kept its body in band 0 while those labels moved to band 1: B19's regenerated schematic had 62 pins not connected
and 23 dangling labels, its netlist differed from the board's by 319 net and node lines, and the review pack shipped
that PDF. A, C, D and P happened to have no part on the seam.

The band is a property of the COLUMN, and the column is the part's: the body records, per item, the x of the emission
that wrote it (`Body.append`), `emit_part`, `emit_pwr_flag` and `text` set that anchor, and `reband` bands by it."""
import os, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import kisch  # noqa: E402

SRC = open(os.path.join(TOOLS, "kisch.py")).read()


def t_the_body_records_the_anchor_of_every_item():
    kisch.reset_body(); out = kisch.out
    kisch._ANCHOR[0] = 1972.0; out.append("(symbol (at 1972.0 100.0 0))"); out.append('(label "X" (at 2030.5 110.0 0))')
    kisch._ANCHOR[0] = 2064.0; out.append("(symbol (at 2064.0 100.0 0))")
    assert kisch.anchors == [1972.0, 1972.0, 2064.0], kisch.anchors
    assert isinstance(kisch.out, kisch.Body), "the import-time body (A and E never reset it) must record anchors too"


def t_a_label_past_the_seam_stays_in_its_parts_band_and_the_next_column_moves():
    kisch.reset_body(); out = kisch.out
    kisch._ANCHOR[0] = 1972.0; out.append("(symbol (at 1972.0 100.0 0))"); out.append('(label "X" (at 2030.5 110.0 0))')
    kisch._ANCHOR[0] = 2064.0; out.append("(symbol (at 2064.0 100.0 0))")
    paper = kisch.reband(out, colw=92.0, page_h=800.0)
    assert "2030.50 110.00" in out[1] or "2030.5 110.0" in out[1], "the label left its part's band: %s" % out[1]
    assert "40.00 960.00" in out[2], "column 22 must open band 1: %s" % out[2]
    assert paper.startswith('"User"'), paper


def t_every_emission_sets_the_anchor():
    for fn in ("def emit_part(p, x, y):", "def emit_pwr_flag(p, x, y):"):
        i = SRC.find(fn); assert i > 0, fn
        assert "_ANCHOR[0] = x" in SRC[i:i + 200], "%s does not set the anchor" % fn
    i = SRC.find("def text(t, x, y, size=2.0):"); assert i > 0
    assert "_ANCHOR[0] = x + 16.0" in SRC[i:i + 300], "a section title sits 15 mm left of its column and must anchor to the column"


def t_reband_never_bands_by_an_items_own_coordinate_when_an_anchor_exists():
    i = SRC.find("def reband("); body = SRC[i:SRC.find("def first_x_max")]
    assert "anchors" in body and "col // cols_per_band" in body, "reband does not band by the anchor's column"
    assert "first_x(it) - x0) // band_w" not in body, "an item is still banded by its own first coordinate"
