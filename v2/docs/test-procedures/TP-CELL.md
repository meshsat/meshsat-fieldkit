# TP-CELL: the limited sample qualification of one Saft MP 176065 xtd cell (U-01's Saft route)

<!-- tp
id: TP-CELL
title: The limited sample qualification of one Saft MP 176065 xtd cell (U-01's Saft route)
register: R-168, R-169
e11: none
route5d: The limited sample qualification of one cell (R-168, R-169; L4-E10 15g)
-->

**Status: PROPOSED, for the supplier to review and agree before execution.** MESHSAT-1357, 3 October 2026. Prototype design:
nothing here has been built, bought, powered or measured. Common rules: `v2/docs/test-procedures/README.md`.

## 1. Purpose and the decision it settles

The ruled pack's cell does not cover the kit's hottest and coldest storage rows on its maker's printed limits. A proposed route, a
4S1P pack of Saft MP 176065 xtd prismatic cells, covers every temperature window on Saft's published sheet, but not current and
temperature together, nor the storage dwell and recovery. The record's class for the route:

<!-- q src="v2/docs/records/l4e10/L4E10-CELL-THERMAL.md" -->
> **A SUPPORTED ROUTE EXISTS ON PUBLISHED MANUFACTURER EVIDENCE FOR THE TEMPERATURE WINDOWS:** the Saft MP 176065 xtd as a 4S1P
> pack in D-06's pocket, every cell limit row's window printed by its maker. **NOT YET ADOPTABLE:** current and temperature
> together and the storage dwell and recovery AWAIT Saft or the limited sample qualification (15g), the fit awaits the mock-up,
> and the adoption awaits the owner's approval (D-06's cell and energy, about 82 Wh nominal against about 145 Wh, and the spend).
> With it LO-01d's cells stay inside the temperature window on the conservative bound (the current at that temperature awaiting
> 15g); LO-01a's complete pass and LO-01e rest on T-H1 for every cell. The HL18650V stays the higher-energy alternative (90.2
> against 55.1 Wh usable), resting on its vendor answer or a lot soak. Missing evidence is not shown to be impossible: each
> missing fact has its check above. FEA-008 stays open until the adoption, the fit and T-H1.
<!-- /q -->

This procedure is the limited sample qualification the record defines in its section 15g, in place of Saft's answer on the
current-at-temperature and storage rows. It settles **U-01's Saft route: adoptable or not** (register rows R-168 and R-169), together
with the fit mock-up (R-167) and T-H1, for the tested lot only; the owner's approval of any cell change (OW-3) follows the evidence.
It is not a substitute for the kit-level tests E3-O, E5, E3-S and E4-S with the pack fitted.

## 2. The specimen and what transfers

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="The limited sample qualification of one cell (R-168, R-169; L4-E10 15g)" col="Specimen" -->
> one Saft MP 176065 xtd cell of the lot to be fitted (three if the owner prefers a spread), never fitted afterwards, a
> thermocouple on its surface, soaked to each temperature first
<!-- /q -->

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="The limited sample qualification of one cell (R-168, R-169; L4-E10 15g)" col="What transfers to the final board" -->
> to the pack as evidence for that lot and sample only; Saft's statement closes the rows for every lot
<!-- /q -->

The record's definition, in full (L4-E10 15g):

<!-- q src="v2/docs/records/l4e10/L4E10-CELL-THERMAL.md" -->
> It substitutes for Saft's answer on the current-at-temperature and storage rows only, as evidence for that lot.
>
> - **Sample:** one cell of the lot to be fitted (three if the owner prefers a spread), never fitted afterwards.
>
> - **Before and after every step:** the capacity at +25 C, C/5 to 2.5 V after CC/CV 4.2 V (its own baseline); the 1 kHz
> impedance; the thickness at full charge; the open-circuit voltage after 24 h.
>
> - **Steps** (a thermocouple on the surface, the cell soaked to temperature first):
>
> - D1: 10 A continuous from full charge to the kit's graceful 3.00 V under load, at -20, -10, +45, +60, +70 and +80 C;
>
> - D2: 18 A for 60 s at full charge and at 30 %, at the same temperatures;
>
> - D3: 20 A for 2 s (the gauge's OCD) at -20 C and at +80 C, at 30 %;
>
> - C1: the drawn 3.0 A from 0 C and at +45 C to 4.2 V (0.1C at -10 and -20 C only if charging below 0 C is wanted);
>
> - S1, S2: 24 h at +71 C and 24 h at -33 C, each at 30 %; S3: ten 24 h cycles of Method 507.6 Procedure II at full charge (E5's
> rest).
>
> - **Pass, every step:**
>
> - the surface at or under +85 C;
>
> - the voltage at or over the CUV's 2.50 V under load;
>
> - no venting or leak;
>
> - after the step, the capacity at least 95 % of the cell's own before, the impedance at most 1.20 times its own before, and the
> thickness at most 1.0 mm over its own before.
>
> - These thresholds are SESSION choices: TEST-PLAN's 5 % recovery line, an impedance margin, and the pocket's height allowance
> for wrap.
>
> - **Its limits:** evidence for that lot and that sample only, at the temperatures and currents run; not a production guarantee,
> not Saft's derating, and not a substitute for E3-O, E5, E3-S and E4-S with the pack fitted.
>
> - **Equipment and time:** a chamber from -40 to +85 C, a 25 A load, a CC/CV source and a logger; about two weeks. **The owner's
> items for this route:** approval of the cell change inside D-06's pocket (4S1P prismatic, about 82 Wh nominal; REQ-046 and
> REQ-077's cell-derived numbers with it) and its spend; sending Saft's drafted questions if the bench pulse is not preferred. The
> Topwell request stays for the HL18650V alternative.
<!-- /q -->

**Consequences for this procedure.** The cell comes from the lot to be fitted and is never fitted afterwards. The result covers the
temperatures and currents run, for that lot and that sample; Saft's written statement closes the rows for every lot. Three cells
instead of one give a spread, if the owner prefers it (5d); the procedure is then run on each.

## 3. Safety

This procedure abuses a lithium-ion cell at the edges of its ratings (20 A, +80 C, -33 C, deep discharge). The laboratory's battery
rules take precedence (README section 6). In addition:

- **Containment:** the cell inside a fire-resistant enclosure in a chamber rated for battery testing, with an exhaust for venting gases;
  no person in front of the chamber door during the high-current and hot steps.
- **Automatic abort** (proposal): the load and the source stop when the surface reaches +90 C (5 K over the pass line, so a failing step
  is recorded and the cell not driven on), when the voltage under load falls under 2.50 V (the pass line and the cell's cut-off), when
  the charge voltage exceeds 4.25 V, or on a smoke or gas sensor in the enclosure.
- **Handling:** the cell is never short-circuited, punctured or crushed; the thickness is read with a non-conductive gauge contact or with
  the tabs insulated.
- **After the test:** the cell is quarantined and disposed of as a damaged lithium cell, never fitted (15g).

## 4. Equipment, and the accuracy each measurement needs

The record names the equipment (15g, quoted in section 2: "a chamber from -40 to +85 C, a 25 A load, a CC/CV source and a logger"). What
each pass line asks of it:

| Item | Class | Accuracy and capability needed |
|---|---|---|
| Battery-rated climatic chamber | a temperature chamber from -40 to +85 C with battery-test safety features | each step's temperature held at the cell's surface (the cell soaked first); its uniformity stated |
| Electronic load | a DC electronic load, 25 A | 10 A, 18 A and 20 A held within 1 % (proposal); the step edges recorded |
| CC/CV source | a battery cycler channel or a programmable source | 4.2 V CV within 10 mV (proposal: the cell's charge limit is the line, so the CV setpoint is not exceeded), C/5 and 3.0 A CC |
| Capacity measurement | the cycler's coulomb count or a shunt and a logger | the capacity ratio before to after resolved to 1.25 % (proposal: a quarter of the 5 % the 95 % line allows), on the same channel each time |
| Voltage under load | four-wire at the cell's tabs | within 10 mV (proposal) against the 2.50 V line |
| Surface thermocouple | fine-gauge type T or K, fixed at the cell's largest face centre (proposal) | within 1 K (proposal) against the 85 C line |
| Impedance meter | a 1 kHz AC internal-resistance meter, four-wire | the ratio before to after resolved to 5 % (proposal: a quarter of the 20 % the 1.20 line allows); the same fixture and tab points every time |
| Thickness gauge | a micrometer or a dial gauge with flat anvils | 0.01 mm resolution, at three marked points (proposal), the greatest reported, against the 1.0 mm line |
| Humidity chamber (S3) | a temperature-humidity chamber | only if S3 applies Method 507.6's humidity to the bare cell (section 6, the open question owed there) |
| Logger | a multi-channel logger | voltage, current and temperature at least once a second during discharges and pulses (proposal), and once a minute during soaks |

## 5. Setup and measurement points

1. The cell in its holder with four-wire connections at the tabs (force and sense), the surface thermocouple fixed, the holder not
   clamping the cell's faces (so the thickness change is free and readable).
2. Measurement points: the tab voltage (sense), the current (the load's and the source's readback, checked by a shunt), the surface
   temperature, the chamber air.
3. The cell's identity: lot, date code, serial if marked; Saft's datasheet revision used (Doc. n 31109-2-0625, June 2025, held back from
   this tree; the supplier obtains it from Saft).

## 6. Steps

**Receipt (R-169).** Capacity at +25 C, C/5 to 2.5 V after CC/CV 4.2 V: the lot's capacity at receipt, filed per cell; the energy in Wh
from the same discharge (proposal: the budget is in Wh). C is taken as the sheet's typical 5.6 Ah until Saft states a rated capacity, so
C/5 is 1.12 A and 0.1C is 0.56 A (INFERRED from L4-E10 15e's "the sheet gives a typical 5.6 Ah"). The CC/CV charge's own current and its
termination current are not stated in the records: TBD (owed by R-168): the charge current and the CV termination current of the CC/CV
4.2 V charge before each capacity check (Saft's question on the termination is drafted), with C/5 and C/20 proposed until stated.

**The checks before and after every step** (15g): the capacity at +25 C as above, the 1 kHz impedance, the thickness at full charge, and
the open-circuit voltage after 24 h. One check serves as the "after" of a step and the "before" of the next (proposal).

**The steps** (15g), in this order (proposal: the charge steps, then the discharges from mild to severe, then the storage steps):

1. **C1:** the drawn 3.0 A from 0 C to 4.2 V, and at +45 C to 4.2 V (and 0.1C at -10 and -20 C only if charging below 0 C is wanted;
   the owner's choice, recorded).
2. **D1:** 10 A continuous from full charge to 3.00 V under load at +45, +60, -10, -20, +70 and +80 C (the record's six temperatures;
   this order is the proposal). The cell charged at +25 C, then soaked to the step's temperature until its surface is within 1 K of it
   for 30 minutes (proposal).
3. **D2:** 18 A for 60 s at full charge and at 30 % state of charge, at the same six temperatures. 30 % is set by removing 70 % of the
   cell's latest measured capacity at C/5 from full at +25 C (proposal), then soaking.
4. **D3:** 20 A for 2 s at 30 %, at -20 C and at +80 C.
5. **S1:** 24 h at +71 C at 30 %, unloaded. **S2:** 24 h at -33 C at 30 %, unloaded.
6. **S3:** ten 24 h cycles of MIL-STD-810 Method 507.6 Procedure II at full charge (E5's rest). Whether the bare cell receives the
   method's humidity or only its temperature profile is not stated: TBD (owed by R-168): whether S3 applies Method 507.6's humidity to the
   bare cell or only its temperature profile.

## 7. Data to record

| Step | Temperature (C) | State of charge | Current (A) | Duration | Surface greatest (C) and U | Voltage least under load (V) and U | Venting or leak | Verdict |
|---|---|---|---|---|---|---|---|---|
| D1 | +45 | full | 10 | to 3.00 V | | | | |

| Check after | Capacity (Ah, Wh) and ratio to before | Impedance at 1 kHz (mOhm) and ratio | Thickness at full charge (mm) and increase | OCV after 24 h (V) | Verdict |
|---|---|---|---|---|---|
| receipt | | | | | |
| C1 | | | | | |

## 8. Pass, fail and inconclusive

The register's acceptances, quoted:

<!-- q src="v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md" row="R-168" col="Acceptance" -->
> Saft's statement filed, or the limited sample qualification of L4-E10 10g on one cell of the lot (D1 to D3, C1, S1 to S3; a
> chamber from -40 to +85 C, a 25 A load, about two weeks; NZ$ 238.72 a cell): every step with the surface at or under +85 C, the
> voltage at or over 2.50 V under load, no venting, the capacity at least 95 %, the impedance at most 1.20 times and the thickness
> at most 1.0 mm over the cell's own before; evidence for that lot only
<!-- /q -->

<!-- q src="v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md" row="R-169" col="Acceptance" -->
> Each cell's capacity at C/5 to 2.5 V at +25 C filed; the pack's usable energy recomputed from the lot's least (the budget takes
> 53.5 Wh at an assumed minimum)
<!-- /q -->

With U taken as README section 3 states, for every step:

- **PASS** when the surface's greatest plus U is at or under +85 C; the voltage under load less U is at or over 2.50 V; no venting or leak
  is seen; and, at the check after the step, the capacity ratio less U is at least 95 % of the cell's own before, the impedance ratio plus
  U is at most 1.20, and the thickness increase plus U is at most 1.0 mm over its own before. These thresholds are the session's choices
  (15g, quoted in section 2), not Saft's limits.
- **FAIL** on any line of any step, on a valid run.
- **R-169:** the capacity at receipt is RECORDED per cell and the pack's usable energy is recomputed from the lot's least by the
  coordinator (the budget takes 53.5 Wh at an assumed minimum).
- **INCONCLUSIVE:** the cell not soaked to the step's temperature; the current not held within its setting; an abort for a reason other
  than the cell (an instrument fault); the impedance fixture or tab points changed between before and after.

## 9. The uncertainty budget

| Term | Source | Value |
|---|---|---|
| Surface temperature | the thermocouple and its fixing | 1 K (proposal) |
| Voltage under load | four-wire at the tabs | 10 mV (proposal) |
| Capacity ratio | the same channel's repeatability, the temperature of the +25 C check | 1.25 % (proposal) |
| Impedance ratio | the meter's repeatability and the fixture | 5 % (proposal) |
| Thickness | the gauge and the marked points | 0.02 mm (proposal) |
| Step currents | the load's setting checked by a shunt | 1 % (proposal) |
| Chamber | its uniformity at the cell | stated |

## 10. Consequence of a fail, and the re-test triggers

- **A fail** leaves the Saft route not adoptable on this evidence; U-01 stays open, and the route rests on Saft's statement (the drafted
  request, OW-9) or a changed proposal. The ruled pack and its rows are untouched (no requirement changes here).
- **A pass** makes the route adoptable on the lot's evidence together with the fit mock-up (R-167) and T-H1; adoption remains the owner's
  approval (OW-3).
- **Re-test triggers** (proposal, after 15g's "Its limits"): another lot; a current, temperature, state of charge or duration outside those
  run; a change of the kit's current profile (10 A continuous, 18 A for 60 s, the gauge's 20 A for 2 s) or of the storage rows.

## 11. Authorisation and purchases (nothing has been bought)

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="The limited sample qualification of one cell (R-168, R-169; L4-E10 15g)" col="Authorisation" -->
> the owner's: the cell(s) and the laboratory; Saft's request
<!-- /q -->

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="The limited sample qualification of one cell (R-168, R-169; L4-E10 15g)" col="What to buy" -->
> MP 176065 xtd, one cell for the limited sample qualification (three if the owner prefers a spread), Saft: 1 at 238.72 NZD each
> (SIMPOWER's listing archived 16 January 2025, a price indicator and not a quote;
> v2/docs/records/l4e10/inputs/prices-2026-10-02.json); price not read: a chamber from -40 to +85 C, a 25 A load, a CC/CV source
> and a logger (a laboratory's service)
<!-- /q -->

What to send (5d): `v2/docs/records/l4e10/clarification/saft-mp176065xtd.txt` (OW-9; the owner sends it; Saft's statement closes the
rows for every lot).
