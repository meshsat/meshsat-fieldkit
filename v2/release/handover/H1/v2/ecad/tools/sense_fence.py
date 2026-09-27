#!/usr/bin/env python3
"""A FENCE THE ROUTER OBEYS AROUND A SENSITIVE NODE'S OWN COPPER (rule ANA-001, 21 September 2026).

E36 is board E's best router board, hard 0 and six open, and its round-1 board FAILS ANA-001 by sixty-seven
micrometres: `TRK_CSP` runs 0.433 mm from `TRK_SW1` over 7.68 mm, all of it outside the courtyard of the part
that carries both. Board E pins ALL SIX of its declared switching nets and the sense pair at a half-millimetre
floor, which is E23's configuration, and E23 read PASS 3 of 3. So this is neither the declaration nor the
pre-lay: **the pre-lay locks the copper IT lays, and the router then added unlocked copper to a net that is
already pinned**, which is the caveat E21 wrote down and the first arm where it bit.

WHAT REACHES THE ROUTER, measured rather than assumed:

  a DSN class-pair clearance   IGNORED by Freerouting 1.9.0 (measured on E17, 18 September)
  a SENSE class clearance      REFUSED BY THIS BOARD'S OWN PINS: WATER_SENSE at U10 pad 38 is 0.200 mm from
                               pad 37, TRK_CSN at U5 pad 2 is 0.250 from pad 1, TRK_CSP at U5 pad 3 is 0.250
                               from pad 4, so 0.50 mm refuses the escape at three pins and the route dies at
                               the source (board A's answer at U16 pin 16, at board E's pins)
  a KiCad custom rule          catches after the fact, steers nothing
  a WIRE KEEP-OUT              OBEYED: a rule area that forbids tracks leaves KiCad's DSN export as
                               `(wire_keepout ...)`, and `route_one.sh` drops those only on POWER layers

So the instrument is a keep-out, and it is drawn AFTER the pre-lay, never by the generator: a generator-drawn
fence is an obstacle to the pre-lay itself, which is the copper the fence exists to protect.

THE SHAPE: the sensitive net's own copper grown by the clearance its declaration asks for, MINUS every piece
of copper that is already there grown by the board's own clearance. Subtracting what exists matters twice: a
rule area that forbids tracks and sits on a track is an `items_not_allowed` violation, which is in the hard
set; and where copper already stands inside the band, the distance is already short and a fence there would be
a claim about a violation it cannot fix. The router is stopped from making NEW copper close; what is close
already is `sensitive_nodes`' to report.

Usage: sense_fence.py <board.kicad_pcb> --board <letter> [--layers F.Cu,B.Cu] [--net NET:MM,...] [--apply]
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict as _v
import kicad_compat as _kc

# KiCad 9's python drops the POLYGON_MODE argument every one of these took in 7 and 8: `BooleanSubtract(b)`,
# `Simplify()` and `Fracture()` are the whole signature, and `pcbnew.SHAPE_POLY_SET.PM_FAST` does not exist.
# The third API pin of the day, after LSET(layer) and PAD.GetEffectiveShape wanting a layer.


def _poly():
    import pcbnew
    return pcbnew.SHAPE_POLY_SET()


def _add_disc(poly, x, y, r, n=12):
    poly.NewOutline()
    for k in range(n):
        a = 2 * math.pi * k / n
        poly.Append(int(x + r * math.cos(a)), int(y + r * math.sin(a)))


def _add_capsule(poly, x1, y1, x2, y2, r):
    """A segment grown by r, as a rectangle plus a disc at each end (twelve-sided, which is inside the circle
    by less than four percent of r and therefore never claims more room than the real clearance)."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1:
        _add_disc(poly, x1, y1, r); return
    ux, uy = dx / L, dy / L
    nx, ny = -uy * r, ux * r
    poly.NewOutline()
    for px, py in ((x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)):
        poly.Append(int(px), int(py))
    _add_disc(poly, x1, y1, r); _add_disc(poly, x2, y2, r)


def build(b, nets, grow_nm, layer, keepout_nm):
    """The fence on one layer: `nets`' copper grown by `keepout_nm`, minus everything else grown by `grow_nm`."""
    import pcbnew
    want = _poly(); other = _poly(); n_src = 0
    for t in b.GetTracks():
        nm = (t.GetNetname() or "").lstrip("/")
        is_via = t.GetClass() == "PCB_VIA"
        if not is_via and t.GetLayer() != layer: continue
        s, e = t.GetStart(), t.GetEnd()
        hw = (_kc.via_width(t) if is_via else t.GetWidth()) / 2   # KiCad 9's PCB_VIA.GetWidth() wants a layer
        if nm in nets and not is_via:
            _add_capsule(want, s.x, s.y, e.x, e.y, hw + keepout_nm); n_src += 1
        # THE FENCED NET'S OWN COPPER IS SUBTRACTED TOO, which the first version forgot: a rule area that
        # forbids tracks and sits on the very track it protects is 84 `items_not_allowed` on board E, and that
        # type is in the hard set. The fence is an ANNULUS, from the copper's own clearance out to the
        # clearance the declaration asks for.
        if is_via: _add_disc(other, s.x, s.y, hw + grow_nm)
        else: _add_capsule(other, s.x, s.y, e.x, e.y, hw + grow_nm)
    for f in b.GetFootprints():
        for p in f.Pads():
            if not p.IsOnLayer(layer): continue
            bb = p.GetBoundingBox()
            other.NewOutline()
            for px, py in ((bb.GetLeft() - grow_nm, bb.GetTop() - grow_nm), (bb.GetRight() + grow_nm, bb.GetTop() - grow_nm),
                           (bb.GetRight() + grow_nm, bb.GetBottom() + grow_nm), (bb.GetLeft() - grow_nm, bb.GetBottom() + grow_nm)):
                other.Append(int(px), int(py))
    if n_src == 0: return None, 0
    want.Simplify(); other.Simplify()
    want.BooleanSubtract(other)
    want.Fracture()            # holes become cut lines: a KiCad rule area is one outline per zone
    return want, n_src


def main(argv):
    import pcbnew
    # `verdict.opt`, never argv.index: a flag given no value is answered rather than raised, and the next flag
    # is never taken as a value (18 September 2026, assembly_set's IndexError read as a finding about seven
    # boards). The suite's ratchet on unguarded flag reads named this file the moment it was written.
    path = argv[0]
    letter = _v.opt(argv, "--board", None)
    layers = (_v.opt(argv, "--layers", "F.Cu,B.Cu") or "F.Cu,B.Cu").split(",")
    apply_ = "--apply" in argv
    _netspec = _v.opt(argv, "--net", None)
    if _netspec:             # NET:KEEP_MM, for a fixture and for asking the question of one net by hand
        nodes = []
        for spec in _netspec.split(","):
            _n, _k = spec.split(":"); nodes.append({"net": _n, "keep_mm": float(_k)})
    else:
        import yaml
        decl = yaml.safe_load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pcb_sensitive.yaml"),
                                   encoding="utf-8"))["boards"].get(letter) or {}
        nodes = [n for n in (decl.get("nodes") or []) if isinstance(n, dict) and n.get("keep_mm")]
    if not nodes:
        print("sense_fence: board %s declares no sensitive node with a clearance, nothing to fence" % letter)
        return 0
    b = pcbnew.LoadBoard(path)
    # a hair MORE than the board's own minimum, so the annulus starts outside anything KiCad would measure
    clr = max(b.GetDesignSettings().m_MinClearance, pcbnew.FromMM(0.13)) + pcbnew.FromMM(0.05)
    made = 0
    for nd in nodes:
        net, keep = nd["net"].lstrip("/"), float(nd["keep_mm"])
        for lname in layers:
            layer = b.GetLayerID(lname)
            if layer < 0: continue
            poly, n_src = build(b, {net}, clr, layer, pcbnew.FromMM(keep))
            if poly is None or poly.OutlineCount() == 0:
                print("sense_fence: %-12s %-6s no copper of this net on this layer" % (net, lname)); continue
            area = poly.Area() / 1e12
            print("sense_fence: %-12s %-6s %d source segment(s) -> %d outline(s), %.2f mm2 of fence at %.2f mm"
                  % (net, lname, n_src, poly.OutlineCount(), area, keep))
            if not apply_: continue
            for i in range(poly.OutlineCount()):
                o = poly.Outline(i)
                if abs(o.Area()) < 1e8: continue        # under 0.1 mm2: a sliver the router cannot use anyway
                z = pcbnew.ZONE(b); z.SetIsRuleArea(True)
                z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
                try: z.SetDoNotAllowZoneFills(False)
                except Exception: pass
                z.SetLayer(layer); z.SetZoneName("ANA-001 fence %s" % net)
                zo = z.Outline(); zo.NewOutline()
                for k in range(o.PointCount()):
                    pt = o.CPoint(k); zo.Append(pt.x, pt.y)
                b.Add(z); made += 1
    if apply_:
        pcbnew.SaveBoard(path, b)
        print("sense_fence: %d rule area(s) added and the board saved" % made)
    return 0


if __name__ == "__main__":
    sys.exit(_v.guard("sense_fence", main, sys.argv[1:], rules=["ANA-001"]))
