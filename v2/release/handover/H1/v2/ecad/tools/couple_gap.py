#!/usr/bin/env python3
"""The couple gap READ BACK off a placed board (15 September 2026, MESHSAT-862; the reviewer of the fifth B placement cycle:
"knobs_seen is the runner reciting its own knob dictionary; no artefact reads the applied couple gap back out of the placed
board"). A couple is the placer's own definition (gen_pcb_b3.py): two two-pad passives whose pad nets are each other's _P
and _N counterparts. For every couple the gap between the two parts' courtyard boxes is measured and the count, median,
smallest and largest gap are printed and returned, so a PLACE_COUPLE_GAP arm carries the number the board shows.

Usage: couple_gap.py <board.kicad_pcb> [--json]"""
import sys, os, json, statistics
import pcbnew


def couples(b):
    pins = {}
    for fp in b.GetFootprints():
        r = fp.GetReference()
        if r[:1] not in ("C", "R", "L") or fp.Pads().size() != 2: continue
        pins[r] = tuple(sorted(p.GetNetname().lstrip("/") for p in fp.Pads()))
    byn = {}
    for r, nn in pins.items(): byn.setdefault(nn, []).append(r)
    out = []; seen = set()
    for r, nn in pins.items():
        if r in seen or not all(x.endswith("_P") for x in nn): continue
        want = tuple(sorted(x[:-2] + "_N" for x in nn))
        for o in byn.get(want, []):
            if o != r and o not in seen: out.append((r, o)); seen.add(r); seen.add(o); break
    return out


def _box(fp, courtyard):
    bb = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd).BBox() if courtyard else fp.GetBoundingBox(False, False)
    if bb.GetWidth() == 0 or bb.GetHeight() == 0: bb = fp.GetBoundingBox(False, False)
    return bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6


def _gap(a, c):
    dx = max(0.0, max(a[0], c[0]) - min(a[2], c[2])); dy = max(0.0, max(a[1], c[1]) - min(a[3], c[3]))
    return round(max(dx, dy), 3)


def measure(path):
    """Two gaps per couple: between the parts' own boxes (pads and body, the packer's box, so PLACE_COUPLE_GAP reads back
    as itself) and between their courtyards (what the pre-router's leg has to cross)."""
    b = pcbnew.LoadBoard(path); fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
    body = []; crt = []
    for r, o in couples(b):
        if r not in fps or o not in fps: continue
        body.append(_gap(_box(fps[r], False), _box(fps[o], False))); crt.append(_gap(_box(fps[r], True), _box(fps[o], True)))
    if not body: return {"couples": 0}
    return {"couples": len(body), "median_mm": round(statistics.median(body), 3), "min_mm": min(body), "max_mm": max(body),
            "courtyard_median_mm": round(statistics.median(crt), 3), "courtyard_min_mm": min(crt)}


def main(a):
    m = measure(a[0])
    if "--json" in a: print(json.dumps(m)); return 0
    print("couple_gap: %d couple(s)%s" % (m["couples"], (", part-box gap median %.2f mm (%.2f to %.2f), courtyard gap median %.2f mm" % (m["median_mm"], m["min_mm"], m["max_mm"], m["courtyard_median_mm"])) if m["couples"] else ""))
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
