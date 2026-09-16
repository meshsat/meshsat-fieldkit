#!/usr/bin/env python3
"""PCB-D D8 numeric gate (MESHSAT-830): outline 100 x 80, four M3 standoff holes at (+-45, +-35), the connectors and the RF chain where gen_pcb_d3.py fixes them,
the RF nets on the right pads (exciter ANT to the relay, relay to the antenna SMA, pad to the drive U.FL, LPF to the output SMA), four copper layers, the SA868 footprint present."""
import sys, math, pcbnew
import os as _bo, sys as _bs; _bs.path.insert(0, _bo.path.dirname(_bo.path.abspath(__file__)))
import boardtable as _bt   # the copper layer count is a DECLARATION in boards/<letter>.json, never a
                           # literal here: six gates carried one, so a layer decision meant editing a
                           # gate, and two experiments came back with their only failure being the gate
                           # describing the previous decision (board A, 12 September; board C, today)
b = pcbnew.LoadBoard(sys.argv[1]); OX, OY = 100.0, 100.0; fails = []; checked = []; _intent_reported = []
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    checked.append(m)
    if not c: fails.append(m)
fps = {f.GetReference(): f for f in b.GetFootprints()}
bb = b.GetBoardEdgesBoundingBox(); w, h = bb.GetWidth() / 1e6, bb.GetHeight() / 1e6
check(abs(w - 100) < 0.3 and abs(h - 80) < 0.3, "outline 100 x 80 (got %.1f x %.1f)" % (w, h))
# THE COPPER LAYER COUNT IS A DECLARATION, NEVER A LITERAL (16 September 2026). A literal here meant a
# layer decision was a gate edit, and twice a measurement came back whose ONLY failure was the gate
# describing the previous decision: board A four layers on 12 September (510 of 511) and board C six
# layers on 16 September. Under the P0 ruling every board's count is open, so it lives in the board
# table with its reason and is read here; a board that declares none keeps the count written below.
_LAYERS = _bt.value("d", "copper_layers", 4)
check(b.GetCopperLayerCount() == _LAYERS, "%d copper layers as board D declares them" % _LAYERS)
for ref, (x, y) in (("H1", (-45, -35)), ("H2", (45, -35)), ("H3", (-45, 35)), ("H4", (45, 35))):
    f = fps.get(ref); p = case(f.GetPosition()) if f else None
    check(f is not None and abs(p[0] - x) < 0.05 and abs(p[1] - y) < 0.05, "standoff hole %s at (%d, %d)%s" % (ref, x, y, "" if f is None else " got %s" % (p,)))
for ref in ("J_HARN1", "J_PWR1", "J_HS1", "J_HS2", "J_USB3", "U2", "K1", "J_ANT", "J_PAIN", "J_PAOUT", "J_VGG", "U3", "U4", "U6", "U7", "U8", "U15", "U16", "L1", "L2"):
    check(ref in fps, "present %s" % ref)
check("U2" in fps and fps["U2"].GetFPIDAsString().endswith("NiceRF_SA868"), "U2 on the NiceRF_SA868 footprint")
SITES = {"J_HARN1": (-42, 8), "J_PWR1": (-42, -16), "J_ANT": (-31, -33), "K1": (-14, -26), "J_PAIN": (9, -29), "J_PAOUT": (35, -30), "J_VGG": (43.5, -22.5), "J_HS1": (46.5, 12), "J_HS2": (46.5, -12), "U2": (-15, 8)}
for ref, (x, y) in SITES.items():
    f = fps.get(ref)
    if f is None: continue
    fb = f.GetBoundingBox(False, False); cx, cy = case(pcbnew.VECTOR2I((fb.GetLeft() + fb.GetRight()) // 2, (fb.GetTop() + fb.GetBottom()) // 2))
    check(abs(cx - x) < 0.6 and abs(cy - y) < 0.6, "%s box centre at (%.1f, %.1f) got (%.1f, %.1f)" % (ref, x, y, cx, cy))
def netof(ref, pad):
    f = fps.get(ref)
    if f is None: return None
    for p in f.Pads():
        if p.GetNumber() == pad: return p.GetNetname().lstrip("/")
    return None
for a, b_, net in ((("U2", "12"), ("K1", "3"), "RF_SA"), (("K1", "6"), ("J_ANT", "1"), "RF_ANT"), (("K1", "2"), ("K1", "7"), "RF_RX"), (("K1", "4"), ("R54", "1"), "RF_PAD_IN"), (("R56", "2"), ("J_PAIN", "1"), "RF_DRV"),
                   (("J_PAOUT", "1"), ("L1", "1"), "RF_PAOUT"), (("L2", "2"), ("K1", "5"), "RF_LPF_OUT"), (("K1", "1"), ("D2", "1"), "+5V_D8"), (("U15", "1"), ("J_VGG", "1"), "VGG_SW")):
    na, nb = netof(*a), netof(*b_)
    check(na == net and nb == net, "%s: %s.%s and %s.%s on %s (got %s, %s)" % (net, a[0], a[1], b_[0], b_[1], net, na, nb))
# nothing on the underside under the exciter, the relay or the connectors (the standoffs press the board there)
for ref in ("U2", "K1", "J_HARN1", "J_HS1", "J_HS2"):
    f = fps.get(ref)
    if f is None: continue
    r = f.GetBoundingBox(False, False); under = [g.GetReference() for g in b.GetFootprints() if g.IsFlipped() and r.Contains(g.GetPosition())]
    check(not under, "no underside part under %s%s" % (ref, "" if not under else ": " + ",".join(under[:6])))
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
# 8 Sep 2026 (MESHSAT-862): the copper checks were wired into the A and P gates only, and they are what finds a pour the router
# has eaten to islands or a stitch via the fill retreated from. D9 ended a clean route with eleven such islands on its front ground pour.
import copper_checks as _cc2; print(_cc2.run(b, check))
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails))
# The verdict is a file and the exit code, and the denominator travels with it: a bare "0 FAIL" is what a
# gate that ran, a gate that loaded an empty board and a gate whose checks were all skipped all print.
# MESHSAT-862, 11 Sep 2026.
import os as _osv, sys as _sysv
_sysv.path.insert(0, _osv.path.dirname(_osv.path.abspath(__file__)))
import verdict as _v
_nfp = len(list(b.GetFootprints()))
_sysv.exit(_v.write("check_pcb_d",
                    _v.INCONCLUSIVE if not _nfp else (_v.PASS if not fails else _v.FAIL),
                    counts={"fail": len(fails), "pass": len(checked) - len(fails), "footprints": _nfp,
                            "intent_items_reported": len(_intent_reported)},
                    denominator=len(checked),
                    evidence=fails,
                    inputs={"board": sys.argv[1]},
                    note="" if _nfp else "the board loaded with no footprints, so nothing here is a judgement of a board"))
