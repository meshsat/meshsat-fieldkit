#!/usr/bin/env python3
"""Every via on the board is a via this process makes (rule VIA-001, MESHSAT-862, 16 September 2026).

A board's own design settings carry the minimum via diameter and the minimum drill it was designed to, and
they are what the DRC judges a via against. What nothing checked is the ANNULAR RING, the copper left around
the hole, which is the number a fabricator quotes and the one a via fails at: a 0.45 mm via on a 0.35 mm drill
has 0.05 mm of ring per side, and a process that guarantees 0.075 will not make it reliably.

WHAT THIS CHECKS, all of it off the board itself, so no number is invented here:
  * the via's diameter against the board's own minimum;
  * its drill against the board's own minimum;
  * its annular ring, (diameter - drill) / 2, against a floor;
  * VIA IN PAD, reported separately, because a via inside a pad is not a defect: it is a deliberate technique
    this project uses on exposed pads and fine-pitch escapes, and it carries a FABRICATION COST (filled and
    capped) that the order paperwork has to name. Reporting it is how that note gets written.

THE ANNULAR RING FLOOR is the only number here that does not come from the board, and it is declared per board
in `boards/<letter>.json` as `annular_min_mm`. Where a board declares none the check is INCONCLUSIVE rather
than passing at some figure this tool made up: the fabricator's own capability page is SOURCE_UNVERIFIED in
this registry, and a via floor asserted without it would be exactly the heuristic-as-law this audit exists to
remove.

Usage: via_audit.py <board.kicad_pcb> [--json]
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pcbnew
import verdict as _v
import signal_class


def _board_table(letter):
    p = os.path.join(HERE, "boards", "%s.json" % letter)
    return json.load(open(p, encoding="utf-8")) if letter and os.path.exists(p) else {}


def audit(path, annular_min=None):
    b = pcbnew.LoadBoard(path)
    ds = b.GetDesignSettings()
    mm = lambda v: v / 1e6
    floor_d = round(mm(ds.m_ViasMinSize), 4)
    floor_h = round(mm(ds.m_MinThroughDrill), 4)
    pads = [(p, p.GetBoundingBox()) for f in b.GetFootprints() for p in f.Pads()]
    small = []
    in_pad = []
    n = 0
    for t in b.GetTracks():
        if t.GetClass() != "PCB_VIA": continue
        n += 1
        d, h = round(mm(t.GetWidth()), 4), round(mm(t.GetDrill()), 4)
        ring = round((d - h) / 2.0, 4)
        pos = t.GetPosition()
        why = []
        if d < floor_d - 1e-9: why.append("diameter %.3f below the board's %.3f" % (d, floor_d))
        if h < floor_h - 1e-9: why.append("drill %.3f below the board's %.3f" % (h, floor_h))
        if annular_min is not None and ring < annular_min - 1e-9:
            why.append("annular ring %.3f below the declared %.3f" % (ring, annular_min))
        if why:
            small.append("via %s at (%.2f, %.2f): %s" % (t.GetNetname() or "(no net)",
                                                         mm(pos.x), mm(pos.y), "; ".join(why)))
        for p, bb in pads:
            if bb.Contains(pos) and p.GetNetname() == t.GetNetname():
                in_pad.append("%s.%s" % (p.GetParentFootprint().GetReference(), p.GetNumber())); break
    return dict(vias=n, floor_d=floor_d, floor_h=floor_h, annular_min=annular_min,
                bad=small, in_pad=sorted(set(in_pad)))


def main(argv):
    if not argv: print(__doc__); return 2
    path = argv[0]
    letter = signal_class.board_letter(path)
    tbl = _board_table(letter)
    amin = tbl.get("annular_min_mm")
    r = audit(path, amin)
    print("via_audit: %d via(s); the board's own minimums are %.3f mm diameter and %.3f mm drill; "
          "the annular floor is %s" % (r["vias"], r["floor_d"], r["floor_h"],
                                       ("%.3f mm, declared by board %s" % (amin, (letter or "?").upper())) if amin is not None
                                       else "NOT DECLARED by this board"))
    for x in r["bad"][:20]: print("  FAIL %s" % x)
    if r["in_pad"]:
        print("  via in pad on %d pad(s), which is deliberate here and is a FABRICATION NOTE, not a defect: %s%s"
              % (len(r["in_pad"]), ", ".join(r["in_pad"][:10]), " ..." if len(r["in_pad"]) > 10 else ""))
    if "--json" in argv: print(json.dumps(r, indent=1))
    if not r["vias"]:
        return _v.write("via_audit", _v.INCONCLUSIVE, denominator=0, inputs={"board": path},
                        note="the board carries no via, so nothing was judged")
    res = _v.FAIL if r["bad"] else (_v.PASS if amin is not None else _v.INCONCLUSIVE)
    return _v.write("via_audit", res,
                    counts={"vias": r["vias"], "below_floor": len(r["bad"]), "via_in_pad": len(r["in_pad"])},
                    denominator=r["vias"], evidence=r["bad"][:20],
                    inputs={"board": path, "annular_min_mm": amin},
                    note=("every via at or above the board's own minimums and the declared annular floor"
                          if res == _v.PASS else
                          ("this board declares no annular floor, so the ring was not judged: the fabricator's "
                           "capability page is unverified in the registry and a floor asserted without it would "
                           "be the heuristic-as-law this audit exists to remove" if res == _v.INCONCLUSIVE else
                           "a via below the process floor is a via the fabricator may not make")))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
