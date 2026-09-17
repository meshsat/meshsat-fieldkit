#!/usr/bin/env python3
"""The assembly set is buildable (rule DFA-001, 16 September 2026).

DFA-001 is a BLOCKER and the half that puts parts on a board backwards is the rotation: "every polarised part's
rotation is verified against its own drawing and against the assembler's convention, with the verification
dated". It read "generation intends to comply" on six boards.

What the gate found on its first run: the seven boards place 41 distinct polarised or pin-1-sensitive
footprints that no rotation row matches at all, including three LQFP families, every JST connector and the
crystals. Those go to the assembler with KiCad's rotation unchanged, which may well be right and has never
been compared with a preview by anyone.

And there are TWO copies of the rotation table, the CSV the ordering session keeps and a literal in
make_handoff.py, which is the one that reaches a CPL. That line is on the never-auto floor, so the gate reads
both and compares rather than editing either.
"""
import os, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import assembly_set as A


def t_the_producer_table_parses_past_a_character_class():
    """`^SOT-23-[568]` contains brackets, and the first version of the parser stopped inside it and reported
    every later row as missing: a false alarm of exactly the kind this tool exists to remove."""
    rows = A.producer_table()
    assert rows, "the producer's rotation table could not be read at all"
    pats = {p for p, _o in rows}
    assert "^SOT-23-[568]" in pats and "^USB_C_Receptacle" in pats, sorted(pats)
    assert len(rows) >= 13, rows


def t_the_two_tables_agree():
    """The CSV the ordering session keeps and the literal the producer applies must say the same thing; a
    difference is a silent wrong rotation waiting to happen."""
    csv_rows = {p: int(o) for p, o, _v in A.rotations()}
    prod = dict(A.producer_table())
    assert csv_rows == prod, {k: (csv_rows.get(k), prod.get(k)) for k in set(csv_rows) | set(prod)
                              if csv_rows.get(k) != prod.get(k)}


def t_every_row_carries_the_date_it_was_compared_with_a_preview():
    rows = A.rotations()
    undated = [p for p, _o, v in rows if not v]
    assert not undated, "rows with no verification field at all: %s" % undated
    unverified = [p for p, _o, v in rows if v.upper() == "UNVERIFIED"]
    assert len(unverified) <= 2, unverified   # the two the record does not cover, named rather than hidden


def t_an_unverified_row_fails_a_board_that_uses_it():
    d = tempfile.mkdtemp(prefix="dfa-")
    p = os.path.join(d, "rot.csv")
    open(p, "w").write("# x\n^LED_0603,180,UNVERIFIED\n")
    r = A.judge(rot=p)
    fails = [f for v in r.values() for f in v["fails"]]
    assert any("nobody has compared" in f for f in fails), fails[:3]


def t_a_footprint_with_no_row_is_inconclusive_and_never_a_pass():
    """Zero can be the right offset; what is not acceptable is that nobody looked."""
    r = A.judge()
    unchecked = {x for v in r.values() for x in v["unchecked"]}
    assert unchecked, "every polarised footprint is covered, which would be a first"
    assert any("LQFP" in x for x in unchecked), sorted(unchecked)[:5]


def t_a_missing_rotation_table_is_an_absent_input_and_not_a_finding():
    """17 September 2026: this gate ran in a sweep tree that holds v2/ecad and not v2/release, so the rotation
    table was not there, and its FAIL replaced a reading taken on the runner WITH the table. A reading taken
    with less input never replaces one taken with more, and an absent input is exactly that; absence is not a
    pass either, so it is INCONCLUSIVE and names the file it could not read."""
    import assembly_set as A
    r = A.judge(rot="/nonexistent/jlc-rotations.csv")
    fails = [f for v in r.values() for f in v["fails"]]
    notes = [n for v in r.values() for n in v.get("notes", [])]
    assert not fails, "an absent table is reported as a finding: %s" % fails[:2]
    assert any("MISSING_INPUT" in n for n in notes), notes[:3]


def t_the_missing_table_reaches_the_verdict_as_inconclusive():
    import subprocess, sys, os, json, tempfile
    TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "out"))
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "assembly_set.py"),
                            "--rot", os.path.join(d, "nope.csv")], cwd=d, capture_output=True, text=True)
        assert r.returncode == 3, "exit %d, and INCONCLUSIVE is 3" % r.returncode
        v = json.load(open(os.path.join(d, "out", "assembly_set.verdict.json")))
        assert v["verdict"] == "INCONCLUSIVE" and v["counts"]["table_present"] is False, v["counts"]


def t_the_ordering_session_gets_its_work_list_as_a_document():
    """DFA-001 IS INCONCLUSIVE FOR ONE REASON AND ONLY ONE PERSON CAN CLOSE IT (17 September 2026).

    Forty-one polarised footprints reach the assembler with KiCad's rotation unchanged because nobody has
    compared them with the assembler's own 2D preview, and only the ordering session has that preview. A list
    it has to reconstruct from a gate's stdout is a list it will not work through, so the gate writes it as a
    document, generated from the same reading the verdict is taken from.

    Executed: generate it into a temporary file from a synthetic result and require every unchecked footprint,
    its boards and a designator to be in it.
    """
    import os, sys, tempfile
    TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, TOOLS)
    import assembly_set as A
    r = {"a": {"unchecked": ["D_SMB", "CP_Elec_8x6.7"], "unverified": ["SOT-23 (matched by SOT)"],
               "fails": [], "notes": [], "examples": {"D_SMB": "D3", "CP_Elec_8x6.7": "C24"}},
         "b": {"unchecked": ["D_SMB"], "unverified": [], "fails": [], "notes": [], "examples": {"D_SMB": "D9"}}}
    d = tempfile.mkdtemp(prefix="rotation-checklist-")
    path = os.path.join(d, "PCB-ROTATION-CHECKLIST.md")
    n = A.checklist(r, path)
    body = open(path, encoding="utf-8").read()
    assert n == 2, "the checklist counted %r distinct footprints, not the two in the world" % n
    assert "`D_SMB`" in body and "A, B" in body, "a footprint used by two boards does not name both: %s" % body[-400:]
    assert "D3" in body and "C24" in body, "the checklist gives no designator to look the part up by"
    assert "SOT-23 (matched by SOT)" in body, "a row that exists with no date is not listed for checking"
    assert "GENERATED" in body.splitlines()[0], "the document does not say it is generated"
