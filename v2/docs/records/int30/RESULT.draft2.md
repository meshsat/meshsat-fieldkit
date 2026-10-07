# Set 30: the result of the integration (DRAFT 2 of `RESULT.md`: the revisions bound, every commit after the reviewed revision classified, the equivalence, the gate lines left to the coordinator; MESHSAT-1357)

**Status: DRAFT for the coordinator**, the one writer of `records/int30/RESULT.md`, who adopts, corrects or discards it at promotion,
fills the gate lines and the INTEGRATED revision, and binds them. Written by the set 30 records-pack worker on branch `fnd/recpack`
from the candidate's integration commit 2a, `bbba3e53e396d3fe0f8ddd2f38d0c169bcc99c45`, on 6 October 2026 from 01:54 CEST. It
adopts the first draft of this section (branch fnd/int30rec at 7930ae68, file `records/int30/RESULT.draft.md` there; not in this
branch's history, so cited as text only) after its own read, and extends it to the candidate. It accepts nothing, closes nothing,
promotes nothing and changes no verdict. **Power-design closure: BLOCKED. Fabrication release: BLOCKED**
(`v2/docs/records/l9t5/l9t5_connected.out:4`; `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:883-884`). Desk-handover readiness is
the coordinator's assessment, kept apart from both (`v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:798`;
`v2/docs/EXECUTION-CONSTITUTION.md:23`). Prototype framing: nothing in the kit is built, bought, powered or measured.

**After this draft's base.** The coordinator's note of 01:56 CEST (`<worktrees>/_runs/claude/recpack/INBOX.md`): the candidate branch
has merged Slot H's set 31 record (`6fe398e9`, carrying `bca7b0dc`, `14082416` and `17ce29d5`), because the release suite on the
applied change list needs the page, the generator's data and the `test_l4e9` expectations that match it; the final integrated revision
is not yet known (the cascade regenerates again, a re-key follows). Citations stay at `bbba3e53`; the four commits are classified in
section 2 (rows S1 to S4), and where the merge changes a statement this draft cites, section 5 names it with the line at `6fe398e9`.

**What governs this page.** The owner's part 25 (`v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:844`): "Use the existing integration
gate to record the reviewed and integrated revisions and the intervening changes. If changes are only verified bindings or presentation,
record that equivalence. If they change a circuit, assumption, model, limit or substantive claim, the affected result needs targeted
verification before being credited. Passing the software suite alone cannot transfer an engineering verdict to altered claims." The
freeze order is the constitution's section 9 (`v2/docs/EXECUTION-CONSTITUTION.md:76`); the coordinator's runbook is outside the tree
(`<worktrees>/_runs/int30/PLAN.md`, sections 4 to 6).

**Citations and placeholders.** `path:N` (or `N-M`) is a line of that file at `bbba3e53` unless a revision is named; a bare `:N` is a
line of the path cited last before it; files outside the tree are named `<worktrees>/...` as text. `test_recpack.py` reads every such
path and line range at its revision, the quoted anchors on their lines and every commit named in a table. The literal placeholders
`__INTEGRATED__`, `__COMMIT2B__`, `__REKEY__`, `__GUARD_RECORD__`, `__GUARD_CHECK__`, `__PASSA__`, `__PASSB__`, `__RUNNER__`,
`__GATE__` and `__PROMO__` are the coordinator's to fill; this draft fills none of them.

## 1. The revisions

| Role | Revision | The check on it, as given | Source |
|---|---|---|---|
| REVIEWED: the one targeted recheck, cx46 | `4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e` | "P0 RECHECK: CORRECTIONS NOT CLOSED." | `v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:8` (base_commit), `:10` (summary) |
| EARLIER REVIEWED: the one focused check, cx45 | `06077cee85d0ed44c74c2a06c9fbb2030a0dedbc` | "P0 CANDIDATE: NOT CONFIRMED." | `v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md:10` (summary), `:20` (the HEAD it read) |
| THE P0 ROUND'S BASE: `fnd/p0base` | `e132db0e73da723cf18d32788aa8c9252c0bcfbe` | none of its own; cx45's JSON names it as its base_commit | `v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md:8` |
| THE FIRST DRAFT'S BASE (Slot D) | `1c6d56f5c4208349d382ecdb5c34ffaa4bb0037e` | none | its commit subject: "checkpoint of the disposition" |
| THE CANDIDATE, integration commit 2a: THIS DRAFT'S BASE | `bbba3e53e396d3fe0f8ddd2f38d0c169bcc99c45` | none: no check has read it | `v2/docs/records/l9t5/README.md:1` ("CANDIDATE READY 3: ac8efbca"); section 2 rows 12 to 18 |
| THE CANDIDATE BRANCH'S TIP at this writing: set 31 merged | `6fe398e9f624160429411e975c26564e553714d3` | none | section 2, rows S1 to S4 |
| COMMIT 2b: the integration's regeneration | `__COMMIT2B__` | none | section 3b |
| THE RE-KEY: record l4e7's results cache | `__REKEY__` | none | section 2, row P2 |
| INTEGRATED: the revision promoted | `__INTEGRATED__` | none; the suite's pass transfers no engineering verdict (part 25 above) | section 6 |

cx46's items, as given (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:114-204`): CLOSED BY THE CORRECTION 3, 11,
12, 15 (four); CLOSED AS CONDITIONAL 14, 16 (two); NOT CLOSED 1, 2, 4, 5, 6, 7, 8, 9, 10, 13, 17, 18 (twelve). The method ended there:
"Do not repeat this review method or relabel these tasks as qualification only." (`:206`). cx45's JSON field base_commit names
`e132db0e` (`v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md:8`) while its first check names the HEAD it read,
`06077cee` (`:20`); this draft takes `06077cee` as the earlier reviewed revision, as the first draft and the runbook do.

## 2. Every commit after the reviewed revision, classified from its diff

`git rev-list 4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e..bbba3e53` lists eighteen commits. Each was read with `git show --stat`, the diff of
every file it touches and, for a merge, `git show --remerge-diff`; the class comes from what the diff changes, never from the subject
line. Rows 1 to 11 are the first draft's (fnd/int30rec at 7930ae68, its section 2), adopted after this worker's read of each file list
and of the four merges' remerge diffs (none carries resolution content except row 9's heading, as the first draft says); their line
citations are re-pointed to `bbba3e53` (none of rows 1 to 11 moved). Rows 12 to 18 are this worker's. Rows S1 to S4 came after this
draft's base on the candidate branch (the set 31 merge). Rows M1 to M4 are on main and not in this history at `bbba3e53`; they enter
with the merge of main that the runbook's fast-forward needs. A citation at another revision is written `<sha>:path:N`. Rows P1 and P2 are the
coordinator's placeholders, written from his notes (`<worktrees>/_runs/int30/RESULT-classification.draft.md`, rows `__COMMIT2__` and
`__REKEY__`) and his diff read (`<worktrees>/_runs/int30/diffread-2b.txt`).

**In this history: (a) BINDINGS OR PRESENTATION 10; (b) SUBSTANTIVE CHANGE 8.** Of the eight (b) rows, rows 5 to 10 narrow claims (the
first draft's reading); rows 17 and 18 do NOT only narrow: they carry D-16 from OPEN to ADDRESSED IN DRAFTS into L4-E9's applied
generator data and its output (section 2, rows 17 and 18; section 5, item 7). Oldest first:

| # | Commit | Parents | What the diff touches | What it changes | Class | Equivalence (a) or verification owed (b) |
|---|---|---|---|---|---|---|
| 1 | `f67ba70065ef371f5c9895e81ce968940b1efab3` | `4d0ff8a2` | `v2/docs/records/l9t5/README.md`, line 1 only | the status line: "CANDIDATE 2 COMMITTED" becomes "CANDIDATE READY 2: 4d0ff8a2" | (a) a README line | no script, output or test touched: every output byte-identical to `4d0ff8a2` |
| 2 | `cd559d20ff20d4260bf7971a61e42dc22ddea4f7` | `b59e7cab` (main) | `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md` (+65: part 23's table row and text added, no line removed); three new records as received: `v2/docs/records/l4close/CHECK-V6-POWER-DRAFTS-7a82e82a-AS-RECEIVED.md`, `v2/docs/records/l4close/CHECK-CX44-F01-SELECTION-8c7c335f-AS-RECEIVED.md`, `v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md` | governing inputs and checks filed as received; no design source, generator, output, test or claim of the candidate | (a) inputs filed (cx46 item 1's smallest correction: "install the exact missing owner instructions", `v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:100`) | every output byte-identical; the files are new or appended |
| 3 | `0d5f855ea729ca3f3d7bf262e1450b539c43c9c2` | `cd559d20` (main) | the owner file (+132: parts 24 and 25, their table rows and text, no line removed); `v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md` (new) | as row 2 | (a) inputs filed | as row 2 |
| 4 | `1a4d3706775ca5cfb7ae017e8755777ef34e3510` | `f67ba700`, `0d5f855e` | the five files of rows 2 and 3 | a merge; `--remerge-diff` shows no resolution content | (a) a merge carrying only rows 2 and 3 | as rows 2 and 3 |
| 5 | `9cc6725d0684a4acd1d3094a554f3c6c5956a363` | `1a4d3706` | 23 files: `v2/docs/records/l9t5/l9t5_paloop.py`, `l9t5_f01.py`/`.out`, `l9t5_connected.py`/`.out`, `L9T5-CASES.md`, the pins of `l9t5_a1.out`, `l9t5_case.out`, `l9t5_drafts.out`, `l9t5_f01_drafts.out`, `l9t5_t10.out`; `v2/docs/records/l8r2/l8r2_dist.py`/`.out`, `l8r2_gndret.py`/`.out`, `l8r2_p0.py`/`.out`; `v2/ecad/tools/tests/test_l9t5.py`, `test_l8r2.py`; four new files in `v2/docs/records/l9t5/stability/` | MODEL: `cap()` gains Q551's held load on the reference (up to 4.4791 mA, release about 30.5 ms; `v2/docs/records/l9t5/l9t5_f01.out:103-108`), IB and C554's leakage at R553's top corner (the integrator's terms 2.1608 become 2.1609 mV), the PRINTED-rows band without the ASSUMPTION residual (6.3890 to 6.8942 A becomes 6.3888 to 6.8945 A, `:132-134`). LIMIT: B-PA1's pass limit 6.352 becomes 6.351 A, the floor rounded down (`:226`). CLAIMS: cx44 finding 3 from "CORRECTED WITH DESK EVIDENCE" to "STILL AN OPEN DESIGN DEFECT for the reference's loading (cx46)" (`v2/docs/records/l9t5/L9T5-CASES.md:51`); V6-B1 from "CORRECTED IN DRAFT" to "OPEN, REMAINING ENGINEERING" (`v2/docs/records/l8r2/l8r2_dist.out:125`); the connected verdict REMAINING ENGINEERING on seven fault rows read from cx46's JSON (`v2/docs/records/l9t5/l9t5_connected.out:319-340`); the worst-case margin row PROVISIONAL/OPEN (`:314`). PREDICATES changed or added in all three scripts; test expectations changed with them | (b) model, limit, claims and predicates | narrows: every claim change is a withdrawal or a downgrade, the limit is stricter. Unmoved: the MODEL band 6.3518 to 6.9259 A (`v2/docs/records/l9t5/l9t5_f01.out:132`), C-ALLTX rev 3 at 15.1308 V (`v2/docs/records/l9t5/L9T5-CASES.md:43`, `v2/docs/records/l9t5/l9t5_case.out:193`; `l9t5_case.out` changed in its paloop digest line only), the return study's solved figures. Owed before any credit: a targeted verification of the held-load term, the corner terms, the B-PA1 rounding and the new predicates |
| 6 | `4d1d02de9f23b628fd19cf6c6f2f4c1918d1b253` | `5cc9cb9d` (the solar author's branch; an ancestor of `4d0ff8a2`) | `v2/docs/records/l4e7/B2-PRESENCE.md`, `L4E7-P0SOL.md`, `README.md`, `SUPPLIER-P1-1-P0SOL.md`, `apply_gen_sch_e_p0sol_b2.py`, `l4e7_p0sol.py`/`.out`; `v2/ecad/tools/tests/test_l4e7.py` | CLAIMS: route B2 "UNSELECTED and WITHDRAWN AS DRAFTED" throughout, the owner item removed, P2 and P3 REMAINING ENGINEERING outside the baseline (`v2/docs/records/l4e7/B2-PRESENCE.md:1-6`, `:27-29`; `v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md:19-23`). The B2 draft's edits are unchanged: its docstring and the comment text it inserts changed, no part or net; the baseline composition `ORDER_E` has no B2 step (`v2/docs/records/l4e7/B2-PRESENCE.md:22-25`) | (b) claim | narrows. `l4e7_p0sol.out`: no decimal figure removed or added (section 3a). Owed: cx46 item 18 read on the new wording (no check has read `4d1d02de`); section 5 item 1 lists the B2 wording left elsewhere |
| 7 | `f973b646dcda188a4016de17d29b3a204d97506c` | `9cc6725d`, `4d1d02de` | the eight files of row 6 | a merge; `--remerge-diff` shows no resolution content | (b) by what it carries (row 6) | as row 6 |
| 8 | `6b768b1e9d8d130f9b541e65a1b48ce9d9a952a2` | `8d7be89c` (Slot C's branch; an ancestor of `4d0ff8a2`) | `v2/docs/records/l4e11/l4e11_power.py`/`.out`; `v2/docs/records/l8p/L8P-BREAKER.md`, `README.md`, `l8p_c4.py`/`.out`; `v2/docs/records/l9t5/L9T5-CASES.md`, `T10-ROUND5.md`, `apply_hw_fw_contract_t10.py`, `l9t5_t10.py`/`.out`; `v2/ecad/tools/tests/test_l8p.py`, `test_l9t5.py` | MODEL: the rail trip's averaging takes RL + RF (5.76 + 100 kOhm) in its charging path: 1.1 s becomes 1.17 s (`v2/docs/records/l9t5/l9t5_t10.out:578-579`) and the transient trip time 171 ms becomes 181 ms (`:634`), the Zth qualification point with it (`:640`); V-B23's response computed, 0.98 s MODEL (`:584-586`); cx46's periodic countermodel reproduced, 127.54 C (`:620`). CALCULATION ADDED: the delta's first-form allowance case, 50 uA cold and 180 uA tripped, executed on 28a's rows (`v2/docs/records/l4e11/l4e11_power.out:2119-2122`, `:2131`). CLAIMS: V-B23's "within 0.2 s" WITHDRAWN (`v2/docs/records/l9t5/apply_hw_fw_contract_t10.py:89`); the sustained thermal bound WITHDRAWN (`v2/docs/records/l9t5/l9t5_t10.out:620`); rev X's V-B20 admission route SUPERSEDED (`v2/docs/records/l9t5/T10-ROUND5.md:51`); C-PROT for the guard PROVISIONAL (`v2/docs/records/l8p/l8p_c4.out:273`, `:355`); FW-B22 PROVISIONAL, CON-004 OPEN (`v2/docs/records/l9t5/l9t5_t10.out:603-604`, `:662-663`). CONTRACT draft rows V-B22, V-B23 and FW-B20 reworded (`v2/docs/records/l9t5/apply_hw_fw_contract_t10.py:11`). IDENTIFIER L9T5-D9 renamed L9T5-D10 in `T10-ROUND5.md` | (b) model, calculation, claims, contract text | narrows, with two points to read first: (i) the Zth point moves from 171 to 181 ms at the same 105 C/W (a longer time reads a larger Zth, so the line is stricter; it is now labelled a measurement, not an acceptance, `v2/docs/records/l9t5/l9t5_t10.out:640`); (ii) the B7b sentence now reads "the B7b residual reads 120.0 C on rev V, inside 125 C (L9T5-D5 withdrawn, round 6)" (`:684`) where `4d0ff8a2` read "the B7b residual is tolerated by SESSION decision L9T5-D5" (that revision's line 655); the 120.0 C was already printed at `4d0ff8a2` (its lines 368 and 512, "holds"), so no new arithmetic, but it is a positive statement on a constant-current MODEL, the form cx46 finding 7 says bounds no periodic peak (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:90`). Owed before any credit: the RL + RF correction, the countermodel's reproduction, the allowance case's rows |
| 9 | `9cf3982a3b1203da90060d09df5ccfbff1151842` | `f973b646`, `6b768b1e` | the 13 files of row 8 | a merge; `--remerge-diff` shows one resolved conflict, `v2/docs/records/l9t5/L9T5-CASES.md`'s heading: "## 0g. Round 6 and its disposition (5 October 2026): T10 after the check cx45's Q3 and the recheck cx46" (the first parent's label 0g, the second parent's title; presentation) | (b) by what it carries (row 8) | as row 8; the resolution itself is a heading |
| 10 | `0b33a1f92fb87d39c7e40c1bc240b2e0311764c5` | `9cf3982a` | 22 files: `v2/docs/records/l9t5/l9t5_connected.py`/`.out`, `apply_l4e9_changelist_p0.py`, `README.md`, `v2/docs/records/l8r2/L8R2-KNOWN-DEFECTS.md`, `v2/docs/records/l8r2/README.md`, `v2/ecad/tools/tests/test_l9t5.py`; digest lines of eleven outputs; three new files in `v2/docs/records/l9t5/stability/` | CLAIMS and PREDICATES in the connected output: the trip's figure named a constant-current MODEL, "not a bound"; cx46's countermodel 127.54 C entered against 125 C (`v2/docs/records/l9t5/l9t5_connected.out:263-265`); the worst-case margin row PROVISIONAL/OPEN on it too (`:314-316`); the predicate "L9T5-F27 answered" added. Register-row draft texts R-242, R-244, R-245 narrowed in `v2/docs/records/l9t5/apply_l4e9_changelist_p0.py` (C-PROT "met on the desk" becomes "PROVISIONAL"; the sustained bound "WITHDRAWN after cx46"). V6-B1 OPEN on `v2/docs/records/l8r2/L8R2-KNOWN-DEFECTS.md:1087`. (a) parts in the same commit: digest lines only in `efuse_check.out`, `l4e7_p0sol.out` (one pin and its prose copy), `l9pwr_budget.out`, `l9stk_copper.out`, `l9stk_protection.out`, `l9t5_a1.out`, `l9t5_case.out`, `l9t5_cm5.out`, `l9t5_drafts.out`, `l9t5_f01.out`, `l9t5_t10.out`: one chain from `l4e11_power.out`'s new content (row 8; its digest `55180aec21d7bed0` becomes `40ca9c0311440ca0`) through l9stk, l9pwr, efuse and l9t5; the stability set `RUN-cr3-*` and `DIGESTS-cr3.txt` added | (b) claims and predicates, with (a) re-pins | narrows. The re-pins: digest lines only (section 3a). Owed: the connected predicates read by the targeted verification; the re-pins by the stability gate row of section 6 |
| 11 | `1c6d56f5c4208349d382ecdb5c34ffaa4bb0037e` | `0b33a1f9` | `v2/docs/records/l9t5/L9T5-CASES.md`, `README.md`, `l9t5_f01.py`/`.out` | the PRINTED-rows band's disclaimer reworded, "which is NOT a guaranteed band" becomes "which is NOT a bound on the cap" (`v2/docs/records/l9t5/l9t5_f01.out:134`): both deny that the band bounds the cap; no figure, predicate or computation changed. `L9T5-CASES.md` row 1 brought to the 6.351 A that row 5 set in the output (`v2/docs/records/l9t5/L9T5-CASES.md:49`); README line 1 | (a) presentation | no figure moved. Condition: the commit leaves two digest pins stale (section 3a); row 14 (`ac8efbca`) re-pinned both, digest lines only |
| 12 | `a1b68e75459766cfa79a082e63791744bec87d73` | `1c6d56f5` | `v2/docs/records/l4close/REMAINING-ENGINEERING.md` (new, 646 lines) | the remaining-engineering ledger's checkpoint: record text gathering filed verdicts; it "designs nothing, computes no new figure, consumes no review and changes no verdict" (`v2/docs/records/l4close/REMAINING-ENGINEERING.md:11-16`) | (a) record text, a new file | no script, output, predicate or existing test touched |
| 13 | `6d9ec491d0a178c0e163f5f8d0f041ec64f884b6` | `a1b68e75` | the ledger (+15, -12) and `v2/ecad/tools/tests/test_remeng.py` (new, 238 lines) | the ledger finished; a new test module over it (no existing expectation changed) | (a) record text and its new test | as row 12 |
| 14 | `ac8efbcabcf315d6bd58c8bebef3c048580e6fc1` | `1c6d56f5` | the l9t5 README line 1; two digest lines (`v2/docs/records/l9t5/l9t5_connected.out:21`, `v2/docs/records/l9t5/l9t5_f01_drafts.out:11`); `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` and `RUN-cr3-pass1.log`; one assertion of `test_l9t5.py` | BINDINGS: the two stale pins of row 11 re-pinned; the cr3 stability record retaken on candidate 3 ("started 22:26, pass 1 ended 22:36, pass 2 22:45", `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt:1`). PRESENTATION: the README's status line adds "a DRAFTED CANDIDATE, unchecked" and "L9T5-F13, F16 and F17 OPEN" for T10 (narrower words for states the T10 output already carries). TEST: the expected words follow row 11's reword (`v2/ecad/tools/tests/test_l9t5.py:956`) | (a) bindings, presentation and one test's expected words | no output figure, limit, model or predicate in the diff. The label and the limit the coordinator's notes name for this commit are in rows 11 and 5 (section 5, item 6) |
| 15 | `d5abed7cfd0228384445851864e3aa8afd324f6b` | `ac8efbca` | the l9t5 README, line 1 | "CANDIDATE 3 COMMITTED" becomes "CANDIDATE READY 3: ac8efbca" (`v2/docs/records/l9t5/README.md:1`) | (a) a README line | none touched |
| 16 | `3d2746c9bdd9a17ad81e19889892e5691973eb63` | `d5abed7c`, `6d9ec491` | the two files of rows 12 and 13 | a merge; `--remerge-diff` empty | (a) a merge carrying rows 12 and 13 (record text and its new test) | as rows 12 and 13 |
| 17 | `7070f1060a69735632338d39d744d3340ce75568` | `3d2746c9` | `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md` (+32), `L4-POWER-ARCHITECTURE.md` (161 lines), `l4e9_power_path.py` (91 lines) | APPLIED, verbatim from the draft that was in the reviewed `4d0ff8a2` (`git show 4d0ff8a2:v2/docs/records/l9t5/apply_l4e9_changelist_p0.py`, its PY_EDITS at line 47): register rows R-220 to R-245, no R-241 (`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:314-338`); the page's P0 note and change-list table (`v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:422`); in the generator's DATA, D-10's state (`v2/docs/records/l4e9/l4e9_power_path.py:4288-4296`), D-16's state from "OPEN (a DEMONSTRATED DEFECT ...)" to "ADDRESSED IN DRAFTS: CORRECTED in draft by P0-7 (R-240 ...)" (`:4391-4394`), the next actions of D-10 and D-16 (`:5630`, `:5635`), the change order and its constraints, and the WITHDRAWN state for FAN_OK's rows (`:5614`). CLERICAL: the applied R-240 row names D-10's item E-1, "its later validation step is S1" (`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:334`) | (b) claim (the states of D-10 and D-16 in the generator's data), with (a) rows and table | NOT only a narrowing: D-10's text restates the defect as E-1; D-16's moves from OPEN to ADDRESSED IN DRAFTS, PROVISIONAL on S3. Its basis is cx45's Q6 ("U5's residual internal-amplifier output is properly PROVISIONAL on S3", `v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md:105`) on a P0-7 draft unchanged since `06077cee`. Owed before credit: the targeted verification of the applied D-10 and D-16 texts against cx45's Q6 and cx46's P0-7 sentence; B2's "an owner item" in the applied D-10 text (section 5, item 1) |
| 18 | `bbba3e53e396d3fe0f8ddd2f38d0c169bcc99c45` | `7070f106` | `l4e9_power_path.py` (16 lines), `l4e9_power_path.out` (228 lines), `v2/docs/records/l9t5/apply_l4e9_changelist_p0.py` (37 lines) | BINDINGS: L4-E9's pins of l4e10's, l4e11's and l4e12's outputs, l4e11's page, TI-QUESTIONS.md and the charger draft (`v2/docs/records/l4e9/l4e9_power_path.py:112`, `:122-123`, `:125`, `:155`, `:162`). TOOL: the D-10/D-16 citation check reads L4-E7's P0 output too (`:180`, `:2418`); the applier's applied-state reader, `--write` still refusing twice (`v2/docs/records/l9t5/apply_l4e9_changelist_p0.py:107`, `:160`). OUTPUT: `l4e9_power_path.out` regenerated, 15 digest lines and 214 other lines: the register 209 to 234 items, the change list 92 to 117 changes, D-10's and D-16's texts, and "17, 2 open; 5 addressed in drafts (D-11, D-13, D-14, D-16, D-15 ...)" (`v2/docs/records/l4e9/l4e9_power_path.out:572`) where `7070f106` read "17, 3 open; 4 addressed in drafts"; "criterion 2 CONDITIONAL with 2 defects open" (`:1017`) | (b) by what its output carries (row 17's applied states), with (a) re-pins and two tool corrections | the output's criterion 2 count moves (3 open to 2 open): owed with row 17. The citation check's source set widens by the output the applied D-10 text cites (its refusal of 83.48 V: `<worktrees>/_runs/int30/integrate6-0054.log:16`); a figure is still refused unless one of L4-E7's outputs prints it. Four of the new pins name bytes that only commit 2b carries (section 3b) |

**Totals in this history:** (a) 10: rows 1, 2, 3, 4, 11, 12, 13, 14, 15, 16. (b) 8: rows 5, 6, 7, 8, 9, 10, 17, 18 (rows 7 and 9 are merges
carrying rows 6 and 8).

**Outside this history at `bbba3e53`, and the placeholders.** After the base, on the candidate branch: (b) 4, rows S1 to S4. On main:
(a) 4, rows M1 to M4. Placeholders: rows P1 and P2.

| # | Commit | Parents | What the diff touches | What it changes | Class | Equivalence or verification owed |
|---|---|---|---|---|---|---|
| S1 | `bca7b0dc293f7b778caf24239a6a8624a1028bd1` | `bbba3e53` | `v2/docs/records/l4e9/l4e9_power_path.py` (+61, -64) | the generator's data: D-10, D-16 and D-17 restated from the two set 30 drafts (the section 8 restatement on fnd/l4e9s8 at f47d1fc4, the page consistency draft on fnd/l4e9pc at 8282895e; both outside this history) | (b) claims | the record classes its D-10, D-16, D-17 change "CLAIM CHANGE" and states that every claim change "narrows a claim or states an open state" (`6fe398e9:v2/docs/records/l4e9/SET31-CHANGES.md:33`, `6fe398e9:v2/docs/records/l4e9/SET31-CHANGES.md:16`); owed: the targeted verification of the restated states |
| S2 | `140824161161eb3e3b09c324d06b8f297746744c` | `bca7b0dc` | `DOWNSTREAM-REGISTER.md` (59 lines), `l4e9_power_path.py` (399 lines) | the gate, the classes, blocks 8e to 8g and the register restated from the two drafts; page and output not yet regenerated (its subject) | (b) claims | as S1; criterion 2 moves from CONDITIONAL to FAIL, the coordinator's verdict words (`6fe398e9:v2/docs/records/l4e9/SET31-CHANGES.md:32`): a narrowing |
| S3 | `17ce29d52ea5ac5844e2f988aa08d8317cef2dde` | `14082416` | the page (374 lines), the register (2), `SET31-CHANGES.md` (new, 136), `l4e9_power_path.out` (166), `l4e9_power_path.py` (58), `v2/ecad/tools/tests/test_l4e9.py` (54) | the page's section 8 with the coordinator's criteria words (1 CONDITIONAL, 2 FAIL, 3 PASS, 4 PASS, 5 CONDITIONAL); PC-01 to PC-16 applied; D-16 ADDRESSED IN DRAFTS throughout (`6fe398e9:v2/docs/records/l4e9/SET31-CHANGES.md:41`); route B2 with "no owner item" in the data (`:54`); R-246, board P's ideal diode, ADDED to the change list and its order (`:45`); the output regenerated against 2b's pinned outputs placed in its working tree only (`:20`); `test_l4e9`'s expectations changed, each with its basis (`:60`) | (b) claims, a change-list row, test expectations | narrows, except R-246: registering record l8p's round 4 draft in board P's round is not a narrowing; owed: its composition read in board P's round and l6r2's board P tables regenerated, with the targeted verification of the restated states. The changed test expectations: their bases are the record's (`:60`), not independently read here |
| S4 | `6fe398e9f624160429411e975c26564e553714d3` | `bbba3e53`, `17ce29d5` | the six files of S1 to S3 | a merge; `--remerge-diff` empty | (b) by what it carries (S1 to S3) | as S1 to S3; it resolves this draft's contradictions 1, 2 and 4 in L4-E9's files and opens item 9 (section 5) |
| M1 | `b0a67a45d6d21a8bf631f8c1b293e61b0e5a52b2` | `0d5f855e` (main) | the owner file only (+221: part 26's table row at line 26 and its text after line 860) | the owner's communications bootstrap instruction filed as received | (a) inputs filed | no design file; every line of the owner file after line 25 moves down by one once main is merged (part 25's binding rule from 844 to 845) |
| M2 | `989b30f35220b87352ae598fab1d4dce70b4e293` | `b0a67a45` (main) | `README.md` and 46 new files under `compact/` (another session, MESHSAT-1500) | the compact kit's folder; nothing under `v2/` | (a) UNRELATED | `git diff --stat b0a67a45 24708af3 -- v2` is empty; the suite runs over them (public hygiene) |
| M3 | `c0ec8b77ce594044e44766e127a1e166b7150e81` | `989b30f3` (main) | `README.md` | the README's top block and news table | (a) UNRELATED | as M2 |
| M4 | `24708af30f073988d9de1d608a1896eb65e6ec4e` | `c0ec8b77` (main) | three files under `compact/` | dashes written out | (a) UNRELATED | as M2 |
| P1 | `__COMMIT2B__` | the candidate | the 27 files of `<worktrees>/_runs/int30/changed-2b.txt` less the three h3 outputs restored to HEAD | the integration's regeneration: re-pins, line-number citations, the applied change list's composition order (section 3b) | (a), as the coordinator's notes give it, on the conditions of section 3b | section 3b; the non-digest lines to be listed at the coordinator's `__NONDIGEST__` |
| P2 | `__REKEY__` | P1 | `v2/docs/records/l4e7/l4e7_stage_settings.results.json` (KEY and parts) and `l4e7_stage_settings.out` | record l4e7's results cache re-keyed on the integrated tree, the output expected byte-identical | (a), as the coordinator's notes give it | the KEY mismatch that makes it necessary: "l4e7 KEY MISMATCH committed 1718dfe54e5373e0 now b813b670989a685d; parts moved: files" with "file v2/docs/records/l4e11/l4e11_power.out: 3a46198439d5 -> 1938c400d140" (`<worktrees>/_runs/int30/finish-0137.log:5-6`) |

## 3. The equivalence, output by output

### 3a. Rows 1 to 11 (`4d0ff8a2` against `1c6d56f5`; the first draft's section 3, adopted)

The first draft's bullets, adopted after this worker recounted the outputs (185 tracked at both revisions, 18 changed; at `bbba3e53`
185 tracked, and rows 12 to 18 change three more: `l4e9/l4e9_power_path.out`, `l9t5/l9t5_connected.out` and `l9t5/l9t5_f01_drafts.out`,
the last two by one digest line each). The figure-by-figure comparison was not re-run here. Its pins at `1c6d56f5` and its stability
reading are replaced by section 3b's at `bbba3e53`.

- **Outputs:** 185 tracked `.out` files under `v2/docs/records/` at both revisions; 167 byte-identical; 18 changed (`git diff --name-only`).
  Digest lines only (9): `efuse/efuse_check.out`, `l9pwr/l9pwr_budget.out`, `l9stk/l9stk_copper.out`, `l9stk/l9stk_protection.out`,
  `l9t5/l9t5_a1.out`, `l9t5/l9t5_case.out`, `l9t5/l9t5_cm5.out`, `l9t5/l9t5_drafts.out`, `l9t5/l9t5_f01_drafts.out`. Text or figures (9):
  `l4e11/l4e11_power.out`, `l4e7/l4e7_p0sol.out`, `l8p/l8p_c4.out`, `l8r2/l8r2_dist.out`, `l8r2/l8r2_gndret.out`, `l8r2/l8r2_p0.out`,
  `l9t5/l9t5_connected.out`, `l9t5/l9t5_f01.out`, `l9t5/l9t5_t10.out`. Method: every changed line of each diff read; a line carrying a
  16-hex or longer digest counted as a pin line.
- **Figures that moved** (each output's decimal figures compared as a multiset between the two revisions, digests removed; integers read
  from the diffs): `l4e11_power.out`, the earlier allowance case's rows (3.447, 5.222, 8.89 V; 0.505 V); `l8r2_dist.out`, the stand-in
  land's 7.2 mm pitch printed; `l9t5_connected.out`, the countermodel (0.50 A, 0.40 s, 1.50 s, 127.54 C, -2.5 K); `l9t5_f01.out`, the held
  load (4.4791 mA, 30.5 ms, 1.044 mV), the integrator (2.1608 to 2.1609 mV), the PRINTED-rows band (6.3890 to 6.8942 A becomes 6.3888 to
  6.8945 A) and B-PA1 (6.352 to 6.351 A); `l9t5_t10.out`, 1.1 to 1.17 s, 171 to 181 ms, V-B23's 0.98 s, the countermodel (0.3484 W,
  0.2122 A, 91.2 K/W, 127.54 C), VOS0's 0.1936 A, rev X's 0.2318 A route removed. `l4e7_p0sol.out`, `l8p_c4.out`, `l8r2_gndret.out` and
  `l8r2_p0.out` changed text only. No other decimal figure of any output moved.
- **No baseline circuit changed.** The scripts changed are calculators, page texts, the contract-row draft, the change-list draft and the
  out-of-baseline B2 draft (comment text only, row 6); no `apply_gen_sch_*` draft of the baseline composition and no generator changed
  (`git diff --name-only 4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e 1c6d56f5`). So the composed netlists of the baseline are the ones cx46
  read; this is an inference from the file list, the composition itself was not re-run here.

### 3b. Commit 2b, from the coordinator's diff read

Source: `<worktrees>/_runs/int30/diffread-2b.txt` (read 01:53 CEST, the working tree of the candidate against `bbba3e53`), 30 changed
files, "TOTAL non-digest changed lines: 94" (its line 76). Where the diff read shows only the first lines of a file ("... N more"),
this worker read the rest of that file's diff from the same working tree at 02:05 (files dated 01:56:48); a committed 2b may differ, and
the coordinator's `__NONDIGEST__` list governs. **The diff read predates the set 31 merge** (`6fe398e9`, 01:56): S3 changed L4-E9's
page, register and output again and added R-246 to board P's round, so the page's digest that l4e10 and l4e11 pin, l5pwr's line
numbers into the page, and l6r2's board P composition move again; S3's own record names those re-pins as owed at the freeze
(`6fe398e9:v2/docs/records/l4e9/SET31-CHANGES.md:118-119`). The statements below describe the 01:53 working tree on `bbba3e53` and
are to be read again on the committed 2b.

- **Digest lines only, 19 outputs:** `efuse/efuse_check.out` (4), `l4e10/l4e10_cell_thermal.out` (2), `l4e11/l4e11_power.out` (2),
  `l4e12/l4e12_thermal.out` (2), `l6pwr/l6pwr_parts.out` (6), `l7pwr/l7pwr_fans_th1.out` (6), `l8gnd/l8gnd_drafts.out` (4),
  `l8r2/l8r2_dist.out` (6), `l8r2/l8r2_p0.out` (2), `l9pwr/l9pwr_budget.out` (12), `l9stk/l9stk_copper.out` (4),
  `l9stk/l9stk_protection.out` (4), `l9t5/l9t5_a1.out` (2), `l9t5/l9t5_case.out` (2), `l9t5/l9t5_cm5.out` (2),
  `l9t5/l9t5_connected.out` (26), `l9t5/l9t5_drafts.out` (6), `l9t5/l9t5_f01.out` (4), `l9t5/l9t5_t10.out` (6). The chain: row 17
  changed L4-E9's page (`bd315f4f375af0b1` at `bbba3e53`), which l4e10 and l4e11 pin; l4e11's output moves by its pin lines to
  `1938c400d1404eae`; its readers move by theirs.
- **Pins in three scripts (6 lines the diff read counts as other):** `l4e10_cell_thermal.py` (L4E9, the page), `l4e11_power.py`
  ("arch", the page), `l4e12_thermal.py` (L4E10_OUT), each from one 64-hex digest to another (diff read lines 20 to 30).
- **A digest's copy in prose (2 lines):** `l4e7/l4e7_p0sol.out` names l4e11's output at `1938c400d1404eae` where it read
  `40ca9c0311440ca0` (diff read lines 31 to 33).
- **Line-number citations (30 lines):** `l5pwr/l5pwr_contracts.out` quotes L4-E9's page and l4e11's output by line; the quoted words
  are unchanged and the line numbers follow the files: the page's quotes from 811 to 838 and from 593 to 620 (row 17 added 27 lines
  above them), l4e11's from 995, 997, 1036, 1048, 1055, 1057, 1059, 1061 and 498 to twelve lines later each (diff read lines 34 to 41
  and this worker's read).
- **The applied change list's composition order (42 lines):** `l8r2/l8r2_gndret.out` (28: board B's round renumbered, steps 60 to 66
  becoming 71 to 89 with R-228 to R-237, R-243 and R-245 inserted, diff read lines 57 to 64); `l8r2/l8r2_drafts.out` (2: board E's
  round as the page's table now gives it, lines 54 to 56); `l6r2/l6r2_passives.out` (12: the board A, B and D chains with the P0
  drafts, two "a pending draft names" lines, lines 43 to 50). No baseline draft or generator changes in 2b (the file list).
- **The three h3 scanner outputs restored to HEAD (14 of the 94 lines), and why.** `h3/public_check.out` prints the time it asked and the
  public repository's head ("An answer is true at the time printed on its first line, not later", `v2/docs/records/h3/public_check.py:14`);
  two runs differ, so the tool refuses it (round 2: "REFUSED, R3 the two runs differ", `<worktrees>/_runs/int30/integrate4-2352.log.targeted:34`).
  `h3/same_patches.out` prints the commit it ran against, "against HEAD (089f7f27)" becoming "(bbba3e53)" (diff read lines 17 to 18),
  so it changes with every commit. `h3/apply_rebinds.out` is the H3 pages' rebind finding of 27 September; regenerated, it reads today's
  registry (`6eb35694e300abff`, 127 bindings over 51 files, becoming `8c8e26858293d6f7`, 146 over 63) and drops its four self-test lines
  (diff read lines 3 to 8); why the self-test lines drop is not established here. All three are records of a past handover, outside P0's
  cascade; the coordinator's runbook keeps them as on main ("h3 dropped: its public_check prints the time it asked and never converges",
  `<worktrees>/_runs/int30/regen_targeted.sh:12`). Restoring them is a presentation choice; it leaves a stale reading of the current
  registry in the tree, named for the next set.
- **Finding for the coordinator (this worker's read, not the diff read):** the regenerated `l6r2_passives.out` gains the line "the other
  drafts alone: v2/docs/records/d8dec31/apply_gen_sch_d_ptt.py refused: apply_gen_sch_d_ptt: already applied (its marker is in the
  file)", because board D now lists `apply_gen_sch_d_ptt.py` both in its chain and as standalone ("chain apply_gen_sch_d_ptt.py,
  apply_gen_sch_d_paloop.py; standalone apply_gen_sch_d_ptt.py"). No figure moves, but that arm of board D's commutation check composes
  nothing; it is a refusal inside an output classed (a), to be listed at `__NONDIGEST__` or corrected.
- **Pins at `bbba3e53` (a reader over every `<16 hex> <path>` line of a records `.out` and every `("path", "<64 hex>")` pair of a records
  `.py`, held makers' sheets set aside, the commit-bound pins of `l4e11_power.py` lines 148, 3230 to 3232 and 3795 to 3796 set aside;
  no generator run):** fourteen stale, every one moved by 2b. Four are AHEAD of the tree: `v2/docs/records/l4e9/l4e9_power_path.py:112`,
  `:122`, `:125` and `:180` name l4e10's, l4e11's, l4e12's and L4-E7's P0 outputs at `aab5ae6b`, `1938c400`, `31883eca` and `28a5b9fd`,
  the bytes 2b carries (`<worktrees>/_runs/int30/integrate4-2352.log:12-16`, `<worktrees>/_runs/int30/integrate4-2352.log.targeted:10`), while the files at
  `bbba3e53` read `bbacc459`, `40ca9c03`, `3bdd5e3e` and `a343ccfe`. So `bbba3e53` alone is not a regenerable revision: its
  `l4e9_power_path.out` was regenerated in a working tree that already held 2b's outputs, and L4-E9's script would refuse on these pins
  at `bbba3e53` (inferred from its refusal form, `<worktrees>/_runs/int30/integrate4-2352.log.targeted:11`; not run here). Ten are
  behind: `v2/docs/records/l4e11/l4e11_power.py:120`, `v2/docs/records/l8gnd/l8gnd_drafts.out:15`, `:37`,
  `v2/docs/records/l8r2/l8r2_drafts.out:10`, `v2/docs/records/l8r2/l8r2_gndret.out:14`, `v2/docs/records/l9t5/l9t5_connected.out:10-13`
  and `v2/docs/records/l9t5/l9t5_drafts.out:60`. The equivalence of rows 17 and 18 holds only with 2b; the stability record is owed on
  the integrated revision (below).
- **Stability evidence in the tree at `bbba3e53`.** The cr3 record now covers candidate 3: its 18 outputs equal their pass-2 digests at
  `bbba3e53` (`v2/docs/records/l9t5/stability/DIGESTS-cr3.txt:4-21`, read file by file here), with `l9t5_f01.out` at `2aa78a957e497677`
  (`:15`); the reviewed revision's record is `v2/docs/records/l9t5/stability/RUN-4d0ff8a2-pass2.log:1-19`. The coordinator's two cascade
  passes on the integration tree read "already identical" for all 18 outputs in pass 2 (`<worktrees>/_runs/int30/integrate5-0025.log:28-47`,
  `<worktrees>/_runs/int30/integrate6b-0057.log:26-45`). cx46 item 14 reads "CLOSED AS CONDITIONAL" with the condition "retain or reproduce successful
  byte-identical repeated output runs on these inputs" (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:183`):
  met for `4d0ff8a2` and for candidate 3 by the files above; owed again on `__INTEGRATED__`, whose outputs 2b changes.

## 4. Pre-existing refusals (outputs unchanged; not set 30's)

From the coordinator's targeted passes on the integration tree (`<worktrees>/_runs/int30/integrate4-2352.log.targeted:4-9`, repeated in
rounds 2 and later): `h3/design_difference.py` "REFUSED, R1 run 1 exited 1"; `h3/handover_counts.py` "REFUSED, R4
v2/docs/reviews/REVIEW-A-LAYER-1-2026-09-27.md is pinned at 4c09af64cb214448 but is d469a268fe0b8768"; `h3/zip_size_estimate.py`
"REFUSED, R1 run 1 exited 3"; `l4close/verify_risks.py` "REFUSED, R1 run 1 exited 1"; `h3/public_check.py` "REFUSED, R3 the two runs
differ" (`:34`). The coordinator's notes record the same four on main `b0a67a45`, run there 00:03 to 00:07, and verify_risks' "item 5
DIFFERS" since 2 October (`<worktrees>/_runs/int30/RESULT-classification.draft.md:23`; no log of that run is in `<worktrees>/_runs/int30`).
Set 29's manifest declared four historical outputs unbound by path (`v2/docs/records/int29/RESULT.md:13`); set 30's list is the same four
(`<worktrees>/_runs/int30/allow-unbound.list`). Each is a record of a past handover or a known difference; none is in P0's cascade.

## 5. Contradictions met while reading (nothing edited; each for its writer through the coordinator)

1. **B2's wording, now in the APPLIED generator.** `v2/docs/records/l4e9/l4e9_power_path.py:4294` (D-10's applied state, row 17: "Route
   B2 (not a baseline row) is an unapproved PARTIAL interface proposal and an owner item"), printed at
   `v2/docs/records/l4e9/l4e9_power_path.out:600`; the draft it came from (`v2/docs/records/l9t5/apply_l4e9_changelist_p0.py:23`, `:47`);
   the comment at `v2/docs/records/l4e9/l4e9_power_path.py:6609-6610`; against `v2/docs/records/l4e7/B2-PRESENCE.md:4-6`, `:27-29`
   ("UNSELECTED and WITHDRAWN AS DRAFTED"; no owner action), `v2/docs/records/l9t5/l9t5_connected.out:359-360` ("no owner item") and the
   owner's part 25 (`v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:834-838`: "B2 need not remain an outstanding owner action").
   Also `v2/docs/records/l4e7/L4E7-P0SOL.md:99`'s heading "(a partial proposal)" against its own `:128-130`. cx46 item 18 asked for the
   withdrawal "throughout" (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:203`). **Changed by `6fe398e9` in
   L4-E9's generator:** D-10's data now reads "Route B2 (not a baseline row) is UNSELECTED and WITHDRAWN AS DRAFTED, with no protection
   credit and no owner item" (`6fe398e9:v2/docs/records/l4e9/l4e9_power_path.out:600`, the data at `6fe398e9:v2/docs/records/l4e9/l4e9_power_path.py:4243-4244`), and no "an owner item" or "the owner's
   item" is left in that file; the draft's texts (`v2/docs/records/l9t5/apply_l4e9_changelist_p0.py:23`, `:47`) and `L4E7-P0SOL.md:99`
   are unchanged (item 9).
2. **D-10's item name: resolved in the register by row 17.** The first draft's item 2 (R-240 calling D-10 "item S1") no longer holds:
   `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:334` reads "the receiving company's engineering item E-1 (its later validation step is
   S1 ...)". The page's decisions table still reads D-10 "ASSIGN to the supplier's phase 1, task P1-1"
   (`v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1278`) against the generator's applied next action, E-1
   (`v2/docs/records/l4e9/l4e9_power_path.py:5630`). **Changed by `6fe398e9`:** the page's table reads D-10 "ASSIGN to the receiving
   company's remaining engineering item E-1" (`6fe398e9:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1384`) and R-240 "item l4e7's
   E-1" (`6fe398e9:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:336`).
3. **T10's row in the connected output.** `v2/docs/records/l9t5/l9t5_connected.out:350-351` ("rev X on V-B20; the containment ...
   CORRECTED IN DRAFT, UNCHECKED") against `v2/docs/records/l9t5/l9t5_t10.out:645-647` (revision X HELD, round 5's route SUPERSEDED) and
   `:662` ("cx45's Q3 NOT CLOSED"). Unchanged since the first draft.
4. **Criterion 2's open-defect count, four readings.** The page: "three material defects are open"
   (`v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:967`), "none open since the update round" (`:975-976`), "criterion 2 has no open
   defect" (`:979`). L4-E9's regenerated output, row 18: "constraint: three material defects are open: D-10's ... and D-16"
   (`v2/docs/records/l4e9/l4e9_power_path.out:560`) against "17, 2 open; 5 addressed in drafts" (`:572`) and "criterion 2 CONDITIONAL
   with 2 defects open" (`:1017`). The page still reads D-16 OPEN (`v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:840`, `:1283`) where the
   generator's data reads ADDRESSED IN DRAFTS (`v2/docs/records/l4e9/l4e9_power_path.py:4391-4394`). **Changed by `6fe398e9`:**
   criterion 2 reads "FAIL" with "two material defects are open: D-10 (E-1) and D-17 (RE-2)"
   (`6fe398e9:v2/docs/records/l4e9/l4e9_power_path.out:559-560`); the page names "Set 29's inconsistency, corrected in the text"
   (`6fe398e9:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1007`) and its decisions table reads D-16 "ADDRESSED IN DRAFTS"
   (`6fe398e9:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1389`). This draft did not re-read every place of the page at `6fe398e9`.
5. **L4-E9's rows in the connected output.** `v2/docs/records/l9t5/l9t5_connected.out:361-362` ("L4-E9's change-list rows: drafted ...;
   L4-E9's own output refuses on this tree at its L4-E11 pin") against row 17 (the rows applied, `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:314-338`;
   "117 changes; none APPLIED" to a generator, `v2/docs/records/l4e9/l4e9_power_path.out:1310`) and row 18 (L4-E9's output regenerated).
   2b moves this output's digest lines only (diff read line 72), so the sentence reaches the integrated revision unless its text changes.
6. **Row 14's class.** The coordinator's notes: "(b): narrows F01's claims (a label, a limit rounded down); no figure recomputed"
   (`<worktrees>/_runs/int30/RESULT-classification.draft.md:15`), against `ac8efbca`'s diff (row 14: no output figure, label or limit;
   the label is row 11's, `v2/docs/records/l9t5/l9t5_f01.out:134`, the limit row 5's, `:226`). This draft classes it (a); the coordinator
   decides.
7. **Rows 17 and 18 against the notes' "narrow or restate" and "(a)".** The notes call row 17's generator data "verbatim from the draft
   that was in the reviewed candidate 4d0ff8a2 and narrow or restate a state" (`<worktrees>/_runs/int30/RESULT-classification.draft.md:18`)
   and the regenerated outputs of commit 2 "digest lines only" (`:19`). The texts are verbatim (this worker counted each in the applier at
   `4d0ff8a2`, `1c6d56f5` and `bbba3e53`), but D-16's move from OPEN to ADDRESSED IN DRAFTS is not a narrowing, and row 18's
   `l4e9_power_path.out` carries 214 non-digest lines (`v2/docs/records/l4e9/l4e9_power_path.out:572`, `:600`, `:615`, `:1017`).
8. **The ledger's own list.** `v2/docs/records/l4close/REMAINING-ENGINEERING.md:619-639` names six more (A to F: one finding identifier
   for two findings, two figures for the return's upper bound, the stability condition, two MODEL readings each for V-B23's response and
   the countermodel's peak, the back-feed's placement, the P0 list's revision); not repeated here.
9. **The change-list draft's applied-state reader against the set 31 merge (a finding opened by `6fe398e9`; inferred, not run).** At
   `bbba3e53` the reader demands every added register row, every register edit and every script edit of the draft verbatim in the tree,
   and otherwise refuses "the register carries R-220 but the applied texts are not this draft's"
   (`v2/docs/records/l9t5/apply_l4e9_changelist_p0.py:117-121`). Set 31 restated several of those texts. This worker compared the
   draft's literal lists (read with `ast`) with the files at `6fe398e9`: 16 texts are no longer verbatim (9 of the added register rows,
   among them R-225, R-227, R-232 and R-236; the three register edits of R-210 to R-212; four script edits, among them D-10's and
   D-16's data); at `bbba3e53` none is missing. The connected script reads the change list through that draft
   (`v2/docs/records/l9t5/l9t5_connected.py:178`), so on `6fe398e9` its regeneration and `apply_l4e9_changelist_p0.py --check` are
   expected to refuse until the reader or the draft follows set 31. For the coordinator before the cascade runs again.

## 6. The gate lines (left to the coordinator; nothing here is filled)

| Gate | Expected source | Result | Measured duration |
|---|---|---|---|
| Record l4e7's cache re-key (row P2) | the box's re-key log; the re-keyed `v2/docs/records/l4e7/l4e7_stage_settings.results.json` and `.out` committed | `__REKEY__` | |
| Stability: the cascade twice, the second pass changing no byte, on `__INTEGRATED__` | `v2/docs/records/l9t5/stability/regen_cascade.sh` through `<worktrees>/_bin/regen_out.py`; its two logs | | |
| candidate_guard record | `v2/ecad/tools/candidate_guard.py record --out <worktrees>/_runs/candidates/__INTEGRATED__.json` | `__GUARD_RECORD__` | |
| candidate_guard check (runner) | `candidate_guard.py check --manifest <worktrees>/_runs/candidates/__INTEGRATED__.json --dir .` | `__GUARD_CHECK__` | |
| Pass A, the box, Python 3.12 | `<worktrees>/_runs/int30s1/suite-box.log` | `__PASSA__` | |
| Pass B, the box, Python 3.11 | `<worktrees>/_runs/int30s1/suite-box-py311.log` | `__PASSB__` | |
| Runner pass (`test_l4e7`) | `<worktrees>/_runs/int30s1/runner/suite-runner.log` | `__RUNNER__` | |
| suite_gate with G7 (identity, module coverage, 0 failed, 0 load errors, every skip explained, totals consistent) | `<worktrees>/_bin/suite_gate.py` over the three logs | `__GATE__` | |
| Promotion (fast-forward of main, push, mirror, candidate_guard check on main) | the runbook's section 5 | `__PROMO__` | |
| Targeted verification of the (b) rows 5, 6, 8, 10, 17, 18 and S1 to S3 before any credit (part 25) | the coordinator's choice of verifier; not the ended review method | owed | |

**Measured so far (`<worktrees>/_runs/int30/*.log`, CEST, the integration working tree; none is a gate line):**

| Step | From | To | Duration | Source |
|---|---|---|---|---|
| The record l4e7 re-key's first measurement on the suite4 box | 21:02 | 21:31 | 29 min | `<worktrees>/_runs/int30/PLAN.md:9` |
| The re-key trial on the suite4 box | 22:51 | 23:18 | 27 min | the coordinator's brief to this worker; no log in `<worktrees>/_runs/int30`; the watchdog reads suite4 ACTIVE from 22:50:02 to 23:30:02 (`<worktrees>/_runs/vast/watchdog.log:1751-1775`) |
| integrate3: every pair's first pass, STOPPED | 23:06:30 | 23:52:53 | 46 min 23 s | `<worktrees>/_runs/int30/integrate3-2306.log:1`, `:16` ("pass 1 covered the pairs up to l4e8 (alphabetical)") |
| integrate4: the L4 pin chain, its stability pass, targeted rounds 1 and 2, stopped | 23:52:53 | 00:24:29 | 31 min 36 s | `<worktrees>/_runs/int30/integrate4-2352.log:1`, `:28`; `<worktrees>/_runs/int30/integrate4-2352.log.targeted:1` (00:00:48) |
| integrate5: the applied-state reader, the cascade's two passes (pass 2 all identical), targeted passes, stopped | 00:25:14 | 00:54:14 | 29 min 0 s (the two cascade passes and step 1 before 00:45:31: 20 min 17 s) | `<worktrees>/_runs/int30/integrate5-0025.log:1`, `:49`; `<worktrees>/_runs/int30/integrate5-0025.log.targeted:1` |
| integrate6: L4-E9's stale pins, stopped for the D-10 citation fix | 00:54:43 | 00:56:36 | 1 min 53 s | `<worktrees>/_runs/int30/integrate6-0054.log:1`, `:16` |
| integrate6b: L4-E9 regenerated, the cascade's two passes (pass 2 all identical) | 00:57:54 | 01:18:19 | 20 min 25 s | `<worktrees>/_runs/int30/integrate6b-0057.log:1`; `<worktrees>/_runs/int30/integrate6b-0057.log.targeted:1` |
| integrate6b's targeted rounds, the KEY check and the affected tests | 01:18:19 | 01:53:09 | 34 min 50 s | `<worktrees>/_runs/int30/integrate6b-0057.log.targeted:1`; `<worktrees>/_runs/int30/finish-0137.log:1`, `:40` |

The affected tests at 01:53 on the uncommitted working tree, as printed: "tests: 346 passed, 16 failed, 0 skipped" (13 of `test_l4e9`,
two of `test_l8r2`, one of `test_l9t5`; `<worktrees>/_runs/int30/finish-0137.log:37`). That is the state before commit 2b, not a gate
result; the gate lines above decide.

## 7. What the promotion closes, and the five claims apart

**Promotion of set 30 closes no power item and releases nothing.** It promotes a DESK candidate, "not an accepted power design" (the
runbook, `<worktrees>/_runs/int30/PLAN.md:50`): the twelve findings cx46 left NOT CLOSED are carried as REMAINING ENGINEERING
(`v2/docs/records/l4close/REMAINING-ENGINEERING.md:85`), the connected verdict reads "THE CONNECTED ELECTRICAL VERDICT: REMAINING
ENGINEERING." (`v2/docs/records/l9t5/l9t5_connected.out:336`), and L4-E9's page reads "**Layer 4's power architecture closes: NO**"
(`v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:972`); after the set 31 merge, "**Layer 4's power architecture closes: NO**: on the set 30 candidate **the power-design closure gate is BLOCKED**" (`6fe398e9:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1005`). The P0 list's revision 3 is drafted beside this page
(`v2/docs/records/l4close/P0-POWER-LIST.rev3.draft2.md`).

| Claim (the constitution's section 2, `v2/docs/EXECUTION-CONSTITUTION.md:22-23`; set 29's form, `v2/docs/records/int29/RESULT.md:67-75`) | State after this set |
|---|---|
| Documents and editable artifacts of the merged rounds | on the candidate as drafts and records; the change-list rows applied to L4-E9's register, page and data (row 17), no drafted circuit change applied to a generator (`v2/docs/records/l4e9/l4e9_power_path.out:1310`) |
| Design reviewed and accepted | no: cx45 "P0 CANDIDATE: NOT CONFIRMED.", cx46 "P0 RECHECK: CORRECTIONS NOT CLOSED."; the (b) rows after `4d0ff8a2` read by no check |
| Circuit changes implemented | none: no board generator and no baseline draft changed after `4d0ff8a2`, through `6fe398e9` (`git diff --name-only 4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e bbba3e53`: the one draft that changed is B2's, out of the baseline, comment text only) |
| Physical qualification | none |
| Fabrication release | BLOCKED; the power-design closure gate BLOCKED |

Desk-handover readiness is the coordinator's assessment against the Layer 4 DESK gate, separate from all five
(`v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:788`).

## 8. Left out, and why

- The gate lines, the INTEGRATED sha, commit 2b's sha and the re-key's result: the coordinator's, at promotion (placeholders kept).
- Commit 2b's equivalence rests on the coordinator's diff read and this worker's read of three truncated files in the working tree; a
  committed 2b is read again by the coordinator (`__NONDIGEST__`).
- The first draft's figure-by-figure comparison of rows 1 to 11 (section 3a) is adopted, not re-run; of rows 12 to 18 only
  `l4e9_power_path.out` changes text beyond digest lines among the outputs (their diffs).
- No suite, gate, generator, candidate_guard or regen_out was run (this worker's brief); the pin reader and the line mapping used `git`
  and short read-only scripts in the session's scratch space, not committed.
- The owner's part 26 is on main (row M1) and not in this branch's history; it is cited as text only.
