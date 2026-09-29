mergeable: no

# AI review: independent check of stream s122, round 7, fnd/s122c at b76e5fd3 (S-122, CFL-016, MESHSAT-1357)

This is an AI review, not a qualified engineering review. Everything below is what I read or ran myself.

**Scope.** Narrow, by the owner's instruction of 29 September 2026: round 7's changes and the eight closing lines only.
The escape classes the scope statement names are minors. Blocking means one of: a closing line false against the
netlist or a maker's page; a closing figure with no binding, or a binding that does not state it; a round 7 change that
breaks a replay or the integrator sequence; a scope statement that claims more than the gate does.

**Set up**
* `fnd/s122c` is at `b76e5fd3` (read with `git rev-parse`). The work is `c3490c9b` and `43b5a25c`, on `1c187977`.
  `checks/check-s122-6.md` is byte identical to my predecessor's CHECK-6.md.
* Check clone: a shared clone at `<scratch>/chk-s122-7`, detached at the tip, remote removed.
* Integration clone: a shared clone at `<scratch>/chk-s122-7-int`, on `fnd/int16`'s tip `36bb1d12`, remote removed
  before any commit, commits with the owner's `-c` flags, never pushed. int16's 945 ignored files under `v2/ecad` and
  `v2/vendor` (minus `__pycache__`) were copied in from its worktree.
* Both clones are removed when this report is written. No real branch was committed to or pushed.
* Time: 29 September 2026, 23:41 to 23:58 CEST (from `date`).
* S-122's scope is nine documents: PANEL.md, CONOPS.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md,
  pcb_decisions.yaml (decisions 28 and 40), EMCON.md (section 0a.1) and DEFINITION-STATUS.md (its section), extended at
  set 14 by check-int15-1's findings. Their verdicts are in `verdicts.out`.
* One deviation from the rules: a read-only size count of the ignored files ran `cd /` inside a subshell. Nothing else
  used `cd`.

**What I read**
* CHECK-6.md, then `git diff 1c187977..b76e5fd3` of V2-SPEC.md, `apply_docs_s122_r7.py`, `judgements.py`,
  `s122lib.py`, `verdicts.py`, `close_s122.py`, `test_close_s122.py`, `apply_registry_s122_r4.py`, README.md (round 7
  section, the binding table, the run order) and LOG.md. The `.out` files I regenerated instead of reading.
* The eight closing lines at the tip.
* `gen_sch_p.py` lines 1 to 10, 55 to 66 and 161 (the CELL4 rail intent, the pack paragraph, `J_CELL`).
* With pdftotext: the Samsung INR18650-35E sheet ("3.3 Nominal Voltage 3.60V"), the RA30H1317M1 sheet's page heading and
  description, the LM5069 sheet's section 7.3 and its footnote, the TE 2199119 sheet's "Service Temperature".
* Board values through `s122lib.netlists`: D `U2`, `U6`, `U7`, `U15`, `U21`; A `Q27`, `Q38`, `U32`, `U6`, `U7`, `U15`.
* `fnd/reviewdc` at `4795d5bf`: `apply_findings.py`'s docstring and README's run order.

## Blocking

**B1. The registry sentence round 7 adds to S-122's title says the finder reads five-digit DS codes as part numbers; it
drops them.**
* `apply_registry_s122_r4.py`'s `S122_ADD4` (the scope statement the closure keeps in S-122's title) now reads: "the
  finder's shapes, which still read an upper-case commit, 'SMBJ15A/BAT54', a DS code of four or five digits (Maxim's
  DS3231 and DS12887 shapes among them) and the EMC test methods' names (CE102, RE102) as part numbers, which a judgement
  must then excuse". Round 6's text said "a DS code of four digits (the shape of Maxim's DS3231)", which was true.
* `s122lib.PN_LIT` holds `^DS\d{5}$`, so `is_partno` returns False for a five-digit DS code. Run through
  `s122lib.partnos`, at the tip and with `1c187977`'s `s122lib.py`:
  * "The clock is a DS12887 from Maxim." gives no part number;
  * "The Maxim DS12887 clock." gives none;
  * "the DS3231 clock" gives `DS3231` (four digits: read, as stated).
* The round's own texts say the opposite of the registry sentence: README m4 ("ST's DS with five digits keeps the shape
  of Dallas's DS12887, which the filter still drops (a stated limit)") and the comment above `PN_LIT` ("which this filter
  still drops").
* So the scope statement claims a real part shape is read and excused, where a document naming a DS12887-shaped part
  would pass unread. That is a claim beyond the gate. In the integration run the closed S-122's title carries the
  sentence ("DS3231 and DS12887 shapes among them" read back from `closed_items`).
* **Fix, one phrase of `S122_ADD4`:** "a DS code of four digits (Maxim's DS3231 shape) and the EMC test methods' names
  (CE102, RE102) as part numbers, which a judgement must then excuse, and do not read a DS code of five digits (Dallas's
  DS12887 shape, which the literature filter drops), 'SMBJ15A-based' or a plural 'SMBJ15As'". The script's read-back
  compares S-122's title with `S122_ADD4` itself, so nothing else moves; re-run the script's screen and step 1 of the
  sequence. The follow-up item's "false hits and misses (..., a DS code of four or five digits, ...)" is accurate as
  written and needs no change.

## Minor

**m1. A unit is compared only where the source states one, and five sources on the closing lines state none.**
* `_values` reads no unit in `PCB:X:outline=240x160` (the four board outlines), `PCB:C:hole=240x176`, `gen_sch_p.py`'s
  `_intent.rail("CELL4", 14.4, ...`, the first number of `E:J_DCIN~9 to 36 V`, and TE's "Service Temperature -40 ~ +80".
* With the key rewritten and the assertion kept, "330 x 200 cm" on V2-SPEC.md line 82 and "14.4 mV node" on line 81 pass
  the scan.
* The scope statements say so ("its unit where the source states one", README, registry sentence, `close_s122.py`'s
  docstring), so this is not an over-claim. Correction 36's "asserts every figure with a unit" (the wording check 6 m3
  asked for) is looser than that.
* **Fix:** read the board-file assertions as mm, and extend TE's assertion to its "+80˚C" (the sheet prints U+02DA, which
  `VAL_UNIT` does not read), or add "its unit where the source states one" to correction 36.

**m2. The closing evidence does not name `apply_docs_s122_r7.py`.**
* `close_s122.py`'s closing string lists `apply_docs_s122.py` to `apply_docs_s122_r6.py` as the scripts that corrected
  the documents. The closed S-122's `closing_evidence` in the integration run holds no "apply_docs_s122_r7".
* README's round 7 replay says "the closing evidence names S-126 and `apply_docs_s122_r5.py` to `_r7.py`". That is not
  so. The rebind entries do name `_r7.py` (the script's `REF`).

**m3. Two role mutants read TRUE that no round 7 text names.** None stands in the committed documents.
* Check 6's second (c) example, "the PCM2912A USB codec and amplifier" on line 84 (judged with the row's judgement), reads
  TRUE: `role_phrases` reads only "USB codec". README's m2 answer claims the first and third (c) examples, which read
  STALE, so nothing over-claims; the example is simply not carried.
* "the CSD18510Q5B VBUS20 switch" (line 81) reads TRUE: a qualifier holding a digit forms no role phrase. Board A's `Q38`
  is the VBUS20 bleed switch; `Q27` is the VBUS switch.
* **Fix:** add both to the follow-up item.

**m4. The follow-up item lists fewer classes than the scope statement.** Its title says "against the escape classes its
scope statement names:" and then lists five. The scope statement also names the active-parts limit of the one-word
qualifier test and the list item judged by the target rule. README names a load written in words other than "to the".
Say "among them", or list all.

**m5. Finder and tokenizer, observations.**
* "The Lapp article 0021917 cable." gives no part number, because `PN_MAKER` consumes "Lapp article" as maker and token.
  The document's form "(article 0021917" is read.
* An eight-digit date ("20260929") reads as a part number at both rounds. It is conservative; the removed guard never
  reached it, as round 7's comment says.
* Round 6's tokenizer reads no figure in "135-175 MHz" or "25 °C". Neither form is on the closing lines.
* Carried from check 6 m4, unchanged: the registry sentence's "an upper-case commit" (1C187977 is read, 1BAFAB8C is not).

**Integration note, not S-122's.** Merging `4795d5bf` onto `36bb1d12` conflicts in `v2/vendor/sources.txt`: both sides
append lines after line 458. I resolved it as the union (int16's two passives lines, then review D's Arlitech line).

## What holds

**1. Check 6's B1 is answered.**
* The "14.4 V node" key on line 81 is bound to `DOC:v2/ecad/tools/gen_sch_p.py~_intent.rail("CELL4", 14.4, 10.0, 18.0,
  "W_BP"`.
* `gen_sch_p.py` line 58 declares CELL4 at 14.4 V nominal, 10.0 to 18.0 V, always on, the top cell node of the block.
* Beside it in the judgement, each run and TRUE:
  * `P:J_CELL~4S block` (the value reads "cell tap sense wires from the 4S block (JST-XH 1x5)");
  * the generator's "one 4S3P block of Samsung INR18650-35E" (line 6);
  * the 35E sheet's "3.3 Nominal Voltage 3.60V" (4 x 3.60 V = 14.4 V).
* The BQ4050 sheet and `P:U1~4S balancing` are gone from the judgement.
* No closing-line judgement carries a test-condition binding. The only maker's pages among their assertions:
  * the SA868 output rows;
  * the RA30H1317M1 heading;
  * the LM5069 7.3 junction row (once in the text);
  * TE's service temperature;
  * the 35E nominal voltage.

**2. The 45-row binding table.**
* A script parsed all 45 rows of README's table. For each row it found the figure token on its line, the `figures_ok` or
  `counts_ok` key that spans it bound to exactly that assertion, and ran the assertion. All 45 hold, and each row's
  "What the source states" begins with `run_assert`'s own message. 0 mismatches.
* Maker's pages: the three rows with a PDF source.
  * 30 W: the sheet's heading "135-175MHz 30W 12.5V" and its description "a 30-watt RF MOSFET Amplifier Module". The
    figure is the part's rating; 12.5 V is the supply it is rated at.
  * -40 to +125 C: section 7.3 Recommended Operating Conditions, "TJ Junction temperature -40 125 °C" (the minus printed
    as U+2013, read as "-"). This is the range the line claims ("its recommended operating conditions").
  * -40 to +80 C: "Service Temperature -40 ~ +80˚C" (the line claims "service temperature").
* The other 42 rows I read against their sources as well:
  * netlist values: D `U2` 2 W; `E:J_DCIN` 9 to 36 V; A's three "5.1 V rail to B16"; `U13`, `U15`, `U16` +13V8_PA,
    +12V_HF, +54V_POE; `U18` 45 W; `U12` 3.3 V; `J_AB1` 2x13; `U41` two CAN-FD fabrics; E `F3` 25 A mini blade;
  * netlist counts: 11 SMPMAX footprints; 3 CM5 receptacles; 3 STM32H743; 7 `_CA` nets; 2 TS3DV642; 2 E72; 17 "3 mm"
    values (D1 to D16 and D22); 2 PCA9555; `J_HS1`, `J_HS2`; `J_FAN1`, `J_FAN2`;
  * board files: the outlines, layer counts, board C's 240 x 176 cutout, board B's In4 zones on the +5V nets, board E's
    eleven clamp zones;
  * records: decisions 43 and 27; `gen_sch_a.py` at `b2709118`, four AP64500 groups.
* Each states its figure as the kit's own value. None is a test condition, an example or another part's value.

**3. m1 of check 6 is answered.**
* `test_close_s122.py`: ALL PASS. T1 reads 8 lines. T2 has seven switches, each load-bearing. T4 refuses 45 of 45
  changes, and the five KEYED plants, with the keys rewritten. T5, with `_fig_match` accepting everything, lets 45 of 45
  through, and the gate refuses at the KEYED 1 W.
* My own plants, each with the judgement's covering keys rewritten to the new text and its assertions kept, so only the
  comparison can catch them. Each is refused by `figure_uncovered`:
  * range order swapped: "36 to 9 V input" (line 86);
  * sign changed: "-54 V PoE" (line 81);
  * second sign changed: "-40 to -80 C" (OPERATING-ENVELOPE.md line 83);
  * unit changed where the source states one: "3 cm LEDs" (line 83), "-40 to +125 V" (OPERATING-ENVELOPE.md line 77),
    "30 V VHF" (line 47), "13.8 A PA" (line 81);
  * transposed: "80 x 100 mm" (line 84).
* A respelled control, "25.0 A fuse", passes as it should. The two unit plants of m1 pass as the scope states.

**4. m2 of check 6, the two fixes.**
* All tests on, these read STALE:
  * "the CSD19532Q5B VBUS switch";
  * "the PCM2912A headphone amplifier and TPA6132A2 amplifier";
  * "the TPA6132A2 USB interface and PCM2912A amplifier";
  * my "the PCM2912A stereo amplifier and TPA6132A2 amplifier".
* With "wordmatch" off, the VBUS mutant reads TRUE. With "load" off, the three amplifier mutants read TRUE.
* Controls stay TRUE: "the PCM2912A USB codec and TPA6132A2 headphone amplifier" and "the CSD18510Q5B VBUS switch".
* The named escape classes are real and named truthfully. Judged on the rows, each reads TRUE and the scan passes it:
  * "the TPS22810 bias FET";
  * "the TLV75801 gate-bias generator";
  * "the TUSB2046B hub fitted since 26 September 2026 (`U4`";
  * "on `PA_KEY` (`U17`";
  * "an NVMe 2280 socket".
* The other finder shapes the sentence names hold as stated: "SMBJ15A/BAT54" is read as one token; "SMBJ15A-based" and
  "SMBJ15As" are not read; CE102, CS101, CS114 and RE102 are read; DS3231 is read. DS12887 is B1.

**5. Minors 3 to 6.**
* **`apply_docs_s122_r7.py`:**
  * on the tip it refuses (`4f1fd784`, not `c480bac2`);
  * on `1c187977`'s V2-SPEC.md, `--check` locates 1 edit;
  * pointing the CONOPS.md row of DEFINITION-STATUS.md's baselines table at V2-SPEC.md makes it refuse;
  * adding V2-SPEC.md to `s122lib.BASELINED` makes it refuse;
  * the real run writes a file identical to the tip, and a second run refuses.
* **The finder** reads S-8261, bq2970, ANN-MB2, 709GNK, 132170, 0021917 (in "Lapp's article 0021917") and 422B, and
  RM3100 and TN2106; RM0433 is not read.
* **Hex addresses:** `figure_tokens` reads no figure in "0x22" or "0x10".
* **String fields:** a string `counts_ok` or `figures_ok` covers nothing, with no crash.
* **The twelve newly judged sentences:** in `verdicts.out` they are the Xenarc 709GNK rows, the Amphenol 132170
  couplers, u-blox, Lapp, MG Chemicals 422B, and decision 40's S-8261 and bq2970. They are 1011 sentences against 1004,
  seven new.

**6. The follow-up item.**
* The follow-up item is S-135 in the integration run. It is SESSION, OPEN, disposition PROCESS, in no record's
  `waits_on`, and not in CFL-016's.
* Its title and `disposition_why` read back as the script's constants, and pass the script's claim screen.
* It names the EMC test methods without a standard's number. No "MIL-STD" string remains in the script.
* Its text matches check 6: m2 (a), (b) and (e) with check 6's own examples, m3's unit-less number, and m4's finder
  shapes. It quotes check 6's "None of these stands in the committed documents." exactly.
* `close_s122.py` refuses without it and names it in the closing evidence.

**7. Replays and the set 15 sequence.**
* **Replays at the tip, byte identical, nine of nine:**
  * `inventory.out`, `verdicts.out`;
  * `inventory-base.out`, `verdicts-base.out` at `e57a7365` (938 sentences, 74 STALE);
  * `inventory-set14.out`, `verdicts-set14.out` at `1bafab8c` (996, 10 STALE);
  * `verdicts-r4.out` at `edead832` (1005, 5);
  * `verdicts-r5.out` at `a6429e66` (1009, 1);
  * `verdicts-r6.out` at `1c187977` (1011, 0).
* **Review D first**, on `36bb1d12`:
  * the merge of `4795d5bf` conflicted in `v2/vendor/sources.txt` only (the integration note above);
  * `facts.py`: 55 facts, 0 FAIL;
  * `test_refusals.py`: 17 cases, 0 FAIL;
  * `apply_findings.py --check`: RD-C-01 extends S-101, RD-C-02 to RD-C-09 and RD-C-24 open S-126 to S-134, as its
    README says;
  * `apply_findings.py` wrote, and a second run refused;
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings. The trace page was rendered and committed.
* **Then S-122:**
  * **Merge.** `git merge --no-ff b76e5fd3` merged with no conflict.
  * **Step 1.** `apply_registry_s122_r4.py`:
    * rebound 5 records (CFL-010, CFL-013, CFL-014, CFL-016, REQ-005);
    * opened **S-135**, the next free number after review D's S-126 to S-134;
    * re-pinned the envelope and ENV-001 to `26e98ecfd2e4ec2f`;
    * a second run refused ("already applied").
    * Against the committed registry, only those five records, S-122 and the new S-135 changed. Review D's `waits_on` on
      CON-009, REQ-007, REQ-008, REQ-012, REQ-035, REQ-052 and REQ-060 stand intact, and the closed items are unchanged.
      The two scripts touch disjoint records.
  * **Step 2.** `rules_lib.py requirements`: 0 errors, 0 warnings. Then `rules_render.py --requirements`.
  * **Step 3.** `rules_status.py`, three times: exit 1 each, NOT_READY, 195 PASS, 39 FAIL, 104 INCONCLUSIVE of 338;
    the three outputs are identical and wrote nothing. The full `rules_render.py` moved CURRENT-EVIDENCE.md from
    `c9b98931` to `0f2c59cb` and the seven status pages. `rules_lib.py requirements` then read 0 errors and 2 warnings,
    CON-010 and REQ-044, as README's set 15 order says.
  * **Step 4.** `inventory.py` and `verdicts.py`: 1011 sentences, 422 TRUE, 0 STALE, 40 BASELINE, 549 NOT DERIVABLE, 0
    UNJUDGED. The only line that moved in each is the header, where `pcb_decisions.yaml` goes from `a41df5d1` to
    `823a6b32`. Committed with the registry and the pages.
  * **Step 5.** A fixture check (first line "mergeable: yes", naming check-int15-1, the nine documents, `verdicts.out` and
    the eight lines) was refused while only staged ("not committed on a line that carries 097d2517"), then committed.
  * **Step 6.** `test_close_s122.py`: ALL PASS.
  * **Step 7.** `close_s122.py` closed S-122; CFL-016 reads PASS with its `waits_on` dropped. S-42, S-123 to S-126, S-134
    and S-135 stay open, among others.
  * **Step 8.** A second run refused ("S-122 is not open").
  * **Step 9.** `rules_lib.py requirements`: 144 records, 0 errors, 2 warnings (CON-010, REQ-044). `rules_lib.py`: 59
    rules, 0 errors, 0 warnings.
  * **Step 10.** `rules_render.py --requirements`, then `tests/run.py test_requirements test_envelope_data`: 72 passed, 0
    failed, 0 skipped. `claims_check.py`: PASS, 91 of 91.
* No step was refused or conflicted because of S-122.

**8. Text rules.**
* Added lines of the diff: no U+2013 or U+2014 (the Python sources name them only as backslash-u escape sequences).
* No internal host name, user path or address.
* CONOPS.md is the `c5430071` file (`6cb7b241cb84d729`) and PRODUCT-BRIEF.md is unchanged since `1bafab8c`. Neither
  moved in the integration run.

**9. The eight closing lines** (what I verified on each, for the next round).
* **V2-SPEC.md line 47.** 2 W is D `U2`'s value, "NiceRF SA868 VHF 2 W exciter". 30 W is the RA30H1317M1 sheet's rating.
  `U6` is the PCM2912A.
* **V2-SPEC.md line 81.** Board A is 240 x 160 mm on six layers. 14.4 V is P's CELL4 (B1 answered). 9 to 36 V is E
  `J_DCIN`. The three 5.1 V slot rails are `J_5V_S1` to `J_5V_S3`. Four AP64500 is `gen_sch_a.py` at `b2709118`. 13.8,
  12 and 54 V are the nets of `U13`, `U15` and `U16`. 45 W is `U18`, 3.3 V is `U12`. Eleven SMP-MAX is `J_BM1` to
  `J_BM11`. 2x13 is `J_AB1`.
* **V2-SPEC.md line 82.** Board B is 330 x 200 mm on six layers, with In4 zones on the +5V nets. Decision 43 has eight
  layers. The counts are three CM5 receptacles, three STM32H743, `U41`'s two CAN-FD fabrics, seven `_CA` nets, two
  TS3DV642 and two E72.
* **V2-SPEC.md line 83.** Board C is 344 x 228 with a 240 x 176 cutout, on four layers. Decision 27 rules six layers.
  There are seventeen "3 mm" LEDs and two PCA9555.
* **V2-SPEC.md line 84.** Board D is 100 x 80 mm on four layers, with two headset jacks. The roles hold: `U6` codec,
  `U7` amplifier, `U15` TLV75801 on `PA_KEY`, `U21` TPS22810 on `+5V_TX`.
* **V2-SPEC.md line 86.** Board E is 267 x 68 mm on four layers. 9 to 36 V is `J_DCIN`, 25 A is `F3`. There are eleven
  clamp zones and two fan headers.
* **OPERATING-ENVELOPE.md line 77.** 9 to 36 V is `J_DCIN`. -40 to +125 C is the LM5069's 7.3 junction row, with its
  sign.
* **OPERATING-ENVELOPE.md line 83.** -40 to +80 C is TE's service temperature.
* All 45 figures hold against their sources, and I found no false closing line. What keeps this report from closing is
  B1, a sentence of the scope statement.

## Counts

Committed `verdicts.out` at `b76e5fd3`, reproduced byte for byte:

| Document | Sentences | TRUE | STALE | BASELINE | NOT DERIVABLE | UNJUDGED | Assertions |
|---|---|---|---|---|---|---|---|
| PANEL.md | 167 | 131 | 0 | 0 | 36 | 0 | 787 |
| CONOPS.md | 288 | 51 | 0 | 40 | 197 | 0 | 784 |
| V2-SPEC.md | 159 | 64 | 0 | 0 | 95 | 0 | 486 |
| OPERATING-ENVELOPE.md | 67 | 22 | 0 | 0 | 45 | 0 | 165 |
| TEST-PLAN.md | 110 | 18 | 0 | 0 | 92 | 0 | 128 |
| ASSEMBLY.md | 160 | 91 | 0 | 0 | 69 | 0 | 242 |
| pcb_decisions.yaml | 10 | 6 | 0 | 0 | 4 | 0 | 17 |
| EMCON.md | 26 | 22 | 0 | 0 | 4 | 0 | 455 |
| DEFINITION-STATUS.md | 24 | 17 | 0 | 0 | 7 | 0 | 276 |
| **Total** | **1011** | **422** | **0** | **40** | **549** | **0** | **3340** |

This round's findings: 1 blocking (B1, the DS12887 sentence of the registry scope statement), 5 minor. Figure tokens
checked: 45 of 45 bound and stated. Own plants: 8 wrong figures, 8 refused.
