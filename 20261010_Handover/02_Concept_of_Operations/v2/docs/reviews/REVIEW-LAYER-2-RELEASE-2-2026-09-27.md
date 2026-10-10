# AI review (not a qualified engineering review): layer 2 (concept of operations), second release check at `eb9f9030`

MESHSAT-1357. Written 27 September 2026, about 15:20 CEST, by a fresh AI reviewer (a Claude subagent). This reviewer
wrote none of the layer's documents and none of the changes in `08f3665a`, `d535c17e` or `eb9f9030`. It did not hold
the first release check of this layer or any pass of Review A, and it did not assemble the handover. This is an **AI
review**. It replaces none of the qualified reviews the records require (D-09: R-BAT, R-SEC, R-PWR, R-HSD), and it
establishes no circuit's correctness. No record in the tree requires a qualified review of layers 1 or 2
(`EXECUTION-PLAN.md`, the Review A definition, lines 65 to 71). Prototype design: nothing has been built, ordered,
powered or deployed.

It is judged against the owner's execution prompt (`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`),
sections 1, 2 and 3, and against the layer's Review A definition (`EXECUTION-PLAN.md` line 73). It is the re-check
that the layer 2 integrator line lists as remaining item (1): "a re-check of B1 to B4 as now fixed by a reviewer who
wrote none of the changed lines, limited to the difference from the release review's sha256 values".

## 1. What was read and run

**Commit judged:** `eb9f9030989de925d6569bc00a846568fa4d300b`, branch `fnd/rel2`, worktree `scratchpad/wt/rel2`. It is
not pushed and is on no other branch. After the first release check's commit `f2b7fa66`, the branch carries:
- `6209ec7e`: the three release reviews, filed;
- `08f3665a`: the wording and citation fixes (B1, the B3 filing, B4 (a), (b) and (d));
- `116c432e` and `953f5658`: handover pages and generated pages;
- `d535c17e`: the second release attempt (B2, B3's completion, B4 (a), (c) and (e));
- `eb9f9030`: its generated pages.

At read time the worktree had no tracked change. One untracked file from another reviewer was present
(`v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md`); this reviewer did not read or touch it. Nothing was edited
except this record, and nothing was run in any tree.

**`main` has moved since the fixer's hand-off.** The hand-off says main is still `953f5658`. At 15:16 CEST `main` and
`origin/main` are at `391d8579`, seven commits later (set 5: `e2aab014`, `ffca0771`, `caba1876`, `b7f96784`,
`730f8489`, `a7b5872e`, `391d8579`).
- Unchanged by them: `CONOPS.md`, `OPERATING-ENVELOPE.md`, `TEST-PLAN.md`, `pcb_envelope.yaml`, `HW-FW-CONTRACT.md` and
  `feasibility/POWER-THERMAL.md`.
- Changed by them, and also by `fnd/rel2`: `PANEL.md` (one row of the kit-bus table: `U28`'s inputs gain `EMCON_EF_FLT`;
  no operator item), `ARCHITECTURE.md`, `handover/ENGINEERING-QUESTIONS.md`, `handover/LAYER-STATUS.md`,
  `pcb_requirements.yaml` and `pcb_interfaces.yaml`.
- Changed by them only: the generators of boards A, B and E.

HOT-R1's netlist premises still hold on main's generators:
- `J_DOCK` pin 12 is `DOCK_SPARE`, which lands on `U27` pin 18, an input whose change raises `EXP_INT` (`gen_sch_a.py`
  lines 266 and 1468 to 1471 at `391d8579`);
- `J_BLK` pin 12 is `BLK_SPARE`, whose only other node is `TP7`;
- `U10` pin 30 (GPIO19) is `NC` (`gen_sch_e.py` lines 661, 696 and 847 at `391d8579`).

What this means for the release is in section 8.

**The layer's files at `eb9f9030`** (sha256, first 16 hex digits):

| sha256/16 | File | Note |
|---|---|---|
| 3ff59edc96a3f8f4 | `v2/docs/CONOPS.md` | equals the registry's `needs_document_sha256` (was 4887ada07f50d808 at `f2b7fa66`) |
| 43361b02743cf3af | `v2/docs/OPERATING-ENVELOPE.md` | equals `pcb_envelope.yaml` `document_sha256` and ENV-001's `verified_sha` (was 6e4bbde9dbf7e136) |
| bbcc2b5cbb721372 | `v2/ecad/tools/pcb_envelope.yaml` | only its document pin and that pin's comment changed (was ce95b2e947099a30) |
| 8bac3c8104424c6c | `v2/docs/PANEL.md` | sections 1, 4, 5, 9 and 10 read (was 4bcbf31f44560ee1) |
| 4f15bd02a6a8be46 | `v2/docs/TEST-PLAN.md` | sections 1, 4, 6 (E3-A, E3-L, E3-H, E3-T), 7 (P10 to P15), 8 (was a0de0b12ff06ba4e) |
| 77b20ca4042f0855 | `v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27.md` | Review A pass 2 (unchanged) |
| e854c2a46ea3d542 | `v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27-pass1.md` | Review A pass 1, filed |
| fe6ca95b6c6356a8 | `v2/docs/reviews/2026-09-27-review-A-layer2-brief.md` | Review A brief, filed |
| cb7c773b9b193e1f | `v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2026-09-27.md` | the first release check |

**Other layers' files read at the same commit, for consistency:**

| sha256/16 | File | What was read |
|---|---|---|
| ad3ba27cef9e0f68 | `feasibility/POWER-THERMAL.md` | sections 1, 9.1 to 9.3, 11 |
| ee74646eb4288076 | `ARCHITECTURE.md` | section 8 |
| 1747d4ae9d3475df | `HW-FW-CONTRACT.md` | sections 0, 3.2, 3.5, 5, 8 and the change record |
| 421a291f7ce4cda2 | `feasibility/EMCON.md` | sections 0a, 4b, 5a; unchanged since `f2b7fa66` |
| 06960ed5c2340811 | `handover/ENGINEERING-QUESTIONS.md` | the index, EQ-03, EQ-13, EQ-25 |
| 7008f55efe227d38 | `handover/CONTINUATION-BRIEF.md` | section 8 |
| c6d068de990b8b62 | `handover/LAYER-STATUS.md` | the status section, layer 2, and the integrator lines of layers 4 and 5 |
| c90a3ef2d902dd4a | `handover/START-HERE.md` | sections 0 to 2 |
| fb819e939f2895da | `v2/ecad/tools/pcb_requirements.yaml` | see below |
| 3ceb54454fb4e04c | `pcb_rules_coverage.yaml` | ENV-001 |
| a5ef21d39f75853c | `v2/docs/records/README.md` | its new sections |
| 6154bd6c15bdfa6b | `rules_lib.py` | the SC-id check |

The registry entries read were REQ-052, 069, 071, 072 and 077, M-02, L-02, SC-21, S-01, S-44, S-53, CFL-008, 009, 011
and 017.

These sources are unchanged since `f2b7fa66`, so the first release check's netlist and datasheet readings of them still
hold at this commit: `gen_sch_a.py`, `gen_sch_b.py`, `gen_sch_c.py`, `gen_sch_e.py`, `gen_sch_p.py`,
`ARCH-PCB-B-IOHA.md`, `THERMAL-COORDINATION.md`, `pcb_interfaces.yaml` and `records/hc2/`.

**Sources checked for this pass:**
- TI SLUUAQ3A, the BQ4050 technical reference manual, as a text copy of the filed PDF (`v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf`):
  - 2.7: the cell temperature is the maximum or the average of the thermistors, as DA Configuration [CTEMP] selects;
  - 3.20: "The device can permanently disable the battery if it detects an open thermistor on TS1, TS2, TS3, or TS4";
  - 11.2.1.4.2 to .5: External 1 to 4 Temp Offset are type I1, -128 to 127, in 0.1 C, so at most 12.7 K;
  - 13.1.48: `ManufacturerAccess()` 0x0072 DAStatus2.
- The Semitec 103AT-2 sheet (`v2/vendor/battery/semitec-103at-2-kempston.pdf`): R25 10.0 kohm, B25/85 3435 K, both +-1 %.
- `gen_sch_p.py` line 221 (`J_TS`: TS1 TS2 TS3 TS4 VSS) and line 418 (`J_TS2`, the second level's own thermistor).
- `gen_sch_b.py` line 1264: the secure element `U8` is on `+3V3_DEV`.

**Runs.** All stdlib, each under a few seconds, in this reviewer's scratch directory `scratchpad/rv2-l2/`, never in a
tree.
- `records/hc2/pwr_red2.py` with `records/rv-pwr/pwr_budget.py` (469d0820b046ef6f) reproduces `pwr_red2.out` byte for
  byte (835910e807d588c4).
- `records/hc2/hotstop_bounds.py` on that output reproduces `hotstop_bounds.out` byte for byte (5f03619f7bf5c476) when
  its input keeps the name `pwr_red2.out`. The script writes its input's file name into its output.
- A sparse shared clone of `eb9f9030` in scratch held `v2/docs`, `v2/ecad/tools` and the 31 vendor, netlist and CAD
  files the registry binds as evidence. In it, `tests/run.py test_envelope_data test_requirements` gave **70 pass,
  0 fail, 1 skip**. The skip needs the gitignored `out/rule-audit`. Among the passes:
  - the real registry validates;
  - the trace page equals its render;
  - every SC- id the registry or a page cites is defined by an entry (the new check);
  - the six envelope fixtures pass, with the document pinned by content and the pin equal to ENV-001's.

**Not run:** `rules_lib.py requirements`, `rules_render.py` and `rules_status.py` in any tree (they write). Nothing of
the COMPATIBILITY change was run: it concerns PWR-001 and CMP-001, not this layer.

**Figures checked against their source and found right:**
- **P15's resistances.** On the 103AT-2's B value of 3435 K the resistances are 3487.9, 3325.7, 3273.6 and 4607.4 ohm
  at +55.0, +56.5, +57.0 and +46.5 C. P15 says "about 3.49, 3.33, 3.27 and 4.61 kohm".
- **The offset limit.** "at most 12.7 K" is 127 x 0.1 C.
- **The new figures in POWER-THERMAL and ARCHITECTURE,** each against `pwr_red2.out`:

| Figure | Value in the documents |
|---|---|
| PS-RED2 | 31.4 W (17.6 to 55.6), heat 31.7 W |
| PS-RED2 inside-air rise | 12.7 to 29.9 K (W4) and 15.8 to 21.1 K (appendix 32.53) |
| PS-RED2 charge hold | from +5.3 to +29.2 C and from +18.4 to +24.5 C |
| PS-SURV-R | 23.3 W (12.8 to 46.9), heat 23.4 W |
| PS-SURV | 21.7 W (12.4 to 42.0), heat 21.9 W |
| PS-RED | 22.2 W (12.7 to 45.9), heat 22.4 W |
| PS-RED charge hold | from +15 to +33 C and from +25 to +29 C (14.6 to 33.1 and 24.9 to 29.4 in the output) |

- **CONOPS's C1 ambients** in the Reduced and Heat stage rows (+20.1 to +37.3 C and +28.9 to +34.2 C; +27.9 to +40.6 C
  and so on) match the output's "C1 air trigger" ceilings.
- **EQ-13's arithmetic.**
  - 108 Wh / 42.8 W = 2.5 h.
  - 21.7 W x 7 h = 152 Wh, and 42.8 W x 7 h = 300 Wh.
  - 42.8 W x 16 h = 685 Wh, about 6.3 times 108 Wh.
  - Two aged packs (about 216 Wh) carry 152 Wh but not 300 Wh.
- **EQ-25.** The +61.6 to +74.2 C is `OPERATING-ENVELOPE.md` lines 408 to 409, and 2.5 K is 57.5 - 55.

## 2. The first release check's four blocking findings, re-checked on `eb9f9030`

| Finding | What was asked | Where it is answered | Disposition |
|---|---|---|---|
| **B1**: two readings of EMCON, a core function | Remove the pre-round-8 mechanism from CONOPS 4b.1, 4f and M4, OPERATING-ENVELOPE section 4, TEST-PLAN section 4 and PANEL; state the design (5G supply removed by hardware at once) against REQ-071's bound; one statement on whether the lamp test lights `D22`. | See the B1 detail below. | **CLOSED.** A grep of these files and `PRODUCT-BRIEF.md` for "airplane mode", "owed on board B", "hardware timers", "once it is drawn" and the old REQ-030 sentence finds only historical sentences that name the round-8 change. Two stale passages remain in other layers' files, each tracked there (n10). |
| **B2**: E3-H cannot tell a working hot stop from one never exercised | A forced run beyond the envelope; a room-temperature walk of one gauge cell reading; NOT_VERIFIED for a step that never acted. | TEST-PLAN P15 (line 163), E3-H (line 136), REQ-077's acceptance, CONOPS Hot stop row (line 335). See the B2 detail below. | **CLOSED.** P15 matches CONOPS 4c, FW-C13, FW-C14 and FW-E10 on thresholds, debounce, release rules and line states. Its method rests on the TRM (3.20, 11.2.1.4, 13.1.48) and on board P's connectors as generated. Nothing is lowered: REQ-077's earlier acceptance is kept whole as part (2), and E3-L's pass line is unchanged. Minors n1 to n3. |
| **B3**: the review history and two sources outside the repository | File pass 1 and the brief with sha256 rows; cite them; say whether the c23 verifier's record exists; cite A06's filed records. | See the B3 detail below. | **CLOSED.** Four historical records under `records/hc2/` still name pass 2's path for pass 1. They are filed byte for byte, and `records/README.md` explains which file is which, so they are left as history. |
| **B4 (a)**: C1 and the reduced mode defined three ways | One definition in POWER-THERMAL, ARCHITECTURE and HW-FW-CONTRACT; the hot stop's firmware rows; tracking. | See the B4 detail below. | **CLOSED.** A grep of `v2/docs` finds no current text that takes the reduced mode as one module or slot 3; the remaining hits are history, candidate patches, or model states now named as the one-module stage. One ambiguity: n4. |
| **B4 (b)**: EMCON.md 5a row 5 and registry titles | Retitle S-01 and S-44 to what remains; track EMCON.md 5a row 5 in layer 4. | S-01 and S-44 restated in `08f3665a`. The layer 4 integrator line lists EMCON.md 5a row 5 as remaining, with REQ-071's desk acceptance (T_off, T_cut). | **CLOSED as tracking.** EMCON.md 5a row 5 marks its state "CLOSED at desk on board B's round 8", but its "as drawn / required by SD-EMC-1" cells still describe the staged removal. This is layer 4's text (n10). |
| **B4 (c)**: EQ-13 against SC-21 | EQ-13 says what the session took. | EQ-13 (line 342) is rewritten. See the B4 detail below. | **CLOSED.** |
| **B4 (d)**: CONTINUATION-BRIEF section 8's stale layer-2 rows | Mark the five rows superseded. | All five carry "Superseded after H1.1 (the release check of 27 September 2026)" with the current file. | **CLOSED** for the five rows named. A sixth layer-2 row the first check did not list is still unmarked (n6). |
| **B4 (e)**: no engineering question for BAT-F19 | An EQ in group C with routes, evidence, recommendation and cost. | EQ-25 (line 386): the exact issue, affected records, evidence (THERMAL-COORDINATION 9a, OPERATING-ENVELOPE section 8, the cell sheet, CFL-017), attempts, three routes with who may take each, the recommendation, expertise, cost. CFL-017's notes point to it. | **CLOSED.** |

**B1 detail.**
- CONOPS M4 (lines 268 to 269 and 278 to 285); 4b's 5G row and the D-05 paragraph (lines 446 to 465); 4b.1's L_max 5G
  row (line 490); the Excluded (496), operator (500) and state (505) paragraphs of 4b.1, now naming REQ-071, 15 of 17
  local rows and 0 of 17 end to end; 4f's 5G EMCON cell (line 961); the EMCON row (line 338).
- `OPERATING-ENVELOPE.md` section 4, lines 289 to 298.
- `TEST-PLAN.md` section 4, line 56: "the hardware EMCON lamp `D22`", with REQ-071 in the trace.
- `PANEL.md` section 1 (line 50), section 4 (line 135: "The lamp test cannot light `D22`: no expander reaches it, and
  setting EMCON is its test") and section 9 (line 195), with the two counts of seventeen named apart.

**B2 detail.**
- **TEST-PLAN P15 (line 163)** is run on the assembled kit, at room temperature, first on the pack and then on shore:
  - one cell thermistor input at board P's `J_TS` is replaced by a make-before-break decade resistance, and each setting
    is read back in DAStatus2();
  - the steps are +55.0, +56.5 and +57.0 C, never reaching OTD at +57.5 C; then +50.0 and +46.0 C after H1, and MAIN at
    +50.0 and +46.0 C after H2;
  - HOT-R1's four states, the TMP117 stand-in (+55.0 and +56.0 C, released at +45.0 C), and SafetyStatus() and
    PFStatus() clean after each run;
  - "A step that did not act reads NOT_VERIFIED for REQ-077, never PASS".
- **E3-H (line 136)** gains the stepped run beyond the envelope (+40 C by 2 K an hour to at most +55 C, shore first,
  labelled a protection test and not an envelope claim), NOT_REACHED for a thermal run that reached no threshold, and
  the +59 C abort, unchanged.
- **REQ-077's acceptance** now has parts (1) P15 and (2) E3-H; its statement, sources, notes and FAIL are otherwise as
  before.
- **CONOPS's Hot stop row (line 335)** names P15.

**B3 detail.**
- `REVIEW-A-LAYER-2-2026-09-27-pass1.md` (sha256 e854c2a46ea3d542, 20460 bytes) equals `scratchpad/rvA2/REVIEW-A-LAYER-2-2026-09-27.pass1.md`.
- `2026-09-27-review-A-layer2-brief.md` (fe6ca95b6c6356a8, 8071 bytes) equals `scratchpad/wt/hc2/drafts/REVIEW-A-BRIEF.md`.
  Both were compared here by sha256.
- `records/README.md` carries both with sha256, bytes, source and "cited by".
- Pass 1 is cited by its filed name at CONOPS lines 20, 46 and 1138, TEST-PLAN line 3 and OPERATING-ENVELOPE line 36.
  CONOPS line 47 cites pass 2's record as pass 2's.
- The integrator line says that no record of the c23 verifier exists and that the release review is the re-check.
- A06 is cited at `records/adj/A06-pack-geometry/` in CONOPS 4a and in OPERATING-ENVELOPE section 4's pack row.

**B4 (a) detail.** CONOPS 4c (line 526) states the definition, and the other documents now follow it:
- POWER-THERMAL section 1 (lines 98 to 99; "Where this page says PS-RED, read the one-module stage"), 735, 822,
  858 to 859, 876 to 877, 899 to 900 and 1163;
- ARCHITECTURE lines 866, 876, 889 and 908;
- HW-FW-CONTRACT FW-C09 (line 108), with FW-C13 (112), FW-C14 (113), FW-E10 (160) and V-C13 (223) new;
- the layer 5 integrator line marks its item (7) done for the contract and keeps PANEL.md's duties as remaining.

**B4 (c) detail.** EQ-13 now says:
- SC-21 governs M1's duration, is the session's, and is replaced by the owner's own setting;
- the failing balance has the session's part (S-53) and the owner's (M-02);
- the options are (a) to (e), with who may take each;
- a shorter mission is excluded as lowering the requirement.

L-02's title, SC-21's "why", S-53, M-02, REQ-072's `waits_on` and CONOPS M1 (lines 210 to 213) say the same. REQ-072
still reads FAIL at desk.

## 3. The owner's section 3 row for layer 2, at `eb9f9030`

| Item (owner's prompt, section 3) | Evidence | Finding |
|---|---|---|
| Normal scenario | M1, the Normal row (line 332), 4a, section 5 | met |
| Degraded scenario | M5; the Reduced, Heat stage, Hot stop and Degraded rows (333 to 337); 4c; 4e | met |
| Startup scenario | the Startup row (331); 4c's start with the lid closed; PANEL section 5's boot order; HOT-R1 read at start-up (FW-C14) | met (PANEL section 5 does not yet list the HOT-R1 read: n5) |
| Charging scenario | the Charging row (336); the gauge's window; `CHRG_INHIBIT` in H1 | met |
| Shutdown scenario | the Shutdown row (343); 4c's graceful shutdown; H2 | met |
| Storage scenario | the Storage and Transport rows (329, 344); 7a row 1156; TEST-PLAN E3-T and E4-T; BAT-F19 now EQ-25 | met |
| Service scenario | the Service and Commissioning rows; 4d | met |
| Fault scenarios | 4e, including the hot stop and its lost detector (rows 944 and 945) | met |
| Operating envelope | OPERATING-ENVELOPE sections 2 to 5 and 8; `pcb_envelope.yaml`, pinned, with its fixtures passing | met; the hot and cold bounds are stated as open and allocated (FEA-004, S-55); minors m1, m5, m9, m10 |
| Simultaneous modes | section 5 | met |
| Explicit behaviour of the retained core functions | 4f, the section 4 rows, 4b, 4b.1, PANEL section 9; EMCON now has one reading (B1) | met; m12 (no hot-stop column in 4f) remains. It is a missing statement, not a missing decision: in H1 the panel controller, the kit bus and `+3V3_DEV` stay up, and `U8` sits on `+3V3_DEV`, so ZEROIZE acts in H1 by the rules already written; in H2 it completes at the next boot, as the "panel controller lost" column says |
| Product decisions settled under existing authority | section 7 and 7a; `session_taken`; registry SC-17 to SC-56. The handover now agrees with them (EQ-13 with SC-21) and the owner-level items have compact questions (EQ-13 with M-02, EQ-25) | met |

## 4. The project's own acceptance items (LAYER-STATUS, layer 2, items 2.1 to 2.17)

| # | Item | Finding at `eb9f9030` |
|---|---|---|
| 2.1 to 2.10 | the scenarios, the envelope, simultaneity and duty | met, as the first release check found; their text is unchanged apart from B1's and B2's edits (section 2) |
| 2.11 | explicit behaviour of the core functions | **met** (B1 closed); m12 remains a minor |
| 2.12 | product decisions settled under existing authority | met inside the layer and in the handover. M-02 is the owner's, recorded as OWNER_ACTION and "reported, not asked", decided before boards A, E and P enter layout. It does not hold layer 2: M1's duration is set (SC-21), and CONOPS M1 states the finding and the way a night is carried today, so no mode, trigger or bearer set waits on it (n8) |
| 2.13 | every owner ruling recorded | met |
| 2.14 | consistent with the current analyses | **met** for C1 and EMCON (B1, B4 (a)). The remaining lags are in other layers' texts and are tracked there (n4, n10) |
| 2.15 | TEST-PLAN envelope limits consistent with the rulings | **met** (B2 closed); m2 remains |
| 2.16 | every source the CONOPS cites is in the repository | **met** (B3 closed) |
| 2.17 | Review A held and recorded | held: pass 1, pass 2, the first release check, and this pass, which has no blocking finding (section 6) |

## 5. The owner's section 2 tests

- **Every acceptance item met with evidence.** Yes (sections 3 and 4).
- **Consistent with the other layers' current files.** Yes on everything that defines a mode, a control or a core
  function: C1, the reduced mode, the heat stage and the hot stop now read the same in CONOPS, OPERATING-ENVELOPE,
  `pcb_envelope.yaml`, POWER-THERMAL, ARCHITECTURE, HW-FW-CONTRACT, the registry and TEST-PLAN. EMCON reads the same in
  CONOPS, OPERATING-ENVELOPE, PANEL, TEST-PLAN and PRODUCT-BRIEF. The remaining differences are wording, or lags in
  another layer's text that its integrator line tracks (n4 to n7, n9, n10).
- **No missing decision of this layer that can change architecture, interface, component, outline or protection.**
  None found. BANK-R1 (SC-34) and HOT-R1 (SC-50) are taken, and what is owed is their drawing on boards B, A and E
  (layer 8, with IF-AE-DOCK pin 12 at layer 5); REQ-052 and REQ-077 read FAIL on the generated boards until then, and
  CONOPS says so. The decisions still open belong to later layers:
  - S-58's hardware stage behind the hot stop is a protection-architecture decision for the D-09 battery reviewer
    (layer 4, EQ-23), before the layout entry of A, E and P;
  - M-02 (the pack) belongs to the owner and to layers 4, 6 and 7, before the layout entry of A, E and P;
  - D-18, the SGP41's replacement and the extended-grade card and SDR are layers 4, 6 and 7;
  - REQ-069's classification changes only a transport claim (EQ-03), no design.
- **Open feasibility questions allocated to the layer that owns them.** FEA-004 with T-H1 and EQ-05; S-55; S-57 with
  EQ-22; S-54; S-58 with EQ-23; S-53 and M-02 with EQ-13; BAT-F19 with EQ-25. Each is stated with the failure it can
  produce. FEA-004's plausible bounds include failure (at the worst corner the hot stop acts from +33.2 C, and at +40 C
  no module then runs on any supply, failing REQ-052), and CONOPS states this (lines 700 to 714 and 786 to 788). It is
  not dismissed as PROVISIONAL. Deferring it past layer 2 is justified in the text (lines 789 to 802): every control
  acts on a measured internal temperature or current, so no mode, trigger, bearer set or product decision of the layer
  changes with the conductance. What changes (the ambients, and the thermal design of the pack pocket and the PA site)
  is layer 4's, gating the placement freeze before the layout of A, D and P. If FEA-004 closes in failure with no
  thermal fix, the route back to the owner on D-02b's closed-lid scope would reopen this layer for that item (m14).
- **Nothing lowered, dropped, weakened or narrowed.** None found in this change:
  - REQ-077's acceptance gains part (1) and keeps its earlier text as part (2);
  - E3-L's pass line is unchanged; E3-H gains a run and loses none;
  - REQ-016 and REQ-072 keep their statements and REQ-072 keeps its FAIL; M1 is not shortened;
  - no registry id was removed (`953f5658` to `eb9f9030`: seven added, M-02 and SC-51 to SC-56; 22 changed in notes,
    titles, evidence bindings, `waits_on` or `why` only, besides REQ-077's acceptance and sources).
- **Session choices marked as the session's.**
  - SC-21 (now stated to govern), SC-49 and SC-50, SC-51 to SC-56 (with `drafted_as`), the heat stage, BANK-R1,
    storage and the rest in CONOPS 7a, each with its reason and reversal;
  - M-02 is marked as the owner's and "reported, not asked";
  - the validator now refuses an SC- id no entry defines, and its fixtures pass.

## 6. Findings of this pass

### BLOCKING

None.

### MINOR (new in this pass; none changes a mode, a requirement, an interface, a part, an outline or a protection)

**n1. P15 is missing from two of REQ-077's verification references.** CONOPS line 715 ("verified by `TEST-PLAN.md`
E3-H") and 7a's hot-stop row (line 1168, "`TEST-PLAN.md` E3-H") name E3-H alone. REQ-077, the Hot stop row and
TEST-PLAN name E3-H with P15. Fix: add P15 in both places.

**n2. P15's resistance list does not match its steps.** The list gives +46.5 C (4.61 kohm), but no step sits at
+46.5 C, and the +50.0 and +46.0 C steps have no value. On the same B value they are about 4.10 and 4.69 kohm
(computed here). Harmless, because every setting is read back in DAStatus2(). Fix: list the values of the steps
actually run.

**n3. P15 has no negative cases.**
- A single reading at or above +56.5 C should not act (CONOPS's "two readings in a row").
- A reading taken straight to +57.0 C should act as H1 first, since H2 requires H1 to be acting.
- With HOT-R1 held high, the reduced-mode-and-outlets-off fallback of CONOPS 4e (row 945) and FW-C14 is not checked;
  only the TMP117 steps are.
Adding these would make P15 test the rules as written. Also, P15's "never at or above OTD" should follow OTD down if
P14 lowers it (CONOPS 4c: H1, H2 and C1's cell trigger move with OTD).

**n4. FW-C09's round-8 fallback is triggered differently from CONOPS 4c (layer 5 text).** FW-C09 triggers it on "the
sensor controller's pack readings stop for 10 s". CONOPS 4c (lines 673 to 675) and FW-C14 trigger the lost-controller
fallback on HOT-R1 held high. CONOPS chose the line precisely so that the heat stage as generated, where the readings
stop reaching any module by design, is not taken for a lost sensor controller. As written, FW-C09 would fire in that
stage and "shed to the reduced mode", which, read from the heat stage, would raise slot 3. Fix: state FW-C09's trigger
as FW-C14's once HOT-R1 is drawn, and say that the fallback never raises a slot.

**n5. CONOPS and PANEL.md lag HW-FW-CONTRACT on the hot stop.** CONOPS lines 680 to 681 still name `PANEL.md` as where
HOT-R1's four states enter the firmware contracts; they are now in HW-FW-CONTRACT (FW-C13, FW-C14, FW-E10), as CONOPS
line 526 says. PANEL section 5's boot order also lacks FW-C14's start-up read of the line, although HW-FW-CONTRACT
lines 18 to 20 say PANEL "is corrected with it". This is the remainder of m13, tracked in the layer 5 integrator line.
Fix: point line 681 at HW-FW-CONTRACT; PANEL.md's duties land with layer 5.

**n6. One more stale layer-2 row in CONTINUATION-BRIEF section 8 (line 451).** The row "E5 test with a vent" still
reads "edit owed", although TEST-PLAN E5 and E8 were corrected (lines 28 and 31) and CFL-008 reads CONFLICT_RESOLVED.
The first check's B4 (d) did not list it. Its "Follow" column is right. Fix: mark it superseded.

**n7. START-HERE section 2 (line 102) still says the reduced mode is "still to be defined".** It reads "a closed-lid
reduced mode (still to be defined, LAYER-STATUS layer 2)". The page frames everything outside section 3a as the
`e3aedb25` record, but this is the handover's entry page. Fix: correct it in the commit that records layer 2's status.

**n8. Layer 2's integrator line omits two items that ENGINEERING-QUESTIONS indexes against layer 2.** Its list of
later-stage items does not name M-02 and S-53 (EQ-13) or BAT-F19 (EQ-25), although the index lists layer 2 as affected
by both. Neither holds layer 2 (section 4, item 2.12; section 5). Fix: name them in the line with that reason, so the
"not hidden" test can be read where the status is.

**n9. Two figures differ between records (layer 3's text).**
- CFL-017's statement quotes OPERATING-ENVELOPE section 8's +65 to +71 C, the 7 September rises. EQ-25 and section 8's
  current bounds give +61.6 to +74.2 C. Both are above +60 C, so no conclusion changes.
- EQ-13 and CONOPS M1 say about 266 W of panel, while S-53 says about 270 W.

**n10. EMCON.md and REQ-071 still describe the superseded 5G mechanism (layers 3 and 4, tracked in layer 4's integrator
line).** EMCON.md 5a row 5's "required by SD-EMC-1" cells, and REQ-071's desk acceptance ("T_off, T_cut and the rail's
decay"), describe the staged removal that round 8 replaced. The requirement's bound (20 s) still holds and CONOPS 4b.1
is right. The acceptance's wording should name the round-8 path when layer 4 rewrites row 5.

### MINOR carried from the first release check

Still open as the first release check described them: m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12, m14, m15 and
m16. Spot-checked here: m1, m5, m6, m9, m10, m12, m14 and m16. m13 is partly answered: HW-FW-CONTRACT carries the
firmware rows, and PANEL.md's own duties remain at layer 5 (n5). m12 is narrowed by the observation in section 3.

## 7. What stays open elsewhere, and does not hold layer 2

These items stay open where they belong, and CONOPS names each:
- HOT-R1 on boards A and E, with REQ-077 FAIL at desk until it is drawn (S-57, EQ-22);
- BANK-R1 on board B, with REQ-052 FAIL on B as generated (S-54);
- the reduced mode's preconditions on board B (FAB-02, FAB-03, CON-003, CON-022, the supervisors' status path);
- the non-destructive hardware stage (S-58, EQ-23);
- the hot stop's firing inside the envelope and the enclosure conductance (FEA-004, EQ-05, T-H1);
- the cold end's 3.6 W/K bound (S-55);
- M1's balance (S-53, and M-02 for the owner, EQ-13);
- BAT-F19 (EQ-25);
- the pack's transport classification (REQ-069, EQ-03).

A layer is not held open by a later board's work (prompt section 1). If one of these closes in a way that changes a mode
or a product decision, prompt section 8 applies: layer 2 reopens for that item only, and a new version is issued. The
two routes that could do so are FEA-004 ending in an owner trade on D-02b's closed-lid scope, and M-02 choosing a
different pack.

## 8. Verdict

**PASS for this pass: no blocking finding.** The four blocking findings of the first release check (B1 to B4) are
closed on the text at `eb9f9030`, and every figure checked reproduces. The fixtures of the envelope and the registry
pass on a clean copy of the commit. The layer's scenarios, envelope, simultaneity, core-function behaviour and product
decisions meet the owner's section 3 row and his section 2 tests. On its content, **layer 2 meets the owner's COMPLETE
test for its own engineering purpose at `eb9f9030`** (an AI review, not a qualified review).

What remains before it can be *recorded* COMPLETE is the release step, not engineering. The owner's definition asks for
"a versioned package another engineer can use", and nothing of `fnd/rel2` is pushed or in a handover snapshot:

1. **Integrate onto the current `main` (`391d8579`, not `953f5658`: section 1).** Re-apply the branch with this record
   filed. The shared files `PANEL.md`, `ARCHITECTURE.md`, `ENGINEERING-QUESTIONS.md`, `LAYER-STATUS.md`,
   `pcb_requirements.yaml` and `pcb_interfaces.yaml` were also changed by set 5, so the layer-2 files are expected to
   change only by main's own edits. Check that by diffing each layer file against its sha256 in section 1. Then
   re-pin, re-run the two fixture sets once, and re-read HOT-R1's premises on the set-5 generators (done here at
   `391d8579`: they hold).
2. **Mark CONOPS baselined** in the commit that files this record (its header, and the Review A definition), and
   update layer 2's integrator line and START-HERE line 102 (n7).
3. **Carry the layer in the next versioned handover snapshot**, whose manifest names that commit.

A confirmation limited to those diffs is enough. If the rebase changes a layer-2 statement beyond main's own edits, that
difference needs a fresh look before the baseline is recorded. The minors n1 to n10 and m1 to m16 can be fixed in the
release commit or later; none of them blocks. The items of section 7 stay open with their owners.
