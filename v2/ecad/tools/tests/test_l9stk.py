"""Layer 9 item 9.12, record l9stk (MESHSAT-1357, 3 October 2026; v2/docs/records/l9stk/): one stackup decision per board,
held as predicates on what l9stk_stackups.py computes and on the decisions apply_decisions_l9stk.py would write.

The predicates: the committed .out is what the script prints and every pinned input is present at the sha256 the output
names; every predicate the script states holds (the outlines and the fabricator's size classes, the pack path's widths, the
bounds on board E's cross-section and on the inner planes, the 2 oz floors, the eight-layer pair geometry); there is one
decision per board, A, B, C, D, E, P and E5, each naming a measurement, a derived bound or the words NO MEASUREMENT HELD,
each on the stack the script computes for its board, each the session's with its way back naming a script; the apply
script parses, appends seven entries to a temporary copy of the register with nothing else moved, and refuses a second run;
the price readings are dated excerpts with their URLs, never a vendor's page; the page carries the output's figures and
every board's price as NOT READ where it was not read; the record's files carry no long dash and no claim word; the README
proposes the LAYER-STATUS row. These are software predicates on the record's text and arithmetic: they establish no
property of any board, stack or price.
"""
import ast
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l9stk")
SCRIPT = os.path.join(REC, "l9stk_stackups.py")
OUT = os.path.join(REC, "l9stk_stackups.out")
APPLY = os.path.join(REC, "apply_decisions_l9stk.py")
PAGE = os.path.join(REC, "L9-STACKUPS.md")
README = os.path.join(REC, "README.md")
PRICES = os.path.join(REC, "inputs", "price-readings-2026-10-03.json")
REGISTER = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_decisions.yaml")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}
BOARDS = ["a", "b", "c", "d", "e", "p", "e5"]
LABELS = ("MEASURED", "DERIVED BOUND", "NO MEASUREMENT HELD")
DASHES = (chr(0x2013), chr(0x2014))   # the en and em dash, written by code point so this file carries neither


def _load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _M():
    if "M" not in _C:
        need(SCRIPT, "the l9stk record")
        m = _load(SCRIPT, "l9stk_stackups_under_test")
        for rel in m.PINS.values():
            need(os.path.join(ROOT, rel), "a pinned input of the l9stk record")
        try:
            R = m.compute()
        except SystemExit as e:
            raise AssertionError("l9stk_stackups.py refused (exit %s)" % e.code)
        _C.update(M=m, R=R, text=m.render(R))
    return _C["M"]


def _A():
    if "A" not in _C:
        need(APPLY, "the l9stk apply script")
        if shutil.which("git") is None or subprocess.run(["git", "-C", REC, "rev-parse"], capture_output=True).returncode:
            raise Skip("the apply script locates the register through git")
        try:
            import yaml  # noqa: F401
        except ImportError:
            raise Skip("PyYAML is needed")
        _C["A"] = _load(APPLY, "apply_decisions_l9stk_under_test")
    return _C["A"]


def t_output_reproduced_byte_for_byte():
    _M()
    need(OUT, "the committed output")
    assert _C["text"] == open(OUT, encoding="utf-8").read(), "l9stk_stackups.out is not what the script prints"


def t_every_input_is_pinned_and_present():
    m = _M()
    for key, rel in m.PINS.items():
        p = os.path.join(ROOT, rel)
        sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
        assert ("%s  sha256 %s" % (rel, sha[:16])) in _C["text"], "%s is not pinned at its current sha256" % rel


def t_every_predicate_holds():
    _M()
    P = _C["R"]["pred"]
    assert len(P) >= 15, "the script states fewer predicates than the record relies on"
    bad = [k for k, v in P.items() if not v]
    assert not bad, "false: %s" % "; ".join(bad)
    for must in ("the pack path needs 23.91 mm on one 1 oz face and 11.95 mm on one 2 oz face",
                 "board E's listed conductors side by side at 1 oz on one face exceed the strip",
                 "on eight layers one width per class meets its target within 2 ohm on outer and inner layers",
                 "no price reading prints a figure at any board's outline"):
        assert must in P, "the predicate %r is gone" % must


def t_the_outlines_are_the_board_files():
    _M()
    O = _C["R"]["outline"]
    assert sorted(O) == sorted(BOARDS)
    want = {"a": (240.0, 160.0), "b": (330.0, 200.0), "c": (344.0, 228.0), "d": (100.0, 80.0), "e": (267.0, 68.0),
            "p": (70.0, 44.0), "e5": (43.0, 26.0)}
    for b, wh in want.items():
        assert (O[b]["w"], O[b]["h"]) == wh, "board %s's outline reads %s x %s" % (b, O[b]["w"], O[b]["h"])
        assert abs(O[b]["order_m2"] - wh[0] * wh[1] * 5 / 1e6) < 1e-4, "the order area is not five boards"


def _decisions():
    A = _A()
    return A, A.DECISIONS


def t_one_decision_per_board_each_names_a_measurement():
    A, D = _decisions()
    assert [d["board"] for d in D] == BOARDS, "not one decision per board in the order A, B, C, D, E, P, E5"
    for d in D:
        txt = d["measurement"]
        assert any(l in txt for l in LABELS), "board %s names no measurement and does not say none is held" % d["board"]
        assert any(l in d["measurement_kind"] for l in LABELS)
        for l in LABELS:
            if l in d["measurement_kind"]:
                assert l in txt, "board %s's kind says %s and its text does not" % (d["board"], l)
    held = {d["board"]: d["measurement"] for d in D}
    for b in ("b", "d", "e5"):    # no route of the alternative (B at eight, D at two) and nothing to route (E5)
        assert "NO MEASUREMENT HELD" in held[b], "board %s must say what is not held" % b


def t_each_decision_is_the_sessions_on_the_computed_stack():
    m = _M()
    A, D = _decisions()
    for d in D:
        b = d["board"]
        row = m.STACK[b][0]
        assert row.upper() in (d["title"] + " " + d["outcome"]).upper(), "board %s's decision does not name %s" % (b, row)
        assert ".py" in d["reversed_by"] and len(d["reversed_by"]) > 60
        assert len(d["authority_why"]) > 200 and "26 September 2026" in d["authority_why"]
        assert d["mark"] == "(L9STK %s)" % b.upper()
    owner = {"c": "decision 27", "p": "decision 28", "e5": "ruling 7", "b": "decision 43"}
    for d in D:
        if d["board"] in owner:
            assert owner[d["board"]] in d["authority_why"] or owner[d["board"]] in d["title"], \
                "board %s's decision does not name the owner's ruling it builds on" % d["board"]


def t_the_apply_script_parses_appends_seven_and_refuses_a_second_run():
    ast.parse(open(APPLY, encoding="utf-8").read())
    A, D = _decisions()
    import yaml
    real = yaml.safe_load(open(REGISTER, encoding="utf-8").read())["decisions"]
    applied = [x for x in real if "(L9STK " in str(x.get("title", ""))]
    tmp = tempfile.mkdtemp(prefix="l9stk-")
    try:
        copy = os.path.join(tmp, "pcb_decisions.yaml")
        shutil.copyfile(REGISTER, copy)
        r1 = subprocess.run([sys.executable, "-B", APPLY, "--registry", copy], capture_output=True, text=True)
        if applied:
            assert len(applied) == 7, "the register carries %d of the seven marks" % len(applied)
            assert r1.returncode == 2 and "second run" in r1.stdout, "a run on an applied register was not refused"
            return
        assert r1.returncode == 0, r1.stdout + r1.stderr
        after = yaml.safe_load(open(copy, encoding="utf-8").read())["decisions"]
        assert after[:len(real)] == real, "an existing decision moved"
        new = after[len(real):]
        assert len(new) == 7 and [e["n"] for e in new] == list(range(max(int(x["n"]) for x in real) + 1,
                                                                     max(int(x["n"]) for x in real) + 8))
        for e, d in zip(new, D):
            assert e["authority"] == "SESSION" and e["status"] == "ruled" and e["blocks"] == {}
            assert e["measurement"] == d["measurement"] and d["mark"] in e["title"]
            assert str(e.get("ruled_on")) == "2026-10-03"
        r2 = subprocess.run([sys.executable, "-B", APPLY, "--registry", copy], capture_output=True, text=True)
        assert r2.returncode == 2 and "second run" in r2.stdout, "a second run was not refused"
        assert open(copy, encoding="utf-8").read().count("(L9STK ") == 7
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_the_price_readings_are_dated_excerpts():
    need(PRICES, "the price readings")
    P = json.load(open(PRICES, encoding="utf-8"))
    assert P["read_on"] == "2026-10-03" and P["not_read"]
    ids = set()
    for r in P["readings"]:
        assert r["url"].startswith("https://") and ("jlcpcb.com" in r["url"] or "nextpcb.com" in r["url"])
        assert r["read_local"].startswith("2026-10-03 ") and re.match(r"[0-9a-f]{16}$", r["page_sha256_16"])
        assert r["excerpts"] and all(10 < len(x) < 700 for x in r["excerpts"]), "%s is not an excerpt" % r["id"]
        assert r["figures"], "%s carries no figure" % r["id"]
        ids.add(r["id"])
    assert {"JLC-1", "JLC-3", "JLC-5", "JLC-6", "JLC-7", "NXP-1"} <= ids
    raw = open(PRICES, encoding="utf-8").read()
    assert not any(c in raw for c in DASHES)
    assert len(raw) < 20000, "the readings file is too large to be excerpts"


def t_the_page_carries_the_outputs_figures_and_the_unread_prices():
    _M()
    R = _C["R"]
    need(PAGE, "the page")
    page = open(PAGE, encoding="utf-8").read()
    P = R["p_planes"]
    lo, hi = P["wmin"]["0.5 oz"]
    cs = R["e_cross"]["sum"]
    imp = {(what.split(",")[0], t): (w, z) for what, t, sec, w, s, z in R["imp"]["b"] if s}
    for s in ("23.91", "6.72", "11.95", "3.36", "195.80", "345", "416", "93 opens", "%.2f to %.2f mm" % (lo, hi),
              "%.2f mm on one 1 oz face" % cs["1 oz"][0], "%.2f mm on each of two faces" % cs["1 oz"][1],
              "0.148 / 0.127", "0.112 / 0.127", "0.332 mm", "0.155 mm", "0.181 mm", "0.130 mm at a 0.127 mm gap",
              "JLC06161H-3313", "JLC08161H-2116", "JLC04161H-7628", "JLC04162H-7628", "2L-2oz", "0.16 mm", "784.32"):
        assert s in page, "the page does not carry %r" % s
    assert page.count("**NOT READ**") >= 7, "every board's price at its outline must read NOT READ"
    for b in ("A", "B", "C", "D", "E", "P", "E5"):
        assert re.search(r"^\| %s \| [^\n]*\*\*NOT READ\*\* \|$" % b, page, re.M), "board %s's price row" % b


def t_the_record_carries_no_long_dash_and_no_claim_word():
    import claims_check
    for fn in sorted(os.listdir(REC)) + ["inputs/" + x for x in sorted(os.listdir(os.path.join(REC, "inputs")))]:
        p = os.path.join(REC, fn)
        if os.path.isdir(p):
            continue
        t = open(p, encoding="utf-8").read()
        assert not any(c in t for c in DASHES), "%s carries a long dash" % fn
        hit = claims_check.CLAIM.search(t)
        assert not hit, "%s carries the claim word %r" % (fn, hit.group(0) if hit else "")
    t = open(os.path.abspath(__file__), encoding="utf-8").read()
    assert not any(c in t for c in DASHES)


def t_the_readme_proposes_the_layer_status_row():
    need(README, "the README")
    t = open(README, encoding="utf-8").read()
    assert re.search(r"^\| 9\.12 \| stackup decided per board with measurement and cost \|", t, re.M), \
        "the README does not propose the 9.12 row"
    for f in ("L9-STACKUPS.md", "l9stk_stackups.py", "l9stk_stackups.out", "apply_decisions_l9stk.py",
              "inputs/price-readings-2026-10-03.json"):
        assert f in t, "the README does not name %s" % f
