#!/usr/bin/env python3
"""r8int6 (the integrator of set 6 of the handover, 27 September 2026): stream w4b's page drafts (page_drafts_w4b.py, beside
this file) re-derived for the integration, where the RF-002 walk's rows land in the same commit as board B's change.

The stream wrote its pages for a tree where the rows were still a draft for the tools author ("drafted for the tools
author", `drafts/w4b/tools/...`). At integration they land together (the integrator's instruction: the board change and
the tool rows land together), so every sentence that says the rows are drafted, not adopted, is restated as landed, and
every `drafts/w4b/` path is the filed record's path. The independent check's corrections that belong in these pages are
applied as well (w4b check 1, an AI check):
  - section 4c's fault F2 row states the SN74LV1T08's VIL in its brown-out band (0.65 V at VCC 3 to 3.6 V) and marks
    3.6 to 4.5 V INFERRED, where the stream stated only VCC 4.5 to 5.5 V while the AP64500 runs down to VIN 3.1 V;
  - section 4c's L2 row states that 0.58 V is just above the LVC1G family's VIL at VCC 1.65 V (0.578 V) and what bounds
    the outcome there, where main's margin was positive.
Every replacement asserts its old text inside the stream's edits exactly once; the stream's own anchor checks then run.
Usage: page_drafts_w4b_r8int6.py <repo root> [--check]"""
import importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location("pd_w4b", os.path.join(HERE, "page_drafts_w4b.py"))
PD = importlib.util.module_from_spec(sp); sp.loader.exec_module(PD)

REC = "v2/docs/records/w4b"
SWAPS = [
    # section 0's bullet
    ("  which closes a fault F2 hole the walk found once it read the SN74LVC2G06. With the rows drafted for the tools author\n"
     "  RF-002's walk reads board B FAIL 1 (`TX_INHIBIT_n`, W3T-F1), PASS 15, UNDECIDED 4 (section 4c).\n",
     "  which closes a fault F2 hole the walk found once it read the SN74LVC2G06. With the walk's rows that landed with the\n"
     "  change (`tools/tx_inhibit.py`), the stream's re-take in scratch read board B FAIL 1 (`TX_INHIBIT_n`, W3T-F1), PASS 15,\n"
     "  UNDECIDED 4 (section 4c).\n"),
    # section 4c, L2 row: the walk's rows landed, and the check's margin note
    ("RF-002's walk, with the rows drafted for the tools author, bounds the line at 0.58 V in its worst fail-safe state (0.50 V on main), under the 0.8 V VIL | CLOSED at desk (the walk's bound) |",
     "RF-002's walk, with the rows that landed with this change, bounds the line at 0.58 V in its worst fail-safe state (0.50 V on main), under the 0.8 V VIL. The 13 uA of new readers raise that worst level (J_AB1 unplugged, board C unpowered, R58 alone) from about 0.52 V to 0.58 V, just above the LVC1G family's VIL at VCC 1.65 V (0.35 x VCC = 0.578 V, SCES217AA, SCES214AF), where main's margin was positive: only U{s}12, U501 to U506 and U536 at the edge of their own supply band see it, and there the outcome is bounded by the new dividers (U502 to U504), by +3V3_ZB staying at or below 1.65 V (U505), by U536's open L4 item and by the module's boot order (U{s}12, INFERRED) (corrected at integration, from the independent check) | CLOSED at desk (the walk's bound) |"),
    # section 4c, fault F2 row: the LV1T08's VIL below VCC 4.5 V
    ("its VIL is 0.8 V at VCC 4.5 to 5.5 V and its inputs are 5.5 V tolerant with II +-1 uA at VCC 0 to 5.5 V;",
     "its VIL is 0.8 V at VCC 4.5 to 5.5 V and 0.65 V at VCC 3 to 3.6 V, and nothing is stated between 3.6 and 4.5 V (a VIL "
     "monotone in VCC there is INFERRED), which matters because the AP64500 keeps running down to VIN 3.1 V (DS41979, "
     "Adjusting UVLO), and EMCON_HW's worst bound of 0.58 V is under 0.65 V (corrected at integration, from the independent "
     "check); its inputs are 5.5 V tolerant with II +-1 uA at VCC 0 to 5.5 V;"),
    # section 4c, RF-002 row
    ("| RF-002's walk | main's `tx_inhibit.py` holds no row for the SN74LVC2G06 or the SN74LV1T08, and its re-take in scratch reads `inhibit_chain_b` FAIL 11, PASS 3, UNDECIDED 6 on the candidate (FAIL 11, PASS 6, UNDECIDED 3 on main); `inhibit_chain_a` and `_c` move by one PASS to UNDECIDED each, on the line's new readers. With the rows drafted for the tools author (`drafts/w4b/tools/apply_tx_inhibit_w4b.py` and its test changes: the two logic rows, the AO3400A read as an N-channel FET, U221 and J_QMX in ACCESSORIES, and a VCC-band field for the LV1T08's VIL) it reads FAIL 1, PASS 15, UNDECIDED 4, and boards A and C as on main.",
     "| RF-002's walk | before this change `tx_inhibit.py` held no row for the SN74LVC2G06 or the SN74LV1T08, and its re-take in scratch read `inhibit_chain_b` FAIL 11, PASS 3, UNDECIDED 6 on the candidate (FAIL 11, PASS 6, UNDECIDED 3 on main); `inhibit_chain_a` and `_c` moved by one PASS to UNDECIDED each, on the line's new readers. The rows land with this change (`tools/tx_inhibit.py` and `tests/test_tx_inhibit.py`, from `%s/tools/apply_tx_inhibit_w4b.py` and its test changes: the two logic rows, the AO3400A read as an N-channel FET, U221 and J_QMX in ACCESSORIES, and a VCC-band field for the LV1T08's VIL), and with them the stream's re-take in scratch read FAIL 1, PASS 15, UNDECIDED 4, and boards A and C as on main." % REC),
    ("| the rows: the tools author's; the three back-feed items: SD-EMC-2's |",
     "| the rows: landed with this change; the three classes the walk does not read: the tools author's; the three back-feed items: SD-EMC-2's |"),
    # section 8's tools hand-off
    ("Drafted by stream w4b (`drafts/w4b/tools/apply_tx_inhibit_w4b.py`, `apply_tx_inhibit_tests_w4b.py`),\n"
     "  with the SN74LV1T08's row (board B's U116, U216, U316) and a VCC-band VIL field; still the tools author's:",
     "Landed with stream w4b's board change (`%s/tools/apply_tx_inhibit_w4b.py`,\n"
     "  `apply_tx_inhibit_tests_w4b.py`, applied at the r8int6 integration), with the SN74LV1T08's row (board B's U116, U216,\n"
     "  U316) and a VCC-band VIL field; still the tools author's:" % REC),
    # ARCHITECTURE 13.4
    ("RF-002's walk does not model the SN74LVC2G06 yet (tools; the row drafted by stream w4b, `EMCON.md` 4c) |",
     "RF-002's walk modelled the SN74LVC2G06 only from stream w4b (tools; the row landed with it, `EMCON.md` 4c) |"),
]


_STREAM_EDITS = PD.edits


def edits():
    E = _STREAM_EDITS()
    for old, new in SWAPS:
        hits = [k for k, (_p, _o, n) in enumerate(E) if old in n]
        assert len(hits) == 1 and E[hits[0]][2].count(old) == 1, "r8int6: %r found in %d edit(s)" % (old[:70], len(hits))
        p, o, n = E[hits[0]]
        E[hits[0]] = (p, o, n.replace(old, new))
    left = [n for _p, _o, n in E if "drafts/w4b" in n or "drafted for the tools author" in n]
    assert not left, "r8int6: a draft path or a 'drafted' sentence is left: %r" % [x[:80] for x in left]
    return E


PD.edits = edits
if __name__ == "__main__":
    sys.exit(PD.main(sys.argv[1:]))
