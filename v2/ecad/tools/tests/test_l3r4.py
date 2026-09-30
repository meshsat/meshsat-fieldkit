"""The definition re-issue on the owner's layer 3 answers is prepared and follows the recorded answers (MESHSAT-1357,
layer 3 round 4, 30 September 2026; closure item L3-C26).

`v2/docs/records/l3r4/reissue.py` maps every passage of the baselined CONOPS.md and PRODUCT-BRIEF.md that an answer to
rows L3-OD1 to L3-OD6 makes inconsistent with the requirements, and once the registry records the answers it writes the
proposed re-issue and its change record. These tests hold the passage map to the baselined files, run the prepared
owner-decision scripts of L3-R2 (v2/docs/records/l3r2/conditional/) on COPIES of the registry in the pattern of its dry
runs, and check the generator on the session's recommended answers, on two other coherent combinations, and its
refusals: rows undecided, an incoherent set, and any write into a baselined file. `apply_layer_status_l3_r4.py` is run
on a copy of LAYER-STATUS.md. Nothing here writes into the tree.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l3r4")
COND = os.path.join(ROOT, "v2", "docs", "records", "l3r2", "conditional")
GEN = os.path.join(REC, "reissue.py")
LSTAT = os.path.join(REC, "apply_layer_status_l3_r4.py")
BASE = {"v2/docs/CONOPS.md": None, "v2/docs/PRODUCT-BRIEF.md": None}
DASHES = ("\u2013", "\u2014")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402
import claims_check as CC  # noqa: E402

# The session's recommended answers (OWNER-DECISIONS-L3.md): approve, 2s2p, adopt, reading-c and the mean day. Rows
# L3-OD2 (which lid item leaves) and L3-OD6's build are the owner's with no recommendation; the fixture takes the QMX
# out and TYP, the placeholders of dryrun.py's example chain.
RECOMMENDED = [("od_l3_6.py", "mean-day", "--build", "TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-out"),
               ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt", "--push-n", "20"), ("od_l3_5.py", "reading-c")]
OTHER = [("od_l3_6.py", "mean-day", "--build", "WAB"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-outside"),
         ("od_l3_3.py", "1s4p"), ("od_l3_4.py", "reject"), ("od_l3_5.py", "measure")]
THIRD = [("od_l3_6.py", "mean-day", "--build", "TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "tablet-out"),
         ("od_l3_3.py", "keep", "--array-wp", "1100", "--entry-a", "80", "--evidence", "EV"), ("od_l3_4.py", "reject"),
         ("od_l3_5.py", "cells")]


def _run(args, cwd=None):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True, cwd=cwd or tempfile.gettempdir())


def _mod():
    need(GEN, "the re-issue generator is not in this tree")
    sys.path.insert(0, REC)
    import reissue as RI
    return RI


def _sha(rel):
    import hashlib
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:16]


def _tree_undecided():
    import yaml
    d = yaml.safe_load(open(os.path.join(TOOLS, "pcb_requirements.yaml"), encoding="utf-8"))
    rows = [str(r.get("decides")).split(":")[0] for r in d["owner_rulings"] if str(r.get("decides") or "").startswith("L3-OD")]
    if rows: raise Skip("rows %s are decided in this tree; the fixtures start from undecided rows" % ", ".join(rows))


def _chain(steps):
    """A copy of the registry with the steps applied by the prepared scripts, as dryrun.py applies them."""
    need(COND, "the conditional scripts of L3-R2 are not in this tree")
    _tree_undecided()
    d = tempfile.mkdtemp(prefix="l3r4-reg-")
    reg = os.path.join(d, "pcb_requirements.yaml")
    shutil.copy(os.path.join(TOOLS, "pcb_requirements.yaml"), reg)
    ev = os.path.join(d, "basis-fixture.md")
    open(ev, "w", encoding="utf-8").write("FIXTURE, not the energy basis: array 1100 Wp, entry 80 A.\n")
    for s in steps:
        extra = [ev if x == "EV" else x for x in s[2:]]
        r = _run([os.path.join(COND, s[0]), "--option", s[1], "--words", "test words", "--date", "2026-10-01",
                  "--registry", reg] + extra, cwd=d)
        assert r.returncode == 0, "%s --option %s exit %d:\n%s" % (s[0], s[1], r.returncode, (r.stdout + r.stderr)[-500:])
    return d, reg


def _generate(reg, expect=0):
    out = tempfile.mkdtemp(prefix="l3r4-out-")
    before = {k: _sha(k) for k in BASE}
    r = _run([GEN, "--registry", reg, "--out-dir", out])
    assert r.returncode == expect, "reissue.py exit %d (expected %d):\n%s" % (r.returncode, expect, (r.stdout + r.stderr)[-600:])
    assert {k: _sha(k) for k in BASE} == before, "a baselined file changed while reissue.py ran"
    return out, r.stdout


def _read(out):
    RI = _mod()
    return (open(os.path.join(out, RI.DRAFT), encoding="utf-8").read(),
            open(os.path.join(out, RI.RECORD), encoding="utf-8").read())


def _common(reg, out):
    """What holds for every generated re-issue: each passage names its rows and rulings, every ruling of the answers is
    cited, the change record binds the draft by its sha, and the texts carry no dash and no unqualified claim."""
    import yaml
    RI = _mod()
    draft, rec = _read(out)
    d = yaml.safe_load(open(reg, encoding="utf-8"))
    rids = {str(r["decides"]).split(":")[0]: r["id"] for r in d["owner_rulings"] if str(r.get("decides") or "").startswith("L3-OD")}
    assert sorted(rids) == list(RI.ROWS), "the fixture does not decide the six rows: %s" % sorted(rids)
    heads = re.findall(r"^### ([CB]\d\d)\. .*$", draft, re.M)
    cites = re.findall(r"^Rows and rulings: (.*)\.$", draft, re.M)
    assert heads and len(heads) == len(cites), "a restated passage has no 'Rows and rulings' line"
    for h, c in zip(heads, cites):
        assert re.search(r"L3-OD\d `[a-z0-9-]+`, D-\d+", c), "passage %s names no row and ruling: %r" % (h, c)
    for row, rid in rids.items():
        assert "%s `" % row in draft and rid in draft, "the draft does not cite %s's ruling %s" % (row, rid)
    import hashlib
    assert hashlib.sha256(draft.encode("utf-8")).hexdigest()[:16] in rec, "the change record does not name the draft's sha"
    assert "PROPOSED" in draft and "PROPOSED" in rec and "definition_reissue" in rec
    for t in (draft, rec):
        assert not any(x in t for x in DASHES), "a generated text carries a dash character"
    n, bad = CC.check([os.path.join(out, RI.DRAFT), os.path.join(out, RI.RECORD)])
    assert not bad, "a generated text carries an unqualified claim: %s" % bad[:2]
    r = _run([GEN, "--registry", reg, "--out-dir", out, "--check"])
    assert r.returncode == 0, "--check reads the files it has just written as out of date:\n%s" % r.stdout
    return draft, rec, rids


def _proposed(RI, reg):
    """The re-issue applied in memory, and the baselined texts: outside the restated passages nothing moves."""
    import yaml
    docs = RI.baselined()
    c = RI.answers(yaml.safe_load(open(reg, encoding="utf-8")), RI.RL.load_data())
    applied, cur = RI.apply_all(docs, c)
    for k, (text, edits) in applied.items():
        back = text
        for p, old, new in edits:
            assert back.count(new) >= 1, "%s's proposed text is not in the proposed document" % p.pid
            back = back.replace(new, old, 1)
        assert back == docs[k], "%s outside the restated passages moved" % k
    return c, applied, cur


# ------------------------------------------------------------------------------------------------ the map
def t_l3r4_the_passage_map_is_generated_from_the_baselined_files():
    _mod()
    r = _run([GEN, "--map", "--check"])
    assert r.returncode == 0, "PASSAGE-MAP.md is not what reissue.py --map writes:\n%s" % r.stdout


def t_l3r4_every_passage_is_found_once_where_the_map_says():
    RI = _mod()
    docs = RI.baselined()
    ids = [p.pid for p in RI.PASSAGES]
    assert len(ids) == len(set(ids)), "a passage id repeats"
    for p in RI.PASSAGES:
        off, end, old = RI.locate(docs[p.doc], p)
        line = docs[p.doc][:off].count("\n") + 1
        assert line == p.a, "%s starts on line %d, not %d" % (p.pid, line, p.a)
        assert (p.new is None) == (p.kind == "CURRENT"), "%s: a CURRENT passage has no proposed text, a DEFINITION one does" % p.pid
        assert p.when == RI.ALL or set(p.when) <= set(RI.ROWS), "%s names a row that is not L3-OD1 to L3-OD6" % p.pid


def t_l3r4_the_baselines_are_the_files_l3r2_names():
    RI = _mod()
    data = RI.RL.load_data()
    for rel in BASE:
        assert _sha(rel) == str(data["baseline_definition"][rel]), "%s is not the baselined text: the map reads another" % rel


# ------------------------------------------------------------------------------------------------ the answers
def t_l3r4_the_recommended_answers_give_the_reissue():
    RI = _mod()
    d, reg = _chain(RECOMMENDED)
    out, msg = _generate(reg)
    draft, rec, rids = _common(reg, out)
    c, applied, cur = _proposed(RI, reg)
    got = {p.pid for k in applied for p, o, n in applied[k][1]}
    for pid in ("C03", "C05", "C06", "C07", "C09", "C14", "C17", "C19", "C21", "C29", "C31", "B03", "B06", "B08", "B13",
                "B15", "B18"):
        assert pid in got, "the recommended answers leave %s unrestated" % pid
    assert len(cur) == len(RI.QMX_CURRENT), "the QMX out of the kit leaves %d statements of the design as generated, not %d" % (
        len(cur), len(RI.QMX_CURRENT))
    rq = c.deploy_req()
    flat = " ".join(re.sub(r"^> ?", "", draft, flags=re.M).split())
    assert rq in draft and c.stmt(rq) in flat, "the deployment condition is not quoted from %s" % rq
    assert c.stmt("REQ-072") in flat, "M1's energy passage does not quote REQ-072 as restated"
    assert "4S15P lid pack" in draft, "the QMX out of the lid does not give the 4S15P lid pack"
    assert "HF has left the kit (owner ruling %s on row L3-OD2)" % rids["L3-OD2"] in draft


def t_l3r4_another_coherent_combination_gives_its_own_reissue():
    """The QMX carried outside with HF kept, 1S4P, no deployment condition and CFL-017 kept open: other passages."""
    RI = _mod()
    d, reg = _chain(OTHER)
    out, msg = _generate(reg)
    draft, rec, rids = _common(reg, out)
    c, applied, cur = _proposed(RI, reg)
    got = {p.pid for k in applied for p, o, n in applied[k][1]}
    assert {"B09", "C03", "C21", "C29"} <= got, "the QMX outside or CFL-017 kept open leaves a passage unrestated"
    assert not ({"C05", "C06", "C10", "C13", "B05", "B13"} & got), "HF kept or no deployment condition restates a passage"
    assert [p.a for p in cur] == [1095], "the QMX outside leaves the lid tray alone as the design as generated"
    assert "1S4P" in draft and "deployment condition (owner ruling" not in draft
    assert "4S15P lid pack" in draft
    d3, reg3 = _chain(THIRD)
    out3, msg3 = _generate(reg3)
    draft3, rec3, rids3 = _common(reg3, out3)
    c3, applied3, cur3 = _proposed(RI, reg3)
    got3 = {p.pid for k in applied3 for p, o, n in applied3[k][1]}
    assert {"C04", "B04", "C08", "B12"} <= got3 and not cur3, "the tablet out restates its passages and no QMX statement"
    assert "4S14P lid pack" in draft3 and "the tablet bracket has left the kit" in draft3


# ------------------------------------------------------------------------------------------------ the refusals
def t_l3r4_refuses_while_a_row_is_undecided():
    _mod()
    _tree_undecided()
    r = _run([GEN, "--out-dir", tempfile.mkdtemp(prefix="l3r4-out-")])
    assert r.returncode == 2 and "undecided" in r.stdout, "the tree's undecided rows were not refused:\n%s" % r.stdout
    d, reg = _chain(RECOMMENDED[:3])
    out, msg = _generate(reg, expect=2)
    assert "L3-OD3, L3-OD4 and L3-OD5 are undecided" in msg, "the refusal does not name the undecided rows: %s" % msg
    assert not os.listdir(out), "a refused run wrote a file"


def t_l3r4_refuses_an_incoherent_set():
    """Rulings written into a decided copy as a set the scripts would refuse: a band adopted on 1S4P, and row L3-OD1
    rejected; the generator refuses both, naming why."""
    _mod()
    d, reg = _chain(RECOMMENDED)
    raw = open(reg, encoding="utf-8").read()
    for a, b, why in (('decides: "L3-OD3:2s2p"', 'decides: "L3-OD3:1s4p"', "without row L3-OD3 answered 2s2p"),
                      ('decides: "L3-OD1:approve"', 'decides: "L3-OD1:reject"', "row L3-OD1 answered reject")):
        assert raw.count(a) == 1, "the fixture does not carry %s once" % a
        bad = os.path.join(d, "incoherent.yaml")
        open(bad, "w", encoding="utf-8").write(raw.replace(a, b))
        out, msg = _generate(bad, expect=2)
        assert "not coherent" in msg and why in msg, "the incoherent set was not refused for its reason: %s" % msg
        assert not os.listdir(out), "a refused run wrote a file"


def t_l3r4_never_writes_a_baselined_file():
    RI = _mod()
    for rel in BASE:
        try:
            RI.guard_out([os.path.join(ROOT, rel)])
        except RI.E.Refused:
            continue
        raise AssertionError("the generator would write into %s" % rel)
    src = open(GEN, encoding="utf-8").read()
    writes = re.findall(r"open\(([^,]+), \"w\"", src)
    assert sorted(writes) == ["MAP", "q"], "the generator opens another file for writing: %s" % writes


# ------------------------------------------------------------------------------------------------ LAYER-STATUS
def t_l3r4_layer_status_row_brought_current_on_a_copy():
    need(LSTAT, "apply_layer_status_l3_r4.py is not in this tree")
    page = os.path.join(ROOT, "v2", "docs", "handover", "LAYER-STATUS.md")
    t = open(page, encoding="utf-8").read()
    sys.path.insert(0, REC)
    import apply_layer_status_l3_r4 as A
    if A.MARK in t:
        assert A.OLD not in t, "the page carries both the old row and the new one"
        r = _run([LSTAT, "--check"])
        assert r.returncode == 2 and "has run" in r.stdout, "a second run was not refused:\n%s" % r.stdout
        t = t.replace(t[t.index(A.MARK):t.index("\n", t.index(A.MARK))], A.OLD)
    cp = os.path.join(tempfile.mkdtemp(prefix="l3r4-ls-"), "LAYER-STATUS.md")
    open(cp, "w", encoding="utf-8").write(t)
    r = _run([LSTAT, "--page", cp])
    assert r.returncode == 0, "the row was not restated on a copy:\n%s" % r.stdout
    new = open(cp, encoding="utf-8").read()
    assert A.MARK in new and A.OLD not in new and "check-l3r2-5.md" in new
    assert new.replace(new[new.index(A.MARK):new.index("\n", new.index(A.MARK))], A.OLD) == t, "the page moved elsewhere"
    r = _run([LSTAT, "--page", cp])
    assert r.returncode == 2, "a second run on the copy was not refused"
