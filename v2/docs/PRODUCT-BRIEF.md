# MeshSat field kit V2: product brief

**Status: DRAFT for Review A of the foundation baseline (MESHSAT-1357), written 25 September 2026, revised on
26 September 2026 with the owner's rulings of 25 and 26 September 2026 (D-01 to D-17, listed in `CONOPS.md`
section 7).**
Prototype design. No V2 board has been fabricated, ordered or powered, and no kit has been field
deployed. Nothing in this brief is a claim about a built product; every line states what the design is
meant to do. The concept of operations with the numbered needs is `CONOPS.md`; the parts and rulings
behind each line are in `V2-SPEC.md`, `OPERATING-ENVELOPE.md`, `PANEL.md`, `ARCH-PCB-B-IOHA.md`,
`TEST-PLAN.md` and the design record `MESHSAT-709-geometry-appendix.md` (sections 32.49 to 32.62).

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

A sealed Peli 1450 case with an aluminium face plate, holding seven carrier boards (A power and I/O,
B compute and radios, C panel backer, D VHF APRS, E dock strip, E5 dock block, P pack protection) and a
4S lithium-ion pack to be built for the kit rather than bought: one 4S3P block of Samsung INR18650-35E cells, about
145 Wh, shrink-wrapped in the east pocket (owner ruling D-06 of 26 September 2026, subject to a measurement of
the owner's case). Its main properties, as designed:

- **Several independent long-range bearers:** Iridium (RockBLOCK 9704), 5G cellular (Quectel RM520N-GL, the
  module the generator carries; its socket as drawn has the wrong key and is being replaced by a key-B part; three
  antenna jacks, ANT0, ANT2 and ANT3, if the case measurement confirms the extra site, otherwise two, owner ruling
  D-07), HF (an assembled QRP Labs QMX), VHF APRS and voice (NiceRF SA868 with a 30 W amplifier), and kit-to-kit
  WiFi without an access point (two AsiaRF AW7915-AED cards sharing one antenna pair).
- **Local networks:** a 1 W LoRa module for Meshtastic, Zigbee and Thread radios (two CC2652P modules),
  the compute modules' own WiFi and Bluetooth, a sealed Gigabit Ethernet port with PoE out.
- **Compute designed to survive the loss of a module:** the owner's requirement is that no single compute
  module is a single point of failure (`V2-SPEC.md` line 29). Three Raspberry Pi Compute Module 5 slots run k3s,
  and each of the three USB peripheral banks is designed to move in hardware to a neighbouring module when
  its home module is lost, under 2-of-3 voted control. Compute redundancy is not peripheral redundancy:
  two bearers have no second path and go with their module, the LoRa module (on one module's SPI) and
  cellular data (on one module's PCIe lane) (`ARCH-PCB-B-IOHA.md` section 15). Both are open design gaps
  against that requirement, not accepted exceptions (`CONOPS.md` section 2a).
- **Power:** its own pack; a 9 to 36 V vehicle and shore input (NATO 2-pin plug cable) that carries no vehicle
  surge claim and is not for 24 V military vehicle buses (owner ruling D-16); a solar input; missions longer than
  the pack rely on the vehicle or solar input (D-06). For accessories, a USB-C outlet that carries power only and
  PoE out (owner ruling D-12).
- **Emission and light discipline, as intended:** one locking EMCON toggle is to silence every
  transmitter through a hardware line that needs no software (appendix 32.50 item 3). The owner ruled what that
  means on 26 September 2026 (D-05): the radios go dark, except that the VHF receiver keeps listening behind its
  transmit-only gate, and GNSS, DCF77 and the lightning sensor continue. What the line does to each radio as
  generated, and the two gaps the design still has to close (the compute modules' own radios, and the WiFi link
  cards' disable pin), are in `CONOPS.md` section 4b. Blackout and NVG panel modes darken the kit.
- **Distress, as intended:** closing the covered SOS toggle for 2 s sends a distress message with the kit's
  position over the bearers that are up, Iridium first when nothing else is, to a configured recipient list. SOS
  never transmits through EMCON: under EMCON the message is queued and the operator is told (owner ruling D-10,
  firmware only).
- **Key protection, as intended:** encrypted drives whose keys are wrapped by a key only the secure element
  holds; holding the covered ZEROIZE toggle for 5 s, the only trigger, destroys that key (a crypto-erase, owner
  ruling D-03 of 26 September 2026, `CONOPS.md` section 4); a case-open switch that logs; key fill as a signed
  procedure over the console, which is the sealed Glenair USB receptacle on the connector plate (appendix 32.50
  items 5, 6 and 16f; owner ruling D-12). Firmware integrity for the prototype is software-verified boot on the
  STM32H743 I/O supervisors, and on the compute modules if Raspberry Pi documents it; a hardware root of trust is
  required at a production trigger (owner ruling D-13).
- **Awareness:** multi-constellation GNSS with a time pulse, a DCF77 second time source, a holdover clock,
  and a sensor suite (inside climate and seal check, floor water, gas, motion, lightning, radiation, an
  outside sensor pod).

## What it is not, today

- Not built, not powered, not measured. Every runtime, temperature and power number is a design estimate
  or a datasheet figure until the prototype test plan (`TEST-PLAN.md`) has run.
- Not rated. The case is Peli's IP67; the face is designed to an IP67-class construction and carries no
  rating until its seal test has run. No IP68 label is ever claimed.
- Not certified to any standard, and no certification is claimed. No CE or RED marking and no EMC claim is made
  for the prototype (D-04): the MIL-STD-810 and MIL-STD-461 plan is a test plan for the prototype, and its
  MIL-STD-461 runs are characterisation, not a qualification that has happened.
- No vehicle surge standard is claimed (D-16): the vehicle entry is recorded as not qualified. Not meant for
  full sun: the kit is to be operated shaded, with a lid sun shield or a tarp (D-02e). Not meant to start from a
  pack cold-soaked below about -10 C at the cells: it needs shore or vehicle power, or warming, first (D-02d).
- Not a finished runtime figure. The published 8 to 9.5 hours came from a pack that no longer fits the
  case and is withdrawn. The runtime requirement is stated as battery-only hours in an idle and a typical mode
  at +20 C for an aged pack (D-06); its values stay PROVISIONAL until the prototype is measured (`CONOPS.md`
  section 6).

## Constraints fixed by owner rulings

The case is the Peli 1450 and never changes (appendix 32.62). There is no vent opening anywhere in the case,
plate or connector plate (32.53). The compute set is three identical CM5 slots (32.52). The owner's ruling
requires that hardware, not firmware, prevents two modules owning one peripheral (`ARCH-PCB-B-IOHA.md`
section 1). Engineering choices are taken by the design sessions and recorded with their evidence; promotion,
publication, money and advertising the kit to its envelope stay with the owner (ruling of 21 September 2026).
Since 26 September 2026, where a ruling leaves a product or scope choice, the session takes the option the
evidence recommends and records it as its own (the owner's standing rule; the choices are listed in `CONOPS.md`
section 7a).

## What the first prototype has to show

Review A accepts this brief, `CONOPS.md` and the operating envelope together. The owner ruled the prototype
scope on 25 September 2026: **full design, staged acceptance.** Every ruled function stays designed and fitted
where copper exists; prototype 1 is accepted on a named core (messaging over Iridium, 5G, LoRa and APRS; the
three-slot failover fabric; pack, vehicle and solar charging; hardware EMCON; ZEROIZE of the secure element;
pack safety; service and programming access), and the rest is built where possible and reported
NOT_YET_TESTED, never as a pass (`CONOPS.md` section 2a). SOS joins the core as D-10 defines it, a choice the
session took under the owner's standing rule. The test plan's hot and cold levels beyond the envelope are
qualification margins with two pass lines: operate to specification inside the envelope, survive and recover at
the margin. Every owner question of the foundation batch is ruled except D-18, on the rating of the internal
fans, which is open and conditional: it does not arise unless no 40 mm fan of the ruled rating fits the coolers,
and if it arises the session settles it under the owner's standing rule. Where a ruling sets a threshold or names
engineering work (the D-11 key-down bound, the D-05 gap fixes, the D-07 jack count after the case measurement),
the requirements that depend on it carry TBD with their effect stated until the work is done, rather than an
assumed value.
