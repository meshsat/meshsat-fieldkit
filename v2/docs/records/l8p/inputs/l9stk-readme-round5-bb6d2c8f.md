## Round 5 (5 October 2026, branch `fnd/l9stk2` from `43da41ca`, case row C-PROT rev 1): the guard re-selected after L8P-F08

**STATUS LINE (written 5 October 2026, 12:20 CEST).** DONE: board P's check of the guard (record l8p round 7, `fnd/l8p2` at
`bab66e6b`, copied into `inputs/`) reproduced from the makers' sheets in `l9stk_guard.py` section 5b: finding L8P-F08 and the
three relabellings; the three corrections the checker derived and a fourth judged on the window (a ramp's reading at every
corner, every off FET on the return counted), on round 4's acceptance and on the two failure modes named for E-13b; a
re-selection by the session (C4) with its acceptance and correction scope, `l9stk_guard.out` section 6 and page 15.9
restated; tests that fail on round 4's window claim. NOT DONE, and why: the guard's draft, its composition, its netlist
reading and its mutations, because the drafts are L4-E11's and record l8p's and this record edits nothing of theirs; no
independent check of this round; nothing physical. NEXT: L4-E11 with board A's generator and record l8p draft page 15.9's
restated scope, then one independent check on its acceptance. **L8P-F07 and L8P-F08 stay OPEN until then.** This was the
first negative check of the selection; a second negative check of C4 ends that loop. Nothing was built, bought, measured
or sent.

**L8P-F08 answered.**

| Item | Round 4 said | Record l8p's check (round 7) | Round 5 |
|---|---|---|---|
| The window | "RET/OUT closed 0.590 against 0.4603": held | a ramp's reading at DOCK_EN_OUT 1.825 V: the return may carry 26.45 uA; the AO3400A's 43.6 uA at 86.25 C puts it at 0.668 V (0.770 V at the most favourable corner): fails | REPRODUCED, every figure; round 4's window claim and acceptance (c) WITHDRAWN |
| The trip accuracy | "printed at a 5 V supply" | printed at VDD 5 V only | relabelled; every trip is at VDD 5 V (the regulator at its table's input, closed, from 8.28 V) |
| The regulator's ground current | 2.25 uA | printed at VIN 6.0 V only, typical elsewhere | relabelled; the 30 uA allowance keeps 11.75 uA |
| The regulator's accuracy | plus or minus 1 % | printed from 100 uA of load | relabelled; NOT PRINTED at the switch's 16 uA, ASSUMED |
| (i) a 2N7002 shunt | | recommended: 13.2 uA in all, a site to 103.8 C | C1: on this round's warmer count 18.83 uA, the return 0.908 V (0.859 V all doubled), a site to 98.7 C: holds |
| (ii) the resistor at 10 or 11 kOhm | | 11.57 kOhm at most (10.86 kOhm with Q44 and Q107 hot); the tripped regulator from 11.93 V | C2: 11 kOhm fails; 10 kOhm holds by 2.09 uA and fails all doubled, the tripped regulator from 12.49 V: NOT SELECTED |
| (iii) the shunt's site bounded | | under 77.9 C; 74.2 C with Q44 and Q107, not available | C3: 69.0 C on the full count, under the 76.25 C air: NOT AVAILABLE |
| a fourth | | | C4: C1 with the fixed resistor as two 7.5 kOhm in series: **SELECTED (SESSION)** |
| FM1, a shorted fixed resistor | | the guard may cycle; E-13b finds it | one resistor: the guard cycles and the breaker stays off (a 39.8 ms closed phase, plus 5.00 ms per uF of the regulator's input capacitor, against the RC hold's 0.110 s: an input capacitor under 14.1 uF); C4: one short still trips and holds, and E-13b's band finds it |
| FM2, a shorted regulator | | up to 23 V on the 6 V switch, latent until E-13b | over 6 V from BRK_VIN 7.60 V; no held zener prints both sides (BZT52C5V6, BZT52C6V2): latent until E-13b; a clamp is Layer 6's search |
| The state before tEN | "the shunt's gate filtered over 2.3 ms and 1.5 ms" | taken high, not printed | the gate network sized (47 kOhm, 1 uF, 1 MOhm): 0.391 V after 3.8 ms; a slower ramp rests on TI's description, bench item E-13b (b2) |
| The no-trip and trip sides | 9.8 K in the service, 6.0 K at C4, 15.68 K for the gradient | reproduced | unchanged: the switch's |
| L8P-F07, L8P-F08 | L8P-F07 OPEN | L8P-F08 OPEN | both OPEN until the draft and an independent check |

**What moved.** `l9stk_guard.py` and `l9stk_guard.out` only (19 pins, 7 new: record l8p's output, 12k and 12b; L4-E11's 20b,
20c and input-return reset at `08f7e38a`; Diodes' zener sheet). Section 5's round 4 text on the shunt and the window carries
its withdrawal; section 5b is new; section 6 is restated; the predicates go from 16 to 30, round 4's window predicate
rewritten without the window. `l9stk_protection.out`, `l9stk_copper.out`, `l9stk_stackups.out` and `l9stk_vh_return.out` did
not move (byte for byte), so round 4's note on record l9pwr's pin stands unchanged.

**SESSION decisions (round 5), each with its reason and its reversal.**
1. **C4 selected**: the 2N7002 shunt (the kit's part) keeps the window on every count read here; the pair of 7.5 kOhm turns
   FM1 into a degraded state that still protects, for one resistor. Reversed by C1 if the drafts' check finds the pair not
   worth its part, or by a check that refuses the count.
2. **One count for every correction**: every off FET on the return at board A's 86.25 C, board P's Q107 included (warmer than
   record l8p's air). It is the conservative side of round 4's own site assumption; reversed by a site bound from the layout.
3. **Q103's gate leakage** at its printed IGSS, not doubled (an oxide leakage), with the doubled figure shown beside; the
   selection holds both ways.
4. **The gate network** 47 kOhm, 1 uF, 1 MOhm: under the 2N7002's least threshold through the regulator's start and tEN with
   OVERTEMP taken high, on within 36.0 ms of a trip. The drafters may size it otherwise against the same inequalities.
5. **The 2N7002's on-resistance** bounded as its 5 V row scaled by the drive and doubled hot (ASSUMED); the requirement is
   38 times that bound.
6. **No supply clamp for FM2**: neither held zener prints both its voltage under 6 V and its current at 5.05 V.

**Findings for other authors (round 5; nothing of theirs is edited here).**

| Finding | Owner |
|---|---|
| L9S5-F1: the guard's draft by page 15.9's restated scope: RT1 becomes two 7.5 kOhm 1 % in series; the 2N7002 shunt beside Q44 with its gate network; a test point on the pair's midpoint; the acceptance (a) to (c) and seven mutations in 15.9 and `l9stk_guard.out` 6 | L4-E11 with board A's generator; record l8p |
| L9S5-F2: L4-E11 20c counts SENSE1 alone on the return and states the window as a ratio bound (25.8 kOhm). Restated as a ramp's reading at DOCK_EN_OUT 1.825 V with Q44, Q107 over Q108, the guard's shunt and Q103's gate counted, the window holds for the pair with 18.83 uA (24.33 uA all doubled) against 26.45 uA | L4-E11 |
| L9S5-F3: record l8p's 12k: its correction (i) taken, with the pair; its count put Q44 and Q107 at the air, this round counts them at board A's 86.25 C | record l8p |
| L9S5-F4: E-13b gains (b), the tripped DOCK_EN_OUT read within its band by BRK_VIN (FM1), and (b2), a slow ramp of the loop with the guard cold (the state before tEN); FM2 stays latent between checks | the supplier's commissioning procedure |
| L9S5-F5: the shunt adds no part type (the kit's 2N7002); a 7.5 kOhm 1 % value; a supply clamp for the LM26LV that prints both sides, if one exists | Layer 6 |

**Tests** (`test_l9stk`, round 5 adds five): L8P-F08 re-derived by hand and round 4's closed-ratio method shown to accept the
failing circuit; the corrections on the full count with mutations; the selection, its failure modes and its gate network
solved by hand; the relabellings read from the sheets; the page and this README carrying round 5.

