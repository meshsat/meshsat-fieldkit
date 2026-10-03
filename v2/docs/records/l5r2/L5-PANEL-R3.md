# L5-R3: the panel's contract against its firmware (MESHSAT-1357, 3 October 2026)

Prototype design: nothing here has been built, powered or measured. Layer 5's third round on `fnd/l5r2` from `6902db8f`, owning
`v2/docs/PANEL.md`, `v2/docs/ASSEMBLY.md` and `v2/docs/HW-FW-CONTRACT.md` for the round. Two inputs come from commits not in this
branch's history and are copied verbatim into `inputs/` with their source and sha256: the panel firmware author's findings F-01 to
F-13 and session choices S-01 to S-36 (`fnd/fw-panel` at `42c27369`, `v2/firmware/panel/README.md` sections 5 and 6), and record
l8r2's section 3d, board C's PI button (`fnd/l8r2` at `29ffb518`). `apply_l5r3.py` wrote the three files once; `l5r3_panel.py`
reads them back (its output pins every file and refuses an excerpt not in its target, a figure no source prints, a finding without
a resolution or a session choice unaccounted for). No requirement is changed, nothing is bought or sent, no generator is edited.

## 1. The rule of decision

Where the documents disagree, the generator and the netlist decide what is wired and `CONOPS.md` and the requirements decide the
behaviour; where a value is unstated it is stated with its basis or marked owed with its owner. Each decision is the session's
(authority SESSION, under the owner's standing rule of 26 September 2026), recorded in place with its reason and its finding id.

## 2. The findings, each resolved

| Finding | Where they disagreed | Decided | On what evidence |
|---|---|---|---|
| F-04 the expander order | PANEL.md 4 (configuration first) against 5 and FW-A08 (outputs first) | outputs first everywhere; every configuration write preceded by an output write (the firmware's S-10, bound in FW-A08 by section 3.8) | the contract's own rows; both orders safe on U1 and U2, so one rule |
| F-05 NVG against the TX lamp's 10 % floor | PANEL.md 8's floor against NVG's 2 % on the one LED rail | the floor withdrawn: the TX lamp follows the panel's duty (2 % in NVG), dark in BLACKOUT | CONOPS 4's NVG row ("panel at 2 % duty ... red and amber indicators only") and its NVIS target (7a); the TX lamp shares `LED_RAIL` behind `Q1` (PANEL.md 1), so a floor raises every lit LED. The firmware's raise of the whole panel to 10 % while keyed goes with it (a firmware change for its author) |
| F-06 the lamp test's sound | "a chirp" against "double chirp (lamp test)" | the double chirp, 50 / 100 / 50 ms (S-15) | the sounder patterns are the specific statement; a single chirp is the acknowledge |
| F-07 a slot fault | in both MASTER WARN's and MASTER CAUT's lists | one slot fault is MASTER CAUT; two compute modules lost is MASTER WARN | CONOPS 4e's fault table ("a compute module lost ... MASTER CAUT"; "two modules lost ... MASTER WARN") |
| F-08 the e-paper's pacing | "at most once a minute" against the QR, SOS and ZEROIZE pages | a change of page refreshes at once; the minute bounds the idle page's content; the panel's least interval owed to Layer 6 | the indications of PANEL.md 9 need their page at once; no held PDi document states a least interval |
| F-09 the operator's retry | "until the operator acts" named no control | the touch UI's retry over the bridge protocol (owed, MESHSAT-837), or a restart with MAIN | the firmware's S-04; the protocol is the firmware's F-02 |
| F-10 the boot-time 5 Hz rule | FW-C14 (back at 1 Hz) against FW-C13 (1 Hz and 30 minutes) | a 5 Hz line at start-up enters H1 with the stop dated at boot; the stricter exit applies | FW-C13's exit and CONOPS 4c's hot stop (at most once in 30 minutes): a restart must not shorten it (S-18) |
| F-11 board D's boot levels | FW-D01 stated none; the firmware wrote all 0 (S-11) | X_SA_PD 1, X_AMP_EN 1, X_MMUTE 0, the generator's designed power-up levels; S-11 not adopted | `gen_sch_d.py`: "PD from the expander (default on)", the level stages' 10 k pull-ups, the codec mute's "defined mute off"; CONOPS: "the VHF path keeps listening" |
| F-12 the margin hold's SOS text | FW-C15 gave none; the EMCON text would be wrong | "SOS QUEUED: MARGIN HOLD, COOLING" in PANEL.md 9 and FW-C15 | the firmware's S-12 |
| F-13 the HDMI select encoding | stated in no contract page | slot 1 both low; slot 2 HDMI_SEL1 high; slot 3 HDMI_SEL2 high (HDMI_SEL1 driven low) | `gen_sch_b.py` lines 1336 to 1348 (U3, U4, U519, U520) and TI SCDS343F Table 1 |

Not in this round's list and left with their owners: F-01 (the PI button, closed in drafts by record l8r2, section 3 below), F-02
(the bridge protocol, MESHSAT-837), F-03 (the SDK's early resets; carried into FW-C02 by section 3.8 as the firmware's finding).

## 3. Record l8r2's PI button texts (DRAFTED, PROVISIONAL)

Applied as record l8r2 section 3d drafts them, each marked DRAFTED and PROVISIONAL with the trigger "l8r2's
`apply_gen_sch_c_pibtn.py` released and board C regenerated", the as-generated state kept beside it (no controller pin reads the
button, the firmware's F-01): PANEL.md section 1's switches row ("read by U1 P1.3"), section 4's U1 port 1 row 3 (PI_BTN_n, low =
pressed, R57 10 k to +3V3, C27 100 nF to GND, tau 1.0 ms, raising EXP_INT), section 5's PI sentence ("read on U1 P1.3, PI_BTN_n, at
every EXP_INT and the once-a-second poll"), ASSEMBLY.md line 127 ("the panel controller reads it on U1 P1.3; nothing leaves the
backer") and FW-C03 (`C:U1` P1.3 (PI_BTN_n)).

## 4. The firmware's session choices

All 36 are accounted for (section 2 of the output): adopted with credit in PANEL.md section 9a (the operator-visible ones) or bound
to their FW rows in HW-FW-CONTRACT.md section 3.8 (S-03, S-05, S-07 to S-10, S-17, S-18, S-20, S-21, S-26 to S-29, S-31, S-32,
S-34, S-35, S-36's definition of a reading): 33 adopted, S-12 and S-36 in part. Three are not adopted, with their reasons: S-11
(F-11), S-19 (the firmware's interim while FW-C09's restore is unimplemented) and S-30 (internal); S-36's polling and gain and S-12's
other texts stay the firmware's.

## 5. The table

<!-- l5r3-table:begin -->
| id | finding or text | target | text written (excerpt, verbatim) | decided by (file; where) | mark | invalidation trigger | criterion (5.x) |
|---|---|---|---|---|---|---|---|
| R3-F04 | F-04 the expander order | PANEL.md | On boot the firmware writes the output registers to 0 first (every LED bit is still an input at power-up, so nothing lights) | fw-panel-sections-5-6-42c27369.md; the firmware's F-04 and S-10; PANEL.md section 5 and FW-A08 (the one rule) | RULE (SESSION, decided on the contract's own rows) | none | 5.7, 5.13 |
| R3-F05 | F-05 NVG against the TX lamp's floor | PANEL.md | The TX lamp follows the panel's duty in every position (DAY 100 %, NIGHT 15 %, NVG 2 %) | fw-panel-sections-5-6-42c27369.md; CONOPS.md; CONOPS section 4's NVG row (behaviour) and section 7a's NVIS target; the shared LED_RAIL (PANEL.md section 1) | RULE (SESSION; CONOPS decides the behaviour) | an owner ruling that the TX lamp outranks the NVG target (a CONOPS change) | 5.11, 5.13 |
| R3-F06 | F-06 the lamp test's chirp | PANEL.md | a double chirp (F-06: this sentence said a chirp | fw-panel-sections-5-6-42c27369.md; PANEL.md's sounder patterns (the specific statement); the firmware's F-06 and S-15 | RULE (SESSION) | none | 5.13 |
| R3-F07 | F-07 the slot fault's indicator | PANEL.md | two compute modules lost; decided 3 October 2026, F-07 | CONOPS.md; fw-panel-sections-5-6-42c27369.md; CONOPS section 4e's fault table | RULE (SESSION; CONOPS decides the behaviour) | none | 5.13 |
| R3-F08 | F-08 the e-paper's pacing | PANEL.md | a change of page refreshes at once and the idle page's content at most once a minute | fw-panel-sections-5-6-42c27369.md; the firmware's F-08 and S-16 | RULE (SESSION); the panel's least interval TBD (Layer 6) | PDi's statement of a least refresh interval (Layer 6) | 5.11 |
| R3-F09 | F-09 the operator's retry | PANEL.md | then leaves it off until the operator acts: from the touch UI, by a retry command over the bridge protocol | fw-panel-sections-5-6-42c27369.md; the firmware's F-09 and S-04 | RULE (SESSION); the protocol owed (MESHSAT-837) | the bridge protocol's definition (MESHSAT-837, the firmware's F-02) | 5.8, 5.11 |
| R3-F10 | F-10 the boot-time 5 Hz rule | HW-FW-CONTRACT.md | at 5 Hz, enter H1 with the stop dated at the start-up and raise no slot until the line is back at 1 Hz and 30 minutes have passed | fw-panel-sections-5-6-42c27369.md; FW-C13's exit (H1 left only at 1 Hz and after 30 minutes); the firmware's F-10 and S-18 | RULE (SESSION, the stricter of the two rows) | none | 5.6, 5.11 |
| R3-F11 | F-11 board D's boot levels | HW-FW-CONTRACT.md | X_SA_PD 1 (the exciter on and receiving, `gen_sch_d.py`: 'PD from the expander (default on)'), X_AMP_EN 1 | gen_sch_d.py; CONOPS.md; fw-panel-sections-5-6-42c27369.md; gen_sch_d.py's SA868 and codec-mute notes and its level stages; CONOPS's EMCON row | NETLIST (the generator's designed power-up levels); RULE (SESSION) | a change of board D's level stages or the SA868's PD polarity | 5.7, 5.11 |
| R3-F12 | F-12 the margin hold's SOS text | PANEL.md | "SOS QUEUED: MARGIN HOLD, COOLING" | fw-panel-sections-5-6-42c27369.md; the firmware's F-12 and S-12 | RULE (SESSION; the firmware's text adopted) | none | 5.11 |
| R3-F12h | F-12 in FW-C15 | HW-FW-CONTRACT.md | the e-paper showing "SOS QUEUED: MARGIN HOLD, COOLING" (F-12 | fw-panel-sections-5-6-42c27369.md; the firmware's F-12 | RULE (SESSION) | none | 5.11 |
| R3-F13 | F-13 the HDMI select encoding | PANEL.md | slot 1 = both selects low; slot 2 = `HDMI_SEL1` high, `HDMI_SEL2` low; slot 3 = `HDMI_SEL2` high | gen_sch_b.py; fw-panel-sections-5-6-42c27369.md; gen_sch_b.py lines 1336 to 1348 (U3, U4, U519, U520) with TI SCDS343F Table 1 | NETLIST (the generator) | a change of board B's display switches | 5.8, 5.13 |
| R3-PI1 | PI: PANEL.md section 1 | PANEL.md | DRAFTED by record l8r2 at `29ffb518` | l8r2-section-3d-29ffb518.md; l8r2 3d's text for section 1 | DRAFTED; PROVISIONAL | l8r2's apply_gen_sch_c_pibtn.py released and board C regenerated | 5.7, 5.13 |
| R3-PI4 | PI: PANEL.md section 4 | PANEL.md | PI_BTN_n, the PI button, low = pressed (PIJ2_A2; R57 10 k to +3V3, C27 100 nF to GND, tau 1.0 ms); raises EXP_INT on a change | l8r2-section-3d-29ffb518.md; l8r2 3d's text for section 4 | DRAFTED; PROVISIONAL | l8r2's apply_gen_sch_c_pibtn.py released and board C regenerated | 5.7 |
| R3-PI5 | PI: PANEL.md section 5 | PANEL.md | (read on U1 P1.3, PI_BTN_n, at every EXP_INT and the once-a-second poll | l8r2-section-3d-29ffb518.md; l8r2 3d's text for section 5 | DRAFTED; PROVISIONAL | l8r2's apply_gen_sch_c_pibtn.py released and board C regenerated | 5.11 |
| R3-PIA | PI: ASSEMBLY.md line 127 | ASSEMBLY.md | (the panel controller reads it on U1 P1.3; nothing leaves the backer | l8r2-section-3d-29ffb518.md; l8r2 3d's text for ASSEMBLY.md | DRAFTED; PROVISIONAL | l8r2's apply_gen_sch_c_pibtn.py released and board C regenerated | 5.13 |
| R3-PIC | PI: FW-C03 | HW-FW-CONTRACT.md | DRAFTED: `C:U1` P1.3 (PI_BTN_n) | l8r2-section-3d-29ffb518.md; l8r2 3d's text for FW-C03 | DRAFTED; PROVISIONAL | l8r2's apply_gen_sch_c_pibtn.py released and board C regenerated | 5.11 |
<!-- l5r3-table:end -->

## 6. Criteria moved (Layer 5's reading)

- **5.7 reset, default and cable-out states:** PARTLY, further: board D's U16 boot levels stated (F-11), the expander boot order one
  rule (F-04), the PI input's state drafted.
- **5.8 communications and addressing:** PARTLY, further: the HDMI select encoding stated (F-13); the panel USB wire format still
  outside the repository (MESHSAT-837, F-02, F-09).
- **5.11 firmware obligations:** PARTLY, further: F-05 to F-12 resolved, 33 session choices adopted with credit (two in part), three
  declined with reasons; the contract and the panel firmware now state the same values.
- **5.13 consistency:** PARTLY, further: the panel page's internal contradictions resolved; ASSEMBLY.md's PI row agrees with the draft.
- **5.6 sequencing:** PARTLY, further: the boot-time hot stop (F-10) and the 1 s slot stagger (S-03) stated.

## 7. Findings for others

| ID | For | Finding | Next action |
|---|---|---|---|
| L5R3-F01 | the integrator | PANEL.md and ASSEMBLY.md moved: the registry's readings CFL-001, CFL-005, CFL-014, CFL-015 and CFL-016 are bound to their content (`rules_lib.py requirements` reads 7 errors, and the trace page does not render until rebound), and `l4e11_power.py` pins both (with HW-FW-CONTRACT.md, already moved in round 2) | rebind on a judged reason (the sentences changed are listed in section 2 and 3), re-pin L4-E11 |
| L5R3-F02 | the panel firmware's author | F-05: the raise of the whole panel to 10 % while keyed is withdrawn (the TX lamp follows the duty); F-11: board D's U16 boot levels are X_SA_PD 1, X_AMP_EN 1, X_MMUTE 0, not S-11's 0 | change `panel_tick` and `EXP_BOOT` and their tests |
| L5R3-F03 | Layer 6 | the e-paper's least interval between refreshes is stated by none of the held PDi documents | PDi's statement |
| L5R3-F04 | Layer 8 board C | the PI texts read DRAFTED until l8r2's draft is released and board C regenerated | lift the marks then |

## 8. Reproduce

`python3 v2/docs/records/l5r2/l5r3_panel.py` (stdlib, under a second); its output is regenerated only through `_bin/regen_out.py`.
`env -C v2/ecad/tools/tests python3 run.py test_l5r2` holds the predicates (the round-3 ones are named `t_r3_`). `apply_l5r3.py
<target> --check` on the tree refuses "already applied".
