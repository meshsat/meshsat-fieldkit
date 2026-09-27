# AI review (not a qualified engineering review)

## Review A, layer 1 (vision, product definition and pitch): second pass, 27 September 2026

MESHSAT-1357. This record holds two passes. The second pass is this section; the first pass, as filed at about 02:30
CEST, follows unchanged in its words under "Appendix: the first pass" (its headings moved down one level).

Reviewer of this pass: one AI reviewer session that wrote none of the pages judged and did not assemble them. It was
given the first pass's record and the closer's re-check brief (`drafts/review-a-layer-1-recheck.md`). Session choice
SC-HC1-4 asks that blocking findings be re-checked by the same reviewer; this pass re-checked B1 and B2 against their
sources and, beyond that, judged the whole layer again against the same criteria, which keeps what the choice is for
(a reviewer independent of the writer). This is an AI review, labelled as one. It is not a qualified engineering review
and does not stand in for any review a record in this tree requires (D-09, `v2/docs/reviews/REVIEW-ROUTES.md`).
Prototype design: nothing in this kit has been built, ordered, powered or field deployed, and nothing below is a
physical result.

**Criteria**, unchanged from the first pass: the owner's handover prompt of 27 September 2026
(`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`), section 3, layer 1 row, and section 2 (what COMPLETE means);
the layer 1 acceptance items of the handover audit (judged at main `e3aedb25`); the definition of Review A, layer 1 in
the brief's last section (SC-HC1-4). Blocking means: an acceptance item the layer claims met and is not; a claim
contradicted by its source or by another record; a choice presented as the owner's that is the session's; a closure
that lowers a requirement, drops a function, weakens protection or narrows scope; a feasibility bound that includes
failure treated as closed where this layer's decision depends on it.

## 1. What was read (worktree state)

Worktree `fnd/hc1` at `/tmp/.../scratchpad/wt/hc1`, read between 05:50 and 06:05 CEST. `git rev-parse HEAD` =
`e3aedb25c849dbda931888b27093ac6c444621cb` (nothing committed on the branch). Uncommitted changes, `git diff --stat`:
`README.md` 30, `v2/BUILD.md` 123, `v2/README.md` 36, `v2/docs/PRODUCT-BRIEF.md` 229, `v2/docs/V2-SPEC.md` 109,
`v2/docs/records/README.md` 177 lines touched; 6 files changed, 574 insertions(+), 130 deletions(-). Untracked:
`drafts/`, `v2/docs/records/adj/`, `v2/docs/records/w1/` and this record. Every hash below equals the table at the end
of the closer's re-check brief; none changed during the review.

| file | sha256/16 |
|---|---|
| `v2/docs/PRODUCT-BRIEF.md` | `6a3b23882ff30434` |
| `README.md` | `d33c351f6212d4c9` |
| `v2/README.md` | `6f9b68c398ccd355` |
| `v2/BUILD.md` | `f82b0e793056f5db` |
| `v2/docs/V2-SPEC.md` | `7fef12e23792b3c0` |
| `v2/docs/records/README.md` | `b79ed92a24e22d9d` |
| `v2/docs/records/adj/A08-5g-socket-and-antennas/drafts/web/SOURCES.txt` | `f039a88e5799374e` |
| `v2/docs/records/w1/w1-decisions.md` | `493db60b7d4ab1b6` |
| `v2/docs/records/w1/w1-conflicts.md` | `eb8d1b0648d0a983` |
| `drafts/apply_hc1_registry.py` | `e72eb69c8b61bf44` |
| `drafts/sc.md` | `036d9f1f19cee84c` |
| `drafts/conops.patch` | `f3c0689516dbbb6b` |
| `drafts/execution-plan.patch` | `34a99775ec7ea95c` |
| `drafts/layer2-emcon-face.patch` | `6bd74b4157b29598` |
| `drafts/layer-status-layer-1.md` | `0015647f6f54a2df` |
| `drafts/review-a-layer-1-prompt.md` | `e7296de79b56d859` |
| `drafts/review-a-layer-1-recheck.md` | `35a6eb8ba62ce649` |
| `drafts/README.md` | `60c3e9385234b18b` |
| `drafts/SOURCES-hc1.yaml` | `768a1dd7e91694d6` |
| `drafts/vendor/standards/mil-std-810h-method-516-8.md` | `f6e0c9e663ae1e3d` |
| this record before this pass (the first pass alone) | `121b7db49000dbe0` |

**Sources**, read at `e3aedb25` (`git show e3aedb25:<path>`): `v2/docs/feasibility/EMCON.md` sections 0, 0a (the counts
at its line 149), 4.1, 4.4 (lines 511 to 573), 5a, 6 and 7; `v2/docs/PANEL.md` sections 1, 3 (GPIO 8, line 77), 4 (line
127), 6 and 7; `v2/ecad/tools/gen_sch_c.py` lines 175 to 217 (the LED rail, `Q1`/`Q2`, `R20`, the TX lamp `D3` on
`LED_RAIL`, the toggles); `v2/docs/CASE-MARGINS.md` opening summary, sections 2.2, 3.4 (lines 740 to 757) and 4 (C1 to
C6); `v2/docs/feasibility/POWER-THERMAL.md` section 0, section 6 and 9.4, findings PWR-F07 to PWR-F09;
`v2/docs/CURRENT-EVIDENCE.md` headline and candidate table; `v2/docs/CONOPS.md` sections 1, 2a, 4b and 7;
`v2/docs/ARCHITECTURE.md` section 11 (line 1084); `v2/docs/EXECUTION-PLAN.md` lines 55 to 64;
`v2/docs/reviews/REVIEW-ROUTES.md`; `v2/ecad/tools/pcb_requirements.yaml` (SC-07, SC-08, REQ-071, FEA-001 to FEA-006,
CFL-016); `v2/docs/review-packets/battery/` (exists). Main has moved to `53a98a71`; read there as well:
`feasibility/EMCON.md` line 168 (the same counts), `CURRENT-EVIDENCE.md` (the same headline and declared phases A32, B21,
C24, D12, E17, P4, E5, SCH-002 FAIL on A and B, INCONCLUSIVE on C, D, E and P), `CONOPS.md` line 316 and `PANEL.md` lines
5 and 127 (still the older EMCON and TX lamp wording, see I5 below). The MIL-STD-810H Method 516.8 file the transcription
names (sha256 `24686aad175659ec...`, the same bytes in the scratch directory's `hc1dl/` and `dl/m516.pdf`), page 516.8-33,
re-read with `pdftotext`; the owner's `public-docs` ruling in the session memory file `project_owner_rulings_2026_09_25.md`
(line 23).

**Checks run**, all read-only in the worktree (its `git status` was the same before and after):
- `python3 drafts/apply_hc1_registry.py --root <wt> --dry-run`: every assertion passes, including that V2-SPEC line 24
  keeps its circuit description byte for byte up to "a mode the module's firmware carries out" and that lines 32, 34, 35
  and 43 and corrections 2, 4, 6, 7, 8, 9, 12, 13 and 19 are byte-identical to `e3aedb25`; on `e3aedb25`'s registry it
  numbers the choices SC-12 to SC-15 (on main, where SC-12 exists, the next free numbers; the closer reports SC-13 to
  SC-16); V2-SPEC would be bound at `2e76cf54ba924700`. Nothing written.
- `python3 tools/rules_lib.py requirements` from the worktree's `v2/ecad`: 3 errors (REQ-005, CFL-013, CFL-016 bound to
  V2-SPEC.md at `df8ac22603440bc5`) and CFL-010's warning, the rebind the script does.
- A script that re-hashed every row of the section "Filed 27 September 2026" of `records/README.md` against the filed
  bytes: 130 rows (127 files and the rewritten-on-filing rows), 0 mismatch, 0 filed file unlisted. `w1/` is
  byte-identical to `drafts/` of the `fnd/w1` worktree.
- A scan of the five pages, the filed records and the drafts for runner paths and internal host names: none. A scan for
  em dashes: none.
- A scan of every file path the five pages cite: all resolve except `v2/vendor/standards/mil-std-810h-method-516-8.md`
  (installed by the apply script, I3) and `sensor_pod.py` (N2).

Not run: the test suite, the claims screen, and the integration on main `53a98a71` (the closer reports them on a
scratch copy; not re-checked here).

## 2. The first pass's blocking findings

**B1 (EMCON statements against `feasibility/EMCON.md` section 0a and FEA-002): CLOSED.**
- `v2/docs/PRODUCT-BRIEF.md:96-121`: the intent (appendix 32.50 item 3, D-05), the circuit as generated at `45bde541`,
  the latency REQ-071 sets (1 s; 20 s for a running 5G module; EMCON.md 5a and REQ-071's acceptance agree), then
  section 0a's reading: 17 transmitters, none dark end to end at desk or on a bench; locally 14 of 17 closed at desk and
  three open, the SA868 (no published receive threshold for the PTT pin held at 2.677 V or more, bench E-01; EMCON.md
  4.1 and section 7), the RockBLOCK 9704 (its own supercapacitors, about 16 J, ENABLE held by the firmware-driven
  expander, the hardware ENABLE owed, the module's behaviour when ENABLE falls in no held document; EMCON.md 4.4 lines
  536 to 573) and the 5G module (SD-EMC-1 not drawn); end to end 0 of 17, each row waiting on the shared items, on
  SD-EMC-6's lamp (not drawn) and on the latency; no bench row; FEA-002. Each figure matches its source at `e3aedb25`
  and on main.
- The TX lamp (`PRODUCT-BRIEF.md:118-120`, `v2/BUILD.md:106`, `V2-SPEC.md` correction 26): `gen_sch_c.py` at `e3aedb25`
  feeds `D3` from `LED_RAIL` through the 300 ohm resistor, and `LED_RAIL` exists only while `Q2`, held off by `R20`,
  is driven from `PANEL_PWM`; `PANEL.md:77` says the pin boots low. The pages are right; `BUILD.md:106` keeps MAIN PWR
  and the EMCON gates as the parts that act without firmware.
- `v2/README.md:5`, `v2/BUILD.md:21`, `V2-SPEC.md:24` and `:76`: the same reading, each with the three open rows, 0 of 17
  end to end, the shared items, the latency and FEA-002. `V2-SPEC.md` correction 26 (lines 209 to 221) says what changed
  and why, and the apply script's CFL-016 re-read says it too.
- The brief's open-items row for FEA-002 (`PRODUCT-BRIEF.md:259`) states why layer 1 can close with FEA-002 open: the
  brief claims nothing about EMCON as met; the one bound that includes failure (whether the RockBLOCK 9704 falls silent
  within 1 s when ENABLE falls with about 16 J on its side) decides layer 4's feasibility and board B's circuit; the
  kit's purpose, its users and the core list (hardware EMCON in it) stand under either outcome; and if no hardware path
  meets a row's limit the requirement is reopened in its own layer, not lowered here. That is an allocation, not a
  dismissal, and it matches the registry: FEA-002's first stage is LAYOUT_ENTRY on boards A to D. See N5 for one
  precision.

**B2 (face wording): CLOSED.** `v2/README.md:3` now reads "with a Xenarc 709GNK monitor set into it, its glass level
with the aluminium face (owner ruling of 9 September 2026, appendix 32.85)", in line with `v2/README.md:56`,
`V2-SPEC.md:56` and `README.md:20`. `V2-SPEC.md:13` reads "face plate off (ten 6-32 screws, case choice C1; correction
20)", in line with line 9, C1 of `CASE-MARGINS.md` section 4 and `BUILD.md:59`, `:93` and `:115`; correction 20 lists
line 13 and says why (lines 149 and 162 to 163), and the apply script's CHANGED list names it. The one remaining "ten
M3" in the pages, `v2/README.md:56`, is labelled as the generated plate and followed by C1's ten 6-32.

## 3. The first pass's minor findings

| # | Disposition, checked |
|---|---|
| M1 | done: `PRODUCT-BRIEF.md:183-187`, `BUILD.md:53` and `:123` give both AW7915 figures (0 C in the 2023 PDF, -10 C on the current page, POWER-THERMAL 9.4) and say they disagree; the LimeSDR from 0 C in use and storage |
| M2 | done: brief `:148-151`, correction 25 (`V2-SPEC.md:203-205`), `drafts/sc.md` and the script cite Peli's exterior 417.6 x 330.2 x 173.2 (CASE-MARGINS 2.2) and about 478 mm over the arrestor rows (X +-238.8, CASE-MARGINS 3.4 line 748); the category holds (478 mm is under 91 cm) |
| M3 | done in `V2-SPEC.md` correction 20 (lines 158 to 162); SC-07's registry text is left to the registry writer (I7) |
| M4 | done: the record name and heading agree in the brief (`:286-288`), `drafts/sc.md`, the script, `drafts/execution-plan.patch` and the prompt |
| M5 | done: `SOURCES.txt` line 1 reads "from the runner."; its row carries the new sha256 and is listed under "Rewritten on filing" |
| M6 | no change needed; confirmed by the re-hash above |
| M7 | done: "no layout of boards A, B, C, D, E or P" with E5 named as having no schematic (`README.md:5`, `:32`; `v2/README.md:17`; `BUILD.md:39`; brief `:157-158`), and `BUILD.md:39` gives SCH-002 as FAIL on A and B and INCONCLUSIVE on C, D, E and P, as CURRENT-EVIDENCE does |
| M8 | done in the brief (`:126-129`: two key-encryption keys, both destroyed); the same wording remains in `V2-SPEC.md:34` (N1) |
| M9 | done: brief `:180-182` and `V2-SPEC.md:73` name "the thermal controls C1 to C4 of `feasibility/POWER-THERMAL.md` section 9.3, not the case choices" |
| M10 | done: correction 22 (`V2-SPEC.md:177-181`), brief `:78-79`, `drafts/sc.md` and the script say two nano-SIMs is the session's default and departs from the approved eSIM plus nano-SIM until the variant's order code is named; the eSIM configuration stays buildable on the same board, so nothing ruled is dropped |
| M11 | done: "and every later one" after the three correction commits (brief `:159-160`, `README.md:32`, `v2/README.md:17`, `BUILD.md:6-7`); "as generated at `45bde541`" stays pinned to that reading, which is still true of it |

## 4. New findings of this pass (all minor, none blocking)

- **N1.** `V2-SPEC.md:34` (Security) still says the drive and eMMC keys are "wrapped by a key the secure element holds"
  and that the toggle "destroys that key", while the same line's parenthetical, the corrected brief (`:126-129`),
  `PANEL.md` section 6, SC-08 and `feasibility/ZEROIZE.md` section 3 give two key-encryption keys, both destroyed. The
  line predates this closer (it is M8's wording in the spec). Aligning it changes a line the apply script asserts is
  byte-identical for CFL-016's rebind, so the fix needs a correction 27, line 34 in the CHANGED list and in CFL-016's
  re-read text.
- **N2.** `BUILD.md:53` cites `sensor_pod.py` for the outside pod; no file of that name exists at `e3aedb25` or anywhere
  in the repository's history (the reference is from the 7 September text). Name the file that draws the pod, or say
  it is not drawn.
- **N3.** The EMCON toggle's cover. `BUILD.md:67` and `V2-SPEC.md:58` put hinged safety covers on SOS and ZEROIZE only;
  `gen_sch_c.py:211` describes `SW_EMCON` with a "hinged safety cover", `PANEL.md:44` gives all three toggles covers,
  and `BUILD.md:113` speaks of "the EMCON cover closed". Pre-existing; one side is wrong. For the components and panel
  layers to settle; the layer 1 pages make no claim that depends on it.
- **N4.** SC-HC1-4 (brief `:289`, `drafts/sc.md`, the script) says blocking findings are "re-checked once by the same
  reviewer". This pass was held by a reviewer session that wrote none of the pages and judged the whole layer again.
  Consider "re-checked once by a reviewer who wrote none of the pages (the first pass's, where it is available)", so the
  gate cannot stall on the availability of one agent session.
- **N5.** The brief's FEA-002 row (`:259`) says every open row's named remedy changes no ruled radio, the case or a
  board-to-board interface. That is true of the remedies EMCON.md names (section 0 says it of 15 rows; the named
  remedies of rows 4 and 5 are both on board B). Two precisions: SD-EMC-6's lamp adds one light-guide hole to the face
  plate (not the Peli case, but part of the enclosure the brief describes); and the RockBLOCK row's failure branch, if
  ENABLE forced low does not silence the module within 1 s with 16 J on its side, could need a change to the bought
  RockBLOCK carrier or the Iridium part itself, which would change a line of "What the V2 kit is". The row's reissue
  clause covers that branch; saying so would make the row complete.
- **N6.** For the integrator, not a defect: the brief's status paragraph (`:3-9`) and `drafts/layer-status-layer-1.md`
  say the re-check is owed; they are to be updated in the commit that files this record.

## 5. Conditions for completion that are not findings against the closer

- **I1.** The pages cite registry ids that exist only after `drafts/apply_hc1_registry.py` runs (SC-HC1-1 to SC-HC1-4,
  owner ruling `public-docs`, REQ-023's new text). The validator on the worktree alone gives 3 errors and 1 warning
  (reproduced). The script runs in the merge commit.
- **I2.** `CONOPS.md:26-27` at `e3aedb25` still says the W1 conflict list is not published; `drafts/conops.patch`
  fixes it, with the re-pin and re-reads the drafts README step 3 names.
- **I3.** `V2-SPEC.md` correction 25 (line 200) cites `v2/vendor/standards/mil-std-810h-method-516-8.md`, which exists
  only in `drafts/` until the script installs it. Its transcription of Table 516.8-IX, Note 1 and Note 5 matches page
  516.8-33 of the file read.
- **I4.** No `v2/docs/handover/LAYER-STATUS.md` and no versioned snapshot under `v2/release/handover/`: the owner's
  section 2 requires "a versioned package another engineer can use" for COMPLETE.
- **I5 (new).** On main `53a98a71`, as at `e3aedb25`, `CONOPS.md` section 4b (line 316: "every row but one, the 5G
  module"), its section 3 D-05 paragraph and section 4 EMCON row, and `PANEL.md:5` ("The lines that act without any
  software are MAIN PWR, EMCON and the TX lamp") and `:127` ("Hardware LEDs, no software: ... TX") contradict
  `feasibility/EMCON.md` section 0a and `gen_sch_c.py`, and so contradict the corrected layer 1 pages, which cite
  `CONOPS.md` section 4b for the circuit as generated. The layer 1 pages are the correct side. The brief is to be
  BASELINED only in a commit where `drafts/layer2-emcon-face.patch` (or the layer 2 writer's equivalent) has also been
  applied, with the re-reads it moves (the CONOPS pin; the CONOPS bindings of REQ-005, CFL-014 and CFL-016; the PANEL.md
  bindings of CFL-001, CFL-005, CFL-014, CFL-015 and CFL-016); otherwise the handover package carries two readings of a
  core function.
- **I6.** `drafts/execution-plan.patch` (the Review A gate) is applied in the same merge, so the gate the brief names
  exists where the plan defines the reviews.
- **I7.** SC-07's registry summary is to carry the two CASE-MARGINS qualifications (M3), as correction 20 does.

## 6. Acceptance items

| # | Item (owner section 3 row, audit acceptance) | Evidence read | Finding |
|---|---|---|---|
| 1 | Clear product purpose | `PRODUCT-BRIEF.md:43-50`; CONOPS NEED-01 | MET |
| 2 | Users stated | `PRODUCT-BRIEF.md:52-64` (D-04 as CONOPS:34 records it; roles with their record; no target organisation, stated) | MET |
| 3 | Prototype scope stated | `PRODUCT-BRIEF.md:214-231` against CONOPS 2a (the core list, including "service and programming access", as the registry's line 205 has it; the deferred list; SOS by the session's choice) | MET |
| 4 | Exclusions stated | `PRODUCT-BRIEF.md:153-197`: not built; not ready for layout or ordered; D-01's deferrals; not rated; not certified; no surge claim; shade; cold start; the hot end with POWER-THERMAL section 0 item 5's figures (+19.5 to +21.6 C; 45 to 81 C cells at +20 C on the independent bound); the two parts not rated to -20 C; the runtime (2.5 h and 1.7 h aged, bounds 1.3 to 3.3 h and 0.9 to 2.3 h, section 6 of POWER-THERMAL); transport (REQ-069); not advertised | MET |
| 5 | Intended outcome stated | `PRODUCT-BRIEF.md:214-231` (staged acceptance, D-02a's two pass lines, the six FEA blockers, which the registry at `e3aedb25` holds as FEA-001 to FEA-006) | MET |
| 6 | Report and deck commitments tracked separately | `PRODUCT-BRIEF.md:233-244` (tracked in the project's tracker; presentation polish does not gate the brief) | MET |
| 7 | Claims agree with the engineering baseline | the audit's eleven contradictions (each corrected, as the first pass found), B1 and B2 (closed, section 2), and a fresh read of every EMCON, case, pack, runtime, thermal, SIM, mass and readiness figure in the five pages against the sources of section 1: the arrestor layout, pitch, plate sizes, holes and screws of C1 to C6; the 145 Wh pack at X 122; 42.8 W and 63.0 W; the part ratings; the declared phases and SCH-002 readings; the mass floor of 7.0 kg; Table 516.8-IX | MET in the five pages; I5 is a contradiction on the layer 2 side that must be closed before the brief is BASELINED; N1 to N3 minor |
| 8 | Every owner ruling of 25 and 26 September recorded | `public-docs` in the brief (`:208-210`), matching the session memory entry of 25 September evening; D-01 to D-18, decisions 27, 28, 30, 40, 41 and 43 as before; W1's table and conflict list filed at `records/w1/` | MET in the pages; the registry and CONOPS halves wait on I1 and I2 |
| 9 | Owed stale texts in `BUILD.md` and both READMEs closed | all lines the audit named, corrected and marked; C1 to C6 numbers match CASE-MARGINS section 4 | MET (N2, N3 minor and pre-existing) |
| 10 | SIM description conflict (CFL-010, S-13) | correction 22 against Quectel HD v1.1 section 4.1.6 and the generator, as the first pass read it | description MET; CFL-010 correctly left open on the TVS array and the variant's code |
| 11 | Carried-mass limit (REQ-023) | Table 516.8-IX re-read in the file (page 516.8-33): under 45.4 kg and under 91 cm, man-packed or man-portable, 122 cm, 26 drops; 45.4 to 90.8 kg, eight corner drops from 76 or 61 cm | MET (a limit where none existed, labelled as the session's, with its reversal) |
| 12 | Records filed so the pages need no scratch directory | 130 rows re-hashed, 0 mismatch, 0 unlisted; no runner path or host name | MET |
| 13 | Required review held and recorded | this record: first pass FAIL on B1 and B2; second pass, both CLOSED, no new blocking finding | MET once this record is filed |
| 14 | Versioned package another engineer can use | no LAYER-STATUS.md, no handover snapshot | NOT MET, not claimed (I4) |
| 15 | Section 2: nothing lowered, dropped, weakened or narrowed; session choices marked; failure-including bounds not closed | SC-HC1-1 to 4, C1 to C6, SC-10 and the thermal controls are each labelled as the session's, none as the owner's; the two-nano-SIM default is stated as a departure with no copper removed; REQ-023 gains a limit; FEA-002 and FEA-004 are stated open with the layer that decides each and a reissue clause; no requirement is lowered | MET |

## 7. Verdict

**PASS on this pass, with minor fixes.** B1 and B2 are closed and no new blocking finding was found: the five pages
state the product's purpose, users, prototype scope, exclusions and intended outcome, and every claim read agrees with
the engineering baseline at `e3aedb25` (and with main `53a98a71` where it moved). The record has no open blocking
finding. N1 to N6 are minor and can land with the integration.

Layer 1 is **not yet COMPLETE**: the brief becomes BASELINED only in the commit that files this record together with
I1 to I3, I5 and I6 (the registry script, the CONOPS and EXECUTION-PLAN patches, the MIL-STD transcription, and layer
2's EMCON and TX lamp correction), and the owner's section 2 also requires the versioned handover package (I4), which
does not exist yet.

---

## Appendix: the first pass (filed at about 02:30 CEST, words unchanged, headings moved down one level)

## AI review (not a qualified engineering review)

### Review A, layer 1 (vision, product definition and pitch): first pass, 27 September 2026

MESHSAT-1357. Reviewer: one fresh AI reviewer (a separate agent session) that wrote none of the pages judged and did
not assemble them. This is an AI review, labelled as one. It is not a qualified engineering review and does not stand
in for any review a record in this tree requires (D-09, `v2/docs/reviews/REVIEW-ROUTES.md`). Prototype design: nothing
in this kit has been built, ordered, powered or field deployed, and nothing below is a physical result.

**Criteria.** The owner's handover prompt of 27 September 2026 (`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`),
section 3, layer 1 row, and section 2 (what COMPLETE means); the layer 1 acceptance items of the handover audit (judged
at main `e3aedb25`); the definition of Review A layer 1 in the brief's last section (session choice SC-HC1-4).
Blocking means: an acceptance item the layer claims met and is not; a claim contradicted by its source or by another
record; a choice presented as the owner's that is the session's; a closure that lowers a requirement, drops a function,
weakens protection or narrows scope; a feasibility bound that includes failure treated as closed where this layer's
decision depends on it.

### 1. What was read (worktree state)

Worktree `fnd/hc1` at `/tmp/.../scratchpad/wt/hc1`: `git rev-parse HEAD` = `e3aedb25c849dbda931888b27093ac6c444621cb`
(nothing committed on the branch); uncommitted changes, `git diff --stat`:

```
 README.md                 |  30 +++----
 v2/BUILD.md               | 123 ++++++++++++++++-------------
 v2/README.md              |  36 +++++----
 v2/docs/PRODUCT-BRIEF.md  | 196 +++++++++++++++++++++++++++++++++++++++-------
 v2/docs/V2-SPEC.md        |  83 +++++++++++++++++---
 v2/docs/records/README.md | 174 ++++++++++++++++++++++++++++++++++++++++
 6 files changed, 518 insertions(+), 124 deletions(-)
```

plus untracked `drafts/`, `v2/docs/records/adj/` and `v2/docs/records/w1/`. The files judged, sha256 first 16, read at
02:30 CEST and unchanged from the start of the review:

| file | sha256/16 |
|---|---|
| `v2/docs/PRODUCT-BRIEF.md` | `914eaec2b32b0fcf` |
| `README.md` | `1678bbfa1bbd2e21` |
| `v2/README.md` | `3cd7c9edd4988216` |
| `v2/BUILD.md` | `ee048e7dc49c7669` |
| `v2/docs/V2-SPEC.md` | `43ef77c9577b7a3e` |
| `v2/docs/records/README.md` | `89e29f455c9add80` |
| `v2/docs/records/w1/w1-decisions.md` | `493db60b7d4ab1b6` |
| `v2/docs/records/w1/w1-conflicts.md` | `eb8d1b0648d0a983` |
| `v2/docs/records/adj/adj_results_w3r2.json` | `aebdb1d4464a87ad` |
| `v2/docs/records/adj/NOT-FILED.tsv` | `76a2cebd3048b46b` |
| `drafts/apply_hc1_registry.py` | `b623b73a39a97315` |
| `drafts/sc.md` | `472f34571f8e168b` |
| `drafts/conops.patch` | `f3c0689516dbbb6b` |
| `drafts/execution-plan.patch` | `89b4cd395da5cd50` |
| `drafts/layer-status-layer-1.md` | `4e3e6c272d375aff` |
| `drafts/SOURCES-hc1.yaml` | `768a1dd7e91694d6` |
| `drafts/vendor/standards/mil-std-810h-method-516-8.md` | `f6e0c9e663ae1e3d` |

Sources were read at `e3aedb25` (`git show e3aedb25:<path>`): `CURRENT-EVIDENCE.md`, `CONOPS.md`, `CASE-MARGINS.md`,
`feasibility/POWER-THERMAL.md`, `feasibility/EMCON.md`, `PANEL.md`, `ARCHITECTURE.md`, `OPERATING-ENVELOPE.md`,
`EXECUTION-PLAN.md`, `reviews/REVIEW-ROUTES.md`, `MESHSAT-709-geometry-appendix.md`, `v2/ecad/tools/pcb_requirements.yaml`,
`v2/ecad/tools/gen_sch_b.py`, `gen_sch_e.py`, `gen_sch_p.py`, `v2/vendor/SOURCES.yaml`,
`v2/vendor/quectel/quectel-rm520n-series-hardware-design-v1.1.pdf`, `v2/release/revA/order/README.md` and the folder
dates of `v2/release/revA/boards/`; and the MIL-STD-810H Method 516.8 file the closer read (sha256 `24686aad175659ec...`,
the same bytes in the scratch directory). Checks run: `python3 tools/rules_lib.py requirements` in the worktree's
`v2/ecad` (read-only; it wrote nothing: `git status` unchanged), which reproduces the closer's 3 errors (REQ-005,
CFL-013, CFL-016 bound to V2-SPEC.md@df8ac226) and 1 warning (CFL-010); a script that re-hashed all 127 rows of the new
records section against the filed bytes (127 match, 0 unlisted files) and scanned the filed records for runner paths.
Not run: the apply script, the claims screen or the test suite (the closer reports them on a copy; not re-checked here).

### 2. Findings

#### Blocking

**B1. The EMCON statements of four pages contradict `feasibility/EMCON.md` (sixth revision) and registry FEA-002 at
`e3aedb25`.**
- `v2/docs/PRODUCT-BRIEF.md:97-101`: "One radio is not yet dark in hardware: the 5G module ...".
- `v2/BUILD.md:21`: "as generated it reaches every transmitter in hardware except the 5G module".
- `v2/README.md:5`: after naming the 5G module's airplane mode, it gives what is owed as "the 5G module's staged supply
  removal (SD-EMC-1) and the items every row of the line shares", and nothing else; `v2/docs/V2-SPEC.md:24` and `:76`
  name the same two items as the only EMCON work owed (unchanged lines, but in the pages judged).
- `v2/BUILD.md:106` (a line marked "Corrected 27 September 2026"): "until it lands, MAIN PWR, the EMCON gates and the TX
  lamp act in hardware".

Against: `feasibility/EMCON.md` at `e3aedb25`, lines 57-64 and the section 0a table (lines 136-149: "local 14 of 17
closed at desk, 3 open (rows 1, 4 and 5); end to end 0 of 17"), and section 4.4 (lines 511-573): the RockBLOCK 9704's
supply gate is drawn, but the module runs on its own two 10 F supercapacitors (about 16 J, line 559) with its ENABLE
(`RB_IEN`) held by the firmware-driven expander U6, so its local chain is OPEN and the remedy (ENABLE forced low by the
EMCON hardware, line 567) is owed; row 1, the SA868, is OPEN locally (its PTT pin's receive threshold is unpublished).
The registry says the same: `v2/ecad/tools/pcb_requirements.yaml` FEA-002 statement (lines 4101-4106 at `e3aedb25`),
"the RockBLOCK 9704 keeps running on its own supercapacitors with its ENABLE held by firmware", with the ENABLE remedy in
its acceptance and closing evidence. On the TX lamp: EMCON.md lines 50-51 ("the TX lamp's supply exists only while the
panel controller drives `PANEL_PWM`") and 1427-1430, and `PANEL.md:77` ("boots low (rail dark until the firmware is
up)"). The pages followed `CONOPS.md` section 4b and `PANEL.md` section 6, which at `e3aedb25` (and still on main
`53a98a71`) say "every row but one"; those are older than EMCON.md's sixth revision on this point. EMCON is core
(D-01) and feasibility blocker FEA-002, so this is a claim about a core function contradicted by its own feasibility
record. **Fix:** state EMCON as EMCON.md section 0a does: local chains closed at desk for 14 of 17 rows, open for the
SA868 (receive threshold unpublished), the RockBLOCK 9704 (stored energy and firmware-held ENABLE; remedy owed) and the
RM520N-GL (SD-EMC-1 not drawn); 0 of 17 end to end; the shared items; no bench row. In BUILD.md:106 drop the TX lamp
from what acts without firmware (MAIN PWR and the EMCON gates stay). Tell the layer 2 writer that CONOPS 4b and PANEL
section 6 need the same correction (not this closer's files).

**B2. Two residual contradictions with the case and face rulings.**
- `v2/README.md:3` keeps "with a Xenarc 709GNK monitor lying on it", while its own Case section (`v2/README.md:56`: "sits
  IN the plate with its glass level with the aluminium face"), `V2-SPEC.md:56`, appendix 32.85 (line 3511, owner ruling
  of 9 September 2026) and the corrected `README.md:20` ("set into it") say the monitor sits in the plate.
- `v2/docs/V2-SPEC.md:13` keeps "face plate off (ten M3)", while `V2-SPEC.md:9` and correction 20 (line 152), C1 of
  `CASE-MARGINS.md` section 4 ("Ten 6-32 UNC x 1/2 in A2 pan-head screws") and `v2/BUILD.md:59` and `:93` give ten 6-32
  screws. Line 13 was not in the audit's list, but it contradicts line 9 of the same page after correction 20.

**Fix:** "set into it" on `v2/README.md:3`; "ten 6-32" on `V2-SPEC.md:13`, added to correction 20's line list (the
apply script's CHANGED list and the CFL-016 rebind text then need line 13 added; CFL-016 does not cite line 13).
`CONOPS.md`'s Service row carries the same "ten M3" (layer 2, for its writer).

#### Conditions for completion that are not findings against the closer (all stated by the closer as open)

- **I1.** The pages cite registry ids that do not exist until `drafts/apply_hc1_registry.py` runs: SC-HC1-1 to SC-HC1-4
  and owner ruling `public-docs` (`PRODUCT-BRIEF.md:74`, `:125`, `:187`, `:246`; `V2-SPEC.md:41`, `:70`, `:165`, `:187`;
  `BUILD.md:11`). The validator on the worktree alone: 3 errors, 1 warning (reproduced). The script must run in the
  merge commit. Note: main `53a98a71` already uses SC-12 (round 8), which the script's next-free numbering handles.
- **I2.** `CONOPS.md:26-27` at `e3aedb25` still says the conflict list is "not published in this repository", against
  `PRODUCT-BRIEF.md:188-189`; `drafts/conops.patch` fixes it and needs the re-pin the drafts README step 3 names.
- **I3.** `V2-SPEC.md:192` cites `v2/vendor/standards/mil-std-810h-method-516-8.md`, which exists only in `drafts/`
  until the script installs it.
- **I4.** No `v2/docs/handover/LAYER-STATUS.md` and no versioned snapshot under `v2/release/handover/`: the owner's
  section 2 requires "a versioned package another engineer can use" for COMPLETE.

#### Minor (not blocking)

- **M1.** "Rated only from 0 C" for the AW7915-AED (`PRODUCT-BRIEF.md:161`, `BUILD.md:53`, `:123`) while the same line
  quotes the maker's current page at -10 to +70 C (`POWER-THERMAL.md:949`). The finding stands (both are outside the
  -20 C end); say "rated no lower than 0 C or -10 C, the maker's two documents disagree".
- **M2.** The mass category is argued from the case's largest inside dimension plus the arrestor rows
  (`PRODUCT-BRIEF.md:129-130`, `V2-SPEC.md:195-196`). Table 516.8-IX classifies by the largest dimension of the test item
  and case, an outside figure. The conclusion is unaffected (a case whose inside is about 382 mm plus about 67 mm of
  arrestors is far below 91 cm), but cite an outside dimension from a Peli source.
- **M3.** `V2-SPEC.md` correction 20 (lines 157-158) and the registry's SC-07 summarise the case layout as "every
  computed margin MET or OPEN and none NOT MET" without the two qualifications the owner-ordered second review of 26
  September asked to keep attached (`CASE-MARGINS.md:46-53`, findings 26 and 27): MET is a sensitivity reading, and two
  OPEN rows (M17g, M17x, the east jumpers under the plugs) fail with the geometry as assumed until the plug is picked.
  Add both.
- **M4.** SC-HC1-4 names the record `v2/docs/reviews/<date>-review-a-layer-1.md` headed "AI review (not a qualified
  review)"; this record was written, as instructed by the integrator, to `REVIEW-A-LAYER-1-2026-09-27.md` with the
  heading above. Align one to the other at integration.
- **M5.** A filed record names the runner host: `v2/docs/records/adj/A08-5g-socket-and-antennas/drafts/web/SOURCES.txt`
  line 1 ("from the runner (nllei01claude01)"). No committed file at `e3aedb25` names an `nllei01` host; redact it the
  way the scratch paths were (for example "from the runner").
- **M6.** The records folder's convention records both hashes for a file rewritten on filing (the "Rewritten on filing"
  table, `records/README.md:190-195`). The new section says two files were rewritten (`$SP`, `$REPO`, `$PLAN`) but gives
  only the filed sha256; add their pre-rewrite sha256 (the rewritten files are `adj/adj_results_w3r2.json` and
  `adj/A03-clamp-orientation/drafts/build_table.py`, by their `$SP` occurrences).
- **M7.** Wording: `BUILD.md:39` lists "INCONCLUSIVE on C, E and P" under "where the folder phase equals the declared
  phase" (E's folder is E6 against E17; D is INCONCLUSIVE too); `README.md:5` and `PRODUCT-BRIEF.md:137-138` say no
  committed layout carries "its board's corrected schematic", which does not apply to E5 (no schematic; CURRENT-EVIDENCE
  reads its board file as its design). Say "no layout of A, B, C, D, E or P".
- **M8.** `PRODUCT-BRIEF.md:108-110` says the drives' keys are wrapped by "a key" that ZEROIZE destroys; D-03 as worked
  out (SC-08, `ZEROIZE.md` section 3, `V2-SPEC.md:34`, CONOPS ZEROIZE row) has two key-encryption keys, both destroyed.
  Pre-existing text; align.
- **M9.** "C1 to C4" means POWER-THERMAL's thermal controls in `PRODUCT-BRIEF.md:159-160` and `V2-SPEC.md:73`, while
  "C1 to C6" are the case choices a few lines away. Qualify the first as "controls C1 to C4 of POWER-THERMAL 9.3".
- **M10.** SC-HC1-1 is labelled as the session's and keeps the eSIM configuration on the same board, so it is not
  presented as the owner's and removes no copper. The owner approved "Dual SIM (eSIM plus nano-SIM)" (appendix line
  2796, "ALL 12 APPROVED"). Building prototype 1 with two nano-SIMs is therefore a session default that departs from the
  approved configuration until the eSIM variant's order code is named. Say that in `V2-SPEC.md` correction 22 and keep
  the variant code on the components layer's list.
- **M11.** Main has moved to `53a98a71` since `e3aedb25`: round 8 changed boards A, D and E (`c0133147`, `76235aad`,
  `bc0f562f`, 27 September). On merge, the pages' "circuit corrections of 26 September 2026 (`faf8c981`, `458b2873`,
  `d90f30e4`)" and "as generated at `45bde541`" need refreshing. The CURRENT-EVIDENCE headline and the declared phases
  are unchanged on main.

### 3. Acceptance items

| # | Item (owner section 3 row, audit acceptance) | Evidence read | Finding |
|---|---|---|---|
| 1 | Clear product purpose | `PRODUCT-BRIEF.md:39-46`; `CONOPS.md` NEED-01 | MET |
| 2 | Users stated | `PRODUCT-BRIEF.md:48-60` (D-04; roles with their record) | MET |
| 3 | Prototype scope stated | `PRODUCT-BRIEF.md:191-208`, matches `CONOPS.md:71-78` (D-01, core list, SC-01 for SOS) | MET |
| 4 | Exclusions stated | `PRODUCT-BRIEF.md:133-174`: not built, not ready for layout or ordered, D-01 deferrals (matches `CONOPS.md:75-77`), not rated, not certified, no surge claim, shade, cold start, the hot end (figures match `POWER-THERMAL.md:66-71`, `:854-855`), the two parts from 0 C (`:949-950`), runtime (matches `:305`, `:307`, PWR-F07), transport (REQ-069), not advertised | MET (M1) |
| 5 | Intended outcome stated | `PRODUCT-BRIEF.md:191-208` (staged acceptance, D-02a's two pass lines, six FEA blockers named) | MET |
| 6 | Report and deck commitments tracked separately | `PRODUCT-BRIEF.md:210-221` | MET |
| 7 | Claims agree with the engineering baseline | the audit's eleven contradictions, each checked: 5G socket key B (`V2-SPEC.md:130`); EMCON compute radios and card supplies (CONOPS 4b); readiness headline (`CURRENT-EVIDENCE.md:6`); declared phases A32, B21, C24, D12, E17, E5, P4 (`CURRENT-EVIDENCE.md:26-34`); folders predate the corrections (last folder commits 12 to 17 Sep, corrections 26 Sep); ordering quarantined (`order/README.md`, decision 41); pack D-06; BUILD's boot and ZEROIZE lines (`PANEL.md:167`, D-03; A01 verdict); devices SC-02 (`V2-SPEC.md:127`); bulkheads C2 to C4; runtime PWR-F07; thermal PWR-F08. All eleven are corrected | **NOT MET: B1, B2** |
| 8 | Every owner ruling of 25 and 26 September recorded | the brief records `public-docs` (`PRODUCT-BRIEF.md:185-189`), consistent with the session memory entry of 25 September evening; W1's table and conflict list filed | MET in the pages; registry and CONOPS halves wait on I1, I2 |
| 9 | Owed stale texts in BUILD.md and both READMEs closed (appendix lines 18860, 18994; CASE-MARGINS C1 to C6 file lists) | the C1 to C6 numbers in `BUILD.md:49`, `:59`, `:65`, `:67`, `:71-73`, `:93` and `v2/README.md:56` match `CASE-MARGINS.md:767-1012` | MET except B2 |
| 10 | SIM description conflict (CFL-010, S-13) | `V2-SPEC.md:41` against `gen_sch_b.py:623-700` (SIM 1 on pins 30-36, SIM 2 on 42-48 behind R272, R287-R289, pin 40 open) and Quectel HD v1.1 section 4.1.6, Figure 19 and 4.1.7 (TVS at most 10 pF) | description MET; CFL-010 correctly left open (TVS array, variant code); M10 |
| 11 | Carried-mass limit (REQ-023) | Table 516.8-IX read in the file itself (page 516.8-33): under 45.4 kg and under 91 cm, man-packed or man-portable, 122 cm, 26 drops; 45.4 to 90.8 kg under 91 cm, 76 cm, eight corner drops. The transcription and the reversal clause match | MET (M2) |
| 12 | Records filed so the pages need no scratch directory | 127 sha256 rows re-hashed, all match, no file unlisted; no `/tmp/claude-1000` or `/home/claude-runner` path left; NOT-FILED classes sum to 445 | MET (M5, M6) |
| 13 | Required review held and recorded | this record | held; blocking findings open, so the brief stays CANDIDATE |
| 14 | Versioned package another engineer can use | no LAYER-STATUS.md, no handover snapshot | NOT MET, not claimed (I4) |
| 15 | Section 2: nothing lowered, dropped, weakened or narrowed; session choices marked as the session's; failure-including bounds not closed | SC-HC1-1 to 4, C1 to C6, SC-10, the thermal controls are each labelled as the session's; no choice is presented as the owner's; REQ-023 gains a limit where none existed; FEA-004 is stated open with the reason layer 1 can close (its decision sits in layers 2 and 4) and named as the item most likely to reopen the brief, which is a proper allocation, not a dismissal | MET, except that B1 overstates how far FEA-002 has come |

### 4. Verdict

**FAIL on this pass.** Two blocking findings (B1, B2) remain. Every other acceptance item for layer 1's purpose is met
in the pages, or waits only on the integration steps I1 to I3 that the closer drafted. With B1 and B2 fixed and I1 to I3
applied in the merge commit, a re-check of those lines by this reviewer should be enough to file a record with no open
blocking finding, and the brief can then move to BASELINED at that commit. Layer 1 is **not COMPLETE**. Beyond B1 and
B2, the owner's section 2 also requires the versioned handover package (I4), which does not exist yet.
