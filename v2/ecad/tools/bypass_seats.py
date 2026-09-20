#!/usr/bin/env python3
"""Where each declared decoupling capacitor could sit, if the packer were never going to put it there.

20 September 2026, appendix 32.306 and 32.311. `bypass_slots.reserve` walks out from the pin to the 3 mm
limit and refuses any spot touching an escaped part's fan, which is its courtyard grown by 2.2 mm. At a
fine-pitch part the pin sits ON the courtyard edge, so nothing inside 3 mm is ever free: across the set,
**131 declared capacitors and not one reserved slot**, and the packer then puts them wherever its region
has room, which on board A was 13.2 to 44.5 mm from the pins they serve and on board B up to 251.9.

THIS IS A REPORT AND IT MOVES NOTHING. It prints the seat line a generator's FIXED table would carry, for
every declared capacitor further from its pin than the limit, measured on the board the generator makes:

  * outside every other footprint's courtyard on that side,
  * outside every escape fan (the same `_needs_fan` and `_fan_box` the reservation uses),
  * outside every rule area that forbids a part,
  * outside every packer REGION rectangle, read from `out/<stem>-regions.json`, which `regionfit` already
    writes beside the board, because a seat INSIDE a rectangle leaves the shelf packer a hole it cannot pack
    around: board A's A81 arm took 27 such seats and overflowed thirteen regions by up to 24.6 mm,
  * inside the board edge, and clear of every seat this run has already handed out.

Board A's A82 arm is what a set of these seats is worth: hard 0, 461 escapes and 2 pads skipped, every
number the baseline's, with the decoupling distance median 13.2 to 5.7 mm and the total 530 to 293.

Usage: bypass_seats.py <board.kicad_pcb> --board <letter> [--limit 3.0] [--reach 12.0] [--frame OX,OY]
       [--out-dir DIR] [--json]
"""
import os, sys, json, math, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v
import pcbnew
import bypass_slots as _bs

MM = 1e6
COPPER = "copper already laid"
LIMIT = 3.0
REACH = 12.0


def _frame(letter, given):
    """The case frame this board's placement generator uses, read rather than assumed.

    A probe written for board A and pointed at board C prints seats in board A's frame, which are numbers
    for a board nobody is building; board A is (150, 110) and board C (297, 210)."""
    if given:
        a, b = given.split(","); return float(a), float(b), "the --frame argument"
    gen = os.path.join(HERE, "gen_pcb_%s3.py" % letter)
    if os.path.exists(gen):
        m = re.search(r"^OX,\s*OY\s*=\s*(-?[\d.]+),\s*(-?[\d.]+)", open(gen, errors="replace").read(), re.M)
        if m: return float(m.group(1)), float(m.group(2)), os.path.basename(gen)
    return 0.0, 0.0, "no frame found: the seats are in BOARD coordinates"


def _fixed(letter):
    """The references the generator seats by hand, read from its FIXED table by PARSING it.

    A capacitor with a fixed seat is a DECISION with its own measurement behind it: board A's five ISNS
    filter capacitors sit at 1.8 to 2.7 mm by hand and C11, C12 and C63 sit where the PA stage's input
    needs them. Offering those a seat would be advice to undo a choice, so they are named and skipped."""
    import ast
    gen = os.path.join(HERE, "gen_pcb_%s3.py" % letter)
    if not os.path.exists(gen): return set()
    try:
        tree = ast.parse(open(gen, errors="replace").read())
    except SyntaxError:
        return set()
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "FIXED" for t in node.targets):
            if isinstance(node.value, ast.Dict):
                for k in node.value.keys:
                    if isinstance(k, ast.Constant) and isinstance(k.value, str): out.add(k.value)
    return out


def _cbox(fp):
    bb = fp.GetCourtyard(pcbnew.F_CrtYd if fp.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd).BBox()
    if bb.GetWidth() <= 0: bb = fp.GetBoundingBox(False, False)
    return bb.GetLeft() / MM, bb.GetTop() / MM, bb.GetRight() / MM, bb.GetBottom() / MM


def seats(board_path, letter, limit=LIMIT, reach=REACH, frame=None):
    b = pcbnew.LoadBoard(board_path)
    stem = os.path.splitext(os.path.basename(board_path))[0]
    d = os.path.dirname(os.path.abspath(board_path))
    # The board may BE in out/ (the placed snapshot) or beside it (the project board); the intent and the
    # region table live in out/ either way. A tool that always appends "out" looks in out/out for half the
    # boards it is given and then reports zero declared capacitors, which is a pass on a denominator of zero.
    outd = d if os.path.basename(d) == "out" else os.path.join(d, "out")
    base = stem[:-len("-placed")] if stem.endswith("-placed") else stem
    ip = os.path.join(outd, base + "-intent.json")
    entries = json.load(open(ip)).get("bypass", []) if os.path.exists(ip) else []
    rp = os.path.join(outd, base + "-regions.json")
    rects = []
    if os.path.exists(rp):
        rects = [(r["name"], r["rect"]) for r in json.load(open(rp)).get("regions", [])]
    OX, OY, how = _frame(letter, frame)
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    moving = {e.get("cap") for e in entries}
    boxes = [(f.GetReference(), *_cbox(f), f.GetLayer()) for f in b.GetFootprints()]
    fans = []
    for g in b.GetFootprints():
        if _bs._needs_fan(g):
            fb = _bs._fan_box(g, 2.2)
            fans.append((fb.GetLeft() / MM, fb.GetTop() / MM, fb.GetRight() / MM, fb.GetBottom() / MM))
    ras = []
    for z in b.Zones():
        if not z.GetIsRuleArea(): continue
        if not (z.GetDoNotAllowPads() or (hasattr(z, "GetDoNotAllowFootprints") and z.GetDoNotAllowFootprints())): continue
        bb = z.GetBoundingBox()
        ras.append((z.GetZoneName() or "rule area", bb.GetLeft() / MM, bb.GetTop() / MM, bb.GetRight() / MM, bb.GetBottom() / MM))
    # AND THE COPPER ALREADY ON THE BOARD (20 September 2026). A placed board is not empty: the generator
    # lays locked power bands and escape stubs before anything is packed, and a seat that clears every
    # courtyard can still sit on one. Board P's first seat arm came back `hard 2`, both of them a
    # capacitor's GND pad against a locked track (/CELL4 and /FUSED), which is this map's blind spot rather
    # than the board's fault. Each track is taken with its own box and the board's own clearance.
    clr = 0.2
    try:
        pro = os.path.splitext(board_path)[0] + ".kicad_pro"
        if os.path.exists(pro):
            clr = float(json.load(open(pro)).get("board", {}).get("design_settings", {}).get("rules", {})
                        .get("min_clearance", clr)) or clr
    except Exception:
        pass
    tracks = []
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA": continue
        bb = t.GetBoundingBox()
        tracks.append((t.GetLayer(), bb.GetLeft() / MM - clr, bb.GetTop() / MM - clr,
                       bb.GetRight() / MM + clr, bb.GetBottom() / MM + clr))
    edge = b.GetBoardEdgesBoundingBox()
    EL, ET, ER, EB = edge.GetLeft() / MM, edge.GetTop() / MM, edge.GetRight() / MM, edge.GetBottom() / MM
    taken = []
    def case(x, y): return (x - OX, OY - y)
    def refuse(x, y, w, h, side):
        l, t, r_, bo = x - w / 2, y - h / 2, x + w / 2, y + h / 2
        if l < EL + 0.5 or r_ > ER - 0.5 or t < ET + 0.5 or bo > EB - 0.5: return "the board edge"
        cl, cb = case(l, bo); cr, ct = case(r_, t)
        for name, (rx0, ry0, rx1, ry1) in rects:
            if min(rx0, rx1) < cr and max(rx0, rx1) > cl and min(ry0, ry1) < ct and max(ry0, ry1) > cb:
                return "region " + name
        for (fl, ft, fr, fb) in fans:
            if fl < r_ and fr > l and ft < bo and fb > t: return "an escape fan"
        for name, L, T, R, B in ras:
            if L < r_ and R > l and T < bo and B > t: return name
        for ref, L, T, R, B, ly in boxes:
            if ly != side or ref in moving: continue
            if L < r_ and R > l and T < bo and B > t: return ref
        for ly, L, T, R, B in tracks:
            if ly != side: continue
            if L < r_ and R > l and T < bo and B > t: return COPPER
        for ref, L, T, R, B in taken:
            if L < r_ and R > l and T < bo and B > t: return ref
        return None
    fixed = _fixed(letter)
    near, found, none, held = [], [], [], []
    for e in entries:
        cap, part, pin = e.get("cap"), e.get("part"), str(e.get("pin"))
        if cap not in fps or part not in fps: none.append((cap, part, pin, 0.0, "not on this board")); continue
        p = next((q for q in fps[part].Pads() if q.GetNumber() == pin), None)
        if p is None: none.append((cap, part, pin, 0.0, "no pin %s on %s" % (pin, part))); continue
        px, py = p.GetPosition().x / MM, p.GetPosition().y / MM
        was = math.hypot(fps[cap].GetPosition().x / MM - px, fps[cap].GetPosition().y / MM - py)
        if was <= limit: near.append((cap, part, pin, was)); continue
        if cap in fixed: held.append((cap, part, pin, was)); continue
        L, T, R, B = _cbox(fps[cap]); w, h = R - L + 0.50, B - T + 0.50
        side = fps[cap].GetLayer()
        got = None
        for dd in [x / 10.0 for x in range(int(limit * 10) // 3, int(reach * 10) + 1)]:
            for ang in range(0, 360, 5):
                x, y = px + dd * math.cos(math.radians(ang)), py + dd * math.sin(math.radians(ang))
                if refuse(x, y, w, h, side) is None: got = (dd, x, y); break
            if got: break
        if got is None:
            none.append((cap, part, pin, was, "no seat within %.1f mm" % reach)); continue
        dd, x, y = got
        taken.append((cap, x - w / 2, y - h / 2, x + w / 2, y + h / 2))
        found.append((cap, part, pin, dd, case(x, y), was))
    return {"near": near, "found": found, "none": none, "held": held, "frame": (OX, OY, how), "intent": ip,
            "regions": len(rects), "fans": len(fans), "tracks": len(tracks), "declared": len(entries), "limit": limit, "reach": reach}


def main(argv):
    if not argv: print(__doc__); return 2
    bp = argv[0]
    letter = _v.opt(argv, "--board", "")
    limit = float(_v.opt(argv, "--limit", str(LIMIT)))
    reach = float(_v.opt(argv, "--reach", str(REACH)))
    r = seats(bp, letter, limit, reach, _v.opt(argv, "--frame", ""))
    OX, OY, how = r["frame"]
    if not r["declared"]:
        # A declaration that is not there is not a board with nothing to say: say which file was wanted.
        print("bypass_seats: no bypass entries at %s" % r["intent"])
        return _v.write("bypass_seats", _v.INCONCLUSIVE, counts={"declared": 0}, denominator=0,
                        advisory=True, out_dir=_v.opt(argv, "--out-dir", None),
                        missing_input="the intent file beside the board (%s)" % r["intent"],
                        note="no declared decoupling capacitor to seat, which is a missing input and not a pass")
    print("bypass_seats: %d declared, %d already within %.1f mm; the frame is (%.1f, %.1f) from %s, "
          "%d region rectangle(s), %d escape fan(s) and %d piece(s) of laid copper in the map"
          % (r["declared"], len(r["near"]), limit, OX, OY, how, r["regions"], r["fans"], r["tracks"]))
    if "--json" in argv:
        print(json.dumps(r, indent=1, default=list))
    else:
        for cap, part, pin, dd, (cx, cy), was in sorted(r["found"], key=lambda t: -t[5]):
            print('         "%s": (%.2f, %.2f, 0),   # %.2f mm from %s pin %s, where it sits %.1f mm away today'
                  % (cap, cx, cy, dd, part, pin, was))
        for cap, part, pin, was, why in sorted(r["none"], key=lambda t: -t[3]):
            print("bypass_seats:   %-6s for %s.%-4s %s (today %.1f mm)" % (cap, part, pin, why, was))
    for cap, part, pin, was in sorted(r.get("held", []), key=lambda t: -t[3]):
        print("bypass_seats:   %-6s for %s.%-4s carries a fixed seat at %.1f mm, which is a decision" % (cap, part, pin, was))
    print("bypass_seats: %d seat(s) offered, %d capacitor(s) with none and %d held by a fixed seat"
          % (len(r["found"]), len(r["none"]), len(r.get("held", []))))
    return _v.write("bypass_seats", _v.PASS, counts={"declared": r["declared"], "near": len(r["near"]), "seatable": len(r["found"]),
                            "no_seat": len(r["none"]), "fixed": len(r.get("held", []))},
                    denominator=r["declared"], advisory=True, out_dir=_v.opt(argv, "--out-dir", None),
                    evidence=['"%s": (%.2f, %.2f, 0)  # %.2f mm from %s pin %s, today %.1f'
                              % (c, cx, cy, dd, p_, pin, was)
                              for c, p_, pin, dd, (cx, cy), was in sorted(r["found"], key=lambda t: -t[5])][:20],
                    note="where each declared decoupling capacitor could sit, outside every courtyard, escape "
                         "fan, part-forbidding rule area, packer region rectangle and the board edge; a "
                         "REPORT, because a seat is a generator's decision and not a tool's")


if __name__ == "__main__":
    sys.exit(_v.guard("bypass_seats", main, sys.argv[1:]))
