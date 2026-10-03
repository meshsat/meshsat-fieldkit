#!/usr/bin/env python3
"""check_l8r2_netlist.py: what the regenerated netlists of boards A and B must show for record l8r2's corrections (Layer 8,
MESHSAT-1357, 3 October 2026). It PARSES a KiCad netlist (an s-expression reader, never a grep) and judges each correction:

  board A  VCO   J_VR1 to J_VR4 pin 1 on VIN_RAW_IN; Q41 pins 1 to 3 (source) on VIN_RAW, pin 4 (gate) on VCO_GATE, pin 5 (drain) on
                 VIN_RAW_IN; U45 pin 2 (OV) on VCO_OV, pin 13 (SRC) on VIN_RAW, pin 14 (PD) on VCO_GATE, pins 7, 8, 9, 10 on GND, pin 19
                 (ISCP) with pin 17 (CS-); R241 between VBUS20 and VCO_OV, R242 between VCO_OV and GND (item 2, S-111)
           D8V3  U44 pin 4 (IN) on +3V3, pin 5 (OUT) on +3V3_A2D; J_MEZZ1 pin 13 on +3V3_A2D; R234 on U44's ILM (item 3, L5R2-F05)
           SLOTS for s in 1 and 3 (round 4, L9P-F02): the LM5176 U(501 or 531) pin 1 (EN) on SLOT_ENs, pin 12 (VOSNS) on +5V_Ss; the
                 stage's VBAT entry Q(501 or 531) pin 5 (drain) on VBAT, pin 4 on Ss_HDRV1, pins 1 to 3 on Ss_SW1; the ISNS shunt
                 R(505 or 535) between Ss_OUT and +5V_Ss; the CS shunt R(506 or 536) between Ss_CS and GND; the INA226 (U8, U10) pin 10
                 on Ss_OUT and pin 8 on +5V_Ss; the AP64500 (U4, U6) and its inductor (L3, L5) gone
           FB01  round 6 (F5-03): the 5.1 V LM5176 stages' dividers at 0.1 %: R32, R33 (slot 2), R40, R41 (the device rail), and R501,
                 R502, R531, R532 where slots 1 and 3 are drawn, each value naming 0.1 %
  board B  FANs  for s in 1 to 3: J_FANs pin 1 on CFANs_V, pin 3 on CFANs_TACH, pin 4 on CFANs_PWM; the boost U(701+30(s-1)) pin 9 on
                 +5V_Ss and pin 6 on CFANs_12V; the eFuse U(702+30(s-1)) pin 4 on CFANs_12V and pin 5 on CFANs_V; the tach stage
                 Q(701+...) gate +3V3_CMs, source FAN_TACHOs, drain CFANs_TACH; the PWM stage Q(702+...) gate +3V3_CMs, source
                 FAN_PWMs, drain CFANs_PWM; no pin of +5V_Ss on J_FANs (item 1, E11-40)
           PNL   U901 pin 4 on +5V_DEV, pin 5 on PANEL_5V_EF; F1 between PANEL_5V_EF and PANEL_5V (item 3, L5R2-F03)
           PH4   J_QMX's and J_CAM's land Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical (item 3, L5R2-F04)
  board C  PIBTN U1 pin 16 (P1.3, PI_BTN_n) on PIJ2_A2; R57 between PIJ2_A2 and +3V3; FB4 pin 2, C27's other pin and J_PIJ2 pin 2 on GND
                 (item 4, the panel firmware's F-01)
Each reads DRAWN (every property holds), NOT DRAWN (the correction's new net or part is absent: today's state) or FAIL (present
and wrong). Nothing has been built or measured: the statements are about netlists.

Usage:  check_l8r2_netlist.py [a=path.net] [b=path.net] [c=path.net]      (default: the committed netlists of the tree)
Exit 0 when every correction reads DRAWN, 4 otherwise, 2 on a usage error."""
import glob
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
PH4 = "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical"


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
    fps, pins, vals = {}, {}, {}
    for sec in (root[1:] if isinstance(root, list) else []):
        if not (isinstance(sec, list) and sec):
            continue
        if sec[0] == "components":
            for c in sec[1:]:
                if isinstance(c, list) and c and c[0] == "comp":
                    ref, fp, va = kv(c, "ref"), kv(c, "footprint"), kv(c, "value")
                    if ref and len(ref) > 1:
                        fps[ref[1]] = fp[1] if fp and len(fp) > 1 else ""
                        vals[ref[1]] = va[1] if va and len(va) > 1 else ""
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
    return {"footprint": fps, "pins": pins, "value": vals}


def judge_props(nl, props, marker):
    """props: [(ref, pin, net)]; marker: a (ref, pin, net) whose absence means NOT DRAWN."""
    P = nl["pins"]
    if P.get(marker[0], {}).get(marker[1]) != marker[2]:
        return "NOT DRAWN", ["%s.%s is on %r, not %s" % (marker[0], marker[1], P.get(marker[0], {}).get(marker[1]), marker[2])]
    bad = ["%s.%s on %r, wanted %s" % (r, p, P.get(r, {}).get(p), n) for r, p, n in props if P.get(r, {}).get(p) != n]
    return ("FAIL", bad) if bad else ("DRAWN", [])


def checks_a(nl):
    out = {}
    vco = [("J_VR%d" % k, "1", "VIN_RAW_IN") for k in range(1, 5)] + [("Q41", p, "VIN_RAW") for p in "123"] + [
        ("Q41", "4", "VCO_GATE"), ("Q41", "5", "VIN_RAW_IN"), ("U45", "2", "VCO_OV"), ("U45", "13", "VIN_RAW"), ("U45", "14", "VCO_GATE"),
        ("U45", "7", "GND"), ("U45", "8", "GND"), ("U45", "9", "GND"), ("U45", "10", "GND"), ("R241", "1", "VBUS20"), ("R241", "2", "VCO_OV"),
        ("R242", "1", "VCO_OV"), ("R242", "2", "GND")]
    v, why = judge_props(nl, vco, ("Q41", "5", "VIN_RAW_IN"))
    iscp, csn = nl["pins"].get("U45", {}).get("19"), nl["pins"].get("U45", {}).get("17")
    if v == "DRAWN" and iscp != csn:
        v, why = "FAIL", ["U45.19 (ISCP) on %r, not with U45.17 (CS-) on %r" % (iscp, csn)]
    out["VCO"] = (v, why)
    d8 = [("U44", "4", "+3V3"), ("U44", "5", "+3V3_A2D"), ("J_MEZZ1", "13", "+3V3_A2D"), ("R234", "1", "U44_ILM")]
    out["D8V3"] = judge_props(nl, d8, ("J_MEZZ1", "13", "+3V3_A2D"))
    out["SLOTS"] = judge_props(nl, slot_props(), ("U501", "12", "+5V_S1"))
    if out["SLOTS"][0] == "DRAWN":
        left = [r for r in ("U4", "U6", "L3", "L5") if r in nl["pins"]]
        if left:
            out["SLOTS"] = ("FAIL", ["the AP64500 stage's %s still on the board" % ", ".join(left)])
    vals = nl.get("value", {})
    refs = ["R32", "R33", "R40", "R41"] + [r for r in ("R501", "R502", "R531", "R532") if r in vals]
    tight = [r for r in refs if "0.1%" in vals.get(r, "")]
    if not tight:
        out["FB01"] = ("NOT DRAWN", ["%s %r" % (r, vals.get(r)) for r in refs[:2]])
    elif len(tight) != len(refs):
        out["FB01"] = ("FAIL", ["%s %r" % (r, vals.get(r)) for r in refs if r not in tight])
    else:
        out["FB01"] = ("DRAWN", [])
    return out


def slot_props():
    """round 4 (L9P-F02): slots 1 and 3 on LM5176 stages, slot 2's (apply_gen_sch_a_slotlm.py)"""
    out = []
    for s, b, ina in (("1", 500, "U8"), ("3", 530, "U10")):
        out += [("U%d" % (b + 1), "1", "SLOT_EN%s" % s), ("U%d" % (b + 1), "12", "+5V_S%s" % s), ("Q%d" % (b + 1), "5", "VBAT"),
                ("Q%d" % (b + 1), "4", "S%s_HDRV1" % s)] + [("Q%d" % (b + 1), p, "S%s_SW1" % s) for p in "123"] + [
                ("R%d" % (b + 5), "1", "S%s_OUT" % s), ("R%d" % (b + 5), "2", "+5V_S%s" % s), ("R%d" % (b + 6), "1", "S%s_CS" % s),
                ("R%d" % (b + 6), "2", "GND"), (ina, "10", "S%s_OUT" % s), (ina, "8", "+5V_S%s" % s)]
    return out


def checks_b(nl):
    out = {}
    fans = []
    for s in (1, 2, 3):
        b = 700 + 30 * (s - 1)
        fans += [("J_FAN%d" % s, "1", "CFAN%d_V" % s), ("J_FAN%d" % s, "3", "CFAN%d_TACH" % s), ("J_FAN%d" % s, "4", "CFAN%d_PWM" % s),
                 ("U%d" % (b + 1), "9", "+5V_S%d" % s), ("U%d" % (b + 1), "6", "CFAN%d_12V" % s), ("U%d" % (b + 2), "4", "CFAN%d_12V" % s),
                 ("U%d" % (b + 2), "5", "CFAN%d_V" % s), ("Q%d" % (b + 1), "1", "+3V3_CM%d" % s), ("Q%d" % (b + 1), "2", "FAN_TACHO%d" % s),
                 ("Q%d" % (b + 1), "3", "CFAN%d_TACH" % s), ("Q%d" % (b + 2), "1", "+3V3_CM%d" % s), ("Q%d" % (b + 2), "2", "FAN_PWM%d" % s),
                 ("Q%d" % (b + 2), "3", "CFAN%d_PWM" % s)]
    out["FANS"] = judge_props(nl, fans, ("J_FAN1", "1", "CFAN1_V"))
    pnl = [("U901", "4", "+5V_DEV"), ("U901", "5", "PANEL_5V_EF"), ("F1", "1", "PANEL_5V_EF"), ("F1", "2", "PANEL_5V")]
    out["PNL"] = judge_props(nl, pnl, ("U901", "5", "PANEL_5V_EF"))
    fp = nl["footprint"]
    lands = {r: fp.get(r) for r in ("J_QMX", "J_CAM")}
    if all(l == PH4 for l in lands.values()):
        out["PH4"] = ("DRAWN", [])
    elif all(l and "PinHeader_1x04_P2.54mm" in l for l in lands.values()):
        out["PH4"] = ("NOT DRAWN", ["%s on %s" % (r, l) for r, l in sorted(lands.items())])
    else:
        out["PH4"] = ("FAIL", ["%s on %s" % (r, l) for r, l in sorted(lands.items())])
    return out


def checks_c(nl):
    P = nl["pins"]
    props = [("U1", "16", "PIJ2_A2"), ("FB4", "2", "GND"), ("J_PIJ2", "1", "PIJ2_A2"), ("J_PIJ2", "2", "GND")]
    v, why = judge_props(nl, props, ("U1", "16", "PIJ2_A2"))
    if v == "DRAWN":
        if set(P.get("R57", {}).values()) != {"PIJ2_A2", "+3V3"}:
            v, why = "FAIL", ["R57 on %r, wanted PIJ2_A2 to +3V3" % sorted(P.get("R57", {}).values())]
        elif set(P.get("C27", {}).values()) != {"PIJ2_A2", "GND"}:
            v, why = "FAIL", ["C27 on %r, wanted PIJ2_A2 to GND" % sorted(P.get("C27", {}).values())]
    return {"PIBTN": (v, why)}


def judge(letter, nl):
    res = checks_a(nl) if letter == "a" else checks_b(nl) if letter == "b" else checks_c(nl)
    lines = []
    for k, (v, why) in res.items():
        lines.append("%s %-5s %s%s" % (letter.upper(), k, v, (": " + "; ".join(why[:3])) if why else ""))
    worst = "DRAWN" if all(v == "DRAWN" for v, _w in res.values()) else ("FAIL" if any(v == "FAIL" for v, _w in res.values()) else "NOT DRAWN")
    return worst, lines


def fixture(letter):
    """A minimal netlist carrying record l8r2's corrections as drafted, for the check's own test."""
    nets = {}
    def add(net, ref, pin):
        nets.setdefault(net, []).append((ref, pin))
    comps, values = {}, {}
    if letter == "a":
        for k in range(1, 5): add("VIN_RAW_IN", "J_VR%d" % k, "1")
        for p in "123": add("VIN_RAW", "Q41", p)
        for ref, pin, net in (("Q41", "4", "VCO_GATE"), ("Q41", "5", "VIN_RAW_IN"), ("U45", "2", "VCO_OV"), ("U45", "13", "VIN_RAW"), ("U45", "14", "VCO_GATE"),
                              ("U45", "7", "GND"), ("U45", "8", "GND"), ("U45", "9", "GND"), ("U45", "10", "GND"), ("U45", "17", "VCO_VS"), ("U45", "19", "VCO_VS"),
                              ("R241", "1", "VBUS20"), ("R241", "2", "VCO_OV"), ("R242", "1", "VCO_OV"), ("R242", "2", "GND"), ("U44", "4", "+3V3"),
                              ("U44", "5", "+3V3_A2D"), ("J_MEZZ1", "13", "+3V3_A2D"), ("R234", "1", "U44_ILM"), ("U44", "7", "U44_ILM")):
            add(net, ref, pin)
        for ref, pin, net in slot_props():
            add(net, ref, pin)
        comps = {r: "Resistor_SMD:R_0603_1608Metric" for r in ("R32", "R33", "R40", "R41", "R501", "R502", "R531", "R532")}
        values = {r: ("53.6k 0.1%" if r in ("R32", "R40", "R501", "R531") else "10k 0.1%") for r in comps}
    else:
        for s in (1, 2, 3):
            b = 700 + 30 * (s - 1)
            for ref, pin, net in (("J_FAN%d" % s, "1", "CFAN%d_V" % s), ("J_FAN%d" % s, "3", "CFAN%d_TACH" % s), ("J_FAN%d" % s, "4", "CFAN%d_PWM" % s),
                                  ("U%d" % (b + 1), "9", "+5V_S%d" % s), ("U%d" % (b + 1), "6", "CFAN%d_12V" % s), ("U%d" % (b + 2), "4", "CFAN%d_12V" % s),
                                  ("U%d" % (b + 2), "5", "CFAN%d_V" % s), ("Q%d" % (b + 1), "1", "+3V3_CM%d" % s), ("Q%d" % (b + 1), "2", "FAN_TACHO%d" % s),
                                  ("Q%d" % (b + 1), "3", "CFAN%d_TACH" % s), ("Q%d" % (b + 2), "1", "+3V3_CM%d" % s), ("Q%d" % (b + 2), "2", "FAN_PWM%d" % s),
                                  ("Q%d" % (b + 2), "3", "CFAN%d_PWM" % s)):
                add(net, ref, pin)
        for ref, pin, net in (("U901", "4", "+5V_DEV"), ("U901", "5", "PANEL_5V_EF"), ("F1", "1", "PANEL_5V_EF"), ("F1", "2", "PANEL_5V"),
                              ("J_QMX", "1", "VBUS_QMX"), ("J_CAM", "1", "+5V_CAM")):
            add(net, ref, pin)
        comps = {"J_QMX": PH4, "J_CAM": PH4}
    if letter == "c":
        nets, comps = {}, {}
        for ref, pin, net in (("U1", "16", "PIJ2_A2"), ("FB4", "2", "GND"), ("J_PIJ2", "1", "PIJ2_A2"), ("J_PIJ2", "2", "GND"),
                              ("R57", "1", "PIJ2_A2"), ("R57", "2", "+3V3"), ("C27", "1", "PIJ2_A2"), ("C27", "2", "GND")):
            add(net, ref, pin)
    s = '(export (version "E")\n  (components\n'
    for ref, fp in sorted(comps.items()):
        s += '    (comp (ref "%s") (value "%s") (footprint "%s"))\n' % (ref, values.get(ref, "x"), fp)
    s += '  )\n  (nets\n'
    for i, (net, nodes) in enumerate(sorted(nets.items()), 1):
        s += '    (net (code "%d") (name "/%s")%s)\n' % (i, net, "".join(' (node (ref "%s") (pin "%s"))' % n for n in nodes))
    return (s + "  ))\n").encode()


def committed(repo):
    out = {}
    for p in sorted(glob.glob(os.path.join(repo, "v2", "ecad", "pcb-*", "out", "*.net"))):
        m = re.match(r"pcb-([abc])-", os.path.basename(os.path.dirname(os.path.dirname(p))))
        if m:
            out[m.group(1)] = p
    return out


def run(paths, repo=REPO, out=sys.stdout):
    verdicts = {}
    for letter in sorted(paths):
        raw = open(paths[letter], "rb").read()
        rel = os.path.relpath(paths[letter], repo)
        out.write("%s sha256 %s\n" % (rel, hashlib.sha256(raw).hexdigest()[:16]))
        v, lines = judge(letter, read_netlist(raw))
        verdicts[letter] = v
        for l in lines:
            out.write("  %s\n" % l)
    kit = "DRAWN" if verdicts and all(v == "DRAWN" for v in verdicts.values()) else ("FAIL" if "FAIL" in verdicts.values() else "NOT DRAWN")
    out.write("record l8r2's corrections on the netlists: %s\n" % kit)
    return kit, verdicts


def main(argv):
    paths = {}
    for a in argv:
        if len(a) > 2 and a[0] in "abc" and a[1] == "=":
            paths[a[0]] = a[2:]
        else:
            sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
            return 2
    kit, _v = run(paths or committed(REPO))
    return 0 if kit == "DRAWN" else 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
