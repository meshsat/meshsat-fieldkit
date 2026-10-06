DONE: Q-53 (the cap, committed dabfe4ca), Q-55 (as apply_q55_ve16.py for set 32's merged tree) and Q-65 (W47: Q-55's change record row and TP-SOLAR.md's quote, edits 5 and 6 of the same script). NOT DONE: nothing of either brief. NEXT: set 32's integrator runs apply_q55_ve16.py after set 31's promotion, re-pins, re-keys, regenerates tp_check.out.

# Record s32small: set 32's two decided small items (MESHSAT-1357, W40, 6 October 2026)

Branch `fnd/s32small` from main `eff28be3b80f882db545a849b0da1def0217f63d`, adopted in set 32. Author W40; config and record
text only: no computation, verdict or claim changed, no `.out` committed. Prototype framing: nothing in the kit is built,
bought, powered or measured.

## Q-53: the handover ZIP's cap (committed dabfe4ca)

The coordinator's decision of 6 October 2026 13:35 CEST (QUEUE line Q-53, authority SESSION under the owner's standing rule of
26 September 2026, reported in checkpoint 32; the owner may overrule it). W36's finding F-S1 measured the overrun.

| File | Old | New |
|---|---|---|
| `v2/docs/handover/pack.yaml:21` (now :33) | `max_zip_bytes: 52428800` | `max_zip_bytes: 104857600`, with the reason as decided in the comment above it (the records' generators about 4.8 MB, outputs about 2.5 MB and pages about 3.9 MB compressed grew the ZIP from H2's 51.9 MB into an estimated 70.2 MB against a 52.4 MB cap that H1 and H2 set themselves; the vendor PDFs stay referenced; a second archive would split what a reviewer reads together) |
| `pack.yaml` comments at the old :75, :87, :224 | "under max_zip_bytes" as a present statement | the same, "as it then stood (52,428,800 bytes)", with the dated note that the cap is 104,857,600 since 6 October 2026; no rule changed, the H1.1 patches and CON-017's ST documents stay referenced |
| `v2/ecad/tools/tests/test_handover_pack.py` | no test held the tree's cap; the fixture's `max_zip_bytes: 1000000` is the throwaway repository's own | a comment saying so above the fixture, and the new `t_the_cap_is_100_mib_and_the_estimate_at_this_tree_is_under_it`: the tree's pack.yaml reads 104857600, and `h3/zip_size_estimate.py` run on HEAD prints the same cap, a positive margin equal to cap minus estimate, and exits 0 |

`handover_pack.py:788-790` reads the cap from the spec (line 613) and needed no change. `h3/zip_size_estimate.py` reads the cap of
the commit it is given (its line 101) and needed no change; its docstring's "(52,428,800)" is a dated statement of 27 September
2026 and is left as H3's record (its sha256 is pinned in `v2/docs/records/README.md`).

Readings (the estimator writes nothing): at eff28be3, `ESTIMATE: 70175272 bytes; H2 was 51894737; cap 52428800; margin -17746472
bytes (OVER THE CAP)`, so 34,682,328 bytes under the new cap. The new test passes on dabfe4ca (17 passed in the module). Its
mutations, on a scratch clone: at the base eff28be3 it fails "pack.yaml's max_zip_bytes is 52428800, not Q-53's 104857600"; with
52428800 committed and the test's constant matched it fails "the estimated ZIP at HEAD is 70177066 bytes, 17748266 over the cap of
52428800".

**What the estimator's design implies for `h3/zip_size_estimate.out`:** keep H3's accepted reading and let a new record carry the
current one. The script estimates a named commit (default HEAD) under a version name (default "H3") and compares with that commit's
own cap. Its `.out` is H3's pre-build reading of 089f7f27 (52,188,777 estimated against H3's built 52,187,825). Run with the
arguments `089f7f27 H3` it reproduces that file except line 1's label (`commit 089f7f27` for `commit HEAD`); a plain regeneration
(regen_out runs it with no arguments) would put the current HEAD under the name "H3" and lose the reading H3's release was checked
against. The current reading belongs in a new record's output, made with the candidate's commit and its own version name.

## Q-55: V-E16's row 3 carries N1a's annotation (apply_q55_ve16.py, for set 32's merged tree)

The coordinator's decision of 6 October 2026 15:22 CEST (QUEUE line Q-55): the record's own invariant, V-E16's rows 2 and 3
mirror the register's R-176 rows 2 and 3 verbatim (record l5pwr's L5-F09 d), carried in set 32 because in set 31 it would have
invalidated the re-key then running.

**Delivered as a script, not an edit (authority SESSION, W40, 6 October 2026; the coordinator confirmed it at 16:21 CEST).** Main
eff28be3 holds neither N1a's annotation of the register (b2564b59), W8's restatement of V-E16 (8840adda) nor `test_w8l5.py` (the
coordinator's form at f0748b49): all are set 31's (`fnd/int31regen`). An edit of V-E16's one-line row here would conflict with W8's
edit of the same line at the merge, and the test does not exist here. Reversed by making the three edits by hand.

The three edits, all checked before any is written (the script's docstring has the full list):

| File | Old | New | Basis |
|---|---|---|---|
| `v2/docs/HW-FW-CONTRACT.md`, V-E16, row 3 | "U5's CSPIN to CSNIN within +-0.240 V, U21 turning Q12 off" | "U5's CSPIN to CSNIN within +-0.240 V (under R-240, drafted, not applied: under 10 mV in magnitude, a layout check, L4E7-P0SOL.md section 5), U21 turning Q12 off", the place the register's R-176 row 3 carries it (`DOWNSTREAM-REGISTER.md:272` at set 31); nothing else in the row | Q-55 |
| `v2/ecad/tools/tests/test_w8l5.py`, end of `t_nothing_else_moved_and_the_bench_rows_are_still_the_registers` | the coordinator's live check (the register differs from W8's by N1a's words alone) | the same, then V-E16 read from the TREE equals the live register's rows 2 and 3; the fixture form stays for W8's own change | Q-55 |
| `v2/ecad/tools/tests/test_l5pwr.py:446-448` (W14's reading of L5-F09 d) | the script's printed values read in the live V-E16 row | where a restated field carries N1a's words they stand exactly once, in V-E16, right after U5's line, and are taken out before the values are read; nothing else of the reading changes | found by the sweep: after the first two edits this test failed "L5-F09 d: a value the script printed is gone" (the script printed row 3 before N1a) |

Checked on a scratch clone of set 31's tip d5d9c252 (removed afterwards): `--check` and the run change exactly the three files
(HW-FW-CONTRACT.md f26757c7c5004cdd to c52eaa5f4ba501ab); a second run exits 3; a half-applied tree and a tree without N1a are
refused (exit 2); on this branch's own tree it refuses (test_w8l5.py is absent). test_w8l5 and test_l5pwr: 22 passed before and
after. Mutations: V-E16 without N1a's words (the patched test kept) fails test_w8l5's new check; the words altered ("under 11 mV")
fails it; the words put also into row 2 fail both tests.

The sweep (the same clone, v2/docs and v2/ecad checked out): the 11 light modules that read HW-FW-CONTRACT.md, before and after
the apply. Before: 156 passed, 26 failed, 2 skipped, the 26 the clone's environment (no firmware tree, no vendor files, the
registry's unheld ST documents). After: the same plus two, both pins, `test_l5r2.t_r3_output_reproduced_and_every_finding_resolved`
(l5r3_panel.out prints the page's sha256) and `test_w24l4e9.t_the_four_typed_in_pins_equal_their_files`
(`l4e9_power_path.py:75`); with the two PINS re-pinned and l5r3_panel.out regenerated on the clone (one line moved, the pin) both
pass. The heavy modules test_l4e5, test_l4e9, test_l4e11 and test_l9t5 were read, not run: none reads V-E16, and their page reads
(FW-C08, the keyed outlets, the FW-B rows, a fixed commit) do not move.

**What set 32 must do after it runs the script:** re-pin `PINS["hwfw"]` in `v2/docs/records/l4e11/l4e11_power.py:54` and
`v2/docs/records/l4e9/l4e9_power_path.py:75` to the printed sha256; re-key the l4e7 KEY (l4e11_power.out is in it and pins the
page); one dependency pass re-pinning l4e11_power.out, l4e9_power_path.out, l5r2_interfaces.out, l5r3_panel.out,
l8gnd_drafts.out and l9t5_t10.out.

## Q-65: Q-55's change record row and TP-SOLAR.md's quote (W47, edits 5 and 6 of apply_q55_ve16.py)

W47's brief (`_runs/claude/w47s32txt/BRIEF.md`, QUEUE line Q-65): the two record texts W40 left (its decision 2 below and its
first finding), written as rows the same script applies, so V-E16's edit, its change record row and the procedure's quote are
applied together once and refused together on a second run. Read at set 31's lineage `3057ae43` (fnd/int31regen), where the
page's change record ends with W8's row and TP-SOLAR.md is as on main.

| File | Old | New | Basis |
|---|---|---|---|
| `v2/docs/HW-FW-CONTRACT.md`, section 10 (the change record, the page's last section) | W8's row "\| 2 (W8, L5-F14) \|" is the last row | one row appended after the V-E16 edit, `CR_ROW`: "\| 2 (Q-55, set 32) \| 6 October 2026 \| By record s32small for set 32 ...", in W8's form (three cells; the change, its basis, the wording before as dated history): V-E16's row 3 carries N1a's words at the place the register's R-176 row 3 carries them since set 31 (`b2564b59`), so rows 2 and 3 again equal the register's verbatim (L5-F09 d's invariant); nothing else in the row; R-240 drafted and not applied, no pass line changed, no claim widened; the wording before "U5's CSPIN to CSNIN within +-0.240 V, U21 turning Q12 off" | Q-55 (the coordinator's decision of 6 October 2026 15:22 CEST) and Q-65 |
| `v2/docs/test-procedures/TP-SOLAR.md`, section 8, after the quote that holds line 297 | (nothing: a pure insertion) | a dated lead-in "**Added 6 October 2026 (set 32, Q-55, quotes only):** ..." and a text quote of the register (`<!-- q src="v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md" -->`): "U5's CSPIN to CSNIN within +-0.240 V (under R-240, drafted, not applied: under 10 mV in magnitude, a layout check, L4E7-P0SOL.md section 5)"; the lead-in says L4-E7's list does not carry the words and that R-240 is not applied, so row 3 and the Row 3 pass line are unchanged | Q-65; tp_check.py's C3 (a text quote is found verbatim in its source) |
| `v2/ecad/tools/tests/test_w8l5.py` (through W40's `TEST_ADD`) | W40's Q-55 tree check of V-E16 | the same, then: Q-55's change record row once, after W8's, three cells, dated 6 October 2026, N1a's words once and the wording before quoted; TP-SOLAR.md quotes the register's annotated U5 line once as a text quote | a test of both rows |

**Line 297 is not a quote of V-E16 or of the register (the brief's premise, corrected; authority SESSION, W47, under the owner's
standing rule of 26 September 2026).** At `3057ae43` the line sits inside a TEXT quote of record l4e7's
`v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md` (R-176's acceptance, round 2, its line 742), which carries no N1a words; the
procedure's register quotes take the Acceptance cells of R-176, R-189 and R-174, and N1a annotated R-176's Item cell. So the quote is
verbatim now and stays verbatim after Q-55 (which does not touch record l4e7); adding the words inside it would fail
`tp_check.py`'s C3 (a text quote must be found verbatim in its source). Taken: the recommended option, the register's annotated
line as the procedure's own text quote right after it, with a dated lead-in, so the procedure carries the words V-E16 carries
after Q-55 without paraphrasing either source. Not taken: (a) leave the procedure as it is (it would not show the annotation
the register and V-E16 carry, the brief's intent); (b) re-point line 297's quote to the register (its six rows are L4-E7's
list; R-176's Acceptance quote already holds C4). Reversed by deleting the inserted lead-in and quote block (edit 6).

**The record that pins TP-SOLAR.md** is `v2/docs/test-procedures/tp_check.out` (its line 102, the sha256/16
`18325bbf0e24cf1d` at `3057ae43`, and the procedure's quote count line, "19 table, 3 text"); the brief's grep
`v2/docs/records/*/*.out` finds none, and no other file of the tree prints TP-SOLAR.md's sha256. It is NOT regenerated here;
set 32's chain regenerates it through `_bin/regen_out.py` after the script runs.

**The test that pins the change record's form.** test_w8l5's last assertion, `l1[-2].startswith("| 2 (W8, L5-F14) |")`, reads
the page at `W8_COMMIT` (8840adda) through `git_show`, not the tree, so it accepts the appended row unchanged (were W8_COMMIT
set to None it would read the tree and fail on Q-55's moved V-E16 line already, before this row). W40's script inserts its
Q-55 block above that assertion; W47's lines extend that block (the third row of the table above).

**Checked on a scratch clone (W47, 6 October 2026, removed afterwards):** a sparse clone (v2/docs, v2/ecad) of set 31's
`3057ae43` with fnd/s32small `44891f15` merged (clean). `--check` held every check and named four files (HW-FW-CONTRACT.md
f26757c7c5004cdd to 12b6ea059a68b5c5, test_w8l5.py 318fd7e85b72df85 to 9dba4249ee9d94cc, test_l5pwr.py a6c6dbf11e4a9e78 to
92b77706c28c3dd0, TP-SOLAR.md 18325bbf0e24cf1d to e750c424b544cff9); the run exited 0 and printed the page's sha256
12b6ea059a68b5c5f0eb4d67513283af2bd8a011f9e80bea7d047e5955b1e99a; a second run and a second `--check` exit 3; a tree with
only edit 6 applied is refused (exit 2, "half applied"); on this branch's own tree it refuses (exit 2, test_w8l5.py absent).
tp_check.py on the applied tree: exit 0, "RESULT: ALL PASS (10 procedures, 123 quotes, 17 TBDs; the bring-up page with 8
TBDs)"; its print differs from the committed tp_check.out in five lines (TP-SOLAR.md's pin, "4 text", "6 paths from v2/", the
index row's quote count 23, the RESULT line's 123 quotes).

run.py over 13 modules (W40's 11 that read HW-FW-CONTRACT.md, plus test_test_procedures and test_w3annex, which read the
procedures): before the apply `tests: 178 passed, 28 failed, 2 skipped`; after it `tests: 175 passed, 31 failed, 2 skipped`, the
three new failures all pins: `test_l5r2.t_r3_output_reproduced_and_every_finding_resolved FAIL l5r3_panel.out is not what the
reader prints`, `test_test_procedures.t_the_committed_out_is_what_the_script_prints FAIL tp_check.out is not what tp_check.py
prints` and `test_w24l4e9.t_the_four_typed_in_pins_equal_their_files FAIL v2/docs/records/l4e9/l4e9_power_path.py:75 pins
v2/docs/HW-FW-CONTRACT.md at f26757c7...`; with both PINS["hwfw"] re-pinned and tp_check.out and l5r3_panel.out regenerated
through `_bin/regen_out.py` on the clone, `tests: 178 passed, 28 failed, 2 skipped` with the failure list identical to the one
before (the 28: the clone's environment, no firmware tree, no vendor files, the registry's unheld documents, and
test_l5pwr.t_output_reproduced_byte_for_byte, l5r2's refusal and W20-18, all failing before the apply too). test_w8l5: 6 of 6
pass after the apply; test_test_procedures 14 of 14 after the regeneration; test_w3annex 10 of 10 throughout.

Mutations (on the applied clone, each restored): Q-55's change record row deleted fails test_w8l5 ("Q-55's change record row is
not once, after W8's"); its date changed fails it ("Q-55's row is not in W8's form"); the quote's words altered ("under 11 mV")
fail test_w8l5 ("TP-SOLAR.md does not quote the register's annotated U5 line once") and test_test_procedures'
t_the_checker_passes_on_the_tree (C3, "a text quote is not found verbatim"); the quote block deleted fails test_w8l5.

**What set 32's chain must do after the script (W40's list, with W47's addition):** re-pin `PINS["hwfw"]` in
`v2/docs/records/l4e11/l4e11_power.py:54` and `v2/docs/records/l4e9/l4e9_power_path.py:75` to the sha256 the script prints
(12b6ea05... on set 31's 3057ae43; the page moves by both the V-E16 edit and the appended row); re-key the l4e7 KEY; one
dependency pass re-pinning l4e11_power.out, l4e9_power_path.out, l5r2_interfaces.out, l5r3_panel.out, l8gnd_drafts.out and
l9t5_t10.out; and regenerate `v2/docs/test-procedures/tp_check.out` (`_bin/regen_out.py <tree> v2/docs/test-procedures/tp_check.py
v2/docs/test-procedures/tp_check.out`), which no other output depends on.

## Session decisions (authority SESSION, W40)

1. Q-55 as an apply script for set 32's merged tree (above).
2. No change record row added to HW-FW-CONTRACT.md section 10 for Q-55: the brief says nothing else in the row, N1a added none to
   the register, and the annotation carries its own provenance; the integrator may add one at set 32 (the tests that read the
   page do not require it). SUPERSEDED 6 October 2026 by the coordinator's Q-65: W47 added the row as edit 5 (above).
3. `h3/zip_size_estimate.py`'s docstring left as H3's dated record (above).

## Findings for other authors (not changed here)

- `v2/docs/test-procedures/TP-SOLAR.md:297` quotes row 3's U5 line without N1a's words; whether the procedure follows the
  register is record tp's question. ANSWERED 6 October 2026 by Q-65 (W47, edit 6): the line quotes record l4e7, verbatim; the
  register's annotated line is added as its own quote.
- `pack.yaml`'s reference rule for the H1.1 patches keeps the reason "moved out in H2 to keep the ZIP under max_zip_bytes", a
  dated statement about H2 that reaches REFERENCED-SOURCES.tsv; left as it is.

## Session decisions (authority SESSION, W47, under the owner's standing rule of 26 September 2026)

1. Both texts as edits 5 and 6 of W40's `apply_q55_ve16.py`, not a sibling script: the change record row belongs with V-E16's
   edit and the procedure's quote with both; one script gives one applied state and one refusal, where two would allow a half
   applied pair. Reversed by moving edits 5 and 6 into a sibling script that requires this one applied.
2. TP-SOLAR.md's line 297 left verbatim and the register's line added as its own quote (the section above).
3. The test of both rows added to W40's `TEST_ADD` block in test_w8l5 (no new module): the block already reads the page and
   the register for Q-55.
