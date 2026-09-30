# Re-check of the set 6 integration candidate at 85ad1193 (AI review), 28 September 2026

<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357). The checker wrote none of the candidate and did not write the first check; its scratch scripts are local (_scratch/chk-int7-2/). Its finding R-1 and its minor items are answered in CHECK-RESPONSE.md, second part. -->

# Fresh re-check of the set 6 integration candidate, `fnd/int7` at `85ad1193` (AI review), 28 September 2026

This is an AI review by a checker that wrote none of the candidate and did not write the first check. It is not a qualified engineering review and replaces none. Prototype design: no V2 board has been built, ordered or measured; everything below is a reading of files.

Checked 28 September 2026, 18:00 to 18:16 CEST, in `<worktrees>/int7` (read only; HEAD `85ad11933058003b084f1de8a99f99ef58f31653`; `git status` empty before and after; no file in the worktree carries a modification time after 18:00:50). Scratch scripts are in `<worktrees>/_scratch/chk-int7-2/`.

```
mergeable: no
```

One blocking finding, in registry text. B-2 and B-3 of the first check are answered. B-1 is answered for the QMX's row only. No reading, count, binding or page is wrong, and INCONCLUSIVE stands for CON-010. One apply script, a CLOSURE.md edit and a re-render answer it; no reading needs re-taking.

## blocking

**R-1, item A1 (first check B-1 a and b): CON-010's dependencies are still incomplete, and S-92's reworded sentence is false by the walk's own rows.**

- **Problem (a):** S-92 now says "this item is one of the two dependencies that remain; the other is S-93". The walk names more than two unstated figures behind the three undecided rows.
- **Problem (b):** the power amplifier's row (A power on J_PA) is undecided on three grounds, and S-93 and CON-010's corrected entry give one. The other two are named by no open or closed item (registry search for IGSS and for U14's pins: no line).
- **Problem (c):** the SA868's row is undecided on three grounds, and S-92 gives one.
- **Evidence, the walk's own text** (the candidate's `tx_inhibit.judge` on the candidate's six netlists, run on a scratch export of `85ad1193`, 1.0 s; it gives 18 pass, 0 failed, 7 undecided, equal to the filed readings A 2, B 4, D 1):

| Row | Grounds the walk names |
|---|---|
| J_PA | U14 (INA226) pins 8 and 9 on +13V8_PA and pin 10 on PA_OUT, "a pin of a part no class here reads" |
| J_PA | Q14, whose other pins sit on U13's drive, "no table here states that its drive is off with its enable" (S-93's subject) |
| J_PA | with U36's supply down, "D Q1 gate (2N7002 PA_EN): its sheet states IGSS at 25 C only" |
| J_HF | Q24 on U15's drive only (S-93's subject) |
| SA868 | "its maker states no input threshold for this pin" (S-92's subject) |
| SA868 | "D U2 pin 5: its maker states no input current for it" |
| SA868 | "D U13 pin 4: an open-drain output EMCON releases, whose off-state current while powered its sheet does not state" |

- **Evidence, the page the entry cites:** `v2/docs/feasibility/EMCON.md` line 185 (section 0a row 2) says the walk reads the PA "UNDECIDED on the LM5176's gate drive in shutdown and on board D's Q1 (4a)". Lines 78 and 1039 say the same. Row 3 (QMX) names the LM5176 alone.
- **Counter-example 1** (`walk_counter.py`): with the LM5176 ground taken away, as if S-93 were closed by any of its three conditions, J_HF reads PASS and J_PA stays UNDECIDED on U14 and on Q1. `inhibit_chain_a` would read 1 undecided of 9.
- **Counter-example 2** (`walk_counter_s92.py`): with a stated receive level on the SA868's pin (1.0, 2.0 or 2.5 V tried), the row stays UNDECIDED on U2 pin 5's input current and U13 pin 4's off-state current.
- **Consequence:** close S-92 and S-93 as their texts ask and re-take RF-002. The predicate still returns INCONCLUSIVE, and CON-010 stands INCONCLUSIVE with an empty `waits_on`. That is the state the first check's B-1 was raised to prevent.
- **Suggested answer:**
  - Name the remaining grounds in an item or items linked from CON-010.
  - Drop the count "two" from S-92.
  - Make each item close when its row reads decided at the re-take.
  - Correct the PA clause of CON-010's entry.
  - Let CLOSURE.md section 1's "(S-92, S-93)" and S-81's closing evidence follow.

## minor

| id | item | note |
|---|---|---|
| n1 | A2 | REQ-032's acceptance asks "in every state of the gates' own supplies" and is allocated to boards A and B. S-65 can move its PA and QMX rows as it can FEA-002's, and it does not wait on S-65. It stands FAIL and waits on S-94, so nothing false follows; the re-read should take S-65 in. |
| n2 | A2 | S-86's second half changes `pcb_energy_chain.yaml`. CFL-006 is bound to that file (`a09ca0293afd1f7c`) and FEA-005 to two packet documents S-86's first half edits. Their bindings go stale when S-86 is applied. REQ-015, REQ-018 and CHO-003 also rest on BAT-002 or PWR-003. I could not show a verdict of theirs moving. |
| n3 | A3 | `e28f91a6` also drew R51, the RAIL_SENSE divider's bottom leg (W4C-F1), on board C. CLOSURE.md section 1 does not list it. RESULT.txt attributes no moved reading to it. |
| n4 | m5 | S-81's closing evidence and CHECK-RESPONSE.md say the brief's wording "is S-91's list". S-91's text, the two H3 checks and errata g to m do not name it. With S-64 closed the wording is moot; drop the pointer or name it in S-91. |
| n5 | m1 | The registry says "the owner's review of the restart plan". The filed file's header says it is an outside reviewer's review that the owner pasted. |
| n6 | m7 | D-F3 exists on the unmerged `fnd/d8dec31` (lines 71 and 391) and names J_USB3. It asks for a clamp, a bulk capacitor and a ferrite, not the current limit S-61 asks for. The reason labels the work "applied after this integration" but names no branch or file, and says in the present tense that it "brings it under board D's hold". `pcb_board_holds.yaml` names neither S-61 nor J_USB3. |
| n7 | m10 | "252 gitignored readings": `pack-MANIFEST` holds 252 entries, of which 240 are verdict files and 12 are ERC reports and their provenance files. |
| n8 | D | CLOSURE.md sections 2 and 7 say streams d8dec31 and d6rel were "checked" mergeable on 28 September. Those results exist only in local scratch (`_scratch/chk-d8dec31/`, `_scratch/chk-d6rel/`); no tree holds them. |
| n9 | A1 | S-93's third closing condition, like S-92's second, is a bench reading on one built board. That is a sample, not a maker's bound. It lowers no requirement; the closure should say which it was. |
| n10 | m8, m9 | S-91's title and S-89's "four fixtures" reach `main` unchanged, each carried with its reason in CHECK-RESPONSE.md. |

## verified

- **A1:** CON-010 has `waits_on: [S-92, S-93]` and `evidence_result` INCONCLUSIVE; statement and acceptance equal `e224ea36`.
  - "cannot time" is gone from entry 35, the only entry changed of 37.
  - Predicate recomputed by me: `inhibit_chain_d` 7 pass, 0 failed, 1 undecided of 8; `inhibit_chain_a` 7, 0, 2 of 9; `safe_lines_d` and `safe_lines_a` PASS; none missing. Result INCONCLUSIVE.
  - S-93's citation stands: SNVSAI1D 7.4.1 reads "Shutdown: VCC off, No switching", and no line of the sheet gives an HDRV level in shutdown. `tx_inhibit.py` lines 3736 to 3739 carry the rule.
  - S-93's three conditions lower no requirement. The exception is R-1.
- **A2:** S-65 and S-86 carry no disposition. S-65 is in the `waits_on` of FEA-002 and REQ-030, S-86 in those of REQ-045 and FEA-004. `rules_status.py` line 810 declares `pcb_energy_chain.yaml` an input of `energy_chain.py`. The links land on records the items can move. Exceptions are n1 and n2.
- **A3:** every moved reading in CLOSURE.md carries the kind RESULT.txt section 5 gives it, and every tool of section 7 is in section 3.
  - `d5e12880` touched tools and tests only and is out of the circuit table.
  - `932cf9d7` changed declarations only: D2's order code, the intent entries, and header lines alone in board P's netlist.
  - `910da406`, `e28f91a6` and `c4ad8350` changed generators and are in section 1.
  - The eight rows of `tx_inhibit.py` and E5's FAIL from `block_contract.py` are stated as instrument and contract corrections. Exception is n3.
- **B, m1:** the review file exists, carries no em or en dash, holds amendment XH-04 at line 24, and CON-010's entry names it.
- **B, m2:** the loop counts a reading whose verdict is not PASS and does not fail as undecided (lines 136 to 137).
- **B, m3 and m4:** S-57 and REQ-077 are named. My count equals the record's: 54 open items linked by 96 links on 60 records, 11 disposed.
- **B, m5:** S-81 is closed by `commit e28f91a6`, which exists and is an ancestor. Its title carries "or S-64 closes before that issue". `inhibit_chain_c` reads PASS of 6, and 0 failed on all six boards. Exception is n4.
- **B, m6:** S-13 is disposed PROCUREMENT and CON-025 has no `waits_on`.
- **B, m7:** see n6.
- **B, m10:** the run records say what CLOSURE.md quotes: `a4b157f0`, 14:52:52 to 14:55:01 UTC, 110.7 s, exit 0, 90 tracked files. The filed manifest and list hash to the values in `pack-SHA256SUMS`.
- **B, m11:** 26 of the 90 tracked readings name `rules_lib.py`; all 90 are at version `a4b157f07618`.
- **B, m12:** `inhibit_chain_b` reads 16 pass, 0 failed, 4 undecided of 20. The three records name board B's reading (REQ-030 and REQ-032 entries 9, 13, 14; REQ-071 entry 6), wait on S-94 and read FAIL.
- **C:** the 16 changed files are the registry, the trace page, 13 files under `v2/docs/records/int7/` and the review file. No reading, tool, generator or other page moved.
  - CURRENT-EVIDENCE.md is byte-identical (`ff781ceffbb41d80`), and both bindings are unchanged.
  - Parsed registry differences, all named in CHECK-RESPONSE.md:
    - S-81 moved to closed; S-93 and S-94 added.
    - S-13, S-61, S-65, S-86 and S-92 changed.
    - Eight records changed in `waits_on` (CON-010 also in `evidence` and `history`).
  - No protected field differs from `main`.
  - CHECK.md equals the checker's own file plus a four-line filing header.
- **D:** all five validators exit 0 (16 documents, 0 out of date; 59 rules and 144 records, 0 errors). Tests: 3 and 71 passed, 0 failed.
  - Every open item is linked or disposed, none both.
  - No dash and no claim word in the nine new or changed registry texts, or in the 69 added lines.

## not_done

- **Full suite on `85ad1193`:** not run; it is the box's.
- **`rules_status` on the final commit:** not re-run. CHECK-RESPONSE.md's three runs in an isolated clone are not verified by me.
- **The walk:** run through `tx_inhibit.judge` only, not through `check_contracts.py`, which writes the reading. The tool and netlists are unchanged since `a4b157f0`.
- **The two counter-examples:** scratch patches of the tool that take one ground away. They show what stays undecided, not what a real closure would read.
- **The PA row's two other grounds:** not judged as circuit or instrument matters.
- **The 252 gitignored files:** read from the manifest only.
- **SC-67's voltages and S-91's 28 findings:** not recalculated or re-counted.
- **The d8dec31 and d6rel check results:** verdict lines read only.

---
Filing note (scrub, 30 September 2026, MESHSAT-1357): 2 paths in this check are written as neutral tokens (`<worktrees>`) under the owner's rule that public files carry no internal host names, user paths or addresses; `v2/docs/records/scrub/MAP.md` lists each by line and token class. No other byte of the check changed; the check as filed is in the repository's history at commit `8fec0733` and before.
