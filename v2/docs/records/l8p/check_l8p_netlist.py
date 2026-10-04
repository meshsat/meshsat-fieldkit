#!/usr/bin/env python3
"""check_l8p_netlist.py: what the regenerated netlists of boards P, E and A must show for record l8p's drafts (Layer 8,
MESHSAT-1357, 4 October 2026): W4DP-F2's breaker on board P and its make-last dock enable loop through boards E and A (record
l9stk section 15.4, C-1 and C-1b, conditions C1 and C2, 15.5's thermal guard). It PARSES the KiCad netlists (an s-expression
reader, never a grep) and the project's own 2 x 6 dock lands, and judges:

  board P  BRK   U101 (LM5069-1, latch-off) pins 1 SENSE BRK_SNS, 2 VIN BRK_VIN, 3 UVLO BRK_UVLO, 4 OVLO and 5 GND on the return,
                 6 TIMER, 7 PWR, 8 PGD on BRK_PGD, 9 OUT PACK_P, 10 GATE BRK_GATE; the sense pair R101 and R102 from BRK_VIN to BRK_SNS;
                 Q101 and Q102 sources on PACK_P, gates on BRK_GATE, drains on BRK_SNS; Q2's source, R6, R7 and R19 on BRK_VIN; R103 on
                 PWR, C101 on TIMER, C102 on GATE, each to the return; C104 and C105 in series from BRK_VIN to the return; D101's
                 cathode on BRK_VIN and anode on the return; D1 still on PACK_P; W_P on PACK_P; the values of record l9stk (VALUES)
           EN    R106 from BRK_VIN to DOCK_EN_OUT; J_SMB pin 7 DOCK_EN_OUT, pin 5 DOCK_EN_RET, pins 1 to 4 SMBC, SMBD, the return,
                 PRES_J; R107 and Q103's gate on DOCK_EN_RET; Q103 drain BRK_G2; R108 and R109 the divider of BRK_G2; Q104 gate
                 BRK_G2, drain on UVLO itself; the hold: R104 from BRK_VIN to BRK_H, C103 from BRK_H to the return, R105 from BRK_H
                 to BRK_HD, D102's anode on BRK_HD and cathode on UVLO; every inverter source on the return (W_N's net, PACK_N)
           INH   the restart inhibit (C-1c): RT101 (NXRT15XH103FA1B) from INH_NTC to the return under R110 from BRK_VIN; R111 and
                 R112 the reference from BRK_VIN; U102 (OPA187) +IN on the reference, -IN on the NTC, V+ on BRK_VIN, V- on the
                 return; R113 from its output to the reference; R114 and R115 its output's divider onto Q105's gate; Q105's drain
                 on UVLO; Q106's gate on U101's PGD net (with R116 from BRK_VIN and R117 to the return) and its drain on Q105's gate;
                 C106 on U102's supply; the values
           REV   the reverse-charge detector (B-R2, route R1, round 3): U103 (OPA187) +IN on R10's cell side (the net R10 shares
                 with no PACK_N pin, through R120) with C109 to the return, -IN on R118 over R119 to the return from REV_VZ, which
                 R129 feeds from U101's VIN and D103 (BZT52C12, cathode on REV_VZ) holds to the return; V+ on U101's VIN, V- on the
                 return; U104 (OPA187) +IN on PACK_P over R121 and R122, -IN on BRK_SNS over R123 and
                 R124, C110 across its inputs, the same supply; R125 and R126 halve U103's output onto Q107's gate, R127 and R128
                 U104's onto Q108's; Q107 drain on the loop's return (Q103's gate net), source on Q108's drain; Q108 source on the
                 return: the two in series, so the return is held low only while both comparators are high; C107 and C108 on
                 the comparators' supply pins; the values; and U104's threshold sits on the right side (its -IN divider's ratio
                 above its +IN's, so PACK_P must exceed BRK_SNS)
  board E  EN    J_SMB pins 1 to 4 SMBC, SMBD, GND, PRES_LEAD, 5 DOCK_EN_RET, 6 GND, 7 DOCK_EN_OUT; J_BLK pin 3 DOCK_EN_RET, 4 GND,
                 5 DOCK_EN_OUT; nothing else on board E on the loop's nets (a pass-through)
  board A  EN    J_DOCK pin 3 DOCK_EN_RET, 4 GND, 5 DOCK_EN_OUT; RT1 (PRF15BB103) from DOCK_EN_OUT to DOCK_EN_RET, and nothing else
                 on the loop's nets
  GROUND BETWEEN (condition C2), on every board present: on J_SMB (a 1x7 row, circuits numbered in order along it) the two loop
                 pins are not neighbours and every pin between them is the board's return; on J_BLK and J_DOCK (the 2 x 6 fields,
                 positions read from meshsat.pretty's PogoTargets_2x6 and PogoPins_2x6) a ground pad sits at the midpoint of the two
                 loop pads and the two are not neighbours
  LOOP     with all three: P's J_SMB pins 7 and 5, E's J_SMB pins 7 and 5, E's J_BLK pins and A's J_DOCK pins of the same numbers
                 carry the same two nets, and RT1 closes them on board A: BRK_VIN, R106, the lead, the dock, RT1 and back to Q103
Each board reads DRAWN (every property holds), NOT DRAWN (the draft's marker part is absent: today's state) or FAIL (present and
wrong). Nothing has been built or measured: the statements are about netlists.

Usage:  check_l8p_netlist.py [p=path.net] [e=path.net] [a=path.net]      (default: the committed netlists of the tree)
Exit 0 when every board given reads DRAWN (and the loop holds when all three are given), 4 otherwise, 2 on a usage error."""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
PRETTY = os.path.join(REPO, "v2", "ecad", "meshsat.pretty")
COMMITTED = {"p": "v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net", "e": "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net",
             "a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"}
OUT, RET = "DOCK_EN_OUT", "DOCK_EN_RET"
XH7 = "Connector_JST:JST_XH_B7B-XH-A_1x07_P2.50mm_Vertical"
LANDS = {"J_DOCK": "PogoPins_2x6", "J_BLK": "PogoTargets_2x6"}

# The values the drafts draw from record l9stk (branch fnd/l9stk at 0d72880b), each with its place there: (board, ref, value
# prefix, l9stk source, the phrase l8p_drafts.py finds in the record's own text (spaces match any run of white space), input file
# key). The netlist must carry each prefix. The parts the record leaves to the drawing are this record's SESSION choices and are
# held by the checks below, not here.
VALUES = [
    ("p", "U101", "LM5069MM-1", "15.4 C-1 and 15.4b: the -1, latch-off", "C-1, an LM5069 circuit breaker on board P, the -1 (latch-off, 15.4b),", "page"),
    ("p", "R101", "4m 1%", "15.4 table, Sense RS: 4 mOhm and 7.5 mOhm in parallel, 1 %", "| Sense RS | 4 mOhm and 7.5 mOhm in parallel, 2.6087 mOhm, 1 % and at most 50 ppm/K", "page"),
    ("p", "R102", "7.5m 1%", "15.4 table, Sense RS", "| Sense RS | 4 mOhm and 7.5 mOhm in parallel", "page"),
    ("p", "Q101", "CSD18510Q5B", "15.4 table, FETs: 2 x CSD18510Q5B", "| FETs | 2 x CSD18510Q5B, 40 V", "page"),
    ("p", "Q102", "CSD18510Q5B", "15.4 table, FETs", "| FETs | 2 x CSD18510Q5B", "page"),
    ("p", "R103", "8.45k", "15.4 table, Power limit: RPWR 8.45 kOhm", "| Power limit | RPWR 8.45 kOhm", "page"),
    ("p", "C101", "10n", "15.4 table, Fault timer: 10 nF", "| Fault timer | 10 nF", "page"),
    ("p", "C102", "22n", "15.4 table, dv/dt start: 22 nF", "| dv/dt start | 22 nF into 593 uF", "page"),
    ("p", "D101", "SMCJ18A", "15.4 table, Clamps: SMCJ18A on VIN", "| Clamps | SMCJ18A on VIN (VR 18 V, VC 29.2 V at 51.4 A)", "page"),
    ("p", "R104", "200k", "15.4 table, Controller, and C-1b's hold: R_U 200 kOhm from VIN onto the node H", "R_U, the series resistor (200 kOhm from VIN), charges C_U on a node H.", "page"),
    ("p", "C103", "3.3u 50V", "15.4 table, Controller: C_U 3.3 uF (50 V)", "into C_U 3.3 uF (50 V), released by the enable loop", "page"),
    ("p", "R105", "150R", "15.4 C-1b, the hold: H reaches UVLO through 150 ohm", "H reaches UVLO through 150 ohm and a 1N4148W.", "page"),
    ("p", "D102", "1N4148W", "15.4 C-1b, the hold: and a 1N4148W", "H reaches UVLO through 150 ohm and a 1N4148W.", "page"),
    ("p", "R106", "10k", "15.4 C-1b: the loop leaves board P from VIN through 10 kOhm", "The loop leaves board P from VIN through 10 kOhm on one J_SMB contact", "page"),
    ("p", "R107", "22k", "15.4 C-1b: a 22 kOhm divider on a first 2N7002's gate", "to a 22 kOhm divider on a first 2N7002's gate", "page"),
    ("p", "Q103", "2N7002", "15.4 C-1b: a first 2N7002", "That FET holds a second 2N7002's gate low;", "page"),
    ("p", "Q104", "2N7002", "15.4 C-1b: the second, when on, pulls UVLO itself", "the second, when on, pulls UVLO itself.", "page"),
    ("p", "R108", "1M", "l9stk_protection.py R_G (prot 3a): the second inverter's gate divider, each half", "R_G = 1e6 # the second inverter's gate divider, each half", "constants"),
    ("p", "R109", "1M", "l9stk_protection.py R_G (prot 3a)", "R_G = 1e6 # the second inverter's gate divider, each half", "constants"),
    ("p", "RT101", "NXRT15XH103FA1B", "15.4b C-1c, the sensor: Murata NXRT15XH103FA1B", "The kit's NTC sheet part, Murata NXRT15XH103FA1B (10 kOhm plus or minus 1 %, B25/85 3434 K, B plus or minus 1 %),", "page"),
    ("p", "R110", "150k 0.1%", "15.4b C-1c: 150 kOhm over the NTC", "The bridge has 150 kOhm over the NTC: 0.111 mA at most, against its 0.12 mA.", "page"),
    ("a", "RT1", "PRF15BB103RB6RC", "15.5 THE THERMAL GUARD: the kit's PRF15BB103 chip PTC, in the enable loop on the battery FETs' copper", "**The part.** The kit's PRF15BB103 chip PTC", "page"),
]


def phrase_rx(phrase):
    """A phrase as a pattern: its words escaped, any run of white space between them."""
    return r"\s+".join(re.escape(w) for w in phrase.split())


def sexp(text):
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


def kv(node, key):
    for x in node[1:] if isinstance(node, list) else []:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def read_netlist(raw):
    tree = sexp(raw.decode("utf-8", "replace"))
    root = tree[0] if tree and isinstance(tree[0], list) else tree
    comps, pins = {}, {}
    for sec in (root[1:] if isinstance(root, list) else []):
        if not (isinstance(sec, list) and sec):
            continue
        if sec[0] == "components":
            for c in sec[1:]:
                if isinstance(c, list) and c and c[0] == "comp":
                    ref, val, fp = kv(c, "ref"), kv(c, "value"), kv(c, "footprint")
                    if ref and len(ref) > 1:
                        comps[ref[1]] = {"value": val[1] if val and len(val) > 1 else "", "footprint": fp[1] if fp and len(fp) > 1 else ""}
        elif sec[0] == "nets":
            for n in sec[1:]:
                if not (isinstance(n, list) and n and n[0] == "net"):
                    continue
                name = str((kv(n, "name") or [None, ""])[1]).lstrip("/")
                for x in n[1:]:
                    if isinstance(x, list) and x and x[0] == "node":
                        r, p = kv(x, "ref"), kv(x, "pin")
                        if r and p and len(r) > 1 and len(p) > 1:
                            pins.setdefault(r[1], {})[p[1]] = name
    on = {}
    for r, d in pins.items():
        for p, n in d.items():
            on.setdefault(n, set()).add(r)
    return {"comps": comps, "pins": pins, "on": on}


def land_positions(name):
    """{pad number: (x, y)} of a land in the project library, parsed from its s-expression."""
    raw = open(os.path.join(PRETTY, name + ".kicad_mod"), encoding="utf-8").read()
    tree = sexp(raw)
    root = tree[0] if tree and isinstance(tree[0], list) else tree
    out = {}
    for x in root[1:]:
        if isinstance(x, list) and x and x[0] == "pad" and len(x) > 1:
            at = kv(x, "at")
            out[str(x[1])] = (float(at[1]), float(at[2]))
    return out


def _pin(nl, ref, pin):
    return nl["pins"].get(ref, {}).get(pin)


def _two(nl, ref):
    return sorted(set(nl["pins"].get(ref, {}).values()))


def props(nl, rows):
    """rows: [(ref, pin, net)]; the failures."""
    return ["%s.%s on %r, wanted %s" % (r, p, _pin(nl, r, p), n) for r, p, n in rows if _pin(nl, r, p) != n]


def between(nl, a, b, ret, ref=None, pins=None):
    """C2's ground contact between the two loop conductors of `ref` (`pins` maps pin to net)."""
    bad = []
    if ref in LANDS:
        pos = land_positions(LANDS[ref])
        pa, pb = pos[a], pos[b]
        d = ((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2) ** 0.5
        pitch = min(((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) ** 0.5 for k, x in pos.items() for j, y in pos.items() if k != j)
        if d < 1.5 * pitch:
            bad.append("%s pins %s and %s are neighbours (%.2f mm apart, pitch %.2f mm)" % (ref, a, b, d, pitch))
        mid = ((pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0)
        at_mid = [k for k, x in pos.items() if abs(x[0] - mid[0]) < 0.01 and abs(x[1] - mid[1]) < 0.01]
        if not at_mid or any(pins.get(k) != ret for k in at_mid):
            bad.append("%s: no ground pad between pins %s and %s (pads at the midpoint %s on %s)" % (ref, a, b, at_mid, [pins.get(k) for k in at_mid]))
    else:
        lo, hi = sorted((int(a), int(b)))
        if hi - lo < 2:
            bad.append("%s pins %s and %s are neighbours" % (ref, a, b))
        mids = [str(k) for k in range(lo + 1, hi)]
        if any(pins.get(k) != ret for k in mids):
            bad.append("%s: pins between %s and %s are %s, not all %s" % (ref, a, b, [pins.get(k) for k in mids], ret))
    return bad


def loop_pins(nl, ref):
    d = nl["pins"].get(ref, {})
    return [p for p, n in d.items() if n == OUT], [p for p, n in d.items() if n == RET]


def values(nl, board):
    return ["%s value %r does not start %r (l9stk %s)" % (ref, nl["comps"].get(ref, {}).get("value"), pre, src)
            for b, ref, pre, src, _pat, _f in VALUES if b == board and not str(nl["comps"].get(ref, {}).get("value", "")).startswith(pre)]


BRK_VALUES = ("U101", "R101", "R102", "Q101", "Q102", "R103", "C101", "C102", "D101")
EN_VALUES = ("R104", "C103", "R105", "D102", "R106", "R107", "Q103", "Q104", "R108", "R109")
INH_VALUES = ("RT101", "R110")
# the restart inhibit's parts the record leaves to the drawing (record l8p's SESSION choices), each value's prefix
INH_SESSION = (("U102", "OPA187"), ("R111", "147k 0.1%"), ("R112", "1.62k 0.1%"), ("R113", "15M"), ("Q105", "2N7002"), ("Q106", "2N7002"))
# the reverse-charge detector (B-R2, route R1, round 3): record l8p's SESSION choices, each value's prefix
REV_SESSION = (("U103", "OPA187"), ("U104", "OPA187"), ("R118", "1.15M 0.1%"), ("R119", "200R 0.1%"), ("R120", "200R"), ("C109", "470n"),
               ("R129", "47k"), ("D103", "BZT52C12"),
               ("R121", "332k 0.05% 10ppm"), ("R122", "33.2k 0.05% 10ppm"), ("R123", "328k 0.05% 10ppm"), ("R124", "33.2k 0.05% 10ppm"),
               ("C110", "1n"), ("C107", "100n"), ("C108", "100n"), ("R125", "100k"), ("R126", "100k"), ("R127", "100k"), ("R128", "100k"),
               ("Q107", "2N7002"), ("Q108", "2N7002"))


def _pairs(nl, rows):
    return ["%s on %s, wanted %s to %s" % (ref, _two(nl, ref), a, b) for ref, a, b in rows if _two(nl, ref) != sorted({a, b})]


def checks_p(nl):
    if "U101" not in nl["comps"] and _pin(nl, "J_SMB", "7") is None and "DOCK_EN_OUT" not in nl["on"]:
        return {"BRK": ("NOT DRAWN", ["U101 is absent"]), "EN": ("NOT DRAWN", ["J_SMB has no pin 7"]), "INH": ("NOT DRAWN", ["U102 is absent"]),
                "REV": ("NOT DRAWN", ["U103 is absent"])}
    ret = _pin(nl, "W_N", "1")
    vin, sns, uvlo, pgd = "BRK_VIN", "BRK_SNS", "BRK_UVLO", "BRK_PGD"
    rows = [("U101", "1", sns), ("U101", "2", vin), ("U101", "3", uvlo), ("U101", "4", ret), ("U101", "5", ret),
            ("U101", "6", "BRK_TMR"), ("U101", "7", "BRK_PWR"), ("U101", "8", pgd), ("U101", "9", "PACK_P"), ("U101", "10", "BRK_GATE"),
            ("D101", "1", vin), ("D101", "2", ret), ("D1", "1", "PACK_P"), ("D1", "2", ret), ("W_P", "1", "PACK_P"),
            ("R6", "1", vin), ("R7", "1", vin), ("R19", "2", vin), ("Q2", "4", "DSG_G"), ("Q2", "5", "SW")]
    rows += [(q, p, "PACK_P") for q in ("Q101", "Q102") for p in "123"] + [(q, "4", "BRK_GATE") for q in ("Q101", "Q102")]
    rows += [(q, "5", sns) for q in ("Q101", "Q102")] + [("Q2", p, vin) for p in "123"]
    bad = props(nl, rows)
    bad += _pairs(nl, (("R101", vin, sns), ("R102", vin, sns), ("R103", "BRK_PWR", ret), ("C101", "BRK_TMR", ret),
                       ("C102", "BRK_GATE", ret), ("C104", vin, "BRK_CMID"), ("C105", "BRK_CMID", ret)))
    bad += [x for x in values(nl, "p") if x.split()[0] in BRK_VALUES]
    if "PACK_P" in {n for n in nl["pins"].get("Q2", {}).values()}:
        bad.append("Q2 still drives PACK_P")
    out = {"BRK": ("FAIL", bad) if bad else ("DRAWN", [])}
    rows = [("J_SMB", "1", "SMBC"), ("J_SMB", "2", "SMBD"), ("J_SMB", "3", ret), ("J_SMB", "4", "PRES_J"), ("J_SMB", "5", RET),
            ("J_SMB", "6", ret), ("J_SMB", "7", OUT), ("Q103", "1", RET), ("Q103", "2", ret), ("Q103", "3", "BRK_G2"),
            ("Q104", "1", "BRK_G2"), ("Q104", "2", ret), ("Q104", "3", uvlo), ("D102", "1", uvlo), ("D102", "2", "BRK_HD")]
    bad = props(nl, rows)
    bad += _pairs(nl, (("R106", vin, OUT), ("R107", RET, ret), ("R108", vin, "BRK_G2"), ("R109", "BRK_G2", ret),
                       ("R104", vin, "BRK_H"), ("C103", "BRK_H", ret), ("R105", "BRK_H", "BRK_HD")))
    bad += [x for x in values(nl, "p") if x.split()[0] in EN_VALUES]
    if nl["comps"].get("J_SMB", {}).get("footprint") != XH7:
        bad.append("J_SMB on %r, not the 7-circuit XH land" % nl["comps"].get("J_SMB", {}).get("footprint"))
    o, r = loop_pins(nl, "J_SMB")
    if len(o) == 1 and len(r) == 1:
        bad += between(nl, o[0], r[0], ret, "J_SMB", nl["pins"].get("J_SMB", {}))
    else:
        bad.append("J_SMB carries the loop on %s and %s" % (o, r))
    out["EN"] = ("FAIL", bad) if bad else ("DRAWN", [])
    # C-1c: the restart inhibit, ratiometric from the breaker's own input, gated by its PGD, acting on its UVLO
    vin_u, uvlo_u, pgd_u = _pin(nl, "U101", "2"), _pin(nl, "U101", "3"), _pin(nl, "U101", "8")
    rows = [("U102", "1", "INH_OUT"), ("U102", "2", ret), ("U102", "3", "INH_REF"), ("U102", "4", "INH_NTC"), ("U102", "5", vin_u),
            ("Q105", "1", "INH_G"), ("Q105", "2", ret), ("Q105", "3", uvlo_u), ("Q106", "1", pgd_u), ("Q106", "2", ret), ("Q106", "3", "INH_G")]
    bad = props(nl, rows)
    bad += _pairs(nl, (("RT101", "INH_NTC", ret), ("R110", vin_u, "INH_NTC"), ("R111", vin_u, "INH_REF"), ("R112", "INH_REF", ret),
                       ("R113", "INH_OUT", "INH_REF"), ("R114", "INH_OUT", "INH_G"), ("R115", "INH_G", ret),
                       ("R116", vin_u, pgd_u), ("R117", pgd_u, ret), ("C106", vin_u, ret)))
    bad += [x for x in values(nl, "p") if x.split()[0] in INH_VALUES]
    bad += ["%s value %r does not start %r (record l8p, SESSION)" % (r_, nl["comps"].get(r_, {}).get("value"), pre)
            for r_, pre in INH_SESSION if not str(nl["comps"].get(r_, {}).get("value", "")).startswith(pre)]
    if (nl["comps"].get("RT101") or {}).get("footprint") != "meshsat:LeadLands_1x02":
        bad.append("RT101 is not on the lead lands (its 10 mm leads to two lands beside the pad)")
    out["INH"] = ("FAIL", bad) if bad else ("DRAWN", [])
    # B-R2, route R1: the reverse-charge detector holds the loop's return low while the charge into the cells exceeds its threshold
    # AND the breaker's body diodes conduct; its two senses, its supply and its one output are read from the pins
    sens = [n for n in set(nl["pins"].get("R10", {}).values()) if n != ret]
    cell = sens[0] if len(sens) == 1 else None
    rows = [("U103", "1", "REV_IOUT"), ("U103", "2", ret), ("U103", "3", "REV_ISNS"), ("U103", "4", "REV_IREF"), ("U103", "5", vin_u),
            ("U104", "1", "REV_VOUT"), ("U104", "2", ret), ("U104", "3", "REV_VP"), ("U104", "4", "REV_VN"), ("U104", "5", vin_u),
            ("Q107", "1", "REV_IG"), ("Q107", "2", "REV_MID"), ("Q107", "3", _pin(nl, "Q103", "1")),
            ("Q108", "1", "REV_VG"), ("Q108", "2", ret), ("Q108", "3", "REV_MID"), ("D103", "1", "REV_VZ"), ("D103", "2", ret)]
    bad = props(nl, rows)
    if cell is None or ret not in nl["pins"].get("R10", {}).values():
        bad.append("R10 is not the sense between the cells and the return (%s)" % _two(nl, "R10"))
    if _pin(nl, "Q103", "1") != RET:
        bad.append("Q107's drain is not on the loop's return: Q103's gate reads %r" % _pin(nl, "Q103", "1"))
    bad += _pairs(nl, (("R129", vin_u, "REV_VZ"), ("R118", "REV_VZ", "REV_IREF"), ("R119", "REV_IREF", ret), ("R120", cell, "REV_ISNS"), ("C109", "REV_ISNS", ret),
                       ("R121", "PACK_P", "REV_VP"), ("R122", "REV_VP", ret), ("R123", sns, "REV_VN"), ("R124", "REV_VN", ret),
                       ("C110", "REV_VP", "REV_VN"), ("R125", "REV_IOUT", "REV_IG"), ("R126", "REV_IG", ret),
                       ("R127", "REV_VOUT", "REV_VG"), ("R128", "REV_VG", ret), ("C107", vin_u, ret), ("C108", vin_u, ret)))
    bad += ["%s value %r does not start %r (record l8p, SESSION)" % (r_, nl["comps"].get(r_, {}).get("value"), pre)
            for r_, pre in REV_SESSION if not str(nl["comps"].get(r_, {}).get("value", "")).startswith(pre)]
    if nl["on"].get("REV_MID", set()) != {"Q107", "Q108"}:
        bad.append("REV_MID reaches %s, wanted Q107 and Q108 alone (the two in series)" % sorted(nl["on"].get("REV_MID", set())))
    ratio = {}
    for top, bot in (("R121", "R122"), ("R123", "R124")):
        try:
            rt_, rb_ = (_ohms(nl["comps"][x]["value"]) for x in (top, bot))
            ratio[top] = rb_ / (rt_ + rb_)
        except (KeyError, ValueError):
            pass
    if len(ratio) != 2 or not ratio["R123"] > ratio["R121"]:
        bad.append("U104's threshold is not on the reverse side (the -IN divider's ratio %s, the +IN's %s)" % (ratio.get("R123"), ratio.get("R121")))
    out["REV"] = ("FAIL", bad) if bad else ("DRAWN", [])
    return out


def _ohms(value):
    """A resistor value's leading figure in ohms: '328k 0.05% ...' is 328000.0, '200R ...' 200.0, '1.15M ...' 1150000.0."""
    m = re.match(r"([0-9.]+)\s*([RkKM]?)", str(value))
    if not m:
        raise ValueError(value)
    return float(m.group(1)) * {"": 1.0, "R": 1.0, "k": 1e3, "K": 1e3, "M": 1e6}[m.group(2)]


def checks_e(nl):
    if _pin(nl, "J_SMB", "7") is None and "DOCK_EN_OUT" not in nl["on"]:
        return {"EN": ("NOT DRAWN", ["J_SMB has no pin 7"])}
    rows = [("J_SMB", "1", "SMBC"), ("J_SMB", "2", "SMBD"), ("J_SMB", "3", "GND"), ("J_SMB", "4", "PRES_LEAD"), ("J_SMB", "5", RET),
            ("J_SMB", "6", "GND"), ("J_SMB", "7", OUT), ("J_BLK", "3", RET), ("J_BLK", "4", "GND"), ("J_BLK", "5", OUT)]
    bad = props(nl, rows)
    for n in (OUT, RET):
        if nl["on"].get(n, set()) != {"J_SMB", "J_BLK"}:
            bad.append("%s reaches %s, wanted J_SMB and J_BLK alone (a pass-through)" % (n, sorted(nl["on"].get(n, set()))))
    if nl["comps"].get("J_SMB", {}).get("footprint") != XH7:
        bad.append("J_SMB on %r, not the 7-circuit XH land" % nl["comps"].get("J_SMB", {}).get("footprint"))
    for ref in ("J_SMB", "J_BLK"):
        o, r = loop_pins(nl, ref)
        if len(o) == 1 and len(r) == 1:
            bad += between(nl, o[0], r[0], "GND", ref, nl["pins"].get(ref, {}))
        else:
            bad.append("%s carries the loop on %s and %s" % (ref, o, r))
    return {"EN": ("FAIL", bad) if bad else ("DRAWN", [])}


def checks_a(nl):
    if "RT1" not in nl["comps"] and "DOCK_EN_OUT" not in nl["on"]:
        return {"EN": ("NOT DRAWN", ["RT1 is absent"])}
    bad = props(nl, [("J_DOCK", "3", RET), ("J_DOCK", "4", "GND"), ("J_DOCK", "5", OUT)])
    if _two(nl, "RT1") != sorted({OUT, RET}):
        bad.append("RT1 on %s, wanted %s to %s" % (_two(nl, "RT1"), OUT, RET))
    for n in (OUT, RET):
        if nl["on"].get(n, set()) != {"J_DOCK", "RT1"}:
            bad.append("%s reaches %s, wanted J_DOCK and RT1 alone" % (n, sorted(nl["on"].get(n, set()))))
    bad += values(nl, "a")
    o, r = loop_pins(nl, "J_DOCK")
    if len(o) == 1 and len(r) == 1:
        bad += between(nl, o[0], r[0], "GND", "J_DOCK", nl["pins"].get("J_DOCK", {}))
    else:
        bad.append("J_DOCK carries the loop on %s and %s" % (o, r))
    return {"EN": ("FAIL", bad) if bad else ("DRAWN", [])}


def check_loop(nls):
    """The loop across the three boards, by pin numbers and net names."""
    p, e, a = nls["p"], nls["e"], nls["a"]
    bad = []
    for pin in ("5", "7"):
        if _pin(p, "J_SMB", pin) != _pin(e, "J_SMB", pin) or _pin(p, "J_SMB", pin) not in (OUT, RET):
            bad.append("J_SMB pin %s: P %r, E %r" % (pin, _pin(p, "J_SMB", pin), _pin(e, "J_SMB", pin)))
    for n in (OUT, RET):
        ke = [k for k, v in e["pins"].get("J_BLK", {}).items() if v == n]
        ka = [k for k, v in a["pins"].get("J_DOCK", {}).items() if v == n]
        if not ke or ke != ka:
            bad.append("%s on J_BLK %s and on J_DOCK %s" % (n, ke, ka))
    if _two(a, "RT1") != sorted({OUT, RET}):
        bad.append("RT1 does not close the loop on board A: %s" % _two(a, "RT1"))
    if _pin(p, "U101", "2") not in _two(p, "R106") or OUT not in _two(p, "R106") or _pin(p, "Q103", "1") != RET:
        bad.append("board P: R106 %s, U101.2 %r, Q103.1 %r" % (_two(p, "R106"), _pin(p, "U101", "2"), _pin(p, "Q103", "1")))
    return ("FAIL", bad) if bad else ("DRAWN", [])


def judge(letter, nl):
    res = {"p": checks_p, "e": checks_e, "a": checks_a}[letter](nl)
    lines = ["%s %-4s %s%s" % (letter.upper(), k, v, (": " + "; ".join(why[:3])) if why else "") for k, (v, why) in res.items()]
    vs = [v for v, _w in res.values()]
    worst = "DRAWN" if all(v == "DRAWN" for v in vs) else ("FAIL" if "FAIL" in vs else "NOT DRAWN")
    if worst == "NOT DRAWN" and "DRAWN" in vs:
        worst = "FAIL"
    return worst, lines


def run(paths, repo=REPO, out=sys.stdout, label=None):
    verdicts, nls = {}, {}
    for letter in ("p", "e", "a"):
        if letter not in paths:
            continue
        raw = open(paths[letter], "rb").read()
        name = label(letter) if label else os.path.relpath(paths[letter], repo)
        out.write("%s sha256 %s\n" % (name, hashlib.sha256(raw).hexdigest()[:16]))
        nls[letter] = read_netlist(raw)
        v, lines = judge(letter, nls[letter])
        verdicts[letter] = v
        for l in lines:
            out.write("  %s\n" % l)
    if set(nls) == {"p", "e", "a"} and all(v == "DRAWN" for v in verdicts.values()):
        v, why = check_loop(nls)
        verdicts["loop"] = v
        out.write("  LOOP %s%s\n" % (v, (": " + "; ".join(why[:3])) if why else ""))
    vs = list(verdicts.values())
    kit = "DRAWN" if vs and all(v == "DRAWN" for v in vs) else ("FAIL" if "FAIL" in vs else "NOT DRAWN")
    out.write("record l8p's breaker and enable loop on the netlists: %s\n" % kit)
    return kit, verdicts


def main(argv):
    paths = {}
    for a in argv:
        if len(a) > 2 and a[0] in "pea" and a[1] == "=":
            paths[a[0]] = a[2:]
        else:
            sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
            return 2
    kit, _v = run(paths or {k: os.path.join(REPO, v) for k, v in COMMITTED.items()})
    return 0 if kit == "DRAWN" else 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
