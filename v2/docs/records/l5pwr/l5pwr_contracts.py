#!/usr/bin/env python3
"""l5pwr_contracts.py: Layer 5's power pass, read back (MESHSAT-1357, set 27, 3 October 2026).

Reads the three contract files Layer 5 owns (pcb_interfaces.yaml, HW-FW-CONTRACT.md, PANEL.md) and the Layer 4 records the pass
drew on, and prints the table L5-POWER-CONTRACTS.md carries: for every entry the contract and field written, the text written (an
excerpt, verbatim), the Layer 4 source that prints its figures, its mark (MAKER, INFERRED, MODELED, PROVISIONAL, RULE; DRAFTED where
the figure is true of a release-guarded draft no generator carries), its invalidation trigger and the Layer 5 criterion (5.x) it
moves. It REFUSES (exit 3) when an excerpt is not in its target or a cited figure is not printed by a cited source, so the table
cannot drift from the files. Every file read is pinned by sha256 in section 0; regen_out.py binds the output to them. Run from the
repository root or anywhere: `python3 v2/docs/records/l5pwr/l5pwr_contracts.py` (a second at most; stdlib only). Nothing here is
measured: it is a check of text against text.

Set 28 (finding F-12, 3 October 2026): set 27's corrections of L4-E7 (round 5) and L4-E11 (section 18) changed what six rows' cited
figures mean, and two of those figures are no longer printed. Those rows are restated in RESTATED (section 1a of the output), never
edited in the table: the figures that no longer stand are checked as printed by the row's sources at L4_BASE, the text that replaced
them is matched once in the tree's sources with its figures parsed from the match, and the targets are read as set 28 carries them
(SET28_COMMIT) to say whether record l5r2 restated them in place or a withdrawn text is still there (a finding).

Set 29 (finding L5-F13, 4 October 2026, the coordinator's integration correction): L4-E9's rounds 7 and 8 corrected LH-04's pointer,
so the two stack voltages row LH-04b cited are no longer printed. The row is restated the same way and named as restated at set 29;
its contract text is NOT RESTATED in the targets (Layer 5's next round)."""
import hashlib
import os
import re
import subprocess
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

# SET 28'S RESTATEMENT (finding F-12 of set 28's RESULT.md, 3 October 2026; authority SESSION under the owner's standing rule of 26
# September 2026). The table above is the pass as written at L5PWR_COMMIT against the Layer 4 records at L4_BASE (fnd/l4e9 before the
# pass). Set 27 then corrected two of those records: L4-E7's round 5 (carried by L4-E9 at 1ba24ca6) withdrew the solar guard's
# reference loop as a passing floor, and L4-E11's section 18 (carried at 92c08cdf and 22cb4c16) moved the mixer fans off VSYS_E onto
# U22's regulated rail and called the hard short's figure an extrapolation and a test target. A row whose cited figure no longer
# stands is restated here, not edited above: the text written stays what the targets carried at L5PWR_COMMIT. Each entry gives the
# figures that no longer stand (each checked as printed by the row's sources at L4_BASE), why, the Layer 4 text that replaced them
# (a pattern with no typed number, matched exactly once in the tree's source; the figures it carries are parsed from the match, never
# typed here), the contract value that changes, the restated mark, trigger and where, and the targets as set 28 carries them
# (SET28_COMMIT): restated in place by record l5r2, or the withdrawn text still there (a finding of section 9 of the page).
L4_BASE = "2c240414"
SET28_COMMIT = "5515ecc0"
RESTATED = {}


def restate(i, withdrawn, why, now, value, mark, trigger, where, target=(), finding=None,
            at=("set 28, F-12", "SET 28 (F-12)", "F-12")):
    """at: the set the row was restated at, as the page words it, as the output words it, and its finding."""
    RESTATED[i] = dict(withdrawn=withdrawn, why=why, now=now, value=value, mark=mark, trigger=trigger, where=where,
                       target=list(target), finding=finding, at=at)


restate("S27-B6", ["0.2396", "0.5287", "60.3", "3.30 uH"],
        "L4-E7's round 5 withdrew round 2's reference loop as a passing floor: at that loop a fault at the connector puts U5's pins past "
        "their absolute maximum, so D-10's guard-on case is OPEN and no loop is claimed to pass",
        [("l4e9md", r"OPEN for the guard-on case: an absolute-rating violation at a connector fault \(round 2's \d+\.\d+ uH WITHDRAWN as a passing floor"),
         ("l4e9md", r"at round 2's \d+\.\d+ uH reference loop, no loop claimed to pass \(L4-E7's round \d+\)"),
         ("l4e9md", r"U5's pins, the complete budget, -\d+\.\d+ to \+\d+\.\d+ V at a fault at the connector \(past the -\d+\.\d+ V ABSOLUTE MAXIMUM\)"),
         ("l4e9md", r"inside \d+ V; at \d+\.\d+ uH U5 \d+\.\d+ V"),
         ("l4e9md", r"turns Q12 off: at most \d+\.\d+ A within \d+\.\d+ us")],
        "CHANGES: the guard-on case is no longer every rating with its margin from the reference loop; it is OPEN (an absolute-rating "
        "violation at a connector fault, no loop claimed to pass), with U5's pins at the reference loop and at the low loop and the "
        "turn-off current as parsed above; the stage question is the engineer's B6-ENG-1",
        "MODELED (L4-E7 round 5); DRAFTED R-173; OPEN (D-10's guard-on case, an absolute-rating violation at a connector fault), PROVISIONAL",
        "B6-ENG-1, the engineer's stage question (R-180 an input only; R-186 Analog Devices' answer; R-187 does not hold, result (ii)); "
        "its wider form B6-ENG-2 (R-189, D-16)",
        "1d row IF-01, 4e (the guard-on row), 8a D-10", finding="L5-F09")
restate("S27-03", ["75 V", "61 A", "3.30 uH"],
        "L4-E7's round 5 restated R-176: row 2's bound on PV_F and row 3's turn-off current changed, and row 3's pass from the reference "
        "loop was withdrawn (no loop is claimed to pass)",
        [("reg", r"PV_F at most \d+ V, its slew and INP inside their absolute ratings"),
         ("reg", r"U21 turning Q12 off \(at most \d+ A, within \d+ us\)"),
         ("reg", r"no loop is claimed to pass \(round \d+\): at \d+\.\d+ uH the pins' complete budget is outside \+-\d+\.\d+ V and B6-ENG-1 decides")],
        "CHANGES in V-E16's rows 2 and 3, not in the excerpt (rows 5 and 6 stand): the parsed bounds replace those the pass wrote for "
        "rows 2 and 3, and row 3 is no longer a pass from any loop until B6-ENG-1 is decided",
        "TEST rows (the bounds MODELED and MAKER); DRAFTED R-173; row 3 OPEN (no loop claimed to pass), PROVISIONAL",
        "row 3: B6-ENG-1 decides the stage (R-180 an input only, R-186, R-187 not holding; B6-ENG-2, R-189); rows 2 and 3 filed against "
        "R-176's bounds at both fault positions",
        "R-176 (rows 2 and 3 as L4-E7's round 5 restated them)",
        [("stale", "hwfw", r"D4 carries nothing, PV_F at most \d+ V;"),
         ("stale", "hwfw", r"U21 turning Q12 off \(at most \d+ A, within \d+ us\)"),
         ("stale", "hwfw", r"a pass only for a loop at or over \d+\.\d+ uH until B6-ENG-1 is decided"),
         ("stale", "hwfw", r"row 3 a pass only from a \d+\.\d+ uH loop until B6-ENG-1"),
         ("stale", "yaml", r"row 3 a pass only for a source loop at or over \d+\.\d+ uH until B6-ENG-1 is decided")], finding="L5-F09")
restate("S27-01", ["0.1486", "9.539", "11.905", "28.6"],
        "L4-E11 section 18 put the mixer fans on U22's regulated rail and declared the dock branch afresh (18b), so the drop, VSYS_E at "
        "the floor and the contact's share are re-derived (18b restates the floor, not VSYS_MIN's start); and L4-E11 17a, after the "
        "recheck, calls the hard short's figure a resistive extrapolation and E11-38's test target, not a bound",
        [("l4e11out", r"with U12's \d+\.\d+ A: \d+\.\d+ A DECLARED on IF-AE-DOCK pin 1 \(was \d+\.\d+ A"),
         ("l4e11out", r"the drop at the floor with \d+\.\d+ A: \d+\.\d+ V, VSYS_E \d+\.\d+ V; at U42's least limit \d+\.\d+ V"),
         ("l4e11out", r"the contact at \d+\.\d+ % of \d+\.\d+ A"),
         ("l4e11out", r"A resistive EXTRAPOLATION, not a bound \(I\): \d+ A would flow"),
         ("l4e11out", r"\d+ A for \d+\.\d+ us \(\d+\.\d+ A2s\) is E11-38's TEST TARGET for the recorded peak")],
        "CHANGES: the branch current, the drop, VSYS_E at the floor and the contact's share are 18b's, parsed above; the excerpt, U42's "
        "band at R(ILIM), stands (the resistor renamed R228); the hard short's figure keeps its number but is a test target, no longer "
        "a ceiling",
        "INFERRED from MAKER rows (SLVSET9G), the branch current MODELED (L4-E11 18b); DRAFTED R-157, R-177, R-178, R-181; PROVISIONAL "
        "(L4-F03: remedy drafted, qualification open)",
        "E11-38 (R-184): U42's limit read outside its band, the hard short's recorded peak over its test target (it revises L4-E11 17a), "
        "the 813's resistance after the cases; E11-35 (R-179): a fan's measured start over U42's room at the declared branch",
        "16e, 17a, 18b; out 16e, 17a, 18b",
        [("restated", "yaml", r"so the branch is declared \d+\.\d+ A \(U12 \d+\.\d+ A, U22 \d+\.\d+ A at the floor with both fans at full speed\)"),
         ("restated", "yaml", r"the contact at \d+\.\d+ percent of \d+\.\d+ A, VSYS_E \d+\.\d+ V at the floor"),
         ("stale", "yaml", r"a short applied while on at most \d+ A for at most \d+\.\d+ us \(a ceiling, no inductance credited; INFERRED\)")],
        finding="L5-F10")
restate("S27-02a", ["0.3356", "0.5713", "0.1 A"],
        "L4-E11 section 18 withdrew the fans directly on VSYS_E; on U22's regulated rail the start rule in amperes on VSYS_E is "
        "superseded (R-179) by the room U42 leaves at the declared branch (18b)",
        [("l4e11out", r"no fan read prints a range covering VSYS_E's \d+\.\d+ to \d+\.\d+ V, so 15a's fans directly on VSYS_E is WITHDRAWN"),
         ("reg", r"the supply range question of 15a to 17a \(\d+\.\d+ V at the top, \d+\.\d+ V at the bottom, \d+\.\d+ and \d+\.\d+ A on VSYS_E\) is superseded by the rail"),
         ("l4e11out", r"with one fan running and U12 on, U42's room \d+\.\d+ A leaves \d+\.\d+ W at the rail for the other fan's start")],
        "CHANGES: the rule is no longer the both-together and one-at-a-time currents on VSYS_E; it is U42's room at the declared branch, "
        "as power at U22's rail for one fan's start, the start current NOT READ (E11-35); VSYS_E at U42's least limit stands",
        "INFERRED (L4-E11 18b); DRAFTED R-177, R-181; PROVISIONAL (the start current NOT READ)",
        "E11-35 (R-179): the named fans' start current read over U42's room at the rail; U42's limit read outside its band (E11-38, R-184)",
        "18, 18b; out 18, 18b; R-179",
        [("restated", "yaml", r"the start rule above \(\d+\.\d+ A and \d+\.\d+ A on VSYS_E\) is superseded by section 18b: with one fan running and U12 on, U42 leaves \d+\.\d+ A of room, \d+\.\d+ W at the rail for the other fan's start"),
         ("stale", "yaml", r"firmware starts them one at a time with a PWM ramp, never both within \d+ s and never while U12 starts \(R-188\)")],
        finding="L5-F10")
restate("S27-02b", ["PWM ramp", "0.5713"],
        "L4-E11 18c restated the stagger for the fans on U22's rail (E11-39, R-188): the ramp is a PWM-duty ramp into the fan's PWM input, "
        "U22's start joins U12's, and the room is U42's at the declared branch (18b), the per-fan start current on VSYS_E superseded (R-179)",
        [("l4e11out", r"each by a PWM-duty ramp into the fan's PWM input, never both within \d+ s and never while U12 or U22 starts"),
         ("reg", r"U42's room \d+\.\d+ A at the floor"),
         ("reg", r"the current through J_DOCK pin 1 under \d+\.\d+ A at every start")],
        "CHANGES the rule's wording, not its intent: a PWM ramp becomes a PWM-duty ramp into the fan's PWM input, and never while U12 "
        "starts becomes never while U12 or U22 starts; the trigger's per-fan start current gives way to U42's room",
        "RULE (L4-E11 17a and 18c, SESSION); DRAFTED R-177, R-181; PROVISIONAL",
        "E11-35 (R-179): the named fans' start current read over U42's room at the rail; U42's limit read outside its band (E11-38, R-184)",
        "out 18c (E11-39 restated); R-188",
        [("restated", "hwfw", r"Start the mixer fans one at a time, each by a PWM-duty ramp into the fan's PWM input, never both within \d+ s and never while U12 or U22 starts \(E11-39, R-188; L4-E11 18c\)")])
restate("SEQ-08", ["17.375", "9.539"],
        "L4-E11 section 18: no named fan's printed range covers VSYS_E, so the fans directly on VSYS_E are withdrawn; they run on U22's "
        "regulated rail, whose band sits inside the named fans' range (18a)",
        [("l4e11out", r"no fan read prints a range covering VSYS_E's \d+\.\d+ to \d+\.\d+ V, so 15a's fans directly on VSYS_E is WITHDRAWN"),
         ("l4e11out", r"the output \d+\.\d+ V \(\d+\.\d+ to \d+\.\d+ V at FB's limits with the \d+ % divider\) inside the fans' \d+\.\d+ to \d+\.\d+ V")],
        "CHANGES: the fans' supply is U22's +12V_FAN, not VSYS_E; the supply range TBD is closed by the rail (DRAFTED); the start "
        "current and the PWM input level stay NOT READ (R-179, F-L7-11)",
        "INFERRED (L4-E11 18a); DRAFTED R-177; PROVISIONAL (the start current and the PWM input level NOT READ)",
        "E11-35 (R-179): the named fans' start current and PWM input level read; R-177's release (U22 and the four-wire headers drawn)",
        "18, 18a; out 18, 18a",
        [("restated", "yaml", r"\+12V_FAN \d+\.\d+ V \(\d+\.\d+ to \d+\.\d+ V at FB's limits\) from U22 on VSYS_E, inside the fans' \d+\.\d+ to \d+\.\d+ V")])

restate("LH-04b", ["11.48", "10.42"],
        "L4-E9's round 7 corrected LH-04's pointer, which had read rv-pwr's PS-ALLTX PLAN line and not the floor's basis (decision "
        "D-11's all-transmit basis), and its round 8 restated it on Layer 9's final drafts",
        [("hand", r"decision D-11's all-transmit basis at \d+ A from a \d+\.\d+ V stack as drawn and \d+\.\d+ V on the final drafts, OCD1's \d+ A only below a \d+\.\d+ V stack there"),
         ("l4e9md", r"decision D-11's all-transmit basis at \d+ A from a \d+\.\d+ V stack as drawn, \d+\.\d+ V on the final drafts, needing \d+\.\d+ V rest against REQ-018's \d+\.\d+ V \(D-17 OPEN")],
        "CHANGES: the pointer is no longer the PS-ALLTX PLAN line's stack voltages; it is decision D-11's all-transmit basis and OCD1's "
        "stack as parsed above, and that basis is not supplied from REQ-018's pass line (D-17 OPEN); the continuous and the peak "
        "service currents stand",
        "MODELED (L4-E9 out 30, on Layer 9's final drafts); PROVISIONAL; D-17 OPEN",
        "PWR-F12 (FEA-004): the chain's short-time rating at the peak service current and F2 near its hot corner; D-17 (L4-E9 8a): "
        "the all-transmit basis against REQ-018's pass line",
        "1d row IF-10; LH-04 as L4-E9's rounds 7 and 8 corrected it (out 30)",
        [("stale", "yaml", r"PS-ALLTX's \d+ A at an \d+\.\d+ V stack and OCD1's \d+ A below \d+\.\d+ V")],
        finding="L5-F13", at=("set 29, L5-F13", "SET 29 (L5-F13)", "L5-F13"))

# A parsed figure: a signed decimal, or an integer with its unit (a section number, a round or an id is not a figure).
FIG = re.compile(r"(?<![\w.+-])(?:\+-|[-+])?\d+(?:\.\d+)?(?: (?:uH|nH|mV|V|mA|A2s|A|W|us|ms|s|%|kOhm|mOhm))?(?![\w.])")


def figures_in(s):
    return [f for f in FIG.findall(s) if "." in f or " " in f]


def flat(s):
    return " ".join(s.split())


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def rx(p):
    """A pattern whose literal spaces match any whitespace, so a match may cross a wrapped line."""
    return re.compile(p.replace(" ", r"\s+"))


def words(s):
    """An excerpt as a pattern: its words in order, any whitespace between."""
    return re.compile(r"\s+".join(re.escape(w) for w in s.split()))


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


# THE TARGETS ARE READ AS THIS PASS WROTE THEM (3 October 2026, Layer 5's second round, record l5r2): this record states what the
# first round wrote, and the second round restated some of those texts in place (FW-E11, the fans' start rule, the SLOT_EN line).
# A reader of the current tree would refuse the day its subject moves on, which is a rule about history; so the three targets are
# read at the commit that carries this pass (in this branch's own history), and the Layer 4 sources from the tree as before.
L5PWR_COMMIT = "1e18a1ca"


def at_commit(commit, rel):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, rel)], capture_output=True)
    if r.returncode != 0:
        sys.stderr.write("l5pwr_contracts: %s is not readable at %s (a git checkout holding this branch's history is needed)\n"
                         % (rel, commit))
        sys.exit(3)
    return r.stdout


def committed(rel):
    return at_commit(L5PWR_COMMIT, rel)


def compute():
    texts, pins, missing, raw = {}, {}, [], {}
    for key, rel in list(TARGETS.items()):
        b = committed(rel)
        texts[key] = flat(b.decode("utf-8"))
        pins[key] = ("%s@%s" % (L5PWR_COMMIT, rel), hashlib.sha256(b).hexdigest())
    for key, rel in list(SOURCES.items()):
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            missing.append(rel)
            continue
        raw[key] = open(p, encoding="utf-8").read()
        texts[key] = flat(raw[key])
        pins[key] = (rel, sha(p))
    if missing:
        sys.stderr.write("l5pwr_contracts: missing %s\n" % ", ".join(missing))
        sys.exit(3)
    # set 28's restatement reads the row sources it cites at L4_BASE and the targets at SET28_COMMIT, both from this branch's history
    base, s28, s28raw, pins2 = {}, {}, {}, {}
    for e in T:
        if e["id"] in RESTATED:
            for s in e["sources"]:
                if s not in base and s in SOURCES:
                    b = at_commit(L4_BASE, SOURCES[s])
                    base[s] = flat(b.decode("utf-8"))
                    pins2["%s@base" % s] = ("%s@%s" % (L4_BASE, SOURCES[s]), hashlib.sha256(b).hexdigest())
    for key, rel in list(TARGETS.items()):
        if key != "panel":
            b = at_commit(SET28_COMMIT, rel)
            s28raw[key] = b.decode("utf-8")
            s28[key] = flat(s28raw[key])
            pins2["%s@set28" % key] = ("%s@%s" % (SET28_COMMIT, rel), hashlib.sha256(b).hexdigest())
    bad, results = [], []
    seen = set()
    ids = [e["id"] for e in T]
    for i in RESTATED:
        if i not in ids:
            bad.append("%s: restated but not a row of the table" % i)
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
        rs = RESTATED.get(e["id"])
        gone = rs["withdrawn"] if rs else []
        for f in gone:
            if f not in e["figures"]:
                bad.append("%s: %r is restated as withdrawn but is not a figure the row cites" % (e["id"], f))
        lost = [f for f in e["figures"] if f not in gone and flat(f) not in src_text]
        if lost:
            bad.append("%s: figures not printed by %s: %s" % (e["id"], ", ".join(e["sources"]), lost))
        res = None
        if rs:
            base_text = " ".join(base[s] for s in e["sources"] if s in base)
            unprinted = [f for f in gone if flat(f) not in base_text]
            if unprinted:
                bad.append("%s: withdrawn figures not printed by %s at %s: %s" % (e["id"], ", ".join(e["sources"]), L4_BASE, unprinted))
            cites = []
            for key, pat in rs["now"]:
                ms = list(rx(pat).finditer(raw.get(key, "")))
                if len(ms) != 1:
                    bad.append("%s: the replacing text is matched %d times (not once) in %s: %r" % (e["id"], len(ms), SOURCES.get(key, key), pat[:60]))
                    continue
                txt = flat(ms[0].group(0))
                cites.append(dict(key=key, file=SOURCES[key], line=line_of(raw[key], ms[0].start()), text=txt, figures=figures_in(txt)))
            tg = e["target"]
            tchecks = []
            if tg in s28:
                m0 = words(e["text"]).search(s28raw[tg])
                written_at_28 = (TARGETS[tg], line_of(s28raw[tg], m0.start())) if m0 else None
            else:
                written_at_28 = None
            for kind, key, pat in rs["target"]:
                ms = list(rx(pat).finditer(s28raw.get(key, "")))
                if not ms:
                    bad.append("%s: the %s text is not in %s at %s: %r" % (e["id"], kind, TARGETS.get(key, key), SET28_COMMIT, pat[:60]))
                    continue
                tchecks.append(dict(kind=kind, file=TARGETS[key], line=line_of(s28raw[key], ms[0].start()), text=flat(ms[0].group(0)),
                                    count=len(ms)))
            restated = any(c["kind"] == "restated" for c in tchecks)
            state = ("RESTATED IN PLACE" if restated and not written_at_28 else "SUPERSEDED IN PLACE" if restated else "NOT RESTATED")
            stale = [c for c in tchecks if c["kind"] == "stale"]
            if (state == "NOT RESTATED" or stale) and not rs["finding"]:
                bad.append("%s: a withdrawn text is still in a target at %s and no finding names it" % (e["id"], SET28_COMMIT))
            if not cites or not any(c["figures"] for c in cites):
                bad.append("%s: restated with no parsed figure" % e["id"])
            res = dict(rs, cites=cites, written_at_28=written_at_28, tchecks=tchecks, state=state)
        eff = dict(e)
        if res:
            eff.update(mark=res["mark"], trigger=res["trigger"], where_now=res["where"])
        for c in e["criteria"]:
            if c not in CRITERIA:
                bad.append("%s: criterion %s is not a Layer 5 criterion this pass moves" % (e["id"], c))
        if "PROVISIONAL" in eff["mark"] and not eff["trigger"].strip():
            bad.append("%s: PROVISIONAL with no trigger" % e["id"])
        for s in (e["text"], e["trigger"], e["mark"], eff["trigger"], eff["mark"]) + ((res["why"], res["value"], res["where"]) if res else ()):
            if chr(0x2014) in s or chr(0x2013) in s:
                bad.append("%s: a dash character" % e["id"])
                break
        results.append(dict(eff, ok_text=ok_text, lost=lost, restated=res, was=dict(mark=e["mark"], trigger=e["trigger"], where=e["where"])))
    if bad:
        for b in bad:
            sys.stderr.write("l5pwr_contracts: %s\n" % b)
        sys.exit(3)
    by_crit = {c: [e["id"] for e in T if c in e["criteria"]] for c in CRITERIA}
    prov = [(e["id"], e["contract"], e["trigger"], e["restated"]["at"][2] if e["restated"] else "") for e in results if "PROVISIONAL" in e["mark"]]
    nfig = sum(len(e["figures"]) for e in T)
    ngone = sum(len(r["withdrawn"]) for r in RESTATED.values())
    return dict(pins=pins, pins2=pins2, rows=results, by_crit=by_crit, prov=prov, nfig=nfig, ngone=ngone)


def md_rows(R):
    out = ["| id | contract | field | text written (excerpt, verbatim in the target) | L4 source row (file; where) | mark | invalidation trigger | criterion (5.x) it moves |",
           "|---|---|---|---|---|---|---|---|"]
    for e in R["rows"]:
        r = e["restated"]
        keys = list(e["sources"]) + ([k for k, _p in r["now"] if k not in e["sources"]] if r else [])
        files = "; ".join(dict.fromkeys(os.path.basename({**TARGETS, **SOURCES}[s]) for s in keys))
        src = files + "; " + (r["where"] + " (restated at " + r["at"][0] + ", section 4a; as written: " + e["was"]["where"] + ")" if r else e["where"])
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (e["id"], e["contract"], e["field"], e["text"].replace("|", "/"), src,
                                                                e["mark"], e["trigger"], ", ".join(e["criteria"])))
    return out


def md_restated(R):
    out = ["| id | cited at `%s`, no longer standing | why (the Layer 4 change: set 27's, or L4-E9's rounds 7 and 8 for a row restated at set 29) | what replaced it (file: the text, its figures parsed) | contract value | the targets at set 28 (`%s`) |" % (L4_BASE, SET28_COMMIT),
           "|---|---|---|---|---|---|"]
    for e in R["rows"]:
        r = e["restated"]
        if not r:
            continue
        now = "; ".join('%s: "%s"' % (os.path.basename(c["file"]), c["text"]) for c in r["cites"])
        tg = [r["state"] + (" (record l5r2)" if r["state"] != "NOT RESTATED" else "")]
        if r["written_at_28"]:
            tg.append("the text written still at %s:%d" % (os.path.basename(r["written_at_28"][0]), r["written_at_28"][1]))
        for c in r["tchecks"]:
            tg.append('%s %s:%d: "%s"' % ("restated" if c["kind"] == "restated" else "withdrawn text still at", os.path.basename(c["file"]),
                                        c["line"], c["text"]))
        if r["finding"]:
            tg.append("finding %s" % r["finding"])
        out.append("| %s | %s | %s | %s | %s | %s |" % (e["id"], ", ".join(r["withdrawn"]), r["why"], now.replace("|", "/"), r["value"],
                                                        "; ".join(tg).replace("|", "/")))
    return out


def render(R):
    L = []
    p = L.append
    p("L5-PWR: LAYER 5'S POWER PASS, READ BACK (MESHSAT-1357, set 27, 3 October 2026). Prototype design: nothing built, powered or")
    p("measured; this is a check of the contracts' text against the Layer 4 records' text. Marks: MAKER (a maker's printed row),")
    p("INFERRED, MODELED, PROVISIONAL (an open condition, its trigger named), RULE (a session rule), TEST (a bench row), NETLIST;")
    p("DRAFTED (R-nn): true of a release-guarded Layer 4 draft that no generator carries yet. Restated at set 28 (finding F-12):")
    p("the rows whose cited figures set 27's Layer 4 corrections changed, against the tree's Layer 4 records (section 1a).")
    p("")
    p("0. INPUTS (sha256; the targets as written at %s, read from this branch's history, and the sources read from the tree)" % L5PWR_COMMIT)
    for key in list(TARGETS) + list(SOURCES):
        rel, h = R["pins"][key]
        p("   %-10s %s  %s" % (key, h, rel))
    p("   read at a commit for set 28's restatement (F-12): the restated rows' sources as this pass read them (%s) and the targets as" % L4_BASE)
    p("   set 28 carries them (%s), both from this branch's history" % SET28_COMMIT)
    for key in sorted(R["pins2"]):
        rel, h = R["pins2"][key]
        p("   %-13s %s  %s" % (key, h, rel))
    p("")
    p("1. THE TABLE AS WRITTEN (%d entries, %d figures; every excerpt found in its target, every figure printed by a cited source but"
      % (len(R["rows"]), R["nfig"]))
    p("   the %d that no longer stand, which section 1a restates and checks as printed by their sources at %s)" % (R["ngone"], L4_BASE))
    for e in R["rows"]:
        p("   %s | %s | %s | target %s" % (e["id"], e["contract"], e["field"], TARGETS[e["target"]]))
        p("      text: %s" % e["text"])
        p("      source: %s; %s" % (", ".join(SOURCES[s] for s in e["sources"]), e["was"]["where"]))
        p("      figures: %s" % (", ".join(e["figures"]) if e["figures"] else "none (a rule or a state, not a figure)"))
        p("      mark: %s" % e["was"]["mark"])
        p("      trigger: %s" % e["was"]["trigger"])
        p("      criteria: %s" % ", ".join(e["criteria"]))
        if e["restated"]:
            p("      RESTATED AT %s: section 1a" % e["restated"]["at"][1])
    p("")
    rows = [e for e in R["rows"] if e["restated"]]
    s28 = [e for e in rows if e["restated"]["at"][2] == "F-12"]
    p("1a. RESTATED AT SET 28 (finding F-12; authority SESSION): %d rows whose cited figures set 27's Layer 4 corrections changed" % len(s28))
    if len(rows) != len(s28):
        p("    AND AT SET 29 (finding L5-F13; the coordinator's integration correction, authority SESSION): %d row whose cited figures"
          % (len(rows) - len(s28)))
        p("    L4-E9's rounds 7 and 8 changed; it is marked 'restated at set 29' below")
    for e in rows:
        r = e["restated"]
        p("   %s | %s | %s" % (e["id"], e["contract"], e["field"]))
        if r["at"][2] != "F-12":
            p("      restated at %s" % r["at"][0])
        p("      no longer standing (printed by %s at %s): %s" % (", ".join(e["sources"]), L4_BASE, ", ".join(r["withdrawn"])))
        p("      why: %s" % r["why"])
        p("      replaced by (the tree's Layer 4 text, matched once; its figures parsed, none typed):")
        for c in r["cites"]:
            p('         %s:%d: "%s"' % (c["file"], c["line"], c["text"]))
        p("      figures in the replacing text (parsed): %s" % ", ".join(dict.fromkeys(f for c in r["cites"] for f in c["figures"])))
        p("      contract value: %s" % r["value"])
        p("      mark now: %s" % r["mark"])
        p("      trigger now: %s" % r["trigger"])
        p("      where now: %s" % r["where"])
        p("      the target at %s: %s%s" % (SET28_COMMIT, r["state"], " (record l5r2)" if r["state"] != "NOT RESTATED" else ""))
        if r["written_at_28"]:
            p("         %s:%d: the text written" % r["written_at_28"])
        for c in r["tchecks"]:
            p('         %s:%d: %s: "%s"' % (c["file"], c["line"], "restated" if c["kind"] == "restated" else "withdrawn text still there", c["text"]))
        if r["finding"]:
            p("      finding: %s (L5-POWER-CONTRACTS.md section 9)" % r["finding"])
    p("")
    p("2. THE LAYER 5 CRITERIA THIS PASS MOVES (Layer 5's reading; the handover page's status is the integrator's to set)")
    for c in sorted(CRITERIA, key=lambda x: float(x)):
        p("   %s %s: %d entries (%s)" % (c, CRITERIA[c], len(R["by_crit"][c]), ", ".join(R["by_crit"][c])))
        p("      %s" % CRITERIA_STATE[c])
    p("")
    p("3. THE PROVISIONAL ENTRIES AND THEIR INVALIDATION TRIGGERS (%d; a restated row's trigger as restated at set 28)" % len(R["prov"]))
    for i, c, t, rs in R["prov"]:
        p("   %s (%s)%s: %s" % (i, c, (" [restated, %s]" % rs) if rs else "", t))
    p("")
    p("4. THE TABLE AS MARKDOWN (L5-POWER-CONTRACTS.md carries these lines; a restated row's mark and trigger as restated)")
    for ln in md_rows(R):
        p("   " + ln)
    p("")
    p("4a. THE RESTATEMENT AS MARKDOWN (L5-POWER-CONTRACTS.md section 4a carries these lines)")
    for ln in md_restated(R):
        p("   " + ln)
    p("")
    p("5. RESULT: every excerpt is in its target and every figure is printed by a cited Layer 4 source, but the figures restated at")
    p("   set 28, which their sources printed at %s; every replacing text is matched once in the tree's Layer 4 records. check_contracts.py" % L4_BASE)
    p("   is a netlist reader and reads none of these files: its reading is unchanged by this pass (L5-POWER-CONTRACTS.md section 5).")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.stdout.write(render(compute()))
