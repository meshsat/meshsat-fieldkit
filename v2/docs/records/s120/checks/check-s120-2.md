mergeable: no

# Independent check of stream s120, round 2 (S-120, second issue)

AI review (desk arithmetic on the makers' documents and the committed netlists, done by running and reproducing), not a
qualified engineering review. 29 September 2026, 19:00 CEST. Checker did not write the work. Round 1: `CHECK.md` beside
this file.

Checked: `fnd/s120` at `afcdb557d2f189496d22a6229ff0a2a5edf5ba94` (confirmed), which merged main `b874b744` as `a757e840`
(the merge differs from `b874b744` only by the six s120 records) and then made `fbed9a7b`, `5078ee24`, `afcdb557`, all as
the owner, no trailer. The clone `<scratch>/chk-s120` is detached at the tip; `<scratch>/chk-s120/_int14` was moved to
`b874b744` for main's tools. The netlists of A and E are unchanged (`6c40250c47195ebb`, `2ed95a0e8069ebf8`); the four held
FET sheets are the ones verified in round 1. No commit, no push, no agent, no box.

B1 to B3 of round 1 are answered. One new blocking item remains, in the closing condition of the new item S-124.

## Blocking

**B1. S-124's closing test names only the upper limits, so it can close with U3's SW1 or SW2 below its negative absolute
rating.** The closing condition (`apply_registry_s120.py` lines 127 to 132, the rating list at line 111; README lines 143 to
147) ends "each result inside 30 V for the FETs and 32 V for U3's pins". SLUSE66A 8.1 p.8 rates SW1 and SW2
at minus 2 V, and minus 4 V for 25 ns; the item's own first sentence quotes only the 25 ns figure, and the `.out` budget
lists both (line 131), but the test does not apply them. They are likely the tightest limit on Q7's turn-off: the item's
own model puts 9.8 A/ns through Q8's body diode at A2, and SW1 then sits at minus VSD less L di/dt of the inductance
between Q8's source and U3's PGND. Minus 4 V less VSD 1.0 V leaves 3 V: about 0.31 nH at A2 (my arithmetic on the
record's model, MODEL, not a bound), less than Q7's 0.82 nH. A bench reading with SW1 at minus 5 V and every VDS inside
30 V would close the item as written.
Fix: add "and CH_SW1 and CH_SW2 no lower than minus 2 V, or minus 4 V for at most 25 ns, against U3's PGND (SLUSE66A
p.8)" to the closing test, state both negative figures in the item's first sentence, and add the SW1 undershoot line to
`.out` section 10 (see n3).

## Minors

n1. The Q2 short ordering (my round 1 m1 said the Q2 short conclusion stood; that was incomplete). In a Q2 short the bus
also rises through ACOV's 26.0 to 27.7 V while the charger still switches (100 us deglitch, SLUSE66A p.14), so Q7 holds the
bus plus VSD, 28.7 V or more before any ringing, exactly as the record says for the FB faults. "For a Q2 short U3 passes its
own 32 V before Q7 reaches 30 V while the pack is above about 1.2 V" holds only after ACOV has stopped the charger. Where:
closing evidence (`apply_registry_s120.py` line 159), S-111's addition (lines 169 to 170, "then pass their rating
first"), README lines 157 to 159, `.out` lines 157 to 159. Fix: claim no order for either fault, or state the Q2 short order as "once ACOV has stopped
the charger".

n2. "L1's largest current inside U2's ratings" (29.51 A) is the steady current limit cycle's peak. In buck mode the LM5176
limits the valley only (7.3.5 p.16: the high side switch skips a cycle if the valley is not below the threshold) and turns
the high side off at the clock (7.3.1), so a first on time after a valley crossing can last nearly a period. Sensitivity
(my arithmetic, unsaturated 12 uH, which overstates the energy far above L1's 17.5 A Isat): a full period on time at 60 V
gives 45.8 A and 23.40 V, Q7 5.60 V to 30 V. The answer does not change; the word "largest" should say "the steady current
limit cycle's" and the sensitivity be stated (`vbus20_bound.py` section 3; `.out` lines 42 to 48; closing evidence).

n3. The "U3 SW1's recommended 26 V" allowances (0.52, 0.57, 0.76 nH) are computed with Q7's turn off di/dt (`.out` lines
137 to 142; README line 131), but SW1 rises above the bus at Q7's turn on (Q8's VDS); at turn off SW1 goes below ground,
whose limit is B1's. Move the 26 V figure to the turn on block (at 3.32 A/ns it is 1.52 nH at A2) and add the negative one.

n4. Three detail strings still print conclusions, not what was read. My mutant with R27 at 20.0k printed "74.76 to 75.51 %
of VDDA ... so SYSOVP is the 4S" (the percentages come from the typed 40.2 and 13.3, `vbus20_bound.py` lines 183 to 190);
my mutant with a 33 nF C998 from CH_ACN_F to GND printed "no capacitor to GND on either (... are not drawn)" beside a list
that holds C998 (lines 204 to 205); "U3 pins" ends in the fixed "so on GND the charger never drives VBUS20" (lines 179 to
180; the author's own m2 mutant shows it after "5 OTG_EN"). The LOG line "each FAIL line printing what the mutant holds"
overstates. All three conditions do FAIL correctly.

n5. The "U3 input sense filter" fact gates the closure on the ABSENCE of Figure 10-3's CACP and CACN (p.85), which the bound
does not rest on (the docstring says "Every circuit fact the bound rests on"). If board A's writer adds TI's own parts, the
closure refuses (my mutant C998: FAIL, exit 1): a rule that fails when its subject is fixed. Print the filter as a record
line and gate only on what the bound uses (R16, C190, C191 on CH_ACN, already its own fact).

n6. Labels: the dump column is not marked MODEL in README section 6 (line 92) or `.out` section 9 (line 101); "never
reached" (ACOV, README line 98, `.out` line 172) and "the bus never reaches a 22 V standoff part's breakdown" (README line
175) rest on the INFERRED bound; say "at the INFERRED bound".

n7. S-124's "Q7's VDS also carrying Q8's VSD" reads as adding 1.0 V to a reading of CH_SW1 that already holds the diode
drop. Say Q7's VDS is read from CH_ACN to CH_SW1 (or from CH_ACN's peak and CH_SW1's measured undershoot); adding VSD again
is conservative, so this is wording only.

## The five items, as reproduced

1. New figures, all reproduced by my own arithmetic from the makers' numbers: valley limit (94 + 1.9) mV over 4.95 mOhm
   19.374 A; buck peaks at the 23.055 V trip 25.295 A (36 V), 28.939 A (55 V), 29.514 A (60 V); boost 28.667 A; energy
   5.226 mJ; bound 23.1981 V. IOFFSET(CS/CSG) is 19 uA in the MAX column (p.7), 1.9 mV across R150 or R151 (100 Ohm each,
   read on the netlist, C123 1 nF across). Margins at DC / dump / bound: Q8 9.04 / 7.76 / 6.80; Q7 (bus plus VSD 1.0 V,
   SLPS516 p.3) 8.04 / 6.76 / 5.80; U3 VBUS 32 V 11.04 / 9.76 / 8.80; recommended 26 V 5.04 / 3.76 / 2.80; BTST1 against
   38 V absolute 10.74 / 9.46 / 8.50 and against 32 V recommended 4.74 / 3.46 / 2.50 (p.8, REGN 6.3 V p.11). Pack side
   BTST2 11.70 / 5.70 at SYSOVP and 7.43 / 1.43 at D1; SW2 12.00 / 6.00 and 7.73 / 1.73. Sensitivities (VREF maximum,
   worst ratio, constant residue): 13.8, 23.4, 37.7 (Q7 at 29 V), 42.5 (Q8), 52.0 percent; recomputing the residue at each
   level gives 13.85, 23.45, 37.83, 42.62, 52.19. Rise rate 18.63 V per ms, 0.373 ms to 30 V (65 cycles). Allowances:
   Q7 0.82 / 0.92 / 1.21 nH; turn on 3.31 ns, valley 10.99 / 9.50 / 7.00 A, Q8 2.72 / 3.15 / 4.27 nH. Dump 22.023 and
   22.241 V. Every `.out` figure agrees at the printed decimals.
2. S-124 cannot close without a measurement: "Closed only on the prototype", the layout reading "does not close this item",
   remedies "are measured the same way". It carries both bus levels (20.96 V and 23.20 V) and the OVP trip reading (FB driven
   through R6 and R7, replacing the INFERRED 23.06 V and the 23.20 V reference). It lacks the negative SW limits (B1).
3. m1 to m11: m2, m3, m5, m6, m8, m10 and m11 answered as asked (pages checked: 9.3.9 and Table 9-3 p.27, IN_VAP p.49,
   EN_OTG p.64, VCELL_4S p.18, Figure 10-3 p.85, VSD and Qrr at 15 V, 18 A, 300 A/us p.3). m4 and m7 answered, with n2 and n3
   left; m9 answered in substance, n4 and n5 left; m1 answered as I asked, n1 corrects my own round 1 advice. The 21 fact
   gate: my own S expression reader confirms VBUS20's 39 pins exactly as `VBUS20_MEMBERS` lists them, R26 13.3k over R27
   40.2k (74.76 to 75.51 percent of VDDA, inside 68.4 to 81.5), and R150, R151 on FE_CS/FE_CSF and GND/FE_CSGF into U2 pins
   16 and 15. `vbus20_bound.py` reprints the committed `.out` byte for byte (exit 0). Four mutants of my own, different
   from the author's: a 100 nF bypass added on VBUS20 (membership FAIL), R27 at 20.0k (strap FAIL), R150 at 1k (CS filter
   FAIL), TI's 33 nF CACN added (sense filter FAIL): 4 of 4 exit 1.
4. Registry: the tip's registry equals `b874b744`'s (sha256/16 1dde1fd16f4e260e). `--check` with the short `afcdb557` wrote
   nothing (sha unchanged). On a scratch copy of each: S-120 closed by `commit afcdb557d2f189496d22a6229ff0a2a5edf5ba94`
   (40 characters from the 8 typed), S-124 opened (SESSION, OPEN), REQ-015 waits on S-106, S-107, S-111, S-124, S-120
   appended after S-121; the two applied copies are byte identical; a second run refuses. `rules_lib.py requirements`: 144
   records, 0 errors, 0 warnings on all four copies (main's tools at `b874b744` and the tip's). The commits a757e840 and
   5078ee24 are refused (README and LOG differ from HEAD's): the integrator must pass the tip or the merge that carries it.
5. Nothing claims ringing is bounded: README 1, 7 and 11, `.out` 10 and 12, the closing evidence and S-124 all say
   INCONCLUSIVE or "not bounded at desk". The bound is labelled INFERRED in the README, the `.out` (sections 3, 8, 12) and
   both registry texts, with its sensitivity; the dump and line figures are labelled MODEL where stated, except the n6
   column headers.

## Counts

Blocking 1. Minor 7. Round 1 items answered: B1, B2, B3 closed; m1 to m11 answered, four with remainders (n1 to n5).
Facts 21 of 21 reproduced by an independent reader. Mutants 4 of 4 FAIL (mine). Registry copies 4 of 4 at 0 errors and 0
warnings; S-124 opened on both lines checked; `closed_by` 40 characters. Figures: every number of `.out` sections 2 to 11
re-derived, all agree at the printed decimals.

<!-- Filed from the checker's report; local paths replaced by <scratch>/ and <local path> (records/int15/apply_check15*.py). Where the report itself spoke of that substitution, its words read garbled. -->
