# Fresh check of the set 6 integration candidate at 1c4235ec (AI review), 28 September 2026

<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357). The checker wrote none of the candidate; its scratch scripts are local (_scratch/chk-int7/). Its findings are answered one by one in CHECK-RESPONSE.md beside this file. -->

# AI check of the set 6 integration candidate, `fnd/int7` at `1c4235ec` (MESHSAT-1357)

This is an AI review by a checker that wrote none of the candidate. It is not a qualified engineering review and replaces none. Prototype design: no V2 board has been built, ordered or measured; everything below is a reading of files.

Checked 28 September 2026, 17:15 to 17:34 CEST, in `/home/claude-runner/worktrees/meshsat-fieldkit/int7` (read only; HEAD `1c4235ec`, `git status` empty before and after). Scratch scripts are in `/home/claude-runner/worktrees/meshsat-fieldkit/_scratch/chk-int7/`.

```
mergeable: no
```

Three blocking findings, all in text the integration wrote. No reading, page count or merge result is wrong. One registry apply script, a CLOSURE.md edit, a re-render and a rebind answer them; no reading needs re-taking.

## blocking

**B-1, item 3: CON-010's link and S-92's text leave out board A's two undecided rows, and the entry gives a reason the files do not.**

- **Problem (a):** S-92 says "this item is the dependency that remains". By the record's own predicate that is false, because `inhibit_chain_a` is an element and reads 2 undecided.
- **Problem (b):** `waits_on: [S-92]` therefore omits a dependency, and no open or closed item names it (searched for LM5176 with gate drive: none).
- **Problem (c):** the entry says board A's rows are ones "the walk reaches in hardware and cannot time from a held document". The files say the walk is UNDECIDED on the LM5176's gate-drive level in shutdown, which TI does not state. The walk times nothing. The clause is typed in `apply_con010_redecide.py`.
- **Evidence:**
  - `v2/ecad/pcb-a-power-a23/routed/inhibit_chain_a.verdict.json`: fail 0, pass 7, undecided 2 of 9.
  - `v2/docs/feasibility/EMCON.md` lines 76 to 79 and rows 2 and 3 of section 0a (lines 185, 186).
  - `v2/ecad/tools/tx_inhibit.py` lines 3737 to 3739.
- **Counter-example:** close S-92 as its own text asks, so `inhibit_chain_d` reads PASS of 8. The predicate still returns INCONCLUSIVE on `inhibit_chain_a`. CON-010 then stands INCONCLUSIVE with an empty `waits_on`, the state erratum l of RELEASE-H3.md recorded for S-64.
- **Suggested answer:** open an item for the LM5176 residual on J_PA and J_HF, add it to CON-010's `waits_on`, reword S-92 and correct the clause. INCONCLUSIVE stands.

**B-2, item 4: two dispositions whose reasons do not hold.**

- **S-65** (CIRCUIT_ITEM, "No record's acceptance names the rail's clamp coordination"):
  - EMCON.md lines 1102 to 1106 name this fault as "Not closed by this", reaching EMCON through U30 and U40, "a registry open item".
  - That page is the one FEA-002, REQ-030, REQ-032 and REQ-071 are bound to (`367c52bcba7eb2a1`), and FEA-002 requires the inhibit to hold "in every state of the lines' own supplies".
  - Counter-example: decide S-65 either way and the PA and QMX rows of EMCON.md change with it, while no record shows the dependency.
- **S-86** (PROCESS, "changing no reading"):
  - The reason covers only the item's first half. Its second half corrects `pcb_energy_chain.yaml`, where F1 carries the 287 ATOF figures and the holder takes the 297 MINI.
  - That file is a declared configuration input of `energy_chain.py` (`rules_status.py` line 810), so PWR-003's and BAT-002's readings are owed again when it changes.
  - I could not show a result flipping: the 297 sheet is held at `v2/vendor/keystone/littelfuse-297-ficcorp.pdf` and the gate prints the melting time. The defect is the reason as written.

**B-3, item 9: CLOSURE.md does not separate the kinds as it says it does.**

- **Problem (a):** section 3 omits two set 6 instrument corrections:
  - `tx_inhibit.py` in `910da406`, which RESULT.txt section 5 says moved eight of board B's eleven failed RF-002 rows.
  - `block_contract.py` in `d5e12880`, which turned E5's INT-001 and SCH-003 to FAIL.
- **Problem (b):** section 1 lists `d5e12880` as a circuit change while its own cell says "a contract, not a copper change".
- **Problem (c):** section 2 says "None" while section 1 holds set 6's declaration changes. RESULT.txt attributes PWR-001's moves on C, D, E and P to declarations and filed sheets.
- **Counter-example:** a reader of CLOSURE.md alone takes RF-002 on B, FAIL to INCONCLUSIVE, as a circuit closure. That is a checker repair readable as a circuit change, which the record's first paragraph says it prevents.

## minor

| id | item | note |
|---|---|---|
| m1 | 3 | "the owner's review of the restart plan, amendment XH-04" is cited in the registry, REQUIREMENTS-TRACE.md line 2113, `rules_lib.py` line 1160 and a test docstring. No file in the repository holds it; it exists only in `~/.claude/plans/fancy-cuddling-flask.md`. Not classed blocking because the predicate is written out in full. File the review under `v2/docs/reviews/`. |
| m2 | 3 | The script computes the result but types the facts around it (SC-67's values, S-64's closure), which I verified true. Its undecided branch tests `counts.undecided`, not the verdict, so a `safe_lines` reading INCONCLUSIVE would fall through to PASS. No effect today. |
| m3 | 1, 9 | Set 6 also closed S-57 (SC-70). The merge script's docstring and CLOSURE.md name only S-64, S-45 and S-76 between them. CLOSURE.md does not name REQ-077's FAIL to INCONCLUSIVE, which reaches `main` with this promotion. |
| m4 | 9 | "17 items linked from 28 records" is 28 links on 24 distinct records. |
| m5 | 4 | S-81's own closing condition is met ("or S-64 closes before that issue"). It was disposed, and its text still says CON-010 reads FAIL. |
| m6 | 4 | S-13 to CON-025 is a weak link: an order code cannot move a TVS capacitance constraint that reads PASS. |
| m7 | 4 | S-61 is rated major in its own text and carried "before board D's layout entry", yet is visible from no record or hold. I found no board D record to take it, so the reason holds as far as I searched. |
| m8 | 2 | S-91's title reads as if `H3-RESPONSE.md` exists; it does not. Two things it lists were done by this integration (`b3d66c70`, `a4b157f0`). |
| m9 | 2 | S-89 says "reproduced on four fixtures"; the review says four cases were run and two show a false PASS. |
| m10 | 9 | No run record of the 28 September re-take is filed under `v2/docs/records/int7/`. "110.7 s, exit 0" and "252 gitignored readings" cannot be traced from the tree. |
| m11 | 6 | Only 26 of the 90 re-written readings name `rules_lib.py` in their code bundle; the other 64 writers do not import it. |
| m12 | 3 | REQ-030, REQ-032 and REQ-071 stand FAIL, unchanged from `main`, bound to EMCON.md. One ground their entries name, "RF-002's reading of board B", now reads 0 failed. For the registry's writer. |

## verified

1. **Merge `069a5d97`:** parents are `7f3a4956` and `d04a4c4c`, base `6ec37197`.
   - The rule holds for every id: 59 open, 58 closed, none doubled, every block equal to a parent's.
   - Needs 19, rulings 29, choices 74 and records 144 equal the set 6 side; no entry lost.
   - Of 37 files `main` changed, 32 are byte-identical at the merge; the three hand-merged pages keep every added line of both sides.
   - RELEASE-H3.md is identical to `main`, the H3 package and both reviews are present, and `a5350e81` carries `main`'s two files unchanged.
2. **S-88 to S-92:** each read against its cited file. S-88, S-89, S-90 and S-92's counts are supported. S-91's twenty-eight is 13 plus 15 in the two checks. Exceptions are B-1, m8 and m9.
3. **CON-010:** recomputed by me as INCONCLUSIVE.
   - `inhibit_chain_d` 0 failed, 1 undecided of 8; `inhibit_chain_a` 0 failed, 2 undecided of 9; `safe_lines_d` and `safe_lines_a` PASS; none missing.
   - Netlist hashes equal the candidate table and the files (A `0a2b59087bcc2678`, C `3fddbb3edcd4248a`, D `7a2c0ac2190b141a`).
   - W3T-F1 is resolved: R14 is 2.2k 1%, R50 is 10k 1% from TX_INHIBIT_n to GND, `inhibit_chain_c` PASS of 6, and 0 failed on all six boards.
   - Statement and acceptance are unchanged from `main`; `evidence_result` is INCONCLUSIVE.
4. **Dispositions:** all 30 read. 16 links land on a record the item can move and 9 dispositions hold; the rest are B-2, m5, m6 and m7. The validator refuses an unlinked, undisposed item (`rules_lib.py` lines 1159 to 1172) and `test_requirements.py` line 848 tests it.
5. **Renderer:** the head sentence comes from `baseline_state` and the seven feasibility records. The two limit notices come from `limits_reading` and leave with the item. TRN-001 is marked on A only and REL-001 on all seven pages. `derived_notices`: 3 passed.
6. **Readings:** the layout-entry table has 35 rows (A 7, B 7, C 3, D 7, E 4, P 5, E5 2), equal to RESULT.txt, none AWAITING_REVALIDATION.
   - 90 tracked readings were re-written, the same 90 files as retake6, all at version `a4b157f07618`.
   - No verdict, count or evidence line changed against `7f3a4956`.
7. **Rebind:** the page is `ff781ceffbb41d80`. My own comparison gives 2 of 15 sections differing and 13 byte-identical. The rows named are on the page and both results are unchanged.
8. **Validators:** all five exit 0 (16 documents, 0 out of date; 59 rules and 144 records with 0 errors). Four test files: 3, 71, 28 and 10 passed, 0 failed.
9. **CLOSURE.md:** its numbers are the page's and RESULT.txt's (35 against 40 on `main`; 71, 10, 2; 209, 40, 89 of 338; 59, 58, 144). Nothing it calls closed is merely refreshed. Attribution is B-3.
10. **Prose:** no em or en dash in added prose; the three hits are the scripts' own dash detectors. The claim pattern finds 0 hits in 22 new registry texts. Prototype framing and the AI review label are present.

## not_done

- **Full suite on `1c4235ec`:** not run by me. `_scratch/int7-suite/suite-box.log` ends "2019 passed, 0 failed, 3 skipped", but its status file is empty and it names no commit, so I cannot attribute it.
- **`rules_status` on the final commit:** not re-run. That the pages are a fixed point rests on the `--check` validators against the worktree's existing audit.
- **The 252 gitignored readings:** not inspected.
- **The walk itself:** not re-run; B-1's reason is read from EMCON.md and the tool's own text.
- **SC-67's voltages:** read, not recalculated.
- **S-91's 28 findings and errata g to m:** counted, not checked one by one.
- **S-61, S-67 and S-83:** judged on statements, not every record's acceptance text.
