#!/usr/bin/env python3
"""The review packet builder (MESHSAT-1357, 26 September 2026; the review of that day, section 5).

`review_packet.py` builds a reviewer's packet for one board at an exact revision. What must hold, on small synthetic
git repositories so the rules run on any host, with no KiCad and no board of this tree:
  * a change is credited only with the IDs written in its OWN statement's comment (the block directly above it, or on
    its lines) on lines ADDED between the two revisions; an ID already on an unchanged line is context; a change with
    none is NO_ID_OF_ANY_KIND;
  * a comment reached past another statement, above an enclosing if/try, only mentioning the reference, or anywhere
    in the added hunk is a CANDIDATE (UNVERIFIED_ATTRIBUTION), never credited: a statement under an if/try whose
    comment sits above the compound, a statement below another commented statement, and a hunk holding two findings
    are each fixtures (the review cycle of 26 September 2026 found a neighbour's IDs credited in all three shapes);
  * a hand-read attribution map is refused unless every ID is written on its cited lines and every cited range is
    tied to the change, a refused build leaves no packet behind, and the counts keep finding IDs apart from rulings;
  * no packet file is one the repository's own .gitignore would keep out of a commit (the native netlists sat under
    an ignored `out/` until 26 September 2026);
  * a package name (SOD-323) is never read as a rule ID; a real rule ID counts only when the registry holds it;
  * the stage reads git objects, never the working tree, and building writes nothing into the repository;
  * every artefact is in MANIFEST.json and SHA256SUMS, `verify` passes on the packet and fails on one changed byte
    or one stray file;
  * the README says first that the design is unbuilt and that the packet releases nothing;
  * a part is joined to SOURCES.yaml by its exact LCSC code in a code field, never by a prefix, a prose mention or an
    alternative the entry did not fit, and a multi-part entry lists only the documents that name that code;
  * a BOM line with NO code joins only an entry that names the board and is on the revision's generators, through its
    `where` read at its own revision and naming the reference or the part, or its fitted order code in the value; a
    stale `where`, another statement on the same generator line, another board, a candidate entry and a coded line are
    each refused, and an entry that names the board and joined nothing is listed (the review cycle of 26 September
    2026 found board E's corrected choke L2 without the entry filed for it, because code-less lines never joined);
  * every packet says QUARANTINED, NOT_FOR_FAB on its front page and in its manifest, and a held board quotes its hold;
    a packet built without a hand reading says on its front page that its change counts are mechanical only;
  * the contracts listed for a board are exactly those whose `boards` name it, with the result the checker decided,
    and the checker's verdicts go to a scratch directory.
"""
import json, os, shutil, subprocess, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip
import review_packet as RP


def _net(comps, nets):
    """A KiCad s-expression netlist that regen_compare.parse_net reads: comps {ref: (value, footprint, lcsc)},
    nets {name: [(ref, pin)]}."""
    c = "".join('    (comp (ref "%s")\n      (value "%s")\n      (footprint "%s")\n      (fields\n'
                '        (field (name "LCSC") "%s"))\n      (libsource (lib "Device") (part "X") (description ""))\n'
                '      (tstamps "t-%s"))\n' % (r, v, f, l, r) for r, (v, f, l) in sorted(comps.items()))
    n = "".join('    (net (code "%d") (name "%s")\n%s)\n' % (
        i + 1, name, "".join('      (node (ref "%s") (pin "%s") (pintype "passive"))\n' % rp for rp in nodes))
        for i, (name, nodes) in enumerate(sorted(nets.items())))
    return ('(export (version "E")\n  (design\n    (source "/x/pcb-x-test.kicad_sch")\n    (date "2026-09-26T00:00:00+0000")\n'
            '    (tool "Eeschema 9.0.9"))\n  (components\n%s  )\n  (nets\n%s  )\n)\n' % (c, n))


GEN_V1 = '''#!/usr/bin/env python3
"""fixture generator"""
# the input stage, as it was: S-09 was already recorded here
part("U1", "Device", "X", "buffer A", "SOT", {"1": "IN", "2": "OUT"}, "C1234")
# an old note naming F-IN-01
part("U2", "Device", "X", "switch", "SOT", {"1": "IN", "2": "GND"}, "C555")
part("D9", "Device", "D", "clamp", "SOD", {"1": "IN", "2": "GND"})
'''

GEN_V2 = '''#!/usr/bin/env python3
"""fixture generator"""
# the input stage, as it was: S-09 was already recorded here
# THE BUFFER IS NOW A SCHMITT PART (W6-F5), package SOD-323 beside it
part("U1", "Device", "X", "buffer B", "SOT", {"1": "IN", "2": "OUT"}, "C1234")
# an old note naming F-IN-01
part("U2", "Device", "X", "switch", "SOT", {"1": "OUT", "2": "GND"}, "C555")
# D9 is removed: its job moves to U1 (adjudication A03)
# THE NEW PULL (owner D-03.2, decision 30)
part("R5", "Device", "R", "10k", "R0603", {"1": "IN", "2": "VCC"}, "C12345")
# THE TEST ACCESS (rule TST-001; rule ZZZ-999 is not in the registry)
for i, net in enumerate(("IN", "OUT"), 7): tp("TP%d" % i, net)
'''


def _git(repo, *a):
    return subprocess.run(["git", "-C", repo] + list(a), capture_output=True, text=True, check=True).stdout.strip()


def _write(root, rel, text):
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text)


CHECKER = '''import os, sys
MISSING = []
def check(ok, text, detail="", boards=None, group=None):
    print(("PASS  " if ok else "FAIL  ") + text)
check(True, "x alone", boards={"X"})
check(False, "x and y disagree", "pin 3", boards={"X", "Y"})
check(True, "y alone", boards={"Y"})
open(os.path.join(os.environ["VERDICT_DIR"], "checker-ran.flag"), "w").write("1")
sys.exit(0)
'''


def _repo(with_checker=True):
    if shutil.which("git") is None: raise Skip("no git on this host")
    d = tempfile.mkdtemp(prefix="rp-test-")
    r = os.path.join(d, "repo"); os.makedirs(r)
    _git(r, "init", "-q")
    base = {
        "v2/ecad/tools/routeflow/x.json": json.dumps({"board": "pcb-x-test", "project": "v2/ecad/pcb-x-test"}),
        "v2/ecad/tools/boards/x.json": json.dumps({"name": "pcb-x-test", "phase": "X3", "_phase_why": "fixture"}),
        "v2/ecad/tools/pcb_rules.yaml": "rules:\n  - {id: TST-001}\n  - {id: SCH-002}\n",
        "v2/ecad/tools/pcb_interfaces.yaml": "interfaces:\n  SIG:\n    what: a signal\n    impedance_ohm: 90\nboards:\n  x:\n    assignments:\n      - {interface: SIG, patterns: [\"OU*\"], class: USB}\n",
        "v2/ecad/tools/pcb_board_holds.yaml": "holds:\n  x: {decision: 31, title: fixture hold, ELECTRICAL_PROTECTION_STATUS: BLOCKED}\n",
        "v2/ecad/tools/pcb_decisions.yaml": "decisions:\n  - {n: 42, title: open one, status: open}\n  - {n: 41, title: closed one, status: ruled}\n",
        "v2/ecad/meshsat.pretty/Foo.kicad_mod": "(footprint Foo)\n",
        "v2/ecad/pcb-x-test/pcb-x-test.kicad_sch": '(kicad_sch (title_block (comment 1 "Phase X3 schematic")))\n',
        "v2/ecad/pcb-x-test/pcb-x-test.kicad_pcb": "(kicad_pcb board file that must never be staged)\n",
        "v2/vendor/SOURCES.yaml": ("parts:\n  - id: pull-up\n    boards: [X]\n    lcsc: \"C12345 (R5)\"\n    note: \"the switch C555 is named here in prose only\"\n"
                                   "    alternative_readings:\n      - {lcsc: C1234, note: weighed, not fitted}\n"
                                   "    fitted_mpn: R-10K\n    identity: MATCH\n    documents:\n      - {path: v2/vendor/r.pdf, revision: A, sha256: abc}\n"
                                   "  - id: clamps\n    parts_and_makers:\n      - {code: C555, model: S1}\n      - {code: C777, model: S2}\n"
                                   "    documents:\n      - {path: v2/vendor/s1.pdf, matches_fitted: \"yes for C555\"}\n"
                                   "      - {path: v2/vendor/s2.pdf, matches_fitted: \"yes for C777\"}\n"),
    }
    for k, v in base.items(): _write(r, k, v)
    _write(r, "v2/ecad/tools/gen_sch_x.py", GEN_V1)
    _write(r, "v2/ecad/pcb-x-test/out/pcb-x-test.net", _net(
        {"U1": ("buffer A", "Package:SOT", "C1234"), "U2": ("switch", "Package:SOT", "C555"), "D9": ("clamp", "meshsat:Foo", "")},
        {"/IN": [("U1", "1"), ("U2", "1"), ("D9", "1")], "/OUT": [("U1", "2")], "GND": [("U2", "2"), ("D9", "2")]}))
    _git(r, "add", "-A"); _git(r, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "v1")
    v1 = _git(r, "rev-parse", "HEAD")
    _write(r, "v2/ecad/tools/gen_sch_x.py", GEN_V2)
    if with_checker: _write(r, "v2/ecad/tools/check_contracts.py", CHECKER)
    _write(r, "v2/ecad/pcb-x-test/out/pcb-x-test.net", _net(
        {"U1": ("buffer B", "Package:SOT", "C1234"), "U2": ("switch", "Package:SOT", "C555"),
         "R5": ("10k", "Resistor:R0603", "C12345"), "TP7": ("TP", "TestPoint:TP", ""), "TP8": ("TP", "TestPoint:TP", "")},
        {"/IN": [("U1", "1"), ("R5", "1"), ("TP7", "1")], "/OUT": [("U1", "2"), ("U2", "1"), ("TP8", "1")],
         "GND": [("U2", "2")], "VCC": [("R5", "2")]}))
    _git(r, "add", "-A"); _git(r, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "v2")
    v2 = _git(r, "rev-parse", "HEAD")
    return d, r, v1, v2


def _packet(with_checker=True):
    d, r, v1, v2 = _repo(with_checker)
    st = os.path.join(d, "stage"); out = os.path.join(d, "packet")
    RP.stage(r, v2, v1, st)
    m = RP.build(st, "x", out, None, (), True)
    return d, r, v1, v2, st, out, m


def _changes(out):
    return {c["ref"]: c for c in json.load(open(os.path.join(out, "changes", "changes.json")))["changes"]}


def t_a_change_is_credited_only_with_ids_on_lines_it_added():
    d, *_, out, m = _packet()
    try:
        ch = _changes(out)
        assert ch["U1"]["finding_ids"] == ["W6-F5"] and ch["U1"]["read"] == "direct", ch["U1"]
        assert "S-09" in ch["U1"]["evidence"]["direct"]["context"].get("finding", []), ch["U1"]["evidence"]
        assert "S-09" not in ch["U1"]["finding_ids"], "an ID on an unchanged line was credited to the change"
        assert ch["U2"]["status"] == "NO_ID_OF_ANY_KIND", ch["U2"]
        assert ch["U2"]["pins_moved"] == {"1": ["IN", "OUT"]}, ch["U2"]["pins_moved"]
        assert ch["R5"]["authority_ids"] == ["D-03.2", "decision 30"] and ch["R5"]["finding_ids"] == [], ch["R5"]
        k = m["counts"]
        assert (k["with_finding_id"], k["authority_or_rule_only"], k["no_id_of_any_kind"], k["unverified_attribution"],
                k["without_finding_id"]) == (1, 3, 1, 1, 5), k
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_loop_and_removed_references_are_attributed_and_say_how():
    d, *_, out, m = _packet()
    try:
        ch = _changes(out)
        for tp in ("TP7", "TP8"):
            assert ch[tp]["kind"] == "ADDED" and ch[tp]["rule_ids"] == ["TST-001"] and ch[tp]["read"] == "loop", ch[tp]
            assert ch[tp]["evidence"]["anchor"] == "loop", ch[tp]["evidence"]
        assert ch["D9"]["kind"] == "REMOVED", ch["D9"]
        # an added comment that names a removed part is a candidate, never the removal's credited finding
        assert ch["D9"]["status"] == "UNVERIFIED_ATTRIBUTION" and ch["D9"]["finding_ids"] == [], ch["D9"]
        assert "A03" in ch["D9"]["evidence"]["automatic"]["candidate_ids"], ch["D9"]["evidence"]
        assert any(cd["kind"] == "mention" for cd in ch["D9"]["evidence"]["candidates"]), ch["D9"]["evidence"]
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_package_name_is_never_a_rule_id():
    ids = RP.extract_ids("package SOD-323 and DFN-006 beside TST-001 and ZZZ-999", {"TST-001"})
    assert ids.get("rule") == ["TST-001"], ids
    assert RP.extract_ids("W7-R2-01 W5-ZEROIZE-4 F-IN-01 R4E-02 A03 A22 D-03.2 D-01-R2", set()) == {
        "adjudication": ["A03"], "finding": ["F-IN-01", "R4E-02", "W5-ZEROIZE-4", "W7-R2-01"],
        "owner_ruling": ["D-01-R2", "D-03.2"]}, "an ID form of the review records is misread"


def t_the_stage_reads_git_objects_and_building_writes_nothing_into_the_repository():
    d, r, v1, v2 = _repo()
    try:
        _write(r, "v2/ecad/tools/gen_sch_x.py", "# a working-tree edit that must not be staged\n")
        before = _git(r, "status", "--porcelain")
        st = os.path.join(d, "stage"); out = os.path.join(d, "packet")
        rec = RP.stage(r, v2, v1, st)
        assert open(os.path.join(st, "rev", "v2", "ecad", "tools", "gen_sch_x.py")).read() == GEN_V2, "the working tree was staged"
        assert not any(k.endswith(".kicad_pcb") for k in rec["files"]), "a board file was staged"
        RP.build(st, "x", out, None, (), True)
        assert _git(r, "status", "--porcelain") == before, "building changed the repository"
        assert not os.path.exists(os.path.join(r, "out")), "a verdict reached the repository"
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_packet_verifies_and_one_changed_byte_or_one_stray_file_does_not():
    d, *_, out, m = _packet()
    try:
        assert RP.verify(out) == [], RP.verify(out)
        p = os.path.join(out, "native", "gen_sch_x.py")
        open(p, "a").write("#")
        bad = RP.verify(out)
        assert any("gen_sch_x.py" in b for b in bad), bad
        open(p, "w").write(GEN_V2)
        assert RP.verify(out) == [], "restoring the bytes did not restore the packet"
        open(os.path.join(out, "stray.txt"), "w").write("x")
        assert any("stray.txt" in b for b in RP.verify(out)), "an unlisted file was accepted"
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_the_readme_says_first_that_nothing_is_built_or_released():
    d, *_, out, m = _packet()
    try:
        head = open(os.path.join(out, "README.md")).read()[:2400]
        assert RP.BANNER in head and "does NOT release" in head and "UNBUILT PROTOTYPE" in head, head[:400]
        assert RP.READINESS in head and m["readiness"] == RP.READINESS, "the packet does not carry the quarantine marker"
        assert "HELD by decision 31" in head and m["hold"][0]["decision"] == 31, "the board's hold is not quoted"
        assert os.path.isfile(os.path.join(out, RP.IDENTITY_CSV)) and "NOT_FOR_FAB" in RP.IDENTITY_CSV
        assert m["change_attribution"] == "MECHANICAL_ONLY" and "CHANGE ATTRIBUTION: MECHANICAL ONLY" in head, \
            "a packet without a hand reading does not say its counts are mechanical"
        assert m["complete"] is False, "a packet without the KiCad exports called itself complete"
        assert "INCOMPLETE" in " ".join(m["notes"]), m["notes"]
        assert "host" in m and "nllei" not in json.dumps(m), "a host name reached a public artefact"
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_part_is_joined_to_its_source_by_the_exact_code():
    d, *_, out, m = _packet()
    try:
        rows = {r["lcsc"]: r for r in json.load(open(os.path.join(out, "bom", "parts-identity.json")))}
        assert [e["id"] for e in rows["C12345"]["sources_entries"]] == ["pull-up"], rows["C12345"]
        assert rows["C1234"]["sources_entries"] == [], "C1234 was joined by a prefix or by an alternative the entry did not fit"
        c555 = rows["C555"]["sources_entries"]
        assert [e["id"] for e in c555] == ["clamps"], "a code named in prose joined an entry: %s" % c555
        assert [d["path"] for d in c555[0]["documents"]] == ["v2/vendor/s1.pdf"], "another code's document was listed: %s" % c555
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_the_contracts_listed_are_those_that_name_the_board():
    d, *_, out, m = _packet()
    try:
        c = json.load(open(os.path.join(out, "contracts", "contracts.json")))
        got = {x["text"]: x["result"] for x in c["this_board"]}
        assert got == {"x alone": "PASS", "x and y disagree": "FAIL"}, got
        assert c["all_boards_count"] == 3, c
        assert not os.path.exists(os.path.join(out, "checker-ran.flag")), "the checker's output reached the packet"
    finally:
        shutil.rmtree(d, ignore_errors=True)
    d, *_, out, m = _packet(with_checker=False)
    try:
        c = json.load(open(os.path.join(out, "contracts", "contracts.json")))
        assert c["status"] == "NOT_RUN" and c["this_board"] == [], c
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------------------------------------- the three shapes
# The review cycle of 26 September 2026 found a neighbour's IDs credited to a change in each of these, checked against
# the real generators at 1f614233 (gen_sch_p.py D1 under `if _tvs:` below a try, whose comment sits above the try;
# gen_sch_e.py D2 below L2; gen_sch_c.py C31 in the hunk of the rectifier fix). Each fixture failed before the fix.
SHAPES_V1 = """#!/usr/bin/env python3
r("R1", "1k", "A", "B")
r("R2", "1k", "B", "C")
part("U1", "Device", "X", "buffer", "SOT", {"1": "A", "2": "B"})
"""
SHAPES_V2 = """#!/usr/bin/env python3
# F-AA-01: R1 IS RAISED TO 2k
r("R1", "2k", "A", "B")
# F-BB-02: R2 IS LOWERED TO 470R
r("R2", "470R", "B", "C")
r("R3", "10k", "C", "GND")
# W6-F5: THE BUFFER U1 IS A SCHMITT PART
part("U1", "Device", "X", "buffer, Schmitt", "SOT", {"1": "A", "2": "B"})
part("R7", "Device", "R", "1k", "R0603", {"1": "B", "2": "C"})
# O-12: THE TERMINAL CAPACITORS ARE IN SERIES
c("C11", "100n", "P", "MID"); c("C12", "100n", "MID", "N")
# S-09 / A03: D1 WAS REVERSED; its cathode is on P now
try:
    from kisch import tvs as _tvs
except ImportError:
    _tvs = None
if _tvs:
    _tvs("D1", "clamp", "P", "N")
else:
    part("D1", "Device", "D_Zener", "clamp", "SMB", {"1": "P", "2": "N"})
"""


def _shapes(hand=None):
    if shutil.which("git") is None: raise Skip("no git on this host")
    d = tempfile.mkdtemp(prefix="rp-shapes-")
    r = os.path.join(d, "repo"); os.makedirs(r)
    _git(r, "init", "-q")
    base = {
        ".gitignore": "out/\n*.kicad_prl\n",
        "v2/ecad/tools/routeflow/x.json": json.dumps({"board": "pcb-x-test", "project": "v2/ecad/pcb-x-test"}),
        "v2/ecad/tools/boards/x.json": json.dumps({"name": "pcb-x-test", "phase": "X3"}),
        "v2/ecad/tools/pcb_rules.yaml": "rules:\n  - {id: TST-001}\n",
        "v2/ecad/pcb-x-test/pcb-x-test.kicad_sch": '(kicad_sch (title_block (comment 1 "Phase X3 schematic")))\n',
    }
    for k, v in base.items(): _write(r, k, v)
    _write(r, "v2/ecad/tools/gen_sch_x.py", SHAPES_V1)
    _write(r, "v2/ecad/pcb-x-test/out/pcb-x-test.net", _net(
        {"R1": ("1k", "R", ""), "R2": ("1k", "R", ""), "U1": ("buffer", "SOT", ""), "C11": ("100n", "C", ""),
         "C12": ("100n", "C", ""), "D1": ("clamp", "SMB", "")},
        {"A": [("R1", "1"), ("U1", "1")], "B": [("R1", "2"), ("R2", "1"), ("U1", "2")], "C": [("R2", "2")],
         "P": [("C11", "1"), ("C12", "1"), ("D1", "2")], "N": [("C11", "2"), ("C12", "2"), ("D1", "1")]}))
    _git(r, "add", "-A"); _git(r, "add", "-f", "v2/ecad/pcb-x-test/out/pcb-x-test.net")   # the tree commits its netlists past out/
    _git(r, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "v1")
    v1 = _git(r, "rev-parse", "HEAD")
    _write(r, "v2/ecad/tools/gen_sch_x.py", SHAPES_V2)
    _write(r, "v2/ecad/pcb-x-test/out/pcb-x-test.net", _net(
        {"R1": ("2k", "R", ""), "R2": ("470R", "R", ""), "R3": ("10k", "R", ""), "U1": ("buffer, Schmitt", "SOT", ""),
         "R7": ("1k", "R", ""), "C11": ("100n", "C", ""), "C12": ("100n", "C", ""), "D1": ("clamp", "SMB", "")},
        {"A": [("R1", "1"), ("U1", "1")], "B": [("R1", "2"), ("R2", "1"), ("U1", "2"), ("R7", "1")],
         "C": [("R2", "2"), ("R3", "1"), ("R7", "2")], "GND": [("R3", "2")],
         "P": [("C11", "1"), ("D1", "1")], "MID": [("C11", "2"), ("C12", "1")], "N": [("C12", "2"), ("D1", "2")]}))
    _git(r, "add", "-A"); _git(r, "add", "-f", "v2/ecad/pcb-x-test/out/pcb-x-test.net")
    _git(r, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "v2")
    v2 = _git(r, "rev-parse", "HEAD")
    st = os.path.join(d, "stage"); out = os.path.join(d, "packet")
    RP.stage(r, v2, v1, st)
    hp = None
    if hand is not None:
        hp = os.path.join(d, "hand.yaml")
        open(hp, "w").write(json.dumps(dict({"board": "x", "rev": v2[:12], "prev": v1[:12], "read_by": "fixture"}, **hand)))
    return d, st, out, hp


def t_a_statement_under_if_or_try_is_never_credited_with_a_neighbours_id():
    d, st, out, _ = _shapes()
    try:
        m = RP.build(st, "x", out, None, (), True)
        ch = _changes(out)
        d1 = ch["D1"]
        assert d1["status"] == "UNVERIFIED_ATTRIBUTION" and d1["finding_ids"] == [], d1
        assert "O-12" not in d1["finding_ids"] + d1["authority_ids"], "the capacitors' finding was credited to the clamp"
        near = [cd for cd in d1["evidence"]["candidates"] if cd["kind"] in ("nearby", "enclosing")]
        assert near and all("O-12" not in RP._flat(cd["ids"]) for cd in near), near
        assert any("S-09" in RP._flat(cd["ids"]) for cd in near), "the block above the try was not offered: %s" % near
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_statement_below_another_commented_statement_takes_none_of_its_ids():
    d, st, out, _ = _shapes()
    try:
        RP.build(st, "x", out, None, (), True)
        ch = _changes(out)
        assert ch["U1"]["finding_ids"] == ["W6-F5"] and ch["U1"]["read"] == "direct", ch["U1"]
        assert ch["R7"]["finding_ids"] == [] and ch["R7"]["status"] == "UNVERIFIED_ATTRIBUTION", ch["R7"]
        assert "W6-F5" in ch["R7"]["evidence"]["automatic"]["candidate_ids"], ch["R7"]["evidence"]
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_hunk_holding_two_findings_credits_each_statement_only_its_own():
    d, st, out, _ = _shapes()
    try:
        m = RP.build(st, "x", out, None, (), True)
        ch = _changes(out)
        assert ch["R1"]["finding_ids"] == ["F-AA-01"], ch["R1"]
        assert ch["R2"]["finding_ids"] == ["F-BB-02"], ch["R2"]
        assert ch["R3"]["finding_ids"] == [] and ch["R3"]["status"] == "UNVERIFIED_ATTRIBUTION", ch["R3"]
        assert {"F-AA-01", "F-BB-02"} <= set(ch["R3"]["evidence"]["automatic"]["candidate_ids"]), ch["R3"]["evidence"]
        k = m["counts"]
        assert k["changes"] == 8 and k["with_finding_id"] == 5 and k["unverified_attribution"] == 3 and k["without_finding_id"] == 3, k
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_hand_reading_is_checked_line_by_line_and_a_refusal_leaves_no_packet():
    lines = SHAPES_V2.splitlines()
    s09 = lines.index("# S-09 / A03: D1 WAS REVERSED; its cathode is on P now") + 1
    f02 = lines.index("# F-BB-02: R2 IS LOWERED TO 470R") + 1
    good = {"rows": {"D1": {"ids": ["S-09", "A03"], "cite": [[s09, s09]], "why": "the clamp is reversed"},
                     "R3": {"ids": [], "cite": [[f02 + 2, f02 + 2]], "why": "a new pull-down; its statement carries no ID"}}}
    d, st, out, hp = _shapes(good)
    try:
        m = RP.build(st, "x", out, None, (), True, hp)
        ch = _changes(out)
        assert ch["D1"]["status"] == "TRACED" and ch["D1"]["read"] == "hand" and ch["D1"]["finding_ids"] == ["A03", "S-09"], ch["D1"]
        assert ch["D1"]["evidence"]["automatic"]["agrees"] is False, "the disagreement with the mechanical reading was lost"
        assert "names_ref" in ch["D1"]["evidence"]["hand"]["ties"][0]["tie"], ch["D1"]["evidence"]["hand"]
        assert ch["R3"]["status"] == "NO_ID_OF_ANY_KIND" and ch["R3"]["read"] == "hand", ch["R3"]
        assert os.path.isfile(os.path.join(out, "changes", "attribution-read-by-hand.yaml"))
        assert m["counts"]["read_by_hand"] == 2, m["counts"]
        assert m["change_attribution"] == "READ_BY_HAND", m["change_attribution"]
        assert "MECHANICAL ONLY" not in open(os.path.join(out, "README.md")).read()
        assert RP.verify(out) == [], RP.verify(out)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    for bad, why in (({"D1": {"ids": ["O-12"], "cite": [[s09, s09]], "why": "x"}}, "an ID not on its cited lines"),
                     ({"D1": {"ids": ["F-BB-02"], "cite": [[f02, f02]], "why": "x"}}, "a cite tied to another statement"),
                     ({"Q9": {"ids": [], "cite": [[1, 1]], "why": "x"}}, "a reference that did not change"),
                     ({"D1": {"ids": ["S-09"], "cite": [[s09, s09]]}}, "a row with no reason")):
        d, st, out, hp = _shapes({"rows": bad})
        try:
            try:
                RP.build(st, "x", out, None, (), True, hp)
            except RuntimeError:
                pass
            else:
                raise AssertionError("the build accepted %s" % why)
            assert not os.path.exists(out), "a refused build left a partial packet behind (%s)" % why
        finally:
            shutil.rmtree(d, ignore_errors=True)


def t_no_packet_file_is_one_the_repository_would_not_commit():
    d, st, out, _ = _shapes()
    try:
        m = RP.build(st, "x", out, None, (), True)
        assert m["gitignore_check"]["ignored"] == [], m["gitignore_check"]
        assert any(r.startswith("native/netlist/") for r in m["artefacts"]), sorted(m["artefacts"])
        # the real tree's own .gitignore, read by git: the same packet placed under release/review-packets/
        root = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
        gi = os.path.join(root, ".gitignore")
        if not os.path.isfile(gi): raise Skip("no .gitignore at the tree root")
        rels = ["v2/release/review-packets/X-X3-00000000/" + r for r in list(m["artefacts"]) + ["MANIFEST.json", "SHA256SUMS"]]
        assert RP.ignored_paths(gi, rels) == [], RP.ignored_paths(gi, rels)
        # and the check bites: a .gitignore that drops the netlist folder makes the packet incomplete
        assert RP.ignored_paths(gi, ["v2/release/review-packets/X/native/out/x.net"]), "the tree stopped ignoring out/; this fixture needs a new witness"
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------------------------------------- lines with no code
CODELESS_V1 = """#!/usr/bin/env python3
part("U1", "Device", "X", "buffer", "SOT", {"1": "A", "2": "B"}, "C1234")
"""
CODELESS_V2 = """#!/usr/bin/env python3
part("U1", "Device", "X", "buffer", "SOT", {"1": "A", "2": "B"}, "C1234")
part("L2", "Device", "L", "Bourns SRF1260-1R5Y choke, common-mode connection", "CMC", {"1": "A", "2": "B"})
part("J_S", "Connector", "C", "SMBus lead to board Y (JST-XH 1x4): SMBC SMBD GND PRES", "XH4", {"1": "A"})
part("Q9", "Device", "Q", "2N7002 fan switch", "SOT23", {"1": "B"})
part("D7", "Device", "D", "SS2040FL rectifier", "SOD123F", {"1": "B"}); part("C9", "Device", "C", "1u", "C0603", {"1": "B"})
"""


def _codeless():
    if shutil.which("git") is None: raise Skip("no git on this host")
    d = tempfile.mkdtemp(prefix="rp-codeless-")
    r = os.path.join(d, "repo"); os.makedirs(r)
    _git(r, "init", "-q")
    for k, v in {"v2/ecad/tools/routeflow/x.json": json.dumps({"board": "pcb-x-test", "project": "v2/ecad/pcb-x-test"}),
                 "v2/ecad/tools/boards/x.json": json.dumps({"name": "pcb-x-test", "phase": "X3"}),
                 "v2/ecad/tools/pcb_rules.yaml": "rules:\n  - {id: TST-001}\n",
                 "v2/ecad/pcb-x-test/pcb-x-test.kicad_sch": '(kicad_sch (title_block (comment 1 "Phase X3 schematic")))\n'}.items():
        _write(r, k, v)
    _write(r, "v2/ecad/tools/gen_sch_x.py", CODELESS_V1)
    _write(r, "v2/ecad/pcb-x-test/out/pcb-x-test.net", _net({"U1": ("buffer", "SOT", "C1234")}, {"A": [("U1", "1")], "B": [("U1", "2")]}))
    _git(r, "add", "-A"); _git(r, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "v1")
    v1 = _git(r, "rev-parse", "HEAD")
    _write(r, "v2/ecad/tools/gen_sch_x.py", CODELESS_V2)
    _write(r, "v2/ecad/pcb-x-test/out/pcb-x-test.net", _net(
        {"U1": ("buffer", "SOT", "C1234"), "L2": ("Bourns SRF1260-1R5Y choke, common-mode connection", "CMC", ""),
         "J_S": ("SMBus lead to board Y (JST-XH 1x4): SMBC SMBD GND PRES", "XH4", ""), "Q9": ("2N7002 fan switch", "SOT23", ""),
         "D7": ("SS2040FL rectifier", "SOD123F", ""), "C9": ("1u", "C0603", "")},
        {"A": [("U1", "1"), ("L2", "1"), ("J_S", "1")], "B": [("U1", "2"), ("L2", "2"), ("Q9", "1"), ("D7", "1"), ("C9", "1")]}))
    _git(r, "add", "-A"); _git(r, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "v2")
    v2 = _git(r, "rev-parse", "HEAD")
    # the SOURCES file names the revision its line numbers were read at, so it is supplied beside the stage (--sources)
    here = v2[:8]
    src = {"tree": v1[:8], "parts": [
        {"id": "choke", "boards": ["X"], "on_main": True, "lcsc": None, "fitted_mpn": "SRF1260-1R5Y", "identity": "MATCH",
         "schematic_name": {"text": "Bourns SRF1260-1R5Y choke", "where": "v2/ecad/tools/gen_sch_x.py:3"}, "where_rev": here,
         "documents": [{"path": "v2/vendor/srf.pdf", "revision": "03/18", "sha256": "aa"}]},
        {"id": "leads", "boards": ["X", "Y"], "on_main": True, "lcsc": "C594232 (Y J_S)", "fitted_mpn": "B4B-XH-A (Y J_S)",
         "identity": "MATCH", "where_rev": here,
         "schematic_name": {"text": "JST-XH 1x4 (B4B-XH-A)", "where": "v2/ecad/tools/gen_sch_y.py:9 (J_S); gen_sch_x.py:2 (U1), :4 (J_S)"}},
        {"id": "stale", "boards": ["X"], "identity": "NOT_PINNED",
         "schematic_name": {"text": "2N7002", "where": "v2/ecad/tools/gen_sch_x.py:5"}},
        {"id": "other-board", "boards": ["Y"], "fitted_mpn": "2N7002", "identity": "MATCH"},
        {"id": "candidate", "boards": ["X"], "on_main": False, "fitted_mpn": "2N7002", "identity": "MATCH"},
        {"id": "moved", "boards": ["X", "Y"], "fitted_mpn": "2N7002", "identity": "MATCH", "update_1": {"boards": ["Y"]}},
        {"id": "rect", "boards": ["X"], "lcsc": "C268712", "identity": "MATCH", "where_rev": here,
         "schematic_name": {"text": "SS2040FL", "where": "v2/ecad/tools/gen_sch_x.py:6"}},
        {"id": "wrong-code", "boards": ["X"], "lcsc": "C9999", "identity": "MATCH", "where_rev": here,
         "schematic_name": {"text": "buffer", "where": "v2/ecad/tools/gen_sch_x.py:2 (U1)"}}]}
    sp = os.path.join(d, "SOURCES.yaml")
    open(sp, "w").write(json.dumps(src))
    st = os.path.join(d, "stage"); out = os.path.join(d, "packet")
    RP.stage(r, v2, v1, st)
    return d, st, out, sp


def t_where_text_is_read_per_generator_and_never_from_another_file():
    got = RP.where_items("v2/ecad/tools/gen_sch_e.py:218 (J_SMB), :540 (J_TAMP); gen_sch_p.py:159 (J_CELL), :481-482; "
                         "the helper kisch.py:345; read 12:22Z")
    assert got == [("e", 218, 218), ("e", 540, 540), ("p", 159, 159), ("p", 481, 482)], got


def t_a_line_without_a_code_joins_only_the_entry_that_covers_it():
    d, st, out, sp = _codeless()
    try:
        m = RP.build(st, "x", out, sp, (), True)
        rows = {" ".join(r["refs"]): r for r in json.load(open(os.path.join(out, "bom", "parts-identity.json")))}
        ids = lambda k: [e["id"] for e in rows[k]["sources_entries"]]
        assert ids("L2") == ["choke"] and rows["L2"]["order_code_on_line"] is False, rows["L2"]
        assert rows["L2"]["sources_entries"][0]["joined_by"].startswith("where gen_sch_x.py:3"), rows["L2"]
        assert [x["path"] for x in rows["L2"]["sources_entries"][0]["documents"]] == ["v2/vendor/srf.pdf"], rows["L2"]
        assert ids("J_S") == ["leads"] and "names J_S" in rows["J_S"]["sources_entries"][0]["joined_by"], rows["J_S"]
        assert ids("Q9") == [], "a stale where, another board, a candidate or a moved entry joined Q9: %s" % rows["Q9"]
        assert ids("D7") == ["rect"], rows["D7"]
        assert ids("C9") == [], "a statement sharing the generator line with the entry's part was joined: %s" % rows["C9"]
        assert ids("U1") == [], "a coded line was joined by a where: %s" % rows["U1"]
        cov = json.load(open(os.path.join(out, "bom", "sources-coverage.json")))
        assert [u["id"] for u in cov["entries_naming_this_board_that_joined_no_line"]] == ["stale", "wrong-code"], cov
        assert m["counts"]["bom_lines_joined_without_code"] == 3 and m["counts"]["bom_lines_joined_by_code"] == 0, m["counts"]
        readme = open(os.path.join(out, "README.md")).read()
        assert "Lines with no LCSC code, joined to the entry that covers them" in readme, readme
        assert "`stale`" in readme and "`wrong-code`" in readme, "the unjoined entries are not listed on the front page"
        assert "not judged critical there, or their entry is owed" not in readme
        assert RP.verify(out) == [], RP.verify(out)
    finally:
        shutil.rmtree(d, ignore_errors=True)
