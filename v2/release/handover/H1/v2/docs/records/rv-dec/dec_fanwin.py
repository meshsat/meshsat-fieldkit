#!/usr/bin/env python3
"""Decision 42, the own-pin window against the fan, per supply pin of named parts (MESHSAT-1357, 26 September 2026).

Reads a committed .kicad_pcb as text (no pcbnew) with dec_geometry's parser. For every footprint whose Value contains
one of the given part names, and every pad of it on a supply net (a net starting with '+', or containing VDD, 3V3,
1V0, 1V1, 1V2, 2V5, VCAP), it prints:
  pin_to_cy  : the pad centre's distance to the nearest courtyard edge on its own side
  win_0402   : the smallest pad-centre to capacitor-centre distance for an 0402 seated just outside the part's
               courtyard in front of that pin (the "own-pin window"), courtyard taken from this board's own 0402
  win_0603   : the same for this board's 0603 ("C" land)
  fan_0402 / fan_0603 : the smallest distance for a capacitor outside the fan (courtyard + 2.2 mm), the rule today
Distances are to the capacitor CENTRE with the capacitor's long axis parallel to the pin row (the orientation
that seats closest); the gate measures to the capacitor's rail PAD, which is closer by up to half the pad pitch.
Usage: dec_fanwin.py <board.kicad_pcb> <name> [<name> ...]"""
import sys, re, math, json
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import dec_geometry as G

SUPPLY = re.compile(r"^/?\+|VDD|3V3|1V0|1V1|1V2|2V5|VCAP|V33|V10|V11", re.I)

def cap_dims(fps, needle):
    for ref, f in fps.items():
        if ref.startswith("C") and needle in f["lib"]:
            w = f["cy"][2] - f["cy"][0]; h = f["cy"][3] - f["cy"][1]
            if abs((f["rot"] % 180) - 90) < 1: w, h = h, w
            return (max(w, h), min(w, h)), ref, f["lib"]
    return None, None, None

def main(a):
    bp, names = a[0], a[1:]
    b = G.parse(open(bp, encoding="utf-8").read()); fps = G.footprints(b)
    d0402, r0402, l0402 = cap_dims(fps, "0402"); d0603, r0603, l0603 = cap_dims(fps, "0603")
    print("capacitor courtyards read from this board: 0402 %s (%s, %s); 0603 %s (%s, %s)" % (d0402, r0402, l0402, d0603, r0603, l0603))
    out = []
    for ref, f in sorted(fps.items()):
        if not any(n.lower() in f["value"].lower() for n in names): continue
        l, t, r, bt = f["cy"]; fan_now, p_now = G.needs_fan(f["pads"], False)
        rows = []
        for p in f["pads"]:
            if not SUPPLY.search(p["net"] or ""): continue
            px, py = p["x"], p["y"]
            dl, dr, dt, db = px - l, r - px, py - t, bt - py
            side = min((dl, "L"), (dr, "R"), (dt, "T"), (db, "B"))
            pin_to_cy = side[0]
            res = {"pin": p["num"], "net": p["net"], "pin_to_cy": round(pin_to_cy, 3)}
            for tag, dims in (("0402", d0402), ("0603", d0603)):
                if not dims: continue
                half_short = dims[1] / 2.0          # long axis along the pin row, so the short half faces the pin
                res["win_" + tag] = round(pin_to_cy + half_short, 3)
                res["fan_" + tag] = round(pin_to_cy + 2.2 + half_short, 3)
            rows.append(res)
        if not rows: continue
        agg = {"ref": ref, "value": f["value"][:60], "lib": f["lib"].split(":")[-1], "fan_now": fan_now, "pitch": p_now,
               "supply_pads": len(rows)}
        for k in ("pin_to_cy", "win_0402", "fan_0402", "win_0603", "fan_0603"):
            vs = [x[k] for x in rows if k in x]
            if vs: agg[k] = [round(min(vs), 2), round(max(vs), 2)]
        out.append(agg)
        print("%-6s %-40s %-34s fan %s (%s) supply pads %3d  pin_to_cy %s  win_0402 %s  fan_0402 %s  win_0603 %s  fan_0603 %s"
              % (ref, agg["value"][:40], agg["lib"][:34], fan_now, p_now, len(rows), agg.get("pin_to_cy"), agg.get("win_0402"),
                 agg.get("fan_0402"), agg.get("win_0603"), agg.get("fan_0603")))
    return out

if __name__ == "__main__":
    o = main(sys.argv[1:])
    if "--json" in sys.argv: pass
