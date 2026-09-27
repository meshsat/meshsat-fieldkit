# AI review (not a qualified engineering review): Review A, layer 2 (concept of operations)

MESHSAT-1357. Written 27 September 2026, 02:47 CEST, by a fresh AI reviewer (a Claude subagent). This reviewer wrote
none of the layer's documents and did not assemble the handover. This is an **AI review**. It replaces none of the
qualified reviews the records require (D-09: R-BAT, R-SEC and the others), and it establishes no circuit's correctness.
Prototype design: nothing has been built, ordered, powered or deployed.

## 1. What was read

**Worktree:** `scratchpad/wt/hc2`, branch `fnd/hc2`.
- `git rev-parse HEAD` = `e3aedb25c849dbda931888b27093ac6c444621cb`, with uncommitted changes.
- `git diff --stat`: 5 files changed, 775 insertions and 193 deletions: `v2/docs/CONOPS.md` (572), `v2/docs/OPERATING-ENVELOPE.md` (152),
  `v2/docs/PANEL.md` (8), `v2/docs/TEST-PLAN.md` (180) and `v2/ecad/tools/pcb_envelope.yaml` (56).
- Untracked: `drafts/`.

This is not a pinned commit. The baseline commit must carry the sha256 values below, or the difference must be
reviewed again.

**Files judged** (sha256, first 16 hex digits):

| sha256/16 | File |
|---|---|
| 3882df42bbad0465 | `v2/docs/CONOPS.md` |
| 807e429a203a7ead | `v2/docs/OPERATING-ENVELOPE.md` |
| 53d682b96e281b9a | `v2/ecad/tools/pcb_envelope.yaml` |
| 89de332a02ce33a1 | `v2/docs/PANEL.md` |
| afb62d0e576fb7c6 | `v2/docs/TEST-PLAN.md` |
| 00e74f3e850b6153 / 9af0296655e07fba | `drafts/pwr_red2.py` / `drafts/pwr_red2.out` (to be filed as `records/hc2/`) |
| 490cf4f5128e22b5, 4024d14f89f1f7d4, 6b28496f44f8a1a5 | `drafts/sc.md`, `drafts/handoffs.md`, `drafts/LAYER-STATUS-layer2.md` |

**Sources checked against, at e3aedb25:**

| sha256/16 | Source |
|---|---|
| 6c3c93b7f32f953a | `ARCH-PCB-B-IOHA.md` |
| bb9c861c9920c8d6 | `feasibility/POWER-THERMAL.md` |
| e57a54d1767bcd59 | `feasibility/EMCON.md` |
| e7a7b9d05a0560ed | `feasibility/ZEROIZE.md` |
| e4a0b78616c69779 | `ASSEMBLY.md` |
| d120ebfb9afbee6e | `gen_sch_e.py` |
| 5f1ce2dd66ed7d2d | `gen_sch_c.py` |
| dedaf34ce285e5ff | `gen_sch_b.py` |
| 03194d7899e36d6a | `part_temps.py` |
| 469d0820b046ef6f | `records/rv-pwr/pwr_budget.py` (the model sha in `pwr_red2.out` matches) |
| 5ec577b952b9dc51 | Samsung INR18650-35E Ver. 1.1 |
| 525d16b2bdee44e5 | TI SLUUAQ3A |

Also checked: the vendor pages for the AW7915-AED, the LimeSDR Mini 2.4 and the RA30H1317M1.

**Main as it stands:** `53a98a71`, compared for integration only. Its `TEST-PLAN.md` is byte-identical to
`drafts/r8bat-TEST-PLAN.lead.md` (sha256/16 86742b72d44adce6). Its registry carries SC-12, a closed S-43 and CFL-017.

**Not re-run:** the closer's test and validator results. Nothing was run in the tree, and nothing in the worktree was
edited except this record.

## 2. What was verified and holds

- **Bank-to-host facts** (CONOPS 4c, lines 446 to 454). They match `ARCH-PCB-B-IOHA.md` section 4 and the section 15
  table row by row. No single slot hosts GNSS, LoRa, Iridium, APRS and the panel.
- **PS-RED2 and PS-SURV figures.** PS-RED2 is 31.4 W (17.6 to 55.6), with 4.3, 3.5 and 2.6 h. PS-SURV is 21.7 W
  (12.4 to 42.0), with 6.3, 5.0 and 3.8 h. PS-EMCON is 47.1 W (37.3 to 80.6). All of these, and every cell of the 4c
  stage-ambient table (lines 506 to 510), reproduce from `pwr_red2.out`. The table takes the lower of C1's air trigger
  and C1's cell trigger per corner.
- **PS-TYP stage ambient.** The PS-TYP row (-6.3 to +27.5, [+28.6 to +30.5]) reproduces from POWER-THERMAL 9.2: the
  SGP41 and discharge columns less 5 K.
- **Figures quoted from POWER-THERMAL.** Sections 4, 6, 7.1, 7.2 and 9.3 (42.8, 63.0, 39.7, 92.0, 203.8, 22.2, 100.4,
  112.3, 150.2, 122.4 to 184.0, 73.9, 15.5 V, 12.4 V, C1 to C4, OCD1) match their source.
- **OPERATING-ENVELOPE figures.** The section 3 rise table, the worst inside air (57.9 and 60.6 C, INFERRED, from
  PS-SURV's rises) and the +61.6 to +72.9 C at +55 C all check.
- **EMCON.md 5a in CONOPS 4b.1.** Every L_max (1 s; 20 s for a running 5G module; 0 at power-up; W_DISABLE1# within
  1 s and not counted), F1 to F9, the exclusion and "no row meets it at desk" are carried without loss.
- **Cell storage figures.** Samsung Ver. 1.1: 3.12 (charge 0 to 45 C, discharge -10 to 60 C); 3.13 (-20 to 25 C for
  a year, -20 to 45 C for 3 months, -20 to 60 C for a month, note 1 at 30 % charge); 7.11 (3.49 to 3.69 V). All as
  quoted.
- **Gauge SHUTDOWN.** SLUUAQ3A 5.4.2 and 13.1.8 (exit when PACK rises above VSTARTUP) and 3.15 (PTC works in
  SHUTDOWN) are as quoted. `gen_sch_e.py` line 213 names MAC 0x0010 as the storage path of record.
- **New vendor rows.** AW7915-AED: 0 to +70 C (2023 PDF), -10 to +70 C (2026 page), storage -20 to +90 C. LimeSDR
  Mini 2.4: 0 to +70 C operating and storage, "Commercial-grade". RA30H1317M1: case -30 to +100 C, storage -40 to
  +110 C. All read from the filed documents.
- **S-39 (PANEL line 184).** Fifteen expander-driven D references, the PI ring and `D3` through its tie `D17` make 17.
  The MAIN ring (`LED_RAIL_SW`) and the TEST ring (`TESTRING_A` from `LED_RAIL`) are hardware-lit, per
  `gen_sch_c.py` lines 201 to 206.
- **ZEROIZE indications.** The incomplete case follows `feasibility/ZEROIZE.md` 3.4 steps 7 and 8 and section 3.5.
- **TEST-PLAN envelope rows.** E5 is sealed and E8 names the valve (CFL-008). The closed-lid state exists. D-02a's two
  pass lines are on E3-S, E3-O, E4-S and E5. E4-O follows D-02d. M1 to M5 are characterisation. M7 is at level 4.
  Every row carries a Purpose and a Verifies column.
- **Labelling and wording.** Every choice taken on 27 September is marked as the session's, with a reversal (CONOPS
  7a, lines 800 to 814). No owner ruling is re-worded as another's. No em dash was added. Nothing is claimed built,
  tested or working.

## 3. Findings

### BLOCKING

**B1. The heat stage loses the 5G module's AT and firmware link and the pack gauge's readings for the graceful
shutdown, and the documents say it keeps 5G.**
- *Where:* CONOPS line 280 (Heat stage row), lines 475 to 478 and 484, line 623 (4f: 5G "yes" in the heat stage),
  line 801 (7a); `drafts/sc.md` SC-L2-02.
- *What the source says:* `ARCH-PCB-B-IOHA.md` section 15 puts "5G module, management | bank 3, port 4 ... This is the
  AT and firmware link only". In the heat stage bank 3 has no host (the row itself says so). Yet the row's list of what
  is lost omits the management link, and the heat stage is chosen because it "keeps ... Iridium and 5G".
- *Graceful shutdown:* the Shutdown row (line 288) and 4c (lines 556 to 561) start the clean shutdown from the gauge's
  state of charge and cell voltage. Those readings reach a module only through the sensor controller on bank 3, so in
  the heat stage on the pack nothing triggers the graceful shutdown. The kit then runs to the gauge's 2.5 V trip. The
  row names only "the battery bar is blank and C2 and C3 have no input".
- *Fix:* state both losses. Either show from Quectel's documents that the RM520N-GL's control plane (AT, and the host
  sequence SD-EMC-1 relies on) is reachable over PCIe, or state 5G in the heat stage as data-only with no AT control
  (or not assured) in the row, 4c, 4f and 7a. Define the heat stage's shutdown source, for example the charger's VBAT
  reading over the kit bus through the panel controller, or state that there is none.

**B2. A lid-closed start-up cannot be decided by the panel controller as generated.**
- *Where:* CONOPS line 277 (Startup row: "with the lid closed at start-up the panel controller raises `SLOT_EN2` and
  `SLOT_EN3` only"), line 279 (Reduced row: "a kit started with its lid closed starts in it") and lines 468 to 469.
- *What the source says:* `gen_sch_e.py` lines 524 to 542 land the lid reed (`J_TAMP`, `TAMPER_IO`) on the sensor
  controller alone ("it never reaches ZEROIZE, the panel or any supervisor"). The sensor controller reaches a module
  only as a USB device on bank 3. So before any module runs, the panel controller has no lid state to act on.
- *Fix:* define the start-up another way. For example: the panel raises slots 2 and 3 first, and slot 1 only once the
  bridge reports the lid open. Or: all three start and then shed. Or name a new sensor-controller-to-panel signal as a
  layer-5 interface item. Keep the Startup row, the Reduced row and 4c consistent with it.

**B3. M1's energy arithmetic leaves out the night, so the layer-4 finding it opens points at the wrong element.**
- *Where:* CONOPS lines 165 to 174 ("the panel would have to deliver that full rating for about 10 to 11 hours of
  every 24"), lines 736 to 738 and line 803; `drafts/LAYER-STATUS-layer2.md` line 18.
- *What the numbers say:* an aged pack holds about 108 Wh usable (line 167, POWER-THERMAL 6). That bridges 2.5 h of
  darkness at PS-IDLE-SPEC, 3.4 h in the reduced mode and 5.0 h in the heat stage. No solar rating carries a night.
  So M1 on pack and solar fails every night in every state, as long as the kit has D-06's one pack and D-01 defers the
  second one. The "10 to 11 hours" figure balances energy per day and ignores storage.
- *Fix:* restate the finding. The binding limit is the ruled pack's energy across the dark hours, with the solar
  path's rating a second limit. Name the routes: overnight vehicle or shore input, or the deferred second pack, whose
  location is not found. Report it to the owner as a consequence of D-06 together with the session's 72 h. Do not
  shorten the mission.

**B4. E3-L's pass line drops the protection criteria that round 8's E3-L carries, and it accepts a part above its
absolute rating.**
- *Where:* TEST-PLAN line 135 (E3-L).
- *What main carries:* main `53a98a71` (the round-8 text, identical to the lead) reads "as E3-A, with the lid
  closed". E3-A (line 134) carries T3 and T4, OTC at 44.0 C, the loads carried by shore while the charge is held off,
  F2's body at most +60 C, no permanent protection action, and the thermistor-against-thermocouple record.
- *What the worktree carries:* the new E3-L keeps only the cell limits and the controls. It adds "the inside air at or
  under the SGP41's +55 C, or the excess recorded as a finding against the part". REQ-052's acceptance asks for
  "every part inside its published range". Taking this file whole, as handoffs.md section 1 instructs, would weaken
  the closed-lid acceptance test for exactly the state in which the pack and F2 run hottest.
- *Fix:* E3-L's pass line is E3-A's, with the lid closed, plus the closer's stage criteria. An SGP41 above +55 C is a
  failure of E3-L as well as a finding.

**B5. The hot-edge closed-lid acceptance is restated down to the heat stage's set, and the cause is board B's bank
allocation, not the thermal bound.**
- *Where:* TEST-PLAN line 135 (E3-L: "at +40 C at least the heat stage's set"); `drafts/handoffs.md` line 88 (REQ-052
  restated); CONOPS lines 475 to 485 and 623 to 625.
- *What changes:* REQ-052's acceptance on main requires the reduced mode's set at the hot edge, "chosen so the owner's
  bearer set stays inside the thermal bound" (S-24). As restated, the requirement drops the LoRa mesh and APRS, two
  core bearers (D-01) of the owner's D-02b example, at the envelope's +40 C with the lid closed. That holds at every
  conductance in the record: the two-slot reduced mode meets C1 below +37.3 C on every bound.
- *Why it is blocking:* the one-module stage lacks them because of board B's bank allocation. A slot allocated to host
  the example would carry about the same heat. The closer names a bank reallocation as the reversal, and board B is
  not at layout entry.
- *Fix:* do not restate the requirement to what the generated board does. Either take the reallocation as a board B
  design item now (subject to IOHA section 8's rule that no bank holds two long-range bearers), or keep REQ-052 at the
  owner's example set. In that case record "not met by board B as generated" as a finding with the reallocation as
  its option, and report it to the owner at the next checkpoint (not asked).

**B6. The commissioning scenario adopts a procedure step that K1 forbids.**
- *Where:* CONOPS lines 575 to 576 (4d step 1 takes the build checks "as `ASSEMBLY.md` section 8 orders them").
- *What the source says:* `ASSEMBLY.md` line 190 (section 8 step 10) is "10 minutes of key-down at 30 W into a load".
  CONOPS section 5 (lines 643 to 650) and the K1 row (line 498) set every PA key-down at 60 s at most. POWER-THERMAL
  PWR-F15 puts the flange at 95 C after one 60 s key-down at 45 W from a +50 C plate, against the RA30H1317M1's
  +100 C case maximum and its 90 C advice.
- *Fix:* CONOPS 4d states that step 10 is superseded by K1 and T-H3's procedure. Hand the correction to
  `ASSEMBLY.md`'s owner. Also align ASSEMBLY line 187 ("all 17 LEDs") with PANEL's seventeen indicators.

**B7. The cold-end carve-out says the kit's own heat brings the inside air to 0 C, and the record's own rises say it
may not.**
- *Where:* CONOPS lines 535 to 538 and 255 to 256; OPERATING-ENVELOPE line 206; pcb_envelope.yaml carve-out
  `below_c: 0`; SC-L2-11.
- *What the numbers say:* at the envelope's -20 C, OPERATING-ENVELOPE's own table (line 128 and the PS-TYP row) on
  appendix 32.53's conductance puts the inside air at -6.8 to -5.5 C in PS-IDLE-SPEC. It puts it at -0.5 to +1.4 C in
  PS-TYP, and PS-TYP counts the link card and the SDR, which the carve-out holds off. Only with the pack heater does
  POWER-THERMAL line 371 reach +2.9 to +5.2 C. So on the design record's conductance the link cards and the SDR may
  never be powered at the cold end, not "come up late".
- *Why it matters:* the kit-to-kit link is a critical peripheral (SC-02) exercised by IOHA A11, and E4-O's functional
  check requires it. This is a feasibility bound that includes failure, and the carve-out decision (against an
  extended-grade part, layer 6) depends on it.
- *Fix:* state the ambient per state and conductance at which the inside air reaches 0 C. If the heater or a warm-up
  load is to do it, name it as the behaviour. Keep E4-O's pass line. Carry the extended-grade replacement as the route
  that removes the failure, with the decision needed before board B's layout entry if a socket or supply changes.

### MINOR

- **m1.** CONOPS line 688: "about 1.2 % of a 75 W key-down, which bounds both". One 1 s beacon a minute is 1.7 %, so
  1.2 % does not bound the moving case. PS-RED2's 0.9 W beacon allowance understates M2's moving case (about 1.25 W).
- **m2.** CONOPS line 328: PS-EMCON aged 60 %, 1.7 h, is not in `pwr_red2.out`, which prints only new and aged 80 %.
  Add it to the script or mark it INFERRED with its arithmetic.
- **m3.** CONOPS line 279: the Reduced row's guarantee cites "the voting and the break-before-make in hardware".
  `ARCH-PCB-B-IOHA.md` section 5 records FAB-03 (the order is not in the generated circuit) and FAB-02 (nothing
  detaches a bank from an unpowered host) as owed on board B. Section 6 records the supervisors' I2C status path as
  absent. The reduced mode makes dropping `SLOT_EN1` routine, so name these as its preconditions.
- **m4.** CONOPS lines 475 to 485: the heat stage has no next stage, and its worst inside air (57.9 and 60.6 C, above
  C1's +50 C) keeps C1's triggers set. Say what the kit does then: it stays in the heat stage, and on the pack the
  gauge's discharge window ends it.
- **m5.** CONOPS lines 563 to 567 and the Transport and Storage rows (lines 275 and 289): the gauge enters SHUTDOWN
  only with no charger present (SLUUAQ3A 5.4.2 and 13.1.8), so the preparation needs every input removed. Two further
  consequences of PS-SHUT are not stated in 7a or in the changed consequences:
  - the lid and tamper log (NEED-10's case-open record) does not run in storage or transport, because board E's
    always-on domain sits on the pack side;
  - a transported kit cannot start from its own pack until an input is applied.
- **m6.** `drafts/LAYER-STATUS-layer2.md` "Stated open" does not list CFL-017/BAT-F19, which SC-L2-03 widens to the
  stored product's +71 C and -33 C margins. Its routes, cells beyond +60 C (D-06 reopened, money) or the owner's
  reading of D-02a, are outside the session's authority. List it with its compact engineering question.
- **m7.** The changed consequences to report to the owner omit two items:
  - the one-module heat stage has neither LoRa nor APRS;
  - loss of compute redundancy may now occur well below +35 C (from -6.3 C ambient on the independent bound).
  When CON-012 is restated, its `residual_risk_accepted: OWNER` must not be carried over to the new ambients.
- **m8.** pcb_envelope.yaml lines 34 to 40 keep the superseded rise and the `above_c: 35` carve-out, so
  `part_temps.py` (lines 50 to 67) still computes a 51 C bar that the envelope withdraws. Land `drafts/part_temps.patch`
  in the same integration commit, or THM-001 reads the SGP41 as in range on a superseded basis.
- **m9.** CONOPS lines 544 to 547: define "back in service" (IOHA section 7 step 11 or step 12), and say whether k3s
  rescheduling of the bridge workload falls inside the 30 s.
- **m10.** E4-O (TEST-PLAN line 27) lost round 8's explicit +1.0 C charge floor and -9.0 C discharge stop, while E3-A
  keeps round 8's T3, T4 and OTC figures. Restore them, since SC-12 on main carries them.
- **m11.** CONOPS lines 46 to 50 and 344 to 346 cite `records/hc2/`, `records/w1/` and A06 as filed. They are not in
  the tree at `e3aedb25` or `53a98a71`. This is a remaining acceptance item (the records hand-off).
- **m12.** Integration against main `53a98a71`: several records there now conflict with this worktree.
  - SC-12 reads "+71 C and -33 C storage with the pack out".
  - S-43 is closed on `dd39fb15`'s pack-out TEST-PLAN.
  - CFL-017 says the session did not take the pack-fitted reading.
  - CONOPS 4c line 481 calls round 8's thresholds "pending merge".
  All need rebinding or restating when SC-L2-03 lands.

## 4. The audit's acceptance items for layer 2

| Item | Evidence in the worktree | Finding |
|---|---|---|
| Normal scenario | CONOPS M1 and Normal row, PWR-F07 figures | met |
| Degraded scenario | M5; 4c recovery bound (30 s); controls C1 to C4; 4e | not met: B1 (heat stage), m3, m9 |
| Startup scenario | Startup row; lid-closed start | not met: B2 |
| Charging scenario | Charging row (unchanged) | met |
| Shutdown scenario | Shutdown row; 4c graceful threshold; OCD1 backstop | not met in the heat stage: B1 |
| Storage scenario | Storage and Transport rows; SC-L2-03 and 04; cell figures verified | met in substance; m5, m6 |
| Service scenario | Service row; 4d commissioning | not met: B6 |
| Fault scenarios | 4e table | met (m4) |
| Operating envelope | OPERATING-ENVELOPE 2 to 5; pcb_envelope.yaml | not met: B7; m8 |
| Simultaneous modes and duty | Section 5, duty profile, PS-BUSY bounded, K1 to K5 | met (m1) |
| Explicit behaviour of the core functions | 4f; 4b.1; PANEL 9 | not met: B1, B5 |
| Product decisions settled under existing authority | 7a (L-02, S-24, S-26, storage, transport, pollution degree, duty); REQ-069 and D-18 stated open with reasons | not met: B3 and B5 rest on stated bases that do not hold; m6 |
| Consistent with the current analyses | 4a, 4c, 5 and 6 against POWER-THERMAL | not met: B1 (IOHA 15), B7 (the envelope's own rises) |
| TEST-PLAN envelope limits consistent with the rulings | E5, E8, the states, the pass lines, M1 to M7 | not met: B4 (E3-L) |
| Every owner ruling recorded | CONOPS 7; OPERATING-ENVELOPE 8 | met |
| Every source cited is in the repo | records/hc2, records/w1, A06 | not met yet (m11; a hand-off) |
| Review A held and recorded | this record | held; its BLOCKING findings are open |

The owner's section 2 test: the deliverables are not yet internally consistent (B1, B2, B6, B7), and two closures
lower or misstate a requirement or its basis (B3, B5). The claim that the enclosure conductance decides no layer-2
item holds for the mode definitions and triggers. It does not hold for the cold-end carve-out (B7). The hot-edge
bearer set does not depend on the conductance: it is lost at +40 C at every bound, which is B5's point.

## 5. Verdict

**FAIL for this pass; layer 2 is not complete.** Seven BLOCKING findings stand, and each needs a change to a document
or to a hand-off, not new evidence. Once they are answered in the documents, the integrator's hand-offs have landed,
and the records are filed, a second pass of this review at the integrating commit can decide the baseline.
