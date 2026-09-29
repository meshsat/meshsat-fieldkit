mergeable: no

# AI review: focused re-check of integration set 12 after the integrator's answers, fnd/int13 at 69156cad (MESHSAT-1357)

This is an AI review, not a qualified engineering review.

**Set-up**
* Clone: a scratch clone, a shared clone detached at `69156cad11ac064f414c16a696c9aefc212a57e4` (checked with `git rev-parse fnd/int13`, still the tip at 16:11).
* Evidence archive of the tip installed: `int13-evidence-69156cad.tar`, sha256 `5f2ee6236328b915c02d...`, 939 files; `git status` clean after it.
* Comparison clone (the coordinator's instruction): a scratch clone, a shared clone at `005e5f5e` with the first check's archive `int13-evidence-005e5f5e.tar` (sha256 `e2256dd9777dd2714f4374da...`) installed; `git status` clean after it.
* The 17 held vendor files: byte identical to the int13 worktree's 17 ignored files; `ibis_fetch.py --check` reads 13 PRESENT of 13; the four TI sheets match `v2/vendor/sources.txt` lines 454 to 457 by full sha256.
* Time: 29 September 2026, 15:56 to 16:13 CEST (from `date`).
* Written in the clone: only this file. My scripts and outputs are in the session scratchpad (`chkb/`). Every rule tool ran from a scratch cwd with `VERDICT_DIR` in the scratchpad; `git status` stayed clean throughout.

**Counts: 1 blocking, 5 minor.** B1 is answered for the two rows it named, and the answer is reproduced byte for byte, but the new CFL-016 entry claims more than was read, and three other rows of the documents it names are still false. m1 to m9 are answered and true. The readings, the order code, the census spec, the validators and the tests hold.

## Blocking items

**B1 (carried). CFL-016's correcting entry says every named document now describes the circuit; three CONOPS rows it names still do not.**

*Where:*
* `v2/ecad/tools/pcb_requirements.yaml` lines 13680 to 13691 (CFL-016's entry "v2/docs/CONOPS.md re-read at integration set 12 (apply_check13_fixes, ...)"), written by `v2/docs/records/int13/apply_check13_fixes.py` lines 154 to 163.
* The sentences at fault: "the section's other rows were read against the same netlist by the check" and "Re-read: every named document describes the circuit as generated".

*Why they are false (board B netlist `3ef9b8c49a01b728`, parsed with `tx_inhibit.parse_netlist`):*
* `v2/docs/CONOPS.md` line 414, the RM520N-GL 5G row: "the enable of its 3.3 V buck, pulled low by `U215` from `EMCON_ON2`". The card's buck is U203 (AP64500, +3V3_S2A, through R265 to +3V3_M2C2). Its EN pin 3 is `S2A_EN`, driven only by U216 pin 4, an SN74LV1T08 on +5V_S2: `EMCON_HW` (pin 1) AND `PCIE_PWR_EN2` (pin 2). U215's second channel is spare: pin 3 on GND, pin 4 NC. U215 drives only `5G_W_DIS_n` (pin 6).
* Line 415, the AW7915-AED row: "the enable of each card's 3.3 V buck, pulled low by `U115` and `U315`". `S1A_EN` (U103 pin 3) and `S3A_EN` (U303 pin 3) are driven only by U116 and U316 (`EMCON_HW` AND `PCIE_PWR_EN1/3`, on +5V_S1/+5V_S3). U115 and U315 pin 3 are on GND and pin 4 is NC; each drives only its card's W_DISABLE1#.
* Line 315, the EMCON row of section 4, which CFL-016's statement names ("CONOPS sections 4, 4b and 5 (the startup enables, EMCON, ... rows)"):
  * It says "the RockBLOCK keeps running on its own stored energy with its ENABLE held by firmware until that ENABLE is forced low in hardware". That contradicts the corrected line 411 and the netlist: `RB_IEN` (J_RB9704 pin 3) is driven by U536 = `EMCON_HW` AND `RB_SW_IEN` through R532, and pulled low by U543.
  * Its "session work owed" list still names "the back-feed paths into the RockBLOCK, the E22 and the E72 (SD-EMC-2)". Set 12 draws those (U537 to U553), and S-01's own text now says they are "drawn and closed at desk".
* All three were already stale on main: W4B-D3 and W4B-D1, commit `910da406` of 27 September. Main's netlist `97823ef1171a61ce` has the same U215, U216, U115, U116, U315 and U316 as the tip. `feasibility/EMCON.md` section 4c records the change ("U{s}15's second channel is freed") and says it supersedes the older statements. CONOPS was never brought into line.
* "Read ... by the check": `checks/check-int13-1.md` records a reading of lines 411 and 412 only. It names no reading of the other rows.

*Why it blocks:* this is B1's own defect again. CFL-016 is CONFLICT_RESOLVED with evidence PASS and `release_effect: BLOCKER`, and it is rebound on a reason that is not true of the file it binds (`CONOPS.md@b2c55e289da2dcbc`).

*Fix:*
* Correct lines 414 and 415 so that U216, U116 and U316 drive the card bucks' enables (`EMCON_HW` AND `PCIE_PWR_EN{s}`, run from each slot's 5 V), while U215, U115 and U315 pull only W_DISABLE1#.
* Correct line 315's RockBLOCK sentence and its owed list to set 12, keeping what S-01 still holds: the 9704's response to ENABLE, and every bench row.
* Assert each gate on the netlist before writing, as `gates_hold()` does: U216, U116 and U316 pins 1, 2 and 4; U203, U103 and U303 pin 3; U215, U115 and U315 pins 3 and 4.
* Append a correcting entry to CFL-016 that withdraws the two sentences. Rebind CFL-016, REQ-005, CFL-014 and `needs_document_sha256` to the new sha.
* If this is left for later, open an S item for lines 315, 414 and 415, and let CFL-016's reading say so rather than "every named document describes the circuit".

## 1. B1 as answered

**Rows 411 and 412, part by part and pin by pin** (`tx_inhibit.parse_netlist`, netlist sha256/16 `3ef9b8c49a01b728`):

| Row claim | Netlist | Holds |
|---|---|---|
| U503 drives the eFuse that feeds the RockBLOCK's only supply | U503.4 `RB_EN` to R530 to `RB_UVLO`, U24 (TPS259631) pin 3; U24.5 `+5V_RB` to J_RB9704.15 | yes |
| U536 = `EMCON_HW` AND `RB_SW_IEN` through R532 | U536 pins 1, 2, 4 = EMCON_HW, RB_SW_IEN (U6.19), RB_IEN_DRV; R532 RB_IEN_DRV to RB_IEN; RB_IEN = J_RB9704.3 (I_EN, Ground Control hardware page line 269) | yes (see m1 on "since stream w4b") |
| U543, a TPS3808G30, holds it low below 2.79 V | U543.1 RESET on RB_IEN, .5 SENSE on +3V3_DEV, .6 VDD on +5V_DEV; `ti-tps3808.pdf` gives 2.79 V for G30 | yes (see m1 on "on +3V3_DEV") |
| RB_GO = RB_IEN AND I_BTD (U537); the logic inputs pass only while RB_GO | U537 pins 1, 2, 4 = RB_IEN, RB_STATUS (J_RB9704.7, I_BTD, hardware page line 281), RB_GO; RB_GO gates U538 (RB_RXD, pin 14) and U539 (RB_CTRL, pin 6) | yes |
| E22_EN = EMCON_HW AND LORA_ON (U504) feeds the VCC load switch | U504 pins 1, 2, 4; R531 to E22_UVLO, U21 (TPS22810) EN; U21 VOUT +5V_LORA to U12 pins 9, 10 | yes |
| LORA_GO, a copy of E22_EN on slot 3's 3.3 V (U544) | U544.2 E22_EN, .4 LORA_GO, .5 +3V3_CM3 | yes |
| TXEN (U546), RXEN (U545), NRST, MOSI, SCK, NSS (U547 to U550) gated by LORA_GO | each AND has pin 2 on LORA_GO; outputs on U12 pins 7, 6, 15, 17, 18, 19; LORA_TXEN (U32A.54 GPIO4) no longer reaches U12 | yes |
| TXEN and RXEN held low by 100 k (R542, R543) | both 100k 1% to GND on LORA_TXEN_G and LORA_RXEN_G | yes |

**The section's other rows against the same netlist:**
* LimeSDR (U501, U502 into U23's EN, only VBUS): true.
* E72 (U505 into U22 feeding +3V3_ZB): true.
* The 5G module's FULL_CARD_POWER_OFF# (U220), W_DISABLE1# (U215) and discharge (Q212, R295): true.
* The compute modules' own radios (U{s}13, U{s}14): true.
* The receive-only row: true; LG290P U11 is on ungated +3V3_DEV.
* The header's inverter and open-drain statements: true.
* The 5G and WiFi buck enables: false (above).
* The board A rows: see m3.

**The records and the diff:**
* The CONOPS diff touches only lines 411 and 412, one hunk (`@@ -411,2 +411,2 @@`).
* Section 2 (the needs table, lines 75 to 145) is untouched. `rules_lib.py requirements` re-reads the published needs against the registry with 0 errors, so moving `needs_document_sha256` to `b2c55e28...` is right.
* REQ-005's reason (section 2a only) and CFL-014's reason (section 4's Charging row only) are true.
* In CFL-016's entry, everything before "the section's other rows" is true.

**Reproduction:**
* `apply_check13_fixes.py` replayed on a scratch clone at `a1f8ec70` gives `CONOPS.md`, `pcb_requirements.yaml`, `apply_rebind_after_circuit.py`, `apply_repin_bc_set12.py` and `rebind_reasons_set12.py` byte identical to `a46db71b`.
* `rules_render.py --requirements` there gives `REQUIREMENTS-TRACE.md` byte identical to `a46db71b`.

## 2. m1 to m9

**Registry diff at a46db71b (parsed):**
* Only `evidence` moved, on CON-010, REQ-044, CON-016, CON-018, CON-019, CFL-005 and REQ-077.
* `evidence` and `evidence_bound_to` moved on CFL-016, CFL-014 and REQ-005.
* Older entries are kept as a prefix.
* At top level only `needs_document_sha256` moved. Among the items only S-01, S-117 and S-118 changed.

| Minor | Answer | Verdict |
|---|---|---|
| m1 | CON-010 correcting entry: the L2 is EMCON.md's line-hold item | true; every other L2 in CON-010 is that item or the parsed parts list |
| m2 | one identical correcting entry on exactly CFL-005, CFL-014, CFL-016, CON-010, CON-016, CON-018, CON-019, REQ-077 | true: my own comparison of board A (`30ad8774` to `6c40250c`) gives +C233, C234, C235, R219, R220; changed C26, C27, L2, Q7 to Q10, R25; 0 pins moved; net CH_COMP2C added |
| m2, the script | `REBIND_CHANGE` default | reproduces: the old and new `entry` expressions, evaluated with the variable unset, give identical text (parts present and empty) |
| m3 | completing entries on CON-010 and REQ-044 | true; they name S-117, the census nodes and the closes |
| m4 | README note | answered; the shift lines are slightly off (m5 below) |
| m5 | README precondition plus the re-take with the sheets installed | answered; board A's `intent_rails` now records `c8595fa806a99074` and `f1aad251830260a5` for documents 7 and 8 |
| m6 | docstring corrected | matches lines 77 and 82 (already pinned: `continue`, then the file is written) |
| m7 | README, carried to the next regeneration of board B, with a reason | answered |
| m8 | S-01 dated pointer | true: `readback_d4e.py --board B` on 3ef9b8c4 fails exactly R527, R532, R238; `readback_chk12.py` reads "every check holds" |
| m9 | "carried at 230fdd65 (first committed at 3d3e32d6)" | true: board A's netlist first reads `6c40250c` at 3d3e32d6, an ancestor of 230fdd65 |

## 3. 58d2ea3f

* **C22932.** JLCPCB's public parts API (queried at 16:03) gives UNI-ROYAL 0603WAF1913T5E, 191 kOhm, plus or minus 1 %, 100 mW, 0603, stock 69,150.
  * R219 is `191k 1%` on `R_0603_1608Metric`.
  * The new MAP row is the first and only MAP entry that matches it (parsed with `ast`).
* **Census spec.** `pdftotext -layout` of page 1 of both held sheets draws S 1 8 D, S 2 7 D, S 3 6 D and G 4 5 D.
  * Board A's Q7 to Q10 sit on PowerPAK SO-8 lands with pins 1 to 3 on source nets, pin 4 on the gate drive and pin 5 on the drain net, which is consistent.
  * `test_rails_census` passes with the sheets installed.

## 4. The readings

**Routed verdicts, tip clone against the first check's archive clone:**
* There are 615 `routed/*.verdict.json` on each side, none only on one side. **0 verdicts moved, 0 counts changed.**
* 90 files differ, all of them in `git_head`, `version`, `tools_tree_sha` and `ts` (the 90 re-taken at `a46db71b`; the other 525 are byte identical). Beyond that:
  * `erc_report.sha256_16` differs on 6 `erc_gate` readings. The six ERC reports differ only in their `date` fields.
  * Board A's `intent_rails` differs on documents 7 and 8: from null to the held sheets' shas.
* The same holds for the 347 unrouted `out/*.verdict.json`: 0 moved, 0 counts changed. `claims_check` (91, 0) and `rules_complete` (339 pairs, 0 errors) are unchanged, and `summary.json` is identical.
* SI-001's `edge_length` reads the models PRESENT (10 asked, 10 present) on both sides.
* The integrator's comparison holds.

**Page runs**

| Run | Result |
|---|---|
| `rules_status.py`, 3 times | exit 1; stdout byte identical; FAIL of 338 (PASS 195, INCONCLUSIVE 104, FAIL 39); the seven board audits equal the archive's once the clone path is normalised; `summary.json` identical; the two verdicts differ only in `ts` |
| `rules_render.py`, 2 times | exit 0; `git status` clean |
| `rules_render.py --check` | 16 documents, 0 out of date |
| `--requirements --check` | current |
| `decisions_render.py --check` | exit 0 |
| `rules_lib.py` | 59 rules, 0 errors, 0 warnings |
| `rules_lib.py requirements` | 144 records, 0 errors, 0 warnings |

## 5. Tests

`tests/run.py test_rails_census test_order_codes test_requirements test_rules_registry test_decision_register`, run from the clone's `v2/ecad/tools` with the 17 held files installed:
* **119 passed, 0 failed, 0 skipped.**
* By module: rails_census 13, order_codes 30, requirements 66, rules_registry 5, decision_register 5.

## 6. Every changed file

`005e5f5e..69156cad` changes 103 files (99 modified, 4 added):
* 58d2ea3f: `lcsc_fill.py` and `test_rails_census.py` (item 3).
* a1f8ec70: `EXECUTION-PLAN.md`; the merge brings exactly `77e35dd3`'s diff, and main is still `77e35dd3`.
* a46db71b: CONOPS, the trace page, the registry, the four scripts, the README and the two filed checks (items 1 and 2).
  * `check-int13-1.md` equals the first check's CHECK.md apart from the clone path line.
  * `check-set12-1.md` equals a scratch clone plus one filing comment.
* 69156cad: 90 routed verdicts (item 4).

Nothing unexplained.

## Minor items

* **m1. CONOPS.md line 411: two phrases misstate the parts.**
  * "`U543`, a TPS3808G30 supervisor on `+3V3_DEV`": U543 is powered from +5V_DEV (pin 6) and senses +3V3_DEV (pin 5), as its own value text says ("supervisor on +5V_DEV watching +3V3_DEV").
  * "through `R532` (since stream w4b)": R532 is set 12's (D4E-B). On main, U536 pin 4 drove RB_IEN directly.
  * `apply_check13_fixes.py` line 60 asserts only U543 pins 1 and 5.
  * Fix: "powered from +5V_DEV and watching +3V3_DEV"; date U536 to w4b and R532 to set 12; assert pin 6.
* **m2. CONOPS.md line 399: the section heading paragraph still says it was read at `45bde541`.** Rows 411 and 412 now describe set 12's netlist. Add the netlist they were read at.
* **m3. CONOPS.md lines 416 and 417, board A's rows, predate board A as generated.**
  * They cite `U26` as generated, and "board A's round 8 candidate" with `gen_sch_a.py` lines 1240 to 1243.
  * On board A `6c40250c`, U26 is the outlet interlock, and U35 to U38 form PA_EN and HF_EN with PA_HOLD and HF_HOLD (through U40), not PA_SW_EN and HF_SW_EN.
  * The `ic()` calls are at lines 1572 to 1575 (1517 to 1520 on main).
  * The problem predates set 12. It is worth correcting with B1's fix.
* **m4. README.md, the "Checks and answers" table.**
  * It says `checks/check-set12-1.md` holds the substance check "and its re-checks on rf2walk2 and rf2walk3".
  * The file holds only the first report. The re-checks exist only as a scratch clone and `CHECK-3.md`, outside the tree, and `records/rf2walk/README.md` cites them by those scratch paths.
  * Fix: file them as `check-set12-2.md` and `check-set12-3.md`, or correct the row.
* **m5. README.md, the m4 note: "+35 lines after line 857 and by +55 after line 907".**
  * The hunks start at main's lines 860 (+35) and 910 (+20, cumulative +55), so lines 858 to 861 and 908 to 910 do not move as stated.
  * Fix: say "from line 862" and "from line 911".

**Counts: 1 blocking, 5 minor. Routed verdicts compared: 615, 0 moved, 0 counts changed. Unrouted: 347, 0 moved. Tests: 119 passed, 0 failed. Validators: 0 errors.**
