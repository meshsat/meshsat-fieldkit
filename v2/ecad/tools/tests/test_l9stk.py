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
proposes the LAYER-STATUS row. The copper question (4 October 2026, the page's section 14): l9stk_copper.out is what
l9stk_copper.py prints from inputs pinned at their sha256; its widths and rises are decision 35's model re-solved here; the
faces' split is checked on a resistor ladder solved here; the page carries its figures and files its findings; the energy
chain draft refuses before the decisions, applies once on a copy, replaces record l8r2's texts to the same bytes and leaves
energy_chain.check's counts unchanged; boards A and E's decisions carry the derived widths. These are software predicates
on the record's text and arithmetic: they establish no property of any board, stack or price.
"""
import ast
import hashlib
import importlib.util
import json
import math
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


def _marked(decisions):
    """The entries whose TITLE ends with one of this record's marks (a text field may name another mark, as A's and E's name
    the open decision)."""
    return [x for x in decisions if re.search(r"\(L9STK (A|B|C|D|E|P|E5|CU)\)$", str(x.get("title", "")).strip())]


def t_the_apply_script_checks_by_default_appends_eight_and_refuses_a_second_run():
    ast.parse(open(APPLY, encoding="utf-8").read())
    A, D = _decisions()
    import yaml
    real = yaml.safe_load(open(REGISTER, encoding="utf-8").read())["decisions"]
    applied = _marked(real)
    tmp = tempfile.mkdtemp(prefix="l9stk-")
    try:
        copy = os.path.join(tmp, "pcb_decisions.yaml")
        shutil.copyfile(REGISTER, copy)
        before = open(copy, encoding="utf-8").read()
        r0 = subprocess.run([sys.executable, "-B", APPLY, "--registry", copy], capture_output=True, text=True)
        assert open(copy, encoding="utf-8").read() == before, "a run without --write wrote the register"
        r1 = subprocess.run([sys.executable, "-B", APPLY, "--registry", copy, "--write"], capture_output=True, text=True)
        if applied:
            assert len(applied) == 8, "the register carries %d of the eight marks" % len(applied)
            assert r1.returncode == 2 and "second run" in r1.stdout, "a run on an applied register was not refused"
            return
        assert r0.returncode == 0 and "CHECK ONLY" in r0.stdout, r0.stdout + r0.stderr
        assert r1.returncode == 0, r1.stdout + r1.stderr
        after = yaml.safe_load(open(copy, encoding="utf-8").read())["decisions"]
        assert after[:len(real)] == real, "an existing decision moved"
        new = after[len(real):]
        n0 = max(int(x["n"]) for x in real) + 1
        assert len(new) == 8 and [e["n"] for e in new] == list(range(n0, n0 + 8))
        for e, d in zip(new[:7], D):
            assert e["authority"] == "SESSION" and e["status"] == "ruled" and e["blocks"] == {}
            assert e["measurement"] == d["measurement"] and str(e["title"]).endswith(d["mark"])
            assert str(e.get("ruled_on")) == "2026-10-03"
        cu = new[7]
        assert cu["status"] == "open" and cu["authority"] == "OWNER" and str(cu["title"]).endswith("(L9STK CU)")
        assert cu["ask"] and cu["holds_nothing_today"] and cu["blocks"] == {}
        r2 = subprocess.run([sys.executable, "-B", APPLY, "--registry", copy, "--write"], capture_output=True, text=True)
        assert r2.returncode == 2 and "second run" in r2.stdout, "a second run was not refused"
        assert len(_marked(yaml.safe_load(open(copy, encoding="utf-8").read())["decisions"])) == 8
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


# ------------------------------------------------------------------------------------------------ the copper question
# (revised 4 October 2026 after the check COPPER: NOT CONFIRMED, the page's section 14): l9stk_copper.py's output, its
# arithmetic re-solved here from the ruled method (decision 35's track_current) with a band's faces and its adjacent return as
# one conductor, the split checked on a resistor ladder solved here, the coordination table's rows and dispositions, the
# drafts on copies.
COPPER = os.path.join(REC, "l9stk_copper.py")
COPPER_OUT = os.path.join(REC, "l9stk_copper.out")
CHAIN_DRAFT = os.path.join(REC, "apply_energy_chain_l9stk.py")
PLATING_DRAFT = os.path.join(REC, "apply_blade_plating_l9stk.py")
CHAIN = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_energy_chain.yaml")
SOURCES = os.path.join(ROOT, "v2", "vendor", "SOURCES.yaml")
L8R2_DRAFT = os.path.join(ROOT, "v2", "docs", "records", "l8r2", "apply_energy_chain_e1oz.py")


def _CU():
    if "CU" not in _C:
        need(COPPER, "the l9stk copper record")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext (poppler) reads the makers' sheets")
        m = _load(COPPER, "l9stk_copper_under_test")
        for rel in m.PINS.values():
            need(os.path.join(ROOT, rel), "a pinned input of the l9stk copper record")
        try:
            R = m.compute()
        except SystemExit as e:
            raise AssertionError("l9stk_copper.py refused (exit %s)" % e.code)
        _C.update(CU=m, CR=R, ctext=m.render(R))
    return _C["CU"]


def t_copper_output_reproduced_byte_for_byte():
    _CU()
    need(COPPER_OUT, "the committed copper output")
    assert _C["ctext"] == open(COPPER_OUT, encoding="utf-8").read(), "l9stk_copper.out is not what the script prints"


def t_copper_every_input_is_pinned_and_present():
    m = _CU()
    for key, rel in m.PINS.items():
        sha = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
        assert ("%s  sha256 %s" % (rel, sha[:16])) in _C["ctext"], "%s is not pinned at its current sha256" % rel


def t_copper_every_predicate_holds():
    _CU()
    P = _C["CR"]["pred"]
    assert len(P) >= 18, "the copper script states fewer predicates than the record relies on"
    bad = [k for k, v in P.items() if not v]
    assert not bad, "false: %s" % "; ".join(bad)
    for must in ("the candidate's two 12.26 mm faces as one conductor read 18.9 K at 25 A and 12.0 K at 20 A",
                 "two 1 oz faces as one conductor need 21.81 mm each at 25 A",
                 "board E's pack end at 1 oz with its return adjacent exceeds the strip; at 2 oz it fits",
                 "every coordination row carries a disposition, and every row over a printed rating a design correction or a gap"):
        assert must in P, "the predicate %r is gone" % must


def _rise(tc, amps, width, t_mm, internal=False):
    """The rise at which decision 35's model rates one conductor (width x t_mm) at amps, by its own bisection here."""
    f = 1.0 if internal else tc.EXTERNAL_FACTOR
    lo, hi = 1e-4, 300.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if tc.conservative(width * t_mm, mid)[0] * f < amps:
            lo = mid
        else:
            hi = mid
    return hi


def t_copper_the_stacked_faces_and_the_adjacent_return_on_the_ruled_method():
    """The checker's figures and the record's widths, re-solved here: two faces as one conductor of their combined section,
    a band and its return as one conductor of twice the width carrying twice the current (an even split)."""
    m = _CU()
    import track_current as tc
    R, I, W = _C["CR"], _C["CR"]["in"], _C["CR"]["w"]
    t1 = 0.035
    assert tc.width_for_current.__defaults__[1] == 10.0
    blade = I["blade_a"]
    # the candidate's 12.26 mm as one conductor: 0.858 mm2 at 25 A, 20 A, and 50 A from the +70 C line
    assert abs(2 * W["cand_even"] * t1 - 0.858) < 1e-3
    assert round(_rise(tc, 25.0, W["cand_even"], 2 * t1), 1) == 18.9
    assert round(_rise(tc, 20.0, W["cand_even"], 2 * t1), 1) == 12.0
    assert round(I["air_c"] + _rise(tc, 50.0, W["cand_even"], 2 * t1), 1) == 147.1
    # the widths: two faces alone, and the pair (each band half of the conductor carrying twice the current)
    assert abs(W["alone_1"] - tc.width_for_current(blade, oz=2.0)) < 1e-9 and round(W["alone_1"], 2) == 21.81
    assert abs(W["pair_1"] - tc.width_for_current(2 * blade, oz=2.0) / 2.0) < 1e-9
    assert abs(W["pair_2"] - tc.width_for_current(2 * blade, oz=4.0) / 2.0) < 1e-9
    k2 = 2 * (m.S_MAX ** 2 + (1 - m.S_MAX) ** 2)
    assert abs(W["pair_1k"] - tc.width_for_current(2 * blade * math.sqrt(k2), oz=2.0) / 2.0) < 1e-9
    # the decided pair is at 10 K at 25 A, re-solved as a conductor of twice the width and twice the face copper
    assert abs(_rise(tc, 2 * blade * math.sqrt(k2), 2 * W["pair_1k"], 2 * t1) - 10.0) < 1e-3
    assert abs(_rise(tc, 2 * blade * math.sqrt(k2), 2 * W["pair_2k"], 4 * t1) - 10.0) < 1e-3
    # every held row of the decided families is the ruled model's own
    for fk in ("D1", "D2", "H1"):
        f = R["fam"][fk]
        for x in f["rows"]:
            if x["dur"] is None and x["cls"] != "pulse" and x["st"] is not None:
                mine = _rise(tc, x["a"] * math.sqrt(2 * 2 * f["k"] ** 2), 2 * f["w"], 2 * t1 * f["oz"])
                assert abs(mine - x["st"]) < 1e-3, "%s %s: %.4f against %.4f" % (fk, x["lab"], mine, x["st"])
    # Onderdonk forward and back, from the worst inside air
    c = m.cmil(W["pair_1k"] * t1)
    for i_face, tt in ((40.0, 0.5), (100.0, 0.05)):
        dT = m.rise_adiabatic(i_face * i_face * tt, W["pair_1k"] * t1, I)
        back = c * math.sqrt(math.log10(1.0 + dT / (I["k234"] + I["t0"])) / (tt * I["k33"]))
        assert abs(back - i_face) < 1e-6 * i_face
    # the cross-sections
    assert abs(R["e_pack_end"]["1 oz"] - 2 * W["pair_1k"]) < 1e-9 and R["e_pack_end"]["1 oz"] > R["strip"]


def t_copper_the_limits_and_the_barrels():
    m = _CU()
    import via_current as vc
    import track_current as tc
    R, I = _C["CR"], _C["CR"]["in"]
    # the lowest printed limit of the parts each band joins, from the worst inside air the tree holds
    assert I["t0"] == max(I["air_c"], I["air_e3o"], I["air_e5"]) and I["t0"] > I["air_c"]
    assert R["limits"]["pack E"][0] == min(I["mini_sn_max_c"], I["holder_max_c"], I["xt60_max_c"])
    assert R["limits_pinned"]["pack E"] == min(I["mini_max_c"], I["holder_max_c"], I["xt60_max_c"])
    assert R["limits"]["shore E"][0] == min(I["mini_sn_max_c"], I["holder_max_c"], I["vh_max_c"])
    # the two annulus conventions, both counts
    t = vc.PLATING_UM / 1000.0
    d = m.drill()
    assert abs(R["barrel"]["outward"]["area"] - math.pi * (d + t) * t) < 1e-12
    assert abs(R["barrel"]["inward"]["area"] - math.pi * (d - t) * t) < 1e-12
    assert R["thermal_barrels"]["pack"]["outward"] == vc.barrels_for(I["blade_a"] / 2.0, d)
    amp_in = tc.conservative(math.pi * (d - t) * t, 10.0)[0]
    assert R["thermal_barrels"]["pack"]["inward"] == int(math.ceil(I["blade_a"] / 2.0 / amp_in - 1e-12))
    # the dock contacts' acceptance: no pin over its rating at the blade's current
    r = R["pin_ratio_need"]
    assert abs(I["blade_a"] / (1 + (I["pins"] - 1) * r) - I["pin_a"]) < 1e-9
    # the pair's 150 C current from E11-29's target
    i150 = 2 * math.sqrt((I["pair_limit"] - I["air_c"]) / (I["pair_rth"] * I["pair_mohm_each"] / 1000.0))
    assert abs(i150 - R["pair_i150"]["70"]) < 1e-9 and round(i150, 1) == 21.4


def _ladder(n, rb, rv_end, rv_mid=None):
    """Two faces of n series segments tied at node 0 (through-hole); the sink on face F at the far end; face B joins F through
    rv_end there and through rv_mid at every inner node when given. Nodal analysis solved here; returns face F's current in its
    last segment, for 1 A in."""
    r = rb / n
    N = 2 * n + 1
    G = [[0.0] * N for _ in range(N)]

    def link(a, b, res):
        g = 1.0 / res
        G[a][a] += g; G[b][b] += g; G[a][b] -= g; G[b][a] -= g
    F = lambda k: k
    B = lambda k: n + k
    link(0, F(1), r)
    link(0, B(1), r)
    for k in range(1, n):
        link(F(k), F(k + 1), r)
        link(B(k), B(k + 1), r)
        if rv_mid:
            link(F(k), B(k), rv_mid)
    link(B(n), F(n), rv_end)
    keep = [i for i in range(N) if i != F(n)]
    A = [[G[i][j] for j in keep] for i in keep]
    bvec = [1.0 if i == 0 else 0.0 for i in keep]
    m = len(keep)
    for c in range(m):
        piv = max(range(c, m), key=lambda x: abs(A[x][c]))
        A[c], A[piv] = A[piv], A[c]; bvec[c], bvec[piv] = bvec[piv], bvec[c]
        for x in range(c + 1, m):
            f = A[x][c] / A[c][c]
            for y in range(c, m):
                A[x][y] -= f * A[c][y]
            bvec[x] -= f * bvec[c]
    v = [0.0] * m
    for c in range(m - 1, -1, -1):
        v[c] = (bvec[c] - sum(A[c][y] * v[y] for y in range(c + 1, m))) / A[c][c]
    V = {keep[i]: v[i] for i in range(m)}
    V[F(n)] = 0.0
    return (V[F(n - 1)] - V[F(n)]) / r


def t_copper_the_split_on_a_solved_ladder():
    m = _CU()
    W = _C["CR"]["w"]
    h = _C["CR"]["h"][1]
    rb = m.r_band(10.0, W["pair_1k"], 1.0)
    rv = m.r_barrel(h) / 15
    want = m.share_one_end(10.0, W["pair_1k"], 1.0, 15, h)
    got = _ladder(20, rb, rv)
    assert abs(got - want) < 1e-9, "the one-end share %.6f against the ladder's %.6f" % (want, got)
    assert _ladder(20, rb, rv, rv_mid=m.r_barrel(h)) > want + 0.01, "stitching along the band did not raise the part's face share"
    for name, w, hh, oz, rows in _C["CR"]["transfer"]:
        for L, n1, n2 in rows:
            assert m.share_one_end(L, w, oz, n1, hh) <= m.S_MAX + 1e-12
            assert m.share_both_ends(L, w, oz, n2, hh) <= m.S_MAX + 1e-12
            if n1 > 1:
                assert m.share_one_end(L, w, oz, n1 - 1, hh) > m.S_MAX, "%s at %g mm: one barrel fewer still holds" % (name, L)


def t_copper_the_coordination_table_has_the_owners_rows():
    _CU()
    R, I = _C["CR"], _C["CR"]["in"]
    C = R["coord"]
    cases = [r["case"] for r in C]
    for must in ("10 A continuous", "18 A for 60 s", "the 25 A case, the gauge working", "the 25 A case, the gauge failed",
                 "sustained overloads", "board P's FETs failed short, blade 135 to 200", "board P's FETs failed short, blade over 600",
                 "the shore input, Q7 shorted"):
        assert any(c.startswith(must) for c in cases), "no row %r" % must
    names = " ".join(n for r in C for n, _t, _f in r["comps"])
    for comp in ("copper", "barrel field", "R17", "R19", "XT60", "dock contacts", "Q39/Q40", "3568 holder"):
        assert comp in names, "no row reads %s" % comp
    for r in C:
        assert r["device"] and r["clearing"] and r["disp"], r["case"]
        assert all(d[:3] in ("(a)", "(b)", "(c)") for d in r["disp"]), r["case"]
        if r["dur"] is None and not r["case"].startswith(("10 A", "the 25 A case, the gauge working")):
            assert "none" in r["clearing"], "%s claims a clearing time no row prints" % r["case"]
    gf = [r for r in C if r["case"].startswith("the 25 A case, the gauge failed")][0]
    assert gf["limit_comp"].startswith("Q39/Q40") and gf["limit_frac"] > 1.0
    assert any("W4DP-F2" in d for d in gf["disp"])
    # a row over a printed rating never rests on a coupon alone
    for r in C:
        if r["limit_frac"] == r["limit_frac"] and r["limit_frac"] > 1.0:
            assert any(d.startswith("(b)") for d in r["disp"]), "%s is over a rating with no design correction" % r["case"]


def t_copper_the_page_carries_the_outputs_figures():
    _CU()
    R, W, I = _C["CR"], _C["CR"]["w"], _C["CR"]["in"]
    need(PAGE, "the page")
    page = open(PAGE, encoding="utf-8").read()
    sec = page[page.index("## 14. The pack path's copper on its basis"):]
    fam = {(fk, x["lab"]): x for fk, f in R["fam"].items() for x in f["rows"]}
    want = ["%.2f" % W[k] for k in ("pair_1", "pair_1k", "pair_2", "pair_2k", "alone_1", "sh_pair_1", "sh_pair_1k", "sh_pair_2k", "vin_pair_1k")]
    want += ["%.2f" % x for _l, _a, w1, w2, w3 in R["ask"] for x in (w1, w2, w3)]
    want += ["%.2f mm" % R["e_pack_end"]["1 oz"], "%.2f mm" % R["e_pack_end"]["2 oz"], "%.2f mm" % R["e_shore"]["1 oz"],
             "%.2f C" % fam[("D1", "gauge failed: blade 135 to 200 %, at most 600 s")]["T"],
             "%.2f C" % fam[("D1", "gauge failed: blade 200 to 350 %, at most 5 s")]["T"],
             "%.2f A" % R["r17_limit_a"], "%.2f A" % R["r19_limit_a"], "%.2f A held" % R["pair_i150"]["70"],
             "%.2f A from %.2f C" % (R["pair_i150"]["t0"], I["t0"]), "%.3f of the highest" % R["pin_ratio_need"],
             "0297025.%s" % I["mini_ag_order"], "0297025.%s" % I["mini_sn_order"], "%g C" % I["xt60_max_c"],
             "%d (through the blade's 600 s point)" % R["field_pack_600"], "(L9STK CU)", "COPPER: NOT CONFIRMED", "W4DP-F2",
             "{:,}".format(int(round(R["i2t_allow_pack"]))) + " A2s", "{:,}".format(int(round(R["i2t_allow_shore"]))) + " A2s",
             "%.4f" % (R["ks"] ** 2), "%.2f C" % I["t0"]]
    for s in want:
        assert s in sec, "section 14 does not carry %r" % s
    for f in ("L9C-F%d" % k for k in range(1, 16)):
        assert f in sec, "section 14 does not file %s" % f


def _reg_with_decisions(tmp):
    reg = os.path.join(tmp, "pcb_decisions.yaml")
    shutil.copyfile(REGISTER, reg)
    import yaml
    if not _marked(yaml.safe_load(open(reg, encoding="utf-8"))["decisions"]):
        r = subprocess.run([sys.executable, "-B", APPLY, "--registry", reg, "--write"], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
    return reg


def t_the_energy_chain_draft_follows_the_decisions_and_replaces_l8r2s():
    m = _CU()
    _A()
    need(CHAIN_DRAFT, "the energy chain draft")
    ast.parse(open(CHAIN_DRAFT, encoding="utf-8").read())
    W = _C["CR"]["w"]
    import track_current as tc
    tmp = tempfile.mkdtemp(prefix="l9stk-chain-")
    try:
        import yaml
        bare = os.path.join(tmp, "bare.yaml")
        shutil.copyfile(REGISTER, bare)
        if not _marked(yaml.safe_load(open(bare, encoding="utf-8"))["decisions"]):
            c0 = os.path.join(tmp, "c0.yaml")
            shutil.copyfile(CHAIN, c0)
            r0 = subprocess.run([sys.executable, "-B", CHAIN_DRAFT, "--chain", c0, "--registry", bare], capture_output=True, text=True)
            assert r0.returncode == 3 and "not integrated" in r0.stderr, "the draft ran before the decisions"
        reg = _reg_with_decisions(tmp)
        c1 = os.path.join(tmp, "c1.yaml")
        shutil.copyfile(CHAIN, c1)
        r1 = subprocess.run([sys.executable, "-B", CHAIN_DRAFT, "--chain", c1, "--registry", reg, "--write"], capture_output=True, text=True)
        if "ALREADY CORRECTED" not in r1.stdout:
            assert r1.returncode == 0 and "WRITTEN" in r1.stdout, r1.stdout + r1.stderr
        r2 = subprocess.run([sys.executable, "-B", CHAIN_DRAFT, "--chain", c1, "--registry", reg, "--write"], capture_output=True, text=True)
        assert r2.returncode == 0 and "ALREADY CORRECTED" in r2.stdout, "a second run was not a no-op"
        st = {s["id"]: s for s in yaml.safe_load(open(c1, encoding="utf-8"))["stages"]}
        sh2 = tc.width_for_current(2 * 20.0, oz=4.0) / 2.0
        for sid, ws in (("DOCK_ENTRY", (W["pair_1"], W["pair_1k"], W["pair_2"], W["pair_2k"])),
                        ("BOARD_A_NODE", (W["pair_1"], W["pair_1k"], W["pair_2"], W["pair_2k"])),
                        ("SHORE_INPUT", (W["sh_pair_1"], W["sh_pair_1k"], sh2, W["sh_pair_2k"]))):
            for w in ws:
                assert "%.2f mm" % w in st[sid]["conductor"]["what"] or ("%.2f" % w) in st[sid]["conductor"]["what"], \
                    "%s does not carry %.2f" % (sid, w)
            assert "(L9STK CU)" in st[sid]["conductor"]["what"]
        for sid, s in st.items():
            pr = s.get("protection") or {}
            if sid in ("PACK_CELLS", "PACK_LEAD", "DOCK_ENTRY", "DOCK_BLOCK", "BOARD_A_NODE", "BOARD_A_CONVERTERS"):
                assert "287-atof" not in str(pr.get("basis")) and "littelfuse-297" in str(pr.get("basis")), sid
                assert float(pr.get("i2t_a2s")) == 625.0, sid
        orig = {s["id"]: s for s in yaml.safe_load(open(CHAIN, encoding="utf-8"))["stages"]}
        for sid in orig:
            if sid not in ("DOCK_ENTRY", "BOARD_A_NODE", "SHORE_INPUT", "PACK_CELLS", "PACK_LEAD", "DOCK_BLOCK", "BOARD_A_CONVERTERS"):
                assert st[sid] == orig[sid], "%s moved" % sid
            assert st[sid].get("conductor", {}).get("rating_a") == orig[sid].get("conductor", {}).get("rating_a")
            assert (st[sid].get("protection") or {}).get("rating_a") == (orig[sid].get("protection") or {}).get("rating_a")
        if os.path.isfile(L8R2_DRAFT):
            c2 = os.path.join(tmp, "c2.yaml")
            shutil.copyfile(CHAIN, c2)
            subprocess.run([sys.executable, "-B", L8R2_DRAFT, "--chain", c2, "--registry", reg, "--write"], capture_output=True, text=True)
            r3 = subprocess.run([sys.executable, "-B", CHAIN_DRAFT, "--chain", c2, "--registry", reg, "--write"], capture_output=True, text=True)
            assert r3.returncode == 0, r3.stdout + r3.stderr
            assert open(c1, encoding="utf-8").read() == open(c2, encoding="utf-8").read()
        import energy_chain
        a, b = energy_chain.check(), energy_chain.check(c1)
        for k in ("stages", "checked", "fails", "stage_fails", "derate_fails"):
            assert a[k] == b[k], "energy_chain.check's %s moved" % k
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_the_plating_draft_pins_the_silver_blade_once():
    m = _CU()
    I = _C["CR"]["in"]
    need(PLATING_DRAFT, "the plating draft")
    tmp = tempfile.mkdtemp(prefix="l9stk-plating-")
    try:
        import yaml
        src = os.path.join(tmp, "SOURCES.yaml")
        shutil.copyfile(SOURCES, src)
        before = open(src, encoding="utf-8").read()
        r0 = subprocess.run([sys.executable, "-B", PLATING_DRAFT, "--sources", src], capture_output=True, text=True)
        assert open(src, encoding="utf-8").read() == before, "a run without --write wrote the file"
        if I["blade_pinned"]:
            assert "ALREADY PINNED" in r0.stdout
            return
        r1 = subprocess.run([sys.executable, "-B", PLATING_DRAFT, "--sources", src, "--write"], capture_output=True, text=True)
        assert r1.returncode == 0 and "WRITTEN" in r1.stdout, r1.stdout + r1.stderr
        r2 = subprocess.run([sys.executable, "-B", PLATING_DRAFT, "--sources", src, "--write"], capture_output=True, text=True)
        assert r2.returncode == 0 and "ALREADY PINNED" in r2.stdout
        a = yaml.safe_load(before)["parts"]
        b = yaml.safe_load(open(src, encoding="utf-8").read())["parts"]
        for x, y in zip(a, b):
            if x.get("id") == "pack-blade-fuse-holder":
                assert ("0297025." + I["mini_ag_order"]) in y["fitted_mpn"] and y["fitted_mpn"] != x["fitted_mpn"]
                x = dict(x, fitted_mpn=y["fitted_mpn"])
            assert x == y, "entry %s moved" % x.get("id")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_boards_a_and_e_leave_the_copper_weight_to_the_owner():
    _CU()
    A, D = _decisions()
    W = _C["CR"]["w"]
    by = {d["board"]: d for d in D}
    for b in ("a", "e"):
        d = by[b]
        assert "1 oz outer" in d["title"] and "open decision" in d["title"], "board %s's title" % b
        assert "(L9STK CU)" in d["outcome"] and "(L9STK CU)" in d["authority_why"]
        for k in ("pair_1", "pair_1k", "pair_2", "pair_2k"):
            assert "%.2f" % W[k] in d["outcome"], "board %s's outcome does not carry %.2f mm" % (b, W[k])
        assert "l9stk_copper.out" in d["measurement"] and "l9stk_copper.py" in d["reversed_by"]
        for old in ("6.72 mm wide on each", "12.26 mm a face", "14.60 mm a face"):
            assert old not in d["outcome"], "board %s still lays %s" % (b, old)
    assert "%.2f" % W["sh_pair_1k"] in by["e"]["outcome"] and "%.2f" % W["vin_pair_1k"] in by["e"]["outcome"]
    assert A.OPEN["mark"] == "(L9STK CU)" and "(3)" in A.OPEN["recommendation"]


def t_the_readme_names_the_copper_files():
    need(README, "the README")
    t = open(README, encoding="utf-8").read()
    for f in ("l9stk_copper.py", "l9stk_copper.out", "apply_energy_chain_l9stk.py", "apply_blade_plating_l9stk.py", "(L9STK CU)"):
        assert f in t, "the README does not name %s" % f
