#!/usr/bin/env python3
"""Numeric verification of PCB-E1 DOCK: outline, rod pass-throughs, the target block where PCB-A's J_DOCK lands, nothing on the underside."""
import sys, pcbnew
import os as _bo, sys as _bs; _bs.path.insert(0, _bo.path.dirname(_bo.path.abspath(__file__)))
import verdict as _vh; _vh.crash_hook("check_pcb_e", sys.argv[1:])   # a crash in this module body writes INCONCLUSIVE, never nothing (18 Sep 2026)
import boardtable as _bt   # the copper layer count is a DECLARATION in boards/<letter>.json, never a
                           # literal here: six gates carried one, so a layer decision meant editing a
                           # gate, and two experiments came back with their only failure being the gate
                           # describing the previous decision (board A, 12 September; board C, today)
OX, OY = 150.0, 110.0
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
b = pcbnew.LoadBoard(sys.argv[1]); fails = []; checked = []; _intent_reported = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    checked.append(m)
    if not c: fails.append(m)
segs = [(case(d.GetStart()), case(d.GetEnd())) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT]
pts = [p for s in segs for p in s]; x0, x1, y0, y1 = min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)
check(abs(x1 - x0 - 267) < 0.01 and abs(y1 - y0 - 68) < 0.01 and abs(y1 + 45) < 0.01 and abs(x1 - 118) < 0.01, "strip 267 x 68 at X -149..118, Y -113..-45 (got X %.1f..%.1f Y %.1f..%.1f)" % (x0, x1, y0, y1))
# THE COPPER LAYER COUNT IS A DECLARATION, NEVER A LITERAL (16 September 2026). A literal here meant a
# layer decision was a gate edit, and twice a measurement came back whose ONLY failure was the gate
# describing the previous decision: board A four layers on 12 September (510 of 511) and board C six
# layers on 16 September. Under the P0 ruling every board's count is open, so it lives in the board
# table with its reason and is read here; a board that declares none keeps the count written below.
_LAYERS = _bt.value("e", "copper_layers", 4)
check(b.GetCopperLayerCount() == _LAYERS, "%d copper layers as board E declares them (JLC04161H-7628 at four; under P0 review 11 Sep 2026)" % _LAYERS)
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
for ref, (x, y) in (("H1", (-110.5, -73.0)), ("H2", (110.5, -73.0))):
    p = case(fps[ref].GetPosition()) if ref in fps else None
    check(p is not None and abs(p[0] - x) < 0.01 and abs(p[1] - y) < 0.01 and abs(list(fps[ref].Pads())[0].GetDrillSize().x / 1e6 - 3.2) < 0.01, "%s rod pass-through Ø3.2 at (%.1f, %.1f)" % (ref, x, y))
jd = fps.get("J_DOCK"); bb = jd.GetBoundingBox(False, False) if jd else None
check(all(not fp.IsFlipped() for fp in b.GetFootprints()), "no part on the underside (it sits on the floor)")
# 26 September 2026 (MESHSAT-1357 round 4): the round's three new functions are parts a placement must carry: J_TAMP the lid
# and tamper switch lead (S-11), U16 the Geiger supply switch (F-BP-02) and U17 the battery-bay SGP41 (S-10). A board placed
# before the generator changed does not carry them and fails here, which is the point: it is not this design.
for ref in ("J_DCIN", "F1", "U3", "Q1", "D1", "U6", "Q7", "L2", "U4", "Q2", "U5", "L1", "R5", "J_SOLAR", "F2", "J_BATT", "F3", "J_BLK", "P_CP", "P_CN", "U10", "U11", "U12", "U13", "U14", "U15", "J_SMB", "J_POD", "J_FAN1", "J_FAN2", "J_TAMP", "U16", "U17", "D10"): check(ref in fps, "%s present" % ref)
def find(xy, d):
    for r, f in fps.items():
        if r.startswith("H") and abs(case(f.GetPosition())[0] - xy[0]) < 0.05 and abs(case(f.GetPosition())[1] - xy[1]) < 0.05 and abs(list(f.Pads())[0].GetDrillSize().x / 1e6 - d) < 0.05: return f
    return None
# E4 height rule (32.18, 32.19 AO): every part north of Y -80 is under PCB-A at 13.4 mm; the tall parts must sit south of it
# J_SMB is a JST-XH 1x4 since 26 September 2026 (S-05) and J_TAMP a JST-XH 1x2 (S-11): the header is 9.8 mm (JST eXH), and
# both keep the 14.0 mm bar the lead headers carry here, which leaves room for the mated housing and the lead's bend.
TALL = {"F1": 16.3, "F2": 16.3, "F3": 16.3, "J_BATT": 10.5, "J_DCIN": 8.0, "J_SOLAR": 8.0, "C11": 7.7, "C12": 7.7, "C24": 6.9, "C25": 6.9, "L1": 10.0, "L2": 8.0, "J_SMB": 14.0, "J_POD": 14.0, "J_LTG": 14.0, "J_GEIGER": 14.0, "J_DCF": 14.0, "J_FAN1": 14.0, "J_FAN2": 14.0, "J_TAMP": 14.0}
for ref, h in TALL.items():
    if ref in fps:
        bb = fps[ref].GetBoundingBox(False, False); top = OY - bb.GetTop() / 1e6; right = bb.GetRight() / 1e6 - OX
        check(h <= 12.0 or top <= -80.0 or right <= -121.0, "%s (%.1f mm tall) sits south of the PCB-A edge, west of X -121 or under 12 mm (top edge Y %.1f, right edge X %.1f)" % (ref, h, top, right))
for (x, y) in [(-104.0, -63.0), (-66.0, -63.0), (-104.0, -83.0), (-66.0, -83.0)]: check(find((x, y), 3.2) is not None, "block standoff hole at (%.1f, %.1f)" % (x, y))
# A09, 26 September 2026 (MESHSAT-1357 round 4): THE CLAMP SITES ARE BOARD A'S, READ FROM BOARD A. This list was a literal
# ending at 102 while board A's LORA receptacle has been at 100 since 7 September (appendix 32.58), and the gate enforced
# the stale number for nineteen days: the two boards could disagree by twice the nest's float and both gates pass. The
# sites are now PARSED (ast, never grepped) from board A's two generators, which must agree with each other, and a
# board whose clamp holes are not at A's X and A's Y is refused. Absence is never a pass: an unreadable RF_X fails.
import ast as _ast
def _a_const(fname, name):
    """The literal value of a top-level `name = ...` (or `name, other = ...`) in a board A generator, or None."""
    try:
        tree = _ast.parse(open(_bo.path.join(_bo.path.dirname(_bo.path.abspath(__file__)), fname), encoding="utf-8").read())
    except Exception:
        return None
    for n in tree.body:
        if not isinstance(n, _ast.Assign): continue
        for t in n.targets:
            if isinstance(t, _ast.Name) and t.id == name:
                try: return _ast.literal_eval(n.value)
                except Exception: return None
            if isinstance(t, _ast.Tuple) and isinstance(n.value, _ast.Tuple):
                for k, e in enumerate(t.elts):
                    if isinstance(e, _ast.Name) and e.id == name:
                        try: return _ast.literal_eval(n.value.elts[k])
                        except Exception: return None
    return None
_RF_A = _a_const("gen_pcb_a.py", "RF_X"); _RF_A3 = _a_const("gen_pcb_a3.py", "RF_X"); _RF_Y = _a_const("gen_pcb_a.py", "RF_Y")
check(isinstance(_RF_A, list) and len(_RF_A) == 11 and _RF_A == _RF_A3 and isinstance(_RF_Y, (int, float)),
      "board A's blind-mate sites read from its generators: gen_pcb_a.py RF_X %s, gen_pcb_a3.py RF_X %s, RF_Y %s" % (_RF_A, _RF_A3, _RF_Y))
for x in (_RF_A if isinstance(_RF_A, list) else []):
    cy = float(_RF_Y) if isinstance(_RF_Y, (int, float)) else -66.0
    check(find((float(x), cy - 10.0), 3.2) is not None and find((float(x), cy + 10.0), 3.2) is not None,
          "float clamp holes at X %.0f, on board A's receptacle (Y %.0f +- 10)" % (x, cy))
# 8 Sep 2026 (MESHSAT-862 Stage C): the intent gates (return path under the pair-class nets, decoupling loops, the rails of the intent file)
if any(t.GetClass() == "PCB_TRACK" and not t.IsLocked() for t in b.GetTracks()):
    import os as _os3, sys as _sys3; _sys3.path.insert(0, _os3.path.dirname(_os3.path.abspath(__file__))); import intent_checks as _ic
    # THE INTENT ITEMS ARE REPORTED HERE AND DECIDED BY THEIR OWN VERDICTS (16 September 2026). They are five
    # rules with five authorities (the return path, the return via, the decoupling loop, the rails, the rest)
    # and `intent_checks` already writes a verdict for each. Counting them in THIS gate's failure list as well
    # made one composite verdict fail every rule it is mapped to: board D routed 0 hard and 0 unrouted with a
    # single item open, one signal via short of a ground via, and that EMC item failed the MECHANICAL rule
    # MEC-001 on six boards through this gate. The same defect must not be counted twice under two authorities.
    _intent_fails = []
    def _intent_check(c, m):
        print(("PASS " if c else "FAIL ") + m)
        _intent_reported.append(m)
        if not c: _intent_fails.append(m)
    print(_ic.run(b, _intent_check, sys.argv[1]))
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails))
# The verdict is a file and the exit code, and the denominator travels with it: a bare "0 FAIL" is what a
# gate that ran, a gate that loaded an empty board and a gate whose checks were all skipped all print.
# MESHSAT-862, 11 Sep 2026.
import os as _osv, sys as _sysv
_sysv.path.insert(0, _osv.path.dirname(_osv.path.abspath(__file__)))
import verdict as _v
_nfp = len(list(b.GetFootprints()))
_sysv.exit(_v.write("check_pcb_e",
                    _v.INCONCLUSIVE if not _nfp else (_v.PASS if not fails else _v.FAIL),
                    counts={"fail": len(fails), "pass": len(checked) - len(fails), "footprints": _nfp,
                            "intent_items_reported": len(_intent_reported)},
                    denominator=len(checked),
                    evidence=fails,
                    inputs={"board": sys.argv[1]},
                    note="" if _nfp else "the board loaded with no footprints, so nothing here is a judgement of a board"))
