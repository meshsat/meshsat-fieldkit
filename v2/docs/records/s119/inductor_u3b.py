#!/usr/bin/env python3
"""inductor_u3b.py: U3B's inductor on the 400 kHz row, checked against the makers' figures (stream s119, S-119,
MESHSAT-1357, 29 September 2026; the second round, for the S-119 decision on U3B).

PROTOTYPE DESIGN, AI arithmetic on the makers' figures: nothing is built or measured.

The part drawn: L2B Coilcraft XAL1010-472ME. Its figures, Coilcraft Document 804-1 (v2/vendor/power/coilcraft-xal1010.pdf,
revised 02/25/26), page 1: 4.7 uH +-20 percent (note 2: at 1 MHz, 0.1 Vrms, 0 A), DCR 5.20 typ / 5.70 max mOhm, Isat 25.4 A
(note 5: the DC current at 25 C that drops the inductance 30 percent, typical; no minimum is printed), Irms 17.5 A for a
20 C rise and 24.0 A for 40 C (note 6: from 25 C ambient, for reference only); the inductance against current is page 2
(Document 804-2), read by stream s117 into records/s117/efficiency.py's INDUCTORS table (INFERRED, imported here, pinned).
The charger's figures, TI SLUSE66A: the switching frequency 340 / 400 / 460 kHz min / typ / max with PWM_FREQ = 1b (8.5,
printed page 16); Equation 2 (Isat at least the charge current plus half the ripple), Equation 3 (the buck ripple), the
boost ripple and the 20 to 40 percent ripple guidance (10.2.2.3, printed page 85); 4.7 uH paired with 400 kHz and 191 k
or 187 k on IADPT (Table 9-4, printed page 27); the converter's input over-current comparator at 150 mV across RAC with
RSNS_RAC = 0b and ACX_OCP at its power-on 1b (8.5, VOCP_lim_ACX, printed page 15).

U3B's envelope as drafted: VIN = VBAT, the node, 12.0 to 16.8 V (4S at 3.0 to 4.2 V a cell); VOUT = the lid pack, 12.0 to
16.8 V; ChargeCurrent at most 7.936 A (code 62); IIN_HOST 6.2 A nominal, 6.3 A maximum with R16B 10 mOhm. The inductor
current is the charge current in buck mode, the input current in boost mode and, in the buck-boost region, the larger
of the two (bounded here by the charge current's 7.936 A). The worst ripple is taken at the lowest inductance (the -20
percent tolerance times the DC-bias fall at the peak current) and the lowest frequency (340 kHz).
Run from the repository root: python3 v2/docs/records/s119/inductor_u3b.py > v2/docs/records/s119/inductor_u3b.out"""
import hashlib
import math
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
PIN_EFF = "c24d5cfe209be3db7437c39c6762ef4257dd881d561cba047284aa7cc08b5809"
if hashlib.sha256(open(os.path.join(TOP, "v2/docs/records/s117/efficiency.py"), "rb").read()).hexdigest() != PIN_EFF:
    sys.stderr.write("inductor_u3b: records/s117/efficiency.py is not the pinned file; refusing\n")
    sys.exit(2)
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/s117"))
import efficiency as EF  # noqa: E402

PART = "XAL1010-472ME"
L_NOM, TOL = 4.7e-6, 0.20
DCR_MAX = 5.70e-3
ISAT, IRMS20, IRMS40 = 25.4, 17.5, 24.0
FS = (340e3, 400e3, 460e3)
ICHG_MAX = 7.936
IIN_MAX = 6.3
V_LO, V_HI = 12.0, 16.8
R16B = 0.010
V_ACX = 0.150


def ripple(mode, vin, vout, f, L):
    if mode == "buck":
        d = vout / vin
        return vin * d * (1.0 - d) / (f * L)
    if mode == "boost":
        d = 1.0 - vin / vout
        return vin * d / (f * L)
    return 0.25 * vin / (f * L)          # the buck-boost bound efficiency.py uses


def main():
    o = []
    P = o.append
    P("U3B'S INDUCTOR ON THE 400 kHz ROW (inductor_u3b.py, stream s119, S-119). %s against Coilcraft 804-1 p.1 and SLUSE66A;" % PART)
    P("AI arithmetic on the makers' figures; nothing built or measured.")
    P("")
    cases = []
    for mode, vin, vout, il in (("buck", V_HI, V_LO, ICHG_MAX),
                                ("buck", V_HI, 14.4, ICHG_MAX),
                                ("boost", V_LO, V_HI, IIN_MAX),
                                ("boost", 14.4, V_HI, IIN_MAX),
                                ("buck-boost bound", V_HI, V_HI, ICHG_MAX),
                                ("buck-boost bound", V_LO, V_LO, ICHG_MAX)):
        for f in FS[:2]:
            for tol_lab, tol in (("nominal L", 0.0), ("L -20 %", TOL)):
                L = L_NOM * (1.0 - tol)
                for _ in range(20):                      # the DC-bias fall at the peak (804-2, INFERRED reading)
                    di = ripple(mode.split()[0] if mode != "buck-boost bound" else "bb", vin, vout, f, L)
                    ipk = il + di / 2.0
                    L = L_NOM * (1.0 - tol) * EF.lfrac(PART, ipk)
                irms = math.sqrt(il * il + di * di / 12.0)
                cases.append((mode, vin, vout, il, f, tol_lab, L, di, ipk, irms))
    P("   %-18s %6s %6s %7s %6s %-10s %8s %9s %8s %8s %9s" % ("mode", "VIN", "VOUT", "IL avg", "fS", "L case", "L (uH)", "ripple", "ripple%", "peak", "RMS"))
    for mode, vin, vout, il, f, tl, L, di, ipk, irms in cases:
        P("   %-18s %6.1f %6.1f %7.2f %6.0f %-10s %8.2f %7.2f A %7.0f%% %6.2f A %7.2f A" % (
            mode, vin, vout, il, f / 1e3, tl, L * 1e6, di, 100.0 * di / ICHG_MAX, ipk, irms))
    worst_pk = max(c[8] for c in cases)
    worst_rms = max(c[9] for c in cases)
    nom = [c for c in cases if c[4] == 400e3 and c[5] == "nominal L"]
    P("")
    P("1. SATURATION (SLUSE66A Equation 2, printed page 85: Isat at least ICHG plus half the ripple): the worst peak above is")
    P("   %.2f A against Isat %.1f A (804-1 p.1, typical, the 30 percent drop): %.0f percent of it. At that current the" % (worst_pk, ISAT, 100.0 * worst_pk / ISAT))
    P("   inductance has fallen to about %.0f percent of its zero-current value on 804-2's curve (INFERRED)." % (100.0 * EF.lfrac(PART, worst_pk)))
    P("2. RMS (804-1 p.1 note 6): the worst RMS above is %.2f A against 17.5 A (20 C rise) and 24.0 A (40 C rise), %.0f percent" % (worst_rms, 100.0 * worst_rms / IRMS20))
    P("   of the first; the copper loss there is at most %.2f W (DCR %.2f mOhm maximum). The rating is Coilcraft's reference" % (worst_rms ** 2 * DCR_MAX, DCR_MAX * 1e3))
    P("   figure on its own board; the rise on board A is a layout item.")
    P("3. RIPPLE (Equation 3 and the boost ripple, page 85; TI's guidance 20 to 40 percent of the maximum charge current): at")
    P("   400 kHz and the nominal inductance the ripple reads %.2f to %.2f A over the envelope, %.0f to %.0f percent of 7.936 A;" % (
        min(c[7] for c in nom), max(c[7] for c in nom), 100.0 * min(c[7] for c in nom) / ICHG_MAX, 100.0 * max(c[7] for c in nom) / ICHG_MAX))
    P("   at 340 kHz with the inductance 20 percent low it reads up to %.2f A. TI pairs 4.7 uH with 400 kHz (Table 9-4, page 27)." % max(c[7] for c in cases))
    i_acx = V_ACX / R16B
    P("4. A FAULT BOUND: the converter's input over-current comparator trips at %.0f mV across R16B, %.1f A of input current" % (V_ACX * 1e3, i_acx))
    P("   (8.5, VOCP_lim_ACX, page 15); in boost mode the inductor carries the input current, so at most %.1f A; in buck mode" % i_acx)
    P("   the inductor's average current is the input current times VIN over VOUT, at most %.1f A at 16.8 V into 12.0 V. Both are" % (i_acx * V_HI / V_LO))
    P("   under the typical Isat; Coilcraft prints no minimum Isat and calls the saturation soft (804-1 p.1), so this is not a")
    P("   bound on a part at its worst. The buck leg's low-side OCP (VOCP_lim_Q2, 150 mV across Q8B) depends on the FET's")
    P("   RDS(on) and is not used here.")
    P("CORE LOSS: not in any of the above. 804-1 p.1 prints none (\"Core and winding loss: See www.coilcraft.com/coreloss\"),")
    P("and no held Coilcraft document gives a figure or a loss model; see records/s119/README.md for the public search.")
    P("END.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
