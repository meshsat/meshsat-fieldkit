# The independent verification of the findings ledger's concrete remaining risks (MESHSAT-1357, 2 October 2026)

Prototype design, desk records: nothing is bought, built, powered or measured. This page changes no engineering record. It
settles items of `FINDINGS-LEDGER.md`, section "Concrete remaining risks", by reading the cited sources and recomputing in
separate code (`verify_risks.py` beside this page, stdlib and pdftotext; it imports and reruns no record's script; every
figure below is printed in `verify_risks.out`). The verifier authored none of the records it checks. Where a record's figure
is wrong it is reported here, not fixed. On the candidate `aa897e38` (branch `fnd/l4close`, ledger at `e1e99c4f`).

**PAUSED CHECKPOINT.** The coordinator stopped this work on 2 October 2026 to reassign the slot. Items 2, 4 and 5 are
settled. Item 3 has an interim reading of one input only, which is not the item's result. Items 6, 7, 9 and 11 are NOT YET
VERIFIED (paused). Nothing is stated as a result for a paused item.

| Item | Ledger rows | Verdict |
|---|---|---|
| 2 | L4-E10:1.2, L4-E10:2.1 | CONFIRMED |
| 3 | L4-E10:1.3, L4-E10:2.3 | NOT YET VERIFIED (paused) |
| 4 | L4-E11:1.5, L4-E11:2.5 | CONFIRMED |
| 5 | L4-E12:1.3, L4-E12:2.2 | CONFIRMED |
| 6 | L4-E7R:2.5 | NOT YET VERIFIED (paused) |
| 7 | L4-E9:1.1, L4-E9:2.1, L4-E11:2.2 | NOT YET VERIFIED (paused) |
| 9 | L4-E8:2.2 | NOT YET VERIFIED (paused) |
| 11 | L4-E12:2.1 | NOT YET VERIFIED (paused) |

## Item 2

**Verdict:** CONFIRMED

**What was read.** `v2/docs/TEST-PLAN.md` (pinned by L4-E10 at sha256 `42a3dff3`): E3-L (line 145), E3-H (line 146), E3-P
(line 149), E4-T (line 152), E4-P (line 153) and P15 (line 173); the screen rows C01, C04, C05 and C16 to C18 of
`v2/docs/records/l4e10/l4e10_cell_thermal.out` (lines 74 to 236) and their summary in `L4E10-CELL-THERMAL.md` (lines 75 to
89); the recheck `checks/astra-check-l4e10-2.md`, blocker R2 and its closure criterion.

**What was computed and how.** `verify_risks.py` item 2: each item the recheck lists, located verbatim in TEST-PLAN.md and
verbatim in the screen row that maps it (17 pairs).

**Against the record.** 17 of 17 mapped and read at the source:
- C05: E3-H's +40 C lid-closed level held until the hot stop acts or its 4 h pass; the repeat with the sensor controller in
  reset; the TMP117 fallback at +55.0 C (shed) and +56.0 C (shutdown), released at +45.0 C (P15's wording); the restart once
  the hottest cell reads +46.5 C or less and 30 minutes have passed; the stepped run from +40 C by 2 K an hour to at most +55 C,
  on shore then on the pack;
- C04: E3-L started once with the lid already closed, entering the reduced mode once the lid is read; E3-L's +40 C level is
  C01's (the recheck's list does not name it);
- C17: OTD stops the discharge before a cell exceeds +60 C and recovers at or below +52.5 C, no immediate refusal claimed
  (the recheck's minor R2 as well);
- C16 and C18: full function after the return to 25 C, capacity within 5 % (PROVISIONAL, as TEST-PLAN marks it);
- the charge states TEST-PLAN leaves unstated named as missing inputs (E3-L, E3-H, E4-T transport, E4-P); E3-P's full charge
  is TEST-PLAN's own.

**Observation, not on the recheck's list (no state change).** E3-P's other pass items, "the second level does not fire" and
"capacity recovery at least 95 % as E3-T", are not restated in C17, which cites MAKER 7.10 (the 95 % recovery row) as its
limit. They are pass items of the test, not thermal gaps; the screen's result (NO GAP) does not depend on them, and TEST-PLAN
carries them.

**Ledger.** L4-E10:2.1 becomes CLOSED; L4-E10:1.2, which points to it, CLOSED with it.

Printed figures: `17 of 17`

## Item 3

**Verdict:** NOT YET VERIFIED (paused)

The latent-storage volumes (0.162 L for E3-O and 1.489 L for E5 at the conditioned corner; 0.275 to 1.175 L for E3-S) have
not been recomputed: the separate two-node enthalpy model was not reached before the stop. Nothing below is the item's
result.

**Interim reading of one input (for the resumed work; not a result).** The pocket's room beyond the 1.0 mm minimums, read
from POWER-THERMAL.md (the block 56.65 x 133.5 x 38.1 mm), SHORTLIST.md and CASE-MARGINS.md section 3.2:
- at the worst stack 0.0559 L, as the record (0.056 L);
- "as designed" the record states 0.121 L. On CASE-MARGINS' "Chosen: nominal" column throughout (C1 on the C6 legs: M4b
  +9.68, M5 +3.65, M6 +4.42 mm) the same formula gives 0.0865 L. The record's 0.1215 L takes M5 at +11.74 mm, the
  superseded "As designed" figure on the flat floor: M5's margin text carries escaped pipes (`\|Y\|`), so the split in
  `l4e10_cell_thermal.py` (rows_cm) that skips three cells lands one cell early for M5 only, while M4b and M6 are read from
  the chosen columns. If the volumes are confirmed when the item resumes, this lowers the room's upper end by 0.035 L: no
  rejection weakens, and E5's best-corner "marginal fit" (0.102 L) would no longer fit. To be judged with the item.

## Item 4

**Verdict:** CONFIRMED

**What was read.** TI SLUSE66A (BQ25731, revised January 2021), p.10, section 8.5: the table's condition "TJ = -40°C to
+125°C, and TJ = 25°C for typical values (unless otherwise noted)"; the row ICHRG_REG_ACC "Charge current regulation accuracy,
5-mΩ RSR sensing resistor, VBAT above VSYS_MIN (0°C to 85°C)", at REG0x03/02() = 0x0200H (1024 mA) -18 % / +21.5 %; the row
ICLAMP, CELL (2 S or more) with VSRN under VSYS_MIN, 384 mA in the TYP column with no limit. Board A's R17 in
`gen_sch_a.py`: "5mOhm 1% 2512 (RSR, charge current sense)". L4E11-SOURCE-ONLY-AND-ENTRY.md section 4 (rule R-b, its three
cases and Q2's line) and `l4e9/DOWNSTREAM-REGISTER.md` row R-136.

**What was computed and how.** Case (i): 1.024 A x (1 + 0.215) / 0.99 and 1.024 A x (1 - 0.18) / 1.01; Q2's diode at VSD 1 V
and 50 C/W over the 62.1 C air; R-b's charge power at 16.884 V.

**Against the record.** 0.8314 to 1.2567 A (record 0.8314 to 1.2567 A); Q2 1.2567 W, 62.836 K, TJ 124.936 C (record 124.9 C)
against 150 C; 21.22 W (record 21.22 W). R-b's bound is stated only inside TI's row condition. Outside it the record keeps
case (ii) (the charger outside 0 to 85 C, its own rise counted, which reads the row's range as the junction's, as the table's
TJ convention does) and case (iii) (under VSYS_MIN, the clamp typical only) INCONCLUSIVE on E11-22, and Q2's 124.9 C
CONDITIONAL on case (i) and on board P's copper. R-136 carries both cases, the clamp's maximum, Q2's copper and the acceptance
"Q2's diode at most 124.9 C at the 62.1 C air confirmed or re-derived". So R-b's bound does not hold outside 0 to 85 C, and
that gap is carried.

**Observation (no state change).** TI's accuracy is the IC's with an exact 5 mOhm RSR; the record adds R17's 1 % and not its
temperature coefficient, and R17 is drawn as a generic part. At 75 ppm/K over the 60 K from 25 C to 85 C the bound becomes
1.2624 A (Q2 125.22 C); at 200 ppm/K 1.2720 A (125.70 C). Both are far under 150 C; R-136's re-derivation should carry R17's
part and its coefficient.

**Ledger.** L4-E11:2.5 becomes CLOSED AS CONDITIONAL (dependency R-136); L4-E11:1.5 with it.

Printed figures: `0.8314 to 1.2567 A`, `124.936 C`, `21.22 W`, `1.2624 A, Q2 at 125.22 C`, `1.2720 A, Q2 at 125.70 C`

## Item 5

**Verdict:** CONFIRMED

**What was read.** TI SNOSD82D (TMP117, revised September 2022): p.1, "±0.15 °C (maximum) from -40 °C to 70 °C" (the sheet prints the minus as a dash); p.6,
section 6.5 Electrical Characteristics, the TMP117 row -40 to 70 C, MIN -0.15, TYP ±0.05, MAX 0.15 °C over free-air
temperature, under the conditions 8 averages, 1-Hz conversion cycle, thermal pad unsoldered (DRV package) and I2C inputs at
VIL ≤ 0.05 V+ and VIH ≥ 0.95 V+ (the factory default configuration is the 1 s cycle with eight averages, section 7.3's averaging paragraph); the
TMP117N grade prints ±0.2 °C from -40 to 100 C and no ±0.15 °C row. Board B's part is TMP117AIDRVR (`gen_sch_b.py`).
L4E12-ELECTRONICS-THERMAL.md section 5d and `l4e12_thermal.out` lines 648 to 655; register rows R-138, R-139 and R-146.

**What was computed and how.** The lag 15.0 K/h x (1 s + 60 s); the thresholds 55 - 0.15 - 0.5 - lag and 50 - 0.15 - 0.5 -
lag; the SGP41's largest temperature at each set point; the break-even time constant of the 54.0 C setting at ±0.15 C and at
the N grade's ±0.2 C.

**Against the record.** Lag 0.254167 K (record 0.254167 K); off point 54.095833 C, set at 54.0 C, the SGP41 at most 54.904167 C
(record the same); on and used at 49.095833 C, set at 49.0 C, at most 49.904167 C (record the same). The ±0.15 °C is a
printed maximum on the base grade under the conditions above. The 54.0 C setting holds while the sensor-to-SGP41 time
constant is at most 83.0 s at 15 K/h (the record assumes 60 s); with the N grade's ±0.2 °C at most 71.0 s.

**What stays open.** The 0.5 K gradient is an ASSUMPTION carried by R-146 (its placement review). The 61 s reading and
response (the 60 s time constant) is an ASSUMPTION that no register row carries: R-138 and R-139 force a shutdown at room
temperature, which does not test the lag. The ledger's state definitions admit CLOSED AS CONDITIONAL only with a carrier for
each dependency, and this verification edits no register, so the row stays STILL OPEN on that one missing carrier: a register
row (R-146's or R-139's acceptance) measuring the time constant at most 83 s, or the setting re-derived from a measured one.

**Ledger.** L4-E12:2.2 stays STILL OPEN, narrowed to the lag's carrier; L4-E12:1.3 with it.

Printed figures: `0.254167 K`, `54.095833 C`, `54.904167 C`, `49.095833 C`, `49.904167 C`, `83.0 s`, `71.0 s`

## Item 6

**Verdict:** NOT YET VERIFIED (paused)

The loaded entry network (U5's 0.2094 V against 0.3 V at the capability scenario's cold end, and the 15 kV discharge) has not
been recomputed. For the resumed work: the drafted topology read from `apply_gen_sch_e_input_limit.py` and
`apply_gen_sch_e_backstop.py` is J_SOLAR, F2, PV_P with the three 33 uF 50 V bulk cans; the sense bank R60 to R64 (five 70 mOhm,
14 mOhm) to TRK_VS, which carries D4, C71 to C74 and C66; R59 (15 mOhm) to TRK_VIN with C13 to C15 and C64; the SMCJ28A row
(Littelfuse p.2: VBR 31.10 to 34.40 V, VC 45.4 V at IPP 33.1 A) and the ZA row (EEHZA1H330XP) were located.

## Item 7

**Verdict:** NOT YET VERIFIED (paused)

The 1.21 Ohm point, the hard-short start and the 0.49 ms delay maximum have not been recomputed. For the resumed work: Figure
4-10 of SLPS540C (CSD19536KTT, p.6) can be read from the page's vector drawing with `mutool draw -F trace` (the plot frame
spans 0.1 to 1000 V and A; the four lines by their legend colours), and Equation 7 and the loaded tOC row are on SLUSEE5E
pp.23 and 10.

## Item 9

**Verdict:** NOT YET VERIFIED (paused)

The VBUS20 loop with Cc2 at 3.3 nF has not been recomputed in a separate loop model. The compensation design equations are
SNVSAI1D pp.26 to 28 (Equations 38 to 46).

## Item 11

**Verdict:** NOT YET VERIFIED (paused)

The rating-category headings have not been read. The record's heading-checked set is the 22 statements of
`l4e12_thermal.out` 0f; less the SGP41's four (read by check 3), 18 statements on 13 parts remain.

## Reproduce

`python3 v2/docs/records/l4close/verify_risks.py > v2/docs/records/l4close/verify_risks.out` (stdlib and pdftotext, read-only,
a few seconds; the held sheets of `v2/vendor/**/held/` are not needed for items 2, 4 and 5). It exits 1 if a source line is not
where it reads it.
