# ARRAY: Option A(i)'s array wiring, the stage's input window and the entry ratings (stream a1solar, MESHSAT-1357)

**Second issue of the charger rows (stream s119, S-119, 29 September 2026).** The energy chain now carries board A's charger U3 at 0.979 (bracket 0.972 to 0.983; was 0.98, read from SLUSE66A Figure 8-4), with the FETs of decision 57, and Option A(i)'s lid charger U3B at 0.972 (bracket 0.963 to 0.978; was 0.975, read from Figure 8-3) on U3's 400 kHz row, which a session decision draws for it (the FET pair of decision 57, XAL1010-472ME, R16B 10 mOhm, IIN_HOST 6.2 A; `records/s119/apply_decision_s119.py`), weighted by energy over the model's own hours. Both are TI's loss equations (SLUSE66A Equations 6 to 22, printed pages 86 to 88) with the sense resistors inside each figure and the inductors' core loss excluded, so each is high by it (`records/s117/efficiency.out` section 7, `records/s119/u3b_hourly.out`). The chain's scripts were re-issued with their pins moved and every output regenerated (`records/s119/README.md`, `records/s119/headline_diff.out`). Where this page quotes a figure listed here, the page's figure is the first issue's and is superseded by the one given here. Model results on the September reference day; nothing is measured. **In this page (`energy_runs.out`, third issue):** section 9's 4S18P at 40 degrees facing south MEETS with 90.6 Wh at +20 C and 26.4 Wh at +15 C in the typical case (was 90.6 and 26.5) and 87.8 and 23.6 Wh in the adverse case (was 87.8 and 23.7), down to +12.9 and +13.2 C as before; a1elec's two-pack case (4S12P lid) MEETS with 30.7 Wh in the typical case and 27.9 Wh in the adverse case, both unchanged (lid 0.5 and 0.0 Wh, down to +9.6 and +10.8 C). **The planes (section 6, the 4S12P lid):** at 20 degrees the planes facing south and 15 degrees west meet in both cases and the one 15 degrees east now meets in the typical case only (was all three); at 30, 40 and 50 degrees the planes 15 degrees either side of south still meet in both, so the rule of section 7 (20 to 50 degrees within 15 degrees of south) no longer holds for the 4S12P lid at 20 degrees 15 degrees east. For the two lid options the owner chooses between, 4S14P and 4S15P, every grid plane of the rule meets in both cases with U3 at its 6.1 A minimum and U3B hour by hour (`records/s119/reconcile_s119.out` section 7); laid flat the 4S14P lid does not meet and the 4S15P lid meets in the typical case only.

29 September 2026, **second issue** after the independent AI check of `9f93a9fc`
(`checks/check-1.md`: B1 the deployment rule, B2 the adverse ratio, minors 1 to 10). Prototype design:
nothing bought, built or measured; AI review, not a qualified review. The panel is SELECTION.md's design basis, the
Renogy RNG-100DB-H (`v2/vendor/solar/renogy-rng-100db-h-flexible-100w-datasheet-2018.pdf` p.2: 100 W, VMPP 18.9 V,
IMPP 5.29 A, Voc 22.5 V, Isc 5.75 A, Voc -0.31 %/K, Isc +0.05 %/K, Pmax -0.42 %/K, NOCT 45 C, -40 to +85 C, series fuse
15 A, system voltage 600 V). Figures are printed by `array_calc.py` into `array_calc.out` and by `energy_runs.py` into
`energy_runs.out` (section named). Every energy result is a reference-day result **on this model** (the September
PVGIS mean day at Leiden), not a field-weather claim. **Section 6 is a DRAFT for board E's writer and is GATED: it is not
applied to `gen_sch_e.py` before the owner restates REQ-016 (section 5), because it contradicts REQ-016's acceptance as
written (PV_IN and PV_P declared at 25 V and 17.6 V).**

Conditions used throughout: cold open-circuit voltage at -20 C cells, the envelope's in-use minimum
(`pcb_envelope.yaml`), read as REQ-016's "coldest operating temperature" (the -40 C reading is in section 5); hot
short-circuit current at 1000 W/m2 and +70 C cells; the edge-of-cloud factor 1.25 from the only held source of one,
SunPower's installation clause (Safety and Installation Instructions 524958 Rev F, 3.0: Isc and Voc "multiplied by a
factor of 1.25 when determining component voltage ratings, conductor capacities, fuse sizes"; the document is held back
from the tree by its terms and fetched by `fetch_held_back.py`); fuse and connector at 1.25 times that current (the
brief's rule; no held standard says otherwise, and the same clause names NEC 690-8's additional 1.25, NEC not held). The
voltage rating basis is the larger of the cold Voc and the clause's 1.25 x Voc at STC.

## 1. The three wirings of four panels (400 Wp) (`array_calc.out` 2, 4, 5, 13)

| | **2S2P (recommended)** | 1S4P (all parallel) | 4S1P (one string) |
|---|---|---|---|
| Voc at STC | 45.0 V | 22.5 V | 90.0 V |
| **cold Voc, -20 C cells** | **51.28 V** | 25.64 V | 102.55 V |
| cold Voc, -40 C cells (the panel's own limit) | 54.07 V | 27.03 V | 108.1 V |
| 1.25 x Voc (the clause) | 56.25 V | 28.12 V | 112.50 V |
| **voltage rating basis** | **56.25 V** | 28.12 V | 112.50 V |
| hot Isc (1000 W/m2, +70 C) | 11.76 A | 23.52 A | 5.88 A |
| **with the edge-of-cloud factor** | **14.70 A** | 29.40 A | 7.35 A |
| fuse and connector rating (x 1.25) | 18.37 A, **20 A chosen** (section 4) | 36.75 A | 9.19 A |
| back-feed into one faulted string from the others, (Np - 1) x 7.35 A | 7.35 A, under the panel's 15 A series fuse rating: no string fuse | 22.05 A, over 15 A: a fuse per panel | none (one string) |
| VMPP, 1000 W/m2 at -20 / +25 / +70 C | 44.1 / 37.5 / 31.0 V | 22.1 / 18.7 / 15.5 V | 88.2 / 74.9 / 62.0 V |
| VMPP, 200 W/m2 at +25 / +70 C; 100 W/m2 at +10 C | 33.2 / 26.2; 33.8 V | 16.6 / 13.1; 16.9 V | 66.4 / 52.5; 67.6 V |
| stage input current at 200 W at the fixed point | 5.83 A at 34.29 V (6.05 A at 33.05 V) | 11.37 A at 17.59 V | |
| stage input current at 200 W at the hot VMPP | 6.45 A at 31.0 V | 12.89 A at 15.5 V | |
| inside the LT8705A's 80 V (8705af pp.2, 3) | yes | yes | **no: excluded** |
| inside the coordinator's 60 V ceiling | yes (56.25 V) | yes | no |
| fixed-point ratio, September day, 5 m lead (`energy_runs.out` 1) | 0.9903 at 34.29 V | 0.9517 at board E's 17.59 V; 0.9743 at its best, 16.68 V | |

**The model and its bracket.** The VMPP rows and every ratio come from a single-diode model fitted to the maker's STC
points (`array_calc.out` 3). For the Renogy the exact fit gives a negative series resistance, so section 3's fit uses
Rs = 0 through the maker's (VMPP, IMPP) point (its maximum at 18.72 V instead of 18.9 V, ideality 1.54 a cell). The
check asked for an Rs > 0 bracket: two further fits through the maker's points with Rs 0.1 and 0.2 ohm (ideality 1.31 and
1.09 a cell) give, at the drafted 34.29 V, **0.9866 to 0.9923 across the three fits**, and 0.9662 at the worst corner of
the set-point window (`array_calc.out` 11, 12). The first issue's "the ratio errs low" is withdrawn: it is not shown
for the drafted point. The adverse case (section 7) takes the worst fit.

**Why the fuse is not what limits the array's own fault current.** A panel is a current source: the array cannot drive
more than its short-circuit current, 14.70 A at the edge-of-cloud condition, into a fault inside the kit, and a 20 A
fuse never opens on it. F2 protects the entry against current from the kit's side (a failed stage switch with the bus
and the pack behind it); back-feed between the two strings stays under each panel's own 15 A rating (the row above).
The conductors between the array and the stage must therefore carry the array's current continuously, and each is
rated at or above the fuse that protects it (section 4).

## 2. The recommended wiring: 2S2P

Two panels in series make a string of about 37.5 V at maximum power; two strings in parallel join outside the case at
a branch pair of the panels' connector class (Renogy's "Solar Connectors", 30 A, 1000 V, IP67) and come to the case on
one lead. It is recommended because it halves every current of the all-parallel wiring (20 A against 40 A class at the
entry, 5.8 A against 11.4 A in operation, a quarter of the lead's loss), needs no fuse per string, stays inside 60 V by
the maker's clause, and lets a fixed input voltage keep 0.990 of the tracked energy **on this model**. Its costs: the
panel entry's parts move from the 25 to 35 V class to the 60 to 100 V class (section 6), F2 can no longer be a 32 V
automotive blade, and REQ-016's voltage moves to about 52 V (section 5), which is the owner's.

The all-parallel wiring stays a standing option (SELECTION.md 4): with the SunPower, the one fully specified crystalline
panel whose cold Voc keeps REQ-016's 25 V at -20 C (24.05 V; at -40 C it is 25.23 V, section 5); it needs a fuse per
panel (24.1 A of back-feed against its 15 A rating), a 40.1 A entry and a stage input of about 14 A at the hot VMPP, and
its maker warns against parallel wiring "without proper system and safety protection" (524958 Rev F 4.0).

## 3. The stage's input window and set point (2S2P)

- **Set point:** the LT8705A's FBIN loop holds the input at VFBIN x (1 + R8 / R9), VFBIN 1.184 / 1.205 / 1.226 V over
  temperature (8705af p.4). Drafted **R8 232k, R9 8.45k (E96, 1 percent): 34.29 V typical; 33.69 to 34.89 V over
  FBIN's range alone and 33.05 to 35.57 V with R8 and R9 at their 1 percent** (`array_calc.out` 12; the first issue's
  205k over 7.50k gave 34.14 V, 32.91 to 35.41 V with the resistors, which the first issue did not state). The pair was
  chosen among six E96 pairs as an equal best worst case across the three fits and the window (0.9662, with 187k /
  6.81k at 0.9663 and 205k / 7.50k at 0.9633); the fits' common optimum, about 34.6 V, falls between the E96 steps.
- **What the fixed point keeps on this model:** 0.9903 of the tracked energy at the typical point with a 5 m lead
  (0.9966 without the lead). June and December keep about 0.988 at the September optimum (`array_calc.out` 7).
- **Window:** operating 26 to 44 V at maximum power over the envelope (section 1), the set point held whenever the stage
  asks more than the array gives; open circuit up to 51.3 V at -20 C cells and 54.1 V at -40 C, rated to 56.3 V by the
  clause. Inside the LT8705A's 5.5 to 80 V operating range and its 81 V SW1 rating.
- **Current at 200 W into the stage:** 5.83 A at 34.29 V, 6.05 A at the window's 33.05 V minimum; 6.45 A if the point
  sat at the hot VMPP.
- **The 200 W is not a limit the board implements.** Board E senses no input or output current: U5's pins 29 to 34 are
  tied to TRK_OUT and PV_P (`gen_sch_e.py:484`), which the check reads as CSNOUT and CSPOUT on TRK_OUT and CSNIN and
  CSPIN on PV_P with no resistor between them. So the stage takes what its load asks up to its inductor current limit,
  and the array gives up to 330 W at 1000 W/m2 and +70 C (`array_calc.out` 5). The energy model's 200 W window is the
  model's clip, as section 4 of the energy record already says of the 100 W one. Section 6 lists it for the writer.
- **A tracking loop is not needed on this model:** the best fixed point is within 1 percent of a tracker; a loop (a
  controller moving FBIN) buys less than the lead's own loss.

## 4. The entry's fuse and connector ratings (2S2P)

| element | as generated | needed for 2S2P | source of the need |
|---|---|---|---|
| F2 current | 10 A mini blade | **20 A** (the standard value at or above 18.37 A) | 1.25 x 14.70 A |
| F2 voltage | Littelfuse MINI 297 class: **32 V DC** (`v2/vendor/keystone/littelfuse-297-ficcorp.pdf`, "Voltage Rating: 32 VDC") | **at least 56.3 V DC** | the voltage basis; a 32 V blade cannot be used on this array |
| F2 interrupting rating | MINI 297: 1000 A at 32 V DC (same sheet); no rating at 56 V | **at its DC voltage (56.3 V or more), at or above the prospective fault current from the kit's side** (the pack through a failed stage; the writer takes that figure from the pack's own protection record) | SunPower 524958 Rev F p.2 footnote: "The series fuse must have an interrupting rating that is equal to or greater than the maximum fault current that the fuse is required to interrupt, including contributions from all connected sources of energy" |
| F2 holder | Keystone 3568, for MINI 297 or 997 class blades (`v2/vendor/keystone/M65p42.pdf`; its own current rating not read here) | the chosen fuse's format, **rated 20 A or more** | |
| J_SOLAR | JST-VH, 10 A | **20 A or more**, 56.3 V | at or above the fuse |
| the wall's solar pair | "D38999 receptacle, spare pair", 18 AWG, 500 mm, VH crimp (`ASSEMBLY.md` table, Solar row); contact size not settled (size 16 at 13 A or size 20 at 7.5 A, `respin-research-mech-2026-09-04.md`) | **20 A or more a pole** (two size 16 contacts a pole, or one size 12) and a conductor rated for it | at or above the fuse |
| the lead from the array | not specified | **20 A or more**; 4 mm2 class as the panels' own 12 AWG leads; 5 m costs about 0.6 percent of the day on this model (`energy_runs.out` 1) | at or above the fuse |
| string fuses | none | **none** (back-feed 7.35 A under the 15 A series fuse rating) | Renogy p.2 |

For 1S4P the same rows read 40 A (the standard value at or above 36.75 A) for F2, J_SOLAR, the wall pair and the lead,
at 28.1 V (a 32 V blade then fits, its 1000 A interrupting rating against the kit-side fault current still to be
shown), plus four string fuses of 10 to 15 A (9.2 A at 1.25 x 1.25 x Isc a panel, under the 15 A series rating).

## 5. What REQ-016 would have to become (the owner's; not changed here)

REQ-016 today: an open-circuit voltage of at most 25 V at the panel's coldest operating temperature, the panel held at
17.6 V, at most 100 W into the stage; F2 and J_SOLAR 10 A. **This record reads "coldest" as the envelope's -20 C cells**
(`pcb_envelope.yaml` in_use minimum); the panels' own lower operating limit is -40 C, and every candidate's figure at
that limit is printed beside it (`array_calc.out` 13). Under Option A(i) the 100 W becomes 200 W in every arrangement
(the owner's instruction). Beyond that:

- **2S2P (recommended):** "at most 200 W into the stage; the array's open-circuit voltage at most 51.3 V at -20 C cells
  (54.1 V at -40 C), every part on the panel entry rated above 56.3 V; the array held at 34.3 V (33.0 to 35.6 V) by the
  stage's input regulation; F2 20 A and at least 56.3 V DC with an interrupting rating above the kit-side fault current;
  J_SOLAR, the wall pair and the lead at least 20 A." The acceptance's bench line becomes a supply set to the 2S2P curve
  (VMPP about 37.5 V, Voc 45 V at 25 C) at 200 W, and a measure of the power the stage actually takes (section 3: the
  board sets no 200 W limit).
- **1S4P:** "at most 200 W; open-circuit voltage at most 25.6 V at -20 C cells (27.0 V at -40 C; 28.1 V by the clause);
  the array held at 16.7 to 17.6 V; the entry rated at least 40 A; a fuse of 10 to 15 A per panel." **REQ-016's 25 V is
  exceeded by the chosen panel even alone** (25.64 V at -20 C), and by the Victron reference (25.81 V). Read at -20 C it
  admits the SunPower (24.05 V) and PowerFilm's 15 V model (24.86 V) only; **read at -40 C it admits none of the
  candidates** (SunPower 25.23 V, PowerFilm 26.17 V).
- **4S1P:** no restatement admits it; the LT8705A's 80 V rules it out.
- A panel held at 17.6 V at 200 W draws 11.4 A, so REQ-016's own F2 and J_SOLAR 10 A fail at 200 W in the all-parallel
  arrangement even before its fault current is counted.

## 6. DRAFT for board E's writer (GATED: not applied before the owner restates REQ-016)

What the 2S2P array asks of `gen_sch_e.py`'s tracker stage. Listed with the generator's line and the need; the writer
checks each against the maker's document. Applying any of it before REQ-016 is restated would put the generator in
conflict with REQ-016's acceptance (PV_IN and PV_P declared at 25 V, the FBIN divider at 17.6 V).

| part (gen_sch_e.py) | as generated | need at 56.3 V and the stage's real current |
|---|---|---|
| R8, R9 (575) | 102k, 7.50k: 17.6 V | **232k, 8.45k, 1 percent: 34.29 V** (33.05 to 35.57 V with FBIN's range and the resistors) |
| Q3 M1 buck top, Q4 M2 buck bottom (495, 496) | BSC028N06NS, BSC039N06NS, 60 V | both see the full input: 56.3 V is 94 percent of 60 V; an 80 or 100 V part |
| C11, C12 (479) | 100 uF 35 V hybrid polymer | 35 V is under 51.3 V: a 63 V class or higher bulk part |
| C13, C14, C15, C64 (480, 567) | 10 uF 50 V, 10 uF 50 V, 4.7 uF 50 V, 100 nF 50 V | 50 V is under 56.3 V: a 100 V class part |
| D4 (478) | SMCJ28A, 28 V standoff | standoff above 56.3 V (a 58 V standoff class); its clamp at the surge current the writer takes must stay under the LT8705A's 80 V VIN rating, which no SMC part of that standoff does at its full rated pulse: the surge basis is the writer's to state |
| D5 (552), the BOOST1 diode | BAT54, 30 V | it blocks about the input voltage when SW1 is high: a diode rated above 56.3 V |
| F2, J_SOLAR (436, 437) | 10 A blade, VH 10 A | section 4 (20 A, 56.3 V DC, interrupting rating) |
| PV_IN, PV_P intent (463) | 17.6 V, 5.68 / 6.25 A, v_max 25 V | 34.29 V, 6.05 A at the window's minimum, 14.70 A peak (the edge-of-cloud Isc), v_max 56.3 V |
| **the 200 W window (new item, check minor 1)** | no input or output current sense: CSPIN/CSNIN on PV_P, CSPOUT/CSNOUT on TRK_OUT (484) | either a sense resistor and the LT8705A's input or output current regulation set to the window, or every downstream part (TRK_OUT, Q2, VIN_RAW, board A's front end) rated for what the inductor limit lets through (next row) |
| TRK_OUT (606), _TRK_A | declared 10.33 A (100 W x 0.93 / 9 V) | at 200 W: 186 W, 12.3 A at 15.1 V (a1elec CHARGER.md 2). With no current regulation the inductor limit sets the ceiling: the buck valley threshold is 69 / 86 / **102 mV** min / typ / max (8705af p.3), 13.8 / 17.2 / **20.4 A** over R5's 5 mOhm, and the maker notes it rises to about 130 mV at higher duty (p.22). Re-derive _TRK_A from the MAXIMUM |
| L1 (the stage's inductor) | XAL1510-103ME, 10 uH | ripple 4.18 A peak to peak from 34.29 V to 15.1 V at 202 kHz (5.27 A from 51.3 V), so the peak at the MAXIMUM valley threshold is about **24.6 A (25.7 A from 51.3 V)** against the part's Isat 26.3 A (a 30 percent inductance drop at 25 C, typical) and Irms 16 / 22 A (20 / 40 K rise; `v2/vendor/power/coilcraft-xal1510.pdf`). **Not shown adequate**: the writer rates L1 at the maximum threshold (and at the p.22 rise), or implements the window of the row above |
| the 0.93 efficiency (606) | declared near unity ratio (17.6 to 15.1 V) | at 34.3 to 15.1 V the stage bucks at 0.44 duty; the 0.93 is not shown at that ratio (bench) |
| R14, R15 SHDN (627) | enable above about 9.5 V | unchanged works (7.3 V on SHDN at 56.3 V, under its 30 V rating); a higher threshold is the writer's option |
| U5 MODE pin 37 | tied to LDO33, discontinuous | unchanged: no current into the array |

The FBIN pin sees 56.3 / 28.46 = 1.98 V at the array's cold open circuit, under its 30 V rating (8705af p.2).

## 7. The energy model's inputs (brief item 3), and the planes the array may face

- **STC rating:** 400 Wp (four RNG-100DB-H at 100 W, the maker's figure with no tolerance published; SunPower's is
  +6/-3 percent). Unchanged: the 400 Wp that section 9 and a1elec's design case use.
- **Performance ratio (40 degrees, facing south; `energy_runs.out` 1, 2):** 0.9417 is PVGIS's panel with maximum-power
  tracking at a free-standing mount. **Typical (B): 0.9417 x 0.9903 = 0.9326.** **Adverse (C), corrected (check B2):**
  the worst of the three fits at the worse end of the set-point window, cells 10 K hotter than the NOCT model and a 10 m
  lead keep 0.9322 of the maximum-power energy at those hotter cells, and the hotter cells themselves lose 0.9765 of the
  maximum-power energy at the typical cells (the model's figure; the maker's -0.42 %/K gives 0.9778, the lower is
  charged): **0.9103, so 0.9417 x 0.9103 = 0.8573**. The first issue's adverse 0.9078 did not charge that loss and took
  neither the resistors' tolerance nor the fit bracket.
- **The two design cases at 40/0 on this model** (`energy_runs.out` 3, 4): section 9's 4S18P MEETS in the typical case
  with 90.6 Wh at +20 C and 26.5 Wh at +15 C (down to +12.9 C) and in the adverse case with 87.8 and 23.7 Wh (down to
  +13.2 C); a1elec's two-pack case MEETS in the typical case with **30.7 Wh** at its lowest (lid 0.5 Wh, down to a lid at
  +9.6 C) and in the adverse case with **27.9 Wh** (lid 0.0 Wh, down to a lid at +10.8 C). REQ-072 stays FAIL: nothing is
  drawn, built or tested.
- **The planes (check B1; `energy_runs.out` 6).** The first issue's rule (30 to 60 degrees, within 45 degrees of south)
  rested on multiplying slope and azimuth factors and on scaling the 40 degree south day; the check showed both wrong on
  PVGIS's own answers, because the packs fill by early afternoon and what decides the night is the afternoon's sun, which
  an east-turned plane loses. **Both proxies are withdrawn.** Each plane of a grid (slopes 0 to 70 degrees in 10 degree
  steps, azimuths 45 degrees east to 45 degrees west in 15 degree steps, 50 planes) is now run on its own PVGIS DRcalc
  September mean day (filed under `v2/vendor/solar/pvgis-planes/`, scaled by the model's own factor 1.00782 found on the
  40/0 anchor, which reproduces the model's profile exactly), with its own fixed-point ratios, in a1elec's two-pack case.
  The planes that **meet in BOTH the typical and the corrected adverse case**, on this model:

  | slope | azimuths meeting both (negative east of south) | typical only |
  |---|---|---|
  | 0 (flat) | none: **flat does NOT meet in either case** | none |
  | 10 | none | -30 to +45 |
  | 20 | -15, 0, +15 | -45, -30, +30, +45 |
  | 30 | -15, 0, +15, +30 | -45, -30, +45 |
  | 40 | -15, 0, +15, +30 | -30, +45 |
  | 50 | -15, 0, +15 | -30, +30, +45 |
  | 60 | 0, +15 | -15, +30 |
  | 70 | none | 0, +15 |

  **The deployment rule restated from the grid, a result on this model: 20 to 50 degrees of slope, facing within 15
  degrees of south** (thinnest margins 3.3 Wh at 20/-15 adverse, 8.9 Wh at 50/-15, 9.5 Wh at 20/+15; every
  grid plane in that rectangle meets in both cases; 30 and 40 degrees also meet at 30 degrees west, 60 degrees only at 0
  and 15 degrees west). The rule is asymmetric because of the afternoon: planes turned west meet where the same turn east
  does not. The grid's 15 and 10 degree steps are its resolution; a plane between two meeting grid points is not itself
  run. PVGIS's other losses in 0.9417 (angle of incidence, spectrum, temperature) are the 40/0 plane's and are kept for
  every plane, labelled in the output.
- The day's packs are full by early afternoon on this model, which is why a few percent of ratio moves the lowest
  point by a few Wh at 40/0 while the plane decides the result.
