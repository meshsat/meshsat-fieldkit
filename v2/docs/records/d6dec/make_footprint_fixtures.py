#!/usr/bin/env python3
"""The pad sets of real lands, read from the committed board text, as fixtures for the fan selection (T1).

MESHSAT-1357, stream d6dec, 27 September 2026. It reads six committed boards with the text reader of the decision 42
record (v2/docs/records/rv-dec/dec_geometry.py, no pcbnew) and writes, for the parts DECOUPLING.md 8.1 T1 names as
fixtures, every pad's number, type, position in nanometres and whether it carries copper. The fixture is data: the
test that reads it needs no KiCad and no board.

Usage: make_footprint_fixtures.py <v2/ecad> <out.json>"""
import os, sys, json, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "rv-dec"))
import dec_geometry as g

WANT = [("pcb-a-power-a23/pcb-a-power.kicad_pcb", "A32", ["U4", "U29", "U2", "U3"]),
        ("pcb-b-compute-b19/pcb-b-compute.kicad_pcb", "B21", ["U82", "U3", "U41", "U25", "U27", "U103", "U10", "J_HDMI"]),
        ("pcb-d-aprs-d9/pcb-d-aprs.kicad_pcb", "D12", ["U15", "U5", "U6", "U4", "U11", "U7"]),
        ("pcb-e1-dock-e7/pcb-e1-dock.kicad_pcb", "E17", ["Q1", "U12"]),
        ("pcb-c-display-c8/pcb-c-display.kicad_pcb", "C24", ["U3", "U5", "U11"])]


def main(a):
    ecad, out = a[0], a[1]; rec = {"what": "pad sets of committed lands, for tests/test_decoupling_rules.py", "boards": {}, "parts": {}}
    for rel, phase, refs in WANT:
        p = os.path.join(ecad, rel); txt = open(p, encoding="utf-8").read()
        rec["boards"][phase] = {"file": rel, "sha256": hashlib.sha256(txt.encode("utf-8")).hexdigest(),
                                "escape_skip": sorted(g.escape_skip(p))}
        fps = g.footprints(g.parse(txt)[0] if isinstance(g.parse(txt)[0], list) else g.parse(txt))
        for r in refs:
            f = fps[r]
            rec["parts"]["%s:%s" % (phase, r)] = {
                "ref": r, "fpid": f["lib"], "layer": f["layer"], "value": f["value"][:60],
                "pads": [{"num": str(q["num"]).strip('"'), "type": q["type"], "cu": bool(q["cu"]),
                          "x_nm": int(round(q["x"] * 1e6)), "y_nm": int(round(q["y"] * 1e6))} for q in f["pads"]],
                "record": {"fan_today": g.needs_fan(f["pads"], False)[0], "fan_copper_term": g.needs_fan(f["pads"], True)[0],
                           "escaped": g.escaped(r, f, rec["boards"][phase]["escape_skip"]),
                           "fan_as_ruled": g.fan_as_ruled(r, f, rec["boards"][phase]["escape_skip"])}}
    with open(out, "w", encoding="utf-8") as fh: fh.write(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    for k, v in rec["parts"].items():
        print("%-12s %-44s pads %3d  %s" % (k, v["fpid"].split(":")[-1][:44], len(v["pads"]), v["record"]))
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
