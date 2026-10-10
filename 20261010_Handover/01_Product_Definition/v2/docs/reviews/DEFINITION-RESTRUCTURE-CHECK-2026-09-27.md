# AI check (not a qualified engineering review)

**Subject.** The definition-baseline restructure of `v2/docs/PRODUCT-BRIEF.md` (layer 1) and `v2/docs/CONOPS.md`
(layer 2), MESHSAT-1357, as the independent review of handover H2 asks
(`v2/docs/reviews/2026-09-27-h2-independent-review.md` section 4).

**Commits.** Base `31cd29b9`; branch `fnd/defstab` head `fa89c7c6` (`fa89c7c689eeaf3488b0740f15c51758cee78b8a`), one
commit, not pushed.

**Checker.** A session that wrote none of the restructure, its heads, its status page, its map or its registry
entries, and that assembled none of them. This is an AI check of named items. It is not a qualified engineering
review, it replaces no review a record requires, and it establishes no circuit's correctness. It was written at
2026-09-27 19:22 CEST.

**Scope.** This check covers the carry-over of content only. Were the definitions kept word for word? Is every moved
block status or history? Do the pointers resolve? Do the needs pin and the needs table agree? Is each rebinding note
true? It does not re-judge whether the baselines were right to be baselined, and it re-takes no reading.

Prototype design: no V2 board has been fabricated, ordered or powered, and no kit has been field deployed.

## Files read

| File | At `31cd29b9` (sha256/16) | At `fa89c7c6` (sha256/16) |
|---|---|---|
| `v2/docs/PRODUCT-BRIEF.md` | `d36bf76b3dea8b30` | `026d9ab493d35ed8` |
| `v2/docs/CONOPS.md` | `4483209659dc391c` | `bbcab7c9876f7993` |
| `v2/docs/handover/DEFINITION-STATUS.md` | (absent) | `b28abd0a3c19acd1` |
| `v2/ecad/tools/pcb_requirements.yaml` | diff read in full | diff read in full |
| `v2/docs/REQUIREMENTS-TRACE.md` | diff read in full | diff read in full |

The baseline commits the new heads and the status page name were checked against git. `6b2a9965` holds the brief at
`d36bf76b3dea8b30`, and its parent holds `c1bb3fe5e082b57e`. That commit files
`reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`. CONOPS is `3ff59edc96a3f8f4` at both `79963b3b` and `eb9f9030`,
and `4483209659dc391c` at `62f26a44` and `31cd29b9`. Neither file changed between those commits and `31cd29b9`. The
table "The two baselines" on the status page states these hashes correctly.

## Method (independent of the editor's `moves.json`)

The editor's map and scripts (`drafts/defstab/`) were not used to reach any result below. Every step used the two
git blobs at `31cd29b9` and `fa89c7c6`, with this checker's own scripts, kept in the session scratchpad
`rv-defstab/` (`wdiff.py`, `sentcheck.py`) and not filed.

1. **Word-level diff.** Each old file was diffed against the part of its new file above the heading "Appendix:
   review and status history (not part of the baseline)". The tool was Python `difflib.SequenceMatcher` with autojunk
   off, over whitespace-separated words.
2. **Placement of removed text.** Every removed span was searched for, whitespace-normalised, in the new file's
   appendix and on `DEFINITION-STATUS.md`. A span that joined several blocks was split into sentences and table
   cells, and each piece was searched for separately.
3. **Additions.** Every added span was located. In both files the new heads are the only added words.
4. **Cited line ranges.** Every entry on the status page (B-S1 to B-S8, C-S1 to C-S7) and in both appendices (A1 to
   A4, A1 to A18) cites old lines. Each entry's body was compared with those lines of the old file.
5. **Structure.** Pipe counts were checked row by row against each table header, and paragraphs were counted.
6. **Needs.** The needs table under `## 2. Needs` was compared old against new. The registry's 19 quoted need
   statements were compared with the table's 19 rows. The full sha256 of the new file was compared with
   `needs_document_sha256`.
7. **Pointers.** Every path, section and record id named in the two heads and on the status page was resolved at
   `fa89c7c6`.
8. **Rebinding notes.** Each claim in the three new registry evidence entries was compared with the diff.
9. **Kept cells and paragraphs.** Every kept table cell or paragraph that lost a sentence was read in full at
   `fa89c7c6`, to confirm that what remains still states the definition it stated before.

## Results

### (1) The definition statements are present word for word

- **No word is added, changed or reordered below either head.** No diff operation below the head adds a word: 0 in
  the brief and 0 in CONOPS. Everything below each head equals the original with deletions only. The deletion
  operations match the editor's block counts. The brief has 8 operations below its head plus its head status
  paragraph, 12 blocks in all, because B-S1 with A2, B-S3 with B-S4, and A3 with A4 are adjacent. CONOPS has 22
  operations below its head plus the two head paragraphs, 25 blocks in all, because C-S3 and A13 are adjacent.
- **Where the definition stands.** In the brief, the definition sections are these: the problem, who it is for,
  what the kit is, what it is not today, the constraints fixed by owner rulings, what the first prototype has to
  show, and what the brief relies on outside the repository. They keep every definition sentence.
- **CONOPS definition.** CONOPS keeps all of the following:
  - the actors of section 1 and the needs of section 2;
  - section 2a's core table, its attribute paragraph (SC-04's reading) and its NEED-03 paragraph (SC-02);
  - missions M1 to M5 (M4's setting, sequence, must-hold and D-05 ruling are intact);
  - the modes table of section 4, whose rows keep their definitions; the Transport row still has the kit off with
    its pack fitted and in the gauge's shutdown, and the Storage row still has the pack fitted;
  - sections 4a to 4f; 4b.1 still states the latency as REQ-071, in its table and in the operator's lead, and 4c's
    control table still defines C1 as normal to the reduced mode, then the heat stage;
  - sections 5 and 6, the rulings of section 7, and every row of 7a except the Review A row (see O1).
- **Prototype framing.** Both files keep it: the brief in its framing paragraph, and CONOPS in "Prototype design.
  Nothing described here has been built, powered or field deployed."
- **Kept text read in context.** Where a sentence was cut out of a paragraph or a cell, the text that remains was
  read. It still reads as a statement of the same definition, with the one exception noted as m4.

**Moves that are partly definition.** Two moved blocks carry definition content as well as a result. The same
content is still stated in a kept definition that the brief cites, so no definition is lost from the set. They are
recorded as m1 and m2 below.

### (2) Nothing moved into the status page or an appendix is definition content

| Block | Where it went | Judgement |
|---|---|---|
| Brief A1 (the status paragraph), A2 (the layer 1 criteria map), A4 ("Review A, layer 1", SC-16) | appendix | review history and process, not definition |
| Brief A3 ("Open items that bear on this brief...") | appendix | the closing argument of layer 1 at its baseline. Each product statement its rows rely on is still in the kept text: D-07's two branches, SC-13, D-18, REQ-069, the hot end stated as a requirement, and the night finding. Its reopen conditions are covered by the head's rule and the status page's "nothing is narrowed silently" (see O2). |
| Brief B-S1, B-S3, B-S5, B-S6, B-S7 | status page | results: the headline counts, the transmitter counts, the case set's commit, board readiness, the model runtimes |
| Brief B-S2 | status page | what the EMCON line is drawn to cut "as generated at `45bde541`", a reading of the generated circuit. The ruled meaning (D-05) and the latency (REQ-071) stay in the definition. |
| Brief B-S4 | status page | mostly a result (no bench row; FEA-002), with a design description of the EMCON lamp (m2) |
| Brief B-S8 | status page | a count of open blockers, with SC-04's application to FEA-007 (m1) |
| CONOPS A1, A2 | appendix | status and review history; the Review A gate is process |
| CONOPS A3, A4, A5, A6 to A10, A13, A15, A16, A17 | appendix | dated correction and change notes. Each row's current statement stays in the row. A10's rationale (the pack is bonded; D-14's service lift) is also in 7a's Storage and transport row. |
| CONOPS A11, A12 | appendix | power-model history. A12's last sentence is a current reconciliation between documents (m3). |
| CONOPS A14 | appendix | a statement that three other documents follow section 4c, a current cross-document state (m3). C1 itself is defined in 4c's control table, which is kept. |
| CONOPS A18 (7a's Review A row) | appendix | a process choice, not a product decision (O1). A copy of 7a's header row was added above it so that the lone row renders; that is harmless. |
| CONOPS C-S1 to C-S7 | status page | results: circuit state as generated, transmitter counts, HOT-R1's and BANK-R1's readings on the generated boards, registry closures. The TMP117 fallback that C-S5 mentions is still described in the kept section 4c (7 mentions). |

Every cited old line range was checked (step 4). Each entry's body stands within its cited lines. Two apparent
misses were artefacts of this checker's own block splitting: B-S8's block ran into the next subheading, and A18
carries the added header row. Both were confirmed by reading.

### (3) The pointers left behind resolve

The following all exist at `fa89c7c6`:

- every path named in the two heads and on the status page: `handover/DEFINITION-STATUS.md`,
  `reviews/2026-09-27-h2-independent-review.md` (section 4 carries the rule), `CURRENT-EVIDENCE.md`,
  `REQUIREMENTS-TRACE.md`, `v2/ecad/tools/pcb_requirements.yaml`, `feasibility/EMCON.md` (section 0a present),
  `feasibility/POWER-THERMAL.md`, `CASE-MARGINS.md` and `CASE-FIT-UNCERTAINTIES.md` (both name the case set
  `v2/release/case-2026-09-27/`), `feasibility/ZEROIZE.md`, `handover/LAYER-STATUS.md`,
  `v2/release/case-2026-09-27/`, and the three release records the status page names;
- every record id named: REQ-003, REQ-014, REQ-030, REQ-052 (the closed-lid reduced mode), REQ-071 (the EMCON
  latency), REQ-072 (M1's balance), REQ-077 (the hot stop), FEA-001, FEA-002, FEA-004, FEA-007 and S-37.

No kept text in either definition points at a moved section. The searches were for the open-items section, "Review
A, layer 1", the status paragraph or line, "How this brief answers", "of that name", "last section of this",
"eighteen rows" and the needs-added note, and none was found. The moved sections' headings changed level only, so
their anchors are unchanged.

One pointer does not resolve in the committed tree (m5): the map `drafts/defstab/moves.json`, which the status page
cites.

### (4) The needs table and the CONOPS needs pin agree

- The needs table rows are byte-identical between `31cd29b9` and `fa89c7c6`.
- The full sha256 of CONOPS at `fa89c7c6` is `bbcab7c9876f7993cb6aa7a742c2a871caedf255b7a10e332adf1c81780a7b38`,
  which equals `needs_document_sha256` in the registry at `fa89c7c6`.
- The registry's 19 quoted statements (NEED-01 to NEED-19) equal the table's 19 statements word for word: 0
  mismatches. This comparison was made by this checker, not by the validator.
- In the trace page's header, only the pin changed (`4483209659dc391c` to `bbcab7c9876f7993`).

### (5) Every rebinding note is true

The notes were checked against the diff.

**Bindings.** Exactly three live bindings named CONOPS, and all three now name `v2/docs/CONOPS.md@bbcab7c9876f7993`:
REQ-005, CFL-016 and CFL-014. The other occurrences in the tree are frozen snapshots (candidate patches, the H1 and
H2 releases, records). No live binding names the brief, so none is left stale.

**The move list in all three notes.** The list is the head's status and Review A paragraphs, the paragraph under the
needs table, section 4's row-history sentence, 4a's two model-history passages, 4c's sentence on the three
documents, section 6's replaced-figures paragraph, 7a's Review A row, the correction notes of 2a, of the Transport,
Startup, Charging, EMCON and Storage rows, of 4b's closing paragraph and of section 5's opening paragraph and APRS
row, and the status sentences of M4, 4b, 4b.1 and 4c. It matches the diff exactly: 18 appendix blocks and 7 status
blocks. Section 5's correction note was in its opening paragraph, "The rule the hardware is designed to".

**REQ-005.** In section 2a only the correction note of 26 September 2026 moved. The paragraph "Which peripherals
NEED-03 protects" is unchanged, and the needs table is byte-identical. **True.**

**CFL-016.** The following are all unchanged: section 4's ZEROIZE and Service rows; its Startup and EMCON rows except
for their correction notes, now A7 and A9; 4a's PS-EMCON row; 4b's key and table; 4b.1's table; 4f; and section 5's
hardware interlock sentence. M4 keeps its setting, sequence, must-hold and D-05 ruling. Its four sentences on the gaps
and the counts stand word for word as C-S1. The claim that no kept sentence describes a replaced circuit carries over
from the reading at `4483209659dc391c`, because the kept sentences are unchanged. **True.**

**CFL-014.** The Charging row loses only its S-07 correction note. The 4S strap, the system node, VBAT and the 256 mA
hostless charge are still in the row. Section 5's S4 row is byte-identical. **True.**

Each note also says "every move word for word, no sentence reworded". This check found no reworded or added word
below either head. **True.**

## Findings

None is blocking. Each is minor: none changes the meaning of a definition statement, and none drops a definition from
the set of the two baselines.

- **m1 (brief B-S8; a sentence that carries definition and a result together moved to the status page).** The
  sentence "Seven feasibility blockers on the core are not closed (... FEA-007 the kit's fit in the Peli 1450 on the
  case choices C1 to C6, core as a condition of every core function under the session's SC-04; ...)" carries a
  count, which is a result, and SC-04's application to the fit, which is scope. The editor's stated rule keeps mixed
  sentences in place. This one moved, and after the move the brief's definition names neither SC-04 nor the fit as a
  core condition. SC-04 itself was 2 mentions in the brief at `31cd29b9` and is 0 now.
  - **Why it is minor.** The scope is carried word for word by CONOPS section 2a's kept attribute paragraph, which
    names fitting the boards and the pack into the 1450 as a core condition (NEED-06). The brief's kept scope section
    cites CONOPS section 2a, and the brief's head points to the registry for the core feasibility blockers. The H2
    review also named exactly this count as the coupling to remove.
  - **For the integrator.** Accept the move as it stands, or restore the sentence to the brief. Either way, record the
    choice on the status page.
- **m2 (brief B-S4; a design description moved with a result).** B-S4 carries the result (no row on a bench; FEA-002)
  and also the description of the hardware EMCON lamp: the one firmware-independent EMCON indication, lit while both
  EMCON lines read low, fed ahead of the dimmer and dark in BLACKOUT, with the TX lamp's supply dependency. The
  operator's use of that lamp stays in the kept CONOPS section 4b.1, and PANEL.md sections 1 and 4 define it. The
  brief keeps "indicators" in the operator row. So no operating intention is lost, but the brief no longer describes
  the lamp.
- **m3 (CONOPS A12's last sentence and A14; current cross-document states filed as unmaintained history).**
  - **A12.** The sentence "`feasibility/POWER-THERMAL.md`'s 53.1 W still carries both WiFi link cards ..., which is
    why this table's figure is lower" explains a figure difference that still exists.
  - **A14.** The sentence "Those three documents follow this section since 27 September 2026 ..." states the present
    alignment of three documents. Without it, the kept sentence that they "first took the reduced mode as one module"
    no longer says that they have since followed section 4c.
  - **Assessment.** Neither sentence is definition, and C1 is defined in the kept control table of section 4c. Both
    are status rather than history, though, and they sit in the appendix marked "Nothing below is maintained" instead
    of on `DEFINITION-STATUS.md`.
- **m4 (brief, "Not a finished runtime figure"; a kept sentence lost its antecedent).** After B-S7 moved, "None of
  these is a claim." follows the TBD runtime values instead of the model figures it originally qualified. It still
  claims nothing, so its meaning is not reversed, but its referent is now vague.
- **m5 (a pointer that does not resolve in the committed tree).** `DEFINITION-STATUS.md` cites
  `drafts/defstab/moves.json` and its scripts "in the branch's worktree". They are untracked at `fa89c7c6`, and
  `v2/docs/records/defstab/` does not exist. The editor declares this owed at integration; until the files are filed,
  the committed page names a map a reader of the tree cannot open. The registry's three new evidence entries name the
  same draft path.
- **m6 (new head text, outside the carry-over).** Both heads and the status page's rule attribute to the H2 review,
  section 4, a rule stated as reopening "only when a requirement, the scope, the operating concept or a product
  decision changes". The review's own words are "a requirement, scope, operating concept or other relevant decision".
  "A product decision" is narrower than "other relevant decision". Align the wording with the source, or say that it
  is the session's reading.

## Observations (no action needed for the carry-over)

- **O1.** CONOPS 7a's Review A row moved. It was the last row, so 7a's positional statement "Rows seven to nine are
  the case choices" still holds, and the registry keeps the choice. 7a's intro says a corrected or withdrawn choice
  keeps its row. This row was neither corrected nor withdrawn but relocated, which is consistent with it being a
  process choice.
- **O2.** The brief's commitment that "nothing is narrowed silently" now stands on the status page ("The rule") and in
  the brief's appendix, not in the brief's own head. The head's reopen rule covers the same triggers.
- **O3.** EQ-27 option (c), the re-read of the five layer 1 pages at every integration with a stale line corrected by
  issuing the brief again, now sits in the brief's appendix A1. ENGINEERING-QUESTIONS.md and LAYER-STATUS.md still
  carry it. Under the new head, a figure inside a kept sentence is a baseline value, not a stale line. The integrator
  should state on LAYER-STATUS layer 1 which rule governs the re-read from now on.

## Verdict

**CONTENT_PRESERVED.**

Both definitions are present word for word. Every moved block is status or history, except the two partly definition
sentences of m1 and m2, whose definition content is still stated in the kept CONOPS text that the brief cites. The
pointers resolve, except the owed map (m5). The needs table, the registry's quoted needs and the pin agree. The three
rebinding notes are true.

This record is the check of the map that `DEFINITION-STATUS.md` records as OWED. It supports re-stamping the
restructured files as carrying their baselines once the integrator has answered m1 and m5; m2, m3, m4 and m6 can be
taken at the same time or left as recorded.
