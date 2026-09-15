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

---

## Decision 13: seven of B's packer regions are smaller than the parts assigned to them, and have been since they were drawn (measured 12 September 2026, 17:55)

**This is the cause behind decision 11, and decision 11's answer did not reach it.** You ruled that the
CR2032 holder moves to GAP12. It moved, and B19's placed board went from 6 hard violations to 16, then
to 78 when the packer was taught to step around the parts that are already there. Reading why found
something older and larger.

**The packer prints `WARNING region X overflows by N mm` and then places the parts that did not fit
outside the rectangle, on top of whatever stands there. Nothing has ever read that line.** B19's
committed placement, the one every pair measurement of the last three days rests on, overflows six
regions already, `IOCA` by 10.2 mm.

| placement | regions that overflow | worst |
|---|---:|---|
| B19 as committed (b19cg24) | 6 | IOCA 10.2 mm |
| plus the two corrected TI land patterns | 7 | IOCA 15.1 mm |
| plus BT1 into GAP12 (your decision 11) | 8 | GAP12 22.9 mm |
| plus the packer stepping around fixed parts | 12 | GAP12 64.7 mm |

**GAP12 cannot hold the coin cell.** With the fixed parts respected it is 64.7 mm short, and the parts
that do not fit land on J_FAN2's header and inside the M.2 socket J_M2C1, which is what the 16 and the 78
are. The move you ruled is right and the room for it does not exist at the rectangle's current size.

**What I have done without asking, because none of it is reserved:** an overflow BLOCKS now, in all six
placement generators, through one shared gate (`tools/regionfit.py`). A board with a measured, benign
overflow declares the number in `tools/boards/<letter>.json` with its reason: **A declares 1.5 mm** (NODE
1.0, FES 1.4, and A24's placed board reads 0 hard at it) and **D declares 0.5 mm** (CTRL 0.2, same
evidence). C, E and P overflow nothing. **B declares nothing and is blocked**, which is the honest state.

**What is yours: the rectangles.** A region is the floor plan, with thermal, RF and assembly
consequences, and it is on the never-auto floor. (It was on the floor only in name until today: the
pattern matched the line the table opens on, so every rectangle in it was unprotected. Fixed, and B's
GAP12 was the change that found it.)

| option | what happens | cost |
|---|---|---|
| **A (recommended): give me a budget to resize the regions of one board at a time, reporting each change and its overflow before and after** | I size GAP12 for the coin cell and the six older overflows, each as a separate measured step, and B's placed board goes to its floor | B's placement moves, so the pair numbers are re-measured on it. That was already true after decision 11 |
| B: rule each rectangle yourself from the numbers | you hold the floor plan exactly | seven rectangles, and B is stopped until they are answered |
| C: leave the regions and drop BT1 from the board | the overflow drops back to the pre-existing six | no coin cell means no holdover clock across a power cut, which is what the DS3231MZ is for |

**My recommendation is A, bounded**: the regions of board B only, one change at a time, each reported
with its before and after overflow, and nothing touched on the other six boards. What it is not is a
free hand over the floor plan.

**Until you rule, B's chain blocks at the placement.** Everything else carries on: A and D declare their
measured numbers, C, E and P overflow nothing, and the D, E and P re-cuts are running.

---

## Decision 9 REOPENED, with the number it was ruled without: the 1.2 mm PWR class costs board D twenty-seven connections (measured 13 September 2026, 00:20)

**You ruled it on 12 September:** *"widen the class to 1.2 mm on the inner layers and re-route D; the
deliverable is re-cut."* The defect behind it was real and still is: D's 5 V rail carries 1 A through a 0.5 mm
class track and IPC-2221 rates that at 0.44 A on an inner layer. **What the ruling did not have was the cost,
because nobody had routed the board at the new width. Now it is measured.**

**D re-routed at 1.2 mm and stopped at twelve open connections, and all twelve are power nets**: `/+5V_D8`
six, GND three, `/+3V3_D8` two, `/PCM_VDD` one. D had reached 0 hard and 0 unrouted at 0.5 mm on 11 September.

**Two arms, one variable, same router invocation** (the first arm did not have that and its number was
withdrawn: it changed the width AND the invocation, so its 105 opens answered nothing):

| D, same placed board, same router call, 100 passes | hard | unrouted |
|---|---:|---:|
| PWR class **0.5 mm** | 0 | **105** |
| PWR class **1.2 mm** (your ruling) | 0 | **132** |

**So the width costs 27 connections of the 416 the board starts with.** Both numbers are far worse than the
production route's 12, which is routeflow with a `via_costs` rules file and its rounds doing their work; the
comparison that matters is the 27 between them, not either number against the production route.

**What 1 A actually needs, IPC-2221, so the options have a floor rather than a feeling:**

| where the rail runs | 10 K rise | 20 K | 30 K |
|---|---:|---:|---:|
| inner layer, 0.5 oz (JLC's four-layer stack) | **1.54 mm** | 1.01 mm | 0.79 mm |
| outer layer, 1 oz | 0.30 mm | 0.19 mm | |

Your 1.2 mm sits at about a 15 K rise on an inner layer. **0.5 mm was never defensible inside the board; on an
OUTER layer the same 1 A needs 0.30 mm and 0.5 mm was always fine there.**

| option | what happens | cost |
|---|---|---|
| **A (recommended): keep 1.2 mm and give me a placement pass on D** | the width stays where you ruled it, and the twenty-seven connections come back by making room rather than by narrowing copper | half a day on D's floor plan, and D's deliverable waits for it |
| B: 1.0 mm, a 20 K rise | about half the twenty-seven back for a hotter rail | a rail at 20 K over ambient inside a sealed case with no vents. I would not take this one |
| C: keep 0.5 mm on the inner layers and carry the rail in locked outer copper, the A21 pattern | the width question disappears: 0.30 mm suffices on an outer layer and the class stops deciding it | this is the architecturally right answer and it is a day on D, with `power_copper.py` already written for A |
| D: 1.2 mm and accept twelve opens | nothing to do | not an option: a board with open connections is not a board |

**My recommendation is A, with C as the thing to do if A does not close it.** The ruling was right; what it
needs is room, not a smaller number.

**This does not block anything else.** D is the only board affected, its deliverable is the one that waits,
and A24, E7, P3 and E5 are cut.

---

# OWNER RULINGS, 13 September 2026 00:40 CEST, asked as four questions and answered in one sitting

**All four went to the recommended option.** They are rulings, not recommendations, and they are not reopened
without a new one.

| # | question | RULING |
|---|---|---|
| **13** | who resizes board B's seven overflowing regions | **I resize them, board B ONLY**, one region at a time, each reported with its overflow before and after. Nothing on the other six boards is touched. The region rectangles of A, C, D, E, P and E5 stay on the never-auto floor |
| **12** | E's LT8705A, three in stock against a need of five | **U5 leaves the CPL and is hand-fitted on all five boards**, bought from Mouser or Digi-Key. About 125 GBP of parts and a reflow step, alongside the Coilcraft inductors, the Bourns choke, the Omron relay and the SA868 |
| **9** (amended) | D's 1.2 mm PWR class costs twenty-seven connections | **KEEP 1.2 mm and rearrange D's parts to make the room.** The width is not narrowed to suit the router; the twenty-seven come back from the floor plan. The locked outer-copper pattern (option C, board A's) stays available if the placement pass does not close it, and would be a new ruling |
| **8** (confirmed) | the order paperwork's approval step | **REMOVED, deliberately and on the record.** I draft the per-board notes, check them and apply them. **Nothing that orders changes:** the cart is untouched, the CPL exclusion table and the JLC rotation table stay reserved, and nothing is paid or submitted without the owner |

## What each of these commits us to

- **13** unblocks board B, which is roughly half the remaining work. Every region change is reported with its
  number, and B's placement moves, so its pair measurements are re-taken on the new floor plan. That was
  already true after decision 11.
- **12** closes board E completely: E7 is cut, and with `U5` out of the CPL the whole board is either bought
  from JLCPCB or has a written purchase route.
- **9** keeps the electrical margin and spends about half a day on D's layout. D's deliverable is the only one
  waiting on it.
- **8** is a change to the never-auto floor itself, not a one-off. `reserved.json`'s order class records it:
  the prose rows of `make_handoff.py` are off the floor, and `EXCLUDE`, `JLC_ROT`, `export_jlc.sh` and the cart
  are still on it. **The rule that nothing is ordered without the owner is untouched.**

---

## Decision 9, the cost re-measured on the production router path (13 September 2026, 02:55 CEST)

**You ruled to keep the 1.2 mm PWR class and rearrange D's parts, and that ruling stands. What follows is the
number it was ruled against, corrected, because it was measured through the wrong launcher.**

The 27 connections came from a pair of arms that both ran `route_pcb.sh`. That launcher routes in place and
does not ask for the per-pass session, so a capped run keeps whatever the last write left; the production
route runs `route_parallel.sh` into `route_one.sh`, which asks for a session every pass and imports the best
one. **Both pairs are internally honest, one variable each. They disagree about the size of the effect and
agree about its sign.** The pair below is the one that describes what the board will actually do, because it
is the path the deliverable is cut through.

| D, same placement chain, same router call, 100 passes, In1 as power layer, GND as a plane | hard | by type | unrouted | vias | route |
|---|---:|---|---:|---:|---|
| PWR class **0.5 mm** | **0** | none | **5** | 174 | 3 min |
| PWR class **1.2 mm** (your ruling) | **9** | clearance 2, shorting_items 6, solder_mask_bridge 1 | **11** | 192 | about 40 min |
| the same two through `route_pcb.sh`, 12 September | 0 / not read | | 105 / 132 | | |

**So the width costs six connections and nine hard violations, not twenty-seven connections.** The nine are
new information that no earlier arm reported: at 1.2 mm the rail tracks do not merely fail to close, they
**collide**, which is what `shorting_items 6` and `clearance 2` are. The route also takes about thirteen times
as long, which is the same congestion showing up as time.

**This does not change your ruling and it makes it cheaper than you were told.** Six connections and nine
collisions is half a day of floor plan, which is what option A was costed at. It does sharpen what the
placement pass has to achieve: it is not only opening six paths, it is giving the 1.2 mm copper somewhere to
run where it is not already touching something else.

**What I got wrong and how:** I compared today's 0.5 mm arm against the record's 27 and reported a
contradiction before checking that the earlier pair used a different launcher. The launcher is a third
variable across the two pairs, not within either. Both numbers stay on the record with their launcher named.

## Board C's last connection is narrower than its own class, and at the class width it does not close (13 September 2026, 02:55 CEST)

**Not a decision yet, a measurement you should have before C is finished.** `stub_router.py` had two class
lookups and both were dead: `netobj.GetNetClass()` raises on KiCad 9, and the project-file fallback written on
7 September to repair that was nested inside the same `try`, after the raising line, so it never ran on any
board. Every stub closure since has been laid at the default **0.25 mm** with a 0.6/0.3 mm via, whatever the
net's class asked for.

**On C that matters.** `/+3V3` is in class RAIL, whose width is **0.5 mm** and whose via is 0.8/0.4 mm. C10's
recorded "0 hard, 1 unrouted", its best result ever, was reached by closing `/+3V3` at **half its class
width**. With both lookups alive the same closure is refused: the 0.5 mm track and the 0.8 mm via do not fit
where the 0.25 mm track and the 0.6 mm via did.

**So C10 is two connections open at the width its own class declares, not one.** That is consistent with what
the record already suspected about this board: `/+3V3` at U3 pad 10 is a **placement** problem, not a closure
one. Nothing is decided here and C's regions stay on the never-auto floor; when C comes up, the question will
be whether to give U3 room or to declare the rail narrower, and the second is a class change, which is yours.

## Decision 14: twelve rails on four boards carry more current than IPC-2221 allows, and the check that says so has never gated anything (measured 13 September 2026, 03:00 CEST)

**This is the one thing I found today that touches boards you would order, so it needs you rather than me.**

`dc_drop.py` computes two numbers per rail: the voltage drop, which decides the verdict, and the worst current
density, which is printed and ignored. The printed comment since 8 September says the density "overstates by
the cell-to-width ratio" and is "reported, not gated, until the raster is validated". **The raster has now been
validated and the direction was backwards.**

The bar is IPC's current for one raster cell's cross-section. IPC-2221 is `I = k dT^0.44 A^0.725`, sublinear in
area, so N cells each at their own limit carry `N^0.275` times what IPC allows the whole track. Measured with
the tool's own function at a 0.5 mm cell: **exact at 0.5 mm width, and lenient by +18 percent at 0.4 mm, +21 at
1 mm, +64 at 3 mm, +65 at 0.25 mm, +94 at 0.2 mm, +98 at 6 mm.** So every rail below is over a bar that is
already too generous, and its number is a floor.

| board | rail | worst density | the (lenient) bar | over by |
|---|---|---:|---:|---:|
| A24 | VBAT | 428.2 A/mm2 | 52.0 | **8.2x** |
| A24 | VBUS20 | 217.4 | 82.7 | 2.6x |
| A24 | +13V8_PA | 172.5 | 82.7 | 2.1x |
| A24 | +12V_HF | 131.6 | 52.0 | 2.5x |
| A24 | VIN_RAW | 130.9 | 82.7 | 1.6x |
| A24 | +5V_S1, +5V_S2, +5V_S3 | 83.2, 83.2, 83.1 | 82.7 | 1.01x |
| E7 | VIN_RAW | 279.2 | 82.7 | **3.4x** |
| E7 | CELL_F | 102.0 | 52.0 | 2.0x |
| P3 | PACK_P | 241.1 | 82.7 | 2.9x |
| P3 | FUSED | 193.2 | 82.7 | 2.3x |
| P3 | CELL4 | 87.4 | 82.7 | 1.06x |

**Every one of them reads MET, because the drop decides and the drop is fine.** A24's VBAT drops 148 mV of a
2 percent budget while its worst cell carries eight times what that cell may carry: a rail can be electrically
quiet and locally too hot at the same time, which is exactly what a density check is for.

**P3's FUSED at 193.2 is the number that became your ruling 7**, the 2 oz order. The same class of number was
sitting in the log for A24 and E7 and nobody escalated it, because nothing reads the line.

**What I have NOT done:** turned the density into a verdict. That would refuse A24, E7 and P3 today, all three
of which are cut, and it changes what "MET" means, which is yours. The corrected direction and its measurement
are in the tool and in a rule that fails if the sign is ever claimed the other way.

| option | what happens | cost |
|---|---|---|
| **A (recommended): gate the density and re-cut the three boards** | the boards that ship carry copper IPC agrees with | the three deliverables re-open; A24's VBAT needs real work at 8.2x, E7 and P3 are mostly the 2 oz question you already ruled on |
| B: gate it at a declared rise above 10 K, per rail with its reason | 20 K costs about a third of the width, 30 K about half; a sealed case with no vents makes a high rise expensive | half a day, and every rail needs a written rise |
| C: leave it reported and order as it stands | nothing to do now | a prototype run that may run hot at the necks, found on the bench instead of on the screen. For five boards of a prototype this is defensible, and it should be a decision rather than an omission |

**My recommendation is A for A24's VBAT specifically, and B or C for the rest**, because 8.2x is a different
kind of number from 1.01x and only the first four rows are clearly worth a re-cut.

## Decision 9, third reading: the 1.2 mm class is wider than 191 of the 230 pads it has to reach (measured 13 September 2026, 03:05 CEST)

**Your ruling says "widen D's PWR class to 1.2 mm ON THE INNER LAYERS". The class carries ONE width for every
layer, so it was applied everywhere, and on the outer layers that is the whole problem.**

| D, class PWR at 1.200 mm | pads on the class's nets | narrower than the class | narrowest |
|---|---:|---:|---|
| | **230** | **191, on 124 parts** | **0.25 mm** |

A track wider than the pad it leaves spills past the pad edges, and that is precisely what the nine hard
violations are. All nine sit at ONE place, D2's relay diode: `/RLY_K` and `/+3V3_D8` on B.Cu at (81, 106),
six `shorting_items`, two `clearance` at 0.0986 and 0.0779 mm against the class's own 0.127, and one mask
bridge. D2 is a SOD-123 with **0.90 mm pads**. U1, a SOT-23-5 whose `/+5V_D8` sits on pads 1 and 3 with GND
between them at **0.95 mm pitch and 0.60 mm pads**, accounts for one of the opens: two 1.2 mm tracks cannot be
0.95 mm apart at any clearance.

**So "rearrange D's parts" cannot close this, and that is why the packer-gap arm failed.** Moving a SOT-23-5
does not widen its pads. On 83 percent of this rail's pads the class width does not fit the land it has to
land on, whatever the floor plan.

**The inner layers have no pads at all, only vias.** Your ruling as written has no conflict anywhere: the
1.2 mm belongs where you put it, and the outer layers need 0.30 mm for 1 A at 1 oz and had 0.5 mm already.

**What it takes to implement it as written.** A KiCad net class has one track width, and Freerouting takes that
one number from the DSN, so per-layer width is not expressible as a class. The rail is carried at 1.2 mm on the
inner layers as locked pre-routed copper, which is `power_copper.py`, board A's pattern, with the class left at
0.5 mm so the router can still reach a 0.25 mm pad. **That is option C of the first reading, which you said
stays available and would be a new ruling. This is me asking for that ruling, with the number that forces it.**

| option | what happens | cost |
|---|---|---|
| **C (recommended now): class back to 0.5 mm, the rail carried at 1.2 mm in locked inner copper** | your ruling implemented where you actually put it, and the router keeps a width that fits a 0.25 mm pad | a day on D with `power_copper.py` already written; D's deliverable waits for it |
| A (the standing ruling): keep 1.2 mm on every layer and rearrange parts | cannot work: 191 of 230 pads are narrower than the class and a floor plan does not change a pad | the half day would be spent and the nine violations would still be there |
| B: 1.2 mm class with a taper at every pad | the tool would have to lay a pad-width stub and widen away from it, for 191 pads | new work in `escape.py` for wide classes, and 191 tapers is a lot of copper nobody has checked |

**What I got wrong:** I read the standing ruling as a floor-plan problem and spent a packer-gap arm on it before
measuring the pads. The pad measurement takes ten seconds and would have said the floor plan was the wrong
lever. The arm is on the record with its numbers either way.

---

# OWNER RULINGS, 13 September 2026 11:20 CEST, asked as three questions and answered in one sitting

**All three went to the recommended option. They are rulings, not recommendations, and they are not reopened
without a new one.**

| # | question | RULING |
|---|---|---|
| **15** | how ruling 9 is implemented, now that the 1.2 mm class is wider than 191 of D's 230 pads | **OPTION C: the PWR class goes back to 0.5 mm and the rail is carried at 1.2 mm on the INNER layers as locked pre-routed copper**, board A's `power_copper.py` pattern. This is ruling 9 implemented where it was actually put. The electrical margin is kept and the router can still reach a 0.25 mm pad |
| **16** | the current density that has never gated anything, twelve rails over a bar that is itself lenient | **GATE IT, and re-cut the worst.** The density becomes a verdict. A24 is re-cut for VBAT at 8.2x, VBUS20 2.6x, +13V8_PA 2.1x and +12V_HF 2.5x; E7 and P3 are largely the 2 oz question already ruled in 7. The three deliverables re-open |
| **17** | board C's U3, whose `/+3V3` will not close at its own class width | **C's regions are RELEASED to the session, board C ONLY**, on decision 13's terms: one region at a time, each reported with its overflow before and after, and nothing on the other boards touched |

## What each of these commits us to

- **15** unblocks D. `power_copper.py` exists and is proved on board A; what is new is applying it to an inner
  layer rather than an outer one, and D's deliverable is re-cut after it. The 0.5 mm class is what the ROUTER
  sees; the 1.2 mm copper is laid before it and locked, so the router never has to fit a 1.2 mm track to a
  0.25 mm pad. **Ruling 9 is not weakened: the rail still carries 1 A in 1.2 mm of inner copper.**
- **16** re-opens A24, E7 and P3, which were the three cut deliverables. It is the largest piece of work of the
  three and it is the one that touches what would be bought. A24's VBAT at 8.2x is the real item; E7 and P3
  should mostly fall out of the 2 oz stackup that ruling 7 already ordered, and that is measured rather than
  assumed before any copper moves.
- **17** unblocks C on the same terms as B. **Boards A, D, E, P and E5 keep their regions on the never-auto
  floor**, and so do B's and C's once their overflow reads zero.

## A CORRECTION TO RULING 15, found while building it (13 September 2026, 11:40 CEST)

**1.2 mm of inner copper does not carry 1 A.** JLC's four-layer stack is 0.5 oz inner, and IPC-2221 at a 10 K
rise gives:

| for 1.0 A | 10 K | 20 K | 30 K |
|---|---:|---:|---:|
| inner 0.5 oz (JLC four-layer) | **1.56 mm** | 1.03 mm | 0.80 mm |
| outer 1 oz | **0.30 mm** | 0.20 mm | 0.15 mm |

| what a width carries at 10 K | inner 0.5 oz | outer 1 oz |
|---|---:|---:|
| 0.50 mm | 0.44 A | **1.45 A** |
| 1.20 mm | **0.83 A** | 2.73 A |
| 1.56 mm | 0.99 A | 3.27 A |

**So ruling 9's 1.2 mm was already short on an inner layer**, at about a 15 K rise rather than 10 K, and
**0.5 mm on an OUTER layer has always been fine for this rail, with 45 percent margin.** The defect ruling 9
was written against is real and is specifically an INNER-layer defect: the router put a 1 A rail on In2 at
0.5 mm, which IPC rates at 0.44 A.

**And ruling 15 is recorded in my wording, not the original option C's.** The first reading of decision 9 said
option C was *"keep 0.5 mm on the inner layers and carry the rail in locked OUTER copper, the A21 pattern"*.
The third reading, which is what was ruled on, said "locked inner copper". The owner chose option C and the
A21 pattern, and the A21 pattern is outer bands with inner feeds; the physics above says outer is also the
right answer. **The substance the owner chose is unchanged; the layer in my sentence was wrong.**

**What this changes in the build:** the PWR class goes back to 0.5 mm either way, and `+5V_D8` is carried from
`J_PWR1` to its consumers in locked copper. The question is only which layer that copper is on, and the
numbers above say the outer layers, because 1.2 mm of inner copper is 0.83 A and 0.5 mm of outer copper is
1.45 A. Taking the rail off In2 is also exactly what `dc_drop` is refusing: its worst cell for `+5V_D8` is
**In2 at 73.0 A/mm2 against 52.0**.

**RULING 15 AMENDED, 13 September 2026 11:45 CEST, asked as one question and answered:** **the locked copper
goes on the OUTER layers**, as option C originally said. The PWR class returns to 0.5 mm and `+5V_D8` is
carried from `J_PWR1` to its consumers in locked F.Cu and B.Cu bands with stitched crossings, so no part of
the 1 A path runs in a 0.5 oz inner track. The substance of ruling 15 is unchanged; the layer in my sentence
was wrong and is corrected here rather than built.

---

# OWNER RULINGS 18 and 19, 13 September 2026 13:00 CEST, two questions and both to the recommendation

| # | question | RULING |
|---|---|---|
| **18** | how board B gets past 37 of 113 pairs, now that the knobs AND the placement lever are both spent | **A FLOOR PLAN BUILT AROUND THE PAIR CORRIDORS.** B is re-placed with the pair corridors as the primary constraint instead of region packing. Two to three days on B alone, and every pair number is re-measured from scratch afterwards. The pair ruling of 10 September is unchanged: no per-pair exception, no coupled-fraction gate |
| **19** | how strict the density gate is, given that its own bar is lenient by 18 to 98 percent | **UNDER 1.1x COUNTS AS MET**, with the reason recorded. A 0.6 percent exceedance of a bar that is itself 18 to 98 percent generous is inside the instrument's own error and is not worth a board re-cut. Everything above 1.1x still fails and still gets fixed |

## What each commits us to

**18 is the largest single piece of work left in the project and it was chosen with its cost stated.** The
evidence that forced it: seven arms at the peak slack moved the pair count by nothing; the couple gap was
worth +8 once and nothing since; and decision 13's region resizes took B's placed board from 150 hard
violations to **0** while the pair count stayed at **37 of 113, to the pair**. 30 of 46 leg refusals are
within 2 mm of the pair's own pads and 22 of 22 retries were refused within 0.3 mm of the first, so no search
can move a straight entry run between two fixed points. **The only thing left that changes the geometry the
search is given is where the parts are**, and that is what this ruling buys. The coupled-fraction gate was
offered a second time with new evidence and refused a second time; it is not offered again.

**19 changes what MET means and is recorded as such.** The bar is IPC's current for ONE raster cell, measured
lenient at every width but exactly one cell: +18 percent at 0.4 mm, +21 at 1 mm, +64 at 3 mm, +65 at 0.25,
+94 at 0.2, +98 at 6 mm. A rail inside 1.1x of that bar is inside the measurement's own uncertainty. **On
A24 this passes the three slot rails at 1.006x and changes nothing else**: VBAT at 8.2x, VBUS20 at 2.6x,
+13V8_PA at 2.1x and VIN_RAW at 1.6x still fail. E7's two rails and P3's two rails are all above 1.1x and are
untouched by it.

---

# OWNER RULINGS 20 and 21, 13 September 2026 13:25 CEST

| # | question | RULING |
|---|---|---|
| **20** | ruling 19's tolerance, whose stated reason I got wrong | **SIZE THE TOLERANCE TO THE REAL CAUSE.** The legitimate error is the raster's own discretisation of a track's true width, not "uncertainty" in the bar. Measure what that is worth and set the tolerance to it. The number stops being one I picked |
| **21** | one order or six boards ahead of B | **ONE ORDER, WHEN ALL SEVEN ARE READY.** One shipment, one set of fees, both free confirmations used once, and every cross-board contract judged against boards that all exist. The six wait for B |

**Why 20 was asked at all.** Ruling 19 was ruled on a rationale I wrote and tier 2b refuted the same hour: what
the leniency measurement shows is a **bias in one direction**, the per-cell bar being 18 to 98 percent too
generous, not noise about it. A rail 0.6 percent over such a bar is genuinely over IPC, and at exactly one cell
width the bar is EXACT, where a 1.1x tolerance is ten percent over IPC outright. **There is still a real error
source, the 0.5 mm raster against a track's true width**, and that is what the tolerance is now sized against
rather than a figure chosen to clear the three rails in front of it.

**21 keeps the plan as one set.** It costs the six boards a few days waiting on B's floor plan, and it means
the cross-board contracts are checked against seven boards that exist rather than six plus a file.

## OWNER RULING 22, 13 September 2026 13:40 CEST

**BUILD THE CONDUCTOR-BASED DENSITY MEASURE.** A rail is judged by the narrowest piece of copper carrying a
meaningful share of its current, that current against IPC-2221 for that piece's own cross-section. No grid, so
it converges by construction. It settles rulings 16, 19 and 20 together and it answers `CELL+` and `+5V_DEV`,
the two A24 rails whose verdict currently depends on a parameter nobody chose on physical grounds.

**The evidence pointed at the split to build.** In 32.162 the rails that barely move with cell size, VBAT at
+6 percent and +13V8_PA at -9, are the ones carrying their current in **planes and bands**, which a 0.5 mm
cell resolves. Every rail that moves by half carries it in **tracks narrower than the cell**. So the raster is
sound where the copper is wide and wrong where it is narrow, and the new measure is aimed at exactly that.

---

## DECISION 23, OPEN: ruling 9's 1.2 mm is sized for a current D's rail does not carry in one place (13 September 2026, 14:40 CEST)

**This does not reopen ruling 9. It puts a number in front of it that did not exist when it was ruled**, and
the number changes what the ruling costs by two thirds. D is blocked either way until you answer.

**What was known when you ruled.** `+5V_D8` is a 1 A rail; IPC-2221 gives 1 A on 0.5 oz inner copper a width
of **1.56 mm** at a 10 K rise, so 1.2 mm was the practical call and the 0.5 mm it had was rated 0.44 A. The
cost measured afterwards: **191 of the 230 pads on the PWR class's nets are narrower than 1.2 mm, on 124
parts, the narrowest 0.25 mm**, and a track wider than its pad spills past the pad edges. All nine hard items
of the 1.2 mm arm sat at one place, D2's SOD-123 with 0.90 mm pads.

**What is known now.** The rail's loads are declared, so the current is no longer split evenly over every part
on the net by a guess. Measured on the cut D10 board with the corrected conductor pass, **the worst single
piece of copper on this rail carries 0.53 A, not 1.0**: the 1 A is the rail's total and it divides among the
loads well before the narrowest track. IPC gives 0.53 A **0.65 mm**.

**And the cost falls with it, counted on D10's own pads:**

| class width | pads narrower than it | parts affected | what it carries on 0.5 oz inner |
|---|---:|---:|---|
| 0.50 mm (today) | 16 of 230 | 4 | 0.44 A, under the measured 0.53 |
| **0.70 mm** | **70 of 230** | **31** | **0.61 A, over the measured 0.53** |
| 1.00 mm | 167 of 230 | 109 | 0.86 A |
| 1.20 mm (ruled) | 191 of 230 | 124 | 1.05 A |

**Option A, recommended: the PWR class goes to 0.70 mm.** It covers the current the rail actually carries with
margin, and it touches 70 pads on 31 parts instead of 191 on 124. The nine hard items of the 1.2 mm arm came
from tracks spilling past small pads, and at 0.70 mm the four parts with pads under 0.5 mm are the only ones
that can still do it.

**THE ROUTE COST IS MEASURED, all three widths through one identical script, one variable, same placed board:**

| PWR class | hard | unrouted | vias |
|---|---:|---:|---:|
| 0.50 mm (today) | 1 (one clearance) | **2** | 171 |
| **0.70 mm** | **0** | 4 | 187 |
| 1.20 mm (ruled) | 2 (two clearance) | **15** | 182 |

**0.70 mm is the only one of the three with no hard violation at all**, and it costs two connections against
today's 0.50 mm where the ruled 1.2 mm costs thirteen. The 1.2 mm figures recorded on 13 September (hard 9,
unrouted 11) came from another session's invocation; through this one it is hard 2 and unrouted 15, which is
the same conclusion by a different route and is why all three were re-run rather than two.

**The first attempt at the 0.70 arm is withdrawn.** It came back hard 0
with 121 unrouted and FOUR vias, and the cause was the arm rather than the width: it set neither
`FR_POWER_LAYERS` nor `FR_PLANE_NETS`, which D's own route profile declares as `In1.Cu` and `GND`, so every
ground pin went into the wire list at the class width instead of being reached by vias through a plane. That
is a second variable and the number measures nothing. Both widths are running again through one identical
invocation, which is the only comparison either supports.

**Option B: keep 1.2 mm as ruled.** It is the width for the whole rail in one conductor, which is the
conservative reading and needs no new argument. It costs six connections and nine hard items measured, and
"rearrange D's parts" cannot close it, because moving a SOT-23-5 does not widen its pads.

**Option C, from the 13 September batch and still open: the class goes back to 0.5 mm and the rail carries its
current in locked inner copper**, the A21 pattern, `power_copper.py`. The class then only has to carry what
the router lays between the copper and the pads.

**Option D: 0.70 mm now, and the copper of option C later if a measurement asks for it.** This is option A
with the door left open, and it is what I would do if the answer were mine.

## DECISION 24, OPEN: board B lays 65 of its 113 pairs, and the pair hold releases no board under 113 (13 September 2026, 22:50 CEST)

**What the hold says.** Owner ruling 10 September 02:00: *every board is held until the pre-router lays every
pair*, no per-pair exception, and the session's own recommendation at the time (gate the controlled fraction at
80 percent) was NOT taken. A, C, D, E and P each carry three to five pairs and meet it. **B carries 113.**

**Where B stands today, measured on the tools that would cut its deliverable** (appendix 32.174): **65 of 113**,
up from 38 this morning, on two changes that are in the tree and graded:

| change | of 113 | what it is |
|---|---:|---|
| this morning | 38 | the board as the record last measured it |
| `PAIR_END_FIT` | 54 | the end emissions asked about the partner BEFORE they are laid; 84 of 152 failed attempts were the pair's own two legs missing by 1 to 15 micrometres |
| corridor slack 0.06 to 0.08 | **65** | the curve re-swept on those tools, eight arms; the declared 0.06 turned out to be the worst point of the sweep |

**The 48 that remain are named**: 18 `no stub path at via` (the leg cannot reach its own escape via through
the fan), 8 the pair's own legs, 8 the two legs crossing, 6 at U209, the rest at U3, U4 and out in the
corridor. **They concentrate at the three PCIe switches, the two M.2 card sockets and the USB muxes**, which is
the station neighbourhood rather than the corridor.

**Ruling 18's floor plan was tried and the board refused it.** Making each fine-pitch front part's courtyard an
obstacle to the underside regions (the rule this board's own generator states in a comment, and breaks 71
times) overflows five regions, the worst by 86.2 mm: the underside region rectangles ARE the IC pockets on the
other side, and the parts under them are the decoupling the 3 mm rule wants there. **The underside of a
three-slot compute board is the decoupling of its three slots**, so there is no elsewhere to put it inside the
present outline.

**Three options, with what each costs.**

1. **Keep grinding the pre-router.** Today's two changes were worth +27 between them and each took an evening.
   The next named causes are the stub into a fan (18) and the leg crossing (8). Nothing says how many of the 48
   are reachable this way, and the last three knobs measured before today were each worth zero.
2. **Gate the controlled fraction** (the 9 September recommendation, refused then): a pair passes when 80
   percent of its judged length is coupled, the router laying the last millimetre into the fan. It ships B at
   its present placement, and it is a change to what "controlled impedance" means on this board.
3. **Give B more board.** The pairs fail where 133-pad 0.40 mm parts sit 17 mm apart with their decoupling
   underneath. A larger outline, or four slots' worth of area for three slots, is the placement answer that
   ruling 18 asks for and the present 330 by 200 mm cannot give.

**Recommendation: 2, with 1 continuing underneath it.** The impedance gate reads back what was laid either
way, so the number in the record stays true; what changes is the bar a pair must clear to ship. **Nothing is
being weakened while this is open: B stays held, and the other six boards are unaffected.**

## DECISION 25, OPEN: board A's USB_WALL pair is 1.47 mm apart and nothing in the tree can close it (14 September 2026, 07:55 CEST)

**The gate.** Owner ruling 5 September 17:00: a differential pair over **1 mm** of intra-pair length mismatch
blocks the chain, and the session never hands the stop to the owner. A24 met it (0.23, 0.13, 0.00 mm). A27
does not: after the density copper of 32.172 and 32.176 the same three pairs come out at

| pair | P | N | apart |
|---|---:|---:|---:|
| USB_D8 | 140.29 | 138.52 | **1.78 mm** at the old corridor slack; **inside 0.5 mm** at the new one, so it is answered |
| USB_WALL | 36.04 | 37.51 | **1.47 mm**, at both slacks |
| USB_E6 | matched | | |

**What was tried, in order, and what each said.**

1. **`meander.py`**, the tool written for this in September: it placed nothing, three rounds running, because a
   pair the pre-router lays end to end has **no unlocked copper** and this tool only ever touched unlocked
   track. It is given the locked copper now (`MEANDER_LOCKED`, guarded by the DRC as before) and still places
   nothing.
2. **A length matcher in the pre-router itself** (`PAIR_LEG_MATCH`, new today): it measures the whole net, not
   just what the pass laid, because **the mismatch is half in the escape stubs** (0.61 mm) and half in the
   corridor run (1.17 mm). It proposes bumps on the short leg's own copper, on the side the partner is not on,
   and every one is judged before it exists. On A **every bump is refused by the leg's own map**: A's pair
   corridors have no free copper beside them. The tool names that refusal rather than saying "no room".
3. **A wider corridor** (slack 0.30 against the default): the same 3 of 3 pairs, and **USB_D8 falls inside
   half a millimetre by itself**, which is the fix for that pair and is declared in `boards/a.json`.
   USB_WALL does not move: 23 of its 36 mm sit within 2 mm of a pad, in the wall connector's own fan, where
   nothing is free.

**What 1.47 mm is, electrically.** USB_WALL is a USB 2.0 pair at 480 Mbit/s. 1.47 mm of FR-4 is about **10
picoseconds**, against a unit interval of 2,083 ps and a USB 2.0 intra-pair skew budget of 100 ps. It is a
number this project's own gate refuses and the standard does not.

**Three options.**

1. **Raise the gate for the USB class only**, to 3 mm, with the timing argument above written into the rule.
   The 90 and 100 ohm DIFF100 classes keep 1 mm. Cost: one line in the gate and a sentence in the record;
   board A ships.
2. **Equalise the escapes** (`escape.py` gives a pair's two pads the same escape length on coarse-pitch parts).
   It is the honest structural fix for the 0.61 mm half, it does not touch the fine-pitch rows where the
   record already refused this on measurement, and it changes a tool every board uses: a day with its own
   measurements on all seven.
3. **Keep routing A** and hope a route lands inside 1 mm. Three rounds today did not; the mismatch is
   geometry this pass reproduces exactly, so this is the option with the least evidence behind it.

**Recommendation: 1, with 2 done afterwards on its own merits.** Nothing about the board changes under option
1; what changes is the bar, and the bar is currently stricter than the standard by a factor of ten.
**A is otherwise finished**: 0 hard, one connection open at the last count, every rail measured on the fill it
is cut with, and its copper answers all four density findings.

## DECISION 26, OPEN: board C is one connection short and no tool in this tree can close it (14 September 2026, 10:55 CEST)

**Where C stands.** C11 routes to **0 hard and ONE unrouted**, passes `check_pcb_c` ALL PASS on the refilled
board, `dc_drop` 1 of 1 rail MET, `impedance` (no pair on this board carries a target, declared that way in the
schematic), and `check_contracts` ALL PASS. The deliverable is refused for that one connection, and the gate is
right to: the set's own definition of clean is 0 unrouted.

**The connection is `/EPD_SDA`**, from J_EPD pin 14 at (225.75, 116.95) to U3 pad 5 at (420.89, 273.95): **249
mm across the panel**, both ends already escaped to their own vias, and not one millimetre of it laid. The
panel is a U with the display window through the middle, so that connection has exactly ONE corridor: east
along the top strip, then south down the right strip. Drawn and read on both routing layers, **that corridor is
a dense parallel bundle** of the panel's other signals.

**Everything that was tried, and what each said.**

| attempt | result |
|---|---|
| 30-pass route (C11 round 1) | 7 unrouted; the finish closed 6 |
| `via_costs` remedy round (C11 round 2) | **3 unrouted**, the finish closed 2: the board's best, ONE open |
| continuation, 8 passes in 3600 s (its budget corrected from 80 passes in 900 s, which bought ONE pass) | 3 in, 3 out |
| stub router, window scale 25, grid 0.2, 80 M nodes (the A22 recipe) | closed the other two, `FAILED: /EPD_SDA track -> track` |
| stub router, the same window at **grid 0.1** | the same: it closes the other two and refuses this one |
| **45-pass route (C12 round 1)** | **12 unrouted**: more passes made it worse |
| C12 round 2 with `via_costs` | 4 unrouted, the stub router closed 2, leaving **two** |

**What that adds up to.** A search on a 0.1 mm grid over the whole board, on all three routing layers, finds no
path: the lane is not there to be found, so this is not a closure problem and no amount of stub searching will
make it one. The router itself, given 45 passes and a via-cost remedy, does not free one either.

**Three options.**

1. **A placement change on C**, which is what the record has said about this board twice (C10's last connection
   was also at U3, walled in by its own package). Moving U3 or J_EPD, or splitting the bundle so one lane is
   free, is a day with a re-route behind it.
2. **Rip up a neighbour by hand** and let the router lay both: `unknot` does this for a router knot, but
   choosing which net to sacrifice is a judgement nothing in the tree makes.
3. **Ship C with the connection made as a wire link** on the assembled board, declared in the assembly notes.
   It is a panel backer, the signal is an I2C SDA line to the e-paper at 400 kHz, and a 250 mm wire is
   electrically unremarkable. Cost: a hand-soldered link on five boards and a line in `ASSEMBLY.md`.

**Recommendation: 1, and 3 only if the schedule forces it.** C is otherwise finished, and the board is already
laid out around a display window that leaves it one corridor: the next C phase should widen that corridor
rather than keep asking the router for a lane that is not there.

### DECISION 25 IS CLOSED AND NEEDS NOTHING FROM YOU (14 September 2026, 12:05 CEST)

**The gate was never the problem and the 1 mm bar stands.** `meander.py` was refused by a condition in its own
code, not by board A. `MEANDER_LOCKED`, written yesterday so that a pair the pre-router lays end to end can
still be lengthened, was gated on the net having **no unlocked copper at all**. That was a hypothesis about
what "laid end to end" means, and the board says otherwise: `/USB_D8_N` carries 12 segments totalling 138.54 mm
of which **four are unlocked, at 0.03, 0.00, 0.00 and 0.00 mm**, the router's own zero-length junction pieces.
Four pieces of nothing were enough to keep the branch shut, so three rounds of length matching chose between
them and reported "could not place the last 1.78 mm".

**Measured on A27's own board, all four legs read the same way:**

| leg | unlocked, longest | locked, longest | windows found, before | after |
|---|---:|---:|---:|---:|
| USB_D8_N | 0.03 mm | 109.45 mm | 0 at every amplitude | 2 |
| USB_D8_P | 0.02 mm | 109.63 mm | 0 | 2 |
| USB_WALL_P | 2.27 mm | 8.33 mm | 0 | 2 |
| USB_WALL_N | 2.27 mm | 8.87 mm | 0 | 3 |

**With the locked copper offered alongside the unlocked, the gate passes on the board as cut**, in one round,
with the DRC deciding as it always has:

```
meander: USB_D8_N +1.78 mm as 1 bump of 0.89 mm on F.Cu, 0.00 mm still to place
meander: USB_WALL_P +1.50 mm as 1 bump of 0.75 mm on F.Cu, 0.00 mm still to place
pair_match: every pair within 1 mm (round 2)
PASS USB_D8 140.32 / 140.32 mm, 0.01 mm apart
PASS USB_E6 200.25 / 200.38 mm, 0.13 mm apart
PASS USB_WALL 39.50 / 39.50 mm, 0.00 mm apart
hard 0, unrouted unchanged
```

**So no option is taken and no bar moves.** Option 1 (a 3 mm gate for the USB class) is withdrawn: the 1 mm
ruling holds on every board and A meets it. Option 2 (equalising a pair's two escapes in `escape.py`) stays
worth doing on its own merits and is not needed by any board today. What this cost is two hours and it is the
second time this week that a tool reported a board's limit when it was reporting its own.


### DECISION 24, THE FLOOR PLAN MEASURED A SECOND TIME AND BOARD B REFUSES IT AGAIN (14 September 2026, 13:55 CEST)

**Ruling 18 asked for a floor plan built around the pair corridors. Both ways of asking the packer for one are
now measured on today's tree, and the board refuses both by the same mechanism.**

| arm | what it asks for | what the board says |
|---|---|---|
| `PLACE_NO_UNDER_FINE=1` | no back-side part under a fine-pitch front part, which is this generator's own written rule and it breaks it 71 times | **5 regions overflow, the worst by 86.2 mm** |
| `PLACE_FINE_MARGIN=2.6` | the room `place_audit`'s own escape envelope wants at a 99-pad QFN, against the 1.6 it gets | **9 regions overflow, the worst by 8.4 mm** |

**86.2 mm is not a rectangle that can be redrawn.** The underside regions ARE the IC pockets of the other
side, and the parts in them are the decoupling those ICs need within 3 mm. The underside of a three-slot
compute board is the decoupling of its three slots, so there is no elsewhere inside this outline. Decision 13
released B's rectangles and that is not the constraint: the constraint is area.

**What did move today, measured with a control arm beside every experiment:**

| arm | of 113 | DIFF100 | USB |
|---|---:|---:|---:|
| control, today's tree | **62** | 35 | 27 |
| the obstacle map at the nets' own class clearances | **64** | 37 | 27 |
| the layer change judged before it is laid, class bar | 58 | 36 | 22 |
| the layer change judged before it is laid, fold bar | 57 | 33 | 24 |

The class-aware map is +2 and is declared for B; it is the correct model rather than a lever, because KiCad's
rule is that the clearance between two items is the larger of their two classes' and the map was using one
literal for every net on every board. The layer-change test costs pairs at either bar and is off.

**A CORRECTION THAT MATTERS TO EVERY NUMBER IN THIS FILE.** The control says **62** where this board's record
carried **71** last night. The generators moved between the two, so 71 is not reproducible on today's tree.
Appendix 32.109's caution, word for word: the baseline also moved because the board did. Every comparison from
here is against a control arm run beside the experiment, never against a remembered number.

**So decision 24 stands exactly as written, with one option fewer.** Option 1 (keep grinding the pre-router)
is what today bought +2 from. Ruling 18's floor plan, option 3's "give B more board", is the same request in
two forms and the packer has now said so twice with a number. Options 2 and 3 are yours; nothing is being
weakened while this is open, B stays held, and the other six boards are unaffected.

### DECISION 26, THE SIX ROUTES OF BOARD C IN ONE TABLE (15 September 2026, 01:55 CEST)

Nothing here needs a ruling of yours that the section above did not already ask for; this is the evidence that
has accumulated since it was written, so that the decision is taken on the whole of it.

| route | what changed | router left | the finish left | which nets |
|---|---|---:|---:|---|
| C11 | 30 passes, then `via_costs 100` | 3 | **1** | `/EPD_SDA` |
| C12 | 45 passes, then `via_costs 100` | 4 | 2 | `/PWM1`, `/HB2` to its test point |
| C13 | rip-up cost 10 | 59 | | |
| C14 | 30 passes with `via_costs 100` from the first round, then 39 | 4 | **2** | `/EPD_SDA`, `/HB3` to its test point |
| C15 | C14 plus `/EPD_SDA` pre-laid on the placed board | 10 | 8 | the bus's other lines, the switch lands, `/GPS_A` |
| C16 | C14 plus the whole six-wire e-paper bus pre-laid (5 of 7 laid) | 15, 16 | 13 | |

**Every net C fails to route is one of two kinds:** a long panel line from the RP2040 in the right strip to the
top strip (the e-paper bus, `/PWM1` to the LED rail switch in the left strip), or a branch to a test point or a
switch land in the bottom strip. **Pre-laying the long lines makes the board worse, twice**: a lane taken by
hand on a board whose strips are its only corridors is a lane the router loses, and it loses two or three more
for it. The stage exists and is declared for no board.

**So the board that stands is C14's: 0 hard, 2 unrouted, committed (sha256 c23512db603477852b4f).** Its two
opens are `/EPD_SDA`, 249 mm and one corridor, and `/HB3` to TP30, 57 mm from the net in the bottom strip.
The second kind is a placement fact that needs no ruling: the panel's test points sit in a row in the bottom
strip and the nets they tap run in the top and right strips, and a test point placed beside its net is a
millimetre of track. That change is in C's generator and is the next thing built. The first kind is the
decision above, unchanged: a placement that gives the panel a second corridor, or a wire link on the assembled
board.

## OWNER RULING, 15 September 2026 02:40 CEST: DECISION 24 IS THE SESSION'S

**His words, verbatim: "while B is blocked on your decision == unblock B from my decision".** Decision 24 (board B
lays 62 to 71 of its 113 pairs and the 10 September hold releases no board under 113) is delegated to the
session, and the session takes **option 2, the one the decision itself recommended**: the pair hold judges the
COUPLED FRACTION of the board's pair copper rather than every pair.

**What is taken.** `boards/b.json` declares `pair_coupled_fraction: 0.80`. The pre-route pair gate holds B only
while the pre-router lays fewer than 80 percent of its pairs; the impedance gate on the routed board passes when
the coupled length across the judged pairs, weighted by each pair's own length, is at least 80 percent of the
total. **Every pair is still read back and named with its own verdict, and the 1 mm intra-pair length gate is
untouched for the pairs that exist.** A board that declares nothing keeps the 10 September rule to the letter:
one pair short and the gate refuses, so A, C, D, E and P are unchanged by this.

**Why 0.80 and not a hoped-for number.** B lays 62 to 71 of 113 on the tools of the day (32.174, 32.185); ruling
18's floor plan is refused by the board's own regions by 86.2 mm (32.185); and USB 2.0's own budget for
uncoupled length is a sixteenth of its edge. Eighty percent of the pair copper coupled, the rest laid by the
router as two traces, is the measured board.

**What it does not do.** It does not route B. B16 flattened near 70 open and B19 has never been routed whole;
the partition route reached the reconcile at 1,121 boundary conflicts (32.93). Lifting the hold puts B on the
same path as the other six, which is a route campaign with its own numbers, and that is what runs next.

**Implementation note, 15 September 2026 04:20 CEST.** The first route under this ruling met a defect the ruling
did not create and could not have seen: B19's pair copper carried 64 hard DRC items of the pre-router's own
making before the router ran (appendix 32.192). Three causes are fixed at the source and the pair copper meets
the DRC on every board now, with a refused pair taken off whole so the fraction is judged on legal copper. The
fraction itself is unchanged at 0.80 by length; nothing here moves it.


## DECISION 27, OPEN: the four-layer boards cannot carry a plane under their back-side signals as built (15 September 2026, 21:30 CEST)

**The ruling of 20:15 CEST** made two return-current rules gates for every board: a filled plane on a neighbouring
layer under every signal track (the larger of 10 mm or 5 percent of a net's length allowed for anti-pads and connector
ends), and a ground via within 1.5 mm of every signal via outside a fine-pitch fan. **Both were measured on every
committed board before anything was re-finished** (`tools/return_report.py`, appendix 32.198). Rule 2 is a tool's job
and needs no ruling: the finish places the ground vias. Rule 1 is a property of the STACK and this is what it reads:

| board | layers | back-side signal track with no plane on a neighbouring layer | nets over their limit |
|---|---|---|---|
| A (A34 committed) | 6 | 7 percent (134 of 1,935 mm); F.Cu 5, In2 6, In3 5 | **3 of 197**, each 10 to 16 mm |
| B (B19 placed, no fill yet) | 6 | not measurable before the route | 21 of 617 rails-as-signals, an intent-file artefact |
| C (C17) | 4 | **62 percent** (6,173 of 9,930 mm) | **81 of 127** |
| D (D11) | 4 | **55 percent** (677 of 1,236 mm) | **27 of 127** |
| E (E9) | 4 | **88 percent** (2,283 of 2,582 mm) | **59 of 76** |
| P (P4) | 2 | 100 percent on B.Cu, 57 percent on F.Cu | 29 of 29 |

**Why.** On JLC's four-layer stack a back-side track's nearest layer is In2, 0.2 mm away, and In1's ground plane is a
1.065 mm core beyond it. C and D route signals on In2 (a third of C's track, a third of D's), so their In2 ground pours
are cut wherever a track runs, and the back-side tracks over those cuts have their return a core away: the loop the
rule refuses. E's In2 carries its power pours and nothing else, and its back-side tracks run between those pours over
bare dielectric. P is two layers and is ruled already (P5: signals on the top layer over the ground pour).

**What needs no ruling and is running.** E: an In2 ground pour under everything the power pours do not cover (a
generator change, no layer change), then E10 re-routed and measured. D: a measurement route with In2 as a power layer
(a solid ground plane, wires on F.Cu and B.Cu only; D is 416 connections and routed 0 and 0 with three routing
layers), in an isolated tree, to see whether two routing layers close it. A: the three nets at 10 to 16 mm are
closed by the return-via fixer and a re-finish, or named. B: read on B19's routed board.

**What needs a ruling: board C.** C routes 9,045 mm of signal on In2; two routing layers were measured on 6 September
(the In1 keep-out board left 14 to 35 connections open in the driver cluster, appendix 32.44 and 32.47), which is why
C became four layers with In2 routable. The rule as ruled cannot hold on C's stack. Options, costed:

1. **C to six layers (JLC06161H-3313: F.Cu, In1 ground, In2 and In3 routing, In4 ground, B.Cu), RECOMMENDED.** Every
   signal layer then has a plane next to it (In2 against In1, In3 against In4). The generators already carry the six-layer
   form for A and B. Cost: about twice the bare-board price of the four-layer C (the largest board of the set, the U
   backer), one regeneration and one route (C's routes take about six hours). A layer count is a reserved class, so it
   waits for the word.
2. **Keep four layers, In2 a solid ground plane, route on F.Cu and B.Cu.** Cheapest if it routes; the 6 September
   measurement says it does not, and nothing in the tools has changed that would make it. The measurement can be
   repeated as D's is, one route, before the six-layer C is cut.
3. **Keep four layers and exempt C's back-side tracks from rule 1 with a written reason** (the panel backer carries
   LEDs, switches and low-speed I2C and SPI). The rule then does not hold on all seven boards, which the 20:15 ruling
   asked for.

Until the word, the run does what needs no ruling: E's pour, D's measurement, A's re-finish, P5's route, the return
vias on every board, and C's re-finish for rule 2 alone (its rule 1 verdict stands as refused).

**Measured since, 15 September 2026 21:46 CEST.** D with In2 as a ground plane (two routing layers, `/root/dexp`, the D12
profile with its plane treatment changed for the run) routed **0 hard, 6 open** at round one, **0 hard, 3 open** at round two
and its finish closed those to **0 hard, 0 unrouted**; the return-path gate then read **13 of 47 signal nets over the 10 mm
floor by 2 to 4 mm** (AF_OUT 13.9 of 132 mm, KEY 14.0 of 166, PA_EN 14.1 of 179), which is the plane's own anti-pads along
via and pin rows, not a routing layer under the track. So for D the answer to option 2 is measured: **two routing layers
close D**, and what remains is whether a net that runs beside a via row for 8 to 10 percent of its length meets the rule
as ruled (the larger of 10 mm or 5 percent). That number is the owner's if the tolerance is to move; the run does not
move it. E10 (the In2 ground fill) routed 0 hard, 2 open at round one, the stub router closed one, round two is running.
C's numbers stand as above.

**Measured again, 15 September 2026 22:16 CEST, the third D round and where its misses ARE.** The In2-plane D closed to
**0 hard, 0 unrouted** at round three as well; its board gate then refused it on rule 1 for **13 of 127 signal nets** and on
rule 2 for **47 of 185 signal vias**, and both numbers are now anatomised (`tools/return_gaps.py`, the fixer's split
refusal line):

- **Rule 1.** The nets over their limit are over by 0.3 to 11.7 mm, and the millimetres are the nets' OWN VIA TRANSITIONS:
  0.6 to 1.0 mm of track over the anti-pad of each of the net's own vias, 15 to 36 vias per net (PTT_HS1_n 16.8 of 226 mm
  in 25 runs, AF_OUT 13.9 of 132 in 24, KEY 14.0 of 166 in 22), plus ONE 12.7 mm run on TX_INHIBIT_n along the seam
  between the In2 ground fill and ruling 15's 1.2 mm rail band (the track runs in the band's 0.3 mm clearance for that
  length, beside the harness header). The number is not a sampling artefact: at a 0.5 mm sample 9 nets are over, at 0.25 mm
  7, the totals within 0.6 mm. So the finding is: **a via-dense net on a four-layer board exceeds the 10 mm floor on its
  transitions alone**, where A22's long nets (the boards the tolerance was calibrated on) absorb theirs in the 5 percent.
- **Rule 2.** The fixer places a ground via beside 138 of the 185; for the other 47 **every one of the 64 candidate sites
  (four rings to 1.5 mm, sixteen directions) is on another net's copper**, none is outside a ground fill. They sit in the
  fanout of the PTT and expander cluster (x 62 to 67, y 105 to 121) and the module's socket rows: the router took the room
  first.

**What needs no ruling and is running.** A ground-via GRID laid before the route (`tools/gnd_grid.py`, pitch 2.1 mm so no
point is further than 1.5 mm from a grid via, placed only where the site is free, inside ground copper, outside every other
net's zone and via keep-out, and clear of the fine-pitch fans) is measured on D in its own tree: if the In2-plane D still
routes to 0 and 0 with the grid down, rule 2 holds by construction and the same stage goes to every board. The grid does
nothing for rule 1's via transitions.

**What needs a ruling, for D and for every via-dense net on the four-layer boards**, in the order recommended:

1. **Rule 1 does not count a via transition that rule 2 satisfies, RECOMMENDED.** A track's last millimetre over its own
   via's anti-pad is the layer change itself; with a ground via within 1.5 mm of that via the return current has its path,
   which is what rule 2 exists to assure. Judging the same millimetre under both rules refuses a board for the transition
   twice. Under this reading D's rule 1 misses shrink to the one seam run (a keep-out strip beside the band, a generator
   change), and the tolerance stays where it is for every run that is not a judged transition. Cost: none in copper; a
   change to what the check counts, which is why it is asked.
2. **The tolerance stays literal and D is routed for fewer vias** (a higher via cost, unmeasured whether the In2-plane D
   still closes; each net would need a third fewer vias) plus the seam keep-out. Cost: routes, and no guarantee.
3. **A larger floor for the four-layer boards** (25 mm). Cost: a number chosen for the board, which is what the calibrated
   tolerance was written to avoid.

**The grid measured on D, 15 September 2026 23:27 CEST (`/root/dgrid`).** With 1,288 ground vias laid before the route (2.1 mm
pitch, every site free of other copper, inside ground, outside the rail band and the fine-pitch fans) the In2-plane D routed
to **2 open and 1 hard** in its one attempt, the stub router closed both opens, and the gate reads **rule 2: 279 of 289
signal vias with a ground via** (10 without a site, against 138 of 185 without the grid) and **rule 1: 11 nets over**, the
same via-transition class as before (the grid does nothing for rule 1, as predicted). The one hard item is the router's
own, a /PCM_XTI track against a solder jumper's pad on F.Cu, a generator item and not the grid's. So for D the answer to
rule 2 is the grid, and what stands between D and both rules is the reading of rule 1 asked above.


A six-layer D is measured irrelevant to this: the anti-pads are the same on any stack. C's ruling above stands unchanged
(its misses are stack, 209 of 453 mm on one net); the same via-transition question will apply to C after its stack is ruled.



## DECISION 28, OPEN: board P cannot hold the return-path rule on two layers, and the ruled P5 does not route (15 September 2026, 22:34 CEST)

**The ruling of 20:15 CEST scoped P as "two layers at 2 oz, re-routed with its signals on the top layer over a solid back-side
ground pour; if the router cannot close it that way, the numbers come back to the owner."** They come back, measured three ways
on the same evening:

| board | rule 1 (a plane under every signal net) | route |
|---|---|---|
| P4 as committed (two layers, wires on both, the B.Cu ground pour) | **29 of 29 signal nets over** their limit, 43 to 104 mm uncovered per net (SMBC 104 of 123 mm) | 0 hard, 0 unrouted |
| P4 plus a board-wide F.Cu ground pour (option "pours on both sides", added to a copy and refilled) | **29 of 29 over**, 30 to 65 mm per net | unchanged |
| **P5 as ruled** (B.Cu a power layer, wires on F.Cu only, `/root/piso`) | not reached | **0 hard, 44 connections open of the board's 35 nets, 4 vias**, 23 minutes: a single routing layer does not carry this board |

**Why.** On two layers a track's only neighbouring layer is the other side, and every track on that side cuts the pour the
first one references; with pours on both sides each side references the other's pour except under its tracks, which on a
70 x 44 mm board carrying the pack path in 3 mm bands and 35 nets is most of the length. The rule is a property of the
stack, exactly as decision 27 found for C, and a two-layer board cannot hold it except by being nearly empty.

**Options, costed, the recommendation first.**

1. **P to four layers (JLC's four-layer stack with 2 oz outer copper, In1 and In2 ground planes, the pack bands on the outer
   layers as they are), RECOMMENDED.** Rule 1 holds by construction on both outer layers; ruling 7's 2 oz stays on the
   layers that carry the pack current; the 35-net route is trivial with two routing layers. Cost: the four-layer price of a
   70 x 44 mm board (small in absolute terms; JLCPCB prices this size in tens of euros for five), a stackup line in the
   order notes, one regeneration. **Measured now in `/root/piso4`** (the same route under routeflow with both inner layers
   as ground planes) so the ruling has the number rather than the argument.
2. **Keep P on two layers and exempt it from rule 1 with a written reason** (a pack gauge board: SMBus at 100 kHz, thermistor
   and sense lines, the pack path in bands, no fast edge anywhere). Cost: the rule then does not hold on all seven boards,
   which the 20:15 ruling asked for, and the exemption is a per-board sentence of the kind the pair ruling refused.
3. **P5 as ruled.** Measured above: it does not route.

E5, the bare dock block, is untouched by this: it carries no track and passes rule 1 as "0 of 0 signal nets".

**Option 1 measured, 15 September 2026 22:50 CEST (`/root/piso4`).** Four-layer P (In1 and In2 ground planes, the 2 oz pack bands on
the outer layers, wires on F.Cu and B.Cu) **routes 0 hard, 0 unrouted, 53 vias, in one attempt**; the return-path gate then
reads **2 of 29 signal nets over the limit by 0.2 and 2.2 mm** (DSG_R 10.2 of 74.5, SMBD 12.2 of 79.1, the via-transition
class of decision 27) and the return-via fixer places 26 of 32 ground vias with **6 signal vias left without a site** in the
gauge's cluster (every candidate on other-net copper). The same board with the ground-via grid laid before the route is being
measured (`/root/piso4g`). So option 1 is one small step from both rules where two layers are 29 nets and 30 to 100 mm away
from rule 1 alone.

