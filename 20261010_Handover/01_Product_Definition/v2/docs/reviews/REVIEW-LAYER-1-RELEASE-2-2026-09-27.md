# AI review (not a qualified engineering review)

## Layer 1 (vision, product definition and pitch): second release check at `eb9f9030`, 27 September 2026

MESHSAT-1357. **Commit judged: `eb9f9030989de925d6569bc00a846568fa4d300b`**, branch `fnd/rel2` (two commits, `d535c17e` and
`eb9f9030`, on `953f5658`, not pushed), read in its worktree between 15:00 and 15:10 CEST; `git status` was
clean before and after every check, and nothing in the tree was edited except this record.

Reviewer: one AI reviewer session that wrote none of the files judged, did not assemble them, did not hold the first
release check (`REVIEW-LAYER-1-RELEASE-2026-09-27.md`) and took no part in Review A's passes. This is an AI review,
labelled as one. It is not a qualified engineering review; no record in this tree requires a qualified review of layer
1 (SC-16), and this record does not stand in for any qualified review the tree does require (D-09,
`v2/docs/reviews/REVIEW-ROUTES.md`). Prototype design: nothing in this kit has been built, ordered, powered or
measured, and nothing below is a physical result.

**The question.** Does layer 1 meet the owner's COMPLETE test (`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`
sections 2 and 3) at this commit: every acceptance item met with evidence; consistent with the other layers' current
files; no missing decision of this layer that can change architecture, interface, component, outline or protection;
open feasibility questions allocated to the layer that owns them and not hidden; nothing lowered, dropped, weakened or
narrowed; session choices marked as the session's; the required review; a versioned package? A layer is not held open by
a later board's work, but it may not hide a blocker.

**Criteria and blocking.** As in the first release check: the owner's section 3 layer 1 row and section 2 tests; the
audit's items 1.1 to 1.12 (`v2/docs/handover/LAYER-STATUS.md` layer 1) and Review A's items. **Blocking** means an
acceptance item the layer claims met and is not; a claim contradicted by its source or by another current record; a
choice presented as the owner's that is the session's; a closure that lowers a requirement, drops a function, weakens
protection or narrows scope; a bound that includes failure left unstated where this layer's lines depend on it.

## 1. What was read

| File at `eb9f9030` | sha256/16 |
|---|---|
| `v2/docs/PRODUCT-BRIEF.md` | `89a11fb01d52f37e` |
| `README.md` | `cfcbe9f8e2183080` |
| `v2/README.md` | `2d6929944d063f74` |
| `v2/BUILD.md` | `0b2861ddb23d24f8` |
| `v2/docs/V2-SPEC.md` | `a92ea2ef3793a3c9` |
| `v2/ecad/tools/pcb_requirements.yaml` (`owner_rulings`, `session_choices`, `open_items`, `closed_items`, the records named below) | `fb819e939f2895da` |
| `v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2026-09-27.md` (the first release check) | `2bd065d12f50298d` |
| `v2/docs/handover/LAYER-STATUS.md` (layer 1 section, its integrator line, the two release paragraphs) | `c6d068de990b8b62` |
| `v2/docs/feasibility/EMCON.md` (sections 0 and 0a) | `421a291f7ce4cda2` |
| `v2/docs/CONOPS.md` (section 3 M1, 4a, 6, 7a row L-02) | `3ff59edc96a3f8f4` |
| `v2/docs/PANEL.md` (lines 50, 52, 135, 189, 195) | `8bac3c8104424c6c` |
| `v2/docs/ASSEMBLY.md` (line 208) | `b49f853f450d49ee` |
| `v2/docs/CURRENT-EVIDENCE.md` (headline, candidate table, feasibility blockers) | `6351a72c7966c4b9` |
| `v2/docs/handover/ENGINEERING-QUESTIONS.md` (EQ-13) | `06960ed5c2340811` |
| `v2/docs/feasibility/POWER-THERMAL.md` (sections 0, 6, 9.4, the findings table) | `ad3ba27cef9e0f68` |
| `v2/docs/CASE-FIT-UNCERTAINTIES.md` (sections 2, 6 and 7) | `efc66afe9140e022` |
| `v2/ecad/tools/gen_footprints_b16.py` (lines 66 to 87) | `e0ad5ba833f1d169` |
| `v2/ecad/tools/panel1450.py` (lines 43, 242 to 248) | `3bdb88df98260244` |
| `v2/ecad/tools/gen_pcb_e.py` (lines 22 to 43) | `46f16a8c3924d25f` |
| `v2/release/case-2026-09-27/README.md` | `531af606ced98859` |
| `v2/release/revA/case/README.md` (its HISTORICAL banner) | `c0852c949f9c3615` |
| `v2/ecad/pcb-c-display-c8/out/pcb-c-display.net` | `11eabc2dddca5161` |
| `v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net` | `adcc3c6736c90e9f` |
| `v2/docs/handover/START-HERE.md` (lines 144, 175, 218) | `c90a3ef2d902dd4a` |

Also read: the owner's prompt sections 1 to 8; `git show --stat` and the messages of `6209ec7e`, `08f3665a`, `116c432e`,
`953f5658`, `d535c17e` and `eb9f9030`; `git diff f2b7fa66 eb9f9030` of the five layer 1 pages; the listing of
`v2/release/case-2026-09-27/` and `v2/release/handover/`; `v2/docs/records/w1/`; the design appendix at lines 17973 to
17990 (32.351), 18154 and 18603 to 18612 (32.362); `CASE-MARGINS.md` rows M4a, M5, M17g and M17x.

**Checks run** (read-only):
- `python3 tools/rules_lib.py requirements` from `v2/ecad`: 144 requirement records, 0 errors, 0 warnings (this includes
  the new check that refuses an undefined SC- id; every SC- id the layer 1 pages cite, SC-02, SC-04, SC-07, SC-08,
  SC-10, SC-13 to SC-16 and SC-21, is defined).
- `python3 tools/claims_check.py` with `VERDICT_DIR` in this reviewer's scratch and `VERDICT_ADVISORY=1`: PASS, 85 claim
  sentences in 12 documents, 0 unqualified. The screen asks each rating word for a qualifier; it does not compare a page
  with the design.
- The registry's `kind: feasibility` records listed with `prototype_1` and `prototype_1_basis` (section 4, R2-B1).
- The committed netlists: board C's carries `D22`; board B's carries `U215`, `U220`, `Q212`, `U222` and `U223`.

Not run: the test suite, any regeneration, the snapshot packer.

## 2. What moved since the first release check

The first release check read `f2b7fa66`. Since then: `6209ec7e` filed the three release records; `08f3665a` applied the
wording fixes of layers 1 and 2 (for layer 1, B1 and B2 in full and B3 in part, V2-SPEC correction 30); `116c432e`
re-anchored the registry's citations and rewrote the integrator lines; `953f5658` rendered the generated pages;
`d535c17e` (the second release attempt) completed B3 in the brief, took the minors m1, m4, m5, m7 and m8, rewrote EQ-13
under SC-21, added the owner action M-02, SC-51 to SC-56, the SC- id validator and, for layers 2 and 3, TEST-PLAN P15,
C1 defined one way and EQ-25; `eb9f9030` rendered the generated pages again. Of the layer 1 pages, `08f3665a` changed
all five and `d535c17e` changed only the brief (its status paragraph, the power bullet, the key-protection bullet, the
two citations of the ruling of 21 September 2026, the FEA-002, L-02 and REQ-072 rows and the closing rule).

## 3. The first release check's findings, re-checked

| Finding | Evidence at `eb9f9030` | Result |
|---|---|---|
| **B1** EMCON, the 5G land and the EMCON lamp as before round 8 | brief lines 83 to 84, 115 to 138 and 287; `v2/README.md` line 5; `v2/BUILD.md` lines 21 and 49; `V2-SPEC.md` lines 24, 41, 59 and 76 and correction 30; `README.md` line 26. Against `EMCON.md` lines 188 to 189 ("local 15 of 17 closed at desk, 2 open (rows 1 and 4 ...); end to end 0 of 17") and section 0's round 8 bullets (the 5G supply removed at once, about 1.2 ms plus 1.8 ms per mF, the flash warning accepted; `D22` through `U14` and `Q7`, its light guide owed); `D22` in board C's netlist; `U215`, `U220`, `Q212` in board B's; `gen_footprints_b16.py` lines 66 to 87 (the two NPTH locating holes of TE C-2199119 rev F); `PANEL.md` lines 50 and 135; S-44 | **CLOSED.** Every line the fix named now says what the sources say; REQ-071's 1 s and 20 s are kept (brief lines 116 to 118) |
| **B2** the case generators and templates said not to carry C1 to C6; readers sent to `release/revA/case/` | `v2/BUILD.md` lines 33, 49, 65, 71 to 73; `v2/README.md` lines 3 and 56; `README.md` line 20; `V2-SPEC.md` line 10 and corrections 20 and 30; brief lines 159 to 162. Against `panel1450.py` line 43 (`PLATE = (377.2, 263.0, 3.0)`) and lines 242 to 248 (`SMA_Z = 59.0`, PolyPhaser GTH-SFF-AL); `release/case-2026-09-27/` (face plate, frame legs, connector plate, RF entry plates, `lid-tray-qmx/`, `templates/case-templates-1to1.pdf`, drawings sheets 1 to 14, its README lines 37 to 39); `release/revA/case/README.md` lines 3 to 10 (HISTORICAL); S-63 (registry line 2081, the QMX tray to be revised before it is printed) | **CLOSED.** Every line points at the current case set and names `release/revA/case/` as superseded history; the committed board files and revA folders are said to predate it, which is true |
| **B3** REQ-072's night finding missing; L-02 stated as the owner's to set; the CONOPS runtime cross-reference stale | brief line 106 (power bullet), lines 213 to 221 (exclusion), 292 (L-02 row), 293 (REQ-072 row), 211 to 212; `V2-SPEC.md` line 23 and correction 30. Against REQ-072 (`prototype_1: core`, `evidence_result: FAIL`, 108 Wh, 2.5 h at 42.8 W, nights of 7 to 16 h, 266 W against 100 W); SC-21 (governs M1's duration, closes L-02, the owner's setting replaces it); L-02 in `closed_items`; M-02 (OWNER_ACTION, OPEN, before boards A, E and P enter layout); S-53; EQ-13 (rewritten, agrees with SC-21); CONOPS lines 181 to 213 and 360, 1059 to 1060 | **CLOSED.** The finding is stated as an exclusion and an open item, allocated (layer 4 for S-53, the owner for M-02), SC-21 is labelled the session's and reversible, and nothing is restated to fit. One qualifier is missing (R2-m2) |
| m1 SC-13's reason | SC-13 `why`: "S-13 holds only the eSIM variant's order code (restated 27 September 2026 ...)" | CLOSED |
| m2 FEA-007 not in the brief | brief lines 256 to 258 and 284 to 295 | **OPEN, and re-judged as blocking: R2-B1.** The first check's reason for classing it minor does not hold (section 4) |
| m3 the EMCON toggle's cover (N3) | `V2-SPEC.md` line 58 and `v2/BUILD.md` line 67 (covers on SOS and ZEROIZE); `PANEL.md` line 52 (all three with hinged covers); `v2/BUILD.md` line 113 ("the EMCON cover") | OPEN, minor (R2-m6) |
| m4 SC-16's "re-checked once" | brief line 318 | CLOSED |
| m5 the lamp's light-guide hole against "the case" | brief line 287: "none of them changes a ruled radio, the Peli case or a board-to-board interface (the hardware lamp's remedy adds a light-guide hole to the made face plate, S-44)" | CLOSED |
| m6 `README.md`'s "eleven blind-mate clamps" | `README.md` line 28; `gen_pcb_e.py` lines 22 to 43 (one clamp bar, twelve cavities with D-07's at X 46) | OPEN, minor (R2-m6) |
| m7 the ruling of 21 September 2026 located | brief lines 225 and 233: "design appendix section 32.362, near its line 18606" | PARTLY: the location cites the ruling but is not it (R2-m4) |
| m8 SC-08 beside D-03 | brief line 144 | CLOSED |
| m9 the release record's name against SC-16's pattern | this record follows the integrator's instruction too | OPEN, minor (R2-m6) |
| Observation: change of method after the same cause twice | brief lines 108 to 138 still restate EMCON transmitter by transmitter; LAYER-STATUS layer 1 remaining item (4) | NOT ADOPTED (section 4, observations) |

## 4. Findings

### Blocking

**R2-B1. The brief states six core feasibility blockers where the requirements registry it cites holds seven: FEA-007,
the kit's fit in the Peli 1450, is core, holds the layout entry of six boards, is BLOCKED on the owner's purchase, has
bounds that include failure on the pack's own fit and on D-07's east plug layout, and is absent from the brief's open
items.**

- `PRODUCT-BRIEF.md` lines 256 to 258: "Six feasibility blockers on the core are not closed (FEA-001 ZEROIZE, FEA-002
  EMCON, FEA-003 the failover fabric, FEA-004 power and thermal, FEA-005 pack protection, FEA-006 decoupling;
  requirements registry, kind feasibility)". The open-items section (lines 274 to 295) says each item bearing on the
  brief "is stated where it lives, with the reason the layer can close while it is open"; FEA-007 is not among them.
- Against: the registry at `eb9f9030` has seven `kind: feasibility` records, every one `prototype_1: core` and
  `release_effect: BLOCKER`. FEA-007's own fields: `prototype_1: core`, `prototype_1_basis: SESSION`,
  `prototype_1_choice: SC-04`, `prototype_1_why: "Fitting the boards, the plate and the pack into the 1450 is a
  condition of every core function (CONOPS section 2a)"`; `holds_layout_entry: [a, b, d, e, e5, p]`; its layout-entry
  stage "BLOCKED on the owner's purchase decision (L-07, D-09)". SC-04 makes "fitting the boards and the pack into the
  1450 (NEED-06)" core. `CURRENT-EVIDENCE.md` lines 177 to 197 list the seven, FEA-007 among them.
  `CASE-FIT-UNCERTAINTIES.md` section 7: 35 of 70 margins OPEN, M17g and M17x "FAILS AS ASSUMED", and with the unstated
  allowances doubled M1, M4a, M5, M15b, M17d, M17f, M17w and M18 read below their minimums; the affected decisions
  include board P's place in the pocket (M4a, M5, on the undesigned hold-down S-27) and "D-07's third 5G jack through the
  east plug layout" (M17g is the east layering under 5G MAIN, which the IRIDIUM, ANT3 and DIV cables pass). Section 6
  records that entering layout on the design basis instead is a residual risk only the owner can accept.
- Why it bears on layer 1. The brief states the pack in the east pocket (D-06, lines 76 to 80) and D-07's jack count
  (lines 87 to 89; the row at line 289 says only "waiting on the board E clamp fit (S-12)" and "the case half is laid
  out"), and both depend on FEA-007's open rows. It is the one core blocker that waits on the owner's money (L-07), and
  the one whose deferral the owner could take as his residual risk. The first release check classed it minor on the
  ground that FEA-007's parent NEED-06 is not a core need; the record's own `prototype_1: core` under SC-04 contradicts
  that ground. So a claim of the brief is contradicted by the source it cites, and a blocker whose bounds include failure
  on two of the brief's lines is not stated: the "claims agree with the engineering baseline" test of the owner's layer 1
  row and the "may not hide a blocker" test of section 2.
- Why it does not keep layer 1 open once stated. Every failing branch of FEA-007 moves a board's outline or placement
  (`CASE-FIT-UNCERTAINTIES.md` section 2: board A's east edge, board B's east edge, stack and CM5 slots, board E's clamp
  lanes, board P's place), and the case never changes (appendix 32.62). The decision it informs is layer 7's and the
  boards' layout entry; the purchase, or the residual, is the owner's. No purpose, user, scope or outcome line of the
  brief changes under either outcome unless the pack rows cannot be met by a board move and a hold-down, which would
  reopen D-06 through the brief's own reissue rule.

**Fix (wording only; no owner answer, purchase or test is needed).**
1. Lines 256 to 258: "Seven feasibility blockers on the core are not closed (FEA-001 ZEROIZE, FEA-002 EMCON, FEA-003 the
   failover fabric, FEA-004 power and thermal, FEA-005 pack protection, FEA-006 decoupling, and FEA-007 the kit's fit in
   the Peli 1450 on the case choices C1 to C6, core as a condition of every core function under the session's SC-04;
   requirements registry, kind feasibility)".
2. Add an open-items row: FEA-007, the kit's fit on C1 to C6 (35 of 70 case margins OPEN; M17g and M17x fail as laid out
   until the jumper plug is picked; the pack's rows M4a and M5 OPEN on its undesigned hold-down, S-27; layout entry of A,
   B, D, E, E5 and P held; the mock-up BLOCKED on the owner's purchase, L-07, or his acceptance of the residual) | "What
   the V2 kit is" (the pack in the east pocket; the antenna entries; D-07's jack count); `CASE-FIT-UNCERTAINTIES.md`
   sections 2, 6 and 7; registry FEA-007, L-07, S-27 | every failing branch moves a board, never the case (32.62), so the
   decision is layer 7's and the boards' layout entry, and the purchase or the residual is the owner's; if the pack rows
   cannot be met by a board move and the hold-down, D-06 is reopened as a product question and this brief is issued
   again.
3. In the D-07 row (line 289), name the east plug layout (M17g, FEA-007) beside the board E clamp fit.

### Minor (not blocking)

- **R2-m1. The lamp test in `v2/BUILD.md` line 113.** "The lamp test lights all 17 LEDs", while line 49 of the same page
  now calls the hardware EMCON lamp `D22` "a seventeenth". `PANEL.md` line 195 and `ASSEMBLY.md` line 208: the lamp test
  lights "all seventeen controller-lit indicators" (`D1` to `D16` and the PI button's ring), and `D22` is not among them
  ("the lamp test cannot light it and setting EMCON is its test"). Say "all seventeen controller-lit indicators (not
  `D22`; `PANEL.md` section 9)". The page's head makes `PANEL.md` govern where they differ, so this is minor.
- **R2-m2. The second pack's reach in the night finding.** Brief lines 219 to 221 name D-01's deferred second pack among
  "the routes that carry the night". EQ-13 (Attempts and results): "A second pack of D-06's size (about 216 Wh aged, the
  two together) carries the shortest night in the lightest state only". Add that qualifier (CONOPS M1 carries the same
  loose wording; for the layer 2 writer).
- **R2-m3. The baseline anchor.** Brief lines 3 to 4 and 46 say the claims were read against the baseline "at
  `e3aedb25`"; the brief now states facts from after it (board B's and board C's round 8, the case release `c351115d`,
  the layer 2 and 3 merges). Name the commit the last reading used (or this record's).
- **R2-m4. The ruling of 21 September 2026 (m7) is located at a citation of it, not at it.** Appendix line 18606 (32.362)
  cites "the owner's ruling of 19:21"; the ruling itself is 32.351 (line 17975 on): a judgement goes to the owner if it
  "spends money, changes what the kit is claimed to be, or accepts a residual risk". Promotion as the owner's is at line
  18154 (32.353). "Publication" is in neither, and the owner's `public-docs` ruling has the foundation documents written
  straight into the public repository. Cite 32.351 and 32.353, and either source "publication" or drop it.
- **R2-m5. Superseded corrections read in the present tense.** `V2-SPEC.md` correction 9 (the land "not yet" carrying
  its locating holes), correction 19 ("the 5G module's supply removal is still owed") and correction 26 ("the 5G module
  (SD-EMC-1 not drawn)", "As drawn, no panel indication of EMCON is independent of firmware") are dated history that
  corrections 28 and 30 supersede, but none says so. Add "(superseded in part by corrections 28 and 30)" to each.
- **R2-m6. Carried from the first check:** m3 (the EMCON toggle's cover: `V2-SPEC.md` line 58 and `v2/BUILD.md` line 67
  against `PANEL.md` line 52 and `v2/BUILD.md` line 113; for the components and panel writers, then the page that is
  wrong), m6 (`README.md` line 28's "eleven blind-mate clamps" against board E's one bar with twelve cavities) and m9 (the
  record name).
- **R2-m7. For other writers, found while checking layer 1's claims** (the layer 1 pages are right on each):
  registry S-12's title still says `gen_footprints_b16.py` "draws neither" locating hole, which lines 66 to 87 now draw
  (the layer 3 writer); S-53 and REQ-016's notes say "about 270 W" where REQ-072, CONOPS M1, EQ-13 and the brief say
  about 266 W (the same arithmetic rounded twice); `START-HERE.md` line 144 ("All nine are IN_PROGRESS"), line 175 (the
  READMEs "stale at `e3aedb25`") and line 218 (V2-SPEC "with dated corrections 1 to 19", now 1 to 30), and
  `CONTINUATION-BRIEF.md` lines 36 to 37, describe layer 1 as at H1.1: the snapshot that carries a BASELINED brief must
  bring them along (acceptance item 14).

### Observations (not findings)

- **Authority.** SC-21 governs M1's duration and is labelled the session's, reversible by the owner's own setting; the
  routes that reopen D-06 or D-01 and the residual are the owner action M-02, reported and not asked; REQ-072 stays FAIL
  and neither REQ-016 nor REQ-072 is restated to fit. Nothing is lowered, and no session choice reads as the owner's.
- **Scope.** SC-02 (LoRa and cellular data as named exceptions to NEED-03 for prototype 1) and correction 29 (four shared
  elements outside NEED-03's failure set) narrow what the redundancy requirement covers for prototype 1; both are
  labelled SESSION with their reason and reversal and stated in the brief (lines 93 to 103), so they are disclosed, not
  silent.
- **M-02 does not hold layer 1 open.** It can change the pack (a component) and boards A, E and P, so it holds those
  boards' layout entry and layers 4 to 7 where they depend on it; for layer 1 it changes only the restatement of D-06's
  pack line, which the brief's reissue rule covers (line 293).
- **The method change is still not adopted.** The same cause produced B1 and B2 twice (Review A's first pass and the
  first release check): the brief restates design state that moves with every circuit round (lines 108 to 138 walk the
  17 transmitters). It is current at `eb9f9030`, and a released snapshot is immutable, so this does not block the
  release; but the next circuit round will make the live brief disagree again. LAYER-STATUS layer 1 remaining item (4)
  names the two remedies; take one before the brief is set BASELINED.

## 5. Figures checked against their sources

| Figure (page, line) | Source | Result |
|---|---|---|
| Headline; declared phases A32, B21, C24, D12, E17, E5, P4; SCH-002 FAIL on A and B, INCONCLUSIVE on C, D, E, P | `CURRENT-EVIDENCE.md` lines 6, 26 to 34 | agrees |
| EMCON: 17 transmitters, local 15 of 17 at desk, SA868 and RockBLOCK 9704 open, 0 of 17 end to end, no bench row | `EMCON.md` section 0, lines 188 to 189 | agrees |
| 5G supply removed at once, about 1.2 ms plus 1.8 ms per mF, the flash warning accepted | `EMCON.md` section 0 (board B bullet), 0a row 5 (1.16 ms plus 1.84 ms per mF) | agrees |
| `D22` drawn, no processor in its path, light guide owed (S-44); fed ahead of the dimmer, dark in BLACKOUT | board C netlist lines 1023, 3939, 3946; `PANEL.md` lines 50, 135, 189; S-44 | agrees |
| SA868 PTT held at 2.677 V or more; RockBLOCK about 16 J; REQ-071 1 s and 20 s | `EMCON.md` 0a and 4.4; REQ-071 acceptance | agrees |
| The key-B land's two locating holes; SIM TVS arrays | `gen_footprints_b16.py` lines 66 to 87; `U222`, `U223` in board B's netlist; V2-SPEC correction 28 | agrees |
| Plate 377.2 x 263.0 x 3.0 on ten 6-32; twelve GTH-SFF-AL at Z 59; case set folders, templates, sheets 1, 2 and 14 | `panel1450.py` lines 43, 245, 248; `release/case-2026-09-27/` listing and README lines 37 to 39 | agrees |
| QMX tray revised before it is printed (S-63) | registry S-63 | agrees |
| 108 Wh aged; 2.5 h at 42.8 W; nights 7 to 16 h at 52 N; about 150 Wh (21.7 W for 7 h); about 266 W against about 100 W | REQ-072 evidence; CONOPS lines 187 to 201 | agrees |
| SC-21 governs M1's duration, closes L-02, replaced by the owner's setting; M-02 owner's, before A, E, P layout | registry SC-21, L-02 (`closed_items`), M-02; EQ-13 | agrees |
| CONOPS 4a and 6 carry 42.8 W, 63.0 W, 2.5 h and 1.7 h | CONOPS lines 360, 1040 to 1041, 1059 to 1060 | agrees |
| 2.5 h and 1.7 h aged, bounds 1.3 to 3.3 h and 0.9 to 2.3 h; charge hold-off +19.5 to +21.6 C; independent bound -18 to +19 C; cells 45 to 81 C | `POWER-THERMAL.md` lines 40 to 41, 68 to 69, 305 to 307, 797 | agrees |
| AW7915-AED 0 to +70 C or -10 to +70 C; LimeSDR 0 to +70 C | `POWER-THERMAL.md` lines 949 to 950 | agrees |
| Two key-encryption keys, both destroyed (SC-08 beside D-03) | registry SC-08 | agrees |
| "Six feasibility blockers on the core" (brief line 256) | registry: seven `kind: feasibility`, all `prototype_1: core`; `CURRENT-EVIDENCE.md` lines 177 to 197 | **disagrees (R2-B1)** |
| D-07's third jack waits on the board E clamp fit only (brief line 289) | `CASE-FIT-UNCERTAINTIES.md` section 7 (D-07 through the east plug layout), `CASE-MARGINS.md` M17g | **incomplete (R2-B1)** |
| The lamp test lights all 17 LEDs (`v2/BUILD.md` line 113) | `PANEL.md` line 195, `ASSEMBLY.md` line 208 | disagrees with the page's own line 49 (R2-m1) |
| The second pack carries the night (brief lines 219 to 221) | EQ-13: the shortest night in the lightest state only | incomplete (R2-m2) |
| Ruling of 21 September 2026 at 32.362 near line 18606 | appendix lines 17975 on (32.351), 18154, 18606 | located at a citation (R2-m4) |

## 6. Acceptance items

| # | Item | Evidence read | Finding |
|---|---|---|---|
| 1 | Clear product purpose (owner row; audit 1.1) | brief lines 51 to 58; CONOPS NEED-01 | MET |
| 2 | Users (1.2) | brief lines 60 to 72 (D-04; four roles; no target organisation, stated) | MET |
| 3 | Prototype scope (1.3) | brief lines 242 to 259 against D-01, SC-01, SC-04 and CONOPS 2a | MET |
| 4 | Exclusions (1.4) | brief lines 172 to 225, including the night finding (REQ-072) | MET (R2-m2) |
| 5 | Intended outcome (1.5) | brief lines 242 to 259: staged acceptance, D-02a's two pass lines, the core feasibility blockers | **NOT MET**: the count and list of core feasibility blockers omit FEA-007 (R2-B1) |
| 6 | Report and deck commitments tracked separately; polish does not gate (1.6) | brief lines 261 to 272 | MET |
| 7 | Claims agree with the engineering baseline (1.7) | sections 3 and 5 | **NOT MET** on R2-B1 alone; B1 to B3 of the first check are closed |
| 8 | Every owner ruling of 25 and 26 September recorded (1.8) | registry `owner_rulings` (D-01 to D-17, D-08a, D-08-reversal, decisions 27, 28, 41, 43, `public-docs`, `standing-rule`); `records/w1/` | MET (R2-m4) |
| 9 | The owed stale texts of BUILD.md and both READMEs closed (1.9) | section 3, B1 and B2 | MET at `eb9f9030` (R2-m1, R2-m6) |
| 10 | SIM description (CFL-010, S-13) (1.10) | SC-13; V2-SPEC line 41, corrections 22 and 28; brief row line 290 | MET; the eSIM variant's order code stays on layer 6's list |
| 11 | Carried-mass limit (REQ-023) | SC-14; REQ-023; brief lines 163 to 170 | MET (the session's limit, with its reversal) |
| 12 | Records filed so the pages need no scratch directory | `v2/docs/records/w1/` present; the release records filed | MET |
| 13 | Required review held (1.11) | Review A layer 1 (two passes); first release check (FAIL, B1 to B3); this record | held; this record has one open blocking finding |
| 14 | Versioned package another engineer can use (1.12) | `v2/release/handover/H1.zip`, `H1.1.zip` carry the brief as a CANDIDATE; nothing at `eb9f9030` is snapshotted; `fnd/rel2` is not pushed; START-HERE and CONTINUATION-BRIEF describe layer 1 as at H1.1 (R2-m7) | **NOT MET** |
| 15 | Section 2: nothing lowered, dropped, weakened or narrowed; session choices marked; bounds that include failure not hidden | SC-02, SC-07, SC-08, SC-10, SC-13 to SC-16 and SC-21 labelled SESSION with reasons and reversals; M-02 the owner's; REQ-072 FAIL carried; no requirement lowered | **NOT MET** on R2-B1 (FEA-007's failing bounds on the pack and on D-07 not stated); otherwise met |
| - | Brief BASELINED at a commit filing a record with no open blocking finding (SC-16) | brief lines 3 to 17 | NOT MET: CANDIDATE, and this record has one open blocking finding |

**Missing decisions of this layer.** None found that can change architecture, interface, component, outline or
protection. The mission duration (SC-21), the SIM (SC-13), the mass limit (SC-14), the public-page treatment (SC-15) and
Review A's definition (SC-16) are taken and labelled; D-18 is conditional and the session's if it arises. The open owner
items that touch the brief's lines, M-02 (the night) and L-07 or the residual on FEA-007 (the mock-up), are decisions of
layers 4 to 7 and of the owner's money and risk, allocated there, and change a layer 1 line only through the brief's
reissue rule; M-02 is stated in the brief, L-07 is not (R2-B1).

## 7. Verdict

**FAIL for release at `eb9f9030`. Layer 1 is not COMPLETE; its status stays IN_PROGRESS.**

The first release check's three blocking findings are **CLOSED** on the text: EMCON, the 5G land and the EMCON lamp now
read as `feasibility/EMCON.md`, the netlists and the generators do (B1); every case line points at
`v2/release/case-2026-09-27/` and names `release/revA/case/` as history (B2); the night finding, SC-21's authority and
the owner's part M-02 are stated, allocated and labelled (B3). Of its minors, m1, m4, m5 and m8 are closed and m7 in part.
Purpose, users, prototype scope, exclusions, the commitments split, the rulings record, the SIM description and the mass
limit meet the owner's section 3 row, and no decision of this layer is missing.

What stops the release is one blocking finding, which the first check left as a minor on a ground the registry
contradicts: **R2-B1**, the brief's "six feasibility blockers on the core" against the registry's seven, with FEA-007 (the
kit's fit in the Peli 1450, core under SC-04, holding six boards' layout entry, BLOCKED on the owner's purchase L-07,
with failing bounds on the pack's fit and on D-07's east plug layout) absent from the open items. It needs wording only:
no owner answer, no purchase and no test.

**To release:** fix R2-B1 (the two sentences and the row of its fix, and the D-07 row), with R2-m1 to R2-m5 on the same
pages; have a reviewer who wrote none of the changed lines re-check the difference from this record's sha256 values at
one pinned commit; take one of the method remedies before the brief is set BASELINED; set the brief to BASELINED in the
commit that files that re-check; then cut a snapshot from a pushed branch that carries the BASELINED brief with the
START-HERE and CONTINUATION-BRIEF lines of R2-m7 brought along (acceptance item 14). The items of R2-m7 for other layers
go to their writers.
