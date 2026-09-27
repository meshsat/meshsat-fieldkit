#!/usr/bin/env python3
"""The decoupling rules of decision 42 as functions, so every tool asks one place (MESHSAT-1357, 27 September 2026).

`v2/docs/feasibility/DECOUPLING.md` rules the placement of a decoupling capacitor by its CLASS, the role its maker
gives it, and section 8.1 lists what the tools owe for it (T1 to T10). Until this file the two placers, the gate and
the escape pass each carried their own copy of a number or of a selection, and the copies had drifted: the placers
held every value to 3.0 mm measured to the capacitor's centre, the gate held a value string that spells "u " to
6.0 mm measured to its rail pad, and the escape fan and the escape pass selected different parts. What is here:

  CLASSES, normalise(), form_problems()     the declaration's schema (T5): class, basis and what each class carries
  limit(), judge()                          one limit, keyed by the class and never by the value string (T2), with the
                                            maker's own distance as a cap no allowance can pass (D6)
  parse_allow()                             an allowance names its capacitor (T6)
  escaped(), copper_fanned(), fanned()      which part gets an escape fan (T1), on plain pad coordinates
  rotations(), best_rotation()              the four orientations of a two-pad capacitor (T3)
  window_box(), in_own_window()             the own-pin window of a class D or L entry (D3, T4)
  via_allowance_mm(), far_side()            the side opposite the part (D5, T9)
  own_via()                                 the ground pad's own via (D2, T10)

NOTHING HERE IMPORTS KiCad. Every function takes plain numbers, tuples and dictionaries, so its fixtures run on a host
that has no pcbnew, and the tools that do hold a board (`bypass_slots.py`, `bypass_place.py`, `intent_checks.py`,
`escape.py`) hand it coordinates through `fan_select.py`'s adapters. Lengths are millimetres unless a name ends in
`_nm`: the fan selection takes KiCad's own integer nanometres, because it must decide exactly as `escape.py` decided
before the selection moved here.

THE NUMBERS AND WHAT THEY ARE. 3.0 mm and 6.0 mm are PROJECT SCREENS, not makers' numbers (DECOUPLING.md section 1:
fifteen makers' documents read, none gives a distance but TI's TPA6132A2, 5 mm). 2.2 mm is the project's escape fan.
A screen separates a pass from a justified deviation; a maker's distance separates a justified deviation from a
failure. Nothing in this file turns a deviation into a pass."""
import math, re

CLASSES = ("R", "D", "L", "A", "B1", "B2")
SCREEN_MM = 3.0          # classes R, D and L: rail pad to the pin (R: to VIN, or to the output loop's pad)
BULK_SCREEN_MM = 6.0     # class B2: the gate's existing bar for bulk no maker places
FAN_MM = 2.2             # the escape fan: a fanned part's courtyard grown by this much is closed to capacitors
ESCAPE_PITCH_NM = 700000     # escape.py: closest two SMD pads 0.7 mm apart or less
ESCAPE_J_PITCH_NM = 600000   # escape.py: a J part over 0.6 mm pitch routes without escapes
FAN_PITCH_NM = 1000000       # the placers' fan: eight or more pads, the closest two 1.0 mm apart or less
FAN_MIN_PADS = 8
NOT_STATED = "not stated by the maker"

# The keys five generators wrote before there was one schema (round 8, 26 and 27 September 2026), and the key each
# becomes. A reader that knows them reads every committed intent file; a generator moves to the canonical key when
# it is next regenerated, and `aliases_used` says which entries have not.
ALIASES = {"floor": "value_floor", "floor_uF": "value_floor", "esr": "esr_max", "esr_bound": "esr_max"}
CANONICAL = ("cap", "part", "pin", "net", "class", "basis", "value_floor", "value_ceiling", "esr_max", "same_side",
             "maker_mm", "provisional", "serves", "pin_role")


class Refused(ValueError):
    """A declaration this project's rules cannot judge: no class, a class that is not ruled, no basis."""


def normalise(entry):
    """(entry with canonical keys, [the alias keys it carried]). Values are not converted: `floor_uF: 0.47` becomes
    `value_floor: 0.47`, and value_farads() reads either spelling."""
    out, used = {}, []
    for k, v in entry.items():
        c = ALIASES.get(k, k)
        if c != k: used.append(k)
        if c in out and out[c] not in (None, "") and v in (None, ""): continue
        out[c] = v
    return out, used


_UNIT = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "μ": 1e-6, "m": 1e-3}


def value_farads(v):
    """A floor or ceiling as farads: 0.47 (a number is microfarads, the unit board D's generator wrote), "1u",
    "198n", "2.2u (-20 percent)", "0.47u effective". None when the text states no number, which is how a maker
    that states none is written (NOT_STATED)."""
    if v is None or isinstance(v, bool): return None
    if isinstance(v, (int, float)): return float(v) * 1e-6
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([pnuµμm])", str(v))
    return float(m.group(1)) * _UNIT[m.group(2)] if m else None


def form_problems(entry):
    """What is wrong with one declaration's FORM, as sentences; empty when it can be judged. T5's schema:
    every entry a ruled class and the maker's clause; class L the maker's value floor and what the maker says of
    ESR, each either a number or the statement that the maker gives none; class R the maker's same side."""
    e, _ = normalise(entry); out = []
    cap = e.get("cap") or "?"
    if e.get("class") not in CLASSES:
        out.append("%s: class %r is not one of %s" % (cap, e.get("class"), ", ".join(CLASSES)))
    if not str(e.get("basis") or "").strip():
        out.append("%s: no basis, the maker's clause this class rests on" % cap)
    if e.get("class") == "L":
        if e.get("value_floor") in (None, ""):
            out.append("%s: class L without `value_floor`: the maker's stability floor, or '%s' with the value "
                       "its application circuit draws" % (cap, NOT_STATED))
        if "esr_max" not in e:
            out.append("%s: class L without `esr_max`: the maker's ESR bound, or '%s'" % (cap, NOT_STATED))
    if e.get("class") == "R" and e.get("same_side") is not True:
        out.append("%s: class R without `same_side: true` (R3: a converter's power stage is never on the other "
                   "side)" % cap)
    if "maker_mm" in e:
        try:
            if float(e["maker_mm"]) <= 0: raise ValueError
        except (TypeError, ValueError):
            out.append("%s: maker_mm %r is not a distance" % (cap, e.get("maker_mm")))
    return out


# ------------------------------------------------------------------------------------------------ T2: the limit
def limit(entry):
    """{"screen_mm", "cap_mm", "measure", "why"} for one declaration, by its class.

    screen_mm  the project's screen, rail pad to pin: within it is a pass. None where the ruling sets no distance
               (class A: the series resistor dominates the loop, A2; class B1: the maker frees rail bulk, B1).
    cap_mm     the maker's own distance where the maker gives one (D6): past it nothing is allowed.
    The value string is not an argument, so a "10u" and a "10u 25V 1210" of one class cannot get two limits."""
    e, _ = normalise(entry); k = e.get("class")
    if k not in CLASSES:
        raise Refused("%s: class %r is not one of %s, so no limit applies and the entry is refused"
                      % (e.get("cap") or "?", k, ", ".join(CLASSES)))
    cap_mm = None
    if e.get("maker_mm") is not None:
        cap_mm = float(e["maker_mm"])
        if cap_mm <= 0: raise Refused("%s: maker_mm %r is not a distance" % (e.get("cap") or "?", e.get("maker_mm")))
    if k in ("R", "D", "L"):
        s, why = SCREEN_MM, {"R": "class R: the input capacitor's rail pad within the 3.0 mm screen of VIN, or an "
                                  "output capacitor's of the output loop's pad (R1, R4)",
                             "D": "class D: the own-pin window, rail pad within the 3.0 mm screen (D2)",
                             "L": "class L: seated as class D (L1), the 3.0 mm screen"}[k]
    elif k == "B2": s, why = BULK_SCREEN_MM, "class B2: bulk no maker places, the gate's existing 6.0 mm screen (B2)"
    elif k == "A": s, why = None, ("class A: no fixed distance, the nearest free seat outside the fan at the pin end "
                                   "of its RC, its distance recorded (A2)")
    else: s, why = None, ("class B1: rail bulk the maker frees of a pin distance; seated toward the regulator it is "
                          "declared against, its distance printed (B1)")
    if cap_mm is not None: why += "; the maker's own %.1f mm is a limit no allowance passes (D6)" % cap_mm
    return {"screen_mm": s, "cap_mm": cap_mm, "measure": "rail pad to pin", "why": why}


def judge(entry, d_mm, allowance=None):
    """(status, sentence) for a declaration whose rail pad sits d_mm from the pin it is declared against.

    pass        within the screen (and within the maker's distance)
    justified   past the screen, within the maker's distance if there is one, and an allowance NAMES this capacitor
    recorded    a class with no distance (A, B1): the distance is printed and decides nothing here
    fail        past the screen with no allowance, or past the maker's distance whatever the allowance says
    An allowance never produces `pass`."""
    lim = limit(entry); cap = entry.get("cap") or "?"
    if lim["cap_mm"] is not None and d_mm > lim["cap_mm"] + 1e-9:
        return "fail", ("%s: %.2f mm, past its maker's %.1f mm; no allowance passes a maker's distance%s"
                        % (cap, d_mm, lim["cap_mm"], " (one was given and is refused)" if allowance else ""))
    if lim["screen_mm"] is None:
        return "recorded", "%s: %.2f mm, recorded; %s" % (cap, d_mm, lim["why"])
    if d_mm <= lim["screen_mm"] + 1e-9:
        return "pass", "%s: %.2f mm, within the %.1f mm screen" % (cap, d_mm, lim["screen_mm"])
    if allowance and str(allowance).strip():
        return "justified", ("%s: %.2f mm, past the %.1f mm screen, a justified deviation: %s"
                             % (cap, d_mm, lim["screen_mm"], str(allowance).strip()[:120]))
    return "fail", "%s: %.2f mm, past the %.1f mm screen, and no allowance names it" % (cap, d_mm, lim["screen_mm"])


# ------------------------------------------------------------------------------------------ T6: the allow file
_ALLOW = re.compile(r"^\s*([A-Za-z]+[A-Za-z0-9_]*\d[A-Za-z0-9_]*)\s*:\s*(\S.*?)\s*$")


def parse_allow(text):
    """({capacitor: reason}, [(line number, line, why it is refused)]).

    A line is `C36: the reason`. It allows ONE capacitor. A line that names none allows nothing and is refused by
    name, because the line of 8 September that every board carried passed every far capacitor on the board and
    quoted itself as the reason for each (DECOUPLING.md 3.2(f): 33 allowances counted as passes on boards B and
    P). A capacitor named twice is refused the second time: two reasons for one seat is a file nobody read."""
    allow, refused = {}, []
    for i, raw in enumerate(str(text or "").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"): continue
        m = _ALLOW.match(line)
        if not m or not re.match(r"^C", m.group(1)):
            refused.append((i, line[:100], "names no capacitor: an allowance is `C<n>: reason` and covers that one")); continue
        ref, reason = m.group(1), m.group(2)
        if len(reason) < 12:
            refused.append((i, line[:100], "gives no reason a reader could check")); continue
        if ref in allow:
            refused.append((i, line[:100], "%s is already allowed by an earlier line" % ref)); continue
        allow[ref] = reason
    return allow, refused


# ---------------------------------------------------------------------------------------- T1: the fan selection
def min_pitch_nm(points):
    """The smallest distance between two pads that are not at one place, as escape.py measures it; 1e9 for none."""
    best = 1e9; n = len(points)
    for i in range(n):
        xi, yi = points[i]
        for j in range(i + 1, n):
            d = math.hypot(xi - points[j][0], yi - points[j][1])
            if 0 < d < best: best = d
    return best


def is_fine(fpid, smd_points_nm):
    """escape.py's `is_fine`, unchanged: the footprint's name holds SOT-23-6 or SOT-23-8, or its closest two SMD
    pads are 0.7 mm apart or less. `smd_points_nm` is EVERY pad of attribute SMD, the paste apertures KiCad draws
    as pads among them, because that is what the escape pass counts today; whether it should is a question about
    the escape pass (DECOUPLING.md 12.3) and this function does not answer it by changing what is escaped."""
    if re.search(r"SOT-23-[68]", str(fpid or "")): return True
    return min_pitch_nm(smd_points_nm) <= ESCAPE_PITCH_NM


def escaped(ref, fpid, smd_points_nm, escape_skip=()):
    """Does the escape pass escape this part: fine pitch, less a J part over 0.6 mm and the board's ESCAPE_SKIP."""
    if not is_fine(fpid, smd_points_nm): return False
    if str(ref).startswith("J") and min_pitch_nm(smd_points_nm) > ESCAPE_J_PITCH_NM: return False
    return str(ref) not in set(escape_skip or ())


def copper_fanned(copper_points_nm):
    """The placers' own term: eight or more NUMBERED SMD pads that carry copper, the closest two 1.0 mm apart or
    less. It keeps the 0.8 mm TQFP and LQFP fans of 9 September, which the escape pass does not escape, and it no
    longer counts a paste aperture as a pin (3.2(a): the SOIC-8-1EP's four apertures made a 1.27 mm part fine)."""
    if len(copper_points_nm) < FAN_MIN_PADS: return False
    return min_pitch_nm(copper_points_nm) <= FAN_PITCH_NM


def fanned(ref, fpid, smd_points_nm, copper_points_nm, escape_skip=()):
    """(fanned, why): the set T1 rules, the union of the two terms."""
    e = escaped(ref, fpid, smd_points_nm, escape_skip); c = copper_fanned(copper_points_nm)
    why = " and ".join(w for w, on in (("the escape pass escapes it", e),
                                       ("eight or more copper pads at 1.0 mm or less", c)) if on)
    return (e or c), (why or "neither escaped nor eight copper pads at 1.0 mm or less")


# ------------------------------------------------------------------------------------------- T3: the rotations
def rotations():
    return (0.0, 90.0, 180.0, 270.0)


def rotate(dx, dy, deg):
    """A pad's offset from its footprint's origin after the footprint turns `deg` (KiCad: counter-clockwise on a
    screen whose y axis points down)."""
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return (dx * c + dy * s, -dx * s + dy * c)


def best_rotation(centre, rail_pad_offset, pin, allowed=None):
    """(rotation, rail pad to pin distance): of the four orientations at one seat, the one that brings the RAIL pad
    nearest the pin. `rail_pad_offset` is the rail pad's offset at rotation 0. `allowed(rotation)` lets the caller
    refuse an orientation whose courtyard does not fit; with none allowed the answer is (None, None)."""
    best = (None, None)
    for r in rotations():
        if allowed is not None and not allowed(r): continue
        ox, oy = rotate(rail_pad_offset[0], rail_pad_offset[1], r)
        d = math.hypot(centre[0] + ox - pin[0], centre[1] + oy - pin[1])
        if best[1] is None or d < best[1] - 1e-9: best = (r, d)
    return best


# ------------------------------------------------------------------------------- D3, T4: the own-pin window
def _grow(box, by):
    return (box[0] - by, box[1] - by, box[2] + by, box[3] + by)


def boxes_meet(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


EDGE_PIN_MM = 1.5        # a pin whose centre is further than this inside the courtyard is no edge pin (an exposed pad)


def pin_side(courtyard, pin):
    """The courtyard edge a pin sits at, "w", "e", "n" or "s" (y grows downward, so "n" is the smaller y), or None
    for a pin that is not at an edge: an exposed pad in the middle of a part has no window in front of it."""
    x0, y0, x1, y1 = courtyard; px, py = pin
    d = {"w": px - x0, "e": x1 - px, "n": py - y0, "s": y1 - py}
    side = min(d, key=lambda k: d[k])
    return side if d[side] <= EDGE_PIN_MM + 1e-9 else None


def window_box(courtyard, pin, along, fan=FAN_MM):
    """The own-pin window of a pin at a part's courtyard edge, as a box (x0, y0, x1, y1): a strip one capacitor
    courtyard wide, centred on the pin, from the courtyard's edge to the fan's edge (D3). `along` is the
    capacitor courtyard's extent ALONG THE PIN ROW in the orientation being tried. None for a pin with no edge."""
    x0, y0, x1, y1 = courtyard; px, py = pin
    side = pin_side(courtyard, pin)
    if side is None: return None
    h = along / 2.0
    if side == "w": return (x0 - fan, py - h, x0, py + h)
    if side == "e": return (x1, py - h, x1 + fan, py + h)
    if side == "n": return (px - h, y0 - fan, px + h, y0)
    return (px - h, y1, px + h, y1 + fan)


def fan_blocks(cap_box, fan_boxes, entry, own_window=None, own_converter=None):
    """The fanned part whose fan refuses this capacitor's courtyard, or None.

    fan_boxes      [(reference, box)], each a fanned part's courtyard grown by the fan
    entry          the declaration being seated
    own_window     the entry's own-pin window (class D and L, D3): inside it the fan of the part it serves is open
    own_converter  the reference of the converter a class R entry is a power-stage part of (R2): that one fan is
                   open to it, and every other part's fan stays closed
    The fan of any OTHER part is never opened, whatever the class."""
    k = entry.get("class")
    for ref, fb in fan_boxes:
        if not boxes_meet(cap_box, fb): continue
        if k == "R" and own_converter is not None and ref == own_converter: continue
        if k in ("D", "L") and ref == entry.get("part") and own_window is not None \
           and cap_box[0] >= own_window[0] - 1e-6 and cap_box[1] >= own_window[1] - 1e-6 \
           and cap_box[2] <= own_window[2] + 1e-6 and cap_box[3] <= own_window[3] + 1e-6: continue
        return ref
    return None


# ------------------------------------------------------------------------------------- D5, T9: the other side
ETA0 = 376.730313668; C_MM_NS = 299.792458; MU0_NH_PER_MM = 4 * math.pi * 1e-1


def l_track_nh_per_mm(w, h):
    """A track of width w over a plane h below it: Hammerstad and Jensen's microstrip Z01 over c (DECOUPLING.md
    5.1; INFERRED, a closed form for comparing seats and not a field solve)."""
    u = w / h
    f = 6 + (2 * math.pi - 6) * math.exp(-((30.666 / u) ** 0.7528))
    return ETA0 / (2 * math.pi) * math.log(f / u + math.sqrt(1 + 4 / u ** 2)) / C_MM_NS


def l_via_pair_nh(length, pitch, radius=0.15):
    """Two vias carrying the loop current out and back: the two-wire line, (mu0 l / pi) acosh(s / 2r)."""
    return MU0_NH_PER_MM * length / math.pi * math.acosh(pitch / (2 * radius))


def stack_geometry(stack):
    """(outer copper, first dielectric, board thickness) of one row of stackup_write.STACKS."""
    cu = [it for it in stack if len(it) == 2]; di = [it for it in stack if len(it) == 4]
    if len(cu) < 2 or not di: raise Refused("a stackup row with %d copper layers and %d dielectrics" % (len(cu), len(di)))
    return float(cu[0][1]), float(di[0][2]), sum(float(it[1]) for it in cu) + sum(float(it[2]) for it in di)


def via_allowance_mm(stack, track_w=0.25, via_pitch=0.8, drill=0.3):
    """The length of outer track whose inductance equals the via pair a far-side capacitor needs, for one stackup
    row: the far side's cost in the unit every other seat is measured in (section 5.2). The via runs from the far
    surface to the first plane under the part: the board less the near outer copper and the first dielectric.

    It is computed from the row, not typed. The page's 3.7 mm for JLC06161H-3313 took a board of 1.5832 mm; the
    fabricator's own layers, which are this row, sum to 1.5384 mm and give 3.5 mm (d6dec finding F-1). The
    four-layer rows sum as the page has them and give its 2.3 mm."""
    cu, h, board = stack_geometry(stack)
    return l_via_pair_nh(board - h - cu, via_pitch, drill / 2.0) / l_track_nh_per_mm(track_w, h)


def stack_from_layers(layers):
    """A board's own stackup, as `stackup_read.layers()` reads it, in the row form of `stackup_write.STACKS`: the
    copper and dielectric layers in order, the mask, paste and silk left out."""
    out = []
    for L in layers or []:
        t = L.get("type"); th = L.get("thickness")
        if th is None: continue
        if t == "copper": out.append((L.get("name"), float(th)))
        elif t in ("core", "prepreg"): out.append((t, L.get("material") or "", float(th), L.get("epsilon_r")))
    return out


def two_sided(smd_front, smd_back):
    """A board is assembled on both sides when it carries SMD footprints on both (section 3.3)."""
    return smd_front > 0 and smd_back > 0


def far_side(entry, board_two_sided, cap_box=None, fan_boxes=(), tht_boxes=()):
    """(offered, why) for a seat on the side opposite the part (D5).

    Refused on a board that is not already assembled on both sides (it would add an assembly side, which is money);
    refused for an entry whose maker names the same side (every class R entry, the STM32H743 in a non-BGA package);
    refused where the seat's courtyard meets the fan box of ANY fanned part, of either side, or a through-hole
    part's courtyard (board B's underside rule, kept as written)."""
    cap = entry.get("cap") or "?"
    if not board_two_sided:
        return False, "%s: this board carries SMD parts on one side only, and a far-side seat adds an assembly side" % cap
    if entry.get("class") == "R" or entry.get("same_side") is True:
        return False, "%s: its maker names the same side as the part (%s)" % (cap, "class R, R3" if entry.get("class") == "R" else "same_side")
    if cap_box is not None:
        for ref, fb in fan_boxes:
            if boxes_meet(cap_box, fb): return False, "%s: inside the escape fan of %s, where its escape vias come through" % (cap, ref)
        for ref, tb in tht_boxes:
            if boxes_meet(cap_box, tb): return False, "%s: over the through-hole part %s" % (cap, ref)
    return True, "%s: a far-side seat, judged by its in-plane distance plus the via allowance" % cap


def loop_equivalent_mm(d_in_plane, far, allowance_mm):
    return d_in_plane + (allowance_mm if far else 0.0)


# ------------------------------------------------------------------------------ D2, T10: the ground pad's own via
def own_via(pad, vias, other_pads, reach_mm=1.5, touch_mm=0.05):
    """The ground via a capacitor's ground pad reaches, and whether it is its own.

    pad         {"xy": (x, y), "net": name, "half": (hx, hy)}  the capacitor's ground pad
    vias        [{"xy": (x, y), "net": name, "r": radius}]
    other_pads  [{"ref": r, "num": n, "xy": (x, y), "net": name, "half": (hx, hy)}]  every other copper pad on the
                board, the capacitor's own rail pad among them
    Returns {"via": index or None, "length_mm": pad centre to via centre, "own": bool, "shared_with": [ref.pad]}.
    The via is the nearest one of the pad's net within `reach_mm`. It is the pad's OWN when no other part's pad of
    that net lands on it: a pad lands on a via when the via's barrel lies within the pad's copper, grown by
    `touch_mm`. The length is printed and not judged: SCAA082A 2.4 says "directly with a via" and gives no
    figure (T10)."""
    px, py = pad["xy"]; best = None
    for i, v in enumerate(vias):
        if v["net"] != pad["net"]: continue
        d = math.hypot(v["xy"][0] - px, v["xy"][1] - py)
        if d <= reach_mm + 1e-9 and (best is None or d < best[1]): best = (i, d)
    if best is None: return {"via": None, "length_mm": None, "own": False, "shared_with": []}
    v = vias[best[0]]; shared = []
    for q in other_pads:
        if q["net"] != pad["net"]: continue
        hx, hy = q["half"]
        if abs(v["xy"][0] - q["xy"][0]) <= hx + v["r"] + touch_mm and abs(v["xy"][1] - q["xy"][1]) <= hy + v["r"] + touch_mm:
            shared.append("%s.%s" % (q["ref"], q["num"]))
    return {"via": best[0], "length_mm": best[1], "own": not shared, "shared_with": sorted(shared)}
