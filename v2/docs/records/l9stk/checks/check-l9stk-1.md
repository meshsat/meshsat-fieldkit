accepted: no

# Record l9stk: the independent checker's check 1, COPPER: NOT CONFIRMED (filed as received)

MESHSAT-1357. An AI review by a fresh Claude session that authored none of the record (an independent checker, not a qualified engineering review, not an Astra check), read-only in a disposable scratch clone at `f76564ebe513b4603d677e43a665d2b426a12fbc` (branch `fnd/l9stk`). Time: 4 October 2026, 00:21 to 00:40 CEST. Nothing in the kit has been built, bought or measured.

Scope, from the coordinator's brief: the copper question: section 14 of `L9-STACKUPS.md`, `l9stk_copper.py` and its output, `apply_decisions_l9stk.py` and `apply_energy_chain_l9stk.py`; the decision-critical figures derived blind from the sources first (the currents, the ruled method, the face split, the adiabatic check, the decision and its scope, the drafts).

Filed by the integrator of set 29 from the checker's final message for the round, without edits to its content. The record's author answered it in the next round (`L9-STACKUPS.md` sections 14 and 15 name each revision); this note is the checker's own record of what it read and found.

## The checker's report, as received

**COPPER: NOT CONFIRMED**

I reproduced every figure in f76564eb exactly. The physics behind the 10 K per face is the problem: the record rates each outer face as if it cooled on its own, and the two faces of a band sit on top of each other. Read under your clarified framing, the record is a candidate width calculation, not a verified fault coordination.

**Blocking discrepancies**

- **B1. The two faces heat each other.** Each face is rated alone at its share (12.5 A on 0.429 mm²). The two faces share the same board area and the same two cooling surfaces, so the band behaves like one conductor of the combined section carrying the combined current. Using decision 35's own model on 0.858 mm² at 25 A:
  - 18.9 K at 25 A, not 10.00 K.
  - 12.0 K at the gauge's held 20 A, over the 10 K criterion.
  - 147.1 °C at the blade's 600 s point (50 A), not 110.9 °C.
  - A simple fin model tuned to the ruled fit's own 10 K for one face gives about 22 K for the stacked pair, which agrees.
  - Treated as one conductor, two 1 oz faces need 21.81 mm each at 25 A. That is the record's own one-face 2 oz figure.
  - On board E the forward band and the return run side by side, which adds more heating. The record does not model this anywhere, and dc_drop's per-cell judge would not catch it either.
- **B2. DC_HS rows left off the page.** The output prints S3 (3.15 mm) with Q7 shorted at 242.3 °C for 35 A over 5 s and 494.8 °C for 60 A over 0.5 s, both over 125 °C. Sections 14.6 and 14.9 quote only the passing rows, and 14.10 lists no residual for this case. The S2 family (9.70 mm a face, a field at each end) would hold 104.6 °C at most on the record's own per-face model.
- **B3. The 125 °C limit is not the lowest limit of the parts these bands join.**
  - The XT60 sheet in the tree gives -20 to 120 °C.
  - The 297 sheet gives 105 °C for the tin-plated blade (.WXT), and the fitted part number "0297025" does not pin the silver-plated version.

**Minors**

- The gauge rows pair each threshold with its own delay. The worst corner of each band (24 A for 2 s, 30 A for 1 s, 55.6 A for 20 ms) still reads within 10 K on B1 (9.21, 7.33 and 0.50 K).
- The energy chain cites the ATOF 287 sheet (1000 A²s, 2.52 mΩ) for the pack blades, but the 3568 holder takes MINI 297/997. The record reads the 297 correctly but does not raise this as a finding.
- The barrel annulus is taken as π(d+t)t, plating outside the 0.4 mm hole. That is the via_current tool's convention, not this record's. If the plating grows inward, the counts become 15 thermal and 30 at P_CP.
- Dock pins: the record assumes the four share evenly. The sheet gives 20 mΩ maximum and no minimum, so the split is not bounded.
- The hard-short predicate is stated on the sheet's unlabelled I²t of 625 A²s, which is not a guaranteed clearing figure.
- E11-29's specimen should be measured with the band carrying its current, since the band's own rise adds to Q39/Q40's junction.
- R17's maker sheet is still owed: its 5 W comes from the catalogue and its derating at 70 °C is unknown.
- L4-E12 models 71.25 °C (E3-O) and 76.25 °C (E5's dwell) inside air without the hold; the +70 °C line holds only with the hold, conditional on T-H1.
- `apply_decisions_l9stk.py` writes when `--check` is left off.

**Points 1 to 6**

1. **Currents: CONFIRMED.** 10 A, 18 A for 60 s, the docking pulse (242.9 A peak, 0.9971 A²s), OCD1/OCD2/AOLD/ASCD and the 297's opening times all match their sources.
2. **Ruled method: CONFIRMED.** Blind results: 12.26 mm, 14.60 mm, 19.52 K, 7.30 mm and 12.14 K. 10 K is the chain's own rise and is applied consistently.
3. **Face split: NOT CONFIRMED.**
   - The electrical part is right: the ladder formulas, the counts (30, 31, 28 and the thermal 14) and the even split between through-hole ends (a wider face is never hotter, by AM-GM).
   - The stitching claim is right. In my ladder simulation, stitches every 2 mm raise the part's face from 0.55 to 0.57 at the end.
   - It fails on the thermal side (B1).
4. **Adiabatic check: NOT CONFIRMED.** The arithmetic holds both ways. The 600 s point fails under B1 and B3, and under the clarified framing the series parts are over their ratings there.
5. **Decision and scope: NOT CONFIRMED.**
   - With these widths, 1 oz is not shown to coordinate (B1, B2).
   - W4DP-F2 is rightly left open, but once B1 is included its residual begins at the 600 s interval, not from 50 A up.
   - Findings F2 to F4 are real defects and correctly routed to their owners. They are design corrections, not coupon items.
6. **Drafts: CONFIRMED.**
   - The decisions draft's `--check` passed and wrote nothing.
   - The energy chain draft refuses (exit 3) until the decisions are in the register.
   - The tests prove a second run is a no-op and that it replaces l8r2's draft.
   - `test_l9stk` and `test_energy_chain`: 48 passed, 0 failed. The tree's files were unchanged by sha.

**Coordination table** (+70 °C inside air; copper given as per-face / stacked)

| Row | Basis | Protective device | Guaranteed max clearing | Readings | Limiting | Disposition |
|---|---|---|---|---|---|---|
| 10 A held | pack declared 10.0 A | none (shedding, firmware) | not applicable | copper 71.6 / 73.0 °C; R17 0.5 W; Q39/Q40 junction 88 °C; XT60 10 of 30 A; pins 2.5 A; 3568 no rating | none over; holder unrated | (a), Q39/Q40 conditional on E11-29 and E11-36; holder (b) Layer 6/7 |
| 18 A for 60 s | PWR-F12 | key-down control (firmware); gauge above 20 A | none in hardware for the 60 s | copper 75.1 / 79.7 °C; R17 1.62 W; Q39/Q40 junction 126.7 °C | Q39/Q40 | (a) conditional on E11-29 and E11-36 |
| 25 A held | blades' rating, chain check 3 | gauge (works through P's FETs) or blades | gauge working: 1 s (OCD2); gauge failed: none (110 % holds at least 360,000 s) | copper 80.0 / 88.9 °C; R17 3.125 W; Q39/Q40 3.3 W per FET, about 179 °C; XT60 about 89 °C; pins 6.25 A if even | Q39/Q40 (over 150 °C from 21.4 A, over 175 °C from 24.5 A) | (b) L4-E11; (b) l9stk widths |
| 20 to 33.75 A held | gauge holds 20 A; blades have no maximum time below 135 % | gauge failed: blades | none up to 33.75 A | at 33.75 A: copper 88.4 / 104.8 °C; barrels 15 K; R17 5.70 W; Q39/Q40 about 269 °C; XT60 over 30 A | Q39/Q40, then XT60 (30 A), R17 (31.6 A) | (b) W4DP-F2, or uprate every series part to 33.75 A |
| P's FETs welded, 50 A | blade's 135 to 200 % row | blades (F2 only from 60 A, within 60 s) | 600 s | copper 110.9 / 147.1 °C; barrels 37 K; R17 12.5 W; Q39/Q40 13.2 W per FET; XT60 about 147 °C; pins 12.5 A each | Q39/Q40, R17, XT60, pins | (b) W4DP-F2 |
| P's FETs welded, 87.5 to 480 A | blade's 200, 350 and 600 % rows | blades | 5 s, 0.5 s, 0.1 s (no clearing I²t printed) | copper 197.5, 175.5, 325.5 °C (copper-only bounds) | every element | (b) W4DP-F2 for the parts; (c) copper coupon (below) |
| Shore, Q7 shorted | F1 10 A MINI 997 | F1 | none to 13.5 A; then 600 s, 5 s, 0.5 s, 0.1 s | R19 at 3 W from 17.32 A, 4 W at 20 A; 12.25 W at 35 A (within its 5x for 5 s); DC_HS 242 and 495 °C | R19, DC_HS | (b) L4-E11 D-06 for R19 (F4); (b) l9stk: DC_HS to S2 |

The copper coupon task (c): a B1 band specimen behind a fitted Ag 0297025, starting from 70 °C, run at 87.5 A until the blade opens. It passes if the peak stays at or under 120 °C with no delamination. This is a supplier task, and only worth running after the series parts are corrected.

**W4DP-F2 closure criterion (from the tree).** An element that acts without firmware opens the discharge path at or below the cells' 24 A at 3P. It is closed either by a fixed hardware discharge overcurrent on the shunt, specified at board P's regeneration (O-11), with pack_protection's hardware row reading PASS and TEST-PLAN row 13 run on that element; or by the owner restating BAT-001. The table adds two conditions: the element must interrupt even when board P's FETs are welded, and it must act before Q39/Q40 pass 150 °C (about 21.4 A held). Note that F2 can break only 80 A.

**Smallest next action (the next deliverable).** One revision of l9stk section 14, then a targeted recheck:
1. Rate stacked faces, and the adjacent return, as one conductor and re-derive the widths and the strip's cross-section.
2. Carry DC_HS at the S2 family.
3. Use 120 °C as the limit and pin the Ag-plated 0297025.
4. Add this table with its dispositions.

**Owner decision: not required now.** It becomes his only if the re-derived 1 oz widths cannot be laid and 2 oz has to be paid for, or if W4DP-F2 is closed by restating BAT-001 (a requirement change) or by TI's custom BQ77207 (an outside contact).

The scratch clone is deleted, nothing was committed, and the main tree is clean.
