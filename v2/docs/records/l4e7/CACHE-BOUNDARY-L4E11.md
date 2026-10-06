DONE: the l4e7 results cache KEY holds the numbers it reads of l4e11_power.out, not the file's bytes (W61). NOT DONE: the re-key (the coordinator's, at adoption). NEXT: one re-key on a rented box, then l4e7_p0sol.out and the KEY-check script's part name.

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
