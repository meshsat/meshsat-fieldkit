#!/usr/bin/env python3
"""Decision 42, 26 September 2026, check of the 16:42 version: which parts does the escape pass escape that the fan T1 specified
would not protect, and which fans does the ruled set add or remove against what the placers build today?

Three sets per board, read from the committed board TEXT (dec_geometry, no pcbnew):
  TODAY  bypass_slots._needs_fan as it runs (every SMD pad, paste apertures included; >= 8 pads, closest two <= 1.0 mm)
  T1     the same test on numbered copper pads only (T1 as the 16:42 version specified it)
  ESC    the parts escape.py escapes (is_fine at escape.py:34-42, less the J and ESCAPE_SKIP exemptions at :176-177)
and the set ruled after the check, RULED = T1 | ESC.

For every part escaped but outside T1 it also prints, per numbered copper pad with a net, the nearest via of that net on
the board and its distance from the pad centre: evidence that the escape pass laid vias there that a fan would protect.
Usage: dec_escset.py <board.kicad_pcb> ..."""
import sys, math
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from dec_geometry import parse, footprints, needs_fan, escaped, escape_skip, smd_min_pitch, kids, kid


def vias(board):
    names = {}
    for n in kids(board, "net"):
        if len(n) > 2: names[n[1]] = n[2]
    out = []
    for v in kids(board, "via"):
        at = kid(v, "at"); nn = kid(v, "net")
        net = names.get(nn[1], nn[1]) if nn else ""
        if nn and len(nn) > 2: net = nn[2]
        out.append((float(at[1]), float(at[2]), net))
    return out


for bp in sys.argv[1:]:
    b = parse(open(bp, encoding="utf-8").read()); fps = footprints(b); skip = escape_skip(bp); vs = vias(b)
    today = {r for r, f in fps.items() if needs_fan(f["pads"], False)[0]}
    t1 = {r for r, f in fps.items() if needs_fan(f["pads"], True)[0]}
    esc = {r for r, f in fps.items() if escaped(r, f, skip)}
    ruled = t1 | esc
    name = bp.split("/")[-2]
    print("== %s   ESCAPE_SKIP %s" % (name, sorted(skip) or "none"))
    print("   TODAY %d   T1 %d   ESC %d   RULED = T1 | ESC %d" % (len(today), len(t1), len(esc), len(ruled)))

    def desc(r):
        f = fps[r]; nsmd = sum(1 for p in f["pads"] if p["type"] == "smd")
        ncu = sum(1 for p in f["pads"] if p["type"] == "smd" and p["cu"] and p["num"] not in ("", '""'))
        return "%-8s %-40s %s  smd %2d (numbered copper %2d)  pitch %.3f" % (
            r, f["lib"].split(":")[-1][:40], f["layer"][0], nsmd, ncu, smd_min_pitch(f["pads"]))

    print("   escaped by escape.py but outside T1 (%d):" % len(esc - t1))
    for r in sorted(esc - t1):
        print("     " + desc(r) + ("   fanned TODAY" if r in today else "   not fanned today"))
        f = fps[r]
        for p in sorted((p for p in f["pads"] if p["type"] == "smd" and p["cu"] and p["num"] not in ("", '""') and p["net"]
                         and not p["net"].startswith("unconnected-")), key=lambda p: p["num"]):
            best = min(((math.hypot(x - p["x"], y - p["y"]), (x, y)) for x, y, n in vs if n == p["net"]), default=None)
            print("         pad %-3s %-18s nearest via of its net %s" % (p["num"], p["net"][:18], "%.2f mm" % best[0] if best else "none"))
    print("   T1 alone would drop from TODAY (%d):" % len(today - t1))
    for r in sorted(today - t1):
        print("     " + desc(r) + ("   ESCAPED, so RULED keeps its fan" if r in esc else "   not escaped, fan removed"))
    print("   RULED removes from TODAY (%d):" % len(today - ruled))
    for r in sorted(today - ruled): print("     " + desc(r))
    print("   RULED adds to TODAY (%d):" % len(ruled - today))
    for r in sorted(ruled - today): print("     " + desc(r))
    print("   fanned TODAY but not escaped (kept by T1's 1.0 mm term, as the 9 September D10 lesson asks) (%d): %s"
          % (len(t1 - esc), " ".join(sorted(t1 - esc))))
    print()
