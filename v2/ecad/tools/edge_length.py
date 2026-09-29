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
    # an allowance answers a net only with its basis held, and never past the length it declares (CSI-D1, CSI-D2)
    try: _tpd_decl = worst_delay(letter)[0]
    except Exception: _tpd_decl = None
    _allow, _allow_bad = load_allow(letter, REPO, tpd=_tpd_decl)
    import fnmatch as _fn
    def _entry(net):
        nm = net.lstrip("/")
        return next((e for e in _allow if _fn.fnmatch(nm, e.get("pattern", ""))), None)
    def mitigation(net, L=None):
        nm = net.lstrip("/")
        if (cls_target or {}).get(net) or (cls_target or {}).get(nm):
            return "an impedance target on its class, so it is a designed transmission line"
        if net in series or nm in series:
            return "a series resistor on it (%s), which is what a source termination looks like from the board" % \
                   ", ".join(series.get(net) or series.get(nm))[:80]
        e = _entry(net)
        if e is not None:
            ok, words = allow_answers(e, L)
            return words if ok else None
        return None
    length, worst_layer, mitigated = {}, {}, []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK": continue
        n = t.GetNetname()
        if not signalnets.is_signal(n, signals): continue
        s, e = t.GetStart(), t.GetEnd()
        length[n] = length.get(n, 0.0) + math.hypot(mm(s.x) - mm(e.x), mm(s.y) - mm(e.y))
        worst_layer.setdefault(n, set()).add(t.GetLayer())
    # EVERY NET A HELD ALLOWANCE NAMES IS HELD TO ITS max_mm FIRST (the independent check of 29 September 2026, B1 and
    # m10): whatever its class, whether its class declares a rise time, whether it is past its critical length, and
    # whether a series resistor or an impedance target also answers it. The length is the declaration's condition.
    allow_over, allow_held, over_limit = [], set(), set()
    for n, L in sorted(length.items()):
        e = _entry(n)
        if e is None: continue
        ok, words = allow_answers(e, L)
        if ok: allow_held.add(n)
        else: allow_over.append("%s: %s" % (n.lstrip("/"), words)); over_limit.add(n.lstrip("/"))
    rows, over, undeclared = [], [], []
    for n, L in sorted(length.items()):
        c = (cls.get(n) or ("UNKNOWN", ""))[0]
        tr, _why = rise_for(n, c)
        if not tr:
            # a net an allowance holds within its declared length is answered by it; one over it is named above
            if c != "LOW_SPEED_OR_DC" and n not in allow_held and n.lstrip("/") not in over_limit:
                undeclared.append("%s (%s)" % (n.lstrip("/"), c))
            continue
        # the SLOWEST layer the net uses decides: a stripline's delay is the longer one
        tpd = max(t_pd_ps_per_mm(er, Lr in outer) for Lr in worst_layer[n])
        crit = (float(tr) * 1000.0) / (float(k) * tpd)
        rows.append(dict(net=n.lstrip("/"), cls=c, mm=round(L, 1), critical_mm=round(crit, 1), rise_ns=tr))
        if n.lstrip("/") in over_limit:
            rows[-1]["mitigation"] = "over its declared limit"
            continue
        if L > crit:
            why = mitigation(n, L)
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
    for x in sorted(allow_over)[:20]: print("  OVER ITS DECLARED LIMIT %s" % x)
    for x in _allow_bad: print("  FAIL edge_allow refused: %s" % x)
    if "--json" in a: print(json.dumps(rows, indent=1))
    return _v.write("edge_length_routed", _v.FAIL if (over or _allow_bad or allow_over) else
                    (_v.INCONCLUSIVE if ((not rows and not allow_held) or undeclared) else _v.PASS),
                    counts={"judged": len(rows), "over_critical_length": len(over),
                            "long_and_answered": len(mitigated), "no_declared_edge": len(undeclared),
                            "over_declared_limit": len(allow_over), "held_within_declared_limit": len(allow_held),
                            "allowances_refused": len(_allow_bad)},
                    denominator=len({r["net"] for r in rows} | {x.lstrip("/") for x in allow_held} | over_limit) or 1,
                    evidence=(["edge_allow refused: %s" % x for x in _allow_bad]
                              + ["OVER ITS DECLARED LIMIT %s" % x for x in sorted(allow_over)] + sorted(over))[:20],
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
# THE EDGE RATE IS A DOCUMENT'S OR IT IS UNDECIDED. Since 27 September 2026 every edge is a record of
# tools/pcb_edge_rates.yaml (see "THE EDGE RATES ARE DATA" below): the document it names must be in the tree, the
# quoted words must be in it (whitespace and markdown quote marks aside), and an IBIS record's number must be the one
# its held model gives. A class entry's own `rise_ns` in boards/<letter>.json must agree with the record that covers
# it; a number the named document or model contradicts is a FAIL, because every length computed from it is wrong. A
# net whose driver has no record is UNDECIDED, and any UNDECIDED net outside LOW_SPEED_OR_DC makes the reading
# INCONCLUSIVE with the net, its class and the part on it named, which is the list of documents a decision still
# needs. Nothing is estimated; where a maker publishes no edge, a stated bound stands in and is marked as one.
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

# ------------------------------------------------------------------------------------------------------------------
# THE EDGE RATES ARE DATA (27 September 2026, MESHSAT-1357, layer 9; the third checkpoint review, sections 5 and 6).
#
# Every edge this reading uses comes from tools/pcb_edge_rates.yaml, a CONFIGURATION INPUT of the edge_length verdict
# (recorded by sha in every reading). It holds three kinds of record, each with the maker's document, the words quoted
# from it, the conditions, the applicability and the verification still owed:
#   interfaces  an edge for a whole signal-class entry of a board, from a document that binds EVERY driver of it (a
#               standard's minimum, the USB 2.0 rows that were EDGE_SOURCES until today), or a stated bound or model
#               for a class whose drivers publish nothing (a power-stage node, an oscillator node, a controlled link);
#   families    an edge for a DRIVER, recognised by its part number at the start of the netlist's value field (never an
#               order code): a maker's IBIS model read per pin by ibis_read.py, a published minimum, a model, or a
#               bound; or a part that drives nothing (an ESD array), a passive switch that passes its far side's edge
#               through, a land that is a connector;
#   far_ends    the drivers beyond a connector, named from the record that lists the far end's parts.
# THE RESOLUTION, per signal net whose class entry no interface record covers (session decisions ER-D1 to ER-D9 of
# 27 September 2026, stated in the data file's header with their reasons and how to reverse each):
#   * every IC or module (reference U...) and every transistor (Q...) on the net is asked for its family; a part with
#     none leaves the net UNDECIDED and is named: nothing is estimated and nothing is defaulted;
#   * a pin the family types as an input, or whose IBIS model drives nothing, contributes no edge;
#   * a connector on the net, or a passive switch's through pin, contributes the far end's drivers when a far_ends
#     record names them, and otherwise leaves the net UNDECIDED naming the connector;
#   * the drivers of a net one two-pin resistor away (a series resistor to another signal net) are the net's too, as
#     they arrive through the resistor only slower; that hop is taken once;
#   * THE GOVERNING EDGE (ER-D13, 27 September 2026, second pass, on the independent check's first blocking item): the
#     governing edge of a net is the fastest edge ANY driver on it can produce. A driver whose maker publishes no
#     minimum has no known fastest edge, so a net that carries even one such driver is DECIDED BY A BOUND, whatever the
#     makers of the other drivers on it publish: their figures are recorded beside it (maker_edge_ns) and decide
#     nothing. Only a net on which EVERY driver has a published minimum (a maker's IBIS model, a maker's published
#     minimum, or a standard's minimum that binds every conforming driver) is decided by a maker's figure. A net that
#     is LAYOUT_BOUND and decided by a bound is named BOUND_DECIDES and its drivers without a figure are named; it is
#     never passed, and its critical length is the bound's.
#   * AN OPEN-DRAIN NET HAS TWO EDGES (the same pass): its FALL is the driver's pull-down and is the edge every record
#     above states for an open-drain pin; its RISE is the pull-up resistor charging the net's capacitance, which no
#     driver sets. The data file's `open_drain` records state the rise with its derivation; the reading attaches it to
#     the net (`rising`) and never takes it as the governing edge: for reflections the governing edge is the fall.
#
# THE MODELS ARE PINNED, NOT HELD (28 September 2026, stream w5si2; session decisions ER-D16 and ER-D17 in the data
# file's header). The makers' IBIS models are not in the repository (several forbid distribution in their header), so
# the reading works in three states and says which it is in:
#   * a model is read only when v2/vendor/ibis-manifest.yaml PINS it (ibis_manifest.py) and the file present is the
#     file pinned, by its full sha256; the record that cites it must cite the same file. The manifest is a tracked
#     configuration input, recorded by sha (inputs.ibis_manifest);
#   * a model that is ABSENT decides nothing: every net that waits on it is UNDECIDED, naming the file, its reason is
#     of kind MODEL_ABSENT, and the reading is INCONCLUSIVE. It fails closed: no figure is taken from the record's own
#     `edge_ns` in the model's absence, because that number is only a copy the model is there to hold;
#   * every model a reading ASKED for is recorded (inputs.model_N: path, the sha256/16 read or `absent: true`, and the
#     sha256/16 pinned), with the state of the set (inputs.model_state: PRESENT, PARTIAL, ABSENT or NOT_ASKED).
# AN UNDECIDED NET CARRIES THE KIND OF ITS REASON (row["undecided_kind"]), set where the reason is made and never read
# back out of its words: NO_DECLARATION (no signal-class entry names the net), MODEL_ABSENT (every reason the net has
# is a model that is not in this tree, so the net is decided once the models are fetched), OTHER (anything else, a
# net with a model absent AND another reason among them). counts: undecided_nets = undecided_no_declaration_nets +
# undecided_model_absent_nets + undecided_other_nets.
# A PIN WHOSE [Ramp] CELL THE MODEL'S OWN V-t TABLE CONTRADICTS (ibis_read FLAGGED, ER-D16) has no maker's figure: it
# takes the instantaneous bound, its net is decided by a bound, and the family's `edge_ns` is the fastest of the pins
# that are not flagged. The record names its flagged pins (`flagged_pins`) and is held to the file on that too.
# ------------------------------------------------------------------------------------------------------------------
RATES_PATH = os.path.join(HERE, "pcb_edge_rates.yaml")
SECTIONS = ("interfaces", "families", "far_ends", "open_drain")
EDGE_KINDS = ("STANDARD", "IBIS", "DATASHEET", "MODEL", "BOUND")
BOUND_KINDS = ("MODEL", "BOUND")
NON_EDGE_KINDS = ("NOT_A_DRIVER", "PASSIVE_SWITCH", "CONNECTOR")
DRIVER_PREFIXES = ("U", "Q")
UNASKED_PREFIXES = ("K", "T")            # a relay, a transformer; and every SW... reference, a mechanical switch


REASON_KINDS = ("NO_DECLARATION", "MODEL_ABSENT", "OTHER")


class Reason(str):
    """Why a net is undecided, as the words a reader sees, carrying WHAT KIND of reason it is (`kind`, one of
    REASON_KINDS) and, for a model that is not in the tree, which file (`file`). The kind is set where the reason is
    made; nothing reads it back out of the words. It serialises as its words."""
    def __new__(cls, text, kind="OTHER", file=None):
        o = str.__new__(cls, text)
        o.kind, o.file = kind, file
        return o


def _because(text, inner):
    """A reason wrapped in where it was met ("beyond J1 on board B: ..."), its kind and file kept."""
    return Reason(text, getattr(inner, "kind", "OTHER"), getattr(inner, "file", None))


def reasons_kind(reasons):
    """The kind of a net's reasons together: MODEL_ABSENT only when EVERY reason is a model that is not in the tree (the
    net is then decided by fetching the models), NO_DECLARATION only when every reason is that, else OTHER."""
    kinds = {getattr(r, "kind", "OTHER") for r in reasons}
    return kinds.pop() if len(kinds) == 1 else "OTHER"


def _yaml_load(path):
    import yaml
    return yaml.safe_load(open(path, encoding="utf-8")) or {}


def _no_rates(path):
    return dict({k: [] for k in SECTIONS}, path=path, sha16=None, search_listing=None)


def load_rates(path=None):
    """(rates, refusals). rates: {"interfaces", "families", "far_ends", "path", "sha16"}; a record the checks below
    refuse is left out and named in refusals (the reading lists them under its fails: the data file is wrong)."""
    path = path or RATES_PATH
    refusals = []
    try:
        raw = _yaml_load(path)
    except Exception as e:
        return _no_rates(path), ["pcb_edge_rates.yaml could not be read: %s: %s" % (type(e).__name__, str(e)[:120])]
    out = dict(_no_rates(path), sha16=hashlib.sha256(open(path, "rb").read()).hexdigest()[:16],
               search_listing=raw.get("search_listing"))
    ids = set()
    for sect in SECTIONS:
        for i, r in enumerate(raw.get(sect) or []):
            why = _refuse(sect, r)
            rid = (r or {}).get("id")
            if not why and rid in ids: why = "the id %s is used twice" % rid
            if why:
                refusals.append("pcb_edge_rates.yaml %s[%d] (%s): %s" % (sect, i, rid, why)); continue
            ids.add(rid)
            out[sect].append(r)
    fam_ids = {f["id"] for f in out["families"]}
    keep = []
    for fe in out["far_ends"]:
        bad = [x for x in fe.get("families") or [] if x not in fam_ids]
        if bad: refusals.append("pcb_edge_rates.yaml far_ends %s names families it does not define: %s" % (fe["id"], ", ".join(bad)))
        else: keep.append(fe)
    out["far_ends"] = keep
    return out, refusals


def citations(rec):
    """Every document a record cites, as [{"document", "quote", "sha256_16", "page", "where", "at"}]: its own
    (document, quote, sha256_16, and page or clause or where), each row of `checked`, each row of `pin_edges`, and an
    open-drain record's `rise`. `at` says where in the record the citation sits, for a refusal's words."""
    out = []
    def one(d, at):
        if isinstance(d, dict) and d.get("document"):
            out.append({"document": d["document"], "quote": d.get("quote"), "sha256_16": d.get("sha256_16"),
                        "page": d.get("page"), "where": d.get("where") or d.get("clause"), "at": at})
        if isinstance(d, dict) and isinstance(d.get("claimed_by"), dict): one(d["claimed_by"], at + ".claimed_by")
    one(rec, "the record")
    for key in ("checked", "pin_edges", "inputs_cited"):
        for j, c in enumerate(rec.get(key) or []): one(c, "%s[%d]" % (key, j))
    if isinstance(rec.get("rise"), dict):
        one(rec["rise"], "rise")
        for j, c in enumerate(rec["rise"].get("checked") or []): one(c, "rise.checked[%d]" % j)
    return out


def _cite_shape(rec):
    """None, or why a citation of the record cannot stand: EVERY document cited carries the sha256/16 of the held
    file it was read from and WHERE in it the words are (a page of a PDF, a clause or table of a transcription), and
    an IBIS record the sha256/16 of its model, the keyword its number is under and the cell as the file writes it
    (the acceptance of 27 September 2026: document, sha256/16, page or IBIS keyword, the words or numbers quoted)."""
    for c in citations(rec):
        sha = c["sha256_16"]
        if not (isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{16}", sha)):
            return "%s cites %s with no sha256_16 of the held file" % (c["at"], c["document"])
        if not c["quote"]: return "%s cites %s and quotes nothing from it" % (c["at"], c["document"])
        pg = c["page"]
        if pg is not None and not (isinstance(pg, int) and pg >= 1): return "%s: page %r is not a page number" % (c["at"], pg)
        if pg is None and not str(c["where"] or "").strip():
            return "%s cites %s with no page and no clause (where)" % (c["at"], c["document"])
    if rec.get("kind") == "IBIS":
        ib = rec.get("ibis") or {}
        sha = ib.get("sha256_16")
        if not (isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{16}", sha)): return "an IBIS record with no sha256_16 of its model"
        if not (ib.get("keyword") and ib.get("ramp")):
            return "an IBIS record that does not say under which keyword its number is (ibis.keyword) and how the file writes it (ibis.ramp)"
    return None


def _refuse_open_drain(r):
    """An open-drain record states the RISE of nets whose fall the drivers set: the pull-up and the capacitance it
    charges. It never gives a net its governing edge."""
    nets = r.get("nets")
    if not (isinstance(nets, dict) and nets and all(isinstance(v, list) and v for v in nets.values())):
        return "an open-drain record names no nets ({board letter: [net patterns]})"
    rise = r.get("rise")
    if not isinstance(rise, dict): return "an open-drain record with no rise"
    if rise.get("kind") not in BOUND_KINDS: return "rise.kind %r: a rise is computed, so it is a MODEL or a BOUND" % (rise.get("kind"),)
    e = rise.get("edge_ns")
    if not isinstance(e, (int, float)) or e < 0: return "rise.edge_ns %r is not a number of nanoseconds" % (e,)
    for f in ("derivation", "measure"):
        if not str(rise.get(f) or "").strip(): return "rise with no %s" % f
    if not rise.get("checked"): return "rise names no document checked"
    for f in ("fall", "applicability", "verification_owed"):
        if not str(r.get(f) or "").strip(): return "no %s" % f
    return _cite_shape(r)


def _refuse(sect, r):
    """None, or why the record cannot stand. The checks are on its SHAPE: an edge with no document, a published figure
    that is not a minimum, a bound or model with no derivation, a citation with no sha256/16 or no page. Whether the
    quoted words are in the document, on that page, and whether the held file is the one cited, is asked when the
    record is used, from the held file."""
    if not isinstance(r, dict) or not r.get("id"): return "no id"
    if sect == "open_drain": return _refuse_open_drain(r)
    k = r.get("kind")
    ok_kinds = {"interfaces": ("STANDARD", "MODEL", "BOUND"), "families": EDGE_KINDS + NON_EDGE_KINDS,
                "far_ends": (None,)}[sect]
    if sect == "far_ends":
        if not r.get("board") or not r.get("nets") or not r.get("basis"): return "a far end needs board, nets and basis"
        if not (r.get("families") or r.get("why_none") or r.get("continues")):
            return "a far end with no families and no continues must say why (why_none)"
        return None
    if k not in ok_kinds: return "kind %r is not one of %s" % (k, ", ".join(x for x in ok_kinds if x))
    if sect == "interfaces" and not r.get("covers"): return "an interface record covers no class entry"
    if sect == "families" and not r.get("parts") and not r.get("far_only"):
        return "a family names no part (a family met only beyond a connector says far_only: true)"
    if sect == "families" and k == "STANDARD" and not (r.get("claimed_by") or {}).get("document"):
        return ("a specification's minimum binds a part only where the part's own datasheet claims the specification: "
                "the record quotes no such claim (claimed_by)")
    if k in EDGE_KINDS:
        for f in ("applicability", "verification_owed"):
            if not str(r.get(f) or "").strip(): return "no %s" % f
        if k == "IBIS":
            ib = r.get("ibis") or {}
            if not (ib.get("file") and ib.get("component")): return "an IBIS record names no file or component"
        if k != "IBIS":
            e = r.get("edge_ns")
            if not isinstance(e, (int, float)) or e < 0: return "edge_ns %r is not a number of nanoseconds" % (e,)
        if k in ("STANDARD", "DATASHEET"):
            if r.get("statistic") != "min":
                return ("statistic %r: only a published MINIMUM bounds the fastest edge; a typical or a maximum value "
                        "is not one (write a MODEL with its margin, or a BOUND)" % (r.get("statistic"),))
            if not (r.get("document") and r.get("quote")): return "a published figure with no document or quote"
        if k in BOUND_KINDS:
            if not str(r.get("derivation") or "").strip(): return "a %s with no derivation" % k
            if not r.get("checked") and not str(r.get("no_document") or "").strip():
                return ("a %s that names no document checked for a published edge (or, where the maker's document is not "
                        "held at all, says so in no_document)" % k)
    for j, pe in enumerate(r.get("pin_edges") or []):
        if not isinstance(pe, dict) or not pe.get("match"): return "pin_edges[%d] names no pin (match)" % j
        pk = pe.get("kind")
        if pk not in ("DATASHEET", "STANDARD", "MODEL", "BOUND"): return "pin_edges[%d] kind %r" % (j, pk)
        pe_e = pe.get("edge_ns")
        if not isinstance(pe_e, (int, float)) or pe_e < 0: return "pin_edges[%d] edge_ns %r" % (j, pe_e)
        if pk in ("DATASHEET", "STANDARD") and (pe.get("statistic") != "min" or not (pe.get("document") and pe.get("quote"))):
            return "pin_edges[%d]: a published figure must be a minimum with its document and quote" % j
        if pk == "STANDARD" and not (pe.get("claimed_by") or {}).get("document"):
            return ("pin_edges[%d]: a specification's minimum binds a part only where the part's own datasheet claims "
                    "the specification, and the row quotes no such claim (claimed_by)" % j)
        if pk in BOUND_KINDS and not pe.get("derivation"): return "pin_edges[%d]: a %s with no derivation" % (j, pk)
    if k == "PASSIVE_SWITCH" and not (r.get("through") or r.get("through_pins")): return "a passive switch names no through pins"
    if (r.get("inputs") or r.get("input_pins")) and k in (EDGE_KINDS + ("PASSIVE_SWITCH",)) and sect == "families":
        for rx in (r.get("inputs"), r.get("through")):
            if rx:
                try: re.compile(rx)
                except re.error as e: return "a pin pattern that is no regular expression (%s)" % e
    if k in ("NOT_A_DRIVER", "PASSIVE_SWITCH", "CONNECTOR") and not (r.get("document") or r.get("basis")):
        return "no document or basis for calling the part %s" % k
    return _cite_shape(r)


def _standards(rates):
    """The STANDARD interface records in the shape EDGE_SOURCES has always had (the fixtures hand their own)."""
    out = []
    for r in rates["interfaces"]:
        if r.get("kind") != "STANDARD": continue
        out.append({"id": r["id"], "rise_ns": float(r["edge_ns"]), "document": r["document"],
                    "clause": r.get("clause") or r.get("conditions") or "", "quote": r["quote"],
                    "covers": {k: tuple(v) for k, v in (r.get("covers") or {}).items()}, "kind": "STANDARD"})
    return tuple(out)


try:
    RATES, RATES_REFUSALS = load_rates()
except Exception as _e:                                     # the reading still runs, and names why nothing decided
    RATES, RATES_REFUSALS = _no_rates(RATES_PATH), ["pcb_edge_rates.yaml: %s: %s" % (type(_e).__name__, str(_e)[:120])]
# The held documents that state an edge for a whole class entry, as the fixtures and the older readers know them: the
# STANDARD records of the data file. `quote` must be found in `document` (normalised), and `rise_ns` is the number the
# document states for the fastest conforming driver, the worst case a board is designed for.
EDGE_SOURCES = _standards(RATES)

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


_TEXT = {}


def _doc_text(path):
    """A held document's words: a PDF through the host's pdftotext (as pack_protection.py and the rails census read
    theirs), anything else as text. None when it cannot be read, which leaves whatever relies on it UNDECIDED."""
    try:
        key = (path, os.path.getmtime(path), os.path.getsize(path))
    except OSError:
        return None
    if key not in _TEXT:
        if path.lower().endswith(".pdf"):
            import subprocess
            try:
                r = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True, timeout=120)
                _TEXT[key] = r.stdout if r.returncode == 0 else None
            except (OSError, subprocess.SubprocessError):
                _TEXT[key] = None
        else:
            _TEXT[key] = open(path, encoding="utf-8", errors="replace").read()
    return _TEXT[key]


def _page_text(path, page):
    """One page of a held PDF, as pdftotext counts pages (the first is 1), or None."""
    try:
        key = (path, os.path.getmtime(path), os.path.getsize(path), int(page))
    except (OSError, ValueError, TypeError):
        return None
    if key not in _TEXT:
        import subprocess
        try:
            r = subprocess.run(["pdftotext", "-f", str(int(page)), "-l", str(int(page)), "-layout", path, "-"],
                               capture_output=True, text=True, timeout=120)
            _TEXT[key] = r.stdout if r.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            _TEXT[key] = None
    return _TEXT[key]


def model_record(repo, doc):
    """What a reading records of a maker's model it asked for, or None when `doc` is no model: {"path", "sha256_16"
    of the file present or "absent": True, "pinned_sha256_16" or None when no manifest row pins it}. A model is a file
    the manifest pins, or any `.ibs` (which must then be pinned to be read)."""
    import ibis_manifest as _im
    row = _im.pin(_im.load(repo), doc)
    if row is None and not str(doc).lower().endswith(".ibs"): return None
    held = _im.sha256_of(os.path.join(repo, doc))
    out = {"path": doc, "pinned_sha256_16": row["sha256"][:16] if row else None}
    if held is None: out["absent"] = True
    else: out["sha256_16"] = held[:16]
    return out


def _model_cited(repo, doc):
    """None when `doc` is no model, or is a model in this tree and the file the manifest pins; else why it cannot be
    read: a Reason of kind MODEL_ABSENT for a pinned model that is not in the tree (the state of a clean clone)."""
    import ibis_manifest as _im
    m = model_record(repo, doc)
    if m is None: return None
    man = _im.load(repo)
    if m["pinned_sha256_16"] is None:
        return "the model %s it cites is pinned by no row of %s%s" % (doc, man["path"], (" (%s)" % man["why"]) if man.get("why") else "")
    if m.get("absent"):
        return Reason("the IBIS model %s it cites is not in this tree: the makers' models are withheld from the repository, %s "
                      "pins this one at sha256/16 %s and tools/ibis_fetch.py fetches it from the maker's address" % (
                          doc, man["path"], m["pinned_sha256_16"]), "MODEL_ABSENT", doc)
    if _im.state_of(repo, _im.pin(man, doc))[0] != _im.PRESENT:
        return "%s is not the file %s pins (sha256/16 %s held, %s pinned)" % (doc, man["path"], m["sha256_16"], m["pinned_sha256_16"])
    return None


def _quotes_hold(rec, repo):
    """None when every document a record cites is held, IS the file the record was written from (sha256/16), and says
    what the record quotes from it, on the page the record names where it names one; else why not. A record whose
    document changed since it was read decides nothing until it is read again. A cited document that is a maker's
    MODEL is held to the manifest that pins it, and one that is not in the tree is said to be so (MODEL_ABSENT)."""
    for c in citations(rec):
        doc, q = c["document"], c["quote"]
        p = os.path.join(repo, doc)
        root = os.path.normpath(os.path.abspath(repo))
        if os.path.isabs(str(doc)) or not os.path.normpath(os.path.abspath(p)).startswith(root + os.sep):
            return "the document %s lies outside the repository: a citation names a file of this tree" % doc
        bad = _model_cited(repo, doc)
        if bad: return bad
        if not os.path.isfile(p): return "the document %s it names is not in this tree" % doc
        if c["sha256_16"] and _sha16(p) != c["sha256_16"]:
            return "%s is not the file the record was read from (sha256/16 %s held, %s cited)" % (doc, _sha16(p), c["sha256_16"])
        if q:
            t = _doc_text(p)
            if t is None: return "the text of %s could not be read" % doc
            if _norm(q) not in _norm(t): return "%s does not contain the words quoted from it (%r)" % (doc, q[:60])
            if c["page"] is not None and p.lower().endswith(".pdf"):
                tp = _page_text(p, c["page"])
                if tp is None: return "page %s of %s could not be read" % (c["page"], doc)
                if _norm(q) not in _norm(tp):
                    return "page %s of %s does not contain the words quoted from it (%r)" % (c["page"], doc, q[:60])
    return None


_LISTING = {}


def _listing(path):
    """{document path: sha256/16} as a search listing names them (edge_search.py's lines "== <document> (sha256/16
    <sha>, ..."), or None when the listing cannot be read."""
    try:
        key = (path, os.path.getmtime(path), os.path.getsize(path))
    except OSError:
        return None
    if key not in _LISTING:
        _LISTING[key] = dict(re.findall(r"(?m)^== (\S+) \(sha256/16 ([0-9a-f]{16}),",
                                        open(path, encoding="utf-8", errors="replace").read()))
    return _LISTING[key]


def _searched(rec, repo, rates=None):
    """None, or why a bound or a model has not shown that its documents were SEARCHED for a published transition: the
    data file names a search listing (search_listing: path and sha256/16), and every document the record cites under
    `checked` is in it at the held file's sha256/16. A record that says no document exists (no_document) cites none."""
    if rec.get("kind") not in BOUND_KINDS: return None
    docs = sorted({c["document"] for c in rec.get("checked") or [] if isinstance(c, dict) and c.get("document")})
    if not docs: return None
    sl = (rates if rates is not None else RATES).get("search_listing") or {}
    if not (sl.get("path") and sl.get("sha256_16")):
        return "the data file names no search listing, so nothing shows its documents were searched for a transition time"
    lp = os.path.join(repo, sl["path"])
    if not os.path.isfile(lp): return "the search listing %s is not in this tree" % sl["path"]
    if _sha16(lp) != sl["sha256_16"]:
        return "the search listing %s is not the file the data file names (sha256/16 %s held, %s named)" % (sl["path"], _sha16(lp), sl["sha256_16"])
    held = _listing(lp) or {}
    for d in docs:
        if d not in held: return "the search listing does not hold %s" % d
        if held[d] != _sha16(os.path.join(repo, d)):
            return "the search listing read %s at sha256/16 %s and the held file is %s" % (d, held[d], _sha16(os.path.join(repo, d)))
    return None


def record_holds(rec, repo, rates=None):
    """None when a record's citations hold (_quotes_hold) and, for a bound or a model, its documents were searched
    (_searched); else why not."""
    return _quotes_hold(rec, repo) or _searched(rec, repo, rates)


def _open_drain_for(letter, net, rates=None, repo=None, used=None):
    """The rise of an open-drain net as the data file's `open_drain` records state it, or None: {"edge_ns", "basis",
    "source", "measure"}, or {"source", "unusable": why} when the record's documents do not hold. Attached to the net
    for the reader; it is never the net's governing edge (the fall is). `used` collects the documents read, by sha."""
    for r in (rates or RATES).get("open_drain") or []:
        if any(fnmatch.fnmatchcase(net, pat) for pat in (r.get("nets") or {}).get(letter, ())):
            why = _quotes_hold(r, repo or REPO)
            if why: return {"source": r["id"], "unusable": why}
            if used is not None:
                for c in citations(r): used[c["document"]] = _sha16(os.path.join(repo or REPO, c["document"]))
            rise = r["rise"]
            return {"edge_ns": float(rise["edge_ns"]), "basis": rise["kind"], "source": r["id"],
                    "measure": rise.get("measure")}
    return None


def _interface_records():
    """The interface records that decide a class entry: the STANDARD ones as EDGE_SOURCES holds them (the fixtures
    replace that tuple) and the MODEL and BOUND ones from the data file."""
    rest = [dict(r, rise_ns=float(r["edge_ns"]), covers={k: tuple(v) for k, v in (r.get("covers") or {}).items()})
            for r in RATES["interfaces"] if r.get("kind") in BOUND_KINDS]
    return [dict(s, kind=s.get("kind") or "STANDARD") for s in EDGE_SOURCES] + rest


def edge_source(letter, pattern, rise_ns, repo=None):
    """(status, source, why) for one class entry. status: DECIDED, UNDECIDED, CONTRADICTED or NOT_COVERED (no interface
    record covers the entry, so its nets are asked for their drivers). The data file is the declaration: a board
    table's own rise_ns, where one is written, must agree with it."""
    repo = repo or REPO
    for s in _interface_records():
        if pattern not in (s.get("covers") or {}).get(letter, ()): continue
        bad = record_holds(s, repo)
        if bad: return "UNDECIDED", s, bad
        where = s.get("clause") or s.get("derivation", "")[:90]
        if rise_ns is not None and abs(float(rise_ns) - float(s["rise_ns"])) > 1e-9:
            return "CONTRADICTED", s, "declared %s ns, and %s states %s ns (%s)" % (
                rise_ns, s.get("document") or "pcb_edge_rates.yaml", s["rise_ns"], where)
        return "DECIDED", s, "%s: %s" % (where, s.get("document") or "pcb_edge_rates.yaml %s" % s["id"])
    if rise_ns:
        return "UNDECIDED", None, ("declares %s ns and no held document is named for it in pcb_edge_rates.yaml"
                                   % rise_ns)
    return "NOT_COVERED", None, "no interface record covers the entry"


# ------------------------------------------------------------------------------------------------------------------
# A DECLARED ALLOWANCE CARRIES ITS BASIS AND THE LENGTH IT HOLDS (29 September 2026, stream csi, MESHSAT-1357; session
# decisions CSI-D1 and CSI-D2, under the owner's standing rule of 26 September 2026, authority SESSION).
# `edge_allow` in boards/<letter>.json answers a net that may be electrically long, beside an impedance target and a
# series termination. Until today an entry was a pattern and a sentence, and a sentence turned a net green (finding
# F-Q1's W5SI-D3 refused to write one for that reason: "a declaration names what holds a net's length"). So:
#   CSI-D1  an entry answers a net only when it carries its basis the way a record of pcb_edge_rates.yaml does: `why`,
#           `ruled_by`, and a citation (`document`, its `sha256_16`, `page` or `where`, the words quoted in `quote`, and
#           any further citations under `checked`), held by the same checks (_cite_shape, _quotes_hold) on every run.
#           An entry that does not hold is refused and FAILS the reading, as a refused record does: the declaration is
#           wrong, and every net it names is left layout-bound. Every document a held entry cites is an input of the
#           reading by sha. Since the independent check of 29 September 2026 (its B2 and m7) an entry is also refused
#           when its pattern has fewer than three characters that are no wildcard, its own quote is shorter than five
#           words, it cites a PDF with no page, or it cites a file outside the repository (_quotes_hold, for every
#           record). Reverse: accept an entry with `why` alone in allow_refusal.
#   CSI-D2  an entry states `max_mm`, the longest the layout may route a net it answers, with `max_mm_basis`; an entry
#           with none is refused (the check's B2). The number is tied to what the entry cites (allow_limit): its
#           `checked` rows quote the lengths measured on a reference layout ("<net> <x> mm") and that layout's delay
#           ("t_pd <x> ps/mm", stated as `reference_ps_per_mm`), and max_mm may be at most the longest quoted length
#           times that delay over this board's slowest (worst_delay), so the limit holds the delay the reference runs
#           at on whichever stack the layout is drawn on. The schematic table hands max_mm to the layout (row
#           ["length_limits"]; the net reads "pending the layout"), and the routed half holds EVERY net a held entry
#           names to it first, whatever its class, its rise time, its critical length or any series resistor on it (the
#           check's B1 and m10): past it the net is named OVER ITS DECLARED LIMIT and the routed verdict fails.
#           edge_length_routed decides no rule yet, so the limit binds a rule only once one names that reading.
#           Reverse: drop the length test in allow_answers and allow_limit.
# ------------------------------------------------------------------------------------------------------------------
LENGTH_QUOTE = re.compile(r"(?<!\S)(\S+)\s+(\d+(?:\.\d+)?)\s*mm(?![\w/])")
TPD_QUOTE = re.compile(r"t_pd\s+(\d+(?:\.\d+)?)\s*ps/mm")
ALLOW_QUOTE_WORDS = 5        # the entry's own quote: a sentence of its document, not a word (the check's m7)
ALLOW_PATTERN_LITERALS = 3   # a pattern names nets: at least three characters that are no wildcard (m7)


def allow_limit(entry, tpd):
    """(limit_mm, how) or (None, why not): the longest a net may be routed on THIS board by what the entry cites. The
    lengths its `checked` rows quote ("<net> <x> mm", measured on a reference layout) are scaled by the delay: the
    reference layout's own t_pd, which a checked row quotes ("t_pd <x> ps/mm") and the entry states as
    `reference_ps_per_mm`, over this board's slowest t_pd, so the limit holds the same delay the reference runs at."""
    lens = [float(m.group(2)) for c in entry.get("checked") or [] if isinstance(c, dict)
            for m in LENGTH_QUOTE.finditer(str(c.get("quote") or ""))]
    if not lens: return None, "no checked row quotes the measured length its max_mm rests on (\"<net> <x> mm\")"
    ref = entry.get("reference_ps_per_mm")
    if isinstance(ref, bool) or not isinstance(ref, (int, float)) or ref <= 0:
        return None, "no reference_ps_per_mm: the delay per millimetre of the layout the length was measured on"
    quoted = [float(m.group(1)) for c in entry.get("checked") or [] if isinstance(c, dict)
              for m in TPD_QUOTE.finditer(str(c.get("quote") or ""))]
    if not any(abs(q - float(ref)) < 0.0005 for q in quoted):
        return None, "reference_ps_per_mm %s is quoted by no checked row (\"t_pd <x> ps/mm\")" % ref
    if not tpd: return None, "no declared stack to scale the reference length to"
    lim = max(lens) * float(ref) / float(tpd)
    return lim, "%.2f mm measured, times %.3f / %.3f ps/mm = %.2f mm" % (max(lens), float(ref), float(tpd), lim)


def allow_refusal(entry, tpd=None):
    """None, or why an edge_allow entry cannot answer a net: its shape, and its max_mm against the lengths it cites
    scaled to this board (allow_limit). Whether its documents say what it quotes is asked by _quotes_hold."""
    if not isinstance(entry, dict) or not str(entry.get("pattern") or "").strip(): return "an entry with no pattern"
    if len(re.sub(r"[*?\[\]!]", "", str(entry["pattern"]))) < ALLOW_PATTERN_LITERALS:
        return "the pattern %r names no nets: fewer than %d characters that are no wildcard" % (entry["pattern"], ALLOW_PATTERN_LITERALS)
    for f in ("why", "ruled_by"):
        if not str(entry.get(f) or "").strip(): return "no %s" % f
    if not entry.get("document"):
        return "no basis: an allowance cites the document it rests on (document, sha256_16, page or where, quote)"
    if len(str(entry.get("quote") or "").split()) < ALLOW_QUOTE_WORDS:
        return "the quote %r is shorter than %d words: an allowance quotes the sentence it rests on" % (entry.get("quote"), ALLOW_QUOTE_WORDS)
    for c in citations(entry):
        if str(c["document"]).lower().endswith(".pdf") and c["page"] is None:
            return "%s cites the PDF %s with no page: a PDF is cited by its page" % (c["at"], c["document"])
    mm = entry.get("max_mm")
    if mm is None:
        return "no max_mm: an allowance holds the net to a length, or it answers nothing"
    if isinstance(mm, bool) or not isinstance(mm, (int, float)) or mm <= 0:
        return "max_mm %r is not a length in millimetres" % (mm,)
    if not str(entry.get("max_mm_basis") or "").strip(): return "a max_mm with no max_mm_basis"
    bad = _cite_shape(entry)
    if bad: return bad
    lim, how = allow_limit(entry, tpd)
    if lim is None: return how
    if float(mm) > lim + 1e-9:
        return "max_mm %.2f is above what its checked rows support on this board (%s)" % (float(mm), how)
    return None


def load_allow(letter, repo=None, used=None, tpd=None):
    """(the entries of the board's edge_allow that answer, [why each other entry is refused]). `used` collects the
    documents the held entries cite, by sha. `tpd` is the board's slowest delay (worst_delay), read here when not given."""
    repo = repo or REPO
    if tpd is None:
        try: tpd = worst_delay(letter)[0]
        except Exception: tpd = None
    held, refused = [], []
    for i, e in enumerate(_bt.value(letter, "edge_allow", []) or []):
        why = allow_refusal(e, tpd) or _quotes_hold(e, repo)
        if why:
            refused.append("edge_allow[%d] (%s): %s" % (i, e.get("pattern") if isinstance(e, dict) else e, why))
            continue
        held.append(e)
        if used is not None:
            for c in citations(e): used[c["document"]] = _sha16(os.path.join(repo, c["document"]))
    return held, refused


def allow_answers(entry, length_mm=None):
    """(answers, words) for one net an entry's pattern matches. At the schematic phase (no length) it answers and says
    the length the layout must hold the net to, pending the layout; at the routed phase it answers only while the routed
    length is at most the entry's max_mm. An entry with no max_mm answers nothing (B2 of the check)."""
    mm = entry.get("max_mm")
    if mm is None: return False, "an edge_allow entry with no max_mm holds no length and answers nothing"
    if length_mm is not None and float(length_mm) > float(mm):
        return False, "routed %.1f mm, past the %.1f mm its edge_allow declaration holds it to (%s)" % (
            float(length_mm), float(mm), str(entry.get("max_mm_basis", ""))[:80])
    if length_mm is not None:
        return True, "declared in edge_allow: routed %.1f mm, within its %.1f mm" % (float(length_mm), float(mm))
    return True, "declared in edge_allow, pending the layout: at most %.1f mm (%s)" % (float(mm), str(entry.get("why", ""))[:60])


# ------------------------------------------------------------------------------------------------------------------
# THE DRIVERS OF ONE NET (ER-D1 to ER-D9, see the block above and the data file's header)
# ------------------------------------------------------------------------------------------------------------------
def _prefix(ref):
    m = re.match(r"^([A-Za-z_]+?)(?=\d|$)", ref or "")
    return (m.group(1) if m else ref or "").rstrip("_")


def _is_connector(prefix):
    """A connector's, a wire land's or a pad's reference (intent_checks.is_connector's test): its value field names
    what it carries, and whatever drives its pin is on the far side."""
    return prefix == "J" or prefix.startswith(("J_", "P_", "PAD", "W_"))


def _family_for(value, families):
    for f in families:
        for rx in f.get("parts") or []:
            if re.match(rx, value or ""): return f
    return None


def _is_input(fam, pin, pinfunction):
    if str(pin) in {str(x) for x in fam.get("input_pins") or []}: return True
    rx = fam.get("inputs")
    return bool(rx and re.match(rx, pinfunction or ""))


MAKER_KINDS = ("STANDARD", "IBIS", "DATASHEET")


def _cand_key(c):
    """The fastest candidate first; at a tie a maker's figure before a model or a bound, and a part on the net before
    one beyond a connector or across a resistor, so the reading names the most direct source of the number."""
    return (c[0], 0 if c[1] in MAKER_KINDS else 1, 1 if c[3].startswith(("beyond", "across")) else 0)


def net_edge(cands):
    """THE GOVERNING EDGE OF ONE NET, from its candidates [(edge_ns, kind, family id, how)] (ER-D13).

    The governing edge is the fastest edge any driver on the net can produce. A driver with a MODEL or a BOUND has no
    published minimum, so its fastest edge is not known: ONE such driver makes the net `decided_by: BOUND`, whatever
    the other drivers' makers publish. `edge_ns` is the fastest candidate of all (the number the critical length is
    computed from); `basis`, `source` and `by` name the candidate that GOVERNS: the fastest of the drivers without a
    published minimum when there is one, else the fastest maker's figure. `maker_edge_ns` is the fastest published
    figure on the net, recorded for the reader and deciding nothing while a bound governs; `bound_drivers` names every
    driver on the net whose maker publishes no minimum."""
    fastest = min(cands, key=_cand_key)
    bounds = sorted((c for c in cands if c[1] in BOUND_KINDS), key=_cand_key)
    makers = sorted((c for c in cands if c[1] in MAKER_KINDS), key=_cand_key)
    gov = bounds[0] if bounds else fastest
    seen, named = set(), []
    for c in bounds:
        if (c[2], c[3]) in seen: continue
        seen.add((c[2], c[3])); named.append("%s: %s" % (c[2], c[3]))
    return {"edge_ns": round(fastest[0], 4), "basis": gov[1], "source": gov[2], "by": gov[3],
            "decided_by": "BOUND" if bounds else "MAKER",
            "maker_edge_ns": round(makers[0][0], 4) if makers else None,
            "maker_by": ("%s: %s" % (makers[0][2], makers[0][3])) if makers else None,
            "bound_drivers": named}


class _Ctx:
    """What resolving the nets of one board needs, read once."""
    def __init__(self, letter, nets, values, rates, repo, signals, rails, no_far=False, netlists=None):
        self.letter, self.nets, self.values, self.rates, self.repo = letter, nets, values, rates, repo
        self.signals, self.rails = set(signals), rails
        self.no_far = no_far                   # a continued board: its own connectors lead back, never further
        self.netlists = netlists if netlists is not None else {}   # letter -> path of the netlist a continuation reads
        self.far_read = {}                     # letter -> {"path", "sha256_16"} of every other board's netlist read
        self._others = {}
        self.used_docs = {}
        import ibis_manifest as _im
        self.manifest = _im.load(repo)         # what pins each model (ER-D17); a model it does not pin is not read
        self.models = {}                       # every model ASKED for: file -> {"path", "sha256_16" | "absent", "pinned_sha256_16"}
        self.fam_ok = {}
        self.contradicted = {}                               # family id -> why: the data file is wrong, a FAIL
        self.parts_on = {}
        for n, d in nets.items():
            for r, p, f, t in d["nodes"]: self.parts_on.setdefault(r, []).append((p, f, n))

    def family_usable(self, fam):
        """None, or why the family's record cannot decide anything (its document is not held or does not say it)."""
        if fam["id"] not in self.fam_ok:
            why = record_holds(fam, self.repo, self.rates)
            if not why and fam.get("kind") == "IBIS":
                why = self._ibis_check(fam)
                if why and why.startswith("CONTRADICTED"): self.contradicted[fam["id"]] = why
            self.fam_ok[fam["id"]] = why
            for d in [c["document"] for c in citations(fam)]:           # a model is recorded under model_N,
                m = model_record(self.repo, d)                          # read or absent; a document only when used
                if m is not None: self.models[d] = m
                elif not why: self.used_docs[d] = _sha16(os.path.join(self.repo, d))
        return self.fam_ok[fam["id"]]

    def _ibis_check(self, fam):
        import ibis_read, ibis_manifest as _im
        ib = fam["ibis"]
        man = self.manifest
        if man.get("why"):
            return "nothing pins the IBIS model %s: %s" % (ib["file"], man["why"])
        row = _im.pin(man, ib["file"])
        if row is None:
            return "the model manifest %s names no %s, so nothing pins the file the record cites%s" % (
                man["path"], ib["file"], ("; it refuses: %s" % "; ".join(man["refusals"])[:200]) if man.get("refusals") else "")
        if ib.get("sha256_16") and not row["sha256"].startswith(ib["sha256_16"]):
            return "CONTRADICTED: the record cites %s at sha256/16 %s and %s pins it at %s" % (
                ib["file"], ib["sha256_16"], man["path"], row["sha256"][:16])
        p = os.path.join(self.repo, ib["file"])
        st, held = _im.state_of(self.repo, row)
        if st == _im.ABSENT:
            self.models[ib["file"]] = {"path": ib["file"], "absent": True, "pinned_sha256_16": row["sha256"][:16]}
            return Reason("the IBIS model %s is not in this tree: the makers' models are withheld from the repository, %s "
                          "pins this one at sha256/16 %s and tools/ibis_fetch.py fetches it from the maker's address" % (
                              ib["file"], man["path"], row["sha256"][:16]), "MODEL_ABSENT", ib["file"])
        self.models[ib["file"]] = {"path": ib["file"], "sha256_16": held[:16], "pinned_sha256_16": row["sha256"][:16]}
        if st == _im.DIFFERS:
            return "%s is not the file %s pins (sha256 %s held, %s pinned)" % (ib["file"], man["path"], held, row["sha256"])
        if ib.get("sha256_16") and _sha16(p) != ib["sha256_16"]:
            return "%s is not the file the record was read from (sha256/16 %s held, %s cited)" % (ib["file"], _sha16(p), ib["sha256_16"])
        model = self._ibis(fam)
        e, how = ibis_read.fastest(model, ib["component"], ib.get("models"))
        stated = fam.get("edge_ns")
        if e is None: return "the IBIS file gives no driving pin for %s: %s" % (ib["component"], how)
        if not isinstance(stated, (int, float)) or abs(float(stated) - e) > 0.0005:
            return "CONTRADICTED: the record states %s ns and %s gives %.4f ns (%s)" % (stated, ib["file"], e, how)
        flagged = sorted(str(p_) for p_, _h in ibis_read.flagged_pins(model, ib["component"], ib.get("models")))
        named = sorted(str(x) for x in fam.get("flagged_pins") or [])
        if flagged != named:
            return ("CONTRADICTED: the record names the pins %s as having a [Ramp] cell the model's own V-t table "
                    "contradicts, and %s gives %s" % (named or "none", ib["file"], flagged or "none"))
        kw, cell = ibis_read.fastest_cite(model, ib["component"], ib.get("models"))
        if ib.get("keyword") is not None and _norm(str(ib["keyword"])) != _norm(kw or ""):
            return "CONTRADICTED: the record cites %r and the number is under %r in %s" % (ib["keyword"], kw, ib["file"])
        if ib.get("ramp") is not None and str(ib["ramp"]).strip() != (cell or ""):
            return "CONTRADICTED: the record quotes the cell %r and %s writes %r" % (ib["ramp"], ib["file"], cell)
        return None

    def _ibis(self, fam):
        import ibis_read
        ib = fam["ibis"]
        model = ibis_read.load(os.path.join(self.repo, ib["file"]))
        if ib.get("selector_add"):
            model = dict(model, selectors=dict(model["selectors"]))
            for sel, extra in ib["selector_add"].items():
                model["selectors"][sel.lower()] = list(model["selectors"].get(sel.lower(), [])) + list(extra)
        return model

    def pin_candidates(self, ref, pin, pf, net):
        """([(edge_ns, kind, family id, how)], [reason]) for one node of the net."""
        pre = _prefix(ref)
        val = self.values.get(ref, "")
        if _is_connector(pre):
            return self.far(ref, net)
        if not pre.startswith(DRIVER_PREFIXES): return [], []
        fam = _family_for(val, self.rates["families"])
        if fam is None:
            return [], ["%s %s: no family in pcb_edge_rates.yaml" % (ref, " ".join(val.split()[:3]))]
        k = fam["kind"]
        if k == "NOT_A_DRIVER": return [], []
        if k == "CONNECTOR": return self.far(ref, net)
        if k == "PASSIVE_SWITCH":
            if str(pin) in {str(x) for x in fam.get("through_pins") or []} or \
               (fam.get("through") and re.match(fam["through"], pf or "")): return self.far(ref, net)
            if _is_input(fam, pin, pf): return [], []
            return [], ["%s pin %s %s (%s): neither a through pin nor a control input of the passive switch as its "
                        "record names them" % (ref, pin, pf or "", fam["id"])]
        if _is_input(fam, pin, pf): return [], []
        why = self.family_usable(fam)
        if why: return [], [_because("%s %s (%s): %s" % (ref, " ".join(val.split()[:2]), fam["id"], why), why)]
        if k == "IBIS":
            import ibis_read
            ib = fam["ibis"]
            sup = fam.get("supply")
            if sup:
                bad = [p for (p, f_, n) in self.parts_on.get(ref, []) if str(p) in {str(x) for x in sup.get("pins") or []}
                       and not re.search(sup.get("rail", "$^"), n)]
                if bad: return [], ["%s (%s): supply pin(s) %s are not on a rail the admitted models cover (%s)" % (
                    ref, fam["id"], ", ".join(bad), sup.get("rail"))]
            st, e, how = ibis_read.pin_edge(self._ibis(fam), ib["component"], pin, ib.get("models"), ib.get("pin_key", "number"))
            if st == "INPUT": return [], []
            if st == "UNKNOWN": return [], ["%s (%s): %s" % (ref, fam["id"], how)]
            if st == "FLAGGED":         # no maker's figure for this pin: the instantaneous bound (ER-D8, ER-D16)
                return [(0.0, "BOUND", fam["id"], "%s %s" % (ref, how))], []
            return [(e, "IBIS", fam["id"], "%s %s" % (ref, how))], []
        for pe in fam.get("pin_edges") or []:
            if re.match(pe["match"], pf or "") or str(pin) in {str(x) for x in pe.get("pins") or []}:
                return [(float(pe["edge_ns"]), pe["kind"], fam["id"], "%s pin %s %s (%s)" % (ref, pin, pf or "", pe.get("conditions", pe["kind"])[:60]))], []
        return [(float(fam["edge_ns"]), k, fam["id"], "%s pin %s %s" % (ref, pin, pf or ""))], []

    def other(self, letter):
        """(_Ctx, None) for another board of this set, read from its committed netlist, or (None, why)."""
        if letter not in self._others:
            path = self.netlists.get(letter)
            if path is None:
                try:
                    import phase_artefacts as _pa
                    path = _pa.netlist(letter)
                except Exception:
                    path = None
            if not path or not os.path.exists(path):
                self._others[letter] = (None, "board %s's netlist is not in this tree" % letter)
            else:
                nets2, values2 = read_netlist(path)
                sig2 = [n for n, d in nets2.items() if not (n.startswith("unconnected-") or n.startswith("+") or GROUND.search(n))]
                self._others[letter] = (_Ctx(letter, nets2, values2, self.rates, self.repo, sig2, set(), no_far=True), None)
                self.far_read[letter] = {"path": _shown(path), "sha256_16": _sha16(path)}
        return self._others[letter]

    def far(self, ref, net):
        """The drivers beyond a connector or a passive switch's through pin, from the far_ends records. A record that
        names the boards the net continues onto is answered from those boards' own netlists, pin by pin; one that
        names families is answered by each family's fastest figure (ER-D7). ON A CONTINUED BOARD (no_far) a record
        that names boards is the link back to the set and adds nothing (the board that asked reads every board of the
        net itself); a record that names families leads off the set and is answered; a connector no record names is a
        reason, as it is on the board that asked."""
        for fe in self.rates["far_ends"]:
            if fe["board"] != self.letter: continue
            if not any(fnmatch.fnmatchcase(net, pat) for pat in fe["nets"]): continue
            via = fe.get("via")
            if via and not any(fnmatch.fnmatchcase(ref, v) for v in via): continue
            cands, reasons = [], []
            if self.no_far and fe.get("continues"): return [], []
            for L2 in fe.get("continues") or []:
                c2, why = self.other(L2)
                if c2 is None: reasons.append("beyond %s (far end %s): %s" % (ref, fe["id"], why)); continue
                if net not in c2.nets:
                    reasons.append("beyond %s (far end %s): board %s's netlist has no net %s" % (ref, fe["id"], L2, net)); continue
                b2, cc, rr = c2.resolve(net, quiet=True)
                cands += [(e, k, fid, "beyond %s on board %s: %s" % (ref, L2.upper(), how)) for e, k, fid, how in cc]
                reasons += [_because("beyond %s on board %s: %s" % (ref, L2.upper(), w), w) for w in rr]
                self.used_docs.update(c2.used_docs)
                self.models.update(c2.models)
                self.contradicted.update(c2.contradicted)
            if fe.get("continues"): return cands, reasons
            fams = {f["id"]: f for f in self.rates["families"]}
            for fid in fe.get("families") or []:
                fam = fams[fid]
                if fam["kind"] in NON_EDGE_KINDS: continue
                why = self.family_usable(fam)
                if why: reasons.append(_because("beyond %s (%s, %s): %s" % (ref, fe["id"], fid, why), why)); continue
                if fam["kind"] == "IBIS":
                    import ibis_read
                    fl = ibis_read.flagged_pins(self._ibis(fam), fam["ibis"]["component"], fam["ibis"].get("models"))
                    if fl:      # which pin is on the far side is not read, and one of them has no figure (ER-D16)
                        cands.append((0.0, "BOUND", fid, "beyond %s (far end %s): %s, whose pin %s has a [Ramp] cell the "
                                      "model's own V-t table contradicts" % (ref, fe["id"], fid, fl[0][0])))
                        continue
                # the part's fastest pin (ER-D7): which of its pins is on the far side is not read
                opts = [(float(fam["edge_ns"]), fam["kind"])] + [(float(pe["edge_ns"]), pe["kind"]) for pe in fam.get("pin_edges") or []]
                e, kind = min(opts)
                cands.append((e, kind, fid, "beyond %s (far end %s): %s" % (ref, fe["id"], fid)))
            return cands, reasons
        return [], ["reaches %s: the driver beyond it is not named in pcb_edge_rates.yaml far_ends" % ref]

    def local(self, net):
        cands, reasons = [], []
        for r, p, f, t in self.nets[net]["nodes"]:
            c, why = self.pin_candidates(r, p, f, net)
            cands += c; reasons += why
        return cands, reasons

    def resolve(self, net, quiet=False):
        """(best candidate or None, [candidates], [reasons]). A net with any reason is UNDECIDED. `quiet`: a continued
        board's net with no driver of its own is not a reason (its drivers may all be on the board that asked)."""
        cands, reasons = self.local(net)
        for r, p, f, t in self.nets[net]["nodes"]:          # one hop through a two-pin series resistor (ER-D6)
            if _prefix(r) != "R": continue
            pins = self.parts_on.get(r, [])
            if len(pins) != 2: continue
            other = pins[1][2] if pins[0][2] == net else pins[0][2]
            if other == net or other not in self.signals: continue
            c2, w2 = self.local(other)
            cands += [(e, k, fid, "across %s from %s: %s" % (r, other, how)) for e, k, fid, how in c2]
            reasons += [_because("across %s from %s: %s" % (r, other, w), w) for w in w2]
        if not reasons and not cands:
            # a net nothing on the board drives, whose driver a far_ends record names by the land it touches (a
            # bench probe on a test pad): that record is its driver (ER-D7); without one the net is UNDECIDED
            for r, p, f, t in self.nets[net]["nodes"]:
                if any(fe["board"] == self.letter and fe.get("undriven_land") and any(fnmatch.fnmatchcase(net, x) for x in fe["nets"])
                       and any(fnmatch.fnmatchcase(r, v) for v in fe.get("via") or []) for fe in self.rates["far_ends"]):
                    c, w = self.far(r, net)
                    cands += c; reasons += w
                    break
        if not reasons and not cands and not quiet:
            reasons = ["no part on the net, or one series resistor away, drives it"]
        best = min(cands, key=_cand_key) if cands else None
        return best, cands, reasons


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


def schematic_table(net_path, letter=None, intent_path=None, facts=None, repo=None, netlists=None):
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
    allow_docs = {}
    allow, allow_bad = load_allow(letter, repo, allow_docs, tpd=tpd)
    for x in allow_bad: res["fails"].append("edge_allow refused: %s" % x)

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

    # THE COUNTS, and the sums a reader can check (tests/test_edge_length.py holds them on every fixture and on the
    # committed netlists): signal_nets = low_speed_nets + decided_nets + undecided_nets + contradicted_nets;
    # decided_nets = maker_edge_nets + bound_edge_nets (ER-D13: decided by a published figure on every driver, or by a
    # bound); may_be_long_nets = answered_nets + layout_bound_nets; layout_bound_nets = maker_held_nets +
    # bound_decided_nets.
    counts = {"signal_nets": len(signals), "decided_nets": 0, "undecided_nets": 0, "low_speed_nets": 0,
              "contradicted_nets": 0, "may_be_long_nets": 0, "answered_nets": 0, "layout_bound_nets": 0,
              "classes": len(rows), "maker_edge_nets": 0, "bound_edge_nets": 0, "bound_decided_nets": 0,
              "maker_held_nets": 0, "undecided_no_declaration_nets": 0, "undecided_model_absent_nets": 0,
              "undecided_other_nets": 0, "allowed_nets": 0}
    for x in RATES_REFUSALS: res["fails"].append("edge data refused: %s" % x)
    res["inputs"]["edge_rates"] = {"path": _shown(RATES["path"]), "sha256_16": RATES.get("sha16")}
    ctx = _Ctx(letter, nets, values, RATES, repo, signals, rails, netlists=netlists)
    used = {}
    for pat in sorted(rows):
        row = rows[pat]
        row["drivers"] = {v: sorted(rs) for v, rs in sorted(row["drivers"].items())}
        nn = len(row["nets"])
        row["net_edges"], row["undecided"], row["undecided_kind"] = {}, {}, {}
        if row["class"] == LOW_CLASS and not row["rise_ns"]:
            row.update(status="LOW_SPEED_OR_DC", why="declared slow or DC with its basis; no edge is asked of it")
            counts["low_speed_nets"] += nn
            continue
        if row["class"] == "UNKNOWN":
            row.update(status="UNDECIDED", why="no signal-class declaration names these nets, so neither their class "
                                               "nor their edge is known")
            row["undecided"] = {n: [Reason("no signal-class declaration", "NO_DECLARATION")] for n in row["nets"]}
            row["undecided_kind"] = {n: "NO_DECLARATION" for n in row["nets"]}
            counts["undecided_nets"] += nn
            counts["undecided_no_declaration_nets"] += nn
            continue
        st, src, why = edge_source(letter, pat, row["rise_ns"], repo)
        row.update(why=why, source=(src or {}).get("id"), document=(src or {}).get("document"))
        if st == "CONTRADICTED":
            row["status"] = st
            counts["contradicted_nets"] += nn
            res["fails"].append("%s (%s, %d net(s)): %s" % (pat, row["class"], nn, why))
            continue
        for c in citations(src) if src else []:           # a model an interface record cites: asked for, read or absent
            m = model_record(repo, c["document"])
            if m is not None: ctx.models[c["document"]] = m
        if st == "DECIDED":
            kind = src.get("kind") or "STANDARD"
            for n in row["nets"]:
                by = "class entry %s, %s" % (pat, src["id"])
                row["net_edges"][n] = net_edge([(float(src["rise_ns"]), kind, src["id"], by)])
            for c in citations(src):
                if c["document"] not in ctx.models: used[c["document"]] = _sha16(os.path.join(repo, c["document"]))
        elif st == "UNDECIDED":
            row["undecided"] = {n: [why] for n in row["nets"]}
        else:                                                 # NOT_COVERED: ask each net for its drivers
            for n in row["nets"]:
                best, cands_n, reasons = ctx.resolve(n)
                if reasons: row["undecided"][n] = reasons
                else: row["net_edges"][n] = net_edge(cands_n)
        for n, e in row["net_edges"].items():
            od = _open_drain_for(letter, n, RATES, repo, used)
            if od: e["rising"] = od
        nd, nu = len(row["net_edges"]), len(row["undecided"])
        row["undecided_kind"] = {n: reasons_kind(rs) for n, rs in row["undecided"].items()}
        row["undecided_models"] = {n: sorted({r.file for r in rs if getattr(r, "file", None)}) for n, rs in row["undecided"].items()
                                   if any(getattr(r, "file", None) for r in rs)}
        for kd in row["undecided_kind"].values():
            counts[{"NO_DECLARATION": "undecided_no_declaration_nets", "MODEL_ABSENT": "undecided_model_absent_nets"}.get(
                kd, "undecided_other_nets")] += 1
        row["status"] = "DECIDED" if not nu else ("UNDECIDED" if not nd else "PARTIAL")
        if row["status"] != "DECIDED" and st == "NOT_COVERED":
            row["why"] = "%d of %d net(s) have a driver the data file does not decide" % (nu, nn)
        counts["undecided_nets"] += nu
        counts["decided_nets"] += nd
        if not nd: continue
        row["rise_ns"] = min(e["edge_ns"] for e in row["net_edges"].values())
        crit_of = {n: float(e["edge_ns"]) * 1000.0 / (float(k) * tpd) for n, e in row["net_edges"].items()}
        row["critical_mm"] = round(min(crit_of.values()), 1)
        row["critical_by_net"] = {n: round(c, 1) for n, c in sorted(crit_of.items())}
        row["bound_nets"] = sorted(n for n, e in row["net_edges"].items() if e["decided_by"] == "BOUND")
        row["maker_nets"] = sorted(n for n, e in row["net_edges"].items() if e["decided_by"] == "MAKER")
        counts["bound_edge_nets"] += len(row["bound_nets"])
        counts["maker_edge_nets"] += len(row["maker_nets"])
        # a board with no declared outline has no corner-to-corner run to compare with, so every net of the class may
        # be long (the second independent check of 26 September: a missing extent read as "never long")
        long_nets = [n for n in row["net_edges"] if extent is None or crit_of[n] < extent]
        row["may_be_long"] = bool(long_nets)
        if not long_nets:
            row["needs"] = "nothing: the critical length is past the board's corner-to-corner run"
            row["answered"], row["layout_bound"], row["bound_decides"], row["maker_holds"] = {}, [], [], []
            continue
        row["needs"] = "an impedance target, a series termination or a declaration, or every net under %.1f mm" % row["critical_mm"]
        ans, bound, limits = {}, [], {}
        for n in sorted(long_nets):
            c, how = cls_of(n)
            if c in targets:
                ans[n] = "impedance target on class %s (%s, from the %s)" % (c, ", ".join("%s %s" % kv for kv in sorted(targets[c].items())), how)
            elif n in series:
                ans[n] = "series resistor %s (a screen)" % "; ".join(series[n])[:80]
            else:
                dec = next((e for e in allow if fnmatch.fnmatch(n, e.get("pattern", ""))), None)
                if dec:
                    ans[n] = allow_answers(dec)[1]
                    counts["allowed_nets"] += 1
                    if dec.get("max_mm") is not None: limits[n] = float(dec["max_mm"])
                else: bound.append(n)
        row["answered"] = ans
        row["length_limits"] = limits
        row["layout_bound"] = bound
        # THE BOUND DECIDES (ER-D9 with ER-D13): a layout-bound net on which at least one driver has no published
        # minimum. Its governing edge is that driver's bound and so is its critical length, whatever the other drivers'
        # makers publish. A layout-bound net is held by a maker's figure only when EVERY driver on it has one. (Until
        # the independent check of 27 September 2026 a net was called maker-held when ANY maker's figure on it gave a
        # length, which named 40 nets by a figure that did not govern them.)
        row["bound_decides"] = [n for n in bound if row["net_edges"][n]["decided_by"] == "BOUND"]
        row["maker_holds"] = [n for n in bound if row["net_edges"][n]["decided_by"] == "MAKER"]
        counts["may_be_long_nets"] += len(long_nets)
        counts["answered_nets"] += len(ans)
        counts["layout_bound_nets"] += len(bound)
        counts["bound_decided_nets"] += len(row["bound_decides"])
        counts["maker_held_nets"] += len(row["maker_holds"])
    res["rows"] = [rows[p] for p in sorted(rows)]
    res["counts"] = counts
    if (RATES.get("search_listing") or {}).get("path"):
        sl = RATES["search_listing"]
        res["inputs"]["search_listing"] = {"path": sl["path"], "sha256_16": _sha16(os.path.join(repo, sl["path"]))}
    # WHAT THE READING DOES NOT ASK (ER-D2, an instrument limit said out loud): a relay's contact, a mechanical switch
    # and a transformer's winding make or pass an edge and are no U or Q part, so no record is asked for them
    slow = {n for r in rows.values() if r.get("status") == "LOW_SPEED_OR_DC" for n in r["nets"]}
    unasked = {}
    for n in signals:
        if n in slow: continue
        for r, _p, _f, _t in nets[n]["nodes"]:
            pre = _prefix(r)
            if pre in UNASKED_PREFIXES or pre.startswith("SW"): unasked.setdefault(n, set()).add(r)
    counts["unasked_part_nets"] = len(unasked)
    if unasked:
        res["notes"].append("%d signal net(s) outside LOW_SPEED_OR_DC carry a relay, a switch or a transformer, which the "
                            "reading asks for no edge (ER-D2, an instrument limit): %s%s" % (
                                len(unasked), ", ".join("%s (%s)" % (n, "/".join(sorted(rs))) for n, rs in sorted(unasked.items())[:12]),
                                " ..." if len(unasked) > 12 else ""))
    # a record the maker's own file contradicts makes every length computed from it wrong: a FAIL, as a declared
    # rise time its document contradicts has been since 26 September
    for L2, rec in sorted(ctx.far_read.items()):
        res["inputs"]["far_netlist_%s" % L2] = rec
    for fid, why in sorted(ctx.contradicted.items()):
        res["fails"].append("pcb_edge_rates.yaml family %s: %s" % (fid, why))
    # every held document this board's edges are taken from, by sha, so a corrected transcription is seen; and every
    # document a held edge_allow entry rests on (CSI-D1)
    used.update(ctx.used_docs)
    used.update(allow_docs)
    for d in list(used):
        m = model_record(repo, d)
        if m is not None:
            ctx.models.setdefault(d, m); del used[d]
    for i, d in enumerate(sorted(used), 1):
        res["inputs"]["document_%d" % i] = {"path": d, "sha256_16": used[d]}
    # THE MODELS (ER-D17): the manifest that pins them, every model this reading asked for (read, or absent), and the
    # state of that set. A model is never recorded as a document: it is not in the repository, and what dates it is
    # its pin in the tracked manifest (rules_status.PINNED_INPUTS).
    man = ctx.manifest
    if man.get("sha256_16"):
        res["inputs"]["ibis_manifest"] = {"path": man["path"], "sha256_16": man["sha256_16"]}
    for x in man.get("refusals") or []: res["fails"].append("model manifest refused: %s" % x)
    asked = [ctx.models[f] for f in sorted(ctx.models)]
    for i, m in enumerate(asked, 1):
        res["inputs"]["model_%d" % i] = dict(m)
    absent = [m["path"] for m in asked if m.get("absent")]
    differ = [m["path"] for m in asked if not m.get("absent") and m.get("sha256_16") != m.get("pinned_sha256_16")]
    import ibis_manifest as _im
    res["inputs"]["model_state"] = {
        "state": _im.set_state([_im.DIFFERS if m["path"] in differ else (_im.ABSENT if m.get("absent") else _im.PRESENT) for m in asked]),
        "asked": len(asked), "present": len(asked) - len(absent), "absent": len(absent), "absent_files": absent,
        "manifest": man["path"], "how_to_fetch": "python3 v2/ecad/tools/ibis_fetch.py --fetch"}
    counts["models_asked"] = len(asked)
    counts["models_absent"] = len(absent)
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


def _reason_summary(r):
    """The distinct reasons a row's nets are undecided, most frequent first."""
    import collections
    c = collections.Counter()
    for rs in (r.get("undecided") or {}).values():
        for x in rs: c[x] += 1
    if not c: return r.get("why") or ""
    return "; ".join("%s%s" % (x, " (x%d)" % k if k > 1 else "") for x, k in c.most_common(3))


def _basis_of(r):
    """How a row's fastest decided edge is known: STANDARD, IBIS, DATASHEET, or a MODEL or BOUND. At equal edges a net
    a bound governs is named before one a maker's figure governs (ER-D13)."""
    ne = r.get("net_edges") or {}
    if not ne: return "?"
    e = min(ne.values(), key=lambda x: (x["edge_ns"], 0 if x.get("decided_by") == "BOUND" else 1))
    return "%s %s" % (e["basis"], e["source"])


def _layout_bound_groups(r, k_tpd=None):
    """[(decided_by, edge_ns, basis, source, critical_mm, [nets])] of a row's layout-bound nets, a bound's group first:
    one evidence line per governing edge, so a net is never shown under an edge that does not govern it."""
    g = {}
    for n in r.get("layout_bound") or []:
        e = r["net_edges"][n]
        key = (0 if e["decided_by"] == "BOUND" else 1, e["edge_ns"], e["basis"], e["source"])
        g.setdefault(key, []).append(n)
    out = []
    for (o, edge, basis, source), nets in sorted(g.items()):
        crit = min((r.get("critical_by_net") or {}).get(n, r.get("critical_mm")) for n in nets)
        out.append(("BOUND" if o == 0 else "MAKER", edge, basis, source, crit, sorted(nets)))
    return out


def write_schematic_verdict(res, out_dir=None, quiet=False, table_file=True):
    """Write the `edge_length` verdict (rule SI-001) and, beside it, the table as edge_length.table.json."""
    import verdict as _v
    result = schematic_result(res)
    c = res.get("counts") or {}
    ev = list(res["fails"])
    for r in res.get("rows") or []:
        if r["status"] in ("UNDECIDED", "PARTIAL"):
            why = _reason_summary(r)
            ev.append("UNDECIDED %s (%s, %d of %d net(s)): %s; ICs on them: %s" % (
                r["pattern"], r["class"], len(r.get("undecided") or r["nets"]), len(r["nets"]), why[:140],
                ", ".join("%s %s" % (" ".join(v.split()[:2]), "/".join(rs[:3])) for v, rs in list(r["drivers"].items())[:4]) or "none"))
    # the summaries before the per-row lines, so the evidence cap never cuts them
    bd = [(r["pattern"], n) for r in res.get("rows") or [] for n in r.get("bound_decides") or []]
    if bd:
        ev.append("BOUND_DECIDES %d layout-bound net(s) whose governing edge is a bound or a model: at least one driver "
                  "on each has no published minimum, whatever the other drivers' makers publish (ER-D13): %s%s" % (
                      len(bd), ", ".join(n for _p, n in bd[:12]), " ..." if len(bd) > 12 else ""))
    mh = [(r["pattern"], n) for r in res.get("rows") or [] for n in r.get("maker_holds") or []]
    if mh:
        ev.append("MAKER_HELD %d layout-bound net(s) on which every driver has a published minimum: %s%s" % (
            len(mh), ", ".join(n for _p, n in mh[:12]), " ..." if len(mh) > 12 else ""))
    al = [(n, r["pattern"], (r.get("length_limits") or {}).get(n)) for r in res.get("rows") or []
          for n, w in sorted((r.get("answered") or {}).items()) if w.startswith("declared in edge_allow")]
    if al:
        ev.append("ALLOWED %d net(s), pending the layout: answered at this phase by an edge_allow declaration whose basis "
                  "holds (CSI-D1), each held to the length it declares (CSI-D2) by the routed half, edge_length_routed, which "
                  "decides no rule yet: %s" % (
                      len(al), ", ".join("%s%s" % (n, " <= %.1f mm" % mm if mm is not None else "") for n, _p, mm in al[:16])))
    for r in res.get("rows") or []:
        for who, edge, basis, source, crit, nets in _layout_bound_groups(r):
            ev.append("LAYOUT_BOUND %s (%s, %.3f ns %s %s, critical %.1f mm, decided by %s): %s%s" % (
                r["pattern"], r["class"], float(edge), basis, source, crit,
                "a bound" if who == "BOUND" else "a published figure on every driver",
                ", ".join(nets[:8]), " ..." if len(nets) > 8 else ""))
    ms = (res.get("inputs") or {}).get("model_state") or {}
    if ms.get("absent"):
        ev.insert(len(res["fails"]), "MODELS_ABSENT %d of the %d makers' IBIS models this reading asks for are not in this "
                  "tree (they are withheld from the repository and pinned by %s): %d net(s) wait on one and read UNDECIDED, "
                  "naming it. Fetch them (%s) and re-take: %s" % (
                      ms["absent"], ms["asked"], ms.get("manifest"), c.get("undecided_model_absent_nets", 0),
                      ms.get("how_to_fetch"), ", ".join(ms.get("absent_files") or [])))
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
                          "corner-to-corner extent, the project file's class where the netlist says Default. Since 27 "
                          "September 2026 every edge is a record of tools/pcb_edge_rates.yaml (a configuration input, by "
                          "sha in inputs.edge_rates): a class entry's interface record, or per net the fastest of its "
                          "drivers' families (a maker's IBIS model read per pin, a published minimum, a model or a "
                          "bound), its far ends and one series resistor away; a net whose driver has no record is "
                          "UNDECIDED. The governing edge of a net is the fastest any driver on it can produce, so one "
                          "driver with no published minimum makes the net decided by a bound whatever the others "
                          "publish (ER-D13); a layout-bound net a bound decides is named under BOUND_DECIDES and holds "
                          "the reading INCONCLUSIVE. counts: decided = maker_edge + bound_edge; layout_bound = "
                          "maker_held + bound_decided. Since 28 September 2026 the makers' IBIS models are pinned by "
                          "v2/vendor/ibis-manifest.yaml (inputs.ibis_manifest) and are not in the repository: a pinned model "
                          "the checkout does not hold decides nothing, its nets read UNDECIDED naming it, and "
                          "inputs.model_state says which state the reading was taken in (ER-D17); undecided = "
                          "undecided_no_declaration + undecided_model_absent + undecided_other; a pin whose [Ramp] "
                          "cell the model's own V-t table contradicts takes the instantaneous bound (ER-D16). Since 29 September 2026 an "
                          "edge_allow declaration answers a net only with its basis held, a refused one FAILS the reading, "
                          "and the length it declares is handed to the layout (length_limits; CSI-D1, CSI-D2)"))


def print_table(res):
    c = res.get("counts") or {}
    i = res.get("inputs") or {}
    print("edge_length: SI-001 schematic table, board %s: k %s, slowest layer %s at %s ps/mm, extent %s mm; %d signal "
          "net(s), %d decided, %d undecided, %d declared slow or DC, %d contradicted; of the decided %d may be "
          "electrically long, %d answered in the netlist and %d layout-bound; of the decided, %d by a published figure "
          "on every driver and %d by a bound or model; of the layout-bound, %d by a published figure on every driver and "
          "%d by a bound (BOUND_DECIDES)"
          % (str(res.get("letter") or "?").upper(), i.get("critical_k"), i.get("slowest_layer"), i.get("t_pd_ps_per_mm"),
             i.get("extent_mm"), c.get("signal_nets", 0), c.get("decided_nets", 0), c.get("undecided_nets", 0),
             c.get("low_speed_nets", 0), c.get("contradicted_nets", 0), c.get("may_be_long_nets", 0),
             c.get("answered_nets", 0), c.get("layout_bound_nets", 0), c.get("maker_edge_nets", 0),
             c.get("bound_edge_nets", 0), c.get("maker_held_nets", 0), c.get("bound_decided_nets", 0)))
    ms = i.get("model_state") or {}
    print("  models: state %s, %d asked for, %d in this tree, %d absent (pinned by %s); undecided by reason: %d with no "
          "signal-class declaration, %d waiting only on a model that is not in this tree, %d other"
          % (ms.get("state"), ms.get("asked", 0), ms.get("present", 0), ms.get("absent", 0), ms.get("manifest"),
             c.get("undecided_no_declaration_nets", 0), c.get("undecided_model_absent_nets", 0),
             c.get("undecided_other_nets", 0)))
    for r in res.get("rows") or []:
        tail = ""
        if r.get("critical_mm") is not None:
            tail = ", %.3f ns %s, critical %.1f mm, %s" % (float(r["rise_ns"]), _basis_of(r), r["critical_mm"],
                                                        "%d answered, %d layout-bound%s" % (len(r.get("answered") or {}), len(r.get("layout_bound") or []),
                                                        ", %d decided by a bound" % len(r["bound_decides"]) if r.get("bound_decides") else "")
                                                        if r.get("may_be_long") else "never long here")
        if r.get("undecided") and r["status"] != "LOW_SPEED_OR_DC" and r["class"] != "UNKNOWN":
            tail += "; undecided %d: %s" % (len(r["undecided"]), _reason_summary(r)[:110])
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