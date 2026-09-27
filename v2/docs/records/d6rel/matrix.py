#!/usr/bin/env python3
"""The reviewer's four-case matrix of finding H3-01, run through the COMMAND LINE of a reliability.py.

Worker d6rel, MESHSAT-1357, 27 to 28 September 2026. The independent review of handover H3
(v2/docs/reviews/2026-09-27-h3-independent-review.md, section "H3-01: REL-001's completeness can be false") ran
the tool's command line in isolated fixture directories and found two silent cases. This script builds the same
four fixtures outside the tree and runs ONE tool on them, so the same fixtures can be shown to the unrepaired
tool and to the repaired one:

  1  one declared JST connector                                   the control: must PASS
  2  the same plus an undeclared IDC header                       the rejection control: must FAIL
  3  the same plus an undeclared "RJ45 MagJack"                   SILENT on the unrepaired tool: must FAIL
  4  board A's own declaration and no netlist at all              SILENT on the unrepaired tool: must be INCONCLUSIVE

Nothing is written in the tree: every fixture and every verdict lands in a temporary directory, and the tool is
run with VERDICT_DIR pointing there. No board has been built; these are readings of fixture netlists.

Usage: matrix.py <tools dir> <reliability.py to run> [--list <pcb_reliability.yaml for case 4>]
  <tools dir>            the tree's v2/ecad/tools (verdict.py and the modules the tool imports are taken from it)
  <reliability.py>       the tool under test. The unrepaired one is
                         git show 73ae2f21:v2/ecad/tools/reliability.py > <dir outside the tree>/reliability.py
  --list                 the declared list whose board A declaration case 4 uses (default: the one beside the tool
                         under test, else the tree's)
Exit 0 when the four cases read PASS, FAIL, FAIL, INCONCLUSIVE; 1 otherwise.
"""
import os, sys, json, hashlib, tempfile, subprocess

NETLIST = """(export (version "E")
  (design
    (source "fixture")
    (date "2026-09-28T00:00:00+0000")
    (tool "fixture written by v2/docs/records/d6rel/matrix.py"))
  (components
%s  )
  (nets
%s  )
)
"""

# ref: (value, footprint, pins)
JST = ("JST-VH socket, 10 A: 5 V from the fixture: + -", "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", 2)
IDC = ("fixture ribbon (IDC 2x5)", "Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical", 10)
RJ45 = ("RJ45 MagJack", "Connector_RJ:RJ45_Amphenol_RJHSE5380", 9)

# ONE SHEET FOR BOTH TOOLS. The unrepaired tool asks a class for name, basis, load and measure and ignores the
# rest; the repaired one asks for the figure's document, page and words. A sheet carrying both is judged by
# each tool on the fields it reads, so the two runs differ in the tool and in nothing else.
SHEET = """schema_version: "2.0.0"
inventory:
  reference_classes:
    J: {kind: mechanical, what: "a connector"}
  footprint:
    mechanical_libraries: ["Connector*"]
    mechanical_names: []
    soldered_libraries: []
    soldered_names: []
boards:
 a:
   classes:
    - name: "the power header"
      refs: ["J_PWR1"]
      footprints: ["Connector_JST:JST_VH_*"]
      cycles: 30
      basis: "a fixture figure, from the fixture document"
      source: {document: "v2/vendor/fixture/jst-vh-fixture.pdf", sha256_16: "%s", page: "1", words: "fixture: 30 cycles"}
      load: "a lead pulled during service"
      measure: "the lead is tied beside the header"
"""
DOC = b"%PDF-1.4 fixture document of v2/docs/records/d6rel/matrix.py: 30 cycles\n"


def netlist(parts):
    comps = "".join('    (comp (ref "%s")\n      (value "%s")\n      (footprint "%s"))\n' % (r, v, f)
                    for r, (v, f, _n) in sorted(parts.items()))
    nets, code = "", 0
    for r, (_v, _f, n) in sorted(parts.items()):
        for pin in range(1, n + 1):
            code += 1
            nets += ('    (net (code "%d") (name "/%s_%d") (class "Default")\n      (node (ref "%s") (pin "%d") (pintype "passive")))\n'
                     % (code, r, pin, r, pin))
    return NETLIST % (comps, nets)


def fixture(root, name, parts, sheet):
    d = os.path.join(root, name)
    ecad = os.path.join(d, "ecad"); vendor = os.path.join(d, "vendor", "fixture")
    os.makedirs(vendor); os.makedirs(os.path.join(d, "out"))
    open(os.path.join(vendor, "jst-vh-fixture.pdf"), "wb").write(DOC)
    if parts is not None:
        # The reviewer's form: the board's own stem directory. No directory of the routeflow profile's name
        # exists in a fixture, so the declared-phase resolution falls to the stem, as it does for board E5.
        os.makedirs(os.path.join(ecad, "pcb-a-power", "out"))
        open(os.path.join(ecad, "pcb-a-power", "out", "pcb-a-power.net"), "w", encoding="utf-8").write(netlist(parts))
    else:
        os.makedirs(ecad)
    p = os.path.join(d, "list.yaml")
    open(p, "w", encoding="utf-8").write(sheet)
    return d, ecad, os.path.join(d, "vendor"), p


def run(tools, tool, d, ecad, vendor, sheet):
    env = dict(os.environ, PYTHONPATH=tools, PYTHONDONTWRITEBYTECODE="1", VERDICT_DIR=os.path.join(d, "out"))
    argv = [sys.executable, tool, "--rel", sheet, "--ecad", ecad, "--board", "a"]
    src = open(tool, encoding="utf-8").read()
    if "--vendor" in src: argv += ["--vendor", vendor]           # the unrepaired tool has no such option
    r = subprocess.run(argv, cwd=d, env=env, capture_output=True, text=True)
    vp = os.path.join(d, "out", "reliability.verdict.json")
    v = json.load(open(vp)) if os.path.exists(vp) else {}
    return r, v


def main(argv):
    tools, tool = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    lst = argv[argv.index("--list") + 1] if "--list" in argv else None
    if lst is None:
        beside = os.path.join(os.path.dirname(tool), "pcb_reliability.yaml")
        lst = beside if os.path.exists(beside) else os.path.join(tools, "pcb_reliability.yaml")
    root = tempfile.mkdtemp(prefix="d6rel-matrix-")
    sheet = SHEET % hashlib.sha256(DOC).hexdigest()[:16]
    print("tool under test : %s  sha256/16 %s" % (tool, hashlib.sha256(open(tool, "rb").read()).hexdigest()[:16]))
    print("tools directory : %s" % tools)
    print("case 4's list   : %s  sha256/16 %s" % (lst, hashlib.sha256(open(lst, "rb").read()).hexdigest()[:16]))
    print("fixtures in     : a temporary directory outside the tree (mkdtemp prefix d6rel-matrix-)")
    print()
    cases = (
        ("1-one-declared-jst", {"J_PWR1": JST}, sheet, "PASS", "one declared JST connector"),
        ("2-plus-undeclared-idc", {"J_PWR1": JST, "J_RIB1": IDC}, sheet, "FAIL", "plus an undeclared IDC header"),
        ("3-plus-undeclared-rj45", {"J_PWR1": JST, "J_ETH": RJ45}, sheet, "FAIL", 'plus an undeclared "RJ45 MagJack"'),
        ("4-board-a-no-netlist", None, open(lst, encoding="utf-8").read(), "INCONCLUSIVE",
         "board A's declaration and no netlist"),
    )
    code = {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 3}
    bad = 0
    for name, parts, sh, want, what in cases:
        d, ecad, vendor, p = fixture(root, name, parts, sh)
        r, v = run(tools, tool, d, ecad, vendor, p)
        got = v.get("verdict")
        ok = (got == want and r.returncode == code[want])
        bad += 0 if ok else 1
        print("== case %s: %s" % (name, what))
        print("   wanted %s (exit %d); the tool says %s (exit %d): %s"
              % (want, code[want], got, r.returncode, "as wanted" if ok else "NOT AS WANTED"))
        print("   counts %s  denominator %s  missing_input %r"
              % (json.dumps(v.get("counts"), sort_keys=True), v.get("denominator"), v.get("missing_input")))
        inp = {k: x for k, x in (v.get("inputs") or {}).items()}
        print("   inputs recorded: %s" % json.dumps(inp, sort_keys=True).replace(root, "<fixtures>"))
        for line in (r.stdout + r.stderr).rstrip().split("\n"):
            print("   | %s" % line.replace(root, "<fixtures>"))
        print()
    print("the matrix: %d of 4 case(s) as wanted, %d not" % (4 - bad, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
