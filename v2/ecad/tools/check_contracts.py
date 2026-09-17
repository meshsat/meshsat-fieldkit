#!/usr/bin/env python3
"""Cross-board contract check for the Rev A set (A20, B13, C5, D6, E4, plus the E5 block, appendix 32.26 and 32.35).

Reads the KiCad netlists in <board>/out/<board>.net and verifies the connections that no single board's gate can see:
the panel ribbon map, the transmit inhibit chain, the three 5 V rails, the dock signal and power contacts, the
shutdown pair on the A to B ribbon, the 2x9 ribbon map itself, the mezzanine harness map and the I2S and wall-port pairs (32.35). Prints one line per contract and exits non-zero on any FAIL.
Usage: check_contracts.py [ecad dir]   (default: the directory above this script)"""
import sys, os, re, collections

ECAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
# 16 September 2026: BOARD P IS IN THE SET. It was left out because the contracts were written for the five
# boards that share connectors, and the pack is joined to board E by two 12 AWG wires rather than a header. A
# wire is a conductor like any other: P's W_P and W_N land on E's XT60, and rule SCH-003 read INCONCLUSIVE on
# board P for as long as no contract named it, which is "absence is never a pass" in the one check that exists
# to compare boards with each other. Board E5, the dock block, has no schematic and therefore no netlist: its
# targets are GENERATED from board A's own board file, so the thing to check there is the board and not the
# netlist, and it is named as a gap rather than left silent.
NETS = {"A": "pcb-a-power", "B": "pcb-b-compute", "C": "pcb-c-display", "D": "pcb-d-aprs", "E": "pcb-e1-dock",
        "P": "pcb-p-pack"}

def netlist_path(stem):
    """The netlist of the DECLARED phase directory, or the newest copy when nothing declares one.

    8 September 2026: a board generated in a copy directory (pcb-a-power-a23) carries the newest netlist, so
    the newest of `<stem>*/out/<stem>.net` counted. 14 September 2026: THAT IS THE WRONG DIRECTORY ON THE BOX.
    Forty-one directories match `pcb-b-compute*` there, every one of them an arm laid down to measure a knob,
    and the newest is whichever arm ran last. A cross-board contract judged against an arm's netlist is the
    "wrong tree" defect of 32.153 in the one check that exists to compare boards with each other. The phase a
    board is cutting is declared in `boards/<letter>.json`, and the routeflow profile of that phase names its
    project directory, so the answer is read rather than guessed; the glob stays as the fallback for a tree
    that carries no profiles."""
    import glob as _glob, json as _json
    here = os.path.dirname(os.path.abspath(__file__))
    for _letter, _stem in NETS.items():
        if _stem != stem: continue
        try:
            _b = _json.load(open(os.path.join(here, "boards", _letter.lower() + ".json")))
            _phase = (_b.get("phase") or "").lower()
            # ONE PROFILE PER LETTER SINCE 15 SEPTEMBER, AND THIS COMPARISON STOPPED BEING TRUE THAT DAY
            # (17 September 2026). Each `routeflow/<letter>.json` now carries the literal phase placeholder
            # `<PHASE>`, which a run fills in from --phase or the board file, so `phase != declared` was true
            # of every profile and the loop selected nothing: `netlist_path` has been falling through to the
            # newest directory by mtime ever since, which is the 14 September defect this function exists to
            # prevent and it bites where it hurts, on a box carrying forty-one arm directories for one board.
            # The profile is identified by the BOARD it routes, which is unique per letter; a profile that
            # still names a real phase is held to it.
            for _pf in sorted(_glob.glob(os.path.join(here, "routeflow", "*.json"))):
                _p = _json.load(open(_pf))
                if _p.get("board") != stem: continue
                _ph = str(_p.get("phase") or "")
                if _ph and not _ph.startswith("<") and _ph.lower() != _phase: continue
                _d = os.path.join(ECAD, os.path.basename(_p.get("project", "")), "out", stem + ".net")
                if os.path.isfile(_d): return _d
        except Exception: pass
    cands = [c for c in _glob.glob(os.path.join(ECAD, stem + "*", "out", stem + ".net")) if os.path.isfile(c)]
    return max(cands, key=os.path.getmtime) if cands else os.path.join(ECAD, stem, "out", stem + ".net")


def load(stem):
    """{net name: {(ref, pin)}} and {(ref, pin): net name} from a KiCad netlist."""
    path = netlist_path(stem)
    if not os.path.exists(path): return None, None
    # 13 September 2026 (MESHSAT-862): A NETLIST OLDER THAN ITS SCHEMATIC DESCRIBES A BOARD THAT NO LONGER
    # EXISTS. Board B's netlist in the box clone was five hours older than its schematic and carried no J_AB2
    # at all, because every B run that day had been in an isolated tree. Four contracts then failed on every
    # board's finish, naming the A-to-B ribbon, and the two generators had been identical all along. The
    # check compared a current A against a B from before the ribbon split. It is reported here and counted as
    # a missing netlist, which is already INCONCLUSIVE rather than a pass: a comparison against stale data is
    # not a result in either direction.
    # THE SIDECAR RECORDS WHICH SCHEMATIC IT CAME FROM, AND A TIMESTAMP WAS BEING READ INSTEAD (17 September
    # 2026). `sch_prov.write` has recorded `schematic_sha256` since 16 September, which is the FACT this guard
    # wants; the mtime is a proxy for it, and the two disagree in both directions. Board B's schematic was
    # rewritten with identical content at 05:19 (a checkout), which made the mtime newer and the netlist
    # "stale" though nothing had changed; and on the same morning ALL SIX netlists had been regenerated and
    # committed without their schematics, so every one of them came from a schematic this tree does not hold
    # while five of the six passed the mtime test because their schematics happened to be older. One board
    # refused and five passed in the identical state is the shape of a guard reading the wrong thing.
    # Content decides when the sidecar is there; the mtime stays the answer when it is not, because a netlist
    # with no provenance is exactly the case the 13 September rule was written for.
    _sch = os.path.join(os.path.dirname(os.path.dirname(path)), stem + ".kicad_sch")
    if os.path.exists(_sch):
        import hashlib as _h, sch_prov as _sp
        _rec = _sp.read(path) or {}
        _want = _rec.get("schematic_sha256")
        _have = _h.sha256(open(_sch, "rb").read()).hexdigest()[:32]
        if _want:
            if _want != _have:
                print("STALE netlist for %s: %s was generated from schematic %s and this tree holds %s. "
                      "Regenerate it (gen_sch then build_sch) before trusting any contract that names this "
                      "board." % (stem, os.path.relpath(path, ECAD), _want[:12], _have[:12]))
                return None, None
        elif os.path.getmtime(path) < os.path.getmtime(_sch) - 1:
            import datetime as _dt
            _f = lambda t: _dt.datetime.fromtimestamp(t).strftime("%d %b %H:%M")
            print("STALE netlist for %s: %s is from %s and its schematic is from %s, and it carries no "
                  "provenance sidecar to say which schematic it came from. Regenerate it (gen_sch then "
                  "build_sch) before trusting any contract that names this board."
                  % (stem, os.path.relpath(path, ECAD), _f(os.path.getmtime(path)), _f(os.path.getmtime(_sch))))
            return None, None
    # AND WHICH GENERATOR WROTE IT (16 September 2026). The timestamp guard above compares a netlist with its
    # OWN schematic, so a whole directory copied from an older generation passes it: both files are old
    # together. That is exactly what happened today. The set verdict taken inside board A's sweep tree failed
    # twelve contracts naming board B's six PCIe receive coupling capacitors as absent, while board B's own
    # netlist carried them and board B's own verdict read PASS on 37 of 37, because A's tree held a copy of B
    # from before they existed. Seven boards carried that FAIL on rule SCH-003.
    # A netlist written by a generator this tree does not have is not evidence about this tree's design, in
    # either direction, so it is reported and counted as missing, which is INCONCLUSIVE and never a pass.
    _letter = next((l for l, st in NETS.items() if st == stem), "")
    if _letter:
        import sch_prov as _prov
        _ok, _why = _prov.current(path, _letter, os.path.dirname(os.path.abspath(__file__)))
        if not _ok:
            print("UNKNOWN GENERATOR for %s: %s" % (stem, _why))
            return None, None
    txt = open(path, encoding="utf-8", errors="replace").read()
    by_net, by_pin = {}, {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\n    \(net |\n  \)\n)', txt, re.S):
        name = m.group(1).lstrip("/"); nodes = set()
        for n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)):
            nodes.add((n.group(1), n.group(2))); by_pin[(n.group(1), n.group(2))] = name
        by_net[name] = nodes
    return by_net, by_pin

B = {}
MISSING = []
for k, stem in NETS.items():
    n, p = load(stem)
    if n is None:
        print("MISSING netlist for %s (%s), run its chain first" % (k, stem))
        MISSING.append(k)
    B[k] = (n or {}, p or {})

# Names that legitimately differ across a connector, with the reason. A contract is about which pin carries what,
# not about a board using another board's vocabulary for its own branch of a net.
ALIAS = [({"PANEL_5V", "+5V"}, "B fuses the panel feed (F6) and names the branch PANEL_5V; C names its incoming rail +5V"),
         ({"TS_CHG", "TS_MOD"}, "A names the thermistor line after the charger input it lands on, the dock after the module it comes from"),
         ({"DOCK_SPARE", "BLK_SPARE"}, "the spare contact, named after the connector on each side")]
def same(a, b):
    return a == b or any({a, b} == pair for pair, _ in ALIAS)

# WHICH BOARDS A CONTRACT IS ABOUT (16 September 2026). Board B was missing six PCIe coupling capacitors, and
# the set verdict this file writes is read as evidence by EVERY board, so five boards that have nothing to do
# with those capacitors reported a failed rule. A contract between two boards is rightly a failure on both; a
# contract that names one board is not evidence about the other six.
#
# Every contract DECLARES its boards rather than having them read out of its sentence. The first version
# inferred them from the text, which is where the sentences already name them, and it was wrong on board A
# within nine tries: "rail X leaves A on J_Y" and "A: the pre-charge pin lands on a cell node net" both lost
# their board, because the English article "A" had to be stripped for the inference to work at all. An
# attribution that is right most of the time puts a board's failure on another board's page.
fails = []; checked = []
per_board = collections.defaultdict(lambda: {"pass": 0, "fail": [], "unjudged": []})
unjudged = []
def check(ok, text, detail="", boards=None):
    if not boards: raise AssertionError("contract %r declares no board: say which boards it is about" % text[:70])
    # A CONTRACT THAT NAMES AN ABSENT BOARD IS UNJUDGED, NOT FAILED (17 September 2026). A contract is an
    # agreement between two boards' netlists, so with one of them missing from this tree the comparison was
    # never made: its pin map reads as empty and every pin "disagrees". The per-board guard below covers the
    # board that is ABSENT and not the board at the other end, so a run on the runner, where no chain has
    # written a netlist, put board B's absence on board C's page as two failed contracts and on board A's as
    # twelve, over readings taken on the box WITH those netlists. Absence is inconclusive here as everywhere:
    # the contract is counted as unjudged, both ends say so, and neither is failed for it.
    _absent = [b for b in boards if b in MISSING]
    if _absent:
        print("UNJUDGED  " + text + "   (%s absent from this tree)" % ", ".join(_absent))
        unjudged.append(text)
        for _b in boards: per_board[_b]["unjudged"].append(text)
        return
    print(("PASS  " if ok else "FAIL  ") + text + (("   " + detail) if detail and not ok else ""))
    checked.append(text)
    if not ok: fails.append(text)
    for _b in boards:
        if ok: per_board[_b]["pass"] += 1
        else: per_board[_b]["fail"].append(text)

def pinmap(board, ref, pins):
    """net name per pin of one connector, '' where the pin is absent."""
    return {p: B[board][1].get((ref, str(p)), "") for p in pins}

# 1. panel ribbon: the 2x13 map (B16/C7, 32.58) must be identical on B and C, all twenty-six pins named
mb, mc = pinmap("B", "J_PANEL", range(1, 27)), pinmap("C", "J_PANEL", range(1, 27))
# 15 September 2026: A CONNECTOR WITH NO PIN NAMED ON ONE BOARD IS A BOARD THAT IS NOT THERE, NOT A DISAGREEMENT
# ON EVERY PIN. C17's finish in an isolated tree read B's map as twenty-six empty strings and this check said
# "differs on pins [1..26]", refusing a board that was 0 hard, 0 unrouted and clean on every other gate. A
# comparison with nothing is not a result in either direction, which is what the staleness rule above already
# says for a netlist older than its schematic; the same is true of a map with no pin in it.
_empty = [k for k, m in (("B", mb), ("C", mc)) if not any(m.values())]
if _empty:
    for k in _empty: print("MISSING J_PANEL map on %s: its netlist names no pin of the connector, so the ribbon contract is not judged" % k)
    MISSING.extend(k for k in _empty if k not in MISSING)
diff = [p for p in range(1, 27) if not same(mb[p], mc[p])] if not _empty else []
check(bool(_empty) or (mb and all(mb.values()) and not diff), "J_PANEL 2x13 map identical on B and C",
      "differs on pins %s: %s" % (diff, {p: (mb[p], mc[p]) for p in diff[:4]}), boards={"B", "C"})

# 2. transmit inhibit: the panel toggle drives it on C, it crosses B and A, and on D it reaches Q3 alone
for k, ref in (("C", "SW_EMCON"), ("B", "J_PANEL"), ("A", "J_AB1"), ("D", "J_HARN1")):
    names = [n for n in B[k][0] if "INHIBIT" in n or "EMCON" in n]
    check(bool(names), "transmit inhibit present on %s (%s)" % (k, ref), "no EMCON or INHIBIT net", boards={k})
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
    check(ok, "D: %s reaches the KEY gate U12 (D8: KEY = PTT_ANY AND TX_INHIBIT_n)" % d_inh[0], str(sorted(seen)), boards={"D"})
    check(all(r in ("J_HARN1", "U12") or r.startswith(("R", "TP")) for r, _ in nodes), "D: nothing but the harness, its pull-down, a test point and the KEY gate touches %s" % d_inh[0], str(sorted(nodes)), boards={"D"})

# 3. four 5 V rails from A22 to B16 (VH pairs, same net names on both boards; 32.56)
for rail, ja, jb in (("+5V_S1", "J_5V_S1", "J_5V_S1"), ("+5V_S2", "J_5V_S2", "J_5V_S2"), ("+5V_S3", "J_5V_S3", "J_5V_S3"), ("+5V_DEV", "J_5V_DEV", "J_5V_DEV")):
    a = [n for (r, p), n in B["A"][1].items() if r == ja and n == rail]
    b = [n for (r, p), n in B["B"][1].items() if r == jb and n == rail]
    check(bool(a) and bool(b), "rail %s leaves A on %s and enters B on %s" % (rail, ja, jb),
          "A pins %d, B pins %d" % (len(a), len(b)), boards={"A", "B"})

# 4. dock signal contacts: A's J_DOCK 1..12 against the strip's J_BLK 1..12 (the block passes each contact through)
ma, me = pinmap("A", "J_DOCK", range(1, 13)), pinmap("E", "J_BLK", range(1, 13))
diff = [p for p in range(1, 13) if ma[p] and me[p] and not same(ma[p], me[p])]
check(ma and me and not diff, "dock 2x6 contact map identical on A (J_DOCK) and E (J_BLK)",
      "differs on %s: %s" % (diff, {p: (ma[p], me[p]) for p in diff[:6]}), boards={"A", "E"})
check(ma.get(8, "") == "SHORE_INHIBIT", "A J_DOCK pin 8 is SHORE_INHIBIT", ma.get(8, "absent"), boards={"A"})
inh = B["E"][0].get("SHORE_INHIBIT", set())
reach = set(r for r, _ in inh)
for r, pin in list(inh):                       # one hop through the series resistor and the pull-down
    if r.startswith("R"):
        for n2, nodes in B["E"][0].items():
            if any(x == r and y != pin for x, y in nodes): reach |= set(x for x, _ in nodes)
check("U10" in reach, "E6: SHORE_INHIBIT reaches the sensor controller U10 (directly or through its series resistor)", str(sorted(reach)), boards={"E"})

# 5. dock power contacts: four CELL+ pins, four returns and the pre-charge pin on A; the strip's lands on E
cp = [r for r, p in B["A"][0].get("CELL+", set()) if r.startswith("J_CP")]
cn = [r for r, p in B["A"][0].get("GND", set()) if r.startswith("J_CN")]
check(len(cp) == 4 and len(cn) == 4, "A22: four CELL+ pins and four return pins (GND, the In1 plane, 32.56) on the dock block", "CELL+ %s, return %s" % (sorted(cp), sorted(cn)), boards={"A"})
pre = B["A"][1].get(("J_PRE1", "1"), "")
check(pre.startswith("CELL") or "PRE" in pre, "A: the pre-charge pin lands on a cell node net", pre or "absent", boards={"A"})
check(("P_CP", "1") in B["E"][1] and ("P_CN", "1") in B["E"][1], "E: the 12 AWG lands P_CP and P_CN exist",
      "%s / %s" % (B["E"][1].get(("P_CP", "1"), "absent"), B["E"][1].get(("P_CN", "1"), "absent")), boards={"E"})
check(B["E"][1].get(("P_CN", "1"), "") == "GND", "E6: the pack return lands on GND (the 14.4 V node's return is the ground plane, 32.56)", B["E"][1].get(("P_CN", "1"), "absent"), boards={"E"})

# 6. shutdown pair on the A to B ribbon
for net in ("PI_SHDN_REQ", "PI_KILL"):
    a = [r for r, p in B["A"][0].get(net, set())]
    b = [r for r, p in B["B"][0].get(net, set())]
    check(bool(a) and bool(b), "ribbon net %s exists on A and B" % net, "A %s, B %s" % (sorted(a), sorted(b)), boards={"A", "B"})

# 7. the A to B ribbon (2x13 since A22/B16, 32.56): identical map on both boards, all twenty-six pins named
ma, mb = pinmap("A", "J_AB1", range(1, 27)), pinmap("B", "J_AB1", range(1, 27))
diff = [p for p in range(1, 27) if not same(ma[p], mb[p])]
check(ma and mb and all(ma.values()) and all(mb.values()) and not diff, "J_AB1 2x13 map identical on A and B",
      "differs on pins %s: %s" % (diff, {p: (ma[p], mb[p]) for p in diff[:4]}), boards={"A", "B"})
# 7b. the wall-port ribbon J_AB2 (2x5 since 12 September 2026, appendix 32.135): the same map on both boards.
# The wall pair left J_AB1 because a 2x13 has two end rows and the ribbon carried three pairs; this connector
# exists so the third pair has an end row of its own.
ma2, mb2 = pinmap("A", "J_AB2", range(1, 11)), pinmap("B", "J_AB2", range(1, 11))
diff2 = [p for p in range(1, 11) if not same(ma2[p], mb2[p])]
check(ma2 and mb2 and all(ma2.values()) and all(mb2.values()) and not diff2, "J_AB2 2x5 map identical on A and B",
      "differs on pins %s: %s" % (diff2, {p: (ma2[p], mb2[p]) for p in diff2[:4]}), boards={"A", "B"})
check(same(ma2.get(1), "USB_WALL_P") and same(ma2.get(2), "USB_WALL_N"), "J_AB2 carries the wall pair on its END row (pins 1 and 2)",
      "pins 1 and 2 are %s and %s" % (ma2.get(1), ma2.get(2)), boards={"A", "B"})
# 8. the mezzanine harness: A's J_MEZZ1 and D's J_HARN1 carry the same sixteen nets
ma, md = pinmap("A", "J_MEZZ1", range(1, 17)), pinmap("D", "J_HARN1", range(1, 17))
diff = [p for p in range(1, 17) if not same(ma[p], md[p])]
check(ma and md and all(ma.values()) and all(md.values()) and not diff, "J_MEZZ1 (A) and J_HARN1 (D) 2x8 maps identical",
      "differs on pins %s: %s" % (diff, {p: (ma[p], md[p]) for p in diff[:4]}), boards={"A", "D"})
# 9. D8 is a USB device set (32.52): its USB pair leaves B16's slot-3 hub, crosses J_AB1 to A22 and the harness to D8's hub
for net in ("USB_D8_P", "USB_D8_N"):
    a = [r for r, p in B["A"][0].get(net, set())]; b = [r for r, p in B["B"][0].get(net, set())]; d = [r for r, p in B["D"][0].get(net, set())]
    check("J_AB1" in a and "J_MEZZ1" in a and "J_AB1" in b and "J_HARN1" in d, "D8 USB pair %s: B16 J_AB1 -> A22 J_AB1/J_MEZZ1 -> D8 J_HARN1" % net, "A %s, B %s, D %s" % (sorted(a)[:4], sorted(b)[:4], sorted(d)[:4]), boards={"A", "B", "D"})
# 10. the wall host port: its USB pair comes from B16's slot-1 hub over the ribbon and ends on A22's wall port part J_USBW
for net in ("USB_WALL_P", "USB_WALL_N"):
    a = [r for r, p in B["A"][0].get(net, set())]; b = [r for r, p in B["B"][0].get(net, set())]
    check("J_USBW" in a and "J_AB2" in a and "J_AB2" in b and any(r in ("U102", "U202", "U302") for r in b), "wall-port pair %s: B16 slot hub -> J_AB2 -> A22 J_USBW" % net, "A %s, B %s" % (sorted(a)[:5], sorted(b)[:5]), boards={"A", "B"})
# 11. the harness 3.3 V and the panel controller's USB: A22's +3V3 reaches D8 over the harness; B16's USB_PNL pair reaches C7 over the ribbon
for k, ref in (("A", "J_MEZZ1"), ("D", "J_HARN1")):
    check(any(r == ref for r, _ in B[k][0].get("+3V3", set())), "+3V3 on %s %s" % (k, ref), boards={k})
for net in ("USB_PNL_P", "USB_PNL_N"):
    check(any(r == "J_PANEL" for r, _ in B["B"][0].get(net, set())) and any(r == "J_PANEL" for r, _ in B["C"][0].get(net, set())), "panel controller USB pair %s on B16 and C7 J_PANEL" % net, boards={"B", "C"})
# 12. the hardware EMCON line: C7's toggle makes TX_INHIBIT_n and EMCON_HW, both cross to B16; TX_INHIBIT_n reaches D8's KEY gate, EMCON_HW the radio disable stages on B16
check(any(r == "SW_EMCON" for r, _ in B["C"][0].get("TX_INHIBIT_n", set())) and any(r == "J_PANEL" for r, _ in B["C"][0].get("EMCON_HW", set())), "C7: SW_EMCON drives TX_INHIBIT_n, EMCON_HW leaves on J_PANEL", boards={"C"})
check(any(r == "J_HARN1" for r, _ in B["D"][0].get("TX_INHIBIT_n", set())) and any(r.startswith("U") for r, _ in B["D"][0].get("TX_INHIBIT_n", set())), "D8: TX_INHIBIT_n from J_HARN1 into the KEY gate", boards={"D"})

# 13 to 15: the safety lines, added 9 September 2026 after a red team found that check 12 passes on a design that does the OPPOSITE of what
# it says (appendix 32.81). Check 12 asks whether the nets exist. These ask who drives them, in which sense, and what happens when the panel
# ribbon is not there. The defect they would have caught: C7 inverted the toggle into two boards that were both built on "low silences", so
# asserting EMCON enabled the 30 W PA and released both M.2 radios, and A22 drove TX_INHIBIT_n back from EMCON_HW, closing a feedback loop.
def _value_of(stem, ref):
    _p = netlist_path(stem)
    if not os.path.isfile(_p): return ""
    txt = open(_p, encoding="utf-8", errors="replace").read()
    m = re.search(r'\(comp \(ref "%s"\)\s*\(value "([^"]*)"\)' % re.escape(ref), txt)
    return m.group(1) if m else ""

# 12b. PCIe AC coupling (rule INT-001, 16 September 2026). Raspberry Pi, Compute Module 5 datasheet, section
# 2.3: "CM5 includes on-board AC coupling capacitors for the PCIe_TX signals. However, external AC coupling
# capacitors are required for PCIe_RX signals, close to the driving source (the peripheral's TX)", and 2.3.1:
# "Ensure each receive (PCIe-Rx) line has an AC coupling capacitor (220 nF) before it enters the IC"
# (v2/vendor/cm5/cm5-datasheet.pdf). Board B connected the switch's transmit pins straight to the module's
# receive pins for three slots, on a design that had passed every gate, because nothing read that clause.
# The contract is the shape of the fix, not the fix itself: the module's receive net carries a capacitor and
# never a second IC, so the same defect cannot come back under a different reference designator.
for _s in (1, 2, 3):
    for _pn in ("P", "N"):
        _net = "PCIE%d_RX_%s" % (_s, _pn)
        _nodes = B["B"][0].get(_net, set())
        if not _nodes and not B["B"][0]:
            continue                                     # no netlist for B: already counted as missing above
        _caps = sorted({r for r, _ in _nodes if r.startswith("C")})
        _ics = sorted({r for r, _ in _nodes if r.startswith("U") or r.startswith("J_M2") or r.startswith("J_")})
        check(len(_caps) == 1, "B: %s has exactly one series AC coupling capacitor (CM5 datasheet 2.3.1)" % _net,
              "capacitors on the net: %s" % (_caps or "none"), boards={"B"})
        check(len(_ics) <= 1, "B: %s enters one IC only, so the capacitor is in series and not a stub" % _net,
              "devices on the net: %s" % _ics, boards={"B"})
        for _c in _caps:
            # NOT `_v`: that is the name this file imports the verdict writer under, further down, and a loop
            # variable at module scope would shadow it. The suite caught it, which is what that rule is for.
            _cv = _value_of("pcb-b-compute", _c)
            check(_cv.startswith("220n"), "B: %s on %s is the 220 nF the module's datasheet asks for" % (_c, _net),
                  "value %r" % _cv, boards={"B"})

# 13. one driver: the inhibit line is made by the panel toggle and read everywhere else. No gate output may sit on it.
for _bd, _stem in (("A", "pcb-a-power"), ("B", "pcb-b-compute")):
    _u = sorted({r for r, _ in B[_bd][0].get("TX_INHIBIT_n", set()) if r.startswith("U")})
    check(not _u, "%s: no device drives TX_INHIBIT_n, the panel toggle is its only source" % _bd, "found %s" % _u, boards={_bd})
_u26 = sorted({pin for r, pin in B["A"][0].get("EMCON_HW", set()) if r == "U26"})
check(set(_u26) <= {"1", "4"}, "A22: EMCON_HW reaches only the AND gates' inputs 1A and 2A, never an output", "U26 pins %s" % _u26, boards={"A"})

# 14. fail safe: with the panel ribbon out, every consumer must read the inhibit line LOW, so each holds it down itself.
for _bd in ("A", "B", "D"):
    _gnd = {r for r, _ in B[_bd][0].get("GND", set())}
    _pull = sorted({r for r, _ in B[_bd][0].get("TX_INHIBIT_n", set()) if r.startswith("R") and r in _gnd})
    check(bool(_pull), "%s: TX_INHIBIT_n is pulled DOWN on this board, so a missing panel inhibits" % _bd, "pull-downs %s" % _pull, boards={_bd})

# 15. the sense: C7 buffers the toggle into EMCON_HW, it does not invert it (both consumer boards silence on LOW).
_u9 = _value_of("pcb-c-display", "U9")
check("1G04" not in _u9 and ("1G34" in _u9 or "buffer" in _u9.lower()), "C7: U9 buffers TX_INHIBIT_n into EMCON_HW rather than inverting it", _u9 or "no value read", boards={"C"})


# 15b. THE PACK'S TWO WIRES ARE A CONNECTOR (16 September 2026). Board P's pack leads are solder lands and
# 12 AWG wire to the XT60 on board E, which is why this set left board P out for as long as it existed and why
# rule SCH-003 had nothing to say about it. A wire is a conductor: what makes it a contract is that both ends
# agree about which conductor carries what, and getting the pack's polarity wrong at the XT60 is the one
# mistake on this kit that destroys a board rather than failing a test.
if "P" in B and B["P"][1] and B["E"][1]:
    _pp = B["P"][1].get(("W_P", "1"), "")
    _pn = B["P"][1].get(("W_N", "1"), "")
    _e2 = B["E"][1].get(("J_BATT", "2"), "")
    _e1 = B["E"][1].get(("J_BATT", "1"), "")
    check(_pp == "PACK_P" and _pn == "PACK_N",
          "P: the pack leads are the pack's own two nets, W_P on the positive and W_N on the return",
          "W_P %r, W_N %r" % (_pp, _pn), boards={"P"})
    check(_e2 == "CELL+" and _e1 == "GND",
          "E: the XT60 carries the pack on pin 2 and the return on pin 1, which is what P's leads land on",
          "J_BATT.2 %r, J_BATT.1 %r" % (_e2, _e1), boards={"E", "P"})
    # The two boards name the same conductor differently and that is correct: the pack board calls its output
    # PACK_P and the dock calls its input CELL+, because each names its own branch. What must be true is that
    # each end is the POSITIVE of the pair on its own board, which is what the two checks above establish, and
    # that neither board has quietly put the return on the conductor the other calls positive.
    check(_pp != "PACK_N" and _e2 != "GND",
          "the pack pair is not crossed between board P's leads and board E's XT60",
          "P positive %r, E pin 2 %r" % (_pp, _e2), boards={"E", "P"})
    _fuse = B["P"][1].get(("F1", "1"), "") or B["P"][1].get(("F1", "2"), "")
    check(bool(_fuse), "P: the pack's blade fuse is on the netlist and carries a net", "F1 %r" % _fuse,
          boards={"P"})

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
        check(not _bad, "%s: %s (%s) is in series with a real pin on both sides" % (_bd, _r, _val), "dead net(s) %s" % _bad, boards={_bd})

# A board whose netlist is not in this tree has not been checked; every contract that names it then reads as a
# 13. A RAIL THAT CROSSES A CONNECTOR IS ONE CONDUCTOR, AND ITS BUDGET IS ONE BUDGET (16 September 2026).
# `+5V_D8` runs from board A's eFuse, out through the mezzanine, into board D's loads. Each board measured its
# own half against the WHOLE budget: A read 2.68 percent against the 2 percent default while D read its half
# against the 3 percent it declares with a reason, so the two halves could sum past the rail's real budget and
# both boards would pass. A rail that appears in more than one board's intent declares what fraction of the
# end-to-end budget THIS board's copper may spend, and the shares must not sum past the budget.
import glob as _glob, json as _json, os as _os
_intents = {}
for _k, _stem in NETS.items():
    for _f in sorted(_glob.glob(_os.path.join(ECAD, _stem + "*", "out", "*-intent.json"))):
        try: _intents[_k] = _json.load(open(_f))
        except ValueError: pass
# A BOARD WHOSE INTENT FILE IS NOT IN THIS TREE HAS DECLARED NOTHING HERE, and that is an absent input rather
# than an absent declaration (17 September 2026). The intent file is written by the schematic generator into
# the project's untracked out/, so on a tree that holds the netlists but not the intent files every shared
# rail reads "no board declares a share": the same run that reads 72 of 72 with them read 64 with 7 rails
# unsplit without them, and wrote that over the fuller reading.
_NO_INTENT = sorted(k for k in NETS if k not in _intents)
if _NO_INTENT:
    print("check_contracts: no intent file in this tree for %s, so what those boards declare about a shared "
          "rail cannot be read here" % ", ".join(_NO_INTENT))
UNSPLIT = []
_shared = {}
for _k, _it in _intents.items():
    for _net, _r in (_it.get("rails") or {}).items():
        _shared.setdefault(_net, {})[_k] = _r
for _net, _by in sorted(_shared.items()):
    if len(_by) < 2 or _net == "GND": continue
    _budgets = {k: float(r.get("budget", 0.02)) for k, r in _by.items()}
    _shares = {k: r.get("share") for k, r in _by.items()}
    _named = ", ".join("%s %.1f%%" % (k, 100 * float(v)) for k, v in sorted(_shares.items()) if v)
    if not all(_shares.values()):
        # UNSPLIT IS AN OPEN QUESTION, NOT A FAILED CONTRACT (16 September 2026). Six rails cross a connector
        # with no share declared, and declaring one is an engineering judgement about where the drop is
        # allowed to fall, not a fact the tree already holds: asserting 50/50 for each of them would be a
        # number with no basis, which is what this registry refuses everywhere else. So an unsplit rail makes
        # the contract set INCONCLUSIVE, the same way an absent netlist does, and it is named every time until
        # someone splits it. What is NOT tolerated is shares that are declared and sum past the budget.
        UNSPLIT.append("%s (%s): %s" % (_net, "/".join(sorted(_by)), "declared %s" % _named if _named else "no board declares a share"))
        print("OPEN  rail %s crosses %s and its end-to-end budget is not split between them (%s)"
              % (_net, "/".join(sorted(_by)), _named or "none declared"))
    if all(_shares.values()):
        _tot = sum(float(v) for v in _shares.values()); _bud = min(_budgets.values())
        check(_tot <= _bud + 1e-9,
              "rail %s: the shares sum to %.1f%% within the %.1f%% the rail declares" % (_net, 100 * _tot, 100 * _bud),
              boards=set(_by))

# FAIL of the contract, which is a claim about the design. It is a claim about the tree. On a rented box where
# only one board has been regenerated, P3's finish printed eleven contract FAILs naming A, and A had simply
# never been generated there (11 September 2026). A missing input is INCONCLUSIVE, and it still blocks.
if MISSING:
    print("\n%d board netlist(s) absent from this tree: %s. Every contract that names one of them was judged "
          "against nothing, so this is INCONCLUSIVE and not a verdict on the design; generate those boards "
          "and run it again." % (len(MISSING), ", ".join(MISSING)))
print("\n%d contract(s) FAILED" % len(fails) if fails else ("\nALL CONTRACTS PASS" if not MISSING else ""))
import os as _osv
sys.path.insert(0, _osv.path.dirname(_osv.path.abspath(__file__)))
import verdict as _v


def _richer_on_disk(tool, missing_now=None):
    """Was the verdict already on disk taken with MORE input than this run has?

    A READING TAKEN WITH LESS INPUT NEVER REPLACES ONE TAKEN WITH MORE (16 September 2026). The contracts are
    judged from the netlists the chains write into each project's untracked out/, so on the runner every board
    is absent; `final_gate.py` runs this check to print one summary line, and that incidental run wrote
    INCONCLUSIVE over board C's contract PASS taken on the box an hour earlier, and over the set's own reading.
    Two rules on six boards moved backwards because of where the command was typed.

    It is deliberately not "never overwrite an INCONCLUSIVE": a tree with the same input or more writes its
    answer whatever that answer is, so a real regression is still recorded, and a tree with no prior verdict
    writes one, so a fresh checkout still says what it found."""
    import json as _j, os as _o
    d = _v_out_dir()
    try: rec = _j.load(open(_o.path.join(d, "%s.verdict.json" % tool), encoding="utf-8"))
    except Exception: return False                  # nothing on disk: this run is the only reading there is
    if missing_now is None:                         # a per-board verdict: was it taken with that netlist?
        return "absent from this tree" not in (rec.get("note") or "")
    was = (rec.get("counts") or {}).get("missing_boards")
    if was is None: return False
    return (was + (rec.get("counts") or {}).get("boards_without_intent", 0)) < missing_now


def _v_out_dir():
    return os.environ.get("VERDICT_DIR") or os.path.join(os.getcwd(), "out")


# A contract set that checked nothing has found nothing wrong, which is not the same as agreement.
# A PER-BOARD VERDICT BESIDE THE SET ONE (16 September 2026), the pattern final_gate already uses. The set
# verdict is what the contracts as a whole say and it still blocks; these say what each board's own contracts
# say, so a board is no longer reported as failing a rule because of a defect on a board it does not touch.
# BOARD E5 HAS NO NETLIST BY CONSTRUCTION AND ITS CONTRACT IS JUDGED, 17 September 2026. The dock block has
# no schematic: gen_pcb_e5.py reads board A's BOARD FILE and puts a target under each spring pin carrying that
# pin's net. This file wrote E5 an INCONCLUSIVE saying so, which was honest and left the one board of the set
# whose interface is blind-mate with no check on its pin map at all. `block_contract.py` judges it between the
# two BOARDS, by position, and writes check_contracts_e5 itself. Nothing is written for E5 here, so the two
# cannot overwrite each other.
for _bd in sorted(set(list(per_board) + list(B))):
    if _bd == "E5": continue          # block_contract.py writes this board's verdict
    # A HOST THAT CANNOT SEE THE NETLIST HAS NOTHING TO SAY ABOUT IT, and saying it anyway DESTROYS the
    # reading taken where the netlist existed (16 September 2026). The netlists are written by the chains into
    # each project's untracked out/, so on the runner every board is absent; one incidental run of this check
    # from `final_gate.py` overwrote board C's contract PASS, taken on the box an hour earlier, with an
    # INCONCLUSIVE about this host. Absence is already INCONCLUSIVE to the readiness computation ("absence is
    # never a pass"), so writing nothing gives the same answer on a fresh tree and keeps the evidence on a
    # tree that has some. The missing board is named on stdout, which is where a report belongs.
    _r = per_board.get(_bd) or {"pass": 0, "fail": [], "unjudged": []}
    _u = len(_r.get("unjudged") or [])
    # THE GUARD COVERS BOTH ENDS NOW. A board is left alone when its OWN netlist is absent, and also when any
    # contract of its own could not be judged because the board at the other end is absent: in both cases this
    # run has less input than whatever is already on disk, and less input never replaces more.
    if (_bd in MISSING or _u) and _richer_on_disk("check_contracts_%s" % _bd.lower()):
        print("check_contracts: %s has %s in this tree and the verdict on disk was taken with them, so it is "
              "left as it stands" % (_bd, "no netlist" if _bd in MISSING else
                                     "%d contract(s) that name an absent board" % _u))
        continue
    _n = _r["pass"] + len(_r["fail"])
    _v.write("check_contracts_%s" % _bd.lower(),
             _v.INCONCLUSIVE if (not _n or _bd in MISSING or _u) else (_v.PASS if not _r["fail"] else _v.FAIL),
             counts={"fail": len(_r["fail"]), "pass": _r["pass"], "unjudged": _u}, denominator=_n + _u,
             evidence=(_r["fail"] + ["unjudged, the other board is absent: " + t for t in (_r.get("unjudged") or [])])[:20],
             inputs={"boards": ",".join(sorted(B))},
             note=("this board's netlist is absent from this tree" if _bd in MISSING else
                   "no contract of this set names this board" if not _n and not _u else
                   "%d of this board's contracts name a board absent from this tree and were not judged" % _u
                   if _u else
                   "the contracts that name this board; the set's own verdict is check_contracts"),
             quiet=True)
if (not checked or MISSING or _NO_INTENT) and _richer_on_disk("check_contracts", len(MISSING) + len(_NO_INTENT)):
    # The same rule for the SET verdict, and it is stricter, because of what this verdict MEANS: the seven
    # boards agree with each other. That cannot be read with a board absent, and an INCONCLUSIVE written from
    # here replaces the set's real reading with a fact about this host. The runner has no netlist for any
    # board (the chains write them into each project's untracked out/), so one incidental run from
    # `final_gate.py` demoted the whole set. Absence is INCONCLUSIVE to the readiness computation already.
    print("check_contracts: %s, so the set was not judged here and its verdict is left as it stands"
          % ("no netlist in this tree" if not checked else "no netlist for " + ", ".join(MISSING)))
    sys.exit(3)
sys.exit(_v.write("check_contracts",
                  _v.INCONCLUSIVE if (not checked or MISSING or (UNSPLIT and not fails)) else (_v.PASS if not fails else _v.FAIL),
                  counts={"fail": len(fails), "pass": len(checked) - len(fails), "missing_boards": len(MISSING),
                          # THE CONTRACTS THAT EXIST AND COULD NOT BE JUDGED ARE COUNTED (17 September 2026).
                          # They are not passes and they are not failures, and leaving them out of the
                          # denominator would make "0 of 0" out of a set where most of the work is simply not
                          # readable on this host: the reader needs to see that there are contracts and that
                          # this run could not reach them.
                          "unjudged": len(unjudged),
                          "boards_without_intent": len(_NO_INTENT), "rails_unsplit": len(UNSPLIT)},
                  denominator=len(checked) + len(unjudged),
                  evidence=(["netlist absent: " + k for k in MISSING] + ["rail unsplit: " + u for u in UNSPLIT]
                            + fails + ["unjudged, a board it names is absent: " + t for t in unjudged[:8]]),
                  inputs={"boards": ",".join(sorted(B))},
                  note=("no contract was evaluated (%d of the set's contracts name a board absent from this "
                        "tree)" % len(unjudged) if not checked else
                        ("%s absent from this tree, so nothing that names them was judged" % ", ".join(MISSING)) if MISSING else
                        ("%d rail(s) cross a connector with no share of their budget declared" % len(UNSPLIT)) if UNSPLIT else "")))
