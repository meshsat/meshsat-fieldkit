DONE: the l4e7 results cache KEY holds the numbers it reads of l4e11_power.out, not the file's bytes (W61); the adoption prepared on W64's conditions (W67, section 7: F-1, F-4, the KEY check's new version beside the old). NOT DONE: the re-key and the regeneration (the coordinator's). NEXT: one re-key on a rented box at this branch's tip, the KEY check swapped in, l4e7_p0sol.out and its dependents regenerated.

# Record L4-E7's results cache at the L4-E11 boundary (W61, 6 October 2026, MESHSAT-1357)

Prototype design records: nothing in this kit has been built, bought, powered or measured. This page describes a change of the
record's cache tooling, not of any computed figure.

**Request.** The owner's workflow request MESHSAT-WORKFLOW-IMPROVE-20261006-1829-01, item 2 (pilot structured numerical
dependencies at the demonstrated l4e11 output boundary, keep full evidence digests, prove that prose-only changes reuse, that
meaningful changes invalidate and that missing or corrupt inputs fail closed); the constitution's section 8 (a cache key covers model
code, relevant inputs and material tool versions; unrelated prose need not invalidate).

**The demonstrated defect.** `l4e7_stage_settings.py` read `l4e11_power.out` whole and its `key_parts()` keyed the file by its whole
sha256, so a change of the input digests that file PRINTS moved the KEY: on 6 October 2026 the file went from a2089b3f6682 (d83d9f2d)
to 36141414a1b6 (31928583) by two printed pin lines only (`hwfw` HW-FW-CONTRACT.md, `arch` L4-POWER-ARCHITECTURE.md) and still
forced a box re-key of the solver (30 to 50 core-minutes). Reading of the history (this branch, `git log -- l4e11_power.out`): 61
committed revisions from cbf8bcb9 (2 October 2026, the round that first printed these sentences) to 31928583 carry ONE set of the
sixteen numbers below; the two earlier revisions do not print them.

## 1. What the record reads of l4e11_power.out (static trace, confirmed on the committed cache)

All reads happen in compute(), on the whitespace-flattened text, with the six patterns now held in `L4E11_NUMBERS` (verbatim the
patterns compute() used before). Line numbers: `l4e11_power.out` at 31928583, `l4e7_stage_settings.py` on this branch.

| Name | Values (31928583) | l4e11_power.out | Use in l4e7_stage_settings.py | In the cached R |
|---|---|---|---|---|
| uv | 7.87 / 8.14 / 8.44 V (UVLO rise) | line 252 | L11["uv"] (2695); uv[2] in the window predicate (3348) and section 10's text (4377) | remedy/L11/uv, remedy/b6/GD/uv |
| uvf | 7.46 / 7.66 / 7.95 V (UVLO fall) | line 252 | uvf[0]: st6 (2962), the guard witnesses (3157, 3164), b6 uvf_lo (3177), text (4377, 4667) | remedy/L11/uvf, b6/uvf_lo, b6/W/vFmin |
| slew | 17.28 / 20.71 / 24.65 V/ms | line 263 | slew[2] slew_hi (2810), slew[0] t_slew (2813), text (4401) | remedy/L11/slew, b6/GD/slew |
| inp | 7.23 V (INP high from DC_P) | line 262 | L11["inp"] (2695), carried in GD | remedy/L11/inp, b6/GD/inp |
| scp | 10.36 / 12.04 / 13.87 A | line 253 | scp[0] scp_lo (2849) in the cut-off predicate (3340); scp[2] isc (2960, 3143, 3155) | remedy/scp_lo, b6/G6/isc, b6/G1/isc; 12.04 parsed only |
| ocp | 6.364 / 6.8 / 7.136 A | line 253 | ocp11 (2850), ocp[0] ocp_lo: t_over (2853), the window (3349), text (4335, 4401, 4496) | remedy/ocp11, remedy/ocp_lo |

Sixteen values; fifteen land in the cached results, the short-circuit threshold's typical (12.04 A) is parsed and order-checked only.
No other read of the file exists: compute() mentions neither its name nor its path (test d); `apply_gen_sch_e_entry.py` of record
l4e11 is a separate input and keeps its whole digest in the KEY's files part.

## 2. The extractor

`l4e11_numbers(text=None, top=None)` returns `{name: [values]}`; compute() takes its numbers from it (one call), and the KEY hashes
its canonical JSON (`l4e11_canonical()`: names sorted, compact separators, float reprs). It refuses with exit 3 and a message naming
the value and the file, never a default, when: the file is missing; the file is unreadable (not UTF-8); a value is missing (its
sentence absent, or truncated away); a value is duplicated (its sentence printed more than once); a value is unparsable (not a
float); a value is out of its declared form (not a plain decimal `\d+(\.\d+)?`, or a least / typical / greatest triple that
descends); or the declared count and the pattern disagree. Each sentence is found by its pattern with every number widened to any
token, so a malformed number refuses as malformed instead of letting another sentence be read in its place; the narrow pattern
must then read the same sentence.

## 3. The KEY and the evidence

- `key_parts()`: the files part no longer holds `v2/docs/records/l4e11/l4e11_power.out`; a new part `l4e11_numbers` holds the sha256
  of the canonical JSON (today 2a417efc93cf2433..., equal at d83d9f2d and 31928583). Every other part unchanged: src (which now
  reaches l4e11_numbers, L4E11_NUMBERS, NUM_FORM and L4E11_OUT through compute()), the other 177 files, scans, solver, python,
  pdftotext.
- `evidence_part()`: written by every run that writes the cache, as the top-level field `evidence` of
  `l4e7_stage_settings.results.json` beside `key`: `{"files": {"v2/docs/records/l4e11/l4e11_power.out": <its sha256>},
  "l4e11_numbers": <the extract>}`. It never enters the KEY. `load_cache()` renders from no cache that lacks it. The file's whole
  digest also stays pinned where it was: l4e9_power_path, l5pwr, l7pwr, l9pwr, l9stk and l4e7_p0sol print it in their outputs.
- `main()`: the extractor runs at every run (after the lead guard), so a missing or malformed number refuses before the cache is read
  or the solver reached.

## 4. Tests (`v2/ecad/tools/tests/test_l4e7_cachekey.py`, no solver, nothing written into the tree)

(a) prose only (the two pin lines of 6 October, the file re-wrapped onto one line, the OV cut-off this record does not read): KEY
equal, while the whole-file KEY of before moves; (b) each of the sixteen values moved inside its order changes the extract's digest,
and one moves the KEY with only its l4e11_numbers part; (c) eight corruptions refuse with exit 3 at the extractor, the KEY, the cache
reader and a run (with and without --recompute) before the solver; (d) a changed pattern, declared form or use moves the source part,
a comment above the extractor does not, and compute() reads the file only through the extractor; (e) the evidence digest is the
file's sha256, a run writes it beside the KEY, a prose change keeps that cache, a cache stripped of it is refused; (f) the file at
d83d9f2d and at 31928583 reads to equal canonical JSON and an equal KEY. test_l4e7's cache test and its `_link_key_inputs` are
restated for the new parts (they read the committed cache, so they hold after the re-key).

## 5. Owed at adoption (the coordinator)

1. ONE re-key of the cache on a rented box (the committed results.json reads MISMATCH under the new definition: its parts lack
   `l4e11_numbers` and `evidence`, and compute()'s source moved). The results are expected identical (the same floats feed compute()),
   so `l4e7_stage_settings.out` should regenerate byte for byte.
2. `_runs/int30/l4e7_key_check.py`: add `"l4e11_numbers"` to its tuple of part names (line `moved = [p for p in ("src", "files", ...`),
   or a move of the numbers alone prints "parts moved: none listed". Its MATCH or MISMATCH verdict needs no change.
3. Then `l4e7_p0sol.out` (it pins this script's and the cache's sha256; before the re-key its 0a refuses with exit 4, the KEY differing
   in more than l4e11_power.out) and the outputs that pin it, in the usual dependency pass.

## 6. SESSION decisions (under the owner's standing rule of 26 September 2026)

- `authority: SESSION`. The extract holds all sixteen values the six patterns read, including the short-circuit typical (12.04 A) that
  no figure uses. Reason: the pattern reads the triple and the order check needs all three; a change there can only cost a re-key,
  never leave a stale cache. Reverse: drop the value from `L4E11_NUMBERS`' scp row and from the triple check.
- `authority: SESSION`. compute() reads its numbers through the extractor (rather than the extractor mirroring compute()'s reads), so
  the KEY's numbers are by construction the numbers computed on. Reason: no second parser to drift. Cost: compute()'s source moved, so
  the one re-key at adoption is a solver run, not a KEY rewrite. Reverse: restore the six g3() reads of 31928583.
- `authority: SESSION`. A cache without its evidence field is never rendered from. Reason: the whole digest is never dropped. Reverse:
  remove the evidence check from `load_cache()`.

## 7. Adoption prepared (W67, 6 October 2026, 19:30 to 20:00 CEST)

W64 read WP-B at 849e66c7 independently (an AI review, not a qualified one; `_runs/claude/w64revkey/REPORT-AS-RECEIVED.md`) and
found it fit for adoption on four conditions, with four findings. This branch carries everything but the re-key and the
regeneration. Nothing was re-keyed, no `_R()` test of test_l4e7 was run and no `.out` was regenerated.

| W64 | What it asks | Done on this branch | What remains (the coordinator's) |
|---|---|---|---|
| condition 1 | one re-key on a rented box; until then no `_R()` test of test_l4e7 on the runner | nothing to do here; no `_R()` test run | the re-key at this branch's tip (not at 849e66c7: F-4 moved the extractor's source, so the KEY's src part moved again) |
| condition 2, F-2's second half | `l4e11_numbers` in the KEY check's part list; its exit 3 documented | the check is runner-local (`_runs/int30/l4e7_key_check.py`, outside git) and in use by set 31's dependents pass, so by the coordinator's correction of about 19:30 its new version is written beside it as `_runs/int30/l4e7_key_check.py.new` (sha256 26dfef093053c9e0) with its fixture test `_runs/int30/test_l4e7_key_check.py` (05279611e823b9f6). The part list gains `l4e11_numbers` (and then any other part either side holds, sorted); a move of the numbers alone prints `parts moved: l4e11_numbers` with one `numbers <name>: <committed> -> <now>` line per moved value group and no file line; exit 3 (the record's refusal before any KEY) is documented beside 0, 1 and 2 and its message quoted on stderr in a line that starts `l4e7 key check REFUSED (exit 3)`; the first line and the file lines keep the format `_bin/preflight.py` and `_runs/int32/chain.sh` parse | swap it in at set 32's adoption (`mv l4e7_key_check.py.new l4e7_key_check.py` in `_runs/int30/`) |
| condition 3, F-1 | regenerate `l4e7_p0sol.out` and its dependents, its 0a sentence restated | `l4e7_p0sol.py`: 0a's reading is `key_state()` and its sentence `para_0a()`. The sentence states only what the KEY check proves and the cache's own fields record (its parts' Python and pdftotext versions; beside the KEY the evidence's sha256 of `l4e11_power.out`, the same bytes as the tree's or a prose-only difference); the typed history (who re-keyed, on what box, after which rounds) and the constant `KEY_AT` are gone. A move of the part `l4e11_numbers` alone refuses (exit 4) naming that part and the moved numbers (`inp 7.23 -> 7.24`); any other stale state names each part plainly; a holding KEY without the evidence field refuses. Before the re-key the script refuses with: "the cache's KEY differs from this tree in: the file v2/docs/records/l4e11/l4e11_power.out (a2089b3f6682d7fd in the cache's KEY, not in the KEY's files part here); the part l4e11_numbers (...); the part src; the cache is stale for this tree: re-key it ...". In memory, served a cache keyed on this tree (nothing written), it exits 0 and differs from the committed `.out` in the pin of `l4e7_stage_settings.py` and the 0a paragraph only | the regeneration below |
| condition 4, F-2's first half | the preflight's moved-files blind spot | already done by W60 in `_bin/preflight.py` (`KEY_PART_FILES` maps the part `l4e11_numbers` to `l4e11_power.out` for `--key-expect`; an exit outside 0, 1 and 2 refuses in every mode); the new check's test t7 reads both through `check_key` | none |
| F-3 | "non-increasing" against the code's "descends" | checked: section 2 above and the extractor's message both say "descends", as the code does (`vals[0] <= vals[1] <= vals[2]`, an equal triple accepted); the queue's "non-increasing" was the coordinator's wording; no file edited | none |
| F-4 | `\d` matches Unicode digits | every regular expression call of `l4e11_numbers()` passes `re.ASCII`; a consumed number written in fullwidth digits (U+FF10 to U+FF19), in Arabic-Indic digits (U+0660 to U+0669) or with one fullwidth digit among ASCII ones now refuses (exit 3, out of its declared form) where 849e66c7 read it as 7.23 (`test_l4e7_cachekey` t_g) | none (the re-key covers the moved source) |

**The regeneration after the re-key** (dependency order; the coordinator's `_runs/int31/dependents.sh <worktree> <log> <base>` does it:
regen_targeted, `repin_l4e9.py`, regen_targeted again, the KEY-only check):
1. The re-key on a rented box at the adoption tip: `l4e7_stage_settings.py --recompute`, its results file then carrying the part
   `l4e11_numbers` and the field `evidence`; `l4e7_stage_settings.out` is expected byte for byte (the same floats feed compute()).
   The KEY check then reads MATCH.
2. `python3 _bin/regen_out.py <worktree> v2/docs/records/l4e7/l4e7_p0sol.py v2/docs/records/l4e7/l4e7_p0sol.out` (it pins the record's
   script, its output and its results file; the 0a paragraph changes as above).
3. The outputs that pin p0sol (`git grep` of its path and of its digests at 849e66c7, 34541a3d3a6c800a for the script and
   7d0ec93f47ae7e62 for the output): `l4e9_power_path.py` line 180 (the typed pin `l4e7p0`, the output's full sha256: `repin_l4e9.py`)
   and `l4e9_power_path.out` line 106; `l9t5_connected.out` line 23 (the output) and line 26 (the script, stale already on this branch:
   `l4e7_p0sol.py` is now d79ffb469ca00d5d). Then their own dependents in the same pass (`l5pwr_contracts.out` pins
   `l4e9_power_path.out` at line 12; the l9t5 cascade).
4. Then the tests that read them: test_l4e7's two p0sol output tests (`t_p0sol_committed_out_is_what_the_script_prints`,
   `t_p0sol_the_inputs_it_pins_are_this_trees_files`), test_l4e9, test_l9t5, and the `_R()` tests of test_l4e7 once the KEY holds.

**Tests as run on the runner** (no solver; one module at a time; `TMPDIR` in the session's scratch):
- `test_l4e7_cachekey.`: `tests: 7 passed, 0 failed, 0 skipped` (W61's six and t_g).
- `test_l4e7.t_p0sol`: `tests: 12 passed, 2 failed, 0 skipped; failed: test_l4e7.t_p0sol_committed_out_is_what_the_script_prints,
  test_l4e7.t_p0sol_the_inputs_it_pins_are_this_trees_files` (both owed to the re-key, as W64 found at 849e66c7; the new
  `t_p0sol_0a_states_the_caches_own_fields_and_names_a_numbers_only_move` passes, and fails at 18982112 with no `key_state`).
- `test_public_hygiene.`: `tests: 4 passed, 0 failed, 0 skipped`.
- `_runs/int30/test_l4e7_key_check.py` (outside git): `tests: 7 passed, 0 failed, 0 skipped` with the new check; with the current
  `l4e7_key_check.py`: `tests: 3 passed, 4 failed, 0 skipped` (t2 "parts moved: none listed", t4 no quoted refusal line, t6 no
  exit 3 in the docstring, t7 the preflight's `--key-expect` refused). On set 31's tree (aa332280, read-only, `python3 -B`) the new and
  the current check print the same `l4e7 KEY MATCH b8fc6fe2d285112c`, exit 0, and the tree's status is unchanged; on this branch
  (the old-definition cache) the new one prints `parts moved: src, files, l4e11_numbers`, the file line and "the committed cache
  carries no numbers beside its KEY".

**SESSION decisions** (`authority: SESSION`, under the owner's standing rule of 26 September 2026; none is an owner question):
- The KEY check lists, after its seven named parts, any further part either side holds (sorted), so a future part is never
  reported as "none listed". Reason: W64's F-2 named exactly that failure for the part added here. Reverse: list the tuple only.
- The KEY check prints one `numbers` line per moved value group, read from the committed cache's evidence. Reason: the moved figure
  is the question a numbers-only move raises; neither `preflight.py` nor `chain.sh` reads such a line (they read the first line and
  the `file` lines). Reverse: drop the block.
- `l4e7_p0sol.py` refuses a holding KEY without the evidence field. Reason: the record's own `load_cache()` never renders from such a
  cache, and 0a's sentence names the evidence. Reverse: drop the third refusal of `key_state()`.
- `re.ASCII` is passed to all four regular expression calls of the extractor, the widened pattern (`\S`, no `\d`) included, so the
  flag is uniform; after `flat()` no Unicode whitespace remains, so `\S` reads the same. Reverse: drop the flag from that call.
