# INT-002 pre-layout assessment: board B's three transformerless module links

MESHSAT-1357, 26 September 2026. A desk review by the session, taken under the owner's standing rule of 26 September
2026. Prototype design: no board B has been fabricated, ordered, assembled or powered, and nothing below is a
measurement. This is not a qualified engineer's review and it is not a physical test. It establishes whether the
proposed coupling is defensible to lay out; it does not establish that the links work. That half is rule INT-003, the
bench link test at the PROTOTYPE phase.

Why this page exists: the review of the 22:35 progress report (`v2/docs/reviews/2026-09-26-second-checkpoint-review.md`,
finding A) found INT-002 classified as a schematic gate while expected to close through a test on the first built
board B, which made it a circular gate on board B's layout entry. It asked for "a defensible pre-layout assessment of the
proposed Ethernet connection" separate from "its later physical verification", and warned that "moving the test to a
later phase does not, by itself, establish that the proposed circuit is viable". This page is the first half. Rule
INT-002 is verified by it (`pcb_rules_coverage.yaml`, pinned by content and bound to the nets it read); INT-003 is the
second half and stays open until the bench.

## 1. What was read

| Document | Identity | What it says about this link |
|---|---|---|
| Microchip KSZ989x/KSZ956x/KSZ9477 hardware design checklist | DS00004151A (2021), `v2/vendor/cluster/ksz989x-hw-design-checklist.pdf`, sha256/16 2a9d80931a0bed4b | section 6.6 permits the topology (quoted in section 3); its checklist row for 6.6 names the question the other end must answer |
| Microchip KSZ9897R data sheet | DS00002330E (2022), `v2/vendor/cluster/ksz9897.pdf`, sha256/16 02aab4c6a8065c49 | section 7.2: the switch's PHY ports use voltage-mode transmit drivers with on-chip terminations |
| Raspberry Pi Compute Module 5 datasheet | Release 3, build date 08/06/2026, `v2/vendor/cm5/cm5-datasheet.pdf`, sha256/16 80070fefd8db6e8a | section 2.2 names the PHY; 2.2.1 and Table 4 describe one topology, a 1:1 MagJack; it neither permits nor forbids capacitive coupling |
| Raspberry Pi CM5 IO board KiCad design | `v2/vendor/cm5/cm5io-kicad.zip`, sha256/16 48b14a6757b0edc0; `CM5IO.kicad_sch` exported to a netlist with `kicad-cli sch export netlist` (KiCad 9) on the build host, 26 September 2026 | the module maker's own reference: how the PHY side of its MagJack is biased (section 4) |
| Broadcom BCM54210PE data sheet | NOT IN THIS TREE | the PHY inside the module; Broadcom does not publish it to this project |
| Board B's netlist | `v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net`, sha256/16 669d02d07aeaae4b | the implemented coupling (section 2) |

## 2. The link as implemented

Board B's KSZ9897RTXI (U1) connects its ports 1 to 3 to the three Compute Module 5 slots (U30A, U31A, U32A, the
receptacles' pins 1 to 100). Read off the netlist, every one of the 24 conductors runs from a switch pin through ONE
series capacitor to one module pin, and nothing else is on either net:

| Slot | Switch pins (U1) | Capacitors | Module pins (receptacle A) |
|---|---|---|---|
| 1 (U30A) | 1, 2 (TXRX1P_A, TXRX1M_A); 4, 5; 6, 7; 8, 9 | C175 to C182, each `100n`, 0402 | 12, 10 (Ethernet_Pair0_P, _N); 4, 6 (Pair1); 11, 9 (Pair2); 3, 5 (Pair3) |
| 2 (U31A) | 12, 13; 15, 16; 17, 18; 20, 21 | C275 to C282, each `100n`, 0402 | 12, 10; 4, 6; 11, 9; 3, 5 |
| 3 (U32A) | 24, 25; 26, 27; 28, 29; 31, 32 | C375 to C382, each `100n`, 0402 | 12, 10; 4, 6; 11, 9; 3, 5 |

The nets are SWP1_A_P to SWP3_D_N on the switch side and ETH1_P0_P to ETH3_P3_N on the module side, 48 nets in all.
Switch pair A goes to module pair 0, B to 1, C to 2, D to 3, and the P and N legs are not crossed. No termination,
pull-up, bias or centre-tap network is fitted on either side. Port 4 of the switch goes to the wall RJ45 through the
Pulse H5007NL magnetics, which is not this link.

## 3. The switch end: permitted, in words that match the implementation

Microchip DS00004151A, section 6.6, "Capacitive Coupling Option", page 12:

> The KSZ989x/KSZ956x/KSZ9477 family switches may be used in transformer-less applications where the PHY-to-PHY
> connection is within one PCB or interconnected PCBs, and a cable is not needed.
> - A single DC blocking 0.1 μF capacitor is placed in series on each of the eight signals.
> - No additional components are needed between the KSZ989x/KSZ956x/KSZ9477 and the capacitor.
> - The other device may require termination or other circuitry. Refer to Microchip documentation for that device.
> - Another option is to achieve DC isolation using single magnetics, with or without Common-mode chokes. [...]
> - Keep auto-negotiation enabled when 1000M speed is used. [...]

The same document's checklist row for section 6.6: "Check if pull-ups are required by the link partner (needed for
Current mode line driver)."

Microchip DS00002330E, section 7.2 ("Magnetics Connection and Selection Guidelines"), opens: "A 1:1 isolation transformer
is required at the line interface." It continues: "The KSZ9897R PHY port design incorporates voltage-mode transmit drivers
and on-chip terminations. With the voltage-mode implementation, the transmit drivers supply the common-mode voltages to
the four differential pairs." The first sentence governs the line interface, the side a cable leaves the board on: the
hardware design checklist separates that side (its section 6.2, transformers at the media interface) from a PHY-to-PHY
link inside one board (its section 6.6, capacitive coupling). On board B the line interface is port 4 to the wall RJ45,
which carries the H5007NL transformer; the three module links leave no board and are not line interfaces, so 7.2's
first sentence is met where it applies and does not govern them (INFERRED from the two documents' own separation).

| Clause 6.6 item | Implementation on netlist 669d02d07aeaae4b | Reading |
|---|---|---|
| within one PCB, no cable | the three modules sit on board B's own receptacles | MATCH |
| a single 0.1 uF in series on each of the eight signals | one `100n` per conductor, 24 of 24 | MATCH |
| no additional components between the switch and the capacitor | the switch-side nets carry the switch pin and the capacitor only | MATCH |
| the other device may require termination or other circuitry | none fitted; see sections 4 and 5 | the open half |
| keep auto-negotiation enabled at 1000M | a configuration requirement, CON-005 | carried by CON-005, not by copper |

## 4. The module end: silent on the topology, and its maker's reference is consistent with it

The CM5 datasheet, section 2.2: the module "integrates a Gigabit Ethernet physical layer (PHY) device [...]: the Broadcom
BCM54210PE", with "Automatic MDI crossover, pair skew correction, and pair polarity correction". Section 2.2.1:
"Ethernet connects to CM5 using a standard 1:1 RJ45 MagJack." Table 4 describes each of the eight Ethernet pins as
"(connect to transformer or MagJack)". The routing guidance: "Route the differential Ethernet signals as 100 Ω
differential pairs [...] the signals within each pair need to be length matched [...] ideally within 0.15 mm", and
pair-to-pair matching "generally not required if differences are less than 50 mm". The datasheet describes the cable
application those pins were designed for. It neither permits nor forbids a capacitively coupled PHY-to-PHY link, and
it does not discuss one.

The module maker's own reference design answers the checklist's question by inference. In the CM5 IO board's KiCad
design (`CM5IO.kicad_sch`), the MagJack U3 (a TRJG0926HENL) has its two PHY-side centre-tap pins, 4 and 5 (`CT`), tied
together to one 100 nF capacitor, C1, to ground, and to nothing else: no supply feeds them. Its line-side taps VC1 to
VC4 go to the PoE header J9. A current-mode line driver needs its centre taps pulled to a supply, which is exactly what
the checklist row asks about; a PHY-side centre tap left on a capacitor to ground is what a voltage-mode driver, like
the switch's own (DS00002330E section 7.2), is given. So the reference design is **consistent with** a BCM54210PE that
needs no pull-ups or centre-tap bias. This is INFERRED from a reference schematic, not stated by Broadcom, and it says
nothing about the PHY's termination or common-mode range when the far end is another PHY through 100 nF.

## 5. The unresolved gap, stated

1. **The BCM54210PE's own requirements for a capacitively coupled link are not known.** Its termination, its common-mode
   output and input ranges, and whether it tolerates a link partner that sets its own common mode through 0.1 uF are in
   a datasheet Broadcom does not publish here. The switch vendor's clause names exactly this ("The other device may
   require termination or other circuitry"). No document this project holds closes it.
2. **Link margin over the routed channel is not known.** Nothing is routed on the corrected board B; the loss and
   impedance of the three links belong to the layout and its fabrication release (FEA-003, FB-FAB-7).
3. **The coupling capacitors' rating is not stated in the netlist.** They read `100n` in 0402 with no voltage or
   dielectric; the order line decides it. The DC across each capacitor is the difference of the two PHYs' common-mode
   voltages, which sit inside their own supply rails (INFERRED; the module's are not published). It is recorded so the
   BOM states a rating rather than inherits one.
4. **Auto-negotiation must stay enabled at 1000M** (clause 6.6), which is a configuration requirement of the OS image,
   the bridge and any switch configuration: CON-005.

What closes items 1 and 2 is rule INT-003: each of the three links up at 1000 Mbit/s full duplex with auto-negotiation
enabled, carrying line-rate traffic without an error, on the first built board B. A written answer from Broadcom or
Raspberry Pi would close item 1 earlier. The fallback decision 29 names is magnetics of an extended-temperature family
on the three links; its trigger is a link that does not come up at 1000M or counts an error. It is a board B respin, so
the cost of the risk is carried, not removed.

## 6. What the layout must keep

From the documents above, for board B's layout of these 48 nets: 100 ohm differential pairs; each pair's legs matched
within 0.15 mm (CM5 datasheet 2.2.1); pair-to-pair differences under 50 mm (the same); one series capacitor per
conductor with nothing between the switch pin and the capacitor (clause 6.6). The module-side reference plane and the
pairs' impedance on the chosen stack are FEA-003's (FB-FAB-7).

## 7. Result

**Defensible to lay out; not shown to work.** The implemented coupling matches the one vendor document that permits the
topology, item by item. The other end's documents neither permit nor forbid it, and its maker's own reference design
biases the PHY side the way a voltage-mode driver is biased, which is consistent with the coupling (INFERRED). The half
no document settles is stated in section 5 and allocated to INT-003 at the PROTOTYPE phase, with the fallback and its
trigger named. Nothing here weakens that test: a link that fails it takes the fallback.

## 8. What binds this assessment

- The 48 nets of section 2 on board B's netlist, by `rules_status.net_digest` (every node, and every part on them with
  its value and land): digest 262e8b039e833d02 on netlist sha256/16 669d02d07aeaae4b. A change to any of them on the
  board's current netlist takes this verification away (`verified_nets` in `pcb_rules_coverage.yaml`) until the section
  is re-read and re-pinned; a change elsewhere on board B does not.
- This page, by its sha256, pinned in `pcb_rules_coverage.yaml` (`verified_sha`).
- The documents of section 1, by the shas listed there.
