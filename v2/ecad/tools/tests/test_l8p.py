"""Layer 8 record l8p (MESHSAT-1357, 4 October 2026, rounds 1 to 6b; v2/docs/records/l8p/): W4DP-F2's breaker drawn as
release-guarded drafts for board P (the latch-off LM5069-1, the make-last enable loop's inverters, the RC hold through a diode, the
restart inhibit C-1c gated by PGD, and in round 3 B-R2's reverse-charge detector on the loop's return), board E (the loop through
J_SMB to the dock) and board A (the loop's thermal guard RT1), from record l9stk section 15 (fnd/l9stk at 0d72880b) and task
L4-E11's section 19h (fnd/l4e11r9 at e60a94a8); and in round 4 a second board P draft, the ideal diode beside the charge switch
Q1 that corrects design defect DD-5 (BAT-F20) on case row C-PROT with CHGIN = 1.

The predicates: the committed .out is what the script prints; each draft checks, applies once on a scratch copy, refuses twice and
refuses the tree's own generator; each board composes in L4-E9's change-list order with this record's draft in its place, first
and last (board E with L4-E7's backstop draft of fnd/l4e7r6, which closes L8P-F01); the designators are this record's sets and
disjoint from every other draft's; every value is found in record l9stk's copied text and the copies are the bytes SOURCES.txt
pins; C-1c's budget closes on figures read from TI's held OPA187 sheet and Murata's NTC sheet; B-R2's detector closes on figures
read from L4-E11's copies and the LM5069, CSD18510Q5B, 2N7002 and BZT52C sheets; DD-5's correction closes on figures read from
the BQ4050's, the CSD17570Q5B's and the LM74700-Q1's sheets, and the old state (Q1's body diode) fails the same computation; the
ideal diode draft refuses a target without the breaker draft; round 5 (the check V1's condition C4 and its minors): the compositions
use L4-E11's round 10 drafts with no stand-in, the interface of 12f is quoted from L4-E11's copied sections 20c and 20d, L8P-F06's
leakage budget and L8P-F07's printed and typical points recompute from the sheets and the copies, and the alternative part's typed
figures read against TDK's held sheet when it is present; round 6 (the independent check V2's V2-B2, V2-B3 and its minors): every
copy of L4-E11 is the round's that l8p_drafts.L4E11_AT names (round 12 at ac72e730 in round 6; round 13 at 4def5975 since round 6b,
where only section 20c changed and no figure this record reads of it moved) and a copy that is not a tree's records/l4e11/ fails, L8P-F06 stands
against BOTH limits of L4-E11's latch (the timing limit reproduced), TDK's window takes the sure-off as a lower bound and a
mutation of that direction fails, the trip side's junction is on the worst split and named not bounded, board A composes in L4-E9's
list order and the whole list composes wherever a tree holds its drafts, the PTC draft quotes what Murata prints; the netlist
check reads NOT DRAWN
on the committed netlists, DRAWN on the netlists regenerated from the patched generators (the loop across the three boards and
the inhibit included) and FAIL on mutated ones; the page carries no em or en dash and no claim word, and names the conditions
and the interface rows owed. No KiCad: generator text, the generators' own part tables and netlist text, on scratch copies; the
tree is never written."""
import hashlib
import importlib.util
import io
import math
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
    for s in ("record l9stk's, L4-E7's and L4-E11's copies (rounds 9 and 13) equal the sha256 SOURCES.txt pins: yes", "the tree's generators are unchanged: yes",
              "+-1.95 K left: consistent", "the split closes", "is ASSUMED from the product search sheet", "THE LOCKOUT AT THE ALLOW EDGE",
              "E-10 gains: VDS under 1.62 V during current-limit excursions", "CLOSED by L4-E7's fnd/l4e7r6 at 914a2f5a",
              "l8p/inputs/l4e7r6-apply_gen_sch_e_backstop-914a2f5a.py OK", "       P INH  DRAWN", "decoupling C106: class D at U102.5 on BRK_VIN",
              "board P, this record's against every other draft's: DISJOINT", "board E, this record's against every other draft's: DISJOINT",
              "board A, this record's against every other draft's: DISJOINT", "record l8p's breaker and enable loop on the netlists: NOT DRAWN",
              "       LOOP DRAWN", "all KiCad's names for open pins: yes; footprints differing: 0", "(R257, C249)",
              "L8P-F01 board E", "L8P-F02 board A", "L8P-F03 board E", "L8P-F04 board A", "L8P-F05 board A", "       P REV  DRAWN",
              "B-R2 BY THE CRITERION: MEETS ON PAPER", "decoupling C107: class D at U103.5 on BRK_VIN", "decoupling C108: class D at U104.5 on BRK_VIN",
              "l8p/inputs/l4e11-section19h-e60a94a8.md", "only the return held LOW is distinct", "       P DIO  DRAWN",
              "DD-5 BY THE CASE ROW: CORRECTED IN THE DRAFT", "'body diode' occurs 0 times in SLUUAQ3A and SLUSC67B",
              "apply_gen_sch_p_idealdiode.py (after apply_gen_sch_p_breaker.py): without it refused; check OK; applied OK; second application refused",
              "l8p/apply_gen_sch_p_idealdiode.py            OK", "decoupling C111: class L at U105.1 on IDL_VCAP",
              "decoupling C112: class D at U105.6 on SCP_OUT", "decoupling C114: class B2 at U105.4 on SW",
              "rail SW       source ['Q1', 'Q109']", "the breaker draft without the ideal diode (DD-5 uncorrected)",
              # rounds 5 and 6
              "l8p/inputs/l4e11r13-apply_gen_sch_a_dd7-4def5975.py OK", "l8p/inputs/l4e11r13-apply_gen_sch_a_charger-4def5975.py OK",
              "board E composed in L4-E9's order: the generator ran to its end (295 parts, intent written: yes)",
              "board A composed in L4-E9's order: the generator ran to its end (728 parts, intent written: yes)",
              "board A, the list's order with the tree's drafts it does not name (l8r2's d8v3, l8r2's vbus20ov): the generator ran to its end (750 parts",
              "packrtn (R-201), slotlm (R-199), fb01 (R-200)", "it is refused, mainpb having taken its R233 and C241 as the next free",
              "THE DELAYS AS BOARD A DRAWS THEM (L4-E11 20d at 4def5975, quoted)", "board A's set 0.85 ms: the sum agrees",
              "20c AS L4-E11's ROUND 13 RESTATES IT ON MURATA'S PRINTED POINTS", "2.894 V) is WITHDRAWN as a bound",
              "the closed return reads closed for any RT1 under 269 kOhm at 10.6 V", "is unchanged from its round 12",
              "breaker's restart (0.9477 s, this record's 0.9477 s: the same)",
              "the static limit 0.846 mA", "the timing limit 520.7 uA", "static 846.0 uA, timing 520.9 uA (L4-E11 prints 520.7)",
              "it leaves the pair 473.9 uA", "leaves 85.9 uA in hand", "it leaves the pair 786.8 uA",
              "L8P-F06: both limits hold at the held case on the ASSUMED doubling", "272.3 uA: reproduced",
              "PACK_P at CELL+", "1 IDSS row, no hot figure",
              "record l9stk 15.5 reads '47 kOhm at 130 C plus or minus 3 C': yes", "the header '*at 4.7kohm *at 47kohm'",
              "PTC's copper passes 133 C: PRINTED. The junction over that copper is NOT BOUNDED",
              "NOT PRINTED at any pack voltage", "it does NOT keep C-PROT's 18 A for 60 s uninterrupted there",
              "inside the window: HOLDS", "the window 10.51 to 10.62, 1.0 % wide: A k EXISTS", "the window 8.53 to 10.62, 24.5 % wide: A k EXISTS",
              "on that table no k exists at either voltage", "NOT SELECTED", "THE JOINT CASE (the check V2's V2-m8): at 23.93 A held the board dissipates 4.57 W",
              "L8P-F06 board P with L4-E11", "L8P-F07 board A with record l9stk"):
        assert s in t, s
    for old in ("NO k EXISTS", "a09e9a60", "ac72e730", "the junction at most 134.88 C against 150 C: PRINTED", "the pair alone fills the clamp's room from a 111.7 C case"):
        assert old not in t, "round 5's statement is back in the output: %s" % old
    assert t.count("record l8p's breaker and enable loop on the netlists: DRAWN") == 3, "the alone, the composed and the tree-order readings"
    assert t.count("record l8p's breaker and enable loop on the netlists: FAIL") == 11, "the ten mutations and the breaker without the ideal diode"
    assert t.count("       P DIO  FAIL") == 2 and t.count("       P DIO  NOT DRAWN") == 2, "DIO's two mutations; NOT DRAWN on the tree and without the draft"
    comp_a = t.split("mutated composed board A (")[1:]
    assert len(comp_a) == 3 and all("       A EN   FAIL: " in c.split("record l8p's")[0] for c in comp_a), "the three mutations of the composed board A"
    assert "REFUSED" not in t.split("5. COMPOSITION")[1].split("6. DESIGNATORS")[0], "a composition step refused"
    assert "with scratch stand-ins" not in t and "the generator refused" not in t, "a stand-in or a refusal is back in the compositions"


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
            for s2 in m.MINE2.get(b, []):       # round 4: the second draft needs the first, and is guarded as it is
                bare = os.path.join(d, os.path.basename(s2) + ".bare.py"); shutil.copy(GEN[b], bare); pre2 = _sha(bare)
                r = _run([s2, bare, "--write"]); assert r.returncode == 3 and b"breaker draft is not applied" in r.stderr and _sha(bare) == pre2, "applied without the breaker draft"
                pre2 = _sha(tgt)
                r = _run([s2, tgt]); assert r.returncode == 0 and b"CHECK OK" in r.stdout and _sha(tgt) == pre2, r.stderr.decode()[-300:]
                r = _run([s2, tgt, "--write"]); assert r.returncode == 0 and b"WRITTEN" in r.stdout, r.stderr.decode()[-300:]
                assert _run([s2, tgt, "--write"]).returncode == 3, "a second application was not refused"
                r = _run([s2, GEN[b], "--write"]); assert r.returncode == 3 and b"NOT RELEASED" in r.stderr, "the tree's own generator was not refused"
                compile(open(tgt, encoding="utf-8").read(), tgt, "exec")
    assert not os.path.exists(os.path.join(REC, "RELEASE.md")), "a release record exists: the drafts are no longer guarded"
    assert all(_sha(GEN[b]) == s for b, s in before.items()), "a draft wrote into the tree"


def t_each_board_composes_in_l4e9s_order_in_its_place_first_and_last():
    m = _need_inputs()
    with tempfile.TemporaryDirectory() as d:
        for b in "pea":
            seq = [m.draft(r, n, b) for r, n in m.ORDER[b]]
            mine = m.mine_seq(b)
            for tag, order in (("fwd", seq[:m.SLOT[b]] + mine + seq[m.SLOT[b]:]), ("first", mine + seq), ("last", seq + mine)):
                p, res = m.compose(b, order, d, tag)
                assert len(res) == len(order) and all(v.startswith("OK") for _s, v in res), (b, tag, res)
                compile(open(p, encoding="utf-8").read(), p, "exec")


def t_the_designators_are_this_records_sets_and_disjoint():
    m = _need_inputs()
    want = {"p": {"U101", "U102", "U103", "U104", "U105", "D101", "D102", "D103", "D104", "RT101"} | {"Q%d" % k for k in range(101, 110)}
            | {"R%d" % k for k in range(101, 132)} | {"C%d" % k for k in range(101, 116)} | {"TP%d" % k for k in range(101, 110)},
            "e": set(), "a": {"RT1"}}
    second = {"Q109", "U105", "D104", "R130", "R131", "C111", "C112", "C113", "C114", "C115", "TP109"}
    with tempfile.TemporaryDirectory() as d:
        for b in "pea":
            fwd = m.order(b, "tree")        # the list's order with the tree's drafts it does not name and L4-E11's DD-7
            p = os.path.join(d, "g_%s.py" % b); shutil.copy(GEN[b], p)
            before = open(p, encoding="utf-8").read(); adds = {}
            for s in fwd:
                assert m.run(s, p, b)[0] == 0, s
                after = open(p, encoding="utf-8").read(); adds[s] = m.added(before, after, s); before = after
            own = m.mine_seq(b)
            mine = set().union(*[adds[x] for x in own])
            assert mine == want[b], (b, sorted(mine ^ want[b]))
            if b == "p":
                assert adds[own[1]] == second and not (adds[own[0]] & second), "the two board P drafts' designators"
            for s, a in adds.items():
                assert s in own or not (a & mine), "%s meets this record's %s" % (s, sorted(a & mine))
            assert not m.duplicates(before), (b, m.duplicates(before))


def t_every_value_is_the_records_and_the_copies_are_pinned():
    m = _M(); chk = _CHK()
    for f, full in m.SOURCES_SHA.items():
        assert _sha(os.path.join(REC, f)) == full, f
        assert full in open(os.path.join(REC, "inputs", "SOURCES.txt"), encoding="utf-8").read(), "SOURCES.txt does not pin %s" % f
    texts = {k: open(os.path.join(REC, v), encoding="utf-8").read() for k, v in m.INPUT_FILES.items()}
    drafts = {b: "".join(open(x, encoding="utf-8").read() for x in m.mine_seq(b)) for b in "pea"}
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
            assert all(m.run(x, t, b)[0] == 0 for x in m.mine_seq(b))
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
        # round 4, DD-5: the ideal diode's nets, each mutation read on the DIO group itself
        for swap, what in (([("Q109", "1"), ("Q109", "5")], "the ideal diode the wrong way round"),
                           ([("U105", "6"), ("U105", "4")], "the controller's ANODE and CATHODE exchanged"),
                           ([("U105", "5"), ("R16", "1")], "the controller's GATE on the gauge's charge switch"),
                           ([("D104", "1"), ("D104", "2")], "EN's diode reversed"),
                           ([("U105", "2"), ("R112", "2")], "the controller's ground on the pack side of R10"),
                           ([("C111", "2"), ("R131", "2")], "the charge pump's capacitor to ground and not to the anode")):
            bad = m.mutate(paths["p"], d, "mut_dio", [tuple(swap)])
            buf = io.StringIO(); kit, v = chk.run({"p": bad}, ROOT, buf)
            assert kit == "FAIL" and "P DIO  FAIL" in buf.getvalue(), "%s and the DIO group did not fail: %s" % (what, buf.getvalue())
        t = os.path.join(d, "breaker_only.py"); shutil.copy(GEN["p"], t)
        assert m.run(m.MINE["p"], t, "p")[0] == 0
        rc, path, _tb = m.netlist_text("p", t, d, "bo")
        buf = io.StringIO(); kit, v = chk.run({"p": path}, ROOT, buf)
        assert rc == 0 and kit == "FAIL" and "P DIO  NOT DRAWN" in buf.getvalue(), "the breaker without the ideal diode did not read FAIL"


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


def t_dd5s_correction_closes_on_read_figures_and_the_old_state_does_not():
    """DD-5 (round 4), case row C-PROT with CHGIN = 1: the defect's figures are record l9stk's and the sheets'; with the ideal diode
    Q109 stays inside its pad and its junction limit at 10 A held, 18 A held and the breaker's 23.93 A held from 76.25 C; the old
    state (Q1's body diode) fails the same limits at every one of them; the BQ4050's documents print no body-diode function; the
    drive, the delays and EN hold their printed limits."""
    m = _need_inputs()
    for sheet in (m.TRM_SHEET, m.BQ4050_SHEET, m.CSD17570_SHEET, m.LM74700_SHEET, m.D4148_SHEET):
        need(sheet, "a maker's sheet DD-5's correction reads")
    texts = {k: open(os.path.join(REC, v), encoding="utf-8").read() for k, v in m.INPUT_FILES.items()}
    B = m.budget(texts["page"])
    R = m.rev_budget(texts["page"], texts["l4e11"], texts["l4e11pre"], B)
    D = m.dd5_budget(texts["page"], B, R)
    assert D["ok"], {k: D[k] for k in ("rth_need", "t_drv_en", "droop", "c111_min", "en_on")}
    assert D["body_diode_hits"] == 0, "the BQ4050's documents now print a body-diode function: approach (i) is to be read again"
    assert (D["p_pad"], D["p_enh"], D["k_hot"], round(D["rds_max"] * 1e6), D["rja"], D["tj_max"]) == (1.48, 0.711, 1.8, 690, 50.0, 150.0), D
    assert [round(x * 1e3) for x in D["vreg"] + D["vfull"] + D["vrev"]] == [13, 20, 29, 34, 50, 57, -17, -11, -2], (D["vreg"], D["vfull"], D["vrev"])
    assert [r["i"] for r in D["rows"]] == [10.0, 18.0, R["i_lim"]] and B["air"] == 76.25, "the case row's currents and start"
    for r in D["rows"]:
        assert r["p109"] <= D["p_pad"] and r["tj_one"] <= D["tj_max"], ("the corrected state", r)
        assert r["p_before"] > D["p_pad"] and B["air"] + r["p_before"] * D["rja"] > D["tj_max"], ("the old state must fail the same limits", r)
        assert r["p109"] < r["p_before"] / 10, r
    assert abs(D["rows"][2]["p2"] - D["p_enh"]) < 5e-4, "Q2's loss is record l9stk's enhanced row"
    assert D["rows"][2]["tj_one"] < 148.5 and 51.0 < D["rth_need"] < 52.0 and 35.0 < D["rth_robust"] < 36.0, (D["rows"][2], D["rth_need"], D["rth_robust"])
    assert D["rows"][0]["tj_hunt"] <= 150 and D["rows"][1]["tj_hunt"] <= 150 and D["rows"][2]["tj_hunt"] > 150, "which rows rest on E-16"
    assert D["t_drv_en"] < D["hold_min"] / 5 and D["vcap_on_min"] - D["droop"] > D["uvlof_max"] + 2 and D["c111_min"] >= 10 * D["ciss_max"], D
    assert D["vcap_off_max"] <= 15 <= D["vgs_abs"] and D["en_on"] < 4.0 and D["i_off"] < 3e-6 and D["i_run"] < 200e-6, D
    dio = open(m.MINE2["p"][0], encoding="utf-8").read()
    for frag in ('pfet5("Q109", "CSD17570Q5B 30 V N-FET', '"IDL_GATE", "SW", "SCP_OUT", "C529279")', 'ic("U105", 6, "LM74700QDBVRQ1',
                 '{"1": "IDL_VCAP", "2": "GND", "3": "IDL_EN", "4": "SW", "5": "IDL_GATE", "6": "SCP_OUT"}, "C2941042")',
                 'c("C111", "220n 50V X7R 0805', '{"1": "IDL_EN", "2": "BRK_VIN"}', 'cls="L"', 'cls="D"', 'cls="B2"'):
        assert frag in dio, frag
    assert '"CHG_G"' not in dio, "the ideal diode draft touches the gauge's charge drive"


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
              "**B-R2's interface, route R1 (section 12f, finding L8P-F04), restated in round 5:**", "| L8P-F04 | A |", "| L8P-F05 | A |", "### 12h. Not taken",
              "**E-14 (record l9stk's, with route R1)**", "**E-12c, a commissioning check like E-12**", "**R10's tolerance and temperature coefficient**",
              "**B-R2's route R1 DRAFTED on board P**", "no new contact",
              "## 13. DD-5: the charge switch's body diode in discharge", "**The case row: C-PROT**", "### 13a. Three approaches compared",
              "**No such function is printed:**", "### 13d. The electrical acceptance on C-PROT with CHGIN = 1", "**Printed guarantees:**",
              "**The condition that stays (E-16).**", "### 13f. The closure credit", "### 13g. What stays open", "**E-8, restated**",
              "**E-12d**, a commissioning check like E-12", "**Round 4 (IF-8, DD-5):**", "### 13h. The ideal diode's own failures",
              "| 10 A held | 30.24 mV, 0.302 W | 10.0 W | 0.124 W | 91.4 C | 97.6 C | 150 C |",
              "| the breaker's 23.93 A held | 30.24 mV, 0.724 W | 23.9 W | 0.711 W | 112.4 C | 148.0 C | 150 C |",
              # rounds 5 and 6
              "**Round 5 (4 October 2026 evening", "### 12f. The interface with L4-E11's DD-7 draft (finding L8P-F04; restated from L4-E11 20c, 20d and 20e",
              "**Round 3's box, and why it is restated.**", "### 12j. The findings L8P-F06 and L8P-F07 (round 5; restated in round 6",
              "#### L8P-F06: the breaker FETs' off leakage into CELL+", "#### L8P-F07: the guard RT1's printed points",
              "**The question to TI (DRAFTED, UNSENT", "**The question to Murata (DRAFTED, UNSENT", "**SESSION decision (round 5, its reason corrected in round 6):**",
              "| L8P-F06 | P, with A |", "| L8P-F07 | A, with P |", "**E-14c** (new)",
              "| C4: `l8p_drafts.out` regenerated on the merged line;", "No stand-in is used since round 5",
              "**Round 6 (4 October 2026 evening, the independent check V2, an AI review).**", "| V2-B2: the F06 figures", "| V2-B3: TDK's",
              "| Left for the breaker pair | 473.9 uA (461.5 uA with BRK_VIN at the clamp) | 786.8 uA |",
              "| In hand with the pair at its ASSUMED 388.0 uA | **85.9 uA** (73.5 uA at the clamp) | 398.8 uA |",
              "| The case at which the pair alone fills it | **103.9 C, 2.9 K over the held case** (103.5 C at the clamp) | 111.2 C |",
              "| The doubling rate at which it fills it at the held case | every 9.63 K or faster (9.68 K at the clamp) | every 8.82 K or faster |",
              "**Acceptance: the pair at most 388 uA at the 101.0 C held case. That keeps both limits:**",
              "**A window exists on the printed limits: 10.51 to 10.62 at 7.6 V (1.0 % wide), 8.53 to 10.62 at 10.6 V.**",
              "| The trip, the junction over that copper (V2-m5) |", "NOT BOUNDED: E11-29's coupon",
              "**U105's package at most 125 C at 23.93 A held (round 6, V2-m7):**", "**The joint case (round 6, V2-m8):**",
              "**L4-E11's DD-7 draft must precede d8dec31's mainpb**",
              # round 6b
              "**Round 6b (4 October 2026 late evening): the copies of L4-E11 taken again at its round 13.**",
              "**What L4-E11's round 13 changed in 20c, and what it did not (round 6b).**", "- **No longer stands:** the \"bound point\" as a bound."):
        assert s in page, s
    for old in ("**No k exists at 7.6 V.**", "does not close at 7.6 V", "the junction at most 134.9 C against 150 C | PRINTED",
                "| 111.7 C | 816.8 uA | the room filled by the pair alone |", "inputs/l4e11-section20c-a09e9a60.md", "inputs/l4e11-section20e-a09e9a60.md",
                "inputs/l4e11-section20c-ac72e730.md", "and nothing on DOCK_EN_OUT, so l9stk's bound point"):
        assert old not in page, "round 5's statement is still on the page: %s" % old
    for ref in ("U101", "R101", "R102", "Q101, Q102", "R103", "C101", "C102", "D101", "R104", "C103", "R105", "D102", "R106", "R107", "Q103",
                "Q104", "R108, R109", "RT101", "R110", "RT1 (board A)"):
        assert "| %s" % ref in page, "the value table omits %s" % ref




def _round5():
    m = _need_inputs()
    for sheet in (m.CSD_SHEET, m.N7002_SHEET, m.PRF_SHEET, m.LM5069_SHEET):
        need(sheet, "a maker's sheet rounds 5 and 6 read")
    texts = {k: open(os.path.join(REC, v), encoding="utf-8").read() for k, v in m.INPUT_FILES.items()}
    B = m.budget(texts["page"])
    R = m.rev_budget(texts["page"], texts["l4e11"], texts["l4e11pre"], B)
    return m, texts, B, R, m.round5(texts, B, R)


def _flat(t):
    return re.sub(r"\s+", " ", t).strip()


def _quotes(sec):
    return [_flat(" ".join(l[2:] for l in grp.split("\n"))) for grp in re.findall(r"(?m)((?:^> .*\n?)+)", sec)]


def t_round5_the_interface_is_quoted_from_the_copies_not_typed():
    """12f and 12j: every blockquote and every quoted cell of the interface table occurs, whitespace aside, in the copy of L4-E11's
    section it names (20c, 20d, 20e or 22g at the commit L4E11_AT names); the delays the output sums agree with 20d's. Since round
    6b 12f carries a third quote, 20c's own withdrawal of record l9stk's 47 kOhm "bound point"."""
    m, texts, B, R, F = _round5()
    page = open(PAGE, encoding="utf-8").read()
    sec = page.split("### 12f.")[1].split("### 12g.")[0]
    copy = {"20c": _flat(texts["l4e11c"]), "20d": _flat(texts["l4e11d"]), "20e": _flat(texts["l4e11e"]), "22g": _flat(texts["l4e11_22g"])}
    quotes = _quotes(sec)
    assert len(quotes) == 3 and all(q in copy["20c"] for q in quotes), [q for q in quotes if q not in copy["20c"]]
    assert sum("withdrawn as a bound by round 13, 23g" in q for q in quotes) == 1, "round 6b's quote of the restated 20c"
    rows = [l for l in sec.split("\n") if l.startswith("| ") and l.rstrip().endswith(("| 20c |", "| 20d |", "| 20e |"))]
    assert len(rows) == 10, rows
    for l in rows:
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        parts = re.findall(r'"(.+?)"', cells[1])
        assert parts and all(_flat(q) in copy[cells[2]] for q in parts), (cells[2], [q for q in parts if _flat(q) not in copy[cells[2]]])
    f06 = page.split("#### L8P-F06:")[1].split("#### L8P-F07:")[0]
    q6 = _quotes(f06)
    assert len(q6) == 3 and q6[0] in copy["20e"] and q6[1] in copy["20e"] and q6[2] in copy["22g"], q6
    assert (F["t_set"], F["t_end"], F["hold_min"], F["restart_l4"]) == (0.85e-3, 1.41e-3, 1.341, 0.9477), F
    assert abs(round(R["t_d"] * 1e3, 2) + F["t_set"] * 1e3 - F["t_end"] * 1e3) < 0.011, "board P's pull plus board A's set is 20d's sum"
    assert abs(F["restart_l4"] - R["t_restart"]) < 5e-5 and abs(F["hold_min"] - R["t_restart"] - F["over_rs"]) < 1e-3


def t_round6_no_copy_of_l4e11_is_a_round_behind_the_tree():
    """The check V2's V2-B2: round 5's copies were L4-E11's round 10 while the candidate held round 11, and no test saw it, because
    the quotes were read against the copies alone. Now every copy is compared with records/l4e11/ wherever the tree holds
    L4-E11's round 10 or later: a copied section that is not in the tree's page word for word, or a copied draft whose bytes
    differ, fails. The guard is exercised on a scratch tree: the copies themselves pass; round 11's 20e (0.597 mA) and a DD-7
    draft with R256 at 6.8k each fail. This record's own tree holds an older L4-E11 (before its round 10), which the copies
    cannot be behind."""
    m = _M()
    assert all(m.L4E11_AT in v for k, v in m.INPUT_FILES.items() if k.startswith(("l4e11c", "l4e11d", "l4e11e", "l4e11_22")))
    assert all(m.L4E11_AT in c for c, _n in m.L4E11_DRAFTS) and all(m.L4E11_AT in f for f, _a in m.FOLLOW["a"])
    assert all(m.L4E11_AT in v for k, v in m.REPLACED.items() if k[0] == "l4e11"), "a composition still uses an older copy of L4-E11's drafts"
    assert not [f for f in os.listdir(os.path.join(REC, "inputs")) if "a09e9a60" in f or "ac72e730" in f], "round 10's or round 12's copies are still in inputs/"
    assert (m.L4E11_AT, m.L4E11_ROUND) == ("4def5975", 13), "the round copied moved: read every quote of a changed section again (the brief of round 6b)"
    assert m.stale_copies(os.path.join(ROOT, "v2", "docs", "records", "l4e11")) == [], "a copy of L4-E11 is not the tree's: take it again (V2-B2)"
    with tempfile.TemporaryDirectory() as d:
        page = "## 20. Round 10\n\n" + "".join(open(os.path.join(REC, m.INPUT_FILES[k]), encoding="utf-8").read() for k, _h in m.L4E11_SECTIONS)
        open(os.path.join(d, "L4E11-SOURCE-ONLY-AND-ENTRY.md"), "w", encoding="utf-8").write(page)
        for c, n in m.L4E11_DRAFTS:
            shutil.copy(os.path.join(REC, c), os.path.join(d, n))
        assert m.stale_copies(d) == [], "the copies do not pass against a tree made of themselves"
        r12 = page.replace("**withdrawn as a bound by round 13, 23g:** ", "")        # round 12's 20c did not carry the withdrawal: round 6's copies against round 13
        assert r12 != page
        open(os.path.join(d, "L4E11-SOURCE-ONLY-AND-ENTRY.md"), "w", encoding="utf-8").write(r12)
        bad = m.stale_copies(d)
        assert len(bad) == 1 and "### 20c." in bad[0], bad
        r11 = page.replace("stays under **0.846 mA** together", "stays under **0.597 mA** together")
        assert r11 != page
        open(os.path.join(d, "L4E11-SOURCE-ONLY-AND-ENTRY.md"), "w", encoding="utf-8").write(r11)
        bad = m.stale_copies(d)
        assert len(bad) == 1 and "### 20e." in bad[0], bad
        open(os.path.join(d, "L4E11-SOURCE-ONLY-AND-ENTRY.md"), "w", encoding="utf-8").write(page)
        dd7 = os.path.join(d, "apply_gen_sch_a_dd7.py")
        t = open(dd7, encoding="utf-8").read(); t2 = t.replace('r("R256", "4.7k 1%"', 'r("R256", "6.8k 1%"')
        assert t2 != t
        open(dd7, "w", encoding="utf-8").write(t2)
        bad = m.stale_copies(d)
        assert len(bad) == 1 and "apply_gen_sch_a_dd7.py" in bad[0], bad
        os.remove(dd7)
        assert any("apply_gen_sch_a_dd7.py" in x for x in m.stale_copies(d)), "a draft missing from a round 10 tree is not reported"


def t_round6_l8p_f06_the_breaker_fets_leakage_against_both_limits():
    """L8P-F06 on L4-E11's round 12 (V2-B2): two limits, the static 0.846 mA and the timing 520.7 uA, both read from the copies; the
    timing limit and the bleed at the hot bound are reproduced from L4-E11's printed inputs; with the LM5069's 1 MOhm and the
    battery FETs' printed 30 uA counted, the timing limit leaves the breaker pair 473.9 uA and the static 786.8 uA; on the ASSUMED
    doubling the pair's 388.0 uA at the held case is 85.9 uA inside the timing limit, which the pair alone fills from 103.9 C or by
    a doubling every 9.63 K (the static: 111.2 C, 8.82 K). E-14c's acceptance keeps the TIMING limit: a pair leakage that round
    5's single static room would have passed (500 uA) does not end the bleed inside the hold."""
    m, texts, B, R, F = _round5()
    for k, want in (("i_static", 0.846e-3), ("i_timing", 520.7e-6), ("l4_each", 272e-6), ("hot_bound", 434.8e-6), ("bleed_hot", 1.218)):
        assert abs(F[k] / want - 1) < 1e-9, (k, F[k])
    assert R["r_so"] == 1e6
    for k, want in (("r256", 4700.0), ("r256_tol", 0.01), ("v_dead", 4.076), ("v_foot", 0.060), ("v0", 17.375), ("c_fused", 104e-6), ("c_tol", 0.20)):
        assert abs(F[k] / want - 1) < 1e-9, (k, F[k])
    assert abs(F["bat25"] - 3e-6) < 1e-12 and abs(F["bat125"] - 30e-6) < 1e-12, "Nexperia's rows as L4-E11 22b quotes them"
    assert (F["idss"], F["idss_v"], F["idss_rows"]) == (1e-6, 32.0, 1), "the sheet now prints another IDSS row: read it instead of the assumption"
    assert F["idss_v"] >= m.V_CLAMP and m.IDSS_DOUBLING == 10.0 and F["t_case"] == 101.0 and F["t_air"] == 76.25
    assert abs(F["pair_case"] - 2e-6 * 2 ** 7.6) < 1e-12 and abs(F["pair_case"] - 388.0e-6) < 0.1e-6, F["pair_case"]
    # the limits reproduced, by this test's own arithmetic as well
    rc, v_inf = 4700 * 1.01 * 104e-6 * 1.2, lambda i: 0.060 + i * 4700 * 1.01
    bleed = lambda i: rc * math.log((17.375 - v_inf(i)) / (4.076 - v_inf(i)))
    assert abs(bleed(434.8e-6) - 1.218) < 0.002 and abs(F["bleed_hot_re"] - bleed(434.8e-6)) < 1e-9, bleed(434.8e-6)
    assert bleed(F["i_timing_re"] * 0.999) < 1.341 < bleed(F["i_timing_re"] * 1.001) and abs(F["i_timing_re"] / 520.7e-6 - 1) < 0.005, F["i_timing_re"]
    assert abs(F["i_static_re"] - (4.076 - 0.060) / 4747.0) < 1e-12 and abs(F["i_static_re"] / 0.846e-3 - 1) < 0.001
    # what each limit leaves the pair
    assert abs(F["room_timing"][16.8] - 473.9e-6) < 1e-9 and abs(F["room_timing"][m.V_CLAMP] - 461.5e-6) < 1e-9, F["room_timing"]
    assert abs(F["room_static"][m.V_CLAMP] - 786.8e-6) < 1e-9 and round(F["l4_each_re"] * 1e6) == 272
    assert abs(F["left_timing"][16.8] - 85.9e-6) < 0.06e-6 and abs(F["left_static"] - 398.8e-6) < 0.06e-6
    assert abs(F["t_fill_timing"][16.8] - 103.9) < 0.05 and abs(F["d_fill_timing"][16.8] - 9.63) < 0.005, (F["t_fill_timing"], F["d_fill_timing"])
    assert abs(F["t_fill_static"] - 111.2) < 0.05 and abs(F["d_fill_static"] - 8.82) < 0.005, (F["t_fill_static"], F["d_fill_static"])
    assert abs(F["each_left_timing"] - 38.63e-6) < 0.01e-6 and abs(F["each_left_static"] - 142.93e-6) < 0.01e-6
    assert F["f06_static"] and F["f06_timing"] and F["f06_holds"] and F["pair_125"] > F["i_static"]
    assert F["t_fill_timing"][16.8] < F["t_fill_static"] and F["left_timing"][16.8] < F["left_static"], "the timing limit is the nearer one"
    # the old statement fails here: round 5's single static room passed any pair under 816.8 uA; 500 uA breaks the timing
    old_room = F["i_static"] - F["i_so"][m.V_CLAMP]
    assert abs(old_room - 816.8e-6) < 1e-9 and 500e-6 < old_room, "round 5's room"
    assert 500e-6 > F["room_timing"][16.8] and F["bleed_fn"](F["i_so"][16.8] + F["bat125"] + 500e-6) > F["hold_min"], "500 uA must not end the bleed inside the hold"
    assert F["bleed_fn"](F["i_so"][16.8] + F["bat125"] + 388e-6) < F["hold_min"], "E-14c's 388 uA keeps the timing limit"
    assert abs(F["bleed_pair_case"] - F["bleed_hot_re"]) < 1e-3 and F["hold_min"] - F["bleed_pair_case"] > 0.12


def t_round5_l8p_f07_rt1s_printed_and_typical_points_against_the_loop():
    """L8P-F07 (V1's condition C3): Murata's row is read from the sheet's text under its own column header (100 kOhm over 110 C,
    4.7 MOhm at 130 +-3 C), and record l9stk's '47 kOhm at 130 C' is the 470 ohm groups' column; the loop's thresholds reproduce
    L4-E11 20c's nominal 61.3 and 201.2 kOhm and tighten with the loads and 1 % parts; the trip side's resistance is printed; the
    junction over the sensor's copper is on L4-E11's worst split (1.513 W, 2.12 K over its own base) and the base against the
    sensor is not bounded (V2-m5), where round 5 added the even split's 1.88 K; the no-trip side at 10 A only from about 15.5 V,
    the 18 A side not at all; on the typical curve 10 A holds and the 18 A service held does not, for every R25 the sheet allows."""
    m, texts, B, R, F = _round5()
    g = F["prf"]["PRF15BB103RB6RC"]
    assert (g["r25"], g["tol"], g["gt"], g["t1"], g["t1_tol"], g["r1"], g["t2"], g["t2_tol"], g["r2"], g["vmax"], g["tmin"], g["tmax"]) == \
        (10e3, 0.5, True, 110.0, None, 100e3, 130.0, 3.0, 4.7e6, 32.0, -20.0, 140.0), g
    b = F["prf"]["PRF15BB102RB6RC"]
    assert (b["r25"], b["t1"], b["t1_tol"], b["r1"], b["t2"], b["t2_tol"], b["r2"]) == (1e3, 115.0, 5.0, 10e3, 130.0, 3.0, 100e3), b
    assert F["l9_47k"] and F["hdr_47k"] == ["4.7kohm"], "l9stk's 47 kOhm reading or the sheet's 470 ohm column changed"
    assert abs(F["nom_on"] - F["l4_on"]) < 50 and abs(F["nom_off"] - F["l4_off"]) < 50, "L4-E11 20c's nominal thresholds"
    assert F["on"][10.6] < F["nom_on"] and 58.0e3 < F["on"][10.6] < 58.8e3 and 110.5e3 < F["on"][16.8] < 111.3e3, F["on"]
    assert 203.0e3 < F["off"][10.6] < 203.8e3 and 340.8e3 < F["off"][16.8] < 341.6e3, F["off"]
    assert 3.55e3 < F["low"][7.6] < 3.60e3 and F["low"][7.6] > 3.46e3, "with the return at 0 V the least RT1 is over V1's 3.46 kOhm"
    assert (F["tj10"], F["tj18"], F["tj24"], F["lead24"]) == (89.4, 118.0, 150.0, 1.88), F
    # the trip side: the resistance is printed; the junction is on the worst split and its base against the sensor is not bounded
    assert F["trip_print"] and g["r2"] > F["off"][16.8]
    assert (F["p_worst"], F["rth_jmb"], F["p_even"]) == (1.513, 1.4, 1.345) and abs(F["p_worst"] / F["p_even"] - 9 / 8) < 0.001
    assert abs(F["lead_worst"] - 2.1182) < 1e-4 and F["lead_worst"] > F["lead24"], "the worst split's lead, not the even split's 1.88 K"
    assert abs(F["trip_tj_worst"] - 135.12) < 0.005 and abs(F["trip_room"] - 14.88) < 0.005, (F["trip_tj_worst"], F["trip_room"])
    assert not F["notrip10_print_low"] and F["notrip10_print_high"] and not F["notrip18_print"]
    assert 15.3 < F["v_print"] < 15.7 and F["v_print"] < B["vmax"], F["v_print"]
    pts = m.PRF_BB_TYP
    assert all(a[0] < b_[0] and a[1] < b_[1] for a, b_ in zip(pts, pts[1:])), "the read curve is not monotonic"
    assert abs(F["curve_x10"] - b["t1"]) <= b["t1_tol"] and abs(F["curve_x100"] - b["t2"]) <= b["t2_tol"], "the 1 kOhm group's points"
    assert F["curve_at_r2"] < F["print_at_r2"] / 1.5, "the curve is not the 10 kOhm part's own above x10"
    assert F["f07_typ_10"] and F["r10_typ"] < F["window"] < F["on"][10.6]
    assert not F["f07_typ_18"] and min(F["r18_typ"]) > F["on"][10.6] and F["r18_typ_cu_lo"] > F["on"][10.6], F["r18_typ"]
    assert F["onset"]["most"] < F["onset"]["nominal"] < F["onset"]["least"] < F["cu18"] < F["tj18"], F["onset"]
    assert 60.0 < F["tau_need"]["most"] < 62.0 and F["tau_need"]["least"] < F["tau_need"]["nominal"] < F["tau_need"]["most"]
    assert F["win_typ"] < F["window"] and F["low_typ"] > F["low"][7.6], (F["win_typ"], F["low_typ"])
    assert F["ba102_notrip"] and not F["ba102_trip"] and not F["ba102_low"]


def t_round6_tdks_window_takes_the_sure_off_as_a_lower_bound():
    """The check V2's V2-B3: with R106 and R107 divided by k the loop sees k x R. No trip to 125 C is an upper bound on k (10.62),
    surely off by 145 C a LOWER bound (8.53), the held reading a lower bound (10.51 at 7.6 V, 6.84 at 10.6 V): a window exists at
    both voltages, 10.51 to 10.62 and 8.53 to 10.62. The window is checked against the three conditions themselves by a scan of
    k; round 5's form (the sure-off as an upper bound) is a mutation of tdk_window and must disagree with that scan. NOT
    SELECTED rests on the dissipation against the sheet's 6 mW note, the static draw, and the sheet's typical table (Rmin 212 ohm
    at 100 C: no k at either voltage)."""
    import inspect
    m, texts, B, R, F = _round5()
    T5 = m.TDK_B59721
    on, off, low = F["on"][10.6], F["off"][16.8], F["low"]
    assert abs(F["tdk_k_notrip"] - on / 5.5e3) < 1e-9 and abs(F["tdk_k_trip"] - off / 40e3) < 1e-9
    assert round(F["tdk_k_notrip"], 2) == 10.62 and round(F["tdk_k_trip"], 2) == 8.53 and round(F["tdk_k_low"][7.6], 2) == 10.51 and round(F["tdk_k_low"][10.6], 2) == 6.84

    def scan(v, r_least):          # the conditions themselves, no bound algebra: every k in 1.00 .. 20.00 by 0.001
        ok = [k / 1000.0 for k in range(1000, 20001) if (k / 1000.0) * T5["r_m5"] <= on and (k / 1000.0) * T5["r_p15"] >= off and (k / 1000.0) * r_least >= low[v]]
        return (ok[0], ok[-1]) if ok else None
    for v in (7.6, 10.6):
        want = scan(v, T5["rr"] * (1 - T5["drr"]))
        lo, hi = F["tdk_win"][v]
        assert want and F["tdk_fits"][v] and abs(lo - want[0]) < 0.002 and abs(hi - want[1]) < 0.002, (v, want, lo, hi)
    assert [round(x, 2) for x in F["tdk_win"][7.6]] == [10.51, 10.62] and [round(x, 2) for x in F["tdk_win"][10.6]] == [8.53, 10.62]
    assert 0.009 < F["tdk_width"][7.6] < 0.011
    # the mutation: round 5's direction (the sure-off as an upper bound) must fail the same scan
    src = inspect.getsource(m.tdk_window)
    mut = src.replace("return max(k_low, k_trip), k_notrip", "return k_low, min(k_trip, k_notrip)")
    assert mut != src, "tdk_window no longer reads as this test expects"
    ns = {}
    exec(mut, ns)
    lo_m, hi_m = ns["tdk_window"](F["tdk_k_low"][7.6], F["tdk_k_trip"], F["tdk_k_notrip"])
    assert lo_m > hi_m and scan(7.6, T5["rr"] * (1 - T5["drr"])) is not None, "the mutated bound must say 'no k at 7.6 V' where the scan finds one"
    # the grounds NOT SELECTED stands on, each with its printed figure
    assert T5["p_meas"] == 6e-3 and F["tdk_p"][0] > 3 * T5["p_meas"] and abs(F["tdk_p"][0] - 18.1e-3) < 0.1e-3 and abs(F["tdk_p"][1] - 21.4e-3) < 0.1e-3, F["tdk_p"]
    assert abs(F["tdk_static"][0] - 4.11e-3) < 0.01e-3 and abs(F["tdk_static"][1] - 5.01e-3) < 0.01e-3 and F["tdk_static"][0] > 9 * F["static"]
    assert (T5["rmin_ref"], T5["t_rmin_ref"]) == (212.0, 100) and round(F["tdk_k_low_ref"][7.6], 2) == 16.86 and round(F["tdk_k_low_ref"][10.6], 2) == 10.98
    assert not any(F["tdk_fits_ref"].values()) and scan(10.6, T5["rmin_ref"]) is None and scan(7.6, T5["rmin_ref"]) is None
    assert abs(F["tdk_trip_tj"] - (145 + F["lead_worst"])) < 1e-9 and F["tdk_trip_tj"] < 150.0


def t_round5_the_alternative_parts_typed_figures_are_tdks():
    """TDK's B59721A figures in l8p_drafts.py are the held sheet's p.4 table and, since round 6, its p.29 reference table (held
    back by its notice; skipped when absent)."""
    m = _M()
    need(m.TDK_SHEET, "TDK's held sheet (python3 v2/docs/records/l8p/fetch_held_back.py)")
    t = m.pdftext(m.TDK_SHEET)
    T = m.TDK_B59721
    assert "Reproduction, publication and dissemination of this publication" in t, "the notice the sheet is held back by"
    page4 = t.split("Page 3 of 35")[1].split("Page 4 of 35")[0]
    assert re.search(r"\(Tsense,1 .5°C\) \(Tsense,1 \+5°C\)\s+\(Tsense,1 \+15°C\)", page4), "the 0805 table's columns"
    for ts in T["tsense"]:
        row = re.search(r"^%d\s+±%d\s+%d\s+≤ ([0-9.]+)\s+≥ ([0-9.]+)\s+≥ ([0-9.]+)\s+B59721A0%03dA062" % (T["rr"], T["drr"] * 100, ts, ts), page4, re.M)
        assert row and tuple(float(x) * 1e3 for x in row.groups()) == (T["r_m5"], T["r_p5"], T["r_p15"]), ts
    assert re.search(r"Max\. operating voltage\s+Vmax\s+%d\s+V DC" % T["vmax"], t)
    assert "should be below\n6 mW for EIA case size 0805" in page4 and T["p_meas"] == 6e-3
    # p.29: the last of the seven 0805 tables; its ordering code is in the figure only, so the table is identified by the rows
    # that carry the type's printed limits (5.5 kOhm at most at 125 C, 13.3 kOhm at least at 135 C)
    page29 = t.split("Page %d of 35" % (T["page_ref"] - 1))[1].split("Page %d of 35" % T["page_ref"])[0]
    assert "Characteristics (typical) for case size 0805" in page29 and "Rmin and Rmax values are typical values for reference only." in page29
    assert re.search(r"\b125\s+410\s+1\.300\s+5\.500\b", page29) and re.search(r"\b135\s+13\.300\s+62\.000\b", page29), "p.29 is not the 130 C type's table"
    assert re.search(r"\b%d\s+%d\s+390\s+605\b" % (T["t_rmin_ref"], T["rmin_ref"]), page29) and re.search(r"\b25\s+%d\s+680\s+1\.020\b" % T["rmin25_ref"], page29)
    num = lambda x: float(x.replace(".", "")) if re.fullmatch(r"\d{1,3}\.\d{3}", x) else float(x)     # the sheet writes 1.670 for 1670 ohm
    rmins = []
    for l in page29.split("\n"):
        r_ = re.match(r"\s*[^\d\s]?\s*\d+\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+([\d.]+)", l)      # T (its minus a non-ASCII sign), Rmin, Rtypical, Rmax, T, Rmin
        if r_:
            rmins += [num(r_.group(1)), num(r_.group(5))]
    assert len(rmins) >= 22 and min(rmins) == T["rmin_ref"], ("the table's least Rmin", sorted(rmins)[:3])


def t_round6_the_lists_whole_order_composes_wherever_its_drafts_are():
    """The check V2's V2-m9: board A (and board E) composed in L4-E9's list order as the candidate carries it. The rows whose
    drafts this record's tree does not hold (record l8r2's packrtn, slotlm and fb01 on board A, packrtn on board E) are named;
    wherever a tree holds them they are composed in their place, right before this record's draft. Either way the composed
    generator runs to its end, the netlist check reads DRAWN, and a mutation of the composed board A reads FAIL. A tree that
    holds some of them and not the others fails."""
    m = _need_inputs(); chk = _CHK()
    with tempfile.TemporaryDirectory() as d:
        for b in "ae":
            seq, missing = m.list_order_full(b)
            assert missing in ([], list(m.LIST_ABSENT[b])), "the tree holds some of the list's l8r2 drafts and not the others: %r" % (missing,)
            mine = m.mine_seq(b)[0]
            held = [x for x in seq if "/l8r2/" in x.replace(os.sep, "/") and os.path.basename(x) in
                    ["apply_gen_sch_%s_%s.py" % (b, n) for _r, n, _row in m.LIST_ABSENT[b]]]
            assert len(held) == len(m.LIST_ABSENT[b]) - len(missing) and all(seq.index(x) < seq.index(mine) for x in held)
            if b == "a":
                dd7, mainpb = m.FOLLOW["a"][0][0], m.draft("d8dec31", "mainpb", "a")
                assert seq.index(mine) < seq.index(dd7) < seq.index(mainpb), "the list's 3g and 3h: ptc, dd7, then mainpb"
                assert not any("d8v3" in x or "vbus20ov" in x for x in seq), "the list does not name l8r2's d8v3 and vbus20ov"
            p, res = m.compose(b, seq, d, "list")
            assert len(res) == len(seq) and all(v.startswith("OK") for _s, v in res), (b, res)
            rc, path, table = m.netlist_text(b, p, d, "list")
            assert rc == 0 and table["intent_written"], (b, path)
            buf = io.StringIO(); kit, v = chk.run({b: path}, ROOT, buf)
            assert kit == "DRAWN", buf.getvalue()
            if b == "a":
                bad = m.mutate(path, d, "mut_list", [(("U48", "2"), ("U48", "1"))])
                kit, v = chk.run({"a": bad}, ROOT, io.StringIO())
                assert kit == "FAIL", "U48's VDD on the return and the list-order board A did not fail"
    # the DD-7 draft after mainpb is refused (mainpb then holds R233 and C241): the order constraint the page states
    with tempfile.TemporaryDirectory() as d:
        p, res = m.compose("a", m.order("a", "last") + [m.FOLLOW["a"][0][0]], d, "late")
        assert res[-1][1].startswith("REFUSED") and "R233" in res[-1][1] and all(v.startswith("OK") for _s, v in res[:-1]), res[-2:]


def t_round6_the_ptc_draft_quotes_what_murata_prints():
    """Round 6: board A's PTC draft quoted record l9stk 15.5's '47 kOhm at 130 C' in its docstring, in the comment it writes and
    in RT1's value text; Murata prints 100 kOhm over 110 C and 4.7 MOhm at 130 +-3 C for this part (the 47 kOhm column is the 470
    ohm groups'). The draft and the generator it produces carry the printed points and not the old quote."""
    m, texts, B, R, F = _round5()
    g = F["prf"]["PRF15BB103RB6RC"]
    assert (g["r1"], g["gt"], g["t1"], g["r2"], g["t2"], g["t2_tol"]) == (100e3, True, 110.0, 4.7e6, 130.0, 3.0)
    src = open(m.MINE["a"], encoding="utf-8").read()
    doc = src.split('"""')[1]
    assert "100 kOhm at a sensing" in doc and "over 110 C, 4.7 MOhm at 130 +-3 C" in _flat(doc) and "L8P-F07, OPEN" in doc
    assert "47 kOhm at 130 +-3 C, 32 V" not in src and "47 kOhm point (127 to 133 C)" not in src and "47k at 130 C" not in src, "the old quote is back"
    with tempfile.TemporaryDirectory() as d:
        t = os.path.join(d, "gen_sch_a.py"); shutil.copy(GEN["a"], t)
        assert m.run(m.MINE["a"], t, "a")[0] == 0
        gen = open(t, encoding="utf-8").read()
        assert '"PRF15BB103RB6RC chip PTC 10k, 100k over 110 C, 4.7M at 130 C (Murata)' in gen and "47k at 130 C" not in gen
        assert "Murata prints 100 kOhm\n# over 110 C and 4.7 MOhm at 130 +-3 C" in gen and "47 kOhm point" not in gen


def t_round6_e8_measures_the_joint_case_and_e16_reads_u105():
    """The check V2's V2-m8 and V2-m7: at 23.93 A held board P dissipates 4.57 W in all (Q109, Q2, the breaker pair, R10 and the
    sense pair, each from the drawn values); the sheet's 50 C/W is one device on a 1.5 in x 1.5 in board, three such boards are
    6.75 in2 and board P is 4.77 in2 a face, so the pads' figures cannot all be the sheet's at once; E-8 says so and E-16 reads
    U105's package against TI's 125 C."""
    m, texts, B, R, F = _round5()
    D = m.dd5_budget(texts["page"], B, R)
    j = dict(D["joint"])
    assert abs(j["Q109"] - 0.724) < 5e-4 and abs(j["Q2"] - 0.711) < 5e-4 and abs(j["R10"] - 23.93 ** 2 * 2e-3) < 1e-9
    assert abs(j["Q101 and Q102"] - 2 * (23.93 / 2) ** 2 * 0.96e-3 * 1.8) < 1e-9
    v = 23.93 / (1 / 4e-3 + 1 / 7.5e-3)
    assert abs(j["R101"] - v * v / 4e-3) < 1e-9 and abs(j["R102"] - v * v / 7.5e-3) < 1e-9
    assert abs(D["p_joint"] - sum(j.values())) < 1e-12 and 4.5 < D["p_joint"] < 4.65, D["p_joint"]
    assert abs(D["board_in2"] - 70.0 * 44.0 / 645.16) < 1e-9 and D["pads_in2"] == 6.75 and D["board_in2"] < D["pads_in2"]
    page = open(PAGE, encoding="utf-8").read()
    e8 = [l for l in page.split("\n") if l.startswith("| **E-8, restated** |")][0]
    e16 = [l for l in page.split("\n") if l.startswith("| **E-16**, ")][0]
    assert "4.57 W in all at 23.93 A held" in e8 and "6.75 in2" in e8 and "4.77 in2" in e8 and "measures that joint case" in e8
    assert "U105's package at most 125 C at 23.93 A held" in e16 and "TJ -40 to 125 C only (SNOSD17G 6.5)" in e16
    lm = m.pdftext(m.LM74700_SHEET)
    assert re.search(r"6\.5 Electrical Characteristics\s*\nTJ = –40°C to \+125°C", lm), "SNOSD17G 6.5's temperature range"


def t_round6_the_l4e11_pin_draft_moves_one_pin_and_only_behind_the_draft():
    """Round 6 changed the PTC draft's bytes, and L4-E11's test pins them (L8P3_PTC). apply_test_l4e11_ptc_pin.py, a draft for the
    integrator, moves that one pin: it carries the sha256 the tree's PTC draft has now, checks before it writes, applies once,
    refuses a second time, and refuses a test_l4e11.py that does not carry the old pin (this tree's own, main's)."""
    m = _M()
    s = os.path.join(REC, "apply_test_l4e11_ptc_pin.py")
    pin = _mod("l8p_pin_under_test", "apply_test_l4e11_ptc_pin.py")
    assert _sha(m.MINE["a"]) == pin.NEW and pin.OLD != pin.NEW, "the pin draft's NEW is not the tree's PTC draft: take it again"
    tree_test = os.path.join(TESTS, "test_l4e11.py")
    before = _sha(tree_test) if os.path.isfile(tree_test) else None
    with tempfile.TemporaryDirectory() as d:
        t = os.path.join(d, "test_l4e11.py")
        body = "import os\n" + pin.LINE % pin.OLD + "\nX = 1\n"
        open(t, "w", encoding="utf-8").write(body)
        r = _run([s, t]); assert r.returncode == 0 and b"CHECK OK" in r.stdout and open(t, encoding="utf-8").read() == body, r.stderr.decode()[-300:]
        r = _run([s, t, "--write"]); assert r.returncode == 0 and b"WRITTEN" in r.stdout, r.stderr.decode()[-300:]
        assert open(t, encoding="utf-8").read() == body.replace(pin.OLD, pin.NEW)
        assert _run([s, t, "--write"]).returncode == 3, "a second application was not refused"
        open(t, "w", encoding="utf-8").write("import os\nX = 1\n")
        assert _run([s, t, "--write"]).returncode == 3 and open(t, encoding="utf-8").read() == "import os\nX = 1\n", "a file without the pin was written"
    if before is not None:
        text = open(tree_test, encoding="utf-8").read()
        if pin.LINE % pin.OLD not in text and pin.LINE % pin.NEW not in text:
            assert _run([s]).returncode == 3, "a test_l4e11.py without the pin was not refused"
        assert _sha(tree_test) == before, "the pin draft wrote into the tree"


def t_round6b_l4e11s_round_13_moved_no_figure_this_record_reads():
    """Round 6b: L4-E11's round 13 restated its 20c on Murata's printed points (record l9stk's 47 kOhm 'bound point' withdrawn as a
    bound) and changed no other section this record copies. Every figure this record reads of 20c, 20d, 20e and 22 is what it was
    at round 12: the held, closed and powered readings, the dead and alive readings, the load on the return, the window, the
    first inverter's band, the delays, the two limits. The page no longer leans on the bound point (12e's sentence restated),
    and the sections that did not change carry the sha256 they had at ac72e730."""
    m, texts, B, R, F = _round5()
    c20 = texts["l4e11c"]
    assert "**withdrawn as a bound by round 13, 23g:** 47 kOhm is\nnot a point of this part" in c20 and "which bounds nothing: round 13, 23g" in c20
    assert "**The bound point** (record l9stk, 10.6 V, RT1 47 kOhm)" not in c20, "the copy is round 12's 20c"
    assert (m.RET_LOW, m.RET_HIGH, m.OUT_POWERED) == (0.7755, 0.84, 1.981)
    for k, want in (("v_dead", 4.076), ("v_alive", 4.774), ("v_foot", 0.060), ("load_ret", 2e-6), ("load_out", 984e3), ("window", 25.8e3),
                    ("l4_on", 61.3e3), ("l4_off", 201.2e3), ("l4_v", 10.6), ("t_set", 0.85e-3), ("t_end", 1.41e-3), ("hold_min", 1.341),
                    ("i_static", 0.846e-3), ("i_timing", 520.7e-6), ("hot_bound", 434.8e-6), ("bleed_hot", 1.218), ("p_worst", 1.513)):
        assert abs(F[k] / want - 1) < 1e-9, "a figure read from L4-E11's copies moved: %s is %r" % (k, F[k])
    assert abs(F["room_timing"][16.8] - 473.9e-6) < 1e-9 and abs(F["left_timing"][16.8] - 85.9e-6) < 0.06e-6 and abs(F["room_static"][m.V_CLAMP] - 786.8e-6) < 1e-9
    same = {"20d": "a5b5b306dadd2a147dfc18acc3fc9f31f0ba97ec00f25859054507b45bf96241", "20e": "9f3d4e017226d18f9579599137c132521094f976a48c01bd83e23b8dd61f9e3a",
            "22b": "583a346a0d2fa2119790f637ceb40bb90fb5cd9b05b806433fc5e960e66f9a45", "22c": "a90a69fa982e8db857efc37aa00fc54063740f660061c9c60840eeffe41278ec",
            "22g": "0595a5a24a5bbc34c1bb49fb5f464cf5e553f129fbf06dee098d0d145e3ee704", "22h": "b65f1dcdb0f61d3cbceb955c4d4e14e82827ec0c596c3b3b6b85866f9652c15f"}
    for sec, sha_ in same.items():
        assert m.SOURCES_SHA["inputs/l4e11-section%s-%s.md" % (sec, m.L4E11_AT)] == sha_, "section %s is no longer round 12's bytes: read its quotes again" % sec
    assert m.SOURCES_SHA["inputs/l4e11-section20c-%s.md" % m.L4E11_AT] != "c860006f87a5777add732c3868c7b17ce3643546afcfc5eb139b4d9377da0086", "20c is still round 12's"
    page = open(PAGE, encoding="utf-8").read()
    e12 = page.split("### 12e.")[1].split("### 12f.")[0]
    assert "so the detector moves no level of the loop." in e12 and "is withdrawn as a bound: 12f, round 6b" in e12
    assert "and nothing on DOCK_EN_OUT, so l9stk's bound point" not in page, "12e still leans on the withdrawn bound point"
