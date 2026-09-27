# The kit's grounding and cable-shield strategy

**Rule GND-002 (MESHSAT-862). Written 16 September 2026.** How signal ground meets the metal of the enclosure,
and what happens to every cable shield entering or leaving the kit, decided once and implemented the same way
everywhere. Nothing here has been built or measured: this is the intended design, and the measurements that
would confirm it are named at the end.

## What the kit is made of, which is what makes this decision what it is

The enclosure is a **Peli 1450, which is plastic**. There is no metal box. The metal in this kit is:

* the **3 mm aluminium face plate** that carries the panel, with board C's backer behind it on eight standoffs;
* the **aluminium connector plate** outside the back wall between the hinge fairings, carrying the six ruled
  wall items: the two MIL-DTL-38999 receptacles, the sealed RJ45, the sealed USB-C, the outside pod's M8 receptacle
  and the ground stud (the session's case choice C3, `CASE-MARGINS.md` section 4; `V2-SPEC.md` line 11 as corrected
  on 27 September 2026 routes the RF entry plates' ground leads to the stud);
* the **two aluminium RF entry plates**, one per end wall, each 6 mm thick and sealed over the wall's holes,
  carrying the **twelve gas-discharge arrestors** (PolyPhaser GTH-SFF-AL) that are the antenna bulkheads, bodies
  outside, five east and seven west at Z 59; each plate is its arrestors' common ground (case choices C2 and C4);
* the **QMX lid bracket**;
* the shells of every cable connector.

The pack is not on this list: it is one shrink-wrapped 4S3P block with no rigid enclosure (owner ruling D-06), so
its only metal is its cells, their straps and board P. **Corrected 27 September 2026 (MESHSAT-1357, layer 3
closer):** this list named nine SMA bulkhead jacks, each clamped in a plastic wall, and the battery module's own
enclosure; both were the design before the case choices of 26 September 2026 and D-06.

So there is no single conductive enclosure to bond to. Each piece of metal is an island held by plastic, and
the only thing that joins them is whatever this design says joins them. That is the whole reason this document
has to exist before the boards are ordered.

## What is built today

**Board C to the face plate.** Eight standoff screws pass through ground ring pads on the backer into the
aluminium plate (`gen_sch_c.py`, the chassis-bond comment). That is a deliberate multipoint bond of the
panel's signal ground to the plate, and it is the only metal-to-board bond in the kit.

**The Ethernet magnetics, board B.** The chip-side centre taps TCT1 to TCT4 each carry their own 100 nF to
ground and are not tied together, which is exactly what the switch vendor asks for a voltage-mode driver
(Microchip DS00004151A section 6.3). The line-side centre taps MCT3 and MCT4 go through 75 ohm resistors to a
common node, and that node carries a 1 nF 2 kV capacitor, which is the same clause's line-side termination.
MCT1 and MCT2 carry the Power over Ethernet feed instead, which is what those taps are for on a PoE port.

**And the one thing that does not match: the common node's capacitor goes to SIGNAL GROUND, and so does the
RJ45 shell.** The clause says both go to CHASSIS ground. There is no chassis net anywhere in this kit: the
string does not appear in any schematic.

**Every arrestor** grounds its body to the RF entry plate it is clamped in, and the shield of the lead inside
runs to the radio's board, where it lands on that board's ground. So every antenna shield is on signal ground by
construction, and each RF entry plate is joined to signal ground once for every antenna lead that leaves it: twelve
bonds, on the boards that carry the radios. **Finding for GND-002 (27 September 2026):** point 4 below asks for ONE
deliberate bond between the case metal and the boards; with the arrestors on metal plates that is not true as
drawn, because the antenna leads already bond the plates to the boards many times. The strategy that is ruled has to
say which of these bonds is the deliberate one, whether the plates join the connector plate and the stud (and by what
conductor), and what the leads' shields do at each end (registry open item on GND-002 and requirement REQ-061).

## The strategy, stated

1. **There is ONE ground on each board and it is signal ground.** No board splits its ground plane. A split
   plane under a signal is a return path with a detour in it, which is what rules RET-001 and RET-003 refuse.
2. **The aluminium face plate is bonded to the panel board's ground at eight points**, as built. On a plastic
   enclosure this plate is the largest conductor in the kit and the one a person touches: bonding it to signal
   ground gives an electrostatic discharge at the panel a short path to the board's ground rather than a long
   one through a switch pin.
3. **The connector plate is the kit's cable-entry reference.** Every shield of every cable that crosses the
   case wall terminates on that plate, at the connector, in a full 360 degree clamp where the connector
   provides one. This is the point of the D38999 shells and of the sealed RJ45's flange.
4. **The plate and the boards are joined at ONE point, deliberately, through a defined impedance.** This is
   the decision that is not yet built, and it is stated here so that it can be: a single bonding strap from
   the connector plate to board A's ground near the dock, plus the 1 nF 2 kV capacitor already on board B's
   common node moved from signal ground to that plate node. One point, because the case is plastic and a
   second bond would put every cable's common-mode current through the board between the two.
5. **A cable shield is never a signal return.** Every pair that leaves the kit is differential and referenced
   on its own board; the shield carries common-mode current to the plate and nothing else.
6. **The pack has no enclosure to bond** (D-06: a shrink-wrapped block); its return enters only on the dock
   block's return pins, and nothing else of the case metal may touch it. A second path would put pack current
   through a chassis bond.

## What has to change on the boards for this to be true

| change | board | why |
|---|---|---|
| a `CHASSIS` net, brought to a single bonding pad near the dock | A | there is nowhere for the strap to land today |
| the 1 nF 2 kV common-node capacitor moved from GND to CHASSIS | B | the switch vendor's clause says chassis; it says signal ground today |
| the RJ45 shell moved from GND to CHASSIS | B | the same clause, and the shell is a cable shield by definition |
| a pad for the connector-plate strap | A | point 4 has to land somewhere |

None of those is large and all of them are schematic changes rather than layout ones, but they are changes to
three boards and they touch owner decision 29's territory (the Ethernet link), so they wait on that ruling
rather than being made piecemeal.

## What would confirm any of this

Nothing in this document is measured, because nothing has been built. What would confirm it, in the order the
prototype can do it:

* continuity and bond resistance from each metal piece to the declared reference, with a four-wire meter;
* a radiated emissions pre-compliance sweep with the lid closed and every transmitter keyed in turn, which is
  the measurement that would show a shield terminated at the wrong end;
* an electrostatic discharge test at the panel, the SMA bodies and the connector plate, which is the one that
  would show whether point 2 works.

Until those exist this is an intended design, and no kit built to it may be described as meeting any emissions
or immunity standard.
