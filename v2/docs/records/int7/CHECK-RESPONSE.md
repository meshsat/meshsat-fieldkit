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
