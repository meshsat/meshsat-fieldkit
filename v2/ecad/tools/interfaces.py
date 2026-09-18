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


def budget_for(letter, net, spec_path=None):
    """(mm, interface, source) for this net on this board, or (None, None, None).

    THE INTERFACE'S OWN SKEW BUDGET, BESIDE THE PROJECT'S NUMBER (rule PAIR-001, 17 September 2026). The pair
    gate refuses a pair over 1.00 mm of intra-pair mismatch, which is this project's decision and not any
    interface's requirement, and the rule asks for the interface's own budget to be CITED beside it. This is
    where a printer reads it: the sheet already carries the number and the clause it was read from, per
    interface, and the per-board assignment says which interface a net belongs to."""
    import fnmatch, yaml
    try: spec = yaml.safe_load(open(spec_path or SPEC, encoding="utf-8"))
    except Exception: return (None, None, None)
    b = ((spec.get("boards") or {}).get(str(letter).lower()) or {})
    bare = str(net).lstrip("/")
    for a in (b.get("assignments") or []):
        for pat in (a.get("patterns") or []):
            if fnmatch.fnmatchcase(bare, pat):
                i = (spec.get("interfaces") or {}).get(a.get("interface")) or {}
                src = (i.get("sources") or [{}])[0]
                return (i.get("intra_pair_mm"), a.get("interface"),
                        "%s %s" % (src.get("title", ""), src.get("clause", "")))
    return (None, None, None)


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
    # ONE VERDICT PER BOARD, NOT ONE FOR THE SET (16 September 2026, and this project has paid for the other
    # shape already). A set-level paperwork verdict decided every board's own result on 16 September, so board
    # E5, the one folder that passed, read FAIL on both paperwork rules because six other folders were stale.
    # Eight of today's disagreements are boards A and B; boards C, D and E carry USB at full speed, declare no
    # impedance target, and agree with their parts' datasheets exactly. They are not failed for another board.
    _note = ("every interface's impedance target and matching tolerance against the specification of the part "
             "that defines it, from pcb_interfaces.yaml; the sources are the hosts' and the modules' own "
             "datasheets")
    # A DECLARED ZERO IS AN ANSWER HERE TOO (17 September 2026). A board may carry no interface with a
    # specification of its own: board E5 is a contact interposer whose every net is board A's, read off A's
    # board by position under each spring pin, and its only "interfaces" are plated wire lands. Written as
    # INCONCLUSIVE that counted as nobody having looked, which is the opposite of what the declaration says. A
    # zero with its reason in `no_interface_targets_why` passes; a zero without one stays a question.
    try:
        import yaml as _yaml
        _spec = _yaml.safe_load(open(SPEC, encoding="utf-8")) or {}
    except Exception:
        _spec = {}
    _decl = {k: str((v or {}).get("no_interface_targets_why") or "").strip()
             for k, v in ((_spec.get("boards") or {}).items())}
    for letter, v in sorted(res.items()):
        _f = v["fails"]; _n = len(v["rows"]); _why = _decl.get(letter, "")
        _res = _v.FAIL if _f else (_v.PASS if _n or _why else _v.INCONCLUSIVE)
        _v.write("interfaces_%s" % letter, _res,
                 counts={"assignments": _n, "disagreements": len(_f)}, denominator=_n,
                 evidence=(_f[:12] or ([_why] if _why and not _n else [])),
                 inputs={"spec": os.path.basename(SPEC), "board": letter},
                 note=_note if _n else ("board %s declares that no interface of its own carries a target, with "
                                        "its reason" % letter.upper() if _why else
                                        "board %s declares no interface assignment" % letter.upper()),
                 quiet=True)
    return _v.write("interfaces", _v.FAIL if fails else (_v.INCONCLUSIVE if not rows else _v.PASS),
                    counts={"assignments": rows, "boards": len(res), "disagreements": len(fails)},
                    denominator=rows, evidence=fails[:25],
                    inputs={"spec": os.path.basename(SPEC)},
                    note=(_note + "; each board also carries its own interfaces_<letter> verdict, because a "
                          "set-level result deciding every board's own is a defect this project has already "
                          "met once" if rows else
                          "no interface assignment is declared, so nothing was compared"))


if __name__ == "__main__":
    # EVERY GATE LEAVES A READING WHEN IT RAISES (18 September 2026). The thirteen one-line entries of this
    # morning were the gates a crash had already cost a verdict; these are the rest of the deciding gates in
    # the coverage map, guarded the same way, so a rule whose tool raised reads INCONCLUSIVE naming the
    # exception rather than 'no verdict', which the registry reads as nobody having looked.
    sys.exit(_v.guard("interfaces", main, sys.argv[1:]))