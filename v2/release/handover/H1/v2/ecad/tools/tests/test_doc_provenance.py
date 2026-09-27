#!/usr/bin/env python3
"""A document that asserts a number about the hardware names the artefact it was read from (rule DOC-002).

MESHSAT-862, 16 September 2026. The rule's phase is RELEASE_PACKAGE and the document in scope is the one a
person reads while placing an order: ORDER-NOTES.txt states a board's size, layer count, thickness, copper
weight and stackup, and it said only "generated from the board file". A note beside a folder cut three phases
ago reads exactly like one beside the current board, and on 12 September three of the seven folders in this
tree described boards this project was not building.
"""
import os, sys, json, glob, hashlib, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import doc_provenance


def _folder(root, name, note_text, zip_bytes=b"gerbers"):
    d = os.path.join(root, "order", name)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "x-gerbers.zip"), "wb").write(zip_bytes)
    open(os.path.join(d, "ORDER-NOTES.txt"), "w").write(note_text)
    return d


def t_a_note_that_names_no_artefact_is_refused():
    """The defective fixture, and it is the tree's own state today."""
    r = tempfile.mkdtemp(prefix="prov-bad-")
    _folder(r, "PCB-X", "MeshSat order notes\n- Size 100 x 50 mm, 4 copper layers, 1.6 mm FR-4\n")
    rows, fails, _ = doc_provenance.judge(r)
    assert rows and fails, (rows, fails)
    assert "names no artefact" in fails[0], fails


def t_a_note_that_names_the_artefact_beside_it_passes():
    """The acceptable fixture: the sha in the note IS the gerber zip in its own folder."""
    r = tempfile.mkdtemp(prefix="prov-ok-")
    body = b"gerbers for this board"
    sha = hashlib.sha256(body).hexdigest()
    _folder(r, "PCB-X", "MeshSat order notes\nPROVENANCE\n- The gerber zip in this folder is sha256 %s\n"
            % sha[:16], zip_bytes=body)
    rows, fails, _ = doc_provenance.judge(r)
    assert rows and not fails, fails


def t_a_note_that_names_another_boards_artefact_is_refused():
    """The case that has actually happened: the numbers are right about a board nobody is building."""
    r = tempfile.mkdtemp(prefix="prov-wrong-")
    other = hashlib.sha256(b"a different board entirely").hexdigest()
    _folder(r, "PCB-X", "MeshSat order notes\n- sha256 %s\n" % other[:16], zip_bytes=b"this board")
    rows, fails, _ = doc_provenance.judge(r)
    assert fails and "not the same thing" in fails[0], fails


def t_the_writers_put_the_identity_in():
    """Both documents that assert hardware numbers name their artefact at the point they are written, so the
    check passes the moment either runs rather than needing anything typed by hand."""
    mh = open(os.path.join(TOOLS, "make_handoff.py"), encoding="utf-8").read()
    assert "PROVENANCE" in mh and "sha256 %s" in mh, "make_handoff writes no provenance block"
    assert "-gerbers.zip" in mh, "the note does not name the artefact the fabricator receives"
    ej = open(os.path.join(TOOLS, "export_jlc.sh"), encoding="utf-8").read()
    assert "sha256 %s" in ej and "_bsha" in ej, "export_jlc's own note names no board"


def t_the_tree_today_is_reported_rather_than_assumed():
    """A rule whose subject does not exist yet must be INCONCLUSIVE, not a pass. There are seven order folders
    in this tree and each has a note, so this rule has something to judge and judges it."""
    rel = os.path.join(os.path.dirname(TOOLS), "..", "release", "revA")
    if not os.path.isdir(os.path.join(rel, "order")):
        return
    rows, fails, notes = doc_provenance.judge(rel)
    assert rows, "the order folders hold no note, so this rule would read INCONCLUSIVE"


def _read(d, letter):
    import json as _j
    p = os.path.join(d, "doc_provenance_%s.verdict.json" % letter)
    return _j.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def _per_board_on(rel, boards):
    """doc_provenance.per_board over a fixture release, with the board table replaced for the call."""
    import tempfile as _t
    rows, fails, _n = doc_provenance.judge(rel)
    keep = doc_provenance._boards
    d = _t.mkdtemp(prefix="prov-per-board-")
    old = os.environ.get("VERDICT_DIR")
    os.environ["VERDICT_DIR"] = d
    try:
        doc_provenance._boards = lambda: boards
        doc_provenance.per_board(rel, rows, fails)
    finally:
        doc_provenance._boards = keep
        if old is None: os.environ.pop("VERDICT_DIR", None)
        else: os.environ["VERDICT_DIR"] = old
    return d


def t_the_rule_is_judged_per_board_and_a_folder_at_another_phase_is_an_absent_input():
    """DOC-002 asks about the document that describes THIS board (18 September 2026).

    One set-level reading was deciding it on all seven boards: board C read FAIL because a note describing C7
    names no artefact, while board C declares C24 and has no order note at all. A document that cannot be traced
    is a failure; a document that does not exist for the board being built is an absent input, and absence is
    not a pass, so it is INCONCLUSIVE and names the phase it wanted and the phase it found. DOC-001, CMP-002,
    SUP-001 and DFM-001 were each split for the same reason on 16 and 17 September.

    ON FIXTURES SINCE 26 SEPTEMBER 2026. This rule read the tree: board C stale at C7 and board E5 failing at its
    own phase. Decision 41 rebuilt the order set, C24 and E5 now carry notes that name their zips, and a rule that
    fails when its subject is fixed is a rule about history. The same three states, built:
    THE DEFECTIVE FIXTURE, a board whose only order folder is a phase it has left: INCONCLUSIVE, naming both.
    A board whose folder is at its declared phase and whose note names no artefact: FAIL.
    THE ACCEPTABLE FIXTURE, a board whose folder is at its declared phase and names the zip beside it: PASS."""
    import tempfile
    rel = tempfile.mkdtemp(prefix="prov-phases-")
    _folder(rel, "PCB-X-KIT-X7", "MeshSat order notes\n- Size 10 x 10 mm\n")                    # x declares X9
    _folder(rel, "PCB-Y-KIT-Y3", "MeshSat order notes\n- Size 10 x 10 mm\n")                    # y declares Y3, no provenance
    body = b"the zip of z"
    _folder(rel, "PCB-Z-KIT-Z2", "MeshSat order notes\nPROVENANCE\n- The gerber zip in this folder is sha256 %s\n"
            % hashlib.sha256(body).hexdigest()[:16], zip_bytes=body)
    d = _per_board_on(rel, [("x", "pcb-x-kit", "X9"), ("y", "pcb-y-kit", "Y3"), ("z", "pcb-z-kit", "Z2")])
    stale = _read(d, "x")
    assert stale and stale["verdict"] == "INCONCLUSIVE", stale and stale["verdict"]
    assert "declares X9" in (stale.get("missing_input") or ""), stale.get("missing_input")
    assert "X7" in (stale.get("missing_input") or ""), "the reading does not name the phase the set holds"
    own_bad = _read(d, "y")
    assert own_bad and own_bad["verdict"] == "FAIL" and own_bad["counts"]["untraceable"] == 1, own_bad
    own_ok = _read(d, "z")
    assert own_ok and own_ok["verdict"] == "PASS", own_ok


def t_every_board_whose_declared_phase_has_an_order_folder_reads_its_own_note():
    """THE PROPERTY ON THE TREE (26 September 2026, owner decision 41): wherever the order set holds a folder at
    the phase its board declares, the note in it names the gerber zip beside it, so DOC-002 is a PASS there and
    never a FAIL. A board whose folder is at another phase is an absent input and is not this rule's business."""
    rel = os.path.join(os.path.dirname(TOOLS), "..", "release", "revA")
    if not os.path.isdir(os.path.join(rel, "order")): return
    rows, fails, _n = doc_provenance.judge(rel)
    d = _per_board_on(rel, doc_provenance._boards())
    judged = [l for l, _s, _p in doc_provenance._boards() if (_read(d, l) or {}).get("verdict") in ("PASS", "FAIL")]
    bad = ["%s: %s" % (l, _read(d, l)["evidence"]) for l in judged if _read(d, l)["verdict"] != "PASS"]
    assert not bad, "a note at its board's declared phase does not name its own zip: %s" % bad


def t_a_board_never_reads_clean_from_another_board_s_folder():
    """The direction that matters: no board may read PASS from a folder that is not its own."""
    src = open(os.path.join(TOOLS, "doc_provenance.py"), encoding="utf-8").read()
    assert "at_phase = [" in src and "ph.upper() == str(decl).upper()" in src, (
        "the per-board reading does not compare the folder's phase with the board's declaration")
