#!/usr/bin/env python3
"""Decision 42, checker item 1: for every declared decoupling entry of a board's intent file, the side the capacitor
sits on, the side of the part it serves, whether the capacitor's centre lies inside the part's courtyard box (under the
part), the capacitor's value and the rail pad to pin distance (the gate's own measure, intent_checks.py:252-253).
Text reader only (dec_geometry.footprints). Usage: dec_sides_decl.py <board.kicad_pcb> <intent.json>"""
import sys, json, math
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from dec_geometry import parse, footprints

b = parse(open(sys.argv[1], encoding="utf-8").read()); fps = footprints(b)
it = json.load(open(sys.argv[2]))
n_back = 0
for e in it.get("bypass", []):
    cap, part, pin = e["cap"], e["part"], str(e["pin"])
    C, P = fps.get(cap), fps.get(part)
    if not C or not P: print("%-5s %-5s pin %-3s not on this board" % (cap, part, pin)); continue
    pad = next((q for q in P["pads"] if q["num"] == pin), None)
    l, t, r, bt = P["cy"]
    under = l <= C["x"] <= r and t <= C["y"] <= bt
    rail = [q for q in C["pads"] if pad and q["net"] == pad["net"]]
    dg = round(math.hypot(rail[0]["x"] - pad["x"], rail[0]["y"] - pad["y"]), 2) if rail and pad else None
    if C["layer"] == "B.Cu": n_back += 1
    print("%-5s %-8s cap %-4s  %-5s %-28s part %-4s pin %-3s net %-12s under_part %-5s pad_to_pin %s"
          % (cap, C["value"][:8], C["layer"][0], part, P["value"][:28], P["layer"][0], pin, e.get("net", "")[:12], under, dg))
print("declared entries with the capacitor on B.Cu:", n_back)
