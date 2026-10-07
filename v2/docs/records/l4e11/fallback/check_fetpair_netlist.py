#!/usr/bin/env python3
"""check_fetpair_netlist.py: the battery FETs of board A read back from a regenerated board A netlist (record l4e11 round FET, task
L4A-70, MESHSAT-1357, 7 October 2026): the drawn three (Q39, Q40, Q42, apply_gen_sch_a_charger.py) or the fallback pair (Q39, Q40,
apply_gen_sch_a_fetpair.py after it).

Usage:  check_fetpair_netlist.py NETLIST [--want pair|three]      (default: pair)

NETLIST is a KiCad export form E netlist of board A (the box's `kicad-cli sch export netlist`, or record l8p's gen_netlist.py run on a
scratch copy of gen_sch_a.py with the drafts applied in L4-E9's order; the tests do the second). It parses the netlist (this record's
check_dd7_netlist.py reader) and reads:
  SET    the battery FETs are exactly the wanted set: each a "BUK6Y10-30PX 30 V P-FET" with pads 1 to 3 (source) on VBAT, pad 4 (gate)
         on CH_BATDRV and pad 5 (the drain tab) on CH_BATQ, so its body diode points from the pack side to VSYS; Q42 absent for the pair;
  GATE   CH_BATDRV reaches U3's pin 21 (BATDRV), the set's gates and, where DD-7 is drawn, the inhibit Q49's drain (pin 3), and nothing
         else: a further gate on BATDRV is a gate load TI's 5 nF reading has not seen;
  DRAIN  CH_BATQ reaches the set's drain tabs, R17's battery-FET pad and R149 (SRP's filter) and nothing else;
  SOURCE every pad of the set off VBAT, CH_BATDRV and CH_BATQ fails.
It reads circuit connectivity only: TI's 5 nF and the bars are the record's (l4e11_fet.py), never a netlist property.
Exit 0: DRAWN; 4: FAIL (each failure printed); 3: NOT DRAWN (no CH_BATDRV: the charger draft is not applied). Nothing is written."""
import hashlib
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("l4e11_check_dd7_reader", os.path.join(os.path.dirname(HERE), "check_dd7_netlist.py"))
_dd7 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(_dd7)
read_netlist = _dd7.read_netlist

SETS = {"pair": ("Q39", "Q40"), "three": ("Q39", "Q40", "Q42")}
VALUE = "BUK6Y10-30PX 30 V P-FET"
PADS = {"1": "VBAT", "2": "VBAT", "3": "VBAT", "4": "CH_BATDRV", "5": "CH_BATQ"}


def judge(raw, want="pair"):
    comps, pins, on = read_netlist(raw)
    if "CH_BATDRV" not in on:
        return "NOT DRAWN", ["no CH_BATDRV net: the charger draft is not applied"]
    bad = []
    fets = SETS[want]
    drawn = sorted(r for r, v in comps.items() if v.startswith(VALUE))
    if drawn != sorted(fets):
        bad.append("the battery FETs drawn are %s, wanted %s" % (drawn, list(fets)))
    for ref in fets:
        got = pins.get(ref, {})
        if not comps.get(ref, "").startswith(VALUE):
            bad.append("%s is not the BUK6Y10-30PX battery FET (%r)" % (ref, comps.get(ref, "absent")[:40]))
        for p, n in PADS.items():
            if got.get(p) != n:
                bad.append("%s.%s on %r, wanted %s" % (ref, p, got.get(p), n))
        extra = sorted(set(got) - set(PADS))
        if extra:
            bad.append("%s carries pads %s the draft does not draw" % (ref, extra))
    gate_ok = {"U3"} | set(fets) | ({"Q49"} if "Q49" in comps else set())
    gate = on.get("CH_BATDRV", set())
    if gate != gate_ok:
        bad.append("CH_BATDRV reaches %s, wanted %s" % (sorted(gate), sorted(gate_ok)))
    if pins.get("U3", {}).get("21") != "CH_BATDRV":
        bad.append("U3.21 (BATDRV) on %r, wanted CH_BATDRV" % pins.get("U3", {}).get("21"))
    if "Q49" in comps and pins.get("Q49", {}).get("3") != "CH_BATDRV":
        bad.append("Q49.3 on %r: the inhibit does not hold the gates" % pins.get("Q49", {}).get("3"))
    drain_ok = set(fets) | {"R17", "R149"}
    if on.get("CH_BATQ", set()) != drain_ok:
        bad.append("CH_BATQ reaches %s, wanted %s" % (sorted(on.get("CH_BATQ", set())), sorted(drain_ok)))
    return ("FAIL", bad) if bad else ("DRAWN", [])


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    want = "pair"
    if "--want" in argv:
        i = argv.index("--want")
        want = argv[i + 1] if i + 1 < len(argv) else ""
        args = [a for a in args if a != want]
    if len(args) != 1 or want not in SETS:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0].strip() + "\n")
        return 2
    raw = open(args[0], "rb").read()
    v, why = judge(raw, want)
    print("board A netlist sha256 %s" % hashlib.sha256(raw).hexdigest()[:16])
    for w in why:
        print("  %s" % w)
    print("the battery FETs, wanted the %s (record l4e11 round FET): %s" % (want, v))
    return {"DRAWN": 0, "FAIL": 4, "NOT DRAWN": 3}[v]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
