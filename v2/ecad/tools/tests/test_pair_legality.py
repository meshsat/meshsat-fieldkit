#!/usr/bin/env python3
"""The pair copper is put to the DRC before anything is laid around it, and a pair the DRC refuses comes off whole
(MESHSAT-862, 15 September 2026).

B19's first route for a deliverable ended before it started: the pre-route DRC on the pair copper read 64 hard items,
all of the pre-router's making (the placed board reads 0), and the chain would have routed six hours towards a finish
that refuses locked copper it cannot change. Three causes are fixed at their source, and one floor catches the rest.
"""
import os, json

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(os.path.dirname(os.path.dirname(TOOLS)), "docs")
PRE = open(os.path.join(TOOLS, "pair_preroute.py")).read()
FULL = open(os.path.join(TOOLS, "full.sh")).read()
PRUNE_PATH = os.path.join(TOOLS, "pair_prune.py")


def t_the_pair_copper_meets_the_drc_before_the_fanout_on_every_board():
    i = FULL.find("pair_prune.py"); assert i > 0, "no board's pair copper is put to the DRC before the fanout"
    assert FULL.find("pair_preroute.py") < i < FULL.find("prefanout.py"), "the prune must run after the pre-router and before the fanout"
    assert "pre-route DRC on the pair copper" in FULL, "the pair copper's own hard count is not printed for the record"


def t_a_pruned_pair_holds_a_board_that_declares_no_fraction():
    assert '[ "$PRUNE" -ne 2 ] || [ "$PP" -ne 0 ] || PP=2' in FULL, (
        "a pair the prune removed must hold the board the way an unlaid pair does; the pair gate reads PP")


def t_pair_prune_judges_with_the_one_hard_set_and_its_exemptions():
    assert os.path.exists(PRUNE_PATH), "pair_prune.py does not exist"
    s = open(PRUNE_PATH).read()
    assert "import" in s and "hardset" in s and "hardset.HARD_PRE" in s and "hardset.exempt(v)" in s, (
        "a second hard set, or one without hardset's exemptions, is the 8 Sep register's finding again")


def t_pair_prune_removes_whole_pairs_on_both_nets_never_a_piece():
    s = open(PRUNE_PATH).read()
    assert "base_of(t.GetNetname()) == base" in s and "chain_len[find(i)] > ESCAPE_MM" in s, (
        "the removal must take every laid piece of BOTH nets of the marked pair, and leave the escapes to escape_prune")
    assert "sys.exit(2)" in s, "a prune that removed something must say so in its exit code"


def t_the_gap_cushion_is_one_knob_applied_to_both_layers():
    assert 'os.environ.get("PAIR_GAP_CUSHION"' in PRE, "the cushion over the DRC clearance is not a knob"
    assert "s = max(s, clr_c + GAP_CUSHION)" in PRE, "the outer gap does not take the cushion"
    assert "s_in = max(s_in, clr_c + GAP_CUSHION)" in PRE, (
        "the INNER gap takes no cushion: 13 of B19's 64 pre-route hard items were an inner pair's own two legs at 0.122 to 0.126 mm against 0.127")
    k = json.load(open(os.path.join(TOOLS, "agent", "knobs.json")))["knobs"]
    assert "PAIR_GAP_CUSHION" in k and k["PAIR_GAP_CUSHION"]["type"] == "number", "the knob is not registered for the agent"
    assert "`PAIR_GAP_CUSHION`" in open(os.path.join(DOCS, "PAIR-PREROUTER-KNOBS.md")).read(), "the knob has no row in the map"


def t_the_via_in_the_pad_between_a_stations_pads_asks_every_layer_first():
    i = PRE.find("_via_site_blocked(b, q.GetPosition()"); assert i > 0, "the via-in-pad site is not judged before it is dropped"
    j = PRE.find("v = pcbnew.PCB_VIA(b); v.SetPosition(q.GetPosition())")
    assert 0 < i < j, "the site check must come BEFORE the via is created and before the pin's escape is stripped"
    assert "inpad_refused" in PRE and "via site(s) refused" in PRE, "a refused site is not said"
    body = PRE[PRE.find("def _via_site_blocked"):PRE.find("def _via_site_blocked") + 2500]
    assert "b.GetFootprints()" in body and "b.GetTracks()" in body, "the check must read the pads of every other part and the copper of every net"


def t_b_declares_the_predictor_as_a_report_with_its_reason():
    b = json.load(open(os.path.join(TOOLS, "boards", "b.json")))
    assert b.get("place_audit_gate_off") is True and len(b.get("_place_audit_gate_off_why", "")) > 80, "B's predictor gate is not declared with a why"
    assert 'cfg place_audit_gate_off' in FULL, "full.sh does not read the declaration"
    for L in "acdep":
        d = json.load(open(os.path.join(TOOLS, "boards", "%s.json" % L)))
        assert not d.get("place_audit_gate_off"), "board %s turns the predictor off without a measured reason" % L


def t_a_profiles_gate_count_is_its_boards_declaration():
    """B19's third pre stage printed PREROUTE-DONE OK and routeflow read GATE_BLOCKED, 'RESULT: ALL PASS 1 of 2 gates':
    the profile carried min_all_pass 2 (the placed-board check and the pre-route check) while boards/b.json declares
    gate_before_placement false, so the chain runs one. The number is the board's declaration, never a profile literal."""
    import glob
    bad = []
    for p in sorted(glob.glob(os.path.join(TOOLS, "routeflow", "[a-p]*[0-9].json"))):
        d = json.load(open(p)); L = d.get("board", "")
        letter = L.split("-")[1][0] if L.startswith("pcb-") else ""
        bp = os.path.join(TOOLS, "boards", "%s.json" % letter)
        if not os.path.exists(bp) or "pre" not in d: continue
        want = 2 if json.load(open(bp)).get("gate_before_placement") else 1
        if d["pre"].get("min_all_pass") != want: bad.append("%s min_all_pass %s, board %s runs %d" % (os.path.basename(p), d["pre"].get("min_all_pass"), letter, want))
    assert not bad, "; ".join(bad)


def t_the_routers_parallel_copper_on_a_rail_comes_off_before_the_judgement():
    """A32 (15 Sep 2026): four rails MISSED on copper that reads MET alone, because Freerouting never sees a pour and laid
    a 0.5 mm inner track in parallel with each band; the solver took a share of the rail through it. rail_prune.py
    removes an unlocked rail piece when the net stays connected without it, before the refill that precedes the gate."""
    s = open(os.path.join(TOOLS, "rail_prune.py")).read()
    assert "IsLocked()" in s and "GetUnconnectedCount" in s and "-intent.json" in s, "the prune must touch only router copper, judge by connectivity, and read the rails from the intent"
    assert "if unconnected() > u0" in s, "a piece that is the only path must go back"
    f = open(os.path.join(TOOLS, "finish.sh")).read()
    i = f.find("rail_prune.py"); j = f.find("zones refilled before t"); assert 0 < i < j, "the prune must run before the refill the judgements read"
    assert 'cfg x rail_prune' in f, "the prune is not declared per board"
    a = json.load(open(os.path.join(TOOLS, "boards", "a.json")))
    assert a["finish"].get("rail_prune") is True and "_rail_prune_why" in a["finish"], "A does not declare it with its measurement"
