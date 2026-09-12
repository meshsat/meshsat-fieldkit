#!/usr/bin/env python3
"""Legend (PCB_TEXT) corrections on the routed boards, by text content, no re-route. Usage: silk_fix_all.py <board.kicad_pcb> <key>
key: a|b|c|d|e1|e2 (the spacer ring R1 is retired with C5). Rules: ("match", {"text"?, "pos"?, "layer"?, "size"?, "angle"?, "halign"?, "delete"?}); match = prefix of the current text."""
import sys, pcbnew
from pcbnew import VECTOR2I, FromMM
OX, OY = {"c": (297.0, 210.0), "e2": (200.0, 20.0)}.get(sys.argv[2], (150.0, 110.0))
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
F, B = pcbnew.F_SilkS, pcbnew.B_SilkS
# 12 September 2026 (MESHSAT-862): THE RULE SETS FOR a, b AND c ARE GONE, for the reason D's were dropped on 8
# September and one worse. They rewrote each board's TITLE, and they rewrote it to a stale phase and a stale
# stackup: A's said "REV A (A18)" and "285 x 160 x 1.6 mm FR-4, 4 layers ... 2026-09-04" while A24 is 240 x 160
# on six layers, B's said "REV A (B12)" and "245x170x1.6 4L" on a six-layer board, C's said "REV A, C5". The
# generators take the phase from the chain (`PHASE`) and write the size and the stackup from the board they are
# building, and this pass ran AFTER them in every finish and put the old text back. A24's routed board carries
# "A18" on its front silk because of it, which `verify_deliverable` correctly refuses. A legend pass may move a
# legend; the facts on it belong to the generator that knows them.
RULES = {
 "e12": [("MESHSAT PCB-E1 DOCK", dict(size=1.2, pos=(0, -52.3)))],
}
b = pcbnew.LoadBoard(sys.argv[1]); n = 0
for d in list(b.GetDrawings()):
    if not isinstance(d, pcbnew.PCB_TEXT) or d.GetLayer() not in (F, B): continue
    s = d.GetText()
    for match, r in RULES.get(sys.argv[2], []):   # a board with no legend rules left (D since 8 Sep 2026) passes through untouched
        if not s.startswith(match): continue
        if r.get("delete"): b.Remove(d); n += 1; break
        if "text" in r: d.SetText(r["text"])
        if "pos" in r: d.SetPosition(P(*r["pos"]))
        if "shift" in r: p = d.GetPosition(); d.SetPosition(VECTOR2I(p.x + FromMM(r["shift"][0]), p.y - FromMM(r["shift"][1])))
        if "size" in r: d.SetTextSize(VECTOR2I(FromMM(r["size"]), FromMM(r["size"]))); d.SetTextThickness(FromMM(max(0.15, r["size"] * 0.16)))
        if "angle" in r: d.SetTextAngleDegrees(r["angle"])
        if "layer" in r: d.SetLayer(r["layer"]); d.SetMirrored(r["layer"] == B)
        n += 1; break
if sys.argv[2] == "e12":
    for fp in b.GetFootprints():
        if fp.GetReference() == "U2": fp.Reference().SetPosition(P(17.2, -60.6)); n += 1
pcbnew.SaveBoard(sys.argv[1], b); print("%s: %d legend items changed" % (sys.argv[2], n))
