# L4-E12: the kit's electronics against the inside air at D-02a's +55 C margin and E5's +60 C dwell (U-02)

MESHSAT-1478 under MESHSAT-1357, layer 4 task L4-E12, 2 October 2026, revised the same day after the collaborator's focused
check (`checks/astra-check-l4e12-1.md`, NOT YET on B1 to B3; section 12 maps each item to its change). **Prototype design,
desk arithmetic: nothing has been bought, built, powered or measured, and no kit has been field deployed.** Every figure
comes from `l4e12_thermal.out` (the script `l4e12_thermal.py` reproduces it byte for byte, pins 63 inputs by sha256 and
reproduces `records/rv-pwr/pwr_budget.out` and `records/hc2/pwr_red2.out` before any figure) and carries its class: MAKER (a
maker's document, page named), MODELED (the tree's power and thermal model and W4's lumped film coefficients), INFERRED (method
stated), ASSUMPTION (a figure no held document gives), CONDITIONAL (holds only on a stated condition). Section numbers in
brackets point to the `.out`.

## 1. The answer in short

- **The finding, part by part.** At T-H1's floor (LO-01a's 1.6664 W/K, reproduced, [2b]) the heat stage's 24.996 W and L4-E8's
  ballasts (2.09 W, +1.254 K) put the mixed inside air at **71.25 C in E3-O and 76.25 C in E5's dwell** (MODELED, [2c]). Judged
  by the corrected rule (powered parts on their operating ranges, absolute maxima only as exclusion screens, [1j]), the screen
  of every fitted line, module and undeclared line [3] finds at E5: the RockBLOCK 9704, the SA868 and its PCM2912A codec and
  G6K relay, the LimeSDR and the H5007NL past +70 C by 6.3 K at the mixed air (11.9 K in the running cooler's exhaust); the SGP41
  past its +55 C by 21.3 K; the MAIN pushbutton (ATP19) past +55 C by 12.6 to 21.3 K; the e-paper past its only stated +60 C by
  7.6 to 16.3 K; board E's and board C's TLV75533 regulators past their recommended +125 C junction; the PI and TEST
  pushbuttons and the sealed USB-C at +70 C in their plate-to-air span.
- **A route that conforms to the stated acceptance exists, CONDITIONAL [5].** E3-O runs exactly as TEST-PLAN states it: deployed, monitor and radios on,
  C1's shedding the one control action; every radio C1 leaves on stays on for the four hours. Its heat (27.086 W with the
  ballasts) holds the mixed air at or under +70 C from **1.806 W/K**. E5 requires logging, not the radios, so the hold acts in
  E5 only; under it 21.587 W need **2.159 W/K, the binding line** (2.709 W/K if the hold is not used). At 2.159 W/K E3-O's mixed
  air is 67.55 C and E5's 70.00 C.
- **The hold's trigger window [4d].** Between E3-O's steady 67.55 C and the 70.00 C by which E5 needs the hold the window is
  2.45 K; less the reference's error twice (TMP117 +-0.2 C, MAKER) and 0.25 K of lag, the reference may sit at most +-0.90 K
  from the air at the +70 C parts. The TMP117 is a board sensor under the coolers: across the exhaust's 0 to 5.64 K the window
  does not exist (it would need 3.111 W/K). It exists only with a reference placed in the mixed air near those parts or
  calibrated at T-H1 to +-0.90 K: CONDITIONAL.
- **The SGP41's own shutdown [5d]**, apart from the hold: off at 53.75 C read by board E's BME688 beside it (+-0.5 C, MAKER,
  within 0.5 K and 0.25 K of lag), on again at its Table 4 maximum of 50 C, off at every start until it reads 50 C; E3-O, which
  starts from a kit at +55 C, never powers it. Its function holds inside the envelope at the line (52.55 C bay air, 0.20 K to
  spare). Unpowered it sits at 67.55 C (E3-O) and 70.00 C (E5) against its +70 C short-term storage, whose duration Sensirion
  does not state: CONDITIONAL on its answer and on a supply switch and a bus of its own.
- **Approach (a), the enclosure alone, is not rejected but not selected**: 2.709 W/K lies over the low case's outer-film cap
  (2.10 W/K) and under W4's high case (2.85 W/K, 3.86 with an infinite inside film); it is what applies, with no hold, if T-H1
  reads at or over it. **(b), wider-rated parts**, is not selectable by the session (five device-set parts, CHO-001).
- **No owner question is forced** [6]: no part has every route rejected on held evidence. The ATP19 and the e-paper are
  conditional future closures (the session's pick; PDi's statement), not closed. The question would be forced only if T-H1 read
  under 1.806 W/K and the radios could not be coupled to the plate in E3-O (section 8 gives the two options then).
- **U-02 stays CONDITIONAL**, on: T-H1 lid open with fans at or over 2.159 W/K; the hold's reference placed or calibrated to
  +-0.90 K; the SGP41's shutdown (placement, switch, bus, Sensirion's duration); the MAIN, PI and TEST pushbuttons picked to
  +85 C; PDi's storage statement; the two 3.3 V regulators changed; the +70 C parts out of the running cooler's exhaust; the
  fans' rating (architecture-level) and ten other lines with no range held (downstream). The sealed case and the power path's
  topology stay.

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

**Which limits apply (the corrected rule, SESSION, [1j]).** A powered part: its maker's recommended or operating range,
whether it must work in the exposure (the CM5, the logging chain, the fans, the radios in E3-O) or is merely powered. An
absolute maximum is a stress rating only (PCM2912A SLES230A p.5: "These are stress ratings only, and functional operation of
the device at these or any other conditions beyond those indicated under Recommended Operating Conditions is not implied";
TLV755P p.4 separates its +150 C absolute junction from its +125 C recommended one): it serves as an exclusion screen, never as
a statement of no damage. A powered part past its operating range and under its absolute maximum is INCONCLUSIVE unless its
maker states recovery (the RM520N's extended range, hardware design V1.1 p.19, "without any unrecoverable malfunction ...
When the temperature returns to the normal operating temperature level, the module will meet 3GPP specifications again"). An
unpowered part: its storage range where stated, else its operating range, the only statement held; a duration the maker does
not state stays open. A part through the plate or the wall is bounded by the plate and the inside air (its rear).

## 3. The thermal state at the margins [2]

| Quantity | Value | Class |
|---|---|---|
| The heat stage after BANK-R1 on shore, plan, into the case | 24.996 W (23.272 W at the pack); as generated 23.345 W; HIGH 50.423 W, not covered (as L4-E10 and LO-01a) | MODELED |
| T-H1's floor: the SGP41's +55 C (Table 5, p.7) at +40 C on shore | 1.6664 W/K; L4-E10's 1.6664 W/K, 70.00 and 75.00 C reproduced | MAKER, MODELED |
| L4-E8's ballasts at the bound's worst corner | 2.09 W, +1.254 K | MODELED by L4-E8, cited from L4-E9 IF-08 |
| Mixed inside air at the floor, E3-O / E5's dwell | 71.25 / 76.25 C (steady; E3-O's 4 h from a kit at +55 C reaches 69.78 to 70.44 C at 32.53's 10 to 8 kJ/K) | MODELED |
| A charge running on shore | +3.446 W, +2.07 K; E3-O states no charge state, the route counts none (TEST-PLAN's owner records it) | MODELED |
| The plate at the ambient plus, of the rise | 0.465 to 0.725 (W4's films: inside 10 to 25, face 9.5 to 11.5 W/m2K) | INFERRED |
| The enclosure, lid open with fans (W4: a sensitivity estimate, not a model of the kit) | W4 1.22 (low case) to 2.85 W/K (high case); 32.53 3.0 to 3.3; outer films alone 2.10 W/K (low case) to 3.86 W/K (high case), a cap of the low case's coefficients and areas, not a universal bound | INFERRED |
| The running module's cooler exhaust over the mixed air | +5.64 K in the heat stage (4.5 W), +2.78 K in the hold (2.0 W idle): the 30 mm fan's 3.7 CFM (Sunon p.1) at 50 % through the heatsink | MAKER, MODELED, ASSUMPTION |
| E3-O as designed | ambient 55.0; mixed 71.25; exhaust 76.89; plate 62.6 to 66.8 C | MODELED, INFERRED |
| E5 as designed | ambient 60.0; mixed 76.25; exhaust 81.89; plate 67.6 to 71.8 C | MODELED, INFERRED |

## 4. The feasibility screen, by the corrected rule [3]

Every fitted line on boards A to E (150 lines of `v2/docs/parts/grade_check.py`'s build, run without writing), the 19 modules
and the 10 lines no grade row covers (read from TI's sheets) are screened; board P and the cells are outside the chamber in
E3-O and E5 (TEST-PLAN's deviation) and stay FEA-008's. **As designed, at E5: 141 NOT REACHED, 9 REACHED, 6 PLACEMENT, 12
INCONCLUSIVE, 7 out of scope, 4 no part or not fitted; at E3-O: 145, 10, 2, 11, 7, 4.** Junction-rated parts carry their own
rise: the converters and LDOs from the model's losses and the makers' thetaJA, judged against their recommended junction
(the absolute one an exclusion screen); signal, protection and pass parts by stated class bounds (ASSUMPTION: 20 mW at 250
C/W, 0.25 W at 60 C/W, controllers 0.5 W).

The parts read one by one (state: work, powered and required; on, powered; off; limits MAKER; local temperatures MODELED
inside, INFERRED at the face and wall):

| Part | State E3-O / E5 | Limit by the rule, document, page | E3-O local / gap | E5 local / gap | Credible way to close |
|---|---|---|---|---|---|
| RockBLOCK 9704 (device set) | work / on | +70 C operating, the only range (Ground Control spec page) | 71.3 to 76.9 C / 1.3 to 6.9 K over | 76.3 to 81.9 C / 6.3 to 11.9 K over | the air at or under +70 C at its place (the line; out of the exhaust) |
| SA868 (device set) | work / on | +70 C working, the only range (Rev 1.3 p.4) | as above | as above | as above |
| PCM2912A (board D U6) | work / on | +70 C recommended (p.5); +125 C absolute, a screen | as above | as above (INCONCLUSIVE: powered, not required) | as above; off under the hold in E5 (storage +150 C) |
| Omron G6K-2F-Y (board D K1) | work / on | +70 C ambient operating (p.3) | as above | as above | as above; an +85 C relay for margin (Layer 6) |
| LimeSDR Mini 2.4 (device set) | off / off | +70 C storage (maker's page: commercial grade only) | as above | as above | the air only |
| Pulse H5007NL (board B T1) | on / on | +70 C operating (p.1) | as above | as above | the air; the maker's HX version (-40 to +85 C, p.1; pinout owed) |
| SGP41 (device set) | on / on | +55 C operating, Table 5, its only powered statement (p.7) | 16.3 to 21.9 K over | 21.3 to 26.9 K over | its own shutdown; unpowered, +70 C short-term storage (p.7) |
| ATP19 MAIN | on / on | +55 C operating (p.1) | 7.6 to 16.3 K over | 12.6 to 21.3 K over | a sealed pushbutton to +85 C (NKK MBN, p.3) |
| PDi e-paper (device set) | off / off | +60 C operation, the only range (flyer p.1; no storage stated) | 2.6 to 11.3 K over | 7.6 to 16.3 K over | its maker's storage range (drafted); no refresh past it |
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
returns its input to the air, L4-E10's corrected balance): the SGP41's own shutdown; the MAIN, PI and TEST pushbuttons to a
+85 C part; PDi's storage statement; the two regulators; the +70 C parts out of the running cooler's exhaust; the fans and the
other lines with no range held.

| | (a) heat path and enclosure | (b) wider-rated parts | (c) SELECTED: E3-O as stated, the hold in E5 only |
|---|---|---|---|
| What it is | the heat stage at both margins, the radios on at both; the inside air lowered by the enclosure (inside fins on the plate, mixing), or the +70 C modules coupled to the plate | every colliding part replaced by one rated to +85 C; the mode and the enclosure unchanged | E3-O: the heat stage with every radio C1 leaves on; E5: beyond the heat stage the charge held, the module idled, board D, the PA rail, RockBLOCK, LoRa, both E72 and Geiger off |
| Heat (MODELED) | 24.996 W at both | 24.996 W at both | 24.996 W in E3-O; 19.497 W in E5 (18.152 W at the pack) |
| Enclosure line (MODELED) | 2.709 W/K (3.010 at 1 K, 3.386 at 2 K); E3-O alone 1.806 W/K | the floor, 1.6664 W/K | **2.159 W/K**, set by E5 (2.399 at 1 K, 2.698 at 2 K; 2.443 with the module at 4.5 W; 4.304 at HIGH); E3-O alone 1.806 W/K |
| Against the physics | over the low case's cap (2.10), under W4's high case (2.85): CONDITIONAL on T-H1 | the inside air at 76.25 C (81.89 in the exhaust) leaves +85 C parts 3.1 to 8.8 K | 0.058 W/K over the low case's cap, inside W4's range and under 32.53's: CONDITIONAL on T-H1 |
| Configuration | E3-O and E5 as stated | as stated | E3-O as stated; E5's radios off (E5 requires logging only); a trigger window that exists only with a placed or calibrated reference |
| Changes | mechanical | five device-set re-picks (the owner's), four with no candidate held | firmware on existing enables (RB_SW_EN, LORA_ON, ZB_ON, GEIGER_EN, board D and the PA as H1 does); the hold's reference |
| Evidence owed | T-H1 at 2.709 W/K or more | makers' sheets for four device-set parts | T-H1 at 2.159 W/K or more; the reference's offset to +-0.90 K |
| Verdict | CONDITIONAL; not selected (0.55 W/K over (c)); applies alone if T-H1 reads at or over 2.709 W/K | not selectable by the session | SELECTED, CONDITIONAL |

Per colliding part [4f]: (a) and (c) CONDITIONAL for the +70 C class, the SGP41 (by its own shutdown), the ATP16 and the
USB-C; REJECTED for the ATP19 (in circuit at +55 C, under the ambient); INCONCLUSIVE for the e-paper (no storage range held).
(b) CLOSES for the ATP19, the ATP16, the H5007NL and the USB-C; OUTSIDE AUTHORITY for the five device-set parts; INCONCLUSIVE
for the relay and the codec. No part has every route rejected.

## 6. The selection: (c), with its margins [5]

**E3-O.** The heat stage with every radio C1 leaves on, no hold: at the line its mixed air is **67.55 C** (73.19 C in the
running cooler's exhaust); the RockBLOCK, the SA868 chain and the H5007NL work 2.45 K inside +70 C at the mixed air, so they
must sit out of the exhaust (Layer 9). E3-O alone would hold from 1.806 W/K.

**E5.** The hold: its heat 19.497 W (as board B is generated, the 5G socket's supply dropped too, 19.497 W); at the line the
mixed air settles at **70.00 C** with the radios off, inside the +70 C class's only statements at 0 K; 2.78 K more in the idle
module's exhaust (placement again).

**The hold's trigger window [4d] (SESSION, PROVISIONAL).** Window 2.45 K of mixed air between E3-O's steady 67.55 C and E5's
need at 70.00 C; less the reference's error twice (TMP117, +-0.2 C to 100 C, MAKER p.1) and 0.25 K of lag (E5's chamber at 15.0
K/h times a 61 s reading and response, ASSUMPTION), the reference may sit at most **+-0.90 K** from the air at the +70 C
parts. Across the exhaust's 0 to 5.64 K spread the window is -3.84 K: **it does not exist** with the TMP117 left where it is;
it would need 3.111 W/K. With a reference placed in the mixed air near those parts, or the TMP117's offset calibrated at T-H1
to +-0.90 K, the trigger sits at the window's middle, **68.65 C** of mixed air plus the calibrated offset, restored 5 K under it
after 30 minutes. The window widens with the conductance (4.17 K at 2.5 W/K; 5.00 K at 2.709 W/K, where no hold is needed).
Inside the envelope the air at the line is 52.55 C, far under it. Actions: the charger's charge-inhibit bit and board D and the
PA rail off through board A's expanders (as H1 does); the RockBLOCK, the LoRa module and both E72 off through their software
enables (U503 RB_SW_EN, U504 LORA_ON, U505 ZB_ON); the Geiger module off (U16, GEIGER_EN); the running module idled, its
logging kept; an SOS raised meanwhile is queued as under EMCON (D-10) and the operator told.

**The SGP41's own shutdown [5d].** Board E's BME688 (U14, +-0.5 C from 0 to 65 C, MAKER p.14), placed beside the SGP41 within
0.5 K (ASSUMPTION, a Layer 9 placement rule), switches its supply off at **53.75 C** (its +55 C less the error, the gradient and
0.25 K of lag) and back on at 50 C (Table 4's recommended maximum, MAKER p.6); the switch is off at every start until a reading
at or under 50 C, so E3-O, which starts from a kit at +55 C, never powers it. Its function is kept for any bay air up to 52.75
C; inside the envelope at the line the air is 52.55 C (0.20 K to spare); at T-H1's floor it would be 56.25 C and the function
would be lost at the hot edge (finding 1 fails that floor anyway). Unpowered it sits at 67.55 C in E3-O and 70.00 C in E5
against its +70 C short-term storage, whose duration Sensirion does not state (drafted request): CONDITIONAL. The circuit
(board E, owed to its generator owner, no draft: the generator needs KiCad's libraries): a TPS22810 load switch (the part board
E already uses for the Geiger) feeding a new +3V3_SGP from +3V3_E6, enabled from U10's free GPIO20 (QFN pin 31) with a 100k
pull-down; the SGP41's VDDH and R57's input on +3V3_SGP; its SDA and SCL moved to GPIO21 and GPIO22 (pins 32 and 34) with 4.7k
pull-ups to +3V3_SGP, so that with the switch off no live bus feeds it through its pins (the firmware runs that bus by PIO and
floats it before switching off).

**The regulators [5c].** Recommended junction +125 C (TLV755P p.4): board E's U13 at the model's plan 0.258 W reaches 127.1 C
(E3-O) and 129.5 C (E5) in SOT-23-5 (231.1 C/W) and 93.4 and 95.8 C in the DRV package (100.2 C/W, the same sheet); at its
rail's declared 0.35 A neither package holds (the DRV part takes at most 0.323 A at E5's air), so a buck, or the rail's load
re-derived. Board C's U5 at its declared typical: 126.1 and 128.5 C in DBV, 92.9 and 95.4 C in DRV. Owed to boards E and C's
generator owners (the DRV land is the WSON-6 board E already uses).

**The pushbuttons.** MAIN (ATP19, +55 C) and PI, TEST (ATP16, +70 C) to a sealed pushbutton whose maker states +85 C: NKK MBN
(IP67, -30 to +85 C, p.3, held), its 12 mm bushing, terminals and cutout owed (Layer 6, 7, 8). The ATP19's IK10 rating is not
matched by the MBN's sheet: a named consequence. Until picked, the ATP19 stays REACHED.

**At the line, every line:** 147 (E3-O) and 148 (E5) NOT REACHED; 7 and 6 PLACEMENT (the +70 C class and the SGP41 at the mixed
air, over only in an exhaust); 3 REACHED at each (the ATP19 and the e-paper, conditional future closures by the pick and PDi's
statement, and the TLV75533 line, closed by the regulator change); 11 INCONCLUSIVE (no range held).

## 7. What stays CONDITIONAL, and what could overturn it

- **T-H1 lid open with fans at or over 2.159 W/K** (E5 with the hold); 2.709 W/K with no hold; 1.806 W/K for E3-O alone. The line
  lies over the low case's outer-film cap (2.10 W/K): at W4's low coefficients no inside fin reaches it. If T-H1 reads between
  1.806 and 2.159 W/K, E3-O still holds and E5 needs the fallback: the radio modules and the LimeSDR coupled to the plate (E5
  plate 66.0 to 69.4 C under the hold at the floor, 0.61 K inside +70 C, INFERRED), the HX magnetics, Bulgin's +80 C, and the
  SGP41, which in the bay air (72.95 C) is past its storage: that branch needs the owner's re-pick (CHO-001), the candidate a
  second BME688 at I2C 0x77, which the outside pod's BME688 (32.54, deferred) then cannot share.
- The hold's reference placed in the mixed air or calibrated to +-0.90 K, and the hold forced at room temperature.
- The SGP41's shutdown (placement within 0.5 K, the switch, the bus, Sensirion's duration); the pushbuttons; the regulators;
  PDi's statement; the placement out of the exhaust.
- **The fans** (D-18): they carry the inside film every conductance here assumes; unrated, they are architecture-level (a fan
  that stops at the margin takes the enclosure to W4's fans-off 0.77 to 1.57 W/K and every margin with it).
- The plan heat: the line is 2.443 W/K with the module at its typical 4.5 W and 4.304 W/K at HIGH; the bench's E3-O and E5
  power readings replace the plan figures. The class bounds of the screen.

## 8. The owner-question test [6]

No part collides under every approach on held evidence: the ATP19 closes by the session's pick; the SGP41 by its own shutdown
(CONDITIONAL); the +70 C class by the air at the line and placement; the e-paper's route rests on a statement PDi has not
published in a held document, a component limitation, not a requirements conflict. **No owner question is forced.**

Not asked, named for completeness: it would be forced only if T-H1 read under 1.806 W/K and the radio modules could not be
held at or under +70 C in E3-O by coupling them to the plate (whose E3-O temperature at the floor is 62.6 to 66.8 C, 3.22 K
inside +70 C at its upper fraction, INFERRED). Then the conflict would be E3-O's configuration (TEST-PLAN line 26: four hours
at +55 C with the monitor and radios on) against the +70 C operating ranges of the device-set radios; Option 1: keep E3-O's
configuration and leave U-02 open, the radios' re-pick or a better heat path owed; Option 2: approve the hold's shedding in
E3-O as a stated deviation (four hours at +55 C, CM5 not shut down and logging, no damage, recovery kept), which closes E3-O at
T-H1's floor (the hold's mixed air 67.95 C) but reports the radios' margin result as a deviation.

## 9. Downstream items (owner by layer; acceptance)

| Owner | Item | Acceptance |
|---|---|---|
| Layer 4 coordinator | U-02's line on T-H1 (lid open, fans: 2.159 W/K; 2.709 with no hold; 1.806 for E3-O) beside LO-01a's; LO-01a's floor with L4-E8's ballasts is 1.8058 W/K (finding 1); L4-E10's conditioned corner moves with the line | the gate's IF-11 and U-02 rows restated on this record |
| Layer 2 and 5 integrators, firmware owner | the hold as a mode for E5's case beyond the envelope (CONOPS 4, HW-FW-CONTRACT): trigger at the window's middle with the calibrated offset, restore, actions, enables, the SOS queue; the SGP41's own shutdown | a forced hold and a forced SGP41 shutdown at room temperature; E3-O and E5 |
| TEST-PLAN's owner | E3-O unchanged; E5's arrangement records the hold beside C1; E3-O's record names the SGP41's own shutdown; E3-O starts from a kit stabilised at +55 C; the pack's charge state at E3-O's start; a forced-hold row like P15; T-H1 reports the plate and wall fractions and the hold reference's offset | the plan's revision |
| Layer 6 components | MAIN, PI, TEST pushbuttons (NKK MBN class, +85 C); the H5007NL's HX version (pinout); an +85 C T/R relay (margin); Bulgin's answer; the NVMe wide grade; the lines with no range held (below) | each maker's range at or over its local temperature at the line (section 6) |
| Layer 6, architecture-level | **the IP68 fans (D-18)**: a maker's operating range reaching the mixed air at the line (70.0 C in E5) with margin | a held sheet; T-H1 with the picked fans |
| Layer 6, downstream | the CR2032 cell and its holder, the QMX (in the lid, at the ambient; the owner's device set, an owner item only if its maker states less than the ambient), the header modules, the panel LEDs, the headset jacks, J_HDMI, the pin headers, the fuse holders, the pre-charge pin: each range read | a held sheet per line |
| Layer 7 mechanical | the enclosure to T-H1's 2.159 W/K (inside fins on the plate, mixer flow); the fallback plate coupling; the MBN cutouts | T-H1 |
| Layer 8, board E's generator owner | the SGP41's switch and bus; U13: a buck, or a DRV-package LDO with the rail's load re-derived under 0.323 A | board E's suite; U13 under +125 C junction at the line's air |
| Layer 8, board C's generator owner | the pushbuttons; U5 to the DRV package; U5's declared 0.72 A peak against 500 mA | board C's suite |
| Layer 9 pre-layout | the +70 C parts and the SGP41 out of the running cooler's exhaust; the BME688 within 0.5 K of the SGP41; the hold's reference in the mixed air near the +70 C parts; the class bounds replaced | the placement review |
| Prototype bench | T-H1 in both lid states with the plate, wall and reference thermocouples; E3-O and E5 with thermocouples on the RockBLOCK, SA868, LimeSDR, H5007NL, SGP41, e-paper, plate and the hold's reference | each TEST-PLAN pass line; section 3's model replaced by the measured conductance |
| Owner (outside contacts) | send PDi's and Sensirion's requests (the route needs them); Ground Control's, NiceRF's and Bulgin's are drafted for the fallback | the answers filed |

## 10. Decisions taken by the session (authority: SESSION, under the owner's standing rule of 26 September 2026)

| Decision | Why the session's | Reversed by |
|---|---|---|
| The corrected rule of section 2 (operating ranges for powered parts; absolute maxima as exclusion screens; storage, else the only range held, for unpowered parts) | the makers' own words on their absolute ratings; the check's B2 | a maker's statement of recovery, or the owner's reading of D-02a |
| E3-O kept exactly as stated; the hold only in E5 | E3-O names the radios on; E5 requires logging only | the owner, if he approved a deviation (section 8) |
| The SGP41's own shutdown is inside E3-O's configuration | the row names the monitor and radios, not the sensor; no function is required during the margin | TEST-PLAN's owner reading the row otherwise |
| (c) selected; (a) not selected; (b) not taken | (c) needs the least conductance within the session's authority; (a) needs 0.55 W/K more; (b) is the owner's | T-H1's reading, or the owner's re-picks |
| The hold's trigger at the window's middle, restore 5 K under (PROVISIONAL); the reference's offset bound +-0.90 K | the window's own arithmetic | the bench (T-H1, the forced hold) |
| The SGP41's thresholds 53.75 C off, 50 C on; the BME688 as the reference | its +55 C less the error, gradient and lag; Table 4's maximum | the bench |
| The regulators changed (DRV or a buck) | an engineering change of a part within the session's authority | the generator owners |
| The e-paper's gap left to PDi's statement, not escalated | a missing statement is a component limitation (the owner's rule) | PDi's answer |
| No generator draft | the changes need footprints and a KiCad run the runner cannot do; a specification is given | the generator owners |

## 11. Files

`l4e12_thermal.py` and `.out`; `fetch_held_back.py` (TI's TLV755P sheet into the ignored `v2/vendor/ti/held/`, sha256
44ac688d7e51f852...); `clarification/` (PDi, Sensirion, Ground Control, NiceRF, Bulgin; drafts for the owner to send);
`checks/astra-check-l4e12-1.md`; `README.md`. The tests: `env -C v2/ecad/tools/tests python3 run.py test_l4e12
test_public_hygiene`. No generator, BOM, registry, interface or Layer 3 file is changed.

## 12. The focused check, and what each item changed

| Item | Change, and its effect on the numbers, margins or verdict |
|---|---|
| B1 (configuration without authority) | withdrawn: the "started with" reading and the claim that the acceptance permitted extra shedding in E3-O. E3-O now runs as stated (every radio C1 leaves on stays on); its heat is the heat stage's 27.086 W with the ballasts, held at or under +70 C from 1.806 W/K (the coordinator's 1.81 confirmed); the hold acts in E5 only, inside a trigger window bounded at 2.45 K (+-0.90 K for the reference) that does not exist with the TMP117 across the exhaust's spread. Binding line unchanged at 2.159 W/K (E5), now CONDITIONAL on the reference as well. Material |
| B2 (the rating rule) | absolute maxima are exclusion screens; powered parts judged on their operating or recommended ranges; survival past them INCONCLUSIVE unless stated (the RM520N's recovery used with its conditions). Re-run: the PCM2912A REACHED in E3-O (recommended +70 C), INCONCLUSIVE at E5 as designed; board E's U13 and board C's U5 REACHED (recommended +125 C junction) and added to the route as a regulator change. Material |
| B3 (the SGP41's transition) | its shutdown made independent of the hold: off at 53.75 C on a reference beside it, with the error, gradient and lag; off at every start until it reads 50 C, so never powered in E3-O; its in-envelope function kept at the line (0.20 K); its unpowered storage CONDITIONAL on Sensirion's duration (drafted). Material |
| The eleven unrated lines | each named as an evidence obligation with its owner; the fans architecture-level (section 9) |
| Minor: 2.709 W/K against W4 | corrected: over the low case's cap, under the high case's 2.85 W/K; (a) is CONDITIONAL, not rejected by physics |
| Minor: the ATP19 and the e-paper | stated as conditional future closures, not closed |
