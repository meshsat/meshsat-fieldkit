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

Usage: edge_length.py <board.kicad_pcb> [--json]
"""
import os, sys, json, math

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


def main(a):
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
        return _v.write("edge_length", _v.INCONCLUSIVE, denominator=0, inputs={"board": path},
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
    return _v.write("edge_length", _v.FAIL if over else (_v.INCONCLUSIVE if (not rows or undeclared) else _v.PASS),
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


if __name__ == "__main__":
    # EVERY GATE LEAVES A READING WHEN IT RAISES (18 September 2026). The thirteen one-line entries of this
    # morning were the gates a crash had already cost a verdict; these are the rest of the deciding gates in
    # the coverage map, guarded the same way, so a rule whose tool raised reads INCONCLUSIVE naming the
    # exception rather than 'no verdict', which the registry reads as nobody having looked.
    sys.exit(_v.guard("edge_length", main, sys.argv[1:]))