# AI review (not a qualified engineering review): layer 2 (concept of operations), release check at `f2b7fa66`

MESHSAT-1357. Written 27 September 2026, about 13:30 CEST, by a fresh AI reviewer (a Claude subagent). This reviewer
wrote none of the layer's documents, held none of the earlier passes of Review A, and did not assemble the handover.
This is an **AI review**: it replaces none of the qualified reviews the records require (D-09: R-BAT, R-SEC and the
others), and it establishes no circuit's correctness. Prototype design: nothing has been built, ordered, powered or
deployed. It is the pass "at the integrating commit" that `CONOPS.md` lines 45 to 49 and `EXECUTION-PLAN.md` (the Review
A definition) name, and it is judged against the owner's execution prompt
(`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`) sections 2 and 3.

## 1. What was read and run

**Commit judged:** `f2b7fa669eba97186af71362230b1895f0bcad48`, branch `fnd/r8int4`, worktree `scratchpad/wt/r8int4`,
not pushed. It holds **7** commits over main `38dcd764` (the brief said 8): `e5fde2ed`, `95e078a1` (the layer 2 and 3
closers), `53292f81`, `0da2778b` (layer 5), `c351115d` (layer 7), `53966a3f` (handover pages), `f2b7fa66` (generated
pages). At read time the tree had no tracked change; one untracked file from another reviewer was present
(`v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2026-09-27.md`), not read and not touched here. Nothing in the worktree was
edited except this record; nothing was run in the main checkout.

**The layer's files at that commit** (sha256, first 16 hex digits):

| sha256/16 | File | Note |
|---|---|---|
| 4887ada07f50d808 | `v2/docs/CONOPS.md` | equals the registry's `needs_document_sha256` |
| 6e4bbde9dbf7e136 | `v2/docs/OPERATING-ENVELOPE.md` | equals `pcb_envelope.yaml` `document_sha256` and ENV-001's `verified_sha` |
| ce95b2e947099a30 | `v2/ecad/tools/pcb_envelope.yaml` | |
| 4bcbf31f44560ee1 | `v2/docs/PANEL.md` | operator sections 1, 3, 5, 8, 9, 10 read; section 4 read where it states operator behaviour |
| a0de0b12ff06ba4e | `v2/docs/TEST-PLAN.md` | sections 1, 2, 4, 6, 7, 8 |
| 77b20ca4042f0855 | `v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27.md` | Review A pass 2 record |
| 835910e807d588c4 / 5f03619f7bf5c476 | `v2/docs/records/hc2/pwr_red2.out` / `hotstop_bounds.out` | |
| add69d02b8232a6b / 60bfcc5f205a09fc | `v2/docs/records/hc3/c23-response.md` / `records/hc2/handoffs.md` | |
| 2db0cc0c165aba42 | `v2/docs/handover/LAYER-STATUS.md` | layer 2 audit at `e3aedb25` and its integrator line |

**Sources checked against, at the same commit:** `ARCH-PCB-B-IOHA.md` (55620cf51446bfc8, sections 4, 15, 15a);
`feasibility/EMCON.md` (421a291f7ce4cda2, sections 0a, 4b, 5a); `feasibility/POWER-THERMAL.md` (465abd3bb9c97416,
sections 1, 9.3); `ARCHITECTURE.md` (bd5f80b1f83793f0); `HW-FW-CONTRACT.md` (7e54827497149141); `pcb_requirements.yaml`
(ab65fea491ee5da1: REQ-004, 016, 018, 024, 025, 030, 036, 042, 052, 069, 071, 072, 074, 077, CON-012, FEA-004, CFL-008,
009, 011, 017, SC-17, 18, 21, 49, 50, S-01, 44, 54 to 58, L-02); `review-packets/battery/THERMAL-COORDINATION.md`
(0d4d60f03260f004, sections 3 and 4); the generators `gen_sch_a.py` (5a97fed72c42b79d), `gen_sch_b.py`
(af6e5821e21b70ef, board B's round 8), `gen_sch_c.py` (7c555c07abc97500), `gen_sch_e.py` (f275102965fafa10) and
`gen_pcb_e5.py`; `handover/ENGINEERING-QUESTIONS.md` and `handover/CONTINUATION-BRIEF.md`; the TI BQ25731 datasheet
(SLUSE66A, Table 9-8 and 9.4.1) and the BQ4050 TRM (SLUUAQ3A 5.4.2 and 13.1.8) as text copies of the filed PDFs.

**Runs** (stdlib, under a second each, in this reviewer's scratch directory `scratchpad/rv-l2/`, never in a tree):
`records/hc2/pwr_red2.py` with `records/rv-pwr/pwr_budget.py` (469d0820b046ef6f) reproduces `pwr_red2.out` byte for
byte (sha256 `835910e807d588c4...`); `records/hc2/hotstop_bounds.py` on that output reproduces `hotstop_bounds.out`
byte for byte (sha256 `5f03619f7bf5c476...`); the six fixtures of `tests/test_envelope_data.py`, run on copies of the
envelope file, the document and the coverage map, all pass (the document pin matches ENV-001's). Not run:
`rules_lib.py`, `rules_render.py`, `rules_status.py` (they write into a tree).

**Figures checked against their source and found right:** every figure of CONOPS 4a's PS-RED2, PS-SURV-R, PS-SURV,
PS-RED and PS-EMCON rows (battery W with bounds, new/aged 80 %/aged 60 % runtimes); the C1 and charge-stop ambient
table of 4c (each cell is the lower of the air and cell triggers of `pwr_red2.out`); OPERATING-ENVELOPE section 3's
rise table, ceilings table and worst inside air (59.2, 62.1, 47.8, 55.6; 57.9, 60.6, 47.3, 54.6 C) and section 8's
+61.6 to +74.2 C; the cold block (71.1 W warm-up, +2.0 to +4.2 C at -20 C, 72.7 W over 20 K = 3.6 W/K); the hot stop's
thresholds (56.5 + 2.07 = 58.57, 57.0 + 2.07 = 59.07; spacing 1.5, 0.5, 0.5 K; the 2.07 K sum equals the packet's
section 3 terms 0.71, 0.40, 0.80, 0.16) and its ambients (+34.8/+35.9 C and +33.2/+34.4 C lid closed, +37.5/+38.6 C and
+36.1/+37.3 C lid open at the independent bound's worst corner, not below +40.3 C and +48.1 C on appendix 32.53's
conductance); M1's arithmetic (about 108 Wh aged usable, 152 Wh for a 7 h night at 21.7 W, 3.08 kWh for 72 h, about
266 W of panel on 4.01 kWh/m2); the BQ25731's `CHRG_INHIBIT` (ChargeOption0 bit 0, "1b: Inhibit Charge") and the
host-terminates-charge text of 9.4.1; the BQ4050's "Charger voltage must not be present for the device to enter SHIP
SHUTDOWN mode" (5.4.2) and "enter SHUTDOWN mode if no charger present is detected" (13.1.8). **HOT-R1's netlist
premises hold at this commit:** `gen_sch_e.py` line 562 (`J_BLK` pin 12 spare), 693 (`TP7` on `BLK_SPARE`), 581 (`U10`
pin 30, GPIO19, `NC`; pins 4 and 5 `SMBD`, `SMBC`), 565 (`U12` on `CELL_F`), 669 (2N7002 already on board E);
`gen_sch_a.py` line 226 (`J_DOCK` pin 12 spare), 1262 (`U27` pin 18 `DOCK_SPARE`), 1267 (`R110` on `EXP_INT`), 269 and
273 (`LTC2954` `KILL`, `Q1` from `PI_KILL`), 784 (the charger at 0x6B); `gen_pcb_e5.py` lines 72 and 96 pass the spare
contact through the dock block one net per contact, so "no contact is added" is true; `pcb_interfaces.yaml`
IF-AE-DOCK pin 12 is `DOCK_SPARE`. The IOHA section 15 bank map and the generator's `PORTS` table (now lines 903 to 905)
and ring (`f = s % 3 + 1`, now line 936) agree with CONOPS 4c.

## 2. Review A pass 2's two blocking findings, re-checked on the merged text

| Finding | Where it is answered at `f2b7fa66` | Disposition |
|---|---|---|
| **P2-B1** (D-02b's row carried the session's choices as the ruling) | CONOPS section 7, row D-02b (line 1099): "with choices taken by the session under the owner's standing rule of 26 September 2026 (section 7a), which are not part of the ruling", the hot stop listed among them, "restated by the session" before the consequences; D-06's row and OPERATING-ENVELOPE section 8 mark theirs the same way | **CLOSED** |
| **P2-B2** (nothing bounds the cells past the heat stage on an input) | the Hot stop row of section 4 (line 335) and the Heat stage row's Exit and Guarantee (line 334); 4c lines 603 to 715 (the two steps, thresholds from the packet's budget, the detector and actor with netlist citations, HOT-R1, firmware or hardware, the destructive backstops named, the open hardware-stage question, the cost under FEA-004 including "closed-lid operation at +40 C ... is predicted to fail REQ-052 on any supply"); 4e rows at lines 944 and 945; 4f's Pack safety row (968); M2 (246 to 248); 7a rows 1168 to 1170 with reversals; OPERATING-ENVELOPE sections 3 (158 to 165) and 4 (223 to 235); `pcb_envelope.yaml` `hot_end.hot_stop` (lines 78 to 83); TEST-PLAN E3-H with the +59 C abort for every E3-A, E3-L and E3-H run; REQ-077 (core, under NEED-13, FAIL at desk until HOT-R1), SC-49, SC-50, S-57, S-58, EQ-22, EQ-23, EQ-05 | **CLOSED in the documents.** The behaviour past the heat stage is defined on measured cell temperatures on the pack and on every input, REQ-052 and +40 C are kept, and the parts of it that are not this layer's are allocated (section 5). One consequence of the fix is not closed: its prototype verification (finding B2 below) |

The c23 verifier's "CLOSED" verdict that LAYER-STATUS cites read the drafts; no record of it is filed in the tree
(finding B3). This pass is the re-check on the merged text that the layer 2 integrator line lists as remaining item (1).

## 3. The owner's section 3 row for layer 2

| Item (owner's prompt, section 3) | Evidence at `f2b7fa66` | Finding |
|---|---|---|
| Normal scenario | M1 (lines 170 to 227), Normal row (332), 4a, section 5 | met |
| Degraded scenario | M5 (287 to 316), Reduced, Heat stage, Hot stop and Degraded rows (333 to 337), 4c, 4e | met |
| Startup scenario | Startup row (331), 4c's start-up with the lid closed (551 to 562), PANEL section 5's boot order | met (HOT-R1's read at boot is a PANEL hand-off under S-57) |
| Charging scenario | Charging row (336), the gauge window control (749), `CHRG_INHIBIT` in H1 | met |
| Shutdown scenario | Shutdown row (343), 4c graceful shutdown (871 to 882), H2 (619) | met |
| Storage scenario | Storage and Transport rows (329, 344), 4c preparation (884 to 891), SC-19 (7a row 1156), REQ-025, REQ-074, TEST-PLAN E3-T, E4-T | met; BAT-F19 stays open outside the session's authority (finding B4 e) |
| Service scenario | Service and Commissioning rows (345, 346), 4d | met |
| Fault scenarios | 4e (fourteen rows, the four common modes included, the hot stop and its lost detector) | met |
| Operating envelope | OPERATING-ENVELOPE sections 2 to 5 and 8, `pcb_envelope.yaml` (pinned, fixtures pass) | met at requirement level; the hot and cold bounds are stated open and allocated (FEA-004, S-55); minors m1, m5, m9, m10 |
| Simultaneous modes | section 5 (D-11 bound, K1 to K5, C4, the interlock, the planning duty profile, S1 to S5) | met |
| Explicit behaviour of the retained core functions | 4f, section 4 rows, 4b, 4b.1, PANEL section 9 | **not met: finding B1** (two readings of EMCON, a core function, in the same document and in PANEL); m12 |
| Product decisions settled under existing authority | section 7, 7a (every session choice with its reason and reversal), `pcb_envelope.yaml` `session_taken`, registry SC-17 to SC-50 | met inside the layer; **the handover contradicts one of them (EQ-13 against SC-21) and gives the one owner-level item no question: finding B4 c and e** |

## 4. The project's own acceptance items (LAYER-STATUS layer 2, items 2.1 to 2.17)

| # | Item | Finding at `f2b7fa66` |
|---|---|---|
| 2.1 | Normal scenario | met (PWR-F07 figures in 4a) |
| 2.2 | Degraded scenario | met: REQ-004's bound set (30 s per device, 60 s for the bridge), C1 to C4 with indications, the reduced mode hosted (slots 2 and 3), the heat stage in both configurations, the hot stop |
| 2.3 | Startup scenario | met |
| 2.4 | Charging scenario | met |
| 2.5 | Shutdown scenario | met (the graceful threshold; the over-current backstop's dark state; H2) |
| 2.6 | Storage scenario | met (pack fitted, gauge shutdown, ex-factory charge; CFL-017 kept open as BAT-F19) |
| 2.7 | Service scenario | met (commissioning 4d: golden image, JP1, D-15 verification, secure element, key fill) |
| 2.8 | Fault scenarios | met |
| 2.9 | Operating envelope | met, with m1, m5, m9, m10 |
| 2.10 | Simultaneous modes and duty | met (PS-BUSY bounded, 60 s key-down, C2 and C3) |
| 2.11 | Explicit behaviour of the core functions | **not met (B1)**; SOS, ZEROIZE and lamp-test indications are set in PANEL 9 |
| 2.12 | Product decisions settled under existing authority | met inside the layer (L-02 by SC-21, S-24 by SC-17, S-26, S-37, CFL-011, CFL-017's storage half, REQ-069 "no route claimed", pollution degree, duty); D-18 stays conditional and is not this layer's (no mode depends on it); B4 c and e for the handover side |
| 2.13 | Every owner ruling recorded | met, and labelled (P2-B1 closed) |
| 2.14 | Consistent with the current analyses | **not met (B1, B4 a and b)**: CONOPS 4b.1 and 4f against 4b and EMCON.md 0a and 4b; POWER-THERMAL sections 1 and 9.3, ARCHITECTURE's PS-RED row and HW-FW-CONTRACT FW-C09 against CONOPS 4c's C1 |
| 2.15 | TEST-PLAN envelope limits consistent with the rulings | met for D-02a's two pass lines, the closed-lid state (E3-L), E5 without a vent, M7 at level 4, the characterisation labels; **not met for E3-H (B2)**; m2 |
| 2.16 | Every source the CONOPS cites is in the repository | **not met (B3)**: `records/w1/`, `records/adj/`, `records/hc2/`, `records/hc3/` are filed, but Review A's first pass and brief are not, and two passages still say A06 is unfiled |
| 2.17 | Review A held and recorded | held (pass 1, pass 2, this pass); the layer is not BASELINED: this pass has blocking findings |

## 5. The integrator line's remaining items, and whether each belongs to this layer

| Remaining item (LAYER-STATUS line 351) | Owner and stage | Judgement |
|---|---|---|
| (1) Re-check of P2-B1 and P2-B2 on the merged text | this review | done: both CLOSED (section 2) |
| (2) HOT-R1 drawn on boards A and E (S-57, EQ-22) | board A and E authors, before their layout entry | correctly allocated: the decision is taken (SC-50), REQ-077 reads FAIL on the generated boards and says so, and a layer is not held open by a later board's work (prompt section 1) |
| (3) A non-destructive hardware stage (S-58, EQ-23) | the D-09 battery-and-protection reviewer, before the layout entry of A, E and P | correctly allocated: protection architecture (layer 4); the requirement it would serve is set here |
| (4) Whether the hot stop fires inside the envelope (FEA-004, EQ-05, T-H1) | layer 4, gating the placement freeze | correctly allocated, and not dismissed: 4c states the failure it can produce (REQ-052 at +40 C lid closed on any supply) and why no layer-2 decision moves with the conductance; m14 on the wording of what follows a failure |
| (5) BANK-R1 on board B (S-54) | board B's author, before its layout entry | correctly allocated: the decision is taken (SC-34 in the registry, 7a row 1154), REQ-052 FAIL on B as generated stated |
| (6) The cold end's 3.6 W/K bound (S-55) | layers 4 and 6, before board B's layout entry | correctly allocated; E4-O's pass line kept |
| (7) E3-H has no forced-trigger step | TEST-PLAN (this layer) and REQ-077's acceptance (layer 3) | **a blocking item of this layer: B2** |
| (8) Layer 1's I5 check | layer 1's reviewer | I5 is not fully answered in this layer's text: B1 is the part still carrying two readings of EMCON |

## 6. Findings of this pass

### BLOCKING

**B1. CONOPS and PANEL carry two readings of EMCON, a core function: the 5G module's inhibit and the hardware EMCON
lamp are described as drawn in one place and as owed in another.**
- *Where:* CONOPS section 4's EMCON row (line 338), 4b's 5G row (446), the D-05 paragraph (453 to 461) and M4 (276 to
  285) state board B's round 8: the 5G supply removed by hardware at once, RF off within about 1.2 ms plus 1.8 ms per mF
  of the module's own capacitance (SD-EMC-1r8, EMCON.md 4b and 0a row 5, CLOSED locally at desk), and the lamp `D22`
  drawn on board C. Against them: **4b.1's L_max table (line 490)** says the 5G row's 20 s is "set by hardware timers at
  their worst tolerance (SD-EMC-1's staged supply removal, owed on board B)", and **M4 (lines 268 to 269)** repeats the
  timer mechanism; **4b.1's Excluded paragraph (496 to 498)** says the lamp shows the shared element "once it is drawn on
  board C", **its operator paragraph (500 to 505)** says "until the lamp is drawn no indicator shows the line's state
  without the panel controller" and derives a 20 s operator lead from the timers, and **its state paragraph (505 to 508)**
  gives rows 1, 4 and 5 as open locally and names "the registry text for REQ-030 ... drafted" where the registry holds
  REQ-071; **4f's 5G row, EMCON column (line 961)** reads "held (airplane mode now; supply removal owed, section 4b.1)".
  Outside CONOPS: OPERATING-ENVELOPE section 4's operating-modes paragraph (lines 289 to 298) says EMCON "puts the 5G
  module in airplane mode" and leaves "the 5G module's supply removal" as session work; TEST-PLAN section 4 (line 56)
  checks "the EMCON lamp once it is drawn"; PANEL section 4 (line 135) says "The lamp test cannot light `D22` ... setting
  EMCON is its test", while PANEL section 9 (line 195) says the lamp "is lit by the lamp test only if its circuit is given
  a test tie, an item for its author", and section 1 (line 50) counts `D22` as the face's seventeenth LED beside section
  9's "seventeen controller-lit indicators" (a different seventeen).
- *Why it is blocking:* the owner's section 3 asks for the explicit behaviour of the retained core functions, and
  section 2 for internally consistent deliverables. 4f is the table written to answer exactly that, and it states the
  5G module's EMCON behaviour of the circuit before round 8; the operator procedure in 4b.1 rests on a mechanism the
  design no longer has. Review A of layer 1 (finding I5) made the brief's BASELINED conditional on the package not
  carrying "two readings of a core function"; the integration of `95e078a1` corrected M4's second paragraph, the EMCON
  row, 4b and the D-05 paragraph but not 4b.1, 4f or the passages above.
- *Fix (desk, about an hour):* (1) 4b.1's 5G row and M4: keep REQ-071's requirement (20 s for a module that has been
  turned on, 0 at power-up, 1 s for every other row) and state the design against it: since board B's round 8 the supply
  is removed by hardware at once, RF off within about 1.2 ms plus 1.8 ms per mF of the module's CINT (TBD, bench E-12),
  the flash residual accepted; drop "set by hardware timers" and "owed on board B". (2) 4b.1's Excluded and operator
  paragraphs: the lamp `D22` is drawn on board C since its round 8, its plate light guide owed (S-44); either keep the
  20 s operator lead as REQ-071's bound until E-12 measures the drawn circuit, saying so, or drop it. (3) 4b.1's state
  paragraph restated at the current commit (EMCON.md 0a: 15 of 17 local at desk, 0 of 17 end to end) with REQ-071 named.
  (4) 4f's 5G EMCON cell: "dark: supply removed by hardware at once since board B's round 8 (section 4b)". (5)
  OPERATING-ENVELOPE section 4's operating-modes paragraph brought to round 8. (6) TEST-PLAN section 4: "the EMCON lamp
  `D22`", and REQ-071 added to the trace for "EMCON with its latency per row". (7) PANEL: one statement of whether the
  lamp test lights `D22` (and if a test tie is wanted, an open item with its number), and section 1 and section 9 saying
  which seventeen each counts. Then re-pin (the registry's needs pin, ENV-001) and re-read the readings bound to the
  changed sections, per the integration recipe.

**B2. TEST-PLAN E3-H cannot fail to verify the hot stop: a run in which the cells never reach the thresholds exercises
nothing, and nothing says what that run proves.**
- *Where:* TEST-PLAN E3-H (section 6): "read during E3-A's and E3-L's runs with no chamber time of its own ... at +40 C
  with the lid closed the level is held until the hot stop has acted or its 4 h have passed"; its pass line and
  REQ-077's prototype acceptance are conditional ("where the hottest cell ... reaches +56.5 C the kit sheds ..."). On
  appendix 32.53's conductance the first step acts not below +40.3 C lid closed and +48.1 C lid open
  (`hotstop_bounds.out`, reproduced here), so inside the envelope it may never act; the stand-in run "with the sensor
  controller held in reset" depends on board B's `TMP117` reaching +55.0 C the same way. The integrator line lists this
  as remaining item (7) (the c23 verifier's residual).
- *Why it is blocking:* REQ-077 is a core safety requirement created by this layer's closing decision (the answer to
  P2-B2). The owner's section 2 counts requirements complete when their verification methods are settled; a method that
  cannot distinguish "acted correctly" from "was never exercised" is not settled, and the layer's own acceptance item 2.15
  covers E3-H.
- *Fix (desk):* add to E3-H (and to REQ-077's prototype acceptance) a run that makes both steps act whatever the
  enclosure does, for example: (a) a forced run, pack fitted, lid closed, the heat stage running, on shore and then on the
  pack, the chamber raised from +40 C in steps (for example 2 K per hour) up to at most D-02a's +55 C until H1 and then H2
  have acted, recorded as a protection test beyond the envelope and never as an envelope claim, with the +59 C abort
  unchanged; and (b) a detection-to-action check at room temperature that walks one gauge cell reading through +55.0,
  +56.5, +57.0 C and back below +46.5 C (a decade resistance in place of one of TS1 to TS4, as P10 does for the second
  level, with the walk kept below OTD's 57.5 C and far below SOT), verifying each step, the 30-minute hold, the MAIN
  release after H2, and the four HOT-R1 line states including held high (sensor controller in reset, `TMP117` stand-in)
  and held low. State that an E3-H run in which a step never acted reads NOT_VERIFIED for REQ-077, never PASS.

**B3. The layer's review history and two of its sources are not in the repository, and the texts still say otherwise.**
- *Where:* CONOPS lines 45 to 48 say the first pass "was recorded (`reviews/REVIEW-A-LAYER-2-2026-09-27.md`: FAIL, seven
  blocking findings ...)"; that path now holds pass 2, which says the first pass "is preserved verbatim outside the
  worktree at `scratchpad/rvA2/REVIEW-A-LAYER-2-2026-09-27.pass1.md` (sha256 `e854c2a46ea3d542...`) for the records
  integrator to file". It is not filed (no file under `v2/docs/reviews/` or `v2/docs/records/` carries it; its sha256
  `e854c2a46ea3d54225e01b346490b6a751bc0365369c60a7c0ed5e2108a0cec9` was checked on the scratch copy). The review brief
  (`fnd/hc2` `drafts/REVIEW-A-BRIEF.md`, hand-off item 12) is not filed. The "fresh verifier (AI)" whose CLOSED verdict
  on P2-B1 and P2-B2 LAYER-STATUS cites has no record in the tree. CONOPS section 4a (lines 401 to 403) and
  OPERATING-ENVELOPE section 4's pack row (line 281) say adjudication A06's working files are not filed, while
  `v2/docs/records/adj/A06-pack-geometry/` holds them. Review A pass 2 made the filing an acceptance item "until the
  integrating commit" (its n14).
- *Why it is blocking:* acceptance item 2.16 (every cited source in the repository) and the owner's section 6 (the
  recipient must not need one particular running host) are not met: the record of the layer's first review lives only
  in a session scratch directory.
- *Fix (records, minutes):* file the pass-1 record (for example as
  `v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27-pass1.md`) and the brief with `records/README.md` rows and sha256; file
  the c23 verifier's record, or say in the layer 2 integrator line that none exists and that this record is the re-check;
  point CONOPS lines 45 to 48 at the filed pass-1 file; cite `records/adj/A06-pack-geometry/` in CONOPS 4a and
  OPERATING-ENVELOPE section 4.

**B4. Other layers' current files and the handover pages contradict or omit what layer 2 settled, and none of it is
tracked as another layer's remaining work.** (The fix lies outside the layer's own text except one sentence; it blocks
releasing layer 2 as COMPLETE because the package would carry two definitions of the same controls.)
- *(a) The C1 control and the reduced mode, three ways.* CONOPS 4c and the Reduced row: C1 sheds to the reduced mode
  (slots 2 and 3), then to the heat stage. `POWER-THERMAL.md` section 1 (line 98, "The reduced mode's one module is slot
  3") and 9.3 (line 876, C1 "shed to one module (slot 3)"); `ARCHITECTURE.md` line 866 ("PS-RED, slot 3 only ... the
  closed-lid reduced mode of D-02b"); and **`HW-FW-CONTRACT.md` FW-C09 (line 108), merged after layer 2 on this same
  branch: "Keep C1 (shed to one module at +50 C air or +55 C cell)"**, with the round-8 fallback ("when the sensor
  controller's pack readings stop for 10 s, shed to the reduced mode") and no row for the hot stop, HOT-R1's four line
  states or the panel controller's read of the line at boot. CONOPS names the POWER-THERMAL and ARCHITECTURE lag as a
  hand-off (lines 333, 524; `records/hc2/handoffs.md` sections 4 and 5) but not FW-C09, and the layer 4 and layer 5
  integrator lines list none of it (S-57 alone names PANEL.md for the line states).
- *(b) EMCON's 5G row in layer 4 and the registry.* `feasibility/EMCON.md` section 5a row 5 still defines the 5G bound by
  SD-EMC-1's staged timers (T_off, T_cut), which section 4b and 0a supersede for board B; the registry's S-01 title still
  asks for "SD-EMC-1's two stages for the 5G module drawn on board B", and S-44 for a lamp that is drawn (its light guide
  is what remains). This is the source of B1's CONOPS text.
- *(c) M1's duration.* The registry closes L-02 by SC-21 (72 h, the session's, replaced by the owner's own setting), and
  CONOPS M1, section 6, the D-06 row and 7a say so; `ENGINEERING-QUESTIONS.md` EQ-13 (group C, external authorisation)
  still says REQ-016 "carries the solar requirement TBD", treats L-02 as open, and recommends against the session setting
  the value ("Option (c) is not recommended because D-06 reserves the value to the owner"). The package states both that
  the decision was taken and that it should not have been.
- *(d) The brief's "records that disagree" table.* `CONTINUATION-BRIEF.md` section 8 (lines 428 to 445) still tells the
  reader to follow superseded positions on five layer-2 topics (runtime 3.4 and 1.8 h, the inside-air rise and +35 C
  restriction, storage "open (CFL-017) ... pack out", the EMCON gap "the 5G module's supply removal", the panel LED count
  "decision owed"), unmarked; H1.1's rule is that a row the work has since met carries a "Superseded" mark.
- *(e) The one owner-level item has no compact question.* BAT-F19 (CFL-017, CONFLICT_OPEN, FAIL): with its pack fitted
  the kit cannot meet D-02a's +55 C operating margin or the +71 C and -33 C storage margins; the routes are a measured
  pack arrangement (the purchase of EQ-05), cells rated beyond +60 C (reopens D-06, money) or the owner's reading of
  D-02a. Two of three need the owner, and `ENGINEERING-QUESTIONS.md` has no entry for it (the prompt, section 6, asks one
  per blocked item); CONOPS reports it as a finding only.
- *Fix:* one sentence in CONOPS 4c (line 524) and the Reduced row (333) naming HW-FW-CONTRACT FW-C09 and ARCHITECTURE's
  PS-RED row beside POWER-THERMAL as documents to follow; the layer 4 integrator line gains POWER-THERMAL 1 and 9.3,
  ARCHITECTURE's PS-RED row and EMCON.md 5a row 5; the layer 5 integrator line gains FW-C09's C1 target and fallback and
  the hot stop's firmware rows (or a registry open item carrying all of them); S-01 and S-44 retitled to what remains;
  EQ-13 marked superseded by SC-21 with the owner's right to replace the value; CONTINUATION-BRIEF section 8's five rows
  marked superseded with the current file; an EQ for BAT-F19 in group C with the three routes, the evidence
  (THERMAL-COORDINATION 9a, OPERATING-ENVELOPE section 8's +61.6 C floor at +55 C), the recommendation and the cost.

### MINOR

- **m1** (pass 2's n1, open). OPERATING-ENVELOPE section 3 (line 162) says only the independent bound is past the
  SGP41's +55 C; the design record's own figure after BANK-R1 is +55.6 C lid closed at +40 C, past it too. S-56 names no
  decision point (board E's layout entry would be the natural one).
- **m2** (n3, open). E4-O runs 4 h at -20 C with the cold warm-up at about 71 W, 1.5 h on an aged pack at +20 C; TEST-PLAN
  lines 27 and 140 say "started warm or on external input" but not that the run is powered from an input.
- **m3** (n4, open). In the heat stage as generated, K2's and C4's cell inputs are lost while a headset PTT can still key
  the PA (`KEY = PTT_ANY AND TX_INHIBIT_n`); CONOPS does not say whether the bridge holds `PA_SW_EN` off there or which
  reading stands in (the hot stop's H1 does turn the PA hold off).
- **m4** (n6 and new). Stale generator line citations; the facts hold: `gen_sch_b.py` "line 543" for the ring (lines 291,
  515 to 516; now 936), `PORTS` "lines 764 to 766" (719; now 903 to 905), `gen_sch_a.py` "line 708" for the charger (589;
  now 784), `gen_sch_e.py` "line 213" for the MAC shutdown (329; the note is at 251). Lines 640 to 671 are labelled "at
  `a8652172`" and hold there, but board B moved after it (`PI_SHDN_REQ` on GPIO6 is `GPIO_FIXED`, line 464; the `TMP117`
  is line 1277).
- **m5** (n7, open). OPERATING-ENVELOPE section 8's last paragraph (lines 454 to 455) lists the pollution degree and the
  duty cycle as left open; section 5 and `session_taken` say the session took both.
- **m6** (n8, open). "its only firmware-update path" (CONOPS lines 334, 581): the HD also lists (D)FOTA; "its only wired
  firmware-update path".
- **m7** (n9, open). The case-open log (NEED-10) does not run in PS-SHUT; the rows say so, but the changed consequences
  reported to the owner do not, and REQ-036's acceptance ("with the kit on and off") does not name the exclusion.
- **m8** (n10, open). The cold end's options omit slowing the mixer fans (on the sensor controller's PWM) while the inside
  air is under 0 C, which lowers the conductance the warm-up works against.
- **m9** (n12 and new). `pcb_envelope.yaml` line 35 files an inside-air carve-out under `ambient_c.carve_outs`; lines 34
  and 40 say `part_temps.py` still computes its bar from the superseded entries, but at this commit it reads
  `worst_inside_air_c` first (`part_temps.py` lines 50 to 60), so the entries or the comments are stale.
- **m10.** OPERATING-ENVELOPE section 4's pack row (line 281): "that number is not computed yet and no runtime is claimed
  here", while CONOPS section 6 carries PROVISIONAL runtimes of 2.5 and 1.7 h.
- **m11.** H1's minimum load (PS-HOLD) is "not computed, TBD", though `records/hc2/pwr_red2.py` can compute it at desk
  from the heat stage's loads less the module; whether H1 alone brings the cells under +46.5 C at +40 C would then be a
  desk bound per conductance rather than wholly FEA-004's.
- **m12.** 4f has no column for the hot stop (nor Startup, Transport or Storage). Every bearer and SOS are lost in H1 and
  H2 (section 4's row, 4e), but ZEROIZE's and EMCON's state there is stated nowhere: H1 keeps the panel controller and the
  kit bus; H2 removes both, so a ZEROIZE toggled during H2 would complete at the next start, as the panel-lost column says.
- **m13.** PANEL.md does not yet carry the reduced mode's panel duties (drop `SLOT_EN1` on the bridge's request, raise slot
  1 again when slot 3 is lost, all three at every start-up) nor the hot stop's indications; CONOPS names them as panel
  firmware contract items. Part of B4 (a)'s tracking.
- **m14.** "lowering the envelope is not an option taken or offered" (CONOPS line 802): if T-H1 closes FEA-004 in failure
  and no thermal architecture change meets REQ-052 lid closed at +40 C, the remaining route is an owner trade on D-02b's
  closed-lid scope; naming that as what FEA-004 would return to the owner is more complete than "not offered". No
  requirement is lowered by saying so.
- **m15** (n2, partly answered). EQ-03 now carries REQ-069's compact question, but the Transport row still says "No mode
  ... of this layer depends on its answer" while a pack required to travel apart would change the Transport row's "pack
  fitted" (a layer-2 mode) as well as layer 7's mounting.
- **m16** (n11, open). M1's routes that reopen D-06 or D-01 (a larger or second pack) change the pack pocket; the stage by
  which the owner's answer is needed (the pack's placement freeze) is not named beside them.

## 7. The owner's section 2 conditions

- **Missing decisions of this layer that can change architecture, interface, component, outline or protection:** none
  found. The reduced mode (SC-17), the heat stage (SC-18), BANK-R1 (SC-34), the hot stop (SC-49), HOT-R1 (SC-50), storage
  and transport (SC-19), the cold warm-up (SC-27), M1's duration (SC-21), "aged", the duty profile, the recovery and
  delivery targets, the pollution degree are taken, recorded with reasons and reversals. What remains open (S-58's
  hardware stage, D-18's fan, the extended-grade card and SDR, the SGP41's replacement) belongs to layers 4 and 6.
- **Feasibility questions allocated to their owners, none hidden:** FEA-004 (T-H1) with the failure it can produce stated;
  S-55; S-57; S-54; S-58. Each has a registry item and an engineering question, except the tracking gaps of B4.
- **No lowered requirement, dropped function, weakened protection or narrowed scope found:** REQ-052 stays at the owner's
  example set and reads FAIL where the design falls short (board B as generated; the hot stop at +40 C); the envelope
  stays -20 to +40 C with the cold link's pass line kept; D-02a's margins are run as deviations and BAT-F19 is not closed
  by them; M1 keeps its setting with no season taken off; D-11's values became pass lines (REQ-018), a tightening; the
  hot stop adds protection. The one narrowing of coverage, the case-open log not running in storage and transport, is a
  deferred function's and is stated (m7).
- **Session choices marked as the session's:** yes, in CONOPS 7 (D-02b, D-06), 7a, OPERATING-ENVELOPE sections 5 and 8,
  `pcb_envelope.yaml` (`hot_end`, `session_taken`), TEST-PLAN section 1 and the registry's SC records.

## 8. Verdict

**FAIL for this pass: layer 2 is not COMPLETE at `f2b7fa66`, and is not to be marked BASELINED.** Review A pass 2's two
blocking findings are closed on the merged text (P2-B1 and P2-B2), every figure checked reproduces, and the layer's
scenarios, envelope, simultaneity and product decisions meet the owner's section 3 row in substance. Four blocking
findings remain, all desk or records work that needs no measurement, no purchase and no owner question:
**B1** (two readings of EMCON, a core function, in CONOPS 4b.1, 4f and M4 against its own section 4 and 4b, and in
OPERATING-ENVELOPE, TEST-PLAN and PANEL), **B2** (E3-H cannot distinguish a working hot stop from one never exercised),
**B3** (the first Review A record, the brief and the verifier's record are outside the repository, and two passages
misstate A06's filing), and **B4** (the C1 control defined three ways across layers 2, 4 and 5, EMCON.md 5a and the
registry titles behind B1, EQ-13 against SC-21, the brief's stale layer-2 rows, and no engineering question for
BAT-F19, none of it tracked in the owning layers' remaining lists). Once they are answered, a confirmation limited to the
difference from the sha256 values of section 1 can decide the baseline; the items allocated to other layers (HOT-R1,
BANK-R1, S-58, FEA-004 and T-H1, S-55, BAT-F19, REQ-069) then stay open where they belong and do not hold layer 2.
