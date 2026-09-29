mergeable: no

# AI review: second focused re-check of integration set 12, fnd/int13 at 7a9f7b5b (MESHSAT-1357)

This is an AI review, not a qualified engineering review.

**Set-up**
* Clone: `<scratch>/chk-int13b`, fetched and detached at `7a9f7b5b08484a50ac117a6329a3787617f6979a` (checked with `git rev-parse fnd/int13`).
* The evidence archive `int13-evidence-69156cad.tar` and the 17 held vendor files stay installed from the first re-check. `git status` shows only my two reports.
* Time: 29 September 2026, 16:28 to 16:38 CEST (from `date`).
* Every rule tool ran from a scratch cwd with `VERDICT_DIR` in the session scratchpad. Replays ran in scratchpad clones, which I removed afterwards.

**Counts: 1 blocking, 4 minor.**
* The rewritten section 4b and the EMCON row's four cells are true, row by row, on the four netlists. The dropped text that mattered is covered, the D-05 paragraph and the notes after the table are unchanged, and minors 1 to 5 are answered.
* The new CFL-016 entry makes a third claim of a reading nobody recorded, and that claim is false in substance.

## Blocking items

**B1 (third round). CFL-016's new entry says my re-check read the record's other documents and found nothing stale outside CONOPS.md. Neither half is true.**

*Where:*
* `v2/ecad/tools/pcb_requirements.yaml` lines 13707 to 13721, CFL-016's entry "v2/docs/CONOPS.md re-read at integration set 12, second pass".
* It is written by `v2/docs/records/int13/apply_conops_4b_set12.py` lines 226 to 235. The sentence at fault is at lines 233 to 235: "The other documents this record names were read by that re-check, which found no stale statement outside CONOPS.md".

*Why it is false:*
* **Not read.** The re-check, as filed (`checks/check-int13-2.md`), records a reading of CONOPS lines 315, 411, 412, 414 to 417 and board B's netlist. It does not mention `PANEL.md`, `V2-SPEC.md`, `OPERATING-ENVELOPE.md`, `TEST-PLAN.md` or decisions 28 and 40. It found nothing about them, so it did not find them clean.
* **Stale statements do exist in them.** Each is on a subject the same entry calls stale in CONOPS:
  * `v2/docs/PANEL.md` line 156 (section 6, the EMCON_HW row) says: "Open: the back-feed of SD-EMC-2 into the RockBLOCK, the E22 and the E72 (the load switches now discharge their outputs; the lines' series resistance is not drawn)." Set 12 draws those paths (U537 to U553 on board B, commit 3115fc58). S-01 says they are "drawn and closed at desk", and CONOPS's new cell 8 says so too.
  * PANEL.md line 156 also names `U26` (`gen_sch_a.py:1102`) and "board A's round 8 candidate" with U35 and U37 at `gen_sch_a.py:1240-1243`. Line 155, the TX_INHIBIT_n row, carries the same candidate citation. This is the U26 and candidate framing that the entry itself calls stale in CONOPS. On board A `6c40250c`, U26 is the outlet interlock and U35 to U38 are generated, at `gen_sch_a.py` lines 1572 to 1575.
  * `v2/docs/V2-SPEC.md` line 76 lists "the RockBLOCK 9704's ENABLE forced low by the EMCON hardware with its stored energy bounded" among the changes "still owed". V2-SPEC line 24 records the ENABLE as "held low by the EMCON hardware since board B's stream w4b", and so does CONOPS's new cell 8.
  * CFL-016's statement names PANEL.md sections 1, 6 and 7 and V2-SPEC.md lines 24, 34, 41, 43 and 76. So its acceptance ("each named document ... describes the circuit as generated") is not met, and its PASS is rebound on a false reason.
* **Two dates in the same entry are wrong.** It says the stale rows were "stale on main since stream w4b".
  * The EMCON row's "back-feed paths owed" became stale with set 12 (3115fc58); on main they were still owed.
  * The board A rows became stale with board A's round 8 (c0133147), not with w4b (910da406).

*Fix:*
* Append a CFL-016 entry that withdraws the sentence and states only what was read.
* Correct PANEL.md lines 155 and 156 and V2-SPEC.md line 76 from the committed netlists, asserting first as `apply_conops_4b_set12.py` does. Then rebind the records bound to those files: CFL-001, CFL-005, CFL-014, CFL-015 and CFL-016 for PANEL.md; CFL-010, CFL-013, CFL-016 and REQ-005 for V2-SPEC.md.
* Or open an S item for those passages and let CFL-016 read accordingly.
* Correct the two dates.
* A method note, since this is the third claim of an unrecorded reading on this record: write into the registry only readings that the script itself performs, or that a filed check records in its own words.

## 1. Section 4b and the EMCON row against the netlists

I parsed all four netlists myself with `tx_inhibit.parse_netlist`: A `6c40250c47195ebb`, B `3ef9b8c49a01b728`, C `87b69472ac83ca5a`, D `a2d48972d171aad1`. Each sha256/16 was read from its file.

| Row | What the text says | Netlist (part: pins) | Holds |
|---|---|---|---|
| Preamble | C: U9 buffers TX_INHIBIT_n onto EMCON_HW through R52 330 Ohm; D23 clamps EMCON_HW to TX_INHIBIT_n | U9 (74LVC1G17 buffer) 2 TX_INHIBIT_n, 4 EMCON_HW_DRV, 5 +3V3; R52 330R 1% EMCON_HW_DRV to EMCON_HW; D23 BAT46W K on TX_INHIBIT_n, A on EMCON_HW | yes |
| Preamble | B inverts EMCON_HW per slot from each module's 3.3 V | U112/U212/U312 SN74LVC1G04: 2 EMCON_HW, 4 EMCON_ON1..3, 5 +3V3_CM1..3 | yes |
| LimeSDR | EMCON_HW AND hub port power AND software enable into the eFuse, its only supply | U501 EMCON_HW AND LIME_HW_EN (U102 PWRCTL1, the TUSB8041's port power); U502 AND LIME_SW_EN; LIME_EN via R529 to U23 (TPS259631) pin 3; U23.5 +5V_LIME to J_LIME VBUS | yes |
| RockBLOCK | RB_EN = EMCON_HW AND RB_SW_EN (U503) | U503 1, 2, 4; RB_EN via R530 to U24 pin 3; U24.5 +5V_RB to J_RB9704.15 | yes |
| RockBLOCK | ENABLE low in hardware since w4b: U536 EMCON_HW AND RB_SW_IEN, through R532 since set 12 | U536 1 EMCON_HW, 2 RB_SW_IEN (U6.19), 4 RB_IEN_DRV; R532 2.7k to RB_IEN (J_RB9704.3, I_EN). U536 first appears in `gen_sch_b.py` at 910da406 (stream w4b); R532 at 3115fc58 (set 12), and it is absent from main's netlist | yes |
| RockBLOCK | U543 TPS3808G30 powered from +5V_DEV, watching +3V3_DEV, holds it low below 2.79 V | U543 1 RB_IEN, 5 SENSE +3V3_DEV, 6 VDD +5V_DEV; G30 threshold 2.79 V (`ti-tps3808.pdf`) | yes |
| RockBLOCK | since set 12, RXD and P_EN pass only while RB_GO = RB_IEN AND I_BTD (U537 to U539) | U537 1 RB_IEN, 2 RB_STATUS (J.7, I_BTD), 4 RB_GO; U538 RB_RXD_H AND RB_GO into J.14; U539 RB_CTRL_H AND RB_GO into J.6. U537 first appears at 3115fc58 | yes |
| E22 | unchanged from the first re-check | read there pin by pin | yes |
| E72 | E72_EN = EMCON_HW AND ZB_ON (U505) into U22; since set 12, RX, reset and BSL only through open drains U540 to U542; RX pulled up to +3V3_ZB (R536, R537) | U505 1, 2, 4; U22.5 EN on E72_EN, VOUT +3V3_ZB to U13.20/U14.20; U540/U542 (SN74LVC2G07, +3V3_DEV) drive ZBx_RXD and ZBx_RST_n; U541 both BSL; R536/R537 on +3V3_ZB; no other host line reaches U13/U14 | yes |
| 5G | buck U203 enable S2A_EN = EMCON_HW AND PCIE_PWR_EN2 from U216 on slot 2's 5 V since w4b | U203.3 S2A_EN; U216 (SN74LV1T08) 1 EMCON_HW, 2 PCIE_PWR_EN2, 4 S2A_EN, 5 +5V_S2 (which feeds U31A's 5 V pins); SN74LV1T08 first appears at 910da406 | yes |
| 5G | FULL_CARD_POWER_OFF# low by U220 from EMCON_ON2; held by U221 on the buck's output through U554 (D4E-F2, set 12); W_DISABLE1# by U215; discharge Q212, R295 15 Ohm | U220 1 EMCON_ON2, 6 5G_PWROFF_n; U221 5, 6 +3V3_S2A, 1 5G_TPR_n; U554 (SN74LVC2G07) 1 5G_TPR_n, 6 5G_PWROFF_n; U215 6 5G_W_DIS_n, 3 GND; Q212 G EMCON_ON2, D 5G_DCHG; R295 +3V3_M2C2 to 5G_DCHG. U221 is from b76c18cb (round 8), U554 from 3115fc58 | yes |
| WiFi | S1A_EN and S3A_EN from U116 and U316 on each slot's 5 V since w4b; W_DISABLE1# by U115 and U315 from EMCON_ON1/3 | U116/U316 1 EMCON_HW, 2 PCIE_PWR_EN1/3, 4 S1A_EN/S3A_EN, 5 +5V_S1/S3; U103.3 and U303.3 on those nets; U115/U315 6 on WIFI_W_DIS_n/WIFI2_W_DIS_n, pin 3 GND | yes |
| SA868 + PA | D: KEY = PTT_ANY AND TX_INHIBIT_n (U12); PA_KEY = KEY AND PA_EN (U14). A: PA_EN = TX_INHIBIT_n AND EMCON_HW AND PA_HOLD (U35, U36 on +3V3_EMCON); exciter supply not gated | D U12 1 PTT_ANY, 2 TX_INHIBIT_n, 4 KEY; U14 1 KEY, 2 PA_EN (J_HARN1.9), 4 PA_KEY. A U35 1 TX_INHIBIT_n, 2 EMCON_HW, 4 PA_TXOK; U36 1 PA_TXOK, 2 PA_HOLD (U40.6), 4 PA_EN, R58 to PA_UVLO, U13 LM5176 (+13V8_PA); both pin 5 +3V3_EMCON. SA868 U2 VBAT on +5V_SA through FB1, no gate. PA_TXOK first appears at c0133147 | yes |
| QMX | HF_EN = TX_INHIBIT_n AND EMCON_HW AND HF_HOLD (U37, U38 on +3V3_EMCON) into its DC converter | U37/U38 as U35/U36 with HF_*; HF_EN via R124 to HF_UVLO, U15 LM5176 (+12V_HF) | yes |
| CM5 radios | U{s}13 from EMCON_ON{s}, U{s}14 from the software request, open drains on the module's 3.3 V | U113/U213/U313 1, 3 EMCON_ON{s}, 6 WL_nDIS{s}, 4 BT_nDIS{s}, 5 +3V3_CM{s}; U114/U214/U314 from WL/BT_nDIS{s}_OFF (U6 outputs) | yes |
| Receive-only | nothing | LG290P U11 on ungated +3V3_DEV | yes |

**The EMCON row (line 315).**
* Cells 0 to 3 and cell 6 are byte identical to 69156cad. Cells 4, 5, 7 and 8 are rewritten.
* Cells 4 and 5 agree with the table above.
* Cell 8's owed list matches `feasibility/EMCON.md` section 4d.5 item by item: E-04, E-11, E-01/S-92, S-93, the walk classes, S-44, E-01 to E-10 and E-12, and section 6.
* Cell 8's "drawn and closed at desk" list matches section 4c (W4B-D1 and W4B-D2, L4 case (2) closed on U501 to U504) and section 4d. SD-EMC-1r8 is from round 8.

**Scope of the diff.**
* The CONOPS diff has four hunks, at old lines 315, 399 to 406, 410 to 411 and 413 to 418, all after section 2.
* The E22 row (412) and the receive-only row (419) are unchanged.
* The needs pin equals CONOPS's full sha256 `3c5d4907...`.
* The REQ-005 reason (section 2a only) and the CFL-014 reason (the Charging row only) are true.

**Replay.**
* `apply_conops_4b_set12.py` replayed on a scratch clone at 69156cad gives CONOPS, the registry, the README, the script and the three filed checks byte identical to 7a9f7b5b.
* After `rules_render.py --requirements`, it gives the trace page byte identical too.

## 2. What the rewrite dropped

* The D-05 paragraph and every line after the table are unchanged (compared line by line to section 4b.1).
* In the other columns of the table, only the RockBLOCK's "after the gate opens" became "after the supply gate opens".
* The old preamble's statements on the per-slot inversion, D4E-F1 and board A are carried in the new preamble.
* Dropped:
  * The statement that every stage on EMCON_ON is an SN74LVC2G06 open drain, except Q212. It is true, and it is kept in `feasibility/EMCON.md` section 4b.
  * The note that rows naming U19, U20, Q206, Q111, Q311, Q106, Q306 or U{s}11 "read with those parts". See minor n3.

## 3. The CFL-016, REQ-005 and CFL-014 entries

* The parsed diff moves only `evidence` and `evidence_bound_to` of CFL-016, REQ-005 and CFL-014, plus `needs_document_sha256`. Every older entry is kept as a prefix.
* Every sentence of the three entries is true, with these exceptions:
  * CFL-016's "stale on main since stream w4b" dates.
  * CFL-016's closing claim about the other documents (B1 above).
* "146 pin assignments" equals the count in `GATES` (55 parts).

## 4. My minors 1 to 5

| Minor | Answer | Verdict |
|---|---|---|
| 1 (U543's supply, R532's date, pin 6) | row text; `GATES` line 49 asserts U543 pin 6 | answered |
| 2 (the preamble's 45bde541) | the preamble names the four set 12 netlists | answered |
| 3 (board A rows) | rewritten on U35 to U38 with no line citations | answered |
| 4 (the re-checks not filed) | `check-set12-2.md` and `-3.md` byte identical to `<scratch>/chk-set12/CHECK-2.md` and `CHECK-3.md`; README row corrected | answered (see n2 on the third filed file) |
| 5 (line shifts) | README: "+35 from main's line 860, +55 from main's line 910" | answered; it matches the hunks |

## 5. Runs

| Run | Result |
|---|---|
| `claims_check.py` (scratch `VERDICT_DIR`) | PASS, 91 claims, 0 unqualified |
| `rules_status.py`, 3 times | exit 1; stdout byte identical (and identical to the run at 69156cad); FAIL of 338 (PASS 195, INCONCLUSIVE 104, FAIL 39); the seven board audits and `summary.json` identical across runs and to 69156cad's |
| `rules_render.py`, 2 times | exit 0; `git status` clean |
| `rules_render.py --check` | 16 documents, 0 out of date |
| `--requirements --check` | current |
| `decisions_render.py --check` | exit 0 |
| `rules_lib.py` | 59 rules, 0 errors, 0 warnings |
| `rules_lib.py requirements` | 144 records, 0 errors, 0 warnings |
| `tests/run.py test_requirements` | 66 passed, 0 failed |

The commit changes no verdict file, so the readings compared in my first re-check stand: 615 routed, 0 moved.

## Minor items

* **n1. `v2/docs/CONOPS.md` lines 400 to 401 overstate what the script asserted.** The text says "every gate, supply and net the rows below name was asserted on those netlists by `apply_conops_4b_set12.py`". `GATES` asserts:
  * no pins of U9, R52 or D23 (only presence, and R52's value);
  * nothing of U214 or U314;
  * nothing of U22's or U23 and U24's pins;
  * nothing of LIME_HW_EN's source.

  I read each on the netlists and each holds, so the circuit text is true. Fix: extend `GATES`, or say "the gates listed in the script".
* **n2. `v2/docs/records/int13/checks/check-int13-2.md` lines 144 and 164 are not my report as written.** The filing regex (`apply_conops_4b_set12.py` line 254) replaced whole file paths with "a scratch clone". The results read "`check-set12-1.md` equals a scratch clone plus one filing comment" and "The re-checks exist only as a scratch clone and `CHECK-3.md`". Fix: replace a path by a name that keeps the file (for example "the checker's `CHECK-2.md`"), and add a filing comment stating the substitution.
* **n3. The dropped U{s}11 pointer.** `v2/docs/CONOPS.md` line 883 (section 4e, dated 45bde541 by its own header) still says a loss of +3V3_DEV "releases every EMCON gate hung on `EMCON_ON` or on a slot's `U{s}11` (EMCON.md L3, open under S-01)". `feasibility/EMCON.md` section 7 records L3 as done in board B's round 8. This is outside CFL-016's named rows. Fix: correct the row with the PANEL.md pass.
* **n4. `v2/docs/PANEL.md` line 63 (section 1, EMCON logic) lists U9 driving EMCON_HW with no mention of R52 or D23.** "EMCON_HW follows TX_INHIBIT_n" stays true; the list of backer parts is incomplete. Fold it into B1's PANEL.md correction.

**Counts: 1 blocking, 4 minor.**
* Rows read pin by pin: 10 table rows, the preamble and 4 cells.
* Replay: byte identical.
* Validators: 0 errors. `claims_check`: 91/0. Tests: 66 passed, 0 failed.
