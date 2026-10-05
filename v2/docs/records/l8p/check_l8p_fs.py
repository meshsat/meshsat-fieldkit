#!/usr/bin/env python3
"""check_l8p_fs.py: Layer 8 record l8p ROUND 9 (MESHSAT-1357, 5 October 2026; the owner's review of checkpoint 3, part 22, item A,
and the check cx45's Q5): board A's netlist read by pin for the fail-safe delta apply_gen_sch_a_thgfs.py, drawn after round 8's guard.

check_l8p_netlist.py (round 8's reader, whose digest other records print) is left as it is; this module reads a board A that carries
the delta, using that reader's netlist parser and helpers:
  EN     the loop on J_DOCK as check_l8p_netlist's EN group reads it, with C268 and path 2's shunt Q61 (drain) admitted on DOCK_EN_OUT;
  PATH1  round 8's guard (the pair in series, U60 on U61's output, R262 from OVERTEMP to Q60's gate, C260 and R263, Q60 on the
         return) with U60's open drain (pin 3) now on THG_ODN, and its cold clamp: Q62 over Q63 in series from Q60's gate to the
         ground, both gates on THG_ODN, THG_ODN on U60's pin 3, the clamp's gates, R269 and a test point alone, the pull-up R268 over
         R269 from U60's supply;
  PATH2  the second guard: U63 (a TPS70950) from VBAT, never from DOCK_EN_OUT; U62 (an LM26LV) on U63's output with its pad and GND
         on the ground, its open drain on nothing, TRIP_TEST and VTEMP on a test point alone; R270 from U62's OVERTEMP to Q61's gate,
         C272 and R271 to the ground; Q61 (a 2N7002) from DOCK_EN_OUT to the ground;
  APART  no net of path 1's supply, switch output or gate is a net of path 2's, and the reverse.
Usage:  check_l8p_fs.py NETLIST      Exit 0 DRAWN, 4 FAIL, 3 NOT DRAWN (U62 absent). Nothing is written."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import check_l8p_netlist as C  # noqa: E402

FS_ON_OUT = {("C268", "1"), ("C268", "2"), ("Q61", "3")}
FS_VALUES = (("U62", "LM26LVQISDX-130"), ("U63", "TPS70950"), ("Q61", "2N7002"), ("Q62", "2N7002"), ("Q63", "2N7002"), ("R268", "220k 1%"),
             ("R269", "220k 1%"), ("R270", "47k"), ("C272", "1u"), ("R271", "1M"), ("C261", "330n 50V"), ("C268", "330n 50V"), ("C269", "100n"),
             ("C270", "330n 50V"), ("C271", "4.7u"))


def fs_drawn(nl):
    """Board A carries the delta: a second LM26LV, U62."""
    return str(nl["comps"].get("U62", {}).get("value", "")).startswith("LM26LV")


def _refs(nl, net):
    return {r for r, _p in C._nodes(nl, net)} if net else set()


def _tp_only(nl, refs):
    return all(C._is_tp(nl, x) for x in refs)


def checks_en_fs(nl):
    """check_l8p_netlist's EN group on a board with the delta: the same facts, C268 and Q61's drain admitted on DOCK_EN_OUT."""
    bad = C.props(nl, [("J_DOCK", "3", C.RET), ("J_DOCK", "4", "GND"), ("J_DOCK", "5", C.OUT)])
    if "RT1" in nl["comps"]:
        bad.append("RT1 is drawn: it is withdrawn (L8P-F07)")
    if C._two(nl, "R260") != sorted({C.OUT, "THG_MID"}) or C._two(nl, "R261") != sorted({"THG_MID", C.RET}):
        bad.append("the loop is not closed by the guard's pair: R260 on %s, R261 on %s" % (C._two(nl, "R260"), C._two(nl, "R261")))
    for n in (C.OUT, C.RET):
        base = {("J_DOCK", "5" if n == C.OUT else "3")}
        extra = sorted(C._nodes(nl, n) - base - C.DD7_ON[n] - C.THG_ON[n] - (FS_ON_OUT if n == C.OUT else set()))
        if extra:
            bad.append("%s reaches %s beyond J_DOCK, the guards' pins and DD-7's readers" % (n, extra))
    if C._pin(nl, "Q44", "3") == C.RET and C._pin(nl, "Q44", "2") != "GND":
        bad.append("Q44's drain is on the return and its source on %r, not the ground" % C._pin(nl, "Q44", "2"))
    bad += C.values(nl, "a")
    o, r = C.loop_pins(nl, "J_DOCK")
    if len(o) == 1 and len(r) == 1:
        bad += C.between(nl, o[0], r[0], "GND", "J_DOCK", nl["pins"].get("J_DOCK", {}))
    else:
        bad.append("J_DOCK carries the loop on %s and %s" % (o, r))
    return ("FAIL", bad) if bad else ("DRAWN", [])


def _switch(nl, u, vdd, tag):
    bad = C.props(nl, [(u, "2", "GND"), (u, "7", "GND")])
    if vdd is None or C._pin(nl, u, "4") != vdd:
        bad.append("%s's VDD (pin 4) on %r, not %s's supply %r" % (u, C._pin(nl, u, "4"), tag, vdd))
    for pin, what in (("1", "TRIP_TEST"), ("6", "VTEMP")):
        n = C._pin(nl, u, pin)
        others = _refs(nl, n) - {u}
        if n is None or not others or not _tp_only(nl, others):
            bad.append("%s's %s (pin %s) on %r reaches %s, not a test point alone" % (u, what, pin, n, sorted(others)))
    return bad


def _supply(nl, reg, sw, vdd, extra, tag):
    bad = []
    for r, p in C._nodes(nl, vdd) if vdd else []:
        if (r, p) in ((reg, "5"), (sw, "4")) or C._is_tp(nl, r) or r in extra:
            continue
        if not (r.startswith("C") and sorted(set(nl["pins"].get(r, {}).values())) == sorted({vdd, "GND"})):
            bad.append("%s's supply %s reaches %s.%s: the regulator's output feeds the switch only" % (tag, vdd, r, p))
    if C._pin(nl, reg, "3") is not None and C._pin(nl, reg, "3") in (vdd, C._pin(nl, reg, "1")):
        bad.append("%s's EN (pin 3) on its IN's net %r: TI forbids it (the 6.5 V clamp)" % (reg, C._pin(nl, reg, "3")))
    return bad


def _network(nl, ot, g, rg, cg, rpd, q, sw, tag):
    bad = []
    if g is None or ot is None or sorted({ot, g}) != C._two(nl, rg):
        bad.append("%s on %s, not from %s's OVERTEMP %r to %s's gate %r" % (rg, C._two(nl, rg), sw, ot, q, g))
    for ref in (cg, rpd):
        if not g or C._two(nl, ref) != sorted({g, "GND"}):
            bad.append("%s on %s, not from %s's gate %r to the ground" % (ref, C._two(nl, ref), q, g))
    if ot and _refs(nl, ot) != {sw, rg}:
        bad.append("%s's OVERTEMP %r reaches %s, not %s alone" % (sw, ot, sorted(_refs(nl, ot)), rg))
    return bad


def checks_thg_fs(nl):
    """Paths 1 and 2 by pin, and their separation."""
    bad = []
    try:
        r1, r2 = C._ohms(nl["comps"]["R260"]["value"]), C._ohms(nl["comps"]["R261"]["value"])
    except (KeyError, ValueError):
        r1 = r2 = 0.0
        bad.append("the pair R260 and R261 is not drawn as two resistors")
    if C._two(nl, "R260") != sorted({C.OUT, "THG_MID"}) or C._two(nl, "R261") != sorted({"THG_MID", C.RET}):
        bad.append("the pair is not in series from %s through THG_MID to %s" % (C.OUT, C.RET))
    mid = _refs(nl, "THG_MID") - {"R260", "R261"}
    if mid and not _tp_only(nl, mid):
        bad.append("THG_MID reaches %s beyond the pair and a test point" % sorted(mid))
    if min(r1, r2) < C.PAIR_LEAST or r1 + r2 > C.PAIR_MOST:
        bad.append("the pair %.0f + %.0f ohm outside %.0f ohm each and %.0f ohm in sum" % (r1, r2, C.PAIR_LEAST, C.PAIR_MOST))
    # path 1: U61 from DOCK_EN_OUT, U60, the gate network, Q60 on the return, and the clamp
    vdd, ot, g = C._pin(nl, "U61", "5"), C._pin(nl, "U60", "5"), C._pin(nl, "Q60", "1")
    bad += C.props(nl, [("U61", "1", C.OUT), ("U61", "2", "GND"), ("Q60", "3", C.RET), ("Q60", "2", "GND")])
    bad += _switch(nl, "U60", vdd, "U61")
    bad += _supply(nl, "U61", "U60", vdd, {"R268"}, "path 1")
    bad += _network(nl, ot, g, "R262", "C260", "R263", "Q60", "U60", "path 1")
    if g and _refs(nl, g) != {"R262", "C260", "R263", "Q60", "Q62"}:
        bad.append("Q60's gate net %s reaches %s, not R262, C260, R263, Q60 and the clamp's Q62" % (g, sorted(_refs(nl, g))))
    odn, cl = C._pin(nl, "U60", "3"), C._pin(nl, "Q62", "2")
    bad += C.props(nl, [("Q62", "1", odn), ("Q63", "1", odn), ("Q62", "3", g), ("Q63", "3", cl), ("Q63", "2", "GND")])
    if odn in (None, "GND", vdd, g):
        bad.append("U60's open drain (pin 3) on %r: it is the clamp's gate net" % odn)
    if cl in (None, "GND", g, odn) or _refs(nl, cl) != {"Q62", "Q63"}:
        bad.append("the clamp's middle %r reaches %s, not Q62's source and Q63's drain alone (two FETs in series)" % (cl, sorted(_refs(nl, cl))))
    on_odn = _refs(nl, odn) - {"U60", "Q62", "Q63", "R269"}
    if (on_odn and not _tp_only(nl, on_odn)) or not {"U60", "Q62", "Q63", "R269"} <= _refs(nl, odn):
        bad.append("THG_ODN reaches %s, not U60's open drain, the clamp's gates, R269 and a test point" % sorted(_refs(nl, odn)))
    pu = C._pin(nl, "R268", "2") if C._pin(nl, "R268", "1") == vdd else C._pin(nl, "R268", "1")
    if pu in (vdd, odn, None) or set(C._two(nl, "R268")) != {vdd, pu} or set(C._two(nl, "R269")) != {pu, odn} or _refs(nl, pu) != {"R268", "R269"}:
        bad.append("the pull-up is not R268 over R269 in series from U60's supply %r to THG_ODN %r" % (vdd, odn))
    # path 2: U63 from VBAT, U62, the gate network, Q61 on DOCK_EN_OUT
    vdd2, ot2, g2 = C._pin(nl, "U63", "5"), C._pin(nl, "U62", "5"), C._pin(nl, "Q61", "1")
    bad += C.props(nl, [("U63", "1", "VBAT"), ("U63", "2", "GND"), ("Q61", "3", C.OUT), ("Q61", "2", "GND")])
    bad += _switch(nl, "U62", vdd2, "U63")
    if C._pin(nl, "U62", "3") is not None:
        bad.append("U62's open drain (pin 3) on %r: path 2 uses its push-pull output only" % C._pin(nl, "U62", "3"))
    bad += _supply(nl, "U63", "U62", vdd2, set(), "path 2")
    bad += _network(nl, ot2, g2, "R270", "C272", "R271", "Q61", "U62", "path 2")
    if g2 and _refs(nl, g2) != {"R270", "C272", "R271", "Q61"}:
        bad.append("Q61's gate net %s reaches %s, not R270, C272, R271 and Q61" % (g2, sorted(_refs(nl, g2))))
    # apart: no net of one path is a net of the other
    one, two = {vdd, ot, g, odn, cl, pu} - {None}, {vdd2, ot2, g2} - {None}
    if one & two or len(two) != 3 or C._pin(nl, "U63", "1") == C.OUT:
        bad.append("the two paths share %s, or path 2's supply is DOCK_EN_OUT" % sorted(one & two))
    # values
    redrawn = {r_ for r_, _p in FS_VALUES}
    bad += ["%s value %r does not start %r (record l9stk 15.9 round 5, and record l8p's SESSION choices)" % (r_, nl["comps"].get(r_, {}).get("value"), pre)
            for r_, pre in C.THG_VALUES + FS_VALUES if (r_ not in redrawn or (r_, pre) in FS_VALUES)
            and not str(nl["comps"].get(r_, {}).get("value", "")).startswith(pre)]
    for q in ("Q60", "Q61"):
        if str(nl["comps"].get(q, {}).get("value", "")).split(":")[0].strip() != "2N7002":
            bad.append("the shunt %s is %r, not the kit's 2N7002" % (q, nl["comps"].get(q, {}).get("value")))
    return ("FAIL", bad) if bad else ("DRAWN", [])


def judge(nl):
    """{"EN": ..., "THG": ...} for a board A with the delta; NOT DRAWN when U62 is absent."""
    if not fs_drawn(nl):
        return {"EN": ("NOT DRAWN", ["U62 is absent"]), "THG": ("NOT DRAWN", ["U62 is absent"])}
    return {"EN": checks_en_fs(nl), "THG": checks_thg_fs(nl)}


def main(argv):
    if len(argv) != 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0].strip() + "\n")
        return 2
    nl = C.read_netlist(open(argv[0], "rb").read())
    res = judge(nl)
    for k, (v, why) in res.items():
        print("A %-4s %s%s" % (k, v, (": " + "; ".join(why)) if why else ""))
    vs = [v for v, _w in res.values()]
    return 3 if "NOT DRAWN" in vs else 4 if "FAIL" in vs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
