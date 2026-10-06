"""W9 (MESHSAT-1357, 6 October 2026): the recorded contradictions restated in record l9t5's hand pages (README.md, T10-ROUND5.md)
and record l8r2's page (L8R2-KNOWN-DEFECTS.md), held as predicates on their text.

The findings come from filed records: the remaining-engineering ledger's section 6, items A and B
(v2/docs/records/l4close/REMAINING-ENGINEERING.md, on the base); the DESK-gate draft's K-01 to K-28 (fnd/dgate 249e9e47), Slot K's
result draft 2 (fnd/recpack 35dca639) and Slot H's set 31 (fnd/l4e9s31 17ce29d5), cited as text only. The base is the set 30
integration commit 2c, 53a68c7c; the README's section W9 is the table of the items. The branch is adopted in the NEXT set with the
cascade: no generator, output or stability file is touched, and every line a page cites in an output is read here at the base
commit (`git show`), because the cascade regenerates the outputs.

The predicates: the second finding that Slot C's T10 page wrote as L9T5-F26 is L9T5-F28, the identifier is used for nothing else,
L9T5-F26 is J_PA's finding alone and the first text is kept only as quoted history; the connected generator's own reading of the T10
page (its two patterns, parsed with ast) still answers L9T5-F27; the return's two declared upper bounds are each stated with their
J_5V_IOC term as the outputs print them, the difference of the totals is the difference of that term, and each statement names the
figure it uses; the README's cap figure is the one the F01 outputs print, 15.1307 V named as 1c's; every E-1 outside the W9 section
names its record; route B2's owner-item words stand only as labelled history; record l8r2's desk drafts are bound to the register's
R-48 and R-190 rows as the base prints them; every cited output line holds its content at the base; no base line moved and no base
text was removed except the one listed swap of the cap figure; every quotation of the ledger found in these pages at the base is still
found; each predicate fails on the base text (the old state). These are software predicates on record text: they establish no
electrical or thermal property and close nothing; nothing in the kit has been built, bought, powered or measured.

Runs under the suite's runner (`python3 -u v2/ecad/tools/tests/run.py test_w9l9t5.`) and under pytest (each t_ function has a test_
alias)."""
import ast
import difflib
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import need, Skip  # noqa: E402

BASE = "53a68c7ce8a8b964d8d3905b4a769b50db096040"     # the set 30 integration commit 2c (the INBOX of W9)
REC = "v2/docs/records"
README = REC + "/l9t5/README.md"
T10R = REC + "/l9t5/T10-ROUND5.md"
CASES = REC + "/l9t5/L9T5-CASES.md"
L8R2 = REC + "/l8r2/L8R2-KNOWN-DEFECTS.md"
PAGES = (README, T10R, CASES, L8R2)
CON = REC + "/l9t5/l9t5_connected.out"
CONPY = REC + "/l9t5/l9t5_connected.py"
DIST = REC + "/l8r2/l8r2_dist.out"
P0 = REC + "/l8r2/l8r2_p0.out"
F01 = REC + "/l9t5/l9t5_f01.out"
F01D = REC + "/l9t5/l9t5_f01_drafts.out"
REG = REC + "/l4e9/DOWNSTREAM-REGISTER.md"
LEDGER = REC + "/l4close/REMAINING-ENGINEERING.md"
CX46 = REC + "/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md"
OWN = "v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md"
B2P = REC + "/l4e7/B2-PRESENCE.md"
OLD_F26 = "L9T5-F26 (Slot A, its `l9t5_connected.out` 193-199, 282-301, 350-352)"
CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)
DASHES = (chr(0x2013), chr(0x2014))
_C = {}


def _norm(t):
    return " ".join(t.split())


def tree(p):
    return open(need(os.path.join(ROOT, p), p), encoding="utf-8").read()


def at(rev, p):
    """the file p at a commit, read with git show; Skip when git or the commit is not here (a copy without history)"""
    k = (rev, p)
    if k not in _C:
        try:
            r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, p)], capture_output=True)
        except OSError:
            raise Skip("git is needed to read %s at %s" % (p, rev[:8]))
        if r.returncode != 0:
            raise Skip("%s at %s is not in this repository's objects" % (p, rev[:8]))
        _C[k] = r.stdout.decode("utf-8")
    return _C[k]


def line(text, n):
    return text.splitlines()[n - 1]


def _section(text, head):
    return text.split(head, 1)[1] if head in text else ""


def _outside_w9(text):
    """a page's text without its W9 section (that section quotes the old texts in its table)"""
    for head in ("\n## W9 (6 October 2026)", "\n## 8. W9 (6 October 2026)"):
        text = text.split(head, 1)[0]
    return text


# ------------------------------------------------------------------------------------------- item A: one identifier, two findings
def _f26_collision(t10, readme):
    """True while T10-ROUND5.md names a finding of its own L9T5-F26 (outside the quoted first text) or L9T5-F28 is missing or
    README's L9T5-F26 is not J_PA's finding"""
    body = _outside_w9(t10)
    own = _norm(body).replace(_norm('"%s"' % OLD_F26), "")
    renamed = "L9T5-F28 (Slot A; renamed from L9T5-F26" in _norm(body)
    other_f26 = re.findall(r"L9T5-F26(?! is Slot A's finding on J_PA)", own.replace("renamed from L9T5-F26", ""))
    jpa = "**Finding L9T5-F26 (Layer 7, the harness; Layer 6):** J_PA" in readme
    return bool(other_f26) or not renamed or not jpa


def t_item_a_the_second_l9t5_f26_is_l9t5_f28():
    t10, readme = tree(T10R), tree(README)
    assert not _f26_collision(t10, readme), "T10-ROUND5.md still names a second finding L9T5-F26"
    assert _f26_collision(at(BASE, T10R), at(BASE, README)), "the predicate does not fail on the base text (the old state)"
    assert _norm('"%s"' % OLD_F26) in _norm(t10), "the first text is not kept as quoted history"
    n227 = line(t10, 227)
    assert "L9T5-F28 (Slot A; renamed from L9T5-F26" in n227, "line 227, which the README cites, does not carry L9T5-F28"
    f26 = readme.split("**Finding L9T5-F26 (Layer 7, the harness; Layer 6):**", 1)[1].split("\n\n", 1)[0]
    for s_ in ("L9T5-F28", "`T10-ROUND5.md` line 227", "lines 192, 347 and 356 to 358 at 53a68c7c"):
        assert s_ in _norm(f26), "README's L9T5-F26 lacks %r" % s_
    # the identifier is new: no other record, test or generator in the tree uses L9T5-F28 (this module and the two pages aside)
    mine = {os.path.normpath(os.path.join(ROOT, p)) for p in (README, T10R)} | {os.path.abspath(__file__)}
    hits = []
    for top in ("v2/docs", "v2/ecad/tools"):
        for d, _s, fs in os.walk(os.path.join(ROOT, top)):
            for f in fs:
                if f.endswith((".md", ".py", ".out", ".yaml", ".txt")):
                    p = os.path.normpath(os.path.join(d, f))
                    if p not in mine:
                        try:
                            if "L9T5-F28" in open(p, encoding="utf-8", errors="replace").read():
                                hits.append(os.path.relpath(p, ROOT))
                        except OSError:
                            pass
    assert not hits, "L9T5-F28 is used elsewhere: %s" % hits[:5]
    assert all("L9T5-F28" not in at(BASE, p) for p in PAGES), "L9T5-F28 already existed at the base"


def t_item_a_the_connected_generator_still_answers_l9t5_f27():
    """l9t5_connected.py reads T10-ROUND5.md for its L9T5-F27 predicate; its two patterns, parsed with ast, still read 'renamed'"""
    tr = ast.parse(tree(CONPY))
    pats = []
    for node in ast.walk(tr):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "search"
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "re" and len(node.args) >= 2
                and isinstance(node.args[1], ast.Name) and node.args[1].id == "r5" and isinstance(node.args[0], ast.Constant)):
            pats.append(node.args[0].value)
    assert len(pats) == 2, "the generator's reading of the T10 page changed: %s" % pats
    t10 = tree(T10R)
    assert re.search(pats[0], t10, re.M) is not None and not re.search(pats[1], t10, re.M), "the generator would read F27 OPEN"


# ------------------------------------------------------------------------------- item B: two figures for the return's upper bound
def _bounds(dist, p0):
    m = re.search(r"^   the declared upper bound \(every lead at its declared peak, the composed intent\): ([\d.]+) A \((.*?)\)$", dist, re.M)
    leads = dict((k, float(v)) for k, v in re.findall(r"(J_\w+) ([\d.]+)", m.group(2)))
    n = re.search(r"the declared upper bound \(i\) ([\d.]+);", p0)
    u = re.search(r"read by the record's constant-power method as U601 [\d.]+ A in place of ([\d.]+) A", p0)
    return float(m.group(1)), leads, float(n.group(1)), float(u.group(1))


def _item_b_stated(readme, l8r2, study, ioc_s, onenode, ioc_n):
    s_, n_, i_s, i_n = "%.4f A" % study, "%.4f" % onenode, "%.4f A" % ioc_s, "%.4f A" % ioc_n
    r59 = line(readme, 59)
    q2 = [l for l in readme.splitlines() if l.startswith("  holds, the declared upper bound's included")]
    h = _section(l8r2, "## 3h. P0 round").split("\n## 4. ")[0]
    ok = (all(x in r59 for x in (n_ + " A in this one-node model", s_, i_s, i_n, "`l8r2_p0.out` section 1", "`l8r2_dist.out` line 86"))
          and len(q2) == 1 and s_ in q2[0] and "not a case the study solves" in q2[0]
          and ("prints as %s among its totals in A" % n_) in h and s_ in h
          and ("this study's declared upper bound is %s" % s_) in _norm(h) and "a case this study does not solve" in _norm(h))
    return ok


def t_item_b_both_upper_bounds_stated_with_their_bases():
    study, leads, onenode, ioc_n = _bounds(tree(DIST), tree(P0))
    ioc_s = leads["J_5V_IOC"]
    assert abs(study - sum(leads.values())) < 1e-3, "the study's total is not its leads' sum"
    # the totals differ by exactly the J_5V_IOC term: 1.3800 A in the study, U601's declared peak 1.4749 A in the one-node model
    assert abs((onenode - study) - (ioc_n - ioc_s)) < 1e-3, (onenode, study, ioc_n, ioc_s)
    assert "its declared peak %.4f A" % ioc_n in line(at(BASE, CON), 151), "l9t5_connected.out line 151 at the base"
    assert _item_b_stated(tree(README), tree(L8R2), study, ioc_s, onenode, ioc_n), "a page lacks a figure, its basis or its use"
    assert not _item_b_stated(at(BASE, README), at(BASE, L8R2), study, ioc_s, onenode, ioc_n), "the predicate passes the base text"
    # the section 3h figures keep test_l8r2's rule: every figure with a unit is printed by l8r2_p0.out or l8r2_dist.out
    h = _section(tree(L8R2), "## 3h. P0 round").split("\n## 4. ")[0]
    figs = sorted(set(re.findall(r"\d+\.\d+ (?:A|V|mOhm)\b", h)))
    assert not [f for f in figs if f not in tree(P0) + tree(DIST)]


# -------------------------------------------------------------------------------------- the cap figure, E-1, route B2, K-07
def _cap_ok(readme):
    l46 = line(readme, 46)
    return (l46.find("15.1308 V on the MODEL as `l9t5_f01_drafts.out` section 5") >= 0 and "15.1307 V was 1c's figure at 88ffe53b" in l46
            and "15.1307 V on the MODEL" not in l46)


def t_the_cap_figure_is_the_one_the_f01_outputs_print():
    need_ = re.search(r"need ([\d.]+) V, a MODEL margin", tree(F01)).group(1)
    assert need_ == "15.1308" and ("need %s V" % need_) in tree(F01D), "the F01 outputs print another figure"
    assert "need 15.1308 V" in line(at(BASE, F01), 145) and "need 15.1308 V" in line(at(BASE, F01D), 56)
    assert "need 15.1307 V" in at("88ffe53b", F01D), "1c's figure at 88ffe53b"
    assert _cap_ok(tree(README)) and not _cap_ok(at(BASE, README))


def _e1_named(text):
    """every E-1 outside the W9 section names its record in the same sentence span"""
    t = _norm(_outside_w9(text))
    for m in re.finditer(r"\bE-1\b", t):
        win = t[max(0, m.start() - 20):m.end() + 20]
        if "l4e7" not in win and "l9stk" not in win:
            return False
    return True


def t_every_e1_names_its_record():
    for p in PAGES:
        assert _e1_named(tree(p)), "%s names an E-1 without its record" % p
    assert not _e1_named(at(BASE, README)), "the predicate passes the base README"
    reg = at(BASE, REG)
    assert "l9stk's E-1" in line(reg, 255) and "l4e7's E-1" in line(reg, 336)


def _b2_ok(readme):
    body = _outside_w9(readme)
    ls = [l for l in body.splitlines() if "the owner's item" in l]
    return bool(ls) and all("as written before cx46" in l and "UNSELECTED and WITHDRAWN AS DRAFTED with no owner item" in l for l in ls)


def t_route_b2_carries_no_owner_item_outside_labelled_history():
    assert _b2_ok(tree(README)) and not _b2_ok(at(BASE, README))
    assert "B2-PRESENCE.md" in line(at(BASE, CX46), 203)
    assert "B2 need not remain an outstanding owner action" in line(at(BASE, OWN), 834)
    assert "UNSELECTED and WITHDRAWN AS DRAFTED" in _norm("\n".join(at(BASE, B2P).splitlines()[0:4]))


def _k07_ok(page):
    l = _norm(" ".join(page.splitlines()[9:11]))
    return ("This record corrects P1-2, P1-3" in l and "in DRAFT: nothing is applied and no independent check has accepted these drafts" in l
            and '"FIX: CHECK and APPLY record l8r2\'s"' in l and '"drafted at the desk, not applied, not independently checked"' in l)


def t_l8r2s_desk_drafts_are_bound_to_the_register():
    assert _k07_ok(tree(L8R2)) and not _k07_ok(at(BASE, L8R2))
    reg = at(BASE, REG)
    for n, rid in ((154, "| R-48 |"), (286, "| R-190 |")):
        l = line(reg, n)
        assert l.startswith(rid) and "FIX: CHECK and APPLY record l8r2's" in l and "drafted at the desk, not applied, not independently checked" in l


# ------------------------------------------------------------------------------------------------ citations, moves and removals
def t_every_cited_output_line_holds_at_the_base():
    con, con4 = at(BASE, CON), at("4d0ff8a2", CON)
    assert all("L9T5-F26" in line(con, n) for n in (192, 347, 356))
    assert line(con, 194).startswith("   the thermal guard on the battery FETs") and line(con, 204).startswith("   the solar entry")
    assert line(con, 293).startswith("   THE FINAL FIGURES") and "PROVISIONAL on V-T10-DROP)" in line(con, 317)
    assert [line(con, n).split()[0:3] for n in (387, 388, 390)] == [["every", "revision", "V"], ["the", "final", "R602"], ["L9T5-F22", "judged", "over"]]
    # the first text's ranges at 4d0ff8a2: the guard row, the final figures, the T10 predicates
    assert "check_l8p_fs.py" in line(con4, 193) and line(con4, 282).startswith("   THE FINAL FIGURES")
    assert line(con4, 350).startswith("   every revision V T10 row holds")
    dist = at(BASE, DIST)
    assert [line(dist, n).split(":")[0].strip()[:20] for n in (59, 68, 77, 86)] == [
        "C-DEV rev 2 (the act", "C-DEV rev 1 (the lab", "the largest steady s", "the declared upper b"]
    assert "27.8159 A" in line(dist, 86) and "J_5V_IOC 1.3800" in line(dist, 86)
    assert "the declared upper bound (i) 27.9108" in line(at(BASE, P0), 21)
    rb = at(BASE, README)
    assert "Finding L9T5-F26" in line(rb, 194) and "1x4 VH" in line(rb, 196)


def t_no_base_line_moved_and_nothing_removed_but_the_cap_swap():
    allowed = {(README, 46): {"7", "15.1308 V "}}
    for p in (README, T10R, L8R2, CASES):
        b, t = at(BASE, p).splitlines(), tree(p).splitlines()
        assert len(t) >= len(b), "%s lost lines" % p
        for i, x in enumerate(b):
            y = t[i]
            if x == y:
                continue
            sm = difflib.SequenceMatcher(a=x, b=y, autojunk=False)
            gone = {x[i1:i2] for tag, i1, i2, _j1, _j2 in sm.get_opcodes() if tag in ("delete", "replace")}
            assert gone <= allowed.get((p, i + 1), set()), "%s line %d lost %r" % (p, i + 1, sorted(gone)[:3])
        added = "\n".join(t[len(b):])
        assert not CLAIM.search(added) and not any(d in added for d in DASHES), "%s: the appended text" % p


def t_the_ledgers_quotations_in_these_pages_stay_found():
    led = at(BASE, LEDGER)
    pos = [i for i, c in enumerate(led) if c == '"']
    quotes = [_norm(led[i + 1:j]) for i, j in zip(pos[0::2], pos[1::2])]
    base = [_norm(at(BASE, p)) for p in PAGES]
    now = [_norm(tree(p)) for p in PAGES]
    found = [q for q in quotes if len(q) >= 12 and any(q in c for c in base)]
    assert found, "no ledger quotation reads these pages"
    lost = [q for q in found if not any(q in c for c in now)]
    assert not lost, "ledger quotations no longer found: %s" % [q[:60] for q in lost[:3]]


def t_the_w9_records_are_stated_and_framed():
    readme = tree(README)
    first = readme.splitlines()[0]
    for s_ in ("W9 (6 October 2026", "adopted in the NEXT set", "DONE:", "NOT DONE:", "NEXT:", "CANDIDATE READY 3: ac8efbca"):
        assert s_ in first, s_
    w9 = _section(readme, "\n## W9 (6 October 2026)")
    rows = re.findall(r"^\| (W9-\d\d) \|", w9, re.M)
    assert rows == ["W9-%02d" % i for i in range(1, 13)], rows
    for s_ in ("Adopted in the NEXT set", "nothing accepted, closed or released", "built,\nbought, powered or measured", "K-09", "K-26", "K-28"):
        assert s_ in w9, s_
    for p in (T10R, L8R2):
        assert "W9 (6 October 2026)" in tree(p) and "adopted in the NEXT set" in tree(p)
    for p in (os.path.abspath(__file__),):
        s = open(p, encoding="utf-8").read()
        assert not any(d in s for d in DASHES), "a dash in this module"


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
