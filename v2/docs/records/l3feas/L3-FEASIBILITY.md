# Layer 3 feasibility: HF with the worst installation, the mission reference case, and the solar interface (stream l3feas, MESHSAT-1357)

**Second issue, 30 September 2026:** it answers CHECK-1 of `24942a5f` (accepted: no; B1 and seven minors; section 4 maps
them). Route R1 now carries its own Kelvin criterion, which the drafted one does not meet.

**30 September 2026.** Branch `fnd/l3feas`, from main at set 16. This page answers the owner's review of the Layer 3
decision brief. These words of the review bind it:

> "Retaining HF and requiring the worst conforming installation is not made logically contradictory by a candidate's
> 10.8 Wh modelled shortfall. It is an unmet target for that candidate. ... Perform the bounded feasibility assessment
> needed to determine whether a credible correction exists within the constraints. If no credible route exists, return a
> quantified trade-off to the owner. Do not automatically delete HF, loosen installation conditions or mark the target
> satisfied."

> "Approve topology separately from electrical compliance. Pin the panel revision and datasheet ... Provide the rating
> derivation or an explicit engineering obligation rather than treating owner approval as verification."

**What this page is.** It is the author's analysis, AI arithmetic, not a qualified review and not the independent check.
- It is **prototype design**: nothing is built, bought, powered or measured.
- It designs nothing and picks no target. No requirement is changed (`pcb_requirements.yaml` is untouched).
- Every result rests on the **CORRECTED PATH, case (iii), HYPOTHETICAL**: board A's charge path with every correction of
  r11dep's `R11-DEPENDENCY.md` assumed closed. As drawn, the circuit fails M1 on every lid (ENERGY-BASIS section 0).

**Labels.** Every figure carries its basis:
- **MAKER (page)**: a maker's document held in `v2/vendor/`;
- **NETLIST**: a committed netlist;
- **MODELED**: the energy model;
- **INFERRED**: a method stated beside it.

**Sources.**
- `hf_wab.py` prints `hf_wab.out`: Task 1.
- `solar_interface.py` prints `solar_interface.out`: Task 3.
- Both reproduce the committed records before printing anything, and refuse otherwise.

## 1. Task 1: HF with the worst installation, the feasibility disposition

**The combination.**
- **Lid:** the tablet-out lid, 4S14P, so the HF set stays inside the kit (REQ-002).
- **Day:** SC-37's mean September day on the 40 degree south plane.
- **Array build:** WAB, the worst array build.
- **Inputs:** WE.

On the corrected path this is **NOT MET by 10.8 Wh** (`energy_basis.out` 5, reproduced in `hf_wab.out` 0).

**Disposition: (b) INCONCLUSIVE.** A candidate route exists within the constraints, but whether it closes the gap rests
on evidence the tree does not hold. It is not (c): nothing shows the gap cannot be closed. It is not (a): at the lower
reading of U3's current, the route's margin sits within about half a point of undocumented efficiencies. That is the
rule of this stream for "conditional, not a basis".

### 1a. The routes, per pack and hour by hour (`hf_wab.out` 1 and 2; MODELED)

**The conditions** are the kit loads:
- PS-IDLE-SPEC 42.8 W plus the lid path's standby drain of 1.8 Wh over 72 h;
- the lid pack at 13.23 C and the base pack at +20 C;
- both packs full and aged at the start;
- each pack's store ends at its own 3.00 V line with the 5 % reserve.

| Route | What it is | TYP | WAB | Lines at WAB: STOP / COMB / EACH |
|---|---|---|---|---|
| **WE** (the reference) | as restated | 44.0 (base 44.0, lid 0.0) | **NOT MET, 10.8 unserved**: the kit stops at hour 71 (start 06 UTC) | fails / N / N |
| **R1** | U3's input limit at its **6.35 A clamp** (MAKER, SLUSE66A 9.6.22 p.80 and Table 9-1's RSNS_RAC = 0b rows, p.26; section 1b); minimum 6.25 A (INFERRED, 100 mA under, as WE's 6.1 A) | 70.7 (48.8, 18.1) | **19.4 (base 19.4, lid 0.0)** | kept / Y / N |
| R1, the lower reading | the same setting, minimum at the front page's 2.5 %: 6.191 A (INFERRED) | 62.3 (46.9, 9.9) | **7.5 (base 7.5, lid 0.0)** | kept / Y / N |
| **R2** | board E's stage at its maker curve's reading 0.965 (INFERRED from another circuit, curve_readings.out 2) | 69.3 (48.3, 14.9) | **12.7 (base 12.7, lid 0.0)** | kept / Y / N |

**Per pack, at the kit loads.** In every route the lid pack reaches its own line on the WAB build, and the base alone
carries the kit's 42.8 W:
- with R1, for 1 hour on the last night (UTC 05, start 06) or 2 hours (UTC 05 to 06, start 18);
- the base's lowest store is then 19.4 and 21.0 Wh.

That is within each pack's limits. The lid stops at its line, and the join lets the base carry (section 2, the join). The
EACH line, each pack above 4.2 Wh, is not met by any route. Of the kit-level line of section 2:
- **conditions 1 and 2** (the kit never stops; the carrying pack above the floor) are met by R1 and R2 on the model;
- **condition 3** (the paths within their limits) is INFERRED;
- **condition 4** (the node's voltage against every load converter's minimum input) is NOT ESTABLISHED.

**Timing.** On the WAB mean day U3's input cap binds for six hours a day, UTC 09 to 14 (18 of 72 hours). The array's
largest hour is 178.6 W into the stage, under the model's 200 W window, so the window never binds.
- R1 raises the cap from 116.8 W to 119.7 W in exactly those hours. That is where its gain of 30.2 Wh on the lowest store comes from.
- The deficit is decided by the last night: the lowest stores fall at UTC 05 and 06.

**Conversion losses.** WE's own terms are unchanged in every route:
- U3 at the makers' maxima (0.9733 by TI's method);
- U3B at its lower bracket (0.963);
- the stage and the front end at 0.93 DECLARED;
- the pack's charge efficiency at 0.95 INFERRED;
- the lid loops at their ESTIMATE's worse end.

### 1b. What each route rests on (`hf_wab.out` 3 and 4)

**R1: U3 at its 6.35 A clamp.** This is an engineering setting: a register value inside the drafted entry.
- **The setting's basis** (MAKER, `hf_wab.out` 4):
  - It stands on SLUSE66A 9.6.22 (p.80): with a 10 mOhm sense, "50 mA to 6350 mA, with 50-mA resolution. The upper
    boundary is implemented through DAC clamp", with no inductance condition.
  - Every RSNS_RAC = 0b row of Table 9-1 (p.26) also reads 6.35 A.
  - 9.3.5 (p.25) is not its basis: it assumes both sense resistors at 10 mOhm, where board A's R17 is 5 mOhm. Table 9-1
    has no row for board A's 4.7 uH either.
  - **ILIM_HIZ does not bind** (9.3.6, p.26: the lower of IIN_DPM and the pin). R19 16.5k from REGN over R20 34.8k
    (NETLIST) put the pin at 3.87 V at REGN's 5.7 V minimum (p.11): 7.17 A by V = 1 V + 40 x IDPM x RAC (p.6), above
    R1's 6.509 A maximum. At REGN's 6.0 V typical the pin reads 4.07 V, above the 4.0 V that disables it (p.80).
- **Front-end limit margin.** U3's maximum is then 6.509 A (the larger of +100 mA, p.80, and +2.5 %, p.1). Through R11
  that is 6.569 A with the carried 0.060 A of other loads, or 6.588 A with four FETs' 0.079 A. The stacked minimum of
  6.793 A leaves **+0.224 A and +0.205 A** (INFERRED).
- **The margin holds only with R1's OWN Kelvin criterion** (CHECK-1 B1; `hf_wab.out` 4). At most this much copper may be
  shared between R11's pads and its two taps:

| Current through R11 | Working temperature | At 25 C, copper at 100 C | At 25 C, copper at 62.1 C | At 6.0 A on the bench |
|---|---|---|---|---|
| 6.569 A (0.060 A of other loads) | **0.215 mOhm** | **0.166 mOhm** | 0.188 mOhm | 1.00 mV |
| 6.588 A (four FETs' 0.079 A) | 0.196 mOhm | 0.152 mOhm | 0.171 mOhm | 0.91 mV |
| drafted 6.415 A, r11dep C-1 | 0.371 mOhm | 0.286 mOhm | 0.324 mOhm | 1.72 mV |

  **Closing C-1 at its drafted 0.29 mOhm does not admit R1.** Such a layout senses 43.75 mV at 6.569 A with the copper at
  100 C, over the 42.7 mV minimum (VSNS 43 mV less the 0.3 mV bias), so the front end can limit first.
- **The corrections B-1 to B-5.**
  - All must be closed, as for the corrected path.
  - **VBUS20's bank in service reaches 100.4 % of its 2.8 A rating at a 2:1 ESR spread** (within it matched). So B-4's
    re-sizing, already owed for the highest permitted current, must also cover the in-service current at 6.569 A.
  - L1 at 9 V is covered by B-1's schedule.
  - The in-service currents of the front end, the stage and the copper rise by 2.4 %.
- **Maker documents still missing.**
  - **C-7, U3's minimum input current at the setting.** SLUSE66A prints only the maximum. The route's result spans **19.4
    Wh** at the INFERRED 6.25 A down to **7.5 Wh** at 6.191 A.
  - **C-8, the three efficiencies.** Each input alone must reach at least these values:

| U3's minimum | Charge efficiency: STOP / COMB | Stage or front end: STOP / COMB | Against the values WE carries |
|---|---|---|---|
| 6.25 A | 0.932 / 0.936 | 0.906 / 0.911 | charge 0.95 (INFERRED, no document); stage and front end 0.93 (DECLARED) |
| 6.191 A | 0.943 / 0.947 | 0.919 / 0.925 | the same |

  At 6.191 A the margins are **0.3 and 0.5 points** on COMB (0.7 and 1.1 on STOP). That is within one point of undocumented
  figures: conditional, not a basis.
- **Power limits.** The 200 W window never binds on this day. The front end does not limit, with R1's Kelvin criterion.
- **Requirements kept:**
  - HF inside (REQ-002);
  - the case (REQ-019);
  - the array as the owner stated it;
  - the installation condition (WAB, 40/0);
  - REQ-072's day, load and 72 h;
  - REQ-075 (the charge current settings are unchanged).

  **No approved requirement moves**, with one exceedance that deepens. R1 raises the stage's in-service input from
  154.9 W to **158.6 W** (6.569 A at 20.887 V over 0.93 twice). That deepens **REQ-016's already open exceedance**
  (at most 100 W into the stage), which is the owner's and is open for Option A(i) as a whole.

**R2: the stage at its maker curve's reading.** This is not a correction. It is a figure the tree must establish (C-8).
- If board E's stage is shown at **0.952 or better** at its operating point, with every other input at WE, the combination
  meets on COMB with no change at all (ENERGY-BASIS section 7).
- At 0.965, the reading of LTC's 35 V curve for board E's own FETs, it meets with 12.7 Wh.
- It rests on the stage's efficiency at 34.3 V to 15.1 V, which no maker document gives. That is bench evidence.

### 1c. The evidence that decides it

The disposition moves to (a) once three things are in hand:
1. **U3's minimum input current** at the setting used, from TI or measured (C-7).
   - At the drafted 6.2 A setting, a minimum of 6.174 A or more already meets COMB, with no change (ENERGY-BASIS section 7).
   - At the clamp, the INFERRED minima give 19.4 Wh (6.25 A) and 7.5 Wh (6.191 A).
2. **The three efficiencies** (C-8), measured on the prototype or given by the makers for these circuits, with margin over
   the table above.
3. **The corrected path's corrections**, closed as r11dep lists them, with two additions for R1:
   - **its own Kelvin criterion**, at most 0.166 mOhm at 25 C (0.152 mOhm with four FETs), in place of C-1's 0.29 mOhm;
   - **the bank's in-service case** added to B-4.

**It moves to (c) only on a re-run, not on any threshold alone.** The combination is re-run with every measured value
together (U3's minimum, the three efficiencies, and R1 and R2 together included), and no route meets. The table's
thresholds hold each input alone with the others at the route's values, and inputs offset one another: a stage measured
above 0.93 offsets a charge figure under its threshold.

**For that case only, the record's own rows** quantify what else moves the result. They are not proposals, and nothing
here deletes HF or loosens the installation:

| Row (ENERGY-BASIS section 8b and section 1) | 4S14P at WE, WAB | Service |
|---|---|---|
| the QMX-out lid (4S15P, HF leaves the kit unless a location is found) | 19.5 Wh (lid 0.0) | reduces: HF leaves |
| PS-IDLE-SPEC with both WiFi link cards off (36.9 W) | 172.6 Wh | reduces: the kit-to-kit link is off |
| the array at 600 Wp | 105.1 Wh | outside the owner's stated array |

## 2. Task 2: the mission reference case, stated exactly for L3-D02

The review's criterion is at the kit loads: "the specified service continues for 72 hours within voltage, power and pack
limits; combined stored Wh alone is insufficient."

| Element | The reference case | Established or assumed |
|---|---|---|
| **Initial state, each pack** | Both packs full at the start: each at its aged usable energy, with no carry-over. Aged to 80 % of the cells' specification minimum. Base 4S6P at +20 C; lid 4S14P or 4S15P at the day's minimum air, 13.23 C | **Full and aged:** ESTABLISHED by requirement (REQ-072 "starting from a full, aged pack (REQ-014)"). **Base +20 C:** REQ-014's basis, an ASSUMPTION about the closed base's temperature. **Lid at 13.23 C:** ASSUMED (the air's minimum, no thermal model of the lid; its temperature factor is INFERRED, a linear lower bound between -10 and 20 C) |
| **Load profile** | PS-IDLE-SPEC, 42.8 W constant at the pack terminals (POWER-THERMAL.md section 4: monitor on, radios idle, APRS beacons), plus the lid path's standby drain of 1.5 to 1.8 Wh over 72 h (reconcile_lid_panel.out NOTES; WE carries 1.8 Wh). Both are split between the packs by capacity | **The mode:** ESTABLISHED as the requirement's mode (REQ-072, SC-05). **Its 42.8 W:** a desk figure from the loads' documents, not a measurement (POWER-THERMAL.md gives 33.1 to 82.8 W as its bounds). **The drain:** INFERRED |
| **Panel orientation** | ONE plane: 40 degrees of slope facing south (azimuth 0), PVGIS's optimum at Leiden (52.160, 4.497). No band is established (ENERGY-BASIS 1a item 3) | **The day:** ESTABLISHED as SC-37's reference day (PVGIS 5.2, SARAH2, the September mean day, 4.014 kWh/m2 on the plane, repeated for 72 h). **The plane:** the model's reference, ASSUMED as the deployment |
| **Installation** | **TYP:** fit "Rs 0", the input held at 34.29 V, NOCT 45 C, a 5 m lead (0.9903). **WAB, the worst array build:** the worst of three fits, the set point at its window's worse end, cells 10 K above NOCT, a 10 m lead, and the hotter cells' own loss (0.9103). The review's "worst conforming installation" is WAB | **Both builds:** DEFINED (ENERGY-BASIS 6b). **Their ratios:** MODELED on the held panel sheet, whose revision is not pinned (section 3) |
| **Each pack's cutoff** | CONOPS 4c's graceful line per pack: RSOC 5 %, or the lowest cell at 3.00 V under load, whichever comes first (the model's store ends there). At a 4S pack that is 12.0 V under load (INFERRED). Hardware floors below it, per pack: the gauge's CUV 2.50 V for 4 s; the second level's UV 2.25 V; the lid path's LM5069 9 V floor (2.25 V a cell) (TOPOLOGY.md 4) | **The line and the floors:** ESTABLISHED as drafted thresholds (TOPOLOGY.md 4 from pcb_pack_protection.yaml and the makers). **The line as the model's end of store:** MODELED |
| **The kit's shutdown** | The host turns the lid path off when the lid reaches its line, and shuts the kit down when the base reaches its line with the lid already out. The kit's shutdown is therefore the base at its line: 12.0 V at the base pack under load | DRAFTED host rule (TOPOLOGY.md 3c), not in firmware |
| **Does the kit continue when one pack cuts off?** | **Yes.** The lid reaches its line: its ideal diode passes nothing and the base, hard-wired to VBAT, carries the kit. The base reaches its line first: the lid carries through its path, limited to 8.7 to 11.0 A (fault-free), until the lid reaches its own line. PS-IDLE-SPEC needs about 3.3 A at 13 V (INFERRED), under 8.7 A | The **join** is a DRAFT (TOPOLOGY.md 3c: LM74700-Q1 ideal diode, reverse threshold -17 / -11 / -2 mV in under 0.75 us, MAKER; LM5069-2 limit 8.7 / 9.8 / 11.0 A, MAKER). **Its limits:** the lid path defaults ON; the host's join rule (0.20 V) keeps the lid-to-base transfer at or under 2.5 A; single faults that defeat it (Q7B shorted, Q_LD welded) are in TOPOLOGY.md 6 for the qualified battery review. None is drawn in a generator |
| **Power-path case** | Case (iii), the CORRECTED PATH, HYPOTHETICAL. Case (i), as drawn, fails M1 on every lid; case (ii), resistor-only, is inconclusive (ENERGY-BASIS section 0) | ASSUMED: every r11dep correction closed |
| **Pass line at the kit loads** | Four conditions, all required (listed below the table) | **Conditions 1 and 2:** MODELED. **Condition 3:** INFERRED at 42.8 W. **Condition 4:** NOT ESTABLISHED: no record reads every load converter's minimum input against 12.0 V at the node. An obligation |

**The pass line's four conditions:**
1. **STOP:** every hour of the 72 h serves the load, with each pack drawn only to its own line.
2. **The margin:** the lowest store of the pack or packs still able to carry the kit stays above the model's
   hourly-step sensitivity, 4.2 Wh. This is COMB's figure, meaningful because a pack at its line contributes nothing.
3. **Power:** every path stays within its limits in every hour: the lid path under its 8.7 A minimum; the charge currents
   within U3's 3.968 A and U3B's 7.936 A and the cells' REQ-075 current.
4. **Voltage:** the node stays at or above every load converter's minimum input with the base at 12.0 V.

COMB alone is not the line: a COMB figure with a pack drawn past its line, or a path past its limit, fails.

## 3. Task 3: the solar interface for L3-D05 (`solar_interface.out`)

### 3a. The panel the tree holds, and its revision

| Item | Held figure (MAKER, `renogy-rng-100db-h-flexible-100w-datasheet-2018.pdf` p.2) |
|---|---|
| File | sha256 `8891821cf70f4124fdb1f02e2fbc7a4a0f4102c51f33ad39c2bfa32e6b60a29f`, 2 pages, title "RNG-100DB-H spec". A retailer's copy: the maker's download page did not render to this host |
| Revision | **NONE printed** on either page. PDF metadata, in the file's own UTC-7 stamps: created 17 August 2018, modified 6 August 2020 |
| Electrical | Pmax 100 W; Vmp 18.9 V; Imp 5.29 A; Voc 22.5 V; Isc 5.75 A; 36 cells (4 x 9); system voltage 600 V DC; maximum series fuse 15 A |
| Coefficients | Pmax -0.42 %/K; Voc -0.31 %/K; Isc +0.05 %/K; NOCT 45 +-2 C; operating -40 to +85 C |
| Mechanical | 1219 x 549 x 2 mm, 1.9 kg; connectors 30 A, 1000 V DC, IP67; 12 AWG leads |

**Renogy's current US page, as the owner's review reports it (not held; compared, not substituted):** Voc 24.4 V, maximum
series fuse 15 A, 1093 x 582 mm.
- **Voltage.** If the kit's panels were that revision, 2S2P's open circuit would read 55.61 V at -20 C cells, 58.63 V at
  -40 C, and **61.00 V by the 1.25 clause, over the coordinator's 60 V safety extra-low-voltage ceiling** (INFERRED
  with the held -0.31 %/K; a1solar: "the standard behind it is not held"). The held sheet
  gives 56.25 V.
- **Energy.** Its Vmp and Isc are not in the review. The stage's fixed input point (34.29 V) and its 0.990 ratio are
  derived from the held Vmp, so they would move too.
- **The series fuse is the same 15 A**, so the protection rows below do not move.

**Pinning the revision is therefore an engineering obligation (O-1).** The held sheet does not settle it. **Closure:**
- the maker's sheet for the revision actually bought is filed, with its revision mark and sha256 in `v2/vendor/sources.txt`;
- a1solar's `array_calc.py` is re-run on it (with the worse of the two sheets for every rating, as SELECTION.md's
  reversal line says);
- the fixed-point ratios, the 34.29 V set point and the voltage basis are re-derived from it.

### 3b. The interface, distinguished, each with its derivation or obligation

| Quantity | Figure | Derivation | Basis | Obligation and closure |
|---|---|---|---|---|
| **Available array power** (2S2P, 4 x 100 W) | 400 W at STC; 329.9 W at 1000 W/m2 and +70 C; 475.6 W at 1000 W/m2 and -20 C; a transient bound of 594.5 W with the 1.25 edge-of-cloud factor; on the mean day at most 194.3 W (TYP) and 178.6 W (WAB) | 4 x Pmax; the fit (array_calc.out 5); Pmax x (1 - 0.0042 x (-45)); x 1.25; the model's hours | MAKER; MODELED; INFERRED | O-1 (section 3a, with its closure) |
| **Controlled converter input power** | **NOT CONTROLLED as drawn.** The 200 W is the energy model's window only. Board E's LT8705A has CSPIN and CSNIN on PV_P, CSPOUT and CSNOUT on TRK_OUT, with no sense resistor. The stage takes what the load asks: 154.9 W in service; 226.3 W at the front end's highest permitted current. Its own ceiling is about 331 W in | NETLIST (U5 pins 30 to 33); 8705af pp.11 and 12 (CSNOUT "Connect this pin to VOUT when not in use", p.11; CSPIN "Connect this pin to VIN when not in use", p.12); r11dep; the buck valley limit at its maximum, 20.4 A x 15.1 V / 0.93 | NETLIST, MAKER, INFERRED | **O-2:** implement the window (a sense resistor with the LT8705A's input or output current regulation set to it), or rate every downstream part for the uncontrolled ceiling. Closure: the declared figure in gen_sch_e.py with its derivation, and a bench measurement of the stage's input at the array's maximum with the load at its maximum |
| **Cold open-circuit exposure** | 51.28 V at -20 C cells; 54.07 V at -40 C (the panel's limit); **56.25 V by the 1.25 clause, the voltage basis** | 2 x Voc x (1 - 0.0031 x dT); 2 x 1.25 x Voc | MAKER, INFERRED (the clause from SunPower 524958 Rev F 3.0, held back) | **O-3:** every PV_P part rated above the pinned revision's basis (56.25 V held; 61.0 V if the current page's revision, which exceeds the coordinator's 60 V safety extra-low-voltage ceiling, whose standard is not held). Closure: the ratings in gen_sch_e.py against the pinned basis (a1solar ARRAY.md 6, gated on REQ-016) |
| **Short-circuit current** | a string: 5.75 A STC, 5.88 A hot, 7.35 A with the factor; the array: 11.50, 11.76, 14.70 A | Isc x (1 + 0.0005 x 45) x 1.25, per string and x 2 | MAKER, INFERRED | none beyond O-1 |
| **Fault currents** | (a) A short at the array's output or in the lead: at most 14.70 A, from a current source; F2 never opens on it. (b) A fault inside one string: back-fed by the other at most 7.35 A. (c) A back-feed from the kit: VIN_RAW through Q2 (the ideal diode U4 failed), M4 and M1's body diode into PV_P. It needs a single fault while M4 conducts with VIN_RAW above the panel, and its sustained source is the vehicle entry, limited to 6.15 A by its LM5069 while that entry holds | INFERRED on the NETLIST topology (Q2, Q6, Q3 nets) | NETLIST, INFERRED | **O-4:** board E's writer files the fault tree of (c), and the prospective current with the vehicle entry failed too |
| **String versus combined-feed protection** | **No string fuse** for faults inside the array: 7.35 A is under the maker's 15 A series fuse rating (read as the module's reverse-current rating, the usual meaning). **F2 is in the combined feed** (NETLIST: PV_IN to PV_P). At 20 A it exceeds one string's 15 A, so with one string disconnected F2 does not protect the other. That string's protection rests on (c) being bounded at 6.15 A, not on F2 | (Np - 1) x 7.35 A against 15 A; the netlist | MAKER, NETLIST, INFERRED | **O-5:** read the applicable standard (IEC 62548 or NEC 690.9; neither is held) and confirm the no-string-fuse rule, together with O-4's bound. If the bound cannot be shown, a string fuse per string is the option (at least 1.25 x 7.35 = 9.2 A and at most 15 A: 10 A). Closure: the clause cited and O-4 filed |
| **The combined-feed fuse F2** | **20 A**, at least **56.25 V DC**, with an interrupting rating at or above the kit-side prospective fault at that voltage. As generated it is a 10 A MINI blade at 32 V DC: not usable | 1.25 x 14.70 = 18.37 A, the standard step at or above it; the voltage basis | INFERRED (a1solar ARRAY.md 4) | **O-6:** the fuse and holder chosen with their maker's DC voltage and interrupting ratings against O-4's fault current. Closure: the maker's sheet filed and the rating shown |
| **Lead, J_SOLAR, the wall's solar pair** | each at least **20 A at 56.25 V** (the conductor at or above the fuse that protects it). As generated J_SOLAR is a JST-VH 10 A; the wall pair's contacts are not settled (size 16 at 13 A or size 20 at 7.5 A) | at or above F2 | INFERRED | **O-7:** each part chosen with its maker's current and voltage ratings. Closure: the maker figures filed |

### 3c. What the owner's approval would, and would not, establish

**It would establish the requirement-level choices** (REQ-016's restatement is his, and it is already open):
- the topology: four RNG-100DB-H in 2S2P, about 400 Wp, into a stage of the 200 W class;
- the voltage class: about 52 V cold open circuit, 56.25 V by the clause;
- the installation condition the mission is judged on.

**It would not establish:**
- any rating of section 3b (O-2 to O-7);
- the panel revision (O-1);
- that the stage limits its input power: it does not, as drawn;
- the fault protection's adequacy;
- conformity to any standard;
- the energy result, which is case (iii), HYPOTHETICAL.

Those are engineering obligations with the closure criteria above. Approving the topology is not verifying it.

## 4. CHECK-1's items, and where each is answered

| Item | Answer |
|---|---|
| B1, R1's Kelvin criterion | 1b: at most 0.215 mOhm working, 0.166 mOhm at 25 C (0.196 and 0.152 mOhm with four FETs); the drafted 0.29 mOhm does not admit R1 (43.75 mV over 42.7 mV); 1c item 3 carries it. Printed in `hf_wab.out` 4 |
| 1, O-1's closure | 3a: the revision bought filed with its mark and sha256, `array_calc.py` re-run, the ratios, set point and voltage basis re-derived |
| 2, the (c) trigger | 1c: a re-run of the combination on every measured value together, R1 and R2 included; no threshold alone |
| 3, "met" at the kit level | 1a: conditions 1 and 2 met on the model, condition 3 INFERRED, condition 4 NOT ESTABLISHED |
| 4, REQ-016 | 1b: the stage's in-service input 154.9 to 158.6 W deepens REQ-016's open exceedance (at most 100 W) |
| 5, the 6.35 A setting's basis | 1a table and 1b: SLUSE66A 9.6.22 (p.80) and Table 9-1's RSNS_RAC = 0b rows (p.26); 9.3.5 and the missing 4.7 uH row named; ILIM_HIZ does not bind (7.17 A at REGN's minimum; 4.07 V typical disables the pin) |
| 6, the 60 V ceiling | 3a and 3b: the coordinator's safety extra-low-voltage ceiling, its standard not held (a1solar) |
| 7, the LT8705A's pages | 3b and `solar_interface.out` 3: pp.11 (CSNOUT) and 12 (CSPIN) |

**Outputs.** `hf_wab.out` is regenerated: section 4 gains the Kelvin criterion per setting, the stage's input, the
setting's basis and the ILIM_HIZ check; sections 0 to 3 are byte identical. `solar_interface.out` is regenerated for
minors 6 and 7 only; every figure is unchanged.
