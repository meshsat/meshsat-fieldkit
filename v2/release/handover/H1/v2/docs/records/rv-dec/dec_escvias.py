#!/usr/bin/env python3
"""Decision 42, 26 September 2026, check of the 16:42 version: does the fan box (courtyard bounding box grown by 2.2 mm) of every part
escape.py escapes contain that part's escape vias? For each escaped part, each numbered copper pad on a signal net (not
GND, not a +rail, so a neighbour's via of a shared net is not mistaken for this part's) and the nearest LOCKED via of that
net within 3.5 mm of the pad centre (escape.py locks its escapes, escape.py:4), this prints whether that via lies inside
the part's fan box. Text reader only. Usage: dec_escvias.py <board.kicad_pcb> ..."""
import sys, math
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from dec_geometry import parse, footprints, escaped, escape_skip, kids, kid
for bp in sys.argv[1:]:
    b = parse(open(bp, encoding="utf-8").read()); fps = footprints(b); skip = escape_skip(bp)
    names = {n[1]: n[2] for n in kids(b, "net") if len(n) > 2}
    vs = []
    for v in kids(b, "via"):
        lk = kid(v, "locked"); at = kid(v, "at"); nn = kid(v, "net")
        if not (lk and lk[1] == "yes") or not nn: continue
        vs.append((float(at[1]), float(at[2]), nn[2] if len(nn) > 2 else names.get(nn[1], nn[1])))
    n_in = n_out = 0; outs = []
    for r, f in sorted(fps.items()):
        if not escaped(r, f, skip): continue
        l, t, rr, bt = f["cy"]; box = (l - 2.2, t - 2.2, rr + 2.2, bt + 2.2)
        for p in f["pads"]:
            if p["type"] != "smd" or not p["cu"] or p["num"] in ("", '""') or not p["net"]: continue
            nt = p["net"]
            if nt in ("GND",) or nt.startswith("/+") or nt.startswith("unconnected-") or nt.startswith("+"): continue
            c = [(math.hypot(x - p["x"], y - p["y"]), x, y) for x, y, n in vs if n == nt]
            c = [q for q in c if q[0] <= 3.5]
            if not c: continue
            d, x, y = min(c)
            if box[0] <= x <= box[2] and box[1] <= y <= box[3]: n_in += 1
            else: n_out += 1; outs.append("%s.%s %s %.2f mm" % (r, p["num"], nt, d))
    print("%s: escaped parts' signal-pad escape vias inside their own fan box %d, outside %d %s"
          % (bp.split("/")[-2], n_in, n_out, outs[:8]))
