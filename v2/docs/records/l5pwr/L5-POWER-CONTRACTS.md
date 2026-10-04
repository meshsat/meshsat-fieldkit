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

**Restated at set 28 (finding F-12 of `../int28b/RESULT.md`, 3 October 2026; authority SESSION).** Set 27 corrected two Layer 4
records after this pass: L4-E7's round 5 withdrew the solar guard's reference loop as a passing floor (D-10's guard-on case OPEN),
and L4-E11's section 18 moved the mixer fans off VSYS_E onto U22's regulated rail (+12V_FAN) and called the hard short's figure a
test target, not a bound. On set 28's line the reader refused ("S27-02b: figures not printed by l4e11out, reg: ['PWM ramp']", and
S27-B6 on three figures L4-E9's page no longer prints). Six rows are restated in section 4a (S27-B6, S27-01, S27-02a, S27-02b,
S27-03, SEQ-08): the table keeps the text written and gives the restated mark and trigger; section 4a names the figures that no
longer stand, why, the Layer 4 text that replaced them with its figures parsed from the file, the contract value that changes, and
the targets as set 28 carries them. Record l5r2 restated two of them in place (S27-02b, SEQ-08) and superseded two beside the text
written (S27-01, S27-02a); the solar guard's texts (S27-B6, S27-03) and two sentences of the dock's pin 1 field still carry the
withdrawn readings (findings L5-F09 and L5-F10, section 9).

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
- **PROVISIONAL entries** rest on B6's guard-on case (OPEN since L4-E7's round 5, which withdrew the loop floor this pass first
  read; every entry on it names B6-ENG-1, section 4a), U-04's start (E11-06, E11-31), L4-F03's fault qualification (E11-38) and
  the other open rows named in section 7.
- **Set 28's restatement (F-12).** A row whose cited figure set 27's Layer 4 corrections changed is restated, never edited: the
  text written stays what the targets carried at `1e18a1ca`; its figures that no longer stand are checked as printed by the row's
  sources at `2c240414` (read from this branch's history); the Layer 4 text that replaced them is a pattern with no typed number,
  matched exactly once in the tree's source, and its figures are parsed from the match; the targets are read at set 28's
  `5515ecc0` to say whether record l5r2 restated the row in place or a withdrawn text is still there. The restated mark and
  trigger replace the written ones in section 4's table and in section 7.
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
| S27-B6 | IF-EXT-DC | protection (the guard already on) | every rating with its margin only from a source loop of at least 3.30 uH (U5 0.2396 V of +-0.240 V, a DESIGN TARGET), NOT under it (at 1.00 uH U5 0.5287 V) | L4-POWER-ARCHITECTURE.md; 1d row IF-01, 4e (the guard-on row), 8a D-10 (restated at set 28, F-12, section 4a; as written: 4e (the guard-on row), 8a D-10) | MODELED (L4-E7 round 5); DRAFTED R-173; OPEN (D-10's guard-on case, an absolute-rating violation at a connector fault), PROVISIONAL | B6-ENG-1, the engineer's stage question (R-180 an input only; R-186 Analog Devices' answer; R-187 does not hold, result (ii)); its wider form B6-ENG-2 (R-189, D-16) | 5.4 |
| LH-03a | IF-AE-DOCK | vin_raw.voltage | solar 7.378 V (the corrected knee's certain HIZ, L4-E9 R-03, a specification) to 30.15 V (the tracker's raised ceiling, R10 232 k; L4-E5, DRAFTED); vehicle 9 to 36 V at the plug (VIN_RAW 8.148 V at 5.983 A from a 9.00 V plug; INFERRED); at most 41.22 V | L4-POWER-ARCHITECTURE.md; 1d row IF-06 | INFERRED; R-03 a specification; DRAFTED R-03, R-123 | R-03's network drawn to the knee (Layer 8); the OV maximum follows R-123's parts | 5.4 |
| LH-03b | IF-AE-DOCK | vin_raw.in_service | fault current at most 11.65 A at R11 8 mOhm and R12 12 mOhm (13.315 A at 7 mOhm), inside the declared 14.10 A and the four 9 A pins (3.88 A each with one open) | L4-POWER-ARCHITECTURE.md; LAYER5-HANDOVER.md; 1d rows IF-06 and IF-07; LH-03 (the 3.88 A with one pin open) | MODELED; R11 and R12 DRAFTED R-04, R-01 | R11's 7 mOhm fallback (V-A07) moves the fault bound to 13.315 A, still inside 14.10 A | 5.5 |
| LH-03c | IF-AE-DOCK | vin_raw.properties | U34's restart guard falls at 6.754 to 7.139 V (R14 76.8k, L4-E9 R-124, DRAFTED), at least 0.1 V under the knee's certain HIZ 7.378 V; as drawn it falls at up to 8.309 V | L4-POWER-ARCHITECTURE.md; 1d row IF-07, 4a | INFERRED; DRAFTED R-124 | R-124's fitted parts: the guard's fall read on the regenerated board | 5.7 |
| LH-04a | IF-AE-DOCK pack_pins; IF-PE-PACK power | charge | at most 3.0 A (FW-A02; REQ-075 3.06 A), under the gauge's OCC 5 A | L4-POWER-ARCHITECTURE.md; 1d row IF-10 | MAKER (the gauge's OCC), INFERRED | FW-A02's setting; R-28 re-derives it at bring-up | 5.5 |
| LH-04b | IF-AE-DOCK pack_pins; IF-PE-PACK power | service | PS-ALLTX's 18 A at an 11.48 V stack and OCD1's 20 A below 10.42 V (pwr_budget.out D-11 line; MODELED) | L4-POWER-ARCHITECTURE.md; LAYER5-HANDOVER.md; 1d row IF-10; LH-04 as L4-E9's rounds 7 and 8 corrected it (out 30) (restated at set 29, L5-F13, section 4a; as written: 1d row IF-10; LH-04) | MODELED (L4-E9 out 30, on Layer 9's final drafts); PROVISIONAL; D-17 OPEN | PWR-F12 (FEA-004): the chain's short-time rating at the peak service current and F2 near its hot corner; D-17 (L4-E9 8a): the all-transmit basis against REQ-018's pass line | 5.5 |
| S27-01 | IF-AE-DOCK | pin1_vsys_dock (the new row of set 27) | U42's I(OL) 1.4713 to 1.8018 A at R(ILIM) 11.0 kOhm 0.1 percent | L4E11-SOURCE-ONLY-AND-ENTRY.md; l4e11_power.out; 16e, 17a, 18b; out 16e, 17a, 18b (restated at set 28, F-12, section 4a; as written: 16e, 17a; out 16 and 17) | INFERRED from MAKER rows (SLVSET9G), the branch current MODELED (L4-E11 18b); DRAFTED R-157, R-177, R-178, R-181; PROVISIONAL (L4-F03: remedy drafted, qualification open) | E11-38 (R-184): U42's limit read outside its band, the hard short's recorded peak over its test target (it revises L4-E11 17a), the 813's resistance after the cases; E11-35 (R-179): a fan's measured start over U42's room at the declared branch | 5.2, 5.5, 5.7 |
| S27-02a | IF-AE-DOCK pin1_vsys_dock; IF-E-FANS sequencing | the fans' start rule | both fans together at most 0.3356 A each, one at a time at most 0.5713 A (the other running at 0.1 A), VSYS_E at the least limit at least 9.494 V at the supplement floor | L4E11-SOURCE-ONLY-AND-ENTRY.md; l4e11_power.out; DOWNSTREAM-REGISTER.md; 18, 18b; out 18, 18b; R-179 (restated at set 28, F-12, section 4a; as written: 17a; out 17) | INFERRED (L4-E11 18b); DRAFTED R-177, R-181; PROVISIONAL (the start current NOT READ) | E11-35 (R-179): the named fans' start current read over U42's room at the rail; U42's limit read outside its band (E11-38, R-184) | 5.6, 5.11 |
| S27-02b | FW-E11 | the fans' start stagger as a firmware row | Start the mixer fans one at a time, each with a PWM ramp, never both within 1 s and never while U12 starts (E11-39, R-188) | l4e11_power.out; DOWNSTREAM-REGISTER.md; out 18c (E11-39 restated); R-188 (restated at set 28, F-12, section 4a; as written: out 17 (E11-39); R-188) | RULE (L4-E11 17a and 18c, SESSION); DRAFTED R-177, R-181; PROVISIONAL | E11-35 (R-179): the named fans' start current read over U42's room at the rail; U42's limit read outside its band (E11-38, R-184) | 5.6, 5.11 |
| S27-03 | V-E16 (IF-EXT-DC bench) | R-176 rows 1 to 6 where they bind the solar port | (5) Q13's leakage at the hot end, under 32.1 uA; (6) no short-circuit trip with C126 at 330 pF in operation and under CS116 (R-174) | DOWNSTREAM-REGISTER.md; R-176 (rows 2 and 3 as L4-E7's round 5 restated them) (restated at set 28, F-12, section 4a; as written: R-176) | TEST rows (the bounds MODELED and MAKER); DRAFTED R-173; row 3 OPEN (no loop claimed to pass), PROVISIONAL | row 3: B6-ENG-1 decides the stage (R-180 an input only, R-186, R-187 not holding; B6-ENG-2, R-189); rows 2 and 3 filed against R-176's bounds at both fault positions | 5.4 |
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
| SEQ-08 | IF-E-FANS power | the fans' supply under (B1) | under (B1) VSYS_E, 9.539 to 17.375 V (L4-E11 15a, 16e; DRAFTED R-177): the fans are declared 12 V class, their maximum supply voltage against 17.375 V and their least operating voltage against 9.539 V TBD (HF-F05, E11-35, R-179) | L4E11-SOURCE-ONLY-AND-ENTRY.md; l4e11_power.out; 18, 18a; out 18, 18a (restated at set 28, F-12, section 4a; as written: 15a (VSYS_E's range), 16e (the drop)) | INFERRED (L4-E11 18a); DRAFTED R-177; PROVISIONAL (the start current and the PWM input level NOT READ) | E11-35 (R-179): the named fans' start current and PWM input level read; R-177's release (U22 and the four-wire headers drawn) | 5.4 |
| SEQ-09 | IF-EXT-DC default_state | the charger before any host write | the charger before any host write: as drawn ChargeCurrent 256 mA at POR (TI's E2E answer) and after the 175 s watchdog, under (B1) 0 A until firmware writes it | L4-POWER-ARCHITECTURE.md; 4c (power-on under (B1)), 4g | MAKER (TI's E2E answer; SLUSE65A); DRAFTED R-157 | none | 5.7 |
| SEQ-10 | FW-C08 hardware fact | the entry's UVLO pin under SHORE_INHIBIT | E's Q8 pulls the entry's UVLO pin low when it is high (as drawn the LM5069's HS_UVLO; on the selected entry the TPS48110-Q1's EN/UVLO on the same net, DRAFTED R-123) | apply_gen_sch_e_entry.py; the entry draft's pin map and part list (Q8 kept) | NETLIST (the draft's text); DRAFTED R-123 | R-123 applied | 5.7 |
<!-- l5pwr-table:end -->

## 4a. Restated at set 28 (finding F-12)

`l5pwr_contracts.out` section 1a prints the same with the line of every citation. "The targets at set 28" reads
`pcb_interfaces.yaml` and `HW-FW-CONTRACT.md` at `5515ecc0`: RESTATED IN PLACE (the text written is gone and record l5r2's text
stands), SUPERSEDED IN PLACE (l5r2's sentence stands beside the text written) or NOT RESTATED; a withdrawn text still there is a
finding of section 9. The figures that no longer stand are the ones the row cited; the replacing text is quoted from the file.

**At set 29 (finding L5-F13, the coordinator's integration correction of 4 October 2026).** Row LH-04b is restated the same way.
L4-E9's round 7 corrected LH-04's pointer (it had read rv-pwr's PS-ALLTX PLAN line as if it were decision D-11's all-transmit
basis) and its round 8 restated it on Layer 9's final drafts, so the two stack voltages the row cited are no longer printed by
L4-E9's page or handover. The `service` strings of IF-AE-DOCK `pack_pins` and IF-PE-PACK `power` in `pcb_interfaces.yaml` still
carry the withdrawn pointer: NOT RESTATED, finding L5-F13 of section 9.

<!-- l5pwr-restated:begin -->
| id | cited at `2c240414`, no longer standing | why (the Layer 4 change: set 27's, or L4-E9's rounds 7 and 8 for a row restated at set 29) | what replaced it (file: the text, its figures parsed) | contract value | the targets at set 28 (`5515ecc0`) |
|---|---|---|---|---|---|
| S27-B6 | 0.2396, 0.5287, 60.3, 3.30 uH | L4-E7's round 5 withdrew round 2's reference loop as a passing floor: at that loop a fault at the connector puts U5's pins past their absolute maximum, so D-10's guard-on case is OPEN and no loop is claimed to pass | L4-POWER-ARCHITECTURE.md: "OPEN for the guard-on case: an absolute-rating violation at a connector fault (round 2's 3.30 uH WITHDRAWN as a passing floor"; L4-POWER-ARCHITECTURE.md: "at round 2's 3.30 uH reference loop, no loop claimed to pass (L4-E7's round 5)"; L4-POWER-ARCHITECTURE.md: "U5's pins, the complete budget, -0.3021 to +0.2591 V at a fault at the connector (past the -0.3 V ABSOLUTE MAXIMUM)"; L4-POWER-ARCHITECTURE.md: "inside 20 V; at 1.00 uH U5 0.5858 V"; L4-POWER-ARCHITECTURE.md: "turns Q12 off: at most 62.7 A within 11.4 us" | CHANGES: the guard-on case is no longer every rating with its margin from the reference loop; it is OPEN (an absolute-rating violation at a connector fault, no loop claimed to pass), with U5's pins at the reference loop and at the low loop and the turn-off current as parsed above; the stage question is the engineer's B6-ENG-1 | NOT RESTATED; the text written still at pcb_interfaces.yaml:1243; finding L5-F09 |
| LH-04b | 11.48, 10.42 | L4-E9's round 7 corrected LH-04's pointer, which had read rv-pwr's PS-ALLTX PLAN line and not the floor's basis (decision D-11's all-transmit basis), and its round 8 restated it on Layer 9's final drafts | LAYER5-HANDOVER.md: "decision D-11's all-transmit basis at 18 A from a 13.898 V stack as drawn and 14.774 V on the final drafts, OCD1's 20 A only below a 13.442 V stack there"; L4-POWER-ARCHITECTURE.md: "decision D-11's all-transmit basis at 18 A from a 13.9 V stack as drawn, 14.77 V on the final drafts, needing 16.214 V rest against REQ-018's 15.5 V (D-17 OPEN" | CHANGES: the pointer is no longer the PS-ALLTX PLAN line's stack voltages; it is decision D-11's all-transmit basis and OCD1's stack as parsed above, and that basis is not supplied from REQ-018's pass line (D-17 OPEN); the continuous and the peak service currents stand | NOT RESTATED; the text written still at pcb_interfaces.yaml:768; withdrawn text still at pcb_interfaces.yaml:768: "PS-ALLTX's 18 A at an 11.48 V stack and OCD1's 20 A below 10.42 V"; finding L5-F13 |
| S27-01 | 0.1486, 9.539, 11.905, 28.6 | L4-E11 section 18 put the mixer fans on U22's regulated rail and declared the dock branch afresh (18b), so the drop, VSYS_E at the floor and the contact's share are re-derived (18b restates the floor, not VSYS_MIN's start); and L4-E11 17a, after the recheck, calls the hard short's figure a resistive extrapolation and E11-38's test target, not a bound | l4e11_power.out: "with U12's 0.8 A: 1.3208 A DECLARED on IF-AE-DOCK pin 1 (was 1.0 A"; l4e11_power.out: "the drop at the floor with 1.3208 A: 0.1795 V, VSYS_E 9.508 V; at U42's least limit 9.494 V"; l4e11_power.out: "the contact at 37.7 % of 3.5 A"; l4e11_power.out: "A resistive EXTRAPOLATION, not a bound (I): 566 A would flow"; l4e11_power.out: "566 A for 4.5 us (1.441 A2s) is E11-38's TEST TARGET for the recorded peak" | CHANGES: the branch current, the drop, VSYS_E at the floor and the contact's share are 18b's, parsed above; the excerpt, U42's band at R(ILIM), stands (the resistor renamed R228); the hard short's figure keeps its number but is a test target, no longer a ceiling | SUPERSEDED IN PLACE (record l5r2); the text written still at pcb_interfaces.yaml:703; restated pcb_interfaces.yaml:720: "so the branch is declared 1.3208 A (U12 0.8 A, U22 0.5208 A at the floor with both fans at full speed)"; restated pcb_interfaces.yaml:722: "the contact at 37.7 percent of 3.5 A, VSYS_E 9.508 V at the floor"; withdrawn text still at pcb_interfaces.yaml:706: "a short applied while on at most 566 A for at most 4.5 us (a ceiling, no inductance credited; INFERRED)"; finding L5-F10 |
| S27-02a | 0.3356, 0.5713, 0.1 A | L4-E11 section 18 withdrew the fans directly on VSYS_E; on U22's regulated rail the start rule in amperes on VSYS_E is superseded (R-179) by the room U42 leaves at the declared branch (18b) | l4e11_power.out: "no fan read prints a range covering VSYS_E's 9.494 to 17.375 V, so 15a's fans directly on VSYS_E is WITHDRAWN"; DOWNSTREAM-REGISTER.md: "the supply range question of 15a to 17a (17.375 V at the top, 9.539 V at the bottom, 0.3356 and 0.5713 A on VSYS_E) is superseded by the rail"; l4e11_power.out: "with one fan running and U12 on, U42's room 0.1504 A leaves 1.21 W at the rail for the other fan's start" | CHANGES: the rule is no longer the both-together and one-at-a-time currents on VSYS_E; it is U42's room at the declared branch, as power at U22's rail for one fan's start, the start current NOT READ (E11-35); VSYS_E at U42's least limit stands | SUPERSEDED IN PLACE (record l5r2); the text written still at pcb_interfaces.yaml:713; restated pcb_interfaces.yaml:723: "the start rule above (0.5713 A and 0.3356 A on VSYS_E) is superseded by section 18b: with one fan running and U12 on, U42 leaves 0.1504 A of room, 1.21 W at the rail for the other fan's start"; withdrawn text still at pcb_interfaces.yaml:714: "firmware starts them one at a time with a PWM ramp, never both within 1 s and never while U12 starts (R-188)"; finding L5-F10 |
| S27-02b | PWM ramp, 0.5713 | L4-E11 18c restated the stagger for the fans on U22's rail (E11-39, R-188): the ramp is a PWM-duty ramp into the fan's PWM input, U22's start joins U12's, and the room is U42's at the declared branch (18b), the per-fan start current on VSYS_E superseded (R-179) | l4e11_power.out: "each by a PWM-duty ramp into the fan's PWM input, never both within 1 s and never while U12 or U22 starts"; DOWNSTREAM-REGISTER.md: "U42's room 0.1504 A at the floor"; DOWNSTREAM-REGISTER.md: "the current through J_DOCK pin 1 under 1.4713 A at every start" | CHANGES the rule's wording, not its intent: a PWM ramp becomes a PWM-duty ramp into the fan's PWM input, and never while U12 starts becomes never while U12 or U22 starts; the trigger's per-fan start current gives way to U42's room | RESTATED IN PLACE (record l5r2); restated HW-FW-CONTRACT.md:187: "Start the mixer fans one at a time, each by a PWM-duty ramp into the fan's PWM input, never both within 1 s and never while U12 or U22 starts (E11-39, R-188; L4-E11 18c)" |
| S27-03 | 75 V, 61 A, 3.30 uH | L4-E7's round 5 restated R-176: row 2's bound on PV_F and row 3's turn-off current changed, and row 3's pass from the reference loop was withdrawn (no loop is claimed to pass) | DOWNSTREAM-REGISTER.md: "PV_F at most 85 V, its slew and INP inside their absolute ratings"; DOWNSTREAM-REGISTER.md: "U21 turning Q12 off (at most 63 A, within 12 us)"; DOWNSTREAM-REGISTER.md: "no loop is claimed to pass (round 5): at 3.30 uH the pins' complete budget is outside +-0.240 V and B6-ENG-1 decides" | CHANGES in V-E16's rows 2 and 3, not in the excerpt (rows 5 and 6 stand): the parsed bounds replace those the pass wrote for rows 2 and 3, and row 3 is no longer a pass from any loop until B6-ENG-1 is decided | NOT RESTATED; the text written still at HW-FW-CONTRACT.md:313; withdrawn text still at HW-FW-CONTRACT.md:313: "D4 carries nothing, PV_F at most 75 V;"; withdrawn text still at HW-FW-CONTRACT.md:313: "U21 turning Q12 off (at most 61 A, within 12 us)"; withdrawn text still at HW-FW-CONTRACT.md:313: "a pass only for a loop at or over 3.30 uH until B6-ENG-1 is decided"; withdrawn text still at HW-FW-CONTRACT.md:261: "row 3 a pass only from a 3.30 uH loop until B6-ENG-1"; withdrawn text still at pcb_interfaces.yaml:1274: "row 3 a pass only for a source loop at or over 3.30 uH until B6-ENG-1 is decided"; finding L5-F09 |
| SEQ-08 | 17.375, 9.539 | L4-E11 section 18: no named fan's printed range covers VSYS_E, so the fans directly on VSYS_E are withdrawn; they run on U22's regulated rail, whose band sits inside the named fans' range (18a) | l4e11_power.out: "no fan read prints a range covering VSYS_E's 9.494 to 17.375 V, so 15a's fans directly on VSYS_E is WITHDRAWN"; l4e11_power.out: "the output 12.001 V (11.512 to 12.431 V at FB's limits with the 1 % divider) inside the fans' 10.8 to 13.2 V" | CHANGES: the fans' supply is U22's +12V_FAN, not VSYS_E; the supply range TBD is closed by the rail (DRAFTED); the start current and the PWM input level stay NOT READ (R-179, F-L7-11) | RESTATED IN PLACE (record l5r2); restated pcb_interfaces.yaml:1634: "+12V_FAN 12.001 V (11.512 to 12.431 V at FB's limits) from U22 on VSYS_E, inside the fans' 10.8 to 13.2 V" |
<!-- l5pwr-restated:end -->

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

- **B6's guard-on case** (S27-B6, S27-03 row 3, IF-EXT-DC's protection and bench; restated at set 28, F-12): as written, the
  guard already on held every rating with its margin from round 2's reference loop; L4-E7's round 5 withdrew that loop as a
  passing floor, so the case is OPEN (an absolute-rating violation at a connector fault, no loop claimed to pass; the figures in
  section 4a, parsed from L4-E9's page and the register). It closes only by B6-ENG-1, the engineer's stage question (R-180 an
  input only, R-186 Analog Devices' answer, R-187 not holding), and its wider form B6-ENG-2 (R-189).
- **U-04's start** (LH-01a, LH-01b, LH-10e, LH-10g, SEQ-07, SEQ-06): E11-06 (P1 at most 20.51 W, the front end at least
  0.88021, N2 in S2), E11-09, E11-23, E11-31 (the start's first window, the held pack current at most 1 mA).
- **L4-F03's fault qualification** (S27-01, S27-02a, S27-02b; restated at set 28, F-12): E11-38 (U42's limit inside its band,
  the hard short's recorded peak against its test target, the 813's resistance), E11-35 (the named fans' start current, NOT READ,
  against U42's room at U22's rail; the per-fan start current on VSYS_E this pass first wrote is superseded, section 4a).
- **The fans' supply** (SEQ-08; restated at set 28, F-12): U22's rail, DRAFTED (R-177); the start current and the PWM input
  level NOT READ (E11-35, R-179).
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

8. **Set 28's restatement (F-12).** The six rows whose cited figures set 27's L4-E7 round 5 and L4-E11 section 18 changed are
   restated beside the table (section 4a), not edited in it: the table states what the first round wrote, and the reader reads
   the targets at `1e18a1ca`, so rewriting it would make the record claim a text the targets never carried. This record edits no
   target (`pcb_interfaces.yaml` is the integrator's file, and the three targets are pinned by sha256 in L4-E9, L4-E11 and L4-E5);
   the withdrawn texts still in them are findings L5-F09 and L5-F10. The figures that no longer stand are checked at the record's
   base `2c240414` and the replacing texts are matched in the tree, so a later Layer 4 change refuses again rather than passing
   silently. *Reverse:* delete the RESTATED entries; the reader then refuses as it did on set 28's line.
9. **L5-F09 and L5-F10 closed in the contracts for set 28 (the coordinator's instruction of 3 October 2026: set 28 must not publish
   withdrawn claims in the contracts; this record's author made the author of those six texts).** `apply_l5pwr2_contracts.py` is the
   integrator's script: idempotent (every old text once and no new text: it applies; every old text gone and every new text
   present: already applied, nothing written; anything else refused), each old text a pattern with its figures as placeholders
   matched exactly once, each new text built from L4-E9's 4e row and 8a D-10, R-176 and L4-E11 17a and E11-39 with every figure
   parsed from those files, the YAML re-parsed, the table rows' cell counts kept and L4-E11's dock draft still applying. V-E16's
   rows 2 and 3 are R-176's rows 2 and 3 verbatim from the register. Each restated text is PROVISIONAL with its trigger (B6-ENG-1 and
   B6-ENG-2 for the guard, E11-38 and E11-35 for the dock branch). The texts outside the six (L5-F11) are left to an assignment.
   *Reverse:* revert the commit that applied it; the old texts are the patterns the script asserts.
10. **L5-F11 and set 28's sweep (the coordinator's instruction of 3 October 2026: set 28 carries no withdrawn claim; this record's
   author is now also Layer 5's author of record l5r2).** `apply_l5f11_contracts.py` (it requires `apply_l5pwr2_contracts.py`
   applied first) restates fourteen texts by the same method: IF-AE-DOCK `pin1_vsys_dock`'s domain (D7 and D8 removed by R-177, U22
   feeding the fans), its declared current and contact share, its drop and VSYS_E (all L4-E11 18b; VSYS_MIN's start said not
   restated there), its start rule as 18b states it, record l5r2's round 2 clause re-pointed at the restated rule, the STATE's
   unnamed fans (Layer 7's D-18 cited through R-179); `FAN1_SW_FAN2_SW.start` (E11-39, 18b); IF-EXT-DC `l4_defects` (OPEN per L4-E9
   8a). The sweep of both files for the wordings Layer 4 withdrew in set 27 (the guard's pass from a loop, the hard short as a
   ceiling or bound, R-176's old row 2 and 3 bounds, the old branch current with its drop and VSYS_E, the per-fan start currents, the
   PWM ramp with U12 alone, the B6 case NOT CLOSED, the unnamed fans, the fans on VSYS_E) found four more: FW-E11's verification and
   V-E11 (U22 left out of R-188's acceptance), section 4.1's R-177 row (the fans on VSYS_E) and HF-F05 ("no fan part is picked",
   unanswered); all four restated, HF-F05's words kept as raised with the answer appended, and a change-record row added. Kept, with
   the reason: (a) IF-AE-DOCK `charge_share` (BAT-F06: board E's always-on domain and fans on CELL_F, the VSYS-side feed not taken)
   is the drawn board's statement, which L4-E11's `apply_pcb_interfaces_dock.py` (R-178) replaces when the drafts apply and anchors
   on, so editing it would break that draft; (b) round 2's reference loop "withdrawn as a passing floor" and the hard short "a
   resistive extrapolation, not a bound" are the current Layer 4 wording; (c) "D7 and D8 removed" (FW-E07, the dock field) is the
   draft's content; (d) "renamed from R221" (FW-E11, the round 2 sentence) is a designator's history; (e) the change record's rows
   are history by design. `test_l5pwr` holds the sweep as a property of the two files. *Reverse:* revert the commit that applied it.

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
| L5-F09 | Layer 5's contract owner (the round after l5r2), the integrator | At set 28 (`5515ecc0`) the solar guard's texts this pass wrote still carry L4-E7's round 2 reading, which its round 5 withdrew: `pcb_interfaces.yaml` IF-EXT-DC `protection` (line 1243: every rating with its margin only from round 2's reference loop, with round 2's U5 figures) and `bench` (line 1274: row 3 a pass only from that loop); `HW-FW-CONTRACT.md` V-E16 (line 313: row 2's PV_F bound, row 3's turn-off current and its pass) and section 4.1's R-173 row (line 261). Section 4a quotes each and the texts that replaced them | DONE for set 28 by `apply_l5pwr2_contracts.py` (decision 9; the integrator's script, applied on `fnd/l5pwr2`): the four texts restated to the Layer 4 text with every figure parsed from L4-E9's page, the register and L4-E11's output, PROVISIONAL with B6-ENG-1 and B6-ENG-2; owed: L4-E9's pins of `hwfw` and `ifaces` and L4-E11's of `hwfw` (their outputs change in those pin lines only), and the `interfaces.py` re-take (CONFIG_INPUTS) |
| L5-F10 | the same | At set 28 `pcb_interfaces.yaml` IF-AE-DOCK `pin1_vsys_dock` still calls the hard short's figure "a ceiling" (line 706; L4-E11 17a now: a resistive extrapolation and E11-38's test target, not a bound) and still words the stagger "with a PWM ramp, ... never while U12 starts" (line 714; L4-E11 18c and FW-E11 at `HW-FW-CONTRACT.md` line 187: a PWM-duty ramp into the fan's PWM input, never while U12 or U22 starts); record l5r2's round 2 sentence (line 723) supersedes the start rule's figures only | DONE for set 28 by `apply_l5pwr2_contracts.py` (decision 9; the integrator's script, applied on `fnd/l5pwr2`): both sentences restated to the Layer 4 text with every figure parsed from L4-E9's page, the register and L4-E11's output, PROVISIONAL with E11-38 (and E11-35 for the stagger); owed: L4-E9's pins of `hwfw` and `ifaces` and L4-E11's of `hwfw` (their outputs change in those pin lines only), and the `interfaces.py` re-take (CONFIG_INPUTS) |
| L5-F11 | Layer 5's contract owner, the coordinator | Outside the rows of L5-F09 and L5-F10, `pcb_interfaces.yaml` IF-AE-DOCK `pin1_vsys_dock` still carries set 27's first fan basis: the feed "(U12, C31, the mixer fans, D7 and D8)" and "1.0 A declared (U12 0.8 A, the fans 0.1 A each), ... 28.6 percent" (lines 698 and 699 at `1c4e0ff2`; R-177 removes D7 and D8, L4-E11 18b declares the branch afresh), the drop and VSYS_E at the floor (line 702) and the start rule's currents on VSYS_E (line 716), each superseded in place by record l5r2's round 2 sentence (line 728), and the STATE's "(E11-35, R-179: no fan is named)" (line 722; Layer 7's D-18 names them), which nothing supersedes; `FAN1_SW_FAN2_SW.start` (line 322) opens with the PWM ramp and U12 alone before its own section 18 sentence; IF-EXT-DC `l4_defects` (line 1289) says D-10's guard-on case NOT CLOSED where L4-E9 8a says OPEN | DONE for set 28 by `apply_l5f11_contracts.py` (decision 10), with the sweep's four further rows; owed: the same re-pins as L5-F09 and the `interfaces.py` re-take |
| L5-F13 | Layer 5's contract owner (its next round), the integrator | At set 29 the `service` strings of IF-AE-DOCK `pack_pins` and IF-PE-PACK `power` in `pcb_interfaces.yaml` still carry the pointer L4-E9's round 7 withdrew (the PS-ALLTX PLAN line's stack voltages, read as if they were decision D-11's all-transmit basis). L4-E9's LH-04 now gives that basis on Layer 9's final drafts, and it is not supplied from REQ-018's pass line (D-17 OPEN). Found by the coordinator at set 29's integration, when this record's script refused on the merged tree; row LH-04b is restated in section 4a and the contract text is left as written | restate both `service` strings in place from L4-E9's LH-04 (a registry change: the Layer 4 readers that pin `pcb_interfaces.yaml` re-pin in that set) |

## 10. What this record does not claim

- Nothing is verified on hardware: every V row is owed, every DRAFTED figure is a draft's, every PROVISIONAL entry stands on an
  open row. Software tests establish this record's own behaviour only.
- The criteria table of section 6 is Layer 5's reading; `LAYER-STATUS.md` is the integrator's page.
- The contracts do not close U-01, U-02, U-04 or B6; they carry Layer 4's conditions into the interfaces with their triggers.
- Set 28's restatement (section 4a) edits no target and no Layer 4 record; it reads them. `apply_l5pwr2_contracts.py` edits six
  texts of the two contract files (L5-F09, L5-F10) and nothing else. The contract values are Layer 4's readings carried, not a new
  derivation.

## 11. Reproduce

`python3 v2/docs/records/l5pwr/l5pwr_contracts.py` prints the table (a second at most, stdlib only); `_bin/regen_out.py` is the
only way the committed output is regenerated. `env -C v2/ecad/tools/tests python3 run.py test_l5pwr` holds the predicates.
`apply_l5pwr.py <target> --check` on the tree refuses "already applied"; on the files at `2c240414` (the contract after
`../l4e5/apply_fw_a16.py`) it checks OK and reproduces the tree's files byte for byte (`test_l5pwr.py` does both). It also holds set 28's restatement: every
withdrawn figure is one the row cites, every replacing text is matched once with its figures parsed, no figure is typed in the
restatement's prose or patterns, and the page's section 4a equals the script's.
