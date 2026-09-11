# Decisions reserved to the owner, batched from the unattended run of 11 September 2026 (MESHSAT-862)

The run does not wait on these. Each is a change that `tools/reserved.json` puts on the never-auto floor, so the
work that does not depend on it carried on and the evidence is collected here. Nothing below has been acted on.

The floor classes are in `tools/reserved.json` with the files that carry them; `reserved.py --list` prints them.

---

## 1. Does the pair hold bind board C? (blocking C10's release, and only C10's)

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

**The decision.** Either the ruling binds C through its stated mechanism, in which case C is not held and its
deliverable can be cut; or the ruling binds the whole set as a set, in which case C waits for B. This is an
interpretation of your own ruling and is not mine to take.

---

## 2. Every board's layer count (the P0 of 11 September, 32.106)

Measured state: A22, B15, B16 six layers on JLC06161H-3313; C7, D9, E6 four on JLC04161H-7628; E5, P3 two. All
1.6 mm.

**What the run can produce without you, and is:** the measurement each decision needs. For A that is the
four-layer rerun with `unknot.py` in the loop that was never done, since A22's 33 hard turned out to be one router
knot rather than congestion. For B the evidence already exists and stands: three CM5 at 0.4 mm receptacle pitch,
93 opens at 8 passes with In1 keep-outs. For C, D, E, E5 and P no rationale was ever recorded at all, the four
layer default being the first board's default copied forward.

**What the run cannot produce:** the cost side. No like-for-like four against six quote has ever been taken and the
promotion was never costed. That needs a quote per board at its real dimensions and quantity five.

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

## 5. vast.ai will not rent to this account, so the work is on the VM

**The ruling, 6 September 11:30:** "RUN EVERYTHING ON VAST.AI AND FIND A BETTER INSTANCE." Routes, generators,
finishes and renders on rented boxes; the VM idle with its services up.

**What happened today.** Every CPU-only offer is refused: `no_such_ask` on six freshly fetched ids, through both
the REST API and the `vastai` CLI, within seconds of the listing that returned them. GPU offers list normally.
The account has 70.92 USD of credit, `can_pay` true, and `paid_verified` 0. Boxes rented on this account as
recently as this morning, so something changed at their end or CPU-only rental now needs verification.

**What the run did instead.** The measurements are on the VM `nllei01gpu01` with `~/meshsat-services.sh stop`
first, as the older rule requires, and a `venv-numba` was built there so the compiled kernel is what runs. The
ruling's purpose was speed, and the alternative it names does not currently exist, so the choice was the VM or
nothing. **It is recorded here rather than assumed**, because it is your ruling.

**What it costs.** The VM is 31 GB shared with its own services and is one machine, so the parallel arms and the
partition route that the box made cheap are serialised. The four board re-routes that phase D needs will be slow
on it: B19's partition route alone was hours on a 128-thread box.

**The decision, when you want it:** verify the vast.ai account, or accept the VM's serial pace for the board
phase, or name another host.
