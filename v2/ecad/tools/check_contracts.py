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
    path = os.path.join(ECAD, stem, "out", stem + ".net")
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

# 1. panel ribbon: the 2x10 map must be identical on B and C, all twenty pins named
mb, mc = pinmap("B", "J_PANEL", range(1, 21)), pinmap("C", "J_PANEL", range(1, 21))
diff = [p for p in range(1, 21) if not same(mb[p], mc[p])]
check(mb and all(mb.values()) and not diff, "J_PANEL 2x10 map identical on B and C",
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
    ok, seen = reaches("D", d_inh[0], "Q3")
    check(ok, "D: %s reaches Q3 (directly or through its resistors)" % d_inh[0], str(sorted(seen)))
    check(all(not r.startswith("U") for r, _ in nodes), "D: nothing but the harness and Q3 drives %s" % d_inh[0], str(sorted(nodes)))

# 3. three 5 V rails from A to B (VH pairs, same net names on both boards)
for rail, ja, jb in (("+5V_M1", "J_5V_M1", "J_5V_M1"), ("+5V_M2", "J_5V_M2", "J_5V_M2"), ("+5V_PI", "J_5V_PI", "J_5V_PI")):
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
check("U2" in reach, "E: SHORE_INHIBIT reaches the opto U2 (directly or through its series resistor)", str(sorted(reach)))

# 5. dock power contacts: four CELL+ pins, four returns and the pre-charge pin on A; the strip's lands on E
cp = [r for r, p in B["A"][0].get("CELL+", set()) if r.startswith("J_CP")]
cn = [r for r, p in B["A"][0].get("CELL_N", set()) if r.startswith("J_CN")]
check(len(cp) == 4 and len(cn) == 4, "A: four CELL+ pins and four return pins on the dock block", "CELL+ %s, return %s" % (sorted(cp), sorted(cn)))
pre = B["A"][1].get(("J_PRE1", "1"), "")
check(pre.startswith("CELL") or "PRE" in pre, "A: the pre-charge pin lands on a cell node net", pre or "absent")
check(("P_CP", "1") in B["E"][1] and ("P_CN", "1") in B["E"][1], "E: the 12 AWG lands P_CP and P_CN exist",
      "%s / %s" % (B["E"][1].get(("P_CP", "1"), "absent"), B["E"][1].get(("P_CN", "1"), "absent")))
check(B["E"][1].get(("P_CN", "1"), "") not in ("GND",), "E: the module return is its own net, not GND", B["E"][1].get(("P_CN", "1"), "absent"))

# 6. shutdown pair on the A to B ribbon
for net in ("PI_SHDN_REQ", "PI_KILL"):
    a = [r for r, p in B["A"][0].get(net, set())]
    b = [r for r, p in B["B"][0].get(net, set())]
    check(bool(a) and bool(b), "ribbon net %s exists on A and B" % net, "A %s, B %s" % (sorted(a), sorted(b)))

# 7. the A to B ribbon (2x9 since A20/B13): identical map on both boards, all eighteen pins named
ma, mb = pinmap("A", "J_AB1", range(1, 19)), pinmap("B", "J_AB1", range(1, 19))
diff = [p for p in range(1, 19) if not same(ma[p], mb[p])]
check(ma and mb and all(ma.values()) and all(mb.values()) and not diff, "J_AB1 2x9 map identical on A and B",
      "differs on pins %s: %s" % (diff, {p: (ma[p], mb[p]) for p in diff[:4]}))
# 8. the mezzanine harness: A's J_MEZZ1 and D's J_HARN1 carry the same sixteen nets
ma, md = pinmap("A", "J_MEZZ1", range(1, 17)), pinmap("D", "J_HARN1", range(1, 17))
diff = [p for p in range(1, 17) if not same(ma[p], md[p])]
check(ma and md and all(ma.values()) and all(md.values()) and not diff, "J_MEZZ1 (A) and J_HARN1 (D) 2x8 maps identical",
      "differs on pins %s: %s" % (diff, {p: (ma[p], md[p]) for p in diff[:4]}))
# 9. I2S from the module to the codec: the four lines exist on B (the module), A (pass-through) and D (the WM8960)
for net in ("I2S_BCLK", "I2S_LRCLK", "I2S_DOUT", "I2S_DIN"):
    have = {k: bool(B[k][0].get(net)) for k in ("A", "B", "D")}
    check(all(have.values()), "I2S line %s on B, A and D" % net, str(have))
check(any(r.startswith("U30") for r, _ in B["B"][0].get("I2S_BCLK", set())), "B: I2S_BCLK leaves a module connector pin", str(sorted(B["B"][0].get("I2S_BCLK", set()))[:4]))
check(any(r == "U5" for r, _ in B["D"][0].get("I2S_BCLK", set())), "D: I2S_BCLK reaches the codec U5", str(sorted(B["D"][0].get("I2S_BCLK", set()))[:4]))
# 10. the wall host port: its USB pair comes from B's hub over the ribbon and ends on A's J_WALL1
for net in ("USB_WALL_P", "USB_WALL_N"):
    a = [r for r, p in B["A"][0].get(net, set())]; b = [r for r, p in B["B"][0].get(net, set())]
    check("J_WALL1" in a and "J_AB1" in a and "U1" in b and "J_AB1" in b, "wall-port pair %s: B hub -> J_AB1 -> A J_WALL1" % net, "A %s, B %s" % (sorted(a), sorted(b)))
# 11. the gated codec rail: B13's +3V3_AB crosses the ribbon and the harness to the codec on D
for k, ref in (("B", "J_AB1"), ("A", "J_AB1"), ("A", "J_MEZZ1"), ("D", "J_HARN1")):
    check(any(r == ref for r, _ in B[k][0].get("+3V3_AB", set())), "+3V3_AB on %s %s" % (k, ref))

print("\n%d contract(s) FAILED" % len(fails) if fails else "\nALL CONTRACTS PASS")
sys.exit(1 if fails else 0)
