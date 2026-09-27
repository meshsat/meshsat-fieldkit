#!/usr/bin/env python3
"""The boards tests/test_decoupling_board.py asks its questions of, built with KiCad's own pcbnew.

Usage: decoupling_fixture.py build <scenario> <dir>     writes <dir>/fix.kicad_pcb, <dir>/out/fix-intent.json and,
                                                        where the scenario has one, <dir>/bypass-allow.txt
       decoupling_fixture.py read <board.kicad_pcb>     prints, as JSON, where every footprint and pad now is
       decoupling_fixture.py reserve <scenario> <dir>   builds the board with its parts and NO capacitor, runs
                                                        bypass_slots.reserve with a placer of its own and prints
                                                        what it seated

Everything is written into the directory it is given and nowhere else; a fixture never touches this tree's
evidence. Coordinates are millimetres. The parts:
    fine      twenty pads in two rows of ten at 0.5 mm pitch: an IC the escape pass escapes, so it is fanned
    small     five pads at 0.95 mm, a SOT-23-5 in all but name: neither escaped nor fanned
    cap       two pads 1.0 mm apart, pad 1 the rail pad
    conv      six pads at 0.65 mm, a converter the escape pass escapes"""
import os, sys, json

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import pcbnew

MM = pcbnew.FromMM


def board(layers=4, w=60.0, h=40.0):
    b = pcbnew.BOARD(); b.SetCopperLayerCount(layers)
    for (x1, y1, x2, y2) in ((0, 0, w, 0), (w, 0, w, h), (w, h, 0, h), (0, h, 0, 0)):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1))); s.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
        s.SetWidth(MM(0.1)); b.Add(s)
    return b


def nets(b, names):
    for n in names: b.Add(pcbnew.NETINFO_ITEM(b, n))
    b.BuildListOfNets()
    return {n: b.FindNet(n).GetNetCode() for n in names}


def part(b, ref, x, y, pads, code, value="", back=False, size=0.3, fpid=None, tht=False):
    """pads: [(number, dx, dy, net or None)]"""
    fp = pcbnew.FOOTPRINT(b); fp.SetReference(ref); fp.SetValue(value)
    if fpid: fp.SetFPIDAsString(fpid)
    fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    made = []
    for num, dx, dy, net in pads:
        p = pcbnew.PAD(fp); p.SetNumber(str(num))
        if tht:
            p.SetAttribute(pcbnew.PAD_ATTRIB_PTH); p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            p.SetSize(pcbnew.VECTOR2I(MM(1.6), MM(1.6))); p.SetDrillSize(pcbnew.VECTOR2I(MM(0.9), MM(0.9)))
            p.SetLayerSet(pcbnew.PAD.PTHMask())
        else:
            p.SetAttribute(pcbnew.PAD_ATTRIB_SMD); p.SetShape(pcbnew.PAD_SHAPE_RECT)
            p.SetSize(pcbnew.VECTOR2I(MM(size), MM(size))); p.SetLayerSet(pcbnew.PAD.SMDMask())
        p.SetPosition(pcbnew.VECTOR2I(MM(x + dx), MM(y + dy)))
        fp.Add(p); made.append((p, net))
    b.Add(fp)
    for p, net in made:
        if net: p.SetNetCode(code[net])
    if back: fp.Flip(fp.GetPosition(), False)
    return fp


def via(b, x, y, net, code, d=0.6, drill=0.3):
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetDrill(MM(drill)); v.SetWidth(MM(d))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNetCode(code[net]); b.Add(v)
    return v


FINE = [(i + 1, i * 0.5 - 2.25, -1.0, None) for i in range(10)] + [(i + 11, i * 0.5 - 2.25, 1.0, None) for i in range(10)]
SMALL = [(1, -0.95, 1.1, None), (2, 0.0, 1.1, None), (3, 0.95, 1.1, None), (4, 0.95, -1.1, None), (5, -0.95, -1.1, None)]
CONV = [(1, -0.65, 1.0, None), (2, 0.0, 1.0, None), (3, 0.65, 1.0, None), (4, 0.65, -1.0, None), (5, 0.0, -1.0, None), (6, -0.65, -1.0, None)]
CAP = lambda rail, other="GND": [(1, -0.5, 0.0, rail), (2, 0.5, 0.0, other)]


def with_nets(pads, mapping, default=None):
    return [(n, dx, dy, mapping.get(n, default if default is not None else ("N%d" % n))) for n, dx, dy, _ in pads]


def entry(cls, part_ref="U1", pin="3", net="+3V3", cap="C1", **kw):
    e = {"cap": cap, "part": part_ref, "pin": str(pin), "net": net}
    if cls is not None: e.update({"class": cls, "basis": "the fixture's maker, p.1: 'as close as possible to the pin'"})
    e.update(kw); return e


def build(scenario, d):
    s = scenario; allow = None; layers = 4
    names = ["+3V3", "GND", "+5V", "SW"] + ["N%d" % i for i in range(1, 21)]
    if s.startswith("g_farside") or s.startswith("p_farside"): layers = 4
    b = board(layers); code = nets(b, names)
    ents = []
    if s in ("g_unclassed", "g_near", "g_far_blanket", "g_far_named", "g_maker_cap", "g_value_bulk", "g_value_pin",
             "g_recorded"):
        part(b, "U1", 10.0, 10.0, with_nets(SMALL, {3: "+3V3", 2: "GND"}), code, "the part")
        pin = (10.95, 11.1)
        dist = {"g_unclassed": 1.5, "g_near": 1.5, "g_far_blanket": 10.0, "g_far_named": 10.0, "g_maker_cap": 10.0,
                "g_value_bulk": 5.0, "g_value_pin": 5.0, "g_recorded": 11.0}[s]
        val = {"g_value_bulk": "10u", "g_value_pin": "10u 25V 1210"}.get(s, "100n")
        # the rail pad (pad 1, at -0.5 of the centre) sits `dist` east of the pin
        part(b, "C1", pin[0] + dist + 0.5, pin[1], CAP("+3V3"), code, val, size=0.6)
        cls = {"g_unclassed": None, "g_maker_cap": "L", "g_value_bulk": "B2", "g_recorded": "A"}.get(s, "D")
        kw = {"value_floor": "2.2u", "esr_max": "not stated by the maker", "maker_mm": 5.0} if s == "g_maker_cap" else {}
        ents = [entry(cls, **kw)]
        if s == "g_far_blanket":
            allow = ("The sixteen declared capacitors sit 8.2 to 32.1 mm from their pins because the placement generator "
                     "shelf-packs passives by reference number; moving them is a floor-plan change and is an owner decision.\n")
        if s in ("g_far_named", "g_maker_cap"):
            allow = "# one capacitor per line\nC1: the own side is full at U1, the nearest seat outside it is 10.0 mm, about 3.9 nH more\n"
    elif s in ("g_farside_onesided", "g_farside_ok", "g_farside_past", "g_farside_fan", "g_farside_same_side"):
        part(b, "U1", 10.0, 10.0, with_nets(SMALL, {3: "+3V3", 2: "GND"}), code, "the part")
        pin = (10.95, 11.1)
        if s != "g_farside_onesided":
            part(b, "R9", 40.0, 30.0, CAP("N1", "N2"), code, "10k", back=True, size=0.6)      # the board is assembled on both sides
        if s == "g_farside_fan":
            part(b, "U7", 14.5, 11.1, with_nets(FINE, {}), code, "a fanned part beside it")
        ip = {"g_farside_past": 2.0}.get(s, 0.3)
        # flipped about its own centre, pad 1 lands at +0.5 of the centre (x mirrors)
        part(b, "C1", pin[0] + ip - 0.5, pin[1], CAP("+3V3"), code, "100n", back=True, size=0.6)
        ents = [entry("D", **({"same_side": True} if s == "g_farside_same_side" else {}))]
        if s == "g_farside_fan": allow = "C1: there is no other seat, and this line must not be able to allow it\n"
    elif s in ("g_shared_via", "g_own_via", "g_no_via"):
        part(b, "U1", 10.0, 10.0, with_nets(SMALL, {3: "+3V3", 2: "GND"}), code, "the part")
        pin = (10.95, 11.1)
        part(b, "C1", pin[0] + 1.5 + 0.5, pin[1], CAP("+3V3"), code, "100n", size=0.6)          # ground pad at pin x + 2.5
        gx, gy = pin[0] + 2.5, pin[1]
        if s == "g_shared_via":
            via(b, gx, gy + 0.7, "GND", code)
            part(b, "C2", gx + 0.5, gy + 1.4, CAP("GND", "N3"), code, "100n", size=0.6)       # its pad 1 lands on that via
        elif s == "g_own_via":
            via(b, gx, gy + 0.7, "GND", code)
        ents = [entry("D")]
    elif s in ("p_window", "p_bulk", "p_unclassed", "p_class_a"):
        part(b, "U1", 20.0, 20.0, with_nets(FINE, {3: "+3V3"}), code, "a fine-pitch part", fpid="Package_DFN_QFN:fixture-20")
        part(b, "C1", 45.0, 30.0, CAP("+3V3"), code, "100n", size=0.6)
        ents = [entry({"p_window": "D", "p_bulk": "B2", "p_unclassed": None, "p_class_a": "A"}[s])]
    elif s in ("p_converter", "p_converter_unnamed"):
        part(b, "U2", 20.0, 20.0, with_nets(CONV, {3: "+5V", 2: "GND", 6: "SW"}), code, "a converter", fpid="Package_TO_SOT_SMD:TSOT-23-6")
        part(b, "L1", 26.0, 17.0, [(1, -1.2, 0.0, "SW"), (2, 1.2, 0.0, "+3V3")], code, "4.7uH", size=1.0)
        part(b, "C1", 45.0, 30.0, CAP("+5V"), code, "10u", size=0.6)
        ents = [entry("R", "U2", 3, "+5V", same_side=True)]
        if s == "p_converter_unnamed":
            # a class R capacitor declared against ANOTHER part (no converter named, none in a power loop): no fan is open to it
            ents = [entry("R", "L1", 1, "SW", same_side=True)]
            b.FindFootprintByReference("C1").Pads()[0].SetNetCode(code["SW"])
    elif s in ("p_farside", "p_farside_onesided"):
        part(b, "U1", 20.0, 20.0, with_nets(SMALL, {3: "+3V3", 2: "GND"}), code, "a small part")
        pin = (20.95, 21.1)
        # the own side is full: parts all round the pin, out past the screen
        k = 0
        for bx in (16.0, 18.5, 21.0, 23.5, 26.0):
            for by in (15.0, 17.2, 22.9, 25.1, 27.3):
                k += 1
                part(b, "R%d" % k, bx, by, [(1, -0.9, 0.0, None), (2, 0.9, 0.0, None)], code, "10k", size=1.6)
        for bx, by in ((16.0, 20.0), (23.9, 20.0), (26.4, 20.0)):
            k += 1; part(b, "R%d" % k, bx, by, [(1, -0.9, 0.0, None), (2, 0.9, 0.0, None)], code, "10k", size=1.6)
        if s == "p_farside":
            part(b, "R99", 50.0, 35.0, CAP("N1", "N2"), code, "10k", back=True, size=0.6)
        part(b, "C1", 45.0, 8.0, CAP("+3V3"), code, "100n", size=0.6)
        ents = [entry("D")]
    elif s in ("e_window", "e_undeclared"):
        # a fanned part whose pins 1 to 10 each carry a net, and a capacitor right in front of pin 3, in its window
        part(b, "U1", 20.0, 20.0, with_nets(FINE, {3: "+3V3"}), code, "a fine-pitch part", fpid="Package_DFN_QFN:fixture-20")
        part(b, "C1", 18.75, 20.0 - 1.15 - 0.45, CAP("+3V3"), code, "100n", size=0.6)
        ents = [entry("D")] if s == "e_window" else []
    else:
        raise SystemExit("decoupling_fixture: no scenario %r" % s)
    os.makedirs(os.path.join(d, "out"), exist_ok=True)
    path = os.path.join(d, "fix.kicad_pcb"); b.Save(path)
    json.dump({"bypass": ents, "rails": {}, "nodes": {}, "pair_classes": {}}, open(os.path.join(d, "out", "fix-intent.json"), "w"))
    if allow is not None: open(os.path.join(d, "bypass-allow.txt"), "w").write(allow)
    print(json.dumps({"board": path, "entries": ents}))
    return path


def read(path):
    b = pcbnew.LoadBoard(path); out = {}
    for f in b.GetFootprints():
        bb = f.GetBoundingBox(False, False)
        out[f.GetReference()] = {"x": pcbnew.ToMM(f.GetPosition().x), "y": pcbnew.ToMM(f.GetPosition().y),
                                 "back": f.GetLayer() != pcbnew.F_Cu, "rot": f.GetOrientationDegrees(),
                                 "box": [pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom())],
                                 "pads": {p.GetNumber(): {"x": pcbnew.ToMM(p.GetPosition().x), "y": pcbnew.ToMM(p.GetPosition().y),
                                                          "net": p.GetNetname()} for p in f.Pads()}}
    out["_vias"] = [[pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y), t.GetNetname()] for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
    out["_tracks"] = sum(1 for t in b.GetTracks() if t.GetClass() == "PCB_TRACK")
    print(json.dumps(out))


def reserve(scenario, d):
    """The reservation on a board that holds the part and not yet the capacitor, as a placement generator calls it."""
    import bypass_slots
    names = ["+3V3", "GND"] + ["N%d" % i for i in range(1, 21)]
    b = board(4); code = nets(b, names)
    part(b, "U1", 20.0, 20.0, with_nets(FINE, {3: "+3V3"}), code, "a fine-pitch part", fpid="Package_DFN_QFN:fixture-20")
    cls = {"r_window": "D", "r_bulk": "B2", "r_unclassed": None}[scenario]
    ents = [entry(cls)]
    def place(ref, x, y, rot, back):
        return part(b, ref, x, y, [(1, -0.5, 0.0, None), (2, 0.5, 0.0, None)], code, "100n", back=back, size=0.6)
    done = bypass_slots.reserve(b, place, lambda v: (pcbnew.ToMM(v.x), pcbnew.ToMM(v.y)), ents)
    c = b.FindFootprintByReference("C1"); pin = next(p for p in b.FindFootprintByReference("U1").Pads() if p.GetNumber() == "3")
    res = {"done": sorted(done), "on_board": c is not None}
    if c is not None:
        res.update({"x": pcbnew.ToMM(c.GetPosition().x), "y": pcbnew.ToMM(c.GetPosition().y), "rot": c.GetOrientationDegrees(),
                    "pads": {p.GetNumber(): [pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)] for p in c.Pads()},
                    "pin": [pcbnew.ToMM(pin.GetPosition().x), pcbnew.ToMM(pin.GetPosition().y)]})
    print("RESERVED " + json.dumps(res))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "build": build(a[1], a[2])
    elif a[0] == "read": read(a[1])
    elif a[0] == "reserve": reserve(a[1], a[2])
    else: raise SystemExit(__doc__)
