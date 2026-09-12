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

**And on 12 September that stopped being an abstract question: it is what holds E7.** E routes to 0 hard and one
or two opens, round after round, and both of the nets that will not close are the same shape. `/USB_E6_P` runs
from `J_BLK` pad 9 at x 68.7 to `R29` pad 2 at x 264.6, **196 mm**. `/GEIGER_IN` runs from `J_GEIGER` at x 11 to
`U10` pad 9 at x 232.75, **214 mm**. E is a **267 mm strip with two routing layers**, and several signals have to
cross almost its whole length with In1 and In2 unavailable to them. The stub router closed the first of those
(63 tracks over 2,036 cells, once its emission was fixed, 32.119) and failed on the second.

**So E's layer decision is not only about pour area. It is about whether a 267 mm board carrying end-to-end
signals should have a routing layer that is not one of its two faces**, and the boards themselves have been
saying so for three rounds.

**D uses its fourth layer and not heavily.** In2 carries 2,182 mm, 34 percent of the routing, against 4,332 mm on
the outers. A two-layer D would have to absorb that; the board is 100 x 80 with an RF section, and In1's ground
plane under the exciter and the filter is an RF requirement, not a routing one. **A four-layer D is defensible on
the ground plane alone and that is the sentence the record never wrote.**

**C uses its fourth layer heavily**: 15,657 mm on In2, 55 percent of all routing, on a 344 x 228 ring. Four layers
stands, and In1 as a solid plane is the owner's own ruling of 5 September 17:08, which was explicitly four-layer
compatible.

**A is the open one, and the P0's framing of it needs one correction that I owe to reading the generator rather
than the record.** Its six layers are two planes (In1, In4) and two inner signal layers carrying 13,459 mm, 69
percent of the routing.

A's promotion was **not** unmeasured. `gen_pcb_a3.py:196` carries the number in a comment beside the In4 plane:
*"four-layer runs left 4 to 11 opens in the converter zones"*. The P0 said A's evidence was 33 hard violations
that turned out to be one router knot; that is a different measurement of a different run. **The four-layer
evidence for A is 4 to 11 open connections, and opens are not what `unknot.py` fixes.**

That makes the question sharper rather than settling it. **Four to eleven opens is inside the range this
pipeline's finish now closes as a matter of course**: `cont_route.sh` takes one continuation pass at six opens or
fewer, the stub router closes what is left, and neither was in the loop when those four-layer rounds were run.
A22's own released route needed exactly that treatment. So the experiment stands, and what it asks is narrower
and cheaper than "does A route on four layers": **does A's four-layer route reach zero after today's finish.**

Two other numbers belong in that experiment. **B.Cu carries 1,159 mm, under 6 percent of the board**, so the
router put almost nothing on the back and a four-layer run asks whether it will use the back when the inner
layers are gone. And A's four-layer form loses In3, which is not only signal: `gen_pcb_a3.py:280` dives the
VIN_RAW trunk onto In3 to cross the VBAT trunk without two nets' bands crossing on one layer (the rule of 32.39).
**That dive needs somewhere else to go before a four-layer A is even generatable**, and it is a placement change,
not a router setting.

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
| A | four-layer A24 with today's finish (continuation pass, stub router) in the loop | whether the 4 to 11 opens of the old four-layer rounds close now |
| E | two-layer variant judged by `dc_drop.py` at the record's currents | whether In2's four pours need their own layer |
| D | none; write the ground-plane rationale | the RF plane is the reason, and it was never written down |
| C | none; write the rationale from this table | 55 percent of routing is on In2 |
| B | none; the 93-opens measurement stands | already evidenced |
| P, E5 | none; write the rationale | both are two layers with nothing inner to weigh |

Each one that runs gets its result recorded here beside the row it answers.

### E, measured 12 September 2026: In2's four pours are worth a quarter of a percentage point

The experiment as the table asks it, on E7's own routed board: delete the four In2 power pours (CELL_F 2,863 mm2,
VIN_RAW 1,269, PV_P 740, TRK_OUT 628, **5,500 mm2 of inner copper**), add nothing anywhere, refill and re-solve
every rail. That is the pessimistic half of the question, because a real two-layer E would put some of that copper
on its faces; if the rails survive it as they stand, the fourth layer is not carrying the power.

| rail | E7 as it is | In2 emptied | what In2 is worth |
|---|---|---|---|
| CELL_F, 10 A | 13 mV, **0.09%** MET (In2 carries 43% of the current) | 26 mV, **0.18%** MET (B.Cu carries 97%) | 13 mV |
| VIN_RAW, 8 A | 213 mV, **1.77%** MET (In2 carries 20%) | 241 mV, **2.01%** MISSED | 28 mV |

**Five and a half thousand square millimetres of inner copper are worth 0.09 and 0.24 percentage points**, and
with all of it gone the 10 A pack node still reads 0.18 percent of 14.4 V. VIN_RAW then sits one millivolt over
its 2 percent line (241 mV against 240), which a wider band on either face closes without a layer.

**So the four pours are not the reason E is a four-layer board.** What is left of E's layer question is In1, the
solid ground plane, and the routing: `layer_audit` says neither inner layer carries one routed track, and 32.125's
route history says the board's real difficulty is end-to-end signals on a 267 mm strip with two routing layers.
That is a routing-space argument, not a power one, and it is the one to put to the owner.


---

## The decisions as they stand, 11 September 2026

**The layer count is on the never-auto floor** (`tools/reserved.json`), so what follows is the measured decision
per board with the evidence that forced it, for the owner to rule on. Four of the seven are written here and
need nothing further; two are open with a named experiment; one is evidenced and stands.

**C panel backer: four layers, decided, no experiment owed.** In2 carries 15,657 mm, 55 percent of all routing on
a 344 x 228 ring, and In1 is a solid ground plane by the owner's ruling of 5 September 17:08, which was itself
written to be four-layer compatible. A two-layer C would have to absorb 55 percent of its routing onto faces that
already carry 12,637 mm, on a board whose middle is a display window. **Cost added over two layers: one stack
step, not yet quoted.**

**D APRS: four layers, decided on the ground plane rather than on routing.** In2 carries 2,182 mm, 34 percent,
which two layers could plausibly absorb on a 100 x 80 board. The reason to keep four is In1: a solid ground plane
under the SA868 exciter, the PA stage and the filter is an RF requirement and the return path for every one of
those stages. That sentence is what the record never wrote down, and it is the decision. **Cost added over two
layers: one stack step, not yet quoted.**

**E1 dock: four layers, and the margin is now measured rather than argued.** E7's own finish says it: `dc_drop`
carries CELL_F at 10.0 A over F.Cu 133 mm2 plus B.Cu 2,327 mm2 plus **In2 2,962 mm2**, and VIN_RAW at 8.0 A over
**In2 1,293 mm2** for a worst drop of **213 mV, 1.77 percent of 12 V against a 2 percent budget**. Take In2 away
and more than half of CELL_F's copper area and all of VIN_RAW's goes with it, against 23 hundredths of a
percentage point of headroom. The second half of the decision is routing, not power: E is a **267 mm** strip and
its opens are end-to-end signals, `/USB_E6_P` 196 mm and `/GEIGER_IN` 214 mm, which is what three rounds of the
route were spent on. **A two-layer E is refused by both halves.** What is NOT settled is the opposite direction:
whether In2 should carry routing as well as pours, which would have closed those two nets without a stub router.

**P pack BMS and E5 dock block: two layers, decided, nothing inner to weigh.** P carries the pack current in 3 mm
bands on both faces and E5 is a bare contact board with 112 mm of copper. Neither has a signal that leaves its
own face. **Open on P, and it is decision 7, not this document: P is described as 2 oz and ordered as 1 oz.**

**B compute: six layers, evidenced, stands.** 82 percent of the routing is on In2 and In3, B.Cu carries 781 mm,
and three CM5 at 0.4 mm receptacle pitch measured 93 opens at 8 passes with In1 keep-outs on 5 September. It is
the one layer decision in this set that was ever taken on a measurement at the time.

**A power: OPEN, and the experiment is named and cheap.** Does A's four-layer route reach zero opens with today's
finish in the loop (a continuation pass at six opens or fewer, then the stub router)? The recorded four-layer
evidence is 4 to 11 opens, which is inside what the finish now closes routinely. **The blocker to running it is
not the router:** `gen_pcb_a3.py:280` dives the VIN_RAW trunk onto In3 to cross the VBAT trunk, and a four-layer
A has no In3, so that dive needs somewhere else to go before a four-layer A can be generated at all. That is a
placement change and it is the work the experiment waits on.

**The cost side is still missing for every row** and cannot be taken here: the runner never logs into JLCPCB and
there is no open pricing endpoint. One quote per board at its real outline and quantity five, at four layers and
at six, from the laptop ordering session, and the delta goes in beside each decision above.
