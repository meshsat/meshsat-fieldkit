#!/usr/bin/env python3
"""Can the fence reach the copper that breaks ANA-001? (rule ANA-001's third report, 21 September 2026)

`sense_fence.py` is this rule's only instrument that reaches the router, and it grows its keep-out around the
copper the PRE-LAY LOCKED. So a fence arm can only move copper the ROUTER laid, and only near a sensitive net
the pre-lay actually touched. Both halves are properties of the board in front of it and neither is visible in
`sensitive_nodes`' own reading, which names one clearance per declared node and says nothing about who laid
the copper on either side. Twice in one morning that gap decided what to do next:

* **Board E.** On E37's finished round-1 board, 23 pairs of segments sit inside the asked clearance on a
  shared layer, the SWITCHING side is locked in NONE of them and the SENSE side in every one. So the fence
  could move all of it, and E38 was read as a real arm rather than as a fence that had never been asked the
  question.
* **Board A.** On A98's finished round-1 board, 88 pairs, the switching side locked in 6 and the sense side in
  35 -- and every one of the tightest rows is a net the pre-lay never touched (`PD_ISNS_P` 0.132 mm from
  `PD_SW1`, `FE_ISNS_P` 0.155, `CH_SRN_F` 0.155), while the nets that DO carry locked copper read 0.213 and
  wider. A fence on board A therefore protects the rows that were already the widest, which is a prediction
  about its arm and the reason A101 adds those nets to the pre-lay instead.

**AND THE RULE'S DENOMINATOR IS NARROWER THAN ITS SUBJECT, which this reports beside it.** `sensitive_nodes`
measures against the nets a board DECLARES as switching, and `switch_list.py` (this rule's second report) asks
whether that list is complete for a switching NODE. A gate drive is excluded from it deliberately, by pin
function, because a gate is not the switching copper; for a keep-away from a current-sense pair it is an
aggressor all the same, ten volts in tens of nanoseconds into amps of gate current. On board E the tightest
approach of all is `TRK_CSN` at 0.204 mm from `TRK_TG2`, a gate drive. So extra nets may be named on the
command line, as patterns, and the row says which side of the declaration each aggressor came from.

**IT IS A REPORT AND IT DECIDES NOTHING.** Whether a gate drive belongs in ANA-001's denominator is a
judgement that belongs with the operating envelope (decision 34), and a tool that turned its own list into a
verdict would be asserting it. What it does is put the geometry in front of whoever rules it, with every
segment's LOCKED flag, its layer and its length, so the next fence arm is designed against a number.

Two things it deliberately does NOT do. It does not measure a pad, only track segments, because the pads are
where `sensitive_nodes`' own courtyard exemption applies and this is about the run between them. And it never
compares segments on different layers: a 0.2 mm overlap through the dielectric is coupling rather than
clearance, `sensitive_nodes` says so in its own note, and this list sets no number for it either.

Usage: sense_reach.py <board.kicad_pcb> --board <letter> [--clearance MM] [--extra PAT,PAT] [--json]
       sense_reach.py <board.kicad_pcb> --sense A,B --switch C,D [--clearance MM] [--json]
"""
import fnmatch
import json
import math
import os
import sys

import verdict as _v

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)


def declared(letter, path=None):
    """The board's own sensitive nodes and switch patterns, read from the file the RULE reads."""
    import yaml
    p = path or os.path.join(TOOLS, "pcb_sensitive.yaml")
    d = yaml.safe_load(open(p, encoding="utf-8")) or {}
    b = (d.get("boards") or d).get(letter) or {}
    nodes = [str(n.get("net") if isinstance(n, dict) else n) for n in (b.get("nodes") or [])]
    return nodes, list(b.get("switch_nets") or [])


def gap(a, b):
    """Edge-to-edge distance in mm between two track segments, which is what a clearance is.

    Sampled from each end against the other segment, which is exact for the endpoint cases and never
    optimistic in between; a clearance question at a tenth of a millimetre does not need more, and a tool
    that needed more would be a DRC."""
    def pt_seg(px, py, x1, y1, x2, y2):
        vx, vy = x2 - x1, y2 - y1
        L = vx * vx + vy * vy
        t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - x1) * vx + (py - y1) * vy) / L))
        return math.hypot(px - (x1 + t * vx), py - (y1 + t * vy))
    (ax, ay), (bx, by) = a["a"], a["b"]
    (cx, cy), (dx, dy) = b["a"], b["b"]
    d = min(pt_seg(ax, ay, cx, cy, dx, dy), pt_seg(bx, by, cx, cy, dx, dy),
            pt_seg(cx, cy, ax, ay, bx, by), pt_seg(dx, dy, ax, ay, bx, by))
    return d - (a["w"] + b["w"]) / 2.0


MM = 1e6      # module level, so a fake board of six methods can drive this where KiCad is not (the
              # `test_rail_crossings` pattern; a stub in sys.modules is what this project forbids)


def segments(board, names):
    out = []
    for t in board.GetTracks():
        if t.GetClass() != "PCB_TRACK":
            continue
        n = t.GetNetname().lstrip("/")
        if n not in names:
            continue
        out.append({"net": n, "layer": t.GetLayer(), "locked": bool(t.IsLocked()),
                    "w": t.GetWidth() / MM, "len": t.GetLength() / MM,
                    "a": (t.GetStart().x / MM, t.GetStart().y / MM),
                    "b": (t.GetEnd().x / MM, t.GetEnd().y / MM)})
    return out


def rows(board, sense_names, switch_names, clearance):
    """Every sense segment within `clearance` of a switching segment ON THE SAME LAYER."""
    sn, wn = segments(board, set(sense_names)), segments(board, set(switch_names))
    out = []
    for s in sn:
        for w in wn:
            if s["layer"] != w["layer"]:
                continue
            d = gap(s, w)
            if d < clearance:
                out.append({"mm": round(d, 4), "sense": s["net"], "switch": w["net"],
                            "layer": board.GetLayerName(s["layer"]),
                            "sense_locked": s["locked"], "switch_locked": w["locked"],
                            "sense_len": round(s["len"], 2), "switch_len": round(w["len"], 2)})
    out.sort(key=lambda r: r["mm"])
    return out, len(sn), len(wn)


def summarise(rs, declared_switch):
    """Per sensitive net: how many pairs, how many with LOCKED sense copper (which is what a fence can be
    grown from), the tightest, and how many of its aggressors the declaration does not carry."""
    per = {}
    for r in rs:
        e = per.setdefault(r["sense"], {"pairs": 0, "locked": 0, "tightest": 9e9, "undeclared_aggressor": 0})
        e["pairs"] += 1
        e["locked"] += 1 if r["sense_locked"] else 0
        e["tightest"] = min(e["tightest"], r["mm"])
        e["undeclared_aggressor"] += 0 if r["switch"] in declared_switch else 1
    return per


def main(argv):
    if not argv or "--help" in argv:
        print(__doc__)
        return 2
    import pcbnew
    path = argv[0]
    clearance = float(_v.opt(argv, "--clearance", 0.50))
    letter = _v.opt(argv, "--board")
    board = pcbnew.LoadBoard(path)
    names = sorted({t.GetNetname().lstrip("/") for t in board.GetTracks()})
    extra_pats = [x for x in (_v.opt(argv, "--extra", "") or "").split(",") if x]
    missing = None
    if letter:
        sense, pats = declared(letter)
        switch = sorted({n for n in names for p in pats if fnmatch.fnmatch(n, p.lstrip("/"))})
        if not sense:
            missing = "board %s declares no sensitive node, so there is nothing to measure" % letter
    else:
        sense = [x for x in (_v.opt(argv, "--sense", "") or "").split(",") if x]
        switch = [x for x in (_v.opt(argv, "--switch", "") or "").split(",") if x]
        pats = list(switch)
    declared_switch = set(switch)
    if extra_pats:
        switch = sorted(set(switch) | {n for n in names for p in extra_pats if fnmatch.fnmatch(n, p.lstrip("/"))})
    rs, n_sense, n_switch = rows(board, sense, switch, clearance)

    per = summarise(rs, declared_switch)
    sw_locked = sum(1 for r in rs if r["switch_locked"])
    se_locked = sum(1 for r in rs if r["sense_locked"])
    nofence = sorted(n for n, e in per.items() if e["locked"] == 0)

    print("sense_reach: board %s, %d sensitive net(s) declared, %d switching net(s) matched%s; %d sense and "
          "%d switching segment(s), asking %.3f mm"
          % ((letter or "-").upper(), len(sense), len(switch),
             (" (%d of them named on the command line and NOT in the declaration)"
              % len(set(switch) - declared_switch)) if extra_pats else "",
             n_sense, n_switch, clearance))
    print("sense_reach: %d pair(s) inside the clearance on a shared layer; the SWITCHING side is locked in %d "
          "of them and the SENSE side in %d" % (len(rs), sw_locked, se_locked))
    if rs:
        print("sense_reach: a fence drawn after the pre-lay can move the switching side of %d of %d pair(s), "
              "and it has locked sense copper to grow from at %d of %d net(s)"
              % (len(rs) - sw_locked, len(rs), len(per) - len(nofence), len(per)))
    for n, e in sorted(per.items(), key=lambda kv: kv[1]["tightest"]):
        print("  %-12s %3d pair(s), %3d with locked sense copper, tightest %.3f mm%s%s"
              % (n, e["pairs"], e["locked"], e["tightest"],
                 ", %d against a net the declaration does not carry" % e["undeclared_aggressor"]
                 if e["undeclared_aggressor"] else "",
                 "   <-- the fence has nothing to grow from here" if e["locked"] == 0 else ""))
    for r in rs[:12]:
        print("  %7.3f mm  %-12s (%s, %s, %.2f mm) against %-12s (%s, %s, %.2f mm)%s"
              % (r["mm"], r["sense"], r["layer"], "LOCKED" if r["sense_locked"] else "router", r["sense_len"],
                 r["switch"], r["layer"], "LOCKED" if r["switch_locked"] else "router", r["switch_len"],
                 "" if r["switch"] in declared_switch else "   (not in this board's switch_nets)"))
    if "--json" in argv:
        print(json.dumps({"rows": rs, "per_net": per}, indent=1))

    # A REPORT NEVER DECIDES A RULE (the 16 September rule for via_current's advisory half). ANA-001 stays
    # sensitive_nodes' to decide; this says what a fence could do about it.
    ev = ["%s %.3f mm from %s on %s (%s sense, %s switching)%s"
          % (r["sense"], r["mm"], r["switch"], r["layer"],
             "locked" if r["sense_locked"] else "router", "locked" if r["switch_locked"] else "router",
             "" if r["switch"] in declared_switch else " [aggressor not declared]") for r in rs[:20]]
    return _v.write("sense_reach", _v.PASS if not rs else _v.FAIL,
                    counts={"pairs": len(rs), "switch_locked": sw_locked, "sense_locked": se_locked,
                            "nets_with_no_locked_sense_copper": len(nofence),
                            "sense_nets": len(sense), "switch_nets": len(switch),
                            "undeclared_aggressor_pairs": sum(1 for r in rs if r["switch"] not in declared_switch)},
                    denominator=len(rs), evidence=ev, advisory=True, missing_input=missing,
                    inputs={"board": path, "clearance": clearance, "declares": pats, "extra": extra_pats},
                    note="every sensitive segment within the asked clearance of switching copper on the SAME "
                         "layer, with each side's locked flag: a fence grown after the pre-lay can move the "
                         "switching side only where the router laid it, and it can be grown at all only where "
                         "the pre-lay locked sense copper. A REPORT; ANA-001 is sensitive_nodes' to decide")


if __name__ == "__main__":
    sys.exit(_v.guard("sense_reach", main, sys.argv[1:]))
