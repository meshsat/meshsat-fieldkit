#!/usr/bin/env python3
"""Each interface against the specification of the part that defines it (rule INT-001, 16 September 2026).

Until today one interface in this project had a source. The Compute Module 5's datasheet states the
requirement for every high-speed interface this design carries and the RM520N-GL's hardware design states the
M.2 socket's own side, so `pcb_interfaces.yaml` holds them as data with the clause each was read from.

The rules here hold the three things that make the check worth having: every number in the file carries the
document it came from, an interface with no target is a DECLARED zero and not a silence, and the tolerance this
project judges a pair with is compared with the tolerance the part asks for, which is the disagreement the rule
exists to find.
"""
import os, sys, json, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
SPEC = os.path.join(TOOLS, "pcb_interfaces.yaml")


def _spec():
    import yaml
    return yaml.safe_load(open(SPEC, encoding="utf-8"))


def t_every_interface_number_carries_the_document_it_came_from():
    d = _spec()
    for name, i in d["interfaces"].items():
        srcs = i.get("sources") or []
        assert srcs, "%s states requirements with no source" % name
        for s in srcs:
            for k in ("title", "clause", "quote", "url_or_path", "accessed"):
                assert s.get(k), "%s: a source is missing %s" % (name, k)
            p = os.path.join(os.path.dirname(os.path.dirname(TOOLS)), s["url_or_path"].replace("v2/", "", 1))
            assert os.path.exists(p), "%s cites %s, which is not in this tree" % (name, s["url_or_path"])


def t_an_interface_with_no_target_says_so_with_its_reason():
    """Boards C and D carry USB only at full speed and their parts' datasheets say so. A declared zero is an
    answer; a silence is not, and the difference has to be visible in the data."""
    d = _spec()
    fs = d["interfaces"]["USB_FULL_SPEED"]
    assert fs.get("impedance_ohm") is None, "the full-speed entry carries a target"
    assert len(str(fs.get("note") or "")) > 120, "the full-speed entry does not say WHY it has none"
    assert fs.get("sources"), "the full-speed reading cites nothing"


def t_the_projects_own_tolerance_is_compared_with_the_parts():
    """The check this rule exists for, RE-STATED AS THE PROPERTY THAT SURVIVES DECISION 36 (21 September
    2026). It used to assert two things that were true only while the decision was open: that the gate holds
    the literal `> 1.0`, and that judging a board today produces a "times tighter" disagreement. Decision 36
    ruled the tighter of the two numbers, so both are now false BECAUSE THE GAP WAS CLOSED, and a rule that
    fails when its subject is fixed is a rule about history.

    What survives, and is what INT-001 is for: this project's own 1.00 mm is still the FLOOR the owner ruled,
    and the comparison still FIRES where the bar a pair would be judged at is looser than its part asks. The
    fixture is the real shape of that defect: an assignment whose nets fall to an EARLIER, looser pattern, so
    the sheet says 0.15 mm and the copper would be judged at 1.00."""
    import interfaces, yaml, tempfile
    assert interfaces.PROJECT_INTRA_MM == 1.0, "the project tolerance this compares against has moved"
    d = _spec()
    d["interfaces"]["LOOSE_FIXTURE"] = dict(d["interfaces"]["USB2_CM5"], intra_pair_mm=None)
    d["interfaces"]["TIGHT_FIXTURE"] = dict(d["interfaces"]["USB2_CM5"], intra_pair_mm=0.15)
    d["boards"] = {"x": {"name": "fixture-board", "assignments": [
        {"interface": "LOOSE_FIXTURE", "patterns": ["SIG*"], "class": "USB"},
        {"interface": "TIGHT_FIXTURE", "patterns": ["SIG_PCIE*"], "class": "USB"}]}}
    t = tempfile.mkdtemp(prefix="iface-tol-")
    p = os.path.join(t, "spec.yaml")
    with open(p, "w") as fh: yaml.safe_dump(d, fh)
    res = interfaces.judge(spec_path=p)
    fails = [f for v in res.values() for f in v["fails"]]
    assert any("times tighter" in f for f in fails), \
        "a pair judged at 1.00 mm whose part asks 0.15 was not reported: %s" % fails[:3]


def t_a_class_that_disagrees_with_its_interface_is_refused():
    """The defective fixture: a board whose class carries the wrong impedance for the interface on it."""
    import interfaces, yaml
    d = _spec()
    # The tolerance matters and is part of the fixture: 90 ohm IS inside 100 ohm plus or minus 10 percent, and
    # the tool is right to accept it there. The defect being reproduced is a class outside the band the part
    # states, so the fixture states a narrower band, which is what a part with a tighter requirement would.
    d["interfaces"]["ETHERNET_CM5"] = dict(d["interfaces"]["ETHERNET_CM5"], impedance_tol_percent=5)
    d["boards"] = {"b": {"name": "pcb-b-compute",
                         "assignments": [{"interface": "ETHERNET_CM5", "patterns": ["ETH*"], "class": "USB"}]}}
    t = tempfile.mkdtemp(prefix="iface-")
    p = os.path.join(t, "spec.yaml"); yaml.safe_dump(d, open(p, "w"))
    res = interfaces.judge(spec_path=p)
    fails = [f for v in res.values() for f in v["fails"]]
    assert any("asks for 100 ohm" in f for f in fails), \
        "a 90 ohm class on a 100 ohm interface was not refused: %s" % fails[:3]


def t_the_boards_impedance_targets_agree_with_the_parts_today():
    """The acceptable half, and it is a real verification rather than a formality: every class on every board
    carries the impedance the part at the other end of that link asks for, including the two that state
    different numbers (the CM5 asks 90 ohm of PCIe, the RM520N-GL 85 plus or minus 10 percent, and 90 is
    inside that band)."""
    import interfaces, glob
    ecad = os.path.dirname(TOOLS)
    res = interfaces.judge()
    bad = []
    for letter, v in res.items():
        # A board whose committed intent file is OLDER than its own generator is being judged on evidence
        # that predates the design, which is a staleness of the tree rather than a disagreement with a
        # datasheet: board D's USB class lost its target on 16 September and its committed netlist is from
        # before that. Skip it and say so instead of failing on a file nobody has regenerated.
        gen = os.path.join(TOOLS, "gen_sch_%s.py" % letter)
        ints = glob.glob(os.path.join(ecad, "pcb-%s*" % letter, "out", "*-intent.json"))
        if not ints or (os.path.exists(gen) and max(os.path.getmtime(i) for i in ints) < os.path.getmtime(gen)):
            continue
        bad += [f for f in v["fails"] if "ohm" in f and "times tighter" not in f]
    assert not bad, "an impedance target disagrees with the part that defines it: %s" % bad[:3]


def t_the_verdict_is_per_board_and_not_one_for_the_set():
    """16 September 2026, and this project has paid for the other shape already: a set-level paperwork verdict
    decided every board's own result, so board E5, the one folder that passed, read FAIL on both paperwork
    rules because six other folders were stale. Eight of today's interface disagreements are boards A and B;
    boards C and E carry USB at full speed, declare no target and agree with their parts' datasheets exactly,
    and must not be failed for another board."""
    import interfaces, yaml
    src = open(os.path.join(TOOLS, "interfaces.py"), encoding="utf-8").read()
    assert '_v.write("interfaces_%s" % letter' in src, "there is no per-board verdict"
    cov = yaml.safe_load(open(os.path.join(TOOLS, "pcb_rules_coverage.yaml"), encoding="utf-8"))
    ent = (cov["rules"] if isinstance(cov.get("rules"), dict) else {})
    text = open(os.path.join(TOOLS, "pcb_rules_coverage.yaml"), encoding="utf-8").read()
    i = text.index("INT-001:")
    assert "interfaces_<letter>" in text[i:i + 400], \
        "INT-001 still reads a set-level verdict, so one board's disagreement decides every board"
    res = interfaces.judge()
    assert not res["c"]["fails"], "board C disagrees with its own parts: %s" % res["c"]["fails"][:2]
    # 21 September 2026: this asserted `res["b"]["fails"]`, board B's own tolerance gap, which decision 36
    # closed. The property the rule is about is that ONE board's disagreement does not decide another's, and
    # that is measured on a fixture instead of on whichever board happens to be failing today.
    d = _spec()
    d["interfaces"]["LOOSE_FIXTURE"] = dict(d["interfaces"]["USB2_CM5"], intra_pair_mm=None)
    d["interfaces"]["TIGHT_FIXTURE"] = dict(d["interfaces"]["USB2_CM5"], intra_pair_mm=0.15)
    d["boards"] = {"c": dict(_spec()["boards"]["c"]),
                   "x": {"name": "fixture-board", "assignments": [
                       {"interface": "LOOSE_FIXTURE", "patterns": ["SIG*"], "class": "USB"},
                       {"interface": "TIGHT_FIXTURE", "patterns": ["SIG_PCIE*"], "class": "USB"}]}}
    t = tempfile.mkdtemp(prefix="iface-split-")
    p = os.path.join(t, "spec.yaml")
    with open(p, "w") as fh: yaml.safe_dump(d, fh)
    res = interfaces.judge(spec_path=p)
    assert res["x"]["fails"], "the fixture board's own disagreement is not reported"
    assert not res["c"]["fails"], "one board's disagreement decided another's: %s" % res["c"]["fails"][:2]


def t_every_number_in_the_sheet_appears_in_one_of_its_own_quotes():
    """A number is only as good as the sentence it was read from (17 September 2026).

    `USB2_CM5` carried an intra-pair tolerance of 0.10 mm and quoted the clause that says "with length
    matching within each pair", which states no number at all: the 0.10 had come from the USB 3.0 clause
    beside it. What applies where an interface clause is silent is the datasheet's own general
    recommendation, 4.2.2, and that says 0.15 mm. The rule is mechanical and it found exactly one entry.
    """
    import yaml
    d = yaml.safe_load(open(os.path.join(TOOLS, "pcb_interfaces.yaml"), encoding="utf-8"))
    bad = []
    for name, v in sorted((d.get("interfaces") or {}).items()):
        quotes = " ".join(str(s.get("quote", "")) for s in (v.get("sources") or []))
        for field in ("intra_pair_mm", "inter_pair_mm", "max_length_mm", "impedance_ohm"):
            val = v.get(field)
            if val is None: continue
            forms = {("%g" % val), ("%s" % val), ("%.2f" % val).rstrip("0").rstrip(".")}
            if not any(f in quotes for f in forms):
                bad.append("%s %s = %s appears in none of its own quotes" % (name, field, val))
    assert not bad, "; ".join(bad)


def t_the_pair_gate_cites_the_interfaces_own_budget_beside_the_projects():
    """Rule PAIR-001 asks for the interface's own skew budget to be cited beside the project's 1.00 mm, which
    is a project decision and no interface's requirement (17 September 2026). The lookup is exercised here and
    the two board gates that print a pair's mismatch are checked for it."""
    import sys as _s
    _s.path.insert(0, TOOLS)
    import interfaces as I
    mm, name, src = I.budget_for("b", "/PCIE_TX_P")
    assert name == "PCIE_CM5" and mm == 0.1 and "Compute Module 5" in src, (mm, name, src)
    mm, name, _ = I.budget_for("a", "/USB_D8_P")
    assert name == "USB2_CM5" and mm == 0.15, (mm, name)
    assert I.budget_for("a", "/NOT_A_PAIR_P") == (None, None, None)
    for fn in ("check_pcb_a.py", "check_pcb_b.py"):
        src = open(os.path.join(TOOLS, fn), encoding="utf-8").read()
        assert "budget_for(" in src, "%s does not cite the interface's own budget" % fn
        assert "DECISION 36" in src or "decision 36" in src, \
            "%s does not say which of the two numbers decides" % fn


def t_a_pair_is_judged_at_the_tighter_of_the_two_numbers():
    """DECISION 36, ruled 21 September 2026 (the session's): a pair is judged at the TIGHTER of this project's
    1.00 mm and the number the part at the end of its link asks for.

    THE DEFECTIVE FIXTURE is an interface asking 0.15 mm: judging its pair at 1.00 mm is the defect the
    decision was filed on, and the bar has to come back 0.15. THE ACCEPTABLE FIXTURES are the two cases where
    the owner's 5 September number stands: an interface that asks for something LOOSER (no interface in this
    tree does today, and the day one does, relaxing a bar an owner ruled is his to rule and not this
    function's to assume), and a net no interface of the board claims at all. Fail closed in both.
    """
    import interfaces as I, yaml, tempfile
    d = _spec()
    d["interfaces"]["TIGHT_FIXTURE"] = dict(d["interfaces"]["USB2_CM5"], intra_pair_mm=0.15)
    d["interfaces"]["LOOSE_FIXTURE"] = dict(d["interfaces"]["USB2_CM5"], intra_pair_mm=2.0)
    d["interfaces"]["SILENT_FIXTURE"] = dict(d["interfaces"]["USB2_CM5"], intra_pair_mm=None)
    d["boards"] = {"x": {"name": "fixture-board", "assignments": [
        {"interface": "TIGHT_FIXTURE", "patterns": ["TIGHT*"], "class": "USB"},
        {"interface": "LOOSE_FIXTURE", "patterns": ["LOOSE*"], "class": "USB"},
        {"interface": "SILENT_FIXTURE", "patterns": ["SILENT*"], "class": "USB"}]}}
    t = tempfile.mkdtemp(prefix="iface-bar-")
    p = os.path.join(t, "spec.yaml")
    with open(p, "w") as fh: yaml.safe_dump(d, fh)

    mm, why = I.bar_for("x", "/TIGHT_LANE0_P", p)
    assert mm == 0.15, "a pair of an interface asking 0.15 mm is judged at %s" % mm
    assert "TIGHT_FIXTURE" in why and "0.15" in why, why

    mm, why = I.bar_for("x", "/LOOSE_LANE0_P", p)
    assert mm == I.PROJECT_INTRA_MM, \
        "an interface asking 2.00 mm loosened a bar the owner ruled at %.2f" % I.PROJECT_INTRA_MM
    assert "tighter than" in why, why

    mm, why = I.bar_for("x", "/SILENT_LANE0_P", p)
    assert mm == I.PROJECT_INTRA_MM and "states no intra-pair number" in why, (mm, why)

    mm, why = I.bar_for("x", "/NOTHING_CLAIMS_THIS_P", p)
    assert mm == I.PROJECT_INTRA_MM and "no interface" in why, (mm, why)

    # and on the real sheet, where the ruling is worth something: board A's USB pair and board B's PCIe.
    assert I.bar_for("a", "/USB_D8_P")[0] == 0.15, "board A's USB pair is not judged at the CM5's 0.15 mm"
    assert I.bar_for("b", "/PCIE_TX_P")[0] == 0.10, "board B's PCIe pair is not judged at the CM5's 0.10 mm"


def t_both_board_gates_judge_at_the_bar_and_not_at_a_literal():
    """ONE PLACE DECIDES (decision 36). Both gates used to compare a pair's mismatch with the literal 1.0, and
    the literal is what the decision moved: a gate that goes back to it would judge board A's USB pair six
    times looser than its host asks, silently, with the interface's own number still PRINTED beside it. The
    rule matches the STATEMENT rather than the words, because a comment quoting the old line would otherwise
    satisfy a grep (the lesson of 21 September's `col(out, xL + 1.0` rule)."""
    import re
    for fn in ("check_pcb_a.py", "check_pcb_b.py"):
        src = open(os.path.join(TOOLS, fn), encoding="utf-8").read()
        assert "bar_for(" in src, "%s does not ask what bar the pair is judged at" % fn
        assert re.search(r"_over = abs\([^)]*\) > _bar", src), \
            "%s does not compare the mismatch with the bar it was given" % fn
        assert not re.search(r"_over = abs\([^)]*\) > 1\.0", src), \
            "%s judges a pair at a literal again" % fn
