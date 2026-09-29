mergeable: no

# AI review: third check of integration set 14, fnd/int15 at f21fc8f8 (MESHSAT-1357)

This is an AI review, not a qualified engineering review. I did not write the work under check; `CHECK.md` and
`CHECK-2.md` (filed as `check-int15-1.md` and `check-int15-2.md`) are mine. Checked 29 September 2026 from 20:28 to
20:37 CEST (times read with `date`). Everything below is what I read or ran myself.

**Set up**
* `fnd/int15` is `f21fc8f806c3e73230761984db937da2a2b9553e`, one commit on `097d2517`, still the tip at 20:36.
* Tip clone: `<scratch>/chk-int15`, moved to `f21fc8f8`, with `int15-evidence-097d2517.tar` re-installed (as asked).
* Throwaway clones in my session scratchpad: `c15/r6` at `097d2517` (the replay) and `c15/r7` at `f21fc8f8` (the
  mutants). Working tree edits only; nothing was committed, and `r7` was reset after each mutant.
* Tools ran with `VERDICT_DIR` in the scratchpad; `git status` of the tip clone shows only my three reports. No commit,
  no push, no agent, no other model, no box. The full suite was not run.

**Counts: 1 blocking, 6 minor.** CHECK-2's B1 is answered in part: the tool now refuses the old check and the five
literal strings. Its part number condition is a declaration, and S-122's new sentence claims more than the gate checks.

## Blocking items

**B1. S-122's new sentence says `close_s122.py` refuses unless "the five sentences are corrected". The gate checks five
literal strings and a declared token, and both can be satisfied with the five sentences still wrong and no part number
read.**

*Where:* `v2/ecad/tools/pcb_requirements.yaml` line 3618 (S-122's title), written by
`records/int15/apply_check15b_fixes.py` (`S122_ADD`). The gate is `gate_set14` in `records/s122/close_s122.py`.

*What I ran* (`gate_set14` called on `r7`, from the repository top):
* The unchanged tree with `check-s122-3.md`: refused on the token. This is your result.
* The token added, the parts left: refused, naming all five strings.
* The parts corrected, no token: refused on the token.
* The token and the parts corrected, with `check-s122-3.md`: refused, "does not name check-int15-1".
* The same, with `check-s122-3.md` edited in the working tree to name check-int15-1: refused, "not committed on a
  line that carries 097d2517". Its adding commit is on the s122b line.
* The token and the parts corrected, with `check-int15-2.md`: the gate passes. The rest of `main` then refuses, on
  the rebinding.
* **The token, and the five parts replaced by other wrong ones** (TMDS351, WM8731, LM5175 on the E6 row, TRACO TEN
  60, a Molex B-key socket), with `check-int15-2.md`: **the gate passes.**
* **The token as one added header line in `inventory.py`, the finder unchanged.** `inventory.py` still writes 862
  sentences. The new inventory differs from the committed one only in that line, the documents' sha line and the two
  changed rows. None of the wrong part numbers is a token in it. Lines 47, 77 and 83 are still outside it.
  `verdicts.py` then reads 2 UNJUDGED, the two changed boards table rows. Two judgement lines (T7, HISTORY, which
  `judgements.py` line 417 still offers) and a new check reading `mergeable: yes` would close S-122.

*So:*
* **Without the part number inventory:** yes. The token is a declaration, satisfied by one header line.
* **With any of the five sentences left:** not with the same strings, but yes in substance.

The only remaining guard is the independent check. S-122's sentence tells the next integrator and checker that the
script has already made sure of the corrections.

*What would make the token an instrument* (any one of the first two, plus the third):
1. The gate runs `s122lib`'s finder itself on probe sentences that name only a maker's part number. For example: "the
   TMDS341A display switch", "Direwolf on the WM8960 codec", "| TRACO TEN 40-2412WIN | dock strip |". It refuses
   unless each probe is inventoried with that part number among its names.
2. The gate refuses unless the committed `inventory.out` holds the three sentences the old finder missed, by their
   location keys, with part number names. They are V2-SPEC.md line 47's second cell, and OPERATING-ENVELOPE.md lines
   77 and 83 or the rows that replace them.
3. For the five sentences, the gate refuses unless `verdicts.out` judges each TRUE, with an assertion naming the
   generated part, and not HISTORY. The parts: `B:U3~TS3DV642` and `B:U4~TS3DV642`, `E:U6~LM5069` for the E6 row,
   `D:U6~PCM2912A`, `B:J_M2C2~2199119`, and the TRACO row gone. That also kills the wrong replacement mutant.

*Fix (either):*
1. Make the gate an instrument as above.
2. At least, append to S-122 a sentence that says exactly what the gate checks: the declared token, the five literal
   strings absent, and the check's provenance. It must also say that the corrections themselves, each part on its
   netlist, are the filed check's to confirm, sentence by sentence. With that, and the minors, I would see no blocker.

## What was checked, item by item

### 1. Can S-122 close without the part number inventory or with the five left?

See B1. The provenance test works as intended: the oldest commit adding the check must descend from `097d2517`. An old
check re-edited, or a renamed check, is refused.

### 2. S-122's addition

* Registry, parsed, `097d2517` to the tip: only S-122's title moves, with the old title kept as a prefix. CFL-016
  still reads FAIL on S-122, and its 15 bindings are current. No other record or item moved.
* The first sentence closes the dated loophole in words: "a sentence closes as dated only if the parts it names are
  shown in the generators at the date it states". The tool enforces it only through the five strings (B1).
* "the re-check found the five sentences above false at their own dates" overstates CHECK-2 (p3).
* The last sentence overstates the gate (B1).

### 3. The minors' fixes

* **n1:** the int15 README carries it, and its text is true.
* **n2:** the README says m3 "concerned the dropped closure; nothing on this line closes S-122". The closure script is
  on this line, named by the s122 README's step 5, and still inserts S-122 at the head of `closed_items` (line 155)
  (p4).
* **n3:** the `int15/` index row is added. "its extension enforced in its closing script" overstates (p5).
* **n4:** the s120 README's note is true. The filed copies differ from the originals only by the `<scratch>/`
  substitution.
* **n5:** "the stale sentences its inventory found" and "five more sentences corrected" are true.
* **n6:** `apply_check15_fixes.py` line 27 now writes its dash guard as Python escape sequences (backslash u2014 and
  backslash u2013), and the new script does the same. No added line from `b874b744` to the tip holds an em or en
  dash.

### 4. Replay of `apply_check15b_fixes.py` on `097d2517`

* On `r6` at `097d2517`, with the script copied from `f21fc8f8`, it wrote:
  * the registry;
  * `close_s122.py`;
  * the s122, records and s120 READMEs;
  * `apply_check15_fixes.py`;
  * `checks/check-int15-2.md`.
* All seven are identical to `f21fc8f8`'s. After `rules_render.py --requirements`, so is REQUIREMENTS-TRACE.md.
* A second run refuses ("already applied").
* The int15 README differs from the tip only by the two hand-written additions (the check-int15-2 row, and the n1 and
  n2 lines).
* The filed check-int15-2 differs from my `CHECK-2.md` in five lines of `<scratch>/` to `<scratch>/`. One of them
  garbles my sentence (p6).

### 5. Status, render, the evidence page, validators

* **`rules_status.py`, three times:** exit 1 each time, with identical stdout, which is identical to main's: FAIL of
  338 (PASS 195, INCONCLUSIVE 104, FAIL 39), NOT_READY. The audits equal `097d2517`'s apart from the head.
* **`rules_render.py`, twice:** nothing written, and the clone is clean.
* **The evidence page:** CURRENT-EVIDENCE.md is `c9b98931...`, main's.
* **Validators and checks:**
  * `rules_lib.py`: 59 rules, 0 errors, 0 warnings;
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings;
  * renderers current (16 documents, and the trace);
  * `decisions_render.py --check`: exit 0;
  * `constraints_bound.py`: PASS;
  * `claims_check.py`: PASS of 91.
* **Tests:** test_requirements 66, test_rules_registry 5, test_decision_register 5 and test_envelope_data 6, which is
  82 passed and 0 failed.
* **Readings:** the archive is the one checked at `097d2517`. Against main, 339 rows, 0 results moved, 0 classes moved.

### 6. Files

* `f21fc8f8` changes 10 files, each within its stated scope. `b874b744..f21fc8f8` changes 54.
* All 30 commits carry the owner's identity and `[MESHSAT-1357]`, with no trailer and no em or en dash in messages.

## Minor items

* **p1. The gate refuses correct text.**
  * A correction note in V2-SPEC.md's own style naming what it corrected ("Line 82 named the TMDS341A ...") is refused.
    I ran this mutant, and it was refused. Correction 32 names the TPS55288 the same way.
  * So would an E6 row that says the bus goes "into A22's LM5176".
  * Fix: test the five rows, not the whole files.
* **p2. The gate and `main` read the check from different places.**
  * The gate opens the check relative to the cwd; `main` reads it relative to the repository, as the docstring (line
    26) says.
  * Run from another cwd, `close_s122.py` now stops with FileNotFoundError. It fails closed, but it crashes rather than
    refusing.
  * Fix: `os.path.join(L.TOP, chk)` in the gate.
* **p3. S-122's addition and the script's docstring say "the re-check found the five sentences above false at their own
  dates".**
  * CHECK-2 said so of lines 82 and 86.
  * Lines 77 and 83 state no date; check-int15-1 found them false when written (16 September).
  * Line 47 was written on 6 September, while the D6 generator still had the WM8960, which left at `bdfc7b3f` (7
    September, 07:15). Neither check found it false at a stated date.
  * The conclusion, that they close only corrected, stands.
  * Fix: an appended correction at the next registry pass.
* **p4. The n2 answer sidesteps m3.** `close_s122.py` line 155 still puts S-122 at the head of `closed_items`. Fix:
  append at the end.
* **p5. The `int15/` index row says S-122's "extension enforced in its closing script".** The gate enforces part of it.
  Not enforced: CFL-016's re-read, check-s122-3's minors, m7, and the five sentences beyond their strings. Fix: "partly
  enforced".
* **p6. The filed `check-int15-2.md`, line 133, reads "four `<scratch>/` to `<scratch>/` substitutions".** The scrub
  rewrote my literal `<scratch>/`, and no filing note records the scrub. Fix: a filing note, or leave backquoted names
  alone.

## Counts

* **Items:** blocking 1 (B1); minor 6.
* **CHECK-2:** B1 answered in part (see B1); n1 carried; n2 carried but sidestepped (p4); n3 to n6 fixed.
* **Mutants:** 8 run.
  * 4 refused as intended: token only, parts only, no check-int15-1, old check.
  * 1 passed as intended: all met.
  * 1 passed wrongly: wrong parts plus the token.
  * 1 refused wrongly: a correction note.
  * The token was shown independent of the finder, and the cwd crash was shown.
* **Replay:** 8 of 8 files byte for byte; a second run refuses.
* **Registry:** only S-122's title moved. CFL-016 FAIL on S-122, 15 of 15 bindings current.
* **Status and render:** stable and clean. The evidence page is main's. Validators 0 errors, 0 warnings.
* **Tests:** 82 passed, 0 failed.
* **Files:** 10 changed, all explained.

<!-- Filed from the checker's report; local paths replaced by <scratch>/ and <local path> (records/int15/apply_check15*.py). Where the report itself spoke of that substitution, its words read garbled. -->
