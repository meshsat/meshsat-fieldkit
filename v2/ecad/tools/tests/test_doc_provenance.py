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
