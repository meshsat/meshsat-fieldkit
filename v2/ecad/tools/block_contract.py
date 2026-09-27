#!/usr/bin/env python3
"""The dock block against the board whose pins land on it (rule SCH-003 for board E5, MESHSAT-862, 17 Sep 2026; and
INT-001 for board E5 since 27 September 2026, MESHSAT-1357, stream w4r).

Board E5 is the one board of the set with no schematic and no netlist. `gen_pcb_e5.py` reads BOARD A's board
file, finds the spring-pin connector J_DOCK, and puts a flat target under each pin carrying that pin's net,
named `<net>_P<pin>`. So E5's contract is not between two netlists, which is why `check_contracts.py` has
declared it unjudgeable since 16 September and written INCONCLUSIVE: it is between E5's board file, which IS
E5's design, and board A's design, and that is what this judges.

It matters because it is the only thing standing between a wrong pin map and a kit that does not work: the
block is a blind-mate interface, the pins are hidden when it is assembled, and a target carrying the wrong
net is invisible until 9 A of pack current is on the wrong conductor. And board A is regenerated constantly,
so the question is live: a J_DOCK that gains a pin or renames a net leaves E5 describing a board that no
longer exists.

BOARD A IS READ AT ITS CURRENT CANDIDATE, ITS NETLIST, NOT ITS BOARD FILE (27 September 2026, MESHSAT-1357, stream
w4r). Until then the pin map came off board A's BOARD FILE, and board A's committed layout predates its current
netlist (its SCH-002 is not a current PASS): after EQ-16 (SC-55) the netlist puts J_DOCK pins 1 to 4 on GND and adds
the VIN_RAW power pins J_VR1 to J_VR4 and their returns J_VN1 to J_VN4, while the board file still carries VIN_RAW on
pins 1 to 4 and no J_VR or J_VN. E5 was generated from that same board file, so the two agreed and the reading said
PASS 33 of 33 about a board A that is no longer the design. A reading of a layout that is not the candidate's can
never be current evidence either (rules_status._bound, OTHER_BOARD). So the NETS come from board A's declared phase
netlist, which the reading records by sha and by content (rules_status binds it while it is board A's current
netlist), and the GEOMETRY comes from the land that netlist names for J_DOCK (meshsat.pretty), mounted the way board
A's placement generator mounts it (DOCK_MOUNT below: the underside, rotation 0). Board A's board file is not read.

What is checked, the signal half geometric and never from a name:
  1. every signal target on E5 has a J_DOCK pad above it, at the same offset from its own connector origin (the
     land from the footprint board A's netlist names for J_DOCK, mounted as DOCK_MOUNT says);
  2. the net that target carries is the net board A's netlist gives that pin, with the pin number appended;
  3. every wire land carries the net of the target of the same pad number (the wire goes straight down);
  4. the power targets carry the pack node and its return, and the pre-charge target carries the pack node;
  5. every blind-mate power pin board A's netlist carries (J_CP, J_CN, J_PRE, J_VR and J_VN, the refs of IF-AE-DOCK in
     pcb_interfaces.yaml) has an E5 target of its kind, as many targets as pins (T_CP under J_CP, T_PRE under
     J_PRE1), and a VIN_RAW pin's target carries the net board A gives that pin. Where the power targets sit is not
     judged here: E5 draws them at fixed places and board A's placement puts its pins over them (a layout property).

Usage: block_contract.py <e5 board.kicad_pcb> [<board A netlist .net> | <board A .kicad_pcb>]
The second argument is optional: by default board A's declared phase netlist in this tree (phase_artefacts.netlist).
A board A BOARD FILE, the form gate_sweep.sh passes, names the phase directory whose out/<stem>.net is read; the
board file itself is not read, and the run says so."""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v
import phase_artefacts as _pa

NAME = "check_contracts_e5"
SIGNAL_TARGET = "T_SIG"
WIRE_LAND = "L_SIG"
CONNECTOR = "J_DOCK"
PACK, RETURN = "CELL+", "CELL_N"
# THE MOUNT OF J_DOCK ON BOARD A, as board A's placement generator states it: gen_pcb_a3.py FIXED["J_DOCK"] =
# (-76, -70, 0), rotation 0, and J_DOCK in BACK, the underside, placed there by `place()` exactly as below (SetPosition,
# Add, Flip(position, False), SetOrientationDegrees). tests/test_per_board_contract_verdict.py parses that table and
# holds this equal to it, so a change of the connector's side or rotation fails the suite before a reading is taken
# with the old mount. The land itself (which pad sits where) is the footprint board A's netlist names.
DOCK_MOUNT = {"back": True, "rotation": 0.0}
# Board A's blind-mate power pins by kind, and the prefix of the E5 targets that take them (IF-AE-DOCK).
POWER_KINDS = ("CP", "CN", "PRE", "VR", "VN")
KICAD_FOOTPRINTS = "/usr/share/kicad/footprints"


# ---------------------------------------------------------------------------------------------------------- inputs
def a_netlist_for(arg=None):
    """(board A's netlist path, note): the netlist named on the command line, the phase directory's netlist of a board
    A board file named there (gate_sweep.sh's form), or board A's declared phase netlist in this tree."""
    if arg and str(arg).endswith(".net"):
        return arg, ""
    if arg and str(arg).endswith(".kicad_pcb"):
        stem = os.path.basename(str(arg))[:-len(".kicad_pcb")]
        p = os.path.join(os.path.dirname(os.path.abspath(str(arg))), "out", stem + ".net")
        return p, ("board A's pin map is read from its netlist %s, not from the board file given (%s), which is not "
                   "read" % (_pa.rel(p), _pa.rel(arg)))
    return _pa.netlist("a"), ""


def _sexp(text):
    """A KiCad s-expression as nested lists of atoms (strings unquoted). Parsed, never grepped."""
    tok = re.compile(r'\(|\)|"((?:[^"\\]|\\.)*)"|([^\s()"]+)')
    stack, cur = [], []
    for m in tok.finditer(text):
        t = m.group(0)
        if t == "(":
            stack.append(cur); cur = []
        elif t == ")":
            done = cur; cur = stack.pop() if stack else []; cur.append(done)
        elif m.group(1) is not None:
            cur.append(m.group(1).replace('\\"', '"'))
        else:
            cur.append(m.group(2))
    return cur


def _kv(node, key):
    for x in node[1:] if isinstance(node, list) else []:
        if isinstance(x, list) and x and x[0] == key: return x
    return None


def read_netlist(raw):
    """{"footprint": {ref: fpid}, "pins": {ref: {pin: net}}} of a KiCad netlist's bytes. Every net is read, the last
    one included (the look-ahead KiCad 9's closing parentheses defeat, R4T-F1, cannot arise in a parse)."""
    tree = _sexp(raw.decode("utf-8", "replace"))
    root = tree[0] if tree and isinstance(tree[0], list) else tree
    fps, pins = {}, {}
    for sec in (root[1:] if isinstance(root, list) else []):
        if not (isinstance(sec, list) and sec): continue
        if sec[0] == "components":
            for c in sec[1:]:
                if not (isinstance(c, list) and c and c[0] == "comp"): continue
                ref, fp = _kv(c, "ref"), _kv(c, "footprint")
                if ref and len(ref) > 1: fps[ref[1]] = fp[1] if fp and len(fp) > 1 else ""
        elif sec[0] == "nets":
            for n in sec[1:]:
                if not (isinstance(n, list) and n and n[0] == "net"): continue
                name = str((_kv(n, "name") or [None, ""])[1]).lstrip("/")
                for x in n[1:]:
                    if isinstance(x, list) and x and x[0] == "node":
                        r, p = _kv(x, "ref"), _kv(x, "pin")
                        if r and p and len(r) > 1 and len(p) > 1: pins.setdefault(r[1], {})[p[1]] = name
    return {"footprint": fps, "pins": pins}


def land_file(fpid):
    """The library file of a footprint id (`meshsat:PogoPins_2x6` is this tree's meshsat.pretty), or None."""
    lib, _s, name = str(fpid or "").partition(":")
    if not (lib and name): return None
    d = os.path.join(os.path.dirname(HERE), "meshsat.pretty") if lib == "meshsat" else \
        os.path.join(KICAD_FOOTPRINTS, lib + ".pretty")
    p = os.path.join(d, name + ".kicad_mod")
    return p if os.path.exists(p) else None


def inputs_for(e5_path, a_net, land=None):
    """What a reading records: E5's board file (E5's design: it has no schematic) by sha, board A's netlist by sha and
    by content, and the J_DOCK land by sha. rules_status binds the first to E5's candidate, the second to board A's
    current netlist (_other_boards_artefacts) and dates the third as a configuration input. Nothing else is read."""
    inp = {"board": _pa.record(e5_path, content=False) or e5_path,
           "board_a_netlist": _pa.record(a_net) or a_net}
    if land: inp["dock_land"] = _pa.record(land, content=False) or land
    return inp


def decides():
    """The rules this reading decides, read from the coverage map: every rule whose verdict is check_contracts_<letter>
    (verdict._rules_for_tool), and every rule that names this verdict for one board alone (`verification.
    verdict_by_board`: INT-001 on E5 since 27 September 2026). The verdict then carries each rule's digest, so a change
    of either rule is seen rule by rule and a registry edit elsewhere does not stale it."""
    out = set(_v._rules_for_tool(NAME))
    try:
        import yaml            # PyYAML itself, not rules_lib: a registry-tool edit must not stale this reading's code
        with open(os.path.join(HERE, "pcb_rules_coverage.yaml"), encoding="utf-8") as f:
            cov = (yaml.safe_load(f) or {}).get("coverage", {})
        for rid, c in cov.items():
            per = (((c or {}).get("verification") or {}).get("verdict_by_board")) or {}
            for letter, raw in (per.items() if isinstance(per, dict) else ()):
                if NAME in [n.strip().replace("<letter>", str(letter)) for n in str(raw or "").split(",")]:
                    out.add(rid)
    except BaseException:
        pass              # as verdict.py: a host that cannot read the map still writes its reading
    return sorted(out)


# ----------------------------------------------------------------------------------------------------------- judge
def _key(pad, origin):
    """A pad's position relative to its own footprint origin, in hundredths of a millimetre, as the generator
    matched them. The connector is on board A's underside and the block is the right way up; both offsets are taken
    after each part's own mount, so the match is between two offsets and nothing else."""
    q = pad.GetPosition()
    return (round((q.x - origin.x) / 1e4), round((q.y - origin.y) / 1e4))


def dock_offsets(fpid):
    """({offset: pin number} of J_DOCK's land mounted as DOCK_MOUNT says, land file) or (None, why)."""
    import pcbnew
    lf = land_file(fpid)
    if not lf: return None, "the land %s board A's netlist names for %s is not in this tree's libraries" % (fpid, CONNECTOR)
    fp = pcbnew.FootprintLoad(os.path.dirname(lf), os.path.basename(lf)[:-len(".kicad_mod")])
    if fp is None: return None, "KiCad could not load the land %s (%s)" % (fpid, _pa.rel(lf))
    b = pcbnew.BOARD()
    at = pcbnew.VECTOR2I(0, 0)
    fp.SetPosition(at); b.Add(fp)
    if DOCK_MOUNT["back"]: fp.Flip(at, False)
    fp.SetOrientationDegrees(DOCK_MOUNT["rotation"])
    o = fp.GetPosition()
    out = {}
    for p in fp.Pads():
        try: out[_key(p, o)] = int(p.GetNumber())
        except ValueError: continue          # an unnumbered pad is no pin
    return (out, lf) if out else (None, "the land %s carries no numbered pad" % fpid)


def judge(e5_path, a_net):
    """({checked, fail, land}, None) or (None, why the block could not be judged)."""
    import pcbnew
    out = {"checked": [], "fail": [], "land": None}
    def ok(t): out["checked"].append(t)
    def bad(t): out["checked"].append(t); out["fail"].append(t)

    a = read_netlist(open(a_net, "rb").read())
    fpid = a["footprint"].get(CONNECTOR)
    if fpid is None:
        return None, "board A's netlist has no %s: the block's whole pin map comes from that connector" % CONNECTOR
    offs, lf = dock_offsets(fpid)
    if offs is None: return None, lf
    out["land"] = lf
    pin_net = a["pins"].get(CONNECTOR) or {}
    above = {}
    for k, pin in offs.items():
        net = pin_net.get(str(pin), "")
        if not net or net.startswith("unconnected-"): net = "SPARE"
        above[k] = (pin, net)

    e5 = pcbnew.LoadBoard(e5_path)
    tgt = e5.FindFootprintByReference(SIGNAL_TARGET)
    land = e5.FindFootprintByReference(WIRE_LAND)
    if tgt is None: return None, "board E5 has no %s" % SIGNAL_TARGET
    tp = tgt.GetPosition()
    seen = {}
    for pad in tgt.Pads():
        num = int(pad.GetNumber()); k = _key(pad, tp)
        got = pad.GetNetname().lstrip("/")
        if k not in above:
            bad("target %d of %s has no %s pad above it at %s" % (num, SIGNAL_TARGET, CONNECTOR, k)); continue
        pin, net = above[k]
        want = "%s_P%d" % (net, pin)
        seen[num] = want
        if got == want: ok("target %d carries %s, which is %s pin %d" % (num, got, CONNECTOR, pin))
        else: bad("target %d carries %r and the pin above it is %s pin %d, on %s in board A's netlist, so it must "
                  "carry %r" % (num, got, CONNECTOR, pin, net, want))
    if land is not None:
        for pad in land.Pads():
            num = int(pad.GetNumber()); got = pad.GetNetname().lstrip("/")
            want = seen.get(num)
            if want is None: bad("wire land %d has no target of the same number" % num)
            elif got == want: ok("wire land %d carries %s, the net of the pin above target %d" % (num, got, num))
            else: bad("wire land %d carries %r and must carry %r, the net of the pin above target %d: the wire would "
                      "leave on another net" % (num, got, want, num))
    else:
        bad("board E5 has no %s: the twelve wires to the strip have nowhere to land" % WIRE_LAND)

    power = {"CP": PACK, "CN": RETURN, "PRE": PACK}
    targets = {K: [] for K in POWER_KINDS}
    for fp in e5.GetFootprints():
        ref = fp.GetReference()
        m = re.match(r"^T_(%s)\d*$" % "|".join(POWER_KINDS), ref)
        if not m: continue
        targets[m.group(1)].append(fp)
        want = power.get(m.group(1))
        if want is None: continue
        nets = {p.GetNetname().lstrip("/") for p in fp.Pads()}
        if nets == {want}: ok("%s carries %s" % (ref, want))
        else: bad("%s carries %s and must carry %s" % (ref, ", ".join(sorted(nets)) or "nothing", want))
    if not targets["CP"]:
        bad("board E5 has no pack-node target")
    # 5. EVERY BLIND-MATE POWER PIN OF BOARD A HAS A TARGET (27 September 2026): board A's netlist says which pins the
    # stack lowers onto the block, so a pin it gains (EQ-16's J_VR and J_VN) and E5 does not carry is refused here.
    for K in POWER_KINDS:
        pins = sorted((r for r in a["footprint"] if re.fullmatch(r"J_%s\d+" % K, r)), key=lambda r: int(r[len(K) + 2:]))
        tg = sorted(fp.GetReference() for fp in targets[K])
        if not pins and not tg: continue
        if len(tg) == len(pins):
            ok("board A's %d J_%s pin(s) %s land on %d T_%s target(s) of E5" % (len(pins), K, ",".join(pins), len(tg), K))
        else:
            bad("board A's netlist carries %d J_%s pin(s)%s and E5 carries %d T_%s target(s)%s: %s"
                % (len(pins), K, (" (" + ", ".join(pins) + ")") if pins else "", len(tg), K,
                   (" (" + ", ".join(tg) + ")") if tg else "",
                   "a pin the stack lowers onto nothing" if len(pins) > len(tg) else "a target no pin of board A lands on"))
        if K == "VR" and pins and tg:
            want = {n for r in pins for n in (a["pins"].get(r) or {}).values() if n and not n.startswith("unconnected-")}
            for fp in targets[K]:
                nets = {p.GetNetname().lstrip("/") for p in fp.Pads()}
                if len(want) == 1 and nets == want: ok("%s carries %s, board A's net on its J_VR pins" % (fp.GetReference(), next(iter(want))))
                else: bad("%s carries %s and board A's J_VR pins are on %s" % (fp.GetReference(), ", ".join(sorted(nets)) or "nothing",
                                                                            ", ".join(sorted(want)) or "nothing"))
    return out, None


# ------------------------------------------------------------------------------------------------------------ main
def main(argv):
    if not argv: print(__doc__); return _v.USAGE
    e5 = argv[0]
    a_net, how = a_netlist_for(argv[1] if len(argv) > 1 else None)
    if how: print("block_contract: %s" % how)
    out_dir = os.environ.get("VERDICT_DIR") or os.path.join(os.path.dirname(os.path.abspath(e5)), "out")
    rules = decides()
    if not a_net or not os.path.exists(a_net):
        print("block_contract: board A's netlist is not in this tree, so the block's pin map cannot be compared with it")
        return _v.write(NAME, _v.INCONCLUSIVE, denominator=0, counts={"fail": 0, "pass": 0},
                        inputs={"board": _pa.record(e5, content=False) or e5}, out_dir=out_dir, rules=rules,
                        missing_input="board A's netlist (%s)" % (_pa.rel(a_net) if a_net else "no declared phase"),
                        note="board A's netlist is not in this tree and the block's every net comes from it")
    try:
        res, why = judge(e5, a_net)
    except ImportError as e:
        # A HOST WITHOUT KiCad WRITES THIS RULE'S OWN VERDICT, declaring the absence, rather than a crash under the tool's
        # name that no rule reads (27 September 2026): rules_status prefers a reading that had its input over this one.
        print("block_contract: KiCad's pcbnew is not importable here (%s)" % e)
        return _v.write(NAME, _v.INCONCLUSIVE, denominator=0, counts={"fail": 0, "pass": 0},
                        inputs=inputs_for(e5, a_net), out_dir=out_dir, rules=rules,
                        missing_input="KiCad's pcbnew, which reads the block's board file and the dock land",
                        note="not judged on this host: the block's targets and the J_DOCK land are read with pcbnew")
    if res is None:
        print("block_contract: %s" % why)
        return _v.write(NAME, _v.INCONCLUSIVE, denominator=0, counts={"fail": 0, "pass": 0},
                        inputs=inputs_for(e5, a_net), out_dir=out_dir, note=why, rules=rules)
    for t in res["checked"]: print(("FAIL  " if t in res["fail"] else "PASS  ") + t)
    n = len(res["checked"]); f = len(res["fail"])
    print("block_contract: %d of %d checks pass against board A's netlist %s" % (n - f, n, _pa.rel(a_net)))
    return _v.write(NAME, _v.PASS if not f else _v.FAIL,
                    counts={"fail": f, "pass": n - f}, denominator=n, evidence=res["fail"][:20],
                    inputs=inputs_for(e5, a_net, res["land"]), out_dir=out_dir, rules=rules,
                    note="the dock block against board A's current netlist: the signal targets matched by position "
                         "under the J_DOCK land mounted as board A mounts it, the power targets by kind; board E5 "
                         "has no netlist, its board file is its design, and board A's board file is not read")


if __name__ == "__main__":
    # EVERY GATE LEAVES A READING WHEN IT RAISES (18 September 2026). The thirteen one-line entries of this
    # morning were the gates a crash had already cost a verdict; these are the rest of the deciding gates in
    # the coverage map, guarded the same way, so a rule whose tool raised reads INCONCLUSIVE naming the
    # exception rather than 'no verdict', which the registry reads as nobody having looked.
    sys.exit(_v.guard("block_contract", main, sys.argv[1:]))
