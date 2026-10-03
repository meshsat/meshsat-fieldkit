#!/usr/bin/env python3
"""l5pwr_contracts.py: Layer 5's power pass, read back (MESHSAT-1357, set 27, 3 October 2026).

Reads the three contract files Layer 5 owns (pcb_interfaces.yaml, HW-FW-CONTRACT.md, PANEL.md) and the Layer 4 records the pass
drew on, and prints the table L5-POWER-CONTRACTS.md carries: for every entry the contract and field written, the text written (an
excerpt, verbatim), the Layer 4 source that prints its figures, its mark (MAKER, INFERRED, MODELED, PROVISIONAL, RULE; DRAFTED where
the figure is true of a release-guarded draft no generator carries), its invalidation trigger and the Layer 5 criterion (5.x) it
moves. It REFUSES (exit 3) when an excerpt is not in its target or a cited figure is not printed by a cited source, so the table
cannot drift from the files. Every file read is pinned by sha256 in section 0; regen_out.py binds the output to them. Run from the
repository root or anywhere: `python3 v2/docs/records/l5pwr/l5pwr_contracts.py` (a second at most; stdlib only). Nothing here is
measured: it is a check of text against text."""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))

TARGETS = {"yaml": "v2/ecad/tools/pcb_interfaces.yaml", "hwfw": "v2/docs/HW-FW-CONTRACT.md", "panel": "v2/docs/PANEL.md"}
SOURCES = {
    "l4e9md": "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md",
    "l4e9out": "v2/docs/records/l4e9/l4e9_power_path.out",
    "reg": "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md",
    "hand": "v2/docs/records/l4e9/LAYER5-HANDOVER.md",
    "l4e11md": "v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md",
    "l4e11out": "v2/docs/records/l4e11/l4e11_power.out",
    "l4e11entry": "v2/docs/records/l4e11/apply_gen_sch_e_entry.py",
    "l4e12md": "v2/docs/records/l4e12/L4E12-ELECTRONICS-THERMAL.md",
    "l4e13md": "v2/docs/records/l4e13/L4E13-PANEL.md",
    "l4e4md": "v2/docs/records/l4e4/L4E4-CURRENT-LIMITS.md",
    "l4e7md": "v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md",
}
CRITERIA = {
    "5.2": "every interface owned at both ends with its connector",
    "5.4": "electrical levels stated per interface",
    "5.5": "power capacity of each power interface with margin",
    "5.6": "sequencing across interfaces",
    "5.7": "reset, default and cable-out states for every control line",
    "5.11": "firmware obligations affecting hardware explicit",
    "5.13": "interface contracts consistent with the tree",
}
# What this pass moves on each criterion, as Layer 5 reads it (the handover page's status is the integrator's to set).
CRITERIA_STATE = {
    "5.2": "PARTLY, further: the four first-twelve contracts the power results touch (IF-AE-DOCK, IF-PE-PACK, IF-AB-POWER, IF-EXT-USB) "
           "carry every pass-2 field (hc5's check_contract_fields.py --all: 'carries every field'); eight of the first twelve still lack "
           "them; the IDC headers' MPNs (EQ-21) unchanged",
    "5.4": "PARTLY, further: the power interfaces' levels stated with their Layer 4 basis and marks (IF-EXT-DC both inputs, IF-AE-DOCK "
           "VIN_RAW and VSYS_DOCK, IF-PE-PACK, IF-EXT-USB, IF-E-FANS); the kit I2C bus's three segments still owed (SC-59)",
    "5.5": "PARTLY, further: IF-EXT-DC's currents against the breaker, the fuses and the interconnect with their margins; IF-AE-DOCK's "
           "in-service and fault currents against the 9 A pins and pin 1 against the 813 under U42; the outlet's trip against the 3 A "
           "contracts and the 5 A receptacle; the PoE monitor's scale; open: I-03's PS-ALLTX, E5's targets and the ground share, the "
           "ribbon and SMP-MAX ratings, the 813's pulse capability (L4-F03)",
    "5.6": "OPEN to PARTLY: L4-E9 section 4's source changes, startup, shutdown and faults written as sequencing fields (IF-EXT-DC, "
           "IF-AE-DOCK, IF-PE-PACK, IF-E-FANS, IF-A-HEAT), the fans' start stagger (FW-E11), the shedding sequence (FW-A21), the boot "
           "writes (FW-A23) and the power lines' table (board_to_board.power_line_states); the SLOT_EN hold is still in no generator "
           "(OWED, Layer 8), so the item named at H2 stays open",
    "5.7": "PARTLY, further: every power line of L4-E9 section 4 has its reset, default and cable-out state and the firmware row that "
           "drives it (power_line_states; the contracts' default_state and cable_out_states); EQ-25 unchanged",
    "5.11": "PARTLY, further: FW-A19 to FW-A23, FW-C15, FW-E11 to FW-E13 added, FW-A09, FW-A14, FW-A16 and FW-C08 restated, PANEL.md "
            "section 10 restated, V-A11, V-C15 and V-E11 to V-E16 defined; the reduced-mode duties of layer 2's m13 still owed",
    "5.13": "PARTLY: the contracts state the drawn board first and every draft as DRAFTED with its register row, so they agree with the "
            "committed netlists today and name what changes when the drafts apply; check_contracts.py reads PASS 99 of 99 unchanged; "
            "the edit dates every interfaces.py reading (CONFIG_INPUTS), so their re-take on every board is owed, as after H2",
}

# id | contract | field | target | text written (verbatim excerpt) | sources (keys) | where in the source | figures | mark | trigger | criteria
T = []


def row(i, c, f, tg, tx, src, where, figs, mark, trig, crit):
    T.append(dict(id=i, contract=c, field=f, target=tg, text=tx, sources=src, where=where, figures=figs, mark=mark, trigger=trig, criteria=crit))


row("LH-01a", "IF-EXT-DC", "levels (DC)", "yaml",
    "per source at VBAT at the plug, the losses hot: 9 V 29.09 to 42.52 W, 12 V 32.22 to 47.72 W, 24 V 69.97 to 90.81 W, 36 V 84.55 to 99.64 W (INFERRED, U3 0.9733)",
    ["l4e11md"], "3h, the source envelope at the plug", ["29.09", "42.52", "32.22", "47.72", "69.97", "90.81", "84.55", "99.64", "0.9733"],
    "INFERRED; PROVISIONAL (REQ-015 at 9.00 V a CONDITIONAL CANDIDATE)",
    "E11-06: P1 over 20.51 W or the front end under 0.88021 at a 9.00 V plug; E11-09 (the knee drawn); E11-23 (the warm-up time)", ["5.4"])
row("LH-01b", "IF-EXT-DC", "current.dc", "yaml",
    "in service at most 5.983 A from a 9.00 V plug (VIN_RAW 8.148 V), 6.4 percent under the breaker's lowest 6.364 A",
    ["l4e9md"], "1d, row IF-05 and the stages' summary", ["5.983", "8.148", "6.4 %", "6.364", "0.88021"],
    "INFERRED (the breaker's rows MAKER, SLUSEE5E); DRAFTED R-123", "E11-06's measurement of the front end's efficiency at the operating point", ["5.5"])
row("LH-01c", "IF-EXT-DC", "protection (the selected entry)", "yaml",
    "UVLO on at 7.87 / 8.14 / 8.44 V and off at 7.46 / 7.66 / 7.95 V of DC_P; OV off above 39.6 / 40.36 / 41.22 V, clear of CS101's 38.83 V at 36 V and under D10's 44.4 V",
    ["l4e9md", "hand"], "1d rows IF-04 and IF-05, 4a, 4e; LH-01",
    ["7.87 / 8.14 / 8.44", "7.46 / 7.66 / 7.95", "39.6 / 40.36 / 41.22", "38.83", "44.4", "6.364 / 6.8 / 7.136", "0.247 / 0.37 / 0.49",
     "10.36 / 12.04 / 13.87", "2.08 uH", "66.15", "0997010.WXN", "900 A"],
    "MAKER (SLUSEE5E rows), INFERRED; DRAFTED R-123, R-17, R-18; PROVISIONAL (the hard short, D-06)",
    "the loop's inductance under 2.08 uH for a hard short in service (R-134, OPEN); D-06's makers' installed and short-time ratings and F1's clearing I2t (R-113, R-115, R-129 to R-132)",
    ["5.4", "5.5"])
row("LH-01d", "IF-EXT-DC", "tbd (the interconnect)", "yaml",
    "the loop read four-wire at 58.51 to 64.21 mOhm on every assembly (R-130)", ["reg"], "R-130", ["58.51", "64.21"],
    "INFERRED; PROVISIONAL", "R-113, R-115, R-129 to R-132 filed", ["5.5"])
row("LH-02a", "IF-EXT-DC", "levels (solar)", "yaml",
    "Vm20 + U_V at most 25.000 V at -20 C and 1000 W/m2, Voc25 20.315 to 22.156 V for its curve shape",
    ["l4e9md", "l4e13md"], "1d rows IF-01 and IF-02; L4E13-PANEL.md (PANEL-ACC, the conditioned hold)",
    ["25.000", "20.315", "22.156", "17.593", "16.970", "18.221", "16.420", "18.813", "31.6k", "2.5485", "2.9318", "44.84", "53.42", "3.0468",
     "3.7408", "93.5521", "168.8", "22.0 mA", "73.3436"],
    "MODELED (L4-E7R); PROVISIONAL (PANEL-ACC, no unit accepted; G_CM and the VIN+ bias)",
    "PANEL-ACC's measurement of the one unit (R-35); the makers' answers on G_CM and U18's VIN+ bias (R-101)", ["5.4"])
row("LH-02b", "IF-EXT-DC", "current.solar", "yaml",
    "in operation at most 3.987 A (PANEL-ACC A-3(a), INFERRED), the conservative bound over L4-E7R's regulation (RIMON_IN 31.6k, 2.5485 A nominal, at most 2.9337 A at 25 V)",
    ["l4e9md", "l4e13md"], "1d row IF-01; L4E13-PANEL.md A-3", ["3.987", "2.9337", "8.1817", "1.25", "10 A"],
    "INFERRED (the 1.25 factor MAKER); PROVISIONAL", "R-29 (the lead's gauge named by Layer 7); R-148 (A-3(c))", ["5.5"])
row("LH-02c", "IF-EXT-DC", "tbd (A-3(c))", "yaml",
    "J_SOLAR and PV_IN carry 13.82 A at the design level 2111.4 W/m2", ["reg"], "R-148", ["13.82", "2111.4"],
    "INFERRED (a COMPONENT_LIMITATION); PROVISIONAL", "R-148: a rating of at least 13.82 A or a bench row before the panel is accepted", ["5.5"])
row("LH-02d", "IF-EXT-DC", "protection (the solar stage)", "yaml",
    "the INB filter, five 100 nF C0G across R66 8.45k (3.960 to 4.496 ms); SWEN off by default below 2.662 V on TRK_LDO33; a response inside 1.087 ms after the filter's 0.4205 J held charge",
    ["l4e9md"], "1d rows IF-01 and IF-02, 4e", ["8.45k", "3.960", "4.496", "2.662", "1.087", "0.4205", "0.0585", "0.1130", "2.51"],
    "MODELED (L4-E7R); DRAFTED R-12, R-19 to R-21, R-98; PROVISIONAL", "the loop's typical rows (break-even 2.51 times), the bulk's temperature and the bank's pulse capability: M2 (R-122)", ["5.4"])
row("S27-B6", "IF-EXT-DC", "protection (the guard already on)", "yaml",
    "every rating with its margin only from a source loop of at least 3.30 uH (U5 0.2396 V of +-0.240 V, a DESIGN TARGET), NOT under it (at 1.00 uH U5 0.5287 V)",
    ["l4e9md"], "4e (the guard-on row), 8a D-10", ["3.30 uH", "0.2396", "0.240", "1.00 uH", "0.5287", "28.55", "31.06", "27.07", "60.3", "11.4 us"],
    "MODELED (L4-E7 round 2); DRAFTED R-173; PROVISIONAL, NOT CLOSED",
    "B6-ENG-1: R-180 (the loop bounded and measured), R-186 (Analog Devices' answer on a sense-pin filter) or R-187 (the sense moved); L4-E7's round 3 on B6 is running and re-reads this sentence", ["5.4"])
row("LH-03a", "IF-AE-DOCK", "vin_raw.voltage", "yaml",
    "solar 7.378 V (the corrected knee's certain HIZ, L4-E9 R-03, a specification) to 30.15 V (the tracker's raised ceiling, R10 232 k; L4-E5, DRAFTED); vehicle 9 to 36 V at the plug (VIN_RAW 8.148 V at 5.983 A from a 9.00 V plug; INFERRED); at most 41.22 V",
    ["l4e9md"], "1d row IF-06", ["7.378", "30.15", "8.148", "5.983", "41.22", "43.18", "64.5"],
    "INFERRED; R-03 a specification; DRAFTED R-03, R-123", "R-03's network drawn to the knee (Layer 8); the OV maximum follows R-123's parts", ["5.4"])
row("LH-03b", "IF-AE-DOCK", "vin_raw.in_service", "yaml",
    "fault current at most 11.65 A at R11 8 mOhm and R12 12 mOhm (13.315 A at 7 mOhm), inside the declared 14.10 A and the four 9 A pins (3.88 A each with one open)",
    ["l4e9md", "hand"], "1d rows IF-06 and IF-07; LH-03 (the 3.88 A with one pin open)", ["11.65", "13.315", "14.10", "3.88", "4.22"],
    "MODELED; R11 and R12 DRAFTED R-04, R-01", "R11's 7 mOhm fallback (V-A07) moves the fault bound to 13.315 A, still inside 14.10 A", ["5.5"])
row("LH-03c", "IF-AE-DOCK", "vin_raw.properties", "yaml",
    "U34's restart guard falls at 6.754 to 7.139 V (R14 76.8k, L4-E9 R-124, DRAFTED), at least 0.1 V under the knee's certain HIZ 7.378 V; as drawn it falls at up to 8.309 V",
    ["l4e9md"], "1d row IF-07, 4a", ["6.754", "7.139", "76.8k", "8.309", "7.378"],
    "INFERRED; DRAFTED R-124", "R-124's fitted parts: the guard's fall read on the regenerated board", ["5.7"])
row("LH-04a", "IF-AE-DOCK pack_pins; IF-PE-PACK power", "charge", "yaml",
    "at most 3.0 A (FW-A02; REQ-075 3.06 A), under the gauge's OCC 5 A", ["l4e9md"], "1d row IF-10", ["3.0 A", "3.06", "OCC 5 A"],
    "MAKER (the gauge's OCC), INFERRED", "FW-A02's setting; R-28 re-derives it at bring-up", ["5.5"])
row("LH-04b", "IF-AE-DOCK pack_pins; IF-PE-PACK power", "service", "yaml",
    "PS-ALLTX's 18 A at an 11.48 V stack and OCD1's 20 A below 10.42 V (pwr_budget.out D-11 line; MODELED)", ["l4e9md", "hand"],
    "1d row IF-10; LH-04", ["11.48", "10.42", "PWR-F12"], "MODELED; PROVISIONAL", "PWR-F12 (FEA-004): the chain's short-time rating at 18 A and F2 near +60 C", ["5.5"])
row("S27-01", "IF-AE-DOCK", "pin1_vsys_dock (the new row of set 27)", "yaml",
    "U42's I(OL) 1.4713 to 1.8018 A at R(ILIM) 11.0 kOhm 0.1 percent", ["l4e11md", "l4e11out"], "16e, 17a; out 16 and 17",
    ["1.4713", "1.8018", "11.0 kOhm", "0.1486", "9.539", "11.905", "202 ms", "500 to 800 ms", "566 A", "4.5 us", "41.1 V", "20 nH", "1.7 mA", "0.1408",
     "2.238", "2.406", "79.3", "28.6"],
    "INFERRED from MAKER rows (SLVSET9G); DRAFTED R-157, R-177, R-178, R-181; PROVISIONAL (L4-F03: remedy drafted, qualification open)",
    "E11-38 (R-184): a limit read outside 1.471 to 1.802 A, the hard short's cases, the 813's resistance after them; E11-35 (R-179): a fan or U12 current over 1.471 A",
    ["5.2", "5.5", "5.7"])
row("S27-02a", "IF-AE-DOCK pin1_vsys_dock; IF-E-FANS sequencing", "the fans' start rule", "yaml",
    "both fans together at most 0.3356 A each, one at a time at most 0.5713 A (the other running at 0.1 A), VSYS_E at the least limit at least 9.494 V at the supplement floor",
    ["l4e11md", "l4e11out"], "17a; out 17", ["0.3356", "0.5713", "0.1 A", "9.494", "1.471"],
    "INFERRED; DRAFTED R-177, R-181; PROVISIONAL", "a fan named whose start exceeds 0.5713 A (E11-35, R-179); U42's limit read outside its band (E11-38)", ["5.6", "5.11"])
row("S27-02b", "FW-E11", "the fans' start stagger as a firmware row", "hwfw",
    "Start the mixer fans one at a time, each with a PWM ramp, never both within 1 s and never while U12 starts (E11-39, R-188)",
    ["l4e11out", "reg"], "out 17 (E11-39); R-188", ["0.5713", "1.471", "PWM ramp"],
    "RULE (L4-E11 17a, SESSION); DRAFTED R-177, R-181; PROVISIONAL",
    "a fan named whose start exceeds 0.5713 A (E11-35, R-179); U42's limit read outside 1.471 to 1.802 A (E11-38, R-184)", ["5.6", "5.11"])
row("S27-03", "V-E16 (IF-EXT-DC bench)", "R-176 rows 1 to 6 where they bind the solar port", "hwfw",
    "(5) Q13's leakage at the hot end, under 32.1 uA; (6) no short-circuit trip with C126 at 330 pF in operation and under CS116 (R-174)",
    ["reg"], "R-176", ["28.55 to 31.06", "27.07", "75 V", "0.240", "61 A", "12 us", "31.80", "32.1 uA", "330 pF", "3.30 uH"],
    "TEST rows (the bounds MODELED and MAKER); DRAFTED R-173; row 3 PROVISIONAL", "row 3 a pass only for a loop at or over 3.30 uH until B6-ENG-1 is decided", ["5.4"])
row("LH-05", "IF-EXT-USB", "current (the outlet's trip)", "yaml",
    "U18's trip at 3.793 to 4.576 A (VI(TRIP) 19.2 to 22.6 mV, MAKER, with 1 percent and 50 ppm/K over 45 K), above every 3 A contract and under the Bulgin PXP4043/C receptacle's 5 A; as drawn R138 10 mOhm trips at 1.897 to 2.288 A",
    ["l4e4md"], "the chosen values (R138); the outlet's bench procedure", ["3.793", "4.576", "19.2", "22.6", "50 ppm/K", "45 K", "PXP4043/C", "1.897", "2.288", "4.212", "5.810", "C2903482"],
    "MAKER rows (SLVSDG8B), INFERRED; DRAFTED R-02", "VI(TRIP)'s row at L4-E4's bench (a); J_USBC_OUT's header and its rating (R-30)", ["5.5"])
row("LH-06a", "IF-AB-POWER currents (+54V_POE)", "monitor", "yaml",
    "full scale 81.92 mV over 5 mOhm is 16.384 A (Current_LSB 0.5 mA, CAL 2048); 3.682 A at a 10.0 V stack for 0.6 A at 54 V over 0.88, 14.33 A at the stage's fault bound (72.38 mV)",
    ["l4e9md", "reg"], "1d row IF-13 and part A; R-27", ["81.92", "16.384", "0.5 mA", "2048", "3.682", "14.33", "72.38", "1.731", "3.025", "76.25", "1.475", "20.135", "0.88"],
    "INFERRED from MAKER rows (SBOS547C); DRAFTED R-06; PROVISIONAL (R227's pulse rating)", "R-101 (R227's pulse rating and capacitance envelope); R-120, R-121 (L10's L(I) at temperature)", ["5.4", "5.11"])
row("LH-06b", "FW-A09", "U17's readings restated", "hwfw",
    "its readings are the PoE stage's INPUT current and POE_VIN (VBUS pin 8 is on POE_VIN; VBAT is POE_VIN plus the shunt's drop)",
    ["reg"], "R-27", ["16.384", "0.5 mA", "2048", "1.731", "3.025"], "INFERRED; DRAFTED R-06", "as LH-06a", ["5.11"])
row("LH-07a", "FW-A16", "LH-07's condition", "hwfw",
    "IIN_HOST is written 4.70 A only on a board A whose netlist carries the ILIM_HIZ network (H3, FW-A18); on a board without it the derated 4.00 A of r11dep applies (R11 10 mOhm)",
    ["hand", "reg"], "LH-07; R-25", ["4.70", "4.00", "R11 10 mOhm"], "INFERRED (L4-E4, L4-E5, r11dep); FW-A18 OWED", "R-03's network drawn (Layer 8), after which the condition is met on every regenerated board", ["5.11"])
row("LH-07b", "V-A08", "restated for the selected entry", "hwfw",
    "the entry's U6 never asserts FLT_I (its current over the breaker's lowest 6.364 A for less than 0.247 ms, its filtered short-circuit sense under 10.36 A), VIN_RAW never falls below 7.24 V",
    ["reg", "l4e11md"], "R-135, R-76; 7a (E11-21)", ["6.364", "0.247", "10.36", "7.24"], "MAKER rows; DRAFTED R-123", "R-123's parts; R-76 reads it on the bench", ["5.6", "5.11"])
row("LH-08", "V-E14", "REQ-015's bench row", "hwfw",
    "the vehicle supply reversed at -36 V and then at +40 V: no damage; DC_P, DC_F and Q1's VDS recorded (at most 66.2 V reversed); the entry's OV trip inside 39.6 to 41.22 V",
    ["hand"], "LH-08", ["-36 V", "+40 V", "66.2", "39.6 to 41.22", "8.44"], "TEST row (the bounds MAKER and INFERRED); DRAFTED R-123, R-17", "R-123 and R-17 applied; the interconnect's resistance ceiling (R-130)", ["5.4"])
row("LH-09", "V-E15", "REQ-016's backstop bench row", "hwfw",
    "the input current at which SWEN falls, at 17.6 V and 25 V, inside 3.0468 to 3.7408 A at 25 V, at commissioning and at layer 8's interval",
    ["hand", "l4e9md"], "LH-09; 1d row IF-02", ["17.6", "3.0468", "3.7408"], "TEST row (the bounds MODELED, L4-E7R); DRAFTED R-19 to R-21", "L4-E7R's stocked RIMON_IN and R66", ["5.4"])
row("LH-10a", "FW-C08", "SHORE_INHIBIT restated", "hwfw",
    "Asserted only on the operator's 'inputs off' and on the water-on-floor isolation, never for a temperature or 'no charge' hold",
    ["l4e11md"], "7a", [], "RULE (L4-E11's R-a, SESSION)", "none: a rule, reversed only by L4-E11 reversing R-a", ["5.7", "5.11"])
row("LH-10b", "FW-A14", "CHG_INHIBIT restated", "hwfw",
    "asserted only by firmware, never as a charge hold (a hold is the CHRG_INHIBIT bit or ChargeCurrent 0, FW-A19), and never while the pack cannot discharge (S2, S4",
    ["l4e11md"], "7a", [], "RULE (SESSION)", "none", ["5.7", "5.11"])
row("LH-10c", "PANEL.md section 10", "the charge-hold sentence", "panel",
    "No hold uses the CHG_INHIBIT line or SHORE_INHIBIT.", ["l4e11md"], "7a", [], "RULE (SESSION)", "none", ["5.11"])
row("LH-10d", "FW-E13", "DCIN_PGD the entry's fault flag", "hwfw",
    "Read it as the entry's FAULT FLAG, no longer a power-good line", ["l4e11md", "l4e11entry"], "7a; the entry draft's pin map",
    ["FLT_I", "FLT_T", "DCIN_PGD"], "DRAFTED R-123", "R-123 applied: until then the drawn line is the LM5069's power good", ["5.7"])
row("LH-10e", "FW-A19", "rule R-a, the hold's flag and the state table", "hwfw",
    "S4 (both off: below -9 C, SHUTDOWN, a permanent fail, no pack) the gauge holds and as drawn the bit is NOT set",
    ["l4e11md"], "section 4 (rule R-a)", ["-9 C", "SHUTDOWN", "256 mA", "Q-TI-3"], "RULE (SESSION); S2's N2 OPEN; the (B1) half DRAFTED R-157, R-158",
    "N2 (Q-TI-3, E11-06): whether VSYS stays regulated in S2 with the charge inhibited; under (B1) S4's exception is withdrawn (R-158)", ["5.6", "5.11"])
row("LH-10f", "FW-A20", "rules R-b and R-b'", "hwfw",
    "exactly two settings, 0x0000 (no charge) and 0x0200 (1024 mA set), and no value under 0x0200",
    ["l4e11md"], "section 4 (rule R-b), 15c (R-b')", ["0x0000", "0x0200", "1024 mA", "14.0 V", "0.8314", "1.2567", "1.257 W", "124.9", "384 mA", "21.22", "17.59", "0x0080", "0.33616", "5.7 V"],
    "MAKER row (SLUSE66A p.10), INFERRED; PROVISIONAL", "E11-22: cases (ii) and (iii), and board P's copper giving TI's 50 C/W", ["5.11"])
row("LH-10g", "FW-A21", "rule R-c, the shedding sequence", "hwfw",
    "P1 shed, the two mixer fans, the HF module, the Geiger module and the 5G module held off, the bridge, GNSS, Iridium and the panel (the SOS path) kept, P1 at most 20.51 W at VBAT",
    ["l4e11md"], "3g, section 4 (rule R-c), 15b", ["20.51", "8.58", "28.12", "0.98 W", "19.57", "35.24", "3.062"],
    "MODELED (hc2's and rv-pwr's models); PROVISIONAL", "E11-06 (P1 measured, the front end's efficiency), E11-23 (the warm-up time), E11-31 (the start's first window)", ["5.6", "5.11"])
row("LH-10h", "FW-A22", "rule R-d", "hwfw",
    "the image keeps PCHG_COMM 1 and the SUV check (SUV permanent fail at 1.0 V), with Q-TI-7 open", ["l4e11md"], "section 4 (rule R-d)",
    ["PCHG_COMM 1", "Q-TI-7"], "RULE (the image)", "Q-TI-7's answer", ["5.11"])
row("S27-B1", "FW-A23", "(B1)'s registers at boot", "hwfw",
    "EN_OOA written 0 first (the printed VSYS accuracy holds only after that write, E11-31); ChargeCurrent written for any charge (0 A at POR and after the watchdog's 175 s",
    ["reg", "l4e11md"], "R-158; 15a, 12c", ["EN_OOA 0", "D5h", "12.054", "12.546", "150 mV", "11.96"], "MAKER rows (SLUSE65A); DRAFTED R-157, R-158",
    "R-157's release record; R-161 (E11-31) reads the registers back on the build", ["5.6", "5.11"])
row("LH-11a", "FW-C15", "the margin hold as a mode", "hwfw",
    "Trigger: a reading at or over 68.65 C of mixed air plus the reference's calibrated offset", ["l4e12md"], "section 6 (the hold's trigger window)",
    ["68.65", "0.899099", "67.55", "70.00", "2.45 K", "5.64 K", "2.159", "30 minutes"], "MODELED (L4-E12, SESSION); PROVISIONAL",
    "the hold's reference placed in the mixed air or calibrated at T-H1 to +-0.899099 K (U-02's line); a measured lag over the 61 s assumption re-derives 68.65 C", ["5.6", "5.11"])
row("LH-11b", "FW-E12", "the SGP41's own shutdown", "hwfw",
    "Power the SGP41 off at a reading of 54.0 C on a TMP117 on its carrier (54.095833 C exact, rounded down: the SGP41 then at most 54.904167 C, under Table 5's +55 C); power it on, and use its output for REQ-042, only at or under 49.0 C (49.095833 C exact)",
    ["l4e12md"], "section 6 (the SGP41), 17.1", ["54.0", "54.095833", "54.904167", "49.0", "49.095833", "0.254167", "0.15"],
    "INFERRED on MAKER rows (Sensirion Tables 4 and 5, the TMP117's 0.15 C); PROVISIONAL; the switch and the carrier TMP117 OWED",
    "R-139's lag test: a lag over 0.254167 K (a time constant over 83.0 s) re-derives 54.0 and 49.0 C; the switch and the TMP117 drawn on board E", ["5.11"])
row("SEQ-01", "board_to_board.power_line_states", "SLOT_EN1..3 (reset, default, cable-out, the hold)", "yaml",
    "SLOT_EN1..3: {reset: \"LOW (A R30, R34, R38 100 k to GND; the RP2040's pads reset as inputs)\"", ["l4e9md"], "4c (the cold start on the pack)",
    ["SLOT_EN one at a time"], "VERIFIED pulls (IF-BC-PANEL); the hold OWED (FW-C02)", "the SLOT_EN hold drawn (Layer 8, board C or A) closes 5.6's open item", ["5.6", "5.7"])
row("SEQ-02", "board_to_board.power_line_states", "VSYS_DOCK (DRAFTED)", "yaml",
    "VSYS_DOCK: {reset: \"DRAFTED (R-157, R-177, R-181): U42's dVdT ramp 3.99 to 8.75 ms once VSYS is present (C237 22 nF)",
    ["l4e11md"], "16e (the inrush)", ["3.99 to 8.75 ms", "22 nF", "24.3 mA"], "INFERRED (TI's Equation 2); DRAFTED R-181", "R-181's release record", ["5.6", "5.7"])
row("SEQ-03", "board_to_board.power_line_states", "EN_OOA and ChargeCurrent at boot", "yaml",
    "EN_OOA: {reset: \"1b at POR (SLUSE65A; (B1) only, DRAFTED R-157)\"", ["l4e11md"], "15a (the sequences), 12c", ["EN_OOA 0", "ChargeCurrent 0 A"],
    "MAKER (SLUSE65A); DRAFTED R-157", "R-157's release record", ["5.6", "5.7"])
row("SEQ-04", "IF-AE-DOCK cable_out_states", "VSYS_DOCK open at E", "yaml",
    "VSYS_DOCK: \"DRAFTED: open at E; board E's auxiliary domain unpowered, its controller dark, read as HOT-R1 lost; U42 unloaded\"",
    ["l4e11md"], "15a (a lost pin 1)", ["HOT-R1 as the detector lost"], "INFERRED; DRAFTED", "none", ["5.7"])
row("SEQ-05", "IF-PE-PACK sequencing", "the pack's connection pulse", "yaml",
    "the inrush into VBAT's capacitors 242.9 A peak, time constant 33.8 us (over ASCD's 55.6 A for 61.5 us against its 183 us delay",
    ["l4e9md", "l4e11md"], "4a (pack connected); 16d, 17b", ["242.9", "33.8 us", "55.6", "61.5 us", "183 us", "123.3", "267.2", "37.2 us"],
    "MODELED; PROVISIONAL", "E11-30: the pulse qualification on six BUK6Y10-30PX samples at 267.2 A and 37.2 us; VF and ISM hot", ["5.6"])
row("SEQ-06", "IF-PE-PACK sequencing", "the held pack under (B1)", "yaml",
    "VSYS piecewise (SRN under 12.054 V: at least 12.054 V; SRN over 12.546 V: VSRN + 150 mV within 2 percent; between: at least 11.96 V), the pack feeds no kit load (its monitor 0.1398 mA",
    ["l4e9md", "l4e11md"], "4a (the charge inhibited); 15a, 15d", ["12.054", "12.546", "150 mV", "11.96", "0.1398", "1 mA"],
    "MAKER rows (SLUSE65A), INFERRED; DRAFTED R-157; PROVISIONAL", "E11-31 (R-161): the held pack current at most 1 mA; D3's hot leakage and the body diodes' current not bounded on held evidence", ["5.6", "5.7"])
row("SEQ-07", "IF-A-HEAT sequencing", "the mat on measured headroom", "yaml",
    "the mat runs on measured headroom (R-c, FW-A21): on only while the source's measured headroom over the load is at least its 8.58 W",
    ["l4e11md"], "3g", ["8.58", "20.51"], "MODELED; PROVISIONAL", "E11-06", ["5.6"])
row("SEQ-08", "IF-E-FANS power", "the fans' supply under (B1)", "yaml",
    "under (B1) VSYS_E, 9.539 to 17.375 V (L4-E11 15a, 16e; DRAFTED R-177): the fans are declared 12 V class, their maximum supply voltage against 17.375 V and their least operating voltage against 9.539 V TBD (HF-F05, E11-35, R-179)",
    ["l4e11md"], "15a (VSYS_E's range), 16e (the drop)", ["17.375", "9.539"], "INFERRED; DRAFTED R-177; TBD (no fan named)", "E11-35 (R-179): a fan named with its range", ["5.4"])
row("SEQ-09", "IF-EXT-DC default_state", "the charger before any host write", "yaml",
    "the charger before any host write: as drawn ChargeCurrent 256 mA at POR (TI's E2E answer) and after the 175 s watchdog, under (B1) 0 A until firmware writes it",
    ["l4e9md"], "4c (power-on under (B1)), 4g", ["256 mA", "175 s", "0 A"], "MAKER (TI's E2E answer; SLUSE65A); DRAFTED R-157", "none", ["5.7"])
row("SEQ-10", "FW-C08 hardware fact", "the entry's UVLO pin under SHORE_INHIBIT", "hwfw",
    "E's Q8 pulls the entry's UVLO pin low when it is high (as drawn the LM5069's HS_UVLO; on the selected entry the TPS48110-Q1's EN/UVLO on the same net, DRAFTED R-123)",
    ["l4e11entry"], "the entry draft's pin map and part list (Q8 kept)", ["HS_UVLO", "Q8", "DCIN_PGD"], "NETLIST (the draft's text); DRAFTED R-123", "R-123 applied", ["5.7"])


def flat(s):
    return " ".join(s.split())


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# THE TARGETS ARE READ AS THIS PASS WROTE THEM (3 October 2026, Layer 5's second round, record l5r2): this record states what the
# first round wrote, and the second round restated some of those texts in place (FW-E11, the fans' start rule, the SLOT_EN line).
# A reader of the current tree would refuse the day its subject moves on, which is a rule about history; so the three targets are
# read at the commit that carries this pass (in this branch's own history), and the Layer 4 sources from the tree as before.
L5PWR_COMMIT = "1e18a1ca"


def committed(rel):
    import subprocess
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (L5PWR_COMMIT, rel)], capture_output=True)
    if r.returncode != 0:
        sys.stderr.write("l5pwr_contracts: %s is not readable at %s (a git checkout holding this branch's history is needed)\n"
                         % (rel, L5PWR_COMMIT))
        sys.exit(3)
    return r.stdout


def compute():
    texts, pins, missing = {}, {}, []
    for key, rel in list(TARGETS.items()):
        raw = committed(rel)
        texts[key] = flat(raw.decode("utf-8"))
        pins[key] = ("%s@%s" % (L5PWR_COMMIT, rel), hashlib.sha256(raw).hexdigest())
    for key, rel in list(SOURCES.items()):
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            missing.append(rel)
            continue
        texts[key] = flat(open(p, encoding="utf-8").read())
        pins[key] = (rel, sha(p))
    if missing:
        sys.stderr.write("l5pwr_contracts: missing %s\n" % ", ".join(missing))
        sys.exit(3)
    bad, results = [], []
    seen = set()
    for e in T:
        if e["id"] in seen:
            bad.append("%s: duplicate id" % e["id"])
        seen.add(e["id"])
        if e["target"] not in TARGETS:
            bad.append("%s: unknown target %s" % (e["id"], e["target"]))
            continue
        ok_text = flat(e["text"]) in texts[e["target"]]
        if not ok_text:
            bad.append("%s: the excerpt is not in %s: %r" % (e["id"], TARGETS[e["target"]], e["text"][:70]))
        src_text = " ".join(texts[s] for s in e["sources"] if s in texts)
        for s in e["sources"]:
            if s not in SOURCES:
                bad.append("%s: unknown source %s" % (e["id"], s))
        lost = [f for f in e["figures"] if flat(f) not in src_text]
        if lost:
            bad.append("%s: figures not printed by %s: %s" % (e["id"], ", ".join(e["sources"]), lost))
        for c in e["criteria"]:
            if c not in CRITERIA:
                bad.append("%s: criterion %s is not a Layer 5 criterion this pass moves" % (e["id"], c))
        if "PROVISIONAL" in e["mark"] and not e["trigger"].strip():
            bad.append("%s: PROVISIONAL with no trigger" % e["id"])
        if chr(0x2014) in e["text"] + e["trigger"] + e["mark"] or chr(0x2013) in e["text"] + e["trigger"] + e["mark"]:
            bad.append("%s: a dash character" % e["id"])
        results.append(dict(e, ok_text=ok_text, lost=lost))
    if bad:
        for b in bad:
            sys.stderr.write("l5pwr_contracts: %s\n" % b)
        sys.exit(3)
    by_crit = {c: [e["id"] for e in T if c in e["criteria"]] for c in CRITERIA}
    prov = [(e["id"], e["contract"], e["trigger"]) for e in T if "PROVISIONAL" in e["mark"]]
    nfig = sum(len(e["figures"]) for e in T)
    return dict(pins=pins, rows=results, by_crit=by_crit, prov=prov, nfig=nfig)


def md_rows(R):
    out = ["| id | contract | field | text written (excerpt, verbatim in the target) | L4 source row (file; where) | mark | invalidation trigger | criterion (5.x) it moves |",
           "|---|---|---|---|---|---|---|---|"]
    for e in R["rows"]:
        src = "; ".join(os.path.basename({**TARGETS, **SOURCES}[s]) for s in e["sources"]) + "; " + e["where"]
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (e["id"], e["contract"], e["field"], e["text"].replace("|", "/"), src,
                                                                e["mark"], e["trigger"], ", ".join(e["criteria"])))
    return out


def render(R):
    L = []
    p = L.append
    p("L5-PWR: LAYER 5'S POWER PASS, READ BACK (MESHSAT-1357, set 27, 3 October 2026). Prototype design: nothing built, powered or")
    p("measured; this is a check of the contracts' text against the Layer 4 records' text. Marks: MAKER (a maker's printed row),")
    p("INFERRED, MODELED, PROVISIONAL (an open condition, its trigger named), RULE (a session rule), TEST (a bench row), NETLIST;")
    p("DRAFTED (R-nn): true of a release-guarded Layer 4 draft that no generator carries yet.")
    p("")
    p("0. INPUTS (sha256; the targets as written at %s, read from this branch's history, and the sources read from the tree)" % L5PWR_COMMIT)
    for key in list(TARGETS) + list(SOURCES):
        rel, h = R["pins"][key]
        p("   %-10s %s  %s" % (key, h, rel))
    p("")
    p("1. THE TABLE (%d entries, %d figures; every excerpt found in its target, every figure printed by a cited source)" % (len(R["rows"]), R["nfig"]))
    for e in R["rows"]:
        p("   %s | %s | %s | target %s" % (e["id"], e["contract"], e["field"], TARGETS[e["target"]]))
        p("      text: %s" % e["text"])
        p("      source: %s; %s" % (", ".join(SOURCES[s] for s in e["sources"]), e["where"]))
        p("      figures: %s" % (", ".join(e["figures"]) if e["figures"] else "none (a rule or a state, not a figure)"))
        p("      mark: %s" % e["mark"])
        p("      trigger: %s" % e["trigger"])
        p("      criteria: %s" % ", ".join(e["criteria"]))
    p("")
    p("2. THE LAYER 5 CRITERIA THIS PASS MOVES (Layer 5's reading; the handover page's status is the integrator's to set)")
    for c in sorted(CRITERIA, key=lambda x: float(x)):
        p("   %s %s: %d entries (%s)" % (c, CRITERIA[c], len(R["by_crit"][c]), ", ".join(R["by_crit"][c])))
        p("      %s" % CRITERIA_STATE[c])
    p("")
    p("3. THE PROVISIONAL ENTRIES AND THEIR INVALIDATION TRIGGERS (%d)" % len(R["prov"]))
    for i, c, t in R["prov"]:
        p("   %s (%s): %s" % (i, c, t))
    p("")
    p("4. THE TABLE AS MARKDOWN (L5-POWER-CONTRACTS.md carries these lines)")
    for ln in md_rows(R):
        p("   " + ln)
    p("")
    p("5. RESULT: every excerpt is in its target and every figure is printed by a cited Layer 4 source. check_contracts.py is a")
    p("   netlist reader and reads none of these files: its reading is unchanged by this pass (L5-POWER-CONTRACTS.md section 5).")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.stdout.write(render(compute()))
