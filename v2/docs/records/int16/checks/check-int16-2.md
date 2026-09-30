mergeable: no

# Check 2 (narrow re-check) of integration set 15, `fnd/int16` at `4012429e` (MESHSAT-1357)

AI review, labelled as such: an independent check by a Claude session that did not build this integration. It is not a
qualified engineering review. 30 September 2026, 02:10 to 02:16 CEST (read from `date`). Scope: `git diff
845a4fd1..4012429e` against check 1's B1, B2 and minors. Everything below is what I read or ran myself, in a shared
clone `_scratch/chk-int16b` with `archives/int16-evidence-4012429e.tar` extracted (`git status` clean after extraction),
now removed. No commits to real branches, no pushes, no box.

`fnd/int16` = `4012429eabcf`, one commit on `845a4fd1`, 16 files.

## Blocking

**R1. S-125 now names a reading sha256 that is not the reading's.** The B1 fix re-took
`records/w5identc/readings/check-board-c-b874b744.json`: its table sha moved to `1f4c513c`, so the file now hashes to
`29840bee91216e59...`. That value is re-pinned in `apply_identities_c.py` and quoted in the w5identc README. S-125's
title in `pcb_requirements.yaml` (line 3610) still reads "(v2/docs/records/w5identc/readings/check-board-c-b874b744.json,
sha256 42ce2b3ea2c1a406)", and REQUIREMENTS-TRACE.md prints the same. This commit edited S-125's title (m6) and left
the sha. Check 1's B1 fix asked for it: "re-pin `READING_SHA256` (and S-125's sha if the reading moves)". No validator
catches it, because S-125's sha lives in a title, not in `evidence_bound_to`. Fix: one more guarded edit of that title
to `29840bee91216e59`, then `rules_render.py --requirements`. While there, "decision 59, ruled by
apply_decision_decoded.py" credits the ruling to a script, where decision 59's `ruled_by` is "SESSION under the owner's
ruling of 21 September 2026". "decision 59, written by apply_decision_decoded.py" would be exact.

## Minors

1. **`apply_check16_fixes.py` itself carries a literal U+2013.** It is the old text it matches: line 59, the TJ
   junction temperature row with its en dash. It is the only dash in the commit's added lines. It could be written with the same
   backslash u2013 escape it writes into `apply_docs_s122_r4.py`.
2. **README step 4 credits the wrong script.** `records/int16/README.md` step 4 says `apply_identities_c.py` recorded
   decision 59 and rebound CFL-016. Those were `apply_decision_decoded.py`; `apply_identities_c.py` opened S-125.
3. **S-125's title line is 195 characters long** (`pcb_requirements.yaml` line 3609), because the flexible edit
   replaced a folded span with one line. The YAML parses; this is cosmetic.

## Check 1's items

* **B1: answered.**
  * `build_table.py` now carries `held_back` and `fetch` into a PRINTED binding. The input JSON and the table gain both
    fields on exactly the three PANJIT bindings: the table diff is those 6 lines. The counts are unchanged (21 PRINTED,
    23 DECODED).
  * With the PANJIT sheet moved away, `tests/run.py identit` gives 64 passed, 0 failed, 0 skipped. `part_identities.py
    check --unfetched-ok` gives `HOLDS_WITH_UNREAD`, `unfetched_ok: true`, 0 problems, bindings READ 18, UNREAD 3,
    DECODED 23. Without the flag it still refuses the three as "held back from the public tree and not fetched on this
    host (v2/docs/records/int16/fetch_held_back.py)", which fails closed.
  * I restored the sheet; its sha256 is `92544a83`.
  * With the sheet present, the check gives READ 21, DECODED 23, 0 problems, and its reading is byte identical to the
    committed one. `build_table.py` re-run leaves the tree clean.
* **B2: answered.** A fresh `part_identities.py render` is byte identical to `BOARD-C-SELECTIONS.md`. The page names
  only `v2/vendor/power/held/panjit-ss2020fl-series.pdf`, marked "(held back)", and never the old path.
* **Replay.** On `845a4fd1`, `apply_panjit_held_w5identc.py`, then `apply_check16_fixes.py`, then `rules_render.py
  --requirements` reproduce every scripted file of `4012429e`. The only differences left are the hand-written files
  (the set README, the index rows, the two filed checks) and the two scripts themselves.
* **m1, m3, m4, m5, m7, m9: answered in `records/int16/README.md`**, and the text is true to check 1.
  * m3: `check-w5identc-3.md` is byte identical to the checker's report.
  * m4: I read the four far sheets from `c08f4d5a`. The Uniroyal CS03 sheet reads "© Uniroyal Electronics Global Co.,
    Ltd. All rights reserved"; the Arlitech, Fenghua and Murata text layers carry no rights or reproduction term. This
    agrees with the README's plan.
  * m7: recording it rather than editing is reasoned: `pcb_decisions.yaml` is bound by sha in CFL-016's reading.
* **m2: answered.** The index rows for `int16/` and `w5identc/` were added, and the `s122/` row now reads eight rounds,
  eight checks.
* **m6: answered, but R1.** The w5identc README carries the new reading and table shas, and S-125 names decision 59 as
  ruled. S-125's own sha was left stale (R1).
* **m8: answered.** `apply_docs_s122_r4.py` has no literal dash. Its parsed string still holds U+2013, and TI's LM5069
  sheet still prints that row with the en dash in pdftotext's text, so the assertion is unchanged at run time.
* **The filed check 1** (`records/int16/checks/check-int16-1.md`) differs from my report in exactly one phrase (line
  110, the trailer named in words). A filing note at its end says so, and says nothing else. The note is accurate.

## Also confirmed

* **Validators.** 0 errors on all five:
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings;
  * `rules_lib.py`: 59 rules, 0 errors, 0 warnings;
  * `rules_render.py --check`: 16 documents, 0 out of date;
  * `rules_render.py --requirements --check`: current;
  * `decisions_render.py --check`: rc 0.
* **Bindings.** All 128 `evidence_bound_to` bindings match their files.
* **Full render order.** `rules_render.py --requirements`, `rules_status.py` x3, `rules_render.py` x2: CURRENT-EVIDENCE.md
  reads `c9b98931` at every step and `git status` is clean. CON-010 and REQ-044 are both bound to
  `CURRENT-EVIDENCE.md@c9b98931fd7cb960`, with 0 warnings.
* **Tests.** `tests/run.py requirement close claims decisions identit`: 175 passed, 0 failed, 2 skipped (no pcbnew).
* **Text.** The added lines carry no host name or user path. The only paths are relative `_scratch/...` names inside the
  two filed checks, as the checkers wrote them. The only dash is minor 1.
* **Commit identity.** The commit is authored and committed by Kyriakos Papadopoulos <ncpjfuzl@mxmx.email>, with no
  trailer.
* **Box suite.** The box result (2303 passed, 0 failed, 3 skipped) is the coordinator's; I did not see it.

## Counts

Blocking 1 (R1, new in this commit). Minors 3. Check 1's items: B1 and B2 answered, minors 1 to 9 answered or recorded.
Replays: 2 scripts, byte identical. Test runs: 175/0/2 with the held files; 64/0/0 without PANJIT's sheet. Render order:
stable at `c9b98931`.
