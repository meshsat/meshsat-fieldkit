"""W14 (MESHSAT-1357, 6 October 2026): record l5pwr's test module after W8's adoption. Two of test_l5pwr's tests pinned the answer
"already applied" of the two contract scripts of record l5pwr (apply_l5pwr2_contracts.py, apply_l5f11_contracts.py) on the tree's
contract files; W8 (fnd/w8l5 8840adda, finding L5-F14, adopted in the NEXT set) restated five texts those scripts wrote, so both
scripts refuse on the tree. test_l5pwr's two tests are restated there with their evidence basis; this module holds the reason for the
restatement, the proposed correction of the one detector found wrong, and W10's unchecked l5r2 item.

Base: fnd/w14l5 27cd9cd2 (fnd/w8l5 1ab30f35 with fnd/w1l5pwr 6ab17e21 merged). At this base the tree's two contract files are the
bytes of W8_COMMIT (`git diff 8840adda 27cd9cd2` on them is empty), and W8_BASE's are what set 30's candidate carries.

The predicates (software predicates on text; they establish no electrical property and accept nothing):
1. The old expectation ("exit 0, already applied") holds for both scripts on the files at W8_BASE and fails for both on the files at
   W8_COMMIT and on a scratch copy of the tree's files (never on the tree itself): the restatement's cause is W8's commit. On those
   two, apply_l5f11_contracts.py as it stood at SET31_BASE (before W24 applied PATCH_L5F11_ORDER) refuses at its ORDER check (history),
   and the tree's script, the row applied, refuses with its own state naming F11-09 (W25's restatement of 6 October 2026).
2. PATCH_L5F11_ORDER, the proposed correction of apply_l5f11_contracts.py's ORDER detector, was a PATCH ROW here and is APPLIED since
   W24's f0d0e54e (set 31, on fnd/int31l4e9 from a6e3a066; W25 restated this predicate on 6 October 2026). History, read through git:
   at SET31_BASE its old text is the script's lines 187 to 191 exactly once and its new text absent, and f0d0e54e's bytes are the
   base's with the row applied verbatim. Applied, at this tree: its new text is the script's lines 187 to 194 exactly once and its old
   text is gone; the tree's script, on scratch copies, gives every answer the patched source gave (BASE2: ORDER, naming the first
   script's old texts; BASE3: CHECK OK, 14 edits; W8_BASE: already applied) and, on W8_COMMIT's files and the tree's copy, the
   script's own accurate state (F11-09's old text gone, its new text absent: W8 restated it) where the base's script, executed in
   memory from the script's own path, still gives the false "is not applied" and the same answer wherever its ORDER check is right.
3. l5r2 (W10's unchecked item): read by parsing, not by running, record l5r2's generators would refuse on W8's text for no reason but a
   moved digest: W8's change touches only IF-EXT-DC's protection, bench and l4_defects; no key hc5's field contract reads, no contract
   of l5r2's no-loss set and no l5r2 row targets them; every l5r2 and l5r3 excerpt in a contract file and every figure l5r2 takes
   from pcb_interfaces.yaml is in W8_COMMIT's text; l5r3's section 3.8 is unchanged.
4. No em or en dash in this module.
"""
import ast
import contextlib
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l5pwr")
APPLY2 = os.path.join(REC, "apply_l5pwr2_contracts.py")
APPLY3 = os.path.join(REC, "apply_l5f11_contracts.py")
L5R2 = os.path.join(ROOT, "v2", "docs", "records", "l5r2", "l5r2_interfaces.py")
L5R3 = os.path.join(ROOT, "v2", "docs", "records", "l5r2", "l5r3_panel.py")
HC5 = os.path.join(ROOT, "v2", "docs", "records", "hc5", "check_contract_fields.py")
YAML_REL = "v2/ecad/tools/pcb_interfaces.yaml"
HWFW_REL = "v2/docs/HW-FW-CONTRACT.md"
W8_BASE = "53a68c7c"     # integration commit 2c on fnd/p0pwr: W8's base, the contract files as set 30's candidate carries them
W8_COMMIT = "8840adda"   # fnd/w8l5: the restatement of L5-F14 (in this branch's history)
BASE2 = "97dbcc43"       # test_l5pwr's: before apply_l5pwr2_contracts.py
BASE3 = "1c4e0ff2"       # test_l5pwr's: after apply_l5pwr2_contracts.py, before apply_l5f11_contracts.py
W8_FIELDS = {("IF-EXT-DC", "protection"), ("IF-EXT-DC", "bench"), ("IF-EXT-DC", "l4_defects")}
APPLY3_REL = "v2/docs/records/l5pwr/apply_l5f11_contracts.py"
SET31_BASE = "a6e3a066"  # fnd/int31's tip: the script before PATCH_L5F11_ORDER (W24's base)
APPLIED_AT = "f0d0e54e"  # fnd/int31l4e9: W24 applied PATCH_L5F11_ORDER verbatim (set 31, 6 October 2026)

sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

# THE PATCH ROW (proposed here by W14; APPLIED verbatim by W24 at f0d0e54e on fnd/int31l4e9 from a6e3a066, set 31: the tests below read
# the applied state since W25 of 6 October 2026, the new text once at lines 187 to 194 and the old text gone, and keep the base's
# old text once at lines 187 to 191 as history; test_l5pwr's t_the_l5f11_restatement_and_the_sweep_hold_on_the_tree_and_the_script_is_
# idempotent then expects the corrected answer instead of the ORDER refusal).
# File: v2/docs/records/l5pwr/apply_l5f11_contracts.py, lines 187 to 191 (main()) at a6e3a066; lines 187 to 194 since f0d0e54e.
# Basis: on W8's tree the script refuses "ORDER: apply_l5pwr2_contracts.py is not applied to these files", which is false: every old
# text of apply_l5pwr2_contracts.py is gone from the tree (it was applied at da85ab29), and W8 then restated four of its new texts
# (L5-F09 a to d). The detector tests the first script's verbatim "already applied" where it should test the presence of what that
# script did, its old texts removed: the same correction set 30 made to apply_l4e9_changelist_p0.py's applied_state() (records/l9t5,
# integration commit 53a68c7c: "the test is the PRESENCE of every row this draft adds ..., not the verbatim text"). The refusal itself
# stays: with the patch the script reads its own state and refuses "not in the state this script applies to: F11-01: old text 0
# time(s), new text present; ...", naming each of its fourteen edits and F11-09's as "old text 0 time(s), new text absent", which is
# accurate (W8 restated F11-09's l4_defects text). Not proposed, and why: a presence-keyed "already
# applied" for either script (as applied_state() answers for its draft) has no reader here (the only programmatic reader of either
# script's answer is this ORDER check; test_w8l5 names them in a comment only), and both docstrings prescribe a refusal for a state
# that is neither, which decision 11's Reverse (b) of L5-POWER-CONTRACTS.md expects "until the contracts and the scripts are restated".
PATCH_L5F11_ORDER = {
    "file": "v2/docs/records/l5pwr/apply_l5f11_contracts.py",
    "old": (
        '    # ORDER: apply_l5pwr2_contracts.py must be applied to these files first\n'
        '    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "apply_l5pwr2_contracts.py"), "--check", "--yaml", paths["yaml"],\n'
        '                        "--hwfw", paths["hwfw"]], capture_output=True, text=True)\n'
        '    if r.returncode != 0 or "already applied" not in r.stdout:\n'
        '        refuse("ORDER: apply_l5pwr2_contracts.py is not applied to these files (%s)" % (r.stdout + r.stderr).strip().splitlines()[-1][:160])\n'),
    "new": (
        '    # ORDER: apply_l5pwr2_contracts.py must be applied to these files first: every old text of it gone. A later round may restate\n'
        '    # its new texts in place (W8 restated L5-F09 a to d under L5-F14): that tree is applied, then restated, not unapplied, and\n'
        '    # this script\'s own state below reads each of its edits as it stands (record l5pwr, W14 of 6 October 2026).\n'
        '    import collections\n'
        '    pre = {k: open(p, encoding="utf-8").read() for k, p in paths.items()}\n'
        '    left = [i for i, tg, _w, old, _n in A.edits(collections.defaultdict(str)) if rx(old).search(pre[tg])]\n'
        '    if left:\n'
        '        refuse("ORDER: apply_l5pwr2_contracts.py is not applied to these files (its old text still in them: %s)" % ", ".join(left))\n'),
}


def _git(commit, rel):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, rel)], capture_output=True)
    if r.returncode != 0:
        raise Skip("commit %s is not in this repository" % commit)
    return r.stdout


def _copy(d, src):
    """The two contract files into `d`: from a commit, or (src None) the tree's bytes; returns the scripts' --yaml/--hwfw args."""
    y, h = os.path.join(d, "pcb_interfaces.yaml"), os.path.join(d, "HW-FW-CONTRACT.md")
    for f, rel in ((y, YAML_REL), (h, HWFW_REL)):
        open(f, "wb").write(_git(src, rel) if src else open(os.path.join(ROOT, rel), "rb").read())
    return ["--yaml", y, "--hwfw", h]


def _run(script, args):
    r = subprocess.run([sys.executable, "-B", script, "--check"] + args, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def _old_expectation(rc, out, _err):
    """test_l5pwr's assertion before W14 (its lines 341 and 392 at 27cd9cd2)."""
    return rc == 0 and "already applied" in out


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def t_the_old_expectations_hold_at_w8s_base_and_fail_at_w8s_commit_and_on_a_copy_of_the_tree():
    need(APPLY2, "record l5pwr's contract script")
    need(os.path.join(ROOT, ".git"), "a git checkout")
    shas = [_sha(os.path.join(ROOT, rel)) for rel in (YAML_REL, HWFW_REL)]
    d = tempfile.mkdtemp(prefix="w14-old-")
    try:
        for src, holds in ((W8_BASE, True), (W8_COMMIT, False), (None, False)):
            args = _copy(d, src)
            for script in (APPLY2, APPLY3):
                got = _run(script, args)
                assert _old_expectation(*got) == holds, (src, os.path.basename(script), got[0], got[1][-200:], got[2][-300:])
            if not holds:
                rc, out, err = _run(APPLY2, args)
                assert rc == 3 and out == "" and all("%s: old text 0 time(s), new text absent" % i in err
                                                     for i in ("L5-F09 a", "L5-F09 b", "L5-F09 c", "L5-F09 d")), (src, err[-400:])
                assert "L5-F10 a: old text 0 time(s), new text present; L5-F10 b: old text 0 time(s), new text present" in err, err[-400:]
                # the base's script (before PATCH_L5F11_ORDER, read at SET31_BASE): its ORDER check's false reason (history)
                rc, out, err = _call(_main_of(_git(SET31_BASE, APPLY3_REL).decode("utf-8"), "base"), args)
                assert rc == 3 and "ORDER: apply_l5pwr2_contracts.py is not applied" in err, (src, err[-300:])
                # the tree's script, the row applied (f0d0e54e): its own state, F11-09 named, no ORDER reason
                rc, out, err = _run(APPLY3, args)
                assert rc == 3 and out == "" and err == _restated() and "ORDER" not in err, (src, err[-300:])
    finally:
        shutil.rmtree(d)
    assert shas == [_sha(os.path.join(ROOT, rel)) for rel in (YAML_REL, HWFW_REL)], "a contract file of the tree changed"


def _main_of(src, tag):
    """A source of apply_l5f11_contracts.py executed in memory, compiled from the script's own path (so its HERE, REPO and the first
    script it loads are the tree's); no file is written."""
    ast.parse(src)
    ns = {"__file__": APPLY3, "__name__": "apply_l5f11_%s_by_w25" % tag}
    exec(compile(src, APPLY3, "exec"), ns)  # noqa: S102
    return ns["main"]


def _lines(src, text):
    i = src.index(text)
    a = src[:i].count("\n") + 1
    return a, a + text.count("\n") - 1


def _applied_sources():
    """(the tree's source, the base's source). History: at SET31_BASE the row's old text is the script's lines 187 to 191 once and its
    new text absent, and APPLIED_AT's bytes are the base's with the row applied verbatim. Applied: at this tree the new text is the
    script's lines 187 to 194 once and the old text is gone (W24, f0d0e54e; restated by W25)."""
    old, new = PATCH_L5F11_ORDER["old"], PATCH_L5F11_ORDER["new"]
    base = _git(SET31_BASE, APPLY3_REL).decode("utf-8")
    assert base.count(old) == 1 and _lines(base, old) == (187, 191) and new not in base, "history: the old text at the base"
    assert _git(APPLIED_AT, APPLY3_REL).decode("utf-8") == base.replace(old, new), "f0d0e54e did not apply the row verbatim"
    src = open(APPLY3, encoding="utf-8").read()
    assert src.count(new) == 1 and _lines(src, new) == (187, 194), "the row's new text is not the script's lines 187 to 194, once"
    assert src.count(old) == 0, "the row's old text still stands in the script"
    return src, base


def _restated():
    return "apply_l5f11_contracts: not in the state this script applies to: %s; refusing, nothing written\n" % "; ".join(
        "%s: old text 0 time(s), new text %s" % (i, "absent" if i == "F11-09" else "present") for i in ["F11-%02d" % n for n in range(1, 15)])


def _call(main, args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = main(["--check"] + args)
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue(), err.getvalue()


def t_the_proposed_order_patch_row_reads_the_order_and_names_the_restated_edit():
    need(APPLY3, "record l5pwr's second contract script")
    need(os.path.join(ROOT, ".git"), "a git checkout")
    before = _sha(APPLY3)
    tree_src, base_src = _applied_sources()
    main = _main_of(tree_src, "tree")       # the applied script (the row's new text in the tree's file)
    base_main = _main_of(base_src, "base")  # the script before the row (SET31_BASE), the history side
    restated = _restated()
    d = tempfile.mkdtemp(prefix="w14-patch-")
    try:
        for src, want in ((BASE2, "ORDER"), (BASE3, "CHECK OK, 14 edit(s)"), (W8_BASE, "already applied"), (W8_COMMIT, restated),
                          (None, restated)):
            args = _copy(d, src)
            rc, out, err = _call(main, args)
            if want == "ORDER":
                assert rc == 3 and err.startswith("apply_l5f11_contracts: ORDER: apply_l5pwr2_contracts.py is not applied to these files "
                                                  "(its old text still in them: L5-F10 a, L5-F10 b, L5-F09 a, L5-F09 b, L5-F09 c, "
                                                  "L5-F09 d)"), (src, err[-300:])
                rc0, _o, err0 = _call(base_main, args)
                assert rc0 == 3 and "ORDER: apply_l5pwr2_contracts.py is not applied" in err0, err0[-300:]
            elif want == restated:
                assert rc == 3 and out == "" and err == restated, (src, rc, out[-200:], err[-300:])
                # the base's script on the same files: refused too, for the false ORDER reason the row corrected
                rc0, _o, err0 = _call(base_main, args)
                assert rc0 == 3 and "ORDER: apply_l5pwr2_contracts.py is not applied" in err0, err0[-300:]
            else:
                assert rc == 0 and want in out and err == "", (src, rc, out[-200:], err[-300:])
                rc0, out0, _e = _call(base_main, args)
                assert rc0 == 0 and want in out0, "the row must not change the script's answer where the base's ORDER check is right"
    finally:
        shutil.rmtree(d)
    assert _sha(APPLY3) == before, "the script was written"


def _literal_assigns(tree):
    out = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            try:
                out[n.targets[0].id] = ast.literal_eval(n.value)
            except ValueError:
                pass
    return out


def _rows(tree, consts, nargs):
    """The literal arguments of every row(...) call (a name resolved to its module-level literal)."""
    rows = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "row":
            vals = []
            for a in n.args[:nargs]:
                vals.append(consts[a.id] if isinstance(a, ast.Name) else ast.literal_eval(a))
            rows.append(vals)
    return rows


def _flat(s):
    return " ".join(str(s).split())


def t_l5r2_would_refuse_on_w8s_text_for_no_reason_but_a_moved_digest():
    """Read by parsing (W10's unchecked item). l5r2_interfaces.py's compute() reads the contract files at: its pins (lines 367 to 372
    and 376, the sha256 printed at l5r2_interfaces.out lines 6, 7 and 26), hc5's field contract on every contract (lines 388 to 392:
    hc5's check reads REQUIRED, `ends` and `tbd` only), the keys each touched contract gained (lines 393 to 401), the no-loss proof of
    the eight contracts EIGHT (lines 402 to 409), each row's excerpt in its target and each figure in its cited sources, `ifaces` being
    pcb_interfaces.yaml (lines 412 to 426), and the tbd owners of the touched contracts (lines 427 to 437). W8's change is three keys of
    IF-EXT-DC, which is touched (TOUCHED) but none of the readings above looks at those keys' values. l5r3_panel.py reads
    HW-FW-CONTRACT.md for its rows' excerpts and its section 3.8 (lines 117 to 122 and 155)."""
    need(L5R2, "record l5r2's generator")
    need(os.path.join(ROOT, ".git"), "a git checkout")
    import yaml
    t2 = ast.parse(open(L5R2, encoding="utf-8").read())
    c2 = _literal_assigns(t2)
    hc5 = _literal_assigns(ast.parse(open(HC5, encoding="utf-8").read()))
    old = {k: _git(W8_BASE, rel).decode("utf-8") for k, rel in (("yaml", YAML_REL), ("hwfw", HWFW_REL))}
    new = {k: _git(W8_COMMIT, rel).decode("utf-8") for k, rel in (("yaml", YAML_REL), ("hwfw", HWFW_REL))}
    assert c2["TARGETS"] == {"yaml": YAML_REL, "hwfw": HWFW_REL} and c2["SOURCES"]["ifaces"] == YAML_REL
    assert [k for k, rel in c2["SOURCES"].items() if rel in (YAML_REL, HWFW_REL)] == ["ifaces"]
    # what W8 changed in the parsed yaml: three keys of IF-EXT-DC, nothing else
    y0, y1 = yaml.safe_load(old["yaml"]), yaml.safe_load(new["yaml"])
    c0, c1 = y0["board_to_board"].pop("contracts"), y1["board_to_board"].pop("contracts")
    assert y0 == y1 and list(c0) == list(c1)
    changed = {(cid, k) for cid in c1 for k in set(c0[cid]) | set(c1[cid]) if c0[cid].get(k) != c1[cid].get(k)}
    assert changed == W8_FIELDS, changed
    assert all(list(c0[cid]) == list(c1[cid]) for cid in c1), "a key was added, moved or removed"
    read_by_hc5 = set(hc5["REQUIRED"]) | {"ends", "tbd"}
    assert not {k for _c, k in changed} & read_by_hc5, "W8 changed a key hc5's field contract reads"
    assert not {c for c, _k in changed} & set(c2["EIGHT"]), "W8 changed a contract of l5r2's no-loss set"
    rows = _rows(t2, c2, 8)
    assert len(rows) == 48 and not [r[0] for r in rows if r[1] in {c for c, _k in changed}], "an l5r2 row targets IF-EXT-DC"
    flat_new = {k: _flat(v) for k, v in new.items()}
    assert not [r[0] for r in rows if _flat(r[4]) not in flat_new[r[3]]], "an l5r2 excerpt is not in W8's text"
    cites = [r for r in rows if "ifaces" in r[5]]
    assert cites and not [(r[0], f) for r in cites for f in r[7] if _flat(f) not in flat_new["yaml"]], "an ifaces figure is gone"
    # l5r3_panel.py: its HW-FW-CONTRACT.md excerpts and its section 3.8
    t3 = ast.parse(open(L5R3, encoding="utf-8").read())
    r3 = [r for r in _rows(t3, _literal_assigns(t3), 4) if r[2] == "hwfw"]
    assert r3 and not [r[0] for r in r3 if _flat(r[3]) not in flat_new["hwfw"]], "an l5r3 excerpt is not in W8's text"
    a, b = "### 3.8 Values adopted from the panel firmware", "## 4. What round 8 changes"

    def sec(t):
        i = t.find(a)
        j = t.find(b, i + 1)
        assert i >= 0 and j > i
        return t[i:j]
    assert sec(old["hwfw"]) == sec(new["hwfw"]), "W8 changed section 3.8"


def t_no_em_or_en_dash():
    t = open(os.path.abspath(__file__), encoding="utf-8").read()
    assert chr(0x2014) not in t and chr(0x2013) not in t
