"""W7 (MESHSAT-1357, 6 October 2026): the 45.88 K/W remnants and the P0 list's figures, held as predicates on two patch files.

The files: v2/docs/records/l4e9/L4E9-4588-PATCH.md (rows P-01 to P-12 for L4-E9's page and the generator data that renders or checks
the same texts; records l4e11 and l4e10 classified) and v2/docs/records/l4close/P0-POWER-LIST.rev3.patch.md (rows R-01 to R-09 for
Slot K's draft 2 of the P0 list's revision 3). Neither patch is applied by this branch: the page, the generator and the P0 list are
the coordinator's files. Set 31 applied the L4-E9 rows P-01 to P-12 verbatim (W24, 467c2aaa on fnd/int31l4e9 from a6e3a066); since
W25 (6 October 2026) the first predicate reads them APPLIED at this tree and PENDING at a6e3a066 through git (the history: the rows
were once true); the P0 rows R-01 to R-09 are read on Slot K's draft 2 at its commit, as before. The predicates, each run on the tree
and on the texts the rows replace:

- every L4-E9 row's New text stands once where the row says and its Old text is gone (a line row by its whole lines, a fragment
  outside the New text), so a half-applied or reverted patch is refused; at a6e3a066 every row's Old text is where the row says (a
  whole line, consecutive lines or a fragment of the named line, once in the file) and its New text is not;
- once every row is applied, each page cell equals the generator data that renders or checks it: 8a's D-14 options and 8b's U-04
  constraint read from the patched generator's syntax tree, the exit table's D-14 state and 8f's UDC-1 current rendered from their
  format strings with the figures L4-E11 prints (the same pairing checked on the old texts, which fixes those figures);
- the generator's own checks still hold on the new data: D-14's figures printed by L4-E11, U-04's expected phrases present, and
  P-05's added expectation refuses the old U-04 text; every decimal of the new U-04 text is printed by L4-E9's output body;
- the predicate the rows serve: each page row's New text names 40.78 K/W without m and the 37.59 K/W target and keeps 45.88 K/W only
  at its own m or labelled set 29's and SUPERSEDED; each Old text fails it;
- the set 29 date of 45.88 K/W read from git where those commits are in the object store, and L4-E11's printed rows read;
- every line of records l4e11 and l4e10's hand pages that prints 45.88 is in the classification table, with the words it quotes;
- every Check line of the P0 rows reads what it says at its revision, every fragment row's Old text is once on its draft line, and
  the rows' old quotations and citations fail where the new ones hold.

These are predicates on record text: they establish no electrical or thermal property, close nothing and accept nothing.
"""
import ast
import glob
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

L4E9P = "v2/docs/records/l4e9/L4E9-4588-PATCH.md"
P0P = "v2/docs/records/l4close/P0-POWER-LIST.rev3.patch.md"
PAGE = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
GEN = "v2/docs/records/l4e9/l4e9_power_path.py"
L4O = "v2/docs/records/l4e9/l4e9_power_path.out"
E11O = "v2/docs/records/l4e11/l4e11_power.out"
E11P = "v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md"
D2 = ("35dca639d1f7cbc72e9649b8bb327f65caa686c9", "v2/docs/records/l4close/P0-POWER-LIST.rev3.draft2.md")
SET31_BASE = "a6e3a066a827b8504e8ce804f82c77dac6955c93"   # fnd/int31's tip: P-01 to P-12 pending (the history side)
APPLIED_AT = "467c2aaa"   # fnd/int31l4e9: W24 applied P-01 to P-12 verbatim (set 31)
DASHES = (chr(0x2013), chr(0x2014))
NEW_EXPECT = "(Zself + 2 Zmut) at most 40.78 K/W without m"
OLD_EXPECT = ("(Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart", "(Zself + Zmut) at most 20.39 K/W the fallback")
_C = {}


def _read(rel):
    if rel not in _C:
        _C[rel] = open(need(os.path.join(ROOT, rel), "a file this module reads"), encoding="utf-8").read()
    return _C[rel]


def _norm(s):
    return " ".join(s.replace("**", "").split())


def _git_show(commit, rel):
    """The file at a commit, or None when this host has no git or not that commit (a code-only checkout, a box clone)."""
    try:
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, rel)], capture_output=True)
    except OSError:
        return None
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def _rows(rel):
    """The patch file's rows: id -> {field: value, 'old': text, 'new': text, 'checks': [...]}."""
    text = _read(rel)
    out = {}
    for blk in re.split(r"\n### ", text)[1:]:
        rid = blk.split(".", 1)[0].strip()
        r = {"checks": []}
        for ln in blk.split("\n"):
            m = re.match(r"- (File|Line|Kind|Pairs with|Renders with): (.*)$", ln)
            if m:
                r[m.group(1)] = m.group(2).strip().strip("`")
            m = re.match(r"- Check: `([0-9a-f]{8}):([^`:]+):(\d+)(?:-(\d+))?` reads \"(.*)\"$", ln)
            if m:
                a = int(m.group(3))
                r["checks"].append((m.group(1), m.group(2), a, int(m.group(4) or a), m.group(5)))
        fences = re.findall(r"```text\n(.*?)\n```", blk, re.S)
        assert len(fences) == 2, "%s: an Old and a New block" % rid
        r["old"], r["new"] = fences
        assert r["old"] != r["new"], "%s: the New text differs" % rid
        out[rid] = r
    return out


def _find(lines, block):
    """The indexes where `block` (a list of whole lines) stands in `lines`."""
    k = len(block)
    return [i for i in range(len(lines) - k + 1) if lines[i:i + k] == block]


def _state(rows, reader=None):
    """'pending' when every L4-E9 row's Old text is where it says, 'applied' when every New text stands once; else refused. `reader`
    gives a file's text (the tree's by default; a commit's for the history side)."""
    seen = set()
    for rid, r in rows.items():
        text = (reader or _read)(r["File"])
        lines = text.split("\n")
        n = int(r["Line"])
        if r["Kind"] in ("line", "lines"):
            old_here = _find(lines, r["old"].split("\n")) == [n - 1]
            new_here = len(_find(lines, r["new"].split("\n"))) == 1
        else:
            old_here = r["old"] in lines[n - 1] and text.count(r["old"]) == 1
            new_here = text.count(r["new"]) == 1
        assert old_here != new_here, "%s: neither its Old nor its New text stands alone where the row says" % rid
        seen.add("pending" if old_here else "applied")
    assert len(seen) == 1, "half applied: %s" % sorted(seen)
    return seen.pop()


def _old_left(rows, reader=None):
    """The rows whose Old text still stands in their file outside their New text: a line row by its whole lines, a fragment by its text
    (W25: the applied side of the first predicate; a New text that contains its Old is read with the New text taken out)."""
    left = []
    for rid, r in sorted(rows.items()):
        text = (reader or _read)(r["File"])
        if r["Kind"] in ("line", "lines"):
            lines, nb = text.split("\n"), r["new"].split("\n")
            at = _find(lines, nb)
            rest = lines[:at[0]] + ["\0"] + lines[at[0] + len(nb):] if len(at) == 1 else lines
            if _find(rest, r["old"].split("\n")):
                left.append(rid)
        elif text.replace(r["new"], "\0").count(r["old"]):
            left.append(rid)
    return left


def _apply(rows, rel, text, which_from, which_to):
    """The file with every row of `rel` turned from one side to the other: whole lines for line rows, fragments otherwise."""
    for rid, r in ((k, v) for k, v in sorted(rows.items()) if v["File"] == rel):
        a, b = r[which_from], r[which_to]
        if r["Kind"] in ("line", "lines"):
            lines = text.split("\n")
            at = _find(lines, a.split("\n"))
            assert len(at) == 1, "%s: its %s lines once" % (rid, which_from)
            i = at[0]
            text = "\n".join(lines[:i] + b.split("\n") + lines[i + len(a.split("\n")):])
        else:
            assert text.count(a) == 1, "%s: its %s text once" % (rid, which_from)
            text = text.replace(a, b)
    return text


def _md_table(text, head):
    lines = text.split("\n")
    i = [k for k, ln in enumerate(lines) if ln.startswith(head)]
    assert len(i) == 1, "one table headed %r" % head
    out = []
    for ln in lines[i[0] + 2:]:
        if not ln.startswith("|"):
            break
        out.append([c.strip() for c in ln.strip().strip("|").split("|")])
    return out


def _fmt(x):
    """The generator's fmt (l4e9_power_path.py, def fmt)."""
    return ("%.4f" % x).rstrip("0").rstrip(".") if isinstance(x, float) else str(x)


def _values():
    """The figures the generator reads from L4-E11's output (its own patterns, lines 2056 to 2061), plus four figures of 16a to 16d
    that the old-text pairing below fixes (a wrong one makes the old page cell differ from its rendering)."""
    t = _read(E11O)
    r9c = t.split("\n19. ROUND 9: ")[1].split("\n   19c. ")[1].split("\n   19d. ")[0]
    m = re.search(r"each FET's \(Zself \+ 2 Zmut\) at most ([\d.]+) K/W steady with R17 placed apart", " ".join(r9c.split()))
    row = re.search(r"^\s*E11-29 \| LAYOUT \|[^\n]*", t, re.M).group(0)
    z3m = re.search(r"so each \(Zself \+ 2 Zmut\) at most ([\d.]+) K/W without m", row)
    zw = re.search(r"each junction's worst-split figure Zw at most ([\d.]+) K/W \(Zself [\d.]+ K/W for three side by side at m [\d.]+\)", row)
    held = re.search(r"the hottest junction stays at most 150 C held at ([\d.]+) A from ([\d.]+) C with the band and R17 in place",
                     " ".join(r9c.split()))
    assert m and z3m and zw and held, "L4-E11's figures as the generator reads them"
    return {"z3": float(m.group(1)), "z3m": float(z3m.group(1)), "zw": float(zw.group(1)), "z2_fb": 20.39,
            "held_lim": (float(held.group(1)), float(held.group(2))), "allow": 21.136, "at_allow": (None, 118.0, None),
            "dock_tj": (None, 123.3), "ciss3": (7.08, 8.61)}


def _arg(node, V):
    """One argument of a % tuple: fmt(F["f02"]["k"][i]), fmt(g["k"]), F["f02"]["k"][i] (kept raw)."""
    wrapped = isinstance(node, ast.Call) and getattr(node.func, "id", "") == "fmt"
    if wrapped:
        node = node.args[0]
    idx = []
    while isinstance(node, ast.Subscript):
        idx.append(node.slice.value)
        node = node.value
    idx = [i for i in reversed(idx) if i != "f02"]
    v = V[idx[0]]
    for i in idx[1:]:
        v = v[i]
    return _fmt(v) if wrapped else v


def _render(node, V):
    assert isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod) and isinstance(node.left, ast.Constant), "a % b"
    return node.left.value % tuple(_arg(a, V) for a in node.right.elts)


def _gen_cells(src, V):
    """D-14's options, U-04's constraint, the exit row D-14's state and UDC-1's current, from the generator's syntax tree."""
    tree = ast.parse(src)
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Dict):
            d = {k.value: v for k, v in zip(n.keys, n.values) if isinstance(k, ast.Constant)}
            idv = d.get("id")
            if isinstance(idv, ast.Constant) and idv.value == "D-14" and "options" in d:
                out["d14"] = d["options"].value
            if isinstance(idv, ast.Constant) and idv.value == "U-04" and "constraint" in d and isinstance(d["constraint"], ast.Constant):
                out["u04"] = d["constraint"].value
            if isinstance(idv, ast.Constant) and idv.value == "UDC-1" and "current" in d:
                out["udc1"] = _render(d["current"], V)
        if isinstance(n, ast.Tuple) and len(n.elts) > 2 and isinstance(n.elts[0], ast.Constant) and n.elts[0].value == "D-14" \
                and isinstance(n.elts[1], ast.Constant) and n.elts[1].value.startswith("(B1)'s battery FET bounded at an unprinted"):
            out["exit"] = _render(n.elts[2], V)
    assert set(out) == {"d14", "u04", "udc1", "exit"}, sorted(out)
    return out


def _page_cells(page):
    return {"d14": [r for r in _md_table(page, "| Defect | What |") if r[0] == "D-14"][0][3],
            "u04": [r for r in _md_table(page, "| Choice | Class |") if r[0] == "U-04"][0][4],
            "exit": [r for r in _md_table(page, "| Defect | Its fault |") if r[0] == "D-14"][0][2],
            "udc1": [r for r in _md_table(page, "| Choice | The current choice") if r[0].startswith("UDC-1")][0][1]}


def _both():
    rows = _rows(L4E9P)
    st = _state(rows)
    other = {"pending": "new", "applied": "old"}[st]
    here = {"pending": "old", "applied": "new"}[st]
    texts = {}
    for rel in (PAGE, GEN):
        cur = _read(rel)
        texts[(rel, here)] = cur
        texts[(rel, other)] = _apply(rows, rel, cur, here, other)
    return rows, texts


def _labelled(text):
    """Every 45.88 K/W is the worst-split figure at its own m, or set 29's (the label before it or just after) and SUPERSEDED."""
    for m in re.finditer(r"45\.88 K/W", text):
        before, after = text[max(0, m.start() - 200):m.start()], text[m.end():m.end() + 260]
        own_m = before.rstrip().endswith("at its own m at most")
        s29 = ("set 29's" in before[-170:] or "set 29's" in after[:120]) and "SUPERSEDED" in after
        if not (own_m or s29):
            return False
    return True


def t_the_l4e9_rows_stand_where_they_say():
    """W25's restatement (6 October 2026) of "pending or applied, never half": APPLIED at this tree (W24, 467c2aaa) with every Old text
    gone, PENDING at fnd/int31's a6e3a066 (read through git), and a row reverted at this tree is refused as half applied."""
    rows = _rows(L4E9P)
    assert sorted(rows) == ["P-%02d" % i for i in range(1, 13)], sorted(rows)
    assert {r["File"] for r in rows.values()} == {PAGE, GEN}
    assert _state(rows) == "applied", "P-01 to P-12 are not applied at this tree (W24, %s)" % APPLIED_AT
    assert not _old_left(rows), "an applied row's Old text still stands: %s" % _old_left(rows)
    base = {rel: _git_show(SET31_BASE, rel) for rel in (PAGE, GEN)}
    if None in base.values():
        raise Skip("fnd/int31's %s is not in this object store (the history side)" % SET31_BASE[:8])
    assert _state(rows, base.get) == "pending", "the rows did not stand pending at %s" % SET31_BASE[:8]
    assert _old_left(rows, base.get) == sorted(rows), "an Old text was missing at %s" % SET31_BASE[:8]
    for rid in ("P-01", "P-12"):   # a fragment row and a line row reverted in memory: half applied, refused
        rel = rows[rid]["File"]
        texts = {PAGE: _read(PAGE), GEN: _read(GEN)}
        texts[rel] = _apply({rid: rows[rid]}, rel, texts[rel], "new", "old")
        try:
            _state(rows, texts.get)
            refused = False
        except AssertionError:
            refused = True
        assert refused and _old_left(rows, texts.get) == [rid], "%s reverted is not refused" % rid


def t_each_page_cell_equals_its_generator_data_on_both_sides():
    rows, texts = _both()
    V = _values()
    assert (V["z3"], V["z3m"], V["zw"]) == (45.88, 40.78, 37.59), "the figures L4-E11 prints"
    for side in ("old", "new"):
        g = _gen_cells(texts[(GEN, side)], V)
        p = _page_cells(texts[(PAGE, side)])
        for k in ("d14", "u04", "exit", "udc1"):
            assert _norm(p[k]) == _norm(g[k]), "%s side, %s: the page cell is not the generator's" % (side, k)
    # a mutation: the page's new D-14 row against the old generator data refuses
    assert _norm(_page_cells(texts[(PAGE, "new")])["d14"]) != _norm(_gen_cells(texts[(GEN, "old")], V)["d14"])


def t_the_generators_own_checks_hold_on_the_new_data():
    rows, texts = _both()
    V = _values()
    new, old = _gen_cells(texts[(GEN, "new")], V), _gen_cells(texts[(GEN, "old")], V)
    t, md = _read(E11O), _read(E11P)
    src = " ".join(t.split("\n15. THE FIX ROUND FOR THE CONSOLIDATION REVIEW")[1].split("\nEND.")[0].split()) + " " + \
        " ".join(md.split("## 16. The fix round for the review of the provisional fixes")[1].split())

    def printed(text):
        return all(re.search(r"(?<![\d.])%s(?![\d])" % re.escape(x), src) for x in re.findall(r"(?<![\d.])\d+\.\d+(?![\d])", text))
    assert printed(new["d14"]), "D-14's figures are printed by L4-E11 (the generator's lines 2041 to 2045)"
    assert not printed(new["d14"].replace("37.59", "37.58")), "a figure L4-E11 does not print is refused"
    for s in OLD_EXPECT:
        assert s in _norm(new["u04"]), "fx_u04_expect still finds %r" % s
    assert NEW_EXPECT in _norm(new["u04"]) and NEW_EXPECT not in _norm(old["u04"]), "P-05's expectation refuses the old U-04 text"
    assert NEW_EXPECT.replace("40.78", "%s") in rows["P-05"]["new"] and '["z3m"]' in rows["P-05"]["new"], "P-05 reads E11-29's bar"
    out = _read(L4O)
    body = out.split("9. THE CLOSURE GATE")[0] + out.split("11. PART A")[1]
    for fig in re.findall(r"\d+\.\d+", new["u04"]):
        assert fig in body, "U-04's figure %s is printed outside the gate (test_l4e9's own rule)" % fig


def t_the_new_texts_name_the_current_row_and_label_the_old_bar():
    rows = _rows(L4E9P)
    page_rows = [k for k, r in rows.items() if r["File"] == PAGE]
    assert sorted(page_rows) == ["P-01", "P-03", "P-06", "P-09", "P-12"]
    for k in page_rows:
        old, new = _norm(rows[k]["old"]), _norm(rows[k]["new"])
        assert "40.78 K/W without m" in new and "37.59 K/W" in new and "SUPERSEDED" in new and "4 October 2026" in new, k
        assert _labelled(new), "%s: an unlabelled 45.88 K/W" % k
        assert "E-1" not in new.replace(rows[k]["old"], ""), "%s: no bare E-1 added (K-08: one identifier, two items)" % k
        assert not ("40.78 K/W without m" in old and _labelled(old)), "%s: the old text already met the predicate" % k
    for k in ("P-02", "P-04", "P-07", "P-10"):
        assert "45.88" in rows[k]["new"] or "%s K/W (set 29's %s K/W" in rows[k]["new"], k


def t_the_set_29_date_and_l4e11s_rows():
    t, md = _read(E11O), _read(E11P)
    tl = t.split("\n")
    assert "each FET's (Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart" in tl[1173], "out 19c"
    assert "(Zself + 2 Zmut) at most 40.78 K/W" in tl[1521], "out 21d"
    assert "at most 45.88 K/W, so each (Zself + 2 Zmut) at most 40.78 K/W without m" in tl[567] and "Zw at most 37.59 K/W" in tl[567]
    assert md.split("\n")[1816] == "## 19. Round 9: record l9stk's protection and record l8p's breaker (4 October 2026; out 19)"
    seen = 0
    for sha, has in (("aa76c89448ec943e3a37357ebc11ce3322fa4020", True), ("d834e6a7be211d1cdd1b18ded54bec1c427048fd", False),
                     ("94971c8ce81a0276a22c4ff3c7594dc3deb46736", False)):
        p = _git_show(sha, PAGE)
        if p is None:
            continue
        seen += 1
        assert ("45.88" in p) == has, "%s: set 29's page prints 45.88 K/W, sets 27 and 28's do not" % sha[:8]
    if not seen:
        raise Skip("sets 27 to 29 are not in this object store")


def t_records_l4e11_and_l4e10_print_45_88_only_where_classified():
    text = _read(L4E9P)
    tab = text.split("## 4. Records l4e11 and l4e10")[1].split("\n## 5.")[0]
    listed = {}
    for m in re.finditer(r"^\| `(v2/docs/records/l4e1[01]/[^`]+)` \| (\d+) \| [^|]+ \| [^|]+ \| \"(.*)\" \|$", tab, re.M):
        listed[(m.group(1), int(m.group(2)))] = m.group(3)
    found = set()
    for d in ("l4e11", "l4e10"):
        for p in glob.glob(os.path.join(ROOT, "v2", "docs", "records", d, "**", "*.md"), recursive=True):
            rel = os.path.relpath(p, ROOT)
            for i, ln in enumerate(open(p, encoding="utf-8").read().split("\n"), 1):
                if "45.88" in ln:
                    found.add((rel, i))
                    assert (rel, i) in listed, "%s:%d prints 45.88 and is not classified" % (rel, i)
                    assert listed[(rel, i)] in ln, "%s:%d does not read %r" % (rel, i, listed[(rel, i)])
    assert found == set(listed), sorted(set(listed) - found)
    assert not [k for k in found if "/l4e10/" in k[0]], "record l4e10 prints no 45.88 K/W"


def t_the_p0_rows_hold_and_their_old_texts_fail():
    rows = _rows(P0P)
    assert sorted(rows) == ["R-%02d" % i for i in range(1, 10)], sorted(rows)
    d2 = _git_show(*D2)
    if d2 is None:
        raise Skip("Slot K's draft 2 (fnd/recpack 35dca639) is not in this object store")
    d2l = d2.split("\n")
    skipped = 0
    for rid, r in rows.items():
        assert r["checks"], rid
        for sha, rel, a, b, words in r["checks"]:
            f = _git_show(sha, rel)
            if f is None:
                skipped += 1
                continue
            assert _norm(words) in _norm(" ".join(f.split("\n")[a - 1:b])), "%s: %s:%s:%d does not read %r" % (rid, sha, rel, a, words)
        if r["Kind"] == "fragment":
            assert r["old"] in d2l[int(r["Line"]) - 1] and d2.count(r["old"]) == 1, "%s: once, on draft 2's line %s" % (rid, r["Line"])
        elif r["Kind"] == "every":
            assert d2.count(r["old"]) == 16 and d2.count(r["new"]) == 0, rid
            assert d2.replace(r["old"], r["new"]).count(r["new"]) == 16
    # the old texts fail where the new hold
    con = _git_show("bbba3e53", "v2/docs/records/l9t5/l9t5_connected.out").split("\n")[361]
    assert rows["R-04"]["new"].lstrip('"') in con and rows["R-04"]["old"].lstrip('"') not in con, "R-04"
    cx = _git_show("bbba3e53", "v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md").split("\n")
    assert "the second negative on the method, which ends it" in cx[2] and "the second negative" not in cx[205], "R-03"
    for rid, sha, rel, n in (("R-05", "6fe398e9", L4O, 1310), ("R-06", "6fe398e9", L4O, 615),
                             ("R-07", "6fe398e9", "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md", 336)):
        ln = _git_show(sha, rel).split("\n")[n - 1]
        q_old = re.findall(r'"([^"]+)"', rows[rid]["old"])[0]
        q_new = re.findall(r'"([^"]+)"', rows[rid]["new"])[1]
        assert q_new in ln and q_old not in ln, "%s: the merge changed the quoted words" % rid
    anx = _git_show("686de0a264e71e364d33e6292a85a653aefc265f", "v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md")
    if anx is not None:
        line = anx.split("\n")[104]
        assert "the pours 0.1 mOhm." not in line and "the pours 0.1 mOhm" in line, "R-08: the old quotation fails on W3's annex"
    else:
        skipped += 1
    assert skipped <= 3, "too many checks skipped (%d)" % skipped


QPROSE = re.compile(r"\"([^\"]{8,400}?)\"[^\"`]{0,80}?\(?`(?:([0-9a-f]{8}):)?(v2/[^`:\s]+):(\d+)(?:-(\d+))?`")


def t_every_prose_quotation_reads_on_its_cited_lines():
    """Each quotation of the two patch files' prose followed by a line citation is found on the cited lines (at the tree, or at the
    commit the citation names, where that commit is in the object store); the rows' fenced texts are held by the tests above."""
    checked = skipped = 0
    for rel in (L4E9P, P0P):
        prose = re.sub(r"```text\n.*?\n```", "", _read(rel), flags=re.S)
        prose = "\n".join(ln for ln in prose.split("\n") if not ln.startswith("- Check:"))
        flat = " ".join(prose.split())
        for m in QPROSE.finditer(flat):
            sha, path, a = m.group(2), m.group(3), int(m.group(4))
            b = int(m.group(5) or a)
            f = _git_show(sha, path) if sha else open(os.path.join(ROOT, path), encoding="utf-8").read()
            if f is None:
                skipped += 1
                continue
            seg = _norm(" ".join(f.split("\n")[a - 1:b]))
            for part in _norm(m.group(1)).split("..."):
                assert part.strip() in seg, "%s: %r is not on %s:%d-%d" % (rel, part.strip()[:60], path, a, b)
            checked += 1
    assert checked >= 8, "the quotations were read (%d, %d skipped)" % (checked, skipped)


def t_no_dashes_and_the_prototype_framing():
    for rel in (L4E9P, P0P, os.path.relpath(os.path.abspath(__file__), ROOT)):
        t = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        assert not any(ch in t for ch in DASHES), rel
    for rel in (L4E9P, P0P):
        assert "Prototype framing" in _norm(_read(rel)) and _read(rel).startswith("**DONE:**"), rel
