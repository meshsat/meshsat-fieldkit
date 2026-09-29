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
