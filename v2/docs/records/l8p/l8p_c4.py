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
  10b. round 9 (V6-m7; the owner's part 22 item A): the three failures the table missed, each with its failed path, the function lost,
     the requirements searched for a permitted latent state (none), the detection left, the interval, the response and the exposure;
  10c. round 9: the correction drafted (apply_gen_sch_a_thgfs.py) judged on C-PROT rev 1 on its own values, composed in L4-E9's order
     after this record's drafts, read by check_l8p_fs.py and L4-E11's check_dd7_netlist.py, mutated seven ways;
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
THGFS = os.path.join(HERE, "apply_gen_sch_a_thgfs.py")      # round 9: the fail-safe delta (the owner's part 22 item A, V6-m7)
REQS = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_requirements.yaml")
ENVELOPE = os.path.join(ROOT, "v2", "docs", "OPERATING-ENVELOPE.md")
PLAN = os.path.join(ROOT, "v2", "docs", "EXECUTION-PLAN.md")
DD7_CHECK = os.path.join(ROOT, "v2", "docs", "records", "l4e11", "check_dd7_netlist.py")
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
FS_ALLOW_COLD, FS_ALLOW_TRIP = 40e-6, 50e-6    # round 9: the guard's draw on DOCK_EN_OUT as the delta restates it (a prerequisite, 10c)
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
    m = need(pg, r"place is two %s kOhm 1 %% in series" % N, "l9stk 15.9: the pair's value")
    pr = float(m.group(1)) * 1e3
    m2 = need(pg, r"\*\*The gate network sized here \(SESSION\):\*\* %s kOhm from OVERTEMP, %s uF and %s MOhm to ground" % (N, N, N), "l9stk 15.9: the gate network")
    L["c4vals"] = dict(pair=(pr, pr), rg=float(m2.group(1)) * 1e3, cg=float(m2.group(2)) * 1e-6, rpd=float(m2.group(3)) * 1e6)
    m = need(pg, r"- Mutations: (.*?)\n- \*\*\(c\)", "l9stk 15.9 (b): the mutations", re.M | re.S)
    L["mutations"] = [x.strip() for x in re.split(r";", " ".join(m.group(1).split())) if x.strip()]
    return L


def read_2n7002():
    t = pdftext(G.N7002)
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
    t = pdftext(BZT)
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


def dock(v, D, S, hot=True, cg_scale=1.0, r_scale=1.0, uvlo=2.7, dt=2e-6, tmax=0.4, leak=0.0, i_out=0.0):
    """The docking start with the drawn capacitors (DERIVED on ASSUMED behaviour: the regulator passes its input to its output once
    the input reaches its least rated 2.7 V, TI printing no UVLO threshold, with no dropout at microamps, through a 50 ohm stand-in
    for its pass element; the switch's outputs enabled tEN after VDD passes 1.3 V; OVERTEMP then at VDD - 0.2 V if hot): the time
    VDD passes 1.3 V and the time the shunt's gate passes the 2N7002's highest threshold. Round 9: leak, a constant current off the
    gate (the cold clamp's off leakage and Q60's IGSS on the delta), i_out a constant draw on DOCK_EN_OUT (path 2's shunt's off
    leakage on the delta); both zero for round 8's draft."""
    r6, rf, r7 = R106 * (1 + TOL), D["rf"] * (1 + TOL), R107 * (1 - TOL)
    rg, rpd, cg = D["rg"] * r_scale, D["rpd"] * r_scale, D["cg"] * cg_scale
    cin, cv = D["cin"] * (1 + C_TOL), (D["cout"] + D["cvdd"]) * (1 + C_TOL)
    out = vdd = g = t = 0.0
    t13 = t25 = None
    ten = None
    while t < tmax:
        ret = max(0.0, (out / rf - D["sinks"]) / (1.0 / rf + 1.0 / r7))
        i_in = (v - out) / r6 - out / D["rout"] - (out - ret) / rf - (i_out if out > 0.0 else 0.0)
        i_reg = (min(out, S["vreg_hi"]) - vdd) / 50.0 if out >= uvlo and vdd < min(out, S["vreg_hi"]) else 0.0
        vot = max(0.0, vdd - S["voh_drop"]) if (hot and ten is not None and t >= ten) else 0.0
        out += (i_in - i_reg) / cin * dt
        vdd += (i_reg - (S["is_max"] if vdd > 0.5 else 0.0) - max(0.0, (vot - g) / rg)) / cv * dt
        g = max(0.0, g + ((vot - g) / rg - g / rpd - leak) / cg * dt)
        if t13 is None and vdd >= VDD_LOW_PR:
            t13, ten = t, t + S["t_en"]
        if t25 is None and g >= S["vth_hi"]:
            t25 = t
        t += dt
    return t13, t25, vdd


def read_fs():
    """Round 9: the fail-safe delta's values, read from apply_gen_sch_a_thgfs.py (never typed here)."""
    sp = importlib.util.spec_from_file_location("l8p_thgfs_values", THGFS)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    g, g2, c = dict(m.GATE), dict(m.GATE2), dict(m.CAPS)
    return dict(clamp=m.CLAMP, pullup=tuple(ohms(v) for _r, v in m.PULLUP), pullup_refs=tuple(r for r, _v in m.PULLUP), switch2=m.SWITCH2,
                reg2=m.REG2, shunt2=m.SHUNT2, rg=ohms(g["R262"]), cg=farads(g["C260"]), rpd=ohms(g["R263"]), rg2=ohms(g2["R270"]),
                cg2=farads(g2["C272"]), rpd2=ohms(g2["R271"]), cin=(farads(c["C261"]), farads(c["C268"])), cout=farads(c["C262"]),
                cvdd=farads(c["C263"]), cin2=farads(c["C270"]), cout2=farads(c["C271"]), caps=c, gate=g, gate2=g2, tps=m.TPS)


def read_lm26lv_od():
    """The LM26LV's open-drain row (SNIS144G 6.6): IOH at TA 30 C and 150 C, and the VOL row at VDD 3.3 V or more."""
    t = pdftext(G.LM26LV)
    m = need(t, r"Logic High output leakage\s+TA = 30°C\s+%s\s+%s\s*\nIOH.*?\n\s+current \(3\)\s+TA = 150°C\s+%s\s+%s" % (N, N, N, N),
             "LM26LV: the open drain's IOH", re.M | re.S)
    S = {"ioh30": float(m.group(2)) * 1e-6, "ioh150": float(m.group(4)) * 1e-6}
    S["vol"] = float(need(t, r"VDD ≥ 3\.3 V, Source ≤ 730 µA\s+%s" % N, "LM26LV: VOL at 730 uA").group(1))
    return S


def read_requirements():
    """Round 9 (the owner's part 22 item A): what the approved requirements say about a latent state of a protective function,
    searched in their own files rather than recalled."""
    Q = {}
    y = open(REQS, encoding="utf-8").read()
    Q["n_req"] = len(re.findall(r"^  - id: REQ-\d+", y, re.M))
    Q["latent"] = len(re.findall(r"latent|proof.test|test interval|diagnostic coverage", y, re.I))
    Q["req044"] = need(y, r"- id: REQ-044\n(?:    .*\n)*?    statement: >-\n\s+(The cell block's protection does not rest on software alone)", "REQ-044").group(1)
    Q["req045"] = need(y, r"- id: REQ-045\n(?:    .*\n)*?    statement: >-\n\s+(From the cells to every load, the maximum fault current is bounded at each stage)",
                       "REQ-045").group(1)
    e = open(ENVELOPE, encoding="utf-8").read()
    need(e, r"\*\*Single-fault conditions the design is expected to survive\*\*", "OPERATING-ENVELOPE: the single-fault paragraph")
    need(e, r"\*\*No fault tree has been drawn and no\s+coordination study exists\*\*", "OPERATING-ENVELOPE: no fault tree")
    need(e, r"the service life is TBD for prototype 1", "OPERATING-ENVELOPE: the service life")
    Q["interval"] = len(re.findall(r"service interval|maintenance interval|between services", e + y, re.I))
    pl = open(PLAN, encoding="utf-8").read()
    need(pl, r"^\| C-PROT rev 1 \|.*every series part within its limits below and above the trip", "EXECUTION-PLAN: C-PROT rev 1")
    return Q


def read_unguarded():
    """RECORD l9stk 15.4 (its protection output, copied): the breaker's current limit and the held current at which the battery FETs
    reach 150 C without any guard."""
    po = open(PROT_OUT, encoding="utf-8").read()
    m = need(po, r"150 C held at %s A from the \+70 C line and %s A from 76\.25 C" % (N, N), "l9stk protection: the unguarded 150 C current")
    U = {"i70": float(m.group(1)), "i76": float(m.group(2))}
    m = need(po, r"current limit %s / %s / %s A" % (N, N, N), "l9stk protection: the current limit")
    U["lim"] = tuple(float(m.group(k)) for k in (1, 2, 3))
    return U


# Round 9: the mutations of the composed board A with the delta, each read on check_l8p_fs's THG group
FS_MUTATIONS = (
    ("the clamp as one FET (Q63 gone, Q62's source on the ground)", [("drop", "Q63"), ("move", "Q62", "2", "GND")]),
    ("the pull-up as one resistor (R269 gone, R268 onto THG_ODN)", [("drop", "R269"), ("move", "R268", "2", "THG_ODN")]),
    ("path 2's supply from DOCK_EN_OUT", [("move", "U63", "1", "DOCK_EN_OUT")]),
    ("path 2's shunt on the return", [("move", "Q61", "3", "DOCK_EN_RET")]),
    ("path 2's switch on path 1's supply", [("move", "U62", "4", "THG_VDD")]),
    ("U61's input as one capacitor (C268 gone)", [("drop", "C268")]),
    ("path 2's gate capacitor removed", [("drop", "C272")]),
)


def compose_fs():
    """Round 9: board A composed in L4-E9's order with this record's drafts, then the delta; the delta's refusals; the netlist read by
    check_l8p_netlist (THG with checks_fs) and L4-E11's check_dd7_netlist; the mutations. Scratch only, removed after."""
    import shutil
    import tempfile
    import l8p_drafts as LD
    import check_l8p_netlist as CHK
    import check_l8p_fs as FSC
    sp = importlib.util.spec_from_file_location("l8p_c4_dd7", DD7_CHECK)
    DD7 = importlib.util.module_from_spec(sp); sp.loader.exec_module(DD7)
    d = tempfile.mkdtemp(prefix="l8p_c4_fs_")
    X = {}
    try:
        _p0, res0 = LD.compose("a", LD.order("a", "without") + [THGFS], d, "fs0")
        X["without"] = res0[-1][1] if res0 else "nothing composed"
        p, res = LD.compose("a", LD.order("a", "fwd") + [THGFS], d, "fs")
        X["res"] = res
        X["n_seq"] = len(res)
        rc, net, _table = LD.netlist_text("a", p, d, "fs")
        X["gen_rc"] = rc
        if rc == 0:
            raw = open(net, "rb").read()
            nl = CHK.read_netlist(raw)
            X["parts"] = len(nl["comps"])
            ca = FSC.judge(nl)
            X["en"], X["thg"] = ca["EN"], ca["THG"]
            X["round8"] = CHK.checks_a(nl)["THG"][0]
            X["dd7"] = DD7.judge(raw)[0]
            X["mut"] = []
            for i, (lab, ops) in enumerate(FS_MUTATIONS):
                q = LD.mutate_ops(net, d, "fsm%d" % i, ops)
                v, why = FSC.judge(CHK.read_netlist(open(q, "rb").read()))["THG"]
                X["mut"].append((lab, v, why[0] if why else ""))
        rc2, msg2 = LD.run(THGFS, p, "a")
        X["twice"] = "refused" if rc2 == 3 and "already applied" in msg2 else "NOT REFUSED (%d: %s)" % (rc2, msg2)
        r = subprocess.run([sys.executable, "-B", THGFS, os.path.join(ROOT, "v2", "ecad", "tools", "gen_sch_a.py"), "--write"], capture_output=True)
        X["tree"] = "refused (NOT RELEASED)" if r.returncode == 3 and b"NOT RELEASED" in r.stderr else "NOT REFUSED (%d)" % r.returncode
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return X


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
    pre = open(os.path.join(HERE, "inputs", "l4e11-section20c-ecb598c5.md"), encoding="utf-8").read()
    v_pre = float(need(pre, r"At the precharge's floor \(BRK_VIN %s V" % N, "L4-E11 20c: the precharge's floor").group(1))
    i_pre = float(need(pre, r"a back-fed precharge\s+carries at most %s A" % N, "L4-E11 20c: the precharge's current", re.M | re.S).group(1))

    out = []
    w = out.append
    w("l8p_c4: record l9stk's guard selection C4 CHECKED on the makers' sheets, then its draft JUDGED on case row C-PROT rev 1 (record l8p round 8,\n")
    w("MESHSAT-1357, 5 October 2026). Desk arithmetic on the makers' sheets, the records' copies and the draft's own values; nothing was built, bought\n")
    w("or measured. LABELS: PRINTED a maker's printed limit; TYPICAL; ASSUMED; DERIVED this script's arithmetic; RECORD another record's figure.\n\n")
    w("0. PINS (sha256/16)\n")
    for p in (L9_OUT5, L9_PAGE5, PROT_OUT, os.path.join(HERE, "inputs", "l4e11-section20c-ecb598c5.md"), G.LM26LV, G.TPS709, G.N7002, G.AO3400A, BZT,
              G.LM5069, DRAFT, os.path.join(HERE, "l8p_guard.py"), THGFS, os.path.join(HERE, "check_l8p_fs.py"), DD7_CHECK,
              os.path.abspath(__file__)) + tuple(os.path.join(ROOT, t) for t, _h, _held in G.PT.inputs(ROOT, PDFTEXT)):
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

    # ------------------------------------------------------------------ the figures, for C4 as record l9stk states it (sections 3 to 7) and for the
    # draft's own values (section 9): one function, so the judgement is the check's arithmetic on what is drawn
    def figures(V):
        F = {}
        n7 = lambda t: N7["idss"] * 2.0 ** ((t - 25.0) / DOUBLING)
        F["n7"] = n7
        F["sense1"] = sense1 = R["load_ret"]
        F["others"] = others = sense1 + 2 * n7(T_SITE) + N7["igss"]
        F["others_all"] = others_all = sense1 + 3 * n7(T_SITE)
        # the shunt's off leakage by the part drawn (the 2N7002 unless the values name another): the window turns on it (L8P-F08)
        shunt = (V.get("shunt") or ("", "2N7002"))[1]
        F["shunt"] = shunt
        F["leak"] = leak = n7(T_SITE) if shunt.startswith("2N7002") else S["ao_idss55"] * 2.0 ** ((T_SITE - 55.0) / DOUBLING) if shunt.startswith("AO3400A") else float("inf")
        F["rf"] = rf = sum(V["pair"])
        rfp, rfm = rf * (1 + TOL), rf * (1 - TOL)
        r6p, r6m, r7p, r7m = R106 * (1 + TOL), R106 * (1 - TOL), R107 * (1 + TOL), R107 * (1 - TOL)
        F["alw"] = alw = allowance(R["out_pw_lo"], R["ret_closed"], rfp, r7m)
        F["sinks"], F["sinks_all"] = sinks, sinks_all = others + leak, others_all + leak
        F["ret"], F["ret_all"] = ret_ramp(R["out_pw_lo"], sinks, rfp, r7m), ret_ramp(R["out_pw_lo"], sinks_all, rfp, r7m)
        F["site"] = 25.0 + DOUBLING * math.log2((alw - others) / N7["idss"]) if alw > others else float("-inf")
        F["site_one"] = bisect(lambda t: sense1 + N7["igss"] + 3 * n7(t) > alw, -50.0, 250.0)
        F["fav"] = ret_ramp(R["out_pw_hi"], sinks, rf, R107)
        F["ret_ao"] = ret_ramp(R["out_pw_lo"], others + S["ao_idss55"] * 2.0 ** ((T_SITE - 55.0) / DOUBLING), rfp, r7m)
        F["ao"] = S["ao_idss55"] * 2.0 ** ((T_SITE - 55.0) / DOUBLING)
        # the gate network
        F["k"] = k = V["rpd"] / (V["rg"] + V["rpd"])
        F["rth"] = rth = V["rg"] * V["rpd"] / (V["rg"] + V["rpd"])
        F["tau"] = tau = V["cg"] * rth
        F["voh"] = voh = 5.0 * (1 - S["acc_out"]) - S["voh_drop"]
        F["vdd_hi"] = vdd_hi = 5.0 * (1 + S["acc_out"])
        F["t_inv"] = t_inv = S["tstr"] + S["t_en"]
        F["g_inv"] = gate(vdd_hi, tau, k, t_inv)
        F["g_on"] = g_on = voh * k - N7["igss"] * rth
        F["t_on"] = t_on = -tau * math.log(1.0 - N7["vth"][1] / (voh * k)) if voh * k > N7["vth"][1] else float("inf")
        F["g_off"] = S["vol"] * k + N7["igss"] * rth
        k_lo = V["rpd"] * (1 - TOL) / (V["rg"] * (1 + TOL) + V["rpd"] * (1 - TOL))
        k_hi = V["rpd"] * (1 + TOL) / (V["rg"] * (1 - TOL) + V["rpd"] * (1 + TOL))
        F["tau_lo"] = tau_lo = V["cg"] * (1 - C_TOL) * (V["rg"] * (1 - TOL) * V["rpd"] * (1 - TOL)) / (V["rg"] * (1 - TOL) + V["rpd"] * (1 - TOL))
        F["tau_hi"] = tau_hi = V["cg"] * (1 + C_TOL) * (V["rg"] * (1 + TOL) * V["rpd"] * (1 + TOL)) / (V["rg"] * (1 + TOL) + V["rpd"] * (1 + TOL))
        F["g_inv_t"] = gate(vdd_hi, tau_lo, k_hi, t_inv)
        F["t_on_t"] = -tau_hi * math.log(1.0 - N7["vth"][1] / (voh * k_lo)) if voh * k_lo > N7["vth"][1] else float("inf")
        F["k_hi"] = k_hi
        F["dwell"] = -tau * math.log(1.0 - N7["vth"][0] / (VDD_LOW_PR * k))
        F["dwell_t"] = -tau_lo * math.log(1.0 - N7["vth"][0] / (VDD_LOW_PR * k_hi))

        # the loop's four readings, the pair intact and with its smaller resistor left alone (a short of the other)
        def readings(r_nom):
            r_p, r_m = r_nom * (1 + TOL), r_nom * (1 - TOL)
            gates = [G.closed(v, GUARD_ALLOW, sinks, r6p, r_p, r7m, R["load_out"])[1] for v in (V_HELD, V_LOW, V_HIGH)]
            g_max = G.closed(V_CLAMP, 0.0, 0.0, r6m, r_m, r7p, 1e18)[1]
            held = G.held(V_HELD, GUARD_ALLOW, r6p, r_m, R["load_out"])
            i_t = V_CLAMP / (r6m + r_m)
            rds = N7["r5"] * (5.0 - N7["vth"][1]) / (g_on - N7["vth"][1]) * HOT_RDS if g_on > N7["vth"][1] else float("inf")
            reg_c = bisect(lambda v: G.closed(v, GUARD_ALLOW, sinks, r6p, r_p, r7m, R["load_out"])[0] >= 6.0, 1.0, V_CLAMP)
            reg_t = bisect(lambda v: G.held(v, GUARD_ALLOW, r6p, r_m, R["load_out"]) >= 6.0, 1.0, 60.0)
            bands = {v: (G.held(v, GUARD_ALLOW, r6p, r_m, R["load_out"]), G.held(v, 0.0, r6m, r_p, R["load_out"])) for v in (V_HELD, V_LOW, V_HIGH)}
            alw_ = allowance(R["out_pw_lo"], R["ret_closed"], r_p, r7m)
            return dict(gates=gates, g_max=g_max, held=held, i_t=i_t, rds=rds, ret_trip=i_t * rds, rds_need=min(R["ret_held"], N7["vth"][0]) / i_t,
                        reg_c=reg_c, reg_t=reg_t, bands=bands, allow=alw_)
        F["RI"], F["R1"] = RI, R1 = readings(rf), readings(min(V["pair"]))
        F["four"] = (all(g > N7["vth"][1] for g in RI["gates"] + R1["gates"]) and RI["g_max"] < N7["vgs"] and R1["g_max"] < N7["vgs"]
                     and RI["held"] > R["out_pw_hi"] and R1["held"] > R["out_pw_hi"] and RI["ret_trip"] < min(R["ret_held"], N7["vth"][0])
                     and R1["ret_trip"] < min(R["ret_held"], N7["vth"][0]))
        F["bands_apart"] = all(R1["bands"][v][1] < RI["bands"][v][0] for v in (V_HELD, V_LOW, V_HIGH))
        F["window"] = F["ret_all"] >= R["ret_closed"] and R1["allow"] >= sinks_all
        # FM1 with one resistor and FM2
        r_in = R106 * R107 / (R106 + R107)
        v_fin = V_HELD * R107 / (R106 + R107)
        F["per_uf"] = per_uf = -r_in * 1e-6 * math.log(1.0 - S["vin_min"] / v_fin)
        F["phase"], F["phase_t"] = S["tstr"] + S["t_en"] + t_on, S["tstr"] + S["t_en"] + F["t_on_t"]
        F["cin_max"], F["cin_max_t"] = (hold[0] - F["phase"]) / per_uf, (hold[0] - F["phase_t"]) / per_uf      # uF
        F["vdd_over"] = bisect(lambda v: G.closed(v, 0.0, 0.0, r6m, rfm, r7p, 1e18)[0] > S["vdd_abs"], 1.0, V_CLAMP)
        return F

    C4V = L["c4vals"]
    F = figures(C4V)
    n7, sense1 = F["n7"], F["sense1"]
    RI, R1 = F["RI"], F["R1"]

    # ------------------------------------------------------------------ 3. the count and the window
    w("\n3. THE COUNT ON THE RETURN AND L4-E11 20c's WINDOW AS A RAMP'S READING (DERIVED, on C4 as record l9stk states it: the pair %.1f + %.1f kOhm;\n"
      % (C4V["pair"][0] / 1e3, C4V["pair"][1] / 1e3))
    w("   R107 at -1 %, the pair's sum at +1 % (two resistors at their worse sign together read as one at +1 %); every off FET on the return on the\n")
    w("   doubling at %.2f C, ASSUMED)\n" % T_SITE)
    w("   L4-E11 20c (RECORD): board A reads DOCK_EN_OUT powered from %.3f V at least, the return closed over %.2f V at most; \"a trigger there stops a\n"
      % (R["out_pw_lo"], R["ret_closed"]))
    w("     dead pack's precharge\". The return rises with DOCK_EN_OUT (it is DOCK_EN_OUT less a constant drop, scaled), so a ramp is never read\n")
    w("     held exactly when the return is over %.2f V at DOCK_EN_OUT %.3f V: one corner bounds every instant of the ramp\n" % (R["ret_closed"], R["out_pw_lo"]))
    w("   the sinks (every node the composed netlists put on DOCK_EN_RET, l8p_drafts.out section 7): U48's SENSE1 %.2f uA (RECORD 20c); board A's\n" % (sense1 * 1e6))
    w("     Q44 and board P's Q107 over Q108 (2N7002s, drains on the return) %.2f uA each; the first inverter Q103's gate at its printed IGSS\n" % (n7(T_SITE) * 1e6))
    w("     %.2f uA (%.2f uA if it doubled too); test point TP104 and the loop's R107 and R261 no sink: %.2f uA (%.2f uA) before the shunt   l9stk %.2f (%.2f)\n"
      % (N7["igss"] * 1e6, n7(T_SITE) * 1e6, F["others"] * 1e6, F["others_all"] * 1e6, L["others"], L["others_all"]))
    w("   the shunt, a 2N7002 at %.2f C: %.2f uA; in all %.2f uA (%.2f uA all doubled)                                       l9stk %.2f (%.2f)\n"
      % (T_SITE, F["leak"] * 1e6, F["sinks"] * 1e6, F["sinks_all"] * 1e6, L["sinks"], L["sinks_all"]))
    w("   the allowance with the pair at +1 %%: %.2f uA                                                                         l9stk %.2f\n" % (F["alw"] * 1e6, L["allow"]))
    w("   the return at DOCK_EN_OUT %.3f V: %.3f V (%.3f V all doubled) against %.2f V: %s                                l9stk %.3f (%.3f)\n"
      % (R["out_pw_lo"], F["ret"], F["ret_all"], R["ret_closed"], "HOLDS" if F["ret_all"] >= R["ret_closed"] else "FAILS", L["ret"], L["ret_all"]))
    w("   the most favourable corner (DOCK_EN_OUT %.3f V, every part nominal): %.3f V, over the held reading's %.4f V\n" % (R["out_pw_hi"], F["fav"], R["ret_held"]))
    w("   the shunt's site may run to %.1f C (%.1f C with every FET on the return at one temperature)                                l9stk %.1f (%.1f)\n"
      % (F["site"], F["site_one"], L["site"], L["site_one"]))
    w("   for comparison, round 4's AO3400A at the same site (%.1f uA): the return %.3f V: FAILS (L8P-F08, round 7)\n" % (F["ao"] * 1e6, F["ret_ao"]))

    # ------------------------------------------------------------------ 4. the loop's four readings
    def print_readings(F_, Lref, ind=""):
        for lab, X, key in (("the pair intact", F_["RI"], "intact"), ("one of the pair shorted", F_["R1"], "one")):
            Lx = Lref[key] if Lref else None
            tail = (lambda s: s) if Lref else (lambda s: "")
            w(ind + "   %s:\n" % lab)
            w(ind + "     (a) on: the gate closed at least %.2f / %.2f / %.2f V at 7.6 / 10.6 / 16.8 V, over 2.5 V; at most %.2f V at the 29.2 V clamp, under 20 V%s\n"
              % (X["gates"][0], X["gates"][1], X["gates"][2], X["g_max"], tail("   l9stk %.2f / %.2f / %.2f" % Lx["gates"]) if Lx else ""))
            w(ind + "     (b) held at 7.6 V (board P's detector or Q44): DOCK_EN_OUT %.2f V, over 1.981 V: read powered%s\n" % (X["held"], tail("                                     l9stk %.2f" % Lx["held"]) if Lx else ""))
            w(ind + "     (c) tripped: %.2f mA through the shunt at the clamp, the return %.2f mV on the ASSUMED %.1f ohm (needed: at most %.0f ohm)%s\n"
              % (X["i_t"] * 1e3, X["ret_trip"] * 1e3, X["rds"], X["rds_need"], tail("                l9stk %.2f mV" % Lx["ret_trip"]) if Lx else ""))
            w(ind + "     (d) the regulator at its table's 6.0 V input from BRK_VIN %.2f V closed (the state that trips), %.2f V tripped%s\n"
              % (X["reg_c"], X["reg_t"], tail("                     l9stk %.2f / %.2f" % (Lx["reg_closed"], Lx["reg_trip"])) if Lx else ""))
            w(ind + "     the window's allowance %.2f uA against %.2f uA of sinks: %s\n" % (X["allow"] * 1e6, F_["sinks_all"] * 1e6, "holds" if X["allow"] >= F_["sinks_all"] else "FAILS"))
    w("\n4. THE LOOP'S FOUR READINGS (DERIVED; R106 10 kOhm, R107 22 kOhm, the pair, each at 1 %% at its worse sign; board A's %.0f kOhm and the guard's\n" % (R["load_out"] / 1e3))
    w("   30 uA on DOCK_EN_OUT; the full count on the return; the first inverter's gate PRINTED 1.0 to 2.5 V, VGS 20 V)\n")
    print_readings(F, L)
    w("   E-13b's tripped DOCK_EN_OUT bands (DERIVED):\n")
    for v in (V_HELD, V_LOW, V_HIGH):
        a, b = RI["bands"][v], R1["bands"][v]
        la, lb = L["bands"][v]
        w("     BRK_VIN %4.1f V: intact %5.2f to %5.2f V, one shorted %5.2f to %5.2f V                                                   l9stk %.2f-%.2f, %.2f-%.2f\n"
          % (v, a[0], a[1], b[0], b[1], la[0], la[1], lb[0], lb[1]))
    w("   the midpoint TP62 (round 8's reading for E-13b (b)): the pair intact holds it within 1 % of the mean of DOCK_EN_OUT and the return; a short of\n")
    w("     R260 puts it on DOCK_EN_OUT, a short of R261 on the return: it names WHICH resistor is shorted, closed or tripped\n")

    # ------------------------------------------------------------------ 5. the gate network
    w("\n5. THE GATE NETWORK AGAINST THE SWITCH'S UNPRINTED OUTPUT BEFORE tEN (DERIVED; %.0f kOhm, %.1f uF, %.1f MOhm as record l9stk sizes it)\n"
      % (C4V["rg"] / 1e3, C4V["cg"] * 1e6, C4V["rpd"] / 1e6))
    w("   nominal: %.1f ms, a divider of %.3f; OVERTEMP taken at VDD's %.2f V through the regulator's %.1f ms start and tEN's %.1f ms: the gate %.3f V;\n"
      % (F["tau"] * 1e3, F["k"], F["vdd_hi"], S["tstr"] * 1e3, S["t_en"] * 1e3, F["g_inv"]))
    w("     a trip: the drive %.2f V (VOH at least %.2f V, the gate's IGSS through %.1f kOhm), 2.5 V in %.1f ms; off: %.3f V             l9stk %.3f V, %.1f ms, %.2f V, %.3f V\n"
      % (F["g_on"], F["voh"], F["rth"] / 1e3, F["t_on"] * 1e3, F["g_off"], L["g_inv"], L["t_on"], L["g_on"], L["g_off"]))
    w("   at the parts' tolerances (resistors 1 %%, the capacitor +-%.0f %%, ASSUMED; X7R's fall under 5 V of bias NOT HELD, Layer 6's on the chosen part):\n" % (C_TOL * 100))
    w("     the least time constant %.1f ms: the gate %.3f V after the same %.1f ms (under 1 V); the most %.1f ms: 2.5 V in %.1f ms\n"
      % (F["tau_lo"] * 1e3, F["g_inv_t"], F["t_inv"] * 1e3, F["tau_hi"] * 1e3, F["t_on_t"] * 1e3))
    w("     so record l9stk's 0.391 V and 36.0 ms are NOMINAL figures (relabelled); its inequalities hold at the tolerances\n")
    w("   the 3.8 ms premise: TI's start (1.5 ms) is printed for a stiff input and a 47 ohm load; here the input is the loop through 10 kOhm, so\n")
    w("     VDD rises over milliseconds (section 9 (e)), and OVERTEMP before tEN is at most VDD: under %.1f V until tEN starts, then %.1f ms. The\n" % (VDD_LOW_PR, S["t_en"] * 1e3))
    w("     taken-high bound (5.05 V for 3.8 ms) covers a step start; a slow ramp needs, for the gate to reach the 2N7002's least 1 V with OVERTEMP\n")
    w("     at 1.3 V, a dwell of %.1f ms nominal (%.1f ms at the tolerances) between VDD's %.3f V and 1.3 V before tEN starts: NOT a desk result (TI\n"
      % (F["dwell"] * 1e3, F["dwell_t"] * 1e3, N7["vth"][0] / F["k"]))
    w("     prints no output state before tEN and no UVLO threshold for the regulator); E-13b (b2) reads the built loop\n")

    # ------------------------------------------------------------------ 6. FM1 and FM2
    z56, z62 = Z["BZT52C5V6"], Z["BZT52C6V2"]
    w("\n6. THE TWO FAILURE MODES (DERIVED on the printed maxima; record l9stk 5b (4))\n")
    w("   FM1 with ONE resistor (C1, not drawn): each closed phase %.1f ms (start %.1f, tEN %.1f, the gate %.1f), %.2f ms per uF of the regulator's input\n"
      % (F["phase"] * 1e3, S["tstr"] * 1e3, S["t_en"] * 1e3, F["t_on"] * 1e3, F["per_uf"] * 1e3))
    w("     capacitor at 7.6 V, under the RC hold's least %.3f s below %.1f uF                                                    l9stk %.1f ms, %.2f ms, %.1f uF\n"
      % (hold[0], F["cin_max"], L["fm1_phase"], L["fm1_per_uf"], L["fm1_cin"]))
    w("     at the gate network's tolerances: %.1f ms, below %.1f uF\n" % (F["phase_t"] * 1e3, F["cin_max_t"]))
    w("   FM1 with the PAIR (C4): one short leaves %.1f kOhm; section 4's second rows: on, held, tripped and the window all hold (allowance\n" % (min(C4V["pair"]) / 1e3))
    w("     %.2f uA); tripped, DOCK_EN_OUT at least %.2f V at 7.6 V, over the regulator's %.1f V least input: it holds on its own supply\n" % (R1["allow"] * 1e6, R1["bands"][V_HELD][0], S["vin_min"]))
    w("   FM2, the regulator's pass element shorted: U60's VDD is the closed DOCK_EN_OUT, over its %.0f V absolute rating from BRK_VIN %.2f V        l9stk %.2f V\n"
      % (S["vdd_abs"], F["vdd_over"], L["fm2_from"]))
    w("     (the whole service); its state then NOT PRINTED. The clamps of the kit's zener sheet (Diodes DS18004 Rev 38, PRINTED): BZT52C5V6 %.1f to %.1f V\n"
      % (z56["vz"][0], z56["vz"][1]))
    w("     at %.0f mA, IR %.1f uA at %.1f V only (its draw at 5.05 V NOT PRINTED, against the 30 uA allowance); BZT52C6V2 to %.1f V, over 6 V: NOT TAKEN\n"
      % (z56["iz"] * 1e3, z56["ir"] * 1e6, z56["vr"], z62["vz"][1]))
    w("     round 8's addition: TP63 on U60's VDD lets E-13b read the regulator directly ((d) below): FM2 is found at the next check, latent between\n")

    # ------------------------------------------------------------------ 7. the check's verdict
    chk = [("the count and the window", abs(F["sinks"] * 1e6 - L["sinks"]) < 0.006 and abs(F["sinks_all"] * 1e6 - L["sinks_all"]) < 0.006
            and abs(F["alw"] * 1e6 - L["allow"]) < 0.006 and abs(F["ret"] - L["ret"]) < 0.0006 and abs(F["ret_all"] - L["ret_all"]) < 0.0006
            and abs(F["site"] - L["site"]) < 0.06 and abs(F["site_one"] - L["site_one"]) < 0.06 and abs(F["others"] * 1e6 - L["others"]) < 0.006
            and abs(F["others_all"] * 1e6 - L["others_all"]) < 0.006 and abs(F["leak"] * 1e6 - L["leak"]) < 0.006),
           ("the loop's readings, intact", all(abs(a - b) < 0.006 for a, b in zip(RI["gates"], L["intact"]["gates"])) and abs(RI["held"] - L["intact"]["held"]) < 0.006
            and abs(RI["ret_trip"] * 1e3 - L["intact"]["ret_trip"]) < 0.006 and abs(RI["reg_c"] - L["intact"]["reg_closed"]) < 0.006 and abs(RI["reg_t"] - L["intact"]["reg_trip"]) < 0.006),
           ("the loop's readings, one shorted", all(abs(a - b) < 0.006 for a, b in zip(R1["gates"], L["one"]["gates"])) and abs(R1["held"] - L["one"]["held"]) < 0.006
            and abs(R1["ret_trip"] * 1e3 - L["one"]["ret_trip"]) < 0.006 and abs(R1["reg_c"] - L["one"]["reg_closed"]) < 0.006 and abs(R1["reg_t"] - L["one"]["reg_trip"]) < 0.006
            and abs(R1["allow"] * 1e6 - L["allow_one"]) < 0.006),
           ("the tripped bands", all(abs(RI["bands"][v][0] - L["bands"][v][0][0]) < 0.006 and abs(RI["bands"][v][1] - L["bands"][v][0][1]) < 0.006
                                     and abs(R1["bands"][v][0] - L["bands"][v][1][0]) < 0.006 and abs(R1["bands"][v][1] - L["bands"][v][1][1]) < 0.006 for v in L["bands"])),
           ("the gate network (nominal)", abs(F["tau"] * 1e3 - L["tau"]) < 0.06 and abs(F["k"] - L["div"]) < 0.0006 and abs(F["g_inv"] - L["g_inv"]) < 0.0006
            and abs(F["t_on"] * 1e3 - L["t_on"]) < 0.06 and abs(F["g_on"] - L["g_on"]) < 0.006 and abs(F["g_off"] - L["g_off"]) < 0.0006
            and abs(RI["rds"] - L["rds"]) < 0.06 and abs(RI["rds_need"] - L["rds_need"]) < 0.6 and abs(RI["i_t"] * 1e3 - L["i_trip"]) < 0.006),
           ("FM1 and FM2", abs(F["phase"] * 1e3 - L["fm1_phase"]) < 0.06 and abs(F["per_uf"] * 1e3 - L["fm1_per_uf"]) < 0.006 and abs(F["cin_max"] - L["fm1_cin"]) < 0.06
            and abs(F["vdd_over"] - L["fm2_from"]) < 0.006),
           ("the zener sheet", abs(z56["vz"][0] - L["z56"][0]) < 1e-9 and abs(z56["vz"][1] - L["z56"][1]) < 1e-9 and abs(z56["vz"][0] - F["vdd_hi"] - L["z56"][2]) < 0.006
            and abs(z56["ir"] * 1e6 - L["z56"][4]) < 1e-9 and abs(z62["vz"][1] - L["z62_hi"]) < 1e-9)]
    reproduced = all(v for _n, v in chk)
    w("\n7. THE CHECK'S VERDICT (the brief's item 1)\n")
    for name, v in chk:
        w("   %-40s %s\n" % (name, "REPRODUCED within its printed rounding" if v else "NOT REPRODUCED"))
    w("   relabelled (none moves a verdict): the gate network's %.3f V and %.1f ms are nominal (at the tolerances %.3f V and %.1f ms); \"under the\n"
      % (L["g_inv"], L["t_on"], F["g_inv_t"], F["t_on_t"] * 1e3))
    w("     2N7002's least 1 V\" is a margin against a 25 C, 250 uA row, hot and sub-threshold NOT PRINTED; the 3.8 ms premise is a step start's (a\n")
    w("     slow ramp is E-13b (b2)); FM1's %.1f uF falls to %.1f uF at the tolerances (C4 does not cycle on one short)\n" % (L["fm1_cin"], F["cin_max_t"]))
    if not reproduced:
        w("   A FIGURE DOES NOT REPRODUCE: the judgement stops here, as the brief orders\n")
        sys.stdout.write("".join(out))
        return 0
    w("   CONFIRMED on the sheets: every figure of record l9stk's C4 this script reads reproduces; the draft is judged below\n")

    # ------------------------------------------------------------------ 8. the draft
    DF = figures(D)
    same = (tuple(D["pair"]) == tuple(C4V["pair"]) and D["rg"] == C4V["rg"] and D["cg"] == C4V["cg"] and D["rpd"] == C4V["rpd"]
            and D["switch"][1].startswith("LM26LVQISDX-130") and D["reg"][1].startswith("TPS70950") and D["shunt"][1] == "2N7002")
    w("\n8. THE DRAFT AS DRAWN (apply_gen_sch_a_thguard.py, read for its values; section 9 is computed on these, not on C4's)\n")
    w("   the pair %s %.1f and %.1f kOhm in series (%.1f kOhm); the switch %s %s; the regulator %s %s; the shunt %s %s\n"
      % (" and ".join(D["pair_refs"]), D["pair"][0] / 1e3, D["pair"][1] / 1e3, DF["rf"] / 1e3, D["switch"][0], D["switch"][1], D["reg"][0], D["reg"][1],
         D["shunt"][0], D["shunt"][1]))
    w("   the gate network R262 %.0f kOhm, C260 %.1f uF, R263 %.1f MOhm; the regulator's input C261 %s, its output C262 %s; U60's C263 %s\n"
      % (D["rg"] / 1e3, D["cg"] * 1e6, D["rpd"] / 1e6, D["cap_text"]["C261"], D["cap_text"]["C262"], D["cap_text"]["C263"]))
    w("   test points %s\n" % ", ".join("%s %s" % x for x in D["tps"]))
    w("   the draft draws C4's values (the pair, the switch's preset, the regulator, the shunt, the gate network): %s\n" % ("yes" if same else "NO"))
    cout_ok = D["cout"] * (1 - C_TOL) >= 1.5e-6 and D["cout"] * (1 + C_TOL) <= 47e-6
    w("   TI's output capacitor (SBVS186H 8.1.1, PRINTED): an effective 1.5 to 47 uF, ESR under 0.2 ohm: %.1f uF at -10 %% is %s 1.5 uF before its\n"
      % (D["cout"] * 1e6, "over" if cout_ok else "UNDER"))
    w("     bias; X7R at 5 V of bias on 16 V parts loses a part of that NOT HELD here: Layer 6 confirms the effective 1.5 uF on the chosen part's curve\n")
    w("   the input capacitor %.1f uF: TI's 0.1 to 2.2 uF, needed for line transients over 10 V (a docking steps DOCK_EN_OUT through 10 kOhm)\n" % (D["cin"] * 1e6))

    # ------------------------------------------------------------------ 9. C-PROT rev 1
    lo_trip, hi_trip = 130.0 - S["acc"], 130.0 + S["acc"]
    m10, m18, mc4 = lo_trip - L["j10"], lo_trip - L["j18"], lo_trip - L["c4_j"]
    g_left, g_left2 = 150.0 - hi_trip - L["lead"], 150.0 - hi_trip - L["lead2"]
    DRI, DR1 = DF["RI"], DF["R1"]
    w("\n9. C-PROT rev 1 ON THE DRAFT (10 A held and 18 A for 60 s never interrupted; every series part within its limits below and above the trip;\n")
    w("   board P's FETs welded, no firmware; start at 76.25 C plus own heating; docking included; each source present or absent)\n")
    w("   (a) NO TRIP, on the switch's PRINTED limits at the case's junction readings (RECORD l9stk 15.5; the junction taken for the switch, the hot\n")
    w("       side): 10 A held %.1f C, %.1f K under %.1f C; the 18 A service read as held %.1f C, %.1f K; the gauge's condition C4 %.1f C, %.1f K\n"
      % (L["j10"], m10, lo_trip, L["j18"], m18, L["c4_j"], mc4))
    w("       the trip limit is PRINTED at VDD 5 V only: the closed loop puts the regulator at its table's input from BRK_VIN %.2f V, under the pack's\n" % DRI["reg_c"])
    w("       least %.1f V, so the whole service is judged on it; the switch's own heating %.3f K (DERIVED)\n" % (V_LOW, 5.0 * S["is_max"] * S["rja"]))
    w("   (b) THE TRIP: surely tripped from %.1f C at the die; the hottest junction leads its mounting base by %.2f K on the worst split (%.2f K with two FETs\n"
      % (hi_trip, L["lead"], L["lead2"]))
    w("       carrying all): %.2f K (%.2f K) left for the gradient from each FET's mounting base to U60's die, a LAYOUT and PHYSICAL condition (E-13)\n" % (g_left, g_left2))
    w("       the delay after the die passes the trip: the gate to 2.5 V within %.1f ms at the tolerances, the breaker's turn-off %.2f ms (RECORD l9stk\n" % (DF["t_on_t"] * 1e3, t_off * 1e3))
    w("       15.4): the junction's rise in that time is NOT BOUNDED here (no thermal impedance curve held by this record); E-13's heat step reads it\n")
    w("   (c) THE LOOP'S FOUR READINGS on the draft's values:\n")
    print_readings(DF, None, "    ")
    w("       the window on the full count: %.3f V (%.3f V all doubled) against %.2f V, the shunt's site free to %.1f C: %s\n"
      % (DF["ret"], DF["ret_all"], R["ret_closed"], DF["site"], "holds" if DF["window"] else "FAILS"))
    w("       the gate network on the draft's values: %.3f V before tEN at the tolerances, 2.5 V within %.1f ms of a trip\n" % (DF["g_inv_t"], DF["t_on_t"] * 1e3))
    # (d) sources and the precharge
    o_pre = G.closed(v_pre, GUARD_ALLOW, DF["sinks"], R106 * (1 + TOL), DF["rf"] * (1 + TOL), R107 * (1 - TOL), R["load_out"])[0]
    w("   (d) EACH SOURCE PRESENT OR ABSENT: the guard's supply is DOCK_EN_OUT, from BRK_VIN through R106: the pack's side of the breaker, whatever\n")
    w("       shore, solar or vehicle do; a source reaches BRK_VIN only back through the breaker's body diodes (a dead pack's precharge, L4-E11 20c,\n")
    w("       at most %.3f A, the FETs' copper at the air). At the precharge's floor (BRK_VIN %.2f V) DOCK_EN_OUT reads at least %.2f V: the regulator\n"
      % (i_pre, v_pre, o_pre))
    w("       in dropout, U60 at VDD under 5 V, where its trip point is NOT PRINTED (relabelled: from %.2f V to %.2f V of BRK_VIN the switch runs on less\n" % (v_pre, DRI["reg_c"]))
    w("       than its printed condition); the FETs sit at the air, %.1f K under the printed no-trip limit at 5 V; E-13b (b2) reads the ramp on the unit\n" % (lo_trip - R["air"]))
    # (e) docking
    D["rf"], D["sinks"], D["rout"] = DF["rf"], DF["sinks"], R["load_out"]
    S2 = dict(vreg_hi=DF["vdd_hi"], voh_drop=S["voh_drop"], is_max=S["is_max"], t_en=S["t_en"], vth_hi=N7["vth"][1])
    w("   (e) DOCKING (DERIVED on ASSUMED behaviour: the regulator passes its input once it reaches its least rated 2.7 V, TI printing no UVLO; the\n")
    w("       capacitors at +10 %; the gate network at its slowest; the enable's mating is a step of BRK_VIN through R106): a docking starts the\n")
    w("       breaker no sooner than the RC hold's least %.3f s after the enable mates (RECORD l9stk 15.4)\n" % hold[0])
    dk = {}
    for v in (V_HELD, V_LOW, V_HIGH):
        t13, t25, _vdd = dock(v, D, S2, hot=True, cg_scale=1 + C_TOL, r_scale=1 + TOL)
        dk[v] = (t13, t25)
        w("       BRK_VIN %4.1f V: VDD passes 1.3 V at %5.1f ms; a HOT guard's gate passes 2.5 V at %5.1f ms: %s the hold's least %.3f s\n"
          % (v, t13 * 1e3, t25 * 1e3 if t25 else float("inf"), "before" if t25 and t25 < hold[0] else "AFTER", hold[0]))
    w("       a COLD guard: the shunt's gate stays under %.3f V through the start (section 5's before-tEN bound), so a docking is never held off\n" % DF["g_inv_t"])
    w("       so a docking with the FETs over the trip is turned off before the breaker can start, from every pack voltage (7.6 V is the breaker's\n")
    w("       PORIT, under the pack's service); the guard's start and DD-7's reading of DOCK_EN_OUT at a docking are L4-E11's 20f row to restate\n")
    # (f) the ground between the boards
    w("   (f) THE GROUND BETWEEN BOARDS A AND P: Q60 pulls the return to board A's ground, as Q44 does; board P's first inverter reads it against\n")
    w("       board P's return: the tripped %.1f mV plus the ground offset between the two at the current then flowing, under %.1f V while the offset\n"
      % (DRI["ret_trip"] * 1e3, N7["vth"][0]))
    w("       stays under %.3f V: the offset is the pack return's copper and contacts (record l9stk 14, C-CU rev 1), NOT BOUNDED here, the same\n" % (N7["vth"][0] - DRI["ret_trip"]))
    w("       condition Q44's input-return pulse already rests on\n")
    i_max = V_CLAMP / (R106 * (1 - TOL) + DF["rf"] * (1 - TOL))
    w("   (g) EVERY SERIES PART WITHIN ITS LIMITS: the guard adds no part to the pack path; its parts on the loop: R260 and R261 carry at most %.2f mA\n" % (i_max * 1e3))
    w("       (%.2f mW each, against the chosen 0603's rating: Layer 6's); the regulator's input at most the 29.2 V clamp against %.0f V PRINTED; Q60 at\n"
      % (i_max ** 2 * max(D["pair"]) * 1e3, S["vin_max"]))
    w("       most 17.4 V against %.0f V, its gate %.2f V against +-%.0f V; C261 at most 29.2 V against its 50 V; U61 off the pour (TJ recommended to\n" % (N7["vds"], DF["g_on"], N7["vgs"]))
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
        ("Q60 gate to drain shorted (round 9, V6-m7)", "cold: the window fails; tripped: no trip can be shown (10b (1))", "E-13b (a) only, the interval UNBOUNDED; the delta makes it trip (10c)"),
        ("C261 open (round 9, V6-m7)", "U61 without the input capacitor TI calls necessary for steps over 10 V (10b (2))", "nothing in service or E-13b; UNBOUNDED; the delta adds C268 (10c)"),
        ("U60's thermal pad (pin 7) open (round 9, V6-m7)", "the die coupled through its leads alone: the lag not bounded (10b (3))", "E-13's heat step once; UNBOUNDED in service; the delta adds U62 (10c)"),
    ]
    w("\n10. EACH SINGLE FAILURE OF THE NEW PARTS (INFERRED from the circuit as drawn; the brief's five first)\n")
    for a, b, c in FAIL:
        w("   %-52s %-112s %s\n" % (a, b, c))
    w("   so: none disables the breaker's own limit or opens the pack path; a failure that removes the guard is found by E-13b (a), (b), (b2) or (d)\n")
    w("   and is LATENT between checks, the battery FETs' junction limit then resting on E-1's bar (G3's state), as record l9stk names it\n")
    w("   ROUND 9 (the owner's part 22): no approved requirement permits a latent state (10b), so every row above marked LATENT is a loss of\n")
    w("   required protection with an UNBOUNDED interval, not a tolerated state: the three V6-m7 rows are corrected in draft (10c), the\n")
    w("   common-path rows stay OPEN (10c, L8P-R9-F1)\n")

    # ------------------------------------------------------------------ 10b. round 9: the three failures the table missed (V6-m7)
    rfp_, r7m_ = DF["rf"] * (1 + TOL), R107 * (1 - TOL)
    rth_ = rfp_ * r7m_ / (rfp_ + r7m_)
    rx = DF["rth"]                                  # Q60's gate on its drain: R262 to OVERTEMP (low, cold) beside R263 to ground
    gd = {}
    for lab, i_s in (("the count", DF["others"]), ("all doubled", DF["others_all"])):
        v_open = ret_ramp(R["out_pw_lo"], i_s, rfp_, r7m_)
        v = v_open * rx / (rx + rth_)
        gd[lab] = (v, v / rx, i_s + v / rx)
    alw_ = DF["alw"]
    two = DF["sinks_all"] + DF["n7"](T_SITE)        # a second shunt (a second sensing path) on the same return, every sink doubled
    two_one = DF["sinks"] + DF["n7"](T_SITE)
    Q = read_requirements()
    UG = read_unguarded()
    r6n, r7n = R106, R107
    # (1) at service, the cold short without the clamp: the network beside R107 on the return (the first inverter's reading, nominal parts)
    r7x = r7n * rx / (r7n + rx)
    ret_svc = G.closed(V_LOW, GUARD_ALLOW, DF["sinks"], r6n, DF["rf"], r7x, R["load_out"])[1]
    # (2) the closed DOCK_EN_OUT a docking steps U61's input to, and the BRK_VIN from which that step is over 10 V
    out168 = G.closed(V_HIGH, GUARD_ALLOW, DF["sinks"], r6n, DF["rf"], r7n, R["load_out"])[0]
    out292 = G.closed(V_CLAMP, GUARD_ALLOW, DF["sinks"], r6n, DF["rf"], r7n, R["load_out"])[0]
    v10 = bisect(lambda v: G.closed(v, GUARD_ALLOW, DF["sinks"], r6n, DF["rf"], r7n, R["load_out"])[0] >= 10.0, 1.0, V_CLAMP)
    w("\n10b. ROUND 9 (V6-m7; the owner's review of checkpoint 3, part 22, item A): THE THREE SINGLE FAILURES THE ROUND 8 TABLE MISSED, EACH\n")
    w("   STATED IN FULL. Round 9's first pass labelled them tolerated (L8P-D9); that label is WITHDRAWN: no requirement permits it\n")
    w("   THE REQUIREMENTS READ FOR A PERMITTED LATENT STATE (searched in their files, not recalled):\n")
    w("     v2/ecad/tools/pcb_requirements.yaml, %d requirements: \"latent\", \"proof test\", \"test interval\", \"diagnostic coverage\": %d matches\n"
      % (Q["n_req"], Q["latent"]))
    w("     REQ-044 \"%s ...\" (the cell block's gauge and secondary)\n" % Q["req044"])
    w("     REQ-045 \"%s ...\" (a protective element per stage, coordinated with\n" % Q["req045"])
    w("       what it protects): neither names a latent state, a detection interval or a coverage\n")
    w("     OPERATING-ENVELOPE section 4, \"Single-fault conditions the design is expected to survive\": the design's protections listed, no latent\n")
    w("       state admitted, and \"No fault tree has been drawn and no coordination study exists\" (PWR-003 open)\n")
    w("     C-PROT rev 1 (EXECUTION-PLAN.md): \"every series part within its limits below and above the trip\"\n")
    w("     the interval E-13b's \"each service\" rests on: NOT DEFINED (%d matches for a service or maintenance interval; the service life is TBD\n"
      % Q["interval"])
    w("       for prototype 1, OPERATING-ENVELOPE section 5). E-13b (a) is a technician's probe step (TP60 tied to TP63), run at commissioning\n")
    w("       and at a service: a docking or a power-up does not run it, so \"at start\" means once, at commissioning\n")
    w("     so NO approved requirement permits a latent state of the guard; each failure below is judged as a loss of required protection\n")
    w("   THE EXPOSURE WHILE THE GUARD IS LOST (RECORD l9stk 15.4, its protection output copied): the breaker's current limit %.2f / %.2f / %.2f A\n"
      % UG["lim"])
    w("     (least / typical / most); without any guard the battery FETs reach 150 C held at %.2f A from the 76.25 C air (%.2f A from +70 C),\n"
      % (UG["i76"], UG["i70"]))
    w("     DERIVED, FETs only: a held current from %.2f A to the breaker's own limit (up to %.2f A) puts a series part over its limit BELOW THE\n"
      % (UG["i76"], UG["lim"][2]))
    w("     TRIP, a condition C-PROT rev 1 covers; in the normal service of section 9 (a) (10 A held %.1f C, the 18 A service %.1f C, condition\n"
      % (L["j10"], L["j18"]))
    w("     C4 %.1f C) no part is over its limit, with or without the guard\n" % L["c4_j"])
    w("   (1) Q60's GATE SHORTED TO ITS DRAIN\n")
    w("     failed path: the gate network (R262 %.0f kOhm to OVERTEMP, low cold; R263 %.1f MOhm to ground) sits on the return; Q60 diode-connected\n"
      % (D["rg"] / 1e3, D["rpd"] / 1e6))
    w("     function lost: cold, at the window's corner (DOCK_EN_OUT %.3f V, the pair at +1 %%, R107 at -1 %%) the return reads %.3f V (%.3f V all\n"
      % (R["out_pw_lo"], gd["the count"][0], gd["all doubled"][0]))
    w("       doubled), %.1f uA through the network, against the %.2f V the window needs: a ramping loop can be read held and a dead pack's\n"
      % (gd["the count"][1] * 1e6, R["ret_closed"]))
    w("       precharge stopped (L4-E11 20c); tripped, the diode-connected Q60 conducts only above its own threshold (PRINTED %.1f to %.1f V at\n" % N7["vth"])
    w("       250 uA, 25 C), so it cannot be shown to pull the return under board P's first inverter's least %.1f V: the trip is LOST\n" % N7["vth"][0])
    w("     detection still working: E-13b (a) only (TRIP_TEST fails to open the breaker). In service none: at the pack's least %.1f V the return\n" % V_LOW)
    w("       with the short reads %.2f V (nominal parts), over the first inverter's 2.5 V: the loop reads closed and the kit runs\n" % ret_svc)
    w("     the maximum interval before detection: to the next E-13b, UNBOUNDED (no service interval exists); the response until then: none\n")
    w("     the exposure in that interval: none in normal service; with a held current from %.2f A to the breaker's limit the FETs pass 150 C,\n" % UG["i76"])
    w("       a prohibited temperature in a C-PROT rev 1 condition, NOT BOUNDED\n")
    w("     so a correction is required: 10c, the cold clamp (the short then trips)\n")
    w("   (2) C261 OPEN\n")
    w("     failed path: U61's only input capacitor\n")
    w("     function lost: TI SBVS186H 8.1.1, PRINTED: \"An input capacitor is necessary if line transients greater than 10 V in magnitude are\n")
    w("       anticipated\". A docking steps U61's input from 0 V to the closed DOCK_EN_OUT: %.2f V at BRK_VIN %.1f V, %.2f V at the %.1f V clamp,\n"
      % (out168, V_HIGH, out292, V_CLAMP))
    w("       over 10 V from BRK_VIN %.2f V (DERIVED, nominal parts): U61's response is then NOT PRINTED, so its output, both switches' VDD (6 V\n" % v10)
    w("       absolute), is not bounded during the step, and the guard's state after it is not printed\n")
    w("     detection: none in service and none in E-13b ((d) reads VDD's settled level, not a capacitor); the assembly's inspection only\n")
    w("     the maximum interval: UNBOUNDED (an open that develops in service, a cracked MLCC, is never looked for); the response: none\n")
    w("     the exposure: at each docking from BRK_VIN %.2f V a voltage over the switch's 6 V absolute maximum cannot be excluded (a prohibited\n" % v10)
    w("       voltage condition, NOT BOUNDED); a switch it damages or leaves low is (1)'s exposure\n")
    w("     so a correction is required: 10c, C268 beside C261\n")
    w("   (3) U60's THERMAL PAD (pin 7) OPEN\n")
    w("     failed path: the die's main thermal path to the battery FETs' pour (pin 2 still grounds it electrically)\n")
    w("     function lost: the die couples through its six leads alone. Its own heating is %.3f K with the pad and small without it, so a slow\n"
      % (5.0 * S["is_max"] * S["rja"]))
    w("       rise is followed; TI prints no thermal figure for the part without its pad, so the lag behind the pour in a rising overload is\n")
    w("       NOT BOUNDED and the trip may come after a battery FET passes 150 C (section 9 (b) leaves the junction's rise in the delay open too)\n")
    w("     detection: E-13's heat step at commissioning (the lag read through VTEMP at TP61) and an X-ray of the WSON at assembly; none in service\n")
    w("     the maximum interval: from commissioning, UNBOUNDED (a pad cracked in service by thermal fatigue is never looked for); response: none\n")
    w("     the exposure: a held current from %.2f A to the breaker's limit, or a fast-rising overload: a FET over 150 C before the trip, NOT\n" % UG["i76"])
    w("       BOUNDED\n")
    w("     so a correction is required: 10c, path 2: a second switch U62 on its own pad, with its own supply and its own shunt\n")
    w("   A SECOND SHUNT ON THE SAME RETURN (round 9's first pass, recorded): its off leakage, %.2f uA at %.2f C, makes the sinks %.2f uA on the\n"
      % (DF["n7"](T_SITE) * 1e6, T_SITE, two_one * 1e6))
    w("     count and %.2f uA all doubled against the %.2f uA allowance: L4-E11 20c's window FAILS, so the correction keeps one shunt\n" % (two * 1e6, alw_ * 1e6))
    R9 = {"gd": gd["the count"][0], "gd_all": gd["all doubled"][0], "two": two, "two_one": two_one, "alw": alw_}

    # ------------------------------------------------------------------ 10c. round 9: the correction drafted (apply_gen_sch_a_thgfs.py)
    FS = read_fs()
    OD = read_lm26lv_od()
    n7t = DF["n7"](T_SITE)
    rpu = sum(FS["pullup"])
    rpu_p, rpu_m, r_one = rpu * (1 + TOL), rpu * (1 - TOL), min(FS["pullup"]) * (1 - TOL)
    leak_pu = OD["ioh150"] + 2 * N7["igss"]                      # U60's open drain (printed IOH) and the clamp's two gates (printed IGSS)
    leak_pu_all = OD["ioh150"] + 2 * n7t                          # the gates taken at the off leakage's doubling (section 3's variant)
    draw0 = S["is_max"] + S["ignd"]                               # path 1's switch and regulator (path 2's are on VBAT)
    cold, cold_all = draw0 + leak_pu + n7t, draw0 + leak_pu_all + n7t       # Q61 off on DOCK_EN_OUT, at the doubling (ASSUMED)
    trip, trip_one = draw0 + DF["vdd_hi"] / rpu_m + n7t, draw0 + DF["vdd_hi"] / r_one + n7t
    # path 1: Q60's gate to drain short with the clamp, the clamp's gates in the held state at BRK_VIN 7.6 V
    held_c = G.held(V_HELD, FS_ALLOW_COLD, R106 * (1 + TOL), DF["rf"] * (1 - TOL), R["load_out"])
    vdd_h = min(5.0 * (1 - S["acc_out"]), held_c)
    vgs, vgs_all = vdd_h - leak_pu * rpu_p, vdd_h - leak_pu_all * rpu_p

    def rds(v):
        return N7["r5"] * (5.0 - N7["vth"][1]) / (v - N7["vth"][1]) * HOT_RDS if v > N7["vth"][1] else float("inf")
    i_cl = DRI["i_t"]
    lim_ret = min(R["ret_held"], N7["vth"][0])
    need_each = lim_ret / i_cl / 2.0
    ret_cl, ret_cl_all = i_cl * 2 * rds(vgs), i_cl * 2 * rds(vgs_all)
    v_need = N7["vth"][1] + N7["r5"] * (5.0 - N7["vth"][1]) * HOT_RDS / need_each
    gate_bound = ((vdd_h - v_need) / rpu_p - OD["ioh150"]) / 2.0
    ret_open = G.closed(V_CLAMP, 0.0, 0.0, R106 * (1 - TOL), DF["rf"] * (1 - TOL), R107 * (1 + TOL), 1e18)[1]
    # path 1's trip with the clamp's off leakage on its gate; path 2's on round 8's network alone
    rg_p, rg_m, rp_p, rp_m = FS["rg"] * (1 + TOL), FS["rg"] * (1 - TOL), FS["rpd"] * (1 + TOL), FS["rpd"] * (1 - TOL)
    k_lo = rp_m / (rg_p + rp_m)
    rth_hi = rg_p * rp_p / (rg_p + rp_p)
    tau_hi = FS["cg"] * (1 + C_TOL) * rth_hi
    leak_g = n7t + N7["igss"]                                     # the clamp off (the stack's leakage bounded by one FET's, ASSUMED) and Q60's IGSS
    fin = DF["voh"] * k_lo - leak_g * rth_hi
    t_on1 = -tau_hi * math.log(1.0 - N7["vth"][1] / fin) if fin > N7["vth"][1] else float("inf")
    g_inv1 = DF["g_inv_t"]                                        # the network is round 8's: its before-tEN bound unchanged
    r2_p, r2_m, rp2_p, rp2_m = FS["rg2"] * (1 + TOL), FS["rg2"] * (1 - TOL), FS["rpd2"] * (1 + TOL), FS["rpd2"] * (1 - TOL)
    k2_lo, k2_hi = rp2_m / (r2_p + rp2_m), rp2_p / (r2_m + rp2_p)
    rth2_hi, rth2_lo = r2_p * rp2_p / (r2_p + rp2_p), r2_m * rp2_m / (r2_m + rp2_m)
    tau2_hi, tau2_lo = FS["cg2"] * (1 + C_TOL) * rth2_hi, FS["cg2"] * (1 - C_TOL) * rth2_lo
    fin2 = DF["voh"] * k2_lo - N7["igss"] * rth2_hi
    t_on2 = -tau2_hi * math.log(1.0 - N7["vth"][1] / fin2) if fin2 > N7["vth"][1] else float("inf")
    g_inv2 = DF["vdd_hi"] * k2_hi * (1.0 - math.exp(-(S["tstr"] + S["t_en"]) / tau2_lo))
    # path 2 tripped: Q61 pulls DOCK_EN_OUT, the return follows; its on-resistance as Q60's (section 4's ASSUMED figure)
    i_q61 = V_CLAMP / (R106 * (1 - TOL))
    out_q61 = i_q61 * DRI["rds"]
    ret_q61 = out_q61 * (R107 * (1 + TOL)) / (DF["rf"] * (1 - TOL) + R107 * (1 + TOL))
    # the loop's readings at the restated allowances
    cin_fs = sum(FS["cin"])
    r_in = R106 * R107 / (R106 + R107)
    per_uf_fs = -r_in * 1e-6 * math.log(1.0 - S["vin_min"] / (V_HELD * R107 / (R106 + R107)))
    cin_max_fs = (hold[0] - (S["tstr"] + S["t_en"] + t_on1)) / per_uf_fs

    def fs_readings(r_nom):
        r_p, r_m = r_nom * (1 + TOL), r_nom * (1 - TOL)
        gates = [G.closed(v, FS_ALLOW_COLD, DF["sinks"], R106 * (1 + TOL), r_p, R107 * (1 - TOL), R["load_out"])[1] for v in (V_HELD, V_LOW, V_HIGH)]
        held = G.held(V_HELD, FS_ALLOW_TRIP, R106 * (1 + TOL), r_m, R["load_out"])
        reg_c = bisect(lambda v: G.closed(v, FS_ALLOW_COLD, DF["sinks"], R106 * (1 + TOL), r_p, R107 * (1 - TOL), R["load_out"])[0] >= 6.0, 1.0, V_CLAMP)
        return gates, held, reg_c
    FRI, FR1 = fs_readings(DF["rf"]), fs_readings(min(D["pair"]))
    # docking, path 1 (path 2's regulator is on VBAT, so its start loads no docking): the delta's capacitors, the pull-up drawn from VDD
    # from the start (the open drain's state before tEN is not printed), the clamp's leakage on the gate, Q61's on DOCK_EN_OUT
    D2 = dict(D)
    D2.update(cin=cin_fs, cout=FS["cout"], cvdd=FS["cvdd"], cg=FS["cg"], rg=FS["rg"], rpd=FS["rpd"])
    S3 = dict(S2)
    S3.update(is_max=S["is_max"] + DF["vdd_hi"] / rpu_m)
    dk_fs = {v: dock(v, D2, S3, hot=True, cg_scale=1 + C_TOL, r_scale=1 + TOL, leak=leak_g, i_out=n7t)[:2] for v in (V_HELD, V_LOW, V_HIGH)}
    # path 2 alone after a breaker start (path 1 failed; VBAT from the pack): its supply's start, tEN, its gate to 2.5 V
    t_p2 = S["tstr"] + S["t_en"] + t_on2
    X = compose_fs()
    fs_ok = (ret_cl < lim_ret and t_on1 < 0.1 and t_on2 < 0.1 and g_inv1 < N7["vth"][0] and g_inv2 < N7["vth"][0]
             and cold_all <= FS_ALLOW_COLD and trip_one <= FS_ALLOW_TRIP and ret_q61 < lim_ret and out_q61 < R["out_pw_lo"]
             and all(g > N7["vth"][1] for g in FRI[0] + FR1[0]) and FRI[1] > R["out_pw_hi"] and FR1[1] > R["out_pw_hi"] and FRI[2] < V_LOW
             and all(dk_fs[v][1] is not None and dk_fs[v][1] < hold[0] for v in dk_fs) and cin_fs * 1e6 * (1 + C_TOL) < cin_max_fs
             and min(FS["cin"]) * (1 - C_TOL) >= 0.1e-6 and cin_fs * (1 + C_TOL) <= 2.2e-6 + 1e-12 and FS["cout2"] * (1 - C_TOL) >= 1.5e-6
             and ret_open < 16.0 and t_p2 < hold[0])
    comp_ok = (X.get("gen_rc") == 0 and all(v.startswith("OK") for _n, v in X["res"]) and X.get("en", ("",))[0] == "DRAWN"
               and X.get("thg", ("",))[0] == "DRAWN" and X.get("dd7") == "DRAWN" and X.get("round8") == "FAIL"
               and all(v == "FAIL" for _l, v, _w in X.get("mut", [])) and len(X.get("mut", [])) == len(FS_MUTATIONS)
               and X["twice"] == "refused" and X["tree"].startswith("refused") and "REFUSED" in X["without"])
    w("\n10c. ROUND 9: THE CORRECTION DRAFTED, apply_gen_sch_a_thgfs.py (after apply_gen_sch_a_thguard.py), ITS VALUES READ FROM THE DRAFT AND\n")
    w("   JUDGED ON C-PROT rev 1 (labels as above; the owner's part 22 item A and the check cx45's Q5). NOT APPLIED; V6-m7 OPEN until an independent\n")
    w("   check has read it. TWO GUARD PATHS that share only the pour they sense and the loop they open:\n")
    w("   path 1, round 8's guard kept (U60, U61 from DOCK_EN_OUT, R262 %s, C260 %s, R263 %s, Q60 on DOCK_EN_RET) with a cold clamp:\n"
      % (FS["gate"]["R262"], FS["gate"]["C260"], FS["gate"]["R263"]))
    w("     %s in series from Q60's gate to ground, gated by U60's open drain (THG_ODN) pulled up by %s %.0f + %.0f kOhm;\n"
      % (" and ".join("%s %s" % c for c in FS["clamp"]), " and ".join(FS["pullup_refs"]), FS["pullup"][0] / 1e3, FS["pullup"][1] / 1e3))
    w("     U61's input C261 %s and C268 %s\n" % (FS["caps"]["C261"], FS["caps"]["C268"]))
    w("   path 2, new: %s %s on the same pour, supplied by %s %s from VBAT (C270 %s in, C271 %s out), C269 %s; its OVERTEMP through\n"
      % (FS["switch2"][0], FS["switch2"][1], FS["reg2"][0], FS["reg2"][1], FS["caps"]["C270"], FS["caps"]["C271"], FS["caps"]["C269"]))
    w("     R270 %s with C272 %s and R271 %s to %s %s from DOCK_EN_OUT to ground; %s\n"
      % (FS["gate2"]["R270"], FS["gate2"]["C272"], FS["gate2"]["R271"], FS["shunt2"][0], FS["shunt2"][1], ", ".join("%s %s" % t_ for t_ in FS["tps"])))
    w("   the rows read (PRINTED): LM26LV open drain IOH at most %.0f uA at 30 C and %.0f uA at 150 C (TI: a testing limit); the 2N7002 as section 2\n"
      % (OD["ioh30"] * 1e6, OD["ioh150"] * 1e6))
    w("   (1) Q60's GATE TO DRAIN SHORT (V6-m7) WITH THE CLAMP: cold, the return is THG_G, which Q62 and Q63 hold at ground\n")
    w("       in the held state at BRK_VIN %.1f V DOCK_EN_OUT reads %.2f V (the cold draw at %.0f uA, R106 at +1 %%, the pair at -1 %%), VDD %.2f V (the\n"
      % (V_HELD, held_c, FS_ALLOW_COLD * 1e6, vdd_h))
    w("       regulator in dropout, no drop at microamps ASSUMED); through %.1f kOhm the open drain's %.0f uA and the gates' printed %.2f uA: VGS at\n"
      % (rpu_p / 1e3, OD["ioh150"] * 1e6, 2 * N7["igss"] * 1e6))
    w("       least %.2f V; each FET %.1f ohm ASSUMED by section 4's convention against at most %.0f ohm each for the %.2f mA of the 29.2 V clamp\n"
      % (vgs, rds(vgs), need_each, i_cl * 1e3))
    w("       to leave the return under %.4f V: the return %.1f mV, HELD: the breaker off, DD-7 reads board P's own pull: the fault TRIPS, found at\n"
      % (lim_ret, ret_cl * 1e3))
    w("       once. The clamp needs each gate's leakage at most %.2f uA (PRINTED %.2f uA at 25 C, hot NOT PRINTED; a Layer 6 or bench condition):\n"
      % (gate_bound * 1e6, N7["igss"] * 1e6))
    w("       with the gates at the off leakage's doubling (%.2f uA each) VGS falls to %.2f V and the clamp is NOT shown; Q60's short then leaves\n"
      % (n7t * 1e6, vgs_all))
    w("       path 1 lost and path 2 holding the protection (2). THG_G carries the return only with this short: at most %.2f V, under C260's 16 V\n" % ret_open)
    w("   (2) THE COMMON PATH (cx45 Q5): each single failure of path 1 (U61 open or its pass element shorted, U60 dead or stuck cold or its pad\n")
    w("       open, R262 open, C260 or R263 shorted, Q60 open or its gate to drain shorted with the clamp not shown) leaves path 2, and each of path 2\n")
    w("       (U63, U62, R270, C272, R271, Q61) leaves path 1: no single failure removes the trip AT ONCE. PROVISIONAL (the recheck cx46,\n")
    w("       items 10 and 17): with path 1 lost, path 2's retries leave the junction's rise unbounded (below), and a latent first failure\n")
    w("       followed by a second removes the trip (L8P-R9-F1): C-PROT rev 1 for the guard is PROVISIONAL at every claim that rests on this\n")
    w("       path 2 tripped: Q61 pulls DOCK_EN_OUT; at the 29.2 V clamp %.2f mA through R106 at -1 %%, on Q60's ASSUMED %.1f ohm, DOCK_EN_OUT %.1f mV\n"
      % (i_q61 * 1e3, DRI["rds"], out_q61 * 1e3))
    w("       and the return %.1f mV: under board P's least %.1f V and the held reading's %.4f V: the breaker off; DOCK_EN_OUT under the powered\n"
      % (ret_q61 * 1e3, N7["vth"][0], R["ret_held"]))
    w("       reading's least %.3f V, so DD-7 reads the loop dark (no trigger, L4-E11 28). A sink on DOCK_EN_OUT does not move the return against\n"
      % R["out_pw_lo"])
    w("       DOCK_EN_OUT: L4-E11 20c's window is unchanged by path 2 (its off leakage counts in the draw, (c))\n")
    w("       path 2's gate: 2.5 V within %.1f ms of a trip at the tolerances, under 1 V before tEN (%.3f V); after a breaker start with path 1 lost\n"
      % (t_on2 * 1e3, g_inv2))
    w("       and VBAT from the pack alone, U63's start, tEN and the gate take at most %.1f ms (the regulator's printed start), under the RC hold's\n"
      % (t_p2 * 1e3))
    w("       least %.3f s; tripping opens the breaker, VBAT may fall, the gate holds on C272 and releases, and the breaker restarts no sooner than\n" % hold[0])
    w("       the hold: a relaxation in which the FETs carry current at most %.1f ms in every %.3f s or more (DERIVED; the junction's rise in each\n"
      % (t_p2 * 1e3, hold[0] + t_p2))
    w("       on-time NOT BOUNDED here, as section 9 (b)'s delay); with VBAT held up by another source, Q61 holds the loop open until the pour cools.\n")
    w("       So with path 1 lost the protection under those retries is NOT shown (cx46 10): the bounded retry-energy analysis is REMAINING\n")
    w("       ENGINEERING, and every claim resting on path 2 alone is PROVISIONAL\n")
    w("   (3) C261 OPEN (V6-m7): C268 stays, %.0f nF (%.0f nF at -10 %%), inside TI's 0.1 to 2.2 uF; the two %.2f uF (%.2f uF at +10 %%)\n"
      % (FS["cin"][1] * 1e9, FS["cin"][1] * (1 - C_TOL) * 1e9, cin_fs * 1e6, cin_fs * (1 + C_TOL) * 1e6))
    w("   (4) U60's PAD OPEN (V6-m7): path 2's U62 on its own pad trips on the same printed limits and opens the loop through Q61\n")
    w("   C-PROT rev 1 ON THE DELTA:\n")
    w("   (a) no trip: each switch on its printed limits, as section 9 (a): %.1f, %.1f and %.1f K\n" % (m10, m18, mc4))
    w("   (b) the trip: path 1's drive %.2f V x %.3f less the clamp's off leakage and Q60's IGSS, %.2f uA, through %.1f kOhm: %.2f V, 2.5 V within\n"
      % (DF["voh"], k_lo, leak_g * 1e6, rth_hi / 1e3, fin))
    w("       %.1f ms at the tolerances (round 8: %.1f ms); path 2 within %.1f ms; under 0.1 s; the gradient budget per switch (E-13)\n"
      % (t_on1 * 1e3, DF["t_on_t"] * 1e3, t_on2 * 1e3))
    w("   (c) the window: the count on the return is unchanged (the clamp sits on THG_G, path 2 on DOCK_EN_OUT): %.3f V (%.3f V all doubled)\n"
      % (DF["ret"], DF["ret_all"]))
    w("       against %.2f V: holds. The guard's draw on DOCK_EN_OUT restated (PRINTED maxima, the off leakage at the doubling): cold at most\n" % R["ret_closed"])
    w("       %.2f uA (U60 %.0f, U61 %.2f, the pull-up's leakage %.2f, Q61 off %.2f), %.2f uA with the clamp's gates doubled; path 1 tripped at\n"
      % (cold * 1e6, S["is_max"] * 1e6, S["ignd"] * 1e6, leak_pu * 1e6, n7t * 1e6, cold_all * 1e6))
    w("       most %.2f uA (the pull-up across %.1f kOhm), %.2f uA with one of its resistors shorted. Allowances taken: %.0f uA cold, %.0f uA\n"
      % (trip * 1e6, rpu_m / 1e3, trip_one * 1e6, FS_ALLOW_COLD * 1e6, FS_ALLOW_TRIP * 1e6))
    w("       tripped, against the 30 uA of Layer 5's row and record l9stk 15.9, both UNRESTATED (L8P-R9-F2: their draft texts for their owners\n")
    w("       are on page 12o; L4-E11 section 28 restates 20c and 20f on the new figures; until the owners apply them, PROVISIONAL):\n")
    for lab, X_ in (("the pair intact", FRI), ("one of the pair shorted", FR1)):
        w("         %s: on %.2f / %.2f / %.2f V at 7.6 / 10.6 / 16.8 V (over 2.5 V); held at 7.6 V DOCK_EN_OUT %.2f V (over %.3f V);\n"
          % (lab, X_[0][0], X_[0][1], X_[0][2], X_[1], R["out_pw_hi"]))
        w("           the regulator at its 6.0 V input from BRK_VIN %.2f V closed\n" % X_[2])
    w("   (d) each source present or absent: path 1 as section 9 (d); path 2 lives while VBAT does, from the pack after a breaker start or from\n")
    w("       any source that holds VBAT up\n")
    w("   (e) docking, path 1 (U63 on VBAT loads no docking), the model of section 9 (e) with the delta's capacitors at +10 %, the pull-up's draw\n")
    w("       from the start, the clamp's leakage on the gate and Q61's on DOCK_EN_OUT:\n")
    for v in (V_HELD, V_LOW, V_HIGH):
        t13, t25 = dk_fs[v]
        w("       BRK_VIN %4.1f V: VDD passes 1.3 V at %5.1f ms; a HOT guard's gate passes 2.5 V at %5.1f ms: %s the hold's least %.3f s\n"
          % (v, t13 * 1e3, t25 * 1e3 if t25 else float("inf"), "before" if t25 and t25 < hold[0] else "AFTER", hold[0]))
    w("       a COLD guard before tEN: path 1's gate %.3f V and path 2's %.3f V at the tolerances, under the 2N7002's least 1 V; FM1 with one\n"
      % (g_inv1, g_inv2))
    w("       resistor: the input capacitors at +10 %% %.2f uF, under the %.1f uF path 1's slower phase allows\n" % (cin_fs * 1e6 * (1 + C_TOL), cin_max_fs))
    w("   (f) the ground between the boards: unchanged for Q60; Q61 pulls DOCK_EN_OUT to board A's ground, read by board P through the same\n")
    w("       return: the offset of section 9 (f) applies alike\n")
    w("   (g) parts within limits: Q61 at most %.1f V on DOCK_EN_OUT against %.0f V; U63's input VBAT at most 18 V (its rail's peak) against\n"
      % (V_CLAMP, N7["vds"]))
    w("       %.0f V PRINTED; Q62 and Q63 at most %.2f V across the two (the return, with Q60's short, the clamp off) against %.0f V each;\n"
      % (S["vin_max"], ret_open, N7["vds"]))
    w("       R268, R269 at most %.3f mW; U60's open drain at most VDD against 6 V; C268 and C270 at most 29.2 V against 50 V\n"
      % (DF["vdd_hi"] ** 2 / r_one * 1e3))
    w("   THE DELTA'S OWN SINGLE FAILURES (INFERRED from the circuit as drawn; none removes the trip at once, each leaving the other path, under\n")
    w("   which L8P-R9-F1 and path 2's unbounded retry heating apply: PROVISIONAL):\n")
    for a_, b_ in (("Q62 or Q63 drain to source shorted", "the other holds the clamp"),
                   ("Q62 or Q63 open, or its gate to source shorted", "the clamp lost: path 1 as round 8, path 2 intact"),
                   ("R268 or R269 shorted", "%.0f kOhm left, the clamp kept; the tripped draw %.2f uA, counted" % (min(FS["pullup"]) / 1e3, trip_one * 1e6)),
                   ("R268 or R269 open", "the clamp off: path 1 as round 8, path 2 intact"),
                   ("Q62's gate to drain shorted", "THG_ODN on THG_G: cold, the pull-up lifts Q60's gate: path 1 trips, found at once"),
                   ("U63 open, or C271 open or shorted", "path 2 lost (its behaviour without its output capacitor NOT PRINTED): path 1 remains"),
                   ("U63's pass element shorted", "U62's VDD at VBAT, over its 6 V: its state NOT PRINTED: trips (found) or path 2 lost (path 1)"),
                   ("U62 dead, stuck cold or its pad open", "path 2 lost: path 1 remains"),
                   ("U62 stuck tripped", "Q61 holds the loop open: found at once"),
                   ("R270 open, C272 or R271 shorted, Q61 open", "path 2 lost: path 1 remains"),
                   ("Q61 drain to source shorted", "DOCK_EN_OUT held low: the breaker never starts, found at once"),
                   ("Q61 gate to drain shorted", "its network loads DOCK_EN_OUT (the window untouched); its trip not shown: path 1 remains"),
                   ("C268, C270 shorted", "DOCK_EN_OUT or VBAT to ground: the loop collapses (found) or VBAT's fuse acts; neither path is needed")):
        w("     %-48s %s\n" % (a_, b_))
    w("   WHAT IS NOT CLOSED HERE, HANDED OVER AS REMAINING ENGINEERING (the owner's part 24; no latent-fault exception presumed): a first\n")
    w("     failure that silently removes ONE path (the rows above marked 'path 1 remains' or 'path 2 lost', and section 10's latent rows on\n")
    w("     path 1) is found only by E-13b, each path on its own (TP60 and TP64), and no service interval bounds that; a second failure in the\n")
    w("     other path before it is found removes the trip (the exposure of 10b). No automatic diagnostic is drafted: one that tests a shunt\n")
    w("     opens the breaker in service, and a cross-check of the two VTEMP outputs sees the switches, not the gate networks or the shunts.\n")
    w("     The cases: the double failures above; the attempted correction: this delta (single failures survived); the outputs PROVISIONAL on\n")
    w("     it: this section's verdict, C-PROT rev 1 for the guard, L4-E11 section 28 (finding L8P-R9-F1). After the recheck cx46 (items 10 and\n")
    w("     17), also REMAINING ENGINEERING: the bounded retry-energy analysis of path 2 alone, and an AUTOMATIC diagnostic (with a bounded\n")
    w("     detection and response interval that covers faults after start-up and faults of the diagnostic itself) or a fault-tolerant redesign;\n")
    w("     L8P-R9-F1 weakens every C-PROT claim for the guard, which stays PROVISIONAL\n")
    w("   COMPOSED (L4-E9's order with this record's drafts, then the delta; scratch, removed after): %d scripts, %s\n"
      % (X["n_seq"], "every one OK" if all(v.startswith("OK") for _n, v in X["res"]) else "; ".join("%s %s" % r_ for r_ in X["res"] if not r_[1].startswith("OK"))))
    w("     the delta without round 8's guard: %s\n" % X["without"])
    w("     the delta a second time: %s; on the tree's own generator: %s\n" % (X["twice"], X["tree"]))
    if X.get("gen_rc") == 0:
        w("     the generator ran to its end (%d parts); check_l8p_fs (this round's reader): A EN %s, A THG %s; round 8's check_l8p_netlist\n"
          % (X["parts"], X["en"][0], X["thg"][0]))
        w("     reads THG %s on it, as it must (it knows no delta: its THG group is to admit the delta when the delta is released, L8P-R9-F3)\n" % X["round8"])
        w("     L4-E11's check_dd7_netlist (its round 18 admits C268 and Q61): %s\n" % X["dd7"])
        for lab, v, why in X["mut"]:
            w("     mutated, %-62s THG %s: %s\n" % (lab + ":", v, why[:90]))
    else:
        w("     the generator FAILED (%r)\n" % X.get("gen_rc"))
    w("   DISPOSITION (10c, after the recheck cx46: CORRECTIONS NOT CLOSED, the method ends): V6-m7 and cx45's Q5 NOT CLOSED. Drafted and\n")
    w("     reproducible: the two paths (the intact circuit's desk rows %s, the composition %s). PROVISIONAL: C-PROT rev 1 for the guard (L8P-R9-F1,\n"
      % ("hold" if fs_ok else "DO NOT HOLD", "reads DRAWN and its mutations FAIL" if comp_ok else "NOT as drafted"))
    w("     the retry heating with path 1 lost), the allowances (L8P-R9-F2, unrestated by their owners). REMAINING ENGINEERING: the retry-\n")
    w("     energy analysis, the automatic diagnostic or a fault-tolerant redesign, the allowance rows' restatement; L8P-R9-F3 at release\n")

    # ------------------------------------------------------------------ 11. verdict and E-13b
    holds = (reproduced and same and m10 > 0 and m18 > 0 and mc4 > 0 and DF["window"] and DF["four"] and DRI["reg_c"] < V_LOW
             and all(dk[v][1] is not None and dk[v][1] < hold[0] for v in dk) and cout_ok and DF["g_inv_t"] < N7["vth"][0] and DF["bands_apart"])
    w("\n11. VERDICT, WHAT STAYS OPEN, AND E-13b\n")
    w("   the check (item 1): C4 CONFIRMED on the makers' sheets, with the relabellings of sections 2, 5 and 9 (d); no figure fails to reproduce\n")
    w("   the draft draws C4's values: %s\n" % ("yes" if same else "NO"))
    w("   the judgement (item 3) on C-PROT rev 1: the intact round 8 circuit's desk rows %s (PROVISIONAL as a protection: a latent single failure\n"
      % ("HOLD" if holds else "DO NOT HOLD"))
    w("     of section 10 removes it, and the delta's L8P-R9-F1 and retry heating are REMAINING ENGINEERING): the no-trip side on the switch's\n")
    w("     printed limits (%.1f, %.1f and %.1f K), the trip\n" % (m10, m18, mc4))
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
      % (5.0 * (1 - S["acc_out"]), DF["vdd_hi"], DRI["reg_c"]))
    w("         1 mA of load, ASSUMED at the switch's microamps)\n")
    w("   L8P-F07 and L8P-F08 stay OPEN until an independent check has read this round (the brief); a negative check of C4 ends that loop\n")
    w("   ROUND 9 (part 22 item A, cx45 Q5, the recheck cx46): V6-m7 OPEN; the two-path delta DRAFTED (10c, apply_gen_sch_a_thgfs.py; its\n")
    w("     intact circuit's desk rows %s), NOT CLOSED: C-PROT for the guard PROVISIONAL; L8P-R9-F1 (a latent first failure and a second, the\n"
      % ("hold" if fs_ok and comp_ok else "DO NOT HOLD"))
    w("     retry heating with path 1 lost: REMAINING ENGINEERING), L8P-R9-F2 (the allowances, unrestated) and L8P-R9-F3 OPEN; E-13b gains (e): TRIP_TEST on each\n")
    w("     switch alone (TP60 with TP63, then TP64 with TP67) opens the breaker; THG_ODN (TP66) reads within %.2f V of VDD cold and low with\n" % (leak_pu * rpu_p))
    w("     TP60 high (the clamp's gate); TP67 reads 4.95 to 5.05 V with VBAT over U63's dropout\n")

    # ------------------------------------------------------------------ 12. predicates
    preds = [
        ("the check: every figure of record l9stk's C4 read here reproduces within its printed rounding", reproduced),
        ("the 2N7002 prints its on-resistance at VGS 5 V and 10 V only, its leakage and threshold at 25 C only", N7["r5"] == 7.0 and N7["r10"] == 5.0),
        ("C4: the window holds as a ramp's reading on the full count, also with Q103's gate doubled", F["ret_all"] >= R["ret_closed"]),
        ("round 4's AO3400A at the same site fails the same window (L8P-F08)", F["ret_ao"] < R["ret_closed"]),
        ("C4: the four readings hold intact and with one of the pair shorted", F["four"]),
        ("C4: E-13b's tripped bands tell a shorted resistor of the pair from the intact pair", F["bands_apart"]),
        ("C4: the gate stays under 1 V through the start and tEN at the tolerances, and passes 2.5 V within 0.1 s of a trip", F["g_inv_t"] < N7["vth"][0] and F["t_on_t"] < 0.1),
        ("a shorted regulator puts over 6 V on the switch from the pack's least service voltage (FM2)", F["vdd_over"] < V_LOW),
        ("the no-trip side is printed at 10 A, in the 18 A service and at condition C4", m10 > 0 and m18 > 0 and mc4 > 0),
        ("the trip side leaves the gradient record l9stk prints", abs(g_left - L["grad"]) < 0.006 and abs(g_left2 - L["grad2"]) < 0.006),
        ("record l9stk's acceptance (b) names seven mutations", len(L["mutations"]) == 7),
        ("the draft draws C4's values", same),
        ("the draft: the window holds on the full count, intact and with one of its pair shorted", DF["window"]),
        ("the draft: the four readings hold intact and with one of its pair shorted", DF["four"]),
        ("the draft: E-13b's bands tell a shorted resistor of its pair from the intact pair", DF["bands_apart"]),
        ("the draft: its gate network keeps the gate under 1 V through the start at the tolerances and on within 0.1 s", DF["g_inv_t"] < N7["vth"][0] and DF["t_on_t"] < 0.1),
        ("the draft: FM1's single-resistor cycle would stay under the hold with its input capacitor, at the tolerances", D["cin"] * 1e6 * (1 + C_TOL) < DF["cin_max_t"]),
        ("the draft: a hot docking reaches the shunt before the RC hold's least start at 7.6, 10.6 and 16.8 V", all(dk[v][1] is not None and dk[v][1] < hold[0] for v in dk)),
        ("the draft: its output capacitor at -10 % is inside TI's 1.5 to 47 uF before its bias", cout_ok),
        ("the intact round 8 circuit's desk rows of C-PROT rev 1 hold (no closure: PROVISIONAL as a protection, section 10)", holds),
        ("round 9: Q60's gate-to-drain short fails the window (V6-m7), and a second shunt on the same return would too", R9["gd"] < R["ret_closed"] and R9["two"] > R9["alw"]),
        ("round 9: no requirement file names a latent state, a proof test or a service interval", Q["latent"] == 0 and Q["interval"] == 0),
        ("round 9: without the guard the FETs pass 150 C held under the breaker's most current limit (the exposure)", UG["i76"] < UG["lim"][2]),
        ("round 9: the delta's clamp holds the return under the held reading with Q60's short at the printed gate leakage", ret_cl < lim_ret),
        ("round 9: path 2 alone holds the return under the held reading and leaves DOCK_EN_OUT dark (DD-7 no trigger)", ret_q61 < lim_ret and out_q61 < R["out_pw_lo"]),
        ("round 9: each path trips within 0.1 s and keeps its gate under 1 V before tEN at the tolerances", t_on1 < 0.1 and t_on2 < 0.1 and g_inv1 < N7["vth"][0] and g_inv2 < N7["vth"][0]),
        ("round 9: the delta's draw is inside the restated allowances, and the loop's readings hold at them", cold_all <= FS_ALLOW_COLD and trip_one <= FS_ALLOW_TRIP
         and all(g > N7["vth"][1] for g in FRI[0] + FR1[0]) and FRI[1] > R["out_pw_hi"] and FR1[1] > R["out_pw_hi"]),
        ("round 9: a hot docking reaches path 1's shunt before the RC hold's least start at 7.6, 10.6 and 16.8 V", all(dk_fs[v][1] is not None and dk_fs[v][1] < hold[0] for v in dk_fs)),
        ("round 9: the delta's intact-circuit desk rows hold (no closure: L8P-R9-F1 and the retry heating are REMAINING ENGINEERING)", fs_ok),
        ("round 9: the delta composes in L4-E9's order, reads DRAWN on both checks, refuses as it must, and its seven mutations fail", comp_ok),
    ]
    w("\n12. PREDICATES\n")
    for text, val in preds:
        w("   %-128s %s\n" % (text, "yes" if val else "NO"))
    sys.stdout.write("".join(out))
    return 0


# W55 (Q-74, 6 October 2026; adopted in set 32 with W34's branch): the makers' PDFs this script reads as text, each with its pdftotext
# options. W34 converted l8p_guard.pdftext, which this script called for its three sheets, but this script's own read of the BZT52C
# sheet was in no table, so it refused on W34's branch ("diodes-bzt52c-ds18004.pdf with -layout is not declared in
# v2/docs/records/l8p's PDFTEXT table", W53). A module's table holds its own reads (PDFTEXT-INVENTORY.md section 2), so the three reads
# are declared here and go through v2/docs/records/_lib/pdftext.py with this table; the texts are the ones l8p_drafts.py and
# l8p_guard.py already declare (the BZT52C and 2N7002 texts committed beside their PDFs, the LM26LV text held back under held/pdftext/
# with its sheet); section 0 prints each text's sha256 after the pins. Nothing this script computes changed. Placed last so that no
# line above it moves. Re-take after a sheet changes: python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l8p
PDFTEXT = {
    "v2/vendor/diodes/diodes-bzt52c-ds18004.pdf": [["-layout"]],
    "v2/vendor/power/jscj-2n7002-c8545.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-lm26lv-snis144g.pdf": [["-layout"]],
}


def pdftext(path):
    """A maker's sheet's committed text, as l8p_guard.pdftext reads it (its absence check, -layout), against this script's table."""
    if not os.path.isfile(path):
        refuse("%s is absent (held back: run v2/docs/records/l8p/fetch_held_back.py)" % rel(path))
    return G.PT.pdf_text(ROOT, rel(path), ["-layout"], PDFTEXT, "v2/docs/records/l8p")


if __name__ == "__main__":
    sys.exit(main())
