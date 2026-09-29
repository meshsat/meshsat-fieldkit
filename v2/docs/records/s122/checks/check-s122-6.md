mergeable: no

# AI review: independent check of stream s122, round 6, fnd/s122c at 1c187977 (S-122, CFL-016, MESHSAT-1357)

This is an AI review, not a qualified engineering review. Everything below is what I read or ran myself.

**Set up**
* `fnd/s122c` is at `1c187977` (read with `git rev-parse`). The work is `19bddf75`; `1c187977` holds the README and LOG. Both sit on `a6429e66` and answer check-s122-5, filed as `checks/check-s122-5.md`, byte identical to my CHECK-5.md.
* Check clone: a shared clone at `<scratch>/chk-s122-6` at the tip, remote removed.
* Throwaway clone for the integrator sequence: `<scratch>/chk-s122-6-int`, a shared clone:
  * checked out at `fnd/int16`'s tip `36bb1d12` (set 15; S-125 open, CFL-016 FAIL waiting on S-122);
  * remote removed before any commit, commits with the owner's `-c` flags, never pushed;
  * int16's ignored files copied in from its worktree, as the integrator installs them.
* Both clones are removed when this report is written.
* Time: 29 September 2026, 22:50 to 23:18 CEST (from `date`).
* S-122 was extended at set 14 by check-int15-1's findings. Its scope is nine documents: PANEL.md, CONOPS.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md, pcb_decisions.yaml (decisions 28 and 40), EMCON.md (section 0a.1) and DEFINITION-STATUS.md (its section). Their verdicts are in `verdicts.out`.

**What I read**
* CHECK-5.md, then `git diff a6429e66..1c187977` in full. I read every file except `verdicts-r5.out`, which I regenerated instead:
  * V2-SPEC.md;
  * README.md and LOG.md;
  * `apply_docs_s122_r6.py`, `close_s122.py`, `test_close_s122.py`;
  * `verdicts.py`, `s122lib.py`, `judgements.py`;
  * `apply_registry_s122_r4.py`;
  * the `.out` diffs.
* The six set 14 netlists through `s122lib.netlists`:
  * A `6c40250c`, B `3ef9b8c4`, C `c9f73945`, D `a2d48972`, E `2ed95a0e`, P `20c7b079`.
  * On board D, U2, U6, U7, U15, U21 and K1, with their pin maps.
* The board files through `verdicts.board_geo`: outlines, layer counts, inner cutouts, zone nets per inner layer, zone names.
* Generators:
  * `gen_sch_d.py` at the tip, at `bdfc7b3f` and at its parent;
  * `gen_sch_a.py` at `b2709118` (its four rail groups);
  * `gen_sch_b.py` (the voters, lines 1877 to 1917);
  * `gen_sch_p.py` (the rail intents);
  * `git log -S` of the SA868 texts.
* Makers' sheets, read with pdftotext:
  * NiceRF SA868 v1.3;
  * Mitsubishi RA30H1317M1;
  * TI LM5069 (7.3);
  * TE 2199119;
  * TI BQ4050;
  * Samsung INR18650-35E.
* Records:
  * `pcb_decisions.yaml` decisions 27 and 43;
  * appendix 32.49 (line 2752 heading, line 2765 row 8);
  * DEFINITION-STATUS.md's "## The two baselines" table.

## Blocking

**B1. V2-SPEC.md line 81's "14.4 V node" is bound to an assertion that states TI's test condition, not the kit's node.**
* The binding is `judgements.py` line 1826: `"14.4 V node": "PDF:v2/vendor/battery/ti-bq4050.pdf~VCC = 14.4 V"`.
* In the BQ4050 sheet that text is TI's characterisation condition, repeated on every electrical table: "Typical values stated where TA = 25°C and VCC = 14.4 V, Min/Max values stated where TA = [minus]40°C to 85°C and VCC = ..." (the minus is printed as U+2013) (pdftotext lines 639, 684, 704 and on).
* So the assertion is a property of the datasheet. It holds whatever pack board P carries: a 3S or a 5S block would leave it true.
* The scan accepts it because the token's digits (144) occur in the assertion's content.
* The judgement's extra `P:U1~4S balancing` is not the binding, and it is the gauge's capability.
* The figure itself is true. The tree has sources that state it, each of which I ran as an assertion and each holds:
  * `DOC:v2/ecad/tools/gen_sch_p.py~_intent.rail("CELL4", 14.4, 10.0, 18.0, "W_BP"` (the cell node declared at 14.4 V);
  * `DOC:v2/ecad/tools/gen_sch_a.py~the pack at its 14.4 V nominal`;
  * `P:J_CELL~4S block`;
  * `PDF:v2/vendor/battery/samsung-35e-orbtronic.pdf~3.3 Nominal Voltage 3.60V` (4 x 3.60 V).
* A binding that asserts something other than the figure it covers blocks by this check's terms. Two more places carry the same binding:
  * the README's binding table ("the BQ4050 sheet's "VCC = 14.4 V" (board P's `U1`, "4S balancing")");
  * the closure's registry sentence ("bound to an assertion of ... a maker's page").
* **Fix:**
  * Bind "14.4 V node" to the `gen_sch_p.py` rail intent, or to the `gen_sch_a.py` sentence, with `P:J_CELL~4S block` beside it.
  * Correct the README table.
  * Re-run the outputs.
* The other 44 bindings assert their figures (the table under "What holds").

## Minor

**m1. The scan's binding test compares digit sets, and no test pins it.**
* `figures_uncovered` (`verdicts.py` 170 to 190) strips signs (line 151) and drops decimal points. It accepts a token when each of its numbers occurs anywhere in the assertion's content.
* I planted each change below, moved the row's judgement and rewrote the `figures_ok` key to the new text, keeping the assertion. Each reads TRUE, and (b) and the scan pass:
  * "160 x 240 mm" on line 81 (the outline, transposed);
  * "2x2 ribbon" on line 81;
  * "+40 to +80 C" on OPERATING-ENVELOPE.md line 83;
  * "+40 to +125 C" on line 77.
* The LM5069 assertion itself drops the minus sign: "Junction temperature|40 125 °C (1) For detailed information on soldering plastic VSSOP". Round 6 also rewrote round 4's TRACO judgement (`75f96bbf14`) to that form.
* **No test exercises the digit comparison.** I replaced `figures_uncovered` with a version that only checks that a bound key spans the token. `test_close_s122.py` still printed ALL PASS, T3 and T4 included.
  * T4's 45 refusals come from the key phrase no longer matching the changed text.
  * So do the README replay's refusals ("-40 to +85 C", "330 x 210 mm", "twelve float clamps").
* **Fix:**
  * Compare the token's ordered, signed numbers with the assertion's.
  * Pin the sign of the LM5069 range: the sheet prints the minus as U+2013, which the no-dash rule keeps out of a judgement's text, so normalise it to a hyphen in the PDF reader before comparing, and assert "-40 125".
  * Add a T5 that rewrites the key and keeps the assertion.

**m2. The role rule's history tie and noun list still let stale text through.** None of these stands in the committed documents. All read TRUE through `close_s122._judge_as` with the row's own judgement:
* **(a) The history tie** (`verdicts.py` 379 to 417) excuses a part when its clause, bounded only by `;`, `(` and `)`, holds a date or one of the words of `HIST`. So a current claim hides as history:
  * "the TUSB2046B hub fitted since 26 September 2026 (`U4`";
  * "the TUSB2046B hub, the grade that was bought (`U4`";
  * "the TUSB2046B hub named on the BOM (`U4`".
* **(b) Nouns outside `ROLE_NOUN` are not read:** "the TPS22810 bias FET", "the TPS22810 bias source", "the TLV75801 gate-bias generator".
* **(c) The forward test reads a role word in a value that names it as the part's load.** D `U6` says "stereo output to the headphone amplifier". So these read TRUE:
  * "the PCM2912A headphone amplifier";
  * "the PCM2912A USB codec and amplifier";
  * "the TPA6132A2 USB interface and PCM2912A amplifier" (the swap, with an unlisted noun on one side).
* **(d) The reverse test compares a one-word qualifier by substring in the part's own values** (line 615). "the CSD19532Q5B VBUS switch" passes through Q38's "VBUS20 bleed switch". The VBUS switch is A `Q27`, a CSD18510Q5B.
* **(e) A designator written with a part is not tied to it:**
  * "the TLV75801 gate-bias LDO on `PA_KEY` (`U17`" (U17 is the hub LDO);
  * "the TPS22810 load switch of the exciter's `+5V_TX` (`U15`)";
  * "the AP64500 buck on slots 1 and 3, `U5` and `U7`".
* **At the gate.** In the throwaway clone I edited line 84 two ways and ran `close_s122.py` each time (judgement moved, outputs re-run, V2-SPEC.md's sha rebound in the registry):
  * **First plant:** it replaced "the TUSB2046I hub (`U4`" and "the TPS22810 load switch of the exciter's". It was refused at (e), only because the MUTANTS lost their anchor text.
  * **Second plant:** it added "with the TUSB2046B hub fitted since 26 September 2026 as the second hub" and "a PCA9555 and the TPS22810 bias FET". `close_s122.py` closed S-122 and set CFL-016 to PASS.
* The registry sentence's "Out of scope by design" names none of (a) to (e) or m1.
* **Fix:**
  * Tie a history excuse to a past-tense verb on the part itself, not to any date in the clause.
  * Read the noun after a part as a role whatever it is, and fail an unknown noun.
  * In the forward test, skip a value phrase "to the <role>".
  * Match the qualifier as a word.
  * Tie "(`Ux`" to the part before it.

**m3. Wording.**
* Correction 36 (V2-SPEC.md line 324) says the closing check "asserts every figure and unit on the lines it closes". Unit-less numbers are not asserted:
  * I planted "an NVMe 2280 socket" on line 82 with the judgement moved; it reads TRUE and the scan passes it;
  * the true value is board B's "M.2 M-key 2242 socket", `J_M2N1` to `J_M2N3`.
  * Say "every figure with a unit, and every spelled count".
* The closure's registry sentence and S-122's round 6 title name the binding sources as netlist values, board files, makers' pages and decisions' records. "all four AP64500 on 7 September" is bound to a generator's text at a commit (`CNT@b2709118`).

**m4. The finder.** I read every scoped sentence of the nine documents: 148 distinct part tokens found, 732 tokens with digits not found.
* **Misses (real parts):** none stands as a claim that the part is on a board where the netlist says otherwise.
  * ABLIC S-8261 and TI bq2970: decision 40, `pcb_decisions.yaml` line 896. The sentence is not inventoried, because it names nothing the finder reads.
  * u-blox ANN-MB2: V2-SPEC.md line 50.
  * Xenarc 709GNK: PANEL.md line 64, which reads TRUE, and V2-SPEC.md lines 56 and 95.
  * Amphenol 132170, six digits after the maker's word: V2-SPEC.md lines 10 and 149, ASSEMBLY.md lines 166 and 224.
  * Lapp 0021917: ASSEMBLY.md line 175.
  * MG Chemicals 422B: ASSEMBLY.md line 224.
* **False hits.** All are conservative, since each needs an excuse:
  * the MIL-STD-461 methods CE102, CS101, CS114 and RE102 (RS103 is now excluded, its siblings are not);
  * DCF77 (a transmitter);
  * TE's product specifications 108-115042 and 108-115049 (on OPERATING-ENVELOPE.md line 83);
  * JLC04162H-7628;
  * a nine-digit number (123456789).
* **`PN_LIT` also drops real part shapes.** None is in the documents today:
  * RM3100 (PNI magnetometer);
  * TN2106 (Microchip FET);
  * DS12887 (RTC).
* **Dead guard.** The date guard `20\d{6}` inside the `\d{9,}` branch (`s122lib.py` 334) can never match.
* **The registry sentence** says the finder "reads an upper-case commit". It reads some: "1C187977" yes, "1BAFAB8C" no (two digits).
* **DS1234 kept as a part shape: sound.** A false part needs a `parts_ok` excuse and never passes silently. The premise "the shape of Maxim's parts" is not exclusive: ST's older datasheet codes are DS with four digits too.

**m5. The run order on set 15.** Merged onto `36bb1d12`:
* **The outputs' header.** `pcb_decisions.yaml` is `823a6b32` (set 15's decision 59), so the committed `inventory.out` and `verdicts.out` differ from the closure's re-run in their header line. The closure refuses ("the committed inventory.out is not this commit's"). The bodies are identical. The README's "If a document of the scope changes on main before step 5" covers it; the integrator must re-run and commit both.
* **The render moves CURRENT-EVIDENCE.md.**
  * The full `rules_render.py` moves it from `c9b98931` to `0f2c59cb`: SGN-001's seven readings leave CURRENT_CANDIDATE (set: 83 to 76) after the registry and ENV-001 change.
  * So `rules_lib.py requirements` reads 0 errors and 2 warnings, CON-010 and REQ-044.
  * On `36bb1d12` alone, status and render leave the tree clean.
  * The run order names neither the rebind nor the SGN-001 re-take.

**m6. Robustness.**
* `figures_uncovered` raises AttributeError on a judgement whose `counts_ok` is a string. Six judgements in the tree have one, none on a closing line. A closing line with one would crash the gate rather than refuse.
* `figure_tokens` reads hex addresses (0x22, 0x10) as "NxM" figures. Conservative.

**Observation, no finding.** `gen_sch_d.py` says "0.5 W low". The SA868 sheet gives 24 / 25 / 26 dBm, which is 0.25 to 0.40 W. Correction 36 quotes both without claiming they agree, and line 47 names only the 2 W.

## What holds

**1. Check 5's B1 is answered.**
* **Line 47 against its sources:**
  * "NiceRF SA868 VHF 2 W exciter (`U2`, correction 36)" is board D's `U2` value word for word: "NiceRF SA868 VHF 2 W exciter, bench-fitted ...".
  * `gen_sch_d.py` line 368 synthesises it; line 9 says "2 W high / 0.5 W low".
  * The v1.3 sheet reads high 31 / 32.5 / 33 dBm and low 24 / 25 / 26 dBm, at VCC 4.0 V. 33 dBm is 2.0 W; typical is 1.8 W. Its feature list says "(1.6W/1.8W)".
  * So 2 W is the part's maximum on the maker's high row, and the board's value.
  * Line 47 carries no 1 W.
* **Correction 36's history holds:**
  * appendix 32.49 is "owner, 6 Sep 2026 18:20 to 23:00", and row 8 reads "NiceRF SA868 1 W module plus a 30 W VHF amplifier stage";
  * `bdfc7b3f` is 2026-09-07 07:15 and adds "2 W high / 0.5 W low", which is absent at its parent;
  * `git log -S` shows no commit removing it since.
* **V2-SPEC.md is not a baseline.** DEFINITION-STATUS.md's table has two rows, PRODUCT-BRIEF.md and CONOPS.md, and `s122lib.BASELINED` is CONOPS.md only.
* **`apply_docs_s122_r6.py` refuses as it should:**
  * on the tip it refuses (sha `c480bac2`, not `9615190d`);
  * on `a6429e66`'s V2-SPEC.md, `--check` locates 2 edits under 9 assertions, and the run writes the file byte identical to the tip;
  * a second run refuses;
  * with the CONOPS.md row of the baselines table pointed at V2-SPEC.md, it refuses ("is a baselined document");
  * with `s122lib.BASELINED` monkeypatched to include V2-SPEC.md, it refuses.

**2. The scan.** I listed all 45 tokens of the eight lines with the key that covers each, ran each bound assertion, and read what it states. 44 assert the figure:

| Line | What I read as the source of each figure |
|---|---|
| V2-SPEC.md 47 | 2 W: D `U2` value. 30 W: the RA30H1317M1 sheet's "135-175MHz 30W 12.5V" |
| V2-SPEC.md 81 | 240 x 160 mm and six layers: board A's file. 9 to 36 V: E `J_DCIN` "vehicle and shore DC in 9 to 36 V". Three 5.1 V slot rails: `J_5V_S1` to `J_5V_S3` "5.1 V rail to B16". All four AP64500 on 7 September: `gen_sch_a.py` at `b2709118` (2026-09-07 11:11), the four groups "SLOT RAIL S1/S2/S3" and "DEVICE RAIL: AP64500 5.1 V + INA226". 13.8, 12 and 54 V: `U13`, `U15`, `U16` LM5176 on `+13V8_PA`, `+12V_HF`, `+54V_POE`. 45 W: `U18` TPS25740A "45 W outlet". 3.3 V: `U12` TPS62933 "3.3 V logic". Eleven sites: `J_BM1` to `J_BM11` Radiall_SMPMAX. 2x13: `J_AB1` "IDC 2x13". **14.4 V: B1** |
| V2-SPEC.md 82 | 330 x 200 mm and six layers: board B's file. 5 V planes: In4 zones on `+5V_S1` to `+5V_S3` and `+5V_DEV`. Eight layers: decision 43's outcome (OWNER, 2026-09-25). Three CM5 slots: three CM5_Conn_A footprints `U30A`, `U31A`, `U32A`. Three supervisors: `U41`, `U51`, `U61` STM32H743. Two CAN-FD fabrics: `U41`'s value. Seven voters: seven `_CA` nets, with seven `_AB` and seven `_BC`, one per voter by `gen_sch_b.py` line 1879 ("out = AB + BC + CA"), built on `U70` to `U79`. Two display switches: `U3`, `U4` TS3DV642. Two E72: `U13`, `U14` |
| V2-SPEC.md 83 | 344 x 228: board C's outline. 240 x 176: its inner Edge.Cuts (x spans include 240, y spans include 176). Four layers: its file. Six: decision 27 "six layers for board C" (OWNER, 2026-09-25). Seventeen 3 mm: `D1` to `D16` and `D22`. Two PCA9555: `U1`, `U2` |
| V2-SPEC.md 84 | 100 x 80 mm and four layers: board D's file. Two headset jacks: `J_HS1`, `J_HS2` |
| V2-SPEC.md 86 | 267 x 68 mm and four layers: board E's file. 9 to 36 V: `J_DCIN`. 25 A: `F3` "25 A mini blade". Eleven float clamps: eleven zones "clamp 5G DIV/5G MAIN/P2P A/P2P B/HF/GNSS/SDR/IRIDIUM/WIFI 2.4/VHF/LORA: no copper under the float clamp". Two mixer fans: `J_FAN1`, `J_FAN2` |
| OPERATING-ENVELOPE.md 77 | 9 to 36 V: `J_DCIN`. -40 to +125 C: the LM5069 sheet's 7.3 TJ row ("Junction temperature", minus 40 and 125 °C, the minus printed as U+2013) and its footnote (1) (sign not asserted, m1) |
| OPERATING-ENVELOPE.md 83 | -40 to +80 C: the TE sheet's "Service Temperature -40 ~ +80" |

I also read the rest of each line against the netlists:
* **Line 81.** In1 and In4 carry only GND zones on board A. `U3` is the BQ25731. The AP64500 is `U4` and `U6`. The LM5176 is `U5` and `U7`. The INA226 is `U8` to `U11`. The D8 site is `J_MEZZ1` and `J_MEZZ_PWR1`.
* **Line 82.** `U101`, `U201`, `U301` PI7C9X2G404. `J_M2N1` to `J_M2N3` M-key 2242. `U102`, `U202`, `U302` TUSB8041. `J_FAN1` to `J_FAN3`. The banks' TMUXHS4212 and TS3USB221A. `U82`, `U83` SKY13351. `U1` KSZ9897. `J_LIME`. `J_RB9704`. `U11` LG290P. `U12` E22. `U9` DS3231SN. `U8` ATECC608B. `U10` TMP117. `J_PANEL` and `J_AB1`.
* **Line 84.**
  * `K1` G6K-2F-Y T/R relay. `L1`, `L2` LPF. `J_PAIN`, `J_PAOUT`, `J_VGG` to the RA30H1317M1.
  * `U6` PCM2912A. `U7` TPA6132A2. `U4` TUSB2046IBVFR. `U3` CP2102N. `U16` PCA9555.
  * `U15` TLV75801 has pin 4 (EN) on `PA_KEY` and pin 6 on `+5V_TX`.
  * `U21` TPS22810 has pin 1 (VOUT) on `+5V_TX` and pin 6 (VIN) on `+5V_D8`.
* **Line 86.** E `U6` LM5069MM-2 "9 V on, 40 V off". A `U2` LM5176 "VBUS20 from VIN_RAW". E `U5` LT8705A. `J_BATT` XT60. `U14` BME688. `U15` BMI270. `J_POD` with SDA and SCL.

**3. Plants, each refused.** Wrong figures on eight different closing lines (six of V2-SPEC.md and both of OPERATING-ENVELOPE.md), each with the row's judgement moved as is. Every one reads STALE or UNJUDGED and the scan refuses it:
* 240 x 170 mm (81);
* eight 2-of-3 voters (82, spelled);
* sixteen 3 mm LEDs (83, spelled);
* 100 x 90 mm (84);
* 30 A fuse (86);
* 45 W amplifier (47);
* -40 to +150 C (77);
* -20 to +80 C (83).

With the key also rewritten:
* all of these are still refused, and so is "12.5 V node";
* "three 3 mm LEDs" and "sixteen 5.1 V slot rails" pass the scan on shared digits, but the count check ("whose number is not 3", "not 16") and (b) refuse them;
* the transpositions and signs of m1 pass.

**Out of scope, as stated.**
* A unit-less figure: "an NVMe 2280 socket" on line 82 reads TRUE, and the scan passes it.
* A figure off the list: "`Y1` 16 MHz" on PANEL.md line 55 reads TRUE, and the gate does not scan that line.
* 159 TRUE sentences off the list hold figure tokens, and none has `figures_ok`.
* Both limits are stated in the README and in S-122's round 6 title ("the scan reads only the lines of the closing list and only numbers with a unit or spelled counts"). The closure's sentence is scoped to "the lines of the closing list" and "figure-and-unit token". That is honest, except for m3's correction 36 wording.

**4. The role rule's committed fixtures.**
* Each of the 14 MUTANTS reads STALE for its intended reason when I judge it one by one:
  * rails converters for 1 to 6;
  * reverse1 on `U15`'s "bias" for 7;
  * reverse2 for 8;
  * forward for 9, 10, 13 and 14;
  * the history tie for 11 and 12.
* Round 5's two fixtures are refused.
* Of my own mutants, these are refused:
  * "the TPS22810 PTT switch" (reverse1, D `U10`);
  * "the CSD18510Q5B bleed switch" (reverse1, A `Q37`);
  * "CP2102N hub";
  * the TPS55288 with a date (the outlet rail).
* The rest are m2.

**5. m2 of check 5 is answered.**
* `test_close_s122.py` prints ALL PASS.
* With each of forward, reverse1, reverse2, rails and history switched off, at least one mutant reads TRUE and `gate_fixtures` refuses.
* With the forward test off, "the TPA6132A2 named a codec" reads TRUE and the gate refuses at it. With all on, it reads STALE.

**6. m3 of check 5 is answered.** The closing evidence string names `apply_docs_s122_r5.py` and `apply_docs_s122_r6.py`.

**7. The finder changes work as described.**
* Read as parts: L76K, 5023520600, SS2020FL.
* Not read as parts: SNVA559, AN2606, RM0433, DS12110, UN38.3, 1000BASE-T, RJ45, RS485, RS103, VBUS20.
* No net name of the six netlists that the new net rule excludes is a real part: the collisions are SPARE10 to SPARE12 and VBUS20.

**8. Replays, all byte identical to the committed files:**
* `inventory.out` and `verdicts.out` (no `S122_AT`);
* `inventory-base.out` and `verdicts-base.out` (`e57a7365`: 931 sentences, 74 STALE);
* `inventory-set14.out` and `verdicts-set14.out` (`1bafab8c`: 989, 10 STALE);
* `verdicts-r4.out` (`edead832`: 998, 5 STALE);
* `verdicts-r5.out` (`a6429e66`: 1002, 1 STALE, V2-SPEC.md line 47, `c60dec6ff0`).

**9. The integrator sequence on `fnd/int16`** (`36bb1d12`):
* **The merge.** `git merge --no-ff 1c187977` merged with no conflict.
* **The registry script.** `apply_registry_s122_r4.py` rebound 5 records (CFL-010, CFL-013, CFL-014, CFL-016, REQ-005) and re-pinned the envelope and ENV-001 to `26e98ecfd2e4ec2f`. A second run refused ("already applied").
* **Renders and status.**
  * `rules_render.py --requirements` ran.
  * `rules_status.py` ran three times, each exit 1 with gate state NOT_READY and the same line: 39 FAIL, 104 INCONCLUSIVE, 195 PASS of 338.
  * `rules_render.py` rewrote CURRENT-EVIDENCE.md and the seven status pages (m5).
* **The fixture check.**
  * A fixture check named the eight lines, check-int15-1, the nine documents and `verdicts.out`.
  * While only staged, it was refused at (d); I then committed it.
* **The closure.**
  * `test_close_s122.py` printed ALL PASS.
  * `close_s122.py` refused first (m5, the header line). After re-running `inventory.py` and `verdicts.py` and committing, it closed S-122 at `126ffe16` and set CFL-016 to PASS. S-42, S-123, S-124 and S-125 stay open.
  * A second run refused ("S-122 is not open").
* **After the closure:**
  * `rules_lib.py requirements`: 144 records, 0 errors, 2 warnings (m5);
  * `rules_lib.py`: 59 rules, 0 errors;
  * `rules_render.py --requirements`, then `tests/run.py test_requirements test_envelope_data`: 72 passed, 0 failed, 0 skipped.

**10. Text rules.**
* No U+2013 or U+2014 in any added line of the diff.
* No internal host name, user path or address.
* CONOPS.md (`6cb7b241cb84d729`, the `c5430071` file) and PRODUCT-BRIEF.md are untouched since `1bafab8c`.

## Counts

Committed `verdicts.out` at `1c187977`, reproduced byte for byte:

| Document | Sentences | TRUE | STALE | BASELINE | NOT DERIVABLE | UNJUDGED | Assertions |
|---|---|---|---|---|---|---|---|
| PANEL.md | 167 | 131 | 0 | 0 | 36 | 0 | 787 |
| CONOPS.md | 287 | 51 | 0 | 40 | 196 | 0 | 784 |
| V2-SPEC.md | 157 | 64 | 0 | 0 | 93 | 0 | 484 |
| OPERATING-ENVELOPE.md | 66 | 22 | 0 | 0 | 44 | 0 | 165 |
| TEST-PLAN.md | 110 | 18 | 0 | 0 | 92 | 0 | 128 |
| ASSEMBLY.md | 158 | 91 | 0 | 0 | 67 | 0 | 242 |
| pcb_decisions.yaml | 9 | 6 | 0 | 0 | 3 | 0 | 17 |
| EMCON.md | 26 | 22 | 0 | 0 | 4 | 0 | 455 |
| DEFINITION-STATUS.md | 24 | 17 | 0 | 0 | 7 | 0 | 276 |
| **Total** | **1004** | **422** | **0** | **40** | **542** | **0** | **3338** |

The three sentences that left the inventory, by sentence id against `a6429e66`'s `verdicts.out`:
* ASSEMBLY.md line 148 cell 2 ("the sealed RJ45 on the connector plate (PoE out on 1-2 and 3-6)");
* ASSEMBLY.md line 148 cell 4 ("RJ45 both ends");
* TEST-PLAN.md line 43 cell 1 ("RS103, radiated susceptibility, 2 MHz to 18 GHz at 50 V/m").

Each was NOT DERIVABLE, with 0 names looked up and only the false part number. The two new sentences are correction 36's.

This round's findings: 1 blocking (B1, the 14.4 V binding), 6 minor.
