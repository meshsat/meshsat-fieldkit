#!/usr/bin/env python3
"""Stream rf2walk2 (MESHSAT-1357): a self-test of readback_chk12.py's positive path. From board B's committed netlist and
intent file it writes, in a directory the caller names (never under v2/ecad), a SYNTHETIC pair carrying exactly what
apply_b_chk12.py and its follow-up apply_b_chk12_led.py ask the generator for (R238 49.9k 1%, R532 2.7k 1%, R527 20.0k 1%, R551 49.9k 1% from +5V_DEV to a new net
RB_TD_CT that also takes U543 pin 4, the module rails' and +3V3_ZB's loads), runs the read-back on it (every check must PASS),
and on three mutants (R551 missing, R532 left at 2.2k, one gate left out of +3V3_CM3's loads), each of which must FAIL. It
tests the read-back, not the circuit: the synthetic files are edited text and no substitute for the regenerated ones.

usage: selftest_readback_chk12.py --tools <v2/ecad/tools> --board-dir <v2/ecad/pcb-b-compute-b19/out> --dir <scratch dir>"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def set_value(t, ref, val):
    m = re.search(r'\(comp \(ref "%s"\)\n\s+\(value "[^"]*"\)' % re.escape(ref), t)
    if not m: raise SystemExit("comp %s not found" % ref)
    return t[:m.start()] + re.sub(r'\(value "[^"]*"\)', '(value "%s")' % val, t[m.start():m.end()]) + t[m.end():]


def synth(net_text, intent, r551=True, r532="2.7k 1%", drop_load=None):
    t = set_value(net_text, "R238", "49.9k 1%")
    t = set_value(t, "R532", r532)
    t = set_value(t, "R527", "20.0k 1%")
    old = re.search(r'\s*\(node \(ref "U543"\) \(pin "4"\)[^\n]*\)', t)
    if not old: raise SystemExit("U543 pin 4 node not found")
    t = t[:old.start()] + t[old.end():]
    k = t.index("  (nets\n") + len("  (nets\n")
    nodes = '      (node (ref "U543") (pin "4") (pintype "passive"))'
    if r551:
        nodes += '\n      (node (ref "R551") (pin "2") (pintype "passive"))'
        m = re.search(r'\(net \(code "\d+"\) \(name "/\+5V_DEV"\)[^\n]*\n', t)
        t = t[:m.end()] + '      (node (ref "R551") (pin "1") (pintype "passive"))\n' + t[m.end():]
        c = t.index("  (components\n") + len("  (components\n")
        t = t[:c] + ('    (comp (ref "R551")\n      (value "49.9k 1%")\n      (footprint "x")\n'
                     '      (libsource (lib "Device") (part "R") (description "x"))\n      (sheetpath (names "/") (tstamps "/")))\n') + t[c:]
        k = t.index("  (nets\n") + len("  (nets\n")
    t = t[:k] + '    (net (code "99999") (name "/RB_TD_CT") (class "Default")\n' + nodes + ")\n" + t[k:]
    j = json.loads(json.dumps(intent))
    gates = {1: ["U112", "U113", "U114", "U115"], 2: ["U212", "U213", "U214", "U215", "U220", "U554"],
             3: ["U312", "U313", "U314", "U315"] + ["U%d" % u for u in range(544, 554)]}
    for s, g in gates.items():
        for u in g:
            if u != drop_load: j["rails"]["+3V3_CM%d" % s]["loads"][u] = 0.001
    for s in (1, 2, 3):                                   # CHK12-LED (apply_b_chk12_led.py): the LED feeds
        j["rails"]["+3V3_CM%d" % s]["loads"]["Q%d01" % s] = 0.0033; j["rails"]["+3V3_CM%d" % s]["loads"]["R%d48" % s] = 0.0033
    for r in ("R536", "R537", "R538"): j["rails"]["+3V3_ZB"]["loads"][r] = 0.00071
    return t, j


def main(argv):
    a = dict(zip(argv[0::2], argv[1::2]))
    if not {"--tools", "--board-dir", "--dir"} <= set(a): print(__doc__); return 2
    if "/v2/ecad/" in os.path.abspath(a["--dir"]) + "/": print("refused: --dir must not lie under v2/ecad"); return 2
    net_text = open(os.path.join(a["--board-dir"], "pcb-b-compute.net"), encoding="utf-8").read()
    intent = json.load(open(os.path.join(a["--board-dir"], "pcb-b-compute-intent.json"), encoding="utf-8"))
    cases = [("synthetic after", {}, 0), ("mutant: R551 missing", {"r551": False}, 1),
             ("mutant: R532 left at 2.2k", {"r532": "2.2k 1%"}, 1), ("mutant: U550 left out of +3V3_CM3", {"drop_load": "U550"}, 1)]
    bad = 0
    for name, kw, want in cases:
        d = os.path.join(a["--dir"], re.sub(r"\W+", "-", name)); os.makedirs(d, exist_ok=True)
        t, j = synth(net_text, intent, **kw)
        open(os.path.join(d, "pcb-b-compute.net"), "w", encoding="utf-8").write(t)
        json.dump(j, open(os.path.join(d, "pcb-b-compute-intent.json"), "w", encoding="utf-8"))
        r = subprocess.run([sys.executable, os.path.join(HERE, "readback_chk12.py"), "--tools", a["--tools"], "--board-dir", d],
                           capture_output=True, text=True)
        ok = (r.returncode == 0) == (want == 0)
        bad += not ok
        print("%s  %-36s read-back exit %d (%s)" % ("PASS" if ok else "FAIL", name, r.returncode, r.stdout.strip().splitlines()[-1]))
    print("RESULT: %s" % ("the read-back passes the synthetic after-files and fails every mutant" if not bad else "%d case(s) wrong" % bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
