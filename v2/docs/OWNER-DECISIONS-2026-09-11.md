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

---

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

