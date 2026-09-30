# Second fresh check of stream d8dec31, tip 9057e668 (AI review), 28 September 2026, 19:54 to 20:15 CEST

Checker chk-d8dec31-2. This is an AI review, not a qualified engineering review. Nothing of the kit has been built,
ordered or measured. Branch `fnd/d8dec31` at `9057e668` (two commits since the first check's `f8e61f05`:
`ec77e6aa`, `9057e668`), worktree `<worktrees>/d8dec31`, read only and untouched.
Everything I wrote is under `_scratch/chk-d8dec31-2/`. The final message is `RESULT.md` beside this file.

## 1. The merge as it will happen

- `git clone --shared` of the main checkout to `view`, `checkout -b chk origin/fnd/int8` (int8 tip `5e765762`, main
  `6b419b02`, merge base of int8 and d8dec31 `73ae2f21`), `git merge --no-ff origin/fnd/d8dec31`.
- ONE conflict, `v2/vendor/sources.txt`, mechanical: both sides appended after the same line 348 (base 348 lines; int8
  added 12 lines, w5tray's materials sheets, the QMX pages and the MIL-STD-810H transcription; d8dec31 added 2 lines,
  the Infineon BSC039N06NS and TI TPS37 sheets). Resolved in the clone by base plus both blocks in that order (362
  lines, 0 markers), committed as `21e82a0c` (scratch only).
- Everything else auto-merged: 58 files, 6855 insertions, 27 deletions. Outside `v2/docs/records/d8dec31/`: the
  review page (new on int8), `v2/ecad/tools/pcb_port_reviews.json` (new), `port_protect.py`, `tests/test_port_protect.py`,
  the two PDFs, `sources.txt`. The stream touches neither `pcb_requirements.yaml` nor the trace page nor
  `vendor-status.txt` (those come as apply scripts), so the conflicts the task warned of do not arise here.
- The merged clone is clean after the test run (`git status --short` empty).

## 2. B1

(a) `env -C view/v2/ecad/tools python3 tests/run.py port_protect`: `tests: 61 passed, 0 failed, 0 skipped`
    (60 `def t_` in the file plus one of test_artefact_recording).
(b) On `tree2` (a second shared clone at 21e82a0c) with `apply_port_declarations.py` applied (A 3 to 18 entries, 30
    internal, 82 pins; D 4/6/26; E 3/13/32; `make_port_reviews.py --check`: "exactly what this script would write"):
    J_USBW moved into `internal_ports` with the 20-character reason "moved inside the box":
    `INCONCLUSIVE of 38, ports 17, ext_pins 19, reviewed 22, disagreements 3`, naming `RECLASSIFIED J_USBW.1 on
    VBUS_WALL`, `.2 on USB_WALL_N`, `.3 on USB_WALL_P`. Baselines: A `PASS of 42` (22 reviewed = 22 declared), D
    `PASS of 21` (8 = 8), E `PASS of 13` (5 = 5). The reading records `inputs.port_reviews` by sha.
(c) J_USBW narrowed to pin 4 (ground): `FAIL of 42` with `FAIL DECLARATION J_USBW.4 is on GND` plus UNCOVERED and
    REVIEWED for pins 1 to 3. J_USBW removed from both lists: `INCONCLUSIVE of 38`, UNCOVERED and REVIEWED named.
(d) My counter-examples (all on the real corrected A table, `repro.py`, `repro2.py`, log in `seq.log`):
    - d1 the reviewed set edited to match the reclassification (J_USBW deleted from `external`, NO `changes` entry,
      no reason) and J_USBW moved to internal: `PASS of 38`, "0 change(s) recorded". PASSES IN SILENCE at the tool.
      What stands behind it: the file's sha in every reading's inputs (readings go stale) and the test
      `t_the_committed_reviewed_sets_are_explicit_and_rest_on_a_review_in_the_tree`, which pins the COUNTS only
      (18/22, 4/8, 3/5). Minor item N1.
    - d1b the set edited, the table as is: `INCONCLUSIVE of 42`, `NOT REVIEWED J_USBW.1/.2/.3`.
    - d2 review file that does not exist: `INCONCLUSIVE`, "rests on v2/docs/reviews/NO-SUCH-REVIEW.md, which is not in
      this tree". d2b review path `README.md` (exists, not a review): `PASS of 42`. Note N4.
    - d3 J_USBW listed TWICE in external_ports: `PASS of 46, ports 19` (was 42, 18). Silent inflation. Minor N2.
    - d3b duplicate JSON key J_USBW in the set holding one pin: `INCONCLUSIVE`, NOT REVIEWED .2 and .3 (json.load keeps
      the last key). d3c duplicate pin key inside J_USBW: `PASS of 42` (identical value; a differing one would win in
      silence). Minor N3.
    - d4 new off_board entry J_DOCK pin 8 not in the set: `INCONCLUSIVE of 54`, `NOT REVIEWED J_DOCK.8 on
      SHORE_INHIBIT: declared off board and in no reviewed set`.
    - d5 a `changes` entry naming J_USBW without a pin while the set still holds it: `INCONCLUSIVE of 38`, RECLASSIFIED.
    - d6 the reviews file absent: board A `INCONCLUSIVE of 42` naming the file; board P (declared zero with its
      reason, no record) `INCONCLUSIVE of 3` (was PASS; stricter, not silent). d6c file present, no record for P:
      `PASS of 3` as before.
    - d7 record `why` of 8 characters: `INCONCLUSIVE`, "carries no reason of 40 characters or more".
(e) `regress_reclassify.py tree2`: 21 `ok` lines, `regress_reclassify: 0 case(s) failed`.
(f) The reviewed set's content, computed by me from the corrected tables and the netlists with port_protect's own
    reader (`repro.py`, section 2f): A 22 pins on 18 connectors, D 8 on 4, E 5 on 3, each EQUAL to the file; every
    record names `v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md`, which exists; one `why` of 311 characters per
    board, `changes` empty. The per-entry reasons live in the board tables (apply_port_declarations.py), not in the
    set; the set carries the pin and its net.

## 3. M1 to M10

- M1 yes. `pdftotext -f 5 -l 5 v2/vendor/ti/ti-lm74700-q1.pdf`: 6.1 Absolute Maximum Ratings, ANODE to GND -65 to
  65 V, CATHODE to ANODE -5 to 75 V; 6.2 ESD Ratings HBM +-2000. Page 4 is the pin table. The ledger row now cites 5.
- M2 yes. 13 rows read "EXTERNAL, protection claimed off this board, not judged here" in `readings/pin-tables.md` and
  in the review (J_BM1 to J_BM11 on A, J_ANT and J_PAOUT on D); J_MAINSW reads "protected off this board (read on
  board C's netlist)". 12 of 18 is right: the corrected A declaration carries 12 off_board entries (J_MAINSW and
  J_BM1 to J_BM11; counted from the applied a.json), the first check's 11 left out J_MAINSW. The review's section
  10 states that TRN-001's PASS of 42 believes those 12 on their text and judged 6 entries on 10 pins.
- M3 yes. E-F3's kind is "BOUND, a conservative model's answer"; a "NOT PROTECTED, BY A BOUND" legend row; section 2
  reads "4 not protected (3 demonstrated ... 1 by a conservative bound: E-F3)"; the registry item says "by a
  conservative bound and not a demonstrated defect".
- M4 yes. "five parts inside (U10, U14, U15, U17 and the module on J_LTG)" in the table, the item and the docstring.
  SDA1's nodes on E's netlist, re-read: D9.1, D9.6, J_LTG.3, J_POD.3, R36.1, U10.6, U14.3, U15.14, U17.3.
- M5 in part. `ids-registry.json` is written under the given root (`v2/docs/records/d8dec31/ids-registry.json`, with
  `registry_top_before`, `ids`, `links`) and the mapping is printed; the closure is a separate stage that refuses
  without the re-take. BUT stage 1 asserts on the MERGED registry (B2) and the closure reads a path where no reading
  of board A lives (B3). With the one-line fix, on int8: S-98 to S-111, validator 0 errors.
- M6 yes. `apply_interfaces_mainsw.py tree2`: "board A's netlist has J_MAINSW.1 on MAIN_PB, not MAIN_PB_LEAD: apply
  apply_gen_sch_a_mainpb.py and re-run the generator first (...)", rc 1; `--force-netlist --check` rc 0; the a_mainpb
  docstring names it. The `src` line stays 278 with a note for the generator owner.
- M7 yes. e_cin's docstring: C382212 is board A's C207's (gen_sch_a.py 665, 729, 800); C6 and C7 carry no code
  (gen_sch_e.py 399); the registry item E-F1 and the README say the same.
- M8 yes. The review's new paragraph "Why this review exists now, and what it closes" and the README name H3-02,
  erratum f and S-88 and the H3 review file; both files exist in the merged tree (RELEASE-H3.md line 114 carries
  erratum f with H3-02).
- M9 yes. `apply_sources_d31.py tree2` rc 0 ("documents_filed_d8dec31 with 2 entries") after checking both files'
  sha256 (8d95c1da..., d6aed9d9...); second run refused. Parts entries for C534330 and C3685740 said owed.
- M10 yes. On the COMMITTED shape of a.json with J_USBW `pins: ["1"]`: `AssertionError: board A: J_USBW.2 carries
  USB_WALL_N and no entry covers it` (rc 1). Untouched, the script reproduces `readings/pin-tables.md` (sha lines
  aside). But see N6: on the corrected table it asserts earlier, in `a_external`.

## 4. The apply order (README's six steps), rehearsed on tree2 with a status snapshot after each

1. `apply_port_declarations.py` edits `boards/a.json`, `d.json`, `e.json`; asserts the old J_DOCK text; second run
   "board A already declares internal_ports: already applied". `make_port_reviews.py --check` reads exactly.
2. `apply_config_inputs_port_reviews.py` edits `rules_status.py` (shared); asserts OLD once, needs the json in the
   tree, imports the patched module from a copy; second run "already applied (the entry is in the file)".
3. `apply_registry_d31.py` edits `pcb_requirements.yaml` (shared) and writes `records/d8dec31/ids-registry.json`.
   AS COMMITTED IT ASSERTS ON INT8 (B2). Fixed copy: S-98 to S-111, `rules_lib: 144 requirement record(s), 0
   error(s), 0 warning(s)`, second run "already applied (its marker is in the file)".
4. `apply_sources_d31.py` edits `v2/vendor/SOURCES.yaml`; second run refused. `apply_holds_review_pin.py` edits
   `pcb_board_holds.yaml` (shared), pins the review as `094817023210d1b0` (the review at 9057e668; the first check
   saw `2bb9167daa7974cb` at f8e61f05, so the sha follows the review, read at apply time); second run "expected three
   unpinned review blocks, found 0".
5. The box's re-take, then `--close-s88 <commit>`: refusals verified (no reading; netlist sha 0000...; tool sha
   2d69facd... against the tree's 7acd5333...; an INCONCLUSIVE reading; a commit not in history, in a checkout);
   `--check` then apply: "S-88 closed by commit 9057e668 on the re-taken reading (PASS of 42, netlist
   0a2b59087bcc2678, tool 7acd5333fc59f8d0); waits_on dropped from REQ-015, REQ-017, REQ-029, CON-018"; second run
   "S-88 is already closed"; validator after: 0 errors. Registry after both stages: 80 open, 61 closed. BUT the
   reading's path (B3).
6. The circuit round: the four `apply_gen_sch_*.py` (not re-run by me; the diff since f8e61f05 changes the
   docstrings of a_mainpb and e_cin only, the first check ran all four on copies), then `apply_interfaces_mainsw.py`
   (refuses until the netlist moves, verified).

## 5. Tests' hygiene

`/tmp/port-*`: 0 before the run, 45 after, removed by me. `test_port_protect.py` has 46 `mkdtemp` calls and 0
`rmtree` or `TemporaryDirectory`. The tests do NOT clean up (minor N5); the author's "mine are removed" was a hand
removal.

## 6. Prose and scope

22 files in `git diff --stat f8e61f05..9057e668`, as claimed. 0 U+2014 or U+2013 in added lines. "AI review" in the
review's title and first paragraph and twice in the README; "Nothing of this kit has been built, ordered or measured"
at review lines 4 to 5. The claimed results reproduced (61 tests, 21 cases, 0 errors after the rehearsal on MAIN;
the rehearsal was on main plus the branch, which is why the int8 anchor was not seen). No protection lowered: the
circuit scripts add parts only. TRN-001's PASS of 42 on A is stated to believe the 12 off_board entries on their text.

## 7. Not done

No generator, no KiCad, no full suite, no box re-take; the four circuit scripts not re-run; the author's neighbouring
test files not re-run; the ledger's other 43 page citations not re-opened (the first check did); the behaviour after a
circuit change moves a netlist (the set's `netlist_sha256_16` as a note) not exercised; the review's prose outside
the diff hunks not re-read.

## Files here

`RESULT.md` (the final message), `check-1.md`, `diff-stat.txt`, `diff-full.patch`, `sources.merged.txt`,
`int8-registry.yaml`, `repro.py`, `repro2.py`, `seq.sh`, `seq.log`, `m10.err`, `pin-tables.chk.md`,
`a.json.corrected`, `apply_registry_d31_fixed.py` (the one-line fix), `chk-verdicts/` (the scratch readings of
section 2). The two scratch clones `view` and `tree2` were removed at the end.

---
Filing note (scrub, 30 September 2026, MESHSAT-1357): 1 path in this check is written as neutral tokens (`<worktrees>`) under the owner's rule that public files carry no internal host names, user paths or addresses; `v2/docs/records/scrub/MAP.md` lists each by line and token class. No other byte of the check changed; the check as filed is in the repository's history at commit `8fec0733` and before.
