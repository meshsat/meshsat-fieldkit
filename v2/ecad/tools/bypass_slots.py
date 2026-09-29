#!/usr/bin/env python3
"""Reserve a slot beside each part for the decoupling capacitors it declares, BEFORE the region packer fills the board.

Owner ruling 9 September 2026 (appendix 32.74, option 3): every placement generator shelf-packed passives into region
rectangles in reference order, so a declared bypass capacitor landed wherever the packer reached. Measured on the
released set: not one capacitor of any board was within the 3 mm the gate asks for, and A22's worst two sat 117 and
121 mm from the pin they serve. `bypass_place.py` moves them afterwards and can only use space the packer left, which
on D9 was nine of sixteen. This runs first: the fixed parts are on the board, nothing else is, so every declared
capacitor takes the spot it needs and the packer works around them.

Call it from a placement generator between the FIXED placement and the region loop:

    import bypass_slots
    reserved = bypass_slots.reserve(board, place, to_case, entries)     # entries = intent's "bypass" list
    ... then skip `reserved` in every region's reference list ...

`place(ref, x, y, rot, back)` is the generator's own placer in case-frame mm; `to_case(vec)` converts a board
VECTOR2I to case-frame mm. A capacitor with no free spot within the limit is left for the packer and reported, so the
gate still sees it as far away rather than the tool pretending it fitted.

SINCE 27 SEPTEMBER 2026 THE SEAT IS DECISION 42's (DECOUPLING.md section 6; MESHSAT-1357). The limit is the entry's
CLASS's and is measured from the capacitor's rail pad, the four orientations are tried, the fan set is the escape
pass's own, a fan is opened for a class D or L entry's own-pin window and for a converter's own class R parts, and a
board already assembled on both sides is offered the other side. All of that is `bypass_search.search`, which
`bypass_place.py` calls too; this file keeps what is its own: it runs BEFORE the packer, it never gives a seated
capacitor a second footprint, and it writes down which capacitors the generator had seated. An entry with no ruled
class is refused by name and left to the packer: the limit has no default."""
import json, math, os, sys, pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoupling_rules as _dr
import fan_select, bypass_search

_DETACHED = []   # KiCad 9: a footprint removed from the board must stay referenced in Python or the next FootprintLoad dies inside the IO plugin

def _courtyard(f):
    try:
        c = f.GetCourtyard(pcbnew.F_CrtYd if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd); bb = c.BBox()
        if bb.GetWidth() > 0: return bb
    except Exception: pass
    return f.GetBoundingBox(False, False)

def _fan_box(f, fan):
    """The courtyard grown by `fan` mm, built from its own edges. BOX2I(origin, size) from a courtyard gave a box of the inflate alone
    (4.4 mm square), so every fan test passed and the protection did nothing: found 9 September 2026 13:35 by printing the box."""
    cb = _courtyard(f); i = int(pcbnew.FromMM(fan))
    return pcbnew.BOX2I(pcbnew.VECTOR2I(cb.GetLeft() - i, cb.GetTop() - i), pcbnew.VECTOR2I(cb.GetWidth() + 2 * i, cb.GetHeight() + 2 * i))

# WHICH PART GETS A FAN is `fan_select.is_fanned` (decision 42, T1): every part the escape pass escapes, and every part
# of eight or more NUMBERED COPPER pads 1.0 mm apart or less. The test that stood here counted every SMD pad, so the
# four paste apertures of a SOIC-8-1EP made a 1.27 mm part fine pitch (DECOUPLING.md 3.2(a)), and it knew nothing of
# the six-pin parts the escape pass escapes (3.2(g)). The 9 September lesson it carried stays in the second term:
# five capacitors 1.9 to 2.6 mm from a 0.8 mm TQFP's pins cost the part beside it six of seventeen escapes (D10, C9).

def reserve(board, place, to_case, entries, limit=None, quiet=False, fan=_dr.FAN_MM, intent=None):
    """Places each declared capacitor beside its pin. Returns the set of references it placed.

    `limit` is no longer a distance every entry shares: None takes each entry's own class's limit, which is the
    ruling. A number can only TIGHTEN it (an arm that asks what a smaller screen would seat), and is said."""
    if not entries: return set()
    # D10 and C9, 9 September 2026: the first floor-plan pass put capacitors 1 mm from QFN and ZIF pins, and the escape pass then had no
    # room for the fans: U7 lost 6 of 17 pads, C9's U3 lost 23 of 57. A fine-pitch part's fan is not free space, so its courtyard grown by
    # `fan` mm is closed to this pass. A capacitor that cannot be served outside every fan is named, not forced.
    path = board.GetFileName() or ""
    ctx = bypass_search.Context(board, path, fan)
    nets = bypass_search.netlist_beside(path)
    if intent is None:
        try:
            ip = os.path.join(os.path.dirname(os.path.abspath(path)) or ".", "out", os.path.splitext(os.path.basename(path))[0] + "-intent.json")
            intent = json.load(open(ip, encoding="utf-8")) if path and os.path.exists(ip) else {}
        except Exception: intent = {}
    done, stuck, report, already = set(), [], [], []
    for e in entries:
        cap, ref, pin = e.get("cap"), e.get("part"), str(e.get("pin"))
        if not cap or cap in done: continue
        bad = _dr.form_problems(e)
        if e.get("class") not in _dr.CLASSES:
            stuck.append((cap, ref, pin, "refused: " + (bad[0].split(": ", 1)[-1] if bad else "no ruled class"))); continue
        p = board.FindFootprintByReference(ref)
        if p is None: stuck.append((cap, ref, pin, "its part is not placed yet")); continue
        pad = next((q for q in p.Pads() if q.GetNumber() == pin), None)
        if pad is None: stuck.append((cap, ref, pin, "no such pin")); continue
        pc = pad.GetPosition(); side = p.GetLayer()
        cx, cy = to_case(pc)
        # A CAPACITOR THAT IS ALREADY ON THE BOARD HAS A SEAT, AND THIS PASS MUST NOT GIVE IT A SECOND
        # (20 September 2026). `place()` CREATES a footprint, so calling it for a capacitor the generator's
        # own FIXED table has already placed adds a second one with the same reference: the net assignment
        # walks `placed` and reaches only the first, and the duplicate's pads land on the board with no net.
        # At HEAD this is invisible because every such capacitor fails the 3 mm search and is removed again,
        # which takes the duplicate with it; an arm that let the search reach further turned it into ELEVEN
        # duplicate references (C4, C11, C63, C64, C106, C107 and the five ISNS filter capacitors) and
        # `netlist_board` blocked the chain at 2,134 of 2,148. A fixed seat is also a DECISION, chosen with
        # its own measurement, so this pass leaves it where it is and says so.
        seated = board.FindFootprintByReference(cap)
        if seated is not None:
            d = math.hypot(seated.GetPosition().x - pc.x, seated.GetPosition().y - pc.y) / 1e6
            done.add(cap); already.append((cap, ref, pin, d)); continue
        fp = place(cap, cx, cy, 0.0, side != pcbnew.F_Cu)   # on the part's own side, then walked out to a free spot
        res = bypass_search.search(ctx, e, fp, p, pad, intent=intent, netlist_pins=nets.get(cap),
                                   tighten=None if limit is None else float(limit))
        if res.get("seat") is None:
            board.Remove(fp); _DETACHED.append(fp); stuck.append((cap, ref, pin, res.get("why") or "no free seat")); continue
        bypass_search.apply(fp, res); done.add(cap)
        report.append((cap, ref, pin, res["d_mm"], e.get("class"), res))
    if not quiet:
        print("bypass_slots: %d of %d declared capacitors reserved a seat within their class's limit, rail pad to pin%s; SMD parts on the "
              "board now %d front and %d back, so the other side is %s; via allowance %s"
              % (len(done), len({e.get("cap") for e in entries}), (" (this arm: no seat past %.1f mm)" % float(limit)) if limit is not None else "",
                 ctx.smd[0], ctx.smd[1], "offered" if ctx.two_sided else "not offered",
                 ("%.1f mm (%s)" % (ctx.allow_mm, ctx.allow_src)) if ctx.allow_mm is not None else ctx.allow_src))
        print("bypass_slots: %s" % ctx.closed_note)
        for cap, ref, pin, d, k, res in report[:6]:
            print("bypass_slots:   %-6s class %-2s beside %s.%-3s rail pad at %.1f mm%s, turned %d (%s)"
                  % (cap, k, ref, pin, d, (", the other side, loop-equivalent %.1f mm" % res["loop_mm"]) if res.get("far") else "",
                     int(res["rotation"]), res["rail"]))
        for cap, ref, pin, why in stuck: print("bypass_slots:   LEFT TO THE PACKER %-6s for %s.%-3s: %s" % (cap, ref, pin, why))
        for cap, ref, pin, d in already:
            print("bypass_slots:   ALREADY SEATED %-6s beside %s.%-3s at %.1f mm, left where the generator put it"
                  % (cap, ref, pin, d))
    # AND THE CAPACITORS THE GENERATOR SEATED ARE WRITTEN DOWN, because the pass that runs later does not
    # know a seat from an accident (20 September 2026). `bypass_place` moves any declared capacitor further
    # than 3 mm from its pin to the first free spot it can find, and a seat chosen outside every region
    # rectangle, escape fan and piece of laid copper is typically 3 to 8 mm out: board D's seat arms came
    # back `hard 33`, then 30, then 30 again, and the collisions are capacitors moved off their seats into
    # spots `bypass_place` does not check the same way. A fixed seat is a decision; this is how the later
    # pass learns which ones they are.
    try:
        if already:
            import os as _os
            d = _os.path.dirname(_os.path.abspath(board.GetFileName() or "")) or "."
            stem = _os.path.splitext(_os.path.basename(board.GetFileName() or "board"))[0]
            outd = d if _os.path.basename(d) == "out" else _os.path.join(d, "out")
            _os.makedirs(outd, exist_ok=True)
            with open(_os.path.join(outd, stem + "-seated.json"), "w", encoding="utf-8") as fh:
                json.dump({"seated": sorted({c for c, _r, _p, _d in already})}, fh, indent=1)
    except Exception as e:
        print("bypass_slots: could not write the seated list (%s)" % e)
    return done
