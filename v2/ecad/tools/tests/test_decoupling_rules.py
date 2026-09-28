#!/usr/bin/env python3
"""Decision 42's rules as functions: one limit by class, an allowance that names its capacitor, one fan selection
(MESHSAT-1357, stream d6dec, 27 September 2026; DECOUPLING.md 8.1, T1, T2, T3, T5, T6, T9 and T10).

Every rule here is a pair: an input that MUST be refused or read as the defect, and the same input made right.
None needs KiCad. The lands are the committed boards' own, read from their text into
`tests/fixtures/decoupling/footprints.json` (v2/docs/records/d6dec/make_footprint_fixtures.py), so the selection
is held to the parts the page names and not to pads a test invented."""
import os, sys, json, ast

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "decoupling", "footprints.json")

import decoupling_rules as dr


def _part(key):
    d = json.load(open(FIX, encoding="utf-8"))
    p = d["parts"][key]; phase = key.split(":")[0]
    smd = [(q["x_nm"], q["y_nm"]) for q in p["pads"] if q["type"] == "smd"]
    cu = [(q["x_nm"], q["y_nm"]) for q in p["pads"] if q["type"] == "smd" and q["num"] and q["cu"]]
    return p, smd, cu, d["boards"][phase]["escape_skip"]


def _fanned(key):
    p, smd, cu, skip = _part(key)
    return dr.fanned(p["ref"], p["fpid"], smd, cu, skip)[0], dr.escaped(p["ref"], p["fpid"], smd, skip), dr.copper_fanned(cu)


# ------------------------------------------------------------------------------------------------ T1: the fan set
def t_a_soic8_with_an_exposed_pad_is_not_fanned_by_its_paste_apertures():
    """THE DEFECTIVE READING was today's: thirteen SMD pads, four of them paste apertures 0.942 mm from the exposed
    pad, made a 1.27 mm part fine pitch (3.2(a)). On its copper pads it is neither escaped nor fanned."""
    for key in ("A32:U4", "B21:U103"):
        p, smd, cu, skip = _part(key)
        assert len(smd) == 13 and len(cu) == 9, "%s: %d SMD pads, %d with copper and a number" % (key, len(smd), len(cu))
        assert dr.min_pitch_nm(smd) <= dr.FAN_PITCH_NM, "the fixture no longer carries the apertures that made the defect"
        assert _fanned(key) == (False, False, False), "%s is fanned: %s" % (key, _fanned(key))


def t_a_wson6_keeps_its_fan_because_the_escape_pass_escapes_it():
    """A copper-pad count alone would cut it (seven copper pads, under the floor of eight); the escape term holds."""
    for key in ("D12:U15", "B21:U10"):
        f, e, c = _fanned(key)
        assert (f, e, c) == (True, True, False), "%s: fanned %s, escaped %s, copper term %s" % (key, f, e, c)


def t_a_six_pin_part_the_escape_pass_escapes_is_fanned():
    for key in ("D12:U5", "A32:U29", "B21:U25", "E17:U12", "C24:U11", "B21:U82"):
        f, e, c = _fanned(key)
        assert f and e and not c, "%s: fanned %s, escaped %s, copper term %s" % (key, f, e, c)


def t_a_part_the_escape_pass_does_not_escape_and_is_no_ic_is_not_fanned():
    for key in ("B21:U27", "D12:U11", "C24:U5"):
        assert _fanned(key) == (False, False, False), "%s (SOT-23-5): %s" % (key, _fanned(key))


def t_an_0p8_mm_quad_flat_pack_is_fanned_though_nothing_escapes_it():
    for key in ("D12:U6", "D12:U4"):
        f, e, c = _fanned(key)
        assert (f, e, c) == (True, False, True), "%s: fanned %s, escaped %s, copper term %s" % (key, f, e, c)


def t_the_fine_pitch_parts_are_fanned():
    for key in ("B21:U41", "C24:U3", "A32:U3", "A32:U2", "D12:U7"):
        f, e, c = _fanned(key)
        assert f and e and c, "%s: fanned %s, escaped %s, copper term %s" % (key, f, e, c)


def t_a_part_in_escape_skip_is_fanned_only_by_its_copper_pads():
    """B21's U3 is left to the router (ESCAPE_SKIP) and keeps its fan by the copper term; a six-pin part in the
    skip list would have none."""
    p, smd, cu, skip = _part("B21:U3")
    assert "U3" in skip, "board B's table no longer skips U3: %s" % skip
    assert _fanned("B21:U3") == (True, False, True), _fanned("B21:U3")
    p6, smd6, cu6, _ = _part("D12:U5")
    assert dr.fanned(p6["ref"], p6["fpid"], smd6, cu6, ["U5"])[0] is False, "a skipped six-pin part was fanned"


def t_the_selection_agrees_with_the_record_that_measured_the_ruling():
    """The decision 42 record read these lands with its own reader (dec_geometry.py) and wrote what it found into
    the fixture; the functions the tools now call give the same set, part by part."""
    d = json.load(open(FIX, encoding="utf-8")); bad = []
    for key, p in d["parts"].items():
        f, e, c = _fanned(key)
        if (f, e, c) != (p["record"]["fan_as_ruled"], p["record"]["escaped"], p["record"]["fan_copper_term"]):
            bad.append("%s: %s against the record's %s" % (key, (f, e, c), p["record"]))
    assert not bad, "; ".join(bad)


def _defs(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    imps = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import): imps |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module: imps.add(n.module)
    return names, imps, tree


def t_the_escape_pass_and_both_placers_call_one_selection():
    """The rule fails when any of the three carries its own copy (T1's own fixture). Asked of the code, by its AST:
    none defines a selection of its own, and each reaches `fan_select`, directly or through the shared search."""
    own = {"escape.py": {"is_fine", "min_pitch"}, "bypass_slots.py": {"_needs_fan", "is_fine"},
           "bypass_place.py": {"_needs_fan", "is_fine"}, "bypass_seats.py": {"_needs_fan", "is_fine"}}
    bad = []
    for name, forbidden in own.items():
        names, imps, tree = _defs(os.path.join(TOOLS, name))
        if names & forbidden: bad.append("%s defines its own %s" % (name, sorted(names & forbidden)))
        if not ({"fan_select", "bypass_search"} & imps): bad.append("%s imports neither fan_select nor bypass_search" % name)
        for n in ast.walk(tree):
            if isinstance(n, ast.Attribute) and n.attr in ("_needs_fan",):
                bad.append("%s still calls %s" % (name, n.attr))
    names, imps, _ = _defs(os.path.join(TOOLS, "bypass_search.py"))
    if "fan_select" not in imps: bad.append("bypass_search.py does not import fan_select")
    assert not bad, "; ".join(bad)


# ------------------------------------------------------------------------------------------------ T2: the limit
def _e(cls, **kw):
    e = {"cap": "C1", "part": "U1", "pin": "1", "net": "+3V3", "class": cls, "basis": "the maker's clause, p.1"}
    e.update(kw); return e


def t_the_value_string_cannot_decide_the_limit():
    """THE DEFECT: the gate read "10u 25V 1210" at 6.0 mm and a bare "10u" at 3.0 mm (3.2(c)). The limit takes
    no value, so two capacitors of one class cannot get two limits."""
    import inspect
    assert "value" not in inspect.signature(dr.limit).parameters, "limit() takes a value again"
    a = dr.limit(_e("R", same_side=True, cap="C4")); b = dr.limit(_e("R", same_side=True, cap="C112"))
    assert a["screen_mm"] == b["screen_mm"] == 3.0, (a, b)


def t_each_class_has_its_own_limit():
    assert dr.limit(_e("D"))["screen_mm"] == 3.0
    assert dr.limit(_e("L", value_floor="1u", esr_max=dr.NOT_STATED))["screen_mm"] == 3.0, "a class L 4.7u keeps 3.0 mm"
    assert dr.limit(_e("B2"))["screen_mm"] == 6.0
    assert dr.limit(_e("B1"))["screen_mm"] is None, "a class B1 entry has no pin distance"
    assert dr.limit(_e("A"))["screen_mm"] is None
    assert dr.limit(_e("D"))["measure"] == "rail pad to pin"


def t_an_entry_without_a_ruled_class_is_refused_and_never_given_a_default():
    for bad in (None, "", "B", "X", "d"):
        try: dr.limit(_e(bad)); raised = False
        except dr.Refused: raised = True
        assert raised, "class %r was given a limit" % (bad,)


def t_a_makers_distance_is_a_limit_no_allowance_passes():
    """THE DEFECTIVE FIXTURE is D12 itself: the TPA6132A2's HPVDD capacitor 18.1 mm from its pin against TI's 5 mm
    (SLOS597B 9, p.17), passed by one allow line. With the maker's distance carried, no allowance passes it."""
    c31 = _e("L", cap="C31", value_floor="2.2u", esr_max=dr.NOT_STATED, maker_mm=5.0)
    st, why = dr.judge(c31, 18.1, allowance="moving it is a floor-plan change across the whole board set")
    assert st == "fail" and "5.0 mm" in why and "refused" in why, (st, why)
    assert dr.judge(c31, 4.2, allowance="the own side is full at U7, 4.2 mm is the nearest seat")[0] == "justified"
    assert dr.judge(c31, 4.2)[0] == "fail", "past the screen with no allowance"
    assert dr.judge(c31, 2.4)[0] == "pass"


def t_an_allowance_is_a_justified_deviation_and_never_a_pass():
    st, why = dr.judge(_e("D"), 9.0, allowance="the own-pin window costs U3 two escapes, measured on C25")
    assert st == "justified", st
    assert dr.judge(_e("D"), 9.0)[0] == "fail"
    assert dr.judge(_e("A"), 11.0)[0] == "recorded", "class A has no distance to fail"
    assert dr.judge(_e("B2"), 5.9)[0] == "pass" and dr.judge(_e("B2"), 6.1)[0] == "fail"


# ------------------------------------------------------------------------------------------------ T6: allow lines
BLANKET = ("the decoupling capacitors of this board sit past 3 mm from the pins they serve; moving them is a "
           "floor-plan change across the whole board set and is an owner decision")


def t_a_line_that_names_no_capacitor_allows_nothing():
    """THE DEFECTIVE FIXTURE is the line of 8 September that five boards carried."""
    allow, refused = dr.parse_allow(BLANKET + "\n")
    assert allow == {}, "a blanket line allowed %s" % allow
    assert len(refused) == 1 and "names no capacitor" in refused[0][2], refused


def t_a_line_that_names_its_capacitor_allows_that_one():
    allow, refused = dr.parse_allow("# a comment\n\nC36: the own side is full at U5, 4.1 mm is the nearest seat\n"
                                    "C42 : the window costs U6 one escape, measured on A66\n")
    assert sorted(allow) == ["C36", "C42"] and not refused, (allow, refused)
    assert "C37" not in allow


def t_a_reason_nobody_could_check_and_a_second_line_for_one_capacitor_are_refused():
    allow, refused = dr.parse_allow("C1: ok\nC2: the nearest free seat outside U3's fan\nC2: another reason entirely here\nR5: not a capacitor at all, a resistor\n")
    assert sorted(allow) == ["C2"], allow
    assert len(refused) == 3, refused


def t_no_allow_file_carries_a_line_that_names_no_capacitor():
    """The data rule, and the one that failed on the tree this file was written against: twelve files, each with
    the line of 8 September. DECOUPLING.md T6 would have kept the phase copies as history; the repository's own
    rule of 12 September (tests/test_driver_hygiene.py, a phase copy declares what its board declares) holds a
    copy to its board's file, and a gate re-run on a phase folder reads the copy, so both are cleared."""
    ecad = os.path.dirname(TOOLS); bad = []; seen = 0
    for d in sorted(os.listdir(ecad)):
        p = os.path.join(ecad, d, "bypass-allow.txt")
        if not d.startswith("pcb-") or not os.path.exists(p): continue
        seen += 1
        allow, refused = dr.parse_allow(open(p, encoding="utf-8").read())
        if refused: bad.append("%s: %d line(s) refused, the first: %s" % (d, len(refused), refused[0][1][:60]))
    assert seen, "no allow file was found under %s, so nothing was checked" % ecad
    assert not bad, "; ".join(bad)


# ------------------------------------------------------------------------------------------------ T5: the form
def t_a_declaration_without_its_class_or_its_basis_is_named():
    assert dr.form_problems({"cap": "C9", "part": "U1", "pin": "1", "net": "+3V3"}), "an unclassed entry had no problem"
    assert any("basis" in p for p in dr.form_problems(_e("D", basis="  ")))
    assert dr.form_problems(_e("D")) == []


def t_class_L_carries_its_floor_and_what_the_maker_says_of_esr():
    assert len(dr.form_problems(_e("L"))) == 2, dr.form_problems(_e("L"))
    assert dr.form_problems(_e("L", value_floor=dr.NOT_STATED + "; its application circuit draws 1 uF", esr_max=dr.NOT_STATED)) == []
    assert dr.form_problems(_e("L", value_floor="2.2u (-20 percent)", esr_max="100 mOhm")) == []


def t_class_R_carries_the_makers_same_side():
    assert any("same_side" in p for p in dr.form_problems(_e("R")))
    assert dr.form_problems(_e("R", same_side=True)) == []


def t_the_keys_round_8_wrote_are_read_and_named_as_aliases():
    e, used = dr.normalise(_e("L", floor_uF=0.47, esr="no number"))
    assert e["value_floor"] == 0.47 and e["esr_max"] == "no number" and sorted(used) == ["esr", "floor_uF"], (e, used)
    assert abs(dr.value_farads(e["value_floor"]) - 0.47e-6) < 1e-12
    assert abs(dr.value_farads("198n") - 198e-9) < 1e-15 and abs(dr.value_farads("2.2u (-20 percent)") - 2.2e-6) < 1e-12
    assert dr.value_farads(dr.NOT_STATED) is None and dr.value_farads("no number") is None


# ------------------------------------------------------------------------------------------------ T3: rotations
def t_the_rotation_kept_is_the_one_that_brings_the_rail_pad_nearest():
    """THE DEFECT: one orientation, so a capacitor whose rail pad is its far pad could not turn it toward the pin
    (3.2(e)). A capacitor centred 1.0 mm east of the pin with its rail pad 0.5 mm further east at rotation 0."""
    rot, d = dr.best_rotation((1.0, 0.0), (0.5, 0.0), (0.0, 0.0))
    assert rot == 180.0 and abs(d - 0.5) < 1e-9, (rot, d)
    rot0, d0 = dr.best_rotation((1.0, 0.0), (0.5, 0.0), (0.0, 0.0), allowed=lambda r: r == 0.0)
    assert rot0 == 0.0 and abs(d0 - 1.5) < 1e-9, "one orientation leaves it at 1.5 mm: %s" % ((rot0, d0),)
    assert dr.best_rotation((1.0, 0.0), (0.5, 0.0), (0.0, 0.0), allowed=lambda r: False) == (None, None)


# ---------------------------------------------------------------------------------------- D3, R2: the fan opened
def t_the_fan_is_opened_for_the_own_pin_window_and_for_nothing_else():
    cy = (0.0, 0.0, 10.0, 10.0); pin = (10.0 - 0.6, 5.0)            # a pin at the east edge of U1
    fans = [("U1", dr._grow(cy, dr.FAN_MM)), ("U2", (12.4, 0.0, 24.0, 10.0))]
    win = dr.window_box(cy, pin, 1.9)
    assert win == (10.0, 5.0 - 0.95, 10.0 + dr.FAN_MM, 5.0 + 0.95), win
    inside = (10.05, 4.53, 10.05 + 0.94, 5.47)                         # an 0402's courtyard, long axis along the row
    assert dr.fan_blocks(inside, fans, _e("D", part="U1"), own_window=win) is None
    assert dr.fan_blocks(inside, fans, _e("D", part="U1"), own_window=None) == "U1", "with no window the fan is closed"
    beside = (10.05, 6.2, 10.99, 7.14)                                 # in U1's fan, in front of ANOTHER pin
    assert dr.fan_blocks(beside, fans, _e("D", part="U1"), own_window=win) == "U1"
    assert dr.fan_blocks(inside, fans, _e("B2", part="U1"), own_window=win) == "U1", "bulk gets no window"
    assert dr.fan_blocks(inside, fans, _e("A", part="U1"), own_window=win) == "U1", "class A: the fan stays closed (A2)"
    other = (12.5, 4.5, 13.5, 5.5)                                     # past U1's fan and in U2's: never opened for U1's capacitor
    assert dr.fan_blocks(other, fans, _e("D", part="U1"), own_window=(10.0, 4.0, 14.0, 6.0)) == "U2"


def t_a_converters_fan_is_open_to_its_own_power_stage_only():
    fans = [("U25", (0.0, 0.0, 8.0, 8.0)), ("U41", (9.0, 0.0, 30.0, 20.0))]
    box = (6.0, 3.0, 7.5, 5.0)
    assert dr.fan_blocks(box, fans, _e("R", part="U25", same_side=True), own_converter="U25") is None
    assert dr.fan_blocks(box, fans, _e("R", part="L1", same_side=True), own_converter="U25") is None
    assert dr.fan_blocks(box, fans, _e("R", part="L1", same_side=True), own_converter=None) == "U25"
    assert dr.fan_blocks((9.5, 3.0, 11.0, 5.0), fans, _e("R", part="U25", same_side=True), own_converter="U25") == "U41"
    assert dr.window_box((0.0, 0.0, 10.0, 10.0), (5.0, 5.0), 1.9) is None, "an exposed pad in the middle has no window"


# ------------------------------------------------------------------------------------------------ T9: the far side
def t_the_via_allowance_is_computed_from_the_stackup_row():
    import stackup_write as sw
    six = dr.via_allowance_mm(sw.STACKS["JLC06161H-3313"]); four = dr.via_allowance_mm(sw.STACKS["JLC04161H-7628"])
    assert abs(four - 2.26) < 0.02, "JLC04161H-7628 reads %.3f mm (DECOUPLING.md 5.2: 2.3)" % four
    # finding F-1 of stream d6dec: the page's 3.7 mm took a six-layer board of 1.5832 mm; the fabricator's own
    # layers sum to 1.5384 mm, which is this row
    cu, h, board = dr.stack_geometry(sw.STACKS["JLC06161H-3313"])
    assert abs(board - 1.5384) < 1e-6 and abs(h - 0.0994) < 1e-9, (cu, h, board)
    assert abs(six - 3.54) < 0.02, "JLC06161H-3313 reads %.3f mm" % six
    assert dr.via_allowance_mm(sw.STACKS["JLC06161H-3313"], via_pitch=0.5) < six < dr.via_allowance_mm(sw.STACKS["JLC06161H-3313"], via_pitch=1.2)


def t_the_boards_own_stackup_gives_the_rows_allowance():
    import stackup_write as sw
    layers = [{"name": "F.Cu", "type": "copper", "thickness": 0.035}, {"name": "dielectric 1", "type": "prepreg", "thickness": 0.2104, "material": "FR4", "epsilon_r": 4.4},
              {"name": "In1.Cu", "type": "copper", "thickness": 0.0152}, {"name": "dielectric 2", "type": "core", "thickness": 1.065, "epsilon_r": 4.6},
              {"name": "In2.Cu", "type": "copper", "thickness": 0.0152}, {"name": "dielectric 3", "type": "prepreg", "thickness": 0.2104, "epsilon_r": 4.4},
              {"name": "B.Cu", "type": "copper", "thickness": 0.035}, {"name": "F.Mask", "type": "Top Solder Mask", "thickness": 0.01}]
    assert abs(dr.via_allowance_mm(dr.stack_from_layers(layers)) - dr.via_allowance_mm(sw.STACKS["JLC04161H-7628"])) < 1e-9


def t_a_far_side_seat_is_refused_where_the_ruling_refuses_it():
    d = _e("D", cap="C53")
    assert dr.far_side(d, False)[0] is False, "a far-side seat on a board assembled on one side (A32, E17, P4)"
    assert dr.far_side(d, True)[0] is True
    assert dr.far_side(_e("R", same_side=True), True)[0] is False, "a converter's power stage on the other side (R3)"
    assert dr.far_side(_e("D", same_side=True), True)[0] is False, "the STM32H743 in its LQFP names the same side"
    fans = [("U7", (10.0, 10.0, 20.0, 20.0))]; tht = [("J1", (30.0, 0.0, 40.0, 10.0))]
    ok, why = dr.far_side(d, True, cap_box=(19.0, 12.0, 20.5, 13.0), fan_boxes=fans, tht_boxes=tht)
    assert ok is False and "U7" in why, why
    ok, why = dr.far_side(d, True, cap_box=(31.0, 2.0, 32.5, 3.0), fan_boxes=fans, tht_boxes=tht)
    assert ok is False and "J1" in why, why
    assert dr.far_side(d, True, cap_box=(22.0, 12.0, 23.5, 13.0), fan_boxes=fans, tht_boxes=tht)[0] is True
    import stackup_write as sw
    a4 = dr.via_allowance_mm(sw.STACKS["JLC04161H-7628"])
    assert abs(dr.loop_equivalent_mm(0.54, True, a4) - 2.80) < 0.02, "D12's C53 reads 2.8 mm (section 7)"
    assert dr.loop_equivalent_mm(0.54, False, a4) == 0.54


# ------------------------------------------------------------------------------------------------ T10: the own via
def t_a_ground_pad_that_shares_its_via_with_a_neighbour_is_not_its_own():
    pad = {"xy": (10.0, 10.0), "net": "GND", "half": (0.3, 0.3)}
    vias = [{"xy": (10.0, 10.8), "net": "GND", "r": 0.3}, {"xy": (10.4, 10.0), "net": "+3V3", "r": 0.3}]
    neighbour = [{"ref": "C2", "num": "2", "xy": (10.0, 11.3), "net": "GND", "half": (0.3, 0.3)},
                 {"ref": "C1", "num": "1", "xy": (9.0, 10.0), "net": "+3V3", "half": (0.3, 0.3)}]
    r = dr.own_via(pad, vias, neighbour)
    assert r["via"] == 0 and r["own"] is False and r["shared_with"] == ["C2.2"], r
    assert abs(r["length_mm"] - 0.8) < 1e-9


def t_a_ground_pad_with_a_via_no_other_pad_lands_on_has_its_own():
    pad = {"xy": (10.0, 10.0), "net": "GND", "half": (0.3, 0.3)}
    vias = [{"xy": (10.0, 10.8), "net": "GND", "r": 0.3}]
    far = [{"ref": "C2", "num": "2", "xy": (10.0, 13.0), "net": "GND", "half": (0.3, 0.3)}]
    r = dr.own_via(pad, vias, far)
    assert r["own"] is True and r["shared_with"] == [], r
    none = dr.own_via(pad, [{"xy": (10.0, 14.0), "net": "GND", "r": 0.3}], far)
    assert none["via"] is None and none["own"] is False, "a via 4 mm away is no via of this pad"


def t_a_far_side_seat_is_priced_at_its_own_via_pitch_where_it_has_two_vias():
    """T9: "On a placed board it is re-read with the seat's own via pitch" (29 September 2026). A pair 0.8 mm apart
    reads the page's allowance; 1.6 mm apart reads more (the loop is larger); a pad with no via of its net within
    1.5 mm gives no pitch, and the caller keeps the page's 0.8 mm and says so."""
    import stackup_write as sw
    row = sw.STACKS["JLC04161H-7628"]
    rail = {"xy": (10.0, 10.0), "net": "+3V3"}; gnd = {"xy": (11.0, 10.0), "net": "GND"}
    at = lambda gx: [{"xy": (9.6, 10.0), "net": "+3V3", "r": 0.3}, {"xy": (gx, 10.0), "net": "GND", "r": 0.3},
                     {"xy": (10.0, 10.4), "net": "SIG", "r": 0.3}]
    p, why = dr.seat_via_pitch(rail, gnd, at(10.4))
    assert abs(p - 0.8) < 1e-9 and "own via pair" in why, (p, why)
    assert abs(dr.via_allowance_mm(row, via_pitch=p) - dr.via_allowance_mm(row)) < 1e-9
    p2, _ = dr.seat_via_pitch(rail, gnd, at(11.2))
    assert abs(p2 - 1.6) < 1e-9 and dr.via_allowance_mm(row, via_pitch=p2) > dr.via_allowance_mm(row) + 0.3
    none, why = dr.seat_via_pitch(rail, gnd, at(14.0))
    assert none is None and "no via of GND" in why, why
    assert dr.seat_via_pitch(rail, None, at(10.4))[0] is None
