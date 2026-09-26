# Qualified review routes before costly fabrication

26 September 2026, MESHSAT-1357. Written by the session in answer to the review of 26 September 2026
(`v2/docs/reviews/2026-09-26-foundation-progress-review.md`), section 3 (last paragraph) and section 5.

**Status of the hardware:** an unbuilt prototype design. No board has been fabricated, ordered, assembled or tested.
**Status of these routes:** prepared, not started. No outside party has been contacted, nothing is contracted and no
money is committed. The session prepares packets and request texts; the owner engages reviewers, and every spend
needs a quote and the owner's approval (owner ruling D-09, `v2/docs/CONOPS.md:400`, appendix 32.366).

Every review so far of the corrected design (since 25 September 2026) was done by AI agent sessions, an author and a
separate refuting reviewer. The review of 26 September says plainly that this is not electrical sign-off. The routes
below are the qualified human reviews wanted before costly fabrication.

## Summary

| Route | What is reviewed | Approval | Packet | When |
|---|---|---|---|---|
| R-BAT | battery pack protection (board P) and its interaction with the charger and the pack input | approved in principle by D-09 (a paid review); the amount needs a quote and the owner's approval | the battery review packet `v2/docs/review-packets/battery/` (stream BAT, pending merge): request, questions, architecture, fault states; board P's review packet rebuilt at the revision that merges it | before the pack PCB is released or the pack is built |
| R-SEC | ZEROIZE and key fill | approved by D-09: the SIDN fonds voucher | board C packet ready; the key and slot lifecycle in `v2/docs/feasibility/ZEROIZE.md` (stream ZER, pending merge); board B packet after round 6 | once the lifecycle is merged, before dependent boards are final |
| R-EMC | EMC pre-compliance of the built kit | approved by D-09: once a prototype exists | the built prototype and its test plan | after the first build |
| **R-PWR** | **the corrected complex power design (board A, board E's input stage, and board B's PoE PSE that board A's 54 V stage feeds)** | **NOT approved: needs the owner's spending approval** (D-09 covered three routes, not this one) | after round 6 merges board A; board E packet ready | before board A enters layout |
| **R-HSD** | **the high-speed digital design: board B's PCIe and USB 3 fabric** | **NOT approved: needs the owner's spending approval** (D-09 covered three routes, not this one) | after round 6 merges board B and the eight-layer escape trial reports | before a board B layout is committed or any board B order |

The two new routes are recorded here as needing the owner's decision on spending, which only the owner can give. Under
the owner's standing rule of 26 September 2026 the session asks no question; the need is stated in this page and in the
next progress report. Sequencing and packet contents are engineering choices and are **taken by the session under the
owner's standing rule of 26 Sep 2026**: R-BAT first; R-PWR as soon as board A's correction merges, offered to the same
engineer as R-BAT where one covers both (the charger sits in both scopes); R-HSD as a separate specialism, once board B
has a merged correction and a measured escape result.

## How the owner would engage a reviewer (every route)

1. **Choose a provider type** from the route's list. Types, not names: this page names no firm or person and none
   has been approached. (The battery review packet's own request, which R-BAT uses, carries a shortlist of three
   firms read from their public pages, also not contacted; choosing among them is the owner's.)
2. **Send the route's request text** (below each route; for R-BAT, the one in the battery packet's
   `REVIEW-REQUEST.md`) with the link to the packet folder at the commit that adds it. The design is public under CERN-OHL-S-2.0 on the GitHub mirror, so no NDA is needed, except for R-SEC's
   secure-element datasheet, which Microchip releases under its own NDA.
3. **Ask for a quote** stating hours, the deliverable (written findings against the named packet revision, each with
   the file and the reason) and the date. D-09 requires a quote and the owner's approval before any spend beyond the
   SIDN voucher; for R-PWR and R-HSD the approval is also the decision to do the review at all.
4. **Tell the reviewer** that the design and all its reviews so far are the work of AI agent sessions, so that nothing
   in the packet is taken as a human engineer's sign-off. How and when this is said to a reviewer the owner already
   works with is the owner's call: the record for one of the mid-September reviewers is to lead with the findings, not
   the method.
5. **Record the findings verbatim** under `v2/docs/reviews/`, as the review of 26 September was. Each finding gets an
   ID and enters the author and refuting-reviewer loop; a qualified reviewer's finding is closed only on fresh evidence,
   never by an agent's agreement.

Provider types common to several routes:

- an independent consulting engineer (self-employed) with the route's specialism;
- an electronics design-services firm that sells design reviews;
- the outside reviewers who read earlier board generations in mid-September (the appendix records their fixes); the
  owner may ask whether they are willing and qualified for a route, and names are not recorded here;
- a university or applied-research group in the field (slower, independent);
- the part makers' application support, for questions about their own parts (free and public, for example the TI E2E
  forum already cited in `v2/vendor/SOURCES.yaml`); a complement to a design review, never a substitute.

## R-BAT: battery pack protection (approved in principle, D-09)

**Why.** Review section 2: a documented protection architecture and a qualified review of the actual schematic and BOM
before pack PCB release, including fuse actuation and interruption, prospective fault current, FET and gate behaviour,
temperature sensing, the commissioning jumper and the charger interaction, and the charger with its controller crashed
reviewed as a state sequence.

**One request, kept in one place.** The request text, the questions for the reviewer and for the part makers, the
protection architecture, the fault-state tables and the candidate circuit are the battery review stream's packet,
`v2/docs/review-packets/battery/` (start at `REVIEW-REQUEST.md`; pending merge when this page was written). This page
keeps no second request text and no second question list, so the two cannot disagree. What this page adds is the route
itself, beside the others, and the check below that the packet covers what the review asked.

**Reviewer.** An electronics engineer with lithium-ion pack protection experience: fuel gauges with primary protection,
second-level protectors, chemical fuses, pack FETs, and ideally the pack safety standards (IEC 62133-2, UN 38.3).
Provider types: the common list, plus battery-pack design houses and battery test laboratories that offer design review
ahead of testing (`REVIEW-REQUEST.md` section 5 there names three from their public pages; none has been contacted).

**Which circuit the reviewer gets.** Revision-bound, so the statements stay true after either merge:
- At `1f614233`, board P's U2 (the BQ7720700 second level) has its TS pin held by a fixed 10k (`gen_sch_p.py:385` value
  text and `:387`, R33), so the second level has no over-temperature function. `v2/release/review-packets/P-P4-1f614233/`
  is the record of that revision and stays as it is.
- The battery review stream's candidate restores the second level's over-temperature trip with its own NTC on a socket
  J_TS2 behind a series and shunt resistor network (`SECONDARY-OT-DECISION.md` in the battery packet). The reviewer is
  sent the circuit at the revision that merges it: the battery packet's `candidate/` files, and board P's review packet
  built by `review_packet.py` at that revision and compared with `1f614233` (see `v2/release/review-packets/README.md`,
  "Boards not here yet"). A packet at `1f614233` is not sent for this review.

**Coverage check of the review's section 2** (question IDs are the battery packet's own, as read in the stream's worktree on 26 September 2026; the integrator re-reads them at merge):

| The review asks for | Where the battery packet answers or asks it |
|---|---|
| a documented protection architecture: exact cells, primary and secondary independence, sensor faults, operating states, loss of the primary | `PROTECTION-ARCHITECTURE.md`; questions Q-P0, Q-P0b, Q-P5 |
| the secondary temperature decision | `SECONDARY-OT-DECISION.md`; Q-P7, Q-P13 |
| the fuse's environmental entries for the assembled pack, actuation and interruption, prospective fault current | `FUSE-INTERPRETATION.md`; Q-P6, Q-P12; Eaton questions Q-E1 to Q-E5 |
| FET and gate behaviour | `FUSE-INTERPRETATION.md` section 4; Q-P6, Q-P8 |
| the commissioning jumper | `FUSE-INTERPRETATION.md` section 5; Q-P11 |
| the charger interaction, and the charger with its controller crashed as a state sequence | `CHARGER-STATE-SEQUENCE.md`; Q-P10; TI questions Q-TI-2, Q-TI-3 |
| transport (review section 5: road transport has its own ADR rules) | outside the battery packet by its own statement (`PROTECTION-ARCHITECTURE.md`, the Transport row: UN 38.3 status and ADR rules "outside this packet", owner the systems stream); not a question for this reviewer |

**Documents filed for this route** (`v2/vendor/`, each with revision and sha256 in `SOURCES.yaml`): BQ4050 (SLUSC67B) and
its technical reference manual (SLUUAQ3A), the bq4050EVM guide (SLUUBF9), BQ7720700 (SLUSEG7D) and TI's pin failure-mode
analysis for it (SFFS317A), Eaton SCF9550 (ELX1135), the Littelfuse ITV9550 30A sheet (the alternative the battery stream
evaluated and did not fit), AO3400A, JSCJ 2N7002, the Murata PRF PTC and the PTC requirement of SLUUAV7C 4.5,
CSD17570Q5B, PESD5V0S1BA, the Samsung INR18650-35E cell sheets, and the JST PH and XH catalogues. The pack input path is
in `v2/release/review-packets/E-E17-1f614233/`.

## R-SEC: ZEROIZE and key fill (approved, D-09: the SIDN voucher)

**Why.** Review section 3: ZEROIZE is part of prototype 1's acceptance core, and its feasibility with the actual
ATECC608B configuration is open. Owner rulings D-03.1 to D-03.3 (crypto-erase through the secure element; the covered
toggle held 5 s is the only trigger; level-sensitive across power loss) and decision 30.

**Reviewer.** A hardware security engineer with secure elements, key management and crypto-erase experience. Provider:
the review time the SIDN fonds voucher buys, which D-09 assigns to this review.

**Packet.**
- Ready: `v2/release/review-packets/C-C24-1f614233/`: the toggle's local sense `ZEROIZE_SW`, read by the panel
  controller at boot, and the buffer U12 that exports it (the boot-read notes are in the generator at the U3 statement,
  `gen_sch_c.py`), and `v2/docs/PANEL.md` section 6 (the hardware lines that work with the controller dead).
- The key and slot lifecycle the review asks for (slot map, permissions, lock state, provisioning, trigger persistence,
  interrupted power) is the ZEROIZE stream's `v2/docs/feasibility/ZEROIZE.md` (pending merge when this page was
  written), a desk result with its development-device experiment still to run. Owed before sending: that page merged,
  and board B's packet (the secure element sits on board B) after round 6 merges.
- Owed and outside the session's reach: Microchip's full ATECC608B datasheet, released under NDA; only the summary
  sheet is held (`SOURCES.yaml`, entry `secure-element`). The owner requests it, or the reviewer uses their own access,
  or the lifecycle is shown on a development device; TPM 2.0 is the fallback D-03.1 names.

**Questions.** Can the ATECC608B's slot configuration destroy the wrapping key in the way D-03.1 needs, and what lock
state does that require? Is the level-sensitive trigger with a "wipe pending" record robust to power loss at every step?
Is key fill over the sealed console port with a signed procedure sound? What does the accepted residual risk (drive
unlock at boot depends on the secure element, the panel and the kit I2C bus) expose?

**Request text (for the owner to send through the voucher):**

> MeshSat is an open-hardware field communications kit (prototype design, nothing built). Its ZEROIZE function is meant
> to crypto-erase stored keys by destroying a wrapping key held in a Microchip ATECC608B, triggered by a covered toggle
> held five seconds and completed after a power loss. The design and its reviews so far are the work of AI agent
> sessions. We ask for a security review of the key and slot lifecycle, the trigger and interrupted-power behaviour,
> and the key-fill procedure; the packet is at [link].

## R-EMC: EMC pre-compliance (approved, D-09: once a prototype exists)

**Why.** Owner ruling D-04 (`v2/docs/CONOPS.md:395`): no CE or RED marking and no EMC claim for the prototype, so
every MIL-STD-461 run of the test plan is characterisation (`v2/docs/V2-SPEC.md:70`, `v2/docs/TEST-PLAN.md`). A pre-compliance session finds the problems a
later formal test would.

**Reviewer.** An EMC test laboratory with a pre-compliance offer (conducted emissions on the power leads, a radiated
scan, and susceptibility where it matters to the transmitters). Provider types: accredited EMC labs and pre-compliance
rental facilities.

**Packet.** The built prototype, `v2/docs/TEST-PLAN.md`, `v2/docs/GROUNDING-AND-SHIELDS.md`, and the board packets at
the built revision. Nothing is owed from the session until a prototype exists.

**Request text:** written when a build date exists; nothing to send now.

## R-PWR: the corrected complex power design (NEW, needs the owner's spending approval)

**Why.** Review section 3: "it leaves the corrected complex power and high-speed digital design without a named
qualified electronics review. Prepare those packets and identify a review route before costly fabrication." Board A
is the kit's power tree. Its committed netlist at `1f614233` (`v2/ecad/pcb-a-power-a23/out/pcb-a-power.net`, read
26 September 2026) carries the BQ25731 charger; five LM5176 buck-boost stages (VBUS20 from VIN_RAW, PD_VPWR, +54V_POE,
+13V8_PA, +12V_HF); a TPS25740A USB-C PD source; three TPS259631 eFuses; four AP64500 bucks and a TPS62933. The +54V_POE
stage is a 54 V boost that feeds the TPS23861 PoE PSE on board B (`gen_sch_a.py:452` at `1f614233`: "LM5176 in boost from
VBAT to 54 V at 0.6 A for the TPS23861 PSE on B16"); the PSE itself is on board B's netlist
(`v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net`, TPS23861PWR), so board B's packet joins this route for the PSE and
its port. Board A's corrections are round 6 candidates; commit `faf8c981` records board A as held on "VBUS20 ripple and
front-end inrush".

**Reviewer.** A power-electronics design engineer experienced in four-switch buck-boost controllers (the LM5176
class), NVDC battery chargers, eFuses and hot-swap front ends, PoE PSE and USB-C PD source stages: someone who checks
compensation, inrush, bulk-capacitor ripple current, gate drive and bootstrap supply, and the rating of every control
pin against its absolute maximum. Provider types: the common list.

**Working pages from the parallel streams** (pending merge when this page was written; the reviewer gets them at the
revision that merges them): `v2/docs/feasibility/POWER-THERMAL.md` (the power and thermal bounds, PROVISIONAL) and
`v2/docs/feasibility/DECOUPLING.md` (decision 42, which rule governs decoupling placement part by part).

**Packet.**
- Ready: `v2/release/review-packets/E-E17-1f614233/` (the input stage board A is fed from: the LM74700-Q1 ideal diode,
  the LM5069 hot-swap limiting at 4.85 to 6.15 A, the SRF1260-1R5Y common-mode choke and the SMCJ40CA inlet clamp).
- Built when round 6 merges board A: board A's packet (`A-<phase>-<revision>`, compared with `1f614233`) with the same
  tool, and board B's packet for the PoE PSE and its port. Documents already filed: LM5176 (SNVSAI1D), BQ25731 (SLUSE66A), TPS2596x (SLVSET8A, the TPS259631 eFuse),
  TPS62933, AP64500, LTC2954 (2954fb, whose order table lists the industrial grade), CSD18510Q5B, Coilcraft XAL1010,
  Panasonic ZK, Vishay WSL, BAT46W, TPD2E2U06-Q1, SN74LVC1G00.
- Owed: `SOURCES.yaml` entries for board A's other regulators (its `owed` list) and the per-stage calculations
  (compensation, ripple current per bulk capacitor, inrush).
- Pending merge, not owed: the charger with its controller crashed, as a state sequence, is the battery packet's
  `v2/docs/review-packets/battery/CHARGER-STATE-SEQUENCE.md` (its `REVIEW-REQUEST.md` question 14, Q-P10, and the
  questions prepared for TI, Q-TI-2 and Q-TI-3). It is written against both board A as committed and the round 6
  candidate, so the R-PWR reviewer reads it for question 2 below at the revision that merges it.

**Questions.**
1. The two items round 6 holds board A on: the ripple on VBUS20 and the front-end inrush, the latter against board
   E's hot-swap current limit (4.85 to 6.15 A, board E's packet). Are the corrections sound?
2. The charger topology: where the kit's loads sit relative to the charge-current sense resistor, and whether the
   charge loop can tell load current from pack current.
3. Each buck-boost stage: bootstrap supply, gate-drive margin, compensation and the FETs' gate charge against the
   controller's VCC capability.
4. Every control and enable pin against its absolute maximum across the pack's range, from 16.8 V at full charge
   (4.2 V per cell; 17.3 V if a charger fault runs the cells to the second level's 4.325 V over-voltage trip) down to 9.0 V, where the second level trips on under-voltage (BQ7720700 UVP 2.25 V per cell,
   SLUSEG7D device comparison table; the gauge's own CUV is 2.50 V per cell, 10.0 V, in the battery packet's
   `PRIMARY-CONFIGURATION.md`), and, for the pins on VIN_RAW, across the 9 to 36 V bus that board E clamps with an
   SMCJ40A (40 V standoff).
5. The heater mat drive and the eFuse settings against the loads they protect.
6. The VBAT path's current capacity at the ruled stackup and copper weight.
7. Decoupling at the fine-pitch parts (decision 42; review section 4): is the placement rule the DECOUPLING page takes
   for each part the right one, and what placement would you accept?
8. The PoE path: board A's 54 V boost stage and board B's TPS23861 PSE, its port protection and the power it may
   draw from the pack.

**Request text (for the owner to send once the spend is approved):**

> MeshSat is an open-hardware field kit (CERN-OHL-S-2.0); its power board is an unbuilt prototype design: a 4S Li-ion
> node with a TI BQ25731 NVDC charger, five LM5176 four-switch buck-boost stages (one of them a 54 V boost for the PoE
> controller on the compute board), eFuses and a USB-C PD source, fed through a hot-swap front end on a second board. The design and its reviews so far are the work of AI
> agent sessions, and a first review found real defects. We want a qualified power-electronics engineer to review the
> corrected schematic before layout and fabrication. The packet (schematic PDF, native files, BOM with datasheets,
> changes with reasons, cross-board contracts) is at [link]. Please quote hours and a date for written findings on the
> questions listed in the packet's review route.

## R-HSD: the high-speed digital design of board B (NEW, needs the owner's spending approval)

**Why.** Review section 3: the three-slot compute failover is in prototype 1's core, and "correcting TX/RX connectivity
removes a defect but does not validate the whole fabric". Board B carries three Compute Module 5 slots, each with a
PCIe Gen 2 packet switch (PI7C9X2G404SL), a USB 3 hub (TUSB8041), SuperSpeed and USB 2 host-select switches
(TMUXHS4212, TS3USB221A), a display switch cascade (TS3DV642), an Ethernet switch (KSZ9897), and M.2 sockets for NVMe,
WiFi cards and the 5G module. The PCIe transmitter-to-transmitter wiring (W3-F01, appendix 32.366) and its companions
are corrected in round 6 candidates, not yet on main.

**Reviewer.** A high-speed digital or signal-integrity engineer with PCIe Gen 2 and USB 3 board design experience:
AC coupling, reference clock distribution and termination, lane polarity and ordering rules, the M.2 and CM5 pinouts,
controlled-impedance stackups with the fabricator, and ideally 2.5D or 3D simulation. This tree has a 2D quasi-static
field solver (`v2/ecad/tools/impedance_2d.py`) and no 3D full-wave or power-delivery simulation, and its impedance
targets are not yet confirmed by the fabricator (rule IMP-001, SOURCE_UNVERIFIED, `v2/docs/PCB-RULE-COVERAGE.md:28`).
Provider types: the common list, plus PCB design bureaus with signal-integrity tools, and the fabricator's own stackup
and impedance engineering for the stackup question alone.

**Packet.**
- Built when round 6 merges board B: board B's packet with the same tool.
- Ready now: `v2/docs/ARCH-PCB-B-IOHA.md` (section 9 PCIe, section 12 FMEA, section 13 acceptance tests, sections 15
  and 15a every peripheral traced), `v2/ecad/tools/pcb_interfaces.yaml` (each interface's own numbers with its source:
  PCIe at the CM5 90 ohm +-10 % and 0.10 mm intra-pair; PCIe at the M.2 module 85 ohm +-10 %, 0.70 mm, 200 mm maximum;
  USB 3 at the CM5 90 ohm, 0.10 mm), the fabricator stackup record
  (`v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md`, the eight-layer trial of decision 43), and the filed
  datasheets (Diodes DS40068, TI SLLSEE4, SLASEP7 with SLLA552, SCDS277, the TS3DV642, the CM5 datasheet, the Quectel
  RM520N-GL hardware design, the TE 2199119 drawing, the KSZ9897).
- The lane, pin and clock map, the contracts and the feasibility blockers the review asks for (section 3, third
  bullet) are the FAB stream's `v2/docs/feasibility/FAILOVER-FABRIC.md` (pending merge when this page was written; a
  desk review of netlists, not a reviewed map). Owed before sending: that page merged, and the eight-layer escape
  trial's result (EXPERIMENTAL under decision 43; a passing trial permits further investigation only).

**Questions.**
1. Per slot: the switch's upstream and downstream lanes, polarity and AC coupling against the CM5 and M.2 pinouts,
   after the round 6 correction.
2. The switch's reference clock: coupling and termination, and clock distribution across three slots.
3. The USB 3 path through the host-select switches and the board-to-board connectors: the loss budget for a failover
   bank, and the LimeSDR SuperSpeed pairs.
4. The module Ethernet links, capacitively coupled with no magnetics (decision 29), and the display switch cascade.
5. The stackup and impedance targets against the fabricator's records; whether 2D results are enough for Gen 2 and
   5 Gb/s at these lengths, and which simulation, if any, is proportionate before a first build.
6. The escape at the CM5's 0.4 mm receptacles on eight layers, return paths at layer changes, and decoupling at the
   fine-pitch parts (decision 42, `v2/docs/feasibility/DECOUPLING.md`).

**Request text (for the owner to send once the spend is approved):**

> MeshSat is an open-hardware field kit (CERN-OHL-S-2.0). Its compute board is an unbuilt prototype design with three
> Raspberry Pi Compute Module 5 slots, a PCIe Gen 2 packet switch and a USB 3 hub per slot, SuperSpeed host-select
> switches for failover between slots, an Ethernet switch and M.2 sockets. The design and its reviews so far are the
> work of AI agent sessions; a first review found every PCIe downstream link wired transmitter to transmitter, since
> corrected. We want a qualified high-speed digital engineer to review the corrected fabric, the interface map and the
> stackup before layout and fabrication. The packet is at [link]. Please quote hours and a date for written findings on
> the questions listed in the packet's review route.

## Sources

- The review of 26 September 2026: `v2/docs/reviews/2026-09-26-foundation-progress-review.md`, sections 2, 3 and 5.
- Owner ruling D-09: `v2/docs/CONOPS.md:400`; appendix `v2/docs/MESHSAT-709-geometry-appendix.md`, section 32.366.
- Board packets: `v2/release/review-packets/README.md`. The battery review packet: `v2/docs/review-packets/battery/`.
- Board A's and board B's power parts: their committed netlists at `1f614233` (paths above), read 26 September 2026.
- Part documents: `v2/vendor/SOURCES.yaml` (revision, URL and sha256 of each).
