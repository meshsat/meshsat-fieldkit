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
    This is the check the rule exists for, and since DECISION 36 (ruled 21 September 2026) the two agree by
    construction: `bar_for` is the one place that decides what a pair is judged at, the board gates call it,
    and this asks that function what bar a net of each interface would get. It is not a tautology: the bar is
    resolved through the board's own assignment patterns, so an assignment whose nets fall to an earlier and
    looser pattern is named here.
  * WHAT IT DOES NOT MEASURE, said plainly because this docstring used to claim it. The mismatch of an actual
    pair and its routed length against `max_length_mm` are read off the BOARD by `check_pcb_a.py` and
    `check_pcb_b.py`, which print every pair with the bar it was judged at; the `board_file` argument here was
    accepted and used by nothing, and it is gone. The length half is owed a reader (board B's M.2 PCIe states
    200 mm and its USB 225) and no line here pretends it has one.

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
# The owner's ruling of 5 September 2026 17:00: a pair over this much intra-pair mismatch blocks a chain.
# DECISION 36 did not move it and could not: it is the number this project refuses at where the part at the
# end of the link asks for nothing, and the floor under every number `bar_for` returns.
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


_SHEET = {}


def _sheet(path):
    """The interface sheet, parsed once per (path, mtime, size).

    `bar_for` doubled the number of times a board gate asks this file a question: board B prints 35 pairs and
    each one now costs a budget AND a bar, which was 70 parses of the same YAML per run. The key carries the
    file's mtime and size so an edited sheet is re-read, and the fixtures each write their own temp path, so
    a stale answer cannot survive a test."""
    import yaml, os as _os
    try: st = _os.stat(path)
    except Exception: return None
    k = (path, st.st_mtime, st.st_size)
    if k not in _SHEET:
        try: _SHEET[k] = yaml.safe_load(open(path, encoding="utf-8"))
        except Exception: _SHEET[k] = None
    return _SHEET[k]


def budget_for(letter, net, spec_path=None):
    """(mm, interface, source) for this net on this board, or (None, None, None).

    THE INTERFACE'S OWN SKEW BUDGET, BESIDE THE PROJECT'S NUMBER (rule PAIR-001, 17 September 2026). The pair
    gate refuses a pair over 1.00 mm of intra-pair mismatch, which is this project's decision and not any
    interface's requirement, and the rule asks for the interface's own budget to be CITED beside it. This is
    where a printer reads it: the sheet already carries the number and the clause it was read from, per
    interface, and the per-board assignment says which interface a net belongs to."""
    import fnmatch
    spec = _sheet(spec_path or SPEC)
    if spec is None: return (None, None, None)
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


def bar_for(letter, net, spec_path=None):
    """The intra-pair mismatch a pair of this net is JUDGED at, and why (decision 36, ruled 21 September 2026).

    THE RULING, in one sentence: the tighter of this project's 1.00 mm and the number the part at the end of
    the link asks for. The owner's ruling of 5 September 2026 17:00 is not reversed and not loosened; what
    decision 36 adds beneath it is the host's own recommendation, where the host states one, so this function
    can only ever refuse a pair the old bar passed and never pass one it refused. That is the whole of why the
    session could take it: a criterion that moves in one direction only accepts no residual risk, and the cost
    was measured before it was ruled, on the COMMITTED boards where KiCad is: board A32's USB_D8 at 0.23 mm
    against the compute module's 0.15, which is 0.08 mm of meander that `pair_match.sh` already lays in every
    finish, and on board B21 one pair, PCIE2_CLK at 0.93 mm, that the owner's 1.00 mm passed.

    WHY THE PROJECT'S NUMBER STAYS THE FLOOR. An interface that asks for something LOOSER than 1.00 mm would,
    read literally, relax a bar an owner ruled; no interface in this tree does today (the loosest is the M.2
    module's 0.70), and the day one does, relaxing it is the owner's to rule and not this function's to
    assume. The `mm >= PROJECT_INTRA_MM` branch below is doing that work and it is deliberate.

    ONE PLACE DECIDES. `check_pcb_a.py` and `check_pcb_b.py` call this and print the number it returns beside
    each pair; `tests/test_interfaces.py` refuses either gate comparing a mismatch to a literal again.

    REVERSAL: return `PROJECT_INTRA_MM` unconditionally and both gates refuse at 1.00 mm as they did before
    this commit, which restores the 5 September ruling on its own.
    """
    mm, iface, src = budget_for(letter, net, spec_path)
    if mm is None:
        return (PROJECT_INTRA_MM,
                "this project's %.2f mm (owner ruling 5 September 2026): %s"
                % (PROJECT_INTRA_MM,
                   "no interface of board %s claims this net" % str(letter).upper() if iface is None
                   else "%s states no intra-pair number" % iface))
    mm = float(mm)
    if mm >= PROJECT_INTRA_MM:
        return (PROJECT_INTRA_MM,
                "this project's %.2f mm, which is tighter than %s's own %.2f mm (%s)"
                % (PROJECT_INTRA_MM, iface, mm, (src or "").strip()))
    return (mm, "%s asks for %.2f mm (%s)" % (iface, mm, (src or "").strip()))


def _probe_net(pattern):
    """A net name that this assignment's pattern matches, so the bar can be resolved the way a real net is."""
    return str(pattern).replace("*", "X").replace("?", "X")


def judge(spec_path=None, ecad=None, only=None):
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
            # THE CHECK THIS RULE EXISTS FOR: what this project judges a pair with, against what the part
            # asks. Until decision 36 was ruled this compared a CONSTANT with the datasheet and failed every
            # high-speed interface of boards A and B, which was the gap the decision was filed on. It asks
            # `bar_for` now, which is the function the board gates judge with, and it asks it through this
            # assignment's own patterns, so what is checked is the bar a real net of this interface gets.
            need = spec.get("intra_pair_mm")
            if need is not None:
                pats = [p for p in (a.get("patterns") or []) if str(p).strip()]
                bar, why = (bar_for(letter, _probe_net(pats[0]), spec_path) if pats
                            else (PROJECT_INTRA_MM, "this assignment names no pattern"))
                row["intra_bar_mm"] = bar
                row["intra_bar_why"] = why
                if bar > float(need) + 1e-9:
                    fails.append("%s %s: a pair of this interface is judged at %.2f mm and %s asks for "
                                 "%.2f mm, which is %.1f times tighter (%s)"
                                 % (letter.upper(), a["interface"], bar, a["interface"], float(need),
                                    bar / float(need), why))
            rows.append(row)
        out[letter] = dict(rows=rows, fails=fails, notes=notes)
    return out


def _glob_intent(ecad, stem):
    import glob
    return [p for p in glob.glob(os.path.join(ecad, stem + "*", "out", stem + "-intent.json"))
            if os.path.isfile(p)]


def main(argv):
    only = _v.opt(argv, "--board", None)
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