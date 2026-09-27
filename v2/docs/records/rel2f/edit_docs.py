"""The documents' half of the release finalizer of layers 1 to 3 (27 September 2026, MESHSAT-1357, branch fnd/rel2
rebased onto main 391d8579 and then 91894cd7), after the second release check at eb9f9030. Ids from apply_registry.py's JSON (the only
argument). Every edit replaces asserted old text; CONOPS and START-HERE keep their line counts (other pages cite them
by line). Session wording under the owner's standing rule of 26 September 2026. Run from the worktree root after
apply_registry.py.

  layer 2 (no blocking item)   CONOPS's status line and its Review A paragraph name the baseline at the commit that
                               carries the reviewed content (79963b3b) and the record; LAYER-STATUS's summary row and
                               integrator line read COMPLETE with the record and the evidence; START-HERE's closed-lid
                               reduced mode (the record's n7); the integrator line names M-02, S-53 and BAT-F19 (n8)
  layers 1 and 3 (blocking)    LAYER-STATUS's integrator lines stay IN_PROGRESS and list what remains; the three
                               engineering questions in ENGINEERING-QUESTIONS.md group A with their index rows
"""
import json, sys

IDS = json.load(open(sys.argv[1])); (S1, S2, S3), (E1, E2, E3) = IDS['S'], IDS['EQ']
CONTENT = '79963b3b'          # the rebased commit that carries the content the second release check read at eb9f9030
MAIN = '91894cd7'              # main when the branch was last rebased (the consolidated re-take)
FIRST = '7dfbfb16'             # the rebased form of d535c17e
R1 = 'REVIEW-LAYER-1-RELEASE-2-2026-09-27.md'; R2 = 'REVIEW-LAYER-2-RELEASE-2-2026-09-27.md'
R3 = 'REVIEW-LAYER-3-RELEASE-2-2026-09-27.md'
files = {}


def rep(path, a, b, n=1):
    if path not in files: files[path] = open(path, encoding='utf-8').read()
    s = files[path]
    assert s.count(a) == n, (path, s.count(a), a[:100]); assert a != b
    files[path] = s.replace(a, b)


def append_to_line(path, head, tail_old, add):
    """Append `add` to the one line that starts with `head` and ends with `tail_old`."""
    if path not in files: files[path] = open(path, encoding='utf-8').read()
    L = files[path].split('\n'); hits = [k for k, l in enumerate(L) if l.startswith(head)]
    assert len(hits) == 1, (path, head, len(hits)); k = hits[0]
    assert L[k].endswith(tail_old), (path, head, L[k][-160:])
    L[k] = L[k] + add; files[path] = '\n'.join(L)


# ================================================================ CONOPS (layer 2 baselined; line count kept)
C = 'v2/docs/CONOPS.md'
rep(C, "**Status: DRAFT for Review A of the foundation baseline (MESHSAT-1357), written 25 September 2026, revised the\n",
    "**Status: BASELINED as layer 2 of the foundation baseline (MESHSAT-1357) at `%s`, the commit that carries on main "
    "`%s` the content the second release check of layer 2 read at `eb9f9030` and found no blocking item in "
    "(`reviews/%s`, an AI review; this document byte-identical, sha256/16 `3ff59edc96a3f8f4`, before this status "
    "line and the Review A paragraph's last sentence were written). Written 25 September 2026, revised the\n"
    % (CONTENT, MAIN, R2))
rep(C, "and a later pass decides the baseline. Until a pass\nfinds no blocking item this document is a DRAFT for Review A. Prototype design.\n",
    "and the second release check (`reviews/%s`, at `eb9f9030`, AI review) found no blocking item, so the layer is "
    "baselined at `%s` (`handover/LAYER-STATUS.md`, layer 2, names the record and its evidence). Until that pass\n"
    "this document was a DRAFT for Review A. Prototype design.\n" % (R2, CONTENT))

# ================================================================ START-HERE (n7; line count kept)
SH = 'v2/docs/handover/START-HERE.md'
rep(SH, "the cells; a closed-lid reduced mode (still to be defined, LAYER-STATUS layer 2). The hot end is not established: the\n",
    "the cells; a closed-lid reduced mode (defined in `CONOPS.md` section 4c since the layer 2 closer, and baselined with "
    "layer 2 after its second release check, LAYER-STATUS layer 2). The hot end is not established: the\n")

# ================================================================ LAYER-STATUS
L = 'v2/docs/handover/LAYER-STATUS.md'
rep(L, "**The second release attempt (27 September 2026):** EQ-13 is rewritten as what the session took (SC-21) and EQ-26 is added.",
    "**The second release attempt (27 September 2026):** EQ-13 is rewritten as what the session took (SC-21) and EQ-26 is "
    "added. **The release finalizer (27 September 2026):** %s to %s are added, the items the second release check left on "
    "layers 1 and 3." % (E1, E3))
rep(L, "| 2. Concept of operations | IN_PROGRESS | round 8's pack temperature ladder (`dd39fb15`, `73d5df1e`) | the closer hc2 "
       "is a candidate in its worktree: Review A, layer 2, second pass FAIL on P2-B1 and P2-B2 |",
    "| 2. Concept of operations | IN_PROGRESS in H1; **COMPLETE** since the second release check (at `%s`, `v2/docs/reviews/%s`, "
    "AI review, no blocking finding; the layer 2 integrator line gives the evidence) | round 8's pack temperature ladder "
    "(`dd39fb15`, `73d5df1e`); after H1.1 the closer hc2 with c23 (`95e078a1`) and both release attempts | in H1: the closer "
    "hc2 was a candidate in its worktree (Review A, layer 2, second pass FAIL on P2-B1 and P2-B2); now: nothing for the "
    "layer's own purpose, the package being the next handover snapshot; the records' minors and the later-stage items "
    "stay with their owners |" % (CONTENT, R2))

LEAD = "**Second release attempt of layers 1, 2 and 3 (27 September 2026, branch `fnd/rel2` from `953f5658`).**"
s = open(L, encoding='utf-8').read() if L not in files else files[L]
i = s.index(LEAD); j = s.index("\n", i)
files[L] = s[:j] + (
    "\n\n**Second release check and the release finalizer (27 September 2026).** Three fresh reviewers, each an AI review "
    "labelled as one and none of them a qualified review, judged layers 1, 2 and 3 at `eb9f9030` (branch `fnd/rel2`, "
    "then on `953f5658`): `v2/docs/reviews/%s`, `%s` and `%s`, filed byte for byte in the commit that carries this "
    "paragraph. **Layer 2** has no blocking finding and **is COMPLETE** for its own engineering purpose at `%s`, the "
    "commit that carries the reviewed content on main `%s`: the branch was rebased onto main after the review, first "
    "onto `391d8579` (set 5; `v2/docs/records/rel2f/resolve_rebase.py`, `check_rebase.py`) and then, when main moved "
    "during the release, onto the consolidated re-take (the pages rendered again, with a third tool entry in "
    "`evidence/COMPATIBILITY.md`), and CONOPS, OPERATING-ENVELOPE, TEST-PLAN, "
    "`pcb_envelope.yaml` and the layer's review records are byte-identical to the files the reviewer read, PANEL.md "
    "differing only by set 5's own row. **Layer 1** reads FAIL for release on one blocking finding (R2-B1: the brief's "
    "six core feasibility blockers against the registry's seven, FEA-007 missing), and **layer 3** NOT COMPLETE on two "
    "procedural items (B-1, the baseline not recorded; B-2, no versioned package). This was the second attempt on "
    "each, so no further fix was applied (the owner's execution prompt, section 4): each remaining item is an open item "
    "of the registry and an engineering question (layer 1: %s and %s; layer 3: %s and %s, %s and %s), and **layers 1 "
    "and 3 stay IN_PROGRESS**. The rebase renumbered the second release attempt's session choices SC-51 to SC-56 as "
    "SC-58 to SC-63 and its question EQ-25 as EQ-26, because set 5 had taken those ids; the three records cite the old "
    "numbers, as at `eb9f9030`. Session choices are the session's under the owner's standing rule of 26 September 2026."
    % (R1, R2, R3, CONTENT, MAIN, S1, E1, S2, E2, S3, E3)) + s[j:]

# layer 1: stays IN_PROGRESS
append_to_line(L, "> **INTEGRATOR LINE, layer 1:**", "(5) the usability check of the snapshot. Owner: the integrator.",
    " **Second release check (27 September 2026):** a fresh reviewer (AI review) judged layer 1 at `eb9f9030` "
    "(`v2/docs/reviews/%s`, filed byte for byte in the commit that carries this sentence): B1, B2 and B3 of the first "
    "check are CLOSED on the text, and of its minors m1, m4, m5 and m8 are closed and m7 in part; purpose, users, scope, "
    "exclusions, the commitments split, the rulings record, the SIM description and the mass limit meet the owner's row. "
    "The verdict is FAIL for release on one blocking finding, R2-B1: the brief's \"six feasibility blockers on the core\" "
    "(lines 256 to 258) against the registry's seven, FEA-007 (the kit's fit in the Peli 1450 on C1 to C6, core under "
    "SC-04, BLOCKED on the owner's purchase L-07 or his acceptance of the residual, with bounds that include failure on "
    "the pack's M4a and M5 and on D-07's east plug layout, M17g) absent from the open items, and the D-07 row naming only "
    "the board E clamp fit. The fix is wording only, but this was the second attempt, so the release finalizer did not "
    "apply it (the owner's section 4; the same cause, the brief restating design state that moves, has now produced B1, "
    "B2 and R2-B1): it is open item %s and ENGINEERING-QUESTIONS %s, which recommends the reviewer's fix together with "
    "the by-reference method. The brief stays CANDIDATE. **Status now: IN_PROGRESS.** Remaining, replacing the list "
    "above: (1) %s and %s: the reviewer's three edits (lines 256 to 258, an open-items row for FEA-007, the east plug "
    "layout in the D-07 row) with R2-m1 to R2-m5 on the same pages, and one of the method remedies; (2) a re-check by a "
    "reviewer who wrote none of the changed lines, at one pinned commit, then the brief set to BASELINED in the commit "
    "that files it; (3) the snapshot from a pushed branch (acceptance item 14; %s), bringing START-HERE lines 144, 175 "
    "and 218 and CONTINUATION-BRIEF lines 36 to 37 along (R2-m7); (4) the carried minors m3, m6 and m9 (R2-m6), and "
    "R2-m7's items for other writers (S-12's title on the locating holes; about 270 W in S-53 and REQ-016's notes "
    "against 266 W elsewhere); (5) the usability check of the snapshot. Owner: the integrator."
    % (R1, S1, E1, S1, E1, S3))

# layer 2: COMPLETE
s = files[L]
h = "> **INTEGRATOR LINE, layer 2:** status at `e3aedb25` IN_PROGRESS; status now: IN_PROGRESS; as of commit:"
assert s.count(h) == 1
files[L] = s.replace(h, "> **INTEGRATOR LINE, layer 2:** status at `e3aedb25` IN_PROGRESS; status now: **COMPLETE at `%s`** "
                        "(the second release check, at the end of this line); as of commit:" % CONTENT)
append_to_line(L, "> **INTEGRATOR LINE, layer 2:**",
    "Owner: the integrator, the TEST-PLAN owner, the registry writer and the board A, B and E authors.",
    " **Second release check and release (27 September 2026):** a fresh reviewer (AI review) judged layer 2 at `eb9f9030` "
    "(`v2/docs/reviews/%s`, filed byte for byte in the commit that carries this sentence): B1 to B4 of the first release "
    "check are CLOSED on the text, every figure it checked reproduces (`records/hc2/pwr_red2.out` and "
    "`hotstop_bounds.out` byte for byte), the envelope and registry fixtures pass on a clean copy, and there is no "
    "blocking finding: layer 2 meets the owner's COMPLETE test for its own engineering purpose. The record's release "
    "steps: (1) integrated onto main `%s` by rebasing `fnd/rel2` (`%s`, `%s`; onto `391d8579` first, resolved by "
    "`records/rel2f/resolve_rebase.py` and checked line by line by `check_rebase.py`, then onto the consolidated re-take "
    "with no conflict in a document, the pages rendered again and `edge_length.py`'s tool entry added by "
    "`records/rel2f/apply_compat.py` so that no current reading lost its class): CONOPS (`3ff59edc96a3f8f4`), OPERATING-ENVELOPE (`43361b02743cf3af`), TEST-PLAN "
    "(`4f15bd02a6a8be46`), `pcb_envelope.yaml` (`bbcc2b5cbb721372`) and the four Review A and release records are "
    "byte-identical to the files the reviewer read, and PANEL.md differs only by set 5's own row (U28's EMCON_EF_FLT on "
    "P1.2, no operator item, read by the reviewer); the needs pin and ENV-001's pins hold at `%s`; `test_envelope_data` "
    "and `test_requirements` pass there (116 passed with test_evidence_class, test_pack_protection and "
    "test_layout_entry_stages); HOT-R1's netlist premises were re-read by the reviewer on `%s`'s generators, which `%s` "
    "carries unchanged; (2) CONOPS's status line and its Review A paragraph name the baseline and the record, START-HERE "
    "no longer calls the closed-lid reduced mode \"still to be defined\" (n7), and the needs pin and the three readings "
    "bound to CONOPS are re-taken on that header change alone (`records/rel2f/post_docs_registry.py`); (3) the versioned "
    "package is the next handover snapshot, which the integrating session cuts from the pushed commit that carries "
    "this line (%s). **Status now: COMPLETE at `%s`** (the content; recorded in the commit that carries this sentence). "
    "Not holding the layer, and named here so that the \"not hidden\" test can be read where the status is (n8): M-02 "
    "and S-53 (EQ-13: M1's night on D-06's pack is the owner's to carry, its day the session's, before boards A, E and P "
    "enter layout; M1's duration is set by SC-21, so no mode, trigger or bearer set waits on them), BAT-F19 (CFL-017, "
    "EQ-26: a qualification margin, not an operating limit), and the later-stage items above (HOT-R1, S-57 and EQ-22; "
    "S-58 and EQ-23; FEA-004, EQ-05 and T-H1; BANK-R1, S-54; S-55; REQ-069 and EQ-03). If one of them closes in a way "
    "that changes a mode or a product decision (FEA-004 ending in an owner trade on D-02b's closed-lid scope, or M-02 "
    "choosing a different pack), layer 2 reopens for that item only and a new version is issued (the owner's section 8). "
    "Carried minors, none blocking: the second check's n1 to n6, n9 and n10 (n4 and n5 are layer 5's text, n9 and n10 "
    "layers 3 and 4's) and the first check's m1 to m16 (m13 partly answered by HW-FW-CONTRACT). Owner of the minors: the "
    "integrator, the TEST-PLAN owner, the registry writer and the layer 5 writer."
    % (R2, MAIN, FIRST, CONTENT, CONTENT, '391d8579', CONTENT, S3, CONTENT))

# layer 3: stays IN_PROGRESS
append_to_line(L, "> **INTEGRATOR LINE, layer 3:**", "Owner:\n the integrator as registry writer.".replace('\n', ''),
    " **Second release check (27 September 2026):** a fresh reviewer (AI review) judged layer 3 at `eb9f9030` "
    "(`v2/docs/reviews/%s`, filed byte for byte in the commit that carries this sentence): R2 to R5 of the first release "
    "check are ANSWERED (R3 on `08f3665a`, which is on the public main), the record is the fresh confirmation R1 asks for, "
    "the figures it checked match their sources, and nothing was lowered, dropped, weakened or narrowed. Its verdict is "
    "NOT COMPLETE on two procedural items: B-1 (item 3.14: `baseline_state` still READY_FOR_REVIEW_B and S-51 open) and "
    "B-2 (item 3.18: no versioned package). This was the second attempt, so the release finalizer applied neither (the "
    "owner's section 4). Since the review the branch was rebased onto main `391d8579` and then `%s`, which adds set 5's "
    "and the consolidated re-take's registry changes and renumbers the reviewed SC-51 to SC-56 as SC-58 to SC-63 (EQ-25 as EQ-26), so the registry at the branch head is no "
    "longer the one the reviewer read (sha256/16 `fb819e939f2895da`), and the record says a registry change beyond its "
    "B-1 fix needs a review of its own. B-1 is open item %s and ENGINEERING-QUESTIONS %s (a confirmation limited to that "
    "difference, then the one baseline commit the record describes); B-2 is %s and %s (the push and the snapshot, the "
    "integrating session's). **Status now: IN_PROGRESS**; `baseline_state` stays READY_FOR_REVIEW_B and S-51 open. "
    "Remaining, replacing the list above: (1) %s and %s; (2) %s and %s (the earlier item on the anchor commit being "
    "public is met, the record's n5); (3) the record's minors n1 to n9 (n1, the three gen_sch_b.py pointers, goes into "
    "the baseline commit) and the first check's m1 to m10, with both records' section 6 notes; (4) REQ-077 FAIL until "
    "HOT-R1 (S-57), and GND-002 unruled (layer 4). Owner: the integrator as registry writer."
    % (R3, MAIN, S2, E2, S3, E3, S2, E2, S3, E3))

# ================================================================ ENGINEERING-QUESTIONS
E = 'v2/docs/handover/ENGINEERING-QUESTIONS.md'
rep(E, "and adds EQ-26 (BAT-F19); their citations are at that branch's commits. Internal names are defined in",
    "and adds EQ-26 (BAT-F19); their citations are at that branch's commits. **The release finalizer of layers 1 to 3 "
    "(27 September 2026, branch `fnd/rel2` rebased onto `%s`)** adds %s to %s, the items the second release check left on "
    "layers 1 and 3 and did not see fixed a third time; their citations are at that branch's commits. Internal names are "
    "defined in" % (MAIN, E1, E3))
s = files[E]; k = s.index('| EQ-26 |'); k = s.index('\n', k) + 1
files[E] = s[:k] + (
    "| %s | The product brief counts six core feasibility blockers where the registry holds seven (FEA-007, the kit's fit "
    "in the Peli 1450, is missing) | A. design work | 1 | none (the brief) | the brief's BASELINED state and layer 1 (%s) |\n"
    "| %s | The requirements registry's baseline is not recorded, and the rebase onto set 5 added registry content its "
    "reviewer did not read | A. design work | 3 | none | `baseline_state`, S-51 and layer 3 (%s) |\n"
    "| %s | No versioned package carries layers 1 to 3 as released | A. design work | 1, 2, 3 | none | layer 3's item "
    "3.18 and layer 1's item 14; the same snapshot carries layer 2's baselined CONOPS (%s) |\n"
    % (E1, S1, E2, S2, E3, S3)) + s[k:]

SEC = """### {e1}. The product brief counts six core feasibility blockers where the registry holds seven ({s1})

Added on 27 September 2026 by the release finalizer of layers 1 to 3 (layer 1's second release check, R2-B1).

| | |
|---|---|
| **Exact issue** | `v2/docs/PRODUCT-BRIEF.md` lines 256 to 258 say six feasibility blockers on the core are not closed (FEA-001 to FEA-006). The requirements registry holds seven `kind: feasibility` records, every one `prototype_1: core` and `release_effect: BLOCKER`. FEA-007, the kit's fit in the Peli 1450 on the case choices C1 to C6 (core under SC-04, which makes fitting the boards and the pack into the 1450 core), is missing from that sentence and from the brief's open items, which say they list every item bearing on the brief. It holds the layout entry of boards A, B, D, E, E5 and P and is BLOCKED on the owner's purchase L-07 or his acceptance of the residual; its bounds include failure (35 of 70 case margins OPEN; M17g and M17x fail as laid out until the jumper plug is picked; the pack's M4a and M5 OPEN on the undesigned hold-down S-27). The brief's pack line (D-06) and its D-07 row (line 289, which names only the board E clamp fit, not the east plug layout M17g) depend on it. |
| **Affected** | Layer 1: the brief's acceptance items 5, 7 and 15 of the record, and its BASELINED state. No board, interface, part or requirement: the fix is wording. FEA-007 itself belongs to layer 7 and to the boards' layout entry. |
| **Evidence** | `v2/docs/reviews/{r1}` sections 4 (R2-B1) and 7; registry FEA-007, SC-04, L-07 and S-27; `v2/docs/CURRENT-EVIDENCE.md`, the feasibility blockers; `v2/docs/CASE-FIT-UNCERTAINTIES.md` sections 2, 6 and 7; `v2/docs/CASE-MARGINS.md` rows M4a, M5, M17g and M17x. |
| **Attempts and results** | The first release check (`REVIEW-LAYER-1-RELEASE-2026-09-27.md`, m2) classed the omission as minor because FEA-007's parent NEED-06 is not a core need; FEA-007's own `prototype_1: core` under SC-04 contradicts that ground, and the second release check (at `eb9f9030`) re-judged it blocking. The two attempts before it closed B1 to B3 (EMCON, the case set, REQ-072's night). This is the third finding of one cause: the brief restates design state (counts, lists, stages) that moves with every circuit or case round, and the change of method both checks asked for (LAYER-STATUS layer 1) was not adopted. Under the owner's section 4 the finalizer did not apply a third fix. |
| **Viable options** | (a) Apply the reviewer's exact fix: the sentence names seven blockers with FEA-007 as core under SC-04; an open-items row for FEA-007 with its failing rows, its allocation to layer 7 and the boards' layout entry, the owner's purchase or residual, and the reissue rule if the pack rows cannot be met by a board move and the hold-down (D-06 reopened); the east plug layout (M17g, FEA-007) named in the D-07 row; with R2-m1 to R2-m5 on the same pages. (b) (a) with the method change: the brief states the feasibility blockers, EMCON's count and the case state by reference to the registry (`kind: feasibility`), `feasibility/EMCON.md` section 0a and the case release, not as restated counts. (c) (a), and the five layer 1 pages re-read at every integration that touches EMCON, the case, CONOPS or a feasibility record. |
| **Recommended next action** | (b), the session's under the owner's standing rule of 26 September 2026: the wording closes R2-B1 and the by-reference statement removes the cause. Then a reviewer who wrote none of the changed lines checks the difference from the record's sha256 values at one pinned commit, the brief is set BASELINED in the commit that files that check, and a snapshot is cut from a pushed branch (item 14; {e3}). |
| **Expertise or equipment** | The docs integrator; one fresh AI reviewer (no qualified review is required for layer 1, SC-16). |
| **Cost and lead time** | Desk work: the edits and one review pass; no money. |

### {e2}. The requirements registry's baseline is not recorded ({s2})

Added on 27 September 2026 by the release finalizer of layers 1 to 3 (layer 3's second release check, B-1).

| | |
|---|---|
| **Exact issue** | `baseline_state` reads READY_FOR_REVIEW_B and S-51 is open, although layer 3's second release check (at `eb9f9030`) confirms R2 to R5 of the first release check answered and finds no blocking finding of substance; it leaves the baseline commit itself as blocking item B-1 (acceptance item 3.14). Since then the branch was rebased onto main `391d8579` and then `{main}`: the registry at its head also carries set 5's records (SC-51 to SC-57, S-64 to S-76 and their readings) and the consolidated re-take's re-read notes (`8ea7867e` to `91894cd7`), the reviewed SC-51 to SC-56 are SC-58 to SC-63 and EQ-25 is EQ-26, and {s1} to {s3} are added, so it is no longer the registry the reviewer read (sha256/16 `fb819e939f2895da`). The record says a registry change beyond its B-1 fix needs a review of its own. |
| **Affected** | Layer 3 (item 3.14 and its status); the requirements part of FOUNDATIONS_BASELINED. No board, interface or part. |
| **Evidence** | `v2/docs/reviews/{r3}` sections 2, 4 (3.14), 5 (B-1, n1) and 7; registry `baseline_state` and S-51; `v2/docs/records/rel2f/resolve_rebase.py` and `check_rebase.py` (what the rebase changed); `git diff 953f5658 {main} -- v2/ecad/tools/pcb_requirements.yaml` (set 5's and the re-take's registry changes). |
| **Attempts and results** | First release check at `f2b7fa66`: NOT COMPLETE on R1 to R5. Second release attempt: R2 to R5 answered at desk. Second release check at `eb9f9030`: R2 to R5 ANSWERED, B-1 and B-2 procedural. The finalizer made neither change (the second attempt; the owner's section 4), and the rebase added registry content the reviewer did not read. |
| **Viable options** | (a) A reviewer who wrote none of it confirms the registry difference between the reviewed content and the branch head (set 5's and the consolidated re-take's registry changes, the renumbering, {s1} to {s3}); then one commit that makes only B-1's changes: `baseline_state` baselined naming the content commit, S-51 closed on the two layer 3 release records, the three `gen_sch_b.py` pointers in SC-58 and SC-63 (:257, :822, :764-766) marked "(as read at e3aedb25)" or renumbered to 267 and 464, 978 and 903 to 905, the trace page re-rendered and the layer 3 integrator line updated. (b) Baseline the reviewed content alone, a registry state before set 5 that main no longer carries, so the baseline would name a registry that is not current. (c) Wait for the next circuit round and review once for both, which lets the registry move again under the review. |
| **Recommended next action** | (a), the session's under the standing rule: the review is limited to the difference, and the baseline commit carries nothing else, as the record asks. |
| **Expertise or equipment** | The registry writer; one fresh AI reviewer (Review B's definition, SC-46; no qualified review is required for layer 3). |
| **Cost and lead time** | Desk work: one review pass and one commit; no money. |

### {e3}. No versioned package carries layers 1 to 3 as released ({s3})

Added on 27 September 2026 by the release finalizer of layers 1 to 3 (layer 3's second release check, B-2).

| | |
|---|---|
| **Exact issue** | Layer 3's acceptance item 3.18 (a versioned, portable layer package) is not met: the reviewed commit was on no remote branch (GitLab and GitHub main were at `953f5658` when it was read; main is `{main}` now) and no handover snapshot has been cut from a commit carrying its content. The anchor `08f3665a` is already on the public main, so LAYER-STATUS layer 3's earlier remaining item on it is met. |
| **Affected** | Layer 3 (3.18) and layer 1 (item 14); the same snapshot carries layer 2's baselined CONOPS. No design file. |
| **Evidence** | `v2/docs/reviews/{r3}` sections 1, 4 (3.18) and 5 (B-2, n5); `v2/release/handover/` (H1 and H1.1 predate the release attempts). |
| **Attempts and results** | None: pushing to main and cutting a snapshot belong to the integrating session, the only committer to main, not to a worktree finalizer. |
| **Viable options** | (a) Push the baseline commit of {e2} to main and cut the next handover snapshot from it, its manifest and `SOURCE.txt` naming that commit, carrying layers 1 to 3 with their status lines. (b) Cut a snapshot now from the branch head with layers 1 and 3 as candidates and layer 2 baselined, and a later one for the layer 3 baseline (two snapshots, nothing lost). |
| **Recommended next action** | (a) once {e2} is done; if {e2} waits, (b), so that layer 2's COMPLETE content is packaged without delay. Then the owner's section 7 usability check of the snapshot. |
| **Expertise or equipment** | The integrating session (push rights and the handover packer), and a fresh usability checker (owner's section 7). |
| **Cost and lead time** | Desk work; no money. |

"""
s = files[E]; k = s.index('\n## B. Physical evidence'); k2 = s.rindex('\n\n', 0, k + 1)
assert s[k2:k] == '\n' or s[k - 1] == '\n'
files[E] = s[:k + 1] + SEC.format(e1=E1, e2=E2, e3=E3, s1=S1, s2=S2, s3=S3, r1=R1, r3=R3, main=MAIN) + s[k + 1:]

for p, body in files.items():
    old = open(p, encoding='utf-8').read(); assert body != old, p
    if p in (C, SH): assert body.count('\n') == old.count('\n'), (p, 'line count changed')
    open(p, 'w', encoding='utf-8').write(body); print('edit_docs (rel2f): wrote', p)
