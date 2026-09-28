# Answers to the fresh check of the set 6 integration (MESHSAT-1357, 28 September 2026)

The check (`CHECK.md`, an AI review) read the first candidate `fnd/int7` `1c4235ec` NOT mergeable on three findings, all in
text the integration wrote. Each is answered here by the integrating session, with the file that carries the answer.
No reading was re-taken for them (none of the answers changes a tool or a declaration). The corrected candidate is
suited and checked again before promotion.

## Blocking findings

| Finding | Answer | Where |
|---|---|---|
| B-1 (a) S-92 called itself "the dependency that remains" | reworded: one of the two that remain, the other being S-93 | `pcb_requirements.yaml` S-92, by `apply_check1_answers.py` |
| B-1 (b) CON-010's `waits_on` omitted board A's two undecided rows | **S-93 opened** (the LM5176's gate-drive level in shutdown, which TI does not state, behind the 30 W amplifier's and the QMX's rows); CON-010 waits on S-92 and S-93. INCONCLUSIVE stands, as the checker's own recomputation gives | the same |
| B-1 (c) the entry said the walk "cannot time" board A's rows | the clause is corrected in place to what the files say (UNDECIDED on the LM5176's unstated gate drive in shutdown, SNVSAI1D 7.4.1, EMCON.md section 0a rows 2 and 3). The entry was written by this integration and never reached `main`; the correction names the check | the same |
| B-2 S-65's disposition (CIRCUIT_ITEM) | withdrawn. EMCON.md names the fault "a registry open item" that reaches EMCON through U30 and U40, and FEA-002 asks the inhibit to hold in every state of the lines' own supplies: S-65 is linked from FEA-002 and REQ-030 | the same |
| B-2 S-86's disposition (PROCESS) | withdrawn. Its second half corrects `pcb_energy_chain.yaml` (F1's fuse figures), a declared configuration input of `energy_chain.py`: S-86 is linked from REQ-045 and FEA-004. Its first half (documents citing moved lines) rides with it | the same |
| B-3 CLOSURE.md did not separate the kinds | second edition: `d5e12880` is a contract correction (section 3), set 6's declaration changes are listed by commit with the readings they moved (section 2), and `tx_inhibit.py`'s and `block_contract.py`'s corrections are in section 3 with RESULT.txt's attribution (eight of board B's eleven failed RF-002 rows moved by the instrument) | `CLOSURE.md` |

## Minor items

| Item | Answer |
|---|---|
| m1 the owner's review cited by the registry was in no file | filed as `v2/docs/reviews/2026-09-28-restart-plan-review.md`; CON-010's entry names the file |
| m2 the first script tested `counts.undecided`, not the verdict | the predicate is recomputed verdict-aware in `apply_check1_answers.py` (a reading that is not PASS and does not fail is undecided) and gives the record's result, INCONCLUSIVE. `apply_con010_redecide.py` stays as the record of what ran |
| m3 S-57's closure and REQ-077's move not named | named in `CLOSURE.md` sections 1 and 5 |
| m4 "17 items linked from 28 records" | restated from the registry: 28 links on 24 distinct records then; after the answers 54 open items linked by 96 links on 60 records, all links counted (`CLOSURE.md` section 5) |
| m5 S-81's own closing condition was met | S-81 closed by commit `e28f91a6` with its evidence; the brief's wording stays on S-91's list |
| m6 S-13 to CON-025 was a weak link | the link is withdrawn; S-13 carries a PROCUREMENT disposition with its reason |
| m7 S-61 visible from no record or hold | its reason now names where it is carried: decision 31's review of board D (stream d8dec31, finding D-F3 on J_USB3), under board D's hold |
| m8 S-91's title reads as if `H3-RESPONSE.md` exists | carried: the page is the next documentation task after this promotion. Of S-91's list this integration did two (the renderer's sentence, `b3d66c70`; CON-010's link, `a4b157f0` and the answers above); the page will say so |
| m9 S-89 says "four fixtures" where the review ran four cases, two with a false PASS | carried to S-89's closure, which stream d6rel's integration writes from the matrix as re-run (PASS, FAIL, FAIL, INCONCLUSIVE on the repaired tool; 2 of 4 as wanted on the old) |
| m10 no run record of the 28 September re-take in the tree | filed under `box/`: `retake-run.txt`, `retake.log`, `other-writers.log`, the pack's checksums, manifest and list, the two driver scripts, and the suite's summary at `1c4235ec` |
| m11 only 26 of the 90 readings name `rules_lib.py` | `CLOSURE.md` section 3 says so; the re-take re-wrote all 90 because the driver re-takes every schematic-phase reading |
| m12 REQ-030, REQ-032 and REQ-071 stand FAIL on a ground that now reads 0 failed | **S-94 opened** and linked from the three records; they are not re-decided here (each rests on EMCON.md's rows as well), and FAIL is the cautious reading until they are |

## What the check could not do, answered

- The suite at `1c4235ec`: the log's last line is the commit it ran on (`box/suite-1c4235ec.txt` quotes it with the log's sha256). The corrected candidate gets its own run.
- `rules_status` on the final commit: run three times in an isolated clone of the exact commit with the one evidence archive installed; the pages reproduced byte for byte (recorded in the checkpoint). Repeated for the corrected candidate.

# Second part: answers to the re-check (`CHECK-2.md`, an AI review, 28 September 2026)

The re-check read the corrected candidate `85ad1193` NOT mergeable on one finding, R-1, and confirmed B-2 and B-3 of the
first check answered. It was the second failure on the same point (CON-010's dependency items), so the method changed
before the third candidate: the items are no longer written from a summary of the readings, which carry one line per
undecided row, but from the walk's own report, which carries every ground, and a script asserts the coverage.

## Blocking finding

| Finding | Answer | Where |
|---|---|---|
| R-1 (a) S-92 said "one of the two dependencies that remain" | S-92 is rewritten: it is the SA868 exciter's row with its three grounds, and says that what remains for CON-010 is this row and board A's two rows (S-93). No count of dependencies is typed | `pcb_requirements.yaml` S-92, by `apply_check2_answers.py` |
| R-1 (b) the amplifier's row is undecided on three grounds and S-93 gave one | S-93 is rewritten to the QMX's row (one ground: Q24 on U15's drive) and the amplifier's row (three: Q14 on U13's drive; U14, the INA226, whose pins no class of the walk reads; board D's Q1 on PA_EN with U36's supply down, IGSS stated at 25 C only) | the same |
| R-1 (c) the SA868's row is undecided on three grounds and S-92 gave one | S-92 names all three (no input threshold and no input current stated for U2 pin 5; the off-state current of the released open-drain output U13 pin 4) | the same |
| R-1, the consequence (closing the items as worded would leave CON-010 INCONCLUSIVE with nothing to wait on) | each item now closes when RF-002, re-taken, reads its row DECIDED, whichever way each ground is answered; and `apply_check2_answers.py` refuses to write unless every part the walk's undecided grounds name, for every undecided row on CON-010's allocated boards, is named in an item CON-010 waits on (`walk_grounds.py` gives the parts: U2, U13; Q1, Q14, U13, U14, U36; Q24, U15) | `walk_grounds.py`, `walk-grounds.txt`, `apply_check2_answers.py` |
| R-1, CON-010's entry and CLOSURE.md | the entry's clause names every ground per row and cites `walk-grounds.txt`; CLOSURE.md sections 5 and 6 follow | `pcb_requirements.yaml` CON-010, `CLOSURE.md` |

## Minor items

| Item | Answer |
|---|---|
| n1 REQ-032 should take S-65 in | REQ-032 waits on S-65 |
| n2 CFL-006 and FEA-005 are bound to files S-86 changes | both wait on S-86. REQ-015, REQ-018 and CHO-003, which rest on the same rules, are not linked: the checker could not show a verdict of theirs moving and neither can this session; their rules' readings are owed again when the file changes, which `rules_status` reports by itself |
| n3 R51 not listed | listed in CLOSURE.md section 1 with the re-take's attribution (no moved reading) |
| n4 S-81's closing evidence pointed at S-91's list | the pointer is gone: with S-64 closed the wording is moot |
| n5 "the owner's review" is an outside reviewer's, pasted by the owner | CON-010's entry says so. The same words in a comment of `rules_lib.py` and in a test's docstring stay as they are: changing `rules_lib.py` again would change the code bundle of 26 readings for a comment. Carried to the next change of that file |
| n6 S-61's reason | rewritten: it names the unmerged branch and file, says what finding D-F3 asks for (a clamp, a bulk capacitor and a ferrite, not this current limit) and that nothing but S-61 carries the current limit until that review is on `main` |
| n7 "252 gitignored readings" | CLOSURE.md says 252 files: 240 verdict files and 12 ERC reports with their provenance files |
| n8 the streams' check results were in no tree | filed under `checks/` with a table of branch, commit and verdict |
| n9 a bench reading on one built board is a sample | S-92 and S-93 say so in their closing conditions: it is recorded as a sample of one board |
| n10 S-91's title and S-89's "four fixtures" | carried as the first part says (m8, m9) |

# Third part: answers to the third check (`CHECK-3.md`, an AI review, 28 September 2026)

The third check read the candidate `f2b8f98d` mergeable with no blocking finding; `main` was fast-forwarded to it. Its
thirteen minor items are answered here. Those that need a registry edit are carried to the next integration set, because
a registry edit after the check would make the promoted revision another than the checked one.

| Item | Answer |
|---|---|
| p1 `walk_grounds.py` reads the four netlists `inhibit_chain_d` records; `inhibit_chain_a` records five | carried to the script's next use: it will read every filed reading's netlists and refuse a disagreement. The checker's own run on the five gave the same seven rows and identical reports |
| p2 the coverage assertion is a necessary condition only, by designator and without the board | accepted as the script's stated limit: it guards against a ground left out, not against a ground misstated. The prose of S-92 and S-93 was read ground by ground by the checker and carries each ground's substance |
| p3 `tx_inhibit.py` prints at most three unsure grounds per state | carried as a tool item for the next registry edit: the walk's report is to print every ground or say how many it cut. On these netlists the longest list is 2, so nothing was cut; an item closes on its row reading decided, which covers a cut ground |
| p4 S-92's 2.86 V is the walk's adverse level, the chain line's 3.12 V the nominal | carried to S-92's next edit: it will name both and say which is which |
| p5 bench E-01 names pin 5's threshold and current, not U13 pin 4's off-state current | carried to S-92's next edit and to EMCON.md's writer: the bench row gains the third ground or the item names another bench row |
| p6 the grounds of Q14 and Q24 are half the instrument's and half a maker's unstated figure | S-93 states both halves; its closing route is reworded at its next edit so that "the instrument's own" is said of the first half only |
| p7 FEA-002 does not wait on S-92 or S-93, and EMCON.md does not show U14 or U13 pin 4's off-state current | carried to the next registry edit, with S-94's re-read of REQ-030, REQ-032 and REQ-071: FEA-002 will wait on S-92 and S-93, and EMCON.md's writer gets the two grounds the page does not show |
| p8 the words "the owner's review" remain in a comment of `rules_lib.py` and in a test's docstring | carried to the next change of `rules_lib.py`, as the second part says; the test's docstring goes with it |
| p9 "12 ERC reports with their provenance files" | corrected in CLOSURE.md: 6 ERC reports and their 6 provenance files |
| p10 the d6rel row of `checks/README.md` did not carry the checker's condition | the row carries it, and says the integrator took the condition as binding |
| p11 six new files cite scratch folders by the runner's absolute path | accepted as a limit of these records: the scratch folders are the checkers' working files and are not part of the repository; each record states what was run and what it read. The paths are kept so that the session that holds them can find them |
| p12 no record of the suite at `85ad1193` in the tree | filed: `box/suite-85ad1193.txt`, and `box/suite-f2b8f98d.txt` for the promoted candidate |
| p13 the first part's "96 links" against CLOSURE.md's 99 | the first part is the second candidate's record and is left as written; the current figures are CLOSURE.md section 5's: 54 open items linked by 99 links on 60 records, 11 disposed |
