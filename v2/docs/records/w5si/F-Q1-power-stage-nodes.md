# Finding F-Q1: the power-stage nodes are asked the wrong question by SI-001, and no rule asks the right one

Stream w5si, second pass, 27 September 2026 (MESHSAT-1357, pre-PCB layer 9). For the integrator. Prototype design work:
nothing has been built or measured. This page proposes; it changes no rule, no board table and no count. The checks
behind it are desk checks by the stream (an AI review where a second reader looked), not a qualified engineering review.

## 1. What is found

SI-001 reads 82 nets of the power stages as LAYOUT_BOUND on a bound (BOUND_DECIDES), and they hold the reading
INCONCLUSIVE on boards A, B, C and E. The readings are `readings/si001-c23c5e76.txt` and
`readings/si001-set6-73ae2f21.txt`; the count is the same on both sets of netlists.

| Board | Nets | What they are |
|---|---|---|
| A | 57 | seven LM5176 stages (FE, S2, SD, PA, HF, POE, PD): 42 gate-drive and bootstrap nets, and S2_SW1, S2_SW2, SD_SW1, SD_SW2; the BQ25731 charger: 6; two TPS62933: B33_BST, HT_BST, HT_SW; two AP64500: S1_BOOT, S3_BOOT |
| B | 14 | bootstrap nodes of six AP64500, seven TPS62933 and one AP63203 |
| C | 1 | EPD_SW, the e-paper panel's discrete boost |
| E | 10 | the LT8705A tracker: 6; the two LM74700-Q1 gates Q1_G and Q2_G; the LM5069 gate HS_GATE; E6_BST |
| all | 82 | |

Three facts, each checked:

1. **No maker of these nine parts publishes a minimum rise or fall time for a gate driver or a switch node.** Eight
   publish no rise or fall time at all. One, the LT8705A, prints rise and fall rows, all typical (20 ns at 3300 pF,
   10 to 90 percent; 20 to 40 ns typical for its switch pins). The LM5176 says where the number comes from: "The rise
   (tr) and the fall (tf) times are based on the MOSFET data sheet information or measured in the lab." So the bound
   in `pcb_edge_rates.yaml` (POWER-STAGE-NODES, instantaneous) is the honest figure, and it will stay a bound until a
   board is measured. Evidence: `evidence/power-stage-layout-guidance.yaml`, 46 citations of 9 documents, every one
   held to its page by `tools/verify_citations.py` (0 do not hold).
2. **No registry rule states a length, a loop area or a copper area for a power stage.** `pcb_rules.yaml` holds 59
   rules. Those that touch the subject state something else: DEC-001 (the loop of a decoupling capacitor with the pin
   it serves), EMC-001 (an EMC sheet per board, no implementation), ANA-001 (the distance of a sensitive node from
   switching copper), PI-001 and PI-002 (current capacity and drop), CMP-001 (absolute maximum ratings).
3. **Which switch nodes SI-001 sees today is an accident of their net class.** Of the 38 switch nodes on the committed
   netlists (nets named `*SW*` that carry an inductor), 32 sit in a power net class (SW, HV or PWR) and are outside
   SI-001's signal set for that reason alone, without a word in any reading. Six sit in class Default and are read:
   board A's HT_SW, S2_SW1, S2_SW2, SD_SW1 and SD_SW2, and board C's EPD_SW. The same kind of node is inside or outside
   the rule by the pattern list of a layout generator.

## 2. Why SI-001 is the wrong question for these nodes

SI-001 asks whether a net behaves as a transmission line, so that its topology and termination follow from that. Its
failure modes, in the registry's words, are "Overshoot into a protection diode, double-clocking, and emissions from an
unterminated stub": each names a RECEIVER with a threshold or a clamp, or a stub.

A switch node, a gate drive and a bootstrap node have neither. What goes wrong on them is different:

- **The hot loop** (input capacitor, the two switches, the sense resistor and back). Its inductance and the switched
  current set the ringing and the overshoot at the switch node, which is a voltage stress on the FETs and the
  controller (CMP-001's question) and a magnetic source (EMC-001's).
- **The switch node's copper.** It moves through the whole input voltage at every cycle: its area is the capacitive
  source. It must also carry the inductor current (PI-001's question).
- **The gate loop** (driver, gate, source, and back to the driver's return, which is the switch node for a high-side
  FET). Its inductance with the FET's input capacitance sets gate ringing and false turn-on.
- **The gate of a hot-swap or ideal-diode controller** is driven by microamperes on the way up (LM5069: 16 uA typical)
  and pulled down hard on a fault. What the makers ask is a short trace, so that the turn-off is not delayed.

These are questions of loop inductance and node area: lumped, not distributed. For scale only, and NOT as a figure
this finding uses: at the one typical any maker prints (LT8705A, 20 ns) the length at which a gate trace would begin
to behave as a line on board E's slowest layer is 20 ns / (6 x 7.154 ps/mm) = 466 mm, against traces the makers ask
to be as short as the placement allows. A typical is not a minimum, so SI-001 does not take it (ER-D8) and neither does
this page.

## 3. What the makers' layout guidance says, per converter

Every quote below is in `evidence/power-stage-layout-guidance.yaml` with its page and the sha256/16 of the held file.
"p." is the page as pdftotext counts it, the first being 1.

| Part (where) | Document, section | Hot loop | Switch node | Gate drive | Bootstrap | A number for layout |
|---|---|---|---|---|---|---|
| LM5176 (A: seven stages) | TI SNVSAI1D, 10.1 Layout Guidelines, p. 30 | "Place the power components including the input filter capacitor CIN, the power MOSFETs QL1 and QH1, and the sense resistor RSENSE close together to minimize the loop area for input switching current in buck operation." | "Minimize the SW1 and SW2 loop areas as these are high dv/dt nodes." | "Layout the forward and return traces close together, either running side by side or on top of each other on adjacent layers to minimize the inductance of the gate drive path." | "Place the BOOT1 bootstrap capacitor close to the IC and connect directly to the BOOT1 to SW1 pins." | none |
| BQ25731 (A: U3) | TI SLUSE66A, 12.1 Table 12-1 and 12.2.2, p. 93 to 94 | "decoupling capacitors as close as possible to IC to decoupling switching loop high frequency noise." | "Capacitors SW1/2 nodes are recommended to use wide copper polygon to connect to power stage ..." | "Use wide trace for gate drive traces, minimum 15 mil trace width." | "... capacitors BST1/2 node are recommended to use at least 8mil trace to connected to IC BST1/2 pins." | gate traces at least 15 mil wide; BST traces at least 8 mil wide |
| TPS62933 (A: U12, U33; B: seven) | TI SLUSEA4D, 12.1, p. 40 | "In a buck converter, the most critical PCB feature is the loop formed by the input capacitors and power ground, as shown in Figure 12-1." | "Keep the SW trace as physically short and wide as practical to minimize radiated emissions." | integrated FETs | "Place a BST capacitor and resistor close to the BST pin and SW node. A > 10-mil width trace is recommended to reduce the parasitic inductance." | BST trace wider than 10 mil |
| AP64500 (A: U4, U6; B: six) | Diodes DS41979 Rev. 5 - 2, PCB Layout, p. 23 | "Place the input capacitors as closely across VIN and GND as possible." | "Place the inductor as close to SW as possible." | integrated FETs | the value only (100 nF), no placement | none |
| AP63203, AP63205 (B: U25; E: U12) | Diodes DS41326 Rev. 3 - 2, PCB Layout, p. 15 | "Place the VIN capacitors as close to the device as possible." | nothing in words | integrated FETs | the value only (100 nF), no placement | none |
| LT8705A (E: U5) | ADI 8705af, Circuit Board Layout Checklist, p. 35 to 36 | "The high di/dt path formed by switch M1, switch M2," "D1, RSENSE and the CIN capacitor should be compact with short leads and PC trace lengths." | "Minimize parasitic SW pin capacitance by removing" "GND and VIN copper from underneath the SW1 and SW2 regions." | "... keeping the GND, BG and SW traces short."; "Keep the high dV/dT nodes SW1, SW2, BOOST1, BOOST2," "TG1 and TG2 away from sensitive small-signal nodes." | "Connect the top driver boost capacitor, CB1, closely to" the BOOST1 and SW1 pins | none |
| LM74700-Q1 (E: U3, U4) | TI SNOSD17G, 12.1, p. 23 | not a switching stage | none | "The Gate pin of the LM74700-Q1 must be connected to the MOSFET gate with short trace. Avoid excessively thin and long trace to the Gate Drive." | none | none |
| LM5069 (E: U6) | TI SNVS452G, 11.1, p. 28 | the high-current path and its return "must be parallel and close to each other to minimize loop inductance." | none | the layout section says nothing of the GATE trace | none | none |
| the e-paper boost (C: Q6, L1, D19) | PDi EPD Driving Circuit Rev. 02 | THE NOTE HAS NO LAYOUT SECTION | | | | none |

What this table shows:

- Every maker of a switching stage asks for the same four things: a small hot loop, a small switch node, gate traces
  run short with their return, the bootstrap capacitor at the pins.
- **Nine documents give three numbers, and all three are WIDTHS** (15 mil, 8 mil, 10 mil). None gives a length, a loop
  area or a copper area.
- One maker (LT8705A) asks for the OPPOSITE of an adjacent reference under the switch node: no GND and no VIN copper
  under SW1 and SW2. A return-path rule that asked a switch node for a plane under it would ask for what the maker
  says to remove.
- Board C's boost has no layout guidance from its maker at all.

## 4. Which rule should govern these nodes

A power-stage layout rule, in the power-integrity or the EMC domain, which the registry does not hold. Its number and
its wording are the registry writer's. What it would say, proposed:

> **Requirement.** Every switching power stage is placed and routed as its controller's maker's layout guidance
> requires: the loop that carries the switched current is as small as the parts allow, the switch node's copper is no
> larger than its current needs, each gate-drive trace runs with its return, and the bootstrap capacitor sits at the
> pins. The gate of a hot-swap or ideal-diode controller is a short trace to its FET.
>
> **Acceptance, per stage.** A sheet that names the stage's hot-loop parts and reports, from the placed and routed
> board: the area enclosed by the hot loop; the copper area of each switch node and what lies under it; the length and
> the width of each gate-drive and bootstrap trace, and the layer its return runs on. Each figure is held to the
> maker's own number where the maker prints one (today three widths), and is REPORTED where the maker prints none.
>
> **What is owed to a bench, and said so (SGN-002).** The ringing and the overshoot at each switch node, measured at
> bring-up against the absolute maximum of the FET and of the controller (CMP-001). No document of this tree bounds
> them: the edge that sets them is the one no maker publishes.
>
> **Verification phase.** PLACED_BOARD for the hot loop (the placement fixes it), ROUTED_BOARD for the rest.

What this proposal does NOT do is state a limit for a loop area or a trace length. None is published, and a number
written here would be this stream's invention. Two ways to a justified limit exist, and both are work for the rule's
owner:

1. **The makers' reference layouts.** The datasheets' layout examples are drawings with no dimensions in the text.
   Where a maker has an evaluation board (the BQ25731 datasheet names one, the BQ257XXEVM, p. 93), the loop area of
   the maker's own board, read from its layout files, is a figure a maker stands behind. No such file is held, and
   whether each maker publishes one with dimensions is not checked here: finding that out is the first step.
2. **A derived bound per stage**: the loop inductance at which the overshoot reaches the absolute maximum, from the
   switched current and the current's fall time. The fall time is again a typical in every FET datasheet held, so this
   gives a MODEL, to be named one, with the bench measurement owed.

## 5. How SI-001's applicability should exclude them

Proposed, for the integrator and the registry writer. Nothing of this is implemented, and the 82 nets stay in the
readings as BOUND_DECIDES until it is ruled.

1. **By declaration, never by net class.** The board table gains a list, for example `power_stage_nodes`, of
   `{pattern, stage, role, controller, basis}` with role one of switch, gate, bootstrap, hot-swap gate. It is the
   erc-allow idiom this repository uses everywhere: an entry with no basis is refused.
2. **Counted apart.** `edge_length.py` reports the matching nets under their own count and names them with the rule
   that covers them. They are not decided, not undecided and not slow. The sums gain one term:
   signal = slow + power-stage + decided + undecided.
3. **Only while the other rule covers them.** SI-001 leaves a net out only if the covering rule is in the registry, is
   applicable to the board, and names the net in its own reading. Otherwise the net stays where it is today. No net
   may fall between two rules: that is how the 32 switch nodes in power net classes are outside every rule now.
4. **Not LOW_SPEED_OR_DC.** That class is skipped by `return_via.py` (line 177) and `ref_change.py` (line 127), and a
   gate loop is a return question. The class proposed in finding F-BOB has the same reason.
5. **The six switch nodes in class Default** (board A's HT_SW, S2_SW1, S2_SW2, SD_SW1, SD_SW2; board C's EPD_SW) take
   the SW net class their 32 siblings have, in `gen_pcb_a3.py` and `gen_pcb_c3.py`. That is a change for the authors
   of boards A and C, after set 6; it is named here and not drafted, because it changes what a layout generator
   emits.

## 6. Decisions taken in this finding

None that changes the design. The stream's decision is to propose and not to implement
(`authority: SESSION`, under the owner's standing rule of 26 September 2026):

- **W5SI-D3.** The 82 power-stage nets stay in SI-001's reading on their bound, and no `edge_allow` declaration is
  written for them. Why: a declaration names what holds a net's length, and no rule holds it; writing one would turn
  the reading green on a sentence. Reverse: once the rule of section 4 exists, apply section 5.

## 7. Open, with the next action

| Open item | Next action | Whose |
|---|---|---|
| The rule of section 4 | write it into `pcb_rules.yaml` and `pcb_rules_coverage.yaml` (next free id), with the nine layout sections as its sources | the registry writer |
| A justified limit | find out whether the makers publish their evaluation boards' layouts with dimensions (the BQ257XXEVM first); if so, file them under `v2/vendor/` and read the hot-loop area | a desk stream |
| The exclusion of section 5 | after the rule exists: the board-table list, the count in `edge_length.py`, a test both ways | the SI-001 tool's owner |
| The six switch nodes in class Default | `gen_pcb_a3.py` and `gen_pcb_c3.py` PATTERNS, after set 6 | boards A and C |
| Board C's boost has no layout guidance | ask PDi for a reference layout of the driving circuit: outside contact, so the text is prepared and the owner sends it | the owner |
| The overshoot at each switch node | bring-up measurement, named in the rule | a bench, when a board exists |
