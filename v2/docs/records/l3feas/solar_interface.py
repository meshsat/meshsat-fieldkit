#!/usr/bin/env python3
"""solar_interface.py: Option A(i)'s solar interface for Layer 3's decision L3-D05, derived rating by rating (stream l3feas,
MESHSAT-1357, 30 September 2026; the owner's review of the decision brief: "Approve topology separately from electrical
compliance. Pin the panel revision and datasheet; distinguish available array power, controlled converter input power,
cold open-circuit exposure, short-circuit/fault currents and string versus combined-feed protection. Provide the rating
derivation or an explicit engineering obligation rather than treating owner approval as verification." and "Do not
replace the held specification with a newer webpage silently.").

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built or measured. Every figure is MAKER (the held Renogy sheet,
read here from its text layer; the LT8705A sheet), NETLIST (board E's committed netlist), MODELED (the energy records) or
INFERRED (a method stated beside it). The figures Renogy's current US page shows are the owner's review's words, not a
held document: they are compared, never substituted.

Before any result it proves that its derivations reproduce a1solar's array_calc.out section 2 row for 2S2P (exit 4).

Second issue (CHECK-1 of 24942a5f, minors 6 and 7): the 60 V ceiling is labelled as the coordinator's safety extra-low-
voltage ceiling whose standard is not held, and the LT8705A's unused sense pins are cited on pp.11 and 12.

Run from the repository root:  python3 v2/docs/records/l3feas/solar_interface.py > v2/docs/records/l3feas/solar_interface.out
Deterministic. Exit 2: the held sheet is not the pinned file; 3: an input cannot be parsed; 4: a reproduction failed."""
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2", "ecad", "tools"))
import netlist_sexp as N  # noqa: E402

SHEET = ("v2/vendor/solar/renogy-rng-100db-h-flexible-100w-datasheet-2018.pdf", "8891821cf70f4124fdb1f02e2fbc7a4a0f4102c51f33ad39c2bfa32e6b60a29f")
ARRAY_OUT = "v2/docs/records/a1solar/array_calc.out"
R11_OUT = "v2/docs/records/r11dep/r11_dep.out"
HF_OUT = "v2/docs/records/l3feas/hf_wab.out"
NET_E = "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"
LT8705A = "v2/vendor/power/lt8705a.pdf"
NS, NP = 2, 2                     # the 2S2P wiring of a1solar's decision A1SOLAR-01
T_COLD, T_LIMIT, T_HOT = -20.0, -40.0, 70.0      # the envelope's in-use minimum cells, the panel's own lower limit, hot cells
EOC = 1.25                        # the edge-of-cloud factor, SunPower 524958 Rev F 3.0 (held back; a1solar ARRAY.md)
RATE = 1.25                       # the rating factor on that current (a1solar ARRAY.md 4; NEC 690-8 named, not held)
CEIL = 60.0                       # the coordinator's safety extra-low-voltage ceiling (a1solar README; no standard held)
FUSES = (10, 15, 20, 25, 30, 40)  # standard fuse steps used by a1solar (ARRAY.md 4)
REVIEW = {"voc": 24.4, "fuse": 15.0, "dims": (1093, 582)}   # the owner's review, 30 Sep 2026: Renogy's current US page (NOT held)


def refuse(code, msg):
    sys.stderr.write("solar_interface: %s; refusing\n" % msg)
    sys.exit(code)


def need(text, pat, what):
    m = re.search(pat, text, re.M)
    if not m:
        refuse(3, "%s not parsed" % what)
    return m


def head_equal(rel):
    text = open(os.path.join(TOP, rel), encoding="utf-8").read()
    head = subprocess.run(["git", "-C", TOP, "show", "HEAD:" + rel], capture_output=True, text=True).stdout
    if text != head:
        refuse(3, "%s differs from HEAD's" % rel)
    return text


def main():
    path = os.path.join(TOP, SHEET[0])
    if hashlib.sha256(open(path, "rb").read()).hexdigest() != SHEET[1]:
        refuse(2, "the held Renogy sheet is not the pinned file")
    txt = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True, check=True).stdout
    info = subprocess.run(["pdfinfo", "-isodates", "-rawdates", path], capture_output=True, text=True, check=True).stdout   # the file's own zone
    pages = int(need(info, r"Pages:\s+(\d+)", "pages").group(1))
    created = need(info, r"CreationDate:\s+(.+)$", "creation date").group(1).strip()
    modified = need(info, r"ModDate:\s+(.+)$", "modification date").group(1).strip()
    title = need(info, r"Title:\s+(.+)$", "title").group(1).strip()
    pmax = float(need(txt, r"Maximum Power at STC\*\s+(\d+) W", "Pmax").group(1))
    vmp = float(need(txt, r"Optimum Operating Voltage \(Vmp\)\s+([\d.]+) V", "Vmp").group(1))
    imp = float(need(txt, r"Optimum Operating Current \(Imp\)\s+([\d.]+) A", "Imp").group(1))
    voc = float(need(txt, r"Open Circuit Voltage \(Voc\)\s+([\d.]+) ?V", "Voc").group(1))
    isc = float(need(txt, r"Short Circuit Current \(Isc\)\s+([\d.]+) A", "Isc").group(1))
    vsys = float(need(txt, r"Maximum System Voltage\s+(\d+) VDC", "system voltage").group(1))
    fuse = float(need(txt, r"Maximum Series Fuse Rating\s+(\d+) A", "series fuse").group(1))
    dims = need(txt, r"Dimensions\s+.*?\((\d+) x (\d+) x (\d+) mm\)", "dimensions").groups()
    mass = need(txt, r"Weight\s+.*?\(([\d.]+) kg\)", "mass").group(1)
    cells = need(txt, r"Number of Cells\s+(\d+) \((\d+) x (\d+)\)", "cells").groups()
    b_p = float(need(txt, r"Temperature Coefficient of Pmax\s+(-?[\d.]+)%", "Pmax coefficient").group(1)) / 100.0
    b_v = float(need(txt, r"Temperature Coefficient of Voc\s+(-?[\d.]+)%", "Voc coefficient").group(1)) / 100.0
    a_i = float(need(txt, r"Temperature Coefficient of Isc\s+(-?[\d.]+)%", "Isc coefficient").group(1)) / 100.0
    noct = need(txt, r"\(NOCT\)\s+(\d+)±(\d+)", "NOCT").groups()
    trange = need(txt, r"Operating Module Temperature\s+(-\d+)ºC to \+(\d+)ºC", "operating range").groups()
    conn = need(txt, r"Rated Current\s+(\d+)A", "connector current").group(1)
    conn_v = need(txt, r"Maximum Voltage\s+(\d+)VDC", "connector voltage").group(1)
    cable = need(txt, r"Output Cables (\d+) AWG", "output cable").group(1)
    revmarks = sorted(set(re.findall(r"\b(?:Rev(?:ision)?\.?\s*[A-Z0-9]+|Version\s*[\d.]+|V\d+\.\d+)\b", txt)))

    # derivations, 2S2P
    voc_c = NS * voc * (1 + b_v * (T_COLD - 25.0))
    voc_l = NS * voc * (1 + b_v * (T_LIMIT - 25.0))
    voc_125 = NS * voc * EOC
    v_basis = max(voc_c, voc_125)
    isc_s_hot = isc * (1 + a_i * (T_HOT - 25.0))
    isc_s_eoc = isc_s_hot * EOC
    isc_a_hot, isc_a_eoc = NP * isc_s_hot, NP * isc_s_eoc
    i_rate = isc_a_eoc * RATE
    f2 = min(x for x in FUSES if x >= i_rate)
    backfeed = (NP - 1) * isc_s_eoc
    p_stc = NS * NP * pmax
    p_cold = p_stc * (1 + b_p * (T_COLD - 25.0))

    # reproduction against array_calc.out section 2 (REN100 2x2)
    ac = head_equal(ARRAY_OUT)
    row = need(ac, r"^\s+REN100\s+2x2\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "array_calc.out REN100 2x2")
    got = ["%d" % p_stc, "%.2f" % voc_c, "%.2f" % voc_125, "%.2f" % v_basis, "%.2f" % isc_a_hot, "%.2f" % isc_a_eoc, "%.2f" % i_rate, "%.2f" % backfeed]
    p_hot = float(need(ac, r"REN100\s+2x2\s+200 W at the hot Vmpp [\d.]+ V = [\d.]+ A; the array's own maximum at 1000 W/m2 and 70 C: ([\d.]+) W", "array_calc.out 5").group(1))
    voc_l_ac = float(need(ac, r"REN100\s+2x2\s+at -20 C\s+[\d.]+ V; at -40 C\s+([\d.]+) V", "array_calc.out 13").group(1))
    bad = sum(1 for a, b in zip(got, row.groups()) if a != b) + (0 if "%.2f" % voc_l == "%.2f" % voc_l_ac else 1)

    # the stage and the entry, from the netlist and the records
    e = N.load(os.path.join(TOP, NET_E))
    pa, ca = e["pins"], e["components"]
    u5 = {p: pa["U5"][p]["net"] for p in ("29", "30", "31", "32", "33", "34")}
    lt = " ".join(subprocess.run(["pdftotext", "-layout", "-f", "12", "-l", "12", os.path.join(TOP, LT8705A), "-"],
                                 capture_output=True, text=True, check=True).stdout.split())
    lt11 = " ".join(subprocess.run(["pdftotext", "-layout", "-f", "11", "-l", "11", os.path.join(TOP, LT8705A), "-"],
                                   capture_output=True, text=True, check=True).stdout.split())
    need(lt11, r"CSNOUT \(Pin 30/Pin 32\): The \(.\) Input to the Output Cur", "LT8705A p.11 CSNOUT")
    need(lt11, r"rent Monitor Amplifier\. Connect this pin to VOUT when not", "LT8705A p.11 CSNOUT's use")
    need(ac, r"60 V: the coordinator's safety-extra-low-voltage ceiling \(README of this folder\); the standard behind it is not held", "array_calc.out the 60 V ceiling")
    need(lt, r"CSPIN \(Pin 33/Pin 37\): The \(\+\) Input to the Input Cur", "LT8705A p.12 CSPIN")
    need(lt, r"rent Monitor Amplifier\. Connect this pin to VIN when not", "LT8705A p.12 CSPIN's use")
    need(lt, r"CSNIN \(Pin 32/Pin 36\)", "LT8705A p.12 CSNIN")
    no_sense = u5["32"] == u5["33"] == "PV_P" and u5["30"] == u5["31"] == "TRK_OUT"
    f2_net = {p: v["net"] for p, v in pa["F2"].items()}
    q2 = {p: pa["Q2"][p]["net"] for p in ("1", "5")}
    q6 = {p: pa["Q6"][p]["net"] for p in ("1", "5")}
    q3 = {p: pa["Q3"][p]["net"] for p in ("1", "5")}
    r11 = head_equal(R11_OUT)
    ms = need(r11, r"OUTPUT: ([\d.]+) W in service \([\d.]+ A at [\d.]+ V over [\d.]+\), ([\d.]+) W at the held maximum, ([\d.]+) W at the proposed maximum", "r11_dep.out the stage's output")
    st_serv, st_max = float(ms.group(1)), float(ms.group(3))
    mt = need(r11, r"buck current limit ([\d.]+) / ([\d.]+) / ([\d.]+) A \(VCS over R5", "r11_dep.out the tracker's limit")
    trk_max = float(mt.group(3))
    hf = head_equal(HF_OUT)
    mh = need(hf, r"The array's largest hour on the mean day is ([\d.]+) W \(TYP\) and ([\d.]+) W \(WAB\)", "hf_wab.out the mean day's largest hour")
    veh = 6.15    # the vehicle entry's LM5069 at its VCL maximum (gen_sch_e.py _VEH_T; r11_dep.out 4)

    o = []
    P = o.append
    P("OPTION A(i)'S SOLAR INTERFACE, RATING BY RATING (solar_interface.py, stream l3feas, MESHSAT-1357). PROTOTYPE DESIGN:")
    P("nothing bought, built or measured. MAKER = the held sheet's text layer; NETLIST = board E's committed netlist; MODELED")
    P("= the energy records; INFERRED = a method stated. The author's analysis, AI arithmetic; not a qualified review.")
    P("")
    P("0. REPRODUCTION: the derivations below reproduce a1solar's array_calc.out section 2 row REN100 2x2 and section 13's")
    P("   -40 C figure: %s" % ("yes" if bad == 0 else "NO (%d)" % bad))
    if bad:
        sys.stdout.write("\n".join(o) + "\n")
        refuse(4, "%d reproduction check(s) failed" % bad)
    P("")
    P("1. THE PANEL THE TREE HOLDS (MAKER, %s)" % SHEET[0])
    P("   sha256 %s, %d pages, title '%s'" % (SHEET[1], pages, title))
    P("   PDF metadata: created %s, modified %s; a retailer's copy (v2/vendor/sources.txt; the maker's download page did not" % (created, modified))
    P("   render to this host). Revision identifier printed on the sheet: %s" % (", ".join(revmarks) if revmarks else "NONE (no 'Rev', 'Revision' or 'Version' mark on either page)"))
    P("   p.2: Pmax %.0f W, Vmp %.1f V, Imp %.2f A, Voc %.1f V, Isc %.2f A; %s cells (%s x %s); maximum system voltage %.0f V DC;" % (
        pmax, vmp, imp, voc, isc, cells[0], cells[1], cells[2], vsys))
    P("     maximum series fuse rating %.0f A; %s x %s x %s mm, %s kg; Pmax %+.2f %%/K, Voc %+.2f %%/K, Isc %+.2f %%/K; NOCT %s +-%s C;" % (
        fuse, dims[0], dims[1], dims[2], mass, b_p * 100, b_v * 100, a_i * 100, noct[0], noct[1]))
    P("     operating %s to +%s C; connectors %s A, %s V DC; output cables %s AWG" % (trange[0], trange[1], conn, conn_v, cable))
    P("   THE REVISION IS NOT SETTLED BY THE HELD SHEET: it carries no revision mark. The owner's review reports Renogy's current US")
    P("   page for the family: Voc %.1f V, maximum series fuse %.0f A, %d x %d mm (not held; compared, not substituted)." % (
        REVIEW["voc"], REVIEW["fuse"], REVIEW["dims"][0], REVIEW["dims"][1]))
    rv_c = NS * REVIEW["voc"] * (1 + b_v * (T_COLD - 25.0))
    rv_l = NS * REVIEW["voc"] * (1 + b_v * (T_LIMIT - 25.0))
    rv_125 = NS * REVIEW["voc"] * EOC
    P("   If the kit's panels were that revision, 2S2P's open circuit would read %.2f V at -20 C cells, %.2f V at -40 C and %.2f V" % (
        rv_c, rv_l, rv_125))
    P("   by the 1.25 clause (INFERRED with the HELD sheet's %.2f %%/K: the current page's coefficient is not read here): %s the" % (
        b_v * 100, "OVER" if rv_125 > CEIL else "under"))
    P("   coordinator's %.0f V safety extra-low-voltage ceiling (array_calc.out 2: 'the standard behind it is not held'), where the" % CEIL)
    P("   held sheet gives %.2f V. Its Vmp, Imp and Isc are not in the review; the stage's fixed input point" % voc_125)
    P("   (R8, R9: 34.29 V, a1solar ARRAY.md 3) and its 0.990 ratio are derived from the held sheet's Vmp and would move with them")
    P("")
    P("2. AVAILABLE ARRAY POWER (2S2P, %d panels)" % (NS * NP))
    P("   at STC: %.0f W (MAKER, %d x %.0f W, no tolerance published)" % (p_stc, NS * NP, pmax))
    P("   at 1000 W/m2 and +70 C cells: %.1f W (MODELED, array_calc.out 5, the single-diode fit)" % p_hot)
    P("   at 1000 W/m2 and -20 C cells: %.1f W (INFERRED, the sheet's Pmax coefficient applied linearly over 45 K); with the" % p_cold)
    P("     edge-of-cloud factor %.2f on the irradiance, a bound of %.1f W for a transient (INFERRED)" % (EOC, p_cold * EOC))
    P("   on SC-37's mean day at 40/0, the largest hour into the stage: %s W (TYP) and %s W (WAB) (MODELED, hf_wab.out 4)" % (mh.group(1), mh.group(2)))
    P("")
    P("3. THE CONVERTER'S INPUT POWER: NOT A CONTROLLED LIMIT AS DRAWN")
    P("   the 200 W is the energy model's window on the stage's input (energy_two_pack.py node_power: min(panel, window))")
    P("   NETLIST: U5 LT8705A pins 30, 31 (CSNOUT, CSPOUT) on %s and 32, 33 (CSNIN, CSPIN) on %s, with no resistor between: %s" % (
        u5["30"], u5["32"], "the input and output current regulation is NOT used" if no_sense else "UNEXPECTED"))
    P("     (MAKER, 8705af pp.11 and 12: CSNOUT 'Connect this pin to VOUT when not in use', p.11; CSPIN 'Connect this pin to VIN")
    P("     when not in use', p.12). So the stage takes what its load asks, up to its own")
    P("     inductor current limit, from what the array gives")
    P("   what the load asks (r11dep, the front end's input is the stage's output): %.1f W out in service, %.1f W into the stage at" % (st_serv, st_serv / 0.93))
    P("     0.93 DECLARED; %.1f W out at the front end's highest permitted current (%.1f W in)" % (st_max, st_max / 0.93))
    P("   the stage's own ceiling: its buck valley limit at the maximum, %.1f A at TRK_OUT's 15.1 V: %.1f W out, %.1f W in (INFERRED:" % (
        trk_max, trk_max * 15.1, trk_max * 15.1 / 0.93))
    P("     the valley threshold taken as the average it passes; the maker notes it rises at higher duty, 8705af p.22)")
    P("   the stage's input is therefore min(the array's available power, the load's demand over the efficiency, its own ceiling):")
    P("   up to %.1f W with a load at the front end's maximum, against the model's 200 W (INFERRED)" % min(p_cold, st_max / 0.93))
    P("")
    P("4. COLD OPEN-CIRCUIT EXPOSURE (the string is two panels in series; the strings in parallel add no voltage)")
    P("   Voc %.1f V a panel: %.2f V at -20 C cells (the envelope's in-use minimum), %.2f V at -40 C (the panel's own limit)," % (voc, voc_c, voc_l))
    P("     %.2f V by the 1.25 clause on STC (SunPower 524958 Rev F 3.0, held back): the voltage basis %.2f V (INFERRED)" % (voc_125, v_basis))
    P("   against: the panel's %.0f V system voltage; the LT8705A's 80 V (8705af pp.2, 3); the coordinator's %.0f V ceiling (its standard" % (vsys, CEIL))
    P("     not held); board E's PV_P parts as")
    P("     generated (60 V FETs, 35 V and 50 V capacitors, a 28 V TVS, gen_sch_e.py; a1solar ARRAY.md 6, gated on REQ-016)")
    P("")
    P("5. SHORT-CIRCUIT AND FAULT CURRENTS (hot cells +70 C at 1000 W/m2; the edge-of-cloud factor %.2f)" % EOC)
    P("   a string: Isc %.2f A at STC, %.2f A hot, %.2f A with the factor; the array: %.2f A, %.2f A, %.2f A" % (
        isc, isc_s_hot, isc_s_eoc, NP * isc, isc_a_hot, isc_a_eoc))
    P("   (a) a short at the array's output, in the lead or at the entry: the array is a current source and delivers at most")
    P("       %.2f A; F2 never opens on it; every conductor from the array to the stage carries it continuously (INFERRED)" % isc_a_eoc)
    P("   (b) a fault inside one string: the other string back-feeds it with at most %.2f A (INFERRED)" % backfeed)
    P("   (c) a back-feed from the kit into the array (NETLIST topology): VIN_RAW -> Q2 (%s to %s, the ideal diode U4 LM74700-Q1," % (q2["5"], q2["1"]))
    P("       blocking) -> TRK_OUT -> Q6 M4 (%s to %s) -> L1 -> Q3 M1's body diode (%s to %s) -> PV_P -> F2 -> the array. It" % (
        q6["5"], q6["1"], q3["1"], q3["5"]))
    P("       needs Q2 or U4 failed (a single fault) while M4 conducts with VIN_RAW above the panel, and its sustained source is the")
    P("       vehicle entry, limited by its LM5069 at %.2f A unless that entry has failed too (INFERRED; the fault tree is owed)" % veh)
    P("")
    P("6. STRING VERSUS COMBINED-FEED PROTECTION")
    P("   the maker's maximum series fuse rating %.0f A (p.2), read as the current a module may carry in reverse (INFERRED: the usual" % fuse)
    P("     meaning; the applicable standard is not held)")
    P("   (b)'s %.2f A is under %.0f A: NO STRING FUSE is needed for faults inside the array (INFERRED; a1solar ARRAY.md 1 and 4)" % (backfeed, fuse))
    P("   F2 sits in the COMBINED feed (NETLIST: F2 between %s and %s). At %d A it exceeds one string's %.0f A, so F2 does not protect a" % (
        f2_net["1"], f2_net["2"], f2, fuse))
    P("     single string: with one string disconnected, a back-feed of (c) reaches the remaining string unfused up to F2's rating.")
    P("     (c) is bounded at %.2f A by the vehicle entry, under %.0f A, while that entry holds: the string's protection rests on (c)'s" % (veh, fuse))
    P("     fault tree, not on F2 (INFERRED)")
    P("   the current page's %.0f A equals the held sheet's: the review's figures do not move this row" % REVIEW["fuse"])
    P("")
    P("7. THE COMBINED-FEED FUSE, LEAD AND CONNECTOR")
    P("   current: %.2f x %.2f A = %.2f A, the standard step at or above it %d A (INFERRED; a1solar ARRAY.md 4)" % (RATE, isc_a_eoc, i_rate, f2))
    P("   voltage: at least %.2f V DC (section 4)" % v_basis)
    P("   interrupting rating: at or above the prospective fault from the kit side at that voltage; NOT DERIVED (the source is the")
    P("     vehicle through a failed entry, a figure no record holds)")
    P("   as generated (NETLIST): F2 '%s'; J_SOLAR '%s'" % (ca["F2"]["value"], ca["J_SOLAR"]["value"][:60]))
    P("   the lead, J_SOLAR, the wall's solar pair and F2's holder: at or above %d A at %.2f V (the conductor at or above the fuse that" % (f2, v_basis))
    P("     protects it)")
    P("")
    P("END. Derivations on the held sheet; nothing is measured, bought or chosen.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
