mergeable: no

# AI review: independent check of stream s122, round 4, fnd/s122c at edead832 (S-122, CFL-016, MESHSAT-1357)

This is an AI review, not a qualified engineering review. Everything below is what I read or ran myself.

**Set up**
* `fnd/s122c` at `edead8323c45ac81d604015a1099917e679820e2` (`git rev-parse fnd/s122c`): two commits, `e5fdf670` and `edead832`, on set 14's main `1bafab8c`.
* Check clone: a new shared clone at `<scratch>/chk-s122` at the tip, removed when done.
* Throwaway clone in my session scratchpad for the registry script and the closure. In it I made one commit of three fixture checks with the owner's `-c` flags; it was never pushed, and the clone is deleted.
* Time: 29 September 2026, 21:22 to 21:32 CEST (from `date`).
* Rule tools ran with `VERDICT_DIR` in scratch.

**What I read**
* `v2/docs/records/int15/checks/check-int15-1.md`: its head and B1. S-122's title in `pcb_requirements.yaml` at the tip, all of it, including its set 13 and set 14 additions and the set 14 third check's correction.
* The round 4 section of `v2/docs/records/s122/README.md`, and these tools:
  * `s122lib.py` (the part number finder, `is_partno` and `partnos`, lines 258 to 313);
  * `close_s122.py` (`gate_set14` and `main`);
  * every `parts_ok` excuse in `judgements.py` (87);
  * `apply_docs_s122_r4.py` and `apply_registry_s122_r4.py`, by their runs.
* The documents:
  * `v2/docs/V2-SPEC.md` lines 45 to 50, 76 and 81 to 86 (the boards table), and correction 34 (lines 296 to 308);
  * `v2/docs/OPERATING-ENVELOPE.md` lines 68 to 97 (section 2's table and its correction note);
  * `v2/docs/handover/DEFINITION-STATUS.md`: the diff, row DC-10 and the dependency table's row;
  * the lines of PANEL.md, ASSEMBLY.md, TEST-PLAN.md, V2-SPEC.md and OPERATING-ENVELOPE.md in the sample below;
  * `v2/docs/CONOPS.md` line 1056 (unchanged; D-13), and `pcb_decisions.yaml` decisions 28 and 40 (unchanged since round 1).
* `v2/docs/records/s122/verdicts.out`: the entries for V2-SPEC.md lines 81, 82, 84 and 86, and a sample of about 40 entries that name part numbers across PANEL.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md and ASSEMBLY.md.
* `feasibility/EMCON.md` and the rest of DEFINITION-STATUS.md are unchanged since round 3.
* Netlists: set 14's six (`tx_inhibit.parse_netlist`: A `6c40250c`, B `3ef9b8c4`, C `c9f73945`, D `a2d48972`, E `2ed95a0e`, P `20c7b079`).
* Generators: `gen_sch_a.py`, `gen_sch_b.py`, `gen_sch_d.py` and `gen_sch_e.py` at `b2709118` (where the boards table was written); `gen_sch_d.py` before and at `bdfc7b3f`; `gen_sch_e.py` line 800 at the tip.
* Makers' sheets, read with `pdftotext`: `v2/vendor/ti/ti-lm5069.pdf`, `v2/vendor/m2/te-2199119-m2-b-key.pdf`, `v2/vendor/m2/amphenol-mdt420b01001-m2-b-key.pdf`.

## Blocking items

**B1. Two part numbers in scope name parts in roles the set 14 netlists do not give them. Both are judged TRUE, and one is a sentence the closing check must name.**
* **`v2/docs/V2-SPEC.md` line 84 (the D8 row): "the TPS22810 gate-bias switch".**
  * On board D, the PA's gate bias is `U15`, TLV75801PDRVR ("PA gate bias VGG 4.48 V while PA_KEY is high"); its EN pin is on `PA_KEY` and its output on `VGG_SW` at `J_VGG`.
  * The only TPS22810 on board D is `U21`, "TPS22810DRV load switch, +5V_TX on while +3V3_D8 is above 2.23 to 2.78 V", which switches the exciter's supply.
  * The TPS22810 was the bias switch on 7 September (`gen_sch_d.py` line 11 at `b2709118`: "bias switched by a TPS22810 on PA_KEY"); `faf8c981` brought in the TLV75801.
  * `verdicts.out` judges the row TRUE. The assertion it makes for the TPS22810 prints the netlist's own "load switch, +5V_TX".
  * This is the class correction 34 corrects in the same row ("Two names were true on 7 September and are not today": the TUSB2046B, the DS3231M). It concerns the PA bias, which EMCON removes through `PA_KEY`.
  * Line 84 is one of the lines the closing check has to name as corrected and true, so I cannot write that closing section.
* **V2-SPEC.md line 81 (the A22 row): "three 5.1 V slot rails and a device rail (AP64500, INA226 monitored)".**
  * On board A, `U4` and `U6` are AP64500 (`+5V_S1`, `+5V_S3`), while `U5` (`+5V_S2`) and `U7` (`+5V_DEV`) are LM5176 buck-boost stages.
  * ASSEMBLY.md lines 132 and 133 say so in the same scope.
  * All four were AP64500 on 7 September (`gen_sch_a.py` lines 205 to 219 and 375 to 377 at `b2709118`).
  * The row is judged TRUE; its assertions check the AP64500 on `U4` only.
* **Why the instrument passes both:** `verdicts.check_parts` asks only whether a part number is on the board the row names. Both are, in another role.
* **I confirmed S-122 closes with both.** In the throwaway clone, after `apply_registry_s122_r4.py`, `close_s122.py` with a committed fixture closed S-122 and set CFL-016 to PASS at the tip as it stands.
* **Fix:**
  * Line 84: the TLV75801 gate-bias LDO `U15` on `PA_KEY` (the TPS22810 bias switch on 7 September), and the TPS22810 load switch of the exciter's `+5V_TX`, `U21`.
  * Line 81: AP64500 on slots 1 and 3 (`U4`, `U6`) and LM5176 stages on slot 2 and the device rail (`U5`, `U7`), with the 7 September value dated.
  * Each fix asserts the value text that states the role ("PA gate bias", "load switch, +5V_TX", "+5V_S2", "+5V_DEV").
  * In the judgement: when a sentence names a part with a role, assert it on the designator whose value states that role, not on the board alone.

## 1. The finder

* **It reads the shapes it was built for.** It returns TMDS341A, LM5069, 105133-0011, CM5108064, RP2040, TPD4E001, AP63203WU-7, 0603WAF1332T5E, "TMR 3-2411", MAX3232, LTC2954, CP2102N, AD9361, GRM188R71C104KA01D, BSS138, 2N7002, NE555, LM358, 1N4148W and DMR858M.
* **It does not read part numbers generally.** These real makers' numbers return nothing:
  * TI's single-gate logic (SN74LVC1G08, SN74LVC2G06DBVR, SN74AUP1G08: no run of three digits);
  * Si2300DS, nRF52840 and IRLML6344TRPbF (a lower-case letter);
  * BAT46W, BAT54, USBLC6-2SC6, E72-2G4M20S1E, ESP32-S3, LIS3MDL, XT60, SMBJ15A and B2B-XH-A (no run of three digits);
  * 5023520600 (all digits, no dash).
* **The gate's probe (a) cannot see this.** Its ten made-up numbers are drawn from the shapes the finder was built for. I checked the probe with a mutant finder that drops digit-led numbers: the gate refuses it (86VFS9G513UM).
* **In scope, no stale part number of the missed shapes.** I swept every token in the in-scope sentences of PANEL.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md, EMCON.md section 0a.1 and the status page's section that the finder does not read.
  * The only maker's number of a missed shape on no netlist is LIS3MDL, in V2-SPEC.md line 76's list of drawings owed. `gen_sch_e.py` line 800 puts the magnetometer in the outside pod, which is not netlisted, so it is not judgeable here.
  * The rest are designators, register addresses, finding identifiers, standards, commits and case items.
* **Sampled verdicts.** I read about 40 verdicts that name part numbers (PANEL 8, V2-SPEC 12, OPERATING-ENVELOPE 8, TEST-PLAN 8, ASSEMBLY 8), each against the netlists.
  * Every part number named is on the board or is excused truly.
  * The one class the instrument misses is B1's: a part on the board in another role.
* **The 87 `parts_ok` excuses.** Each is what it says: a document number, an LCSC code, a case, bought or withdrawn item, a module's chipset, or an assertion at a commit.

## 2. The seven corrections

* **V2-SPEC.md line 82:** true.
  * Board B's `U3` and `U4` are TS3DV642A0RUAR, and `U9` is DS3231SN.
  * At `b2709118`, `gen_sch_b.py` carried the TS3DV642 (lines 9, 100, 398) and a "DS3231MZ holdover clock" (line 15).
  * No TMDS341A is on any board.
* **Line 84:** the TUSB2046I correction is true: board D's `U4` is TUSB2046IBVFR, and `gen_sch_d.py` carried the TUSB2046B at `b2709118`. The rest of the row fails as B1 says.
* **Line 86:** true, and it was false at its own date.
  * Board E's `U6` is LM5069MM-2 and board A's `U2` is the LM5176 "VBUS20 from VIN_RAW".
  * At `b2709118`, `gen_sch_e.py` lines 103 to 104 carry the LM5069 hot swap and send the raw bus "into A22's LM5176 front end", while the row written at `b2709118` put "the LM5176 9 to 36 V front end" on E6.
  * Minor m2 applies to the same row.
* **Line 47:** true.
  * Board D's `U6` is PCM2912A.
  * `gen_sch_d.py` held five WM8960 mentions before `bdfc7b3f` (7 September 07:15) and none at it, before `b2709118` (11:11).
  * The RA30H1317M1's sheet is a row of OPERATING-ENVELOPE.md section 2.
* **Correction 34:** true, except that its "Two names were true on 7 September and are not today" misses line 84's TPS22810 and line 81's AP64500 (B1).
* **OPERATING-ENVELOPE.md line 77:** true.
  * Board E's `U6` is LM5069 and no TRACO part is on any board.
  * SNVS452G section 7.3, Recommended Operating Conditions, gives TJ junction temperature -40 to 125 C.
* **Line 83:** true.
  * Board B's `J_M2C2` is TE 2199119-3.
  * The TE sheet's Performance Ratings (product specifications 108-115042 and 108-115049) give Service Temperature -40 to +80 C. Amphenol's MDT420B01001 sheet gives -40 C to +80 C too.
  * Board B's Amphenol parts are the MDT420M02001 sockets `J_M2N1` to `J_M2N3`.
* **The envelope:** no envelope number left the document. Every number of `pcb_envelope.yaml` found in OPERATING-ENVELOPE.md at `1bafab8c` is still in it, and `+75` is not an envelope value.
* **CONOPS.md line 1056 and DC-10:** true.
  * Board B's `U41` read STM32H753VITx at `1f614233` and reads STM32H743VIT6 since `458b2873`, which I read in round 3.
  * CON-017 reads PASS.

## 3. The gate (a) to (d), by mutants of my own

* **(a)** A finder without its digit-led rule is refused. The finder as committed passes although it misses the shapes in section 1.
* **(b)** It finds only the five phrasings it names; line 84 is found through its "PCM2912A USB codec". B1's two clauses pass it and the verdicts, and S-122 closes.
* **(c)** A fixture that leaves "V2-SPEC.md line 84" out of the closing section is refused.
* **(d)**
  * A fixture that is only staged is refused, by the provenance test.
  * A committed fixture without check-int15-1 is refused.
  * The full committed fixture closes.
* **Answer:** yes, S-122 can close with a stale part statement left in scope. The two instances I found are in section 1's sense of B1: part numbers on the board, named in a role they no longer have.

## 4. Replay

* **Documents.** `apply_docs_s122_r4.py --check`, with V2-SPEC.md, OPERATING-ENVELOPE.md, DEFINITION-STATUS.md and `records/int15/apply_check15c_fixes.py` taken from `1bafab8c`: 12 edits located, 51 assertions hold. The run makes the four files equal the tip, and a second run refuses.
* **Outputs.** `inventory.py` and `verdicts.py` with `--stdout`, at the tip, with `S122_AT=e57a7365` and with `S122_AT=1bafab8c`, reproduce all six committed outputs byte for byte.
  * Tip: 985 sentences, 410 TRUE, 0 STALE, 40 BASELINE, 535 NOT DERIVABLE, 0 UNJUDGED, 3219 assertions.
  * Set 14's documents: 975 sentences, 7 STALE, 0 UNJUDGED. The 7 are V2-SPEC.md lines 47, 82, 84 and 86, OPERATING-ENVELOPE.md lines 77 and 83, and CONOPS.md line 1056.
* **Registry.** `apply_registry_s122_r4.py` rebinds 5 records (CFL-010, CFL-013, CFL-014, CFL-016, REQ-005). It re-pins the envelope and ENV-001's `verified_sha` from `a8e65995` to `26e98ecf`, and refuses a second run. `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings. `rules_lib.py`: 59 rules, 0 errors.
* **Closure.** With the committed fixture it closes S-122 and sets CFL-016 to PASS, and refuses a second run. After `rules_render.py --requirements`, `tests/run.py test_requirements test_envelope_data` gives 71 passed, 0 failed, 1 skipped.

## Minor items

* **m1.** The finder misses several real part number shapes (section 1), and the gate's probe cannot detect it. Add probes drawn from the parts the netlists carry (the SN74 family, BAT46W, USBLC6-2SC6, Si2300DS, E72-2G4M20S1E), or widen `is_partno` to a letter-led token with a run of two digits and five characters or more.
* **m2.** V2-SPEC.md line 86 keeps "the sensor controller with the BME688, BMI270 and magnetometer". Board E carries the BME688 (`U14`) and the BMI270 (`U15`) but no magnetometer: `gen_sch_e.py` line 800 puts it in the outside pod, reached through `J_POD` (`SDA1`, `SCL1`). Line 65's "six-axis IMU with magnetometer" says the same. This is not a part number, but line 86 is a closing sentence; say where the magnetometer is.
* **m3.** V2-SPEC.md line 83 (the C7 row) keeps "sixteen LEDs" under a count excuse dated 7 September, while the round 4 rule says the boards table's date excuses no part. Board C carries seventeen 3 mm LEDs with `D22`.

## Counts

* **Blocking: 1** (B1: V2-SPEC.md line 84's TPS22810 as the gate-bias switch and line 81's AP64500 for all four rails, both judged TRUE; S-122 closes with them). **Minor: 3.**
* Corrections true: 6 of 7 (line 84 true for the TUSB2046I and false for the TPS22810).
* Temperature ranges read from the sheets: 2 of 2 as the rows state.
* Replays: byte identical; validators 0 errors; tests 71 passed, 0 failed.
* Named in this report: check-int15-1; PANEL.md, CONOPS.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md, `pcb_decisions.yaml` decisions 28 and 40, `feasibility/EMCON.md`, `handover/DEFINITION-STATUS.md`, and `verdicts.out`.
