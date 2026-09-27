"""The new text of the restructure (MESHSAT-1357, 27 September 2026, branch fnd/defstab): each document's head (its
status line, the rule and one sentence per dependency naming where its current state lives), the appendix
introductions and the status page's own text. Everything else in the three files is moved text, written byte for byte
by build.py."""

RULE_SOURCE = "the independent review of handover H2, `reviews/2026-09-27-h2-independent-review.md` section 4"
RULE_SOURCE_FULL = "the independent review of handover H2, `v2/docs/reviews/2026-09-27-h2-independent-review.md` section 4"

BRIEF_HEAD = """
**Status: layer 1 of the foundation baseline (MESHSAT-1357), BASELINED at `6b2a9965`.** How it was reviewed and
baselined is recorded in the appendix at the end of this file; how this file's present text relates to the text
baselined at that commit, and the current state of everything this brief depends on, is `handover/DEFINITION-STATUS.md`.

**When this brief is reopened (the rule of %s).** This definition is reopened only when a requirement, the scope,
the operating concept or a product decision changes. A changed count or a circuit correction updates the status page,
`handover/DEFINITION-STATUS.md`, and the records it names, not this baseline. A figure, a commit or an "as generated"
remark that stands inside a sentence or a table row of the definition below is its value when this brief was
baselined; its current value is kept where the list below says, and a change to it alone does not reopen this brief.

**Where the current state of each dependency lives.**

- What the design has and has not shown, board by board, and whether any board is ready for layout, is kept on
  `CURRENT-EVIDENCE.md`.
- Every requirement with its reading, and every feasibility blocker on the core with the evidence that closes it, is
  kept in the requirements registry `v2/ecad/tools/pcb_requirements.yaml` and its generated page `REQUIREMENTS-TRACE.md`.
- Where each transmitter stands against EMCON as the owner ruled it (D-05) and the latency the session set (REQ-071) is
  kept in `feasibility/EMCON.md` section 0a, under feasibility blocker FEA-002.
- The power, thermal and runtime figures, the hot end and the energy balance of mission M1 are kept in
  `feasibility/POWER-THERMAL.md`, under feasibility blocker FEA-004 and requirement REQ-072.
- The kit's fit in the Peli 1450, and which case set the generators carry, is kept in `CASE-MARGINS.md` and
  `CASE-FIT-UNCERTAINTIES.md`, under feasibility blocker FEA-007.
- Whether the fitted secure element allows ZEROIZE as ruled is kept in `feasibility/ZEROIZE.md`, under feasibility
  blocker FEA-001.
- The state of each layer of the handover, with its review records, is kept on `handover/LAYER-STATUS.md`.
""" % RULE_SOURCE

CONOPS_HEAD = """
**Status: layer 2 of the foundation baseline (MESHSAT-1357), BASELINED at `79963b3b`.** How it was reviewed and
baselined is recorded in the appendix at the end of this file; how this file's present text relates to the text
baselined at that commit, and the current state of everything this document depends on, is
`handover/DEFINITION-STATUS.md`.

**When this document is reopened (the rule of %s).** This definition is reopened only when a requirement, the scope,
the operating concept or a product decision changes. A changed count or a circuit correction updates the status page,
`handover/DEFINITION-STATUS.md`, and the records it names, not this baseline. A figure, a commit or an "as generated"
remark that stands inside a sentence or a table row of the definition below is its value when this document was
baselined; its current value is kept where the list below says, and a change to it alone does not reopen this
document.

**Where the current state of each dependency lives.**

- What the design has and has not shown, board by board, and whether any board is ready for layout, is kept on
  `CURRENT-EVIDENCE.md`.
- Every requirement traced to the needs of section 2, with its reading, and every feasibility blocker on the core with
  the evidence that closes it, is kept in the requirements registry `v2/ecad/tools/pcb_requirements.yaml` and its
  generated page `REQUIREMENTS-TRACE.md`.
- Where each transmitter stands against EMCON as the owner ruled it (D-05) and against REQ-071's latency is kept in
  `feasibility/EMCON.md` section 0a, under feasibility blocker FEA-002.
- Whether board B's generator carries BANK-R1 and the generators of boards A and E carry HOT-R1, and so how REQ-052
  and the hot stop's requirement REQ-077 read on the generated boards, is kept in the requirements registry.
- The power, thermal and runtime figures, the hot end and the energy balance of mission M1 are kept in
  `feasibility/POWER-THERMAL.md`, under feasibility blocker FEA-004 and requirement REQ-072.
- The kit's fit in the Peli 1450 is kept in `CASE-MARGINS.md` and `CASE-FIT-UNCERTAINTIES.md`, under feasibility
  blocker FEA-007.
- Whether the fitted secure element allows ZEROIZE as ruled is kept in `feasibility/ZEROIZE.md`, under feasibility
  blocker FEA-001.
- The state of each layer of the handover, with its review records, is kept on `handover/LAYER-STATUS.md`.
""" % RULE_SOURCE

APPENDIX_INTRO = ("Not part of the baseline. Moved here word for word on 27 September 2026 (branch `fnd/defstab`, "
                  "MESHSAT-1357) from the %s above, as it stood at `31cd29b9`: the record of how %s was reviewed and "
                  "baselined, and the notes that recorded its own revisions. The changing implementation results that "
                  "stood in its running text moved to `handover/DEFINITION-STATUS.md`. Each entry names where it stood "
                  "and its lines at `31cd29b9`; a moved section's own heading is one level lower here. Nothing below "
                  "is maintained: the current state is where the head of this file says.")
BRIEF_APPENDIX_INTRO = APPENDIX_INTRO % ("brief", "the brief")
CONOPS_APPENDIX_INTRO = APPENDIX_INTRO % ("document", "this document")

STATUS_HEAD = """
# Definition status: layers 1 and 2

The status page of the two completed definition baselines of the foundation baseline (MESHSAT-1357):
`v2/docs/PRODUCT-BRIEF.md`, layer 1, the product definition, and `v2/docs/CONOPS.md`, layer 2, the concept of operations. It exists so
that the baselines change only when the definition does (%s). Prototype design: no V2 board has been fabricated,
ordered or powered, and no kit has been field deployed; nothing on this page is a claim about a built product.

## The rule

A definition baseline is reopened only when a requirement, the scope, the operating concept or a product decision
changes. A changed count or a circuit correction updates this page and the records it names, not the baseline. When a
change does reopen a baseline, the affected document is issued again through its layer's review, and the change is
stated in it; nothing is narrowed silently.

## The two baselines

| Layer | Document | BASELINED at | sha256/16 of the file baselined | Release record (AI reviews and checks, none a qualified engineering review) |
|---|---|---|---|---|
| 1, product definition | `v2/docs/PRODUCT-BRIEF.md` | `6b2a9965` | `d36bf76b3dea8b30` (unchanged through `31cd29b9`) | `v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`, the narrow verification of the targeted fix, after `v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md` |
| 2, concept of operations | `v2/docs/CONOPS.md` | `79963b3b` | `3ff59edc96a3f8f4` as the release check read it at `eb9f9030`; `4483209659dc391c` with its status line written (`62f26a44`, unchanged through `31cd29b9`), the file handover H2 carries | `v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md` |

`v2/docs/handover/LAYER-STATUS.md`, layers 1 and 2, names every review record of both layers with its evidence.

## The restructure of 27 September 2026

On 27 September 2026 (branch `fnd/defstab`, from `31cd29b9`) both documents were restructured as the review asks.
Each keeps its definition, meaning its purpose, scope, users, prototype scope, exclusions, fixed constraints, operating
intentions, needs, missions, modes, scenarios and product decisions, with every sentence word for word, and states at
its head the rule above and one sentence per dependency naming where that dependency's current state lives. The
review history of the baseline attempts, and the notes that recorded each document's own revisions, moved to an
appendix at the end of the same file, headed "Appendix: review and status history (not part of the baseline)". The
changing implementation results that stood in running text (transmitter counts, circuit revisions, feasibility-blocker
counts, reading results, commit-by-commit status) moved to this page, word for word, below. Nothing was split or
reworded: a sentence that carries definition content and a result together stayed where it was, and so did every
table row but its revision notes; each document's head says that such a figure or remark is its value at the baseline.

The map of every move is `drafts/defstab/moves.json` in the branch's worktree, written with the build script that
asserts it (`drafts/defstab/build.py`, `cuts.py` and `heads.py`), to be filed under `v2/docs/records/defstab/` when the
branch is integrated. For every moved block it gives the old line range at `31cd29b9`, the new location and the
sha256; for every block of each definition it gives the sha256 before and after, and which moves closed it up. The
script checks that each kept block equals its original with the moved text removed, that every sentence of a kept
block is a sentence of the original, and that every moved text stands byte for byte at its new place. CONOPS's needs
table is byte-identical; the requirements registry's pin on the whole file (`needs_document_sha256`) is re-taken, and
the three readings bound to CONOPS (REQ-005, CFL-014 and CFL-016) are rebound, each with an entry naming what moved and
stating that the statements it rests on are unchanged. No reading is bound to the brief.

**Not re-stamped.** The restructure does not take either baseline again: each stands at its commit in the table above.
Whether the restructured text carries its baseline unchanged is for a check of the map by a session or person that
wrote none of the restructure. State: OWED.

## Where the current state lives

| Dependency | Where its current state is kept | Where the definition relies on it |
|---|---|---|
| What the design has shown, board by board, and each board's readiness for layout | `v2/docs/CURRENT-EVIDENCE.md` | the brief, "What it is not, today" |
| Every requirement with its reading; the feasibility blockers on the core, FEA-001 to FEA-007, each with its closing evidence and stage | the requirements registry `v2/ecad/tools/pcb_requirements.yaml` and `v2/docs/REQUIREMENTS-TRACE.md` | the brief, "What the first prototype has to show"; CONOPS section 2a |
| EMCON, transmitter by transmitter, against D-05 and REQ-071 | `v2/docs/feasibility/EMCON.md` section 0a; FEA-002, REQ-030 and REQ-071 in the registry | the brief, "What the V2 kit is" (emission discipline); CONOPS M4, sections 4b and 4b.1 |
| Power, thermal and runtime; the hot end; M1's energy balance | `v2/docs/feasibility/POWER-THERMAL.md`; FEA-004, REQ-014 and REQ-072 in the registry | the brief, "What it is not, today"; CONOPS M1 and sections 4a, 4c, 5 and 6 |
| The heat stage's required set on board B (BANK-R1) and the hot stop's path (HOT-R1 on boards A and E) | REQ-052 and REQ-077 in the registry | CONOPS section 4c |
| The kit's fit in the Peli 1450 and the case set the generators carry | `v2/docs/CASE-MARGINS.md`, `v2/docs/CASE-FIT-UNCERTAINTIES.md` and `v2/release/case-2026-09-27/`; FEA-007 in the registry | the brief, "What the V2 kit is" (the pack, the antenna entries); CONOPS section 4a (the pack) |
| ZEROIZE on the fitted secure element | `v2/docs/feasibility/ZEROIZE.md`; FEA-001 in the registry | the brief, "What the V2 kit is" (key protection); CONOPS section 4, ZEROIZE row |
| Each layer of the handover and its reviews | `v2/docs/handover/LAYER-STATUS.md` | the appendix of each document |

## What the two documents carried at their baselines

Moved here word for word on 27 September 2026 from the running text of the two documents at `31cd29b9` (for the
brief, the text baselined at `6b2a9965`; for CONOPS, the text it has carried since `62f26a44`). Each entry is the state
as it stood then, not a current reading: the current state is the source the table above names, and a later change is
recorded there, never by editing the baselines. Paths in the moved text are relative to `v2/docs/`, as in the
documents it came from.
""" % RULE_SOURCE_FULL

STATUS_FROM = {
    "v2/docs/PRODUCT-BRIEF.md": "Eight entries, in the brief's order.",
    "v2/docs/CONOPS.md": "Seven entries, in the document's order.",
}

STATUS_TAIL = ""
