#!/usr/bin/env python3
"""Decision 42, cycle 3: is every part board B's PLACE_NO_UNDER_FINE would treat (gen_pcb_b3.is_fine, lines 356-364,
with 16 or more SMD pads, line 396) inside the fanned set as ruled after the check of the 16:42 version (26 September 2026) (dec_geometry.fan_as_ruled: escape.py's escaped
set, or _needs_fan on numbered copper pads)? Text reader; usage: dec_finesets.py <board.kicad_pcb> ..."""
import sys, re, math
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from dec_geometry import parse, footprints, needs_fan, fan_as_ruled, escape_skip
for bp in sys.argv[1:]:
    fps = footprints(parse(open(bp, encoding="utf-8").read())); skip = escape_skip(bp)
    fine16, fanned = set(), set()
    for ref, f in fps.items():
        smd = [p for p in f["pads"] if p["type"] == "smd"]
        pts = [(p["x"], p["y"]) for p in smd]
        best = min((math.hypot(a[0] - b[0], a[1] - b[1]) for i, a in enumerate(pts) for b in pts[i + 1:] if a != b), default=1e9)
        is_fine = bool(re.search(r"SOT-23-[68]|SOT-583|TSOT-23-6", f["lib"])) or best <= 0.7 + 1e-9
        if is_fine and len(smd) >= 16: fine16.add(ref)
        if fan_as_ruled(ref, f, skip): fanned.add(ref)
    print("%s: PLACE_NO_UNDER_FINE set %d, fanned set %d, in the first and not the second: %s"
          % (bp.split("/")[-2], len(fine16), len(fanned), sorted(fine16 - fanned) or "none"))
