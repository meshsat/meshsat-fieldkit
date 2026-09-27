# AI review (not a qualified engineering review)

## Layer 3 (requirements) against the owner's COMPLETE test, at `f2b7fa66`: 27 September 2026

MESHSAT-1357. Reviewer: one fresh AI reviewer session (a Claude subagent) that wrote none of the requirements
registry, its trace page, the test plan's trace, the Review B record, the targeted fixer's answers or the integration
commits, and was given only the owner's execution prompt, the layer status page and the task. This is an **AI
review**: it is not a qualified engineering review, it replaces none of the qualified reviews the records require
(owner ruling D-09, `v2/docs/reviews/REVIEW-ROUTES.md`), and it establishes no circuit's correctness. Prototype
design: nothing in this kit has been built, ordered, powered or field deployed, and nothing below is a physical
result. Written 27 September 2026, 13:28 CEST.

**Commit judged:** `f2b7fa669eba97186af71362230b1895f0bcad48`, branch `fnd/r8int4` (8 commits on main `38dcd764`, not
pushed), worktree `$SP/wt/r8int4` (`$SP` is the session scratch directory). The tree was clean when read, apart from a
parallel reviewer's untracked layer 1 record, which this review did not read. Nothing but this file was written in the
worktree; every tool run happened in a `git archive` export of the commit under `$SP/rv-l3/exp`, except two read-only
runs named below.

**Criteria.** The owner's execution prompt of 27 September 2026 (`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`),
section 2 (COMPLETE) and section 3's layer 3 row: "Source-linked, measurable requirements with acceptance conditions,
applicability, allocation and verification stage/method. Resolve contradictions. Distinguish needs, design choices,
assumptions and historical decisions." The project's own acceptance items 3.1 to 3.18 (`v2/docs/handover/LAYER-STATUS.md`,
layer 3, the audit at `e3aedb25`) and its integrator line (line 505). The six blocking findings and fifteen minors of
Review B's first pass (`v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md`), which the integrator line says were
answered by the targeted fixer c23 and closed by a verifier whose re-check "on the merged registry" was not run (its
remaining item 1). This review is that re-check as well as the release judgement.

**Blocking** means: an acceptance item not met; a claim contradicted by its source or by another current record; a
choice presented as the owner's that is the session's, or the reverse; a closure that lowers a requirement, drops a
function, weakens protection or narrows scope; an open question hidden or allocated to a layer that does not own it.

## 1. What was read and run

**Files judged at `f2b7fa66` (sha256, first 16 hex digits):**

| sha256/16 | File |
|---|---|
| `ab65fea491ee5da1` | `v2/ecad/tools/pcb_requirements.yaml` (144 records) |
| `bba64d37f87a6851` | `v2/docs/REQUIREMENTS-TRACE.md` (generated) |
| `a0de0b12ff06ba4e` | `v2/docs/TEST-PLAN.md` |
| `4887ada07f50d808` | `v2/docs/CONOPS.md` (the pinned needs document) |
| `6e4bbde9dbf7e136` | `v2/docs/OPERATING-ENVELOPE.md` |
| `73a797e44d42fa6d` | `v2/docs/V2-SPEC.md` |
| `30bfbbcd4cb418c5` | `v2/ecad/tools/pcb_rules.yaml` |
| `ce95b2e947099a30` | `v2/ecad/tools/pcb_envelope.yaml` |
| `c0458c53923d7925` | `v2/ecad/tools/rules_lib.py` |
| `d9dfa6fb8a1961ef` | `v2/ecad/tools/rules_render.py` |
| `2db0cc0c165aba42` | `v2/docs/handover/LAYER-STATUS.md` |
| `68ea7d30400ff4b5` | `v2/docs/handover/ENGINEERING-QUESTIONS.md` |
| `1d4494487d470bb2` | `v2/docs/handover/START-HERE.md` |
| `021f6e24b3801481` | `v2/docs/handover/CONTINUATION-BRIEF.md` |
| `7a6c679f446b1baa` | `v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md` |
| `add69d02b8232a6b` | `v2/docs/records/hc3/c23-response.md` |
| `c6a8d3693cc962b6` | `v2/docs/records/hc3/blocked-questions-layer-3.md` |
| `d04ab7bdc144337f` | `v2/docs/records/r8int4/citations-reread-r8int4.md` |
| `7e54827497149141` | `v2/docs/HW-FW-CONTRACT.md` |
| `4bcbf31f44560ee1`, `b49f853f450d49ee`, `55620cf51446bfc8` | `v2/docs/PANEL.md`, `v2/docs/ASSEMBLY.md`, `v2/docs/ARCH-PCB-B-IOHA.md` (citation targets) |

**Sources opened to check figures:** `gen_sch_e.py` `f275102965fafa10`; `gen_sch_b.py` `af6e5821e21b70ef`;
`review-packets/battery/THERMAL-COORDINATION.md` section 3; `v2/vendor/power/lt8705a.pdf`;
`v2/vendor/ti/ti-tpd4e001.pdf` `e10f97586a1aa314`; `v2/vendor/battery/samsung-35e-orbtronic.pdf` `5ec577b952b9dc51`;
`v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json` `bb2f165c642a36f0`; `v2/vendor/sciosense/sciosense-as3935-factsheet.pdf`
`b1d889c1768bab4b`; `v2/vendor/standards/mil-std-3009-nvis-2001-02-02.md` `e74d552faac46a8e`;
`v2/vendor/standards/erc-rec-74-01-2022-05.md` `8d4d5d554bcc8ac8`; the LimeSDR Mini 2.0 product page
`f1146105a3c09ebc`; `v2/vendor/SOURCES.yaml`.

**Tools run (supporting checks; a clean validator does not make a requirement right):**
- In the export: `rules_lib.py requirements` gives 144 records, 0 errors, 16 warnings, all of them "git cannot say"
  or "out/rule-audit is not in this tree"; `rules_render.py --requirements --check` gives "is current";
  `tests/run.py requirement` gives 67 passed, 0 failed, 2 skipped.
- In the worktree, read-only with `PYTHONDONTWRITEBYTECODE=1`, `git status` unchanged afterwards: `rules_lib.py
  requirements` gives 144 records, 0 errors, 0 warnings; `--check` current.
- Scripts of this review (stdlib and PyYAML, in `$SP/rv-l3`): every `evidence_bound_to` sha against the file at the
  commit (121 of 121 current); a TBD scan of every live statement, acceptance and provisional field (none); every rule
  of `pcb_rules.yaml` against the live records' `satisfied_by` (59 of 59 named); the TEST-PLAN forward and reverse
  trace; every `file:line` citation against the files changed between the citation anchor `95e078a1` and `f2b7fa66`
  (section 4, R3); the registry diff from `53292f81` (the re-anchor) to `f2b7fa66`.

## 2. Figures checked against their sources

Each was opened and found as the record states it, unless a finding is named.

- **REQ-016 (B4).** `gen_sch_e.py` line 455 declares the panel entry `v_work=25.0, v_max=25.0`; D4 is an SMCJ28A
  (line 469, 28 V standoff, 31.1 V from); R8 102k and R9 7.50k (line 504) with the LT8705A's FBIN regulation of
  1.205 V typical (1.184 to 1.226 V, `lt8705a.pdf` electrical table) give 17.59 V; 100 W at 17.6 V is 5.68 A, under
  F2's and J_SOLAR's 10 A (lines 427, 428). Matches.
- **REQ-072 and SC-37.** PVGIS, Leiden, 40 degrees: September's mean over 2015 to 2020 is 4.01 kWh/m2 a day (3.60 to
  4.59 by year), December 1.13; every month from April to August is higher than September. 72 h x 42.8 W = 3,082 Wh;
  (3,082 - 108) / 3 = 991 Wh a day; / 0.93 = 1,066 Wh; / 4.0 h = 266 W. Matches. CONOPS M1's night: 108 Wh / 42.8 W =
  2.5 h; 21.7 W x 7 h = 152 Wh. Matches.
- **REQ-075 and SC-23.** Samsung INR18650-35E Ver. 1.1: "For cycle life : 1,020mA" (clause 3.5), 3 x 1.02 = 3.06 A;
  "Min 3,350mAh", 0.8 x 3 x 3.35 = 8.04 Ah; discharge -10 to 60 C at the cell surface. Matches.
- **REQ-077 and SC-49 (B1).** THERMAL-COORDINATION section 3: the published hot-side terms 0.71, 0.40, 0.80 and 0.16 K
  sum to 2.07 K (the table's own sum row); 56.5 + 2.07 = 58.57 C and 57.0 + 2.07 = 59.07 C, both inside +60 C; the
  order C1 55.0, H1 56.5, H2 57.0, OTD 57.5 C. The same thresholds and release (+46.5 C) are in CONOPS section 4 and
  4c (lines 335, 618, 619, 630), OPERATING-ENVELOPE section 4 (lines 224 to 228), `pcb_envelope.yaml` (lines 79 to 81)
  and TEST-PLAN E3-H (line 136). Consistent; see m4.
- **REQ-041 (B2).** AS3935 factsheet: "30 seconds later, the storm is within 10 km", "Stay in the shelter for 30
  minutes after the last sound of thunder". Matches; see m8.
- **REQ-034 (B3).** MIL-STD-3009 transcription: Type I and Class B (lines 27 to 36, 44), 5.7.2 with "1.6 x 10^-10 NRB
  (for Class B NVIS)" (line 106), 5.7.2.2's square-wave chart at 20 feet (lines 118 to 122); SOURCES.yaml entry at
  lines 3439 to 3449 with the sha256 of the file read. Matches.
- **CON-025 (B6).** `gen_sch_b.py` lines 763, 786 and 791: U222 and U223, TPD4E001DBVR, one per SIM holder, on the
  holder side. TI SLLS682P: "IO Capacitance: 1.5pF (Typical)", the electrical table giving a typical value only. See m3.
- **REQ-030.** ERC Recommendation 74-01 transcription, Table 2's last row: -57 dBm to 1 GHz, -47 dBm above for
  receivers and idle transmitters; the record's -67 and -57 dBm are 10 dB under. Matches (Review B's m1 answered).
- **REQ-058.** LimeSDR Mini 2.0 page: "Max. Safe Rx Input Power 10 dBm"; the record's +7 dBm is 3 dB under. Matches
  (m3 of Review B answered).
- **CONOPS pin.** `needs_document_sha256` (line 140) equals the sha256 of `CONOPS.md` at the commit
  (`4887ada07f50d808...`). Matches.

## 3. The acceptance items

The owner's row (section 3) and the project's items 3.1 to 3.18, judged at `f2b7fa66`.

| # | Item | Evidence at `f2b7fa66` | Finding |
|---|---|---|---|
| 3.1 | Every record traces to a need of CONOPS section 2, pinned by content | validator 0 errors; the pin equals CONOPS; every parent a NEED-nn | MET |
| 3.2 | Source-linked (owner) | 144 of 144 carry `source`; `source_check` VERIFIED 140, INFERRED 4 (CON-006, CON-011, CON-012, CON-014, each with its derivation) | MET |
| 3.3 | Citations resolvable by a recipient of the snapshot | `sources_read_at: 95e078a1`, which is on no remote branch (`git branch -r --contains` is empty; `eadbe571`, `e3aedb25` and `38dcd764` are on `origin/main`); START-HERE section 9 (line 305) tells the recipient the lines are at `e3aedb25`; 11 citations in 8 records land on other text at the commit judged | **NOT MET** (R3) |
| 3.4 | Measurable acceptance on every requirement (owner) | 0 TBD records; no "TBD" in any live statement, acceptance or provisional field; REQ-003, REQ-004, REQ-014, REQ-016, REQ-018, REQ-030, REQ-069, ASM-002 settled | MET, except REQ-077's prototype half (R4) |
| 3.5 | Applicability (owner) | every live record core (80) or deferred (58) with a basis (NEED_DEFAULT 92, SESSION 25, NAMED 21); SC-02 and ASM-002's exceptions disclosed | MET; Review B's m5 (REQ-074) unanswered, m5 below |
| 3.6 | Allocation (owner) | every record has `allocated_to` (validator and scan) | MET |
| 3.7 | Verification method and phase (owner) | all 144; SCHEMATIC 121, PLACED_BOARD 9, PROTOTYPE 8, RELEASE_PACKAGE 4, ROUTED_BOARD 2 | MET (R4 on the quality of one method) |
| 3.8 | No check needs a later stage's product (owner section 5) | REQ-048 SCHEMATIC on the netlist, final PLACED_BOARD; REQ-004's bound is need-derived (30 s, 60 s, SC-25); CON-013 characterisation; FEA stages clean (`STAGE_CANNOT_NEED`, suite) | MET |
| 3.9 | Contradictions resolved (owner) | CFL-017 the one open conflict, stated as a qualification finding with why layer 3 closes with it (Review B m12 answered); CFL-010 resolved (B6); but the registry contradicts itself and the handover on M1 (R2), CFL-006 reads FAIL while resolved (m1) and CFL-011 is resolved without its reading (m2) | **NOT MET** (R2) |
| 3.10 | Needs, design choices, assumptions and history kept apart (owner) | 19 needs, 3 CHO, 7 ASM, 6 SPD, 29 owner rulings, 50 session choices all `authority: SESSION`, D-06's note labelled the session's (m7 answered), CON-012's acceptance separated (m10 answered), the part-name rule in the header (lines 58 to 61, m13 answered); but six session choices live outside the registry (R5) and the registry calls L-02 the owner's while a session choice closed it (R2) | **NOT MET** (R2, R5) |
| 3.11 | TBDs listed with their effect | 0 TBD; the trace page's TBD list is empty | MET |
| 3.12 | Every critical mission outcome has a measurable requirement | NEED-01 REQ-003; NEED-02 REQ-076; NEED-03 REQ-004, REQ-073, ASM-002; NEED-05 REQ-014, REQ-016, REQ-018, REQ-072; NEED-08 REQ-030, REQ-071; NEED-13 REQ-046 and, idle cells on an input, REQ-077 (B1) | MET |
| 3.13 | REQ-050: TEST-PLAN traces every test to a requirement with its purpose | REQ-050 PASS, bound to TEST-PLAN `a0de0b12`; by this review's parse, 46 rows under a Purpose and Verifies header, each naming at least one record except E10 (out of scope, "none"); 56 distinct ids, none unknown and none superseded; section 4's trace in prose | MET (the reverse trace is a separate note, section 6) |
| 3.14 | Review B held and the registry baselined | `baseline_state: READY_FOR_REVIEW_B` (line 137); S-51 open (line 1842); the Review B record holds only its first pass (FAIL); the verifier's CLOSED for B1 to B6 is stated in the integrator line and in no filed record | **NOT MET** (R1) |
| 3.15 | Every open item is carried by a record | S-20 into REQ-075 (SC-40); S-48 to S-63 and L-07 each named by the records that wait on them | MET; S-53's class, R2 |
| 3.16 | Every BLOCKER or MUST_JUSTIFY rule has a parent record | 59 of 59 rules (44 BLOCKER, 15 MUST_JUSTIFY) named by a live record's `satisfied_by` | MET |
| 3.17 | The trace is generated and current | `--check` current in the worktree and the export; header counts equal the registry's | MET |
| 3.18 | Versioned, portable layer package | the branch is not pushed; the anchor commit is not public; START-HERE's anchor is wrong for this registry (R3); no snapshot is cut from this commit | **NOT MET** (R1, R3) |

**The owner's section 2 tests.** Current and internally consistent: no (R2, R3). Acceptance satisfied: no (above).
Required review: no (R1). Versioned package: no (3.18). No lowered requirement, dropped function, weakened protection
or narrowed scope: none found; from the re-anchor `53292f81` to `f2b7fa66` the registry changed CON-006, CON-020,
REQ-019 and REQ-047's texts, each tightened or corrected (the pocket bounded by the fillet and the legs; the
supervisors off the TPS23861's broadcast address; REQ-019 without its fabrication-release fallback; the dock and
blind-mate stack owed as its own analysis), and B2, B3 and B4's restorations hold. Session choices marked as the
session's: SC-01 to SC-50 yes; SC-HF-01 to SC-HF-06 marked in `HW-FW-CONTRACT.md` but not in the registry (R5).
Open feasibility allocated to its owner: yes for HOT-R1 (S-57, EQ-22, boards A and E), the non-destructive hardware
stage (S-58, EQ-23, the D-09 battery reviewer), whether the hot stop fires inside the envelope (FEA-004, EQ-05),
GND-002 (S-50, layer 4), the case rows (FEA-007, layer 7); **not** for M1 (R2).

## 4. Review B's six blocking findings, re-checked on the merged files

| Finding | What the merged files say | Verdict |
|---|---|---|
| B1, the hot end on an input | REQ-077 (line 7593), core, NEED-13, BLOCKER: act on the measured cell temperature in every mode and input state before +60 C; desk acceptance (a path needing no compute module; thresholds under OTD and inside +60 C by the published budget) and prototype acceptance (E3-H); FAIL at SCHEMATIC on `gen_sch_e.py` until HOT-R1 (S-57), which is board work correctly held outside layer 3. Carried into SC-18, CON-012, REQ-024, REQ-046, REQ-052 and FEA-004 (`blocks` lists REQ-077; its notes name the ambients). The five documents agree on the thresholds (section 2). | CLOSED; residuals R4, m4 and section 6's firmware contract note |
| B2, the mast-down alarm | REQ-041's statement names the alarm and its acceptance sets 10 km and 30 minutes (SC-47), from the maker's factsheet | CLOSED; m8 |
| B3, the NVG target | REQ-034's acceptance: MIL-STD-3009 5.7.2 and 5.7.2.2, Type I Class B, radiance as characterisation, no claim until the examination passes; the transcription is filed with its SOURCES entry | CLOSED; m10 |
| B4, the solar window | REQ-016: at most 25 V open circuit at the coldest, the generator's own `v_max` | CLOSED |
| B5, M1 against REQ-016 and REQ-072 | CONOPS M1 (lines 196 to 209) carries the window, September at Leiden as the design month, no season taken off M1; SC-37's season clause withdrawn | CLOSED as written; the M1 question it leads to is R2 |
| B6, CFL-010 | CFL-010 (line 8837) CONFLICT_RESOLVED on SC-13's one description; the TVS array is CON-025 (line 8944), PASS on U222 and U223; S-13 keeps only the eSIM variant's order code | CLOSED; m3 |

Review B's minors: m1, m2, m3, m4, m6, m7, m10, m11, m12, m13 and m14 are answered in the registry; m5 (REQ-074) and
m9 (REQ-069's dependency) are not changed; m8 and m15 are part of R2 and section 6.

## 5. Findings

Registry line numbers are `pcb_requirements.yaml` at `f2b7fa66`.

### BLOCKING

**R1. Review B has not passed on the merged registry, and the registry is not baselined.**
- *Where:* `baseline_state: READY_FOR_REVIEW_B` (line 137); S-51 (line 1842: "Review B held ..., its findings
  answered, and baseline_state set to name the commit it baselines"), open; `REVIEW-B-LAYER-3-2026-09-27.md` records
  only the first pass (verdict FAIL, section 7); the integrator line (LAYER-STATUS line 505) says B1 to B6 were
  "CLOSED by the fresh verifier (AI)", but no record of that verifier is filed under `v2/docs/reviews/` or
  `v2/docs/records/`, and the same line lists "Review B's re-check on the merged registry (not run)".
- *Why blocking:* acceptance item 3.14 and the owner's "required review". A closure stated only in an integrator line
  cannot be followed by a recipient.
- *What this review supplies:* the re-check of section 4 (all six closed in substance on the merged files). It does
  not supply the baseline, because R2 to R5 stand.
- *Fix:* answer R2 to R5; file this record and the c23 verifier's output (or state that this record replaces it);
  have a fresh reviewer confirm the answers on the commit that carries them; then set `baseline_state` to a
  baselined value naming that commit and close S-51.

**R2. Mission M1: the registry contradicts itself and the handover on who holds M1's duration and on what M1's
failure blocks, and the owner-only routes have no compact engineering question.**
- *Where and what each says:*
  - Registry header, line 67: "L-02 keeps its id: its class was corrected to OWNER_ACTION (D-06 leaves the value to
    the owner)"; line 1589 defines OWNER_ACTION as "something the owner has ruled that he does or sets himself".
  - Closed items, L-02 (line 2225): closed by SC-21, a session choice (line 1358: 72 hours, "D-06 left it for the
    owner to set later and the standing rule forbids asking").
  - `ENGINEERING-QUESTIONS.md` EQ-13 (lines 341 to 353, index line 40): "REQ-016 carries the solar requirement TBD";
    affected "no board once the solar input window is set"; recommends letting "the energy balance wait for L-02 as an
    advisory record", and says the session setting the value "is not recommended because D-06 reserves the value to
    the owner; the standing rule stops questions, it does not transfer a value the owner kept". At `f2b7fa66` REQ-016
    has no TBD, REQ-072 (line 4127) is a core BLOCKER reading FAIL at desk, and SC-21 set the value.
  - S-53 (line 1859), class SESSION, and `records/hc3/blocked-questions-layer-3.md` item 3: on D-06's pack the kit
    "stops every night whatever the solar rating"; the routes are an overnight input (which changes M1's setting),
    D-01's deferred second pack or a larger pack ("both reopen D-06, the owner's"), a re-rated input path of about 300 W
    (which "alone does not cure the night"), or "a residual only the owner can accept"; affected: the pack, the 9 to
    36 V entry, board E's solar stage (D4, F2, J_SOLAR) and board A's front end, "before boards A, E and P enter
    layout".
  - REQ-016's notes (line 4079 onward): "a re-rating would restate this record", `waits_on: S-53`. REQ-016 (at most
    100 W into the stage) and REQ-072 (about 266 W of panel on the reference day, and a night the pack cannot bridge)
    cannot both be met on the architecture of D-06; no conflict record says so.
  - Review B's m8 ("keep it visible in the handover as an owner action outstanding") is listed as not done in
    `c23-response.md`.
- *Why blocking:* three contradictions between current records ("Resolve contradictions"); the handover's one place
  for blocked questions tells a recipient that no hardware waits on M1 and that the session may not set the value,
  while the registry has set it and records that the pack, board E and board A wait on the answer ("may not hide a
  blocker"); and the authority question (does SC-21 stand under the standing rule of 26 September, or does D-06's
  reservation hold) is answered both ways inside the registry. This review does not decide that authority question;
  it is the owner's rulings that conflict, and the records must say which one governs.
- *Fix (lowers nothing; M1 and REQ-072 stay as stated):* (1) state once which governs, SC-21 under the standing rule
  or D-06's reservation, and make the header (line 67), L-02 and EQ-13 agree with it; (2) rewrite EQ-13 as the M1
  question in the section 6 form: exact issue (REQ-072 fails at desk on D-06's one pack whatever the solar rating),
  affected decisions (D-06, D-01, SC-21, REQ-016, REQ-072) and boards (A, E, P, the pack pocket), evidence (S-53, CONOPS
  M1, `blocked-questions-layer-3.md` item 3), the four routes with who may take each, the recommended action, and when
  it must be decided (before A, E and P enter layout); (3) put the owner's half of S-53 (routes b and d) in the class the
  header reserves for it, an owner action (M-nn), so it reads as external authorisation and not as session work; (4)
  state in REQ-016 or a CFL record that REQ-016's window and REQ-072 cannot both hold on D-06's architecture, pending
  that decision.

**R3. The citation anchor is stated three ways, and 11 citations land on other text at the commit judged.**
- *Where:* the registry's `sources_read_at: 95e078a1` (line 114; the trace page repeats it); START-HERE section 9
  (line 305): "Where a code or data file is cited by line (`file:line`), the line is at `e3aedb25`"; `95e078a1` is
  on no remote branch. After the re-anchor (`53292f81`), the layer 5 and 7 merges (`0da2778b`, `c351115d`) changed
  PANEL.md (two lines inserted after line 175), ASSEMBLY.md (lines inserted from line 32) and ARCH-PCB-B-IOHA.md (line
  169 rewritten). Of 367 `file:line` citations in the registry (21 marked "as read at eadbe571"), 106 point into files
  changed since `95e078a1`; 95 still read the same text and 11 do not: CON-004 (IOHA 169 to 173), REQ-012 (PANEL
  187), REQ-013 (PANEL 191), CON-006 (ASSEMBLY 81), REQ-033 (PANEL 185, 187), REQ-034 (PANEL 184), REQ-060 (PANEL 191,
  197), REQ-066 (ASSEMBLY 159, 173). Example: REQ-034 cites `PANEL.md:184`, which at `95e078a1` is the NVG row, at
  `f2b7fa66` the DAY row, and at `e3aedb25` (where START-HERE sends the reader) the TEST and ACK controls line.
  ASSEMBLY.md line 81, CON-006's citation, is now the heading "## 2. Build order".
- *Why blocking:* acceptance items 3.3 and 3.18; a recipient following the package's own instruction lands on the
  wrong text.
- *Fix:* after the last merge that touches a cited file, re-run the re-anchoring to the release commit (reading the
  eight records' passages by hand, as `citations-reread-r8int4.md` did for twenty), set `sources_read_at` to it, push,
  and restate START-HERE section 9 as "at the commit the registry's `sources_read_at` names".

**R4. REQ-077's prototype acceptance can pass without the hot stop ever acting.**
- *Where:* REQ-077's acceptance (line 7593 onward): "where the hottest cell as the gauge reads it reaches the first
  threshold the kit sheds ..., and where it reaches the second the kit shuts itself down"; TEST-PLAN E3-H (line 136)
  is read only during E3-A's and E3-L's runs, "with no chamber time of its own"; section 7 (P10 to P14) tests the pack's
  own layers and not H1 or H2. The layer 2 integrator line records the same gap as a residual (its item 7).
- *Why blocking:* REQ-077 is the core NEED-13 requirement that closed B1. If the chamber runs never bring a cell to
  +56.5 C (a better enclosure than the lower bound), both conditions are vacuous and the requirement reads as met with
  its function never exercised, on the pack or on shore. A verification method that cannot fail is not a settled
  method (owner section 2: "Requirements can be complete when their scope, limits and verification methods are
  settled").
- *Fix:* add to REQ-077 and to TEST-PLAN section 7 a forced-trigger step at room temperature, on the pack and on shore:
  the gauge's hottest reading driven past +56.5 and +57.0 C (a decade resistance on one TS input, as P10 does for the
  second level, or local heating of one cell), with H1's and H2's actions, times and release checked; and the same
  with the sensor controller held in reset and the TMP117 driven past +55.0 and +56.0 C.

**R5. Six session choices are recorded outside the registry.**
- *Where:* SC-HF-01 to SC-HF-06, `HW-FW-CONTRACT.md` section 8 (for example SC-HF-02, the kit I2C bus in three
  segments, and SC-HF-06, the monitor's touch USB on board D's J_USB3); the registry's S-59 and S-61 (lines 1898, 1915)
  cite SC-HF-02 and SC-HF-06, which no registry entry defines; the registry's `session_choices` end at SC-50. START-HERE
  section 9 (line 309): a closer's engineering choice is recorded "in `pcb_requirements.yaml` `session_choices` in the
  SC-nn form". The integrator line lists it as remaining item 3.
- *Why blocking:* acceptance item 3.10 and the owner's section 1 ("do not create a second requirements registry or
  parallel authority"). The choices are marked as the session's where they stand, so nothing is presented as the
  owner's; the defect is the second id series.
- *Fix:* enter the six as SC-51 to SC-56 with question, taken, why and reversal, keep `HW-FW-CONTRACT.md` pointing at
  them, and let the validator refuse an `SC-` id no registry entry defines.

### MINOR (not blocking)

- **m1. CFL-006 reads FAIL while CONFLICT_RESOLVED** (line 7677): its acceptance includes "the enclosure", and
  `v2/cad/pack_4s.py` still draws the 4S4P block (S-27). The header (lines 44 to 49) makes this a policy, but the trace
  page's own legend says "an open conflict reads FAIL on its own sources", so the page reads against itself. Treat it
  as B6 was treated: the settled cell and count resolve the conflict, and the enclosure is S-27's and layer 7's.
- **m2. CFL-011 is resolved but NOT_JUDGED** (line 9126), "until OPERATING-ENVELOPE.md and pcb_envelope.yaml are read
  again". Both now carry SC-17's definition (OPERATING-ENVELOPE lines 214 to 216, "slots 2 and 3, monitor off";
  `pcb_envelope.yaml` line 76), so the reading can be taken.
- **m3. CON-025 reads PASS on a typical figure.** TI publishes 1.5 pF typical and no maximum for the TPD4E001's
  channel capacitance; the acceptance asks for "at most 10 pF by its maker's published figure". The margin is about six
  times, so the verdict is not in doubt, but the record should say it accepts a typical value and why.
- **m4. E3-H's +59 C line sits inside the design's own bound for H2.** On the published terms H2 acts with the hottest
  cell at up to 59.07 C (57.0 + 2.07), before the budget's two TBD terms; E3-H and REQ-077 fail a run at a cell surface
  of +59 C. On an input with idle cells the sensor-lag term (0.80 K at 3.2 K per minute, the 18 A adiabatic rate) is
  far smaller, so the practical risk is low; state which budget the +59 C line comes from, or re-derive H2 with P14
  before the line is used.
- **m5. REQ-074 is still deferred under NEED-07** (line 4902), with no reason given, although it restates the cell
  maker's safety limit for a kit with its pack (Review B's m5, unanswered).
- **m6. SC-10** (line 705) still says "REQ-018 keeps its TBD" beside SC-35 (line 853), which took its values as REQ-018's
  pass lines; mark SC-10 as carried by SC-35.
- **m7. The layer 3 blocked-questions record numbers its open items at `53a98a71`** (S-47 to S-56, one or two below
  the registry at this commit), so a recipient must translate every id; renumber it at release, or give both.
- **m8. The AS3935 factsheet** that SC-47 and REQ-041 rest on is in the tree since `d8233d14` but has no
  `v2/vendor/SOURCES.yaml` entry (layer 6's list).
- **m9. CONTINUATION-BRIEF section 0** (headed H1) still says "CFL-010 stays open only for the SIM TVS array" and that
  the layer 2, 3, 5 and 7 closers are candidates; true of H1, not of a snapshot cut from this commit. Label or update
  it with the next snapshot.
- **m10. MIL-STD-3009's currency is unchecked:** its SOURCES entry says "whether a later revision or validation notice
  supersedes it was not checked"; check ASSIST before the target is used.

## 6. Notes on allocation to other layers (not findings against layer 3)

- **The hot stop's firmware obligations are in no firmware contract.** REQ-077 is allocated to `fw_panel` and
  `fw_sensor`; `HW-FW-CONTRACT.md` and `PANEL.md` carry neither the four line states nor H1 and H2 (no match for "hot
  stop", HOT-R1 or BLK_SPARE), and `pcb_interfaces.yaml` IF-AE-DOCK names pin 12 only as DOCK_SPARE. The hand-off is
  written (`records/hc2/handoffs.md`, item 5 of its summary and section 16), but layer 5's integrator line (LAYER-STATUS
  line 826) does not list it among its remaining items. It belongs in layer 5's list.
- **The reverse trace.** 43 live records whose method includes PROTOTYPE_MEASUREMENT are named in no TEST-PLAN row
  (the integrator line says 42; FEA-007 is new); 25 are core BLOCKERs (REQ-006, CON-002 to CON-005, CON-022, FEA-003,
  REQ-073, REQ-072, CON-006, REQ-071, CON-021, FEA-002, CON-020, CON-026, FEA-001, FEA-005, REQ-075, REQ-049, REQ-054,
  REQ-055, CON-024, CFL-014, REQ-066, FEA-007). Several are tested in their feasibility pages (IOHA section 13, EMCON,
  ZEROIZE, CASE-FIT-UNCERTAINTIES, sometimes by their own test numbers rather than the record ids); REQ-006,
  REQ-049, REQ-055, REQ-066, REQ-075, CON-002, CON-004, CFL-014 and CON-024 are named by id on no page under `v2/docs`
  other than the generated pages, the handover pages, the records and the reviews. Each record's own acceptance states its prototype check, so the owner's
  "verification stage/method" is met at record level; the gap is the test plan's (Review B's m15), for its owner.
- **E5's INT-001** binds only once `pcb_rules_coverage.yaml` names `check_contracts_e5` (integrator item 4): an
  evidence binding for the registry writer, no requirement text.

## 7. Verdict

**Layer 3 is NOT COMPLETE at `f2b7fa66`. Status: IN_PROGRESS**, as the integrator line already states.

What holds: the registry is source-linked, measurable (no TBD remains), applicable, allocated and staged; every rule
has a parent; the needs pin matches; the trace page is generated and current; REQ-050's forward trace holds; no
requirement was lowered, no function dropped and no protection weakened in the merges examined; Review B's six blocking
findings are closed in substance on the merged files, and the figures checked in section 2 match their sources.

What keeps it open, all desk work under existing authority except the owner's own reading of which ruling governs M1's
duration (R2, item 1), which the records must state rather than ask:
- **R1:** Review B not passed on the merged registry; no baseline.
- **R2:** M1: registry against itself and against EQ-13 on authority and on what waits; the owner-only routes have no
  compact question.
- **R3:** the citation anchor stated three ways; 11 citations in 8 records land on other text.
- **R4:** REQ-077's prototype check can pass without the hot stop acting.
- **R5:** SC-HF-01 to 06 outside the registry.

Once R1 to R5 are answered on one commit, a fresh reviewer should confirm them there, and the registry can be
baselined naming that commit. After two unsuccessful passes on the same finding the method changes (the owner's
prompt, section 4).
