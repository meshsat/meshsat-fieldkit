# The pair coverage decision, with the numbers (9 September 2026, 22:00 CEST; MESHSAT-862)

This is the decision the record has carried open since 9 September 00:50 ("the binding constraint, and the owner decision it needs"). It is written now because tonight's runs finally measured *why* the pre-router misses pairs, which changes what the options cost. Prototype work: no board is built and none is ordered.

## 1. What the gate asks and what the tools deliver

`impedance_check.py` fails a board when any differential pair misses its target. Freerouting 1.9.0 has no differential-pair router, so **every pair the pre-router does not lay reads UNCOUPLED** and the board is not clean. The pre-router is therefore the only thing standing between this set and a release.

Measured coverage: **B19 38 of 113 pairs (34 percent)**, B17 36 of 99 (36), A23 1 of 3, D9 4 of 4. Small boards are fine; the two big ones are not.

## 2. Why the misses happen, measured tonight

From `pair_report.py` over a full B19 pass (160 failed attempts):

| count | reason | what it means |
|---|---|---|
| 46 | the legs clear no smoothing of the centreline | the legs are a parallel offset of the corridor and **overshoot 41 percent at every right-angle corner**, so they collide where the corridor does not (32.90) |
| 38 | no stub path at a via | the corridor was laid but the short hop from its end to one leg's escape via could not be found, concentrated at the CM5 receptacles' 0.4 mm escape scheme and the two HDMI switches |
| 18 | the expansion caps | a 261 mm pair exhausts 5.4 million expansions of a 0.1 mm grid; the small 2D search stops at 9,398 |

By part: 40 died at a via, 12 at U1, 8 at U4, 8 at U30B. **None of the three is a placement problem**, which is what makes this a tool decision rather than another floor-plan pass.

## 3. The three options

**A. Fix the pre-router.** The three causes above are now named and each has an obvious remedy: mitre or fillet the leg offset at corners (or make the search pay for turns); aim the corridor's end at the escape via instead of near it, and let the stub use the other layer; a coarser grid for long pairs (`PAIR_GRID_LONG`, written and off until measured). Cost: days, not hours, and the record's own estimate said so. Benefit: it raises coverage on every board and is the only option that makes the gate true rather than tolerable.

**B. A measured exception per pair, in the `erc-allow.txt` idiom.** Honest bookkeeping, and it is how this repo already handles a defect it has decided to accept. Cost: **78 written reasons on B19 alone**, each of which is the same sentence, and a gate that has been argued down rather than met. It buys paperwork, not engineering.

**C. Gate the controlled fraction.** Judge a pair by how much of its judged length is coupled and inside tolerance, with a threshold, instead of pass or fail on the whole net. This is not a weakening dressed up: `impedance_check.py` already exempts pin fans by the same logic (a 3 mm feature against a 75 mm edge), USB 2.0 and USB 3 both allow short uncoupled regions at the connector, and the tool already reports the percentage per pair. What it needs is a threshold with a reason, and pairs below it still fail.

## 4. RULING (owner, 10 September 2026, 02:00 CEST)

**Option B: hold every board until the pre-router lays every pair.** The gate is unchanged, no exception is written, and no board of this set is released while any pair reads UNCOUPLED. The recommendation below was option C and was not taken; it is kept as written because the record keeps what was recommended as well as what was ruled.

**What that makes the work.** The pre-router is now the critical path for the whole set, and the three causes measured tonight are the programme: the leg clearance against the corridor (46 of 160 failed attempts), the stub hop into an escape via at the CM5 receptacles and the HDMI switches (38), and the search expansion caps (18). Each is measured against the same board with one variable at a time, in the discipline that caught the wall-clock budget and the neutral mitre change tonight.

## 5. Recommendation as it was written

**C as the gate rule, A as the engineering work, B never.** The gate should say what good enough is and measure it, which is C; the tool should get better at laying pairs, which is A and now has three named leads; and B is thirty pages of the same excuse.

A concrete C: a pair passes when **at least 80 percent of its judged length is within tolerance** and no unreferenced run exceeds the existing `UNREF_MM`, and a pair with less than that fails as it does today. On D9's measured pairs that changes nothing (they are at 99 percent); on B19 it is the difference between a board that can be released with its numbers stated and a board that cannot be released at all.

**This is the owner's call**, and the numbers above are what it should be made on. Nothing in this note changes a gate on its own.
