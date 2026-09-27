#!/usr/bin/env python3
"""A ground-via grid laid BEFORE the route, so that rule 2 of the return-current ruling (a ground via within 1.5 mm of every
signal via, owner ruling 15 September 2026 20:15 CEST, appendix 32.198) holds by construction rather than by a fixer that
looks for room after the router has taken it (on D12's In2-plane route the fixer found a site for 138 of 185 signal vias and
NONE for the other 47: all 64 candidates on other-net copper, 15 September 2026 20:12 UTC).

A square grid of pitch P puts every point of the board within P / sqrt(2) of a grid via, so P = 2.1 mm covers the 1.5 mm
rule everywhere the grid can be laid. Where it cannot be laid the fixer still runs after the route. A grid via is placed
only where, on the placed board (escapes, fanout and pair copper already down):
  - the site is free of other-net pads, tracks and vias at the board's own via and clearance (return_via._site_free);
  - the site lies inside a filled GND zone on some layer (return_via._in_gnd_fill): a ground via outside all ground copper
    connects nothing, and the test also keeps the grid inside the outline;
  - the site is outside every filled zone of another net on every layer: a via through a rail's locked band or island
    slices copper the rail rules sized (ruling 15's 1.2 mm band on D), where a via in a ground PLANE only takes an anti-pad;
  - the site is outside every rule area that forbids vias;
  - no fine-pitch fan is within FAN_MM (return_via's own exemption: those vias are exempt and the fan needs its room);
  - no ground via already stands within half a pitch (the escapes' and stitches' own vias count as grid points).
The vias are locked through vias of the board's minimum size on GND. drc.sh then judges the board once and any grid via in
a hard violation is removed. Prints `gnd_grid: N candidate points, P placed, skipped: copper C, no ground fill F, other-net
zone Z, via keep-out K, fine-pitch fan N2, ground via near G; removed by the DRC R`.

Usage: gnd_grid.py <board.kicad_pcb> [--pitch 2.1] [--dry]      declared per board as "gnd_grid": {"pitch": 2.1} in boards/<letter>.json"""
import os, sys, math, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew, hardset, return_via
import boardorder

PITCH_MM = 2.1
TOOLS = os.path.dirname(os.path.abspath(__file__))


def _mm(v): return v / 1e6


def main(a):
    path = a[0]; pitch = float(a[a.index("--pitch") + 1]) if "--pitch" in a else PITCH_MM; dry = "--dry" in a
    if dry:
        tmp = os.path.splitext(path)[0] + "-gnd_grid-dry.kicad_pcb"; shutil.copy(path, tmp)
        for e in (".kicad_pro", ".kicad_prl"):
            if os.path.exists(os.path.splitext(path)[0] + e): shutil.copy(os.path.splitext(path)[0] + e, os.path.splitext(tmp)[0] + e)
        path = tmp; print("gnd_grid: dry run on %s" % tmp)
    b = pcbnew.LoadBoard(path); ds = b.GetDesignSettings()
    gnd = b.FindNet("GND")
    if gnd is None: print("gnd_grid: the board has no GND net; nothing placed"); return 0
    vd, vdr = max(0.4, _mm(ds.m_ViasMinSize)), max(0.2, _mm(ds.m_MinThroughDrill)); clr = max(_mm(ds.m_MinClearance), 0.127)
    try: pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    except Exception: pass
    fine = return_via._fine_pads(b)
    gnd_vias = [(_mm(t.GetPosition().x), _mm(t.GetPosition().y)) for t in boardorder.tracks(b) if t.GetClass() == "PCB_VIA" and t.GetNetname().lstrip("/") == "GND"]
    other_zones = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname().lstrip("/") != "GND" and z.GetFilledArea() > 0]
    via_keepouts = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
    bb = b.GetBoardEdgesBoundingBox(); x0, y0, x1, y1 = _mm(bb.GetLeft()), _mm(bb.GetTop()), _mm(bb.GetRight()), _mm(bb.GetBottom())
    skipped = {"copper": 0, "no ground fill": 0, "other-net zone": 0, "via keep-out": 0, "fine-pitch fan": 0, "ground via near": 0}
    new = []; n_cand = 0; half = pitch / 2.0
    cells = {}
    for gx, gy in gnd_vias: cells.setdefault((int(gx // half), int(gy // half)), []).append((gx, gy))
    def gnd_near(x, y):
        cx, cy = int(x // half), int(y // half)
        return any(math.hypot(x - gx, y - gy) <= half for i in (-1, 0, 1) for j in (-1, 0, 1) for gx, gy in cells.get((cx + i, cy + j), []))
    y = y0 + pitch / 2.0
    while y < y1:
        x = x0 + pitch / 2.0
        while x < x1:
            n_cand += 1; p = pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)); ok = True
            if gnd_near(x, y): skipped["ground via near"] += 1; ok = False
            elif return_via._near((x, y), fine, return_via.FAN_MM): skipped["fine-pitch fan"] += 1; ok = False
            elif any(k.Outline().Contains(p) for k in via_keepouts): skipped["via keep-out"] += 1; ok = False
            elif any(z.GetFilledPolysList(L).Contains(p) for z in other_zones for L in z.GetLayerSet().Seq()): skipped["other-net zone"] += 1; ok = False
            elif not return_via._in_gnd_fill(b, x, y, vd): skipped["no ground fill"] += 1; ok = False
            elif not return_via._site_free(b, x, y, vd, clr, "GND"): skipped["copper"] += 1; ok = False
            if ok:
                v = pcbnew.PCB_VIA(b); v.SetPosition(p); v.SetDrill(int(vdr * 1e6)); v.SetWidth(int(vd * 1e6)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(gnd); v.SetLocked(True)
                b.Add(v); new.append((round(x, 3), round(y, 3))); cells.setdefault((int(x // half), int(y // half)), []).append((x, y))
            x += pitch
        y += pitch
    pcbnew.SaveBoard(path, b)
    removed = 0
    # The DRC judges the grid and every via it names comes off, and it is asked AGAIN until it names none (15 September 2026
    # 23:55 CEST, C on six layers: one pass removed 222 and left 104, every one a via inside a rule area, because a single
    # report is not proof that what is left is clean).
    if new:
        od = os.path.join(os.path.dirname(os.path.abspath(path)), "out"); os.makedirs(od, exist_ok=True)
        rep = os.path.join(od, os.path.basename(os.path.splitext(path)[0]) + "-gnd_grid-drc.json")
        left = {pt for pt in new}
        for _ in range(3):
            subprocess.run([os.path.join(TOOLS, "drc.sh"), path, rep], capture_output=True, text=True)
            d = hardset.load(rep); bad = return_via._own_hard(d, sorted(left))
            if not bad: break
            b = pcbnew.LoadBoard(path)
            for t in list(boardorder.tracks(b)):   # the grid itself is walked in x and y; board order decides nothing here
                if t.GetClass() == "PCB_VIA" and t.GetNetname().lstrip("/") == "GND" and (round(_mm(t.GetPosition().x), 3), round(_mm(t.GetPosition().y), 3)) in bad: b.Remove(t); removed += 1
            pcbnew.SaveBoard(path, b); left -= bad
    print("gnd_grid: pitch %.2f mm, via %.2f/%.2f, %d candidate points, %d placed, skipped: %s; removed by the DRC %d" % (pitch, vd, vdr, n_cand, len(new) - removed, ", ".join("%s %d" % kv for kv in skipped.items()), removed))
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
