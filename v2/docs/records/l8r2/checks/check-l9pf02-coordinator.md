accepted: CLOSED AS CONDITIONAL (the coordinator's closing check, not an independent or a collaborator's check)

# The coordinator's closing check of L9P-F02 after the collaborator's two runs

At commit `aa07066e` (branch fnd/l8r3, record l8r2 sections 1s, 1t and 1u). The collaborator's focused check (cx38, NOT CONFIRMED,
B1 to B3) and targeted recheck (cx39, NOT CLOSED, B1 to B3 and F5-03) are filed as received in this folder; both runs are spent. This
check follows the owner's rule: exhausting the runs is neither a pass nor a question, so the coordinator checks the last corrections
and labels the result as its own. Written on 4 October 2026.

## What was recomputed from the sources (not read back from the record's script)

| Item | Source | Recomputed | Record | Result |
|---|---|---|---|---|
| F5-03, the 5.1 V window with both dividers at 0.1 percent | LM5176 VREF 0.788 / 0.800 / 0.812 V (SNVSAI1D); 53.6 k over 10 k; IBIAS(FB) 25 nA through 53.6 k | 5.0032 to 5.1730 V, with the bias 5.0019 to 5.1744 V | 5.0019 to 5.1744 V | reproduces; inside the CM5's 4.75 to 5.25 V |
| The loop's least limit | 43 mV over 6 mOhm at +1 percent | 7.095710 A | 7.095710 A | reproduces |
| The steady envelope | 23.197 W slot loads plus 2.75 W over 0.80 for the fan branch, at 4.9019 V | 5.4336 A, margin +1.6621 A | 5.4336 A, +1.6622 A | reproduces (rounding) |
| The bounded start | the fan branch at most 1.80 A (100 us moving average) on the slot rail | 6.5323 A, margin +0.5634 A | the same | reproduces |
| The degraded fan | the branch held under the eFuse limit | 6.1525 A, margin +0.9432 A | the same | reproduces |
| The declaration | 6.6 A on all three slot leads | covers the bounded start; +0.4957 A to the loop's least | the same | reproduces |
| The record's output and tests | `_bin/regen_out.py`; `run.py test_l8r2 test_l8gnd test_public_hygiene` | "already identical"; 40 passed, 0 failed, 0 skipped | the same | reproduces |

## The four items of the recheck

- B1 (the Figure 24 bound): the unsupported upper-bound claim is withdrawn; the AP64500's rejection rests on its 5 A rating (5.487 A
  and 5.118 A at its least voltage with the fan on the rail), and the no-fan option's 48.4 C is labelled a CONDITIONAL screen. CLOSED.
- B2 (declarations over the start-up and fault envelope): 6.6 A on both boards' slot leads, the entries and returns at 2.60 A, and
  C4-3's waveform acceptance (sampling, the 100 us moving average at most 1.80 A, the duration above the steady current, the slot at
  most 6.6 A). CLOSED AS CONDITIONAL on C4-3, which measures the start the bound assumes. MINOR: C4-3's "above the steady 0.712 A" uses
  the steady branch current at the old least voltage (4.829 V); at 4.9019 V it is 0.7013 A. The duration criterion should name the
  steady current it measures on the specimen; to be corrected in the record's next round.
- B3 (thermal acceptance over the whole matrix): C4-1's measured case temperature plus the stage's measured loss times 0.8 C/W at
  every steady point at 50 C ambient, acceptance at most +125 C; C4-6's 36.89 C/W junction-to-ambient screen labelled a screen.
  CLOSED AS CONDITIONAL on C4-1 and C4-6.
- F5-03 (the 5.252 V output): corrected in a release-guarded draft (`apply_gen_sch_a_fb01.py`), its netlist check reads the eight
  resistors; Layer 6 owes the 0.1 percent part codes. CLOSED AS CONDITIONAL on the draft's application and the part codes.

## Result

L9P-F02: the defect (slots 1 and 3's AP64500 over its rating with the coolers on the rail) is corrected in drafts: the slots move to
the LM5176 stage with the coolers at full speed and no duty cap, approved cooling and compute service unchanged. It stays OPEN in the
register until the drafts are applied and C4-1 to C4-6 pass; the owner's only item is sending the drafted Sanyo Denki question (C4-4).
Nothing here is built or measured.
