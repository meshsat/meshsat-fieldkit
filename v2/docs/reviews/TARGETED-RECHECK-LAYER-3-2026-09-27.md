# AI check (not a qualified engineering review)

## Narrow re-check of layer 3's re-baseline, 27 September 2026

MESHSAT-1357. **Commit checked: `2c12be91505bbb61d64b4ca6b969a5eb87314a80`**, branch `fnd/l3rb`, two commits on main
`ef144760`: `a54b793b` (S-80's wording fix, S-81 added) and `2c12be91` (the baseline). Not pushed. Read in its worktree
from 18:40 to 18:50 CEST. `git status` was clean before and after every check. Nothing in the tree was edited except
this record.

**Result: B-1 of `v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md`, left NOT_CLOSED by
`v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md` section 3, is CLOSED at `2c12be91`.**

Checker: one AI session. It wrote none of the lines checked, took no part in the fix or the baseline, and did not hold
any earlier check. This is an **AI check of named items only**:
- It is not a layer review and not a qualified engineering review.
- It stands in for no qualified review that the records require (D-09, SC-46, `v2/docs/reviews/REVIEW-ROUTES.md`).
- The design is a prototype. Nothing in this kit has been built, ordered, powered or measured.

**Scope (the workflow's brief).** Only these items:
1. B-1's finding is closed by the stated remedy:
   - CON-010's newest evidence entry reads FAIL, consistent with its `evidence_result` and `history`;
   - the header names `79963b3b`;
   - the trace page is re-rendered.
2. `baseline_state`, `baseline_reviews` and the closures of S-51, S-78 and S-80 are correct and name a commit on this
   branch.
3. The registry has no difference from `ef144760` beyond these.

Out of scope, and not judged:
- S-81's engineering content, beyond its being a stated addition;
- S-79 (the package);
- the pages that other layers own.

## 1. What was read

| File | At | sha256/16 |
|---|---|---|
| `v2/ecad/tools/pcb_requirements.yaml` | `ef144760` | `9a3aed63341c8eaa` |
| same | `a54b793b` | `c8fded5cb0a165d6` (as S-51, S-78 and S-80 state) |
| same | `2c12be91` | `0c87f065a2c9defd` |
| same | `3e4799eb` (the file the narrow verification read) | `58b77b5d15b2fc7d` |
| `v2/docs/REQUIREMENTS-TRACE.md` | `a54b793b` | `285612fedd4cf81d` (as stated) |
| same | `2c12be91` | `8896c5caeb246d30` |
| `v2/docs/CURRENT-EVIDENCE.md` | `ef144760` and `2c12be91` | `7a834fe55aea6ccd` (unchanged) |
| `v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md` | `ef144760`, `a54b793b`, `2c12be91` | `ae70b1a7811ecea1` |
| `v2/docs/records/l3rb/rebaseline_difference.py` and `.out` | `2c12be91` | sha256 as `v2/docs/records/README.md` lines 317 and 318 give them |
| `git show 79963b3b` (message and registry diff) | | |

**Checks run.** All were read-only. The scripts and outputs are in the session scratch `rv-l3rb/` and are not filed.
1. **An independent entry-by-entry comparison** of the registry (`cmp.py`, `cmp2.py`).
   - Commits compared: `ef144760` to `a54b793b`, `a54b793b` to `2c12be91`, `ef144760` to `2c12be91`, and `3e4799eb` to
     `2c12be91`.
   - What it covers: every top-level key; every id-keyed section (needs, owner rulings, session choices, open items,
     closed items, records) field by field; list fields element by element; and the YAML comment lines, diffed apart
     from the parse.
2. **CON-010's changed entry.** The old and new text were compared character by character, to find where they first
   differ.
3. **The closed entries against the open ones.** The titles of S-51, S-78 and S-80 in `closed_items` were compared
   with their open titles at `ef144760`.
4. **`79963b3b` in history.** It is an ancestor of the head. Its registry diff adds the CON-010 note that ends "it
   stays INCONCLUSIVE, on the file at 7a834fe55aea6ccd" and the REQ-044 note, both bound to `@7a834fe55aea6ccd`. Its
   message calls it the rebased form of `eb9f9030`.
5. **The validators, in `git archive` exports** of `a54b793b` and `2c12be91`. `rules_lib.py requirements` gave 144
   records and 0 errors at each commit, with 17 and 20 warnings. Every warning is "git cannot say here whether commit
   ... exists", which comes from the export, or "out/rule-audit is not in this tree". The three extra warnings at the
   head are the three `a54b793b` closures. `git cat-file -t a54b793b` in the worktree gives `commit`.
   `rules_render.py --requirements --check` reports the trace page current at both commits (rc 0).
6. **The fixer's `rebaseline_difference.py`**, re-run at the head. Its output is byte-identical to the committed
   `rebaseline_difference.out`, and it ends "ALL ASSERTIONS HOLD".
7. **sha256/16** of the four records named in `baseline_reviews`, at `ef144760`, `a54b793b` and `2c12be91`.

## 2. B-1's remedy, item by item

| Condition (narrow verification, section 3, "What closes it") | Result |
|---|---|
| (1) CON-010's entry 28 ends with the record's actual state: reasons unchanged, FAIL on W3T-F1, on the file at `7a834fe55aea6ccd` | **PASS.** Entry 28 of 29, 0-based (the newest), is the one that changed. Old and new share their first 929 characters, through "...its own reasons are unchanged and it stays". Old tail: "INCONCLUSIVE, on the file at 7a834fe55aea6ccd". New tail: "FAIL on W3T-F1 (S-64, EQ-25), on the file at 7a834fe55aea6ccd (corrected at the re-baseline of layer 3 on 27 September 2026, S-80: this entry had ended 'it stays INCONCLUSIVE', against the consolidated re-take's FAIL above)". This now agrees with the rest of the record: `evidence_result: FAIL`, `history` ending "so it reads FAIL", entry 26 (the re-take, INCONCLUSIVE to FAIL on W3T-F1) and entry 27 (FAIL). `evidence_bound_to` is unchanged. S-64 is the open item "Finding W3T-F1". ENGINEERING-QUESTIONS line 52 is EQ-25, "TX_INHIBIT_n's fail-safe level ... (W3T-F1)". Entry 25 still reads "stands INCONCLUSIVE on the file at 0cf3947848784ced", but it comes before the re-take, so it is history, not a contradiction. |
| (2) The header's difference paragraph names `79963b3b`'s re-take of the reviewed attempt's own CURRENT-EVIDENCE re-read on CON-010 and REQ-044 | **PASS.** The paragraph "THE TARGETED FIX OF LAYERS 1 AND 3" now lists, among the difference from the reviewed file, "79963b3b's re-take of the reviewed attempt's own re-read of v2/docs/CURRENT-EVIDENCE.md on CON-010 and REQ-044". It names both bindings (`@6351a72c7966c4b9` replaced by `@7a834fe55aea6ccd`) and says the clause was added by the re-baseline (S-80). This matches `git show 79963b3b`. On REQ-044 the note stays consistent: its newest entry ends "so it stays INCONCLUSIVE, on the file at 7a834fe55aea6ccd", and `evidence_result` is INCONCLUSIVE. |
| (3) The trace page is re-rendered | **PASS.** `REQUIREMENTS-TRACE.md` was re-rendered in both commits, and `--check` reports it current at each. At `2c12be91`: line 1976 (CON-010's newest evidence) ends "it stays FAIL on W3T-F1 (S-64, EQ-25) ... against the consolidated re-take's FAIL above)"; line 10 reads "Registry state **BASELINED at a54b793b**"; S-51, S-78 and S-80 have left the open-items table and appear under closed items; S-81 appears as open. No line of the page still ends "it stays INCONCLUSIVE, on the file at 7a834fe55aea6ccd" under a FAIL heading. The only such line, 2443, is REQ-044's, under "INCONCLUSIVE". |
| (4) `baseline_state` and S-51/S-78 handled as the reversal says, then re-baselined | **PASS, see section 3.** One difference from the letter of step (4): the baseline was written before this re-check, not in the commit that files it. The registry records that as the session's decision and keeps a reversal clause. This re-check finds nothing that would trigger the clause (section 5). |

## 3. The baseline and the closures

| Item | Result |
|---|---|
| `baseline_state` | "BASELINED at a54b793b". `a54b793b` is on `fnd/l3rb` (`git branch --contains`). Its registry is `c8fded5cb0a165d6`, which holds S-80's wording fix. Naming the content commit from the commit after it is the form B-1 allows. The previous check accepted the same form for `cecfd0f1`. **PASS** |
| `baseline_reviews` | Four entries: `REVIEW-B-LAYER-3-2026-09-27.md@7a6c679f446b1baa`, `REVIEW-LAYER-3-RELEASE-2026-09-27.md@1c3bc2d99f9efb51`, `REVIEW-LAYER-3-RELEASE-2-2026-09-27.md@cf8c73fb288be2fb` and `TARGETED-CHECK-LAYERS-1-3-2026-09-27.md@ae70b1a7811ecea1`. All four hashes match the files at `ef144760`, `a54b793b` and `2c12be91`. The comment above the list says each is an AI review or check, never a qualified review (SC-46), and that no re-check of S-80's edits is among them. **PASS** |
| S-51 closed | Moved from `open_items` to `closed_items` with `closed_by: commit a54b793b` and `closing_evidence` naming the registry at `a54b793b` by hash and the four records by hash. The title is kept, and only its last sentence ("Open until S-80 closes; ...") is dropped. **PASS** |
| S-78 closed | Same move, `closed_by: commit a54b793b`. The closing evidence names the header paragraph, CON-010's entry, `rebaseline_difference.out` and the trace page at `285612fedd4cf81d`, which is that file's hash at `a54b793b`. The title is kept, and only "Open until ... Layer 3 stays IN_PROGRESS." is dropped. **PASS** |
| S-80 closed | Same move, `closed_by: commit a54b793b`. The closing evidence quotes CON-010's new ending exactly as it is in the file, says step (4) was not held, and states the reopen rule. The title's "Open until" became "The fix it names, in". **PASS** |
| Form of the closed entries | Each has the keys `id`, `title`, `closed_by` and `closing_evidence`, as S-77 and the other commit closures do. No `status` or `class` key remains, which is also the existing form. **PASS** |

## 4. No other registry difference from `ef144760`

This re-check's own comparison finds the following, and nothing else.

**`ef144760` to `a54b793b`:**
- `open_items` S-81 added;
- `records` CON-010 `evidence` differs at index 28 of 29, and only there;
- 21 comment lines differ: 3 removed and 18 added. They are the "TARGETED FIX" paragraph's three rewritten lines, now
  ten lines, and the new "RE-BASELINE OF LAYER 3" paragraph.

**`a54b793b` to `2c12be91`:**
- `baseline_state` and `baseline_reviews` changed;
- `open_items` S-51, S-78 and S-80 removed, and `closed_items` S-51, S-78 and S-80 added;
- 27 comment lines differ: 2 removed and 25 added. They are the new "THE BASELINE, AGAIN" paragraph and the rewritten
  two-line comment above `baseline_reviews`, now three lines.

**`3e4799eb` to `2c12be91`:**
- All 144 records are present on both sides.
- The only record field that differs is CON-010's `evidence`.
- No protected field differs: kind, statement, acceptance, allocation, verification method or phase, prototype_1 and
  its basis or choice, `satisfied_by`, status, `evidence_result`, release effect, parent or candidate.
- Needs, owner rulings and session choices are equal.

These counts agree with the fixer's `.out`: "comment lines removed 3, added 18", then "removed 2, added 25". They also
agree with the header paragraph "THE BASELINE, AGAIN". Every changed comment line is in the stated paragraphs or in the
comment above `baseline_reviews`.

S-81 is an open item. By the header's own rule, open items move without a review of the baseline. Its figures and
citations match what they cite: EQ-25 is "RF-002 FAIL on current evidence on boards A to D", and S-64 is W3T-F1 at 1.09
V against 0.8 V. It is a stated addition, not an unstated difference.

**PASS.**

## 5. Observations (not findings; for the integrator)

- **This record is the re-check that S-80's step (4) names.** It is a check by a session that wrote neither edit, at one
  pinned commit. It finds neither edit short of the verification's section 3, and it finds no registry difference that
  the header paragraphs leave unstated. So the reversal clause in "THE BASELINE, AGAIN" is not triggered. Four places in
  the registry say this re-check was not held: that paragraph, the comment above `baseline_reviews`, and the closing
  evidence of S-51 and of S-80. If the integrator files this record, those places describe the state before it was
  filed. Adding this record to `baseline_reviews`, and a sentence to that effect, is the integrator's choice. It is a
  change to readings and notes, not to the baseline.
- **Cosmetic.** The header line "and this fix: the three gen_sch_b.py pointers ... (SC-58's :257 and :822, SC-63's
  :764-766)" is 137 characters long. The fixer's report says 133. The file already had 386 lines over 120 characters
  at `ef144760`.
- **Unchanged by design and outside this scope:** the fixer's "left for integrator" list. It covers the layer 3 line in
  LAYER-STATUS, EQ-28 and EQ-30, S-79's future-tense title, and EMCON.md sections 3 and 7 against 4b.
- The commit messages carry no co-author trailer, and both commits are authored by the owner's identity.

## 6. Result

| Item | Result |
|---|---|
| Layer 3 B-1 (after S-80's fix and the baseline) at `2c12be91` | **CLOSED** |
| B-1 remedy (1): CON-010's newest entry reads FAIL, consistent with `evidence_result` and `history` | PASS |
| B-1 remedy (2): the header names `79963b3b`'s re-take on CON-010 and REQ-044 | PASS |
| B-1 remedy (3): the trace page re-rendered and current | PASS |
| `baseline_state` "BASELINED at a54b793b", a commit on `fnd/l3rb` | PASS |
| `baseline_reviews`: four records, hashes match | PASS |
| S-51, S-78 and S-80 closed by `commit a54b793b`, with evidence | PASS |
| No registry difference from `ef144760` beyond the stated ones | PASS |
