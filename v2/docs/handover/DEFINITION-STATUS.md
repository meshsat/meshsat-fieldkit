# Definition status: layers 1 and 2

The status page of the two completed definition baselines of the foundation baseline (MESHSAT-1357):
`v2/docs/PRODUCT-BRIEF.md`, layer 1, the product definition, and `v2/docs/CONOPS.md`, layer 2, the concept of operations. It exists so
that the baselines change only when the definition does (the independent review of handover H2, `v2/docs/reviews/2026-09-27-h2-independent-review.md` section 4). Prototype design: no V2 board has been fabricated,
ordered or powered, and no kit has been field deployed; nothing on this page is a claim about a built product.

## The rule

A definition baseline is reopened only when a requirement, the scope, the operating concept or another relevant
decision changes. A changed count or a circuit correction updates this page and the records it names, not the
baseline. When a change does reopen a baseline, the affected document is issued again through its layer's review, and
the change is stated in it; nothing is narrowed silently. The review's own words are "a requirement, scope, operating
concept or other relevant decision"; the heads of the two documents say "a product decision", which is narrower, and
where the two differ the review's words govern (finding m6 of the check of the restructure, below).

## The two baselines

| Layer | Document | BASELINED at | sha256/16 of the file baselined | Release record (AI reviews and checks, none a qualified engineering review) |
|---|---|---|---|---|
| 1, product definition | `v2/docs/PRODUCT-BRIEF.md` | `a9f212c7`, re-stamped: an editorial restructure with no definition change of the text first baselined at `6b2a9965` | `026d9ab493d35ed8` at `a9f212c7`, the file the check of the restructure read at `fa89c7c6`; `85513b92ed0daf55` with the re-stamped status paragraph, its only difference; `d36bf76b3dea8b30` at `6b2a9965` (unchanged through `31cd29b9`) | `v2/docs/reviews/DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md`, the check of the restructure (CONTENT_PRESERVED), on `v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`, the narrow verification of the targeted fix, after `v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md` |
| 2, concept of operations | `v2/docs/CONOPS.md` | `a9f212c7`, re-stamped: an editorial restructure with no definition change of the text first baselined at `79963b3b` | `bbcab7c9876f7993` at `a9f212c7`, the file the check of the restructure read at `fa89c7c6`; `6ebe6760c4312bca` with the re-stamped status paragraph, its only difference, the needs table byte-identical; `3ff59edc96a3f8f4` as the release check read it at `eb9f9030`; `4483209659dc391c` with its status line written (`62f26a44`, unchanged through `31cd29b9`), the file handover H2 carries; `6cb7b241cb84d729` at `c5430071`, the owner's rulings of 28 September on the re-stamped text (D-19, D-20 and M1's owner instruction, `v2/docs/records/s122/checks/check-s122-2.md`), the file `CONOPS.md` carries since stream s122 restored it | `v2/docs/reviews/DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md`, the check of the restructure (CONTENT_PRESERVED), on `v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md` |

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

The map of every move is `v2/docs/records/defstab/moves.json`, written with the build script that asserts it
(`build.py`, `cuts.py` and `heads.py` beside it) and re-derived independently by `verify.py`. They were written in the
branch's worktree as `drafts/defstab/`, the path the three registry entries of `fa89c7c6` name, and are filed byte for
byte with `apply_registry.py` in the commit that files the check below (`v2/docs/records/README.md`, section "Filed 27
September 2026: the definition restructure's map"); the map describes the two files at `fa89c7c6`. For every moved block it gives the old line range at `31cd29b9`, the new location and the
sha256; for every block of each definition it gives the sha256 before and after, and which moves closed it up. The
script checks that each kept block equals its original with the moved text removed, that every sentence of a kept
block is a sentence of the original, and that every moved text stands byte for byte at its new place. CONOPS's needs
table is byte-identical; the requirements registry's pin on the whole file (`needs_document_sha256`) is re-taken, and
the three readings bound to CONOPS (REQ-005, CFL-014 and CFL-016) are rebound, each with an entry naming what moved and
stating that the statements it rests on are unchanged. No reading is bound to the brief.

**The check of the map: HELD, CONTENT_PRESERVED.** The restructure did not take either baseline again; whether the
restructured text carries its baseline unchanged was left to a check of the map by a session or person that wrote
none of the restructure. A session that wrote none of it, and used neither the map nor its scripts to reach a result,
checked the carry-over of content at `fa89c7c6` against `31cd29b9`:
`v2/docs/reviews/DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md` (headed "AI check (not a qualified engineering review)",
sha256/16 `4c09af64cb214448`, filed byte for byte in the commit that carries this paragraph). Its verdict is
**CONTENT_PRESERVED**: both definitions are present word for word, with no word added or reworded below either head;
every moved block is status or history, save the two partly definition moves m1 and m2, whose definition content the
kept CONOPS text the brief cites still states; the pointers resolve, save the map (m5); the needs table, the
registry's 19 quoted needs and the pin agree; and the three rebinding notes are true. None of its findings is blocking,
and it supports re-stamping once m1 and m5 are answered. The answers, taken by the session under the owner's standing
rule of 26 September 2026:

- **m1, the brief's entry B-S8 (the count of open feasibility blockers, with SC-04's application of the fit in the
  Peli 1450 as a core condition): the move is accepted, not reversed.** The count is a result, which the H2 review
  names as the coupling that caused a release failure, and restoring the sentence word for word would put it back in
  the definition. The fit's standing as a core condition stays stated where the brief's definition already sends its
  reader: CONOPS section 2a's kept attribute paragraph (NEED-06, SC-04's reading), which the brief's scope section
  cites, and FEA-007 in the requirements registry, which the brief's head names for every feasibility blocker on the
  core. The sentence stands word for word as entry B-S8 below.
- **m5, the map not resolvable in the committed tree: answered** by filing it, above.
- **m2, m3, m4 and m6: carried** to each document's next issue; none changes a definition statement. m2: the brief no
  longer describes the hardware EMCON lamp, which `PANEL.md` sections 1 and 4 define and CONOPS section 4b.1 keeps in
  the operator's use. m3: CONOPS appendix entries A12 (its last sentence, why section 4a's PS-EMCON figure is lower
  than `feasibility/POWER-THERMAL.md`'s 53.1 W) and A14 (the three documents that follow section 4c) state current
  cross-document states in the unmaintained appendix; the current state is in those documents. m4: the brief's "None
  of these is a claim." now follows the TBD runtime values rather than the model figures of entry B-S7; it still
  claims nothing. m6: answered for this page in "The rule", above.
- **Observation O3** (which rule governs the re-read of the layer 1 pages from now on) is answered on
  `v2/docs/handover/LAYER-STATUS.md`, layer 1's integrator line.

**Re-stamped at `a9f212c7`.** `a9f212c7` is the commit that files the check and these answers, and carries both
documents byte-identical to the files the check read at `fa89c7c6`. The commit after it sets each document's status
paragraph to BASELINED at `a9f212c7`, an editorial restructure with no definition change, citing the check and the
release records the baseline rests on (the table above); nothing else in either file changes, so the brief is
`85513b92ed0daf55` and CONOPS `6ebe6760c4312bca` with that paragraph. A re-stamp is not a new review: the
definition is the one baselined at `6b2a9965` and `79963b3b` on the release records in the table, and the check
establishes only that the restructured text carries it. The requirements registry's pin on CONOPS (`needs_document_sha256`) is re-taken on the status paragraph
alone, with the needs table byte-identical, and the three readings bound to CONOPS (REQ-005, CFL-014 and CFL-016)
are rebound with an entry each naming that change. No reading is bound to the brief.

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
| CONOPS's circuit passages whose values differ from the committed netlists (EMCON, HOT-R1, the TX lamp, the device rails, generator line numbers, the supervisors' status path, the fabric's break-before-make and back-power gating, board A's CC array, the supervisors' part of D-13) | the section "Current values of CONOPS's circuit passages (stream s122, 29 September 2026)" below | `CONOPS.md` sections 4, 4b, 4c, 4e, 4f, 7 and 7a |
| The passages of both documents that layer 3's closure restates (18 passages; the re-issue authorised by owner ruling D-38, not yet re-stamped into either document) | the section "Layer 3's definition re-issue (30 September 2026): the approved change record governs until the re-stamp" below; `handover/layer3/DEFINITION-CHANGE-RECORD-L3.md` and `handover/layer3/DEFINITION-REISSUE-DRAFT.md` | `CONOPS.md`, passage (baselined line): C01 (3), C02 (15 to 16), S07 (67), S01 (152), S02 (163 to 165), S03 (167 to 198), S04 (215 to 216), S11 (321), S05 (1019 to 1024), C29 (1040), C31 (1062), S06 (1101); `PRODUCT-BRIEF.md`, passage (baselined line): B01 (3), B02 (15), S08 (60), S09 (171 to 179), B18 (207 to 209), S10 (309) |

## Current values of CONOPS's circuit passages (stream s122, 29 September 2026)

`CONOPS.md` is restored to its text at `c5430071` (the owner's rulings of 28 September, the last change the rule
above allows; stream s122 withdrew set 12's circuit edits `a46db71b` and `7a9f7b5b` and its own round 1), and its
circuit statements are read through this page (CFL-016 and S-122 of the requirements registry). A statement of
`CONOPS.md` about the circuit, and a figure, a commit, a generator line or an "as generated" remark inside it, is its
value when the document was baselined or last reopened. Where the committed netlists now differ, or where the value
is a line number of a generator that has since moved, the current value is kept where the row below says, and that
place is judged against the netlists by `v2/docs/records/s122/verdicts.py`. Where the value the baseline
carries already differed from the netlists at the commit its passage names or where the passage was written,
the row says so: that value was wrong when it was written, not overtaken by a later change (independent check
`v2/docs/records/s122/checks/check-s122-2.md`, m3). Read on the committed netlists of
integration set 13: board A `6c40250c47195ebb`, B `3ef9b8c49a01b728`, C `c9f7394594201045`, D `a2d48972d171aad1`, E
`2ed95a0e8069ebf8`.

| Row | `CONOPS.md` passage | The current value | Where it is kept |
|---|---|---|---|
| DC-01 | section 4's EMCON row; section 4b's preamble and table | what EMCON drives and removes, radio by radio, as set 12 draws it and set 13 keeps it: the RockBLOCK's ENABLE forced low in hardware (`U536`, `U543`), the back-feed gates of the RockBLOCK, the E22 and the E72 (`U537` to `U553`), the card bucks' enables from `U116`, `U216` and `U316`, and board A's PA and HF gates `U35` to `U38` | `feasibility/EMCON.md` section 0a.1; FEA-002, REQ-030 and REQ-071 in the registry |
| DC-02 | section 4's Heat stage and Hot stop rows; section 4c's HOT-R1 passages; section 4f's row of the pack's safety; section 7a's HOT-R1 row | HOT-R1 is drawn on boards A and E since stream w4ae: board E's `Q11` (2N7002), its gate on `HOT_R1_G` from `U10` pin 30 and held off by `R58`, pulls the dock line `BLK_SPARE` at `J_BLK` pin 12; board A reads it as `DOCK_SPARE` at `J_DOCK` pin 12, pulled up by `R216`, on `U27` pin 18 (IO1_5); REQ-077 reads INCONCLUSIVE and waits on S-58 | REQ-077 in the registry |
| DC-03 | section 4e, the panel controller lost | EMCON and MAIN PWR act without the panel controller, and so does the EMCON lamp `D22`, fed from `LED_RAIL_SW` through `R47`; the TX lamp `D3` does not: its feed `LED_RAIL` is `Q1`'s drain, which only `Q2` turns on, from `PANEL_PWM` (GPIO 8); the baseline's text was already wrong at its reading: at `45bde541` and at `a9f212c7` board C's `R36` fed `D3` from `LED_RAIL`, `Q1`'s drain, as it does now | `PANEL.md` sections 1 and 4; `feasibility/EMCON.md` section 8 |
| DC-04 | section 4e, a device rail lost | `+5V_DEV` is made by board A's `U7` (LM5176) and `+3V3_DEV` by board B's `U25` (AP63203) from `+5V_DEV`; the baseline's text was already wrong at its reading: at `45bde541` and at `a9f212c7` board B's `U25` made `+3V3_DEV` from `+5V_DEV`, as it does now | this row; `V2-SPEC.md` correction 32 |
| DC-05 | section 4e, a device rail lost, what the loss releases | a loss of `+3V3_DEV` releases no module radio: each slot makes `EMCON_ON1..3` from its own 3.3 V (`U112`, `U212`, `U312`; EMCON.md L3, closed at desk in board B's round 8), and `U543`, run from `+5V_DEV`, holds the RockBLOCK's ENABLE (`RB_IEN`) low while `+3V3_DEV` is below its threshold | `feasibility/EMCON.md` sections 0a.1 and 7 |
| DC-06 | every generator or tool line number the definition cites (sections 4, 4c and 4e among them) | the line of the commit the citation names, or, undated, of the commit its passage was written at; where stream s122 read the parts at `e57a7365`: `R42` at `gen_sch_a.py:1104`, `R2`, `R184` and `R4` at 338 to 339, `R103` and `R104` at 1598, `R111` at 1611, `U21` at 1340, `U22` at 1372, `R26` and `R27` at 972, `J_USBC_OUT` at 1306, `J_USBW` at 1668, and `J_TAMP` at `gen_sch_e.py:796` | the generators at the commit read; `v2/docs/records/s122/verdicts.out` |
| DC-07 | section 4's Reduced row (its Guarantee cell) and section 4c's `SLOT_EN1` passage: the supervisors' I2C status path, called absent or owed as generated | the three supervisors are targets on the kit bus the panel controller masters: `U41`, `U51` and `U61` have pin 93 (PB7) on `SDA` and pin 92 (PB6) on `SCL`, which reach `J_PANEL`, since `458b2873` (both pins unconnected at its parent `1f614233`); the baseline's text was already wrong at its reading, at `45bde541`, at `95e078a1` where the passages were written, and at `c5430071`; what is owed is the TCA9517A segment of SC-HF-02, which board B does not carry | `ARCH-PCB-B-IOHA.md` section 6; `HW-FW-CONTRACT.md` FW-B08 and section 6.5 |
| DC-08 | the same two passages: the break-before-make order (FAB-03, CON-003) and a bank detached from a host that has lost its power (FAB-02, CON-022), called owed or not done as generated | both drawn in board B's round 8, present at `95e078a1` where the passages were written and at `c5430071`, absent at `45bde541`: each slot's power-good `PG{s}` is its module's own 3.3 V through 1 k with 100 k to ground (`R191` and `R192` for slot 1), buffered by a 74LVC1G17 (`U530` to `U532`) and inverted (`U533` to `U535`); per bank a 74LVC1G157 (`U513` to `U515`) selects the dark flag of the host the delayed select passes, and the bank's enable `BOE{b}_n` (`U516` to `U518`) is forced high while the break-before-make term `BBM{b}` is up and is that flag otherwise; the display switches' enables are the power-good of the slot each passes (`U519` for `U3`, `U520` for `U4`); S-42 stays OPEN, its title listing FAB-02 (b) and (c) and the break-before-make with the gate's assertion and its mutation, and CON-003 and CON-022 read INCONCLUSIVE, waiting on it | `ARCH-PCB-B-IOHA.md` section 5; `feasibility/FAILOVER-FABRIC.md` sections 9 and 9a; S-42, CON-003 and CON-022 in the registry |
| DC-09 | section 7's D-17 row: board A's USB-C CC pins, the array riding on a board A update called owed | the array is drawn: board A's `U31` (TPD2E2U06) on `PD_CC1` and `PD_CC2`, the CC pins of `J_USBC_OUT`, since `458b2873`, and so at `45bde541` and at `c5430071`; the row was written at `68bc9e8f`, before `458b2873` drew it | this row |
| DC-10 | section 7's D-13 row: the STM32H753 in the schematic, the component mismatch with the H743 called open (check-s122-3 m1) | the three supervisors' schematic text is the H743 the project buys: board B's `U41`, `U51` and `U61` read STM32H743VIT6 since `458b2873` (STM32H753VITx at `68bc9e8f`, where the row was written), and CON-017, which asks that text, the BOM and regeneration parity, reads PASS | CON-017 in the registry; `V2-SPEC.md` correction 32 |

## Layer 3's definition re-issue (30 September 2026): the approved change record governs until the re-stamp

Layer 3's closure (owner rulings D-28 to D-37, `handover/layer3/`) restates 18 passages of the two documents, each
listed with its lines, its baselined and its proposed text in the change record
`handover/layer3/DEFINITION-CHANGE-RECORD-L3.md` (sha256/16 `681f37b665a57d03`) and the draft
`handover/layer3/DEFINITION-REISSUE-DRAFT.md` (sha256/16 `a04b0a6cc7400635`). The re-issue is authorised by owner ruling
D-38, his closure instructions of 30 September 2026 (the affected CONOPS and product-brief passages generated from his
choices and accepted by one targeted acceptance review; the session's reading is labelled as such in
`handover/layer3/OWNER-INSTRUCTION-2026-09-30.md`), and its acceptance is the targeted independent review of layer 3's
closure (closure item L3-C27 of `handover/layer3/L3-RECONCILIATION.md`); `handover/layer3/l3r2.yaml` names the record
with that ruling (`definition_reissue`). **Neither document is re-stamped yet**: the proposed texts are written into
`CONOPS.md` and `PRODUCT-BRIEF.md` by their re-stamp through layers 1 and 2, each issued again with the change stated in
it (the rule above), an open obligation of the integrator (closure item L3-C63). **Until that re-stamp, where either
document differs from the approved change record, the change record governs.** The rows the draft proposes for this
page's current values, copied from it:

| Row | Where | Current value |
|---|---|---|
| DC-L3-M1 | `CONOPS.md` section 3 (M1) and sections 6 and 7a; `PRODUCT-BRIEF.md`, the power bullet and the M1 bullet | REQ-072 reads FAIL (DESK_REVIEW, SCHEMATIC phase, release effect MUST_JUSTIFY) when the re-issue is written; its latest evidence entry in the requirements registry: "The modelled baseline (the owner's clarification D-28: reported honestly, the shortfall recorded prominently), read from v2/docs/records/l3batt/runtime.out, the output of v2/docs/records/l3batt/runtime.py (stream l3batt, checked), by v2/docs/records/l3r5/runtime_reader.py for D-32: with HF and the tablet kept and no tablet charging, battery-only from full, D-06's 4S3P pack runs 2.52 h at +20 C (1.04 h at -10 C) and the studied in-case candidate, Option A(i)'s base 4S6P and a 4S9P lid (544.4 Wh usable aged at +20 C), 12.71 h (5.24 h at -10 C); solar-assisted on the mean day in TYP the candidate stops at 05 UTC of the first night, hour 23 from a 06 UTC start and hour 11 from an 18 UTC start, as drawn (266.7 Wh unserved at 48 h, 494.7 Wh at 72 h) and on the hypothetical corrected path (102.2 Wh at 48 h, 165.7 Wh at 72 h, NOM) alike, in 0 of 864 past September windows at 48 h and 0 at 72 h. The objective's lower end is missed even without tablet charging: design risk DR-01, assigned to layer 4. The corrected path is not implemented. Reads FAIL." |

**The solar-assisted figures in the row DC-L3-M1 above and in the draft's passage S03** (the stop at 05 UTC of the first night, 266.7 / 494.7 Wh unserved as drawn, 102.2 / 165.7 Wh on the hypothetical corrected path at 48 / 72 hours, 0 of 864 windows) are historical results of proposal P-03's array (400 Wp in 2S2P into the model's 200 W stage window), which retained REQ-016 (D-34) does not admit, their unserved energy understated (finding L3-R01 of the independent review the owner relayed on 1 October 2026, with the engineering collaborator's layer 4 check of 30 September 2026; `handover/layer3/REQUIREMENTS-L3-R2.md` section 2.3 states the case, `v2/docs/records/l3am/DISPOSITIONS.md` the disposition). The approved change record and draft are not rewritten (D-38): the re-stamp (L3-C63) carries this label into `CONOPS.md` and `PRODUCT-BRIEF.md`, and until then it reads beside them. The result on the retained window awaits layer 4 task L4-E2 (`v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md`, pending).

## What the two documents carried at their baselines

Moved here word for word on 27 September 2026 from the running text of the two documents at `31cd29b9` (for the
brief, the text baselined at `6b2a9965`; for CONOPS, the text it has carried since `62f26a44`). Each entry is the state
as it stood then, not a current reading: the current state is the source the table above names, and a later change is
recorded there, never by editing the baselines. Paths in the moved text are relative to `v2/docs/`, as in the
documents it came from.

### From `PRODUCT-BRIEF.md`

Eight entries, in the brief's order.

#### B-S1. From the head (the framing paragraph)

*`PRODUCT-BRIEF.md` lines 34 to 36 at `31cd29b9`: the evidence headline's counts, quoted.*

What the design has and has not shown
today is `CURRENT-EVIDENCE.md`, whose headline reads **"Foundations incomplete; 0 boards ready for layout; 0
physically verified."**

#### B-S2. From the section "What the V2 kit is" (emission and light discipline)

*`PRODUCT-BRIEF.md` lines 116 to 121 at `31cd29b9`: what the EMCON line is drawn to do as generated, with board B's round 8.*

As generated at `45bde541` the line is drawn to remove the supply of the
  SDR, the RockBLOCK, the LoRa module, both Zigbee and Thread radios, the HF unit and both WiFi link cards, to turn off
  the PA's rail and keying while the VHF exciter keeps receiving, to pull the compute modules' own WiFi and Bluetooth
  disables low, and to put the 5G module in airplane mode through its disable pin, a mode its own firmware carries out;
  since board B's round 8 (27 September 2026) it also removes the 5G module's supply by hardware at once (SD-EMC-1r8,
  `feasibility/EMCON.md` section 4b; `CONOPS.md` section 4b).

#### B-S3. From the section "What the V2 kit is" (emission and light discipline)

*`PRODUCT-BRIEF.md` lines 123 to 137 at `31cd29b9`: the transmitter counts (17, 15 of 17 local, 0 of 17 end to end) and their open rows.*

Read transmitter by
  transmitter against that (`feasibility/EMCON.md` section 0a, sixth revision, with board B's round 8), the kit has 17
  transmitters and **none is dark end to end, at desk or on a bench**:
  - Locally, the radio's own chain closes at desk for 15 of the 17 and is open for two. The SA868 VHF exciter: its
    maker publishes no receive threshold for the PTT pin the design holds at 2.677 V or more (bench E-01). The RockBLOCK
    9704: once its supply is cut it keeps running on its own supercapacitors, about 16 J, with its ENABLE held by a
    firmware-driven expander, so the ENABLE forced low by the EMCON hardware is owed, and what the Iridium module does
    when ENABLE falls is stated in no held document (section 4.4). The 5G module's chain closes at desk since board B's
    round 8: its supply is removed at once, with RF off within about 1.2 ms plus 1.8 ms per mF of the module's own input
    capacitance, which no held document states (bench E-12), and the maker's warning that cutting a working module's
    supply can corrupt its flash accepted as a residual (section 4b).
  - End to end, 0 of 17 rows is closed: every row also waits on the items the rows share, the toggle and its conductor
    (accepted by SD-EMC-6 only with a hardware EMCON lamp on board C, drawn since board C's round 8 as `D22` with no
    processor in its path, and not yet visible, because its light-guide hole in the face plate is owed, open item
    S-44) and the EMCON line's own open items (sections 3 and 7), and no row is shown to meet the latency.

#### B-S4. From the section "What the V2 kit is" (emission and light discipline)

*`PRODUCT-BRIEF.md` lines 139 to 142 at `31cd29b9`: the bench state and the lamps as drawn (D22, the TX lamp's supply).*

No row has been shown on a bench; EMCON is feasibility blocker FEA-002 of the requirements registry. The one panel
  indication of EMCON that is independent of firmware is that lamp, lit while both EMCON lines read low, fed ahead of
  the panel's dimmer and dark in BLACKOUT (`PANEL.md` sections 1 and 4); the TX lamp's supply exists only while the
  panel controller drives its LED dimmer (`feasibility/EMCON.md` section 0; `PANEL.md` section 3, GPIO 8).

#### B-S5. From the section "What the V2 kit is" (antenna entries)

*`PRODUCT-BRIEF.md` lines 164 to 167 at `31cd29b9`: which commit's generators and release folders carry the case choices.*

The case generators carry C1 to C6
  since `c351115d`, and the current case set (CAD, drawings and 1:1 templates) is `v2/release/case-2026-09-27/`; the
  committed board files and the deliverable folders of `v2/release/revA/` predate it and still carry the earlier
  eleven coupler sites at 88 mm, which is history.

#### B-S6. From the section "What it is not, today" (not ready for layout)

*`PRODUCT-BRIEF.md` lines 181 to 184 at `31cd29b9`: board readiness and the circuit corrections the deliverable folders predate.*

No board of the set is ready for layout, and no layout of boards A, B, C, D, E
  or P carries its board's corrected schematic (board E5 has no schematic; its board file is its design): the
  deliverable folders of `v2/release/revA/boards/` predate the circuit corrections of `faf8c981`, `458b2873` and
  `d90f30e4` and every later one (`CURRENT-EVIDENCE.md`, the candidate table).

#### B-S7. From the section "What it is not, today" (runtime)

*`PRODUCT-BRIEF.md` lines 214 to 217 at `31cd29b9`: the power model's current runtime figures and the commit that aligned CONOPS.*

The current PROVISIONAL model
  gives an aged pack 2.5 h in the idle mode and 1.7 h in the typical mode, within bounds of 1.3 to 3.3 h and 0.9 to
  2.3 h (`feasibility/POWER-THERMAL.md` section 6, PWR-F07); `CONOPS.md` sections 4a and 6 carry the same
  PWR-F07 figures since the layer 2 merge (`95e078a1`).

#### B-S8. From the section "What the first prototype has to show"

*`PRODUCT-BRIEF.md` lines 261 to 265 at `31cd29b9`: the count of open feasibility blockers on the core.*

Seven feasibility blockers on the core are not closed (FEA-001 ZEROIZE, FEA-002 EMCON, FEA-003 the
failover fabric, FEA-004 power and thermal, FEA-005 pack protection, FEA-006 decoupling, and FEA-007 the kit's fit in
the Peli 1450 on the case choices C1 to C6, core as a condition of every core function under the session's SC-04;
requirements registry, kind feasibility); each names the evidence that closes it and the stage at which that evidence can exist
(`EXECUTION-PLAN.md`, stage gates).

### From `CONOPS.md`

Seven entries, in the document's order.

#### C-S1. From section 3, mission M4

*`CONOPS.md` lines 275 to 285 at `31cd29b9`: the gaps as generated, board B's round 8 and the transmitter counts.*

As
generated since `458b2873` the two gaps this mission first named are closed in the schematic: the compute modules'
own WiFi and Bluetooth are pulled off through open drains, and the WiFi link cards lose their supply. What remains is
session work under the ruling (S-01), read transmitter by transmitter in `feasibility/EMCON.md` section 0a: the 5G
module, whose only path was its disable pin, a firmware-mediated airplane mode, and the items every row of the EMCON
line shares (section 4b). **Since board B's round 8 (27 September 2026) the 5G module's supply is removed by hardware
at once and board B's shared items are drawn (section 4b)**, so the radio's own chain is closed at desk for 15 of the
17 transmitters and open for two: the SA868 (its PTT pin's receive threshold is unpublished) and the RockBLOCK 9704
(once its supply is cut it runs on its own supercapacitors with its ENABLE held by firmware). No row is closed end to
end, from the toggle to silence at the antenna port, so NEED-08 is not met for any transmitter until the design closes
it, and no row has been shown on a bench.

#### C-S2. From section 4b (the D-05 paragraph)

*`CONOPS.md` lines 455 to 468 at `31cd29b9`: the transmitter counts, board B's round 8 and the open shared items.*

Read transmitter by transmitter
(`feasibility/EMCON.md` section 0a, sixth revision), the radio's own chain meets that meaning at desk for 15 of the 17
transmitters. The 5G module's is among them since board B's round 8 (27 September 2026): its only EMCON path had been
its disable pin, and its supply is now removed by hardware at once with a bounded time to RF off (EMCON.md section 4b,
SD-EMC-1r8). Two stay open: the SA868, whose PTT pin's receive threshold its maker does not publish (bench E-01), and
the RockBLOCK 9704, whose own supercapacitors keep the module running after its supply gate opens, with its ENABLE held
by firmware (EMCON.md section 4.4). What every row
shares was open as well (EMCON.md section 7: the line's hold with its source gone, a loss of board B's `+3V3_DEV`
that released every gate hung on `EMCON_ON` or on `U{s}11`, gate supplies outside their range, the drive of the
2N7002s, and the back-feed paths of SD-EMC-2); on board B round 8 closes the hold, the `+3V3_DEV` loss and the drive at
desk, and the 5G module's back-feed, and leaves open the gate supplies of `U501` to `U505` and the back-feed into the
RockBLOCK, the E22 and the E72 (EMCON.md section 4b); end to end, from the toggle to silence at the antenna port within
the latency of REQ-071, no row is closed; and no row has been shown on a bench (EMCON.md section 6, twelve tests, none
of which can use the kit's own SDR, whose supply EMCON removes).

#### C-S3. From section 4b (its closing paragraph)

*`CONOPS.md` lines 473 to 474 at `31cd29b9`: the commits that drew the two switches.*

The WiFi cards' converter enables are drawn since `458b2873`; the 5G supply
switch, SD-EMC-1's, is drawn since board B's round 8 (SD-EMC-1r8, EMCON.md section 4b).

#### C-S4. From section 4b.1 (what the operator does with it)

*`CONOPS.md` lines 505 to 507 at `31cd29b9`: the transmitter counts against REQ-071.*

**State at this revision:** this is a requirement on the design (REQ-071), and no row meets it end to end at desk yet
(`feasibility/EMCON.md` sections 0a and 5a: locally 15 of the 17 rows close at desk, rows 1 and 4, the SA868 and the RockBLOCK 9704, are open, and every row inherits the shared items of
its section 3, so 0 of 17 close end to end).

#### C-S5. From section 4c (HOT-R1)

*`CONOPS.md` lines 677 to 679 at `31cd29b9`: the hot stop requirement's reading on the generated boards.*

**Until HOT-R1 is in both generators the hot stop's requirement reads FAIL on the generated boards,** a finding
reported to the owner, not asked: the stop then acts only where the bridge links the two controllers (the normal and
reduced modes, and the heat stage after BANK-R1, up to H1 itself), and falls back to the `TMP117` elsewhere.

#### C-S6. From section 4c (BANK-R1)

*`CONOPS.md` lines 738 to 740 at `31cd29b9`: REQ-052's reading on board B as generated.*

**Until BANK-R1 is in board B's generator,
REQ-052 is not met by board B as generated** (its one-module stage lacks the LoRa mesh and APRS): a finding against the
generated board, reported to the owner at the next checkpoint, not asked.

#### C-S7. From section 4c (the recovery and delivery targets)

*`CONOPS.md` lines 869 to 869 at `31cd29b9`: the registry items the targets closed.*

These close S-37 and REQ-003's latency TBD for the kit's part.
