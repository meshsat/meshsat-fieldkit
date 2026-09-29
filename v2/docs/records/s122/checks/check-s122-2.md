mergeable: no

# AI review: independent check of stream s122, round 2, fnd/s122b at 83cb0640 (S-122, CFL-016, MESHSAT-1357)

This is an AI review, not a qualified engineering review. Everything below is what I read or ran myself.

**Set up**
* `fnd/s122b` at `83cb0640d21cc37ebaccb9e87d81c50c8a851a07` (`git rev-parse fnd/s122b`), nine commits on main `b874b744`; the worktree `s122b` is at the same commit.
* Shared clones in my session scratchpad:
  * one at the tip, to read;
  * one at `b874b744`, then at `1594090e` (round 1 on this branch), for the document scripts;
  * one at the tip for the registry script and the closure. In that throwaway clone one commit of four fixture checks was made with the owner's `-c` flags, as the brief asks. It was never pushed, and no real tree was touched.
* Time: 29 September 2026, 18:41 to 18:55 CEST (from `date`).
* Rule tools ran with `VERDICT_DIR` in scratch.

**What I read**
* The nine documents:
  * `v2/docs/PANEL.md`: lines 59, 89, 90, 107, 156, 180, 201, and the whole file in round 1;
  * `v2/docs/CONOPS.md`: lines 1 to 60, 297 to 324, 397 to 460, 478 to 493, 588 to 660, 730 to 750, 840 to 918;
  * `v2/docs/V2-SPEC.md`: lines 3, 30, 81, 82, 262 to 290, and the whole file in round 1;
  * `v2/docs/OPERATING-ENVELOPE.md`: line 286 and section 4;
  * `v2/docs/TEST-PLAN.md`: line 54, and round 1's lines, unchanged since (`42a3dff3`);
  * `v2/docs/ASSEMBLY.md`: lines 81 to 95, 116 to 181, 198 to 224;
  * `v2/ecad/tools/pcb_decisions.yaml`: decisions 28 and 40, unchanged since round 1;
  * `v2/docs/feasibility/EMCON.md`: section 0a.1 (lines 212 to 246) whole, and every line naming CONOPS;
  * `v2/docs/handover/DEFINITION-STATUS.md`: lines 3 to 30, 92 to 127 (its new row and its new section whole), 250 to 270.
* Records and tools:
  * `v2/docs/records/s122/verdicts.out`: every CONOPS entry (247), every EMCON.md and DEFINITION-STATUS.md entry, ASSEMBLY sections 2 and 9, every entry carrying a FAILS line;
  * `README.md`, `LOG.md`, `s122lib.py`, `verdicts.py` (the decision logic), `apply_docs_s122_r2.py`, `close_s122.py`, `apply_registry_s122.py` (by its output);
  * the registry records S-122, CFL-016, REQ-077, CON-017, CON-003, CON-022, S-42.
* Other files:
  * `v2/docs/ARCH-PCB-B-IOHA.md` lines 98 to 108;
  * `v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27-pass1.md` lines 190 to 200;
  * the lines of EXECUTION-PLAN.md, ZEROIZE.md, V2-SPEC.md and PANEL.md that cite CONOPS section 4b or CONOPS line numbers.
* Netlists and generators:
  * the six netlists of set 13, parsed with `tx_inhibit.parse_netlist`: A `6c40250c`, B `3ef9b8c4`, C `c9f73945`, D `a2d48972`, E `2ed95a0e`, P `20c7b079`;
  * board B's netlist at `45bde541`, `95e078a1` and `a9f212c7`; board C's at `e57a7365` and `a9f212c7`;
  * `gen_sch_a.py` and `gen_sch_e.py` at the DC-06 lines.

## Blocking items

**B1 (round 2). A CONOPS circuit statement that is false on every netlist since before the baseline is judged NOT DERIVABLE and has no DC row.**
* Where:
  * `v2/docs/CONOPS.md` line 310 (section 4, Reduced row, the Guarantee cell): "the supervisors' I2C status path, absent as generated (`ARCH-PCB-B-IOHA.md` section 6)".
  * Lines 490 to 492 (section 4c): "Dropping `SLOT_EN1` as a routine act rests on three board B items owed as generated ... and the supervisors' I2C status path".
  * `verdicts.out` entries `CONOPS.md#4:L310:cell:5:s2` and `CONOPS.md#4c:L478:para:s3`, both NOT DERIVABLE ("HELD DOCUMENT").
* Against the netlists:
  * On set 13, `U41`, `U51` and `U61` have pin 93 (PB7) on `SDA` and pin 92 (PB6) on `SCL`, the kit bus the panel controller masters.
  * The same pins are on `SDA` and `SCL` at `45bde541`, at `95e078a1` (where this text was written, 27 September 12:34) and at `a9f212c7` (the baseline).
  * `ARCH-PCB-B-IOHA.md` line 104 reads "CORRECTED at `458b2873` ... SDA and SCL are PB7 and PB6". Review A's m3, which the sentence follows, misread that corrected finding as open.
* Why blocking:
  * The sentence names a circuit fact the netlists decide, and it is false.
  * By the stream's own rule, a CONOPS passage that differs from the netlists is BASELINE only with a DC row and STALE without one. DC-01 to DC-06 do not cover it.
  * So `close_s122.py` would close S-122 on "0 STALE" and set CFL-016 to PASS over a false statement in section 4, which CFL-016 names.
* Fix:
  * Add a DC row (the supervisors are kit bus targets on PB7 and PB6 since `458b2873`; the TCA9517A segment of SC-HF-02 is owed on the generator), and judge both sentences BASELINE on it.
  * In the same pass, judge the FAB-02 clause beside it ("which nothing does as generated") against board B's round 8 `U519` and `U520` (PANEL.md section 5) and S-42's list, rather than as a held document.

## 1. The baseline rule's application

* **CONOPS.md is `c5430071`'s file.** `cmp` against `git show c5430071:v2/docs/CONOPS.md` is identical; sha256 `6cb7b241cb84d729...`. `c5430071` adds only D-19, D-20 and M1's owner instruction to the re-stamped baseline `edd3c848`.
* **The DC rows are true on set 13's netlists.**
  * DC-01: `U536`, `U543`, `U537` to `U553`, `U116`/`U216`/`U316` and `U35` to `U38` as stated.
  * DC-02: `Q11` 2N7002, gate `HOT_R1_G` on `U10` pin 30 with `R58`, drain `BLK_SPARE` at `J_BLK` pin 12; board A `DOCK_SPARE` at `J_DOCK` pin 12, `R216` 10k to +3V3, `U27` pin 18 (IO1_5); REQ-077 INCONCLUSIVE, waits on S-58.
  * DC-03: `D3` from `LED_RAIL` through `R36`; `Q1` drain `LED_RAIL`, gate held off by `R17`, driven only by `Q2` from `PANEL_PWM` through `R19`, `R20` 100k to GND; `D22` from `LED_RAIL_SW` through `R47`.
  * DC-04: `U7` LM5176 on `+5V_DEV`; `U25` AP63203 from `+5V_DEV`.
  * DC-05: `U112`/`U212`/`U312` on each module's 3.3 V; `U543` on `+5V_DEV` watching `+3V3_DEV`, output `RB_IEN`.
  * DC-06: every line cited holds its part at the tip, and `gen_sch_a.py` and `gen_sch_e.py` are byte identical to `e57a7365`'s.
* **Consistency with CFL-016 and the H2 rule.**
  * CONOPS's head says an "as generated" remark "is its value when this document was baselined; its current value is kept where the list below says". DEFINITION-STATUS.md says a circuit correction updates the status page, not the baseline.
  * CFL-016's acceptance field is unchanged. The new CFL-016 entry records that CONOPS is read through the status page and that the places the rows name "must describe the circuit as generated".
  * I read that as consistent with both texts, on one condition: every CONOPS circuit statement that differs from the netlists must have a row. B1 is one that does not.
  * DC-03 and DC-04 are also not changed values: CONOPS had them wrong at its own reading (board C's `R36` on `LED_RAIL`, and board B's `U25` making `+3V3_DEV`, at `45bde541` and at `a9f212c7`). See m3.
* **What else is now contradicted.**
  * PANEL.md line 156 and V2-SPEC.md line 24 cite CONOPS section 4b for values the restored 4b no longer carries (m1, m2).
  * EXECUTION-PLAN.md line 629 says 4b and the EMCON row "are rewritten" (observation).
  * EMCON.md's other CONOPS citations (lines 54, 300, 1671, 2150) are dated to `b69f20db` and unaffected.
  * `feasibility/ZEROIZE.md`'s `CONOPS.md:404` (and `:212`, `:215`, `:400`) was written at `9b0635d1` against the file before the restructure. It pointed at other text at the base and still does. The D-13 row is line 1056; the restore neither caused nor fixed this (observation).
  * The only pins of the replaced CONOPS sha (`3c5d4907`) are in the registry and its trace page, which the registry script moves.

## 2. Round 1's items

* **B1** (HOT-R1): answered. 4f's edit is withdrawn. Lines 311 and 312, 4c's HOT-R1 passages, 4c line 715 and 4f are BASELINE on DC-02, which is true.
* **B2** (ASSEMBLY section 9's counts): answered.
  * Lines 87, 217, 218 and 219 read 17 Mill-Max 0858 pins, two E-key sockets `J_M2C1`/`J_M2C3`, and 17 LEDs on `LED_D3.0mm` with `D22`; I counted each on the netlists.
  * The count rule holds everywhere but one ordinal ("the first three reaching their switches", PANEL line 156).
* **B3** (the TX lamp): answered. The TRUE verdict is withdrawn and the sentence is BASELINE on DC-03, which is true.
* **m1:** answered. The preamble is withdrawn. 0a.1's list `EMCON_A` asserts the inputs of `U214`/`U314`, `U547` to `U550` and `U540` to `U542`, the supplies of `U540` to `U542`, and `F3`.
* **m2:** answered. OPERATING-ENVELOPE.md line 286: "on the PA's rail and bias"; `U15` is enabled by `PA_KEY`.
* **m3:** withdrawn with the restore.
* **m4:** answered (`e57a7365`).
* **m5:** answered (`J_VN1` to `J_VN4` on GND, 9 A class).
* **m6:** answered: MOSI, SCK and NSS through `U548` to `U550`; MISO through `U553` (`LORA_MISO` to `SPI3_MISO`).
* **m7:** answered, plus line 30. `U1` is the seven-port KSZ9897R; `U18` TPS25740A and `U19` LM5176; `U41`, `U51` and `U61` read STM32H743VIT6; CON-017 reads PASS; `c5de605d` line 267 names the TPS55288 as gone.
* **m8:** answered (the 29 September heading; line 3 names it).
* **m9:** answered in part. Each entry now names which parts of the change the record's own text names; the entries still do not re-read the argument.
* **m10:** answered. My staged fixture refused ("not committed at HEAD as it stands").
* **m11:** answered. The closure entry names `SCOPE` and what is outside it.
* **m12:** answered in part. TEST-PLAN.md line 54 is inventoried (NOT DERIVABLE, TEST) and true. B1 above is an in-scope sentence the finder did inventory; the instrument's gap there is the verdict, not the finder.

## 3. Round 2's corrections and sampling

* **Each correction, read against the netlists.**
  * PANEL.md lines 89 and 90: `U3` GPIO2 to GPIO5 on `EPD_SCL_R`, `EPD_SDA_R`, `EPD_DC_R`, `EPD_CS_R`; `R53` to `R56` 27R to `EPD_SCL`/`SDA`/`DC`/`CS`, at `J_EPD` pins 13, 14, 11, 12. Board C's only change at set 13 is `R53` to `R56` and `U3` pins 4 to 7, from a parsed comparison with `e57a7365`'s netlist.
  * PANEL.md line 156 (m6) and line 180 (set 13's shas).
  * OPERATING-ENVELOPE.md line 286.
  * ASSEMBLY.md lines 87, 180, 204, 217, 218 and 219.
  * V2-SPEC.md lines 3, 30, 81 and 82, and correction 32 under its own heading.
  * All are true and minimal.
* **Sampling.**
  * Boards A, B, D, E and P have the same netlist shas as set 12, so my round 1 reading of PANEL.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md and decisions 28 and 40 (more than 20 sentences each) stands on set 13.
  * In CONOPS.md I read all 34 BASELINE, all 27 TRUE, and the 103 NOT DERIVABLE sentences that name a part or net or state what is generated, owed or absent.
  * In EMCON.md 0a.1 and the status page's section I read all 21 and all 14 sentences, and checked the circuit claims on the netlists (0a.1's preamble and rows as in check-int13-3; board C's `U9`, `R52`, `D23` on set 13).
  * Found: B1. No other NOT DERIVABLE or BASELINE verdict I read is TRUE or STALE instead.

## 4. Replay

* **Round 1 on `b874b744`.** `apply_docs_s122.py` refuses there (board C's netlist is set 13's). But the six documents at `b874b744` are byte identical to `e57a7365`'s, and at `1594090e` to `dac1b672`'s, which I replayed byte for byte in round 1.
* **Round 2.** `apply_docs_s122_r2.py --check` on `1594090e`: 16 edits located, 497 assertions hold. The run gives all eight changed documents byte identical to `83cb0640`, and a second run refuses.
* **Outputs.** `inventory.py` and `verdicts.py` (with `--stdout`) at the tip and with `S122_AT=e57a7365` reproduce `inventory.out`, `verdicts.out`, `inventory-base.out` and `verdicts-base.out` byte for byte.
* **Registry script.** `apply_registry_s122.py` rebinds 20 records and refuses a second run. `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings. `rules_lib.py`: 59 rules, 0 errors.
* **Closure**, in the throwaway clone:
  * a staged fixture refuses;
  * committed fixtures refuse without EMCON.md and DEFINITION-STATUS.md, and with `mergeable: no`;
  * the full committed fixture closes S-122 and sets CFL-016 to PASS (S-123 stays open);
  * a second run refuses.
  * After it, `rules_lib.py requirements` gives 0 errors, and after `rules_render.py --requirements`, `tests/run.py test_requirements test_envelope_data` gives 71 passed, 0 failed, 1 skipped.

## Minor items

* **m1.** `v2/docs/PANEL.md` line 156 cites "`CONOPS.md` section 4b" for the E72s' open-drain gates `U540` to `U542`; the restored 4b's E72 row names only `U505`. Cite EMCON.md section 0a.1.
* **m2.** `v2/docs/V2-SPEC.md` line 24 (a line CFL-016 names) states the RockBLOCK's ENABLE held low since w4b and cites "`CONOPS.md` section 4b", which now says "ENABLE driven only by the firmware expander `U6`". Cite EMCON.md section 0a.1.
* **m3.** DC-03 and DC-04 give values CONOPS already had wrong at `45bde541` and at the baseline, while the section's lead says CONOPS carries "its value when the document was baselined". Say in those rows that the baseline text was wrong at its reading, not overtaken.
* **m4.** DEFINITION-STATUS.md's baselines table (line 22) names CONOPS files up to `6ebe6760` and `4483209659dc391c`. The new section rests on `c5430071`'s `6cb7b241`, which the table does not name.
* **m5.** The README and 0a.1's judgement say 495 assertions; `apply_docs_s122_r2.py` prints 497 on `1594090e`.
* **m6.** The README cites `cb446b03`, `c263ddce` and `53292087`, which are on `fnd/s122` and are not ancestors of `83cb0640`. This branch's commits are `51952c0c` and `29acd948`.
* **m7.** The parser splits a wrapped list item from its continuation lines, so a sentence across them is judged in two halves (CONOPS lines 845 to 846 and 865; V2-SPEC's corrections). I saw no stale claim hidden by it.
* **m8.** Two count excuses name the wrong thing: V2-SPEC line 41's "two nano-SIM holders" is excused as "case items", and ASSEMBLY line 92's "two headset jacks" with a sentence about light guides. Both counts are true (`J_SIM1`, `J_SIM2`; `J_HSJ1`, `J_HSJ2`); `counts_ok` is not checked by the script.

*Observations, not counted:* EXECUTION-PLAN.md line 629 and ZEROIZE.md's CONOPS line citations, above.

## Counts

* **Blocking: 1** (B1: the supervisors' I2C status path, CONOPS lines 310 and 490 to 492, NOT DERIVABLE with no DC row). **Minor: 8.**
* Documents named and read: PANEL.md, CONOPS.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md, `pcb_decisions.yaml` decisions 28 and 40, `feasibility/EMCON.md`, `handover/DEFINITION-STATUS.md`, and `verdicts.out`.
* Round 1's items: B1 to B3 answered; m1 to m12 answered, two in part.
* DC rows true: 6 of 6. Round 2 corrections true: 16 of 16.
* Replays: byte identical; validators 0 errors; tests 71 passed, 0 failed.
