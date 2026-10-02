# L4-E12: the kit's electronics against the inside air at D-02a's +55 C margin and E5's +60 C dwell (U-02)

MESHSAT-1478 under MESHSAT-1357, layer 4 task L4-E12, 2 October 2026. **Prototype design, desk arithmetic: nothing has been
bought, built, powered or measured, and no kit has been field deployed.** Every figure comes from `l4e12_thermal.out` (the
script `l4e12_thermal.py` reproduces it byte for byte, pins 62 inputs by sha256 and reproduces `records/rv-pwr/pwr_budget.out`
and `records/hc2/pwr_red2.out` before any figure) and carries its class: MAKER (a maker's document, page named), MODELED (the
tree's power and thermal model and W4's lumped film coefficients), INFERRED (method stated), ASSUMPTION (a figure no held
document gives), CONDITIONAL (holds only on a stated condition). Section numbers in brackets point to the `.out`.

## 1. The answer in short

- **The finding stands as L4-E10 put it, now part by part.** At T-H1's floor (LO-01a's 1.6664 W/K, reproduced, [2b]) the
  heat stage's 24.996 W and L4-E8's ballasts (2.09 W, +1.254 K) put the mixed inside air at **71.25 C in E3-O and 76.25 C in
  E5's dwell** (MODELED, [2c]). The screen of every fitted line, module and undeclared line [3b] finds, at E5: **RockBLOCK
  9704, SA868, LimeSDR, G6K relay, H5007NL magnetics over their +70 C by 6.3 K at the mixed air (11.9 K in the running
  cooler's exhaust); the SGP41 over its absolute +55 C by 21.3 K; the MAIN pushbutton (ATP19) over its +55 C by 12.6 to 21.3 K;
  the e-paper over its only stated +60 C by 7.6 to 16.3 K**; the PI and TEST pushbuttons and the sealed USB-C at +70 C in their
  plate-to-air span. The AW7915-AED cards (storage +90 C), the Xenarc (storage +80 C), the 5G module (storage +90 C), the
  PCM2912A (absolute +125 C under bias) and the CM5 (+85 C) do not collide once the heat stage has turned them off or once
  their makers' wider statements are read [3a].
- **Selected: approach (c), the margin hold** [4c, 5]: a step of the kit's own controls beyond the heat stage, on board B's
  TMP117 at +64.0 C, that holds the charge, idles the running module (no shutdown) and powers off board D, the PA rail, the
  RockBLOCK, the LoRa module, both E72, the Geiger module and the SGP41 (existing enables, firmware; the SGP41 needs a switch
  on board E); plus the session's picks for the parts limited at or under the ambient. It cuts the heat at the margin from
  24.996 W to 19.497 W (MODELED). **E3-O then holds at T-H1's existing floor (mixed air 67.95 C, 2.05 K inside +70 C); E5
  needs T-H1 lid open with fans at or over 2.159 W/K** (2.399 for 1 K of margin), where the mixed air is 70.0 C.
- **Rejected: (a), the heat path and the enclosure alone**, which needs 2.709 W/K (3.386 for 2 K), beyond the sealed case's
  outer-film cap at W4's low coefficients (2.10 W/K) and at W4's top (2.85), and cannot help the parts whose limit is at or
  under the margin's ambient [4a]. **(b), wider-rated parts**, is not selectable by the session: five of the colliding parts
  are the owner's device set (CHO-001) and no wider-rated candidate is held for four of them [4b].
- **U-02 can close CONDITIONALLY, on exactly:** T-H1 at or over 2.159 W/K lid open with fans; the hold implemented and forced
  at room temperature; the SGP41 on a switched supply and a bus of its own (board E); the MAIN, PI and TEST pushbuttons picked
  to +85 C (NKK MBN class, held sheet); **PDi's storage statement for the e-paper** (drafted); the +70 C parts kept out of the
  running cooler's exhaust; the unpicked parts (fans, NVMe wide grade, coin cell, header modules) reaching the hold's air. It
  does not change the power path's topology and keeps the sealed case.
- **No owner question is forced** [6]: no part has every route rejected on held evidence. The e-paper's only route rests on a
  storage statement its maker has not published in a held document, a component limitation; the owner's two actions are
  outside contacts (section 9).
- **Two findings outside U-02** [2e, 3d]: (1) at LO-01a's floor L4-E8's ballasts put E3-L's inside air at 56.25 C, over the
  SGP41's +55 C line of REQ-052; LO-01a's floor with the ballasts counted is 1.8058 W/K. (2) Board E's U13, a TLV75533 in
  SOT-23-5 (231.1 C/W, absolute junction +150 C, MAKER), sits on a rail its generator declares at 0.35 A typical and 0.60 A
  peak from 5.0 V: 0.595 W, +137.5 K, past +150 C at any local air above 12.5 C, and the peak exceeds the part's 500 mA; board
  C's U5 (the same part) is declared 0.72 A peak. At the power model's plan load U13 holds (135.8 C at E5's air, against 150).

## 2. The acceptance, read first [1]

| Source | Text (quoted) |
|---|---|
| D-02a, owner ruling 25 Sep 2026 | "TEST-PLAN's +55 C operating, +71 C storage and -33 C storage are QUALIFICATION MARGINS over the -20 to +40 C use and -20 to +45 C storage envelope, with two pass lines: operate to specification inside the envelope; survive and recover at the margin." |
| SC-03 (E5) | "A qualification margin, judged like E3 and E4 under D-02a: survive and recover at the margin, and operate to specification inside the envelope." |
| TEST-PLAN E3 (section 2) | "**E3-O** operation 4 hours at +55 C deployed with the monitor and radios on, on shore or vehicle input, as a deviation with the cells kept out of the heat"; pass: "survive and recover (D-02a): no damage, no deformation, no lost data or keys, CM5 throttling logged but no shutdown, and the functional check passes once the kit is back inside the envelope with its pack refitted" |
| TEST-PLAN E5 | 10 cycles of 24 h at 95 % RH, 30 to 60 C, "deployed (lid open; the case has **no vent opening**", "on shore or vehicle input with the kit logging"; pass: "survive and recover (D-02a, SC-03): no condensation inside (inside humidity log), no corrosion, functional check passes" |
| TEST-PLAN section 6, the deviation's arrangement | "the kit's controls read room-temperature cells, so of their temperature triggers only C1's inside-air trigger sheds modules" |
| CONOPS 4 | C1: "inside air +50 C or any cell +55 C ... normal to the reduced mode; reached again in the reduced mode, to the heat stage"; the heat stage after BANK-R1 turns off "slots 1 and 2, so bank 1 (the SDR, the camera, the QMX, the wall port), the 5G module (its data is slot 2's), both WiFi link cards, the monitor" |
| Method 507.6 (as L4-E10 transcribed it, fnd/l4e10) | operational checks "near the end of the fifth and tenth cycles", in the cycle's 30 C part |

**What it requires (INFERRED from the texts).** At E3-O and E5 the kit is to survive and recover; operation to
specification is required only inside the envelope (D-02a, REQ-051). During the margin the only function required is E3-O's
running module, not shut down (its throttling logged), and E5's logging. The configuration is fixed: deployed, lid open, on
an input, E3-O started with the monitor and radios on. The kit's own controls act during both runs and the rows record it:
C1 already takes the kit to the heat stage, which turns off the monitor, both WiFi link cards, the 5G module and bank 1.
**Not permitted:** the lid-closed reduced mode (it changes the deployed configuration) and EMCON ("radios dark", against E3-O's
radios on). **Permitted by the pass lines:** a further step of the kit's own controls beyond the envelope, which removes no
function the requirements ask for (they ask none during the margin but the running module) and acts nowhere inside the
envelope [4c]; this is the session's reading, recorded as such (section 10) and named for TEST-PLAN's owner.

**Which ratings apply (SESSION, the rule this record judges by, [1j]).** A part powered during the margin: its maker's widest
statement of no damage for an energised part (its absolute maximum where the sheet gives one, else an extended range with
recovery, else its operating range). A part unpowered: its storage range, else its operating range (the only statement held
covers it). No statement held: INCONCLUSIVE. A part through the plate or the wall is bounded by the plate (favourable) and
the inside air (its rear).

## 3. The thermal state at the margins [2]

| Quantity | Value | Class |
|---|---|---|
| The heat stage after BANK-R1 on shore, plan, into the case | 24.996 W (23.272 W at the pack); as generated 23.345 W; HIGH 50.423 W, not covered (as L4-E10 and LO-01a) | MODELED |
| T-H1's floor: the SGP41's +55 C (Table 5, p.7) at +40 C on shore | 1.6664 W/K; L4-E10's 1.6664 W/K, 70.00 and 75.00 C reproduced | MAKER, MODELED |
| L4-E8's ballasts at the bound's worst corner | 2.09 W, +1.254 K | cited (L4-E9 IF-08) |
| Mixed inside air at the floor, E3-O / E5's dwell | 71.25 / 76.25 C (steady; E3-O's 4 h from a kit at +55 C reaches 69.78 to 70.44 C at 32.53's 10 to 8 kJ/K) | MODELED |
| A charge running on shore (the pack at room temperature) | +3.446 W, +2.07 K (the hold holds the charge) | MODELED |
| The plate at the ambient plus, of the rise | 0.465 to 0.725 (W4's films: inside 10 to 25, face 9.5 to 11.5 W/m2K) | INFERRED |
| The enclosure, lid open with fans | W4 1.22 to 2.85 W/K (32.53: 3.0 to 3.3); outer films alone (inside film infinite) 2.10 to 3.86 W/K; low outer films with W4's high inside film 1.62 W/K | INFERRED |
| The running module's cooler exhaust over the mixed air | +5.64 K in the heat stage (4.5 W), +2.78 K in the hold (2.0 W idle): the 30 mm fan's 3.7 CFM (Sunon p.1) at 50 % through the heatsink | MAKER, MODELED, ASSUMPTION |
| E3-O present design | ambient 55.0; mixed 71.25; exhaust 76.89; plate 62.6 to 66.8 C | MODELED, INFERRED |
| E5 present design | ambient 60.0; mixed 76.25; exhaust 81.89; plate 67.6 to 71.8 C | MODELED, INFERRED |

## 4. The feasibility screen [3]

Every fitted line on boards A to E (150 lines of `v2/docs/parts/grade_check.py`'s build, run without writing), the 19
modules and the 10 lines no grade row covers (read from TI's sheets) are screened; board P and the cells are outside the
chamber in E3-O and E5 (TEST-PLAN's deviation) and stay FEA-008's. **At E5 as designed: 143 NOT REACHED, 8 REACHED, 6
PLACEMENT (over only at the upper local bound), 11 INCONCLUSIVE (no range held), 7 out of scope, 4 no part or not fitted.**
Junction-rated parts carry their own rise: the converters and LDOs from the model's losses and the makers' thetaJA (the
tightest, the AP2112K-2.5 at 124.8 C and board E's TLV75533 at 135.8 C at E5's air, under their absolute +150 C); signal,
protection and pass parts by stated class bounds (ASSUMPTION: 20 mW at 250 C/W, 0.25 W at 60 C/W, controllers 0.5 W).

The parts read one by one (MAKER limits; local temperatures MODELED inside, INFERRED at the face and wall):

| Part | State in the heat stage | Governing limit (rule of section 2), document, page | E3-O local / gap | E5 local / gap | Credible way to close |
|---|---|---|---|---|---|
| RockBLOCK 9704 (device set) | powered | +70 C operating, the only range (Ground Control spec page) | 71.3 to 76.9 C / 1.3 to 6.9 K over | 76.3 to 81.9 C / 6.3 to 11.9 K over | air at or under +70 C (hold and enclosure), or the maker's storage range (drafted) |
| SA868 (device set) | powered | +70 C working, the only range (Rev 1.3 p.4) | as above | as above | as above (NiceRF drafted) |
| LimeSDR Mini 2.4 (device set) | off | +70 C storage (maker's page: commercial grade only) | 1.3 to 6.9 K over | 6.3 to 11.9 K over | air at or under +70 C only |
| Omron G6K-2F-Y (board D K1) | in circuit | +70 C ambient operating (p.3) | 1.3 to 6.9 K over | 6.3 to 11.9 K over | air at or under +70 C; an +85 C relay (Layer 6) |
| Pulse H5007NL (board B T1) | in circuit | +70 C operating (p.1) | 1.3 to 6.9 K over | 6.3 to 11.9 K over | air; the maker's HX version (-40 to +85 C, p.1; pinout owed) |
| SGP41 (device set) | powered | +55 C operating, absolute (Table 5, p.7: "may cause permanent damage") | 16.3 to 21.9 K over | 21.3 to 26.9 K over | unpowered: +70 C short-term storage (p.7), so a switch and its own bus |
| ATP19 MAIN | in circuit | +55 C operating (p.1) | 7.6 to 16.3 K over | 12.6 to 21.3 K over | a sealed pushbutton to +85 C (NKK MBN, p.3) |
| PDi e-paper (device set) | refreshed on events | +60 C operation, the only range (flyer p.1; no storage stated) | 2.6 to 11.3 K over | 7.6 to 16.3 K over | its maker's storage range (drafted); no refresh during the hold |
| ATP16 PI, TEST | in circuit | +70 C operating (p.1) | 0.0 to 1.3 K over | 0.0 to 6.3 K over | air; NKK MBN |
| Bulgin PXP4043/C | off | +70 C (its sheet p.1; the 4000 series sheet p.3: -40 to +80 C) | 0.0 to 1.3 K over | 0.0 to 6.3 K over | air; Bulgin's answer (drafted) |
| AW7915-AED x2 (device set) | off | +90 C storage (p.3) | 13.1 K inside | 8.1 K inside | none needed |
| RM520N-GL (device set) | off after BANK-R1 | +90 C storage (p.19); +85 C extended if powered | 13.1 K inside | 8.1 K inside | none needed |
| Xenarc 709GNK (device set) | off | +80 C storage (p.4) | 8.8 K inside | 3.8 K inside | none needed |
| PCM2912A (board D U6) | powered | +125 C ambient under bias, absolute (p.5) | 48.1 K inside | 43.1 K inside | none needed |
| CM5 (device set) | slot 3 running | +85 C operating (p.28) | 8.1 K inside | 3.1 K inside | none needed |
| Floyd Bell sounder | events | +85 C storage (p.1) | 13.8 K inside | 8.8 K inside | muted during the hold |
| NVMe (not picked) | powered | the pick's line: a wide grade, -40 to +85 C (Cervoz p.10) | 8.1 K inside | 3.1 K inside | the pick |

Connectors rated +80 C (the M.2 sockets, board B's USB-C service ports) are over only in the exhaust at E5 (PLACEMENT, 1.9
K). INCONCLUSIVE for want of a range: the pin headers, J_HDMI, the panel LEDs, the CR2032 cell and its holder, the fuse
holders, the headset jacks, the pre-charge pin, the fans (D-18), the header modules (Geiger, lightning, DCF77, pod, camera)
and the QMX (in the lid, at the ambient with the lid open). Each is a range to read, Layer 6's (section 9).

## 5. Three complete approaches compared [4]

The same margins, the same floor, the same ballasts, the plan heat.

| | (a) heat path and enclosure | (b) wider-rated parts | (c) SELECTED: the margin hold |
|---|---|---|---|
| What it is | the parts and the mode unchanged; the inside air lowered by the enclosure (inside fins on the plate, mixing) or the +70 C modules coupled to the plate | every colliding part replaced by one rated to +85 C; the mode and the enclosure unchanged | beyond the heat stage, at the TMP117's +64.0 C, the charge held, the module idled, board D, the PA rail, RockBLOCK, LoRa, both E72, Geiger and the SGP41 off; no e-paper refresh, the sounder muted; restored at +59.0 C after 30 min |
| Heat at the margin (MODELED) | 24.996 W | 24.996 W | 19.497 W (18.152 W at the pack) |
| Enclosure line for E5 (MODELED) | 2.709 W/K (3.010 at 1 K, 3.386 at 2 K); plate coupling alone 1.963 W/K for the coupled parts, the rest still 2.709 | the floor, 1.6664 W/K | **2.159 W/K** (2.399 at 1 K, 2.698 at 2 K); 2.443 with the module at its typical 4.5 W; 4.304 at HIGH |
| E3-O | needs 1.806 W/K for the +70 C parts | at the floor | **at the floor: mixed air 67.95 C** |
| Against the physics | beyond the outer-film cap at W4's low coefficients (2.10) and W4's top (2.85); cannot cool below the ambient, so the SGP41, ATP19 and e-paper stay open | the inside air at 76.25 C (81.89 in the exhaust) leaves +85 C parts 3.1 to 8.8 K | 0.06 W/K over the cap at W4's low outer films, inside W4's range and under 32.53's |
| Changes | mechanical; the session's picks for the three ambient-limited parts anyway | five device-set re-picks (the owner's, CHO-001), four with no candidate held; the session's picks | firmware on existing enables (RB_SW_EN, LORA_ON, ZB_ON, GEIGER_EN, board D and the PA as H1 does); one board E circuit item (the SGP41's switch and bus); the session's picks (MAIN, PI, TEST) |
| Cost | inside fins and fan flow (no sheet held) | candidates unknown | three pushbuttons, one load switch, two resistors and two capacitors on board E; firmware |
| Evidence owed | T-H1 at 2.709 W/K or more | makers' sheets for four device-set parts | T-H1 at 2.159 W/K or more; PDi's storage statement; the hold's forced test |
| Verdict | REJECTED as a design basis | not selectable by the session (outside authority; INCONCLUSIVE) | SELECTED, CONDITIONAL |

Per colliding part [4d]: (a) CONDITIONAL for the +70 C class, REJECTED for the SGP41, ATP19 and the e-paper; (b) CLOSES for
ATP19, ATP16, H5007NL and the USB-C, OUTSIDE AUTHORITY for the five device-set parts, INCONCLUSIVE for the relay; (c) CLOSES
or CONDITIONAL for every part but ATP19 (REJECTED: in circuit at +55 C) and the e-paper (INCONCLUSIVE: no storage range
held). No part has every route rejected.

## 6. The selection: (c), with its margins [5]

**The hold (SESSION, PROVISIONAL).** Trigger: board B's TMP117 (C1's own sensor, under the coolers) at +64.0 C in two
readings. Inside the envelope the heat stage's air at +40 C at T-H1's floor, read in the exhaust, is 61.89 C; 2.0 K of
allowance gives the trigger, so the hold acts nowhere inside the envelope at or over the floor. Before it acts the air is at
most 69.6 C even in the exhaust; once in it the mixed air (67.95 C in E3-O, 70.0 C in E5) stays over the restore; in E5's
30 C phase the heat stage reads at most 51.89 C, so the kit cycles back as C1 designs. Actions: the charger's charge-inhibit
bit and board D and the PA rail off through board A's expanders (as H1 does); the RockBLOCK, the LoRa module and both E72
off through their software enables (`lvc1g08` U503 RB_SW_EN, U504 LORA_ON, U505 ZB_ON); the Geiger module off (U16,
GEIGER_EN); the running module asked to idle (no shutdown, its throttling logged); the SGP41 off (below); no e-paper refresh
and the sounder muted while it holds; an SOS raised meanwhile is queued as under EMCON (D-10) and the operator told. Restore
at +59.0 C after 30 minutes, to the heat stage. Every enable but the SGP41's exists in the generators (read in [7b]).

**The SGP41 (board E, owed to its generator owner, no draft: the generator needs KiCad's libraries to run).** A TPS22810
load switch (the part board E already uses for the Geiger, `kisch.tps22810`) feeding a new +3V3_SGP from +3V3_E6, enabled
from U10's free GPIO20 (QFN pin 31) with a 100k pull-down; the SGP41's VDDH and R57's input on +3V3_SGP; its SDA and SCL
moved from SDA1/SCL1 to GPIO21 and GPIO22 (pins 32 and 34) with 4.7k pull-ups to +3V3_SGP, so that with the switch off no
live bus feeds it through its pins (the firmware runs that bus by PIO and floats it before switching off); the rails, loads,
bypass and basis entries re-declared. Unpowered, its absolute short-term storage range reaches +70 C (p.7), CONDITIONAL on
"short-term" covering E5's ten days (Sensirion drafted).

**The pushbuttons.** MAIN (ATP19, +55 C) and PI, TEST (ATP16, +70 C) to a sealed pushbutton whose maker states +85 C: NKK MBN
(IP67, -30 to +85 C, p.3, held), with its 12 mm bushing, terminals and cutout owed (Layer 6, 7, 8). The ATP19's IK10 vandal
rating is not matched by the MBN's sheet: a named consequence.

**Margins at the selected line** (E5 at 2.159 W/K, E3-O at T-H1's floor; K inside the limit at the lower / the upper bound
of each span: inside, the mixed air / the running cooler's exhaust; face and wall, the plate / the inside air; [5a]):

| Part | Hold state | Limit (MAKER) | E3-O | E5 |
|---|---|---|---|---|
| RockBLOCK, SA868, G6K | off | +70 C operating, the only range | 68.0 to 70.7 C: +2.05 / -0.73 K, PLACEMENT | 70.0 to 72.8 C: +0.00 / -2.78 K, PLACEMENT |
| LimeSDR | off | +70 C storage | as above | as above |
| SGP41 | off (switch) | +70 C short-term storage | as above | as above |
| H5007NL | in circuit | +70 C operating | as above | as above |
| ATP16, PXP4043/C | in circuit, off | +70 C | 61.0 to 68.0 C: +2.05 K at the rear | 64.7 to 70.0 C: +0.00 K at the rear |
| Xenarc | off | +80 C storage | +18.97 / +12.05 K | +15.35 / +10.00 K |
| AW7915, RM520N | off | +90 C storage | +22.05 / +19.27 K | +20.00 / +17.22 K |
| CM5, NVMe (wide grade) | idle, powered | +85 C | +17.05 / +14.27 K | +15.00 / +12.22 K |
| ATP19 (until replaced) | in circuit | +55 C | REACHED, -12.95 K at the rear | REACHED, -15.00 K at the rear |
| e-paper (until PDi answers) | not refreshed | +60 C, the only range | REACHED, -7.95 K at the rear | REACHED, -10.00 K at the rear |

At the selected line 149 lines read NOT REACHED; 6 PLACEMENT (the +70 C class, 0 K at the mixed air: hence the placement
condition); 2 REACHED (ATP19 and the e-paper, closed by the pick and by PDi's statement); 11 INCONCLUSIVE (no range held).

## 7. What stays CONDITIONAL, and what could overturn it

- **T-H1 lid open with fans at or over 2.159 W/K** (E5). It lies 30 % over LO-01a's floor and 0.06 W/K over the sealed case's
  outer-film cap at W4's low coefficients: at those coefficients no inside fin reaches it. **If T-H1 reads between 1.6664 and
  2.159 W/K**, the fallback is the hold with the LimeSDR, the RockBLOCK and board D coupled to the plate: the plate at E5 is
  66.0 to 69.4 C, 0.61 K inside +70 C at its upper fraction (INFERRED), the mixed air 72.95 C; it then also needs the HX
  magnetics and Bulgin's +80 C, and **the SGP41 in the bay air at 72.95 C is past its +70 C storage**: that fallback needs
  the owner's re-pick of the battery-bay gas sensor (CHO-001), the candidate a second BME688 (gas -40 to +85 C, storage
  -45 to +85 C, p.8 and p.15, already on board E) at I2C 0x77, which the outside pod's BME688 (32.54, deferred) then cannot
  share. Under 1.6664 W/K LO-01a fails first.
- The hold implemented and forced at room temperature, as P15 forces the hot stop (TEST-PLAN's owner).
- The SGP41's switch and bus (board E); the pushbuttons (board C); the placement out of the exhaust (Layer 9).
- **PDi's storage statement** covering 64.7 to 70.0 C (E5) and 61.0 to 68.0 C (E3-O) unpowered: if it falls short, the e-paper
  collides under every approach (section 8).
- The plan heat: the hold's line is 2.443 W/K with the module at its typical 4.5 W and 4.304 W/K at HIGH; the bench's E3-O
  and E5 power readings replace the plan figures.
- The class bounds of the screen (signal, pass and controller parts) and the INCONCLUSIVE ranges.

## 8. The owner-question test [6]

No part collides under every approach on held evidence: ATP19 closes by the session's pick; the SGP41 by the board E switch
(CONDITIONAL); the +70 C class by the hold and the line; the e-paper's route rests on a statement PDi has not published in a
held document, which is a component limitation and not a requirements conflict. **No owner question is forced.**

Conditional, not asked: if PDi's statement does not cover the e-paper at E5 (the plate at 64.7 to 70.0 C), the conflict would
be E5 (SC-03 under D-02a: survive and recover through a 60 C dwell with the kit on an input) against the e-paper's maker's
range, by up to 10 K; the options then would be (1) another display part (the owner's, CHO-001), (2) E5 and E3-O run with the
e-paper's exposure as a stated deviation (the owner's, D-29), (3) a thermal break between the e-paper and the plate holding it
near the chamber air (Layer 7, CONDITIONAL on PDi's figure being at least the chamber's 60 C plus the break's residual).

## 9. Downstream items (owner by layer; acceptance)

| Owner | Item | Acceptance |
|---|---|---|
| Layer 4 coordinator | U-02's line on T-H1 (lid open, fans: 2.159 W/K) carried beside LO-01a's; LO-01a's floor with L4-E8's ballasts is 1.8058 W/K (finding 1); L4-E10's conditioned corner moves with the line | the gate's IF-11 and U-02 rows restated on this record |
| Layer 2 and 5 integrators, firmware owner | the hold as a mode beyond the envelope (CONOPS 4, HW-FW-CONTRACT): trigger, restore, actions, enables, the SOS queue | a forced hold at room temperature (each enable seen off, the module idle and logging, the charge held); E3-O and E5 |
| TEST-PLAN's owner | E3-O and E5's arrangement records the hold beside C1; a forced-hold row like P15; E3-O's start with the charge state recorded; T-H1 reports the plate and wall fractions | the plan's revision |
| Layer 6 components | MAIN, PI, TEST pushbuttons (NKK MBN class, +85 C); H5007NL's HX version (pinout); an +85 C T/R relay (optional, for margin); Bulgin's answer; the fans (D-18) to at least the hold's air at E5 plus margin (+75 C class); the NVMe wide grade; the CR2032 cell and holder, the header modules, panel LEDs, headset jacks, fuse holders, J_HDMI, pin headers: ranges read | each maker's range at or over its local temperature at the selected line (section 6) |
| Layer 7 mechanical | the enclosure to T-H1's 2.159 W/K (inside fins on the plate, mixer flow); the fallback plate coupling for the LimeSDR, the RockBLOCK and board D; the MBN cutouts | T-H1 |
| Layer 8, board E's generator owner | the SGP41's switch and bus (section 6); U13 (finding 2): a buck or a DRV-package LDO (100.2 C/W, MAKER) and a part for the declared 0.60 A | board E's suite; U13's junction under +125 C at the declared load at E3-L's air |
| Layer 8, board C's generator owner | the pushbuttons; U5's declared 0.72 A peak against its 500 mA | board C's suite |
| Layer 9 pre-layout | the +70 C parts and the SGP41 out of the running cooler's exhaust; the screen's class bounds replaced by laid-out figures | the placement review |
| Prototype bench | T-H1 in both lid states with the plate and wall thermocouples; E3-O and E5 with thermocouples on the RockBLOCK, SA868, LimeSDR, H5007NL, SGP41, e-paper and plate | each TEST-PLAN pass line; section 3's model replaced by the measured conductance |
| Owner (outside contacts) | send PDi's request (the selection needs it); Ground Control's, NiceRF's, Sensirion's and Bulgin's are drafted for the fallback | the answers filed |

## 10. Decisions taken by the session (authority: SESSION, under the owner's standing rule of 26 September 2026)

| Decision | Why the session's | Reversed by |
|---|---|---|
| The ratings rule of section 2 (absolute maximum or storage where the maker states it; else the only range held) | an engineering reading of D-02a's "survive and recover" against makers' statements | the owner's reading of D-02a, or a maker's statement |
| A step of the kit's own controls beyond the envelope is permitted during E3-O and E5 | the pass lines require no function but the running module; the rows already record C1's shedding; nothing inside the envelope changes | the owner or TEST-PLAN's owner reading the rows otherwise |
| (c) selected; (a) rejected; (b) not taken | (c) needs the least conductance and the fewest changes within the session's authority; (a) passes the physical cap; (b) is the owner's for the device set | T-H1's reading, or the owner's re-picks |
| The hold's +64.0 C trigger and +59.0 C restore (PROVISIONAL) | the trigger sits over the in-envelope air in the exhaust by 2.0 K and under the +70 C class by 6 K | the bench (T-H1, the forced hold) |
| The SGP41 switched off in the hold rather than re-picked | its re-pick is the owner's (CHO-001); the switch keeps the pick | the owner's re-pick, or Sensirion's answer |
| NKK MBN as the pushbuttons' class | the only sealed pushbutton to +85 C in a held sheet | Layer 6's pick |
| The e-paper's gap left to PDi's statement, not escalated | a missing statement is a component limitation (the owner's rule) | PDi's answer |
| No generator draft | the changes need footprints and a KiCad run the runner cannot do; a specification is given instead | the generator owners |

## 11. Files

`l4e12_thermal.py` and `.out`; `fetch_held_back.py` (TI's TLV755P sheet into the ignored `v2/vendor/ti/held/`, sha256
44ac688d7e51f852...); `clarification/` (PDi, Ground Control, NiceRF, Sensirion, Bulgin; drafts for the owner to send);
`README.md`. The tests: `env -C v2/ecad/tools/tests python3 run.py test_l4e12 test_public_hygiene`. No generator, BOM,
registry, interface or Layer 3 file is changed.
