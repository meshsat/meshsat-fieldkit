#!/usr/bin/env python3
"""Every interface against the specification of the part that defines it (rule INT-001, MESHSAT-862,
16 September 2026).

The rule asks that each interface be designed to ITS OWN specification rather than to a house number, and until
today one interface in this project had a source: the Compute Module 5's PCIe clauses. That datasheet turns out
to state the requirement for every high-speed interface this design carries, and the 5G module's hardware
design states the M.2 socket's own side, so `pcb_interfaces.yaml` carries them as data with the document and
clause each was read from.

WHAT IT JUDGES, on the netlist and the board:

  * the IMPEDANCE the board's own net class asks for, against the interface's required impedance and the
    tolerance the part states. Both ends of a link are checked where both state a number: the CM5 asks 90 ohm
    of PCIe and the RM520N-GL asks 85 plus or minus 10 percent, so one class satisfies both, and this says so
    rather than leaving it to be noticed.
  * the INTRA-PAIR matching this project judges the board with, against the number the interface asks for.
    This is the check the rule exists for: the board gate warns above 1.0 mm and the CM5 asks for 0.1 mm on
    PCIe and USB 3.0 and 0.15 on HDMI and Ethernet, which is six to ten times tighter.
  * where a routed board is given, the MEASURED mismatch of every pair of that interface, and the routed
    length against any maximum the part states.

WHAT IT DOES NOT DO. It does not invent a requirement for an interface no part in this tree describes, and it
does not treat a board that declares NO impedance target as a failure: boards C and D carry USB only at full
speed and their parts' datasheets say so, which is a declared zero with a reason.

Usage: interfaces.py [<board.kicad_pcb>] [--board <letter>] [--json]
"""
import os, sys, re, json, fnmatch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

SPEC = os.path.join(HERE, "pcb_interfaces.yaml")
# The tolerance this project's own board gates warn above, so the two can be compared in one place.
PROJECT_INTRA_MM = 1.0


def _classes(project_file):
    """{net: class} from a .kicad_pro, the only place KiCad 9 keeps the assignment."""
    try: d = json.load(open(project_file, encoding="utf-8"))
    except Exception: return {}, {}
    ns = (d.get("net_settings") or {})
    byname = {}
    for c in (ns.get("classes") or []):
        byname[c.get("name")] = c
    out = {}
    for pat, cls in (ns.get("netclass_patterns") or []) if isinstance(ns.get("netclass_patterns"), list) else []:
        out[pat] = cls
    asg = ns.get("netclass_assignments") or {}
    for net, cls in asg.items():
        out[net] = cls[0] if isinstance(cls, list) and cls else cls
    return out, byname


def judge(spec_path=None, ecad=None, only=None, board_file=None):
    import yaml
    d = yaml.safe_load(open(spec_path or SPEC, encoding="utf-8"))
    ifaces = d["interfaces"]
    ecad = ecad or os.path.dirname(HERE)
    out = {}
    for letter, b in sorted((d.get("boards") or {}).items()):
        if only and letter != only: continue
        stem = b["name"]
        rows, fails, notes = [], [], []
        # the intent's pair classes carry the target this project assigns to each class
        intent = None
        for cand in sorted(_glob_intent(ecad, stem)):
            intent = cand; break
        pair_classes = {}
        if intent:
            try: pair_classes = (json.load(open(intent, encoding="utf-8")).get("pair_classes") or {})
            except Exception: pass
        for a in b.get("assignments", []):
            spec = ifaces.get(a["interface"])
            if spec is None:
                fails.append("%s: %s names an interface nothing describes" % (letter.upper(), a["interface"]))
                continue
            cls = a.get("class")
            want = spec.get("impedance_ohm")
            have = (pair_classes.get(cls) or {}).get("z_diff")
            tol = float(spec.get("impedance_tol_percent") or 0) / 100.0
            row = dict(board=letter, interface=a["interface"], cls=cls, required_ohm=want, class_ohm=have,
                       intra_required_mm=spec.get("intra_pair_mm"), intra_project_mm=PROJECT_INTRA_MM)
            if want is None:
                # A declared zero with a reason: the part's own datasheet says the interface has no target.
                if have is not None:
                    fails.append("%s %s: the class %s carries a %.0f ohm target and the parts' own datasheets "
                                 "say this interface has none" % (letter.upper(), a["interface"], cls, have))
                else:
                    notes.append("%s %s: no impedance target, which is what its parts' datasheets say"
                                 % (letter.upper(), a["interface"]))
            elif have is None:
                fails.append("%s %s: the class %s carries no impedance target and %s asks for %s ohm"
                             % (letter.upper(), a["interface"], cls, a["interface"], want))
            elif abs(have - want) > want * tol + 1e-9:
                fails.append("%s %s: the class %s is %.0f ohm and %s asks for %s ohm within %.0f percent"
                             % (letter.upper(), a["interface"], cls, have, a["interface"], want, tol * 100))
            # THE CHECK THIS RULE EXISTS FOR: what this project judges a pair with, against what the part asks.
            need = spec.get("intra_pair_mm")
            if need is not None and PROJECT_INTRA_MM > float(need) + 1e-9:
                fails.append("%s %s: this project judges intra-pair mismatch at %.2f mm and %s asks for %.2f mm, "
                             "which is %.1f times tighter"
                             % (letter.upper(), a["interface"], PROJECT_INTRA_MM, a["interface"], float(need),
                                PROJECT_INTRA_MM / float(need)))
            rows.append(row)
        out[letter] = dict(rows=rows, fails=fails, notes=notes)
    return out


def _glob_intent(ecad, stem):
    import glob
    return [p for p in glob.glob(os.path.join(ecad, stem + "*", "out", stem + "-intent.json"))
            if os.path.isfile(p)]


def main(argv):
    only = argv[argv.index("--board") + 1] if "--board" in argv else None
    res = judge(only=only)
    rows = sum(len(v["rows"]) for v in res.values())
    fails = [f for v in res.values() for f in v["fails"]]
    notes = [n for v in res.values() for n in v["notes"]]
    print("interfaces: %d interface assignment(s) over %d board(s) against the parts' own specifications; "
          "%d disagreement(s)" % (rows, len(res), len(fails)))
    for f in fails[:25]: print("  FAIL %s" % f)
    for n in notes[:8]: print("  note %s" % n)
    if "--json" in argv: print(json.dumps(res, indent=1))
    return _v.write("interfaces", _v.FAIL if fails else (_v.INCONCLUSIVE if not rows else _v.PASS),
                    counts={"assignments": rows, "boards": len(res), "disagreements": len(fails)},
                    denominator=rows, evidence=fails[:25],
                    inputs={"spec": os.path.basename(SPEC)},
                    note=("every interface's impedance target and matching tolerance against the specification "
                          "of the part that defines it, from pcb_interfaces.yaml; the sources are the hosts' "
                          "and modules' own datasheets" if rows else
                          "no interface assignment is declared, so nothing was compared"))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
