# AI review (not a qualified engineering review): Review A, layer 2 (concept of operations), pass 2

MESHSAT-1357. Written 27 September 2026, about 06:50 CEST, by a fresh AI reviewer (a Claude subagent). This reviewer
wrote none of the layer's documents, did not hold the first pass and did not assemble the handover. This is an **AI
review**. It replaces none of the qualified reviews the records require (D-09: R-BAT, R-SEC and the others), and it
establishes no circuit's correctness. Prototype design: nothing has been built, ordered, powered or deployed.

This file overwrites the first pass's record at the same path, as the brief asks. The first pass (FAIL, seven blocking
findings B1 to B7, twelve minor m1 to m12) is preserved verbatim outside the worktree at
`scratchpad/rvA2/REVIEW-A-LAYER-2-2026-09-27.pass1.md` (sha256 `e854c2a46ea3d542...`) for the records integrator to
file beside this one; section 3 below lists each of its findings with the answer this pass checked.

## 1. What was read

**Worktree:** `scratchpad/wt/hc2`, branch `fnd/hc2`.
- `git rev-parse HEAD` = `e3aedb25c849dbda931888b27093ac6c444621cb`, with uncommitted changes.
- `git diff --stat`: 5 files changed, 1000 insertions and 193 deletions: `v2/docs/CONOPS.md` (758),
  `v2/docs/OPERATING-ENVELOPE.md` (174), `v2/docs/PANEL.md` (8), `v2/docs/TEST-PLAN.md` (180),
  `v2/ecad/tools/pcb_envelope.yaml` (73).
- Untracked: `drafts/` and this record.

This is not a pinned commit. The baseline commit must carry the sha256 values below for the five files, or the
difference must be reviewed.

**Files judged** (sha256, first 16 hex digits; they equal `drafts/final-shas.txt`):

| sha256/16 | File |
|---|---|
| ab28e85bebec4e4c | `v2/docs/CONOPS.md` |
| 6930e4f05a59ac5c | `v2/docs/OPERATING-ENVELOPE.md` |
| 6333e5d212f57a78 | `v2/ecad/tools/pcb_envelope.yaml` |
| 5bffe28fcca3283f | `v2/docs/PANEL.md` (section 9 changed) |
| a87e66cf431d938d | `v2/docs/TEST-PLAN.md` |
| 5790bc7e444bebc4 / 835910e807d588c4 | `drafts/pwr_red2.py` / `drafts/pwr_red2.out` (to be filed as `records/hc2/`) |
| 932fec2a1ae394e6 | `drafts/handoffs.md` |
| 274d4eee84971521 | `drafts/sc.md` |
| 2ae6c38edd55f051 | `drafts/LAYER-STATUS-layer2.md` |
| fa2b60fbf4cdc486 | `drafts/gen_sch_b.BANK-R1.patch` |
| 8ac3c352b99853cd | `drafts/ASSEMBLY.step10-and-lamp-test.patch` |
| 3f384a558f02729c | `drafts/part_temps.patch` |
| dbc256931885af15 | `drafts/REVIEW-A-BRIEF.md` |

**Sources checked against, at `e3aedb25`:**

| sha256/16 | Source |
|---|---|
| 6c3c93b7f32f953a | `v2/docs/ARCH-PCB-B-IOHA.md` (sections 2, 4 to 8, 10, 12, 13, 15, 15a) |
| bb9c861c9920c8d6 | `v2/docs/feasibility/POWER-THERMAL.md` (7.1, 9.3, 9.4) |
| e57a54d1767bcd59 | `v2/docs/feasibility/EMCON.md` (4.5, 5a) |
| 7f6c34697753bac1 | `v2/ecad/tools/gen_sch_a.py` (the charger at 0x6B, line 708; R17 the 5 mOhm RSR shunt, lines 24 to 48) |
| dedaf34ce285e5ff | `v2/ecad/tools/gen_sch_b.py` (`PORTS` lines 764 to 766; the ring `f = s % 3 + 1` line 788; CP2102N supplies lines 919, 937, 949; `U19` line 974; `U6` on the kit bus lines 1030 to 1040) |
| 5f1ce2dd66ed7d2d | `v2/ecad/tools/gen_sch_c.py` (LEDs lines 190 to 206) |
| d120ebfb9afbee6e | `v2/ecad/tools/gen_sch_e.py` (lines 213, 503 to 508, 524 to 542) |
| 28904a37f2f18103 | `v2/ecad/tools/check_pcb_b.py` (the BEARERS invariant, lines 424 to 431) |
| 469d0820b046ef6f | `v2/docs/records/rv-pwr/pwr_budget.py` |
| 2bae882148b45172 | `v2/vendor/quectel/quectel-rm520n-series-hardware-design-v1.1.pdf` (section 3.2, the feature table) |
| 3e5e927fdf63cf6a | `v2/vendor/ti/bq25731-datasheet.pdf` (SLUSE66A 9.6.8, 9.6.10, Table 9-8) |
| 331f35ed1f027a74 | `v2/vendor/sensirion/sgp41-datasheet.pdf` (operating -20 to +55 C) |
| 5e942dd41e9e4ed0 | `v2/docs/MESHSAT-709-geometry-appendix.md` (32.50 item 6, 32.53 line 2860) |
| acd19f7bfc50b7ad | `v2/ecad/tools/pcb_requirements.yaml` (REQ-025, REQ-036, REQ-052 as they stand) |

**Main as it stands now:** `84e52461` (not `53a98a71`, which `drafts/handoffs.md` section 1 is written against),
compared for integration only: `pcb_requirements.yaml` 00029b87049b1f5f, `PANEL.md` 8eeb152e4d82080c, `ASSEMBLY.md`
30db27eee509212c, `pcb_pack_protection.yaml` 54039554131c1e26, `gen_sch_d.py` 0f1d59fd60ffb5ef,
`review-packets/battery/THERMAL-COORDINATION.md` (its section 4 tables).

**Run:** `drafts/pwr_red2.py`, copied with `pwr_budget.py` at `e3aedb25` into this reviewer's own scratch directory
(outside the worktree and the main tree), reproduces `drafts/pwr_red2.out` byte for byte (sha256 `835910e807d588c4...`,
under a second). **Not re-run:** the closer's `rules_lib.py`, `rules_render.py` and test results, because they write
into a tree. Nothing was run in the main tree, and nothing in the worktree was edited except this record.

## 2. What was verified and holds

- **The bank facts behind every mode.** CONOPS 4c (lines 477 to 488) matches `ARCH-PCB-B-IOHA.md` sections 4 and 15
  and the generator: bank s fails over to slot `s % 3 + 1`; each module has two host ports (USB3-0 home, USB3-1 one
  neighbour bank), so slot 2 can host banks 2 and 1 and slot 3 banks 3 and 2 at once; the four CP2102N bridges are on
  `+5V_DEV` and the radios' software enables are on the kit-bus expander `U6`, so no bank device depends on a dropped
  slot's rail. The per-slot tables (what slot 1, 2 or 3 alone carries) are right.
- **BANK-R1.** The patch exchanges exactly `RB_DP/DM` with `QMX_DP/DM` (port 4, banks 1 and 2) and `USB_PNL_P/N` with
  `USB_WALL_P/N` (bank 1 port 2, bank 3 port 3). On the result, `check_pcb_b.py`'s BEARERS invariant (Iridium, HF,
  APRS) has one bearer per bank; slot 3 alone then hosts GNSS, both E72, Iridium, APRS, the sensor controller, the
  panel controller and LoRa; three of the four core bearers survive any one module loss, as CONOPS line 579 says.
- **B1's sources.** Quectel HD v1.1 section 3.2: in both PCIe modes the module "Supports MBIM/QMI/QRTR/AT over PCIe
  interface", and "For USB-AT-based PCIe mode, the firmware upgrade via PCIe interface is not supported, so USB 2.0
  interface must be reserved for the firmware upgrade". SLUSE66A: VBAT 64 mV per LSB for 1S to 4S (9.6.10); IDCHG
  512 mA per LSB with a 5 mOhm RSR (9.6.8); EN_LWPWR resets to 1 and "ADC is not available in Low Power Mode" (Table
  9-8). `gen_sch_a.py` line 708: the BQ25731 at 0x6B on the kit bus; R17 is the 5 mOhm shunt. 12.8 V less one cell at
  2.50 V leaves 3.43 V on each of the others, as line 723 says.
- **B2's source.** `gen_sch_e.py` lines 524 to 542: the reed reaches the sensor controller alone. The start-up cost
  (60.6 W over two minutes, 7.3 kJ, into 8 to 10 kJ/K, appendix 32.53 line 2860) is under 1 K.
- **B3's arithmetic.** About 108 Wh usable when aged (42.8 x 2.5, 31.38 x 3.47, 21.73 x 5.03); 21.7 W for 7 h is
  about 152 Wh; the daily solar hours (10 to 11, 7.5 to 8, 5 to 5.5) follow from 100 W of front end.
- **Every new figure of pass 2** (PS-SURV-R 23.3 W, 12.8 to 46.9, 5.9 / 4.7 / 3.5 h; PS-EMCON aged 60 % 1.7 h; the
  stage-ambient rows of CONOPS 4c lines 612 to 618; the hot-end cell corners of lines 631 to 636; the COLD block
  rows of lines 661 to 666; 72.7 W over 20 K = 3.6 W/K; `pcb_envelope.yaml`'s `inside_air_bounds_k`,
  `worst_inside_air_c` and `cold_end`; OPERATING-ENVELOPE section 3's tables and the +61.6 to +74.2 C at +55 C)
  reproduces from `pwr_red2.out`.
- **The lamp test.** `gen_sch_c.py`: fifteen expander LEDs plus the TX lamp `D3` make `D1` to `D16`; with the PI ring
  that is seventeen controller-lit indicators, as PANEL line 184, CONOPS line 998 and the ASSEMBLY patch now say.
- **TEST-PLAN.** E3-L carries E3-A's pass line with the lid closed, the owner's example with the SOS path at every
  level, the SGP41 as a failure, and does not waive the generated board; E4-O restores UTC +1.0 C and UTD -9.0 C and
  requires the link after the warm-up; T-H3 replaces ASSEMBLY step 10; the stored and transport states have every
  input unplugged.
- **Labelling elsewhere.** Every 7a row, the Reduced and Heat stage rows, OPERATING-ENVELOPE section 8's D-02b
  paragraph ("The session's definition of 27 September 2026"), `pcb_envelope.yaml`'s `hot_end` and `session_taken`, and
  TEST-PLAN section 1 ("session text, not an owner ruling") mark the session's choices. No em dash was added. Nothing
  is claimed built, tested or working.

## 3. The first pass's findings, each answer checked

| Finding | Answer checked | Disposition |
|---|---|---|
| B1 heat stage losses, 5G, shutdown source | CONOPS line 308, 536 to 557, 715 to 726; 4f line 802; SC-L2-02, 10 | answered (n4 and n8 below are precision items) |
| B2 lid-closed start-up | Startup row line 305, 4c lines 513 to 524, SC-L2-17 | answered |
| B3 M1 and the night | M1 lines 175 to 198, section 6, D-06 row, SC-L2-05 | answered (n11: no decision point) |
| B4 E3-L pass line | TEST-PLAN line 135 | answered |
| B5 REQ-052 not restated down | 4c lines 526 to 591, handoffs 3.6, SC-L2-18, BANK-R1 patch | answered (n1: BANK-R1's cost to the SGP41 unstated) |
| B6 ASSEMBLY step 10 | 4d step 1, T-H3, ASSEMBLY patch | answered (the patch lands with its owner) |
| B7 the cold end | 4c lines 648 to 695, OE section 4, `cold_end`, E4-O | answered (n3 and n10) |
| m1 to m10, m12 | as the brief's table maps them | answered; m4's wording is what P2-B2 below finds incomplete |
| m11 records not filed | handoffs 1 and 12 | still open until the integrating commit (n14) |

## 4. Findings of this pass

### BLOCKING

**P2-B1. The owner-rulings table carries the session's reduced mode, heat stage and BANK-R1 inside D-02b's ruling
cell without marking them as the session's.**
- *Where:* CONOPS line 938 (section 7, row D-02b, column "The ruling"): "**As ruled; carried since 27 September 2026 by
  section 4c:** the reduced mode runs slots 2 and 3, and the owner's example on one module is its heat stage, which
  board B carries once two of its hub ports are exchanged (BANK-R1; ...)".
- *Why it is blocking:* these are SC-L2-01, SC-L2-02 and SC-L2-18 (`drafts/sc.md`), taken under the owner's standing
  rule. The same table's D-06 row (line 945) marks its 27 September addition "taken by the session under the owner's
  standing rule"; the D-02b row names no author, so read alone it states the session's definition as part of the
  owner's ruling. The project's own rule is that a session decision inside an owner rulings list is marked as the
  session's, or it reads back later as the owner's. OPERATING-ENVELOPE section 8 marks the same content correctly.
- *Fix:* one clause: "taken by the session under the owner's standing rule of 26 September 2026 (section 7a)" before
  "the reduced mode runs slots 2 and 3", and "restated by the session" before the two consequences.

**P2-B2. The heat stage is the last stage, and on an input nothing bounds the cells when it cannot hold: at a corner
the record itself calls plausible, inside the in-use envelope, the kit as defined soaks its pack above the maker's
+60 C, against its permanent trips.**
- *Where:* CONOPS lines 562 to 566 ("There is no stage after this one ... the kit then stays in the heat stage, and on
  the pack the gauge's discharge window ends it"); the Heat stage row's Exit (line 308); 4c lines 630 to 646 ("so
  there the kit runs at +40 C only on an input"; "no mode, trigger, bearer set or product decision of this document
  changes with the enclosure conductance, because every control acts on a measured internal temperature or current");
  no row in 4e; TEST-PLAN E3-L (line 135) runs +40 C lid closed on shore with no abort line.
- *What the record says:* at +40 C with the lid closed, at the independent bound's lowest conductance, the heat
  stage's inside air is +60.6 C as generated and +62.1 C after BANK-R1 (`pcb_envelope.yaml` line 67; OPERATING-ENVELOPE
  section 3). On an input the pack carries no current, so its cells sit at about the inside air (the model's own cell
  rise is the pack's I2R over its block conductance, `pwr_red2.py` via `pb.cell_temp`, zero at zero current), and the
  front end's and the charger's conversion losses add heat inside (INFERRED). The charge is held (OTC 44.0 C), the
  discharge FET's opening (OTD 57.5 C) removes no heat, and C1 has nothing left to shed. The cells then sit above the
  maker's +60 C ("Don't leave, charge or use the battery in a car or similar place where inside of temperature may be
  over 60°C", Ver. 1.1, quoted in TEST-PLAN section 6), within about a kelvin of the second level's lowest
  over-temperature trip (62.7 C, TEST-PLAN P10, which blows F2 and retires the pack) and near the gauge's permanent SOT
  (64.2 C, TEST-PLAN section 5 row 8). The battery packet on main already records the same hole for the case where the
  gauge's readings reach no module, which is the heat stage as generated: "nothing sheds the kit's own heat by cell
  temperature, and on shore L8 cannot either" (THERMAL-COORDINATION section 4, the "sensor controller down" row). M2,
  the vehicle move with the lid closed on the vehicle input, is exactly this state.
- *Why it is blocking:* the layer closes its hot end on the argument that behaviour on measured temperatures makes it
  indifferent to the unmeasured conductance (CONOPS 4c, `drafts/LAYER-STATUS-layer2.md` "Stated open"). At the low end
  of the recorded conductance that behaviour runs out and leaves a permanent protective action as the first one to act;
  "no further stage" is this layer's decision, and it rests on a bound that includes failure. Whether the kit can hold
  +40 C with the lid closed is layer 4's (FEA-004, T-H1); what it does when it cannot is this layer's and needs no
  measurement. (The first pass's m4 suggested the present wording; it covered the pack and missed the input.)
- *Fix:* define the behaviour past the heat stage on measured temperatures, on the pack and on an input. For example:
  with C1's triggers still set in the heat stage and the hottest cell (after BANK-R1, where the gauge is read) or the
  inside air (as generated, where it is not) at a stated threshold that keeps the cells under +60 C with the gauge's
  error budget, the bridge shuts every module down, the charge stays held, the e-paper and MASTER WARN say why, and
  the kit restarts only once the inside air has fallen by a stated margin; PROVISIONAL thresholds, the session's, in 7a
  with a reversal. Carry it into the Heat stage row, 4c's "no further stage", 4e (a row), 4f, M2, OPERATING-ENVELOPE
  section 4's hot-end carve-out and `pcb_envelope.yaml`'s `hot_end`, and into E3-L: its expected action at +40 C, and an
  abort at a cell surface of +59 C so that the acceptance test never drives the pack into its permanent trips. State in
  4c that at that corner closed-lid operation at +40 C is predicted to fail REQ-052 on any supply, not only on the pack
  (a layer-4 item under FEA-004). This lowers no requirement and narrows no envelope: REQ-052 and +40 C stay, and the
  pack is protected where the design cannot yet show it meets them.

### MINOR

- **n1. BANK-R1's cost to the SGP41 is unstated.** OPERATING-ENVELOPE lines 156 to 161 give +55.6 C lid closed on
  appendix 32.53's conductance after BANK-R1 (54.6 C as generated), then say "At the independent bound that is past
  the SGP41's +55 C": the design record's own figure is past it too once BANK-R1's 1.6 W is added. So E3-L's SGP41
  criterion (pass-1 B4) is predicted to fail at +40 C lid closed on both bounds in the required stage. State it in OE
  section 3 and beside BANK-R1 in CONOPS 4c, name the route (a wider-range gas sensor, OE section 7 option 2) and the
  decision point (board E's layout entry); `drafts/LAYER-STATUS-layer2.md` lists the SGP41 at 62.1 C only.
- **n2. REQ-069 is not independent of this layer.** CONOPS line 303 says "No mode, interface or board of this layer
  depends on its answer" and then that a pack required to travel apart reopens its bonded mounting (layer 7); that
  answer would also change SC-L2-03's transport half (pack fitted) and the Transport row. State the dependency and its
  decision point (before the pack's mounting is frozen), and give REQ-069 the compact engineering question the owner's
  prompt section 6 asks for (attempts: UNECE refused this host with HTTP 403 on 27 September 2026; options include
  another public copy of the ADR text and the UN Model Regulations' prototype-battery provision; recommendation;
  expertise; cost of a UN 38.3 test if needed). LAYER-STATUS carries two lines.
- **n3. E4-O does not say what powers its 4 h.** TEST-PLAN lines 27 and 140: "started warm or from shore or vehicle
  input". The cold warm-up draws about 71 W, 1.5 h on an aged pack at +20 C and less in the cold (CONOPS line 394), so
  on the pack alone E4-O fails on energy before it answers the carve-out. State that it runs on an input.
- **n4. The heat stage as generated also loses inputs of the PA's guards.** K2's cell gate and C4's 2.70 V cut read
  the gauge (POWER-THERMAL 9.3), which reaches no module in that stage, while a headset push to talk can still key the
  PA (`KEY = PTT_ANY AND TX_INHIBIT_n`). State whether the bridge holds `PA_SW_EN` off there (APRS is lost anyway) or
  which reading stands in (the charger's IDCHG for C4's current; the flange ADC at 0x48 and the TMP117 stay on the kit
  bus).
- **n5. Integration is against `53a98a71`; main is `84e52461`.** Since then: `9f28c238` draws the hardware EMCON lamp
  `D22` on board C, and main's PANEL section 4 says "The lamp test cannot light `D22` ... setting EMCON is its test",
  while this worktree's PANEL line 184 says the lamp is lit by the lamp test "only if its circuit is given a test tie",
  and CONOPS lines 311, 459 to 460 and 466 to 467 still call it owed; `73d5df1e` writes UTC 1.0 / OTC 44.0 C and UTD
  -9.0 / OTD 57.5 C into `pcb_pack_protection.yaml` itself, while CONOPS lines 560 and 600 say the file carries 0 to 45
  and -10 to 60 C; `45f6d83f` and main's ASSEMBLY now count 17 light guides (`D1` to `D16` and `D22`), beside which
  "seventeen controller-lit indicators" must keep saying which seventeen. Reconcile in the integrating commit; take
  every pin and binding from that commit's files (handoffs 3.1 already says so).
- **n6. Stale line citation.** CONOPS lines 265 and 477 to 478 cite `gen_sch_b.py` line 543 for the ring; at
  `e3aedb25` `f = s % 3 + 1` is line 788 (543 is PCIe AC coupling). `ARCH-PCB-B-IOHA.md` section 15 carries the same
  stale ":543". The fact stands.
- **n7.** OPERATING-ENVELOPE line 438 ("What these rulings leave open: ... the pollution degree ... and the duty cycle")
  reads as open while section 5 says the session took both on 27 September: add "since taken by the session
  (section 5)".
- **n8.** CONOPS lines 308 and 543 call the 5G module's USB link "its only firmware-update path"; the same HD's feature
  table lists "(D)FOTA (A/B system updates supported)". Say "its only wired firmware-update path, which Quectel
  reserves USB 2.0 for".
- **n9. NEED-10's cost of the storage decision is not reported.** The rows state that the lid and tamper log does not
  run in PS-SHUT, but LAYER-STATUS's "changed consequences to report to the owner" omits it, and handoffs 3.6 does not
  restate REQ-036 (its acceptance: the log records "with the kit on and off"). Add both: the case-open record covers
  use and PS-OFF, not storage or transport.
- **n10. The cold end's options miss the one that needs no part.** The fans are what take the enclosure from about
  2.1 W/K in still air to 3.0 to 3.3 W/K (appendix 32.53 line 2860); the mixer fans are on the sensor controller's PWM
  (`gen_sch_e.py` lines 503 and 508). Slowing or stopping them while the inside air is under 0 C lowers the conductance
  the warm-up works against. Add it to CONOPS 4c and the LAYER-STATUS compact question (T-H1 already measures fans on
  and off).
- **n11. The M1 and SGP41 findings carry no decision point.** M1's routes that reopen D-06 or D-01 change the pack
  pocket: name the stage by which the owner's answer is needed (the pack's placement freeze, the same point as FEA-004).
- **n12.** `pcb_envelope.yaml` line 35 files an inside-air carve-out (`below_c: 0`, "inside air, not ambient") under
  `ambient_c.carve_outs`. No tool reads it at `e3aedb25` (`part_temps.py` reads only `above_c` with "reduced mode"),
  but the list's name says ambient. Move it under `cold_end` or key it `on: inside_air`.
- **n13. A battery-packet fallback conflicts with the heat stage as generated.** THERMAL-COORDINATION on main (the
  "sensor controller down" row) drafts a panel fallback to the reduced mode when the sensor controller's pack readings
  stop for 10 s; in the heat stage as generated they stop by design, so the fallback would re-power slot 3 and the kit
  would cycle between the two stages. Reconcile with the battery stream (for example the charger's readings as the
  fallback's input in that stage) and add it to handoffs section 11.
- **n14 (pass-1 m11, still open).** `records/hc2/`, `records/w1/`, the first pass's record and the brief are not
  filed; CONOPS line 58 already calls `records/hc2/` "filed with this revision". An acceptance item until the
  integrating commit.

## 5. The audit's acceptance items for layer 2

| Item | Evidence in the worktree | Finding |
|---|---|---|
| Normal scenario | M1, Normal row, 4a (PWR-F07 figures) | met |
| Degraded scenario | M5, Degraded row, 4c (reduced mode, heat stage in both configurations, recovery targets), 4e | not met: P2-B2 (the last stage on an input) |
| Startup scenario | Startup row, 4c start-up paragraph (SC-L2-17) | met |
| Charging scenario | Charging row | met |
| Shutdown scenario | Shutdown row; 4c graceful shutdown on the pack and in the heat stage as generated | met for the energy end; P2-B2 for the thermal end |
| Storage scenario | Storage and Transport rows, 4c preparation, SC-L2-03; cell figures checked | met in substance; n9; BAT-F19 stated open outside the session's authority |
| Service scenario | Service and Commissioning rows, 4d | met (the ASSEMBLY patch lands with its owner) |
| Fault scenarios | 4e | not met: P2-B2 (no row for the heat stage exhausted); n13 |
| Operating envelope | OPERATING-ENVELOPE 2 to 5, `pcb_envelope.yaml` | met at requirement level with the hot and cold bounds stated open; n1, n7, n12 |
| Simultaneous modes and duty | section 5, the planning duty profile, PS-BUSY bounded, K1 to K5 | met |
| Explicit behaviour of the core functions | 4f, 4b.1, PANEL 9 | met; n4 |
| Product decisions settled under existing authority | 7a; the owner-level conflicts (M1 against D-06, BAT-F19) reported, not asked | met, with n2 (REQ-069's dependency) and n11 |
| Consistent with the current analyses | 4a, 4c, 5, 6 against POWER-THERMAL, IOHA, EMCON | met for the layer's own files; POWER-THERMAL, ARCHITECTURE, IOHA, ZEROIZE and PANEL line 5 wait on hand-offs; n5, n13 |
| TEST-PLAN envelope limits consistent with the rulings | sections 1, 2, 6, 8 | met; n3; P2-B2 for E3-L's abort |
| Every owner ruling recorded | CONOPS 7, OPERATING-ENVELOPE 8 | recorded; not met as labelled: P2-B1 |
| Every source cited is in the repo | records/hc2, records/w1, A06, the reviews | not met until the integrating commit (n14) |
| Review A held and recorded | this record | held; two BLOCKING findings open |

**The owner's section 2 test.** The seven blocking findings of the first pass are answered in the documents, and the
figures reproduce. The layer is not yet complete: one choice of the session reads as the owner's (P2-B1); the hot end's
closing argument, that behaviour on measured temperatures makes the layer indifferent to the conductance, fails at the
recorded low end on an input (P2-B2), which is a feasibility bound including failure under a decision this layer
takes; and the package is not versioned (uncommitted worktree, hand-offs against an older main, records unfiled).
The cold-end bound (3.6 W/K), the hot-end ambients, M1's night, BAT-F19 and REQ-052 on the generated board are
stated open with owners and routes, and none of them is closed by lowering a requirement.

## 6. Verdict

**FAIL for this pass; layer 2 is not complete.** Two BLOCKING findings stand: P2-B1 is a one-clause labelling fix;
P2-B2 needs one defined behaviour (a final thermal control past the heat stage, on the pack and on an input) carried
through the named sections and E3-L. Neither needs new evidence or a measurement. Once both are answered in the
documents, the hand-offs are re-based on main `84e52461` (n5) and integrated, and the records are filed, a
confirmation at the integrating commit, limited to the difference from the sha256 values above plus those fixes, can
decide the baseline.
