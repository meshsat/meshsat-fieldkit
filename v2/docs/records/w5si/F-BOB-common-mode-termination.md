# Finding F-BOB: board B's BOB is a common-mode termination, no signal class asks the right question of it, and a class is proposed

Stream w5si, second pass, 27 September 2026 (MESHSAT-1357, pre-PCB layers 8 and 9). For the integrator. Prototype
design work: nothing has been built or measured. This page proposes a class; it changes no tool and no rule. It
answers the third blocking item of the independent check (AI review) of the first pass.

## 1. What BOB is

Board B's net BOB is the common node of the line-side termination of the wall Ethernet port, the one known as the Bob
Smith termination. On the committed netlist (`pcb-b-compute-b19/out/pcb-b-compute.net`) and in `gen_sch_b.py`, read
twice: at `c23c5e76`, where this finding was written, the netlist was sha256/16 `8b78c59754a6a0c7` and the three calls
that name the net stood on line 1151; on the set 6 integration line (`85ad1193`, read 28 September 2026 by stream
w5si2) the netlist is `028997a6c5e8810f` and the calls stand on line 1191. The facts are the same on both (the net
carries R9 pin 2, R10 pin 2 and C33 pin 1; 75 ohm, 75 ohm, 1 nF 2 kV). A line number and a digest are pointers into
one revision: `apply/apply_decisions_w5si.py` derives both from the tree it runs on and asserts the facts.

```
T1 pin 18 (MCT3, the cable-side centre tap of pair C) -- R9, 75 ohm --+
T1 pin 15 (MCT4, the cable-side centre tap of pair D) -- R10, 75 ohm --+-- BOB -- C33, 1 nF 2 kV -- GND
```

Three parts are on the net (R9, R10, C33) and no IC. T1 is the Pulse H5007NL magnetics, whose barrier is built for
1500 V rms (its datasheet's Hipot column). The job of the node is to carry the cable's common-mode current to the
enclosure, so that it does not radiate from the cable: its return path IS its function.

`boards/b.json` declares it `CLOCKED_DIGITAL`, "the break-before-make timing node of the same logic". That basis
describes the BBM* nets. The first pass of this stream saw that, and then moved BOB to `LOW_SPEED_OR_DC`
(W5SI-D2). The identification was right and the class was wrong, as the check found.

## 2. Why none of the four classes fits

`signal_class.py` holds four classes, and each asks one question of a return path.

| Class | Its question (`QUESTION`) | What it does to BOB |
|---|---|---|
| CONTROLLED_IMPEDANCE | ADJACENT, 10 mm or 5 percent | BOB has no impedance target |
| HIGH_SPEED_DIGITAL | ADJACENT, 10 mm or 5 percent | asks for a filled reference on the neighbouring layer along the net |
| CLOCKED_DIGITAL | ADJACENT, 30 mm or 15 percent | the same question, looser |
| LOW_SPEED_OR_DC | EXISTS | "There is no edge to speak of". RET-001 (`intent_checks.py`) asks it only whether a reference exists anywhere under it, and `return_via.py` line 177 (RET-004) and `ref_change.py` line 127 (RET-003) SKIP the class |

- **LOW_SPEED_OR_DC hides the net.** It takes the one node whose purpose is a return current out of RET-003 and
  RET-004, on the ground that it has no edge. It carries whatever the cable brings.
- **The three judged classes ask for the opposite of what the maker asks.** They want a filled reference plane next to
  the net. Microchip's hardware design checklist for this switch family (DS00004151A, section 6.5, p. 12) says: "The
  signal ground should extend only to the edge of the magnetics, and there should be no signal ground under the
  magnetics, connector, and the area in between." A layout that follows the maker leaves BOB with no adjacent
  reference, and RET-002 then flags it; a layout that satisfies RET-002 puts signal ground under the line side of an
  isolation barrier.

So the question a return rule should ask of BOB is a third one, which no class carries.

## 3. What the makers say (the evidence)

`evidence/cable-side-termination.yaml`: 9 citations of 3 held documents, each held to its page by
`tools/verify_citations.py` (0 do not hold).

| Document | Page | Words |
|---|---|---|
| Microchip DS00004151A, KSZ989x hardware design checklist | 10 | "All line-side transformer center taps should be individually terminated to a common node through" 75 ohm resistors. "The common node is then connected to chassis ground through a 1000 pF, 2 kV capacitor." |
| the same | 10 | "The metal case shield of the RJ45 connector is also tied to chassis ground." |
| the same, 6.5 Chassis Ground | 12 | "The signal ground should extend only to the edge of the magnetics, and there should be no signal ground under the magnetics, connector, and the area in between." |
| the same | 12 | "If a true chassis ground is available, the connector shield and line-side termination should connect to it." and, with no chassis, to route chassis ground "with ample copper along the edge of the board to a place where it can be connected to the digital ground" |
| TI SLUSBX9I, TPS23861 (board B's PoE controller) | 91 | "The cable terminations typically consist of series resistor (usually 75 Ω) and capacitor (usually 10 nF) circuits from each data transformer center tap to a common node which is then bypassed to a chassis ground (or system earth ground) with a high-voltage capacitor (usually 1000 pF to 4700 pF at 2 kV)." |
| Pulse H5007NL | 1 | Hipot 1500 (V rms) |

IEEE 802.3's own isolation clause is not held in this tree (the registry says so under INT-003) and is not cited here.

## 4. The class proposed

Working name `CABLE_SIDE`. The name and the numbers are the integrator's and the registry writer's to rule.

**Members on board B:** BOB, and with it the rest of the same circuit: MCT3 and MCT4 (declared LOW_SPEED_OR_DC today,
"a magnetics centre tap, a DC reference node", so they are skipped by both return rules as BOB would have been), and
the cable-side pairs MDI_* (declared HIGH_SPEED_DIGITAL today, so they are asked for the adjacent reference the maker
says to keep away). The PoE centre taps POE_P and POE_DRAIN are power nets (net class HV) and outside the signal
classes.

**What the class means:** a conductor on the cable side of an isolation barrier. Its reference is the enclosure, not
the board's signal ground.

**Its question, `ISOLATED`, and the rules that would apply to it:**

| Rule | What it asks of a CABLE_SIDE net | Source | Where it would live |
|---|---|---|---|
| R1, the return | the termination's capacitor returns to the chassis copper the board declares, by a path whose length is reported | Microchip DS00004151A 6.5; GND-002's chassis statement | GND-002's written strategy (`docs/GROUNDING-AND-SHIELDS.md`), which already names "gen_sch_b.py magnetics termination" as an implementation |
| R2, the keep-out | no copper of signal ground or of a supply on any layer under the net, under the magnetics' line side, under the connector and in the area between | Microchip DS00004151A 6.5 | the return-path block of `intent_checks.py` (RET-001, RET-002), where each class's question is dispatched; it REPLACES the adjacent-reference question for the class |
| R3, the clearance | the spacing from the net's copper to every other net is the one ISO-001 resolves for the PORT's isolation voltage (the barrier's 1500 V rms, the capacitor's 2 kV), not for the 57 V the intent declares for the pairs | Pulse H5007NL; ISO-001's own sources and decision 34 | `spacing.py`, ISO-001's tool |
| R4, SI-001 | not asked for an edge: the net has no driver and no receiver. The termination's values (75 ohm, 1 nF at 2 kV) are INT-001's | the checklist, p. 10 | `edge_length.py`, as finding F-Q1 section 5 proposes for the power stages |

RET-002, RET-003 and RET-004 would leave the class out ONLY because R1 and R2 take it in. A class that only excluded
would be LOW_SPEED_OR_DC under another name.

**The numbers** (a path length for R1, a clearance for R3) are not proposed here. R3's comes from ISO-001, whose
standard (IEC 60664-1) is not in the tree and whose pollution degree is decision 34. R1 has no published figure.

## 5. What this stream does in the meantime

| Item | What is done | Why |
|---|---|---|
| BOB's class in `boards/b.json` | KEPT as committed, CLOCKED_DIGITAL. Only the basis is corrected, by `apply/apply_board_b_declarations.py`, and it says in words that the class is held until this proposal is ruled | it keeps the net judged by both return rules, so it stays visible. A flag from RET-002 on it is a screen's flag ("examined against RET-001 rather than failed outright") and sends a reader to this page |
| MCT3, MCT4, MDI_* | not touched | they are outside the blocking item; changing them is the same decision as the class, and it is the integrator's |
| SI-001 | the data file holds an interface record for BOB, CABLE-SIDE-TERMINATION: an instantaneous bound, with the two makers' sentences as its checked documents. BOB reads decided by a bound | before, it read UNDECIDED with the reason "no part on the net, or one series resistor away, drives it", which was a description of the instrument and not of the net |
| What SI-001 then says of BOB | ANSWERED, by the series-resistor screen: R9 and R10 are 75 ohm between two signal nets | the screen cannot tell a termination from a source resistor, and says so of itself. The answer is a coincidence and the record says so. No declaration is written |

Decision, `authority: SESSION` under the owner's standing rule of 26 September 2026:

- **W5SI-D2, replaced.** BOB keeps its class and gets a true basis; the class that fits is proposed and not taken.
  Why: a class is a rule's scope, and the scope of the return rules is not this stream's to narrow or to widen. Reverse:
  restore the basis.

## 6. A side finding on the same port, for board B's author

**F-BOB-2. The two powered pairs have no common-mode termination drawn.** T1's cable-side centre taps of pairs A and
B (pins 24 and 21) go to POE_P and POE_DRAIN, the PoE feed and its return, and to nothing else: no 75 ohm and no
capacitor joins them to BOB. Only pairs C and D (MCT3, MCT4) are terminated. TI's sentence for a powered port is a
series resistor AND a capacitor "from each data transformer center tap to a common node". Whether the feed's own
decoupling is an adequate common-mode termination for pairs A and B is an engineering question for board B's author
and an EMC reviewer; it is a circuit question, not an instrument defect, and nothing in this stream changes it.

**F-BOB-3, not new: the termination returns to signal ground.** C33's other plate and the RJ45's shield are on GND,
and no board declares a chassis net. Both makers return the termination to chassis ground.
`v2/docs/GROUNDING-AND-SHIELDS.md` already says so and already lists the two board B changes as owed (the 1 nF 2 kV
capacitor and the RJ45 shell moved from GND to a CHASSIS net). It is named here only so that the class's rule R1 is
read with it: R1 has nothing to land on until that net exists.

## 7. Open, with the next action

| Open item | Next action | Whose |
|---|---|---|
| The class | rule it: name, members, question, and the tools that carry R1 to R4 | the integrator, with the registry writer |
| The basis of BOB | run `apply/apply_board_b_declarations.py` after set 6 | the integrator |
| F-BOB-2 | decide the termination of pairs A and B; if added, two 75 ohm and two capacitors to BOB in `gen_sch_b.py` | board B's author |
| F-BOB-3 | the two owed board B changes of `GROUNDING-AND-SHIELDS.md` (the capacitor and the shell to a CHASSIS net) | the grounding work, already recorded |
