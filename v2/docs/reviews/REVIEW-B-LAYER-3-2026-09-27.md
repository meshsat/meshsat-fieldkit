# AI review (not a qualified engineering review)

## Review B, layer 3 (requirements with verification): first pass, 27 September 2026

MESHSAT-1357. Reviewer: one fresh AI reviewer session (a Claude subagent) that wrote none of the requirements registry,
its trace page, the test plan's requirement trace or the closer's drafts, did not assemble them, and was given only the
owner's handover prompt, the layer audit and the closer's return. This is an **AI review**. It is not a qualified
engineering review, it replaces none of the qualified reviews the records require (owner ruling D-09,
`v2/docs/reviews/REVIEW-ROUTES.md`), and it establishes no circuit's correctness. Prototype design: nothing in this kit
has been built, ordered, powered or field deployed, and nothing below is a physical result.

**Criteria.** The owner's handover prompt of 27 September 2026 (`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`
at `e3aedb25`), section 3's layer 3 row ("Source-linked, measurable requirements with acceptance conditions,
applicability, allocation and verification stage/method. Resolve contradictions. Distinguish needs, design choices,
assumptions and historical decisions.") and section 2's COMPLETE test; the layer 3 acceptance items of the handover
audit (`scratchpad/hand/audit.json`, record `layer: 3`, judged at `e3aedb25`); the fifteen checks of the closer's brief
(`drafts/hc3/review-b-requirements-brief.md`). **Blocking** means: an acceptance item not met that the layer claims met;
a claim contradicted by its source or by another record; a choice presented as the owner's that is the session's; a
closure that lowers a requirement, drops a function, weakens protection or narrows scope; a feasibility bound that
includes failure treated as closed where this layer's decision depends on it.

## 1. What was read

**Worktree:** `$SP/wt/hc3` (the session scratch directory, written `$SP` on filing),
branch `fnd/hc3`, read between 06:53 and 07:10 CEST.

- `git rev-parse HEAD` = `e3aedb25c849dbda931888b27093ac6c444621cb` (nothing committed on the branch).
- `git diff --stat`: 5 files changed, 2269 insertions(+), 758 deletions(-): `v2/docs/REQUIREMENTS-TRACE.md` (898),
  `v2/ecad/tools/pcb_board_facts.yaml` (8), `v2/ecad/tools/pcb_energy_chain.yaml` (12),
  `v2/ecad/tools/pcb_pack_protection.yaml` (4), `v2/ecad/tools/pcb_requirements.yaml` (2105).
- Untracked: `drafts/` (the closer's integration kit) and this record. `git status` was the same before and after
  this review; nothing but this file was written in the worktree.

This is not a pinned commit. The registry is written to be re-applied on main by `drafts/hc3/apply_registry.py`, so the
baseline commit will differ from what is judged here; section 6 says what must be confirmed there.

**Files judged (sha256, first 16 hex digits):**

| sha256/16 | File (in the worktree) |
|---|---|
| `b99fca47672aae83` | `v2/ecad/tools/pcb_requirements.yaml` (the registry, 140 records) |
| `3eabb83f4e7daa5e` | `v2/docs/REQUIREMENTS-TRACE.md` (generated) |
| `07af4d0f2b166694` | `v2/ecad/tools/pcb_board_facts.yaml` |
| `39feae15de45d37e` | `v2/ecad/tools/pcb_energy_chain.yaml` |
| `2a16c1eb2205bcb5` | `v2/ecad/tools/pcb_pack_protection.yaml` |
| `b9080983ccc03a84` | `v2/docs/CONOPS.md` (as at `e3aedb25`; the pinned needs document) |
| `e7a90ba054150bb7` | `v2/docs/TEST-PLAN.md` (as at `e3aedb25`) |
| `df8ac22603440bc5` | `v2/docs/V2-SPEC.md` (as at `e3aedb25`) |
| `89de81a11c52f34a` | `v2/docs/OPERATING-ENVELOPE.md` (as at `e3aedb25`) |
| `abd4e687bef6fe0d` | `v2/ecad/tools/pcb_rules.yaml` |
| `c0458c53923d7925` | `v2/ecad/tools/rules_lib.py` |
| `d9dfa6fb8a1961ef` | `v2/ecad/tools/rules_render.py` |
| `01a6137e30fccfb9` | `v2/ecad/tools/tests/test_requirements.py` |
| `636026b7e7e4ec4e` | `drafts/sc.md` |
| `73684a3a2f191037` | `drafts/hc3/README.md` |
| `9a2128d34c83d658` | `drafts/hc3/review-b-requirements-brief.md` |
| `a110a62fc5c9e6fb` | `drafts/hc3/blocked-questions-layer-3.md` |
| `8b84ef5b2e3b95e3` | `drafts/hc3/layer-status-layer-3.md` |
| `5e467bb617ab6a74` | `drafts/hc3/citations-reread.md` |
| `b53c77a958b8adf0` | `drafts/hc3/CONOPS-d11.on-hc2.patch` |
| `a9bafaf8d0afe27b` | `drafts/hc3/NEED-03-public-statements.on-hc1.patch` |
| `63d72b0f2e6729dc` | `drafts/hc3/EXECUTION-PLAN.review-B.patch` |
| `b908487e72238569` | `drafts/hc3/GROUNDING-AND-SHIELDS.patch` |
| `1ebae2b81590fc19` | `drafts/hc3/apply_registry.py` (surveyed for its guards, not run) |
| `8d4d5d554bcc8ac8` | `drafts/hc3/vendor/standards/erc-rec-74-01-2022-05.md` |
| `0f95e97083d7f16c` | `drafts/hc3/vendor/standards/mil-std-461g-requirement-matrix.md` |
| `f6e0c9e663ae1e3d` | `drafts/hc3/vendor/standards/mil-std-810h-method-516-8.md` |
| `bb2f165c642a36f0` | `drafts/hc3/vendor/solar/pvgis-leiden-monthly-2015-2020.json` |

**Sources opened to check figures (sha256/16):** `v2/ecad/tools/gen_sch_e.py` `d120ebfb9afbee6e`;
`v2/docs/feasibility/POWER-THERMAL.md` `bb9c861c9920c8d6`; `v2/docs/ARCH-PCB-B-IOHA.md` `6c3c93b7f32f953a`;
`v2/docs/MESHSAT-709-geometry-appendix.md` `5e942dd41e9e4ed0`; `v2/docs/GROUNDING-AND-SHIELDS.md` `8f305cc23551084f`;
`v2/vendor/battery/samsung-35e-orbtronic.pdf` `5ec577b952b9dc51`; `v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf`
`525d16b2bdee44e5`; `v2/vendor/limesdr/myriadrf-limesdr-mini-2-0-page-20260925.html` `f1146105a3c09ebc`;
`v2/vendor/rockblock/rb9704-datasheet-RB9704-001-JUN26.pdf` `d48acbea28ee2a7d`; `v2/vendor/cm5/cm5-datasheet.pdf`
`80070fefd8db6e8a`. **Sibling worktrees read for what the registry will be integrated with** (not judged here):
fnd/hc2 `v2/docs/CONOPS.md` `ab28e85bebec4e4c`, `v2/docs/TEST-PLAN.md` `a87e66cf431d938d`,
`v2/docs/OPERATING-ENVELOPE.md` `6930e4f05a59ac5c`, `v2/ecad/tools/pcb_envelope.yaml` `6333e5d212f57a78`, and its Review
A layer 2 pass 2 record `77b20ca4042f0855` (06:50, verdict FAIL, P2-B1 and P2-B2 open); fnd/hc1 Review A layer 1 record
`d469a268fe0b8768` (pass 2, PASS with minor fixes).

**Tools run (supporting checks, not the review):** in the worktree, with `PYTHONDONTWRITEBYTECODE=1`,
`python3 rules_lib.py requirements` gives "140 requirement record(s), 0 error(s), 0 warning(s)" and
`python3 rules_render.py --requirements --check` gives "is current". `tests/run.py requirement` was run in a scratch
copy of `v2/ecad`, `v2/docs` and `v2/cad` (vendor linked read-only): 67 passed, 0 failed, 1 skipped. The integration
simulation the closer describes (main `53a98a71` plus fnd/hc1 and fnd/hc2, 388 changes, suite 1670 passed) was **not**
reproduced by this review: it needs a worktree in the shared repository, which this reviewer may not create.

## 2. Figures checked against their sources

Each of these was opened and found as the record states it:

- **PVGIS (SC-36):** the filed JSON gives the September mean on the 40 degree plane as 4.01 kWh/m2 a day (2015 to 2020;
  3.60 to 4.59 by year) and December 1.13; April to August all higher than September. Matches.
- **REQ-072's arithmetic:** 72 h x 42.8 W = 3,082 Wh; less 108 Wh is 991 Wh a day; / 0.93 = 1,066 Wh; / 4.0 h of
  full sun is about 266 W. Matches, and the FAIL does not depend on the planning figures within their bounds.
- **Samsung INR18650-35E Ver. 1.1:** clause 3.5 "For cycle life: 1,020mA" (REQ-075's 3.06 A for 3P); minimum 3,350 mAh
  (SC-22's 8.04 Ah = 0.8 x 3 x 3.35); 3.12 discharge -10 to 60 C; 3.13 storage -20 to 25 C for a year, -20 to 45 C for
  three months; 7.11 ex-factory 3.49 to 3.69 V; "Don't leave, charge or use the battery in a car or similar place where
  inside of temperature may be over 60 C". Match.
- **LimeSDR Mini 2.0 page (REQ-058):** "Max. Safe Rx Input Power 10 dBm, Absolute maximum". Matches.
- **RockBLOCK 9704 datasheet (REQ-010):** "Data transfer packet size flexible from 25 to 100,000 bytes". Matches.
- **CM5 datasheet (SC-41):** "Raspberry Pi Ltd doesn't support certification with non-approved antennas". Matches.
- **POWER-THERMAL.md section 7.2 (REQ-018, REQ-059, SC-34):** PS-ALLTX 203.8 W; 15.31 V needed on main's pack path,
  0.19 V under the 15.5 V floor; PA alone above 12.4 V; K1 60 s; K2 flange at most +75 C; C4 +85 C. Match.
- **gen_sch_e.py (REQ-016):** D4 SMCJ28A, R8/R9 FBIN 17.6 V, F2 10 A, J_SOLAR 10 A, 5.68 A at 17.6 V. Match, but see B4:
  the generator declares the panel entry at `v_max=25.0` ("about 25 V cold").
- **ARCH-PCB-B-IOHA.md section 15 (REQ-052's FAIL):** Iridium and the panel controller on bank 1, GNSS on bank 2, APRS on
  bank 3, the LoRa module on slot 3's SPI; no single slot carries the owner's example with the SOS path. Matches.
- **MIL-STD-461G transcription (SC-42):** Ground, Army row marks CE102, CS101, CS114, RE102, RS103 "A". Matches.
- **MIL-STD-810H transcription (SC-13):** under 45.4 kg and under 91 cm, man-portable, 122 cm, 26 drops. Matches.
- **ERC Recommendation 74-01 transcription (SC-37):** reference bandwidths 1 kHz, 10 kHz, 100 kHz, 1 MHz; receiver and
  idle-transmitter line -57 dBm to 1 GHz, -47 dBm above. Consistent with the published recommendation as this reviewer
  knows it; the transcription names the file's sha256 (not re-fetched here).
- **BQ4050 TRM SLUUAQ3A:** 5.4.2 "Charger voltage must not be present for the device to enter SHIP SHUTDOWN mode";
  13.1.8 FETs off at Ship FET Off Time, SHUTDOWN "if no charger present is detected"; 5.4.4.2 EMSHUT through the MFC
  sequence opens both FETs. See minor finding m4.
- **Citation sample:** 32 of the 302 `file:line` citations, drawn at random across records, owner rulings and session
  choices, were opened at `e3aedb25` (the worktree's files); every one lands on the text the record relies on (two needed
  the long appendix line 3056 and V2-SPEC line 73 read to their end). No cited file is missing.

## 3. The acceptance items

| # | Item (source) | Evidence in the worktree | Finding |
|---|---|---|---|
| 1 | Every record traces to a need of CONOPS section 2, pinned by content (owner s.3; audit) | validator 0 errors; `needs_document_sha256` equals sha256 of `CONOPS.md` at `e3aedb25` (`b9080983...`); the apply script re-pins after checking the merged needs table | MET here; re-pin to be confirmed at integration |
| 2 | Source-linked (owner s.3) | 140 of 140 carry `source`; VERIFIED 136, INFERRED 4 (CON-006, CON-011, CON-012, CON-014, each with its derivation); REQ-023's former "none (gap)" now cites the MIL-STD-810H transcription | MET |
| 3 | Citations resolvable by a recipient (owner s.3, s.6; audit) | `sources_read_at: e3aedb25`; 302 citations, none to a missing file; 32 sampled, all correct; the four pass-line documents are in `companion_documents`, filed only at integration | MET in the worktree; the four documents must be filed at integration (section 6) |
| 4 | Measurable acceptance on every requirement (owner s.3; audit) | TBD list empty; retyped records read by name (section 4, check 3) | **NOT MET as claimed:** B3 (REQ-034), B4 (REQ-016); minor m1, m2 |
| 5 | Applicability (owner s.3) | every live record carries `prototype_1` with a basis; SESSION deferrals name their choice (validator) | MET; minor m5, m6 |
| 6 | Allocation (owner s.3) | validator | MET |
| 7 | Verification method and phase (owner s.3) | validator; SCHEMATIC 118, PLACED_BOARD 8, PROTOTYPE 8, RELEASE_PACKAGE 4, ROUTED_BOARD 2 | MET |
| 8 | No requirement's check needs a later stage's product (owner s.5; audit) | REQ-048 (line 6296) now SCHEMATIC on the netlist, PLACED_BOARD final; REQ-004 bound set from the need (SC-24); CON-013 retyped to characterisation; FEA stages pass `STAGE_CANNOT_NEED` | MET |
| 9 | Contradictions resolved (owner s.3; audit) | CFL-003, CFL-006 sources corrected; CFL-018 recorded; CFL-007/008/009 resolve on fnd/hc2's TEST-PLAN at integration; CFL-010, CFL-017, CFL-018 stay open | **NOT MET as claimed:** B5 (CONOPS M1 against REQ-016, REQ-072 and SC-36), B6 (CFL-010 kept open on a board B item); B1's contradiction |
| 10 | Needs, design choices, assumptions and historical decisions distinguished (owner s.3; audit) | owner rulings, session choices (45, all SESSION), open and closed items, history fields; the owner's `public-docs` ruling recorded from the session's notes of 25 September (confirmed in the session memory) | MET in substance; minor m7, m8, m13, m14 |
| 11 | TBDs listed with their effect (audit) | 0 TBD | MET |
| 12 | Every critical mission outcome has a measurable requirement (audit) | NEED-01 REQ-003; NEED-02 REQ-076 (new); NEED-03 REQ-004, REQ-073, ASM-002; NEED-05 REQ-014, REQ-016, REQ-018, REQ-072; NEED-08 REQ-030, REQ-071 | MET for these; B1 finds the core NEED-13 case of cells soaking hot on an input uncovered |
| 13 | REQ-050: TEST-PLAN traces every test to a requirement and states its purpose (audit) | reads FAIL in the worktree on `e3aedb25`'s TEST-PLAN (0 ids); fnd/hc2's TEST-PLAN (`a87e66cf...`) has a Purpose and a Verifies column on every table, all ids real; the apply script takes the PASS only on that exact text with REQ-076 filled | NOT MET in the worktree; expected at integration, but fnd/hc2's TEST-PLAN must change again for P2-B2 (E3-L), so the hand reading will need redoing |
| 14 | Review B held and the registry baselined (audit) | this record, first pass; `baseline_state: READY_FOR_REVIEW_B` | held; FAIL on this pass |
| 15 | Every open item that is a requirement limit carried by a record (audit) | S-20 closed into REQ-075 (SC-39); new S-46 to S-54 name their layers | MET |
| 16 | Every BLOCKER or MUST_JUSTIFY rule has a parent record (audit finding) | computed here: 59 of 59 rules named by a live record (CON-023 and CON-024 carry 25 of them) | MET; minor m6 |
| 17 | Trace generated and current (audit) | `rules_render.py --requirements --check` current | MET |
| 18 | Versioned, portable layer package (owner s.6; audit) | uncommitted worktree; `v2/docs/handover/LAYER-STATUS.md` absent (a draft row exists); four cited documents not yet in `v2/vendor/` | NOT MET (section 6); not claimed met |

## 4. The brief's fifteen checks

| # | Check | Result |
|---|---|---|
| 1 | Trace to needs, pin | PASS (worktree) |
| 2 | Source-linked, twenty citations | PASS (32 sampled) |
| 3 | Measurable; retypes lower nothing | FINDING: B2 (REQ-041), B3 (REQ-034), B4 (REQ-016); m1 (REQ-030), m2 (REQ-043), m3 (REQ-058), m4 (REQ-042). REQ-003, REQ-004, REQ-010, REQ-011, REQ-014, REQ-018, REQ-023, REQ-025, REQ-028, REQ-033, REQ-040, REQ-059, REQ-061, REQ-063, ASM-002, ASM-005, CON-011, CON-013 judged not lowered; REQ-069 see m9 |
| 4 | Applicability and allocation | PASS; m5, m6 |
| 5 | Method and phase, no later-stage product | PASS |
| 6 | Contradictions | FINDING: B1, B5, B6 |
| 7 | Kinds apart; SESSION never presented as the owner's | PASS with minor m7 (D-06 note), m8 (L-02), m10 (CON-012's acceptance sentence) |
| 8 | Open items carried | PASS |
| 9 | Rules to requirements | PASS (59 of 59) |
| 10 | REQ-050 | not judgeable in the worktree (FAIL on `e3aedb25`); to confirm at integration |
| 11 | Exposures of FEA-003, FEA-004, M1 | PASS for FEA-003 and REQ-072/S-51; FINDING for FEA-004's hot end (B1, m11) |
| 12 | Blocked questions | PASS with minor m9 (item 1's "no board" claim); CFL-017 judged in section 5, m12 |
| 13 | Trace page, em dashes, framing | PASS (0 em dashes in the registry, the trace page and every draft) |
| 14 | Integration rebinds (CFL-001, CFL-016, REQ-072, REQ-050, CFL-007/8/9) | not judgeable: they exist only after `apply_registry.py` runs; the confirmation pass must open them |
| 15 | Reverse trace | 42 records with PROTOTYPE_MEASUREMENT are named nowhere in fnd/hc2's TEST-PLAN; after IOHA section 13, EMCON section 6 and ZEROIZE section 5 are allowed for, core BLOCKERs with no planned test anywhere this reviewer found: REQ-049, REQ-055, REQ-066, REQ-072, REQ-075, CON-006 (REQ-054 appears only in CONOPS; REQ-076 until its id is filled). For the test plan's owner (m15) |

## 5. Findings

Registry line numbers are the worktree's (`pcb_requirements.yaml` at `b99fca47672aae83`). Session choice and open item
ids are the worktree's; on main `53a98a71` the apply script gives SC-12 and above and S-46 and above one number more
(`drafts/hc3/ids.txt`).

### BLOCKING

**B1. The hot end on an input: the registry adopts "no further stage" (SC-17) on a bound that includes failure, and no
requirement says what the kit does before idle cells pass +60 C.**
- *Where:* SC-17 (line 1097, text at line 1111: "No further stage: the kit stays, and on the pack the gauge's discharge
  window ends it"); CON-012 (line 7337); REQ-046 (line 6140, charge and discharge windows only); REQ-052 (line 6798,
  acceptance "E3-L: E3-A's pass line with the lid closed"); REQ-074 (line 4182, "never left where its cells may pass
  ... +60 C", written for transport and storage); FEA-004's notes (line 3267 onward).
- *What the sources say:* fnd/hc2's `pcb_envelope.yaml` (`6333e5d2`) `worst_inside_air_c`: lid closed at the +40 C
  envelope edge, on the independent bound's lowest conductance, 62.1 C after BANK-R1 and 60.6 C as generated (INFERRED
  arithmetic, 40 C plus the stage's rise). On shore or vehicle input the pack carries no current, so its cells sit near
  the inside air; the gauge's OTC holds charge and OTD opens the discharge FET, neither removes heat, and C1 has nothing
  left to shed. The maker forbids leaving or using the cells above +60 C (35E Ver. 1.1, "Environmental misusage"), and
  fnd/hc2's TEST-PLAN E3-L (line 135) makes "every cell surface at most +60 C throughout ... no permanent protection
  action" REQ-052's pass line, so at that corner the kit as defined fails its own acceptance on shore, not only on the
  pack, with the second level's over-temperature protector (its window starts at 62.7 C, TEST-PLAN P10) as the first
  protective action that removes the cause.
- *Why blocking:* this layer records SC-17 as a settled choice and REQ-024's statement treats the hot end as behaviour
  on measured temperatures, "the ambient ... being a bound until measured"; that argument runs out at the recorded low
  conductance on an input, which is a feasibility bound including failure treated as closed. NEED-13 (pack safety) is
  core, and no core record requires the kit to act before idle cells leave the maker's limit. FEA-004's notes list what
  it would reopen (REQ-018, REQ-059, REQ-014, REQ-072) and omit this. The same gap was found at layer 2 by its Review A
  pass 2 (P2-B2, 06:50), after this registry was written (06:40); it is confirmed here independently from the sources
  above.
- *Fix (lowers nothing; +40 C and REQ-052 stay):* once layer 2 defines the final thermal control past the heat stage
  (on the pack and on an input), carry it into SC-17, CON-012 and REQ-024, and add a core requirement under NEED-13 (or
  extend REQ-046): in every use state, on the pack or on an input, the kit sheds every module and holds the charge
  before any cell passes a stated threshold under +60 C less the gauge's error budget (PROVISIONAL thresholds, the
  session's, with the reading used where the gauge is not reachable), with E3-L's abort at the cell surface as its
  test; add REQ-052's cell line and this control to FEA-004's list of what a failure reopens.

**B2. REQ-041 drops the owner-approved lightning mast-down alarm.**
- *Where:* REQ-041 (line 5795), acceptance at line 5805: "its only alarm levels are REQ-042's (SC-44)"; SC-44 (line
  940).
- *Source:* appendix 32.50 walk-through (`MESHSAT-709-geometry-appendix.md:2802`): "Sensors, all **approved as
  proposed**: ... (6) AS3935 lightning detector with a mast-down alarm"; `V2-SPEC.md:65` "AS3935 lightning detector
  with a mast-down alarm". No other record carries it (the registry mentions lightning only in D-01, D-05 and REQ-041's
  statement).
- *Why blocking:* a closure that drops an owner-approved function (deferred under D-01, but "every ruled function
  stays designed and fitted").
- *Fix:* REQ-041 states the mast-down alarm with a measurable level (for example the AS3935's reported storm distance
  at or below a stated class, taken as a session choice with its reason and reversal), and keeps "no other accuracy
  target" for the rest.

**B3. REQ-034 lowers NEED-09's night-vision-compatible panel to "no claim".**
- *Where:* REQ-034 (line 5291), acceptance at line 5300; SC-44.
- *Source:* NEED-09 (line 169; CONOPS section 2): "give a night-vision-compatible panel (NVG)". D-01 (line 233) defers
  the "NVG claim", and says every ruled function stays designed and fitted. At `e3aedb25` the acceptance kept a
  compatibility target owed ("night-vision compatibility of the light guides, LEDs and monitor is TBD"); the audit
  listed board C's LEDs and filters as its downstream parts.
- *Why blocking:* the closure removes the only statement that the panel is to be compatible, so board C's indicators,
  light guides and the monitor's NVG setting now have no design target at all; D-01 deferred the claim, not the
  design. Whether red and amber indicators at the 2 % step are compatible is exactly what a target would judge.
- *Fix:* keep a need-level compatibility target as the deferred design requirement, either a public night-vision
  lighting standard's class and radiance limits filed under `v2/vendor/standards/`, or a measurable viewing criterion
  through an image intensifier at a stated distance, and keep "no document claims compatibility until it is tested".

**B4. REQ-016's window is wider than the generator it says it states.**
- *Where:* REQ-016 (line 3414, statement at 3420: "an open-circuit voltage of at most 28 V at the panel's coldest
  operating temperature"); SC-35 (line 749: "states board E's input window as generated").
- *Source:* `gen_sch_e.py` lines 384 to 418: the SMCJ28A was chosen because it "stands off 28 V, which is still above
  the 25 V a cold 36-cell panel reaches open circuit", and the panel entry is declared `v_work=25.0, v_max=25.0`
  ("about 22 V open circuit at 25 degC and about 25 V cold"), which is what the derating rules judge PV_P's parts
  against.
- *Why blocking:* a claim ("as generated") contradicted by its source; the requirement admits panels between 25 and 28
  V cold that the design's own declaration never considered, and removes the 3 V the generator keeps below the clamp.
- *Fix:* state 25 V, or raise the generator's `v_max` to 28 V and have PV_P's parts judged there, then state it.

**B5. The needs document's M1 and the registry disagree after integration, and SC-36 narrows M1's season outside
CONOPS.**
- *Where:* REQ-016 (DEFINED, 100 W window), REQ-072 (line 3458, "on the reference day of SC-36"), SC-36 (line 768;
  line 777: "M1 is a mission of that season; from October to March no solar-sustained mission duration is claimed").
- *Source:* fnd/hc2's CONOPS (`ab28e85b`), section 3 M1, the text the integration takes: "the LT8705A tracker's own
  limit is **TBD**, board E", "REQ-016's panel class and input window follow from that judgement" (layer 4), "(INFERRED;
  no insolation figure is held in this tree)", and no season. `drafts/hc3/CONOPS-d11.on-hc2.patch` does not touch M1.
- *Why blocking:* contradictions between the registry and its pinned needs document ("Resolve contradictions"), and a
  scope statement on a CONOPS mission made only in a session choice.
- *Fix:* a CONOPS M1 patch on fnd/hc2's file that carries REQ-016's settled window, the PVGIS reference day and, if
  kept, the season (reported to the owner as a statement of what M1 claims); or drop SC-36's season clause and keep
  September only as the design month.

**B6. CFL-010 stays an open core BLOCKER conflict for items that are not a contradiction between sources.**
- *Where:* CFL-010 (line 7087); SC-12 (line 990, the SIM description settled); S-13; the layer status draft
  (`drafts/hc3/layer-status-layer-3.md`) lists "contradictions resolved or open with what resolves them (CFL-010: the SIM
  TVS array on board B)" among the items met.
- *Why blocking:* once SC-12 and fnd/hc1's V2-SPEC land, what keeps CFL-010 open is the SIM TVS array on board B (a
  layer 8 schematic item) and the eSIM variant's order code (layer 6). An open core conflict holds layer 3 on a later
  board's work, which the owner's prompt (section 1) says not to do, and the item is claimed met.
- *Fix:* at integration read CFL-010 as CONFLICT_RESOLVED on the settled description, and carry the TVS array (at most
  10 pF, Quectel HD v1.1 section 4.1.7) as a constraint on board B's SIM lines reading FAIL at SCHEMATIC until drawn,
  and the eSIM order code on the components layer's list. Nothing is lowered: the TVS array stays required.

### MINOR (not blocking)

- **m1. REQ-030's silence line moves with the analyser** (line 4603; SC-37 line 786). "No emission above the displayed
  noise floor" with the floor "at least 10 dB below" the Table 2 line gives different verdicts on different setups.
  Fix the threshold at 10 dB under Table 2 (-67 dBm to 1 GHz, -57 dBm above) in the reference bandwidths, and judge the
  ports of every receiver D-05 keeps on (GNSS, DCF77, lightning) against the receiver line, as the VHF port is.
- **m2. REQ-043's pass line says "is intended to be"** (line 5905) and "or the session's pick if none fits", which can
  admit a fan the statement excludes. Write "each fan is one its maker rates IP68"; a non-IP68 fallback would be a
  statement change taken openly.
- **m3. REQ-058 designs to the absolute maximum with no margin** (line 7205), and NEED-17's "blinding" is not covered.
  State a margin under +10 dBm, and a recovery line after key-down if blinding is meant.
- **m4. REQ-042's "put the pack in its shutdown"** (line 5831) is the gauge's MAC SHUTDOWN, which it enters only with no
  charger present (SLUUAQ3A 5.4.2, 13.1.8); with shore, vehicle or solar present the persisting state is not shown.
  State the FET-open state (EMSHUT through the MFC sequence, 5.4.4.2, opens both FETs regardless) and the input-present
  case.
- **m5. REQ-074 restates the cell maker's safety instruction** but is parented to NEED-07 and deferred (line 4182); it
  is pack safety (NEED-13, core). Consider moving it, or say why deferred.
- **m6. CON-024 is deferred** (line 7636) on the same facts that make CON-023 core under SC-04 (return paths,
  impedance and pairs are conditions of the core bearers' links). The rules keep their own release effect, so the
  practical effect is small; align the applicability.
- **m7. D-06's `note`** (line 331) is the session's reading inside an owner ruling entry, unlabelled. Mark it as the
  session's.
- **m8. L-02 is closed by SC-20** (line 1901), a session planning value, although D-06 reserves the mission duration to
  the owner. Keep it visible in the handover as an owner action outstanding (the record says the owner's setting
  replaces it).
- **m9. Blocked question 1 (REQ-069) says no board depends on the classification.** A route that needs the pack
  carried apart reopens the VHB-bonded mounting (layer 7) and SC-18/SC-19's and REQ-074's pack-fitted transport. State
  the dependency and its decision point. Separately: REQ-069's pass line (line 3780) is satisfied by never claiming a
  route while D-04 says the route "is stated"; the positive obligation lives only in S-50. It was the same at
  `e3aedb25`, so this is not a new lowering, but the handover should say the kit has no established carriage route
  with its pack.
- **m10. CON-012's acceptance** (line 7347) begins "Accepted by the owner (D-02b) as 'one module' in the heat, reached
  on measured temperatures", putting SC-17's trigger in the owner's sentence; the notes correct it. Write "the owner's
  acceptance (D-02b) is one module above +35 C; since 27 September 2026 the session's SC-17 enters it on measured
  temperatures".
- **m11. CON-012's statement names only the lid-closed ambient** (+20.1 C). fnd/hc2's CONOPS heat stage row gives lid
  open +30.8 to +41.8 C on the independent bound after BANK-R1, below the owner-accepted +35 C, which loses NEED-03
  (core) lid open. Say so in CON-012 and in FEA-004's exposures.
- **m12. CFL-017** (line 6686). This reviewer agrees none of its three exits is the session's at desk (a measured pack
  arrangement needs hardware, cells beyond +60 C reopen D-06, and D-02a's scope is the owner's to read), and that layer
  3 can close with it open: it is a qualification finding (the owner's condition that a qualification margin is not an
  error) whose effect is REQ-051's text, not a board. Say that in the record so it does not read as an unresolved
  source contradiction.
- **m13. Part names in requirement statements.** Most are owner-ruled (the device set of 6 September, the LT8705A of
  4 September ruling F, the BQ4050 through D-15), but nothing in a record says which part names are ruled and which are
  the session's; the audit's item stands in part. A line in each record's notes would do.
- **m14. Stale text:** CON-013's `history` still says the record "makes the ambient TBD"; CFL-018 cites
  GROUNDING-AND-SHIELDS.md without a line (the audit read lines 15 and 16).
- **m15. The reverse trace** (check 15): the core BLOCKERs listed there have a PROTOTYPE_MEASUREMENT method and no test
  in any plan this reviewer found. For the test plan's owner; REQ-050 asks only the forward trace.

## 6. What COMPLETE still needs beyond the findings (not findings against a claim)

1. **The worktree is not the deliverable.** Nothing is committed. In the worktree REQ-050, CFL-007 and CFL-009 read
   FAIL and CFL-008 and CFL-010 are open because the TEST-PLAN, CONOPS and V2-SPEC they are read against are still
   `e3aedb25`'s; SC-16 to SC-33 cite CONOPS sections 4c and 4e and TEST-PLAN section 6, which exist only in fnd/hc2; the
   four pass-line documents sit in `drafts/hc3/vendor/` under `companion_documents`. All of it resolves only at the
   integration commit.
2. **Layer 2's inputs are not final.** Review A of layer 2, pass 2, is FAIL with P2-B1 and P2-B2 open; P2-B2's answer
   changes CONOPS 4c, the heat stage row, OPERATING-ENVELOPE section 4, `pcb_envelope.yaml` and TEST-PLAN E3-L, so the
   registry's SC-17, CON-012 and REQ-024 texts and the apply script's hand-read TEST-PLAN guard (`a87e66cf...`) must
   follow (B1).
3. **The integration simulation was not reproduced here**, and the brief's check 14 (the re-bound readings of CFL-001,
   CFL-016, REQ-072, REQ-050, CFL-007, CFL-008, CFL-009) can only be done on the integrated files.
4. **The package:** `v2/docs/handover/LAYER-STATUS.md` does not exist; the layer 3 row is a draft.

## 7. Verdict

**FAIL on this pass. Layer 3 is not COMPLETE.** The registry is a large step forward and most of it holds up against
its sources:
- the TBD list is empty;
- the stage cycles are gone;
- every rule has a parent record;
- NEED-02, NEED-03's fault containment, the charge current and M1's balance have requirements;
- M1's failing balance is kept as a failing requirement and not shortened;
- NEED-03's failure set is decided at layer 3 from the need's own words and is disclosed;
- the citations re-anchor correctly;
- every figure checked in section 2 matches its source.

Six blocking findings stand:
- **B1:** the hot end on an input is closed on a bound that includes failure, and no core requirement says what the
  kit does before idle cells pass +60 C.
- **B2:** the owner-approved lightning alarm is dropped.
- **B3:** NEED-09's compatibility target is lowered to "no claim".
- **B4:** REQ-016's 28 V is not the generator's declared 25 V.
- **B5:** CONOPS M1 contradicts REQ-016, REQ-072 and SC-36, and SC-36 narrows M1's season outside CONOPS.
- **B6:** CFL-010 holds layer 3 open on a board B item.

None needs new evidence, a purchase or an outside contact; B1 waits on layer 2's answer to P2-B2. Once they are
answered and the integration of `drafts/hc3/README.md` has run, the same reviewer should confirm at the integration
commit. That confirmation covers:
- the blocking findings;
- the difference from the sha256 values above;
- the readings the apply script re-binds (check 14);
- the four filed documents.

After two unsuccessful passes on the same finding the method changes (handover prompt, section 4).
