#!/usr/bin/env python3
"""check_l8p_netlist.py: what the regenerated netlists of boards P, E and A must show for record l8p's drafts (Layer 8,
MESHSAT-1357, 4 October 2026): W4DP-F2's breaker on board P and its make-last dock enable loop through boards E and A (record
l9stk section 15.4, C-1 and C-1b, conditions C1 and C2, 15.5's thermal guard). It PARSES the KiCad netlists (an s-expression
reader, never a grep) and the project's own 2 x 6 dock lands, and judges:

  board P  BRK   U101 (LM5069-2) pins 1 SENSE BRK_SNS, 2 VIN BRK_VIN, 3 UVLO BRK_UVLO, 4 OVLO and 5 GND on the return, 6 TIMER, 7 PWR,
                 8 PGD open, 9 OUT PACK_P, 10 GATE BRK_GATE; the sense pair R101 and R102 from BRK_VIN to BRK_SNS; Q101 and Q102
                 sources on PACK_P, gates on BRK_GATE, drains on BRK_SNS; Q2's source, R6, R7 and R19 on BRK_VIN; R103 on PWR, C101
                 on TIMER, C102 on GATE, each to the return; C104 and C105 in series from BRK_VIN to the return; D101's cathode on BRK_VIN and anode on the return; D1
                 still on PACK_P; W_P on PACK_P; the values of record l9stk (VALUES below)
           EN    R106 from BRK_VIN to DOCK_EN_OUT; J_SMB pin 7 DOCK_EN_OUT, pin 5 DOCK_EN_RET, pins 1 to 4 SMBC, SMBD, the return,
                 PRES_J; R107 and Q103's gate on DOCK_EN_RET; Q103 drain BRK_G2; R108 and R109 the divider of BRK_G2; Q104 gate
                 BRK_G2, drain BRK_DIS; R105 from BRK_DIS to BRK_UVLO; R104 from BRK_VIN to BRK_UVLO; C103 from BRK_UVLO to the return;
                 every inverter source on the return; the return is W_N's net (PACK_N)
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

# The values the drafts draw, each with its place in record l9stk (branch fnd/l9stk at 2c8b29fb): (board, ref, value prefix,
# l9stk source, the pattern l8p_drafts.py finds in the record's own text, input file key). The netlist must carry each prefix.
VALUES = [
    ("p", "U101", "LM5069MM-2", "15.4 C-1, 'an LM5069-2 circuit breaker on board P'", r"C-1, an LM5069-2 circuit breaker on board P", "page"),
    ("p", "R101", "4m 1%", "15.4 table, Sense RS: 4 mOhm and 7.5 mOhm in parallel, 1 %", r"\| Sense RS \| 4 mOhm and 7\.5 mOhm in parallel, 2\.6087 mOhm, 1 % and at most 50 ppm/K", "page"),
    ("p", "R102", "7.5m 1%", "15.4 table, Sense RS", r"\| Sense RS \| 4 mOhm and 7\.5 mOhm in parallel", "page"),
    ("p", "Q101", "CSD18510Q5B", "15.4 table, FETs: 2 x CSD18510Q5B", r"\| FETs \| 2 x CSD18510Q5B, 40 V", "page"),
    ("p", "Q102", "CSD18510Q5B", "15.4 table, FETs", r"\| FETs \| 2 x CSD18510Q5B", "page"),
    ("p", "R103", "8.45k", "15.4 table, Power limit: RPWR 8.45 kOhm", r"\| Power limit \| RPWR 8\.45 kOhm", "page"),
    ("p", "C101", "10n", "15.4 table, Fault timer: 10 nF", r"\| Fault timer \| 10 nF", "page"),
    ("p", "C102", "22n", "15.4 table, dv/dt start: 22 nF", r"\| dv/dt start \| 22 nF into 593 uF", "page"),
    ("p", "D101", "SMCJ18A", "15.4 table, Clamps: SMCJ18A on VIN", r"\| Clamps \| SMCJ18A on VIN \(VR 18 V, VC 29\.2 V at 51\.4 A\)", "page"),
    ("p", "R104", "200k", "15.4 table, Controller: UVLO from VIN through R_U 200 kOhm", r"UVLO from VIN through R_U 200 kOhm into C_U 3\.3 uF \(50 V\)", "page"),
    ("p", "C103", "3.3u 50V", "15.4 table, Controller: into C_U 3.3 uF (50 V)", r"into C_U 3\.3 uF \(50 V\), released by the enable loop", "page"),
    ("p", "R106", "10k", "15.4 C-1b: the loop leaves board P from VIN through 10 kOhm", r"The loop leaves board P from VIN through 10 kOhm on one J_SMB contact", "page"),
    ("p", "R107", "22k", "15.4 C-1b: a 22 kOhm divider on a first 2N7002's gate", r"to a 22 kOhm divider on a first 2N7002's gate", "page"),
    ("p", "Q103", "2N7002", "15.4 C-1b: a first 2N7002", r"a first 2N7002's gate\. That FET holds a\s+second 2N7002's gate low", "page"),
    ("p", "Q104", "2N7002", "15.4 C-1b: a second 2N7002", r"second 2N7002's gate low; the second, when on, discharges UVLO through 150 ohm", "page"),
    ("p", "R105", "150R", "15.4 C-1b: discharges UVLO through 150 ohm", r"discharges UVLO through 150 ohm", "page"),
    ("p", "R108", "1M", "l9stk_protection.py R_G (prot 3a): the second inverter's gate divider, each half", r"R_G = 1e6\s+# the second inverter's gate divider, each half", "constants"),
    ("p", "R109", "1M", "l9stk_protection.py R_G (prot 3a)", r"R_G = 1e6\s+# the second inverter's gate divider, each half", "constants"),
    ("a", "RT1", "PRF15BB103RB6RC", "15.5 THE THERMAL GUARD: the kit's PRF15BB103 chip PTC, in the enable loop on the battery FETs' copper", r"\*\*The part\.\*\* The kit's PRF15BB103 chip PTC", "page"),
]


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


def checks_p(nl):
    if "U101" not in nl["comps"] and _pin(nl, "J_SMB", "7") is None and "DOCK_EN_OUT" not in nl["on"]:
        return {"BRK": ("NOT DRAWN", ["U101 is absent"]), "EN": ("NOT DRAWN", ["J_SMB has no pin 7"])}
    ret = _pin(nl, "W_N", "1")
    vin, sns = "BRK_VIN", "BRK_SNS"
    rows = [("U101", "1", sns), ("U101", "2", vin), ("U101", "3", "BRK_UVLO"), ("U101", "4", ret), ("U101", "5", ret),
            ("U101", "6", "BRK_TMR"), ("U101", "7", "BRK_PWR"), ("U101", "9", "PACK_P"), ("U101", "10", "BRK_GATE"),
            ("D101", "1", vin), ("D101", "2", ret), ("D1", "1", "PACK_P"), ("D1", "2", ret), ("W_P", "1", "PACK_P"),
            ("R6", "1", vin), ("R7", "1", vin), ("R19", "2", vin), ("Q2", "4", "DSG_G"), ("Q2", "5", "SW")]
    rows += [(q, p, "PACK_P") for q in ("Q101", "Q102") for p in "123"] + [(q, "4", "BRK_GATE") for q in ("Q101", "Q102")]
    rows += [(q, "5", sns) for q in ("Q101", "Q102")] + [("Q2", p, vin) for p in "123"]
    bad = props(nl, rows)
    if _pin(nl, "U101", "8") not in (None, "") and not str(_pin(nl, "U101", "8")).startswith("unconnected-"):
        bad.append("U101.8 (PGD) on %r, drafted open" % _pin(nl, "U101", "8"))
    for ref, a, b in (("R101", vin, sns), ("R102", vin, sns), ("R103", "BRK_PWR", ret), ("C101", "BRK_TMR", ret),
                      ("C102", "BRK_GATE", ret), ("C104", vin, "BRK_CMID"), ("C105", "BRK_CMID", ret)):
        if _two(nl, ref) != sorted({a, b}):
            bad.append("%s on %s, wanted %s to %s" % (ref, _two(nl, ref), a, b))
    bad += [x for x in values(nl, "p") if x.split()[0] in ("U101", "R101", "R102", "Q101", "Q102", "R103", "C101", "C102", "D101")]
    if "PACK_P" in {n for n in nl["pins"].get("Q2", {}).values()}:
        bad.append("Q2 still drives PACK_P")
    out = {"BRK": ("FAIL", bad) if bad else ("DRAWN", [])}
    rows = [("J_SMB", "1", "SMBC"), ("J_SMB", "2", "SMBD"), ("J_SMB", "3", ret), ("J_SMB", "4", "PRES_J"), ("J_SMB", "5", RET),
            ("J_SMB", "6", ret), ("J_SMB", "7", OUT), ("Q103", "1", RET), ("Q103", "2", ret), ("Q103", "3", "BRK_G2"),
            ("Q104", "1", "BRK_G2"), ("Q104", "2", ret), ("Q104", "3", "BRK_DIS")]
    bad = props(nl, rows)
    for ref, a, b in (("R106", vin, OUT), ("R107", RET, ret), ("R108", vin, "BRK_G2"), ("R109", "BRK_G2", ret),
                      ("R105", "BRK_DIS", "BRK_UVLO"), ("R104", vin, "BRK_UVLO"), ("C103", "BRK_UVLO", ret)):
        if _two(nl, ref) != sorted({a, b}):
            bad.append("%s on %s, wanted %s to %s" % (ref, _two(nl, ref), a, b))
    bad += [x for x in values(nl, "p") if x.split()[0] not in ("U101", "R101", "R102", "Q101", "Q102", "R103", "C101", "C102", "D101")]
    if nl["comps"].get("J_SMB", {}).get("footprint") != XH7:
        bad.append("J_SMB on %r, not the 7-circuit XH land" % nl["comps"].get("J_SMB", {}).get("footprint"))
    o, r = loop_pins(nl, "J_SMB")
    if len(o) == 1 and len(r) == 1:
        bad += between(nl, o[0], r[0], ret, "J_SMB", nl["pins"].get("J_SMB", {}))
    else:
        bad.append("J_SMB carries the loop on %s and %s" % (o, r))
    out["EN"] = ("FAIL", bad) if bad else ("DRAWN", [])
    return out


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
