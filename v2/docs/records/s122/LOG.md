# Stream s122 log (29 September 2026, CEST from `date`)

- 17:01 Brief and worker rules read. Worktree `fnd/s122` created from `e57a7365`. Read S-122 and CFL-016 in the
  registry and the three filed checks `check-int13-2.md`, `-3.md` and `-4.md`.
- 17:05 to 17:10 `s122lib.py` (parser, finder, scope) and `inventory.py`: 580 sentences on the first count. The
  netlists read are set 12's (A `6c40250c47195ebb`, B `3ef9b8c49a01b728`, C `87b69472ac83ca5a`, D `a2d48972d171aad1`,
  E `2ed95a0e8069ebf8`, P `20c7b0795593d761`), the ones CFL-016 is bound to.
- 17:10 to 17:20 `verdicts.py` (names, citations, assertions). Its first run flagged the undated generator citations
  (PANEL.md 155 and 156, ASSEMBLY.md section 4 and 8) and the removed parts (`U{s}11`). Read the named documents in
  scope and the netlist facts behind them. Found beyond the three checks' list: CONOPS.md's and V2-SPEC.md's device-rail
  converters (`+3V3_DEV` is board B's `U25`, and was at `45bde541`), V2-SPEC.md line 73's fans, ASSEMBLY.md's dock
  contacts (EQ-16 and w4ae), OPERATING-ENVELOPE.md's and TEST-PLAN.md's HOT-R1 sentences, CONOPS.md 4f.
- 17:20 Checkpoint commit `bdf88002` (tools and the first base inventory).
- 17:20 to 17:35 `judgements.py` for every sentence, `apply_docs_s122.py` (43 passages; `--check` first). Two
  misjudgements of mine found by the scripts and corrected: PANEL.md's "Open:" sentence was outside the finder (the
  finder now knows "load switches" and "back-feed"), and I had judged the D-05 sentence beside it STALE; widening the
  finder to rails and "as generated" added 32 sentences, all judged. Assertion slips of mine that the script refused
  (U7's pin for RB_FLT, U10's GPIO17 by function name) were fixed in the judgements, not in the documents.
- 17:35 Base outputs regenerated with `S122_AT=e57a7365`: 599 sentences, 34 STALE. Documents corrected, outputs
  re-run: 605 sentences, 0 STALE, 0 UNJUDGED. Commit `cb446b03`.
- 17:35 to 17:44 `apply_registry_s122.py` and `close_s122.py`, replayed on a scratch clone of the branch (never in this
  tree). The first rebind reason said every changed line held a STALE sentence, which was not true of V2-SPEC.md
  lines 35 and 268 to 278 nor of CONOPS.md's 4e header; the reason is now read from the sentence sets of the two
  versions and the two verdict files. The CFL-016 entry now names the three passages the base verdicts did not call
  STALE. Replays: `rules_lib.py requirements` 0 errors, `test_envelope_data` 6 passed, `test_requirements` 65 passed
  after the trace page is re-rendered.
- 17:44 README and this log.

No box, no agent, no other model. No gate, `rules_status.py` or `rules_render.py` was run in this tree; the render and
the tests ran only in the scratch clone, which is removed.

## Round 2 (29 September 2026, CEST from `date`)

- 18:13 The coordinator's message and the independent check of round 1 read (`checks/check-s122-1.md`, filed byte for
  byte from the checker's `CHECK.md`): not mergeable, B1 to B3 and m1 to m12, all 43 corrections read true.
- 18:14 `fnd/int14` (`bd1cbb07`) merged at `4d3a9708`, no conflict: board C's netlist moves to `c9f7394594201045`,
  the registry gains S-122's set 13 addition and S-123.
- 18:15 to 18:24 `s122lib.py`: CONOPS's section 4 whole with 4a to 4f, ASSEMBLY's section 2 whole, EMCON.md 0a.1 and
  the status page's section in scope; EMCON and spelled counts of parts in the finder (a first count pattern took
  "3 V switch" and "16 SO land" as counts, and was narrowed to spelled counts). `verdicts.py`: the BASELINE verdict,
  the count rule, count, registry and file assertions. `apply_docs_s122_r2.py`: CONOPS restored to `c5430071` (byte
  for byte, needs table unchanged), EMCON.md 0a.1 and the status page written, 16 passages; three assertion slips of
  mine (U553's value text, U11's supply pin, the E22's MISO pin) refused by the script and fixed, and the QMX's `F3`
  added before the text was committed. Commit `c263ddce`.
- 18:24 to 18:29 Judgements for the 280 new and 82 count sentences; the round 1 judgement of CONOPS 4e's "the TX
  lamp act without it" (TRUE) withdrawn for BASELINE (B3). Base and after re-run.
- 18:30 to 18:34 `apply_registry_s122.py` re-issued (20 records, the CONOPS restore's reason, the part overlap per
  record, the baseline entry); `close_s122.py` (HEAD blob test, scope wording, the baseline checks). Replays on a
  scratch clone, removed after. Commits `fdf713d4`, `53292087`.
- 18:35 README, this log, the check filed.

No box, no agent, no other model. No gate, `rules_status.py` or `rules_render.py` ran in this tree.

## Rebuild on the promoted set 13 (29 September 2026, CEST from `date`)

- 18:37 The coordinator's message: `fnd/int14` was rewound (`bd1cbb07` dropped) and set 13 promoted as main `32f26b41`,
  milestone `b874b744`; the registry's S-122 set 13 sentence gains its closing clause and S-123 is reworded; board C's
  netlist and every document are the same. `fnd/s122b` created from `b874b744` in its own worktree; the seven stream
  commits cherry-picked in order with the owner's flags (the merge `4d3a9708` left out), no conflict, each commit's
  diff reading PASSED on the pre-commit check.
- 18:38 `inventory.py` and `verdicts.py` re-run on `b874b744`'s tree, and with `S122_AT=e57a7365`: all four outputs
  byte identical to the committed ones (849 sentences, 0 STALE, 0 UNJUDGED; the base 60 STALE), so no output is
  regenerated. No script asserts S-122's or S-123's wording: `apply_registry_s122.py` appends its correction to
  whatever title the registry holds and checks it reads back; `close_s122.py` reads the title as it is. Changed: the
  round 2 document script's base commit (`4d3a9708`, not an ancestor here, to `1594090e`, whose CONOPS.md is the same
  file), and the dropped merge named in the registry script's docstring and in the README.
- 18:39 to 18:40 Replay on a throwaway clone of `ede23557`: the four outputs byte identical; `apply_docs_s122_r2.py`
  refuses a second run; `apply_registry_s122.py` rebinds 20 records, keeps S-122's promoted text with its closing
  clause and appends the n3 and n4 correction after it, and refuses a second run; `rules_lib.py requirements` 144
  records, 0 errors, 0 warnings; `test_envelope_data` 6 passed; `test_requirements` 65 passed after the trace page's
  render; `close_s122.py` refused the fixture while only staged, closed S-122 with it committed (not filed), CFL-016
  PASS, S-123 still open, and refused a second run; after it `rules_lib.py requirements` 0 errors and
  `test_requirements` with `test_envelope_data` 71 passed. The clone is deleted.
