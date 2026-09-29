#!/usr/bin/env python3
"""Stream d4emcon (MESHSAT-1357): a self-test of readback_d4e.py's positive path, so that its FAIL on the committed netlists is
not the only thing it has ever printed. From board C's committed netlist it writes, in a directory the caller names (never
under v2/ecad), a SYNTHETIC netlist carrying exactly what apply_c_d4e_f1.py asks the generator for (U9 pin 4 moved to a new net
EMCON_HW_DRV with R52 pin 1; R52 pin 2 and D23 pin 2 on EMCON_HW; D23 pin 1 on TX_INHIBIT_n; the two parts with their values),
then runs the read-back on it (every check must PASS) and on three mutants (U9 pin 4 left on EMCON_HW; D23 pin 1 missing; R52's
value changed), each of which must FAIL. It is a test of the read-back, not of the circuit: the synthetic file is text edited
from the committed one and is no substitute for the regenerated netlist.

usage: selftest_readback_c.py --tools <v2/ecad/tools> --net <committed pcb-c-display.net> --dir <scratch dir>"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def comp(ref, value):
    return ('    (comp (ref "%s")\n      (value "%s")\n      (footprint "x")\n      (libsource (lib "Device") (part "R") (description "x"))\n'
            '      (sheetpath (names "/") (tstamps "/")))\n' % (ref, value))


def node(ref, pin):
    return '      (node (ref "%s") (pin "%s") (pintype "passive"))' % (ref, pin)


def synth(text, keep_u9=False, drop_d23_k=False, r52_value="330R 1%"):
    t = text
    u9 = node("U9", "4").replace('(pintype', '(pinfunction "EMCON_HW") (pintype')
    if t.count(u9) != 1: raise SystemExit("anchor for U9 pin 4 not found once")
    new_nodes = node("R52", "2") + "\n" + node("D23", "2")
    t = t.replace(u9, (u9 + "\n" if keep_u9 else "") + new_nodes)
    m = re.search(r'\(net \(code "\d+"\) \(name "/TX_INHIBIT_n"\)[^\n]*\n', t)
    if not m: raise SystemExit("TX_INHIBIT_n not found")
    if not drop_d23_k:
        t = t[:m.end()] + node("D23", "1") + "\n" + t[m.end():]
    k = t.index("  (nets\n") + len("  (nets\n")
    t = t[:k] + '    (net (code "9999") (name "/EMCON_HW_DRV") (class "Default")\n' + node("U9", "4") + "\n" + node("R52", "1") + ")\n" + t[k:]
    c = t.index("  (components\n") + len("  (components\n")
    t = t[:c] + comp("R52", r52_value) + comp("D23", "BAT46W-7-F") + t[c:]
    return t


def run(tools, path):
    r = subprocess.run([sys.executable, os.path.join(HERE, "readback_d4e.py"), "--tools", tools, "--board", "C", path], capture_output=True, text=True)
    return r.returncode, r.stdout


def main(argv):
    a = dict(zip(argv[0::2], argv[1::2]))
    if not {"--tools", "--net", "--dir"} <= set(a): print(__doc__); return 2
    if "/v2/ecad/" in os.path.abspath(a["--dir"]) + "/": print("refused: --dir must not lie under v2/ecad"); return 2
    os.makedirs(a["--dir"], exist_ok=True)
    text = open(a["--net"], encoding="utf-8").read()
    cases = [("synthetic after", {}, 0), ("mutant: U9 pin 4 still on EMCON_HW", {"keep_u9": True}, 1),
             ("mutant: D23 pin 1 missing", {"drop_d23_k": True}, 1), ("mutant: R52 at 3.3k", {"r52_value": "3.3k"}, 1)]
    bad = 0
    for name, kw, want in cases:
        p = os.path.join(a["--dir"], "c-%s.net" % re.sub(r"\W+", "-", name))
        open(p, "w", encoding="utf-8").write(synth(text, **kw))
        rc, out = run(a["--tools"], p)
        ok = (rc == 0) == (want == 0)
        bad += not ok
        print("%s  %-38s read-back exit %d (%s)" % ("PASS" if ok else "FAIL", name, rc, out.strip().splitlines()[-1]))
    print("RESULT: %s" % ("the read-back passes the synthetic after-netlist and fails every mutant" if not bad else "%d case(s) wrong" % bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
