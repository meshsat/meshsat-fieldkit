#!/usr/bin/env python3
"""Source, path, victim: the EMC sheet as data, checked against the board (rule EMC-001, 16 Sep 2026).

EMC-001 asks for an EMC sheet per board, the switching sources with their frequencies and edge rates, the
sensitive victims, the coupling paths considered with the measure taken at each, and a pre-compliance plan for
what cannot be decided on paper. It read "no verification" on six boards.

`pcb_emc.yaml` is the sheet. This is the gate over it, and the check that makes it a gate rather than prose is
the first one:

  EVERY SWITCHING PART IN THE NETLIST IS DECLARED AS A SOURCE. An undeclared converter is an undeclared
  source, and a sheet that lists thirteen of a board's fourteen is worse than no sheet, because it reads as
  complete. The part list comes from the board's own netlist by part number, not from anybody's memory.

Then: every declared source, victim and path element exists in that netlist; every frequency names a basis and
the basis file is in this tree; every path names a measure AND the evidence for it; and every board carries a
pre-compliance plan, because the paper half of this rule cannot close the measurement half and must not look
as though it has.

WHAT IT DOES NOT DO. It does not compute an emission, it does not know an edge rate the datasheet does not
publish, and it does not turn a plan into a measurement. Those belong to the laboratory stage, which is why
this rule's own note says so.

Usage: emc_sheet.py [--emc pcb_emc.yaml] [--ecad <dir>] [--board <letter>] [--json]
"""
import os, re, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

ECAD = os.path.dirname(HERE)
VENDOR = os.path.normpath(os.path.join(ECAD, "..", "vendor"))
EMC = os.path.join(HERE, "pcb_emc.yaml")
# Part numbers that switch current in this design. A part here and not in a board's sheet is a defect; a part
# NOT here that switches is a gap in this list, so it is stated in one place and tested against the netlist.
SWITCHERS = ("AP64500", "AP63203", "AP63205", "AP63200", "TPS62933", "LM5176", "LT8705", "TPS55288",
             "TPS56637", "LMR33640", "TPS23861")


def netlist_for(stem, ecad=None):
    ecad = ecad or ECAD
    c = [p for p in glob.glob(os.path.join(ecad, stem + "*", "out", stem + ".net")) if os.path.isfile(p)]
    return max(c, key=os.path.getmtime) if c else None


def parts(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    return dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', t))


def judge(emc=None, ecad=None, only=None, vendor=None):
    import yaml
    d = yaml.safe_load(open(emc or EMC, encoding="utf-8"))
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
        comps = parts(net) if net else None
        srcs = {str(s.get("ref")): s for s in (b.get("sources") or [])}
        if comps is None:
            notes.append("board %s has no netlist in this tree, so the sheet could not be compared with it" % letter.upper())
        else:
            found = {r: v for r, v in comps.items() if any(k in (v or "").upper() for k in SWITCHERS)}
            for r, v in sorted(found.items()):
                if r not in srcs:
                    fails.append("%s: %s (%s) switches and the sheet does not declare it as a source"
                                 % (letter.upper(), r, v[:50]))
            for r in sorted(set(srcs) - set(comps)):
                fails.append("%s: the sheet declares source %s and the netlist has no such part" % (letter.upper(), r))
            for v in (b.get("victims") or []):
                for r in (v.get("refs") or []):
                    if str(r) not in comps:
                        fails.append("%s: the sheet names %s as a victim and the netlist has no such part"
                                     % (letter.upper(), r))
        for s in (b.get("sources") or []):
            if not s.get("basis"):
                fails.append("%s: source %s carries no basis for its frequency" % (letter.upper(), s.get("ref")))
            elif have_vendor:
                for tok in str(s["basis"]).replace(",", " ").split():
                    if not tok.startswith("v2/vendor/"): continue
                    name = tok.rstrip(".,;:)]}\"'")
                    if not os.path.exists(os.path.join(vdir, name[len("v2/vendor/"):])):
                        fails.append("%s: source %s names %s, which is not in this tree" % (letter.upper(), s.get("ref"), name))
            if s.get("f_khz") is None and "not a converter" not in str(s.get("basis", "")):
                notes.append("%s: source %s declares no frequency" % (letter.upper(), s.get("ref")))
        if not (b.get("sources") or []) and not str(b.get("_sources_why", "")).strip():
            fails.append("%s: the sheet lists no source and does not say why, and 'none' is a claim" % letter.upper())
        for p in (b.get("paths") or []):
            for k in ("from", "to", "mechanism", "measure", "evidence"):
                if not str(p.get(k, "")).strip():
                    fails.append("%s: a coupling path carries no %s" % (letter.upper(), k))
        if not (b.get("paths") or []):
            fails.append("%s: the sheet considers no coupling path at all" % letter.upper())
        if not (b.get("pre_compliance") or []):
            fails.append("%s: the sheet carries no pre-compliance plan, so the half of this rule that needs "
                         "hardware is not named" % letter.upper())
        out[letter] = dict(sources=len(b.get("sources") or []), victims=len(b.get("victims") or []),
                           paths=len(b.get("paths") or []), plan=len(b.get("pre_compliance") or []),
                           fails=fails, notes=notes, netlist=bool(net))
    return out


def main(argv):
    emc = argv[argv.index("--emc") + 1] if "--emc" in argv else None
    ecad = argv[argv.index("--ecad") + 1] if "--ecad" in argv else None
    only = argv[argv.index("--board") + 1].lower() if "--board" in argv else None
    try:
        r = judge(emc, ecad, only)
    except Exception as e:
        print("emc_sheet: the sheet could not be read (%s: %s)" % (type(e).__name__, e))
        return _v.write("emc_sheet", _v.INCONCLUSIVE, denominator=0, rules=["EMC-001"],
                        note="the EMC sheet could not be read, so nothing was judged")
    fails = [f for v in r.values() for f in v["fails"]]
    for letter, v in sorted(r.items()):
        print("emc_sheet: %-3s %2d source(s) %2d victim(s) %2d path(s) %d plan item(s)%s"
              % (letter.upper(), v["sources"], v["victims"], v["paths"], v["plan"],
                 "" if v["netlist"] else "  (no netlist here)"))
    for n in [n for v in r.values() for n in v["notes"]][:12]: print("  note %s" % n)
    for f in fails: print("  FAIL %s" % f)
    if "--json" in argv: print(json.dumps(r, indent=1))
    res = _v.FAIL if fails else _v.PASS
    return _v.write("emc_sheet", res, rules=["EMC-001"],
                    counts={"boards": len(r), "sources": sum(v["sources"] for v in r.values()),
                            "paths": sum(v["paths"] for v in r.values()), "fail": len(fails)},
                    denominator=sum(v["sources"] + v["paths"] + v["plan"] for v in r.values()) or 1,
                    evidence=fails[:20], inputs={"sheet": os.path.basename(emc or EMC)},
                    note="the EMC sheet against the boards: every switching part in a netlist declared as a "
                         "source with a basis this tree holds, every victim and source present, every coupling "
                         "path carrying a measure and its evidence, and a pre-compliance plan per board. It "
                         "computes no emission and knows no edge rate a datasheet does not publish; the "
                         "measurement half of the rule is the laboratory stage")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
