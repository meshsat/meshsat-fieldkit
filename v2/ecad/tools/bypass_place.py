#!/usr/bin/env python3
"""Put every declared decoupling capacitor next to the pin it serves (MESHSAT-862 Stage C, 8 Sep 2026).

The audit's finding W2 was that the placement generators shelf-pack the capacitors into a rectangle by reference number
with no proximity rule at all. With the bypass entries of `intent.py` declared, that stopped being an assertion: on D9
every declared capacitor sat 8 to 22 mm from the pin it bypasses, against the 3 mm the gate asks for. A 100 nF at 13 mm
is loop inductance, not decoupling.

This pass moves each declared capacitor that sits past its limit to the best free seat within it, walking outward and
around from the pin. A seat is free when the capacitor's courtyard clears every other footprint's courtyard on that
side, every rule area, the board edge and every escape fan that is not open to it. It runs after the placement
generator and before the escapes, and it reports moved, already close, and stuck.

SINCE 27 SEPTEMBER 2026 THE LIMIT AND THE SEAT ARE DECISION 42's (DECOUPLING.md section 6; MESHSAT-1357): the limit is
the entry's class's, measured from the capacitor's RAIL pad to the pin; the four orientations are tried; a fan is
opened for the own-pin window of a class D or L entry and for a converter's own class R parts; the other side is
offered on a board already assembled on both sides, at its in-plane distance plus the via allowance. The walk is
`bypass_search.search`, which `bypass_slots.reserve` calls too. An entry with no ruled class is refused by name and
counted as stuck: the limit has no default.

Usage: bypass_place.py <board.kicad_pcb> [--limit MM] [--dry]   -> exit 1 when one is stuck (a placement question).
       --limit can only tighten a class's limit (an arm that asks what a smaller screen seats)."""
import sys, os, json, math, pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoupling_rules as _dr
import fan_select, bypass_search

def mm(v): return v / 1e6
def FM(v): return pcbnew.FromMM(v)

def courtyard(f):
    try:
        c = f.GetCourtyard(pcbnew.F_CrtYd if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd); bb = c.BBox()
        if bb.GetWidth() > 0: return bb
    except Exception: pass
    return f.GetBoundingBox(False, False)

def main(a):
    if not a: print(__doc__); return 2
    bp = a[0]; tighten = float(a[a.index("--limit") + 1]) if "--limit" in a else None
    dry = "--dry" in a
    b = pcbnew.LoadBoard(bp)
    ip = os.path.join(os.path.dirname(os.path.abspath(bp)) or ".", "out", os.path.splitext(os.path.basename(bp))[0] + "-intent.json")
    if not os.path.exists(ip): print("bypass_place: no intent file at %s, nothing declared" % ip); return 0
    intent = json.load(open(ip)); entries = intent.get("bypass", [])
    # A CAPACITOR THE GENERATOR SEATED IS NOT MOVED. `bypass_slots` writes the list beside the board when it
    # finds a capacitor already placed from the FIXED table; those seats were measured against the region
    # rectangles, the escape fans and the copper already laid, and this pass checks none of those, so moving
    # one is undoing a decision with a worse test. Board D's seat arm came back `hard 30` three times for
    # exactly that reason.
    sp = os.path.join(os.path.dirname(ip), os.path.splitext(os.path.basename(bp))[0] + "-seated.json")
    seated = set()
    if os.path.exists(sp):
        try: seated = set(json.load(open(sp)).get("seated", []))
        except Exception: seated = set()
    if seated:
        before = len(entries)
        entries = [e for e in entries if e.get("cap") not in seated]
        print("bypass_place: %d capacitor(s) carry a seat the generator chose and are left alone" % (before - len(entries)))
    if not entries: print("bypass_place: 0 bypass entries declared, nothing to place"); return 0
    # A PASS GIVEN A BOARD ITS PARTS ARE NOT ON HAS MEASURED NOTHING (20 September 2026). Boards A and B
    # declared this pass at `mechanical`, which in full.sh is AFTER the outline generator and BEFORE the
    # placement generator, so it ran on a board with NO FOOTPRINTS and reported every entry as "not on the
    # board": `0 moved, 0 already within 3.0 mm, 40 stuck of 40 declared`, which is the same summary line a
    # real run prints. Asked of board A's PLACED board the same pass reads 5 within 3 mm and 35 STUCK at 16.5
    # to 139.6 mm, so the line was not only useless, it was hiding a real finding. The docstring above has
    # said "after the placement generator" since the day it was written.
    on_board = sum(1 for e in entries
                   if b.FindFootprintByReference(e.get("cap") or "") is not None
                   and b.FindFootprintByReference(e.get("part") or "") is not None)
    if not on_board:
        print("bypass_place: INCONCLUSIVE, not one of the %d declared pairs is on this board, which carries %d "
              "footprint(s): this pass runs AFTER the placement generator"
              % (len(entries), len(list(b.GetFootprints()))))
        return 3
    # 9 September 2026: this pass had no idea what an escape fan is, and it ran in no chain until that day, so nothing ever noticed. Wired into
    # every chain it promptly parked capacitors 1 to 3 mm from QFN and ZIF pins and cost those parts their escapes (D10's U7 six of
    # seventeen, C9's U3 twenty-three of fifty-seven). An escaped IC's fan is closed to this pass, the same rule bypass_slots.py uses; since
    # 27 September 2026 both take it from `fan_select` through the shared search, and it is the escape pass's own set.
    # only a rule area that forbids FOOTPRINTS blocks a placement; the board-wide "no tracks on In1" and edge-band areas cover
    # every spot on the board and are about copper, not parts (8 Sep 2026: testing every rule area made all 16 capacitors "stuck")
    ctx = bypass_search.Context(b, bp, _dr.FAN_MM, rule_hit=True)
    nets = bypass_search.netlist_beside(bp)
    print("bypass_place: SMD parts %d front and %d back, so the other side is %s; via allowance %s; %d fanned part(s)"
          % (ctx.smd[0], ctx.smd[1], "offered" if ctx.two_sided else "not offered",
             ("%.1f mm (%s)" % (ctx.allow_mm, ctx.allow_src)) if ctx.allow_mm is not None else ctx.allow_src, len(ctx.fans)))
    print("bypass_place: %s" % ctx.closed_note)
    moved = near = stuck = recorded = 0
    for e in entries:
        f = b.FindFootprintByReference(e["cap"]); p = b.FindFootprintByReference(e["part"])
        if f is None or p is None: print("bypass_place: %s or %s not on the board" % (e["cap"], e["part"])); stuck += 1; continue
        pin = next((q for q in p.Pads() if q.GetNumber() == str(e["pin"])), None)
        if pin is None: print("bypass_place: %s has no pin %s" % (e["part"], e["pin"])); stuck += 1; continue
        if e.get("class") not in _dr.CLASSES:
            print("bypass_place: REFUSED %s -> %s.%s: %s" % (e["cap"], e["part"], e["pin"],
                  (_dr.form_problems(e) or ["no ruled class"])[0].split(": ", 1)[-1])); stuck += 1; continue
        lim = _dr.limit(e); pc = pin.GetPosition()
        # where it sits now, by the gate's own measure: its rail pad to the pin, plus the allowance on the other side
        num, how = bypass_search.rail_pad_number(e, f, pin, nets.get(e["cap"]))
        pads = [q for q in f.Pads() if str(q.GetNumber()).strip() and (num is None or q.GetNumber() == num)]
        d0 = max(mm(math.hypot(q.GetPosition().x - pc.x, q.GetPosition().y - pc.y)) for q in pads) if pads else \
            mm(math.hypot(f.GetPosition().x - pc.x, f.GetPosition().y - pc.y))
        far0 = f.GetLayer() != p.GetLayer()
        loop0 = _dr.loop_equivalent_mm(d0, far0, ctx.allow_mm or 0.0)
        st0, _why0 = _dr.judge(e, loop0)
        # CLOSED AGAIN (D3, T4; 29 September 2026): a capacitor that sits in an opening the escape pass found costing
        # an escape (its own-pin window, or its converter's fan) is re-seated with that opening shut, even to a seat
        # further out; it is never "already within its limit" there
        shut = e["part"] if (e["cap"] in ctx.closed.get("window", ()) and e.get("class") in ("D", "L")) else \
            (ctx.converter_of(e, intent) if (e["cap"] in ctx.closed.get("stage", ()) and e.get("class") == "R") else None)
        in_shut = False
        if shut is not None and not far0:
            fb = dict(ctx.fans).get(shut)
            in_shut = fb is not None and _dr.boxes_meet(fan_select.courtyard_box(f), fb)
        if st0 == "pass" and not in_shut and (tighten is None or loop0 <= tighten + 1e-9): near += 1; continue
        # the search speaks of the part's own side and the other one, so the capacitor is put on the part's side
        # for it and put back if it does not move
        if far0: f.Flip(f.GetPosition(), False)
        res = bypass_search.search(ctx, e, f, p, pin, intent=intent, netlist_pins=nets.get(e["cap"]), tighten=tighten)
        stays = res.get("seat") is None or dry or (not in_shut and res["loop_mm"] >= loop0 - 0.05)
        if stays and far0: f.Flip(f.GetPosition(), False)
        if res.get("seat") is None:
            if st0 == "recorded":
                recorded += 1
                print("bypass_place: %-5s class %s stays %.1f mm from %s.%s: %s" % (e["cap"], e["class"], loop0, e["part"], e["pin"], res.get("why")))
                continue
            print("bypass_place: STUCK %s (class %s) -> %s.%s, %s (it sits %.1f mm away, rail pad to pin%s)%s"
                  % (e["cap"], e["class"], e["part"], e["pin"], res.get("why"), d0, ", the other side" if far0 else "",
                     ("; it sits in the fan of %s, closed again by the escape pass, so the seat it has is refused" % shut) if in_shut else ""))
            stuck += 1; continue
        if res["loop_mm"] >= loop0 - 0.05 and not in_shut:
            # the search found nothing nearer than where it is (a class with no screen): it stays
            recorded += 1
            print("bypass_place: %-5s class %s stays %.1f mm from %s.%s, the nearest free seat" % (e["cap"], e["class"], loop0, e["part"], e["pin"]))
            continue
        if not dry: bypass_search.apply(f, res)
        print("bypass_place: %-5s class %-2s -> %s.%-3s %5.1f mm to %.1f mm%s, turned %d (%s)%s"
              % (e["cap"], e["class"], e["part"], e["pin"], loop0, res["loop_mm"],
                 (" on the other side (%.1f mm in plane)" % res["d_mm"]) if res.get("far") else "", int(res["rotation"]), res["rail"],
                 (", out of the fan of %s, closed again by the escape pass" % shut) if in_shut else ""))
        if res["status"] == "recorded": recorded += 1
        moved += 1
    print("bypass_place: %d moved, %d already within their class's limit, %d stuck of %d declared%s"
          % (moved, near, stuck, len(entries), (" (%d of a class with no distance, recorded)" % recorded) if recorded else ""))
    if moved and not dry: pcbnew.SaveBoard(bp, b)
    return 1 if stuck else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
