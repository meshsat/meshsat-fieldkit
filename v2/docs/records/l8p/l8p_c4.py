#!/usr/bin/env python3
"""l8p_c4.py: Layer 8 record l8p, round 8 (MESHSAT-1357, 5 October 2026): record l9stk's guard selection C4 CHECKED on the makers'
sheets (the brief's item 1, as round 7 checked G2), then the draft that draws it, apply_gen_sch_a_thguard.py, JUDGED on case row
C-PROT rev 1 (item 3). Findings L8P-F07 and L8P-F08 stay OPEN until an independent check has read this.

Record l9stk's round 5 (branch fnd/l9stk2 at bb6d2c8f; its page 15.9 and l9stk_guard.out, copied into inputs/ with sha256) re-selected
C4 after round 7's negative check of G2 (L8P-F08): the TI LM26LV 130 C switch and its TPS70950 supply as before, the shunt on
DOCK_EN_RET a 2N7002 through a gate network (47 kOhm, 1 uF, 1 MOhm), the fixed resistor in RT1's place two 7.5 kOhm in series.
This script prints:
  0. its pins;
  1. what record l9stk states of C4 (read from its copied output, never retyped);
  2. the 2N7002 on its sheet: the leakage, threshold and gate rows, its on-resistance rows (VGS 5 V and 10 V only);
  3. the count on the return and L4-E11 20c's window as a RAMP's reading at its corners, every sink on the return counted;
  4. the loop's four readings for C4 intact and with one of its pair shorted;
  5. the gate network against the switch's unprinted output before tEN: record l9stk's nominal figures, the same at the parts'
     tolerances, and the dwell a slow ramp would need to lift the gate to the 2N7002's least threshold;
  6. the two failure modes FM1 and FM2 and the clamps considered;
  7. the check's verdict (a figure that does not reproduce stops the judgement there);
  8. the draft as drawn (its values read from apply_gen_sch_a_thguard.py);
  9. C-PROT rev 1 on the draft: the no-trip side (10 A held, 18 A for 60 s, the gauge's condition C4) on the switch's printed
     limits, the trip before any battery FET's 150 C within the gradient budget, the loop's four readings, each source present or
     absent with the back-fed precharge, the docking start, the ground between boards A and P;
  10. each single failure of the new parts: it trips, or E-13b finds it, or it is named latent;
  11. the verdict, what stays open, and E-13b restated;
  12. the predicates.
Labels: PRINTED (a maker's printed limit), TYPICAL, ASSUMED, DERIVED (this script's arithmetic), RECORD (another record's figure, read
from its copy). Nothing has been built, bought or measured.

Run from the repository root:  python3 v2/docs/records/l8p/l8p_c4.py   (l8p_c4.out is its output, regenerated with _bin/regen_out.py).
Exit 0 on a completed check and judgement, whatever the verdict; 2 when an input is missing or a pattern no longer matches."""
import hashlib
import importlib.util
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import l8p_guard as G  # noqa: E402  (round 7's sheet readers: LM26LV, TPS709, AO3400A, 2N7002, LM5069; L4-E11 20c; l9stk 15)

L9_OUT5 = os.path.join(HERE, "inputs", "l9stk_guard-bb6d2c8f.out.txt")
L9_PAGE5 = os.path.join(HERE, "inputs", "l9stk-section15.9-bb6d2c8f.md")
PROT_OUT = os.path.join(HERE, "inputs", "l9stk_protection-0d72880b.out.txt")
BZT = os.path.join(ROOT, "v2", "vendor", "diodes", "diodes-bzt52c-ds18004.pdf")
DRAFT = os.path.join(HERE, "apply_gen_sch_a_thguard.py")
PINNED = {L9_OUT5: "d84dcb3bab2f1f6009eafa5aec98533d59ee9513e89f574595d7080020ffa79c",
          L9_PAGE5: "08a656ab0230986dbac4ec0c33c7f6c00f876eecb5792cf0343591796093cb9b"}

R106, R107, TOL = 10e3, 22e3, 0.01      # board P's loop resistors (record l8p's draft), 1 % ASSUMED (the draft prints none)
V_CLAMP = 29.2                          # BRK_VIN's clamp (record l9stk 15.4)
GUARD_ALLOW = 30e-6                     # the guard's allowance on DOCK_EN_OUT (record l9stk 15.9; Layer 5's row)
T_SITE = 86.25                          # board A's parts' ASSUMED site (record l9stk round 4 and 5, L4-E11 20d's figure)
DOUBLING = 10.0                         # ASSUMED: off leakage doubles every 10 K from the sheet's row (records l9stk, l8p, L4-E11)
HOT_RDS = 2.0                           # ASSUMED: on-resistance hot at twice the 25 C row (record l8p's convention, l9stk's N7_HOT)
C_TOL = 0.10                            # ASSUMED: the draft's capacitors at +-10 % (an X7R K grade; the value text prints none)
V_HELD, V_LOW, V_HIGH = 7.6, 10.6, 16.8  # the breaker's PORIT, the pack's least and most (record l9stk 15)
VDD_LOW_PR = 1.3                        # LM26LV: tEN is counted from VDD passing 1.3 V (SNIS144G Figure 1)
U = "\u00b5"


def refuse(msg):
    sys.stderr.write("l8p_c4: REFUSED: %s\n" % msg)
    sys.exit(2)


def rel(p):
    return os.path.relpath(p, ROOT)


def sha(p, n=64):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:n]


N = r"([0-9]+(?:\.[0-9]+)?)"      # a number, never its sentence's full stop


def need(text, pat, what, flags=re.M):
    m = re.search(pat, text, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its input" % what)
    return m


def ohms(v):
    m = re.match(r"([0-9.]+)\s*([RkKM]?)", v)
    return float(m.group(1)) * {"": 1.0, "R": 1.0, "k": 1e3, "K": 1e3, "M": 1e6}[m.group(2)]


def farads(v):
    m = re.match(r"([0-9.]+)\s*([pnu])", v)
    return float(m.group(1)) * {"p": 1e-12, "n": 1e-9, "u": 1e-6}[m.group(2)]


def read_l9stk5():
    """Record l9stk round 5's statements of C4, read from its copied output (RECORD)."""
    t = open(L9_OUT5, encoding="utf-8").read()
    pg = open(L9_PAGE5, encoding="utf-8").read()
    L = {}
    m = need(t, r"^\s+C4\s+2N7002\s+two 7\.5 kOhm in series\s+%s uA\s+%s uA\s+%s \(\s*%s\) uA\s+%s \(%s\) V\s+holds\s+%s C \(%s C\)" % ((N,) * 8), "l9stk: the C4 row")
    (L["leak"], L["allow"], L["sinks"], L["sinks_all"], L["ret"], L["ret_all"], L["site"], L["site_one"]) = (float(m.group(k)) for k in range(1, 9))
    m = need(t, r"(%s) uA before the shunt \((%s) uA all doubled\)" % (N, N), "l9stk: the count before the shunt")
    L["others"], L["others_all"] = float(m.group(1)), float(m.group(3))
    for key, lab in (("intact", r"C4"), ("one", r"C4, one")):
        m = need(t, r"^\s+%s\s+%s /\s+%s /\s+%s V\s+\(against 2\.5 V\)\s+%s V \(over 1\.981 V\)\s+%s mV \(under 775\.5 mV\)\s+from\s+%s V / %s V" % ((re.escape(lab),) + (N,) * 7),
                 "l9stk: the loop's readings, %s" % lab)
        L[key] = dict(gates=(float(m.group(1)), float(m.group(2)), float(m.group(3))), held=float(m.group(4)), ret_trip=float(m.group(5)),
                      reg_closed=float(m.group(6)), reg_trip=float(m.group(7)))
    m = need(t, r"Each closed phase lasts about %s ms" % N, "l9stk: FM1's closed phase")
    L["fm1_phase"] = float(m.group(1))
    m = need(t, r"adding\s+%s ms per uF at 7\.6 V: under the hold for an input capacitor under %s uF" % (N, N), "l9stk: FM1's input capacitor", re.M | re.S)
    L["fm1_per_uf"], L["fm1_cin"] = float(m.group(1)), float(m.group(2))
    L["allow_one"] = float(need(t, r"keeps the window \(allowance %s uA\)" % N, "l9stk: the one-shorted allowance").group(1))
    L["bands"] = {}
    for v in ("7.6", "10.6", "16.8"):
        m = need(t, r"BRK_VIN\s+%s V: tripped DOCK_EN_OUT\s+%s to\s+%s V intact,\s+%s to\s+%s V with one shorted" % ((re.escape(v),) + (N,) * 4), "l9stk: the band at %s V" % v)
        L["bands"][float(v)] = ((float(m.group(1)), float(m.group(2))), (float(m.group(3)), float(m.group(4))))
    L["fm2_from"] = float(need(t, r"over its 6 V absolute rating from BRK_VIN\s+%s V" % N, "l9stk: FM2").group(1))
    m = need(t, r"47 kOhm from OVERTEMP, 1 uF and 1 MOhm to ground: %s ms, a divider of %s" % (N, N), "l9stk: the gate network")
    L["tau"], L["div"] = float(m.group(1)), float(m.group(2))
    L["g_inv"] = float(need(t, r"leaves the gate at %s V, under the 2N7002's least 1 V" % N, "l9stk: the gate before tEN").group(1))
    m = need(t, r"a trip reaches 2\.5 V in\s+%s ms and the drive settles at %s V" % (N, N), "l9stk: the gate's rise", re.M | re.S)
    L["t_on"], L["g_on"] = float(m.group(1)), float(m.group(2))
    m = need(t, r"drives at least\s+%s V: %s ohm ASSUMED" % (N, N), "l9stk: the 2N7002's on-resistance bound", re.M | re.S)
    L["rds"] = float(m.group(2))
    m = need(t, r"the tripped return needs at most %s ohm\s+at the 29\.2 V clamp \(%s mA\)" % (N, N), "l9stk: the on-resistance needed", re.M | re.S)
    L["rds_need"], L["i_trip"] = float(m.group(1)), float(m.group(2))
    L["g_off"] = float(need(t, r"reaches its gate as %s V, against its least threshold 1 V" % N, "l9stk: the off gate").group(1))
    m = need(t, r"the BZT52C5V6\s+\(%s to %s V at 5 mA\) sits %s V over the regulator's %s V and prints its reverse current at 2 V only \(%s uA\)" % ((N,) * 5),
             "l9stk: the 5.6 V zener", re.M | re.S)
    L["z56"] = tuple(float(m.group(k)) for k in range(1, 6))
    L["z62_hi"] = float(need(t, r"the BZT52C6V2 reaches %s V, over the switch's 6 V" % N, "l9stk: the 6.2 V zener").group(1))
    m = need(t, r"no trip: 10 A held:\s+the hottest junction at the allowances %s C" % N, "l9stk: 10 A")
    L["j10"] = float(m.group(1))
    L["j18"] = float(need(t, r"no trip: 18 A for 60 s, read as held: the hottest junction at the allowances %s C" % N, "l9stk: 18 A").group(1))
    L["c4_j"] = float(need(t, r"the junction reads %s C held \(DERIVED" % N, "l9stk: the gauge's condition C4").group(1))
    m = need(t, r"18 A service, %s K at condition C4; %s K \(%s K\) left for the gradient" % (N, N, N), "l9stk: the margins restated")
    L["m_c4"], L["grad"], L["grad2"] = float(m.group(1)), float(m.group(2)), float(m.group(3))
    m = need(t, r"its junction leads its mounting base by %s K\s*\n\s+with two FETs carrying all.*?by %s K" % (N, N), "l9stk: the junction's lead", re.M | re.S)
    L["lead"], L["lead2"] = float(m.group(1)), float(m.group(2))
    need(pg, r"\*\*SELECTED \(SESSION\), round 5: C4\.\*\*", "l9stk 15.9: the selection C4")
    need(pg, r"place is two 7\.5 kOhm 1 % in series", "l9stk 15.9: the pair")
    m = need(pg, r"- Mutations: (.*?)\n- \*\*\(c\)", "l9stk 15.9 (b): the mutations", re.M | re.S)
    L["mutations"] = [x.strip() for x in re.split(r";", " ".join(m.group(1).split())) if x.strip()]
    return L


def read_2n7002():
    t = G.pdftext(G.N7002)
    S = {}
    S["vds"] = float(need(t, r"Drain-Source Voltage\s+VDS\s+%s" % N, "2N7002: VDS").group(1))
    S["vgs"] = float(need(t, r"Gate-Source Voltage\s+VGS\s+±%s" % N, "2N7002: VGS").group(1))
    S["tj"] = float(need(t, r"Junction Temperature\s+TJ\s+%s" % N, "2N7002: TJ").group(1))
    m = need(t, r"Gate-Threshold Voltage\s+Vth\(GS\)\s+VDS=VGS, ID=250 µA\s+%s\s+%s\s+%s" % (N, N, N), "2N7002: the threshold")
    S["vth"] = (float(m.group(1)), float(m.group(3)))
    m = need(t, r"Gate-body Leakage\s+lGSS\s+VDS=0 V, VGS=±20 V\s+±%s\s+nA" % N, "2N7002: IGSS")
    S["igss"] = float(m.group(1)) * 1e-9
    S["idss"] = float(need(t, r"Zero Gate Voltage Drain Current\s+IDSS\s+VDS=60 V, VGS=0 V\s+(\d+)\s+nA", "2N7002: IDSS").group(1)) * 1e-9
    m = need(t, r"VGS=10 V, ID=500mA\s+%s\s+%s\s*\n.*?Drain-Source On-Resistance.*?\n\s+VGS=5 V, ID=50mA\s+%s\s+%s" % (N, N, N, N), "2N7002: RDS(on)", re.M | re.S)
    S["r10"], S["r5"] = float(m.group(2)), float(m.group(4))
    need(t, r"Ta =25 ℃ unless otherwise specified", "2N7002: the table's 25 C")
    return S


def read_bzt():
    t = G.pdftext(BZT)
    need(t, r"DS18004 Rev\. 38", "BZT52C: the revision")
    Z = {}
    for part in ("BZT52C5V6", "BZT52C6V2"):
        m = need(t, r"^\s+%s\s+\S+\s+%s\s+%s\s+%s\s+%s\s+%s\s+%s\s+%s\s+%s\s+%s" % ((re.escape(part),) + (N,) * 9), "BZT52C: %s" % part)
        Z[part] = dict(vz=(float(m.group(2)), float(m.group(3))), iz=float(m.group(4)) * 1e-3, ir=float(m.group(8)) * 1e-6, vr=float(m.group(9)))
    return Z


def read_draft():
    sp = importlib.util.spec_from_file_location("l8p_thguard_values", DRAFT)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    D = dict(pair=tuple(ohms(v) for _r, v in m.PAIR), pair_refs=tuple(r for r, _v in m.PAIR), switch=m.SWITCH, reg=m.REG, shunt=m.SHUNT)
    g = dict(m.GATE)
    D["rg"], D["cg"], D["rpd"] = ohms(g["R262"]), farads(g["C260"]), ohms(g["R263"])
    c = dict(m.CAPS)
    D["cin"], D["cout"], D["cvdd"] = farads(c["C261"]), farads(c["C262"]), farads(c["C263"])
    D["cap_text"] = c
    D["tps"] = m.TPS
    D["new"] = m._NEW_LOOP
    return D


# ------------------------------------------------------------------------------------------------ the loop (DERIVED)
def ret_ramp(o, i_sink, rf, r7):
    """The return on a closed loop at a given DOCK_EN_OUT reading o, the sinks i_sink on it (a ramp's reading at any instant)."""
    return (o - i_sink * rf) * r7 / (rf + r7)


def allowance(o, ret_need, rf, r7):
    return (o - ret_need * (rf + r7) / r7) / rf


def bisect(f, lo, hi, n=80):
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if f(mid) else (mid, hi)
    return hi


def gate(v_src, tau, k, t):
    return v_src * k * (1.0 - math.exp(-t / tau))


def dock(v, D, S, hot=True, cg_scale=1.0, r_scale=1.0, uvlo=2.7, dt=2e-6, tmax=0.4):
    """The docking start with the drawn capacitors (DERIVED on ASSUMED behaviour: the regulator passes its input to its output once
    the input reaches its least rated 2.7 V, TI printing no UVLO threshold, with no dropout at microamps, through a 50 ohm stand-in
    for its pass element; the switch's outputs enabled tEN after VDD passes 1.3 V; OVERTEMP then at VDD - 0.2 V if hot): the time
    VDD passes 1.3 V and the time the shunt's gate passes the 2N7002's highest threshold."""
    r6, rf, r7 = R106 * (1 + TOL), D["rf"] * (1 + TOL), R107 * (1 - TOL)
    rg, rpd, cg = D["rg"] * r_scale, D["rpd"] * r_scale, D["cg"] * cg_scale
    cin, cv = D["cin"] * (1 + C_TOL), (D["cout"] + D["cvdd"]) * (1 + C_TOL)
    out = vdd = g = t = 0.0
    t13 = t25 = None
    ten = None
    while t < tmax:
        ret = max(0.0, (out / rf - D["sinks"]) / (1.0 / rf + 1.0 / r7))
        i_in = (v - out) / r6 - out / D["rout"] - (out - ret) / rf
        i_reg = (min(out, S["vreg_hi"]) - vdd) / 50.0 if out >= uvlo and vdd < min(out, S["vreg_hi"]) else 0.0
        vot = max(0.0, vdd - S["voh_drop"]) if (hot and ten is not None and t >= ten) else 0.0
        out += (i_in - i_reg) / cin * dt
        vdd += (i_reg - (S["is_max"] if vdd > 0.5 else 0.0) - max(0.0, (vot - g) / rg)) / cv * dt
        g += ((vot - g) / rg - g / rpd) / cg * dt
        if t13 is None and vdd >= VDD_LOW_PR:
            t13, ten = t, t + S["t_en"]
        if t25 is None and g >= S["vth_hi"]:
            t25 = t
        t += dt
    return t13, t25, vdd


def main():
    for p, want in PINNED.items():
        if not os.path.isfile(p):
            refuse("%s is absent" % rel(p))
        if sha(p) != want:
            refuse("%s is not the pinned bytes (sha256 %s, wanted %s)" % (rel(p), sha(p, 16), want[:16]))
    for p, want in G.PINNED.items():
        if not os.path.isfile(p):
            refuse("%s is absent (held back: run v2/docs/records/l8p/fetch_held_back.py)" % rel(p))
    L = read_l9stk5()
    S = G.read_sheets()
    R = G.read_records()
    N7 = read_2n7002()
    Z = read_bzt()
    D = read_draft()
    po = open(PROT_OUT, encoding="utf-8").read()
    m = need(po, r"which the RC\s+hold makes ([0-9.]+) to ([0-9.]+) s after the enable mates", "l9stk protection: the RC hold")
    hold = (float(m.group(1)), float(m.group(2)))
    t_off = float(need(po, r"\(UVLODEL 11 us typical, no maximum printed\): ([0-9.]+) ms in all", "l9stk protection: the turn-off").group(1)) * 1e-3
    pre = open(os.path.join(HERE, "inputs", "l4e11-section20c-4def5975.md"), encoding="utf-8").read()
    v_pre = float(need(pre, r"At the precharge's floor \(BRK_VIN %s V" % N, "L4-E11 20c: the precharge's floor").group(1))
    i_pre = float(need(pre, r"a back-fed precharge\s+carries at most %s A" % N, "L4-E11 20c: the precharge's current", re.M | re.S).group(1))

    out = []
    w = out.append
    w("l8p_c4: record l9stk's guard selection C4 CHECKED on the makers' sheets, then its draft JUDGED on case row C-PROT rev 1 (record l8p round 8,\n")
    w("MESHSAT-1357, 5 October 2026). Desk arithmetic on the makers' sheets, the records' copies and the draft's own values; nothing was built, bought\n")
    w("or measured. LABELS: PRINTED a maker's printed limit; TYPICAL; ASSUMED; DERIVED this script's arithmetic; RECORD another record's figure.\n\n")
    w("0. PINS (sha256/16)\n")
    for p in (L9_OUT5, L9_PAGE5, PROT_OUT, os.path.join(HERE, "inputs", "l4e11-section20c-4def5975.md"), G.LM26LV, G.TPS709, G.N7002, G.AO3400A, BZT,
              G.LM5069, DRAFT, os.path.join(HERE, "l8p_guard.py"), os.path.abspath(__file__)):
        w("   %s  %s%s\n" % (sha(p, 16), rel(p), "  (held back, fetch_held_back.py)" if "/held/" in p else ""))

    # ------------------------------------------------------------------ 1. record l9stk's statements
    w("\n1. WHAT RECORD l9stk STATES OF C4 (RECORD: its l9stk_guard.out and page 15.9 at bb6d2c8f, copied; SESSION, unchecked)\n")
    w("   the shunt a 2N7002 at %.2f uA (86.25 C), the allowance %.2f uA, the sinks %.2f (%.2f all doubled) uA, the return at DOCK_EN_OUT 1.825 V %.3f (%.3f) V,\n"
      % (L["leak"], L["allow"], L["sinks"], L["sinks_all"], L["ret"], L["ret_all"]))
    w("     the shunt's site free to %.1f C (%.1f C every FET on the return at one temperature); %.2f uA before the shunt (%.2f all doubled)\n"
      % (L["site"], L["site_one"], L["others"], L["others_all"]))
    for key, lab in (("intact", "intact"), ("one", "one of the pair shorted")):
        x = L[key]
        w("   %s: the first inverter's gate closed %.2f / %.2f / %.2f V; held DOCK_EN_OUT %.2f V; tripped return %.2f mV; the regulator's 6.0 V input\n"
          % (lab, x["gates"][0], x["gates"][1], x["gates"][2], x["held"], x["ret_trip"]))
        w("     from %.2f V closed, %.2f V tripped\n" % (x["reg_closed"], x["reg_trip"]))
    w("   the gate network 47 kOhm, 1 uF, 1 MOhm: %.1f ms, %.3f; %.3f V before tEN (3.8 ms); 2.5 V in %.1f ms, the drive %.2f V; off %.3f V; RDS(on) %.1f ohm\n"
      % (L["tau"], L["div"], L["g_inv"], L["t_on"], L["g_on"], L["g_off"], L["rds"]))
    w("     ASSUMED against %.0f ohm needed at %.2f mA\n" % (L["rds_need"], L["i_trip"]))
    w("   FM1 (one resistor): a closed phase %.1f ms, %.2f ms per uF of the regulator's input capacitor, under the hold below %.1f uF; with the pair one short\n"
      % (L["fm1_phase"], L["fm1_per_uf"], L["fm1_cin"]))
    w("     keeps the window (allowance %.2f uA); FM2 over the switch's 6 V from BRK_VIN %.2f V; acceptance (b)'s mutations: %d\n"
      % (L["allow_one"], L["fm2_from"], len(L["mutations"])))

    # ------------------------------------------------------------------ 2. the 2N7002
    w("\n2. THE 2N7002 ON ITS SHEET: JSCJ (Jiangsu Changjiang), SOT-23, September 2016, committed; every row at Ta 25 C (\"unless otherwise specified\")\n")
    w("   PRINTED: VDS %.0f V; VGS +-%.0f V; TJ %.0f C; threshold %.1f to %.1f V at VDS = VGS and 250 uA; IGSS +-%.0f nA at +-20 V; IDSS %.0f nA at 60 V\n"
      % (N7["vds"], N7["vgs"], N7["tj"], N7["vth"][0], N7["vth"][1], N7["igss"] * 1e9, N7["idss"] * 1e9))
    w("   PRINTED: RDS(on) %.0f ohm at most at VGS 10 V and 500 mA, %.0f ohm at VGS 5 V and 50 mA: no row under 5 V, none above 25 C\n" % (N7["r10"], N7["r5"]))
    w("   the leakage: one row, 25 C at 60 V; on the doubling (ASSUMED) %.2f uA at %.2f C; at the return's VDS of about 0.84 V NOT PRINTED (the 60 V\n"
      % (N7["idss"] * 2 ** ((T_SITE - 25.0) / DOUBLING) * 1e6, T_SITE))
    w("     row taken as the bound, as record l9stk counts it)\n")
    w("   the threshold: one row, 25 C at 250 uA; hot NOT PRINTED (it falls with temperature), the current under it NOT PRINTED; so \"under its least\n")
    w("     1 V\" bounds the gate against a 25 C row at 250 uA, not the microamps the window allows (relabelled: a margin, not a printed bound)\n")
    w("   the on-resistance: at the drive under 5 V NOT PRINTED; record l9stk's %.1f ohm (the 5 V row scaled by the drive over the highest threshold,\n" % L["rds"])
    w("     x2 hot) is ASSUMED, as it says; the requirement it is held against is DERIVED below\n")

    # ------------------------------------------------------------------ 3. the count and the window
    n7 = lambda t: N7["idss"] * 2.0 ** ((t - 25.0) / DOUBLING)
    sense1 = R["load_ret"]
    others = sense1 + 2 * n7(T_SITE) + N7["igss"]
    others_all = sense1 + 3 * n7(T_SITE)
    leak = n7(T_SITE)
    rf = sum(D["pair"])
    D["rf"] = rf
    rfp, rfm, r6p, r6m, r7p, r7m = rf * (1 + TOL), rf * (1 - TOL), R106 * (1 + TOL), R106 * (1 - TOL), R107 * (1 + TOL), R107 * (1 - TOL)
    alw = allowance(R["out_pw_lo"], R["ret_closed"], rfp, r7m)
    sinks, sinks_all = others + leak, others_all + leak
    ret, ret_all = ret_ramp(R["out_pw_lo"], sinks, rfp, r7m), ret_ramp(R["out_pw_lo"], sinks_all, rfp, r7m)
    site = 25.0 + DOUBLING * math.log2((alw - others) / N7["idss"])
    site_one = bisect(lambda t: sense1 + N7["igss"] + 3 * n7(t) > alw, -50.0, 250.0)
    fav = ret_ramp(R["out_pw_hi"], sinks, rf, R107)
    ao = S["ao_idss55"] * 2.0 ** ((T_SITE - 55.0) / DOUBLING)
    ret_ao = ret_ramp(R["out_pw_lo"], others + ao, rfp, r7m)
    w("\n3. THE COUNT ON THE RETURN AND L4-E11 20c's WINDOW AS A RAMP'S READING (DERIVED; R107 at -1 %, the pair's sum at +1 %: the two 7.5 kOhm at\n")
    w("   their worse sign together read as one 15 kOhm at +1 %%; every off FET on the return on the doubling at %.2f C, ASSUMED)\n" % T_SITE)
    w("   L4-E11 20c (RECORD): board A reads DOCK_EN_OUT powered from %.3f V at least, the return closed over %.2f V at most; \"a trigger there stops a\n"
      % (R["out_pw_lo"], R["ret_closed"]))
    w("     dead pack's precharge\". The return rises with DOCK_EN_OUT (it is DOCK_EN_OUT less a constant drop, scaled), so a ramp is never read\n")
    w("     held exactly when the return is over %.2f V at DOCK_EN_OUT %.3f V: one corner bounds every instant of the ramp\n" % (R["ret_closed"], R["out_pw_lo"]))
    w("   the sinks: U48's SENSE1 %.2f uA (RECORD 20c); board A's Q44 and board P's Q107 over Q108 (2N7002s, drains on the return) %.2f uA each;\n"
      % (sense1 * 1e6, n7(T_SITE) * 1e6))
    w("     the first inverter Q103's gate at its printed IGSS %.2f uA (%.2f uA if it doubled too): %.2f uA (%.2f uA) before the shunt   l9stk %.2f (%.2f)\n"
      % (N7["igss"] * 1e6, n7(T_SITE) * 1e6, others * 1e6, others_all * 1e6, L["others"], L["others_all"]))
    w("   the shunt Q60, a 2N7002 at %.2f C: %.2f uA; in all %.2f uA (%.2f uA all doubled)                                     l9stk %.2f (%.2f)\n"
      % (T_SITE, leak * 1e6, sinks * 1e6, sinks_all * 1e6, L["sinks"], L["sinks_all"]))
    w("   the allowance with the pair at +1 %%: %.2f uA                                                                         l9stk %.2f\n" % (alw * 1e6, L["allow"]))
    w("   the return at DOCK_EN_OUT %.3f V: %.3f V (%.3f V all doubled) against %.2f V: %s                                l9stk %.3f (%.3f)\n"
      % (R["out_pw_lo"], ret, ret_all, R["ret_closed"], "HOLDS" if ret_all >= R["ret_closed"] else "FAILS", L["ret"], L["ret_all"]))
    w("   the most favourable corner (DOCK_EN_OUT %.3f V, every part nominal): %.3f V, over the held reading's %.4f V\n" % (R["out_pw_hi"], fav, R["ret_held"]))
    w("   the shunt's site may run to %.1f C (%.1f C with every FET on the return at one temperature)                                l9stk %.1f (%.1f)\n"
      % (site, site_one, L["site"], L["site_one"]))
    w("   for comparison, round 4's AO3400A at the same site (%.1f uA): the return %.3f V: FAILS (L8P-F08, round 7)\n" % (ao * 1e6, ret_ao))

    # the gate network's drive (section 5 prints it): the 2N7002's on-resistance bound in section 4 scales to it
    k = D["rpd"] / (D["rg"] + D["rpd"])
    rth = D["rg"] * D["rpd"] / (D["rg"] + D["rpd"])
    voh = 5.0 * (1 - S["acc_out"]) - S["voh_drop"]
    g_on = voh * k - N7["igss"] * rth

    # ------------------------------------------------------------------ 4. the loop's four readings
    def readings(rf_nom):
        r_p, r_m = rf_nom * (1 + TOL), rf_nom * (1 - TOL)
        gates = [G.closed(v, GUARD_ALLOW, sinks, r6p, r_p, r7m, R["load_out"])[1] for v in (V_HELD, V_LOW, V_HIGH)]
        g_max = G.closed(V_CLAMP, 0.0, 0.0, r6m, r_m, r7p, 1e18)[1]
        held = G.held(V_HELD, GUARD_ALLOW, r6p, r_m, R["load_out"])
        i_t = V_CLAMP / (r6m + r_m)
        rds = N7["r5"] * (5.0 - N7["vth"][1]) / (g_on - N7["vth"][1]) * HOT_RDS
        reg_c = bisect(lambda v: G.closed(v, GUARD_ALLOW, sinks, r6p, r_p, r7m, R["load_out"])[0] >= 6.0, 1.0, V_CLAMP)
        reg_t = bisect(lambda v: G.held(v, GUARD_ALLOW, r6p, r_m, R["load_out"]) >= 6.0, 1.0, 60.0)
        bands = {v: (G.held(v, GUARD_ALLOW, r6p, r_m, R["load_out"]), G.held(v, 0.0, r6m, r_p, R["load_out"])) for v in (V_HELD, V_LOW, V_HIGH)}
        alw_ = allowance(R["out_pw_lo"], R["ret_closed"], r_p, r7m)
        return dict(gates=gates, g_max=g_max, held=held, i_t=i_t, rds=rds, ret_trip=i_t * rds, rds_need=min(R["ret_held"], N7["vth"][0]) / i_t,
                    reg_c=reg_c, reg_t=reg_t, bands=bands, allow=alw_)
    RI, R1 = readings(rf), readings(rf / 2.0)
    w("\n4. THE LOOP'S FOUR READINGS (DERIVED; R106 10 kOhm, R107 22 kOhm, the pair, each at 1 %% at its worse sign; board A's %.0f kOhm and the guard's\n" % (R["load_out"] / 1e3))
    w("   30 uA on DOCK_EN_OUT; the full count on the return; the first inverter's gate PRINTED 1.0 to 2.5 V, VGS 20 V)\n")
    for lab, X, key in (("C4, the pair intact", RI, "intact"), ("C4, one of the pair shorted", R1, "one")):
        Lx = L[key]
        w("   %s:\n" % lab)
        w("     (a) on: the gate closed at least %.2f / %.2f / %.2f V at 7.6 / 10.6 / 16.8 V, over 2.5 V; at most %.2f V at the 29.2 V clamp, under 20 V   l9stk %.2f / %.2f / %.2f\n"
          % (X["gates"][0], X["gates"][1], X["gates"][2], X["g_max"], Lx["gates"][0], Lx["gates"][1], Lx["gates"][2]))
        w("     (b) held at 7.6 V (board P's detector or Q44): DOCK_EN_OUT %.2f V, over 1.981 V: read powered                                     l9stk %.2f\n" % (X["held"], Lx["held"]))
        w("     (c) tripped: %.2f mA through the shunt at the clamp, the return %.2f mV on the ASSUMED %.1f ohm (needed: at most %.0f ohm)                l9stk %.2f mV\n"
          % (X["i_t"] * 1e3, X["ret_trip"] * 1e3, X["rds"], X["rds_need"], Lx["ret_trip"]))
        w("     (d) the regulator at its table's 6.0 V input from BRK_VIN %.2f V closed (the state that trips), %.2f V tripped                     l9stk %.2f / %.2f\n"
          % (X["reg_c"], X["reg_t"], Lx["reg_closed"], Lx["reg_trip"]))
        w("     the window's allowance %.2f uA against %.2f uA of sinks: %s\n" % (X["allow"] * 1e6, sinks_all * 1e6, "holds" if X["allow"] >= sinks_all else "FAILS"))
    w("   E-13b's tripped DOCK_EN_OUT bands (DERIVED):\n")
    bands_apart = True
    for v in (V_HELD, V_LOW, V_HIGH):
        a, b = RI["bands"][v], R1["bands"][v]
        bands_apart &= b[1] < a[0]
        la, lb = L["bands"][v]
        w("     BRK_VIN %4.1f V: intact %5.2f to %5.2f V, one shorted %5.2f to %5.2f V                                                   l9stk %.2f-%.2f, %.2f-%.2f\n"
          % (v, a[0], a[1], b[0], b[1], la[0], la[1], lb[0], lb[1]))
    w("   the midpoint TP62 (round 8's reading for E-13b (b)): the pair intact holds it within 1 % of the mean of DOCK_EN_OUT and the return; a short of\n")
    w("     R260 puts it on DOCK_EN_OUT, a short of R261 on the return: it names WHICH resistor is shorted, closed or tripped\n")

    # ------------------------------------------------------------------ 5. the gate network
    tau = D["cg"] * rth
    vdd_hi = 5.0 * (1 + S["acc_out"])
    t_inv = S["tstr"] + S["t_en"]
    g_inv = gate(vdd_hi, tau, k, t_inv)
    t_on = -tau * math.log(1.0 - N7["vth"][1] / (voh * k))
    g_off = S["vol"] * k + N7["igss"] * rth
    # at the parts' tolerances: the least time constant for the before-tEN side, the most for the trip side (1 % resistors, C +-10 %)
    k_lo = D["rpd"] * (1 - TOL) / (D["rg"] * (1 + TOL) + D["rpd"] * (1 - TOL))
    k_hi = D["rpd"] * (1 + TOL) / (D["rg"] * (1 - TOL) + D["rpd"] * (1 + TOL))
    tau_lo = D["cg"] * (1 - C_TOL) * (D["rg"] * (1 - TOL) * D["rpd"] * (1 - TOL)) / (D["rg"] * (1 - TOL) + D["rpd"] * (1 - TOL))
    tau_hi = D["cg"] * (1 + C_TOL) * (D["rg"] * (1 + TOL) * D["rpd"] * (1 + TOL)) / (D["rg"] * (1 + TOL) + D["rpd"] * (1 + TOL))
    g_inv_t = gate(vdd_hi, tau_lo, k_hi, t_inv)
    t_on_t = -tau_hi * math.log(1.0 - N7["vth"][1] / (voh * k_lo))
    # the slow ramp: OVERTEMP is at most VDD; before VDD passes 1.3 V the gate's source is under 1.3 V; the dwell that lifts the gate to the
    # least threshold with OVERTEMP held at 1.3 V (then tEN's 2.3 ms at VDD, which a slow ramp keeps near 1.3 V)
    dwell = -tau * math.log(1.0 - N7["vth"][0] / (VDD_LOW_PR * k))
    dwell_t = -tau_lo * math.log(1.0 - N7["vth"][0] / (VDD_LOW_PR * k_hi))
    w("\n5. THE GATE NETWORK AGAINST THE SWITCH'S UNPRINTED OUTPUT BEFORE tEN (DERIVED; R262 %.0f kOhm, C260 %.1f uF, R263 %.1f MOhm as drawn)\n"
      % (D["rg"] / 1e3, D["cg"] * 1e6, D["rpd"] / 1e6))
    w("   nominal: %.1f ms, a divider of %.3f; OVERTEMP taken at VDD's %.2f V through the regulator's %.1f ms start and tEN's %.1f ms: the gate %.3f V;\n"
      % (tau * 1e3, k, vdd_hi, S["tstr"] * 1e3, S["t_en"] * 1e3, g_inv))
    w("     a trip: the drive %.2f V (VOH at least %.2f V, the gate's IGSS through %.1f kOhm), 2.5 V in %.1f ms; off: %.3f V             l9stk %.3f V, %.1f ms, %.2f V, %.3f V\n"
      % (g_on, voh, rth / 1e3, t_on * 1e3, g_off, L["g_inv"], L["t_on"], L["g_on"], L["g_off"]))
    w("   at the parts' tolerances (resistors 1 %%, C260 +-%.0f %%, ASSUMED; X7R's fall under 5 V of bias NOT HELD, Layer 6's on the chosen part):\n" % (C_TOL * 100))
    w("     the least time constant %.1f ms: the gate %.3f V after the same %.1f ms (under 1 V); the most %.1f ms: 2.5 V in %.1f ms\n"
      % (tau_lo * 1e3, g_inv_t, t_inv * 1e3, tau_hi * 1e3, t_on_t * 1e3))
    w("     so record l9stk's 0.391 V and 36.0 ms are NOMINAL figures (relabelled); its inequalities hold at the tolerances\n")
    w("   the 3.8 ms premise: TI's start (1.5 ms) is printed for a stiff input and a 47 ohm load; here the input is the loop through 10 kOhm, so\n")
    w("     VDD rises over milliseconds (section 9 (f)), and OVERTEMP before tEN is at most VDD: under %.1f V until tEN starts, then %.1f ms. The\n" % (VDD_LOW_PR, S["t_en"] * 1e3))
    w("     taken-high bound (5.05 V for 3.8 ms) covers a step start; a slow ramp needs, for the gate to reach the 2N7002's least 1 V with OVERTEMP\n")
    w("     at 1.3 V, a dwell of %.1f ms nominal (%.1f ms at the tolerances) between VDD's %.3f V and 1.3 V before tEN starts: NOT a desk result (TI\n"
      % (dwell * 1e3, dwell_t * 1e3, N7["vth"][0] / k))
    w("     prints no output state before tEN and no UVLO threshold for the regulator); E-13b (b2) reads the built loop\n")

    # ------------------------------------------------------------------ 6. FM1 and FM2
    r_in = R106 * R107 / (R106 + R107)
    v_fin = V_HELD * R107 / (R106 + R107)
    per_uf = -r_in * 1e-6 * math.log(1.0 - S["vin_min"] / v_fin)
    phase = S["tstr"] + S["t_en"] + t_on
    phase_t = S["tstr"] + S["t_en"] + t_on_t
    cin_max = (hold[0] - phase) / per_uf            # uF (per_uf is seconds per uF)
    cin_max_t = (hold[0] - phase_t) / per_uf
    vdd_over = bisect(lambda v: G.closed(v, 0.0, 0.0, r6m, rfm, r7p, 1e18)[0] > S["vdd_abs"], 1.0, V_CLAMP)
    z56, z62 = Z["BZT52C5V6"], Z["BZT52C6V2"]
    w("\n6. THE TWO FAILURE MODES (DERIVED on the printed maxima; record l9stk 5b (4))\n")
    w("   FM1 with ONE resistor (C1, not drawn): each closed phase %.1f ms (start %.1f, tEN %.1f, the gate %.1f), %.2f ms per uF of the regulator's input\n"
      % (phase * 1e3, S["tstr"] * 1e3, S["t_en"] * 1e3, t_on * 1e3, per_uf * 1e3))
    w("     capacitor at 7.6 V, under the RC hold's least %.3f s below %.1f uF                                                    l9stk %.1f ms, %.2f ms, %.1f uF\n"
      % (hold[0], cin_max, L["fm1_phase"], L["fm1_per_uf"], L["fm1_cin"]))
    w("     at the gate network's tolerances: %.1f ms, below %.1f uF; the draft's C261 is %.1f uF (+-10 %%): FM1's cycle stays under the hold either way\n"
      % (phase_t * 1e3, cin_max_t, D["cin"] * 1e6))
    w("   FM1 with the PAIR (C4, drawn): one short leaves %.1f kOhm; section 4's second rows: on, held, tripped and the window all hold (allowance\n" % (rf / 2e3))
    w("     %.2f uA); tripped, DOCK_EN_OUT at least %.2f V at 7.6 V, over the regulator's %.1f V least input: it holds on its own supply\n" % (R1["allow"] * 1e6, R1["bands"][V_HELD][0], S["vin_min"]))
    w("   FM2, the regulator's pass element shorted: U60's VDD is the closed DOCK_EN_OUT, over its %.0f V absolute rating from BRK_VIN %.2f V        l9stk %.2f V\n"
      % (S["vdd_abs"], vdd_over, L["fm2_from"]))
    w("     (the whole service); its state then NOT PRINTED. The clamps of the kit's zener sheet (Diodes DS18004 Rev 38, PRINTED): BZT52C5V6 %.1f to %.1f V\n"
      % (z56["vz"][0], z56["vz"][1]))
    w("     at %.0f mA, IR %.1f uA at %.1f V only (its draw at 5.05 V NOT PRINTED, against the 30 uA allowance); BZT52C6V2 to %.1f V, over 6 V: NOT TAKEN\n"
      % (z56["iz"] * 1e3, z56["ir"] * 1e6, z56["vr"], z62["vz"][1]))
    w("     round 8's addition: TP63 on U60's VDD lets E-13b read the regulator directly (d below): FM2 is found at the next check, latent between\n")

    # ------------------------------------------------------------------ 7. the check's verdict
    chk = [("the count and the window", abs(sinks * 1e6 - L["sinks"]) < 0.006 and abs(sinks_all * 1e6 - L["sinks_all"]) < 0.006 and abs(alw * 1e6 - L["allow"]) < 0.006
            and abs(ret - L["ret"]) < 0.0006 and abs(ret_all - L["ret_all"]) < 0.0006 and abs(site - L["site"]) < 0.06 and abs(site_one - L["site_one"]) < 0.06
            and abs(others * 1e6 - L["others"]) < 0.006 and abs(others_all * 1e6 - L["others_all"]) < 0.006 and abs(leak * 1e6 - L["leak"]) < 0.006),
           ("the loop's readings, intact", all(abs(a - b) < 0.006 for a, b in zip(RI["gates"], L["intact"]["gates"])) and abs(RI["held"] - L["intact"]["held"]) < 0.006
            and abs(RI["ret_trip"] * 1e3 - L["intact"]["ret_trip"]) < 0.006 and abs(RI["reg_c"] - L["intact"]["reg_closed"]) < 0.006 and abs(RI["reg_t"] - L["intact"]["reg_trip"]) < 0.006),
           ("the loop's readings, one shorted", all(abs(a - b) < 0.006 for a, b in zip(R1["gates"], L["one"]["gates"])) and abs(R1["held"] - L["one"]["held"]) < 0.006
            and abs(R1["ret_trip"] * 1e3 - L["one"]["ret_trip"]) < 0.006 and abs(R1["reg_c"] - L["one"]["reg_closed"]) < 0.006 and abs(R1["reg_t"] - L["one"]["reg_trip"]) < 0.006
            and abs(R1["allow"] * 1e6 - L["allow_one"]) < 0.006),
           ("the tripped bands", all(abs(RI["bands"][v][0] - L["bands"][v][0][0]) < 0.006 and abs(RI["bands"][v][1] - L["bands"][v][0][1]) < 0.006
                                     and abs(R1["bands"][v][0] - L["bands"][v][1][0]) < 0.006 and abs(R1["bands"][v][1] - L["bands"][v][1][1]) < 0.006 for v in L["bands"])),
           ("the gate network (nominal)", abs(tau * 1e3 - L["tau"]) < 0.06 and abs(k - L["div"]) < 0.0006 and abs(g_inv - L["g_inv"]) < 0.0006 and abs(t_on * 1e3 - L["t_on"]) < 0.06
            and abs(g_on - L["g_on"]) < 0.006 and abs(g_off - L["g_off"]) < 0.0006 and abs(RI["rds"] - L["rds"]) < 0.06 and abs(RI["rds_need"] - L["rds_need"]) < 0.6
            and abs(RI["i_t"] * 1e3 - L["i_trip"]) < 0.006),
           ("FM1 and FM2", abs(phase * 1e3 - L["fm1_phase"]) < 0.06 and abs(per_uf * 1e3 - L["fm1_per_uf"]) < 0.006 and abs(cin_max - L["fm1_cin"]) < 0.06
            and abs(vdd_over - L["fm2_from"]) < 0.006),
           ("the zener sheet", abs(z56["vz"][0] - L["z56"][0]) < 1e-9 and abs(z56["vz"][1] - L["z56"][1]) < 1e-9 and abs(z56["vz"][0] - vdd_hi - L["z56"][2]) < 0.006
            and abs(z56["ir"] * 1e6 - L["z56"][4]) < 1e-9 and abs(z62["vz"][1] - L["z62_hi"]) < 1e-9)]
    reproduced = all(v for _n, v in chk)
    w("\n7. THE CHECK'S VERDICT (the brief's item 1)\n")
    for name, v in chk:
        w("   %-40s %s\n" % (name, "REPRODUCED within its printed rounding" if v else "NOT REPRODUCED"))
    w("   relabelled (none moves a verdict): the gate network's %.3f V and %.1f ms are nominal (at the tolerances %.3f V and %.1f ms); \"under the\n"
      % (L["g_inv"], L["t_on"], g_inv_t, t_on_t * 1e3))
    w("     2N7002's least 1 V\" is a margin against a 25 C, 250 uA row, hot and sub-threshold NOT PRINTED; the 3.8 ms premise is a step start's (a\n")
    w("     slow ramp is E-13b (b2)); FM1's 14.1 uF falls to %.1f uF at the tolerances (C4 does not cycle on one short)\n" % cin_max_t)
    if not reproduced:
        w("   A FIGURE DOES NOT REPRODUCE: the judgement stops here, as the brief orders\n")
        sys.stdout.write("".join(out))
        return 0
    w("   CONFIRMED on the sheets: every figure of record l9stk's C4 this script reads reproduces; the draft is judged below\n")

    # ------------------------------------------------------------------ 8. the draft
    w("\n8. THE DRAFT AS DRAWN (apply_gen_sch_a_thguard.py, read for its values)\n")
    w("   the pair %s %.1f kOhm in series (%.1f kOhm); the switch %s %s; the regulator %s %s; the shunt %s %s\n"
      % (" and ".join(D["pair_refs"]), D["pair"][0] / 1e3, rf / 1e3, D["switch"][0], D["switch"][1], D["reg"][0], D["reg"][1], D["shunt"][0], D["shunt"][1]))
    w("   the gate network R262 %.0f kOhm, C260 %.1f uF, R263 %.1f MOhm; the regulator's input C261 %s, its output C262 %s; U60's C263 %s\n"
      % (D["rg"] / 1e3, D["cg"] * 1e6, D["rpd"] / 1e6, D["cap_text"]["C261"], D["cap_text"]["C262"], D["cap_text"]["C263"]))
    w("   test points %s\n" % ", ".join("%s %s" % x for x in D["tps"]))
    cout_ok = D["cout"] * (1 - C_TOL) >= 1.5e-6 and D["cout"] * (1 + C_TOL) <= 47e-6
    w("   TI's output capacitor (SBVS186H 8.1.1, PRINTED): an effective 1.5 to 47 uF, ESR under 0.2 ohm: %.1f uF at -10 %% is %s 1.5 uF before its\n"
      % (D["cout"] * 1e6, "over" if cout_ok else "UNDER"))
    w("     bias; X7R at 5 V of bias on 16 V parts loses a part of that NOT HELD here: Layer 6 confirms the effective 1.5 uF on the chosen part's curve\n")
    w("   the input capacitor %.1f uF: TI's 0.1 to 2.2 uF, needed for line transients over 10 V (a docking steps DOCK_EN_OUT through 10 kOhm)\n" % (D["cin"] * 1e6))

    # ------------------------------------------------------------------ 9. C-PROT rev 1
    lo_trip, hi_trip = 130.0 - S["acc"], 130.0 + S["acc"]
    m10, m18, mc4 = lo_trip - L["j10"], lo_trip - L["j18"], lo_trip - L["c4_j"]
    g_left, g_left2 = 150.0 - hi_trip - L["lead"], 150.0 - hi_trip - L["lead2"]
    w("\n9. C-PROT rev 1 ON THE DRAFT (10 A held and 18 A for 60 s never interrupted; every series part within its limits below and above the trip;\n")
    w("   board P's FETs welded, no firmware; start at 76.25 C plus own heating; docking included; each source present or absent)\n")
    w("   (a) NO TRIP, on the switch's PRINTED limits at the case's junction readings (RECORD l9stk 15.5; the junction taken for the switch, the hot\n")
    w("       side): 10 A held %.1f C, %.1f K under %.1f C; the 18 A service read as held %.1f C, %.1f K; the gauge's condition C4 %.1f C, %.1f K\n"
      % (L["j10"], m10, lo_trip, L["j18"], m18, L["c4_j"], mc4))
    w("       the trip limit is PRINTED at VDD 5 V only: the closed loop puts the regulator at its table's input from BRK_VIN %.2f V, under the pack's\n" % RI["reg_c"])
    w("       least %.1f V, so the whole service is judged on it; the switch's own heating %.3f K (DERIVED)\n" % (V_LOW, 5.0 * S["is_max"] * S["rja"]))
    w("   (b) THE TRIP: surely tripped from %.1f C at the die; the hottest junction leads its mounting base by %.2f K on the worst split (%.2f K with two FETs\n"
      % (hi_trip, L["lead"], L["lead2"]))
    w("       carrying all): %.2f K (%.2f K) left for the gradient from each FET's mounting base to U60's die, a LAYOUT and PHYSICAL condition (E-13)\n" % (g_left, g_left2))
    w("       the delay after the die passes the trip: the gate to 2.5 V within %.1f ms at the tolerances, the breaker's turn-off %.2f ms (RECORD l9stk\n" % (t_on_t * 1e3, t_off * 1e3))
    w("       15.4): the junction's rise in that time is NOT BOUNDED here (no thermal impedance curve held by this record); E-13's heat step reads it\n")
    w("   (c) THE LOOP'S FOUR READINGS: section 4, intact and with one of the pair shorted, every one holds; the window holds on the full count\n")
    w("       (%.3f V; %.3f V all doubled) with the shunt's site free to %.1f C\n" % (ret, ret_all, site))
    # (d) sources and the precharge
    o_pre = G.closed(v_pre, GUARD_ALLOW, sinks, r6p, rfp, r7m, R["load_out"])[0]
    w("   (d) EACH SOURCE PRESENT OR ABSENT: the guard's supply is DOCK_EN_OUT, from BRK_VIN through R106: the pack's side of the breaker, whatever\n")
    w("       shore, solar or vehicle do; a source reaches BRK_VIN only back through the breaker's body diodes (a dead pack's precharge, L4-E11 20c,\n")
    w("       at most %.3f A, the FETs' copper at the air). At the precharge's floor (BRK_VIN %.2f V) DOCK_EN_OUT reads at least %.2f V: the regulator\n"
      % (i_pre, v_pre, o_pre))
    w("       in dropout, U60 at VDD under 5 V, where its trip point is NOT PRINTED (relabelled: from %.2f V to %.2f V of BRK_VIN the switch runs on less\n" % (v_pre, RI["reg_c"]))
    w("       than its printed condition); the FETs sit at the air, %.1f K under the printed no-trip limit at 5 V; E-13b (b2) reads the ramp on the unit\n" % (lo_trip - R["air"]))
    # (e) docking
    D["sinks"], D["rout"] = sinks, R["load_out"]
    S2 = dict(vreg_hi=vdd_hi, voh_drop=S["voh_drop"], is_max=S["is_max"], t_en=S["t_en"], vth_hi=N7["vth"][1])
    w("   (e) DOCKING (DERIVED on ASSUMED behaviour: the regulator passes its input once it reaches its least rated 2.7 V, TI printing no UVLO; the\n")
    w("       capacitors at +10 %; the gate network at its slowest; the enable's mating is a step of BRK_VIN through R106): a docking starts the\n")
    w("       breaker no sooner than the RC hold's least %.3f s after the enable mates (RECORD l9stk 15.4)\n" % hold[0])
    dk = {}
    for v in (V_HELD, V_LOW, V_HIGH):
        t13, t25, vdd_end = dock(v, D, S2, hot=True, cg_scale=1 + C_TOL, r_scale=1 + TOL)
        dk[v] = (t13, t25)
        w("       BRK_VIN %4.1f V: VDD passes 1.3 V at %5.1f ms; a HOT guard's gate passes 2.5 V at %5.1f ms: %s the hold's least %.3f s\n"
          % (v, t13 * 1e3, t25 * 1e3, "before" if t25 < hold[0] else "AFTER", hold[0]))
    w("       a COLD guard: the shunt's gate stays under %.3f V through the start (section 5's before-tEN bound), so a docking is never held off\n" % g_inv_t)
    w("       so a docking with the FETs over the trip is turned off before the breaker can start, from every pack voltage (7.6 V is the breaker's\n")
    w("       PORIT, under the pack's service); the guard's start and DD-7's reading of DOCK_EN_OUT at a docking are L4-E11's 20f row to restate\n")
    # (f) the ground between the boards
    w("   (f) THE GROUND BETWEEN BOARDS A AND P: Q60 pulls the return to board A's ground, as Q44 does; board P's first inverter reads it against\n")
    w("       board P's return: the tripped %.1f mV plus the ground offset between the two at the current then flowing, under %.1f V while the offset\n"
      % (RI["ret_trip"] * 1e3, N7["vth"][0]))
    w("       stays under %.3f V: the offset is the pack return's copper and contacts (record l9stk 14, C-CU rev 1), NOT BOUNDED here, the same\n" % (N7["vth"][0] - RI["ret_trip"]))
    w("       condition Q44's input-return pulse already rests on\n")
    w("   (g) EVERY SERIES PART WITHIN ITS LIMITS: the guard adds no part to the pack path; its parts on the loop: R260 and R261 carry at most %.2f mA\n"
      % (V_CLAMP / (R106 * (1 - TOL) + rfm) * 1e3))
    w("       (%.2f mW each, against the chosen 0603's rating: Layer 6's); the regulator's input at most the 29.2 V clamp against %.0f V PRINTED; Q60 at\n"
      % ((V_CLAMP / (R106 * (1 - TOL) + rfm)) ** 2 * D["pair"][0] * 1e3, S["vin_max"]))
    w("       most 17.4 V against %.0f V, its gate %.2f V against +-%.0f V; C261 at most 29.2 V against its 50 V; U61 off the pour (TJ recommended to\n" % (N7["vds"], g_on, N7["vgs"]))
    w("       %.0f C), U60 on it (TJ(MAX) %.0f C)\n" % (S["tj_rec"], S["tj_abs"]))

    # ------------------------------------------------------------------ 10. single failures
    FAIL = [
        ("U60 stuck on (OVERTEMP high)", "Q60 holds the return: the breaker stays off", "found at once (the kit does not start)"),
        ("U60 stuck off (OVERTEMP low), dead, or its VDD open", "no trip", "E-13b (a): TRIP_TEST high fails to open the breaker; (d) reads VDD; LATENT between checks"),
        ("R260 or R261 shorted (FM1 with the pair)", "7.5 kOhm left: still trips and holds on its own supply (sections 4 and 6)", "E-13b (b): the tripped band and the midpoint TP62"),
        ("R260 or R261 open", "the loop open: the breaker stays off", "found at once"),
        ("U61's pass element shorted (FM2)", "U60's VDD over its 6 V from 7.60 V; its state NOT PRINTED", "E-13b (d): VDD at TP63; LATENT between checks"),
        ("U61 open (no output: the supply open)", "U60 unpowered; R263 holds the shunt off: no trip", "E-13b (a) and (d); LATENT between checks"),
        ("C262 or C263 shorted (VDD to ground)", "U61 limits into the short and draws DOCK_EN_OUT to its dropout: the return falls, the breaker stays off", "found at once"),
        ("C261 shorted (DOCK_EN_OUT to ground)", "the loop collapses: the breaker stays off", "found at once"),
        ("C262 open", "U61 without its output capacitor: its behaviour NOT PRINTED", "E-13b (d) reads VDD's level only; LATENT"),
        ("Q60 drain to source shorted", "the return held: the breaker stays off", "found at once"),
        ("Q60 open, or R262 open, or C260 or R263 shorted", "the shunt never conducts: no trip", "E-13b (a); LATENT between checks"),
        ("C260 open, or R262 shorted", "the gate filter gone: the before-tEN half of the window rests on TI's description alone", "E-13b (b2); LATENT"),
        ("R263 open", "no effect while U60 is powered (its push-pull holds the gate); undocked the gate floats on C260", "LATENT, no service effect named"),
        ("TRIP_TEST lifted (contamination, a probe)", "the guard trips: the breaker off", "found at once"),
    ]
    w("\n10. EACH SINGLE FAILURE OF THE NEW PARTS (INFERRED from the circuit as drawn; the brief's five first)\n")
    for a, b, c in FAIL:
        w("   %-52s %-112s %s\n" % (a, b, c))
    w("   so: none disables the breaker's own limit or opens the pack path; a failure that removes the guard is found by E-13b (a), (b), (b2) or (d)\n")
    w("   and is LATENT between checks, the battery FETs' junction limit then resting on E-1's bar (G3's state), as record l9stk names it\n")

    # ------------------------------------------------------------------ 11. verdict and E-13b
    holds = (reproduced and m10 > 0 and m18 > 0 and mc4 > 0 and ret_all >= R["ret_closed"] and all(g > N7["vth"][1] for g in RI["gates"] + R1["gates"])
             and RI["held"] > R["out_pw_hi"] and R1["held"] > R["out_pw_hi"] and RI["ret_trip"] < min(R["ret_held"], N7["vth"][0])
             and R1["ret_trip"] < min(R["ret_held"], N7["vth"][0]) and RI["reg_c"] < V_LOW and all(dk[v][1] < hold[0] for v in dk) and cout_ok)
    w("\n11. VERDICT, WHAT STAYS OPEN, AND E-13b\n")
    w("   the check (item 1): C4 CONFIRMED on the makers' sheets, with the relabellings of sections 2, 5 and 9 (d); no figure fails to reproduce\n")
    w("   the judgement (item 3) on C-PROT rev 1: %s on the desk: the no-trip side on the switch's printed limits (%.1f, %.1f and %.1f K), the trip\n"
      % ("HOLDS" if holds else "DOES NOT HOLD", m10, m18, mc4))
    w("     side within the %.2f K gradient budget (a layout and physical condition), the four readings, the window on the full count, the docking start\n" % g_left)
    w("   OPEN, and not closable on the desk: E-13 (the gradient from each FET's mounting base to U60, the heat step's lag); E-13b (b2) (the state\n")
    w("     before tEN in a slow ramp, the switch under 5 V in a precharge); the ground offset of (f); X7R's bias at C262 and C260 (Layer 6); the\n")
    w("     land (TI's NGF0006A, 2.20 x 2.50 mm, drawn on a 2 x 2 mm WSON-6 stand-in); FM2 latent between checks; the independent check of this round\n")
    w("   E-13b at commissioning and at each service (record l9stk 15.9's (a), (b), (b2) and (c), with round 8's (b) midpoint and (d)):\n")
    w("     (a) TRIP_TEST (TP60) tied to VDD (TP63) opens the breaker (board P's TP104 low); released, it restarts after the RC hold\n")
    w("     (b) DOCK_EN_OUT read tripped within its band by BRK_VIN (section 4); TP62 at the mean of DOCK_EN_OUT and the return within 1 %\n")
    w("     (b2) the loop ramped slowly with the guard cold: the return never under %.2f V while DOCK_EN_OUT is over %.3f V\n" % (R["ret_closed"], R["out_pw_lo"]))
    w("     (c) VTEMP (TP61) with TRIP_TEST high reads VTRIP, %.3f V for the 130 C preset (SNIS144G Table 1, gain 4)\n" % S["vtrip130_g4"])
    w("     (d) VDD (TP63) reads %.2f to %.2f V with the loop closed at BRK_VIN over %.2f V (a shorted or open regulator; TI's +-1 %% is printed at\n"
      % (5.0 * (1 - S["acc_out"]), vdd_hi, RI["reg_c"]))
    w("         1 mA of load, ASSUMED at the switch's microamps)\n")
    w("   L8P-F07 and L8P-F08 stay OPEN until an independent check has read this round (the brief); a negative check of C4 ends that loop\n")

    # ------------------------------------------------------------------ 12. predicates
    preds = [
        ("the check: every figure of record l9stk's C4 read here reproduces within its printed rounding", reproduced),
        ("the 2N7002 prints its on-resistance at VGS 5 V and 10 V only, its leakage and threshold at 25 C only", N7["r5"] == 7.0 and N7["r10"] == 5.0),
        ("the window holds as a ramp's reading on the full count, also with Q103's gate doubled", ret_all >= R["ret_closed"]),
        ("round 4's AO3400A at the same site fails the same window (L8P-F08)", ret_ao < R["ret_closed"]),
        ("the four readings hold intact and with one of the pair shorted", all(g > N7["vth"][1] for g in RI["gates"] + R1["gates"]) and RI["g_max"] < N7["vgs"]
         and R1["g_max"] < N7["vgs"] and RI["held"] > R["out_pw_hi"] and R1["held"] > R["out_pw_hi"] and RI["ret_trip"] < min(R["ret_held"], N7["vth"][0])
         and R1["ret_trip"] < min(R["ret_held"], N7["vth"][0])),
        ("E-13b's tripped bands tell a shorted resistor of the pair from the intact pair", bands_apart),
        ("the gate stays under 1 V through the start and tEN at the tolerances, and passes 2.5 V within 0.1 s of a trip", g_inv_t < N7["vth"][0] and t_on_t < 0.1),
        ("FM1's single-resistor cycle stays under the hold with the draft's input capacitor, at the tolerances", D["cin"] * (1 + C_TOL) < cin_max_t * 1e-6),
        ("a shorted regulator puts over 6 V on the switch from the pack's least service voltage (FM2)", vdd_over < V_LOW),
        ("the no-trip side is printed at 10 A, in the 18 A service and at condition C4", m10 > 0 and m18 > 0 and mc4 > 0),
        ("the trip side leaves the gradient record l9stk prints", abs(g_left - L["grad"]) < 0.006 and abs(g_left2 - L["grad2"]) < 0.006),
        ("a hot docking reaches the shunt before the RC hold's least start at 7.6, 10.6 and 16.8 V", all(dk[v][1] < hold[0] for v in dk)),
        ("the draft's output capacitor at -10 % is inside TI's 1.5 to 47 uF before its bias", cout_ok),
        ("record l9stk's acceptance (b) names seven mutations", len(L["mutations"]) == 7),
        ("C-PROT rev 1 holds on the desk for the draft (the physical conditions apart)", holds),
    ]
    w("\n12. PREDICATES\n")
    for text, val in preds:
        w("   %-128s %s\n" % (text, "yes" if val else "NO"))
    sys.stdout.write("".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
