"""Layer 3 round 5: the owner's reviewer's review of the decision brief, recorded as owner ruling D-26 (MESHSAT-1357,
30 September 2026).

The review's central finding: the decision logic confused a candidate's failure with an invalid owner requirement. These
tests hold what round 5 changes: D-26 recorded once with its six passages filed word for word; every option of the six
rows carrying the studied candidate's status and a feasibility disposition; the feasibility items defined with the files
their evidence is bound to; the bounded feasibility record of stream l3feas bound to its checked tip; the acceptance
definitions written into the prepared restatements (REQ-072 at the kit loads, REQ-078's full test conditions, REQ-051's
environment table, REQ-016's compliance apart from its topology); the reviewer's status levels; and the round 5 layer
status script, run on a copy of the page. The owner's addendum D-27: row L3-OD7 (M1's runtime) answered before rows
L3-OD1, L3-OD2, L3-OD4 and L3-OD6, whose scripts refuse until it is; the provenance of the 72 hours read from the registry.
The formerly refused combinations and the contradictions still refused are
tested in test_l3r2.py; the re-issue generator's semantics in test_l3r4.py. Nothing here writes into the tree.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
L3 = os.path.join(ROOT, "v2", "docs", "handover", "layer3")
REC5 = os.path.join(ROOT, "v2", "docs", "records", "l3r5")
COND = os.path.join(ROOT, "v2", "docs", "records", "l3r2", "conditional")
D26 = os.path.join(REC5, "apply_l3r5_d26.py")
D27 = os.path.join(REC5, "apply_l3r5_d27.py")
LSTAT = os.path.join(REC5, "apply_layer_status_l3_r5.py")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
sys.path.insert(0, L3)
from harness import need, Skip  # noqa: E402


def _run(args, cwd=None):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True, cwd=cwd or tempfile.gettempdir())


def _rl():
    import render_l3r2 as RL
    return RL


def t_l3r5_d26_is_recorded_once_with_its_six_passages():
    need(D26, "the D-26 script is not in this tree")
    sys.path.insert(0, REC5)
    import apply_l3r5_d26 as A
    import rules_lib as R
    req = R.load_requirements()
    r = next((x for x in req["owner_rulings"] if x["id"] == "D-26"), None)
    assert r is not None and r.get("title") == A.TITLE, "D-26 is not the review of the decision brief"
    instr = open(os.path.join(L3, "OWNER-INSTRUCTION-2026-09-30.md"), encoding="utf-8").read()
    flat = " ".join(line.lstrip("> ") for line in instr.split("\n"))
    for q in A.QUOTES:
        assert " ".join(q.split()) in " ".join(flat.split()), "a passage of the review is not filed word for word: %r" % q[:50]
    assert len(A.QUOTES) == 6
    out = _run([D26, "--check"])
    assert out.returncode == 2 and "has run" in out.stdout, "a second run of the D-26 script was not refused:\n%s" % out.stdout


def t_l3r5_every_option_shows_its_candidate_and_disposition():
    RL = _rl()
    data = RL.load_data()
    kinds = {"CREDIBLE", "CONDITIONAL", "INCONCLUSIVE", "NO_ROUTE", "OWED", "NONE"}
    for d in data["decisions"]:
        for o in d["options"]:
            assert o.get("status"), "%s %s shows no candidate status" % (d["id"], o["id"])
            assert (o.get("disposition") or {}).get("kind") in kinds, "%s %s has no feasibility disposition" % (d["id"], o["id"])
            assert "CANNOT MEET" not in str(o.get("flag")), "%s %s states a candidate's shortfall as a proof" % (d["id"], o["id"])
    ids = [x["id"] for x in data["feasibility_items"]]
    assert ids == ["FI-%02d" % n for n in range(1, 7)], "the feasibility items are not FI-01 to FI-06: %s" % ids
    for x in data["feasibility_items"]:
        assert x["disposition"]["kind"] in kinds - {"NONE"} and x.get("candidate") and x.get("target"), x["id"]
        for b in x["bound"]:
            assert os.path.isfile(os.path.join(ROOT, b)), "%s binds %s, which this tree does not hold" % (x["id"], b)
    page = open(os.path.join(L3, "OWNER-DECISIONS-L3.md"), encoding="utf-8").read()
    for fid in ids:
        assert "| %s |" % fid in page, "the decision page does not list %s, the feasibility records' page" % fid
    for name in ("OWNER-DECISIONS-L3.md", "REQUIREMENTS-L3-R2.md", "L3-RECONCILIATION.md"):
        body = open(os.path.join(L3, name), encoding="utf-8").read()
        assert "CANNOT MEET" not in body and "not self-consistent" not in body, \
            "%s states a candidate's shortfall as a proof or a contradiction" % name
    for a in data["acceptance_definitions"]:
        assert a["title"] in " ".join(page.split()) or a["title"][0].upper() + a["title"][1:] in page, a["label"]


def t_l3r5_the_feasibility_record_is_bound_to_its_checked_tip():
    import copy
    RL = _rl()
    data = RL.load_data()
    ok, why = RL.basis_ok(data, "feasibility_basis")
    assert ok, "the feasibility record is not bound to its checked tip: %s" % why
    for key, bad in (("sha16", "0" * 16), ("tip", "24942a5fed1936b01b569b4ac319ae0bc8265e6b")):
        d2 = copy.deepcopy(data)
        d2["feasibility_basis"][key] = bad
        assert not RL.basis_ok(d2, "feasibility_basis")[0], "a feasibility basis with its %s changed still binds" % key
    chk = RL.filed(data, "feasibility_checks")
    assert [c["verdict"] for c in chk] == ["NOT_ACCEPTED", "ACCEPTED"], "the two checks of stream l3feas are not filed"


def t_l3r5_the_acceptance_definitions_are_in_the_restatements():
    """The prepared scripts write the acceptance definitions (D-26): REQ-072's pass line at the kit loads, REQ-078's
    full test conditions with the push as a design target, REQ-051's environment table and its consequence, and REQ-016
    approved apart from its compliance (FI-06); the candidate's status stays beside each, never a PASS."""
    need(COND, "the conditional scripts are not in this tree")
    import yaml
    reg0 = os.path.join(TOOLS, "pcb_requirements.yaml")
    if any(str(r.get("decides") or "").startswith("L3-OD") for r in yaml.safe_load(open(reg0, encoding="utf-8"))["owner_rulings"]):
        raise Skip("rows are decided in this tree")
    d = tempfile.mkdtemp(prefix="l3r5-reg-")
    reg = os.path.join(d, "pcb_requirements.yaml")
    shutil.copy(reg0, reg)
    for s in (("od_l3_7.py", "72-required"), ("od_l3_6.py", "mean-day", "--build", "TYP"),
              ("od_l3_1.py", "approve", "--pass-line", "kit-loads"),
              ("od_l3_2.py", "qmx-out"), ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt", "--push-n", "10"),
              ("od_l3_5.py", "reading-c")):
        r = _run([os.path.join(COND, s[0]), "--option", s[1], "--words", "test words", "--date", "2026-10-01",
                  "--registry", reg] + list(s[2:]), cwd=d)
        assert r.returncode == 0, "%s --option %s exit %d:\n%s" % (s[0], s[1], r.returncode, (r.stdout + r.stderr)[-400:])
    y = yaml.safe_load(open(reg, encoding="utf-8"))
    R = {r["id"]: r for r in y["records"]}
    flat = lambda rid, f: " ".join(str(R[rid].get(f) or "").split())
    a72 = flat("REQ-072", "acceptance")
    for w in ("at the kit loads", "4.2 Wh", "8.7 A", "3.968 A", "7.936 A", "12.0 V", "ONE benchmark plane",
              "combined stored energy alone is not the line"):
        assert w in a72, "REQ-072's acceptance does not carry %r" % w
    req078 = next(r for r in y["records"] if r.get("parent") == "NEED-06" and r["id"] not in
                  {x["id"] for x in yaml.safe_load(open(reg0, encoding="utf-8"))["records"]})
    s78 = " ".join(req078["statement"].split())
    for w in ("100 degrees on its stay", "rigid flat surface", "static operator push of up to 10 N", "not a standard",
              "normal to the lid tablet's screen at its far edge"):
        assert w in s78, "the stability requirement does not carry %r" % w
    fea = [r for r in y["records"] if r.get("kind") == "feasibility" and r["id"] not in
           {x["id"] for x in yaml.safe_load(open(reg0, encoding="utf-8"))["records"]}]
    by = {r["blocker_ids"][0]: r for r in fea}
    assert set(by) == {"FI-05", "FI-06"}, "the recommended set records %s" % sorted(by)
    assert by["FI-05"]["evidence_result"] == "FAIL" and "6.1 N" in " ".join(by["FI-05"]["statement"].split()), \
        "a 10 N push on the QMX-out lid does not read FAIL against its 6.1 N"
    assert all(r["evidence_result"] != "PASS" for r in fea) and R["REQ-072"]["evidence_result"] == "FAIL"
    assert "environment table" in flat("REQ-051", "notes") and "reduces the claimed capability" in flat("REQ-051", "notes")


def t_l3r5_the_status_level_follows_the_answers():
    import copy
    import rules_lib as R
    RL = _rl()
    req, data, h3 = R.load_requirements(), RL.load_data(), RL.load_h3()
    lvl, s = RL.status_level(req, {}, data, h3)
    assert lvl is None and "None of the three levels holds yet" in s
    x = lambda o, **f: (o, "D-99", "2026-10-01", "", f)
    dec = {"L3-OD7": x("72-required"), "L3-OD1": x("reject"), "L3-OD3": x("2s2p"), "L3-OD4": x("reject"),
           "L3-OD5": x("reading-c"), "L3-OD6": x("mean-day", build="TYP", share=None)}
    lvl, s = RL.status_level(req, {k: v for k, v in dec.items() if k != "L3-OD7"}, data, h3)
    assert lvl is None, "decisions read recorded with row L3-OD7, M1's runtime, unanswered (D-27)"
    lvl, s = RL.status_level(req, dec, data, h3)
    assert lvl == "DRAFTED", "all rows settled (row L3-OD2 not applicable) do not read decisions recorded"
    g = RL.gate(req, dec, data, h3)
    assert not g[4][1] and "OWED" in g[4][2], "an owed disposition reads MET in the fifth condition"
    assert not g[3][1], "an acceptance of the handover with the decisions pending covers the decided issue"
    d2 = copy.deepcopy(data)
    d2["feasibility_basis"]["sha16"] = "0" * 16
    assert RL.status_level(req, dec, d2, h3)[0] is None, "decisions read recorded with the feasibility record unbound"


def t_l3r5_layer_status_restated_on_a_copy():
    need(LSTAT, "apply_layer_status_l3_r5.py is not in this tree")
    sys.path.insert(0, REC5)
    import apply_layer_status_l3_r5 as A
    page = os.path.join(ROOT, "v2", "docs", "handover", "LAYER-STATUS.md")
    t = open(page, encoding="utf-8").read()
    if A.MARK in t:
        r = _run([LSTAT, "--check"])
        assert r.returncode == 2 and "has run" in r.stdout, "a second run was not refused:\n%s" % r.stdout
        for old, new in reversed(A.EDITS): t = t.replace(new, old)
    cp = os.path.join(tempfile.mkdtemp(prefix="l3r5-ls-"), "LAYER-STATUS.md")
    open(cp, "w", encoding="utf-8").write(t)
    r = _run([LSTAT, "--page", cp])
    assert r.returncode == 0, "the page was not restated on a copy:\n%s" % r.stdout
    new = open(cp, encoding="utf-8").read()
    assert A.MARK in new and "Status level (the owner's reviewer's three, D-26)" in new
    back = new
    for old, nw in reversed(A.EDITS): back = back.replace(nw, old)
    assert back == t, "the page moved outside the restated texts"
    assert _run([LSTAT, "--page", cp]).returncode == 2, "a second run on the copy was not refused"


def t_l3r5_d27_is_recorded_once_with_the_addendum_quoted():
    need(D27, "the D-27 script is not in this tree")
    sys.path.insert(0, REC5)
    import apply_l3r5_d27 as A
    import rules_lib as R
    r = next((x for x in R.load_requirements()["owner_rulings"] if x["id"] == "D-27"), None)
    assert r is not None and r.get("title") == A.TITLE, "D-27 is not the owner's addendum"
    flat = " ".join(" ".join(l.lstrip("> ") for l in open(os.path.join(L3, "OWNER-INSTRUCTION-2026-09-30.md"),
                                                          encoding="utf-8").read().split("\n")).split())
    for q in A.QUOTES:
        assert '"%s"' % q in flat, "a paragraph of the addendum is not filed word for word: %r" % q[:50]
    assert A.QUOTES[1] in " ".join(str(r["ruling"]).split()), "the ruling does not carry the owner's words"
    out = _run([D27, "--check"])
    assert out.returncode == 2 and "has run" in out.stdout, "a second run of the D-27 script was not refused:\n%s" % out.stdout


def t_l3r5_the_72_hours_are_the_sessions_sc21_preserved_by_d20():
    """D-27: the provenance l3r2.yaml states is the registry's: SC-21 is the session's choice of 27 September 2026 under
    the standing rule and takes the 72 hours; D-20 preserves M1 and REQ-072 with their specified duration and states no
    figure; D-21's words carry "the approved 72-hour mission"; D-27 questions it."""
    import rules_lib as R
    req = R.load_requirements()
    sc = next(c for c in req["session_choices"] if c["id"] == "SC-21")
    assert sc["authority"] == "SESSION" and sc["under"] == "standing-rule" and sc["taken_on"] == "2026-09-27"
    assert "72 hours on the PS-IDLE-SPEC energy basis (42.8 W)" in " ".join(sc["taken"].split())
    rul = {x["id"]: " ".join(str(x["ruling"]).split()) for x in req["owner_rulings"]}
    assert "with their specified duration and operating conditions, are preserved" in rul["D-20"]
    assert not re.search(r"\b72\b", rul["D-20"]), "D-20 states a figure for M1's duration"
    assert "the approved 72-hour mission" in rul["D-21"] and "questioning the 72-hour requirement" in rul["D-27"]
    data = _rl().load_data()
    assert data["runtime_provenance"] == {"choice": "SC-21", "preserved_by": "D-20", "read_as_approved_under": "D-21",
                                          "questioned_by": "D-27", "record": None}, "the provenance is not the one read here"
    assert "SC-21" in " ".join(str(next(r for r in req["records"] if r["id"] == "REQ-072")["statement"]).split())


def t_l3r5_rows_1_2_4_and_6_wait_on_row_7():
    """D-27: no row asks the owner to remove a function or accept a deployment condition before row L3-OD7 is answered.
    On a copy: rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6 refuse while it is unanswered; row L3-OD5 does not wait; after
    48-required-72-desired or 72-required-battery-upgrade the four refuse until restated from the runtime comparison;
    after 72-required they apply, and REQ-072 names row L3-OD7's ruling in place of SC-21. Row L3-OD7 itself is held on
    the tree's registry until the runtime comparison is filed."""
    need(COND, "the conditional scripts are not in this tree")
    import yaml
    reg0 = os.path.join(TOOLS, "pcb_requirements.yaml")
    if any(str(r.get("decides") or "").startswith("L3-OD") for r in yaml.safe_load(open(reg0, encoding="utf-8"))["owner_rulings"]):
        raise Skip("rows are decided in this tree")
    def copy():
        d = tempfile.mkdtemp(prefix="l3r5-r7-")
        shutil.copy(reg0, os.path.join(d, "pcb_requirements.yaml"))
        return d, os.path.join(d, "pcb_requirements.yaml")
    def step(reg, d, script, opt, *extra):
        return _run([os.path.join(COND, script), "--option", opt, "--words", "test words", "--date", "2026-10-01",
                     "--registry", reg] + list(extra), cwd=d)
    d, reg = copy()
    for s in (("od_l3_1.py", "approve", "--pass-line", "kit-loads"), ("od_l3_1.py", "reject"), ("od_l3_2.py", "qmx-out"),
              ("od_l3_4.py", "reject"), ("od_l3_6.py", "mean-day", "--build", "TYP")):
        r = step(reg, d, *s)
        assert r.returncode == 2 and "presupposes row L3-OD7" in r.stdout, "%s answered before row L3-OD7:\n%s" % (s[0], r.stdout)
    assert step(reg, d, "od_l3_5.py", "reading-c").returncode == 0, "row L3-OD5 waits on row L3-OD7"
    for o in ("48-required-72-desired", "72-required-battery-upgrade"):
        d, reg = copy()
        assert step(reg, d, "od_l3_7.py", o).returncode == 0
        for s in (("od_l3_1.py", "reject"), ("od_l3_6.py", "mean-day", "--build", "TYP")):
            r = step(reg, d, *s)
            assert r.returncode == 2 and "restated from the runtime comparison" in r.stdout, "%s applied after %s" % (s[0], o)
        rec = {x["id"]: x for x in yaml.safe_load(open(reg, encoding="utf-8"))["records"]}["REQ-072"]
        st, acc = " ".join(rec["statement"].split()), " ".join(rec["acceptance"].split())
        if o.startswith("48"):
            assert "for 48 hours, M1's required duration" in st and "72 hours desired" in st and "for 48 hours" in acc
            assert "72 hours" not in acc, "REQ-072's acceptance keeps a 72 hour pass line under 48 hours required"
        else:
            assert "for M1's 72 hours (owner ruling" in st and "upgraded battery arrangement" in " ".join(rec["notes"].split())
        assert rec["evidence_result"] == "FAIL", "the runtime answer changed REQ-072's reading"
    d, reg = copy()
    assert step(reg, d, "od_l3_7.py", "72-required").returncode == 0
    assert step(reg, d, "od_l3_1.py", "approve", "--pass-line", "kit-loads").returncode == 0
    y = yaml.safe_load(open(reg, encoding="utf-8"))
    r7 = next(x["id"] for x in y["owner_rulings"] if str(x.get("decides")) == "L3-OD7:72-required")
    st = " ".join({x["id"]: x for x in y["records"]}["REQ-072"]["statement"].split())
    assert "72 hours (owner ruling %s on row L3-OD7)" % r7 in st and "SC-21" not in st, "row L3-OD1 restated the 72 hours as SC-21's"
    sys.path.insert(0, COND)
    import cond as C
    try:
        C.hold({"check": False, "registry": C.E.REGISTRY}, "L3-OD7")
    except C.E.Refused as e:
        assert "held (D-27)" in str(e) and "runtime_comparison" in str(e), str(e)
    else:
        raise AssertionError("row L3-OD7 would be written into the tree's registry before the runtime comparison is filed")


def t_l3r5_the_pages_ask_nothing_before_row_7():
    """The decision page lists row L3-OD7 first; rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6 read HELD (D-27) and their
    recommendations ask nothing until it is answered; a row L3-OD7 answer other than 72-required beside a decided row
    prepared for 72 hours reads as a contradiction, and 72-required clears the wait."""
    RL = _rl()
    data = RL.load_data()
    page = open(os.path.join(L3, "OWNER-DECISIONS-L3.md"), encoding="utf-8").read()
    rows = [l.split("|")[1].strip() for l in page.split("\n") if re.match(r"^\| L3-OD\d \|", l)]
    assert rows[:7] == ["L3-OD7", "L3-OD1", "L3-OD2", "L3-OD3", "L3-OD4", "L3-OD5", "L3-OD6"], rows[:7]
    for rid in RL.RUNTIME_ROWS:
        line = next(l for l in page.split("\n") if l.startswith("| %s |" % rid))
        cells = [c.strip() for c in line.split("|")]
        assert cells[5].startswith("**HELD (D-27)") and cells[9].startswith("HELD (D-27)"), "%s asks before row L3-OD7" % rid
    x = lambda o: (o, "D-99", "2026-10-01", "", {})
    assert RL.runtime_wait("L3-OD1", {"L3-OD7": x("72-required")}) == ""
    assert "restated from the runtime comparison" in RL.runtime_wait("L3-OD4", {"L3-OD7": x("48-required-72-desired")})
    why, ok = RL.coherent({"L3-OD7": x("48-required-72-desired"), "L3-OD1": x("approve")}, data)
    assert not ok and "L3-OD7" in why[0], "a 48 hour runtime beside a row prepared for 72 hours reads coherent"
    assert RL.coherent({"L3-OD7": x("48-required-72-desired"), "L3-OD5": x("reading-c")}, data)[1]
