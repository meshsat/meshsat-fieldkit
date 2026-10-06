"""W13 (MESHSAT-1357, 6 October 2026): W5's findings on L4-E9's side, held as predicates on one patch file.

The file: v2/docs/records/l4e9/L4E9-W5-PATCH.md (rows WP-01 to WP-27 for the coordinator). Nothing in it is applied by this branch:
L4-E9's page, register, generator, output and inputs are the integration's files, the drafts are records l8p's and l4e11's. Set 31
applied WP-01 to WP-22 with the re-take of section 2 (W24, bad162ad on fnd/int31l4e9 from a6e3a066); WP-23 to WP-27 wait (the
coordinator's decision: only with the next circuit change to those drafts). Since W25 (6 October 2026) the first predicate reads the
applied state at this tree and the pending state at a6e3a066 through git (the history: the rows were once true). The predicates,
each run on the tree and on the texts the rows replace:

- every row's Old text is where the row says (a whole line, consecutive lines or a fragment once in the file), or its New text is;
  the re-take rows (WP-01 to WP-06) and the list rows (WP-07 to WP-22) each stand all pending or all applied, never half: APPLIED at
  this tree with every Old text gone, the copies the new pins name standing with their digests and round 1's copies removed, and
  all pending at a6e3a066; the docstring rows WP-23 to WP-27 stand pending at both;
- the three copies: their sha256, round 1's bytes at 515f6cf2, W5's files and their sha256, the LM5069 lines and the quoted unified
  diffs recomputed; the re-taken bytes still meet the generator's two checks on a copy (read from its syntax tree), which a copy
  without its draft marker fails; the new pins name the drafts' current bytes and the commit that last changed them;
- each generator row of the change list equals its page cell before and after the rows (test_l4e9's rule), the six companions are
  W5's section 6 item 1 table and the register's own R-206 to R-208, every new text names the other five in the register's order,
  every old text fewer; "l8p section 5" is gone from L4-E9's three files once the rows stand, and the two commits print what R-208's
  new text says they print;
- the docstring rows change one module docstring and nothing a draft executes, and name the companions the old texts did not;
- every pin line the cascade tables list reads its digest at the base, and level 1 is complete over the records and tools.

These are predicates on record text: they establish no electrical or thermal property, close nothing and accept nothing.
"""
import ast
import difflib
import hashlib
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

PATCH = "v2/docs/records/l4e9/L4E9-W5-PATCH.md"
GEN = "v2/docs/records/l4e9/l4e9_power_path.py"
PAGE = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
REG = "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"
BASE, W5, R1 = "3e566c551498f66bda0c092581ce71016ea9bd30", "cd19df597350b8f56b78fc172e6966e78dba8049", "515f6cf2"
BRK_MD = "v2/docs/records/l8p/L8P-BREAKER.md"
SIX = ["R-206", "R-207", "R-208", "R-222", "R-244", "R-246"]
L8P_DRAFTS = {"apply_gen_sch_p_breaker.py", "apply_gen_sch_p_idealdiode.py", "apply_gen_sch_e_enable.py", "apply_gen_sch_a_ptc.py",
              "apply_gen_sch_a_thguard.py", "apply_gen_sch_a_thgfs.py"}
GROUPS = {"re-take": ["WP-%02d" % i for i in range(1, 7)], "list": ["WP-%02d" % i for i in range(7, 23)]}
DOCS = ["WP-%02d" % i for i in range(23, 28)]
SET31_BASE = "a6e3a066a827b8504e8ce804f82c77dac6955c93"   # fnd/int31's tip: every row pending (the history side)
APPLIED_AT = "bad162ad"   # fnd/int31l4e9: W24 applied WP-01 to WP-22 and the re-take (set 31); WP-23 to WP-27 not applied
DASHES = (chr(0x2013), chr(0x2014))
_C = {}


def _read(rel):
    if rel not in _C:
        _C[rel] = open(need(os.path.join(ROOT, rel), "a file this module reads"), encoding="utf-8").read()
    return _C[rel]


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _git_show(commit, rel):
    """The file's bytes at a commit, or None when this host has no git or not that commit (a code-only checkout, a box clone)."""
    try:
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, rel)], capture_output=True)
    except OSError:
        return None
    return r.stdout if r.returncode == 0 else None


def _rows():
    text = _read(PATCH)
    out = {}
    for blk in re.split(r"\n### ", text)[1:]:
        blk = re.split(r"\n## |\n#### ", blk)[0]
        rid = blk.split(".", 1)[0].strip()
        r = {"title": blk.split("\n", 1)[0]}
        for ln in blk.split("\n"):
            m = re.match(r"- (File|Line|Kind|Pairs with|Source|Class): (.*)$", ln)
            if m:
                r[m.group(1)] = m.group(2).strip().strip("`")
        fences = re.findall(r"```text\n(.*?)\n```", blk, re.S)
        assert len(fences) == 2, "%s: an Old and a New block" % rid
        r["old"], r["new"] = fences
        assert r["old"] != r["new"], "%s: the New text differs" % rid
        out[rid] = r
    return out


def _find(lines, block):
    k = len(block)
    return [i for i in range(len(lines) - k + 1) if lines[i:i + k] == block]


def _where(r, text):
    """('old' | 'new'): which side of the row stands in `text` where the row says; refuses neither or both."""
    lines = text.split("\n")
    n = int(r["Line"])
    if r["Kind"] in ("line", "lines"):
        old_here = _find(lines, r["old"].split("\n")) == [n - 1]
        new_here = len(_find(lines, r["new"].split("\n"))) == 1
    else:
        old_here = r["old"] in lines[n - 1] and text.count(r["old"]) == 1
        new_here = text.count(r["new"]) == 1
    assert old_here != new_here, "%s: neither its Old nor its New text stands alone where the row says" % r["title"]
    return "old" if old_here else "new"


def _old_left(r, text):
    """Whether row r's Old text still stands in `text` outside its New text (a line row by its whole lines; W25)."""
    if r["Kind"] in ("line", "lines"):
        lines, nb = text.split("\n"), r["new"].split("\n")
        at = _find(lines, nb)
        rest = lines[:at[0]] + ["\0"] + lines[at[0] + len(nb):] if len(at) == 1 else lines
        return bool(_find(rest, r["old"].split("\n")))
    return r["old"] in text.replace(r["new"], "\0")


def _turn(r, text, to):
    """`text` with row r turned to side `to` (a no-op when it stands there already)."""
    frm = "old" if to == "new" else "new"
    if _where(r, text) == to:
        return text
    a, b = r[frm], r[to]
    if r["Kind"] in ("line", "lines"):
        lines = text.split("\n")
        at = _find(lines, a.split("\n"))
        assert len(at) == 1
        return "\n".join(lines[:at[0]] + b.split("\n") + lines[at[0] + len(a.split("\n")):])
    assert text.count(a) == 1
    return text.replace(a, b)


def _side(rows, ids, to):
    """{file: text} with every row of `ids` turned to `to`, in memory."""
    out = {}
    for rid in ids:
        r = rows[rid]
        out[r["File"]] = _turn(r, out.get(r["File"], _read(r["File"])), to)
    return out


def _copies():
    """The copy sections: [{'crel', 'drel', 's0', 's1', 'lm', 'diff'}]."""
    text = _read(PATCH)
    out = []
    for sec in re.split(r"\n#### The copy ", text)[1:]:
        sec = re.split(r"\n## |\n#### ", sec)[0]
        crel = re.match(r"`([^`]+)`", sec).group(1)
        s0 = re.search(r"- The base copy: sha256 `([0-9a-f]{64})`", sec).group(1)
        m = re.search(r"- W5's file: `([^`]+)` at `cd19df59`, sha256 `([0-9a-f]{64})`; the same bytes at `([0-9a-f]{8})`", sec)
        lm = re.search(r"- The copy's LM5069 lines: ([^\n]*)\.\n", sec).group(1)
        lm = [int(x) for x in lm.split(", ")] if lm[0].isdigit() else []
        diff = re.search(r"```diff\n(.*?)\n```", sec, re.S).group(1).split("\n")
        out.append({"crel": crel, "drel": m.group(1), "s1": m.group(2), "last": m.group(3), "s0": s0, "lm": lm, "diff": diff})
    assert len(out) == 3, "three copies"
    return out


def _w5_bytes(c):
    b = _git_show(W5, c["drel"])
    if b is None:
        p = os.path.join(ROOT, c["drel"])
        if os.path.exists(p) and _sha(open(p, "rb").read()) == c["s1"]:
            return open(p, "rb").read()
        raise Skip("W5's branch (fnd/w5l8p cd19df59) is not in this object store and the tree's draft has moved")
    return b


def _copy_bytes(c):
    p = os.path.join(ROOT, c["crel"])
    if os.path.exists(p):
        return open(p, "rb").read()
    b = _git_show(BASE, c["crel"])
    if b is None:
        raise Skip("the copy was re-taken and the base %s is not in this object store" % BASE[:8])
    return b


def _change_order(src):
    """rid -> Depends text, from the generator's CHANGE_ORDER by its syntax tree."""
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "CHANGE_ORDER":
            return {e.elts[1].value: e.elts[3].value for e in n.value.elts}
    raise AssertionError("no CHANGE_ORDER")


def _page_changes(page):
    """rid -> Depends cell of the page's change list (section 3)."""
    lines = page.split("\n")
    i = [k for k, ln in enumerate(lines) if ln.startswith("| # | Step | Row | Board and generator | Apply script | Depends on |")]
    assert len(i) == 1, "one change list on the page"
    out = {}
    for ln in lines[i[0] + 2:]:
        if not ln.startswith("|"):
            break
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        out[c[2]] = c[5]
    return out


def _companions(text):
    m = re.findall(r"[Ii]n one release with ((?:R-\d+, )*R-\d+ and R-\d+)", text)
    return [re.findall(r"R-\d+", x) for x in m]


def _rid_of(r):
    m = re.search(r"\b(R-2\d\d)\b", r["title"])
    return m.group(1)


def t_every_row_stands_where_it_says_and_no_group_is_half_applied():
    rows = _rows()
    assert sorted(rows) == ["WP-%02d" % i for i in range(1, 28)], sorted(rows)
    for rid, r in rows.items():
        for k in ("File", "Line", "Kind", "Pairs with", "Source", "Class"):
            assert r.get(k), "%s has no %s" % (rid, k)
        assert re.match(r"(BINDING|PRESENTATION|CLAIM CHANGE)\b", r["Class"]), (rid, r["Class"])
        assert not any(d in r["old"] + r["new"] for d in DASHES), rid
    for name, ids in GROUPS.items():
        sides = {_where(rows[i], _read(rows[i]["File"])) for i in ids}
        assert len(sides) == 1, "the %s rows are half applied: %s" % (name, sorted(sides))
        # W25: applied at this tree (W24, bad162ad), every Old text gone
        assert sides == {"new"}, "the %s rows are not applied at this tree (W24, %s)" % (name, APPLIED_AT)
        assert not [i for i in ids if _old_left(rows[i], _read(rows[i]["File"]))], "an applied %s row's Old text still stands" % name
    for rid in DOCS:
        # not applied (the coordinator's decision: only with the next circuit change to those drafts): the Old text once, as before
        assert _where(rows[rid], _read(rows[rid]["File"])) == "old", "%s was applied" % rid
    # the re-take (section 2) applied: each new pin's copy stands with its digest, round 1's copy is gone
    for rid in ("WP-01", "WP-02", "WP-03"):
        _k, (p_old, s_old) = list(ast.literal_eval("{" + rows[rid]["old"].strip().rstrip(",") + "}").items())[0]
        _k, (p_new, s_new) = list(ast.literal_eval("{" + rows[rid]["new"].strip().rstrip(",") + "}").items())[0]
        assert _sha(open(os.path.join(ROOT, p_new), "rb").read()) == s_new, "%s: the copy %s is not the pinned bytes" % (rid, p_new)
        assert not os.path.exists(os.path.join(ROOT, p_old)), "%s: round 1's copy %s still stands" % (rid, p_old)
    # history: at fnd/int31's a6e3a066 every row stood pending, its Old text where it says and round 1's copies in place
    base = {}
    for rid, r in rows.items():
        b = _git_show(SET31_BASE, r["File"])
        if b is None:
            raise Skip("fnd/int31's %s is not in this object store (the history side)" % SET31_BASE[:8])
        base[r["File"]] = b.decode("utf-8")
    for rid, r in rows.items():
        assert _where(r, base[r["File"]]) == "old", "%s did not stand pending at %s" % (rid, SET31_BASE[:8])
    for rid in ("WP-01", "WP-02", "WP-03"):
        _k, (p_old, s_old) = list(ast.literal_eval("{" + rows[rid]["old"].strip().rstrip(",") + "}").items())[0]
        assert _sha(_git_show(SET31_BASE, p_old)) == s_old, "%s: round 1's copy at %s" % (rid, SET31_BASE[:8])
    # a mutation: a fragment row and a re-take row reverted in memory at this tree are refused (the row numbers are the base's, so a
    # reverted Old text off its base line reads "neither"; either way the applied predicate above fails on it)
    for rid in ("WP-07", "WP-01"):
        r = rows[rid]
        reverted = _turn(r, _read(r["File"]), "old")
        try:
            side = _where(r, reverted)
        except AssertionError:
            side = None
        assert side != "new" and _old_left(r, reverted), "%s reverted is not refused" % rid
    text = _read(PATCH)
    assert not any(d in text for d in DASHES), "a dash in the patch file"
    assert "## 6. ONLY WITH THE NEXT CIRCUIT CHANGE TO THESE DRAFTS" in text
    assert text.index("## 6. ONLY WITH THE NEXT CIRCUIT CHANGE") < text.index("### WP-23.") and text.index("### WP-22.") < text.index("## 6. ")


def t_the_copies_digests_lines_and_diffs_recomputed():
    for c in _copies():
        cb, wb = _copy_bytes(c), _w5_bytes(c)
        assert _sha(cb) == c["s0"] and _sha(wb) == c["s1"], c["crel"]
        r1 = _git_show(R1, c["drel"])
        if r1 is not None:
            assert r1 == cb, "the copy is not round 1's draft byte for byte: %s" % c["crel"]
        last = _git_show(c["last"], c["drel"])
        if last is not None:
            assert last == wb, "W5's bytes are not the draft at its last change %s" % c["last"]
        lm = [i + 1 for i, ln in enumerate(cb.decode().split("\n")) if "LM5069" in ln]
        assert lm == c["lm"], (c["crel"], lm)
        assert all("LM5069-2" in ln or "LM5069MM-2" in ln for ln in (cb.decode().split("\n")[i - 1] for i in lm)), "a copy line names the -1"
        diff = list(difflib.unified_diff(cb.decode().splitlines(), wb.decode().splitlines(), "a/%s" % c["crel"],
                                         "b/%s@cd19df59" % c["drel"], n=3, lineterm=""))
        assert diff == c["diff"], "the quoted diff of %s is not the bytes' diff" % c["crel"]
        assert not any(re.search(r"LM5069(MM)?-2\b", ln) for ln in wb.decode().split("\n") if "U101" in ln), "W5's file draws U101 as the -2"


def t_the_retaken_bytes_meet_the_generators_checks_on_a_copy():
    src = _read(GEN)
    tree = ast.parse(src)
    pat = [n.args[0].value for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "search"
           and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str) and "APPLIED" in n.args[0].value]
    assert len(pat) == 1, pat
    drafts = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "L8_DRAFTS":
            drafts = {e.elts[0].value: (e.elts[1].value, e.elts[2].value) for e in n.value.elts}
    for c in _copies():
        key = [k for k, (nm, _t) in drafts.items() if k.startswith("l8p_") and c["drel"].endswith(nm + ".py")]
        assert len(key) == 1, c["drel"]
        target = drafts[key[0]][1]
        txt = _w5_bytes(c).decode()
        assert re.search(pat[0], txt[:3000]) and target in txt, "the re-taken %s would be refused by the generator" % c["drel"]
        cut = re.sub(r"NOT\s+APPLIED", "NOT YET IN", txt[:3000]) + txt[3000:]
        assert not (re.search(pat[0], cut[:3000]) and target in cut), "the check passes a copy without its draft marker"


def t_the_new_pins_name_the_drafts_current_bytes_and_their_commit():
    rows = _rows()
    cps = {c["drel"].split("/")[-1][:-3]: c for c in _copies()}
    for rid in ("WP-01", "WP-02", "WP-03"):
        r = rows[rid]
        k_old, (p_old, s_old) = list(ast.literal_eval("{" + r["old"].strip().rstrip(",") + "}").items())[0]
        k_new, (p_new, s_new) = list(ast.literal_eval("{" + r["new"].strip().rstrip(",") + "}").items())[0]
        assert k_old == k_new
        d = re.match(r"v2/docs/records/l4e9/inputs/l8p-(apply_gen_sch_[a-z_]+)-515f6cf2\.txt$", p_old).group(1)
        c = cps[d]
        assert p_old == c["crel"] and s_old == c["s0"], rid
        assert p_new == "v2/docs/records/l4e9/inputs/l8p-%s-%s.txt" % (d, c["last"]) and s_new == c["s1"], rid
        try:
            lg = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%H", BASE, "--", c["drel"]], capture_output=True, text=True)
        except OSError:
            lg = None
        if lg is not None and lg.returncode == 0 and lg.stdout.strip():
            assert lg.stdout.strip().startswith(c["last"]), "%s: the draft last changed at %s" % (rid, lg.stdout.strip()[:8])


def t_each_change_list_row_equals_its_page_cell_on_both_sides():
    rows = _rows()
    ids = GROUPS["list"]
    for to in ("old", "new"):
        files = _side(rows, ids, to)
        co = _change_order(files.get(GEN, _read(GEN)))
        pc = _page_changes(files.get(PAGE, _read(PAGE)))
        for g in ("WP-07", "WP-09", "WP-11", "WP-13", "WP-15", "WP-17"):
            rid = _rid_of(rows[g])
            assert co[rid] == pc[rid], "%s side: %s's page cell is not the script's" % (to, rid)
    gen_new = _side(rows, ids, "new")
    for f in (GEN, PAGE, REG):
        assert "l8p section 5" not in gen_new[f], "%s still cites l8p section 5" % f
        assert "l8p section 5" in _side(rows, ids, "old")[f], "%s: the old side has no l8p section 5" % f


def t_the_six_companions_are_named_by_every_new_text_and_by_no_old_one():
    rows = _rows()
    reg = _read(REG)
    for rid in ("R-206", "R-207", "R-208"):
        line = [ln for ln in reg.split("\n") if ln.startswith("| %s |" % rid)][0]
        assert _companions(line) == [[x for x in SIX if x != rid]], "the register's %s does not name the other five" % rid
    md = _git_show(W5, BRK_MD)
    if md is not None:
        item = md.decode().split("\n1. **One release for the six drafts")[1].split("\n2. **Board P")[0]
        tab = re.findall(r"\| `(apply_[a-z_]+\.py)` \| [PEA] \| (R-\d+) \|", item)
        assert sorted(r for _d, r in tab) == SIX and {d for d, _r in tab} == L8P_DRAFTS, tab
    for i in range(7, 22):
        r = rows["WP-%02d" % i]
        own = _rid_of(r)
        new, old = _companions(r["new"]), _companions(r["old"])
        assert new == [[x for x in SIX if x != own]], (r["title"], new)
        assert "(record l8p's drafts, L8P-BREAKER.md section 6 item 1)" in r["new"]
        assert not old or len(old[0]) < 5, (r["title"], old)


def t_r208s_citation_reads_what_each_commit_prints():
    rows = _rows()
    r = rows["WP-22"]
    assert "(l8p section 5)" in r["old"] and "R248 and C247" in r["old"]
    assert "l8p section 6 item 4" in r["new"] and "R264 and C264" in r["new"] and "R248 and C247 were round 1's" in r["new"]
    assert "(l8p section 6 item 4)" in rows["WP-07"]["new"] and "(l8p section 5)" in rows["WP-07"]["old"]
    old = _git_show(R1, BRK_MD)
    new = _git_show(W5, BRK_MD)
    if old is None or new is None:
        raise Skip("record l8p at 515f6cf2 or W5's branch at cd19df59 is not in this object store")
    old, new = old.decode(), new.decode()
    s5 = old.split("\n## 5. ")[1].split("\n## 6. ")[0]
    assert s5.startswith("Order constraints for L4-E9's change list") and "still takes R248 and C247" in s5
    assert new.split("\n## 5. ")[1].startswith("Designators per draft")
    s6 = new.split("\n## 6. ")[1].split("\n## 7. ")[0]
    assert s6.startswith("Order constraints for L4-E9's change list")
    i4 = " ".join(s6.split("\n4. **Board A: step 3g")[1].split("\n5. **")[0].split())
    assert "It adds no R or C, so by itself it composes anywhere" in i4 and "mainpb takes R264 and C264 on this tree's order" in i4
    assert "R248" not in s6, "section 6 still prints round 1's designators"


def t_the_docstring_rows_change_one_docstring_and_name_the_companions():
    rows = _rows()
    for rid in DOCS:
        r = rows[rid]
        text = _read(r["File"])
        old, new = _turn(r, text, "old"), _turn(r, text, "new")
        to, tn = ast.parse(old), ast.parse(new)
        do, dn = ast.get_docstring(to, clean=False), ast.get_docstring(tn, clean=False)
        assert do != dn and r["old"] in do and r["new"] in dn, rid
        to.body, tn.body = to.body[1:], tn.body[1:]
        assert ast.dump(to) == ast.dump(tn), "%s changes more than the module docstring" % rid
        base = os.path.basename(r["File"])
        flat = " ".join(r["new"].split())
        if base in L8P_DRAFTS:
            want = L8P_DRAFTS - {base}
            got = set(re.findall(r"apply_gen_sch_[a-z_]+\.py", " ".join(r["new"].split())))
            assert got == want, (rid, sorted(want - got))
            assert len(set(re.findall(r"apply_gen_sch_[a-z_]+\.py", r["old"])) & want) < 5, rid
            assert "section 6 item 1" in flat and "never alone" in flat, rid
        else:
            assert "six drafts" in flat and "three drafts" in r["old"] and "section 6 item 1" in flat, rid


def _pin_tables():
    text = _read(PATCH)
    out = {}
    for sec in re.split(r"\n#### The pins of ", text)[1:]:
        sec = re.split(r"\n## |\n#### |\n### ", sec)[0]
        m = re.match(r"`([^`]+)` \(sha256/16 `([0-9a-f]{16})`\): (\d+) files at level 1, (\d+) files in the cascade", sec)
        tab = re.findall(r"^\| (\d+) \| `([^`]+)` \| (\d+) \| `([^`]+)` \| `([0-9a-f]{16})` \|$", sec, re.M)
        out[m.group(1)] = {"s16": m.group(2), "n1": int(m.group(3)), "n": int(m.group(4)),
                           "rows": [(int(a), b, int(c), d, e) for a, b, c, d, e in tab]}
    return out


def _base_tree_texts():
    """{path: text} of every tracked file under v2/docs/records and v2/ecad/tools at the base, read with one git cat-file stream."""
    try:
        ls = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "-z", BASE, "--", "v2/docs/records", "v2/ecad/tools"],
                            capture_output=True, text=True)
    except OSError:
        return None
    if ls.returncode != 0:
        return None
    ents = [ln.split("\t", 1) for ln in ls.stdout.split("\0") if ln]
    ents = [(meta.split()[2], path) for meta, path in ents if meta.split()[1] == "blob"]
    r = subprocess.run(["git", "-C", ROOT, "cat-file", "--batch"], input="".join(s + "\n" for s, _p in ents).encode(), capture_output=True)
    data, out, pos = r.stdout, {}, 0
    for _s, path in ents:
        nl = data.index(b"\n", pos)
        size = int(data[pos:nl].split()[2])
        out[path] = data[nl + 1:nl + 1 + size].decode("utf-8", "replace")
        pos = nl + 1 + size + 1
    return out


def t_every_listed_pin_reads_its_digest_at_the_base_and_level_one_is_complete():
    tabs = _pin_tables()
    rows = _rows()
    assert sorted(tabs) == sorted(rows[i]["File"] for i in DOCS), sorted(tabs)
    texts = _base_tree_texts()
    if texts is None:
        raise Skip("the base %s is not in this object store" % BASE[:8])
    for draft, t in tabs.items():
        assert _sha(texts[draft].encode())[:16] == t["s16"], draft
        files = set()
        for lv, f, n, pinned, s16 in t["rows"]:
            assert _sha(texts[pinned].encode())[:16] == s16, (f, pinned)
            assert s16 in texts[f].split("\n")[n - 1], "%s line %d does not print %s" % (f, n, s16)
            files.add(f)
        l1 = {f for lv, f, _n, _p, _s in t["rows"] if lv == 1}
        assert len(l1) == t["n1"] and len(files) == t["n"], draft
        found = {p for p, x in texts.items() if p != draft and t["s16"] in x}
        assert found == l1, "level 1 of %s: listed %s, found %s" % (draft, sorted(l1 - found), sorted(found - l1))
