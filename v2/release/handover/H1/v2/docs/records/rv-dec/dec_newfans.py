#!/usr/bin/env python3
"""Decision 42, 26 September 2026, check of the 16:42 version: what do the fans the ruled set ADDS (parts the escape pass
escapes that today's _needs_fan does not fan) cost the declared capacitors? For every declared entry of a board's
committed intent file, whose capacitor is on the board, this reports whether the capacitor's courtyard overlaps the fan
box of an added part other than the one it serves (then today's seat would be refused by the ruled placers), and
whether its own part is one of the added ones. Also counts every capacitor footprint (reference C...) on the board whose
courtyard overlaps an added fan box on the same side. Text reader; usage: dec_newfans.py <board.kicad_pcb> <intent.json>"""
import sys, json
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from dec_geometry import parse, footprints, needs_fan, fan_as_ruled, escape_skip
bp, ip = sys.argv[1], sys.argv[2]
fps = footprints(parse(open(bp, encoding="utf-8").read())); skip = escape_skip(bp)
added = {r: f for r, f in fps.items() if fan_as_ruled(r, f, skip) and not needs_fan(f["pads"], False)[0]}
def box(f): l, t, r, b = f["cy"]; return (l - 2.2, t - 2.2, r + 2.2, b + 2.2)
def ov(a, b): return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
it = json.load(open(ip)); hits = []; own = []
for e in it.get("bypass", []):
    C = fps.get(e["cap"]); P = fps.get(e["part"])
    if not C or not P: continue
    if e["part"] in added: own.append((e["cap"], e["part"]))
    h = [r for r, f in added.items() if r != e["part"] and ov(C["cy"], box(f))]
    if h: hits.append((e["cap"], e["part"], e["pin"], h, C["layer"][0]))
allc = sorted(r for r, f in fps.items() if r.startswith("C") and any(ov(f["cy"], box(g)) for g2, g in added.items() if g["layer"] == f["layer"]))
print("%s: added fans %d; declared entries whose part gains a fan: %s; declared capacitors whose present seat lies in an added fan box of another part: %s; every C footprint in an added box on its own side: %d"
      % (bp.split("/")[-2], len(added), own or "none", hits or "none", len(allc)))
