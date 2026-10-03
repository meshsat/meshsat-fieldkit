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


# ------------------------------------------------------------------------------------------------ the copper question
# (4 October 2026, the page's section 14): l9stk_copper.py's output, its arithmetic recomputed from the ruled method
# (decision 35's track_current), the split checked on a resistor ladder solved here, the energy chain draft on copies.
COPPER = os.path.join(REC, "l9stk_copper.py")
COPPER_OUT = os.path.join(REC, "l9stk_copper.out")
CHAIN_DRAFT = os.path.join(REC, "apply_energy_chain_l9stk.py")
CHAIN = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_energy_chain.yaml")
L8R2_DRAFT = os.path.join(ROOT, "v2", "docs", "records", "l8r2", "apply_energy_chain_e1oz.py")


def _CU():
    if "CU" not in _C:
        need(COPPER, "the l9stk copper record")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext (poppler) reads the blade's time-current table")
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
    assert len(P) >= 20, "the copper script states fewer predicates than the record relies on"
    bad = [k for k, v in P.items() if not v]
    assert not bad, "false: %s" % "; ".join(bad)
    for must in ("6.72 mm a face is over 10 K at the blade's rating",
                 "12.26 mm a face at an even split is at 10 K at the blade's rating",
                 "on every pack family the backstop's 5 s interval and faster are over the printed maximum by the tree's bounds",
                 "the copper is not the fuse: the 600 % row's bound on B1 and B2 is under the governing face's fusing I2t"):
        assert must in P, "the predicate %r is gone" % must


def _ruled_rise(tc, amps_face, width, t_mm):
    """The rise at which decision 35's model rates an outer conductor at amps_face, solved here by its own bisection."""
    lo, hi = 1e-4, 200.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if tc.conservative(width * t_mm, mid)[0] * tc.EXTERNAL_FACTOR < amps_face:
            lo = mid
        else:
            hi = mid
    return hi


def t_copper_arithmetic_against_the_ruled_method():
    m = _CU()
    import track_current as tc
    R, I, W = _C["CR"], _C["CR"]["in"], _C["CR"]["w"]
    t1 = 0.035
    blade, wst, shore = I["blade_a"], I["shore_withstand_a"], I["shore_fuse_a"]
    s = m.S_MAX
    # the widths are track_current.width_for_current at its default rise, and that default is decision 35's 10 K
    assert tc.width_for_current.__defaults__[1] == 10.0
    for key, amps in (("coord_even", blade / 2), ("coord_smax", blade * s), ("svc_even", I["kd_a"] / 2), ("sh20_even", wst / 2),
                      ("sh20_smax", wst * s), ("sh10_smax", shore * s), ("vin_smax", I["vin_raw"] * s)):
        a = W[key] * t1
        assert abs(tc.conservative(a, 10.0)[0] * tc.EXTERNAL_FACTOR - amps) < 1e-6, "%s does not carry %.3f A at 10 K" % (key, amps)
    # each rise in the families is the ruled model's own: re-solved here for the held rows
    for fk, fam in R["fam"].items():
        for lab, a, dur, cls, i2t, st, ad, r, src in fam["rows"]:
            if dur is None and cls != "pulse" and st is not None:
                face = a * (fam["s"] if fam["faces"] == 2 else 1.0)
                mine = _ruled_rise(tc, face, fam["w"], t1 * fam["oz"])
                assert abs(mine - st) < 1e-3, "%s %s: %.4f K against the record's %.4f K" % (fk, lab, mine, st)
    # the page's headline readings
    rows = {(fk, r[0]): r for fk, f in R["fam"].items() for r in f["rows"]}
    assert round(rows[("A1", "held under the gauge's OCD1")][7], 2) == 12.39
    assert round(rows[("A1", "the blade's rating (the chain's check 3)")][7], 2) == 19.52
    assert round(I["air_c"] + rows[("B1", "blade 135 to 200 %, at most 600 s")][7], 1) == 110.9
    # Onderdonk, forward and back: the adiabatic rise of an I2t, put back through the fusing form, returns the current
    for fk in ("B1", "B2", "S2"):
        f = R["fam"][fk]
        c = m.cmil(f["w"] * t1 * f["oz"])
        for i_face, tt in ((40.0, 0.5), (100.0, 0.05)):
            dT = m.rise_adiabatic(i_face * i_face * tt, f["w"], f["oz"], I)
            back = c * math.sqrt(math.log10(1.0 + dT / (I["k234"] + I["air_c"])) / (tt * I["k33"]))
            assert abs(back - i_face) < 1e-6 * i_face
    # the backstop read monotone from the blade's rows: held to the first timed row, then each interval's top for the row below's maximum
    env = m.envelope(blade, I["mini_rows"], I["pf_high"])
    timed = [(p, b) for p, a, b in I["mini_rows"] if b is not None]
    assert env[0][1] == blade * timed[0][0] / 100.0 and env[0][2] is None
    for (lab, a, d), (p0, t0), (p1, _t) in zip(env[1:], timed, timed[1:]):
        assert abs(a - blade * p1 / 100.0) < 1e-9 and d == t0
    # the docking pulse's I2t is the exponential's, peak squared times the time constant over two
    assert abs(I["dock_pk"] ** 2 * I["dock_tau"] / 2.0 - 0.9971) < 5e-4


def _ladder(n, rb, rv_end, rv_mid=None, both=False):
    """Two faces of n series segments (rb in all) tied at node 0 (through-hole); the sink on face F at the far end; face B
    joins F through rv_end at the far end (and at the near end too when both), and through rv_mid at every inner node when
    given. Solved by nodal analysis here; returns face F's share of the current at the far end's last segment."""
    r = rb / n
    # nodes: F1..Fn (Fn is the sink, held at 0 V), B1..Bn, and with both-ends a near face-F entry; node 0 is the source
    N = 2 * n + 1      # 0 source, 1..n F, n+1..2n B
    G = [[0.0] * N for _ in range(N)]

    def link(a, b, res):
        g = 1.0 / res
        G[a][a] += g; G[b][b] += g; G[a][b] -= g; G[b][a] -= g
    F = lambda k: k                      # k in 1..n
    B = lambda k: n + k
    link(0, F(1), r)
    if both:
        link(0, B(1), r + rv_end)        # the near end on face F too: B reached through a field
    else:
        link(0, B(1), r)
    for k in range(1, n):
        link(F(k), F(k + 1), r)
        link(B(k), B(k + 1), r)
        if rv_mid:
            link(F(k), B(k), rv_mid)
    link(B(n), F(n), rv_end)
    # inject 1 A at node 0, ground F(n): solve the reduced system
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
    i_f_last = (V[F(n - 1)] - V[F(n)]) / r      # face F's current in its last segment, before the field joins
    return i_f_last


def t_copper_the_split_on_a_solved_ladder():
    """The record's closed forms against a resistor ladder solved here: one end through-hole gives (Rb + Rv) / (2 Rb + Rv), and
    stitching along the band raises the part's face share (the page's 'moves current onto the part's face early')."""
    m = _CU()
    W = _C["CR"]["w"]
    h = _C["CR"]["h"][1]
    rb = m.r_band(10.0, W["coord_smax"], 1.0)
    rv = m.r_barrel(h) / 15
    want = m.share_one_end(10.0, W["coord_smax"], 1.0, 15, h)
    got = _ladder(20, rb, rv)
    assert abs(got - want) < 1e-9, "the one-end share %.6f against the ladder's %.6f" % (want, got)
    stitched = _ladder(20, rb, rv, rv_mid=m.r_barrel(h))
    assert stitched > want + 0.01, "stitching along the band did not raise the part's face share"
    # the split count holds the part's face at the governing share at every tabled length
    for name, w, hh, rows in _C["CR"]["transfer"]:
        for L, n1, n2 in rows:
            assert m.share_one_end(L, w, 1.0, n1, hh) <= m.S_MAX + 1e-12
            assert m.share_both_ends(L, w, 1.0, n2, hh) <= m.S_MAX + 1e-12
            if n1 > 1:
                assert m.share_one_end(L, w, 1.0, n1 - 1, hh) > m.S_MAX, "%s at %g mm: one barrel fewer still holds" % (name, L)


def t_copper_the_page_carries_the_outputs_figures():
    _CU()
    R, W = _C["CR"], _C["CR"]["w"]
    need(PAGE, "the page")
    page = open(PAGE, encoding="utf-8").read()
    sec = page[page.index("## 14. The pack path's copper on its basis"):]
    rows = {(fk, r[0]): r for fk, f in R["fam"].items() for r in f["rows"]}
    want = ["%.2f mm" % W[k] for k in ("coord_even", "coord_smax", "sh20_even", "sh20_smax", "sh10_smax", "vin_smax", "coord_smax_2oz")]
    want += ["%.2f K" % rows[("A1", "held under the gauge's OCD1")][7], "%.2f K" % rows[("A1", "the blade's rating (the chain's check 3)")][7],
             "%.1f C" % (R["in"]["air_c"] + rows[("A1", "blade 135 to 200 %, at most 600 s")][7]),
             "%.1f C" % (R["in"]["air_c"] + rows[("B1", "blade 135 to 200 %, at most 600 s")][7]),
             "%.1f C" % (R["in"]["air_c"] + rows[("B1", "blade 200 to 350 %, at most 5 s")][7]),
             "%.2f mm a face of the 68 mm strip" % R["e_cross"]["sum"], "%.2f mm a face at the pack end" % R["e_cross"]["pack_end"],
             "%d at P_CP" % max(R["e7_cellf_n"], R["thermal_barrels"]["pack"]), "%.2f mm" % R["e7_cellf_len"],
             "%.2f A" % R["r17_limit_a"], "%.2f A" % R["r19_limit_a"], "%.1f mm of a 14.60 mm band" % R["barrel_mm_eq"],
             "19.50 to 28.20 mm", "0.9971 A2s", "854a2bf5", "OWNER DECISION", "%.2f K" % R["nonfuse_rise"]["B1"]]
    want += ["%.2f / %.2f" % (two, one) for _lab, _a, two, one in R["ask"]]
    for s in want:
        assert s in sec, "section 14 does not carry %r" % s
    for f in ("L9C-F%d" % k for k in range(1, 10)):
        assert f in sec, "section 14 does not file %s" % f


def _reg_with_decisions(tmp):
    """A copy of the register with this record's seven decisions appended (the apply script on a copy)."""
    reg = os.path.join(tmp, "pcb_decisions.yaml")
    shutil.copyfile(REGISTER, reg)
    import yaml
    have = [x for x in yaml.safe_load(open(reg, encoding="utf-8"))["decisions"] if "(L9STK " in str(x.get("title", ""))]
    if not have:
        r = subprocess.run([sys.executable, "-B", APPLY, "--registry", reg], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
    return reg


def t_the_energy_chain_draft_follows_the_decisions_and_replaces_l8r2s():
    _CU()
    _A()
    need(CHAIN_DRAFT, "the energy chain draft")
    ast.parse(open(CHAIN_DRAFT, encoding="utf-8").read())
    W = _C["CR"]["w"]
    tmp = tempfile.mkdtemp(prefix="l9stk-chain-")
    try:
        import yaml
        bare = os.path.join(tmp, "bare.yaml")
        shutil.copyfile(REGISTER, bare)
        if not [x for x in yaml.safe_load(open(bare, encoding="utf-8"))["decisions"] if "(L9STK " in str(x.get("title", ""))]:
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
        for sid, keys in (("DOCK_ENTRY", ("coord_even", "coord_smax")), ("BOARD_A_NODE", ("coord_even", "coord_smax")),
                          ("SHORE_INPUT", ("sh20_even", "sh20_smax", "sh10_smax"))):
            for k in keys:
                assert "%.2f mm" % W[k] in st[sid]["conductor"]["what"], "%s does not carry %.2f mm" % (sid, W[k])
            assert "2 oz" not in str(st[sid]["conductor"])
        orig = {s["id"]: s for s in yaml.safe_load(open(CHAIN, encoding="utf-8"))["stages"]}
        for sid in orig:
            if sid not in ("DOCK_ENTRY", "BOARD_A_NODE", "SHORE_INPUT"):
                assert st[sid] == orig[sid], "%s moved" % sid
            else:
                assert st[sid]["conductor"]["rating_a"] == orig[sid]["conductor"]["rating_a"]
        # after record l8r2's draft has run, this one still applies, to the same bytes
        if os.path.isfile(L8R2_DRAFT):
            c2 = os.path.join(tmp, "c2.yaml")
            shutil.copyfile(CHAIN, c2)
            subprocess.run([sys.executable, "-B", L8R2_DRAFT, "--chain", c2, "--registry", reg, "--write"], capture_output=True, text=True)
            r3 = subprocess.run([sys.executable, "-B", CHAIN_DRAFT, "--chain", c2, "--registry", reg, "--write"], capture_output=True, text=True)
            assert r3.returncode == 0, r3.stdout + r3.stderr
            assert open(c1, encoding="utf-8").read() == open(c2, encoding="utf-8").read()
        # the chain's own gate reads the corrected copy as it reads the tree's
        import energy_chain
        a, b = energy_chain.check(), energy_chain.check(c1)
        for k in ("stages", "checked", "fails", "stage_fails", "derate_fails"):
            assert a[k] == b[k], "energy_chain.check's %s moved" % k
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_boards_a_and_e_decide_at_the_coordination_current():
    _CU()
    A, D = _decisions()
    W = _C["CR"]["w"]
    by = {d["board"]: d for d in D}
    for b in ("a", "e"):
        d = by[b]
        assert "1 oz outer" in d["title"], "board %s's title must keep '1 oz outer' (record l8r2's guard reads it)" % b
        for k in ("coord_even", "coord_smax"):
            assert "%.2f mm" % W[k] in d["outcome"], "board %s's outcome does not carry %.2f mm" % (b, W[k])
        assert "l9stk_copper.out" in d["measurement"] and "l9stk_copper.py" in d["reversed_by"]
        assert "6.72 mm wide on each" not in d["outcome"], "board %s still lays the 18 A width" % b
    assert "%.2f mm" % W["sh20_even"] in by["e"]["outcome"] and "%.2f mm" % W["vin_smax"] in by["e"]["outcome"]


def t_the_readme_names_the_copper_files():
    need(README, "the README")
    t = open(README, encoding="utf-8").read()
    for f in ("l9stk_copper.py", "l9stk_copper.out", "apply_energy_chain_l9stk.py"):
        assert f in t, "the README does not name %s" % f
