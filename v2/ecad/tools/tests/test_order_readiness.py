#!/usr/bin/env python3
"""No order folder reads as an approved package (owner decision 41, ruled 25 September 2026, executed 26 September).

The ruling rebuilt `v2/release/revA/order/` from the deliverable folders that exist and quarantined it in the same
commit: every ORDER-NOTES.txt opens with its board's readiness in the owner's four fields (ROUTING_STATUS,
ELECTRICAL_PROTECTION_STATUS, FAB_READINESS, PUBLICATION_STATUS). These rules hold the writer to it, both ways:
a held board carries the hold's own words and nothing computed in their place, an unheld board's values come
from the registry and never read released while promotion is frozen, a re-stamp replaces its block and leaves
the note below it byte for byte, and the producer computes the block before it writes the note.
"""
import os, re, sys, json, shutil, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import order_readiness as OR
import rules_status as S


def _row(rule, domain, result, effect="BLOCKER", phase="ROUTED_BOARD", evidence=None):
    return {"rule": rule, "domain": domain, "result": result, "release_effect": effect,
            "verification_phase": phase, "why": "", "evidence": evidence}


class _Ctx:
    """The one surface order_readiness reads, with nothing from this tree behind it."""
    def __init__(self, rows, holds=None, frozen=True, decisions=None, declared="X9"):
        self.S = S
        self.m = {"boards": {"x": {"project": "pcb-x-kit"}}, "manifest_version": "fixture",
                  "promotion": {"frozen": frozen, "frozen_at": "2026-09-16T00:35:00+02:00"}}
        self.fp = "fixturefingerprint"
        self.holds = holds or {}
        self._rows, self._decl, self._dec = rows, declared, decisions or {}

    def status(self, letter):
        return {"rows": self._rows, "subject": {"declared_phase": self._decl}}

    def decision(self, n):
        return self._dec.get(str(n))


PASSING = [_row("RTE-001", "ROUTING", "PASS"), _row("RTE-002", "ROUTING", "PASS"),
           _row("TRN-001", "TRANSIENT_PROTECTION", "PASS", phase="SCHEMATIC"),
           _row("STK-001", "STACKUP", "PASS")]


def t_an_unheld_board_reads_its_values_off_the_registry_and_is_never_released_while_frozen():
    """ACCEPTABLE: every required rule passes. The routing and protection fields read PASS, and the board is still
    NOT_READY and NOT_RELEASED, because promotion is frozen and a folder is released only by the owner."""
    L = OR.block("PCB-X-KIT-X9", _Ctx(PASSING), today="2026-09-26")
    got = OR.parse("\n".join(L))
    assert got == {"ROUTING_STATUS": "PASS", "ELECTRICAL_PROTECTION_STATUS": "PASS",
                   "FAB_READINESS": "NOT_READY", "PUBLICATION_STATUS": "NOT_RELEASED"}, got
    assert L[0] == OR.HEAD and "NOT_FOR_FAB" in L[0], L[0]
    assert "declares X9 and this folder is cut from the X9 deliverable" in "\n".join(L)


def t_a_failing_routing_or_protection_rule_is_what_the_field_says():
    """DEFECTIVE: one routing rule fails and one protection rule is unanswered. Neither field may read PASS."""
    rows = [_row("RTE-001", "ROUTING", "FAIL"), _row("RTE-002", "ROUTING", "PASS"),
            _row("TRN-001", "TRANSIENT_PROTECTION", "INCONCLUSIVE", phase="SCHEMATIC"),
            _row("BAT-001", "ENERGY_STORAGE", "PASS", phase="SCHEMATIC")]
    got = OR.parse("\n".join(OR.block("PCB-X-KIT-X9", _Ctx(rows))))
    assert got["ROUTING_STATUS"] == "FAIL" and got["ELECTRICAL_PROTECTION_STATUS"] == "INCONCLUSIVE", got
    assert got["FAB_READINESS"] == "NOT_READY", got


def t_a_held_board_carries_the_hold_s_own_words_and_says_when_its_decision_is_ruled():
    """The hold's four fields are the owner's words and are carried verbatim, whatever the registry computes; when
    the register calls the decision ruled while the hold entry stands, the block says both, and lifts nothing."""
    hold = {"decision": 31, "title": "board x's ports", "ROUTING_STATUS": "OPEN",
            "ELECTRICAL_PROTECTION_STATUS": "BLOCKED_DECISION_31", "FAB_READINESS": "NOT_READY",
            "PUBLICATION_STATUS": "HELD", "forbidden": "any orderable package", "lifts_when": "the entry is deleted"}
    ctx = _Ctx(PASSING, holds={"x": hold}, decisions={"31": {"status": "ruled", "ruled_on": "2026-09-21", "ruled_by": "SESSION"}})
    text = "\n".join(OR.block("PCB-X-KIT-X9", ctx))
    got = OR.parse(text)
    assert got == {k: hold[k] for k in OR.FIELDS}, got
    assert "held by decision 31" in text and "records decision 31 as ruled on 2026-09-21" in text, text
    assert "the registry today: the board's routing rules read RTE-001 PASS" in text


def t_a_folder_at_another_phase_says_it_is_not_the_board_being_built():
    text = "\n".join(OR.block("PCB-X-KIT-X7", _Ctx(PASSING, declared="X9")))
    assert "This folder holds X7 and board X declares X9" in text, text
    assert "not a judgement of the files in this folder" in text


def t_the_parts_the_order_code_rules_reject_are_named():
    """A failing CMP-002 is named down to the line it refuses, from the verdict that decided it."""
    d = tempfile.mkdtemp(prefix="readiness-parts-")
    v = os.path.join(d, "jlc_certify_x.verdict.json")
    json.dump({"evidence": ["WRONG_MODEL: 25 A mini blade (Keystone 3568 holder)"]}, open(v, "w"))
    rows = PASSING + [_row("CMP-002", "COMPONENT_SELECTION", "FAIL", phase="RELEASE_PACKAGE", evidence=v)]
    text = "\n".join(OR.block("PCB-X-KIT-X9", _Ctx(rows)))
    shutil.rmtree(d, ignore_errors=True)
    assert "the order-code rules name WRONG_MODEL: 25 A mini blade" in text, text


def t_a_restamp_replaces_its_block_and_leaves_the_note_byte_for_byte():
    """ACCEPTABLE: two stamps give one block, and everything below it, the provenance DOC-002 reads included, is
    the note make_handoff wrote. DEFECTIVE: a block that opens and never closes is refused, never guessed at."""
    d = tempfile.mkdtemp(prefix="readiness-stamp-")
    f = os.path.join(d, "PCB-X-KIT-X9"); os.makedirs(f)
    body = "MeshSat order notes\n\nPROVENANCE\n- The gerber zip in this folder is sha256 0123456789abcdef\n"
    p = os.path.join(f, "ORDER-NOTES.txt"); open(p, "w").write(body)
    ctx = _Ctx(PASSING)
    OR.stamp(p, ctx); once = open(p).read()
    OR.stamp(p, ctx); twice = open(p).read()
    assert once == twice and once.count(OR.HEAD) == 1, twice[:400]
    assert once.endswith(body) and OR.strip_block(once) == body, once[-200:]
    open(p, "w").write(OR.HEAD + "\nROUTING_STATUS = PASS\n" + body)
    try:
        OR.strip_block(open(p).read())
    except ValueError as e:
        assert "never closes" in str(e), e
    else:
        raise AssertionError("an unclosed block was stripped by guesswork")
    shutil.rmtree(d, ignore_errors=True)


def t_the_check_finds_a_note_without_its_block():
    d = tempfile.mkdtemp(prefix="readiness-check-")
    for n, text in (("PCB-X-KIT-X9", "MeshSat order notes\n"),
                    ("PCB-Y-KIT-Y2", "\n".join(OR.block("PCB-X-KIT-X9", _Ctx(PASSING))) + "\nMeshSat order notes\n")):
        os.makedirs(os.path.join(d, "order", n))
        open(os.path.join(d, "order", n, "ORDER-NOTES.txt"), "w").write(text)
    os.makedirs(os.path.join(d, "order", "superseded", "PCB-X-KIT-X1"))
    open(os.path.join(d, "order", "superseded", "PCB-X-KIT-X1", "ORDER-NOTES.txt"), "w").write("old\n")
    bad = OR.check(d)
    shutil.rmtree(d, ignore_errors=True)
    assert len(bad) == 1 and bad[0].startswith("PCB-X-KIT-X9"), bad


def t_every_order_note_in_this_tree_is_quarantined():
    """THE PROPERTY ON THE TREE: every board's order folder opens with a complete block, and while promotion is
    frozen none of them reads ready or released."""
    rel = OR.release_dir()
    if not os.path.isdir(os.path.join(rel, "order")): return
    assert OR.check(rel) == [], OR.check(rel)
    frozen = bool((S.manifest().get("promotion") or {}).get("frozen"))
    for d in OR.order_folders(rel):
        got = OR.parse(open(os.path.join(d, "ORDER-NOTES.txt"), encoding="utf-8").read())
        if frozen:
            assert got.get("FAB_READINESS") == "NOT_READY", (os.path.basename(d), got)
            assert got.get("PUBLICATION_STATUS") in ("NOT_RELEASED", "HELD"), (os.path.basename(d), got)
    readme = open(os.path.join(rel, "order", "README.md"), encoding="utf-8").read()
    assert OR.README_BEGIN in readme and OR.README_END in readme, "the order index carries no readiness table"
    assert "Order after the" not in readme, "the order index still tells a reader to order"


def t_the_producer_writes_no_note_without_its_block():
    """make_handoff.py computes the block BEFORE it writes the note, so a failure to compute it leaves no note at
    all, and it re-stamps every other note of the set at the end of a run. Read as source: the module needs
    pcbnew."""
    src = open(os.path.join(TOOLS, "make_handoff.py"), encoding="utf-8").read()
    i = src.index("notes = _OR.block(tag, _ORC) + notes")
    j = src.index('open(os.path.join(jd, "ORDER-NOTES.txt"), "w")')
    assert i < j, "the note is written before its readiness block is computed"
    assert "_OR.stamp_all(RELEASE" in src[j:], "the other notes of the set are not re-stamped"


def _handoff_tree():
    """make_handoff.py in a fixture tree with one D row and a stub pcbnew, as test_handoff_phase builds it."""
    import test_handoff_phase as H
    return H._tree(["D8"], "D8")


def t_a_boards_run_refuses_a_board_the_table_does_not_carry():
    """DEFECTIVE: `--boards q` names no row. It must refuse, never report the set as rebuilt."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    d, tools, stub = _handoff_tree()
    r = subprocess.run([sys.executable, os.path.join(tools, "make_handoff.py"), "--boards", "q"], capture_output=True,
                       text=True, env=dict(os.environ, PYTHONPATH=stub), cwd=d)
    shutil.rmtree(d, ignore_errors=True)
    assert r.returncode != 0 and "--boards names q, and the table carries d" in (r.stdout + r.stderr), r.stdout + r.stderr
    # ACCEPTABLE: the board the table carries is selected and the run goes on past the selection
    d, tools, stub = _handoff_tree()
    r = subprocess.run([sys.executable, os.path.join(tools, "make_handoff.py"), "--boards", "d"], capture_output=True,
                       text=True, env=dict(os.environ, PYTHONPATH=stub), cwd=d)
    shutil.rmtree(d, ignore_errors=True)
    assert "--boards names" not in (r.stdout + r.stderr), r.stdout + r.stderr


def t_an_older_order_folder_goes_under_superseded_and_is_never_overwritten_there():
    src = open(os.path.join(TOOLS, "make_handoff.py"), encoding="utf-8").read()
    body = src[src.index("def _supersede(stem, tag):"):src.index("def _outer_oz(")]
    d = tempfile.mkdtemp(prefix="supersede-")
    ns = {"os": os, "re": re, "sys": sys, "shutil": shutil, "_glob": __import__("glob"), "JLC": d}
    exec(compile(body, "make_handoff._supersede", "exec"), ns)
    for n in ("PCB-X-KIT-X7", "PCB-X-KIT-X9", "PCB-XY-KIT-Z1"):
        os.makedirs(os.path.join(d, n))
    ns["_supersede"]("pcb-x-kit", "PCB-X-KIT-X9")
    assert os.path.isdir(os.path.join(d, "superseded", "PCB-X-KIT-X7")), os.listdir(d)
    assert os.path.isdir(os.path.join(d, "PCB-X-KIT-X9")) and os.path.isdir(os.path.join(d, "PCB-XY-KIT-Z1"))
    os.makedirs(os.path.join(d, "PCB-X-KIT-X7"))                       # the same name again: refused
    try:
        ns["_supersede"]("pcb-x-kit", "PCB-X-KIT-X9")
    except SystemExit as e:
        assert "already under order/superseded/" in str(e), e
    else:
        raise AssertionError("a superseded folder was overwritten")
    shutil.rmtree(d, ignore_errors=True)
