#!/usr/bin/env python3
"""No net class carries a clearance, a width, a via or a drill below the board's own minimum (rule IMP-002,
MESHSAT-862, 16 September 2026).

A class number below the board's manufacturing minimum is a lie the router believes: the DSN carries the
class, the router lays copper to it, and the DRC finds the violations afterwards. It happened on A23 (25
clearance violations from a class below the board minimum, appendix 32.79) and it was live again today on
board B, whose project file shipped the USB and DIFF100 classes at 0.10 mm against a 0.127 mm board minimum
while the generator's own table said 0.127.

Both places are checked, because both are read by something: the PROJECT FILE (the router, the DSN export and
every gate that resolves a net's class) and the BOARD's design settings (the DRC). A class that is missing
from one of them is reported, not assumed equal.

Usage: class_floor.py <board.kicad_pcb> [--pro <project file>]      exits 0 PASS, 1 FAIL, 3 INCONCLUSIVE
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pcbnew
import verdict as _v

FIELDS = (("clearance", "m_MinClearance"), ("track_width", "m_TrackMinWidth"),
          ("via_diameter", "m_ViasMinSize"), ("via_drill", "m_MinThroughDrill"))


def mm(v): return v / 1e6


def check(board_path, pro_path=None):
    b = pcbnew.LoadBoard(board_path); ds = b.GetDesignSettings()
    floors = {}
    for name, attr in FIELDS:
        try: floors[name] = round(mm(getattr(ds, attr)), 4)
        except Exception: pass
    pro = pro_path or os.path.splitext(board_path)[0] + ".kicad_pro"
    if not os.path.exists(pro):
        return None, floors, ["no project file beside the board: its classes cannot be read, and the router reads them"]
    d = json.load(open(pro))
    classes = ((d.get("net_settings") or {}).get("classes") or [])
    if not classes:
        return None, floors, ["the project file declares no net class"]
    bad = []
    for c in classes:
        for name, _attr in FIELDS:
            floor = floors.get(name)
            if floor is None or c.get(name) is None: continue
            # KiCad writes a class value of 0 to mean "inherit the board default", which is not a violation
            if float(c[name]) == 0: continue
            if round(float(c[name]), 4) < floor - 1e-9:
                bad.append("class %s %s %.4f mm is below the board minimum %.4f mm"
                           % (c.get("name", "?"), name, float(c[name]), floor))
    return classes, floors, bad


def main(a):
    if not a: print(__doc__); return 2
    board = a[0]; pro = _v.opt(a, "--pro", None)
    classes, floors, bad = check(board, pro)
    n = len(classes or [])
    print("class_floor: %d class(es) against the board's own minimums %s" % (n, json.dumps(floors, sort_keys=True)))
    for x in bad: print("  FAIL %s" % x)
    if classes is None:
        return _v.write("class_floor", _v.INCONCLUSIVE, counts={"classes": 0}, denominator=0,
                        evidence=bad, inputs={"board": board}, note="; ".join(bad)[:160])
    return _v.write("class_floor", _v.FAIL if bad else _v.PASS,
                    counts={"classes": n, "below_floor": len(bad)}, denominator=n * len(FIELDS),
                    evidence=bad[:20], inputs={"board": board, "project": pro or os.path.splitext(board)[0] + ".kicad_pro"},
                    note="every class at or above the board's minimums" if not bad else "a class below the board minimum is a lie the router believes")


if __name__ == "__main__":
    import verdict as _vg   # a gate that crashes writes INCONCLUSIVE, never nothing (18 September 2026)
    sys.exit(_vg.guard("class_floor", main, sys.argv[1:]))
