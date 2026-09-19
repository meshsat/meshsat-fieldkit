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

Usage: rail_barrels.py <placed board.kicad_pcb> [--intent path] [--apply] [--max-barrels 8] [--reach 6.0]
                       [--board <letter>] [--out-dir DIR]
       Reports by default; `--apply` lays the barrels, DRCs, keeps what the DRC accepts and saves.
       exit 0 nothing to do or laid, 1 every site refused by the DRC, 3 no intent file to work from."""
import sys, os, math, json, shutil

TOOLS = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TOOLS)
import verdict as _v
import rail_crossings as _rc
import via_current as _vc

# KiCad IS IMPORTED IN `main`, and so are the two modules that import it at their own top (`power_copper` and
# `via_parallel`). `plan`, `_routed` and `_obstacles` touch method names only, never a pcbnew constant, so
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
REACH = 6.0              # how far to look for another net's pad when choosing the axis (barrel_sites' own number)
FLOOR = 0.2995           # hole to hole, this project's own rule; power_copper.stitch enforces it


def _routed(b):
    """True when a router has been over this board (place_audit's own test, 16 September)."""
    segs = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]
    if len(segs) <= 100: return False
    unlocked = sum(1 for t in segs if not t.IsLocked())
    return unlocked > 100 and unlocked > 0.20 * len(segs)


def _obstacles(b, net, x, y, reach):
    """Every other net's pad centre within reach of the site, in mm."""
    out = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if (p.GetNetname() or "").lstrip("/") == net: continue
            q = p.GetPosition(); px, py = q.x / 1e6, q.y / 1e6
            if math.hypot(px - x, py - y) <= reach: out.append((px, py))
    return out


def plan(row, others, max_barrels=MAX_BARRELS):
    """(pts, axis, note): where the barrels of one short crossing go, or ([], axis, why not).

    Pure arithmetic over numbers, so it is exercised where KiCad is not. The count and the pitch come from
    `power_copper`; the axis is the one whose points stay furthest from another net's pad, which is
    `barrel_sites --suggest`'s own choice made by the thing that lays them."""
    x, y = row["at"]; drill = row["drill"]; need = int(row["need"])
    if need > max_barrels:
        return [], "x", ("%d barrels of %.2f mm for %.2f A is a busbar and not a cluster: this site is a "
                         "placement item, not copper to add beside the pad" % (need, drill, row["amps"]))
    pitch = drill + 0.4
    span = (need - 1) * pitch
    def pts_for(ax):
        return [((x - span / 2.0 + i * pitch, y) if ax == "x" else (x, y - span / 2.0 + i * pitch))
                for i in range(need)]
    def worst(ax):
        return min([math.hypot(px - ox, py - oy) for px, py in pts_for(ax) for ox, oy in others] or [99.0])
    wx, wy = worst("x"), worst("y")
    axis = "x" if wx >= wy else "y"
    room = ("%.2f mm to another net's pad on this axis, %.2f on the other" % (max(wx, wy), min(wx, wy))) \
        if others else "nothing else within %.1f mm" % REACH
    return pts_for(axis), axis, room


def main(argv):
    if not argv: print(__doc__); return 2
    import pcbnew
    import power_copper as _pc
    import via_parallel as _vp
    path = argv[0]
    apply_ = "--apply" in argv
    maxb = int(_v.opt(argv, "--max-barrels", MAX_BARRELS))
    reach = float(_v.opt(argv, "--reach", REACH))
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

    plans, declined = [], []
    for r in rows:
        others = _obstacles(b, r["net"], r["at"][0], r["at"][1], reach)
        pts, axis, note = plan(r, others, maxb)
        if not pts: declined.append((r, note)); continue
        plans.append((r, pts, axis, note))
    for r, note in declined:
        print("rail_barrels: DECLINED %s at %s pad %s (%.2f, %.2f): %s"
              % (r["net"], r["ref"], r["pad"], r["at"][0], r["at"][1], note))
    for r, pts, axis, note in plans:
        print("rail_barrels: %s at %s pad %s (%.2f, %.2f): %d barrel(s) of %.2f mm for %.2f A, %d there, "
              "spread on %s, %s" % (r["net"], r["ref"], r["pad"], r["at"][0], r["at"][1], r["need"],
                                    r["drill"], r["amps"], r["have"], axis, note))
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
        pc.stitch(r["net"], pts, drill=r["drill"], width=max(r["drill"] + 0.3, 0.6))
        laid.append((r, pts))
    pcbnew.SaveBoard(path, b)
    h, u, d = _vp._measure(path)
    if h > h0 or u > u0:
        hits = _vp._hit_positions(d)
        keep = []
        for r, pts in laid:
            if any(math.hypot(px - hx, py - hy) < 1.0 for px, py in pts for hx, hy in hits):
                print("rail_barrels: the DRC refuses %s at %s pad %s: that site is reverted"
                      % (r["net"], r["ref"], r["pad"]))
                continue
            keep.append((r, pts))
        shutil.copy2(bak, path)
        b = pcbnew.LoadBoard(path)
        nets = {}
        for t in list(b.GetTracks()) + [p for fp in b.GetFootprints() for p in fp.Pads()]:
            n = (t.GetNetname() or "").lstrip("/")
            if n and n not in nets: nets[n] = t.GetNet()
        pc = _pc.PowerCopper(b, lambda n, create=False: nets[n.lstrip("/")], P)
        for r, pts in keep: pc.stitch(r["net"], pts, drill=r["drill"], width=max(r["drill"] + 0.3, 0.6))
        pcbnew.SaveBoard(path, b)
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
