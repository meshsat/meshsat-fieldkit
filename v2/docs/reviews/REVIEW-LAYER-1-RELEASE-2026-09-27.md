# AI review (not a qualified engineering review)

## Layer 1 (vision, product definition and pitch): release check at `f2b7fa66`, 27 September 2026

MESHSAT-1357. **Commit judged: `f2b7fa669eba97186af71362230b1895f0bcad48`**, branch `fnd/r8int4` (eight commits on main
`38dcd764`, not pushed), read in its worktree between 13:05 and 13:25 CEST; `git status` was clean before and after, and
nothing in the tree was edited except this record.

Reviewer: one AI reviewer session that wrote none of the files judged, did not assemble them and did not take part in
Review A's first or second pass. This is an AI review, labelled as one. It is not a qualified engineering review, no
record in this tree requires a qualified review of layer 1 (SC-16, `EXECUTION-PLAN.md` lines 65 to 71), and it does not
stand in for any qualified review the tree does require (D-09, `v2/docs/reviews/REVIEW-ROUTES.md`). Prototype design:
nothing in this kit has been built, ordered, powered or measured, and nothing below is a physical result.

**The question.** Does layer 1 meet the owner's COMPLETE test (`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`
section 2, and the layer 1 row of section 3) at this commit, so that it can be released?

**Criteria.** The owner's section 3 layer 1 row (purpose, users, prototype scope, exclusions, intended outcome; report and
deck commitments tracked separately; claims agree with the engineering baseline) and his section 2 tests (current,
internally consistent deliverables; acceptance items met with evidence; the required review; a versioned package; no
missing decision of this layer that can change architecture, interface, component, outline or protection; open
feasibility questions allocated to the layer that owns them and not hidden; nothing lowered, dropped, weakened or
narrowed; session choices marked as the session's). The project's own items: the audit's acceptance items 1.1 to 1.12 in
`v2/docs/handover/LAYER-STATUS.md` layer 1 and its integrator line; Review A layer 1's items 1 to 15
(`v2/docs/reviews/REVIEW-A-LAYER-1-2026-09-27.md` section 6) and its open conditions I5 and I2; the Review A definition
of `PRODUCT-BRIEF.md`'s last section (SC-16). **Blocking** means, as in Review A's passes: an acceptance item the layer
claims met and is not; a claim contradicted by its source or by another current record; a choice presented as the
owner's that is the session's; a closure that lowers a requirement, drops a function, weakens protection or narrows
scope; a bound that includes failure left unstated or treated as closed where this layer's lines depend on it.

## 1. What was read

| File at `f2b7fa66` | sha256/16 |
|---|---|
| `v2/docs/PRODUCT-BRIEF.md` | `6247bff0a46795b4` |
| `README.md` | `d33c351f6212d4c9` (the same bytes Review A's second pass read) |
| `v2/README.md` | `6f9b68c398ccd355` (the same bytes Review A's second pass read) |
| `v2/BUILD.md` | `27ce60fca0b764ea` |
| `v2/docs/V2-SPEC.md` | `73a797e44d42fa6d` |
| `v2/ecad/tools/pcb_requirements.yaml` (`owner_rulings`, `session_choices`, and the records cited below) | `ab65fea491ee5da1` |
| `v2/docs/reviews/REVIEW-A-LAYER-1-2026-09-27.md` | `d469a268fe0b8768` |
| `v2/docs/handover/LAYER-STATUS.md` (layer 1, the H1 status table, the "Merged after H1.1" paragraph) | `2db0cc0c165aba42` |
| `v2/docs/feasibility/EMCON.md` (sections 0, 0a, 4.1, 4.4, 4b) | `421a291f7ce4cda2` |
| `v2/docs/CONOPS.md` (sections 2a, 3 M1 and D-05, 4, 4b, 4b.1, 6, 7) | `4887ada07f50d808` |
| `v2/docs/PANEL.md` (lines 5, 50, 52, 135) | `4bcbf31f44560ee1` |
| `v2/ecad/tools/gen_sch_c.py` (lines 11, 238 to 266) | `7c555c07abc97500` |
| `v2/ecad/tools/gen_footprints_b16.py` (lines 7, 66 to 87) | `e0ad5ba833f1d169` |
| `v2/ecad/tools/panel1450.py` (lines 17, 38 to 49, 242 to 252) | `3bdb88df98260244` |
| `v2/release/revA/case/README.md` (its HISTORICAL banner) | `c0852c949f9c3615` |
| `v2/docs/CURRENT-EVIDENCE.md` (headline, candidate table) | `23ec56778cee856e` |

Also read: `v2/release/case-2026-09-27/README.md`, `v2/ecad/tools/case_wall_cutouts.py` (docstring),
`v2/cad/face_plate.py`, `v2/ecad/tools/gen_pcb_e.py` lines 22 to 44, `v2/ecad/tools/gen_sch_b.py` lines 763 to 791,
`v2/docs/feasibility/POWER-THERMAL.md` (sections 0, 6, 9.2 to 9.4, the findings table), `v2/docs/CASE-MARGINS.md`
(lines 276 and 773), `v2/docs/ARCHITECTURE.md` (lines 1125 to 1129), `v2/vendor/standards/mil-std-810h-method-516-8.md`,
`v2/docs/records/w1/`, `v2/docs/EXECUTION-PLAN.md` lines 55 to 71, `v2/docs/handover/START-HERE.md`,
`v2/docs/handover/CONTINUATION-BRIEF.md` (the contradictions table), `v2/docs/handover/ENGINEERING-QUESTIONS.md` EQ-13,
and `git log`/`git show --stat` of every commit from `e3aedb25` to `f2b7fa66`.

**Checks run** (read-only; `git status` unchanged after each):
- `python3 tools/rules_lib.py requirements` from `v2/ecad`: 144 requirement records, 0 errors, 0 warnings.
- `python3 tools/claims_check.py`: PASS, 85 claim sentences in 12 documents, 0 unqualified. This screen asks each rating
  word for a qualifier; it does not compare a page with the design, so it cannot see the findings below.
- The committed netlists: `pcb-c-display.net` carries `D22` (the hardware EMCON lamp); `pcb-b-compute.net` carries
  `U215`, `U220` and `Q212` (the 5G module's supply removal of SD-EMC-1r8).
- Every figure listed in section 5 re-read at its source.

Not run: the test suite, any regeneration, the snapshot packer.

## 2. What moved since Review A's second pass

The second pass read the closer's worktree on `e3aedb25` and main `53a98a71` (01:59). The layer 1 closer merged at
`2ef6aa2a` (06:33). Since `53a98a71` the tree has taken, among others: `9f28c238` (02:49, board C's round 8: the hardware
EMCON lamp `D22`), `45f6d83f` (board E's clamp bar with twelve cavities), `b76c18cb` (board B's round 8: SD-EMC-1r8, the
5G land's locating holes, the SIM TVS arrays), `95e078a1` (the layer 2 and layer 3 closers: CONOPS with EMCON at 15 of
17, the hot stop, REQ-072 to REQ-077, SC-17 to SC-50, L-02 closed by SC-21) and `c351115d` (the case release: C1 to C6
in `panel1450.py`, `case_wall_cutouts.py` and `v2/cad/`, `v2/release/case-2026-09-27/`, `release/revA/case/` marked
HISTORICAL, FEA-007). Of the layer 1 pages, only `V2-SPEC.md` (corrections 28 and 29, lines 24, 41 and 76) and two rows
of the brief (the SIM row, the single points of failure) were brought along. `README.md` and `v2/README.md` are byte for
byte the text the second pass read; `v2/BUILD.md` changed only for N2.

## 3. The item the integrator line leaves open: I5 and I2 on the merged CONOPS and PANEL

- **I2: CLOSED.** `CONOPS.md` lines 69 to 70 and 1088 cite `records/w1/w1-conflicts.md` and `w1-decisions.md`; lines
  1124 to 1128 record the owner's `public-docs` ruling. Both files exist under `v2/docs/records/w1/`.
- **I5: CLOSED on the CONOPS and PANEL side.** `CONOPS.md` lines 273 to 285 (section 3, D-05), 338 (section 4, EMCON row)
  and 453 to 463 (section 4b) now state EMCON as `feasibility/EMCON.md` section 0a does: local 15 of 17 at desk, the
  SA868 and the RockBLOCK 9704 open, the 5G module's supply removed by hardware since board B's round 8, 0 of 17 end to
  end, no bench row. `PANEL.md` line 5 names MAIN PWR and EMCON as the lines that act without software and says the TX
  lamp's feed needs the controller; lines 50 and 135 name the hardware EMCON lamp `D22`. Three residuals remain in
  `CONOPS.md`, layer 2's file, and contradict its own section 4b: line 490 (section 4b.1, the 5G row's L_max still
  "SD-EMC-1's staged supply removal, owed on board B"), lines 496 to 498 (the lamp "once it is drawn on board C") and
  line 961 ("airplane mode now; supply removal owed"). They are for the layer 2 writer.
- **But I5's risk has reversed.** I5 said the handover must not carry "two readings of a core function". At `f2b7fa66`
  it still does, with the layer 1 pages now the stale side: finding B1.

## 4. Findings

### Blocking

**B1. EMCON, the 5G socket land and the EMCON lamp are stated as before round 8 in the brief, both READMEs and BUILD.md,
against `feasibility/EMCON.md`, CONOPS, PANEL, V2-SPEC's own line 24 and correction 28, and the generators.**

- `PRODUCT-BRIEF.md` lines 115 to 120: "the radio's own chain closes at desk for 14 of the 17 and is open for three ...
  The 5G module: its staged supply removal (SD-EMC-1, open item S-01) is not drawn". Line 266 (the FEA-002 row): "locally
  14 of 17 closed at desk and three open ... the 5G module (SD-EMC-1 not drawn) ... no panel indication independent of
  firmware".
- `PRODUCT-BRIEF.md` lines 121 to 127: the shared element is accepted only "with a hardware EMCON lamp on board C, which
  is not drawn", and "As drawn, no panel indication of EMCON is independent of firmware".
- `PRODUCT-BRIEF.md` lines 78 to 79: the key-B socket's "land still lacks the maker's two locating holes, open item
  S-12".
- `v2/README.md` line 5: "the radio's own chain closes at desk for 14 and is open for ... the 5G module (its staged
  supply removal, SD-EMC-1, is owed)". `v2/BUILD.md` line 21: "14 of the 17 ... the 5G module, which the line only puts
  in airplane mode ... until its supply removal SD-EMC-1 is drawn".
- `V2-SPEC.md` line 24 (already at 15 of 17) still says the lamp on board C "is not drawn"; line 76 lists "the hardware
  EMCON lamp on board C (SD-EMC-6)" as owed; line 59 and `README.md` line 26 count sixteen LEDs.
- `PRODUCT-BRIEF.md` lines 10 to 12 (status): BASELINED waits on the layer 2 EMCON and face text, "which is not in this
  tree yet"; it is in the tree since `95e078a1`.

Against: `feasibility/EMCON.md` lines 189 to 190 ("local 15 of 17 closed at desk, 2 open (rows 1 and 4; row 5 closed at
desk by board B's round 8)"), section 0 (board C's round 8 draws the lamp, `D22` through `U14` and `Q7`, its plate light
guide still owed); `gen_sch_c.py` lines 261 to 266 and `D22` in the committed board C netlist; `U215`, `U220`, `Q212` in
the committed board B netlist; `gen_footprints_b16.py` lines 66 to 87 (the land with TE C-2199119 rev F's two NPTH
locating holes); `V2-SPEC.md` lines 24, 41 and 76 and correction 28 (lines 230 to 238); `CONOPS.md` lines 273 to 285,
338, 453 to 463; `PANEL.md` lines 5, 50 and 135. EMCON is core (D-01) and feasibility blocker FEA-002, so the package
carries two readings of a core function; and the brief understates the design state it summarises, which the section 3
row's "claims agree with the engineering baseline" does not allow in either direction.

**Fix.** State EMCON in the brief (lines 113 to 127 and 266), `v2/README.md` line 5 and `v2/BUILD.md` line 21 as
`EMCON.md` section 0a and V2-SPEC line 24 now do: 15 of 17 locally at desk, the SA868 and the RockBLOCK 9704 open, the
5G module's supply removed by hardware since board B's round 8 (SD-EMC-1r8, RF off within about 1.2 ms plus 1.8 ms per
mF of an unpublished input capacitance, the flash warning accepted), 0 of 17 end to end, no bench row. State the lamp as
drawn on board C (`D22`, no processor in its path) with its face-plate light-guide hole owed (S-44), in the brief, V2-SPEC
lines 24, 59 and 76 and `README.md` line 26. Replace the locating-hole clause of brief lines 78 to 79 with V2-SPEC
line 41's. Update the status paragraph. Keep the latency sentence (REQ-071 still sets 1 s and 20 s, registry line 5534).

**B2. The layer 1 pages say the case generators do not carry C1 to C6 and send the reader to `release/revA/case/`, which
is now marked "HISTORICAL, SUPERSEDED ... Do not make, cut, drill or order anything from this folder".**

- `v2/BUILD.md` line 49: the plate "becomes 377.2 x 263.0 x 3.0 mm with a rebated band, which the plate generator does
  not carry yet. The face plate is a CNC part from the DXF and STEP in `release/revA/case/face-plate/`"; the QMX tray
  "is printed from `release/revA/case/lid-bracket-qmx/`". Line 33: "the face itself is the aluminium plate of
  `release/revA/case/face-plate/`". Line 71: "`release/revA/case/face-plate/` drawing, to be regenerated for C1". Line
  72: the templates of `release/revA/case/` "still show the eleven 6.5 mm D-holes at Z 88 until `case_wall_cutouts.py`
  carries C2".
- `v2/README.md` line 3: the face plate is `cad/face_plate.py`, `release/revA/case/face-plate/`, C1 "which the generated
  plate does not carry yet"; "the generators and templates still carry eleven couplers at 88 mm". Line 56: "As generated,
  the face plate (365.5 x 249.5 x 3, ten M3 ...)", C1 and C6 "which the generators do not carry yet", "the eleven couplers
  sit in the end walls at 88 mm as generated", "The templates are in `release/revA/case/`".
- `README.md` line 20: "the generators and case templates still carry the eleven couplers at 88 mm". `V2-SPEC.md` line 10:
  "history until `panel1450.py` and `case_wall_cutouts.py` carry C2"; correction 20 (lines 163 to 164): "The generators
  (`panel1450.py`, `case_wall_cutouts.py`) and the templates of `release/revA/case/` still carry the eleven couplers at Z
  88". `PRODUCT-BRIEF.md` lines 149 to 150: "The generators and the committed boards still carry the earlier eleven
  couplers at 88 mm".

Against: `panel1450.py` lines 38 to 49 (`PLATE = (377.2, 263.0, 3.0)`, ten 6-32 UNC) and 242 to 252 (twelve PolyPhaser
GTH-SFF-AL at `SMA_Z = 59.0`); `case_wall_cutouts.py`'s docstring (drawn for C2, C3 and C4; the earlier issue
superseded); `v2/cad/face_plate.py` line 5 (377.2 x 263.0); `v2/release/case-2026-09-27/README.md` (C1 to C6, CAD,
drawings, 1:1 templates, the QMX lid tray); `v2/release/revA/case/README.md` lines 3 to 10 (HISTORICAL). A reader who
follows `v2/BUILD.md` section 2 or `v2/README.md` today is sent to the superseded plate and templates. The board files
committed for the declared phases do still carry the earlier sites, so only the "generators" and "templates" halves of
these sentences are wrong.

**Fix.** Point every one of these lines at `v2/release/case-2026-09-27/` and say the case generators carry C1 to C6
since `c351115d`; keep the statement that the committed board files (and the revA deliverable folders) predate it; add
a V2-SPEC correction for lines 10 and correction 20's last sentence.

**B3. The brief omits a desk FAIL on a core requirement that bears on its own power and pack lines: on D-06's pack and
the solar input alone the kit does not run through a single night (REQ-072), and it still says the owner sets the
mission duration later although SC-21 has set it.**

- `PRODUCT-BRIEF.md` lines 99 to 102: "a solar input; missions longer than the pack rely on the vehicle or solar input
  (D-06)". "What it is not, today" (lines 160 to 204) and the open-items table (lines 263 to 273) do not state the M1
  finding. Line 271: "L-02, the mission duration for the solar balance, which the owner sets later (D-06)".
- Against: registry REQ-072 (parent NEED-05, `prototype_1: core`, `evidence_result: FAIL`, evidence at desk: "The design
  as generated does not carry M1": the aged pack's about 108 Wh bridges 2.5 h at 42.8 W against nights of 7 to 16 h at
  52 N, and 72 hours ask a panel of about 266 W where boards E and A take about 100 W); SC-21 (72 hours, closes L-02,
  "Reported to the owner as a consequence of D-06 ... not asked"); `CONOPS.md` lines 170 to 215 (M1; "on pack and solar
  alone the kit does not hold M1 through a single night, whatever the solar rating"; the routes that carry the night:
  an overnight input on the 9 to 36 V entry, D-01's deferred second pack, or a larger pack, which reopens D-06).
- Its outcome can change a line of "What the V2 kit is" (the pack, owner ruling D-06) or of the prototype scope (D-01's
  deferred second pack), so it is an item that bears on the brief. The brief's own rule (lines 255 to 261) is that every
  such item is stated with where it lives and why the layer can close with it open. Leaving it out is the hidden-blocker
  case of the owner's section 2.
- Same topic, a stale cross-reference: `PRODUCT-BRIEF.md` lines 199 to 200 and `V2-SPEC.md` line 23 say `CONOPS.md`
  sections 4a and 6 "still carry the earlier model's" 3.4 h and 1.8 h (32.4 W, 60.1 W); `CONOPS.md` lines 360, 376 and
  1059 to 1064 now carry PWR-F07's 42.8 W, 63.0 W, 2.5 h and 1.7 h and say they replace the W2 model's figures.
- For the handover writer, not layer 1's file: `ENGINEERING-QUESTIONS.md` EQ-13 still recommends option (a) and argues
  that the session may not set the value D-06 reserved (option (c)), while SC-21 took (c) and the registry closes L-02
  on it. The two must be reconciled; SC-21 is labelled as the session's and reversible, so it is not presented as the
  owner's, but whether the standing rule reaches a value D-06 kept for the owner is stated nowhere as settled.

**Fix.** Add to "What it is not, today": on its pack and solar input alone the kit does not run through a night at
52 N in any state (REQ-072 FAIL at desk; CONOPS M1), so multi-day operation needs an overnight input on the vehicle and
shore entry until the owner reopens D-06 or D-01's second pack. Add an open-items row: REQ-072 and SC-21, where they
live, the layer that owns the finding (layer 4 for the energy architecture; the owner for D-06 and D-01), and why layer 1
can close (purpose, users and the core list stand; the pack line and the brief are reissued if the owner reopens D-06).
Correct line 271 to name SC-21's 72 hours as the session's planning value that the owner's setting replaces, and lines
199 to 200 and V2-SPEC line 23 to say CONOPS now carries PWR-F07's figures.

### Minor (not blocking)

- **m1. SC-13's reason is stale.** Registry SC-13 `why`: "The SIM TVS array ... and the eSIM variant's code stay owed
  under S-13, so CFL-010 stays open." CFL-010 reads `CONFLICT_RESOLVED` on SC-13's description, CON-025 reads PASS on
  `U222` and `U223` (`gen_sch_b.py` lines 763 to 791), and S-13 now holds only the eSIM variant's order code. Align the
  sentence; the choice itself is unchanged.
- **m2. FEA-007 is not in the brief.** FEA-007 (the kit's fit on C1 to C6: 35 of 70 margins OPEN, M17g and M17x failing
  as laid out, LAYOUT_ENTRY held on A, B, D, E, E5 and P, the mock-up blocked on the owner's purchase L-07) has bounds
  that include failure. Its remedies move boards, not the case (appendix 32.62: the case never changes), so it does not
  change a layer 1 line, but the open-items table should carry it with that allocation (layer 7 and the boards' layout
  entry). The brief's "Six feasibility blockers on the core" (line 235) is literally true, since FEA-007's parent NEED-06
  is not a core need; say so, so a reader does not take six for the registry's total.
- **m3. N3 is still open:** `V2-SPEC.md` line 58 puts hinged covers on SOS and ZEROIZE only; `PANEL.md` line 52 gives all
  three locking toggles covers, `gen_sch_c.py` describes `SW_EMCON` with one, and `v2/BUILD.md` line 113 speaks of "the
  EMCON cover". One side is wrong; for the components and panel writers, then the page that is wrong.
- **m4. N4 is half done and now inconsistent:** the brief (line 296) says blocking findings are "re-checked once by the
  same reviewer"; SC-16 in the registry says "re-checked once". Take SC-16's wording into the brief (this check, like the
  second pass, was held by a reviewer other than the first).
- **m5. N5 is still open:** the FEA-002 row (line 266) says no open row's remedy changes "the case"; SD-EMC-6's lamp adds a
  light-guide hole to the face plate, and the RockBLOCK row's failure branch could change a bought part. The row's reissue
  clause covers the second; name the first.
- **m6. The board E role in `README.md` line 28** says "eleven blind-mate clamps"; board E's generator draws one clamp bar
  with a cavity per site, eleven or twelve with D-07's at X 46 (`gen_pcb_e.py` lines 22 to 44, `45f6d83f`).
- **m7. The ruling of 21 September 2026** (brief lines 204 and 212: publication, money, promotion and advertising stay
  with the owner) is cited with no location; it is recorded in the design appendix (line 18606, "the owner's ruling of
  19:21"). Name that location so a recipient needs no session memory.
- **m8. Key wrapping.** Brief lines 133 to 136 and `V2-SPEC.md` line 34 put "two key-encryption keys ... destroys both"
  beside owner ruling D-03, whose words are "a key the secure element holds; ZEROIZE destroys it". The two-key scheme is
  the session's implementation, SC-08; cite SC-08 beside D-03 so the scheme does not read as the owner's.
- **m9. This record's name** follows the integrator's instruction, not SC-16's pattern `REVIEW-A-LAYER-1-<date>.md`;
  align one to the other at integration, as M4 of the first pass did.

### Observations (not findings)

- SC-02 names LoRa and cellular data as exceptions to NEED-03 for prototype 1, and correction 29 names four shared
  elements outside NEED-03's failure set. Both narrow what the owner's redundancy requirement covers for prototype 1; both
  are labelled SESSION, give their reason and their reversal, and are stated in the brief (lines 88 to 98). Under the
  standing rule this is disclosed, not silent narrowing.
- SC-13's default build (two nano-SIMs) departs from the approved eSIM plus nano-SIM and says so; both configurations stay
  on the board, so nothing ruled is dropped.
- **The cause of B1 and B2 has now recurred** (Review A's first pass B1 was the same kind of finding). The owner's section
  4 asks for a change of method after two unsuccessful attempts. The layer 1 pages restate design state that moves with
  every circuit round and every CAD merge (transmitter counts, what is "not drawn", what "the generators" carry). Either
  state those facts only by reference (`feasibility/EMCON.md` section 0a, `CURRENT-EVIDENCE.md`, the case release) and
  keep the pages to the product-level statement, or make re-reading the five layer 1 pages a step of every integration
  that touches EMCON, the case or CONOPS.

## 5. Figures checked against their sources

| Figure (page, line) | Source | Result |
|---|---|---|
| Headline, declared phases A32, B21, C24, D12, E17, E5, P4; SCH-002 FAIL on A and B, INCONCLUSIVE on C, D, E, P | `CURRENT-EVIDENCE.md` lines 6, 26 to 34 | agrees |
| 145 Wh, 144.7 Wh at 3,350 mAh (V2-SPEC 20) | 4 x 3.6 V x 3 x 3.35 Ah = 144.7 Wh | agrees |
| 42.8 W, 63.0 W; 2.5 h and 1.7 h aged; bounds 1.3 to 3.3 h and 0.9 to 2.3 h | `POWER-THERMAL.md` lines 32 to 41, 209 to 210, 305, 966 | agrees |
| charge hold-off +19.5 to +21.6 C; independent bound -18 to +19 C; cells 45 to 81 C at +20 C | `POWER-THERMAL.md` lines 68, 797, 806, 854 to 855 | agrees |
| AW7915-AED 0 to +70 C (2023 PDF), -10 to +70 C (page); LimeSDR 0 to +70 C in use and storage | `POWER-THERMAL.md` lines 949 to 950 | agrees |
| Peli 1450 exterior 417.6 x 330.2 x 173.2 mm; about 478 mm over the arrestors (X +-238.8) | `CASE-MARGINS.md` lines 276 and 773 | agrees |
| sourced mass floor about 7.0 kg | `ARCHITECTURE.md` lines 1125 to 1129 | agrees |
| Table 516.8-IX: under 45.4 kg and under 91 cm, man-packed or man-portable, 122 cm, 26 drops | `v2/vendor/standards/mil-std-810h-method-516-8.md` lines 33 to 36 | agrees |
| REQ-071: 1 s, and 20 s for a running 5G module | registry REQ-071 acceptance | agrees |
| SA868 PTT held at 2.677 V or more; RockBLOCK about 16 J | `EMCON.md` lines 456, 479, 610 | agrees |
| EMCON local 14 of 17, 5G open, lamp not drawn (brief, both READMEs' and BUILD's EMCON lines) | `EMCON.md` lines 189 to 190; netlists | **disagrees (B1)** |
| 5G land lacks its locating holes (brief 78 to 79) | `gen_footprints_b16.py` lines 66 to 87; V2-SPEC correction 28 | **disagrees (B1)** |
| generators carry eleven couplers at Z 88; plate generator lacks C1 | `panel1450.py`, `case_wall_cutouts.py`, `face_plate.py` | **disagrees (B2)** |
| CONOPS still carries 3.4 h and 1.8 h | `CONOPS.md` lines 360, 376, 1059 to 1064 | **disagrees (B3)** |
| D-01 core list and deferred list | registry D-01 `core_needs`, `deferred_named`; brief lines 169 to 172 and 223 to 227 | agrees |

## 6. Acceptance items

| # | Item | Evidence read | Finding |
|---|---|---|---|
| 1 | Clear product purpose (owner row; audit 1.1) | brief lines 46 to 53; CONOPS NEED-01 | MET |
| 2 | Users (1.2) | brief lines 55 to 67 (D-04; four roles with their records; no target organisation, stated) | MET |
| 3 | Prototype scope (1.3) | brief lines 221 to 238 against registry D-01 and SC-01 | MET |
| 4 | Exclusions (1.4) | brief lines 160 to 204, figures of section 5 | **NOT MET**: the M1 night finding (B3) is missing; otherwise complete (m2 for FEA-007) |
| 5 | Intended outcome (1.5) | brief lines 221 to 238: staged acceptance, D-02a's two pass lines, the six core FEA blockers | MET (m2) |
| 6 | Report and deck commitments tracked separately; polish does not gate (1.6) | brief lines 240 to 251 | MET |
| 7 | Claims agree with the engineering baseline (1.7) | section 4 and section 5 | **NOT MET**: B1, B2, B3 |
| 8 | Every owner ruling of 25 and 26 September recorded (1.8) | registry `owner_rulings`: D-01 to D-17, D-08a, D-08-reversal, decisions 27, 28, 41, 43 (30 and 40 through D-03 and D-15), `public-docs`, `standing-rule`; CONOPS lines 1124 to 1128; `records/w1/` | MET (m7) |
| 9 | The owed stale texts of BUILD.md and both READMEs closed (1.9) | closed at `2ef6aa2a`; re-staled by `9f28c238`, `b76c18cb`, `95e078a1`, `c351115d` | **NOT MET at `f2b7fa66`**: B1, B2 |
| 10 | SIM description (CFL-010, S-13) (1.10) | SC-13; CFL-010 CONFLICT_RESOLVED; CON-025 PASS; V2-SPEC line 41, corrections 22 and 28; `gen_sch_b.py` lines 763 to 791 | MET; the eSIM variant's order code stays on layer 6's list (S-13); m1 |
| 11 | Carried-mass limit (REQ-023) | SC-14; REQ-023; section 5 | MET (a limit where none existed, labelled as the session's, with its reversal) |
| 12 | Records filed so the pages need no scratch directory | `records/w1/` present; Review A's second pass re-hashed the filed set; not re-hashed here | MET as recorded by that pass |
| 13 | Required review held (1.11) | Review A layer 1, first pass FAIL and second pass PASS, filed; this release check | held; this check reopens three blocking items caused by later merges |
| 14 | Versioned package another engineer can use (1.12) | `v2/release/handover/H1.zip`, `H1.1.zip`: partial snapshots with the brief at CANDIDATE; nothing at `f2b7fa66` is snapshotted, and the branch is not pushed | **NOT MET** |
| 15 | Section 2: nothing lowered, dropped, weakened or narrowed; session choices marked; bounds that include failure not hidden | SC-01, SC-02, SC-07, SC-10, SC-13 to SC-16, SC-21, C1 to C6 and the thermal controls are each SESSION and labelled; REQ-023 gains a limit; no requirement is lowered; FEA-002 and FEA-004 are allocated with reissue clauses | **NOT MET** until B3 is fixed (REQ-072 not stated); m8 |
| I5 | Layer 2's EMCON and face text on the merged CONOPS and PANEL | section 3 | CLOSED there (three residuals for layer 2); reversed onto the layer 1 pages as B1 |
| I2 | CONOPS cites the filed W1 records and records `public-docs` | section 3 | CLOSED |
| - | Brief BASELINED at a commit filing a record with no open blocking finding (SC-16) | brief lines 3 to 12 | NOT MET: CANDIDATE, and this record has three open blocking findings |

**Missing decisions of this layer.** None found that can change architecture, interface, component, outline or
protection: the SIM (SC-13), the mass limit (SC-14), the Review A definition (SC-16), the public-page treatment (SC-15)
and the mission duration (SC-21, with its authority question in B3) are taken and labelled. D-18 is conditional and the
session's if it arises. The open items that bear on the brief are allocated to the layers that own them (FEA-001 to
FEA-006 to layers 4, 8 and 9; FEA-007 to layer 7 and the boards' layout entry; REQ-072 to layer 4 and the owner), but
two of them (REQ-072, FEA-007) are not stated in the brief.

## 7. Verdict

**FAIL for release. Layer 1 is not COMPLETE at `f2b7fa66`; its status stays IN_PROGRESS.**

Purpose, users, prototype scope, intended outcome, the commitments split, the rulings record, the SIM description and the
mass limit meet the owner's section 3 row, and no decision of this layer is missing. What stops the release is
consistency with the current baseline: three blocking findings, each introduced by merges after Review A's second pass
(board C's and board B's round 8, the case release, and the layer 2 and 3 closers), and none needing the owner, a
purchase or a physical test:

- **B1** the EMCON count, the 5G land and the EMCON lamp as before round 8 (brief, `v2/README.md`, `v2/BUILD.md`, and
  V2-SPEC lines 24, 59 and 76, `README.md` line 26);
- **B2** the case generators and templates stated as not carrying C1 to C6, with the reader sent to the superseded
  `release/revA/case/` (`v2/BUILD.md`, both READMEs, V2-SPEC line 10 and correction 20, the brief);
- **B3** the M1 night finding (REQ-072 FAIL at desk, a core requirement) absent from the brief's exclusions and open
  items, L-02 stated as still the owner's to set, and the stale CONOPS runtime cross-reference.

**To release:** fix B1 to B3 (and m1, m4, m5, m7 and m8, which touch the same lines); have a reviewer who wrote none of
the changed lines re-check them against this record at one pinned commit; set the brief to BASELINED in the commit that
files that re-check; then cut a snapshot that carries the BASELINED brief (acceptance item 14), since H1 and H1.1 carry it
as a candidate. The layer 2 residuals of section 3 and EQ-13's contradiction with SC-21 go to their writers. Adopt the
method change of section 4 so that the next circuit round or CAD merge does not re-stale the layer 1 pages.
