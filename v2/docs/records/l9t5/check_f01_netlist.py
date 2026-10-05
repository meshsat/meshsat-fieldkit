#!/usr/bin/env python3
"""check_f01_netlist.py: what the regenerated netlists of boards A and D must show for record l9t5's F01 drafts, the PA drain-current
cap (P0-1, MESHSAT-1357, 5 October 2026). It PARSES the netlists (record l8p's s-expression reader, never a grep) and judges:

  board A  SENSE  U551 (INA250A2) IN+ 14 to 16 on +13V8_PA, IN- 1 to 3 on +13V8_PAJ; VIN+ 12 with SH+ 13 alone on one net, VIN- 5 with
                  SH- 4 alone on one net; GND 6, 8, 11; REF 7 on GND; OUT 9 PA_IMON; VS 10 on the loop's supply +5V_D8IN
           FEED   J_PA pin 1 on +13V8_PAJ, and nothing else on +13V8_PAJ but U551's IN- pins: no path to the PA bypasses the sense
           SET    U552 (TLV758P) OUT 1 PA_ISET, FB 2 PA_ISFB, EN 4 and IN 6 on +5V_D8IN; R551 PA_ISET to PA_ISFB over R552 PA_ISFB to GND;
                  the set point from their values: 0.55 V x (1 + R551 / R552) / 0.5 V/A, equal to l9t5_paloop.py's to 0.1 percent
           LOOP   U553 half A: IN1+ 3 on PA_ISET, IN1- 2 on PA_INTN, OUT1 1 on PA_INTO, R553 PA_IMON to PA_INTN, C554 PA_INTN to PA_INTO
                  (the sense on the INVERTING input: the integrator falls when the current is over); half B: IN2+ 5 PA_MID, IN2- 6
                  PA_INVN, OUT2 7 PA_ILIM_A, R554 PA_INTO to PA_INVN, R555 PA_INVN to PA_ILIM_A, R556 and R557 the midpoint; V+ 8 on
                  +5V_D8IN; R558 PA_ILIM_A to PA_ILIM; J_MEZZ1 pin 16 on PA_ILIM
           U13    its FB divider R50 and R51 at 0.1 percent (the case's margin rests on it)
  board D  INJ    J_HARN1 pin 16 on PA_ILIM; R57 PA_ILIM to VGG_FB; C76 PA_ILIM to GND; R82 VGG_SW to VGG_FB, R83 VGG_FB to GND; U15
                  FB 2 on VGG_FB, OUT 1 on VGG_SW, EN 4 on PA_KEY; nothing else on VGG_FB
           BAND   the band from R82, R83 and R57's values (l9t5_paloop.vgg_band): nominal 4.4825 V to 0.5 percent, top under 5 V, the
                  loop's authority under 3.5 V
  SIGN     the loop's sign read from the topology: PA_ILIM rises with the current (two inverting stages) and lowers VGG (R57 into the
           feedback node of a regulator whose output rises when FB falls): negative feedback, else FAIL
  BOTH     J_MEZZ1 pin 16 (A) and J_HARN1 pin 16 (D) on PA_ILIM
Each board reads DRAWN (every property holds), NOT DRAWN (U551 on A, or R57 on D, absent: the drawn state) or FAIL. Nothing has been
built or measured: these are statements about netlists.
Usage:  check_f01_netlist.py [a=path.net] [d=path.net]      (default: the committed netlists of the tree)
Exit 0 when every board given reads DRAWN (and the pair holds when both are given), 4 otherwise, 2 on a usage error."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(REPO, "v2", "docs", "records", "l8p"))
sys.path.insert(0, HERE)
import check_l8p_netlist as L8P  # noqa: E402
import l9t5_paloop as PL  # noqa: E402

COMMITTED = {"a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "d": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net"}
SUPPLY = "+5V_D8IN"


def pin(nl, ref, p):
    return nl["pins"].get(ref, {}).get(p)


def value(nl, ref):
    return nl["comps"].get(ref, {}).get("value", "")


def members(nl, net):
    return sorted("%s.%s" % (r, p) for r, d in nl["pins"].items() for p, n in d.items() if n == net)


def between(nl, ref, a, b):
    return sorted(set(nl["pins"].get(ref, {}).values())) == sorted({a, b})


def ohm(v):
    t = v.split()[0]
    mult = 1e3 if t.lower().endswith("k") else 1e6 if t.endswith("M") else 1.0
    return float(t.rstrip("kKM")) * mult


def rows(nl, want):
    return ["%s.%s on %r, wanted %s" % (r, p, pin(nl, r, p), n) for r, p, n in want if pin(nl, r, p) != n]


def check_a(nl, S=None):
    if "U551" not in nl["comps"]:
        return "NOT DRAWN", ["U551 is absent (the drawn state: J_PA on +13V8_PA, VGG open loop)"], {}
    bad = rows(nl, [("U551", p, "+13V8_PA") for p in ("14", "15", "16")] + [("U551", p, "+13V8_PAJ") for p in ("1", "2", "3")]
               + [("U551", p, "GND") for p in ("6", "7", "8", "11")] + [("U551", "9", "PA_IMON"), ("U551", "10", SUPPLY),
               ("J_PA", "1", "+13V8_PAJ"), ("J_PA", "2", "GND"),
               ("U552", "1", "PA_ISET"), ("U552", "2", "PA_ISFB"), ("U552", "3", "GND"), ("U552", "4", SUPPLY), ("U552", "6", SUPPLY),
               ("U553", "1", "PA_INTO"), ("U553", "2", "PA_INTN"), ("U553", "3", "PA_ISET"), ("U553", "4", "GND"), ("U553", "5", "PA_MID"),
               ("U553", "6", "PA_INVN"), ("U553", "7", "PA_ILIM_A"), ("U553", "8", SUPPLY), ("J_MEZZ1", "16", "PA_ILIM")])
    for a_, b_ in (("12", "13"), ("4", "5")):
        n1, n2 = pin(nl, "U551", a_), pin(nl, "U551", b_)
        if n1 != n2 or members(nl, n1) != sorted(["U551.%s" % a_, "U551.%s" % b_]):
            bad.append("U551 pins %s and %s are not alone on one net (Kelvin taps): %s" % (a_, b_, members(nl, n1)))
    feed = [m for m in members(nl, "+13V8_PAJ") if m not in ("U551.1", "U551.2", "U551.3", "J_PA.1")]
    if feed:
        bad.append("+13V8_PAJ carries more than the sense's load side and J_PA: %s" % feed)
    for ref, a_, b_ in (("R551", "PA_ISET", "PA_ISFB"), ("R552", "PA_ISFB", "GND"), ("R553", "PA_IMON", "PA_INTN"), ("C554", "PA_INTN", "PA_INTO"),
                        ("R554", "PA_INTO", "PA_INVN"), ("R555", "PA_INVN", "PA_ILIM_A"), ("R556", SUPPLY, "PA_MID"), ("R557", "PA_MID", "GND"),
                        ("R558", "PA_ILIM_A", "PA_ILIM")):
        if not between(nl, ref, a_, b_):
            bad.append("%s is not between %s and %s: %s" % (ref, a_, b_, sorted(set(nl["pins"].get(ref, {}).values()))))
    for ref in ("R50", "R51"):
        if "0.1%" not in value(nl, ref):
            bad.append("%s (U13's FB divider) is %r, not 0.1 percent" % (ref, value(nl, ref)))
    info = {}
    try:
        rt, rb = ohm(value(nl, "R551")), ohm(value(nl, "R552"))
        info["i_set"] = 0.55 * (1 + rt / rb) / PL.G_SENSE
        if abs(info["i_set"] / (0.55 * (1 + PL.R_SET_TOP / PL.R_SET_BOT) / PL.G_SENSE) - 1) > 0.001:
            bad.append("the set point from R551 %s and R552 %s is %.4f A, not l9t5_paloop.py's" % (value(nl, "R551"), value(nl, "R552"), info["i_set"]))
        if S is not None:
            L = PL.cap(S, 110e-6, 50.0, r_top=rt, r_bot=rb)
            info.update(i_min=L["i_min"], i_max=L["i_max"], u13_min=L["u13_min"])
            if L["i_max"] >= L["u13_min"]:
                bad.append("the cap's top %.4f A is not under U13's loop minimum %.4f A" % (L["i_max"], L["u13_min"]))
    except (ValueError, ZeroDivisionError) as e:
        bad.append("the set point's values do not parse: %s" % e)
    # the sign: half A takes the sense on its inverting input (R553 to IN1-) and the set point on IN1+; half B takes A's output on IN2-
    sign_a = -1 if (pin(nl, "U553", "2") == "PA_INTN" and pin(nl, "U553", "3") == "PA_ISET" and between(nl, "R553", "PA_IMON", "PA_INTN")) else +1
    sign_b = -1 if (pin(nl, "U553", "6") == "PA_INVN" and between(nl, "R554", "PA_INTO", "PA_INVN")) else +1
    info["sign_a_to_ilim"] = sign_a * sign_b
    if sign_a * sign_b != +1:
        bad.append("PA_ILIM does not rise with the PA's current (stage signs %+d, %+d): with board D's injection the loop would be positive feedback" % (sign_a, sign_b))
    return ("FAIL" if bad else "DRAWN"), (bad or ["U551, U552, U553 and the harness conductor as drafted; set point %.4f A" % info.get("i_set", float("nan"))]), info


def check_d(nl, S=None):
    if "R57" not in nl["comps"]:
        return "NOT DRAWN", ["R57 is absent (the drawn state: VGG open loop at 4.30 to 4.68 V)"], {}
    bad = rows(nl, [("J_HARN1", "16", "PA_ILIM"), ("U15", "1", "VGG_SW"), ("U15", "2", "VGG_FB"), ("U15", "4", "PA_KEY")])
    for ref, a_, b_ in (("R57", "PA_ILIM", "VGG_FB"), ("C76", "PA_ILIM", "GND"), ("R82", "VGG_SW", "VGG_FB"), ("R83", "VGG_FB", "GND")):
        if not between(nl, ref, a_, b_):
            bad.append("%s is not between %s and %s: %s" % (ref, a_, b_, sorted(set(nl["pins"].get(ref, {}).values()))))
    extra = [m for m in members(nl, "VGG_FB") if m not in ("U15.2", "R82.1", "R82.2", "R83.1", "R83.2", "R57.1", "R57.2")]
    if extra:
        bad.append("VGG_FB carries more than U15's FB, R82, R83 and R57: %s" % extra)
    info = {}
    if S is not None:
        try:
            r82, r83, r57 = ohm(value(nl, "R82")), ohm(value(nl, "R83")), ohm(value(nl, "R57"))
            lo, nom, hi, auth = PL.vgg_band(S, r82=r82, r83=r83, rinj=r57)
            info.update(band=(lo, nom, hi), auth=auth)
            if abs(nom / 4.4825 - 1) > 0.005:
                bad.append("VGG's nominal at rest is %.4f V, not the drawn 4.4825 V (R82 %s, R83 %s, R57 %s)" % (nom, value(nl, "R82"), value(nl, "R83"), value(nl, "R57")))
            if hi >= 5.0:
                bad.append("VGG's top at rest %.3f V is not under the module's 5 V" % hi)
            if auth >= 3.5:
                bad.append("the loop's authority leaves VGG at %.3f V, not under 3.5 V" % auth)
        except (ValueError, ZeroDivisionError) as e:
            bad.append("R82, R83 or R57's value does not parse: %s" % e)
    # the injection's sign: R57 feeds U15's FEEDBACK node (VGG falls as PA_ILIM rises); on VGG_SW it would drive the output itself
    if not between(nl, "R57", "PA_ILIM", "VGG_FB"):
        bad.append("R57 does not enter U15's feedback node, so PA_ILIM does not lower VGG through the regulator")
    return ("FAIL" if bad else "DRAWN"), (bad or ["J_HARN1 pin 16, R57, C76 and R83 as drafted"]), info


def main(argv):
    paths = {}
    for a in argv:
        if "=" not in a or a.split("=", 1)[0] not in ("a", "d"):
            sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
            return 2
        k, v = a.split("=", 1)
        paths[k] = v
    if not paths:
        paths = {k: os.path.join(REPO, v) for k, v in COMMITTED.items()}
    S = PL.read_sheets()
    ok = True
    nls = {}
    for k in ("a", "d"):
        if k not in paths:
            continue
        nl = L8P.read_netlist(open(paths[k], "rb").read())
        nls[k] = nl
        st, msgs, _info = (check_a if k == "a" else check_d)(nl, S)
        print("board %s F01 %s: %s" % (k.upper(), st, "; ".join(msgs)))
        ok = ok and st == "DRAWN"
    if "a" in nls and "d" in nls:
        pa, pd = pin(nls["a"], "J_MEZZ1", "16"), pin(nls["d"], "J_HARN1", "16")
        pair = pa == pd == "PA_ILIM"
        print("pair J_MEZZ1.16 / J_HARN1.16: %s (%s / %s)" % ("HOLDS" if pair else "FAIL", pa, pd))
        ok = ok and pair
    return 0 if ok else 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
