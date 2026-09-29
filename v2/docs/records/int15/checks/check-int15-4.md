mergeable: yes

# AI review: fourth check of integration set 14, fnd/int15 at 1bafab8c (MESHSAT-1357)

This is an AI review, not a qualified engineering review. I did not write the work under check; `CHECK.md` to
`CHECK-3.md` (filed as `check-int15-1.md` to `-3.md`) are mine. Checked 29 September 2026 from 20:42 to 20:51 CEST
(times read with `date`). Everything below is what I read or ran myself.

**This is an integration check of set 14. It is not the independent check that S-122's closure asks for, and it
must not be filed or used as one.** It did not re-read the five corrected sentences, which are not corrected yet.

**Set up**
* `fnd/int15` is `1bafab8c6ac03c34b375ec4c2549e45c5b49501b`, one commit on `f21fc8f8`, still the tip at 20:50.
* Tip clone: `<scratch>/chk-int15`, moved to `1bafab8c`, with `int15-evidence-097d2517.tar` re-installed (as asked).
* Throwaway clones in my session scratchpad: `c15/r8` at `f21fc8f8` (the replay) and `c15/r7` at `1bafab8c` (the
  mutants). Working tree edits only, reset after each run; nothing committed.
* Tools ran with `VERDICT_DIR` in the scratchpad; `git status` of the tip clone shows only my four reports. No commit,
  no push, no agent, no other model, no box. The full suite was not run.

**Counts: 0 blocking, 5 minor.** CHECK-3's B1 is answered: S-122's sentence now says what the gate checks and leaves
substance to the filed check. p2 to p6 are fixed.

## Blocking items

None.

## 1. The gate against the mutants

I called `gate_set14` in the tip's `close_s122.py` on `r7`, from the repository top unless stated. For mutants that
pass the finder probe I used a "rigged" finder: `s122lib.names` gains a `parts` key that returns only the five probe
strings.

**Refused as intended:**
* **G0**, the unchanged tree with `check-s122-3.md`: refused at the finder probe ("does not read the part number
  WM8960"). This is your result.
* **M1**, the rigged finder only: refused, "verdicts.out asserts no board B's U3 or U4 as TS3DV642".
* **M1b**, the rigged finder and the four assertions appended to `verdicts.out`, rows left: refused, listing all
  five rows.
* **M2**, the rows corrected and the assertions present, the finder unchanged: refused at the probe.
* **M3**, everything else met, with `check-s122-3.md`: refused, "does not name check-int15-1".
* **M4**, the same, with `check-s122-3.md` edited to name check-int15-1: refused, "not committed on a line that
  carries 097d2517".
* **M8**, assertions for the wrong boards (B U6 LM5069, A U6 PCM2912A): refused, "asserts no board E's U6 as LM5069".

**Passed as intended:**
* **M5**, everything met with `check-int15-2.md`. `main` would then refuse on its first line, `mergeable: no`.
* **M7**, a V2-SPEC correction note naming the TMDS341A and the WM8960 outside the rows. p1 is fixed.
* **M10**, M5 run from a scratch cwd with the relative check path. p2 is fixed.
* **M11**, a real pattern finder for part numbers in place of the rig. The probe can be met honestly.

**Passed, with the five sentences wrong in substance:**
* **M6:** the five parts replaced by other wrong ones (TMDS351, WM8731, LM5175 on E6, TRACO TEN 60, a Molex B-key
  socket).
* **M9:** the same five wrong parts kept, with the rows' first cells changed. The labels became `B16 (compute)`,
  `APRS, VHF voice`, `TRACO TEN40-2412WIN` and `Amphenol M.2 B-key socket (MDT420B01001)`. The E6 row kept its label
  and "the LM5176 9 to 36 V front end", with "all under A22" added at its end.

**The two probes you asked for:**
* **(a) A finder that knows only the five probe strings passes.** The rig returns `TMDS341A` for "the TMDS341A display
  switch", but nothing for "the XQ4417B display switch" or "Direwolf on the WM8731 codec". The pattern finder returns
  all three.
* **(b) Assertions for the wrong board are refused (M8). Assertions of the right board anywhere in `verdicts.out` pass
  (M1b to M5).**
  * They are not tied to the five sentences.
  * The J_M2C2 one is met today by three unrelated sentences: V2-SPEC.md lines 41 and 76, and ASSEMBLY.md line 218.
    So condition (b) holds for the B-key row without any work on OPERATING-ENVELOPE.md line 83.

**So can S-122 close with the five sentences wrong in substance?** Yes, past the gate: M6 and M9. S-122's sentence now
says so, in effect: "Confirming that each correction is true in substance remains the filed check's job". That is the
guard I asked for at minimum, so this no longer blocks.

**What would make (a) and (b) instruments** (q2):
* (a): probe with part numbers made up at run time, for example random letter and digit strings. Or probe with every
  part number the six netlists' values carry. A hard-coded list then cannot pass.
* (b): key each assertion to the five sentences' locations in `verdicts.out`, and require each of them TRUE and not
  HISTORY.
* (c): find the rows by what they say, not by their exact first cell. Refuse "LM5176" in the E6 row except in "A22's
  LM5176".

## 2. S-122's correcting sentence (registry line 3623)

Registry, parsed, `f21fc8f8` to the tip: only S-122's title moves, with the old title kept as a prefix. CFL-016 reads
FAIL on S-122 with 15 bindings, all current.

Clause by clause:
* "the previous sentence overstated the closing script": true.
* "the finder returns a maker's part number from probe sentences that name only one": true (five fixed probes).
* "verdicts.out asserts board B's U3 or U4 as TS3DV642, ... J_M2C2 as 2199119": true as a file search. It does not
  claim the assertions belong to the five sentences, and they need not.
* "V2-SPEC.md's B16, APRS and E6 rows and OPERATING-ENVELOPE.md's TRACO and Amphenol rows no longer name the parts
  check-int15-1 found": **not exact** (q1).
  * Rows are found by their exact first cells, so relabelled rows keep the parts (M9).
  * The E6 row may keep "the LM5176 ... front end" whenever "A22" appears anywhere in it (M9, with the label
    unchanged).
* "the filed check names check-int15-1 and was committed on a line that carries 097d2517": true. The oldest commit
  adding the check must descend from `097d2517`.
* "Confirming that each correction is true in substance remains the filed check's job": true, and it is the sentence
  that matters.
* "check-int15-2 found lines 82 and 86 false at their stated date; lines 47, 77 and 83 carry no date": true. The lines
  themselves state no date; the two documents' titles do.

## 3. p4 to p6

* **p4.** `close_s122.py` line 168 now inserts before `records:`. With the gate call stubbed out (a working tree test
  only), the closure on `r7` put S-122 last of 69 `closed_items`, and `rules_lib requirements` read 0 errors.
* **p5.** The `int15/` row now reads "its closing script gated on a part-number finder and the corrected rows, the
  substance left to the filed check". That is true.
* **p6.** Seven filed checks (`check-int15-1` to `-3`, `check-s120-1` to `-4`):
  * each first line is still `mergeable: ...`;
  * each ends with the filing note;
  * each equals the scrub of the checker's report plus the note, byte for byte;
  * none holds a local path or the account name.
  * The note's "its words read garbled" is true of check-int15-2 line 133 and of two lines of check-int15-3.

## 4. Replay of `apply_check15c_fixes.py` on `f21fc8f8`

* On `r8` at `f21fc8f8`, the committed script (which writes the notes at the end) wrote:
  * the registry;
  * `close_s122.py`;
  * the records index;
  * `check-int15-3.md`;
  * the notes on the six earlier filed checks.
* After `rules_render.py --requirements`, all twelve script and render outputs equal `1bafab8c`'s, byte for byte. A
  second run refuses.
* The int15 README differs only by its hand written check-int15-3 row, which the script does not write. So the replay
  reproduces the commit. The first run with notes at the head left no trace in it.

## 5. Status, render, the page, validators, tests

* **`rules_status.py`, three times:** exit 1 each time, with identical stdout, which is identical to main's: FAIL of
  338 (PASS 195, INCONCLUSIVE 104, FAIL 39), NOT_READY. The audits equal `f21fc8f8`'s apart from the head.
* **`rules_render.py`, twice:** nothing written, and the clone is clean.
* **The evidence page:** CURRENT-EVIDENCE.md is `c9b98931...`, main's.
* **Validators and checks:**
  * `rules_lib.py`: 59 rules, 0 errors, 0 warnings;
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings;
  * renderers current;
  * `decisions_render.py --check`: exit 0;
  * `constraints_bound.py`: PASS;
  * `claims_check.py`: PASS of 91.
* **Tests:** test_requirements 66, test_rules_registry 5, test_decision_register 5 and test_envelope_data 6, which is
  82 passed and 0 failed.
* **Readings:** against main, 339 rows, 0 results moved, 0 classes moved (the same archive as at `097d2517`).

## 6. Files

* `1bafab8c` changes 13 files, each within its stated scope. `b874b744..1bafab8c` changes 56.
* All 31 commits carry the owner's identity and `[MESHSAT-1357]`, with no trailer, and no em or en dash is added.

## Minor items

* **q1. S-122's clause on the rows is broader than the gate.**
  * The gate finds rows by their exact first cells.
  * It lets the E6 row keep the LM5176 whenever "A22" appears anywhere in it.
  * Fix: at the next registry pass append "rows found by their first cells; the E6 row may name the LM5176 where it
    names A22". Or tighten the gate as in section 1 (c).
* **q2. (a) and (b) are not yet instruments** (section 1).
  * The probe passes a finder that knows only the five strings.
  * The assertions are not tied to the five sentences, and the J_M2C2 one is already met by unrelated ones.
  * These are not blocking, because S-122 now leaves substance to the filed check.
* **q3. The gate cannot tell S-122's closing check from any other check.**
  * Any check committed after `097d2517` that says `mergeable: yes` and names check-int15-1 and the ten file names
    would do, an integration check like this one included.
  * Fix: require a marker only a closing check carries, for example a heading that names S-122's closure and the five
    lines.
* **q4. Two docstrings say more than the code:**
  * `apply_check15c_fixes.py` line 17 says "a filing note heading every filed check", but it ends them;
  * `close_s122.py` line 58 says the verdicts "assert the generated parts the corrected sentences name", but the gate
    does not tie them to those sentences.
* **q5.** The int15 README's check-int15-3 row says "the gate made an instrument". It is part way there (q2).

## Counts

* **Items:** blocking 0; minor 5. CHECK-3: B1 answered; p1 to p6 answered (p1 and p2 tested, p3 in S-122's sentence,
  p4 tested, p5, p6).
* **Mutants:** 13 run.
  * 7 refused as intended: G0, M1, M1b, M2, M3, M4, M8.
  * 4 passed as intended: M5, M7, M10, M11.
  * 2 passed with wrong substance: M6, M9, which the filed check owns by S-122's sentence.
* **Replay:** 12 of 12 script and render outputs byte for byte; a second run refuses.
* **Registry:** only S-122's title moved. CFL-016 FAIL on S-122, 15 of 15 bindings current.
* **Status and render:** stable and clean. The evidence page is main's. Validators 0 errors, 0 warnings.
* **Tests:** 82 passed, 0 failed.
* **Files:** 13 changed, all explained.

<!-- Filed from the checker's report; local paths replaced by <scratch>/ and <local path> (records/int15/apply_check15*.py). Where the report itself spoke of that substitution, its words read garbled. -->
