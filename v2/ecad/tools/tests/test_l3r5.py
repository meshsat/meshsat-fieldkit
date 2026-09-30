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
    assert ids == ["FI-%02d" % n for n in range(1, 10)], "the feasibility items are not FI-01 to FI-09: %s" % ids
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
    for s in (("od_l3_7.py", "72-required", "--hf", "available", "--external", "no", "--tablet-charging", "no"),
              ("od_l3_6.py", "mean-day", "--build", "TYP"),
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
    assert set(by) == {"FI-05", "FI-06", "FI-08"}, "the recommended set records %s" % sorted(by)
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
    dec = {"L3-OD7": x("72-required", hf="available", external="no"), "L3-OD1": x("reject"), "L3-OD3": x("2s2p"), "L3-OD4": x("reject"),
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
    """D-27: the provenance l3r2.yaml states is the registry's and the filed comparison's: SC-21 is the session's choice of
    27 September 2026 under the standing rule and takes the 72 hours; D-20 preserves M1 and REQ-072 with their specified
    duration and states no figure; D-21's words carry "the approved 72-hour mission"; PROVENANCE.md, bound by its check,
    finds the figure first as SC-L2-05 at de59686e and its provenance as the owner's UNVERIFIED."""
    import rules_lib as R
    req = R.load_requirements()
    sc = next(c for c in req["session_choices"] if c["id"] == "SC-21")
    assert sc["authority"] == "SESSION" and sc["under"] == "standing-rule" and sc["taken_on"] == "2026-09-27"
    assert "72 hours on the PS-IDLE-SPEC energy basis (42.8 W)" in " ".join(sc["taken"].split())
    rul = {x["id"]: " ".join(str(x["ruling"]).split()) for x in req["owner_rulings"]}
    assert "with their specified duration and operating conditions, are preserved" in rul["D-20"]
    assert not re.search(r"\b72\b", rul["D-20"]), "D-20 states a figure for M1's duration"
    assert "the approved 72-hour mission" in rul["D-21"] and "questioning the 72-hour requirement" in rul["D-27"]
    RL = _rl()
    data = RL.load_data()
    pv = data["runtime_provenance"]
    assert (pv["choice"], pv["preserved_by"], pv["read_as_approved_under"], pv["questioned_by"]) == ("SC-21", "D-20", "D-21", "D-27")
    assert RL.basis_ok(data, "runtime_comparison")[0], "the comparison is not bound to its checked tip"
    rp = os.path.join(ROOT, pv["record"])
    assert pv["record"] in [o["path"] for o in data["runtime_comparison"]["outputs"]], "PROVENANCE.md is not bound by the check"
    prov = " ".join(open(rp, encoding="utf-8").read().split())
    for w in ("**Provenance of 72 hours as the owner's: UNVERIFIED.**", "SC-L2-05", "`de59686e`"):
        assert w in prov, "PROVENANCE.md does not read %r" % w
    assert pv["as_the_owners"] == "UNVERIFIED" and pv["first_appearance"] == "SC-L2-05 at de59686e"
    import rules_lib  # noqa: F401
    assert RL.closure_state(next(c for c in data["closure"] if c["id"] == "L3-C57"), req, {}, data) == "CLOSED"


def t_l3r5_row_7_is_filled_from_the_checked_comparison_by_exact_keys():
    """Row L3-OD7's table reads back equal to the filed runtime.out (runtime_reader.py), a second fill is refused, the
    comparison is bound to its checked tip, both checks are filed, and every figure row L3-OD7's prose states is printed
    as a whole token by the comparison's own files."""
    sys.path.insert(0, REC5)
    import fill_l3r7_from_comparison as FL
    RL = _rl()
    data = RL.load_data()
    row = next(d for d in data["decisions"] if d["id"] == "L3-OD7")
    out = next(o for o in data["runtime_comparison"]["outputs"] if o["path"].endswith("runtime.out"))
    tbl = FL.table(open(os.path.join(ROOT, out["path"]), encoding="utf-8").read())
    assert row["runtime_table"]["store"] == tbl["store"] and row["runtime_table"]["rows"] == tbl["rows"]
    r = _run([os.path.join(REC5, "fill_l3r7_from_comparison.py"), "--check"])
    assert r.returncode == 2 and "has run" in r.stdout, r.stdout
    assert [c["verdict"] for c in RL.filed(data, "runtime_checks")] == ["ACCEPTED", "ACCEPTED"]
    src = " ".join(" ".join(open(os.path.join(ROOT, "v2/docs/records/l3batt", f), encoding="utf-8").read().split())
                   for f in ("runtime.out", "COMPARISON.md", "SHORTLIST.md", "PROVENANCE.md"))
    prose = " ".join([row["owner_test"], row["recommendation"], row["consequences"]] +
                     [o["flag"] for o in row["options"]] + [o["text"] for s in row["subchoices"] for o in s["options"]])
    for num in sorted(set(re.findall(r"(?<![\w.])\+?(\d+\.\d+)(?= (?:Wh|h|W|kg|A|V)\b)", prose))):
        assert re.search(r"(?<![\d.])%s\b" % re.escape(num), src), "row L3-OD7 states %s, which the comparison does not print" % num
    sys.path.insert(0, COND)
    import cond as C
    assert C.runtime_figures() == tbl


def t_l3r5_row_7_comes_first_and_carries_its_answer():
    """D-27: rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6 refuse while row L3-OD7 is unanswered; row L3-OD5 does not wait. After
    48 hours with HF listening, the tablet charged and an external store at VBAT: REQ-072 states 48 hours, the receiver's
    load, the tablet's allowance and the external store; FI-07 and FI-09 are recorded; row L3-OD1 carries the answer; row
    L3-OD6 refuses until its table is restated; the QMX out is refused as a contradiction with HF listening; both lid items
    kept is recorded on FI-07, not refused. After 72 hours with no external store: FI-08 and M-02 carry it, and both kept
    records FI-04. Row L3-OD7 is held on the tree's registry only while the comparison is not bound (it is)."""
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
    def r7(reg, d, opt, hf, ext, tab):
        r = step(reg, d, "od_l3_7.py", opt, "--hf", hf, "--external", ext, "--tablet-charging", tab)
        assert r.returncode == 0, r.stdout[-400:]
    def fea(reg):
        return {x["blocker_ids"][0]: x for x in yaml.safe_load(open(reg, encoding="utf-8"))["records"] if x.get("kind") == "feasibility"
                and x["id"] >= "FEA-008"}
    d, reg = copy()
    for s in (("od_l3_1.py", "approve", "--pass-line", "kit-loads"), ("od_l3_1.py", "reject"), ("od_l3_2.py", "both-kept"),
              ("od_l3_4.py", "reject"), ("od_l3_6.py", "mean-day", "--build", "TYP")):
        r = step(reg, d, *s)
        assert r.returncode == 2 and "presupposes row L3-OD7" in r.stdout, "%s answered before row L3-OD7:\n%s" % (s[0], r.stdout)
    assert step(reg, d, "od_l3_5.py", "reading-c").returncode == 0, "row L3-OD5 waits on row L3-OD7"
    r = step(reg, d, "od_l3_7.py", "72-required", "--hf", "available", "--external", "maybe", "--tablet-charging", "no")
    assert r.returncode == 2 and "--external must be one of" in r.stdout, "an unknown sub-choice was taken"
    d, reg = copy()
    r7(reg, d, "48-required-72-desired", "listening", "authorise-vbat", "yes")
    f = fea(reg)
    assert set(f) == {"FI-07", "FI-09"} and f["FI-07"]["evidence_result"] == "INCONCLUSIVE"
    assert "+84.2 Wh usable at NOM and +122.2 at WE" in " ".join(f["FI-07"]["statement"].split())
    rec = {x["id"]: x for x in yaml.safe_load(open(reg, encoding="utf-8"))["records"]}["REQ-072"]
    st, acc = " ".join(rec["statement"].split()), " ".join(rec["acceptance"].split())
    for w in ("for 48 hours, M1's required duration", "72 hours desired", "the QMX receiver on through M1 (1.14 W more",
              "the tablet charged from the USB-C outlet", "external battery arrangement", "joined at VBAT"):
        assert w in st, "REQ-072's statement does not carry %r" % w
    assert "ends the 48 hours above" in acc and "72 hours" not in acc and rec["evidence_result"] == "FAIL"
    assert step(reg, d, "od_l3_1.py", "approve", "--pass-line", "kit-loads").returncode == 0
    rec = {x["id"]: x for x in yaml.safe_load(open(reg, encoding="utf-8"))["records"]}["REQ-072"]
    st, acc = " ".join(rec["statement"].split()), " ".join(rec["acceptance"].split())
    assert "the kit's two packs" in st and "for 48 hours, M1's required duration" in st and "SC-21" not in st
    assert "every hour of the 48 serves the load" in acc and "QMX receiver on" in acc and "external battery arrangement" in acc
    r = step(reg, d, "od_l3_6.py", "mean-day", "--build", "TYP")
    assert r.returncode == 2 and "restated from the runtime comparison" in r.stdout
    r = step(reg, d, "od_l3_2.py", "qmx-out")
    assert r.returncode == 2 and "cannot both hold" in r.stdout, "the QMX out was taken with HF listening"
    r = step(reg, d, "od_l3_2.py", "both-kept")
    assert r.returncode == 0, "both lid items kept, the owner's stated wish, was refused:\n%s" % r.stdout
    assert "FI-04" not in fea(reg), "both kept with an external store records FI-04 in place of FI-07"
    d, reg = copy()
    r7(reg, d, "72-required", "available", "no", "no")
    f = fea(reg)
    assert set(f) == {"FI-08"} and f["FI-08"]["evidence_result"] == "FAIL"
    y = yaml.safe_load(open(reg, encoding="utf-8"))
    assert "no external battery arrangement" in " ".join(next(x for x in y["open_items"] if x["id"] == "M-02")["title"].split())
    rid = next(x["id"] for x in y["owner_rulings"] if str(x.get("decides")).startswith("L3-OD7:"))
    st = " ".join({x["id"]: x for x in y["records"]}["REQ-072"]["statement"].split())
    assert "for M1's 72 hours (owner ruling %s on row L3-OD7)" % rid in st and "SC-21" not in st
    for s in (("od_l3_1.py", "approve", "--pass-line", "kit-loads"), ("od_l3_2.py", "both-kept")):
        assert step(reg, d, *s).returncode == 0
    assert "FI-04" in fea(reg), "both lid items kept without an external store records no FI-04"
    sys.path.insert(0, COND)
    import cond as C
    C.hold({"check": False, "registry": C.E.REGISTRY}, "L3-OD7")        # bound: not held


def t_l3r5_the_pages_ask_nothing_before_row_7():
    """The decision page lists row L3-OD7 first with its sub-choices and its table; rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6
    read HELD (D-27) and their recommendations ask nothing until it is answered; after it, only row L3-OD6 waits, and only
    after 48 hours or HF listening; the contradictions are row L3-OD6 beside those answers and the QMX out beside HF
    listening, while both lid items kept with or without an external store reads coherent."""
    RL = _rl()
    data = RL.load_data()
    page = open(os.path.join(L3, "OWNER-DECISIONS-L3.md"), encoding="utf-8").read()
    rows = [l.split("|")[1].strip() for l in page.split("\n") if re.match(r"^\| L3-OD\d \|", l)]
    assert rows[:7] == ["L3-OD7", "L3-OD1", "L3-OD2", "L3-OD3", "L3-OD4", "L3-OD5", "L3-OD6"], rows[:7]
    for rid in RL.RUNTIME_ROWS:
        line = next(l for l in page.split("\n") if l.startswith("| %s |" % rid))
        cells = [c.strip() for c in line.split("|")]
        assert cells[5].startswith("**HELD (D-27)") and cells[9].startswith("HELD (D-27)"), "%s asks before row L3-OD7" % rid
    line7 = next(l for l in page.split("\n") if l.startswith("| L3-OD7 |"))
    for w in ("`--hf`", "`--external`", "`--tablet-charging`", "`authorise-vbat`", "`authorise-dc-entry`"):
        assert w in line7, "row L3-OD7 does not show %s" % w
    assert "## Row L3-OD7's options, quantified" in page and "| 72 hours | WE |" in page
    x = lambda o, **f: (o, "D-99", "2026-10-01", "", f)
    b72 = {"L3-OD7": x("72-required", hf="available", external="no")}
    assert all(RL.runtime_wait(r, b72) == "" for r in RL.RUNTIME_ROWS)
    a48 = {"L3-OD7": x("48-required-72-desired", hf="available", external="authorise-vbat")}
    assert RL.runtime_wait("L3-OD4", a48) == "" and "restated from the runtime comparison" in RL.runtime_wait("L3-OD6", a48)
    lis = {"L3-OD7": x("72-required", hf="listening", external="no")}
    assert "restated" in RL.runtime_wait("L3-OD6", lis)
    assert not RL.coherent(dict(a48, **{"L3-OD6": x("mean-day", build="TYP")}), data)[1]
    assert not RL.coherent(dict(lis, **{"L3-OD1": x("approve"), "L3-OD2": x("qmx-out")}), data)[1]
    for ext in ("no", "authorise-vbat"):
        s = {"L3-OD7": x("72-required", hf="available", external=ext), "L3-OD1": x("approve"), "L3-OD2": x("both-kept")}
        assert RL.coherent(s, data)[1], "both lid items kept reads as a contradiction (external %s)" % ext
