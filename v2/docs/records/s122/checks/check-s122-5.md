mergeable: no

# AI review: independent check of stream s122, round 5, fnd/s122c at a6429e66 (S-122, CFL-016, MESHSAT-1357)

This is an AI review, not a qualified engineering review. Everything below is what I read or ran myself.

**Set up**
* `fnd/s122c` at `a6429e66`: two commits, `8d7874f5` and `a6429e66`, on `edead832`. They answer check-s122-4, which is filed as `checks/check-s122-4.md`, byte identical to my CHECK-4.md.
* Check clone: a new shared clone at `<scratch>/chk-s122` at the tip. It is removed when done.
* Throwaway clone in my session scratchpad for the registry script and the closure:
  * one commit of two fixture checks, with the owner's `-c` flags;
  * its remote was removed, it was never pushed, and it is deleted.
* Time: 29 September 2026, 21:52 to 22:10 CEST (from `date`).
* Tools ran with `VERDICT_DIR` in scratch.

**What I read**
* The round 5 section of `v2/docs/records/s122/README.md`.
* The tools:
  * `verdicts.py`: `check_roles`, `role_phrases`, `rail_lists`, `ROLE_NOUN`, `ROLE_SYN`, and how `judge` uses them;
  * `s122lib.py`: `is_partno`, `partnos`, `PN_PIN`, and the round 5 diff;
  * `close_s122.py`: `gate_set14` (a) to (e), and `main`;
  * the five `roles_ok` bindings in `judgements.py`;
  * the round 5 diff of `apply_registry_s122_r4.py`.
* The documents:
  * `v2/docs/V2-SPEC.md` lines 47, 76 and 81 to 86, and correction 35 (lines 310 to 320);
  * `v2/docs/PANEL.md` line 182.
  * Of the nine documents, only V2-SPEC.md changed since `edead832`:
    * PANEL.md, CONOPS.md, OPERATING-ENVELOPE.md, TEST-PLAN.md and ASSEMBLY.md are unchanged;
    * so are `pcb_decisions.yaml` decisions 28 and 40, `feasibility/EMCON.md` and `handover/DEFINITION-STATUS.md`.
* `verdicts.out`: every TRUE sentence that names a part number in PANEL.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md and ASSEMBLY.md (113 sentences). For each, I read the part's context against the netlist values that carry it.
* The six set 14 netlists, read with `tx_inhibit.parse_netlist`: A `6c40250c`, B `3ef9b8c4`, C `c9f73945`, D `a2d48972`, E `2ed95a0e`, P `20c7b079`.
* Generators:
  * `gen_sch_a.py` and `gen_sch_d.py` at `b2709118`;
  * `gen_sch_d.py` at `faf8c981^` and `faf8c981`, and at the tip (lines 9, 367 and 368);
  * `gen_sch_e.py` line 800.
* Sheets, read with pdftotext:
  * `v2/vendor/nicerf/nicerf-sa868-datasheet-v1.3.pdf`;
  * `v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf` ("135-175MHz 30W").
* Design record: `MESHSAT-709-geometry-appendix.md` line 2765 (32.49).

## Blocking

**B1. V2-SPEC.md line 47 is one of the eight lines of the closing list, and it states the exciter's power differently from the netlist.**
* The line says "NiceRF SA868 1 W with a 30 W VHF amplifier stage".
* The netlist and generator say otherwise:
  * Board D's `U2` value is "NiceRF SA868 VHF 2 W exciter, bench-fitted (castellated; VBAT 3.3 to 5.5 V, TX 1 A)".
  * `gen_sch_d.py` has carried "the NiceRF SA868 VHF exciter (bench-fitted, 2 W high / 0.5 W low)" since `bdfc7b3f` (7 September); it reads the same at `b2709118` and at the tip.
* The maker's sheet v1.3 gives:
  * output power, high: 31 / 32.5 / 33 dBm;
  * output power, low: 24 / 25 / 26 dBm;
  * "High and low power options (1.6W/1.8W)".
* No netlist, generator or held sheet I read gives the SA868 as 1 W. The "1 W" is the wording of the 6 September device set (appendix line 2765, "NiceRF SA868 1 W module plus a 30 W VHF amplifier stage"), and the row carries no date.
* The row's judgement asserts only that SA868 is on board D, so it reads TRUE.
* The part number and its role (exciter) are right; the rating is not. I cannot name this line in a closing check as describing the circuit as generated.
* **Fix:**
  * Correct line 47 to the generated part: for example "NiceRF SA868 VHF 2 W exciter (`U2`; 1 W in the device set of 6 September, 32.49)", as a correction 36.
  * Assert `D:U2~VHF 2 W exciter`.
  * Add a check that a figure with a unit written right after a part number is in a value that carries the part, or is bound by an assertion.
* My scan of all TRUE sentences in the nine documents for "<part> <number> <unit>" found this one mismatch. RA30H1317M1 30 W is carried only by the connector notes, and its sheet says "30W".

## Minor

**m1. The role rule has blind spots. S-122 can close with a stale part or role left in the forms it does not read.** I ran these mutants through `verdicts.judge`, each with the sentence's own judgement moved to the mutant's digest.

Refused, as intended:
* the TPS22810 as the gate-bias LDO;
* the TLV75801 as the load switch;
* "TPS22810 gate bias switch" without the hyphen;
* codec and amplifier swapped;
* the CP2102N as the hub;
* the TUSB2046I as the bridge;
* "(AP64500, INA226 monitored)";
* "(LM5176, INA226 monitored)";
* a monitor not on A (INA219).

Read TRUE, and stale:
* **(a)** `rail_lists` returns from the whole sentence when a parenthetical after "rails" holds anything but plain parts (`return out` inside the item loop).
  * On line 81 as corrected, the first list is not plain, so no later list in that row is read.
  * "the 13.8 V PA and 12 V HF rails (AP64500)" and "the 54 V PoE rail (AP64500)" read TRUE, although A `U13` and `U15` (`+13V8_PA`, `+12V_HF`) and `U16` (`+54V_POE`) are LM5176.
  * A list with a non-part item, "(AP64500, EMCON gated)", is skipped even alone.
  * A rail with no `RAIL_WORD`, "the 3.3 V logic rail (LM5176)", is not read; A `U12` is a TPS62933.
* **(b)** A named function is judged against any carrier on the board. "the 45 W USB-C outlet (TPS25740A and an AP64500 stage" reads TRUE; the stage is A `U19`, an LM5176 on `PD_VPWR`.
* **(c)** Line 81's two converters swapped ("the LM5176 buck on slots 1 and 3 ... AP64500 stages on slot 2") read TRUE, because "buck" matches "buck-boost" and "stage" matches "buck". Only gate (b)'s pinned pattern refuses it.
* **(d)** A one-word qualifier escapes the reverse test: "the TPS22810 bias switch" reads TRUE, because D `U21` is a switch.
* **(e)** Nouns outside `ROLE_NOUN` are not read: "the TPS22810 gate-bias supply" and "the TPS22810 gate-bias driver" both read TRUE.
* **(f)** A part that `parts_ok` excuses for a history note can be put back as the current part in the same sentence: "(TPS25740A and a TPS55288 stage;" and "the TUSB2046B hub (`U4`" both read TRUE.

At the gate:
* In the throwaway clone I planted "(AP64500, EMCON gated)" on line 81's PA and HF rails.
* I moved the judgement to the new digest, regenerated `inventory.out` and `verdicts.out` (420 TRUE, 0 STALE), and rebound V2-SPEC.md in the registry.
* `close_s122.py` then closed S-122, with that line in its closing list.

None of these stands in the documents as committed: in my reading of the 113 sentences, every part named with a role holds it on the netlist (B1 is a rating).

**Fix:**
* In `rail_lists`, go on to the next list, and read the part items of a list that also holds other items.
* Judge "<part> <role> on <rail or slot>" by that rail's converters.
* Tie a `parts_ok` history excuse to its clause.
* Apply the reverse test to a one-word qualifier when another carrier's value states "<qualifier> <noun>".

**m2. Gate (e) does not pin the forward direction.** With the forward test disabled (`if False:` in `check_roles`), `close_s122.py` closes S-122 in the throwaway clone. With the whole rule, the reverse test or `rail_lists` disabled, it refuses. **Fix:** add a forward fixture to (e), for example line 84 with the codec and amplifier swapped, which must read STALE.

**m3. `close_s122.py` line 275 omits the round 5 script.** The closing evidence names apply_docs_s122.py to apply_docs_s122_r4.py as the scripts that corrected the documents. It does not name apply_docs_s122_r5.py, which wrote correction 35 (four of the eight lines). `apply_registry_s122_r4.py` does name it. **Fix:** add it.

**m4. The finder.**
* Of 87 real part numbers of other shapes, in "the %s part on the board", it misses two:
  * L76K, which it takes for a designator;
  * 5023520600, which has no maker's word before it (the documented rule).
* It also misses tokens in "SMBJ15A/BAT54", "SMBJ15A-based" and a plural "SMBJ15As". The documents hold none of these.
* Of 132 non-parts, it reads 15 as parts:
  * literature and manual codes: SNVA559, SLVA505, AN2606, RM0433, ES0392, PM0253, UM2179, TN1204, DS1234;
  * 1000BASE-T, UN38.3, RJ45, RS485;
  * the net VBUS20;
  * an upper-case commit.
* These errors are conservative: a false part needs a `parts_ok` entry to stay TRUE.
* The netlist-drawn probe is a real instrument:
  * it takes 105 distinct tokens from 398 U, Q, D, Y and K designators;
  * round 4's finder misses 35 of them;
  * a finder without the mixed-case rule misses Si2300DS-T1-GE3.
* Two limits of the probe:
  * It skips a token that the finder's own `PN_PIN` excludes (one today: C `D18`, "GPIO25"), so a wider exclusion would drop its own probes.
  * It leaves out connectors, although the documents name TE 2199119-3, R222M00720, 813-S1-012-10-016101, B4B-XH-A and XT60.

## 1. The four corrections, on the netlists

All four hold:

| Line | What the netlists and generators carry |
|---|---|
| 84 | D `U15` "TLV75801PDRVR adjustable LDO, PA gate bias VGG 4.48 V while PA_KEY is high", pin 4 (EN) on `PA_KEY`. D `U21` "TPS22810DRV load switch, +5V_TX ...", VOUT on `+5V_TX`. At `b2709118`, `gen_sch_d.py` line 11: "bias switched by a TPS22810 on PA_KEY". The TLV75801 appears 0 times at `faf8c981^` and 10 times at `faf8c981`. |
| 81 | A `U4` and `U6` AP64500SP-13 (`+5V_S1`, `+5V_S3`). A `U5` and `U7` LM5176PWPR (`+5V_S2`, `+5V_DEV`). INA226 `U8` to `U11` on the four rails. At `b2709118`, `buck5` (AP64500) built `U4` to `U7`. |
| 86 | E `U14` BME688 and `U15` BMI270, on `SDA1`/`SCL1`. No magnetometer on E. `J_POD` carries `SDA1` and `SCL1`. `gen_sch_e.py` line 800: "the magnetometer sits in the outside pod (32.57)". |
| 83 | 17 parts on C: `D1` to `D16` and `D22` (EMCON). S-44 is OPEN. |

* Correction 35 (lines 310 to 320) says the same, and I read it true.
* `roles_ok`, as I read the netlists:
  * A `U2` is "LM5176PWPR buck-boost controller, VBUS20 from VIN_RAW";
  * E `U5` pins 32 to 34 are on `PV_P`;
  * C `U1` is "PCA9555PW 0x22: LED sinks, light mode inputs".

## 2. The sample of TRUE sentences with parts, across the five documents

* I read all 113 TRUE sentences in PANEL.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md and ASSEMBLY.md that name a part number, against the carriers' values.
* Every role I read holds, for example:
  * the 74LVC1G17 buffers;
  * the SN74LVC1G57 wired as a NOR;
  * the TPS23861 PoE PSE controller;
  * the STM32H743 I/O supervisors;
  * the KSZ9897R Ethernet switch;
  * the DS3231SN holdover clock;
  * the BQ25731 charger;
  * the SKY13351 switches;
  * the R222M00720 blind-mate receptacles;
  * ASSEMBLY.md line 132's slot rails and line 133's LM5176 device rail stage.
* Parts on no netlist were in places that say so:
  * TCA9517A, PANEL.md line 182: "Owed on A22 and B16";
  * LIS3MDL, V2-SPEC.md line 76: a list of drawings;
  * C9866: a purchase code;
  * TPS55288, TUSB2046B, DS3231M, WM8960 and TMDS341A: correction notes.
* The one mismatch is B1.

## 3. The gate

Results in the throwaway clone, after `apply_registry_s122_r4.py`:

| Case | Result |
|---|---|
| The committed fixture | Closes S-122; CFL-016 PASS |
| A second run | Refused ("S-122 is not open") |
| A committed fixture without "V2-SPEC.md line 81" | Refused by (c) |
| `check_roles` returning nothing | Refused by (e) |
| The reverse test off | Refused by (e) |
| `rail_lists` off | Refused by (e) |
| The forward test off | Closes (m2) |
| The planted rail list of m1 | Closes (m1) |
| Line 47 as committed | Closes (B1) |

The answer to the question: yes, S-122 can close with a stale role left in the forms of m1, and with B1's stale rating.

## 4. Replay

* **Outputs.** Regenerated in the check clone, byte identical:
  * `inventory.out` and `verdicts.out`;
  * `verdicts-base.out` (`S122_AT=e57a7365`): 934 sentences, 74 STALE;
  * `verdicts-set14.out` (`S122_AT=1bafab8c`): 992 sentences, 10 STALE (CONOPS.md 1056, V2-SPEC.md 47, 81, 82, 83, 84 and 86, OPERATING-ENVELOPE.md 77 twice and 83);
  * `verdicts-r4.out` (`S122_AT=edead832`): 4 STALE, V2-SPEC.md 81, 83, 84 and 86. Its FAILS lines carry the role rule's own findings for 81 ("AP64500 is given the slot rail; A:U5 is LM5176...") and for 84.
* **Documents.** With V2-SPEC.md from `edead832`, `apply_docs_s122_r5.py` wrote "5 edits written, 33 assertions held first", and the file equals `a6429e66`'s (`9615190d8881790d`). A second run is refused.
* **Registry.**
  * `apply_registry_s122_r4.py` rebinds CFL-010, CFL-013, CFL-014, CFL-016 and REQ-005, and re-pins the envelope and ENV-001 to `26e98ecfd2e4ec2f`.
  * A second run is refused.
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings. `rules_lib.py`: 59 rules, 0 errors.
* **Closure.**
  * With the committed fixture, it closes S-122 and sets CFL-016 to PASS.
  * `rules_lib.py requirements` then reads 0 errors.
  * After `rules_render.py --requirements`, `tests/run.py test_requirements test_envelope_data` gives 71 passed, 0 failed, 1 skipped.

## Counts

Committed `verdicts.out` at `a6429e66`, reproduced:

| Document | Sentences | TRUE | STALE | BASELINE | NOT DERIVABLE | UNJUDGED | Assertions |
|---|---|---|---|---|---|---|---|
| PANEL.md | 167 | 131 | 0 | 0 | 36 | 0 | 787 |
| CONOPS.md | 287 | 51 | 0 | 40 | 196 | 0 | 784 |
| V2-SPEC.md | 155 | 62 | 0 | 0 | 93 | 0 | 442 |
| OPERATING-ENVELOPE.md | 66 | 22 | 0 | 0 | 44 | 0 | 164 |
| TEST-PLAN.md | 111 | 18 | 0 | 0 | 93 | 0 | 128 |
| ASSEMBLY.md | 160 | 91 | 0 | 0 | 69 | 0 | 242 |
| pcb_decisions.yaml | 9 | 6 | 0 | 0 | 3 | 0 | 17 |
| EMCON.md | 26 | 22 | 0 | 0 | 4 | 0 | 455 |
| DEFINITION-STATUS.md | 24 | 17 | 0 | 0 | 7 | 0 | 276 |
| **Total** | **1005** | **420** | **0** | **40** | **545** | **0** | **3295** |

This round's findings: 1 blocking, 4 minor.
