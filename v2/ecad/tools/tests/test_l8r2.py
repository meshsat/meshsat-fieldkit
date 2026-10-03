"""Layer 8 record l8r2 (MESHSAT-1357, 3 October 2026; v2/docs/records/l8r2/): the known engineering defects corrected at the desk
on printed parts, as release-guarded drafts: board B's coolers on a 12 V step-up (E11-40), VBUS20's over-voltage cut-off on board A
(S-111), PANEL_5V and board D's 3.3 V behind eFuses (L5R2-F03, F05), J_QMX and J_CAM on the JST PH land (L5R2-F04); round 3 (3 October
2026): item 1 re-decided on record l9pwr's L9P-F02 (the coolers' step-up kept with the modules' 70 % Fan_PWM maximum), the pack path's
return declared as a rail on boards A and E (record l9stk's finding), the energy chain's board E 2 oz texts corrected by an apply script.

The predicates: the committed .out is what the script prints; each draft checks, applies once, refuses twice and refuses the tree's
own generator; board A composes in L4-E9's order with l8gnd's and this record's drafts and d8dec31's mainpb last, and every other
draft's anchors still apply after this record's (in sequence and each alone); board B composes forward, in reverse and each alone;
the designators are disjoint on both boards and are exactly this record's sets; the figures hold their stated margins; the netlist
check reads NOT DRAWN on the committed netlists, DRAWN on fixtures and FAIL on a mutated fixture; the page carries no em or en dash
and no claim word. No KiCad: generator text, netlist text and arithmetic, on scratch copies; the tree is never written."""
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

TESTS = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(TESTS)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l8r2")
RECS = os.path.dirname(REC)
GEN_A = os.path.join(TOOLS, "gen_sch_a.py")
GEN_B = os.path.join(TOOLS, "gen_sch_b.py")
GEN_C = os.path.join(TOOLS, "gen_sch_c.py")
GEN_E = os.path.join(TOOLS, "gen_sch_e.py")
CHAIN = os.path.join(TOOLS, "pcb_energy_chain.yaml")
FIX = os.path.join(REC, "apply_energy_chain_e1oz.py")
SCRIPT = os.path.join(REC, "l8r2_drafts.py")
OUT = os.path.join(REC, "l8r2_drafts.out")
PAGE = os.path.join(REC, "L8R2-KNOWN-DEFECTS.md")
CHECK = os.path.join(REC, "check_l8r2_netlist.py")
MINE = {"a": ["d8v3", "vbus20ov", "packrtn"], "b": ["fans12", "panel5v", "ph4"], "c": ["pibtn"], "e": ["packrtn"]}
sys.path.insert(0, TESTS)
from harness import need, Skip  # noqa: E402

CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)
_C = {}


def _mod(path, name):
    if name not in _C:
        need(path, "a file of the l8r2 record")
        sp = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        _C[name] = m
    return _C[name]


def _M():
    return _mod(SCRIPT, "l8r2_drafts_under_test")


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _run(args):
    return subprocess.run([sys.executable, "-B"] + args, capture_output=True)


def _mine(board):
    return [os.path.join(REC, "apply_gen_sch_%s_%s.py" % (board, n)) for n in MINE[board]]


def _need_inputs():
    m = _M()
    for p in m.INPUTS:
        need(os.path.join(ROOT, p), "an input of record l8r2")
    return m


def t_the_committed_output_is_what_the_script_prints():
    _need_inputs()
    before = {g: _sha(g) for g in (GEN_A, GEN_B)}
    r = subprocess.run([sys.executable, "-B", SCRIPT], capture_output=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr.decode()[-400:]
    assert r.stdout == open(OUT, "rb").read(), "l8r2_drafts.out is not what l8r2_drafts.py prints; regenerate it with _bin/regen_out.py"
    assert all(_sha(g) == s for g, s in before.items()), "the script wrote into the tree"
    t = r.stdout.decode()
    for s in ("board A pairwise intersections: none (DISJOINT)", "board B pairwise intersections: none (DISJOINT)",
              "record l8r2's corrections on the netlists: NOT DRAWN", "fixture A: DRAWN", "fixture B: DRAWN", "(R248, C247)", ": REJECTED",
              "SELECTED (SESSION): (a) with the modules' 70 % Fan_PWM maximum", "REFUSED (intent: rail +5V_S1 declares a 5.00 A peak",
              "OK at every prefix", "IDENTICAL", "the corrected texts name those widths: YES", "the same as this script's E_ROUND",
              "equals record l9pwr's printed current in every row: YES"):
        assert s in t, s


def t_each_draft_checks_applies_once_refuses_twice_and_refuses_the_tree():
    before = {g: _sha(g) for g in (GEN_A, GEN_B, GEN_C, GEN_E)}
    with tempfile.TemporaryDirectory() as d:
        for board, gen in (("a", GEN_A), ("b", GEN_B), ("c", GEN_C), ("e", GEN_E)):
            for s in _mine(board):
                tgt = os.path.join(d, os.path.basename(s)); shutil.copy(gen, tgt); pre = _sha(tgt)
                r = _run([s, tgt]); assert r.returncode == 0 and b"CHECK OK" in r.stdout, r.stderr.decode()[-300:]
                assert _sha(tgt) == pre, "--check wrote"
                r = _run([s, tgt, "--write"]); assert r.returncode == 0 and b"WRITTEN" in r.stdout, r.stderr.decode()[-300:]
                assert _run([s, tgt, "--write"]).returncode == 3, "a second application was not refused"
                r = _run([s, gen, "--write"]); assert r.returncode == 3 and b"NOT RELEASED" in r.stderr, "the tree's own generator was not refused"
    assert all(_sha(g) == s for g, s in before.items()), "a draft wrote into the tree"


def t_board_a_composes_in_l4e9s_order_with_mainpb_last_and_every_anchor_still_applies():
    m = _need_inputs()
    pa = [m.draft(r, n, "a") for r, n in m.POWER_A]; l8 = [m.draft(r, n, "a") for r, n in m.L8_A]; mine = _mine("a")
    with tempfile.TemporaryDirectory() as d:
        for tag, seq in (("fwd", pa + l8), ("rev", mine + pa + l8[:2])):
            p, res = m.compose(GEN_A, seq, d, tag, mainpb_last=True)
            assert all(v.startswith("OK") for _s, v in res) and len(res) == len(seq) + 1, (tag, res)
            assert "(R248, C247)" in res[-1][1], res[-1]
            compile(open(p, encoding="utf-8").read(), p, "exec")
        r12 = [x for x in pa if x.endswith("_r12.py")]
        for s in pa:
            p = os.path.join(d, "alone_" + os.path.basename(s)); shutil.copy(GEN_A, p)
            for x in mine + (r12 if s.endswith("_bank.py") else []):
                assert _run([x, p, "--write"]).returncode == 0, x
            r = _run([s, p, "--write"]); assert r.returncode == 0, "%s refused after l8r2's drafts: %s" % (s, r.stderr.decode()[-200:])
        _p, res = m.compose(GEN_A, l8[::-1], d, "l8rev")
        assert all(v == "OK" for _s, v in res), res


def t_board_b_composes_forward_in_reverse_and_each_alone():
    m = _need_inputs()
    pb = [m.draft(r, n, "b") for r, n in m.L8_B]
    with tempfile.TemporaryDirectory() as d:
        for tag, seq in (("fwd", pb), ("rev", pb[::-1])):
            p, res = m.compose(GEN_B, seq, d, tag)
            assert all(v == "OK" for _s, v in res), (tag, res)
            compile(open(p, encoding="utf-8").read(), p, "exec")
        for s in pb:
            _p, res = m.compose(GEN_B, [s], d, "alone_" + os.path.basename(s)[:-3])
            assert res[0][1] == "OK", res


def t_the_designators_are_disjoint_and_this_records_are_exact():
    m = _need_inputs()
    pa = [m.draft(r, n, "a") for r, n in m.POWER_A + m.L8_A]; pb = [m.draft(r, n, "b") for r, n in m.L8_B]
    with tempfile.TemporaryDirectory() as d:
        pA, addA = m.designators(GEN_A, pa, d, "a", mainpb_last=True)
        pB, addB = m.designators(GEN_B, pb, d, "b")
        assert addA["l8r2/apply_gen_sch_a_d8v3.py"] == {"U44", "R234", "R235", "R236", "R237", "R238", "C242", "C243"}
        assert addA["l8r2/apply_gen_sch_a_vbus20ov.py"] == {"U45", "Q41", "C244", "C245", "C246"} | {"R%d" % k for k in range(239, 248)}
        assert addA["d8dec31/apply_gen_sch_a_mainpb.py"] == {"R248", "C247"} and addA["l8r2/apply_gen_sch_a_packrtn.py"] == set()
        pE, addE = m.designators_e(d)
        assert addE["l8r2/apply_gen_sch_e_packrtn.py"] == set() and not m.duplicates(open(pE, encoding="utf-8").read())
        fans = {"%s%d" % (p, 700 + 30 * (s - 1) + k) for s in (1, 2, 3) for p, ks in (("U", (1, 2)), ("L", (1,)), ("Q", (1, 2)), ("R", range(1, 13)), ("C", range(1, 11))) for k in ks}
        assert addB["l8r2/apply_gen_sch_b_fans12.py"] == fans
        assert addB["l8r2/apply_gen_sch_b_panel5v.py"] == {"U901", "R901", "R902", "R903", "R904", "R905", "C901", "C902"}
        assert addB["l8r2/apply_gen_sch_b_ph4.py"] == set() and addB["l8gnd/apply_gen_sch_b_gnd002.py"] == set()
        for add in (addA, addB):
            names = sorted(add)
            for i, x in enumerate(names):
                for y in names[i + 1:]:
                    assert not ((add[x] or set()) & (add[y] or set())), "%s and %s share %s" % (x, y, sorted(add[x] & add[y]))
        assert not m.duplicates(open(pA, encoding="utf-8").read()) and not m.duplicates(open(pB, encoding="utf-8").read())


def t_item1_the_coolers_rail_holds_its_margins():
    m = _M(); o = m.item1(); V = m.V
    assert V["vfan"][0] < o["vout"][0] and o["vout"][2] < V["vfan"][1], o["vout"]
    assert V["ilim"][0] > o["peak_fault"][2] and V["isat"] > V["ilim"][2], "ILIM under the fault peak or Isat under ILIM"
    assert V["fc"] < o["fc_max"] and max(o["fc_at"].values()) < o["fc_max"], "the crossover over its limit"
    assert abs(o["r5_calc"] - V["r5"]) / V["r5"] < 0.02 and o["c6_calc"] < 10e-12
    assert o["efuse"][2] < 0.54 and o["efuse"][0] > V["ifan"] * 2 and o["ovlo"][0] > o["vout"][2]
    assert abs(o["slot_a"] - 0.461) < 0.001 and o["a_minus_b"] > 0, "the slot power or the choices' difference moved"


def t_item2_the_clamp_fails_at_the_fault_and_the_cut_off_holds_the_bus():
    m = _M(); t = m.item2(); V = m.V
    assert t["band_in_service"] and t["smcj_ratio"] > 10 and t["smcj_p_1a"] > V["smcj22a"][5], "the clamp's rejection rests on its power"
    assert t["trip"][0] > V["bus_bound"] and t["trip"][1] < V["u3_rec"], t["trip"]
    assert t["release"][1] < t["trip"][0] and t["en_on"][1] < V["uv_fall"]
    assert max(t["after_q2"], t["after_fb"]) < V["u3_abs"] - 5 and t["margin_q7"] > 2, (t["after_q2"], t["after_fb"])
    assert t["after_q2"] < V["u3_rec"] and t["over_rec"] < 0.5


def t_item3_each_conductor_stays_under_its_rating():
    m = _M(); u = m.item3(); V = m.V
    assert u["old_cond"] > V["i_cond"], "the defect as found is not over the conductor's rating"
    assert u["pnl_cond_mm"] < V["i_cond"] and u["pnl"][0] > V["c_peak"], u["pnl"]
    assert 0.5 <= u["pnl_pin"][0] and u["pnl_pin"][1] < V["vovlo_f"][0]
    assert u["d8"][3] == "printed row" and u["d8"][0] > 2 * V["d_peak"] and u["d8"][2] < V["i_cond"]
    assert 0.5 <= u["d8_pin"][0] and u["d8_pin"][1] < V["vovlo_f"][0]


def t_the_netlist_check_reads_the_tree_not_drawn_and_the_fixtures_drawn():
    chk = _mod(CHECK, "l8r2_check_under_test")
    nets = chk.committed(ROOT)
    for k in ("a", "b", "c"):
        need(nets.get(k, os.path.join(ROOT, "missing-%s.net" % k)), "board %s's committed netlist" % k.upper())
    kit, v = chk.run(nets, ROOT, open(os.devnull, "w"))
    assert kit == "NOT DRAWN" and v == {"a": "NOT DRAWN", "b": "NOT DRAWN", "c": "NOT DRAWN"}, v
    bad = chk.fixture("c").replace(b'(node (ref "R57") (pin "2"))', b'')
    assert chk.judge("c", chk.read_netlist(bad))[0] == "FAIL", "a pull-up off +3V3 is not refused"
    for letter in ("a", "b", "c"):
        assert chk.judge(letter, chk.read_netlist(chk.fixture(letter)))[0] == "DRAWN"
    bad = chk.fixture("a").replace(b'(node (ref "U45") (pin "2"))', b'(node (ref "U45") (pin "99"))')
    assert chk.judge("a", chk.read_netlist(bad))[0] == "FAIL"
    bad = chk.fixture("b").replace(b'"/CFAN2_V") (node (ref "J_FAN2") (pin "1"))', b'"/CFAN2_V")')
    assert chk.judge("b", chk.read_netlist(bad))[0] == "FAIL"


def t_the_page_and_the_record_carry_no_dash_and_no_claim_word():
    need(PAGE, "the record's page")
    files = [os.path.join(REC, f) for f in sorted(os.listdir(REC)) if f.endswith((".md", ".py", ".out"))] + [os.path.abspath(__file__)]
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "%s carries an em or en dash" % os.path.relpath(p, ROOT)
        if p != os.path.abspath(__file__):
            mm = CLAIM.search(" ".join(t.split()))
            assert not mm, "%s carries a claim word: %r" % (os.path.relpath(p, ROOT), mm.group(0))
    page = open(PAGE, encoding="utf-8").read()
    for s in ("E11-40", "S-111", "L5R2-F03", "L5R2-F04", "L5R2-F05", "P1-1", "REJECTED", "SELECTED", "NOT DRAWN", "R248", "DRAFT",
              "L9P-F02", "L9P-F03", "70 %", "7.5638", "apply_gen_sch_a_packrtn.py", "apply_gen_sch_e_packrtn.py", "(L9STK E)",
              "apply_energy_chain_e1oz.py", "ASM-002"):
        assert s in page, s


def t_no_new_net_of_this_record_names_a_net_any_board_already_has():
    """Every net this record's drafts add is new on EVERY board, not only on its own (the bring-up author's finding of 3 October
    2026: board A's branch was first named +3V3_D8, board D's own rail's name, so one name crossed the harness for two rails)."""
    chk = _mod(CHECK, "l8r2_check_under_test")
    import glob
    nets = set()
    for p in glob.glob(os.path.join(ROOT, "v2", "ecad", "pcb-*", "out", "*.net")):
        nl = chk.read_netlist(open(p, "rb").read())
        nets |= {n for pins in nl["pins"].values() for n in pins.values()}
    assert "+3V3_D8" in nets, "board D's own +3V3_D8 is not read: the netlists were not parsed"
    for board in ("a", "b", "c", "e"):
        for s in _mine(board):
            m = _mod(s, "nets_" + os.path.basename(s)[:-3])
            clash = sorted(set(getattr(m, "NETS", ())) & nets)
            assert not clash, "%s adds %s, a net a committed netlist already carries" % (os.path.basename(s), clash)
    d8 = _mod(os.path.join(REC, "apply_gen_sch_a_d8v3.py"), "nets_apply_gen_sch_a_d8v3")
    assert "+3V3_A2D" in d8.NETS and "+3V3_D8" not in open(os.path.join(REC, "apply_gen_sch_a_d8v3.py"), encoding="utf-8").read()


def t_board_c_the_pi_button_composes_with_layer_6s_draft_in_either_order():
    """Layer 6's apply_gen_sch_c_lcsc.py (fnd/l6r2 at 7633ae0a, copied in inputs/ with its helper) and this record's PI button
    draft give the same generator in either order; this record's adds R57 alone and Layer 6's adds no part."""
    m = _need_inputs()
    pi = os.path.join(ROOT, m.PIBTN)
    with tempfile.TemporaryDirectory() as d:
        l6 = m.l6_scratch(d); outs = []
        for seq in ([l6, pi], [pi, l6]):
            p = os.path.join(d, "c_%d.py" % len(outs)); shutil.copy(GEN_C, p)
            for x in seq:
                r = _run([x, p, "--write"]); assert r.returncode == 0, (x, r.stdout.decode()[-200:], r.stderr.decode()[-200:])
            outs.append(open(p, "rb").read())
        assert outs[0] == outs[1], "the order of the two board C drafts changes the result"
        _p, add = m.designators(GEN_C, [l6, pi], d, "c_desig")
        assert add[os.path.relpath(pi, RECS)] == {"R57"} and add[os.path.relpath(l6, RECS)] == set(), add


def t_item4_the_pi_button_reaches_u1_p1_3_with_its_pull_up_and_debounce():
    m = _M(); q = m.item4()
    assert abs(q["tau"] - 1.0e-3) < 1e-9 and q["t_release"] < 2e-3 and abs(q["i_press"] - 0.33e-3) < 0.01e-3
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c.py"); shutil.copy(GEN_C, p)
        assert _run([os.path.join(REC, "apply_gen_sch_c_pibtn.py"), p, "--write"]).returncode == 0
        t = open(p, encoding="utf-8").read()
        assert '"16": "PIJ2_A2", "17": "SPARE2"' in t and 'r("R57", "10k", "PIJ2_A2", "+3V3", "R", "C25804")' in t
        assert '"PIJ2_B2"' not in t and 'c("C27", "100n", "PIJ2_A2", "GND"' in t and '"ZEROIZE_HW", "PIJ2_A2", "SPARE2"' in t
        assert "R3 on board A" not in t, "the stale note on the PI lead survived"



def t_board_e_the_pack_return_composes_with_the_change_lists_round_at_every_prefix():
    """Board E's round in the change list's order (L4-POWER-ARCHITECTURE.md's table, d8dec31's cin last) is the script's E_ROUND, and
    this record's pack return applies after every prefix of it, before it, and before cin; it adds no designator."""
    m = _need_inputs()
    er = [m.draft(r, n, "e") for r, n in m.E_ROUND]; mine = _mine("e")
    assert m.e_round_page() == [os.path.basename(x) for x in er], "the change list's board E round moved"
    with tempfile.TemporaryDirectory() as d:
        for k in range(len(er) + 1):
            _p, res = m.compose_e(er[:k] + mine, d, "p%d" % k)
            assert all(v == "OK" for _s, v in res) and len(res) == k + 1, (k, res)
        p, res = m.compose_e(mine + er, d, "first")
        assert all(v == "OK" for _s, v in res) and len(res) == len(er) + 1, res
        compile(open(p, encoding="utf-8").read(), p, "exec")


def t_item1_round3_the_bound_holds_every_state_and_the_round2_draft_is_refused():
    """Record l9pwr's figures parsed (never typed): the drafted coolers reproduce L9P-F02 (-0.010 A at HIGH), the 70 % maximum
    holds every AP64500 and LM5176 slot converter at HIGH in every state at the step-up's 0.85 and at its low 0.80, the device rail
    is the same in every option; round 2's slot loads are refused by intent.rail itself and round 3's accepted."""
    m = _M(); P = m.l9pwr(); o = m.item1_r3(); V = m.V
    assert len(P["states"]) == 11 and P["r9"]["equal"] == "EQUAL" and P["f02"][0] == "L9P-F02" and P["f03"][0] == "L9P-F03"
    ap = [r for r in o["rows"] if r["part"].startswith("AP64500")]
    assert min(r["margin"]["a"] for r in ap) < 0 and abs(min(r["margin"]["a"] for r in ap) + 0.010) < 0.001, "L9P-F02 not reproduced"
    for r in o["rows"]:
        assert abs(r["I"]["a"] - r["printed"]) < 0.0006, r
        assert r["margin"]["cap"] > 0 and r["margin"]["cap_lo"] > 0 and r["margin"]["b"] > r["margin"]["cap"] > r["margin"]["a"], r
        assert r["margin"]["rel"] > 0, r
    allt = [x for x in o["dev"] if x["state"] == "PS-ALLTX"][0]
    assert allt["margin"] < 0 and abs(allt["drafted"] - allt["drawn"] - allt["u901"]) < 0.002, allt
    assert o["fixed"] > 0.5 and o["ipk"] < V["ap_ipk"][0], (o["fixed"], o["ipk"])
    rows = m.r3_slot_loads()
    assert [m.intent_says(pk, ld).split(" ")[0] for _t, ld, pk in rows] == ["accepted", "REFUSED", "accepted"], rows
    assert sum(rows[2][1].values()) <= rows[2][2], "round 3's slot loads over the declared peak"
    assert abs(m.item1()["a_vbat"] - P["r9"]["this"]) < 1e-9 and "eta_slot" not in m.F, "the flat 0.90 is still carried"


def t_item1_the_fan_row_still_reads_with_layer_7s_reader():
    """Record l7pwr's reader parses this draft's slot row with two expressions (l7pwr_fans_th1.py, read_rails); the round 3 row keeps
    their form, so that reader reads 0.33 A, 1.4 W, 0.85 and 5.0 V and the watts it derives stay consistent (0.33 x 5.0 - 1.4 > 0)."""
    fx = _mod(os.path.join(REC, "apply_gen_sch_b_fans12.py"), "fans12_under_test")
    row = fx._NEW_LOAD
    a = re.search(r'"U%d" % \(701 \+ 30 \* \(s - 1\)\): ([\d.]+),\s+# l8r2 \(E11-40\): the cooler fan\'s 12 V step-up, ([\d.]+) W of fan over ([\d.]+)', row)
    b = re.search(r"\(ASSUMPTION\) at ([\d.]+) V", row)
    assert a and b, row
    amps, watts, eta, volts = float(a.group(1)), float(a.group(2)), float(a.group(3)), float(b.group(1))
    assert abs(watts - _M().V["duty_max"] * _M().V["pfan"]) < 1e-9 and abs(amps - round(watts / eta / volts, 2)) < 1e-9 and amps * volts > watts


def t_item5_the_pack_returns_are_rails_that_intent_itself_accepts():
    """Each board's draft replaces GND's node by a rail returning the pack path's counted rail at the pack's 18 A with this board's
    half percent; intent.py evaluates the file's declarations and accepts them; every source and load is on GND on the committed
    netlist; record l9stk's finding reads as found ("board A none; board E none")."""
    m = _need_inputs()
    assert m.l9stk_rows()[1] == "board A none; board E none"
    with tempfile.TemporaryDirectory() as d:
        for letter, gen, net, ret in (("a", GEN_A, m.NET_A, "CELL+"), ("e", GEN_E, m.NET_E, "CELL_F")):
            p = os.path.join(d, letter + ".py"); shutil.copy(gen, p)
            assert _run([os.path.join(REC, "apply_gen_sch_%s_packrtn.py" % letter), p, "--write"]).returncode == 0
            t = open(p, encoding="utf-8").read()
            assert '_intent.node("GND"' not in t
            got = m.rail_calls(t, (ret, "GND"))
            assert got[ret][0] == "accepted" and got["GND"][0] == "accepted", got
            g = got["GND"][1]
            assert g["returns"] == ret and g["amps_peak"] == 18.0 and g["share"] == 0.005 and g["volts"] == 0.0, g
            pins = m.netlist_pins(os.path.join(ROOT, net))
            src = g["source"] if isinstance(g["source"], list) else [g["source"]]
            for ref in src + list(g["loads"]):
                assert any(str(n).lstrip("/") == "GND" for n in pins.get(ref, {}).values()), (letter, ref)


def t_item6_the_energy_chain_correction_is_idempotent_follows_the_decision_and_moves_no_verdict():
    """The apply script refuses while the register carries no ruled "(L9STK E)" decision; with one it checks, writes once, and a
    second run writes nothing; the corrected chain names no 2 oz on board E, names the widths track_current computes, and reads the
    same in energy_chain.check; a chain whose old text is not there exactly once is refused; the tree's chain is never written."""
    m = _need_inputs(); o = m.item6()
    before = _sha(CHAIN)
    with tempfile.TemporaryDirectory() as d:
        ch = os.path.join(d, "c.yaml"); shutil.copy(CHAIN, ch)
        reg = os.path.join(d, "r.yaml"); shutil.copy(os.path.join(TOOLS, "pcb_decisions.yaml"), reg)
        assert _run([FIX, "--chain", ch]).returncode == 3
        assert _run([FIX, "--chain", ch, "--registry", reg]).returncode == 3
        open(reg, "a", encoding="utf-8").write('  - n: 999\n    title: "Board E at 1 oz outer (L9STK E)"\n    status: ruled\n')
        r = _run([FIX, "--chain", ch, "--registry", reg]); assert r.returncode == 0 and b"CHECK OK" in r.stdout and _sha(ch) == _sha(CHAIN)
        r = _run([FIX, "--chain", ch, "--registry", reg, "--write"]); assert r.returncode == 0 and b"WRITTEN" in r.stdout
        once = open(ch, "rb").read()
        r = _run([FIX, "--chain", ch, "--registry", reg, "--write"]); assert r.returncode == 0 and b"ALREADY CORRECTED" in r.stdout
        assert open(ch, "rb").read() == once
        import yaml
        st = {s["id"]: s for s in yaml.safe_load(once)["stages"]}
        for sid, wid in (("DOCK_ENTRY", "%.2f mm on each of two 1 oz faces" % o["w25"][0]),
                         ("SHORE_INPUT", "%.2f mm on each of two 1 oz faces or %.2f mm on one" % o["w10"])):
            c = st[sid]["conductor"]
            assert "2 oz" not in str(c) and "1 oz" in c["what"] and wid in c["basis"], (sid, c)
        sys.path.insert(0, TOOLS)
        import energy_chain as ec
        a, b = ec.check(CHAIN, None), ec.check(ch, None)
        assert all(a.get(k) == b.get(k) for k in ("fails", "stage_fails", "derate_fails")) and a["checked"] == b["checked"]
        bad = os.path.join(d, "bad.yaml"); open(bad, "w", encoding="utf-8").write(open(CHAIN, encoding="utf-8").read().replace(
            "rating_a: 10.0, basis: \"gen_pcb_e3.py\"}", "rating_a: 10.0, basis: \"gen_pcb_e3.py \"}"))
        assert _run([FIX, "--chain", bad, "--registry", reg]).returncode == 3
    assert _sha(CHAIN) == before, "the tree's chain was written"
    assert o["a_672_two"] < 25.0 and max(o["dchs_1oz"]) < 10.0 <= min(o["dchs_2oz"]), "the two findings' arithmetic moved"
