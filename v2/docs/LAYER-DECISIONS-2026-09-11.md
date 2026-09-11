# Every board's layer count, measured (P0, 11 September 2026, MESHSAT-862)

The owner reopened every board's layer decision on 11 September. The reason is in section 5a of the handover and
in appendix 32.106, and it is not that a number is wrong: it is that **four layers has no recorded rationale at
all**. Its first appearance in the record is a statement of state, PCB-A copied it from PCB-B with "same JLC
stackup", and the promotions to six were session decisions written inside a list of owner rulings.

This document is the evidence half. **It rules nothing.** The layer count and the stackup are on the never-auto
floor (`tools/reserved.json`, class "layer count and stackup"); the decision is in
`OWNER-DECISIONS-2026-09-11.md` section 2.

## The instrument

`tools/layer_audit.py` reads a board file as text and reports, per copper layer, the track count and length, the
widths in use, the zones and their nets, and the share of the board's routing that sits on an inner layer. It
needs no KiCad, so it runs on the runner.

**It is checked against a fact, not trusted:** its layer count for all seven boards equals the number of copper
gerbers in that board's shipped zip (A 6, B 6, C 4, D 4, E 4, P 2, E5 2), which is an artefact it does not read.
Its first version reported every board as having zero copper, because KiCad 9 writes multi-line tab-indented
s-expressions and the regexes were written for the one-line KiCad 7 form. A parser that silently reports nothing
is the same defect class as a gate that silently passes.

## What each board actually carries

| board | size mm | copper | outer mm | inner mm | inner share | inner layers with no track |
|---|---|---:|---:|---:|---:|---|
| A power | 240 x 160 | 6 | 6,162 | 13,459 | 69% | In1, In4 |
| B compute | 245 x 170 | 6 | 4,370 | 20,589 | 82% | In1, In4 |
| C panel backer | 344 x 228 | 4 | 12,637 | 15,657 | 55% | In1 |
| D APRS | 100 x 80 | 4 | 4,332 | 2,182 | 34% | In1 |
| E1 dock | 267 x 68 | 4 | 8,715 | **0** | **0%** | In1, In2 |
| P pack BMS | 70 x 44 | 2 | 2,416 | 0 | 0% | (none) |
| E5 dock block | 43 x 26 | 2 | 112 | 0 | 0% | (none) |

Measured on the current project board of each, 11 September 2026.

## What the table says, board by board

**E1 dock is the finding.** It is a four-layer board and **neither inner layer carries one routed track**. In1 is
a ground plane and In2 carries four power pours (CELL_F, VIN_RAW, PV_P, TRK_OUT). So E's fourth layer buys pour
area, not routing space, and the question for E is a power question with a number attached: whether those four
pours can live on the two outer layers beside the 3 mm bands already there, at the currents of the record. That
is answerable by `dc_drop.py` on a two-layer variant, which is an experiment, not a debate, and it is the cheapest
layer decision in the set.

**D uses its fourth layer and not heavily.** In2 carries 2,182 mm, 34 percent of the routing, against 4,332 mm on
the outers. A two-layer D would have to absorb that; the board is 100 x 80 with an RF section, and In1's ground
plane under the exciter and the filter is an RF requirement, not a routing one. **A four-layer D is defensible on
the ground plane alone and that is the sentence the record never wrote.**

**C uses its fourth layer heavily**: 15,657 mm on In2, 55 percent of all routing, on a 344 x 228 ring. Four layers
stands, and In1 as a solid plane is the owner's own ruling of 5 September 17:08, which was explicitly four-layer
compatible.

**A is the open one, exactly as the P0 says.** Its six layers are two planes (In1, In4) and two inner signal layers
carrying 13,459 mm, 69 percent of the routing. The plain question is whether that fits on three routing layers
instead of four. **The measurement nobody has taken is a four-layer rerun with `unknot.py` in the loop**: A22 was
promoted after eight failed four-layer rounds whose 33 hard violations turned out to be a single router knot, and
no four-layer attempt was ever made after `unknot.py` existed.

There is a second number in A's row worth reading: **B.Cu carries 1,159 mm, under 6 percent of the board.** The
router put almost nothing on the back. A four-layer rerun is therefore not only "can three layers hold four
layers' copper": it is also "will the router use the back side when the inner layers are not there".

**B is evidenced and stands.** 82 percent of its routing is on In2 and In3, and B.Cu carries 781 mm. Three CM5 at
0.4 mm receptacle pitch measured 93 opens at 8 passes with In1 keep-outs (5 September 17:08). That is a measurement
against the stack, and it is the one layer decision in the set that was ever taken on evidence.

**P and E5 are two layers and neither has an inner layer to discuss.** P carries the pack current in 3 mm bands on
both faces on JLC's 2 oz stack; E5 is a bare contact board. Both need their decision written, and for both the
measurement is already in the board.

## What is still missing, and it is the same thing for every board

**The cost side.** No like-for-like four against six quote exists for any board in this set, and the promotions
were never costed. The runner cannot take one: JLCPCB publishes no open PCB pricing endpoint (the three paths the
open parts API's shape suggests all return 404) and the standing rule is that the runner never logs into JLCPCB.
The quote comes from the laptop ordering session, one per board at its real outline and quantity five, at four
layers and at six, nothing else changed.

## The experiments this document asks for

| board | experiment | what it answers |
|---|---|---|
| A | four-layer rerun of A24 with `unknot.py` in the loop, same placement, same passes | whether the promotion to six was ever needed |
| E | two-layer variant judged by `dc_drop.py` at the record's currents | whether In2's four pours need their own layer |
| D | none; write the ground-plane rationale | the RF plane is the reason, and it was never written down |
| C | none; write the rationale from this table | 55 percent of routing is on In2 |
| B | none; the 93-opens measurement stands | already evidenced |
| P, E5 | none; write the rationale | both are two layers with nothing inner to weigh |

Each one that runs gets its result recorded here beside the row it answers.
