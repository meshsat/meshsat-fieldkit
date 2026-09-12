#!/usr/bin/env python3
"""A pair may not short itself, and the two places where it did are the two that were exempt from asking.

Measured on A24, 12 September 2026 (MESHSAT-862, appendix 32.134). A's three ribbon pairs laid 3 of 3 for the
first time and the pre-route DRC then reported 22 hard, 13 of them BETWEEN THE PAIR'S OWN TWO NETS at the
J_AB1 station fan: `shorting_items` between /USB_D8_N and /USB_D8_P on 0.1 mm segments, and a clearance item
between /USB_D8_N and /USB_WALL_N. The tool had printed a DIVE line for that very pair, so the geometry was
seen; what went down unasked was the fan.

Every piece this tool lays is tested against that leg's own occupancy map, which counts the partner's copper
as an obstacle, EXCEPT in two callers, and both exemptions are about pads:

  `fan_leg`  exempts the last 1.2 mm of the run into the pad, because the partner's PAD legitimately blocks
             the map there and a fan that refused to enter its own station would lay nothing.
  `stub`     lays a straight piece without asking when start and goal fall inside one grid cell.

Neither exemption was ever meant to excuse the partner's TRACKS, and both did. `own_clear` is the question
they now ask, and the pair is judged once more after it is laid, so no pair can be kept whose own two legs
break the class clearance.

The rules read the source: the defect leaves no exception and no log line, only copper."""
import math, os, re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get("PAIR_OWN_SRC", os.path.join(TOOLS, "pair_preroute.py"))


def _src():
    return open(SRC, errors="replace").read()


def _body(name, src=None):
    s = src if src is not None else _src()
    i = s.find("def %s(" % name)
    assert i >= 0, "pair_preroute.py has no %s" % name
    ind = len(s[:i].split("\n")[-1])
    out = []
    for ln in s[i:].split("\n")[1:]:
        if ln.strip() and len(ln) - len(ln.lstrip()) <= ind: break
        out.append(ln)
    return "\n".join(out)


def t_the_helper_exists_and_asks_about_the_other_leg():
    b = _body("own_clear")
    assert "other_of(net)" in b, "own_clear does not look at the other leg of this pair"
    assert "clr_c" in b, "own_clear judges by something other than the class clearance"
    assert "PCB_VIA" in b, "own_clear ignores the partner's vias (a dive lays two of them)"


def t_the_fan_asks_before_it_takes_its_1_2_mm_exemption():
    """`if clear: seg(...)` was the whole of it, and `clear` is answered by a map whose last 1.2 mm is skipped."""
    b = _body("fan_leg")
    m = re.search(r"if clear[^\n]*:\s*seg\(", b)
    assert m is None or "own_clear" in m.group(0), "fan_leg still lays its straight fan without asking about the partner:\n  " + (m.group(0) if m else "")
    assert "own_clear" in b, "fan_leg never consults own_clear"


def t_the_sub_cell_stub_shortcut_asks_too():
    b = _body("stub")
    i = b.find("1.5 * gr.G")
    assert i >= 0, "the stub shortcut is gone; this rule needs rewriting against what replaced it"
    assert "own_clear" in b[i:i + 400], "the stub's straight shortcut still lays copper without asking about the partner"


def t_a_laid_pair_is_judged_against_its_own_partner_before_it_is_kept():
    """The crossing test of 9 September answers only crossings: two segments 0.05 mm apart never cross."""
    s = _src()
    assert "_near" in s and "_seg_gap(" in s, "no gap test between the two legs of a laid pair"
    i = s.find("if _near and not _cross:")
    assert i >= 0, "a pair whose own legs breach the clearance is not rolled back"
    assert "rollback()" in s[i:i + 300], "the near-miss verdict does not roll the pair back"


def t_the_geometry_helpers_are_right():
    """_pt_seg and _seg_gap are pure functions of numbers, so they are run here rather than read.

    They carry the verdict for every pair on every board, and both cases that matter are endpoint cases:
    a point beyond the end of a segment (clamped, not projected past it) and two parallel segments."""
    s = _src(); i = s.find("def _pt_seg("); j = s.find("def fp_centre(")
    assert 0 <= i < j, "the helpers are not where this rule looks for them"
    ns = {"math": math}
    exec(compile(s[i:j], "pair_preroute.py", "exec"), ns)
    pt, gap = ns["_pt_seg"], ns["_seg_gap"]
    assert abs(pt(0.0, 1.0, 0.0, 0.0, 10.0, 0.0) - 1.0) < 1e-9
    assert abs(pt(-3.0, 4.0, 0.0, 0.0, 10.0, 0.0) - 5.0) < 1e-9, "a point before the start is projected onto the line instead of the segment"
    assert abs(pt(14.0, 3.0, 0.0, 0.0, 10.0, 0.0) - 5.0) < 1e-9, "a point past the end is projected onto the line instead of the segment"
    assert abs(pt(1.0, 1.0, 2.0, 2.0, 2.0, 2.0) - math.hypot(1.0, 1.0)) < 1e-9, "a zero-length segment (two identical ends) is not measured as a point"
    assert abs(gap(0.0, 0.0, 10.0, 0.0, 0.0, 0.27, 10.0, 0.27) - 0.27) < 1e-9, "two parallel legs at the pair pitch do not read as that pitch apart"
    assert gap(0.0, 0.0, 10.0, 0.0, 20.0, 0.0, 30.0, 0.0) == 10.0


def t_a_coupled_pair_at_its_own_pitch_is_never_refused():
    """The bar this rule protects: the check must refuse a fan that folds back on its partner and never the
    pair's own coupled run. A USB pair here is w 0.13 with a gap of 0.14, so its legs run 0.27 mm apart
    centre to centre, and the demand is the class clearance plus one width. The generator's own floor
    (`s = max(s, clr_c + 0.013)`) is what keeps those two apart, so it is checked here as well."""
    s = _src()
    assert re.search(r"s = max\(s, clr_c \+ 0\.01\d\)", s), "the intra-pair gap no longer has the class clearance as its floor"
    w, gap_, clr = 0.13, 0.14, 0.127
    need = max(0.0, clr - 0.005) + w
    assert w + gap_ > need, "a correctly coupled pair would be refused by its own clearance test (%.3f against %.3f)" % (w + gap_, need)

def t_the_two_offset_legs_are_judged_against_each_other():
    """The occupancy maps cannot answer this one: both legs are laid by this pair, so when the maps are built
    neither is on the board, and each leg's own map excuses its partner by construction. A's /USB_D8 came out
    of the offset loop with its two legs 0.038 mm apart in eleven places against a 0.249 mm demand."""
    b = _body("legs_clear")
    assert "_seg_dist(" in b, "legs_clear never measures one leg against the other"
    assert "clr_c + wid(L)" in b, "the mutual test does not use the class clearance and the leg width"


def t_a_crossing_is_distance_zero():
    """_seg_gap alone reports the endpoint distances, which for two crossing segments are all positive: an X
    of two 10 mm legs reads 5 mm apart. Every caller that asks "how close" must get zero there."""
    s = _src(); i = s.find("def _pt_seg("); j = s.find("def fp_centre(")
    ns = {"math": math}; exec(compile(s[i:j], "pair_preroute.py", "exec"), ns)
    assert ns["_seg_dist"](0.0, 0.0, 10.0, 10.0, 0.0, 10.0, 10.0, 0.0) == 0.0, "two crossing legs do not read as touching"
    assert abs(ns["_seg_dist"](0.0, 0.0, 10.0, 0.0, 0.0, 0.27, 10.0, 0.27) - 0.27) < 1e-9
    assert ns["_seg_gap"](0.0, 0.0, 10.0, 10.0, 0.0, 10.0, 10.0, 0.0) > 4.9, "this is the trap the rule above exists for"

def t_a_twist_is_declared_only_where_the_pads_are_on_opposite_sides():
    """A's /USB_D8 runs between two IDC headers that both carry P on the same side, and the tool declared a
    twist anyway: the entry-station branch forces side_a, side_b to +1 and -1 so the swap machinery gets its
    chance, and when neither station is swappable that forced value fell straight through to `crossing = True`.
    The pair then dived at a 2.54 mm pad field for no reason and laid its N fan across its own P leg."""
    s = _src()
    assert "real_a, real_b = side_a, side_b" in s, "the honest sides are not kept before the entry-station forcing"
    i = s.find("if swappable_(pa, na): twist =")
    assert i > 0
    tail = s[i:i + 1200]
    assert "crossing = real_a * real_b < 0" in tail, "a pair with nothing to swap still takes the forced twist"
    assert "crossing = True" not in tail.split("crossing = real_a")[0], "the forced twist still reaches `crossing = True`"
