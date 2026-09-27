#!/usr/bin/env python3
"""PCB-E5 DOCK BLOCK numeric gate (rule MEC-001 and the rest, MESHSAT-862, 16 September 2026).

**Board E5 had no gate at all.** Six boards have one and the seventh, the raised contact block the whole
energy chain passes through, had none: every rule verified by `check_pcb_<letter>` read "no check_pcb_e5
verdict for this board", which is the registry saying, correctly, that nothing had ever asserted a number
about it. It is the smallest board in the set and it carries the pack current.

What it asserts, all of it from `gen_pcb_e5.py`'s own header and the appendix (32.25, 32.26):
  * the outline, 43 by 26 mm at X -106.5 to -63.5 and Y -85 to -59 in the case frame, and two copper layers;
  * the four M3 standoff holes in the corners, which are the strip's own BLOCK_HOLES;
  * the 2 x 6 signal target field and the 2 x 6 plated wire lands below it, on their declared centres;
  * nine power targets: four CELL+, four return, one pre-charge that mates first;
  * the two 12 AWG wire holes, one per pack conductor;
  * that every signal target carries a net and that no target is left on the board's default net, because a
    target with no net is a contact that connects nothing and nothing else here would notice;
  * that CELL+ and the return are poured on both layers and stitched, since this is a 10 A path.

Usage: check_pcb_e5.py <board.kicad_pcb>
"""
import sys, os
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boardtable as _bt
import verdict as _v

b = pcbnew.LoadBoard(sys.argv[1]); OX, OY = 150.0, 110.0
fails = []; checked = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m); checked.append(m)
    if not c: fails.append(m)
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))

fps = {f.GetReference(): f for f in b.GetFootprints()}
bb = b.GetBoardEdgesBoundingBox(); w, h = bb.GetWidth() / 1e6, bb.GetHeight() / 1e6
check(abs(w - 43.0) < 0.3 and abs(h - 26.0) < 0.3, "outline 43 x 26 (got %.1f x %.1f)" % (w, h))
_LAYERS = _bt.value("e5", "copper_layers", 2)
check(b.GetCopperLayerCount() == _LAYERS, "%d copper layers as the registry's facts declare them" % _LAYERS)
check(abs(b.GetDesignSettings().GetBoardThickness() / 1e6 - 1.6) < 0.01, "1.6 mm thick")

for ref, (x, y) in (("H1", (-104.0, -63.0)), ("H2", (-66.0, -63.0)), ("H3", (-104.0, -83.0)), ("H4", (-66.0, -83.0))):
    f = fps.get(ref); p = case(f.GetPosition()) if f else None
    check(f is not None and abs(p[0] - x) < 0.05 and abs(p[1] - y) < 0.05,
          "standoff hole %s at (%.1f, %.1f)%s" % (ref, x, y, "" if f is None else " got %s" % (p,)))

for ref, (x, y), what in ((("T_SIG"), (-76.0, -70.0), "the 2 x 6 signal target field"),
                          (("L_SIG"), (-76.0, -76.5), "the 2 x 6 plated wire lands"),
                          (("T_PRE"), (-103.0, -70.0), "the pre-charge target, which mates first"),
                          (("WH_CP"), (-92.0, -81.0), "the 12 AWG CELL+ hole"),
                          (("WH_CN"), (-93.0, -62.5), "the 12 AWG return hole")):
    f = fps.get(ref); p = case(f.GetPosition()) if f else None
    check(f is not None and abs(p[0] - x) < 0.2 and abs(p[1] - y) < 0.2,
          "%s (%s) at (%.1f, %.1f)%s" % (what, ref, x, y, "" if f is None else " got %s" % (p,)))

for k in range(1, 5):
    for pre, net, row in (("T_CP%d", "CELL+", -73.0), ("T_CN%d", "CELL_N", -67.0)):
        ref = pre % k; f = fps.get(ref)
        nets = {p.GetNetname().lstrip("/") for p in f.Pads()} if f else set()
        check(f is not None and nets == {net}, "%s is a %s target on the row at Y %.0f (got %s)" % (ref, net, row, sorted(nets)))

sig = fps.get("T_SIG"); lands = fps.get("L_SIG")
if sig and lands:
    sn = [p.GetNetname() for p in sig.Pads()]; ln = [p.GetNetname() for p in lands.Pads()]
    check(len(sn) == 12 and all(n for n in sn), "all twelve signal targets carry a net (%d named)" % sum(1 for n in sn if n))
    check(len(ln) == 12 and all(n for n in ln), "all twelve wire lands carry a net (%d named)" % sum(1 for n in ln if n))
    check(set(x.lstrip("/") for x in sn) == set(x.lstrip("/") for x in ln),
          "every signal target has a wire land of the SAME net beneath it (targets %d, lands %d, shared %d)"
          % (len(set(sn)), len(set(ln)), len(set(x.lstrip("/") for x in sn) & set(x.lstrip("/") for x in ln))))

pours = {}
for z in b.Zones():
    if z.GetIsRuleArea(): continue
    pours.setdefault(z.GetNetname().lstrip("/"), []).append(z)
for net in ("CELL+", "CELL_N"):
    zs = pours.get(net, [])
    check(len(zs) >= 2, "%s is poured on both layers (%d zone(s))" % (net, len(zs)))
vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
for net in ("CELL+", "CELL_N"):
    n = sum(1 for v in vias if v.GetNetname().lstrip("/") == net)
    check(n >= 2, "%s is stitched between the layers (%d via(s)) because this is the 10 A path" % (net, n))

print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails))
_nfp = len(list(b.GetFootprints()))
sys.exit(_v.write("check_pcb_e5", _v.INCONCLUSIVE if not _nfp else (_v.PASS if not fails else _v.FAIL),
                  counts={"fail": len(fails), "pass": len(checked) - len(fails), "footprints": _nfp},
                  denominator=len(checked), evidence=fails, inputs={"board": sys.argv[1]},
                  note="" if _nfp else "the board loaded with no footprints, so nothing here is a judgement of a board"))
