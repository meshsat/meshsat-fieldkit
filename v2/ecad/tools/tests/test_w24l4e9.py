"""W24 (MESHSAT-1357, 6 October 2026): set 31's application of the filed patch rows, held as predicates on the tree.

What was applied on branch fnd/int31l4e9 from a6e3a066 (fnd/int31's tip), every new text verbatim from its row:
- W7's rows P-01 to P-12 (v2/docs/records/l4e9/L4E9-4588-PATCH.md): L4-E9's page and generator;
- W13's rows WP-01 to WP-22 (v2/docs/records/l4e9/L4E9-W5-PATCH.md) with the re-take of the three verbatim l8p inputs by the
  row file's own git show and git rm commands;
- W20's rows for six files (v2/docs/records/int30/NEXT-SET-SMALL-ITEMS.patch.md): W20-01 to W20-12, W20-15, W20-16, W20-17,
  W20-23, W20-24; and W20-N1a's candidate A, the coordinator's decision N1a of 05:28 CEST;
- W14's PATCH_L5F11_ORDER (a literal in tests/test_w14l5.py) to v2/docs/records/l5pwr/apply_l5f11_contracts.py;
- then the four typed-in pins, each the sha256 of its file as it stands after every edit above.

NOT applied, and held so: W13's WP-23 to WP-27 (the coordinator's decision: only with the next circuit change to those drafts) and
R-217's release words (W20-N2: they wait for record l4e11's restatement of E11-43).

The predicates: every applied row's new text stands once in its file and its old text is gone (a line row by its whole line; a row
whose new text contains its old is read with the new text taken out); on the base commit the same predicate names every applied
row; the four pins equal the sha256 of their files; the re-taken copies are the drafts' bytes at the commits they are named after;
WP-23 to WP-27 and R-217's three texts stand as they were; the touched scripts parse and the interfaces YAML loads; no em or en
dash. Predicates on record text: they establish no electrical or thermal property, close nothing and accept nothing.
"""
import ast
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

BASE = "a6e3a066a827b8504e8ce804f82c77dac6955c93"
P7 = "v2/docs/records/l4e9/L4E9-4588-PATCH.md"
P13 = "v2/docs/records/l4e9/L4E9-W5-PATCH.md"
P20 = "v2/docs/records/int30/NEXT-SET-SMALL-ITEMS.patch.md"
W14 = "v2/ecad/tools/tests/test_w14l5.py"
PAGE = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
GEN = "v2/docs/records/l4e9/l4e9_power_path.py"
REG = "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"
E11 = "v2/docs/records/l4e11/l4e11_power.py"
HWFW = "v2/docs/HW-FW-CONTRACT.md"
IFACES = "v2/ecad/tools/pcb_interfaces.yaml"
SUPP = "v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md"

APPLIED = (["P-%02d" % i for i in range(1, 13)] + ["WP-%02d" % i for i in range(1, 23)]
           + ["W20-%02d" % i for i in list(range(1, 13)) + [15, 16, 17, 23, 24]] + ["W20-N1a", "PATCH_L5F11_ORDER"])
HELD = ["WP-%02d" % i for i in range(23, 28)]
# the files the brief allows this branch to change (the test module aside)
ALLOWED = {PAGE, GEN, REG, E11, HWFW, IFACES, "v2/docs/records/l9t5/l9t5_connected.py",
           "v2/docs/records/l9t5/apply_l4e9_changelist_p0.py", "v2/docs/records/l5pwr/apply_l5f11_contracts.py"}
# the re-take of W13's section 2: (generator pin key, old copy, new copy, commit, draft)
RETAKE = (("l8p_breaker", "l8p-apply_gen_sch_p_breaker-515f6cf2.txt", "l8p-apply_gen_sch_p_breaker-6eeb6cfe.txt", "6eeb6cfe",
           "v2/docs/records/l8p/apply_gen_sch_p_breaker.py"),
          ("l8p_enable", "l8p-apply_gen_sch_e_enable-515f6cf2.txt", "l8p-apply_gen_sch_e_enable-69b8c3bb.txt", "69b8c3bb",
           "v2/docs/records/l8p/apply_gen_sch_e_enable.py"),
          ("l8p_ptc", "l8p-apply_gen_sch_a_ptc-515f6cf2.txt", "l8p-apply_gen_sch_a_ptc-8e6a938c.txt", "8e6a938c",
           "v2/docs/records/l8p/apply_gen_sch_a_ptc.py"))
INPUTS = "v2/docs/records/l4e9/inputs"
# the four typed-in pins and the values they held at the base
OLD_PINS = {"hwfw": "9b0d04c39beafb7dd3ef3269b05e2230fe68ee019dc83c2e0c9be0ea80d391db",
            "ifaces": "393305bed4edfd26588164da96871f17ce70492688e5648729545a3cc5987023",
            "ow4": "43c524c32e68c085"}
DASHES = (chr(0x2013), chr(0x2014))
_T = {}
_G = {}


def _read(rel):
    if rel not in _T:
        _T[rel] = open(need(os.path.join(ROOT, rel), "a file of this branch"), encoding="utf-8").read()
    return _T[rel]


def _sha(rel):
    return hashlib.sha256(open(need(os.path.join(ROOT, rel), "a pinned file"), "rb").read()).hexdigest()


def _show(rev, rel):
    k = (rev, rel)
    if k not in _G:
        need(os.path.join(ROOT, ".git"), "a git checkout")
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, rel)], capture_output=True)
        if r.returncode != 0:
            raise Skip("%s:%s is not in this object store" % (rev, rel))
        _G[k] = r.stdout
    return _G[k]


def _rows():
    """Every row of the three patch files, parsed from the files as committed (the File, the Kind, the Old and New blocks)."""
    out = {}
    for rel in (P7, P13, P20):
        t = _read(rel)
        for m in re.finditer(r"^### ((?:P|WP|W20)-\d+)\. .*?$(.*?)(?=^### |^## |\Z)", t, re.S | re.M):
            body = m.group(2)
            out[m.group(1)] = dict(id=m.group(1), file=re.search(r"^- File: `([^`]+)`", body, re.M).group(1),
                                   kind=re.search(r"^- Kind: (.*)$", body, re.M).group(1),
                                   old=re.search(r"^- Old:\n\n```text\n(.*?)\n```\n", body, re.S | re.M).group(1),
                                   new=re.search(r"^- New:\n\n```text\n(.*?)\n```\n", body, re.S | re.M).group(1))
    t = _read(P20)
    m = re.search(r"- \*\*W20-N1a\*\*, `([^`]+)` line \d+, Old:\n\n```text\n(.*?)\n```\n\n  Candidate A:\n\n```text\n(.*?)\n```\n", t, re.S)
    out["W20-N1a"] = dict(id="W20-N1a", file=m.group(1), kind="fragment", old=m.group(2), new=m.group(3))
    for node in ast.parse(_read(W14)).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "PATCH_L5F11_ORDER":
            d = ast.literal_eval(node.value)
            out["PATCH_L5F11_ORDER"] = dict(id="PATCH_L5F11_ORDER", file=d["file"], kind="lines", old=d["old"], new=d["new"])
    return out


def _n2():
    """W20-N2a to N2c: R-217's release words, their Old text and candidate B (neither written: the coordinator's N2 waits)."""
    t = _read(P20)
    out = []
    for m in re.finditer(r"- \*\*(W20-N2[abc])\*\*, `([^`]+)` line \S+, Old:\n\n```text\n(.*?)\n```\n\n  Candidate A:\n\n```text\n(.*?)\n```"
                         r"\n\n  Candidate B:\n\n```text\n(.*?)\n```", t, re.S):
        out.append(dict(id=m.group(1), file=m.group(2), old=m.group(3), b=m.group(5)))
    return out


def _whole_line(kind, old):
    return kind.startswith("line") and not old.endswith("\n")


def _count_old(text, r):
    if _whole_line(r["kind"], r["old"]):
        return len(re.findall(r"(?m)^" + re.escape(r["old"]) + r"$", text))
    return text.count(r["old"])


def problems(texts, rows):
    """The ids of the rows whose new text does not stand once in its file, or whose old text still stands outside the new."""
    bad = []
    for r in rows:
        t = texts[r["file"]]
        if t.count(r["new"]) != 1:
            bad.append((r["id"], "new text %d times" % t.count(r["new"])))
            continue
        rest = t.replace(r["new"], "\0")
        if _count_old(rest, r):
            bad.append((r["id"], "old text still present"))
    return bad


def _pins(texts):
    """The four typed-in pins as the files carry them: (name, file, line, value), the two generators read by ast."""
    out = []
    for rel, keys in ((GEN, ("hwfw", "ifaces")), (E11, ("hwfw",))):
        for node in ast.walk(ast.parse(texts[rel])):
            if isinstance(node, ast.Dict):
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and k.value in keys and isinstance(v, ast.Tuple):
                        out.append((k.value, rel, k.lineno, v.elts[0].value, v.elts[1].value))
    rows = [(i, ln) for i, ln in enumerate(texts[PAGE].split("\n"), 1) if ln.startswith("| OW-4 |")]
    assert len(rows) == 1, "the page has %d OW-4 rows" % len(rows)
    i, ln = rows[0]
    m = re.findall(r"`(%s)`, in the tree, ([0-9a-f]{16}), UNSENT" % re.escape(SUPP), ln)
    assert len(m) == 1, "OW-4's cell names %s %d times" % (SUPP, len(m))
    out.append(("ow4", PAGE, i, m[0][0], m[0][1]))
    return out


def t_the_brief_rows_are_the_ones_held_and_only_allowed_files_are_named():
    rows = _rows()
    missing = [i for i in APPLIED + HELD if i not in rows]
    assert not missing, missing
    assert sorted({rows[i]["file"] for i in APPLIED}) == sorted(ALLOWED - {E11}), sorted({rows[i]["file"] for i in APPLIED})
    assert {rows[i]["file"] for i in HELD} == {"v2/docs/records/l8p/apply_gen_sch_p_breaker.py", "v2/docs/records/l8p/apply_gen_sch_e_enable.py",
                                              "v2/docs/records/l8p/apply_gen_sch_a_ptc.py", "v2/docs/records/l8p/apply_gen_sch_a_thguard.py",
                                              "v2/docs/records/l4e11/apply_gen_sch_a_dd7.py"}


def t_every_applied_row_stands_once_and_its_old_text_is_gone():
    rows = [_rows()[i] for i in APPLIED]
    texts = {r["file"]: _read(r["file"]) for r in rows}
    bad = problems(texts, rows)
    assert not bad, bad


def t_on_the_base_the_predicate_names_every_applied_row():
    rows = [_rows()[i] for i in APPLIED]
    texts = {r["file"]: _show(BASE, r["file"]).decode("utf-8") for r in rows}
    named = {i for i, _ in problems(texts, rows)}
    assert named == set(APPLIED), sorted(set(APPLIED) - named)
    for r in rows:   # each old text stood once on the base, by its kind (the stop rule of the brief; P-12, a line row, by its whole line)
        assert _count_old(texts[r["file"]], r) == 1, (r["id"], _count_old(texts[r["file"]], r))


def t_a_row_reverted_or_doubled_is_named():
    rows = _rows()
    for rid in ("P-09", "WP-22", "W20-24", "W20-N1a", "PATCH_L5F11_ORDER"):
        r = rows[rid]
        t = _read(r["file"])
        assert problems({r["file"]: t.replace(r["new"], r["old"])}, [r]), "%s reverted is not named" % rid
        assert problems({r["file"]: t + "\n" + r["new"]}, [r]), "%s doubled is not named" % rid


def t_the_four_typed_in_pins_equal_their_files():
    texts = {rel: _read(rel) for rel in (GEN, E11, PAGE)}
    pins = _pins(texts)
    assert sorted((n, rel) for n, rel, _l, _p, _v in pins) == sorted([("hwfw", GEN), ("ifaces", GEN), ("hwfw", E11), ("ow4", PAGE)]), pins
    for name, rel, line, path, value in pins:
        want = _sha(path)
        assert value == (want[:16] if name == "ow4" else want), "%s:%d pins %s at %s, the file reads %s" % (rel, line, path, value, want)
        assert value != OLD_PINS[name], "%s:%d still holds the base value" % (rel, line)
    assert {p for _n, _r, _l, p, _v in pins} == {HWFW, IFACES, SUPP}


def t_a_pin_on_changed_bytes_is_named():
    texts = {rel: _read(rel) for rel in (GEN, E11, PAGE)}
    for name, rel, line, path, value in _pins(texts):
        mutated = hashlib.sha256(open(os.path.join(ROOT, path), "rb").read() + b"\n").hexdigest()
        assert value != (mutated[:16] if name == "ow4" else mutated), (rel, line)


def t_the_retaken_copies_are_the_drafts_bytes_and_round_1s_are_gone():
    g = ast.parse(_read(GEN))
    pins = {}
    for node in ast.walk(g):
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value in ("l8p_breaker", "l8p_enable", "l8p_ptc") and isinstance(v, ast.Tuple):
                    pins[k.value] = (v.elts[0].value, v.elts[1].value)
    for key, old, new, commit, draft in RETAKE:
        assert pins[key] == ("%s/%s" % (INPUTS, new), _sha("%s/%s" % (INPUTS, new))), (key, pins[key])
        assert not os.path.exists(os.path.join(ROOT, INPUTS, old)), "round 1's copy %s still stands" % old
        t = _read("%s/%s" % (INPUTS, new))
        assert re.search(r"NOT\s+APPLIED|DRAFT\s+for\s+the\s+integrator", t[:3000]), "%s lost the draft marker the generator reads" % new


def t_the_retaken_copies_equal_git_show_at_their_commits():
    for _key, _old, new, commit, draft in RETAKE:
        assert open(os.path.join(ROOT, INPUTS, new), "rb").read() == _show(commit, draft), new


def t_wp23_to_wp27_and_r217s_words_stand_unapplied():
    rows = _rows()
    for rid in HELD:
        r = rows[rid]
        t = _read(r["file"])
        assert _count_old(t, r) == 1, "%s: its old text no longer stands once" % rid
        assert r["new"] not in t, "%s: its new text was written" % rid
    n2 = _n2()
    assert [n["id"] for n in n2] == ["W20-N2a", "W20-N2b", "W20-N2c"], n2
    assert [n["file"] for n in n2] == [REG, GEN, PAGE], [n["file"] for n in n2]
    for n in n2:
        t = _read(n["file"])
        assert t.count(n["old"]) == 1, "%s: R-217's words no longer stand once" % n["id"]
        assert n["b"] not in t, "%s: candidate B was written" % n["id"]


def t_the_touched_scripts_parse_and_the_interfaces_yaml_loads():
    for rel in (GEN, E11, "v2/docs/records/l9t5/l9t5_connected.py", "v2/docs/records/l9t5/apply_l4e9_changelist_p0.py",
                "v2/docs/records/l5pwr/apply_l5f11_contracts.py"):
        ast.parse(_read(rel))
    try:
        import yaml
    except ImportError:
        raise Skip("PyYAML is not importable on this host")
    assert isinstance(yaml.safe_load(_read(IFACES)), dict)


def t_no_em_or_en_dash_in_what_was_written():
    rows = _rows()
    for rid in APPLIED:
        for d in DASHES:
            assert d not in rows[rid]["new"], rid
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    for d in DASHES:
        assert d not in src, "this module carries a dash"
    for _n, rel, line, _p, _v in _pins({rel: _read(rel) for rel in (GEN, E11, PAGE)}):
        for d in DASHES:
            assert d not in _read(rel).split("\n")[line - 1], (rel, line)
