# Third check of the set 6 integration, candidate f2b8f98d (AI review), 28 September 2026

<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357), after the promotion it allowed. The checker wrote none of the candidate and neither of the two earlier checks; its scratch is local (_scratch/chk-int7-3/). Its minor items are answered in CHECK-RESPONSE.md, third part. -->

# Fresh check of the third candidate of the set 6 integration, `fnd/int7` at `f2b8f98d` (AI review), 28 September 2026

This is an AI review by a checker that wrote none of the candidate and neither of the two earlier checks. It is not a qualified engineering review and replaces none. Prototype design: no V2 board has been built, ordered or measured; everything below is a reading of files.

Checked 28 September 2026, 18:26 to 18:42 CEST, in `/home/claude-runner/worktrees/meshsat-fieldkit/int7`, read only. HEAD is `f2b8f98d5c8475e526f2c3a1318f082be395b4a6`; `git status` was empty before and after, and no file in the worktree is newer than my first scratch file. Scratch is `/home/claude-runner/worktrees/meshsat-fieldkit/_scratch/chk-int7-3/` (`dump.py`, `walk-run.txt`, two empty markers); the other scripts ran on standard input. For part of the run the session's harness allowed read-only commands only; the two test files ran after that lifted.

```
mergeable: yes
```

R-1 is answered by the walk's own measure. Nothing moved that should not have, and the answers introduced no blocking defect. The result holds for `f2b8f98d` exactly.

## blocking

None.

## minor

| id | item | note |
|---|---|---|
| p1 | A1 | `walk_grounds.py` reads all three rows from a walk on the four netlists `inhibit_chain_d` records (A, B, C, D). Board A's filed reading `inhibit_chain_a` records five (E as well). I re-ran the walk on the five: the same seven undecided rows, every report identical. No effect today; the script does not check it. |
| p2 | A2 | The coverage assertion is a necessary condition only. It matches U and Q designators by name, from a regular expression over the report's prose, without the board. U13 and U14 are different parts on boards A and D. It would pass an item that names a designator and misstates its ground. Here the prose carries every ground's substance. |
| p3 | A2 | `tx_inhibit.py` line 2413 prints at most three unsure grounds per state (`net["unsure"][:3]`). On these netlists the longest list is 2, over 92 networks solved, so nothing was cut. A longer list would drop grounds from the report without a sign. The closing condition (row decided) covers it. |
| p4 | A2 | S-92 ground (3) quotes 2.86 V "by R88 and R89 alone". The same report's chain line gives 3.12 V for the same divider. 2.86 V is the walk's adverse level "from the currents that are known"; the item does not say which of the two it quotes. |
| p5 | A2 | S-92 names bench E-01 as its bench route. E-01 (EMCON.md line 1665) names pin 5's threshold and input current, not U13 pin 4's off-state current. No hole follows, because the item closes on the row reading decided. |
| p6 | A2 | S-93's closing route calls the grounds of Q14 and Q24 "the instrument's own". That fits their first half (type or pin map not read). Their second half is a maker's unstated figure (the LM5176's drive in shutdown). The item states both halves. |
| p7 | A4 | FEA-002 (INCONCLUSIVE, boards a, b, c, d, kit, rests on RF-002) waits on S-01, S-02, S-44, S-87 and S-65, not on S-92 or S-93. EMCON.md, which it is bound to, shows the SA868's threshold and current, the LM5176 residual and board D's Q1. It does not show U14 (the INA226) or U13 pin 4's off-state current while powered. |
| p8 | n5 | The words remain in `rules_lib.py` line 1160 (comment) and `tests/test_derived_notices.py` line 2 (docstring). Leaving the comment is acceptable: 26 tracked readings name `rules_lib.py` in their code bundle. The carry is recorded in CHECK-RESPONSE.md only, in no open item. I did not check whether a test file is in any code bundle. |
| p9 | n7 | CLOSURE.md says "12 ERC reports with their provenance files". The manifest holds 6 ERC reports and their 6 provenance files. The sum, 240 and 12 of 252, is right. |
| p10 | n8 | The README's d6rel row says "no blocking item". The file adds a condition: "if you meant the board reading, treat m1 as blocking". The row does not carry it. |
| p11 | n8 | Six new files cite scratch folders by the runner's absolute path, which no reader of the repository can open. `main` already holds 13 files with that path. |
| p12 | D | CLOSURE.md section 6 says the suite read the same at `85ad1193`. The local log agrees (`_scratch/int7-suite2/suite-box.log`: 2019 passed, 0 failed, 3 skipped, EXIT 0, the commit's full hash). No record of it is in the tree, where the first candidate's is (`box/suite-1c4235ec.txt`). |
| p13 | D | CHECK-RESPONSE.md's first part (m4) still says 96 links; CLOSURE.md says 99. The first part is the second candidate's record and is unchanged; a reader may take 96 for the current figure. |

## verified

- **A1:** my run of `walk_grounds.py` without `--write` equals the filed `walk-grounds.txt` byte for byte, apart from the final newline that printing adds (15889 against 15888 bytes). Seven undecided rows, three on CON-010's boards. The grounds, from the report's parts:
  - SA868 exciter (D key on U2), three:
    - no input threshold stated for U2 pin 5, with SA_PTT_n at 2.85 V when U13's supply +3V3_D8 is down and at 2.86 V with EMCON on;
    - no input current stated for U2 pin 5;
    - U13 pin 4's off-state current while powered not stated.
  - 30 W amplifier (A power on J_PA), three:
    - U14 (INA226), pins 8 and 9 on +13V8_PA and pin 10 on PA_OUT, a part no class reads;
    - Q14 pin 5 (CSD18510Q5B) on PA_OUT, type or pin map not read, its other pins on PA_HDRV2 and PA_SW2 (U13 pins 19 and 18), no table stating the drive is off with its enable;
    - with U36's supply +3V3_EMCON down, PA_UVLO at 0.35 V and board D's Q1 gate on PA_EN, IGSS stated at 25 C only.
  - QMX (A power on J_HF), one: the same for Q24 pin 5 on HF_OUT with U15's drive (HF_HDRV2, HF_SW2).
- **A2:** every ground above is stated in the item that covers its row, with its part, pin, net, figure and what the maker does not state. No ground is named by its designator alone. Checked against the netlists:
  - board D: SA_PTT_n carries R88, R89, U13 pin 4 and U2 pin 5 only; Q1 is the 2N7002 with its gate on PA_EN (board A's Q1 is another part, on PI_KILL);
  - board A: U13 and U15 are LM5176PWPR; U14 is the INA226.
  - The walk's solved network for the EMCON state has R88 and R89 as its only pulls and no pin current.
  - SNVSAI1D 7.4.1 reads "Shutdown: VCC off, No switching" (`v2/vendor/ti/lm5176-datasheet.pdf`, `98191bec36d43771`).
  - EMCON.md lines 185, 186 and 1036 to 1039 name the LM5176 residual and board D's Q1, as S-93 says.
  - The designator assertion alone would not be enough (p2); the prose is.
- **A3:** CON-010 has `waits_on: [S-92, S-93]` and reads INCONCLUSIVE; statement and acceptance equal `e224ea36`. Entry 35 names every ground per row and equals my list. S-92 closes only when the re-take reads its row decided, S-93 only when both rows do. With CHECK-2's counter-examples applied, a row that stays undecided on a remaining ground keeps its item open. CON-010 cannot stand INCONCLUSIVE on these rows with nothing to wait on. The hole R-1 described is closed.
- **A4:** seven records rest on RF-002. REQ-030, REQ-032 and REQ-071 read FAIL and wait on S-94. REQ-031 is NOT_JUDGED. CFL-004 reads PASS on board B alone, on the six Compute Module rows, which the walk reads PASS. FEA-002 is p7. No record reads PASS on a row the walk leaves undecided.
- **B n1:** REQ-032 waits on S-01, S-94, S-65.
- **B n2:** CFL-006 (bound to `pcb_energy_chain.yaml@a09ca0293afd1f7c`) and FEA-005 (bound to two packet documents) wait on S-86.
- **B n3:** CLOSURE.md section 1 lists R51. `e28f91a6` drew it (10 k, RAIL_SENSE to GND); RESULT.txt names it nowhere.
- **B n4:** S-81's closing evidence no longer points at S-91's list.
- **B n5:** CON-010's entry says the review was pasted by the owner; the filed review's header agrees. The registry and the trace page no longer carry the old words. See p8.
- **B n6:** every statement in S-61's reason is true.
  - `fnd/d8dec31` (`f8e61f05`) is an ancestor of neither `main` nor the candidate; the review file is on that branch only.
  - D-F3 (lines 71 and 391) names J_USB3 and asks for a clamp, a bulk capacitor and a ferrite, not a current limit.
  - `pcb_board_holds.yaml` names neither S-61 nor J_USB3, on the candidate and on that branch.
  - SC-63 points at S-61 for the current limit.
- **B n7:** the manifest holds 252 entries, 240 verdict files and 12 others. See p9.
- **B n8:** all five rows of the README match their files in branch, commit, verdict and count of findings (7, 1 blocking and 10, 8, 10, NOT mergeable on three). Each commit is on its branch. `fnd/w5si2` tracks no model file; `fnd/w5si` tracks 13; the candidate none. Three filed results equal the checker's own file; two differ in one line each, as the README says.
- **B n9:** both items record a bench reading as a sample of one board.
- **C:** the 14 changed files are the registry, the trace page and 12 under `v2/docs/records/int7/`. CURRENT-EVIDENCE.md is byte-identical (`ff781ceffbb41d80`, same blob), and both bindings are unchanged. All 125 bindings of the registry hash to their files. Parsed differences are the eight expected and no other: CON-010 evidence entry 35; `waits_on` of REQ-032, CFL-006, FEA-005; titles of S-92, S-93; S-61's reason; S-81's closing evidence. No comment line changed.
- **D:** the five validators exit 0 (16 documents, 0 out of date; trace page current; 59 rules and 144 records, 0 errors). Tests: `derived_notices` 3 passed, `requirements` 71 passed, 0 failed.
  - Counts recomputed: 65 open, 59 closed, 144 records; 54 linked by 99 links on 60 records; 11 disposed; none both, none neither.
  - No em or en dash and no claim word in the five changed registry texts, no dash in the 861 added lines.
  - All 25 commits of `e224ea36..HEAD` are authored and committed by Kyriakos Papadopoulos, carry the issue tag and no trailer. `main` is an ancestor, so a fast-forward is possible.

## not_done

- **Full suite on `f2b8f98d`:** not run; it is the box's.
- **`rules_status` on the final commit:** not run.
- **`apply_check2_answers.py`:** not replayed. I compared its texts with the registry and the parsed differences with its declared edits.
- **The walk:** run through `tx_inhibit.judge` in memory only, not through `check_contracts.py`, which writes the reading.
- **The grounds of U14, Q14, Q24 and Q1:** named and compared, not judged as circuit matters. The INA226's sheet was not read.
- **The suite at `85ad1193`:** the local log's last lines only.
- **The streams' checks:** their findings were counted and compared, not re-verified.
