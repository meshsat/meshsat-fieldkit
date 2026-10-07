"""W11 (MESHSAT-1357, 6 October 2026): record l9t5's statements that still described L4-E9's change list as unapplied, or L4-E9's
output as refusing at its L4-E11 pin, restated for the NEXT set, held as predicates on their text.

The facts come from this tree: set 30's integration commit 7070f106 applied the change list (the register's rows R-220 to R-245, the
page's P0 note, the draft's applied_state() and its --check); set 31's run of L4-E9's generator (records/l4e9/SET31-CHANGES.md lines
20 to 25, the four cascade pins of l4e9_power_path.out); cx46's verdict (CORRECTIONS NOT CLOSED) and the remaining-engineering
ledger's classes; l9t5_t10.out's 10j (f) and 10j disposition. The DESK-gate draft's K-26 and K-28 (fnd/dgate 249e9e47) are cited as
text only. The base is W9's tip, 02b0d30d (the INBOX of W11).

The predicates: README lines 1, 76 and 158 keep their old words, each labelled with the round that wrote them and followed by the
restatement (APPLIED by the integrator at 7070f106; applying the rows accepts no draft; the claims OPEN or PROVISIONAL as the ledger
classes them; L4-E9's generator re-pinned at 2a and its output regenerated in set 31 with its four cascade pins); no unlabelled stale
statement stands outside the W9 and W11 sections; the connected generator's section 11 literals carry the new T10 and change-list
rows and none of the old words, with the same number of printed lines; the committed output carries either the old rows (before the
cascade regenerates it) or exactly the generator's new rows, never a mixture or another text; every ledger quotation found in the
connected output at the base is still found with the new rows; every cited source line holds its content; no base line of the README
moved and no base text was removed; each predicate on the pages fails on the base text (the old state). These are software
predicates on record text: they establish no electrical or thermal property and close nothing; nothing in the kit has been built,
bought, powered or measured.

Runs under the suite's runner (`python3 -u v2/ecad/tools/tests/run.py test_w11l9t5.`) and under pytest (each t_ function has a test_
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

BASE = "02b0d30de657c06190600f708a67d24500c0484d"     # W9's tip, fnd/w9l9t5 (the INBOX of W11)
APPLIED = "7070f106"                                   # set 30's integration commit 1, which applied the change list
REC = "v2/docs/records"
README = REC + "/l9t5/README.md"
CON = REC + "/l9t5/l9t5_connected.out"
CONPY = REC + "/l9t5/l9t5_connected.py"
DRAFT = REC + "/l9t5/apply_l4e9_changelist_p0.py"
T10 = REC + "/l9t5/l9t5_t10.out"
REG = REC + "/l4e9/DOWNSTREAM-REGISTER.md"
PAGE = REC + "/l4e9/L4-POWER-ARCHITECTURE.md"
L4O = REC + "/l4e9/l4e9_power_path.out"
S31 = REC + "/l4e9/SET31-CHANGES.md"
LEDGER = REC + "/l4close/REMAINING-ENGINEERING.md"
CX46 = REC + "/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md"
CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)
DASHES = (chr(0x2013), chr(0x2014))

# the connected output's two rows as the base prints them (lines 350 to 352 and 361 to 362) and as the generator prints them now
OLD_T10 = [
    "   T10: L9T5-F06 OPEN pending its independent check; rev X on V-B20; the containment (Slot C's round 6, composed here) CORRECTED IN",
    "     DRAFT, UNCHECKED, its qualification limits (the LDO's resistance and Zth on board B) and the VOS0 residual handed over (10j (e));",
    "     L9T5-F27, the decision identifier both records use (10)",
]
NEW_T10 = [
    "   T10: L9T5-F06 OPEN pending its independent check; revision X HELD with no admission route (round 5's V-B20 route SUPERSEDED, 10j (f));",
    # restated by W41 (6 October 2026; basis: W38's F10, the checks as received: cx45 reads "P0-3: NOT CONFIRMED" [CX45:10], "NOT
    # CLOSED" is cx46's word for items 5 to 8 [CX46:136-151]): each word attributed to its check
    "     the containment (Slot C's round 6, composed here) drafted, composed, read by pin and mutated; Q3: cx45 'P0-3: NOT CONFIRMED',"
    " cx46's items 5 to 8 'NOT CLOSED' (10j, after cx46);",
    "     its qualification limits (the LDO's resistance and Zth on board B) and the VOS0 residual handed over (10j (e)); L9T5-F27, the decision"
    " identifier both records use (10)",
]
OLD_CL = [
    "   L4-E9's change-list rows: drafted (apply_l4e9_changelist_p0.py), applied by the integrator with the re-takes it names (L4-E11's",
    "     and L4-E10's pins of the page, Layer 6's l6r2_passives compositions); L4-E9's own output refuses on this tree at its L4-E11 pin",
]
NEW_CL = [
    "   L4-E9's change-list rows: drafted here (apply_l4e9_changelist_p0.py), APPLIED by the integrator at set 30's integration commit"
    " 7070f106 to L4-E9's",
    "     register, script and page; applying them accepts no draft (cx46: CORRECTIONS NOT CLOSED; the claims read OPEN or PROVISIONAL as"
    # restated by W41 (6 October 2026; basis: W38's F4): the four pins are the cascade's current digests, named by their PINS keys in
    # l4e9_power_path.py (re-pinned by the chain, refused when an output differs: its load_inputs), not 2b's; "set 31" is this lineage,
    # and record l4e9's own SET31-CHANGES.md (merged at 6fe398e9) is named apart
    " above); L4-E9's generator re-pinned at 2a (bbba3e53), its output regenerated in set 31 (this lineage, fnd/int31regen) with its"
    " four cascade pins (PINS l4e10, l4e11, l4e12, l4e7p0) at those outputs' current digests, which the chain re-pins, refusing at a"
    " pin whose output differs (first regenerated at commit 2b's digests by record l4e9's SET31-CHANGES.md, merged at 6fe398e9)",
]
# W20's three generator literals of section 11, applied verbatim by f08dbb97 (set 31, W20's rows) after W11's tip; the generator
# check below swaps them too (restated by W41, 6 October 2026; basis: f08dbb97's diff of l9t5_connected.py, the filed change).
W20_LITS = [
    ("   script with this record's text draft apply_l4e9_changelist_p0.py applied in memory (V6-m11: rows R-220 to R-245 for the drafts",
     "   script, which carry this record's text draft apply_l4e9_changelist_p0.py (V6-m11: rows R-220 to R-245 for the drafts that had none)"),
    ("   that had none; the tree's files unchanged until the integrator applies it with the re-takes the draft names): %d changes, every",
     "   as the integrator applied it at 7070f106, read from the tree (the draft's applied state), set 31's R-246 with them: %d changes, every"),
    ("     sustained, 150 C transient); rev Y's rows, the cover for a rev X part, at 14.0 k: %s over (%s): rev X stays on V-B20",
     "     sustained, 150 C transient); rev Y's rows, the cover for a rev X part, at 14.0 k: %s over (%s): revision X stays HELD with no"
     " admission route (round 5's V-B20 route SUPERSEDED, 10j (f))"),
]
# W11's tip: the W11 section of the README says its line numbers are this branch's (restated by W41, see t_every_cited_source_line_holds)
W11_TIP = "85b6f25836f8a4e8312181efbad89976f212672c"
STALE_CON = ("rev X on V-B20", "CORRECTED IN", "own output refuses on this tree", "applied by the integrator with the re-takes")
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


def _outside(text):
    """the README without its W9 and W11 sections (both quote the old texts in their tables); W11 follows W9"""
    return text.split("\n## W9 (6 October 2026)", 1)[0]


# ------------------------------------------------------------------------------------------------------ the README's three lines
LABELS = {
    # stale words -> the label and restatement every line carrying them must also carry
    "it is the integrator's to apply": "it is the integrator's to apply (as written in round 4c, before set 30's integration; W11: APPLIED "
                                       "since, by the integrator, at set 30's integration commit 7070f106",
    "refuses at its L4-E11 pin": "refuses at its L4-E11 pin [as written in the cx45 correction set, before set 30's integration; W11: the "
                                 "change list APPLIED since at 7070f106",
    "change-list rows a draft for the integrator": "change-list rows a draft for the integrator (as written at CANDIDATE READY 3, before "
                                                   "set 30's integration; W11: APPLIED since, by the integrator, at set 30's integration "
                                                   "commit 7070f106)",
}


def _stale_unlabelled(readme):
    """the lines outside the W9 and W11 sections that carry a stale statement without its label and restatement"""
    bad = []
    for i, l in enumerate(_outside(readme).splitlines(), 1):
        for stale, label in LABELS.items():
            if stale in l and label not in l:
                bad.append((i, stale))
    return bad


def _restated(readme):
    """README lines 1, 76 and 158 carry the restatement with its sources"""
    l1, l76, l158 = line(readme, 1), line(readme, 76), line(readme, 158)
    return (l1.startswith("W11 (6 October 2026, `fnd/w11l9t5` from W9's tip 02b0d30d, adopted in the NEXT set with the cascade): DONE:")
            and all(s in l1 for s in ("NOT DONE:", "NEXT:", LABELS["change-list rows a draft for the integrator"], "W9 (6 October 2026"))
            and all(s in l76 for s in (LABELS["it is the integrator's to apply"], "rows R-220 to R-245 with no R-241",
                                       "`records/l4e9/DOWNSTREAM-REGISTER.md` lines 316 to 340", "`records/l4e9/L4-POWER-ARCHITECTURE.md` line 422",
                                       "`applied_state()` reads, its lines 107 to 127", "its `--check` printing APPLIED BEFORE",
                                       "applying the rows accepts no draft", "read OPEN or PROVISIONAL",
                                       "`records/l4close/REMAINING-ENGINEERING.md` section 4", "its lines 566 to 581",
                                       "CORRECTIONS NOT CLOSED)"))
            and all(s in l158 for s in (LABELS["refuses at its L4-E11 pin"], "re-pinned at set 30's integration commit 2a, bbba3e53",
                                        "regenerated in set 31 through `_bin/regen_out.py`", "lines 55, 64, 67 and 106",
                                        "the digests of the coordinator's commit 2b", "it refuses at those four pins",
                                        "`records/l4e9/SET31-CHANGES.md` lines 20 to 25]")))


def t_the_readme_restates_the_change_list_as_applied():
    readme = tree(README)
    assert _restated(readme), "README lines 1, 76 or 158 lack the restatement or a source"
    assert not _stale_unlabelled(readme), "a stale statement stands unlabelled: %s" % _stale_unlabelled(readme)
    base = at(BASE, README)
    assert not _restated(base), "the restatement predicate passes the base text"
    assert len(_stale_unlabelled(base)) == 3, "the base carries %s, not the three stale statements" % _stale_unlabelled(base)
    # never closed, never accepted: the inserted words (the README's text not in the base) carry no closure or acceptance claim
    sm = difflib.SequenceMatcher(a=base, b=readme, autojunk=False)
    added = " ".join(readme[j1:j2] for tag, _i1, _i2, j1, j2 in sm.get_opcodes() if tag in ("insert", "replace"))
    rest = _norm(added)
    for ok in ("nothing accepted, closed or released", "accepts no draft", "NOT CLOSED"):
        rest = rest.replace(ok, "")
    left = re.findall(r"\b(closed|closes|close|accepted|accepts|released|releases)\b", rest, re.I)
    assert not left, "the inserted text says %s" % sorted(set(left))
    assert not CLAIM.search(added) and not any(d in added for d in DASHES), "the inserted text"


def t_no_base_line_moved_and_nothing_removed():
    b, t = at(BASE, README).splitlines(), tree(README).splitlines()
    assert len(t) >= len(b), "the README lost lines"
    changed = []
    for i, x in enumerate(b):
        y = t[i]
        if x == y:
            continue
        sm = difflib.SequenceMatcher(a=x, b=y, autojunk=False)
        gone = [x[i1:i2] for tag, i1, i2, _j1, _j2 in sm.get_opcodes() if tag in ("delete", "replace")]
        assert not gone, "README line %d lost %r" % (i + 1, gone[:3])
        changed.append(i + 1)
    assert changed == [1, 76, 158], changed
    added = "\n".join(t[len(b):])
    assert added.lstrip("\n").startswith("## W11 (6 October 2026)"), "the appended text is not the W11 section"
    assert not CLAIM.search(added) and not any(d in added for d in DASHES), "the appended text"


def t_the_w11_section_is_stated_and_framed():
    w11 = tree(README).split("\n## W11 (6 October 2026)", 1)
    assert len(w11) == 2, "no W11 section"
    w11 = w11[1]
    rows = re.findall(r"^\| (W11-\d\d) \|", w11, re.M)
    assert rows == ["W11-%02d" % i for i in range(1, 6)], rows
    flat = _norm(w11)
    for s_ in ("Adopted in the NEXT set, with the cascade.", "nothing accepted, closed or released", "built, bought, powered or measured",
               "K-26", "K-28", "**The connected output is left as committed.**", "regen_out: REFUSED, R1 run 1 exited 1",
               "the refusal is not a stale pin", "**Left out", "`l9t5_connected.py` line 518", "`l9t5_connected.py` line 843"):
        assert s_ in flat, s_
    s = open(os.path.abspath(__file__), encoding="utf-8").read()
    assert not any(d in s for d in DASHES), "a dash in this module"


# --------------------------------------------------------------------------------------------- the generator's section 11 literals
def _section11_calls(src):
    """the w(...) calls of section 11 in order: a str for a constant argument, None for a formatted one"""
    tr = ast.parse(src)
    calls = []
    for node in ast.walk(tr):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "w" and len(node.args) == 1:
            a = node.args[0]
            calls.append((node.lineno, a.value if isinstance(a, ast.Constant) and isinstance(a.value, str) else None))
    calls.sort()
    texts = [c[1] for c in calls]
    i = [k for k, x in enumerate(texts) if x and x.startswith("11. THE CONNECTED VERDICT")]
    j = [k for k, x in enumerate(texts) if x == "12. THE PREDICATES"]
    assert len(i) == 1 and len(j) == 1, "section 11's bounds are not read"
    return calls[i[0]:j[0]]


def _gen_ok(src):
    sec = _section11_calls(src)
    lits = [x for _n, x in sec]
    # The run is matched at the length of the run it is looked for (set 31's candidate d0e283aa failed test_rule_windows on the fixed
    # `k:k + 3` and `k:k + 2`, 6 Oct 2026; the comparison is the same exact subsequence match, its size read from its subject).
    ok_new = (any(lits[k:k + len(NEW_T10)] == NEW_T10 for k in range(len(lits)))
              and any(lits[k:k + len(NEW_CL)] == NEW_CL for k in range(len(lits))))
    stale = [s for x in lits if x for s in STALE_CON if s in x]
    return ok_new and not stale


def _without_round10(src):
    """W151's round 10 (7 October 2026, Layer 4 task L4A-61; record l9t5 T10-ROUND10.md): an additive section 11a after section 11,
    printed by one call and one appended block of functions, held by its own predicates (test_l9t5_rowb.py). It is taken out here,
    exactly and once, so this module keeps holding W11's change and nothing else against the base."""
    call = "        rowb_section(w, FC, t14, FR, P)\n"
    mark = "\n\n# " + "=" * 134 + "\n# ROUND 10 (7 October 2026, W151"
    if call not in src and mark not in src:
        return src
    assert src.count(call) == 1 and src.count(mark) == 1, "round 10's call or block is not in the generator once"
    head, tail = src.split(mark, 1)
    assert "\n\n\nif __name__ == \"__main__\":" in tail, "round 10's block is not the generator's last before its entry point"
    return head.replace(call, "").rstrip("\n") + "\n\n\nif __name__ == \"__main__\":" + tail.split("\n\n\nif __name__ == \"__main__\":", 1)[1]


def t_the_generator_prints_the_restated_rows():
    src = _without_round10(tree(CONPY))
    assert _gen_ok(src), "the generator's section 11 lacks a new row or keeps a stale word"
    base = at(BASE, CONPY)
    assert not _gen_ok(base), "the predicate passes the base generator"
    # the same number of printed lines in section 11, so every later line of the output keeps its number
    assert len(_section11_calls(src)) == len(_section11_calls(base))
    # nothing else of the generator changed: the base with the two blocks swapped is the tree's generator
    swapped = base
    for old, new in ((OLD_T10, NEW_T10), (OLD_CL, NEW_CL)):
        for o, n in zip(old, new):
            assert swapped.count('w("%s")' % o) == 1, o[:40]
            swapped = swapped.replace('w("%s")' % o, 'w("%s")' % n)
    for o, n in W20_LITS:
        assert swapped.count('w("%s"' % o) == 1, o[:40]
        swapped = swapped.replace('w("%s"' % o, 'w("%s"' % n)
    assert swapped == src, "the generator differs from the base in more than the two rows' literals and W20's three"
    ast.parse(src)
    assert not CLAIM.search("\n".join(NEW_T10 + NEW_CL)) and not any(d in "".join(NEW_T10 + NEW_CL) for d in DASHES)


# ------------------------------------------------------------------------------------- the committed output, before or after the cascade
def _blocks(text):
    ls = text.splitlines()
    i = [k for k, l in enumerate(ls) if l.startswith("   T10: L9T5-F06 OPEN pending its independent check;")]
    j = [k for k, l in enumerate(ls) if l.startswith("   L4-E9's change-list rows:")]
    if len(i) != 1 or len(j) != 1:
        return None
    return ls[i[0]:i[0] + 3], ls[j[0]:j[0] + 2]


def _out_state(text):
    """'old' while the committed output predates the cascade, 'new' once it is the generator's, None for anything else"""
    b = _blocks(text)
    if b is None:
        return None
    if b == (OLD_T10, OLD_CL):
        return "old"
    sec = text.split("11. THE CONNECTED VERDICT", 1)[-1].split("12. THE PREDICATES", 1)[0]
    if b == (NEW_T10, NEW_CL) and not any(s in sec for s in STALE_CON):
        return "new"
    return None


def t_the_output_is_the_base_or_the_generators_rows():
    text = tree(CON)
    assert _out_state(text) in ("old", "new"), "the connected output's two rows are neither the committed nor the generator's"
    base = at(BASE, CON)
    assert _out_state(base) == "old" and line(base, 350) == OLD_T10[0] and line(base, 361) == OLD_CL[0]
    new = base
    for old, nw in ((OLD_T10, NEW_T10), (OLD_CL, NEW_CL)):
        new = new.replace("\n".join(old), "\n".join(nw))
    assert _out_state(new) == "new" and len(new.splitlines()) == len(base.splitlines())
    mixed = base.replace("\n".join(OLD_T10), "\n".join(NEW_T10))
    assert _out_state(mixed) is None, "a mixture of the two generators' rows must be refused"
    tampered = new.replace("revision X HELD with no admission route", "rev X on V-B20")
    assert _out_state(tampered) is None, "a changed new row must be refused"


def t_the_ledgers_quotations_in_the_output_stay_found():
    """every quotation of the remaining-engineering ledger found in the connected output at the base is found with the new rows too"""
    led = tree(LEDGER)
    pos = [i for i, c in enumerate(led) if c == '"']
    quotes = [_norm(led[i + 1:j]) for i, j in zip(pos[0::2], pos[1::2])]
    base = at(BASE, CON)
    new = base
    for old, nw in ((OLD_T10, NEW_T10), (OLD_CL, NEW_CL)):
        new = new.replace("\n".join(old), "\n".join(nw))
    found = [q for q in quotes if len(q) >= 12 and q in _norm(base)]
    assert found, "no ledger quotation reads the connected output"
    lost = [q for q in found if q not in _norm(new)]
    assert not lost, "ledger quotations lost with the new rows: %s" % [q[:60] for q in lost[:3]]
    # the README keeps every ledger quotation it held at the base
    rb, rt = _norm(at(BASE, README)), _norm(tree(README))
    lost = [q for q in quotes if len(q) >= 12 and q in rb and q not in rt]
    assert not lost, "ledger quotations lost from the README: %s" % [q[:60] for q in lost[:3]]


# --------------------------------------------------------------------------------------------------------------- the cited sources
def t_every_cited_source_line_holds():
    # Restated by W41 (6 October 2026). Basis: the W11 section of the README says "line numbers are this branch's" (W11's tip
    # 85b6f258), and filed set 31 changes moved the cited lines since: the ledger (99bbc0c6, 92b754c5, b76c1480 and main's 836f711b
    # through d5d9c252: section 1 at 103, section 4 at 652, section 5 at 670) and the draft (f08dbb97). So the cited lines are read
    # at W11's tip, where they were cited, and the tree is held to carry the same headings and the twelve OPEN or PROVISIONAL states.
    tree_led = tree(LEDGER)
    for h in ("## 1. The twelve cx46 findings NOT CLOSED, each a REMAINING ENGINEERING item", "## 4. The claims a remaining item weakens",
              "## 5. Summary"):
        assert ("\n" + h) in tree_led, h
    s4 = tree_led.split("\n## 4. The claims a remaining item weakens", 1)[1].split("\n## 5. Summary", 1)[0]
    rows = [l.split(" | ")[3] for l in s4.splitlines() if l.startswith("| ") and not l.startswith("| Claim") and "---" not in l]
    # thirteen on the tree: W11's twelve and the ledger's HO-L row for E11-37 (99bbc0c6), every one OPEN or PROVISIONAL
    assert len(rows) == 13 and all(("OPEN" in s or "PROVISIONAL" in s) for s in rows), rows

    def cited(p):    # the cited lines at W11's tip (Skip without that commit)
        return at(W11_TIP, p)
    reg = cited(REG)
    ids = [line(reg, n).split(" | ")[0][2:] for n in range(316, 341)]
    assert ids == ["R-%d" % n for n in range(220, 246) if n != 241], ids
    assert line(cited(PAGE), 422).startswith("**The P0 round (record l9t5, Slot A, 5 October 2026;")
    dr = cited(DRAFT)
    assert line(dr, 107) == "def applied_state(root):" and "set 30's integration commit 7070f106 wrote the three files" in line(dr, 108)
    assert line(dr, 127) == "    return {p_reg: reg, p_py: py, p_page: page}, ch, m"
    assert "NOT APPLIED to the tree by this record" in line(dr, 3)
    s31 = cited(S31)
    assert "refuses at its pins of four cascade outputs (l4e10, l4e11, l4e12 and L4-E7's" in line(s31, 20)
    assert "2a pinned at the bytes of the coordinator's commit 2b" in line(s31, 21)
    assert "The committed `l4e9_power_path.out` (regen_out: replaced, twice byte-identical, every printed pin current)" in line(s31, 24)
    l4o = cited(L4O)
    for n, k, p in ((55, "l4e10", "l4e10_cell_thermal.out"), (64, "l4e11", "l4e11_power.out"), (67, "l4e12", "l4e12_thermal.out"),
                    (106, "l4e7p0", "l4e7_p0sol.out")):
        f = line(l4o, n).split()
        assert f[0] == k and f[2].endswith(p), (n, f)
    assert '"summary": "P0 RECHECK: CORRECTIONS NOT CLOSED.' in line(cited(CX46), 10)
    led = cited(LEDGER)
    assert line(led, 85).startswith("## 1. The twelve cx46 findings NOT CLOSED, each a REMAINING ENGINEERING item")
    assert line(led, 566).startswith("## 4. The claims a remaining item weakens") and line(led, 583) == "## 5. Summary"
    states = [l.split(" | ")[3] for l in led.splitlines()[569:581]]
    assert len(states) == 12 and all(("OPEN" in s or "PROVISIONAL" in s) for s in states), states
    t10 = cited(T10)
    assert "revision X is HELD with no admission route (round 5's V-B20 route" in line(t10, 646) and "SUPERSEDED" in line(t10, 647)
    assert "DISPOSITION (10j, after cx46): cx45's Q3 NOT CLOSED" in line(t10, 662)


def t_the_change_list_was_applied_at_7070f106():
    try:
        r = subprocess.run(["git", "-C", ROOT, "show", "--name-only", "--format=%s", APPLIED], capture_output=True)
    except OSError:
        raise Skip("git is needed to read %s" % APPLIED)
    if r.returncode != 0:
        raise Skip("%s is not in this repository's objects" % APPLIED)
    out = r.stdout.decode("utf-8").splitlines()
    assert "the L4-E9 change-list rows R-220 to R-245 applied by records/l9t5/apply_l4e9_changelist_p0.py" in out[0]
    assert sorted(l for l in out[1:] if l.strip()) == sorted(REC + "/l4e9/" + f for f in (
        "DOWNSTREAM-REGISTER.md", "L4-POWER-ARCHITECTURE.md", "l4e9_power_path.py")), out
    assert "| R-220 |" not in at(APPLIED + "^", REG) and "| R-220 |" in at(APPLIED, REG)
    # the draft reads the applied tree and writes nothing
    before = {p: open(os.path.join(ROOT, p), "rb").read() for p in (REG, PAGE, REC + "/l4e9/l4e9_power_path.py")}
    r = subprocess.run([sys.executable, "-B", os.path.join(ROOT, DRAFT), ROOT, "--check"], capture_output=True)
    text = r.stdout.decode("utf-8")
    assert r.returncode == 0 and "APPLIED BEFORE (the tree carries every row this draft adds and the page's P0 note" in text, text[-300:]
    assert all(open(os.path.join(ROOT, p), "rb").read() == b for p, b in before.items()), "the check wrote the tree"


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
