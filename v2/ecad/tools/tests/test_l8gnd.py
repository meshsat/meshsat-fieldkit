"""Layer 8 record l8gnd (MESHSAT-1357, 3 October 2026; v2/docs/records/l8gnd/): the two Layer 5 generator items that had been
"in no generator" since the Layer 3 handover (LAYER-STATUS rows 5.6 and 5.12), as release-guarded drafts.

The predicates: the committed .out is what the script prints; each draft checks without writing, applies once, refuses a second
time and refuses the tree's own generator; this record's two board A drafts apply after every power draft of L4-E4 to L4-E11 in
L4-E9's change-list order, and every one of those drafts' anchors still applies after this record's two (in sequence and each alone);
the two apply in either order; no two board A drafts add the same designator (L6P-F01's method, H pads and tokens included) and this
record's are H1, R229 and U43, R230 to R232, C240; the board B draft moves exactly C33's cold end and J_ETH's shield to CHASSIS and
adds no part; the netlist check parses, reads the committed netlists NOT DRAWN on A and B, DRAWN on fixtures that carry the drafted
changes, and FAIL on a second bond or a capacitor left on GND; the keeper holds both levels against the pad's weakest pull-down and
the panel's drive overrides it inside 4 mA; the land draft is one plated pad on pad 1 at 4.3 over 12.0; the page proposes the two
LAYER-STATUS rows and carries no em or en dash and no claim word.

No KiCad: everything here is generator text, netlist text and arithmetic, on scratch copies, and the tree is never written."""
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
REC = os.path.join(ROOT, "v2", "docs", "records", "l8gnd")
RECS = os.path.dirname(REC)
GEN_A = os.path.join(TOOLS, "gen_sch_a.py")
GEN_B = os.path.join(TOOLS, "gen_sch_b.py")
SCRIPT = os.path.join(REC, "l8gnd_drafts.py")
OUT = os.path.join(REC, "l8gnd_drafts.out")
PAGE = os.path.join(REC, "L8-GND002-SLOTEN.md")
CHECK = os.path.join(REC, "check_gnd002_netlist.py")
LAND = os.path.join(REC, "footprints", "ChassisLug_M4_CHASSIS.kicad_mod")
MINE_A = [os.path.join(REC, "apply_gen_sch_a_gnd002.py"), os.path.join(REC, "apply_gen_sch_a_hotr1.py")]
MINE_B = os.path.join(REC, "apply_gen_sch_b_gnd002.py")
sys.path.insert(0, TESTS)
from harness import need, Skip  # noqa: E402

CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)
_CACHE = {}


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _mod(path, name):
    key = (path, name)
    if key not in _CACHE:
        need(path, "a file of the l8gnd record")
        sp = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        _CACHE[key] = m
    return _CACHE[key]


def _run(args, cwd=None):
    return subprocess.run([sys.executable, "-B"] + args, capture_output=True, cwd=cwd)


def _theirs():
    m = _mod(SCRIPT, "l8gnd_drafts_under_test")
    paths = [os.path.join(RECS, r, "apply_gen_sch_a_%s.py" % n) for r, n in m.POWER_ORDER]
    for p in paths:
        need(p, "a board A power draft of L4-E4 to L4-E11 (L4-POWER-ARCHITECTURE.md section 3)")
    return paths


def t_the_committed_output_is_what_the_script_prints():
    need(OUT, "the record's committed output")
    before = {g: _sha(g) for g in (GEN_A, GEN_B)}
    r = _run([SCRIPT], cwd=ROOT)
    assert r.returncode == 0, r.stderr.decode()[-400:]
    assert r.stdout == open(OUT, "rb").read(), "l8gnd_drafts.out is not what l8gnd_drafts.py prints; regenerate it with _bin/regen_out.py"
    assert all(_sha(g) == s for g, s in before.items()), "the script wrote into the tree"
    txt = r.stdout.decode()
    assert "pairwise intersections: none (DISJOINT)" in txt and "GND-002 on the kit: NOT DRAWN (A NOT DRAWN, B NOT DRAWN" in txt
    assert "fixture A: DRAWN" in txt and "fixture B: DRAWN" in txt and "the two results carry the same part calls: YES" in txt


def t_each_draft_checks_applies_once_refuses_twice_and_refuses_the_tree():
    before = {g: _sha(g) for g in (GEN_A, GEN_B)}
    with tempfile.TemporaryDirectory() as d:
        for script, gen in [(s, GEN_A) for s in MINE_A] + [(MINE_B, GEN_B)]:
            tgt = os.path.join(d, os.path.basename(script)[:-3] + "_gen.py")
            shutil.copy(gen, tgt)
            pre = _sha(tgt)
            r = _run([script, tgt])
            assert r.returncode == 0 and b"CHECK OK" in r.stdout, r.stderr.decode()[-300:]
            assert _sha(tgt) == pre, "--check wrote"
            r = _run([script, tgt, "--write"])
            assert r.returncode == 0 and b"WRITTEN" in r.stdout, r.stderr.decode()[-300:]
            r = _run([script, tgt, "--write"])
            assert r.returncode == 3, "a second application was not refused"
            r = _run([script, gen, "--write"])
            assert r.returncode == 3 and b"NOT RELEASED" in r.stderr, "the tree's own generator was not refused"
    assert all(_sha(g) == s for g, s in before.items()), "a draft wrote into the tree"


def t_this_records_drafts_apply_after_every_power_draft_in_l4e9s_order():
    theirs = _theirs()
    with tempfile.TemporaryDirectory() as d:
        a = os.path.join(d, "gen_sch_a.py"); shutil.copy(GEN_A, a)
        for s in theirs + MINE_A:
            r = _run([s, a, "--write"])
            assert r.returncode == 0, "%s refused: %s" % (os.path.relpath(s, RECS), r.stderr.decode()[-200:])
        txt = open(a, encoding="utf-8").read()
        assert 'part("H1", "Mechanical", "MountingHole_Pad"' in txt and 'r("R229", "0R 2512 (CHASSIS bond link)", "CHASSIS", "GND", "RS2512")' in txt
        assert 'ic("U43", 14, "SN74LVC08APWR quad AND: the SLOT_EN keepers' in txt and '"LUGM4": "meshsat:ChassisLug_M4_CHASSIS"' in txt
        assert txt.count('_intent.node("CHASSIS"') == 1 and txt.count("SECTIONS.append((") >= 2
        compile(txt, a, "exec")


def t_every_power_drafts_anchor_survives_this_records_drafts():
    """This record's two first, then L4-E9's order step by step; and each power draft alone after this record's two (the bank
    draft after R12, which it requires by design). A refusal here is the finding the brief names: an anchor broken by this record."""
    theirs = _theirs()
    r12 = [t for t in theirs if t.endswith("apply_gen_sch_a_r12.py")]
    with tempfile.TemporaryDirectory() as d:
        a = os.path.join(d, "seq.py"); shutil.copy(GEN_A, a)
        for s in MINE_A + theirs:
            r = _run([s, a, "--write"])
            assert r.returncode == 0, "%s refused after this record's drafts: %s" % (os.path.relpath(s, RECS), r.stderr.decode()[-200:])
        for s in theirs:
            p = os.path.join(d, "alone_" + os.path.basename(s)); shutil.copy(GEN_A, p)
            for m in MINE_A + (r12 if s.endswith("apply_gen_sch_a_bank.py") else []):
                assert _run([m, p, "--write"]).returncode == 0
            r = _run([s, p, "--write"])
            assert r.returncode == 0, "%s alone refused after this record's drafts: %s" % (os.path.relpath(s, RECS), r.stderr.decode()[-200:])


def t_this_records_two_board_a_drafts_apply_in_either_order():
    with tempfile.TemporaryDirectory() as d:
        for order in (MINE_A, MINE_A[::-1]):
            p = os.path.join(d, "o_" + os.path.basename(order[0])); shutil.copy(GEN_A, p)
            for s in order:
                assert _run([s, p, "--write"]).returncode == 0, "%s refused in order %s" % (s, [os.path.basename(x) for x in order])


def t_the_board_a_designators_are_disjoint_from_every_drafts():
    """L4-E11's method, extended to H pads: every board A draft applied in L4-E9's order with this record's last; the designators each
    adds are read from the text it writes (part-call position and tokens outside comments) and no two drafts add the same one."""
    m = _mod(SCRIPT, "l8gnd_drafts_under_test")
    theirs = _theirs()
    added = {}
    with tempfile.TemporaryDirectory() as d:
        a = os.path.join(d, "gen_sch_a.py"); shutil.copy(GEN_A, a)
        before = open(a, encoding="utf-8").read()
        for s in theirs + MINE_A:
            assert _run([s, a, "--write"]).returncode == 0, s
            after = open(a, encoding="utf-8").read()
            new = set(m.added_calls(before, after)) | (set(m.multiline_calls(after)) - set(m.multiline_calls(before))) | m.added_tokens(before, after)
            added[os.path.relpath(s, RECS)] = new
            before = after
    assert added["l8gnd/apply_gen_sch_a_gnd002.py"] == {"H1", "R229"}, sorted(added["l8gnd/apply_gen_sch_a_gnd002.py"])
    assert added["l8gnd/apply_gen_sch_a_hotr1.py"] == {"U43", "R230", "R231", "R232", "C240"}, sorted(added["l8gnd/apply_gen_sch_a_hotr1.py"])
    names = sorted(added)
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            both = added[x] & added[y]
            assert not both, "%s and %s both add %s" % (x, y, sorted(both))


def t_the_board_b_draft_moves_c33_and_the_shell_to_chassis_and_adds_no_part():
    m = _mod(SCRIPT, "l8gnd_drafts_under_test")
    with tempfile.TemporaryDirectory() as d:
        b = os.path.join(d, "gen_sch_b.py"); shutil.copy(GEN_B, b)
        before = open(b, encoding="utf-8").read()
        assert _run([MINE_B, b, "--write"]).returncode == 0
        after = open(b, encoding="utf-8").read()
        assert not m.added_calls(before, after) and not (set(m.multiline_calls(after)) - set(m.multiline_calls(before))), "a part was added on B"
        assert m.calls(before)["C33"][1] == ["BOB", "GND", "C1812"] and m.calls(after)["C33"][1] == ["BOB", "CHASSIS", "C1812"]
        sh = lambda t: re.search(r'"SH":\s*"([A-Z]+)"\}\)', m.strip_comments(t)).group(1)
        assert sh(before) == "GND" and sh(after) == "CHASSIS"
        assert after.count('"CHASSIS"') == 3 and '_intent.node("CHASSIS", 0.0' in after, "CHASSIS appears on C33, J_ETH SH and the node declaration only"
        assert m.strip_comments(after).count("CHASSIS") == 4, "CHASSIS outside comments: C33, SH, the node's name and its text"
        compile(after, b, "exec")


def t_the_netlist_check_parses_and_judges_the_committed_netlists_and_the_fixtures():
    chk = _mod(CHECK, "l8gnd_check_under_test")
    m = _mod(SCRIPT, "l8gnd_drafts_under_test")
    nets = chk.committed(ROOT)
    for k in ("a", "b", "c", "e"):
        need(nets.get(k, os.path.join(ROOT, "missing-%s.net" % k)), "board %s's committed netlist" % k.upper())
    buf = io.StringIO()
    kit, v = chk.run(nets, ROOT, buf)
    assert kit == "NOT DRAWN" and v["a"] == "NOT DRAWN" and v["b"] == "NOT DRAWN" and v["c"] == "HOLDS" and v["e"] == "HOLDS", v
    assert all(l.split(" sha256 ")[1][:16] == _sha(os.path.join(ROOT, l.split(" sha256 ")[0]))[:16] for l in buf.getvalue().splitlines() if " sha256 " in l)
    nl = chk.read_netlist(open(nets["a"], "rb").read())
    assert ("J_DOCK", "12") in nl["nets"]["DOCK_SPARE"] and nl["pins"] if False else ("R216", "1") in nl["nets"]["DOCK_SPARE"], "the parser reads a known net"
    assert chk.judge("a", chk.read_netlist(m.fixture_a()))[0] == "DRAWN" and chk.judge("b", chk.read_netlist(m.fixture_b()))[0] == "DRAWN"
    # drawn wrong: a second bond on A; the capacitor left on GND on B; a chassis net on E
    two = m.fixture_a().replace(b'(node (ref "C4") (pin "2"))', b'(node (ref "C4") (pin "2")) (node (ref "H1") (pin "1"))')
    assert chk.judge("a", chk.read_netlist(two))[0] == "FAIL"
    wrong = m.fixture_b().replace(b'(name "/CHASSIS") (node (ref "C33") (pin "2"))', b'(name "/CHASSIS")').replace(b'(name "GND") (node (ref "T1") (pin "1"))', b'(name "GND") (node (ref "T1") (pin "1")) (node (ref "C33") (pin "2"))')
    assert chk.judge("b", chk.read_netlist(wrong))[0] == "FAIL"
    e_bad = b'(export (version "E") (components) (nets (net (code "1") (name "/CHASSIS") (node (ref "X1") (pin "1")))))'
    assert chk.judge("e", chk.read_netlist(e_bad))[0] == "FAIL" and chk.judge("e", chk.read_netlist(b'(export (version "E") (components) (nets (net (code "1") (name "GND") (node (ref "X1") (pin "1")))))'))[0] == "HOLDS"


def t_the_keeper_holds_both_levels_and_the_panel_overrides_it():
    m = _mod(SCRIPT, "l8gnd_drafts_under_test")
    K = m.keeper()
    k = {n: v for n, (v, _c, _w) in m.KEEPER.items()}
    for tag in ("rpd_min", "rpd_max"):
        assert K[tag]["v_high"] > k["vih"] + 0.5, "held high under VIH plus 0.5 V at %s" % tag
        assert K[tag]["v_high"] > max(k["ap_ven_h_max"], k["lm_ven_op_max"]) + 1.0, "held high too close to an enable's ON threshold"
        assert K[tag]["v_low"] < k["vil"] - 0.5 and K[tag]["v_low"] < min(k["ap_ven_l_min"], k["lm_ven_stby_min"]) - 0.3
    assert K["rpd_min"]["v_high"] < K["rpd_max"]["v_high"], "the weaker pull-down is the worse case"
    assert K["drive_ok"] and K["i_override_ma"] < 1.0 and K["i_sink_held_high_ma"] < 1.0
    assert k["rp_voh_min"] > k["vih"] and k["rp_vol_max"] < k["vil"], "the panel's own levels pass the gate's thresholds"
    rdown = k["rpd_min"] * k["rpull"] / (k["rpd_min"] + k["rpull"])
    assert abs(K["rpd_min"]["v_high_div"] - (k["v33_min"] - k["voh_drop"]) * rdown / (k["rk"] + rdown)) < 1e-9
    classes = {c for _n, (_v, c, _w) in m.KEEPER.items()}
    assert classes <= {"MAKER", "INFERRED", "BOUND"} and sum(1 for _n, (_v, c, _w) in m.KEEPER.items() if c == "INFERRED") == 1


def t_the_land_draft_is_one_plated_pad_on_pad_1_at_4_3_over_12_0():
    chk = _mod(CHECK, "l8gnd_check_under_test")
    need(LAND, "the land draft")
    tree = chk.sexp(open(LAND, encoding="utf-8").read())
    fp = tree[0]
    assert fp[0] == "footprint" and fp[1] == "ChassisLug_M4_CHASSIS"
    pads = [x for x in fp if isinstance(x, list) and x and x[0] == "pad"]
    assert len(pads) == 1 and pads[0][1] == "1" and pads[0][2] == "thru_hole"
    size = chk.kv(pads[0], "size"); drill = chk.kv(pads[0], "drill"); layers = chk.kv(pads[0], "layers")
    assert float(size[1]) == 12.0 and float(size[2]) == 12.0 and float(drill[1]) == 4.3 and "*.Cu" in layers and "*.Mask" in layers
    assert chr(0x2014) not in open(LAND, encoding="utf-8").read()


def t_the_page_proposes_the_two_rows_and_carries_no_dash_or_claim_word():
    need(PAGE, "the record's page")
    files = [os.path.join(REC, f) for f in sorted(os.listdir(REC)) if f.endswith((".md", ".py", ".out"))] + [LAND, os.path.abspath(__file__)]
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "%s carries an em or en dash" % os.path.relpath(p, ROOT)
        if p != os.path.abspath(__file__):
            mm = CLAIM.search(" ".join(t.split()))
            assert not mm, "%s carries a claim word: %r" % (os.path.relpath(p, ROOT), mm.group(0))
    page = open(PAGE, encoding="utf-8").read()
    for s in ("| 5.6 |", "| 5.12 |", "apply_gen_sch_a_gnd002.py", "apply_gen_sch_b_gnd002.py", "apply_gen_sch_a_hotr1.py", "check_gnd002_netlist.py",
              "DS00004151A", "SCAS283W", "Table 625", "DRAFTED", "not applied", "H1", "R229", "U43", "R230", "C240", "CHASSIS", "SLOT_EN1_K"):
        assert s in page, "the page does not name %r" % s
    for word in ("change 1", "change 2", "change 3", "change 4"):
        assert word in page, "the page does not number %s" % word
    assert "a fifth" in page or "no fifth" in page, "the page does not say that no fifth change is drawn"
