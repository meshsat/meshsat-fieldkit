#!/usr/bin/env python3
"""Prevention before repair (rule PLC-002, MESHSAT-862, 16 September 2026).

The finish repairs things. Every repair is a defect the placement or the route did not prevent, and the rule
asks two things of that: each closer names the defect class it repairs and why prevention was not possible, and
the placed-board predictor covers the classes that have been repaired MORE THAN ONCE.

`pcb_closers.yaml` is the first half. This gate checks it and decides the second, and the checks are:

  1. COMPLETENESS, which is what makes it a gate: every tool the finish actually invokes that changes copper
     must be declared. The list comes from finish.sh itself, not from anybody's memory, so a stage added to the
     finish and not declared here is a failure rather than a silence.
  2. Every declaration carries a defect class and a reason prevention was not possible.
  3. A class marked `repeated` must name what now prevents it. A `prevented_by` that says NOTHING is read as
     what it says: the class is UNCOVERED, the rule's second half is not met for it, and the verdict is a
     failure that names the classes rather than a pass that hides them.

Three classes are uncovered today and each is a real design item: a pour island with no via of its own net, a
pad its own plane cannot reach, and a stitch via the pour has retreated from. All three are the same shape,
copper laid at placement time and cut by the router afterwards, and the honest reading is that the stitching
belongs in the placement.

Usage: closer_audit.py [--closers pcb_closers.yaml] [--finish finish.sh] [--json]
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

CLOSERS = os.path.join(HERE, "pcb_closers.yaml")
FINISH = os.path.join(HERE, "finish.sh")
# Stages the finish runs that only READ the board: they are not repairs and are not asked to declare one.
READERS = {"drc.sh", "guarded.sh", "hardset.py", "verdict.py", "via_audit.py", "dc_drop.py", "impedance_check.py",
           "netlist_board.py", "check_contracts.py", "port_protect.py", "pruned_gate.py", "pair_audit.py",
           "pair_match.sh", "stackup_write.py", "derate.py", "clock_check.py", "place_audit.py", "class_floor.py",
           "return_gaps.py", "fab_limits.py", "via_current.py", "thermal.py", "spacing.py", "edge_length.py",
           "ref_change.py", "signalnets.py", "intent_checks.py", "check_zone_nets.py", "lcsc_fill.py",
           "verify_deliverable.py", "export_jlc.sh", "build_pcb.sh", "finish_board.sh", "energy_chain.py",
           "power_sequence.py", "ground_system.py", "emc_sheet.py", "closer_audit.py",
           # carry_placed.py reads the placed snapshot and the board being cut and writes verdicts; it never
           # opens either for writing, which is the property that lets it decide whether the placement
           # measurement belongs to this board (17 September 2026).
           "carry_placed.py",
           # safe_lines.py reads the netlist and the board's declaration and writes a verdict: rule SCH-004
           # blocks the deliverable the way TRN-001 does beside it, and neither touches copper (17 Sep 2026).
           "safe_lines.py"}


def finish_stages(path=None):
    """Every tool the finish invokes, from the script itself."""
    txt = open(path or FINISH, encoding="utf-8", errors="replace").read()
    names = set(re.findall(r"\$T/([a-z_0-9]+\.(?:py|sh))", txt))
    return {n for n in names if n not in READERS}


# WRITTEN AND NEVER RUN, the third time (16 September 2026). `bypass_place.py` existed for a day before any
# chain called it; `widen_net.py` was written this morning for a rule that went on failing on two boards while
# it sat in the tools directory with its own tests passing; and `logo_silk.py` draws the mark the owner ruled
# on to these boards, and no board carries a silkscreen polygon. A tool that changes copper and that nothing
# invokes is not a tool, it is a plan. Every one of them is either invoked by a chain, a board declaration or
# another tool, or it is DECLARED here as idle with the reason, and the gate refuses anything else.
def copper_writers(here=None):
    """Every tool in this directory that saves a board."""
    import glob
    here = here or HERE
    out = []
    for f in sorted(glob.glob(os.path.join(here, "*.py"))):
        try: src = open(f, encoding="utf-8", errors="replace").read()
        except Exception: continue
        if "SaveBoard(" in src: out.append(os.path.basename(f))
    return out


def invoked_names(here=None):
    """The text of everything that could invoke a tool: the shell chains, the routeflow profiles, the board
    declarations, the arm specifications and the other tools, with shell variables left as wildcards."""
    import glob
    here = here or HERE
    files = []
    # A DECLARATION IS NOT AN INVOCATION. The yaml files here are data: pcb_closers.yaml names every tool it
    # declares idle and pcb_rules_coverage.yaml names the tool behind every rule, so counting them turned each
    # declaration into its own proof that something runs the tool. What can invoke a tool is a chain, a
    # routeflow profile, a board or arm declaration, or another tool.
    for pat in ("*.sh", "*.py", "routeflow/*.json", "boards/*.json", "arms/*.json",
                "pair_router/*.py", "agent/*.py"):
        files += glob.glob(os.path.join(here, pat))
    # COMMENTS DO NOT INVOKE ANYTHING, and the first version of this counted them: the paragraph above names
    # logo_silk.py, which took it off its own list of tools nothing runs. Every # comment is dropped before a
    # name is looked for, in shell, python and yaml alike.
    def _code(text):
        return "\n".join(l.split("#", 1)[0] for l in text.splitlines())
    return [(os.path.basename(f), _code(open(f, encoding="utf-8", errors="replace").read())) for f in files]


def never_invoked(here=None):
    """Copper-changing tools that nothing in this tree names."""
    import fnmatch
    callers = invoked_names(here)
    tok = re.compile(r"[A-Za-z0-9_${}]+\.(?:py|sh)")
    out = []
    for w in copper_writers(here):
        mod = w[:-3]; hit = False
        for f, s in callers:
            if f == w: continue
            if w in s or re.search(r"\b(?:import|from)\s+%s\b" % re.escape(mod), s): hit = True; break
            for m in tok.findall(s):
                if "$" in m and fnmatch.fnmatch(w, re.sub(r"\$\{?[A-Za-z_][A-Za-z0-9_]*\}?", "*", m)):
                    hit = True; break
            if hit: break
        if not hit: out.append(w)
    return out


# What a board has said about a prevention it could adopt. A DECLARED ZERO IS AN ANSWER AND AN UNDECLARED ZERO
# IS NOT, which is this project's rule everywhere else and was not applied here (17 September 2026): board P
# measured the ground-via grid on its own copper, 21 open connections against 0 without it, wrote that down and
# declared none, and this gate still read it as a class nobody had covered. A board that measured a prevention
# and refused it HAS answered the rule's second half; a board that has not measured it has not.
DECLARED, REFUSED, SILENT = "declared", "refused", "silent"
NOT_MEASURED = "NOT MEASURED"


def board_declares(letter, key):
    """DECLARED, REFUSED (measured and written down) or SILENT for this board and this prevention."""
    import json
    p = os.path.join(HERE, "boards", "%s.json" % (letter or "").lower())
    if not os.path.exists(p): return SILENT
    try: d = json.load(open(p, encoding="utf-8"))
    except Exception: return SILENT
    if d.get(key): return DECLARED
    why = str(d.get("_%s_why" % key) or d.get("%s_why" % key) or "").strip()
    if why and NOT_MEASURED not in why.upper(): return REFUSED
    return SILENT


def judge(closers=None, finish=None, letter=None):
    import yaml
    d = yaml.safe_load(open(closers or CLOSERS, encoding="utf-8"))
    decl = {str(c.get("tool")): c for c in (d.get("closers") or [])}
    run = finish_stages(finish)
    fails, uncovered, notes = [], [], []
    # A BOARD WITH NO CHAIN HAS NO CLOSERS. Board E5 is the bare dock block: copper, holes and contact targets,
    # generated from board A's own board file, with no schematic and no finish. Asking which of its repairs are
    # prevented is asking about repairs that never happen (16 September 2026).
    # 17 September 2026: board E5 has a table now, because the rules that ask a BOARD a question need somewhere
    # to read its answer, and the table says `chain: false`. The discriminator is the declaration, not the
    # absence of the file.
    _bt_path = os.path.join(HERE, "boards", "%s.json" % (letter or "").lower())
    _no_chain = not os.path.exists(_bt_path)
    if not _no_chain:
        try:
            import json as _json
            _no_chain = _json.load(open(_bt_path, encoding="utf-8")).get("chain") is False
        except Exception:
            _no_chain = False
    if letter and _no_chain:
        notes.append("board %s has no chain and therefore no closer runs on it" % letter.upper())
        return dict(declared=len(decl), in_finish=len(run), fails=[], uncovered=[], notes=notes)
    for t in sorted(run - set(decl)):
        fails.append("%s changes the board in the finish and is not declared: a repair nobody has named is a "
                     "stage of the design that nobody has written down" % t)
    for t in sorted(set(decl) - run):
        notes.append("%s is declared and the finish does not invoke it" % t)
    # the third half of this rule: a tool that changes copper and that NOTHING runs. It is a property of THIS
    # tools directory, so it is asked only of the real declaration file: a fixture names two closers in a
    # temporary directory and knows nothing about the tree it is testing.
    idle = {str(e.get("tool")): e for e in (d.get("idle_tools") or [])}
    for t in (never_invoked() if os.path.abspath(closers or CLOSERS) == os.path.abspath(CLOSERS) else []):
        e = idle.get(t)
        if not e:
            fails.append("%s changes copper and nothing in this tree invokes it: a tool nobody runs is a plan, "
                         "not a tool (declare it in pcb_closers.yaml `idle_tools` with the reason, or wire it)" % t)
        elif not str(e.get("why", "")).strip():
            fails.append("%s is declared idle and gives no reason" % t)
        else:
            notes.append("%s: idle by declaration (%s)" % (t, str(e["why"])[:80]))
    if os.path.abspath(closers or CLOSERS) == os.path.abspath(CLOSERS):
        for t in sorted(set(idle) - set(never_invoked())):
            notes.append("%s is declared idle and something does invoke it now" % t)
    for t, c in sorted(decl.items()):
        if not str(c.get("defect_class", "")).strip():
            fails.append("%s declares no defect class" % t)
        if not str(c.get("why_prevention_failed", "")).strip():
            fails.append("%s does not say why prevention was not possible" % t)
        if c.get("repeated"):
            p = str(c.get("prevented_by") or "").strip()
            key = c.get("prevented_by_board_declaration")
            if p and not p.upper().startswith("NOTHING"):
                continue
            # A PER-BOARD PREVENTION IS A PER-BOARD FACT (16 September 2026). Three classes are prevented by a
            # ground-via grid laid before the route, and a grid is declared board by board because it is not
            # free: board P measured it at 21 open connections against 0 without. So the class is covered on a
            # board that declares the grid and uncovered on one that does not, and this gate says which.
            if key and letter:
                said = board_declares(letter, key)
                if said == DECLARED:
                    notes.append("%s: covered on board %s by its own %s declaration" % (t, letter.upper(), key))
                    continue
                if said == REFUSED:
                    notes.append("%s: covered on board %s by a MEASURED refusal of %s, written down with its "
                                 "numbers; the repair stays and the board says why the prevention is not free"
                                 % (t, letter.upper(), key))
                    continue
                uncovered.append("%s on board %s: %s (prevented by declaring %s, which this board does not)"
                                 % (t, letter.upper(), str(c.get("defect_class", ""))[:60], key))
                continue
            uncovered.append("%s: %s" % (t, str(c.get("defect_class", ""))[:80]))
    return dict(declared=len(decl), in_finish=len(run), fails=fails, uncovered=uncovered, notes=notes)


def main(argv):
    cl = argv[argv.index("--closers") + 1] if "--closers" in argv else None
    fi = argv[argv.index("--finish") + 1] if "--finish" in argv else None
    letter = argv[argv.index("--board") + 1].lower() if "--board" in argv else None
    try:
        r = judge(cl, fi, letter)
    except Exception as e:
        print("closer_audit: could not read the declarations (%s: %s)" % (type(e).__name__, e))
        return _v.write("closer_audit", _v.INCONCLUSIVE, denominator=0, rules=["PLC-002"],
                        note="the closer declarations could not be read")
    print("closer_audit: %d closer(s) declared, %d copper-changing stage(s) in the finish" % (r["declared"], r["in_finish"]))
    for n in r["notes"]: print("  note %s" % n)
    for u in r["uncovered"]:
        print("  UNCOVERED %s" % u)
    for f in r["fails"]: print("  FAIL %s" % f)
    if "--json" in argv: print(json.dumps(r, indent=1))
    res = _v.FAIL if (r["fails"] or r["uncovered"]) else _v.PASS
    return _v.write("closer_audit", res, rules=["PLC-002"],
                    counts={"declared": r["declared"], "in_finish": r["in_finish"],
                            "uncovered_classes": len(r["uncovered"]), "fail": len(r["fails"])},
                    denominator=max(1, r["declared"]),
                    evidence=(r["fails"] + ["uncovered: " + u for u in r["uncovered"]])[:20],
                    inputs={"closers": os.path.basename(cl or CLOSERS)},
                    note="every copper-changing stage of the finish declares the defect class it repairs and "
                         "why prevention was not possible, and a class repaired more than once names what now "
                         "prevents it. A class that names NOTHING is reported as uncovered and fails this rule, "
                         "because that is the rule's second half unmet rather than a silence")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
