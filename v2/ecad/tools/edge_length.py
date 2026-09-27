#!/usr/bin/env python3
"""Which nets are long enough, for their own edges, to behave as transmission lines (rule SI-001,
MESHSAT-862, 16 September 2026).

SI-001 asks for exactly this and has had nothing: "every net is classified by whether it behaves as a
transmission line, from its rise time, propagation delay and electrical length, and its topology and
termination follow from that classification, not from its bit rate or clock frequency". Its coverage note read
"no net in this project has ever been classified by edge rate" and that is now half wrong and half right: every
net IS classified, by spectral content, with 413 declarations across the seven boards, and what was missing is
the arithmetic that turns a class into a LENGTH.

WHAT IT COMPUTES, from the board and from declarations that carry their basis:
  * the propagation delay of the layer each segment sits on, from the board's own stackup: an outer layer is a
    microstrip and sees an effective permittivity of about (er + 1) / 2 plus the fringing term, an inner layer
    is a stripline and sees er itself. t_pd = sqrt(er_eff) / 299.792 mm per picosecond;
  * the RISE TIME, declared in `boards/<letter>.json`. A rise time is a property of the DRIVER, not of a class:
    board A's HIGH_SPEED_DIGITAL nets are gate drives whose edges are tens of nanoseconds, while board B's are
    a memory bus. So the first place looked at is the `signal_classes` entry itself, beside the basis that
    already says what the net is (`rise_ns` on the entry); a board-wide `rise_ns` map by class name is the
    fall-back for a board where one number is honestly true of the whole class. Nothing is assumed: a net whose
    class carries no declared edge is COUNTED AND NAMED, never estimated, because the whole point of this rule
    is that the edge decides and an edge nobody wrote down decides nothing;
  * the CRITICAL LENGTH, l = t_r / (k * t_pd), where k is the criterion. The common engineering readings are
    k = 6 (conservative, a line is "electrically long" past a sixth of the rise distance) and k = 2 (the
    lumped limit). The board declares `critical_k` with its reason. NO STANDARD IN THIS TREE STATES A VALUE
    FOR k, and one document now calibrates it: ECSS-E-HB-20-07A section 6.1.2.3, transcribed in
    v2/vendor/standards/, works a real case where a 35 mm clock track with a 200 ps edge failed a radiated
    emission test at 1.4 GHz. That track is one rise distance long (t_r / t_pd = 34.5 mm on its microstrip),
    which is k = 1, and the handbook calls it a textbook radiator. So k = 1 is measured to be too long, k = 2
    is half of a known failure, and k = 6 puts a judged net at a sixth of it. The number is still this
    project's choice; what the handbook removes is the pretence that it was chosen against nothing.

WHAT A NET PAST ITS CRITICAL LENGTH MEANS, which is the half this rule got wrong on its first day. Being a
transmission line is not a defect: at a 200 ps edge every net on a 285 mm board is one, and a rule that fails
them all says only that physics holds. What is a defect is an UNCONTROLLED and UNTERMINATED transmission line.
So a net past its critical length is asked what it has, in the order the handbook's own bullets give
(6.1.2.5.2: "Use of tracks with controlled characteristic impedance: microstrips or striplines; matched
terminations", and its example's fix is a 1 kOhm series resistor, not a shorter track):
  * CONTROLLED: the net carries an impedance target, so it was designed as a transmission line;
  * SERIES: a resistor of 10 to 150 ohm sits on the net with its other end on another signal net, which is
    what a source termination looks like from the board alone. This is a SCREEN and says so: the board file
    knows neither which end drives nor what the receiver is, so a damping resistor in a filter counts here too
    and the list is printed for reading rather than trusted as proof;
  * DECLARED: the board names the net in `edge_allow` with a reason, the erc-allow idiom;
  * and anything left is the finding: a long, fast, unterminated net with no impedance target.

Then every signal net's routed length is measured and compared with the critical length for ITS class. A net
past it is reported with both numbers: that is the list SI-001 asks for, and it is the list that says which
lines want a termination or an impedance target rather than a width.

TWO READINGS SINCE 26 SEPTEMBER 2026 (MESHSAT-1357). SI-001 is verified at the SCHEMATIC phase and its registry
evidence scope is the schematic and the stackup, so its reading is the TABLE the rule's acceptance asks for, taken
from the committed netlist, the held documents and the declared stack (see schematic_table below): per class, the
driver edge rate and the document that states it (UNDECIDED where no held document does), the critical length on
the declared stack, and whether the netlist carries the coupling or termination the class needs. That reading is
the `edge_length` verdict. The ROUTED comparison above is the layout gate's and writes `edge_length_routed`; a
board run writes the schematic table as well when the netlist it was placed from sits beside it.

Usage: edge_length.py --netlist <netlist.net> [--out-dir DIR] [--json]   the schematic table (verdict edge_length)
       edge_length.py <board.kicad_pcb> [--json]         the routed comparison (verdict edge_length_routed), and the
                                                         table from out/<stem>.net beside the board when there is one
"""
import os, sys, json, math, re, hashlib, fnmatch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v
import boardtable as _bt

C_MM_PER_PS = 0.299792458    # the speed of light, millimetres per picosecond


def t_pd_ps_per_mm(er, outer):
    """Propagation delay on this layer. A microstrip's field is part air, a stripline's is all laminate."""
    if not er: return None
    er_eff = (er + 1.0) / 2.0 + 0.04 if outer else er     # the 0.04 is the usual fringing allowance
    return math.sqrt(er_eff) / C_MM_PER_PS


def routed_main(a):
    """The ROUTED comparison, the layout gate's half of SI-001 (verdict edge_length_routed): every signal net's
    routed length on the board file against the critical length of its class. See the module docstring."""
    if not a: print(__doc__); return _v.USAGE
    path = a[0]
    import pcbnew, intent, signalnets
    import impedance_check as _imp
    mm = lambda v: v / 1e6
    b = pcbnew.LoadBoard(path)
    it = intent.load(path) or {}
    letter = _bt.letter_for(path)
    rise = _bt.value(letter, "rise_ns") or {}
    k = _bt.value(letter, "critical_k")
    out_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "out")
    stack = _imp.read_stackup(path)
    outer = {pcbnew.F_Cu, pcbnew.B_Cu}
    ers = [e for (_n, kind, _t, e) in stack if kind in ("prepreg", "core") and e]
    er = (sum(ers) / len(ers)) if ers else None
    _entries_with_rise = [e for e in (_bt.value(letter, "signal_classes", []) or []) if e.get("rise_ns")]
    if (not rise and not _entries_with_rise) or not k or er is None:
        missing = [w for w, v in (("rise_ns anywhere", rise or _entries_with_rise), ("critical_k", k),
                                  ("a stackup with epsilon_r", er)) if not v]
        print("edge_length: not judged: this board declares %s" % ", ".join("no " + m for m in missing))
        return _v.write("edge_length_routed", _v.INCONCLUSIVE, denominator=0, inputs={"board": path},
                        counts={"missing": len(missing)},
                        note="this board declares %s, and an edge nobody wrote down decides nothing"
                             % ", ".join("no " + m for m in missing), out_dir=out_dir)

    try:
        import signal_class as _sc
        targets = {n for n, v in (it.get("pair_classes") or {}).items() if v}
        cls = _sc.classify(b, path, targets, None)[0]
    except Exception:
        cls = {}
        targets = set()
    # every net whose own class carries an impedance target, read from the project file the board is judged with
    # An impedance target is a property of the net's CLASS, and the class assignment lives in the project file
    # beside the board, which is also where impedance_check reads it (KiCad's Python exposes no net class).
    cls_target = {}
    try:
        import netclass as _nc
        _pro = os.path.splitext(path)[0] + ".kicad_pro"
        _assign = json.load(open(_pro)).get("net_settings", {}).get("netclass_assignments", {}) if os.path.exists(_pro) else {}
        for _net in list(_assign):
            _klass = _nc.class_of(_assign, _net)
            if _klass and _klass in targets: cls_target[str(_net).lstrip("/")] = _klass
    except Exception:
        pass
    # the per-entry rise time, matched the way signal_class matches: a shell glob over the net name
    import fnmatch
    entries = [e for e in (_bt.value(letter, "signal_classes", []) or []) if e.get("rise_ns")]

    def rise_for(net, klass):
        n = net.lstrip("/")
        for e in entries:
            if fnmatch.fnmatch(n, e["pattern"]): return e["rise_ns"], e["pattern"]
        return rise.get(klass), klass
    signals, _ = signalnets.classify(b, path, (it.get("rails") or {}).keys())
    # WHAT A LONG NET HAS. Read from the board, once, because a per-net walk over every footprint is quadratic
    # on board B's 951.
    _rails = {r.lstrip("/") for r in (it.get("rails") or {})}
    def _is_rail(nm):
        nm = (nm or "").lstrip("/")
        return (not nm) or nm.startswith("+") or nm in _rails or nm.upper() in ("GND", "GNDA", "AGND", "GND_V")
    def _ohms(v):
        v = (v or "").strip().upper().replace(" ", "")
        m2 = __import__("re").match(r"^(\d+(?:\.\d+)?)(R|K|M)?$", v.replace("OHM", "").replace("\u03a9", ""))
        if not m2: return None
        x = float(m2.group(1))
        return x * {None: 1.0, "R": 1.0, "K": 1e3, "M": 1e6}[m2.group(2)]
    series = {}
    for fp in b.GetFootprints():
        if not fp.GetReference().startswith("R"): continue
        pads = [p for p in fp.Pads()]
        if len(pads) != 2: continue
        ohm = _ohms(fp.GetValue())
        if ohm is None or not (10.0 <= ohm <= 150.0): continue
        a_, b_ = pads[0].GetNetname(), pads[1].GetNetname()
        if _is_rail(a_) or _is_rail(b_) or a_ == b_: continue      # a pull-up is not a termination
        for this, other in ((a_, b_), (b_, a_)):
            series.setdefault(this, []).append("%s %s to %s" % (fp.GetReference(), fp.GetValue(), other.lstrip("/")))
    _allow = _bt.value(letter, "edge_allow", []) or []
    import fnmatch as _fn
    def mitigation(net):
        nm = net.lstrip("/")
        if (cls_target or {}).get(net) or (cls_target or {}).get(nm):
            return "an impedance target on its class, so it is a designed transmission line"
        if net in series or nm in series:
            return "a series resistor on it (%s), which is what a source termination looks like from the board" % \
                   ", ".join(series.get(net) or series.get(nm))[:80]
        for e in _allow:
            if _fn.fnmatch(nm, e.get("pattern", "")): return "declared: %s" % str(e.get("why", ""))[:90]
        return None
    length, worst_layer, mitigated = {}, {}, []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK": continue
        n = t.GetNetname()
        if not signalnets.is_signal(n, signals): continue
        s, e = t.GetStart(), t.GetEnd()
        length[n] = length.get(n, 0.0) + math.hypot(mm(s.x) - mm(e.x), mm(s.y) - mm(e.y))
        worst_layer.setdefault(n, set()).add(t.GetLayer())
    rows, over, undeclared = [], [], []
    for n, L in sorted(length.items()):
        c = (cls.get(n) or ("UNKNOWN", ""))[0]
        tr, _why = rise_for(n, c)
        if not tr:
            if c != "LOW_SPEED_OR_DC": undeclared.append("%s (%s)" % (n.lstrip("/"), c))
            continue
        # the SLOWEST layer the net uses decides: a stripline's delay is the longer one
        tpd = max(t_pd_ps_per_mm(er, Lr in outer) for Lr in worst_layer[n])
        crit = (float(tr) * 1000.0) / (float(k) * tpd)
        rows.append(dict(net=n.lstrip("/"), cls=c, mm=round(L, 1), critical_mm=round(crit, 1), rise_ns=tr))
        if L > crit:
            why = mitigation(n)
            rows[-1]["mitigation"] = why or "none"
            if why: mitigated.append("%s (%s): %.0f mm past %.0f mm, %s" % (n.lstrip("/"), c, L, crit, why))
            else:
                over.append("%s (%s): %.0f mm routed against a critical length of %.0f mm at a %.1f ns edge, "
                            "with no impedance target, no series resistor on it and no declaration"
                            % (n.lstrip("/"), c, L, crit, float(tr)))
    print("edge_length: er %.2f, criterion l = t_r / (%s x t_pd); %d signal net(s) judged, %d past their "
          "critical length of which %d are controlled, terminated or declared and %d are not, %d with a class "
          "but no declared edge"
          % (er, k, len(rows), len(over) + len(mitigated), len(mitigated), len(over), len(undeclared)))
    for x in sorted(mitigated)[:12]: print("  long and answered: %s" % x)
    if undeclared: print("  no declared edge: %s%s" % (", ".join(sorted(undeclared)[:12]),
                                                       " ..." if len(undeclared) > 12 else ""))
    for x in sorted(over)[:20]: print("  OVER %s" % x)
    if "--json" in a: print(json.dumps(rows, indent=1))
    return _v.write("edge_length_routed", _v.FAIL if over else (_v.INCONCLUSIVE if (not rows or undeclared) else _v.PASS),
                    counts={"judged": len(rows), "over_critical_length": len(over),
                            "long_and_answered": len(mitigated), "no_declared_edge": len(undeclared)},
                    denominator=len(rows) or 1, evidence=sorted(over)[:20],
                    inputs={"board": path, "critical_k": k, "epsilon_r": round(er, 3)},
                    note=("no net on this board carries a class with a declared rise time" if not rows else
                          "every signal net's routed length against the critical length its own class implies, "
                          "and a net past it is asked whether it is impedance-controlled, series-terminated or "
                          "declared before it is called a defect: being a transmission line is physics, being "
                          "an uncontrolled one is the finding"),
                    out_dir=out_dir)


# ------------------------------------------------------------------------------------------------------------------
# RULE SI-001 AT THE SCHEMATIC PHASE (26 September 2026, MESHSAT-1357; review of 26 September 2026, section 6).
#
# The rule's acceptance: "A per-board table: net class, driver edge rate from the device datasheet, the length above
# which that edge rate makes the net a transmission line on this stackup, and the nets that exceed it with their
# topology and termination." Its registry evidence scope is the schematic and the stackup, and its phase is SCHEMATIC,
# so the table is taken from what exists before layout: the committed netlist of the declared phase (by sha and by
# content), the board table's signal-class declarations, the held documents in v2/vendor, and the declared stack.
# Which nets EXCEED the critical length is a routed length and stays with the layout gate (routed_main above,
# verdict edge_length_routed); what the table says per class instead is the length a layout must stay under, and
# whether the netlist already carries what a net needs if it does not.
#
# THE EDGE RATE IS A DOCUMENT'S OR IT IS UNDECIDED. A class entry's `rise_ns` in boards/<letter>.json is accepted only
# where EDGE_SOURCES below names a held file that states it: the file must be in the tree, the quoted words must be in
# it (whitespace and markdown quote marks aside), and the number it states must be the declared number. A declared
# number the named document contradicts is a FAIL, because every length computed from it is wrong; a declared number
# no held document states, and a class with no number at all, are UNDECIDED, and any UNDECIDED net outside
# LOW_SPEED_OR_DC makes the reading INCONCLUSIVE with the net, its class and the ICs on it named, which is the list
# of datasheets a decision still needs. Nothing is estimated.
#
# THE CHOICES THIS MAKES where more than one option stood, each a session decision of 26 September 2026 under the
# owner's standing rule of that day (reverse any of them by changing the constant it names):
#   * LOW_SPEED_OR_DC is not asked for an edge. It is the class this project declares, with a basis per entry, for an
#     enable, a sense line or a level, and the rule's own false-positive analysis counts the undeclared nets without
#     it (60 on board A, 380 on board B). Asking it for an edge would be a change of the rule, which is the registry
#     writer's (LOW_CLASS);
#   * a net's class and its edge come from the FIRST signal-class entry its name matches, which is how
#     signal_class.classify reads the same declarations; the routed half read the first entry that carried a rise
#     time, which can give a net the edge of a class it is not in;
#   * the declared stack is the board's `stackup` in pcb_board_facts.yaml on its declared routing layers, AND every
#     stack a layer decision has ruled for the board (RULED_STACKS: board C six layers by decision 27, board P four
#     layers at 2 oz by decision 28, and board B's eight-layer measurement under decision 43, EXPERIMENTAL), on all of
#     their copper layers because no routing layer is declared for them yet; the SLOWEST layer of all of them sets
#     the critical length, so the table holds whichever stack the layout is drawn on;
#   * a stripline's delay is taken at the LARGER dielectric constant of its two neighbours (a bound: its effective
#     constant lies between them), and a microstrip's from its one neighbour as the routed half computes it;
#   * a class "may be electrically long" on a board when its critical length is shorter than the board's outline
#     width plus height, the longest run a net makes corner to corner without a meander; and what it then needs is
#     one of an impedance target on its net class (a designed transmission line), a series resistor of 10 to 150 ohm
#     to another signal net in the netlist (the source-termination screen the routed half uses, still a screen: a
#     netlist does not say which end drives), or a declaration in edge_allow; a net with none of them is LAYOUT_BOUND,
#     and its critical length is the length the layout gate holds it to. That is not a failure at this phase;
#   * a net's net class is the netlist's own; where the netlist says Default, the project file's explicit assignment
#     is read, because the layout generators write the classes there (the routed half reads only that). A net the two
#     disagree on is named in the reading.
#   * the board-wide `rise_ns` map by class name, which the routed half falls back to and no board declares today, is
#     not read: an edge is a driver's, and the document that states it is named per class entry.
# ------------------------------------------------------------------------------------------------------------------
ECAD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ECAD))
LOW_CLASS = "LOW_SPEED_OR_DC"
SERIES_OHMS = (10.0, 150.0)
GROUND = re.compile(r"(^|_)GND[0-9]*$|^GND", re.I)      # the ground test ground_system.py applies (GND-001)
# the power classes the placement generators write, as signalnets.POWER_CLASSES reads them (the same set, kept
# here so the reading does not depend on a module the writer instrument cannot see)
POWER_CLASSES = {"HV", "NODE", "PWR", "RAIL", "SW", "BANK", "GNDC"}

# The held documents that state an edge, and the class entries each one decides. A board-table entry with a rise time
# that no row here covers is UNDECIDED. `quote` must be found in `document` (normalised), and `rise_ns` is the number
# the document states for the fastest conforming driver, the worst case a board is designed for.
EDGE_SOURCES = (
    {"id": "USB2-HS", "rise_ns": 0.5,
     "document": "v2/vendor/standards/usb-2-0-specification-2024-09-27.md",
     "clause": "USB 2.0 section 7.1.2.2, THSR and THSF, 10 to 90 percent, a minimum",
     "quote": "high-speed differential rise and fall times must be 500 ps or longer",
     "covers": {"a": ("USB_*_P", "USB_*_N"),
                "b": ("USB_*_N", "USB_*_P", "USB_OTG_*", "*_DM", "*_DP"),
                "d": ("USB1_?R", "USB*_P", "USB*_N", "HUB_DP*", "HUB_DM*")}},
    {"id": "USB2-FS", "rise_ns": 4.0,
     "document": "v2/vendor/standards/usb-2-0-specification-2024-09-27.md",
     "clause": "USB 2.0 Table 7-9, TFR and TFF, 10 to 90 percent, a minimum",
     "quote": "| Rise time | TFR | Figure 7-8, Figure 7-9 | 4 | 20 | ns |",
     "covers": {"c": ("USB_PNL_*", "USB_D*_R"),
                "e": ("USB_*",)}},
)

# The stacks a layer decision has ruled for a board, beside the one pcb_board_facts.yaml declares. These are RULINGS,
# dated, and are held here rather than read from pcb_decisions.yaml at run time: that file changes whenever any
# decision is recorded, and as a configuration input of this reading it would make every board's SI-001 reading stale
# on each of those edits. tests/test_edge_length.py holds each row to its decision's status (`ruled`) and to the
# stack table, so a reopened decision fails the suite instead of drifting here.
RULED_STACKS = {
    "b": ((43, "JLC08161H-2116", "the eight-layer measurement decision 43 orders, EXPERIMENTAL"),),
    "c": ((27, "JLC06161H-3313", "six layers, decision 27"),),
    "p": ((28, "JLC04162H-7628", "four layers at 2 oz, decision 28"),),
}


def _sha16(path):
    try: return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    except OSError: return None


def _shown(path):
    """A recorded path: relative to v2/ecad, or to the repository for a document, never absolute (a reading that
    records a path under a temporary directory is refused as a fixture's, rules_status._temp_input)."""
    ap = os.path.abspath(path)
    for root in (ECAD, REPO):
        if ap.startswith(root + os.sep): return os.path.relpath(ap, root)
    return os.path.join(os.path.basename(os.path.dirname(ap)), os.path.basename(ap))


def read_netlist(path):
    """({net: {"class": name, "nodes": [(ref, pin, pinfunction, pintype)]}}, {ref: value}); every net, the last
    one too (a net ends at the next net or at the end of the file, R4T-F1)."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    nets = {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(?: \(class "([^"]*)"\))?(.*?)(?=\(net \(code|\Z)',
                         txt, re.S):
        nodes = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)(?: \(pinfunction "([^"]*)"\))?'
                           r'(?: \(pintype "([^"]*)"\))?', m.group(3))
        nets[m.group(1).lstrip("/")] = {"class": m.group(2) or "", "nodes": nodes}
    values = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt))
    return nets, values


def _norm(text):
    """Words as a reader sees them: markdown quote marks dropped, whitespace collapsed."""
    return " ".join(re.sub(r"(?m)^\s*>\s?", " ", text).split())


def edge_source(letter, pattern, rise_ns, repo=None):
    """(status, source, why) for one class entry's declared rise time. status: DECIDED, UNDECIDED or CONTRADICTED."""
    repo = repo or REPO
    for s in EDGE_SOURCES:
        if pattern not in (s.get("covers") or {}).get(letter, ()): continue
        doc = os.path.join(repo, s["document"])
        if not os.path.isfile(doc):
            return "UNDECIDED", s, "the document %s it names is not in this tree" % s["document"]
        if _norm(s["quote"]) not in _norm(open(doc, encoding="utf-8", errors="replace").read()):
            return "UNDECIDED", s, "%s does not contain the words quoted from it (%r)" % (s["document"], s["quote"][:60])
        if rise_ns is None:
            return "DECIDED", s, "%s: %s" % (s["clause"], s["document"])
        if abs(float(rise_ns) - float(s["rise_ns"])) > 1e-9:
            return "CONTRADICTED", s, "declared %s ns, and %s states %s ns (%s)" % (rise_ns, s["document"], s["rise_ns"], s["clause"])
        return "DECIDED", s, "%s: %s" % (s["clause"], s["document"])
    if rise_ns:
        return "UNDECIDED", None, ("declares %s ns and no held document is named for it in edge_length.EDGE_SOURCES"
                                   % rise_ns)
    return "UNDECIDED", None, "no edge is declared and no held document states one"


def stack_delays(name):
    """[(copper layer, outer, t_pd ps/mm)] for a named stack of stackup_write.STACKS, or None if it is not held.
    A microstrip sees (er + 1) / 2 + 0.04 of its one neighbour, as t_pd_ps_per_mm computes; a stripline is bounded by
    the LARGER constant of its two neighbours."""
    from stackup_write import STACKS
    rows = STACKS.get(name)
    if not rows: return None
    out = []
    for i, r in enumerate(rows):
        if len(r) != 2: continue
        nb = [rows[j][3] for j in (i - 1, i + 1) if 0 <= j < len(rows) and len(rows[j]) == 4]
        outer = r[0] in ("F.Cu", "B.Cu")
        if not nb: continue
        out.append((r[0], outer, t_pd_ps_per_mm(max(nb), outer)))
    return out


def worst_delay(letter, facts=None):
    """(t_pd, chosen, candidates, notes): the slowest routing layer over every stack the board may be drawn on."""
    import rules_lib as _R
    f = (facts if facts is not None else _R.board_facts()).get(letter) or {}
    cands, notes = [], []
    decl = f.get("stackup")
    if decl:
        rl = set(f.get("routing_layers") or [])
        d = stack_delays(decl)
        if d is None: notes.append("the declared stack %s is not in stackup_write.STACKS" % decl)
        else:
            use = [x for x in d if not rl or x[0] in rl]
            cands += [(decl, "declared in pcb_board_facts.yaml, on its routing layers %s" % ",".join(sorted(rl) or ["(all)"]), x)
                      for x in use]
    for n, name, why in RULED_STACKS.get(letter, ()):
        if name == decl: continue
        d = stack_delays(name)
        if d is None: notes.append("%s (%s) is not in stackup_write.STACKS" % (name, why)); continue
        cands += [(name, "%s, on every copper layer (no routing layer is declared for it)" % why, x) for x in d]
    if not cands: return None, None, [], notes
    best = max(cands, key=lambda c: c[2][2])
    return best[2][2], best, cands, notes


def _ohms(v):
    v = (v or "").strip().upper().replace(" ", "")
    m2 = re.match(r"^(\d+(?:\.\d+)?)(R|K|M)?", v.replace("OHM", "").replace("Ω", ""))
    if not m2: return None
    x = float(m2.group(1))
    return x * {None: 1.0, "R": 1.0, "K": 1e3, "M": 1e6}[m2.group(2)]


def schematic_table(net_path, letter=None, intent_path=None, facts=None, repo=None):
    """SI-001 at the schematic phase: the per-class table and its result. See the block comment above."""
    import boardtable as _bt, signal_class as _sc, netclass as _nc, rules_lib as _R
    repo = repo or REPO
    letter = letter or _bt.letter_for(net_path)
    stem = os.path.splitext(os.path.basename(net_path))[0]
    ndir = os.path.dirname(os.path.abspath(net_path))
    intent_path = intent_path or os.path.join(ndir, stem + "-intent.json")
    pro = os.path.join(os.path.dirname(ndir), stem + ".kicad_pro")
    res = {"letter": letter, "rows": [], "fails": [], "notes": [], "missing_input": None, "inputs": {}, "counts": {}}
    if not os.path.exists(net_path):
        res["missing_input"] = "no netlist at %s" % _shown(net_path); return res
    nrec = {"path": _shown(net_path), "sha256_16": _sha16(net_path)}
    try:
        import regen_compare as _rc
        nrec["content16"] = _rc.content_hash(open(net_path, encoding="utf-8", errors="replace").read())
    except Exception as e:
        nrec["content16_absent"] = "%s: %s" % (type(e).__name__, str(e)[:80])
    res["inputs"]["netlist"] = nrec
    if not letter:
        res["missing_input"] = "no board table names %s, so its declarations cannot be read" % stem; return res
    tpath = os.path.join(HERE, "boards", "%s.json" % letter)
    for key, p in (("intent", intent_path), ("board_table", tpath), ("project", pro),
                   ("board_facts", os.path.join(HERE, "pcb_board_facts.yaml")),
                   ("stack_table", os.path.join(HERE, "stackup_write.py"))):
        if os.path.exists(p): res["inputs"][key] = {"path": _shown(p), "sha256_16": _sha16(p)}
    it = json.load(open(intent_path, encoding="utf-8")) if os.path.exists(intent_path) else {}
    if facts is None: facts = _R.board_facts()
    k = _bt.value(letter, "critical_k")
    tpd, chosen, cands, snotes = worst_delay(letter, facts)
    res["notes"] += snotes
    outline = (facts.get(letter) or {}).get("outline_mm") or []
    extent = float(outline[0]) + float(outline[1]) if len(outline) == 2 else None
    res["inputs"].update({"critical_k": k, "extent_mm": extent,
                          "t_pd_ps_per_mm": round(tpd, 3) if tpd else None,
                          "slowest_layer": ("%s %s" % (chosen[0], chosen[2][0])) if chosen else None,
                          "stacks": sorted({c[0] for c in cands})})
    if not k or not tpd:
        res["missing_input"] = "this board declares %s" % " and ".join(
            w for w, v in (("no critical_k", k), ("no stack held in stackup_write.STACKS", tpd)) if not v)
        return res

    nets, values = read_netlist(net_path)
    rails = {r.lstrip("/") for r in (it.get("rails") or {})}
    targets = {c: v for c, v in (it.get("pair_classes") or {}).items() if v}
    assign = {}
    if os.path.exists(pro):
        try: assign = json.load(open(pro, encoding="utf-8")).get("net_settings", {}).get("netclass_assignments", {}) or {}
        except ValueError: assign = {}
    decls, bad = _sc.declarations(letter)
    for x in bad: res["fails"].append("signal class declaration refused: %s" % x)
    table = _bt.value(letter, "signal_classes", []) or []          # the same table signal_class reads
    rise_of = {e.get("pattern"): e.get("rise_ns") for e in table}
    allow = _bt.value(letter, "edge_allow", []) or []

    def cls_of(n):
        c = nets[n]["class"]
        if c and c != "Default": return c, "netlist"
        a = _nc.class_of(assign, "/" + n) or _nc.class_of(assign, n)
        return (a, "project file") if a else ("Default", "netlist")
    disagree = []
    for n in nets:
        c = nets[n]["class"] or "Default"
        a = _nc.class_of(assign, "/" + n) or _nc.class_of(assign, n)
        if a and a != c: disagree.append("%s (netlist %s, project %s)" % (n, c, a))
    if disagree:
        res["notes"].append("%d net(s) whose netlist class differs from the project file's assignment: %s%s"
                            % (len(disagree), ", ".join(sorted(disagree)[:8]), " ..." if len(disagree) > 8 else ""))

    def is_signal(n):
        d = nets[n]
        if n.startswith("unconnected-") or n.startswith("+") or GROUND.search(n) or n in rails: return False
        if len({r for r, _p, _f, _t in d["nodes"]}) < 2: return False       # one part: nothing to run between
        return str(cls_of(n)[0]).split(",")[0].strip().upper() not in POWER_CLASSES   # a list's first, as netclass reads it
    signals = sorted(n for n in nets if is_signal(n))

    # the source-termination screen, from the netlist: a two-pin resistor of 10 to 150 ohm between two signal nets
    on = {}
    for n, d in nets.items():
        for r, p, _f, _t in d["nodes"]: on.setdefault(r, []).append(n)
    sig = set(signals)
    series = {}
    for r, ns in on.items():
        if not r.startswith("R") or len(ns) != 2 or ns[0] == ns[1]: continue
        ohm = _ohms(values.get(r))
        if ohm is None or not (SERIES_OHMS[0] <= ohm <= SERIES_OHMS[1]): continue
        if ns[0] in sig and ns[1] in sig:
            for a_, b_ in ((ns[0], ns[1]), (ns[1], ns[0])):
                series.setdefault(a_, []).append("%s %s to %s" % (r, values.get(r), b_))

    rows = {}
    for n in signals:
        hit = None
        for pat, klass, basis in decls:
            if fnmatch.fnmatchcase(n, pat) or fnmatch.fnmatchcase("/" + n, pat): hit = (pat, klass, basis); break
        pat, klass, basis = hit or ("(no declaration)", "UNKNOWN", "")
        row = rows.setdefault(pat, {"pattern": pat, "class": klass, "basis": basis[:160], "nets": [],
                                    "rise_ns": rise_of.get(pat) if hit else None, "drivers": {}})
        row["nets"].append(n)
        for r, _p, _f, _t in nets[n]["nodes"]:
            if r.startswith("U"): row["drivers"].setdefault(values.get(r, "?"), set()).add(r)

    counts = {"signal_nets": len(signals), "decided_nets": 0, "undecided_nets": 0, "low_speed_nets": 0,
              "contradicted_nets": 0, "may_be_long_nets": 0, "answered_nets": 0, "layout_bound_nets": 0,
              "classes": len(rows)}
    for pat in sorted(rows):
        row = rows[pat]
        row["drivers"] = {v: sorted(rs) for v, rs in sorted(row["drivers"].items())}
        nn = len(row["nets"])
        if row["class"] == LOW_CLASS and not row["rise_ns"]:
            row.update(status="LOW_SPEED_OR_DC", why="declared slow or DC with its basis; no edge is asked of it")
            counts["low_speed_nets"] += nn
        elif row["class"] == "UNKNOWN":
            row.update(status="UNDECIDED", why="no signal-class declaration names these nets, so neither their class "
                                               "nor their edge is known")
            counts["undecided_nets"] += nn
        else:
            st, src, why = edge_source(letter, pat, row["rise_ns"], repo)
            if st == "DECIDED" and row["rise_ns"] is None: st, why = "UNDECIDED", "the entry declares no rise time"
            row.update(status=st, why=why, source=(src or {}).get("id"), document=(src or {}).get("document"))
            if st == "CONTRADICTED":
                counts["contradicted_nets"] += nn
                res["fails"].append("%s (%s, %d net(s)): %s" % (pat, row["class"], nn, why))
            elif st == "UNDECIDED":
                counts["undecided_nets"] += nn
        if row["status"] != "DECIDED":
            continue
        counts["decided_nets"] += nn
        crit = float(row["rise_ns"]) * 1000.0 / (float(k) * tpd)
        row["critical_mm"] = round(crit, 1)
        # a board with no declared outline has no corner-to-corner run to compare with, so every net of the class may
        # be long (the second independent check of 26 September: a missing extent read as "never long")
        row["may_be_long"] = extent is None or crit < extent
        if not row["may_be_long"]:
            row["needs"] = "nothing: the critical length is past the board's corner-to-corner run"
            continue
        row["needs"] = "an impedance target, a series termination or a declaration, or every net under %.1f mm" % crit
        ans, bound = {}, []
        for n in row["nets"]:
            c, how = cls_of(n)
            if c in targets:
                ans[n] = "impedance target on class %s (%s, from the %s)" % (c, ", ".join("%s %s" % kv for kv in sorted(targets[c].items())), how)
            elif n in series:
                ans[n] = "series resistor %s (a screen)" % "; ".join(series[n])[:80]
            else:
                dec = next((e for e in allow if fnmatch.fnmatch(n, e.get("pattern", ""))), None)
                if dec: ans[n] = "declared in edge_allow: %s" % str(dec.get("why", ""))[:80]
                else: bound.append(n)
        row["answered"] = ans
        row["layout_bound"] = bound
        counts["may_be_long_nets"] += nn
        counts["answered_nets"] += len(ans)
        counts["layout_bound_nets"] += len(bound)
    res["rows"] = [rows[p] for p in sorted(rows)]
    res["counts"] = counts
    # every held document this board's edges are taken from, by sha, so a corrected transcription is seen
    for i, d in enumerate(sorted({s["document"] for s in EDGE_SOURCES if letter in (s.get("covers") or {})}), 1):
        res["inputs"]["document_%d" % i] = {"path": d, "sha256_16": _sha16(os.path.join(repo, d))}
    return res


def schematic_result(res):
    """PASS only when every signal net is decided and none is left to the layout. A LAYOUT_BOUND net (may be long, no
    impedance target, no series termination, no declaration) is answered by nothing at this phase, and the routed
    comparison (edge_length_routed) decides no rule, so the reading stays INCONCLUSIVE naming each one with its
    critical length until the schematic answers it (session decision TSN-D18 of 26 September 2026, reversing TSN-D8
    under the owner's standing rule of that day, on the second independent check's finding)."""
    import verdict as _v
    if res.get("missing_input"): return _v.INCONCLUSIVE
    if res["fails"]: return _v.FAIL
    c = res["counts"]
    if not c.get("signal_nets") or c.get("undecided_nets"): return _v.INCONCLUSIVE
    if c.get("layout_bound_nets") or any(r.get("layout_bound") for r in res.get("rows") or []):
        return _v.INCONCLUSIVE
    return _v.PASS


def write_schematic_verdict(res, out_dir=None, quiet=False, table_file=True):
    """Write the `edge_length` verdict (rule SI-001) and, beside it, the table as edge_length.table.json."""
    import verdict as _v
    result = schematic_result(res)
    c = res.get("counts") or {}
    ev = list(res["fails"])
    for r in res.get("rows") or []:
        if r["status"] == "UNDECIDED":
            ev.append("UNDECIDED %s (%s, %d net(s)): %s; ICs on them: %s" % (
                r["pattern"], r["class"], len(r["nets"]), r["why"][:90],
                ", ".join("%s %s" % (v, "/".join(rs[:3])) for v, rs in list(r["drivers"].items())[:5]) or "none"))
    for r in res.get("rows") or []:
        if r.get("layout_bound"):
            ev.append("LAYOUT_BOUND %s (%s, %.1f ns, critical %.1f mm): %s" % (
                r["pattern"], r["class"], float(r["rise_ns"]), r["critical_mm"], ", ".join(r["layout_bound"][:8])))
    inputs = dict(res.get("inputs") or {})
    if res.get("letter"): inputs["board"] = res["letter"]
    od = out_dir or os.environ.get("VERDICT_DIR") or "out"
    if table_file and res.get("rows") is not None and not res.get("missing_input"):
        try:
            os.makedirs(od, exist_ok=True)
            rows = [dict(r, nets=r["nets"]) for r in res["rows"]]
            with open(os.path.join(od, "edge_length.table.json.part"), "w", encoding="utf-8") as f:
                json.dump({"rule": "SI-001", "board": res.get("letter"), "inputs": inputs, "counts": c,
                           "notes": res.get("notes") or [], "rows": rows}, f, indent=1, sort_keys=True)
            os.replace(os.path.join(od, "edge_length.table.json.part"), os.path.join(od, "edge_length.table.json"))
        except OSError as e:
            print("edge_length: the table could not be written (%s)" % e)
    return _v.write("edge_length", result, rules=["SI-001"], counts=c, denominator=c.get("signal_nets") or 0,
                    evidence=ev[:50], inputs=inputs, out_dir=out_dir, quiet=quiet,
                    missing_input=res.get("missing_input"),
                    note=("SI-001 at the schematic phase, from the committed netlist, the held documents and the declared "
                          "stack: per class the edge rate and the document that states it (UNDECIDED where none does), "
                          "the critical length l = t_r / (k t_pd) on the slowest layer of every stack the board may be "
                          "drawn on, and whether the netlist carries an impedance target, a series termination or a "
                          "declaration where a net may be electrically long. The routed lengths are the layout gate's "
                          "(edge_length_routed). The table is edge_length.table.json beside this verdict. Session "
                          "decisions of 26 September 2026: LOW_SPEED_OR_DC asked no edge, the first matching entry "
                          "decides, the slowest layer of the declared and ruled stacks, the stripline bound, the "
                          "corner-to-corner extent, the project file's class where the netlist says Default"))


def print_table(res):
    c = res.get("counts") or {}
    i = res.get("inputs") or {}
    print("edge_length: SI-001 schematic table, board %s: k %s, slowest layer %s at %s ps/mm, extent %s mm; %d signal "
          "net(s), %d decided, %d undecided, %d declared slow or DC, %d contradicted; of the decided %d may be "
          "electrically long, %d answered in the netlist and %d layout-bound"
          % (str(res.get("letter") or "?").upper(), i.get("critical_k"), i.get("slowest_layer"), i.get("t_pd_ps_per_mm"),
             i.get("extent_mm"), c.get("signal_nets", 0), c.get("decided_nets", 0), c.get("undecided_nets", 0),
             c.get("low_speed_nets", 0), c.get("contradicted_nets", 0), c.get("may_be_long_nets", 0),
             c.get("answered_nets", 0), c.get("layout_bound_nets", 0)))
    for r in res.get("rows") or []:
        tail = ""
        if r.get("critical_mm") is not None:
            tail = ", %.1f ns, critical %.1f mm, %s" % (float(r["rise_ns"]), r["critical_mm"],
                                                        "%d answered, %d layout-bound" % (len(r.get("answered") or {}), len(r.get("layout_bound") or []))
                                                        if r.get("may_be_long") else "never long here")
        print("  %-12s %-22s %-20s %3d net(s)%s" % (r["status"], r["pattern"][:22], r["class"][:20], len(r["nets"]), tail))
    for n in res.get("notes") or []: print("  note: %s" % n)
    for f in res.get("fails") or []: print("  FAIL %s" % f)
    if res.get("missing_input"): print("  not judged: %s" % res["missing_input"])


def netlist_main(argv):
    """edge_length.py --netlist <netlist.net> [--out-dir DIR] [--json]: SI-001 at the schematic phase."""
    net = _v.opt(argv, "--netlist")
    if not net: print(__doc__); return _v.USAGE
    res = schematic_table(net, _v.opt(argv, "--board"))
    print_table(res)
    if "--json" in argv:
        print(json.dumps(res, indent=1, default=list))
    return write_schematic_verdict(res, out_dir=_v.opt(argv, "--out-dir"))


def main(a):
    """--netlist: the schematic table (edge_length). A board: the routed comparison (edge_length_routed), under its
    own crash guard so a crash there is never filed under the schematic verdict, and then the table from the netlist
    beside the board when there is one, into the same directory."""
    if not a: print(__doc__); return _v.USAGE
    if "--netlist" in a: return netlist_main(a)
    rc = _v.guard("edge_length_routed", routed_main, a)
    path = a[0]
    stem = os.path.splitext(os.path.basename(path))[0]
    net = os.path.join(os.path.dirname(os.path.abspath(path)), "out", stem + ".net")
    if os.path.exists(net):
        res = schematic_table(net)
        print_table(res)
        write_schematic_verdict(res, out_dir=os.path.join(os.path.dirname(os.path.abspath(path)), "out"))
    return rc


if __name__ == "__main__":
    # EVERY GATE LEAVES A READING WHEN IT RAISES (18 September 2026). The thirteen one-line entries of this
    # morning were the gates a crash had already cost a verdict; these are the rest of the deciding gates in
    # the coverage map, guarded the same way, so a rule whose tool raised reads INCONCLUSIVE naming the
    # exception rather than 'no verdict', which the registry reads as nobody having looked.
    sys.exit(_v.guard("edge_length", main, sys.argv[1:]))