# MeshSat field kit V2: status of the nine pre-PCB layers

Written 27 September 2026 (MESHSAT-1357) from a layer-by-layer audit of the repository at commit `e3aedb25`
(`e3aedb25c849dbda931888b27093ac6c444621cb`), and brought forward edition by edition since. Every status,
acceptance verdict and citation of that audit (Appendix A since after H2) is as judged at that commit; paths are
repository paths, and its "file:line" citations are lines at `e3aedb25`. This page is the layer
view that `v2/docs/EXECUTION-PLAN.md` line 18 names. It is a view over the existing records, never a second
registry: requirements stay in `v2/ecad/tools/pcb_requirements.yaml`, decisions in `v2/ecad/tools/pcb_decisions.yaml`,
evidence classes in `v2/docs/CURRENT-EVIDENCE.md`.

**At H3** the section "Status at handover H3" is the current status. It is short: H3's design is H2's, so it states
what H3 changes and leaves the H2 section's rows for layers 4 to 9 and its layout-entry table as the status they are.

**How to read this page after H2.** Three strata, newest first. (1) The section "Status at handover H2" is the current
status (**H3:** with the H3 section above it): one row per layer with the evidence for its status and what remains, and the per-board layout-entry reasons.
(2) Each layer's own section (Layer 1 to Layer 9) opens with its status and **a short acceptance table at H2**, item
by item under the audit's numbering: MET, PARTLY or **OPEN**, with the record or commit behind it or what remains
(added after H2, the H2 usability check's minor finding 10). For layers 1, 2 and 3 the table follows their release
checks; for layers 4 to 9, which no release check has judged, it is this page's reading of what landed since
`e3aedb25`, each line naming its commit or record. (3) **Appendix A** holds, per layer and moved byte for byte, the
audit at `e3aedb25` (acceptance tables with their inline **Superseded in H1** marks, deliverables, cycles, actions,
per-board lines) and the layer's `INTEGRATOR LINE`, the running record H1 to H2, oldest step first, its last step
marked **H2**. **The audit's file:line citations are lines at `e3aedb25`**, not at the snapshot: open the cited file
at `e3aedb25` on the public repository (`https://raw.githubusercontent.com/meshsat/meshsat-fieldkit/e3aedb25/<path>`)
to follow one. The sections "Status at handover H1" and "Summary at `e3aedb25`" are kept as history. Where the
acceptance table at H2 and the appendix differ, the table is the newer; where either differs from a record it cites,
the record governs. The internal names used here are defined in `v2/docs/handover/GLOSSARY.md`. The counts of the design's
state in the H2 section (the layout-entry reasons, the registry's counts, the BOM rows, the questions) are printed by
`v2/docs/records/h2/handover_counts.py` from the files of the snapshot (its output is `handover_counts.out` beside it);
every other figure names the commit it comes from.

**Prototype framing.** No V2 board has been fabricated, ordered, assembled, powered or measured. Every review of the
current design so far is an AI review (an author session and a separate refuting session), labelled as such; none of
it is electrical sign-off.

**What the statuses mean** (the owner's execution prompt, `v2/docs/reviews/2026-09-27-handover-execution-prompt.md`
sections 2 and 3). COMPLETE means complete for the layer's own engineering purpose, with its acceptance items met, its
required review held and a versioned package another engineer can use; it never means a later physical test has
passed. IN_PROGRESS means work remains and at least part of it can proceed. BLOCKED means nothing that closes the
layer can proceed without an outside step. NOT_STARTED means no deliverable exists.

**At `e3aedb25` no layer is COMPLETE.** All nine are IN_PROGRESS. **In H2, layers 1 and 2 are COMPLETE** for their
own engineering purpose and layers 3 to 9 are IN_PROGRESS (section "Status at handover H2"). **After H2, layer 3 is COMPLETE** in the commit that files `v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md` (branch `fnd/l3rb`; the H2 files carry it IN_PROGRESS, and its package is the next snapshot, H3). **In H3, layers 1, 2 and 3 are COMPLETE** and layers 4 to 9 are IN_PROGRESS; the commit that made layer 3 COMPLETE is `24e7bf5a`. **FOUNDATIONS_BASELINED keeps its recorded scope**
(`v2/docs/EXECUTION-PLAN.md` line 3 and lines 58 to 66: the product definition, the requirements with their
verification method, the architecture and budgets, the interface contracts and the review of parts and circuits,
gated by Reviews A to D). It is not reached, and nothing on this page uses it to imply that the nine layers or a
fabrication package are complete. No percentages appear here: where a layer is not COMPLETE, its remaining acceptance
items are listed.

**Integrator lines.** Each layer's record in Appendix A ends with a line marked `INTEGRATOR LINE`. When a closer
finishes an item, the integrator updates that line (status now, the commit, the items closed with their evidence) and
the layer's acceptance table at H2, and leaves the `e3aedb25` record above the line unchanged, so the history stays
readable.

**Who the "workers" are.** The worker names are the current session's division of work: the *integrator* is the
single writer who merges and commits (standing condition 4, one writer per shared file) and acts as docs, records and
registry writer; a *fresh checker* is an agent or person who did not write what it checks (an AI checker's result is
labelled AI review); the *board streams* r8a, r8b, r8c, r8d, r8e and r8p are the circuit round 8 authors per board,
*r8bat* the battery stream, the *tools stream* (ts-net, r8cert) the checker authors, and the *parts*, *case*,
*power* (rv-pwr) and board B *placement* streams are named for their subject. Their work at `e3aedb25` exists only in
unmerged branches (`fnd/<name>`), which a snapshot does not carry. An incoming team maps these roles to its own
people. "Owner" means the project owner, who alone decides money, outside contact, publication and promotion.

**Blocked questions** are written out once each in `v2/docs/handover/ENGINEERING-QUESTIONS.md` (EQ-01 to EQ-14 at `e3aedb25`; **superseded in H1, see the integrator lines**: EQ-01 to EQ-21, round 8 added EQ-15 to EQ-21) and
referred to here by id. **After H1.1 (set 4):** EQ-22 to EQ-24 are added and EQ-05 carries the hot stop. **The second release attempt (27 September 2026):** EQ-13 is rewritten as what the session took (SC-21) and EQ-26 is added. **The release finalizer (27 September 2026):** EQ-27 to EQ-29 are added, the items the second release check left on layers 1 and 3. **The finalizer of the targeted fix (27 September 2026):** EQ-27 is answered, EQ-28 is reopened and EQ-30 is added, the narrow verification's finding on layer 3. **In H2:** EQ-01 to EQ-30, thirty questions (18 design work, 5 physical evidence, 7 external authorisation), with the index's last column restated at H2. **After H2 (branch `fnd/l3rb`):** EQ-28 and EQ-30 are answered by the re-baseline of layer 3 and its re-check, and EQ-29's package for layer 3 is the next snapshot, H3.

**Board names.** Boards are named by letter and declared phase (A32, B21, C24, D12, E17, E5, P4, from
`v2/ecad/tools/boards/<x>.json`). "Board B" means the three-module compute board of the current generation (B16
onward); the single-module B12 to B15 folders under `v2/release/revA/boards/` belong to an earlier generation.

## Status at handover H3 (prepared 27 September 2026)

**This section is the current status.** H3 is the fourth handover snapshot, filed as `v2/release/handover/H3.zip` with
`H3.zip.sha256` and `H3.MANIFEST.tsv` beside it; its `SOURCE.txt` names the one commit every file of it comes from, and
`v2/docs/handover/RELEASE-H3.md` is its release record. **Layers 1, 2 and 3 are COMPLETE, layers 4 to 9 are
IN_PROGRESS, and none is BLOCKED as a whole.** COMPLETE means complete for the layer's own engineering purpose; it
never means a physical test has passed, and no V2 board has been built. Every review named is an AI review or an AI
check, labelled as one, and none is a qualified engineering review.

**H3's design content is H2's.** Between H2's source commit `b89b50b4` and H3's, no schematic, netlist, intent, land,
generator, board table, checking tool, export, CAD file, diagram or maker document changed
(`v2/docs/records/h3/design_difference.out`, which lists the eleven files under `v2/ecad/` that did: the packer and
its test, two registries and INT-001's seven tracked readings). So the H2 section below, with its notes "after H2",
stays the status of layers 4 to 9 and of every board, and this section states only what H3 changes. Its counts are
printed by `v2/docs/records/h3/handover_counts.py` (`handover_counts.out` beside it).

| Layer | Status in H3 | What H3 changes in the H2 section's row |
|---|---|---|
| 1. Product definition | **COMPLETE** | the definition baseline stays `6b2a9965`. `v2/docs/PRODUCT-BRIEF.md` was re-stamped BASELINED at `a9f212c7` by an editorial restructure with no definition change: the check of the restructure, `v2/docs/reviews/DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md` (an AI check, sha256/16 `4c09af64cb214448`), reads CONTENT_PRESERVED. The file H3 carries is `85513b92ed0daf55`; its changing results stand word for word in `DEFINITION-STATUS.md` |
| 2. Concept of operations | **COMPLETE** | the definition baseline stays `79963b3b`. `v2/docs/CONOPS.md` was re-stamped BASELINED at `a9f212c7` the same way, on the same check; the file H3 carries is `6ebe6760c4312bca`, its needs table byte-identical, the registry's pin on it and the three readings bound to it re-taken |
| 3. Requirements | **COMPLETE** since commit `24e7bf5a` | the registry reads `baseline_state` BASELINED at `a54b793b`, written in `2c12be91`, and the re-check `v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md` (an AI check, `7831358b96b6f5ca`) finds B-1 CLOSED at `2c12be91`; S-51, S-78 and S-80 are closed. Acceptance item 3.18, the versioned package: met by the H3 snapshot cut from this commit's successor (the integrator confirms it in `RELEASE-H3.md`; the registry H3 carries still lists S-79 as open, and it is closed in the commit that files the snapshot). At H3 the registry holds 144 records, 58 open and 53 closed items |
| 4 to 9 | IN_PROGRESS | nothing: each layer's row of the H2 section is its status |

**Layout entry at H3** is the H2 section's table, unchanged: **0 boards ready for layout, 40 reasons** (A 7, B 7, C 5,
D 8, E 5, P 6, E5 2); `v2/docs/CURRENT-EVIDENCE.md` is the same file (sha256/16 `7a834fe55aea6ccd`).

**Known gaps.** Those of H2 hold in H3, with two differences: `v2/cad/render/scene.py` is bundled, so the diagrams'
manifest check is expected to read from the ZIP what it reads in the repository (gap 6; not run on an H3 build), and
the layout constraint sheets' power tables are bound to H3's netlists (gap 8). **Errata:** what H3 knowingly does not
fix is listed once, in `START-HERE.md` section 1a (the constraint sheets' other sections at `e3aedb25`; this page's
mix of status and history; the re-take in a repository built from the ZIP; the questions page not re-read row by row;
the set 6 candidate; board A's external-port declaration).

**Outside H3.** A circuit candidate, set 6, stands on branch `fnd/r8int6`, not promoted: it draws remedies for several
items this page lists as open (EQ-25 on board C, HOT-R1 on A and E, PWR-001's declarations on C and P and the flyback
diodes on D and E, BAT-001's table on P, E5's INT-001). The integrating session reports its suite on the KiCad host at
2010 passed, 1 failed, 3 skipped, the failure a checker's false positive under repair. Five desk streams, wave 5a, are
being recovered from their transcripts. None of it is in H3, and none of it is evidence until it is checked and
promoted.

## Status at handover H2 (27 September 2026)

**This section was the current status at H2; at H3 the section above is, and it keeps this section's rows for layers
4 to 9 and its layout-entry table as the status. The sections after this one are history.** H2 is the third handover snapshot, filed
as `v2/release/handover/H2.zip` with `H2.zip.sha256` and `H2.MANIFEST.tsv` beside it; its `SOURCE.txt` names the one
commit every file of it comes from, on branch `fnd/h2`. Its design is main `62f26a44` plus that branch: board B's
round 8 (`b76c18cb`, integrated in `cc3313f3`); set 4, the layer 2, 3, 5 and 7 closers and the re-take driver
(`e5fde2ed` to `c351115d`, integrated in `f2b7fa66`); set 5, wave 3 on boards A, B, D and E (`ffca0771`, `caba1876`,
`b7f96784`) with the RF-002 tool row (`e2aab014`) and the diagrams (`730f8489`), integrated in `a7b5872e`; the
consolidated re-take of every schematic-phase reading (`8ea7867e`, installed on main in `5ca81eea`); the release
checks and attempts of layers 1 to 3 (`6209ec7e` to `62f26a44`); and on `fnd/h2` the targeted fix of layers 1 and 3
(`cecfd0f1`, `3e4799eb`), its narrow verification (`6b2a9965`), the claims screen re-taken after it (`763bccdf`) and
the H2 exports (`c5d09c78`). The last design change is `b7f96784`, the last tool change `7dfbfb16`. **H2 is a partial
handover: layers 1 and 2 are COMPLETE, layers 3 to 9 are IN_PROGRESS, and none is BLOCKED as a whole.** COMPLETE means
complete for the layer's own engineering purpose (the owner's execution prompt, section 2); it never means a later
physical test has passed, and no V2 board has been built. Every review named here is an AI review, labelled as one,
and none is a qualified engineering review. **After H2 (branch `fnd/l3rb` from main `ef144760`):** layer 3 is COMPLETE in the commit that files the re-check of its re-baseline (its row below); the H2 files carry it IN_PROGRESS, and its versioned package is the next snapshot, H3.

| Layer | Status in H2 | Evidence for the status | What remains (owner) |
|---|---|---|---|
| 1. Product definition | **COMPLETE** since `6b2a9965` | `v2/docs/PRODUCT-BRIEF.md` BASELINED in `6b2a9965` (**H3:** re-stamped BASELINED at `a9f212c7`, an editorial restructure with no definition change, `v2/docs/reviews/DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md`, CONTENT_PRESERVED; `6b2a9965` stays the definition baseline). Review records, each an AI review: Review A, layer 1 (`v2/docs/reviews/REVIEW-A-LAYER-1-2026-09-27.md`, two passes, the second with no blocking finding); the release check (`REVIEW-LAYER-1-RELEASE-2026-09-27.md`, FAIL on B1 to B3, fixed in `08f3665a` and `7dfbfb16`); the second release check (`REVIEW-LAYER-1-RELEASE-2-2026-09-27.md`, FAIL on R2-B1 alone); the narrow verification (`TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`, sha256/16 `ae70b1a7811ecea1`: R2-B1 and R2-m1 CLOSED at `3e4799eb`, no new contradiction). The versioned package, acceptance item 14: this snapshot | nothing for the layer's own purpose. Carried, not holding it: the minors R2-m2 to R2-m7 (with m3, m6 and m9); the verifier's observation (d) and W3T-F1's name in the FEA-002 row, at the brief's next issue (the integrator); the fresh usability check of H2 (the owner's section 7). The layer reopens for that item only if FEA-002, FEA-004, FEA-007 or REQ-072 closes against the design |
| 2. Concept of operations | **COMPLETE** at `79963b3b` (recorded in `62f26a44`) | `v2/docs/CONOPS.md` BASELINED (**H3:** re-stamped BASELINED at `a9f212c7`, an editorial restructure with no definition change, on the same check, CONTENT_PRESERVED; `79963b3b` stays the definition baseline. Since the restructure CONOPS is no longer byte-identical to the file the release check read: its definition is kept word for word, and every block that moved is mapped in `v2/docs/records/defstab/moves.json`); at H2 CONOPS, `OPERATING-ENVELOPE.md`, `TEST-PLAN.md` and `pcb_envelope.yaml` byte-identical to the files the second release check read. Review records, each an AI review: Review A, layer 2 (`REVIEW-A-LAYER-2-2026-09-27-pass1.md` and `REVIEW-A-LAYER-2-2026-09-27.md`: FAIL, then P2-B1 and P2-B2 answered by c23); the release check (`REVIEW-LAYER-2-RELEASE-2026-09-27.md`, FAIL on B1 to B4, answered in `08f3665a` and `7dfbfb16`); the second release check (`REVIEW-LAYER-2-RELEASE-2-2026-09-27.md`, no blocking finding). The versioned package: this snapshot | nothing for the layer's own purpose. Carried, not holding it: M-02 and S-53 (EQ-13), BAT-F19 (EQ-26), HOT-R1 (S-57, EQ-22), S-58 (EQ-23), FEA-004 (EQ-05), BANK-R1 (S-54), S-55, REQ-069 (EQ-03); the minors n1 to n6, n9, n10 and m1 to m16 (the integrator, the TEST-PLAN owner, the registry writer, the layer 5 writer). The layer reopens for that item only if FEA-004 ends in an owner trade on D-02b's closed-lid scope or M-02 picks a different pack |
| 3. Requirements | **COMPLETE** in the commit that files `v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md`, `24e7bf5a` (after H2, branch `fnd/l3rb`; the H2 files carry it IN_PROGRESS) | `pcb_requirements.yaml` validates (144 records, 0 errors, 0 warnings in a git checkout holding the registry's closing commits and the gitignored readings; from the ZIP alone 13 errors and 17 warnings, 0 and 17 once REGENERATE.md section 1a's documents are restored, and in a repository built from the ZIP 30 errors, the closed-by-commit checks among them: REGENERATE.md section 7 gives each count's condition; added after H2) and reads `baseline_state` BASELINED at `a54b793b`: S-80's wording fix in `a54b793b` (CON-010's newest entry ends FAIL on W3T-F1, the header names `79963b3b`'s re-take on CON-010 and REQ-044, the trace page re-rendered; S-81 added) and the baseline in `2c12be91` (S-51, S-78 and S-80 closed; `v2/docs/records/l3rb/rebaseline_difference.out`, ALL ASSERTIONS HOLD). Review records, each an AI review or check, all five in `baseline_reviews` by sha256/16: Review B (`REVIEW-B-LAYER-3-2026-09-27.md`), the release check (`REVIEW-LAYER-3-RELEASE-2026-09-27.md`, NOT COMPLETE on R1 to R5, all answered since), the second release check (`REVIEW-LAYER-3-RELEASE-2-2026-09-27.md`, NOT COMPLETE on the procedural B-1 and B-2), the narrow verification (`TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`, `ae70b1a7811ecea1`: B-1 NOT_CLOSED on one unstated difference) and the re-check (`TARGETED-RECHECK-LAYER-3-2026-09-27.md`, `7831358b96b6f5ca` as filed: B-1 CLOSED at `2c12be91`, its three remedies, the baseline, the closures and the absence of any other registry difference each PASS). A record closure: it closes no electrical defect. The versioned package, acceptance item 3.18: the next snapshot, H3 (S-79, EQ-29); **H3:** met by the H3 snapshot cut from this commit's successor, which the integrator confirms | nothing for the layer's own purpose but its package: H3, cut from the pushed commit that carries this row, closes S-79 and EQ-29 (the integrating session). Carried, not holding it: the release-2 record's minors n2 to n9 and the first check's m1 to m10, with both records' section 6 notes; REQ-077 FAIL until HOT-R1 (S-57); GND-002 unruled (layer 4); S-81 (layer 1's writer). The layer reopens if a record's statement, acceptance, applicability, allocation, verification or release effect changes, which the registry header makes a change to the baseline needing its own review. Owner: the integrator as registry writer |
| 4. System architecture | IN_PROGRESS | seven feasibility records, FEA-001 to FEA-007, each FEASIBILITY_OPEN, core and INCONCLUSIVE. Merged since H1: board B's failover fabric FAB-01 to FAB-04 and EMCON remedies (`b76c18cb`), board A's EMCON gates behind their own eFuse (`ffca0771`, EQ-17 closed at desk with its tOVLO bound), C1 defined one way (`7dfbfb16`), FEA-007 (`c351115d`), every diagram on set 5's netlists (`730f8489`) | FEA-001 to FEA-007 on their named evidence (EQ-01, EQ-02, EQ-05 to EQ-08, EQ-10); Review C, not held; W3T-F1 (S-64, EQ-25); BAT-F20 (S-46, EQ-15); S-58 (EQ-23); REQ-072's night (S-53, M-02); `feasibility/EMCON.md` section 5a row 5; GND-002; the qualified reviews R-BAT, R-PWR and R-HSD (EQ-10 to EQ-12); the diagrams' manifest re-stamped (known gap 6). Owner: the integrator and the blockers' owners |
| 5. Partitioning and interfaces | IN_PROGRESS | merged since H1: the closer hc5 (`0da2778b`: `HW-FW-CONTRACT.md` version 1, 30 contracts in `pcb_interfaces.yaml`, the kit I2C budget CON-026 FAIL at desk), SC-58 to SC-63 and the hot stop's firmware rows (`7dfbfb16`), the dock's VIN_RAW on four power pins (SC-55, `b7f96784`: EQ-16 answered at desk for the supply side); INT-001 re-taken on the committed netlists (the re-take) | the first twelve contracts' pass-2 fields; S-59 to S-62 and HF-F08; the SLOT_EN hold; GND-002; D-07's site on A; S-74 and S-75 (EQ-16's E5 fit and ground return); E5's INT-001, the one schematic-phase reading the re-take leaves AWAITING_REVALIDATION (the coverage map to name `check_contracts_e5`, registry writer); HOT-R1 with IF-AE-DOCK pin 12 (S-57); PANEL.md's reduced-mode and hot-stop duties; Review C; EQ-12. Owner: the integrator and the board A, B, D and E authors |
| 6. Components | IN_PROGRESS | merged since H1: board A's and B's part entries for set 5 in `SOURCES.yaml` (`ffca0771`, `caba1876`), W3B-F1 and W3B-F2 drawn on B, decision 42's class and the maker's clause on every one of B's 277 decoupling entries | no MPN field: 1630 of the 2393 per-reference rows of the six H2 BOMs carry no LCSC code, 1446 of them resistors, capacitors and inductors (EQ-21); S-65, S-71 to S-73, S-76; carried from H1 and not re-checked in H2: hc6's recommended part changes, `pcb_part_temps.patch`, PROCUREMENT's readings, U8 (EQ-06), R-PWR (EQ-11), the two OUTSIDE grades, the INFERRED order codes, `PARTS.md`. Owner: the parts writer and the board authors |
| 7. Mechanical and enclosure | IN_PROGRESS | merged since H1: the closer hc7 (`c351115d`: C1 to C6 in the generators and CAD, `v2/release/case-2026-09-27/`, `CASE-FIT-UNCERTAINTIES.md`, FEA-007 and L-07; **restated after H2:** FEA-007 holds the layout entry of A, B, D, E, E5 and P, D and E5 on its desk items alone, A, B, E and P on their desk items and the mock-up; C is not held by it at layout entry) | the mock-up purchase (L-07, EQ-08) and the heat test before it (EQ-05); the QMX lid tray (S-63, EQ-24); the jumper plug (M17g, M17x), the pack hold-down (S-27), the sealed RJ45; the superseded face drawings; the "single source" wording and `scene.py`'s typed QY; E5's targets and holes (S-74). The ZIP cap it named is answered in H2 (the superseded candidate patches referenced). Owner: the case writer and the integrator |
| 8. Schematics | IN_PROGRESS on every board | round 8 on all six boards with a schematic (board B at `b76c18cb`), set 5 on A, B, D and E; regeneration PARITY on all six on KiCad 9.0.9 and the H2 exports (`c5d09c78`); every schematic-phase reading current on the committed netlists but E5's INT-001 (the re-take, `8ea7867e`) | per board, the layout-entry reasons below; then the functional circuit review per board (Review D); decision 31's protection review on A, D and E; HOT-R1 on A and E (S-57); EQ-25 on C; BAT-F20 (S-46) and the pack-protection table on P (REQ-044); S-47's item 10 on E; the qualified reviews (EQ-10 to EQ-12). Owner: the board streams and the integrator |
| 9. Pre-layout design analysis | IN_PROGRESS | PWR-001 and SI-001 read on the committed netlist of every board (the re-take); the constraint sheets and the stackup record of H1, **stale against the H2 intents in H2 itself and re-bound to the H2 line after H2** (known gap 8) | SI-001 INCONCLUSIVE on all six boards with a schematic until the edge rates their drivers' makers do not publish are declared (known gap 5); the drafts hc9 left for other owners; board E's pack-path bands (2 oz declared, 1 oz board); PWR-F12 at 18 A for 60 s on E, E5 and P; the heat test (EQ-05), F2 (EQ-07), prices (EQ-14), channel budgets (EQ-12). Owner: the integrator and the board streams |

**Layout entry at H2** (`v2/docs/CURRENT-EVIDENCE.md`, generated, sha256/16 `7a834fe55aea6ccd`): **0 boards ready for
layout, 40 reasons** (101 before the consolidated re-take): 15 current readings that are not a PASS (the design's or its
declarations' answer), 1 deciding verification still owed (E5's INT-001), 3 decision 31's protection review (A, D, E)
and 21 layout-entry stages of the feasibility blockers FEA-001 to FEA-007. No row is left that a re-take alone would
make current. The RF-002 FAIL on boards A to D is the fail-safe level of `TX_INHIBIT_n` with board C unpowered
(EQ-25; its recommended remedy is one resistor changed and one added on board C).

| Board | Reasons | Each reason |
|---|---:|---|
| A | 7 | SI-001 INCONCLUSIVE; RF-002 FAIL; decision 31's protection review; FEA-002, FEA-004, FEA-006, FEA-007 |
| B | 7 | SI-001 INCONCLUSIVE; RF-002 FAIL; FEA-001, FEA-002, FEA-003, FEA-006, FEA-007 |
| C | 5 | PWR-001 FAIL (among its failures, four power nets no rail declares: C_DVDD, EPD_VCC, LED_RAIL, LED_RAIL_SW); SI-001 INCONCLUSIVE; RF-002 FAIL; FEA-002, FEA-006 |
| D | 8 | PWR-001 INCONCLUSIVE (RLY_K, S-76); SI-001 INCONCLUSIVE; RF-002 FAIL; decision 31; FEA-002, FEA-004, FEA-006, FEA-007 |
| E | 5 | PWR-001 INCONCLUSIVE (FAN1_SW and FAN2_SW, S-76); SI-001 INCONCLUSIVE; decision 31; FEA-006, FEA-007 |
| P | 6 | PWR-001 FAIL (among its failures, BAT_F, PBI, SEC_VDD, SW and VCC_F, power nets no rail declares); SI-001 INCONCLUSIVE; BAT-001 FAIL (the gate's table `pcb_pack_protection.yaml` still describes the old generator, REQ-044); FEA-005, FEA-006, FEA-007 |
| E5 | 2 | INT-001 PASS, AWAITING_REVALIDATION (UNBOUND); FEA-007 |

**Known gaps of H2** (START-HERE section 3 gives each with its effect): (1) the readings the status pages render live
in gitignored `out/` folders, and their tracked copies under each phase's `routed/` are left out with the stale layout
verdicts beside them; (2) the test suite needs a git checkout; (3) the ZIP is deterministic per host only; (4) maker
documents and the superseded candidate patches are referenced, not bundled; (5) SI-001's edge-rate declarations are
owed on every board; (6) the diagrams' `build.py --check` reads 6 of 11 current in the repository because
`ARCHITECTURE.md` changed outside its Mermaid blocks (`extract_mermaid.py --check` reads the sources current), and 4 of
11 from the H2 ZIP, whose `pack.yaml` excluded `v2/cad/render/scene.py`, an input of the two case drawings (bundled
after H2; after H2 the repository reads 5 of 11, the control-lines drawing's input `pcb_interfaces.yaml` having changed
in its `read_at` header only); (7) Q-B-ESC-1's final boards are not in the package; (8) added after H2: the layout
constraint sheets were bound to `e3aedb25`'s netlists and intents (board A's VIN_RAW read 12.31 A there against 14.10 A
at H2), and are re-bound to the H2 line after H2.

## Status at handover H1 (27 September 2026)

**History since H2: this section was the current status of H1 and H1.1; the section above replaces it.** H1 is the first
handover snapshot (`v2/release/handover/H1/`, its `SOURCE.txt` names the commit it was built from). The design as it
stands in H1 is main `84e52461` (circuit round 8, sets 1 and 2: boards A, C, D, E and P regenerated; the netlist
tools PWR-001, SI-001 and RF-002; the pack's temperature ladder) plus the handover branch `fnd/h1`, whose last design
change is `99cde56b` (the layer 6 records); after it come only the schematic exports of every board at `99cde56b`
(`v2/release/handover/_generated/`, regeneration PARITY on all six) and these pages. Each layer's `INTEGRATOR LINE`
below says what moved since `e3aedb25` and what remains. **H1 is a partial handover: no layer is COMPLETE.**

| Layer | Status in H1 | Merged since `e3aedb25` | What remains (the layer's own section and its integrator line give each item) |
|---|---|---|---|
| 1. Product definition | IN_PROGRESS in H1; **COMPLETE** since the narrow verification of the targeted fix (the commit that files `v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`, AI check, R2-B1 and R2-m1 of `v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md` CLOSED at `3e4799eb`; the brief BASELINED; the layer 1 integrator line gives the evidence) | closer hc1 (`2ef6aa2a`); Review A, layer 1 (AI review) second pass with no blocking finding; after H1.1 both release attempts and the targeted fix (`cecfd0f1`) | in H1: layer 2's EMCON and face text in `CONOPS.md` and `PANEL.md` (Review A finding I5), then the brief BASELINED; the fresh usability check of the snapshot; now: nothing for the layer's own purpose, the package being the H2 snapshot (S-79) and its usability check; the carried minors stay with their owners |
| 2. Concept of operations | IN_PROGRESS in H1; **COMPLETE** since the second release check (at `79963b3b`, `v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md`, AI review, no blocking finding; the layer 2 integrator line gives the evidence) | round 8's pack temperature ladder (`dd39fb15`, `73d5df1e`); after H1.1 the closer hc2 with c23 (`95e078a1`) and both release attempts | in H1: the closer hc2 was a candidate in its worktree (Review A, layer 2, second pass FAIL on P2-B1 and P2-B2); now: nothing for the layer's own purpose, the package being the next handover snapshot; the records' minors and the later-stage items stay with their owners |
| 3. Requirements | IN_PROGRESS | registry entries of hc1, hc9 and hc6 and of round 8 (S-43 closed, S-46 BAT-F20, S-47 HC9-E1); after H1.1 hc3 with c23, both release attempts and the targeted fix (`cecfd0f1`, the baseline `3e4799eb`, reversed by the narrow verification) | in H1: the closer hc3 is a candidate, its first review running when H1 was cut; Review B; now: the narrow verification's finding on B-1 (S-80, EQ-30: CON-010's newest entry against its FAIL, and `79963b3b`'s re-take unstated in the registry header), then a re-check of that wording fix and the re-baseline (S-51, S-78, EQ-28); the package (S-79, EQ-29) |
| 4. System architecture | IN_PROGRESS | diagrams of hc4, rebuilt on round 8 by w3g and on set 5 at the r8int5 integration (drawn at `b7f96784`, committed at `730f8489`); hc6's supervisor reconciliation; round 8's EMCON gating on A, C and D | FEA-001 to FEA-006; BAT-F20; Review C |
| 5. Partitioning and interfaces | IN_PROGRESS | R8E-N01 recorded in `pcb_interfaces.yaml` (round 8) | the closer hc5 is a candidate: its first review had three blocking items, a second review running when H1 was cut |
| 6. Components | IN_PROGRESS | closer hc6 (`99cde56b`), review with no blocking item | no MPN field in any generator (1497 of 2205 BOM rows without an LCSC code); the recommended part changes; U8; R-PWR; two OUTSIDE grades |
| 7. Mechanical and enclosure | IN_PROGRESS | board E's blind-mate clamp bar (`45f6d83f`) | the closer hc7 is a candidate: first review with three blocking items, its second pass running when H1 was cut |
| 8. Schematics | IN_PROGRESS on every board | round 8 on A, C, D, E and P; exports and regeneration parity of all six at `99cde56b` | board B's round 8 is not merged; PWR-001 FAIL on A, B, D and E; the consolidated re-take; functional reviews; HC9-E1 on E; BAT-F20 on P |
| 9. Pre-layout design analysis | IN_PROGRESS | per-board layout constraint sheets and the stackup record (hc9) | HC9-E1; the drafts hc9 left for other owners; the heat test, F2 and prices; channel budgets |

**Layout entry at H1** (`CURRENT-EVIDENCE.md`, generated): 0 boards ready; reasons A 17, B 16, C 11, D 15, E 16, P 15,
E5 5. **Round 8 findings that are new since `e3aedb25`** are ENGINEERING-QUESTIONS EQ-15 to EQ-21.

**Candidates left in worktrees** (branches `fnd/<name>` from `e3aedb25`, r8b from `fc144600`, never pushed; the
integrating session merges each once its last review has no blocking item). **Since H1.1 each is bundled as an
UNACCEPTED candidate patch**, `v2/docs/handover/candidates/<name>.patch`, with its base commit, sha256 and the last
review's blocking findings written out in `v2/docs/handover/candidates/README.md`. A step on this page that says
"merge r8b" or "after the r8b merge" means: apply `candidates/r8b.patch` to `fc144600` and merge it with regeneration
parity; the same holds for hc2, hc3, hc5 and hc7. The table's last column is the state when H1 was cut; the README
gives the state at export (hc2, hc5 and hc7: second review FAIL with two blocking findings each; hc3: first review
FAIL with six; r8b: second check with no blocking finding).

| Closer | Layer | Files | Review state when H1 was cut |
|---|---|---|---|
| hc2 | 2 | `CONOPS.md`, `OPERATING-ENVELOPE.md`, `PANEL.md`, `TEST-PLAN.md`, `pcb_envelope.yaml`, Review A layer 2 record | first pass FAIL (B1 to B7), second pass FAIL on P2-B1 (CONOPS section 7 row D-02b carries session choices as an owner ruling) and P2-B2 (nothing protects the pack once the heat stage fails on an input) |
| hc3 | 3 | `pcb_requirements.yaml`, `REQUIREMENTS-TRACE.md`, `pcb_board_facts.yaml`, `pcb_energy_chain.yaml`, `pcb_pack_protection.yaml`, drafts | first review running; its drafts number new open items from S-47, which hc9 now holds on this branch, so they renumber at merge |
| hc5 | 5 | `HW-FW-CONTRACT.md`, new interface contracts, records `hc5/`, `w5/` | first review PASS_WITH_FIXES with three blocking items (ARCHITECTURE section 12's claim that every interface is owned at both ends; IF-EXT-ETH judged by INT-001 on the MDI pairs; HW-FW-CONTRACT FW-A02's reason); second review running |
| hc7 | 7 | `v2/cad/` generators and drawings, `zstack`, `CASE-FIT-UNCERTAINTIES.md`, `release/case-2026-09-27/`, `test_case_geometry.py` | first review PASS_WITH_FIXES with three blocking items (`panel1450.py` falls back silently when `zstack.json` is missing; the `frame_seat.py` draft changes U51's height; outline-deciding rows deferred to fabrication release); second pass running |
| r8b | 8 (board B) | board B's round 8 circuit, `FAILOVER-FABRIC` and IOHA patches | not merged; residual stated (EQ-20); its IOHA patch must be re-derived on hc6's reconciled text; `candidates/r8b.patch` |

**Merged after H1.1.** Board B's round 8 landed on main at `b76c18cb` (integrated in `cc3313f3`). The set 4 branch `fnd/r8int4` then merged the re-take driver (`e5fde2ed`, REGENERATE section 9), hc2 and hc3 with the targeted fixer c23 and `fnd/hc1`'s held patches (`95e078a1`, `53292f81`), hc5 with c5 (`0da2778b`) and hc7 with c7 (`c351115d`), so `candidates/hc2.patch`, `hc3.patch`, `hc5.patch`, `hc7.patch` and `r8b.patch` are superseded by those commits; each layer's integrator line says what landed and what remains.

**Release check of layers 1, 2 and 3 (27 September 2026).** Three fresh reviewers, each an AI review labelled as one and none of them a qualified review, judged layers 1, 2 and 3 at `f2b7fa66` against the owner's execution prompt, sections 2 and 3 (`v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2026-09-27.md`, `REVIEW-LAYER-2-RELEASE-2026-09-27.md` and `REVIEW-LAYER-3-RELEASE-2026-09-27.md`, filed in `6209ec7e`). None called its layer complete: layer 1 FAIL for release (B1 to B3), layer 2 FAIL (B1 to B4), layer 3 NOT COMPLETE (R1 to R5). Their blocking items whose fix is wording or a citation were applied once, as the reviews state them: `08f3665a` (the pages of layers 1 and 2, the filed Review A records, twenty readings rebound) and the commit that carries this paragraph (the registry's citations re-anchored to `08f3665a`, START-HERE section 9, these lines). A layer is not marked COMPLETE on a fix no fresh reviewer has seen, so **layers 1, 2 and 3 stay IN_PROGRESS**; each integrator line below says what was applied and what remains.

**Second release attempt of layers 1, 2 and 3 (27 September 2026, branch `fnd/rel2` from `953f5658`).** Every blocking item the release checks left open is answered at desk, without lowering a requirement, dropping a function, weakening protection or narrowing scope: layer 2's B2 and layer 3's R4 (REQ-077's forced trigger at room temperature, `TEST-PLAN.md` P15, and E3-H's stepped run beyond the envelope), layer 2's B3 (the first Review A pass cited by its filed name wherever a page still named pass 2's file for it, and both filed records in `records/README.md` with their sha256), layer 2's B4 (C1 defined one way in POWER-THERMAL, ARCHITECTURE and HW-FW-CONTRACT, which gains the hot stop's and HOT-R1's rows; EQ-13; EQ-26 for BAT-F19), layer 3's R2 (SC-21 governs M1's duration; the owner's part of M1's failing balance is the owner action M-02) and R5 (SC-58 to SC-63, and the validator refusing an SC- id no registry entry defines), and layer 1's completion of B3 with the release check's minors m1, m4, m5, m7 and m8. The scripts and their records are `v2/docs/records/rel2/`. Session choices are the session's under the owner's standing rule of 26 September 2026. No fresh reviewer has seen these fixes yet, so **layers 1, 2 and 3 stay IN_PROGRESS**; each integrator line says what was done and what remains.

**Second release check and the release finalizer (27 September 2026).** Three fresh reviewers, each an AI review labelled as one and none of them a qualified review, judged layers 1, 2 and 3 at `eb9f9030` (branch `fnd/rel2`, then on `953f5658`): `v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md`, `REVIEW-LAYER-2-RELEASE-2-2026-09-27.md` and `REVIEW-LAYER-3-RELEASE-2-2026-09-27.md`, filed byte for byte in the commit that carries this paragraph. **Layer 2** has no blocking finding and **is COMPLETE** for its own engineering purpose at `79963b3b`, the commit that carries the reviewed content on main `91894cd7`: the branch was rebased onto main after the review, first onto `391d8579` (set 5; `v2/docs/records/rel2f/resolve_rebase.py`, `check_rebase.py`) and then, when main moved during the release, onto the consolidated re-take (the pages rendered again, with a third tool entry in `evidence/COMPATIBILITY.md`), and CONOPS, OPERATING-ENVELOPE, TEST-PLAN, `pcb_envelope.yaml` and the layer's review records are byte-identical to the files the reviewer read, PANEL.md differing only by set 5's own row. **Layer 1** reads FAIL for release on one blocking finding (R2-B1: the brief's six core feasibility blockers against the registry's seven, FEA-007 missing), and **layer 3** NOT COMPLETE on two procedural items (B-1, the baseline not recorded; B-2, no versioned package). This was the second attempt on each, so no further fix was applied (the owner's execution prompt, section 4): each remaining item is an open item of the registry and an engineering question (layer 1: S-77 and EQ-27; layer 3: S-78 and EQ-28, S-79 and EQ-29), and **layers 1 and 3 stay IN_PROGRESS**. The rebase renumbered the second release attempt's session choices SC-51 to SC-56 as SC-58 to SC-63 and its question EQ-25 as EQ-26, because set 5 had taken those ids; the three records cite the old numbers, as at `eb9f9030`. Session choices are the session's under the owner's standing rule of 26 September 2026.

**Targeted fix of layers 1 and 3 (27 September 2026, branch `fnd/h2` from `62f26a44`).** After two attempts on each, the method changes to a targeted fix and a narrow verification (the owner's execution prompt, section 4). Layer 1: R2-B1 and R2-m1 fixed with the reviewers' wording in `cecfd0f1` (S-77 closed, EQ-27). Layer 3: the registry header states the renumbering and the rest of the difference from the reviewed file in `cecfd0f1`, and the next commit writes `baseline_state` BASELINED at `cecfd0f1` on Review B's three records (S-51 and S-78 closed, EQ-28); the package, B-2, is the H2 snapshot the workflow builds next (S-79, EQ-29). **Layers 1 and 3 stay IN_PROGRESS** until the narrow verification and H2; each integrator line says what was done and what remains.

**Narrow verification of the targeted fix and its finalizer (27 September 2026, branch `fnd/h2`).** One session that wrote none of the lines checked, took no part in the fix and held neither release check verified the named items at `3e4799eb` (`v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`, headed "AI check (not a qualified engineering review)", filed byte for byte in the commit that carries this paragraph, sha256/16 `ae70b1a7811ecea1`). **Layer 1:** R2-B1 and R2-m1 CLOSED with no new contradiction in the lines touched, so the brief is BASELINED in that commit and **layer 1 is COMPLETE** for its own engineering purpose (the layer 1 integrator line gives the evidence; the package is the H2 snapshot, S-79). **Layer 3:** B-1 NOT_CLOSED on one registry difference the header did not state (when the reviewed attempt landed at `79963b3b`, its own CURRENT-EVIDENCE re-read on CON-010 and REQ-044 was replaced by a rebase note, and on CON-010 that note ends "it stays INCONCLUSIVE" where the record reads FAIL); the registry's own reversal applies, so `baseline_state` is READY_FOR_REVIEW_B again and S-51 and S-78 are open, the finding is open item S-80 and ENGINEERING-QUESTIONS EQ-30, and its wording fix is not applied in this pass (the owner's execution prompt, section 4: no unbounded author and check loop). **Layer 3 stays IN_PROGRESS**; the verifier's five other B-1 conditions PASS, so a re-check can be limited to that fix. **Layer 2 stays COMPLETE** as recorded. The verifier's observations, not findings, are placed on the integrator lines of layers 1 and 3 with their owners. Session choices are the session's under the owner's standing rule of 26 September 2026.

## Summary at `e3aedb25` (the audit)

| Layer | Status at `e3aedb25` | Acceptance items not met | Blocked questions | Closable with desk work under existing authority | First closing actions |
|---|---|---|---|---|---|
| 1. Product definition | IN_PROGRESS | 7 of 12 | none | yes: every remaining item is a desk edit or a session choice | correct the brief and the public pages against the baseline; settle SIM (CFL-010) and the mass limit; hold Review A |
| 2. Concept of operations | IN_PROGRESS | 13 of 17 | EQ-05 (does not block closure if behaviour is defined on measured internal thresholds) | yes, except the ambient figures of the hot-end controls, which are stated as bounds until measured | define the reduced mode so the owner's bearer set and the SOS path have hosts; restate the hot end; add fault, commissioning, shutdown scenarios; hold Review A |
| 3. Requirements | IN_PROGRESS | 11 of 18 | EQ-03, EQ-04, EQ-13 (none stops the layer if REQ-016 is split) | yes | settle the core TBD limits; resolve CFL-010 and make three "resolved" conflicts true; trace TEST-PLAN to requirements; hold Review B |
| 4. System architecture | IN_PROGRESS | 20 of 22 | EQ-01, EQ-02, EQ-05, EQ-06, EQ-07, EQ-10 | partly: re-anchoring, contradictions, round 8 circuits and capped box experiments; the bench, heat test and qualified reviews need authorisation | re-anchor ARCHITECTURE.md after round 8; fix the supervisor address contradiction; restage FEA-003 and FEA-004; hold Review C |
| 5. Partitioning and interfaces | IN_PROGRESS | 13 of 15 | EQ-12 | mostly; R-HSD needs the owner's spend | write contracts for the uncovered interfaces; close the power-capacity findings; draw the SLOT_EN hold and GND-002 |
| 6. Components | IN_PROGRESS | 11 of 11 | EQ-06, EQ-11 | mostly; U8 and R-PWR need authorisation | make mismatch marks a checker input; apply the recommended codes; per-board BOM with identity; H743 matrix |
| 7. Mechanical and enclosure | IN_PROGRESS | 15 of 17 | EQ-05, EQ-08 | mostly; the mock-up and heat test need a purchase | implement case choices C1 to C6 in the geometry source and CAD; pick the jumper plug and the RJ45; draw the stack and the pack hold-down |
| 8. Schematics | IN_PROGRESS | 13 of 18 | EQ-06, EQ-09, EQ-10, EQ-11, EQ-12 | mostly; U8 and the qualified reviews need authorisation | integrate round 8 per board with parity; one consolidated re-take; PDFs, BOMs, packets; per-board functional review |
| 9. Pre-layout design analysis | IN_PROGRESS | 17 of 20 | EQ-05, EQ-07, EQ-09, EQ-11, EQ-12, EQ-14 | partly; the heat test, F2 evidence, prices and reviews need authorisation | write PWR-F12 into the registries; decide the stackups; per-board layout constraint sheets; channel budgets |

---

## Layer 1. Vision, product definition and pitch

**At H2: COMPLETE** since `6b2a9965` (the brief BASELINED after the narrow verification). **H3:** COMPLETE; the brief is re-stamped BASELINED at `a9f212c7`, an editorial restructure with no definition change (`v2/docs/reviews/DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md`, CONTENT_PRESERVED), and `6b2a9965` stays its definition baseline. The states below are those of the second release check (`v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md`, section 4, which maps its rows to these items) with the targeted fix and its narrow verification (`v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`); every one is an AI review. The audit of this layer at `e3aedb25` and its edition history (the integrator line) are Appendix A, section A.1, unchanged.

| Item | Acceptance item (short) | At H2 | Evidence, or what remains |
|---|---|---|---|
| 1.1 | clear product purpose | MET | the release check's row 1 |
| 1.2 | users stated | MET | row 2 (D-04; four roles; no target organisation, stated) |
| 1.3 | prototype scope stated | MET | row 3 (D-01, SC-01, SC-04, CONOPS 2a) |
| 1.4 | exclusions stated | MET | row 4; minor R2-m2 carried |
| 1.5 | intended outcome stated | MET | row 5 was NOT MET on R2-B1 (FEA-007 missing from the core feasibility blockers); closed by the targeted fix `cecfd0f1`, verified CLOSED at `3e4799eb` |
| 1.6 | report and deck commitments tracked separately | MET | row 6 |
| 1.7 | claims agree with the engineering baseline | MET | row 7 (B1 to B3 of the first check closed, R2-B1 closed as for 1.5); README.md's "eleven blind-mate clamps" (R2-m6's m6) corrected after H2 |
| 1.8 | every owner ruling of 25 and 26 September recorded | MET | row 8; minor R2-m4 |
| 1.9 | the owed stale texts of BUILD.md and both READMEs closed | MET | row 9, at `eb9f9030` (R2-m1, R2-m6) |
| 1.10 | SIM description (CFL-010, S-13) | MET | row 10 (SC-13); the eSIM variant's order code is on layer 6's list |
| 1.11 | required review held (Review A) | MET | Review A layer 1 (two passes), two release checks and the narrow verification, all AI reviews, labelled |
| 1.12 | versioned package another engineer can use | MET | the H2 snapshot (`v2/release/handover/H2.zip`) |
| rows 11, 12, 15 of the release check | carried-mass limit (REQ-023); records filed; section 2 of the owner's prompt | MET | SC-14; `v2/docs/records/w1/`; nothing lowered, dropped, weakened or narrowed (row 15 met once R2-B1 closed) |

---

## Layer 2. Concept of operations

**At H2: COMPLETE** at `79963b3b` (recorded in `62f26a44`). **H3:** COMPLETE; CONOPS is re-stamped BASELINED at `a9f212c7`, an editorial restructure with no definition change (the same check, CONTENT_PRESERVED), and `79963b3b` stays its definition baseline. The states below are those of the second release check (`v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md`, section 4, items 2.1 to 2.17), an AI review with no blocking finding. The audit of this layer at `e3aedb25` and its edition history (the integrator line) are Appendix A, section A.2, unchanged.

| Item | Acceptance item (short) | At H2 | Evidence, or what remains |
|---|---|---|---|
| 2.1 to 2.10 | the normal, degraded, startup, charging, shutdown, storage, service and fault scenarios; the envelope; simultaneous modes and duty | MET | section 4 of the release check: met as the first release check found, with B1's and B2's edits |
| 2.11 | explicit behaviour of the core functions | MET | B1 closed; minor m12 |
| 2.12 | product decisions settled under existing authority | MET | inside the layer; M-02 is the owner's action, recorded and not holding the layer (SC-21 sets M1's duration) |
| 2.13 | every owner ruling recorded | MET |  |
| 2.14 | consistent with the current analyses | MET | for C1 and EMCON (B1, B4 (a)); the lags in other layers' texts are tracked there (n4, n10) |
| 2.15 | TEST-PLAN envelope limits consistent with the rulings | MET | B2 closed; minor m2 |
| 2.16 | every source the CONOPS cites is in the repository | MET | B3 closed |
| 2.17 | Review A held and recorded | MET | passes 1 and 2, the first release check and the second, all AI reviews |

---

## Layer 3. Requirements

**After H2: COMPLETE** (branch `fnd/l3rb`): item 3.14 is MET by the re-baseline at `a54b793b` and its re-check (`v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md`, B-1 CLOSED at `2c12be91`); item 3.18 closes with the next snapshot, H3. The table below keeps the states at H2. **H3:** the commit is `24e7bf5a`; item 3.18 is met by the H3 snapshot cut from this commit's successor (the integrator confirms), and rows 3.14 and 3.18 below say so.

**At H2: IN_PROGRESS.** The states below are those of the second release check (`v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md`, section 4, at `eb9f9030`, the content landed at `79963b3b`) and the narrow verification of the targeted fix (B-1 NOT_CLOSED at `3e4799eb`); AI reviews. The audit of this layer at `e3aedb25` and its edition history (the integrator line) are Appendix A, section A.3, unchanged.

| Item | Acceptance item (short) | At H2 | Evidence, or what remains |
|---|---|---|---|
| 3.1 to 3.8 | records trace to needs; source-linked; citations resolvable; measurable acceptance; applicability; allocation; verification method and phase; no check needs a later stage's product | MET | section 4 of the release check; minors n1, m5 carried |
| 3.9 | contradictions resolved | MET | M1 stated one way (R2); CFL-017's routes in EQ-26; minors n4, m1, m2 carried |
| 3.10 to 3.13 | needs, choices, assumptions and history kept apart; TBDs with their effect; every critical mission outcome measurable; REQ-050's trace of TEST-PLAN | MET | minor n3 carried |
| 3.14 | Review B held and the registry baselined | **OPEN** at H2; **MET** since after H2 (`2c12be91`, re-check B-1 CLOSED) | at H2, B-1: S-80 and EQ-30 (CON-010's newest entry against its FAIL, and the header naming `79963b3b`'s re-take), a re-check of that fix, then the re-baseline (S-51, S-78) |
| 3.15 | every open item carried by a record | MET in substance | the letter is not met (n7: open items in no record's `waits_on`) |
| 3.16, 3.17 | every BLOCKER or MUST_JUSTIFY rule has a parent record; the trace generated and current | MET | 59 of 59 rules named; `rules_render.py --requirements --check` current in a git checkout |
| 3.18 | versioned, portable layer package | **OPEN** at H2; met by H3 | at H2, B-2: S-79 and EQ-29, a snapshot cut from a pushed commit carrying the re-baseline; H2 carries layer 3 IN_PROGRESS. **H3:** met by the H3 snapshot cut from this commit's successor (the integrator confirms) |

---

## Layer 4. System architecture

**At H2: IN_PROGRESS.** No release check has judged this layer; the states below are this page's reading of what landed since `e3aedb25` (the integrator line in Appendix A.4 and the H2 table above), each naming its commit or record. "As at `e3aedb25`" means nothing since changes the audit's answer. The audit of this layer at `e3aedb25` and its edition history (the integrator line) are Appendix A, section A.4, unchanged.

| Item | Acceptance item (short) | At H2 | Evidence, or what remains |
|---|---|---|---|
| 4.1 | functional diagrams current (power, data, control) | MET | `v2/docs/diagrams/`: context, interconnect, power tree, power-up, lanes and fabric, control lines, battery states, case; drawn on set 5's netlists at `b7f96784` (`730f8489`), SVG and PDF; hc4's two AI reviews; the manifest check's count is START-HERE known gap 6 |
| 4.2 | physical diagrams current | PARTLY | the case drawings and the case release carry C1 to C6 (`c351115d`); `v2/cad/pack_4s.py` still draws the 4S4P block (S-27) and `scene.py`'s QY is a typed copy |
| 4.3 | diagrams and architecture reviewed, AI review labelled | PARTLY | hc4's AI reviews of the diagrams; Review C not held |
| 4.4 | power and data paths documented on the committed design | PARTLY | documented at `eadbe571` (ARCHITECTURE sections 4 and 5, cited to generator lines); the diagrams are on set 5's netlists; ARCHITECTURE's text is not re-read on the H2 netlists (its section 3.1 re-anchored after H2 only) |
| 4.5 | control paths consistent and complete | PARTLY | supervisor addresses 0x34 to 0x36 everywhere (hc5, `0da2778b`); the control-lines drawing; open: the SLOT_EN hold in no generator, EMCON's shared-line items L1 to L4 and L7 (FEA-002), TX_INHIBIT_n's fail-safe level (EQ-25) |
| 4.6 | mode behaviour defined | PARTLY | the reduced mode (SC-17), the heat stage and the hot stop defined in CONOPS 4c and baselined with layer 2; the restrictions stated as controls; open: HOT-R1 in the generators (EQ-22), BANK-R1 (S-54), the SDR limiter as at `e3aedb25` |
| 4.7 | energy and runtime budget with margin | **OPEN** | PROVISIONAL runtime; no runtime value set, so no margin; REQ-072 FAIL at desk (S-53, M-02, EQ-13) |
| 4.8 | thermal budget with margin | **OPEN** | conductance unmeasured; the bound includes failure (FEA-004, EQ-05) |
| 4.9 | lane budgets with margin | **OPEN** | as at `e3aedb25` (FEA-003, EQ-01, EQ-12) |
| 4.10 | rail and interconnect margins | PARTLY | PWR-003 PASS on B (`b76c18cb`: F1 the MF-MSMF110); the dock's VIN_RAW on four 9 A pins (SC-55, EQ-16's supply side); board B's supplies declared from the makers' sheets (`caba1876`, PWR-001 PASS on A and B); not re-checked at H2: R17's rating, IF-AB-POWER's two ends (I-03), PWR-F02 |
| 4.11 | mass, dimension and cost budgets | PARTLY | a mass limit set (SC-14, REQ-023); dimensions: 35 of 70 case rows OPEN, M17g and M17x failing as assumed (FEA-007); cost TBD (EQ-14) |
| 4.12 | trade decisions recorded | PARTLY | SC-01 to SC-63 with their reversals; open: board B's stackup and escape method (EQ-01), the layer counts, U8 (EQ-06), F2 (EQ-07), the fans (D-18) |
| 4.13 to 4.18 | feasibility demonstrated; ZEROIZE, EMCON, failover, power and thermal, battery questions resolved | **OPEN** | FEA-001 to FEA-007 all FEASIBILITY_OPEN: EMCON 15 of 17 local at desk and 0 of 17 end to end (EQ-02 the RockBLOCK row); FAB-01 to FAB-04 drawn (`b76c18cb`) with EQ-20's residual; the flange sensor drawn on D (`76235aad`); ZEROIZE's bench (EQ-06); R-BAT (EQ-10) |
| 4.19 | Review C held | **OPEN** |  |
| 4.20 | no feasibility stage waits for what it gates | **OPEN** | the misplacements of CONTINUATION-BRIEF section 5.1 stand |
| 4.21 | qualified review routes named and costed | MET | as at `e3aedb25`; none engaged |
| 4.22 | sibling records consistent with the architecture | PARTLY | IOHA, ZEROIZE, CONOPS, OPERATING-ENVELOPE and `pcb_pack_protection.yaml`'s topology line brought in line (CONTINUATION-BRIEF section 8, H2 marks); open: FAILOVER-FABRIC's Q-B-ESC-1 text, ARCHITECTURE 13.1's F-CH-04 row, POWER-THERMAL's pack-path widths |

---

## Layer 5. Partitioning and interfaces

**At H2: IN_PROGRESS.** No release check has judged this layer; the states below are this page's reading of what landed since `e3aedb25` (Appendix A.5's integrator line and the H2 table above). The audit of this layer at `e3aedb25` and its edition history (the integrator line) are Appendix A, section A.5, unchanged.

| Item | Acceptance item (short) | At H2 | Evidence, or what remains |
|---|---|---|---|
| 5.1 | board responsibilities and partition settled | **OPEN** | board B's outline and floor plan (EQ-01) |
| 5.2 | every interface owned at both ends with its connector | PARTLY | 30 contracts (hc5, `0da2778b`); the first twelve lack the pass-2 fields; the board-to-board IDC headers carry no MPN (EQ-21) |
| 5.3 | pinouts identical at both ends | MET | `check_contracts.py` PASS 99 of 99 on the H2 netlists (map identity and presence only); INT-001 current on the six boards with a schematic, E5's UNBOUND |
| 5.4 | electrical levels stated per interface | PARTLY | the kit I2C budget computed (CON-026 FAIL at desk; three segments owed, SC-59, S-59); `HW-FW-CONTRACT.md`; the rest as at `e3aedb25` |
| 5.5 | power capacity of each power interface with margin | PARTLY | IF-AE-DOCK answered at desk for the supply (SC-55); IF-BC-PANEL's PWR-003 PASS (`b76c18cb`); open: E5's targets and the ground share (S-74, S-75), IF-AB-POWER (I-03), the ribbon and SMP-MAX ratings TBD |
| 5.6 | sequencing across interfaces | **OPEN** | the SLOT_EN hold in no generator; HOT-R1 (S-57, EQ-22) |
| 5.7 | reset, default and cable-out states for every control line | PARTLY | HOT-R1's four line states in `HW-FW-CONTRACT.md`; TX_INHIBIT_n's fail-safe level found failing (EQ-25); the rest as at `e3aedb25` |
| 5.8 | communications and addressing consistent | PARTLY | supervisor addresses reconciled (0x34 to 0x36); the panel USB wire format outside the repository (MESHSAT-837) |
| 5.9 | harnesses defined and consistent | PARTLY | ASSEMBLY section 4 carries C2 to C4 (`c351115d`); the touch USB's board end (SC-63); open: the jumper plug (M17g, M17x), J_AB2's lead |
| 5.10 | mechanical mating of every interface | **OPEN** | W4-F17; the clamp bar replaces the nests (`45f6d83f`); D-07's site on A in no generator; E5 generated from A32's board file (S-74) |
| 5.11 | firmware obligations affecting hardware explicit | PARTLY | `HW-FW-CONTRACT.md` version 1 (heartbeat resolved; FW-C13, FW-C14, FW-E10 for the hot stop); PANEL.md's reduced-mode and hot-stop duties owed (layer 2's m13) |
| 5.12 | GND-002 implemented everywhere | **OPEN** | none of the four board changes in a generator |
| 5.13 | interface contracts consistent with the tree | PARTLY | `read_at` re-anchored at `ef144760` after H2; the contracts' generator lines are as each contract states them; the pass-2 fields owed |
| 5.14 | Review C over the interfaces | **OPEN** | EQ-12 for R-HSD |
| 5.15 | INT-002 pre-layout assessment | MET | PASS as a desk review (the session's AI review) on board B's current nets (`PCB-RULE-STATUS-B.md`); INT-003 at prototype |

---

## Layer 6. Components

**At H2: IN_PROGRESS.** No release check has judged this layer; the states below are this page's reading of what landed since `e3aedb25` (Appendix A.6's integrator line); hc6's records were reviewed once (AI review, no blocking item). The audit of this layer at `e3aedb25` and its edition history (the integrator line) are Appendix A, section A.6, unchanged.

| Item | Acceptance item (short) | At H2 | Evidence, or what remains |
|---|---|---|---|
| 6.1 | exact manufacturer, MPN, package and grade per fitted part | **OPEN** | no MPN field; 1630 of 2393 per-reference BOM rows without an LCSC code (EQ-21); grades in `v2/docs/parts/GRADE-CHECK.md`, AW7915-AED and LimeSDR OUTSIDE |
| 6.2 | supporting documents with revision, source and currency | PARTLY | fourteen SOURCES entries added (hc6); the documents START-HERE section 8 names are not held |
| 6.3 | selection rationale recorded | PARTLY | for critical parts (hc6); not for the passive and connector majority |
| 6.4 | compatibility findings; mismatches stay mismatches | PARTLY | `jlc_certify.py` reads the declared mismatches (`661ca3a4`); the standing wrong models not re-checked at H2 |
| 6.5 | STM32H753 against STM32H743 | MET at desk | `v2/docs/parts/STM32H743-COMPATIBILITY.md` (`99cde56b`); the firmware obligations it names are S-41 |
| 6.6 | procurement constraints and alternatives | PARTLY | `PROCUREMENT.md` with dated readings; HX6096NL's readings not filed |
| 6.7 | regenerated outputs preserve part decisions | PARTLY | regeneration PARITY on all six at H2; codes the certification refuses still typed in generators, not re-checked at H2 |
| 6.8 | a current, versioned BOM with identity per board | PARTLY | the H2 NOT_FOR_FAB BOMs of all six boards; identity only where an LCSC code is chosen (EQ-21) |
| 6.9 | CMP-001 | MET | PASS on every board on evidence that counts as current (`CURRENT-EVIDENCE.md`); its DC-bias gap is 9.18 |
| 6.10 | CMP-002 and SUP-001 | **OPEN** | INCONCLUSIVE: the certification readings predate the tool's change |
| 6.11 | Review D per board and R-PWR before A's layout entry | **OPEN** | EQ-11 |

---

## Layer 7. Mechanical and enclosure

**At H2: IN_PROGRESS.** No release check has judged this layer; the states below are this page's reading of what landed since `e3aedb25` (Appendix A.7's integrator line: hc7 and its targeted fixer c7, `c351115d`, with the fresh verifier's AI check). The audit of this layer at `e3aedb25` and its edition history (the integrator line) are Appendix A, section A.7, unchanged.

| Item | Acceptance item (short) | At H2 | Evidence, or what remains |
|---|---|---|---|
| 7.1 | editable CAD current | PARTLY | C1 to C6 in `panel1450.py`, `z_budget.py`, `case_wall_cutouts.py` and the CAD (`c351115d`); `scene.py` and `v2/images/face-section.png` draw the superseded face; the pack box draws 4S4P (S-27) |
| 7.2 | dimensioned drawings of every made part and templates | MET | `v2/release/case-2026-09-27/` sheets 1 to 14; the QMX tray not to be printed before S-63 (EQ-24) |
| 7.3 | board envelopes and the Z stack | PARTLY | the Z stack drawn (`zstack.json`, the case-zstack drawing); W4-F17 open |
| 7.4 | mounting and retention | **OPEN** | the pack hold-down (S-27) and the stack's retention undesigned; the face's mounting drawn (C1) |
| 7.5 | connector, cable and service access | PARTLY | the connector plate (C3) drawn; the jumper plug (M17g, M17x) and the sealed RJ45 open |
| 7.6 | tolerance analysis reproducible | MET | as at `e3aedb25`; `frame_seat.py` and `case_margins.py` reproduce byte for byte from the ZIP (the H2 usability check) |
| 7.7 | blind-mate and dock tolerance stack closed on paper | **OPEN** | FEA-007's desk item for A, E and E5 (the clamp bar and an ANT3 clamp at X +46) |
| 7.8 | thermal interfaces specified | PARTLY | the PA flange sensor drawn on D (`76235aad`); the fans unsettled (D-18); the conductance (EQ-05) |
| 7.9 | critical fit uncertainties resolved by suitable evidence | **OPEN** | FEA-007: the mock-up (L-07, EQ-08) and the desk items |
| 7.10 | later physical checks allocated, deferral justified | PARTLY | FEA-007 stages the YES rows at layout entry on the decision they move; FEA-004's heat-test staging stays in CONTINUATION-BRIEF 5.1's misplacements |
| 7.11, 7.12 | REQ-019 (every case margin MET); CON-006 (a named pack build with its hold-down) | **OPEN** | 35 rows OPEN, 2 failing as assumed; S-27 |
| 7.13 | MEC-001 on the current case geometry | PARTLY | board C's gate reads the Z stack (`c351115d`); MEC-001 reads FAIL on A and PASS on B to P and E5 (`PCB-RULE-STATUS-*.md`); the case rows remain FEA-007's |
| 7.14 | session engineering choices recorded with authority | MET | SC-07 and the case choices, SESSION under the standing rule |
| 7.15 | no contradictory live specifications; superseded artefacts labelled | PARTLY | ASSEMBLY, V2-SPEC, BUILD, the READMEs and REQ-047 carry C1 to C6; `release/revA/case/` labelled HISTORICAL; `scene.py` and `face-section.png` superseded |
| 7.16 | review labelled; no qualified route pretended | PARTLY | the agent checks are labelled AI; no qualified mechanical route exists (FEA-007) |
| 7.17 | portable regeneration of the mechanical outputs | PARTLY | `v2/cad/requirements-cad.txt` and `.lock` pin the CAD's Python packages; the margin scripts reproduce; renders need Blender 4.2 on a GPU host |

---

## Layer 8. Schematics

**At H2: IN_PROGRESS on every board.** No release check has judged this layer; the states below are this page's reading of what landed since `e3aedb25` (Appendix A.8's integrator line and the H2 table above). Per board, the layout-entry reasons are the H2 section's table. The audit of this layer at `e3aedb25` and its edition history (the integrator line) are Appendix A, section A.8, unchanged.

| Item | Acceptance item (short) | At H2 | Evidence, or what remains |
|---|---|---|---|
| 8.1 | current native schematic per board | MET | round 8 on all six, set 5 on A, B, D and E; regeneration PARITY on all six |
| 8.2 | readable PDFs | MET | `v2/release/handover/_generated/` (A, B, D, E at `763bccdf`; C, P at `99cde56b`) |
| 8.3, 8.4 | generator inputs and source; netlists | MET | title-block labels keyed in the glossary |
| 8.5 | BOMs | PARTLY | two NOT_FOR_FAB BOMs per board; the identity gap is layer 6's (EQ-21) |
| 8.6 | functional circuit reviews completed | **OPEN** | Review D per board; R-BAT, R-PWR, R-HSD (EQ-10 to EQ-12) |
| 8.7 | exact part and land mapping | PARTLY | SCH-005 PASS on current evidence on all six; the WRONG_MODEL rows of condition 1 not re-checked at H2 |
| 8.8 | relevant ERC completed | MET | SCH-001 PASS on current evidence on all six (the re-take); board B's errors allow-listed with reasons |
| 8.9 | regeneration shown by regenerating and comparing | MET | PARITY on all six from a clean archive (REGENERATE.md section 4), reproduced by the H2 usability check |
| 8.10 | known schematic-affecting defects closed per board | **OPEN** | TRN-001 and PWR-003 now PASS; open: EQ-25 on C (RF-002 on A to D), PWR-001 on C, D, E, P, BAT-001 on P (REQ-044), HOT-R1 on A and E (EQ-22), the FEA items per board |
| 8.11 | board-specific completion marked | MET | per board in the H2 section and `CURRENT-EVIDENCE.md` |
| 8.12 | Review D per board gates layout entry | **OPEN** |  |
| 8.13 | schematic-phase rules PASS on current-candidate evidence | **OPEN** | every schematic-phase reading current but E5's INT-001; 15 current readings are not a PASS |
| 8.14 | decision 31's layout-entry requirements on A, D, E | PARTLY | fitted parts and TRN-001 PASS on current evidence; the review record owed |
| 8.15 | INT-002 on board B's current nets | MET | desk review, AI, bound (`PCB-RULE-STATUS-B.md`) |
| 8.16 | review packet at each board's candidate | **OPEN** | the packets are at `1f614233`; A and B never packaged |
| 8.17 | condition 1: substitutions stay mismatches until proven | PARTLY | declared mismatches read by the certification (`661ca3a4`); not re-checked at H2 |
| 8.18 | STM32H743 alignment | MET | the generator and netlist; V2-SPEC's corrections name the H743 |

---

## Layer 9. Pre-layout design analysis

**At H2: IN_PROGRESS.** No release check has judged this layer; the states below are this page's reading of what landed since `e3aedb25` (Appendix A.9's integrator line and the H2 table above). The audit of this layer at `e3aedb25` and its edition history (the integrator line) are Appendix A, section A.9, unchanged.

| Item | Acceptance item (short) | At H2 | Evidence, or what remains |
|---|---|---|---|
| 9.1 | current power calculations with margins and sensitivities | **OPEN** | `pwr_budget.py` reproduces from the ZIP, but models the `1f614233` boards; not re-run on the H2 line |
| 9.2 | current energy calculations with sensitivities | **OPEN** | PROVISIONAL; REQ-072 FAIL at desk |
| 9.3 | protection coordination on the current design | PARTLY | `energy_chain.py` PASS of 98 on the H2 netlists once Mill-Max's page 28 is restored (REGENERATE.md section 6); PWR-003 PASS on A, B, E, P, E5; BAT-001 FAIL on P (REQ-044); decision 31's review owed |
| 9.4 | thermal analysis current | **OPEN** | FEA-004, EQ-05; THM-001 INCONCLUSIVE on every board |
| 9.5 | signal analysis pre-layout | **OPEN** | SI-001 INCONCLUSIVE on all six (edge rates owed, START-HERE known gap 5); IMP-001 INCONCLUSIVE; channel budgets (EQ-12) |
| 9.6 | timing analysis | PARTLY | PWR-002 PASS on A, B, E, P and CLK-001 PASS where it applies; FB-FAB-4's break-before-make drawn (`b76c18cb`) with EQ-20's residual; EMCON latency end to end open (FEA-002) |
| 9.7 | placement constraints analysed | PARTLY | the per-board sheets (re-bound to the H2 line after H2); board B's floor plan (EQ-01); PLC-001 FAIL on A and B reads their historical layouts |
| 9.8 | constraints handed to layout written per board | MET | `v2/docs/layout-constraints/`, re-bound to the H2 line after H2 (known gap 8); each sheet's open items named |
| 9.9 | analyses needing routed geometry named and allocated | MET | as at `e3aedb25` |
| 9.10 | analyses needing hardware in the test plan | PARTLY | TEST-PLAN traces its tests to requirements (3.13) and carries P15, E3-L and E3-H; the heat-balance test is in POWER-THERMAL section 10 and READY-TO-ACT, not re-checked in TEST-PLAN at H2 |
| 9.11 | pre-layout portion without claiming post-layout or physical verification | MET |  |
| 9.12 | stackup decided per board with measurement and cost | **OPEN** | board B undecided; board A's copper weight; no price (EQ-14) |
| 9.13 | every board passes the staged layout-entry test | **OPEN** | 0 of 7; 40 reasons |
| 9.14 to 9.16 | FEA-004 (A, D), FEA-006 (A to P), FEA-003 (B) and FEA-005 (P) layout-entry stages | **OPEN** | each is among its boards' layout-entry reasons at H2 |
| 9.17 | INT-002 current on its 48 nets | MET | as 8.15 |
| 9.18 | CMP-001 with DC-bias derating | **OPEN** | as at `e3aedb25` |
| 9.19 | qualified reviews preserved; AI review labelled | PARTLY | labelling met; R-PWR and R-HSD unapproved (EQ-11, EQ-12) |
| 9.20 | a representative calculation re-runs from the repository alone | MET | `energy_chain.py` (REGENERATE.md section 6) and `pwr_budget.py` from the ZIP; most other tools need `pcbnew` |

---

## Appendix A. The audit at `e3aedb25` and each layer's edition history

Moved here after H2 (27 September 2026, the H2 usability check's minor finding 10), byte for byte, from the layer sections above: for each layer its status at `e3aedb25`, scope, prerequisites, deliverables by revision, the acceptance items as judged at `e3aedb25` (with their inline **Superseded in H1** marks), the unresolved decisions, the stage-gate cycles, the next closing actions, the per-board lines and the `INTEGRATOR LINE` with its steps H1 to H2. Its file:line citations are lines at `e3aedb25`. Other pages cite these by layer and item ("LAYER-STATUS layer 3, item 3.4", "layer 8 actions 1 to 3"), which are here under the same numbers. The acceptance table at H2 that opens each layer section above is the current reading; where it and this record differ, it is the newer.

### A.1 Layer 1. Vision, product definition and pitch (the audit at `e3aedb25` and the edition history)

**Status at `e3aedb25`: IN_PROGRESS.** Purpose, users, scope and intended outcome are written and every ruling of 25
and 26 September 2026 but one is recorded. The public pages contradict the engineering baseline (the 5G socket key and
the EMCON gaps in the brief; readiness and ordering claims in both READMEs and `v2/BUILD.md`; stale bulkhead, pack and
runtime lines in V2-SPEC), the SIM conflict CFL-010 is open, one owner ruling and W1's decision table are not in the
repository, and Review A has not been held. Every remaining item is a desk edit or a session choice under the owner's
standing rule, so the layer can close independently of layer 2, except for restating layer 2's reduced-mode and
storage decisions once taken.

**Scope.** What the kit is for, who operates it, prototype scope (D-01), exclusions and intended outcome, and every
public claim about it (`README.md`, `v2/README.md`, `v2/BUILD.md`, `v2/docs/V2-SPEC.md`,
`v2/docs/PRODUCT-BRIEF.md`) agreeing with the engineering baseline. Kit-level; no board-specific completion.

**Prerequisites.** None upstream. It rests on the owner rulings of 25 and 26 September 2026 (`v2/docs/CONOPS.md`
section 7; `pcb_requirements.yaml` `owner_rulings`; `pcb_decisions.yaml`; appendix 32.365 to 32.367) and must agree with
`v2/docs/CURRENT-EVIDENCE.md` lines 6 and 26 to 32, V2-SPEC corrections 1 to 19, `v2/docs/CASE-MARGINS.md` section 4,
`v2/docs/feasibility/POWER-THERMAL.md` sections 0 and 9, and `v2/docs/feasibility/EMCON.md` sections 4 and 5a.

**Deliverables**

| File | Revision (commit, sha256/16) | Current | Note |
|---|---|---|---|
| `v2/docs/PRODUCT-BRIEF.md` | `b69f20db`, f09185c8635af1d4 | no | status DRAFT for Review A (line 3); lines 44 to 46 (5G socket "wrong key") and 63 to 68 (EMCON gaps) describe the circuit before `458b2873` |
| `README.md` | `b69f20db`, c882227c8b435124 | no | line 5 "designed, generated and checked"; lines 22 to 30 list A24, B19, D11, E9 against declared A32, B21, D12, E17; line 61 ordering at JLCPCB against decision 41 |
| `v2/README.md` | `b69f20db`, 233cc08056a3e6f1 | no | line 5 EMCON sentence before `458b2873`; line 35 7 September readiness; lines 3 and 52 eleven couplers at 88 mm |
| `v2/BUILD.md` | `b69f20db`, b756013686343ca5 | no | the 7 September guide: ordering A22 and B16, a 4S4P pack, eleven D-holes at Z 88, ZEROIZE as hardware without panel firmware; named owed in appendix 32.366 |
| `v2/docs/V2-SPEC.md` | `9a151c78`, df8ac22603440bc5 | no | lines 10 and 11 (bulkheads, connector plate), 23 (runtime), 73 (thermal) and 41 (SIM, CFL-010) are stale or open |
| `v2/ecad/tools/pcb_requirements.yaml` | `a6f87e9d`, acd19f7bfc50b7ad | yes | the rulings record (layer 3 owns the file); L-02 is classed OWNER_ACTION against the standing rule |
| `v2/ecad/tools/pcb_decisions.yaml` | `31ce3840`, 1367edbf54a842d3 | yes | decisions 27, 28, 30, 40, 41, 43 carry authority OWNER; 0 decisions open |
| `v2/docs/OWNER-DECISIONS-2026-09-11.md` | `9d566e8b`, 0726834a1f8bca08 | yes | owner decision records |
| `v2/docs/MESHSAT-709-geometry-appendix.md` | `b69f20db`, 5e942dd41e9e4ed0 | yes (history) | rulings 32.49 to 32.62; foundation records 32.365 (line 18725), 32.366 (18739), 32.367 (18875) |
| `v2/docs/EXECUTION-PLAN.md` | `e3aedb25`, 73b98e8fddd05b70 | yes | conditions (lines 90 to 98), Review A (line 60), milestones |

**Acceptance items**

| # | Item | Met | Evidence |
|---|---|---|---|
| 1.1 | Clear product purpose | yes | `v2/docs/PRODUCT-BRIEF.md` lines 13 to 20 |
| 1.2 | Users stated | yes | brief lines 22 to 34 (operator, second crew member, local users, remote correspondents; no target organisation, stated) |
| 1.3 | Prototype scope stated | yes | brief lines 112 to 127; `v2/docs/CONOPS.md` lines 71 to 105; registry D-01 |
| 1.4 | Exclusions stated | no | brief lines 84 to 99 omit D-01's deferred functions (only in CONOPS lines 75 to 77), that the hot end is not established (POWER-THERMAL.md lines 66 to 72, FEA-004), and that the bought AW7915-AED and LimeSDR are rated only from 0 C (POWER-THERMAL.md lines 945 to 953) |
| 1.5 | Intended outcome stated | yes | brief lines 112 to 127: staged acceptance on a named core, D-02a's two pass lines |
| 1.6 | Report and deck commitments tracked separately; presentation polish does not delay technical closure | yes | no presentation deliverable in the repository is coupled to the technical layers; the brief does not say where external commitments are tracked (a gap) |
| 1.7 | Claims agree with the engineering baseline | no | brief lines 44 to 46 and 63 to 68 against V2-SPEC lines 130 and 140 and CONOPS lines 313 to 318; `README.md` line 5 and `v2/README.md` lines 3 and 35 against CURRENT-EVIDENCE line 6; `v2/BUILD.md` lines 10, 11, 41, 58, 92 and section 1 against D-06, decision 41, PANEL.md line 167 and D-03; V2-SPEC lines 10, 23 and 73 against CASE-MARGINS C2 and POWER-THERMAL PWR-F07 and PWR-F08 |
| 1.8 | Every owner ruling of 25 and 26 September recorded | no | recorded: D-01 to D-17, D-08a, the D-08 reversal (D-18 is an open conditional item, not a ruling), the standing rule, decisions 27, 28, 30, 40, 41, 43. Not recorded: the owner's ruling of 25 September evening that the foundation documents go directly into the public repository; the options and recommendations each D-question was ruled on (W1's decision table, cited by CONOPS lines 407 to 409 and by SC-01, SC-03, SC-05) |
| 1.9 | The project's own owed list closed (stale BUILD.md and READMEs; appendix 32.366 line 18860, 32.367 line 18994) | no | all three files last touched `b69f20db` and still carry the texts named |
| 1.10 | SIM description conflict resolved (CFL-010, S-13) | no | V2-SPEC line 41 says eSIM plus nano-SIM; the generator fits two nano-SIM holders with an eSIM build option |
| 1.11 | Required review held and recorded (Review A) | no | no Review A record exists; no record mandates a qualified review for this layer, so a fresh-checker AI review, labelled, can serve |
| 1.12 | Versioned package another engineer can use | no | at `e3aedb25` neither this page nor a `v2/release/handover/` snapshot exists |

**Unresolved decisions**

| Decision | Downstream impact | Waits on later evidence |
|---|---|---|
| Dual SIM: eSIM plus nano-SIM, or two nano-SIM holders with an eSIM build option (CFL-010, S-13) | board B SIM holders and SIM TVS array, the public claim, RM520N-GL USIM2 wiring | no: desk choice from Quectel's hardware design Figure 19 and appendix 32.50 item 12 |
| Kit carried-mass limit (REQ-023; no mass requirement exists anywhere) | validity of the ruled E1 drop severity (MIL-STD-810 Method 516 presumes a mass category), carry concept, pack and case | no: the limit is a product decision; only the measured mass comes later; the standard is not held |
| How the public pages present the 7 September deliverables and build guide | risk that a reader orders boards whose layouts do not carry the corrected netlists | no: wording only |

**Stage-gate cycles and remedies**
- No circular gate. Review A is undefined as written (`v2/docs/EXECUTION-PLAN.md` line 60 names its content and what it
  gates, but no reviewer, criteria or record location), so nobody can pass it. Remedy: define it as one fresh checker,
  labelled AI review, against the owner's section 3 items for the layer, recorded under `v2/docs/reviews/`.

**Next closing actions** (all doable now under existing authority)
1. Rewrite PRODUCT-BRIEF lines 44 to 46 (5G socket key B since `458b2873`, S-12 locating holes open) and 63 to 68
   (EMCON as generated; the open gap SD-EMC-1 with its 20 s latency bound for a running 5G module, EMCON.md 5a);
   extend "What it is not, today" with D-01's deferred functions, the unestablished hot end, the two parts rated only
   from 0 C, and the CURRENT-EVIDENCE headline. Worker: docs integrator. Dependency: none. About 1 h.
2. `README.md` (lines 5, 10, 20, 22 to 30, 61) and `v2/README.md` (lines 3, 5, 9 to 15, 35, 52): the CURRENT-EVIDENCE
   headline, the deliverable folders marked as predating the corrected schematics with the declared phases, the order
   set quarantined, the EMCON sentence, the bulkhead layout as the session's case choice C2 (twelve arrestor
   bulkheads at Z 59, the third 5G jack conditional on D-07). Docs integrator; none; about 1 h.
3. Head `v2/BUILD.md` as the 7 September guide, not for ordering, and correct lines 9, 10, 11, 41, 58 and 92 against
   SC-02, D-06, PANEL.md line 167, D-03 and CASE-MARGINS C2. Docs integrator; none; 1 to 2 h.
4. V2-SPEC corrections 20 onward for lines 10 and 11 (CASE-MARGINS C2 to C5), 23 (PWR-F07 with its bounds), 73
   (PWR-F08: proposed controls); settle CFL-010 by a session choice recorded as an SC entry, then update line 41. Docs
   integrator and registry writer; none; about 2 h.
5. Settle REQ-023: a carried-mass limit and the MIL-STD-810 Method 516 transit-drop category the E1 severity presumes,
   filing the standard's table under `v2/vendor` with a `SOURCES.yaml` entry; add the limit to the brief. Registry
   writer; none; about 1 h.
6. Record the owner's 25 September evening ruling (foundation documents go directly into the public repository) in
   the registry and CONOPS section 7; file W1's decision table and conflict list under `v2/docs/records/w1/` with
   sha256; point CONOPS lines 26 to 27 and 407 to 409 at them. Records integrator; none; about 1 h.
7. Hold Review A for layer 1 (fresh checker, labelled AI review, at a pinned commit), record it under
   `v2/docs/reviews/`, fix, set the brief to BASELINED at that commit and update the integrator line below. Fresh
   checker plus docs integrator; after actions 1 to 6; 2 to 3 h.

**Per board.** Kit-level layer. Board B: the SIM decision changes its holders and SIM protection. All boards: the
public revision rows must say the deliverable folders predate the corrected schematics (declared phases A32, B21,
C24, D12, E17, E5, P4).

> **INTEGRATOR LINE, layer 1:** status at `e3aedb25` IN_PROGRESS; status now: **COMPLETE in the commit that files `v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`** (the narrow verification, at the end of this line); as of commit: branch `fnd/r8int4` (set 4 after H1.1; commits `e5fde2ed` the re-take driver, `95e078a1` and `53292f81` layers 2 and 3, `0da2778b` layer 5, `c351115d` layer 7); items closed since `e3aedb25`: acceptance items 1 to 13 of `v2/docs/reviews/REVIEW-A-LAYER-1-2026-09-27.md` section 6 (purpose, users, scope, exclusions, outcome, commitments, claims against the baseline, rulings recorded, stale texts, the SIM description by SC-13, the mass limit REQ-023 by SC-14, records filed, the review held); its minors N1 and N2 fixed (`2ef6aa2a`); the registry half applied (`public-docs`, SC-13 to SC-16, REQ-023, CFL-010, S-13); item 14 met in part by H1 and H1.1, partial handovers. **Since H1.1:** finding I5 answered in the text: `fnd/hc1`'s held `drafts/layer2-emcon-face.patch` re-derived onto board B's round 8 (`95e078a1`: CONOPS M4, section 4's EMCON and Service rows, 4b's RockBLOCK row and the D-05 paragraph state EMCON as `feasibility/EMCON.md` section 0a does, 15 of 17 transmitters closed locally at desk and 0 of 17 end to end; the Service row names case choice C1's ten 6-32 screws; PANEL line 5 no longer lists the TX lamp as acting without software); I2 (`drafts/conops.patch`: the `public-docs` ruling in CONOPS section 7; its other two hunks were already in the layer 2 closer's text); NEED-03's public statements (V2-SPEC line 29 and correction 29, the brief's compute paragraph; ASM-002); V2-SPEC correction 22, correction 28, line 41 and the brief's SIM row reconciled with round 8's TVS arrays and with CFL-010 resolved on correction 22's description (the eSIM variant's order code stays under S-13); review record: as above. **Release check (27 September 2026):** a fresh reviewer (AI review) judged layer 1 at `f2b7fa66` (`v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2026-09-27.md`, filed in `6209ec7e`): I5 and I2 are CLOSED on the merged CONOPS and PANEL (the check this line had listed as remaining item (1)), and the verdict is FAIL for release on three blocking findings that merges after Review A's second pass caused: B1 (the EMCON count, the 5G supply removal, the EMCON lamp and the 5G land's locating holes stated as before round 8), B2 (the case generators and templates stated as not carrying C1 to C6, readers sent to the HISTORICAL `release/revA/case/`), B3 (REQ-072's night finding missing from the brief; L-02 and the CONOPS runtime cross-reference stale). Applied once in `08f3665a`, all three being wording: B1 and B2 in full (the brief, `README.md`, `v2/README.md`, `v2/BUILD.md`, V2-SPEC lines 10, 23, 24, 59 and 76 with correction 30), B3 in the brief (an exclusion and an open-items row for REQ-072; L-02 named as SC-21's planning value with its authority question left to layer 3's R2) and V2-SPEC line 23; EQ-13's reconciliation with SC-21 is not wording and stays with layer 3's R2. **Status now: IN_PROGRESS** (the reviewer did not call the layer complete, and no fresh reviewer has seen the fixes). Remaining: (1) a re-check of B1 to B3 as fixed in `08f3665a` by a reviewer who wrote none of the changed lines, at one pinned commit, then the brief set to BASELINED in the commit that files that re-check; (2) a snapshot that carries the BASELINED brief, from a pushed branch (acceptance item 14: H1 and H1.1 carry the brief as a CANDIDATE); (3) the release check's minors, m1 (SC-13's reason still says CFL-010 stays open), m2 (FEA-007 in the brief's open items, and "six feasibility blockers on the core" said to exclude it), m3 (N3, the EMCON toggle's cover), m4 (N4, SC-16's "re-checked once"), m5 (N5, the lamp's light-guide hole against "the case"), m6 (`README.md`'s "eleven blind-mate clamps"), m7 (the ruling of 21 September 2026 located in the design appendix near its line 18606), m8 (SC-08 cited beside D-03 for the two key-encryption keys), m9 (the release record's name against SC-16's pattern), and I7; (4) EQ-13 against SC-21, with layer 3's R2; (5) the method change the reviewer asks for (owner's section 4; the same cause twice): state EMCON and the generators' state in the layer 1 pages by reference to `feasibility/EMCON.md` section 0a, `CURRENT-EVIDENCE.md` and the case release, or re-read the five layer 1 pages in every integration that touches EMCON, the case or CONOPS; (6) the fresh usability check of the snapshot (owner's prompt section 7). Owner: the integrator. **Second release attempt (27 September 2026, branch `fnd/rel2` from `953f5658`, the commit that carries this sentence):** B1 to B3 of the release check were checked against the reviewer's exact fixes as applied in `08f3665a`: B1 and B2 are complete as applied (the brief, `README.md`, `v2/README.md`, `v2/BUILD.md` and V2-SPEC lines 10, 23, 24, 59 and 76 with correction 30 say what `feasibility/EMCON.md` section 0a and the case release say); B3 is completed here: the brief's power bullet points at the night finding, its L-02 row names SC-21 as governing M1's duration under the standing rule (the session's, replaced by the owner's own setting), its REQ-072 row names the owner's part as the registry's owner action M-02, and EQ-13 is reconciled with SC-21 (this line's remaining item (4), with layer 3's R2). Minors taken: m1 (SC-13's reason no longer says CFL-010 stays open), m4 (the brief's closing rule in SC-16's words, "re-checked once"), m5 (the FEA-002 row: the lamp's light-guide hole is in the made face plate, not the Peli case), m7 (the ruling of 21 September 2026 located at the design appendix's section 32.362, near its line 18606), m8 (the two key-encryption keys named as SC-08's in the brief). **Status now: IN_PROGRESS** (no fresh reviewer has seen these). Remaining, replacing the list above: (1) a re-check of B1 to B3 and of these completions by a reviewer who wrote none of the changed lines, at one pinned commit, then the brief set to BASELINED in the commit that files it; (2) the snapshot from a pushed branch (acceptance item 14); (3) the minors m2, m3, m6 and m9, and I7; (4) the method change of the reviewer's section 4 (EMCON and the generators' state stated by reference, or the five layer 1 pages re-read at every integration that touches EMCON, the case or CONOPS); (5) the usability check of the snapshot. Owner: the integrator. **Second release check (27 September 2026):** a fresh reviewer (AI review) judged layer 1 at `eb9f9030` (`v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md`, filed byte for byte in the commit that carries this sentence): B1, B2 and B3 of the first check are CLOSED on the text, and of its minors m1, m4, m5 and m8 are closed and m7 in part; purpose, users, scope, exclusions, the commitments split, the rulings record, the SIM description and the mass limit meet the owner's row. The verdict is FAIL for release on one blocking finding, R2-B1: the brief's "six feasibility blockers on the core" (lines 256 to 258) against the registry's seven, FEA-007 (the kit's fit in the Peli 1450 on C1 to C6, core under SC-04, BLOCKED on the owner's purchase L-07 or his acceptance of the residual, with bounds that include failure on the pack's M4a and M5 and on D-07's east plug layout, M17g) absent from the open items, and the D-07 row naming only the board E clamp fit. The fix is wording only, but this was the second attempt, so the release finalizer did not apply it (the owner's section 4; the same cause, the brief restating design state that moves, has now produced B1, B2 and R2-B1): it is open item S-77 and ENGINEERING-QUESTIONS EQ-27, which recommends the reviewer's fix together with the by-reference method. The brief stays CANDIDATE. **Status now: IN_PROGRESS.** Remaining, replacing the list above: (1) S-77 and EQ-27: the reviewer's three edits (lines 256 to 258, an open-items row for FEA-007, the east plug layout in the D-07 row) with R2-m1 to R2-m5 on the same pages, and one of the method remedies; (2) a re-check by a reviewer who wrote none of the changed lines, at one pinned commit, then the brief set to BASELINED in the commit that files it; (3) the snapshot from a pushed branch (acceptance item 14; S-79), bringing START-HERE lines 144, 175 and 218 and CONTINUATION-BRIEF lines 36 to 37 along (R2-m7); (4) the carried minors m3, m6 and m9 (R2-m6), and R2-m7's items for other writers (S-12's title on the locating holes; about 270 W in S-53 and REQ-016's notes against 266 W elsewhere); (5) the usability check of the snapshot. Owner: the integrator. **Targeted fix (27 September 2026, branch `fnd/h2` from `62f26a44`, commit `cecfd0f1`):** after the two attempts the method changes to a targeted fix and a narrow verification (the owner's section 4, the session's choice under his standing rule of 26 September 2026). R2-B1 is fixed with the reviewer's exact wording: `PRODUCT-BRIEF.md` names seven core feasibility blockers, FEA-001 to FEA-007, with FEA-007 (the kit's fit in the Peli 1450 on C1 to C6, core under SC-04, BLOCKED on L-07 or the owner's acceptance of the residual, bounds including failure on M17g, M17x, M4a and M5) in the open-items table and the east plug layout (M17g, FEA-007) in the D-07 row, as the registry and `CURRENT-EVIDENCE.md` state it; R2-m1 is fixed in `v2/BUILD.md` (the lamp test lights the seventeen controller-lit indicators, not `D22`; `PANEL.md` section 9 and `ASSEMBLY.md` step 7 already said so and are unchanged). S-77 is closed by `cecfd0f1` (EQ-27). Not taken in this fix: R2-m2 to R2-m7 and the by-reference method remedy. **Status now: IN_PROGRESS**, the brief a CANDIDATE. Remaining, replacing the list above: (1) the narrow verification of the changed lines by a reviewer who wrote none of them, at one pinned commit, then the brief set to BASELINED in the commit that files it; (2) the H2 snapshot from the pushed branch (acceptance item 14; S-79), with START-HERE and CONTINUATION-BRIEF brought along (R2-m7); (3) R2-m2 to R2-m7 and the method remedy; (4) the usability check of the snapshot. Owner: the integrator. **Narrow verification and release (27 September 2026, branch `fnd/h2`):** a session that wrote none of the changed lines, took no part in the fix and held neither release check verified the targeted fix at `3e4799eb` (`v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`, "AI check (not a qualified engineering review)", sha256/16 `ae70b1a7811ecea1`, filed byte for byte in the commit that carries this sentence): **R2-B1 CLOSED** (brief line 256 names seven core feasibility blockers, FEA-001 to FEA-007, in the reviewer's words; the registry holds exactly seven `kind: feasibility` records, each `prototype_1: core` and BLOCKER, FEA-007 SESSION under SC-04, and `CURRENT-EVIDENCE.md` lists the same seven; the FEA-007 open-items row agrees with `CASE-FIT-UNCERTAINTIES.md` sections 2, 6 and 7 and `CASE-MARGINS.md` rows M17g and M17x; the D-07 row names the east plug layout), **R2-m1 CLOSED** (`v2/BUILD.md` line 113 agrees with `PANEL.md` line 195 and `ASSEMBLY.md` line 208; its line 49 counts light guides, not lamp-test indicators), and no new contradiction in the lines touched. **Method remedy taken** by the session under the owner's standing rule of 26 September 2026, the one the release-2 record asked for before the brief is set BASELINED (its section 4, observations; ENGINEERING-QUESTIONS EQ-27, option (c)): the five layer 1 pages (the brief, `README.md`, `v2/README.md`, `v2/BUILD.md`, `V2-SPEC.md`) are re-read at every integration that touches EMCON, the case, CONOPS or a feasibility record, the integration records the re-read on this line, and a line found stale is corrected by issuing the brief again (its open-items rule). **First re-read, set 5's W3T-F1** (the verifier's observation (c)): the brief (the emission-discipline bullets of "What the V2 kit is" and the FEA-002 row), `V2-SPEC.md` (lines 24 and 220), `README.md`, `v2/README.md` and `v2/BUILD.md` state EMCON by `feasibility/EMCON.md` section 0a's counts, local 15 of 17 and end to end 0 of 17, which EMCON.md still gives after set 5 (section 4b); W3T-F1 (`TX_INHIBIT_n`'s fail-safe level with board C unpowered, S-64, EQ-25, under which RF-002 reads FAIL on boards A and D and CON-010 reads FAIL) is a finding on a shared item, which every end-to-end row already waits on, so no stated count or claim is contradicted; the brief does not name it, and naming it in the FEA-002 row is carried to the brief's next issue. **Applied in the commit that carries this sentence:** the brief's status set to BASELINED (its status paragraph only; the rest byte-identical to the verified file, sha256/16 `c1bb3fe5e082b57e`); S-77 stays closed, its closing evidence extended by one sentence naming the verification; EQ-27 answered. **Status now: COMPLETE** for layer 1's own engineering purpose: the release-2 record's acceptance items 5, 7 and 15, NOT MET on R2-B1 alone, are met with it closed, items 1 to 4, 6 and 8 to 12 were met there, and item 13, the required review, is held with no open blocking finding. It never means a later physical test has passed. The versioned package (item 14) is the H2 snapshot the handover workflow cuts from the pushed commit that carries this line (S-79, EQ-29), bringing START-HERE and CONTINUATION-BRIEF along (R2-m7), then the usability check of the snapshot (the owner's section 7). Not holding the layer, carried: R2-m2 to R2-m7 (with m3, m6 and m9); the verifier's observation (d), brief lines 90 to 92 and 254 naming only the board E clamp fit for D-07 ("laid out" is not "met", so no contradiction; wording for the next issue), and (e), LAYER-STATUS layer 4's H1 row and `REGENERATE.md` line 430 still saying FEA-001 to FEA-006 (those pages' writers); W3T-F1's name in the FEA-002 row. If an open item the brief names closes against the design (FEA-002, FEA-004, FEA-007, REQ-072), the affected requirement reopens in its own layer and the brief is issued again; layer 1 then reopens for that item only. Owner: the integrator. **H2 (27 September 2026):** COMPLETE, carried into the H2 snapshot, which is the versioned package of acceptance item 14 (START-HERE and CONTINUATION-BRIEF brought along, R2-m7's first half; the verifier's observation (e) answered: this page's layer 4 row and REGENERATE.md section 9 now name FEA-001 to FEA-007 where they state the current set). What remains is the H2 section's row for layer 1. Owner: the integrator. **Definition restructure and re-stamp (27 September 2026, branch `fnd/defstab` from `31cd29b9`):** the independent review of handover H2 (`v2/docs/reviews/2026-09-27-h2-independent-review.md` section 4) asked that the completed definition layers stop changing with every count. `fa89c7c6` restructured `PRODUCT-BRIEF.md`: every definition sentence kept word for word under a new head (the rule that reopens it and where each dependency's current state lives), the status and review history moved word for word to an appendix in the same file, and the changing results (the evidence headline, EMCON as generated, the transmitter counts, the lamps as drawn, the case set's commit, board readiness, the runtimes, the count of feasibility blockers) moved word for word to `v2/docs/handover/DEFINITION-STATUS.md`. A session that wrote none of it checked the carry-over (`v2/docs/reviews/DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md`, AI check, sha256/16 `4c09af64cb214448`, filed in `a9f212c7`): **CONTENT_PRESERVED**, no blocking finding. Its m1 (the count of open feasibility blockers moved together with SC-04's application of the fit in the Peli 1450) is answered by accepting the move, the fit as a core condition staying in CONOPS section 2a and FEA-007, and its m5 (the map untracked) by filing the map and its scripts under `v2/docs/records/defstab/`, both in `a9f212c7`; m2, m3, m4 and m6 are carried to the next issue (DEFINITION-STATUS.md). **Re-stamped:** the brief's status paragraph reads BASELINED at `a9f212c7`, an editorial restructure with no definition change of the text baselined at `6b2a9965`, citing the check and the release records the baseline rests on (`v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`, after `v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md`), in the commit that carries this sentence; nothing else in the brief changes. **The re-read from now on** (the check's observation O3; taken by the session under the owner's standing rule of 26 September 2026): the H2 review's rule governs the brief. A figure, a commit or an "as generated" remark inside a kept sentence is its value at the baseline; a changed count or a circuit correction updates DEFINITION-STATUS.md and the records it names, not the brief; the brief is issued again, through layer 1's review, only when a requirement, the scope, the operating concept or another relevant decision changes. EQ-27 option (c)'s re-read at every integration that touches EMCON, the case, CONOPS or a feasibility record continues for the four public pages that still state design state (`README.md`, `v2/README.md`, `v2/BUILD.md`, `V2-SPEC.md`): a stale line there is corrected in that page and recorded on this line, and reopens layer 1 only under the same rule; the brief is no longer part of that re-read. **Status now: COMPLETE**, BASELINED at `a9f212c7`. Owner: the integrator.

### A.2 Layer 2. Concept of operations (the audit at `e3aedb25` and the edition history)

**Status at `e3aedb25`: IN_PROGRESS.** The CONOPS records every ruling and covers the normal, startup, charging and
service cases, but it is not consistent with the committed analyses. The owner's reduced-mode example cannot run on one
module, because Iridium and the panel controller (the SOS path) sit on USB bank 1, which only slots 1 and 2 host,
while LoRa is on slot 3's SPI. Its only ambient trigger relies on the deferred outside pod. Its hot-end consequences
and runtime figures are superseded by POWER-THERMAL. Storage and transport contradict REQ-025 and the +71 C margin
(CFL-017). Duty, fault, shutdown and commissioning behaviour and several product decisions are open, TEST-PLAN's
envelope limits lag the rulings, and Review A is not held. Every item is decidable at desk under the standing rule.
Only the ambient figures of the hot-end controls wait on a physical measurement (EQ-05). Deferring those figures is
justified, because behaviour can be defined on measured internal thresholds, so no layer-2 decision depends on the
number.

**Scope.** Actors, needs NEED-01 to NEED-19, missions M1 to M5, operating modes (normal, reduced, degraded, startup,
charging, shutdown, storage, transport, service, EMCON, blackout, NVG, SOS, ZEROIZE), power states, simultaneous modes
and duty, the runtime statement, the envelope with its carve-outs, fault behaviour and the behaviour of the D-01 core
functions; operator-facing behaviour in PANEL.md; TEST-PLAN's envelope limits. Kit-level.

**Prerequisites.** Layer 1 scope and D-01, D-04; decision 34 and rulings D-02a to D-02e, D-05, D-06, D-10, D-11, D-14,
D-16; consistency (not completion) with the layer 4 facts it describes (`v2/docs/ARCH-PCB-B-IOHA.md` sections 4 and 15,
EMCON.md 4b and 5a, POWER-THERMAL.md 7 and 9, CASE-MARGINS.md 4).

**Deliverables**

| File | Revision (commit, sha256/16) | Current | Note |
|---|---|---|---|
| `v2/docs/CONOPS.md` | `9a151c78`, b9080983ccc03a84 | no | DRAFT for Review A (line 3); has not absorbed PWR-F07, F08, F13, F14, EMCON 5a's latency bounds or IOHA's bank map; cites unpublished drafts at lines 26 to 27, 237 to 238, 408 |
| `v2/docs/OPERATING-ENVELOPE.md` | `9a151c78`, 89de81a11c52f34a | no | sections 3 and 4 derive the hot end from the 10 K and 16 K estimate POWER-THERMAL 9.1 supersedes; section 2 lacks the AW7915-AED and LimeSDR; pollution degree and duty cycle open (lines 340 to 341) |
| `v2/ecad/tools/pcb_envelope.yaml` | `9a151c78`, bc78efbf633223b5 | no | `inside_air_rise_k` 10 and 16 (lines 36 to 38); open list (lines 122 to 126) has only service life |
| `v2/docs/PANEL.md` | `9a151c78`, b1cde9f7ff1ada7b | no | current against the circuit at `45bde541`, but 17 against 16 LEDs (S-39, line 184), SOS indications open, and no statement of the panel's host in the reduced mode |
| `v2/docs/TEST-PLAN.md` | `9a151c78`, e7a90ba054150bb7 | no | three states only (line 8); lacks D-02a's two pass lines (lines 18 to 20); E5 "vent open" (line 20); M7 "proposal" (line 36) |
| `v2/ecad/tools/pcb_board_facts.yaml` | `bed211b6`, 4a0474ddac0b1404 | no | `_product` line 282 "no temperature range ruled yet" (CFL-003) |
| `v2/docs/feasibility/POWER-THERMAL.md` | `428c697c`, bb9c861c9920c8d6 | yes (input) | its findings PWR-F07, F08, F09, F13, F14 name CONOPS and the envelope as edits owed (lines 966 to 973) |
| `v2/docs/ARCH-PCB-B-IOHA.md` | `7808734f`, 6c3c93b7f32f953a | yes (input) | the bank-to-host map (sections 4 and 15) |
| `v2/docs/feasibility/EMCON.md` | `a6f87e9d`, e57a54d1767bcd59 | yes (input) | latency bounds and fault conditions (section 5a) |
| `v2/docs/CASE-MARGINS.md` | `a6f87e9d`, 275a3083db30a7bf | yes (input) | case choices C1 to C6, summarised in CONOPS 7a |
| `v2/docs/ASSEMBLY.md` | `9a151c78`, e4a0b78616c69779 | yes (for D-14's lift procedure) | not audited line by line for this layer |
| `v2/docs/records/w2/w2-runtime.md` | `428c697c`, 2b203982023f6fe6 | yes | the W2 budget CONOPS lines 237 to 238 call unpublished; superseded by `records/rv-pwr/pwr_budget.py` |

**Acceptance items**

| # | Item | Met | Evidence |
|---|---|---|---|
| 2.1 | Normal scenario | yes | CONOPS line 218 and mission M1 (lines 127 to 144); its figures are stale (item 2.14) |
| 2.2 | Degraded scenario | no | CONOPS lines 189 to 204 and 221 cover module loss, heat, cold; REQ-004's recovery time is "TBD, measured on hardware" with no required bound; controls C1 to C4 (POWER-THERMAL lines 876 to 929) absent; shedding to slot 3 leaves bank 1 (Iridium, panel) hostless (IOHA lines 70 to 72, 323 to 326) |
| 2.3 | Startup scenario | yes | CONOPS line 217 with PANEL.md line 133 boot order, the ZEROIZE read before slots, D-02d |
| 2.4 | Charging scenario | yes | CONOPS line 220 (gauge window, VSYS topology since `458b2873`, hostless 256 mA behaviour; S-20 owed) |
| 2.5 | Shutdown scenario | no | CONOPS line 227: graceful shutdown threshold TBD; the proposed backstop that leaves the kit dark until an input returns (POWER-THERMAL 9.3) not described |
| 2.6 | Storage scenario | no | CONOPS line 228 and TEST-PLAN line 8 store with the pack out; REQ-025 says pack fitted; OPERATING-ENVELOPE lines 154 to 155 bound storage by the pack; storage charge TBD; CFL-017 open |
| 2.7 | Service scenario | no | CONOPS line 229 covers opening, the lift, console, key fill, rpiboot, SWD; commissioning (gauge golden image, JP1 arming, D-15 data-flash verification, secure-element provisioning and lock, key fill) has no scenario although D-03, D-12, D-15 depend on it |
| 2.8 | Fault scenarios | no | no operator-level behaviour for panel-controller loss (PANEL.md line 167), ribbon unplugged or a logic rail lost (EMCON 5a F5, F6), fan failure, floor water and battery-bay gas shutdown (NEED-12, REQ-042), a pack protection trip, the four common modes of ASM-002 |
| 2.9 | Operating envelope | no | adopted (decision 34) but sections 3 and 4 rest on rises POWER-THERMAL lines 768 to 770 put below even appendix 32.53's conductance; section 2 lacks the AW7915-AED and LimeSDR; pollution degree and duty cycle open; no storage humidity |
| 2.10 | Simultaneous modes and duty | no | CONOPS lines 332 to 379 carry D-11's bound, but PS-BUSY, every duty cycle and the outlets' minimum contract are TBD; PWR-F13 and PWR-F14 (at most 60 s per key-down, not "minutes", line 359) not applied; controls C2 and C3 absent |
| 2.11 | Explicit behaviour of the core functions | no | SOS has no host path in a one-module reduced mode or after C1 sheds to slot 3; EMCON's latency bounds (1 s per row, 20 s for a running 5G module, 0 at power-up, EMCON.md lines 1277 to 1330) absent from CONOPS 4b and M4; ZEROIZE indications (S-19), SOS indications (S-32), per-bearer delivery targets (S-37) open |
| 2.12 | Product decisions settled under existing authority | no | open: L-02, S-24 and CFL-011, CFL-017, REQ-069, powered-in-transit (CONOPS lines 158 to 159), S-26, D-18, pollution degree, duty profile |
| 2.13 | Every owner ruling recorded | yes | CONOPS lines 405 to 462; OPERATING-ENVELOPE section 8; `pcb_envelope.yaml` and `pcb_requirements.yaml` `owner_rulings` |
| 2.14 | Consistent with the current analyses | no | CONOPS lines 252 to 254, 374 to 375, 389 to 392 against PWR-F07; 142 to 144 and 420 against PWR-F08; line 258 PS-EMCON computed for the circuit before `458b2873`; lines 219 and 256 against the IOHA bank map and C1 |
| 2.15 | TEST-PLAN envelope limits consistent with the rulings | no | TEST-PLAN line 8 has no closed-lid state (CFL-009 nevertheless reads resolved); lines 18 to 20 lack the two pass lines; line 20 vent (CFL-008 open); line 36 "proposal"; M1 to M5 not labelled characterisation |
| 2.16 | Every source the CONOPS cites is in the repository | no | adjudications A01 to A11 (CONOPS line 268 cites A06) and W1's drafts exist only outside the tree; CONOPS lines 237 to 238 call the W2 budget unpublished though `records/w2/` holds it |
| 2.17 | Review A held and recorded | no | CONOPS line 3 DRAFT; no record; the 25 September independent challenge is not filed |

**Unresolved decisions**

| Decision | Downstream impact | Waits on later evidence |
|---|---|---|
| Reduced-mode definition and trigger (S-24, CFL-011) | D-02b's example needs GNSS (bank 2), LoRa (slot 3 SPI), Iridium (bank 1) and APRS (bank 3), and SOS needs the panel (bank 1); no single slot hosts all. Two modules (slots 2 and 3) avoid a board B change; a bank reallocation would change board B. Moves PS-RED, closed-lid heat, C1's shed target, TEST-PLAN's closed-lid test | no (host coverage is a netlist fact; the thermal proof of the chosen set is FEA-004's) |
| Storage and transport configuration of the pack, storage charge, how the +71 C and -33 C margins and E5 apply (CFL-017, S-43, REQ-025) | board P protection coordination (SCF9550 F2 rated -20 to +60 C; BQ7720700 trip 62.7 to 77.5 C), TEST-PLAN E3 to E5 states, CONOPS rows | no: a product decision from the need, not from what the circuit can pass; R-BAT then checks the protection |
| Pack dangerous-goods classification and route (REQ-069) | Transport row, M2, packaging, possibly a UN 38.3 test | no: a desk reading of the ADR; only a test, if required, is later (EQ-03) |
| Whether the kit is powered in transport; the Transport state separated from M2's powered vehicle move | PS-OFF or a reduced state in vehicles, E2 state, transport treatment | no |
| M1 mission duration (L-02, classed OWNER_ACTION) | REQ-016 panel class and input window, input path rating, energy budget | no; reserved to the owner by D-06 (EQ-13); splitting REQ-016 removes the hardware dependence |
| Reference duty profile per bearer, PS-BUSY, the outlets' minimum contract under D-11 | power and thermal budgets, runtime, C2 and C3 thresholds, REQ-017, REQ-018 | no |
| Definition of "aged" (S-26) | REQ-014's hours | no |
| Required failover recovery time (REQ-004) and per-bearer delivery targets (S-37, REQ-003) | supervisor and bridge firmware timing, IOHA A1 to A14 pass lines | no |
| Ambient at which C1 sheds and charging holds off; whether three-module PS-TYP is sustained at +20 C lid open | D-02b's accepted consequences (+35 C, +25 C), REQ-014's reference state, CON-013, possibly the thermal architecture | **yes** (EQ-05); layer 2 can close with behaviour on measured internal thresholds and the numbers stated as bounds |
| Cold-end bought parts: carve-out or replacement for the AW7915-AED and LimeSDR, and a -20 C NVMe grade (PWR-F09) | component picks, envelope carve-outs, IOHA A11 | no (lowering the kit envelope is not an option) |
| Pollution degree (ISO-001) and duty cycle (REL-001) | creepage and clearance for the 54 V PoE rail and the isolation barrier | no |
| D-18, IP68 cooler fans (conditional on the Delta 40 mm fan fitting the coolers) | the sealed case's thermal path | no: a desk fit check |

**Stage-gate cycles and remedies**
- L-02 is classed OWNER_ACTION while the standing rule forbids asking the owner, so as classed it can never close.
  Remedy: split REQ-016 (layer 3) so no hardware depends on L-02, and record the classification explicitly.
- CON-013 and REQ-052 tie layer-2 statements to TEST-PLAN E3 (a built prototype) or the heat-balance test. Remedy:
  state behaviour on measured internal thresholds (POWER-THERMAL 9.3) and allocate the ambient figures to FEA-004,
  whose heat test gates placement freeze, not layer-2 closure.
- Review A undefined: same remedy as layer 1.

**Next closing actions**
1. Decide the reduced mode under the standing rule so D-02b's bearer set and the SOS path have hosts (recommended: two
   modules, slots 2 and 3; trigger the lid reed on J_TAMP or C1's internal thresholds; confirm from IOHA section 7
   that an unpowered slot 1 moves bank 1 to slot 2). Record as a session choice under S-24 and CFL-011 with its
   departure from the example's "one module" stated; update CONOPS, PS-RED (recomputed with
   `records/rv-pwr/pwr_budget.py`), M2, M5, OPERATING-ENVELOPE section 4, `pcb_envelope.yaml`, and ask the power
   stream to move C1's shed target (POWER-THERMAL lines 98 and 876; ARCHITECTURE line 832). Docs integrator with the
   power stream; none; half a day.
2. Restate the hot end (PWR-F08) in OPERATING-ENVELOPE 3 and 4, `pcb_envelope.yaml` and V2-SPEC line 73 as
   POWER-THERMAL 9.1's per-state bounds, with C1 to C4 as the behaviour and FEA-004's heat test as the evidence that
   fixes the numbers; add the AW7915-AED, LimeSDR and RA30H1317M1 rows; take PWR-F09 without narrowing the envelope;
   rule pollution degree and duty cycle (or list them open in `pcb_envelope.yaml`); fix `_product` (CFL-003). Commit
   the config inputs, re-pin ENV-001, run the suite once. Docs integrator and registry writer; none; half a day.
3. Bring CONOPS 4a, 5 and 6 to POWER-THERMAL (PWR-F07 figures and bounds, PS-TYP with outlets and PS-BUSY as bounded,
   APRS key-down at most 60 s with K1 to K5 and C4, controls C2 and C3 with what the operator sees, PS-EMCON for the
   `458b2873` circuit, sources pointed at `records/w2` and `records/rv-pwr`); mirror PWR-F07 in V2-SPEC line 23. Docs
   integrator with rv-pwr; after action 1; half a day.
4. Settle the operational profile under the standing rule: duty per bearer and PS-BUSY, the outlets' minimum contract,
   "aged" (S-26), M1's duration by splitting REQ-016 (see layer 3); record each as an SC entry; open a layer 4 finding
   rather than shorten a mission. Registry writer with docs integrator; none; half a day.
5. Settle storage and transport (CFL-017, S-43, REQ-025, REQ-069) from the product need; separate Transport from M2;
   classify the pack at desk from the ADR text, filed under `v2/vendor` with a SOURCES entry; merge r8bat's TEST-PLAN
   rewrite only after checking its option against "do not select a qualification condition merely because the
   circuit can pass it". Battery stream and docs integrator; after the r8bat merge; 1 day.
6. Add the missing scenarios: a fault table (panel-controller loss, ribbon unplugged, +3V3_DEV loss, fan failure,
   water and gas shutdown, pack trip and backstop, input faults, the four common modes) with indication and recovery;
   SOS in the reduced mode and after a bank-1 host loss; commissioning (golden image, JP1, D-15 verification,
   secure-element provisioning and lock per ZEROIZE.md section 3, key fill); graceful shutdown; a required REQ-004
   bound; per-bearer targets (S-37). Docs integrator and registry writer; after action 1; 1 day.
7. Carry EMCON.md 5a into CONOPS 4b and M4 (latency bounds, fault conditions F1 to F9, the REQ-030 text drafted in
   EMCON section 8); close S-19, the operator half of S-32 and S-39 in PANEL.md. Docs integrator and registry writer;
   none; 2 to 3 h.
8. TEST-PLAN envelope limits: E5 without a vent and E8 naming Peli's valve (CFL-008); the closed-lid state and thermal
   test (D-02b), with CFL-009 reopened until they exist; D-02a's two pass lines on E3 and E4 and SC-03's on E5; E4's
   start per D-02d; M1 to M5 labelled characterisation; M7 at decision 34's level; current board names. Docs
   integrator; after action 5; 2 to 3 h.
9. Settle D-18 at desk from the Delta 40 mm fan and CM5 Cooler drawings (file the fan drawing first). Parts stream;
   1 to 2 h.
10. File adjudications A01 to A11 and W1's drafts under `v2/docs/records/` with sha256; correct CONOPS lines 26 to 27,
    237 to 238, 268, 408 to cite tree paths. Records integrator; none; 1 to 2 h.
11. Hold Review A for layer 2 (fresh checker, AI review, against section 3 of the owner's prompt and against IOHA 15,
    EMCON 5a and POWER-THERMAL 9 at a pinned commit); record, fix, mark BASELINED, update the line below. After
    actions 1 to 10; half a day.
12. **Needs the owner's purchase authorisation:** run the empty-case heat-balance test (EQ-05) and re-derive C1 to C4
    and D-02b's figures. A person with the hardware, the power stream for the analysis; 1 to 2 days bench plus lead
    time. Not a condition of layer 2 closure under option (a) of EQ-05.

**Per board.** Kit-level. B: the reduced-mode definition decides which slots stay powered; moving Iridium or the
panel off bank 1 would change board B, which a two-module reduced mode avoids. P: the storage and transport decision
sets F2 and the BQ7720700 over-temperature coordination. A: the outlets' minimum contract and C2's shed through
PD_SW_EN and POE_SW_EN; the graceful shutdown threshold. D: the 60 s key-down depends on the flange sensor (PWR-F15).
E: the lid reed on J_TAMP as trigger; the water and gas shutdown behaviour. C: panel indications (S-19, S-39, SOS)
and the hardware EMCON lamp (S-44).

> **INTEGRATOR LINE, layer 2:** status at `e3aedb25` IN_PROGRESS; status now: **COMPLETE at `79963b3b`** (the second release check, at the end of this line); as of commit: branch `fnd/r8int4` (set 4 after H1.1; commits `e5fde2ed` the re-take driver, `95e078a1` and `53292f81` layers 2 and 3, `0da2778b` layer 5, `c351115d` layer 7); items closed since `e3aedb25`: round 8's pack temperature ladder (`dd39fb15`, `73d5df1e`); **the closer hc2 merged** (`95e078a1`: CONOPS, OPERATING-ENVELOPE, PANEL section 9, TEST-PLAN with the new row E3-H, `pcb_envelope.yaml` re-pinned, records `v2/docs/records/hc2/`), its Review A layer 2 record filed (`v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27.md`, AI review: first pass FAIL on B1 to B7, second pass FAIL on P2-B1 and P2-B2); the targeted fixer c23 answered P2-B1 (CONOPS section 7's D-02b row names the session's choices apart from the ruling) and P2-B2 (the hot stop past the heat stage on the cells' measured temperature, H1 at +56.5 C shedding to the minimum load and H2 at +57.0 C shutting the kit down; session choices SC-49 and SC-50, requirement REQ-077; `records/hc3/c23-response.md`), both CLOSED by a fresh verifier (AI); the verifier's new contradictions fixed at integration: OPERATING-ENVELOPE section 4 and `pcb_envelope.yaml` state CONOPS 4c's release (H1 by itself at +46.5 C and after 30 minutes, H2 only by MAIN), the Heat stage row says the gauge's charge window acts first and the hot stop before OTD, board P's second level, SOT and the PTC, and the present-tense guarantees in CONOPS 4c and OPERATING-ENVELOPE 4 are restated as what REQ-077 requires and the design intends, FEA-004 open; the mock-up's timing in CONOPS 4a and the D-06 row (`c351115d`); the needs pin re-pinned twice, the needs table unchanged. **Release check (27 September 2026):** a fresh reviewer (AI review) judged layer 2 at `f2b7fa66` (`v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2026-09-27.md`, filed in `6209ec7e`): P2-B1 and P2-B2 are CLOSED on the merged text, which was this line's remaining item (1) (no record of the c23 verifier exists in the tree, its CLOSED living only in the session's workflow journal, so this release review is the re-check on the merged text), every figure it checked reproduces, and the verdict is FAIL on four blocking findings. Applied once in `08f3665a`, the wording and citation parts: B1 (CONOPS M4, 4b.1 and 4f; OPERATING-ENVELOPE section 4; TEST-PLAN section 4 with REQ-071; PANEL sections 1 and 9 with one statement that the lamp test cannot light `D22`), B3 (the first Review A pass filed as `v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27-pass1.md`, sha256 `e854c2a46ea3d542`, and its brief as `v2/docs/reviews/2026-09-27-review-A-layer2-brief.md`, `fe6ca95b6c6356a8`, both byte for byte; CONOPS's header points at them; A06's records cited in CONOPS 4a and OPERATING-ENVELOPE section 4), B4 (a) (the three lagging documents named as hand-offs in CONOPS section 4's Reduced row and 4c, and in the layer 4 and 5 lines), (b) (S-01 and S-44 restated to what remains) and (d) (CONTINUATION-BRIEF section 8's rows marked superseded); the needs pin, the envelope's two pins and twenty readings rebound. **Status now: IN_PROGRESS.** Remaining: (1) B2, not wording: E3-H and REQ-077's prototype acceptance gain a forced run that makes both steps act (the chamber raised from +40 C in steps to at most +55 C, recorded as a protection test beyond the envelope, the +59 C abort kept) and a room-temperature detection-to-action check that walks one gauge cell reading through +55.0, +56.5 and +57.0 C and back below +46.5 C with the 30-minute hold, the MAIN release after H2 and HOT-R1's four line states, a run in which a step never acted reading NOT_VERIFIED, never PASS (the TEST-PLAN owner and the registry writer; layer 3's R4 is the same item); (2) B4 (c), EQ-13 against SC-21, with layer 3's R2; (3) B4 (e), an ENGINEERING-QUESTIONS entry for BAT-F19 (CFL-017) in group C with its three routes, its evidence (THERMAL-COORDINATION 9a, OPERATING-ENVELOPE section 8's +61.6 C floor at +55 C), a recommendation and its cost; (4) a re-check of B1, B3 and B4 as fixed by a reviewer who wrote none of the changed lines, limited to the difference from the release review's sha256 values, then CONOPS marked baselined in the commit that files it; (5) the release review's minors m1 to m16; (6) the items that belong to later stages and stay open where they belong: HOT-R1 on boards A and E before their layout entry (S-57, EQ-22), a non-destructive hardware stage behind the hot stop (S-58, EQ-23), whether the hot stop fires inside the envelope (FEA-004, EQ-05, T-H1), BANK-R1 on board B (S-54) and the cold end's 3.6 W/K bound (S-55). Owner: the integrator, the TEST-PLAN owner, the registry writer and the board A, B and E authors. **Second release attempt (27 September 2026, `fnd/rel2`, the commit that carries this sentence):** remaining item (1), B2, answered: `TEST-PLAN.md` P15 forces the hot stop at room temperature on the pack and on shore (one cell thermistor input substituted by a make-before-break decade resistance, read back in the gauge's `DAStatus2()` and never at its OTD of +57.5 C, because the gauge's own temperature offsets reach at most 12.7 K; H1 and its release, H2 through `PI_KILL` and MAIN, MASTER WARN and the e-paper, HOT-R1's four states, the TMP117 stand-in), E3-H gains its stepped run beyond the envelope (+40 C by 2 K an hour to at most +55 C, the +59 C abort kept) and the rule that a step that acted in no run reads NOT_VERIFIED, E3-L's pass line is unchanged, and REQ-077's prototype acceptance says the same (layer 3's R4 is this item). B3 completed: the first Review A pass is cited by its filed name at CONOPS lines 20 and 1138, TEST-PLAN line 3 and OPERATING-ENVELOPE line 36 (CONOPS lines 45 to 48 already did), and `records/README.md` carries both filed files with their sha256 (`e854c2a46ea3d542`, `fe6ca95b6c6356a8`); no record of the c23 verifier exists, as stated above. B4 completed: C1 is defined one way, as CONOPS 4c and SC-17 (the layer 2 closer's reduced-mode choice, `records/hc2/sc.md` row 1) state it: shed to the reduced mode on slots 2 and 3, then, reached again, to the heat stage's one module, which is slot 3 after BANK-R1 and slot 2 as board B is generated (CONOPS 4c's own text and SC-18; no source read contradicts it), in `feasibility/POWER-THERMAL.md` sections 1, 9.1, 9.2 and 9.3, `ARCHITECTURE.md` section 8 and `HW-FW-CONTRACT.md` FW-C09, which also gains FW-C13, FW-C14, FW-E10 and V-C13 for the hot stop and HOT-R1; (c) EQ-13 rewritten with SC-21 governing (layer 3's R2); (e) EQ-26 written for BAT-F19 (CFL-017) in group C, with its three routes, the evidence, the session's recommendation and the cost. Fifteen readings rebound, the needs pin and the envelope's two pins re-taken (`records/rel2/post_docs_registry.py`). **Status now: IN_PROGRESS.** Remaining, replacing the list above: (1) a re-check of B1 to B4 as now fixed by a reviewer who wrote none of the changed lines, limited to the difference from the release review's sha256 values, then CONOPS marked baselined in the commit that files it; (2) the release review's minors m1 to m16; (3) the later-stage items listed above (HOT-R1 on boards A and E, S-57 and EQ-22; S-58 and EQ-23; FEA-004, EQ-05 and T-H1; BANK-R1, S-54; S-55). Owner: the integrator, the TEST-PLAN owner, the registry writer and the board A, B and E authors. **Second release check and release (27 September 2026):** a fresh reviewer (AI review) judged layer 2 at `eb9f9030` (`v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md`, filed byte for byte in the commit that carries this sentence): B1 to B4 of the first release check are CLOSED on the text, every figure it checked reproduces (`records/hc2/pwr_red2.out` and `hotstop_bounds.out` byte for byte), the envelope and registry fixtures pass on a clean copy, and there is no blocking finding: layer 2 meets the owner's COMPLETE test for its own engineering purpose. The record's release steps: (1) integrated onto main `91894cd7` by rebasing `fnd/rel2` (`7dfbfb16`, `79963b3b`; onto `391d8579` first, resolved by `records/rel2f/resolve_rebase.py` and checked line by line by `check_rebase.py`, then onto the consolidated re-take with no conflict in a document, the pages rendered again and `edge_length.py`'s tool entry added by `records/rel2f/apply_compat.py` so that no current reading lost its class): CONOPS (`3ff59edc96a3f8f4`), OPERATING-ENVELOPE (`43361b02743cf3af`), TEST-PLAN (`4f15bd02a6a8be46`), `pcb_envelope.yaml` (`bbcc2b5cbb721372`) and the four Review A and release records are byte-identical to the files the reviewer read, and PANEL.md differs only by set 5's own row (U28's EMCON_EF_FLT on P1.2, no operator item, read by the reviewer); the needs pin and ENV-001's pins hold at `79963b3b`; `test_envelope_data` and `test_requirements` pass there (116 passed with test_evidence_class, test_pack_protection and test_layout_entry_stages); HOT-R1's netlist premises were re-read by the reviewer on `391d8579`'s generators, which `79963b3b` carries unchanged; (2) CONOPS's status line and its Review A paragraph name the baseline and the record, START-HERE no longer calls the closed-lid reduced mode "still to be defined" (n7), and the needs pin and the three readings bound to CONOPS are re-taken on that header change alone (`records/rel2f/post_docs_registry.py`); (3) the versioned package is the next handover snapshot, which the integrating session cuts from the pushed commit that carries this line (S-79). **Status now: COMPLETE at `79963b3b`** (the content; recorded in the commit that carries this sentence). Not holding the layer, and named here so that the "not hidden" test can be read where the status is (n8): M-02 and S-53 (EQ-13: M1's night on D-06's pack is the owner's to carry, its day the session's, before boards A, E and P enter layout; M1's duration is set by SC-21, so no mode, trigger or bearer set waits on them), BAT-F19 (CFL-017, EQ-26: a qualification margin, not an operating limit), and the later-stage items above (HOT-R1, S-57 and EQ-22; S-58 and EQ-23; FEA-004, EQ-05 and T-H1; BANK-R1, S-54; S-55; REQ-069 and EQ-03). If one of them closes in a way that changes a mode or a product decision (FEA-004 ending in an owner trade on D-02b's closed-lid scope, or M-02 choosing a different pack), layer 2 reopens for that item only and a new version is issued (the owner's section 8). Carried minors, none blocking: the second check's n1 to n6, n9 and n10 (n4 and n5 are layer 5's text, n9 and n10 layers 3 and 4's) and the first check's m1 to m16 (m13 partly answered by HW-FW-CONTRACT). Owner of the minors: the integrator, the TEST-PLAN owner, the registry writer and the layer 5 writer. **H2 (27 September 2026):** COMPLETE, carried into the H2 snapshot, the versioned package the release record's step (3) names (S-79 for layer 2's part). What remains is the H2 section's row for layer 2. Owner: the integrator. **Definition restructure and re-stamp (27 September 2026, branch `fnd/defstab` from `31cd29b9`):** as for layer 1 (the H2 review's section 4), `fa89c7c6` restructured `CONOPS.md`: every definition sentence kept word for word under a new head, 18 blocks of review and revision history moved word for word to an appendix in the same file, and 7 blocks of changing results (M4's gaps and counts, section 4b's counts and circuit commits, 4b.1's state, 4c's HOT-R1 and BANK-R1 readings and the targets' registry closures) moved word for word to `v2/docs/handover/DEFINITION-STATUS.md`; the needs table byte-identical. The check of the carry-over (`v2/docs/reviews/DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md`, AI check, filed in `a9f212c7`): **CONTENT_PRESERVED**, no blocking finding; the needs table, the registry's 19 quoted needs and the pin agree, and the notes of the three readings rebound in `fa89c7c6` (REQ-005, CFL-016 and CFL-014) are true; its m3 (appendix A12's last sentence and A14, two current cross-document states in the unmaintained appendix) is carried to CONOPS's next issue. **Re-stamped:** CONOPS's status paragraph reads BASELINED at `a9f212c7`, an editorial restructure with no definition change of the text baselined at `79963b3b`, citing the check and the release record the baseline rests on (`v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md`), in the commit that carries this sentence; nothing else in CONOPS changes, the needs pin is re-taken on that paragraph alone (`bbcab7c9876f7993` to `6ebe6760c4312bca`) with the needs table byte-identical, and REQ-005, CFL-016 and CFL-014 are rebound with an entry each. From now on the H2 review's rule governs CONOPS as layer 1's line states it for the brief. **Status now: COMPLETE**, BASELINED at `a9f212c7`. Owner: the integrator.

### A.3 Layer 3. Requirements (the audit at `e3aedb25` and the edition history)

**Status at `e3aedb25`: IN_PROGRESS.** The registry is structurally sound: the validator reports 0 errors, the
generated trace is current and the CONOPS pin matches. It is not complete. Eight core records have an unsettled limit
or scope (REQ-003, REQ-004, REQ-014, REQ-016, REQ-018, REQ-030, REQ-069, ASM-002). One core conflict is open (CFL-010),
four more are open, and three "resolved" conflicts still fail on their sources. REQ-050's test-plan trace is absent,
NEED-02 lacks a behavioural requirement, ten deferred TBDs can still change a part, interface, outline or protection
element (D-01 designs and fits deferred functions, so deferral does not excuse them), and Review B has not been held.
Every item is closable under existing authority (the standing rule and desk research); none needs a purchase, an
outside contact or a physical test.

**Scope.** Source-linked, measurable requirements with acceptance, applicability (prototype 1 core or deferred under
D-01), allocation, verification method and phase; contradictions resolved; needs, design choices, assumptions and
historical decisions kept apart; every TBD listed with its effect. Authority: `v2/ecad/tools/pcb_requirements.yaml`
(132 records: 71 REQ, 22 CON, 7 ASM, 3 CHO, 6 SPD, 17 CFL, 6 FEA; 19 needs quoted from CONOPS section 2 and pinned by
sha256; 28 owner rulings; 11 session choices; 35 open and 38 closed items; status counts DEFINED 76, TBD 27,
CONFLICT_OPEN 5, CONFLICT_RESOLVED 12, FEASIBILITY_OPEN 6, SUPERSEDED 6). The six FEA records sit in this registry but
are layer 4 blockers; they hold layer 3 only where a failure would change a requirement's statement (FEA-003 could
reopen NEED-03's scope, FEA-004 D-11's declared values), and that dependency must be stated.

**Prerequisites.** Layer 1 (PRODUCT-BRIEF at `b69f20db`); layer 2's needs table, pinned at `pcb_requirements.yaml`
line 120 (`needs_document_sha256` b9080983ccc03a84, equal to CONOPS at `e3aedb25`; any CONOPS edit must re-pin in the
same commit); the owner rulings and decision 34; OPERATING-ENVELOPE and `pcb_envelope.yaml`; TEST-PLAN as the
verification plan REQ-050 requires to trace every test.

**Deliverables**

| File | Revision (commit, sha256/16) | Current | Note |
|---|---|---|---|
| `v2/ecad/tools/pcb_requirements.yaml` | `a6f87e9d`, acd19f7bfc50b7ad | yes | `baseline_state` DRAFT_FOR_REVIEW_C (line 117); `sources_read_at` eadbe571 (line 118) |
| `v2/docs/REQUIREMENTS-TRACE.md` | `a6f87e9d`, 6788c517b898c86a | yes | generated; `rules_render.py --requirements --check` reads current |
| `v2/ecad/tools/rules_lib.py` | `dd3b9074`, c0458c53923d7925 | yes | the validator; it does not check that file:line citations still resolve, that a resolved conflict's sources were corrected, or that every rule has a parent record |
| `v2/ecad/tools/rules_render.py` | `dd3b9074`, d9dfa6fb8a1961ef | yes | renderer; runs from a plain export with PyYAML 6 and Python 3.11 |
| `v2/ecad/tools/tests/test_requirements.py` | `9f848223`, 01a6137e30fccfb9 | yes | 66 passed, 0 failed, 2 skipped in an export (the skips need the gitignored `out/rule-audit`); fixtures do not establish that the requirements are right |
| `v2/docs/CONOPS.md` | `9a151c78`, b9080983ccc03a84 | yes (as pinned) | carries TBDs the registry mirrors, and the Storage row that REQ-025 contradicts |
| `v2/docs/TEST-PLAN.md` | `9a151c78`, e7a90ba054150bb7 | no | no requirement ids at all, so REQ-050 is unmet; E5 vent (CFL-008); E3 and E4 pack fitted (CFL-017); no closed-lid state; test article names superseded boards |
| `v2/docs/OPERATING-ENVELOPE.md` | `9a151c78`, 89de81a11c52f34a | yes | lines 154 to 155 treat storage as pack fitted, against CONOPS line 228 |
| `v2/docs/V2-SPEC.md` | `9a151c78`, df8ac22603440bc5 | no | the most cited source (41 line citations); Cellular row still eSIM plus nano-SIM (CFL-010) |
| `v2/ecad/tools/pcb_rules.yaml` | `dd3b9074`, abd4e687bef6fe0d | yes | 59 rules; 27 are named by no record (below) |
| `v2/ecad/tools/pcb_decisions.yaml` | `31ce3840`, 1367edbf54a842d3 | yes | 21 ruled, 4 closed, 0 open |
| `v2/ecad/tools/pcb_interfaces.yaml` | `7808734f`, 4a553b9d3c304f63 | yes | interfaces a record may be allocated to |
| `v2/ecad/tools/pcb_board_facts.yaml` | `bed211b6`, 4a0474ddac0b1404 | no | line 282 (CFL-003); line 259 "about 200 Wh" against D-06 |
| `v2/ecad/tools/pcb_pack_protection.yaml` | `4fbfa479`, 03dc766d99cf03f7 | no | line 24 "4S3P or 4S4P, about 200 Wh" (S-27; CFL-006 marked resolved) |
| `v2/ecad/tools/pcb_energy_chain.yaml` | `c161b3d8`, 935e524eed0ee4d1 | no | lines 19, 46, 53 describe the old pack |
| `v2/docs/GROUNDING-AND-SHIELDS.md` | `daca8888`, 8f305cc23551084f | no | "nine SMA bulkhead jacks" and "the battery module's own enclosure" (lines 15 to 16) against SC-07 and D-06 |
| the FEA pages (EMCON, ZEROIZE, FAILOVER-FABRIC, POWER-THERMAL, DECOUPLING, the battery REVIEW-REQUEST) | as listed in layer 4 | yes | REQ-071, REQ-035 and REQ-018 take their pass lines from them |

**Acceptance items**

| # | Item | Met | Evidence |
|---|---|---|---|
| 3.1 | Every record traces to a need of CONOPS section 2, pinned by content | yes | validator 0 errors; the pinned sha equals CONOPS; every parent is a NEED-nn |
| 3.2 | Source-linked | yes | 132 of 132 carry `source`; VERIFIED 125, INFERRED 7 (REQ-014, REQ-018, CON-006, CON-014 among them, each with its derivation); REQ-023 is the one "none (gap)" |
| 3.3 | Citations resolvable by a recipient of the snapshot | no | line citations were read at `eadbe571`; 163 of the 276 file:line citations point into files changed since (V2-SPEC 41, TEST-PLAN 28, OPERATING-ENVELOPE 22, ARCH-PCB-B-IOHA 21, PANEL 12, gen_sch_b 11, others); a ZIP without git history cannot read `eadbe571` |
| 3.4 | Measurable acceptance on every requirement | no | 27 TBD records. Core TBDs with an unsettled limit: REQ-003 latency (line 1289, S-37), REQ-004 failover timeout (line 1395), REQ-014 "aged" (line 2348, S-26), REQ-016 solar window and panel class (line 2541, L-02), REQ-018 key-down time and state-of-charge floor (line 2721, S-14), REQ-030 bench emission threshold (line 3563), REQ-069 pack classification (line 2831), ASM-002 NEED-03 common modes (line 2003). Undeclared TBDs inside DEFINED records: the outlets' "minimum contract" in REQ-017 (line 2577) and CON-019 (line 2777, which reads PASS), TBD in CONOPS lines 260 and 377; REQ-024's "+35 C" carve-out, a proposed control per CON-012 (line 6120) |
| 3.5 | Applicability | yes | 126 live records carry core or deferred with a basis; markets in REQ-053. To disclose: SC-02 (line 513) makes LoRa and cellular data named exceptions to NEED-03 because making them critical would reopen board B's floor plan: recorded and reversible, but a scope reduction |
| 3.6 | Allocation | yes | every record has `allocated_to` (validator) |
| 3.7 | Verification method and phase on every record | yes | all 132 (SCHEMATIC 112, PLACED_BOARD 7, PROTOTYPE 7, RELEASE_PACKAGE 4, ROUTED_BOARD 2); final phase never precedes it |
| 3.8 | No requirement's check needs a later stage's product (owner section 5) | no | REQ-048 (line 5198) is checked "against the placed boards before layout entry" at phase SCHEMATIC; REQ-004 (line 1395) takes its pass line from the measurement it judges; the FEA stages are clean |
| 3.9 | Contradictions resolved | no | 5 CONFLICT_OPEN (CFL-003, 008, 010, 011, 017); 3 CONFLICT_RESOLVED whose acceptance fails on their sources (CFL-006, CFL-009, CFL-007); unrecorded contradictions (CONTINUATION-BRIEF section 8) |
| 3.10 | Needs, design choices, assumptions and historical decisions distinguished | no | largely met (19 needs, CHO 3, ASM 7, SPD 6, 28 rulings with D-08 reversed and kept, 11 session choices with SC-06 withdrawn and kept, 38 closed items); but 17 REQ statements embed a part or implementation choice (REQ-016 "through the LT8705A tracker", REQ-043 IP68 fans, REQ-044 BQ4050) and some TBDs carry design decisions (CON-011, REQ-042, REQ-061) |
| 3.11 | TBDs listed with their effect | yes | 27 TBD records each with `tbd_effect`; the trace's TBD list has 27 rows; the two undeclared TBDs above are not in it |
| 3.12 | Every critical mission outcome has a measurable requirement | no | NEED-01 has one record, REQ-003, TBD; NEED-02 has no behavioural requirement that a message is delivered over another bearer when one is down; NEED-03 REQ-004 and ASM-002 TBD; NEED-05 REQ-014, REQ-016, REQ-018 TBD; NEED-08 REQ-071 DEFINED but REQ-030 TBD |
| 3.13 | REQ-050 (core blocker): TEST-PLAN traces every test to a requirement and states each test's purpose | no | TEST-PLAN contains no requirement id; E3 and E4's purposes live in OPERATING-ENVELOPE line 293 |
| 3.14 | Review B held and the registry baselined | no | no record in `v2/docs/reviews/`; `baseline_state` DRAFT_FOR_REVIEW_C; no record mandates a qualified review for this layer, so a labelled AI review can serve |
| 3.15 | Every open item is carried by a record | no | S-20 (charge current inside the cells' cycle-life rating, line 795) has no waiting record |
| 3.16 | Every BLOCKER or MUST_JUSTIFY rule has a parent record (added from a finding) | no | 27 of 59 rules are named by no record: SCH-001, SCH-002, SCH-005, PI-001, PI-003, GND-001, STK-001, STK-002, RET-001 to RET-004, IMP-001, IMP-002, PAIR-001, ANA-001, PLC-002, RTE-001, RTE-002, VIA-001, VIA-002, PLN-001, DFM-001, DFA-001, DOC-001, OUT-001, SGN-001 |
| 3.17 | The generated trace is current and not hand-kept | yes | `rules_render.py --requirements --check` current in a checkout and an export |
| 3.18 | Versioned, portable layer package | no | citations anchored at `eadbe571`; closed-by-commit checks need git; the PASS-to-rule-class check needs the gitignored `out/rule-audit/*.json` |

**Unresolved decisions**

| Decision | Downstream impact | Waits on later evidence |
|---|---|---|
| NEED-03 common modes (ASM-002, S-36): +5V_DEV and +3V3_DEV single converters on A, the J_PANEL ribbon, the KSZ9897R, the single-master kit I2C bus: mitigate or name as exceptions | A converters, B switch and I2C topology, C ribbon; the public NEED-03 claim (V2-SPEC line 29) | no. An accepted residual lowers NEED-03's claim, so it must be visible and must not be written as an OWNER residual |
| D-11 declared values (REQ-018, S-14, SC-10) and the outlets' minimum contract (POWER-THERMAL line 1176 proposes 0 W, outlets off) | chain short-time ratings (PWR-F12), A's pack-path copper, D's flange sensor, gauge configuration, REQ-017, CON-019, REQ-059 | no; FEA-004 may reopen them, which belongs on FEA-004, not as a TBD here |
| REQ-004 failover bound | HAL adoption timers, supervisor firmware, IOHA A1 to A14 | no |
| REQ-016 split: the solar input window against M1's energy balance | board E's LT8705A stage, its protection and connector | no; only the mission duration is the owner's (EQ-13) |
| REQ-014 "aged" (S-26); REQ-003 delivery and latency (S-37); REQ-030 emission threshold per antenna port | runtime statement, bridge acceptance, EMCON bench pass lines; no board change | no |
| SIM description (CFL-010, S-13) and the SIM TVS array | board B holders and TVS, V2-SPEC, BOM | no |
| CM5 radios and antennas (CON-011, S-16) | B's J_BM3 path, case jack count, EMCON rows, NEED-16 | no if the recommended route is taken (EQ-04) |
| Water and battery-bay gas response (REQ-042): thresholds, the device that opens the pack, whether the SGP41 senses hydrogen | E to P interface (J_SMB is 4 pins), P's shutdown input, possibly a new sensor | no |
| Chassis bond (REQ-061, GND-002) | every board's ESD and arrestor return, the stud and connector plate, REQ-029 | no; session work since 21 September (appendix 32.362) |
| Other hardware-affecting deferred limits: REQ-058 SDR damage level, REQ-043 fan part and fit (D-18), REQ-040 holdover drift, REQ-041 sensor accuracy, REQ-034 NVG claim level, REQ-011 tablet envelope, REQ-023 mass, REQ-059 PA duty, CON-015 third 5G jack, S-20 charge current, S-19 with S-39 and CON-021 | limiter part, coolers, RTC, sensors, C LEDs and filters, lid bracket, pack and plate trades, D thermal path, A site and bulkhead, gauge and charger configuration | no: D-01 designs and fits deferred functions, so their parts and protection must be settled before layout |
| Transit temperature with the pack fitted, reconciling SC-09 with the product requirement | TEST-PLAN E3, operating instructions, REQ-025 | no |
| Pack transport classification (REQ-069) | procedure and CONOPS only | no (EQ-03) |

**Stage-gate cycles and remedies**
- REQ-048 (line 5198) needs placed boards at phase SCHEMATIC. Remedy: SCHEMATIC acceptance on the netlist (every rail
  has a current limit and a measurement point, every programmable device its header), final phase PLACED_BOARD.
- REQ-004 (line 1395) takes its pass line from the measurement it judges, so it cannot fail. Remedy: a need-derived
  bound now; per-device timeouts become characterisation.
- ASM-002 (line 2003) and S-36 (line 864) wait on Review C (architecture), while Review B (requirements) gates the
  architecture budgets. Remedy: decide scope at layer 3, mitigations at layer 4.
- CON-013 (line 6156) holds a charge hold-off ambient TBD "until the enclosure conductance is measured". Remedy: type
  it as characterisation of REQ-046's window so it does not hold a baseline.
- No cycle in the six FEA stages: STAGE_CANNOT_NEED is enforced, and each layout-entry stage needs DESK or
  DEVELOPMENT_HARDWARE only.

**Next closing actions** (all doable now under existing authority; session choices get SC ids at merge, since an
unmerged branch already drafts an SC-12)
1. Settle the core limits: REQ-003 per-bearer delivery and latency (closes S-37); REQ-004 re-adoption bound; REQ-014
   "aged" as a fraction of the cell's minimum capacity with its source; REQ-030 a numeric emission threshold per
   antenna port from a cited limit. Each as a session choice; TBD to DEFINED; re-render the trace. Integrator; about
   3 h.
2. Set D-11's values in REQ-018 (key-down time; rest-voltage floors from SC-10) and define the outlets' minimum contract
   (0 W, outlets off) in REQ-017, CON-019, REQ-018 and CONOPS lines 260 and 377; write on FEA-004 that its failure
   would reopen them; REQ-059's duty equal; re-pin the CONOPS sha. Integrator with the power stream; about 2 h.
3. Split REQ-016 into a DEFINED core record for the solar input window and maximum input power of E's LT8705A stage,
   and a deferred ADVISORY record for M1's energy balance waiting on L-02. Integrator with board E's author; about 1 h.
4. Decide ASM-002 and S-36 per common mode (mitigate in round 8 where it is a schematic change, else a named
   exception with its reason) and carry the exceptions into REQ-004, ASM-001 and every public NEED-03 statement.
   Integrator with boards A, B, C authors; after round 8 for any mitigation; about 4 h.
5. Resolve CFL-010: one SIM description in V2-SPEC and the generator, the SIM TVS array (at most 10 pF) fitted; read
   CFL-010 on the committed B netlist. Board B author and integrator; after the r8b merge (`candidates/r8b.patch`); about 2 h.
6. Make the resolved conflicts true on their sources: the pack files to the 4S3P INR18650-35E, about 145 Wh (CFL-006,
   S-27); `_product` citing OPERATING-ENVELOPE (CFL-003); TEST-PLAN's closed-lid state and test (CFL-009) and each
   test's purpose (CFL-007); re-read the CFLs on bound files, following the integration recipe (commit config inputs
   before `rules_status`; re-take affected readings with an output directory). Battery stream and integrator; about
   3 h plus re-takes on a KiCad host.
7. Revise TEST-PLAN: E5 sealed, E3 and E4 per SC-09, the current board set, and on every row (E1 to E10, M1 to M7,
   sections 4 and 5) the requirement ids it verifies and its purpose (acceptance, qualification margin,
   characterisation); take REQ-050's desk reading. Test-plan owner and integrator; about 4 h.
8. Add the missing requirements: NEED-02 bearer failover behaviour; carriage temperature with the pack fitted; REQ-025
   aligned with CONOPS storage and the storage charge set; S-20's charge current on a record; S-19's ZEROIZE
   indication into REQ-035 with S-39 and CON-021 reconciled. Integrator; CONOPS re-pin in the same commit; about 4 h.
9. Settle or move out the hardware-affecting deferred TBDs (CON-011, REQ-042, REQ-061 with GND-002 ruled as a decision
   and GROUNDING-AND-SHIELDS.md corrected, REQ-058, REQ-043, REQ-040, REQ-041, REQ-034, REQ-011, REQ-023, CON-015).
   Where the TBD is a design choice, the requirement keeps its need-level limit and the choice goes to a decision
   record. Integrator with the board, parts and case streams; about 1 day.
10. Settle or retype the software, procedure and characterisation TBDs (REQ-010, REQ-033, REQ-052 and CFL-011 with one
    reduced-mode definition, REQ-063 MIL-STD-461 edition, REQ-028 as "no service-life requirement for prototype 1",
    CON-013 as characterisation, REQ-024 and CON-012's "+35 C", REQ-069 from the ADR). About 4 h.
11. Fix REQ-048's stage. 15 min.
12. Give the 27 unnamed rules parent records (PI-001, PI-003 to REQ-045; GND-001 to REQ-061 and REQ-029; IMP, PAIR,
    RET, STK to CON-003 and FEA-003's link records; one kit-level requirement that each board implements its reviewed
    netlist and is fabricable at its declared fabricator and stack for the rest). About 2 h.
13. Re-anchor every file:line citation to the snapshot commit and set `sources_read_at` to it. After actions 1 to 12;
    about 3 h.
14. Hold Review B (fresh checker, AI review) over the records, the TEST-PLAN trace and the trace page; answer the
    findings; set `baseline_state` to a baselined value naming the commit; update the line below; the snapshot carries
    `out/rule-audit/*.json` or says how to regenerate it. After actions 1 to 13; about 3 h.

**Per board.** A: ASM-002 converters, REQ-018 and FEA-004 (pack-path copper at 18 A), the outlets' minimum contract,
CON-015 (third 5G site), REQ-061. B: CFL-010, CON-011, ASM-002 (KSZ9897R, kit I2C), REQ-004, REQ-058; SC-02's
exceptions to disclose. C: S-39 against CON-021, S-19, REQ-034, REQ-033, ASM-002 (J_PANEL ribbon). D: REQ-018 and
REQ-059 for the PA thermal path; REQ-058. E: REQ-016 window, REQ-042 path and thresholds, REQ-061 stud, CON-015 clamp,
REQ-040, REQ-041. P: REQ-042 shutdown input, the pack documents still at 200 Wh, S-20, REQ-025, REQ-018 floor,
REQ-069. E5: no layer 3 item of its own.

> **INTEGRATOR LINE, layer 3:** status at `e3aedb25` IN_PROGRESS; status now: **COMPLETE in the commit that files `v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md`** (the re-check, at the end of this line; its package the next snapshot, H3); as of commit: branch `fnd/r8int4` (set 4 after H1.1; commits `e5fde2ed` the re-take driver, `95e078a1` and `53292f81` layers 2 and 3, `0da2778b` layer 5, `c351115d` layer 7); items closed since `e3aedb25`: S-43 (closed on `dd39fb15`); S-46 (BAT-F20, EQ-15) and S-47 (HC9-E1) opened; from the merged closers hc1, hc9 and hc6 as at H1. **Since H1.1:** the closer hc3's registry change through its apply script (`95e078a1`, 404 changes, `records/hc3/apply_registry.py`): REQ-072 to REQ-077 (REQ-077 the hot stop), CON-023 to CON-025 (CON-025 the SIM TVS array, PASS on round 8's U222 and U223), CFL-018, S-48 to S-58, SC-17 to SC-50; REQ-041's mast-down alarm, REQ-034's NVIS target (MIL-STD-3009 Type I, Class B), REQ-016's 25 V solar window, M1's September design day, CFL-010 resolved (ADVISORY), CON-012 separating the owner's acceptance from the session's choices; the citations re-anchored from `eadbe571` to `95e078a1` (`53292f81`: 87 carried, 20 of them read by hand at integration, `records/r8int4/citations-reread-r8int4.md`); Review B layer 3 record filed (`v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md`, AI review), its findings B1 to B6 answered by c23 and CLOSED by the fresh verifier (AI); REQ-024 and FEA-004's notes restated on REQ-077; the layer 5 records CON-020 at 0x34 to 0x36, S-59 to S-62 and CON-026 (`0da2778b`); the layer 7 records REQ-047 (6-32), CON-006, L-07, FEA-007, REQ-019 without its fabrication-release fallback and S-63 (`c351115d`); `rules_lib.py requirements` 144 records, 0 errors, 0 warnings. **Release check (27 September 2026):** a fresh reviewer (AI review) judged layer 3 at `f2b7fa66` (`v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2026-09-27.md`, filed in `6209ec7e`). It is Review B's re-check on the merged registry, which this line listed as remaining item (1): Review B's B1 to B6 are CLOSED in substance on the merged files. No record of the c23 verifier exists in the tree (its CLOSED lives only in the session's workflow journal), so this record stands in for it. Its verdict is NOT COMPLETE on five blocking findings. Applied once, the citation and wording parts: R3 in the commit that carries this line (the registry's citations re-anchored from `95e078a1` to `08f3665a`: ten moved, three read by hand, five that name their own commit left; `records/r8int4/citations-reread-release.md`; START-HERE section 9 says a registry citation is at the commit `sources_read_at` names); R1's filing (the record committed, and the verifier's absence stated here). **Status now: IN_PROGRESS**; `baseline_state` stays READY_FOR_REVIEW_B and S-51 open. Remaining: (1) R1: a fresh reviewer confirms R2 to R5 answered on one commit, then `baseline_state` names that commit and S-51 closes; (2) R2, not wording: state once which governs M1's duration, SC-21 under the owner's standing rule of 26 September 2026 or D-06's reservation, and make the registry header's L-02 sentence, L-02 and EQ-13 agree with it; rewrite EQ-13 as the M1 question (REQ-072 FAIL at desk on D-06's one pack whatever the solar rating; the decisions D-06, D-01, SC-21, REQ-016 and REQ-072; boards A, E and P and the pack pocket; the four routes and who may take each; decided before A, E and P enter layout); the owner's half of S-53 as an owner action; and a statement, in REQ-016 or a conflict record, that REQ-016's window and REQ-072 cannot both hold on D-06's architecture; (3) R3's last step, `08f3665a` on the public repository once the integrating session pushes the branch; (4) R4, layer 2's B2 (REQ-077's forced-trigger step); (5) R5: SC-HF-01 to 06 entered as SC-58 to SC-63 and the validator refusing an SC id no entry defines (code, not wording); (6) the release review's minors m1 to m10 and its section 6 notes (the hot stop's firmware rows in no contract, for layer 5; the 43 PROTOTYPE_MEASUREMENT records no TEST-PLAN row names, 25 of them core BLOCKERs, for the TEST-PLAN owner; E5's INT-001 binding); (7) from the earlier list, REQ-077 FAIL until HOT-R1 (S-57) and GND-002 unruled (layer 4, `records/hc3/blocked-questions-layer-3.md` item 6). Owner: the integrator as registry writer. **Second release attempt (27 September 2026, `fnd/rel2`, the commit that carries this sentence; `records/rel2/apply_registry.py`, by record id with asserted old text and next-free numbering):** R2 answered: SC-21 governs M1's duration under the owner's standing rule of 26 September 2026, recorded as the session's and replaced by the owner's own setting; the registry header's L-02 sentence, L-02 and SC-21 say so, and ENGINEERING-QUESTIONS EQ-13 states what the session took and what the owner may reverse or decide, no longer an open owner question; the owner's part of M1's failing balance is the owner action M-02 (the second pack, a larger pack, or accepting the residual; REQ-072 waits on it), S-53 keeps the session's part (the input path's rating), and REQ-016 and REQ-072 record that they cannot both hold on D-06's architecture; REQ-072's FAIL at desk is carried as it stands. R4 answered with layer 2's B2 (REQ-077's forced trigger P15 and E3-H's stepped run). R5 answered: SC-HF-01 to SC-HF-06 are SC-58 to SC-63, each with question, taken, why with its "Reverse by", and `drafted_as`; HW-FW-CONTRACT.md section 8 and S-59 and S-61 name them; `rules_lib.py requirements` refuses any SC- id cited in the registry or a page of `v2/docs/` or `v2/docs/handover/` that no entry defines by id or `drafted_as`, with fixtures both ways in `tests/test_requirements.py`; the rules_lib.py change moved two writers' code bundles, answered by two `kind: tool` entries in `v2/docs/evidence/COMPATIBILITY.md` (`records/rel2/tool_compat.py`). Layer 1's m1 (SC-13) is also in the registry. **Status now: IN_PROGRESS**; `baseline_state` stays READY_FOR_REVIEW_B and S-51 open. Remaining, replacing the list above: (1) R1: a fresh reviewer confirms R2 to R5 on one commit, then `baseline_state` names that commit and S-51 closes; (2) R3's last step, the anchor commit on the public repository once the integrating session pushes; (3) the release review's minors m1 to m10 and its section 6 notes (the 43 PROTOTYPE_MEASUREMENT records no TEST-PLAN row names, 25 of them core BLOCKERs; E5's INT-001 binding; the hot stop's firmware rows are now FW-C13, FW-C14 and FW-E10, while IF-AE-DOCK names pin 12 only when HOT-R1 lands, S-57); (4) REQ-077 FAIL until HOT-R1 (S-57), and GND-002 unruled (layer 4). Owner: the integrator as registry writer. **Second release check (27 September 2026):** a fresh reviewer (AI review) judged layer 3 at `eb9f9030` (`v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md`, filed byte for byte in the commit that carries this sentence): R2 to R5 of the first release check are ANSWERED (R3 on `08f3665a`, which is on the public main), the record is the fresh confirmation R1 asks for, the figures it checked match their sources, and nothing was lowered, dropped, weakened or narrowed. Its verdict is NOT COMPLETE on two procedural items: B-1 (item 3.14: `baseline_state` still READY_FOR_REVIEW_B and S-51 open) and B-2 (item 3.18: no versioned package). This was the second attempt, so the release finalizer applied neither (the owner's section 4). Since the review the branch was rebased onto main `391d8579` and then `91894cd7`, which adds set 5's and the consolidated re-take's registry changes and renumbers the reviewed SC-51 to SC-56 as SC-58 to SC-63 (EQ-25 as EQ-26), so the registry at the branch head is no longer the one the reviewer read (sha256/16 `fb819e939f2895da`), and the record says a registry change beyond its B-1 fix needs a review of its own. B-1 is open item S-78 and ENGINEERING-QUESTIONS EQ-28 (a confirmation limited to that difference, then the one baseline commit the record describes); B-2 is S-79 and EQ-29 (the push and the snapshot, the integrating session's). **Status now: IN_PROGRESS**; `baseline_state` stays READY_FOR_REVIEW_B and S-51 open. Remaining, replacing the list above: (1) S-78 and EQ-28; (2) S-79 and EQ-29 (the earlier item on the anchor commit being public is met, the record's n5); (3) the record's minors n1 to n9 (n1, the three gen_sch_b.py pointers, goes into the baseline commit) and the first check's m1 to m10, with both records' section 6 notes; (4) REQ-077 FAIL until HOT-R1 (S-57), and GND-002 unruled (layer 4). Owner: the integrator as registry writer. **Targeted fix and baseline (27 September 2026, branch `fnd/h2` from `62f26a44`):** B-1 answered in two commits. `cecfd0f1` states in the registry header that SC-51 to SC-56 of the reviewed `eb9f9030` are SC-58 to SC-63 here and EQ-25 is EQ-26, renumbered by the rebase because set 5 had taken those ids, with the rest of the difference (set 5's entries, the consolidated re-take's re-read notes, the finalizer's S-77 to S-79 and CONOPS rebinds), and marks n1's three `gen_sch_b.py` pointers in SC-58 and SC-63 "(as read at e3aedb25)"; `v2/docs/records/h2/registry_difference.py` computes that difference entry by entry (`registry_difference.out`: the six renumbered choices identical to the reviewed ones; no record's statement, acceptance, applicability, allocation, verification or release effect changed). The commit that carries this sentence sets `baseline_state` to BASELINED at `cecfd0f1` with `baseline_reviews` naming Review B's records (`REVIEW-B-LAYER-3-2026-09-27.md`, `REVIEW-LAYER-3-RELEASE-2026-09-27.md`, `REVIEW-LAYER-3-RELEASE-2-2026-09-27.md`, by sha256/16), closes S-51 by `cecfd0f1` on them and S-78 (EQ-28), and re-renders `REQUIREMENTS-TRACE.md` (acceptance item 3.14). The confirmation of the difference is the narrow verification of this fix (the owner's section 4); if it finds a difference the header does not state, `baseline_state` returns to READY_FOR_REVIEW_B and S-51 and S-78 reopen. **B-2, the package (item 3.18), is answered by the H2 snapshot this workflow builds next** from the pushed commit that carries the baseline; S-79 stays open until it is cut (EQ-29). **Status now: IN_PROGRESS** until the narrow verification confirms the baseline and H2 is cut. Remaining, replacing the list above: (1) the narrow verification; (2) H2 (S-79); (3) the record's minors n2 to n9 and the first check's m1 to m10, with both records' section 6 notes; (4) REQ-077 FAIL until HOT-R1 (S-57), and GND-002 unruled (layer 4). Owner: the integrator as registry writer. **Narrow verification (27 September 2026, branch `fnd/h2`):** a session that wrote none of the lines, took no part in the fix and held neither release check verified B-1 at `3e4799eb` (`v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`, "AI check (not a qualified engineering review)", sha256/16 `ae70b1a7811ecea1`, filed byte for byte in the commit that carries this sentence): **B-1 NOT_CLOSED.** Five of its six conditions PASS: `baseline_state` named a commit on `fnd/h2` and `baseline_reviews` the three records, whose hashes match; S-51 was closed by commit with evidence; the renumbering (SC-51 to SC-56 as SC-58 to SC-63, EQ-25 as EQ-26) is mechanical and complete, every reviewed entry landing identical under the map and every live-page citation following it, with n1's pointers holding at `e3aedb25`; set 5's entries, the re-take's move of CON-010 to FAIL, the finalizer's S-77 to S-79 and the baseline commit's own changes are typed correctly, and no record's kind, statement, acceptance, applicability, allocation, verification or release effect differs from the reviewed file; the validator gives 0 errors and the trace page is current. The sixth fails on one difference the registry header did not state: when the reviewed attempt landed at `79963b3b` (the rebased `eb9f9030`), its own CURRENT-EVIDENCE re-read on CON-010 and REQ-044 (bound `@6351a72c7966c4b9`) was replaced by a rebase note bound `@7a834fe55aea6ccd`, and on CON-010 that note, the record's newest evidence entry, ends "it stays INCONCLUSIVE" while the re-take's entry moved the reading to FAIL and `evidence_result` and `history` read FAIL (`REQUIREMENTS-TRACE.md` shows both under CON-010), so S-78's closing claim was not accurate. **Applied in the commit that carries this sentence, and nothing more** (`v2/docs/records/h2/apply_verification.py`, every edit asserting the text it replaces): the registry's own reversal, `baseline_state` READY_FOR_REVIEW_B with S-51 and S-78 reopened (`baseline_reviews` kept as the records the re-baseline names); the finding as open item S-80 and ENGINEERING-QUESTIONS EQ-30, with EQ-28 reopened; S-79's last sentence restated (the H2 snapshot carries layer 3 IN_PROGRESS, EQ-29 option (b)); a registry header paragraph saying so; `REQUIREMENTS-TRACE.md` re-rendered. The wording fix itself (CON-010's newest entry ending FAIL on W3T-F1, the header naming `79963b3b`'s re-take) is not applied in this pass (the owner's execution prompt, section 4: no unbounded author and check loop). **Status now: IN_PROGRESS.** Remaining, replacing the list above: (1) S-80 and EQ-30: the wording fix of the record's section 3, the trace page re-rendered, a re-check of those two edits by a reviewer who wrote neither, at one pinned commit, and the re-baseline (S-51, S-78) in the commit that files it; (2) S-79 and EQ-29, the package from the pushed commit that carries the re-baseline; (3) the release-2 record's minors n2 to n9 and the first check's m1 to m10, with both records' section 6 notes; (4) REQ-077 FAIL until HOT-R1 (S-57), and GND-002 unruled (layer 4); (5) the verifier's observations for the registry writer: `registry_difference.out` was taken at `cecfd0f1`, and `registry_difference.py` sees no YAML comments, asserts nothing on open items or session choices and attributes no causes, which is how this difference passed it, so the re-check reads the chain of commits and not the script's output alone; and none of S-64 to S-80 is in any record's `waits_on` (S-64 decides CON-010's verdict and is carried only in its evidence text, the release-2 reviewer's n7). Owner: the integrator as registry writer. **H2 (27 September 2026):** IN_PROGRESS, carried into the H2 snapshot as `baseline_state` READY_FOR_REVIEW_B (EQ-29 option (b)); S-79 stays open, since it closes only with a snapshot cut from the pushed commit that carries the re-baseline. Nothing was applied to the registry for H2. What remains is the H2 section's row for layer 3, first S-80 and EQ-30. Owner: the integrator as registry writer. **Re-baseline (27 September 2026, branch `fnd/l3rb` from main `ef144760`):** S-80's fix exactly as the narrow verification's section 3 gives it, in `a54b793b` (`v2/docs/records/l3rb/apply_fix.py`, asserted anchors): CON-010's newest evidence entry ends with the record's actual state, FAIL on W3T-F1 (S-64, EQ-25), on the file at `7a834fe55aea6ccd`; the header's paragraph on the targeted fix names `79963b3b`'s re-take of the reviewed attempt's own CURRENT-EVIDENCE re-read on CON-010 and REQ-044; the trace page re-rendered; the verification's observation (c) recorded as S-81 for layer 1's writer. Then `2c12be91` (`apply_baseline.py`): `baseline_state` BASELINED at `a54b793b`, `baseline_reviews` naming Review B's three records and the narrow verification, S-51, S-78 and S-80 closed by commit `a54b793b`; `rebaseline_difference.py` compares the registry entry by entry, comment lines and open items included, at `3e4799eb`, `ef144760`, `a54b793b` and `2c12be91` (ALL ASSERTIONS HOLD). S-80's fourth step, the re-check, was not held before that baseline: the session's choice under the owner's standing rule of 26 September 2026, with a reversal clause in the registry header. **Re-check (27 September 2026):** one session that wrote neither edit, took no part in the fix or the baseline and held no earlier check re-checked them at `2c12be91` (`v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md`, "AI check (not a qualified engineering review)", sha256/16 `7831358b96b6f5ca` as filed in the commit that carries this sentence, with one phrase rewritten: the trailer's name in its last observation, which the repository's pre-commit check refuses on any added line; the checker's own file had `ab9b3ec1e590a41a`, both in `v2/docs/records/README.md`): **B-1 CLOSED.** Remedy (1), CON-010's newest entry reads FAIL in agreement with its `evidence_result`, its `history` and the re-take's entries: PASS. Remedy (2), the header names `79963b3b`'s re-take with both bindings: PASS. Remedy (3), the trace page re-rendered and current at both commits: PASS. The baseline and `baseline_reviews`, four hashes matching: PASS. S-51, S-78 and S-80 closed with evidence: PASS. Its own entry-by-entry comparison finds no registry difference from `ef144760` beyond the stated ones and no protected field changed from `3e4799eb`: PASS. So the reversal clause is not triggered. **Applied in the commit that carries this sentence** (`v2/docs/records/l3rb/apply_recheck.py`, asserted anchors and an asserted entry-by-entry difference; `edit_docs.py` for the pages): the record added to `baseline_reviews`; a registry header paragraph on the re-check; one sentence appended to the closing evidence of S-51, S-78 and S-80, since the re-check's observation found that they, the header and the comment above `baseline_reviews` said no re-check was held; one sentence appended to S-79's title; `REQUIREMENTS-TRACE.md` re-rendered; ENGINEERING-QUESTIONS EQ-28 and EQ-30 answered and EQ-29 given its layer 3 package. Nothing else in the registry moved: these are notes, closed items' evidence and an open item, which the header lets move without a review of the baseline. **Status now: COMPLETE** for the layer's own engineering purpose, on the review records (Review B and the two release checks) and the two targeted checks (the narrow verification and this re-check), each an AI review or check and none a qualified review (none is required for layer 3, SC-46). This is a record closure and closes no electrical defect. Its versioned package, acceptance item 3.18, is the next snapshot, H3, cut from the pushed commit that carries this line; S-79 and EQ-29 close with it. Remaining, carried and not holding the layer: (1) H3 (S-79, EQ-29), the integrating session's, which also restates START-HERE's and CONTINUATION-BRIEF's layer 3 lines, written at H2; (2) the release-2 record's minors n2 to n9 and the first check's m1 to m10, with both records' section 6 notes; (3) REQ-077 FAIL until HOT-R1 (S-57), and GND-002 unruled (layer 4); (4) S-81, for layer 1's writer; (5) the fixer's list for other writers, as the re-check's section 5 names it: `feasibility/EMCON.md` sections 3 and 7 against section 4b, not judged here. The layer reopens if a record's statement, acceptance, applicability, allocation, verification or release effect changes. Owner: the integrator as registry writer.

### A.4 Layer 4. System architecture (the audit at `e3aedb25` and the edition history)

**Status at `e3aedb25`: IN_PROGRESS.** The architecture page, five feasibility pages, board B's feasibility page and
the battery packet exist, cite their sources and state their limits. The layer is not COMPLETE: none of the six
design-critical feasibility questions is closed, and the thermal, EMCON, board B and battery bounds all include
failure; no review of the architecture is recorded (Review C not held), and the physical diagrams predate the current
case and pack rulings; the budgets either have no requirement value to hold a margin against (runtime, mass, cost) or
have bounds that include failure (thermal, dock contacts, +5V_S1); and several records contradict each other. Much of
the closing work can be done now (round 8 circuits, desk remedies, registry and page fixes, capped box experiments).
Four sub-items need an outside step: the ZEROIZE bench parts (L-06), the empty-case heat test (a purchase), R-BAT
engagement (L-03), and the R-HSD and R-PWR approvals (L-04, L-05).

**Scope.** The single system view of the V2 kit and the evidence that its prototype-1 core is feasible at this stage:
functional and physical diagrams; power, data and control paths across A, B, C, D, E, E5 and P; mode behaviour;
budgets with margins (energy and runtime, thermal, lanes, rails, mass, dimensions, cost); trade decisions; and the six
feasibility blockers of `pcb_requirements.yaml` and ARCHITECTURE.md section 14: FEA-001 ZEROIZE (line 4586), FEA-002
EMCON (4097), FEA-003 failover fabric and board B escape (1652), FEA-004 power and thermal (2397), FEA-005 battery
protection (4958), FEA-006 decoupling (1756).

**Prerequisites.** Layers 1 to 3; OPERATING-ENVELOPE and `pcb_envelope.yaml`; the committed netlists at `e3aedb25`
(sha256/16: A 7b08510106687b3d, B 669d02d07aeaae4b, C 2834f0d8c4071d56, D f13d8b70099ab03e, E d910e49c5f5f50b2, P
4342c4cbe1b43dc4); the case basis CASE-MARGINS.md (D-08 reversed, D-08a).

**Deliverables**

| File | Revision (commit, sha256/16) | Current | Note |
|---|---|---|---|
| `v2/docs/ARCHITECTURE.md` | `4cd20d54`, cdb009f522d14a6b | no | anchored to the `eadbe571` netlists; line 1314 says Q-B-ESC-1 has not run, against its own 14.1; line 1115 says no SMBus lead check exists, against `check_contracts.py` lines 486 to 534; 14.2's evidence columns predate CURRENT-EVIDENCE; its review is not labelled AI review |
| `v2/docs/feasibility/ZEROIZE.md` | `428c697c`, e7a7b9d05a0560ed | no | desk content current; rule Z-C3 keeps the supervisors at 0x30 to 0x32 (lines 192, 660); line 566 "pending merge" |
| `v2/docs/feasibility/EMCON.md` | `a6f87e9d`, e57a54d1767bcd59 | yes | sixth revision; local 14 of 17 transmitters closed at desk, end to end 0 of 17; the RockBLOCK row reopened (4.4); line 1469 cites a patch not in the tree |
| `v2/docs/feasibility/FAILOVER-FABRIC.md` | `428c697c`, 4646ad528ec4b3c6 | no | lane, pin and clock map 202 of 202 rows OK; sections 1, 8.1, 8.2 and 10 stale (the netlist is on main since `458b2873`; Q-B-ESC-1 ran at `4cd20d54`) |
| `v2/docs/feasibility/POWER-THERMAL.md` | `428c697c`, bb9c861c9920c8d6 | yes | PROVISIONAL, anchored at `01469100`; its hand-offs in section 11 mostly not executed |
| `v2/docs/feasibility/DECOUPLING.md` | `428c697c`, 15915adb18843695 | yes | decision 42 ruled per capacitor class; "Nothing is laid for this ruling yet" |
| `v2/docs/B-FEASIBILITY.md` | `4cd20d54`, d67a27812b620b0c | yes | escape diagnosis, options A1 to A8, Q-B-ESC-1 result (7.8, EXPERIMENTAL, INCONCLUSIVE), Q-B-ESC-2 specification (7.9) |
| `v2/ecad/tools/routeflow/experiments/b_esc1/results/2026-09-26/` | `4cd20d54` | yes | Q-B-ESC-1's filed results with sha256; the final boards and sessions stayed on the build host |
| `v2/docs/ARCH-PCB-B-IOHA.md` | `7808734f`, 6c3c93b7f32f953a | no | sections 6 (lines 97, 101) and 10a (lines 166 to 175) still describe the STM32H753 on PB1/PB2 |
| `v2/docs/review-packets/battery/` (MANIFEST.md `428c697c` f0c6d05a0c5bdfe7; REVIEW-REQUEST.md `d90f30e4` e36ebfd98c2ead3a; PROTECTION-ARCHITECTURE, SECONDARY-OT-DECISION, CHARGER-STATE-SEQUENCE, FUSE-INTERPRETATION, PRIMARY-CONFIGURATION, README at `d90f30e4`) | `d90f30e4` / `428c697c` | no | `check_manifest.py` RELEASE CHECK PASS (132 rows) on an export of `e3aedb25`; candidate netlist equals main's P; but CHARGER-STATE-SEQUENCE and MANIFEST line 18 read board A's charger at `1f614233` plus an uncommitted candidate, and the manifest does not bind `gen_sch_a.py`; secondary over-temperature coordination against 60 C open |
| `v2/ecad/tools/pcb_requirements.yaml` | `a6f87e9d`, acd19f7bfc50b7ad | yes | FEA-001 to FEA-006 with three stages each; internal contradictions (CON-020 line 4424 and S-41 line 887 keep 0x30 to 0x32; FEA-003's text names Q-B-ESC-1 "on the corrected inputs"; FEA-001's notes say two filed scripts are not filed) |
| `v2/docs/feasibility/fab/` (`fabmap.py` 5b2bb0cfce37f5e5, `voters.py` 8d8f5d855219647c, `pulldowns.py`, `lengths.py`, `out/`) | `7808734f` | yes | read-only scripts behind the fabric map |
| `v2/docs/records/rv-pwr/` (`pwr_budget.py` 469d0820b046ef6f, `pwr-chain-redeclaration.yaml` 039c72aa6f451dbd, `pwr-part-temps-rows.yaml`, `pwr-maker-questions.md`) | `428c697c` | yes | the power and thermal model; the PWR-F12 re-declaration and part-temperature rows exist only as records |
| `v2/docs/records/rv-zer/zeroize/` (`zer_config.py` 3d4271b2b9aec3e0, `zer_budget.py` 8cdad0569ec3d814) | `428c697c` | yes | ZEROIZE slot-map and wipe-budget checkers |
| `v2/ecad/tools/pcb_interfaces.yaml` (`board_to_board`) | `7808734f`, 4a553b9d3c304f63 | yes | data only; no tool reads the section |
| `v2/docs/EXECUTION-PLAN.md` | `e3aedb25`, 73b98e8fddd05b70 | yes | stage gates (lines 100 to 131) |
| `v2/docs/CURRENT-EVIDENCE.md` | `b9600c4a`, 9c9bba12790d645a | yes | generated layout-entry test with the FEA stages per board (lines 79 to 194) |

**Acceptance items**

| # | Item | Met | Evidence |
|---|---|---|---|
| 4.1 | Functional diagrams current, covering power, data and control | no | five mermaid diagrams in ARCHITECTURE (lines 163, 240, 265, 334, 590) and one each in PROTECTION-ARCHITECTURE and CHARGER-STATE-SEQUENCE, topologically valid; no control-line diagram for EMCON_HW, TX_INHIBIT_n, EMCON_ON, ZEROIZE, SLOT_EN and PI_KILL across A, B, C, D; no rendered SVG or PDF |
| 4.2 | Physical diagrams current | no | ARCHITECTURE section 7 is tables only; `v2/cad` last changed `47684b3d` (15 September), before D-06, C1 and C6, D-07; `panel1450.py` still codes face top 101.4 |
| 4.3 | Diagrams and architecture reviewed, AI review labelled | no | no review record; the header cites challengers and adjudications A01 to A11, of which only w2, w4, w6 records are filed; Review C not held; both owner reviews say they did not inspect the tree |
| 4.4 | Power and data paths documented on the committed design | yes | ARCHITECTURE 4.1 to 4.6 and 5.1 to 5.5 cited to generator lines; fabric map 202 of 202 OK; contracts in `pcb_interfaces.yaml` |
| 4.5 | Control paths consistent and complete | no | supervisor I2C addresses conflict (0x34 to 0x36 in ARCHITECTURE lines 130 and 556; 0x30 to 0x32 in PANEL line 157, ZEROIZE lines 192 and 660, CON-020, which collides with the TPS23861 broadcast 0x30); the SLOT_EN hold across a panel reset is in no generator; EMCON shared-line items L1 to L4 and L7 open |
| 4.6 | Mode behaviour defined | no | reduced mode undefined (S-24); the +35 C and +25 C controls are proposed but OPERATING-ENVELOPE line 150 states them as design; all-transmit "not an achievable default without receive protection" (ARCHITECTURE line 991) and the SDR limiter is in no generator |
| 4.7 | Energy and runtime budget with margin | no | 2.5 h and 1.7 h aged, PROVISIONAL, bounds 1.3 to 3.3 h and 0.9 to 2.3 h; "aged" undefined; no runtime value set, so no margin; CONOPS still 3.4 h and 1.8 h |
| 4.8 | Thermal budget with margin | no | conductance bounded at 1.22 to 2.85 W/K, a 2.3 times spread; three typical modules at +20 C put the cells at 45 to 81 C against 60 C; the bound includes failure and nothing is measured; fans have no part number |
| 4.9 | Lane budgets with margin | no | one PCIe Gen2 x1 lane per slot (about 3.2 Gb/s) shared by NVMe and card, below the RM520N-GL peak of 3.3 Gb/s; 12 of 12 USB hub ports used; no USB 3, PCIe or HDMI channel budget; inner pairs solve to 140.5 ohm against 100 on the six-layer stack |
| 4.10 | Rail and interconnect margins | no | PWR-F01 and F03 (B declarations below makers' figures), PWR-F02 (+5V_S1 at 4.65 of 5 A); R17 1.62 W at 18 A on a 3 W part with no sheet; IF-AB-POWER ends disagree (I-03); IF-AE-DOCK 3.08 of 3.5 A per contact with no margin for one open contact; PWR-003 FAIL on B_PANEL_5V |
| 4.11 | Mass, dimension and cost budgets | no | mass: a 7.0 kg floor, total TBD, no limit; dimensions: 35 of 70 case rows OPEN and M17g, M17x fail as assumed; the face Z budget rests on unsourced Xenarc and heatsink heights; cost TBD |
| 4.12 | Trade decisions recorded | no | recorded with reversal conditions: SC-02, BAT-F06, the SLOT_EN pull-up withdrawn, I3-F01, the D-07 reading, decisions 29, 42, 43, SD-EMC-1. Open: board B stackup and escape method, layer counts for A, D, E, E5 (P0 rule), the U8 part, F2 at 18 A, the fans |
| 4.13 | Demonstrated feasibility at this stage | no | all six FEA records FEASIBILITY_OPEN, evidence INCONCLUSIVE, every layout-entry stage OPEN |
| 4.14 | ZEROIZE question resolved | no | documentary feasibility closed, physical demonstration open; U1 and U4 unpublished; U8 choice not made (EQ-06) |
| 4.15 | EMCON question resolved | no | local 14 of 17, end to end 0 of 17; SD-EMC-1 not drawn; RockBLOCK 9704 runs on about 16 J of supercapacitor with ENABLE held by firmware (EQ-02); REQ-071's latency not shown for any row |
| 4.16 | Failover question resolved | no | FAB-01 to FAB-04 open (S-42); Q-B-ESC-1 INCONCLUSIVE; board B has never routed; signal integrity UNVALIDATED; ASM-002's common modes neither accepted nor mitigated (EQ-01) |
| 4.17 | Power and thermal question resolved | no | PWR-F12 (the chain declared at 10 A continuous while every PA key-down makes 18 A a 60 s current; F2 not shown at 18 A), PWR-F15 (no flange sensor), unmeasured conductance (EQ-05, EQ-07) |
| 4.18 | Battery question resolved | no | all reviews AI; R-BAT not engaged (L-03); the secondary trip 62.7 to 77.5 C not coordinated with the 60 C cell limit; F1 before F2 on a hard short (Q-E4) unproven (EQ-10) |
| 4.19 | Review C held | no | defined at EXECUTION-PLAN line 62; no record; ASM-002 and S-36 wait on it |
| 4.20 | No feasibility stage waits for what it gates | no | see the cycles below |
| 4.21 | Qualified review routes named and costed | yes | `v2/docs/reviews/REVIEW-ROUTES.md` and READY-TO-ACT 2.1 to 2.5; none engaged; R-PWR and R-HSD need the owner's spend |
| 4.22 | Sibling records consistent with the architecture | no | stale at `e3aedb25`: IOHA 6 and 10a, ZEROIZE Z-C3, CONOPS runtimes, OPERATING-ENVELOPE's +35 C wording, `pcb_pack_protection.yaml` line 24, `pcb_part_temps.yaml` (no AW7915 or LimeSDR rows), GROUNDING-AND-SHIELDS "nine SMA" |

**Unresolved decisions**

| Decision | Downstream impact | Waits on later evidence |
|---|---|---|
| U8 secure element: ATECC608B-SSHDA-T, or SLB 9673 TPM (or SE050E2HQ1) | B's U8 land (SOIC-8 or UQFN-32), panel firmware, procurement, REQ-035 | yes: Z-EXP-A and B (EQ-06) |
| Board B stackup (JLC06161H-3313 or JLC08161H-2116) and escape method (floor plan A4, via-in-pad A3, re-assigned A2) | B's stack, price (L-01), impedance class, R-HSD scope, possibly outline or partitioning | yes: Q-B-ESC-2 and decision 43's run (EQ-01) |
| Whether board B fits 330 x 200 at all, or needs partitioning or a larger outline (A4, A6; A8 feature cuts excluded by D-01) | layers 4, 5, 7, 8 for B and the case layout | yes (EQ-01) |
| Thermal architecture: reduced mode (S-24), the +35 C and +25 C controls, the fans (D-18), a conduction path to the plate | hot-part placement on A, B, D; pack location; firmware controls C1 to C4; NEED-03 availability at temperature | yes (EQ-05) |
| PWR-F12: re-declare the pack chain (10 A continuous, 18 A for 60 s, 20 A for 2 s) and choose F2 (Eaton SCF9550-30-05 publishes no derating; Littelfuse ITV9550L1430 publishes 25 A at 60 C) | A pack-path copper and R17, P's F2 part and land, D-11 key-down rules | no for the re-declaration; F2's margin is EQ-07 |
| EMCON remedies: SD-EMC-1 with fallback (iii) drawn, L1 to L4 and L7, an EMCON_ON source independent of +3V3_DEV, the SD-EMC-6 lamp on C, RockBLOCK ENABLE forced low by hardware | circuits on A, B, C, D; the face-plate light-guide hole | no (round 8 authors them) |
| RockBLOCK 9704: ENABLE low plus a supply cut, or a module-independent remedy | B circuit; REQ-071's 1 s | yes (EQ-02) |
| SLOT_EN hold across a panel reset: board C or A, and its latch form | IF-BC-PANEL and IF-AB-RIBBON semantics | no |
| PA flange sensor (PWR-F15): part, lead and address on D | D netlist, IF-AD-HARNESS, K2 and C4 | no |
| Battery protection coordination and R-BAT findings (secondary trip against 60 C, Q-E4, BAT-F07 FET SOA, BAT-F12, BAT-F14) | P circuit and possibly its strategy after layout | yes (EQ-10) |
| AW7915-AED and LimeSDR outside -20 C (PWR-F09): carve-out or replacement | envelope carve-outs, parts list, possibly B sockets | no |
| Supervisor kit-bus addresses 0x34 to 0x36 or 0x30 to 0x32 | supervisor firmware, ZEROIZE residual R7, PANEL bus table | no (contradictory records; 0x34 to 0x36 recommended) |
| Layer counts for A, D, E and E5 (P0 rule: a written decision per board with measurement and cost) | stackups for layout entry and price | no |
| Whole-kit common modes (ASM-002, S-36) | NEED-03 claim; A, B, C if mitigated | no |
| RF coexistence under D-11 all-transmit (SDR limiter W4-F12; an antenna isolation budget: the 6th harmonic of 144.8 MHz falls at 868.8 MHz in EU868; the 1 W LoRa sits 62 to 124 mm from the 5G jacks) | B or wall-jack circuit, jack plan, M6 test | no |
| SC-02 (LoRa and 5G data as named NEED-03 exceptions) | reversing it changes board B's floor plan; present as a scope exception | no |
| When R-PWR is timed: before A's layout entry or at fabrication release | A's layout entry; owner spend | no |

**Stage-gate cycles and remedies**
- FEA-003's layout-entry stage (`pcb_requirements.yaml` lines 1680 to 1693) requires `check_pcb_b.py` at 0 FAIL, and
  that script loads a board file (`check_pcb_b.py` line 15), so it waits on a placement. Remedy: move the netlist-level
  assertions (TEST2 strap, pull-downs, back-power, fabric) into a netlist reader, or declare the generator's pre-route
  board an EXPERIMENTAL input, and move the geometry half to fabrication release.
- FEA-003 also requires the escape strategy "from Q-B-ESC-1's reading on the corrected inputs and the stack decision
  43 selects". Q-B-ESC-1 ran on the uncorrected B21; the corrected-input test is Q-B-ESC-2, and decision 43's run is a
  whole-board route with no recorded cap. Remedy: rename the evidence to Q-B-ESC-2; give decision 43's run a recorded
  cap and the EXPERIMENTAL label (legitimate under the owner's section 4).
- FEA-004 stages the empty-case heat test at FABRICATION_RELEASE "before the placement of the hot parts is frozen"
  (lines 2445 to 2455), although placement is frozen inside layout and the bound includes failure; FEA-004 also does
  not hold board B, which carries the three CM5 heat sources. Remedy: make the heat test a gate before hot-part
  placement on A, B and D, and add B to FEA-004's holds.
- FEA-004 stages F2 at 18 A for 60 s at P's fabrication release although a failure changes P's fuse part and possibly
  its land. Remedy: hold P's layout entry on F2's identity.
- FEA-005: R-BAT at fabrication release matches the owner's first review ("before pack PCB release"), not a cycle; but
  its findings can change P's protection after layout, so the battery part of layer 4 cannot close before it.
- FEA-001: no cycle; the development-device test gates only U8, and needs the L-06 purchase.
- FEA-002: no cycle (fallback (iii) in circuit replaces bench E-05 at layout entry), but the RockBLOCK row cannot close
  at desk without the 9704's ENABLE behaviour, and VENDOR_ANSWER is not among the stage's needs. Remedy: a
  module-independent desk remedy, or declare a vendor or development step.
- FEA-006: no cycle (placement reads at fabrication release).

**Next closing actions**
1. Re-anchor ARCHITECTURE.md to the round 8 merge commit: netlist shas, section 3.1, 14.2's evidence columns from
   CURRENT-EVIDENCE, IF-PE-PACK's SMBus lead contract, section 15 (Q-B-ESC-1 ran); label its challenger review as AI
   review. Integrator; after round 8; about 2 h.
2. Resolve the supervisor addresses to 0x34 to 0x36 (I3-F01) in CON-020, S-41, PANEL section 7, ZEROIZE Z-C3 and IOHA
   section 6; re-render the trace. Integrator; none; about 1 h.
3. Bring IOHA 6 and 10a to the H743 on PB6/PB7 and FAILOVER-FABRIC 1, 8.1, 8.2 and 10 to `458b2873` and `4cd20d54`; fix
   the FEA-001 notes and the "pending merge" sentences; rebind the FEA readings. Integrator; none; about 2 h.
4. Restage FEA-003 as in the first two cycles above. Integrator; after r8b's FAB-01 to FAB-04 (`candidates/r8b.patch`); half a day.
5. Restage FEA-004 as in the third and fourth cycles. Integrator; none; about 1 h.
6. Merge PWR-F12 into `pcb_energy_chain.yaml` and `pcb_pack_protection.yaml` (10 A, 18 A for 60 s, 20 A for 2 s, F2 as
   a stage, 4S3P); derive A's pack-path copper constraint at 18 A; choose R17 with its maker sheet. Battery stream and
   board A writer; after r8bat; half a day.
7. Complete round 8's architecture circuits and merge with parity: on B, SD-EMC-1 with fallback (iii), L2, L3, L7, the
   RockBLOCK ENABLE forced low by EMCON hardware, FAB-01 to FAB-04; on C, L1 and the SD-EMC-6 lamp; on D, L4, the
   flange sensor and the TPA6132A2 at 2.2 uF; draw the SLOT_EN hold; update IF-BC-PANEL and IF-AB-RIBBON. Board
   streams and integrator; round 8.
8. Run Q-B-ESC-2 (5 USD cap) and then decision 43's eight-layer whole-board run (capped, EXPERIMENTAL) on the post-round
   8 B netlist; record in B-FEASIBILITY 7.9 and FEA-003. Placement stream and integrator on a build host; after the r8b
   merge (`candidates/r8b.patch`) and the router import fix; about 3 box-hours per run.
9. Channel budgets from primary documents (USB 3.2 Gen 1 from USB-IF; the TUSB8041, TMUXHS4212 and TS3DV642 layout
   guides; PCIe CEM and HDMI where public) against the placement screen's lengths (FB-FAB-7). Half a day.
10. Narrow the thermal bound at desk (a documented lumped model of the Peli 1450 with sensitivity analysis), settle
    D-18, define S-24 against the pessimistic bound, mark +35 C and +25 C as proposed in OPERATING-ENVELOPE, fix CONOPS
    runtimes, add the part-temperature rows and a PWR-F09 decision. Power stream and integrator; 1 day; does not
    replace the measurement.
11. Add an RF coexistence item at desk (isolation budget across the jack plan; the SDR limiter drawn) as a requirement
    or feasibility row. Half a day.
12. Resolve R-PWR's timing in one place and correct REVIEW-ROUTES, L-04 and ARCHITECTURE 14.2 to match. Under 1 h.
13. Hold Review C (fresh checker, AI review) over ARCHITECTURE.md; file its record; record ASM-002's four common modes
    as mitigated or residual with reasons; file or summarise W1, W3, W5, W7 and A01 to A11. After action 1; half a day.
14. Readable diagrams: render the seven mermaid diagrams to SVG or PDF; add a control-line diagram; add a physical plan
    and Z-stack drawing at C1 and C6 with the D-06 pack after the `pack_4s.py` and `panel1450.py` updates. 1 day.
15. Re-bind the battery packet's charger reading to main's `gen_sch_a.py` (add it to MANIFEST's cited documents);
    complete the secondary over-temperature coordination. Battery stream; after r8a; half a day.
16. **Needs authorisation (L-06):** Z-EXP-A and Z-EXP-B on ATECC608B-SSHDA-T (EQ-06). 1 to 2 days bench.
17. **Needs authorisation (purchase):** the empty-case heat-balance test with the PA patch block (EQ-05). About 2 days
    bench.
18. **Needs the owner (money and outside contact):** engage R-BAT; approve or decline R-PWR and R-HSD; send the
    prepared maker questions (Eaton Q-E1 to Q-E5, AsiaRF, Xenarc, Lime, Diodes, Raspberry Pi, and Iridium or Ground
    Control on the 9704's ENABLE). L-03, L-04, L-05.

**Per board.**
- A: held at layout entry by FEA-002 (L2 at R102 and single gates, L4), FEA-004 (PWR-F12 copper at 18 A; R17; PWR-F02)
  and FEA-006 (G1 to G3). R-PWR timing contradictory. Open: D-07 third RF site at X +46; SLOT_EN hold if on A; layer
  count not re-decided; I-03; R4A-N13.
- B: held by FEA-001 (U8), FEA-002 (SD-EMC-1, L2, L3, L7, RockBLOCK row, SD-EMC-2 back-feed), FEA-003 (FAB-01 to
  FAB-04, escape and stack, channel budgets, reference clock) and FEA-006 (G4 to G7, G10). FEA-004 does not name B
  although B holds the dominant heat. PWR-F01, F03, F04; PWR-003 FAIL on B_PANEL_5V; the address contradiction.
  Whole-board feasibility undemonstrated.
- C: held by FEA-002 (L1 GPIO21 buffer; SD-EMC-6 lamp) and FEA-006 (G9, G13, G14); the SLOT_EN hold if on C; six-layer
  regeneration owed (decision 27).
- D: held by FEA-002 (L4), FEA-004 (flange sensor) and FEA-006 (G12, G14: TPA6132A2 at 2.2 uF within 5 mm). The D-04
  VHF band lock is in no generator. The PA case during a 60 s key-down reaches 95 to 118 C on the record's patch
  figure (ARCHITECTURE 8.4).
- E: held only by FEA-006 (G11, G13, G14). Open: the A09 clamp bar and D-07 clamp; VIN_RAW declaration (R4A-N12).
- P: held by FEA-005 (packet current, secondary coordination, charger state sequence) and FEA-006 (G8). F2 at 18 A is
  staged only at P's fabrication release. R-BAT not engaged. Four-layer 2 oz regeneration owed (decision 28).
- E5: no feasibility blocker names it; the D-14 insulating cap not drawn or sourced (S-22).

> **INTEGRATOR LINE, layer 4:** status at `e3aedb25` IN_PROGRESS; status now: IN_PROGRESS; as of commit: H1; items closed since `e3aedb25`: readable diagrams of the context, board interconnect, power tree, power-up, lanes and fabric, control lines, battery states and the case (`v2/docs/diagrams/`, hc4; rebuilt by w3g on the round 8 netlists and at the r8int5 integration on set 5's, drawn at `b7f96784` and committed at `730f8489`: `build.py --check` reads 11 of 11 current, and `power_tree.py`'s attribution check is not complete, measured on every build, as its README says); `ARCHITECTURE.md` 5.5, 6.1, 13.3, 15 and `ARCH-PCB-B-IOHA.md` 6 and 10a reconciled with the STM32H743 compatibility page (hc6); round 8 gated board A's PA and HF rails on both EMCON lines (`c0133147`), powered board D's transmit chain only while its EMCON gates are in range (`76235aad`) and gave board C a hardware EMCON lamp (`9f28c238`); review record: hc4's two AI reviews (filed in H1.1 as `v2/docs/records/handover/hc4-reviews.md`; the second FAILed only on the power-tree claim, fixed at merge). New since `e3aedb25`: BAT-F20 (EQ-15), board A's +3V3 overvoltage window (EQ-17), RF-002's undecided TX_INHIBIT_n line (EQ-18), board B's round 8 residual (EQ-20). Remaining: FEA-001 to FEA-006 as in this section; Review C. **After the release check of layers 1 to 3 (27 September 2026), also here** (the layer 2 release review, B4 (a) and (b)): `feasibility/POWER-THERMAL.md` sections 1 and 9.3 and `ARCHITECTURE.md`'s PS-RED row still take the reduced mode as slot 3 alone, against CONOPS section 4c's slots 2 and 3 (`records/hc2/handoffs.md` sections 4 and 5); `feasibility/EMCON.md` section 5a row 5 still bounds the 5G module by SD-EMC-1's staged timers, which sections 0a and 4b supersede for board B since its round 8 (REQ-071's desk acceptance names the same T_off and T_cut, the registry writer's); REQ-072's night finding (the energy architecture, S-53). **Second release attempt (27 September 2026, `fnd/rel2`):** `feasibility/POWER-THERMAL.md` sections 1, 9.1, 9.2 and 9.3 (and one hand-off line of section 11) and `ARCHITECTURE.md` section 8 now take C1 as CONOPS 4c defines it (the reduced mode of slots 2 and 3, then the heat stage's one module; PS-RED named the one-module stage and PS-RED2 the reduced mode), so that part of the list above is done; `feasibility/EMCON.md` section 5a row 5 and REQ-072's night (S-53, and the owner's part M-02) remain. **H2 (27 September 2026, set 5 and the consolidated re-take):** still IN_PROGRESS. Landed since H1: board B's round 8 (`b76c18cb`: FAB-01 to FAB-04, the per-slot EMCON lines, SD-EMC-1r8's 5G supply removal), board A's EMCON gates behind the eFuse U39 (`ffca0771`, EQ-17 closed at desk with its tOVLO bound, bench E-11), C1 one way in POWER-THERMAL and ARCHITECTURE section 8 (`7dfbfb16`), FEA-007 (`c351115d`), the diagrams on set 5's netlists (`730f8489`); the feasibility set is seven, FEA-001 to FEA-007, all FEASIBILITY_OPEN. Found since: W3T-F1 (S-64, EQ-25). What remains is the H2 section's row for layer 4. Owner: the integrator and the blockers' owners.

### A.5 Layer 5. Partitioning and interfaces (the audit at `e3aedb25` and the edition history)

**Status at `e3aedb25`: IN_PROGRESS.** The partition and twelve board-to-board contracts exist, and their pin maps
agree on the `e3aedb25` netlists (`check_contracts.py` PASS 96 of 96, re-run by the audit outside the tree). The
layer's acceptance is not met. About a dozen board-to-device and board-to-outside interfaces have no contract. Power
capacity is unshown or failing on IF-AB-POWER, IF-AE-DOCK and IF-BC-PANEL. The SLOT_EN hold, the chassis bond, D-07's
third RF site and the monitor's touch USB port are missing decisions or circuits that change interfaces (the touch port
is decided since the layer 5 merge of 27 September 2026: SC-HF-06, board D's spare hub port `J_USB3`, `HW-FW-CONTRACT.md` section 8). Supervisor
addresses contradict across six records, the firmware contract items exist only in drafts, and board B's outline
can still move under FB-FAB-6. Most closing actions are desk and generator work; R-HSD needs the owner's spend.

**Scope.** The responsibilities of the seven boards and every interface owned at both ends: connector and mating
part, pin map, levels, power capacity, sequencing, reset and cable-out default states, communications and addresses,
harness, mechanical mating, grounding and shield termination, and the firmware obligations the hardware relies on
(ARCHITECTURE.md sections 3, 4.3, 5, 6, 10, 12; `pcb_interfaces.yaml` `board_to_board`).

**Prerequisites.** Layer 4 items that can move an interface (FB-FAB-6, EMCON L1 to L4 and L7 with SD-EMC-1 and 2,
FB-ZER-1, PWR-F12, PWR-F15); layer 3 records CON-020, CON-017, ASM-002, REQ-045, REQ-049, REQ-030, REQ-071 and open
items S-12, S-22, S-36, S-40, S-41; layer 6 identities of the interface parts; layer 7 case geometry (CASE-MARGINS C2
to C4, rows M14 and M17); layer 8 netlists.

**Deliverables**

| File | Revision (commit, sha256/16) | Current | Note |
|---|---|---|---|
| `v2/ecad/tools/pcb_interfaces.yaml` | `7808734f`, 4a553b9d3c304f63 | no | read at `eadbe571`; IF-PE-PACK `smbus.judged_by` (line 474) says no check exists; IF-EXT-USB `stale_text` (line 579) describes a row corrected at `9a151c78`; `judged_by` line citations have moved; no tool reads the section (lines 26 to 32), so every line is a contract, not a verdict |
| `v2/ecad/tools/check_contracts.py` | `b4ee78ec`, 304cad5fa2886a73 | yes | PASS 96 of 96 on the `e3aedb25` netlists (scratch re-run); the RF-002 transmitter walk (its section 15a) was not run, because `tx_inhibit.py` is not in the tree; it judges map identity and presence only |
| `v2/ecad/tools/interfaces.py` | `b4ee78ec`, 7b7e4f3a0241cf35 | yes | INT-001 readings on all seven boards AWAITING_REVALIDATION (TOOL_CHANGED) |
| `v2/ecad/tools/block_contract.py` | `07e53438`, b8533c8fde76ee32 | yes | E5 targets generated from A's board file A32, which predates A's corrected netlist; E5's INT-001 is a PASS over 0 checks and UNBOUND; needs pcbnew |
| `v2/docs/ARCHITECTURE.md` | `4cd20d54`, cdb009f522d14a6b | no | anchored at `eadbe571`; section 12's IF-PE-PACK row (line 1115) contradicted by `check_contracts.py` 15c |
| `v2/docs/PANEL.md` | `9a151c78`, b1cde9f7ff1ada7b | no | line 157 supervisors at 0x30 to 0x32; line 79 heartbeat "while its supervisor runs" against ARCHITECTURE line 1009 (CM5 bridge on GPIO16); line 162 names a DS3231M; retired board phases; section 11 defers the wire format to MESHSAT-837 |
| `v2/docs/GROUNDING-AND-SHIELDS.md` | `daca8888`, 8f305cc23551084f | no | "nine SMA bulkhead jacks" (line 15), SMA bodies on plastic (line 39), board changes "wait on" decision 29 (line 73), which is ruled; lacks C4's entry-plate bonds; its four board changes are in no generator |
| `v2/docs/ASSEMBLY.md` | `9a151c78`, e4a0b78616c69779 | no | line 145 RF jumpers (132170 couplers at Z 88, 150 to 250 mm) against C2 and C4 (arrestors at Z 59, 232 to 412 mm); line 146 connector plate 54 x 82 x 3 against C3 (114.0 x 68.3 x 5.0); line 125 monitor touch USB with no board end (D8 `J_USB3` since the layer 5 merge, SC-HF-06) |
| `v2/docs/ARCH-PCB-B-IOHA.md` | `7808734f`, 6c3c93b7f32f953a | no | H753 baseline (line 97), addresses 0x30 to 0x32 (line 99) |
| `v2/docs/feasibility/FAILOVER-FABRIC.md` | `428c697c`, 4646ad528ec4b3c6 | yes | AI desk review; FAB-02 and FAB-04 bear on IF-AB-POWER and IF-BC-PANEL |
| `v2/docs/feasibility/EMCON.md` | `a6f87e9d`, e57a54d1767bcd59 | yes | AI desk review; no row closed end to end |
| `v2/docs/feasibility/ZEROIZE.md` | `428c697c`, e7a7b9d05a0560ed | no | lines 106, 192, 660 keep 0x30 to 0x32 |
| `v2/docs/CASE-MARGINS.md` | `a6f87e9d`, 275a3083db30a7bf | yes | connector plate C3, entry plates C2 and C4, jumper rows M17 |
| `v2/docs/reviews/INT-002-PRE-LAYOUT-ASSESSMENT.md` | `dd3b9074`, cad907b73c7ed8ea | yes | AI desk review of B's three transformerless Ethernet links; the PHY's datasheet is not held; bench half INT-003 at PROTOTYPE |
| `v2/ecad/tools/pcb_requirements.yaml` | `a6f87e9d`, acd19f7bfc50b7ad | no (for this layer) | CON-020 and S-41 at 0x30 to 0x32; no record is allocated to an IF-* contract |
| `v2/ecad/tools/pcb_energy_chain.yaml` | `c161b3d8`, 935e524eed0ee4d1 | no | PWR-F12 owed; PA, HF, PoE and PD branches are not stages |
| the six netlists `v2/ecad/pcb-*/out/*.net` | A `3a1f6576` 7b08510106687b3d; B `3a1f6576` 669d02d07aeaae4b; C `faf8c981` 2834f0d8c4071d56; D `458b2873` f13d8b70099ab03e; E `faf8c981` d910e49c5f5f50b2; P `d90f30e4` 4342c4cbe1b43dc4 | yes | round 8 will change all six |

**Acceptance items**

| # | Item | Met | Evidence |
|---|---|---|---|
| 5.1 | Board responsibilities and partition settled | no | written (ARCHITECTURE 3.1, 3.2), but board B's outline and floor plan are not settled (B has never routed; FB-FAB-6 open; A6 larger outline and A4 floor-plan study live options) |
| 5.2 | Every interface owned at both ends with its connector | no | twelve contracts exist (`pcb_interfaces.yaml` lines 257 to 579); none for external DC and solar, Ethernet with PoE out (54 V), the monitor (power, HDMI, touch USB; IF-MON and seventeen more contracts added at the layer 5 merge, `pcb_interfaces.yaml`), the B-to-A RF pigtails, D's J_ANT to A's J_RF1 (30 W VHF), headsets, camera, E's pod, DCF77, Geiger, lightning, tamper, water and fan leads, A's J_HEAT, P's cell and thermistor leads, B's cooler fans. Board-to-board connectors J_PANEL, J_AB1, J_AB2, J_MEZZ1, J_HARN1 are "IDC 2xN" classes with no MPN or LCSC code |
| 5.3 | Pinouts identical at both ends | yes | `check_contracts.py` PASS 96 of 96 on the `e3aedb25` netlists (scratch re-run). Committed evidence still AWAITING_REVALIDATION; E5 is a PASS over 0 checks; the RF blind-mate row is judged only by `check_pcb_e.py`. Map identity only; it does not establish circuit correctness |
| 5.4 | Electrical levels stated per interface | no | stated only for the EMCON and inhibit lines; no speed, pull-up or capacitance budget for the kit I2C bus across A, B, C, D over the 350, 80 and 60 mm ribbons; the USB 2.0 high-speed wall path has no assessment; back-power into unpowered pins INFERRED only |
| 5.5 | Power capacity of each power interface shown with margin | no | IF-AB-POWER ends disagree (I-03: +5V_S2 A 2.5 A typical against B 4.2 A typical and 5.63 A coincident; +5V_DEV 3.2 A against 3.8 A typical and 6.0 A peak), JST-VH rating unsourced; IF-AE-DOCK 12.31 A over four 3.5 A Preci-Dip 813 contacts (3.08 A each, 4.10 A with one open), board E declares 6.15 A, the round 8 E draft derives 14.10 A (3.53 A per contact, over the rating); IF-BC-PANEL PWR-003 FAIL (F1 2.0 A hold over a 1.23 A track), ribbon rating TBD; pack pins 9 A per Mill-Max pin from a description; SMP-MAX and RG-316 at 30 W on 144 MHz TBD |
| 5.6 | Sequencing across interfaces | no | power-up and boot order written (ARCHITECTURE 4.3, 10.2; PANEL section 5); the SLOT_EN hold across a panel reset is in no generator |
| 5.7 | Reset, default and cable-out states for every control line | no | cable-out states exist for three contracts; EMCON_HW's hold with its source gone UNDECIDED; HDMI_SEL1/2 not a guaranteed low at 100 k (FAB-04); SLOT_EN, ZEROIZE_HW, SHORE_INHIBIT pull states listed as not judged |
| 5.8 | Communications and addressing consistent | no | supervisor addresses 0x34 to 0x36 in ARCHITECTURE line 572 and IF-BC-PANEL, 0x30 to 0x32 in CON-020, S-41, PANEL line 157, IOHA line 99, ZEROIZE lines 106, 192, 660; 0x30 is the TPS23861 broadcast; the panel USB wire format lives outside the repository (MESHSAT-837) |
| 5.9 | Harnesses defined and consistent | no | ASSEMBLY section 4 lists leads, but its RF jumper and connector plate rows contradict C2 to C4; J_AB2's lead length TBD; the touch USB row had no board end (D8 `J_USB3` since the layer 5 merge, SC-HF-06); the east jumper plug unpicked, M17g and M17x fail as assumed |
| 5.10 | Mechanical mating of every interface | no | A's J_AB2 header stands about 3.1 mm into board D (W4-F17); the float-clamp nests overlap at the 14 mm pitch; D-07's third 5G site and its clamp in no generator; blind-mate alignment judged by nothing; E5 generated from A32's board file |
| 5.11 | Firmware obligations affecting hardware explicit | no | ARCHITECTURE section 10 and PANEL summarise, but the itemised contract FW-A01 to FW-A16 that ARCHITECTURE line 397, `records/r4a/r4-decisions.md` and CHARGER-STATE-SEQUENCE cite exists only in worktree drafts; the heartbeat source is stated two ways |
| 5.12 | GND-002: chassis and shield strategy implemented everywhere | no | none of GROUNDING-AND-SHIELDS' four board changes is in a generator; C4's entry-plate bond not carried |
| 5.13 | Interface contracts consistent with the tree | no | `pcb_interfaces.yaml` predates `93138ac1`, `9a151c78` and `3a1f6576` |
| 5.14 | Review C over interfaces owned on both ends | no | no record; challengers and adjudications were AI reviews; R-HSD not commissioned (EQ-12) |
| 5.15 | INT-002 pre-layout assessment of the transformerless links | yes | `v2/docs/reviews/INT-002-PRE-LAYOUT-ASSESSMENT.md`, PASS as a pinned desk review labelled as the session's AI review; INT-003 bench test at PROTOTYPE |

**Unresolved decisions**

| Decision | Downstream impact | Waits on later evidence |
|---|---|---|
| Where the Xenarc 709GNK touchscreen's USB connects, and how it follows the display owner on failover | B hub allocation (all twelve ports used), a new contract, possibly a hub or mux on B; the touch UI that CONOPS Blackout, PANEL section 9 and V2-SPEC line 56 rely on | no; decided at the layer 5 merge as the session's choice (SC-HF-06, board D's spare hub port `J_USB3`, `HW-FW-CONTRACT.md` section 8, no board B change), its costs owed on board D (HF-F06, open item S-61) |
| The SLOT_EN hold across a panel reset: board, part, reset and power-loss behaviour | IF-BC-PANEL and IF-AB-RIBBON, boot order, panel in-system update | no |
| Dock VIN_RAW contact capacity and remedy (more contacts, a hardware limit, or a higher-rated contact), including one open contact and hot-end derating | A's J_DOCK map, E's J_BLK, E5 targets, IF-AE-DOCK, FW-A16 | no |
| IF-AB-POWER current contract per lead (I-03), JST-VH and 16 AWG ratings | lead gauge, connector, A's stage limits, B's +5V_S2 peak | no |
| PANEL_5V protection: F1 value against the conductor and ribbon rating | B's F1, the IDC header and ribbon MPN, PWR-003 on B | no |
| GND-002 implementation (CHASSIS net and strap pad on A, B's common-node capacitor and RJ45 shell to CHASSIS, entry-plate leads to stud F) | A and B circuits, connector and arrestor plates, every cable's EMC | no; decision 29 is ruled |
| D-07's third 5G jack: A's site at X +46 and E's clamp with the clamp bar | A's RF row, E's clamp geometry, IF-AE-RF, the east wall | no |
| Relocation for W4-F17 (J_AB2 under D) | A placement or D's standoffs, IF-AB-WALL | no |
| Kit I2C bus speed, pull-ups and capacitance budget; the 0x34 to 0x36 block propagated | pull-ups on B and C, possibly a buffer or split (ZEROIZE R7), firmware | no |
| Hot-plug rules still "(proposed)" on five contracts | ASSEMBLY procedures, connector choice | no |
| Board B outline and floor plan (FB-FAB-6; A4, A6) | B's connector placements, possibly a repartition | yes (EQ-01) |

**Stage-gate cycles and remedies**
- No circular gate. Misplacement 1: the `board_to_board` contracts are read by no tool, so the computed layout-entry
  test does not see open contract findings (I-03, R4A-N13, W4-F17, the SLOT_EN hold); they gate only through
  ARCHITECTURE 14.2 prose and must be checked by hand at layout entry.
- Misplacement 2: SCH-003 "cross-board contracts" is phase ROUTED_BOARD (`pcb_rules.yaml` line 189) although its
  evidence exists at schematic; INT-001 at SCHEMATIC reads the same check, so the pin-map half is not deferred.
- Sequencing, not a cycle: E5's INT-001 can bind only while A's layout carries A's netlist, so E5 enters layout after
  A's placement (E5 is generated from A's board file).
- The case mock-up was recommended before outlines freeze and carried to fabrication release if not run; since the
  layer 7 merge its board-moving checks are required before the layout entry of boards A, B, E and P, which is BLOCKED on the purchase since 27 September 2026 (FEA-007, L-07; `v2/docs/CASE-FIT-UNCERTAINTIES.md` sections 1, 2 and 7). M17g and M17x
  fail as assumed, so the jumper plug must be picked at desk before A and E layout entry.

**Next closing actions**
1. Re-anchor `pcb_interfaces.yaml` `board_to_board` and ARCHITECTURE section 12 after round 8 (netlist shas, `judged_by`
   lines, IF-PE-PACK's check, stale text removed). Integrator; after round 8.
2. Write contracts for the uncovered interfaces (IF-EXT-DC, IF-EXT-ETH, IF-MON, IF-BA-RF, IF-DA-VHF, headsets, camera,
   E's sensor, pod, tamper, water and fan leads, A's J_HEAT, P's cell and thermistor leads, B's cooler fans), each with
   ends, parts, pins, levels, current, hot-plug and judge. Interfaces stream, integrator; after round 8.
3. Rule and draw the monitor touch USB path (port reallocation or added capacity on B, its failover behaviour with
   HDMI_SEL); record as a SESSION decision. Board B author; after r8b (`candidates/r8b.patch`) and before Q-B-ESC-2 fixes B's netlist.
   **Ruled at the layer 5 merge** (SC-HF-06, board D's spare hub port `J_USB3`, `HW-FW-CONTRACT.md` section 8): no port reallocation on B, the HAL shares the touch to the display owner
   (FW-B19); board D's current limit on `J_USB3` and its budget line remain (HF-F06, S-61), before D's layout entry.
4. Design and draw the SLOT_EN hold on C or A with its power-loss and ZEROIZE interplay; update IF-BC-PANEL,
   IF-AB-RIBBON, PANEL section 5, ARCHITECTURE 4.3. Board C (or A) author; after r8c or r8a.
5. Propagate 0x34 to 0x36 (CON-020, S-41, PANEL 7, IOHA 6 and 10a, ZEROIZE Z-C3); state the kit I2C speed, pull-ups
   and capacitance budget. Integrator and ZEROIZE page writer; none.
6. Re-declare VIN_RAW on A and E from the r8e derivation after review; decide the dock contact remedy including one
   open contact and derating; update IF-AE-DOCK, E5 targets and FW-A16. Boards A and E authors; after r8e.
7. Close I-03 and the PANEL_5V coordination with held ratings: file the JST-VH catalogue and an IDC header and ribbon
   datasheet, pick MPNs, reconcile both ends. Boards A and B authors, parts stream; after r8b (`candidates/r8b.patch`).
8. Implement GND-002 in A and B; rewrite GROUNDING-AND-SHIELDS.md to the arrestor plates and decision 29 as ruled.
   Boards A and B authors, integrator; after round 8.
9. Draw D-07's third site on A (X +46) and E's clamp with the clamp bar (R4E-07); pick the east jumper plug so M17g and
   M17x are MET or a lever is taken. Boards A and E, case stream; after the r8e clamp-bar patch.
10. Turn the "(proposed)" hot-plug rules into SESSION decisions; fix ASSEMBLY lines 125, 145, 146. Integrator; after
    actions 3 and 9.
11. File the hardware and firmware contract (FW-A01 to FW-A16, from the W5 and r4a drafts) as one versioned page;
    resolve the heartbeat source. Records stream, integrator; none.
12. Re-take INT-001 on the committed netlists after round 8 on a KiCad host; write a Review C record over the
    contracts, labelled AI review. Integrator and a fresh reviewer; after actions 1 to 11.

**Per board.**
- A: A end of IF-AB-RIBBON, IF-AB-WALL, IF-AB-POWER, IF-AD-HARNESS, IF-AE-DOCK, IF-AC-MAINSW, IF-AE-RF, IF-A-PA,
  IF-LID-HF, IF-EXT-USB. Open: I-03, R4A-N13 (r8e draft: 3.53 A per contact), W4-F17, the site at X +46, GND-002,
  EMCON L2 (R102), J_MON and J_HEAT without contracts, the SLOT_EN hold if on A.
- B: B end of IF-BC-PANEL, IF-AB-RIBBON, IF-AB-WALL, IF-AB-POWER, IF-LID-HF. Open: PWR-003 on B_PANEL_5V, FAB-02,
  FAB-04, addresses, EMCON L2, L3, L7, SD-EMC-1 and 2, touch USB with no port (on board D since the layer 5 merge, SC-HF-06), GND-002, RF pigtail and Ethernet
  contracts missing, outline under FB-FAB-6, R-HSD. INT-002 desk PASS (AI), INT-003 at prototype.
- C: C end of IF-BC-PANEL and IF-AC-MAINSW. Open: SLOT_EN hold, EMCON L1, the SD-EMC-6 lamp, PANEL address and
  heartbeat text; the face-plate bond is defined (eight ground rings).
- D: D end of IF-AD-HARNESS and IF-A-PA. Open: the +5V_D8 lead unjudged, the flange-sensor lead, D-04 band lock, W4-F17,
  J_ANT to J_RF1 and headset leads without contracts.
- E: E end of IF-AE-DOCK, IF-PE-PACK and IF-AE-RF clamps. Open: VIN_RAW (R4A-N12), clamp nests overlap, the D-07 clamp,
  J_BATT text naming the withdrawn BB-2590/U, external DC and solar, pod, sensor, tamper, water and fan leads.
- P: P end of IF-PE-PACK; SMBus lead passes. Open: PWR-F12 at 18 A for 60 s, cell and thermistor leads.
- E5: pass-through of IF-AE-DOCK from A32's board file; INT-001 UNBOUND; the D-14 insulating cap (S-22).

> **INTEGRATOR LINE, layer 5:** status at `e3aedb25` IN_PROGRESS; status now: IN_PROGRESS; as of commit: branch `fnd/r8int4` (set 4 after H1.1; commits `e5fde2ed` the re-take driver, `95e078a1` and `53292f81` layers 2 and 3, `0da2778b` layer 5, `c351115d` layer 7); items closed since `e3aedb25`: R8E-N01 recorded (round 8, EQ-16); board E's raw bus from both feeds (`bc0f562f`). **Since H1.1, the closer hc5 merged** (`0da2778b`): `v2/docs/HW-FW-CONTRACT.md` version 1 (the FW rows of boards A to P and the kit bus, the heartbeat source resolved from the netlist, V-nn checks, findings HF-F01 to F08, session choices SC-HF-01 to 06); eighteen new contracts in `pcb_interfaces.yaml` (30 in all; `records/hc5/check_contract_fields.py` reads 18 of 18); the monitor's touch USB given a board end (SC-HF-06, board D's `J_USB3`, carried in IF-MON, ASSEMBLY, PANEL, ARCHITECTURE section 12 and these pages); the supervisors' block 0x34 to 0x36 in CON-020, PANEL 7, IOHA 6 and ZEROIZE Z-C3; the kit I2C budget (CON-026 FAIL at desk: as one segment the bus cannot meet its 300 ns targets; SC-HF-02's three segments owed); ARCHITECTURE section 12 keeping board B's round 8 facts on IF-BC-PANEL; both of hc5's second-review blocking items CLOSED by the fresh verifier (AI); the claims-screen regression fixed at integration (ENV-002 PASS) and the second review's wording minors taken (V-B19, FW-A08, HF-F06 raised to major, IF-E-WATER, IF-E-SENSORS, IF-DA-VHF, IF-MON's D8_EN, IF-EXT-DC with D-16, IF-AE-RF and W4-F10 after the clamp bar). Remaining: (1) the first twelve contracts carry none of the pass-2 field list (`records/hc5/check_contract_fields.out.txt`); (2) SC-HF-02 drawn on A and B (S-59), HF-F02 on A (S-60), HF-F06 on D before its layout entry (S-61), HF-F07 on E (S-62), HF-F08 (the MDI side, judged by nothing); (3) the SLOT_EN hold, the dock contact remedy (EQ-16), GND-002, D-07's site on A; (4) INT-001 re-taken on the committed netlists (the re-take driver) and E5's INT-001 bound; (5) SC-HF-01 to 06 into the registry's session choices; (6) a Review C over the contracts; EQ-12; (7) after the release check of layers 1 to 3 (27 September 2026; the layer 2 release review, B4 (a), and the layer 3 release review, section 6): `HW-FW-CONTRACT.md` FW-C09 keeps C1 as a shed to one module with the round 8 fallback to "the reduced mode", against CONOPS section 4c's reduced mode on slots 2 and 3, and no row carries the hot stop (H1, H2), HOT-R1's four line states or the panel controller's read of the line at boot (`records/hc2/handoffs.md`, item 5 of its summary and section 16), nor PANEL.md the reduced mode's and the hot stop's panel duties (layer 2's m13). Owner: the integrator and the board A, B, D and E authors. **Second release attempt (27 September 2026, `fnd/rel2`):** item (5) done: SC-HF-01 to 06 are the registry's SC-58 to SC-63 (each recording its draft name as `drafted_as`), and the validator refuses an SC- id no entry defines; item (7) done for the contract: FW-C09 takes C1 as CONOPS 4c defines it, and FW-C13, FW-C14, FW-E10 and V-C13 carry the hot stop, HOT-R1's four line states and the panel controller's read of the line at boot. PANEL.md's reduced-mode and hot-stop panel duties (layer 2's m13) and IF-AE-DOCK's pin 12 (with HOT-R1, S-57) remain. **H2 (27 September 2026, set 5 and the consolidated re-take):** still IN_PROGRESS. Landed since this line's last step: SC-55 (`b7f96784`), VIN_RAW across the dock on four Mill-Max power pins with four returns and the 813 contacts as ground on both halves, with IF-AE-DOCK and three dock checks in `check_contracts.py`, so EQ-16 is answered at desk for the supply side (E5's fit, S-74, and the ground share, S-75, open); item (4) done by the re-take, INT-001 current on the six committed netlists, E5's INT-001 still AWAITING_REVALIDATION (UNBOUND). What remains is the H2 section's row for layer 5. Owner: the integrator and the board A, B, D and E authors.

### A.6 Layer 6. Components (the audit at `e3aedb25` and the edition history)

**Status at `e3aedb25`: IN_PROGRESS.** Part identity work is substantial and honest about its limits
(`v2/vendor/SOURCES.yaml`, the certification re-take at `45bde541`, 14 condition-1 marks, the reconciliation page),
but no acceptance item is met: no board has a per-line manufacturer, MPN and grade record; 42 current BOM lines read
WRONG_MODEL and 4 NO_STOCK; several critical parts have no identity entry; the H743 case is recorded in contradictory
states; grade is checked for 13 parts only; and nothing stops a tool re-run from erasing the mismatch marks. Almost
every closing action is desk, generator or tool work; the U8 choice waits on a bench purchase and R-PWR on the owner's
spend.

**Scope.** For every fitted part of A, B, C, D, E, P and E5: exact manufacturer, MPN, package and temperature grade,
supporting documents with revision and source, selection rationale, compatibility findings (owner condition 1: a
substitution is a mismatch until proven), procurement constraints and supported alternatives, and proof that
regenerated outputs preserve those decisions.

**Prerequisites.** Layer 8 netlists (the BOM source; they carry no MPN field); layer 5 interface parts; layer 7 case
parts; the FB-ZER-1 bench result for U8; owner authority for purchases and R-PWR.

**Deliverables**

| File | Revision (commit, sha256/16) | Current | Note |
|---|---|---|---|
| `v2/vendor/SOURCES.yaml` | `a6f87e9d`, 0546f5dfe18879ee | no | 65 critical-part entries; top-level identity, grade and name fields are stale where update blocks moved them (io-supervisor-mcu, power-button-controller, cellular-socket, which still describes the retired key-M socket with no entry for the fitted TE 2199119-3); no entry for RockBLOCK 9704, LimeSDR Mini 2.4, AW7915-AED, TPS23861, Preci-Dip 813, Mill-Max 0858, Radiall SMP-MAX, JST-VH, IDC headers, Glenair 233-370 and D38999, PolyPhaser arrestors, Xenarc 709GNK |
| `v2/release/revA/order/JLC-CERTIFIED.tsv` | `2aaa7b7f`, f615147fd58ddf7b | yes | 867 rows: CERTIFIED 594, BENCH_FITTED 88, WRONG_MODEL 75, HAND_FIT 60, NO_STOCK 15, NOT_CHECKED 12, NOT_AT_JLC 9, NO_PART_CHOSEN 6, PACKAGE_MISMATCH 5, NOT_IDENTIFIED 3; 14 rows hand-marked "MISMATCH under owner condition 1"; a full `jlc_certify.py` run would write CERTIFIED over the marks; CERTIFIED is a dated catalogue reading, not grade or suitability evidence |
| `v2/docs/evidence/WRONG-MODEL-RECONCILIATION.md` | `428c697c`, 97b1f63aa6ea11f1 | no | judged the `1f614233` candidates; its owed list stands |
| `v2/ecad/tools/jlc_certify.py` | `29f00554`, 76eadc959673d682 | no | no declared-mismatch input; takes the first part-shaped token of prose, producing parser WRONG_MODEL rows |
| `v2/ecad/tools/lcsc_fill.py` | `83ff00c4`, da4dbe667e26d0eb | no | its MAP carries the key (4.7u, C_0805) twice (lines 52 and 118); Python keeps the later |
| `v2/ecad/tools/jlc-handfit.txt` | `faf8c981`, cf8ec02e6f463be8 | yes | E's two 10 A Keystone 3568 holders match no allow line |
| per-board `lcsc-allow.txt` | A `eb22bddf`; B `1bfc361b`; C `29f00554`; D `ab3e57d5`; E `faf8c981`; P `ab3e57d5` | no | A's SMA allow line does not match the current row text; P's F1 relies on A's line |
| `v2/ecad/tools/pcb_part_temps.yaml` | `0ec34ce0`, f1cefc3a48504a01 | no | 13 parts; lists parts no current netlist fits; no rule compares every part's range with the envelope; H5007NL is 0 to 70 C against -20 C |
| `v2/vendor/open-picks.txt` | `4ffbf639`, 928545af9bf7b2be | no | 11 September text: tamper switch still open (fitted since `faf8c981`), four 5G jacks (D-07 ruled three), Bulgin PX0833 recommended (fails fit and is rated 42 V against 54 V PoE) |
| `v2/vendor/PARTS.md` | `62960469`, f0b36d00a90dcd21 | no | legend reads CERTIFIED as "JLCPCB returns this exact part", refuted by SOURCES.yaml's header |
| `v2/release/review-packets/C-C24-1f614233/bom/`, `E-E17-1f614233/bom/` | `ccf5808e` | no | circuits match `e3aedb25` but the joins predate later SOURCES changes; rebuild before sending; D and P packets superseded; A and B have none |
| `v2/docs/review-packets/battery/candidate/pcb-p-pack-bom.csv` | `d90f30e4`, 2e3980dc2a769db2 | yes | the only tracked current BOM for P |
| `v2/ecad/pcb-*/out/*-bom.csv` | not in git | no | gitignored; the local copies date from 11 September |
| `v2/docs/records/r4b/pin_parity.py` | `428c697c`, a36a9ffe82fbffd1 | yes | H743 against H753 LQFP-100 pin parity, 100 of 100 (RECORDED) |
| `v2/ecad/tools/pcb_board_holds.yaml` | `dd3b9074`, cdeac27ab5f7802d | yes | decision 31 fitted parts at layout entry (A U31 TPD2E2U06QDBZRQ1 C488151; D and E clamps) |

**Acceptance items**

| # | Item | Met | Evidence |
|---|---|---|---|
| 6.1 | Exact manufacturer, MPN, package and grade for every fitted part, per board | no | the netlists carry no MPN or manufacturer field; identity rests on LCSC codes resolved by the table, which is a catalogue reading. A join of the `e3aedb25` netlists against the table (727 BOM lines): 568 CERTIFIED, 42 WRONG_MODEL, 4 NO_STOCK, 40 HAND_FIT, 43 BENCH_FITTED, 30 with no row (IDC and pin headers, wire lands, spring pins). Grade compared with the envelope for 13 parts; H5007NL OUTSIDE. SA868 and RM520N-GL order codes NOT_PINNED |
| 6.2 | Supporting documents held with revision, source and currency | no | most critical parts have documents with sha256. Not held: ATECC608B full datasheet (NDA), ST RM0433, BCM54210PE, JST-VH catalogue, Mill-Max 0858, IDC header and ribbon, binder M8, RG-316; currency unconfirmed for ELX1135, 2954fb, DS12110, Peli 1451-931; one source URL missing |
| 6.3 | Selection rationale recorded | no | present for critical parts; absent for the passive and connector majority and the parts with no SOURCES entry |
| 6.4 | Compatibility findings recorded; known mismatches stay mismatches | no | the 14 hand-marked rows (B U80 74LVC86APW against SN74LVC86APWR; A J_MAINSW and J_HEAT gold -GU variant; A U1 LTC2954 suffix; E J_SMB and P J_SMB -G variant; P J_TS and D J_VGG -GW variant; B and D amber LEDs as yellow KT-0603Y; P J_TS2 annotated). Standing wrong models on current lines: A J_RF1 to 11 (132134-11 asked, 132134 answered), B six U.FL (C434808 against the U.FL-R-SMT-1 land), B U9 "DS3231MZ+" on a SOIC-8 land with C9866 resolving to the SOIC-16 DS3231SN, E F1 and F2 holders with no purchase route |
| 6.5 | STM32H753 against STM32H743 (CON-017, S-41, D-13) | no | the generator and netlist name STM32H743VIT6 C114409 and pin parity is 100 of 100, but the peripheral compatibility matrix (FDCAN at 1 Mbps or less, I2C1 target, GPIO, IWDG, SWD) from DS12110 is not written and firmware built for the H743 cannot exist yet; SOURCES says MATCH while CON-017, ARCHITECTURE line 585, EXECUTION-PLAN condition 1 and IOHA say open |
| 6.6 | Procurement constraints and supported alternatives | no | NO_STOCK: P U2 BQ7720700DSSR (3 against a need of 5), P F2 SCF9550-30-05 (0), B Y1 to Y4 25 MHz C164047; alternatives recorded piecemeal (ITV9550 evaluated, HX5004NL named, SLB 9673 fallback with no JLC stock); stock figures are dated readings of 25 and 26 September |
| 6.7 | Regenerated outputs preserve part decisions | no | a certification re-run erases the 14 marks; generators still type refused codes (A J_RF C3174425, B U.FL C434808, B U9 C9866); `lcsc_fill.py`'s duplicate key; BOMs only in untracked folders. Schematic regeneration parity itself is RECORDED (`faf8c981`, `458b2873`, `3a1f6576`) |
| 6.8 | A current, versioned BOM with identity per board | no | current only for C and E (quarantined packets, to be rebuilt) and P (battery candidate); none in git for A, B, D |
| 6.9 | CMP-001: no absolute maximum reached | no | PASS on every board but AWAITING_REVALIDATION (TOOL_CHANGED) |
| 6.10 | CMP-002 and SUP-001: package on land is the package ordered; every part buyable | no | RELEASE_PACKAGE phase; INCONCLUSIVE until re-taken; U9 and the key-B socket's missing locating holes (S-12) are land defects found at desk |
| 6.11 | Review D per board and R-PWR before A's layout entry | no | no Review D record; R-PWR needs the owner's spend (EQ-11) |

**Unresolved decisions**

| Decision | Downstream impact | Waits on later evidence |
|---|---|---|
| H743 compatibility at the schematic stage: write the DS12110 matrix, allocate CON-017 clause 4 (firmware builds) to the firmware stage, reconcile the records | B supervisors U41, U51, U61; S-40 | no |
| Adopt the recommended codes for the condition-1 rows (C158012, C144395, C131337; amber LED rows; U80 as SN74LVC86APWR; the LTC2954 suffix from ADI's order guide) | BOM lines on A, B, D, E, P; no land change | no |
| Holdover RTC on B U9: DS3231M (SOIC-8) with a purchase route, or DS3231SN on a 16-pin SO land | B U9 land, kit bus row 0x68 | no |
| Ethernet magnetics T1: H5007NL (0 to 70 C) with a stated carve-out, or HX5004NL after a pin check | B T1 part and possibly land; REQ-024 | no |
| Board B U8: ATECC608B-SSHDA-T or the SLB 9673 fallback | B U8 land, ZEROIZE firmware, kit bus | yes (EQ-06) |
| Purchase routes and alternatives for SCF9550, BQ7720700, the 25 MHz crystal, the Keystone 3568 holders | P and E BOMs; a land change if an alternative's package differs | no |
| Pin the SA868 and RM520N-GL order codes | D exciter footprint and band, B module variant, the EMCON bench | no (buying stays the owner's) |
| Identity and ratings for the interface parts (IDC, JST-VH, Mill-Max 0858, SMP-MAX, Preci-Dip 813, sealed RJ45 at 54 V, sealed USB-C at 45 W, jumper plug, M8, ground stud, arrestors) | layer 5 capacity rows, connector plate, M17g and M17x | no |
| Move CMP-002's identity-and-land half to layout entry | the layout-entry test; avoids a re-layout for a land defect | no |
| Fans (D-18): Delta 40 mm IP68 or 60 mm Same Sky CFM-6025BG68, or not IP68 | cooler and mixer fans, thermal basis | no |

**Stage-gate cycles and remedies**
- CMP-002 and SUP-001 sit at RELEASE_PACKAGE while the land evidence exists at schematic: not a cycle, but a late gate
  that lets a land defect reach layout. Remedy: move the identity-and-land half to layout entry; keep stock at order in
  SUP-001.
- CON-017 clause 4 (firmware built for the H743) at SCHEMATIC holds B's schematic record on a deliverable the layout
  decision does not need. Remedy: allocate it to the firmware stage with its reason; keep clause 3 at schematic.
- FB-ZER-1's Z-EXP-A and B before B's layout entry need a purchase only the owner can authorise: a genuine external
  authorisation on the U8 choice, not a cycle.

**Next closing actions**
1. Write the STM32H743 peripheral matrix from DS12110 Rev 10 and AN4938 Rev 7 (held); fetch RM0433 through the
   Internet Archive; set CON-017 clause 4 to the firmware stage; reconcile SOURCES, ARCHITECTURE 5.5 and 13.3, IOHA 6
   and 10a. Parts stream and integrator; none.
2. Land the declared-mismatch input for `jlc_certify.py` (the r8cert draft `tools/jlc-mismatch.yaml` with its tests),
   fix the part-token parser, delete `lcsc_fill.py` line 118's duplicate key, and add fixtures proving a full run keeps
   every mark. Tools stream; after review of the draft.
3. Apply the recommended codes and texts in the generators and allow lists (C158012, C144395, C131337, LED colour text,
   U80, U.FL C88373, A J_RF identity or hand-fit route, U9 part and land, E F1 and F2 and P F1 allow lines). Board
   streams; after round 8.
4. Re-take `jlc_certify` over the current candidates' BOMs (public API, no login, no cart) after round 8, then publish a
   per-board BOM with identity as versioned NOT_FOR_FAB files (packets for A, B, D; rebuilt C, E; P at `d90f30e4` or
   later). Parts stream on a KiCad host; after actions 2 and 3.
5. Add SOURCES entries for RockBLOCK 9704, LimeSDR Mini 2.4, AW7915-AED, TPS23861, the chosen DS3231, Preci-Dip 813,
   Mill-Max 0858, Radiall SMP-MAX R222M00720 and R222M80500, JST-VH, the IDC header and ribbon, Glenair 233-370 and
   D38999, PolyPhaser GTH-SFF-AL, Xenarc 709GNK, TE 2199119-3, CM5108064; align top-level fields with update blocks;
   regenerate PARTS.md with a correct legend; rewrite `open-picks.txt`. Parts stream; none.
6. Extend the grade check to every fitted active part and connector against `pcb_envelope.yaml`; rule H5007NL against
   HX5004NL; correct `pcb_part_temps.yaml`. Parts stream and board B author; none.
7. Record procurement constraints and alternatives for SCF9550, BQ7720700, the 25 MHz crystal and every single-source
   critical part, with dated stock readings; pin the SA868 and RM520N-GL order codes from the makers' documents.
   Parts stream; none.
8. Move CMP-002's identity-and-land half to layout entry in `pcb_rules.yaml` and the coverage map as a SESSION
   decision. Registry writer; rule fingerprint re-pin and re-render.
9. **Needs authorisation (L-06):** Z-EXP-A and Z-EXP-B on the fitted ATECC608B-SSHDA-T to decide U8 (EQ-06).
10. **Needs the owner (spend):** commission R-PWR (EQ-11); the session prepares A's packet after round 8.

**Per board** (join of the `e3aedb25` netlists against the table)
- A: 183 lines: 144 CERTIFIED, 14 WRONG_MODEL (J_RF1 to 11; J_MAINSW and J_HEAT; U1 suffix), 18 HAND_FIT, 3
  BENCH_FITTED, 4 with no row (J_AB1, J_AB2, J_MEZZ1 IDC headers, J_USBC_OUT pin header); pack pins "Mill-Max 0858
  class" with no MPN; decision 31's U31 recorded; R-PWR not commissioned.
- B: 245 lines: 200 CERTIFIED, 14 WRONG_MODEL (four parser rows on the reference clock and HCSL parts, U80, U9, six
  U.FL, amber LEDs), 2 NO_STOCK (Y1 to Y4), 5 HAND_FIT, 13 BENCH_FITTED, 11 with no row; H743 CON-017 INCONCLUSIVE and
  recorded inconsistently; H5007NL grade OUTSIDE; U8 open (EQ-06); the key-B socket land lacks its locating holes
  (S-12); no SOURCES entries for TPS23861, AW7915-AED, RockBLOCK 9704, LimeSDR.
- C: 73 lines: 40 CERTIFIED, 0 WRONG_MODEL, 12 HAND_FIT, 17 BENCH_FITTED, 4 with no row (J_PANEL IDC, J_MAINSW and J_PIJ2
  lands, JP2); a current-circuit packet exists and must be rebuilt.
- D: 86 lines: 74 CERTIFIED, 7 WRONG_MODEL (R80, R81, Y1, Y2 parser rows; J_VGG; LED2 and LED5 amber), 2 HAND_FIT, 2
  BENCH_FITTED, 1 with no row (J_HARN1); SA868 NOT_PINNED; no current BOM in git.
- E: 103 lines: 83 CERTIFIED, 4 WRONG_MODEL (F1 and F2 holders; J_TAMP parser row; J_SMB), 3 HAND_FIT, 7 BENCH_FITTED, 6
  with no row; a current-circuit packet exists, to be rebuilt.
- P: 37 lines: 27 CERTIFIED, 3 WRONG_MODEL (J_TS parser row, J_SMB, J_TS2), 2 NO_STOCK (U2 BQ7720700DSSR 3 against 5; F2
  SCF9550-30-05 0, ITV9550 evaluated as the alternative), 1 BENCH_FITTED, 4 with no row; current BOM in the battery
  candidate; R-BAT pending.
- E5: no placed parts (17 footprints: targets, holes, wire lands); the D-14 insulating cap neither drawn nor sourced.

> **INTEGRATOR LINE, layer 6:** status at `e3aedb25` IN_PROGRESS; status now: IN_PROGRESS; as of commit: `99cde56b` (H1); items closed since `e3aedb25`: the STM32H743 compatibility matrix against the H753 and the errata (`v2/docs/parts/STM32H743-COMPATIBILITY.md`), procurement constraints and alternatives with dated public readings (`PROCUREMENT.md`), the grade of every fitted active part and connector against the envelope (`GRADE-CHECK.md`, regenerated at H1 for round 8's boards C and P), fourteen new SOURCES entries and the maker documents behind them (hc6; its review, an AI review, has no blocking item); `jlc_certify.py` reads the declared mismatches (`661ca3a4`); review record: hc6's review (filed in H1.1 as `v2/docs/records/handover/hc6-review.md`). Remaining: the generators write no MPN field, and 1497 of the 2205 per-reference rows of the six schematic BOMs carry no LCSC code, 1322 of them resistors, capacitors and inductors (EQ-21); the generator changes hc6 recommends (HC6-SC-3, HC6-SC-6 to HC6-SC-9: board B's T1 to the Pulse HX6096NL, the crystals, the IDC headers, the Mill-Max pins, consigned lines); `pcb_part_temps.patch` of `fnd/hc6` with its part_temps re-take; PROCUREMENT.md's readings for HX6096NL and four alternatives, not filed; U8 (EQ-06); R-PWR (EQ-11); LimeSDR Mini 2.4 and AW7915-AED OUTSIDE the envelope; the INFERRED order codes of the SA868 and the RM520N-GL; `PARTS.md` regeneration. **H2 (27 September 2026, set 5):** still IN_PROGRESS. Landed since H1: set 5's part entries for boards A and B (`ffca0771`, `caba1876`), W3B-F1 and W3B-F2 drawn on B, decision 42's class on B's 277 decoupling entries. Re-counted on the H2 exports: 1630 of 2393 per-reference BOM rows carry no LCSC code, 1446 of them R, C and L (EQ-21). New open items S-65, S-71 to S-73 and S-76. The rest of this line's list is carried and was not re-checked in H2. Owner: the parts writer and the board authors.

### A.7 Layer 7. Mechanical and enclosure (the audit at `e3aedb25` and the edition history)

**Status at `e3aedb25`: IN_PROGRESS.** A reproducible design-basis tolerance analysis exists (`v2/docs/CASE-MARGINS.md`
with `v2/vendor/peli/frame_seat.py`, re-run byte-identical at `e3aedb25`), and the case choices C1 to C6 are recorded
as SC-07. The editable CAD and every drawing predate C1 to C6, and the declared single geometry source
`v2/ecad/tools/panel1450.py`, which the MEC-001 checks read, carries superseded numbers. Four made parts have no
drawing. Two margins fail with the geometry as assumed, pending a desk pick that can move board B's east edge. The
pack hold-down, stack retention, dock and blind-mate tolerance stack, the J_AB2-under-D bay, the fans and the floor
plan are undesigned, and the thermal interfaces rest on an enclosure conductance whose bound includes failure. Most
closing work is desk work; the case mock-up and the heat test need the owner's purchase authorisation.

**Scope.** The kit in the Peli 1450 (current moulding of drawing 1451-931, 15 January 2025, D-08a) with the 1450PF
frame: editable CAD and dimensioned drawings of every made part (face plate, setting legs with locator and wedges,
connector plate, two RF entry plates, lid tray, pack hold-down, rod-stack retention, wall templates); board envelopes
and the Z stack with named spacers; mounting and retention; connector, cable and service access; the tolerance
analysis against Peli's figures; the thermal interfaces. Not electrical, RF-performance or EMC verification.

**Prerequisites.** D-01, D-02b, D-02c, D-02e, D-06, D-07, D-08 reversed and D-08a; layer 4's thermal architecture
(FEA-004); layer 5's mechanical interfaces; layer 6 picks that decide rows (CASE-MARGINS section 6); board outlines and
placements from `gen_pcb_{a,b,c,d,e,e5,p}.py` and `gen_pcb_{a,b}3.py`.

**Deliverables**

| File | Revision (commit, sha256/16) | Current | Note |
|---|---|---|---|
| `v2/docs/CASE-MARGINS.md` | `a6f87e9d`, 275a3083db30a7bf | yes | 70 margins: 35 MET as a sensitivity reading, 35 OPEN (two of them failing as assumed); changes C1 to C6; checks T1 to T11; none of C1 to C6 is in CAD; its ASSEMBLY line citations are at `29f00554`; its independent checks were agent checks not labelled AI review |
| `v2/vendor/peli/frame_seat.py` and `1450/frame_seat.out` | `a6f87e9d`, 93049a16bf89ed30 and 214e915b985518cb | yes | stdlib; re-run byte-identical; board inputs are typed constants (lines 118, 120, 122, 584), so they can drift silently |
| `v2/vendor/peli/case_margins.py` and `1450/case_margins.out` | `b69f20db`, 3391fe828e17870c and 1609b6e5f65f3c29 | yes | re-run identical |
| `v2/vendor/peli/step_faces.py`, `dxf_read.py` and readings | `b69f20db` | yes | readers of Peli's STEP and DXF |
| `v2/vendor/peli/1450/` (1451-931 STEP top and bottom, 1450PF STEP, customer drawing PDF and DXF, `1450_pf.pdf`) and `panel-frame-inst.pdf` | `c1f6f357`; `b69f20db` | yes | maker geometry; the base STEP outer skin is an envelope block; the Peli web captures are cited by sha256 but not in the tree |
| `v2/ecad/tools/panel1450.py` | `c2333029`, df4959c6b4b81825 | no | superseded: plate 365.5 x 249.5 on M3 from below (lines 16 to 18), FACE_TOP_Z 101.4 (line 26), SMA_Z 88 and the old wall lists (lines 116 to 118); B16_TALL (line 36) hand-typed |
| `v2/ecad/tools/case_wall_cutouts.py` | `2306b0e6`, f89c5ed0e34a6dba | no | still the 54 x 82 x 3 plate between ribs and eleven D-holes at Z 88 |
| `v2/ecad/tools/z_budget.py` | `ad3b00c2`, 9468924a47799e67 | no | datum 101.4, a non-Peli datum |
| `v2/cad/face_plate.py`, `v2/cad/plate_drawing.py` | `ad3b00c2` | no | pre-C1 (no 4.6 mm holes, rebate or relief pocket) |
| `v2/cad/frame_leg.py`, connector plate, RF entry plate and pack hold-down CAD | absent | no | owed (CASE-MARGINS C3, C4, C6; READY-TO-ACT 6.2) |
| `v2/cad/pack_4s.py` | `209bb369` | no | its box does not fit; redesign owed under D-06 |
| `v2/cad/lid_bracket_qmx.py` | `1f46cf83` | no | the tray may stand; its placement predates C5 |
| `v2/cad/float_clamp.py` | `37ee6631` | no | 16 mm nests overlap at the 14 mm pitch; clamp bar owed |
| `v2/cad/battery_module.py` | `d8a09b95` | no | the retired twelve-cell module |
| `v2/cad/render/scene.py`, `glb/`, `v2/cad/stack-heightmap.json` | `47684b3d`, `6851b27c`, `e5f1cea7` | no | presentation; 7 and 5 September geometry |
| `v2/release/revA/case/` | `ad3b00c2` and earlier | no | historical and not labelled as such; the face-plate DXF lacks the recessed-monitor window its README describes |
| `v2/docs/ASSEMBLY.md` | `9a151c78`, e4a0b78616c69779 | no | partly corrected; lines 38, 43, 55, 72 to 75 and section 3 contradict C1 to C5; board names A22, B16, C7, D8, E6 |
| `v2/docs/ARCHITECTURE.md` sections 7, 8, 9, 11, 13.6; POWER-THERMAL sections 9 and 10; READY-TO-ACT sections 5 and 6; `records/w4/` | as listed above | yes | stack, thermal, RF plan, mass and dimension budgets, the costed tests |
| `v2/ecad/tools/pcb_board_facts.yaml` | `bed211b6` | yes | outlines agree with the `gen_pcb_*.py` generators |
| `v2/docs/TEST-PLAN.md` | `9a151c78` | no | no T1 to T11, rise per state, closed-lid test or weighing; E5 and E8 vent steps |

**Acceptance items**

| # | Item | Met | Evidence |
|---|---|---|---|
| 7.1 | Editable CAD current for the board set and the chosen arrangement | no | C1 to C6 exist only in CASE-MARGINS section 4; `panel1450.py`, `face_plate.py`, `case_wall_cutouts.py`, `z_budget.py` and `scene.py` carry superseded geometry; four made parts have no CAD |
| 7.2 | Dimensioned drawings of every made part and wall templates | no | the only drawings are the pre-C1 face plate (`1f46cf83`) and the pre-C2 wall template (`2306b0e6`) |
| 7.3 | Board envelopes (outline, holes, height zones both sides, the Z stack with named spacers) | no | outlines VERIFIED and consistent; the stack "INFERRED until the stack is drawn"; spacers unnamed; tall-part heights hand-copied; J_AB2 stands 3.1 mm into board D (W4-F17) |
| 7.4 | Mounting and retention (face, stack, pack, dock) | no | face designed on paper only; the rod stack held only by VHB pads with the north rods footless (W4-F7); the pack hold-down undesigned; RockBLOCK fastener type and drop owed |
| 7.5 | Connector, cable and service access | no | the connector plate laid out against class envelopes, but the recommended RJ45 fails its envelope and 54 V; USB-C, M8, pod and stud TBD; M17g (-2.43 mm) and M17x (-0.38 mm) fail as assumed; floor plan not drawn; lift-out M7 MET |
| 7.6 | Tolerance analysis with a stated model and reproducible computation | yes | CASE-MARGINS section 1 (model, verdict rule), 3.1 and 3.2 (70 rows); both scripts reproduce byte-identical; MET qualified as a sensitivity reading |
| 7.7 | Blind-mate and dock contact tolerance stack closed on paper (REQ-047) | no | no row judges it (CASE-MARGINS section 6 end); the 813 pin window (+0.4/-1.0 mm) and the SMP-MAX axial +-1 mm have no current stack; nests overlap; E17 carries LORA at X 102 against A's 100; no clamp for ANT3 at X +46 |
| 7.8 | Thermal interfaces specified with feasibility at this stage | no | paths in words only; mixer fans unplaced and the fan part unsettled; the flange sensor not drawn; REQ-059 TBD; the conductance bound includes failure (EQ-05) |
| 7.9 | Critical fit uncertainties resolved by suitable evidence | no | M1 OPEN on three TBD contributors (1.80 against 2.0 with allowances doubled); M17g and M17x fail as assumed; M20, M4a, M5 and the dock window open |
| 7.10 | Later physical checks allocated, with deferral justified where the decision does not depend on them | no | T1 to T11 allocated per board, but option (c)'s justification is gate authority, not decision independence, while M17x and M18 decide B's east edge and M1 its stack; FEA-004 puts the heat test at fabrication release against the review and POWER-THERMAL section 10 |
| 7.11 | REQ-019: every case-dependent margin MET | no | 35 OPEN, 2 failing as assumed |
| 7.12 | CON-006: a named pack build with its hold-down, every margin MET | no | M4a, M5 OPEN; hold-down undesigned; `pack_4s.py` does not fit |
| 7.13 | MEC-001 judged on the current case geometry | no | PASS on B, C, D, E, P from checks that read `panel1450.py`'s superseded geometry; CASE-MARGINS 3.2 finds eleven rows below minimum as designed; A reads FAIL |
| 7.14 | Session engineering choices recorded with authority | yes | SC-07 (C1 to C6), SESSION under the standing rule; CONOPS 7a |
| 7.15 | No contradictory live specifications; superseded artefacts labelled | no | `v2/release/revA/case/README.md` unlabelled; ASSEMBLY, V2-SPEC, BUILD, README, REQ-047 ("ten M3"), CON-006 ("X +120 to +178") and GROUNDING-AND-SHIELDS line 39 contradict C1 to C6 |
| 7.16 | Review labelled; AI review not standing in for a required qualified review | no | CASE-MARGINS' independent checks were agent checks, unlabelled; no qualified mechanical or thermal review route exists |
| 7.17 | Portable regeneration of the mechanical outputs | no | the margin scripts are stdlib and reproduce; the CAD needs `build123d`, `ezdxf` and `matplotlib` with no pinned versions and no requirements file; renders need Blender 4.2 on a GPU host |

**Unresolved decisions**

| Decision | Downstream impact | Waits on later evidence |
|---|---|---|
| Jumper right-angle SMA crimp plug for RG-316 (cable-axis offset, ferrule, reach), or a lever (5G MAIN turned 26.5 degrees, IRIDIUM to the back bundle, or ANT3 dropped) | M17g and M17x decide B's east edge at X 165 and its east-end tall parts, and whether D-07 falls back to two 5G jacks | no: a maker's drawing and a pick |
| Sealed RJ45 re-pick in the shell 15 envelope rated for 54 V; the USB-C panel drawing, M8, pod, stud | connector plate C3 layout, wall holes, clearances under B (U51) and A | no |
| Pack hold-down design (the `pack_4s.py` redesign) | P's place, M4a and M5, CON-006, E1 and E2 survival | no |
| Rod-stack retention (W4-F7; proposal RF-1 not ruled) | mounting holes on A, B, E, a possible floor plate, REQ-022 | no |
| J_AB2 inside D's mezzanine rectangle: move the header or re-derive D's standoff | A placement, D standoffs, the bay spacer | no |
| Dock and blind-mate tolerance stack and E's clamp bar with an ANT3 clamp at X +46 | A, E, E5 connector X and Y, block height and shims, gap spacer; REQ-047; D-07 | no |
| Fan parts and positions and the floor plan | E placement, legs' zones, jumper routes, the thermal coupling | no for the design; fan capacity depends on the heat test |
| Whether the sealed no-vent case keeps cells, the PA flange and at-risk parts inside limits across the envelope | hot-part placement on A, B, D, P; fan count; PA mounting and flange sensor; pack location; the +35 and +25 C controls; possibly layer 4 | yes (EQ-05) |
| The 30 OPEN rows on unstated allowances, the frame seat M20 and the arrestor O-ring M13 | outlines and connector places of A, B, C, E, P; the plates' drilling | yes (EQ-08) |
| M1 face-over-heatsink contributors (Xenarc rear frame, CM5 cooler height, named spacers) | B stack height, C backer, leg pad height 94.13 | no: lookups and a drawing now |
| E1 end-wall drops onto arrestors standing 43.9 mm proud: a guard or a stated test exclusion | entry plate design, TEST-PLAN E1, mass | no |

**Stage-gate cycles and remedies**
- No strict cycle. Missing gate: the computed layout-entry test contains no case-geometry item, so a board could read
  ready on `panel1450.py`'s superseded geometry with M17g and M17x failing for B. Remedy: add a geometry item.
- CASE-MARGINS section 7 option (c) carries the mock-up rows to fabrication release when the case is not bought; the
  recorded reason is gate authority, not decision independence, and for M17x and M18 (B's east edge), M1 (B's stack,
  C) and M4a and M5 (P, A's east edge) the layout decision does depend on them. Remedy: close what a desk pick can
  close before layout entry and keep the carry-over explicit per board. (Done at the layer 7 merge: option (c) is
  withdrawn and FEA-007 holds the layout entry of boards A, B, E and P on the mock-up.)
- FEA-004 places the heat test at FABRICATION_RELEASE, against the second review ("before freezing affected placement
  and pack design") and POWER-THERMAL section 10 ("before more layout"); the bound includes failure, so a PROVISIONAL
  label cannot defer it. Remedy: as layer 4's FEA-004 restaging.

**Next closing actions**
1. Implement C1 to C6 in the single geometry source and regenerate: `panel1450.py` (plate 377.2 x 263.0 R16 with its
   rebate band, frame bosses at the STEP bores, FACE_TOP_Z derived from 94.13 + 9.39 + 3.00, SMA_Z 59, the C2 wall
   lists, leg constants), `z_budget.py`, `face_plate.py` and `plate_drawing.py` (4.6 mm holes, rebate, relief),
   `case_wall_cutouts.py` (connector plate 114 x 68.3 x 5 with six items, entry plate sheet), new `v2/cad/frame_leg.py`,
   connector plate and entry plate CAD; then re-take `check_pcb_c` and MEC-001 in a clean clone. Case writer (sole
   owner of `panel1450.py`), CAD on a host with `build123d`; about one working day plus host time.
2. Publish the regenerated case set as a new versioned folder (STEP, DXF, dimensioned PDFs, 1:1 templates); mark
   `v2/release/revA/case/README.md` HISTORICAL. Integrator; after action 1.
3. Bring the live specifications in line with C1 to C6 (ASSEMBLY 1, 2, 3, 7, 9; V2-SPEC lines 8 to 13 and 42; BUILD
   lines 35, 45, 57 to 59; README line 52; REQ-047 and CON-006; CONOPS line 267; READY-TO-ACT 6.1;
   GROUNDING-AND-SHIELDS lines 15 and 39); label CASE-MARGINS' checks as AI review. Integrator; none.
4. Pick the jumper plug from a maker's drawing (cable axis at least 1.38 mm from the inner end, ferrule at most 2.58
   mm, reach at most 13.58 mm) or take a lever; re-run `frame_seat.py` so M17g and M17x meet their minimums before B's
   layout entry. Parts stream with the case writer.
5. Re-pick the sealed RJ45 (shell 15, 54 V or more); obtain the PXP4043/C drawing, the binder 86 6618 1121 00004 sheet,
   the ground stud and the pod class; re-run `frame_seat` part E. Parts stream.
6. Close M1's TBDs: file Raspberry Pi's CM5 cooler drawing, draw the Xenarc rear frame, name the 13.4 mm gap and the
   bay spacers with tolerances, file the C&K and APEM heights. Parts stream and case writer.
7. Draw the Z stack from the committed boards (part heights and sides read from the KiCad files); resolve W4-F17; add a
   desk check of B's 54.5 mm overhang beyond the rods (carrying the RockBLOCK) for E2. Board A placement owner and
   case writer; after round 8 schematic merges (outlines unchanged).
8. Write the dock and blind-mate tolerance stack (SMP-MAX axial +-1 mm and radial float against the rods' 0.3 mm; the
   813 window +0.4/-1.0 mm; the Mill-Max pins; the 1.1 mm VHB pads with their thickness tolerance; spacers and
   laminates); design E's
   clamp bar with an ANT3 clamp at X +46; regenerate E so LORA reads A's X. Board E stream with the case writer.
9. Design the pack hold-down (the `pack_4s.py` redesign) and the rod-stack retention, each with an E1 and E2 load
   estimate and the VHB and primer choice. Case writer.
10. Settle the fans and draw the floor plan (fans, water electrodes, sensor modules, harness and jumper lanes, the
    shore lead lane), clear of the legs. Case writer with board E; after action 8.
11. TEST-PLAN: add T1 to T11 (or cross-reference them), the inside-air rise per state lid open and closed, the
    closed-lid thermal test, mass weighing and antenna return loss; correct E5 and E8; decide the E1 end-wall guard or
    exclusion. Integrator.
12. Re-allocate stages per the owner's section 2: for each OPEN row and board, record whether the layout decision
    depends on it; close those at desk before layout entry or add them to that board's layout-entry requirement; add a
    geometry item to the computed test; reconcile FEA-004, EXECUTION-PLAN and POWER-THERMAL section 10. Registry
    writer.
13. Make `frame_seat.py` read its board inputs from `panel1450.py` and the board files, add a drift test, pin the CAD
    toolchain (a requirements file with `build123d`, OCP, `ezdxf`, `matplotlib` versions), write a host-independent
    regeneration note. Tools stream; after action 1.
14. File the Wayback captures of the Peli 1450 and 1450PF pages that CASE-MARGINS section 1 cites (licence and
    publication checked), or state that the recipient re-fetches them. Records stream.
15. Look up PolyPhaser's O-ring dimension and the 1450PF polymer grade (Internet Archive if the makers' sites refuse);
    if absent, prepare but do not send the question texts. Parts stream; contact stays with the owner.
16. **Needs the owner's purchase authorisation:** buy the current-moulding case and 1450PF frame (serving both tests),
    then the made parts, one arrestor, the picked jumper plugs and stand-ins; run the heat test, then T1, T2, T4, T5,
    T6, T10 and T11 (EQ-05, EQ-08). An assembler with gauges; after action 1's drawings.

**Per board.**
- A (240 x 160, `gen_pcb_a.py` lines 16 to 17): outline VERIFIED; its east edge bounds the pack pocket (M4a OPEN); the
  ANT3 site at X +46 is in no generator; J_AB2 stands into D (W4-F17); MEC-001 reads FAIL.
- B (330 x 200, `gen_pcb_b.py` line 21): outline VERIFIED; the east edge and east-end tall parts depend on M17x and M18;
  the stack height under the monitor is M1 OPEN; underside over the pack M6 MET; tall-part envelopes hand-copied;
  RockBLOCK fastener drop owed; the 54.5 mm overhang unassessed for E2.
- C (ring 344 x 228, void 240 x 176): its height changes with C1 and C6, but `check_pcb_c.py` reads the superseded
  FACE_TOP_Z 101.4, so its MEC-001 PASS is on superseded geometry; M21h MET.
- D (100 x 80 mezzanine on 6 mm standoffs): the J_AB2 collision; the PA flange thermal path, flange sensor and plate
  patch unmeasured.
- E (267 x 68, `gen_pcb_e.py` line 15): nests overlap; LORA at X 102 against A's 100; no ANT3 clamp; M15b OPEN; the north
  rods have no foot; fans and floor plan not drawn.
- E5 (43 x 26): the dock contact window has no current stack.
- P (70 x 44 at the pack's south end): hold-down undesigned (CON-006, M4a, M5).
- Case parts (face plate, legs, connector plate, two entry plates, lid tray): on paper in CASE-MARGINS C1 to C6; no
  current CAD or drawing; the revA case files are historical.

> **INTEGRATOR LINE, layer 7:** status at `e3aedb25` IN_PROGRESS; status now: IN_PROGRESS; as of commit: branch `fnd/r8int4` (set 4 after H1.1; commits `e5fde2ed` the re-take driver, `95e078a1` and `53292f81` layers 2 and 3, `0da2778b` layer 5, `c351115d` layer 7); items closed since `e3aedb25`: board E's clamp bar (`45f6d83f`); hc4's case drawings (at `e3aedb25`). **Since H1.1, the closer hc7 merged** (`c351115d`): the case choices C1 to C6 in `panel1450.py`, `z_budget.py`, `case_wall_cutouts.py` and the CAD; the board reading required (`ZstackMissing`) and in board C's gate's evidence identity (`check_pcb_c.py` declared in `rules_status.CONFIG_INPUTS`); `frame_seat.py` reading U51 at ST's maximum (no figure moved); `v2/release/case-2026-09-27/` (the made parts' STEP and DXF, fourteen sheets with the QMX lid tray on sheet 14, MANIFEST checked); `CASE-FIT-UNCERTAINTIES.md`; FEA-007 and L-07 (the layout entry of boards A, B, E and P BLOCKED on the mock-up purchase; C, D and E5 not held); `test_case_geometry.py`; the fresh verifier CLOSED the tray release and left the timing NOT_CLOSED on six passages and two new contradictions, all fixed at integration (READY-TO-ACT's one-case order with its consequence, S-1 and S-8; REQ-019; ARCHITECTURE section 7; the layout-constraint README; OPERATING-ENVELOPE's pack row; V2-SPEC correction 18; EQ-08, the brief and this page). Remaining: (1) the mock-up purchase (L-07, EQ-08) and, with one case, the heat test before it (EQ-05); (2) the QMX lid tray revised from the unit's enclosure drawing before it is printed: the unit has jacks on both end panels and the tray notches one (S-63, EQ-24); (3) the jumper plug pick (M17g, M17x), the pack's hold-down (S-27), the sealed RJ45; (4) `v2/images/face-section.png` and `v2/cad/render/` still draw the superseded face (their owners'); (5) `CASE-MARGINS.md`'s 'Implemented in CAD' note and the `v2/cad` README call `panel1450.py` the single source including the tray, whose Y place lives in `lid_bracket_qmx.PLACE_Y` (c7's choice), and `scene.py`'s QY is a typed copy no test ties to it; (6) the snapshot's ZIP cap: the case release adds about 1.6 MB compressed where H1.1 left 1.3 MB under `pack.yaml`'s max_zip_bytes. Owner: the case writer and the integrator. **H2 (27 September 2026):** still IN_PROGRESS; item (6) is answered by the H2 assembler under the owner's standing rule of 26 September 2026: the five superseded candidate patches are referenced, not bundled (`pack.yaml`), which keeps H2 under the cap with the case release bundled. Items (1) to (5) remain, with S-74 (E5's targets and 12 AWG holes for EQ-16's power pins). Owner: the case writer and the integrator.

### A.8 Layer 8. Schematics (the audit at `e3aedb25` and the edition history)

**Status at `e3aedb25`: IN_PROGRESS.** Committed native schematics, netlists and generator sources exist for all six
schematic boards, with provenance that matches HEAD, but no board meets the layer. Readable PDFs and BOMs of the
committed schematics exist only for C, E and P. ERC on the committed A and B schematics does not exist, and the other
boards' current readings are untracked and TOOL_CHANGED. No whole-board functional review exists, and the qualified
reviews that records require (R-PWR, R-BAT, R-HSD) are not done. Part and land mismatches remain, and every board
carries open schematic-affecting defects whose remedies sit in uncommitted round 8 branches. Some items need outside
steps (B's U8, the qualified reviews), but most are doable now.

**Scope.** Per board: the native KiCad 9 schematic generated by `gen_sch_<x>.py` from `boards/<x>.json` and the shared
inputs (`kisch.py`, `intent.py`, `schlayout.py`, `idc_pads.py`, `gen_footprints_*.py`, `v2/ecad/meshsat.pretty`), its
netlist with provenance sidecar and intent file, a readable paged PDF, the BOM, ERC under `erc_gate.py` with its allow
list, regeneration parity (condition 5), a functional circuit review (AI labelled as AI; qualified where required),
exact part and land mapping (SCH-005, condition 1), and closure of every known schematic-affecting defect. E5 is a bare
contact board whose board file is its design (CURRENT-EVIDENCE.md line 34). Layout is layer 10.

**Prerequisites.** Layer 3 (the FEA layout-entry stages are circuit items here); layer 4 rulings that decide circuits
(EMCON SD-EMC-1, 2, 6 and L1 to L4, L7; the U8 part; FB-FAB-1 to 5; decoupling G1 to G14); layer 5 contracts; layer 6
identities (condition 1); decisions 29, 31, 34, 42 and D-13; a KiCad 9.0.9 host with `mupdf-tools` (the runner that
wrote these pages has no `pcbnew`).

**Deliverables**

| File | Revision (commit, sha256/16) | Current | Note |
|---|---|---|---|
| `v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_sch` | `3a1f6576`, d2360d4804609f1d | yes | declared A32, title-block label A65; the sidecar's schematic sha matches |
| `v2/ecad/pcb-a-power-a23/out/pcb-a-power.net` (+ `.net.prov.json`, `-intent.json`) | `3a1f6576`; net 7b08510106687b3d, prov 50bb70fb5e8678eb (generator 73232f60649f2c83), intent 83ba5e43a6fbcccb | yes | all 69 generator files named in the sidecar match HEAD |
| `v2/ecad/tools/gen_sch_a.py` | `3a1f6576`, 7f6c34697753bac1 | yes | title comment at line 1228 still describes "the BB-2590/U node" |
| `v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_sch` | `3a1f6576`, d6a25e63622e20da | yes | declared B21; the round 8 draft changes 1103 to 1227 parts, uncommitted |
| `v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net` (+ sidecar, intent) | `3a1f6576`; net 669d02d07aeaae4b, prov d7d029791bc7fd5c (generator eb5602ec41555d35), intent cf461c0b75ce368b | yes | sidecar files match HEAD |
| `v2/ecad/tools/gen_sch_b.py` | `3a1f6576`, dedaf34ce285e5ff | yes | STM32H743VIT6 at lines 281 to 289; U9 "DS3231MZ+" on a SOIC-8 land with C9866 at line 1047 |
| `v2/ecad/pcb-b-compute-b19/erc-allow.txt` | `25d72abd`, 9810934c1c03f745 | yes | explains 5 errors (3 pin_to_pin #FLG, 2 power_pin_not_driven J_SIM) |
| `v2/ecad/pcb-c-display-c8/pcb-c-display.kicad_sch` and `out/pcb-c-display.net` | `faf8c981`; sch 8591f93e40cff1b8, net 2834f0d8c4071d56; prov `3a1f6576` 838986d546e8b5b4 | yes | byte-identical to the native file in the C-C24 packet |
| `v2/ecad/pcb-d-aprs-d9/pcb-d-aprs.kicad_sch` and `out/pcb-d-aprs.net` | `458b2873`; sch 355d232002582471, net f13d8b70099ab03e; prov `3a1f6576` aa8faa090d221dc9 | yes | declared D12, title label D37P; differs from the superseded D-D12 packet |
| `v2/ecad/pcb-e1-dock-e7/pcb-e1-dock.kicad_sch` and `out/pcb-e1-dock.net` | `faf8c981`; sch 4b0438bec4a85b45, net d910e49c5f5f50b2; prov `3a1f6576` 50c0ec3f8cc12028 | yes | declared E17, title label E42P; byte-identical to the E-E17 packet; J_BATT still names the withdrawn BB-2590/U cable (`gen_sch_e.py` lines 192 to 193) |
| `v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_sch` and `out/pcb-p-pack.net` | `d90f30e4`; sch 2dba8588613db426, net 4342c4cbe1b43dc4; prov `3a1f6576` 438cd961c69a74fe | yes | P4; byte-identical to the battery packet's candidate |
| `v2/ecad/tools/boards/{a,b,c,d,e,p}.json` | a `1bf7fca1`, b `9bd0d629`, c `faf8c981`, d `14a43af7`, e `faf8c981`, p `a0ad97d9` | yes | phase fields A32, B21, C24, D12, E17, P4 differ from the title labels A65, D37P, E42P |
| shared inputs `kisch.py`, `intent.py`, `schlayout.py`, `idc_pads.py`, `meshsat.pretty/` | `3a1f6576`, `1df05d2c`, `d6dfbc7c`, `2ab96992`, `faf8c981` | yes | named in every sidecar |
| tools `build_sch.sh`, `full.sh`, `sch_prov.py`, `sch_pages.py`, `regen_compare.py`, `erc_gate.py`, `review_packet.py` | `458b2873`, `b4ee78ec`, `6104cb81`, `458b2873`, `6104cb81`, `b4ee78ec`, `ccf5808e` | yes | `build_sch.sh` writes PDF, BOM and ERC into `out/`, which `.gitignore` ignores |
| `v2/release/review-packets/C-C24-1f614233/`, `E-E17-1f614233/` | `ccf5808e` | yes (circuit) | readable PDF, BOM, ERC, part map; to be rebuilt before sending |
| `v2/docs/review-packets/battery/candidate/` | `d90f30e4` | yes | P's PDF, BOM and ERC report |
| `v2/release/review-packets/D-D12-1f614233/`, `P-P4-1f614233/` | `ccf5808e` | no | labelled SUPERSEDED |
| older PDFs under `v2/release/revA/boards/` and `v2/ecad/easyeda-pro/` | 6 to 17 September | no | none shows the committed A, B or D schematic |
| order-set BOMs under `v2/release/revA/order/` | 8 and 26 September | no | predate `faf8c981` |
| `v2/ecad/pcb-*/routed/erc_gate.verdict.json`, `pin_map_lands_<x>.verdict.json` | 21 September readings | no | taken on older netlists; the 26 September readings sit untracked |
| `v2/ecad/tools/pcb_board_holds.yaml` | `dd3b9074`, cdeac27ab5f7802d | yes | decision 31 holds on A, D, E at FABRICATION_RELEASE with `layout_entry_requires` |
| `v2/docs/reviews/INT-002-PRE-LAYOUT-ASSESSMENT.md` | `dd3b9074`, cad907b73c7ed8ea | yes | bound to net digest 262e8b039e833d02 on 669d02d07aeaae4b |
| `v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md` | absent | no | `pcb_board_holds.yaml` lines 62 to 63, 101 to 102, 146 to 147 pin sha256 null |
| `v2/docs/CURRENT-EVIDENCE.md`, `PCB-RULE-STATUS-{A,B,C,D,E,P,E5}.md` | `b9600c4a` | yes | rendered from untracked `v2/ecad/out/rule-audit/*.json` |
| `v2/release/revA/order/JLC-CERTIFIED.tsv` | `2aaa7b7f` | yes | 75 WRONG_MODEL rows |
| `v2/docs/records/r4a`, `r4b`, `r4e`, `r4p`, `r6d` | `428c697c` and later | yes | AI author and refuting-reviewer records of the round 4 to 6 corrections; they review the changes, not whole-board function; no W7 records filed |

**Acceptance items**

| # | Item | Met | Evidence |
|---|---|---|---|
| 8.1 | Current native schematic per board | yes | all six committed; each sidecar's schematic sha equals the file. They are the committed candidates only: round 8 rewrites all six, and the defects below stay open on them |
| 8.2 | Readable PDFs of the current schematics | no | PDFs of the exact committed schematic exist only for C, E (packets) and P (battery candidate); A, B, D have none. **Superseded in H1, see the integrator line:** A3-paged PDFs of all six committed schematics at `99cde56b` in `v2/release/handover/_generated/<board>/` (board B's is the pre-round-8 B21) |
| 8.3 | Generator inputs and source | yes | tracked; every file named in each sidecar matches HEAD. Gaps: no regeneration README (see `v2/docs/handover/REGENERATE.md`); the title labels A65, D37P, E42P undocumented |
| 8.4 | Netlists | yes | committed with sidecars and intent files for all six boards |
| 8.5 | BOMs | no | current only in the C and E packets and P's candidate; none for A, B, D. **Superseded in H1, see the integrator line:** two NOT_FOR_FAB BOMs per board for all six at `99cde56b` (`v2/release/handover/_generated/`); the MPN gap of layer 6 stands |
| 8.6 | Functional circuit reviews completed | no | no whole-board, function-by-function review for any board; rounds 4 to 6 reviewed the corrections (AI author plus AI refuter); R-BAT, R-PWR, R-HSD not done |
| 8.7 | Exact part and land mapping | no | SCH-005 readings are 21 September readings on older netlists (AWAITING_REVALIDATION). WRONG_MODEL on current parts: B U9 (SOIC-8 land, SOIC-16 code), B U80, A U1 suffix, amber LEDs coded yellow (B LED14, 24, 25, 34; D LED2, 5), JST plating variants (A J_HEAT, J_MAINSW; D J_VGG; E J_SMB; P J_TS2) and E's J_TAMP parser row. Mismatch persistence is not yet a checker input. (Board C's Q2 to Q4 are 2N7002 C8545 on the committed netlist and CERTIFIED; the table's WRONG_MODEL row for an "Si1308EDL class" switch dates from a board C generator before 12 September and does not apply) |
| 8.8 | Relevant ERC completed | no | **Superseded in H1, see the integrator line:** an ERC report of every committed schematic at `99cde56b` is in `v2/release/handover/_generated/` (B five errors, allow-listed, plus warnings; the rest warnings only); the ERC readings bound to the current schematics still await the re-take (REGENERATE.md section 9). At `e3aedb25`: no ERC report of the committed A and B schematics anywhere; C, D, E, P readings bound to the current schematic sit untracked and read TOOL_CHANGED; tracked ERC reports exist for C, E and P; only warnings except B's five allow-listed errors; the kicad-cli "annotation errors" warning on C, D, E, P exports is unexplained |
| 8.9 | Regeneration shown by regenerating and comparing | no | `3a1f6576`'s message reports PARITY on 36 artefacts (filed in H1.1 as `v2/docs/records/handover/3a1f6576-commit-message.txt`), but the compare outputs stayed on the build host; W7's parity record is not filed; only the battery packet files parity outputs. **Superseded in H1, see the integrator line:** regeneration of all six boards from a clean extraction read PARITY with the stated netlist hashes, and the parity reports are in `v2/release/handover/_generated/<board>/`; the usability check of H1 reproduced it on its own KiCad 9.0.9 host |
| 8.10 | Known schematic-affecting defects closed per board | no | open: TRN-001 FAIL on A and B (clamp symbol), PWR-003 FAIL on B, BAT-001 FAIL on P, FEA-002 EMCON items, FEA-003 FB-FAB-1 to 5 on B, FEA-001 U8, FEA-004 D flange sensor, FEA-006 G1 to G14 in all six generators, FEA-005 P coordination |
| 8.11 | Board-specific completion marked explicitly | no | this page did not exist at `e3aedb25` |
| 8.12 | Review D per board gates layout entry | no | none of its four items is complete for any board |
| 8.13 | Schematic-phase rules PASS on current-candidate evidence | no | 0 of 7 boards; every schematic-phase row AWAITING_REVALIDATION; 7 current readings in the set, all SGN-001 |
| 8.14 | Decision 31 `layout_entry_requires` on A, D, E | no | fitted parts met (A U31; D D9 to D14; E D9, D10); the review record absent; TRN-001 not a current PASS on any of the three |
| 8.15 | INT-002 pre-layout assessment on B's current nets | yes | PASS as a desk review (AI, not qualified) bound to the 48 nets; lapses if round 8 changes any of them |
| 8.16 | Review packet at each board's actual candidate | no | A and B never packaged; D and P packets superseded; C and E to be rebuilt |
| 8.17 | Condition 1: substitutions stay mismatches until proven | no | 75 WRONG_MODEL rows, several on current netlists; not a checker input yet |
| 8.18 | STM32H743 alignment (D-13, S-30) | yes | `gen_sch_b.py` lines 281 to 289 and the netlist carry STM32H743VIT6 C114409; S-30 closed at `458b2873`. V2-SPEC lines 82 and 135 still say H753 |

**Unresolved decisions**

| Decision | Downstream impact | Waits on later evidence |
|---|---|---|
| Board B U8 secure element | U8 part, land and bus; REQ-035; D-03; decision 30; R-SEC scope | yes (EQ-06) |
| SD-EMC-1 for the RM520N-GL: hardware supply removal in circuit (fallback iii) or bench E-05 first | B slot 2 circuit (buck enable, FULL_CARD_POWER_OFF#, discharge, supervisor) | no: FEA-002's layout-entry stage accepts either |
| B_PANEL_5V protection (PWR-003): MF-MSMF110 or a wider PANEL class | B F1 or the layout conductor class | no |
| Decision 29: keep the three CM5 Ethernet links capacitively coupled or fit magnetics | 24 capacitors against three magnetics on B; a respin if INT-003 fails | yes (EQ-09) |
| Board P second-level over-temperature coordination (62.7 to 77.5 C against 60 C; sensor placement and lag; behaviour with the primary failed) | U2 option, the R33 and R34 thermistor network, placement constraints, the BAT-001 table | no at desk; R-BAT can still change it (EQ-10) |
| SA868 keying inhibit: PTT-pin inhibit (no published threshold) or supply removal under EMCON | D exciter control, EMCON row 1 | no if supply gating is chosen |
| RockBLOCK 9704 under EMCON | B RockBLOCK control path | yes for the latency proof (EQ-02); the circuit remedy can be drawn now |
| Staging of R-PWR (A), R-BAT (P), R-HSD (B) against schematic completion and layout entry | whether A, B, P may enter layout before a qualified reviewer sees the schematic | no: staging is the session's; the reviews need the owner's authorisation. Recommendation: keep each qualified review a condition of layer 8 COMPLETE for its board, whatever layout-entry experiments are allowed |
| Phase naming: title labels A65, D37P, E42P against declared A32, D12, E17 | readability and byte-identical regeneration | no |

**Stage-gate cycles and remedies**
- Decision 31 (A, D, E): repaired in the registry (`pcb_board_holds.yaml` lines 15 to 35, 44, 84, 128 restage the
  holds to FABRICATION_RELEASE with desk-satisfiable `layout_entry_requires`; the fabrication hold stays). Remaining at
  layout entry: the review record `v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md` and TRN-001 PASS on the
  current netlist.
- INT-002 (B): repaired by the split (`pcb_rules.yaml` lines 1540 to 1609 make it a SCHEMATIC desk assessment; lines
  1615 to 1648 move the bench test to INT-003 at PROTOTYPE). Residual risk, not a cycle: the decisive unknown is
  carried to the built board with a respin fallback (EQ-09).
- PWR-001 and SI-001 (all six boards): LIVE cycle at `e3aedb25`. Both are schematic-phase layout-entry rules whose
  tools (`intent_checks.py`, `edge_length.py`) read only the board file, so their readings can be current only on a
  layout that carries the netlist (CURRENT-EVIDENCE lines 56 to 62). The session decided to teach the tools the
  netlist; that work is uncommitted.
- E5 INT-001: sequencing, not a cycle (E5 follows A's layout).
- FEA-001 (U8): not a cycle; the development-device test legitimately gates the part choice and needs a purchase.
- R-BAT and R-HSD staged at FABRICATION_RELEASE while ARCHITECTURE 14.2 and L-04, L-05 time them before layout:
  inconsistent staging, not a cycle. Letting layout start before a qualified schematic review risks rework, and does
  not make layer 8 COMPLETE.

**Next closing actions**
1. Integrate the round 8 board streams one at a time: regenerate on a KiCad 9.0.9 host, compare with `regen_compare.py`
   and a netlist diff against each stream's expected-change list, file the parity and diff outputs under
   `v2/docs/records/r8<x>/`. This closes, among others, B's FAB-01 to FAB-04, L1 to L3, L7, SD-EMC-1 and 2, S-12, S-13,
   F1 and G4 to G10; C's L1, SD-EMC-6, G9, G13, G14; D's L4, flange sensor, G12, G14; A's U26 gates and G1 to G3; E's
   G11, G13, G14 and VIN_RAW; P's G8. Integrator with the board streams; one pass per board.
2. Merge the tools that remove the live cycle and keep mismatches: ts-net (PWR-001 and SI-001 on the netlist) and
   r8cert (`jlc-mismatch.yaml` as a checker input with fixtures). Tools stream, then integrator.
3. One consolidated re-take, in a clean clone at the merged revision on a KiCad 9.0.9 host, of every schematic-phase
   reading per board (ERC with `--run`, safe lines, pin map and lands, derating, power sequence, energy chain, port
   protection, clocks, contracts and interfaces, pack protection, and the netlist-based PWR-001 and SI-001); commit the
   verdicts and ERC reports to a tracked location; re-render the pages. After actions 1 and 2; one host session.
4. Update `pcb_pack_protection.yaml` to the drawn second level (U2 BQ7720700) and chemical fuse (F2 SCF9550); re-take
   BAT-001; write the secondary over-temperature coordination against 60 C with placement and lag constraints. Battery
   stream and board P stream; after r8p.
5. Write `v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md` for A, D and E on the merged netlists (every exposed
   conductor, the first part met, the clamp rating against decision 34's transient level, placement and return-path
   constraints), labelled as the session's desk review; pin its sha256 and the netlist sha in `pcb_board_holds.yaml`.
   Board streams A, D, E with the holds writer; after round 8.
6. Build review packets with `review_packet.py` at the merged revision (A and B for the first time, D, P beside the
   battery packet, rebuilt C and E), each with the paged PDF, native files, NOT_FOR_FAB BOM, part map, change report
   and contracts; label the older folders superseded. Review stream; KiCad host with `mupdf-tools`.
7. Write a per-board functional circuit review record by function (power entry and protection, rails and sequencing,
   clocks, straps and boot pins, each interface against its contract, EMCON and safety lines, test access) by an agent
   that did not write the board, bound to the netlist sha and labelled AI review (`v2/docs/reviews/CIRCUIT-REVIEW-<x>.md`).
   It does not replace R-BAT, R-PWR or R-HSD. After round 8.
8. Resolve part and land mismatches on the current netlists by changing the code or filing a proven compatibility
   entry (B U9, B U80, amber LED codes, JST plating variants, A U1). Parts stream with the board streams; after r8cert.
9. Fix the stale generator strings (`gen_sch_a.py` line 1228, `gen_sch_e.py` lines 192 to 193, `gen_sch_b.py` lines 643
   and 1160); align the title-block PHASE with `boards/*.json` or document the key; identify the symbol behind the
   "annotation errors" warning. Board streams.
10. Correct V2-SPEC lines 82 and 135 and EXECUTION-PLAN line 92 (H743 since `458b2873`); reconcile ARCHITECTURE 14.2
    with FEA-005's stages and L-04 as a recorded session ruling. Integrator.
11. File W7's records (`w7-regen-parity.md`, `w7-skips.md`, `w7-holds.md`, `w7-dispositions.md`) under
    `v2/docs/records/w7/`; commit the regeneration parity outputs of the current revision. Records stream.
12. Keep the schematic regeneration guide current (`v2/docs/handover/REGENERATE.md`) with the per-board commands, the
    PHASE per board, parity and expected shas; update the per-board rows here. Integrator; after round 8 for the shas.
13. **Needs the owner (spend and outside contact):** commission R-PWR and R-HSD, engage R-BAT, buy the Z-EXP bench parts
    (L-06); optionally ask Raspberry Pi or Broadcom about the CM5 PHY under capacitive coupling. The session prepares
    texts only.

**Per board.**
- A (`pcb-a-power-a23`, declared A32, title A65): NOT COMPLETE. Schematic d2360d48 and netlist 7b085101 committed with a
  matching sidecar; no PDF, BOM, ERC or review packet of this schematic anywhere. TRN-001 reads FAIL on an older netlist
  (the PASS on this netlist is claimed only in `3a1f6576`'s message). Open: decision 31 review; EMCON L1, L2, L4 at
  U26; G1 to G3; the stale BB-2590/U title; WRONG_MODEL on U1, J_HEAT, J_MAINSW. R-PWR required before layout (L-04)
  and not approved. Review so far AI only.
- B (`pcb-b-compute-b19`, B21): NOT COMPLETE, the most open board. No current PDF, BOM or packet; ERC last taken on a
  superseded schematic. FAIL: TRN-001 (older netlist), PWR-003. Open: FAB-01 to FAB-04; EMCON L1 to L3, L7, SD-EMC-1 and
  2; S-12; S-13; G4 to G10; U9; U80. Blocked: U8 (EQ-06) and R-HSD (EQ-12). INT-002 PASS is an AI desk review tied to
  48 nets round 8 may change.
- C (`pcb-c-display-c8`, C24): NOT COMPLETE, the closest board. PDF, BOM and ERC in the C-C24 packet (rebuild for the
  current SOURCES.yaml). Open: EMCON L1 (U3 GPIO21 on EMCON_HW), the SD-EMC-6 lamp, G9, G13, G14. Readings await
  revalidation. Review so far AI change review only.
- D (`pcb-d-aprs-d9`, declared D12, title D37P): NOT COMPLETE. No PDF, BOM or packet in the tree; current ERC untracked.
  Decision 31 review absent (fitted parts met). Open: EMCON L4; the SA868 PTT threshold; the flange sensor; G12, G14;
  WRONG_MODEL on J_VGG and the LEDs. RF-002 PASS comes from a contract reading while end-to-end EMCON is open.
- E (`pcb-e1-dock-e7`, declared E17, title E42P): NOT COMPLETE. PDF, BOM and ERC in the E-E17 packet (rebuild).
  Decision 31 review absent. Open: G11, G13, G14; VIN_RAW (R4A-N12); the J_BATT text; WRONG_MODEL on J_SMB and J_TAMP.
  Its hold forbids publication of the board file while the repository is public (a contradiction to resolve).
- P (`pcb-p-pack-p2`, P4): NOT COMPLETE. PDF, BOM and ERC in the battery candidate. BAT-001 FAIL because
  `pcb_pack_protection.yaml` still declares no second protector and no fuse. Open: secondary coordination against
  60 C, G8, WRONG_MODEL on J_TS2. R-BAT (D-09) not engaged and can change the circuit.
- E5 (`pcb-e5-block`): NOT APPLICABLE to layer 8 (no schematic by construction); its contract binds once A's layout
  carries A's netlist.

> **INTEGRATOR LINE, layer 8:** status at `e3aedb25` IN_PROGRESS; status now: IN_PROGRESS; as of commit: H1; per board: A open (round 8 regenerated, `c0133147`; PWR-001 FAIL on current evidence, EQ-19; +3V3 window, EQ-17), B open (round 8 NOT merged, in `fnd/r8b`, exported in H1.1 as `v2/docs/handover/candidates/r8b.patch`, EQ-20; PWR-001 FAIL on current evidence, 28 supplies undeclared), C open (round 8 regenerated, `9f28c238`, netlist `11eabc2d`; PWR-001 and SI-001 read on the older netlist; RF-002 undecided on U14, EQ-18), D open (round 8, `76235aad`; PWR-001 FAIL on current evidence), E open (round 8, `bc0f562f`; PWR-001 FAIL on current evidence; HC9-E1, S-47, the LT8705A sense resistor in the inductor leg, blocks layout entry), P open (round 8, `7bef62bd`, netlist `085f8333`; BAT-F20, EQ-15; PWR-001 and SI-001 awaiting the re-take), E5 not applicable; items closed since `e3aedb25`: readable paged PDFs, two NOT_FOR_FAB BOMs, ERC and netlist parity of all six boards at `99cde56b` with provenance, and regeneration PARITY of all six from a clean extraction (`v2/release/handover/_generated/`, REGENERATE.md sections 4 and 5). Remaining: board B's round 8 merged with parity; the consolidated re-take of every schematic-phase reading on the committed netlists; PWR-001's supply declarations on A, B, D and E; the per-board functional circuit reviews; HC9-E1 on E; BAT-F20 on P; the qualified reviews (EQ-10 to EQ-12). **H2 (27 September 2026, board B's round 8, set 5 and the consolidated re-take):** still IN_PROGRESS on every board. Landed since H1: board B's round 8 (`b76c18cb`, integrated in `cc3313f3`); set 5 on A (`ffca0771`), B (`caba1876`), D and E (`b7f96784`), each regenerated with parity; the consolidated re-take of every schematic-phase reading on the committed netlists (`8ea7867e`: 83 readings on seven boards, layout-entry reasons 101 to 40); the H2 exports of A, B, D and E with regeneration PARITY on all six (`c5d09c78`). PWR-001 on current evidence: A and B PASS, D and E INCONCLUSIVE (S-76), C and P FAIL (power nets no rail declares). S-47's core (the tracker's sense on its bottom leg) is drawn (SC-56), its item 10 open. The per-board layout-entry reasons and what remains are the H2 section's table and row for layer 8. Owner: the board streams and the integrator.

### A.9 Layer 9. Pre-layout design analysis (the audit at `e3aedb25` and the edition history)

**Status at `e3aedb25`: IN_PROGRESS.** Substantial pre-layout analysis exists and is honestly labelled: a reproducible
power model, decision 42's per-class decoupling ruling, a stackup measurement for every board, INT-002's desk
assessment, board A's converter record and a costed thermal experiment. None of it is bound to the netlists round 8
is producing, and its own rulings are not written into the registries the tools read (PWR-F12, part temperatures,
DEC-001). Board B's and board P's stackups and board A's copper weight are undecided, no per-board constraint set for
layout exists, and the thermal bound on the typical mode includes failure. Most closing actions are doable now; the
physical, price and outside-contact items are blocked and written as questions.

**Scope.** Current calculations and models, with assumptions, margins and sensitivities, for power, energy,
protection, thermal, signal, timing and placement, per board; the stackup per board (P0 rule; decisions 7, 27, 28,
35, 43); the constraints handed to layout, written per board; and the analyses that need routed geometry or hardware,
named and allocated. Excludes post-layout SI and physical verification.

**Prerequisites.** Layer 8 schematics current per board (every netlist-bound analysis is re-read after round 8,
EXECUTION-PLAN line 25); layer 5 currents and contracts; layer 6 parts where the analysis depends on them (R17's
sheet, NVMe, fans, U8, MLCC DC-bias curves); layer 7 outlines, pack location, PA flange site, conductance inputs;
layer 2 envelope and modes; decisions 7, 27, 28, 35, 42, 43, 46 and the PWR-F12, F14, F15 session rulings.

**Deliverables**

| File | Revision (commit, sha256/16) | Current | Note |
|---|---|---|---|
| `v2/docs/feasibility/POWER-THERMAL.md` | `428c697c`, bb9c861c9920c8d6 | no | PROVISIONAL; anchored at `01469100`; tables computed on the `1f614233` boards; its integrator items 1 to 10 (lines 1140 to 1190) not executed |
| `v2/docs/records/rv-pwr/pwr_budget.py` (+ `.out`, `.json`) | `428c697c`, 469d0820b046ef6f | no | re-run byte-identical, so the path reproduces; but it encodes rail declarations transcribed from `1f614233` generators |
| `v2/docs/records/rv-pwr/pwr-chain-redeclaration.yaml` | `428c697c`, 039c72aa6f451dbd | no | draft PWR-F12 re-declaration, not in the registries |
| `v2/docs/records/rv-pwr/pwr-part-temps-rows.yaml` | `428c697c`, cee34b52c6b45259 | no | draft rows, not merged |
| `v2/docs/feasibility/DECOUPLING.md` | `428c697c`, 15915adb18843695 | yes | the ruling is current; nothing implemented (DEC-001 text unchanged; `gen_sch_d.py` line 458 still fits 1 uF; `gen_sch_b.py` line 1124 ties VDDA to 3.3 V) |
| `v2/docs/records/rv-dec/` | `428c697c` | yes | measurements on the pre-correction boards |
| `v2/docs/records/r4a/r4-decisions.md`, `r4-open-items.md` | `428c697c` | yes | board A's seven LM5176 stage compensations, ripple, soft start, restart guard; the scripts and runs behind it are not in the tree |
| `v2/ecad/tools/pcb_energy_chain.yaml` | `c161b3d8`, 935e524eed0ee4d1 | no | every pack stage 10 A continuous and 18 A peak with no duration; no F2 stage |
| `v2/ecad/tools/pcb_pack_protection.yaml` | `4fbfa479`, 03dc766d99cf03f7 | no | 10 A and 18 A without duration |
| `v2/ecad/tools/pcb_envelope.yaml` | `9a151c78`, bc78efbf633223b5 | no | inside-air rise 10 and 16 K, below POWER-THERMAL 9.1's own bounds |
| `v2/ecad/tools/pcb_part_temps.yaml` + `part_temps.py` | `0ec34ce0` | no | hot bar 51 C from the old estimate; AW7915-AED, LimeSDR, F2, the PA absent |
| `v2/ecad/tools/pcb_fuse_derating.yaml` | `e6b2026b` | yes | no row for F2 |
| `track_current.py`, `power_copper.py`, `dc_drop.py`, `via_current.py` | `06c9eda0` | yes | decision 35's conservative current model; `dc_drop` and `via_current` judge routed boards only |
| `impedance_check.py`, `impedance_2d.py` | `e392598b`, `63e3fbf3` | yes | no solve yet on JLC08161H-2116 or option A2 for B |
| `thermal.py`, `edge_length.py`, `place_audit.py`, `region_room.py`, `derate.py`, `energy_chain.py` | various | yes | `thermal.py` computes no junction temperature; `edge_length.py` reads only the board file; `derate.py` has no DC-bias derating |
| `v2/ecad/tools/stackup_write.py` (STACKS) | `d468613e`, b55a3c0f58c805c2 | yes | rows JLC04161H-7628, JLC06161H-3313, 2L, 2L-2oz, JLC04162H-7628 (P), JLC08161H-2116 (B experiment); P's inner copper weight not chosen |
| `v2/docs/LAYER-DECISIONS-2026-09-11.md` | `445d7623`, 2149ce06635566bb | no | predates decisions 27, 28, 43: says B six "stands", C four and P two "decided" |
| `v2/ecad/tools/pcb_decisions.yaml` | `31ce3840` | yes | decision 46 accepts gate-drive lengths measured on the obsolete A98 board |
| `v2/ecad/tools/boards/{a,b,c,d,e,p,e5}.json` | various | no | `a.json` and `c.json` layer rationales contradict the record; `rise_ns` absent on A, E, P |
| `v2/docs/reviews/INT-002-PRE-LAYOUT-ASSESSMENT.md` | `dd3b9074` | yes | "defensible to lay out; not shown to work" |
| `v2/docs/B-FEASIBILITY.md` and the Q-B-ESC-1 results | `4cd20d54` | yes | stack facts, Q-B-ESC-1, Q-B-ESC-2 specification |
| `v2/docs/feasibility/FAILOVER-FABRIC.md` | `428c697c` | no | read on a round 6 candidate; FB-FAB-7 channel budgets absent |
| `v2/docs/CURRENT-EVIDENCE.md` | `b9600c4a` | yes | 0 of 7 boards ready; A 16, B 16, C 10, D 15, E 15, P 14, E5 6 blocker lines |
| `v2/docs/records/w4/`, `v2/docs/reviews/READY-TO-ACT.md`, `v2/vendor/fabricator/` | `428c697c`, `6ba28392`, `d468613e` | yes | independent conductance bound; costed tests; fabricator stack and capability sources |
| EMCON.md 5a and `records/rv-zer/zeroize/zer_budget.py` | `a6f87e9d`, `428c697c` | yes | EMCON latency and ZEROIZE time budget; REQ-071 reads FAIL until the circuits are drawn |

**Acceptance items**

| # | Item | Met | Evidence |
|---|---|---|---|
| 9.1 | Current power calculations with assumptions, margins and sensitivities | no | POWER-THERMAL 1 to 5 and `pwr_budget.py` give LOW, PLAN, HIGH per load and reproduce, but model the `1f614233` boards; declarations below makers' figures stand (PWR-F01 card rail 1.5 A against 3.0 A; PWR-F03 KSZ 0.8 A against 1.21 A); A's compensation scripts not in the tree |
| 9.2 | Current energy calculations with sensitivities | no | 2.5 h and 1.7 h aged with bounds; "aged" TBD; CONOPS still carries the old figures |
| 9.3 | Protection coordination on the current design | no | PWR-F12 only in prose and a draft; the chain and protection registries unchanged; PWR-003 FAIL on B, BAT-001 FAIL on P; the decision 31 review record absent |
| 9.4 | Thermal analysis current; a bound that includes failure not closed by a label | no | cells 45.4 to 81.3 C in PS-TYP at +20 C against 60 C; AP2112K supervisor LDO +152 K at 400 MHz, past 150 C; PA flange 95 to 118 C for a 60 s key-down; conductance unmeasured; THM-001 INCONCLUSIVE everywhere |
| 9.5 | Signal analysis pre-layout (SI classes, impedance on the chosen stack, channel budgets) | no | SI-001 INCONCLUSIVE on all six; `rise_ns` undeclared on A, E, P; IMP-001 INCONCLUSIVE; B inner pairs 140.5 ohm against 100; no channel budget for PCIe upstream, USB 3 failover (up to 255 mm) or HDMI (up to 396 mm) |
| 9.6 | Timing analysis (sequencing, break-before-make, EMCON latency, ZEROIZE, clocks) | no | PWR-002 and CLK-001 AWAITING_REVALIDATION; FB-FAB-4 break-before-make budget OPEN; REQ-071 FAIL until drawn; ZEROIZE budget present |
| 9.7 | Placement constraints analysed | no | decision 42 ruled but not landed; B floor-plan study not done; PLC-001 FAIL on A32 and B21; decision 46 accepted on A98; P's thermistor and sense placement not written |
| 9.8 | Constraints handed to layout written per board | no | no per-board constraint document; constraints scattered over `boards/*.json`, intents, `pcb_interfaces.yaml`, `pcb_sensitive.yaml`, `pcb_emc.yaml`, the feasibility pages and the appendix; A's 18 A width, B_PANEL_5V width, RF-001 remediation, ISO-001 creepage on A and E, the PA flange site not written as constraints |
| 9.9 | Analyses needing routed geometry named and allocated | yes | `pcb_rules.yaml` phases (PLACED_BOARD: DEC-001, THM-001, PLC-001, ANA-001; ROUTED_BOARD: PI-001 to 003, IMP-001, PAIR-001, RET-*, ISO-001, RF-001, STK-001); FEA fabrication stages |
| 9.10 | Analyses needing hardware named and allocated in the test plan | no | named in POWER-THERMAL 10, INT-003, EMCON E-01 to E-12, IOHA A1 to A14, but TEST-PLAN lacks the heat-balance and rise tests, and E3's pass line conflicts with POWER-THERMAL 9.2 and D-02a |
| 9.11 | Pre-layout portion without claiming post-layout or physical verification | yes | labelling throughout (CURRENT-EVIDENCE line 6; POWER-THERMAL line 3; INT-002 section 7; desk reviews labelled as not qualified) |
| 9.12 | Stackup decided per board with measurement and cost (P0 rule, STK-002) | no | B undecided (six re-assigned, unsolved, or eight, run not started); A's copper weight for 18 A undecided; C six ruled but not regenerated; P four at 2 oz with inner weight not chosen; no price for any board |
| 9.13 | Every board passes the staged layout-entry test | no | 0 of 7; 92 blocker lines |
| 9.14 | FEA-004 layout-entry stage (A, D) closed at desk | no | PWR-F12 not in registries; A's 18 A constraint not derived; the flange sensor not on D's netlist |
| 9.15 | FEA-006 layout-entry stage (A, B, C, D, E, P) closed | no | T1 to T10 and G1 to G14 not on main; the Diodes question unsent |
| 9.16 | FEA-003 (B) and FEA-005 (P) layout-entry stages | no | FB-FAB-1 to 5 open; Q-B-ESC-2 not run; FB-FAB-7 budgets absent; P's coordination and placement constraints not stated |
| 9.17 | INT-002 current on its 48 nets | yes | DESK_REVIEW PASS bound to 669d02d07aeaae4b; AI review, labelled |
| 9.18 | CMP-001 includes DC-bias derating of every storage or filter MLCC | no | `derate.py` lines 19 to 21 record the gap; DECOUPLING section 10 "TBD" |
| 9.19 | Required qualified reviews preserved; AI review labelled | no | labelling met; R-PWR and R-HSD unapproved and staged differently across REVIEW-ROUTES, ARCHITECTURE 14.2 and EXECUTION-PLAN lines 118 to 126 |
| 9.20 | A representative calculation can be re-run from the repository alone | no | `pwr_budget.py` yes; A's converter calculations no (scripts only in drafts); most tools need `pcbnew` |

**Unresolved decisions**

| Decision | Downstream impact | Waits on later evidence |
|---|---|---|
| Board B stackup: six layers re-assigned (A2, In3 as GND) or eight (JLC08161H-2116), with layer use and pair widths | B's pair widths, impedance classes, vias, escape strategy, thickness, price, every routed rule; FEA-003 | yes (EQ-01); the `impedance_2d` solves for A2 and eight layers are desk work that can come first |
| Board A pack-path copper weight (1 oz or 2 oz outer) and width at 18 A for 60 s | A's stackup code and price, power band geometry around CELL+, CELL_FUSED, VBAT, R17 | no: decision 35's model gives 23.91 mm at 1 oz outer or 11.95 mm at 2 oz (inner layers need 85 to 170 mm); a 60 s transient calculation may relax it; only the 2 oz price is the owner's |
| Board P inner copper weight on the four-layer 2 oz stack | P current density, price, STK-001 | no |
| Enclosure conductance: whether PS-TYP with three modules is sustainable from +20 C, and the C1 and C2 thresholds | three-module redundancy in the heat (a core function), pack and hot-part placement, fans, the +25 and +35 C restrictions, REQ-014 | yes (EQ-05) |
| F2 margin at 18 A for 60 s from +55 C, which sets K2 and the key-down duration | REQ-018, K1 and K2, P's release, the pack protection test | yes (EQ-07) |
| Whether decision 46's gate-drive acceptance carries into A's next layout | A converter placement, EMI, R-PWR scope | no: TI's layout guidance (controller between its FETs) can be written as the constraint now |
| B's transformerless links: a magnetics footprint option or a respin fallback; the coupling capacitors' rating | B parts and area, INT-003 fallback cost | no (EQ-09 for the underlying unknown) |
| R-PWR staging | A's layout entry | no; the spend is the owner's (EQ-11) |
| Edge rates (`rise_ns`) for A, E, P; per-device decoupling distance for classes D and L | SI-001, terminations, DEC-001 | no |
| Layer-count prices (4, 6, 8) per board at real outline and quantity 5 | STK-002 on all seven boards; decision 27's "six if the price is close" | yes (EQ-14) |

**Stage-gate cycles and remedies**
- No layout-entry check that a stackup is decided (STK-001 is ROUTED_BOARD, STK-002 RELEASE_PACKAGE), although the
  owner's section 5 names the stackup as a layout-entry input: a check applied too late. Remedy: a layout-entry
  stackup check.
- IMP-001 exists only at ROUTED_BOARD; "can the chosen stack meet the pair targets" has no layout-entry gate. Remedy:
  a pre-layout impedance feasibility check per pair class.
- THM-001 is PLACED_BOARD; the per-part dissipation that sets hot-part copper has no pre-layout stage, and
  `thermal.py` computes no junction temperature.
- FEA-004's heat test deferred past layout entry while pack placement and the three-module claim depend on it (as in
  layer 4).
- PWR-001 and SI-001 read only board files (the live cycle of layer 8), open until the tools stream merges.
- FEA-003's need for "the stack decision 43 selects" is a legitimate bounded experiment, provided it stays
  EXPERIMENTAL with caps; it has not started.
- Decision 31 and INT-002 are split correctly; the decision 31 review record does not exist; the BCM54210PE question
  can still change B's parts after build, with a respin as the only recorded fallback.

**Next closing actions**
1. Write PWR-F12 into `pcb_energy_chain.yaml` and `pcb_pack_protection.yaml` (10 A continuous held by C2 and C3, 18 A for
   60 s, 20 A for 2 s, F2 as a stage with its unknown derating stated); re-take energy chain and pack protection on the
   committed netlists. Battery stream with the integrator; after the P and A merges; half a day plus a re-take.
2. Derive A's pack-path copper constraint at 18 A for 60 s under decision 35 with a transient calculation; take the
   copper-weight decision; correct PWR-F12's 16.18 and 8.09 mm figures in POWER-THERMAL. Board A stream; none (the 2 oz
   price goes to the owner only if 2 oz is the answer).
3. Re-run `pwr_budget.py` on the round 8 declarations and re-anchor POWER-THERMAL; file the model beside its page as
   `v2/docs/feasibility/power_thermal_model.py`. Power stream; after round 8.
4. Execute POWER-THERMAL's integrator items 1, 3, 4 and 10 (CONOPS figures; OPERATING-ENVELOPE +25 and +35 C as proposed
   controls; re-pin `pcb_envelope.yaml` so the part-temperature hot bar is not the 7 September estimate; add the
   AW7915-AED, LimeSDR, cells, F2 and RA30H1317M1 rows and replace the PCB-LIS1A15 row). Integrator.
5. Land decision 42: T1 to T10 in the tools and DEC-001's text, G1 to G14 in the generators, and a DC-bias
   effective-capacitance table for class L and B1 parts from maker curves. Tools stream and board streams; after round 8.
6. Bring the stackup record current: a per-board stackup decision table (code, layer use, copper weights, measurement,
   price status) superseding LAYER-DECISIONS-2026-09-11's summary; correct `boards/a.json` and `boards/c.json` and the
   STK-002 coverage reason; choose P's inner copper weight; run `impedance_2d` on JLC06161H-3313 with In3 as GND (A2) and
   on JLC08161H-2116 for B's layer assignment and pair widths. Integrator and board B stream; `reserved.json` floor edits
   only under decisions 28 and 43.
7. Add a layout-entry stackup check and a pre-layout impedance feasibility check per pair class to the registry.
   Registry writer.
8. Write one layout constraint sheet per board (A, B, C, D, E, P, E5) as a view over the registries (stackup and layer
   use; power band widths at declared currents, including A's 18 A path and B_PANEL_5V at least 0.78 mm at 1 oz or
   MF-MSMF110; pair targets and budgets, the CM5's 0.15 mm; decoupling class seats; sensitive-node keep-outs; creepage
   for A's and E's high-voltage nets; RF path rules; hot parts, including the PA flange site, the LDOs and the LM5176
   seated between its FETs per SNVSAI1D; protection clamps at the entry with a short ground return; P's thermistor and
   sense placement; the analyses owed at PLACED, ROUTED and PROTOTYPE). Integrator with each board stream; after round 8
   and action 6; one to two days.
9. Write `v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md` (as layer 8 action 5).
10. SI-001 pre-layout: merge the netlist-reading tools, declare `rise_ns` per class for A, E and P from datasheets,
    re-take. Tools stream; after the ts-net merge.
11. Write B's channel budgets per link (PCIe upstream, USB 3 home and failover through the TMUXHS4212, HDMI through two
    TS3DV642, LimeSDR, Ethernet) from primary documents, against FAILOVER-FABRIC 8.3's lengths; re-read the fabric map
    on the committed netlist. Board B stream; specifications not held may need access.
12. File A's converter calculation scripts and runs (`loop_design.py`, `bulk_ripple.py`, `ripple_dense.py`,
    `softstart.py`, `restart.py`, `comp9_corners.py`, the loop and ripple runs) into `v2/docs/records/r4a/`. Records
    writer with the board A and tools owners.
13. Reconcile R-PWR's stage across REVIEW-ROUTES, ARCHITECTURE 14.2, EXECUTION-PLAN and the registry. Integrator.
14. Reopen decision 46 for A's next layout: write TI's layout guidance as a placement constraint, or record why the A98
    acceptance holds on the corrected netlist. Board A stream.
15. INT-002 follow-ups: decide a magnetics footprint provision or record the respin fallback with its cost; state the
    coupling capacitors' voltage and dielectric; prepare (not send) the Raspberry Pi or Broadcom question. Board B
    stream; after r8b (`candidates/r8b.patch`; re-pin the 48-net digest).
16. TEST-PLAN: add the heat-balance, lid-open and lid-closed rise and PA patch tests; rewrite E3's pass line to D-02a's
    two lines with POWER-THERMAL 9.2's ceilings. Test-plan owner.
17. One re-take of every schematic-phase reading on the committed round 8 netlists in a clean clone (as layer 8
    action 3).
18. **Needs the owner (purchase and hands):** the empty-case heat-balance test (EQ-05).
19. **Needs the owner (outside contact or purchase):** F2's behaviour above +60 C at 18 A from Eaton, or a coupon test
    (EQ-07).
20. **Needs the owner's ordering session:** like-for-like layer-count prices per board (EQ-14).

**Per board.**
- A (A32; netlist 7b08510106687b3d; board 58e26c67987b1daa predates it, SCH-002 FAIL): 16 blocker lines. Power: seven
  LM5176 stages analysed (scripts not in the tree); PWR-F02 slot 1 at 4.65 of 5 A; the pack path at 18 A needs 23.91 mm
  at 1 oz outer or 11.95 mm at 2 oz, not written; R17 1.62 W on a 3 W part with no sheet. Stackup: six layers measured
  (the four-layer arm left 345 unrouted), copper weight open, no price. Placement: decision 46 on A98; G1 to G3; RF-001
  (11 RF paths) and ISO-001 (5 below limit on 6 high-voltage nets) not written as constraints. R-PWR staging
  contradictory.
- B (B21; 669d02d07aeaae4b; B21's board 416 unrouted, predates the netlist): 16 lines. Stackup undecided (six-layer
  inner pairs 140.5 ohm; A2 unsolved; the eight-layer row's layer use TBD; Q-B-ESC-1 INCONCLUSIVE; Q-B-ESC-2 and decision
  43's run not started). Signal: no channel budget for PCIe upstream (118 to 140 mm), USB 3 failover (up to 255 mm plus a
  mux), HDMI (up to 396 mm through two switches), LimeSDR (217 mm); INT-003 at prototype. Power and thermal: PWR-F01,
  F03, F05; AP2112K supervisor LDO +152 K at 400 MHz (PWR-F04: a firmware clock bound or a 3.3 V feed); PWR-003 FAIL;
  KSZ9897R +28.7 K; T1 H5007NL 0 to +70 C. Placement: PLC-001 FAIL 13 of 75 on B21; G4 to G7, G10; floor-plan study owed.
- C (C24; 2834f0d8c4071d56): 10 lines. Six layers ruled (decision 27, from RET-001 and RET-002 failing on 15 B.Cu nets at
  four) but not regenerated; no price. Two low-current rails; `rise_ns` 4.0 on two classes; no thermal item named.
- D (D12; f13d8b70099ab03e): 15 lines. Four layers on the RF ground-plane reason. A 60 s key-down from a +50 C plate
  reaches 95 to 118 C against the maker's 90 C and +100 C; the flange sensor not on the netlist; the PA flange site an
  unwritten thermal constraint. G12: the TPA6132A2 still at 1 uF against the maker's 2.2 uF within 5 mm. PI-003 FAIL on
  D12.
- E (E17; d910e49c5f5f50b2): 15 lines. Four layers kept on routing and In1 (the power half refuted by the In2
  experiment). On E17: PI-001 FAIL (7 missed), ISO-001 FAIL (92 below limit on 8 high-voltage nets), ANA-001 FAIL, none
  written as constraints for the next layout. `rise_ns` absent; always-on drain 0.2 to 1.7 W TBD.
- P (two-layer P4; 4342c4cbe1b43dc4): 14 lines. FEA-005 (coordination and placement constraints; O-11 re-placement with
  J_TS2, R34, TP15); G8; BAT-001 FAIL. Four layers at 2 oz ruled (JLC04162H-7628), inner weight not chosen, not
  regenerated. F2 at 18 A for 60 s from +55 C unproven and absent from the energy chain.
- E5 (no schematic; board 686b29a734c55b9a): 6 lines. 2L-2oz by decision 7; STK-001 FAIL on the board file's Dk 4.6
  against the record's 4.5. It carries the pack current through its contacts, so the 18 A for 60 s re-declaration
  applies; the mate test of its contact targets at prototype.

> **INTEGRATOR LINE, layer 9:** status at `e3aedb25` IN_PROGRESS; status now: IN_PROGRESS; as of commit: H1; items closed since `e3aedb25`: per-board layout constraint sheets A, B, C, D, E, E5 and P with their calculations (`v2/docs/layout-constraints/`) and the stackup decision record (`v2/docs/STACKUP-DECISIONS.md`) (hc9; second review, an AI review, PASS_WITH_FIXES, its two blocking wording items fixed at merge); PWR-001 and SI-001 read on the netlists and RF-002 on every board (round 8 set 2); per-board constraint sheets: A, B, C, D, E, E5, P. Remaining: HC9-E1 (S-47) on board E before its layout entry; the drafts hc9 left for other owners in `fnd/hc9` (`apply_power_thermal.py`, `apply_boards_rationales.py`, `apply_coverage_stk002.py`, `apply_pcb_emc_u5_basis.py`, the draft rules STK-003 and IMP-003), each with its re-take; board E's pack-path bands declared 2 oz in the energy chain while board E is 1 oz; PWR-F12 at 18 A for 60 s on boards E, E5 and P; the heat test (EQ-05), F2 (EQ-07), prices (EQ-14) and channel budgets (EQ-12). **H2 (27 September 2026, the consolidated re-take):** still IN_PROGRESS. PWR-001 and SI-001 are read on the committed netlists of every board and are current; SI-001 reads INCONCLUSIVE on all six boards with a schematic (at the re-take A 114 of 290 signal nets undecided, B 532 of 882, C 33 of 134, D 27 of 135, E 37 of 82, P 22 of 44) because the drivers' makers publish no edge rate for most classes: the edge-rate declarations are owed (a stated bound per class, or a bring-up measurement). HC9-E1's core is drawn (S-47, SC-56). What remains is the H2 section's row for layer 9. Owner: the integrator and the board streams.
