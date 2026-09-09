#!/usr/bin/env python3
"""Cross-board contract check for the Rev A set (A20, B13, C5, D6, E4, plus the E5 block, appendix 32.26 and 32.35).

Reads the KiCad netlists in <board>/out/<board>.net and verifies the connections that no single board's gate can see:
the panel ribbon map, the transmit inhibit chain, the three 5 V rails, the dock signal and power contacts, the
shutdown pair on the A to B ribbon, the 2x9 ribbon map itself, the mezzanine harness map and the I2S and wall-port pairs (32.35). Prints one line per contract and exits non-zero on any FAIL.
Usage: check_contracts.py [ecad dir]   (default: the directory above this script)"""
import sys, os, re, collections

ECAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NETS = {"A": "pcb-a-power", "B": "pcb-b-compute", "C": "pcb-c-display", "D": "pcb-d-aprs", "E": "pcb-e1-dock"}

def load(stem):
    """{net name: {(ref, pin)}} and {(ref, pin): net name} from a KiCad netlist."""
    import glob as _glob   # 8 Sep 2026: a board generated in a copy directory (pcb-a-power-a23) carries the newest netlist; the newest of <stem>*/out/<stem>.net counts
    cands = [c for c in _glob.glob(os.path.join(ECAD, stem + "*", "out", stem + ".net")) if os.path.isfile(c)]
    path = max(cands, key=os.path.getmtime) if cands else os.path.join(ECAD, stem, "out", stem + ".net")
    if not os.path.exists(path): return None, None
    txt = open(path, encoding="utf-8", errors="replace").read()
    by_net, by_pin = {}, {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\n    \(net |\n  \)\n)', txt, re.S):
        name = m.group(1).lstrip("/"); nodes = set()
        for n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)):
            nodes.add((n.group(1), n.group(2))); by_pin[(n.group(1), n.group(2))] = name
        by_net[name] = nodes
    return by_net, by_pin

B = {}
for k, stem in NETS.items():
    n, p = load(stem)
    if n is None: print("MISSING netlist for %s (%s), run its chain first" % (k, stem))
    B[k] = (n or {}, p or {})

# Names that legitimately differ across a connector, with the reason. A contract is about which pin carries what,
# not about a board using another board's vocabulary for its own branch of a net.
ALIAS = [({"PANEL_5V", "+5V"}, "B fuses the panel feed (F6) and names the branch PANEL_5V; C names its incoming rail +5V"),
         ({"TS_CHG", "TS_MOD"}, "A names the thermistor line after the charger input it lands on, the dock after the module it comes from"),
         ({"DOCK_SPARE", "BLK_SPARE"}, "the spare contact, named after the connector on each side")]
def same(a, b):
    return a == b or any({a, b} == pair for pair, _ in ALIAS)

fails = []
def check(ok, text, detail=""):
    print(("PASS  " if ok else "FAIL  ") + text + (("   " + detail) if detail and not ok else ""))
    if not ok: fails.append(text)

def pinmap(board, ref, pins):
    """net name per pin of one connector, '' where the pin is absent."""
    return {p: B[board][1].get((ref, str(p)), "") for p in pins}

# 1. panel ribbon: the 2x13 map (B16/C7, 32.58) must be identical on B and C, all twenty-six pins named
mb, mc = pinmap("B", "J_PANEL", range(1, 27)), pinmap("C", "J_PANEL", range(1, 27))
diff = [p for p in range(1, 27) if not same(mb[p], mc[p])]
check(mb and all(mb.values()) and not diff, "J_PANEL 2x13 map identical on B and C",
      "differs on pins %s: %s" % (diff, {p: (mb[p], mc[p]) for p in diff[:4]}))

# 2. transmit inhibit: the panel toggle drives it on C, it crosses B and A, and on D it reaches Q3 alone
for k, ref in (("C", "SW_EMCON"), ("B", "J_PANEL"), ("A", "J_AB1"), ("D", "J_HARN1")):
    names = [n for n in B[k][0] if "INHIBIT" in n or "EMCON" in n]
    check(bool(names), "transmit inhibit present on %s (%s)" % (k, ref), "no EMCON or INHIBIT net")
def reaches(board, netname, target):
    """The net itself, plus one hop through any series or pull resistor on it."""
    nodes = B[board][0].get(netname, set()); seen = set(r for r, _ in nodes)
    for r, pin in list(nodes):
        if r.startswith("R"):
            for n2, other in B[board][0].items():
                if any(x == r and y != pin for x, y in other): seen |= set(x for x, _ in other)
    return target in seen, seen
d_inh = [n for n in B["D"][0] if "INHIBIT" in n]
if d_inh:
    nodes = B["D"][0][d_inh[0]]
    ok, seen = reaches("D", d_inh[0], "U12")
    check(ok, "D: %s reaches the KEY gate U12 (D8: KEY = PTT_ANY AND TX_INHIBIT_n)" % d_inh[0], str(sorted(seen)))
    check(all(r in ("J_HARN1", "U12") or r.startswith(("R", "TP")) for r, _ in nodes), "D: nothing but the harness, its pull-down, a test point and the KEY gate touches %s" % d_inh[0], str(sorted(nodes)))

# 3. four 5 V rails from A22 to B16 (VH pairs, same net names on both boards; 32.56)
for rail, ja, jb in (("+5V_S1", "J_5V_S1", "J_5V_S1"), ("+5V_S2", "J_5V_S2", "J_5V_S2"), ("+5V_S3", "J_5V_S3", "J_5V_S3"), ("+5V_DEV", "J_5V_DEV", "J_5V_DEV")):
    a = [n for (r, p), n in B["A"][1].items() if r == ja and n == rail]
    b = [n for (r, p), n in B["B"][1].items() if r == jb and n == rail]
    check(bool(a) and bool(b), "rail %s leaves A on %s and enters B on %s" % (rail, ja, jb),
          "A pins %d, B pins %d" % (len(a), len(b)))

# 4. dock signal contacts: A's J_DOCK 1..12 against the strip's J_BLK 1..12 (the block passes each contact through)
ma, me = pinmap("A", "J_DOCK", range(1, 13)), pinmap("E", "J_BLK", range(1, 13))
diff = [p for p in range(1, 13) if ma[p] and me[p] and not same(ma[p], me[p])]
check(ma and me and not diff, "dock 2x6 contact map identical on A (J_DOCK) and E (J_BLK)",
      "differs on %s: %s" % (diff, {p: (ma[p], me[p]) for p in diff[:6]}))
check(ma.get(8, "") == "SHORE_INHIBIT", "A J_DOCK pin 8 is SHORE_INHIBIT", ma.get(8, "absent"))
inh = B["E"][0].get("SHORE_INHIBIT", set())
reach = set(r for r, _ in inh)
for r, pin in list(inh):                       # one hop through the series resistor and the pull-down
    if r.startswith("R"):
        for n2, nodes in B["E"][0].items():
            if any(x == r and y != pin for x, y in nodes): reach |= set(x for x, _ in nodes)
check("U10" in reach, "E6: SHORE_INHIBIT reaches the sensor controller U10 (directly or through its series resistor)", str(sorted(reach)))

# 5. dock power contacts: four CELL+ pins, four returns and the pre-charge pin on A; the strip's lands on E
cp = [r for r, p in B["A"][0].get("CELL+", set()) if r.startswith("J_CP")]
cn = [r for r, p in B["A"][0].get("GND", set()) if r.startswith("J_CN")]
check(len(cp) == 4 and len(cn) == 4, "A22: four CELL+ pins and four return pins (GND, the In1 plane, 32.56) on the dock block", "CELL+ %s, return %s" % (sorted(cp), sorted(cn)))
pre = B["A"][1].get(("J_PRE1", "1"), "")
check(pre.startswith("CELL") or "PRE" in pre, "A: the pre-charge pin lands on a cell node net", pre or "absent")
check(("P_CP", "1") in B["E"][1] and ("P_CN", "1") in B["E"][1], "E: the 12 AWG lands P_CP and P_CN exist",
      "%s / %s" % (B["E"][1].get(("P_CP", "1"), "absent"), B["E"][1].get(("P_CN", "1"), "absent")))
check(B["E"][1].get(("P_CN", "1"), "") == "GND", "E6: the pack return lands on GND (the 14.4 V node's return is the ground plane, 32.56)", B["E"][1].get(("P_CN", "1"), "absent"))

# 6. shutdown pair on the A to B ribbon
for net in ("PI_SHDN_REQ", "PI_KILL"):
    a = [r for r, p in B["A"][0].get(net, set())]
    b = [r for r, p in B["B"][0].get(net, set())]
    check(bool(a) and bool(b), "ribbon net %s exists on A and B" % net, "A %s, B %s" % (sorted(a), sorted(b)))

# 7. the A to B ribbon (2x13 since A22/B16, 32.56): identical map on both boards, all twenty-six pins named
ma, mb = pinmap("A", "J_AB1", range(1, 27)), pinmap("B", "J_AB1", range(1, 27))
diff = [p for p in range(1, 27) if not same(ma[p], mb[p])]
check(ma and mb and all(ma.values()) and all(mb.values()) and not diff, "J_AB1 2x13 map identical on A and B",
      "differs on pins %s: %s" % (diff, {p: (ma[p], mb[p]) for p in diff[:4]}))
# 8. the mezzanine harness: A's J_MEZZ1 and D's J_HARN1 carry the same sixteen nets
ma, md = pinmap("A", "J_MEZZ1", range(1, 17)), pinmap("D", "J_HARN1", range(1, 17))
diff = [p for p in range(1, 17) if not same(ma[p], md[p])]
check(ma and md and all(ma.values()) and all(md.values()) and not diff, "J_MEZZ1 (A) and J_HARN1 (D) 2x8 maps identical",
      "differs on pins %s: %s" % (diff, {p: (ma[p], md[p]) for p in diff[:4]}))
# 9. D8 is a USB device set (32.52): its USB pair leaves B16's slot-3 hub, crosses J_AB1 to A22 and the harness to D8's hub
for net in ("USB_D8_P", "USB_D8_N"):
    a = [r for r, p in B["A"][0].get(net, set())]; b = [r for r, p in B["B"][0].get(net, set())]; d = [r for r, p in B["D"][0].get(net, set())]
    check("J_AB1" in a and "J_MEZZ1" in a and "J_AB1" in b and "J_HARN1" in d, "D8 USB pair %s: B16 J_AB1 -> A22 J_AB1/J_MEZZ1 -> D8 J_HARN1" % net, "A %s, B %s, D %s" % (sorted(a)[:4], sorted(b)[:4], sorted(d)[:4]))
# 10. the wall host port: its USB pair comes from B16's slot-1 hub over the ribbon and ends on A22's wall port part J_USBW
for net in ("USB_WALL_P", "USB_WALL_N"):
    a = [r for r, p in B["A"][0].get(net, set())]; b = [r for r, p in B["B"][0].get(net, set())]
    check("J_USBW" in a and "J_AB1" in a and "J_AB1" in b and any(r in ("U102", "U202", "U302") for r in b), "wall-port pair %s: B16 slot hub -> J_AB1 -> A22 J_USBW" % net, "A %s, B %s" % (sorted(a)[:5], sorted(b)[:5]))
# 11. the harness 3.3 V and the panel controller's USB: A22's +3V3 reaches D8 over the harness; B16's USB_PNL pair reaches C7 over the ribbon
for k, ref in (("A", "J_MEZZ1"), ("D", "J_HARN1")):
    check(any(r == ref for r, _ in B[k][0].get("+3V3", set())), "+3V3 on %s %s" % (k, ref))
for net in ("USB_PNL_P", "USB_PNL_N"):
    check(any(r == "J_PANEL" for r, _ in B["B"][0].get(net, set())) and any(r == "J_PANEL" for r, _ in B["C"][0].get(net, set())), "panel controller USB pair %s on B16 and C7 J_PANEL" % net)
# 12. the hardware EMCON line: C7's toggle makes TX_INHIBIT_n and EMCON_HW, both cross to B16; TX_INHIBIT_n reaches D8's KEY gate, EMCON_HW the radio disable stages on B16
check(any(r == "SW_EMCON" for r, _ in B["C"][0].get("TX_INHIBIT_n", set())) and any(r == "J_PANEL" for r, _ in B["C"][0].get("EMCON_HW", set())), "C7: SW_EMCON drives TX_INHIBIT_n, EMCON_HW leaves on J_PANEL")
check(any(r == "J_HARN1" for r, _ in B["D"][0].get("TX_INHIBIT_n", set())) and any(r.startswith("U") for r, _ in B["D"][0].get("TX_INHIBIT_n", set())), "D8: TX_INHIBIT_n from J_HARN1 into the KEY gate")

# 13 to 15: the safety lines, added 9 September 2026 after a red team found that check 12 passes on a design that does the OPPOSITE of what
# it says (appendix 32.81). Check 12 asks whether the nets exist. These ask who drives them, in which sense, and what happens when the panel
# ribbon is not there. The defect they would have caught: C7 inverted the toggle into two boards that were both built on "low silences", so
# asserting EMCON enabled the 30 W PA and released both M.2 radios, and A22 drove TX_INHIBIT_n back from EMCON_HW, closing a feedback loop.
def _value_of(stem, ref):
    import glob as _g
    cands = [c for c in _g.glob(os.path.join(ECAD, stem + "*", "out", stem + ".net")) if os.path.isfile(c)]
    if not cands: return ""
    txt = open(max(cands, key=os.path.getmtime), encoding="utf-8", errors="replace").read()
    m = re.search(r'\(comp \(ref "%s"\)\s*\(value "([^"]*)"\)' % re.escape(ref), txt)
    return m.group(1) if m else ""

# 13. one driver: the inhibit line is made by the panel toggle and read everywhere else. No gate output may sit on it.
for _bd, _stem in (("A", "pcb-a-power"), ("B", "pcb-b-compute")):
    _u = sorted({r for r, _ in B[_bd][0].get("TX_INHIBIT_n", set()) if r.startswith("U")})
    check(not _u, "%s: no device drives TX_INHIBIT_n, the panel toggle is its only source" % _bd, "found %s" % _u)
_u26 = sorted({pin for r, pin in B["A"][0].get("EMCON_HW", set()) if r == "U26"})
check(set(_u26) <= {"1", "4"}, "A22: EMCON_HW reaches only the AND gates' inputs 1A and 2A, never an output", "U26 pins %s" % _u26)

# 14. fail safe: with the panel ribbon out, every consumer must read the inhibit line LOW, so each holds it down itself.
for _bd in ("A", "B", "D"):
    _gnd = {r for r, _ in B[_bd][0].get("GND", set())}
    _pull = sorted({r for r, _ in B[_bd][0].get("TX_INHIBIT_n", set()) if r.startswith("R") and r in _gnd})
    check(bool(_pull), "%s: TX_INHIBIT_n is pulled DOWN on this board, so a missing panel inhibits" % _bd, "pull-downs %s" % _pull)

# 15. the sense: C7 buffers the toggle into EMCON_HW, it does not invert it (both consumer boards silence on LOW).
_u9 = _value_of("pcb-c-display", "U9")
check("1G04" not in _u9 and ("1G34" in _u9 or "buffer" in _u9.lower()), "C7: U9 buffers TX_INHIBIT_n into EMCON_HW rather than inverting it", _u9 or "no value read")


# 16. an in-line part is in line with something (9 Sep 2026, E7, appendix 32.83). R48 on E is drawn as the Geiger
# module's "pulse input series" resistor, but U10 pin 9 sat on GEIGER_PULSE with the connector, so the pulse reached
# the RP2040 directly and the resistor hung off it with only TP13 on its far side: a part that does nothing, the same
# class as the EMCON gate of 32.80. A two-pin part whose value says series must have a real pin on BOTH of its nets,
# counting neither test points, nor power flags, nor the part itself.
_IGNORE = ("TP", "#FLG", "#PWR")
for _bd, _stem in NETS.items():
    _nets, _pins = B[_bd]
    if not _pins: continue
    _refs = {}
    for (r, pin), net in _pins.items(): _refs.setdefault(r, {})[pin] = net
    for _r, _pp in sorted(_refs.items()):
        if not _r.startswith(("R", "FB", "L", "F")) or len(_pp) != 2: continue
        _val = _value_of(_stem, _r)
        if "series" not in _val.lower(): continue
        _bad = [n for n in _pp.values()
                if not [q for q, _ in _nets.get(n, set()) if q != _r and not q.startswith(_IGNORE)]]
        check(not _bad, "%s: %s (%s) is in series with a real pin on both sides" % (_bd, _r, _val), "dead net(s) %s" % _bad)

print("\n%d contract(s) FAILED" % len(fails) if fails else "\nALL CONTRACTS PASS")
sys.exit(1 if fails else 0)
