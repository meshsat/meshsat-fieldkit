"""Layer 8 record l8r2 (MESHSAT-1357, 3 October 2026; v2/docs/records/l8r2/): the known engineering defects corrected at the desk
on printed parts, as release-guarded drafts: board B's coolers on a 12 V step-up (E11-40), VBUS20's over-voltage cut-off on board A
(S-111), PANEL_5V and board D's 3.3 V behind eFuses (L5R2-F03, F05), J_QMX and J_CAM on the JST PH land (L5R2-F04); round 3 (3 October
2026): item 1 re-decided on record l9pwr's L9P-F02 (the coolers' step-up kept with the modules' 70 % Fan_PWM maximum), the pack path's
return declared as a rail on boards A and E (record l9stk's finding), the energy chain's board E 2 oz texts corrected by an apply script;
round 4 (3 October 2026, the owner's focused check of L9P-F02): the 70 % maximum withdrawn, slots 1 and 3 on slot 2's LM5176 stage
(apply_gen_sch_a_slotlm.py), the coolers at full speed, every figure of the check held to its stated verdict.

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
MINE = {"a": ["d8v3", "vbus20ov", "packrtn", "slotlm", "fb01"], "b": ["fans12", "panel5v", "ph4", "rt500"], "c": ["pibtn"], "e": ["packrtn"]}
CHECK_FILED = os.path.join(REC, "checks", "astra-check-l9pf02-1.md")
RECHECK_FILED = os.path.join(REC, "checks", "astra-check-l9pf02-2.md")
HELD_FAN = {p: os.path.join(ROOT, "v2", "vendor", "fans", "held", "sanyo-denki-san-ace-c1152b001-2510-p%s.pdf" % p) for p in ("0362", "0616", "0623", "0633")}
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
              "round 3 SELECTED (SESSION): (a) with the modules' 70 % Fan_PWM maximum", "REFUSED (intent: rail +5V_S1 declares a 5.00 A peak",
              "SELECTED (SESSION): slots 1 and 3 on the LM5176 stage", "slotlm then L4-E11's charger: REFUSED, as expected",
              "the charger then slotlm: OK", "in either order give one generator: YES", "A SLOTS DRAWN", "VERDICT: NOT A MARGIN",
              "POSSIBLE, NOT ESTABLISHED", "the same generator either way: YES", "not a temperature of the drawn stage",
              "A FB01  DRAWN", "NOT claimed as a bound on the drawn stage", "5.0019 to 5.1744 V",
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
    late = [m.draft(r, n, "a") for r, n in m.AFTER_CHARGER]; first = [x for x in mine if x not in late]
    charger = [x for x in pa if x.endswith("_charger.py")]
    with tempfile.TemporaryDirectory() as d:
        for tag, seq in (("fwd", pa + l8), ("rev", first + pa + l8[:2] + late)):
            p, res = m.compose(GEN_A, seq, d, tag, mainpb_last=True)
            assert all(v.startswith("OK") for _s, v in res) and len(res) == len(seq) + 1, (tag, res)
            assert "(R248, C247)" in res[-1][1], res[-1]
            compile(open(p, encoding="utf-8").read(), p, "exec")
        r12 = [x for x in pa if x.endswith("_r12.py")]
        for s in pa:
            p = os.path.join(d, "alone_" + os.path.basename(s)); shutil.copy(GEN_A, p)
            for x in first + ([] if s in charger else late) + (r12 if s.endswith("_bank.py") else []):
                assert _run([x, p, "--write"]).returncode == 0, x
            r = _run([s, p, "--write"]); assert r.returncode == 0, "%s refused after l8r2's drafts: %s" % (s, r.stderr.decode()[-200:])
        _p, res = m.compose(GEN_A, l8[::-1], d, "l8rev")
        assert all(v == "OK" for _s, v in res), res
        # round 4's order constraint: slotlm rewrites the VBAT entry L4-E11's charger anchors on, so the charger goes first
        _p, res = m.compose(GEN_A, late + charger, d, "o1"); assert res[-1][1].startswith("REFUSED"), res
        _p, res = m.compose(GEN_A, charger + late, d, "o2"); assert all(v == "OK" for _s, v in res), res
        pk = [x for x in mine if x.endswith("_packrtn.py")]
        p1, r1 = m.compose(GEN_A, pk + late, d, "pk1"); p2, r2 = m.compose(GEN_A, late + pk, d, "pk2")
        assert all(v == "OK" for _s, v in r1 + r2) and open(p1, "rb").read() == open(p2, "rb").read(), "packrtn and slotlm differ by order"


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
        slot = {"%s%d" % (p, b + k) for b in (500, 530) for p, ks in (("U", (1,)), ("Q", range(1, 5)), ("L", (1,)), ("D", (1, 2)),
                                                                       ("R", range(1, 13)), ("C", range(1, 20))) for k in ks}
        assert addA["l8r2/apply_gen_sch_a_slotlm.py"] == slot, sorted(addA["l8r2/apply_gen_sch_a_slotlm.py"] ^ slot)
        assert addA["l8r2/apply_gen_sch_a_fb01.py"] == set()
        pE, addE = m.designators_e(d)
        assert addE["l8r2/apply_gen_sch_e_packrtn.py"] == set() and not m.duplicates(open(pE, encoding="utf-8").read())
        fans = {"%s%d" % (p, 700 + 30 * (s - 1) + k) for s in (1, 2, 3) for p, ks in (("U", (1, 2)), ("L", (1,)), ("Q", (1, 2)), ("R", range(1, 13)), ("C", range(1, 11))) for k in ks}
        assert addB["l8r2/apply_gen_sch_b_fans12.py"] == fans
        assert addB["l8r2/apply_gen_sch_b_panel5v.py"] == {"U901", "R901", "R902", "R903", "R904", "R905", "C901", "C902"}
        assert addB["l8r2/apply_gen_sch_b_ph4.py"] == set() and addB["l8gnd/apply_gen_sch_b_gnd002.py"] == set()
        assert addB["l8r2/apply_gen_sch_b_rt500.py"] == set()
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
    bad = chk.fixture("a").replace(b'(node (ref "R535") (pin "2"))', b'')
    assert chk.judge("a", chk.read_netlist(bad))[0] == "FAIL", "slot 3's ISNS shunt off +5V_S3 is not refused"
    bad = chk.fixture("a").replace(b'(ref "R41") (value "10k 0.1%")', b'(ref "R41") (value "10k 1%")')
    assert chk.judge("a", chk.read_netlist(bad))[0] == "FAIL", "a divider resistor left at 1 % is not refused"


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
              "apply_energy_chain_e1oz.py", "ASM-002", "1s, L9P-F02 focused check", "apply_gen_sch_a_slotlm.py", "WITHDRAWN",
              "UNRESOLVED", "CONDITIONAL", "1t, answers to the collaborator's check", "5.515 A", "apply_gen_sch_b_rt500.py",
              "POSSIBLE, NOT ESTABLISHED", "3.44 W", "1u, answers to the recheck", "apply_gen_sch_a_fb01.py", "6.6 A", "5.0019"):
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
    assert [m.intent_says(pk, ld).split(" ")[0] for _t, ld, pk in rows] == ["accepted", "REFUSED", "accepted", "accepted", "accepted"], rows
    assert sum(rows[2][1].values()) <= rows[2][2], "round 3's slot loads over the declared peak"
    assert abs(m.item1()["a_vbat"] - P["r9"]["this"]) < 1e-9 and "eta_slot" not in m.F, "the flat 0.90 is still carried"


def t_item1_the_fan_row_still_reads_with_layer_7s_reader():
    """Record l7pwr's reader parses this draft's slot row with two expressions (l7pwr_fans_th1.py, read_rails); round 5's row keeps
    their form, so that reader reads 0.69 A, 2.75 W, 0.80 and 5.0 V (the envelope) and the watts it derives stay consistent."""
    fx = _mod(os.path.join(REC, "apply_gen_sch_b_fans12.py"), "fans12_under_test")
    row = fx._NEW_LOAD
    a = re.search(r'"U%d" % \(701 \+ 30 \* \(s - 1\)\): ([\d.]+),\s+# l8r2 \(E11-40\): the cooler fan\'s 12 V step-up, ([\d.]+) W of fan over ([\d.]+)', row)
    b = re.search(r"\(ASSUMPTION\) at ([\d.]+) V", row)
    assert a and b, row
    amps, watts, eta, volts = float(a.group(1)), float(a.group(2)), float(a.group(3)), float(b.group(1))
    assert abs(watts - _M().V["fan_env"]) < 1e-9 and abs(eta - _M().V["eta_lo"]) < 1e-9 and abs(amps - round(watts / eta / volts, 2)) < 1e-9 and amps * volts > watts


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


def t_round4_the_focused_check_holds_its_verdicts():
    """Round 4 (the owner's L9P-F02 questions): round 3's +0.129 A is a HIGH state at the nominal 5.1 V and reads negative at the
    AP64500's least output with the rail's drop; 0.019 A is a declaration's; the fan's input at 70 % is bracketed around round 3's
    linear bound (so it bounds nothing); the AP64500 is over 5 A in every unenforced state and over +125 C at C1's air in every HIGH
    option; the pick at 70 % moves more air than the approved basis's fan; the LM5176 stage holds every state with margin, its hottest
    FET under +150 C on the sheet's copper; the drafts carry the figures the check derives."""
    m = _M(); o = m.item1_r4(); V = m.V
    c1 = {lab.split(" (")[0]: fig for lab, fig, _s, _b in o["c1"]}
    assert abs(c1["+0.129 A"] - 0.129) < 0.0006 and abs(c1["+0.019 A"] - 0.019) < 0.0006 and c1["the same state at the least voltage"] < 0
    c2 = o["c2"]
    assert c2["law"][2] < c2["linear"] < c2["chord"][0], "the linear bound is no longer inside the bracket"
    assert c2["room_least"] < c2["law"][0] and c2["start_slot_w"] > 8.0
    over = [i2 > 5.0 for (_st, _p, pce, _f, _w), (_i1, i2, _i3) in zip(o["c3"], o["c3_i"]) if "high" in pce]
    assert over and all(over), o["c3_i"]
    assert all(o["lm_limit"] - i3 > 0.5 for _i1, _i2, i3 in o["c3_i"]), o["c3_i"]
    b1 = o["b1"]   # round 5, B1: the drawn frequency, and a start that may reach the HS limit and need not
    assert abs(b1["fsw"] - 100000.0 / 68.0 * 1e3) < 1 and b1["pk_nom"] < V["ap_ipk"][0] < b1["pk_lo"]
    assert [r for r in o["c3"] if r[0].startswith("firmware failure, PWM block")][0][4] == o["env"]["w"], "the last duty is not up to 100 %"
    least = {tag: (i, tl) for tag, i, tl in o["fig24_least"]}
    assert all(tl is None or tl < o["air"] for _i, tl in least.values()) and least["(b) no cooler on the slot rail"][1] is not None
    hi = [j for j in o["junction"] if not j[0].startswith("PLAN")]
    assert all(tj > V["ap_tj"][0] for _t, _v, _i, _e, _l, tj in hi) and o["ap_i125"] < 4.0
    assert o["fig24"]["air"] < 4.871
    c4 = o["c4"]
    assert c4["p70_floor"] > c4["rep_pa"] + 10 and c4["q100_needed"] < V["pq100"][1], c4
    cw = o["corr_worst"]   # rounds 5 and 6, B2: the steady envelope, the qualified start and a degraded fan, all under the declaration
    assert max(cw) <= V["slot_peak"] < o["lm_limit"] and cw[0] < o["lm_limit"] - 1.5 and o["lm_limit"] - max(cw) > 0.5
    assert abs(o["lm_limit"] - 0.043 / 0.00606) < 1e-9 and o["peak_need"] == cw[1] and o["start_calc"] < V["start_bound"]
    assert o["slot2_start"] < V["slot_peak"] and o["v"]["hi_lm"] < V["cm5_vin"][1] and o["v"]["least_lm"] > 5.0 and o["v"]["load_lm"] > 4.9
    rth = [r for _i, r in o["matrix_rth"]]
    assert rth == sorted(rth, reverse=True) and abs(o["matrix_rth"][-1][0] - V["slot_peak"]) < 1e-12 and 36.0 < rth[-1] < 37.5, rth
    assert abs(o["env"]["branch"] - V["fan_env"] / V["eta_lo"]) < 1e-12 and o["env"]["branch"] < 3.44 < o["env"]["branch"] + 0.01
    assert o["fet_tj"][1] < V["csd"][3] - 25 and o["fet_tj"][2] > V["csd"][3] and V["csd"][3] - 25 < o["fet_rr"][1] < V["csd"][3], (o["fet_tj"], o["fet_rr"])
    assert o["peak_need"] <= V["slot_peak"] == 6.6 and abs(o["entry"] - 2.60) < 0.005
    assert o["decl4"][2] == "accepted" and o["decl4"][1] == V["slot_peak"] == o["decl4"][3] == o["decl4"][4] and abs(o["fan_row"] - 0.69) < 1e-9
    assert o["lm_window"]["hi"] > V["cm5_vin"][1] > o["lm_window"]["hi01"] and o["lm_window"]["lo01"] > o["lm_window"]["lo"]
    sl = open(os.path.join(REC, "apply_gen_sch_a_slotlm.py"), encoding="utf-8").read()
    for s in ("%.3f A" % o["peak_need"], "%.3f V" % o["v"]["load_lm"], "%.3f A" % cw[0], "7.096 A", "PEAK = 6.6", "ENTRY = 2.60"):
        assert s in sl, s
    fx = _mod(os.path.join(REC, "apply_gen_sch_b_fans12.py"), "fans12_r4_under_test")
    assert ", 6.6, " in fx._NEW_PEAK and "70 %" not in fx._NEW_LOAD and "70 %" not in fx._NEW_FAN.split("ROUND 4")[1]
    src = o["src"]
    assert src["c1_air"] == 50.0 and src["h2"][2] == 0.873 and src["sunon"] == (3.7, 0.11) and src["dts"][2] == 41566 and src["pce_pd"] and src["gate"]


def t_round4_the_catalogue_figures_read_from_the_held_pages():
    """The cooler's figures round 4 types (the record's F) are the maker's words on the held catalogue pages (fetched by the record's
    fetch_held_back.py; skipped where they are not held)."""
    for p in HELD_FAN.values():
        need(p, "a held San Ace catalogue page (fetch_held_back.py)")
    txt = {k: " ".join(subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True).stdout.decode().split()) for k, p in HELD_FAN.items()}
    m = _M(); (r100, r25) = m.V["fan_rows"]
    assert re.search(r"100 0\.17 2\.0 13700 0\.38 13\.4 210 0\.84 44 9WPA0412P6G001 12 10\.8 to 13\.2 25 0\.03 0\.36 3000 0\.07 2\.5 9\.8", txt["0362"]), "p.362's rows"
    assert r100 == (100, 0.17, 2.0, 13700, 0.38, 210.0) and r25 == (25, 0.03, 0.36, 3000, 0.07, 9.8)
    assert "When control terminal is open, speed is the same as at 100% duty cycle" in txt["0362"]
    assert "Models without ratings for 0% PWM duty cycle have zero speed at 0%" in txt["0362"]
    assert "current several times the rated current may flow" in txt["0633"]
    assert "the coil current is cut off at regular cycles" in txt["0616"]
    assert "VIH =4.75 to 5.25 V" in txt["0623"] and "VIL= 0 to 0.4 V" in txt["0623"] and "The input signal voltage and the frequency differ with models" in txt["0623"]


def t_round5_the_rt_draft_sets_500_khz_and_composes_with_layer_6():
    """Round 5 (O-20): the RT draft changes buck33's RT from 68 k to 200 k (DS41979 Eq. 7: 1470.6 kHz to 500 kHz) and its docstring
    sentence, adds no designator or net, and composes with record l6r2's board B drafts in either order into one generator."""
    m = _need_inputs()
    rt = os.path.join(REC, "apply_gen_sch_b_rt500.py")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "b.py"); shutil.copy(GEN_B, p)
        assert _run([rt, p, "--write"]).returncode == 0
        before, after = open(GEN_B, encoding="utf-8").read().splitlines(), open(p, encoding="utf-8").read().splitlines()
        import difflib
        changed = [l for l in difflib.unified_diff(before, after, n=0) if l[:1] in "+-" and not l.startswith(("+++", "---"))]
        assert len([l for l in changed if l.startswith("-")]) == 2, changed
        t2 = "\n".join(after)
        assert '"200k 1% (RT: 500 kHz)"' in t2 and '"68k (RT: 500 kHz)"' not in t2
        l6 = [os.path.join(ROOT, x) for x in m.L6_B]
        p1, r1 = m.compose(GEN_B, [rt] + l6, d, "x1"); p2, r2 = m.compose(GEN_B, l6 + [rt], d, "x2")
        assert all(v == "OK" for _s, v in r1 + r2) and open(p1, "rb").read() == open(p2, "rb").read(), (r1, r2)
    assert abs(100000.0 / 68.0 - 1470.588) < 0.001 and abs(100000.0 / 200.0 - 500.0) < 1e-9


def t_round5_the_collaborators_check_is_filed_as_received():
    """The collaborator's check of round 4 (cx38) is filed under checks/ unchanged: its first line, its verdict, its three blockers."""
    need(CHECK_FILED, "the collaborator's check as filed")
    c = open(CHECK_FILED, encoding="utf-8").read()
    assert c.startswith("accepted: no\n") and "L9P-F02: NOT CONFIRMED" in c
    for b in ("- B1: Correct the AP64500 timing mismatch", "- B2: Correct the replacement's load declarations", "- B3: Complete the conditional acceptance package"):
        assert b in c, b


def t_round6_the_divider_draft_corrects_the_window_and_composes_in_every_order():
    """Round 6 (F5-03): the divider draft sets both resistors of slot 2's and the device rail's stages (and slots 1 and 3's, where
    slotlm is drawn) at 0.1 % through a helper keyword whose default keeps every other stage; with the pack return and slotlm the
    three drafts give one generator in all six orders; the window is inside the CM5's 4.75 to 5.25 V."""
    fb = os.path.join(REC, "apply_gen_sch_a_fb01.py"); sl = os.path.join(REC, "apply_gen_sch_a_slotlm.py"); pk = os.path.join(REC, "apply_gen_sch_a_packrtn.py")
    import itertools
    outs = set()
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "alone.py"); shutil.copy(GEN_A, p)
        assert _run([fb, p, "--write"]).returncode == 0
        a = open(p, encoding="utf-8").read()
        assert a.count('rfb_val="10k 0.1%", rfb_tol="0.1%",') == 2 and 'r(rft, rfb_top + " " + rfb_tol, vout, N("FB"));' in a and 'rfb_tol="1%",' in a
        for k, order in enumerate(itertools.permutations((pk, sl, fb))):
            q = os.path.join(d, "o%d.py" % k); shutil.copy(GEN_A, q)
            for x in order:
                r = _run([x, q, "--write"]); assert r.returncode == 0, (order, r.stderr.decode()[-200:])
            outs.add(open(q, "rb").read())
        assert len(outs) == 1, "the order of packrtn, slotlm and fb01 changes the result"
        assert list(outs)[0].decode().count('rfb_val="10k 0.1%", rfb_tol="0.1%",') == 4
    m = _M(); o = m.item1_r4(); V = m.V
    lo = 0.788 * (1 + 53.6 * 0.999 / (10 * 1.001)) - 25e-9 * 53.6e3; hi = 0.812 * (1 + 53.6 * 1.001 / (10 * 0.999)) + 25e-9 * 53.6e3
    assert abs(o["v"]["least_lm"] - lo) < 1e-12 and abs(o["v"]["hi_lm"] - hi) < 1e-12 and 4.75 < lo and hi < 5.25 and 0.812 * (1 + 53.6 * 1.01 / 9.9) > 5.25


def t_round6_the_recheck_is_filed_as_received():
    need(RECHECK_FILED, "the collaborator's recheck as filed")
    c = open(RECHECK_FILED, encoding="utf-8").read()
    assert c.startswith("accepted: no\n") and "L9P-F02 RECHECK: NOT CLOSED" in c and "- F5-03: Correct both divider resistors" in c


def t_closing_check_c4_3_names_the_measured_steady_current():
    """The coordinator's closing check (MINOR): C4-3's duration criterion is taken on the steady current measured on the specimen plus
    a stated tolerance; the desk's 0.7013 A at 4.9019 V is printed as the expected value; no threshold names round 5's 0.712 A."""
    page = open(PAGE, encoding="utf-8").read()
    c43 = page[page.index("- **C4-3, the actual cooler chain"):page.index("- **C4-4, the maker's answer")]
    assert "I_SS" in c43 and "10 % of I_SS or 0.05 A, the larger" in c43 and "not the threshold" in c43 and "0.712" not in c43
    m = _M(); o = m.item1_r4(); V = m.V
    assert abs(V["fan_env"] / V["eta_lo"] / o["v"]["load_lm"] - 0.7013) < 5e-5
    out = open(OUT, encoding="utf-8").read()
    assert "0.7013 A at 4.9019 V" in out and "expected values, not the threshold" in out


# ---------------------------------------------------------------------------------------------------------------- rounds 7 and 8
GNDRET = os.path.join(REC, "l8r2_gndret.py")
GNDRET_OUT = os.path.join(REC, "l8r2_gndret.out")
GNDCHK = os.path.join(REC, "check_gndret_netlist.py")
L9_DRAFT = os.path.join(REC, "inputs", "l9t5-apply_gen_sch_b_iocbuck-841e6c7e.py")
L9_DRAFT_A = os.path.join(REC, "inputs", "l9t5-apply_gen_sch_a_iocbuck-841e6c7e.py")
R7 = {n: os.path.join(REC, "apply_gen_sch_b_%s.py" % n) for n in ("gndret", "fandec")}
R8 = {"b": os.path.join(REC, "apply_gen_sch_b_gndrtn.py"), "a": os.path.join(REC, "apply_gen_sch_a_gndrtn.py")}
B_ROUND = [os.path.join(RECS, "l8gnd", "apply_gen_sch_b_gnd002.py")] + [os.path.join(REC, "apply_gen_sch_b_%s.py" % n) for n in ("fans12", "panel5v", "ph4", "rt500")]
B_FULL = B_ROUND + [R7["fandec"], R7["gndret"], R8["b"], L9_DRAFT]
_R8 = {}


def _gn():
    return _mod(os.path.join(RECS, "l8p", "gen_netlist.py"), "l8p_gen_netlist_under_test")


def _b_copy(d, tag, seq, edit=None):
    p = os.path.join(d, tag + ".py"); shutil.copy(GEN_B, p)
    for x in seq:
        r = _run([x, p, "--write"]); assert r.returncode == 0, (os.path.basename(x), r.stderr.decode()[-300:])
    if edit:
        t0 = open(p, encoding="utf-8").read(); t1 = edit(t0); assert t1 != t0, "the mutation changed nothing"
        open(p, "w", encoding="utf-8").write(t1)
    return p


def _b_run(d, tag, seq, edit=None):
    """(return code, the generator's log, the recorded table or None, the netlist bytes or None) of a composed scratch generator"""
    p = _b_copy(d, tag, seq, edit); net = os.path.join(d, tag + ".net")
    rc, log, table = _gn().run(p, net, "pcb-b-compute")
    return rc, log, table, (open(net, "rb").read() if rc == 0 else None)


def _a_run(d, tag, with_return=True, first=False):
    """board A composed in L4-E9's order with Layer 9's draft, the return draft last or first, mainpb LAST, then Layer 6's table"""
    m = _mod(GNDRET, "l8r2_gndret_under_test")
    seq = [os.path.join(ROOT, "v2", "docs", "records", r, "apply_gen_sch_a_%s.py" % n) for r, n in m.ROUND_A] + [L9_DRAFT_A]
    if with_return:
        seq = ([R8["a"]] + seq) if first else (seq + [R8["a"]])
    p, err = m.compose_a(seq, d, tag); assert err is None, err
    net = os.path.join(d, tag + ".net")
    rc, log, table = _gn().run(p, net, "pcb-a-power")
    assert rc == 0 and table["intent_written"] and not table["unplaced"], log[-300:]
    return table, open(net, "rb").read()


def _composed():
    """both boards composed once with every draft (cached): the board B table and netlist, the board A netlist, the figures, the totals"""
    if not _R8:
        for p in list(R7.values()) + list(R8.values()) + [GNDCHK, GNDRET, L9_DRAFT, L9_DRAFT_A] + B_ROUND:
            need(p, "a file of record l8r2's rounds 7 and 8")
        m = _mod(GNDRET, "l8r2_gndret_under_test")
        for p in list(m.SHEETS.values()) + [m.BUDGET, m.L9T5_OUT, m.V3, m.CASES, m.L4E12_OUT, m.L9STK_PAGE, m.ENVELOPE, m.CHAIN]:
            need(os.path.join(ROOT, p), "an input of rounds 7 and 8")
        with tempfile.TemporaryDirectory() as d:
            rc, log, tb, nb = _b_run(d, "b_full", B_FULL)
            assert rc == 0 and tb["intent_written"] and not tb["unplaced"], log[-300:]
            _ta, na = _a_run(d, "a_full")
        F = m.figures(); rows = m.budget(m.BUDGET)["PS-ALLTX"]
        cdev = rows["S1"]["least"] + rows["S2"]["least"] + rows["S3"]["least"] + F["cdev_u7"] + F["cdev_u601"]
        _R8.update(tb=tb, nb=nb, na=na, F=F, cdev=cdev, upper=tb["intent"]["rails"]["GND"]["amps_peak"])
    return _R8


def t_round7_the_old_state_stops_on_the_typed_return_and_the_correction_runs_to_its_end():
    """RSM-01, reproduced and corrected: board B's round in L4-E9's order stops on GND's typed 21.0 A after fans12 (21.51 A of loads),
    without Layer 9's draft and with it; with the gndret draft alone it stops on fans12's unclassed capacitors (the second stop);
    with both of round 7's drafts it runs to its end and the return's figures are the leads' sums."""
    for p in list(R7.values()) + [GNDCHK, L9_DRAFT] + B_ROUND:
        need(p, "a file of record l8r2's round 7")
    chk = _mod(GNDCHK, "l8r2_gndchk_under_test")
    with tempfile.TemporaryDirectory() as d:
        for tag, seq in (("old", B_ROUND), ("old_l9", B_ROUND + [L9_DRAFT])):
            rc, log, _t, _n = _b_run(d, tag, seq)
            assert rc != 0 and "rail GND declares a 21.00 A peak and its loads sum to 21.51 A" in log, (tag, log[-300:])
        rc, log, _t, _n = _b_run(d, "half", B_ROUND + [R7["gndret"]])
        assert rc != 0 and "C704 -> U701.9" in log and "carries no class" in log, log[-300:]
        rc, log, table, net = _b_run(d, "new", B_ROUND + [R7["fandec"], R7["gndret"]])
        assert rc == 0 and table["intent_written"], log[-300:]
        g = table["intent"]["rails"]["GND"]
        assert (g["amps_typ"], g["amps_peak"]) == (13.3, 26.4) and g["source"] == ["J_5V_S1", "J_5V_S2", "J_5V_S3", "J_5V_DEV", "J_54V"], g
        assert abs(sum(g["loads"].values()) - 22.113) < 1e-9 and g["loads"]["R12"] == 0.6 and "UPPER BOUND" in g["note"], g
        assert chk.judge(chk.read_netlist(net), table["intent"])[0] == "DRAWN"
        rc, log, table, net = _b_run(d, "new_l9", B_ROUND + [R7["fandec"], R7["gndret"], L9_DRAFT])
        g = table["intent"]["rails"]["GND"]
        assert rc == 0 and g["amps_peak"] == 27.9108 and g["amps_typ"] == 13.3 and g["source"][-2:] == ["J_5V_IOC", "J_54V"], (rc, g)
        assert chk.judge(chk.read_netlist(net), table["intent"])[0] == "DRAWN"


def t_round7_each_draft_is_guarded_and_composes_with_layer_9s_draft_in_any_order():
    for name, s in R7.items():
        need(s, "a draft of round 7")
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "b.py"); shutil.copy(GEN_B, p); before = _sha(p)
            assert _run([s, p]).returncode == 0 and _sha(p) == before, "%s --check wrote or refused" % name
            assert _run([s, p, "--write"]).returncode == 0 and _sha(p) != before
            compile(open(p, encoding="utf-8").read(), p, "exec")
            r = _run([s, p, "--write"]); assert r.returncode == 3 and b"already applied" in r.stderr, r.stderr
            before = _sha(GEN_B); r = _run([s, GEN_B, "--write"])
            assert r.returncode == 3 and b"NOT RELEASED" in r.stderr and _sha(GEN_B) == before, "%s wrote the tree's generator" % name
    with tempfile.TemporaryDirectory() as d:
        a, b = R7["fandec"], R7["gndret"]
        orders = [B_ROUND + [a, b, L9_DRAFT], B_ROUND + [L9_DRAFT, a, b], [b, a] + B_ROUND + [L9_DRAFT], [b] + B_ROUND[::-1] + [a, L9_DRAFT]]
        outs = [open(_b_copy(d, "o%d" % i, seq), "rb").read() for i, seq in enumerate(orders)]
        assert len(set(outs)) == 1, "the order of board B's drafts changes the generator"
        t = outs[0].decode()
        assert t.count('["J_5V_S1", "J_5V_S2", "J_5V_S3", "J_5V_DEV", "J_5V_IOC"], loads=_GND_LOADS') == 1 and t.count("def _gnd_return(") == 1
        assert '_intent.rail("GND", 0.0, 10.0, 21.0' not in t and t.count('_intent.rail("GND"') == 1


def t_round7_the_return_is_derived_and_a_typed_figure_or_a_missed_lead_is_refused():
    """Not a larger typed number: the same draft on the committed generator gives 22.23 A; the old text with 21.0 simply raised runs
    and FAILS the check; a lead left off the return, a lead reversed on the netlist and a lead whose rail is elsewhere are refused."""
    chk = _mod(GNDCHK, "l8r2_gndchk_under_test")
    full = B_ROUND + [R7["fandec"], R7["gndret"], L9_DRAFT]

    def sub1(old, new):
        def f(t):
            assert t.count(old) == 1, (t.count(old), old)
            return t.replace(old, new)
        return f
    with tempfile.TemporaryDirectory() as d:
        rc, _log, table, net = _b_run(d, "alone", [R7["gndret"]])
        g = table["intent"]["rails"]["GND"]
        assert rc == 0 and (g["amps_typ"], g["amps_peak"]) == (13.3, 22.23) and abs(sum(g["loads"].values()) - 20.343) < 1e-9, g
        nl0 = chk.read_netlist(open(os.path.join(ROOT, "v2", "ecad", "pcb-b-compute-b19", "out", "pcb-b-compute.net"), "rb").read())
        import json as _json
        it0 = _json.load(open(os.path.join(ROOT, "v2", "ecad", "pcb-b-compute-b19", "out", "pcb-b-compute-intent.json"), encoding="utf-8"))
        assert chk.judge(nl0, it0)[0] == "NOT DRAWN", "the committed board does not read NOT DRAWN"
        rc, _log, table, net = _b_run(d, "raised", B_ROUND + [R7["fandec"], L9_DRAFT],
                                      sub1('_intent.rail("GND", 0.0, 10.0, 21.0, ', '_intent.rail("GND", 0.0, 10.0, 30.0, '))
        v, lines = chk.judge(chk.read_netlist(net), table["intent"])
        assert rc == 0 and v == "FAIL" and any(l.startswith("R2 ") for l in lines) and any("J_54V" in l for l in lines), (rc, v, lines)
        rc, _log, table, net = _b_run(d, "no54", full, sub1('_srcs = list(leads) + ["J_54V"]', "_srcs = list(leads)"))
        v, lines = chk.judge(chk.read_netlist(net), table["intent"])
        assert rc == 0 and v == "FAIL" and any(l.startswith("R1 J_54V") for l in lines), (v, lines)
        rc, log, _t, _n = _b_run(d, "s9", full, sub1('6.6, "J_5V_S%d" % _n, loads=_SLOT_LOADS(_n)', '6.6, "J_5V_S%d" % (9 if _n == 2 else _n), loads=_SLOT_LOADS(_n)'))
        assert rc != 0 and "do not each carry exactly one arriving rail" in log, log[-300:]
        rc, log, _t, _n = _b_run(d, "over", full, sub1('    "U%d03" % s: 2.2, ', '    "U%d03" % s: 4.2, '))
        assert rc != 0 and "rail +5V_S1 declares a 6.60 A peak and its loads sum to 7.34 A" in log, log[-300:]
        rc, _log, table, net = _b_run(d, "good", full)
        assert rc == 0 and chk.judge(chk.read_netlist(net), table["intent"])[0] == "DRAWN"
        a, b = b'(node (ref "J_5V_S2") (pin "1"))', b'(node (ref "J_5V_S2") (pin "2"))'
        assert net.count(a) == 1 and net.count(b) == 1
        swapped = net.replace(a, b"\x00").replace(b, a).replace(b"\x00", b)
        v, lines = chk.judge(chk.read_netlist(swapped), table["intent"])
        assert v == "FAIL" and any(l.startswith("R1 J_5V_S2 is named a return lead and is none") for l in lines), (v, lines)
        v, lines = chk.judge(chk.read_netlist(net.replace(b' (node (ref "R12") (pin "2"))', b"", 1)), table["intent"])
        assert v == "FAIL" and any(l.startswith("R3 ") and "R12" in l for l in lines), (v, lines)


def t_round8_the_worst_case_is_found_not_sampled():
    """The recheck V3's blocker. On C-DEV rev 1 as drawn, round 7's six sampled cases put a 5 V lead's pin 2 under its printed 10 A;
    the maximum over every vertex of the contact-resistance box is over it. A judgment on the sampled figure passes and is wrong:
    this test fails on that old state. The enumeration is held to an independent sum for the recheck's corner and, on a small
    network, to a brute-force walk of every raw vertex."""
    import itertools
    c = _composed(); m = _mod(GNDRET, "l8r2_gndret_under_test"); F = c["F"]
    TH = F["t_e5"]; conds = m.conductors(F, TH, True); bx = m.box(F)
    assert abs(c["cdev"] - F["v3_total"]) < 2e-3, (c["cdev"], F["v3_total"])
    old = m.sampled_round7(c["cdev"], conds, F)
    ext, shift, nst, raw = m.extremes(c["cdev"], conds, bx)
    assert old["VH"] <= F["vh_a16"] < ext["VH"][0], "the sampled figure (%.4f A) is not the state the recheck refused, or the enumeration (%.4f A) misses its corner" % (old["VH"], ext["VH"][0])
    assert old["RIB"] < ext["RIB"][0] and ext["RIB"][0] > F["cab_a"], (old["RIB"], ext["RIB"][0])
    assert raw == 4 ** 23 and nst == 21 * 3 * 171, (raw, nst)
    # the recheck's corner by an independent sum: J_5V_IOC's contacts at 0, every other VH contact at 20 mOhm, every IDC contact at 20 mOhm
    r16 = 1.72e-8 * 0.15 / 1.25e-6 * (1 + 0.00393 * (TH - 20)) * 1e3; r18 = 1.72e-8 * 0.15 / 0.83e-6 * (1 + 0.00393 * (TH - 20)) * 1e3
    rr = 237.0 * 0.08 * (1 + 0.00393 * (TH - 20))
    G = 1 / r16 + 4 / (r16 + 40.0) + 1 / (r18 + 40.0) + 17 / (rr + 40.0)
    corner = c["cdev"] / G / r16
    assert abs(corner - ext["VH"][0]) < 1e-9 and abs(corner - F["v3_ioc"]) < 2e-3, (corner, ext["VH"][0], F["v3_ioc"])
    assert "J_5V_IOC" in ext["VH"][1], ext["VH"][1]
    # a small network, every raw vertex walked: two leads of one make, one odd lead, two ribbon conductors
    small = [("A", "VH", 1, 2.0), ("B", "VH", 1, 2.0), ("C", "VH18", 1, 3.0), ("R", "RIB", 2, 20.0)]
    lohi = {"VH": (0.0, 20.0), "VH18": (0.0, 20.0), "RIB": (0.0, 20.0)}
    flat = [(n, k, wr) for n, k, cnt, wr in small for _ in range(cnt)]
    best = {}
    for combo in itertools.product(*[[(a, b) for a in lohi[k] for b in lohi[k]] for _n, k, _w in flat]):
        g = [1.0 / (wr + a + b) for (_n, _k, wr), (a, b) in zip(flat, combo)]
        for (n_, k_, _wr), gi in zip(flat, g):
            best[k_] = max(best.get(k_, 0.0), 10.0 * gi / sum(g))
    e2, _s2, _n2, raw2 = m.extremes(10.0, small, lohi)
    assert raw2 == 4 ** 5 and all(abs(e2[k][0] - best[k]) < 1e-12 for k in best), (e2, best)
    C = m.classes_of(small, lohi); an, _sh = m.analytic(10.0, C)
    assert all(abs(a - e2[cl["kind"]][0]) < 1e-12 for a, cl in zip(an, C))


def t_round8_the_return_drafts_are_guarded_and_compose_on_both_boards():
    chk = _mod(GNDCHK, "l8r2_gndchk_under_test"); c = _composed()
    for board, gen in (("b", GEN_B), ("a", GEN_A)):
        s = R8[board]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "g.py"); shutil.copy(gen, p)
            if board == "b":
                r = _run([s, p, "--write"]); assert r.returncode == 3 and b"apply_gen_sch_b_gndret.py is not applied" in r.stderr, r.stderr
                assert _run([R7["gndret"], p, "--write"]).returncode == 0
            before = _sha(p)
            assert _run([s, p]).returncode == 0 and _sha(p) == before
            assert _run([s, p, "--write"]).returncode == 0 and _sha(p) != before
            compile(open(p, encoding="utf-8").read(), p, "exec")
            r = _run([s, p, "--write"]); assert r.returncode == 3 and b"already applied" in r.stderr, r.stderr
            before = _sha(gen); r = _run([s, gen, "--write"])
            assert r.returncode == 3 and b"NOT RELEASED" in r.stderr and _sha(gen) == before, "the return draft wrote the tree's generator"
    with tempfile.TemporaryDirectory() as d:
        o1 = open(_b_copy(d, "o1", B_FULL), "rb").read()
        o2 = open(_b_copy(d, "o2", [R7["gndret"], R8["b"], R7["fandec"]] + B_ROUND[::-1] + [L9_DRAFT]), "rb").read()
        assert o1 == o2, "the order of board B's drafts changes the generator"
        _t1, n1 = _a_run(d, "a_last"); _t2, n2 = _a_run(d, "a_first", first=True)
        assert n1 == n2 == c["na"], "board A's netlist depends on where the return draft is applied"
    nB, nA = chk.read_netlist(c["nb"]), chk.read_netlist(c["na"])
    g = c["tb"]["intent"]["rails"]["GND"]
    assert g["source"] == ["J_5V_S1", "J_5V_S2", "J_5V_S3", "J_5V_DEV", "J_5V_IOC", "J_54V", "J_GR1", "J_GR2", "J_GR3"] and g["amps_peak"] == 27.9108, g
    assert chk.judge(nB, c["tb"]["intent"])[0] == "DRAWN"
    v, _lines, whole = chk.judge_pair(nA, nB)
    assert v == "DRAWN" and whole == ["J_GR1", "J_GR2", "J_GR3"], (v, whole)
    for nl in (nA, nB):
        for ref in whole:
            assert nl["pins"][ref] == {"1": "GND", "2": "GND"} and "XT60-F" in nl["value"][ref], (ref, nl["pins"][ref])
    l8 = _mod(CHECK, "l8r2_check_under_test")
    assert l8.judge("b", l8.read_netlist(c["nb"]))[0] == "DRAWN" and l8.judge("a", l8.read_netlist(c["na"]))[0] == "DRAWN"


def t_round8_the_return_removed_misplaced_or_half_terminated_is_refused():
    chk = _mod(GNDCHK, "l8r2_gndchk_under_test"); c = _composed()
    nB, nA = chk.read_netlist(c["nb"]), chk.read_netlist(c["na"])
    nl0a = chk.read_netlist(open(os.path.join(ROOT, "v2", "ecad", "pcb-a-power-a23", "out", "pcb-a-power.net"), "rb").read())
    nl0b = chk.read_netlist(open(os.path.join(ROOT, "v2", "ecad", "pcb-b-compute-b19", "out", "pcb-b-compute.net"), "rb").read())
    assert chk.judge_pair(nl0a, nl0b)[0] == "NOT DRAWN"                     # the return removed: the committed boards
    v, lines, whole = chk.judge_pair(nl0a, nB)                              # drawn on board B alone
    assert v == "FAIL" and whole == [] and all("absent on board A" in l for l in lines[1:]), (v, lines)
    raw = c["nb"]
    wrong = raw.replace(b' (node (ref "J_GR2") (pin "1"))', b"", 1)         # landed on the wrong net: pin 1 moved onto +5V_DEV
    wrong = wrong.replace(b'(name "/+5V_DEV")', b'(name "/+5V_DEV") (node (ref "J_GR2") (pin "1"))', 1)
    nw = chk.read_netlist(wrong)
    assert wrong != raw and nw["pins"]["J_GR2"] == {"1": "+5V_DEV", "2": "GND"}, nw["pins"]["J_GR2"]
    v, lines = chk.judge(nw, c["tb"]["intent"]); vp, lp, whole = chk.judge_pair(nA, nw)
    assert v == "FAIL" and any("J_GR2 is not whole on GND" in l for l in lines) and vp == "FAIL" and whole == ["J_GR1", "J_GR3"], (v, lines, vp, lp)
    keep = [l for l in raw.split(b"\n") if b'(comp (ref "J_GR3")' not in l]
    drop = b"\n".join(keep).replace(b' (node (ref "J_GR3") (pin "1"))', b"").replace(b' (node (ref "J_GR3") (pin "2"))', b"")
    nd = chk.read_netlist(drop)                                             # one termination dropped: J_GR3 absent on board B
    assert "J_GR3" not in nd["pins"]
    v, lines = chk.judge(nd, c["tb"]["intent"]); vp, lp, whole = chk.judge_pair(nA, nd)
    assert v == "FAIL" and vp == "FAIL" and whole == ["J_GR1", "J_GR2"] and any("J_GR3 is absent on board B" in l for l in lp), (v, vp, lp)
    half = chk.read_netlist(c["na"].replace(b' (node (ref "J_GR1") (pin "2"))', b"", 1))
    vp, lp, whole = chk.judge_pair(half, nB)                                # one contact of a socket missing on board A
    assert vp == "FAIL" and whole == ["J_GR2", "J_GR3"], (vp, lp)
    with tempfile.TemporaryDirectory() as d:                                # a socket the declaration does not name
        rc, _log, table, net = _b_run(d, "unnamed", B_FULL, lambda t: t.replace('_rets = ["J_GR1", "J_GR2", "J_GR3"]', '_rets = ["J_GR1", "J_GR2"]'))
        v, lines = chk.judge(chk.read_netlist(net), table["intent"])
        assert rc == 0 and v == "FAIL" and any("J_GR3 has both pins on GND and is not named" in l for l in lines), (v, lines)


def t_round8_every_branch_is_inside_its_printed_rating_at_every_vertex_with_the_return():
    """The closure criterion, on the census of the composed netlists: C-DEV rev 1 and the declared upper bound, both copper ends,
    every vertex. Without the return it does not hold; with one lead a ribbon conductor is over; with two it holds on the printed
    ratings only; with the three drawn it holds on the least ratings too, the XT60 terminations at their printed limit included."""
    chk = _mod(GNDCHK, "l8r2_gndchk_under_test"); c = _composed(); m = _mod(GNDRET, "l8r2_gndret_under_test"); F = c["F"]
    nB, nA = chk.read_netlist(c["nb"]), chk.read_netlist(c["na"])
    whole = chk.judge_pair(nA, nB)[2]; n_ret = 2 * len(whole)
    assert n_ret == 6 and len(chk.leads(nB, c["tb"]["intent"])) == 6 and sum(len(v) for v in chk.ground_conductors(nB).values()) == 17
    assert (F["xt_a_old"], F["xt_a_new"], F["xt_rise"], F["xt_r_old"], F["xt_r_new"], F["xt_awg"], F["xt_tmin"], F["xt_tmax"]) == (30.0, 35.0, 85.0, 0.55, 1.0, 12, -20.0, 120.0), F
    assert (F["vh_a16"], F["vh_rc1"], F["cab_a"], F["cab_tmax"], F["sock_rc"], F["t_e5"], F["t_cold"], F["mm2_12"]) == (10.0, 20.0, 1.0, 105.0, 20.0, 76.25, -20.0, 3.31), F
    assert m.box(F)["RET"] == (0.0, 1.0) and m.box(F)["VH"] == (0.0, 20.0) and m.box(F)["RIB"] == (0.0, 20.0)
    allow = min(F["l9_shift_allow"], F["v3_shift_allow"]); assert 0.9 < allow < 0.96
    least = {"VH": lambda T: m.least_rating(F["vh_a16"], F["vh_tmax"], T), "RIB": lambda T: m.least_rating(F["cab_a"], F["cab_tmax"], T),
             "RET": lambda T: min(30.0, m.least_rating(F["xt_a_new"], F["xt_tmax"], T, F["xt_rise"]))}
    printed = {"VH": 10.0, "RIB": 1.0, "RET": 30.0}
    assert abs(least["RIB"](76.25) - 0.59948) < 1e-4 and abs(least["RET"](76.25) - 25.1101) < 1e-3 and least["RIB"](-20.0) == 1.0

    def rows(n, total):
        out = []
        for T in (F["t_e5"], F["t_cold"]):
            ext, shift, _n, _raw = m.extremes(total, m.conductors(F, T, True, n), m.box(F))
            assert shift <= allow * 1e3
            out += [(k, T, ext[k][0]) for k in ("VH", "RIB", "RET") if k in ext]
        return out
    for total in (c["cdev"], c["upper"]):
        r6 = rows(n_ret, total)
        assert all(cur <= printed[k] and cur <= least[k](T) for k, T, cur in r6), r6
        r0 = rows(0, total)
        assert any(k == "VH" and cur > 10.0 for k, _T, cur in r0) and any(k == "RIB" and cur > 1.0 for k, _T, cur in r0), r0
    r4 = rows(4, c["upper"])
    assert all(cur <= printed[k] for k, _T, cur in r4) and any(cur > least[k](T) for k, T, cur in r4), "two leads no longer sit between the printed and the least ratings"
    r2 = rows(2, c["cdev"])
    assert any(k == "RIB" and cur > 1.0 for k, _T, cur in r2), "one lead holds: the selection is no longer the least"
    xt = max(cur for k, _T, cur in rows(n_ret, c["upper"]) if k == "RET")
    assert 10.5 < xt < 11.5 and xt < least["RET"](76.25) < 30.0, xt


def t_round8_the_committed_output_is_what_the_script_prints_and_its_predicates_hold():
    need(GNDRET, "the rounds 7 and 8 script"); need(GNDRET_OUT, "its output")
    _composed()
    before = (_sha(GEN_B), _sha(GEN_A))
    r = subprocess.run([sys.executable, "-B", GNDRET], capture_output=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr.decode()[-400:]
    assert r.stdout == open(GNDRET_OUT, "rb").read(), "l8r2_gndret.out is not what l8r2_gndret.py prints; regenerate it with _bin/regen_out.py"
    assert (_sha(GEN_B), _sha(GEN_A)) == before, "the script wrote into the tree"
    t = r.stdout.decode()
    preds = [l.rsplit(None, 1) for l in t.split("\n9. PREDICATES\n")[1].splitlines() if l.startswith("   ") and l.strip()]
    assert len(preds) == 27 and all(v == "yes" for _p, v in preds), (len(preds), [p for p, v in preds if v != "yes"])
    for s in ("the stop is reproduced after fans12 and at every later stage, without Layer 9's draft (rt500's line) and with it (iocbuck's line): yes",
              "WHICH DRAFT MOVES THE SUM: fans12 alone, by +1.770 A", "an UPPER BOUND", "the four orders give one generator, byte for byte: yes; every order runs to its end: yes",
              "every mutation stops or fails: yes (13 of 13)", "L8R2-F31 OPEN", "THE RECHECK'S CORNER, REPRODUCED", "10.6376 A in its pin 2 (V3: 10.6375 A)",
              "WHAT ROUND 7'S SAMPLING MISSED", "SELECTED (authority SESSION): D1 with 6 conductors, 3 leads", "THE RETURN PATH AS DRAWN DOES NOT HOLD",
              "THE CORRECTION IS DRAFTED, NOT ACCEPTED", "NOT RAISED TO MAKE THE GENERATOR PASS", "C-DEV rev 1", "C-ALLTX rev 3",
              "PRINTED 30 A (V1.2, no condition) and 35 A MAX with 12 AWG at a rise under 85 C (2021V1)", "NO RATING PRINTED for AWG 18 on the standard header",
              "F-1 one return lead absent or open", "F-2 one XT60 contact of one return lead open", "F-3 one 5 V lead's pin 2 open", "F-4a one 5.1 V stage in its current limit",
              "F-4b the sources' deliverable bound", "F-5 every return lead absent", "TOLERATED inside every printed rating: F-0, F-1, F-2, F-3, F-4a",
              "NOT tolerated: F-4b, F-5", "LATENT (nothing protects against it and nothing reveals it in service): F-1, F-2, F-3 and F-5",
              "NOT CLOSED: L8R2-F31 is OPEN until an independent check has read this", "no independent check has read round 8",
              "check_l8r2_netlist.py (rounds 1 to 6) board B DRAWN", "record l8gnd's check_gnd002_netlist.py board B DRAWN, board A DRAWN"):
        assert s in t, s
    for l in t.splitlines():
        if "L8R2-F31" in l:
            assert not any(wd in l.split("L8R2-F31", 1)[1][:24] for wd in (" CLOSED", " ACCEPTED", " CORRECTED BY")), l


def t_round8_the_page_and_the_readme_carry_the_rounds():
    page = open(PAGE, encoding="utf-8").read(); readme = open(os.path.join(REC, "README.md"), encoding="utf-8").read()
    for s in ("## 3g. Item 7 (rounds 7 and 8)", "RSM-01", "L8R2-F30", "L8R2-F31", "L8R2-F32", "L8R2-F33", "L8R2-F38", "L8R2-F39", "apply_gen_sch_b_gndret.py",
              "apply_gen_sch_b_fandec.py", "apply_gen_sch_a_gndrtn.py", "apply_gen_sch_b_gndrtn.py", "UPPER BOUND", "C-DEV rev 1", "27.9108 A", "22.23 A", "OPEN",
              "authority: SESSION", "IF-AB-POWER", "NOT CONFIRMED", "10.6376 A", "every vertex", "XT60", "UNSENT", "LATENT", "WITHDRAWN"):
        assert s in page, s
    for s in ("l8r2_gndret.py", "l8r2_gndret.out", "check_gndret_netlist.py", "apply_gen_sch_b_gndret.py", "apply_gen_sch_b_fandec.py", "apply_gen_sch_a_gndrtn.py",
              "apply_gen_sch_b_gndrtn.py", "round 8", "astra-check-t5-recheck-cx41.md"):
        assert s in readme, s
    first = next(l for l in page.splitlines() if "L8R2-F31" in l)
    assert "OPEN" in first, "the page does not carry the capacity finding as OPEN where it names it first"
    for l in page.splitlines():
        if "L8R2-F31" in l:
            assert not any(wd in l.split("L8R2-F31", 1)[1][:24] for wd in (" CLOSED", " ACCEPTED", " is closed")), l


# ------------------------------------------------------------------------------------------------ P0 round (5 October 2026, Slot A)
P0 = os.path.join(REC, "l8r2_p0.py")
P0_OUT = os.path.join(REC, "l8r2_p0.out")


def t_p0_the_output_is_reproduced_pinned_and_every_predicate_holds():
    import subprocess
    need(P0, "l8r2_p0.py")
    need(P0_OUT, "l8r2_p0.out")
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is needed")
    r = subprocess.run([sys.executable, "-B", P0], cwd=ROOT, capture_output=True)
    assert r.returncode == 0, r.stderr.decode()[-300:]
    text = r.stdout.decode("utf-8")
    assert text == open(P0_OUT, encoding="utf-8").read(), "l8r2_p0.out is not what the script prints"
    rows = [l for l in text.split("6. PREDICATES")[1].split("l8r2_p0: done")[0].splitlines() if l.strip()]
    assert len(rows) >= 10 and all(l.rstrip().endswith(" yes") for l in rows), rows
    pins = re.findall(r"^\s{3}([0-9a-f]{16}) (v2/\S+)$", text, re.M)
    assert len(pins) >= 10
    for h, rel_ in pins:
        assert hashlib.sha256(open(os.path.join(ROOT, rel_), "rb").read()).hexdigest().startswith(h), rel_


def t_p0_v6_b1_reproduces_v6_and_the_disposition_is_provisional_and_open_where_no_layout_realises_it():
    text = open(P0_OUT, encoding="utf-8").read()
    for s_ in ("0.3543 mOhm (declared peak) and 0.7747 mOhm (C-DEV rev 1)", "0.1436 and", "0.4386 mOhm", "V6-B1 is not closed", "after cx46 OPEN, REMAINING ENGINEERING",
               "STILL OPEN", "L8R2-F33a", "NOT A CORRECTION", "covers the COUNTED branches only", "NO CURRENT RATING PRINTED",
               "authority: SESSION", "WIRE-TO-WIRE rating"):
        assert s_ in text, s_
    page = open(PAGE, encoding="utf-8").read()
    sec = page.split("## 3h. P0 round")[1].split("## 4. ")[0]
    for s_ in ("L8R2-F33a", "PROVISIONAL", "STILL OPEN", "authority: SESSION", "UNSENT"):
        assert s_ in sec, s_
    # every figure the section quotes is printed by an output: l8r2_p0.out, or l8r2_dist.out for the cx45 correction paragraph (the placed
    # distributed model)
    dist = open(os.path.join(ROOT, "v2", "docs", "records", "l8r2", "l8r2_dist.out"), encoding="utf-8").read()
    figs = sorted(set(re.findall(r"\d+\.\d+ (?:A|V|mOhm)\b", sec)))
    assert figs and not [f for f in figs if f not in text + dist], [f for f in figs if f not in text + dist]


def t_p0_the_group_centre_reading_is_withdrawn_as_realisability():
    """cx45 Q2: the group-centre construction of l8r2_p0.out 2b places no footprint and solves no current; its claim of realisability
    is withdrawn there, in 6d and on the page, and the placed distributed model replaces it"""
    text = open(P0_OUT, encoding="utf-8").read()
    assert "it is NOT evidence that the condition is realisable" in text and "SESSION L8R2-D9 withdrawn with it" in text
    assert "MET on the" not in text and "realisable on the placement as drawn)" not in text
    page = open(PAGE, encoding="utf-8").read()
    assert "the group-centre reading of `l8r2_p0.out` 2b placed no footprint" in page and "l8r2_dist.py" in page
    gr = " ".join(open(os.path.join(REC, "l8r2_gndret.out"), encoding="utf-8").read().split())
    assert "the sockets are PLACED with their" in gr and "a STUDY, not a correction" in gr and "V6-B1 stays OPEN as REMAINING ENGINEERING" in gr


DIST = os.path.join(REC, "l8r2_dist.py")
DIST_OUT = os.path.join(REC, "l8r2_dist.out")


def _dist_module():
    import importlib.util
    try:
        import numpy  # noqa: F401
        import scipy  # noqa: F401
    except ImportError:
        raise Skip("numpy and scipy are needed")
    need(DIST, "l8r2_dist.py")
    sp = importlib.util.spec_from_file_location("l8r2_dist_under_test", DIST)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def t_p0_dist_output_reproduced_pinned_and_every_predicate_holds():
    import subprocess
    _dist_module()
    need(DIST_OUT, "l8r2_dist.out")
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is needed")
    r = subprocess.run([sys.executable, "-B", DIST], cwd=ROOT, capture_output=True)
    assert r.returncode == 0, r.stderr.decode()[-300:]
    text = r.stdout.decode("utf-8")
    assert text == open(DIST_OUT, encoding="utf-8").read(), "l8r2_dist.out is not what the script prints"
    rows = [l for l in text.split("7. PREDICATES")[1].split("l8r2_dist: done")[0].splitlines() if l.strip()]
    assert len(rows) >= 6 and all(l.rstrip().endswith(" yes") for l in rows), rows
    for h, rel_ in re.findall(r"^\s{3}([0-9a-f]{16}) (v2/\S+)$", text, re.M):
        assert hashlib.sha256(open(os.path.join(ROOT, rel_), "rb").read()).hexdigest().startswith(h), rel_


def t_p0_dist_the_placement_is_clear_and_the_network_is_the_composed_one():
    """the placement draft re-read independently: each site's courtyard against every placed courtyard (a separate loop), inside the
    outline; the conductors are the composed netlists' (six VH, seventeen ribbon pins, six XT60 contacts)"""
    m = _dist_module()
    text = open(DIST_OUT, encoding="utf-8").read()
    for b in "ab":
        fps = m.footprints(m.PCB[b])
        segs = m.outline(m.PCB[b])
        for ref, x0, y0, x1, y1 in re.findall(r"^   board %s (\S+)\s+at \([\d.]+, [\d.]+\) rotated\s+\d+: courtyard \(([\d.]+), ([\d.]+)\)-\(([\d.]+), ([\d.]+)\)" % b.upper(), text, re.M):
            box = tuple(float(v) for v in (x0, y0, x1, y1))
            for f in fps.values():
                c = f["crt"]
                if c is None:
                    continue
                apart = c[0] >= box[2] + m.CLEAR - 1e-6 or c[2] <= box[0] - m.CLEAR + 1e-6 or c[1] >= box[3] + m.CLEAR - 1e-6 or c[3] <= box[1] - m.CLEAR + 1e-6
                assert apart, (b, ref, f["name"])
            assert all(m.inside(segs, [px], [py])[0] for px, py in ((box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3]))), (b, ref)
    assert "6 VH lead pin 2s, 17 ribbon ground conductors" in text and "6 XT60 return contacts" in text


def t_p0_dist_the_verdict_matches_its_rows_and_the_one_node_model_is_kept_beside_it():
    text = open(DIST_OUT, encoding="utf-8").read()
    rows = re.findall(r"^     ([+-]\d+\.\d\d) C (VH|RIB|RET)\s+\S+\s+([\d.]+) A \(.*?\): printed ([\d.]+) A (holds|OVER); least ([\d.]+) A (holds|OVER)$", text, re.M)
    assert len(rows) == 24
    for T_, k, cur, pr, vp, le, vl in rows:
        assert (float(cur) <= float(pr)) == (vp == "holds") and (float(cur) <= float(le)) == (vl == "holds"), (T_, k, cur)
    assert all(r_[4] == "holds" for r_ in rows), "a printed row over its rating"
    svc = rows[:6] + rows[12:18]                       # C-DEV rev 2 and the largest steady state
    assert all(r_[6] == "holds" for r_ in svc)
    over = [r_ for r_ in rows if r_[6] == "OVER"]
    assert over and all(r_[0] == "+76.25" for r_ in over) and rows.index(over[0]) >= 18      # the declared upper bound only
    assert "5. AGAINST THE ONE-NODE MODEL" in text and "5b. THE ROUTE FOR THE DECLARED UPPER BOUND'S RIBBON ROW" in text
    assert "NOT drafted: no service row needs it" in text and "SESSION decision L8R2-D11" in text
    # cx46 item 4: the study is labelled as what it is and V6-B1 stays OPEN as REMAINING ENGINEERING
    flat = " ".join(text.split())
    for s_ in ("STAND IN for it (ASSUMPTION, cx46 item 4)", "their AVERAGE", "not a global bound over the tolerance box",
               "DISPOSITION OF V6-B1 AFTER cx46 (kept as given; the second negative ends the method): OPEN, REMAINING ENGINEERING",
               "a STUDY, not a correction", "the selected female lands, the real source and load sites"):
        assert s_ in flat, s_
    assert "CORRECTED IN DRAFT" not in text and "holds on the placed distributed one" not in text
