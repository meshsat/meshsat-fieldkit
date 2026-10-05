#!/usr/bin/env python3
"""Record l9t5, P0-1 (MESHSAT-1357, 5 October 2026): the PA drain-current cap's design values and its band, every term labelled,
in one place, so the comparison (l9t5_f01.py), the case (l9t5_case.py section 8), the drafts (apply_gen_sch_a_paloop.py,
apply_gen_sch_d_paloop.py) and the netlist check (check_f01_netlist.py) read the same numbers. PROTOTYPE DESIGN, DESK ARITHMETIC:
nothing is built or measured. Imported, never run for an output; stdlib and pdftotext.

ROUND 2 OF THE SELECTION (after Astra's advisory challenge cx44, NOT SUPPORTED, first negative, kept as given): the terms are split
into PRINTED limits, TYPICAL figures carried as allowances, ASSUMPTIONS and MODEL arithmetic; U13's BIAS leaves R55 (re-tapped to
PA_OUT, ahead of the shunt), so R55 carries the PA's feed and microamperes; the set point carries a 1 mA preload (the TLV758P's
accuracy test condition); the set point starts from zero at each key (OUTLET_OK holds it, C557 ramps it); board D's VGG gets a
defined bleed (R58), because the LDO U15 cannot sink.

The loop (correction (c) of F01 / D-17):
  board A  U551 INA250A2 (2 mOhm integrated shunt, 500 mV/A) in series from +13V8_PA to +13V8_PAJ (J_PA pin 1), VS on +5V_D8IN, REF
           to ground; U552 TLV758P set point PA_ISET (R551 2.80k over R552 549 Ohm, 0.1 %, a 1.0 mA preload); R559 1k and C557 10 uF
           into PA_ISP, the integrator's set point, held at 0 V by Q551 (2N7002) while OUTLET_OK is high (the PA not keyed:
           OUTLET_OK = NOT (TR_APRS AND PA_EN), U30), so at each key the set point rises from zero with 10 ms; U553 TLV9062: half A
           integrates PA_IMON against PA_ISP (R553 10.0k, C554 47 nF), R560 470k from +5V_D8IN into its summing node makes the held
           state wind down; half B inverts it about PA_MID (R554 to R557), so PA_ILIM_A rests at 0 V while the current is under the
           set point; R558 into J_MEZZ1 pin 16 (AB_SPARE renamed PA_ILIM); U13's FB divider to 0.1 % (fb01's keyword); U13's BIAS
           re-tapped to PA_OUT.
  board D  J_HARN1 pin 16 PA_ILIM; C76 1 nF; R57 110k into VGG_FB; R83 10.0k to 11.0k (R83 // R57 = 10.0k: the band at rest is the
           drawn one); R58 10k from VGG_SW to ground, the bleed that gives VGG a defined fall rate with C62.
"""
import math
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

SHEETS = {
    "ina250": "v2/vendor/ti/held/ti-ina250-sbos511c.pdf",
    "tlv758p": "v2/vendor/ti/ti-tlv758p.pdf",
    "tlv9062": "v2/vendor/ti/ti-tlv9062-op-amp.pdf",
    "lm5176": "v2/vendor/ti/lm5176-datasheet.pdf",
    "wsl": "v2/vendor/vishay/vishay-wsl-power-metal-strip.pdf",
    "csd18510": "v2/vendor/battery/ti-csd18510q5b.pdf",
    "ina226": "v2/vendor/ti/ti-ina226.pdf",
}

# ---- the design values (SESSION, record l9t5 P0-1, round 2 of the selection)
G_SENSE = 0.5                      # V/A, INA250A2
R_SET_TOP, R_SET_BOT = 2.80e3, 549.0      # R551, R552: 0.1 % 25 ppm/K; 0.55 V / 549 = 1.0 mA preload (SBVS351D's IOUT = 1 mA test)
R_SS, C_SS = 1e3, 10e-6            # R559, C557: the set point's ramp at each key, 10 ms
R_INT, C_INT = 10e3, 47e-9         # R553, C554: the integrator, 0.47 ms
R_BIAS = 470e3                     # R560: +5V_D8IN into the summing node (the held state winds down)
R_INV = 10e3                       # R554 to R557, 0.1 % 25 ppm/K
R_OUT = 1e3                        # R558
R83_NEW, R_INJ, R82 = 11.0e3, 110e3, 71.5e3   # board D
R_BLEED = 10e3                     # board D's R58 on VGG_SW
C62 = 2.2e-6                       # board D's U15 output capacitor (nominal)
C_FILT = 1e-9                      # board D's C76
U13_RT, U13_RB = 162e3, 10e3
DIV_TOL, DIV_TCR, DIV_DT = 0.001, 25e-6, 65.0
R1PC_TOL, R1PC_TCR = 0.01, 100e-6  # the tree's 1 % 0603 class (UNI-ROYAL 0603WAF, gen_sch_d.py's note): ASSUMPTION for 162k/10k
T_AIR, T_COLD, T_REF = 76.25, -20.0, 25.0     # C: board A's inside air bound (L4-E12, C-PROT rev 1's start), the cold end, 25 C
V5 = (4.872, 5.002, 5.133)         # V: +5V_D8IN's DC band (stream s99a's u41_divider.out, gen_sch_a.py's note)
V5_WORK = 5.14
IB_BOUND = 1e-9                    # A: TLV9062 input bias (TYPICAL 0.5 pA printed only): ASSUMPTION
IR_X7R_OHM_F = 50.0                # Ohm F: a ceramic capacitor's insulation resistance product (ASSUMPTION: no capacitor sheet held)
IDSS_25, IDSS_DOUBLE_K = 80e-9, 10.0   # A, K: 2N7002 IDSS printed at 25 C (JSCJ); doubling every 10 K (record l8p's ASSUMPTION)
GND_SHIFT = 0.10                   # V: board D's ground above board A's at the harness (bounded below, MODEL)
ISNS_R, ISNS_TOL = 0.006, 0.01     # R55: WSL25126L000FEA, 6 mOhm 1 %
R55_RTH = 100.0                    # K/W: WSL2512's derating line (1.0 W to 70 C, zero at 170 C): MODEL, not a printed resistance
R55_OTHER_A = 0.0010               # A: R55's loads beside the PA feed, bounded in r55_other() (MODEL on printed and typical rows)
NONLIN = 0.0003                    # INA250 nonlinearity, TYPICAL 0.03 %, carried as an allowance


def _pdf(key):
    p = os.path.join(ROOT, SHEETS[key])
    if not os.path.isfile(p):
        raise SystemExit("l9t5_paloop: %s is not in the tree%s" % (SHEETS[key], " (held back: v2/docs/records/l4e7/fetch_held_back.py)" if "held" in SHEETS[key] else ""))
    r = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit("l9t5_paloop: pdftotext could not read %s" % SHEETS[key])
    return r.stdout.decode("utf-8", "replace")


def _need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        raise SystemExit("l9t5_paloop: %s: the pattern no longer matches its pinned sheet" % what)
    return m


def read_sheets():
    """The printed (and typical) rows the loop rests on, each parsed from its sheet."""
    S = {}
    t = _pdf("ina250")
    S["ina_rev"] = _need(t, r"(SBOS511C)", "the INA250 sheet's number").group(1)
    S["ina_gerr"] = float(_need(t, r"System gain error\(6\)\s+±([\d.]+)%", "INA250 gain error over temperature").group(1)) / 100
    S["ina_ios"] = float(_need(t, r"INA250A2, ISENSE = 0 A\s+±([\d.]+)\s+±([\d.]+)", "INA250A2 offset current").group(2)) * 1e-3
    S["ina_dios"] = float(_need(t, r"RTI versus temperature\s+TA = –40°C to 125°C\s+(\d+)\s+(\d+)\s+μA/°C", "INA250 offset drift").group(2)) * 1e-6
    S["ina_psr"] = float(_need(t, r"PSR\s+VS = 2\.7 V to 36 V, TA = –40°C to 125°C\s+±([\d.]+)\s+±([\d.]+)\s+mA/V", "INA250 PSR").group(2)) * 1e-3
    S["ina_cmr"] = float(_need(t, r"INA250A2, VIN\+ = 0 V to 36 V,\s*\n\s*(\d+)\s+(\d+)", "INA250A2 CMR").group(1))
    S["ina_rsh"] = float(_need(t, r"Shunt resistance\s+([\d.]+)\s+(\d)\s+([\d.]+)\s*\n\s*RSHUNT\s+onboard amplifier", "INA250 shunt").group(2)) * 1e-3
    S["ina_rpkg"] = float(_need(t, r"Package resistance\s+IN\+ to IN–\s+([\d.]+)", "INA250 package resistance").group(1)) * 1e-3
    S["ina_imax"] = float(_need(t, r"TA = –40°C to 85°C\s+±(\d+)\s+A", "INA250 continuous current").group(1))
    S["ina_rja"] = float(_need(t, r"RθJA\s+Junction-to-ambient thermal resistance\s+([\d.]+)", "INA250 RthJA").group(1))
    S["ina_iq"] = float(_need(t, r"IQ\s+Quiescent current\s+TA = –40°C to 125°C\s+(\d+)\s+(\d+)\s+μA", "INA250 IQ").group(2)) * 1e-6
    S["ina_ib"] = float(_need(t, r"IB\s+Input bias current\s+IB\+, IB-, ISENSE = 0 A\s+±(\d+)\s+±(\d+)\s+μA", "INA250 IB").group(2)) * 1e-6
    S["ina_bw"] = float(_need(t, r"INA250A2, CL = 10 pF\s+(\d+)", "INA250A2 bandwidth (TYPICAL)").group(1)) * 1e3
    S["ina_stress"] = [float(x) / 100 for x in re.findall(r"(?:ISENSE = 30 A for 5 seconds|500 cycles|260°C solder, 10 s|1000 hours, TA = 150°C|24 hours, TA = –65°C)\s+±([\d.]+)%", t)]
    if len(S["ina_stress"]) != 5:
        raise SystemExit("l9t5_paloop: the INA250's five shunt stress rows")
    _need(t, r"System gain error does not include the\s*\n\s*stress related characteristics", "INA250 note 6")
    pins = {"IN–": "1, 2, 3", "IN\\+": "14, 15, 16", "OUT": "9", "REF": "7", "SH–": "4", "SH\\+": "13", "VIN–": "5", "VIN\\+": "12", "VS": "10"}
    for nm, nos in pins.items():
        _need(t, r"^\s*%s\s+%s\s" % (nm, re.escape(nos)), "INA250 pin %s" % nm)
    _need(t, r"^\s*GND\s+6, 8, 11\s", "INA250 GND pins")
    t = _pdf("tlv758p")
    S["ref_rev"] = _need(t, r"(SBVS351D)", "the TLV758P sheet's number").group(1)
    S["ref_vfb"] = float(_need(t, r"VFB\s+Feedback voltage\s+TJ = 25°C\s+([\d.]+)\s+V", "TLV758P VFB").group(1))
    S["ref_acc"] = float(_need(t, r"Output accuracy\(1\)\s+–40°C ≤ TJ ≤ \+85°C\s+–(\d+)%\s+(\d+)%", "TLV758P accuracy").group(2)) / 100
    S["ref_acc125"] = float(_need(t, r"–40°C ≤ TJ ≤ \+125°C\s+–([\d.]+)%\s+([\d.]+)%", "TLV758P accuracy to 125 C").group(2)) / 100
    _need(t, r"VIN = VOUT\(NOM\) \+ 0\.5 V or 1\.5 V \(whichever is greater\), IOUT = 1 mA,", "TLV758P test condition IOUT = 1 mA")
    S["ref_line"] = float(_need(t, r"Line regulation\s+VOUT\(NOM\) \+ 0\.5 V\(2\) ≤ VI N ≤ 6\.0 V\s+(\d+)\s+([\d.]+)\s+mV", "TLV758P line regulation").group(2)) * 1e-3
    S["ref_ifb"] = float(_need(t, r"IFB\s+Feedback pin current\s+([\d.]+)\s+([\d.]+)\s+µA", "TLV758P IFB").group(2)) * 1e-6
    S["ref_ignd"] = float(_need(t, r"IGND\s+Ground current\s+–40°C ≤ TJ ≤ \+125°C\s+(\d+)\s+µA", "TLV758P IGND").group(1)) * 1e-6
    S["ref_cout_min"] = float(_need(t, r"COUT\s+Output capacitor\(1\)\s+(\d+)\s+(\d+)\s+µF", "TLV758P COUT").group(1)) * 1e-6
    t = _pdf("tlv9062")
    S["oa_rev"] = _need(t, r"(SBOS839N)", "the TLV906x sheet's number").group(1)
    S["oa_vos"] = float(_need(t, r"VS = 5V, TA = –40°C to 125°C\s+±([\d.]+)\s*\n", "TLV9062 VOS over temperature").group(1)) * 1e-3
    S["oa_psrr"] = float(_need(t, r"PSRR\s+Power-supply rejection ratio\s+VS = 1\.8V – 5\.5V, VCM = \(V–\)\s+±([\d.]+)\s+±([\d.]+)\s+µV/V", "TLV9062 PSRR").group(2)) * 1e-6
    S["oa_cmrr"] = float(_need(t, r"VS = 5\.5V, \(V–\) – 0\.1V < VCM < \(V\+\) – 1\.4V,\s*\n\s*(\d+)\s+(\d+)", "TLV9062 CMRR").group(1))
    S["oa_ib_typ"] = float(_need(t, r"IB\s+Input bias current\s+±([\d.]+)\s+pA", "TLV9062 IB").group(1)) * 1e-12
    S["oa_swing"] = float(_need(t, r"Voltage output swing from supply\s+VS = 5\.5V, RL = 10kΩ\s+(\d+)", "TLV9062 output swing").group(1)) * 1e-3
    S["oa_iq"] = float(_need(t, r"VS = 5\.5V, IO = 0mA, TA = –40°C to 125°C\s+(\d+)", "TLV9062 IQ").group(1)) * 1e-6
    S["oa_aol"] = float(_need(t, r"VS = 5\.5V, \(V–\) \+ 0\.05V < VO < \(V\+\) – 0\.05V,\s*\n\s*(\d+)\s+(\d+)", "TLV9062 AOL").group(1))
    t = _pdf("lm5176")
    S["lm_vref"] = tuple(float(x) for x in _need(t, r"VREF\s+Feedback reference voltage\s+FB = COMP\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "LM5176 VREF").groups())
    S["lm_ibfb"] = float(_need(t, r"IBIAS\(FB\)\s+Feedback pin input bias current\s+FB in regulation\s+(\d+)\s+nA", "LM5176 FB bias").group(1)) * 1e-9
    S["lm_vsns"] = tuple(float(x) * 1e-3 for x in _need(t, r"VSNS\s+Average current loop regulation target\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "LM5176 VSNS").groups())
    S["lm_fsw"] = tuple(float(x) * 1e3 for x in _need(t, r"fSW\(1\)\s+Switching frequency 1\s+RT = 40 k\S\s+(\d+)\s+(\d+)\s+(\d+)", "LM5176 fSW").groups())
    S["lm_vcc"] = tuple(float(x) for x in _need(t, r"VVCC\(VIN\)\s+Regulation voltage\s+VBIAS = 0 V, VCC open\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "LM5176 VCC").groups())
    S["lm_iop"] = float(_need(t, r"VIN operating current\s+VEN/UVLO = 2 V, VFB = 0\.9 V\s+(\d+)\s+(\d+)\s+mA", "LM5176 operating current").group(2)) * 1e-3
    _need(t, r"For VBIAS > 8 V, the VCC regulator draws power\s*\n?\s*from the BIAS pin", "LM5176 BIAS takes VCC's power above 8 V")
    t = _pdf("wsl")
    S["wsl_tcr"] = float(_need(t, r"± (\d+) for 5 m\S to 6\.9 m\S", "WSL2512 TCR 5 to 6.9 mOhm").group(1)) * 1e-6
    t = _pdf("csd18510")
    m = _need(t, r"Qg\s+Gate charge total \(4\.5 V\)\s+(\d+)\s+(\d+)\s+nC\s*\nQg\s+Gate charge total \(10 V\)\s+(\d+)\s+(\d+)\s+nC", "CSD18510Q5B Qg")
    S["fet_qg45"], S["fet_qg10"] = float(m.group(2)) * 1e-9, float(m.group(4)) * 1e-9
    t = _pdf("ina226")
    S["u14_vbus_z"] = float(_need(t, r"VBUS input impedance\s+(\d+)\s+kΩ", "INA226 VBUS impedance (TYPICAL)").group(1)) * 1e3
    return S


def u13_window(S, tol, tcr):
    """U13's output (VREF printed, the divider at tol and tcr over 65 K, IBIAS(FB) printed): (lowest, nominal, highest)."""
    lmv = S["lm_vref"]
    e = tol + tcr * 65.0
    return (lmv[0] * (1 + U13_RT * (1 - e) / (U13_RB * (1 + e))) - S["lm_ibfb"] * U13_RT,
            lmv[1] * (1 + U13_RT / U13_RB),
            lmv[2] * (1 + U13_RT * (1 + e) / (U13_RB * (1 - e))) + S["lm_ibfb"] * U13_RT)


def bias_current(S):
    """What U13's BIAS draws (VCC's regulator above 8 V): four CSD18510Q5B gates at VCC's top, Qg read between the printed 4.5 V and
    10 V maxima (MODEL: linear between them), at fSW's printed maximum scaled from 40 k to the drawn 40.2 k, plus the operating
    current's printed maximum (taken as the IC's own share). The re-tap takes all of it off R55."""
    vcc = S["lm_vcc"][2]
    qg = S["fet_qg45"] + (S["fet_qg10"] - S["fet_qg45"]) * (vcc - 4.5) / (10.0 - 4.5)
    fsw = S["lm_fsw"][2] * 40.0 / 40.2
    return 4 * qg * fsw + S["lm_iop"], qg, fsw


def r55_other(S, vpa_hi):
    """R55's loads beside the PA feed once BIAS is on PA_OUT: U13's divider (162k + 10k), U14's VBUS (830 k TYPICAL) and IN- (0.1 nA
    TYPICAL), U551's VIN+ bias (35 uA PRINTED max), U13's ISNS- pin through R163 (3 uA, the generator's note), and the output
    bulk's leakage (two 470 uF 25 V hybrid polymers, 0.01 CV, ASSUMPTION: no Panasonic ZK leakage row held)."""
    terms = [("U13's FB divider at the rail's top", vpa_hi / (U13_RT + U13_RB)),
             ("U14 VBUS (TYPICAL 830 kOhm)", vpa_hi / S["u14_vbus_z"]),
             ("U551 VIN+ bias, PRINTED 35 uA max", S["ina_ib"]),
             ("U13 ISNS- through R163, 3 uA (generator's note)", 3e-6),
             ("C170, C171 leakage, 2 x 0.01 x 470 uF x 25 V (ASSUMPTION)", 2 * 0.01 * 470 * 25 * 1e-6)]
    return terms, math.fsum(x for _l, x in terms)


def cap(S, r_top=R_SET_TOP, r_bot=R_SET_BOT):
    """The cap's band. The integrator settles where PA_IMON + R553 x (V+ - PA_ISP) / R560 = PA_ISP + VOS, so
    I = (PA_ISP x (1 + R553/R560) - V+ x R553/R560 + VOS) / (G (1 + gain error)) - IOS, PA_ISP = PA_ISET - (Q551 + C557 leakage) x R559.
    Every term is listed with its label; the corners are taken together (worst case, linear)."""
    L = {}
    L["vpa_drawn"] = u13_window(S, R1PC_TOL, R1PC_TCR)
    L["vpa"] = u13_window(S, DIV_TOL, DIV_TCR)
    e = DIV_TOL + DIV_TCR * DIV_DT
    vfb, acc = S["ref_vfb"], S["ref_acc"]
    L["ref_preload"] = vfb / r_bot
    L["vset"] = (vfb * (1 - acc) * (1 + r_top * (1 - e) / (r_bot * (1 + e))) - S["ref_ifb"] * r_top - S["ref_line"],
                 vfb * (1 + r_top / r_bot),
                 vfb * (1 + acc) * (1 + r_top * (1 + e) / (r_bot * (1 - e))) + S["ref_ifb"] * r_top + S["ref_line"])
    dT = max(T_AIR - T_REF, T_REF - T_COLD)
    dv5 = max(abs(V5[0] - 5.0), abs(V5[2] - 5.0))
    L["ios_terms"] = [("offset current, PRINTED max at 25 C (A2)", "PRINTED", S["ina_ios"]),
                      ("its drift, PRINTED %.0f uA/K max over %.2f K (board A's air -20 to %.2f C)" % (S["ina_dios"] * 1e6, dT, T_AIR), "PRINTED", S["ina_dios"] * dT),
                      ("PSR, PRINTED %.0f mA/V max, +5V_D8IN %.3f to %.3f V against the 5 V test" % (S["ina_psr"] * 1e3, V5[0], V5[2]), "PRINTED", S["ina_psr"] * dv5),
                      ("CMR, PRINTED %.0f dB min, VIN+ up to %.3f V against the 12 V test" % (S["ina_cmr"], L["vpa"][2]), "PRINTED",
                       abs(L["vpa"][2] - 12.0) * 10 ** (-S["ina_cmr"] / 20.0) / S["ina_rsh"])]
    L["ios"] = math.fsum(x for _l, _k, x in L["ios_terms"])
    L["gain_terms"] = [("system gain error, PRINTED max -40 to 125 C (amplifier and shunt)", "PRINTED", S["ina_gerr"]),
                       ("the shunt's five stress rows, TYPICAL column, excluded from the gain error by note 6: carried whole", "TYPICAL", math.fsum(S["ina_stress"])),
                       ("nonlinearity, TYPICAL 0.03 %, carried whole", "TYPICAL", NONLIN)]
    L["gerr"] = math.fsum(x for _l, _k, x in L["gain_terms"])
    L["gerr_printed"] = S["ina_gerr"]
    vcm = L["vset"][2]
    L["vos_terms"] = [("VOS, PRINTED %.1f mV max (VS 5 V, -40 to 125 C)" % (S["oa_vos"] * 1e3), "PRINTED", S["oa_vos"]),
                      ("PSRR, PRINTED %.0f uV/V max over +5V_D8IN's %.3f V from the 5 V of the VOS row" % (S["oa_psrr"] * 1e6, dv5), "PRINTED", S["oa_psrr"] * dv5),
                      ("CMRR, PRINTED %.0f dB min (VS 5.5 V row; ASSUMPTION that it holds at 4.87 to 5.13 V), VCM %.3f V against VS/2" % (S["oa_cmrr"], vcm), "PRINTED",
                       abs(vcm - V5[0] / 2) * 10 ** (-S["oa_cmrr"] / 20.0)),
                      ("IB, TYPICAL %.1f pA only: bounded at %.0f nA into R553 (ASSUMPTION)" % (S["oa_ib_typ"] * 1e12, IB_BOUND * 1e9), "ASSUMPTION", IB_BOUND * R_INT),
                      ("C554's leakage, %.0f Ohm F (ASSUMPTION) at %.2f V into R553" % (IR_X7R_OHM_F, V5[2]), "ASSUMPTION", V5[2] / (IR_X7R_OHM_F / C_INT) * R_INT),
                      ("finite gain, PRINTED AOL %.0f dB min: at most the output's travel %.2f V divided by it" % (S["oa_aol"], V5[2]), "PRINTED", V5[2] * 10 ** (-S["oa_aol"] / 20.0))]
    L["vos"] = math.fsum(x for _l, _k, x in L["vos_terms"])
    i_leak = IDSS_25 * 2 ** ((T_AIR - T_REF) / IDSS_DOUBLE_K) + V5[2] / (IR_X7R_OHM_F / C_SS)
    L["leak"] = i_leak
    eb = R1PC_TOL + R1PC_TCR * 65.0

    def I(vset, vp, rb, vos, g, ios, il):
        visp = vset - il * R_SS
        return (visp * (1 + R_INT / rb) - vp * R_INT / rb + vos) / (G_SENSE * (1 + g)) - ios
    L["i_nom"] = I(L["vset"][1], V5[1], R_BIAS, 0.0, 0.0, 0.0, 0.0)
    L["i_max"] = I(L["vset"][2], V5[0], R_BIAS * (1 + eb), L["vos"], -L["gerr"], -L["ios"], 0.0)
    L["i_min"] = I(L["vset"][0], V5[2], R_BIAS * (1 - eb), -L["vos"], L["gerr"], L["ios"], i_leak)
    L["i_max_printed_only"] = I(L["vset"][2], V5[0], R_BIAS * (1 + eb), S["oa_vos"] + S["oa_psrr"] * dv5, -S["ina_gerr"], -L["ios"], 0.0)
    L["i_min_printed_only"] = I(L["vset"][0], V5[2], R_BIAS * (1 - eb), -(S["oa_vos"] + S["oa_psrr"] * dv5), S["ina_gerr"], L["ios"], 0.0)
    # U13's own loop and R55: the shunt hot at the cap's top, its printed TCR
    vs = S["lm_vsns"]
    L["r55_w"] = (L["i_max"] + R55_OTHER_A) ** 2 * ISNS_R
    L["r55_t"] = T_AIR + L["r55_w"] * R55_RTH
    L["u13_min_init"] = vs[0] / (ISNS_R * (1 + ISNS_TOL))
    L["u13_min"] = vs[0] / (ISNS_R * (1 + ISNS_TOL) * (1 + S["wsl_tcr"] * (L["r55_t"] - T_REF)))
    L["u13_max"] = vs[2] / (ISNS_R * (1 - ISNS_TOL) * (1 - S["wsl_tcr"] * (T_REF - T_COLD)))
    L["bias"] = bias_current(S)
    L["r55_terms"], L["r55_other"] = r55_other(S, L["vpa"][2])
    L["p_max"] = L["vpa"][2] * L["i_max"]
    L["p_max_drawn"] = L["vpa_drawn"][2] * L["i_max"]
    L["ina_w"] = L["i_max"] ** 2 * S["ina_rpkg"]
    L["ina_tj"] = T_AIR + L["ina_w"] * S["ina_rja"]
    L["supply_a"] = S["ina_iq"] + S["ref_ignd"] + L["ref_preload"] + 2 * S["oa_iq"] + V5_WORK / (2 * R_INV) + V5_WORK / R_BIAS
    return L


def vgg_band(S, r82=R82, r83=R83_NEW, rinj=R_INJ, gnd_shift=GND_SHIFT, rest_hi=None):
    """Board D's VGG with the injection resistor, the loop at rest (PA_ILIM between 0 V and its rest top, seen at board D with the
    ground shift): U15 regulates VGG_FB to VFB; VGG = VFB + R82 x (VFB / R83 + (VFB - V_ILIM) / R57) + IFB x R82, every resistor 1 %
    with 100 ppm/K over 65 K (gen_sch_d.py's term), VFB +-1 %, line regulation 7.5 mV.
    Returns (lowest, nominal, highest, the loop's authority: VGG's highest at PA_ILIM's top)."""
    e = R1PC_TOL + R1PC_TCR * 65.0
    vfb = S["ref_vfb"]
    if rest_hi is None:
        rest_hi = rest_top(S)

    def v(vf, a, b, c, vil, ifb):
        return vf + a * (vf / b + (vf - vil) / c) + ifb * a
    nom = v(vfb, r82, r83, rinj, 0.0, 0.0)
    hi = v(vfb * (1 + S["ref_acc"]), r82 * (1 + e), r83 * (1 - e), rinj * (1 - e), -gnd_shift, S["ref_ifb"]) + S["ref_line"]
    lo = v(vfb * (1 - S["ref_acc"]), r82 * (1 - e), r83 * (1 + e), rinj * (1 + e), rest_hi + gnd_shift, -S["ref_ifb"]) - S["ref_line"]
    auth = v(vfb * (1 + S["ref_acc"]), r82 * (1 + e), r83 * (1 - e), rinj * (1 - e), V5[0] - S["oa_swing"] - gnd_shift, S["ref_ifb"]) + S["ref_line"]
    return lo, nom, hi, auth


def rest_top(S):
    """PA_ILIM's highest while the loop rests, at board A: half A at its top rail (V+ less at most its printed swing), half B's
    output 2 x PA_MID - PA_INTO with the four 0.1 % 25 ppm/K resistors at their worst, plus half B's VOS times its noise gain 2."""
    e = DIV_TOL + DIV_TCR * DIV_DT
    k = (1 - e) / (1 + e)
    return V5[2] * (1 - k) + k * S["oa_swing"] + 2 * S["oa_vos"]


def ground_shift_bound(peak_a=2.0, contact_max=0.020, lead_m=0.150, awg16_ohm_m=13.17e-3, hot=1.25):
    """Board D's ground above board A's at the harness, bounded on the D8 power lead alone (its JST-VH pin 2: two contacts at JST's
    printed 20 mOhm after test, and 16 AWG at 150 mm, ASSUMPTION, hot), at +5V_D8's declared 2.0 A peak; the harness ground
    conductors and the coax shields in parallel only lower it. MODEL."""
    return peak_a * (2 * contact_max + lead_m * awg16_ohm_m * hot)


def dynamics(S, km=(3.0, 10.0, 30.0)):
    """The loop's small-signal crossover for module slopes dIDD/dVGG of km A/V (TYPICAL curves only: three values shown), the
    integrator's gain 1/(s R553 C554), the injection R82 / R57, the sense G: f_c = G x R82/R57 x km / (2 pi R553 C554); the lags the
    sheets give (INA250A2 bandwidth TYPICAL; the 1 us harness filter); VGG's fall rate with the bleed R58 and C62 (U15 cannot sink):
    MODEL."""
    out = []
    for k in km:
        fc = G_SENSE * (R82 / R_INJ) * k / (2 * math.pi * R_INT * C_INT)
        lag = math.degrees(math.atan(fc / S["ina_bw"])) + math.degrees(math.atan(2 * math.pi * fc * R_OUT * C_FILT))
        out.append((k, fc, 90.0 - lag))
    fall = 4.2 / R_BLEED / C62                  # V/s at VGG 4.2 V, the bleed alone (no module gate current counted)
    ramp_t = 3 * R_SS * C_SS
    return out, fall, ramp_t
