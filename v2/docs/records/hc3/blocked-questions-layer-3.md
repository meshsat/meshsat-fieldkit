# Layer 3 (requirements): the questions left open, each as an engineering question

Prepared 27 September 2026 by the layer 3 closer (MESHSAT-1357, worktree fnd/hc3) for the handover's continuation
brief, in the form the owner's handover prompt asks (section 6: exact issue, affected decisions and boards, evidence,
attempts, options, recommended next action, expertise or equipment, cost and lead time where known). Registry ids are
the ones the apply script gives on main at 53a98a71 (`drafts/hc3/ids.txt` has both numberings; the script prints the
final ones). **On main a8652172** (27 September 2026, the targeted fixer c23) S-47 is taken by HC9-E1, so every open
item this file numbers S-47 or higher is one higher there (S-51 is S-52, and so on; items 13 to 15, added by c23, give
both). Nothing here has been built, ordered, powered or tested.

**Why layer 3 can close with these open (the owner's section 2 tests).** Requirements are complete "when their scope,
limits and verification methods are settled". For each item below the requirement's statement and pass line are
settled; what is open is a fact to establish (a classification, a maker's position), a design answer at layer 4, 5 or
6, a physical result, or an owner's own setting. Items 3, 7, 8 and 9 are the ones that could change requirement TEXT, and
each says so and names the layer whose decision depends on it. None is hidden as a future task: each is an open item
(S-nn) or an open record in the registry, and REQUIREMENTS-TRACE.md lists them.

## 1. The pack's dangerous-goods classification (REQ-069, open item S-51)

- **Issue.** No transport route is claimed for the kit with its 145 Wh 4S3P pack, which is built for the kit and has
  no UN 38.3 test summary; its classification and the conditions it could travel under are not established.
- **Affects.** REQ-069, CONOPS section 4's Transport row and section 7a, the operating instructions. No board.
- **Evidence.** SC-06 (road as the operator's own equipment) withdrawn on 26 September 2026 (review of that day,
  section 5, R5); the ADR's text could not be fetched on 27 September 2026 (UNECE answered HTTP 403 to this host).
- **Attempts.** SC-06, taken and withdrawn; one fetch of the ADR, refused.
- **Options.** (a) Desk classification from the regulations' own text: the UN number of a lithium-ion battery alone
  or in or with equipment, class 9, the special provisions for a battery above 100 Wh without a test summary, the
  prototype and low-production provisions, any private-carriage exemption, for road, air and parcel carriage
  separately; (b) UN 38.3 tests on the built pack design; (c) a dangerous-goods safety adviser's written opinion.
- **Recommended.** (a), from a copy of the ADR (and the IATA or carrier rules) filed under `v2/vendor/` with its
  SOURCES.yaml row; (c) only if (a) leaves the route open.
- **Why layer 3 closes without it.** REQ-069's requirement (no route claimed before it is established) is settled and
  checkable on the documents; the classification is a fact, not a limit, and no board depends on it.
- **Expertise, cost.** A dangerous-goods safety adviser (ADR) if needed: a short paid opinion, cost unknown here; UN
  38.3 needs built packs and a laboratory quote (weeks). Either needs the owner's spending approval.

## 2. Compute Module 5's radio approval through the kit's antenna path (CON-011, open item S-47)

- **Issue.** Whether the module's approval with Raspberry Pi's Antenna Kit holds when that kit's antenna is reached
  through board A's J_RF3, a blind-mate joint, coaxial cable and a wall gas-discharge arrestor.
- **Affects.** CON-011, NEED-16's claim, the WIFI 2.4 jack; no board changes with the answer.
- **Evidence.** CM5 datasheet section 4.1.2 (approval only with the Antenna Kit); the Antenna Kit brief; the
  generator's slot assignment (slot 1 on the jack, slots 2 and 3 dark unless the local WiFi is moved to them).
- **Options.** (a) keep the path, show it passive and measure its loss, claim nothing until the maker answers (taken,
  SC-42); (b) antenna inside the case (overrules the owner's device ruling of 6 September 2026 and weakens the link
  under the aluminium plate); (c) module radios disabled (drops a ruled function).
- **Recommended.** (a), and the owner sends the prepared question (`drafts/hc3/question-raspberry-pi-cm5-antenna.md`;
  the session contacts nobody outside).
- **Why layer 3 closes without it.** CON-011 requires a passive path and no approval claim until the answer is held;
  both are settled and checkable. The layer audit had recommended (b); it was not taken because (b) reverses an owner
  ruling, which the session may not do.
- **Expertise, cost.** Raspberry Pi's compliance contact; no cost known; lead time unknown.

## 3. Mission M1's energy: the night first, then the solar path (REQ-072, open item S-52; layer 4)

- **Issue.** M1's 72 hours in PS-IDLE-SPEC on pack and solar (the layer 2 closer's planning value, SC-21, standing in
  for the owner's own setting under D-06). Binding: the aged pack's about 108 Wh bridges 2.5 h at PS-IDLE-SPEC (3.5 h
  reduced, 4.7 to 5.0 h in the heat stage) against nights of about 7 to 16 h at 52 N, so on pack and solar alone the
  kit stops every night whatever the panel's rating. Second: about 1.0 kWh a day into the kit needs, on the reference
  day (September at Leiden, 4.0 kWh/m2 on an optimally inclined panel, PVGIS-SARAH2 2015 to 2020, SC-37), a panel of
  about 270 W, while board E's LT8705A stage and board A's front end take about 100 W. REQ-072 reads FAIL at desk.
- **Affects.** The pack (D-06's one 4S3P block), the 9 to 36 V entry, board E's solar stage (its rating, clamp D4,
  fuse F2, connector J_SOLAR) and board A's front end; REQ-016's window would be restated if the path is re-rated.
- **Evidence.** REQ-072's desk reading (bound to gen_sch_e.py and POWER-THERMAL.md; re-read on round 8's board E);
  CONOPS section 3 M1 as the layer 2 closer restated it after its Review A (finding B3).
- **Options.** (a) an overnight input on the 9 to 36 V entry (a vehicle or a second source) named as part of M1;
  (b) D-01's deferred second pack, or a larger pack (both reopen D-06, the owner's); (c) a re-rated input path of
  about 300 W, which alone does not cure the night; (d) record that prototype 1 does not meet M1, with its reason: a
  residual only the owner can accept. A shorter mission is not a remedy (the owner's prompt forbids narrowing scope to
  close an item).
- **Recommended.** Report it to the owner at the next checkpoint as a consequence of D-06 with the session's 72 hours
  (not asked); layer 4 carries it with the pack and input path, before boards A, E and P enter layout. The owner may
  set M1's duration or the pack at any time, which moves the numbers.
- **Why layer 3 closes without it.** The requirement is stated and measurable; whether the design meets it is layer
  4's. Its TEXT changes only if the owner sets another duration (the session's value is reversible by his).
- **Expertise, cost.** Power design (boards E and A); part costs of a larger stage unknown here.

## 4. The four shared elements outside NEED-03's failure set (ASM-002, open item S-36, REQ-073; layer 4)

- **Issue.** +5V_DEV and +3V3_DEV (one converter each on board A), the J_PANEL ribbon, the KSZ9897R and the kit I2C
  bus are single points of failure of the kit (SC-39 decides NEED-03's scope at layer 3 and names them); and a failed
  supervisor can hold the kit I2C bus it shares with the secure element (ZEROIZE.md R7), which REQ-073 forbids.
- **Affects.** Boards A, B and C; every public NEED-03 statement.
- **Options.** Mitigate each at layer 4 (a second converter with ORing, per-supervisor bus isolation, a second ribbon
  path) or carry it as a named single point of failure with its reason.
- **Recommended.** Isolate each supervisor's I2C from the kit bus first (it is inside NEED-03 and touches ZEROIZE); the
  other three at Review C.
- **Why layer 3 closes without it.** The scope is decided (SC-39); REQ-073 is a settled requirement whose desk reading
  is expected to find the bus open, which is a layer 4 and layer 8 finding.

## 5. A hydrogen-rated battery-bay sensor (REQ-042, open item S-48; layer 6)

- **Issue.** The SGP41's datasheet specifies VOC and NOx responses and names hydrogen only as a background gas, so the
  approved hydrogen sensing (appendix 32.54) has no specified part.
- **Options.** A hydrogen-rated MOX or catalytic sensor on board E's bay header, picked from its maker's documents; or
  Sensirion's written statement of the SGP41's hydrogen response (an outside contact: text prepared, the owner sends).
- **Why layer 3 closes without it.** REQ-042's behaviour, path and timing are settled (SC-41, SC-31); the part is
  layer 6's, and it may add a sensor to board E's bay header (a board E schematic item before its layout entry).

## 6. The grounding strategy (REQ-061, open item S-49, CFL-018; layers 4 and 5)

- **Issue.** No board declares a chassis net. With the twelve arrestors on two aluminium RF entry plates, every antenna
  lead already bonds a plate to a board's ground, so the one deliberate bond GROUNDING-AND-SHIELDS.md point 4 asks for
  is not true as drawn (the closer's correction of that page, `drafts/hc3/GROUNDING-AND-SHIELDS.patch`, records it).
- **Why the session did not rule GND-002 in this pass.** The page's own strategy no longer stands once corrected, so
  there is no recommended option to take; at least two stand, and they differ in the lightning, ESD and emissions
  paths and in what they change on boards A, B and E (the CHASSIS net, the Ethernet common node's capacitor, the RJ45
  shell, the antenna leads). That is architecture and interface work with an EMC route under D-09, not a requirement
  limit.
- **Options.** (a) Mesh bonding: the two RF entry plates, the connector plate and the stud bonded together as the
  kit's chassis, the boards joined to it through every antenna shield, and point 4's single bond replaced by that
  equipotential; (b) point 4 kept: every antenna lead DC-isolated at its plate (a DC block with an isolated outer
  conductor), so the one deliberate strap from the stud to board A is the only low-frequency bond. Each has variants.
- **Recommended.** Rule it at layer 4 before boards A, B and E enter layout, from the arrestor maker's installation
  documents and the ground-stud geometry, and record it in pcb_decisions.yaml.
- **Why layer 3 closes without it.** REQ-061 keeps its need-level limit (one stud, a named conductor from every
  arrestor body and cable shield, a measured bond resistance); the strategy is design.

## 7. What FEA-003 and FEA-004 would reopen (layer 4 feasibility)

- FEA-003 (the failover fabric) failing reopens NEED-03's scope as REQ-004, REQ-006 and SC-39 state it, and the bound
  of SC-25; ASM-001's exceptions would grow.
- FEA-004 (power and thermal) failing reopens D-11's declared values in REQ-018 and REQ-059 (SC-35), the stated hours
  of REQ-014 in any mode whose cells leave their window, and the power states REQ-072 can claim. Round 8's PWR-F16 (a
  hung controller with the push to talk held is bounded by nothing: K1, K2 and C4 are firmware) sits under it.
- Both are held open at layer 4, where the current stage's decisions depend on them (the owner's prompt, section 2);
  the registry states both exposures in the records' notes.

## 8. The kit with its own pack at D-02a's margins (CFL-017, finding BAT-F19)

- **Issue.** The cells are rated to +60 C (and stored no lower than -20 C, or 0 C on the older sheet), so the kit with
  its pack fitted cannot meet D-02a's +55 C operating margin, E5's +60 C dwell, or the +71 C and -33 C storage margins,
  since the stored kit keeps its pack (SC-19). TEST-PLAN runs those levels as stated deviations without the cells.
- **Options.** A measured pack arrangement that keeps the cells inside their limits at the margins (the bounded
  enclosure heat experiment, POWER-THERMAL section 10); cells rated beyond them, which reopens owner ruling D-06; or
  the owner's own reading of D-02a for the kit without its cells. None is the session's to take at desk: the first
  needs hardware, the other two are the owner's.
- **Why layer 3 closes without it.** D-02a's margins are stated as ruled and REQ-051 says how each runs and what its
  result may claim; the owner's own conditions say a qualification margin is not an error. What is open is a
  qualification finding about the product, kept visible as an open conflict and never reported as the kit's margin.
  If the owner reads D-02a differently, REQ-051's text changes; if a pack arrangement is pursued, that is layer 4 and
  7 work. Review B is asked to judge this item in particular.

## 9. REQ-052 against board B as generated (open item S-53, BANK-R1; layers 4 and 8)

- **Issue.** REQ-052 keeps the owner's closed-lid example (GNSS, the LoRa mesh, Iridium and APRS beacons with the SOS
  path) for the one-module heat stage, and as board B is generated no single slot carries it (Iridium and the panel
  on bank 1, hosted by slots 1 or 2; the LoRa module on slot 3's SPI; APRS on bank 3). REQ-052 reads FAIL at desk.
- **Options.** BANK-R1 (SC-34 on main): exchange two pairs of hub ports on board B so slot 3 carries the set, no part
  added (the layer 2 closer's `drafts/gen_sch_b.BANK-R1.patch`, for board B's owner); its fallback exchange; or the
  owner rules the trade between his example and IOHA section 8's rule if neither exchange holds.
- **Why layer 3 closes without it.** The requirement is kept as the owner set it and reads FAIL on the generated board;
  the remedy is a board B schematic change before its layout entry (layer 8), and the enclosure's part is FEA-004's.

## 10. The cold warm-up's bound (open item S-54; layers 4 and 6)

- **Issue.** Below 0 C inside air the WiFi link cards and the SDR wait for the kit's cold warm-up, which reaches 0 C at
  -20 C ambient only up to about 3.6 W/K of enclosure conductance, lid open with fans; above it the kit-to-kit link, a
  critical peripheral, is lost at -20 C and TEST-PLAN E4-O fails.
- **Options.** An extended-grade link card and SDR (layer 6); the empty-case heat-balance test (T-H1) to measure the
  conductance. The envelope is not narrowed.
- **Why layer 3 closes without it.** REQ-024 states the envelope and the carve-out as settled; whether the design holds
  at the bound is a feasibility question decided before board B's layout entry where a socket or supply changes.

## 11. The battery-bay SGP41 at the hot end (open item S-55; layer 6, under FEA-004)

- **Issue.** Board E's U17 is rated to +55 C; the worst inside air is 60.6 C lid closed as board B is generated (62.1 C
  after BANK-R1), which `part_temps.py` reports once the layer 2 closer's patch to it lands.
- **Options.** Another part, a placement out of the hottest air, or a stated carve-out, picked at layer 6.
- **Why layer 3 closes without it.** REQ-052's acceptance already fails any part outside its published range; the pick
  is a component decision.

## 12. The owner's reserved value M1 (context for item 3)

- D-06 reserved the mission duration to the owner (L-02); the standing rule of 26 September 2026 forbids asking, so
  the layer 2 closer set 72 hours (SC-21) and closed L-02 by it. The owner may replace it at any time; no board depends
  on the value except through item 3.

## 13. The hot stop's path: HOT-R1 on boards A and E (REQ-077, open item S-55 here and S-57 on main a8652172; layers 5 and 8)

- **Issue.** Past the heat stage the kit acts on the pack's measured cell temperature (the hot stop, CONOPS section 4c,
  REQ-077). The gauge is read by board E's sensor controller only; as generated its only link to the panel controller,
  which owns the slot enables, the switched loads and PI_KILL, is USB through a compute module's bridge, which the heat
  stage as board B is generated does not host and which the stop's own first step removes.
- **Affects.** REQ-077 (FAIL on the generated boards until drawn), boards A and E, the dock contract IF-AE-DOCK's pin 12,
  the sensor controller's and the panel controller's firmware contracts (PANEL.md).
- **Evidence.** `gen_sch_e.py` at a8652172: J_BLK pin 12 (BLK_SPARE) reaches only TP7 (lines 562, 693); U10's GPIO19 (pin
  30) not connected (line 581); `gen_sch_a.py`: J_DOCK pin 12 is DOCK_SPARE (line 226) on U27 pin 18 (line 1262), whose
  EXP_INT (R110, line 1267) is the panel controller's interrupt; `gen_sch_c.py` line 127 (U3 GPIO24 EXP_INT, GPIO13 to 15
  SLOT_EN, GPIO19 PI_KILL).
- **Attempts.** The interrupted second pass proposed a stand-in on board B's TMP117 where the cell readings do not reach
  a module; it is kept only as the fallback when the sensor controller is lost, because the finding asks for the cells'
  own temperature on every input state.
- **Options.** (a) HOT-R1 as taken (SC-50 on main): GPIO19 through an open-drain 2N7002 on board E, a 10 k pull-up on
  board A, four line states; (b) a USB-only path, keeping a module that hosts both controllers' banks running in the
  heat stage (not available as generated; after BANK-R1 slot 3 would host both, but H1 still stops it); (c) a new kit-bus
  device on board E the panel controller polls (a part and a bus branch through the dock, which has no spare pair).
- **Recommended.** (a): no new part number and no new contact; decided with the board A and E regenerations.
- **Expertise or equipment.** None beyond the board owners; bench check in `TEST-PLAN.md` E3-H.
- **Cost and lead time.** One transistor and two resistors per kit; the next regeneration of boards A and E, before their
  layout entry.
- **Why layer 3 closes without it.** The requirement, its desk and bench acceptance and its verification stage are
  settled; what is open is the netlist change that meets it, which reads FAIL until drawn.

## 14. A non-destructive hardware stage behind the hot stop (open item S-56 here and S-58 on main; the D-09 review)

- **Issue.** The hot stop is firmware in two controllers; the hardware behind it on an input is destructive (board P's
  second level from 62.7 C blows F2; the gauge's SOT from 64.2 C and the PTC are permanent failures).
- **Affects.** REQ-077, REQ-044, REQ-046; boards A, E and P; Q-P15 of the battery packet.
- **Evidence.** `review-packets/battery/THERMAL-COORDINATION.md` sections 4 (L8 to L12), 7 (the sensor controller down)
  and 8 (the hold that would enforce 60 C in hardware pulls the pack's FETs, which removes no heat on an input).
- **Attempts.** None drawn; the packet's section 8 decided not to add its hold now and put it to the reviewer.
- **Options.** (a) none (firmware stop, destructive backstops, TI's own layering); (b) the packet's hold on board P
  alone; (c) a comparator on its own thermistor on the hottest cell, at most 57.5 C with its tolerance and 5 K of
  hysteresis, taking board A's KILL low without firmware (a second dock contact, or a hardware decode of HOT-R1's
  held-low state on board A).
- **Recommended.** (c), put to the D-09 battery-and-protection reviewer with Q-P15; the session keeps (a) with HOT-R1
  until then.
- **Expertise or equipment.** Battery protection and functional safety (the D-09 reviewer); the bench readings P14 and
  E3-H.
- **Cost and lead time.** A comparator, a reference, a thermistor and a transistor per kit (no part filed: TBD); the
  review's lead time (D-09's quote, the owner's money); decided before the layout entry of boards A, E and P.
- **Why layer 3 closes without it.** The requirement (act before idle cells pass +60 C) is set and measurable; whether a
  second, firmware-free means is required is a protection-architecture judgement for a qualification route this layer
  does not own, recorded with its options.

## 15. Whether the hot stop fires inside the envelope (FEA-004; layer 4)

- **Issue.** On the model's figures the hot stop's first step acts, at the independent bound's worst corner, from +33.2
  to +38.6 C ambient (lid closed and open, on the pack and on an input, both heat-stage configurations), and on appendix
  32.53's conductance not below +40.3 C (`records/hc2/hotstop_bounds.out`). Where it fires at +40 C the kit runs no
  module, so REQ-052's stage criteria and REQ-024's use at +40 C are not met there, on any supply; the cells stay inside
  +60 C.
- **Affects.** REQ-052, REQ-024, CON-012, FEA-004's reopen list; the pack pocket's thermal path and the placement freeze.
- **Evidence.** `records/hc2/pwr_red2.out` (the rises) and `hotstop_bounds.out`; the enclosure conductance is unmeasured.
- **Attempts.** None; it is a measurement.
- **Options.** Measure (T-H1), then, if it fires inside the envelope: a better thermal path for the pack pocket and the
  plate, or a lower-heat heat stage; lowering the envelope is not an option taken or offered.
- **Recommended.** T-H1 before the placement freeze of the pack and the PA flange site (FEA-004's fabrication-release
  stage).
- **Expertise or equipment.** The empty-case heat-balance rig of `TEST-PLAN.md` T-H1 (a current-moulding Peli 1450, the
  1450PF frame, a plate blank, resistive loads, thermocouples); its purchase is the owner's to authorise.
- **Cost and lead time.** As T-H1 (`reviews/READY-TO-ACT.md` section 5); weeks, on the case's delivery.
- **Why layer 3 closes without it.** The requirement texts are settled and a FAIL at +40 C would be recorded, not waived;
  what the measurement decides is a design outcome (layer 4), and FEA-004 names what it would reopen.

