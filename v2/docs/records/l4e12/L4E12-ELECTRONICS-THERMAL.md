# L4-E12: the kit's electronics against the inside air at D-02a's +55 C margin and E5's +60 C dwell (U-02)

MESHSAT-1478 under MESHSAT-1357, layer 4 task L4-E12, 2 October 2026, revised the same day after the collaborator's focused
check (`checks/astra-check-l4e12-1.md`, NOT YET on B1 to B3) and again after its targeted recheck
(`checks/astra-check-l4e12-2.md`, NOT YET on B2 and B3); section 12 maps each item to its change. **Prototype design, desk
arithmetic: nothing has been bought, built, powered or measured, and no kit has been field deployed.** Every figure comes from
`l4e12_thermal.out` (the script `l4e12_thermal.py` reproduces it byte for byte, pins 69 inputs by sha256 and reproduces
`records/rv-pwr/pwr_budget.out` and `records/hc2/pwr_red2.out` before any figure) and carries its class: MAKER (a maker's
document, page named), MODELED (the tree's power and thermal model and W4's lumped film coefficients), INFERRED (method
stated), ASSUMPTION (a figure no held document gives), CONDITIONAL (holds only on a stated condition). Section numbers in
brackets point to the `.out`.

## 1. The answer in short

- **The finding, part by part.** At T-H1's floor (LO-01a's 1.6664 W/K, reproduced, [2b]) the heat stage's 24.996 W and L4-E8's
  ballasts (2.09 W, +1.254 K) put the mixed inside air at **71.25 C in E3-O and 76.25 C in E5's dwell** (MODELED, [2c]). Judged
  by the corrected rule (every limit with its rating category; powered parts on their recommended or operating ranges; an
  absolute rating only as an exclusion screen, [1j]), the screen of every fitted line, module and undeclared line [3] finds at
  E5: the RockBLOCK 9704, the SA868 and its G6K relay, the LimeSDR and the H5007NL past +70 C by 6.3 K at the mixed air (11.9 K
  in the running cooler's exhaust) and the PCM2912A codec past its recommended +70 C; the SGP41 past Table 4's recommended +50 C
  by 26.3 K and Table 5's absolute +55 C by 21.3 K; the MAIN pushbutton (ATP19) past +55 C by 12.6 to 21.3 K; the e-paper past
  its only stated +60 C by 7.6 to 16.3 K; board E's and board C's TLV75533 regulators past their recommended +125 C junction;
  the PI and TEST pushbuttons and the sealed USB-C at +70 C in their plate-to-air span.
- **A route that conforms to the stated acceptance exists, CONDITIONAL [5].** E3-O runs exactly as TEST-PLAN states it: deployed, monitor and radios on,
  C1's shedding the one control action; every radio C1 leaves on stays on for the four hours. Its heat (27.086 W with the
  ballasts) holds the mixed air at or under +70 C from **1.806 W/K**. E5 requires logging, not the radios, so the hold acts in
  E5 only; under it 21.587 W need **2.159 W/K, the binding line** (2.709 W/K if the hold is not used). At 2.159 W/K E3-O's mixed
  air is 67.55 C and E5's 70.00 C.
- **The hold's trigger window [4d].** Between E3-O's steady 67.55 C and the 70.00 C by which E5 needs the hold the window is
  2.45 K; less the reference's error twice (TMP117 +-0.2 C, MAKER) and 0.254167 K of lag, the reference may sit at most
  **+-0.899099 K** from the air at the +70 C parts. The TMP117 is a board sensor under the coolers: across the exhaust's 0 to
  5.64 K the window does not exist (it would need 3.111 W/K). It exists only with a reference placed in the mixed air near those
  parts or calibrated at T-H1 to +-0.899099 K: CONDITIONAL.
- **The SGP41 [5d].** Its own shutdown runs on a TMP117 on its carrier (+-0.15 C maximum to 70 C, MAKER; the BME688's +-0.5 C
  sits in Bosch's Typ column and is not used): off at a reading of **54.0 C** (54.095833 C exact, rounded down; the SGP41 then
  at most 54.904167 C, under Table 5's absolute +55 C), on and its output used only at or under **49.0 C** (49.095833 C exact;
  at most 49.904167 C, under Table 4's recommended +50 C). Inside the envelope that needs its location at or under 48.35 C at
  +40 C in every state. The coolest place that still samples the bay air, the east wall's inner skin in the pack pocket, needs
  **2.535 W/K**: with the lid open inside W4's range and under 32.53's, with the lid closed over every conductance the record
  carries (32.53's 1.5 to 2.0, W4's high case 2.49). And the envelope stores the kit at -20 to +45 C, outside Table 4's 5 to
  30 C storage, which no location changes. **No location holds it inside its maker's conditions in the envelope**: the first
  revision's claim that its function was kept at the line is withdrawn. At the margins it is off, under Table 5's +70 C
  short-term storage (absolute): INCONCLUSIVE, Sensirion's duration and recovery owed (drafted).
- **Approach (a), the enclosure alone, is not rejected but not selected**: 2.709 W/K lies over the low case's outer-film cap
  (2.10 W/K) and under W4's high case (2.85 W/K, 3.86 with an infinite inside film); it is what applies, with no hold, if T-H1
  reads at or over it. **(b), wider-rated parts**, is not selectable by the session (five device-set parts, CHO-001).
- **One owner question is raised [6], after the routes are assessed: the SGP41 in the envelope** (CFL-002's conflict, CHO-001's
  pick against REQ-042's VOC channel under D-02a). Options: A, a BME688-class sensor in its place (the session's
  recommendation); B, the VOC channel dropped; C, the SGP41 kept with its channel reported as not covered while its reference
  reads over 49.0 C and after storage outside 5 to 30 C (section 8). Nothing at the margins forces a question: no part there has
  every route rejected on held evidence. Escalation on T-H1's reading stays open (section 8).
- **33 lines cleared only by an absolute rating are INCONCLUSIVE** [7d] (CSD17577Q5A's +150 C among them; the least clearance
  11.8 K), each owing a maker's statement supporting operation or the parts discipline's derating rule (Layer 6).
- **U-02 stays CONDITIONAL**, on: T-H1 lid open with fans at or over 2.159 W/K; the hold's reference placed or calibrated to
  +-0.899099 K; the SGP41's shutdown at the margins (a TMP117 on its carrier within 0.5 K, the switch, the bus, Sensirion's
  duration) and the owner's answer for its in-envelope function; the MAIN, PI and TEST pushbuttons picked to +85 C; PDi's
  storage statement; the two 3.3 V regulators changed; the +70 C parts out of the running cooler's exhaust; the fans' rating
  (architecture-level), ten other lines with no range held and the 33 lines cleared only by an absolute rating (downstream).
  The sealed case and the power path's topology stay.
- **U-02 in depth (section 13, the dependency round of 2 October 2026).** The 2.159 W/K is E5's heat under the hold (19.497 W
  into the case plus L4-E8's 2.09 W) over the 10 K from E5's +60 C dwell to the +70 C class, at 0 K of margin; it moves
  0.100 W/K per watt and 0.216 W/K per kelvin of limit. It assumes the lid open, the fans running (slot 3's cooler fan and the
  two mixers; D-18 not picked, no fan's rating held) and the plate and walls as the only path out. The fans' power is counted
  in the power budget, the profile, the replay and L4-E9's endurance (2.0 W in the hold, 3.1 W in the profile), not in the
  8.4 W with no document. T-H1 runs on the prototype bench at Layer 9 once the owner authorises it, with dummy heaters in an
  empty Peli 1450 (draft procedure beside this record); it passes at a reading of 2.416 W/K or more. If it reads short, the
  plate coupling and a deeper hold in E5 (the session's) hold E5 to 1.125 W/K and E3-O to 1.399 W/K; under that only a
  deviation of E3-O or a re-pick remains, the owner's.
- **U-02's class (section 14, the consolidation): T-H1 DECIDES.** A first-principles conservative bound gives 0.566 W/K (E5)
  and 0.607 W/K (E3-O) with the fans' flow credited at zero. The budget's 1.22 W/K already assumes the fans' inside film. With
  every session measure, E5 holds and E3-O is short by 0.212 W/K (the module reaches 92.61 C against +85 C). The smallest
  experiment is one lid-open, fans-on point at 21.2 W: 2.462 W/K or more keeps the design as stated, 1.516 W/K or more keeps
  it with the fallback, 0.951 W/K or more keeps E3-O with every session measure, and below that the owner decides.
- **Heat rejection for the approved profile (section 15): no approach reaches the need on bounded evidence.** The profile's 43.4 W
  at +40 C needs 1.447 W/K, and charging on the design day needs 1.507 to 1.832 W/K. Fins on the plate, leading the large loads
  into the plate, and the lid as a radiator, assembled, reach 1.384 W/K: 1.252 W short. The remaining options are the owner's:
  PS-IDLE as a labelled alternative at +40 C (40.2 W fits that route), or a requirement change. U-02 stays a closure condition
  on T-H1's reading. (Its closing line, one point at two heaters (42.4 W) at 1.509 W/K, is corrected by section 16.)
- **The thermal reconciliation (section 16, the owner's amendment of 2 October 2026, 14:20).** The 1.509 W/K line established
  only the profile's +70 C class at +40 C, which no requirement asks for (C1 sheds the profile at +50 C inside air, REQ-024;
  D-02b runs one module above +35 C); the words "operation at +40 C" are withdrawn. The owner's 2.83 W/K belongs to no
  requirement's mode. P is the heaters plus the fans; the room reading is the conservative side (1.6 to 3.7 %); the endpoint is
  a drift of at most 0.1 K/h over an hour or a first-order fit over three time constants; authorisation is the owner's,
  acceptance the coordinator's check. (Its +55 C line and its "closes four conditions" are corrected by section 17.)
- **The fix round of the Layer 4 review (section 17, astra-check-l4close-1's B3, B4 and B7).** The SGP41's +55 C is Table 5's
  absolute row: a screen, never a line; its sensing ends at Table 4's +50 C, and option C switches it off at a 54.0 C reading,
  never keeping it powered on +55 C. Every required mode now carries its heat balance, ambient and every correctly categorised
  local limit, and its governing line is the tightest. The heat stage at +40 C is governed, as ruled, by the SGP41's Table 4
  (2.554 W/K on the pack, 2.709 W/K on shore, read at 2.905 and 3.081 W/K), and under C, A or B by the cells' hot stop H1 (1.666
  and 1.642 W/K, read at 1.804 and 1.767 W/K); REQ-014's profile at +20 C by C1's +50 C (1.447 W/K, read at 1.508); E3-O and E5
  by the e-paper's unpowered range until PDi states one (then 1.806 and 2.159 W/K); charging on the design day by T4 on the
  charging cells (2.025 and 2.525 W/K, read at 2.123 and 2.677). The charging heat is a balance: 50.044 W on the model's
  boundary, 52.134 W with the solar stage's ballasts, so K7 and K8 need 1.810 and 2.200 W/K (read at 1.889 and 2.315). The
  battery-only run coupled to C1: on the bound C1 sheds the profile from 2.01 h and the run lasts 2.52 to 2.95 h with its shed
  states; 2.52 h stays energy-only. A bench point closes only the conductance of its own configuration. The addendum (17.9): the
  outside capacity with a zero inside resistance (1.856 to 1.906 W/K at the margins' rises, conservative; section 14's 1.540 to
  1.571 W/K was the bound with a 50 m/s inside flow) leaves four lines over the MODELLED capacity even with the route (a model
  figure on named coefficient ends, not a physical bound), none of them shown impossible (the review of the provisional fixes,
  L4-F04): E3-L at +40 C lid closed as ruled, a MODELLED SHORTFALL OF THE ANALYSED ARRANGEMENT (the SGP41's Table 4 on the mixed
  air; short by 0.275 W/K on the pack, 0.430 W/K on shore), and the e-paper's unpowered +60 C row at E3-O (short 0.955 W/K) and
  E5 (no modelled room), a MISSING STORAGE QUALIFICATION; no DEMONSTRATED CONFLICT. Every other line T-H1 decides, some only with
  the route fitted.

## 2. The acceptance, read first [1]

| Source | Text (quoted) |
|---|---|
| D-02a, owner ruling 25 Sep 2026 | "TEST-PLAN's +55 C operating, +71 C storage and -33 C storage are QUALIFICATION MARGINS over the -20 to +40 C use and -20 to +45 C storage envelope, with two pass lines: operate to specification inside the envelope; survive and recover at the margin." |
| SC-03 (E5) | "A qualification margin, judged like E3 and E4 under D-02a: survive and recover at the margin, and operate to specification inside the envelope." |
| TEST-PLAN E3 (section 2) | "**E3-O** operation 4 hours at +55 C deployed with the monitor and radios on, on shore or vehicle input, as a deviation with the cells kept out of the heat"; pass: "survive and recover (D-02a): no damage, no deformation, no lost data or keys, CM5 throttling logged but no shutdown, and the functional check passes once the kit is back inside the envelope with its pack refitted" |
| TEST-PLAN E5 | 10 cycles of 24 h at 95 % RH, 30 to 60 C, "deployed (lid open; the case has **no vent opening**", "on shore or vehicle input with the kit logging"; pass: "survive and recover (D-02a, SC-03): no condensation inside (inside humidity log), no corrosion, functional check passes" |
| TEST-PLAN section 6, the deviation's arrangement | "the kit's controls read room-temperature cells, so of their temperature triggers only C1's inside-air trigger sheds modules" |
| CONOPS 4 | C1: "inside air +50 C or any cell +55 C ... normal to the reduced mode; reached again in the reduced mode, to the heat stage"; the heat stage after BANK-R1 turns off "slots 1 and 2, so bank 1 (the SDR, the camera, the QMX, the wall port), the 5G module (its data is slot 2's), both WiFi link cards, the monitor" |
| Method 507.6 (as L4-E10 transcribed it, fnd/l4e10) | operational checks "near the end of the fifth and tenth cycles", in the cycle's 30 C part; 30 C to 60 C in 2 h |

**What it requires (INFERRED from the texts).** At both margins the kit is to survive and recover; operation to specification
is required only inside the envelope. E3-O runs four hours at +55 C deployed with the monitor and radios on; the one control
action its arrangement records is C1's inside-air shedding, which takes the kit to the heat stage. **Nothing else may turn a
radio off in E3-O**: the radios C1 leaves on (Iridium, the LoRa mesh, APRS, both E72, GNSS) stay on for the four hours. The
first revision's reading that the monitor and radios were only "started" on, and its claim that the acceptance permitted the
hold's extra shedding in E3-O, are withdrawn. E5 requires logging, not the radios, so a step of the kit's controls that turns
radios off may act in E5 and must not act in E3-O. The SGP41 is neither the monitor nor a radio, and E3-O's row does not name
it: its own protective shutdown is inside E3-O's stated configuration (SESSION reading, named exactly for TEST-PLAN's owner:
"switching the battery-bay gas sensor off at its own temperature limit during E3-O"). The lid-closed mode and EMCON change
the configuration and are not used. E3-O is taken to start from a kit stabilised at the chamber's +55 C, as L4-E10 took it;
started straight from E3-S's +71 C soak, the radios would be past +70 C at power-on (a sequence item for TEST-PLAN's owner).

**Which limits apply (the corrected rule, SESSION, [1j]).** Every judged limit names its rating category, read where the
maker prints it: the heading each of 22 rated statements sits under is read before it on its page, with no competing heading
between [0f]. A powered part is judged on its recommended or operating range (the range a sheet's electrical characteristics
hold over counts as operating), whether it must work in the exposure (the CM5, the logging chain, the fans, the radios in
E3-O) or is merely powered. An absolute rating (Absolute Maximum Ratings, limiting values, a junction-and-storage row) is a
stress rating only (PCM2912A SLES230A p.5: "These are stress ratings only, and functional operation of the device at these or
any other conditions beyond those indicated under Recommended Operating Conditions is not implied"; TLV755P p.4 separates its
+150 C absolute junction from its +125 C recommended one): it clears a part only as an exclusion screen. Past its supporting
range (or with none held) and under its absolute rating a part is INCONCLUSIVE, operation or survival not stated, unless its
maker states recovery (the RM520N's extended range, hardware design V1.1 p.19, "without any unrecoverable malfunction ... When
the temperature returns to the normal operating temperature level, the module will meet 3GPP specifications again"). An
unpowered part: its storage range where its maker states one outside its absolute table, else a range it may operate in
(INFERRED to cover it unpowered); an absolute storage row is a screen, and a duration the maker does not state stays open.
**The SGP41**: its gas sensing specifications hold only when it is stored and operated under Table 4's recommended conditions
(section 2.3, p.6): operation -10 to +50 C, storage 5 to 30 C; Table 5's -20 to +55 C operating and -40 to +70 C short-term
storage are absolute ratings (p.7: "Stress levels beyond those listed in Table 5 may cause permanent damage to the device").
The first revision judged it on Table 5's +55 C as its "only powered statement": withdrawn. For the grade rows of the general
screen the category is read from each row's clause and quote (rule printed in [3b]); a junction row whose table the quote does
not name is taken as absolute, the conservative reading. A part through the plate or the wall is bounded by the plate and the
inside air (its rear).

## 3. The thermal state at the margins [2]

| Quantity | Value | Class |
|---|---|---|
| The heat stage after BANK-R1 on shore, plan, into the case | 24.996 W (23.272 W at the pack); as generated 23.345 W; HIGH 50.423 W, not covered (as L4-E10 and LO-01a) | MODELED |
| T-H1's floor: the SGP41's +55 C (Table 5, p.7, an absolute rating; LO-01a's criterion reproduced as stated) at +40 C on shore | 1.6664 W/K; L4-E10's 1.6664 W/K, 70.00 and 75.00 C reproduced. By the corrected rule the bay air at Table 4's +50 C needs 2.709 W/K with the ballasts (a finding for LO-01a's owner and for E3-L's "+55 C" line, section 9) | MAKER, MODELED |
| L4-E8's ballasts at the bound's worst corner | 2.09 W, +1.254 K | MODELED by L4-E8, cited from L4-E9 IF-08 |
| Mixed inside air at the floor, E3-O / E5's dwell | 71.25 / 76.25 C (steady; E3-O's 4 h from a kit at +55 C reaches 69.78 to 70.44 C at 32.53's 10 to 8 kJ/K) | MODELED |
| A charge running on shore | +3.446 W, +2.07 K; E3-O states no charge state, the route counts none (TEST-PLAN's owner records it) | MODELED |
| The plate at the ambient plus, of the rise | 0.465 to 0.725 (W4's films: inside 10 to 25, face 9.5 to 11.5 W/m2K); a PP wall's inner face 0.541 to 0.781 (wall 8 to 10 W/m2K); the floor's 0.588 to 0.898 (3 to 8 W/m2K) | INFERRED |
| The enclosure, lid open with fans (W4: a sensitivity estimate, not a model of the kit) | W4 1.22 (low case) to 2.85 W/K (high case); 32.53 3.0 to 3.3; outer films alone 2.10 W/K (low case) to 3.86 W/K (high case), a cap of the low case's coefficients and areas, not a universal bound | INFERRED |
| The enclosure, lid closed with fans | W4 1.06 to 2.49 W/K; 32.53 1.5 to 2.0 | INFERRED |
| The running module's cooler exhaust over the mixed air | +5.64 K in the heat stage (4.5 W), +2.78 K in the hold (2.0 W idle): the 30 mm fan's 3.7 CFM (Sunon p.1) at 50 % through the heatsink | MAKER, MODELED, ASSUMPTION |
| E3-O as designed | ambient 55.0; mixed 71.25; exhaust 76.89; plate 62.6 to 66.8 C | MODELED, INFERRED |
| E5 as designed | ambient 60.0; mixed 76.25; exhaust 81.89; plate 67.6 to 71.8 C | MODELED, INFERRED |

## 4. The feasibility screen, by the corrected rule [3]

Every fitted line on boards A to E (150 lines of `v2/docs/parts/grade_check.py`'s build, run without writing), the 19 modules
and the 10 lines no grade row covers (read from TI's sheets) are screened; board P and the cells are outside the chamber in
E3-O and E5 (TEST-PLAN's deviation) and stay FEA-008's. **As designed, at E5: 108 NOT REACHED, 9 REACHED, 6 PLACEMENT, 45
INCONCLUSIVE, 7 out of scope, 4 no part or not fitted; at E3-O: 112, 10, 2, 44, 7, 4.** Every screened line carries its
rating's category [3b]: of the 168 screened, 31 recommended, 13 the range the electrical characteristics hold over, 77
operating as printed, 9 a distributor's parametric figure, 5 storage (parts read one by one) and **33 absolute**: the clause
names maximum ratings or limiting values (2N7002, BAT54W, 1N4148W, BC857B, AO3400A and AO3401A, LTC2954, VEML7700, the two
PESD parts, the RA30 PA's case rating; 11), a junction row whose table the quote does not name (BAT46W, SMBJ18A, SMBJ58A,
SMBJ6.0A, the four SMCJ, SS14, USBLC6-2SC6; 10, the conservative reading), a junction-and-storage row (BZT52C12, SMBJ5.0A,
SS2040FL, SI2300DS, the two BSC FETs; 6), a power-dissipation row (SN74LVC08A, SN74LVC86A), a distributor's figure for a TI
power FET (CSD18510Q5B, CSD19532Q5B; the held CSD17577Q5A sheet prints the family's -55 to 150 C as its absolute
junction-and-storage row, p.1), and the two undeclared CSD17577Q5A and CSD17578Q5A (their held sheets' Absolute Maximum
Ratings, p.1). An absolute row cleared at the line is INCONCLUSIVE, not NOT REACHED; the first revision's ordinary NOT REACHED for
CSD17577Q5A's +150 C is withdrawn. Board D's TUSB2046I is judged on the held TI sheet's recommended TA (-40 to +85 C, p.6),
its grade row's +115 C junction being its Absolute Maximum Ratings row. Junction-rated parts carry their own rise: the
converters and LDOs from the model's losses and the makers' thetaJA, judged against their recommended junction (the absolute
one an exclusion screen; TPS62933 on its recommended -40 to +150 C, p.5, not its absolute table's row); signal, protection and
pass parts by stated class bounds (ASSUMPTION: 20 mW at 250 C/W, 0.25 W at 60 C/W, controllers 0.5 W).

The parts read one by one (state: work, powered and required; on, powered; off; limits MAKER; local temperatures MODELED
inside, INFERRED at the face and wall):

| Part | State E3-O / E5 | Limit by the rule, document, page | E3-O local / gap | E5 local / gap | Credible way to close |
|---|---|---|---|---|---|
| RockBLOCK 9704 (device set) | work / on | +70 C operating, the only range (Ground Control spec page) | 71.3 to 76.9 C / 1.3 to 6.9 K over | 76.3 to 81.9 C / 6.3 to 11.9 K over | the air at or under +70 C at its place (the line; out of the exhaust) |
| SA868 (device set) | work / on | +70 C working, the only range (Rev 1.3 p.4) | as above | as above | as above |
| PCM2912A (board D U6) | work / on | +70 C recommended (p.5); +125 C absolute (under bias), a screen | as above | as above (INCONCLUSIVE: powered, not required) | as above; off under the hold in E5 (its +70 C taken to cover it unpowered; the +150 C Tstg is absolute, a screen) |
| Omron G6K-2F-Y (board D K1) | work / on | +70 C ambient operating (p.3) | as above | as above | as above; an +85 C relay for margin (Layer 6) |
| LimeSDR Mini 2.4 (device set) | off / off | +70 C storage (maker's page: commercial grade only) | as above | as above | the air only |
| Pulse H5007NL (board B T1) | on / on | +70 C operating (p.1) | as above | as above | the air; the maker's HX version (-40 to +85 C, p.1; pinout owed) |
| SGP41 (device set) | on / on | +50 C recommended (Table 4, p.6); +55 C absolute (Table 5, p.7), a screen | 21.3 to 26.9 K over (past its absolute +55 C: REACHED) | 26.3 to 31.9 K over (REACHED) | at the margins its own shutdown (unpowered under Table 5's absolute +70 C: INCONCLUSIVE); in the envelope the owner's question (section 8) |
| ATP19 MAIN | on / on | +55 C operating (p.1) | 7.6 to 16.3 K over | 12.6 to 21.3 K over | a sealed pushbutton to +85 C (NKK MBN, p.3) |
| PDi e-paper (device set) | off / off | +60 C operation, the only range (flyer p.1; no storage stated), taken to cover it unpowered | 2.6 to 11.3 K over | 7.6 to 16.3 K over | its maker's storage range (drafted); no refresh past it |
| ATP16 PI, TEST | on / on | +70 C operating (p.1) | 0.0 to 1.3 K over | 0.0 to 6.3 K over | the air; NKK MBN |
| Bulgin PXP4043/C | off / off | +70 C (its sheet p.1; the 4000 series sheet p.3: -40 to +80 C) | 0.0 to 1.3 K over | 0.0 to 6.3 K over | the air; Bulgin's answer (drafted) |
| AW7915-AED x2, RM520N-GL (device set) | off / off | +90 C storage (p.3; p.19) | 13.1 K inside | 8.1 K inside | none needed |
| Xenarc 709GNK (device set) | off / off | +80 C storage (p.4) | 8.8 K inside | 3.8 K inside | none needed |
| CM5 (device set) | work / work | +85 C operating (p.28) | 8.1 K inside | 3.1 K inside | none needed |
| Floyd Bell sounder | off / off | +85 C storage (p.1) | 13.8 K inside | 8.8 K inside | muted unless SOS |
| NVMe (not picked) | on / on | the pick's line, a wide grade -40 to +85 C (Cervoz p.10) | 8.1 K inside | 3.1 K inside | the pick |
| TLV75533 board E U13 and board C U5 | work / work | +125 C recommended junction (TLV755P p.4); +150 C absolute, a screen | REACHED | REACHED | the regulator changed (5c) |

Connectors rated +80 C (the M.2 sockets, board B's USB-C service ports) are over only in the exhaust at E5 (PLACEMENT). The
board E finding of the first revision stands (3d): U13 on a rail its generator declares at 0.35 A typical and 0.60 A peak is
past its recommended junction at any local air above -12.5 C (0.595 W, +137.5 K) and its peak past the part's 500 mA; board
C's U5 is declared 0.72 A peak. Even at the model's plan load U13 passes its recommended junction at both margins.

## 5. Three complete approaches compared [4]

Common to all three, because the air cannot be cooled below the ambient without a cooler (and a cooler in the sealed case
returns its input to the air, L4-E10's corrected balance): the SGP41's own shutdown at the margins and its in-envelope
function (the owner's question, section 8); the MAIN, PI and TEST pushbuttons to a +85 C part; PDi's storage statement; the two
regulators; the +70 C parts out of the running cooler's exhaust; the fans, the other lines with no range held and the lines
cleared only by an absolute rating.

| | (a) heat path and enclosure | (b) wider-rated parts | (c) SELECTED: E3-O as stated, the hold in E5 only |
|---|---|---|---|
| What it is | the heat stage at both margins, the radios on at both; the inside air lowered by the enclosure (inside fins on the plate, mixing), or the +70 C modules coupled to the plate | every colliding part replaced by one rated to +85 C; the mode and the enclosure unchanged | E3-O: the heat stage with every radio C1 leaves on; E5: beyond the heat stage the charge held, the module idled, board D, the PA rail, RockBLOCK, LoRa, both E72 and Geiger off |
| Heat (MODELED) | 24.996 W at both | 24.996 W at both | 24.996 W in E3-O; 19.497 W in E5 (18.152 W at the pack) |
| Enclosure line (MODELED) | 2.709 W/K (3.010 at 1 K, 3.386 at 2 K); E3-O alone 1.806 W/K | the floor, 1.6664 W/K | **2.159 W/K**, set by E5 (2.399 at 1 K, 2.698 at 2 K; 2.443 with the module at 4.5 W; 4.304 at HIGH); E3-O alone 1.806 W/K |
| Against the physics | over the low case's cap (2.10), under W4's high case (2.85): CONDITIONAL on T-H1 | the inside air at 76.25 C (81.89 in the exhaust) leaves +85 C parts 3.1 to 8.8 K | 0.058 W/K over the low case's cap, inside W4's range and under 32.53's: CONDITIONAL on T-H1 |
| Configuration | E3-O and E5 as stated | as stated | E3-O as stated; E5's radios off (E5 requires logging only); a trigger window that exists only with a placed or calibrated reference |
| Changes | mechanical | five device-set re-picks (the owner's), four with no candidate held | firmware on existing enables (RB_SW_EN, LORA_ON, ZB_ON, GEIGER_EN, board D and the PA as H1 does); the hold's reference |
| Evidence owed | T-H1 at 2.709 W/K or more | makers' sheets for four device-set parts | T-H1 at 2.159 W/K or more; the reference's offset to +-0.899099 K |
| Verdict | CONDITIONAL; not selected (0.55 W/K over (c)); applies alone if T-H1 reads at or over 2.709 W/K | not selectable by the session | SELECTED, CONDITIONAL |

Per colliding part [4f]: (a) and (c) CONDITIONAL for the +70 C class, the ATP16 and the USB-C; INCONCLUSIVE for the SGP41
(off by its own shutdown, the air clears only Table 5's absolute +70 C short-term storage: its survival is Sensirion's to
state) and for the e-paper (no storage range held); REJECTED for the ATP19 (in circuit at +55 C, under the ambient). (b)
CLOSES for the ATP19, the ATP16, the H5007NL and the USB-C; OUTSIDE AUTHORITY for the five device-set parts; INCONCLUSIVE for
the relay and the codec. No part at the margins has every route rejected.

## 6. The selection: (c), with its margins [5]

**E3-O.** The heat stage with every radio C1 leaves on, no hold: at the line its mixed air is **67.55 C** (73.19 C in the
running cooler's exhaust); the RockBLOCK, the SA868 chain and the H5007NL work 2.45 K inside +70 C at the mixed air, so they
must sit out of the exhaust (Layer 9). E3-O alone would hold from 1.806 W/K.

**E5.** The hold: its heat 19.497 W (as board B is generated, the 5G socket's supply dropped too, 19.497 W); at the line the
mixed air settles at **70.00 C** with the radios off, inside the +70 C class's only statements at 0 K; 2.78 K more in the idle
module's exhaust (placement again).

**The hold's trigger window [4d] (SESSION, PROVISIONAL).** Window 2.45 K of mixed air between E3-O's steady 67.55 C and E5's
need at 70.00 C; less the reference's error twice (TMP117, +-0.2 C to 100 C, MAKER p.1) and 0.254167 K of lag (E5's chamber at
15.0 K/h times a 61 s reading and response, ASSUMPTION), the reference may sit at most **+-0.899099 K** from the air at the +70 C
parts (the first revision's rounded +-0.90 K exceeded it). Across the exhaust's 0 to 5.64 K spread the window is -3.84 K: **it does not exist** with the TMP117 left where it is;
it would need 3.111 W/K. With a reference placed in the mixed air near those parts, or the TMP117's offset calibrated at T-H1
to +-0.899099 K, the trigger sits at the window's middle, **68.65 C** of mixed air plus the calibrated offset, restored 5 K under it
after 30 minutes. The window widens with the conductance (4.17 K at 2.5 W/K; 5.00 K at 2.709 W/K, where no hold is needed).
Inside the envelope the air at the line is 52.55 C, far under it. Actions: the charger's charge-inhibit bit and board D and the
PA rail off through board A's expanders (as H1 does); the RockBLOCK, the LoRa module and both E72 off through their software
enables (U503 RB_SW_EN, U504 LORA_ON, U505 ZB_ON); the Geiger module off (U16, GEIGER_EN); the running module idled, its
logging kept; an SOS raised meanwhile is queued as under EMCON (D-10) and the operator told.

**The SGP41 [5d].** CHO-001 picks it for the battery bay; REQ-042 makes its VOC channel part of the pack's shutdown;
CFL-002's acceptance: "The SGP41 is fitted where the battery bay's air is sampled, or an owner ruling drops it".

*Its shutdown and power-on (SESSION).* The reference is a TMP117 on the SGP41's carrier (+-0.15 C maximum from -40 to 70 C,
MAKER, TMP117 p.1); board E's BME688 is not used, its +-0.5 C sitting in Table 10's Typ column with no maximum (p.14). The
TMP117 sits within 0.5 K of the SGP41 with its own heating (ASSUMPTION, a placement rule measured at the bench) and is read
every second with 0.254167 K of lag (E5's 15 K/h times 61 s, ASSUMPTION). Power off at a reading of 55 - 0.15 - 0.5 - 0.254167
= 54.095833 C, set at **54.0 C** (rounded down): the SGP41 is then at most 54.904167 C, 0.095833 K under Table 5's absolute
+55 C. Power on, and its output used for REQ-042, at a reading at or under 50 - 0.15 - 0.5 - 0.254167 = 49.095833 C, set at
**49.0 C**: at most 49.904167 C while its output is used. Between the two it stays powered and its output is logged as outside
Table 4; it is off at every start until a reading at or under 49.0 C, so E3-O, which starts from a kit at +55 C, never powers
it.

*Its in-envelope function: the one engineering route, bounded first.* With the power-on reading at 49.0 C and 0.5 K kept for a
bounded restart (SESSION), its location must stay at or under 48.35 C at +40 C ambient in every in-envelope state. The binding
state is the heat stage, 27.086 W with the ballasts, lid open or closed (E3-L runs it at +40 C with the lid closed); C1 holds
the other states' air at its +50 C on board B's TMP117 plus 0.2 C and the lag, 50.454 C. The places that still sample the bay
air (fractions INFERRED from W4's films, temperatures MODELED at +40 C):

| Location | Fraction of the air's rise | Needs | Lid open at the line (2.159 W/K) | Lid closed at 32.53's 2.0 / 1.5 W/K | C1-held states |
|---|---|---|---|---|---|
| the bay air where board E's U17 sits (as designed) | 1.000 | 3.244 W/K | 52.55 C | 53.54 / 58.06 C | 50.45 C |
| the east wall's inner skin in the pack pocket | 0.541 to 0.781 | 2.535 W/K | 49.80 C | 50.58 / 54.11 C | 48.17 C |
| the floor's inner skin under the pack | 0.588 to 0.898 | 2.912 W/K | 51.27 C | 52.16 / 56.21 C | 49.39 C |

The coolest is the east wall's inner skin (the pack keeps 7.38 mm to that wall at the worst, CASE-MARGINS M4b): a carrier
bonded to the skin, the SGP41 sampling the bay air through a diffusion port whose response is owed to the bench. It needs
**2.535 W/K** with the lid open, inside W4's 2.85 and under 32.53's 3.0 to 3.3, and the same with the lid closed, over 32.53's
1.5 to 2.0 and over W4's high case 2.49: **not held with the lid closed on any conductance the record carries.** Where it
holds, the other states are met: the C1-held states at 48.17 C (0.18 K to spare); a warm start from the envelope's +45 C
storage (powered at once); recovery from E3-O's end (63.35 C at the skin at 2.535 W/K) to a restart in 2.98 to 3.73 h at +40 C
(32.53's 8 to 10 kJ/K). A cooled mount is not a route: a cooler in the sealed case returns its input to the air, and one
through the wall is a new penetration and a new subsystem. **Storage:** the envelope stores the kit at -20 to +45 C for three
months (-20 to +25 C for a year), outside Table 4's 5 to 30 C, and an unpowered kit's inside sits at the ambient, so no
location changes it. **Result: no location holds the SGP41 inside its maker's conditions in the envelope.** CHO-001 binds the
part, so the owner's question is raised (section 8). The first revision's claim that its function was kept at the line (52.55 C
bay air, 0.20 K to spare) rested on Table 5's absolute +55 C and the BME688's typical figure, and is withdrawn.

*At the margins* it is off: at the line, in the bay air 67.55 C (E3-O) and 70.00 C (E5), at the skin 64.80 and 67.81 C, under
Table 5's +70 C short-term storage, an absolute rating: INCONCLUSIVE, Sensirion's duration and recovery owed (drafted, with the
storage and the +50 to +55 C questions); in a cooler's exhaust it would pass it (72.78 C in E5), so it stays out of it. The
circuit for the shutdown (board E, owed to its generator owner, no draft: the generator needs KiCad's libraries): a TPS22810
load switch (the part board E already uses for the Geiger) feeding a new +3V3_SGP from +3V3_E6, enabled from U10's free GPIO20
(QFN pin 31) with a 100k pull-down; the SGP41's VDDH and R57's input on +3V3_SGP; its SDA and SCL moved to GPIO21 and GPIO22
(pins 32 and 34) with 4.7k pull-ups to +3V3_SGP, so that with the switch off no live bus feeds it through its pins (the firmware
runs that bus by PIO and floats it before switching off); the TMP117 beside it on board E's always-powered sensor bus at an
address free there. Whichever option the owner takes, the shutdown stays for the margins unless the part goes (option B) or
is replaced by one whose range covers them (option A).

**The regulators [5c].** Recommended junction +125 C (TLV755P p.4): board E's U13 at the model's plan 0.258 W reaches 127.1 C
(E3-O) and 129.5 C (E5) in SOT-23-5 (231.1 C/W) and 93.4 and 95.8 C in the DRV package (100.2 C/W, the same sheet); at its
rail's declared 0.35 A neither package holds (the DRV part takes at most 0.323 A at E5's air), so a buck, or the rail's load
re-derived. Board C's U5 at its declared typical: 126.1 and 128.5 C in DBV, 92.9 and 95.4 C in DRV. Owed to boards E and C's
generator owners (the DRV land is the WSON-6 board E already uses).

**The pushbuttons.** MAIN (ATP19, +55 C) and PI, TEST (ATP16, +70 C) to a sealed pushbutton whose maker states +85 C: NKK MBN
(IP67, -30 to +85 C, p.3, held), its 12 mm bushing, terminals and cutout owed (Layer 6, 7, 8). The ATP19's IK10 rating is not
matched by the MBN's sheet: a named consequence. Until picked, the ATP19 stays REACHED.

**At the line, every line [5b]:** 114 NOT REACHED at each margin; 7 PLACEMENT (the +70 C class and the SGP41 at the mixed air,
over only in an exhaust; the SGP41 then INCONCLUSIVE on its absolute short-term storage); 3 REACHED (the ATP19 and the e-paper,
conditional future closures by the pick and PDi's statement, and the TLV75533 line, closed by the regulator change); 44
INCONCLUSIVE (11 with no range held, 33 cleared only by an absolute rating [7d]).

## 7. What stays CONDITIONAL, and what could overturn it

- **T-H1 lid open with fans at or over 2.159 W/K** (E5 with the hold); 2.709 W/K with no hold; 1.806 W/K for E3-O alone. The line
  lies over the low case's outer-film cap (2.10 W/K): at W4's low coefficients no inside fin reaches it. If T-H1 reads between
  1.806 and 2.159 W/K, E3-O still holds and E5 needs the fallback: the radio modules and the LimeSDR coupled to the plate (E5
  plate 66.0 to 69.4 C under the hold at the floor, 0.61 K inside +70 C, INFERRED), the HX magnetics, Bulgin's +80 C; the
  SGP41 in the bay air (72.95 C) is then past Table 5's absolute +70 C short-term storage, which the owner's question of section
  8 covers (option A's BME688 is electrically operable to +85 C).
- The hold's reference placed in the mixed air or calibrated to +-0.899099 K, and the hold forced at room temperature.
- The SGP41's shutdown at the margins (the TMP117 on its carrier within 0.5 K, the switch, the bus, Sensirion's duration) and
  the owner's answer for its in-envelope function; the pushbuttons; the regulators; PDi's statement; the placement out of the
  exhaust.
- **LO-01a's criterion and E3-L's line read Table 5's absolute +55 C.** By the corrected rule the SGP41's specified operation
  ends at Table 4's +50 C: the bay air there needs 2.709 W/K with the ballasts (finding for LO-01a's owner and TEST-PLAN's owner;
  with option A or B the criterion moves to the replacing part or goes).
- **The 33 lines cleared only by an absolute rating** (the least clearance 11.8 K, LTC2954): INCONCLUSIVE until a maker's
  statement supporting operation or the parts discipline's derating rule covers each.
- **The fans** (D-18): they carry the inside film every conductance here assumes; unrated, they are architecture-level (a fan
  that stops at the margin takes the enclosure to W4's fans-off 0.77 to 1.57 W/K and every margin with it).
- The plan heat: the line is 2.443 W/K with the module at its typical 4.5 W and 4.304 W/K at HIGH; the bench's E3-O and E5
  power readings replace the plan figures. The class bounds of the screen.

## 8. The owner-question test [6]

The question is asked only after the engineering routes are assessed (sections 5 to 7), and not only in one named case.

**At the margins** no part has every route rejected or outside authority on held evidence: the ATP19 closes by the session's
pick; the +70 C class by the air at the line and placement; the SGP41 by its own shutdown (its survival under Table 5's
absolute short-term storage is Sensirion's to state); the e-paper's route rests on a statement PDi has not published in a held
document, a component limitation, not a requirements conflict.

**Inside the envelope: the SGP41. RAISED.** No location holds it inside its maker's conditions (section 6: the lid-closed line
of 2.535 W/K lies over every conductance the record carries, and the envelope's storage lies outside Table 4), and CHO-001 binds
the part. The conflict is CFL-002's: CHO-001's SGP41 in the battery bay against REQ-042's VOC channel under D-02a's "operate to
specification inside the envelope". **Owner question: which of these three?**

- **A. A BME688-class gas sensor in the bay in its place** (Bosch: gas sensing -40 to +85 C, p.8, "The sensors are electrically
  operable within this range. Actual performance may vary."; its IAQ figures tested at 5 to 40 C, p.9; storage -45 to +85 C, an
  absolute rating, p.15). Consequence: powered with no shutdown across the envelope and both margins (bay air 52.55 C at +40 C,
  67.55 and 70.00 C at the line); REQ-042's VOC level set from the BME688's own baseline instead of "the SGP41's own clean-air
  baseline as its datasheet defines the VOC index" (its acceptance restated); its gas performance over +40 C and after storage
  owed to Bosch or the bench; a second BME688 takes I2C 0x77 on board E, which the deferred outside pod's BME688 then cannot
  share; CHO-001's line and CFL-002 restated.
- **B. The battery-bay VOC channel dropped.** Consequence: REQ-042 restated to water on the floor and hydrogen (S-49's part);
  CHO-001's line and CFL-002 restated; U17 and its switch off board E; a venting cell is then seen by the hydrogen channel and
  the cells' own temperatures only.
- **C. The SGP41 kept, its channel reported as not covered** (REQ-042: "a state outside a sensing part's published range is
  reported as not covered by that channel, never assumed") while its reference reads over 49.0 C (on the east wall's skin: lid
  closed above about +34.24 to +37.77 C ambient at 32.53's 1.5 to 2.0 W/K, lid open above about +38.55 C at the line) and after
  storage outside 5 to 30 C until Sensirion states otherwise. Consequence: a restriction of the VOC channel inside the
  envelope, which D-02a does not grant today; the location's carrier and T-H1's lid-closed reading set where it starts.

The session's recommendation: **A**, the one option that keeps a powered VOC channel across the envelope and the margins with
a part the kit already carries. The radios' route (section 6) does not depend on the answer.

**Later, on T-H1's reading** (escalation is not limited to the case above): if T-H1 reads under 2.159 W/K lid open, E5 fails
for the +70 C class unless the plate coupling of section 7 holds them (at 2.000 W/K E3-O's mixed air is 68.543 C, under +70 C,
while E5's under the hold is 70.793 C, over it); under 1.806 W/K E3-O fails as well. Each case is assessed against the routes
then left (the plate coupling's evidence, wider-rated parts) before any question; what would then go to the owner is a
device-set re-pick (CHO-001) or a stated deviation of E3-O's configuration (four hours at +55 C with the hold's shedding,
CM5 not shut down and logging, no damage, recovery kept), each reported as such.

## 9. Downstream items (owner by layer; acceptance)

| Owner | Item | Acceptance |
|---|---|---|
| Owner | the SGP41 question (section 8: A, B or C; CFL-002) | a ruling recorded against CHO-001, REQ-042 and CFL-002 |
| Layer 4 coordinator | U-02's line on T-H1 (lid open, fans: 2.159 W/K; 2.709 with no hold; 1.806 for E3-O) beside LO-01a's; LO-01a's floor with L4-E8's ballasts is 1.8058 W/K (finding 1), and its criterion reads Table 5's absolute +55 C (2.709 W/K at Table 4's +50 C); L4-E10's conditioned corner moves with the line; the owner's SGP41 question carried | the gate's IF-11 and U-02 rows restated on this record |
| Layer 2 and 5 integrators, firmware owner | the hold as a mode for E5's case beyond the envelope (CONOPS 4, HW-FW-CONTRACT): trigger at the window's middle with the calibrated offset, restore, actions, enables, the SOS queue; the SGP41's own shutdown (off at a TMP117 reading of 54.0 C, on and used at or under 49.0 C, off at every start until then) | a forced hold and a forced SGP41 shutdown at room temperature; E3-O and E5 |
| TEST-PLAN's owner | E3-O unchanged; E5's arrangement records the hold beside C1; E3-O's record names the SGP41's own shutdown; E3-O starts from a kit stabilised at +55 C; the pack's charge state at E3-O's start; a forced-hold row like P15; T-H1 reports the plate, wall and floor fractions in both lid states and the hold reference's offset; E3-L's SGP41 line judged on its own temperature against Table 4's +50 C (or the replacing part's range), not the inside air against Table 5's absolute +55 C | the plan's revision |
| Layer 6 components | MAIN, PI, TEST pushbuttons (NKK MBN class, +85 C); the H5007NL's HX version (pinout); an +85 C T/R relay (margin); Bulgin's answer; the NVMe wide grade; the lines with no range held (below); the 33 lines cleared only by an absolute rating [7d] | each maker's range at or over its local temperature at the line (section 6); for the 33, a maker's statement supporting operation or the parts discipline's derating rule |
| Layer 6, architecture-level | **the IP68 fans (D-18)**: a maker's operating range reaching the mixed air at the line (70.0 C in E5) with margin | a held sheet; T-H1 with the picked fans |
| Layer 6, downstream | the CR2032 cell and its holder, the QMX (in the lid, at the ambient; the owner's device set, an owner item only if its maker states less than the ambient), the header modules, the panel LEDs, the headset jacks, J_HDMI, the pin headers, the fuse holders, the pre-charge pin: each range read | a held sheet per line |
| Layer 7 mechanical | the enclosure to T-H1's 2.159 W/K (inside fins on the plate, mixer flow); the fallback plate coupling; the MBN cutouts | T-H1 |
| Layer 8, board E's generator owner | the SGP41's switch and bus and the TMP117 beside it (or option A's or B's change); U13: a buck, or a DRV-package LDO with the rail's load re-derived under 0.323 A | board E's suite; U13 under +125 C junction at the line's air |
| Layer 8, board C's generator owner | the pushbuttons; U5 to the DRV package; U5's declared 0.72 A peak against 500 mA | board C's suite |
| Layer 9 pre-layout | the +70 C parts and the SGP41 out of the running cooler's exhaust; the TMP117 within 0.5 K of the SGP41; the hold's reference in the mixed air near the +70 C parts; the class bounds replaced | the placement review |
| Prototype bench | T-H1 in both lid states with the plate, wall and reference thermocouples; E3-O and E5 with thermocouples on the RockBLOCK, SA868, LimeSDR, H5007NL, SGP41, e-paper, plate and the hold's reference | each TEST-PLAN pass line; section 3's model replaced by the measured conductance |
| Owner (outside contacts) | send PDi's and Sensirion's requests (the route needs them; Sensirion's now asks about storage at -20 to +45 C and operation at +50 to +55 C as well); Ground Control's, NiceRF's and Bulgin's are drafted for the fallback | the answers filed |

## 10. Decisions taken by the session (authority: SESSION, under the owner's standing rule of 26 September 2026)

| Decision | Why the session's | Reversed by |
|---|---|---|
| The corrected rule of section 2 (every limit with its category; recommended or operating ranges for powered parts; absolute ratings only as exclusion screens, INCONCLUSIVE when cleared; storage, else a range it may operate in, for unpowered parts) | the makers' own words on their absolute ratings; the checks' B2 | a maker's statement of recovery or of operation, or the owner's reading of D-02a |
| A grade row's category read from its clause and quote; a junction row whose table the quote does not name taken as absolute | the conservative reading of an unnamed table; the held CSD17577Q5A sheet for the TI FETs' distributor figures | each maker's sheet read at its table |
| E3-O kept exactly as stated; the hold only in E5 | E3-O names the radios on; E5 requires logging only | the owner, if he approved a deviation (section 8) |
| The SGP41's own shutdown is inside E3-O's configuration | the row names the monitor and radios, not the sensor; no function is required during the margin | TEST-PLAN's owner reading the row otherwise |
| (c) selected; (a) not selected; (b) not taken | (c) needs the least conductance within the session's authority; (a) needs 0.55 W/K more; (b) is the owner's | T-H1's reading, or the owner's re-picks |
| The hold's trigger at the window's middle, restore 5 K under (PROVISIONAL); the reference's offset bound +-0.899099 K | the window's own arithmetic | the bench (T-H1, the forced hold) |
| The SGP41's thresholds 54.0 C off and 49.0 C on and used, on a TMP117 on its carrier | Table 5's absolute +55 C and Table 4's +50 C less the printed maximum error, the gradient and the lag, rounded down | the bench |
| 0.5 K kept under the power-on reading inside the envelope (48.35 C at the location) | a restart in a bounded time | the bench |
| The SGP41's in-envelope function raised to the owner | no location holds it and CHO-001 binds the part (the owner's rule: a question only when the routes are exhausted and the choice is his) | the owner's ruling |
| The regulators changed (DRV or a buck) | an engineering change of a part within the session's authority | the generator owners |
| The e-paper's gap left to PDi's statement, not escalated | a missing statement is a component limitation (the owner's rule) | PDi's answer |
| No generator draft | the changes need footprints and a KiCad run the runner cannot do; a specification is given | the generator owners |

## 11. Files

`l4e12_thermal.py` and `.out`; `fetch_held_back.py` (TI's TLV755P sheet into the ignored `v2/vendor/ti/held/`, sha256
44ac688d7e51f852...); `clarification/` (PDi, Sensirion, Ground Control, NiceRF, Bulgin; drafts for the owner to send);
`checks/astra-check-l4e12-1.md` and `checks/astra-check-l4e12-2.md`; `T-H1-PROCEDURE-DRAFT.md` (sections 13 and 16); `README.md`.
`fetch_held_back.py` also fetches Rittal's page that section 16 cites into the ignored `v2/vendor/rittal/held/` (sha256
fd3a31d31c88adb4...). The tests: `env -C v2/ecad/tools/tests python3 run.py test_l4e12
test_public_hygiene`. No generator, BOM, registry, interface or Layer 3 file is changed.

## 12. The two checks, and what each item changed

| Item | Change, and its effect on the numbers, margins or verdict |
|---|---|
| B1 (configuration without authority) | withdrawn: the "started with" reading and the claim that the acceptance permitted extra shedding in E3-O. E3-O now runs as stated (every radio C1 leaves on stays on); its heat is the heat stage's 27.086 W with the ballasts, held at or under +70 C from 1.806 W/K (the coordinator's 1.81 confirmed); the hold acts in E5 only, inside a trigger window bounded at 2.45 K (+-0.899099 K for the reference, after the recheck) that does not exist with the TMP117 across the exhaust's spread. Binding line unchanged at 2.159 W/K (E5), now CONDITIONAL on the reference as well. Material |
| B2 (the rating rule) | absolute maxima are exclusion screens; powered parts judged on their operating or recommended ranges; survival past them INCONCLUSIVE unless stated (the RM520N's recovery used with its conditions). Re-run: the PCM2912A REACHED in E3-O (recommended +70 C), INCONCLUSIVE at E5 as designed; board E's U13 and board C's U5 REACHED (recommended +125 C junction) and added to the route as a regulator change. Material |
| B3 (the SGP41's transition) | its shutdown made independent of the hold: off at 53.75 C on a reference beside it, with the error, gradient and lag; off at every start until it reads 50 C, so never powered in E3-O; its in-envelope function kept at the line (0.20 K); its unpowered storage CONDITIONAL on Sensirion's duration (drafted). Material; its reference, thresholds and in-envelope claim superseded by the recheck rows below |
| The eleven unrated lines | each named as an evidence obligation with its owner; the fans architecture-level (section 9) |
| Minor: 2.709 W/K against W4 | corrected: over the low case's cap, under the high case's 2.85 W/K; (a) is CONDITIONAL, not rejected by physics |
| Minor: the ATP19 and the e-paper | stated as conditional future closures, not closed |
| Recheck B2 (rating provenance) | every judged limit names its category; the headings of 22 rated statements are read on their pages; the SGP41 is judged on Table 4's recommended +50 C, Table 5's +55 C an absolute screen; 33 lines cleared only by an absolute rating are INCONCLUSIVE, CSD17577Q5A's +150 C among them (it read NOT REACHED); TPS62933 judged on its recommended row, TUSB2046I on its recommended TA; P11 extended to every screened row, every part read one by one, the junction table and the SGP41's key. Effect: as designed 108 and 112 NOT REACHED (was 141 and 145), 45 and 44 INCONCLUSIVE (was 12 and 11); at the line 114 NOT REACHED and 44 INCONCLUSIVE at each margin; the route's line unchanged at 2.159 W/K. Material |
| Recheck B3 (the protection bound) | the reference is a TMP117 on the SGP41's carrier with a printed +-0.15 C maximum (the BME688's +-0.5 C is typical, p.14); off at a reading of 54.0 C (54.095833 C exact, rounded down; the SGP41 at most 54.904167 C), on and used at or under 49.0 C (49.095833 C exact; at most 49.904167 C). Material |
| Recheck B3 (in-envelope sensing and recovery) | the claim that its function was kept at the line withdrawn; the one engineering route bounded first: its location at or under 48.35 C at +40 C in every state; the coolest place, the east wall's skin, needs 2.535 W/K, inside the lid-open range and over every lid-closed conductance the record carries; warm start and recovery met where it holds (2.98 to 3.73 h); the envelope's storage lies outside Table 4's 5 to 30 C. No location holds: one owner question (section 8: A, B or C, A recommended). Material |
| Recheck minor: the exclusive owner condition | replaced by an escalation after the routes are assessed (section 8), with the recheck's example reproduced: at 2.000 W/K E3-O's air is 68.543 C and E5's under the hold 70.793 C |
| Recheck minor: rounding | the hold's offset allowance printed +-0.899099 K; the SGP41's thresholds printed exact and rounded down (54.0 and 49.0 C) |

## 13. Update: U-02 in depth (the dependency round of 2 October 2026) [8]

The owner's point, relayed by the coordinator: "explain what supports the 2.159 W/K threshold, the enclosure/fan
configuration it assumes, and where fan power enters the energy budget. Name who would perform T-H1 and the practical test
method. Establish what a failed measurement would change and whether a feasible fallback exists." The branch was brought to
set 26's candidate `aa897e38` first (a fast-forward); the record reproduces there unchanged before this section. L4-E8's
ballasts and L4-E10's floor and air are now read from their pinned outputs (`records/l4e8/ripple_dense.out`,
`records/l4e10/l4e10_cell_thermal.out`), and E5's cycle from the tree's transcription of Method 507.6
(`v2/vendor/standards/mil-std-810h-method-507-6.md`); 69 inputs are pinned.

### 13.1 What supports the line [8a]

Each line is the heat into the sealed case over the room between the ambient and the limit of the parts the air must hold,
G = Q / (T_limit - T_ambient), at 0 K of margin:

| Line | Heat Q | Ambient | Limit | G | per +-1 W | per +-1 K of limit (ambient -+1 K) |
|---|---|---|---|---|---|---|
| E5 under the hold | 21.587 W (19.497 W + the ballasts' 2.09 W) | 60 C | +70 C | **2.159 W/K** | 0.100 W/K: 2.059 to 2.259 | -0.216 W/K: 1.962 to 2.399 |
| E3-O, the heat stage | 27.086 W (24.996 W + 2.09 W) | 55 C | +70 C | 1.806 W/K | 0.067 W/K: 1.739 to 1.872 | -0.120 W/K: 1.693 to 1.935 |
| E5 with no hold | 27.086 W | 60 C | +70 C | 2.709 W/K | 0.100 W/K: 2.609 to 2.809 | -0.271 W/K: 2.462 to 3.010 |

- **E5's heat, built up (MODELED, plan):** 14.671 W at the load pins, 3.445 W in the converters, 0.036 W in the
  distribution: 18.152 W at the pack; on shore the front end's and the charger's loss adds 1.345 W: 19.497 W into the case;
  L4-E8's ballasts at the bound's worst corner add 2.09 W (MODELED by L4-E8): 21.587 W. Its largest loads: the running
  module idle 2.000 W, panel board C 1.500 W, the switch chip's 1.2 V 1.452 W, the two mixer fans 1.440 W, the device rail's
  logic 1.300 W, the three supervisors 1.297 W (the `.out` lists all nineteen with their battery-side shares).
- **The hold's action:** the running module 4.500 to 2.000 W, the PA 0.900, board D 0.600, the LoRa module 0.300, the
  Geiger module 0.300, the RockBLOCK 0.060 and both E72 0.048 W to nothing: 24.996 W to 19.497 W into the case.
- **The ambient** is E5's dwell, 60 C from 0200 to 0800 (6 h) of Table 507.6-IX (TEST-PLAN E5, read). **The limit** is the
  +70 C class the hold leaves in the air, each at its limit by the rule of section 2: the RockBLOCK, the SA868, the G6K and
  the PCM2912A (off; their operating or recommended +70 C taken to cover them unpowered), the LimeSDR (off; its +70 C
  storage), the H5007NL (on, +70 C operating), the ATP16 and the PXP4043/C (at the plate to the air). **The margin** is 0 K at
  the line; 1 K needs 2.399 W/K, 2 K 2.698 W/K.
- **Classes:** the heat MODELED (the model's rows carry their own tiers: S a sheet's figure, R representative, D declared, T a
  placeholder); the ballasts MODELED by L4-E8; the ambient and the limits as read (TEST-PLAN, Method 507.6, the makers'
  sheets); the line MODELED, and as a requirement on T-H1 CONDITIONAL. E3-O's 1.806 W/K equals LO-01a's floor with the
  ballasts (1.8058 W/K) only because both rooms are 15 K.

### 13.2 The configuration it assumes [8b]

- **Lid open, deployed, on shore** (TEST-PLAN E3-O and E5): every conductance is W4's lid-open value with the fans, or a T-H1
  reading in that state.
- **The fans (32.53 item 2, REQ-043):** five, three cooler fans (one per module's cooler on its slot's header) and two mixer
  fans under the plate on board E's sensor controller, speed set from the inside climate reading. In both margins three run:
  slot 3's cooler fan (0.51 W) and the two mixers (1.44 W). **D-18 is OPEN, no fan is picked.** The model's representatives:
  Sunon MF30060V2 (30 mm, 0.36 W, 3.7 CFM; not IP68) for the coolers and GF60151B9 to B6 (60 mm, IP68, 0.39 to 1.50 W, 10.6
  to 21.3 CFM) for the mixers; READY-TO-ACT names Same Sky's CFM-6025BG68 for the mixers. **No held sheet gives a fan's
  operating temperature**; REQ-043's acceptance asks for "a published operating range covering -20 C to the inside-air bar
  part_temps.py computes from pcb_envelope.yaml" (section 7's ARCHITECTURE line).
- **The heat path under the no-vent ruling:** the 3 mm aluminium plate (0.0912 m2) and the PP walls (0.137 to 0.220 m2) and
  floor (0.096 to 0.135 m2) only. W4's split, lid open with the fans: low case 0.778 W/K through the walls and floor and
  0.444 W/K through the plate, high case 2.131 and 0.718 W/K. The mixers stir the air under the plate across the boards and
  onto the plate and walls: W4's inside film is 10 to 25 W/m2K with them and 4 to 6 W/m2K without.
- **The hold's reference:** today board B's TMP117 under the coolers (CONOPS 4c), in the coolers' air; section 6 requires it in
  the mixed air by the +70 C parts or calibrated to +-0.899099 K.
- **If the fans stop** (W4 lid open, fans off: 0.77 to 1.57 W/K; 32.53 says about 2.1 W/K still): without the fans' own
  heat (2.16 W into the case), E5's mixed air is 72.38 to 85.36 C (it would need 1.943 W/K to stay at +70 C) and E3-O's 70.89 to 87.56 C, so the
  +70 C class passes its limit on W4's still values. Parts coupled to the plate (F4 below) stay at the plate: at most 69.82 C
  in E5 and 67.60 C in E3-O with the still film's plate fraction (0.258 to 0.387). One mixer of two stopping lies between the
  two states (no model). Slot 3's cooler fan stopping leaves the module to its own throttling (CM5 4.4, below 85 C), which
  E3-O's pass line allows. The controls act on the measured air whatever the cause; a stopped fan is seen by its tachometer
  only where the picked fan has one.

### 13.3 The fans in the energy budget [8c]

**They are counted, and not in the undocumented share.** `records/rv-pwr/pwr_budget.py` carries "cooler fan slot 1..3" in
every state where its slot runs and "two mixer fans" in every state, tier R (representatives, D-18 open, the mixers' PWM duty
TBD); `records/l3batt/load_trace.out` lists them in the 42.8 W profile (the mixers 1.45 W, the coolers 0.57, 0.56 and 0.55 W,
tier R; its tiers S 16.8, R 11.3, D 6.3, T 8.4 W); the replay carries that profile ("PS-IDLE-SPEC 42.8 W at the pack
terminals over its 39 loads", `records/l4e/l4e_replay.out`), and L4-E9's endurance the same 42.8 W (`l4e9_power_path.out`
at `aa897e38`, cited and not pinned, because that output quotes this record). The 8.40 W with no document are the Xenarc
(6.03 W), WiFi link card 2 in standby (1.30 W) and the PA (1.07 W); no fan is among them. The fans' heat is inside the case
and inside every heat figure of 13.1.

| Mode (MODELED, plan) | Fans running | Fans at the pack | Of the mode | Per day | At the loads, low .. plan .. high |
|---|---|---|---|---|---|
| PS-IDLE-SPEC (the profile) | 4 | 3.128 W | 7.3 % of 42.824 W | 75.1 Wh | 1.86 .. 2.97 .. 4.68 W |
| PS-TYP | 4 | 3.112 W | 4.9 % of 62.958 W | 74.7 Wh | 1.86 .. 2.97 .. 4.68 W |
| PS-RED, lid closed | 2 | 2.000 W | 9.0 % of 22.205 W | 48.0 Wh | 1.14 .. 1.95 .. 3.56 W |
| the heat stage | 2 | 2.000 W | 8.6 % of 23.272 W | 48.0 Wh | 1.14 .. 1.95 .. 3.56 W |
| E5's hold | 2 | 2.010 W | 11.1 % of 18.152 W | 48.2 Wh | 1.14 .. 1.95 .. 3.56 W |

The picked fans' power moves both budgets: at the representatives' low and high figures E5's hold carries 18.616 to
21.236 W into the case and its line is **2.071 to 2.333 W/K**; the profile at the fans' high figures is 44.557 W against
42.824 W, so a runtime falls to 0.961 of its value. **Register row drafted** for L4-E9's downstream register (its owner
inserts it; this record edits no other record): "R-new | EVIDENCE | The five fans' power (D-18, REQ-043): the picked fans'
maker's figures at the duty the controls set replace pwr_budget.py's representative rows; E5's line moves 0.100 W/K per W
into the case and the profile by the fans' battery-side watts | L4-E12 8c | Layer 6 components with D-18 | a held sheet;
T-H1 logs the fans' drawn power".

### 13.4 T-H1: who and how [8d]

- **Who:** the prototype bench, as Layer 9's physical verification, once the owner authorises it (TEST-PLAN section 8: "it
  needs no built kit, and its purchase is the owner's to authorise"; READY-TO-ACT 5.3 lists "who runs the test and where (the
  session cannot)" as missing). A laboratory only for a chamber run at E5's +60 C, the owner's spend.
- **Hardware:** a current-moulding Peli 1450 with the 1450PF frame and a 3 mm aluminium plate blank, resistive heaters (6.8
  ohm at 12.0 V, 21.2 W each), the fans (stand-ins until D-18), a PicoLog TC-08 (READY-TO-ACT 5.2) plus a second for sixteen
  channels, a supply with its voltage and current logged. No electronics.
- **Method:** heaters spread as the model spreads E5's hold (board B 12.06 W, board A 1.81 W plus the ballasts' 2.09 W, board C
  and the face 1.50 W, the front end and charger 1.35 W, board E 0.83 W, the fans 1.95 W themselves); one heater's 21.2 W puts
  about 9.8 K on the air at the line, two 19.6 K. Eight points: two powers, lid open and closed, fans on and off. The time
  constant C/G is 0.78 to 2.27 h (32.53's 8 to 10 kJ/K over W4's 1.22 to 2.85 W/K), so a point takes 3.6 to 10.5 h to
  come within 1 % and the eight 29 to 84 h; a point ends when the mixed air drifts at most 0.1 K/h over an hour.
- **Uncertainty (ASSUMPTION, k = 1):** each channel 0.2 K after an isothermal comparison, the mixed air's spread 0.3 K, the
  ambient's drift 0.3 K, the steady-state residual 0.129 K, so the rise 0.526 K; the power 0.7 %, the leads 0.5 %. Expanded
  (k = 2): 10.7 % at a 10 K rise and 5.5 % at 20 K.
- **Pass line:** the measured conductance, lid open with the fans, less its expanded uncertainty, at or over 2.159 W/K: **a
  reading of at least 2.416 W/K at a 10 K rise** (2.285 W/K at 20 K). The room reading under-reads the margin (the outside
  films' radiation grows from the room to +60 C; on W4's films the margin's conductance is 1.15 to 1.20 times the room's,
  INFERRED); the pass line does not take that credit.
- **The procedure:** `T-H1-PROCEDURE-DRAFT.md` beside this record (channels, run order, data reduction, the pass lines and what
  each result decides).

### 13.5 A failed reading, and the fallback [8e]

| Reading, lid open with the fans | E3-O's mixed air | E5's under the hold |
|---|---|---|
| 2.100 W/K (the low case's cap) | 67.90 C | 70.28 C, past +70 C |
| 2.000 W/K | 68.54 C | 70.79 C, past |
| 1.900 W/K | 69.26 C | 71.36 C, past |
| 1.806 W/K | 70.00 C | 71.95 C, past |
| 1.666 W/K (LO-01a's floor) | 71.25 C, past | 72.95 C, past |
| 1.500 W/K | 73.06 C, past | 74.39 C, past |

A reading in (1.806, 2.159) W/K: E3-O holds as stated, E5 under the hold passes +70 C for the class of 13.1. Under 1.806
W/K E3-O passes it too. The fallbacks inside the rulings (no vent, the Peli 1450 kept):

| Fallback | What it buys (MODELED or INFERRED) | Feasibility | Whose |
|---|---|---|---|
| F1 fins on the plate (no penetration) | on W4's films, outside fins of twice the area multiply a reading by 1.125 to 1.131, fins of twice the area on both faces by 1.252 to 1.363 (a reading of 1.806 W/K would read 2.261 to 2.462 W/K); outside fins alone saturate at the inside film (1.690 W/K in the low case) | CONDITIONAL on the face's free area (the monitor, the e-paper, the switches) and the lid's clearance (CASE-MARGINS M3); the reading's own split from T-H1 | the session's (Layer 7) |
| F2 conduction from the hot boards to the plate | the air's balance loses (1 - f) of the heat led into the plate: E5 needs 5.76 W led (2.97 W at the low plate fraction) at a 2.000 W/K reading, 12.82 (6.60) W at 1.806 W/K; board B carries 12.06 W of the hold's heat | CONDITIONAL on a pad path from those parts to the plate | the session's (Layer 7) |
| F3 a deeper hold in E5 (E5 requires logging only) | turning off the switch chip (2.541 W), the NVMe (0.900 W), the PCIe switch (0.625 W) and the GNSS (0.327 W) while the module logs on its own storage takes E5's heat to 13.429 W and its line to **1.552 W/K**; a reading G allows 10 G - 2.09 W (17.91 W at 2.000 W/K) | CONDITIONAL on a supply switch for each (none read for the switch chip: Layer 8) and on E5's logging path | the session's (E5's stated configuration); never in E3-O |
| **F4 the plate coupling** (section 7) | the RockBLOCK, board D and the LimeSDR on pads to the plate sit at the plate: E5 holds them to **1.564 W/K**, E3-O to 1.309 W/K; the +80 C connectors in the exhaust then set E3-O's floor at **1.399 W/K** (1.309 out of the exhaust); with F3, E5 to **1.125 W/K**; with the fans stopped the coupled parts stay at most 69.82 C | CONDITIONAL on the pads' own rise and path; the H5007NL, ATP16 and PXP4043/C take section 6's wider parts or statements | the session's (Layer 7) |

**The best fallback is F4 with F3 in E5:** no owner ruling and no change to E3-O; E5 holds down to 1.125 W/K and E3-O down
to 1.399 W/K (1.309 W/K with the connectors out of the exhaust). **What needs the owner:** a reading under E3-O's F4 floor
leaves a deviation of E3-O's configuration (the hold in E3-O) or a device-set re-pick (CHO-001); the SGP41 is section 8's
question already.

### 13.6 What stays CONDITIONAL after this round

T-H1 lid open with the fans reading at least 2.416 W/K (2.159 W/K after its expanded uncertainty), with the picked fans; D-18's
pick with its maker's power (the line moves 0.100 W/K per W) and its operating range (REQ-043); the hold's reference placed or
calibrated; and, if the reading falls short, F4 (the pads) and F3 (the switches, the logging path). The uncertainty budget is
the bench's to replace with its own instruments' figures.

### 13.7 Decisions taken by the session in this round (authority: SESSION)

| Decision | Why the session's | Reversed by |
|---|---|---|
| T-H1's pass line is the reading less its expanded uncertainty (k = 2) against 2.159 W/K; the radiation credit is not taken | a measured requirement is met only beyond its uncertainty | the bench's own budget, or a chamber run at +60 C |
| F4 with F3 is the fallback; F3's list keeps the logging path | both inside the rulings and E5's stated configuration; F4 holds E3-O unchanged | T-H1's split and the generator owners' switches |
| L4-E9's output is cited, not pinned | it quotes this record; a pin would bind the two records in a cycle | the coordinator |
| L4-E8's and L4-E10's figures and E5's cycle read from their pinned files | they are on the base since set 26 | the coordinator |

## 14. The conservative lower bound, and U-02's class (the consolidation, 2 October 2026) [9]

The owner's question: "Thermal: finish the conservative feasibility bound and fallback. State whether T-H1 confirms the
design or determines whether it can work. Give the test configuration and acceptance condition if measurement remains
necessary." **Answer: T-H1 DECIDES. U-02 stays a closure condition.** On held geometry and conservative coefficients the
sealed case does not hold E3-O as stated, even with every measure inside the session's authority; E5 holds with them.

### 14.1 The model and its coefficients [9a]

The inside air reaches the ambient by two paths in parallel, each solved for its heat at the stated air rise (natural
convection is not linear, so the bound is computed at each condition's own rise):

- **the plate:** the inside film, the 3 mm aluminium (no resistance to speak of), then the outside films (lid open), or the
  enclosed layer to the lid and the lid's shell (lid closed);
- **the walls:** the inside film, the PP shell, the outside films;
- **the floor:** adiabatic, because the case stands on its feet 8.38 mm over a support whose temperature no document gives.

| Quantity | Value the bound takes | Range | Source and class |
|---|---|---|---|
| The plate's area, outside | 0.0912 m2, L = A/P 0.0741 m | | W4's plate outline (`panel1450.py` PLATE), pinned |
| The walls, inside / outside | 0.1296 / 0.1444 m2 | | CASE-MARGINS 2.1 and 2.2: the perimeter 377.75 x 263.45 mm at mid-height, floor to the shoulder at 101.04 mm; the outer perimeter over the base's 108.97 mm |
| The shell's thickness | 5.34 mm | | CASE-MARGINS 2.3 (Peli's drawing, VERIFIED there) |
| Lid closed: the ceiling, the skirt, the layer | 0.0803 m2, 0.0578 m2, 53.5 mm | the layer 46.5 to 53.5 mm | CASE-MARGINS 2.1 and 2.2; W4 |
| The plate's emissivity | 0.70 | 0.70 to 0.90 (anodised, 32.53) | textbook emissivity tables, INFERRED |
| The shell's emissivity | 0.85 | 0.85 to 0.95 (pigmented PP) | textbook, INFERRED; Peli publishes none |
| The PP's conductivity | 0.12 W/mK | 0.12 to 0.22 W/mK | textbook polymer tables, INFERRED |
| The plate's view past the open lid | 0.70 | 0.70 to 1.00 | ASSUMPTION (the lid taken as reradiating) |
| Outside convection | still air at the margin's ambient | a chamber's circulation would add | natural convection: a plate facing up, Nu = 0.54 Ra^(1/4) (0.15 Ra^(1/3) over 1e7), L = A/P (McAdams; Lloyd and Moran); a vertical wall, Churchill and Chu, Nu = {0.825 + 0.387 Ra^(1/6)/[1 + (0.492/Pr)^(9/16)]^(8/27)}^2; textbook, INFERRED |
| The enclosed layer, lid closed | | | Hollands et al., Nu = 1 + 1.44[1 - 1708/Ra]+ + [(Ra/5830)^(1/3) - 1]+, plus radiation between the plate and the lid |
| Radiation | to surroundings at the ambient | | eps F sigma (T1^2 + T2^2)(T1 + T2) |
| The inside film | natural convection only | the fans' flow and the stack's radiation credited separately below | no held document places or picks the fans (D-18 open), so their flow is credited at zero |

### 14.2 The bound [9b]

| Condition | Lid open, with the fans (their flow credited at zero) | The coefficients' other ends | Lid closed | With a 50 m/s inside flow (a film near 45 W/m2K; not the zero-resistance capacity, 17.9) |
|---|---|---|---|---|
| E5: +60 C, the air 10 K up | **0.566 W/K** | 0.626 | 0.505 | 1.540 |
| E3-O: +55 C, the air 15 K up | **0.607 W/K** | 0.673 | 0.537 | 1.571 |
| the envelope's +40 C, the air 15 K up | 0.598 W/K | | 0.524 | |

Credits that no held evidence bounds, at E5 (lid open):

| Credit | Bound with it |
|---|---|
| the fans' flow across the inner faces, 0.2 m/s | 0.608 W/K |
| the fans' flow, 0.5 m/s | 0.690 W/K |
| the fans' flow, 1.0 m/s | 0.799 W/K |
| the stack's radiation to the plate | 0.654 W/K (0.767 with 0.5 m/s) |
| the floor on its feet, over a support at the ambient | 0.697 W/K |
| all the favourable ends together, with 1.0 m/s | 1.145 W/K |

The bound's films at E5 are 4.13 W/m2K inside at the plate and 3.85 at the walls, and outside 7.72 at the face and 10.03 at
the walls. The lid-closed and envelope figures belong to U-01 and LO-01a, not to this record; they are recorded because the
same bound lies far under LO-01a's 1.6664 W/K.

### 14.3 The budget's 1.22 W/K reconciled [9c]

The budget's 1.22 to 2.85 W/K (lid open, fans) and 1.06 to 2.49 W/K (lid closed) are W4's lumped estimate, as pwr_budget.py
carries them. W4 uses fixed films:

- inside, 10 to 25 W/m2K, for "low-velocity forced flow from the mixer and cooler fans, plus internal radiation";
- outside, 9.5 to 11.5 at the face, 8 to 10 at the walls and 3 to 8 at the floor, at about 310 K with emissivities of 0.85
  to 0.9;
- the base's walls at 0.137 to 0.220 m2, and PP at 0.018 m2K/W.

**It is a sensitivity estimate, not a lower bound: its low end already assumes the fans' film.** Changing one assumption at a
time, from W4's low case to the bound (E5):

| Step | Conductance |
|---|---|
| W4's low case | 1.222 W/K |
| the floor adiabatic | 1.009 |
| the walls' inner area to the plate | 0.977 |
| the wall 5.34 mm of PP at 0.12 W/mK | 0.925 |
| the outer films at +60 C with the conservative emissivities and the lid's view | 0.928 |
| the inside film: natural convection only | **0.566** |

The decisive term is the inside film. W4's low case takes 10 W/m2K with the fans; natural convection gives 3.85 to 4.13 W/m2K.
**The consolidation's statement holds, and the gap is wider:** the model's low bound of 1.22 W/K lies under E3-O's floor of
1.399 W/K, and the conservative bound, 0.566 to 0.607 W/K, lies further under it.

### 14.4 Against the lines and the fallback [9d]

- **CORRECTED in 17.9:** this bullet read 1.540 to 1.571 W/K as the outside films' cap with any inside film. Those figures are the
  bound with a 50 m/s inside flow, whose film is near 45 W/m2K. The capacity with the inside resistance at zero is 1.856 W/K at
  E5's rise and 1.906 W/K at E3-O's (conservative ends), 3.144 and 3.181 W/K at the optimistic ends with the floor. So E3-O's
  1.806 W/K lies under it even at the conservative ends, and E5's 2.159 W/K over it there but under it at the optimistic ends.
  No physics bars either line; T-H1 decides.
- **Section 8's floors lie over the bound.** E5's 1.125 W/K (F4 with F3) is 0.559 W/K above it; E3-O's 1.399 W/K (1.309 with
  the connectors out of the exhaust) is 0.792 W/K above it.
- **Where the air settles on the bound** (lid open, at its own rise):

| State | Mixed air | Plate | The +70 C class on the plate (F4) | The +80 C connectors | The module's +85 C at its intake (device set) |
|---|---|---|---|---|---|
| E5, the hold | 90.93 C | 71.48 C | past +70 C | past | past |
| E5, the deeper hold (F3) | 83.41 C | 68.58 C | inside | past (in or out of the exhaust) | inside |
| E3-O, the heat stage | 92.61 C | 69.22 C | inside | past | **past** |

**With every session measure** (F4; F3 in E5; the +80 C connectors on board B replaced by +85 C parts, Layer 6; the HX
magnetics; the wider buttons), the module's +85 C at its intake binds:

| Margin | Conductance needed | Bound at the same rise | Result | What would close it |
|---|---|---|---|---|
| E5 | 0.621 W/K at 25 K | 0.671 W/K | holds, 0.050 W/K to spare | nothing further needed |
| E3-O | 0.903 W/K at 30 K | 0.691 W/K | **gap of 0.212 W/K** | the fans' flow across the inner faces, 1.28 m/s on its own; or the stack's radiation and the floor's support, which together raise the bound to 0.938 W/K |

### 14.5 U-02's class, and what closes the gap [9e]

**T-H1 DECIDES feasibility; it does not confirm an already-supported design.** On bounded evidence E3-O, with every radio on
at +55 C in still air, puts the module's intake at 92.61 C against its +85 C. Each route to the missing 0.212 W/K, and whose
it is:

| Route | Status |
|---|---|
| The mixers' flow at the inner faces (1.28 m/s; their placement is Layer 7's) | T-H1 measures it |
| The stack's radiation and the floor's support | T-H1 measures them |
| Leading the module's heat into the plate | competes with F4 for the plate's outside (0.704 W/K at the bound's face film) and needs a finned plate the face's layout has not been shown to carry: Layer 7's, unbounded |
| A deeper hold in E3-O | a deviation of E3-O's configuration: the owner's |
| A device-set re-pick (CHO-001) | the owner's |

None closes the gap on held evidence within the session's authority without the measurement.

### 14.6 The smallest experiment, and its acceptance [9f]

**One point of T-H1:**
- lid open;
- the fans at full duty: the two mixers and slot 3's cooler fan (stand-ins until D-18);
- one heater's 21.2 W, spread as E5's hold spreads it (section 13.4);
- room temperature, still air;
- four mixed-air channels, two ambient, the plate's inner face and a wall's inner face: one PicoLog TC-08.

It runs until the mixed air drifts at most 0.1 K/h over an hour: about 5.9 h at the line's conductance, and up to 21.1 h if
the case is as poor as the bound (time constant 4.57 h). G = P / rise; each threshold is the target plus its expanded
uncertainty at that point's rise:

| A reading of at least | Its rise | Meets | Settles |
|---|---|---|---|
| **2.462 W/K** | 8.6 K | 2.159 W/K | the design as stated (route (c)), no fallback |
| **1.516 W/K** | 14.0 K | 1.399 W/K | section 8's fallback (F4, F3); 1.410 W/K reaches 1.309 with the connectors out of the exhaust |
| 1.199 W/K | 17.7 K | 1.125 W/K | E5 with F4 and F3 |
| **0.951 W/K** | 22.3 K | 0.903 W/K | E3-O with every session measure, provided the measured plate fraction keeps the plate-coupled +70 C class inside (the fraction times 27.086 W over the reading, at most 15 K) |
| 0.644 W/K | 32.9 K | 0.621 W/K | E5 with every session measure |

**Acceptance condition:** read lid open with the fans at one power, **2.462 W/K or more** keeps the design as stated;
**1.516 W/K or more** keeps it with the session's fallback; **0.951 W/K or more** keeps E3-O with every session measure;
**under 0.951 W/K** E3-O as stated cannot hold on the session's means, and the owner decides (a deviation of E3-O or a
re-pick). The room reading is the conservative side of the margin's (section 13.4). The full eight-point T-H1 follows, for
the fans-off case, the lid-closed state and the fractions (`T-H1-PROCEDURE-DRAFT.md`).

### 14.7 The fans' power [9g]

Section 13.3 stands. The fans' power is counted in pwr_budget.py, the 42.8 W profile, its replay and L4-E9's endurance: 2.0 W
in the hold and 3.1 W in the profile. It is not among the 8.4 W with no document. The bound credits the fans' flow at zero but
still counts their heat inside the case, so nothing in 13.3 changes.

### 14.8 Decisions taken by the session in this round (authority: SESSION)

| Decision | Why the session's | Reversed by |
|---|---|---|
| The bound credits the fans' flow, the stack's radiation and the floor's support at zero | no held document bounds them; each is shown as a credit | T-H1's reading |
| The class follows the bound: CONFIRMS only if the bound, with every session measure, clears both margins | the owner's question, read literally | T-H1 |
| The smallest experiment is one lid-open, fans-on point at one heater's power | it settles the class; the rest of T-H1 characterises | the bench |

## 15. The heat-rejection question (the consolidation, 2 October 2026) [10]

**Corrected by sections 16 and 17:** the profile at +40 C is not a requirement (C1 sheds it, REQ-024; D-02b); 1.447 W/K is the
profile's own condition at REQ-014's +20 C (K6); 15.5's 42.4 W left the fans out of P; and charging is a balance (17.3, the
review's B4): 52.134 W into the case, so its start line needs 1.810 to 2.200 W/K and a running charge more (17.2). The charging
figures below are restated on that heat; the rest stand as figures of the bound.

The owner: "For any function still failing after repeated corrections, compare at most three credible approaches ...
Quantify the consequences for power, heat, space, cost and endurance. Select the best-supported route", and "If no supported
alternative exists, name the exact missing fact and the smallest practical experiment." The question asked of this record: if
T-H1 reads under what the approved profile needs, what change inside the rulings restores the profile at REQ-024's +40 C, and
charging on the design day? **Answer: none of the three reaches the need on bounded evidence.** The best route, built from
all three, falls 1.252 W (0.063 W/K) short at +40 C. U-02 stays a closure condition, and its exact missing fact is T-H1's
reading.

### 15.1 The need [10a]

- **The profile's heat:** PS-IDLE-SPEC puts 43.413 W into the case with the lid open (MODELED: 42.824 W at the pack plus the
  pack's own I2R; L4-E9's 43.4 W at `a0212d9e`).
- **The +70 C class at +40 C:** it needs **1.447 W/K**.
- **Charging with the profile running:** a charge starts only while the gauge reads at or under 42 C (TEST-PLAN, T3). On SC-37's
  design day, with the air at 13.2 to 18.3 C (the replay), the charging heat of 52.134 W (17.3) needs **1.810 to 2.200 W/K**.
- **The rulings:** no vent or opening anywhere (32.53); the Peli 1450 kept at any cost; the face a 3 mm aluminium plate carrying
  the UI (32.40).
- **The model:** every figure is on section 14's bound (the inside air moves by natural convection only, the coefficients sit at
  their conservative ends, still air), extended to two nodes, the inside air and the plate.

### 15.2 The three approaches compared [10b]

**(a) Fins on the face's free strips.**
- The free area is 0.0552 m2: the plate's 0.0912 m2 less the monitor window (0.0288 m2) and the e-paper lens (0.0071 m2).
- The fins are fixed under M3's space beneath the QMX tray (19.92 mm nominal, 14.11 mm with the unstated allowances doubled), or
  a clip-on exchanger is fitted when deployed.
- The effective area multiplier is 2 to 3 (ASSUMPTION; a vendor's heat-sink datasheet gives the real one).

**(b) The large loads led into the plate** by heat pipes, bars and gap pads, so the plate rejects them at its own temperature and
the air keeps only the rest. They total 23.641 W at their pins:
- the Xenarc, 6.0 W;
- the live WiFi card, 4.0 W;
- the three modules, 6.0 W;
- panel board C, 1.5 W;
- the switch chip, 2.541 W;
- the three NVMe, 2.7 W;
- the PA, 0.9 W.

**(c) The open lid as a second radiator.**
- An aluminium skin on the lid's flat ceiling (0.0803 m2, an upper bound, since the QMX tray and the tablet bracket share it),
  0.329 m tall when open.
- A copper braid from the plate's edge runs inside the seal line: 0.20 m, 200 mm2, so 2.56 K/W (ASSUMPTION).

| Approach (MODELED on the bound; the profile's 43.413 W at +40 C, the charging heat's 52.134 W on the design day) | +40 C: the air / the plate / G | Design day 13.2 C: the air / G | 18.3 C: the air / G |
|---|---|---|---|
| none: the bound | 96.61 C / 62.34 C / 0.767 W/K | 80.37 C / 0.776 | 85.28 C / 0.778 |
| (a) fins, k 2 | 92.89 / 56.15 / 0.821 | 75.74 / 0.834 | 80.69 / 0.836 |
| (a) fins, k 3 | 90.84 / 52.78 / 0.854 | 73.16 / 0.869 | 78.15 / 0.871 |
| (b) the large loads into the plate | 79.59 / 70.08 / 1.096 | 64.43 / 1.018 | 69.29 / 1.022 |
| (b) with (a)'s fins, k 3 | 72.41 / 56.96 / 1.339 | 55.76 / 1.225 | 60.71 / 1.229 |
| (c) the lid's skin on a strap | 94.17 / 58.27 / 0.801 | 77.31 / 0.813 | 82.26 / 0.815 |
| **(b) + (a) + (c), the best route** | **71.36 / 55.12 / 1.384** | 54.46 / 1.263 | 59.43 / 1.268 |
| need | the air at 70 C: 1.447 W/K | the air at 42 C: 1.810 | 2.200 |

**Why (a) alone barely helps:** the plate's inner film limits it. **Why (b) helps most:** it bypasses that film entirely. **What
(c) adds:** the strap carries 4.37 W in the best route.

### 15.3 Consequences [10c]

All three are passive: no power, no change to endurance, and the heat into the case unchanged. Costs are TBD; no quote is
held.

| | Space and mass | The UI | The rulings | Confirmed by |
|---|---|---|---|---|
| (a) | about 0.39 kg of 1.5 mm fins at an 8 mm pitch to the worst M3 height (ASSUMPTION); no inside space; a clip-on exchanger needs stowage | the strips between the monitor, the e-paper and the switches; the light guides kept clear | bonded fins keep the face a 3 mm plate (a SESSION reading); an extruded, thicker face would change 32.40's ruling (the owner's) | a vendor's heat-sink datasheet with its natural-convection resistance, or a T-H1 point with the fins |
| (b) | spreaders and pads in the 11.9 to 22.9 mm between board B's tall parts and the face parts; mass TBD | the plate runs at 55.12 C (70.08 C without fins): the face's touch temperature rises (no held limit; an evaluation is owed), the e-paper's +60 C is passed without fins, the switches go to +85 C parts | all inside the seal | the heat pipes' or pads' datasheets, and a T-H1 point with the conduction kit |
| (c) | about 0.58 kg (a 1 mm skin 0.22 kg, the braid 0.36 kg); the braid's fatigue over the hinge cycles; the lid tray's layout | none | inside the seal line, no penetration | a T-H1 point with the lid open and the skin fitted |

In (b) each led part sits at the plate's temperature plus its own path's drop. The WiFi card's +70 C limit caps that drop at
about 15 K in the best route.

### 15.4 The selection, the shortfall, and the owner's options [10d]

**None of the three reaches the need on bounded evidence.**
- **At +40 C:** the best route (b with (a)'s fins and (c)) keeps the air at 71.36 C. It rejects 42.161 W with the air at +70 C
  against the profile's 43.413 W: **short by 1.252 W (0.063 W/K)**.
- **Charging with the profile running:** stays **0.547 and 0.932 W/K** short on the design day's cold and warm ends (on the
  charging heat of 17.3).
- **On the bound alone:** the case rejects 20.449 W at +40 C, 22.964 W short.
- **What would carry the route over:** the inside film the fans make (credited at zero in section 14), and the fins' and the
  paths' real resistances. Each is a measurement or a maker's datasheet, and none is held.

The remaining options are the owner's:
- **An ALTERNATIVE duty cycle at +40 C, labelled as such:** PS-IDLE (the monitor dimmed, no beacon) puts 40.242 W into the case,
  1.919 W under the best route's 42.161 W. Nothing fits on the bound alone.
- **A requirement change:** the profile's ambient ceiling, or charging with the profile running on the design day.

### 15.5 U-02 by the owner's exit definition [10e]

**U-02 is a CLOSURE CONDITION.** Its exact fact: the sealed case's conductance with the lid open and the fans running, as T-H1
reads it. The fans' inside film is the part no document bounds.

**The smallest experiment:**
- one T-H1 point, lid open;
- the fans at full duty;
- two heaters (42.4 W, about the profile's heat), spread as the boards dissipate;
- room air, run to steady state.

**Its acceptance**, each threshold being the target plus its expanded uncertainty:

| Reading | Settles |
|---|---|
| at least **1.509 W/K** (28.1 K rise) | meets 1.447 W/K: the profile at +40 C, with no route needed |
| at least **1.906 W/K** (22.2 K rise) | meets 1.810 W/K: charging with the profile on the design day's cold end |
| at least **2.342 W/K** (18.1 K rise) | meets 2.200 W/K: charging with the profile on the design day's warm end |

These readings take the 42.4 W of two heaters for every line and are superseded: sections 16 and 17 read each mode at its own heat,
the fans counted (17.4).

Under 1.509 W/K, the route of 15.4 is built and its kit measured at the same bench point; if it still reads short, the owner
chooses among 15.4's options.

### 15.6 Decisions taken by the session in this round (authority: SESSION)

| Decision | Why the session's | Reversed by |
|---|---|---|
| The three approaches compared on the same bound and model, each alone and assembled | the owner's rule: at most three, quantified | T-H1 and the makers' datasheets |
| The fins' multiplier 2 to 3, the braid 0.20 m by 200 mm2, the set of loads led into the plate | no held datasheet or layout gives them; each is printed with its effect | a vendor's datasheet; Layer 7's layout |
| No route selected: none reaches the need on bounded evidence | the owner's exit definition, read literally | T-H1's reading |

## 16. The thermal reconciliation (the owner's amendment of 2 October 2026, 14:20, item 1) [11]

The owner asked what section 15.5's line means: that a T-H1 point at 42.4 W reading at least 1.509 W/K "establishes operation
at +40 C ambient". His check: 42.4 / 1.509 = 28.1 K, so the air would be about +68.1 C at +40 C; and if a +55 C inside-air limit
applied to that mode, the need would be 42.4 / (55 - 40) = 2.83 W/K. This section answers him point by point. Every figure is
printed in the `.out`'s section 11.

**The answer in short:**
- **The arithmetic of 1.509 holds, but the claim was too wide.** It establishes only the profile's +70 C class at +40 C, and
  no requirement asks for that: at +40 C the controls shed the profile (C1 at +50 C inside air, REQ-024; D-02b runs one module
  above +35 C). The words "operation at +40 C" are withdrawn.
- **The owner's +68.1 C is right.** The same reading puts the air at 68.1 C at +40 C, past C1's +50 C trigger, so the kit
  would not stay in the profile there.
- **CORRECTED in section 17 (the review's B3):** a +55 C inside-air line exists only as REQ-052's and E3-L's fail line, read
  from the SGP41's Table 5 absolute row. It is a screen (K1, K5: 1.806 W/K), not a functional limit; the SGP41's sensing ends at
  Table 4's +50 C, and each mode's governing line is section 17's.
- **The owner's 2.83 W/K belongs to no requirement's mode.** No requirement holds the profile's 42.4 W under +55 C at +40 C.
- **One lid-open, fans-on point meets four conductance screens, and closes no mode (corrected in section 17).** At the heat
  stage's heat (heaters 25.136 W plus the fans), a reading of at least **1.958 W/K** meets the screens K1, K3, K4 and K9 at the
  mixed air, for its own configuration only.

### 16.1 The claim, checked [11a]

**The arithmetic.**
- At the bench: 42.4 W / 1.509 W/K = 28.1 K.
- The expanded uncertainty at that rise is 4.12 % (k = 2).
- After it: 1.509 x (1 - 0.0412) = 1.447 W/K, which is the profile's 43.413 W over the 30 K from +40 C to the +70 C class.

**What it establishes:** the profile's own +70 C class at +40 C. No requirement asks for that, because the kit does not run the
profile at +40 C:
- REQ-024: "on measured inside-air (+50 C) and cell (+55 C) temperatures the kit sheds to its reduced mode and then its heat
  stage (C1)";
- D-02b: "above +35 C ambient the kit runs one module".

**Where 1.447 W/K does belong:** it is the profile's own condition at REQ-014's +20 C ("its battery-only runtime is stated in
hours in an idle and a typical mode (PS-IDLE-SPEC and PS-TYP) at +20 C"). There the profile runs unshed only while the inside air
stays under C1's +50 C: 43.413 W over 30 K (K6 below).

### 16.2 The heat, counted once [11b]

All MODELED, plan. Nothing is counted twice: the fans' power is among the loads at the pins, and on the bench it is measured,
not modeled.

| Mode | At the load pins (the fans among them) | Converters and distribution | Front end and charger | Pack's own I2R | L4-E8's ballasts | Into the case |
|---|---|---|---|---|---|---|
| The profile PS-IDLE-SPEC, on the pack | 36.448 W (2.97 W: the three modules' coolers and the two mixers) | 6.376 W | none | 0.590 W | not counted (solar stage only) | **43.413 W** |
| The profile charging on the design day (corrected, 17.3: the balance) | as above | as above | 3.174 W source path + 3.446 W charge path | 0.600 W (charging) | 2.09 W (the solar stage runs) | **52.134 W** |
| The heat stage on shore (C1's end state) | 19.378 W (1.95 W: slot 3's cooler and the two mixers) | 3.893 W | 1.725 W | none | 2.09 W (the worst corner, the margins' rule) | **27.086 W** |

**What is not in the profile's heat:**
- L4-E8's ballasts: 0.0093 W at its nominal illustration, at most 2.09 W at the bound's worst corner, and only while the solar
  stage runs;
- the solar entry's sense bank (solar current only);
- Q39's 0.0945 W with L4-E11's (B1), as L4-E9 at `a0212d9e` states it.

**The bench.**
- **The heater:** READY-TO-ACT's heater is 6.8 ohm at 12.0 V, giving 21.176 W of heat (all of its electrical power stays
  inside). Two give 42.353 W, the "42.4 W".
- **The fans:** they run from the bench supply. Their measured draw is heat inside the case and is added to the heaters, so
  **P = the heaters + the fans, never the heaters alone.** Section 15.5's 42.4 W left the fans out; 16.6 restates it.
- **Standing for a mode:** the heaters are set to the mode's heat less the fans' measured draw:
  - the profile, 40.443 W (two heaters at 11.73 V);
  - the heat stage, 25.136 W (one heater at 13.07 V).
- The fans' measured draw replaces their modeled share, so nothing is counted twice.

### 16.3 The nodes and the limits [11c]

**The nodes.** The conductance G = Q / rise is defined between two nodes:
- the mixed inside air: the mean of the air channels, with the hold's reference placed in it (section 4d);
- the ambient air: shaded channels about 0.5 m from the case.

**The ambients.**
- **On the bench:** the room, +22 C taken.
- **In operation:** REQ-024, "The kit operates at -20 to +40 C ambient".

**The limits, each with its reference:**

| Limit | At the node | Reference |
|---|---|---|
| C1's +50 C inside-air and +55 C cell triggers | control triggers that shed, not damage limits | REQ-024; CONOPS 4: "C1, module shedding \| inside air +50 C or any cell +55 C \| normal to the reduced mode; reached again in the reduced mode, to the heat stage; restores 5 K below" |
| The SGP41's +55 C: a SCREEN, Table 5's absolute row (corrected in 17.1) | the inside air | REQ-052: "every part inside its published range (an SGP41 above +55 C fails)"; TEST-PLAN E3-L: "the inside air at or under the SGP41's +55 C; an SGP41 above +55 C fails E3-L"; resting on its Table 5 absolute row |
| The SGP41's +50 C | the inside air | its Table 4, under this record's corrected rule (section 4d); the owner's CFL-002 |
| The +70 C class | the inside air | the makers' sheets of section 4: RockBLOCK 9704, SA868, G6K, PCM2912A, LimeSDR, H5007NL, ATP16, PXP4043/C; the AW7915's 0 to +70 C operating while the profile runs it |
| The module's +85 C | its intake | CM5 datasheet p.28 |
| The cells | the cells, taken at the air | E3-A: "no charge starts while the gauge reads above 42 C (T3)"; "every cell surface at most +60 C throughout" |
| Every part in its range | every part | REQ-024's acceptance: "part_temps.py finds no part outside its range" |

**D-02a's +55 C is an AMBIENT qualification margin, not an inside-air limit.** In its own words: "TEST-PLAN's +55 C operating,
+71 C storage and -33 C storage are QUALIFICATION MARGINS over the -20 to +40 C use and -20 to +45 C storage envelope, with two
pass lines: operate to specification inside the envelope; survive and recover at the margin." It is the ambient of E3-O (K9).

**Each condition, and the conductance it needs** (Q over the room from the ambient to the limit):

| Id | Requirement and mode | Lid | Heat into the case | Ambient | Limit at the node | Needs |
|---|---|---|---|---|---|---|
| K1 | REQ-024 and E3-A at +40 C: C1's end state, the heat stage on shore with the ballasts | open | 27.086 W | +40 C | the SGP41's +55 C (REQ-024's acceptance, every part in its range; REQ-052's and E3-L's line; its Table 5) | **1.806 W/K** |
| K2 | the same, the SGP41 judged on its Table 4 +50 C (this record's corrected rule; the owner's CFL-002 open) | open | 27.086 W | +40 C | the SGP41's +50 C (Table 4) | 2.709 W/K |
| K3 | the same, the +70 C class in the heat stage (the H5007NL, the ATP16, the PXP4043/C and the radios C1 leaves on) | open | 27.086 W | +40 C | +70 C (the makers' sheets of section 4) | 0.903 W/K |
| K4 | the same, the module's intake | open | 27.086 W | +40 C | the module's +85 C (CM5 4.4) | 0.602 W/K |
| K5 | REQ-052 and E3-L at +40 C: the heat stage | closed | 27.086 W | +40 C | the SGP41's +55 C (E3-L's line) | **1.806 W/K** |
| K6 | REQ-014 at +20 C: the profile on the pack, not shed by C1 | open | 43.413 W | +20 C | C1's inside-air trigger +50 C (REQ-024) | 1.447 W/K |
| K7 | charging on SC-37's design day, the profile running, the balance of 17.3, cold end | open | 52.134 W | +13.2 C | the gauge's charge start T3 42 C (the idle cells at the air; a running charge's T4 is 17.2's) | 1.810 W/K |
| K8 | the same, warm end | open | 52.134 W | +18.3 C | T3 42 C | 2.200 W/K |
| K9 | E3-O, D-02a's +55 C AMBIENT margin: the heat stage, every radio C1 leaves on | open | 27.086 W | +55 C | +70 C (U-02) | 1.806 W/K |
| K10 | E5's +60 C dwell under the hold | open | 21.587 W | +60 C | +70 C (U-02) | 2.159 W/K |
| X1 | the profile at +40 C (no requirement: C1 sheds it, REQ-024; D-02b runs one module above +35 C) | open | 43.413 W | +40 C | C1's +50 C | 4.341 W/K |
| X2 | the profile's +70 C class at +40 C (the consolidation's framing; no requirement) | open | 43.413 W | +40 C | +70 C | 1.447 W/K |
| X3 | the owner's conditional check: 42.4 W under a +55 C inside-air limit at +40 C | open | 42.400 W | +40 C | +55 C | 2.827 W/K |

**Does a +55 C inside-air limit exist? Only as a test plan's fail line (CORRECTED in section 17, the review's B3).**
- **Where it appears:** REQ-052's acceptance and E3-L's line ("an SGP41 above +55 C fails"), both read from the SGP41's Table 5,
  the absolute ratings. An absolute rating is an exclusion screen: it never stands in for the sensor's function, which Table 4
  supports to +50 C. This round had read it as a limit "the SGP41 being a part with that published range": withdrawn.
- **What K1 and K5 are:** screens, 1.806 W/K (LO-01a's floor with the ballasts), not closure lines. The governing line of each
  mode is section 17's.
- **The owner's conditional 2.83 W/K (X3)** belongs to no requirement's mode.
- **No temperature requirement is relaxed:** every limit is applied as written, and K2 keeps the SGP41 on Table 4 for the
  owner's CFL-002.

**Part-level hot spots.** These limits sit on a part's junction or case, not on the air:
- the TLV75533 regulators' +125 C recommended junction (3c, 5c);
- the converters' junctions (3c);
- the module's SoC (its own throttle);
- the PA's flange on the plate (CONOPS's key-down window and C4, PWR-F15; not this section's K conditions);
- the parts in a cooler's exhaust (2h, +5.64 K over the mixed air);
- the plate-mounted face parts (the plate's own temperature).

**What T-H1's air reading bounds, and what it does not.**
- **It bounds** the parts rated by ambient that sit in the mixed air.
- **It does not bound** the junction-rated parts (their rise is modeled: THM-001 at +40 C, REQ-024's acceptance) or the parts in
  the exhaust (placement). T-H2 measures both on the built kit.
- **The face parts:** the plate fraction T-H1 records bounds them.

### 16.4 The relationship, the evidence, and the translation [11d]

**The relationship (the owner's primary reference).** Rittal's calculation basis for enclosure climate control
(`https://www.rittal.de/downloads/eBook/TSH/EN/Climate_control/pubData/SEO/Page_6.html`) gives the steady balance:
- "QS = A k ΔT (watts)";
- A is the effective heat-dissipating enclosure surface (to IEC 890), and k the heat transfer coefficient, "for sheet steel
  k = 5.5 W/m2K";
- the largest rise follows as Qv / (A k).

The page was read on 2 October 2026 (12:39Z, HTTP 200, 2522 bytes, sha256 `fd3a31d31c88adb4...`). It is held back by its
copyright: `fetch_held_back.py` fetches it into the ignored `v2/vendor/rittal/held/` and checks the sha256.

**The product A k is this record's G = Q / rise. The steel figure is not this enclosure's:**
- the Peli 1450 is a 5.34 mm polypropylene shell;
- only natural convection moves the air inside (the fans' flow is credited at zero);
- the face is an aluminium plate, with the lid open.

So this enclosure's k comes from its own films and walls (section 14's bound). At +40 C and K1's 15.0 K rise, the areas are the
plate's exposed 0.0912 m2 and the walls' outer 0.1444 m2, together 0.2356 m2; the floor is taken as adiabatic.

| Coefficients | k plate | k walls | k whole | A k |
|---|---|---|---|---|
| the bound | 2.85 W/m2K | 2.34 | 2.54 | 0.598 W/K |
| the coefficients' other ends | 3.22 | 2.54 | 2.81 | 0.661 W/K |

**Against the need:**
- **Sheet steel's 5.5 W/m2K** on the same area would read 1.296 W/K.
- **K1's 1.806 W/K** needs k = 7.66 W/m2K over that area, 2.7 to 3.0 times what the bound's films give.
- **With a 50 m/s inside flow** (a film near 45 W/m2K) A k reaches 1.504 W/K (1.859 at the coefficients' other ends), in still
  air with the floor adiabatic. As first written this was called the outside films' cap; **corrected in 17.9:** with the inside
  resistance at zero, the capacity at K1's rise is 1.810 W/K (2.963 at the optimistic ends with the floor), over K1's 1.806 W/K.
- **The tree's other evidence spans the need:** W4's lumped estimate gives 1.22 to 2.85 W/K (fixed films with the fans, the floor
  counted), and 32.53 gives 3.0 to 3.3 W/K.

**So the bound under the need leaves feasibility unestablished, not refuted.** What the bound does not credit:
- the floor's support;
- the outside's real films and its air movement;
- the fans' film inside;
- heat led into the plate past the air (15.2 (b)).

Only a measured G decides it: T-H1.

**Why the simple calculation is not enough.** There are two heat paths in parallel (the plate and the walls), each through an
inside film, a wall and an outside film. Their convection depends on the rise and their radiation on the absolute temperatures,
so G is not one constant: it changes with the heat (a reading at one heat bounds that heat) and with the ambient.

**The translation from the bench to +40 C** (the bound's model at the same rise, G = Q / rise, at +22 C against +40 C):

| Case | Rise 15 K: room, then +40 C | Factor | Rise 30 K: room, then +40 C | Factor |
|---|---|---|---|---|
| the bound | 0.588 then 0.598 W/K | x 1.018 | 0.671 then 0.682 W/K | x 1.016 |
| the coefficients' other ends | 0.648 then 0.661 | x 1.021 | 0.740 then 0.755 | x 1.020 |
| the fans' flow 0.5 m/s | 0.681 then 0.697 | x 1.025 | 0.741 then 0.756 | x 1.020 |
| the stack's radiation | 0.646 then 0.670 | x 1.037 | 0.735 then 0.759 | x 1.033 |

- **The operating ambient's conductance is 1.6 to 3.7 % above the room's** at the same rise. The room reading is the conservative
  side, and the translation's uncertainty is not material. So the procedure tests at room temperature, with an optional
  confirming point in a chamber at +40 C.
- **Section 13.4's 1.15 to 1.20** came from W4's outside-film radiation alone. The inside film, which is convective, dominates the
  whole.
- **The bench's 28.1 K is not the same 28.1 K at +40 C:** the rise there is the bench's divided by the factor above. The rise also
  changes with the heat, so each heat needs its own point (16.6).

**The transient.** E3-A holds +40 C for 4 h. At 1.806 W/K the case's time constant is 1.23 to 1.54 h (32.53's thermal mass), so
the air reaches 92.6 to 96.1 % of its steady rise within the dwell. The steady state is the bound.

**The sun.** No solar load enters the derivation:
- REQ-024: "the kit is operated shaded (D-02e)";
- D-02e: "'Operate shaded' is a stated operating condition, with a shade accessory (a lid sun shield or a tarp); full-sun design
  is a later qualification item. No board change.";
- TEST-PLAN holds no Method 505 row.

Full sun stays a later qualification item.

### 16.5 The margin [11e]

Each condition's bench reading is taken at its own heat (the heaters plus the fans). Its threshold is the need plus the expanded
uncertainty at that rise (the budget of 13.4). The room-to-operating credit of 16.4 is kept as margin, not taken.

| Id | Heat | Needs | A reading of at least | Its rise | U (k = 2) |
|---|---|---|---|---|---|
| K1 | 27.086 W | 1.806 W/K | **1.958 W/K** | 13.8 K | 7.8 % |
| K2 | 27.086 W | 2.709 W/K | 3.081 W/K | 8.8 K | 12.1 % |
| K3 | 27.086 W | 0.903 W/K | 0.941 W/K | 28.8 K | 4.0 % |
| K4 | 27.086 W | 0.602 W/K | 0.620 W/K | 43.7 K | 3.0 % |
| K5 | 27.086 W | 1.806 W/K | **1.958 W/K** (lid closed) | 13.8 K | 7.8 % |
| K6 | 43.413 W | 1.447 W/K | **1.508 W/K** | 28.8 K | 4.0 % |
| K7 | 52.134 W | 1.810 W/K | **1.889 W/K** | 27.6 K | 4.2 % |
| K8 | 52.134 W | 2.200 W/K | **2.315 W/K** | 22.5 K | 5.0 % |
| K9 | 27.086 W | 1.806 W/K | 1.958 W/K | 13.8 K | 7.8 % |
| K10 | 21.587 W | 2.159 W/K | **2.455 W/K** | 8.8 K | 12.1 % |

**How 1.509 followed from 1.447 (16.1):** it is X2's need at 42.4 W of heaters, with the fans left out of P.

### 16.6 What one point closes, and what remains [11f]

**CORRECTED in section 17 (the review's B3): a dummy-load, mixed-air point closes only the conductance of its own
configuration, and no mode's functionality.** As first written, this subsection said one point "closes" REQ-024 and E3-A; it
meets only conductance screens:

**Met by one passing point** (lid open, the fans on, at the heat stage's heat: the heaters at 25.136 W plus the fans; a reading
of at least **1.958 W/K**):
- **K1, K3, K4:** the conductance screens of the heat stage at +40 C at the mixed air (the SGP41's Table 5 row, the +70 C class
  and the module's intake). The governing lines of REQ-024 and E3-A are section 17's.
- **K9:** the conductance screen of E3-O's +70 C class at its +55 C ambient margin.

**Closed only by a further measured point:**

| Id | The point | Reading needed |
|---|---|---|
| K5 | lid closed, the same heat | at least 1.958 W/K, lid closed |
| K6 | the profile's heat (REQ-014 at +20 C) | at least 1.508 W/K |
| K7, K8 | the profile charging (17.3's heat), plus the cells' own rise over the air (U-01's) | at least 1.889 and 2.315 W/K |
| K10 | the hold's heat in E5 | at least 2.455 W/K |

**Open:**
- **K2:** the SGP41 judged on Table 4 (the owner's CFL-002).
- **The part-level hot spots:** T-H2 and THM-001.
- **The fans' rating:** D-18, REQ-043.
- **Full sun:** D-02e, a later qualification item.
- **The cells on the pack at +40 C:** U-01, L4-E10.

### 16.7 The procedure [11g]

`T-H1-PROCEDURE-DRAFT.md` is revised to this section. In short:

**The points,** run in the order K1, K5, K10, K6, then K7 and K8 (one point, one heat, two needs). Each is set to the mode's heat
less the fans' measured draw. The heaters are READY-TO-ACT's 6.8 ohm (the nearest whole number of them), spread over the places in
proportion:

| Point | Heat | Heaters (fans) | Setting | Spread over the places (W, plan) |
|---|---|---|---|---|
| K1, K5 (and K9) | 27.086 W | 25.136 W (1.950 W) | one at 13.07 V | board B 14.972; board A 4.284; the front end and the charger 1.725; board C and the face 1.500; board D and the PA 1.500; board E 1.155 |
| K10 | 21.587 W | 19.637 W (1.950 W) | one at 11.56 V | board B 12.057; board A 3.903; board C and the face 1.500; the front end and the charger 1.345; board E 0.832 |
| K6 | 43.413 W | 40.443 W (2.970 W) | two at 11.73 V each | board B 26.234; board C and the face 7.500; board A 3.464; board D and the PA 1.500; board E 1.155; the pack 0.590 |
| K7, K8 | 52.134 W (17.3) | 49.164 W (2.970 W) | two at 12.93 V each | board B 26.234; board C and the face 7.500; the front end and the charger 6.620; board A 3.464; board E 3.245; board D and the PA 1.500; the pack 0.600 |

**Duration at each pass line.** The time constant is tau = C / G, with C = 10 kJ/K (32.53's upper bound for the kit, and so for
the empty case). A point is steady within 1 % of its rise at ln(100) tau, then an hour is averaged:
- K1 and K5: tau 1.42 h, steady at 6.5 h (the fit's three time constants, 4.3 h);
- K10: tau 1.13 h, 5.2 h (3.4 h);
- K6: tau 1.84 h, 8.5 h (5.5 h);
- K7: tau 1.47 h, 6.8 h (4.4 h), at 17.3's heat.

Section 17.4 replaces these points by one per mode's heat and lid state, with each mode's governing reading.

A case as poor as the bound takes up to 21.1 h a point.

**The endpoint**, either of:
- **steady state:** the mixed air drifts at most 0.1 K/h over an hour;
- **a transient fit:** a first-order fit theta(t) = theta_ss + (theta_0 - theta_ss) exp(-t/tau) over at least three time
  constants, with residuals at most 0.05 K RMS and tau within a factor 2 of C/G. Theta_ss's fitted standard error joins the
  rise's uncertainty.

**The verdict per point:**
- **Pass:** the reading less its expanded uncertainty is at or over the condition's need, i.e. the reading meets 16.5's
  threshold.
- **Fail:** it is under it.
- **Inconclusive** (the point is repeated): the endpoint is not met, or in the averaging hour the supply or a fan's draw moves by
  more than 1 %, or the ambient by more than 1 K.

**Authorisation and acceptance are separate.** Authorising the physical test (the bench, the people, the spend) is the owner's.
Accepting its result goes through the coordinator's check of the filed record against this section. No temperature requirement
is relaxed to make a point pass.

### 16.8 What this changes in sections 1, 13, 14 and 15

- **Section 15.5's first line is withdrawn as worded.** "1.509 W/K meets 1.447 W/K: the profile at +40 C" established only X2.
  Its 42.4 W left the fans out of P. The profile's own condition is K6, at REQ-014's +20 C (1.508 W/K at its own heat).
- **Section 15.1 and 15.5's charging needs are corrected, twice.** They took the profile's 43.413 W without the charge path; this
  round's 46.859 W still left out the source path's loss on the profile's own power. The balance of 17.3 gives 52.134 W, so the
  start line needs **1.810 to 2.200 W/K**, read at 1.889 and 2.315 W/K, and a running charge more (17.2).
- **The model findings of sections 14 and 15 stand.** The bound, the approaches and the shortfall are figures of the bound,
  not of the kit. The profile's ambient ceiling at +40 C (X1, 4.341 W/K) is not a requirement, because C1 sheds the profile there.
- **Section 13.4's E5 pass line is now read at E5's own heat.** It becomes 2.455 W/K at 21.587 W (heaters 19.637 W plus the
  fans), which replaces 2.416 W/K at one heater's 21.2 W.
- **Section 14.6's E3-O fallback lines were computed at 21.2 W.** Read at E3-O's own 27.086 W they are conservative: a lower heat
  gives a smaller rise, a lower G and a larger uncertainty.

### 16.9 Decisions taken by the session in this round (authority: SESSION)

| Decision | Why the session's | Reversed by |
|---|---|---|
| Each T-H1 point at its mode's heat, the heaters set to it less the fans' measured draw, P = heaters + fans | the owner's instruction to count the fans without double counting; the model gives the modes' heat | a measured fan draw differing from the model (the setting follows the measurement) |
| The room reading kept as the conservative side; no chamber required | the bound's model gives 1.6 to 3.7 % in its favour at +40 C, not material against U of 4 to 12 % | a chamber point at +40 C reading under the room's |
| The heaters' count the nearest whole number of READY-TO-ACT's 21.2 W heaters, one at 13.07 V for K1 | inside the heaters' 50 W class on their blanks; the places' spread can use one resistor per place instead | the heaters' maker's derating, once bought |
| Rittal's page cited, not filed | its copyright, read conservatively; only the relationship and the steel figure are quoted | the publisher's terms |

## 17. The fix round of the Layer 4 review (astra-check-l4close-1: B3, B4 and B7) [12]

The owner's one authorised review of the consolidation (`v2/docs/records/l4close/checks/astra-check-l4close-1.md`, set 27's
candidate `8fbb68b6`) read NOT YET. Three of its seven blocking items are this record's, and this section answers them:
- **B3:** the SGP41's rating and option C were misstated, and K1/K3 were component screens offered as closure criteria.
- **B4:** the charging heat left out the source path's loss on the running profile's power.
- **B7:** the battery-only 2.52 h was exempted from the thermal question.

The reviewer's own derivation (E2(a) to E2(d)) was used as a check, not copied, and the script reproduces its figures:
- 50.04367 W of charging heat, needing 1.7376 and 2.1115 W/K, read at 1.8135 and 2.2222 W/K;
- 2.063 h to C1 at a constant 0.6711 W/K, and 2.151 h at 0.7404 W/K;
- the bound's 0.598 to 0.661 W/K at +40 C.

Two readings differ from the review, each taken from the tree:
- **The gauge's charge thresholds.** TEST-PLAN gives T3 42 C (no charge starts above), T4 43 C (a running charge stops) and OTC
  44 C. The review's "42/45 C" pairs T3 with the 35E's +45 C, which is the cell's own charge limit.
- **The ballasts.** The design day's charge comes through the solar stage, so L4-E8's ballasts are added to the charging heat.

### 17.1 The SGP41 and option C, restated [12a]

**Sensirion's sheet separates function from survival.**
- **Table 4 (p.6), the recommended conditions:** operation to +50 C and storage 5 to 30 C. The gas sensing specifications hold
  only under these.
- **Table 5 (p.7), the absolute ratings:** operation to +55 C and short-term storage to +70 C ("Stress levels beyond those listed
  in Table 5 may cause permanent damage to the device").

So sensing is supported to +50 C only. The +55 C row is an exclusion screen and never stands in for the sensor's function.

**Option C of CFL-002 (section 8), as defined:**
- the part is kept;
- its channel is reported as not covered while its reference reads over 49.0 C, and after storage outside 5 to 30 C until
  Sensirion states otherwise;
- it is switched off at a 54.0 C reading, so it is never powered on the +55 C line;
- unpowered, its survival rests on Table 5's short-term storage row (absolute: INCONCLUSIVE until Sensirion, the clarification
  drafted).

**What is withdrawn:**
- Section 16's reading of REQ-024's acceptance as a +55 C inside-air limit "the SGP41 being a part with that published range".
- The use of K1 and K5 (1.806 W/K) as closure lines: they are screens.
- Section 16.6's "closes K1, K3, K4 and K9".

### 17.2 Every required mode, its local limits and its governing line [12a]

**How each mode is judged.** Each mode has its heat balance, its ambient and every correctly categorised local limit:
- **the cells:** at the air plus their own I2R over the pack block's lowest film (0.1481 W/K);
- **the control thresholds** whose firing ends or sheds the mode;
- **the parts at their local air,** the cooler's exhaust included;
- **the junctions,** with their modeled rise;
- **the unpowered parts:** their storage rows, or, where no storage row is held, their operating rows read to cover them
  unpowered (INFERRED).

The governing line is the tightest of them. Absolute ratings are listed as screens and never decide a line.

**Two bases:**
- **The design basis is the route's** (5b, 5c): the +70 C parts out of the running cooler's exhaust, the two regulators changed
  and the pushbuttons moved to an +85 C part.
- **"As designed"** (without those measures) is printed per mode in the `.out`. It differs only where the exhaust or the
  pushbuttons bind: at E3-O and E5 the as-designed ATP19 at the face has no conductance.

**The hot stop is a functional line inside the envelope.** A hot stop within the envelope fails the operating requirement (the
review's E2(a); E3-H), so H1 binds in M1 to M4 and in M5.

| Id | Mode | Heat into the case | Ambient, lid | Governing local limit as ruled (its category) | Needs | Bench reading | Under C, A or B | Needs | Bench reading |
|---|---|---|---|---|---|---|---|---|---|
| M1 | REQ-024 and E3-A at +40 C: C1's end state, the heat stage on the pack, the required set (REQ-052) | 25.536 W (the heat stage 23.272, the cells 0.174, the ballasts 2.090) | +40 C, open | the SGP41's sensing to Table 4's +50 C at its bay air (MAKER, recommended) | 2.554 W/K | 2.905 W/K | the cells' hot stop H1 at a +56.5 C reading, the cells 1.18 K over the air (CONTROL: ends the mode) | 1.666 W/K | 1.804 W/K |
| M2 | the same on shore (E3-A's 2 h), the pack idle | 27.086 W (23.272, the source path 1.725, the ballasts 2.090) | +40 C, open | the SGP41's Table 4 +50 C | 2.709 W/K | 3.081 W/K | the idle cells' hot stop H1 at +56.5 C | 1.642 W/K | 1.767 W/K |
| M3 | REQ-024 and E3-L at +40 C, the heat stage on the pack | 25.536 W | +40 C, closed | the SGP41's Table 4 +50 C | 2.554 W/K | 2.905 W/K | H1 | 1.666 W/K | 1.804 W/K |
| M4 | the same on shore | 27.086 W | +40 C, closed | the SGP41's Table 4 +50 C | 2.709 W/K | 3.081 W/K | the idle cells' H1 | 1.642 W/K | 1.767 W/K |
| M5 | REQ-014 at +20 C: PS-IDLE-SPEC on the pack, battery-only, unshed | 43.413 W (42.824, the cells 0.590) | +20 C, open | C1's inside-air +50 C (CONTROL: sheds the profile; the SGP41's Table 4 at the same +50 C) | 1.447 W/K | 1.508 W/K | the same | 1.447 W/K | 1.508 W/K |
| M6 | E3-O at +55 C, 4 h: the heat stage, every radio C1 leaves on, on shore, the cells kept out (TEST-PLAN's deviation) | 27.086 W | +55 C, open | the e-paper unpowered: only its +60 C operating row held (INFERRED) | 5.417 W/K | 7.758 W/K | the same | 5.417 W/K | 7.758 W/K |
| M7 | E5's +60 C dwell: the hold, logging, on shore, the cells kept out | 21.587 W (the hold 18.152, the source path 1.345, the ballasts 2.090) | +60 C, open | the e-paper unpowered (INFERRED) | no conductance (the limit at the ambient) | none | the same | none | none |
| M8 | charging on SC-37's design day, cold end: the profile running, the solar stage charging | 52.134 W (17.5) | +13.2 C, open | T4 on the charging cells: a running charge stops above 43 C, the cells 4.05 K over the air (CONTROL) | 2.025 W/K | 2.123 W/K | the same | 2.025 W/K | 2.123 W/K |
| M9 | the same, warm end | 52.134 W | +18.3 C, open | T4 on the charging cells | 2.525 W/K | 2.677 W/K | the same | 2.525 W/K | 2.677 W/K |

**Where an INFERRED line governs (M6, M7),** the maker-stated line beside it is:
- **E3-O:** the +70 C class at its local air (the RockBLOCK 9704 and the rest of section 4's class, MAKER operating), 1.806 W/K,
  read at 1.958 W/K.
- **E5:** the LimeSDR's +70 C storage row (MAKER storage), 2.159 W/K, read at 2.455 W/K.

That line governs once PDi states an unpowered range at or over +70 C.

**The other lines in each mode** (the `.out`'s 12a lists every one with the mixed air it allows):
- **M1 to M4:**
  - the cells' 35E +60 C, at 1.357 and 1.354 W/K;
  - the e-paper unpowered, at 1.277 and 1.354 W/K;
  - the +70 C class, at 0.851 to 0.903 W/K;
  - every other line needs less.
- **M5:**
  - C1's cell trigger, at 1.400 W/K;
  - H1, at 1.335 W/K;
  - the cells' +60 C, at 1.205 W/K.
- **M8 and M9:**
  - OTC, at 1.949 and 2.408 W/K;
  - the 35E's +45 C charge limit, at 1.879 and 2.302 W/K;
  - T3's start, at 1.810 and 2.200 W/K (K7, K8);
  - C1, at 1.417 and 1.645 W/K.
- **The SGP41, unpowered above its 54.0 C reading,** appears in every mode only as a screen (Table 5's +70 C short-term storage).

**What remains, per mode, beyond the conductance:**

| Mode | Remaining evidence condition |
|---|---|
| M1, M3 | T-H1's point at this heat in this lid state; the cells' own rise in the pocket (the block's film 5 to 15 W/m2K, the lowest taken; L4-E10, U-01); the gauge's reading error at H1 (`records/hc2/hotstop_bounds.out`; the thresholds PROVISIONAL, HOT-R1 owed on boards A and E) |
| M2, M4 | T-H1's point at this heat in this lid state; the idle cells at the air; the gauge's reading error at H1 |
| M5 | T-H1's point at the profile's heat; the cells' rise; the battery-only run's transient (17.6: on the bound C1 sheds the profile before its energy ends) |
| M6 | PDi's storage statement for the e-paper (drafted); the fitted pack at the margin is U-01's, since E3-O runs with the cells kept out (BAT-F19, CFL-017); the unpowered SGP41's short-term storage duration (Sensirion) |
| M7 | as M6, with no conductance meeting the e-paper's operating row at E5's +60 C; the parts the hold turns off, on their operating rows read to cover them unpowered until their makers state storage |
| M8, M9 | T-H1's point at the charging heat; the charging cells' rise over the air (U-01); the source path's efficiency (the model's 0.95 front end taken for the solar stage, INFERRED); a charge started under T3 cycles on T4 once the cells pass it |
| all | the parts' local air in the built kit (T-H2); the junctions' modeled rise (THM-001); the 33 lines cleared only by an absolute rating (section 7); the fans' rating (D-18); CFL-002 (the owner's) |

### 17.3 CFL-002, with C as defined [12a]

The options move the heat stage's line at +40 C as follows:
- **As ruled today** (no option taken; REQ-042's VOC channel sensing across the envelope): the SGP41's Table 4 +50 C governs the
  heat stage at +40 C. It needs 2.554 W/K on the pack and 2.709 W/K on shore, in either lid state.
- **Under C:** the channel is reported not covered above its 49.0 C reading and the sensor is off from 54.0 C. The line moves to
  the cells' hot stop H1: 1.666 W/K on the pack and 1.642 W/K on shore. The unpowered SGP41's survival stays a screen until
  Sensirion states its short-term storage duration. C restricts REQ-042's channel inside the envelope, which D-02a does not grant
  today.
- **Under A** (a BME688 in its place, gas sensing electrically operable to +85 C, its performance stated only to +40 C) **and B**
  (the channel dropped): the line is H1's, as under C. A also owes the BME688's gas performance above +40 C.

CFL-002 stays the owner's question. No option is taken here.

### 17.4 What a bench point closes, and the points [12a, 12d]

**What a bench point closes.** T-H1 is a dummy-load, mixed-air measurement:
- **It establishes** the conductance between the mixed air and the ambient for its own configuration (lid state, fan state and
  supply, heat, heat placement, room air), and the temperature offsets it records.
- **It closes no mode's functionality.** The cells' rise in the pack, the parts' local air in the built kit, the junctions, the
  hot stop's thresholds and every functional check of E3-A, E3-L, E3-O and E5 stay with their own evidence (U-01, T-H2, THM-001,
  E3-H).
- **Other states need their own points:** lid-closed and fans-off each need a point.
- **The translation is a model,** not a validation. 16.4's room-to-operating translation does not validate other fans, flow
  restrictions, lid states or heat placements.

**The points: one per heat and lid state, the fans on** (`T-H1-PROCEDURE-DRAFT.md`, revised):

| Point (modes) | Heat | Lid | Heaters (the model's fans) | Readings: as ruled / under C | tau at the lowest reading, steady at, the fit's three time constants |
|---|---|---|---|---|---|
| M2, M6 | 27.086 W | open | 25.136 W (1.950 W), one at 13.07 V | M2 3.081 / 1.767 W/K; M6 7.758 W/K (the stated line 1.958 W/K) | 1.57 h, 7.2 h, 4.7 h |
| M1 | 25.536 W | open | 23.586 W (1.950 W), one at 12.66 V | 2.905 / 1.804 W/K | 1.54 h, 7.1 h, 4.6 h |
| M4 | 27.086 W | closed | as M2 | 3.081 / 1.767 W/K | 1.57 h, 7.2 h, 4.7 h |
| M3 | 25.536 W | closed | as M1 | 2.905 / 1.804 W/K | 1.54 h, 7.1 h, 4.6 h |
| M7 | 21.587 W | open | 19.637 W (1.950 W), one at 11.56 V | none (the e-paper); the stated line 2.455 W/K | 1.13 h, 5.2 h, 3.4 h |
| M5 | 43.413 W | open | 40.443 W (2.970 W), two at 11.73 V each | 1.508 W/K | 1.84 h, 8.5 h, 5.5 h |
| M8, M9 | 52.134 W | open | 49.164 W (2.970 W), two at 12.93 V each | 2.123 and 2.677 W/K | 1.31 h, 6.0 h, 3.9 h |

**Then two more runs:** the fans-off case at M2's heat (no pass line: the failure case), and 17.6's transient point.

A point passes for a mode and an option when its reading meets that line. It closes that conductance only.

### 17.5 The charging heat as a balance (B4) [12b]

**What was wrong.** Section 11 added only the charge increment to the battery profile's heat (46.859 W), leaving out the source
path's loss on the profile's own power while it is supplied through the charger.

**The balance** on the model's boundary (pwr_budget: the charge path at 0.98 x 0.95 = 0.931; ICHG 3.0 A into the pack at 15.5 V):

| Term | W |
|---|---|
| input from the source: (42.824 + 46.5) / 0.931 | 95.944 |
| less stored in the cells: 46.5 less the charging cells' I2R 0.600 | 45.900 |
| less exported (the outlets) | 0.000 |
| **heat into the case** | **50.044** |
| = the profile at the battery node | 42.824 |
| + the source path's loss on it | 3.17382 |
| + the charge path's loss | 3.44629 |
| + the charging cells' I2R | 0.600 |

**With the solar stage.** The reviewer's 50.04367 W is reproduced. On SC-37's design day the charge comes through the solar stage,
so L4-E8's ballasts add 2.09 W at their worst corner (the margins' rule). The result, 52.134 W, is used in sections 10, 11 and 12a.

**K7 and K8** (T3's start, the idle cells at the air):

| Ambient | Heat | Needs | A reading of at least |
|---|---|---|---|
| +13.2 C | 50.044 W (the review's boundary) | 1.7376 W/K | 1.8135 W/K |
| +13.2 C | 52.134 W (with the ballasts) | 1.8102 W/K | 1.8892 W/K |
| +18.3 C | 50.044 W | 2.1115 W/K | 2.2221 W/K |
| +18.3 C | 52.134 W | 2.1997 W/K | 2.3150 W/K |

**A running charge needs more.** It is governed by T4 on the charging cells (17.2, M8 and M9): their own 0.600 W over the block's
film adds 1.35 to 4.05 K, the 4.05 K taken.

**E3-O's charge (section 2d) keeps the charge path's 3.446 W only.** The pack is outside the case there, and its cells' I2R with
it.

### 17.6 The battery-only run coupled to C1 (B7) [12c]

**The model (MODELED, energy-and-thermal):**
- PS-IDLE-SPEC on the pack (42.824 W at the pack, 43.413 W into the case) from a kit soaked at +20 C, lid open, shaded, still
  air.
- C1 moves the kit to the reduced mode at the inside air's +50 C. Its trigger still holds at the next reading, so the kit moves
  on to the heat stage (23.272 W at the pack, 23.446 W into the case). CONOPS states no dwell between the two; the model takes
  none.
- The reduced mode's restore, 5 K under the trigger, is not reached.
- The run ends on the 35E's usable 107.9 Wh at the profile's rate. The shed states' slightly larger usable energy is not
  credited.
- The cells are quasi-steady over the air, by their own I2R over the block's lowest film.
- One thermal node, C the kit's 8 to 10 kJ/K (32.53), integrated in 10 s steps on the enclosure model's own G(rise) (section 9,
  lid open).

**The reviewer's constant-G check, reproduced** (C 8 kJ/K):
- 0.6711 W/K reaches C1 at 2.063 h and, unshed, puts the air at 54.46 C at 2.52 h;
- 0.7404 W/K reaches C1 at 2.151 h.

| Enclosure | C | C1 acts at | The heat stage for | The run | The air at most | The cells at most (H1 at 56.5 C) |
|---|---|---|---|---|---|---|
| the bound | 8 kJ/K | 2.01 h | 0.94 h | 2.95 h | 51.21 C | 53.99 C, not reached |
| the bound | 10 kJ/K | 2.51 h | 0.01 h | 2.52 h | 50.02 C | 53.99 C, not reached |
| the coefficients' other ends | 8 kJ/K | 2.09 h | 0.79 h | 2.88 h | 50.41 C | 54.00 C, not reached |
| the coefficients' other ends | 10 kJ/K | not reached | none | 2.52 h | 49.33 C | 53.31 C, not reached |

**Energy-and-thermal (MODELED):**
- Where C1 acts, it sheds the profile from 2.01 to 2.51 h. The runtime with the shed states is then 2.52 to 2.95 h, of which
  2.01 to 2.51 h unshed.
- The profile runs its whole energy unshed only from a constant 0.960 W/K (C 8 kJ/K) or 0.630 W/K (C 10 kJ/K). It runs unshed
  for any duration from K6's 1.447 W/K.
- There is no hot stop on the bound.

**Energy only: 2.52 h** (107.9 Wh at 42.8 W) stays labelled energy-only. It is not an established unshed PS-IDLE-SPEC endurance.

**The bench runs that would show it:**
- **On T-H1's bench, a transient point.** The empty case is soaked at room temperature. The heaters are stepped to the profile's
  heat less the fans' draw (40.443 W) and, once the mixed air has risen 30 K, to the heat stage's battery-only heat less the fans'
  draw (21.496 W), logged to the run's end. This gives the time to C1 and the air after it. The empty case's thermal mass is
  under the kit's, which is the conservative side.
- **On the built kit (Layer 9), a battery-only run.** PS-IDLE-SPEC from a 24 h soak at +20 C, lid open, shaded, still air,
  logging the inside air at the hold's reference, the four cell thermistors, the gauge's energy and every C1 transition, to the
  graceful shutdown. This gives the runtime with its shed states, and shows whether the cells stay under H1.

Authorisation is the owner's; acceptance is the coordinator's check.

### 17.7 What this changes elsewhere

**In this record:**
- section 1 and section 16 (the +55 C line, the "closes" wording, K7 and K8);
- section 15's charging columns (now on 52.134 W: the best route short by 0.547 and 0.932 W/K);
- section 10e's readings (superseded by 17.4).

**Outside this record, on L4-E9's page** (the coordinator integrates; nothing outside this folder is edited here):
- `L4-POWER-ARCHITECTURE.md`:296, :313, :633 and :658 describe option C as keeping the sensor powered on the +55 C line;
- :302 carries 46.859 W;
- :317 exempts the battery-only run from the thermal question.

**In the findings ledger:** the rows L4-E12:2.1 and L4-E12:1.2 (the review's E6) rest on that reading.

### 17.8 Decisions taken by the session in this round (authority: SESSION)

| Decision | Why the session's | Reversed by |
|---|---|---|
| The hot stop H1 counts as a functional line inside the envelope | a hot stop within the envelope fails the operating requirement (the review's E2(a); E3-H's acceptance) | the owner's ruling on the hot stop's place |
| An unpowered part with only an operating row held is judged on it (INFERRED), so the e-paper governs E3-O and E5 until PDi states storage | the conservative reading of the corrected rule; the maker-stated line is printed beside it | PDi's storage statement |
| The charging heat on the design day carries L4-E8's ballasts (the solar stage runs) and the model's 0.95 front end stands for the solar stage | the margins' rule; no held solar-stage efficiency at this load | L4-E7's or L4-E8's efficiency figure; a measurement |
| The cells' rise over the block's lowest film (5 W/m2K) | L4-E10's conservative end | L4-E10's measured film (U-01) |
| C1's reduced mode moves on to the heat stage at once while the trigger holds | CONOPS states no dwell | the firmware's dwell, once stated |
| The battery-only run's usable energy is the profile's 107.9 Wh in every phase | the shed states' larger figure is not credited | none needed (conservative) |
| TEST-PLAN's T3 42 C, T4 43 C and OTC 44 C used for the charge, the 35E's +45 C as the cell's own limit | the tree's text governs over the review's "42/45" reading | TEST-PLAN's owner |

### 17.9 The outside capacity, and which lines a reading can pass at all (the addendum) [12e]

**The question.** The coordinator's addendum to this round: a T-H1 reading cannot exceed what the case's outside surfaces can pass.
Some of 17.2's lines are high, so each line needs a class:
- **(i):** reachable in the bare sealed case, so T-H1 decides;
- **(ii):** reachable only with the combined heat-rejection route fitted (section 15: R-170 fins, R-171 the large loads into the
  plate, R-172 the lid skin), so T-H1 with the route decides;
- **Over the modelled capacity even with the route and a perfect inside film.** The capacity is a model figure on the coefficient
  ends and heat paths named below, not a physical upper bound on every arrangement the rulings allow, so a line over it is not proof that
  no measurement can pass it (the review of the provisional fixes, L4-F04). It falls in one of three named categories, decided by
  the line's own property:
  - **MODELLED SHORTFALL OF THE ANALYSED ARRANGEMENT:** a held local limit over the analysed arrangement's modelled capacity,
    judged on the mixed air. An engineering task: a different heat path, or the part's local temperature measured apart from
    the mixed-air screen, may change it.
  - **MISSING STORAGE QUALIFICATION:** an unpowered part judged on an operating row read to cover storage (INFERRED). An
    evidence task: the maker's storage statement, or a storage soak of a sample with its function read back.
  - **DEMONSTRATED CONFLICT:** a measured local temperature over a mandatory limit with the route fitted. Only this category
    justifies asking the owner to change a requirement or a ruling. None at present: nothing is built or measured.

**The capacity.** It is computed with the inside resistance at zero:
- **Every inner face sits at the inside air,** and the 3 mm aluminium plate is taken as isothermal.
- **It is taken at each line's own ambient and rise,** in still air.
- **Bare:** the plate's outer face and the walls through the PP shell. With the lid closed, the path is the enclosed layer, the
  lid's shell and its outside films.
- **With the route:** fins of multiplier 2 (conservative) or 3 (optimistic) on the free strips' 0.0552 m2, adding 0.0552 to
  0.1105 m2 of effective outside area. The lid skin adds 0.0803 m2 on its 2.56 K/W strap. The large loads led into the plate add
  nothing once the inner faces sit at the air. The route acts with the lid open only: closed, the fins sit in the enclosed layer
  and the skin faces the plate, so the closed case is taken bare.
- **Coefficient ends:**
  - conservative: the plate's emissivity 0.70, the shell's 0.85, PP 0.12 W/mK, the plate's view 0.70, the floor adiabatic;
  - optimistic: 0.90, 0.95, 0.22 W/mK and 1.00, with the floor credited over a support at the ambient.

**A correction it brings.** Section 14's figures of 1.540 and 1.571 W/K (and 16.4's 1.504) were not the outside capacity. They
are the bound with a 50 m/s inside flow, whose film is near 45 W/m2K, not a zero inside resistance. The capacity proper is:
- 1.856 W/K at E5's rise and 1.906 W/K at E3-O's on the conservative ends;
- 1.810 W/K at K1's rise.

So E3-O's 1.806 W/K and K1 lie under it even on the conservative ends (14.4 and 16.4 corrected).

**The classes.** Each class is read at the optimistic ends (what physics may allow), with the conservative-end class beside it:

| Mode | Line | Needs | Capacity bare (cons. / opt.) | With the route (cons. / opt.) | Class (conservative ends) | Over the model: category and shortfall |
|---|---|---|---|---|---|---|
| M1 E3-A on the pack, open | the SGP41's Table 4 (as ruled) | 2.554 W/K at 10.00 K | 1.725 / 2.849 | 2.468 / 4.391 | (i) (over the model) | |
| M1 | the cells' hot stop H1 (C, A, B) | 1.666 W/K at 15.32 K | 1.815 / 2.969 | 2.594 / 4.589 | (i) ((i)) | |
| M2 E3-A on shore, open | the SGP41's Table 4 | 2.709 W/K at 10.00 K | 1.725 / 2.849 | 2.468 / 4.391 | (i) (over the model) | |
| M2 | the idle cells' H1 | 1.642 W/K at 16.50 K | 1.832 / 2.993 | 2.617 / 4.627 | (i) ((i)) | |
| M3 E3-L on the pack, closed | the SGP41's Table 4 | 2.554 W/K at 10.00 K | 1.335 / 2.279 | as bare | **over the model** | **MODELLED SHORTFALL OF THE ANALYSED ARRANGEMENT: 0.275 W/K, 2.749 W** |
| M3 | the cells' H1 | 1.666 W/K at 15.32 K | 1.385 / 2.356 | as bare | (i) (over the model) | |
| M4 E3-L on shore, closed | the SGP41's Table 4 | 2.709 W/K at 10.00 K | 1.335 / 2.279 | as bare | **over the model** | **MODELLED SHORTFALL OF THE ANALYSED ARRANGEMENT: 0.430 W/K, 4.300 W** |
| M4 | the idle cells' H1 | 1.642 W/K at 16.50 K | 1.395 / 2.371 | as bare | (i) (over the model) | |
| M5 REQ-014 at +20 C | C1's air trigger | 1.447 W/K at 30.00 K | 1.875 / 2.950 | 2.686 / 4.596 | (i) ((i)) | |
| M6 E3-O at +55 C | the e-paper's +60 C operating row, unpowered (INFERRED) | 5.417 W/K at 5.00 K | 1.704 / 2.915 | 2.429 / 4.462 | **over the model** | **MISSING STORAGE QUALIFICATION: 0.955 W/K, 4.775 W** |
| M6 | the +70 C class (maker-stated) | 1.806 W/K at 15.00 K | 1.906 / 3.181 | 2.714 / 4.904 | (i) ((i)) | |
| M7 E5 at +60 C | the e-paper's +60 C row | no room (the limit at the ambient) | none at a zero rise | none | **over the model** | **MISSING STORAGE QUALIFICATION: the whole 21.587 W** |
| M7 | the LimeSDR's +70 C storage row (maker-stated) | 2.159 W/K at 10.00 K | 1.856 / 3.144 | 2.642 / 4.831 | (i) ((ii)) | |
| M8 charging, cold end | T4 on the charging cells | 2.025 W/K at 25.75 K | 1.797 / 2.803 | 2.578 / 4.369 | (i) ((ii)) | |
| M8 | T3's start (K7) | 1.810 W/K at 28.80 K | 1.829 / 2.849 | 2.623 / 4.443 | (i) ((i)) | |
| M9 charging, warm end | T4 on the charging cells | 2.525 W/K at 20.65 K | 1.764 / 2.782 | 2.531 / 4.326 | (i) ((ii)) | |
| M9 | T3's start (K8) | 2.200 W/K at 23.70 K | 1.800 / 2.833 | 2.581 / 4.409 | (i) ((ii)) | |

**So T-H1 decides every line but four, and those four are not shown impossible.** Where a line is (ii), or over the model, only at
the conservative ends, the bare reading may fall short; the same point is then repeated with the route fitted (`T-H1-PROCEDURE-DRAFT.md` section 6).

**The four lines over the modelled capacity, by category** (none lowers a requirement silently; an option that changes a
requirement or a ruling stays the owner's and goes to him only when a measurement demonstrates the conflict).

**MODELLED SHORTFALL OF THE ANALYSED ARRANGEMENT: (1) E3-L at +40 C, lid closed, as ruled (M3 on the pack, M4 on shore).** The
SGP41's Table 4 +50 C sensing row, judged on the bay's mixed air, lies over the analysed closed case's modelled capacity (a model
figure on the coefficient ends above, not a physical bound).

| Option | Effect | Authority |
|---|---|---|
| a closed-lid conduction path, plate to the lid's inner face inside the seal (the combined route R-170 to R-172 carried to the closed lid) | not modelled here, so it closes nothing yet; it changes the analysed arrangement | the session's to develop (Layer 7) |
| the SGP41's local air measured at its port, apart from the mixed-air screen | the sensor's own temperature, not the mixed air, against Table 4's +50 C | the session's (a T-H1 channel) |
| CFL-002's C, A or B | the line moves to the cells' hot stop H1 (1.666 and 1.642 W/K), under the closed capacity's optimistic end and over its conservative one: T-H1's lid-closed point decides | the owner's, only if a measurement demonstrates the conflict |
| a closed-lid ceiling on REQ-042's VOC channel | on the model the bay air holds Table 4's +50 C lid closed only to an ambient of +31.3 to +38.8 C on the pack and +30.2 to +38.2 C on shore (conservative to optimistic) | the owner's (a requirement change), only if a measurement demonstrates the conflict |
| D-02b's closed-lid test at +40 C restated | E3-L's +40 C level with the VOC channel's state named | the owner's (a ruling change), only if a measurement demonstrates the conflict |

**MISSING STORAGE QUALIFICATION: (2) E3-O at +55 C (M6) and (3) E5's +60 C dwell (M7).** The unpowered e-paper is judged on its
+60 C operating row read to cover it (INFERRED); no storage row is held, so the shortfall is against an inferred limit, not a
demonstrated one. At E3-O it lies over the route's modelled capacity; at E5 the ambient equals that row, so no modelled capacity
and no plate fraction carries it.

| Option | Effect | Authority |
|---|---|---|
| PDi's storage statement | with a range at or over +70 C M6's line becomes the +70 C class, 1.806 W/K, class (i), and M7's the LimeSDR's +70 C storage row, 2.159 W/K, class (i) at the optimistic ends | the request is the session's (drafted, `clarification/pervasive-displays-e2370ks0c1.txt`); sending it is the owner's |
| a storage soak of a sample at the mode's temperature, its function read back after it | evidence for that lot, not a maker's range | the session's (a bench item) |
| the e-paper's own temperature at its window in the plate, measured (M6) | a local temperature apart from the mixed air: at the bound's plate fraction 0.362 it needs 1.963 W/K, at W4's high 0.725 it needs 3.926 W/K, both under the route's optimistic capacity: the measured fraction decides | the session's (a T-H1 channel at the window) |
| an e-paper with a held range at or over +70 C | the line becomes the +70 C class | the owner's (CHO-001), only if a measurement demonstrates the conflict |
| E3-O or E5 run with the e-paper's state recorded as a deviation | the margin's acceptance restated for that part | the owner's (TEST-PLAN), only if a measurement demonstrates the conflict |

**DEMONSTRATED CONFLICT: none at present.** A line enters it only on a measured local temperature over a mandatory limit with the
route fitted; no part of this kit is built or measured.

**Charging lies under the modelled capacity (class (i)).** For scale only: charging solely in the heat stage would put 31.133 W into the case and need 1.209
and 1.508 W/K at T4's line, class (i) at both ends. That would cost the profile's service while charging, against the 48 to
72 h DESIGN OBJECTIVE that is already NOT MET. It is the owner's choice of duty cycle, and is not taken.

| Decision (authority: SESSION) | Why the session's | Reversed by |
|---|---|---|
| The capacity taken with the inside resistance at zero, the plate isothermal and still air | the coordinator's definition; still air is the conservative environment | a measured outside film |
| The class read at the optimistic ends, the conservative-end class printed beside it | a line is put over the model only where no coefficient end in the held ranges carries it on the analysed paths | none needed |
| A line over the modelled capacity is put in a named category by its property (MODELLED SHORTFALL OF THE ANALYSED ARRANGEMENT, MISSING STORAGE QUALIFICATION, DEMONSTRATED CONFLICT), never called a line no reading can pass | the review of the provisional fixes (L4-F04): the capacity is a model figure on chosen coefficients and paths, an INFERRED storage reading is not a demonstrated limit, and only a measured local temperature demonstrates a conflict | a measured local temperature over a mandatory limit with the route fitted (then DEMONSTRATED CONFLICT, the owner's) |
| The route not credited with the lid closed | its fins and skin act on the open lid | a closed-lid route, modelled |
