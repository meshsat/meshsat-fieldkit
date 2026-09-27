#!/usr/bin/env python3
"""Stream d4emcon (MESHSAT-1357): the level at every EMCON control node of the kit, in each fault state, from the
divider the committed netlists draw and the makers' stated pin currents.

This is an arithmetic of its own, not the RF-002 instrument's solver: it builds each node's resistive network from the
netlist (every two-pin resistor on the node, read through to the nets behind it), puts each pin's stated current into it
in the adverse direction, and solves it. Where it agrees with tools/tx_inhibit.py the two were derived apart; where it
does not, the record says which and why. It judges nothing that is not a number: a pin whose current no held sheet
bounds is listed under `unbounded`, and the state then reads UNDECIDED whatever the known currents give.

CONVENTIONS (the instrument's, R4T-D28 and R4T-D36, so the two can be compared): a resistor at the adverse end of the
tolerance its value states (5 percent where it states none); a rail at its name's voltage plus 5 percent against a node
that must stay low, minus 5 percent under one that must stay high; a rail that is down is an open circuit (nothing says
what its loads hold it at); pin currents from the -40 to +85 C column, or the wider one where the sheet has no such
column; a part that may be powered or not while another part reads the node passes the larger of II and Ioff.
BOTH POLARITIES: `v_adverse` has every pin current in the direction that hurts, `v_other` the opposite one.

It reads the netlists through tx_inhibit.parse_netlist and takes the logic and switch families' pin maps and stated
currents from the instrument's LOGIC and SWITCHES tables (each row cites its sheet); the module pins are in PINS below.
It writes only the files named by --out (never under v2/ecad).

usage: fault_levels.py --tools <v2/ecad/tools> --ecad <v2/ecad> --out <dir>"""
import hashlib, json, os, re, sys

NETLISTS = {"A": "pcb-a-power-a23/out/pcb-a-power.net", "B": "pcb-b-compute-b19/out/pcb-b-compute.net",
            "C": "pcb-c-display-c8/out/pcb-c-display.net", "D": "pcb-d-aprs-d9/out/pcb-d-aprs.net"}
RAIL_TOL, TOL_DEFAULT = 0.05, 0.05

# Pins the families' tables do not hold: what the part's maker states at the pin. kind "leak": a current bound in amps;
# "pull": (volts, ohms) inside the part; "none": the maker states nothing, so the pin is unbounded.
PINS = {
    ("D", "U2", "5"): dict(kind="none", cite="NiceRF SA868 datasheet Rev 1.3 (2022-8), section 8 Pin definition (page 9): pin 5 "
                           "PTT 'Module Input, Transmitting/receiving control, \"0\" force the module to enter TX state; and "
                           "\"1\" to Rx state'; no level, input current or internal pull is stated"),
    ("B", "J_RB9704", "3"): dict(kind="pull_net", r_series=10e3, r_up=270e3, r_dn=430e3, v_up=5.3,
                                 cite="Ground Control, RockBLOCK 9704 hardware page (fetched 27 September 2026), pin 3 I_EN: 'a "
                                 "weak voltage-divider (270KOhm/430KOhm) pull-up to the input voltage' and 'a series 10KOhm "
                                 "resistor to the input of the buffer'; Signal Thresholds: Logic In LOW 0.4 V maximum, Logic In "
                                 "HIGH 2.0 V minimum; DC Power 5.3 V maximum"),
    ("B", "J_M2C2", "6"): dict(kind="pull", pull=(0.0, 100e3),
                               cite="Quectel RM520N series Hardware Design v1.1, 3.5 (FULL_CARD_POWER_OFF#): 'it has internally "
                               "pulled down with a 100 kOhm resistor'; pin table: VIHmin 1.19 V, VIHmax 4.4 V"),
    ("B", "J_M2C2", "8"): dict(kind="pull", pull=(1.8, 100e3),
                               cite="Quectel RM520N series Hardware Design v1.1, pin table: pin 8 W_DISABLE1# DI, 'Internally "
                               "pulled up to 1.8 V with a 100 kOhm resistor'"),
}
PINS[("B", "U221", "1")] = dict(kind="leak", amps=300e-9,
                                cite="TI TPS3808, SBVS050N 6.5 (page 6): IOH 'RESET leakage current' 300 nA maximum at VRESET "
                                "6.5 V, RESET not asserted; with its VDD down the pin is rated to 7 V (6.1) and no current is stated")
for _s, _u in ((1, 30), (2, 31), (3, 32)):
    for _p in ("89", "91"):
        PINS[("B", "U%dA" % _u, _p)] = dict(kind="pull", pull=(3.3, 1.8e3),
                                            cite="Raspberry Pi Compute Module 5 datasheet, release 3, pin table (page 20): pins 89 "
                                            "and 91 'Internally pulled up through 1.8 kOhm to CM5_3.3V'; no input-low level is "
                                            "stated for either pin")
IGSS = [(r"2N7002", 80e-9, "JSCJ 2N7002 (LCSC C8545), sheet J,Sep,2016, page 2: IGSS +-80 nA at Ta 25 C only, so it bounds "
         "nothing over the envelope; taken here as a 25 C figure and the state marked"),
        (r"Si2300DS", 100e-9, "Vishay Si2300DS, document 65701 (S10-0111-Rev. A, 18-Jan-10), page 2: IGSS +-100 nA at VGS +-12 V, "
         "under 'TJ = 25 C, unless otherwise noted', so a 25 C figure; VGS(th) 0.6 V to 1.5 V"),
        (r"AO3400", 100e-9, "AOS AO3400A: IGSS +-100 nA at VGS +-12 V, a 25 C figure (v2/vendor/power/aos-ao3400a-n-mosfet.pdf)")]
# A powered gate driving LOW: its maker's VOL rows at the supply the gate runs from, smallest load first, as (IOL amps, VOL
# volts). The row used is the first whose IOL covers what the node asks the gate to sink; no row is interpolated.
VOL = {
    "74LVC1G08 AND": dict(rows=[(100e-6, 0.1), (16e-3, 0.4), (24e-3, 0.55)],
                          cite="TI SN74LVC1G08, SCES217AA 5.5: VOL 0.1 V at IOL 100 uA (VCC 1.65 V to 5.5 V), 0.4 V at 16 mA "
                               "and 0.55 V at 24 mA (VCC 3 V)"),
    "74LVC1G08 AND, TECH PUBLIC": dict(rows=[(100e-6, 0.1), (16e-3, 0.6), (24e-3, 0.8)],
                                       cite="TECH PUBLIC 74LVC1G08 (LCSC C19829591), page 3, -40 to +125 C: VOL 0.1 V at IOL "
                                            "100 uA (VCC 1.65 V to 5.5 V), 0.6 V at 16 mA and 0.8 V at 24 mA (VCC 3.0 V)"),
    "74AUP1G08 AND": dict(rows=[(20e-6, 0.1), (2.7e-3, 0.33), (4e-3, 0.45)],
                          cite="TI SN74AUP1G08, SCES502Q 5.5 (page 7), -40 to +85 C: VOL 0.1 V at IOL 20 uA (VCC 0.8 V to "
                               "3.6 V), 0.33 V at 2.7 mA and 0.45 V at 4 mA (VCC 3 V)"),
    "74LV1T08 AND": dict(rows=[(20e-6, 0.1), (4e-3, 0.2), (8e-3, 0.35)],
                         cite="TI SN74LV1T08, SCLS739F 6.5, -40 to +125 C: VOL 0.1 V at IOL 20 uA (VCC 1.65 V to 5.5 V), 0.2 V "
                              "at 4 mA and 0.35 V at 8 mA (VCC 4.5 V; the 8 mA row as stream w4b read it)"),
    "74LVC2G06 dual open-drain inverter": dict(rows=[(100e-6, 0.1), (16e-3, 0.4), (24e-3, 0.55)],
                                               cite="TI SN74LVC2G06, SCES307J 6.5 (page 6): VOL 0.1 V at IOL 100 uA (VCC 1.65 V "
                                                    "to 5.5 V), 0.4 V at 16 mA and 0.55 V at 24 mA (VCC 3 V)"),
}
TECHPUBLIC = {("D", r) for r in ("U9", "U10", "U12", "U14")}      # board D's 74LVC1G08 are TECH PUBLIC's (LCSC C19829591)


def ohms_tol(tx, v):
    return tx._ohms(v), tx._tol(v)


class Boards:
    def __init__(self, tx, ecad):
        self.tx = tx
        self.nl = {k: tx.parse_netlist(os.path.join(ecad, p)) for k, p in NETLISTS.items()}
        self.sha = {k: hashlib.sha256(open(os.path.join(ecad, p), "rb").read()).hexdigest()[:16] for k, p in NETLISTS.items()}
        self.mates = {}
        for m in tx.MATES:
            self.mates[m["a"]] = m["b"]; self.mates[m["b"]] = m["a"]


def solve(nodes, fixed, res, inj):
    """Node voltages: nodes a list of ids, fixed {id: volts}, res [(a, b, ohms)], inj {id: amps into it}."""
    unk = [n for n in nodes if n not in fixed]
    ix = {n: i for i, n in enumerate(unk)}
    n = len(unk)
    A = [[0.0] * (n + 1) for _ in range(n)]
    for x, i in ix.items(): A[i][n] += inj.get(x, 0.0)
    for a, b, r in res:
        g = 1.0 / max(r, 1e-3)
        for p, q in ((a, b), (b, a)):
            if p in ix:
                A[ix[p]][ix[p]] += g
                if q in ix: A[ix[p]][ix[q]] -= g
                elif q in fixed: A[ix[p]][n] += g * fixed[q]
    for i in range(n):
        piv = max(range(i, n), key=lambda r_: abs(A[r_][i]))
        if abs(A[piv][i]) < 1e-18: return None                      # a floating node
        A[i], A[piv] = A[piv], A[i]
        for r_ in range(n):
            if r_ != i and A[r_][i]:
                f = A[r_][i] / A[i][i]
                A[r_] = [x - f * y for x, y in zip(A[r_], A[i])]
    out = dict(fixed)
    for x, i in ix.items(): out[x] = A[i][n] / A[i][i]
    return out


def network(B, k0, n0, want, down=(), cut=(), drive=None, absent=(), reader=None):
    """The network seen from (board k0, net n0). want "LOW" or "HIGH"; down: (board, rail) pairs at 0 V, whose parts are
    unpowered; cut: connector (board, ref) pairs unplugged; drive {(board, ref, pin): volts}: outputs held at a level;
    absent: (board, ref) parts taken out (the open toggle); reader (board, ref): the part that reads the node, taken
    powered. Returns dict(v_adverse, v_other, legs, leaks, unbounded, floating)."""
    tx = B.tx
    low = want == "LOW"
    down, cut, absent, drive = set(down), set(cut), set(absent), dict(drive or {})
    nodes, fixed, res = [], {"GND": 0.0}, []
    leaks, unbounded, legs = [], [], []
    inj_mag = {}
    seen, todo, done = set(), [(k0, n0)], set()

    def powered(k, ref):
        rails = tx._supply_nets(B.nl[k], ref)
        if not rails: return None
        return any((k, r) not in down for r in rails)

    def leak(k, n, amps, label, cite):
        inj_mag[(k, n)] = inj_mag.get((k, n), 0.0) + amps
        leaks.append(dict(node="%s %s" % (k, n), pin=label, uA=round(amps * 1e6, 4), cite=cite))

    while todo:
        k, n = todo.pop(0)
        if (k, n) in seen: continue
        seen.add((k, n)); nodes.append((k, n))
        nl = B.nl.get(k)
        if nl is None: continue
        for ref, pin, fn in nl["nets"].get(n, []):
            v = tx.value(nl, ref)
            if (k, ref) in absent or re.match(r"^(#|TP|C\d)", ref): continue
            if (k, ref, pin) in drive:
                key = "DRV %s %s.%s" % (k, ref, pin); fixed[key] = drive[(k, ref, pin)]
                res.append(((k, n), key, 1e-3)); legs.append("%s %s pin %s drives the node at %.3f V" % (k, ref, pin, drive[(k, ref, pin)]))
                continue
            ps = tx.pins_of(nl, ref)
            if re.match(r"^R\d", ref) and len(ps) == 2:
                if (k, ref) in done: continue
                done.add((k, ref))
                far = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
                r, tol = ohms_tol(tx, v)
                if tx._dead(far) or r is None: continue
                if tx.is_ground(far):
                    rr = r * (1 + tol) if low else r * (1 - tol)
                    res.append(((k, n), "GND", rr)); legs.append("%s %s %s (%s, taken %.4g) to GND" % (k, ref, v[:12], n, rr))
                elif tx.is_rail(far):
                    if (k, far) in down:
                        legs.append("%s %s %s to %s, which is down: taken absent" % (k, ref, v[:12], far)); continue
                    vr = tx.rail_volts(far)
                    vv = vr * (1 + RAIL_TOL) if low else vr * (1 - RAIL_TOL)
                    rr = r * (1 - tol) if low else r * (1 + tol)
                    key = "RAIL %s %s" % (k, far); fixed[key] = vv
                    res.append(((k, n), key, rr)); legs.append("%s %s %s (taken %.4g) to %s at %.3f V" % (k, ref, v[:12], rr, far, vv))
                else:
                    res.append(((k, n), (k, far), r)); legs.append("%s %s %s (nominal) from %s to %s" % (k, ref, v[:12], n, far))
                    todo.append((k, far))
                continue
            if re.match(r"^(J|P)\w*", ref):
                mate = B.mates.get((k, ref))
                if mate and (k, ref) not in cut and mate not in cut and (k, ref, pin) not in PINS:
                    k2, r2 = mate
                    if k2 in B.nl:
                        n2 = B.nl[k2]["pin"].get((r2, pin), "")
                        if not tx._dead(n2) and (k2, n2) not in seen:
                            res.append(((k, n), (k2, n2), 1e-3)); todo.append((k2, n2))
                    continue
                if mate: continue
            pm = PINS.get((k, ref, pin))
            if pm is not None:
                if pm["kind"] == "none":
                    unbounded.append("%s %s pin %s: %s" % (k, ref, pin, pm["cite"]))
                elif pm["kind"] == "leak":
                    leak(k, n, pm["amps"], "%s pin %s" % (ref, pin), pm["cite"])
                elif pm["kind"] == "pull":
                    pv, po = pm["pull"]
                    up = tx._anchor_rails(nl, dict(ref=ref)) if False else None
                    key = "PIN %s %s.%s" % (k, ref, pin); fixed[key] = pv * ((1 + RAIL_TOL) if low else (1 - RAIL_TOL)) if pv else 0.0
                    res.append(((k, n), key, po)); legs.append("%s %s pin %s: the module's own pull, %g V through %g Ohm (%s)" % (
                        k, ref, pin, pv, po, pm["cite"][:60]))
                elif pm["kind"] == "pull_net":
                    mid = (k, "#inside %s.%s" % (ref, pin)); nodes.append(mid)
                    res.append(((k, n), mid, pm["r_series"])); res.append((mid, "GND", pm["r_dn"]))
                    if (k, "#module_input") not in down:
                        key = "PIN %s %s.%s" % (k, ref, pin); fixed[key] = pm["v_up"]
                        res.append((mid, key, pm["r_up"]))
                    legs.append("%s %s pin %s: the module's divider %g k / %g k behind %g k (%s)" % (
                        k, ref, pin, pm["r_up"] / 1e3, pm["r_dn"] / 1e3, pm["r_series"] / 1e3, pm["cite"][:50]))
                continue
            fam = tx.logic_of(nl, ref)
            if fam is not None and not tx._unmapped(fam):
                is_in = any(pin in ins for ins, _o, _k in fam["gates"])
                is_out = any(pin == o for _i, o, _k in fam["gates"])
                if not (is_in or is_out): continue
                p_on = powered(k, ref)
                if (k, ref) == reader: p_on = True
                if p_on is False or (is_out and p_on is not True):
                    if fam.get("ioff") is None:
                        unbounded.append("%s %s pin %s: an unpowered %s, whose sheet states no Ioff (%s)" % (k, ref, pin, fam["name"], fam["leak_cite"][:80]))
                    else:
                        leak(k, n, fam["ioff"], "%s pin %s, unpowered (Ioff)" % (ref, pin), fam["leak_cite"])
                elif is_in:
                    amps = fam["ii"] if (k, ref) == reader else max(fam["ii"], fam.get("ioff") or 0.0)
                    leak(k, n, amps, "%s pin %s, an input (%s)" % (ref, pin, "II, the reader, powered" if (k, ref) == reader
                                                                   else "the larger of II and Ioff, powered or not"), fam["leak_cite"])
                else:
                    kind = [kd for _i, o, kd in fam["gates"] if o == pin][0]
                    if kind in tx.OPEN_DRAIN:
                        unbounded.append("%s %s pin %s: a powered open-drain output that is released, whose off-state current its "
                                         "sheet states only for VCC 0 V (Ioff %.0f uA, %s)" % (k, ref, pin, (fam.get("ioff") or 0) * 1e6,
                                                                                            fam["leak_cite"][:60]))
                        leak(k, n, fam.get("ioff") or 0.0, "%s pin %s, a released open drain (its Ioff row as a stand-in, not a "
                             "bound)" % (ref, pin), fam["leak_cite"])
                    else:
                        raise SystemExit("%s %s pin %s is a push-pull output on %s and the state does not say what it drives" % (k, ref, pin, n))
                continue
            sw = tx.switch_of(nl, ref)
            if sw and pin == sw["en"]:
                if sw.get("en_leak") is None:
                    unbounded.append("%s %s enable: %s" % (k, ref, sw["off_cite"][:150]))
                else:
                    leak(k, n, sw["en_leak"], "%s enable (%s)" % (ref, sw["name"]), sw["off_cite"])
                continue
            fq = tx.fet_of(nl, ref)
            if fq is not None:
                if pin == fq[1]["G"]:
                    g = next(((a, c) for rx, a, c in IGSS if re.search(rx, v, re.I)), (100e-9, "no held sheet's row is read "
                             "here for this FET's gate current; 100 nA is a stand-in"))
                    leak(k, n, g[0], "%s gate (a 25 C figure)" % ref, g[1])
                    unbounded.append("%s %s gate (%s): %s" % (k, ref, v[:24], g[1]))
                else:
                    other = fq[1]["D"] if pin == fq[1]["S"] else fq[1]["S"]
                    if tx.is_ground(nl["pin"].get((ref, other), "")):
                        unbounded.append("%s %s drain (%s), a switch to ground held off: its off-state current is stated at 25 C "
                                         "only, and it flows out of the node" % (k, ref, v[:24]))
                    else:
                        unbounded.append("%s %s pin %s (%s): a FET channel this arithmetic does not read" % (k, ref, pin, v[:24]))
                continue
            if re.match(r"^(D|LED)\w*", ref) and len(ps) == 2:
                far = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
                if fn == "A" and tx.is_ground(far): continue              # an anode here, its cathode on ground: it only drains
                unbounded.append("%s %s (%s) pin %s, a diode to %s" % (k, ref, v[:20], pin, far)); continue
            if re.match(r"^SW\w*", ref): continue
            unbounded.append("%s %s pin %s (%s, %r): no held sheet states its current" % (k, ref, pin, v[:30], fn))
    out = {}
    for name, sgn in (("v_adverse", 1.0 if low else -1.0), ("v_other", -1.0 if low else 1.0)):
        got = solve(nodes, fixed, res, {x: sgn * a for x, a in inj_mag.items()})
        out[name] = None if got is None else got.get((k0, n0))
        out[name + "_nodes"] = None if got is None else {("%s %s" % x if isinstance(x, tuple) else x): round(vv, 4)
                                                        for x, vv in got.items() if isinstance(x, tuple)}
    out.update(legs=legs, leaks=leaks, unbounded=unbounded, floating=out["v_adverse"] is None,
               sum_uA=round(sum(inj_mag.values()) * 1e6, 4))
    # what a driver on the node is asked to sink (adverse polarity): every other element's current into the node
    got = solve(nodes, fixed, res, {x: (1.0 if low else -1.0) * a for x, a in inj_mag.items()})
    sink = None
    at = {a_ for a_, b_, _r in res if str(b_).startswith("DRV ")}          # the nets a driver sits on
    if got is not None and at:
        sink = 0.0
        for nd in at:
            sink += inj_mag.get(nd, 0.0) if low else -inj_mag.get(nd, 0.0)
            for a_, b_, r_ in res:
                if str(a_).startswith("DRV ") or str(b_).startswith("DRV "): continue
                if a_ == nd: sink += (got[b_] - got[a_]) / max(r_, 1e-3)
                elif b_ == nd: sink += (got[a_] - got[b_]) / max(r_, 1e-3)
    out["sink_A"] = sink
    return out


def main(argv):
    tools = ecad = outd = None
    while argv:
        if argv[0] == "--tools": tools = argv[1]
        elif argv[0] == "--ecad": ecad = argv[1]
        elif argv[0] == "--out": outd = argv[1]
        else: print(__doc__); return 2
        argv = argv[2:]
    if not (tools and ecad and outd): print(__doc__); return 2
    if "/v2/ecad/" in os.path.abspath(outd) + "/": print("refused: --out lies under v2/ecad"); return 2
    sys.path.insert(0, os.path.abspath(tools)); sys.dont_write_bytecode = True
    import tx_inhibit as tx
    B = Boards(tx, ecad)
    PAN, AB, MEZ = ("B", "J_PANEL"), ("A", "J_AB1"), ("A", "J_MEZZ1")
    C_DOWN = [("C", "+3V3"), ("C", "+5V")]
    TOG = [("C", "SW_EMCON")]
    rows = []

    def row(rid, what, k, n, want, limit, limit_cite, **st):
        r = network(B, k, n, want, **st)
        va = r["v_adverse"]
        if r["floating"]: verdict = "FAIL (floating)"
        elif limit is None: verdict = "UNDECIDED (no stated threshold)"
        else:
            ok = (va < limit) if want == "LOW" else (va >= limit)
            verdict = ("UNDECIDED (a pin current is unbounded)" if r["unbounded"] else "PASS") if ok else "FAIL"
        rows.append(dict(id=rid, what=what, node="%s %s" % (k, n), want=want, limit=limit, limit_cite=limit_cite,
                         verdict=verdict, **r))

    LVC = "VIL 0.8 V at VCC 3 V to 3.6 V (TI SCES217AA 5.3; TECH PUBLIC 74LVC1G08 page 3 for board D)"
    AUP = "VIL 0.9 V at VCC 3 V to 3.6 V (TI SCES502Q 5.3)"
    SCH = "VT- 0.80 V minimum at VCC 3 V (Diodes DS35124 Rev. 8-2) and 0.84 V (TI SCES414P 6.5): read at 0.8 V"
    # ------------------------------------------------------------ the two lines, the source gone
    for rid, what, k, n, lim, cite, st in (
        ("L-TXI-1", "TX_INHIBIT_n at board D's U12, board C unpowered, every ribbon in", "D", "TX_INHIBIT_n", 0.8, LVC,
         dict(down=C_DOWN, absent=TOG, reader=("D", "U12"))),
        ("L-TXI-2", "TX_INHIBIT_n at board A's U35 and U37, board C unpowered, every ribbon in", "A", "TX_INHIBIT_n", 0.9, AUP,
         dict(down=C_DOWN, absent=TOG, reader=("A", "U35"))),
        ("L-TXI-3", "TX_INHIBIT_n at board D's U12, the panel ribbon unplugged", "D", "TX_INHIBIT_n", 0.8, LVC,
         dict(cut=[PAN], reader=("D", "U12"))),
        ("L-TXI-4", "TX_INHIBIT_n at board A's U35 and U37, the panel ribbon unplugged", "A", "TX_INHIBIT_n", 0.9, AUP,
         dict(cut=[PAN], reader=("A", "U35"))),
        ("L-TXI-5", "TX_INHIBIT_n at board D's U12, the A-B ribbon unplugged", "D", "TX_INHIBIT_n", 0.8, LVC,
         dict(cut=[AB], reader=("D", "U12"))),
        ("L-TXI-6", "TX_INHIBIT_n at board A's U35 and U37, the A-B ribbon unplugged", "A", "TX_INHIBIT_n", 0.9, AUP,
         dict(cut=[AB], reader=("A", "U35"))),
        ("L-TXI-7", "TX_INHIBIT_n at board A's U35 and U37, the mezzanine harness unplugged as well as the A-B ribbon", "A",
         "TX_INHIBIT_n", 0.9, AUP, dict(cut=[AB, MEZ], reader=("A", "U35"))),
        ("L-TXI-8", "TX_INHIBIT_n at board C's U9 and U14 (the lamp), board C powered, the panel ribbon unplugged and the "
         "toggle released: the released level", "C", "TX_INHIBIT_n", 2.0, "VT+ 2.00 V maximum at VCC 3 V (Diodes DS35124 Rev. "
         "8-2; no row between 3 V and 4.5 V): the released level must be above it for the line to RELEASE, which is the "
         "function and not the inhibit", dict(cut=[PAN], absent=TOG, reader=("C", "U9"))),
        ("L-EH-1", "EMCON_HW at board B's gates, board C unpowered, every ribbon in", "B", "EMCON_HW", 0.8, LVC,
         dict(down=C_DOWN, reader=("B", "U503"))),
        ("L-EH-2", "EMCON_HW at board B's gates, board C unpowered and the A-B ribbon unplugged", "B", "EMCON_HW", 0.8, LVC,
         dict(down=C_DOWN, cut=[AB], reader=("B", "U503"))),
        ("L-EH-3", "EMCON_HW at board B's gates, the panel ribbon unplugged and the A-B ribbon unplugged", "B", "EMCON_HW", 0.8,
         LVC, dict(cut=[PAN, AB], reader=("B", "U503"))),
        ("L-EH-4", "EMCON_HW at board A's U35 and U37, the A-B ribbon unplugged", "A", "EMCON_HW", 0.9, AUP,
         dict(cut=[AB], reader=("A", "U35"))),
        ("L-EH-5", "EMCON_HW at board B's U116, U216, U316 (SN74LV1T08 on the slot's 5 V), board C unpowered and the A-B ribbon "
         "unplugged", "B", "EMCON_HW", 0.8, "VIL 0.8 V at VCC 4.5 V to 5.5 V (TI SCLS739F 6.5); 0.65 V at VCC 3 V to 3.6 V",
         dict(down=C_DOWN, cut=[AB], reader=("B", "U216"))),
    ):
        want = "HIGH" if rid == "L-TXI-8" else "LOW"
        row(rid, what, k, n, want, lim, cite, **st)
    # board C's line with the toggle released and board C powered has U9 driving EMCON_HW; with board C unpowered U9's
    # output passes its Ioff, which network() takes because C's +3V3 is down.
    # ------------------------------------------------------------ the enables, their gate driving LOW (EMCON asserted)
    def vol_rows(k, ref):
        fam = tx.logic_of(B.nl[k], ref)
        return VOL[fam["name"] + (", TECH PUBLIC" if (k, ref) in TECHPUBLIC else "")]

    def driven(rid, what, k, n, lim, cite, drv, **st):
        """A node its gate drives LOW: the first VOL row whose IOL covers what the node asks the gate to sink."""
        v = vol_rows(drv[0], drv[1])
        for iol, vol in v["rows"]:
            r = network(B, k, n, "LOW", drive={drv: vol}, **st)
            if r["sink_A"] is not None and r["sink_A"] <= iol: break
        r["driver"] = "%s %s pin %s, VOL %.2f V at IOL %g mA: %s; the node asks it to sink %.1f uA of stated current, so the " \
            "pins no sheet bounds would have to pass %.3g mA more to leave this row" % (
                drv[0], drv[1], drv[2], vol, iol * 1e3, v["cite"], r["sink_A"] * 1e6, (iol - r["sink_A"]) * 1e3)
        va = r["v_adverse"]
        if lim is None: verdict = "UNDECIDED (no stated threshold)"
        elif va >= lim: verdict = "FAIL of the bound (the sheet's rows bound the level at %.2f V; what the part does is not stated)" % va
        elif r["unbounded"]: verdict = "PASS on the stated currents; UNDECIDED by the rule (a pin's current has no stated maximum)"
        else: verdict = "PASS"
        rows.append(dict(id=rid, what=what, node="%s %s" % (k, n), want="LOW", limit=lim, limit_cite=cite, verdict=verdict, **r))

    TPS2596 = "VUVLO(F) 1.08 V minimum: 'the device turns OFF the FET' (TI SLVSET8A 7.5 and 8.3.x); VSD 0.53 V minimum for the lowest shutdown current"
    TPS22810 = "VENF 1.08 V minimum (TI SLVSDH0C 7.5); VSHUTF 0.5 V minimum for low IQ"
    LM5176 = "VEN(STBY) 0.55 V minimum: below it 'the converter is held in a low power shutdown mode' (TI SNVSAI1D 6.5, 7.3.3); VEN(OP) 1.17 V minimum, below which the PWM controller is disabled"
    AP64500 = "VEN_L 1.03 V minimum (Diodes DS41979 Rev. 5-2, Electrical Characteristics)"
    TLV758 = "VEN(LO) 0.3 V maximum (TI SBVS351D 5.5)"
    EN = [
        ("2a", "PA drain supply: PA_UVLO at board A's U13 (LM5176)", "A", "PA_UVLO", 0.55, LM5176, ("A", "U36", "4"), [("A", "+3V3_EMCON")], "A", "U13"),
        ("3", "QMX: HF_UVLO at board A's U15 (LM5176)", "A", "HF_UVLO", 0.55, LM5176, ("A", "U38", "4"), [("A", "+3V3_EMCON")], "A", "U15"),
        ("4", "RockBLOCK supply: RB_UVLO at board B's U24 (TPS259631)", "B", "RB_UVLO", 1.08, TPS2596, ("B", "U503", "4"), [("B", "+3V3_DEV")], "B", "U24"),
        ("4-en", "RockBLOCK ENABLE: RB_IEN at J_RB9704 pin 3", "B", "RB_IEN", 0.4, "Logic In LOW 0.4 V maximum (Ground Control, RockBLOCK 9704 hardware page, Signal Thresholds)", ("B", "U536", "4"), [("B", "+3V3_DEV")], "B", "J_RB9704"),
        ("5", "RM520N-GL supply: S2A_EN at board B's U203 (AP64500)", "B", "S2A_EN", 1.03, AP64500, ("B", "U216", "4"), None, "B", "U203"),
        ("6", "AW7915-AED slot 1 supply: S1A_EN at board B's U103 (AP64500)", "B", "S1A_EN", 1.03, AP64500, ("B", "U116", "4"), None, "B", "U103"),
        ("7", "AW7915-AED slot 3 supply: S3A_EN at board B's U303 (AP64500)", "B", "S3A_EN", 1.03, AP64500, ("B", "U316", "4"), None, "B", "U303"),
        ("14", "E22-900M30S supply: E22_UVLO at board B's U21 (TPS22810)", "B", "E22_UVLO", 1.08, TPS22810, ("B", "U504", "4"), [("B", "+3V3_DEV")], "B", "U21"),
        ("15-16", "both E72 supply: E72_EN at board B's U22 (TPS22810)", "B", "E72_EN", 1.08, TPS22810, ("B", "U505", "4"), [("B", "+3V3_DEV")], "B", "U22"),
        ("17", "LimeSDR supply: LIME_UVLO at board B's U23 (TPS259631)", "B", "LIME_UVLO", 1.08, TPS2596, ("B", "U502", "4"), [("B", "+3V3_DEV")], "B", "U23"),
        ("2b", "PA gate bias: PA_KEY at board D's U15 (TLV75801P)", "D", "PA_KEY", 0.3, TLV758, ("D", "U14", "4"), [("D", "+3V3_D8")], "D", "U15"),
        ("1-key", "SA868 keying: KEY at board D's U13 and U14", "D", "KEY", 0.8, LVC, ("D", "U12", "4"), [("D", "+3V3_D8")], "D", "U13"),
    ]
    for rid, what, k, n, lim, cite, drv, dead, rk, rref in EN:
        driven(rid + " (a)", what + ", EMCON asserted and its gate powered: the gate drives LOW", k, n, lim, cite, drv,
               reader=(rk, rref))
        if dead:
            row(rid + " (b)", what + ", its gate's own supply %s lost (0 V) with everything else up" % dead[0][1], k, n, "LOW",
                lim, cite, down=dead, reader=(rk, rref))
    # ------------------------------------------------------------ board D's supply gate for the exciter, the VGG regulator and the relay
    row("1-sup (b)", "board D's +5V_TX switch: TXSUP_EN at U21 (TPS22810) with +3V3_D8 at 0 V: the exciter, the VGG regulator "
        "and the relay coil lose their supply with the keying gates", "D", "TXSUP_EN", "LOW", 1.08, TPS22810, down=[("D", "+3V3_D8")],
        reader=("D", "U21"))
    # ------------------------------------------------------------ the SA868's keying pin, released
    row("1 (a)", "SA868 PTT: SA_PTT_n at U2 pin 5, EMCON asserted: U13 released, the pin held by R88 and R89 from +5V_SA", "D",
        "SA_PTT_n", "HIGH", None, "NiceRF states no '1' level for PTT (SA868 Rev 1.3, page 9)", reader=("D", "U2"))
    # ------------------------------------------------------------ the module pins EMCON pulls low through an open drain
    for s, u in ((1, 30), (2, 31), (3, 32)):
        for nm, pin, ch in (("WL_nDIS", "89", "6"), ("BT_nDIS", "91", "4")):
            driven("%d" % ({("WL_nDIS", 1): 8, ("WL_nDIS", 2): 9, ("WL_nDIS", 3): 10, ("BT_nDIS", 1): 11, ("BT_nDIS", 2): 12,
                            ("BT_nDIS", 3): 13}[(nm, s)]) + " (a)",
                   "CM5 slot %d %s at U%dA pin %s, EMCON asserted: U%d13 sinks the module's 1.8 kOhm pull-up" % (s, nm, u, pin, s),
                   "B", "%s%d" % (nm, s), None,
                   "the CM5 datasheet states no input-low level for pins 89 and 91 ('if driven low, the ... interface will be "
                   "disabled', release 3, page 20)", ("B", "U%d13" % s, ch), reader=("B", "U%dA" % u))
    Q = "'driving FULL_CARD_POWER_OFF# pin LOW (<= 0.2 V) or tri-stating the pin will turn off the module' (Quectel RM520N " \
        "series Hardware Design v1.1, 3.5)"
    driven("5-off (a1)", "RM520N-GL FULL_CARD_POWER_OFF# at J_M2C2 pin 6 at the instant EMCON asserts, the socket rail still up: "
           "U220 sinks R238", "B", "5G_PWROFF_n", 0.2, Q, ("B", "U220", "6"), reader=("B", "J_M2C2"))
    driven("5-off (a2)", "RM520N-GL FULL_CARD_POWER_OFF# at J_M2C2 pin 6 with EMCON held, the socket rail removed", "B",
           "5G_PWROFF_n", 0.2, Q, ("B", "U220", "6"), down=[("B", "+3V3_S2A")], reader=("B", "J_M2C2"))
    # ------------------------------------------------------------ the lamp
    row("lamp (b)", "the EMCON lamp's gate: EMCLAMP_G at board C's Q7 with U14 unpowered (board C's +3V3 lost, its +5V up): the "
        "lamp is dark", "C", "EMCLAMP_G", "LOW", 0.6, "VGS(th) 0.6 V minimum (Vishay Si2300DS, as board C's part value quotes it; the "
        "sheet's own row is a 25 C figure)", down=[("C", "+3V3")], reader=("C", "Q7"))
    os.makedirs(outd, exist_ok=True)
    L = ["The level at each EMCON control node in each fault state (stream d4emcon, tools/fault_levels.py)"]
    for k in sorted(B.sha): L.append("  board %s  %s  sha256/16 %s" % (k, NETLISTS[k], B.sha[k]))
    L.append("  conventions: resistors and rails at their adverse ends (5 percent where no tolerance is stated), a dead rail open,")
    L.append("  pin currents at their stated maximum in the adverse direction (v_adverse) and in the other (v_other)")
    L.append("")
    for r in rows:
        L.append("=" * 118)
        L.append("%s  %s" % (r["id"], r["what"]))
        L.append("   node %s must stay %s; limit %s: %s" % (r["node"], r["want"], ("%.2f V" % r["limit"]) if r["limit"] is not None else "none stated", r["limit_cite"]))
        if r["floating"]:
            L.append("   RESULT: the node floats")
        else:
            L.append("   RESULT: %.3f V adverse, %.3f V with the pin currents the other way, %s uA of stated pin current: %s" % (
                r["v_adverse"], r["v_other"], r["sum_uA"], r["verdict"]))
        if r.get("driver"): L.append("     drv   " + r["driver"])
        for x in r["legs"]: L.append("     leg   " + x)
        for x in r["leaks"]: L.append("     pin   %-14s %-44s %8.3f uA   %s" % (x["node"], x["pin"], x["uA"], x["cite"][:120]))
        for x in r["unbounded"]: L.append("     UNBOUNDED  " + x[:230])
        if r.get("v_adverse_nodes") and len(r["v_adverse_nodes"]) > 1:
            L.append("     nodes (adverse): " + ", ".join("%s %.3f V" % kv for kv in sorted(r["v_adverse_nodes"].items())))
    L.append("")
    L.append("SUMMARY")
    for r in rows:
        L.append("  %-12s %-13s %-38s %s" % (r["id"], r["node"], ("floats" if r["floating"] else "%.3f V (other polarity %.3f V)" % (
            r["v_adverse"], r["v_other"])), r["verdict"] + ("" if r["limit"] is None else " against %.2f V" % r["limit"])))
    open(os.path.join(outd, "fault-levels-set6.txt"), "w").write("\n".join(L) + "\n")
    json.dump(dict(netlists=B.sha, rows=rows), open(os.path.join(outd, "fault-levels-set6.json"), "w"), indent=1, sort_keys=True, default=str)
    print("\n".join(L[-(len(rows) + 1):]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
