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

THE ANNULAR RING FLOORS are the only numbers here that do not come from the board, they are declared per board
in `boards/<letter>.json`, and THERE ARE TWO OF THEM because the fabricator states two (16 September 2026):

  * `annular_min_mm` is the PTH ANNULAR RING row and it binds a PLATED COMPONENT HOLE, a through-hole part's
    pad or a mounting pad that carries copper: multilayer 1 oz recommended 0.20 mm, absolute minimum 0.15.
  * `via_ring_min_mm` is what the VIA rows leave, and it binds a VIA: the same document's smallest via is
    0.25 mm of copper on a 0.15 mm hole, which is 0.05 mm of ring per side.

Applying the first row to a via is the defect this split exists to remove, and it is not hypothetical: on 16
September board D12 routed 0 hard and 0 unrouted and was refused for ONE via at 0.125 mm of ring, a 0.45/0.20
via that is nearly two and a half times the fabricator's own via minimum. Read the other way the two rows
contradict each other, because no via at the stated minimum 0.25/0.15 can carry 0.20 mm of ring, so the
annular row cannot be about vias. Where a board declares neither floor the ring is INCONCLUSIVE rather than
passing at some figure this tool made up.

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


def audit(path, annular_min=None, via_ring_min=None):
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
        if via_ring_min is not None and ring < via_ring_min - 1e-9:
            why.append("annular ring %.3f below the declared via floor %.3f" % (ring, via_ring_min))
        if why:
            small.append("via %s at (%.2f, %.2f): %s" % (t.GetNetname() or "(no net)",
                                                         mm(pos.x), mm(pos.y), "; ".join(why)))
        for p, bb in pads:
            if bb.Contains(pos) and p.GetNetname() == t.GetNetname():
                in_pad.append("%s.%s" % (p.GetParentFootprint().GetReference(), p.GetNumber())); break
    # THE PLATED COMPONENT HOLES, which is what the fabricator's annular ring row is about. A non-plated hole
    # has its own row and usually no copper at all here, so it is counted and left unjudged rather than failed
    # for a ring it was never meant to have.
    holes = 0; npth = 0; thin = []
    for f in b.GetFootprints():
        for p in f.Pads():
            dx, dy = mm(p.GetDrillSizeX()), mm(p.GetDrillSizeY())
            if dx <= 0 and dy <= 0: continue
            try: plated = p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH
            except AttributeError: plated = True
            if not plated: npth += 1; continue
            holes += 1
            sx, sy = mm(p.GetSizeX()), mm(p.GetSizeY())
            ring = round(min(sx - dx, sy - dy) / 2.0, 4)
            if annular_min is not None and ring < annular_min - 1e-9:
                thin.append("plated hole %s.%s (%s) at (%.2f, %.2f): annular ring %.3f below the declared %.3f"
                            % (f.GetReference(), p.GetNumber(), p.GetNetname() or "(no net)",
                               mm(p.GetPosition().x), mm(p.GetPosition().y), ring, annular_min))
    return dict(vias=n, floor_d=floor_d, floor_h=floor_h, annular_min=annular_min, via_ring_min=via_ring_min,
                bad=small, in_pad=sorted(set(in_pad)), plated_holes=holes, npth_holes=npth, thin_pads=thin)


def main(argv):
    if not argv: print(__doc__); return 2
    path = argv[0]
    letter = signal_class.board_letter(path)
    tbl = _board_table(letter)
    amin = tbl.get("annular_min_mm")
    vmin = tbl.get("via_ring_min_mm")
    r = audit(path, amin, vmin)
    print("via_audit: %d via(s) and %d plated component hole(s) (%d non-plated, not judged); the board's own "
          "minimums are %.3f mm diameter and %.3f mm drill; the via ring floor is %s and the plated hole ring "
          "floor is %s"
          % (r["vias"], r["plated_holes"], r["npth_holes"], r["floor_d"], r["floor_h"],
             ("%.3f mm" % vmin) if vmin is not None else "NOT DECLARED by this board",
             ("%.3f mm" % amin) if amin is not None else "NOT DECLARED by this board"))
    for x in r["bad"][:20]: print("  FAIL %s" % x)
    for x in r["thin_pads"][:20]: print("  FAIL %s" % x)
    if r["in_pad"]:
        print("  via in pad on %d pad(s), which is deliberate here and is a FABRICATION NOTE, not a defect: %s%s"
              % (len(r["in_pad"]), ", ".join(r["in_pad"][:10]), " ..." if len(r["in_pad"]) > 10 else ""))
    if "--json" in argv: print(json.dumps(r, indent=1))
    if not r["vias"]:
        _v.write("via_annular", _v.INCONCLUSIVE, denominator=0, inputs={"board": path}, quiet=True,
                 note="the board carries no via, so nothing was judged")
        return _v.write("via_audit", _v.INCONCLUSIVE, denominator=0, inputs={"board": path},
                        note="the board carries no via, so nothing was judged")
    # TWO CRITERIA, TWO VERDICTS, for the same reason dc_drop has two: they have different authorities. The
    # diameter and the drill are judged against the BOARD'S OWN minimums, which the board carries and the DRC
    # already believes, so that question can be answered here. The annular ring is judged against a FABRICATOR
    # capability, and this tree's only fabricator capability file is a JavaScript-blocked page scrape with no
    # capability data in it. Answering the first honestly must not depend on the second being unanswerable.
    ring_bad = [x for x in r["bad"] if "annular" in x] + r["thin_pads"]
    floor_bad = [x for x in r["bad"] if "annular" not in x]
    # VIA-002 covers both kinds of hole, so its denominator is both kinds, and it can only be answered for the
    # kinds this board has declared a floor for. A board that declares one and not the other is INCONCLUSIVE:
    # a partial answer reported as a pass is the shape this registry exists to refuse.
    judged = (r["vias"] if vmin is not None else 0) + (r["plated_holes"] if amin is not None else 0)
    undeclared = [k for k, v in (("the via ring", vmin), ("the plated hole ring", amin)) if v is None]
    _v.write("via_annular", (_v.INCONCLUSIVE if undeclared else (_v.FAIL if ring_bad else _v.PASS)),
             counts={"vias": r["vias"], "plated_holes": r["plated_holes"], "npth_holes": r["npth_holes"],
                     "below_ring": len(ring_bad)}, denominator=judged or (r["vias"] + r["plated_holes"]),
             evidence=ring_bad[:20], inputs={"board": path, "annular_min_mm": amin, "via_ring_min_mm": vmin},
             quiet=True,
             note=("this board declares no floor for %s, so that ring was not judged: a floor asserted without "
                   "the fabricator's own row would be the heuristic-as-law this audit exists to remove"
                   % " and ".join(undeclared) if undeclared else
                   "the copper left around every hole against the two floors this board declares, the via rows "
                   "for vias and the annular ring row for plated component holes"))
    return _v.write("via_audit", _v.FAIL if floor_bad else _v.PASS,
                    counts={"vias": r["vias"], "below_floor": len(floor_bad), "via_in_pad": len(r["in_pad"]),
                            "below_ring": len(ring_bad), "plated_holes": r["plated_holes"]},
                    denominator=r["vias"], evidence=floor_bad[:20],
                    inputs={"board": path},
                    note=("every via at or above the board's own minimum diameter and drill; the annular ring is "
                          "judged separately in via_annular.verdict.json, and %s"
                          % ("no floor is declared for it" if (amin is None or vmin is None)
                             else "%d hole(s) are under a floor" % len(ring_bad))))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
