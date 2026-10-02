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
`checks/astra-check-l4e12-1.md` and `checks/astra-check-l4e12-2.md`; `T-H1-PROCEDURE-DRAFT.md` (section 13); `README.md`. The tests: `env -C v2/ecad/tools/tests python3 run.py test_l4e12
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
