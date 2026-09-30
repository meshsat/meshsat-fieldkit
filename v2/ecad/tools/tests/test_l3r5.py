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
    assert not g[3][1], "an acceptance of the handover with the decisions pending covers the decided issue"
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
    assert len(brief.strip().split("\n")) <= 45, "the brief runs to %d lines" % len(brief.strip().split("\n"))
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
