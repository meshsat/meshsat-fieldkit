#!/usr/bin/env python3
"""check_l8p_fs.py: Layer 8 record l8p ROUND 9 (MESHSAT-1357, 5 October 2026; the owner's review of checkpoint 3, part 22, item A):
board A's netlist read by pin for the fail-safe delta apply_gen_sch_a_thgfs.py, drawn after round 8's guard.

check_l8p_netlist.py (round 8's reader, whose digest other records print) is left as it is; this module reads a board A that carries
the delta, using that reader's netlist parser and helpers:
  EN   the loop on J_DOCK as check_l8p_netlist's EN group reads it, with C268 admitted beside C261 on DOCK_EN_OUT and the delta's
       redrawn values (R262 22 kOhm, C261 330 nF) read from FS_VALUES instead of round 8's rows;
  THG  round 8's THG group with the delta's changes: each switch's push-pull OVERTEMP through its own 1N4148W onto one cathode net
       feeding R262; U60's open drain (pin 3) on THG_ODN; Q60's gate net R262, C260, R263, Q60 and the clamp's Q62;
  FS   the delta itself (checks_fs): the cold clamp Q62 over Q63 in series from Q60's gate to the ground, both gates on THG_ODN; THG_ODN
       on the two open drains, the clamp's gates, R269 and a test point alone; the pull-up R268 over R269 from the switches' supply;
       U62 on the supply with its pad and GND on the ground, TRIP_TEST and VTEMP on a test point alone; C268 beside C261.
Usage:  check_l8p_fs.py NETLIST      Exit 0 DRAWN, 4 FAIL, 3 NOT DRAWN (U62 absent). Nothing is written."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import check_l8p_netlist as C  # noqa: E402

FS_ON_OUT = {("C268", "1"), ("C268", "2")}
FS_VALUES = (("U62", "LM26LVQISDX-130"), ("Q62", "2N7002"), ("Q63", "2N7002"), ("R268", "47k 1%"), ("R269", "47k 1%"), ("D60", "1N4148W"),
             ("D61", "1N4148W"), ("R262", "22k"), ("C261", "330n 50V"), ("C268", "330n 50V"), ("C269", "100n"))


def fs_drawn(nl):
    """Board A carries the delta: a second LM26LV, U62."""
    return str(nl["comps"].get("U62", {}).get("value", "")).startswith("LM26LV")


def checks_en_fs(nl):
    """check_l8p_netlist's EN group on a board with the delta: the same facts, C268 admitted on DOCK_EN_OUT, R262's row the delta's."""
    bad = C.props(nl, [("J_DOCK", "3", C.RET), ("J_DOCK", "4", "GND"), ("J_DOCK", "5", C.OUT)])
    if "RT1" in nl["comps"]:
        bad.append("RT1 is drawn: it is withdrawn (L8P-F07)")
    if C._two(nl, "R260") != sorted({C.OUT, "THG_MID"}) or C._two(nl, "R261") != sorted({"THG_MID", C.RET}):
        bad.append("the loop is not closed by the guard's pair: R260 on %s, R261 on %s" % (C._two(nl, "R260"), C._two(nl, "R261")))
    for n in (C.OUT, C.RET):
        base = {("J_DOCK", "5" if n == C.OUT else "3")}
        extra = sorted(C._nodes(nl, n) - base - C.DD7_ON[n] - C.THG_ON[n] - (FS_ON_OUT if n == C.OUT else set()))
        if extra:
            bad.append("%s reaches %s beyond J_DOCK, the guard's pins, C268 and DD-7's readers" % (n, extra))
    if C._pin(nl, "Q44", "3") == C.RET and C._pin(nl, "Q44", "2") != "GND":
        bad.append("Q44's drain is on the return and its source on %r, not the ground" % C._pin(nl, "Q44", "2"))
    bad += [x for x in C.values(nl, "a") if not x.startswith("R262 ")]
    o, r = C.loop_pins(nl, "J_DOCK")
    if len(o) == 1 and len(r) == 1:
        bad += C.between(nl, o[0], r[0], "GND", "J_DOCK", nl["pins"].get("J_DOCK", {}))
    else:
        bad.append("J_DOCK carries the loop on %s and %s" % (o, r))
    return ("FAIL", bad) if bad else ("DRAWN", [])


def checks_thg_fs(nl):
    """The thermal guard on board A by pin with the delta drawn: round 8's THG group (check_l8p_netlist.checks_thg) with the delta's
    changes (fs_drawn() selects them), then checks_fs."""
    if "U60" not in nl["comps"]:
        return ("NOT DRAWN", ["U60 is absent"])
    bad = []
    # the pair: two resistors in series, C.OUT to THG_MID to C.RET, the midpoint on nothing else but a test point
    try:
        r1, r2 = C._ohms(nl["comps"]["R260"]["value"]), C._ohms(nl["comps"]["R261"]["value"])
    except (KeyError, ValueError):
        r1 = r2 = 0.0
        bad.append("the pair R260 and R261 is not drawn as two resistors")
    if C._two(nl, "R260") != sorted({C.OUT, "THG_MID"}) or C._two(nl, "R261") != sorted({"THG_MID", C.RET}):
        bad.append("the pair is not in series from %s through THG_MID to %s: R260 on %s, R261 on %s" % (C.OUT, C.RET, C._two(nl, "R260"), C._two(nl, "R261")))
    mid = {r for r, _p in C._nodes(nl, "THG_MID")}
    if mid - {"R260", "R261"} and not all(C._is_tp(nl, x) for x in mid - {"R260", "R261"}):
        bad.append("THG_MID reaches %s beyond the pair and a test point" % sorted(mid - {"R260", "R261"}))
    if min(r1, r2) < C.PAIR_LEAST or r1 + r2 > C.PAIR_MOST:
        bad.append("the pair %.0f + %.0f ohm: each must be at least %.0f ohm (a short of the other keeps the held reading) and the sum at most %.0f ohm"
                   % (r1, r2, C.PAIR_LEAST, C.PAIR_MOST))
    # the switch: VDD from the regulator, its pad and GND on the ground, the push-pull OVERTEMP on the gate network, the open drain on nothing
    vdd, ot = C._pin(nl, "U60", "4"), C._pin(nl, "U60", "5")
    bad += C.props(nl, [("U60", "2", "GND"), ("U60", "7", "GND"), ("U61", "1", C.OUT), ("U61", "2", "GND")])
    if vdd is None or vdd != C._pin(nl, "U61", "5"):
        bad.append("U60's VDD (pin 4) on %r and U61's OUT (pin 5) on %r: the switch is not on the regulator's output" % (vdd, C._pin(nl, "U61", "5")))
    fs = fs_drawn(nl)
    if not fs and C._pin(nl, "U60", "3") is not None:
        bad.append("U60's open-drain output (pin 3) is on %r: the push-pull OVERTEMP (pin 5) is the one used" % C._pin(nl, "U60", "3"))
    drive = ot
    if fs:
        # round 9: each switch's push-pull OVERTEMP through its own 1N4148W (anode pin 2) onto one cathode net, THG_OR, which feeds R262
        drive = C._pin(nl, "D60", "1")
        for sw, d in (("U60", "D60"), ("U62", "D61")):
            if C._pin(nl, sw, "5") is None or C._pin(nl, d, "2") != C._pin(nl, sw, "5") or {r for r, _p in C._nodes(nl, C._pin(nl, sw, "5"))} != {sw, d}:
                bad.append("%s's push-pull OVERTEMP (pin 5) on %r does not reach %s's anode alone" % (sw, C._pin(nl, sw, "5"), d))
        if drive is None or C._pin(nl, "D61", "1") != drive or {r for r, _p in C._nodes(nl, drive)} != {"D60", "D61", "R262"}:
            bad.append("the diodes' cathodes (D60 %r, D61 %r) are not one net reaching R262 alone" % (drive, C._pin(nl, "D61", "1")))
    elif ot is None or ot != C._pin(nl, "R262", "1") and ot != C._pin(nl, "R262", "2"):
        bad.append("U60's push-pull OVERTEMP (pin 5) on %r does not reach R262 (%s)" % (ot, C._two(nl, "R262")))
    for pin, what in (("1", "TRIP_TEST"), ("6", "VTEMP")):
        n = C._pin(nl, "U60", pin)
        others = {r for r, _p in C._nodes(nl, n)} - {"U60"} if n else set()
        if n is None or not others or not all(C._is_tp(nl, x) for x in others):
            bad.append("U60's %s (pin %s) on %r reaches %s, not a test point alone" % (what, pin, n, sorted(others)))
    if C._pin(nl, "U61", "3") is not None and C._pin(nl, "U61", "3") in (C.OUT, C._pin(nl, "U61", "1")):
        bad.append("U61's EN (pin 3) on its IN's net %r: TI forbids it (the 6.5 V clamp)" % C._pin(nl, "U61", "3"))
    if vdd:
        for r, p in C._nodes(nl, vdd):
            if (r, p) in (("U61", "5"), ("U60", "4")) or C._is_tp(nl, r) or fs and ((r, p) == ("U62", "4") or r == "R268"):
                continue
            if not (r.startswith("C") and sorted(set(nl["pins"].get(r, {}).values())) == sorted({vdd, "GND"})):
                bad.append("the switch's supply %s reaches %s.%s: the regulator's output feeds the switch only" % (vdd, r, p))
    # the gate network and the shunt
    g = C._pin(nl, "Q60", "1")
    if g is None or drive is None or sorted({drive, g}) != C._two(nl, "R262"):
        bad.append("R262 on %s, not from OVERTEMP %r to Q60's gate %r" % (C._two(nl, "R262"), drive, g))
    for ref in ("C260", "R263"):
        if C._two(nl, ref) != sorted({g, "GND"}) if g else True:
            bad.append("%s on %s, not from Q60's gate %r to the ground" % (ref, C._two(nl, ref), g))
    want_g = {"R262", "C260", "R263", "Q60"} | ({"Q62"} if fs else set())
    if g and {r for r, _p in C._nodes(nl, g)} != want_g:
        bad.append("Q60's gate net %s reaches %s, not %s alone" % (g, sorted({r for r, _p in C._nodes(nl, g)}), ", ".join(sorted(want_g))))
    if fs:
        bad += checks_fs(nl, g, vdd)
    bad += C.props(nl, [("Q60", "3", C.RET), ("Q60", "2", "GND")])
    if str(nl["comps"].get("Q60", {}).get("value", "")).split(":")[0].strip() != "2N7002":
        bad.append("the shunt Q60 is %r, not the kit's 2N7002 (an AO3400A's leakage broke the window: L8P-F08)" % nl["comps"].get("Q60", {}).get("value"))
    redrawn = {r_ for r_, _p in FS_VALUES} if fs else set()
    bad += ["%s value %r does not start %r (record l9stk 15.9 round 5, and record l8p's SESSION choices)" % (r_, nl["comps"].get(r_, {}).get("value"), pre)
            for r_, pre in C.THG_VALUES + (FS_VALUES if fs else ()) if (r_ not in redrawn or (r_, pre) in FS_VALUES)
            and not str(nl["comps"].get(r_, {}).get("value", "")).startswith(pre)]
    return ("FAIL", bad) if bad else ("DRAWN", [])


def checks_fs(nl, g, vdd):
    """Round 9 (the owner's part 22 item A, V6-m7): the fail-safe delta by pin. The cold clamp Q62 over Q63 in series from Q60's gate to
    the ground, both gates on THG_ODN; THG_ODN on the two switches' open drains (pin 3), the clamp's gates, the pull-up's lower resistor
    and a test point alone; the pull-up R268 over R269 from the switches' supply; U62 on the supply, its pad and GND on the ground, its
    TRIP_TEST and VTEMP on a test point alone; C268 beside C261 on U61's input."""
    bad = []
    odn = C._pin(nl, "U60", "3")
    if odn is None or C._pin(nl, "U62", "3") != odn:
        bad.append("the open drains U60.3 (%r) and U62.3 (%r) are not one net" % (odn, C._pin(nl, "U62", "3")))
    cl = C._pin(nl, "Q62", "2")
    bad += C.props(nl, [("Q62", "1", odn), ("Q63", "1", odn), ("Q62", "3", g), ("Q63", "3", cl), ("Q63", "2", "GND"), ("U62", "2", "GND"),
                      ("U62", "7", "GND"), ("U62", "4", vdd), ("C268", "1", C.OUT), ("C268", "2", "GND")])
    if cl in (None, "GND", g, odn) or {r for r, _p in C._nodes(nl, cl)} != {"Q62", "Q63"}:
        bad.append("the clamp's middle %r reaches %s, not Q62's source and Q63's drain alone (two FETs in series)" % (cl, sorted({r for r, _p in C._nodes(nl, cl)} if cl else [])))
    on_odn = {r for r, _p in C._nodes(nl, odn)} if odn else set()
    if on_odn - {"U60", "U62", "Q62", "Q63", "R269"} and not all(C._is_tp(nl, x) for x in on_odn - {"U60", "U62", "Q62", "Q63", "R269"}) \
            or not {"U60", "U62", "Q62", "Q63", "R269"} <= on_odn:
        bad.append("THG_ODN reaches %s, not the two open drains, the clamp's gates, R269 and a test point" % sorted(on_odn))
    pu = C._pin(nl, "R268", "2") if C._pin(nl, "R268", "1") == vdd else C._pin(nl, "R268", "1")
    if pu in (vdd, odn, None) or set(C._two(nl, "R268")) != {vdd, pu} or set(C._two(nl, "R269")) != {pu, odn} \
            or {r for r, _p in C._nodes(nl, pu)} != {"R268", "R269"}:
        bad.append("the pull-up is not R268 over R269 in series from the supply %r to THG_ODN %r (R268 on %s, R269 on %s)" % (vdd, odn, C._two(nl, "R268"), C._two(nl, "R269")))
    for pin, what in (("1", "TRIP_TEST"), ("6", "VTEMP")):
        n = C._pin(nl, "U62", pin)
        others = {r for r, _p in C._nodes(nl, n)} - {"U62"} if n else set()
        if n is None or not others or not all(C._is_tp(nl, x) for x in others):
            bad.append("U62's %s (pin %s) on %r reaches %s, not a test point alone" % (what, pin, n, sorted(others)))
    if vdd is None or set(C._two(nl, "C269")) != {vdd, "GND"}:
        bad.append("C269 on %s, not U62's supply to the ground" % C._two(nl, "C269"))
    return bad


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
