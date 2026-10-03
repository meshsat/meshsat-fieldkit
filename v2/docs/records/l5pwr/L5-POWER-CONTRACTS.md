# L5-PWR: Layer 4's power results written into Layer 5's interface contracts (MESHSAT-1357, set 27, 3 October 2026)

Prototype design: nothing here has been built, powered or measured. This page records Layer 5's power pass on the integration
candidate `fnd/l4e9` at `2c240414` (L4-E9's consolidation with L4-F01 to L4-F04 and CP01 to CP03 carried): the handover entries
LH-01 to LH-11 of `../l4e9/LAYER5-HANDOVER.md`, the set 27 rows and the power lines' states, written into the three files Layer 5
owns (`v2/ecad/tools/pcb_interfaces.yaml`, `v2/docs/HW-FW-CONTRACT.md`, `v2/docs/PANEL.md` section 10) by `apply_l5pwr.py`, read
back by `l5pwr_contracts.py` (its output `l5pwr_contracts.out` pins every file by sha256 and refuses an excerpt that is not in
its target or a figure no cited source prints). No requirement is changed: a contract never loosens a Layer 3 requirement, and
where the drawn board falls short of one (the LM5069 at a 9.00 V plug, the outlet's drawn trip under its 3 A contracts) the
contract says so and names the draft that closes it. No L4 record and no generator is edited. The owner's instruction of 2 October
2026 (`v2/docs/handover/OWNER-INSTRUCTION-2026-10-02.md`) is followed: Layer 5's artefacts are editable, their assumptions and
invalidation triggers visible, and nothing is counted complete that is only drafted.

## 1. What was written, and where

| Entry | Target | What |
|---|---|---|
| LH-01, LH-02 | `pcb_interfaces.yaml` IF-EXT-DC | levels (both inputs), current (dc, solar, contacts, vh), protection, sequencing, default_state, tbd, firmware, bench and the L4 defects; the drawn board stated first, the selected entry and the solar stage's drafts marked DRAFTED with their register rows |
| LH-03, LH-04, set 27 | IF-AE-DOCK | vin_raw's voltage, in-service and fault current and properties; pack_pins' charge and service rows; the new field `pin1_vsys_dock` (the dock's pin 1 as VSYS_DOCK behind U42: 1.471 to 1.802 A, the drop, the fans' start rule, its PROVISIONAL state); levels, current, harness, mating, judged_by, tbd, sequencing, default_state, cable_out_states, firmware, bench. The `pins` map stays the committed netlists' (pin 1 GND), which is what `check_contracts.py` reads; L4-E11's `apply_pcb_interfaces_dock.py` keeps every anchor and still checks OK on the patched file |
| LH-04 | IF-PE-PACK | power's charge and service rows; levels, current, harness, mating, judged_by, tbd, sequencing (the connection pulse, the held pack under (B1), a dead and a cold pack, the stops), default_state, firmware, bench |
| LH-05 | IF-EXT-USB | ends, harness, mating, hot_plug, levels, current (the outlet's trip, drawn and drafted), protection, sequencing, default_state, firmware, bench, tbd |
| LH-06 | IF-AB-POWER | the +54V_POE row's `monitor` (U17 on R227, L4-E9 R-06, DRAFTED); ends' parts, harness, levels, current, default_state, sequencing, mating, judged_by, tbd |
| set 27 (the fans), R-c | IF-E-FANS, IF-A-HEAT | the fans' supply under (B1) and their start rule; the mat on measured headroom |
| criteria 5.6, 5.7 | `board_to_board.power_line_states` | eleven lines of L4-E9 section 4 (SLOT_EN1..3 with the hold OWED, SHORE_INHIBIT, CHG_INHIBIT, the CHRG_INHIBIT bit and ChargeCurrent, EN_OOA, DCIN_PGD, HOT_R1, VSYS_DOCK, the fans' switches, U34's guard, SWEN), each with its reset, default and cable-out state and the firmware row that drives it |
| LH-07 | `HW-FW-CONTRACT.md` FW-A16, FW-A18, V-A06 to V-A10, FW-E04, FW-C01 | L4-E5's `apply_fw_a16.py` applied as register row R-23 assigns to Layer 5, then LH-07's condition on FW-A16 (the 4.70 A only with the H3 network) and V-A08 as L4-E11 7a restates it (R-135) |
| LH-10 | FW-C08, FW-A14, FW-E13 (new), PANEL.md section 10 | SHORE_INHIBIT and CHG_INHIBIT never a charge hold and never asserted while the pack cannot discharge; DCIN_PGD the entry's fault flag (DRAFTED R-123); the hold sentence of PANEL.md section 10 |
| LH-10's rules R-a to R-d, (B1)'s registers | FW-A19 to FW-A23 (new) | the hold's flag and the state table, ChargeCurrent's two settings and R-b', the shedding sequence with the mat on measured headroom and the VSYS_UVP recovery, PCHG_COMM 1 and the SUV check, EN_OOA 0 and the power-on registers |
| LH-06 | FW-A09 | U17's calibration and meaning on R227 (R-27) |
| LH-11 | FW-C15, FW-E12 (new) | the margin hold as a mode (68.65 C of mixed air plus the calibrated offset, restore 5 K under after 30 minutes, PROVISIONAL), the SGP41's own shutdown (54.0 C off, 49.0 C on and used); the CONOPS half drafted as `apply_conops_l5pwr.py` for the CONOPS owner |
| set 27 (the fans) | FW-E11 (new) | the fans' start stagger as a firmware row (E11-39, R-188) |
| LH-08, LH-09, R-176, the new rows | V-A11, V-C15, V-E11 to V-E16 (new) | the bench rows: the charger's rules, the forced hold, the fans' start, the SGP41, DCIN_PGD, REQ-015's vehicle entry, REQ-016's backstop, the solar guard's six rows (row 3 a pass only from a 3.30 uH loop) |
| the drafts | HW-FW-CONTRACT.md section 4.1 (new), the version paragraph, the State legend, the change record | which release-guarded draft moves which rows, and the rows' state until it applies |

## 2. Inputs read

Section 0 of `l5pwr_contracts.out` pins every file: the three targets as written, L4-E9's `L4-POWER-ARCHITECTURE.md` (1d the
interface rows, 4 the operating behaviour, 5 and 8a), `l4e9_power_path.out`, `DOWNSTREAM-REGISTER.md` and `LAYER5-HANDOVER.md`,
L4-E11's record and output (3g, 3h, section 4, 7a, 15a, 15b, 15c, 15d, 16e, 17a) and its entry draft, L4-E12's record (section 6,
17.1), L4-E13's page (PANEL-ACC), L4-E4's page (R138) and L4-E7's control decision (R-176, the guard). The reader's table names,
for every entry, the source row its figures are printed by.

## 3. Method

- **Marks.** MAKER (a maker's printed row), INFERRED (arithmetic on printed or verified figures), MODELED (a record's model),
  PROVISIONAL (an open condition, the invalidation trigger named beside it), RULE (a session rule of L4-E11 or L4-E12), TEST (a
  bench row), NETLIST or VERIFIED (read in a netlist or a draft's text). DRAFTED (R-nn) marks a figure true of a release-guarded
  Layer 4 draft that no generator carries yet; wherever the drawn board differs it is stated first ("as drawn ..."), so the
  contracts agree with the committed netlists today and name what changes when the drafts apply.
- **PROVISIONAL entries** rest on B6's loop floor (L4-E7's round 3 on B6 is running elsewhere; every entry on it names B6-ENG-1's
  three routes), U-04's start (E11-06, E11-31), L4-F03's fault qualification (E11-38) and the other open rows named in section 7.
- **Traceability.** Every excerpt in the table is verbatim in its target and every figure is printed by the cited Layer 4 file;
  `l5pwr_contracts.py` refuses otherwise, and `test_l5pwr.py` holds it.
- **One script per target**, run once by the author who owns the targets, kept as the change's exact statement; it refuses a
  second run and asserts after patching the yaml that every anchor of L4-E11's dock draft still occurs once.
- **L4-E5's draft applied first** (`../l4e5/apply_fw_a16.py --write`), because register row R-23 assigns its application to
  Layer 5; `test_l4e5.py`'s apply fixture is re-stated on the contract as committed at `2c240414` (a rule that fails when its
  subject is fixed is a rule about history).

## 4. The table

<!-- l5pwr-table:begin -->
| id | contract | field | text written (excerpt, verbatim in the target) | L4 source row (file; where) | mark | invalidation trigger | criterion (5.x) it moves |
|---|---|---|---|---|---|---|---|
| LH-01a | IF-EXT-DC | levels (DC) | per source at VBAT at the plug, the losses hot: 9 V 29.09 to 42.52 W, 12 V 32.22 to 47.72 W, 24 V 69.97 to 90.81 W, 36 V 84.55 to 99.64 W (INFERRED, U3 0.9733) | L4E11-SOURCE-ONLY-AND-ENTRY.md; 3h, the source envelope at the plug | INFERRED; PROVISIONAL (REQ-015 at 9.00 V a CONDITIONAL CANDIDATE) | E11-06: P1 over 20.51 W or the front end under 0.88021 at a 9.00 V plug; E11-09 (the knee drawn); E11-23 (the warm-up time) | 5.4 |
| LH-01b | IF-EXT-DC | current.dc | in service at most 5.983 A from a 9.00 V plug (VIN_RAW 8.148 V), 6.4 percent under the breaker's lowest 6.364 A | L4-POWER-ARCHITECTURE.md; 1d, row IF-05 and the stages' summary | INFERRED (the breaker's rows MAKER, SLUSEE5E); DRAFTED R-123 | E11-06's measurement of the front end's efficiency at the operating point | 5.5 |
| LH-01c | IF-EXT-DC | protection (the selected entry) | UVLO on at 7.87 / 8.14 / 8.44 V and off at 7.46 / 7.66 / 7.95 V of DC_P; OV off above 39.6 / 40.36 / 41.22 V, clear of CS101's 38.83 V at 36 V and under D10's 44.4 V | L4-POWER-ARCHITECTURE.md; LAYER5-HANDOVER.md; 1d rows IF-04 and IF-05, 4a, 4e; LH-01 | MAKER (SLUSEE5E rows), INFERRED; DRAFTED R-123, R-17, R-18; PROVISIONAL (the hard short, D-06) | the loop's inductance under 2.08 uH for a hard short in service (R-134, OPEN); D-06's makers' installed and short-time ratings and F1's clearing I2t (R-113, R-115, R-129 to R-132) | 5.4, 5.5 |
| LH-01d | IF-EXT-DC | tbd (the interconnect) | the loop read four-wire at 58.51 to 64.21 mOhm on every assembly (R-130) | DOWNSTREAM-REGISTER.md; R-130 | INFERRED; PROVISIONAL | R-113, R-115, R-129 to R-132 filed | 5.5 |
| LH-02a | IF-EXT-DC | levels (solar) | Vm20 + U_V at most 25.000 V at -20 C and 1000 W/m2, Voc25 20.315 to 22.156 V for its curve shape | L4-POWER-ARCHITECTURE.md; L4E13-PANEL.md; 1d rows IF-01 and IF-02; L4E13-PANEL.md (PANEL-ACC, the conditioned hold) | MODELED (L4-E7R); PROVISIONAL (PANEL-ACC, no unit accepted; G_CM and the VIN+ bias) | PANEL-ACC's measurement of the one unit (R-35); the makers' answers on G_CM and U18's VIN+ bias (R-101) | 5.4 |
| LH-02b | IF-EXT-DC | current.solar | in operation at most 3.987 A (PANEL-ACC A-3(a), INFERRED), the conservative bound over L4-E7R's regulation (RIMON_IN 31.6k, 2.5485 A nominal, at most 2.9337 A at 25 V) | L4-POWER-ARCHITECTURE.md; L4E13-PANEL.md; 1d row IF-01; L4E13-PANEL.md A-3 | INFERRED (the 1.25 factor MAKER); PROVISIONAL | R-29 (the lead's gauge named by Layer 7); R-148 (A-3(c)) | 5.5 |
| LH-02c | IF-EXT-DC | tbd (A-3(c)) | J_SOLAR and PV_IN carry 13.82 A at the design level 2111.4 W/m2 | DOWNSTREAM-REGISTER.md; R-148 | INFERRED (a COMPONENT_LIMITATION); PROVISIONAL | R-148: a rating of at least 13.82 A or a bench row before the panel is accepted | 5.5 |
| LH-02d | IF-EXT-DC | protection (the solar stage) | the INB filter, five 100 nF C0G across R66 8.45k (3.960 to 4.496 ms); SWEN off by default below 2.662 V on TRK_LDO33; a response inside 1.087 ms after the filter's 0.4205 J held charge | L4-POWER-ARCHITECTURE.md; 1d rows IF-01 and IF-02, 4e | MODELED (L4-E7R); DRAFTED R-12, R-19 to R-21, R-98; PROVISIONAL | the loop's typical rows (break-even 2.51 times), the bulk's temperature and the bank's pulse capability: M2 (R-122) | 5.4 |
| S27-B6 | IF-EXT-DC | protection (the guard already on) | every rating with its margin only from a source loop of at least 3.30 uH (U5 0.2396 V of +-0.240 V, a DESIGN TARGET), NOT under it (at 1.00 uH U5 0.5287 V) | L4-POWER-ARCHITECTURE.md; 4e (the guard-on row), 8a D-10 | MODELED (L4-E7 round 2); DRAFTED R-173; PROVISIONAL, NOT CLOSED | B6-ENG-1: R-180 (the loop bounded and measured), R-186 (Analog Devices' answer on a sense-pin filter) or R-187 (the sense moved); L4-E7's round 3 on B6 is running and re-reads this sentence | 5.4 |
| LH-03a | IF-AE-DOCK | vin_raw.voltage | solar 7.378 V (the corrected knee's certain HIZ, L4-E9 R-03, a specification) to 30.15 V (the tracker's raised ceiling, R10 232 k; L4-E5, DRAFTED); vehicle 9 to 36 V at the plug (VIN_RAW 8.148 V at 5.983 A from a 9.00 V plug; INFERRED); at most 41.22 V | L4-POWER-ARCHITECTURE.md; 1d row IF-06 | INFERRED; R-03 a specification; DRAFTED R-03, R-123 | R-03's network drawn to the knee (Layer 8); the OV maximum follows R-123's parts | 5.4 |
| LH-03b | IF-AE-DOCK | vin_raw.in_service | fault current at most 11.65 A at R11 8 mOhm and R12 12 mOhm (13.315 A at 7 mOhm), inside the declared 14.10 A and the four 9 A pins (3.88 A each with one open) | L4-POWER-ARCHITECTURE.md; LAYER5-HANDOVER.md; 1d rows IF-06 and IF-07; LH-03 (the 3.88 A with one pin open) | MODELED; R11 and R12 DRAFTED R-04, R-01 | R11's 7 mOhm fallback (V-A07) moves the fault bound to 13.315 A, still inside 14.10 A | 5.5 |
| LH-03c | IF-AE-DOCK | vin_raw.properties | U34's restart guard falls at 6.754 to 7.139 V (R14 76.8k, L4-E9 R-124, DRAFTED), at least 0.1 V under the knee's certain HIZ 7.378 V; as drawn it falls at up to 8.309 V | L4-POWER-ARCHITECTURE.md; 1d row IF-07, 4a | INFERRED; DRAFTED R-124 | R-124's fitted parts: the guard's fall read on the regenerated board | 5.7 |
| LH-04a | IF-AE-DOCK pack_pins; IF-PE-PACK power | charge | at most 3.0 A (FW-A02; REQ-075 3.06 A), under the gauge's OCC 5 A | L4-POWER-ARCHITECTURE.md; 1d row IF-10 | MAKER (the gauge's OCC), INFERRED | FW-A02's setting; R-28 re-derives it at bring-up | 5.5 |
| LH-04b | IF-AE-DOCK pack_pins; IF-PE-PACK power | service | PS-ALLTX's 18 A at an 11.48 V stack and OCD1's 20 A below 10.42 V (pwr_budget.out D-11 line; MODELED) | L4-POWER-ARCHITECTURE.md; LAYER5-HANDOVER.md; 1d row IF-10; LH-04 | MODELED; PROVISIONAL | PWR-F12 (FEA-004): the chain's short-time rating at 18 A and F2 near +60 C | 5.5 |
| S27-01 | IF-AE-DOCK | pin1_vsys_dock (the new row of set 27) | U42's I(OL) 1.4713 to 1.8018 A at R(ILIM) 11.0 kOhm 0.1 percent | L4E11-SOURCE-ONLY-AND-ENTRY.md; l4e11_power.out; 16e, 17a; out 16 and 17 | INFERRED from MAKER rows (SLVSET9G); DRAFTED R-157, R-177, R-178, R-181; PROVISIONAL (L4-F03: remedy drafted, qualification open) | E11-38 (R-184): a limit read outside 1.471 to 1.802 A, the hard short's cases, the 813's resistance after them; E11-35 (R-179): a fan or U12 current over 1.471 A | 5.2, 5.5, 5.7 |
| S27-02a | IF-AE-DOCK pin1_vsys_dock; IF-E-FANS sequencing | the fans' start rule | both fans together at most 0.3356 A each, one at a time at most 0.5713 A (the other running at 0.1 A), VSYS_E at the least limit at least 9.494 V at the supplement floor | L4E11-SOURCE-ONLY-AND-ENTRY.md; l4e11_power.out; 17a; out 17 | INFERRED; DRAFTED R-177, R-181; PROVISIONAL | a fan named whose start exceeds 0.5713 A (E11-35, R-179); U42's limit read outside its band (E11-38) | 5.6, 5.11 |
| S27-02b | FW-E11 | the fans' start stagger as a firmware row | Start the mixer fans one at a time, each with a PWM ramp, never both within 1 s and never while U12 starts (E11-39, R-188) | l4e11_power.out; DOWNSTREAM-REGISTER.md; out 17 (E11-39); R-188 | RULE (L4-E11 17a, SESSION); DRAFTED R-177, R-181; PROVISIONAL | a fan named whose start exceeds 0.5713 A (E11-35, R-179); U42's limit read outside 1.471 to 1.802 A (E11-38, R-184) | 5.6, 5.11 |
| S27-03 | V-E16 (IF-EXT-DC bench) | R-176 rows 1 to 6 where they bind the solar port | (5) Q13's leakage at the hot end, under 32.1 uA; (6) no short-circuit trip with C126 at 330 pF in operation and under CS116 (R-174) | DOWNSTREAM-REGISTER.md; R-176 | TEST rows (the bounds MODELED and MAKER); DRAFTED R-173; row 3 PROVISIONAL | row 3 a pass only for a loop at or over 3.30 uH until B6-ENG-1 is decided | 5.4 |
| LH-05 | IF-EXT-USB | current (the outlet's trip) | U18's trip at 3.793 to 4.576 A (VI(TRIP) 19.2 to 22.6 mV, MAKER, with 1 percent and 50 ppm/K over 45 K), above every 3 A contract and under the Bulgin PXP4043/C receptacle's 5 A; as drawn R138 10 mOhm trips at 1.897 to 2.288 A | L4E4-CURRENT-LIMITS.md; the chosen values (R138); the outlet's bench procedure | MAKER rows (SLVSDG8B), INFERRED; DRAFTED R-02 | VI(TRIP)'s row at L4-E4's bench (a); J_USBC_OUT's header and its rating (R-30) | 5.5 |
| LH-06a | IF-AB-POWER currents (+54V_POE) | monitor | full scale 81.92 mV over 5 mOhm is 16.384 A (Current_LSB 0.5 mA, CAL 2048); 3.682 A at a 10.0 V stack for 0.6 A at 54 V over 0.88, 14.33 A at the stage's fault bound (72.38 mV) | L4-POWER-ARCHITECTURE.md; DOWNSTREAM-REGISTER.md; 1d row IF-13 and part A; R-27 | INFERRED from MAKER rows (SBOS547C); DRAFTED R-06; PROVISIONAL (R227's pulse rating) | R-101 (R227's pulse rating and capacitance envelope); R-120, R-121 (L10's L(I) at temperature) | 5.4, 5.11 |
| LH-06b | FW-A09 | U17's readings restated | its readings are the PoE stage's INPUT current and POE_VIN (VBUS pin 8 is on POE_VIN; VBAT is POE_VIN plus the shunt's drop) | DOWNSTREAM-REGISTER.md; R-27 | INFERRED; DRAFTED R-06 | as LH-06a | 5.11 |
| LH-07a | FW-A16 | LH-07's condition | IIN_HOST is written 4.70 A only on a board A whose netlist carries the ILIM_HIZ network (H3, FW-A18); on a board without it the derated 4.00 A of r11dep applies (R11 10 mOhm) | LAYER5-HANDOVER.md; DOWNSTREAM-REGISTER.md; LH-07; R-25 | INFERRED (L4-E4, L4-E5, r11dep); FW-A18 OWED | R-03's network drawn (Layer 8), after which the condition is met on every regenerated board | 5.11 |
| LH-07b | V-A08 | restated for the selected entry | the entry's U6 never asserts FLT_I (its current over the breaker's lowest 6.364 A for less than 0.247 ms, its filtered short-circuit sense under 10.36 A), VIN_RAW never falls below 7.24 V | DOWNSTREAM-REGISTER.md; L4E11-SOURCE-ONLY-AND-ENTRY.md; R-135, R-76; 7a (E11-21) | MAKER rows; DRAFTED R-123 | R-123's parts; R-76 reads it on the bench | 5.6, 5.11 |
| LH-08 | V-E14 | REQ-015's bench row | the vehicle supply reversed at -36 V and then at +40 V: no damage; DC_P, DC_F and Q1's VDS recorded (at most 66.2 V reversed); the entry's OV trip inside 39.6 to 41.22 V | LAYER5-HANDOVER.md; LH-08 | TEST row (the bounds MAKER and INFERRED); DRAFTED R-123, R-17 | R-123 and R-17 applied; the interconnect's resistance ceiling (R-130) | 5.4 |
| LH-09 | V-E15 | REQ-016's backstop bench row | the input current at which SWEN falls, at 17.6 V and 25 V, inside 3.0468 to 3.7408 A at 25 V, at commissioning and at layer 8's interval | LAYER5-HANDOVER.md; L4-POWER-ARCHITECTURE.md; LH-09; 1d row IF-02 | TEST row (the bounds MODELED, L4-E7R); DRAFTED R-19 to R-21 | L4-E7R's stocked RIMON_IN and R66 | 5.4 |
| LH-10a | FW-C08 | SHORE_INHIBIT restated | Asserted only on the operator's 'inputs off' and on the water-on-floor isolation, never for a temperature or 'no charge' hold | L4E11-SOURCE-ONLY-AND-ENTRY.md; 7a | RULE (L4-E11's R-a, SESSION) | none: a rule, reversed only by L4-E11 reversing R-a | 5.7, 5.11 |
| LH-10b | FW-A14 | CHG_INHIBIT restated | asserted only by firmware, never as a charge hold (a hold is the CHRG_INHIBIT bit or ChargeCurrent 0, FW-A19), and never while the pack cannot discharge (S2, S4 | L4E11-SOURCE-ONLY-AND-ENTRY.md; 7a | RULE (SESSION) | none | 5.7, 5.11 |
| LH-10c | PANEL.md section 10 | the charge-hold sentence | No hold uses the CHG_INHIBIT line or SHORE_INHIBIT. | L4E11-SOURCE-ONLY-AND-ENTRY.md; 7a | RULE (SESSION) | none | 5.11 |
| LH-10d | FW-E13 | DCIN_PGD the entry's fault flag | Read it as the entry's FAULT FLAG, no longer a power-good line | L4E11-SOURCE-ONLY-AND-ENTRY.md; apply_gen_sch_e_entry.py; 7a; the entry draft's pin map | DRAFTED R-123 | R-123 applied: until then the drawn line is the LM5069's power good | 5.7 |
| LH-10e | FW-A19 | rule R-a, the hold's flag and the state table | S4 (both off: below -9 C, SHUTDOWN, a permanent fail, no pack) the gauge holds and as drawn the bit is NOT set | L4E11-SOURCE-ONLY-AND-ENTRY.md; section 4 (rule R-a) | RULE (SESSION); S2's N2 OPEN; the (B1) half DRAFTED R-157, R-158 | N2 (Q-TI-3, E11-06): whether VSYS stays regulated in S2 with the charge inhibited; under (B1) S4's exception is withdrawn (R-158) | 5.6, 5.11 |
| LH-10f | FW-A20 | rules R-b and R-b' | exactly two settings, 0x0000 (no charge) and 0x0200 (1024 mA set), and no value under 0x0200 | L4E11-SOURCE-ONLY-AND-ENTRY.md; section 4 (rule R-b), 15c (R-b') | MAKER row (SLUSE66A p.10), INFERRED; PROVISIONAL | E11-22: cases (ii) and (iii), and board P's copper giving TI's 50 C/W | 5.11 |
| LH-10g | FW-A21 | rule R-c, the shedding sequence | P1 shed, the two mixer fans, the HF module, the Geiger module and the 5G module held off, the bridge, GNSS, Iridium and the panel (the SOS path) kept, P1 at most 20.51 W at VBAT | L4E11-SOURCE-ONLY-AND-ENTRY.md; 3g, section 4 (rule R-c), 15b | MODELED (hc2's and rv-pwr's models); PROVISIONAL | E11-06 (P1 measured, the front end's efficiency), E11-23 (the warm-up time), E11-31 (the start's first window) | 5.6, 5.11 |
| LH-10h | FW-A22 | rule R-d | the image keeps PCHG_COMM 1 and the SUV check (SUV permanent fail at 1.0 V), with Q-TI-7 open | L4E11-SOURCE-ONLY-AND-ENTRY.md; section 4 (rule R-d) | RULE (the image) | Q-TI-7's answer | 5.11 |
| S27-B1 | FW-A23 | (B1)'s registers at boot | EN_OOA written 0 first (the printed VSYS accuracy holds only after that write, E11-31); ChargeCurrent written for any charge (0 A at POR and after the watchdog's 175 s | DOWNSTREAM-REGISTER.md; L4E11-SOURCE-ONLY-AND-ENTRY.md; R-158; 15a, 12c | MAKER rows (SLUSE65A); DRAFTED R-157, R-158 | R-157's release record; R-161 (E11-31) reads the registers back on the build | 5.6, 5.11 |
| LH-11a | FW-C15 | the margin hold as a mode | Trigger: a reading at or over 68.65 C of mixed air plus the reference's calibrated offset | L4E12-ELECTRONICS-THERMAL.md; section 6 (the hold's trigger window) | MODELED (L4-E12, SESSION); PROVISIONAL | the hold's reference placed in the mixed air or calibrated at T-H1 to +-0.899099 K (U-02's line); a measured lag over the 61 s assumption re-derives 68.65 C | 5.6, 5.11 |
| LH-11b | FW-E12 | the SGP41's own shutdown | Power the SGP41 off at a reading of 54.0 C on a TMP117 on its carrier (54.095833 C exact, rounded down: the SGP41 then at most 54.904167 C, under Table 5's +55 C); power it on, and use its output for REQ-042, only at or under 49.0 C (49.095833 C exact) | L4E12-ELECTRONICS-THERMAL.md; section 6 (the SGP41), 17.1 | INFERRED on MAKER rows (Sensirion Tables 4 and 5, the TMP117's 0.15 C); PROVISIONAL; the switch and the carrier TMP117 OWED | R-139's lag test: a lag over 0.254167 K (a time constant over 83.0 s) re-derives 54.0 and 49.0 C; the switch and the TMP117 drawn on board E | 5.11 |
| SEQ-01 | board_to_board.power_line_states | SLOT_EN1..3 (reset, default, cable-out, the hold) | SLOT_EN1..3: {reset: "LOW (A R30, R34, R38 100 k to GND; the RP2040's pads reset as inputs)" | L4-POWER-ARCHITECTURE.md; 4c (the cold start on the pack) | VERIFIED pulls (IF-BC-PANEL); the hold OWED (FW-C02) | the SLOT_EN hold drawn (Layer 8, board C or A) closes 5.6's open item | 5.6, 5.7 |
| SEQ-02 | board_to_board.power_line_states | VSYS_DOCK (DRAFTED) | VSYS_DOCK: {reset: "DRAFTED (R-157, R-177, R-181): U42's dVdT ramp 3.99 to 8.75 ms once VSYS is present (C237 22 nF) | L4E11-SOURCE-ONLY-AND-ENTRY.md; 16e (the inrush) | INFERRED (TI's Equation 2); DRAFTED R-181 | R-181's release record | 5.6, 5.7 |
| SEQ-03 | board_to_board.power_line_states | EN_OOA and ChargeCurrent at boot | EN_OOA: {reset: "1b at POR (SLUSE65A; (B1) only, DRAFTED R-157)" | L4E11-SOURCE-ONLY-AND-ENTRY.md; 15a (the sequences), 12c | MAKER (SLUSE65A); DRAFTED R-157 | R-157's release record | 5.6, 5.7 |
| SEQ-04 | IF-AE-DOCK cable_out_states | VSYS_DOCK open at E | VSYS_DOCK: "DRAFTED: open at E; board E's auxiliary domain unpowered, its controller dark, read as HOT-R1 lost; U42 unloaded" | L4E11-SOURCE-ONLY-AND-ENTRY.md; 15a (a lost pin 1) | INFERRED; DRAFTED | none | 5.7 |
| SEQ-05 | IF-PE-PACK sequencing | the pack's connection pulse | the inrush into VBAT's capacitors 242.9 A peak, time constant 33.8 us (over ASCD's 55.6 A for 61.5 us against its 183 us delay | L4-POWER-ARCHITECTURE.md; L4E11-SOURCE-ONLY-AND-ENTRY.md; 4a (pack connected); 16d, 17b | MODELED; PROVISIONAL | E11-30: the pulse qualification on six BUK6Y10-30PX samples at 267.2 A and 37.2 us; VF and ISM hot | 5.6 |
| SEQ-06 | IF-PE-PACK sequencing | the held pack under (B1) | VSYS piecewise (SRN under 12.054 V: at least 12.054 V; SRN over 12.546 V: VSRN + 150 mV within 2 percent; between: at least 11.96 V), the pack feeds no kit load (its monitor 0.1398 mA | L4-POWER-ARCHITECTURE.md; L4E11-SOURCE-ONLY-AND-ENTRY.md; 4a (the charge inhibited); 15a, 15d | MAKER rows (SLUSE65A), INFERRED; DRAFTED R-157; PROVISIONAL | E11-31 (R-161): the held pack current at most 1 mA; D3's hot leakage and the body diodes' current not bounded on held evidence | 5.6, 5.7 |
| SEQ-07 | IF-A-HEAT sequencing | the mat on measured headroom | the mat runs on measured headroom (R-c, FW-A21): on only while the source's measured headroom over the load is at least its 8.58 W | L4E11-SOURCE-ONLY-AND-ENTRY.md; 3g | MODELED; PROVISIONAL | E11-06 | 5.6 |
| SEQ-08 | IF-E-FANS power | the fans' supply under (B1) | under (B1) VSYS_E, 9.539 to 17.375 V (L4-E11 15a, 16e; DRAFTED R-177): the fans are declared 12 V class, their maximum supply voltage against 17.375 V and their least operating voltage against 9.539 V TBD (HF-F05, E11-35, R-179) | L4E11-SOURCE-ONLY-AND-ENTRY.md; 15a (VSYS_E's range), 16e (the drop) | INFERRED; DRAFTED R-177; TBD (no fan named) | E11-35 (R-179): a fan named with its range | 5.4 |
| SEQ-09 | IF-EXT-DC default_state | the charger before any host write | the charger before any host write: as drawn ChargeCurrent 256 mA at POR (TI's E2E answer) and after the 175 s watchdog, under (B1) 0 A until firmware writes it | L4-POWER-ARCHITECTURE.md; 4c (power-on under (B1)), 4g | MAKER (TI's E2E answer; SLUSE65A); DRAFTED R-157 | none | 5.7 |
| SEQ-10 | FW-C08 hardware fact | the entry's UVLO pin under SHORE_INHIBIT | E's Q8 pulls the entry's UVLO pin low when it is high (as drawn the LM5069's HS_UVLO; on the selected entry the TPS48110-Q1's EN/UVLO on the same net, DRAFTED R-123) | apply_gen_sch_e_entry.py; the entry draft's pin map and part list (Q8 kept) | NETLIST (the draft's text); DRAFTED R-123 | R-123 applied | 5.7 |
<!-- l5pwr-table:end -->

## 5. check_contracts.py before and after

Run on the committed netlists (A23, B19, C8, D9, E7, P2 phase folders) with `VERDICT_DIR` in the session's scratchpad, never
in the tree, before any edit and after the last one:

| Run | Set verdict | Contracts | The RF-002 walk (its own group) |
|---|---|---|---|
| before (`2c240414`) | PASS of 99 | 99 pass, 0 fail, 0 unjudged, 0 undecided, 0 rails unsplit | 15 PASS, 11 UNDECIDED |
| after (this pass) | PASS of 99 | the same | the same |

The two stdouts are identical line for line, and the two set verdicts differ only in their `ts`, `tools` and `version` fields (provenance, not an answer: the tools folder holds `pcb_interfaces.yaml` and the tests, both edited). **Why
nothing changed:** `check_contracts.py` is a netlist reader. It compares the committed netlists' pin maps against each other and
its own ALIAS table; it reads neither `pcb_interfaces.yaml` nor the two documents, and this pass edits no netlist, no generator
and not the checker. The dock's pin 1 stays GND on both committed netlists, so the contract's `pins` map (kept as the netlists')
and the checker agree; the alias VSYS_DOCK and VSYS_E that the selected architecture needs arrives in the checker's ALIAS table
with L4-E11's `apply_pcb_interfaces_dock.py` (register row R-178), together with the generator drafts R-157 and R-177, after their
release records. A check_contracts reading that moves because of this pass would be a defect of the pass; none moved.

## 6. The Layer 5 criteria this pass moves (Layer 5's reading; the handover page's status is the integrator's to set)

| Criterion | At H2 (`LAYER-STATUS.md`) | After this pass | What remains |
|---|---|---|---|
| 5.2 every interface owned at both ends with its connector | PARTLY: the first twelve lack the pass-2 fields | PARTLY, further: IF-AE-DOCK, IF-PE-PACK, IF-AB-POWER and IF-EXT-USB carry every pass-2 field (hc5's `check_contract_fields.py --all`: "carries every field"; IF-EXT-USB gained its `ends`) | eight of the first twelve still lack them; the IDC headers' MPNs (EQ-21); E5's end has no part or src (no schematic) |
| 5.4 electrical levels stated per interface | PARTLY | PARTLY, further: the power interfaces' levels with their Layer 4 basis and marks (IF-EXT-DC both inputs, IF-AE-DOCK, IF-PE-PACK, IF-EXT-USB, IF-E-FANS) | the kit I2C bus's three segments (SC-59); the rest as at `e3aedb25` |
| 5.5 power capacity of each power interface with margin | PARTLY | PARTLY, further: IF-EXT-DC's currents against the breaker, the fuses and the interconnect; IF-AE-DOCK's in-service and fault currents against the 9 A pins and pin 1 against the 813 under U42; the outlet's trip against its 3 A contracts and the 5 A receptacle; the PoE monitor's scale | I-03's PS-ALLTX (INCONCLUSIVE at both ends); E5's targets and the ground share (S-74, S-75); the ribbon and SMP-MAX ratings; the 813's pulse capability (L4-F03, E11-38) |
| 5.6 sequencing across interfaces | OPEN: the SLOT_EN hold in no generator; HOT-R1 | PARTLY: L4-E9 section 4's source changes, startup, shutdown and faults as sequencing fields; the fans' start (FW-E11), the shedding sequence (FW-A21), the boot writes (FW-A23); `power_line_states` | the SLOT_EN hold still in no generator (OWED, Layer 8, board C or A), so H2's named item stays open |
| 5.7 reset, default and cable-out states for every control line | PARTLY | PARTLY, further: every power line of L4-E9 section 4 has its reset, default and cable-out state and its firmware row | TX_INHIBIT_n's fail-safe level (EQ-25); the rest as at `e3aedb25` |
| 5.11 firmware obligations affecting hardware explicit | PARTLY | PARTLY, further: FW-A19 to FW-A23, FW-C15, FW-E11 to FW-E13 added; FW-A09, FW-A14, FW-A16, FW-C08 restated; PANEL.md section 10 restated; V-A11, V-C15, V-E11 to V-E16 | the reduced-mode duties of layer 2's m13; the SGP41's switch and carrier TMP117 not drawn (FW-E12 over parts OWED) |
| 5.13 interface contracts consistent with the tree | PARTLY | PARTLY: the drawn board first, every draft DRAFTED with its row; check_contracts PASS 99 of 99 unchanged | the edit dates every `interfaces.py` reading (CONFIG_INPUTS): their re-take on every board is owed, as after H2 |

Not moved: 5.3 (pinouts identical at both ends) stays MET, with the same reading before and after.

## 7. The PROVISIONAL entries and their invalidation triggers

Section 3 of `l5pwr_contracts.out` lists them by id; the groups:

- **B6's loop floor** (S27-B6, S27-03 row 3, IF-EXT-DC's protection and bench): the guard already on holds every rating with
  its margin only from a source loop of at least 3.30 uH (U5 0.2396 V of +-0.240 V); invalidated or closed by B6-ENG-1's route
  (R-180 the loop bounded and measured, R-186 Analog Devices' answer, R-187 the sense moved) and by L4-E7's round 3 on B6.
- **U-04's start** (LH-01a, LH-01b, LH-10e, LH-10g, SEQ-07, SEQ-06): E11-06 (P1 at most 20.51 W, the front end at least
  0.88021, N2 in S2), E11-09, E11-23, E11-31 (the start's first window, the held pack current at most 1 mA).
- **L4-F03's fault qualification** (S27-01, S27-02a, S27-02b): E11-38 (U42's limit inside 1.471 to 1.802 A, the hard short's
  cases, the 813's resistance), E11-35 (a fan named whose start exceeds 0.5713 A).
- **The pack's connection pulse** (SEQ-05): E11-30 (six BUK6Y10-30PX at 267.2 A and 37.2 us; VF and ISM hot).
- **R-b's cases** (LH-10f): E11-22 (cases (ii) and (iii), board P's copper).
- **PANEL-ACC and the stage's bound** (LH-02a, LH-02b, LH-02c, LH-02d): R-35 (no unit accepted), R-101 (G_CM and the VIN+ bias),
  R-29 (the lead's gauge), R-148 (A-3(c)), R-122 (M2 on the loop's typical rows).
- **D-06's ratings** (LH-01c, LH-01d): R-113, R-115, R-129 to R-132; the hard short in service R-134.
- **The margin hold and the SGP41** (LH-11a, LH-11b): the hold's reference (placed in the mixed air or calibrated at T-H1 to
  +-0.899099 K, U-02's line) and the 61 s lag assumption; R-139's lag test (over 0.254167 K re-derives 54.0 and 49.0 C).
- **The PoE monitor** (LH-06a): R-101 (R227's pulse rating and capacitance envelope).
- **The pack chain** (LH-04b): PWR-F12 (FEA-004).

## 8. Decisions taken by the session (authority: SESSION, under the owner's standing rule of 26 September 2026)

1. **L4-E5's draft applied to the tree** by its own script, because R-23 assigns its application to Layer 5; `test_l4e5.py`'s
   apply fixture re-stated on the contract at `2c240414`. *Reverse:* revert the contract's FW-A16, FW-A18 and V rows by the
   script's own edits (it is reversible line for line).
2. **The dock's `pins` map kept as the committed netlists'** and the drafted pin 1 written as its own field `pin1_vsys_dock`,
   with L4-E11's dock draft's anchors kept intact. *Why:* criterion 5.3 and `check_contracts.py` judge the committed netlists,
   on which pin 1 is GND on both boards; a contract claiming VSYS_DOCK today would disagree with the checker's PASS, and the
   draft that flips the map is L4-E11's, release-guarded, applied with the generator drafts. *Reverse:* R-178's application.
3. **The ids** FW-A19 to FW-A23, FW-C15, FW-E11 to FW-E13, V-A11, V-C15, V-E11 to V-E16 (LH-08's and LH-09's V rows are V-E14 and
   V-E15; the handover left them to Layer 5), and the section headings' ranges moved with them.
4. **The power lines' states in one table** (`board_to_board.power_line_states`) rather than spread over contracts, because
   criteria 5.6 and 5.7 ask for every control line; `interfaces.py`, `review_packet.py` and `check_contract_fields.py` read other
   keys and are unaffected (verified by running them).
5. **CONOPS not edited**: its two halves (R-138, R-133) are drafted as `apply_conops_l5pwr.py` for the CONOPS owner, who rebinds
   the registry's and L4-E12's readings of CONOPS.md after applying it.
6. **"percent" spelled out** in every text written, as the newer contracts do; no em or en dash anywhere.
7. **The outlet's plate receptacle** named Bulgin PXP4043/C only as L4-E4 reads it (no vendor document is held); J_USBC_OUT's
   header stays TBD with R-30's effect.

## 9. Findings for other layers and the integrator

| ID | For | Finding | Next action |
|---|---|---|---|
| L5-F01 | Layer 4 (L4-E9, L4-E11, L4-E5) | The three files are pinned by sha256 in `l4e9_power_path.py` (hwfw, ifaces), `l4e11_power.py` (hwfw, panel) and `l4e5_source_control.py` (hwfw); after this pass each refuses "is not the pinned file" and `test_l4e9`, `test_l4e11` and 13 of `test_l4e5`'s predicates fail at that refusal. L4-E11's reader also `need()`s the pre-E11-03 texts of FW-C08, FW-A14 and PANEL.md's cold-hold sentence (lines 405 to 408), which its own E11-03 asked Layer 5 to change | re-pin at the merge (L4-E9's round 5 is planned); L4-E11 reads those three texts at a commit (its GIT_PINS mechanism) or re-states its `need()` on the restated texts |
| L5-F02 | the integrator | `pcb_requirements.yaml` binds five readings to PANEL.md's old content (CFL-001, CFL-005, CFL-014, CFL-015, CFL-016: `rules_lib.py requirements` reads 5 errors, and four predicates of `test_requirements.py` fail on that alone, since no trace page renders while the registry has an error); `pcb_interfaces.yaml` is a CONFIG_INPUT of `interfaces.py` | rebind the five on a judged reason (section 10's one sentence changed; sections 1 to 9 and 11 unchanged); re-take `interfaces.py` on every board, as after H2 |
| L5-F03 | Layer 8 board E, L4-E12 | The SGP41 (`E:U17`) has no load switch from the controller and no TMP117 on its carrier in the netlist; FW-E12 is an obligation over parts OWED | board E's generator draws the switch and the reference (L4-E12 section 6 names both) |
| L5-F04 | Layer 4 (L4-E4), Layer 8 board A | As drawn R138 10 mOhm trips at 1.897 to 2.288 A, under the outlet's 3 A PD contracts: the drawn outlet cannot deliver its PDOs until R-02 applies (L4-E4's own reading, now a contract statement in IF-EXT-USB) | R-02's release |
| L5-F05 | Layer 6, Layer 7 | IF-EXT-USB's plate receptacle (Bulgin PXP4043/C) is named only in L4-E4's page; no vendor document is held; J_USBC_OUT is unnamed (R-30); the outlet lead's construction at 3 A is TBD | the parts filed with their sheets; ASSEMBLY.md's row |
| L5-F06 | Layer 8 (board C or A) | The SLOT_EN hold across a panel reset is still in no generator (FW-C02 OWED): criterion 5.6's item named at H2 stays open after this pass | the hold drawn |
| L5-F07 | the CONOPS owner | CONOPS section 4 carries neither the margin hold as a mode nor the source-only statement | `apply_conops_l5pwr.py --write`, then the rebinds |
| L5-F08 | the integrator (E5) | IF-AE-DOCK's E5 end has no `part`, `src` or ref because the block has no schematic; hc5's field checker reports it as information | a `what` end is the honest form; no action unless the checker's rule changes |

## 10. What this record does not claim

- Nothing is verified on hardware: every V row is owed, every DRAFTED figure is a draft's, every PROVISIONAL entry stands on an
  open row. Software tests establish this record's own behaviour only.
- The criteria table of section 6 is Layer 5's reading; `LAYER-STATUS.md` is the integrator's page.
- The contracts do not close U-01, U-02, U-04 or B6; they carry Layer 4's conditions into the interfaces with their triggers.

## 11. Reproduce

`python3 v2/docs/records/l5pwr/l5pwr_contracts.py` prints the table (a second at most, stdlib only); `_bin/regen_out.py` is the
only way the committed output is regenerated. `env -C v2/ecad/tools/tests python3 run.py test_l5pwr` holds the predicates.
`apply_l5pwr.py <target> --check` on the tree refuses "already applied"; on the files at `2c240414` (the contract after
`../l4e5/apply_fw_a16.py`) it checks OK and reproduces the tree's files byte for byte (`test_l5pwr.py` does both).
