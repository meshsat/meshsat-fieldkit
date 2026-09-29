#!/usr/bin/env python3
"""Decision 42 on boards: the gate, the two placers and the escape pass, each asked of a board KiCad built
(MESHSAT-1357, stream d6dec, 27 September 2026; DECOUPLING.md 8.1, T2 to T6, T9 and T10).

Every rule is a pair, the defective board and the same board made right, and every board is built in a temporary
directory by tests/decoupling_fixture.py: nothing here reads or writes this tree's evidence. They need KiCad's
pcbnew and skip where it is absent; the rules themselves are held on every host by tests/test_decoupling_rules.py."""
import os, sys, json, math, tempfile, subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "decoupling_fixture.py")


def _pcbnew():
    try:
        import pcbnew; return pcbnew
    except Exception as e:
        raise Skip("no pcbnew here (%s)" % type(e).__name__)


def _env(d):
    e = dict(os.environ); e.pop("ESCAPE_SKIP", None)
    e["VERDICT_DIR"] = os.path.join(d, "out"); e["PYTHONDONTWRITEBYTECODE"] = "1"
    return e


def _build(scenario, d):
    r = subprocess.run([sys.executable, FIXTURE, "build", scenario, d], capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, "the %s fixture did not build:\n%s" % (scenario, (r.stdout + r.stderr)[-900:])
    return os.path.join(d, "fix.kicad_pcb")


def _read(path):
    r = subprocess.run([sys.executable, FIXTURE, "read", path], capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (r.stdout + r.stderr)[-600:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def _gate(scenario):
    _pcbnew()
    with tempfile.TemporaryDirectory(prefix="dec-gate-") as d:
        path = _build(scenario, d)
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "intent_checks.py"), path], cwd=d, env=_env(d),
                           capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        vp = os.path.join(d, "out", "intent_decoupling.verdict.json")
        assert os.path.exists(vp), "the gate wrote no decoupling verdict:\n%s" % out[-900:]
        v = json.load(open(vp))
        lines = [l for l in out.split("\n") if "bypass C1" in l]
        return v["verdict"], v.get("counts") or {}, (lines[0] if lines else ""), out


def _place(scenario, extra=()):
    _pcbnew()
    d = tempfile.mkdtemp(prefix="dec-place-")
    path = _build(scenario, d)
    before = _read(path)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "bypass_place.py"), path] + list(extra), cwd=d, env=_env(d),
                       capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout + r.stderr, before, _read(path)


def _rail_d(after, part="U1", pin="3", cap="C1", rail="1"):
    p, c = after[part]["pads"][pin], after[cap]["pads"][rail]
    return math.hypot(p["x"] - c["x"], p["y"] - c["y"])


def _meets(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _fan(after, part="U1", fan=2.2):
    x0, y0, x1, y1 = after[part]["box"]
    return (x0 - fan, y0 - fan, x1 + fan, y1 + fan)


# ------------------------------------------------------------------------------------------------ the gate, T2 and T6
def t_an_entry_with_no_class_fails_the_gate_by_name():
    """THE DEFECTIVE FIXTURE: the declaration every intent file carried until round 8, a capacitor, a part and a pin.
    1.5 mm from its pin, it passed at the old gate's 3.0 mm for a 100 nF value; it has no limit now, and is refused."""
    verdict, counts, line, out = _gate("g_unclassed")
    assert verdict == "FAIL" and counts.get("unclassed") == 1, (verdict, counts, line)
    assert "is not one of" in line, line


def t_the_same_entry_with_its_class_passes():
    verdict, counts, line, out = _gate("g_near")
    assert verdict == "PASS" and counts.get("pass") == 1 and counts.get("justified") == 0, (verdict, counts, line)
    assert "class D" in line and "within the 3.0 mm screen" in line, line


def t_a_line_that_names_no_capacitor_allows_none():
    """THE DEFECTIVE FIXTURE is the allow file five boards carried: one line, no capacitor named. The capacitor
    10 mm from its pin read PASS under it; it reads FAIL."""
    verdict, counts, line, out = _gate("g_far_blanket")
    assert verdict == "FAIL" and counts.get("fail") == 1, (verdict, counts, line)
    assert counts.get("allow_lines_refused") == 1, counts
    assert "names no capacitor" in out and "allows nothing" in out, out[-600:]


def t_a_line_that_names_the_capacitor_makes_a_justified_deviation_and_no_pass():
    verdict, counts, line, out = _gate("g_far_named")
    assert verdict == "PASS", (verdict, counts, line)
    assert counts.get("justified") == 1 and counts.get("pass") == 0 and counts.get("fail") == 0, counts
    assert "justified deviation" in line and "JUSTIFIED" in line, line


def t_no_line_passes_a_makers_own_distance():
    """The TPA6132A2's case (SLOS597B 9, p.17, 5 mm): the capacitor is named in the allow file and sits 10 mm out."""
    verdict, counts, line, out = _gate("g_maker_cap")
    assert verdict == "FAIL" and counts.get("justified") == 0, (verdict, counts, line)
    assert "5.0 mm" in line and "refused" in line, line


def t_the_value_string_does_not_decide_the_limit():
    """THE DEFECT (3.2(c)): a bare "10u" read 3.0 mm and a "10u 25V 1210" 6.0 mm. At 5.0 mm from its pin, a class B2
    capacitor spelled "10u" passes its 6.0 mm and a class D capacitor spelled "10u 25V 1210" fails its 3.0 mm:
    each the reverse of what its value string used to decide."""
    v1, c1, l1, _ = _gate("g_value_bulk")
    assert v1 == "PASS" and "(10u)" in l1 and "6.0 mm" in l1, (v1, c1, l1)
    v2, c2, l2, _ = _gate("g_value_pin")
    assert v2 == "FAIL" and "(10u 25V 1210)" in l2 and "3.0 mm" in l2, (v2, c2, l2)


def t_a_class_with_no_distance_is_recorded_and_is_neither_a_pass_nor_a_failure():
    verdict, counts, line, out = _gate("g_recorded")
    assert verdict == "PASS" and counts.get("recorded") == 1 and counts.get("pass") == 0, (verdict, counts, line)
    assert "recorded" in line and "class A" in line, line


# ------------------------------------------------------------------------------------------------ the gate, T9
def t_a_far_side_capacitor_on_a_board_assembled_on_one_side_is_refused():
    """THE DEFECTIVE FIXTURE: the only SMD part on the back is the declared capacitor itself, 0.3 mm in plane from
    its pin. It would add an assembly side (A32, E17, P4)."""
    verdict, counts, line, out = _gate("g_farside_onesided")
    assert verdict == "FAIL" and counts.get("far_side") == 1, (verdict, counts, line)
    assert "one side only" in line, line


def t_the_same_capacitor_on_a_board_assembled_on_both_sides_is_judged_with_the_via_allowance():
    verdict, counts, line, out = _gate("g_farside_ok")
    assert verdict == "PASS" and counts.get("pass") == 1, (verdict, counts, line)
    assert "via allowance" in line and "in plane plus" in line, line
    v2, c2, l2, _ = _gate("g_farside_past")
    assert v2 == "FAIL", "2.0 mm in plane plus the allowance is past the 3.0 mm screen: %s" % l2


def t_a_far_side_capacitor_inside_a_fan_is_refused_whatever_the_allow_file_says():
    verdict, counts, line, out = _gate("g_farside_fan")
    assert verdict == "FAIL" and counts.get("justified") == 0, (verdict, counts, line)
    assert "escape fan of U7" in line, line


def t_a_part_whose_maker_names_the_same_side_takes_no_far_side_seat():
    verdict, counts, line, out = _gate("g_farside_same_side")
    assert verdict == "FAIL" and "same side" in line, (verdict, counts, line)


# ------------------------------------------------------------------------------------------------ the gate, T10
def t_a_ground_via_that_is_also_a_neighbours_landing_is_a_deviation():
    verdict, counts, line, out = _gate("g_shared_via")
    assert verdict == "PASS" and counts.get("no_own_via") == 1 and counts.get("justified") == 1 and counts.get("pass") == 0, (counts, line)
    assert "also the landing of C2.1" in line, line


def t_a_ground_pad_with_its_own_via_passes_and_the_via_is_named():
    verdict, counts, line, out = _gate("g_own_via")
    assert verdict == "PASS" and counts.get("pass") == 1 and counts.get("no_own_via") == 0, (counts, line)
    assert "its own ground via 0.70 mm from the pad" in line, line


def t_a_ground_pad_with_no_via_at_all_is_a_deviation_and_never_a_pass():
    verdict, counts, line, out = _gate("g_no_via")
    assert counts.get("pass") == 0 and counts.get("no_own_via") == 1, (verdict, counts, line)
    assert "has no via within" in line, line


# ------------------------------------------------------------------------------------------------ the placers
def t_a_class_D_capacitor_is_seated_in_its_own_pin_window_rail_pad_first():
    """T3 and D3. THE DEFECT was the fan closed to every capacitor and one orientation: at a fine-pitch part nothing
    within 3.0 mm of the pin was ever free (131 declared capacitors and not one reserved slot, appendix 32.306)."""
    rc, out, before, after = _place("p_window")
    assert rc == 0 and "1 moved" in out, out[-600:]
    d = _rail_d(after)
    assert d < 1.5, "the rail pad sits %.2f mm from the pin; the window seats it under 1.5 mm" % d
    c = after["C1"]; pin = after["U1"]["pads"]["3"]
    assert abs(c["x"] - pin["x"]) < 0.02, "the capacitor is not centred on its pin's axis: %.3f against %.3f" % (c["x"], pin["x"])
    assert _meets(c["box"], _fan(after)), "the seat is outside the fan, which is where it sat before the window"
    other = math.hypot(pin["x"] - c["pads"]["2"]["x"], pin["y"] - c["pads"]["2"]["y"])
    assert d < other, "the pad nearest the pin is the ground pad (%.2f against %.2f): it was not turned" % (d, other)


def t_bulk_gets_no_window_and_stays_outside_the_fan():
    rc, out, before, after = _place("p_bulk")
    assert rc == 0 and "1 moved" in out, out[-600:]
    assert not _meets(after["C1"]["box"], _fan(after)), "a class B2 capacitor was seated inside the fan"
    assert _rail_d(after) <= 6.0 + 1e-6, "past its 6.0 mm screen: %.2f" % _rail_d(after)


def t_a_class_A_capacitor_takes_the_nearest_seat_outside_the_fan():
    rc, out, before, after = _place("p_class_a")
    assert rc == 0, out[-600:]
    assert not _meets(after["C1"]["box"], _fan(after)), "class A: the fan stays closed (A2)"
    assert _rail_d(after) < 6.0, "the nearest free seat outside the fan is a few millimetres out, it sits %.2f" % _rail_d(after)


def t_the_placer_refuses_an_entry_with_no_class_and_moves_nothing():
    rc, out, before, after = _place("p_unclassed")
    assert rc == 1 and "REFUSED" in out and "0 moved" in out, out[-600:]
    assert abs(after["C1"]["x"] - before["C1"]["x"]) < 1e-6 and abs(after["C1"]["y"] - before["C1"]["y"]) < 1e-6


def t_a_converters_fan_is_open_to_its_own_input_capacitor():
    """R2. The converter is a TSOT-23-6, which the escape pass escapes, so it is fanned as ruled (T1) and its input
    capacitor's seat within 3.0 mm of VIN lies inside that fan."""
    rc, out, before, after = _place("p_converter")
    assert rc == 0 and "1 moved" in out, out[-600:]
    assert _rail_d(after, "U2", "3") <= 3.0 + 1e-6, "%.2f mm" % _rail_d(after, "U2", "3")
    assert _meets(after["C1"]["box"], _fan(after, "U2")), "the seat is outside the converter's fan, so the fixture asked nothing"


def t_no_other_parts_fan_is_opened_for_a_class_R_capacitor():
    """THE DEFECTIVE FIXTURE for R2's other half: a class R capacitor declared against the inductor, with no
    converter named and none in a power loop, is not let into the converter's fan."""
    rc, out, before, after = _place("p_converter_unnamed")
    if "1 moved" in out:
        assert not _meets(after["C1"]["box"], _fan(after, "U2")), "a fan was opened for a capacitor that names no converter"
    else:
        assert "STUCK" in out, out[-600:]


def t_the_other_side_is_offered_on_a_board_assembled_on_both_sides():
    rc, out, before, after = _place("p_farside")
    assert "the other side is offered" in out, out[-900:]
    assert rc == 0 and "1 moved" in out, out[-900:]
    assert after["C1"]["back"] is True, "the own side is full and the capacitor did not go to the other"
    assert "on the other side" in out and "in plane" in out, out[-600:]


def t_the_other_side_is_not_offered_on_a_board_assembled_on_one_side():
    rc, out, before, after = _place("p_farside_onesided")
    assert "the other side is not offered" in out, out[-900:]
    assert after["C1"]["back"] is False, "a first SMD part was put on the back of a one-sided board"
    assert rc == 1 and "STUCK" in out, out[-600:]


def _reserve(scenario):
    _pcbnew()
    with tempfile.TemporaryDirectory(prefix="dec-res-") as d:
        r = subprocess.run([sys.executable, FIXTURE, "reserve", scenario, d], capture_output=True, text=True, timeout=600,
                           env=_env(d), cwd=d)
        out = r.stdout + r.stderr
        assert r.returncode == 0, out[-900:]
        line = [l for l in out.split("\n") if l.startswith("RESERVED ")]
        assert line, out[-900:]
        return json.loads(line[0][9:]), out


def t_the_reservation_seats_a_class_D_capacitor_in_its_window():
    res, out = _reserve("r_window")
    assert res["done"] == ["C1"] and res["on_board"], (res, out[-400:])
    far = max(math.hypot(res["pin"][0] - p[0], res["pin"][1] - p[1]) for p in res["pads"].values())
    assert far <= 3.0 + 1e-6, "its farther pad sits %.2f mm out, past the screen" % far
    assert "bounds its rail pad" in out, "with no netlist beside the board the rail pad is a bound, and must say so"


def t_the_reservation_refuses_an_entry_with_no_class():
    res, out = _reserve("r_unclassed")
    assert res["done"] == [] and not res["on_board"], res
    assert "LEFT TO THE PACKER" in out and "refused" in out, out[-600:]


# ------------------------------------------------------------------------------------------------ the escape pass, T4
def _escape(scenario):
    _pcbnew()
    d = tempfile.mkdtemp(prefix="dec-esc-")
    path = _build(scenario, d)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "escape.py"), path], cwd=d, env=_env(d),
                       capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout + r.stderr, _read(path)


def t_an_escape_lost_to_an_own_pin_window_is_reported_by_part_and_cause():
    rc, out, after = _escape("e_window")
    assert rc == 0, out[-900:]
    assert "lost to its own-pin windows (D3)" in out, out[-1200:]
    assert "escape: U1 lost" in out and "C1" in out, out[-1200:]


def t_the_same_capacitor_undeclared_is_another_reason_and_no_window_is_blamed():
    rc, out, after = _escape("e_undeclared")
    assert rc == 0, out[-900:]
    assert "lost to" not in out, out[-1200:]
    assert "escape: decoupling cost: 0 refused pad(s) would have been escaped without a declared seat" in out, out[-1200:]


# ---------------------------------------------------------------------- closed again (D3, T4; 29 September 2026)
def _escape_then_place(tamper=None):
    """The e_window board: the escape pass runs, writes what it closes again beside the intent, and the placer runs
    on the same board. `tamper(record)` edits the record between the two, to make it stale."""
    _pcbnew()
    d = tempfile.mkdtemp(prefix="dec-close-")
    path = _build("e_window", d)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "escape.py"), path], cwd=d, env=_env(d),
                       capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, (r.stdout + r.stderr)[-900:]
    cp = os.path.join(d, "out", "fix-escape-cost.json")
    assert os.path.exists(cp), "the escape pass wrote no cost record:\n%s" % (r.stdout + r.stderr)[-900:]
    rec = json.load(open(cp))
    if tamper: tamper(rec); json.dump(rec, open(cp, "w"))
    before = _read(path)
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "bypass_place.py"), path], cwd=d, env=_env(d),
                       capture_output=True, text=True, timeout=600)
    return rec, p.returncode, p.stdout + p.stderr, before, _read(path)


def t_a_window_that_cost_an_escape_is_closed_again_on_the_next_placement():
    """D3: "A window that costs an escape the part needs is closed again". THE DEFECT before 29 September: the pass
    printed the cost and the next placement opened the same window again, so C1 read "already within its limit"."""
    rec, rc, out, before, after = _escape_then_place()
    assert [x["ref"] for x in rec["close"]["window"]] == ["C1"] and rec["close"]["window"][0]["cost"] == ["U1"], rec["close"]
    assert "closed again from fix-escape-cost.json: 1 own-pin window(s), 0 converter opening(s); 0 stale" in out, out[-900:]
    assert "0 already within" in out, "C1 was read as already within its limit inside a closed window:\n" + out[-900:]
    if "1 moved" in out:
        assert not _meets(after["C1"]["box"], _fan(after)), "C1 was moved and is still inside U1's fan"
    else:
        # the conflict decision 42 measured: outside the fan nothing lies within the 3.0 mm screen, so it is STUCK and
        # says why, and bypass_seats names the seat further out (D4)
        assert rc == 1 and "STUCK C1" in out and "closed again by the escape pass" in out, out[-900:]


def t_a_stale_closure_is_not_applied_and_says_so():
    """THE ACCEPTABLE PAIR: the same record with U1 recorded 1 mm from where it stands is stale (the part moved since
    the pass measured it), so nothing is closed and C1 stays in its window, within its limit."""
    def moved(rec):
        for row in rec["close"]["window"]:
            row["parts_at"]["U1"][0] += 1000000
    rec, rc, out, before, after = _escape_then_place(moved)
    assert "closed again from fix-escape-cost.json: 0 own-pin window(s), 0 converter opening(s); 1 stale entry not applied" in out, out[-900:]
    assert rc == 0 and "1 already within" in out, out[-900:]
    assert abs(after["C1"]["x"] - before["C1"]["x"]) < 1e-6 and abs(after["C1"]["y"] - before["C1"]["y"]) < 1e-6
