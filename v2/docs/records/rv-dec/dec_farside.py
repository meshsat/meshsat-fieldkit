#!/usr/bin/env python3
"""Decision 42, checker cycle 3 (26 September 2026): what board B's underside rule leaves of the far-side seat (D5).

Board B's rule as written (gen_pcb_b3.py:155): underside decoupling "never beneath a fine-pitch part whose escapes need
the vias"; appendix line 3010: "never under a fine-pitch part (its escapes need the vias) and never under a through-hole
header". Kept as written, a far-side seat is refused inside the fan box of any part the escape pass fans (courtyard
bounding box grown by 2.2 mm, bypass_slots._fan_box), whichever side that part is on, and over any through-hole part's
courtyard. The fanned set is the one ruled after the check of the 16:42 version (26 September 2026) (dec_geometry.fan_as_ruled): every
part escape.py escapes (its is_fine, less the J and ESCAPE_SKIP exemptions), together with every part _needs_fan fans
when counted on numbered copper pads (T1). The 16:42 version used T1's set alone, which left out the WSON-6-1EP,
MLPD-6 and SOT-23-6 parts escape.py escapes.

For each declared decoupling entry of a two-sided board's intent file this prints:
  - whether the part it serves is fanned (then the far side under the pin is inside that part's own fan box),
  - whether the pin lies inside ANOTHER part's fan box or a through-hole courtyard (then the far side under the pin
    is refused as well),
  - for a capacitor already on the side opposite its part, whether its courtyard overlaps any fan box or through-hole
    courtyard (then its present seat is inadmissible under the rule), and which part's.
And, set-wide for the board, how many SMD footprints on each side overlap a fan box of a part on the other side.
Text reader only (dec_geometry.parse/footprints/needs_fan); it decides nothing.
Usage: dec_farside.py <board.kicad_pcb> <intent.json>"""
import sys, json
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from dec_geometry import parse, footprints, needs_fan, fan_as_ruled, escape_skip

FAN = 2.2

def overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]

def inside(x, y, b):
    return b[0] <= x <= b[2] and b[1] <= y <= b[3]

b = parse(open(sys.argv[1], encoding="utf-8").read()); fps = footprints(b); skip = escape_skip(sys.argv[1])
it = json.load(open(sys.argv[2]))
fanned, tht = {}, {}
for ref, f in fps.items():
    if any(p["type"] == "thru_hole" for p in f["pads"]):
        tht[ref] = f["cy"]
    if fan_as_ruled(ref, f, skip):
        l, t, r, bt = f["cy"]; fanned[ref] = ((l - FAN, t - FAN, r + FAN, bt + FAN), f["layer"])
print("fanned parts as ruled (escape.py's escaped set, or numbered copper pads >= 8 at <= 1.0 mm): %d (F %d, B %d); through-hole parts: %d"
      % (len(fanned), sum(1 for v in fanned.values() if v[1] == "F.Cu"), sum(1 for v in fanned.values() if v[1] == "B.Cu"), len(tht)))

# set-wide: SMD footprints overlapping the fan box of a part on the OTHER side
cross = {"F.Cu": [], "B.Cu": []}
for ref, f in fps.items():
    if ref in fanned or not any(p["type"] == "smd" and p["cu"] for p in f["pads"]) or any(p["type"] == "thru_hole" for p in f["pads"]):
        continue
    hits = [g for g, (box, side) in fanned.items() if side != f["layer"] and overlap(f["cy"], box)]
    if hits: cross[f["layer"]].append((ref, hits))
for side in ("B.Cu", "F.Cu"):
    other = "F.Cu" if side == "B.Cu" else "B.Cu"
    print("SMD footprints on %s overlapping the fan box of a %s part: %d" % (side, other, len(cross[side])))

rows = {"fanned_part": 0, "under_pin_in_other_fan": 0, "under_pin_open": 0, "not_on_board": 0}
print()
for e in it.get("bypass", []):
    cap, part, pin = e["cap"], e["part"], str(e["pin"])
    C, P = fps.get(cap), fps.get(part)
    if not C or not P: rows["not_on_board"] += 1; print("%-5s %-6s pin %-3s not on this board" % (cap, part, pin)); continue
    pad = next((q for q in P["pads"] if q["num"] == pin), None)
    if pad is None: rows["not_on_board"] += 1; print("%-5s %-6s pin %-3s no such pin" % (cap, part, pin)); continue
    own_fan = part in fanned
    other_fan = [g for g, (box, _s) in fanned.items() if g != part and inside(pad["x"], pad["y"], box)]
    other_tht = [g for g, cy in tht.items() if g != part and inside(pad["x"], pad["y"], cy)]
    if own_fan: verdict = "far side under the pin REFUSED: its own part is fanned"; rows["fanned_part"] += 1
    elif other_fan or other_tht: verdict = "far side under the pin REFUSED: inside %s" % ", ".join(other_fan + other_tht); rows["under_pin_in_other_fan"] += 1
    else: verdict = "far side under the pin open"; rows["under_pin_open"] += 1
    seat = ""
    if C["layer"] != P["layer"]:
        cf = [g for g, (box, _s) in fanned.items() if overlap(C["cy"], box)]
        ct = [g for g, cy in tht.items() if overlap(C["cy"], cy)]
        seat = "   | its present far-side seat: %s" % ("INADMISSIBLE, overlaps the fan box of %s" % ", ".join(cf + ct) if (cf or ct) else "clear of every fan box and through-hole courtyard")
    print("%-5s %-9s %-6s %-30s pin %-3s %s%s" % (cap, C["value"][:9], part, P["lib"].split(":")[-1][:30], pin, verdict, seat))
print()
print("summary:", json.dumps(rows))
