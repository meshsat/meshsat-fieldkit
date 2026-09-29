mergeable: no

# AI review: re-check of integration set 14, fnd/int15 at 097d2517 (MESHSAT-1357)

This is an AI review, not a qualified engineering review. I did not write the work under check; the first check
(`CHECK.md`, filed as `records/int15/checks/check-int15-1.md`) is mine. Checked 29 September 2026 from 20:14 to 20:23
CEST (times read with `date`). Everything below is what I read or ran myself.

**Set up**
* `fnd/int15` is `097d2517836b3ae31d057d44fbe4ceb62307b505`, one commit on `9eaf406f`, still the tip at 20:22.
  `1f3dd306` is not an ancestor, and no local or remote tracking branch contains it.
* Tip clone: `<scratch>/chk-int15`, moved to `097d2517`. Archive `int15-evidence-097d2517.tar` installed: sha256
  `7c2cf6038d96cd59...`, 939 files, the same file list as before, none of them tracked.
* Main clone: `<scratch>/chk-int15-base` at `b874b744`, unchanged since the first check.
* Throwaway clones in my session scratchpad: `c15/r4` at `9eaf406f` (the replay) and `c15/r5` at `097d2517` (the
  closure test). Neither was committed to.
* Every tool ran from a scratch cwd (`env -C`) with `VERDICT_DIR` in the scratchpad. `git status` of the tip clone
  shows only my two reports. No commit, no push, no agent, no other model, no box. The full suite was not run.

**Counts: 1 blocking, 6 minor.** B2 of the first check is answered. B1 is carried into S-122, but S-122 can still
close without it (B1 below).

## Blocking items

**B1. S-122 can close today without the part number inventory and without the five sentences.**

1. **The closure tool reads none of the extension.**
   * `records/s122/close_s122.py` is unchanged (`records/s122/` is identical at `9eaf406f` and `097d2517`).
   * I ran it on `r5` at `097d2517` with the check already filed there:
     `close_s122.py v2/docs/records/s122/checks/check-s122-3.md`.
   * It printed "S-122 closed at 097d2517; CFL-016 reads PASS (was FAIL); 862 sentences, 0 STALE, 0 UNJUDGED".
     Afterwards `rules_lib.py requirements` read 0 errors and 0 warnings.
   * That is the dropped closure of `1f3dd306`, repeated on the same check.
   * Its gates (lines 61 to 91) ask:
     * the rebinds, and bindings that are current (the three new ones are);
     * a re-run of the unchanged inventory and verdicts, which still read no part numbers;
     * CFL-016's baseline entry and the status rows;
     * a committed check whose first line is `mergeable: yes` and which names ten file names.
   * None of them reads S-122's title, a part number, the five lines, check-s122-3's minors or m7.
   * The s122 README (line 224, step 5) still sends the integrator to this script.
2. **The extension's own words leave the escape B1 found.** S-122's title (registry line 3611) lets the five
   sentences be "corrected, or dated where the document states their date".
   * V2-SPEC.md lines 82 and 86 sit under a heading that states its date ("as generated on 7 September 2026").
   * Both were false on that date: `gen_sch_b.py` carried the TS3DV642 and never a TMDS341A, and `gen_sch_e.py`
     line 104 at `b2709118` puts the LM5176 on A22.
   * Dating them is the T7 HISTORY premise (`judgements.py` line 417) that check-int15-1's B1 found false.
   * The extension does not ask that a HISTORY judgement check its named parts at the stated date.

*Why it blocks:* the set answers B1 by keeping CFL-016 at FAIL on an extended S-122. With the tool as committed, and
with a condition that admits the same excuse, the extension is words only. The coordinator asked this question
directly, and the answer is yes: S-122 can close without either.

*Fix:*
1. Guard `close_s122.py`, or retire it. Retiring means it refuses with "superseded at set 14" and the s122 README's step
   5 names its successor. A guarded script refuses unless:
   * the named check was committed after `097d2517` and names `check-int15-1.md` and the five lines;
   * `inventory.out` inventories makers' part numbers (for example `TMDS341A`, `TS3DV642` and `WM8960` appear as
     tokens);
   * none of V2-SPEC.md lines 47, 82 and 86 and OPERATING-ENVELOPE.md lines 77 and 83 still names the TMDS341A, the
     WM8960, an LM5176 on E6, the TRACO converter or the Amphenol B-key socket, unless a judgement asserts that part
     in the generator at the date the sentence states.
2. Append to S-122's title: a dated sentence closes as dated only when its named parts are asserted in the generators
   at that date; lines 82 and 86 were not, so they are corrected.

## What was checked, item by item

### 1. Every sentence the script writes

**CFL-016's new entry** (registry line 14304). Each sentence, read against the files:
* "stream s122's inventory entry above describes the inventory as reading every sentence that names a part": true (the
  entry at `9eaf406f`, whose phrase the script asserts before writing).
* "in the check's words the finder reads designators, nets and board names, not makers' part numbers": true. It is my
  wording, in check-int15-1 B1 and in my final message.
* "The check names five sentences in this record's scope that name parts no generator carries":
  * the five, their line numbers and each parenthetical are true on the set 13 netlists: `U3` and `U4`
    TS3DV642A0RUAR; A's `U2` and E's `U6` LM5069MM-2; D's `U6` PCM2912A; no TRACO part on any netlist; `J_M2C2` TE
    2199119-3.
  * The umbrella clause is my own heading, and for line 86 it is loose: the LM5176 is carried, on board A (n1).
* "S-122's closure at 1f3dd306 was therefore premature and is not on this line": true.
* "this record reads FAIL and waits on S-122, extended with these sentences": true (`evidence_result: FAIL`,
  `waits_on: [S-122]`).
* "Its reading also rests on DEFINITION-STATUS.md (rows DC-01 to DC-09), EMCON.md section 0a.1 and ASSEMBLY.md, which
  it is bound to here (2db0ad36da754fa4, c8eb306265110076, 942d562edd128759)": true. All three sha16 are the files'
  at the tip.
* Nothing in the entry goes beyond my report or the files.

**S-122's extension** (line 3611). It keeps the old title as a prefix and states what the closure owes:
* part numbers in the inventory;
* the five sentences judged and corrected, or dated (see B1.2);
* CFL-016 re-read with the three files bound;
* check-s122-3's three minors, described truly: CONOPS.md line 1056's D-13 row, the absent rule's four words, and the
  README's CON-003 quote;
* check-int15-1's m7.

It claims nothing as done.

**`records/int15/README.md`:**
* True: the branch, the two streams' summaries, the rewind, the check table's summary of B1 and B2, and m1, m2, m6
  and m8.
* Loose (n5): "The stale sentences are corrected".
* Missing (n2): check-int15-1's m3.

**The commit message:** true as far as I can read it. "never pushed" I cannot see from the runner, but no remote
tracking ref holds `1f3dd306`.

### 2. CFL-016's FAIL, its bindings, S-122's extension

* **Registry, parsed, `9eaf406f` to the tip:**
  * only CFL-016 (`evidence` +1 as a prefix, `evidence_bound_to` +3) and S-122's title change;
  * open items 86, closed items 68, both unchanged in membership;
  * the top level is unchanged.
* **Registry, main to the tip:**
  * 21 records change: 20 rebinds and REQ-015's `waits_on` (S-106, S-107, S-111, S-124);
  * CFL-016 now reads FAIL on S-122, as on main; no result moved against main;
  * S-120 is closed and S-124 open; S-111's title is extended;
  * S-122 is open with its title extended twice, and S-123 is unchanged;
  * the needs pin is `6cb7b241...`.
* **Bindings:** CFL-016's 15 bindings are all current at the tip, including the three new ones.
* **Can S-122 close without the part number inventory and the five sentences?** Yes (B1).

### 3. Replay of `apply_check15_fixes.py` on `9eaf406f`

* On `r4` at `9eaf406f`, with the script and the hand-written `records/int15/README.md` copied from `097d2517`, the
  script wrote:
  * the registry;
  * the records index;
  * `records/int15/checks/check-int15-1.md`;
  * the four `records/s120/checks/check-s120-*.md`.
* All seven are identical to `097d2517`'s, and a second run refuses ("already applied").
* With the new archive installed, `rules_render.py --requirements`, `rules_status.py` and `rules_render.py` give
  `097d2517`'s REQUIREMENTS-TRACE.md and CURRENT-EVIDENCE.md byte for byte.
* Nine of nine generated files match; the two copied files are the same by construction.
* The filed check-int15-1 equals my `CHECK.md` apart from four `<scratch>/` to `<scratch>/` substitutions (lines 9, 12,
  123 and 328).

### 4. Status, render, the evidence page, validators

* **`rules_status.py`, three times at the tip:**
  * exit 1 each time, with identical stdout: FAIL of 338 (PASS 195, INCONCLUSIVE 104, FAIL 39), NOT_READY;
  * that stdout is identical to main's run.
  * The audits of runs 1 and 3 differ only in SGN-001's `writers` (rules_render.py, read from the archive, against
    rules_status.py). Runs 2 and 3 are identical. This is the self reference that predates the set.
* **`rules_render.py`, twice:** exit 0, nothing written, `git status` clean.
* **The evidence page:** CURRENT-EVIDENCE.md is sha256 `c9b98931...`, main's. No diff from `b874b744` to `097d2517`.
* **Readings, main against the tip:**
  * 339 rule and board rows, 0 results moved, 0 evidence classes moved;
  * the archives differ from main's in the same nine files as before (the seven audits, the status verdict, and
    `rules_complete`), and 930 are identical.
* **Validators and checks:**
  * `rules_lib.py`: 59 rules, 0 errors, 0 warnings;
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings;
  * `rules_render.py --check`: 16 documents, 0 out of date; `--requirements --check`: current;
  * `decisions_render.py --check`: exit 0;
  * `constraints_bound.py`: PASS;
  * `claims_check.py` (scratch): PASS of 91.
* **Tests:** test_requirements 66, test_rules_registry 5, test_decision_register 5 and test_envelope_data 6, which is
  82 passed and 0 failed.

### 5. The filed s120 checks and the index rows

* **The four filed checks** hold no local path: no `/home`, `/tmp`, `/root`, account name or `_scratch`. Each differs
  from its original in `<scratch>/chk-s120/` only by `<scratch>/` substitutions (one line each; no other change).
* **The `s120/` row** is true: four rounds, four checks under `checks/`, 23.40 V INFERRED on the typical 10 percent
  trip, decision 57's 30 V FETs, S-120 closed and S-124 prototype only.
* **The `s122/` row** is true: two branches, three rounds, three filed checks, CONOPS restored, S-122 open. "Stale
  sentences corrected" is loose (n5).
* The rows sit after `int14/` and before `s119/`. There is no row for `int15/` (n3).

### 6. Files

`b874b744..097d2517` changes 52 files. They are the union of the 45 of `9eaf406f`'s line and the 11 of `097d2517` (53
files), less CURRENT-EVIDENCE.md, which is back to main's. Each is within its commit's stated scope.

All 29 commits carry the owner's identity as author and committer and `[MESHSAT-1357]`, with no trailer. The one added
line with an em or en dash is the script's own dash guard constant (n6); the messages have none.

## Minor items

* **n1.** CFL-016's entry repeats my B1 heading, "name parts no generator carries". For V2-SPEC.md line 86 that is
  loose: the LM5176 is generated, on board A, and the sentence puts it on E6. The entry's parenthetical says so
  exactly. Fix: at S-122's closure, say "parts on no board, or not on the board the sentence names".
* **n2.** check-int15-1's m3 is neither answered nor carried: `close_s122.py` line 131 inserts S-122 at the head of
  `closed_items`, and that script is still S-122's closure. Fix: with B1's guard, or a line in the int15 README.
* **n3.** `records/README.md` has no row for `int15/`.
* **n4.** The s120 README (lines 9 to 11, 244, 258, 262) and LOG (lines 40, 70, 93) still cite the checks as
  `<scratch>/chk-s120/...` rather than `checks/check-s120-1.md` to `-4.md`. No note records the `<scratch>/`
  substitution in the filed copies. Fix: one line in the s120 README.
* **n5.** "The stale sentences are corrected" (int15 README) and "stale sentences corrected" (the `s122/` index row)
  read as complete, while five sentences in scope are carried by S-122. Fix: "the stale sentences the stream found".
* **n6.** `apply_check15_fixes.py` line 27 writes its dash guard as literal em and en dash characters, where the other
  scripts use escapes. Cosmetic.

## Counts

* **Items:** blocking 1 (B1); minor 6. First check: B2 answered; B1 carried but not enforced (this B1); m1, m2, m6 and
  m8 carried; m4, m5 and m7 carried or filed; m3 not carried (n2).
* **Script sentences:** CFL-016's entry, 6 of 6 true (one umbrella clause loose, n1); S-122's extension claims nothing
  done, with one escape (B1.2).
* **Replay:** 9 of 9 generated files byte for byte; a second run refuses.
* **Closure test:** `close_s122.py` closes S-122 at `097d2517` with check-s122-3 (B1.1).
* **Readings:** 339 rows, 0 results moved, 0 classes moved; the evidence page is main's.
* **Validators:** 0 errors, 0 warnings. Renderers current. `claims_check` PASS of 91.
* **Tests:** 82 passed, 0 failed.
* **Files:** 52 changed, all explained. Filed s120 checks: 4 of 4 free of local paths.

<!-- Filed from the checker's report; local paths replaced by <scratch>/ and <local path> (records/int15/apply_check15*.py). Where the report itself spoke of that substitution, its words read garbled. -->
