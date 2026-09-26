#!/usr/bin/env python3
"""Decision 42, blocking item 1 of the checker (26 September 2026): which boards are ALREADY assembled on both sides.
Reads each committed .kicad_pcb as text (no pcbnew) and counts footprints per side by what they carry:
SMD = at least one copper smd pad and no plated hole; THT = at least one thru_hole pad; OTHER = neither (mechanical,
fiducial, logo, np holes only). Also prints each footprint's attr (smd / through_hole / board_only / exclude_from_bom / dnp).
Usage: dec_sides.py <board.kicad_pcb> [--list-back]"""
import sys, collections
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from dec_geometry import parse, kids, kid

def main(path, list_back=False):
    b = parse(open(path, encoding="utf-8").read())
    cnt = collections.Counter(); back = []
    for fp in kids(b, "footprint"):
        ref = val = ""
        for p in kids(fp, "property"):
            if len(p) > 2 and p[1] == "Reference": ref = p[2]
            if len(p) > 2 and p[1] == "Value": val = p[2]
        side = kid(fp, "layer")[1]
        lib = fp[1] if len(fp) > 1 and isinstance(fp[1], str) else ""
        attr = kid(fp, "attr"); attrs = attr[1:] if attr else []
        smd = tht = False
        for p in kids(fp, "pad"):
            typ = p[2]
            lays = kid(p, "layers")[1:] if kid(p, "layers") else []
            cu = any(l.endswith(".Cu") for l in lays)
            if typ == "thru_hole": tht = True
            elif typ == "smd" and cu: smd = True
        kind = "THT" if tht else ("SMD" if smd else "OTHER")
        cnt[(side, kind)] += 1
        if side == "B.Cu": back.append((ref, kind, val, lib, " ".join(attrs)))
    print(path)
    for side in ("F.Cu", "B.Cu"):
        print("  %s  SMD %3d  THT %3d  OTHER %3d" % (side, cnt[(side, "SMD")], cnt[(side, "THT")], cnt[(side, "OTHER")]))
    if list_back:
        for r in sorted(back, key=lambda r: (r[1], r[0])): print("    back:", *r)

if __name__ == "__main__":
    main(sys.argv[1], "--list-back" in sys.argv)
