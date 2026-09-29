#!/usr/bin/env python3
"""Stream rf2walk2 (MESHSAT-1357): the read-back of apply_b_chk12.py on board B's regenerated netlist and intent file.

It PARSES the netlist with tx_inhibit.parse_netlist (the RF-002 walk's own reader) and the intent file with json, and asserts
each change the draft makes, printing PASS or FAIL with what it read: the four resistor values, R551 between +5V_DEV and U543
pin 4 on its own net, U543 pin 3 left open, and in the intent file each module 3.3 V rail's loads naming every logic part the
netlist puts on that rail and +3V3_ZB's naming R536 to R538. The loads are compared with the NETLIST, not with a list typed
here: a logic part (a U part other than the module's receptacle) on +3V3_CM{s} whose ref the rail's loads omit fails. On set
12's committed files every change FAILS, which is the reading filed beside it.

usage: readback_chk12.py --tools <v2/ecad/tools> --board-dir <v2/ecad/pcb-b-compute-b19/out> [--out <file.txt>]"""
import hashlib, json, os, sys


def main(argv):
    args, it = {}, iter(argv)
    for a in it:
        args[a] = next(it, "")
    if "--tools" not in args or "--board-dir" not in args:
        print(__doc__); return 2
    sys.path.insert(0, args["--tools"])
    import tx_inhibit
    d = args["--board-dir"]
    npath, ipath = os.path.join(d, "pcb-b-compute.net"), os.path.join(d, "pcb-b-compute-intent.json")
    nl = tx_inhibit.parse_netlist(npath)
    intent = json.load(open(ipath, encoding="utf-8"))
    rails = intent.get("rails", {})
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
    out = ["The read-back of apply_b_chk12.py (stream rf2walk2, tools/readback_chk12.py)",
           "  netlist v2/%s  sha256/16 %s" % (npath.split("/v2/")[-1], sha(npath)),
           "  intent  v2/%s  sha256/16 %s" % (ipath.split("/v2/")[-1], sha(ipath)), ""]
    fails = 0

    def check(ok, what):
        nonlocal fails
        fails += not ok
        out.append("%s  %s" % ("PASS" if ok else "FAIL", what))

    for ref, val in (("R238", "49.9k 1%"), ("R532", "2.7k 1%"), ("R527", "20.0k 1%"), ("R551", "49.9k 1%")):
        got = (nl["comps"].get(ref) or {}).get("value", "")
        check(got.startswith(val), "value %s %r (expected %r)" % (ref, got[:30], val))
    pin = nl["pin"]
    r551 = sorted([pin.get(("R551", "1"), ""), pin.get(("R551", "2"), "")])
    check(r551 == sorted(["+5V_DEV", "RB_TD_CT"]), "R551 between %s (expected +5V_DEV and RB_TD_CT)" % " and ".join(r551))
    ct = sorted((r, p) for r, p, _f in nl["nets"].get("RB_TD_CT", []))
    check(ct == [("R551", "2"), ("U543", "4")] or ct == [("R551", "1"), ("U543", "4")],
          "net RB_TD_CT carries %s (expected U543 pin 4 and one R551 pin)" % ", ".join("%s.%s" % x for x in ct))
    mr = pin.get(("U543", "3"), "")
    check(not mr or mr.startswith("unconnected-"), "U543 pin 3 (MR) open: %r" % mr)
    for s in (1, 2, 3):
        rail = "+3V3_CM%d" % s
        logic = sorted({r for r, _p, _f in nl["nets"].get(rail, []) if r.startswith("U") and r != "U3%dA" % (s - 1)})
        loads = (rails.get(rail) or {}).get("loads", {})
        miss = [r for r in logic if r not in loads]
        check(not miss, "%s loads name every logic part on it (%d on the netlist; missing %s)" % (rail, len(logic), ", ".join(miss) or "none"))
    zb = (rails.get("+3V3_ZB") or {}).get("loads", {})
    check(all(r in zb for r in ("R536", "R537", "R538")), "+3V3_ZB loads name R536, R537, R538 (%s)" % ", ".join(sorted(zb)))
    out += ["", "RESULT: %s" % ("every check holds" if not fails else "%d check(s) fail" % fails)]
    text = "\n".join(out) + "\n"
    if "--out" in args:
        if "/v2/ecad/" in os.path.abspath(args["--out"]):
            print("refused: the output must not lie under v2/ecad"); return 2
        open(args["--out"], "w", encoding="utf-8").write(text)
    print(text, end="")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
