"""The layer 3 amendment (MESHSAT-1357, 1 October 2026; v2/docs/records/l3am/): the independent review the owner relayed,
findings L3-R01, L3-R02, L3-R04 and L3-R05, and the finding carried from the engineering collaborator's layer 4 check.

Each test states a property that holds before and after an acceptance is filed again, with fixtures for the negative case:
the acceptance binds the reviewed content (L3-R04: a revision that is no commit or the wrong commit, or a material change
to the requirements, the owner brief, the governing change record or the acceptance policy, invalidates it; a change to
anything else does not; a record without a manifest binds nothing; B1 of the amendment's check: the requirements digest
binds the owner rulings, the session choices, the accepted exceptions and the stage conditions, and every field of the
registry is classified in or out); the findings close only with a new accepted check of this amendment, bound to a
reviewed revision whose content the tree still holds (B2), and the acceptance script verifies that check again; the
acceptance script writes the manifest, refuses what the binding refuses and keeps a superseded record as history; every section of a current view that states a
solar-assisted figure names the case it was computed with (L3-R01), and the case agrees with the files and the summary;
REQ-042 cannot read satisfied because its hydrogen part is named (L3-R02); REQ-016's window is the one D-34 retained and
its protection is judged apart from it (L3-R05). Nothing here writes into the tree; the fixture commits are unreferenced
objects (l3amfix.py).
"""
import copy
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
L3 = os.path.join(ROOT, "v2", "docs", "handover", "layer3")
AM = os.path.join(ROOT, "v2", "docs", "records", "l3am")
ACC = os.path.join(ROOT, "v2", "docs", "records", "l3r5", "apply_l3r5_accept.py")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
sys.path.insert(0, L3)
from harness import need  # noqa: E402

LEGACY = "b4b199d0ceee6d7a632b85090fbf3bf95a602758"
CLOSE = os.path.join(AM, "apply_l3am_findings_closed.py")


def _run(args):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True, cwd=tempfile.gettempdir())


def _tree():
    import render_l3r2 as RL
    import rules_lib as R
    return RL, R.load_requirements(), RL.load_data()


def _record(RL, req, data, rev):
    return {"revision": rev, "authorised_by": "D-39", "evidence": [data["independent_check"][-1]["record"]],
            "accepted_on": "2026-10-01", "manifest": RL.content_manifest(req, data)}


def _root_copy(RL, data, overrides=None):
    """A directory holding what acceptance_ok reads under its root (the two hashed files and the evidence), with
    `overrides` {path: bytes} written into it; nothing else of the tree."""
    d = tempfile.mkdtemp(prefix="l3am-root-")
    for p in [RL.BRIEF_REL, RL.RECORD_REL] + [c["record"] for c in data["independent_check"]]:
        os.makedirs(os.path.dirname(os.path.join(d, p)), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, p), os.path.join(d, p))
    for p, b in (overrides or {}).items():
        os.makedirs(os.path.dirname(os.path.join(d, p)), exist_ok=True)
        open(os.path.join(d, p), "wb").write(b)
    return d


# ------------------------------------------------------------------------------------------------ L3-R04
def t_l3am_acceptance_binds_the_reviewed_content():
    """acceptance_ok holds only for a record whose revision is a commit of this repository holding the content its
    manifest names, and whose manifest matches the content as it stands. Positive: the content as it stands, accepted at a
    commit that holds it, stays valid, and so it does when an unrelated record (a reading added to a registry record, a
    note), a layer 4 file or another record file changes. Negative: forty zeros, forty 'a', an existing commit of the
    wrong content (the repository's first commit, and the legacy acceptance's b4b199d0 once the content moved), REQ-016's
    statement changed to 500 W, the owner brief or the change record changed by a byte, the acceptance policy changed.
    The legacy record (no manifest) reads as history, not acceptance: the status level stays DRAFTED."""
    import l3amfix as F
    RL, req, data = _tree()
    rev = F.commit_with()
    good = copy.deepcopy(data); good["baseline_acceptance"] = _record(RL, req, data, rev)
    ok, why = RL.acceptance_ok(req, good)
    assert ok, "the unchanged accepted content does not validate: %s" % why
    # unrelated changes leave it valid
    req2 = copy.deepcopy(req)
    r72 = next(r for r in req2["records"] if r["id"] == "REQ-072")
    r72["evidence"] = list(r72.get("evidence") or []) + ["v2/docs/records/l4e/fixture.md read at layer 4 (a fixture)"]
    next(r for r in req2["records"] if r["id"] == "CFL-016")["notes"] = "a fixture note"
    assert RL.acceptance_ok(req2, good)[0], "a reading or a note added to a registry record invalidated the acceptance"
    root = _root_copy(RL, good, {"v2/docs/records/l4e/FIXTURE.md": b"a layer 4 file\n",
                                 "v2/docs/records/l3r5/README.md": b"another record, changed\n"})
    assert RL.acceptance_ok(req, good, root=root)[0], "a layer 4 file or another record invalidated the acceptance"
    hist = copy.deepcopy(good); hist["baseline_acceptance_history"] = [{"revision": LEGACY}]
    assert RL.acceptance_ok(req, hist)[0], "the acceptance's own history entered the policy it hashes"
    # a revision that is no commit, or the wrong commit
    for bad_rev, want in (("0" * 40, "not a commit"), ("a" * 40, "not a commit"), (F.root_commit(), "does not hold")):
        d = copy.deepcopy(good); d["baseline_acceptance"]["revision"] = bad_rev
        ok, why = RL.acceptance_ok(req, d)
        assert not ok and want in why, "revision %s: %s" % (bad_rev[:12], why or "valid")
    if RL.manifest_differs(RL.manifest_at(LEGACY)[0], good["baseline_acceptance"]["manifest"]):
        d = copy.deepcopy(good); d["baseline_acceptance"]["revision"] = LEGACY
        ok, why = RL.acceptance_ok(req, d)
        assert not ok and "does not hold the content" in why, why
    # material changes
    req3 = copy.deepcopy(req)
    r16 = next(r for r in req3["records"] if r["id"] == "REQ-016")
    assert "at most 100 W into the stage" in r16["statement"]
    r16["statement"] = r16["statement"].replace("at most 100 W into the stage", "at most 500 W into the stage")
    ok, why = RL.acceptance_ok(req3, good)
    assert not ok and "requirements" in why, "REQ-016 at 500 W kept the acceptance: %s" % why
    for path in (RL.BRIEF_REL, RL.RECORD_REL):
        b = open(os.path.join(ROOT, path), "rb").read() + b"\n"
        ok, why = RL.acceptance_ok(req, good, root=_root_copy(RL, good, {path: b}))
        assert not ok and "changed since" in why, "%s changed kept the acceptance: %s" % (path, why)
    pol = copy.deepcopy(good)
    next(x for x in pol["status_levels"] if x["id"] == "VALIDATED")["holds_when"] = "the owner asks for it"
    ok, why = RL.acceptance_ok(req, pol)
    assert not ok and "acceptance_policy" in why, "a changed acceptance policy kept the acceptance: %s" % why
    # the legacy record: history, not acceptance
    legacy = copy.deepcopy(data)
    legacy["baseline_acceptance"] = {"revision": LEGACY, "authorised_by": "D-39", "accepted_on": "2026-09-30",
                                     "evidence": [data["independent_check"][-1]["record"]]}
    ok, why = RL.acceptance_ok(req, legacy)
    assert not ok and "no content manifest" in why, why
    dec, h3 = RL.decided(req, legacy), RL.load_h3()
    assert RL.status_level(req, dec, legacy, h3)[0] == "DRAFTED"
    # the tree's own record: validates only with a manifest
    filed = data.get("baseline_acceptance")
    if filed and not filed.get("manifest"): assert not RL.acceptance_ok(req, data)[0]


def _valid(R, req):
    """rules_lib's own validation of a fixture registry: [] when the registry is schema-valid."""
    errs, _w = R.validate_requirements(copy.deepcopy(req))
    return errs


def t_l3am_the_requirements_digest_binds_normative_content():
    """B1 of the amendment's check and its recheck, by the principle (render_l3r2.REQUIREMENTS_PRINCIPLE): what states a
    demand or an authority is in the digest; what legitimately changes as downstream work progresses is not. Every field
    of the tree's registry is placed in a category of the principle, and every record status value rules_lib allows has
    its projection. Closures the registry's own validator accepts leave the digest and a bound acceptance unchanged:
    FEA-003's layout stage closed as rules_lib requires (status CLOSED, closed_by, holds_layout_entry updated; the same
    closure with the summary left stale is refused by the validator), FEA-003 closed altogether (FEASIBILITY_CLOSED,
    resolved_by), CFL-006 between its open and its resolved state, and S-128 closed by a commit with REQ-042 no longer
    waiting on it; so do an added reading, a note and a history line, each schema-valid. Eight normative changes
    invalidate, each for a requirements mismatch: D-11's ruling, a session choice's answer, CON-012's accepted exception,
    a stage's requires, needs and holds, a record's rulings, and an added owner ruling."""
    import l3amfix as F
    import rules_lib as R
    RL, req, data = _tree()
    cats = dict(RL.IN_CATEGORIES, **RL.OUT_CATEGORIES)
    assert not set(RL.IN_CATEGORIES) & set(RL.OUT_CATEGORIES) and "IN is whatever states" in RL.REQUIREMENTS_PRINCIPLE
    seen = {"top": set(req), "ruling": {k for x in req["owner_rulings"] for k in x},
            "choice": {k for x in req["session_choices"] for k in x}, "record": {k for x in req["records"] for k in x},
            "stage": {k for x in req["records"] for s in (x.get("stages") or []) for k in s}}
    for kind, keys in seen.items():
        miss = sorted(keys - set(RL.REQUIREMENTS_FIELDS[kind]))
        assert not miss, "the registry's %s fields %s are placed in no category of the principle" % (kind, miss)
        assert all(c in cats for c in RL.REQUIREMENTS_FIELDS[kind].values()), kind
    assert set(RL.STATUS_PROJECTION) == set(R.REQ_STATUS), "a record status value has no projection"
    assert len({RL.STATUS_PROJECTION[s] for s in ("FEASIBILITY_OPEN", "FEASIBILITY_CLOSED")}) == 1
    assert len({RL.STATUS_PROJECTION[s] for s in ("CONFLICT_OPEN", "CONFLICT_RESOLVED")}) == 1
    assert RL.STATUS_PROJECTION["SUPERSEDED"] != RL.STATUS_PROJECTION["DEFINED"]
    assert not _valid(R, req), "the tree's registry does not validate"
    digest = RL.requirements_digest(req)
    good = copy.deepcopy(data); good["baseline_acceptance"] = _record(RL, req, data, F.commit_with())
    assert RL.acceptance_ok(req, good)[0], RL.acceptance_ok(req, good)[1]

    def rec(r, rid): return next(x for x in r["records"] if x["id"] == rid)

    def stage(r, rid="FEA-003", name="LAYOUT_ENTRY"): return next(s for s in rec(r, rid)["stages"] if s["stage"] == name)
    assert rec(req, "FEA-003")["holds_layout_entry"] and stage(req)["status"] == "OPEN", "FEA-003's layout stage is not open"
    # FEA-003's layout stage closed as rules_lib requires
    closed = copy.deepcopy(req)
    stage(closed).update(status="CLOSED", closed_by="a fixture closure: FB-FAB-1 to FB-FAB-7 closed on the committed netlist")
    stale = _valid(R, closed)
    assert stale and "holds_layout_entry" in stale[0], "the validator accepts a closed layout stage with a stale hold: %s" % stale
    rec(closed, "FEA-003")["holds_layout_entry"] = []
    # FEA-003 closed altogether
    whole = copy.deepcopy(closed)
    for s in rec(whole, "FEA-003")["stages"]:
        s.update(status="CLOSED", closed_by="a fixture closure of the stage, its evidence named")
    rec(whole, "FEA-003").update(status="FEASIBILITY_CLOSED", resolved_by="a fixture: every stage closed with its evidence")
    # CFL-006 between its open and its resolved state
    assert rec(req, "CFL-006")["status"] == "CONFLICT_RESOLVED" and rec(req, "CFL-006")["evidence_result"] == "FAIL"
    opened = copy.deepcopy(req)
    rec(opened, "CFL-006")["status"] = "CONFLICT_OPEN"; rec(opened, "CFL-006").pop("resolved_by")
    # S-128 closed by a commit, REQ-042 no longer waiting on it
    s128 = copy.deepcopy(req)
    item = next(x for x in s128["open_items"] if x["id"] == "S-128"); s128["open_items"].remove(item)
    s128["closed_items"].append({"id": "S-128", "title": item["title"], "closed_by": "commit %s" % F.root_commit()[:12],
                                 "closing_evidence": "a fixture closure read in v2/docs/records/l3am/DISPOSITIONS.md"})
    rec(s128, "REQ-042")["waits_on"] = [x for x in rec(s128, "REQ-042")["waits_on"] if x != "S-128"]
    reading = copy.deepcopy(req)
    rec(reading, "REQ-072")["evidence"].append("v2/docs/records/l3batt/COMPARISON.md re-read at layer 4 (a fixture reading)")
    noted = copy.deepcopy(req)
    rec(noted, "REQ-016")["notes"] = str(rec(noted, "REQ-016")["notes"]) + " A fixture note."
    rec(noted, "REQ-016")["history"] = str(rec(noted, "REQ-016")["history"]) + " A fixture history line."
    for name, fx in (("FEA-003's layout stage closed", closed), ("FEA-003 closed", whole), ("CFL-006 open", opened),
                     ("S-128 closed", s128), ("a reading added", reading), ("a note and a history line", noted)):
        errs = _valid(R, fx)
        assert not errs, "%s is not schema-valid: %s" % (name, errs[:3])
        assert RL.requirements_digest(fx) == digest, "%s changed the requirements digest" % name
        assert RL.acceptance_ok(fx, good)[0], "%s invalidated the acceptance: %s" % (name, RL.acceptance_ok(fx, good)[1])
    hist = copy.deepcopy(good); hist["baseline_acceptance_history"] = [{"revision": LEGACY}]
    assert RL.acceptance_ok(req, hist)[0], "the acceptance's history entered the policy"
    mutations = (
        ("D-11's ruling", lambda r: next(x for x in r["owner_rulings"] if x["id"] == "D-11").update(
            ruling="Only one radio may transmit at a time.")),
        ("a session choice's answer", lambda r: r["session_choices"][0].update(taken="a different answer")),
        ("CON-012's accepted exception", lambda r: rec(r, "CON-012")["residual_risk_accepted"].update(
            what="Above +25 C ambient the kit runs one compute module.")),
        ("a stage's requires", lambda r: stage(r).update(requires="nothing closes this stage but a fixture text")),
        ("a stage's needs", lambda r: stage(r).update(needs=["DESK", "VENDOR_ANSWER"])),
        ("a stage's holds", lambda r: stage(r).update(holds=["b", "e"])),
        ("a record's rulings", lambda r: rec(r, "REQ-016")["rulings"].append("D-11")),
        ("an added owner ruling", lambda r: r["owner_rulings"].append({"id": "D-99", "authority": "OWNER", "ruled_on": "2026-10-02",
                                                                       "title": "a fixture", "ruling": "a fixture ruling", "source": []})),
    )
    assert len(mutations) == 8
    for name, edit in mutations:
        r2 = copy.deepcopy(req); edit(r2)
        assert RL.requirements_digest(r2) != digest, "%s left the digest unchanged" % name
        ok, why = RL.acceptance_ok(r2, good)
        assert not ok and "(requirements)" in why, "%s kept the acceptance: %s" % (name, why or "valid")


def t_l3am_the_acceptance_script_files_a_bound_record_and_supersedes():
    """apply_l3r5_accept.py on copies of l3r2.yaml, each built from the state before the amendment's check
    (l3amfix.open_state), so the test holds whether the tree's findings are OPEN or CLOSED: it refuses while the review's
    findings are OPEN, and when they read CLOSED by a check that does not verify (check-l3r5-3, the newest check filed
    before the amendment, named by hand); with the findings closed by a fixture check of the
    amendment (l3amfix.closed_copy) it refuses a revision that is not a commit or does not hold the copy's content, and
    --supersede with nothing filed; at a commit holding the copy's content, a child of the checked revision, it files a
    record with the content manifest that acceptance_ok validates; a second run is refused; --supersede keeps the filed
    record, as parsed, at the end of baseline_acceptance_history."""
    need(ACC, "the acceptance script is not in this tree")
    import l3amfix as F
    RL, req, data = _tree()
    raw = open(os.path.join(L3, "l3r2.yaml"), encoding="utf-8").read()

    def copy_of(text):
        p = os.path.join(tempfile.mkdtemp(prefix="l3am-accept-"), "l3r2.yaml"); open(p, "w", encoding="utf-8").write(text)
        return p
    null = "\n".join("baseline_acceptance: null" if l.startswith("baseline_acceptance:") else l for l in raw.split("\n"))
    null = F.open_state(null)
    rf = [l for l in null.split("\n") if l.startswith("review_findings: {")]
    assert len(rf) == 1 and ", state: OPEN," in rf[0], "the open state does not read OPEN"
    old_check = F.pre_amendment_newest()
    assert yaml.safe_load(null)["independent_check"][-1]["record"] == old_check
    r = _run([ACC, "--data", copy_of(null), "--revision", F.commit_with(), "--evidence", old_check, "--check"])
    assert r.returncode == 2 and "are OPEN" in r.stdout, "filed with the findings open:\n%s" % r.stdout
    by_hand = null.replace(rf[0], rf[0].replace(", state: OPEN,", ", state: CLOSED, checked_by: %s," % old_check), 1)
    rev_h = F.commit_with({"v2/docs/handover/layer3/l3r2.yaml": by_hand.encode("utf-8")})
    r = _run([ACC, "--data", copy_of(by_hand), "--revision", rev_h, "--evidence", old_check, "--check"])
    assert r.returncode == 2 and "does not verify" in r.stdout, "filed with the findings closed by the old check:\n%s" % r.stdout
    tip = F.tip()
    closed, check = F.closed_copy(null, tip)
    rev = F.commit_with({"v2/docs/handover/layer3/l3r2.yaml": closed.encode("utf-8")}, parent=tip)
    for bad, want in (("0" * 40, "not a commit"), (F.commit_with(), "does not")):
        r = _run([ACC, "--data", copy_of(closed), "--revision", bad, "--evidence", check, "--check"])
        assert r.returncode == 2 and want in r.stdout, "revision %s was not refused:\n%s" % (bad[:12], r.stdout)
    r = _run([ACC, "--data", copy_of(closed), "--revision", rev, "--evidence", check, "--supersede", "--check"])
    assert r.returncode == 2 and "nothing to supersede" in r.stdout, r.stdout
    p = copy_of(closed)
    r = _run([ACC, "--data", p, "--revision", rev, "--evidence", check, "--date", "2026-10-01"])
    assert r.returncode == 0, r.stdout
    got = yaml.safe_load(open(p, encoding="utf-8"))
    ba = got["baseline_acceptance"]
    assert ba["revision"] == rev and ba["authorised_by"] == "D-39" and ba["evidence"] == [check]
    assert set(ba["manifest"]) == {"requirements", "owner_brief", "change_record", "acceptance_policy"}
    assert RL.acceptance_ok(req, got)[0], RL.acceptance_ok(req, got)[1]
    r = _run([ACC, "--data", p, "--revision", rev, "--evidence", check])
    assert r.returncode == 2 and "has run" in r.stdout, "a second acceptance was not refused:\n%s" % r.stdout
    r = _run([ACC, "--data", p, "--revision", rev, "--evidence", check, "--date", "2026-10-02", "--supersede"])
    assert r.returncode == 0, r.stdout
    got2 = yaml.safe_load(open(p, encoding="utf-8"))
    assert got2["baseline_acceptance_history"] == [ba] and got2["baseline_acceptance"]["accepted_on"] == "2026-10-02"
    assert {k: v for k, v in got2.items() if not k.startswith("baseline_acceptance")} == \
        {k: v for k, v in got.items() if not k.startswith("baseline_acceptance")}
    # the tree's legacy record, superseded on a copy: kept as history, as filed
    if data.get("baseline_acceptance") and not data["baseline_acceptance"].get("manifest"):
        legacy = closed.replace("baseline_acceptance: null", [l for l in raw.split("\n") if l.startswith("baseline_acceptance:")][0], 1)
        p2 = copy_of(legacy)
        r = _run([ACC, "--data", p2, "--revision", rev, "--evidence", check])
        assert r.returncode == 2 and "has run" in r.stdout, r.stdout
        r = _run([ACC, "--data", p2, "--revision", rev, "--evidence", check, "--supersede"])
        assert r.returncode == 0, r.stdout
        got3 = yaml.safe_load(open(p2, encoding="utf-8"))
        assert got3["baseline_acceptance_history"] == [data["baseline_acceptance"]]
    assert open(os.path.join(L3, "l3r2.yaml"), encoding="utf-8").read() == raw, "the test changed the tree's l3r2.yaml"


def t_l3am_findings_close_only_with_a_check_of_the_amendment():
    """B2 of the amendment's check: apply_l3am_findings_closed.py closes the findings only with a new accepted check of
    this amendment. The copies are built from the state before the amendment's check (l3amfix.open_state: findings OPEN,
    the checks filed since the amendment's base taken out), whatever the tree holds; on the tree only what holds in either
    state: check-l3r5-3 never closes the findings, and findings the tree reads CLOSED are closed by a check of the
    amendment that verifies. Refused: check-l3r5-3 (the newest check before the amendment), a fixture record carrying
    the format under an old check's name, a record whose first line says no while filed ACCEPTED, a record without the
    scope line, a header line padded with a space (the three lines are compared exactly), a reviewed revision that is not a
    commit or not an ancestor of the tip, and a reviewed revision before a later change to any test file the amendment's
    commits changed (every one of them listed in AMENDMENT_FILES) or to one of its scripts. Accepted: a fixture check of
    the tip, its header exact; the script then changes checked_by, state and
    status and nothing else, and a second run is refused."""
    need(CLOSE, "the closing script is not in this tree")
    import l3amfix as F
    RL, req, data = _tree()
    tree_raw = open(os.path.join(L3, "l3r2.yaml"), encoding="utf-8").read()
    raw = F.open_state(tree_raw)
    old_check = F.pre_amendment_newest()
    assert yaml.safe_load(raw)["independent_check"][-1]["record"] == old_check
    r = _run([CLOSE, "--check-record", old_check, "--check"])
    assert r.returncode == 2 and "REFUSED" in r.stdout, "the pre-amendment check closed the findings:\n%s" % r.stdout
    rf = data["review_findings"]
    assert rf["state"] in ("OPEN", "CLOSED"), rf["state"]
    if rf["state"] == "CLOSED":
        sys.path.insert(0, AM)
        import apply_l3am_findings_closed as FC
        assert str(rf["checked_by"]) not in F.base_checks(), "the tree's findings are closed by a pre-amendment check"
        try:
            FC.verify(str(rf["checked_by"]), data)
        except FC.L.Refused as e:
            raise AssertionError("the check that closed the tree's findings does not verify: %s" % e)

    def copy_of(text):
        p = os.path.join(tempfile.mkdtemp(prefix="l3am-close-"), "l3r2.yaml"); open(p, "w", encoding="utf-8").write(text)
        return p
    tip = F.tip()

    def close(path, sha, head=tip, check=True):
        p = copy_of(F.with_check(raw, path, sha))
        return p, _run([CLOSE, "--data", p, "--check-record", path, "--head", head] + (["--check"] if check else []))
    r = _run([CLOSE, "--data", copy_of(raw), "--check-record", old_check, "--head", tip, "--check"])
    assert r.returncode == 2 and "scope" in r.stdout, "check-l3r5-3 closed the findings on a copy:\n%s" % r.stdout
    for args, want in (((tip, "check-l3r5-3.md"), "before the amendment"),
                       ((tip, "check-x.md", F.SCOPE, "accepted: no"), "accepted"),
                       ((tip, "check-x.md", F.SCOPE, "accepted: yes "), "not exactly"),
                       ((tip, "check-x.md", F.SCOPE, " accepted: yes"), "not exactly"),
                       ((tip, "check-x.md", F.SCOPE + " "), "scope"),
                       ((tip, "check-x.md", "scope: Layer 3 closure"), "scope"),
                       (("0" * 40,), "not a commit"),
                       ((F.commit_with(parent=F.root_commit()),), "ancestor")):
        path, sha = F.amendment_check(*args)
        _p, r = close(path, sha)
        assert r.returncode == 2 and want in r.stdout, "%s: %s" % (want, r.stdout)
    # a revision before a later change to an amendment file: every test file the amendment changed is compared (the
    # recheck's minor), and so is a script of the amendment; the test files its commits change are all listed
    sys.path.insert(0, AM)
    import l3amlib as LIB
    msgs = subprocess.run(["git", "-C", ROOT, "log", "--format=%H", "-i", "--grep=layer 3 amendment", "%s..HEAD" % LIB.BASE],
                          capture_output=True, text=True).stdout.split()
    changed = set()
    for c in msgs:
        changed |= set(subprocess.run(["git", "-C", ROOT, "diff-tree", "--no-commit-id", "--name-only", "-r", c],
                                      capture_output=True, text=True).stdout.split())
    changed |= set(subprocess.run(["git", "-C", ROOT, "diff", "--name-only", "HEAD"], capture_output=True, text=True).stdout.split())
    tests = sorted(x for x in changed if x.startswith("v2/ecad/tools/tests/"))
    assert tests and not set(tests) - set(LIB.AMENDMENT_FILES), "test files the amendment changed are not compared: %s" % (
        sorted(set(tests) - set(LIB.AMENDMENT_FILES)))
    for rel in tests + ["v2/docs/records/l3am/apply_l3am_r02.py"]:
        earlier = F.commit_with({rel: open(os.path.join(ROOT, rel), "rb").read() + b"# an earlier text\n"})
        later = F.commit_with(parent=earlier)
        path, sha = F.amendment_check(earlier)
        _p, r = close(path, sha, head=later)
        assert r.returncode == 2 and "changed since" in r.stdout and rel in r.stdout, "%s: %s" % (rel, r.stdout)
    # a check of the tip: accepted, and only checked_by, state and status change
    path, sha = F.amendment_check(tip)
    p, r = close(path, sha, check=False)
    assert r.returncode == 0, r.stdout
    before = yaml.safe_load(F.with_check(raw, path, sha)); after = yaml.safe_load(open(p, encoding="utf-8"))
    assert {k: v for k, v in after.items() if k != "review_findings"} == {k: v for k, v in before.items() if k != "review_findings"}
    a, b = before["review_findings"], after["review_findings"]
    assert sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k)) == ["checked_by", "state", "status"]
    assert b["state"] == "CLOSED" and b["checked_by"] == path
    r = _run([CLOSE, "--data", p, "--check-record", path, "--head", tip, "--check"])
    assert r.returncode == 2 and "has run" in r.stdout, r.stdout
    assert open(os.path.join(L3, "l3r2.yaml"), encoding="utf-8").read() == tree_raw, "the test changed the tree's l3r2.yaml"


# ------------------------------------------------------------------------------------------------ L3-R01
MARKS = re.compile(r"05 UTC|\bof 864\b|\bunserved\b")


def _sections(body):
    return re.split(r"(?m)^(?=#{1,6} )", body)


def t_l3am_every_solar_figure_names_its_case():
    """Every section of the three pages that states a solar-assisted figure (the stop hour, the energy unserved, the
    windows of 864) carries the label of l3r2.yaml's solar_case, and so do LAYER-STATUS.md's layer 3 section, the current
    owner brief, DEFINITION-STATUS.md's re-issue section and REQ-072's notes. The case names the pack, the load profile,
    the array, the voltage window and the stage limit, and section 2.3 prints each; its figures are runtime.out's, and a
    fixture with a figure changed, or a page section without its label, is refused. The baseline statement is the text
    the approved draft quotes (the figures and the evidence kept as written)."""
    RL, req, data = _tree()
    sc = RL.solar_case(data, req)
    assert sc and sc["proposal"] == "P-03" and sc["state"] == "HISTORICAL" and sc["pending"]["task"] == "L4-E2"
    pages = {n: open(os.path.join(L3, n), encoding="utf-8").read() for n in RL.PAGES.values()}
    for n, body in pages.items():
        for s in _sections(body):
            if MARKS.search(s): assert RL.SOLAR_KEY in s, "%s: %r states solar figures unlabelled" % (n, s[:80])
    sec23 = pages["REQUIREMENTS-L3-R2.md"].split("### 2.3 ", 1)[1].split("\n### ", 1)[0]
    for k in ("pack", "load_profile", "array", "voltage_window", "stage_limit"):
        assert RL.cell(sc[k]) in sec23, "section 2.3 does not state the case's %s" % k
    for q in sc["retained"]["quotes"]: assert q in sec23
    for v in sc["figures"].values(): assert v in sec23
    body = pages["OWNER-DECISIONS-L3.md"]
    cut = body.replace(RL.solar_caption(data, "of this row")[0], "", 1)
    assert cut != body
    try:
        RL.solar_guard("fixture", cut, data); raise AssertionError("a section without its label was not refused")
    except RL.RenderError:
        pass
    d2 = copy.deepcopy(data); d2["solar_case"]["figures"]["drawn_unserved_48_72"] = "266.7 / 400.0"
    try:
        RL.solar_case(d2); raise AssertionError("a figure that is not runtime.out's was not refused")
    except RL.RenderError:
        pass
    ls = open(os.path.join(ROOT, "v2/docs/handover/LAYER-STATUS.md"), encoding="utf-8").read()
    l3 = ls.split("## Layer 3. Requirements\n", 1)[1].split("\n### History: layer 3 at H2 and H3", 1)[0]
    for para in l3.split("\n\n"):
        if MARKS.search(para) or "meet at nominal inputs" in para: assert "proposal P-03's array" in para, para[:100]
    brief = open(os.path.join(L3, "OWNER-INSTRUCTION-2026-09-30.md"), encoding="utf-8").read()
    brief = " ".join(brief.split("## Current owner brief", 1)[1].split("\n## ", 1)[0].split())
    assert "05 UTC" in brief and "historical results of proposal P-03's array" in brief
    ds = open(os.path.join(ROOT, "v2/docs/handover/DEFINITION-STATUS.md"), encoding="utf-8").read()
    sec = ds.split("## Layer 3's definition re-issue", 1)[1].split("\n## ", 1)[0]
    assert "05 UTC" in sec and "proposal P-03's array" in sec
    r72 = next(r for r in req["records"] if r["id"] == "REQ-072")
    assert "proposal P-03's array" in " ".join(r72["notes"].split()) and "L4-E2" in r72["notes"]
    trace = open(os.path.join(ROOT, "v2/docs/REQUIREMENTS-TRACE.md"), encoding="utf-8").read()
    blk = trace.split("**REQ-072**", 1)[1].split("\n**REQ-", 1)[0]
    assert "05 UTC" in blk and "proposal P-03's array" in blk
    draft = open(os.path.join(L3, "DEFINITION-REISSUE-DRAFT.md"), encoding="utf-8").read()
    flat = " ".join(" ".join(l.lstrip("> ") for l in draft.split("\n")).split())
    assert " ".join(data["baseline_statement"].split()) in flat, "the baseline statement moved from the approved draft's text"


# ------------------------------------------------------------------------------------------------ L3-R02
def req042_defects(req, data):
    """What stops REQ-042's acceptance from being an end-to-end verification specification (L3-R02), as text."""
    r = next(x for x in req["records"] if x["id"] == "REQ-042")
    a = " ".join(str(r["acceptance"]).split())
    bad = []
    for s in re.split(r"(?<=\.)\s", a):
        if "S-49" in s and re.search(r"\b(met|satisfied|passes|closes)\b", s) and not re.search(r"\b(only|never|not)\b", s):
            bad.append("a sentence lets S-49 settle it: %s" % s[:100])
    for w in ("Stimulus and threshold basis", "States:", "from the moment the stimulus reaches the alarm level",
              "MASTER WARN", "both protection FETs", "until service", "channel by channel"):
        if w not in a: bad.append("no %r" % w)
    items = {x["id"]: x for x in req["open_items"]}
    lay = data.get("open_items_layer") or {}
    derive = [x for x in r.get("waits_on") or [] if x != "S-49" and x in items and str((lay.get(x) or {}).get("layer")) == "4"]
    if not derive: bad.append("no open item at layer 4 derives its levels")
    if "PROTOTYPE_MEASUREMENT" not in r["verification_method"] or r["final_phase"] != "PROTOTYPE":
        bad.append("its physical test is not downstream")
    return bad


def t_l3am_req042_is_not_satisfied_by_naming_a_part():
    """REQ-042's statement is H3's; its acceptance is channel by channel, end to end, and no sentence lets S-49's part
    settle it; it waits on a layer 4 item that derives the levels; S-49's title says it closes the selection only. With
    S-49 closed in a fixture the record still waits on that item and its acceptance still asks the test; the acceptance as
    it read before the correction is caught."""
    RL, req, data = _tree()
    r = next(x for x in req["records"] if x["id"] == "REQ-042")
    h3 = RL.load_h3()["records"]["REQ-042"]
    assert r["statement"] == h3["statement"] and r["prototype_1"] == h3["prototype_1"], "REQ-042's statement or scope moved"
    assert not req042_defects(req, data), req042_defects(req, data)
    s49 = next(x for x in req["open_items"] if x["id"] == "S-49")
    assert "its selection only" in s49["title"] and "nothing of REQ-042's acceptance" in " ".join(s49["title"].split())
    fx = copy.deepcopy(req)
    item = next(x for x in fx["open_items"] if x["id"] == "S-49")
    fx["open_items"].remove(item)
    fx["closed_items"].append(dict(item, status="CLOSED", closed_by="a fixture part"))
    assert not req042_defects(fx, data), "closing S-49 changed what REQ-042 asks"
    old = copy.deepcopy(req)
    next(x for x in old["records"] if x["id"] == "REQ-042")["acceptance"] = h3["acceptance"]
    assert req042_defects(old, data), "the acceptance as it read before the correction passes"


# ------------------------------------------------------------------------------------------------ L3-R05
def t_l3am_req016_window_kept_protection_judged_apart():
    """REQ-016's statement is the window D-34 retained, byte for byte H3's; its acceptance keeps the window's pass lines
    and judges protection apart under TRN-001 with the maker's breakdown and clamping figures, the bounded ESD result and
    the unresolved surge and over-voltage obligations, and no longer reads the breakdown onset under the capacitors as
    protection; the maker's sheet it cites is held, and TRN-001 is among the rules it names."""
    RL, req, data = _tree()
    r = next(x for x in req["records"] if x["id"] == "REQ-016")
    h3 = RL.load_h3()["records"]["REQ-016"]
    assert r["statement"] == h3["statement"], "REQ-016's statement moved"
    a = " ".join(r["acceptance"].split())
    old = " ".join(h3["acceptance"].split())
    head, tail = old.split("the panel input's clamp D4 is an SMCJ28A", 1)
    assert a.startswith(head) and tail.split(";", 1)[1] .split("Prototype:")[0].strip() in a
    for w in ("under rule TRN-001", "31.1 and 34.4 V at 1 mA", "45.4 V at its 33.1 A", "does not show that PV_P stays under 35 V",
              "0.005 and 0.010 V", "no level is ruled", "claims no surge or over-voltage protection"):
        assert w in a, "REQ-016's acceptance does not read %r" % w
    assert "conducting from 31.1 V, under the 35 V bulk capacitors" not in a
    assert "TRN-001" in r["satisfied_by"]["rules"]
    assert os.path.isfile(os.path.join(ROOT, "v2/vendor/power/littelfuse-smcj-series-tvs.pdf"))
    assert any(s.startswith("v2/vendor/power/littelfuse-smcj-series-tvs.pdf") for s in r["source"])


# ------------------------------------------------------------------------------------------------ the status and the scripts
def t_l3am_status_reads_the_review_until_it_is_closed():
    """While l3r2.yaml's review_findings is OPEN, LAYER-STATUS.md's layer 3 and the requirements page read "Layer 3
    accepted baseline; independent review findings open (L3-R01 to L3-R05)", kept apart from "design compliance verified"
    and "fab-ready"; each of the amendment's scripts refuses a second run; the review is filed at the sha it names."""
    RL, req, data = _tree()
    rf = data["review_findings"]
    assert RL.sha16_bytes(open(os.path.join(ROOT, rf["review"]), "rb").read()) == rf["sha16"]
    if rf["state"] == "OPEN":
        ls = open(os.path.join(ROOT, "v2/docs/handover/LAYER-STATUS.md"), encoding="utf-8").read()
        l3 = ls.split("## Layer 3. Requirements\n", 1)[1].split("\n### History", 1)[0]
        assert rf["status"] in l3 and "\"design compliance verified\"" in l3 and "\"fab-ready\"" in l3
        spec = open(os.path.join(L3, "REQUIREMENTS-L3-R2.md"), encoding="utf-8").read()
        assert rf["status"] in spec
    for s in ("apply_l3am_findings.py", "apply_l3am_r01.py", "apply_l3am_r02.py", "apply_l3am_r05.py",
              "apply_layer_status_l3am.py"):
        r = _run([os.path.join(AM, s), "--check"])
        assert r.returncode == 2 and "has run" in r.stdout, "a second run of %s was not refused:\n%s" % (s, r.stdout)
