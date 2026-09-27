# AI review (not a qualified engineering review)

## Layer 3 (requirements), second release attempt, at `eb9f9030`: 27 September 2026

MESHSAT-1357. Reviewer: one fresh AI reviewer session (a Claude subagent) that wrote none of the requirements registry,
its trace page, the test plan's trace, the Review B records, the first release review of this layer or the fixes of the
second release attempt, and did not take part in the first release review. This is an **AI review**: it is not a
qualified engineering review, it replaces none of the qualified reviews the records require (owner ruling D-09,
`v2/docs/reviews/REVIEW-ROUTES.md`), and it establishes no circuit's correctness. Prototype design: nothing in this kit
has been built, ordered, powered or field deployed, and nothing below is a physical result. Written 27 September 2026,
15:21 CEST.

**Commit judged:** `eb9f9030989de925d6569bc00a846568fa4d300b`, branch `fnd/rel2` (two commits, `d535c17e` and
`eb9f9030`, on main `953f5658`; on no remote branch), worktree `$SP/wt/rel2` (`$SP` is the session scratch directory).
The tree was clean when read; during the review parallel reviewers' untracked layer 1 and layer 2 records
(`REVIEW-LAYER-1-RELEASE-2-2026-09-27.md`, `REVIEW-LAYER-2-RELEASE-2-2026-09-27.md`) appeared, which this review did not
read. Nothing but this file was written
in the worktree. The tools ran in a `git archive` export of the commit under `$SP/rv2-l3/exp`, except the validator and
the render check, which also ran read-only in the worktree (`PYTHONDONTWRITEBYTECODE=1`, `git status` unchanged).

**Criteria.** The owner's execution prompt of 27 September 2026
(`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`), sections 1 to 3: COMPLETE for the layer's own purpose; a
layer is not held open by a later board's work, but may not hide a blocker; layer 3's row ("Source-linked, measurable
requirements with acceptance conditions, applicability, allocation and verification stage/method. Resolve
contradictions. Distinguish needs, design choices, assumptions and historical decisions."). The project's acceptance
items 3.1 to 3.18 (`v2/docs/handover/LAYER-STATUS.md`, layer 3). The five blocking findings R1 to R5 of the first
release review (`v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2026-09-27.md`, at `f2b7fa66`) and the fixer's answers to them.

**Blocking** means, as in the first release review: an acceptance item not met; a claim contradicted by its source or by
another current record; a choice presented as the owner's that is the session's, or the reverse; a closure that lowers a
requirement, drops a function, weakens protection or narrows scope; an open question hidden or allocated to a layer that
does not own it.

## 1. What was read and run

**Files judged at `eb9f9030` (sha256, first 16 hex digits):**

| sha256/16 | File |
|---|---|
| `fb819e939f2895da` | `v2/ecad/tools/pcb_requirements.yaml` (144 records, 56 session choices, 44 open and 49 closed items) |
| `1c390fdf67ec0405` | `v2/docs/REQUIREMENTS-TRACE.md` (generated) |
| `4f15bd02a6a8be46` | `v2/docs/TEST-PLAN.md` |
| `3ff59edc96a3f8f4` | `v2/docs/CONOPS.md` (the pinned needs document) |
| `43361b02743cf3af` | `v2/docs/OPERATING-ENVELOPE.md` |
| `1747d4ae9d3475df` | `v2/docs/HW-FW-CONTRACT.md` |
| `ad3ba27cef9e0f68` | `v2/docs/feasibility/POWER-THERMAL.md` |
| `ee74646eb4288076` | `v2/docs/ARCHITECTURE.md` |
| `89a11fb01d52f37e` | `v2/docs/PRODUCT-BRIEF.md` |
| `6154bd6c15bdfa6b`, `d9dfa6fb8a1961ef`, `12e0dc352c7a44c5` | `v2/ecad/tools/rules_lib.py`, `rules_render.py`, `tests/test_requirements.py` |
| `30bfbbcd4cb418c5`, `bbcc2b5cbb721372` | `v2/ecad/tools/pcb_rules.yaml`, `pcb_envelope.yaml` |
| `c6d068de990b8b62`, `06960ed5c2340811`, `c90a3ef2d902dd4a`, `0ac50b8e26d2de06` | `v2/docs/handover/LAYER-STATUS.md`, `ENGINEERING-QUESTIONS.md`, `START-HERE.md`, `GLOSSARY.md` |
| `7a6c679f446b1baa`, `1c3bc2d99f9efb51` | `v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md`, `REVIEW-LAYER-3-RELEASE-2026-09-27.md` |
| `699d7a062db56cdc`, `603b5cdbc92bdc91`, `8338e5a3f04c395a` | `v2/docs/records/r8int4/citations-reread-release.md`, `records/rel2/apply_registry.py`, `v2/docs/evidence/COMPATIBILITY.md` |
| `83cca82cce9d4c43` | `v2/docs/records/hc2/sc.md` (the layer 2 closer's drafts) |

**Sources opened to check figures:** `v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf` (`525d16b2bdee44e5`, read as text);
`semitec-103at-2-kempston.pdf` (`e565be10f6b78dee`); `gen_sch_b.py` (`af6e5821e21b70ef`) at `e3aedb25`, `84e52461`,
`08f3665a` and `eb9f9030`; `gen_sch_p.py` (`91ccbb922c427d43`); `v2/vendor/ti/bq25731-datasheet.pdf`
(`3e5e927fdf63cf6a`); `ti-ina226.pdf` (`c9b67f886d4a5241`); `microchip-atecc608b-summary-DS40002239B.pdf`
(`1b21d7b0d5c6265f`); `ti-tca9517a-i2c-buffer.pdf` (`ad2d7dc599458300`); `records/hc5/zer/run-90kHz.txt`
(`2c907bc91dc19c0d`); `records/hc5/kit_i2c_budget.out.txt`; `records/hc2/pwr_red2.out` (`835910e807d588c4`).

**Tools run (supporting checks; a clean validator does not make a requirement right):**
- In the export: `rules_lib.py requirements`: 144 records, 0 errors, 16 warnings, every one "git cannot say" or
  "out/rule-audit is not in this tree"; `rules_render.py --requirements --check`: current; `tests/run.py requirement`:
  71 passed, 0 failed, 2 skipped (67 before this attempt; the four new fixtures are the SC- id checks).
- In the worktree, read-only: `rules_lib.py requirements` 144 records, 0 errors, 0 warnings; `--check` current.
- Scripts of this review (stdlib and PyYAML, in `$SP/rv2-l3`): every `file:line` of every `source` field compared, text
  for text, between the registry at `f2b7fa66` (anchor `95e078a1`) and at `eb9f9030` (anchor `08f3665a`); the same
  citations compared between `08f3665a` and `eb9f9030`; the `file:line` citations outside `source` fields that this
  attempt added; every SC- id in every tracked file under `v2/` against the registry's ids and `drafted_as`; TEST-PLAN's
  forward and reverse trace; which open items a record waits on; the byte-identity claims of the fifteen rebinds (the
  PS-IDLE-SPEC row, TEST-PLAN rows M7, E3-L, E5, E8, CONOPS sections 2 and 2a and its needs table); `git ls-remote` of
  GitLab and GitHub `main` (both `953f5658`, of which `08f3665a` is an ancestor).

## 2. The first release review's blocking findings, re-checked on `eb9f9030`

| Finding | What the files now say | Verdict |
|---|---|---|
| R1, Review B not passed on the merged registry; no baseline | This record is the fresh confirmation R1's fix asks for. `baseline_state` is still `READY_FOR_REVIEW_B` and S-51 open, as the layer 3 integrator line states. The first release review is filed (`6209ec7e`) and the integrator line says it stands in for the c23 verifier, of whom no record exists. | **Confirmation given here; the baseline itself is not yet recorded** (section 5, B-1) |
| R2, M1: who holds the duration, what fails, the owner's routes | One statement throughout: SC-21 governs M1's duration under the standing rule, recorded as the session's, replaced by the owner's own setting. It appears in the registry header (the L-02 sentence), L-02 (closed items), SC-21's `why`, EQ-13, CONOPS M1 (line 213) and 7a (line 1157), and PRODUCT-BRIEF (lines 292 and 293). D-06's own words ("the mission duration for the solar energy balance is set later by the owner") are kept: the owner may still set it. EQ-13 is in the section 6 form (exact issue, affected, evidence, attempts, options with who may take each, recommendation, expertise, cost, and when: before A, E and P enter layout). The owner's part is M-02 (OWNER_ACTION: the second pack, a larger pack, or accepting the residual), which REQ-072 waits on. S-53 keeps the session's part, the input path's rating. REQ-016 and REQ-072 both record that they cannot both hold on D-06's architecture, and neither is restated. | **ANSWERED** (n4 is wording) |
| R3, citation anchor stated three ways; 11 citations on other text | `sources_read_at: 08f3665a`; START-HERE section 9 names it for registry `source` citations. `08f3665a` is on the public `main` of GitLab and GitHub. Of 280 `source` citations, 277 read byte for byte the same at `08f3665a` as at `95e078a1` under their new numbers. The other three are CON-004 (IOHA 169 to 173), REQ-007 (V2-SPEC 53 to 62) and REQ-066 (ASSEMBLY 194), which `citations-reread-release.md` reads by hand. I re-read CON-004 and REQ-066: the text they rely on stands. At `eb9f9030` itself, 279 of the 280 still read as at the anchor; the exception is REQ-050's `TEST-PLAN.md:1-3`, anchored. | **ANSWERED**; three new pointers outside `source` fields are wrong at the anchor (n1) |
| R4, REQ-077's prototype acceptance could pass without the stop acting | REQ-077's prototype acceptance now has two parts. Part (1) is TEST-PLAN P15: the stop forced at room temperature, on the pack and then on shore, by substituting one cell thermistor input. It covers H1, H1's release, H2 through `PI_KILL` with the kit staying off on shore, MAIN above and below the release, HOT-R1's four states, and the TMP117 stand-in at +55.0 and +56.0 C released at +45.0 C. Part (2) is E3-H, including a stepped run beyond the envelope. A step that acted in neither part reads NOT_VERIFIED, and a thermal run that reached no threshold is recorded as NOT_REACHED and stands in for nothing. The first release review's fix is taken in full. HW-FW-CONTRACT FW-C13, FW-C14, FW-E10 and V-C13 carry the same steps. | **ANSWERED** (n8, n9 are precision) |
| R5, six session choices outside the registry | SC-51 to SC-56 each have question, taken, why ending in "Reverse by", sources and `drafted_as` SC-HF-01 to 06. HW-FW-CONTRACT section 8 gains a Registry column, and S-59 and S-61 cite SC-52 and SC-56. `rules_lib.py requirements` refuses an SC- id cited in the registry or in `v2/docs/*.md` or `v2/docs/handover/*.md` that no entry defines, and refuses a malformed or duplicate draft name. Four fixtures test this both ways, and the tree's own fixture shows it is not vacuous. A scan of every tracked file under `v2/` finds no undefined SC- id on a live page. Outside the pages it finds package names (SC-70, SC-76, SC-88), test fixtures, and the layer 2 closer's placeholders SC-L2-01 to 18 in filed records (n3). | **ANSWERED** |

## 3. Figures checked against their sources

Each was opened and found as the record states it, unless a finding is named.

- **P15's substitution (REQ-077).** SLUUAQ3A: section 3.20 "Open Thermistor Permanent Fail (TS1, TS2, TS3, TS4)"
  (an open input is a permanent failure, so the make-before-break decade box is right); 11.2.1.4.2 to 11.2.1.4.5,
  External 1 to 4 Temp Offset, I1, -128 to 127 in 0.1 C, so at most +12.7 K, which cannot bring room temperature to
  +55 C; 13.1.48, `ManufacturerAccess()` 0x0072 `DAStatus2()`, which returns TS1 to TS4. Board P's `J_TS` is a JST-PH
  1x5 carrying TS1 TS2 TS3 TS4 VSS (`gen_sch_p.py` line 40). The resistances from the 103AT-2's B25/85 of 3435 K:
  3.488, 3.326, 3.274 and 4.607 kohm at +55.0, +56.5, +57.0 and +46.5 C, which match 3.49, 3.33, 3.27 and 4.61. See n8.
- **The thresholds.** H1 +56.5 C, H2 +57.0 C, both in two readings in a row, released at +46.5 C; the TMP117 stand-in
  at +55.0 and +56.0 C, released at +45.0 C; OTD +57.5 C. These agree across REQ-077, SC-49, SC-50, CONOPS (lines 335
  and 671), TEST-PLAN P15 and E3-H, HW-FW-CONTRACT FW-C13, FW-C14 and FW-E10, and OPERATING-ENVELOPE section 4.
- **The solar path under H1.** The LT8705A stage is ORed into VIN_RAW ahead of the BQ25731 (ARCHITECTURE lines 279 and
  327). The charger's `CHRG_INHIBIT` therefore holds a solar charge as it holds a shore or vehicle charge, so testing on
  the pack and on shore covers the input states REQ-077 names.
- **EQ-13's arithmetic.** 108 Wh / 42.8 W = 2.5 h; 21.7 W x 7 h = 152 Wh; 42.8 W x 7 h = 300 Wh; 42.8 W x 16 h = 685 Wh,
  6.3 times 108 Wh; a second pack (about 216 Wh aged in all) covers 152 Wh and not 300 Wh. Matches.
- **SC-55's bus timeouts.** BQ25731 tTIMEOUT 25 to 35 ms; INA226 SMBus timeout 28 to 35 ms; ATECC608B (DS40002239B)
  SMBus time-out 25 to 35 ms. Matches "25 to 35 ms".
- **SC-52 and SC-53.** The TCA9517A takes 400 pF on each side (SCPS245E). `run-90kHz.txt` gives 6.72 ms for the longest
  transfer and 0.521 s for the nominal sequence. Matches.
- **SC-51 and SC-56's facts.** `GPIO_FIXED` maps GPIO16 to `HB_CM%d` (line 464 at `08f3665a`; `CM5_PINS` pin 29 is
  GPIO16, line 267); the level stage is `level(Q(5), R(57), "HB%d", "HB_CM%d", ...)` (line 978); every hub port is
  allocated in `PORTS` (lines 903 to 905). The facts hold; the line numbers the entries give do not (n1).
- **The rebinds.** The PS-IDLE-SPEC row of POWER-THERMAL, TEST-PLAN rows M7, E3-L, E5 and E8, and CONOPS sections 2 and
  2a are byte-identical between `953f5658` and `eb9f9030`, as the fifteen new readings say. CONOPS changed only lines 20,
  48, 213, 333, 335, 524, 526, 1138 and 1157, with no insertion.
- **The needs pin.** `needs_document_sha256` equals the sha256 of `CONOPS.md` at the commit (`3ff59edc...`), and the
  needs table is unchanged.

## 4. The acceptance items at `eb9f9030`

| # | Item | Evidence at `eb9f9030` | Finding |
|---|---|---|---|
| 3.1 | Every record traces to a need of CONOPS section 2, pinned by content | validator 0 errors; the pin equals CONOPS; the needs table is byte-identical to the one at `953f5658` | MET |
| 3.2 | Source-linked (owner) | 144 of 144 carry `source`; VERIFIED 140, INFERRED 4 (CON-006, CON-011, CON-012, CON-014, each with its derivation) | MET |
| 3.3 | Citations resolvable by a recipient | anchor `08f3665a`, public; 277 of 280 `source` citations identical, 3 read by hand; START-HERE section 9 agrees | MET, except three new pointers in `why` text (n1, minor) |
| 3.4 | Measurable acceptance on every requirement (owner) | no TBD in any live statement, acceptance or provisional field; REQ-077's prototype acceptance can no longer pass without the stop acting (P15, NOT_VERIFIED) | MET |
| 3.5 | Applicability (owner) | core 80, deferred 58; basis NEED_DEFAULT 92, SESSION 25, NAMED 21 | MET; m5 carried |
| 3.6 | Allocation (owner) | every record has `allocated_to` | MET |
| 3.7 | Verification method and phase (owner) | all 144; SCHEMATIC 121, PLACED_BOARD 9, PROTOTYPE 8, RELEASE_PACKAGE 4, ROUTED_BOARD 2; REQ-077's method settled | MET |
| 3.8 | No check needs a later stage's product (owner section 5) | unchanged from `f2b7fa66`; P15 is a prototype test, REQ-077's desk phase reads the generators; no cycle added | MET |
| 3.9 | Contradictions resolved (owner) | M1 stated one way (R2); CFL-017, the one open conflict, now has its routes in EQ-25; REQ-016 and REQ-072 record that they cannot both hold on D-06's architecture, with the day's energy given to S-53 (the session, layer 4) and the night to M-02 (the owner). REQ-016 is SC-36's window taken from the generator, and its notes say a re-rating restates it, so precedence is already fixed: the session's window gives way, and the need-derived REQ-072 is not lowered. | MET; n4 (wording), m1 and m2 carried |
| 3.10 | Needs, design choices, assumptions and history kept apart (owner) | 19 needs, 3 CHO, 7 ASM, 6 SPD, 29 owner rulings, 56 session choices all `authority: SESSION`; SC-HF drafts entered (R5); SC-21 recorded as the session's and M-02 as the owner's | MET; n3 carried |
| 3.11 | TBDs listed with their effect | no TBD record; the trace page's TBD list is empty | MET |
| 3.12 | Every critical mission outcome has a measurable requirement | unchanged from `f2b7fa66`; NEED-13 now verifiable through REQ-077 (P15) | MET |
| 3.13 | REQ-050: TEST-PLAN traces every test to a requirement with its purpose | 47 rows under Purpose and Verifies, each filled (E10 out of scope, "none"); P15 verifies REQ-077; 57 ids named in the plan, none unknown or superseded; REQ-050 rebound to `4f15bd02` | MET (reverse trace: section 6) |
| 3.14 | Review B held and the registry baselined | this record confirms R2 to R5 answered; `baseline_state: READY_FOR_REVIEW_B`, S-51 open | **NOT MET** (B-1, procedural) |
| 3.15 | Every open item is carried by a record | M-02 by REQ-072; S-53 by REQ-016 and REQ-072. But ten open items are in no record's `waits_on`: L-01, S-13, S-23, S-47, S-51, S-56, S-60, S-61, S-62 and S-63. The same was true at `f2b7fa66`, where 3.15 was marked MET. | MET in substance; letter not met (n7) |
| 3.16 | Every BLOCKER or MUST_JUSTIFY rule has a parent record | 59 of 59 rules named by a live record's `satisfied_by` | MET |
| 3.17 | The trace is generated and current | `--check` current in the worktree and the export | MET |
| 3.18 | Versioned, portable layer package | the anchor is public, but `eb9f9030` is on no remote branch and no snapshot is cut from a commit carrying this content | **NOT MET** (B-2, procedural) |

**The owner's section 2 tests.**
- Current and internally consistent: yes for the layer's own files, apart from the minors below.
- Acceptance satisfied: yes, except 3.14 and 3.18.
- Required review: this record, together with the first release review and Review B's first pass.
- Versioned package: no (3.18).
- Nothing lowered, dropped, weakened or narrowed: none found.
  - REQ-077's acceptance, E3-H and the OWNER_ACTION definition were strengthened or widened.
  - S-53's removed half moved whole to M-02.
  - E3-L's pass line is byte-identical.
  - No statement or pass line of any other record changed.
- Session choices marked as the session's: SC-01 to SC-56, all `authority: SESSION`; SC-21 is stated as governing
  under the standing rule and M-02 as the owner's.
- Open feasibility allocated to its owner:
  - M1's day to S-53 (layer 4) and its night to M-02 (the owner), before A, E and P enter layout.
  - HOT-R1 to S-57 and EQ-22 (boards A and E).
  - The non-destructive stage to S-58 and EQ-23 (the D-09 reviewer).
  - The stop's firing inside the envelope to FEA-004 and EQ-05.
  - BAT-F19 to CFL-017 and EQ-25.
  - GND-002 to S-50 (layer 4).
  - None of them hides a blocker, and none is a decision of this layer that can change architecture, interface,
    component, outline or protection. Each changes whether the design meets a settled requirement, or is the owner's
    reopening of his own ruling.

## 5. Findings

Registry line numbers are `pcb_requirements.yaml` at `eb9f9030`.

### BLOCKING (procedural; no finding of substance remains)

**B-1. The baseline is not recorded (acceptance item 3.14; the last step of R1).**
- *Where:* `baseline_state: READY_FOR_REVIEW_B` (line 148). S-51 is open: "baseline_state set to name the commit it
  baselines".
- *Why blocking:* COMPLETE needs the required review and a baselined registry. This record supplies the confirmation;
  the baseline has to be written.
- *Fix:* one commit on main that:
  - sets `baseline_state` to a baselined value naming the commit that carries this content (the registry at sha256
    `fb819e939f2895da` apart from the edits listed here; identify it by content if the branch is rebased);
  - closes S-51 with this record as its evidence;
  - corrects the three pointers of n1;
  - re-renders the trace page and updates the layer 3 integrator line.

  No other registry change belongs in that commit, so that this review still describes it.

**B-2. No versioned package (acceptance item 3.18).**
- *Where:* `eb9f9030` is on no remote branch; GitLab and GitHub `main` are at `953f5658`.
- *Why blocking:* the owner's COMPLETE asks for "a versioned package another engineer can use".
- *Fix:* push the commit of B-1 to main and cut the next handover snapshot from it.

### MINOR (not blocking)

- **n1. Three pointers SC-51 and SC-56 added are wrong at the registry's anchor and at this commit.** SC-51's `why`
  cites `gen_sch_b.py:257` and `:822`, and SC-56's `why` cites `gen_sch_b.py:764-766`. These are the contract's
  citations at `e3aedb25` (HW-FW-CONTRACT line 9 names that anchor), copied without their commit. At `08f3665a`,
  whose `gen_sch_b.py` is the same file as at `eb9f9030`:
  - line 257 is blank;
  - line 822 is an EMCON comment;
  - lines 764 to 766 are SIM wiring comments.

  The facts sit at lines 267 and 464 (GPIO16 to `HB_CM%d`), 978 (the level stage) and 903 to 905 (`PORTS`). Append
  "(as read at e3aedb25)" or renumber, in the B-1 commit. The header's anchor rule covers only `source` fields; say
  what anchor a `file:line` in `why`, `notes` or `evidence` text follows.
- **n2. The trace page does not render `drafted_as`.** Record evidence on the page still names SC-HF-02 and SC-HF-06
  (lines 625, 877 and 879), and nothing on the page maps them to SC-52 and SC-56. Render "drafted as SC-HF-0n" with
  each choice.
- **n3. The layer 2 closer's placeholders have no `drafted_as`.** SC-L2-01 to SC-L2-18 are cited in filed records:
  `records/hc2/sc.md`, `handoffs.md`, `LAYER-STATUS-layer2.md`, the Review A records of layer 2, and
  `handover/candidates/README.md`. The mapping to SC-17 to SC-34 (checked by question: SC-L2-01 is SC-17's reduced
  mode, SC-L2-05 is SC-21's M1, SC-L2-16 is SC-32, SC-L2-18 is SC-34's BANK-R1) is written nowhere, and the
  validator's globs do not reach those files. GLOSSARY says a cited draft is entered under `drafted_as`. Add
  `drafted_as` to SC-17 to SC-34 (or widen the globs to `records/` and `reviews/`).
- **n4. "Which one gives way" (REQ-016's notes, line 4333) reads as if REQ-072 could give way.** M-02 and EQ-13
  say neither record is restated and a shorter mission is not an option. Say instead that REQ-016's window, the
  session's SC-36, follows S-53's judgement of the input path; that REQ-072 is not restated; and that the night is
  M-02's. Retyping REQ-016's 100 W figure as the generated stage's value (a constraint) would leave no pair of core
  requirements that cannot both hold. M-02's title also says the owner's answer "can move board E's solar stage (D4,
  F2, J_SOLAR) and board A's front end". Those are S-53's; the owner's routes move the pack, its pocket and board P.
- **n5. LAYER-STATUS layer 3, remaining item (2) is already met.** It reads "R3's last step, the anchor commit on the
  public repository once the integrating session pushes", but `08f3665a` is on the public `main`. What remains of 3.18
  is B-2.
- **n6. P15's set points sit on the thresholds.** The decade box is set so that `DAStatus2()` reads +56.5 C and +57.0 C
  exactly. A reading that dithers 0.1 K low never gives "the second reading at or above". Set each a little above its
  threshold, inside the 0.5 K below OTD (for example +56.7 and +57.2 C). Also, the resistances P15 lists are for +46.5
  C, while the steps it runs after H1 and H2 are +50.0 and +46.0 C (4.10 and 4.69 kohm by the same formula).
- **n7. 3.15's letter.** The ten open items named in the table are carried by no record.
  - S-56 names REQ-052 in its own title ("REQ-052's acceptance fails any part outside its published range"), so REQ-052
    should wait on it.
  - The others are board defects judged by rules (S-47, S-60, S-62), board or case items (S-23, S-61, S-63), the review
    itself (S-51), the eSIM order code (S-13, named by CFL-010) and money (L-01).

  Add S-56 to REQ-052, and restate 3.15 as "every open item that can change a record's verdict is carried by it".
- **n8. What PASS needs for REQ-077 when a chamber reaches nothing.** The acceptance says a step that acted in neither
  part is NOT_VERIFIED. It does not say whether P15 alone, with P14's measured gradient inside the budget, is enough for
  PASS when E3-H is NOT_REACHED. State it.
- **n9. E3-H's stepped run exceeds some parts' ratings.** On shore, idle cells sit at the inside air, so H1 at a
  +56.5 C cell means the inside air is at or above the SGP41's +55 C before H1 acts (S-56). Say whether such parts are
  removed for the run or accepted at risk. With the stepped run's 2 K an hour, the sensor-lag term of the published
  budget is negligible, so m4's +59 C line has about 0.7 K in hand there. Say so beside the abort line.

**Carried from the first release review, unchanged at `eb9f9030` and still minor:**
- m1: CFL-006 reads FAIL while resolved.
- m2: CFL-011 is still NOT_JUDGED. OPERATING-ENVELOPE, `pcb_envelope.yaml`, POWER-THERMAL and ARCHITECTURE now all
  carry SC-17's definition, so the reading can be taken.
- m3: CON-025 passes on a typical figure.
- m4: see n9.
- m5: REQ-074 is deferred with no reason given.
- m6: SC-10 still says "REQ-018 keeps its TBD".
- m7: `records/hc3/blocked-questions-layer-3.md` still uses `53a98a71` numbering.
- m8: the AS3935 factsheet still has no `SOURCES.yaml` entry.
- m9: CONTINUATION-BRIEF section 0 is stale.
- m10: MIL-STD-3009's currency is unchecked.

## 6. Notes on other layers (not findings against layer 3)

- **ARCHITECTURE section 8.3 (line 908), edited in this attempt, still gives the envelope a carve-out "above +35 C (one
  module...)".** OPERATING-ENVELOPE section 4 (line 214 onward) enters no carve-out on an ambient reading, and
  `pcb_envelope.yaml` line 34 marks +35 C superseded as a trigger. CON-012 keeps D-02b's "one module above +35 C" as the
  owner's acceptance, which is consistent. Layer 4 should word 8.3 the same way.
- **The reverse trace.** 42 live records whose method includes PROTOTYPE_MEASUREMENT are named nowhere in TEST-PLAN.
  24 of them are core BLOCKERs: CFL-014, CON-002 to CON-006, CON-020 to CON-022, CON-024, CON-026, FEA-001 to FEA-003,
  FEA-005, FEA-007, REQ-006, REQ-049, REQ-054, REQ-055, REQ-066, REQ-072, REQ-073 and REQ-075. Each record's own
  acceptance states its prototype check, so the owner's "verification stage/method" is met at record level. REQ-072's
  72-hour emulator run is the plainest missing row. This is for the test plan's owner.
- **The handover's continuation brief** does not yet tell a PCB engineer that boards A, E and P wait on M-02 and S-53
  before layout entry. The next snapshot's brief should.
- **PANEL.md's hot-stop duties and IF-AE-DOCK pin 12** remain with S-57 (layer 5), as LAYER-STATUS says.

## 7. Verdict

**Layer 3 is NOT COMPLETE at `eb9f9030`. Status: IN_PROGRESS.** Two acceptance items stand, both procedural: the
baseline is not recorded (3.14, B-1) and there is no versioned package (3.18, B-2).

What holds:
- The first release review's R2 to R5 are answered on this commit, and R3 is answered on `08f3665a`.
- This record is the fresh confirmation R1 asks for.
- The registry is source-linked, measurable (no TBD), applicable, allocated and staged.
- M1 is stated one way, with the owner's part as an owner action that is visible and timed.
- REQ-077 can no longer read PASS without its stop acting.
- The session's choices live in one registry, and a validator now refuses a second id series on the pages.
- The trace page is current, and every rule has a parent.
- The figures checked match their sources.
- Nothing was lowered, dropped, weakened or narrowed.
- No decision of this layer that can change architecture, interface, component, outline or protection is missing. The
  open questions that remain are allocated to layer 4, to board work or to the owner, and each is named with its
  deadline.

**What closes it:** the B-1 commit (baseline naming the commit that carries this content, S-51 closed on this record,
n1's three pointers, the trace re-rendered), then B-2 (pushed, and a snapshot cut from it). A commit that makes only
those changes needs no further review of this layer. Any other registry change in it would need one. The minors n2 to
n9 and m1 to m10 can follow in later versions without holding the baseline.
