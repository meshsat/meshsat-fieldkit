# c23, the targeted fixer: answers to Review A pass 2 (layer 2) and Review B pass 1 (layer 3)

MESHSAT-1357, 27 September 2026, from about 11:05 CEST. Prototype design: nothing here has been built, ordered,
powered or tested. The owner's execution prompt (section 4) says that after two unsuccessful attempts to close the same
issue the method changes; this pass does not redo either layer. It fixes the named findings only, in fnd/hc2 (layer 2:
CONOPS, OPERATING-ENVELOPE, TEST-PLAN, `pcb_envelope.yaml`) and fnd/hc3 (layer 3: the registry through its apply
script), continuing from the files the layer-3 closer's second pass left when a usage limit stopped it at about 07:52.
Every engineering choice below is the session's under the owner's standing rule of 26 September 2026, with its reason
and reversal; none is the owner's. Nothing was committed or pushed; the main checkout was not edited and no gate was run
in it. Registry ids are given as they fall on main `a8652172` (this worktree's are one lower for SC and two lower for the new S items;
`drafts/hc3/ids.txt`).

| Finding | Outcome | Where |
|---|---|---|
| Review A P2-B1 | CLOSED | fnd/hc2 CONOPS section 7, row D-02b |
| Review A P2-B2 and Review B B1 (the hot end on an input) | CLOSED, with three recorded open items (HOT-R1, a hardware stage question, FEA-004's firing question) | fnd/hc2 CONOPS 3 (M2), 4, 4c, 4e, 4f, 7a; TEST-PLAN E3-H; OPERATING-ENVELOPE 3, 4; `pcb_envelope.yaml`; `drafts/hotstop_bounds.py`; fnd/hc3 REQ-077, SC-49, SC-50, S-57, S-58, and REQ-024, REQ-046, REQ-052, CON-012, FEA-004, SC-18 |
| Review B B2 (the mast-down alarm) | CLOSED | REQ-041, SC-47; CONOPS 4e, 7a |
| Review B B3 (the NVG target) | CLOSED | REQ-034, SC-48; CONOPS section 4 NVG row, 7a; `v2/vendor/standards/mil-std-3009-nvis-2001-02-02.md` |
| Review B B4 (the solar window) | CLOSED | REQ-016, SC-36; CONOPS M1 |
| Review B B5 (M1 against REQ-016, REQ-072 and SC-37) | CLOSED | CONOPS M1, 7a; SC-37 |
| Review B B6 (CFL-010) | CLOSED | CFL-010, CON-025, S-13; `V2-SPEC-CFL-010.on-main.patch` |

## P2-B1: D-02b's row carried the session's choices without saying so

- **Finding.** CONOPS section 7, row D-02b: after "As ruled; carried since 27 September 2026 by section 4c:" the row
  listed three of the session's choices (the reduced mode on slots 2 and 3, the one-module heat stage, BANK-R1) as if
  they were the owner's ruling.
- **Changed.** fnd/hc2 `v2/docs/CONOPS.md` section 7, row D-02b: the reviewer's two clauses, "with choices taken by the
  session under the owner's standing rule of 26 September 2026 (section 7a), which are not part of the ruling" and
  "restated by the session" before the two consequences; the new hot stop is listed there as the session's too.
- **Evidence.** The row as it now reads, beside D-06's row, which already marks its 27 September addition as the
  session's; the choices are in section 7a (the reduced mode, the heat stage, BANK-R1, the hot stop, HOT-R1).
- **Outcome.** Closed.

## P2-B2 and B1: past the heat stage the kit acts on the pack's measured cell temperature, on every input

- **Finding.** On shore or vehicle input at +40 C, lid closed, at the independent bound's lowest conductance, idle cells
  sit at about the inside air (60.6 C as generated, 62.1 C after BANK-R1), above the maker's +60 C, and nothing acts by
  cell temperature before the destructive backstops (the second level's trip from 62.7 C that blows F2, the gauge's SOT
  from 64.2 C). No core record required the kit to act before idle cells pass +60 C.
- **Decided (session design decision, SC-49 "the hot stop" and SC-50 "HOT-R1").**
  - *What it acts on and when.* The hottest of the four cell thermistors TS1 to TS4, as the pack gauge reads them, in
    every mode and every input state. **H1, shed to the minimum load,** at +56.5 C in two readings a second apart:
    every running module shut down cleanly (`PI_SHDN_REQ`) and `SLOT_EN1..3` dropped within 60 s; the monitor, heater,
    board D, PoE, the USB-C outlet, the wall port's VBUS and the PA and HF holds off through board A's expanders; the
    shared device rail kept (it feeds the panel controller); the mixer fans at full speed; the charge held. **H2, the
    kit's controlled shutdown,** at +57.0 C with H1 acting: `PI_KILL`, so `Q1` takes the LTC2954's `KILL` low and
    `RAIL_EN` stops every converter on board A. Released at +46.5 C: H1 by the panel controller at most once in 30
    minutes (back to the heat stage's one module), H2 by the operator's MAIN, the panel controller raising no slot
    until the cells read released.
  - *Charging held.* By the gauge's own window at these readings (T3 42 C inhibit, T4 43 C suspend, OTC 44.0 C;
    `THERMAL-COORDINATION.md` section 4) and, in H1, by the charger's `CHRG_INHIBIT` bit (ChargeOption0 bit 0, TI
    SLUSE66A 9.4.1 and 9.6.1), which ends a charge while the converter keeps carrying the kit from the input. Not by
    board A's `CHG_INHIBIT` line: it puts the charger in HIZ, whose converter shuts off (SLUSE66A 9.3.8), and with no
    BATFET (`gen_sch_a.py` line 782 at `a8652172`) the kit's load would move onto the pack.
  - *Thresholds, from the battery packet's error budget* (`review-packets/battery/THERMAL-COORDINATION.md` section 3,
    main `a8652172`): the published hot-side terms are 0.71 + 0.40 + 0.80 + 0.16 = 2.07 K. A cell is at most 58.57 C
    when H1 acts and 59.07 C when H2 acts (1.43 K and 0.93 K inside +60 C, left for the budget's two TBD terms, the ADC
    and the gradient, read in TEST-PLAN P14). In the same reading the order is fixed whatever the sensor's error: C1
    55.0, H1 56.5, H2 57.0, OTD 57.5 C (1.5, 0.5, 0.5 K apart), so on the pack the kit sheds and stops before the pack
    drops out. The stop's own detection is at most 1.2 s slower than the gauge's, 0.06 K at the budget's 3.2 K per
    minute. When P14 lowers OTD, H1, H2 and C1's cell trigger come down with it. PROVISIONAL.
    `drafts/hotstop_bounds.py` (fnd/hc2, stdlib, self-checked against `pwr_red2.out`'s own 60 C ceilings) prints these
    and the ambients below (`drafts/hotstop_bounds.out`).
  - *Which controller and which path, from the netlists at `a8652172`.* Detector: board E's sensor controller `U10`,
    the gauge's only SMBus host (`gen_sch_e.py` line 264 `J_SMB`; line 581, GPIO2 and GPIO3 on `SMBD` and `SMBC`), on
    board E's always-on domain (`U12`, line 565, EN on `CELL_F`). Actor: the panel controller `U3` on board C
    (`gen_sch_c.py` line 127): `SLOT_EN1..3` (GPIO13 to 15, `J_PANEL` 21 to 23, `J_AB1` 17 to 19) to board A's `U4`,
    `U5`, `U6` (`gen_sch_a.py` lines 916, 949, 917); `PI_SHDN_REQ` (GPIO18) to every module's GPIO6 (`gen_sch_b.py` line
    402); the kit bus (GPIO0, GPIO1) to `U27` 0x21 and `U28` 0x24 (`gen_sch_a.py` lines 1259 to 1266) and the charger
    at 0x6B (line 784); `PI_KILL` (GPIO19, `J_AB1` pin 10) to `Q1` and the LTC2954 (lines 269, 273). **As generated the
    only path between them is USB through a running module:** `USB_E6` (`gen_sch_e.py` line 590; `J_BLK` 9 and 10,
    `J_DOCK` 9 and 10, `J_AB1` 25 and 26) to board B's bank 3 hub port 2 (`gen_sch_b.py` line 766), the bridge, and on
    to the panel controller on bank 1 port 2 (line 764). It is absent in the heat stage as generated (bank 3 has no
    host) and H1 itself removes it. **HOT-R1:** the dock's spare contact already runs from board E's `J_BLK` pin 12
    (`BLK_SPARE`, only `TP7`, lines 562 and 693) through the dock to board A's `J_DOCK` pin 12 (`DOCK_SPARE`, line 226),
    which lands on `U27` pin 18, whose change raises `EXP_INT` (`R110`, line 1267), the panel controller's GPIO24
    (`J_AB1` 13, `J_PANEL` 6). HOT-R1 drives it from `U10` GPIO19 (pin 30, not connected) through an open-drain 2N7002
    with a gate pull-down, and pulls it up with 10 k on board A; `IF-AE-DOCK` names pin 12. Four states: 1 Hz toggle
    (read, below H1; each edge after a fresh reading), 5 Hz (H1), held low (H2; a short to ground also stops the kit),
    held high (the sensor controller lost). On the last the panel controller applies the same steps to board B's
    TMP117 (`gen_sch_b.py` line 1050, on the kit bus) at +55.0 and +56.0 C with THERMAL-COORDINATION section 7's
    fallback; the line also stops that fallback mistaking the heat stage as generated for a lost sensor controller
    (Review A's minor n13). The panel controller reads the line before raising any slot at start-up.
  - *Firmware or hardware.* Firmware (the two controllers) over one hardware line, through actuators whose pull-downs
    keep a released load off. A control, not a protection.
  - *The backstops behind it, named as destructive.* The gauge's OTD (57.5 C) is firmware and recoverable but removes
    no heat on an input; the hardware backstops are all destructive: board P's second level (BQ7720700, fixed 70 C,
    from 62.7 C at its thermistor, blows F2 and retires the pack), the gauge's SOT (65.0 C, from 64.2 C in truth,
    permanent, F2 blown) and the PTC at the FETs (about 110 to 133 C, permanent) (`THERMAL-COORDINATION.md` section 4,
    L8 to L12, and section 8).
- **Changed.**
  - fnd/hc2 `v2/docs/CONOPS.md`: status paragraph and sources; section 4 (a new Hot stop row; the Heat stage row's Exit
    "Past it, the hot stop" and its Guarantee); section 4c (the hot stop: the two steps, the thresholds, the path,
    HOT-R1, firmware or hardware, the destructive backstops, the open design question, the cost with FEA-004 OPEN;
    the "whether the hot end holds" and "why this layer can close" paragraphs); 4e (three rows: the hot stop, its
    detector lost, and the mast-down alarm of B2); 4f (Pack safety); M2 (a hot vehicle); 7 (D-02b); 7a (three rows:
    the hot stop, HOT-R1, the hardware stage question, and the heat stage's row marked).
  - fnd/hc2 `v2/docs/TEST-PLAN.md`: a new row **E3-H** (the hot stop, read during E3-A's and E3-L's runs; the
    expected action of both steps before any cell surface reaches +59 C, on the pack and on shore, no permanent
    protection action; the TMP117 stand-in with the sensor controller held in reset; **the abort at a cell surface of
    +59 C for every E3-A, E3-L and E3-H run**; where the stop acts inside the envelope, E3-L's stage criteria are a FAIL
    of REQ-052, not a waiver). **E3-L's and E3-A's rows are byte-for-byte unchanged** (asserted by the edit script);
    section 6's introduction says so.
  - fnd/hc2 `v2/docs/OPERATING-ENVELOPE.md` (revision note; section 3's "the heat stage, which nothing further sheds"
    corrected and the input case stated; section 4's hot end names the stop and says its firing inside -20 to +40 C is
    FEA-004's; the operating modes line) and `v2/ecad/tools/pcb_envelope.yaml` (`hot_end.hot_stop` with 56.5, 57.0,
    46.5 and its OPEN status; the worst-air comment; `document_sha256` re-pinned to `354bc222...`); fnd/hc2
    `drafts/pcb_rules_coverage.ENV-001.patch` re-pinned to the same; `drafts/final-shas.txt` refreshed.
  - fnd/hc3 registry, through `drafts/hc3/ops_l3.py` and `ops_l2.py` (edited by `scratchpad/c23/edit_ops_c23.py`,
    regenerated into `apply_registry.py`): **REQ-077, a core requirement under NEED-13**: "In every mode and on every
    input state ... the kit acts on the pack's measured cell temperature before any cell passes the cell maker's +60 C,
    idle cells on an input included: it sheds to its minimum load and then shuts itself down in a controlled way with
    the charge held, before the pack gauge's discharge over-temperature or any permanent pack protection acts, and it
    restarts only once the cells have cooled"; acceptance measurable at desk (a path that needs no compute module, and
    the thresholds under OTD and inside +60 C by the published budget) and on the prototype (TEST-PLAN E3-H, both steps
    before +59 C, no permanent action, the abort); MANUAL_REVIEW and PROTOTYPE_MEASUREMENT, SCHEMATIC to PROTOTYPE;
    reads **FAIL** at SCHEMATIC on `gen_sch_e.py` (at e3aedb25, and by a reading op on `a8652172`'s `f275102965fafa10`)
    until HOT-R1 is drawn. SC-49 and SC-50; open items **S-57** (HOT-R1 owed on boards A and E) and **S-58** (the
    hardware stage question). Carried into **SC-18** (the heat stage, "past it, the hot stop"), **CON-012** (the
    statement names the stop and its ambients; the acceptance separates the owner's D-02b acceptance from the session's
    choices), **REQ-024** (the stop is not a carve-out; FEA-004's, open), **REQ-046** (its windows act on charge and
    discharge; an idle pack on an input is REQ-077's), **REQ-052** (where the stop acts at +40 C it reads FAIL there on
    any supply, OPEN until T-H1) and **FEA-004**'s reopen list (whether the stop fires inside the envelope, with the
    ambients).
  - fnd/hc3 drafts: the second pass's `CONOPS-pass2.on-hc2-d11.patch` and `TEST-PLAN-hotstop.on-hc2.patch` (whose hot
    stop stood on the TMP117 where the cell readings did not reach a module) are retired to `drafts/hc3/superseded/`;
    `CONOPS-d11.on-hc2.patch` is rebased; the TEST-PLAN guard accepts `652353b9cb624cf3`, read by hand.
- **Whether it fires inside the envelope (FEA-004, OPEN; written on the pages).** On the model's figures H1 acts, lid
  closed, at the independent bound's worst corner from +34.8 C (pack) and +35.9 C (input) as generated, +33.2 C and
  +34.4 C after BANK-R1; lid open from +37.5 and +38.6 C (+36.1 and +37.3 C); on appendix 32.53's conductance not below
  +40.3 C lid closed and +48.1 C lid open. So at the worst corner closed-lid operation at +40 C (and lid-open) is
  predicted to fail REQ-052 on any supply; that stays OPEN until the empty-case heat-balance test (TEST-PLAN T-H1).
- **Outcome.** Closed: the stage is decided and written, the requirement exists and is carried, and the pages say what
  stays open. Three items are recorded, each with its compact engineering question (`drafts/hc3/blocked-questions-layer-3.md`
  items 13 to 15):
  1. **HOT-R1 on boards A and E (S-57).** Issue: REQ-077 needs a path that needs no compute module. Affected: boards A,
     E; IF-AE-DOCK; the two firmware contracts. Evidence: the netlist facts above. Options: (a) HOT-R1; (b) USB only
     (not available in the heat stage as generated); (c) a kit-bus device on board E (no spare pair through the dock).
     Recommended (a). Expertise: the board owners. Cost: one transistor, two resistors; lead time the next regeneration
     of A and E, before their layout entry.
  2. **A non-destructive hardware stage (S-58).** Issue: behind the firmware stop the hardware is destructive. Options:
     (a) none; (b) the packet's hold on board P (removes no heat on an input); (c) a comparator on its own thermistor on
     the hottest cell, at most 57.5 C with its tolerance and 5 K hysteresis, taking board A's KILL low without firmware.
     Recommended (c) to the D-09 battery-and-protection reviewer with Q-P15. Expertise: battery protection and
     functional safety. Cost: a comparator, a reference, a thermistor and a transistor per kit (no part filed, TBD);
     decided before the layout entry of A, E and P.
  3. **The firing inside the envelope (FEA-004).** Issue, evidence and ambients as above. Recommended: T-H1 before the
     placement freeze. Equipment: the empty-case rig (a current-moulding Peli 1450, the 1450PF frame, a plate blank,
     resistive loads, thermocouples); its purchase is the owner's to authorise; weeks, on the case's delivery.

## B2: REQ-041 dropped the lightning detector's mast-down alarm

- **Changed.** REQ-041's acceptance: its alarms are REQ-042's and the mast-down alarm, MASTER WARN with the cause when
  the AS3935 reports a lightning event at a storm distance of 10 km or less, cleared after 30 minutes with none at 10 km
  or less, checked by injecting the interrupt and a 10 km estimate (SC-47); CONOPS 4e row and 7a row.
- **Evidence.** Appendix 32.50, sensor 6 (approved "with a mast-down alarm"); V2-SPEC line 65; the AS3935 factsheet
  (`v2/vendor/sciosense/sciosense-as3935-factsheet.pdf`: the 30-30 rule, "the storm is within 10 km", "Stay in the
  shelter for 30 minutes").
- **Outcome.** Closed (drafted by the interrupted second pass; c23 checked the factsheet's words and added the CONOPS
  rows).

## B3: REQ-034 had no night-vision compatibility target

- **Changed.** REQ-034's acceptance names MIL-STD-3009's lighting system NVIS compatible examination (5.7.2) for a
  Type I, Class B NVIS on the panel, its light guides and the monitor at their NVG levels, TABLE III radiance recorded
  as characterisation, and "No document claims night-vision compatibility until that examination has passed on the
  built prototype" (SC-48); CONOPS section 4's NVG row and 7a. The transcription is filed by the apply script as
  `v2/vendor/standards/mil-std-3009-nvis-2001-02-02.md` with its SOURCES.yaml block.
- **Evidence.** MIL-STD-3009 (2 February 2001, Distribution Statement A; sha256 `93d34359...` of the file read): 1.3,
  3.1.3 (Class A not compatible with red), 3.1.4, 5.7.2 and 5.7.2.2 (checked by c23 against the text); appendix 32.50
  item 16c (the NVG light red). One sentence of SC-48 was given its evidence reference so the claims screen passes.
- **Outcome.** Closed.

## B4: the solar window allowed 28 V, above the 25 V the generator declares

- **Changed.** REQ-016: at most 25 V open circuit at the panel's coldest, as board E's generator declares the panel
  entry (v_max on `PV_P` and `PV_IN`, against which the parts are judged), 17.6 V held, 100 W; the SMCJ28A named as
  standing off above the window; SC-36 restated; CONOPS M1 carries the same window.
- **Evidence.** `gen_sch_e.py` (the panel entry's intent, v_max 25.0; D4 SMCJ28A; R8, R9, F2, J_SOLAR).
- **Outcome.** Closed (the preferred 25 V; no part is re-judged).

## B5: CONOPS M1 against REQ-016, REQ-072 and the solar reference-day choice

- **Changed.** fnd/hc2 CONOPS M1: the "LT8705A limit TBD", "REQ-016's window follows from layer 4" and "no insolation
  figure is held" sentences are replaced by the window as REQ-016 states it, the design month's PVGIS figure (September
  at Leiden, 4.0 kWh/m2 a day on the optimal plane, about 266 W of panel for the 72 hours) and REQ-072 reading FAIL at
  desk on both limits. The reference-day choice (SC-37 on main; the reviewer's "SC-36" in the worktree numbering) first
  said "from October to March no solar-sustained mission duration is claimed"; that clause narrowed M1 in a session
  choice alone, which this layer may not do, so the second pass withdrew it and the choice's scope statement is now
  that September is the design month, not a season M1 is limited to, with a month of less sun asking more of the panel
  (December about 1.1 kWh/m2), recorded beside it at layer 4. CONOPS M1 carries that statement, and a 7a row.
- **Evidence.** `v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json` (Sep 4.01, Dec 1.13 kWh/m2, as Review B
  checked); REQ-072's evidence (3,082 Wh over 72 h, 991 Wh a day, 1,066 Wh at 0.93, about 266 W).
- **Outcome.** Closed. Reversal: another site or month, or the owner's own M1 setting.

## B6: CFL-010 was held open on a later board's work

- **Changed.** CFL-010 is resolved on the settled description (CONFLICT_RESOLVED, PASS on V2-SPEC at integration,
  ADVISORY) and its acceptance no longer carries the two non-conflict items. The SIM TVS array is board B's constraint
  **CON-025** (at most 10 pF per channel on each holder's RST, CLK and DATA, Quectel RM520N HD v1.1 section 4.1.7),
  reading **FAIL** until drawn: on main `a8652172` by c23's hand reading of `gen_sch_b.py` (`dedaf34ce285e5ff`, line
  676: "The TVS array the HD asks for (at most 10 pF) is an open item in drafts"); on board B's round 8 (fnd/r8int3,
  `af6e5821e21b70ef`) the apply script takes the PASS reading instead (TI TPD4E001DBVR `U222`, `U223`, 1.5 pF typical,
  SLLS682P 5.4). S-13 keeps only the eSIM variant's order code. V2-SPEC's correction is `V2-SPEC-CFL-010.on-main.patch`.
- **Outcome.** Closed.

## Validation

- fnd/hc3 worktree (from `e3aedb25`), `drafts/hc3/rebuild.sh`: 414 ops, 383 changes; `rules_lib.py requirements` 142
  records, 0 errors, 0 warnings; `rules_render.py --requirements --check` current.
- Integration simulation on a scratch clone of main `a8652172` (`drafts/hc3/sim/build_sim_clone.sh`, `BASE=a8652172`,
  never pushed; driver `scratchpad/c23/validate.sh`): fnd/hc2 merged, the drafted patches applied (all ok; fnd/hc1's
  CONOPS patch refuses its two redundant hunks as documented); the apply script's dry run refuses nothing and reports
  one expected `HAND RE-READ` (CON-025's round-8 PASS, whose revision is not on main); 410 changes; a second run writes
  nothing; `rules_lib.py requirements` 142 records, 0 errors, 0 warnings; the trace page rendered and current;
  `claims_check.py` 84 claim sentences, 0 unqualified; tests test_requirements 60 passed and 1 skipped,
  test_envelope_data 6, test_part_temps 5, test_pack_protection 8, test_energy_chain 26, test_rules_status 35 and 1
  skipped, test_rules_registry 5, test_pcb_rules 16, test_artefact_recording 18, test_handover 12; none failed. The
  whole suite was not run.
- Five citations carried into the changed envelope files were re-read by hand (`drafts/hc3/citations-reread.md`, last
  section; `reviewed-pairs.json`).
- Main has since moved to `84d0a527` (H1.1, handover pages only); none of the layer files differs from `a8652172`.

## Not done here, and why

- Review A's minors n1 to n14 (n13 is answered as a side effect of HOT-R1's lost state) and Review B's minors m8, m9
  and m15: outside the named findings. Review B's m1 to m7 and m11 to m14 were drafted by the interrupted second pass
  and are carried in its ops unchanged, validated by the runs above but not re-reviewed by c23; m10 (CON-012's
  acceptance) is answered by c23's rewrite of that acceptance for B1.
- `PANEL.md` is not edited: the hot stop's firmware contract (the four line states, the two steps) is a layer-5
  hand-off (fnd/hc2 `drafts/handoffs.md` pass 3, item 16), and editing PANEL now would break the registry's rebinds on
  its sections.
- The records filing (`records/hc2/` including `hotstop_bounds.py` and `.out`), Review A's next pass and Review B's
  second pass are the integrator's and the reviewers'.
