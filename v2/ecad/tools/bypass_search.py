#!/usr/bin/env python3
"""The seat of one declared decoupling capacitor, searched one way by both placers (decision 42; MESHSAT-1357).

`bypass_slots.reserve` seats a capacitor before the packer fills the board and `bypass_place.py` moves one after it.
Each carried its own walk out from the pin, and both walked the same way: one orientation, the distance measured to
the capacitor's centre, 3.0 mm for every value, the fan of every part with eight SMD pads closed (DECOUPLING.md
3.2(b), (d), (e)). This is that walk once, under the ruling of section 6:

  * the limit is the CLASS's (decoupling_rules.limit), measured from the capacitor's RAIL pad to the pin (T2);
  * the four orientations are tried at every seat and the one that brings the rail pad nearest is kept (T3);
  * the fan set is the escape pass's own (fan_select, T1), and a fan is opened in two places only: a class D or L
    entry's own-pin window, and a converter's fan to its own class R parts (D3, R2, T4);
  * on a board already assembled on both sides a seat on the other side is offered, judged by its in-plane distance
    plus the stackup's via allowance, never inside any fanned part's fan box and never over a through-hole part,
    and never for an entry whose maker names the same side (D5, T9).

IT SEATS WITHIN THE SCREEN OR NOT AT ALL. A capacitor with no seat inside its class's screen is reported and left
where it is (to the packer, or where the packer put it): the nearest seat further out is `bypass_seats.py`'s to
name, because that report knows the packer's regions and this walk does not, and a seat taken inside a region
overflowed thirteen of them on board A (A81, appendix 32.311). Classes A and B1 have no screen; their nearest free
seat is looked for out to REACH_MM and its distance is recorded.

Needs KiCad's pcbnew. The rules themselves are in decoupling_rules.py, which does not."""
import os, sys, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import decoupling_rules as dr
import fan_select, stackup_read, stackup_write

MM = 1e6
REACH_MM = 12.0          # classes with no screen (A, B1): how far the nearest free seat is looked for
R_START, R_STEP, A_STEP = 0.8, 0.1, 10


def _box_mm(bb):
    return (bb.GetLeft() / MM, bb.GetTop() / MM, bb.GetRight() / MM, bb.GetBottom() / MM)


def allowance(board, path=None):
    """(mm, source): the via allowance of this board's own stackup, or of the default row for its copper layer
    count where the board file carries no stackup yet (a board still in the placement generator)."""
    layers = []
    if path and os.path.exists(path):
        try: layers = stackup_read.layers(path)
        except Exception: layers = []
    row = dr.stack_from_layers(layers)
    if len([x for x in row if len(x) == 2]) >= 2 and any(len(x) == 4 for x in row):
        return dr.via_allowance_mm(row), "the board file's own stackup"
    n = board.GetCopperLayerCount()
    name = {4: "JLC04161H-7628", 6: "JLC06161H-3313", 8: "JLC08161H-2116"}.get(n)
    if name is None: return None, "a board of %d copper layers has no inner plane to return through" % n
    return dr.via_allowance_mm(stackup_write.STACKS[name]), "stackup_write's row %s, the default for %d layers" % (name, n)


class Context:
    """What one board offers a seat, read once: its fans, its through-hole parts, its sides, its allowance."""

    def __init__(self, board, path=None, fan=dr.FAN_MM, rule_hit=False):
        self.board = board; self.path = path or board.GetFileName() or ""
        self.fan = fan; self.rule_hit = rule_hit
        self.skip = fan_select.escape_skip(self.path)
        self.fans = fan_select.fan_boxes(board, self.skip, fan)
        self.tht = fan_select.tht_boxes(board)
        f, bk = fan_select.smd_sides(board); self.smd = (f, bk); self.two_sided = dr.two_sided(f, bk)
        self.allow_mm, self.allow_src = allowance(board, self.path)
        self.edge = _box_mm(board.GetBoardEdgesBoundingBox())
        # only a rule area that forbids FOOTPRINTS blocks a part; the board-wide copper areas cover every spot
        self.rule = [z for z in board.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowFootprints()]
        self.rule_boxes = [_box_mm(z.GetBoundingBox()) for z in self.rule]
        self.converters = {}

    def converter_of(self, entry, intent=None):
        """The converter whose fan is open to a class R entry (R2): the part it is declared against when that part
        is the converter, the entry's own `converter` when it names one (an output capacitor declared against the
        inductor's pad), or the converter of the power loop that lists the capacitor."""
        if entry.get("class") != "R": return None
        if entry.get("converter"): return entry["converter"]
        for lp in (intent or {}).get("power_loops", []) or []:
            if entry.get("cap") in (lp.get("caps") or []): return lp.get("converter")
        fanned = {r for r, _ in self.fans}
        return entry.get("part") if entry.get("part") in fanned else None


def shapes(fp, rail_number):
    """{(far, rotation): (rail dx, rail dy, courtyard w, h, courtyard centre dx, dy)} in mm, relative to the
    footprint's position, read from KiCad by putting the footprint in each of its eight states and back."""
    out = {}
    pos = fp.GetPosition(); rot0 = fp.GetOrientationDegrees(); start_back = fp.GetLayer() != pcbnew.F_Cu
    flipped = False
    try:
        for far in (False, True):
            if far and not flipped: fp.Flip(fp.GetPosition(), False); flipped = True
            for r in dr.rotations():
                fp.SetOrientationDegrees(r); fp.SetPosition(pos)
                pad = next((q for q in fp.Pads() if q.GetNumber() == str(rail_number)), None)
                if pad is None: continue
                cb = fan_select.courtyard_box(fp)
                out[(far, r)] = ((pad.GetPosition().x - pos.x) / MM, (pad.GetPosition().y - pos.y) / MM,
                                 cb[2] - cb[0], cb[3] - cb[1],
                                 (cb[0] + cb[2]) / 2.0 - pos.x / MM, (cb[1] + cb[3]) / 2.0 - pos.y / MM)
    finally:
        if flipped: fp.Flip(fp.GetPosition(), False)
        fp.SetOrientationDegrees(rot0); fp.SetPosition(pos)
        assert (fp.GetLayer() != pcbnew.F_Cu) == start_back, "bypass_search: the footprint did not come back to its side"
    return out


def rail_pad_number(entry, cap_fp, pin_pad, netlist_pins=None):
    """(pad number, how it is known). The rail pad is the capacitor's pad on the pin's net. On a board whose nets
    are assigned the pads say so; before that the netlist beside the board does (`netlist_pins`: {pad: net} of the
    capacitor). With neither, the FARTHER pad is measured and named a bound: the rail pad is no further than it."""
    net = pin_pad.GetNetname() or entry.get("net") or ""
    named = [q.GetNumber() for q in cap_fp.Pads() if q.GetNetname() and q.GetNetname().lstrip("/") == str(net).lstrip("/")]
    if named: return named[0], "the board's nets"
    if netlist_pins:
        for num, n in sorted(netlist_pins.items()):
            if str(n).lstrip("/") == str(entry.get("net") or "").lstrip("/"): return str(num), "the netlist beside the board"
    return None, "not known: the capacitor's farther pad is measured, which bounds its rail pad"


def search(ctx, entry, cap_fp, part_fp, pin_pad, intent=None, netlist_pins=None, moving=(), tighten=None):
    """The best seat for one declared capacitor, or None with the reason.

    Returns {"seat": (x nm, y nm) or None, "far": bool, "rotation": deg, "d_mm": rail pad to pin in plane,
             "loop_mm": d_mm plus the via allowance on the far side, "status": "pass" | "recorded" | None,
             "limit": the class's limit, "rail": how the rail pad is known, "why": sentence}
    `moving` are references whose present courtyards do not count (capacitors this pass is about to move).
    `tighten` is a distance no seat may pass, for an arm that asks what a smaller screen seats; it never widens."""
    lim = dr.limit(entry)                       # raises decoupling_rules.Refused for an entry with no ruled class
    cap = entry.get("cap"); ref = part_fp.GetReference()
    if cap_fp.GetLayer() != part_fp.GetLayer():
        raise ValueError("bypass_search: %s is handed over on the side opposite %s; the caller puts it on the part's "
                         "side first, because `far` below means the side opposite the PART" % (cap, ref))
    pc = pin_pad.GetPosition(); px, py = pc.x / MM, pc.y / MM
    rail, how = rail_pad_number(entry, cap_fp, pin_pad, netlist_pins)
    nums = [q.GetNumber() for q in cap_fp.Pads() if str(q.GetNumber()).strip()]
    sh = {}
    for num in ([rail] if rail is not None else nums):
        for k, v in shapes(cap_fp, num).items(): sh.setdefault(k, []).append(v)
    if not sh: return {"seat": None, "status": None, "limit": lim, "rail": how, "why": "%s has no numbered pad" % cap}
    screen = lim["screen_mm"]; reach = (screen if screen is not None else REACH_MM)
    own_back = part_fp.GetLayer() != pcbnew.F_Cu
    pcy = fan_select.courtyard_box(part_fp)
    side_name = dr.pin_side(pcy, (px, py))
    conv = ctx.converter_of(entry, intent)
    far_ok, far_why = dr.far_side(entry, ctx.two_sided)
    if far_ok and ctx.allow_mm is None: far_ok, far_why = False, "%s: %s" % (cap, ctx.allow_src)
    # the courtyards near the pin, by side, read once: a seat is tested against tens of boxes, not the whole board
    span = reach + 6.0
    near = {False: [], True: []}
    for g in ctx.board.GetFootprints():
        gr = g.GetReference()
        if gr == cap or gr in moving: continue
        gb = fan_select.courtyard_box(g)
        if gb[2] < px - span or gb[0] > px + span or gb[3] < py - span or gb[1] > py + span: continue
        near[g.GetLayer() != pcbnew.F_Cu].append((gr, gb))
    fans = [(r, fb) for r, fb in ctx.fans if not (fb[2] < px - span or fb[0] > px + span or fb[3] < py - span or fb[1] > py + span)]
    tht = [(r, tb) for r, tb in ctx.tht if not (tb[2] < px - span or tb[0] > px + span or tb[3] < py - span or tb[1] > py + span)]
    rules = [(z, zb) for z, zb in zip(ctx.rule, ctx.rule_boxes)
             if not (zb[2] < px - span or zb[0] > px + span or zb[3] < py - span or zb[1] > py + span)]
    out = (px - part_fp.GetPosition().x / MM, py - part_fp.GetPosition().y / MM)
    nn = math.hypot(*out) or 1.0; ux, uy = out[0] / nn, out[1] / nn
    best = None; refused = {}
    max_off = max(math.hypot(v[0], v[1]) for vs in sh.values() for v in vs)
    sides = [False] + ([True] if far_ok else [])
    r10 = int(round(R_START * 10)); r_end = int(round((reach + max_off) * 10))
    while r10 <= r_end:
        r = r10 / 10.0
        if best is not None and r - max_off > best["loop_mm"] + 1e-9: break
        for ang in range(0, 360, A_STEP):
            th = math.radians(ang); dx, dy = ux * math.cos(th) - uy * math.sin(th), ux * math.sin(th) + uy * math.cos(th)
            cx, cy = px + dx * r, py + dy * r
            for far in sides:
                for rot in dr.rotations():
                    vs = sh.get((far, rot))
                    if not vs: continue
                    # the rail pad's distance; with the rail pad unknown, the farther of the pads (a bound)
                    d = max(math.hypot(cx + v[0] - px, cy + v[1] - py) for v in vs)
                    loop = dr.loop_equivalent_mm(d, far, ctx.allow_mm or 0.0)
                    if screen is not None and loop > screen + 1e-9: continue
                    if lim["cap_mm"] is not None and loop > lim["cap_mm"] + 1e-9: continue
                    if tighten is not None and loop > tighten + 1e-9: continue
                    if best is not None and loop >= best["loop_mm"] - 1e-9: continue
                    v0 = vs[0]; w, h = v0[2], v0[3]; bx, by = cx + v0[4], cy + v0[5]
                    box = (bx - w / 2.0, by - h / 2.0, bx + w / 2.0, by + h / 2.0)
                    why = _refuse(ctx, entry, box, (cx, cy), far, own_back, near, fans, tht, rules, pcy, side_name,
                                  (px, py), w, h, conv, ref)
                    if why: refused[why] = refused.get(why, 0) + 1; continue
                    best = {"seat": (int(round(cx * MM)), int(round(cy * MM))), "far": far, "rotation": rot,
                            "d_mm": d, "loop_mm": loop}
        r10 += int(round(R_STEP * 10))
    res = {"limit": lim, "rail": how, "far_offered": far_ok, "far_why": far_why, "converter": conv}
    if best is None:
        top = sorted(refused.items(), key=lambda kv: -kv[1])[:3]
        res.update({"seat": None, "status": None,
                    "why": "no free seat %s (%s)" % (("within the %.1f mm screen" % screen) if screen is not None
                                                     else "within %.1f mm" % REACH_MM,
                                                     "; ".join("%s x%d" % kv for kv in top) or "every seat is past the limit")})
        return res
    st, why = dr.judge(entry, best["loop_mm"])
    res.update(best); res.update({"status": st, "why": why})
    return res


def _refuse(ctx, entry, box, centre, far, own_back, near, fans, tht, rules, pcy, side_name, pin, w, h, conv, part_ref):
    """Why a seat is refused, as a short reason, or None when it is free."""
    e = ctx.edge
    if not (e[0] <= box[0] and box[2] <= e[2] and e[1] <= box[1] and box[3] <= e[3]): return "off the board"
    side_back = own_back != far
    for gr, gb in near[side_back]:
        if dr.boxes_meet(box, gb): return "the courtyard of %s" % gr
    for z, zb in rules:
        if dr.boxes_meet(box, zb):
            if not ctx.rule_hit: return "a rule area that forbids parts"
            try:
                if z.HitTestFilledArea(z.GetFirstLayer(), pcbnew.VECTOR2I(int(centre[0] * MM), int(centre[1] * MM)), 0):
                    return "a rule area that forbids parts"
            except Exception: return "a rule area that forbids parts"
    if far:
        ok, why = dr.far_side(entry, ctx.two_sided, box, fans, tht)
        if not ok: return "the far side: " + why.split(": ", 1)[-1][:60]
        return None
    if pcy[0] <= centre[0] <= pcy[2] and pcy[1] <= centre[1] <= pcy[3]: return "inside the part it serves"
    win = None
    if entry.get("class") in ("D", "L") and side_name is not None:
        win = dr.window_box(pcy, pin, h if side_name in ("e", "w") else w, ctx.fan)
    blk = dr.fan_blocks(box, fans, entry, own_window=win, own_converter=conv)
    if blk: return "the escape fan of %s" % blk
    return None


def apply(fp, seat):
    """Put a footprint on the seat the search chose: its side, its orientation, its position."""
    if seat.get("far"): fp.Flip(fp.GetPosition(), False)
    fp.SetOrientationDegrees(seat["rotation"])
    fp.SetPosition(pcbnew.VECTOR2I(seat["seat"][0], seat["seat"][1]))


def netlist_beside(board_path):
    """{reference: {pad: net}} from the netlist beside a board (out/<stem>.net), or {} where there is none."""
    if not board_path: return {}
    p = os.path.join(os.path.dirname(os.path.abspath(board_path)) or ".", "out",
                     os.path.splitext(os.path.basename(board_path))[0] + ".net")
    if not os.path.exists(p): return {}
    try:
        import netlist_sexp
        doc = netlist_sexp.load(p)
    except Exception: return {}
    return {ref: {num: d["net"] for num, d in pins.items()} for ref, pins in doc["pins"].items()}
