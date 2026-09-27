#!/usr/bin/env python3
"""What a declared decoupling seat costs the escape pass, asked of the pass's own probes (decision 42, T4;
MESHSAT-1357, stream d6dec, 27 September 2026).

`escape_cost` holds no KiCad call: escape.py hands it the probes of every attempt it made for a refused pad and its
own clearance test. Here the clearance test is a small board of circles, so the rule runs on any host; the pass
itself is held to a real board by tests/test_decoupling_board.py, where KiCad is."""
import os, sys, ast, math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import escape_cost


INTENT = {"bypass": [{"cap": "C1", "part": "U1", "pin": "3", "net": "+3V3", "class": "D", "basis": "x"},
                     {"cap": "C2", "part": "U1", "pin": "9", "net": "+1V1", "class": "L", "basis": "x"},
                     {"cap": "C3", "part": "U2", "pin": "3", "net": "+5V", "class": "R", "basis": "x", "same_side": True},
                     {"cap": "C9", "part": "U4", "pin": "3", "net": "+3V4", "class": "D", "basis": "x"},
                     {"cap": "C7", "part": "U1", "pin": "20", "net": "+3V3", "class": "B2", "basis": "x"}],
          "power_loops": [{"converter": "U2", "loop": "input", "caps": ["C4"], "parts": ["Q1", "R1"], "class": "R"}]}
SIDE = {"U1": "F", "U2": "F", "U4": "F", "U7": "F", "U11": "F", "C1": "F", "C2": "F", "C3": "F", "C4": "F", "Q1": "F",
        "R1": "F", "C9": "B", "C7": "F"}
# the obstacles of the small board: (reference, x, y, radius)
PADS = [("C1", 2.0, 0.0, 0.4), ("C3", 12.0, 0.0, 0.4), ("Q1", 14.0, 0.0, 0.6), ("C9", 22.0, 0.0, 0.4),
        ("R9", 32.0, 0.0, 0.4), ("C7", 42.0, 0.0, 0.4)]


def _clear(pt, r, lane, ignore):
    for ref, x, y, rr in PADS:
        if ignore and ref in ignore: continue
        if math.hypot(pt[0] - x, pt[1] - y) < r + rr + lane: return False
    return True


def _cost():
    return escape_cost.Cost(INTENT, SIDE.get)


def t_a_pad_refused_by_its_parts_own_window_capacitor_is_lost_to_the_window():
    c = _cost()
    tried = [(0.35, [((2.0, 0.3), 0.3), ((1.5, 0.3), 0.1)])]
    assert not all(_clear(p, r, 0.35, None) for p, r in tried[0][1]), "the fixture's pad is not refused to begin with"
    assert c.ask("U1", "4", tried, _clear) == "window"
    assert any("U1 lost 1 escape(s) to its own-pin windows" in l and "C1" in l for l in c.lines()), c.lines()


def t_a_pad_refused_by_something_else_is_lost_to_nothing_here():
    """THE ACCEPTABLE FIXTURE: R9 is no declared capacitor, so no cause changes the answer and none is blamed."""
    c = _cost()
    assert c.ask("U1", "30", [(0.35, [((32.0, 0.3), 0.3)])], _clear) is None
    assert "1 refused for another reason" in c.lines()[0] and "0 refused pad(s) would have been escaped" in c.lines()[0], c.lines()


def t_bulk_in_the_fan_is_no_window_and_is_not_excused_as_one():
    """A class B2 capacitor has no window (D3 opens the fan for classes D and L only): a pad it costs is reported
    as refused for another reason, which is how a bulk capacitor parked in a fan shows up."""
    c = _cost()
    assert c.refs("U1", "window") == {"C1", "C2"}, c.refs("U1", "window")
    assert c.ask("U1", "21", [(0.35, [((42.0, 0.3), 0.3)])], _clear) is None


def t_a_converters_own_power_stage_is_its_own_cause():
    c = _cost()
    assert c.refs("U2", "stage") == {"C3", "C4", "Q1", "R1"}, c.refs("U2", "stage")
    assert c.ask("U2", "5", [(0.75, [((12.0, 0.5), 0.3)]), (0.35, [((14.0, 0.2), 0.3)])], _clear) == "stage"
    assert any("U2 lost 1 escape(s) to its own power-stage parts" in l for l in c.lines())


def t_a_far_side_capacitor_costs_the_part_it_sits_under_whoever_it_serves():
    """D12's C15 and C16 serve U4 and sit inside U7's fan: the cost is U7's."""
    c = _cost()
    assert c.refs("U7", "far_side") == {"C9"} and c.refs("U4", "far_side") == {"C9"}
    assert c.ask("U7", "2", [(0.35, [((22.0, 0.3), 0.3)])], _clear) == "far_side"
    assert any("U7 lost 1 escape(s) to declared capacitors on the side opposite it" in l for l in c.lines())


def t_a_part_left_to_the_router_is_asked_about_its_pins_via_sites():
    c = _cost()
    sites = [((22.0, 0.3), 0.3), ((22.0, 1.0), 0.3), ((22.0, 3.0), 0.3)]
    assert c.pin_sites("U11", "5", sites, _clear, lane=0.35) == 2
    assert c.pin_sites("U11", "4", [((60.0, 0.0), 0.3)], _clear) == 0, "a free site was counted"
    assert any("U11 is left to the router" in l and "2 of the via site(s) at 1 of its pins" in l for l in c.lines()), c.lines()


def t_an_exposed_pads_via_site_refused_by_a_far_side_capacitor_is_counted():
    c = _cost()
    assert c.site_refused("U7", "C9") is True and c.site_refused("U7", "R9") is False
    assert any("U7 had 1 via site(s) of its exposed pad refused by the far-side capacitor C9" in l for l in c.lines())


def t_the_question_never_lays_copper():
    """Asked of escape.py by its AST: `ignore` reaches `clear` only through the question (`_ask_clear`), and the
    calls that precede a via or a track being added pass no `ignore`."""
    tree = ast.parse(open(os.path.join(TOOLS, "escape.py"), encoding="utf-8").read())
    with_ignore = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "clear":
            if len(n.args) > 6 or any(k.arg == "ignore" for k in n.keywords): with_ignore.append(n.lineno)
    ask = next(f for f in ast.walk(tree) if isinstance(f, ast.FunctionDef) and f.name == "_ask_clear")
    inside = {n.lineno for n in ast.walk(ask) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "clear"}
    assert with_ignore and set(with_ignore) <= inside, "clear() is called with `ignore` outside the question: lines %s" % sorted(set(with_ignore) - inside)
    adds = [n for n in ast.walk(ask) if isinstance(n, ast.Attribute) and n.attr in ("Add", "SaveBoard")]
    assert not adds, "the question adds something to the board"
