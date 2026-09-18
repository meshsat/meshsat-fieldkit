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


def t_the_rule_is_judged_per_board_and_a_folder_at_another_phase_is_an_absent_input():
    """DOC-002 asks about the document that describes THIS board (18 September 2026).

    One set-level reading was deciding it on all seven boards: board C read FAIL because a note describing C7
    names no artefact, while board C declares C24 and has no order note at all. A document that cannot be traced
    is a failure; a document that does not exist for the board being built is an absent input, and absence is
    not a pass, so it is INCONCLUSIVE and names the phase it wanted and the phase it found. DOC-001, CMP-002,
    SUP-001 and DFM-001 were each split for the same reason on 16 and 17 September.

    THE ACCEPTABLE FIXTURE is board E5, whose order folder IS at its declared phase: it is judged, and on this
    tree it FAILS, which is the one real failure the set-level reading was hiding among six it did not own.
    THE DEFECTIVE FIXTURE is every other board, whose folder is a phase the board has left."""
    import tempfile, json as _j
    rel = os.path.join(os.path.dirname(TOOLS), "..", "release", "revA")
    if not os.path.isdir(os.path.join(rel, "order")): return
    rows, fails, _n = doc_provenance.judge(rel)
    with tempfile.TemporaryDirectory() as d:
        old = os.environ.get("VERDICT_DIR")
        os.environ["VERDICT_DIR"] = d
        try: doc_provenance.per_board(rel, rows, fails)
        finally:
            if old is None: os.environ.pop("VERDICT_DIR", None)
            else: os.environ["VERDICT_DIR"] = old

        seen = [f for f in os.listdir(d) if f.startswith("doc_provenance_")]
        assert len(seen) >= 6, "a per-board reading was not written for every board: %s" % sorted(seen)

        stale = _read(d, "c")
        assert stale and stale["verdict"] == "INCONCLUSIVE", stale and stale["verdict"]
        assert "declares C24" in (stale.get("missing_input") or ""), stale.get("missing_input")
        assert "C7" in (stale.get("missing_input") or ""), "the reading does not name the phase the set holds"

        own = _read(d, "e5")
        assert own and own["verdict"] in ("PASS", "FAIL"), "board E5's own folder was not judged: %s" % own
        assert own["verdict"] == "FAIL" and own["counts"]["untraceable"] == 1, (
            "board E5's note names an artefact now, so this fixture needs its number re-read: %s" % own["counts"])


def t_a_board_never_reads_clean_from_another_board_s_folder():
    """The direction that matters: no board may read PASS from a folder that is not its own."""
    src = open(os.path.join(TOOLS, "doc_provenance.py"), encoding="utf-8").read()
    assert "at_phase = [" in src and "ph.upper() == str(decl).upper()" in src, (
        "the per-board reading does not compare the folder's phase with the board's declaration")
