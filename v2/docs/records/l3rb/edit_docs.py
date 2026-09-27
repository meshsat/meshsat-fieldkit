"""The handover pages after the re-check of layer 3's re-baseline (27 September 2026, MESHSAT-1357, branch fnd/l3rb).
Run from the repository root on 2c12be91 after apply_recheck.py; every edit asserts the text it replaces or extends.

The re-check (v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md, an AI check) finds B-1 CLOSED at 2c12be91, so:
- v2/docs/handover/LAYER-STATUS.md: layer 3 COMPLETE in the H2 section's row and in its integrator line, in the commit
  that files the re-check, on the review records and the two targeted checks; its package is the next snapshot, H3.
  The page's two summary sentences say so after H2, whose files carry layer 3 IN_PROGRESS.
- v2/docs/handover/ENGINEERING-QUESTIONS.md: EQ-28 and EQ-30 answered, EQ-29's package for layer 3 named as H3.
"""
import subprocess

head = subprocess.run(["git", "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
assert head == "2c12be91", head
REC = "v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md"
RECN = "`%s`" % REC


def edit(path, pairs):
    t = open(path, encoding="utf-8").read()
    t0 = t
    for old, new in pairs:
        assert t.count(old) == 1, "%s: anchor found %d times: %r" % (path, t.count(old), old[:90])
        assert old != new
        t = t.replace(old, new)
    assert t.count(chr(0x2014)) == t0.count(chr(0x2014)), "em dash added"
    assert t != t0
    open(path, "w", encoding="utf-8").write(t)
    print("edited %s (%d edits)" % (path, len(pairs)))


LS = "v2/docs/handover/LAYER-STATUS.md"
ROW3_OLD_START = "| 3. Requirements | IN_PROGRESS | `pcb_requirements.yaml` validates (144 records, 0 errors, 0 warnings) and reads `baseline_state` READY_FOR_REVIEW_B:"
ls = open(LS, encoding="utf-8").read().split("\n")
rows = [l for l in ls if l.startswith(ROW3_OLD_START)]
assert len(rows) == 1
ROW3_OLD = rows[0]
assert ROW3_OLD.endswith("GND-002 unruled. Owner: the integrator as registry writer |")

ROW3_NEW = (
    "| 3. Requirements | **COMPLETE** in the commit that files " + RECN + " (after H2, branch `fnd/l3rb`; the H2 "
    "files carry it IN_PROGRESS) | `pcb_requirements.yaml` validates (144 records, 0 errors, 0 warnings) and reads "
    "`baseline_state` BASELINED at `a54b793b`: S-80's wording fix in `a54b793b` (CON-010's newest entry ends FAIL on "
    "W3T-F1, the header names `79963b3b`'s re-take on CON-010 and REQ-044, the trace page re-rendered; S-81 added) and "
    "the baseline in `2c12be91` (S-51, S-78 and S-80 closed; `v2/docs/records/l3rb/rebaseline_difference.out`, ALL "
    "ASSERTIONS HOLD). Review records, each an AI review or check, all five in `baseline_reviews` by sha256/16: Review B "
    "(`REVIEW-B-LAYER-3-2026-09-27.md`), the release check (`REVIEW-LAYER-3-RELEASE-2026-09-27.md`, NOT COMPLETE on R1 "
    "to R5, all answered since), the second release check (`REVIEW-LAYER-3-RELEASE-2-2026-09-27.md`, NOT COMPLETE on "
    "the procedural B-1 and B-2), the narrow verification (`TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`, "
    "`ae70b1a7811ecea1`: B-1 NOT_CLOSED on one unstated difference) and the re-check "
    "(`TARGETED-RECHECK-LAYER-3-2026-09-27.md`, `7831358b96b6f5ca` as filed: B-1 CLOSED at `2c12be91`, its three remedies, the "
    "baseline, the closures and the absence of any other registry difference each PASS). A record closure: it closes no "
    "electrical defect. The versioned package, acceptance item 3.18: the next snapshot, H3 (S-79, EQ-29) | nothing for "
    "the layer's own purpose but its package: H3, cut from the pushed commit that carries this row, closes S-79 and "
    "EQ-29 (the integrating session). Carried, not holding it: the release-2 record's minors n2 to n9 and the first "
    "check's m1 to m10, with both records' section 6 notes; REQ-077 FAIL until HOT-R1 (S-57); GND-002 unruled (layer 4); "
    "S-81 (layer 1's writer). The layer reopens if a record's statement, acceptance, applicability, allocation, "
    "verification or release effect changes, which the registry header makes a change to the baseline needing its own "
    "review. Owner: the integrator as registry writer |")

IL_OLD = "> **INTEGRATOR LINE, layer 3:** status at `e3aedb25` IN_PROGRESS; status now: IN_PROGRESS; as of commit:"
IL_NEW = ("> **INTEGRATOR LINE, layer 3:** status at `e3aedb25` IN_PROGRESS; status now: **COMPLETE in the commit that "
          "files " + RECN + "** (the re-check, at the end of this line; its package the next snapshot, H3); as of commit:")
END_OLD = "What remains is the H2 section's row for layer 3, first S-80 and EQ-30. Owner: the integrator as registry writer."
END_NEW = END_OLD + (
    " **Re-baseline (27 September 2026, branch `fnd/l3rb` from main `ef144760`):** S-80's fix exactly as the narrow "
    "verification's section 3 gives it, in `a54b793b` (`v2/docs/records/l3rb/apply_fix.py`, asserted anchors): CON-010's "
    "newest evidence entry ends with the record's actual state, FAIL on W3T-F1 (S-64, EQ-25), on the file at "
    "`7a834fe55aea6ccd`; the header's paragraph on the targeted fix names `79963b3b`'s re-take of the reviewed attempt's "
    "own CURRENT-EVIDENCE re-read on CON-010 and REQ-044; the trace page re-rendered; the verification's observation (c) "
    "recorded as S-81 for layer 1's writer. Then `2c12be91` (`apply_baseline.py`): `baseline_state` BASELINED at "
    "`a54b793b`, `baseline_reviews` naming Review B's three records and the narrow verification, S-51, S-78 and S-80 "
    "closed by commit `a54b793b`; `rebaseline_difference.py` compares the registry entry by entry, comment lines and "
    "open items included, at `3e4799eb`, `ef144760`, `a54b793b` and `2c12be91` (ALL ASSERTIONS HOLD). S-80's fourth "
    "step, the re-check, was not held before that baseline: the session's choice under the owner's standing rule of 26 "
    "September 2026, with a reversal clause in the registry header. **Re-check (27 September 2026):** one session that "
    "wrote neither edit, took no part in the fix or the baseline and held no earlier check re-checked them at "
    "`2c12be91` (" + RECN + ", \"AI check (not a qualified engineering review)\", sha256/16 `7831358b96b6f5ca` as filed in "
    "the commit that carries this sentence, with one phrase rewritten: the trailer's name in its last observation, "
    "which the repository's pre-commit check refuses on any added line; the checker's own file had `ab9b3ec1e590a41a`, "
    "both in `v2/docs/records/README.md`): **B-1 CLOSED.** Remedy (1), CON-010's newest entry reads "
    "FAIL in agreement with its `evidence_result`, its `history` and the re-take's entries: PASS. Remedy (2), the header "
    "names `79963b3b`'s re-take with both bindings: PASS. Remedy (3), the trace page re-rendered and current at both "
    "commits: PASS. The baseline and `baseline_reviews`, four hashes matching: PASS. S-51, S-78 and S-80 closed with "
    "evidence: PASS. Its own entry-by-entry comparison finds no registry difference from `ef144760` beyond the stated "
    "ones and no protected field changed from `3e4799eb`: PASS. So the reversal clause is not triggered. **Applied in "
    "the commit that carries this sentence** (`v2/docs/records/l3rb/apply_recheck.py`, asserted anchors and an asserted "
    "entry-by-entry difference; `edit_docs.py` for the pages): the record added to `baseline_reviews`; a registry header "
    "paragraph on the re-check; one sentence appended to the closing evidence of S-51, S-78 and S-80, since the "
    "re-check's observation found that they, the header and the comment above `baseline_reviews` said no re-check was "
    "held; one sentence appended to S-79's title; `REQUIREMENTS-TRACE.md` re-rendered; ENGINEERING-QUESTIONS EQ-28 and "
    "EQ-30 answered and EQ-29 given its layer 3 package. Nothing else in the registry moved: these are notes, closed "
    "items' evidence and an open item, which the header lets move without a review of the baseline. **Status now: "
    "COMPLETE** for the layer's own engineering purpose, on the review records (Review B and the two release checks) "
    "and the two targeted checks (the narrow verification and this re-check), each an AI review or check and none a "
    "qualified review (none is required for layer 3, SC-46). This is a record closure and closes no electrical defect. "
    "Its versioned package, acceptance item 3.18, is the next snapshot, H3, cut from the pushed commit that carries "
    "this line; S-79 and EQ-29 close with it. Remaining, carried and not holding the layer: (1) H3 (S-79, EQ-29), the "
    "integrating session's, which also restates START-HERE's and CONTINUATION-BRIEF's layer 3 lines, written at H2; (2) "
    "the release-2 record's minors n2 to n9 and the first check's m1 to m10, with both records' section 6 notes; (3) "
    "REQ-077 FAIL until HOT-R1 (S-57), and GND-002 unruled (layer 4); (4) S-81, for layer 1's writer; (5) the fixer's "
    "list for other writers, as the re-check's section 5 names it: `feasibility/EMCON.md` sections 3 and 7 against "
    "section 4b, not judged here. The layer reopens if a record's statement, acceptance, applicability, allocation, "
    "verification or release effect changes. Owner: the integrator as registry writer.")

edit(LS, [
    ("own engineering purpose and layers 3 to 9 are IN_PROGRESS (section \"Status at handover H2\").",
     "own engineering purpose and layers 3 to 9 are IN_PROGRESS (section \"Status at handover H2\"). **After H2, layer 3 "
     "is COMPLETE** in the commit that files " + RECN + " (branch `fnd/l3rb`; the H2 files carry it IN_PROGRESS, and "
     "its package is the next snapshot, H3)."),
    ("with the index's last column restated at H2.",
     "with the index's last column restated at H2. **After H2 (branch `fnd/l3rb`):** EQ-28 and EQ-30 are answered by "
     "the re-baseline of layer 3 and its re-check, and EQ-29's package for layer 3 is the next snapshot, H3."),
    ("and none is a qualified engineering review.\n\n| Layer | Status in H2 |",
     "and none is a qualified engineering review. **After H2 (branch `fnd/l3rb` from main `ef144760`):** layer 3 is "
     "COMPLETE in the commit that files the re-check of its re-baseline (its row below); the H2 files carry it "
     "IN_PROGRESS, and its versioned package is the next snapshot, H3.\n\n| Layer | Status in H2 |"),
    (ROW3_OLD, ROW3_NEW),
    (IL_OLD, IL_NEW),
    (END_OLD, END_NEW),
])

EQ = "v2/docs/handover/ENGINEERING-QUESTIONS.md"
edit(EQ, [
    (" and adds an H2 sentence to the attempts rows of EQ-19, EQ-20, EQ-21, EQ-25 and EQ-29. Internal names",
     " and adds an H2 sentence to the attempts rows of EQ-19, EQ-20, EQ-21, EQ-25 and EQ-29. **The re-baseline of layer 3 "
     "(27 September 2026, branch `fnd/l3rb` from `ef144760`)** applies EQ-30's option (a): the wording fix (`a54b793b`), "
     "the baseline (`2c12be91`) and the re-check of the two edits (" + RECN + ", an AI check, B-1 CLOSED); it answers "
     "EQ-28 and EQ-30, and names EQ-29's package for layer 3 as the next snapshot, H3; its citations are at that "
     "branch's commits. Internal names"),
    ("| none | reopened: the targeted fix wrote `baseline_state` BASELINED at `cecfd0f1` (`3e4799eb`), and its narrow "
     "verification found one registry difference the header does not state, so under the registry's reversal "
     "`baseline_state` reads READY_FOR_REVIEW_B and S-51 and S-78 are open until EQ-30 is done |",
     "| none | answered: reopened by the narrow verification of the targeted fix, then, after EQ-30's wording fix "
     "(`a54b793b`), the registry BASELINED at `a54b793b` (`2c12be91`, S-51 and S-78 closed) and the re-check at "
     "`2c12be91` finding B-1 CLOSED; layer 3 COMPLETE in the commit that files the re-check |"),
    ("| none | answered for layers 1 and 2 by the H2 snapshot (option (b): layers 1 and 2 baselined, layer 3 "
     "IN_PROGRESS); S-79 stays open until a snapshot is cut from the pushed commit that carries the layer 3 "
     "re-baseline |",
     "| none | answered for layers 1 and 2 by the H2 snapshot (option (b): layers 1 and 2 baselined, layer 3 "
     "IN_PROGRESS); S-79 stays open until a snapshot is cut from the pushed commit that carries the layer 3 "
     "re-baseline: that content is on `fnd/l3rb` (the re-baseline and its re-check), and the snapshot is H3 |"),
    ("| none | the layer 3 baseline (S-80, then S-51 and S-78): a wording fix and a re-check of it |",
     "| none | answered: the wording fix (`a54b793b`), the baseline (`2c12be91`) and the re-check of the two edits "
     "(B-1 CLOSED at `2c12be91`); S-80, S-51 and S-78 closed |"),
    ("**Reopened**; option (a) stands, limited now to EQ-30's two edits. |",
     "**Reopened**; option (a) stands, limited now to EQ-30's two edits. **Re-baseline and re-check (27 September "
     "2026, branch `fnd/l3rb`):** EQ-30's two edits in `a54b793b`; `2c12be91` sets `baseline_state` BASELINED at "
     "`a54b793b` with `baseline_reviews` naming Review B's three records and the narrow verification, and closes S-51, "
     "S-78 and S-80 by commit `a54b793b` (`v2/docs/records/l3rb/rebaseline_difference.out`: the registry's difference "
     "entry by entry, comment lines included, ALL ASSERTIONS HOLD); the re-check at `2c12be91` (" + RECN + ", an AI "
     "check by a session that wrote neither edit) finds B-1 CLOSED and no registry difference the header does not "
     "state, and the commit that files it adds it to `baseline_reviews`. Layer 3 is COMPLETE in that commit. "
     "**Answered.** |"),
    ("The branch is pushed by the integrating session, which makes the snapshot's commit public; S-79 stays open for "
     "layer 3. |",
     "The branch is pushed by the integrating session, which makes the snapshot's commit public; S-79 stays open for "
     "layer 3. **After H2 (27 September 2026, branch `fnd/l3rb`):** layer 3's re-baseline (`a54b793b`, baselined in "
     "`2c12be91`) and its re-check (" + RECN + ", B-1 CLOSED) are the content option (a) waited on; the package is the "
     "next snapshot, H3, cut from the pushed commit that carries them, and S-79 closes with it. |"),
    ("(the owner's execution prompt, section 4: no unbounded author and check loop). |",
     "(the owner's execution prompt, section 4: no unbounded author and check loop). **Re-baseline (27 September 2026, "
     "branch `fnd/l3rb` from `ef144760`):** option (a) applied. `a54b793b` makes the two edits exactly as the "
     "verification's section 3 gives them (`v2/docs/records/l3rb/apply_fix.py`) and re-renders the trace page; "
     "`2c12be91` baselines the registry at `a54b793b` and closes S-51, S-78 and S-80, taking the baseline before the "
     "re-check under the owner's standing rule of 26 September 2026 with a reversal clause; option (b)'s script "
     "extension is met by `v2/docs/records/l3rb/rebaseline_difference.py` (comment lines and open items compared, "
     "commit by commit). **Re-check (27 September 2026, at `2c12be91`, " + RECN + ", an AI check by a session that "
     "wrote neither edit):** B-1 CLOSED; remedies (1) to (3) PASS, the baseline and the closures PASS, no unstated "
     "registry difference, so the reversal is not triggered. **Answered.** |"),
])
