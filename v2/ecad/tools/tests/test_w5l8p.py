"""Set 30 note of record l8p (MESHSAT-1357, 6 October 2026, worker W5 on fnd/w5l8p from set 30's integration commit 2c
53a68c7c; adopted in the NEXT set): the release statement and U101's part number copies, record text only.

The findings answered: Slot H's not-reconciled item on record l8p's one release (SET31-CHANGES.md at 17ce29d5, "five drafts"
against the register's six rows), Slot G's PC-04, PC-13 and C-5 (8282895e), Slot L's K-14 and K-19 (249e9e47).

The predicates, each parsed (ast for the drafts, the table cells for the page and the register), never grepped from prose:
- every apply script of record l8p that reads RELEASE.md beside itself (HERE from __file__, RELEASE = os.path.join(HERE,
  "RELEASE.md"), a released() function) is named in L8P-BREAKER.md section 6 item 1, and nothing else is; the item's count word
  equals that number; each named draft's register row is the row of DOWNSTREAM-REGISTER.md whose Item names the script and whose
  From names record l8p; the released() functions are one function, so one file releases all of them or none;
- U101 is the latch-off LM5069MM-1 wherever record l8p draws, checks or tables it, and no file of the record outside its verbatim
  input copies names the automatic-retry part number;
- the changed pages carry a dated set 30 note with the promoted sha (W5's placeholder, filled in set 31) and the NEXT set, and section 14 accounts for all
  28 of Slot L's K items.
Each predicate is also run on the old state or on a mutation and must refuse it. No generator, no suite, no KiCad; the tree is
only read."""
import ast
import os
import re

from harness import need

TESTS = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(TESTS)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l8p")
PAGE = os.path.join(REC, "L8P-BREAKER.md")
README = os.path.join(REC, "README.md")
REGISTER = os.path.join(ROOT, "v2", "docs", "records", "l4e9", "DOWNSTREAM-REGISTER.md")

CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)
WORDS = {"three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8}
RETRY_PART = ("LM5069MM-" + "2", "LM5069-" + "2")   # spelled apart so this file does not carry the strings it looks for

# Section 6 item 1 as it stood at 53a68c7c (rounds 8 and 9), the state the findings name: it must fail the predicate.
OLD_ITEM1 = ("1. **One release for the five drafts.** P (the breaker, then the ideal diode), E and A (the PTC draft, then, after "
             "L4-E11's DD-7,\n   the guard draft) are released and applied together, never one alone. The netlist check reads FAIL on "
             "a board P that carries the breaker without the ideal diode (DD-5 uncorrected).\n")


def _read(p):
    return open(p, encoding="utf-8").read()


def _drafts():
    """Every apply_*.py of record l8p, name -> source."""
    return {f: _read(os.path.join(REC, f)) for f in sorted(os.listdir(REC)) if f.startswith("apply_") and f.endswith(".py")}


_HERE = ast.dump(ast.parse("os.path.dirname(os.path.abspath(__file__))", mode="eval").body)
_REL = ast.dump(ast.parse('os.path.join(HERE, "RELEASE.md")', mode="eval").body)


def _release_fn(src):
    """The module's released() function as an ast dump if the module reads RELEASE.md beside itself, else None."""
    tree = ast.parse(src)
    here = rel = fn = None
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if n.targets[0].id == "HERE":
                here = ast.dump(n.value)
            elif n.targets[0].id == "RELEASE":
                rel = ast.dump(n.value)
        elif isinstance(n, ast.FunctionDef) and n.name == "released":
            fn = ast.dump(n)
    return fn if (here == _HERE and rel == _REL and fn) else None


def release_group(drafts):
    return {name for name, src in drafts.items() if _release_fn(src)}


def _item1(page):
    sec = page.split("\n## 6. Order constraints")[1].split("\n## 7. ")[0]
    return sec.split("\n2. **Board P")[0]


def page_release_item(page):
    """(count word, {draft: (board, register row)}, the item's text) from section 6 item 1."""
    item = _item1(page)
    m = re.search(r"\*\*One release for the (\w+) drafts", item)
    rows = {}
    for l in item.split("\n"):
        r = re.match(r"^\s*\| `(apply_[a-z0-9_]+\.py)` \| ([A-Z]) \| (R-\d+) \|\s*$", l)
        if r:
            assert r.group(1) not in rows, "a draft named twice: %s" % r.group(1)
            rows[r.group(1)] = (r.group(2), r.group(3))
    return (m.group(1) if m else None), rows, item


def register_rows(reg):
    """script -> register row id, over the rows whose From names record l8p (the Item cell names the script in backticks)."""
    out = {}
    for l in reg.split("\n"):
        if not l.startswith("| R-"):
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if "l8p" not in c[3]:
            continue
        for s in re.findall(r"`(apply_[a-z0-9_]+\.py)`", c[2]):
            assert s not in out, "two register rows apply %s" % s
            out[s] = c[0]
    return out


def release_problems(page, drafts, reg):
    group = release_group(drafts)
    word, rows, item = page_release_item(page)
    regmap = register_rows(reg)
    p = []
    if WORDS.get(word) != len(group):
        p.append("the item counts %r drafts, %d read RELEASE.md" % (word, len(group)))
    if set(rows) != group:
        p.append("named %s, reading RELEASE.md %s" % (sorted(rows), sorted(group)))
    for name, (board, row) in rows.items():
        if regmap.get(name) != row:
            p.append("%s is %s on the page, %s in the register" % (name, row, regmap.get(name)))
        if board != name[len("apply_gen_sch_")].upper():
            p.append("%s on board %s" % (name, board))
    for name in drafts:
        if name not in group and name not in item:
            p.append("%s reads no RELEASE.md and the item does not say so" % name)
    fns = {_release_fn(drafts[n]) for n in group}
    if len(fns) != 1:
        p.append("the drafts carry %d different released() functions" % len(fns))
    return p


def t_one_release_md_covers_exactly_the_drafts_the_page_names():
    page = _read(need(PAGE, "the l8p record page"))
    reg = _read(need(REGISTER, "L4-E9's downstream register"))
    drafts = _drafts()
    assert release_problems(page, drafts, reg) == [], release_problems(page, drafts, reg)
    word, rows, item = page_release_item(page)
    assert word == "six" and len(rows) == 6, (word, rows)
    assert "apply_test_l4e11_ptc_pin.py" not in release_group(drafts) and "**Not covered by this `RELEASE.md`:**" in item
    flat = re.sub(r"\s+", " ", item)
    for old in ('"One release for the three drafts" from round 1', '"One release for the four drafts" from round 4',
                '"One release for the five drafts" from round 8'):
        assert old in flat, "the item's history is not kept, dated: %s" % old


def t_the_old_item_and_mutations_fail_the_release_predicate():
    page = _read(need(PAGE, "the l8p record page"))
    reg = _read(need(REGISTER, "L4-E9's downstream register"))
    drafts = _drafts()
    item = _item1(page)
    new1 = item.split("\n1. ", 1)[1].split("   - `check_contracts.py` section 15c")[0]
    old_page = page.replace("1. " + new1, OLD_ITEM1)
    assert old_page != page and release_problems(old_page, drafts, reg), "the old item passes"
    thgfs = "   | `apply_gen_sch_a_thgfs.py` | A | R-244 |\n"
    muts = {"a row dropped": page.replace(thgfs, ""),
            "the test pin draft named": page.replace(thgfs, thgfs + "   | `apply_test_l4e11_ptc_pin.py` | A | R-208 |\n"),
            "two rows swapped": page.replace("| P | R-206 |", "| P | R-2XX |").replace("| P | R-246 |", "| P | R-206 |").replace("| P | R-2XX |", "| P | R-246 |"),
            "the count word": page.replace("**One release for the six drafts", "**One release for the five drafts")}
    for what, m in muts.items():
        assert m != page and release_problems(m, drafts, reg), "a mutation passes: %s" % what
    d2 = dict(drafts)
    d2["apply_gen_sch_a_thgfs.py"] = d2["apply_gen_sch_a_thgfs.py"].replace('os.path.join(HERE, "RELEASE.md")', 'os.path.join(HERE, "RELEASE-X.md")')
    assert release_problems(page, d2, reg), "a draft reading another release file passes"
    d3 = dict(drafts)
    d3["apply_gen_sch_e_enable.py"] = d3["apply_gen_sch_e_enable.py"].replace('lines[0] != "released: yes"', 'lines[0] != "released: YES"')
    assert d3 != drafts and release_problems(page, d3, reg), "a draft with its own released() passes"


def u101_problems(files):
    """files: path relative to the record -> text. U101 the -1 wherever the record draws, checks or tables it."""
    p = []
    for rel, t in files.items():
        if rel.startswith("inputs/"):
            continue
        for s in RETRY_PART:
            if s in t:
                p.append("%s names %s" % (rel, s))
    brk = ast.parse(files["apply_gen_sch_p_breaker.py"])
    calls = [n.value for n in ast.walk(brk) if isinstance(n, ast.Constant) and isinstance(n.value, str) and 'ic("U101"' in n.value]
    if not calls or not all(re.search(r'ic\("U101", 10, "LM5069MM-1 ', c) for c in calls):
        p.append("the breaker draft's U101 call is not the -1")
    chk = ast.parse(files["check_l8p_netlist.py"])
    rows = [n for n in ast.walk(chk) if isinstance(n, ast.Tuple) and len(n.elts) > 2
            and all(isinstance(e, ast.Constant) for e in n.elts[:3]) and n.elts[1].value == "U101"]
    if not rows or any(r.elts[2].value != "LM5069MM-1" for r in rows):
        p.append("check_l8p_netlist.py does not expect the -1 for U101")
    dio = ast.parse(files["apply_gen_sch_p_idealdiode.py"])
    req = [n for n in dio.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "REQUIRES"]
    if not req or not any('ic("U101", 10, "LM5069MM-1 circuit breaker' in e for e in ast.literal_eval(req[0].value)):
        p.append("the ideal diode draft does not require the -1's call")
    tab = [l for l in files["L8P-BREAKER.md"].split("\n") if l.startswith("| U101 | ")]
    if len(tab) != 1 or not tab[0].startswith("| U101 | LM5069MM-1, the latch-off variant"):
        p.append("the value table's U101 row is not the -1")
    return p


def _record_files():
    out = {}
    for d, _, fs in os.walk(REC):
        for f in fs:
            if f.endswith((".md", ".py", ".out", ".txt")):
                q = os.path.join(d, f)
                out[os.path.relpath(q, REC).replace(os.sep, "/")] = _read(q)
    return out


def t_u101_is_the_latch_off_minus_1_in_every_file_of_the_record():
    need(PAGE, "the l8p record page")
    files = _record_files()
    assert u101_problems(files) == [], u101_problems(files)
    sec = _read(PAGE).split("\n## 14. Set 30 note")[1]
    for s in ('"The protection candidate now selects latch-off LM5069-1."', "OWNER-INSTRUCTION-2026-10-04.md` line 140",
              "l8p-apply_gen_sch_p_breaker-515f6cf2.txt", "l8p-apply_gen_sch_a_ptc-515f6cf2.txt", "l8p-apply_gen_sch_e_enable-515f6cf2.txt"):
        assert s in sec, "section 14 does not cite %s" % s
    own = os.path.join(ROOT, "v2", "docs", "handover", "OWNER-INSTRUCTION-2026-10-04.md")
    if os.path.exists(own):
        assert _read(own).split("\n")[139] == "- The protection candidate now selects latch-off LM5069-1. B-R2, DD-3, DD-5 and E11-37 have remaining work. Confirm their latest state before assigning anything."


def t_a_minus_2_anywhere_in_the_record_fails_the_u101_predicate():
    need(PAGE, "the l8p record page")
    files = _record_files()
    muts = []
    m = dict(files); m["apply_gen_sch_p_breaker.py"] = m["apply_gen_sch_p_breaker.py"].replace('ic("U101", 10, "LM5069MM-1 ', 'ic("U101", 10, "LM5069MM-' + '2 ')
    muts.append(m)
    m = dict(files); m["check_l8p_netlist.py"] = m["check_l8p_netlist.py"].replace('("p", "U101", "LM5069MM-1"', '("p", "U101", "LM5069MM-' + '2"')
    muts.append(m)
    m = dict(files); m["L8P-BREAKER.md"] = m["L8P-BREAKER.md"].replace("| U101 | LM5069MM-1, the latch-off variant", "| U101 | " + RETRY_PART[0])
    muts.append(m)
    m = dict(files); m["README.md"] = m["README.md"] + "\nU101 " + RETRY_PART[1] + "\n"
    muts.append(m)
    for i, mm in enumerate(muts):
        assert mm != files and u101_problems(mm), "mutation %d passes" % i
    m = dict(files); m["inputs/x.md"] = RETRY_PART[0]
    assert u101_problems(m) == [], "a verbatim input copy is not the record's statement"


def _expand(spec):
    out = set()
    for a, b in re.findall(r"K-(\d\d)(?: to K-(\d\d))?", spec):
        out |= set(range(int(a), int(b or a) + 1))
    return out


def t_the_changed_pages_carry_the_dated_set30_note():
    page = _read(need(PAGE, "the l8p record page"))
    readme = _read(need(README, "the l8p README"))
    sec = page.split("\n## 14. Set 30 note (6 October 2026)")[1]
    flat = re.sub(r"\s+", " ", sec)
    # W5 wrote the placeholder `__INTEGRATED__` in both notes. Restated by W41 (6 October 2026; basis: W10's plan R0,
    # `_runs/int31/PLAN.draft.md` lines 206 to 212, and W38's finding F2): filled with set 30's promoted sha, dd1aed00
    # (`_runs/int30/ADOPTION-VALUES.md`), short as both notes name their other commits; the placeholder is gone from both files.
    assert "__INTEGRATED__" not in page and "__INTEGRATED__" not in readme, "a placeholder is not filled"
    for s in ("promoted candidate `dd1aed00`", "**Adopted in the NEXT set", "`53a68c7c`", "**SESSION decision W5-D1**", "To reverse:",
              "**W5-F1", "**W5-F2", "**W5-F3", "SET31-CHANGES.md` lines 107 to 108", "lines 151 to 158, 236 to 242 and 296",
              "lines 324 and 329"):
        assert s in flat, s
    first = readme.split("\n\n")[0]
    assert first.startswith("**Set 30 note (6 October 2026") and "promoted candidate `dd1aed00`" in first and "NEXT set" in first
    assert all(w in first for w in ("DONE", "NOT DONE", "NEXT")), first
    k = flat.split("**Slot L's K items")[1]
    named = _expand(k.split("The other twenty-six (")[1].split(")")[0])
    assert "K-14 is this record's" in k and "K-19 names this folder's breaker draft" in k
    assert named | {14, 19} == set(range(1, 29)) and not named & {14, 19} and len(named) == 26, sorted(named)
    for p in (PAGE, README, os.path.abspath(__file__)):
        t = _read(p)
        assert "\u2014" not in t and "\u2013" not in t, "an em or en dash in %s" % os.path.basename(p)
    assert not CLAIM.search(sec), CLAIM.search(sec).group(0)
