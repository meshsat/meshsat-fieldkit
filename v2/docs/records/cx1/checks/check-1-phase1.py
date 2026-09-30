#!/usr/bin/env python3
"""Phase 1 of the AI review of the cx1 candidate (finding I-03, IF-AB-POWER): the checker's own figures,
derived from the sources in the cx1 worktree BEFORE any candidate file was opened.

Reads (parsed, never grepped): both intent files and pcb_interfaces.yaml. Maker figures are typed in from the
held documents with their page (the pdftotext page of the held file, and the printed page where it differs).
Writes nothing but standard output.
"""
import hashlib, json, os, sys
import yaml

W = os.environ.get("CX1_WORKTREE", os.path.join(os.environ.get("WORKTREES", os.path.expanduser("~/worktrees/meshsat-fieldkit")), "cx1"))
A_INTENT = W + "/v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json"
B_INTENT = W + "/v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json"
D_INTENT = W + "/v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs-intent.json"
IFACES = W + "/v2/ecad/tools/pcb_interfaces.yaml"

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

for p in (A_INTENT, B_INTENT, D_INTENT, IFACES):
    print("input %s sha256 %s" % (p.replace(W + "/", ""), sha(p)))

a = json.load(open(A_INTENT)); b = json.load(open(B_INTENT)); d = json.load(open(D_INTENT))
_y = yaml.safe_load(open(IFACES)); ifc = _y["board_to_board"]["contracts"]["IF-AB-POWER"]
print("board A intent written %s; board B intent written %s; board D intent written %s" % (a["written"], b["written"], d["written"]))
print("contract title: %s" % ifc["title"])

# ---------------------------------------------------------------- maker figures (typed in, each with its page)
LM5176_VSNS_MV = (43.0, 50.0, 57.0)    # TI SNVSAI1D (June 2017, revised Aug 2021) 6.5 Electrical Characteristics, CONSTANT CURRENT LOOP, VSNS, PDF p.7; min/max over -40 to 125 C junction
LM5176_ISNS_S2_OHM = 0.006             # gen_sch_a.py:1006 isns="6m" (R35), stage S2 (U5)
LM5176_ISNS_SD_OHM = 0.006             # gen_sch_a.py:1015 isns="6m" (R43), stage SD (U7)
LM5176_ISNS_POE_OHM = 0.020            # gen_sch_a.py:1112 isns="20m" (R71), stage POE (U16)
AP64500_CONT_A = 5.0                   # Diodes DS41979 Rev. 5-2 p.1 "5A Continuous Output Current"
AP64500_IPEAK_LIMIT = (6.8, 8.0, 9.2)  # DS41979 Rev. 5-2 p.6 IPEAK_LIMIT HS Peak Current Limit (Note 8)
JST_VH_RATING_A_AWG16_STD = 10.0       # JST VH catalogue p.1 "Current rating: 10 A AC/DC *When using AWG #16 with the standard type header"
JST_VH_RATING_A_AWG18_SHROUDED = 7.0   # JST VH catalogue p.1 "7A AC/DC *When using AWG #18 with the shrouded type header"
JST_VH_CONTACT_MOHM_INITIAL = 10.0     # JST VH catalogue p.1 "Contact resistance: Initial value/ 10 mOhm max."
JST_VH_CONTACT_MOHM_AFTER = 20.0       # JST VH catalogue p.1 "After test/ 20 mOhm max."
JST_VH_MM2_AWG16 = 1.25                # JST VH catalogue p.2 contact table SVH-41T-P1.1 "#20 to #16 (0.5 to 1.25)" mm2
JST_VH_MM2_AWG18 = 0.83                # JST VH catalogue p.2 contact table SVH-21T-P1.1 "#22 to #18 (0.33 to 0.83)" mm2
RM520N_CONT_A = 3.0                    # Quectel RM520N-GL HD v1.0 (2022-07-15) 3.3.1, PDF p.28 (printed 27): "continuous current capability of the power supply is 3.0 A at least"
RM520N_PEAK_A = 4.0                    # Quectel RM520N series HD v1.1 (2023-03-16) 3.3.1, PDF p.30 (printed 29): "peak current capability of the power supply is 4 A at least" (NOT in the -GL v1.0 text)
RM520N_MAX_AVG_MA = 1512.0             # RM520N-GL HD v1.0 Table 37, PDF p.67 (printed 66): LTE CA, the largest averaged consumption row
CM5_OPERATION_A = 0.9                  # CM5 datasheet release 3, section 3.3 PDF p.16 (printed 15) and Table 9 PDF p.28 (printed 27): Iload 900 mA typical, no maximum
CM5_IDLE_A = 0.4
CM5_INPUT_CAPABILITY_A = 5.0           # CM5 datasheet 1.3 PDF p.6: "Single 5 V power input with USB power delivery support for up to 5 A at 5 V" (an input capability, not a draw)
RHO_CU = 1.72e-8                       # ohm m at 20 C: v2/ecad/tools/dc_drop.py:23 (the tree's own constant)
LEAD_M_EACH_WAY = 0.150                # ASSEMBLY.md section 4 rows 132 to 134: 150 mm
V_SLOT = 5.1; V_DEV = 5.0; V_POE = 54.0
EFF_CARD_BUCK = 0.88                   # gen_sch_b.py:170 efficiency=0.88 (a project floor; DS41979 Fig. 4 is VIN 12 V, not plotted at 5 V)
EFF_CORE_BUCK = 0.85
V_CARD2 = 3.456                        # gen_sch_b.py:169 (R202 33.2 k)

def lm_limits(r_ohm):
    return tuple(mv / 1000.0 / r_ohm for mv in LM5176_VSNS_MV)

# ---------------------------------------------------------------- what each end declares
print("\n== declarations (parsed from the intent files)")
for rail in ("+5V_S1", "+5V_S2", "+5V_S3", "+5V_DEV", "+54V_POE"):
    ra, rb = a["rails"][rail], b["rails"][rail]
    print("%-9s A: typ %.2f peak %.2f loads %s | B: typ %.2f peak %.2f loads-sum %.3f (%d loads)" % (
        rail, ra["amps_typ"], ra["amps_peak"], ra["loads"], rb["amps_typ"], rb["amps_peak"], sum(rb["loads"].values()), len(rb["loads"])))

# ---------------------------------------------------------------- +5V_S2 behind board B's end
print("\n== +5V_S2 loads behind board B (PS-ALLTX: slot loaded, 5G module transmitting)")
def at_5v1(i_out, v_out, eff):
    return i_out * v_out / eff / V_SLOT
card_typ = at_5v1(RM520N_CONT_A, V_CARD2, EFF_CARD_BUCK)
card_peak = at_5v1(RM520N_PEAK_A, V_CARD2, EFF_CARD_BUCK)
card_avgmax = at_5v1(RM520N_MAX_AVG_MA / 1000.0, V_CARD2, EFF_CARD_BUCK)
s2b_typ = at_5v1(b["rails"]["+3V3_S2B"]["amps_typ"], 3.3, EFF_CARD_BUCK)
s2b_peak = at_5v1(b["rails"]["+3V3_S2B"]["amps_peak"], 3.3, EFF_CARD_BUCK)
core_typ = at_5v1(b["rails"]["+1V0_S2"]["amps_typ"], 1.0, EFF_CORE_BUCK)
core_peak = at_5v1(b["rails"]["+1V0_S2"]["amps_peak"], 1.0, EFF_CORE_BUCK)
fan = b["rails"]["+5V_S2"]["loads"]["J_FAN2"]; gate = b["rails"]["+5V_S2"]["loads"]["U216"]
cm5_alloc = b["rails"]["+5V_S2"]["loads"]["U31A"]
print("  5G card buck U203 at 3.456 V / 0.88: 3.0 A cont -> %.3f A; 4 A peak -> %.3f A; 1.512 A max averaged (Table 37) -> %.3f A" % (card_typ, card_peak, card_avgmax))
print("  NVMe+switch 3.3 V buck U204: typ %.3f A, peak %.3f A (project allowance 0.9/1.8 A at 3.3 V)" % (s2b_typ, s2b_peak))
print("  1.0 V core buck U205: typ %.3f A, peak %.3f A (project allowance 0.8/1.2 A)" % (core_typ, core_peak))
print("  CM5 module: maker typical %.2f A (no maximum); project allowance %.2f A; fan %.2f A (TBD per contract line 1057); gate %.3f A" % (CM5_OPERATION_A, cm5_alloc, fan, gate))
s2_typ = CM5_OPERATION_A + card_typ + s2b_typ + core_typ + fan + gate
s2_coinc = cm5_alloc + card_peak + s2b_typ + core_typ + fan + gate
s2_allpeak = cm5_alloc + card_peak + s2b_peak + core_peak + fan + gate
s2_maxavg = CM5_OPERATION_A + card_avgmax + s2b_typ + core_typ + fan + gate
print("  SUM typical (CM5 0.9, card 3.0 A cont)         = %.3f A  (board B declares typ %.2f)" % (s2_typ, b["rails"]["+5V_S2"]["amps_typ"]))
print("  SUM coincident (CM5 1.6 alloc, card 4 A peak)  = %.3f A  (the contract's 5.63 A)" % s2_coinc)
print("  SUM every branch at its peak or allowance      = %.3f A  (a bound)" % s2_allpeak)
print("  SUM with the card at Quectel's largest average = %.3f A" % s2_maxavg)
lim = lm_limits(LM5176_ISNS_S2_OHM)
print("  board A limit: LM5176 U5 average current loop, VSNS %s mV / R35 %.0f mOhm = %.3f / %.3f / %.3f A (min/typ/max)" % (LM5176_VSNS_MV, LM5176_ISNS_S2_OHM * 1e3, *lim))
print("  margins to the MINIMUM limit: coincident %.3f A; all-peak %.3f A; to the VH 10 A: all-peak %.3f A" % (lim[0] - s2_coinc, lim[0] - s2_allpeak, JST_VH_RATING_A_AWG16_STD - s2_allpeak))
print("  board A's declaration 2.5/5.0 against B's derivation: typ short by %.2f A, peak short by %.2f A (coincident) / %.2f A (all-peak)" % (
    s2_typ - a["rails"]["+5V_S2"]["amps_typ"], s2_coinc - a["rails"]["+5V_S2"]["amps_peak"], s2_allpeak - a["rails"]["+5V_S2"]["amps_peak"]))
print("  board B's own declared peak %.2f is BELOW its own coincident figure %.3f" % (b["rails"]["+5V_S2"]["amps_peak"], s2_coinc))

# ---------------------------------------------------------------- +5V_S1 / +5V_S3 (AP64500 stages, WiFi cards)
print("\n== +5V_S1 and +5V_S3 (AP64500 stages; ends agree 2.5/5.0)")
card13_max = 9.1 / EFF_CARD_BUCK / V_SLOT   # AsiaRF 9 to 9.1 W maximum (POWER-THERMAL.md PWR-F01, VERIFIED there; the AsiaRF sheet is held under v2/vendor/wifi/, not re-read here)
s1_plan = cm5_alloc + card13_max + s2b_typ + core_typ + fan + gate
s1_allpeak = cm5_alloc + card13_max + s2b_peak + core_peak + fan + gate
print("  WiFi card at AsiaRF's 9.1 W max through 0.88 at 5.1 V = %.3f A; slot sum with CM5 1.6 alloc: %.3f A (POWER-THERMAL PS-ALLTX PLAN 4.65 A); all-peak %.3f A" % (card13_max, s1_plan, s1_allpeak))
print("  limit: AP64500 %.1f A continuous rating (DS41979 p.1); HS peak limit %s A (p.6). Margin of the declared 5.0 A peak to the 5 A rating: %.2f A" % (AP64500_CONT_A, AP64500_IPEAK_LIMIT, AP64500_CONT_A - 5.0))
print("  board B's declared loads sum %.3f A against the declared typical 2.5 A on both ends" % sum(b["rails"]["+5V_S1"]["loads"].values()))

# ---------------------------------------------------------------- +5V_DEV
print("\n== +5V_DEV")
rb_dev = b["rails"]["+5V_DEV"]; ra_dev = a["rails"]["+5V_DEV"]; rd = d["rails"]["+5V_D8"]
print("  board B loads (declared, apportioned): %s" % rb_dev["loads"])
print("  board B loads sum %.3f A; B declares typ %.2f peak %.2f arriving" % (sum(rb_dev["loads"].values()), rb_dev["amps_typ"], rb_dev["amps_peak"]))
print("  board A: typ %.2f peak %.2f, loads %s (J_5V_DEV share %.2f)" % (ra_dev["amps_typ"], ra_dev["amps_peak"], ra_dev["loads"], ra_dev["loads"]["J_5V_DEV"]))
print("  board D's +5V_D8 (behind A's eFuse U23, ILM 2.0 A): typ %.2f peak %.2f, loads sum %.3f" % (rd["amps_typ"], rd["amps_peak"], sum(rd["loads"].values())))
wall_ilm = 0.89  # gen_sch_a.py:1533 U32 "1k 1% (ILM: 0.89 A)"
lim_sd = lm_limits(LM5176_ISNS_SD_OHM)
print("  board A limit: LM5176 U7, VSNS / R43 %.0f mOhm = %.3f / %.3f / %.3f A" % (LM5176_ISNS_SD_OHM * 1e3, *lim_sd))
typ_recon = rb_dev["amps_typ"] + rd["amps_typ"] + ra_dev["loads"]["U32"]
peak_declared_sum = rb_dev["amps_peak"] + rd["amps_peak"] + wall_ilm
peak_declared_sum_dtyp = rb_dev["amps_peak"] + rd["amps_typ"] + wall_ilm
print("  converter sum at the ends' TYPICALS (B 3.8 + D 1.0 + wall 0.3) = %.2f A against A's declared typ %.2f" % (typ_recon, ra_dev["amps_typ"]))
print("  converter sum at the ends' PEAKS (B 6.0 + D 2.0 eFuse ILM + wall 0.89 ILM) = %.2f A: %.2f A OVER the minimum limit %.3f (a bound: two of the three are protection limits)" % (peak_declared_sum, peak_declared_sum - lim_sd[0], lim_sd[0]))
print("  converter sum with D at its declared peak 2.0 and the wall port off = %.2f; with D typical 1.0 and wall 0.89 = %.2f (A's declared 6.9 = 6.0 + 0.9, D8 at 0)" % (rb_dev["amps_peak"] + rd["amps_peak"], peak_declared_sum_dtyp))
print("  POWER-THERMAL.md line 709: PS-ALLTX +5V_DEV PLAN 5.89 A, HIGH 7.8 A: HIGH exceeds the 7.167 A minimum by %.2f A (the page says so itself)" % (7.8 - lim_sd[0]))
print("  lead disagreement: A apportions %.2f A to J_5V_DEV, B declares %.2f A typical arriving: %.2f A apart" % (ra_dev["loads"]["J_5V_DEV"], rb_dev["amps_typ"], rb_dev["amps_typ"] - ra_dev["loads"]["J_5V_DEV"]))

# ---------------------------------------------------------------- +54V_POE
print("\n== +54V_POE")
rb_poe = b["rails"]["+54V_POE"]; ra_poe = a["rails"]["+54V_POE"]
lim_poe = lm_limits(LM5176_ISNS_POE_OHM)
print("  ends: A typ %.2f peak %.2f; B typ %.2f peak %.2f, loads %s" % (ra_poe["amps_typ"], ra_poe["amps_peak"], rb_poe["amps_typ"], rb_poe["amps_peak"], rb_poe["loads"]))
print("  board A limit: LM5176 U16 boost, VSNS / R71 %.0f mOhm = %.3f / %.3f / %.3f A; margin at 0.6 A: %.2f A" % (LM5176_ISNS_POE_OHM * 1e3, *lim_poe, lim_poe[0] - 0.6))
print("  in PS-ALLTX the rail is OFF by hardware (POE_EN = POE_SW_EN AND OUTLET_OK, S-14): 0 A in the named mode")
print("  lead 18 AWG (ASSEMBLY row 134): the catalogue's 10 A is stated for AWG 16 on the standard header and 7 A for AWG 18 on the SHROUDED header; no figure is stated for AWG 18 on the standard header B2P-VH that both boards fit")

# ---------------------------------------------------------------- lead pair drops
print("\n== lead pair drop, 150 mm each way (300 mm of conductor), rho_cu %.2e ohm m (dc_drop.py), areas from the JST catalogue p.2" % RHO_CU)
for awg, mm2 in (("16", JST_VH_MM2_AWG16), ("18", JST_VH_MM2_AWG18)):
    r_wire = RHO_CU * 2 * LEAD_M_EACH_WAY / (mm2 * 1e-6)
    print("  AWG %s (%.2f mm2): wire loop %.3f mOhm" % (awg, mm2, r_wire * 1e3))
    for i in (2.5, 4.2, 5.0, 5.63, 6.38, 7.167):
        v_wire = r_wire * i
        v_c_init = 4 * JST_VH_CONTACT_MOHM_INITIAL / 1e3 * i
        v_c_after = 4 * JST_VH_CONTACT_MOHM_AFTER / 1e3 * i
        print("    at %.3f A: wire %.1f mV (%.2f %% of 5.1 V); four VH contacts at the 10 mOhm initial max %.0f mV (%.2f %%), at the 20 mOhm after-test max %.0f mV (%.2f %%)" % (
            i, v_wire * 1e3, 100 * v_wire / V_SLOT, v_c_init * 1e3, 100 * v_c_init / V_SLOT, v_c_after * 1e3, 100 * v_c_after / V_SLOT))
# the ASTM B258 area for comparison (formula, not a held document)
for n in (16, 18):
    d_mm = 0.127 * 92 ** ((36 - n) / 39.0)
    print("  ASTM B258 formula (not held): AWG %d diameter %.3f mm, area %.3f mm2" % (n, d_mm, 3.14159265 * d_mm ** 2 / 4))
print("  the contract's budget: 2 percent of 5.1 V = %.0f mV, shares A 0.5 point + B 1.5 points = 2.0 points: NO share for the lead and its four contacts" % (0.02 * V_SLOT * 1e3))

# Filing note (scrub, 30 September 2026, MESHSAT-1357): 1 path in this check is derived from an environment variable with a default (`$CX1_WORKTREE`) under the owner's rule that public files carry no internal host names, user paths or addresses; v2/docs/records/scrub/MAP.md lists each by line and token class. No other byte of the check changed but the import of os the derivation needs; the check as filed is in the repository's history at commit 8fec0733 and before.
