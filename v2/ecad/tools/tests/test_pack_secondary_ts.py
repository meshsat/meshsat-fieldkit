#!/usr/bin/env python3
"""The second level's temperature input on board P (MESHSAT-1357, review stream BAT, 26 September 2026).

WHY IT EXISTS. The review of 26 September 2026 (v2/docs/reviews/2026-09-26-foundation-progress-review.md, section 2)
refused a design that held the BQ7720700's TS pin on a fixed 10 kohm to VSS, which disabled the second level's
over-temperature to meet a +71 C storage margin. Stream BAT restored it (an own 103AT-2 on a socket J_TS2 behind a
series resistor, with a shunt from TS to VSS that keeps an open lead or a cold cell from reading as under-temperature),
and the checker of that cycle found that nothing in the suite would notice a return to the fixed resistor: the suite
passed identically with main's generator swapped in. This file is the fixture it asked for
(v2/docs/review-packets/battery/SECONDARY-OT-DECISION.md holds the decision and its numbers).

THE PROPERTY, stated on connectivity and published numbers, never on a reference designator's history:
  1. U2 pin 12 (TS) reaches an OFF-BOARD thermistor socket, a connector whose other pin is on VSS, through ONE series
     resistor, and the net between them carries nothing else (the NTC is the cell's, not the board's);
  2. the resistors from TS straight to VSS (the shunt) cap the network: nominal at most CAP_OHM, and CAP_OHM with its
     tolerance and its drift down to -40 C at least MARGIN under the lowest under-temperature resistance the chip may
     apply, RUT_LOW_OHM, which is derived here from SLUSEG7D 6.5's 26.7 kohm and TUT_ACC's +-5 C (the chip's own UT
     accuracy; RUT_ACC is the EXTERNAL resistance accuracy the data sheet's footnote assumes, the first cycle's error);
  3. the network trips at the BQ7720700's 70 C within TRIP_BAND on the Semitec 103AT table (the series resistor puts
     back what the shunt takes away);
  4. no capacitor on TS (SLUSEG7D 7.3.3: CTS at most 200 pF; there is no place for one).
A fixed resistor alone, a bare socket with no cap, a cap above CAP_OHM, an on-board sensor, a capacitor on TS and a
series resistor that moves the trip all FAIL; the taken network PASSES.

HOW IT READS. A netlist through regen_compare.parse_net (balanced S-expression blocks); the generator through `ast`
(its literal r(), c(), part() and synth() calls). Nothing is grepped.

Run by tests/run.py; or by hand on any generator or netlist:
    python3 test_pack_secondary_ts.py <gen_sch_p.py | pcb-p-pack.net>     prints PASS or FAIL with the reasons
"""
import ast, math, os, re, sys

TESTS = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(TESTS)
sys.path.insert(0, TOOLS)
V2 = os.path.dirname(os.path.dirname(TOOLS))          # the v2/ directory
GEN = os.path.join(TOOLS, "gen_sch_p.py")
NET_COMMITTED = os.path.join(TOOLS, "..", "pcb-p-pack-p2", "out", "pcb-p-pack.net")
NET_PACKET = os.path.join(V2, "docs", "review-packets", "battery", "candidate", "pcb-p-pack.net")

# ---- published numbers (SLUSEG7D Rev. D 6.5 and section 4; Semitec 103AT-2, v2/vendor/battery/semitec-at-p12-13.pdf;
# ---- UNI-ROYAL 0603WAF +-1 %, +-100 ppm/C as read from JLC's API, drafts/box/jlc-queries-bat.json)
ROT_OHM = 2195.0          # NTC OT detection external resistance for 70 C, the BQ7720700's threshold
OT_C = 70.0
RUT_OHM = 26700.0         # the lowest NTC UT detection external resistance (the 0 C option)
UT_ACC_C = 5.0            # TUT_ACC, "UT Detection Accuracy (NTC)", read as the chip's alone (the conservative reading)
TOL, TCR, T_BOARD_MIN = 0.01, 100e-6, -40.0
T = [-50, -40, -30, -20, -10, 0, 10, 20, 25, 30, 40, 50, 60, 70, 80, 85, 90, 100, 110]
R_103AT = [x * 1000.0 for x in (329.5, 188.5, 111.3, 67.77, 42.47, 27.28, 17.96, 12.09, 10.00, 8.313, 5.827, 4.160,
                                3.020, 2.228, 1.668, 1.451, 1.266, 0.9731, 0.7576)]
# ---- the design's choices, judged against the numbers above
CAP_OHM = 18000.0         # the chosen shunt cap (nominal)
MARGIN = 0.10             # the cap with tolerance and drift stays at least this far under RUT_LOW_OHM
TRIP_BAND = 1.5           # C, the network's nominal trip against OT_C


def ntc(t):
    k = max(i for i in range(len(T) - 1) if T[i] <= t) if t < T[-1] else len(T) - 2
    x0, x1, x = 1 / (T[k] + 273.15), 1 / (T[k + 1] + 273.15), 1 / (t + 273.15)
    return math.exp(math.log(R_103AT[k]) + (math.log(R_103AT[k + 1]) - math.log(R_103AT[k])) * (x - x0) / (x1 - x0))


def temp_at(r_target, f, lo=-50.0, hi=110.0):
    for _ in range(80):
        mid = (lo + hi) / 2
        if f(mid) > r_target: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def _rut_low():
    """26.7 kohm moved by TUT_ACC's +5 C at the 103AT's own slope there: the lowest UT resistance the chip may apply."""
    t_ut = temp_at(RUT_OHM, ntc)
    beta = -(math.log(ntc(t_ut + 0.05)) - math.log(ntc(t_ut - 0.05))) / 0.1
    return RUT_OHM * math.exp(-UT_ACC_C * beta)


RUT_LOW_OHM = _rut_low()


def ohms(v):
    """'18k' 18000, '270R' 270, '2k2' 2200, '1M' 1e6, '100R 1% (...)' 100; None when it is not a resistance."""
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([RrkKM]?)(\d*)", v or "")
    if not m: return None
    mult = {"": 1.0, "R": 1.0, "r": 1.0, "k": 1e3, "K": 1e3, "M": 1e6}[m.group(2)]
    base = float(m.group(1)) * mult
    if m.group(3): base += float("0." + m.group(3)) * mult
    return base


def par(*rs):
    return 1.0 / sum(1.0 / r for r in rs)


# ---------------------------------------------------------------- readers: {ref: value}, {ref: {pin: net}}
def from_netlist(path):
    import regen_compare
    comps, nets = regen_compare.parse_net(open(path, encoding="utf-8", errors="replace").read())
    values = {ref: (c.get("value") or "") for ref, c in comps.items()}
    pins = {}
    for name, nodes in nets.items():
        for ref, pin, _pf, _pt in nodes:
            pins.setdefault(ref, {})[str(pin)] = name.lstrip("/")
    return values, pins


def from_generator(path):
    """The literal calls of a gen_sch generator: r(ref, value, a, b), c(ref, value, a, b), part(ref, lib, sym, value,
    fp, {pin: net}) and synth(ref, name, value, fp, {pin: net}). A call with a computed reference is not read."""
    tree = ast.parse(open(path, encoding="utf-8").read(), path)
    values, pins = {}, {}
    lit = lambda n: n.value if isinstance(n, ast.Constant) else None
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)): continue
        fn, a = node.func.id, node.args
        kw = {k.arg: k.value for k in node.keywords}
        if fn in ("r", "c") and len(a) >= 4 and all(isinstance(lit(x), str) for x in a[:4]):
            values[lit(a[0])] = lit(a[1]); pins[lit(a[0])] = {"1": lit(a[2]), "2": lit(a[3])}
        elif fn in ("part", "synth"):
            idx = 5 if fn == "part" else 4
            d = a[idx] if len(a) > idx else kw.get("nets")
            ref, val = (lit(a[0]) if a else None), (lit(a[3]) if fn == "part" and len(a) > 3 else lit(a[2]) if len(a) > 2 else None)
            if not isinstance(ref, str) or not isinstance(d, ast.Dict): continue
            mp = {}
            for k, v in zip(d.keys, d.values):
                if lit(k) is not None and isinstance(lit(v), str): mp[str(lit(k))] = lit(v)
            values[ref] = val or ""; pins[ref] = mp
    return values, pins


def read(path):
    return from_generator(path) if path.endswith(".py") else from_netlist(path)


# ---------------------------------------------------------------- the judgement
def judge(values, pins, gnd="GND", ic="U2", ts_pin="12"):
    """The failures of the property in this module's docstring, as sentences; an empty list is a PASS."""
    f = []
    if ic not in pins or ts_pin not in pins[ic]:
        return ["%s pin %s is not on this board, so the second level's TS input cannot be judged" % (ic, ts_pin)]
    ts = pins[ic][ts_pin]
    if ts == gnd: return ["%s pin %s (TS) is tied to %s: that reads as over-temperature" % (ic, ts_pin, gnd)]
    members = lambda net: [(ref, p) for ref, mp in pins.items() for p, n in mp.items() if n == net]
    on_ts = [(ref, p) for ref, p in members(ts) if not (ref == ic and p == ts_pin) and not ref.startswith("TP")]
    shunts, series = [], []
    for ref, p in on_ts:
        other = [n for q, n in pins[ref].items() if q != p]
        if ref.startswith("C"):
            f.append("%s is a capacitor on TS (SLUSEG7D 7.3.3: at most 200 pF, and this design has no place for one)" % ref)
        elif ref.startswith("R") and len(pins[ref]) == 2:
            (shunts if other == [gnd] else series).append((ref, other[0]))
        else:
            f.append("%s sits on TS and is neither the network's resistor nor a test point" % ref)
    sockets = []
    for ref, far in series:
        rest = [(r_, p) for r_, p in members(far) if r_ != ref]
        conn = [(r_, p) for r_, p in rest if r_.startswith("J")]
        if len(rest) == 1 and len(conn) == 1:
            j = conn[0][0]
            if sorted(set(pins[j].values())) == sorted({far, gnd}):
                sockets.append((ref, j)); continue
        f.append("%s leaves TS for %s, which is not a two-way socket to %s alone (%s): the second level's sensor must be "
                 "off the board, on the cell" % (ref, far, gnd, ", ".join("%s.%s" % x for x in rest) or "nothing"))
    if not sockets:
        f.append("TS does not reach an off-board thermistor socket through a series resistor: the second level has no "
                 "temperature sensor of its own (a fixed resistor to %s holds TS at one reading and disables its "
                 "over-temperature, the design the review of 26 September 2026 refused)" % gnd)
    elif len(sockets) > 1:
        f.append("TS reaches %d sockets (%s); the network is judged for one sensor" % (len(sockets), sockets))
    if not shunts:
        f.append("no resistor caps TS to %s: an open or unplugged NTC reads as an infinite resistance, above every "
                 "under-temperature resistance SLUSEG7D 6.5 lists, and the data sheet does not say whether the "
                 "BQ7720700 carries UT (question Q-TI-1)" % gnd)
        return f
    rv = [ohms(values.get(r_)) for r_, _ in shunts]
    if None in rv: return f + ["shunt value(s) %s cannot be read as resistances" % [values.get(r_) for r_, _ in shunts]]
    rp = par(*rv)
    if rp > CAP_OHM + 1e-6:
        f.append("the shunt from TS to %s is %.0f ohm, above the %.0f ohm cap: with the NTC open it reads %.0f ohm at +1 "
                 "percent and %.0f C, and the chip may apply its lowest UT threshold at %.0f ohm (26.7 kohm moved by TUT_ACC's "
                 "+5 C), so an unplugged lead or a cold cell could read as under-temperature and open the fuse"
                 % (gnd, rp, CAP_OHM, rp * (1 + TOL) * (1 + (25 - T_BOARD_MIN) * TCR), T_BOARD_MIN, RUT_LOW_OHM))
    if sockets:
        rs = ohms(values.get(sockets[0][0]))
        if rs is None:
            f.append("series resistor %s's value %r cannot be read" % (sockets[0][0], values.get(sockets[0][0])))
        else:
            trip = temp_at(ROT_OHM, lambda t: par(rp, rs + ntc(t)))
            if abs(trip - OT_C) > TRIP_BAND:
                f.append("the network (%s %.0f ohm in series, %.0f ohm shunt) trips at %.1f C on the 103AT table, more than "
                         "%.1f C from the BQ7720700's %.0f C" % (sockets[0][0], rs, rp, trip, TRIP_BAND, OT_C))
    return f


# ---------------------------------------------------------------- fixtures
def _board(extra=()):
    """A second level on its own: U2 with TS on TS_SEC and its supply pins; `extra` adds (ref, value, {pin: net})."""
    values = {"U2": "BQ7720700DSSR", "TP15": "TS_SEC"}
    pins = {"U2": {"9": "GND", "12": "TS_SEC", "13": "GND"}, "TP15": {"1": "TS_SEC"}}
    for ref, v, mp in extra:
        values[ref] = v; pins[ref] = dict(mp)
    return values, pins


R33 = lambda v: ("R33", v, {"1": "TS_SEC", "2": "GND"})
R34 = lambda v: ("R34", v, {"1": "TS_SEC", "2": "TS_SEC_J"})
J_TS2 = ("J_TS2", "PH 1x2", {"1": "TS_SEC_J", "2": "GND"})


def t_the_taken_network_passes():
    """THE ACCEPTABLE FIXTURE: 270 ohm in series to an off-board 103AT-2 on J_TS2, 18 kohm from TS to VSS."""
    r = judge(*_board([R33("18k"), R34("270R"), J_TS2]))
    assert r == [], r


def t_a_fixed_resistor_alone_on_ts_fails():
    """Main 1f614233's arrangement: TS held on a fixed 10 kohm, no sensor. The regression the review objected to."""
    r = judge(*_board([R33("10k")]))
    assert any("no temperature sensor of its own" in x for x in r), r


def t_the_first_cycles_22k_shunt_fails_the_cap():
    """200 ohm / 22 kohm: its open-NTC ceiling (about 22.4 kohm at +1 percent and -40 C) is above the lowest UT
    resistance at TUT_ACC (about 21.5 kohm), so it is not indifferent to an unstated UT."""
    r = judge(*_board([R33("22k"), R34("200R"), J_TS2]))
    assert any("above the 18000 ohm cap" in x for x in r), r


def t_a_bare_socket_with_no_cap_fails():
    """TI's Figure 8-1 as drawn: acceptable only once TI states UT is off (Q-TI-1), so this design refuses it."""
    values, pins = _board([("J_TS2", "PH 1x2", {"1": "TS_SEC", "2": "GND"})])
    r = judge(values, pins)
    assert any("does not reach an off-board thermistor socket" in x for x in r), r
    assert any("no resistor caps TS" in x for x in r), r


def t_an_on_board_sensor_fails():
    """A thermistor on the board measures the board, not the hottest cell (Samsung's 2016 note)."""
    r = judge(*_board([R33("18k"), R34("270R"), ("RT9", "103AT", {"1": "TS_SEC_J", "2": "GND"})]))
    assert any("not a two-way socket" in x for x in r), r


def t_a_capacitor_on_ts_fails():
    r = judge(*_board([R33("18k"), R34("270R"), J_TS2, ("C99", "100n", {"1": "TS_SEC", "2": "GND"})]))
    assert any("capacitor on TS" in x for x in r), r


def t_a_series_resistor_that_moves_the_trip_fails():
    """1 kohm in series moves the network's trip well below 70 C (about 62 C nominal)."""
    r = judge(*_board([R33("18k"), R34("1k"), J_TS2]))
    assert any("more than 1.5 C" in x for x in r), r


def t_the_cap_itself_clears_the_chips_lowest_ut_resistance():
    """The constant is a derivation, not a number typed in: 26.7 kohm at the 103AT's 0.5 C moved by TUT_ACC's +5 C is
    about 21.5 kohm, and 18 kohm at +1 percent with 100 ppm/C down to -40 C is about 18.3 kohm, 15 percent under it."""
    assert 21000 < RUT_LOW_OHM < 22000, RUT_LOW_OHM
    ceiling = CAP_OHM * (1 + TOL) * (1 + (25 - T_BOARD_MIN) * TCR)
    assert ceiling <= RUT_LOW_OHM * (1 - MARGIN), (ceiling, RUT_LOW_OHM)
    assert 22000 * (1 + TOL) * (1 + (25 - T_BOARD_MIN) * TCR) > RUT_LOW_OHM   # the first cycle's shunt does not


def t_the_generator_in_this_tree_holds_the_property():
    """Read by ast from gen_sch_p.py: main 1f614233's generator fails this (fixed 10 kohm), the candidate passes."""
    values, pins = from_generator(GEN)
    assert "U2" in pins and len(pins) > 40, "the ast reader found %d parts in %s" % (len(pins), GEN)
    r = judge(values, pins)
    assert r == [], r


def t_the_current_netlist_holds_the_property():
    """The netlist written by THIS tree's generator (sch_prov), whichever copy that is: the committed board P netlist
    once integrated, or the review packet's regenerated candidate before. A netlist of another generator is not judged."""
    from harness import Skip
    import sch_prov
    why = []
    for p in (NET_COMMITTED, NET_PACKET):
        if not os.path.exists(p): why.append("%s absent" % os.path.relpath(p, V2)); continue
        ok, w = sch_prov.current(p, "p")
        if ok:
            r = judge(*from_netlist(p))
            assert r == [], "%s: %s" % (os.path.relpath(p, V2), r)
            return
        why.append(w[:160])
    raise Skip("no board P netlist on this host was written by this tree's generator: " + " | ".join(why))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.split("Run by")[1]); sys.exit(2)
    v, p = read(sys.argv[1])
    res = judge(v, p)
    ts = (p.get("U2") or {}).get("12")
    print("%s: %d parts read; U2 pin 12 on %s; shunt cap %.0f ohm; lowest UT resistance at TUT_ACC %.0f ohm"
          % (sys.argv[1], len(p), ts, CAP_OHM, RUT_LOW_OHM))
    print("PASS" if not res else "FAIL\n  - " + "\n  - ".join(res))
    sys.exit(0 if not res else 1)
