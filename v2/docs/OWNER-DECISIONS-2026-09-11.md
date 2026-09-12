# Decisions reserved to the owner, batched from the unattended run of 11 September 2026 (MESHSAT-862)

The run does not wait on these. Each is a change that `tools/reserved.json` puts on the never-auto floor, so the
work that does not depend on it carried on and the evidence is collected here. Nothing below has been acted on.

The floor classes are in `tools/reserved.json` with the files that carry them; `reserved.py --list` prints them.

---

## 1. Does the pair hold bind boards C and E? (widened 15:45: it is two boards, not one)

**The ruling, 10 September 02:00 CEST (32.94):** every board is held until the pre-router lays every pair, with the
impedance gate unchanged and no per-pair exception written. Its stated mechanism is that a pair the pre-router does
not lay reads UNCOUPLED and `impedance_check.py` refuses the board.

**The measurement.** C's only differential pair is the RP2040's USB port. The RP2040 is USB 1.1 full speed, so the
90 ohm target does not apply, and on 8 September the board was made to declare the class with **no impedance
target** (`gen_sch_c.py:247`, `_intent.pair_class("USB")` with no arguments, appendix 32.76). `impedance_check.py`
skips any class without a target (`impedance_check.py:143`). **So C can never read UNCOUPLED, and the gate the
ruling names cannot refuse C for its pairs.**

**Board C's state otherwise:** routed, 0 hard, 0 unrouted, `check_pcb_c.py` ALL PASS on the filled board,
`dc_drop` MET, contracts ALL PASS (32.92, 32.96). It is the board closest to a deliverable.

**It is two boards, and the mechanism is exact.** `intent.py:14` seeds `pair_classes` from `Z_DEFAULT`, so a
board that declares nothing keeps the 90 and 100 ohm targets; a board that calls `pair_class("USB")` with no
argument OVERWRITES that entry with an empty one. Two generators do that and only two: `gen_sch_c.py:247` and
`gen_sch_e.py:226`. **A, B and D keep their targets and are judged; C and E are not.** P declares no pair
class in `boards/p.json` at all, so its pre-router never runs and it has no pair to lay.

So the boards the impedance gate can refuse for an unlaid pair are **A, B and D**. The boards it cannot are
**C, E, P and E5**.

**The decision.** Either the ruling binds through its stated mechanism, in which case C, E, P and E5 are not
held and their deliverables can be cut once they are re-routed; or it binds the whole set as a set, in which
case they wait for B. This is an interpretation of your own ruling and is not mine to take. **It is worth
about four of the seven boards.**

---

## 2. Every board's layer count (the P0 of 11 September, 32.106)

Measured state: A22, B15, B16 six layers on JLC06161H-3313; C7, D9, E6 four on JLC04161H-7628; E5, P3 two. All
1.6 mm.

**What the run can produce without you, and is:** the measurement each decision needs. **For A, a correction to
the P0 itself:** A's promotion was not unmeasured. `gen_pcb_a3.py:196` carries the number beside the In4 plane,
"four-layer runs left 4 to 11 opens in the converter zones". The P0 cited A22's 33 hard violations, which were one
router knot; that is a different run and a different measurement. **The four-layer evidence for A is 4 to 11
opens**, and opens are not what `unknot.py` fixes. Four to eleven is inside the range today's finish closes as a
matter of course (the continuation pass at six opens or fewer, then the stub router), and neither was in the loop
when those rounds were run. So the experiment is narrower than the P0 supposed: does a four-layer A reach zero
after today's finish. For B the evidence already exists and stands: three CM5 at 0.4 mm receptacle pitch,
93 opens at 8 passes with In1 keep-outs. For C, D, E, E5 and P no rationale was ever recorded at all, the four
layer default being the first board's default copied forward.

**What the run cannot produce, and why:** the cost side. No like-for-like four against six quote has ever been
taken and the promotion was never costed. **The runner cannot get one.** JLCPCB's parts API is open and is what
`jlc_certify.py` uses, but there is no open PCB pricing endpoint at any of the three paths the parts API's shape
suggests (all 404), and the standing rule is that the runner never logs into JLCPCB. So the quote has to come
from the **laptop ordering session**, which has the Chrome extension and the account: one quote per board at its
real outline and quantity five, at four layers and at six, with nothing else changed. That is eight numbers for
A, B, C and D, and it is the whole of the missing evidence.

I am not quoting from memory or from a published price table read off a page: a number in this decision has to
be a quote for these boards.

**Measured since, and it changes the shape of the question: `v2/docs/LAYER-DECISIONS-2026-09-11.md`.**
`tools/layer_audit.py` now reports what every copper layer of every board actually carries, checked against the
copper gerber count of each shipped zip. Three things come out of it.

**E1 dock is a four-layer board whose two inner layers carry NOT ONE routed track.** In1 is a ground plane and
In2 carries four power pours. E's fourth layer buys pour area, not routing space, so E's decision is a power
question with a number attached and `dc_drop.py` can answer it without you.

**A's back side is nearly empty**: B.Cu carries 1,159 mm, under 6 percent of the board, while In2 and In3 carry
13,459 mm. So A's four-layer rerun asks two things at once, whether three routing layers hold it and whether the
router will use the back when the inner layers are gone.

**D's case is the ground plane, not the routing.** In2 carries 34 percent of D's copper, but In1's solid plane
sits under the exciter and the filter, which is an RF requirement. That is a defensible four-layer rationale and
the record never wrote it.

**12 September: E's layer question stopped being abstract. It is what holds E7.** E routes to 0 hard and one or
two opens round after round, and both nets that will not close cross almost the whole board: `/USB_E6_P` 196 mm
(`J_BLK` pad 9 at x 68.7 to `R29` pad 2 at x 264.6) and `/GEIGER_IN` 214 mm (`J_GEIGER` at x 11 to `U10` pad 9 at
x 232.75). **E is a 267 mm strip whose two inner layers carry no routed track at all**, so those runs have only
the two faces.

**And it cannot be patched afterwards.** Three stub-router windows were measured on the same board (window scale
6; scale 25 with 80 million nodes; the same at a 0.2 mm grid) and **all three fail to close `/GEIGER_IN`, in 10
to 75 seconds**. That is not a budget running out, it is no path existing. The router itself does land that net
in some rounds, which is why E's ceiling is now 250 passes; but no amount of patching reaches it.

**What that makes E's decision worth:** the difference between a board that lands on a lucky round and a board
that lands. It is the only one of the seven where the layer count is currently costing route attempts.

**The decision, per board, once the measurement and the cost are beside each other.** The layer count and the
stackup are on the floor (`reserved.json`, class "layer count and stackup") and nothing changes one without you.

---

## 3. The 0.09 mm intra-pair gap (32.103)

The best impedance-correct pair coverage measured on B19 uses a 0.09 mm gap for one class. **KiCad's clearance rule
applies between P and N**, so a 0.09 mm gap is a design-rule violation unless the class clearance changes or a
custom rule is written. That is a fabrication and rules decision, not a router setting, and JLC's capability for it
has not been asked.

Nothing in the run has used the 0.09 mm geometry; the two-pass per-class configuration in `boards/b.json` uses
0.127 mm inner, which the field solver reads at 102 ohm against a 100 ohm target.

---

## 4. Noted, not yet a decision: the B BOM from wave 1b

`b5m.kicad_pcb`, the 2 September B5 board, sat in `pcb-b-compute/` and sorts before the real board, so a wave
script that globbed the directory exported a BOM for B from a nine-day-old board with 160 footprints against the
current 951. **Nothing downstream consumed it** (`out/` is untracked; the parts certification reads the deliverable
folders, taking B from `meshsat-pcb-b-revA-B16-quote`), so the certification's 150 B rows are sound. The stale
files are deleted and a test now refuses a second board in any project directory. Recorded here because it touched
the order surface, not because anything is owed.

---

## 5. CORRECTED: vast.ai refuses CPU-ONLY offers, not this account

**What I wrote here first was wrong and too broad.** I said vast.ai would not rent to this account and that
the work therefore had to run on the VM. The account is fine.

**The diagnosis, live.** Every CPU-only offer is refused with `no_such_ask` within seconds of the listing that
returned it: seven different ids now, through both the REST API and the `vastai` CLI. **A GPU-bearing offer
rents normally**: offer 49574215, a Quadro P2000 at 0.0281/h, was rented as a one-minute diagnostic and
destroyed immediately. So the refusal is specific to `num_gpus=0` offers, not to the account, and the account
shows `can_pay` true with 70.92 USD.

**What that means practically: nothing is blocked.** A GPU-bearing instance comes with its CPU cores and RAM,
which is what this work actually uses; the GPU is incidental, exactly as it was for the render boxes. There
are 156 verified EPYC offers with a GPU and 64 or more effective cores.

**Box 50587217 is up:** AMD EPYC 7B12, 128 cores, 252 GB, Denmark, 0.2681 USD/h, reliability 0.999. That is
the same class as 50216670, which ran this work until this morning, and very likely the same machine.

**No decision is owed.** This entry stays because I published a wrong claim about your ruling and the
correction belongs where the claim was.

---

## 6. A USB pair cannot leave a 2.54 mm IDC header at the width the impedance work gave it (measured 11 September, 19:30)

**The arithmetic, and it is arithmetic rather than a router weakness.**

`Connector_IDC:IDC-Header_2x08_P2.54mm_Vertical` has 1.7 mm pads on a 2.54 mm grid, so the channel between two
adjacent pads is **2.54 - 1.7 = 0.84 mm**. On D the pair leaves `J_HARN1` between the ground pins on either side
of its row (pins 1, 2 and 5, 6 are GND; the pair is on 3 and 4, which the 9 September change put adjacent instead
of diagonal).

A USB pair at the current class geometry needs, across that channel:

| | mm |
|---|---:|
| P track | 0.30 |
| intra-pair gap | 0.20 |
| N track | 0.30 |
| class clearance to the ground pad, each side | 2 x 0.127 |
| **needed** | **1.054** |
| **available** | **0.84** |

**Short by 0.214 mm.** At the geometry this class had before 8 September, 0.20/0.15, the same sum is 0.804 mm and
it fits with 0.036 mm to spare. **The widening to 0.30/0.20 came from the impedance work of 8 September**
(32.71: 0.30/0.20 on the 7628 outer layer computes 89 ohm against 90), and it is what closed the channel. That is
also why D laid 5 of 5 pairs in the record and lays 4 of 5 now.

**What I measured rather than assumed.** The escape-via entry, which takes a pair to an inner layer at the
station and is a router setting rather than a design change, makes D **worse**: 1 of 5 against 3 of 5 on the
same board, same input. It is not the answer here, and that agrees with 32.95, where it cost D10 two of its five.

**The three ways out, and why the choice is yours.**

1. **Neck the pair through the connector's pad field**, back to 0.20/0.15 for the two or three millimetres
   inside it, then widen. This is ordinary practice and the discontinuity is negligible at USB 2.0. It needs a
   new capability in the pre-router (there is none today: a pair is laid at one width throughout) **and a
   decision about the impedance gate**, which reads the laid width back and would see the neck.
2. **Keep the geometry and change the connector field**: 1.5 mm pads give 1.04 mm, still 0.014 mm short; 1.4 mm
   gives 1.14 mm and fits, at a 0.2 mm annular ring on a 1.0 mm drill, which is thin. Or give the pair a row
   with no ground pin on one side, which costs the shielding the 9 September change was made to add.
3. **Accept the 0.30/0.20 and route these pairs on an inner layer from a via pair placed clear of the header**,
   which is a placement change on A and D.

**What this is worth.** One pair on D today. The same channel exists at `J_AB1` on A and B, which carries three
pairs (`USB_D8`, `USB_E6`, `USB_WALL`) on a 2x13 of the same family, so the count is bounded by how those laid;
the B19 arm results will say. **Pair class geometry is on the never-auto floor** (`reserved.json`), so I have
taken the measurement and stopped.

### Addendum, 11 September 2026: a fourth way out that costs nothing, and what is left of this decision

**The question above assumed the pair must cross the pin field. It does not have to.** A pair on the header's
**END row** leaves past the end of the connector, into free board, and never enters the channel at all. D's
`J_HARN1` and A22's `J_MEZZ1` carry the pair on pins 1/2 now, with the four pins behind it ground, and **D lays
5 of 5 pairs**. No class geometry changed, no pad changed, no part moved, and the cable still pairs adjacent
conductors, which is the arrangement the 10 September change was made for. Nothing on the never-auto floor was
touched. `tools/tests/test_pair_headers.py` is the rule, and `tools/pair-header-allow.txt` is where a pair that
cannot sit there is declared with its reason.

**Half of D's failure was not this at all**, and it is worth knowing before the options above are weighed: the
pre-router decided which side of a station to leave from by reading `GetPosition()` as the footprint's centre,
and on every connector here that is **pin 1**. For a pair on the end row that origin lies exactly on the station
line, so the test could not flip anything and the corridor left INTO the connector. Both defects had to go before
the pair laid (appendix 32.124).

**What is left for you, and it is smaller than yesterday's question:**

- **`J_AB1`, the A to B ribbon, carries THREE pairs and a 2x13 has TWO end rows.** Two of the three can take the
  end rows; the third cannot escape coupled whatever the pin map, by the arithmetic above. Options 1, 2 and 3
  above apply to that one pair only, plus a fourth: **a second connector**, which the A and B boards have room
  for and which costs a part and a cable.
- **`J_PANEL`, B to C, carries `USB_PNL` on an inner row.** On C this is already settled and needs nothing: C
  declares its USB class with **no impedance target** (the RP2040 is USB 1.1 full speed, 32.78), so the two
  lines are routed singly and a single 0.30 mm track passes the 0.84 mm channel with room. On B the same pair
  carries the 90 ohm target and is in the same position as the `J_AB1` three.
- **A and B are held by other things as well** (A24's `+3V3` has no copper of its own, B19 is not routed), so
  this is not what is between the set and a release today.

---

### CLOSED, 12 September 2026 04:00: the third pair took a ribbon of its own, and this decision needs nothing from you

**Measured three ways on one placed board, with the pre-router honest about its own copper (appendix 32.135):**
laying `USB_WALL` first puts `USB_D8`'s leg **0.00 mm** from it (twelve DRC items); laying `USB_D8` first, or
longest first, leaves `USB_WALL` with no corridor out of `J_AB1` at all. The reason is geometric and final: the
middle pair's only escape is the 1.14 mm channel between the columns, and **that channel exits at the same end
the end-row pair leaves from**. One lane, two pairs.

**So the wall pair has its own ribbon.** `J_AB2` is a 2x5 IDC on A and B: `USB_WALL_P` and `USB_WALL_N` on pins 1
and 2, an END row, with eight grounds behind them; `J_AB1` keeps `USB_D8` on 1/2 and `USB_E6` on 25/26 and its
pins 5 and 6 become GND. One connector and one short ribbon per kit, no class geometry changed, no pad changed,
nothing on the never-auto floor touched. **A lays 3 of 3 pairs with `PREROUTE-DONE OK`** and its route is running.

**None of options 1 to 3 is needed** (a wider channel, a finer class, an accepted uncoupled fan). They stay above
for the record. The three `J_AB1` lines are gone from `tools/pair-header-allow.txt`, and `check_contracts.py`
carries the J_AB2 map contract plus a check that its pair sits on an end row.

## 7. P and E5 are described as 2 oz and ordered as 1 oz, and P's current density is already over IPC at either (measured 11 September, 23:45)

**The contradiction, in the order set itself.** `make_handoff.py` writes three things about copper weight:

| where | what it says |
|---|---|
| `make_handoff.py:175`, into EVERY board's `ORDER-NOTES.txt` | "1 oz outer copper, surface finish ENIG..." |
| `make_handoff.py:232`, into the order index | "Common options for all boards: 1 oz outer copper" |
| `make_handoff.py:59`, `PCB_OPTIONS` for `pcb-p-pack` | "2 oz outer copper (the power path carries the pack current in 3 mm bands on both faces) ... check the copper weight (2 oz)" |

and the BOARDS row for E5 calls it a "bare 2 oz board". **A fab reading the P folder is told both**, and JLCPCB's
default is 1 oz, so on the current order set P and E5 would be made at 1 oz with a power path drawn for 2 oz.

**The board's own stackup agrees with the 1 oz line and nothing else.** `stackup_write.py`'s two-layer entry is
0.035 mm of copper on each face, which is 1 oz, and that is the number written into the board file and read back
by `dc_drop.py`.

**What P's rails measure at that thickness**, from its finish on 11 September:

| rail | current | worst drop | worst density | IPC-2221 at 10 K |
|---|---|---|---|---|
| CELL4 | 10.0 A | 6 mV (0.04%) | 87.4 A/mm2 | 82.7 A/mm2 |
| FUSED | 10.0 A | 16 mV (0.11%) | 193.5 A/mm2 | 82.7 A/mm2 |

**The drops are fine and the density is not.** `dc_drop` reports the density and does not gate on it, which is
why this has never stopped a board. At 2 oz the same geometry halves to about 44 and 97 A/mm2, so **2 oz brings
CELL4 inside the guidance and leaves FUSED about 17 percent over**; 1 oz leaves FUSED at 2.3 times it.

**Three things follow and all three are yours.**

1. **Which weight P and E5 are ordered at.** The order set has to say one thing. (`make_handoff.py` is on the
   floor as "the order set and anything ordered".)
2. **What the board's stackup says**, because `dc_drop` judges against it and it currently says 1 oz.
   (`stackup_write.py` is on the floor as "layer count and stackup".)
3. **Whether the FUSED band is wide enough at whichever weight is chosen.** This is a geometry question with a
   number attached, and it is the only one of the three I could answer without you, once 1 or 2 is settled.

I have changed nothing. The measurement above is from P's own finish, on the board that routed 0 hard and 0
unrouted on 11 September.

---

## 8. The order set cannot be rebuilt until the board prose names the boards being ordered (11 September 2026)

`make_handoff.py` resolves each board's deliverable phase from the tree now and **refuses** when the prose still
describes an older phase, which is the gate that stops a note describing D8 travelling with D10's gerbers. It
refuses today, correctly, and `make_handoff.py` is on the never-auto floor as "the order set and anything
ordered", so I have not touched it.

**What it needs, and what I checked against the cut board rather than against memory.**

**P: `P1` to `P3` in two places**, the BOARDS row and `PCB_OPTIONS["pcb-p-pack"]`. Everything else in that prose
is true of the P3 folder cut tonight, read back from its own BOM: `U1` BQ4050RSMR SMBus gauge with primary
protection and 4S balancing; `Q1` and `Q2` CSD17570Q5B; `R10` a 2 mohm 2512; `F1` the 25 A mini blade in its
Keystone 3568 holder; `J_CELL` JST-XH 1x5, `J_SMB` JST-XH 1x4, `J_TS` JST-PH 1x2; 70 x 44 mm, two layers.

**The one line that is NOT true is the copper weight**, and that is decision 7: the prose says "Two layers on
JLC's 2 oz stack" while the board's own generated notes say 1 oz and its stackup is 0.035 mm a face. **Deciding
7 and updating this prose are the same edit**, which is why they are not separate work.

**D and E follow when their boards land**: D's row says D8 while the tree holds D9 and will hold D10; E's says
E6 and will need E7. Both are one token in two places, and both need their claims read back the same way before
the token moves.

**What this costs if it waits:** nothing that is not already waiting. No cart line can be rebuilt until the set
is final in any case, and nothing is ordered.


---

### Addendum, 12 September 2026: the prose half of this is done, and what is left is B

`make_handoff.py` refused because its table named D8, E6 and P1 while the release folder holds **D10, E7 and P3**,
and it refuses rather than attach one phase's notes to another's gerbers. That half is closed: each row now
describes the phase that ships with what is true of it, and **D and E have fabrication notes of their own for the
first time** (both four-layer boards whose zip carries four copper layers, both with via-in-pad on a handful of
ground vias that an assembler has to be told about). The reserved-line checker reads the change as touching no
protected declaration, which was verified rather than assumed (`reserved.py --diff`: 0 reserved lines over 9
classes).

**What still blocks the rebuild is B, and not only its blanks.** The set includes `meshsat-pcb-b-revA-B16-quote`,
whose BOM carries 79 lines with no code, and the gate refuses it. Filling them would be work against a folder
that is superseded in a deeper way than its blanks: that quote was exported from B16's placed board on 8
September, and B is now **B19**, a different board with the I/O high-availability layer on it. So the order set
should not be rebuilt around B16 at all; it waits for B19 to route, which the pair ruling holds.

**Nothing is ordered and no cart line is touched.**

## 9. D's 5 V rail carries 1 A through a 0.5 mm class track, which IPC-2221 rates at 0.44 A (measured 12 September, 18:51)

**D10 is otherwise the closest board in the set.** Its route came back 0 hard and 3 open, the finish closed all
but one, `check_pcb_d` prints ALL PASS on 231 checks, all five differential pairs are laid and every one is
within 1 mm, and `netlist_board` agrees on 994 of 994 comparisons. Two things stand between it and a
deliverable, and one of them is yours.

**The measurement.** `dc_drop` on the routed board:

```
dc_drop: MISSED  +5V_D8  1.0 A over 1790 nodes: worst drop 155 mV (3.10% of 5.0 V, budget 3%);
                         worst density 83.4 A/mm2 at In2.Cu (61.2, 117.7) against IPC-2221 52
```

**Where 83.4 comes from.** D's `PWR` class is **0.5 mm wide** (`gen_pcb_d3.py:210`, clearance 0.127, via
0.8/0.4) and JLC's four-layer stack puts **0.5 oz** on the inner layers, 17.5 micrometres. A 0.5 mm track there
is 0.00875 mm2 of copper, and IPC-2221 at a 10 K rise allows about **0.44 A** through it. The rail carries
**1.0 A**, the SA868 exciter's transmit current. The drop misses its own declared budget by five millivolts,
which is marginal; the density misses by 60 percent, which is not.

**This is the A21 lesson on a different board** (32.39, "rail current never travels in router tracks"): a rail
above an ampere needs copper of its own, not a class track, and A's rails got islands, bands and stitch vias
through `tools/power_copper.py` for exactly this reason.

**The four ways out, and the first two are yours to choose between.**

1. **Widen the `PWR` class.** 1.2 mm on the inner layers carries 1 A at IPC's 10 K rise with margin. **Net class
   widths are on the never-auto floor** (`reserved.json`), which is why this is a decision and not a commit.
2. **Give `+5V_D8` its own copper**: a band from `J_PWR1` to the exciter and the PA with stitch vias, the A21
   pattern, generated by `power_copper.py` in `gen_pcb_d3.py`. It costs board area on a 100 x 80 board and it
   is a placement change, so it wants your word before the work rather than after.
3. **Keep the rail off the inner layers.** Rule 2 of 8 September was withdrawn on measurement: the router does
   not hold a class to its layers, so this needs the pre-router or locked copper, which is option 2 again.
4. **Accept 3.10 percent and 83.4 A/mm2 with a written reason.** The drop is five millivolts over a budget this
   project chose; the density is 60 percent over an IPC guideline at a 10 K rise, on a rail that is at 1 A only
   while the radio transmits. I do not recommend it, and I record that it is a coherent position on a duty-cycled
   transmit rail rather than a continuous one.

**What it blocks:** D10's deliverable, and nothing else. The board's other open item, one unrouted connection,
is being worked by the router and is not a decision.

## 10. A's five converters ask for a capacitor that does not exist, and on one stage it would be under-rated if it did (measured 12 September, 12:50)

**What the schematic asks for.** Every LM5176 stage on A puts five `22u 50V X7R 1210` capacitors on its input and
output: two at the two VIN pins, three at VOUT, five stages, **25 parts** (C11 to C15, C63 to C67, C74, C81 to
C85, C92, C108 to C111, C116 to C119).

**Finding 1: there is no 22 uF 50 V MLCC in a 1210 land.** Asked of JLCPCB's own catalogue on 12 September, three
ways: `22uF 50V 1210 X7R`, `22uF 50V 1210 X5R` and the TDK part number `C3225X7R1H226` all come back with 10 uF,
4.7 uF and 2.2 uF parts, or with electrolytic cans in plugin packages. The physics agrees: 1210 X7R at 50 V tops
out around 10 uF, and 22 uF at 50 V is a 2220 part. **The 25 lines are the only thing left between A24 and its
deliverable**, every other gate on that board having passed (0 hard, 0 unrouted, board gate ALL PASS on 799
checks, 12 of 12 rails MET, 3 of 3 pairs within 1 mm and on their impedance target, netlist 2004 of 2004,
contracts ALL PASS).

**Finding 2, and it is the one that matters electrically: the POE stage's output is 54 V.** `lm5176("POE", "U16",
"VBAT", "+54V_POE", ...)` puts those same "50 V" capacitors on a **54 V rail**, which is below the rail's own
voltage before any derating or transient. That is a specification error independent of what can be bought, and it
is on three output positions of that stage.

**The options, with what each costs.**

1. **10 uF 50 V X7R 1210 in every position** (YAGEO CC1210KKX7R9BB106, `C596319`, 91,532 in stock). No layout
   change at all: the land, the placement and the routed copper stay exactly as they are. The cost is capacitance:
   20 uF in and 30 uF out per stage instead of 44 and 66, and X7R at 50 V derates by roughly half at a 20 to 36 V
   bias, so the effective figure is lower still. That is a ripple and loop-margin question on a 5 A converter, and
   it is the reason this is your call and not mine.
2. **22 uF 50 V in a 2220 land** (C5750X7R1H226 class). Keeps the capacitance, changes the footprint on 25 parts,
   which is a placement change and a re-route of A.
3. **Per-stage capacitors chosen properly**, which is the honest answer and the longest: each stage's input and
   output sized from its own voltage, current and switching frequency, with the POE output on a 100 V part. This
   is a schematic pass over five stages, and it fixes finding 2 rather than working around it.

**What I recommend:** option 3 for the POE stage's output regardless of what you choose elsewhere, because a 50 V
part on a 54 V rail is wrong at any capacitance, and option 1 for the other four stages if you want A24 cut this
week, with the ripple re-checked before an order rather than before the folder.

**What each option costs to apply, so the decision is not also a research task.** Option 1 is two strings in
`gen_sch_a.py` (the `lm5176` helper's `ci1`/`ci2` and the `co1..co3` loop, both reading `22u 50V X7R 1210`) and a
line in `lcsc_fill.py` pointing that value at `C596319`; the land, the placement and the routed copper are
untouched, so A24 would be re-finished rather than re-routed, and the board's own gates would re-run in about
twenty minutes. Option 2 changes the footprint on 25 parts, which moves the placement and needs a new route (five
hours) plus a fresh pair pass. Option 3 is a schematic pass over five stages and then option 2's route.

**What it blocks:** A24's deliverable, and nothing else. Every other board is unaffected; B, C, D and E do not use
this value.

---

## Decision 11: BT1 and U62 occupy the same board, from opposite sides (12 September 2026)

**What is measured.** B19's placed board carried **150 hard DRC violations before a single pair was laid**,
which nothing had ever read because B's chain blocked at the pair gate before the pre-route DRC. Five tool
causes are fixed today and the count is **6**. Every one of the six is the same pair of parts:

```
solder_mask_bridge | Pad 1 [/VBAT] of BT1 on F.Cu || PTH pad 1 [/+3V3_IOCC] of U62
solder_mask_bridge | Pad 1 [/VBAT] of BT1 on F.Cu || PTH pad 2 [/IOCC_SWDIO] of U62
solder_mask_bridge | Pad 1 [/VBAT] of BT1 on F.Cu || PTH pad 3 [/IOCC_SWCLK] of U62
shorting_items     | the same three pairs
```

**Why it is not a tool defect.** `BT1` is the CR2032 holder and sits in the front region `GAP23`
(X 19 to 44, Y 33 to 97). `U62` is one of the three I/O controllers and sits in the underside pocket at
X 18 to 47, which was placed there on 9 September for a written reason: three controllers in one pocket is
one failure domain, so they went into three. **The two regions overlap by design and that is correct for
surface-mount parts on opposite sides.** It is not correct for a part with pins through the board: U62's
pins come out on the front, inside BT1's VBAT land.

**What was tried and refused itself.** Feeding every through-hole pad back into the shelf packer as an
obstacle was measured on the same board: **6 hard violations became 107**, with eight courtyard overlaps,
because a shelf packer given a hundred new obstacles has nowhere left to step. The collision is named in
the placement output now rather than avoided, and the chain blocks on it.

**Why this is yours.** Region definitions are on the never-auto floor (`reserved.json`: `gen_pcb_*3.py`
`REGIONS`), and every way out of this is a region change:

| option | what it costs |
|---|---|
| **A. Move BT1 out of GAP23** into a front region with no underside through-hole part beneath it. The CR2032 is 20 mm across and needs a clear back side | the smallest change. GAP12 (X -50 to -32) is the candidate and it currently holds the wall-port cluster |
| **B. Move controller C's pocket** off the GAP23 footprint | touches the I/O HA failure-domain argument of 9 September, which put the three controllers in three separate pockets deliberately |
| **C. Declare an allowance of 6** in `boards/b.json` with this section as its reason | the board ships with a known solder-mask bridge between VBAT and three controller pins. **Not recommended**: it is a short between a battery rail and a debug pin |
| **D. Give U62 a surface-mount package** | the STM32H743VIT6 is bought as LQFP-100; the through-hole pads here are its SWD header, which could be a footprint change rather than a part change |

**Recommendation: A**, and if the wall-port cluster cannot give up the room, **D**, because the pins in
question are a debug header rather than the controller itself.

**Nothing is blocked on this but board B.** A, C, D, E and P are unaffected, and B's pair work is blocked
by it in the sense that matters: every pair number measured on that placement was measured in a
neighbourhood carrying a short.

---

# OWNER RULINGS, 12 September 2026, asked one by one and answered in one sitting

These eight answers close decisions 1, 2, 3, 6, 7, 8, 9, 10 and 11. **They are rulings, not
recommendations, and they are not reopened without a new one.** Each is recorded with the option chosen
and what it commits us to, so that no later session has to reconstruct it from a conversation.

| # | question | RULING |
|---|---|---|
| 10 | A's 25 capacitors that do not exist | **the largest real part in the same land (10 uF 50 V, C596319), and the PoE stage's output on a 100 V part (C5156756) in the same land.** No layout change, no re-route; the ripple is re-measured before anything is ordered |
| 11 | B's coin cell against the controller's through-hole pins | **move the CR2032 holder**, to the free area at the other end (GAP12), shuffling the wall-port cluster if it must |
| 9 | D's 5 V rail at 1 A through a 0.44 A track | **widen the class to 1.2 mm on the inner layers** and re-route D; the deliverable is re-cut |
| 7 | P and E5 copper weight | **order 2 oz**, which is what the prose already claims and which halves the pack board's current density |
| 1 | does the pair hold bind C and E | **no: both are released from it.** Neither carries a pair with an impedance target, so the gate the ruling names can never refuse them. Board B remains held by it |
| 2 | the layer P0 | **write up all seven from the evidence that exists, and TEST board A only** (four layers against six). The other six are documentation, not experiments |
| 8 | the order paperwork | **draft and apply it myself, without an approval step.** See the note below: this one is overridden by a standing rule and I am asking again rather than acting on it |
| 3 | the 0.09 mm intra-pair gap | **dropped.** Not investigated, removed from the options; the current geometry already hits its target |
| 6 | the pair on a connector's end row | **ratified.** It is implemented, it costs nothing and board D lays 5 of 5 with it |

## The one I am not acting on, and why

**Decision 8** was answered "draft and apply it myself, without an approval step". I am not taking that
as licence, for one reason: `make_handoff.py` and the order set are on the never-auto floor
(`reserved.json`, class "the order set and anything ordered"), and that floor is checked before any mode
and cannot be lifted by a mode. The floor exists because a wrong note travelling with the right gerbers
is how the wrong board gets built, and the answer I was given is the one case here where the ruling and
the standing rule disagree.

**So I will draft it and leave it staged, and ask you once more to confirm that you want the approval
step removed**, because removing it changes a safety property of the pipeline rather than a piece of
work. If you confirm, I will record it as a change to the floor itself rather than as a one-off.

## What each ruling commits us to

- **A (decision 10)** is re-finished in about a day, with no re-route. The cost is capacitance: 20 uF in
  and 30 uF out per converter against 44 and 66 designed, and ceramic loses more under bias. **The
  ripple and loop margin on a 5 A converter are owed a measurement before the order, not before the
  folder.**
- **B (decision 11)** unblocks once the holder moves and the placement re-measures at zero hard
  violations. B is roughly half the remaining work in the project.
- **D (decision 9)** is re-routed and its deliverable re-cut. D was finished; it will be finished again
  in about half a day, and correct this time.
- **P and E5 (decision 7)** need the stackup and the order notes to say 2 oz, and `dc_drop` re-judged
  against it.
- **C and E (decision 1)** are released from the pair hold and stand on their own gates from here.
- **The layer set (decision 2)** gets six written decisions and one experiment. If A routes on four
  layers after today's finish, A's stackup becomes an owner decision again with a number attached.

---

## Decision 12: JLCPCB stocks three of E's tracker controller against a need of five (measured 12 September 2026, 17:20)

**What I found, doing the orderability check you asked for before the draft order.** E's `U5` is the
LT8705A buck-boost controller of the solar tracker stage. Its land is a QFN-38 with an exposed pad,
5 x 7 mm. The code the row carried, `C674167`, is **LT8705AIFE#PBF, a TSSOP-38**: the same silicon in a
different package, and it would not sit on that land at all. That is fixed at source, and the wrong code
is on the block list so it cannot come back.

**What is not fixable at source is the stock.** JLCPCB carries the QFN variant as `C674164`
(LT8705AEUHF#TRPBF, 24.55 GBP) and `C580337` (LT8705AEUHF#PBF, 31.51 GBP), **both at stock 3**, against a
need of 5 for five boards. Read back from JLCPCB's parts API on 12 September 2026. So JLC cannot place
this part on five boards whatever else we decide.

**What I need from you, and why I am not deciding it myself.** The exclusion table in `make_handoff.py`
is the list of references JLC is told not to place, and it is on the never-auto floor because it decides
what is bought. Taking `U5` off the assembly is therefore yours, not mine. (Your 12 September ruling
delegated drafting and approving the order NOTES; it explicitly left anything that orders reserved, and
this orders.)

| option | what happens | cost |
|---|---|---|
| **A (recommended): U5 leaves the CPL, fitted by hand on all five boards** | JLC assembles everything around it; five controllers come from Mouser or Digi-Key and are soldered here. The stage is already described as bench-fitted in the schematic and in appendix 32.54 | five hand-soldered QFN-38 parts with an exposed pad, which is a reflow or hot-plate job, not an iron job. About 125 GBP of parts |
| B: assemble three boards and leave two without the tracker | no hand soldering of this part | two of the five boards cannot run the solar tracker, and the five boards stop being identical, which the kit's whole logistics story rests on |
| C: change the controller to a part JLC stocks in quantity | JLC places everything | a new device, new pin map, new compensation and a new footprint on a board that is otherwise finished. Days, and it reopens a settled stage |

**My recommendation is A.** The tracker is already the one stage on E the record calls bench-fitted, the
rest of E is unaffected, and it keeps the five boards identical. What it costs is a reflow step here,
which we will be doing anyway for the other hand-fit parts on the list (the Coilcraft inductors, the
Bourns choke, the Omron relay, the SA868).

**Until you rule, nothing moves:** `U5` stays in the exclusion table exactly as it is, the corrected code
`C674164` is in the generator so the deliverable BOM names the right part for whoever fits it, and the
certification table reads the row HAND_FIT with its purchase route.
