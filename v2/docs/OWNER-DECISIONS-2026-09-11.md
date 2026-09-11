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

**What the run can produce without you, and is:** the measurement each decision needs. For A that is the
four-layer rerun with `unknot.py` in the loop that was never done, since A22's 33 hard turned out to be one router
knot rather than congestion. For B the evidence already exists and stands: three CM5 at 0.4 mm receptacle pitch,
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
