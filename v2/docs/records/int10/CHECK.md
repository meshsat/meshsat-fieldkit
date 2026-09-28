mergeable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357), with one internal address redacted. Blocking item B1 and minor items M1, M4 and M7 are answered in CLOSURE.md beside this file; the rest are carried there. -->

# Check of integration set 9, fnd/int10 at 27d8a129 onto main 9147db5d (MESHSAT-1357, 29 September 2026)

**AI review, not a qualified review.** One Claude checker who wrote none of the candidate, working read-only in the
scratch clone `_scratch/chk-int10`.
- **The final commit judged is 27d8a129b64718c0341a58385aec4a34505ac027.** It is 03237888 plus one change: board
  A's EMC sheet gains U41 (section 6).
- Sections 3 to 5 were read at 03237888; the new commit changes only `v2/ecad/tools/pcb_emc.yaml`.
- These were re-run at 27d8a129 with the same results as below: `rules_lib.py`, `rules_lib.py requirements`, both
  `rules_render.py --check`, and `decisions_render.py --check`.
- `pcb_emc.yaml` is in no rules_status config input and in no record's binding.

The candidate's ignored readings
were copied from the int10 worktree into this clone only (905 files: board `out/` folders and `v2/ecad/out/rule-audit`);
`v2/vendor/*/ibis`, caches and test scratch were excluded, and nothing was copied the other way. Prototype design:
nothing is built, ordered or measured.

The engineering content of the set holds up (sections 3 to 5 below). The one blocking item concerns how the line was
committed, not what it contains.

## 1. Blocking

**B1. Four commits on the line are authored and committed as a Claude identity.** `3ea5a994`, `8eca1ef3`,
`b11e6a16` and `cef7cb77` (the merges of streams energy, od01 and s99reg, and of main 9147db5d) carry
`author the runner's service identity (address redacted by the integrator)` and the same committer (`git cat-file -p cef7cb77`). Main has
none: 0 of its history, and all of its recent merges, are `Kyriakos Papadopoulos <ncpjfuzl@mxmx.email>`. The other 37
commits of the set are the owner's identity. The repository's standing rule is "commits as the owner, never as any
Claude identity". The owner ruling of 3 September 2026 rewrote this history to remove Claude attribution, and
GitLab mirror 34 publishes `main` to github.com/meshsat/meshsat-fieldkit within minutes. Promoting the line as it is,
the way set 8 was promoted (main's history contains fnd/int9's commits unchanged), would publish these four.
- 27d8a129 itself is the owner's, but it still has all four in its ancestry.
- Fix: re-create the four merges with the same trees under the owner's identity (`git -c user.name=... -c
  user.email=...`), then carry the other commits that descend from 3ea5a994 across, up to 27d8a129 (found with
  `merge-base --is-ancestor 3ea5a994`). The contents do not change, so every binding by content still holds.
- Checked: no tracked file outside `v2/ecad/*/routed/` cites any of the shas that would change. The re-take's verdict
  files carry `version`/`git_head` `cef7cb77c420` as provenance only (`rules_status.py` does not read `git_head`).
  After the rewrite they would name a commit that is off the line. Re-take them or record the mapping.

## 2. Minor (none changes a verdict, a number a rule judges, or a disposition)

- **M1. The "only" in the judged rebind reasons is false for four records.** The H2 clause says "U39 and R209 appear
  only in an earlier rebind entry that lists the H2 differences". For CFL-005, CON-010, CFL-016 and CFL-014, U39 also
  appears in a second entry: the r8int5 PANEL.md re-read (U28's EMCON_EF_FLT, "low when U39 has cut that supply") for
  three of them, and for CON-010 the EMCON.md re-read (U39's OVLO at 3.83 to 4.11 V). Those entries read U39's
  overvoltage lockout and fault line, and the change leaves both alone (only R209's value text moved). So the
  conclusion stands, but the sentence written into four registry entries is untrue. It is true for CON-019, CON-018
  and CON-016.
- **M2. IF-AB-POWER's +5V_DEV row has no line cite.** It cites "(gen_sch_a.py, the S-99 lines)" where every other
  cite is a line. The rail is at `gen_sch_a.py:140`, and the U41 block is at 1369 to 1376.
- **M3. "over every tolerance" is wider than the band is.** Decision 55's outcome, board A's +5V_D8IN intent note
  and sheet A's +5V_D8IN note call 4.872 to 5.133 V the band "over every tolerance". It is a DC set-point band, and
  PFM ripple and load-step overshoot are not in it. The generator comment and S-99 (d) already say "a DC set-point
  band".
- **M4. The erratum and the hold disagree about whether a review is owed.** The erratum says "the next review of
  board A (owed anyway after the regeneration)", but the decision 31 hold's review requirement was moved to the new
  netlist and CURRENT-EVIDENCE reads it "met". One of the two should change. On the facts below (M5), the pin is
  right and the parenthesis should go.
- **M5. The repin proof checks less than the review's subject covers.** The review's subject is every exposed
  conductor and the part it meets first. `apply_repin_circuit_s99.py` checks that the 22 reviewed external pins stay
  on their nets and that no added part is a connector. It would not catch a new non-connector part on an external
  net. I checked this directly: none of the 19 external nets (plus GND) changed its node set, and every added part
  sits on VBAT, RAIL_EN, GND or the new nets. So the fact holds; the proof should assert it next time.
- **M6. Board D's derivations that quote the old source are not tracked in the registry.** Board D's +5V_D8 note
  still reads "the source is board A's eFuse output on the 5.0 V device rail ... worst case 4.90 V", and U41's DC
  bottom is 4.872 V. `gen_sch_d.py:430-434` derives SA_PTT_n's receive band from "the source's 4.90 V" and "nominal
  3.18 V at 5.088 V"; at 4.872 V and 5.002 V it is about 2.676 V (2.668 V with the stand-in) and 3.126 V. That is a
  shift of 9 mV and 54 mV in a band the file itself leaves to the bench. `records/s99a/README.md` section 4 lists some
  of board D's stale texts but not this derivation, and no S item carries them (S-116 covers the codec only).
- **M7. S-99's "Closes when" list does not say what this set finished.** It still lists "board A is regenerated ...;
  PWR-001 and INT-001 are re-taken on it; the IF-AB-POWER +5V_DEV row reads the new figures", and this set did all
  three. The text does not say they are done and that (a) to (g) remain. Status OPEN is correct.
- **M8. ASSEMBLY.md step 3 omits the new rail.** It lists the rails that come up at their own converters and does
  not name +5V_D8IN (5.0 V, 4.87 to 5.13 V). The heater rail was already missing before this set.
- **M10. Board A's EMC sheet does not declare U3 (BQ25731) as a source.** U3 is a 400/800 kHz buck-boost charger
  (SLUSE66A features table) and appears in the sheet only as a victim. `emc_sheet.py` SWITCHERS lacks "BQ25731", so the
  test cannot catch it. This predates the set: main misses it the same way. Next action: add U3 as a source with its
  programmed frequency and dithering, add "BQ25731" to SWITCHERS, and re-take emc_sheet. Board A's emc_sheet reading
  itself dates from 21 September (10 sources).
- **M11. The new U41 row could be tighter.** It could carry `spread_percent: 6` and the 450 to 550 kHz range
  (SLUSEA4D 8.5 p.7 and 9.3.10), and name J_MEZZ_PWR1 as the lead its output leaves on. The same spread applies to
  U12, U33 and board B's TPS62933 rows. The sheet's older text also undercounts: the first path says "the five LM5176
  switch nodes" (there are seven) and the pre-compliance line says "all five converters" (twelve sources are
  declared).
- **M9. Carried as the set's own README records them:** IF-AB-POWER `converters` still reads "7.2 to 9.5 A";
  C231/C232 read "22u 10V" but map to C2918511, a 25 V part (named in S-99 (d)); the XAL6060-682ME and board A's use
  of C705784/C861078 still need a certification line (decision 55 says so). Observation only: S-115 (the layout
  generator refuses the board) is LAYOUT_STAGE, so it is not among A's 6 layout-entry reasons.

## 3. The circuit (brief item 1): reproduced from the netlists with my own S-expression parser

- **Parts.** Main 612, candidate 622. Added exactly U41, L13, C227 to C232, R217 and R218. None removed.
- **Pins that moved.** Exactly three: U23.4 (IN), C103.1 and R100.1 moved from /+5V_DEV to /+5V_D8IN. New nets are
  /+5V_D8IN (C103, C231, C232, L13.2, R100, R217, U23.4), D8B_BST, D8B_FB, D8B_SS, D8B_SW, and U41's unconnected pin 1.
  No net disappeared.
- **Value text only.** R186 "1k 1% (ILM: 0.89 A)" became "0.91 A" and R209 "4.7k (0.18 A)" became "0.20 A". The
  value strings of U23, U32 and U39 follow.
- **U41 against SLUSEA4D Table 7-1.** Pin 1 RT is left open (500 kHz, "Float for 500 kHz"), 2 EN on RAIL_EN, 3 VIN on
  VBAT, 4 GND, 5 SW on L13, 6 BST through C227 100 nF to SW, 7 SS with C228 10 nF (at least 6.8 nF required), 8 FB on
  R217/R218. All match.
- **L and C against Table 10-2.** 5 V at 500 kHz asks 6.8 uH and at least 10 uF effective COUT; the design has 6.8 uH
  and 2 x 22 uF. Ripple is 1.033 A at 16.8 V in, and the peak at 2.0 A is 2.517 A, against IHS_LIMIT 4.2 A minimum.
- **EN level.** RAIL_EN is R2 100k to VBAT over R184 39k, 5.05 V at 18 V. U41's EN pull-up currents (0.7 + 1.4 uA)
  into 28 kOhm add about 0.06 V, which stays under EN's 5.5 V recommended maximum.
- **Divider.** 56.2k over 10.7k with VFB 784 to 816 mV (TJ -40 to 150 C, SLUSEA4D 8.5 p.6), 0.1 percent plus 25 ppm/C
  over 65 K and IFB 0.15 uA gives **4.8718 to 5.1329 V**, nominal 5.0019 V. Without TC it is 4.8852 to 5.1189 V.
  `u41_divider.py` and `codec_floor.py` reproduce byte for byte. Both codes match board D's R80 and R81 in D's netlist
  and are CERTIFIED in JLC-CERTIFIED.tsv.
- **TPS2596 equation 7** (SLVSET8A printed p.28, worked example 903 / (1 - 0.0112) = 913.2 ohm) gives
  ILIM = 903 / RILM + 0.0112:
  - 1k: 0.9142 A
  - 4.7k: 0.2033 A
  - 453R: 2.0046 A
  - 909R: 1.0046 A
  - board B's 301R: 3.0112 A

  Every ILM label on boards A and B agrees at its written precision.

## 4. Declarations, leads, pins, rebinds (brief items 2 to 6)

- **Intent.**
  - +5V_DEV: 4.1 A typical = J_5V_DEV 3.8 + U32 0.3. Peak 6.9142 = B's 6.0 + 0.9142.
  - +5V_D8IN: 1.0 / 2.0 A, load U23 1.0, v_work 5.14.
  - VBAT: Q32 1.61 (4.1 x 5.088 / 12.96 = 1.6096), U41 0.4 (0.386).
  - Margins: 7.056897 - 6.9142 = 0.142697; 7.095710 - 6.9142 = 0.181510; the 909 ohm row scaled gives 0.956044
    (margin 0.100853); with R186 at -1 percent 0.091314. All reproduced.
  - Adequacy is not claimed anywhere: the P-tier 8.171220 A stays open under S-99.
- **Leads and contracts.**
  - `lead_ends`: 5 of 5 AGREE (declaration consistency only).
  - `check_contracts`: PASS of 99. `interfaces_a`: PASS, 0 disagreements.
  - The committed netlist (599ee964a9c23d6e), intent (070b4c5e41e023e5) and interfaces (363af4715553e42b) are the
    files those readings name.
  - `gen_sch_a.py`'s sha (eb2e347e4d371e0f) is the provenance's.
- **Line cites.** Opened at every cited line: A 54, 119, 152, 1051-1052, 1149, 1387, 1596-1599, 1613-1618; B 85,
  111, 271, 551, 1119, 1210, 1637-1638; D 259-261; `gen_pcb_a3.py` 208, 280, 312, 583-586 (S-115). All correct.
- **Moved pins.**
  - Hold, port set and reliability line now read 599ee964a9c23d6e.
  - Reliability: 82 candidates, 57 classed, 25 excluded, 0 refused, unchanged. `port_protect_a` PASS (TRN-001).
  - The review's only figure that changed, 0.89 A at line 244, enters no conclusion, as the erratum states.
- **Rebinds.**
  - I read all eight records against the change. None has a subject the change touches.
  - REQ-077: U41's EN joins RAIL_EN, so the kill also drops the D8 input. The shed path the record states is unchanged.
  - CFL-014: U41 is on VBAT, the system side of R17.
  - CON-016: no diode or clamp was added.
  - CON-010: no part of the KEY/VGG path changed.
  - Apart from M1, the sentences are true.
- **Validator.** 144 records, 0 errors, 0 warnings; rules 59, 0 errors.
- **Registry texts.** S-99, S-115, S-116, decision 55 (only appended; decisions 1 to 54 unchanged), REQ-072's note
  (FAIL unchanged; 107.9 Wh, 320 Wh, 483 Wh, 2120 Wh and 8.4 W found in `energy_budget.out`), and the REQ-044 and
  CON-010 page rebinds are consistent.
  - S-116's figures were recomputed: 4.341 / 4.241 / 3.84 V at 2.0 A; options 4.316, 4.401, 4.369 and 4.389 V.
  - The page rebinds' figures match the page: sections, 34 to 34 reasons, and the inhibit_chain A/D/C counts
    7/2/9, 7/1/8 and 6/6.
  - Consistency and adequacy stay separate throughout.

## 5. Sheet A, the pages, the merged streams, the tools (brief items 5, 7, 8, 9)

- **Sheet A.** `rail_widths.py --markdown`, run fresh, is byte-identical to the committed `rail_widths.out`. All 35 of
  sheet A's power rows equal it. The +5V_DEV, SD_OUT, +5V_D8IN and VBUS_WALL notes match the change, and their
  "Before" figures match main. `constraints_bound.py` (printing only): A PASS of 338, and every sheet PASS.
- **Pages.**
  - Layout-entry reasons: 34 to 34 (A 6).
  - CURRENT-EVIDENCE: 13 changes, all 2dfe1c546cb39ccb to 599ee964a9c23d6e, in the candidate, holds, PASS and desk
    sections.
  - PCB-RULE-STATUS-A counts: ERC 1524 to 1557 (all warnings: lib_symbol_issues, off-grid, wire endpoint),
    pin_map_lands 612 to 622, derate 268 to 274, intent_rails 35 to 36, power_sequence 34 to 35.
  - No verdict moved on any board.
- **Merged streams.** The energy and od01 merges touch only their own records folders. Neither contains any personal
  data: the postcode is a placeholder, and Leiden is SC-37's site, already in the tree. Neither records any order,
  payment or contact: the RFQ is "NOT SENT", the checkout list says nothing was carted, and ordering, quotes and the
  operator stay the owner's in `od01/README.md`. No `.ibs` file is tracked, and no CLAUDE.md or `.claude/` file is
  either.

## 6. The added EMC row, 27d8a129 (the coordinator's question)

- **The row is correctly sourced.**
  - U41, TPS62933, f_khz 500, edge_ns null.
  - Basis: `v2/vendor/ti/ti-tps62933.pdf` Table 7-1, "Float for 500 kHz". The file exists in the tree, and SLUSEA4D
    8.5 p.7 gives fSW 450 / 500 / 550 kHz with RT floating.
  - Board A's netlist has U41 pin 1 on `unconnected-(U41-NC-Pad1)`. D8B_SW is on board A.
- **It is complete to the standard of its sibling rows (U12, U33), with two gaps, both minor (M11):**
  - It carries no `spread_percent`. SLUSEA4D 9.3.10 and 8.5 p.8 give the TPS62933 a ±6 percent internal spread at
    fSW/128, and the schema already carries `spread_percent: 6` on board B's AP63203 row.
  - It routes the output through "the mezzanine harness". U41's output leaves board A on J_MEZZ_PWR1, the separate VH
    5 V lead. IF-AD-HARNESS names the lead in its title, but the path text does not name it.
- **Test and judge.** `test_emc_sheet`: 7 passed. `emc_sheet.judge(only='a')`: 12 sources, 0 fails.
- **Does the sheet miss any other switching part? Yes, one, and it predates this set (M10).** Board A's netlist has 13
  switching parts:
  - 7 LM5176: U2, U5, U7, U13, U15, U16, U19
  - 2 AP64500: U4, U6
  - 3 TPS62933: U12, U33, U41
  - **U3, the BQ25731 buck-boost charge controller**

  The sheet declares the first twelve. **U3 is only a victim.** SLUSE66A (held as
  `v2/vendor/ti/bq25731-datasheet.pdf`) gives the BQ25731 a switching frequency of 400 k / 800 kHz with a dithering
  pattern. `emc_sheet.py`'s SWITCHERS tuple has no "BQ25731", so the completeness test cannot see it. Main's sheet
  misses it the same way.

  Nothing else on board A matches a converter. U18 (TPS25740A) is a PD controller that drives U19's enable, and the
  eFuses do not switch.
- **Found on the way (outside board A, not judged):** board C carries a "boost inductor" L1 with no part in SWITCHERS;
  the IC that switches it was not identified in the time box.
- **Tools run in the clone.**
  - `rules_lib.py` (exit 0), `rules_lib.py requirements` (exit 0)
  - `rules_render.py --check`: exit 0, 16 documents, 0 out of date with the evidence installed. Without it,
    PCB-ETA.md reads stale and CURRENT-EVIDENCE is not rendered.
  - `rules_render.py --requirements --check` (exit 0), `decisions_render.py --check` (exit 0)
  - tests `test_constraints_bound` 36 passed, `test_interfaces` 10 passed
  - No gate or writer was run, and the clone's tracked tree is clean.
