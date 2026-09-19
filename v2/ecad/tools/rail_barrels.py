#!/usr/bin/env python3
"""The barrels a declared rail's own crossing needs, laid on the PLACED board (rule PI-003, the cheap half answered).

MESHSAT-862, 19 September 2026. `rail_crossings.py` names every crossing where a declared rail changes layer
through fewer barrels than its current needs, and it deliberately lays nothing, because where to put copper is
a placement question whose shape differs per board. That was right while the sites were unknown. They are not
unknown any more, and on every board of this set they have ONE shape: the site is a pad of the rail's own part,
the single barrel there is the fanout's own locked via, and the room beside it is EMPTY because nothing is
routed yet. Board B's three slot rails at 2.20 A through one 0.25 mm barrel inside their bulk capacitor's pad
are that shape three times from one generator line.

IT RUNS BEFORE THE ROUTE AND `via_parallel.py` RUNS AFTER IT. They answer the same rule and they are not
interchangeable: after a route the space beside a source pad is full, every candidate has to be checked against
the copper that is already there, and a barrel's link back to its net has to be drawn and proved, which is what
that file's rings, fields and link tests are for. Before a route the same answer is three points and a drill.
This is the C10 lesson of 15 September in another place: the corridor a closure cannot reach afterwards is
empty at generation time. So this tool REFUSES a routed board and says which tool that board's question belongs
to, rather than laying locked copper into traffic.

WHAT IT WILL NOT DO. A site whose current needs more than `--max-barrels` (8 by default) is DECLINED with its
number and reported as a placement item. Board P's CELL4 crosses at ONE 0.50 mm barrel carrying 18.00 A, which
is eighteen barrels; eighteen barrels in a row beside a pad is a busbar and a different pad, not a cluster, and
a tool that draws it anyway would turn a measured refusal into copper nobody chose. The same cap is what stops
this becoming a way to answer a rule by decoration.

The count, the pitch and the hole-to-hole floor are `power_copper`'s, which takes them from `via_current`, which
is the rule that judges this after the route; the sites are `rail_crossings.rows`, which is the judge's own walk
carrying its numbers instead of its prose. Nothing here has its own opinion about which site is short or how
many barrels it needs.

Usage: rail_barrels.py <placed board.kicad_pcb> [--intent path] [--apply] [--max-barrels 8]
                       [--board <letter>] [--out-dir DIR]
       Reports by default; `--apply` lays the barrels, DRCs, keeps what the DRC accepts and saves.
       exit 0 nothing to do or laid, 1 every site refused by the DRC, 3 no intent file to work from."""
import sys, os, math, json, shutil

TOOLS = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TOOLS)
import verdict as _v
import rail_crossings as _rc
import via_current as _vc
import hardset

# KiCad IS IMPORTED IN `main`, and so are the two modules that import it at their own top (`power_copper` and
# `via_parallel`). `plan` is a function of numbers and a callable, and `_routed` touches method names only, so
# every rule about where a barrel goes, when a site is declined and what counts as a routed board runs on the
# runner instead of skipping there. This is the same split `rail_crossings.judge` carries and the reason
# `test_pair_router_imports` exists: a tool whose rules only run where KiCad is leaves the suite green while
# the tool is broken.
#
# THE DRC IS ASKED THROUGH `via_parallel`'s OWN TWO HELPERS and not through a second copy of them here. The
# 17 September defect worth remembering is `return_gaps.py` quietly ceasing to agree with its own gate; two
# tools that both answer "what does the DRC say about this board" drift the same way. `test_rail_barrels`
# refuses a private copy of either in this file.

MAX_BARRELS = 8          # above this a cluster is a busbar: declined, reported, and left to the placement
FLOOR = 0.2995           # hole to hole, this project's own rule; power_copper.stitch enforces it


def _save_filled(pcbnew, b, path):
    """Save, reload and REFILL before anything measures this board.

    A through via lands in every pour it crosses, and a pour filled before the via existed still has its
    copper there: the DRC then reads `Clearance violation (zone clearance 0.3000 mm; actual 0.0000 mm)` at
    every barrel and the whole set is reverted. Board A's first three runs of this tool said exactly that
    seven times. It is the 14 September defect in another place, where the gate and every rail verdict were
    read off a fill from four stages earlier and the finish learnt to refill before it judges. The save and
    reload come first because `ZONE_FILLER` segfaults on a board built in python and fills a saved-then-loaded
    copy fine (17 September, the board fixtures)."""
    pcbnew.SaveBoard(path, b)
    b2 = pcbnew.LoadBoard(path)
    b2.BuildConnectivity()
    pcbnew.ZONE_FILLER(b2).Fill(b2.Zones())
    pcbnew.SaveBoard(path, b2)


def _routed(b):
    """True when a router has been over this board (place_audit's own test, 16 September)."""
    segs = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]
    if len(segs) <= 100: return False
    unlocked = sum(1 for t in segs if not t.IsLocked())
    return unlocked > 100 and unlocked > 0.20 * len(segs)


def plan(row, free, max_barrels=MAX_BARRELS):
    """(pts, axis, note): where the barrels this crossing still needs go, or ([], axis, why not).

    `free(x, y)` answers whether a barrel may stand at (x, y): on a board it is `return_via._site_free`, this
    project's ONE site test, which knows about every other net's pads, tracks and vias on every layer and has
    the paste-aperture fix of 17 September in it. Here it is a callable so that every rule about the LATTICE
    runs where KiCad is not.

    THE LATTICE IS ANCHORED ON THE BARREL ALREADY THERE, not on the pad centre. The first version centred
    `need` points on the pad, which on a site with one barrel in the middle puts two new holes half a pitch
    from it: board A's seven sites came back `clearance, hole_clearance, hole_to_hole` and every one was
    reverted. The site already has `have` barrels; what is owed is `need - have`, laid on the same lattice,
    growing outward from the ones that are there and skipping any position that is occupied or refused."""
    x, y = row["at"]; drill = row["drill"]; need = int(row["need"]); have = int(row["have"])
    near = list(row.get("near") or [])
    if need > max_barrels:
        return [], "x", ("%d barrels of %.2f mm for %.2f A is a busbar and not a cluster: this site is a "
                         "placement item, not copper to add beside the pad" % (need, drill, row["amps"]))
    if need <= have:
        return [], "x", "this site already carries the barrels its current needs"
    pitch = drill + 0.4
    floor = drill + FLOOR
    # The anchor is the existing barrel nearest the pad, so the new copper grows out of the copper that is
    # there; with no barrel recorded the pad itself is the anchor.
    ax, ay = min(near, key=lambda q: math.hypot(q[0] - x, q[1] - y)) if near else (x, y)
    owed = need - have          # ONE place holds this number: written twice, a mutation of either survived
    best = None
    for axis in ("x", "y"):
        pts, k = [], 1
        while len(pts) < owed and k <= 4 * need:
            for sgn in (1, -1):
                if len(pts) >= owed: break
                cx = ax + (k * pitch if axis == "x" else 0.0) * sgn
                cy = ay + (k * pitch if axis == "y" else 0.0) * sgn
                if any(math.hypot(cx - qx, cy - qy) < floor - 1e-9 for qx, qy in near + pts): continue
                if not free(cx, cy): continue
                pts.append((cx, cy))
            k += 1
        if best is None or len(pts) > len(best[0]): best = (pts, axis)
    pts, axis = best
    if not pts:
        return [], axis, ("no free site on either axis at this pitch: the %d barrel(s) this crossing needs "
                          "have nowhere to stand, which is a placement item" % need)
    note = ("%d of the %d still owed" % (len(pts), owed)) if len(pts) < owed \
        else "every barrel still owed has a free site"
    return pts, axis, note


def main(argv):
    if not argv: print(__doc__); return 2
    import pcbnew
    import power_copper as _pc
    import via_parallel as _vp
    import return_via as _rv
    path = argv[0]
    apply_ = "--apply" in argv
    maxb = int(_v.opt(argv, "--max-barrels", MAX_BARRELS))
    letter = _v.opt(argv, "--board", None)
    out_dir = _v.opt(argv, "--out-dir", None)
    stem = os.path.splitext(os.path.basename(path))[0]
    for suf in ("-placed", "-preroute", "-par-routed", "-cleaned"):
        if stem.endswith(suf): stem = stem[: -len(suf)]
    pdir = os.path.dirname(os.path.abspath(path))
    if os.path.basename(pdir) == "out": pdir = os.path.dirname(pdir)
    ip = _v.opt(argv, "--intent", os.path.join(pdir, "out", stem + "-intent.json"))
    tool = "rail_barrels" + ("_" + letter if letter else "")

    if not os.path.exists(ip):
        print("rail_barrels: no intent file at %s, so no rail declares a current here" % ip)
        _v.write(tool, "INCONCLUSIVE", {}, 0, evidence=ip, missing_input="the board's intent file",
                 note="no rail declares a current here", out_dir=out_dir, rules=["PI-003"])
        return 3

    rails = json.load(open(ip, encoding="utf-8")).get("rails") or {}
    b = pcbnew.LoadBoard(path)
    if _routed(b):
        # A LOCKED VIA LAID INTO TRAFFIC IS NOT THIS TOOL'S ANSWER (see the header). Saying so is the whole
        # difference between the two halves of PI-003's fix.
        print("rail_barrels: this board is ROUTED; the barrels of a routed board are via_parallel.py's, "
              "which checks every candidate against the copper that is there and proves each link")
        _v.write(tool, "INCONCLUSIVE", {}, 0, evidence=path, missing_input="an unrouted board",
                 note="a routed board's barrels are via_parallel.py's, not this tool's",
                 out_dir=out_dir, rules=["PI-003"])
        return 3

    rows, judged = _rc.rows(b, rails)
    if not rows:
        print("rail_barrels: %d crossing(s) of %d declared rail(s) carry the barrels their current needs, "
              "nothing to lay" % (judged, len(rails)))
        _v.write(tool, "PASS", {"short": 0, "judged": judged}, judged, evidence=path,
                 note="every declared rail's own crossing already carries the barrels its current needs",
                 out_dir=out_dir, rules=["PI-003"])
        return 0

    ds = b.GetDesignSettings()
    clr = max(pcbnew.ToMM(ds.m_MinClearance), 0.127)     # return_via's own floor, and its reason
    plans, declined = [], []
    for r in rows:
        own = "/" + r["net"] if not r["net"].startswith("/") else r["net"]
        own = own if any((p.GetNetname() or "") == own for fp in b.GetFootprints() for p in fp.Pads()) \
            else r["net"]
        free = lambda X, Y, _w=r["width"], _o=own: _rv._site_free(b, X, Y, _w, clr, _o)
        pts, axis, note = plan(r, free, maxb)
        if not pts: declined.append((r, note)); continue
        plans.append((r, pts, axis, note))
    for r, note in declined:
        print("rail_barrels: DECLINED %s at %s pad %s (%.2f, %.2f): %s"
              % (r["net"], r["ref"], r["pad"], r["at"][0], r["at"][1], note))
    for r, pts, axis, note in plans:
        print("rail_barrels: %s at %s pad %s (%.2f, %.2f): +%d barrel(s) of %.2f/%.2f mm for %.2f A, %d there, "
              "spread on %s, %s" % (r["net"], r["ref"], r["pad"], r["at"][0], r["at"][1], len(pts),
                                    r.get("width", 0.0), r["drill"], r["amps"], r["have"], axis, note))
    if not apply_:
        print("rail_barrels: %d site(s) planned, %d declined, nothing laid (give --apply)"
              % (len(plans), len(declined)))
        _v.write(tool, "FAIL" if rows else "PASS",
                 {"short": len(rows), "planned": len(plans), "declined": len(declined), "judged": judged},
                 judged, evidence=path, advisory=True,
                 note="a dry run: %d crossing(s) short, %d answerable beside the pad, %d a placement item"
                      % (len(rows), len(plans), len(declined)), out_dir=out_dir, rules=["PI-003"])
        return 0

    bak = path + ".rail_barrels.bak"; shutil.copy2(path, bak)
    h0, u0, _ = _vp._measure(path)
    laid = []
    P = lambda x, y: pcbnew.VECTOR2I(pcbnew.FromMM(float(x)), pcbnew.FromMM(float(y)))
    nets = {}
    for t in list(b.GetTracks()) + [p for fp in b.GetFootprints() for p in fp.Pads()]:
        n = (t.GetNetname() or "").lstrip("/")
        if n and n not in nets: nets[n] = t.GetNet()
    pc = _pc.PowerCopper(b, lambda n, create=False: nets[n.lstrip("/")], P)
    for r, pts, axis, note in plans:
        # `stitch` carries the hole-to-hole floor and the count check, so a plan this file got wrong stops here
        # with its number rather than reaching a board.
        # THE RING IS THE ONE ALREADY ON THIS SITE, never a number this file chose. Board A declares a 0.20 mm
        # annular floor and the first version's `max(drill + 0.3, 0.6)` is 0.15 mm of ring on a 0.40 mm drill.
        # `stitch` checks the floor WITHIN this call; the barrels already on the site are the
        # plan's to keep clear of, which it does before a point is ever offered here.
        pc.stitch(r["net"], pts, drill=r["drill"], width=r["width"])
        laid.append((r, pts))
    _save_filled(pcbnew, b, path)
    h, u, d = _vp._measure(path)
    if h > h0 or u > u0:
        hits = _vp._hit_positions(d)
        keep = []
        # A GATE THAT STRIPS COPPER MUST NAME WHAT IT HIT, and the TYPE alone is not that (8 September 2026,
        # `escape_prune`, which printed a pad list until the placement could not be corrected from it). The
        # DRC's own description names both items of the pair, which is the counterparty, so it travels here.
        types = {}
        for v_ in d.get("violations", []):
            if v_.get("type") not in hardset.HARD_POST: continue
            for i_ in v_.get("items", []):
                p_ = i_.get("pos") or {}
                if "x" in p_ and "y" in p_:
                    types.setdefault((float(p_["x"]), float(p_["y"])), []).append(
                        (v_["type"], " ".join((v_.get("description") or "").split())[:160]))
        for r, pts in laid:
            hit = [t for px, py in pts for (hx, hy), ts in types.items()
                   if math.hypot(px - hx, py - hy) < 1.0 for t in ts]
            if hit:
                print("rail_barrels: the DRC refuses %s at %s pad %s (%s): that site is reverted"
                      % (r["net"], r["ref"], r["pad"], ", ".join(sorted({t for t, _ in hit}))))
                for why in sorted({w for _, w in hit})[:2]:
                    print("rail_barrels:     %s" % why)
                continue
            keep.append((r, pts))
        shutil.copy2(bak, path)
        b = pcbnew.LoadBoard(path)
        nets = {}
        for t in list(b.GetTracks()) + [p for fp in b.GetFootprints() for p in fp.Pads()]:
            n = (t.GetNetname() or "").lstrip("/")
            if n and n not in nets: nets[n] = t.GetNet()
        pc = _pc.PowerCopper(b, lambda n, create=False: nets[n.lstrip("/")], P)
        for r, pts in keep: pc.stitch(r["net"], pts, drill=r["drill"], width=r["width"])
        _save_filled(pcbnew, b, path)
        h, u, _ = _vp._measure(path)
        laid = keep
        if h > h0 or u > u0:
            print("rail_barrels: HURT (hard %d -> %d, unrouted %d -> %d): reverting every barrel"
                  % (h0, h, u0, u))
            shutil.copy2(bak, path); laid = []
    n_vias = sum(len(p) - r["have"] for r, p in laid)
    print("rail_barrels: %d site(s) answered with %d barrel(s), %d refused by the DRC, %d declined "
          "(hard %d -> %d, unrouted %d -> %d)"
          % (len(laid), sum(len(p) for _, p in laid), len(plans) - len(laid), len(declined), h0, h, u0, u))
    res = "PASS" if (laid and not declined and len(laid) == len(plans)) else ("FAIL" if declined or not laid else "FAIL")
    _v.write(tool, res,
             {"sites": len(laid), "barrels": sum(len(p) for _, p in laid), "declined": len(declined),
              "refused": len(plans) - len(laid), "short": len(rows), "judged": judged},
             judged, evidence=path,
             note="%d of %d short crossing(s) answered beside the pad; %d declined as a placement item"
                  % (len(laid), len(rows), len(declined)), out_dir=out_dir, rules=["PI-003"])
    return 0 if laid or not plans else 1


if __name__ == "__main__":
    sys.exit(_v.guard("rail_barrels", main, sys.argv[1:], rules=["PI-003"]))
