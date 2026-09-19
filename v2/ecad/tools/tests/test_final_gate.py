#!/usr/bin/env python3
"""The final gate's DECISION, executed against every state it can meet (15 September 2026, red team report 1 P0).

The first version of this file checked that words existed in the source ("newest_folders", "QUOTE", "INCONCLUSIVE")
and the decision underneath was wrong on three counts: parts certification was recorded and never used, a quote-only
folder was counted as held and ignored by the PASS condition, and a board with no folder fell out of the denominator.
A source-scanning rule cannot see that. These rules run `final_gate.main` against a synthetic boards directory and a
fake `run` that answers each sub-gate with a chosen exit code, and assert the verdict for each state of the table:
all pass, a deliverable failure, a quote folder, a missing board, contracts failed, contracts unjudgeable,
certification open, certification unjudgeable, and a subset."""
import os, sys, json, tempfile, importlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import verdict

LETTERS = ("a", "b", "c", "d", "e", "e5", "p")


def _world(folders, sub, phases=None):
    """A boards directory with the given deliverable folders and a fake `run` answering each sub-gate.
    `sub` maps 'deliverable:<folder>' | 'contracts' | 'certify' to (rc, stdout)."""
    d = tempfile.mkdtemp(prefix="final-gate-")
    bdir = os.path.join(d, "boards"); os.makedirs(bdir)
    for L in LETTERS:
        if L != "e5": open(os.path.join(bdir, "%s.json" % L), "w").write(json.dumps({"phase": (phases or {}).get(L, "%s1" % L.upper())}))
    rdir = os.path.join(d, "release"); os.makedirs(rdir)
    for f in folders:
        os.makedirs(os.path.join(rdir, f)); open(os.path.join(rdir, f, "%s-gerbers.zip" % f.split("-revA")[0].replace("meshsat-", "")), "w").write("")
    def run(cmd):
        tool = os.path.basename(cmd[1])
        if tool == "verify_deliverable.py":
            rc, out = sub.get("deliverable:" + os.path.basename(cmd[2]), (0, "verify_deliverable: ALL PASS (36 of 36 properties)"))
            return rc, out
        if tool == "check_contracts.py": return sub.get("contracts", (0, "contracts: ALL PASS 42 of 42"))
        if tool == "jlc_certify.py": return sub.get("certify", (0, "jlc_certify: 469 components, CERTIFIED 469"))
        if tool == "claims_check.py":
            return sub.get("claims", (0, "claims_check: 19 claim sentence(s) in 8 document(s), 0 without a qualifier, an evidence reference or a declared reason"))
        raise AssertionError("unexpected command %s" % cmd)
    # THIS SYNTHETIC SET DECLARES ITS OWN HOLDS, and declares none (16 September 2026). The gate reads
    # tools/pcb_board_holds.yaml by default, which today holds board E on decision 31, so without this every
    # fixture below would be judging the real hold instead of the folder logic it is about. The hold itself
    # has its own fixtures both ways in test_board_hold.py.
    hold = os.path.join(d, "holds.yaml"); open(hold, "w").write("holds: {}\n")
    return d, bdir, rdir, run, hold


def _verdict(argv, folders, sub, out_dir, phases=None):
    fg = importlib.import_module("final_gate")
    d, bdir, rdir, run, hold = _world(folders, sub, phases)
    fg.BOARDS = rdir
    cwd = os.getcwd(); os.chdir(d)
    try:
        rc = fg.main(list(argv), run=run, boards_dir=bdir, holds_path=hold)
    finally:
        os.chdir(cwd)
    v = json.load(open(os.path.join(d, "out", "final_gate.verdict.json")))
    return rc, v["result"] if "result" in v else v.get("verdict"), v


FULL = ["meshsat-pcb-%s-revA-%s1" % (L, L.upper()) for L in LETTERS]


def t_the_whole_manifest_passing_is_pass():
    rc, res, v = _verdict([], FULL, {}, None)
    assert res == "PASS" and rc == 0, (res, rc, v)
    assert v["denominator"] == 7


def t_a_deliverable_failure_is_fail():
    rc, res, v = _verdict([], FULL, {"deliverable:meshsat-pcb-c-revA-C1": (1, "verify_deliverable: 1 FAIL (35 of 36 properties)")}, None)
    assert res == "FAIL" and rc != 0, (res, rc)


def t_a_quote_only_folder_fails_the_set():
    folders = [f for f in FULL if "-pcb-b-" not in f] + ["meshsat-pcb-b-revA-B1-quote"]
    rc, res, v = _verdict([], folders, {}, None)
    assert res == "FAIL", "a held board read as a pass of the set: %s" % v
    assert v["counts"]["quote"] == 1


def t_a_required_board_with_no_folder_fails_the_set():
    folders = [f for f in FULL if "-pcb-d-" not in f]
    rc, res, v = _verdict([], folders, {}, None)
    assert res == "FAIL", "a board that vanished from the table read as a pass: %s" % v
    assert v["counts"]["missing"] == 1 and any("D: no deliverable folder" in e for e in v["evidence"])
    assert v["denominator"] == 7, "the denominator is the manifest, not the folders that exist"


def t_failed_contracts_are_fail_and_absent_contracts_are_inconclusive():
    rc, res, v = _verdict([], FULL, {"contracts": (1, "contracts: 2 FAIL of 42")}, None)
    assert res == "FAIL", v
    rc, res, v = _verdict([], FULL, {"contracts": (3, "6 board netlist(s) absent from this tree")}, None)
    assert res == "INCONCLUSIVE", v


def t_open_certification_is_fail_and_unasked_certification_is_inconclusive():
    rc, res, v = _verdict([], FULL, {"certify": (1, "jlc_certify: 469 components, CERTIFIED 460, WRONG_MODEL 9")}, None)
    assert res == "FAIL", "parts certification OPEN and the gate said PASS: %s" % v
    rc, res, v = _verdict([], FULL, {"certify": (3, "jlc_certify: 469 components, NOT_CHECKED 469")}, None)
    assert res == "INCONCLUSIVE", v


def t_a_failure_beats_an_unjudged_component():
    rc, res, v = _verdict([], FULL, {"contracts": (3, "absent"), "deliverable:meshsat-pcb-a-revA-A1": (1, "verify_deliverable: 1 FAIL (35 of 36 properties)")}, None)
    assert res == "FAIL", "an unjudged contract check hid a real deliverable failure: %s" % v


def t_a_subset_is_never_the_set():
    rc, res, v = _verdict(["--boards", "c,d"], FULL, {}, None)
    assert res == "INCONCLUSIVE", "a two-board look read as the set's PASS: %s" % v


def t_it_opens_no_board_and_touches_no_host():
    src = open(os.path.join(TOOLS, "final_gate.py")).read()
    for bad in ("import pcbnew", "ssh ", "route_one", "freerouting"):
        assert bad not in src, "final_gate should read artefacts only, found %r" % bad
    assert "*.kicad_pcb" not in src, "the stem must come from the gerber zip's name, not from a board glob"
    assert 'l.startswith("verify_deliverable:")' in src, "the summary is reconstructed instead of read"


def t_a_folder_that_is_not_the_declared_phase_fails_the_set():
    """15 September 2026, after the return-current rules became gates: every folder in the tree had been cut before those gates
    existed and every one passed here, because verify_deliverable judges a folder against ITSELF. The tree declares the phase
    its generators stamp; a folder naming an earlier one is a board this set is not building."""
    rc, res, v = _verdict([], FULL, {}, None, phases={"c": "C9"})
    assert res == "FAIL" and rc == 1, (res, rc, v)
    assert v["counts"]["fail"] == 1 and v["counts"]["pass"] == 6, v["counts"]
    rc2, res2, v2 = _verdict([], FULL, {}, None)   # the same folders, each the declared phase
    assert res2 == "PASS", (res2, v2)


def t_a_rating_claimed_in_a_public_document_fails_the_set():
    """Rule ENV-002 at the release gate. The documents go to the public mirror within minutes of a push, and
    nothing in this project has been fabricated or powered: a rating asserted without the test that
    establishes it is a promise to whoever would carry the kit, and it stops the release exactly as a failed
    folder does."""
    rc, res, v = _verdict([], FULL, {"claims": (1, "claims_check: 19 claim sentence(s) in 8 document(s), 3 without a qualifier, an evidence reference or a declared reason")}, None)
    assert res == "FAIL" and rc != 0, "an unqualified rating in a public document passed the release gate: %s" % v
    assert any("claims" in e for e in v.get("evidence", [])), "the refusal does not say the claims screen is why: %s" % v


def t_an_unreadable_claims_screen_is_inconclusive_and_never_a_pass():
    rc, res, v = _verdict([], FULL, {"claims": (3, "claims_check: INCONCLUSIVE")}, None)
    assert res == "INCONCLUSIVE", "a claims screen that could not judge read as a pass: %s" % v


def t_the_set_verdict_does_not_decide_every_board_s_own_paperwork():
    """Fourteen rule-board pairs said the wrong thing about the wrong boards (MESHSAT-862, 16 September 2026).

    DOC-001 and OUT-001 are verified by the final gate, and the final gate judges the SET, so every board
    inherited the set's failure: board E5's folder is the ONE that passes and it read FAIL on both rules
    because six other folders are stale. The set verdict is unchanged and still decides the release; the
    per-board ones say whose paperwork is actually behind."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "final_gate.py"),
               encoding="utf-8").read()
    assert '_v.write("final_gate_%s"' in src, "the gate writes no per-board verdict"
    # 19 September 2026: this was two fixed byte windows (700 and 1,400) and the second broke the moment the
    # per-board write grew a missing-input line. A rule about two lines uses the construct that holds them.
    from harness import block
    seg = block(src, '    for r in rows:\n        _v.write("final_gate_%s"')
    assert seg, "the per-board loop is not where this rule looks for it"
    assert "quiet=True" in seg, "the per-board verdicts drown the set's own line"
    assert 'for l in missing' in src[src.index('_v.write("final_gate_%s"'):], "a required board with no folder gets no verdict of its own"

    # AND THE READING SAYS WHY IT COULD NOT ANSWER (19 September 2026). Board B's DOC-001 row read
    # "final_gate_b INCONCLUSIVE" and nothing else, while this verdict's own evidence already said the tree
    # declares B21 and the only folder is a quote. A quote folder is a reading taken with less input.
    assert "missing_input=" in seg, "a quote folder does not declare the input it lacks"
    assert 'r["quote"]' in seg and "declared" in seg, "the missing input does not name the phase the folder cannot answer for"
    assert 'r["stale"]' in seg, "a stale folder still gets a note true of every board"
    cov = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pcb_rules_coverage.yaml"),
               encoding="utf-8").read()
    assert "final_gate_<letter>" in cov, "the coverage map still reads only the set verdict for DOC-001 and OUT-001"


def t_a_run_against_another_manifest_writes_nothing_into_this_trees_evidence():
    """THE INCIDENT, 18 September 2026, and it is the third time this shape has cost a reading.

    `verdict.write` defaults to `out` relative to the CURRENT DIRECTORY. A fixture that hands this gate a
    synthetic boards directory and calls it from `v2/ecad` therefore wrote its two-folder answer straight over
    the set's own: `final_gate PASS of 2` sat in `v2/ecad/out/` and rule OUT-001, the order paperwork, read it
    as a PASS on all seven boards while five of the seven folders are stale or held. The manifest and the
    evidence travel together now: a caller that supplies its own manifest gets its own out directory, and this
    rule runs the gate the way the fixture did and requires the tree's own verdict not to move."""
    import json as _j, importlib, shutil, tempfile, os
    fg = importlib.import_module("final_gate")
    ecad = os.path.dirname(TOOLS)
    live = os.path.join(ecad, "out", "final_gate.verdict.json")
    before = open(live, encoding="utf-8").read() if os.path.isfile(live) else None

    def fake_run(cmd):
        who = os.path.basename(cmd[1])
        if who == "verify_deliverable.py": return 0, "verify_deliverable: ALL PASS (21 of 21 properties)\n"
        if who == "check_contracts.py": return 0, "contracts ALL PASS\n"
        if who == "jlc_certify.py": return 0, "jlc_certify: 1 components, CERTIFIED 1\n"
        return 0, "claims_check: 0 without a qualifier\n"

    d = tempfile.mkdtemp(prefix="final-gate-elsewhere-")
    boards = os.path.join(d, "boards"); os.makedirs(boards)
    _j.dump({"name": "pcb-e1-dock", "phase": "E9"}, open(os.path.join(boards, "e.json"), "w"))
    folders = os.path.join(d, "release", "revA", "boards")
    os.makedirs(os.path.join(folders, "meshsat-pcb-e-revA-E9")); os.makedirs(os.path.join(folders, "meshsat-pcb-e5-revA-E5"))
    keep, cwd = fg.BOARDS, os.getcwd()
    try:
        fg.BOARDS = folders; os.chdir(ecad)          # exactly what the offending fixture did
        fg.main(["--json", os.path.join(d, "out.json")], run=fake_run, boards_dir=boards)
        after = open(live, encoding="utf-8").read() if os.path.isfile(live) else None
        assert after == before, "a run against another manifest overwrote this tree's own final_gate verdict"
        assert os.path.isfile(os.path.join(d, "out", "final_gate.verdict.json")), \
            "the run wrote its verdict neither here nor beside the manifest it was given"
    finally:
        fg.BOARDS = keep; os.chdir(cwd); shutil.rmtree(d, ignore_errors=True)
