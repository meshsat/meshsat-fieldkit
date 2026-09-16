#!/usr/bin/env python3
"""What carries load and what sees cycling (rule REL-001, MESHSAT-862, 16 September 2026).

The rule asks for a per-board list of the parts and joints that carry mechanical load or see cycling, the
expected cycles or level, and the measure taken. It read "no verification" on seven boards.

This kit is CARRIED, so the question is not academic: every connector mated in the field is a wear item and
every board-mounted jack is a lever with the case as its fulcrum. `pcb_reliability.yaml` declares the classes
per board with the rating from the part's own datasheet where this tree holds one, and this gate checks:

  1. COMPLETENESS, which is what makes it a gate: every part in the netlist whose value names a connector, a
     socket, a holder or a jack must fall in exactly one declared class. A list that covers nine of a board's
     eleven jacks reads as complete.
  2. Each class names its load and its measure, and a class with no cycle figure says why it has none, because
     "no number" and "nobody looked" read the same in a table and must not.
  3. A cited datasheet is in this tree.

WHAT IT CANNOT DO is test anything: REL-001 is verified at the PROTOTYPE and no board has been built. This is
the paper half, and the rule's phase says so.

Usage: reliability.py [--rel pcb_reliability.yaml] [--ecad <dir>] [--board <letter>] [--json]
"""
import os, re, sys, json, glob, fnmatch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

ECAD = os.path.dirname(HERE)
VENDOR = os.path.normpath(os.path.join(ECAD, "..", "vendor"))
REL = os.path.join(HERE, "pcb_reliability.yaml")
# What counts as load-bearing or cycling, by the words a part's own value carries. A part here is asked for;
# a part not here is not, which is why the list is in one place and tested against the boards.
WEAR = re.compile(r"socket|receptacle|holder|SMA|XT60|JST|IDC|header|standoff|U\.FL|M\.2|blade", re.I)


def netlist_for(stem, ecad=None):
    ecad = ecad or ECAD
    c = [p for p in glob.glob(os.path.join(ecad, stem + "*", "out", stem + ".net")) if os.path.isfile(p)]
    return max(c, key=os.path.getmtime) if c else None


def judge(rel=None, ecad=None, only=None, vendor=None):
    import yaml
    d = yaml.safe_load(open(rel or REL, encoding="utf-8"))
    import rules_lib as R
    facts = R.board_facts()
    vdir = vendor or VENDOR
    have_vendor = os.path.isdir(vdir)
    out = {}
    for letter, b in sorted((d.get("boards") or {}).items()):
        if only and letter != only: continue
        stem = (facts.get(letter) or {}).get("project")
        net = netlist_for(stem, ecad) if stem else None
        fails, notes = [], []
        classes = b.get("classes") or []
        covered, double = set(), []
        if net:
            txt = open(net, encoding="utf-8", errors="replace").read()
            parts = {r: v for r, v in re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt)}
            wear = {r for r, v in parts.items() if WEAR.search(v or "")}
            for r in sorted(wear):
                hit = [c for c in classes if any(fnmatch.fnmatchcase(r, p) for p in (c.get("refs") or []))]
                if not hit:
                    fails.append("%s: %s (%s) carries load or sees cycling and is in no declared class"
                                 % (letter.upper(), r, (parts[r] or "")[:45]))
                elif len(hit) > 1:
                    double.append("%s: %s falls in %d classes (%s)" % (letter.upper(), r, len(hit),
                                  ", ".join(c.get("name", "?") for c in hit)))
                else:
                    covered.add(r)
            for c in classes:
                want = c.get("count_expected")
                got = len([r for r in wear if any(fnmatch.fnmatchcase(r, p) for p in (c.get("refs") or []))])
                if want is not None and int(want) != got:
                    fails.append("%s: class %s expects %s part(s) and the netlist has %d"
                                 % (letter.upper(), c.get("name"), want, got))
        else:
            notes.append("board %s has no netlist in this tree, so the list could not be compared with it" % letter.upper())
        for c in classes:
            for k in ("name", "load", "measure", "basis"):
                if not str(c.get(k, "")).strip():
                    fails.append("%s: a class carries no %s" % (letter.upper(), k))
            if c.get("cycles") is None and "no " not in str(c.get("basis", "")).lower() \
               and "not " not in str(c.get("basis", "")).lower():
                fails.append("%s: class %s gives no cycle figure and does not say why it has none"
                             % (letter.upper(), c.get("name")))
            if have_vendor:
                for tok in str(c.get("basis", "")).replace(",", " ").split():
                    if not tok.startswith("v2/vendor/"): continue
                    name = tok.rstrip(".,;:)]}\"'")
                    if not os.path.exists(os.path.join(vdir, name[len("v2/vendor/"):])):
                        fails.append("%s: class %s cites %s, which is not in this tree" % (letter.upper(), c.get("name"), name))
        fails += double
        out[letter] = dict(classes=len(classes), covered=len(covered), fails=fails, notes=notes, netlist=bool(net))
    return out


def main(argv):
    rel = argv[argv.index("--rel") + 1] if "--rel" in argv else None
    ecad = argv[argv.index("--ecad") + 1] if "--ecad" in argv else None
    only = argv[argv.index("--board") + 1].lower() if "--board" in argv else None
    if only and only not in (yaml_boards := set((__import__("yaml").safe_load(open(rel or REL, encoding="utf-8")).get("boards") or {}))):
        print("reliability: board %s declares no reliability list; the boards that do are %s"
              % (only.upper(), ", ".join(sorted(x.upper() for x in yaml_boards))))
        return _v.write("reliability", _v.INCONCLUSIVE, denominator=0, rules=["REL-001"],
                        inputs={"board": only},
                        note="this board carries no declared list of load-bearing or cycling parts")
    try:
        r = judge(rel, ecad, only)
    except Exception as e:
        print("reliability: the list could not be read (%s: %s)" % (type(e).__name__, e))
        return _v.write("reliability", _v.INCONCLUSIVE, denominator=0, rules=["REL-001"],
                        note="the reliability list could not be read")
    fails = [f for v in r.values() for f in v["fails"]]
    for letter, v in sorted(r.items()):
        print("reliability: %-3s %2d class(es), %2d part(s) covered%s"
              % (letter.upper(), v["classes"], v["covered"], "" if v["netlist"] else "  (no netlist here)"))
    for n in [n for v in r.values() for n in v["notes"]][:8]: print("  note %s" % n)
    for f in fails: print("  FAIL %s" % f)
    if "--json" in argv: print(json.dumps(r, indent=1))
    res = _v.FAIL if fails else _v.PASS
    return _v.write("reliability", res, rules=["REL-001"],
                    counts={"boards": len(r), "classes": sum(v["classes"] for v in r.values()),
                            "covered": sum(v["covered"] for v in r.values()), "fail": len(fails)},
                    denominator=max(1, sum(v["classes"] + v["covered"] for v in r.values())),
                    evidence=fails[:20], inputs={"list": os.path.basename(rel or REL)},
                    note="every part that carries load or sees cycling falls in a declared class with its cycle "
                         "figure or the reason it has none, its load and the measure taken. It tests nothing: "
                         "REL-001 is verified at the prototype and no board has been built")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
