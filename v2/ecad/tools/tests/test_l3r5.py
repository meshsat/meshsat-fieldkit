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
    import l3pre
    reg0 = l3pre.base_registry()
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
    # the property is CHECK-5's scope ("decisions pending"): judged with CHECK-5 the newest filed check, since later checks
    # of the closure (check 3 of round 5, accepted) are filed after it and the fourth condition follows the newest
    d5 = copy.deepcopy(data)
    d5["independent_check"] = [c for c in data["independent_check"] if "/l3r2/checks/" in c["record"]]
    assert d5["independent_check"][-1]["record"].endswith("check-l3r2-5.md")
    assert not RL.gate(req, dec, d5, h3)[3][1], "an acceptance of the handover with the decisions pending covers the decided issue"
    d2 = copy.deepcopy(data)
    d2["feasibility_basis"]["sha16"] = "0" * 16
    assert RL.status_level(req, dec, d2, h3)[0] is None, "decisions read recorded with the feasibility record unbound"


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
    assert pv["record"] == data["runtime_provenance_basis"]["record"] and RL.basis_ok(data, "runtime_provenance_basis")[0], \
        "PROVENANCE.md is not bound by the check that lists it"
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
    assert [c["verdict"] for c in RL.filed(data, "runtime_checks")] == ["ACCEPTED", "ACCEPTED", "ACCEPTED"]
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
    import l3pre
    reg0 = l3pre.base_registry()
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
    sys.path.remove(COND)




def _git_page(sha):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:v2/docs/handover/LAYER-STATUS.md" % sha], capture_output=True)
    if r.returncode != 0: raise Skip("the page at %s is not in this repository" % sha)
    return r.stdout.decode("utf-8")


def t_l3r5_layer_status_restated_on_a_copy():
    """Round 5's two layer status scripts, run in order on a copy of the page as the branch took it (a547fe1d): the
    first restates the gate for D-26 and D-27, the second writes the closure; each refuses a second run, and the tree's
    page carries both marks."""
    need(LSTAT, "apply_layer_status_l3_r5.py is not in this tree")
    LSTAT_B = os.path.join(REC5, "apply_layer_status_l3_r5b.py")
    sys.path.insert(0, REC5)
    import apply_layer_status_l3_r5 as A
    import apply_layer_status_l3_r5b as B
    tree = open(os.path.join(ROOT, "v2", "docs", "handover", "LAYER-STATUS.md"), encoding="utf-8").read()
    assert A.MARK in tree and B.MARK in tree, "the tree's page does not carry both of round 5's restatements"
    for s in (LSTAT, LSTAT_B):
        r = _run([s, "--check"])
        assert r.returncode == 2 and "has run" in r.stdout, "a second run of %s was not refused" % os.path.basename(s)
    cp = os.path.join(tempfile.mkdtemp(prefix="l3r5-ls-"), "LAYER-STATUS.md")
    base = _git_page("a547fe1d")
    open(cp, "w", encoding="utf-8").write(base)
    for s in (LSTAT, LSTAT_B):
        r = _run([s, "--page", cp])
        assert r.returncode == 0, "%s did not restate the copy:\n%s" % (os.path.basename(s), r.stdout)
        assert _run([s, "--page", cp]).returncode == 2, "a second run of %s on the copy was not refused" % os.path.basename(s)
    new = open(cp, encoding="utf-8").read()
    assert B.MARK in new and "No owner decision remains" in new and "| The target is unambiguous | MET |" in new
    assert "Completion statuses, kept apart" in new and B.WHOSE_NEW in new


def _instr():
    return open(os.path.join(L3, "OWNER-INSTRUCTION-2026-09-30.md"), encoding="utf-8").read()


def t_l3r5_the_closure_rulings_and_the_current_owner_brief():
    """D-28 to D-31 recorded once, each quoted word for word in the instruction file; the file opens with the current
    owner brief (at most about 40 lines), whose every ruling id exists in the registry, and the superseded instructions
    are marked in place, their text kept."""
    import rules_lib as R
    req = R.load_requirements()
    have = {r["id"]: r for r in req["owner_rulings"]}
    for rid in ("D-28", "D-29", "D-30", "D-31"):
        assert rid in have and have[rid]["authority"] == "OWNER", "%s is not recorded" % rid
    sys.path.insert(0, REC5)
    import apply_l3r5_d28_d29 as A
    import apply_l3r5_d30 as B
    import apply_l3r5_d31 as C
    flat = " ".join(" ".join(l.lstrip("> ") for l in _instr().split("\n")).split())
    for q in A.Q28 + A.Q29 + B.QUOTES + C.QUOTES:
        assert '"%s"' % " ".join(q.split()) in flat, "a paragraph is not filed word for word: %r" % q[:60]
    for s in ("apply_l3r5_d28_d29.py", "apply_l3r5_d30.py", "apply_l3r5_d31.py", "apply_l3r5_closure.py"):
        r = _run([os.path.join(REC5, s), "--check"])
        assert r.returncode == 2 and "has run" in r.stdout, "a second run of %s was not refused" % s
    text = _instr()
    heads = re.findall(r"^## (.+)$", text, re.M)
    assert heads[0].startswith("Current owner brief"), "the file does not open with the current owner brief"
    i = text.index("## Current owner brief"); j = text.index("\n## ", i + 5)
    brief = text[i:j]
    # 55 since round 5's fix round (the collaborator's closure check astra-check-l3r5-1, B1: the brief names the ASM and CHO
    # records one by one instead of two blanket lines, and B3: the line that the approved change record governs until the
    # documents' re-stamp); the brief stays one screen of 120-character lines.
    assert len(brief.strip().split("\n")) <= 55, "the brief runs to %d lines" % len(brief.strip().split("\n"))
    for rid in sorted(set(re.findall(r"\bD-\d\d\b", brief))):
        assert rid in have, "the brief names %s, which no ruling carries" % rid
    for w in ("NO external battery", "48 to 72 hours is a baseline design objective", "Owner decisions open:** none",
              "Samsung INR18650-35E"):
        assert w in " ".join(brief.split()), "the brief does not read %r" % w
    for mark in ("**Superseded in part by D-28:**", "**Superseded by D-28:**", "**Superseded in part:** the third passage"):
        assert mark in text, "a superseded instruction is not marked in place: %r" % mark
    assert "Preserve the approved 72-hour mission" in text, "a superseded instruction's text was removed"


def t_l3r5_the_closure_applied_to_the_registry():
    """Rows L3-OD2 to L3-OD7 answered by D-32 to D-37 with D-28's and D-29's words; REQ-072 the only design objective, its
    profile stated, its baseline read from the bound runtime.out, reading FAIL and not a BLOCKER; the store inside the
    Peli 1450 (REQ-014); the tablet's charging a capability at the outlet (REQ-011) with R138 named (REQ-017) as CHECK-3
    of stream l3batt states it; CFL-017 resolved and FEA-008 carrying the modes; M-02 closed by D-28."""
    import rules_lib as R
    sys.path.insert(0, REC5)
    import runtime_reader as RR
    req = R.load_requirements()
    recs = {r["id"]: r for r in req["records"]}
    dec = {str(r["decides"]).split(":")[0]: (str(r["decides"]).split(":")[1], r) for r in req["owner_rulings"]
           if str(r.get("decides") or "").startswith("L3-OD")}
    want = {"L3-OD7": "objective-48-72", "L3-OD2": "both-kept", "L3-OD3": "unchanged", "L3-OD4": "reject",
            "L3-OD5": "layer4-obligation", "L3-OD6": "mean-day"}
    assert {k: v[0] for k, v in dec.items()} == want, "the rows are not the closure's answers: %s" % dec
    assert [dec[r][1]["id"] for r in ("L3-OD7", "L3-OD2", "L3-OD3", "L3-OD4", "L3-OD5", "L3-OD6")] == ["D-%d" % n for n in range(32, 38)]
    r7 = dec["L3-OD7"][1]
    assert (r7["m1_hf"], r7["m1_external"], r7["m1_tablet_charging"]) == ("available", "no", "optional")
    assert dec["L3-OD6"][1]["weather_build"] == "TYP" and "L3-OD1" not in dec
    obj = [r["id"] for r in req["records"] if r.get("obligation") == "OBJECTIVE"]
    assert obj == ["REQ-072"], "the design objectives are %s" % obj
    r72 = recs["REQ-072"]
    assert r72["evidence_result"] == "FAIL" and r72["release_effect"] == "MUST_JUSTIFY" and "M-02" not in (r72.get("waits_on") or [])
    for w in ("PS-IDLE-SPEC, 42.8 W", "HF available and not receiving", "the tablet not charged", "one plane, 40 degrees facing south",
              "(WAB) a sensitivity", "not owner-approved operating restrictions"):
        assert w in " ".join(r72["objective_profile"].split()), "REQ-072's profile does not state %r" % w
    txt = open(os.path.join(ROOT, "v2/docs/records/l3batt/runtime.out"), encoding="utf-8").read()
    b, sol = RR.battery_only(txt), RR.solar(txt)
    ev = " ".join(str(r72["evidence"][-1]).split())
    for fig in (b["D06"]["hours_20"], b["A35"]["usable_20"], b["A35"]["hours_20"], sol[("48", "DRAWN", "TYP")]["unserved"],
                sol[("72", "NOM", "TYP")]["unserved"]):
        assert fig in ev, "REQ-072's baseline evidence does not carry %s from runtime.out" % fig
    assert "inside the Peli 1450 and no external battery" in " ".join(recs["REQ-014"]["statement"].split())
    a11 = " ".join(recs["REQ-011"]["acceptance"].split())
    assert a11.startswith("The charging capability is specified at the USB-C outlet, not by a tablet model") and \
        "no daily schedule is required" in a11
    chk = open(os.path.join(REC5, "checks/l3batt-check-3/CHECK-3.md"), encoding="utf-8").read()
    for rid in ("REQ-011", "REQ-017"):
        n = " ".join(str(recs[rid]["notes"]).split())
        assert "R138" in n and "1.92 to 2.26 A" in n and "1.92 to 2.26 A" in chk
    assert recs["CFL-017"]["status"] == "CONFLICT_RESOLVED" and "FEA-008" in recs["CFL-017"]["resolved_by"]
    f8 = recs["FEA-008"]
    assert f8["blocker_ids"] == ["LO-01a", "LO-01d", "LO-01e", "LO-01f", "LO-01g", "LO-01h"] and f8["release_effect"] == "MUST_JUSTIFY"
    closed = {x["id"]: x for x in req["closed_items"]}
    assert closed["M-02"]["closed_by"] == "D-28" and not any(x["id"] == "M-02" for x in req["open_items"])


def t_l3r5_an_objective_is_validated():
    """The validator (rules_lib) holds the obligation field: an objective never a BLOCKER, always with its profile, only
    a requirement; a profile on a mandatory record refused."""
    import copy
    import rules_lib as R
    req = R.load_requirements()
    for mutate, msg in ((lambda r: r.__setitem__("release_effect", "BLOCKER"), "never a BLOCKER"),
                        (lambda r: r.pop("objective_profile"), "states the operating profile")):
        q = copy.deepcopy(req)
        mutate(next(r for r in q["records"] if r["id"] == "REQ-072"))
        errs, _ = R.validate_requirements(q)
        assert any(msg in e for e in errs), "the validator did not refuse: %s" % msg
    q = copy.deepcopy(req)
    next(r for r in q["records"] if r["id"] == "REQ-014")["objective_profile"] = "a profile on a mandatory requirement"
    errs, _ = R.validate_requirements(q)
    assert any("not a design objective" in e for e in errs), "a profile on a mandatory record was taken"


def t_l3r5_cfl017_by_mode_and_the_cells_provenance():
    """Each quote of the cell's provenance is in its source; each mode's gap is the arithmetic of the figures beside it;
    the maker sheets as filed carry the limits the modes use (read with pdftotext), and OPERATING-ENVELOPE.md the rises."""
    RL = _rl()
    data = RL.load_data()
    for q in data["cell_provenance"]["quotes"]:
        src = "\n".join(l.lstrip("> ") for l in open(os.path.join(ROOT, q["source"]), encoding="utf-8").read().replace("**", "").split("\n"))
        assert " ".join(q["text"].split()) in " ".join(src.split()), "%s does not carry %r" % (q["source"], q["text"][:50])
    for m in data["cell_modes"]:
        if m.get("req_c") is None: continue
        gap = abs(float(m["req_c"]) - float(m["limit_c"]))
        forms = {"%.1f K" % gap, "%.2f K" % gap, "%d K" % round(gap)}
        assert any(f in m["gap"] for f in forms), "%s's gap %r is not %s" % (m["id"], m["gap"], sorted(forms))
    env = " ".join(open(os.path.join(ROOT, "v2/docs/OPERATING-ENVELOPE.md"), encoding="utf-8").read().split())
    for f in ("+62.1 C lid closed", "+61.6 to +74.2 C", "6.63 to 7.30", "13.16 to 14.47"):
        assert f in env, "OPERATING-ENVELOPE.md does not read %r" % f
    if shutil.which("pdftotext") is None: raise Skip("pdftotext is not installed")
    def sheet(name):
        out = subprocess.run(["pdftotext", "-layout", os.path.join(ROOT, "v2/vendor/battery", name), "-"], capture_output=True)
        return " ".join(out.stdout.decode("utf-8", "replace").split())
    v11, v10 = sheet("samsung-35e-orbtronic.pdf"), sheet("samsung-35e-akkuzentrum.pdf")
    for w in ("Ver. 1.1", "Charge : 0 to 45°C", "Discharge : -10 to 60°C", "1 year : -20~25°C", "3 months : -20~45°C",
              "1 month : -20~60°C", "(Cell Surface Temperature)"):
        assert w in v11, "the Ver. 1.1 sheet does not read %r" % w
    for w in ("Charge : 0 to 45°C (Ambient)", "Discharge : -10 to 60°C (Ambient)", "1 year : 0~23°C", "3 months : 0~45°C",
              "1 month : 0~60°C"):
        assert w in v10, "the Version 1.0 sheet does not read %r" % w


def t_l3r5_the_closure_pages_and_the_reissue():
    """The pages state the closure: row L3-OD7 first, the rows answered with their answers first, row L3-OD1 closed as
    layer 4 architecture, no owner decision left, the consolidated questions reconciled, the modelled baseline, the
    design risks, the cell modes and the completion statuses; the definition re-issue drafted and current."""
    RL = _rl()
    data = RL.load_data()
    page = open(os.path.join(L3, "OWNER-DECISIONS-L3.md"), encoding="utf-8").read()
    rows = [l.split("|")[1].strip() for l in page.split("\n") if re.match(r"^\| L3-OD\d \|", l)]
    assert rows[:7] == ["L3-OD7", "L3-OD1", "L3-OD2", "L3-OD3", "L3-OD4", "L3-OD5", "L3-OD6"], rows[:7]
    for rid in ("L3-OD7", "L3-OD2", "L3-OD3", "L3-OD4", "L3-OD5", "L3-OD6"):
        line = next(l for l in page.split("\n") if l.startswith("| %s |" % rid))
        cells = [c.strip() for c in line.split("|")]
        assert cells[5].startswith("**Answered (D-3") and cells[9].startswith("DECIDED"), "%s does not show its answer" % rid
    l1 = next(l for l in page.split("\n") if l.startswith("| L3-OD1 |"))
    assert "CLOSED AT LAYER 3 AS LAYER 4 ARCHITECTURE" in l1 and "**Closed as layer 4 architecture:**" in l1
    assert "## The closure (D-28, D-29): the owner decision left" in page and "None. CFL-017" in page
    for q in data["consolidated_questions"]:
        assert "| %s |" % q["q"] in page, "%s is not reconciled on the page" % q["q"]
    spec = open(os.path.join(L3, "REQUIREMENTS-L3-R2.md"), encoding="utf-8").read()
    for h in ("### 2.2 Mandatory requirements and the design objective (D-28)", "### 2.3 The modelled baseline",
              "### 2.4 Design risks, assigned", "### 2.5 CFL-017 by mode", "### 2.6 Completion statuses, kept apart"):
        assert h in spec, "the requirements page has no %r" % h
    assert "#### REQ-072 (requirement, design objective," in spec and "#### REQ-014 (requirement, mandatory," in spec
    assert "| Target unambiguous | MET |" in spec and "| Requirement-changing owner decisions resolved | MET |" in spec
    lvl = RL.status_level(__import__("rules_lib").load_requirements(), RL.decided(__import__("rules_lib").load_requirements(), data),
                          data, RL.load_h3())[0]
    assert lvl == "DRAFTED", "the closure does not read requirements drafted and decisions recorded"
    for s in ([os.path.join(ROOT, "v2/docs/records/l3r4/reissue.py"), "--check"],
              [os.path.join(ROOT, "v2/docs/records/l3r4/reissue.py"), "--map", "--check"]):
        r = _run(s, cwd=ROOT)
        assert r.returncode == 0 and "current" in r.stdout, "the re-issue is not current:\n%s" % r.stdout
    draft = open(os.path.join(L3, "DEFINITION-REISSUE-DRAFT.md"), encoding="utf-8").read()
    for pid in ("S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "S10", "S11"):
        assert "### %s. " % pid in draft, "the draft does not restate %s" % pid
    assert "48 to 72 hours, a design objective" in draft and "72 hours required" not in draft
    x = lambda o, **f: (o, "D-99", "2026-10-01", "", f)
    a48 = {"L3-OD7": x("48-required-72-desired", hf="available", external="no")}
    assert not RL.coherent(dict(a48, **{"L3-OD6": x("mean-day", build="TYP")}), data)[1]
    obj = {"L3-OD7": x("objective-48-72", hf="available", external="no")}
    assert RL.coherent(dict(obj, **{"L3-OD6": x("mean-day", build="TYP"), "L3-OD2": x("both-kept")}), data)[1]
    assert RL.settled("L3-OD1", obj, data) and not RL.settled("L3-OD1", a48, data), "row L3-OD1's closure is not the closure's"


def t_l3r5_fix_round_superseded_conditions_are_marked_where_they_stand():
    """The collaborator's closure check astra-check-l3r5-1, B2: the 72 hours of SC-21 and the deployment conditions are no
    longer classified as requirements in the current views. SC-21 is marked superseded in the registry by D-28 (applied as
    D-32), its taken value and L-02 kept, and the mark is printed on the trace page and in the operating conditions; the
    two classification rows keep their place marked SUPERSEDED with what holds now; D-21's quoted instruction carries its
    mark; acceptance definitions 1b and 4b are marked; the supersession script refuses a second run. No current view
    classifies 72 hours or a deployment condition as a REQUIREMENT."""
    import rules_lib as R
    RL = _rl()
    req, data = R.load_requirements(), RL.load_data()
    sc = next(c for c in req["session_choices"] if c["id"] == "SC-21")
    assert sc.get("superseded_on") == "2026-09-30" and "D-32" in str(sc.get("superseded_by")) and sc.get("closes") == ["L-02"]
    assert "72 hours on the PS-IDLE-SPEC energy basis (42.8 W)" in " ".join(sc["taken"].split())
    spec = open(os.path.join(L3, "REQUIREMENTS-L3-R2.md"), encoding="utf-8").read()
    rec = open(os.path.join(L3, "L3-RECONCILIATION.md"), encoding="utf-8").read()
    dec_page = open(os.path.join(L3, "OWNER-DECISIONS-L3.md"), encoding="utf-8").read()
    trace = open(os.path.join(ROOT, "v2", "docs", "REQUIREMENTS-TRACE.md"), encoding="utf-8").read()
    assert "**SUPERSEDED on 2026-09-30 by D-28 (applied as D-32):** 72 hours on the PS-IDLE-SPEC energy basis" in spec
    assert "SUPERSEDED 2026-09-30 by D-28 (applied as D-32): 72 hours on the PS-IDLE-SPEC" in trace
    assert "**Superseded in part by D-28 (applied as D-32):" in spec, "D-21's quoted instruction carries no mark"
    for c in data["classification"]:
        text = " ".join(c["item"].split())
        if ("72 hours" in text and "48 to 72" not in text) or "deployment conditions" in text:
            assert c.get("superseded_by") and c.get("now"), "%r is still classified %s" % (text[:60], c["level"])
    assert "| SUPERSEDED by D-28, applied as D-32 (30 September 2026) (was REQUIREMENT (layer 3)):" in rec
    assert "| SUPERSEDED by D-28, applied as D-35 (30 September 2026) (was REQUIREMENT (layer 3)):" in rec
    assert "| DESIGN OBJECTIVE (layer 3) |" in rec
    for label in ("1b", "4b"):
        a = next(x for x in data["acceptance_definitions"] if x["label"] == label)
        assert a.get("superseded_by") and "**Superseded by %s:**" % a["superseded_by"] in dec_page
    assert "72 hours today" not in dec_page and "(REQ-072 today)" not in dec_page
    r = _run([os.path.join(REC5, "apply_l3r5_supersede_sc21.py"), "--check"])
    assert r.returncode == 2 and "has run" in r.stdout, "a second run of the SC-21 script was not refused:\n%s" % r.stdout


def t_l3r5_fix_round_the_brief_the_reissue_and_the_gate():
    """The collaborator's closure check astra-check-l3r5-1 (accepted: no) is filed byte for byte and named NOT_ACCEPTED,
    so the gate's fourth condition reads NOT MET until the targeted recheck is filed. B1: the brief names the ASM and CHO
    records one by one with the rulings that bind them. B3: D-38 records the owner's closure instructions word for word
    and decides the re-issue; definition_reissue names the change record at its sha with D-38; the record states the route
    that holds (authority D-38, acceptance the targeted review) and no PROPOSED; L3-C26 reads CLOSED and the gate's third
    condition MET; the re-stamp is L3-C63, the integrator's, OPEN; the brief, the requirements page, DEFINITION-STATUS.md and
    LAYER-STATUS.md say the change record governs until the re-stamp; CFL-016 is rebound to the status page it reads.
    M1: DR-03 names 15 V. Each fix-round script refuses a second run, and the approved re-issue reads current."""
    import rules_lib as R
    RL = _rl()
    req, data = R.load_requirements(), RL.load_data()
    # The first check is no longer the last filed: its targeted recheck astra-check-l3r5-2 (accepted: no) is filed after
    # it (the second fix round, t_l3r5_recheck_decided_rows_carry_no_option_they_did_not_take), so the first is found by
    # its record rather than by its place.
    chk = next(c for c in data["independent_check"] if c["record"].endswith("astra-check-l3r5-1.md"))
    assert chk["verdict"] == "NOT_ACCEPTED"
    assert open(os.path.join(ROOT, chk["record"]), encoding="utf-8").readline().strip() == "accepted: no"
    flat = " ".join(_instr().split("## Current owner brief", 1)[1].split("\n## ", 1)[0].split())
    for w in ("ASM-006 carries owner ruling D-02e's operating condition \"operate shaded\"", "CHO-001, the device set, is the owner's ruling",
              "the one replaceable selection these rulings establish", "the change record governs (D-38)",
              "**The definition re-issue** is authorised by his closure instructions D-38"):
        assert w in flat, "the brief does not read %r" % w
    for w in ("the registry's ASM records. ", "the registry's CHO records. "):
        assert w not in flat, "the brief still carries the blanket line %r" % w
    instr = " ".join(" ".join(l.lstrip("> ") for l in _instr().split("\n")).split())
    r38 = next(x for x in req["owner_rulings"] if x["id"] == "D-38")
    sys.path.insert(0, REC5)
    import apply_l3r5_d38 as A
    assert str(r38.get("decides")) == "definition_reissue" and len(A.QUOTES) == 3
    for q in A.QUOTES:
        assert " ".join(q.split()) in instr and " ".join(q.split()) in " ".join(r38["ruling"].split()), "a quote is not word for word"
    assert "The session's reading, not his words" in " ".join(r38["ruling"].split())
    dr = data["definition_reissue"]
    assert dr["approved_by"] == "D-38" and dr["record"].endswith("DEFINITION-CHANGE-RECORD-L3.md")
    assert RL.sha16_bytes(open(os.path.join(ROOT, dr["record"]), "rb").read()) == dr["sha16"]
    dec = RL.decided(req, data)
    assert RL.reissue_ok(req, data, dec)[0], RL.reissue_ok(req, data, dec)[1]
    items = {c["id"]: c for c in data["closure"]}
    assert RL.closure_state(items["L3-C26"], req, dec, data) == "CLOSED"
    assert items["L3-C63"]["whose"] == "INTEGRATOR" and RL.closure_state(items["L3-C63"], req, dec, data) == "OPEN"
    g = RL.gate(req, dec, data, RL.load_h3())
    # the fourth condition follows the newest filed check: NOT MET while the fix round's recheck (not accepted) was the
    # newest, MET once check 3 (accepted) is filed after it
    newest_ok = str(data["independent_check"][-1]["verdict"]).upper() == "ACCEPTED"
    assert g[2][1] and g[3][1] is newest_ok, "the third condition should read MET and the fourth follow the newest check: %s" % [(x[0], x[1]) for x in g]
    record = open(os.path.join(ROOT, dr["record"]), encoding="utf-8").read()
    assert "AUTHORISED by owner ruling D-38" in record and "**Acceptance:** the targeted independent review" in record
    assert "PROPOSED" not in record, "the approved record still reads PROPOSED"
    spec = open(os.path.join(L3, "REQUIREMENTS-L3-R2.md"), encoding="utf-8").read()
    assert "the change record governs" in spec and "| Contradictions and requirement-level TBDs closed | MET |" in spec
    assert "on the 5, 9 and 15 V contracts" in spec, "DR-03 does not name the 15 V contract"
    ds = open(os.path.join(ROOT, "v2", "docs", "handover", "DEFINITION-STATUS.md"), encoding="utf-8").read()
    assert "the change record governs" in ds and "| DC-L3-M1 |" in ds
    cfl = next(r for r in req["records"] if r["id"] == "CFL-016")
    assert "v2/docs/handover/DEFINITION-STATUS.md@%s" % RL.sha16_bytes(ds.encode("utf-8")) in cfl["evidence_bound_to"]
    ls = open(os.path.join(ROOT, "v2", "docs", "handover", "LAYER-STATUS.md"), encoding="utf-8").read()
    assert "waits on the owner's approving ruling" not in ls and "L3-C63" in ls
    for s in ("apply_l3r5_d38.py", "apply_definition_status_l3r5.py", "apply_layer_status_l3_r5c.py"):
        r = _run([os.path.join(REC5, s), "--check"])
        assert r.returncode == 2 and "has run" in r.stdout, "a second run of %s was not refused:\n%s" % (s, r.stdout)
    r = _run([os.path.join(ROOT, "v2/docs/records/l3r4/reissue.py"), "--check"], cwd=ROOT)
    assert r.returncode == 0 and "current" in r.stdout, "the approved re-issue does not read current:\n%s" % r.stdout


# The recheck's closure criterion (astra-check-l3r5-2, B2), held on the structures and not on the strings the earlier
# fixes searched for. For each option a decided row did NOT take: its id where it names the option (an id with a hyphen
# or a digit anywhere, case-sensitive; a common word only backticked on a line that names the row) and the words by
# which its prepared restatement stated a requirement change. The words are the collaborator's (a deployment band, a
# ground slope, a push) and the stale entries' own; an option's text is allowed only where the same entry names the
# ruling that did not take it.
UNTAKEN_WORDS = {
    ("L3-OD7", "72-required"): ("72 hours required",),
    ("L3-OD7", "48-required-72-desired"): ("48 hours required",),
    ("L3-OD2", "qmx-out"): ("QMX clause is removed", "no HF bearer in the kit", "HF leaves the kit", "8 inch tablet",
                            "narrows to 8 inch"),
    ("L3-OD2", "qmx-outside"): ("sealed case-wall lead", "QMX carried outside"),
    ("L3-OD2", "tablet-out"): ("tablet bracket leaves the lid", "the bracket drawn or dropped"),
    ("L3-OD3", "2s2p"): ("REQ-016 restated", "200 W in 2S2P"),
    ("L3-OD3", "1s4p"): ("REQ-016 restated",),
    ("L3-OD4", "adopt"): ("deployment band", "plane band", "band's least-energy plane", "ground slope", "operator push",
                          "slope and push", "REQ-078"),
    ("L3-OD5", "reading-c"): ("reading of D-02a", "without its cells"),
    ("L3-OD5", "measure"): ("open until the heat experiment",),
    ("L3-OD5", "cells"): ("cells rated above +60 C",),
    ("L3-OD6", "coverage"): ("coverage target", "coverage window"),
}


def _untaken_hits(text, row, taken, options):
    """The words of the options of `row` other than `taken` that `text` carries."""
    hits = []
    for o in options:
        if o == taken: continue
        if re.search(r"[-\d]", o):
            if re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(o), text): hits.append(o)
        elif "`%s`" % o in text and re.search(r"\b%s\b" % re.escape(row), text):
            hits.append(o)
        for w in UNTAKEN_WORDS.get((row, o), ()):
            if w.lower() in text.lower(): hits.append(w)
    return hits


def _section(body, start, end):
    a = body.index(start)
    b = body.index(end, a + len(start)) if end else len(body)
    return body[a:b].split("\n")


def _current_view_cells(pages):
    """[(where, text)] of the current views the criterion names, each unit being what must carry its own mark: in the
    change table (6.1) the Why cell; in the downstream table (7) the Why cell and the Impact cell apart, and the note on
    what is left out; in the execution questions the note cell; in the reconciliation (L3-RECONCILIATION.md) the decided
    target's lines, the settled rows' line, and every table row and line of (b) to (d). The evidence blocks of (a) (the
    facts, the basis's figures and the four cases, bound to their checked tips) are the checked basis's, not a target."""
    spec, rec = pages["REQUIREMENTS-L3-R2.md"], pages["L3-RECONCILIATION.md"]
    out = []
    for l in _section(spec, "### 6.1 Baseline changes", "### 6.2"):
        if l.startswith("| ") and not l.startswith("| Record") and not l.startswith("|---"):
            c = [x.strip() for x in l.split("|")]
            out.append(("6.1 %s why" % c[1], c[4]))
    for l in _section(spec, "## 7. Downstream impacts by layer", "## 8."):
        if l.startswith("| ") and not l.startswith("| Layer") and not l.startswith("|---"):
            c = [x.strip() for x in l.split("|")]
            out += [("7 %s %s why" % (c[1], c[2]), c[3]), ("7 %s %s impact" % (c[1], c[2]), c[4])]
        elif l.startswith("Not in the table"):
            out.append(("7 left out", l))
    lines = rec.split("\n")
    a0, b0 = lines.index("## (a) The current target configuration"), lines.index("## (b) Every requirement-changing proposal since H3")
    for l in lines[a0:b0]:
        if l.startswith("- L3-OD") or l.startswith("**The other answers") or l.startswith("**Under the other answers") or \
                l.startswith("**Decided so far"):
            out.append(("recon (a)", l))
    exq = False
    for l in lines[b0:]:
        if l.startswith("| Question | Row | What changed |"): exq = True; continue
        if exq and l.startswith("| Q"):
            c = [x.strip() for x in l.split("|")]
            out.append(("execution %s note" % c[1], c[3])); continue
        if exq and not l.startswith("|"): exq = False
        if l.strip() and not l.startswith("|---"): out.append(("recon", l))
    return out


def _stale(req, data, pages):
    """Every place the criterion fails, as text; [] when it holds."""
    RL = _rl()
    dec = RL.decided(req, data)
    rows = {d["id"]: [o["id"] for o in d["options"]] for d in data["decisions"]}
    bad = []
    # 1. every impacts entry names in `rows` each row its why names, and names the ruling of each decided row (the
    #    proposal of each row closed as a later layer's)
    for rid, e in (data.get("impacts") or {}).items():
        why = " ".join(str(e.get("why")).split())
        named = set(RL.ROW_RX.findall(why))
        if not named <= set(e.get("rows") or []):
            bad.append("impacts %s names %s in its why but not in rows" % (rid, sorted(named - set(e.get("rows") or []))))
        for r in sorted(named | set(e.get("rows") or [])):
            m = RL.row_mark(r, dec, data)
            if m and m not in why: bad.append("impacts %s names row %s without %s" % (rid, r, m))
    # 2. every execution question whose row is settled names the row's mark in its own note
    for q in data.get("execution_plan_questions") or []:
        m = RL.row_mark(q["row"], dec, data)
        if m and m not in q["note"]: bad.append("execution question %s (row %s) does not name %s" % (q["q"], q["row"], m))
    # 3. no current view carries an option a decided row did not take, unless the same unit names that row's ruling
    for where, text in _current_view_cells(pages):
        for r, v in dec.items():
            hits = _untaken_hits(text, r, v[0], rows[r])
            if hits and v[1] not in text:
                bad.append("%s carries %s of row %s without %s: %s" % (where, hits, r, v[1], text[:120]))
    # 4. the downstream table shows no record of a settled row as pending, and a row closed as layer 4 as its proposal
    spec = pages["REQUIREMENTS-L3-R2.md"]
    for rid, e in (data.get("impacts") or {}).items():
        rs = e.get("rows") or []
        if rs and all(RL.settled(r, dec, data) for r in rs) and "| %s (if decided) |" % rid in spec:
            bad.append("%s renders (if decided) with every row it names settled" % rid)
        closed = [r for r in rs if RL.closed_row(r, dec, data)]
        if closed and "| %s (applied) |" % rid not in spec and \
                "| %s (layer 4 proposal %s, not applied) |" % (rid, RL.row_mark(closed[0], dec, data)) not in spec:
            bad.append("%s is tied to %s but does not render as its layer 4 proposal" % (rid, closed[0]))
    return bad


def t_l3r5_recheck_decided_rows_carry_no_option_they_did_not_take():
    """The recheck astra-check-l3r5-2 (accepted: no) failed B2 a second time: the stale text sat in l3r2.yaml structures
    written option-neutral before the owner answered, not in the literals the earlier fixes searched for. Its closure
    criterion, held structurally: for every decided row, the rendered current views (the change table, the downstream
    table, the execution questions and the reconciliation) carry no text of an option the ruling did not take unless
    the same entry names that ruling; every impacts entry that names a decided row names its ruling (row L3-OD1, closed
    as layer 4 architecture, its proposal P-01); the downstream table shows no settled row's record as pending. A
    fixture copy with one stale entry, the REQ-072 entry as it read before this fix, fails; so does a stale execution
    question. The recheck is filed byte for byte and named NOT_ACCEPTED next to the first check."""
    import copy
    import rules_lib as R
    RL = _rl()
    req, data = R.load_requirements(), RL.load_data()
    pages = {n: open(os.path.join(L3, n), encoding="utf-8").read() for n in RL.PAGES.values()}
    bad = _stale(req, data, pages)
    assert not bad, "the current views carry options their rulings did not take:\n  %s" % "\n  ".join(bad[:12])
    dec = RL.decided(req, data)
    assert RL.row_tag("L3-OD1", dec, data) == "L3-OD1, closed as layer 4 architecture (P-01)"
    assert "| REQ-075 (layer 4 proposal P-01, not applied) |" in pages["REQUIREMENTS-L3-R2.md"]
    assert "REQ-016 not changed (D-34)" in pages["REQUIREMENTS-L3-R2.md"] and "REQ-078 not added (D-35)" in pages["REQUIREMENTS-L3-R2.md"]
    # D-22's supply-range rule is carried by a record (the gap the author raised on this fix): its classification row
    # names REQ-072, and REQ-072's desk acceptance carries the clause, written once by its apply script
    row = next(c for c in data["classification"] if c["item"].startswith("The rule that an M1 energy claim holds across"))
    assert row["level"] == "REQUIREMENT" and "REQ-072" in row["where"] and "D-22" in row["where"], row["where"]
    r72 = next(r for r in req["records"] if r["id"] == "REQ-072")
    a72 = " ".join(r72["acceptance"].split())
    assert "with the charge bus at U3's input (VBUS20) at its lowest established steady-state voltage" in a72 and \
        "every load-holding limit at its minimum" in a72 and "(D-22: " in a72 and "D-22" in r72["rulings"], \
        "REQ-072's acceptance does not carry D-22's clause"
    r = _run([os.path.join(REC5, "apply_l3r5_d22_req072.py"), "--check"])
    assert r.returncode == 2 and "has run" in r.stdout, "a second run of the D-22 script was not refused:\n%s" % r.stdout
    # the fixtures: one stale entry each, rendered in memory from a copy of l3r2.yaml; the tree is not written
    stale72 = ("L3-OD1, L3-OD3, L3-OD4 and L3-OD6: two packs, the array (row L3-OD3), the supply range and the 3.00 V floor, "
               "the deployment band, the weather basis (the benchmark's limitations in its notes, or a coverage target)")
    for name, edit in (
            ("REQ-072's why as it read before", lambda d: d["impacts"]["REQ-072"].update(why=stale72)),
            ("REQ-072's layer 9 on the band", lambda d: d["impacts"]["REQ-072"]["layers"].update(
                {9: "REQ-072's prototype run with an array emulator on the band's least-energy plane"})),
            ("Q4's note as it read before", lambda d: next(q for q in d["execution_plan_questions"] if q["q"] == "Q4").update(
                note="the deployment rule: the plan's '20 to 50 degrees' is superseded; the band comes from the checked "
                     "energy basis, and the open kit's slope and push are added")),
            ("REQ-016 without its rows", lambda d: d["impacts"]["REQ-016"].pop("rows"))):
        d2 = copy.deepcopy(data)
        edit(d2)
        keep = RL.load_data
        RL.load_data = lambda: copy.deepcopy(d2)
        try:
            p2 = RL.render_all()
        finally:
            RL.load_data = keep
        assert _stale(req, d2, p2), "a fixture with %s passes the check" % name
    chk = [c for c in data["independent_check"] if "astra-check-l3r5" in c["record"]]
    assert [os.path.basename(c["record"]) for c in chk] == ["astra-check-l3r5-1.md", "astra-check-l3r5-2.md"]
    assert [c["verdict"] for c in chk] == ["NOT_ACCEPTED", "NOT_ACCEPTED"]
    src = os.path.join(ROOT, chk[-1]["record"])
    assert open(src, encoding="utf-8").readline().strip() == "accepted: no"
    assert RL.sha16_bytes(open(src, "rb").read()) == chk[-1]["sha16"]
    # judged with the recheck the newest filed check (check 3, accepted, is filed after it at the closure)
    dr2 = copy.deepcopy(data)
    k = [i for i, c in enumerate(data["independent_check"]) if c["record"].endswith("astra-check-l3r5-2.md")][0]
    dr2["independent_check"] = data["independent_check"][:k + 1]
    g = RL.gate(req, dec, dr2, RL.load_h3())
    assert not g[3][1], "the fourth condition reads MET with the recheck not accepted"


# The owner's clarification on B2, relayed by the coordinator on 30 September 2026: "Historical descriptions of rejected
# lid options may remain. An entry passes only when its current status accurately reflects the applicable ruling. Merely
# mentioning D-33 must not excuse contradictory current text or an option still presented as awaiting a decision."
HISTORY_MARK = re.compile(r"\b(?:was|were) not (?:taken|adopted)\b|\bnot added\b|\bnot applied\b|\bsuperseded\b", re.I)
ANSWERED = re.compile(r"\brow (L3-OD\d) answered ([\w-]+) \((D-\d+)\)")


def _status_units(data, pages):
    """The units whose current status is judged: every impacts entry's why, the 6.1 why cells, the section 7 why and
    impact cells (and its left-out line), and the execution questions' notes, as l3r2.yaml holds them and as rendered.
    The reconciliation's proposal table is history by design and is not among them."""
    out = [(w, t) for w, t in _current_view_cells(pages) if w.startswith(("6.1", "7 ", "execution"))]
    out += [("impacts %s" % rid, " ".join(str(e.get("why")).split())) for rid, e in (data.get("impacts") or {}).items()]
    out += [("question %s" % q["q"], " ".join(str(q["note"]).split())) for q in data.get("execution_plan_questions") or []]
    return out


def _status_wrong(req, data, pages):
    """(a) wherever a unit says 'row L3-ODn answered X (D-nn)', X is the row's decided option and D-nn its ruling; (b)
    each unit split into clauses at ';': a clause carrying words of an option its row's ruling did not take passes only
    if that same clause carries a history marker (was or were not taken or adopted, not added, not applied,
    superseded). Naming the ruling does not excuse a clause."""
    RL = _rl()
    dec = RL.decided(req, data)
    rows = {d["id"]: [o["id"] for o in d["options"]] for d in data["decisions"]}
    bad = []
    for where, text in _status_units(data, pages):
        for m in ANSWERED.finditer(text):
            r, opt, rid = m.groups()
            if r in dec and (opt, rid) != (dec[r][0], dec[r][1]):
                bad.append("%s: row %s answered %s (%s), decided %s (%s)" % (where, r, opt, rid, dec[r][0], dec[r][1]))
        for clause in re.split(r";\s*", text):
            if HISTORY_MARK.search(clause): continue
            for r, v in dec.items():
                hits = _untaken_hits(clause, r, v[0], rows[r])
                if hits: bad.append("%s: a current clause carries %s of row %s: %s" % (where, hits, r, clause[:120]))
    return bad


def t_l3r5_current_status_follows_the_ruling():
    """An entry passes only when its current status is the ruling's (the owner's clarification on B2): the tree passes,
    history kept in clauses marked as such; an entry citing D-33 with contradictory current text fails, and so does one
    naming an option the row did not take as its answer. The stale case (REQ-072's why as it read before the fix) is
    t_l3r5_recheck_decided_rows_carry_no_option_they_did_not_take's fixture."""
    import copy
    import rules_lib as R
    RL = _rl()
    req, data = R.load_requirements(), RL.load_data()
    pages = {n: open(os.path.join(L3, n), encoding="utf-8").read() for n in RL.PAGES.values()}
    bad = _status_wrong(req, data, pages)
    assert not bad, "a current status does not follow its ruling:\n  %s" % "\n  ".join(bad[:12])
    for name, why in (
            ("contradictory current text citing D-33",
             "row L3-OD2 answered both-kept (D-33): no HF bearer in the kit, REQ-002 restated; qmx-outside's note was not taken"),
            ("the wrong answered option citing D-33",
             "row L3-OD2 answered qmx-out (D-33): the HF bearer removed; qmx-outside's note was not taken")):
        d2 = copy.deepcopy(data)
        d2["impacts"]["REQ-002"]["why"] = why
        assert _status_wrong(req, d2, pages), "a fixture with %s passes" % name


def t_l3r5_d39_is_conditional_and_acceptance_is_its_own_record():
    """D-39 (decides layer3_baseline) records the owner's conditional closure authorisation, its four quotes filed word
    for word, and a second run refuses. The ruling is not acceptance: with D-39 alone the status level reads DRAFTED, on
    the tree and on a fixture whose newest independent check is accepted; only with l3r2.yaml's baseline_acceptance filed
    (the verified revision, D-39, the evidence held, the newest check among it) does it read VALIDATED. The acceptance
    script refuses on the tree (its newest check is not accepted), a revision that is no commit and a path the tree does
    not hold, files one line on a copy, and refuses a second run; it is never run on the tree here."""
    import copy
    import yaml
    import rules_lib as R
    RL = _rl()
    req, data = R.load_requirements(), RL.load_data()
    sys.path.insert(0, REC5)
    import apply_l3r5_d39 as A
    r39 = [r for r in req["owner_rulings"] if str(r.get("decides")) == "layer3_baseline"]
    assert [r["id"] for r in r39] == ["D-39"] and r39[0]["authority"] == "OWNER" and str(r39[0]["ruled_on"]) == "2026-09-30"
    flat = " ".join(" ".join(l.lstrip("> ") for l in _instr().split("\n")).split())
    for q in A.QUOTES:
        assert q in flat and q in " ".join(r39[0]["ruling"].split()), "a quote is not word for word: %r" % q[:50]
    assert "D-39 is a CONDITIONAL authorisation" in " ".join(r39[0]["ruling"].split())
    r = _run([os.path.join(REC5, "apply_l3r5_d39.py"), "--check"])
    assert r.returncode == 2 and "has run" in r.stdout, "a second run of the D-39 script was not refused:\n%s" % r.stdout
    dec, h3 = RL.decided(req, data), RL.load_h3()
    assert data.get("baseline_acceptance") is None and RL.status_level(req, dec, data, h3)[0] == "DRAFTED"
    fixture_check = {"record": "v2/docs/records/l3r2/checks/check-l3r2-5.md", "sha16": "c1c9db881ededfe2",
                     "verdict": "ACCEPTED", "scope": "a fixture: an accepted newest check"}
    d1 = copy.deepcopy(data)
    d1["independent_check"].append(fixture_check)
    assert all(x[1] for x in RL.gate(req, dec, d1, h3)), "the fixture's gate is not all MET"
    assert RL.status_level(req, dec, d1, h3)[0] == "DRAFTED", "D-39 without the acceptance record reads beyond DRAFTED"
    head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    d2 = copy.deepcopy(d1)
    d2["baseline_acceptance"] = {"revision": head, "authorised_by": "D-39", "evidence": [fixture_check["record"]],
                                 "accepted_on": "2026-10-01"}
    assert RL.status_level(req, dec, d2, h3)[0] == "VALIDATED", RL.acceptance_ok(req, d2)
    d3 = copy.deepcopy(d2)
    d3["baseline_acceptance"]["evidence"] = ["v2/docs/handover/layer3/l3r2.yaml"]
    assert RL.status_level(req, dec, d3, h3)[0] == "DRAFTED", "an acceptance not listing the newest check validates"
    acc = os.path.join(REC5, "apply_l3r5_accept.py")
    r = _run([acc, "--revision", head, "--evidence", fixture_check["record"], "--check"])
    # on the tree it refuses with the fixture's evidence: before check 3 because the newest check was not accepted, after
    # it because the evidence does not list the newest check
    assert r.returncode == 2 and ("not ACCEPTED" in r.stdout or "does not list the newest independent check" in r.stdout), \
        "the acceptance script ran on the tree:\n%s" % r.stdout
    d = tempfile.mkdtemp(prefix="l3r5-accept-")
    copy_path = os.path.join(d, "l3r2.yaml")
    raw = open(os.path.join(L3, "l3r2.yaml"), encoding="utf-8").read()
    add = "  - {record: %s, sha16: %s, verdict: ACCEPTED, scope: fixture}\nbaseline_acceptance: null\n" % (
        fixture_check["record"], fixture_check["sha16"])
    assert raw.count("\nbaseline_acceptance: null\n") == 1
    open(copy_path, "w", encoding="utf-8").write(raw.replace("\nbaseline_acceptance: null\n", "\n" + add))
    for args, why in (([ "--revision", "0" * 40, "--evidence", fixture_check["record"]], "not a commit"),
                      (["--revision", head, "--evidence", "v2/docs/records/l3r5/checks/no-such-check.md"], "not a file"),
                      (["--revision", head, "--evidence", "v2/docs/handover/layer3/l3r2.yaml"], "does not list the newest")):
        r = _run([acc] + args + ["--data", copy_path])
        assert r.returncode == 2 and why in r.stdout, "%s was not refused:\n%s" % (why, r.stdout)
    r = _run([acc, "--revision", head, "--evidence", fixture_check["record"], "--date", "2026-10-01", "--data", copy_path])
    assert r.returncode == 0, r.stdout
    got = yaml.safe_load(open(copy_path, encoding="utf-8"))["baseline_acceptance"]
    assert got == {"revision": head, "authorised_by": "D-39", "evidence": [fixture_check["record"]], "accepted_on": "2026-10-01"}
    r = _run([acc, "--revision", head, "--evidence", fixture_check["record"], "--data", copy_path])
    assert r.returncode == 2 and "has run" in r.stdout, "a second acceptance was not refused:\n%s" % r.stdout
    assert yaml.safe_load(open(os.path.join(L3, "l3r2.yaml"), encoding="utf-8")).get("baseline_acceptance") is None
