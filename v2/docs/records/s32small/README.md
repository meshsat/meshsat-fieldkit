DONE: Q-53 (the cap, committed dabfe4ca) and Q-55 (as apply_q55_ve16.py for set 32's merged tree). NOT DONE: nothing of the brief. NEXT: set 32's integrator runs apply_q55_ve16.py after set 31's promotion, re-pins, re-keys.

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

## Session decisions (authority SESSION, W40)

1. Q-55 as an apply script for set 32's merged tree (above).
2. No change record row added to HW-FW-CONTRACT.md section 10 for Q-55: the brief says nothing else in the row, N1a added none to
   the register, and the annotation carries its own provenance; the integrator may add one at set 32 (the tests that read the
   page do not require it).
3. `h3/zip_size_estimate.py`'s docstring left as H3's dated record (above).

## Findings for other authors (not changed here)

- `v2/docs/test-procedures/TP-SOLAR.md:297` quotes row 3's U5 line without N1a's words; whether the procedure follows the
  register is record tp's question.
- `pack.yaml`'s reference rule for the H1.1 patches keeps the reason "moved out in H2 to keep the ZIP under max_zip_bytes", a
  dated statement about H2 that reaches REFERENCED-SOURCES.tsv; left as it is.
