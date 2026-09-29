mergeable: yes

# AI review: third focused re-check of integration set 12, fnd/int13 at d0717859 (MESHSAT-1357)

This is an AI review, not a qualified engineering review.

**Set-up**
* Clone: `<scratch>/chk-int13b`, fetched and detached at `d0717859e6dbfcad69f288b85910ffde32f325f2` (checked with `git rev-parse fnd/int13`).
* The evidence archive `int13-evidence-69156cad.tar` and the 17 held vendor files are still installed; `git status` shows only my three reports.
* Time: 29 September 2026, 16:43 to 16:51 CEST (from `date`).
* Every rule tool ran from a scratch cwd with `VERDICT_DIR` in the session scratchpad. The replay ran in a scratchpad clone, which I removed afterwards.

**Counts: 0 blocking, 4 minor.**
* The change of diagnosis is sound. CFL-016 reads FAIL on true grounds and waits on an open item whose closing condition would stop the overclaims.
* Nothing else moves.
* Three sentences in the new text still say more than the filed checks say (n1 to n3). None supports a result: each errs toward FAIL or toward an open item. They should be corrected at the next registry pass, but they do not hold the merge.

## 1. The new CFL-016 entry and S-122, sentence by sentence

**The CFL-016 entry** (`pcb_requirements.yaml`, CFL-016's last evidence entry, text in `apply_cfl016_set12.py` lines 52 to 65):

| Sentence | Against the record | Verdict |
|---|---|---|
| The entry of apply_conops_4b_set12 said the other documents were read by check-int13-2, which found nothing stale outside CONOPS.md | CFL-016's entry of 7a9f7b5b says exactly that | true |
| "That sentence is withdrawn: check-int13-2 read CONOPS.md only, and says so." | Of the documents CFL-016 names, check-int13-2 records a reading of CONOPS.md only; that is check-int13-3's statement (its B1, "Not read"). check-int13-2 itself never says what it did not read | first half true; "and says so" is not in check-int13-2's words (n1) |
| The back-feed item went stale with 3115fc58; the board A rows with board A's round 8 (c0133147) | 3115fc58 first carries U537 to U554 in `gen_sch_b.py` and is not on main; c0133147's body opens "Round 8, board A" and first carries U35 to U38 and U26 as the outlet interlock | true |
| "In the words of check-int13-3": PANEL.md line 156 lists the back-feed as open, which set 12 draws | check-int13-3, B1 | true |
| "PANEL.md lines 155 and 156 still name U26 and board A's round 8 candidate at gen_sch_a.py:1240-1243" | check-int13-3 says line 156 names U26 (at `:1102`) and the candidate, and line 155 "carries the same candidate citation". Line 155 does not name U26 | misquoted (n2) |
| V2-SPEC.md line 76 lists the RockBLOCK's ENABLE forced low as owed | check-int13-3, B1 | true |
| CONOPS.md line 883 names the slots' earlier gate parts and an open L3; PANEL.md line 63 omits R52 and D23 | check-int13-3, n3 and n4 | true |
| No filed reading has re-read the rest of the named documents against set 12's netlists | The six filed checks under `records/int13/checks/`: none does | true |
| CONOPS 4b and the EMCON row stay as rewritten; check-int13-3 read them true pin by pin | check-int13-3 section 1 and its count line ("10 table rows, the preamble and 4 cells") | true |
| The result is FAIL (was PASS) | the parsed diff | true |

**S-122** (the open item's title, script lines 67 to 77):

| Sentence | Against the record | Verdict |
|---|---|---|
| The named documents have not been re-read whole against the committed netlists since S-07 | I read CFL-016's 75 evidence entries. Every re-read after S-07 is a diff reading ("two places change", "byte-identical") or a hand re-read of named lines; none claims a whole re-read against a netlist | true |
| "passages known from that check describe replaced circuits: PANEL.md lines 63, 155 and 156; V2-SPEC.md line 76; CONOPS.md line 883" | True of 156, 76 and 883. For line 63, check-int13-3 says the text "stays true" and the parts list is incomplete. For line 155, it says the line carries a stale candidate citation, while the circuit it describes (U35 and U37) is the generated one | too strong for 63 and 155 (n3) |
| The 4b preamble overstates the script; 146 assignments on 55 parts; the check read the rest (U9, R52, D23 pins, U214, U314, U22 to U24, LIME_HW_EN's source) | check-int13-3 n1; `GATES` holds 55 parts and 146 pins | true |
| Owner, closing condition | a condition, not a claim | see n4 on its scope |

**By my own rule:**
* Neither text claims a reading that no script made and no filed check states, as the ground for a result.
* The three misquotes (n1 to n3) attribute words to filed checks that the checks do not contain. Each errs in the conservative direction, and the FAIL stands without them, on PANEL.md line 156 and V2-SPEC.md line 76, which check-int13-3 states in its own words.

## 2. Is FAIL the right reading, and is the status form right

* **FAIL is right.**
  * CFL-016's acceptance asks that each named document "describes the circuit as generated".
  * On set 12, PANEL.md line 156 lists as open a back-feed that set 12 draws, and V2-SPEC.md line 76 lists as owed a RockBLOCK ENABLE that w4b drew.
  * These are known contradictions, not an absent input, so FAIL and not INCONCLUSIVE.
* **The status form is consistent.**
  * `rules_lib.py` allows CONFLICT_RESOLVED with FAIL. It forbids only FAIL without a phase or class, and CONFLICT_OPEN reading anything but FAIL.
  * The registry holds exactly two such records, CFL-006 (FAIL, waits on S-27 and S-86, resolved by D-06) and now CFL-016.
  * The named conflict (the 45bde541 passages of its statement) stays resolved by S-07. What fails is the continuing acceptance on set 12, which is the same shape as CFL-006.
  * `resolved_by` is dated to S-07 at 45bde541, so it stays true as history.
* **Rule checks.** `waits_on: [S-122]` names an open item. evidence_phase SCHEMATIC and class DESK_REVIEW are kept, and every `evidence_bound_to` is current (0 warnings).

## 3. What else moves

* **Parsed registry diff.** Only CFL-016 moved: `evidence` gained one entry with the older ones kept as a prefix, `evidence_result` went from PASS to FAIL, and `waits_on` was added. S-122 was added to `open_items` with the same keys as the other 72 plain items.
  * Nothing else moved: no other record, open item, closed item or top-level field.
  * S-121 is absent, as reserved.
* **Documents.**
  * `CURRENT-EVIDENCE.md` is not in the commit; its sha256/16 is `dbd82cddb8bcfdd4`. CON-010 and REQ-044, the two records bound to it, are current.
  * No record binds `REQUIREMENTS-TRACE.md` or the checks folder.
  * The trace page changes only where it should: the open-item count in its header (85 to 86); the PASS and FAIL counts (21 to 20 and 13 to 14; DESK_REVIEW 21 to 20 and 12 to 13); CFL-016's row, its "waits on S-122" and its new entry; the S-122 row; and CFL-016 moved from the passing list to the failing one (13 to 14).
* **Why CFL-016's FAIL is not on the evidence page or in the layout-entry reasons** (`rules_status.layout_entry`):
  * Layout entry counts the applicable SCHEMATIC rule rows, the holds with their `layout_entry_requires`, and the open records of kind feasibility.
  * CFL-016 is a conflict record. No hold names it (`pcb_board_holds.yaml`), and its rule DOC-002 is a RELEASE_PACKAGE rule read by `doc_provenance.py` and `ledger_verify.py`, not from the registry.
  * `CURRENT-EVIDENCE.md` renders rule and board pairs from `out/rule-audit`.
  * The layout-entry reasons are 34 as before: A 6, B 8, C 4, D 6, E 3, P 5, E5 2. None names CFL-016.
* **Runs.**

| Run | Result |
|---|---|
| `rules_status.py`, 3 times | exit 1; stdout byte identical, and identical to the runs at 69156cad and 7a9f7b5b; FAIL of 338 (PASS 195, INCONCLUSIVE 104, FAIL 39); the seven board audits and `summary.json` byte identical across runs and to 7a9f7b5b's |
| `rules_render.py`, 2 times | exit 0; `git status` clean |
| `rules_render.py --check` | 16 documents, 0 out of date |
| `--requirements --check` | current |
| `decisions_render.py --check` | exit 0 |
| `rules_lib.py` | 59 rules, 0 errors, 0 warnings |
| `rules_lib.py requirements` | 144 records, 0 errors, 0 warnings |
| `claims_check.py` (scratch `VERDICT_DIR`) | PASS, 91 claims, 0 unqualified |
| `tests/run.py test_requirements test_decision_register` | 71 passed, 0 failed |
| Replay of `apply_cfl016_set12.py` on a scratch clone at 7a9f7b5b, then `rules_render.py --requirements` | the registry, the trace page, the script and the two changed checks byte identical to d0717859 |

## 4. The re-filed checks

* **No local paths.** The six files under `records/int13/checks/` hold no `/home`, `/root`, `/tmp` or the runner's account name; the script also refuses on them (line 101).
* **They read as written.**
  * `check-int13-2.md` and `check-int13-3.md` differ from my `CHECK.md` and `CHECK-2.md` only where `<scratch>/` became `<scratch>/`, with every file name kept. The two sentences my n2 named now read "`check-set12-1.md` equals `<scratch>/chk-set12/CHECK.md` plus one filing comment" and "exist only as `<scratch>/chk-set12/CHECK-2.md` and `CHECK-3.md`".
  * `check-set12-2.md` and `-3.md` are byte identical to their sources.
  * `check-set12-1.md` is its source plus the filing comment.
  * `check-int13-1.md` holds no path.
* **Not added:** a filing comment on the `<scratch>` substitution, which I had suggested. The placeholder is self-evident, so nothing is lost.

## Minor items

* **n1. The CFL-016 entry's "check-int13-2 read CONOPS.md only, and says so."** check-int13-2 does not say what it did not read. The statement is check-int13-3's. Fix: "check-int13-3 records that check-int13-2 names, of these documents, CONOPS.md only."
* **n2. The same entry's "PANEL.md lines 155 and 156 still name U26 and board A's round 8 candidate at gen_sch_a.py:1240-1243"**, under "In the words of check-int13-3". Line 155 does not name U26. Fix: "PANEL.md line 156 names U26 (`gen_sch_a.py:1102`), and lines 155 and 156 cite board A's round 8 candidate at `gen_sch_a.py:1240-1243`."
* **n3. S-122's "passages known from that check describe replaced circuits: PANEL.md lines 63, 155 and 156".** check-int13-3 says line 63 stays true with an incomplete parts list, and line 155's circuit is the generated one under a stale candidate citation. Fix: "are stale or incomplete", with the check's reason per line.
* **n4. S-122's closing condition is narrower than CFL-016's acceptance.**
  * It re-derives "every statement of those documents about the EMCON line and the parts it gates".
  * CFL-016's statement also names the startup enables, ZEROIZE, the Service row, the outlets' tie to the PA, PANEL.md section 7's bus table, and the outcomes of decisions 28 and 40.
  * "CFL-016 is then re-read" covers this only implicitly. Fix: name every subject of CFL-016's statement in the condition, or say that the re-read of CFL-016 reads them.

*Observation, not counted:* the trace page labels every evidence entry of a record with the record's current result. All of CFL-016's historical entries, the S-07 readings included, now render as "Evidence (FAIL, DESK_REVIEW)", as CFL-006's do. This is the renderer's existing behaviour, not something this commit introduced.

**Counts: 0 blocking, 4 minor.**
* Sentences checked: 10 in the entry and 4 in S-122.
* Status: 3 runs, identical. Render: 2 runs, clean. Validators: 0 errors, 0 warnings. `claims_check`: 91/0. Tests: 71 passed, 0 failed.
* Replay: byte identical. Layout-entry reasons: 34, unchanged.
