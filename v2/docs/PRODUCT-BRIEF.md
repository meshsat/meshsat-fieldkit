# MeshSat field kit V2: product brief

**Status: CANDIDATE for Review A, layer 1 (defined in the last section of this brief), revised on 27 September 2026
by the layer 1 closer of the engineering handover (MESHSAT-1357) against the engineering baseline at `e3aedb25`. It
becomes BASELINED only at the commit that files a Review A record with no open blocking finding.** The first pass of
that review (`reviews/REVIEW-A-LAYER-1-2026-09-27.md`, an AI review) found two blocking items, B1 (the EMCON
statements overstated how far the design has come against `feasibility/EMCON.md` section 0a) and B2 (two lines
contradicting the face rulings), and eleven minor ones; this revision answers each. The second pass of the same record (27 September 2026, an AI
review by a session that wrote none of the pages) closed B1 and B2 and left no blocking finding; its minor findings N1
(`V2-SPEC.md` line 34, correction 27) and N2 (`BUILD.md`, a CAD file that does not exist) are corrected. Its finding I5
(layer 2's EMCON and face text in `CONOPS.md` and `PANEL.md`) is answered there since `95e078a1`. The release check
at `f2b7fa66` (`reviews/REVIEW-LAYER-1-RELEASE-2026-09-27.md`, an AI review by a reviewer who wrote none of the
pages) found three blocking items that later merges had caused: B1 (the EMCON count, the 5G module's supply removal,
the EMCON lamp and the 5G socket's land stated as before board B's and board C's round 8), B2 (the case generators
and templates stated as not carrying C1 to C6) and B3 (the night finding of mission M1, requirement REQ-072, missing
from the exclusions and the open items). This revision answers the three at desk; the brief stays a CANDIDATE until a
reviewer who wrote none of the changed lines re-checks them at one pinned commit. The second release attempt of the same day (branch `fnd/rel2`) compared the three fixes with the reviewer's exact fixes and completed B3 (this is not the re-check a fresh reviewer owes), states M1's duration as governed by the session's SC-21 with the owner's part as the requirements registry's M-02, and takes the release check's minors m1, m4, m5, m7 and m8. The second release check at `eb9f9030` (`reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md`, an AI review) closed B1 to B3 and found one blocking item, R2-B1 (the core feasibility blockers counted as six where the requirements registry holds seven, FEA-007 missing); the targeted fix of 27 September 2026 (branch `fnd/h2`) applies that record's wording (the count of seven below, FEA-007's row among the open items and the east plug layout in the D-07 row), and the brief stays a CANDIDATE until a reviewer who wrote none of those lines re-checks them. History: written
25 September 2026 as a draft for Review A of the foundation baseline; revised on 26 September 2026 with the owner's
rulings of 25 and 26 September 2026 (D-01 to D-17, listed in `CONOPS.md` section 7) and later that day for the owner's
reversal of D-08 with D-08a and the session's SC-02 (appendix 32.367); revised on 27 September 2026 for the circuit as
generated at `45bde541` (the 5G socket, EMCON), the case choices C1 to C6 of `CASE-MARGINS.md` section 4, the power
and thermal findings of `feasibility/POWER-THERMAL.md`, the dual SIM and the carried-mass limit, and the exclusions
the handover audit found missing.
Prototype design. No V2 board has been fabricated, ordered or powered, and no kit has been field
deployed. Nothing in this brief is a claim about a built product; every line states what the design is
meant to do. The concept of operations with the numbered needs is `CONOPS.md`; the requirements are the registry
`v2/ecad/tools/pcb_requirements.yaml` and its generated page `REQUIREMENTS-TRACE.md`; the parts and rulings behind
each line are in `V2-SPEC.md`, `OPERATING-ENVELOPE.md`, `PANEL.md`, `ARCH-PCB-B-IOHA.md`, `TEST-PLAN.md` and the
design record `MESHSAT-709-geometry-appendix.md` (sections 32.49 to 32.62). What the design has and has not shown
today is `CURRENT-EVIDENCE.md`, whose headline reads **"Foundations incomplete; 0 boards ready for layout; 0
physically verified."**

## How this brief answers layer 1

The owner's handover prompt of 27 September 2026 (`reviews/2026-09-27-handover-execution-prompt.md`, section 3) asks
layer 1 for a clear product purpose, users, prototype scope, exclusions and intended outcome, claims that agree with the
engineering baseline, and report and deck commitments tracked apart from the technical work.

| Layer 1 item | Where it is answered |
|---|---|
| Purpose | "The problem" below; `CONOPS.md` NEED-01 |
| Users | "Who it is for" below; `CONOPS.md` section 1 |
| Prototype scope | "What the first prototype has to show" below; `CONOPS.md` section 2a (owner ruling D-01) |
| Exclusions | "What it is not, today" below |
| Intended outcome | "What the first prototype has to show" below |
| Claims against the baseline | this brief, `README.md`, `v2/README.md`, `v2/BUILD.md` and `V2-SPEC.md`, each read against `CURRENT-EVIDENCE.md`, `CONOPS.md` sections 2a and 7, `CASE-MARGINS.md` section 4 and the pages of `feasibility/` at `e3aedb25` |
| Commitments outside the technical work | "What this brief relies on outside this repository" below |
| Open items and why the layer can close with them | the section of that name below |
| The review | "Review A, layer 1" below |

## The problem

When the internet and the cellular network are down or absent, people nearby can still talk over local
off-grid networks (Meshtastic LoRa handhelds, Zigbee and Thread devices, WiFi), but their messages cannot
leave the area. A gateway that depends on one long-range bearer fails when that bearer fails, and a gateway
that depends on one computer fails when that computer does. MeshSat's software takes a message off a local
network and routes it out over whatever long-range bearer is still up, preferring the free ones over the
metered ones. The V2 field kit is the hardware that carries that software into the field.

## Who it is for

The owner scoped the prototype on 26 September 2026 (ruling D-04): a non-commercial prototype, operated in the
Netherlands and the EU by a licensed radio amateur. No CE or RED conformity marking and no EMC claim is made for
it, and the design keeps a route to the EU market open. No target organisation is named. The roles the design
itself implies are:

| Role | What the design gives them | Where it is recorded |
|---|---|---|
| Kit operator | the face plate: a 7 inch touch monitor, an e-paper status panel, locking EMCON, SOS and ZEROIZE toggles, indicators. Every transmitter is to be configured to the operator's licence and the EU limits, with a band lock on the VHF path; the HF transmitter is to operate on the amateur bands under the owner's licence | `V2-SPEC.md` panel table; appendix 32.50 item 16a; `CONOPS.md` section 7 (D-04) |
| Second crew member | a second sealed headset jack with its own push-to-talk | appendix 32.50 item 16g |
| Local end users | their own Meshtastic, Zigbee or Thread devices and WiFi clients, and a rugged tablet (ATAK class) in the lid | appendix 32.50 item 16d; `V2-SPEC.md` bearers |
| Remote correspondents | reached over Iridium, cellular, HF (Winlink and Reticulum over the Mercury modem), VHF APRS, or a second kit over a kit-to-kit WiFi link; an SOS goes to a configured recipient list | `V2-SPEC.md` bearers table; `CONOPS.md` section 4 (SOS) |

## What the V2 kit is

A sealed Peli 1450 case with an aluminium face plate on the 1450PF frame, holding seven carrier boards (A power and
I/O, B compute and radios, C panel backer, D VHF APRS, E dock strip, E5 dock block, P pack protection) and a
4S lithium-ion pack to be built for the kit rather than bought: one 4S3P block of Samsung INR18650-35E cells, about
145 Wh, shrink-wrapped in the east pocket (owner ruling D-06 of 26 September 2026; its fit designed against
Peli's own figures, `CASE-MARGINS.md`, since the owner reversed D-08). Its main properties, as designed:

- **Several independent long-range bearers:** Iridium (RockBLOCK 9704), 5G cellular (Quectel RM520N-GL, the
  module the generator carries, on an M.2 key-B socket, TE 2199119-3, since `458b2873`, whose land carries the
  maker's two locating holes since board B's round 8 (`V2-SPEC.md` correction 28); dual SIM as two nano-SIM holders, the second behind four 0 ohm links at
  the module so that the same board also builds the eSIM-plus-nano-SIM configuration of appendix 32.50 item 12 with an
  eSIM-fitted module variant, the session's choice SC-13, under which prototype 1 is to be built with two nano-SIMs,
  a departure from the approved eSIM plus nano-SIM until that variant's order code is named; three antenna jacks,
  ANT0, ANT2 and ANT3, if the board E clamp fit is shown (the case half of the condition is laid out from Peli's
  figures), otherwise two, owner ruling D-07), HF (an assembled QRP Labs QMX), VHF APRS and voice (NiceRF SA868 with a 30 W amplifier), and kit-to-kit
  WiFi without an access point (two AsiaRF AW7915-AED cards sharing one antenna pair).
- **Local networks:** a 1 W LoRa module for Meshtastic, Zigbee and Thread radios (two CC2652P modules),
  the compute modules' own WiFi and Bluetooth, a sealed Gigabit Ethernet port with PoE out.
- **Compute designed to survive the loss of a module:** the owner's requirement is that no single compute
  module is a single point of failure (`V2-SPEC.md` line 29). Three Raspberry Pi Compute Module 5 slots run k3s,
  and each of the three USB peripheral banks is designed to move in hardware to a neighbouring module when
  its home module is lost, under 2-of-3 voted control. Compute redundancy is not peripheral redundancy:
  two bearers have no second path and go with their module, the LoRa module (on one module's SPI) and
  cellular data (on one module's PCIe lane) (`ARCH-PCB-B-IOHA.md` section 15). Both are the named exceptions
  to that requirement for prototype 1 (`ARCH-PCB-B-IOHA.md` section 15a, `CONOPS.md` section 2a).
  The requirement's failure set is the loss of one module or one I/O supervisor; four shared elements are outside
  it and are single points of failure of the kit as designed, not claimed as covered: the `+5V_DEV` and `+3V3_DEV`
  converters on board A, the `J_PANEL` ribbon, the KSZ9897R Ethernet switch and the kit I2C bus with its one master
  (`V2-SPEC.md` correction 29; whether each is mitigated is open at the architecture layer).
- **Power:** its own pack; a 9 to 36 V vehicle and shore input (NATO 2-pin plug cable) that carries no vehicle
  surge claim and is not for 24 V military vehicle buses (owner ruling D-16); a solar input; missions longer than
  the pack rely on the vehicle or solar input (D-06), and on the pack and solar input alone the kit does not run through a night (REQ-072, "What it is not, today"). For accessories, a USB-C outlet that carries power only and
  PoE out (owner ruling D-12).
- **Emission and light discipline, as intended:** one locking EMCON toggle is to silence every transmitter through a
  hardware line that needs no software (appendix 32.50 item 3). The owner ruled what that means on 26 September 2026
  (D-05): the radios go dark, except that the VHF receiver keeps listening behind its transmit-only gate, and GNSS,
  DCF77 and the lightning sensor continue. As generated at `45bde541` the line is drawn to remove the supply of the
  SDR, the RockBLOCK, the LoRa module, both Zigbee and Thread radios, the HF unit and both WiFi link cards, to turn off
  the PA's rail and keying while the VHF exciter keeps receiving, to pull the compute modules' own WiFi and Bluetooth
  disables low, and to put the 5G module in airplane mode through its disable pin, a mode its own firmware carries out;
  since board B's round 8 (27 September 2026) it also removes the 5G module's supply by hardware at once (SD-EMC-1r8,
  `feasibility/EMCON.md` section 4b; `CONOPS.md` section 4b). The session set the latency every inhibit must meet: at
  most 1 s from the toggle for every transmitter, and 20 s for a 5G module that is running, by paths no processor or
  radio firmware can lengthen (SD-EMC-7, requirement REQ-071, `feasibility/EMCON.md` section 5a). Read transmitter by
  transmitter against that (`feasibility/EMCON.md` section 0a, sixth revision, with board B's round 8), the kit has 17
  transmitters and **none is dark end to end, at desk or on a bench**:
  - Locally, the radio's own chain closes at desk for 15 of the 17 and is open for two. The SA868 VHF exciter: its
    maker publishes no receive threshold for the PTT pin the design holds at 2.677 V or more (bench E-01). The RockBLOCK
    9704: once its supply is cut it keeps running on its own supercapacitors, about 16 J, with its ENABLE held by a
    firmware-driven expander, so the ENABLE forced low by the EMCON hardware is owed, and what the Iridium module does
    when ENABLE falls is stated in no held document (section 4.4). The 5G module's chain closes at desk since board B's
    round 8: its supply is removed at once, with RF off within about 1.2 ms plus 1.8 ms per mF of the module's own input
    capacitance, which no held document states (bench E-12), and the maker's warning that cutting a working module's
    supply can corrupt its flash accepted as a residual (section 4b).
  - End to end, 0 of 17 rows is closed: every row also waits on the items the rows share, the toggle and its conductor
    (accepted by SD-EMC-6 only with a hardware EMCON lamp on board C, drawn since board C's round 8 as `D22` with no
    processor in its path, and not yet visible, because its light-guide hole in the face plate is owed, open item
    S-44) and the EMCON line's own open items (sections 3 and 7), and no row is shown to meet the latency.

  No row has been shown on a bench; EMCON is feasibility blocker FEA-002 of the requirements registry. The one panel
  indication of EMCON that is independent of firmware is that lamp, lit while both EMCON lines read low, fed ahead of
  the panel's dimmer and dark in BLACKOUT (`PANEL.md` sections 1 and 4); the TX lamp's supply exists only while the
  panel controller drives its LED dimmer (`feasibility/EMCON.md` section 0; `PANEL.md` section 3, GPIO 8). Blackout and
  NVG panel modes darken the kit.
- **Distress, as intended:** closing the covered SOS toggle for 2 s sends a distress message with the kit's
  position over the bearers that are up, Iridium first when nothing else is, to a configured recipient list. SOS
  never transmits through EMCON: under EMCON the message is queued and the operator is told (owner ruling D-10,
  firmware only).
- **Key protection, as intended:** encrypted drives whose keys are wrapped by two key-encryption keys that only the
  secure element holds, both needed to unlock a drive (the two-key scheme is the session's, SC-08, under D-03's crypto-erase); holding the covered ZEROIZE toggle for 5 s, the only trigger,
  destroys both (a crypto-erase, owner ruling D-03 of 26 September 2026, `CONOPS.md` section 4,
  `feasibility/ZEROIZE.md` section 3); a case-open switch that logs; key fill as a signed
  procedure over the console, which is the sealed Glenair USB receptacle on the connector plate (appendix 32.50
  items 5, 6 and 16f; owner ruling D-12). Firmware integrity for the prototype is software-verified boot on the
  STM32H743 I/O supervisors, and on the compute modules if Raspberry Pi documents it; a hardware root of trust is
  required at a production trigger (owner ruling D-13). Whether the fitted secure element allows the erase as ruled
  is feasibility blocker FEA-001 (`feasibility/ZEROIZE.md`).
- **Awareness:** multi-constellation GNSS with a time pulse, a DCF77 second time source, a holdover clock,
  and a sensor suite (inside climate and seal check, floor water, gas, motion, lightning, radiation, an
  outside sensor pod).
- **Antenna entries:** twelve gas-discharge arrestors are the antenna bulkheads, five on the east wall and seven on
  the west at 59 mm above the floor, on one aluminium RF entry plate per end wall; the connector plate between the
  hinge fairings carries the shore and solar input, the USB console and host port, the Ethernet, the USB-C outlet,
  the sensor pod and the ground stud (`CASE-MARGINS.md` C2 to C4, the session's choices under the owner's standing
  rule of 26 September 2026). The twelfth bulkhead is the third 5G jack of D-07, which also waits on the board E clamp fit. The case generators carry C1 to C6
  since `c351115d`, and the current case set (CAD, drawings and 1:1 templates) is `v2/release/case-2026-09-27/`; the
  committed board files and the deliverable folders of `v2/release/revA/` predate it and still carry the earlier
  eleven coupler sites at 88 mm, which is history.
- **Carried as one closed case:** the design target, the session's choice SC-14 for requirement REQ-023, is a kit
  that weighs under 45.4 kg (100 lb) closed and latched with the pack and the lid's carried items fitted, with its
  largest dimension under 91 cm (36 in), the man-packed or man-portable row of MIL-STD-810H Method 516.8 Table
  516.8-IX, whose 26 drops from 1.22 m the owner ruled as the transit drop test E1 (D-02c). At desk the sourced mass
  floor is about 7.0 kg with the total TBD (`ARCHITECTURE.md` section 11); the table classifies by the outside of the
  item and its case, and the Peli 1450's exterior is 417.6 x 330.2 x 173.2 mm on Peli's product page, with the arrestor
  rows making the case about 478 mm long (X +-238.8, `CASE-MARGINS.md` sections 2.2 and 3.4). The kit is to be weighed
  and measured at assembly.

## What it is not, today

- Not built, not powered, not measured. Every runtime, temperature and power number is a design estimate
  or a datasheet figure until the prototype test plan (`TEST-PLAN.md`) has run.
- Not ready for layout and not ordered. No board of the set is ready for layout, and no layout of boards A, B, C, D, E
  or P carries its board's corrected schematic (board E5 has no schematic; its board file is its design): the
  deliverable folders of `v2/release/revA/boards/` predate the circuit corrections of `faf8c981`, `458b2873` and
  `d90f30e4` and every later one (`CURRENT-EVIDENCE.md`, the candidate table). The order folder is rebuilt and
  quarantined and nothing is ordered from it (owner decision 41 of 25 September 2026).
- Not accepted on every function it carries. Prototype 1 is accepted on the core D-01 names (below); the Geiger
  counter, the lightning detector, DCF77, the outside sensor pod, the camera, net audio recording, the tablet
  bracket, the NVG claim, HF and a second pack are designed and fitted where copper exists and reported NOT_YET_TESTED,
  never as a pass (`CONOPS.md` section 2a). The second pack has no location found; it is deferred, not withdrawn.
- Not rated. The case is Peli's IP67; the face is designed to an IP67-class construction and carries no
  rating until its seal test has run. No IP68 label is ever claimed.
- Not certified to any standard, and no certification is claimed. No CE or RED marking and no EMC claim is made
  for the prototype (D-04): the MIL-STD-810 and MIL-STD-461 plan is a test plan for the prototype, and its
  MIL-STD-461 runs are characterisation, not a qualification that has happened.
- No vehicle surge standard is claimed (D-16): the vehicle entry is recorded as not qualified. Not meant for
  full sun: the kit is to be operated shaded, with a lid sun shield or a tarp (D-02e). Not meant to start from a
  pack cold-soaked below about -10 C at the cells: it needs shore or vehicle power, or warming, first (D-02d).
- Not shown at the hot end of its envelope. The envelope is -20 to +40 C in use (`OPERATING-ENVELOPE.md` section 4).
  The +35 C one-module and +25 C charge hold-off restrictions the owner accepted with D-02b are proposed controls, not
  established limits: with the current heat budget even the design record's own enclosure conductance puts the charge
  hold-off for three typical modules at +19.5 to +21.6 C, and on the independent bound for the unmeasured conductance
  three typical modules at +20 C put the cells anywhere from 45 C to 81 C against their 60 C discharge limit
  (`feasibility/POWER-THERMAL.md` section 0 item 5 and section 9.3, finding PWR-F08; feasibility blocker FEA-004). The
  design takes controls driven by measured pack current and temperatures instead of the ambient figures (the thermal
  controls C1 to C4 of `feasibility/POWER-THERMAL.md` section 9.3, not the case choices C1 to C6), and an early
  heat-balance test is proposed there; until it has run the hot end is undecided.
- Two bought parts are not rated to the envelope's -20 C in use: the AsiaRF AW7915-AED WiFi
  link cards (0 to +70 C in the maker's 2023 PDF and -10 to +70 C on its current page; the maker's two documents
  disagree) and the LimeSDR Mini 2.4 (0 to +70 C in operation and in storage) (`feasibility/POWER-THERMAL.md` section
  9.4, PWR-F09). Whether they stay as carve-outs the kit warms or are replaced is open, a parts decision of the design
  sessions.
- Not a finished runtime figure. The published 8 to 9.5 hours came from a pack that no longer fits the
  case and is withdrawn. The runtime requirement is stated as battery-only hours in an idle and a typical mode
  at +20 C for an aged pack (D-06); its values are TBD and measured on the prototype. The current PROVISIONAL model
  gives an aged pack 2.5 h in the idle mode and 1.7 h in the typical mode, within bounds of 1.3 to 3.3 h and 0.9 to
  2.3 h (`feasibility/POWER-THERMAL.md` section 6, PWR-F07); `CONOPS.md` sections 4a and 6 carry the same
  PWR-F07 figures since the layer 2 merge (`95e078a1`). None of these is a claim.
- Not able to run through a night on its own pack and solar input. On the one pack of D-06 and the solar input alone
  the kit does not run through a night at 52 N in any state: the aged pack holds about 108 Wh usable, which carries
  the idle state of the runtime requirement (42.8 W) for about 2.5 h against nights of about 7 hours at midsummer and
  about 16 at midwinter, and the shortest night in the lightest state asks about 150 Wh; and the 72 hours of mission
  M1 ask for a panel of about 266 W on the design day, where the solar input takes at most about 100 W (`CONOPS.md`
  M1; requirement REQ-072, part of prototype 1's core, reads FAIL at desk; the figures are PROVISIONAL or INFERRED
  there). The routes that carry the night are an overnight input on the 9 to 36 V vehicle and shore entry, D-01's
  deferred second pack, or a larger pack, which reopens D-06; until the owner rules on the last two, running through
  a night needs that overnight input.
- No transport route is claimed for the pack: its classification, the conditions that apply to it or an applicable
  exception are to be established first (`CONOPS.md` section 7a, requirement REQ-069).
- Not advertised to its envelope. Publication, money, promotion and advertising the kit to its envelope stay with
  the owner (ruling of 21 September 2026, design appendix section 32.362, near its line 18606).

## Constraints fixed by owner rulings

The case is the Peli 1450 and never changes (appendix 32.62). There is no vent opening anywhere in the case,
plate or connector plate (32.53). The compute set is three identical CM5 slots (32.52). The owner's ruling
requires that hardware, not firmware, prevents two modules owning one peripheral (`ARCH-PCB-B-IOHA.md`
section 1). Engineering choices are taken by the design sessions and recorded with their evidence; promotion,
publication, money and advertising the kit to its envelope stay with the owner (ruling of 21 September 2026, design appendix section 32.362, near its line 18606).
Since 26 September 2026, where a ruling leaves a product or scope choice, the session takes the option the
evidence recommends and records it as its own (the owner's standing rule; the choices are listed in `CONOPS.md`
section 7a and, as SC-nn records, in the requirements registry). On the evening of 25 September 2026 the owner ruled
that the foundation documents (this brief, the concept of operations, the requirements and the decision table) are
written directly into this public repository, not into a private draft area first (registry id `public-docs`). The
decision table and conflict list behind the rulings D-01 to D-17, with the options and recommendation each question
was ruled on, are filed at `v2/docs/records/w1/` (`w1-decisions.md`, `w1-conflicts.md`).

## What the first prototype has to show

The owner ruled the prototype scope on 25 September 2026: **full design, staged acceptance.** Every ruled function
stays designed and fitted where copper exists; prototype 1 is accepted on a named core (messaging over Iridium, 5G,
LoRa and APRS; the three-slot failover fabric; pack, vehicle and solar charging; hardware EMCON; ZEROIZE of the
secure element; pack safety; service and programming access), and the rest is built where possible and reported
NOT_YET_TESTED, never as a pass (`CONOPS.md` section 2a). SOS joins the core as D-10 defines it, a choice the
session took under the owner's standing rule. The test plan's hot and cold levels beyond the envelope are
qualification margins with two pass lines: operate to specification inside the envelope, survive and recover at
the margin. Every owner question of the foundation batch is ruled except D-18, on the rating of the internal
fans, which is open and conditional: it does not arise unless no 40 mm fan of the ruled rating fits the coolers,
and if it arises the session settles it under the owner's standing rule. Where a ruling sets a threshold or names
engineering work (the D-11 key-down bound, the D-05 gap fixes, the D-07 jack count after the board E clamp fit),
the requirements that depend on it carry TBD with their effect stated until the work is done, rather than an
assumed value. Seven feasibility blockers on the core are not closed (FEA-001 ZEROIZE, FEA-002 EMCON, FEA-003 the
failover fabric, FEA-004 power and thermal, FEA-005 pack protection, FEA-006 decoupling, and FEA-007 the kit's fit in
the Peli 1450 on the case choices C1 to C6, core as a condition of every core function under the session's SC-04;
requirements registry, kind feasibility); each names the evidence that closes it and the stage at which that evidence can exist
(`EXECUTION-PLAN.md`, stage gates).

## What this brief relies on outside this repository

- **The software.** The claims about routing, SOS, device sharing across the modules and the panel's behaviour rely
  on the MeshSat Bridge (`github.com/meshsat/meshsat`) and on firmware that is specified but not written: the panel
  controller (issue MESHSAT-837), the sensor controller (MESHSAT-838) and the HAL device sharing and per-device
  services (MESHSAT-835 to 848). The issues are in the project's tracker (YouTrack project MESHSAT), which is not
  public. `PANEL.md` is the only one of those contracts this repository holds.
- **External commitments.** The project's report, presentation and event commitments are tracked in that tracker and
  are not deliverables of this layer; presentation polish does not gate this brief (owner's handover prompt, section
  3, layer 1).
- **The approved foundation plan** is a file outside the repository; `EXECUTION-PLAN.md` summarises it and carries the
  owner's seven standing conditions.

## Open items that bear on this brief, and why layer 1 can close with them open

Layer 1 decides what the kit is for, for whom, the prototype's scope and exclusions and the intended outcome. Each item
below is stated where it lives, with the reason the layer can close while it is open. This brief states every such
function or figure as a requirement or an intention and claims nothing about whether it is met, so none of the items
changes the kit's purpose, its users or the prototype's scope under either outcome; four could change a stated line,
FEA-004 an envelope line, FEA-002 the latency the session set, and REQ-072 and FEA-007 the pack line, and their rows say how that is handled. If an item closes against the design, the affected requirement is
reopened as a product question in its own layer and this brief is issued again with the change; nothing is narrowed
silently.

| Item | Where it is stated | Why layer 1 can close with it open |
|---|---|---|
| FEA-004, the hot end: the enclosure conductance is not measured, and on its independent bound the cells leave their window at +20 C with three typical modules | "What it is not, today"; `feasibility/POWER-THERMAL.md` sections 0 and 9 | The bound includes failure, so the envelope's upper limit is not claimed here, only stated as the requirement. The decision that depends on the evidence is layer 2's envelope and layer 4's thermal architecture, and the proposed heat-balance test informs them. **This is the item most likely to reopen this brief:** if the test shows that the sealed case cannot keep the cells inside their window at the envelope's top with the ruled functions, the envelope line or the thermal design changes, which is an owner-level product question under the ruling of 21 September 2026. |
| FEA-002 EMCON: 0 of 17 transmitters dark end to end; locally 15 of 17 closed at desk and two open, the SA868 (PTT threshold unpublished) and the RockBLOCK 9704 (its own stored energy, about 16 J, and an ENABLE firmware holds); the 5G module's supply removed by hardware at once since board B's round 8 (SD-EMC-1r8); the shared items, with the hardware EMCON lamp `D22` drawn on board C and its light guide in the face plate owed (S-44); no bench row | "What the V2 kit is" (emission discipline); `feasibility/EMCON.md` sections 0a, 4.4, 5a and 7; registry FEA-002, REQ-030, REQ-071 | The brief states EMCON as the owner ruled it (D-05) and the latency the session set (REQ-071), and claims neither met. Every open row has a remedy named on the board that owns it (EMCON.md section 7), and none of them changes a ruled radio, the Peli case or a board-to-board interface (the hardware lamp's remedy adds a light-guide hole to the made face plate, S-44). One bound includes failure: whether the RockBLOCK 9704 goes silent within 1 s when its ENABLE falls, with about 16 J stored on its side, is stated by no held document (section 4.4). The decision that depends on it is layer 4's feasibility and board B's circuit (layers 8 and 9), not this layer's: the kit's purpose, its users and the core (hardware EMCON in it) stand under either outcome. If no hardware path can meet a row's limit, the requirement is not lowered here: it is reopened as a product question in its own layer and this brief is issued again with the change. |
| FEA-001 ZEROIZE, FEA-003 failover fabric, FEA-005 pack protection, FEA-006 decoupling | the bullets above; registry, kind feasibility | Each is an architecture or circuit feasibility question with a design path named on its page (for ZEROIZE the SLB 9673 fallback on the same site). The functions stay defined as ruled; their feasibility is layer 4's and the circuits are layers 8 and 9's. |
| FEA-007, the kit's fit in the Peli 1450 on the case choices C1 to C6 (core under the session's SC-04): 35 of 70 case margins OPEN; M17g and M17x fail as laid out until the jumper plug is picked; the pack's rows M4a and M5 OPEN on its undesigned hold-down (S-27); the layout entry of boards A, B, D, E, E5 and P held; the mock-up BLOCKED on the owner's purchase (L-07) or his acceptance of the residual | "What the V2 kit is" (the pack in the east pocket; the antenna entries; D-07's jack count); `CASE-FIT-UNCERTAINTIES.md` sections 2, 6 and 7; registry FEA-007, L-07 and S-27 | The bounds include failure, so no fit is claimed here. Every failing branch moves a board's outline or placement, never the case (appendix 32.62), so the decision it informs is layer 7's and the boards' layout entry, and the purchase or the residual is the owner's. If the pack rows cannot be met by a board move and the hold-down, D-06 is reopened as a product question and this brief is issued again. |
| D-07's third 5G jack, waiting on the board E clamp fit (S-12) and on the east plug layout (M17g, FEA-007) | "What the V2 kit is" | Both branches (three or two jacks on ANT0, ANT2 and ANT3 or ANT0 and ANT2) are ruled; the case half is laid out, and its east plug layout under 5G MAIN, which the IRIDIUM, ANT3 and DIV cables pass, fails M17g as laid out until the jumper plug is picked (FEA-007, the row above). It changes a jack count, not the product. |
| SIM protection and the eSIM variant's order code (CFL-010, S-13) | "What the V2 kit is"; `V2-SPEC.md` correction 22 | The description is settled (SC-13) and CFL-010 is resolved on it; the TVS array is drawn on board B since its round 8 (`V2-SPEC.md` correction 28), and the variant's code is a procurement item for an eSIM build only (S-13). |
| The two parts not rated to -20 C (PWR-F09) | "What it is not, today" | A parts decision (layer 6): carve-out with warming or replacement. It does not change what the kit is for. |
| REQ-014's runtime values, measured on the prototype; L-02, the mission duration for the solar balance, which D-06 left for the owner to set later and for which the session took 72 hours as a planning value under the owner's standing rule (SC-21, which governs it under that rule, is recorded as the session's and closes L-02 in the requirements registry; the owner's own setting replaces it; `handover/ENGINEERING-QUESTIONS.md` EQ-13) | "What it is not, today"; `CONOPS.md` sections 3 (M1) and 6 | The requirement's form is ruled; the values are prototype measurements, and missions longer than the pack are stated to rely on vehicle or solar input, with the night finding in the next row. |
| REQ-072, M1's energy balance (core, FAIL at desk): on the D-06 pack and the solar input alone the kit does not run through a night at 52 N in any state, and M1's 72 hours ask about 266 W of panel where the solar input takes at most about 100 W | "What it is not, today"; `CONOPS.md` section 3 (M1); registry REQ-072, SC-21 and S-53 | The finding is allocated to layer 4 (the energy architecture: whether the input path is re-rated, S-53, before boards A, E and P enter layout) and to the owner (a larger pack reopens D-06; the second pack is D-01's deferred item; accepting the residual is his alone: the requirements registry's owner action M-02, decided before boards A, E and P enter layout). The kit's purpose, its users and the core list stand under either outcome, nothing is claimed, and this brief states the overnight input a night needs today. If the owner reopens D-06 or D-01's second pack, the pack line of "What the V2 kit is" changes and this brief is issued again. |
| D-18, the fans' rating | "What the first prototype has to show" | Conditional; settled by the session if it arises; no product change. |
| The pack's transport route (REQ-069) | "What it is not, today" | No route is claimed; establishing one is a bounded item before any carriage. |

## Review A, layer 1

**Definition, taken by the session under the owner's standing rule of 26 September 2026 (SC-16).**
`EXECUTION-PLAN.md` names Review A's content (product brief, concept of operations, modes, runtime, environment,
ZEROIZE meaning, markets) and what it gates, but no reviewer, criteria or record, so as written nobody could pass it.
For layer 1 it is:

- **An AI review, labelled as one, never a qualified review.** No qualified review is required of layer 1 by any record
  in this tree: the engineering reviews the owner approved or named (D-09 and the review routes) are for ZEROIZE and key
  fill, the battery and its protection, EMC, the power design and board B's fabric. Should an engineer's review of layer 1
  ever be required, this review does not stand in for it.
- **One fresh reviewer**: a session or person that wrote none of the pages under review and did not assemble them.
- **The pages:** this brief, `README.md`, `v2/README.md`, `v2/BUILD.md` and `V2-SPEC.md`, at one pinned commit.
- **The criteria:** the owner's handover prompt, section 3, layer 1 row, and section 2's tests: each layer 1 item is
  answered; every claim agrees with the engineering baseline (`CURRENT-EVIDENCE.md`, `CONOPS.md` sections 2a and 7,
  `V2-SPEC.md` corrections, `CASE-MARGINS.md` section 4, the pages of `feasibility/`); nothing is claimed that the
  evidence does not establish; no requirement is lowered, no function dropped and no scope narrowed; every open item
  is stated with why the layer can or cannot close without it; session choices are marked as the session's.
- **The record:** `v2/docs/reviews/REVIEW-A-LAYER-1-<date>.md`, headed "AI review (not a qualified engineering
  review)", naming the reviewer, the commit, each criterion with its finding, and each finding as blocking or minor.
  The first pass is `reviews/REVIEW-A-LAYER-1-2026-09-27.md`.
- **Closing:** blocking findings are fixed and re-checked once (SC-16's words); after two unsuccessful passes on
  the same finding the method changes (handover prompt, section 4). This brief's status becomes BASELINED at the commit
  that files a record with no open blocking finding. Layer 2's part of Review A (`CONOPS.md`, `OPERATING-ENVELOPE.md`)
  is held the same way by its own fresh reviewer.
