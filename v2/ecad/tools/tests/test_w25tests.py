"""W25 (MESHSAT-1357, 6 October 2026): set 31's test restatements after the patch rows were applied, held as predicates.

What W25 restated on fnd/int31tests (base f47189b1, W24's tip; W23's fnd/int31cite 1b2d5123 merged at ce122dfa):
- test_w7rem.t_the_l4e9_rows_stand_where_they_say: P-01 to P-12 read APPLIED at this tree (W24, 467c2aaa) and PENDING at a6e3a066;
- test_w13l4e9.t_every_row_stands_where_it_says_and_no_group_is_half_applied: WP-01 to WP-22 APPLIED (W24, bad162ad) with the
  re-taken copies, PENDING at a6e3a066; WP-23 to WP-27 pending at both (the coordinator's decision: only with the next circuit change);
- test_w20oneliners.t_set31s_applied_rows_stand_at_this_tree_and_the_waiting_ones_do_not (new): W20-01 to W20-24, N1a, N3a and N3b
  applied, N2a to N2c waiting; the module's reads of c4492dd3 stay as the history;
- test_w14l5's two ORDER predicates: PATCH_L5F11_ORDER APPLIED (W24, f0d0e54e), the base's script at a6e3a066 as the history;
- W20's test rows W20-18 to W20-22 applied (test_l5pwr's docstring, test_l9t5's three rows, test_remeng's comment);
- the coordinator's seven citation keys after W23's re-cite (test_remeng's two AMENDMENT_CITES entries and item E's string, the
  N3a and N3b rows as candidate A; test_w3annex's four ANCHORS keys).

The predicates: every restated module is green here (test_l9t5 and test_l5pwr are NOT run whole: they regenerate records and fail
by design before the coordinator's regeneration; the one test_l9t5 test whose expectation changed reads no output and is run); per
patch file, the applied rows counted (each New text once at this tree and its Old text gone outside it, matched as text) and the
waiting rows counted (each Old text once, its New text absent); a reverted row is named; no em or en dash in this module or in the
restated modules. Predicates on test and record text: they establish no electrical or thermal property, close nothing and accept
nothing. Prototype framing: nothing in the kit is built, bought, powered or measured.
"""
import ast
import importlib.util
import os
import re
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

P7 = "v2/docs/records/l4e9/L4E9-4588-PATCH.md"
P13 = "v2/docs/records/l4e9/L4E9-W5-PATCH.md"
P20 = "v2/docs/records/int30/NEXT-SET-SMALL-ITEMS.patch.md"
W14 = "v2/ecad/tools/tests/test_w14l5.py"
RESTATED = ("test_w7rem", "test_w13l4e9", "test_w20oneliners", "test_w14l5", "test_remeng", "test_w3annex")
ONE_L9T5 = "t_p0_connected_the_change_list_carries_every_composed_draft"   # W20-19 to W20-21's test; it reads no output
EDITED = RESTATED + ("test_l9t5", "test_l5pwr")
DASHES = (chr(0x2013), chr(0x2014))
_T = {}


def _read(rel):
    if rel not in _T:
        _T[rel] = open(need(os.path.join(ROOT, rel), "a file a row names"), encoding="utf-8").read()
    return _T[rel]


def _rows(rel, prefix):
    """{id: {file, old, new}} of one patch file's rows (### <id>. ..., a File line, an Old and a New block)."""
    out = {}
    for m in re.finditer(r"^### (%s-\d+)\. .*?$(.*?)(?=^### |^## |\Z)" % prefix, _read(rel), re.S | re.M):
        b = m.group(2)
        out[m.group(1)] = dict(file=re.search(r"^- File: `([^`]+)`", b, re.M).group(1),
                               old=re.search(r"^- Old:\n\n```text\n(.*?)\n```\n", b, re.S | re.M).group(1),
                               new=re.search(r"^- New:\n\n```text\n(.*?)\n```\n", b, re.S | re.M).group(1))
    return out


def _needs():
    """W20's NEEDS THE COORDINATOR items: {id: {file, old, a, b}}."""
    out = {}
    for m in re.finditer(r"- \*\*(W20-N\d[a-z])\*\*, `([^`]+)` line \S+, Old:\n\n```text\n(.*?)\n```\n\n  Candidate A:\n\n```text\n(.*?)\n```"
                         r"\n\n  Candidate B:\n\n```text\n(.*?)\n```", _read(P20), re.S):
        out[m.group(1)] = dict(file=m.group(2), old=m.group(3), a=m.group(4), b=m.group(5))
    return out


def _applied(text, new, old):
    """New once and Old gone outside it (matched as text)."""
    return text.count(new) == 1 and old not in text.replace(new, "\0")


def _waiting(text, new, old):
    return text.count(old) == 1 and new not in text


def _count(rows, ids, pred):
    return sum(1 for i in ids if pred(_read(rows[i]["file"]), rows[i]["new"], rows[i]["old"]))


def _load(name):
    sp = importlib.util.spec_from_file_location("w25_" + name, os.path.join(HERE, name + ".py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def t_every_restated_module_is_green():
    failed, skipped, ran = [], [], 0
    calls = [(n, f) for n in RESTATED for f in sorted(dir(_load(n))) if f.startswith("t_")] + [("test_l9t5", ONE_L9T5)]
    mods = {}
    for n, f in calls:
        mods.setdefault(n, _load(n))
        try:
            getattr(mods[n], f)()
            ran += 1
        except Skip as e:
            skipped.append("%s.%s (%s)" % (n, f, e))
        except Exception as e:  # noqa: BLE001
            failed.append("%s.%s: %s" % (n, f, str(e)[:160]))
    assert not failed, failed
    if skipped:
        raise Skip("not green here, skipped: %s" % skipped)
    assert ran >= 55, ran


def t_l4e9_4588_patch_twelve_applied():
    rows = _rows(P7, "P")
    ids = ["P-%02d" % i for i in range(1, 13)]
    assert sorted(rows) == ids
    assert _count(rows, ids, _applied) == 12, [i for i in ids if not _applied(_read(rows[i]["file"]), rows[i]["new"], rows[i]["old"])]


def t_l4e9_w5_patch_twenty_two_applied_and_five_waiting():
    rows = _rows(P13, "WP")
    done, wait = ["WP-%02d" % i for i in range(1, 23)], ["WP-%02d" % i for i in range(23, 28)]
    assert sorted(rows) == done + wait
    assert _count(rows, done, _applied) == 22, [i for i in done if not _applied(_read(rows[i]["file"]), rows[i]["new"], rows[i]["old"])]
    assert _count(rows, wait, _waiting) == 5, [i for i in wait if not _waiting(_read(rows[i]["file"]), rows[i]["new"], rows[i]["old"])]


def t_next_set_small_items_twenty_seven_applied_and_three_waiting():
    rows = _rows(P20, "W20")
    ids = ["W20-%02d" % i for i in range(1, 25)]
    assert sorted(rows) == ids
    n = _count(rows, ids, _applied)
    ns = _needs()
    assert sorted(ns) == ["W20-N1a", "W20-N2a", "W20-N2b", "W20-N2c", "W20-N3a", "W20-N3b"], sorted(ns)
    n += _applied(_read(ns["W20-N1a"]["file"]), ns["W20-N1a"]["a"], ns["W20-N1a"]["old"])
    for k in ("W20-N3a", "W20-N3b"):   # candidate A carries a placeholder line: its pattern once, the Old text gone
        x = ns[k]
        pat = re.escape(x["a"].replace(" with the ledger re-cited", "")).replace(
            re.escape("<the end line the coordinator reads>"), r"\d+").replace(re.escape("<the start line the coordinator reads>"), r"\d+")
        t = _read(x["file"])
        n += len(re.findall(pat, t)) == 1 and x["old"] not in t
    assert n == 27, n
    w = sum(1 for k in ("W20-N2a", "W20-N2b", "W20-N2c") if _waiting(_read(ns[k]["file"]), ns[k]["b"], ns[k]["old"]))
    assert w == 3, w


def t_the_order_patch_row_applied():
    for node in ast.parse(_read(W14)).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "PATCH_L5F11_ORDER":
            d = ast.literal_eval(node.value)
            assert _applied(_read(d["file"]), d["new"], d["old"]), "PATCH_L5F11_ORDER is not applied at this tree"
            return
    raise AssertionError("no PATCH_L5F11_ORDER in test_w14l5")


def t_a_reverted_row_is_named_and_a_waiting_row_written_is_seen():
    r = _rows(P20, "W20")["W20-19"]
    t = _read(r["file"])
    assert _applied(t, r["new"], r["old"]) and not _applied(t.replace(r["new"], r["old"]), r["new"], r["old"])
    w = _rows(P13, "WP")["WP-23"]
    t = _read(w["file"])
    assert _waiting(t, w["new"], w["old"]) and not _waiting(t.replace(w["old"], w["new"]), w["new"], w["old"])


def t_no_em_or_en_dash():
    for n in EDITED + ("test_w25tests",):
        t = open(os.path.join(HERE, n + ".py"), encoding="utf-8").read()
        assert not any(d in t for d in DASHES), n
