"""Stream l4small (MESHSAT-1357, worker W133, branch fnd/l4small, 7 October 2026): register tasks L4A-60 (revision X not admitted,
SESSION L9T5-D11), L4A-80 (the B2 wording swept, SESSION L4E7-D1) and W130's correction 2 (R-208's R264 and C264), written as apply
scripts that the set 33 integrator runs on the integrated tree.

The predicates, on either state of the tree: before the integrator runs the scripts each one is applied to temporary copies of its
files (never to the tree), and after it the tree's own files are read; a tree with some scripts applied and others not, or a script
half applied, fails. (1) Each script applies once and refuses a second run; the engine refuses a partial application, a removal in a
KEEP edit and a moved line. (2) L4A-60's acceptance: in every file that carries a current procurement, inspection, contract, model or
task instruction for the supervisors, each wording that would admit revision X (an admission route, a revision V or X procurement or
goods-in line, a rev X qualification as a task) stands within reach of the decision L9T5-D11 that supersedes it, outside CON-017 (5)'s
own bound; the decision carries authority, its reason, who ruled, when and its reversal; FW-B20, HC6-SC-1 and the procurement line
say revision V only. (3) L4A-80's acceptance: no selected, recommended or owner-request wording for B2 in record l4e7's files, the
ledger's B2 rows, L4-E9's copy and the change-list draft's docstring, and the decision L4E7-D1 with its fields; the withdrawn B2
draft refuses the repository's own generator even when a RELEASE.md with an accepted check is present (the old guard, the mutant,
let it through). (4) W130's correction 2: R-208 names R264 and C264 on record l8p's own composition and R603 and C607 on the connected
candidate's full order, each at the line of its output that prints it. (5) The restated W11 generator check refuses a partial
application. Every predicate is also run against the old text and must fail there. These are software predicates on record text:
they establish no electrical property, change no verdict and close nothing; nothing in the kit has been built, bought, powered or
measured.

Runs under the suite's runner (`python3 -u v2/ecad/tools/tests/run.py test_l4small.`)."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import importlib.util

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records")
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import need  # noqa: E402

SCRIPTS = ("l9t5/apply_l4small_revx.py", "l9t5/apply_l4small_layer6.py", "l4close/apply_l4small_ledger.py",
           "l4small/apply_l4small_register.py", "l4small/apply_l4small_b2.py", "l4small/apply_l4small_tests.py")
DASHES = (chr(0x2013), chr(0x2014))
DX, DB = "L9T5-D11", "L4E7-D1"
REACH = 400
# wording that would admit revision X (an admission route, a V or X procurement or goods-in line, a qualification as a task)
ADMIT = ("V or X", "0x2001", "waits on V-B20", "admitted only by V-B20", "accepted only after the supplier's V-B20",
         "until its own qualification", "HELD on V-B20", "a rev X part's qualification", "a rev X part's V-B20",
         "three rev X STM32H743VIT6", "held until its own qualification", "rev X on V-B20", "rev X stays on V-B20")
REVX_FILES = ("v2/docs/records/l9t5/T10-ROUND5.md", "v2/docs/records/l9t5/L9T5-CASES.md", "v2/docs/records/l9t5/l9t5_t10.py",
              "v2/docs/records/l9t5/l9t5_connected.py", "v2/docs/records/l9t5/apply_hw_fw_contract_t10.py",
              "v2/docs/parts/STM32H743-COMPATIBILITY.md", "v2/docs/parts/PROCUREMENT.md",
              "v2/docs/records/l4close/REMAINING-ENGINEERING.md", "v2/docs/records/l4close/P0-POWER-LIST.md",
              "v2/docs/records/l4e9/l4e9_power_path.py", "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md")
# CON-017 (5) is the requirement's bound (ES0392 2.24.2), which revision V meets: a clause that states that bound, or quotes the
# requirement's own words, is not an instruction
REQ_BOUND = re.compile(r"CON-017 \(5\)[^.;]*$")
REQ_WORDS = "the fitted supervisors are silicon revision "
# wording that would select, recommend or ask the owner about route B2 (matched as written; the last two in any case)
B2_BAD = ("waits on the owner", "waits on an owner", "Decision asked", "decision is asked", "Recommendation", "(recommended)",
          "recommends adopting", "Adopt the presence pair", "B2 selected", "selected by the coordinator", "if the owner adopts",
          "a PROPOSAL until the owner", "owner request:", "would prevent")
B2_BAD_ANY_CASE = ("partial proposal", "unapproved partial")
B2_FILES = ("v2/docs/records/l4e7/B2-PRESENCE.md", "v2/docs/records/l4e7/L4E7-P0SOL.md", "v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md",
            "v2/docs/records/l4e7/l4e7_p0sol.out", "v2/docs/records/l4e7/apply_gen_sch_e_p0sol_b2.py", "v2/docs/records/l4e7/README.md",
            "v2/docs/records/l4close/REMAINING-ENGINEERING.md", "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md")
# not here: record l9t5's apply_l4e9_changelist_p0.py, whose docstring sentence on route B2 is record l4k's K-24 (fnd/l4k)


def _mod(rel, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REC, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _files(m):
    edits = getattr(m, "EDITS", None) or m.edits
    edits = edits(ROOT) if callable(edits) else edits
    rels = [e[0] for e in edits] + [a[0] for a in getattr(m, "APPENDS", ())]
    if m.NAME == "apply_l4small_register":
        rels += [m.L8P, m.CON]
    if m.NAME == "apply_l4small_layer6":
        rels += [m.L3P]
    return sorted(set(rels))


def _run(script, root, *flags):
    return subprocess.run([sys.executable, "-B", os.path.join(REC, script)] + ([root] if root else []) + list(flags),
                          capture_output=True, text=True)


def _state(script):
    """'old' when the tree is before the script, 'new' after it; anything else fails"""
    r = _run(script, None, "--check")
    if r.returncode == 0:
        return "old"
    assert r.returncode == 3 and "already applied" in r.stderr, (script, r.stderr[-300:])
    return "new"


_CACHE = {}


def _applied(script):
    """{rel: text} of the script's files after it: the tree's own when the integrator has run it, else temporary copies"""
    if script in _CACHE:
        return _CACHE[script]
    m = _mod(script, "l4small_" + os.path.basename(script)[:-3])
    rels = _files(m)
    if _state(script) == "new":
        out = {rel: open(os.path.join(ROOT, rel), encoding="utf-8").read() for rel in rels}
    else:
        td = tempfile.mkdtemp(prefix="l4small_")
        try:
            for rel in rels:
                os.makedirs(os.path.dirname(os.path.join(td, rel)), exist_ok=True)
                shutil.copy(os.path.join(ROOT, rel), os.path.join(td, rel))
            r = _run(script, td, "--write")
            assert r.returncode == 0, (script, r.stderr[-400:])
            r2 = _run(script, td, "--write")
            assert r2.returncode == 3 and "already applied" in r2.stderr, (script, "a second run was not refused", r2.stderr[-200:])
            out = {rel: open(os.path.join(td, rel), encoding="utf-8").read() for rel in rels}
        finally:
            shutil.rmtree(td, ignore_errors=True)
    _CACHE[script] = out
    return out


def _all_applied():
    texts = {}
    for s in SCRIPTS:
        texts.update(_applied(s))
    return texts


def _tree_or_applied(rel, texts):
    return texts[rel] if rel in texts else open(os.path.join(ROOT, rel), encoding="utf-8").read()


def _norm(t):
    return " ".join(t.split())


def _unlabelled(text, phrases, label, exempt=None, any_case=False):
    """each occurrence of a phrase with no `label` within REACH characters (whitespace normalised), outside an exempt span"""
    t = _norm(text)
    bad = []
    hay = t.lower() if any_case else t
    for p in phrases:
        for m in re.finditer(re.escape(p.lower() if any_case else p), hay):
            win = t[max(0, m.start() - REACH):m.end() + REACH]
            if label in win:
                continue
            if exempt is not None and exempt(t, m.start(), m.end()):
                continue
            bad.append(t[max(0, m.start() - 80):m.end() + 40])
    return bad


HISTORY = "kept as written only as history, not an instruction"   # round 6's own label on T10-ROUND5.md section 3 (1)


def _req_bound(t, i, j):
    pre = t[max(0, i - 100):i]
    return bool(REQ_BOUND.search(pre)) or pre.endswith(REQ_WORDS) or HISTORY in t[max(0, i - 200):i]


def _revx_violations(texts):
    out = []
    for rel in REVX_FILES:
        out += [(rel, b) for b in _unlabelled(_tree_or_applied(rel, texts), ADMIT, DX, _req_bound)]
    return out


def _b2_violations(texts):
    out = []
    for rel in B2_FILES:
        tx = _tree_or_applied(rel, texts)
        whole = rel.endswith(("B2-PRESENCE.md", "apply_gen_sch_e_p0sol_b2.py"))   # pages whose whole subject is route B2
        near_b2 = None if whole else (lambda t, i, j: "B2" not in t[max(0, i - 300):j + 300])
        out += [(rel, b) for b in _unlabelled(tx, B2_BAD, DB, near_b2)]
        out += [(rel, b) for b in _unlabelled(tx, B2_BAD_ANY_CASE, DB, near_b2, any_case=True)]
        nt = _norm(tx)
        for m in re.finditer(r"owner item", nt):
            if "/l4e7/" not in rel and near_b2(nt, m.start(), m.end()):
                continue
            pre = nt[max(0, m.start() - 12):m.start()]
            if not re.search(r"(\bno |\bNo |NO |[Rr]ound 2's )$", pre):
                out.append((rel, nt[max(0, m.start() - 60):m.end() + 30]))
    return out


# ------------------------------------------------------------------------------------------------------------------ (1) the engine
def t_every_script_applies_once_and_refuses_a_second_run():
    for s in SCRIPTS:
        need(os.path.join(REC, s), "the apply script is not in this tree")
        assert _applied(s), s     # _applied runs it on copies, twice, when the tree is before it
    states = {s: _state(s) for s in SCRIPTS}
    assert len(set(states.values())) == 1, "the scripts are applied to the tree in part: %s" % states


def t_the_engine_refuses_a_partial_application_a_removal_and_a_moved_line():
    sys.path.insert(0, os.path.join(REC, "l4small"))
    import l4small_edit as E
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "page.md")
        open(p, "w", encoding="utf-8").write("alpha beta\ngamma delta\n| a | b |\n")
        ok = [("page.md", "alpha beta", "alpha [x] beta", True)]
        assert E.plan(td, ok)["page.md"][1] == "alpha [x] beta\ngamma delta\n| a | b |\n"
        for edits, why in (([("page.md", "gamma delta", "gamma XX", True)], "removes text"),
                           ([("page.md", "gamma delta", "gamma\ndelta", True)], "line count"),
                           ([("page.md", "| a | b |", "| a | b | c |", False)], "number of cells"),
                           ([("page.md", "omega", "omega [x]", True)], "occurs 0 times")):
            try:
                E.plan(td, edits)
            except E.Refused as ex:
                assert why in str(ex), (why, str(ex))
            else:
                raise AssertionError("not refused: %s" % why)
        open(p, "w", encoding="utf-8").write("alpha [x] beta\ngamma delta\n| a | b |\n")
        for edits, why in ((ok, "already applied"), (ok + [("page.md", "gamma delta", "gamma [y] delta", True)], "partly applied")):
            try:
                E.plan(td, edits)
            except E.Refused as ex:
                assert why in str(ex), (why, str(ex))
            else:
                raise AssertionError("not refused: %s" % why)


# --------------------------------------------------------------------------------------------------------- (2) L4A-60, revision X
def t_no_current_instruction_admits_revision_x():
    texts = _all_applied()
    bad = _revx_violations(texts)
    assert not bad, "wording that admits revision X without L9T5-D11 in reach: %s" % bad[:4]
    # the old text, the mutant: the same predicate refuses the files as they stand before the scripts
    old = {rel: open(os.path.join(ROOT, rel), encoding="utf-8").read() for rel in REVX_FILES} if _state(SCRIPTS[0]) == "old" else None
    if old is not None:
        assert _revx_violations(old), "the predicate passes the old text"
    # and a single label removed from the applied page is found
    r5 = "v2/docs/records/l9t5/T10-ROUND5.md"
    cut = re.sub(r" \[as written at round 5; superseded by SESSION L9T5-D11[^\]]*\]", "", texts[r5], count=1)
    assert cut != texts[r5] and _revx_violations(dict(texts, **{r5: cut})), "a removed label is not found"


def t_the_decision_l9t5_d11_carries_its_fields_and_the_rows_say_revision_v_only():
    texts = _all_applied()
    r5 = texts["v2/docs/records/l9t5/T10-ROUND5.md"]
    sec = r5.split("\n## W133 (7 October 2026): SESSION decision L9T5-D11, revision X not admitted\n", 1)
    assert len(sec) == 2, "section W133 is missing"
    rows = dict(re.findall(r"^\| (\w+) \| (.+) \|$", sec[1], re.M))
    for k in ("decision", "authority", "authority_why", "ruled_by", "ruled_on", "reversed_by"):
        assert rows.get(k, "").strip(), k
    assert rows["authority"] == "SESSION" and rows["ruled_on"] == "2026-10-07" and "NOT ADMITTED" in rows["decision"]
    assert "UNSELECTED OPTION" in rows["decision"] and "refused at goods-in" in rows["decision"] and "M-B" in rows["reversed_by"]
    assert "Revision X is NOT ADMITTED" in rows["decision"] and "revision V only" in rows["decision"]
    ctr = texts["v2/docs/records/l9t5/apply_hw_fw_contract_t10.py"]
    fw = ctr.split("FW_B20 = (", 1)[1].split("\nFW_B21", 1)[0]
    assert "silicon revision V only" in fw and "revision X \"\n          \"NOT ADMITTED, record l9t5 SESSION L9T5-D11" in fw
    assert "held until its own qualification" not in fw and " or X" not in fw
    prc = [l for l in texts["v2/docs/parts/PROCUREMENT.md"].splitlines() if l.startswith("| ST STM32H743VIT6 (C114409)")]
    assert len(prc) == 1 and "| revision V ONLY (SESSION L9T5-D11" in prc[0] and "revision X NOT ADMITTED" in prc[0]
    hc = [l for l in texts["v2/docs/parts/STM32H743-COMPATIBILITY.md"].splitlines() if l.startswith("| HC6-SC-1 |")]
    assert len(hc) == 1 and "narrowed to revision V ONLY by SESSION L9T5-D11" in hc[0]


def t_con017_is_rebound_to_the_patched_page_and_its_clause_5_is_unchanged():
    import hashlib
    texts = _all_applied()
    page = texts["v2/docs/parts/STM32H743-COMPATIBILITY.md"]
    pin = "v2/docs/parts/STM32H743-COMPATIBILITY.md@%s" % hashlib.sha256(page.encode("utf-8")).hexdigest()[:16]
    reg = hashlib.sha256(texts["v2/ecad/tools/pcb_requirements.yaml"].encode("utf-8")).hexdigest()[:16]
    assert "`v2/ecad/tools/pcb_requirements.yaml` (sha256/16 `%s`," % reg in texts["v2/docs/handover/layer3/REQUIREMENTS-L3-R2.md"]
    for rel in ("v2/ecad/tools/pcb_requirements.yaml", "v2/docs/REQUIREMENTS-TRACE.md"):
        assert texts[rel].count(pin) == 1, (rel, pin)
        assert "(5) the fitted supervisors are" in texts[rel] and "silicon revision V or X (marking V or X; DBGMCU_IDC REV_ID 0x2003 or 0x2001" \
            in _norm(texts[rel]), rel
        assert "fitted revision is V only (SESSION L9T5-D11, record l9t5)" in _norm(texts[rel]), rel


# ------------------------------------------------------------------------------------------------------------- (3) L4A-80, route B2
def t_no_selected_recommended_or_owner_request_wording_for_b2():
    texts = _all_applied()
    bad = _b2_violations(texts)
    assert not bad, "B2 wording without L4E7-D1 in reach: %s" % bad[:4]
    if _state("l4small/apply_l4small_b2.py") == "old":
        old = {rel: open(os.path.join(ROOT, rel), encoding="utf-8").read() for rel in B2_FILES}
        assert _b2_violations(old), "the predicate passes the old text"
    page = open(os.path.join(REC, "l4e7", "B2-PRESENCE.md"), encoding="utf-8").read()
    sec = page.split("\n## 8. SESSION decision L4E7-D1 (7 October 2026): no presence-pair route is taken up\n", 1)
    assert len(sec) == 2, "B2-PRESENCE.md section 8 is missing"
    rows = dict(re.findall(r"^\| (\w+) \| (.+) \|$", sec[1], re.M))
    for k in ("decision", "authority", "authority_why", "ruled_by", "ruled_on", "reversed_by"):
        assert rows.get(k, "").strip(), k
    assert rows["authority"] == "SESSION" and rows["ruled_on"] == "2026-10-07" and "No presence-pair route is taken up" in rows["decision"]
    assert not any(d in sec[1] for d in DASHES)


def t_the_withdrawn_b2_draft_refuses_the_tree_even_with_a_release():
    """the old guard let a RELEASE.md written for record l4e7's other drafts release route B2 too; the decision refuses it always"""
    texts = _all_applied()
    rel = "v2/docs/records/l4e7/apply_gen_sch_e_p0sol_b2.py"
    new = texts[rel]
    old = open(os.path.join(ROOT, rel), encoding="utf-8").read() if _state("l4small/apply_l4small_b2.py") == "old" else None

    def refuses(src):
        with tempfile.TemporaryDirectory() as td:
            rec = os.path.join(td, "v2", "docs", "records", "l4e7")
            tools = os.path.join(td, "v2", "ecad", "tools")
            os.makedirs(rec)
            os.makedirs(tools)
            open(os.path.join(rec, "apply_gen_sch_e_p0sol_b2.py"), "w", encoding="utf-8").write(src)
            open(os.path.join(rec, "CHECK.md"), "w", encoding="utf-8").write("accepted: yes\n")
            open(os.path.join(rec, "RELEASE.md"), "w", encoding="utf-8").write(
                "released: yes\ncheck: v2/docs/records/l4e7/CHECK.md\n")
            gen = os.path.join(tools, "gen_sch_e.py")
            shutil.copy(os.path.join(ROOT, "v2", "ecad", "tools", "gen_sch_e.py"), gen)
            before = open(gen, encoding="utf-8").read()
            r = subprocess.run([sys.executable, "-B", os.path.join(rec, "apply_gen_sch_e_p0sol_b2.py"), gen, "--write"],
                               capture_output=True, text=True)
            assert open(gen, encoding="utf-8").read() == before, "the generator was written"
            return r.returncode == 3 and "NOT RELEASED: route B2 is UNSELECTED and WITHDRAWN AS DRAFTED" in r.stderr
    assert refuses(new), "the withdrawn draft does not refuse the tree's generator under a RELEASE.md"
    if old is not None:
        assert not refuses(old), "the mutant (the old guard) refuses as the new one does: the test would not see the defect"


# ------------------------------------------------------------------------------------------------------ (4) W130's correction 2
def t_r208_names_both_readings_at_their_lines():
    texts = _all_applied()
    reg = texts["v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"]
    m = re.search(r"\(R264 and C264 on record l8p's own board A composition, l8p_drafts\.out:(\d+); R603 and C607 on the connected "
                  r"candidate's full order, l9t5_connected\.out:(\d+)\)", reg)
    assert m, "R-208 lacks W130's words"
    row = [l for l in reg.splitlines() if l.startswith("| R-208 |")]
    assert len(row) == 1 and m.group(0) in row[0]
    l8p = open(os.path.join(REC, "l8p", "l8p_drafts.out"), encoding="utf-8").read().splitlines()
    con = open(os.path.join(REC, "l9t5", "l9t5_connected.out"), encoding="utf-8").read().splitlines()
    assert "(R264, C264)" in l8p[int(m.group(1)) - 1] and "apply_gen_sch_a_mainpb" in l8p[int(m.group(1)) - 1]
    assert "R603, C607 on MAIN_PB" in con[int(m.group(2)) - 1]
    # inserted after set 31's applied row WP-22 (its new text must stand once, test_w24l4e9), labelled, never inside it
    assert "its section 5 at `515f6cf2`) [restated 7 October 2026 by W130's correction 2, records/l4small: " + m.group(0) + "]" in row[0]
    oldrow = [l for l in open(os.path.join(ROOT, "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"), encoding="utf-8").read().splitlines()
              if l.startswith("| R-208 |")]
    if _state("l4small/apply_l4small_register.py") == "old":
        assert "R603 and C607" not in oldrow[0], "the predicate passes the old row"


# ----------------------------------------------------------------------------------------------- (5) the restated W11 check
def t_the_restated_generator_check_refuses_a_partial_application():
    """test_w11l9t5's restated check takes the generator at W11's base, swaps the rows' literals, W20's three and W133's three, and
    requires the tree's generator to equal the result: a tree generator carrying two of W133's three insertions must not"""
    texts = _all_applied()
    t = _mod("l4small/apply_l4small_tests.py", "l4small_tests_script")
    ns = {}
    exec(t.W133_LITS, ns)
    lits = ns["W133_LITS"]
    revx = _mod("l9t5/apply_l4small_revx.py", "l4small_revx_script")
    assert lits == [(o, n) for rel, o, n, _k in revx.EDITS if rel.endswith("l9t5_connected.py")], "the literals are not the edits"
    src = texts["v2/docs/records/l9t5/l9t5_connected.py"]
    base = src
    for o, n in lits:
        assert base.count(n) == 1
        base = base.replace(n, o)

    def restated_check(tree_src):
        swapped = base
        for o, n in lits:
            assert swapped.count(o) == 1
            swapped = swapped.replace(o, n)
        return swapped == tree_src
    assert restated_check(src), "the restated check refuses the applied generator"
    partial = base.replace(lits[0][0], lits[0][1]).replace(lits[1][0], lits[1][1])
    assert not restated_check(partial), "the restated check passes a generator with two of the three insertions (the mutant)"
    assert not restated_check(base), "the restated check passes the generator before the insertions"
    w11 = texts["v2/ecad/tools/tests/test_w11l9t5.py"]
    loop = w11.split("    for o, n in W133_LITS:", 1)
    assert len(loop) == 2 and loop[1].split("\n", 4)[3].startswith("    assert swapped == src"), "the loop is not right before the check"


def t_the_streams_files_are_framed():
    for rel in ["l4small/README.md", "l4small/l4small_edit.py"] + list(SCRIPTS):
        s = open(os.path.join(REC, rel), encoding="utf-8").read()
        assert not any(d in s for d in DASHES), rel
    s = open(os.path.abspath(__file__), encoding="utf-8").read()
    assert not any(d in s for d in DASHES)
    first = open(os.path.join(REC, "l4small", "README.md"), encoding="utf-8").readline()
    for w in ("DONE:", "NOT DONE:", "NEXT:"):
        assert w in first, w


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
