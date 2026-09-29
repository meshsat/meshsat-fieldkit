#!/usr/bin/env python3
"""The read-back's own test (stream s117, MESHSAT-1357, 29 September 2026): readback_s117.check() must FAIL on board A's
committed netlist, PASS on a synthetic netlist that carries exactly what apply_gen_sch_a_s117.py draws, and FAIL on each
mutant of that synthetic netlist (one wrong thing at a time); against() must hold the synthetic netlist to exactly the
change and refuse one more. The synthetic netlist is the committed one, parsed, with the
drawn change made to the parsed structure; nothing is written to disk. Exit 0 when every case reads as it must."""
import copy, os, subprocess, sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import readback_s117 as RB
N = RB.N


def put(doc, ref, value, footprint, pinmap):
    """Set a part's value, land and pins in the parsed structure, moving its pins between nets."""
    doc["components"][ref] = {"value": value, "footprint": footprint, "fields": {}, "libpart": ""}
    for (r, p) in [k for k in doc["pin_net"] if k[0] == ref]:
        old = doc["pin_net"].pop((r, p))
        doc["nets"][old] = [x for x in doc["nets"][old] if (x[0], x[1]) != (r, p)]
    for p, net in pinmap.items():
        doc["pin_net"][(ref, p)] = net
        doc["nets"].setdefault(net, []).append((ref, p, "", "passive"))


def drop(doc, ref):
    for (r, p) in [k for k in doc["pin_net"] if k[0] == ref]:
        old = doc["pin_net"].pop((r, p))
        doc["nets"][old] = [x for x in doc["nets"][old] if (x[0], x[1]) != (r, p)]
    doc["components"].pop(ref, None)


R0603, C0603 = "Resistor_SMD:R_0603_1608Metric", "Capacitor_SMD:C_0603_1608Metric"


def after(base):
    d = copy.deepcopy(base)
    put(d, "L2", "4.7uH XAL1010-472ME (Isat 25.4 A)", "Inductor_SMD:L_Coilcraft_XAL1010-XXX", {"1": "CH_SW1", "2": "CH_SW2"})
    put(d, "R25", "40.2k 1%", R0603, {"1": "CH_COMP1", "2": "CH_COMP1C"})
    put(d, "C26", "4.7n", C0603, {"1": "CH_COMP1C", "2": "GND"})
    put(d, "C234", "33p", C0603, {"1": "CH_COMP1", "2": "GND"})
    put(d, "R220", "15k 1%", R0603, {"1": "CH_COMP2", "2": "CH_COMP2C"})
    put(d, "C235", "680p", C0603, {"1": "CH_COMP2C", "2": "GND"})
    put(d, "C27", "15p NP0", C0603, {"1": "CH_COMP2", "2": "GND"})
    put(d, "R219", "191k 1%", R0603, {"1": "IADPT", "2": "GND"})
    put(d, "C233", "33p", C0603, {"1": "IADPT", "2": "GND"})
    return d


def mutants(good):
    out = []

    def m(name, fn):
        d = copy.deepcopy(good); fn(d); out.append((name, d))
    m("L2 left on the XAL60xx land", lambda d: put(d, "L2", "4.7uH XAL1010-472ME (Isat 25.4 A)", "Inductor_SMD:L_Coilcraft_XAL6060-XXX", {"1": "CH_SW1", "2": "CH_SW2"}))
    m("L2 the 3.3 uH part", lambda d: put(d, "L2", "3.3uH XAL1010-332ME (Isat 27.4 A)", "Inductor_SMD:L_Coilcraft_XAL1010-XXX", {"1": "CH_SW1", "2": "CH_SW2"}))
    m("IADPT resistor 169k (the 3.3 uH row)", lambda d: put(d, "R219", "169k 1%", R0603, {"1": "IADPT", "2": "GND"}))
    m("IADPT resistor at 5 percent", lambda d: put(d, "R219", "191k 5%", R0603, {"1": "IADPT", "2": "GND"}))
    m("IADPT resistor with no tolerance", lambda d: put(d, "R219", "191k", R0603, {"1": "IADPT", "2": "GND"}))
    m("IADPT resistor to +3V3", lambda d: put(d, "R219", "191k 1%", R0603, {"1": "IADPT", "2": "+3V3"}))
    m("IADPT capacitor 150 pF", lambda d: put(d, "C233", "150p", C0603, {"1": "IADPT", "2": "GND"}))
    m("IADPT capacitor missing", lambda d: drop(d, "C233"))
    m("IADPT resistor missing", lambda d: drop(d, "R219"))
    m("a second resistor on IADPT", lambda d: put(d, "R999", "191k 1%", R0603, {"1": "IADPT", "2": "GND"}))
    m("R25 at the 800 kHz row's 16.9k", lambda d: put(d, "R25", "16.9k 1%", R0603, {"1": "CH_COMP1", "2": "CH_COMP1C"}))
    m("C26 at the 800 kHz row's 3.3 nF", lambda d: put(d, "C26", "3.3n", C0603, {"1": "CH_COMP1C", "2": "GND"}))
    m("C234 missing", lambda d: drop(d, "C234"))
    m("C235 at the 800 kHz row's 1200 pF", lambda d: put(d, "C235", "1.2n", C0603, {"1": "CH_COMP2C", "2": "GND"}))
    m("C27 left at 1 nF", lambda d: put(d, "C27", "1n", C0603, {"1": "CH_COMP2", "2": "GND"}))
    m("R220 on the wrong net", lambda d: put(d, "R220", "15k 1%", R0603, {"1": "CH_COMP1", "2": "CH_COMP2C"}))
    m("C121 removed (the 800 kHz permission)", lambda d: drop(d, "C121"))
    return out


def main():
    base = N.load(RB.DEFAULT)
    fails = 0
    r0 = RB.check(base)
    ok0 = all(ok for _, ok, _ in r0)
    print("committed netlist: %s (%d of %d checks hold) -> %s" % ("PASS" if ok0 else "FAIL", sum(ok for _, ok, _ in r0), len(r0),
                                                                "as it must" if not ok0 else "WRONG"))
    fails += ok0
    good = after(base)
    r1 = RB.check(good)
    ok1 = all(ok for _, ok, _ in r1)
    print("synthetic after:   %s (%d of %d) -> %s" % ("PASS" if ok1 else "FAIL", sum(ok for _, ok, _ in r1), len(r1),
                                                     "as it must" if ok1 else "WRONG"))
    if not ok1:
        for n, ok, det in r1:
            if not ok: print("    FAIL %s: %s" % (n, det))
    fails += not ok1
    for name, d in mutants(good):
        r = RB.check(d)
        bad = [n for n, ok, _ in r if not ok]
        print("mutant %-40s %s -> %s" % (name + ":", "FAIL (%s)" % "; ".join(bad) if bad else "PASS", "as it must" if bad else "WRONG"))
        fails += not bad
    # --against: the synthetic regeneration against the committed netlist holds to exactly the change; one more change fails
    ra = RB.against(good, base)
    oka = all(ok for _, ok, _ in ra)
    print("against, synthetic after vs committed: %s -> %s" % ("PASS" if oka else "FAIL", "as it must" if oka else "WRONG"))
    fails += not oka
    for name, fn in (("R24's value moved too", lambda d: put(d, "R24", "22k", R0603, {"1": "PSYS", "2": "GND"})),
                     ("a sixth new part", lambda d: put(d, "C999", "100n", C0603, {"1": "IADPT", "2": "GND"})),
                     ("R219 drawn to +3V3 instead of GND", lambda d: put(d, "R219", "191k 1%", R0603, {"1": "IADPT", "2": "+3V3"}))):
        d = copy.deepcopy(good); fn(d)
        bad = [n for n, ok, _ in RB.against(d, base) if not ok]
        print("against, mutant %-34s %s -> %s" % (name + ":", "FAIL (%s)" % "; ".join(bad) if bad else "PASS", "as it must" if bad else "WRONG"))
        fails += not bad
    # --fets (the second issue): the four FETs as apply_gen_sch_a_fets_s117.py draws them
    PP = "Package_SO:PowerPAK_SO-8_Single"
    def with_fets(d0):
        d = copy.deepcopy(d0)
        for ref, (part, pinmap) in RB.FETS.items():
            put(d, ref, "%s 30 V N-FET" % part, PP, pinmap)
        return d
    gf = with_fets(good)
    rf = RB.check_fets(base)
    print("fets, committed netlist: %s -> %s" % ("PASS" if all(ok for _, ok, _ in rf) else "FAIL", "WRONG" if all(ok for _, ok, _ in rf) else "as it must"))
    fails += all(ok for _, ok, _ in rf)
    okf = all(ok for _, ok, _ in RB.check(gf) + RB.check_fets(gf) + RB.against(gf, base, True))
    print("fets, synthetic after with the FETs, against the committed netlist (--fets): %s -> %s" % ("PASS" if okf else "FAIL", "as it must" if okf else "WRONG"))
    fails += not okf
    bad0 = [n for n, ok, _ in RB.against(gf, base, False) if not ok]
    print("fets, the same without --fets: %s -> %s" % ("FAIL (%s)" % "; ".join(bad0) if bad0 else "PASS", "as it must" if bad0 else "WRONG"))
    fails += not bad0
    for name, fn in (("Q7 left a CSD18510Q5B", lambda d: put(d, "Q7", "CSD18510Q5B 40 V N-FET", PP, RB.FETS["Q7"][1])),
                     ("Q7 and Q8 swapped", lambda d: (put(d, "Q7", "CSD17577Q5A 30 V N-FET", PP, RB.FETS["Q7"][1]), put(d, "Q8", "CSD17578Q5A 30 V N-FET", PP, RB.FETS["Q8"][1]))),
                     ("Q9 on another land", lambda d: put(d, "Q9", "CSD17577Q5A 30 V N-FET", "Package_SON:VSON-8_5x6mm", RB.FETS["Q9"][1])),
                     ("Q10 drain and source swapped", lambda d: put(d, "Q10", "CSD17577Q5A 30 V N-FET", PP, {"1": "VBAT", "2": "VBAT", "3": "VBAT", "4": "CH_HIDRV2", "5": "CH_SW2"}))):
        d = copy.deepcopy(gf); fn(d)
        bad = [n for n, ok, _ in RB.check_fets(d) if not ok]
        print("fets, mutant %-30s %s -> %s" % (name + ":", "FAIL (%s)" % "; ".join(bad) if bad else "PASS", "as it must" if bad else "WRONG"))
        fails += not bad
    print("selftest_readback_s117: %s" % ("every case as it must" if not fails else "%d case(s) WRONG" % fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
