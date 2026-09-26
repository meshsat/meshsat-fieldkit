# Round 4, board E (dock strip): decisions and records

MESHSAT-1357, Review D (parts and circuits). Author: the round-4 board E session, 26 September 2026 (first box run
2026-09-25 23:25 UTC; FIX-UP PASS after the independent review's REJECT, box runs 2026-09-26 00:25 to 00:38 UTC in
/root/r4/e, whose session ended on an infrastructure error before it reported; SECOND FIX-UP PASS, which verified
that work from the primary sheets and re-ran everything in /root/r5/e, 2026-09-26 07:18 UTC onward, the times in
`drafts/box/out-r5/run.log`). Worktree branch fnd/r4e at main 82dd1e4d. Nothing is built; nothing is committed.
Files changed: `v2/ecad/tools/gen_sch_e.py`, `v2/ecad/tools/gen_pcb_e.py`, `v2/ecad/tools/check_pcb_e.py`. Everything
else is under `drafts/`, including `drafts/integrator/r4e-integrator.patch`: the seven changes to files this author
may not write that must land in the same commit (the SGP41 land and its generator, boards/e.json, pcb_reliability.yaml,
and since the second fix-up board E's two `lcsc-allow.txt` copies and `tools/jlc-handfit.txt` for the new choke).

Where a choice remained, it was taken by the session under the owner's standing rule of 26 September 2026 (the
owner is not asked; the option the evidence recommends is taken and recorded here with the options and the reason).

## Review response (fix-up pass, 26 September 2026)

The independent reviewer returned REJECT with two blocking items. Both were right and both are fixed; changing L2 for
the second one exposed a third defect, older and worse, which is fixed with it (R4E-09).

| Item | Reviewer's finding | Resolution |
|---|---|---|
| blocking 1, S-09 / R4E-01, D10 | a one-way SMCJ40A in front of the LM74700-Q1 ideal diode is forward-biased by a reversed input: a short through F1 | D10 is the two-way Littelfuse SMCJ40CA (LCSC C80273) on `Device:D_TVS`; reverse behaviour and the unclaimed negative surge recorded (R4E-01) |
| blocking 2, F-IN-02 / R4E-02, L2 | the SRF1260-4R7Y rating quoted was the PARALLEL column; each winding carries the line current, so the SERIES column (3.59 A) applies and 4.85 A runs it about 73 K hot | L2 becomes the SRF1260-1R5Y (6.89 A series Irms, same family, sheet, land); VIN_RAW and its five segments declared 6.15 A typical and peak (the continuous worst case, VCL max / RS); the IIN_HOST bound and the W at 9, 12, 24 V recomputed from VCL min; value text and comments corrected (R4E-02) |
| found in the fix, R4E-09 | (not in the review) | L2's pin map put DC_HS and GND_V on one winding and VIN_RAW and GND on the other: fixed to input 1, 2 and output 3, 4 |
| minor 1, suite gate | two suite failures come from files this author may not write | a git-format patch for the integrator, `drafts/integrator/r4e-integrator.patch`, applied in a box clone with this round's three files: the full suite PASSES there (see "Gates and the suite"); S-10 and S-11 marked PARTIAL until it lands |
| minor 2, D-02b vs tamper | a normally-open reed reads a cut lead as "lid open": right for tamper, wrong for the reduced-mode trigger | recorded with the resolution for the harness step (open item 17): end-of-line resistors at the sensor and the lead read on ADC3 (pin 41, free) |
| minor 3, solar reverse polarity | nothing blocks a reversed panel ahead of D4 | open item 18 |
| minor 4, F1 voltage rating | the blade family is rated 32 V against the 36 V service maximum | open item 19 |
| minor 5, PRES coupling | E's 1M pull-up reads right only while P keeps its 10k | added to open item 8 (the J_SMB contract) |
| minor 6, GPIO17 pull-down | the pad's default pull-down swamps R55 | added to open item 10 (firmware) |
| minor 7, stale text | gen_sch_e.py:228 still said 8.0/10.0 A | corrected; J_BATT value and title-block comment 2 stay open item 16 |
| minor 8, JST B4B-XH-A-G | the -G suffix is not in the held catalogue | recorded under R4E-04: accepted as board P's precedent part only |
| minor 9, check_pcb_e RF_X count | the gate requires exactly 11 sites; D-07 may make it 12 | recorded on open item 5 (the D-07 site) |
| found in the second fix-up | (not in the review) | the L2 row lost its purchase cover: board E's `lcsc-allow.txt` and `tools/jlc-handfit.txt` name SRF1260-4R7Y only, so `lcsc_fill` FAILS the new BOM (L2 blank, not allowed) and `verify_deliverable` would find no hand-fit route; the allow line (in both of board E's copies, which a suite rule keeps identical) and the hand-fit route are added to the integrator patch (see "Second fix-up pass") |

### Second fix-up pass (26 September 2026, after the first fix-up's session ended before reporting)

The first fix-up's generator (sha256 d95672f4...) was in the worktree and on the box, unreported. This pass took
nothing from it on trust. Each of its load-bearing claims was re-read from the primary document by this pass:

- **Bourns SRF1260** (`v2/vendor/power/bourns-srf1260-common-mode-choke.pdf`, sha256 93b2dc75...): page 1 rendered at
  200 dpi here (`drafts/datasheets/img/r5-srf1260-schematic.png`, `r5-srf1260-layout.png`, `r5-srf1260-dimensions.png`).
  The table's text layer gives SRF1260-1R5Y series 6 uH, 0.0302 Ohm, 6.89 A Irms, 9.15 A Isat, and 4R7Y series 3.59 A.
  The "Electrical Schematic" draws N1 from terminal 1 to terminal 3 and N2 from 2 to 4, with dots on 1 and 2. The
  PARALLEL drawing joins 1 to 2 and 3 to 4. The recommended layout, top view, has 1 and 2 across the 1.28 mm gap and 4
  and 3 below them, so each winding runs corner to diagonal corner. R4E-09 stands on the sheet itself.
- **KiCad land and the committed board** (box, pcbnew, `out-r5/l2_winding_probe.txt`): the land's pads are 1 (-4.25,
  -1.7), 2 (-4.25, 1.7), 3 (4.25, 1.7), 4 (4.25, -1.7). The two longest pairs (9.15 mm) are 1-3 and 2-4. On the
  committed E17 board L2 carries pad 1 /DC_HS, 2 /VIN_RAW, 3 /GND_V, 4 GND. So on the board as committed, winding 1-3
  joins DC_HS to GND_V and winding 2-4 joins VIN_RAW to GND: both lines are shorted through the choke.
- **Littelfuse SMCJ series** (`drafts/datasheets/littelfuse-smcj-series-tvs.pdf`, 6e610db9...): the SMCJ40A / SMCJ40CA
  row reads VR 40.0 V, VBR 44.40 / 49.10 V at 1 mA, VC 64.5 V at 23.3 A.
- **TI LM74700-Q1** (SNOSD17G, e16b3a8c...): ANODE to GND -65 to 65 V; CATHODE to ANODE -5 to 75 V; EN to GND for
  V(ANODE) <= 0 V from V(ANODE). In 10.1.1.3 the TVS- breakdown is "beyond than maximum reverse battery voltage", and
  the design example chooses a 60 V FET.
- **Part records**: LCSC C80273 = Littelfuse SMCJ40CA, DO-214AB, stock 4,960. C7320434 = Bourns SRF1260-1R5Y, stock 0.
  JLC reads the same, and the 4R7Y's C3273444 is also stock 0.
- **Owner rulings cited** (memory project_owner_rulings_2026_09_25): D-04 makes no EMC claim, D-06 has missions
  outlast the pack on vehicle or solar input, and D-16 makes no vehicle surge claim. Each says what the record uses
  it for.

**What this pass changed.** (1) The integrator patch gained three files. Board E's `lcsc-allow.txt` gets a
`Bourns SRF1260-1R5Y` line, and `tools/jlc-handfit.txt` gets an `SRF1260-1R5Y` purchase route. The allow edit goes into
BOTH `v2/ecad/pcb-e1-dock/lcsc-allow.txt` (the board's canonical project) and `v2/ecad/pcb-e1-dock-e7/lcsc-allow.txt`
(its phase copy). The first box run of this pass had the phase copy alone, and the commit-set suite refused it:
`test_driver_hygiene.t_a_phase_copy_declares_what_its_board_declares`, "pcb-e1-dock-e7/lcsc-allow.txt differs from
pcb-e1-dock's" (`drafts/box/out-r5-try1/tests/run_full_int.log`, 1393 passed, 1 failed). The two files were
byte-identical at 82dd1e4d and are byte-identical again in the patch. The old 4R7Y lines are
kept, because the released E6, E7 and E9 BOMs and the committed E17 schematic carry that part, and
`verify_deliverable` reads `jlc-handfit.txt` for them. Two reasons are amended: the allow file's `(XH or pin header)`
and `Bourns SRF1260-4R7Y` lines now say they cover only E17 as committed and go when E is re-cut. The four existing
hunks rebuild byte-identically (`drafts/integrator/mkpatch.sh`, from `scratch/a` = 82dd1e4d and `scratch/b`), and
`git apply --check` passes on the worktree. (2) A comment in `gen_sch_e.py` at J_SMB now states the two PRES
preconditions: the firmware turns GPIO17's pad pull-down off, and board P must keep its R14. This is a comment only;
the netlist is unchanged (below). (3) The first fix-up's unfilled suite placeholder in "Gates and the suite" is replaced by this pass's results.
(4) Open items 24 and 25 were added.

**Taken by the session under the owner's standing rule of 26 September 2026: keep the two E17 allow lines.** The
options were (a) to remove them now, (b) to keep them with the reason amended, or (c) to widen them to a family
substring (`Bourns SRF1260-`). (b) was taken. Under (a), the committed E17 BOM, still the board of record until
layout entry, would lose its cover. Under (c), a variant nobody has chosen would be allowed, which the file's own
header forbids. `lcsc_fill` counts stale lines without failing on them, and it names all four on the new BOM. Two of
those, `(JST-VH` and `on XT60-M`, were already stale on the 82dd1e4d baseline BOM (open item 24).

## R4E-01. S-09 / A03 / F-IN-01: the one-way clamps point the right way, and the inlet clamp is two-way

**Finding.** D1, D2, D3, D4 are unidirectional SMCJ parts (A suffix; CA is the two-way part: Littelfuse SMCJ series
rev 11/20/15, `drafts/datasheets/littelfuse-smcj-series-tvs.pdf`, sha256 6e610db9...). On the KiCad 9
`Diode_SMD:D_SMC` land pad 1 is the cathode (A03, read on every committed board). All four had the RETURN on pad 1:
each is forward-biased across its line from first connection and clamps no positive surge. D10 (decision 31's inlet
clamp) had the same orientation on the committed netlist (pin 1 GND_V, pin 2 DC_F): forward-biased on a correctly
connected input.

**Change (generator), D1 to D4.** Cathode (pin 1) on the line, anode (pin 2) on the line's own return:

| Ref | Part, LCSC | pin 1 (K) | pin 2 (A) | where |
|---|---|---|---|---|
| D1 | SMCJ40A, C224052 | DC_P | GND_V | behind the ideal diode Q1 |
| D2 | SMCJ40A, C224052 | VIN_RAW | GND | behind Q1, the hot-swap and L2 |
| D3 | SMCJ18A, C374030 (new code: board A's D1 part, it had none) | CELL_F | GND | the pack node |
| D4 | SMCJ28A, C224047 | PV_P | GND | the panel input (see open item 18) |

D1 and D2 sit behind Q1, where a reversed vehicle input never arrives, so one-way parts are right there.

**Change (generator), D10: the fix-up pass.** The first pass turned D10 round (cathode on DC_F). The reviewer showed
that this only moves the short: DC_F is the ANODE side of the LM74700-Q1 ideal diode (`ideal_diode("U3", "Q1", ...,
"DC_F", "DC_P", "GND_V")`), the side a reversed input reaches, so a one-way part there is forward-biased by a reversed
input, DC_IN -> F1 -> D10 -> GND_V: a vehicle battery blows the 10 A blade, a current-limited supply below 10 A cooks
the SMC part, and the ideal diode's -65 V reverse rating is defeated. TI's own sheet for U3 (`v2/vendor/ti/ti-lm74700-q1.pdf`,
SNOSD17G, sha256 e16b3a8c...), 10.1.1.3: "a bi-directional TVS diode is used to protect from positive and negative
transient voltages", and "The breakdown voltage of TVS- should be beyond than maximum reverse battery voltage ... so
that the TVS- is not damaged due to long time exposure to reverse connected battery".

D10 is now the **Littelfuse SMCJ40CA**, the two-way part of the same datasheet row (SMCJ40A / SMCJ40CA, marking GFR /
BFR): VR 40.0 V, VBR 44.40 V minimum and 49.10 V maximum at IT 1 mA, VC 64.5 V at Ipp 23.3 A, IR 1 uA at VR, 1500 W at
10/1000 us, TJ -65 to +150 C, DO-214AB, the same D_SMC land. **LCSC C80273**, Littelfuse, DO-214AB, stock 4,960
(LCSC detail record `drafts/lcsc/C80273.json` and JLC parts API `drafts/jlc/jlc-SMCJ40CA.json`, both 26 September
2026; the JLC search returned eleven other SMCJ40CA listings from other makers, which were not taken: the part of
record is the Littelfuse one this project holds the sheet for). Symbol `Device:D_TVS` (KiCad's two-way suppressor, pins A1/A2), pad
1 on DC_F and pad 2 on GND_V, which for a two-way part is either way round.

**Reverse polarity, as it stands now.** With the input reversed (up to the 36 V service maximum) DC_F sits below GND_V.
D10's breakdown in that direction is 44.4 V minimum, above 36 V, so no current flows through it (1 uA at 40 V, 25 C);
U3's ANODE to GND is rated -65 V (EN is tied to the anode, which the EN row allows for V(ANODE) <= 0) and Q1's body
diode is reverse-biased, so the ideal diode blocks the reversal as designed. D1 on DC_P and D2 on VIN_RAW never see it.

**Not claimed (D-16).** A negative surge. At D10's negative clamp (64.5 V at 23.3 A) Q1's drain to source is that plus
the voltage held on DC_P: 76.5 V on a 12 V input, above Q1's 60 V (BSC039N06NS) and the LM74700's 75 V CATHODE to ANODE
absolute maximum. TI's 24 V answer (Figure 10-3, two one-way parts back to back with a low-breakdown TVS-) does not
fit either: a TVS- that survives a 36 V reversed input clamps above 40 V, which with 36 V on DC_P is again over 60 V.
Negative-surge immunity on this entry would need a 100 V class ideal-diode FET, which is a design change for the day a
vehicle surge claim is wanted (D-16 revisit).

**The tool defect this exposed.** `derate.py` reads a suppressor's standoff with `\bSM[ABC]J(\d+(?:\.\d+)?)A?\b`, which
does NOT match a two-way part number (`SMCJ40CA`: the C breaks the word boundary), so a value reading only "SMCJ40CA
..." would fall through to the generic rating path and FAIL against the 53.3 V clamp level. D10's value names the
datasheet row as well ("SMCJ40CA (bidirectional, Littelfuse SMCJ40 row: ...)"), which is where the standoff lives for
both suffixes, so derate reads 40 V today (probe on the box: `out/repo/v/derate_d10_probe.txt`, D10 standoff read 40)
and will keep reading it once the pattern is fixed. The one-line fix, `A?` -> `C?A?`, is open item 20 (tools owner).

**Choice taken by the session under the owner's standing rule of 26 September 2026: the one-way symbol for D1 to D4.**
Options: (a) keep `Device:D_TVS` (KiCad's BIDIRECTIONAL suppressor, pins A1/A2); (b) KiCad's unidirectional TVS symbols
`Diode:1.5SMCxxA` / `Diode:SM6T*A` (single-triangle glyph, but their pins are ALSO named A1/A2, read from the KiCad
9.0.9 library on the box); (c) `Device:D_Zener` (pin 1 K, pin 2 A). Taken: (c). Reason: a one-way part needs a
netlist that names its cathode or no check can read its orientation (W1 S-09, A03 symbol verdict); (a) and (b) do
not. The netlist reads `pinfunction "K"` on pin 1 of D1 to D4. The Zener glyph is the cosmetic cost. Value strings
keep the SMCJ part numbers, which is what `derate` (standoff rule) and `port_protect` (protection regex) read.

**Choice taken by the session under the owner's standing rule of 26 September 2026: D10's two-way form.** Options:
(a) one SMCJ40CA; (b) two one-way parts back to back (TI Figure 10-3). Taken: (a). Reason: at this entry's 36 V reverse
maximum and 60 V FET, (b) buys no negative-surge rating that (a) lacks (see "Not claimed"), and (a) is one part on the
land decision 31 already placed. Decision 31's own text names "A SECOND SMCJ40A"; its amendment to SMCJ40CA is open
item 21 (pcb_decisions.yaml is not this author's file).

## R4E-02. F-IN-02: the vehicle input rated for what the limiter lets through

**Finding (W2).** U6 LM5069-2 with R19 = 10 mOhm limits at VCL / RS, VCL 48.5 min, 55 typ, 61.5 max mV
(`v2/vendor/ti/ti-lm5069.pdf`, SNVS452G, sha256 d60d8106..., electrical characteristics), so 4.85 to 6.15 A, against
VIN_RAW declared 8.0 A typical / 10.0 A peak.

**What the first pass got wrong (reviewer, confirmed).** It kept R19 and restated the declaration to 4.85 A typical /
6.15 A peak, justifying the path with the choke L2 "7.18 A Irms and 9.71 A Isat". Those are the SRF1260-4R7Y's
PARALLEL columns (`v2/vendor/power/bourns-srf1260-common-mode-choke.pdf`, sha256 93b2dc75..., table header "Parallel
Rating ... Series Rating"). L2 carries the positive line on one winding and the return on the other, so each winding
carries the whole line current and the thermal equivalent is the SERIES column: 4R7Y 18.8 uH, 0.0479 Ohm, **3.59 A
Irms**, 4.86 A Isat, "Temperature Rise .... 40 C at rated Irms", operating -40 to +105 C with the rise included. At
4.85 A it dissipates 4.85^2 x 0.0479 = 1.13 W against the 0.62 W of its 40 C rise: about 73 K of rise, over the
105 C limit at the 51 C inside-air bar. And 4.85 A was the wrong number to declare: a unit whose VCL sits at 61.5 mV
passes 6.15 A continuously without ever limiting, bounded only by board A's IIN_HOST.

**Options (reviewer's).** (a) R19 to 18 mOhm (2.69 to 3.42 A), restate everything at that limit. (b) A common-mode
choke whose per-line rating covers 6.15 A continuous at the inside temperature.

**Taken by the session under the owner's standing rule of 26 September 2026: (b), L2 = Bourns SRF1260-1R5Y.** The
evidence for (b) over (a): at a 12 V vehicle, (a) guarantees 2.69 A x 12 V x 0.93 (W2's front-end efficiency) = about
30 W on VBUS20, which is the kit's idle alone (W2 PS-IDLE 29.4 W at the battery) with nothing left to charge, while
D-06 makes vehicle and solar input the way a mission outlasts the pack. (b) keeps R19, U6's timer and power-limit
design (R24, C5) untouched, because RS does not change.

The part: SRF1260-1R5Y, same family, same held sheet, same land and pin map. Series column: 6 uH (1.5 uH per winding),
0.0302 Ohm max, **6.89 A Irms** (40 C rise), 9.15 A Isat. At 6.15 A continuous: 6.15^2 x 0.0302 = 1.14 W against
1.43 W at rated Irms, **about 32 K of rise, 83 C at the 51 C bar** (22 K under 105 C); at 4.85 A about 20 K. In the
common-mode connection the differential flux cancels, so Isat is not the governing limit, and the series Isat covers
6.15 A anyway. LCSC **C7320434** (LCSC detail and JLC parts API, 26 September 2026: `drafts/lcsc/C7320434.json`,
`drafts/jlc/jlc-SRF1260_1R5Y.json`); JLC stock 0, as the 4R7Y's C3273444 also reads (`drafts/jlc/jlc-SRF1260_4R7Y.json`),
so the part stays hand-fitted like its predecessor (vendor/PARTS.md HAND_FIT) and the BOM's LCSC field stays empty
rather than name a code JLC cannot place. Rejected neighbours in the same table: 1R0Y (7.51 A, 1.0 uH) and R47Y
(8.8 A, 0.47 uH) would add margin that is not needed (1R5Y runs at 89 percent of its Irms, 22 K under the limit) and
give up common-mode inductance for it; 2R2Y (5.46 A) runs 101.7 C at 6.15 A, 3 K under the limit, too close. Cost: common-mode inductance 1.5 uH per winding where it was
4.7; no filter calculation in this tree rests on the value, and D-04 claims no EMC performance.

The rest of the path is rated above 6.15 A continuous: F1 10 A blade (8 A at 65 C, pcb_fuse_derating.yaml; its
VOLTAGE rating is open item 19), J_DCIN JST-VH 10 A, Q1 BSC039N06NS 3.9 mOhm (0.15 W), R19 10 mOhm 2512 (0.38 W),
Q7 CSD19532Q5B 4.6 mOhm (0.17 W).

**The declaration (generator, intent).** VIN_RAW and its five series segments (DC_IN, DC_F, DC_P, HS_S, DC_HS) are
declared **6.15 A typical and 6.15 A peak**: the continuous worst case, VCL(max) / RS, which is what `dc_drop` must
judge a conductor's steady rise at. The circuit breaker (VCB 80 to 130 mV) can pass up to 13 A for at most tCB 1.2 us
before it pulls the gate: a sub-microsecond edge no thermal rule reads, recorded in the generator and not declared.

**Consequences, recomputed from VCL(min) / RS = 4.85 A (what the entry is guaranteed to pass, so what the host may
ask), at W2's front-end efficiency of 0.93:**

| input | guaranteed in | on VBUS20 | board A's IIN_HOST bound (at 20 V) |
|---|---|---|---|
| 9 V | 43.7 W | about 40.6 W | at or below about 2.0 A |
| 12 V | 58.2 W | about 54 W | at or below about 2.7 A |
| 24 V | 116 W | the front end's own 100 W | the charger's own limit (5.0 A at 20 V) |

Against W2's budget (battery side): at 12 V the entry carries the idle (29.4 W) plus about 25 W of charge, and falls
about 6 W short of PS-TYP (60.1 W), which the pack makes up; at 24 V it carries PS-TYP and charges. The IIN_HOST rule
is board A's host contract (open item 6). Recording the reviewer's (a) figure for comparison: under 18 mOhm the 12 V
bound would have been about 1.5 A.

## R4E-09. Found while changing L2: the choke's pin map shorted both lines

**Finding.** gen_sch_e.py mapped L2 as {1 DC_HS, 2 VIN_RAW, 3 GND_V, 4 GND}, on the reading "winding 1 pins 1-2 on the
positive line, winding 2 pins 3-4 on the return (pin map per the Bourns drawing, verified 7 Sep 2026)". The Bourns
sheet says otherwise, read on the rendered page (`drafts/datasheets/img/srf1260-schematic-zoom.png`,
`srf1260-schematic-crop.png`, from `srf1260-p1-1.png` at 200 dpi):
- "Electrical Schematic": N1 is drawn between pins 1 and 3 and N2 between pins 2 and 4, dots on 1 and 2;
- its PARALLEL drawing joins 1 to 2 and 3 to 4, which would short a winding if the windings were 1-2 and 3-4;
- "Recommended Layout": 1 top left, 2 top right, 4 bottom left, 3 bottom right, pads 2.15 x 4.50 mm with the 1.28 mm
  gap between 1 and 2 (and between 4 and 3): so each winding runs corner to DIAGONAL corner.

The land in use is KiCad's `Inductor_SMD:L_CommonModeChoke_Bourns_SRF1260` (read from the KiCad 9.0.9 library on the
box): pads 1 (-4.25, -1.7), 2 (-4.25, 1.7), 3 (4.25, 1.7), 4 (4.25, -1.7), each 4.5 x 2.15 mm, the Bourns land turned a
quarter turn. Its diagonals are 1-3 and 2-4, and a diagonal stays a diagonal under any rotation or mirror of the part,
so on this land the windings join pads 1 and 3, and pads 2 and 4, whichever way the part is placed. The old map
therefore put **DC_HS and GND_V on one winding and VIN_RAW and GND on the other**: a few milliohms across the vehicle
input behind the hot-swap (U6 would sit in current limit and time out, retrying) and across the raw bus (which also
takes the solar tracker's output through U4). The committed E17 board carries the same map (pads read on the box:
1 /DC_HS, 2 /VIN_RAW, 3 /GND_V, 4 GND).

**Change (generator).** {1 DC_HS, 2 GND_V, 3 VIN_RAW, 4 GND}: the input side on pads 1 and 2, the output side on 3 and
4, winding 1-3 on the positive line and winding 2-4 on the return. The dots sit on two pads across the small gap, so
on this land either on pads 1 and 2 or on 3 and 4 depending on how the part is turned; in both cases the line current
and the return current pass their windings in opposite senses, the differential flux cancels, and the part is the
common-mode choke that boards/e.json (GND_V "meets GND through the second winding") and pcb_emc.yaml describe. The
`pass_through` basis and the value text say the same. Netlist: L2.2 VIN_RAW -> GND_V, L2.3 GND_V -> VIN_RAW.

**Consequence for layout entry (not this author's file).** `gen_pcb_e3.py:249` takes VIN_RAW's source pad as
`_padc("L2", "2")` and lays VIN_RAW's ten source barrels and the In2 pour from it; VIN_RAW is on pad 3 now. Open item 22.

## R4E-03. F-BP-02: the storage state and the always-on domain

**Finding.** With the pack connected and the kit off, board E's AP63205 (EN tied to CELL_F) keeps +5V_E6 up and the
Geiger module's HV supply sat on it directly (declared 0.10 A at 5 V: 0.5 W, about 0.57 W from the pack); with F-BP-01
and the gauge, W2 measured 0.37 to 1.87 W kit-off: 1 to 6 days from 30 percent.

**Options.** (a) A load switch on the always-on domain's big consumer; (b) a gauge-commanded SHUTDOWN (ship) path;
(c) both. **Taken by the session under the owner's standing rule of 26 September 2026: (c)**, which is W2's own
recommendation ("a ship state (gauge FETs off by SMBus command before storage), an E always-on budget with the Geiger
module on a switched rail").

- **Hardware (generator):** U16 TPS22810DRVR (LCSC C527679, TI SLVSDH0C, WSON-6 DRV: 1 VOUT, 2 QOD open, 3 CT,
  4 GND, 5 EN/UVLO, 6 VIN, pad GND; 2.7 to 18 V, 3 A, -40 to +105 C; shutdown 0.5 uA typ / 2.3 uA max at 5 V) switches
  +5V_E6 to a new rail +5V_GEIGER that alone feeds J_GEIGER pin 1. EN = GEIGER_EN from the RP2040 GPIO18 (U10 pin 29),
  R56 100k to ground (EN must not float; tube off while U10 is in reset). C53 1n CT, C54 10u 25V 1206 and C55 100n on
  the output, C56 1u at VIN (datasheet CIN 1 uF), declared as U16 pin 6's bypass. The same part and pin map boards B
  and D already use (`kisch.tps22810`).
- **Storage path (firmware on the part S-05 connects):** the BQ4050's ManufacturerAccess() 0x0010 SHUTDOWN, sent by
  the sensor controller over SMBC/SMBD. BQ4050 TRM SLUUAQ3A (fetched, `drafts/datasheets/ti-sluuaq3a-bq4050-trm.pdf`,
  sha256 525d16b2...), 5.4.2 and 13.1.8: the FETs turn off after Ship FET Off Time (default 10 s), the gauge enters
  SHUTDOWN after Ship Delay (default 20 s) "if no charger present is detected", and returns to NORMAL when the PACK
  pin exceeds VSTARTUP; SHUTDOWN current 1.6 uA (SLUSC67B 6.5). Preconditions the firmware must enforce: shore,
  vehicle and panel disconnected (a charger voltage on PACK prevents entry), and the controller logs the storage entry
  BEFORE the command, because the FETs take its own supply away. Wake: any charger voltage at PACK+ (shore, vehicle or
  panel through board A's charger). The SHUTDN-pin emergency shutdown (5.4.4.1, PRES pin high-to-low with EMSHUT
  enabled in data flash) and Auto Ship (5.4.3) are recorded as alternatives, not the path of record.

**What remains (typical, 25 C, from the held datasheets; kit off, not in storage).** Board E: the CELL_MON divider
R42 + R43 on CELL_F, 118 uA at 14.4 V = 1.7 mW (2.3 mW at 16.8 V); the AP63205's 22 uA quiescent (0.3 mW); on
+3V3_E6 the RP2040 in DORMANT 0.18 mA typical (4.2 mA maximum across temperature, Table 637), the TLV75533's 33 uA
maximum ground current, the SGP41 idle 34 uA (105 max, heater off), the BMI270 suspend 3.5 uA, the BME688 sleep
0.15 uA, the lid pull-up 33 uA while the lid is shut, the PRES pull-up 3.3 uA, U16 off 0.5 uA. Sum on +3V3_E6 about
0.3 mA, about 1.7 mW at 5 V, about 3 mW from the pack at an assumed 60 percent light-load buck efficiency (the
AP63205 sheet plots no efficiency at 1 to 2 mW, so this figure is an assumption, flagged). Board E total about 4 to
5 mW typical (about 25 to 30 mW worst case, dominated by the RP2040's 4.2 mA dormant maximum across temperature), against about 0.6 W before. NOT included:
the DCF77 module, the AS3935 module and the outside pod (no datasheets held; TBD), board A's always-on parts (TBD,
board A author), the gauge itself (NORMAL 336 uA, SLEEP 75 uA, i.e. 1.1 to 4.8 mW at 14.4 V), and F-BP-01's 0.17 W on
board P, which alone still empties a 30 percent pack (43.5 Wh of 145) in about 10 days until board P's D2 is fixed.
With F-BP-01 fixed, board E plus the gauge is about 6 to 10 mW: 180 to 300 days from 30 percent. **In storage
(ship mode)** the gauge draws 1.6 uA and the kit's domains are unpowered; cell self-discharge and board P's cell-side
parts (TBD, board P author) are what remain. Firmware obligations for the kit-off figure: DORMANT with the SGP41
heater off and U16 off (a measuring SGP41 alone is about 10 mW).

## R4E-04. S-05 / A07: the pack SMBus lead mates

**Change.** J_SMB is JST B4B-XH-A (LCSC C594232, record "B4B-XH-A-G"; JST eXH catalogue: 2.5 mm, 3 A, -25 to +85 C,
9.8 mm; `drafts/datasheets/jst-exh.pdf`), board P's own part, pin for pin P's order: 1 SMBC, 2 SMBD, 3 GND, 4 PRES.
The BB-2590-era 1x6 (1 SDA0, 2 SCL0, 3 SDA1, 4 SCL1, 5 GND, 6 GND) is gone; the sensor bus SDA1/SCL1 keeps every
other device. Nets SDA0/SCL0 are renamed SMBD/SMBC (P's names): the old names said I2C0 on GPIO2/3, which the RP2040
maps to I2C1 (datasheet Table 279); roles unchanged (U10 pin 4 SMBD, pin 5 SMBC, pull-ups R34/R35 4.7k).

**Choice taken by the session under the owner's standing rule of 26 September 2026: the PRES network.** The item
says "PRES to a GPIO" (A07 had recommended NC). Options: direct to the GPIO; through a series resistor with a pull-up.
Taken: J_SMB.4 (PRES_LEAD) through R54 1k to GPIO17 (PRES_IO, U10 pin 28), R55 1M to +3V3_E6. Reason, from the
sheets: P holds PRES with R14 10k (system present needs 20 k or lower, SLUSC67B 8.2.2.2.3); with 1M the controller
reads HIGH with the lead out (3.3 V less 1 uA RP2040 leakage x 1M: 2.3 V against its 2.0 V VIH) and LOW with it in,
and the gauge sees 0.03 V plus its 10 to 20 uA sampling pulse into 10k: 0.21 V against its 0.55 V VIL. 100k would
have left 0.48 V at the gauge (70 mV of margin), which is why 1M. The 1k limits contention if the GPIO drives while
the lead faults. RP2040 pads reset with pull-down (datasheet pin table), so no power-up edge reaches SHUTDN.

**Recorded after review.** (1) The LCSC record's model reads "B4B-XH-A-G"; the held JST eXH catalogue lists B4B-XH-A and
does not explain a -G suffix. It is accepted here only as board P's own precedent part (lcsc_fill assigns P's J_SMB the
same C594232), so the mating halves are identical; the suffix stays unexplained. (2) The PRES network reads correctly
only while board P holds PRES with its R14 10k to ground: if P ever releases PRES, the gauge's 10 to 20 uA sampling
pulse into E's 1M reads "not present". This goes into the J_SMB contract (open item 8). (3) GPIO17's pad pull-down
(about 50 k at reset) swamps R55 1M, so the PRES read needs the pull-down disabled in firmware (open item 10).

## R4E-05. S-10 / C-05: the SGP41 in the battery bay

**Change.** U17 SGP41-D-R4 (Sensirion, LCSC C3659325, JLC stock 2,572 on 26 Sep 2026: `drafts/jlc_SGP41_.json`), the
part appendix 32.54 picked, on the sensor bus SDA1/SCL1 at I2C 0x59 (no conflict: BME688 0x76, BMI270 0x68).
Datasheet v1.0 December 2021 (`v2/vendor/sensirion/sgp41-datasheet.pdf`, sha256 331f35ed...): Table 6 pin map,
Figure 6 circuit copied (VDD through R57 4.7 Ohm, LCSC C23164 0603WAF470KT5E, with C57 1u at the pin; VDDH straight
from +3V3_E6 with C58 1u; pin 4 and the die pad to ground), VDD/VDDH 1.7 to 3.6 V. Absolute operating -20 to +55 C
(meets the -20 C condition); gas specification -10 to +50 C (W6-P7, recorded).

**Choice taken by the session under the owner's standing rule of 26 September 2026: where the bay's air is sampled.**
Options: (a) on board E at its east end; (b) on board P (inside the pack's shrink wrap, which is not the bay's air);
(c) a remote sensor on a lead (a new board or a COTS breakout, neither in the part list). Taken: (a). Reason: the pack
sits in the east pocket X 120 to 178 (A06) and the strip ends at X 118, so E's east end, south of PCB-A's edge (about
X 110 to 117, Y -105 to -90), is the nearest copper to the bay in the same sealed air volume, stirred by the mixer
fans; no new board, no new lead. Placement happens at layout entry.

**Footprint.** KiCad 9.0.9 has no land for this DFN-6 (2.44 x 2.44, P0.8). Drawn from Sensirion Figure 18 by
`drafts/footprints/gen_footprint_sgp41.py` into `drafts/footprints/meshsat.pretty/`
(`Sensirion_DFN-6-1EP_2.44x2.44mm_P0.8mm_EP1.25x1.7mm`): pads 0.55 x 0.40 at x = +-1.15, y = -0.8/0/+0.8; exposed pad
7, 1.25 x 1.70 with the 0.3 mm pin-1 chamfer; paste 1.05 x 1.50. The 2.3 mm dimension is centre to centre (measured on
the rendered page; the edge-to-edge reading would overlap the exposed pad). pin_map_lands judged U17 against it:
PASS (178 of 178). **Assembly:** the sensor opening must stay free of conformal coating and the board is not washed
after the SGP41 is placed (datasheet 5.4); board E is declared conformally coated, so a coating mask is a work
instruction.

**Status after review: PARTIAL.** The generator side is done; the land must reach `v2/ecad/meshsat.pretty` through a
declared generator before the commit (suite failure 1). That is `drafts/integrator/r4e-integrator.patch`
(`tools/gen_footprints_e.py`, the land, `boards/e.json` `footprint_generator`), proved on the box: with it and no draft
footprint directory, pin_map_lands judges U17 against the library land (PASS 178/178) and the suite passes.

## R4E-06. S-11: the lid and tamper switch

**Change.** J_TAMP JST B2B-XH-A (LCSC C158012, -25 to +85 C) carries the lead of a reed sensor under the frame:
TAMPER_LEAD with R52 100k to +3V3_E6, R53 10k to TAMPER_IO (GPIO16, U10 pin 27), C52 100n to ground (1 ms falling,
11 ms rising: the 1 m lead passes a 30 W VHF stage). It reaches the sensor controller only: never ZEROIZE, the panel
or a supervisor (D-03.2). The controller is always powered (U12 EN on CELL_F) and wakes from DORMANT on a GPIO edge
(RP2040 datasheet 2.11.3), so it logs the lid with the kit off and reports it over USB as the reduced mode's trigger
(D-02b). Internal lead, so not an external port for TRN-001 (port_protect still PASS, 3 declared ports).

**Choice taken by the session under the owner's standing rule of 26 September 2026: the switch.** Options: (a) a
hermetically sealed reed sensor under the frame with a magnet in the lid; (b) an IP67 snap-action switch pressed by
the lid; (c) a Hall sensor. Taken: (a) Littelfuse 59140-1-S-05-A (normally open, sensitivity S: activate 9 to 16 mm,
release 10 to 17 mm with the 57140-000 AlNiCo actuator; hermetically sealed, IP67, -40 to +105 C; 1000 mm tinned
leads; operates through aluminium; datasheet revised 03/25/22, `drafts/datasheets/littelfuse-59140-reed-sensor-2022-03-25.pdf`,
sha256 c54b8c66...). Reason: no penetration of any seal and no moving part at the seal, no standby current of its
own, works through the aluminium face. **Normally open** was taken over normally closed because it is tamper-evident:
lid shut = contact closed = LOW, so a cut or unplugged lead reads "lid open" and is logged; a normally-closed contact
would read a cut lead as a shut lid. The sensor has no LCSC code (a lead part, hand-fitted). The actual lid-to-frame
gap against the 9 to 16 mm activation needs the D-08 case measurement.

**Recorded after review: the two rulings want opposite failure readings.** For tamper evidence (D-03.2, logs only) a
cut or unplugged lead should read "lid open", which the normally-open reed does. For the reduced mode's trigger (D-02b)
the safe reading of a lead that cannot be read is "lid closed" (run reduced). One binary contact cannot give both.
**Taken by the session under the owner's standing rule of 26 September 2026:** keep the normally-open contact and the
digital read now, and resolve it at the harness step with end-of-line supervision, not in this pass. Options: (a)
implement now; (b) record now and implement with the sensor's mount and harness (D-08); (c) accept the conflict.
Reasons for (b): the supervising resistors must sit at the SENSOR end of the lead (a splice beside a hermetically
sealed reed whose mount is not designed until the case is measured); the board side needs only a pin move, and the pin
is free, so nothing is foreclosed; and the reduced mode does not rest on the lid alone (D-02b's own rule runs one
module above +35 C ambient, and the kit reads ambient on the outside pod and inside air on U14), so a cut lead cannot turn into an unobserved
over-temperature meanwhile. The design, computed for open item 17: TAMPER to GPIO29/ADC3 (U10 pin 41, NC today;
RP2040 datasheet: pin 41 "GPIO29 / ADC3", VIH 2.0 V and VIL 0.8 V at IOVDD 3.3 V, RIN_ADC 100 k minimum, so C52 100n
holds the node for single conversions), R52 100k pull-up kept, 10k in series and 470k across the reed at the sensor:
lid shut 0.30 V (LOW), lid open 2.73 V (HIGH), lead cut 3.30 V (HIGH), lead shorted 0 V (LOW). The digital level still
wakes the controller from DORMANT on either edge, and one ADC reading then tells shut from short (0.30 V apart) and
open from cut (0.57 V apart); firmware treats cut and short as "lid state unknown": log tamper AND run reduced. S-11
is therefore PARTIAL, together with the suite item of open item 2.

## R4E-07. A09: the LoRa blind-mate site, and the nest that does not fit

**Change.** `gen_pcb_e.py` RF_SITES LORA 102 -> 100 (appendix 32.58; board A's RF_X and J_BM11 at 100).
`check_pcb_e.py` no longer carries a literal site list: it PARSES (ast) `RF_X` from `gen_pcb_a.py` and `gen_pcb_a3.py`
and `RF_Y` from `gen_pcb_a.py`, requires the two RF_X to agree, and checks the clamp holes at each (x, RF_Y +- 10). On
the box: the regenerated mechanical board passes all eleven sites including X 100; the committed E17 board FAILS
"float clamp holes at X 100", which the old gate (literal 102) passed, so the gate now catches the defect it enforced.

**Recorded, not solved here (layout entry).** The float_clamp.py nest is 16 mm along X, 24 along Y, cavity 8.5 mm for
the 6.5 mm plug body (1.0 mm float), M3 holes at (0, +-10), cable slot to +X. At A's pitch it cannot be built:
- neighbours 14 mm apart overlap by 2 mm, IRIDIUM (88) and LORA (100) 12 mm apart by 4 mm;
- the LORA nest spans X 92 to 108 against E's H2 standoff keep-out (d 9 around (110.5, -73): X 106 to 115), 2 mm in;
- each cable slot exits +X at about 2.7 mm above the strip straight into the next nest (4.5 mm tall).

**Proposed geometry (taken by the session under the owner's standing rule of 26 September 2026 as the
recommendation for layout entry).** Options: (a) eleven narrower blocks (X width 11.5 mm: the 8.5 cavity with 1.5 mm
walls, 0.5 mm clear at the 12 mm pitch), holes kept at (0, +-10), cable slots turned to +-Y; (b) one clamp bar for all
sites. Recommended: (b). One bar X -57.75 to 105.75 (VHF cavity edge -56.25 minus a 1.5 mm wall to LORA +4.25 plus
1.5), 24 mm across Y as today, 4.5 mm tall, eleven 8.5 mm cavities on A's RF_X (and a twelfth at X 46 if D-07's third
5G jack is confirmed: 14 mm from 32 and 60), 3.5 mm or more of material between cavities at the 12 mm pitch; the M3
clamp holes move to the mid-pitch points between cavities (where no cavity or slot is), which also takes them off
the cable paths; cable slots to -Y or +Y as the harness to the wall bulkheads needs (open, D-08 and the harness plan).
The bar's east end at 105.75 clears the H2 keep-out (106) by 0.25 mm and a 6 mm rod spacer by about 1.75 mm (the
spacer OD is not specified, A09 unknown). Reason for (b): no inter-nest gaps to hold at a 12 mm pitch, one part to
make, and the holes leave the slot lines. Consequences for board E at layout entry: the per-site F.Cu keep-out circles
(d 12, touching at the 12 mm pitch) become the bar's footprint, and the clamp holes move (a board and gate change).
float_clamp.py and scene.py:278 (SMA_X 102) are not this author's files.

## R4E-08. D-16: no vehicle surge claim

Nothing changes on board E. The owner ruled (26 Sep) no vehicle surge claim for the prototype; the entry is recorded
as "not qualified" in the envelope and ConOps with the warning against 24 V military buses. What board E's entry is,
for that record: F1 10 A blade (its 32 V family rating against the 36 V service maximum is open item 19); D10 at the
entry on DC_F, the two-way SMCJ40CA (40 V standoff and 44.4 V minimum breakdown each way, 64.5 V clamping at 23.3 A,
10/1000 us); the LM74700-Q1 ideal diode with a BSC039N06NS 60 V FET, which blocks a reversed input to the 36 V service
maximum; D1, the one-way SMCJ40A on DC_P behind it; the LM5069 with UVLO 9 V, OVLO 40 V and a CSD19532Q5B 100 V pass
FET, limiting at 4.85 to 6.15 A; the SRF1260-1R5Y common-mode choke; D2 SMCJ40A on VIN_RAW. No MIL-STD-1275 or
ISO 16750-2 pulse is claimed or checked (the standards are not held), and specifically no NEGATIVE surge: at D10's
negative clamp Q1 would see about 76.5 V on a 12 V input against its 60 V (R4E-01). R4E-01, R4E-02 and R4E-09 change
the parts and the map, not this position.

## Netlist difference (base = 82dd1e4d regenerated, parity with the committed netlist; new = round 4 after the fix-up)

Base regeneration against the committed netlist and schematic: PARITY (W7's regen_compare, exit 0 for both; the only
differences are its declared noise: source path/date/tool, title date, the comment-1 phase label), and 0 semantic
differences (`out/netdiff_committed_vs_base.txt`). Base 162 components / 118 nets; round 4: 178 / 124.

**Second fix-up, re-run (`drafts/box/out-r5/`).** The baseline is /root/r4/e/out/base, read and not rebuilt:
`pcb-e1-dock.net` sha256 12610262... and the intent 81dd8d94.... Parity was re-checked against the committed netlist:
PARITY_AFTER_NOISE, content hash 7f6c3838a920dc4f on both, 0 semantic differences. The round-4 netlist was
regenerated from a fresh 82dd1e4d clone in /root/r5/e/repo with gen_sch_e.py sha256 d120ebfb.... That generator
differs from the first fix-up's d95672f4 only by the J_SMB comment. The diff against the baseline is 16 added,
8 changed, 24 pins moved, 42 pins added, 2 removed, 11 nets added, 5 removed and 11 changed, exactly the list below.
The first fix-up's netlist and this run's differ by 0. The commit-set netlist (/root/r5/e/int: the integrator patch,
no draft footprint directory) and this run's also differ by 0. Every difference is intended (`out-r5/netdiff.txt`,
`out-r5/netdiff.json`), and each carries its finding ID:

- Added (16): C52 to C58, J_TAMP, R52 to R57, U16, U17 (R4E-03, R4E-05, R4E-06, R4E-04's R54/R55).
- Changed (8):
  - D1, D2, D3, D4: lib `Device:D_TVS` -> `Device:D_Zener`, value adds "unidirectional, cathode on <line>"; D3 LCSC ''
    -> C374030 (R4E-01).
  - D10: value "SMCJ40A (...)" -> "SMCJ40CA (bidirectional, Littelfuse SMCJ40 row: ...)", LCSC C224052 -> C80273; lib
    stays `Device:D_TVS` (R4E-01, fix-up).
  - L2: value "Bourns SRF1260-4R7Y ... winding 1 pins 1-2 ..." -> "Bourns SRF1260-1R5Y ... common-mode connection ...
    winding pins 1-3 ... 2-4 ..." (R4E-02, R4E-09); footprint unchanged; LCSC stays empty (hand-fit).
  - J_SMB: `Conn_01x06` PinHeader 2.54 -> `Conn_01x04` `JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical`, LCSC C594232, value (R4E-04).
  - J_GEIGER: value only, "5 V switched by U16" (R4E-03).
- Pins moved (24): D1/D2/D3/D4 pins 1 and 2 (8); D10.1 GND_V -> DC_F and D10.2 DC_F -> GND_V (a two-way part, so a
  pad swap with no electrical meaning, kept so every clamp on this board has its line on pad 1); **L2.2 VIN_RAW -> GND_V
  and L2.3 GND_V -> VIN_RAW (R4E-09)**; J_GEIGER.1 +5V_E6 -> +5V_GEIGER; J_SMB.1 SDA0 -> SMBC, .2 SCL0 -> SMBD, .3 SDA1 ->
  GND, .4 SCL1 -> PRES_LEAD; R34.1 SDA0 -> SMBD; R35.1 SCL0 -> SMBC; U10.4 -> SMBD; U10.5 -> SMBC; U10.27 -> TAMPER_IO,
  U10.28 -> PRES_IO, U10.29 -> GEIGER_EN (were no-connects).
- Pins added (42): the 16 new parts' pins. Pins removed (2): J_SMB.5 and J_SMB.6 (GND; the 1x6 is gone).
- Nets added (11): +5V_GEIGER, GEIGER_CT, GEIGER_EN, PRES_IO, PRES_LEAD, SGP_VDD, SMBC, SMBD, TAMPER_IO, TAMPER_LEAD,
  U16's QOD no-connect. Nets removed (5): SDA0, SCL0 and the three no-connect nets of U10 pins 27 to 29.
- Nets whose members changed (11): +3V3_E6, +5V_E6, GND, GND_V, CELL_F, DC_F, DC_P, PV_P, VIN_RAW, SDA1 (+U17.3,
  -J_SMB.3), SCL1 (+U17.6, -J_SMB.4). GND_V and VIN_RAW include L2's two pins trading places.
- Intent (`out/*/pcb-e1-dock-intent.json`): VIN_RAW and its five segments DC_IN, DC_F, DC_P, HS_S, DC_HS: amps_typ 8.0
  -> 6.15, amps_peak 10.0 -> 6.15, their loads the same, notes rewritten (R4E-02); +5V_E6 loads J_GEIGER -> U16;
  +3V3_E6 loads + U17 0.005 A; new rail +5V_GEIGER (5.0 V, 0.1 A, source and switch U16, enable GEIGER_EN, fed from
  +5V_E6); pass_through L2's basis rewritten (R4E-09); bypass + C56 (U16.6), C57 (U17.1), C58 (U17.5).
- BOM side effect (unchanged from the first pass): the grouped rows 1n, 1u, 100n, 10u 25V, 10k, 1k, 1M carry the codes
  the new members were given, which are the codes lcsc_fill.py assigns to those value/land pairs anyway.

Determinism: two further runs of the round-4 generator are byte-identical to each other and to the box run's
schematic (`out/tests/determinism.txt`, title-block date masked).

## Gates and the suite (box, KiCad 9.0.9; run of record /root/r5/e, 2026-09-26 07:32:59 to 07:56:33 UTC)

The run of record is `drafts/box/out-r5/run.log`, from script `drafts/box/r5e_box.sh`. It used fresh clones of the
box's main clone at 82dd1e4d and wrote only under /root/r5/e. The main clone's `git status` was identical before and
after. Inputs (`incoming-sha256.txt`): gen_sch_e.py d120ebfb..., gen_pcb_e.py 8d3df42c..., check_pcb_e.py
9eb2cf85..., and the integrator patch 7e7c80ca....

**Schematic phase, round-4 netlist (`repo`, with the draft land through KISCH_FP_DIRS; the base's value in
brackets).**
- erc_gate: PASS, 0 blocking of 356 warnings (337). The changes: +25 lib_symbol_issues on the new symbol instances,
  the class every symbol here already carries; +1 footprint_link_issues for U17, whose land is only in the draft
  directory; +5 zero-length wire ends; -12 off-grid ends (`out-r5/erc_types.txt`).
- port_protect TRN-001: PASS 8/8, 3 declared ports.
- pin_map_lands SCH-005: PASS 178/178 (162).
- derate CMP-001: PASS 51/51 (49), with D10's standoff read as 40 V (`out-r5/derate_tvs_probe.txt`).
- safe_lines: PASS 1/1. clock_check: PASS 1/1.
- power_path: PASS, 14 rails, 2 feeds, 0 undeclared.
- power_sequence: PASS 14/14, 0 unresolved.
- check_contracts: PASS 73/73.
- review_nets: the same 3 pre-existing notes as the base.
- lcsc_fill, on the 82dd1e4d allow list: **FAIL**, 1 blank row not allowed (L2), and no hand-fit key matches L2. This
  is the gap the patch closes.

**The commit set (`int`: the three files plus the seven-file integrator patch, NO draft footprint directory).**
- gen_footprints_e.py writes the land byte-identically to the draft (sha256 4fd7bf77... on all three copies).
- erc_gate: PASS, 0 blocking of 355. The U17 footprint_link warning is gone.
- pin_map_lands: PASS 178/178 against the library land.
- lcsc_fill: **PASS**, 14 blank rows, all allow-listed. L2 matches the `SRF1260-1R5Y` hand-fit route.
- The netlist has 0 differences from the repo netlist.

**Probes.**
- `l2_winding_probe.txt`: KiCad's land and the committed E17 board's pads, read with pcbnew (R4E-09).
- `derate_tvs_probe.txt`: D1 to D4 and D10 standoffs as derate's own pattern reads them. A bare "SMCJ40CA" reads
  None; open item 20.
- `determinism.txt`: two further runs are byte-identical to each other and to the run's schematic.

**Mechanical (A09; gen_pcb_e.py and check_pcb_e.py are unchanged since the first pass).**
- gen_pcb_e.py was regenerated. check_pcb_e on it passes the outline, rods, block holes, the A-derived site
  read-back (RF_X from both of board A's generators, RF_Y -66) and all eleven clamp sites. Its 34 FAIL lines are the
  part-presence checks of a board with no parts.
- On the committed E17 board the gate reads RESULT 5 FAIL: J_TAMP, U16, U17 and D10 absent, and the clamp holes not
  at X 100. That is the intended reading. The extra "intent file present" line is because the board was checked as a
  copy outside its project directory; it is the same in the first fix-up's run.

**Full suite.**
- Round-4 clone (`out-r5/tests/run_full_repo.log`): 1392 passed, 2 failed, 11 skipped. The two failures are
  `test_footprint_library.t_every_named_footprint_is_in_the_library` (the SGP41 land) and
  `test_reliability.t_the_committed_list_covers_every_wear_part_of_every_board` (J_TAMP). Both pass on the base clone
  (the first fix-up's `out/tests/run_base_failed.log`), and both are closed by files this author may not write.
- **Commit set (`out-r5/tests/run_full_int.log`): 1394 passed, 0 failed, 11 skipped.**
- The first box run of this pass (`out-r5-try1/`), with the allow edit in the phase copy only, read 1393 passed and 1
  failed (`test_driver_hygiene.t_a_phase_copy_declares_what_its_board_declares`). The fix is in "Second fix-up pass"
  above.

**The first fix-up's run in /root/r4/e (history, `drafts/box/out/`).** Its netlist is identical to this run's, 0
differences (`out-r5/netdiff_r4run_vs_repo.txt`), and its commit-set suite read 1394 passed, 0 failed, 11 skipped
(`out/int/int.log`) with the four-file patch. That patch did not yet carry the allow lists. The suite never exercises
lcsc_fill on a regenerated BOM, which is why it passed without them.

## The commit set on current main (29f00554), for the integrator (box /root/r5/e/head, 08:01 to 08:08 UTC)

The round's baseline is 82dd1e4d, and every gate of record above ran there. Main has moved six commits since, to
29f00554, and 29f00554 changed one line in both of board E's `lcsc-allow.txt` (`BOOTSEL` became `BOOTSEL:`). That
line is three lines above this round's allow hunk, so `r4e-integrator.patch` does not apply to main.
`drafts/integrator/r4e-integrator-on-29f00554.patch` (sha256 a1c34bdd...) is the same seven changes built on main's
copies (`scratch-29f00554/`). It differs only in that context line, and `git apply --check` passes on main's files.
The generator files, `boards/e.json`, `jlc-handfit.txt` and `pcb_reliability.yaml` are unchanged on main since
82dd1e4d.

**The run** (`drafts/box/r5e_box_head.sh`, evidence `drafts/box/out-r5-head/`). Main's commits reached the box as a
bundle (`git bundle create ... 82dd1e4d..main` on the runner, read only; sha256 31e37cd2...). They were fetched into
this run's own clone only. The box's main clone stayed at 82dd1e4d and its status is unchanged. The run used
29f00554, this round's three files and the rebased patch, with no draft footprint directory.
- The land is regenerated byte-identically (4fd7bf77...).
- The netlist has 0 differences from the r5 run's.
- erc_gate PASS (355), pin_map_lands PASS 178/178, port_protect PASS 8/8, derate PASS 51/51, safe_lines PASS, clock_check
  PASS, power_path PASS, power_sequence PASS 14/14.
- **Full suite: 1471 passed, 0 failed, 11 skipped.**

Three readings differ from the 82dd1e4d run. Each was attributed on a clean 29f00554 clone with this round's files
absent (`out-r5-head/clean/`):
- check_contracts: INCONCLUSIVE (4 pass, 0 fail, 45 unjudged, "A, B, C, D, P absent from this tree"). On clean main it
  reads INCONCLUSIVE with all six boards absent: main's tree state, not this round.
- lcsc_fill under main's `lcsc_fill.py`: FAIL on F1, F2, F3, the three blade holders, rows this round did not touch.
  The unchanged 82dd1e4d baseline BOM fails the same three on clean main. L2 is covered.
- SCH-002 (`netlist_parts.py`, new on main), the committed E17 board against a netlist:
  - against the baseline netlist: PASS 322/322;
  - against the round-4 netlist: FAIL, 7 values and 1 land. The values are D1, D2, D3, D4, J_GEIGER, J_SMB and L2; the
    land is J_SMB, 1x6 header against XH 1x4. There are 18 references only in the netlist: this round's 16 new parts
    plus the two the baseline already had, D10 among them.
  This is the hold reading of plan condition 6: E17 is not re-cut in this round, and SCH-002 will pass only when board E
  is regenerated from this schematic at layout entry.

## Evidence index (drafts/box/out, SHA256SUMS beside them; the first pass's evidence kept in drafts/box/out-pass1)

- **Second fix-up (the run of record for the final state): `drafts/box/out-r5/`** from `drafts/box/r5e_box.sh` (box
  /root/r5/e only, SHA256SUMS beside them). It holds `run.log`, `baseline-sha256.txt` and `incoming-sha256.txt`;
  `repo/` and `int/`, each with the schematic, netlist, intent, BOM, ERC, the JLC BOM and every gate's log and verdict
  under `v/` (including `lcsc_fill.log` and `handfit_probe.txt`); `netdiff.*`, `netdiff_repo_vs_int.txt`,
  `netdiff_r4run_vs_repo.txt`, `regen_compare_*.json`, `intent_diff.txt` and `erc_types.txt`;
  `l2_winding_probe.txt` and `derate_tvs_probe.txt`; `determinism.txt`; `mech/` and `e17/`; and `tests/run_full_repo.log`
  and `tests/run_full_int.log`. The patch builder is `drafts/integrator/mkpatch.sh`, and the rendered Bourns pages are
  `drafts/datasheets/img/r5-srf1260-*.png`. The check on current main is `drafts/box/r5e_box_head.sh`, with
  its evidence in `drafts/box/out-r5-head/` (see "The commit set on current main"). The directories below are the first fix-up's run in /root/r4/e and are kept
  as history.

- `run.log`, `nohup.log`: the box run (script `drafts/box/r4e_box.sh`, unchanged); `tests/`: determinism and both suite
  runs (script `drafts/box/r4e_box_tests.sh`); `int/`: the commit-set run (script `drafts/box/r4e_box_int.sh`).
- `base/`, `repo/`, `int/`: schematic, netlist, intent, provenance, BOM, ERC json/rpt, gen and build logs, and each
  gate's log and verdict under `*/v/`; `repo/v/derate_d10_probe.txt` (derate's own pattern read on D1 to D4 and D10).
- `netdiff.*`, `regen_compare_*.json`, `netdiff_committed_vs_base.txt`, `erc_types.txt`.
- `mech/`: gen_pcb_e.py's mechanical board and check_pcb_e on it; `e17/`: check_pcb_e (new and old) on the committed E17.
- `drafts/integrator/r4e-integrator.patch` (git format, sha256 recorded in the final report) and its scratch sources.
- Datasheets relied on for the fix-up, all held with their sha256:
  - Littelfuse SMCJ series, rev 11/20/15 (`drafts/datasheets/littelfuse-smcj-series-tvs.pdf`, 6e610db9...): the
    SMCJ40A/SMCJ40CA row, polarity note "Color band denotes positive end (cathode) except Bidirectional".
  - TI LM74700-Q1, SNOSD17G (`v2/vendor/ti/ti-lm74700-q1.pdf`, e16b3a8c...): 6.1, 6.3, 10.1.1.3, 10.1.1.4.
  - TI LM5069, SNVS452G (`v2/vendor/ti/ti-lm5069.pdf`, d60d8106...): VCL, tCL, VCB, tCB, 9.2.1.2.1.
  - Bourns SRF1260 (`v2/vendor/power/bourns-srf1260-common-mode-choke.pdf`, 93b2dc75...): the parallel and series
    table, the electrical schematic, the recommended layout; rendered pages in `drafts/datasheets/img/srf1260-*.png`.
  - Raspberry Pi RP2040 datasheet, build-date 2025-02-20 (`v2/vendor/rp2040/rpi-rp2040-datasheet.pdf`, be56fbb7...):
    Table 625 (VIH/VIL), the pin table (pin 41 GPIO29/ADC3), Table 627 (RIN_ADC).
  - KiCad 9.0.9 `Inductor_SMD:L_CommonModeChoke_Bourns_SRF1260` and `L_Bourns_SRF1260` read on the box.
- Part records of 26 September 2026: `drafts/lcsc/C80273.json` (SMCJ40CA, Littelfuse, stock 4,960),
  `drafts/lcsc/C7320434.json` (SRF1260-1R5Y, Bourns, stock 0), `drafts/jlc/jlc-SMCJ40CA.json`,
  `drafts/jlc/jlc-SRF1260*.json`, `drafts/jlc/jlc-SRF1280.json`; the first pass's records as listed there.

## Open items (not done here, each with its reason)

1. SGP41 land into `v2/ecad/meshsat.pretty` through a declared footprint generator (suite failure 1). Not this
   author's file. Ready: `drafts/integrator/r4e-integrator.patch` (proved on the box, above).
2. `pcb_reliability.yaml`: J_TAMP into board E's lead class (suite failure 2). Not this author's file. In the same patch.
3. `boards/e.json` `signal_classes` for the new nets (RET-001 would judge them UNKNOWN at the strictest bar on the
   routed board). In the same patch, as are board E's two `lcsc-allow.txt` copies and `tools/jlc-handfit.txt` lines for
   the SRF1260-1R5Y (without them `lcsc_fill` refuses the L2 row: `out-r5/repo/v/lcsc_fill.log` FAIL against
   `out-r5/int/v/lcsc_fill.log` PASS). **The patch (seven files, sha256 in the final report) must land in the same
   commit as gen_sch_e.py.**
4. Placement at layout entry (`gen_pcb_e3.py`, not now): seats for J_TAMP, R52, R53, C52; U16, R56, C53 to C56; U17,
   R57, C57, C58 at the strip's east end nearest the pack pocket; R54, R55; the JST-XH 1x4 J_SMB in the vacated 1x6
   site (A07 found it fits with pin 1 about 1 mm south, not DRC-proven). check_pcb_e demands J_TAMP, U16, U17 and D10.
5. The clamp bar (R4E-07): `v2/cad/float_clamp.py`, `v2/cad/render/scene.py:278` (SMA_X 102 -> 100) and board E's
   clamp holes and keep-outs at layout entry; the rod spacer OD and the cable direction to the wall bulkheads are
   unknowns (A09). D-07's possible twelfth site at X 46: `check_pcb_e.py` requires board A's two RF_X lists to agree
   and to hold exactly eleven sites (`len(_RF_A) == 11`), so a twelfth site on board A makes the gate refuse until
   the gate and gen_pcb_e.py's RF_SITES are updated with it. That is intended; it belongs to the D-07 item.
6. Board A (its author): VIN_RAW is still declared 8/10 A in gen_sch_a.py (6.15/6.15 A here); the host's IIN_HOST
   rule (at or below about 2.0 A at 9 V, 2.7 A at 12 V, at 20 V) belongs in W5's hardware/firmware contract.
7. Board P (its author): J_SMB pin 3 to PACK_N (A07 fix 2, the lead's ground in parallel with the shunt); D2's VBUS
   (F-BP-01, 0.17 W, which alone still empties a stored-connected pack in about 10 days).
8. `check_contracts.py`: a J_SMB contract, P against E, pin for pin (A07 fix 4), and in it the PRES coupling: E's
   R55 1M reads correctly only while P keeps R14 10k to ground. Not this author's file.
9. Documents: ASSEMBLY.md :45, :60, :140 and PANEL.md :128, :155 (the SMBus lead is a straight XH 1x4; the sensor
   controller, not the charger, reads the gauge), a new appendix entry correcting 32.62, and one correcting the
   7 September "pin map verified" record of the SRF1260 (R4E-09). Not this author's files.
10. Firmware (W5): the kit-off policy (DORMANT, SGP41 heater off, U16 off), the storage command MAC 0x0010 with its
    preconditions and its wake, the lid log and the reduced-mode report over USB, the PRES read **with GPIO17's pad
    pull-down disabled** (about 50 k swamps R55 1M), the gauge's EMSHUT/NR data-flash choice, SGP41 conditioning
    (10 s maximum) and humidity compensation from U14.
11. Mechanics (D-08): the reed sensor's mount under the frame and the magnet pocket in the lid; the real gap against
    the 9 to 16 mm activation distance.
12. Assembly: coating mask over the SGP41 opening, no wash after it, SGP41 on the last reflow; L2 (SRF1260-1R5Y) is
    hand-fitted (JLC stock 0, as its predecessor), bought from a Bourns distributor with the order set.
13. Standby currents of the DCF77 module, the AS3935 module and the outside pod: no datasheets held, so the kit-off
    figure of R4E-03 excludes them.
14. W1 S-09's other halves: the one-way clamps on boards A, B, D, P and the rectifiers on C (their authors), and an
    orientation check in the protection gate (tools owner). Board A's own SMCJ40A on its VIN_RAW is behind E's ideal
    diode, so one-way is right there; any board clamp IN FRONT of a reverse-polarity element needs the two-way part.
15. Board E's hold stays (plan condition 6): the E17 board carries neither D10 nor the corrected clamps nor the
    corrected L2 map, and nothing here is placed or routed.
16. Stale BB-2590/U wording outside this round's items: J_BATT's value string and the schematic title-block comment 2
    (schematic and BOM text only).
17. D-02b against tamper evidence (R4E-06): end-of-line supervision at the harness step: TAMPER to GPIO29/ADC3 (U10 pin
    41, free), 10k series and 470k across the reed at the sensor end; firmware classifies shut, open, cut and short and
    treats cut or short as "log tamper and run reduced".
18. Solar input reverse polarity (pre-existing, reachable now that D4 points the right way): nothing ahead of D4
    blocks a reversed panel, so a reversed lead forward-biases D4 at the panel's short-circuit current (about 6.25 A, the reviewer's figure for the 100 W panel class)
    continuously and F2 (10 A) does not clear it; D4's typical failure mode is a short (Littelfuse sheet). The J_SOLAR
    VH plug and the wall connector are keyed, so it takes a miswired harness. Recommended: an ideal diode ahead of F2
    or D4 as on the vehicle entry (LM74700-Q1 and an N-FET), sized for the panel; a board E design change for the
    next round, with the LT8705A stage's own input rating checked.
19. F1's voltage rating (pre-existing): the blade family this project applies (pcb_fuse_derating.yaml, Littelfuse
    ATOF 0287, 32 V) is rated below the entry's 36 V service maximum, so interruption above 32 V is not guaranteed.
    Recommended: a blade family rated for at least 36 V (a 58 V automotive blade family, with its datasheet fetched
    when picked) or a different fuse in F1's position; J_DCIN and the holder re-checked with it.
20. `derate.py` (tools owner): the suppressor pattern `\bSM[ABC]J(\d+(?:\.\d+)?)A?\b` misses two-way part numbers;
    `A?` -> `C?A?` fixes it (D10's value names the row, so today's reading is right either way).
21. `pcb_decisions.yaml` decision 31 (and its rendered page): "A SECOND SMCJ40A goes on DC_F" should read SMCJ40CA,
    with the reverse-polarity reason (R4E-01). Not this author's file; re-render with decisions_render.py.
22. `gen_pcb_e3.py:249` (layout entry): `_L2S = _padc("L2", "2")` is VIN_RAW's source pad; after R4E-09 VIN_RAW is
    on pad 3, and the VIN_RAW barrels, the In2 pour and the escape stub follow it; DC_HS stays on pad 1. The E17 board
    itself must not be ordered with its L2 map (it shorts both lines).
23. `v2/vendor/PARTS.md` is regenerated by kb_inventory.py: the new part numbers SMCJ40CA and SRF1260-1R5Y are covered
    by the held Littelfuse SMCJ and Bourns SRF1260 sheets (their rows are in them).
24. Stale allow lines in board E's `lcsc-allow.txt` (both copies, which must stay identical; integrator, at the re-cut): on the round-4 BOM `lcsc_fill` names
    four lines that cover no row. Two are this round's: `(XH or pin header)` and `Bourns SRF1260-4R7Y`, kept on purpose
    to cover E17 as committed, with their reasons amended. Two are pre-existing: `(JST-VH` and `on XT60-M` were already
    stale on the 82dd1e4d baseline BOM, because J_DCIN and J_SOLAR carry C274411 and the J_BATT value reads "Amass
    XT60-M: ...". Remove all four when board E is re-cut at layout entry. Remove the 4R7Y line in `jlc-handfit.txt`
    only when no released E BOM still names the part.
25. L2 is hand-fitted (JLCPCB stock 0) but is not in `make_handoff.py`'s EXCLUDE set for `pcb-e1-dock`, which
    `jlc-handfit.txt`'s own header asks for. This is pre-existing (the 4R7Y was the same) and unchanged by this round.
    JLC places nothing on a row without a code, so the order set is not wrong today, but L2 stays in the JLC CPL.
    Tools owner, at the next order set.
26. Integration onto main (integrator): apply `drafts/integrator/r4e-integrator-on-29f00554.patch` on main at
    29f00554, or `r4e-integrator.patch` on 82dd1e4d. Both carry the same seven changes. On 29f00554 the commit set
    passes the suite: 1471 passed, 0 failed, 11 skipped. Main's own open readings, the six absent netlists behind check_contracts and
    F1 to F3 under the corrected lcsc_fill, predate this round and are not closed by it.
