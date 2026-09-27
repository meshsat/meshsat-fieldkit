"""The requirements registry refuses what it exists to refuse, and its trace page is generated
(MESHSAT-1357, foundation baseline, 26 September 2026).

`pcb_requirements.yaml` is where the kit's needs become requirements with a pass line, a verification method and
phase, the rules and decisions that settle them, and prototype 1's staged scope (owner ruling D-01). Each check of
`rules_lib.validate_requirements` is shown here twice: a defective fixture that must FAIL and the acceptable fixture
it was cut from, which must PASS. A validator that stops refusing reads green on the real registry for ever, so the
refusals are the part worth testing. The real registry must validate, and `v2/docs/REQUIREMENTS-TRACE.md` must be
exactly what the registry renders.

Every fixture is built in memory or in a temporary directory, and nothing here writes into the tree: the rule that
damages the trace page to prove `--check` refuses a hand edit damages a copy (`--page`), as 2ba560ec and 82dd1e4d
moved the other fixtures off the tree's own files.
"""
import contextlib, copy, hashlib, io, os, shutil, subprocess, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import rules_lib as R
import rules_render as RR
import claims_check as CC
from harness import need, Skip

PAGE = os.path.join(RR.DOCS, RR.REQ_TRACE)
NEEDS_TABLE = ("| ID | Need | Source |\n|---|---|---|\n"
               "| NEED-01 | Relay messages between local networks and remote correspondents. | brief |\n"
               "| NEED-02 | Keep at least one long-range path when any single bearer is unavailable. | spec |\n")
CONOPS_ROWS = "# CONOPS\n\n## 2. Needs\n\n" + NEEDS_TABLE + "\n## 3. Missions\n\nText.\n"


def _doc(text):
    d = tempfile.mkdtemp(prefix="req-conops-")
    p = os.path.join(d, "CONOPS.md")
    open(p, "w", encoding="utf-8").write(text)
    return p


def _fixture(conops=CONOPS_ROWS):
    """(registry, keyword arguments) for a small registry that validates. Every defective fixture below is this
    one with ONE thing wrong, so an error can only come from the thing the rule is about."""
    doc = _doc(conops)
    req = {
        "schema_version": 1, "sources_read_at": "d468613e", "needs_document": "v2/docs/CONOPS.md",
        "needs_document_sha256": hashlib.sha256(conops.encode()).hexdigest(),
        "needs": [{"id": "NEED-01", "statement": "Relay messages between local networks and remote correspondents."},
                  {"id": "NEED-02", "statement": "Keep at least one long-range path when any single bearer is unavailable."}],
        "owner_rulings": [
            {"id": "D-01", "authority": "OWNER", "ruled_on": "2026-09-25", "title": "scope",
             "ruling": "Staged acceptance on a named core.", "core_needs": ["NEED-01"]},
            {"id": "D-03", "authority": "OWNER", "ruled_on": "2026-09-26", "title": "ZEROIZE", "decision": 30,
             "ruling": "Crypto-erase through the secure element."},
            {"id": "standing-rule", "authority": "OWNER", "ruled_on": "2026-09-26", "title": "not asked again",
             "ruling": "The session takes the recommended option and records it as its own."}],
        "session_choices": [
            {"id": "SC-01", "authority": "SESSION", "under": "standing-rule", "taken_on": "2026-09-26",
             "question": "Does the alert join the core?", "taken": "Yes.",
             "why": "The ruling that defines the alert makes it firmware only, and the table recommended it.",
             "closes": ["D-01-R2"]}],
        "open_items": [{"id": "D-05", "class": "OWNER", "status": "OPEN", "title": "EMCON meaning"},
                       {"id": "S-01", "class": "SESSION", "status": "OPEN", "title": "EMCON gates"}],
        "closed_items": [{"id": "D-01-R2", "closed_by": "SC-01", "title": "Does the alert join the core?"}],
        "records": [
            {"id": "REQ-001", "kind": "requirement", "parent": "NEED-01",
             "statement": "A LoRa mesh packet reaches a remote correspondent.",
             "acceptance": "In the functional check a mesh packet passes; the bridge forwards it within 10 s.",
             "allocated_to": ["b", "sw"], "verification_method": ["SCRIPT", "PROTOTYPE_MEASUREMENT"],
             "verification_phase": "SCHEMATIC", "final_phase": "PROTOTYPE", "prototype_1": "core",
             "prototype_1_basis": "NEED_DEFAULT", "satisfied_by": {"rules": ["RF-002"], "decisions": [30]},
             "rule_coverage": "PARTIAL", "rulings": ["D-03"], "status": "DEFINED", "evidence_result": "NOT_JUDGED",
             "release_effect": "BLOCKER", "source": ["v2/docs/PANEL.md:130", "owner ruling D-03"],
             "source_check": "VERIFIED"},
            {"id": "REQ-002", "kind": "requirement", "parent": "NEED-02",
             "statement": "Each bearer has an end-to-end latency target.",
             "acceptance": "Latency per bearer TBD.", "tbd_effect": "The bridge's software acceptance cannot be written.",
             "allocated_to": ["sw"], "verification_method": ["PROTOTYPE_MEASUREMENT"], "verification_phase": "PROTOTYPE",
             "prototype_1": "deferred", "prototype_1_basis": "NEED_DEFAULT",
             "satisfied_by": {"rules": [], "decisions": []}, "rule_coverage": "NONE", "waits_on": ["D-05"],
             "status": "TBD", "evidence_result": "NOT_YET_TESTED", "release_effect": "ADVISORY",
             "source": ["v2/docs/PANEL.md:130"], "source_check": "VERIFIED"},
            {"id": "CFL-001", "kind": "conflict", "parent": "NEED-01",
             "statement": "Two documents map the failover differently.", "acceptance": "One mapping in every document.",
             "allocated_to": ["b"], "verification_method": ["MANUAL_REVIEW"], "verification_phase": "SCHEMATIC",
             "prototype_1": "core", "prototype_1_basis": "NEED_DEFAULT", "satisfied_by": {"rules": [], "decisions": []},
             "rule_coverage": "NONE", "waits_on": ["S-01"], "status": "CONFLICT_OPEN", "evidence_result": "FAIL",
             "evidence_phase": "SCHEMATIC", "release_effect": "BLOCKER", "source": ["v2/docs/PANEL.md:130"],
             "source_check": "VERIFIED"},
            {"id": "SPD-001", "kind": "superseded", "parent": "NEED-02", "statement": "A 65 W outlet.",
             "acceptance": "n/a", "allocated_to": ["a"], "verification_method": ["MANUAL_REVIEW"],
             "verification_phase": "SCHEMATIC", "satisfied_by": {"rules": [], "decisions": []},
             "status": "SUPERSEDED", "superseded_by": "a 45 W outlet", "evidence_result": "NOT_APPLICABLE",
             "release_effect": "NONE", "source": ["v2/docs/PANEL.md:130"], "source_check": "VERIFIED"},
        ]}
    kw = {"rules": [r["id"] for r in R.load()["rules"]],
          "decisions": {30: {"n": 30, "status": "open"}, 34: {"n": 34, "status": "ruled", "authority": "SESSION",
                                                                "ruled_on": "2026-09-21"}},
          "interfaces": {"SMBUS_GAUGE"}, "needs_doc": doc, "root": R.REPO_ROOT}
    return req, kw


def _rec(req, rid):
    return next(r for r in req["records"] if r["id"] == rid)


def _bind(rel):
    """path@sha256/16 of a tracked file as this tree holds it, the form `evidence_bound_to` takes."""
    return "%s@%s" % (rel, hashlib.sha256(open(os.path.join(R.REPO_ROOT, rel), "rb").read()).hexdigest()[:16])


def _passing(req, rid="REQ-001", cls="DESK_REVIEW"):
    """Make `rid` a PASS read at desk on PANEL.md, bound to it by content: the acceptable reading the class rules
    below each break in one way."""
    r = _rec(req, rid)
    r.update({"evidence_result": "PASS", "evidence_phase": "SCHEMATIC", "evidence_class": cls,
              "evidence": ["v2/docs/PANEL.md section 6 read for this test"], "evidence_bound_to": [_bind("v2/docs/PANEL.md")]})
    return r


def _head_commit():
    import subprocess
    r = subprocess.run(["git", "-C", R.REPO_ROOT, "rev-parse", "HEAD"], capture_output=True, text=True)
    if r.returncode != 0: raise Skip("git cannot name this tree's HEAD")
    return r.stdout.strip()


def _errors(req, kw):
    need(os.path.join(R.REPO_ROOT, "v2", "docs", "PANEL.md"), "the fixtures cite a tracked document")
    return R.validate_requirements(req, **kw)[0]


def _refused(req, kw, words):
    errs = _errors(req, kw)
    assert any(all(w in e for w in words) for e in errs), \
        "the defective fixture was not refused for %r; errors were: %s" % (words, errs[:6])


# ------------------------------------------------------------------------------------------ the acceptable fixture
def t_the_acceptable_fixture_passes():
    req, kw = _fixture()
    errs = _errors(req, kw)
    assert not errs, "the acceptable fixture was refused: %s" % errs


# ------------------------------------------------------------------------------------------ the needs table
def t_only_the_needs_table_is_read_as_needs():
    """The round-3 defect: a scope table in section 2a whose first column is NEED-nn was read as need statements,
    and a later row overwrote an earlier one. Only the table under '| ID | Need | Source |' is read."""
    scope = ("\n### 2a. What prototype 1 is accepted against\n\n| Need | Scope | Note |\n|---|---|---|\n"
             "| NEED-01 | core | the four bearers |\n| NEED-02 | core, for the secure element | x |\n")
    text = CONOPS_ROWS.replace("\n## 3. Missions", scope + "\n## 3. Missions")
    got = R.conops_needs(_doc(text))
    assert got == {"NEED-01": "Relay messages between local networks and remote correspondents.",
                   "NEED-02": "Keep at least one long-range path when any single bearer is unavailable."}, got
    req, kw = _fixture(text)
    assert not _errors(req, kw), "a NEED-keyed table outside the needs table broke the registry: %s" % _errors(req, kw)


def t_a_repeated_need_in_the_needs_table_is_refused():
    text = CONOPS_ROWS.replace("| NEED-02 | Keep", "| NEED-01 | Keep")
    try:
        R.conops_needs(_doc(text))
    except R.NeedsTableError as e:
        assert "repeats NEED-01" in str(e), e
    else:
        raise AssertionError("a repeated NEED id in the needs table was read, the later row winning")
    req, kw = _fixture(text)
    _refused(req, kw, ("cannot be read", "repeats NEED-01"))


def t_a_needs_table_that_cannot_be_read_as_one_table_is_refused():
    for text, words in ((CONOPS_ROWS.replace("| ID | Need | Source |", "| Id | What | From |"), "no needs table"),
                        (CONOPS_ROWS + "\n## 9. Again\n\n" + NEEDS_TABLE, "2 needs tables"),
                        (CONOPS_ROWS.replace("| NEED-02 | Keep", "| NEED-2 | Keep"), "not '| NEED-nn | need | source |'")):
        try:
            R.conops_needs(_doc(text))
        except R.NeedsTableError as e:
            assert words in str(e), (words, str(e))
        else:
            raise AssertionError("a needs table that is not one table of distinct needs was read (%s)" % words)


def t_the_needs_table_ends_at_the_next_section():
    """A NEED row after the table has ended, or in the next section, is not a need."""
    text = CONOPS_ROWS.replace("Text.", "| NEED-03 | Not a need, a mission row. | x |")
    assert set(R.conops_needs(_doc(text))) == {"NEED-01", "NEED-02"}


# ------------------------------------------------------------------------------------------ unknown references
def t_an_unknown_rule_id_fails():
    req, kw = _fixture(); _rec(req, "REQ-001")["satisfied_by"]["rules"] = ["RF-002", "XYZ-999"]
    _refused(req, kw, ("REQ-001", "XYZ-999", "pcb_rules.yaml does not hold"))


def t_an_unknown_decision_fails():
    req, kw = _fixture(); _rec(req, "REQ-001")["satisfied_by"]["decisions"] = [999]
    _refused(req, kw, ("REQ-001", "decision 999"))


def t_an_unknown_need_fails():
    req, kw = _fixture(); _rec(req, "REQ-001")["parent"] = "NEED-99"
    _refused(req, kw, ("REQ-001", "NEED-99", "is not a need"))


def t_an_open_item_nobody_declared_fails():
    req, kw = _fixture(); _rec(req, "REQ-002")["waits_on"] = ["D-99"]
    _refused(req, kw, ("REQ-002", "D-99", "not an open item"))


def t_waiting_on_a_ruled_question_fails():
    req, kw = _fixture(); _rec(req, "REQ-002")["waits_on"] = ["D-03"]
    _refused(req, kw, ("REQ-002", "D-03", "is ruled"))


def t_waiting_on_a_closed_item_fails():
    req, kw = _fixture(); _rec(req, "REQ-002")["waits_on"] = ["D-01-R2"]
    _refused(req, kw, ("REQ-002", "D-01-R2", "SC-01 closed"))


def t_waiting_on_a_decision_an_owner_ruling_names_fails():
    req, kw = _fixture(); _rec(req, "REQ-002")["waits_on"] = ["decision-30"]
    _refused(req, kw, ("REQ-002", "decision-30", "owner ruling here has ruled"))


def t_an_unknown_interface_or_element_fails():
    req, kw = _fixture(); _rec(req, "REQ-001")["allocated_to"] = ["b", "board-z"]
    _refused(req, kw, ("REQ-001", "board-z"))
    req, kw = _fixture(); _rec(req, "REQ-001")["allocated_to"] = ["b", "SMBUS_GAUGE"]
    assert not _errors(req, kw), "an interface of pcb_interfaces.yaml was refused as an allocation"


# ------------------------------------------------------------------------------------------ vocabularies
def t_a_bad_vocabulary_fails():
    cases = (("kind", "wish", ("kind 'wish'",)), ("verification_method", ["SCRIPT", "GUESS"], ("GUESS",)),
             ("verification_phase", "SOMETIME", ("SOMETIME",)), ("prototype_1", "maybe", ("maybe",)),
             ("evidence_result", "LOOKS_FINE", ("LOOKS_FINE",)), ("release_effect", "SEVERE", ("SEVERE",)),
             ("status", "DONE", ("DONE",)), ("source_check", "TRUSTED", ("TRUSTED",)),
             ("prototype_1_basis", "READING", ("READING",)))
    for field, bad, words in cases:
        req, kw = _fixture(); _rec(req, "REQ-001")[field] = bad
        _refused(req, kw, ("REQ-001",) + words)


def t_an_id_that_does_not_match_its_kind_fails():
    req, kw = _fixture(); _rec(req, "REQ-001")["kind"] = "constraint"
    _refused(req, kw, ("REQ-001", "numbered CON-nnn"))


# ------------------------------------------------------------------------------------------ TBD and numbers
def t_a_tbd_without_its_effect_fails():
    req, kw = _fixture(); _rec(req, "REQ-002").pop("tbd_effect")
    _refused(req, kw, ("REQ-002", "a TBD with no effect"))


def t_a_tbd_that_the_status_does_not_admit_fails():
    req, kw = _fixture(); _rec(req, "REQ-002")["status"] = "DEFINED"
    _refused(req, kw, ("REQ-002", "carries a TBD and its status is DEFINED"))


def t_a_hedged_number_in_a_blockers_pass_line_fails_and_the_provisional_field_does_not():
    """The defect this registry was built to stop: a PROVISIONAL figure standing as a release gate (W1's original
    runtime and peak-power pass lines read exactly like this)."""
    req, kw = _fixture()
    _rec(req, "REQ-001")["acceptance"] = "PS-ALLTX, about 227 W at the battery, is supplied with every rail in regulation."
    _refused(req, kw, ("REQ-001", "hedged number", "227 W"))
    req, kw = _fixture(); r = _rec(req, "REQ-001")
    r["acceptance"] = "PS-ALLTX is supplied with every rail in regulation for a key-down duration TBD."
    r["tbd_effect"] = "The pack thresholds and the load-shed rule cannot be set."; r["status"] = "TBD"
    r["provisional"] = "PS-ALLTX is about 227 W at the battery (PROVISIONAL)."
    assert not _errors(req, kw), "a provisional figure kept out of the pass line was refused: %s" % _errors(req, kw)


def t_an_inferred_number_in_a_blockers_pass_line_fails():
    req, kw = _fixture(); r = _rec(req, "REQ-001"); r["source_check"] = "INFERRED"
    _refused(req, kw, ("REQ-001", "INFERRED", "10 s"))
    req, kw = _fixture(); r = _rec(req, "REQ-001"); r["source_check"] = "INFERRED"; r["release_effect"] = "MUST_JUSTIFY"
    r["prototype_1"] = "deferred"; r["prototype_1_basis"] = "SESSION"; r["prototype_1_choice"] = "SC-01"
    r["prototype_1_why"] = "the session takes it so, for a test"
    assert not _errors(req, kw), "an inferred number outside a release gate was refused: %s" % _errors(req, kw)


# ------------------------------------------------------------------------------------------ prototype 1 scope
def t_a_deferred_record_is_never_a_blocker():
    req, kw = _fixture(); _rec(req, "REQ-002")["release_effect"] = "BLOCKER"
    _refused(req, kw, ("REQ-002", "a deferred record is a BLOCKER"))


def t_a_scope_against_its_need_needs_a_reason():
    req, kw = _fixture(); _rec(req, "REQ-002")["prototype_1"] = "core"
    _refused(req, kw, ("REQ-002", "NEED_DEFAULT", "default is deferred"))
    req, kw = _fixture(); r = _rec(req, "REQ-002"); r["prototype_1"] = "core"; r["prototype_1_basis"] = "SESSION"
    r["prototype_1_choice"] = "SC-01"
    _refused(req, kw, ("REQ-002", "no prototype_1_why"))


def t_a_scope_the_session_took_names_its_choice():
    """Under the owner's standing rule of 26 September 2026 the session takes a scope and records it as its own; a
    scope that names no session choice reads as nobody's, and a choice on a scope the need decides is noise."""
    req, kw = _fixture(); r = _rec(req, "REQ-002"); r["prototype_1_basis"] = "SESSION"
    r["prototype_1_why"] = "the session takes it so, for a test"
    _refused(req, kw, ("REQ-002", "prototype_1_choice", "names no session choice"))
    r["prototype_1_choice"] = "SC-01"
    assert not _errors(req, kw), "a scope naming its session choice was refused: %s" % _errors(req, kw)
    req, kw = _fixture(); _rec(req, "REQ-001")["prototype_1_choice"] = "SC-01"
    _refused(req, kw, ("REQ-001", "not the session's"))


def t_a_session_choice_is_the_sessions_and_taken_under_an_owner_ruling():
    req, kw = _fixture(); req["session_choices"][0]["authority"] = "OWNER"
    _refused(req, kw, ("SC-01", "is not SESSION"))
    req, kw = _fixture(); req["session_choices"][0]["under"] = "D-77"
    _refused(req, kw, ("SC-01", "D-77", "not an owner ruling"))
    req, kw = _fixture(); req["session_choices"][0]["why"] = ""
    _refused(req, kw, ("SC-01", "no why"))


def t_a_session_choice_can_add_a_core_need_and_the_default_follows():
    req, kw = _fixture(); req["session_choices"][0]["adds_core_needs"] = ["NEED-02"]
    assert R.core_needs(req) == ["NEED-01", "NEED-02"] and R.owner_core_needs(req) == ["NEED-01"]
    _refused(req, kw, ("REQ-002", "NEED_DEFAULT", "default is core"))
    req, kw = _fixture(); req["session_choices"][0]["adds_core_needs"] = ["NEED-42"]
    _refused(req, kw, ("SC-01", "NEED-42"))


def t_a_closed_item_names_what_closed_it():
    req, kw = _fixture(); req["closed_items"][0]["closed_by"] = "SC-99"
    _refused(req, kw, ("D-01-R2", "SC-99", "neither an owner ruling, a session choice nor a commit"))
    req, kw = _fixture(); req["closed_items"] = []
    _refused(req, kw, ("SC-01", "closes D-01-R2", "closed items do not say so"))
    req, kw = _fixture(); req["open_items"].append({"id": "D-01-R2", "class": "OWNER", "status": "OPEN", "title": "x"})
    _refused(req, kw, ("D-01-R2", "both open and closed"))


# ------------------------------------------------------------------------------------------ results and evidence
def t_a_result_without_its_evidence_fails():
    req, kw = _fixture(); r = _rec(req, "REQ-001"); r["evidence_result"] = "PASS"; r["evidence_phase"] = "SCHEMATIC"
    _refused(req, kw, ("REQ-001", "PASS with no evidence"))
    req, kw = _fixture(); r = _rec(req, "REQ-001"); r["evidence_result"] = "FAIL"; r["evidence_phase"] = "SCHEMATIC"
    r["evidence"] = ["somebody looked at it"]
    _refused(req, kw, ("REQ-001", "names no file"))
    req, kw = _fixture(); r = _rec(req, "REQ-001"); r["evidence_result"] = "FAIL"; r["evidence_phase"] = "SCHEMATIC"
    r["evidence"] = ["v2/docs/PANEL.md section 6: the pins reach only U6"]
    r["evidence_class"] = "DESK_REVIEW"; r["evidence_bound_to"] = [_bind("v2/docs/PANEL.md")]
    assert not _errors(req, kw), "a FAIL naming its file was refused: %s" % _errors(req, kw)


def t_hardware_results_wait_for_hardware():
    req, kw = _fixture(); _rec(req, "REQ-001")["evidence_result"] = "NOT_YET_TESTED"
    _refused(req, kw, ("REQ-001", "NOT_YET_TESTED is for a record that needs hardware"))


def t_an_open_conflict_reads_fail():
    req, kw = _fixture(); r = _rec(req, "CFL-001"); r["evidence_result"] = "NOT_JUDGED"; r.pop("evidence_phase")
    _refused(req, kw, ("CFL-001", "an open conflict reads FAIL"))


def t_a_source_that_is_not_in_the_tree_fails():
    req, kw = _fixture(); _rec(req, "REQ-001")["source"] = ["v2/docs/NO-SUCH-DOCUMENT.md:12"]
    _refused(req, kw, ("REQ-001", "does not exist in this tree"))
    req, kw = _fixture(); _rec(req, "REQ-001")["source"] = ["owner ruling D-77"]
    _refused(req, kw, ("REQ-001", "D-77"))
    req, kw = _fixture(); _rec(req, "REQ-001")["source"] = ["session choice SC-77"]
    _refused(req, kw, ("REQ-001", "SC-77"))


# ------------------------------------------------------------------------------------------ needs and rulings
def t_the_needs_must_be_the_published_ones():
    req, kw = _fixture(); req["needs"][1]["statement"] = "Keep a path."
    _refused(req, kw, ("NEED-02", "quoted differently"))
    req, kw = _fixture(); req["needs_document_sha256"] = "0" * 64
    _refused(req, kw, ("has changed since its needs were quoted",))
    req, kw = _fixture(); req["needs"] = req["needs"][:1]; _rec(req, "REQ-002")["parent"] = "NEED-01"
    _rec(req, "SPD-001")["parent"] = "NEED-01"; _rec(req, "REQ-002")["prototype_1"] = "core"
    _rec(req, "REQ-002")["release_effect"] = "BLOCKER"
    _refused(req, kw, ("NEED-02", "not quoted here"))


def t_an_absent_needs_document_is_a_warning_and_not_a_pass():
    req, kw = _fixture(); kw["needs_doc"] = os.path.join(tempfile.mkdtemp(), "absent.md")
    need(os.path.join(R.REPO_ROOT, "v2", "docs", "PANEL.md"), "the fixtures cite a tracked document")
    errs, warns = R.validate_requirements(req, **kw)
    assert not errs, errs
    assert any("not compared" in w for w in warns), "an absent CONOPS was not reported: %s" % warns


def t_an_owner_ruling_that_contradicts_the_decision_index_fails():
    req, kw = _fixture(); kw["decisions"][30] = {"n": 30, "status": "ruled", "authority": "SESSION", "ruled_on": "2026-09-21"}
    _refused(req, kw, ("D-03", "decision 30", "SESSION"))
    req, kw = _fixture()
    errs, warns = R.validate_requirements(req, **kw)
    assert any("still reads open" in w for w in warns), "an owner ruling the index has not recorded was not reported"
    req, kw = _fixture(); kw["decisions"][30] = {"n": 30, "status": "ruled", "authority": "OWNER", "ruled_on": "2026-09-26"}
    errs, warns = R.validate_requirements(req, **kw)
    assert not errs and not any("decision 30" in w for w in warns), (errs, warns)


def t_a_registry_with_no_scope_ruling_fails():
    req, kw = _fixture(); req["owner_rulings"][0].pop("core_needs")
    _refused(req, kw, ("no owner ruling names prototype 1's core",))


# ------------------------------------------------------------------------------------------ the real registry
def t_the_real_registry_validates():
    need(R.REQUIREMENTS, "no requirements registry in this tree")
    errs, warns = R.validate_requirements()
    assert not errs, "pcb_requirements.yaml does not validate (%d):\n  %s" % (len(errs), "\n  ".join(errs[:20]))


def t_the_real_needs_are_the_published_conops():
    """The pin, asserted on the real document. A worker tree holds the registry before CONOPS is published beside
    it; there this skips and says why, and the rule above has already reported the absence as a warning."""
    req = R.load_requirements()
    doc = need(os.path.join(R.REPO_ROOT, req["needs_document"]), "CONOPS is published with this registry (MESHSAT-1357)")
    have = hashlib.sha256(open(doc, "rb").read()).hexdigest()
    assert have == req["needs_document_sha256"], \
        "CONOPS changed since the needs were quoted (pinned %s, now %s)" % (req["needs_document_sha256"][:16], have[:16])
    pub = R.conops_needs(doc)
    assert pub == {n["id"]: " ".join(n["statement"].split()) for n in req["needs"]}, "the quoted needs differ from CONOPS"


def t_every_owner_ruling_of_the_brief_is_recorded_as_the_owners():
    """The rulings of 25 and 26 September 2026 this registry applies, each dated and the owner's: D-01, D-02a and
    D-02b on 25 September (about 23:27 to 23:40 CEST), D-02c and every later one on 26 September."""
    req = R.load_requirements(); by = {r["id"]: r for r in req["owner_rulings"]}
    want = {"D-01": "2026-09-25", "D-02a": "2026-09-25", "D-02b": "2026-09-25", "D-02c": "2026-09-26",
            "decision-27": "2026-09-25", "decision-28": "2026-09-25", "decision-41": "2026-09-25",
            "decision-43": "2026-09-25", "standing-rule": "2026-09-26"}
    for k in ("D-02d", "D-02e", "D-03", "D-04", "D-05", "D-06", "D-07", "D-08", "D-08a", "D-08-reversal", "D-09",
              "D-10", "D-11", "D-12", "D-13", "D-14", "D-15", "D-16", "D-17"):
        want[k] = "2026-09-26"
    for rid, day in want.items():
        assert rid in by, "the owner ruling %s is not recorded" % rid
        assert by[rid]["authority"] == "OWNER" and by[rid]["ruled_on"] == day, "%s is not the owner's of %s" % (rid, day)
    assert by["D-03"].get("decision") == 30 and by["D-15"].get("decision") == 40, "D-03 or D-15 lost its decision"
    assert by["D-08"].get("reversed_by") == "D-08-reversal", "D-08 does not read as reversed by the owner"
    assert not [r["id"] for r in req["records"] if "D-08" in (r.get("rulings") or [])], "a record rests on reversed D-08"
    closed = {i["id"]: i["closed_by"] for i in req["closed_items"]}
    assert closed.get("M-01") == "D-08-reversal", "the owner's case measurement is not closed by his reversal"
    assert "D-18" not in by, "D-18 is conditional and must not read as ruled"
    open_ids = {i["id"] for i in req["open_items"]}
    assert "D-18" in open_ids and not (open_ids & set(want)), "a ruled question is still open: %s" % (open_ids & set(want))
    assert not [i["id"] for i in req["open_items"] if i["class"] == "OWNER"], \
        "an OWNER question is open, and the owner is not asked again (standing rule of 26 September 2026)"


def t_every_choice_the_session_took_is_recorded_as_the_sessions():
    req = R.load_requirements(); sc = {c["id"]: c for c in req["session_choices"]}
    closed = {i["id"]: i["closed_by"] for i in req["closed_items"]}
    assert all(c["authority"] == "SESSION" and c["under"] == "standing-rule" for c in sc.values())
    assert sc["SC-01"].get("adds_core_needs") == ["NEED-19"], "SOS did not join the core by SC-01"
    assert closed.get("D-01-R1") == "SC-02" and closed.get("D-01-R2") == "SC-01" and closed.get("D-02a-R1") == "SC-03"
    assert closed.get("S-38") == "SC-02" and "NAMED EXCEPTIONS" in sc["SC-02"]["taken"], \
        "SC-02 does not name LoRa and cellular data as the exceptions IOHA section 15a and appendix 32.366 record"
    assert sc["SC-06"].get("withdrawn_on") == "2026-09-26", "the road route (SC-06) is not withdrawn"
    assert not [r["id"] for r in req["records"] if "SC-06" in (r.get("choices") or [])], "a record rests on SC-06"
    assert not [r["id"] for r in req["records"] if r.get("prototype_1_basis") == "READING"], "a reading is left"
    assert "NEED-19" not in R.owner_core_needs(req) and "NEED-19" in R.core_needs(req)


def t_no_em_or_en_dash_in_the_registry_or_the_page():
    for p in (R.REQUIREMENTS, PAGE):
        if not os.path.exists(p): continue
        t = open(p, encoding="utf-8").read()
        assert "\u2014" not in t and "\u2013" not in t, "%s carries an em or en dash" % os.path.basename(p)


# ------------------------------------------------------------------------------------------ evidence classes
def t_the_classes_are_current_evidence_classes():
    """A record's reading is classed in the same six classes CURRENT-EVIDENCE.md gives every rule-board reading, and
    counts where rules_status counts it (plus a bound desk review or a physical test)."""
    import rules_status as S
    assert tuple(R.REQ_EVIDENCE_CLASSES) == tuple(S.EVIDENCE_CLASSES), (R.REQ_EVIDENCE_CLASSES, S.EVIDENCE_CLASSES)
    assert set(R.REQ_PASS_CLASSES) == set(S.COUNTS_AS_CURRENT) | {S.DESK_REVIEW, S.PHYSICAL_TEST}


def t_a_reading_without_its_class_fails():
    req, kw = _fixture(); _passing(req).pop("evidence_class")
    _refused(req, kw, ("REQ-001", "no evidence_class"))
    req, kw = _fixture(); _passing(req)
    assert not _errors(req, kw), "a bound desk PASS was refused: %s" % _errors(req, kw)


def t_a_pass_on_evidence_awaiting_revalidation_fails():
    """Review of 26 September 2026, section 1: evidence awaiting revalidation never decides."""
    for cls in ("AWAITING_REVALIDATION", "NO_EVIDENCE"):
        req, kw = _fixture(); _passing(req, cls=cls)
        _refused(req, kw, ("REQ-001", "PASS on evidence classed %s" % cls))


def t_a_physical_test_before_hardware_fails():
    req, kw = _fixture(); _passing(req, cls="PHYSICAL_TEST")
    _refused(req, kw, ("REQ-001", "PHYSICAL_TEST at SCHEMATIC"))


def t_a_desk_reading_binds_what_it_read():
    req, kw = _fixture(); _passing(req).pop("evidence_bound_to")
    _refused(req, kw, ("REQ-001", "names no file it is bound to"))
    req, kw = _fixture(); _passing(req)["evidence_bound_to"] = ["v2/docs/PANEL.md@" + "0" * 16]
    _refused(req, kw, ("REQ-001", "bound to v2/docs/PANEL.md", "re-read it"))
    req, kw = _fixture(); _passing(req)["evidence_bound_to"] = ["v2/docs/NO-SUCH.md@" + "0" * 16]
    _refused(req, kw, ("REQ-001", "not in this tree"))
    # a stale FAIL warns and does not refuse: the record still says what failed, and the next reading replaces it
    req, kw = _fixture(); r = _passing(req); r["evidence_result"] = "FAIL"
    r["evidence_bound_to"] = ["v2/docs/PANEL.md@" + "0" * 16]
    errs, warns = R.validate_requirements(req, **kw)
    assert not errs and any("re-read it" in w for w in warns), (errs, warns)


def t_a_pass_whose_rules_are_not_current_fails():
    """A PASS whose rules judge the whole record rests on those rules' readings, so they must count on its boards."""
    req, kw = _fixture(); r = _passing(req); r["rule_coverage"] = "FULL"
    kw["rule_classes"] = {("RF-002", "b"): "AWAITING_REVALIDATION"}
    _refused(req, kw, ("REQ-001", "RF-002", "AWAITING_REVALIDATION", "board B"))
    kw["rule_classes"] = {("RF-002", "b"): "CURRENT_CANDIDATE"}
    assert not _errors(req, kw), _errors(req, kw)
    req, kw = _fixture(); _passing(req)             # PARTIAL: the record's own bound reading carries the PASS
    kw["rule_classes"] = {("RF-002", "b"): "AWAITING_REVALIDATION"}
    assert not _errors(req, kw), _errors(req, kw)


# ------------------------------------------------------------------------------------------ reversals and withdrawals
def t_a_reversed_ruling_is_cited_by_nothing():
    """D-08, 26 September 2026: the owner reversed his own ruling that morning; it keeps its row and nothing rests on it."""
    req, kw = _fixture()
    req["owner_rulings"].append({"id": "D-08", "authority": "OWNER", "ruled_on": "2026-09-26", "title": "measure",
                                 "ruling": "The owner measures his case.", "reversed_by": "D-08-reversal"})
    req["owner_rulings"].append({"id": "D-08-reversal", "authority": "OWNER", "ruled_on": "2026-09-26",
                                 "title": "withdrawn", "ruling": "The measurement is withdrawn."})
    assert not _errors(req, kw), _errors(req, kw)
    _rec(req, "REQ-001")["rulings"] = ["D-03", "D-08"]
    _refused(req, kw, ("REQ-001", "cites D-08", "D-08-reversal reversed"))
    req["owner_rulings"][-2]["reversed_by"] = "D-77"
    _refused(req, kw, ("D-08", "reversed by 'D-77'"))


def t_a_withdrawn_choice_is_rested_on_by_nothing():
    """SC-06, 26 September 2026: the road route was withdrawn after the review of that day."""
    req, kw = _fixture()
    req["session_choices"].append({"id": "SC-02", "authority": "SESSION", "under": "standing-rule",
                                   "taken_on": "2026-09-26", "question": "Which route?", "taken": "By road.",
                                   "why": "An unknown test status was read as leaving road open.",
                                   "withdrawn_on": "2026-09-26",
                                   "withdrawn_why": "Road carriage has its own dangerous-goods rules (the ADR)."})
    assert not _errors(req, kw), _errors(req, kw)
    _rec(req, "REQ-001")["choices"] = ["SC-02"]
    _refused(req, kw, ("REQ-001", "rests on SC-02", "withdrew"))
    req, kw = _fixture(); req["session_choices"][0].update({"withdrawn_on": "2026-09-26", "withdrawn_why": "x"})
    _refused(req, kw, ("SC-01", "withdrawn with no reason"))
    _refused(req, kw, ("SC-01", "withdrawn and still closes"))


def t_a_commit_closes_an_item_only_with_its_evidence_and_only_if_the_tree_holds_it():
    """The round-4 challenge: S-06, S-17 and S-25 were answered on main by commits, and a registry that could close
    an item only by a ruling kept them open."""
    head = _head_commit()
    req, kw = _fixture(); req["open_items"] = [i for i in req["open_items"] if i["id"] != "S-01"]
    _rec(req, "CFL-001")["waits_on"] = []
    req["closed_items"].append({"id": "S-01", "closed_by": "commit %s" % head[:8], "title": "EMCON gates",
                                "closing_evidence": "v2/docs/PANEL.md section 6 read at HEAD: the gates are drawn."})
    assert not _errors(req, kw), _errors(req, kw)
    req["closed_items"][-1]["closed_by"] = "commit 0123abcd"
    _refused(req, kw, ("S-01", "commit 0123abcd", "does not hold"))
    req["closed_items"][-1]["closed_by"] = "commit %s" % head[:8]; req["closed_items"][-1]["closing_evidence"] = "done"
    _refused(req, kw, ("S-01", "no closing_evidence"))
    req["closed_items"][-1]["closing_evidence"] = "v2/docs/PANEL.md section 6 read at HEAD: the gates are drawn."
    _rec(req, "CFL-001")["waits_on"] = ["S-01"]
    _refused(req, kw, ("CFL-001", "waits on S-01", "cite that instead"))


# ------------------------------------------------------------------------------------------ feasibility blockers
def _blocker(req):
    """An open feasibility blocker on PANEL.md (a tracked page), holding REQ-001."""
    r = {"id": "FEA-001", "kind": "feasibility", "parent": "NEED-01", "title": "a core function not yet shown",
         "statement": "The function is supported at desk level and not yet shown on the part.",
         "acceptance": "The bench records pass on the fitted part.",
         "feasibility_page": "v2/docs/PANEL.md", "blocker_ids": ["EMCON_HW", "ZEROIZE_HW"],
         "closing_evidence": "The bench pass records filed with the part lot and the configuration read back.",
         "owner": "The session runs the bench once the parts exist; the spend is the owner's.",
         "blocks": ["REQ-001"], "holds_layout_entry": ["b"], "allocated_to": ["b"],
         "verification_method": ["PROTOTYPE_MEASUREMENT"], "verification_phase": "SCHEMATIC",
         "final_phase": "PROTOTYPE", "prototype_1": "core", "prototype_1_basis": "NEED_DEFAULT",
         "satisfied_by": {"rules": [], "decisions": []}, "rule_coverage": "NONE", "status": "FEASIBILITY_OPEN",
         "evidence_result": "INCONCLUSIVE", "evidence_phase": "SCHEMATIC", "evidence_class": "DESK_REVIEW",
         "evidence": ["v2/docs/PANEL.md section 6 read: supported, not shown"],
         "evidence_bound_to": [_bind("v2/docs/PANEL.md")], "release_effect": "BLOCKER",
         "source": ["v2/docs/PANEL.md section 6"], "source_check": "VERIFIED"}
    req["records"].append(r)
    return r


def t_a_feasibility_blocker_names_its_page_ids_evidence_and_owner():
    """Review of 26 September 2026, section 3 and checkpoint item 1: every core function whose feasibility is not
    closed is an explicit blocker naming its page, the page's own ids, the closing evidence and its owner."""
    req, kw = _fixture(); _blocker(req)
    assert not _errors(req, kw), "the acceptable blocker was refused: %s" % _errors(req, kw)
    req, kw = _fixture(); _blocker(req)["blocker_ids"] = ["FB-NOT-ON-THE-PAGE"]
    _refused(req, kw, ("FEA-001", "FB-NOT-ON-THE-PAGE", "is not on v2/docs/PANEL.md"))
    req, kw = _fixture(); _blocker(req)["feasibility_page"] = "v2/docs/feasibility/NO-SUCH.md"
    _refused(req, kw, ("FEA-001", "feasibility_page", "not in this tree"))
    for k in ("closing_evidence", "owner"):
        req, kw = _fixture(); _blocker(req)[k] = ""
        _refused(req, kw, ("FEA-001", "a feasibility blocker with no %s" % k))
    req, kw = _fixture(); b = _blocker(req); b["blocks"] = []; b["holds_layout_entry"] = []
    _refused(req, kw, ("FEA-001", "holds nothing"))
    req, kw = _fixture(); _blocker(req)["blocks"] = ["REQ-999"]
    _refused(req, kw, ("FEA-001", "REQ-999", "not a record"))
    req, kw = _fixture(); _blocker(req)["status"] = "DEFINED"
    _refused(req, kw, ("FEA-001", "FEASIBILITY_OPEN or FEASIBILITY_CLOSED"))
    req, kw = _fixture(); _blocker(req)["release_effect"] = "MUST_JUSTIFY"
    _refused(req, kw, ("FEA-001", "on the core is a BLOCKER"))


def t_an_open_blocker_and_what_it_holds_never_read_pass():
    req, kw = _fixture(); b = _blocker(req); b["evidence_result"] = "PASS"
    _refused(req, kw, ("FEA-001", "PASS on a record whose pass line is not settled"))
    req, kw = _fixture(); _blocker(req); _passing(req)
    _refused(req, kw, ("REQ-001 reads PASS while FEA-001", "is open"))
    req, kw = _fixture(); b = _blocker(req); _passing(req)
    b.update({"status": "FEASIBILITY_CLOSED", "resolved_by": "the bench records of the test", "evidence_result": "PASS"})
    assert not _errors(req, kw), "a closed blocker still held its record: %s" % _errors(req, kw)


def t_the_real_blockers_cover_the_core_functions_the_review_names():
    """ZEROIZE, EMCON, the failover fabric, power and thermal, battery protection and decoupling: each open core
    function the review of 26 September 2026 names has an open blocker on its own page."""
    need(R.REQUIREMENTS, "no requirements registry in this tree")
    req = R.load_requirements()
    fea = [r for r in req["records"] if r["kind"] == "feasibility"]
    pages = {r["feasibility_page"] for r in fea}
    for want in ("v2/docs/feasibility/ZEROIZE.md", "v2/docs/feasibility/EMCON.md",
                 "v2/docs/feasibility/FAILOVER-FABRIC.md", "v2/docs/feasibility/POWER-THERMAL.md",
                 "v2/docs/feasibility/DECOUPLING.md", "v2/docs/review-packets/battery/REVIEW-REQUEST.md"):
        assert want in pages, "no feasibility blocker on %s" % want
    for r in fea:
        assert r["prototype_1"] == "core" and r["release_effect"] == "BLOCKER" and r["evidence_result"] != "PASS", r["id"]


def t_no_real_record_reads_pass_on_evidence_that_does_not_count():
    """Judged against the rule classes of this tree's audits, which rules_status wrote (CURRENT-EVIDENCE.md)."""
    need(R.REQUIREMENTS, "no requirements registry in this tree")
    rc = R.rule_classes_from_audit()
    if rc is None: raise Skip("out/rule-audit is not in this tree (gitignored): the rule classes cannot be read")
    errs, _w = R.validate_requirements(rule_classes=rc)
    assert not errs, errs[:10]
    for r in R.load_requirements()["records"]:
        if r["evidence_result"] == "PASS":
            assert r.get("evidence_class") in R.REQ_PASS_CLASSES and r.get("evidence_bound_to"), r["id"]


def t_a_pass_at_an_earlier_phase_says_the_final_phase_is_not_judged():
    """CON-019's shape: PASS read at SCHEMATIC, acceptance ending at PROTOTYPE. The cell says both; a record judged at
    its final phase says only its result."""
    early = {"evidence_result": "PASS", "evidence_phase": "SCHEMATIC", "final_phase": "PROTOTYPE"}
    whole = {"evidence_result": "PASS", "evidence_phase": "SCHEMATIC", "final_phase": "SCHEMATIC"}
    none = {"evidence_result": "NOT_JUDGED", "final_phase": "PROTOTYPE"}
    assert RR._result(early) == "PASS at SCHEMATIC; PROTOTYPE not yet judged", RR._result(early)
    assert RR._result(whole) == "PASS at SCHEMATIC", RR._result(whole)
    assert RR._result(none) == "NOT_JUDGED", RR._result(none)


# ------------------------------------------------------------------------------------------ the trace page
def t_the_trace_page_is_generated_not_hand_kept():
    need(PAGE, "the trace page has not been rendered yet")
    assert open(PAGE, encoding="utf-8").read() == RR.requirements_doc(), \
        "REQUIREMENTS-TRACE.md differs from what pcb_requirements.yaml renders: run rules_render.py --requirements"


def t_check_refuses_a_hand_edited_trace_page():
    """Executed on COPIES (`--page`): a damaged copy is refused, an undamaged copy is current, the tree's page is
    never written."""
    need(PAGE, "the trace page has not been rendered yet")
    before = open(PAGE, "rb").read()
    d = tempfile.mkdtemp(prefix="req-page-")
    bad, good = os.path.join(d, "bad.md"), os.path.join(d, "good.md")
    shutil.copy(PAGE, bad); shutil.copy(PAGE, good)
    open(bad, "a", encoding="utf-8").write("\n<!-- a hand edit -->\n")
    def run(p):
        return subprocess.run([sys.executable, os.path.join(TOOLS, "rules_render.py"), "--requirements", "--check",
                               "--page", p], capture_output=True, text=True, cwd=TOOLS)
    pb, pg = run(bad), run(good)
    assert pb.returncode == 1, "--check did not refuse a hand-edited copy (exit %d):\n%s" % (pb.returncode, (pb.stdout + pb.stderr)[-400:])
    assert pg.returncode == 0, "--check refused an untouched copy:\n%s" % (pg.stdout + pg.stderr)[-400:]
    assert open(PAGE, "rb").read() == before, "the check wrote into the tree's own trace page"


def t_the_page_names_every_record_need_choice_and_item():
    need(PAGE, "the trace page has not been rendered yet")
    t = open(PAGE, encoding="utf-8").read(); req = R.load_requirements()
    missing = [x for x in [r["id"] for r in req["records"]] + [n["id"] for n in req["needs"]] +
               [i["id"] for i in req["open_items"]] + [i["id"] for i in req["closed_items"]] +
               [c["id"] for c in req["session_choices"]] if x not in t]
    assert not missing, "the trace page does not name: %s" % missing


def t_the_page_does_not_change_with_the_decision_index_for_what_an_owner_ruling_names():
    """The page is rendered in a worker tree and must be current in the merged tree, where pcb_decisions.yaml
    records decisions 30 and 40 as the owner's. A decision an owner ruling names is shown by the ruling."""
    need(R.REQUIREMENTS, "no requirements registry in this tree")
    req = R.load_requirements(); dec = R.decisions_index()
    ruled = copy.deepcopy(dec); opened = copy.deepcopy(dec)
    for r in req["owner_rulings"]:
        if r.get("decision") is None: continue
        n = int(r["decision"])
        ruled[n].update({"status": "ruled", "authority": "OWNER", "ruled_on": r["ruled_on"]})
        opened[n].update({"status": "open", "authority": None, "ruled_on": None})
    assert RR.requirements_doc(req=req, dec=ruled) == RR.requirements_doc(req=req, dec=opened), \
        "the trace page depends on whether this tree's pcb_decisions.yaml has recorded the owner's rulings yet"


def t_no_page_is_rendered_from_a_registry_that_does_not_validate():
    """Judged on the fixture's own CONOPS and root, so the refusal is for the defect and never for the pin."""
    req, kw = _fixture(); _rec(req, "REQ-002").pop("tbd_effect")
    try:
        RR.requirements_doc(req=req, dec=kw["decisions"], needs_doc=kw["needs_doc"], root=kw["root"],
                            interfaces=kw["interfaces"])
    except ValueError as e:
        assert "does not validate" in str(e) and "a TBD with no effect" in str(e), e
    else:
        raise AssertionError("a trace page was rendered from a registry that does not validate")
    req, kw = _fixture()
    body = RR.requirements_doc(req=req, dec=kw["decisions"], needs_doc=kw["needs_doc"], root=kw["root"],
                               interfaces=kw["interfaces"])
    assert "REQ-001" in body and "SC-01" in body


def t_a_refused_trace_page_fails_the_run_and_every_other_page_still_renders():
    """The round-3 defect: a registry that did not validate raised out of render(), so every rule page stopped
    rendering and --check crashed instead of refusing. The refusal is now the trace page's alone."""
    need(R.REQUIREMENTS, "no requirements registry in this tree")
    keep = RR.requirements_doc
    def broken(*a, **k): raise ValueError("pcb_requirements.yaml does not validate (1 error(s)): a test")
    RR.requirements_doc = broken
    try:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            files = RR.render(board_docs=False)
            refused = list(RR.REFUSED)
            rc = RR.main(["--check"])
    finally:
        RR.requirements_doc = keep
    names = {os.path.basename(p) for p in files}
    assert RR.REQ_TRACE not in names and refused == [RR.REQ_TRACE], (names, refused)
    assert {"PCB-GOLDEN-RULES.md", "PCB-RULE-COVERAGE.md", "PCB-GAP-REGISTER.md"} <= names, names
    assert rc == 1 and "REFUSED" in out.getvalue() and "refused" in out.getvalue(), out.getvalue()[-400:]


# ------------------------------------------------------------------------------------------ the claims screen
def t_the_foundation_documents_are_screened_for_claims():
    for doc in ("v2/docs/PRODUCT-BRIEF.md", "v2/docs/CONOPS.md", "v2/docs/REQUIREMENTS-TRACE.md"):
        assert doc in CC.DEFAULT, "%s is not in claims_check.py's DEFAULT list" % doc


def t_the_trace_page_states_requirements_not_claims():
    need(PAGE, "the trace page has not been rendered yet")
    n, bad = CC.check([os.path.relpath(PAGE, CC.ROOT)])
    assert n and not bad, "the trace page carries an unqualified claim: %s" % bad[:3]


def t_a_negation_in_front_of_a_claim_word_is_not_a_claim():
    """'its sheath is not rated for sun' says the opposite of a rating; 'its sheath is rated for sun' is one."""
    d = tempfile.mkdtemp(prefix="claims-")
    for text, flagged in (("The sheath is not rated for sun, rain or frost.", False),
                          ("The sheath is rated for sun, rain or frost.", True),
                          ("The kit is certified and the sheath is not rated for sun.", True),
                          ("The enclosure is IP67 and waterproof.", True)):
        p = os.path.join(d, "doc.md"); open(p, "w", encoding="utf-8").write(text + "\n")
        n, bad = CC.check([p])
        assert n == 1 and bool(bad) == flagged, (text, bad)
