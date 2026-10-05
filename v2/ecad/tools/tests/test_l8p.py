"""Layer 8 record l8p (MESHSAT-1357, 4 October 2026, rounds 1 to 3; v2/docs/records/l8p/): W4DP-F2's breaker drawn as
release-guarded drafts for board P (the latch-off LM5069-1, the make-last enable loop's inverters, the RC hold through a diode, the
restart inhibit C-1c gated by PGD, and in round 3 B-R2's reverse-charge detector on the loop's return), board E (the loop through
J_SMB to the dock) and board A (the loop's thermal guard RT1), from record l9stk section 15 (fnd/l9stk at 0d72880b) and task
L4-E11's section 19h (fnd/l4e11r9 at e60a94a8).

The predicates: the committed .out is what the script prints; each draft checks, applies once on a scratch copy, refuses twice and
refuses the tree's own generator; each board composes in L4-E9's change-list order with this record's draft in its place, first
and last (board E with L4-E7's backstop draft of fnd/l4e7r6, which closes L8P-F01); the designators are this record's sets and
disjoint from every other draft's; every value is found in record l9stk's copied text and the copies are the bytes SOURCES.txt
pins; C-1c's budget closes on figures read from TI's held OPA187 sheet and Murata's NTC sheet; B-R2's detector closes on figures
read from L4-E11's copies and the LM5069, CSD18510Q5B, 2N7002 and BZT52C sheets; the netlist check reads NOT DRAWN
on the committed netlists, DRAWN on the netlists regenerated from the patched generators (the loop across the three boards and
the inhibit included) and FAIL on mutated ones; the page carries no em or en dash and no claim word, and names the conditions
and the interface rows owed. No KiCad: generator text, the generators' own part tables and netlist text, on scratch copies; the
tree is never written."""
import hashlib
import importlib.util
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

TESTS = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(TESTS)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l8p")
SCRIPT = os.path.join(REC, "l8p_drafts.py")
OUT = os.path.join(REC, "l8p_drafts.out")
PAGE = os.path.join(REC, "L8P-BREAKER.md")
GEN = {b: os.path.join(TOOLS, "gen_sch_%s.py" % b) for b in "pea"}
sys.path.insert(0, TESTS)
from harness import need, Skip  # noqa: E402

CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)
_C = {}


def _mod(name, fname):
    if name not in _C:
        p = need(os.path.join(REC, fname), "a file of the l8p record")
        if REC not in sys.path:
            sys.path.insert(0, REC)
        sp = importlib.util.spec_from_file_location(name, p)
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        _C[name] = m
    return _C[name]


def _M():
    return _mod("l8p_drafts_under_test", "l8p_drafts.py")


def _CHK():
    return _mod("check_l8p_netlist_under_test", "check_l8p_netlist.py")


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _run(args):
    return subprocess.run([sys.executable, "-B"] + args, capture_output=True)


def _need_inputs():
    m = _M()
    need(m.OPA187, "TI's held OPA187 sheet (python3 v2/docs/records/l8p/fetch_held_back.py)")
    for b in "pea":
        need(GEN[b], "board %s's generator" % b.upper()); need(m.NET[b], "board %s's committed netlist" % b.upper())
        for r, n in m.ORDER[b]:
            need(m.draft(r, n, b), "a board %s draft L4-E9's order composes" % b.upper())
    return m


def t_the_committed_output_is_what_the_script_prints():
    _need_inputs()
    before = {b: _sha(GEN[b]) for b in "pea"}
    r = subprocess.run([sys.executable, "-B", SCRIPT], capture_output=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr.decode()[-400:]
    assert r.stdout == open(OUT, "rb").read(), "l8p_drafts.out is not what l8p_drafts.py prints; regenerate it with _bin/regen_out.py"
    assert all(_sha(GEN[b]) == s for b, s in before.items()), "the script wrote into the tree"
    t = r.stdout.decode()
    for s in ("record l9stk's, L4-E7's and L4-E11's copies equal the sha256 SOURCES.txt pins: yes", "the tree's generators are unchanged: yes",
              "+-1.95 K left: consistent", "the split closes", "is ASSUMED from the product search sheet", "THE LOCKOUT AT THE ALLOW EDGE",
              "E-10 gains: VDS under 1.62 V during current-limit excursions", "CLOSED by L4-E7's fnd/l4e7r6 at 914a2f5a",
              "l8p/inputs/l4e7r6-apply_gen_sch_e_backstop-914a2f5a.py OK", "       P INH  DRAWN", "decoupling C106: class D at U102.5 on BRK_VIN",
              "board P, this record's against every other draft's: DISJOINT", "board E, this record's against every other draft's: DISJOINT",
              "board A, this record's against every other draft's: DISJOINT", "record l8p's breaker and enable loop on the netlists: NOT DRAWN",
              "       LOOP DRAWN", "all KiCad's names for open pins: yes; footprints differing: 0", "(R248, C247)",
              "L8P-F01 board E", "L8P-F02 board A", "L8P-F03 board E", "L8P-F04 board A", "L8P-F05 board A", "       P REV  DRAWN",
              "B-R2 BY THE CRITERION: MEETS ON PAPER", "decoupling C107: class D at U103.5 on BRK_VIN", "decoupling C108: class D at U104.5 on BRK_VIN",
              "l8p/inputs/l4e11-section19h-e60a94a8.md", "only the return held LOW is distinct"):
        assert s in t, s
    assert t.count("record l8p's breaker and enable loop on the netlists: DRAWN") == 2, "the alone and the composed readings"
    assert t.count("record l8p's breaker and enable loop on the netlists: FAIL") == 5, "the five mutations"
    assert "REFUSED" not in t.split("5. COMPOSITION")[1].split("6. DESIGNATORS")[0], "a composition step refused"
    for seg in t.split("with scratch stand-ins for ")[1:]:      # none at all since L4-E11's round 9 corrected L8P-F02 and L8P-F03
        assert "L8P-F01" not in seg.split("\n")[0], "a stand-in for the closed L8P-F01 is still used"


def t_each_draft_checks_applies_once_refuses_twice_and_refuses_the_tree():
    m = _M()
    before = {b: _sha(GEN[b]) for b in "pea"}
    with tempfile.TemporaryDirectory() as d:
        for b in "pea":
            s = m.MINE[b]
            tgt = os.path.join(d, os.path.basename(s) + ".gen.py"); shutil.copy(GEN[b], tgt); pre = _sha(tgt)
            r = _run([s, tgt]); assert r.returncode == 0 and b"CHECK OK" in r.stdout, r.stderr.decode()[-300:]
            assert _sha(tgt) == pre, "--check wrote"
            r = _run([s, tgt, "--write"]); assert r.returncode == 0 and b"WRITTEN" in r.stdout, r.stderr.decode()[-300:]
            assert _run([s, tgt, "--write"]).returncode == 3, "a second application was not refused"
            r = _run([s, GEN[b], "--write"]); assert r.returncode == 3 and b"NOT RELEASED" in r.stderr, "the tree's own generator was not refused"
            compile(open(tgt, encoding="utf-8").read(), tgt, "exec")
    assert not os.path.exists(os.path.join(REC, "RELEASE.md")), "a release record exists: the drafts are no longer guarded"
    assert all(_sha(GEN[b]) == s for b, s in before.items()), "a draft wrote into the tree"


def t_each_board_composes_in_l4e9s_order_in_its_place_first_and_last():
    m = _need_inputs()
    with tempfile.TemporaryDirectory() as d:
        for b in "pea":
            seq = [m.draft(r, n, b) for r, n in m.ORDER[b]]
            for tag, order in (("fwd", seq[:m.SLOT[b]] + [m.MINE[b]] + seq[m.SLOT[b]:]), ("first", [m.MINE[b]] + seq), ("last", seq + [m.MINE[b]])):
                p, res = m.compose(b, order, d, tag)
                assert len(res) == len(order) and all(v.startswith("OK") for _s, v in res), (b, tag, res)
                compile(open(p, encoding="utf-8").read(), p, "exec")


def t_the_designators_are_this_records_sets_and_disjoint():
    m = _need_inputs()
    want = {"p": {"U101", "U102", "U103", "U104", "D101", "D102", "D103", "RT101"} | {"Q%d" % k for k in range(101, 109)}
            | {"R%d" % k for k in range(101, 130)} | {"C%d" % k for k in range(101, 111)} | {"TP%d" % k for k in range(101, 109)},
            "e": set(), "a": {"RT1"}}
    with tempfile.TemporaryDirectory() as d:
        for b in "pea":
            seq = [m.draft(r, n, b) for r, n in m.ORDER[b]]
            fwd = seq[:m.SLOT[b]] + [m.MINE[b]] + seq[m.SLOT[b]:]
            p = os.path.join(d, "g_%s.py" % b); shutil.copy(GEN[b], p)
            before = open(p, encoding="utf-8").read(); adds = {}
            for s in fwd:
                assert m.run(s, p, b)[0] == 0, s
                after = open(p, encoding="utf-8").read(); adds[s] = m.added(before, after, s); before = after
            mine = adds[m.MINE[b]]
            assert mine == want[b], (b, sorted(mine ^ want[b]))
            for s, a in adds.items():
                assert s == m.MINE[b] or not (a & mine), "%s meets this record's %s" % (s, sorted(a & mine))
            assert not m.duplicates(before), (b, m.duplicates(before))


def t_every_value_is_the_records_and_the_copies_are_pinned():
    m = _M(); chk = _CHK()
    for f, full in m.SOURCES_SHA.items():
        assert _sha(os.path.join(REC, f)) == full, f
        assert full in open(os.path.join(REC, "inputs", "SOURCES.txt"), encoding="utf-8").read(), "SOURCES.txt does not pin %s" % f
    texts = {k: open(os.path.join(REC, v), encoding="utf-8").read() for k, v in m.INPUT_FILES.items()}
    drafts = {b: open(m.MINE[b], encoding="utf-8").read() for b in "pea"}
    for b, ref, pre, src, pat, key in chk.VALUES:
        assert re.search(chk.phrase_rx(pat), texts[key]), "l9stk no longer reads %s's value (%s)" % (ref, src)
        call = re.search(r'(?:ic|r|c|part|pfet5|nfet)\(\\?"%s\\?", ' % re.escape(ref), drafts[b])
        assert call, "%s is not drawn in the board %s draft" % (ref, b.upper())
    assert "R_G = 1e6" in texts["constants"] and "R_E1, R_E2 = 10e3, 22e3" in texts["constants"] and "R_BRIDGE = 150e3" in texts["constants"]
    assert m.R_BRIDGE == 150e3 and 'r("R110", "150k 0.1% 25ppm (the NTC bridge)", "BRK_VIN", "INH_NTC")' in drafts["p"]
    assert '"LM5069MM-1 circuit breaker' in drafts["p"] and "LM5069MM-2" not in drafts["p"], "U101 is not the -1"


def t_the_netlist_check_reads_not_drawn_drawn_and_fail():
    m = _need_inputs(); chk = _CHK()
    kit, v = chk.run(m.NET, ROOT, io.StringIO())
    assert kit == "NOT DRAWN" and set(v.values()) == {"NOT DRAWN"}, v
    with tempfile.TemporaryDirectory() as d:
        paths = {}
        for b in "pea":
            t = os.path.join(d, "gen_sch_%s.py" % b); shutil.copy(GEN[b], t)
            assert m.run(m.MINE[b], t, b)[0] == 0
            rc, path, table = m.netlist_text(b, t, d, "t")
            assert rc == 0 and table["intent_written"] and not table["unplaced"], (b, path)
            paths[b] = path
        buf = io.StringIO(); kit, v = chk.run(paths, ROOT, buf)
        assert kit == "DRAWN" and v.get("loop") == "DRAWN", buf.getvalue()
        bad = m.mutate(paths["e"], d, "mut_e", [(("J_BLK", "4"), ("J_BLK", "5"))])
        kit, v = chk.run({"e": bad}, ROOT, io.StringIO())
        assert kit == "FAIL", "the ground between J_BLK's loop pins moved and the check did not fail"
        raw = open(paths["p"], encoding="utf-8").read().replace('(node (ref "D101") (pin "1"))', '(node (ref "D101") (pin "9"))')
        open(os.path.join(d, "mut_p.net"), "w", encoding="utf-8").write(raw)
        kit, v = chk.run({"p": os.path.join(d, "mut_p.net")}, ROOT, io.StringIO())
        assert kit == "FAIL", "the input clamp left BRK_VIN and the check did not fail"
        for swap, what in (([("Q106", "1"), ("R117", "2")], "Q106's gate left PGD"), ([("Q104", "3"), ("R105", "1")], "Q104 no longer pulls UVLO directly"),
                           ([("U102", "3"), ("U102", "4")], "the comparator's inputs exchanged"),
                           ([("U104", "3"), ("U104", "4")], "the reverse comparator's inputs exchanged"),
                           ([("Q107", "3"), ("Q105", "3")], "the detector's pull moved off the loop's return onto UVLO"),
                           ([("R120", "1"), ("R119", "2")], "the charge comparator no longer on R10's cell side"),
                           ([("D103", "1"), ("D103", "2")], "the reference's zener reversed")):
            bad = m.mutate(paths["p"], d, "mut_%s" % swap[0][0], [tuple(swap)])
            buf = io.StringIO(); kit, v = chk.run({"p": bad}, ROOT, buf)
            assert kit == "FAIL", "%s and the check did not fail: %s" % (what, buf.getvalue())


def t_the_unpatched_generators_reproduce_the_committed_netlists():
    m = _need_inputs(); chk = _CHK()
    with tempfile.TemporaryDirectory() as d:
        for b in "pea":
            rc, path, _t = m.netlist_text(b, GEN[b], d, "base")
            assert rc == 0, path
            a, k = chk.read_netlist(open(path, "rb").read()), chk.read_netlist(open(m.NET[b], "rb").read())
            pa, pk = m.pins_of(a), m.pins_of(k)
            diff = [x for x in set(pa) | set(pk) if pa.get(x) != pk.get(x)]
            assert all(pa.get(x) is None and str(pk.get(x)).startswith("unconnected-") for x in diff), (b, sorted(diff)[:5])
            assert all(a["comps"][r]["footprint"] == k["comps"][r]["footprint"] for r in a["comps"]), b


def t_the_restart_inhibits_budget_closes_on_read_figures():
    """C-1c (DD-8): the window is the record's, the comparator's figures are read from TI's held sheet and the NTC's from Murata's,
    the split leaves the checker's 0.9 K for the gradient on both sides, the comparator under 0.47 K, the hysteresis under 0.5 K,
    the drawn reference within 0.05 K of the record's trip, the bridge current under the NTC's rating."""
    m = _need_inputs()
    page = open(os.path.join(REC, m.INPUT_FILES["page"]), encoding="utf-8").read()
    B = m.budget(page)
    assert (B["allow"], B["block"], B["trip"], B["half"], B["r_trip"]) == (77.25, 83.20, 80.22, 2.97, 1653.0), B
    assert B["window_ok"] and B["closes"], B
    read = {"vos": 10e-6, "drift": 0.015e-6, "ios": 14.5e-9, "ib": 7.5e-9, "psrr": 1e-6}
    assert all(abs(B[k] - v) <= 1e-6 * v for k, v in read.items()), ("the OPA187's figures", {k: B[k] for k in read})
    assert B["vs"][1] >= 29.2 and B["vs_abs"] >= 36, "the OPA187's supply against BRK_VIN's clamp"
    assert B["k_op"] <= 0.47 and B["hyst_max"] <= 0.5 and 0 < B["hyst_nom"] <= B["hyst_max"], B
    assert B["grad_allow"] >= 0.9 and B["grad_block"] >= 0.9, B
    assert abs(B["k_nominal"]) <= 0.05 and B["i_bridge"] <= B["imax"], B
    assert abs(B["lockout"] - 1.0) < 1e-9, "the allow edge is the inside air plus 1 K"


def t_b_r2s_detector_closes_on_read_figures():
    """B-R2, route R1 (round 3): the open case is L4-E11's, the threshold's floor is over the LDO-mode precharge and its top under
    the latched FET's safe level, the reverse threshold sits between a running breaker's channel drop and the body diodes' typical
    VSD, the pull and the interface's levels hold at PORIT, the restart fits board A's least hold, and the copies are pinned."""
    m = _need_inputs()
    for f in ("inputs/l4e11-section19h-e60a94a8.md", "inputs/l4e11-section15c-precharge-e60a94a8.md"):
        assert _sha(os.path.join(REC, f)) == m.SOURCES_SHA[f], f
    for sheet in (m.CSD_SHEET, m.N7002_SHEET, m.BZT_SHEET, m.LM5069_SHEET):
        need(sheet, "a maker's sheet the detector reads")
    texts = {k: open(os.path.join(REC, v), encoding="utf-8").read() for k, v in m.INPUT_FILES.items()}
    B = m.budget(texts["page"])
    R = m.rev_budget(texts["page"], texts["l4e11"], texts["l4e11pre"], B)
    assert R["ok"], {k: R[k] for k in ("m_lo", "m_hi", "vt_min", "vt_max", "v_chan", "vsd_150", "tj_at_max")}
    assert (R["i_safe"], R["i_rb"], R["i_ldo"], R["r10"], R["i_lim"]) == (1.405, 1.2567, 0.33616, 2e-3, 23.93), R
    assert R["i_th_min"] > R["i_ldo"] * 1.05 and R["i_th_max"] < R["i_safe"] / 1.10, (R["i_th_min"], R["i_th_max"])
    assert R["tj_at_max"] < 145.0, R["tj_at_max"]
    assert R["vt_min"] > 2 * R["v_chan"] and R["vt_max"] < R["vsd_150"] - 0.05, (R["vt_min"], R["v_chan"], R["vt_max"], R["vsd_150"])
    assert R["gate_run"] > R["n_vth"][1] + 1.0 and m.V_CLAMP / 2 < R["n_vgs"], (R["gate_run"], R["n_vth"])
    assert R["out_run"] >= m.OUT_POWERED + 0.5 and R["v_ret"] < m.RET_LOW / 10, (R["out_run"], R["v_ret"])
    assert R["t_restart"] < m.STRETCH_MIN and R["t_d"] < 1e-3, (R["t_restart"], R["t_d"])
    assert R["out_run"] / 2 < R["n_vth"][1], "L8P-F04's premise: Q47 at half of DOCK_EN_OUT no longer reads the loop powered"
    drafts = open(m.MINE["p"], encoding="utf-8").read()
    for frag in ('"OPA187IDBVR zero-drift amplifier as the reverse-charge detector', '"BZT52C12-7-F zener', '"1.15M 0.1% 25ppm', '"328k 0.05% 10ppm',
                 'nfet("Q107", "REV_IG", "REV_MID", "DOCK_EN_RET"', 'nfet("Q108", "REV_VG", "PACK_N", "REV_MID"'):
        assert frag in drafts, frag


def t_the_page_is_clean_and_names_the_rows_owed():
    page = open(need(PAGE, "the l8p record page"), encoding="utf-8").read()
    for p in [PAGE, os.path.join(REC, "README.md")] + [os.path.join(REC, f) for f in os.listdir(REC) if f.endswith(".py")]:
        t = open(p, encoding="utf-8").read()
        assert "\u2014" not in t and "\u2013" not in t, "an em or en dash in %s" % os.path.basename(p)
    assert not CLAIM.search(page), CLAIM.search(page).group(0)
    for s in ("**Status: DRAFTED, not applied.**", "**The fifth to seventh J_SMB contacts:**", "**The dock enable contacts:**",
              "**PACK_P live only while docked:**", "**The make-last contact's 1 mm (C1):**", "**The mating order C1, both ways:**",
              "**The third battery FET's designator**", "**IF-1, critical to the service under the -1:**", "**IF-2:**", "L8P-F01", "L8P-F02", "L8P-F03",
              "**The NTC's tolerance at 80 C is ASSUMED.**", "**E-12b, a commissioning check like E-12**", "**E-10's line gains:**",
              "**The lockout at the allow edge.**", "**The NTC is bonded to the pad.**", "**DD-7, the input-return pulse:**", "**IF-7:**",
              "**CLOSED** by L4-E7's `fnd/l4e7r6` at `914a2f5a`", "**Order codes owed:**",
              "## 12. B-R2: the charge through a latched breaker", "**The criterion, item by item:**", "### 12a. What exists, and why none of it tells board A",
              "**B-R2's interface, route R1 (section 12f, finding L8P-F04):**", "| L8P-F04 | A |", "| L8P-F05 | A |", "### 12h. Not taken",
              "**E-14 (record l9stk's, with route R1)**", "**E-12c, a commissioning check like E-12**", "**R10's tolerance and temperature coefficient**",
              "**B-R2's route R1 DRAFTED on board P**", "no new contact"):
        assert s in page, s
    for ref in ("U101", "R101", "R102", "Q101, Q102", "R103", "C101", "C102", "D101", "R104", "C103", "R105", "D102", "R106", "R107", "Q103",
                "Q104", "R108, R109", "RT101", "R110", "RT1 (board A)"):
        assert "| %s" % ref in page, "the value table omits %s" % ref
