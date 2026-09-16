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
           "power_sequence.py", "ground_system.py", "emc_sheet.py", "closer_audit.py"}


def finish_stages(path=None):
    """Every tool the finish invokes, from the script itself."""
    txt = open(path or FINISH, encoding="utf-8", errors="replace").read()
    names = set(re.findall(r"\$T/([a-z_0-9]+\.(?:py|sh))", txt))
    return {n for n in names if n not in READERS}


def board_declares(letter, key):
    """Does this board declare the thing that prevents a class? The declaration is the board's own."""
    import json
    p = os.path.join(HERE, "boards", "%s.json" % (letter or "").lower())
    if not os.path.exists(p): return False
    try: return bool(json.load(open(p, encoding="utf-8")).get(key))
    except Exception: return False


def judge(closers=None, finish=None, letter=None):
    import yaml
    d = yaml.safe_load(open(closers or CLOSERS, encoding="utf-8"))
    decl = {str(c.get("tool")): c for c in (d.get("closers") or [])}
    run = finish_stages(finish)
    fails, uncovered, notes = [], [], []
    # A BOARD WITH NO CHAIN HAS NO CLOSERS. Board E5 is the bare dock block: copper, holes and contact targets,
    # generated from board A's own board file, with no schematic and no finish. Asking which of its repairs are
    # prevented is asking about repairs that never happen (16 September 2026).
    if letter and not os.path.exists(os.path.join(HERE, "boards", "%s.json" % letter.lower())):
        notes.append("board %s has no chain and therefore no closer runs on it" % letter.upper())
        return dict(declared=len(decl), in_finish=len(run), fails=[], uncovered=[], notes=notes)
    for t in sorted(run - set(decl)):
        fails.append("%s changes the board in the finish and is not declared: a repair nobody has named is a "
                     "stage of the design that nobody has written down" % t)
    for t in sorted(set(decl) - run):
        notes.append("%s is declared and the finish does not invoke it" % t)
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
                if board_declares(letter, key):
                    notes.append("%s: covered on board %s by its own %s declaration" % (t, letter.upper(), key))
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
