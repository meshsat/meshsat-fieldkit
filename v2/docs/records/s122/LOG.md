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

## Round 3 (the answer to `checks/check-s122-2.md`: 1 blocking, 8 minor)

- 19:20 (one label for the round's work, read from `date` when this entry was written; the round began after the
  check's reading of 18:41 to 18:55) Check read whole and filed byte for byte as `checks/check-s122-2.md`.
  - B1: read on the netlists by `verdicts.py`'s new at-commit assertions: `U41`, `U51`, `U61` PB7 on `SDA` and PB6 on
    `SCL` on set 13 and at `458b2873`, `45bde541`, `95e078a1`, `a9f212c7` and `c5430071`, unconnected at `1f614233`;
    board B's `U513` to `U520` and `U530` to `U535` at `95e078a1` and `c5430071`, none at `45bde541`; `U519` and `U520`
    the display switches' enables; S-42 OPEN, CON-003 and CON-022 INCONCLUSIVE waiting on it. Rows DC-07 and DC-08
    written; both sentences BASELINE on them.
  - The method: every CONOPS.md sentence with absent, owed, not drawn or not connected is inventoried in any section
    and judged TRUE or BASELINE, or binds each such word to a phrase not about the circuit. Before (the committed
    `verdicts.out` at `83cb0640`): 14 such sentences, 1 TRUE, 7 BASELINE, 6 NOT DERIVABLE. After: 18, 3 TRUE, 11
    BASELINE, 4 NOT DERIVABLE (phrases bound), 0 STALE, 0 UNJUDGED. New from the sweep: section 7's D-17 row (board A's
    `U31` drawn since `458b2873`, row DC-09; the row written at `68bc9e8f`, CONOPS.md's first commit), section 7a's
    HOT-R1 row (added to DC-02), section 7a's BANK-R1 row (TRUE: the hub ports are as at `45bde541` and REQ-052 reads
    FAIL), section 2's need. Section 4e's `SLOT_EN` hold turned TRUE on the three boards' exact net members.
  - m7: the parser keeps wrapped items' continuation lines; the 11 merged texts judged again. m8: the count rule
    checks each count's cover; 29 judgements given a cover per count.
  - `apply_docs_s122_r3.py --check` and then its run on `83cb0640`'s three documents: 10 edits, 144 assertions held
    first; a second run refuses. Outputs regenerated: 862 sentences, 339 TRUE, 0 STALE, 38 BASELINE, 485 NOT
    DERIVABLE, 0 UNJUDGED, 2803 assertions; the base 808 sentences, 64 STALE.
  - Read and recorded as an observation, not changed: CON-003's and CON-022's evidence text against `R480`, `R500` at
    10k and `U513` to `U520` drawn on the netlist they are bound to.
- 19:23 Committed `89b9ac6b` behind the pre-commit PASSED line. Replay on a throwaway clone of it: the four outputs
  byte identical; `apply_docs_s122_r3.py` from `83cb0640`'s three documents gives the tip byte for byte and refuses a
  second run; `apply_docs_s122_r2.py --check` on `1594090e`'s documents reads 497 assertions (check-s122-2 m5);
  `apply_registry_s122.py` rebinds 20 records with round 3's entries and refuses a second run; `rules_lib.py
  requirements` 144 records, 0 errors, 0 warnings; the requirement and envelope tests 69 passed and 2 failed before the
  trace page's render, 71 passed after; `close_s122.py` refused the fixture while staged, closed S-122 with it
  committed (862 sentences, 0 STALE, 0 UNJUDGED; CFL-016 PASS; S-123 and S-42 open) and refused a second run; after it
  0 errors, 71 passed, `claims_check` PASS 91 of 91. The clone is deleted.

## Round 4 (set 14: makers' part numbers; `fnd/s122c` from `1bafab8c`)

- 20:52 Worktree `s122c` on `fnd/s122c` from `1bafab8c` (set 14, `fnd/int15`). Read whole: S-122's title in the
  registry at `1bafab8c` (its three set 14 additions), `records/int15/checks/check-int15-1.md` to `-3.md`, the fourth
  check of set 14 (the integrator's `CHECK-4.md`, not filed), `checks/check-s122-3.md`, and `close_s122.py`'s
  `gate_set14`.
- 21:16 (one label for the round's work up to the README, read from `date`):
  - `s122lib.partnos`: makers' part numbers by shape (and in cited sheets' file names), returned by `names()` under
    `parts`; a table cell carries its row label. `verdicts.check_parts` judges each against the six netlists' part
    values (a part on no netlist, or not on the one board a sentence and its row name, needs `parts_ok`; a NOT
    DERIVABLE judgement is never an excuse). New assertion form `PDF:` (pdftotext). The absent rule's wordings widened
    (check-s122-3 m2). First run: 951, then 986 sentences with 149 UNJUDGED and 11 STALE before judging.
  - `apply_docs_s122_r4.py --check`, then its run on `1bafab8c`'s documents: 12 edits, 51 assertions held first; a
    second run refuses. V2-SPEC.md lines 47, 82, 84, 86 and correction 34; OPERATING-ENVELOPE.md lines 77 and 83 and
    a correction note (the LM5069's range from `ti/ti-lm5069.pdf` SNVS452G 7.3, the TE socket's from
    `m2/te-2199119-m2-b-key.pdf`, both read by pdftotext); row DC-10; the int15 docstring (q4).
  - Every new or changed sentence judged in `judgements.py` (round 4 block): 985 sentences, 410 TRUE, 0 STALE, 40
    BASELINE, 535 NOT DERIVABLE, 0 UNJUDGED, 3219 assertions. `verdicts-set14.out` (the documents at `1bafab8c`): 7
    STALE, each corrected; `verdicts-base.out` (`e57a7365`): 72 STALE.
  - `close_s122.py`'s `gate_set14` rewritten (probes made up at run time, sentences found by what they say and TRUE,
    the closing check's marker with their lines). On this tree it refused `check-s122-3.md` at the marker, and a
    fixture with the marker and no lines listing the six lines.
  - `apply_registry_s122_r4.py` written (rebinds against `1bafab8c`, CFL-016's entry and note, S-122's sentence, the
    envelope re-pin); its two new sentences pass claims_check's screen.
- 21:20 Committed `e5fdf670` behind the pre-commit PASSED line. Replay on a throwaway clone of it: the six outputs byte
  identical; `apply_docs_s122_r4.py` from `1bafab8c`'s four files gives the tip byte for byte and refuses a second run;
  the gate refused ten mutants (a rigged finder, the documents at `1bafab8c`, TMDS351 with the row relabelled, the
  LM5176 back in the E6 row "all under A22", a WM8731 codec, a Molex B-key row, a TRACO TEN 60 row, the B16 row judged
  HISTORY, the B16 row without its U3 and U4 assertions, a check without the marker);
  `apply_registry_s122_r4.py` rebound 5 records and refused a second run; `rules_lib.py requirements` 144 records, 0
  errors, 0 warnings; the tests 69 passed and 2 failed before the trace page's render, 71 passed after; the closure
  refused the fixture while staged, closed S-122 with it committed (CFL-016 PASS; S-42, S-123, S-124 open) and refused a
  second run; after it 0 errors, 71 passed, `claims_check` PASS 91 of 91. The clone is deleted.

## Round 5 (the answer to `checks/check-s122-4.md`: 1 blocking, 3 minor)

- 21:33 Check read whole (the checker's report, filed byte for byte as `checks/check-s122-4.md`).
- 21:48 (one label for the round's work, read from `date`):
  - `verdicts.check_roles`: a part named in a role is read against the designators whose values carry it (forward:
    the noun, with `ROLE_SYN`; reverse: a specific qualifier stated by another designator; rails: a plain part list
    after a rail phrase against each converter or monitor of that rail's net); `roles_ok` binds a role to an own
    assertion on a designator that carries the part. On the documents at `edead832` it reads V2-SPEC.md lines 81 and 84
    STALE (`verdicts-r4.out`, which also carries lines 83 and 86 as STALE by the check's m2 and m3).
  - `s122lib.is_partno` widened (the check's m1 list, and all-digit numbers after a maker's name) with exclusions by
    shape; every semiconductor, crystal and relay part number of the six netlists' values is read.
  - `apply_docs_s122_r5.py --check`, then its run: 5 edits, 33 assertions held first; a second run refuses.
  - Judgements for the new and corrected texts: 1005 sentences, 420 TRUE, 0 STALE, 40 BASELINE, 545 NOT DERIVABLE, 0
    UNJUDGED, 3295 assertions.
  - `close_s122.py`'s gate: the netlists' part numbers in the probe, the round 5 rows in (b), the role fixtures in
    (e). On this tree it passed (a), (b) and (e) three times and refused a marker-only fixture at (c), listing
    V2-SPEC.md lines 47, 81, 82, 83, 84 and 86 and OPERATING-ENVELOPE.md lines 77 and 83.
  - `apply_registry_s122_r4.py` re-issued for the round 5 diff (its REF, CFL-016's entry, S-122's sentence); the new
    texts pass claims_check's screen.
- 21:51 Committed `8d7874f5` behind the pre-commit PASSED line. Replay on a throwaway clone of it: the seven outputs
  byte identical; `apply_docs_s122_r5.py` from `edead832`'s V2-SPEC.md gives the tip byte for byte and refuses a second
  run; the gate refused eight mutants (round 4's finder, the role rule off, V2-SPEC.md as at `edead832`, the TPS22810
  gate-bias switch, the AP64500 list, the magnetometer, sixteen LEDs, a check without line 81);
  `apply_registry_s122_r4.py` rebound 5 records and refused a second run; `rules_lib.py requirements` 144 records, 0
  errors, 0 warnings; the tests 69 passed and 2 failed before the trace page's render, 71 passed after; the closure
  refused the fixture while staged, closed S-122 with it committed (CFL-016 PASS; S-42, S-123, S-124 open) and refused
  a second run; after it 0 errors, 71 passed, `claims_check` PASS 91 of 91. The clone is deleted.
