**Status: DONE: the screen of L4A-101 (the four rows, the window on printed limits, the line for L4A-56: CHANGE-METHOD to M-A with the thermal-headroom companion). NOT DONE: no draft, no regulator part selected, no independent check; ADI's MAX4995A unread (analog.com refused, the Internet Archive offline). NEXT: the coordinator reads this before dispatching L4A-56 (re-scoped per section 3) and L4A-57.**

# Record l4lim: the limiter window screen before L4A-56 and L4A-57 (Layer 4 task L4A-101)

- **Author:** W135 (Claude), MESHSAT-1357, 7 October 2026 from 04:49 CEST (times from `date`, Europe/Amsterdam). Branch `fnd/l4lim` from main `be07863bbca206a81ab42b9f96a7684c5c10a746`.
- **Why:** the AI-scope register (`_runs/l4ai/REGISTER.draft.md`, W129's draft 2, section 9 item 5) chose for RE-6 and RE-7 a current limiter with a PRINTED limit at each supervisor LDO's input (method M-A). W127's challenge (check 1a, finding 3) found that M-A's acceptance leaves out the bus-fault states, the LDO output short, the limiter's own dissipation and T10-A3's headroom. This screen states the window on printed limits, or names the method change, before any drafting (constitution sections 5 and 6).
- **Framing:** prototype design. Nothing has been built, bought, powered or measured. This is a screen, not an acceptance. It closes no cx46 item and moves no state. cx46 CORRECTIONS NOT CLOSED and Layer 4's DESK gate NOT PASSED stand. Every junction figure is a MODEL on printed thermal resistances, never a measured temperature.
- **Evidence:** `l4lim_screen.py` prints `l4lim_screen.out` (regenerated with `_bin/regen_out.py`). It parses record l9t5's T10 output (`v2/docs/records/l9t5/l9t5_t10.out`, cited below as T10:line) and the makers' sheets, and imports record l9t5's T10 and drafts modules for the AP2112 and TCAN334 rows and the supply path. Before substituting anything it reproduces T10-A3's printed 3.6524 V against 3.5213 V. Cited below as OUT:line. Its test is `v2/ecad/tools/tests/test_l4lim.py`.
- **Labels:** PRINTED (a maker's limit or tested row), TYPICAL, MODEL (arithmetic on labelled inputs), ASSUMPTION, INFERRED, SESSION.

## 1. The screen

All figures are at T10's corner: revision V (fitted, L9T5-D7), the 14.0k set point, 76.25 C inside air (T10:69), and the LDO's worst drop 0.8669 V (T10:500). The criterion is unchanged: 125 C for every sustained state and 150 C only for a transient that hardware ends (the owner's part 22). The LDO's 125 C current is I125 = 48.75 K / (theta x 0.8669 V) (MODEL on the PRINTED theta).

**The window's edges** (OUT:22-57):

| Edge | Figure | Label and source |
|---|---|---|
| Upper: AP2112K (SOT25, 184 C/W) | I125 0.3056 A | MODEL on PRINTED 184 C/W, "No Heatsink", DS39724 p.3; T10:112 |
| Upper: AP2112M (SO-8, 114 C/W) | I125 0.4933 A | same sheet, same row |
| Upper: AP2112R5 (SOT89-5, 120 C/W) | I125 0.4686 A | same sheet, same row |
| S1: largest sustained served state | 0.1855 A | MODEL, T10:622-634 (a window average) |
| S2: normal-service peak, both transceivers dominant in the same bit | 0.2839 A | MODEL, T10:515. It has 10i's babbling-row composition: the bounded controller, the circuit's auxiliaries and 2 x 60 mA dominant (PRINTED). |
| S3: row-7 fault rows, held (rev V) | B1, B2 0.3486; B3 0.2495; B4 0.2846; B5 0.3686 A | MODEL, T10:361-368. B1, B2 and B5 carry I_f values that T10 ASSUMED. |
| S3: the brief's (f1) | 0.3726 A | MODEL, T10:160, on round 4's rev Y 144 MHz controller (a cover) |
| S3': the same rows with the healthy fabric's transceiver dominant in the same bit | B5 0.4240 A (largest); B1, B2 0.4040; B4 0.3400; B3 0.3049 A | MODEL: held, less the 0.0046 A share (T10:301), plus 0.060 A dominant (PRINTED) |
| S4: row 8, both fabrics faulted (survive only) | (f2) 0.5491 A; rev V held 0.5639 A | MODEL, T10:172 and T10:375 |
| HO-E, for reference | VOS0's 105 C limit from 0.1936 A | MODEL, T10:605. It is 4.4 % over S1, so no current limit both serves S1 and holds it (W127 finding 2; L4A-59). |

IOHA row 7 reads "quorum continues on the other fabric" (`ARCH-PCB-B-IOHA.md`:244). So the healthy fabric's frames are part of the served state, and S3' is row 7's instantaneous peak.

**The four rows:**

| Row | What must hold | Figures (label, source) | Result |
|---|---|---|---|
| (1) The window against the rows the design must serve, and the capacitance that would bridge a limited frame | **W1** (no served state limited): IOSmin at least the served peak, and IOSmax at most I125. **W2** (served peaks limited and bridged): the bridging capacitance must fit within what a latch-off limiter can start into, and the latch timer must restart between limited intervals. | **At 184 C/W:** W1 against S2 alone needs IOSmax / IOSmin at most 1.077, a +-3.7 % band (MODEL, OUT:90). Against S3' (0.4240 A) the edges cross. The best E96 bands under I125 are C1 at 102 kOhm, 0.2274 to 0.3002 A, and C2 at 90.9 kOhm, 0.2247 to 0.2999 A (MODEL on the makers' equations, OUT:91-92). **W2's capacitance:** C = (I - IOSmin) x t / 0.2505 V. The 0.2505 V is the LDO's least 3.2505 V less the TCAN334's least supply 3.0 V (PRINTED, SLLSEQ7F 5.3 p.5). Intervals: a frame of 135 bit-times at 500 kbit/s, 270 us (ASSUMPTION, T10's frame model); TI's printed 11-bit worst dominant run, 22 us (SLLSEQ7F p.9 note 1); the driver time-out, 3.8 ms (PRINTED). C1 can start into at most 62.5 uF at its least 0.2274 A and least 5 ms; B4's limited frame needs 121.4 uF (OUT:101-104). C2 can start into at most 23.4 uF; it already fails at S2's 63.8 uF (OUT:108-111). | **At 184 C/W: NO WINDOW ON PRINTED LIMITS.** W1 is closed. W2 conflicts on the record's own frame model, and in any case rests on a latch-timer restart that neither maker prints. **With the companion (C1 at 49.9 kOhm):** IOS 0.4702 to 0.5704 A, from the PRINTED row 0.475 to 0.565 A at -40 to 125 C TJ (SLVS841F p.7) with the resistor's 1 %. IOSmin is over S3' by 46 mA, so W1 holds on the served side and no bridging capacitance is needed. The LDO must hold 125 C at 0.5704 A, so theta must be at most 98.6 C/W. All three AP2112 packages fail this (132.6 C at 114 C/W; OUT:119-131). |
| (2) The LDO output short (the AP2112's foldback is 50 mA TYPICAL only and "acts in no row", T10:113, T10:179) | A PRINTED fault timer with latch-off, or the case excluded with a reason | Both candidates print a fault timer with latch-off: C1's deglitch is 5 / 7.5 / 10 ms (PRINTED, SLVS841F p.7), and it then latches off "until power is cycled or the device enable is toggled" (p.13-14). C2's tBLANK is 2 / 6 / 20 ms (PRINTED, DS41186 p.6) with a latch-off (p.9); that the latch uses tBLANK is INFERRED. (i) When the short draws the limiter's limit through the LDO, the event's energy is at most 4.1174 V x 0.5704 A x 10 ms = 23.5 mJ (MODEL; C2: 44.8 mJ). (ii) When the LDO holds its own short current under the limiter's limit, the limiter does not act. The AP2112's 50 mA is TYPICAL, with no maximum printed (OUT:143-157). | **(i) BOUNDED** on printed limits. **(ii) EXCLUDED** from the LDO-junction criterion with a reason (SESSION W135-2): a supervisor on a shorted rail is already lost, and IOHA row 3 (`ARCH-PCB-B-IOHA.md`:240) reads "the other two are a majority and ownership is unaffected". The containment that row needs holds on printed limits whatever the LDO does: +5V_IOC and the other two branches see at most IOSmax. An LDO that fails shorted from input to output becomes case (i), which latches. The bounded-interval disconnection of a dead branch is the peers' vote on the limiter's EN (L4A-54; turnoff at most 3 ms, PRINTED). That is a finding, not a printed timer. |
| (3) The limiter's own dissipation while limiting, and its restart waveform | Bounded dissipation, and no unbounded periodic waveform | **In service at S3':** 24.3 mW (rDS(on) 0.135 ohm PRINTED), junction 80.7 C at 182.6 C/W (C1 DBV) or 79.2 C at 120 C/W (C2) (MODEL). **Limiting into a shorted output:** at most 2.348 W (C1) or 2.242 W (C2), for at most the timer's PRINTED maximum of 10 ms or 20 ms. The junction during that time is not computed, because no transient thermal impedance is printed. Surviving it is the part's stated function, backed by its own thermal protection: C1 from 135 C minimum in current limit (p.14); C2 at about 145 C (p.10), with no limit printed. **Restart:** the latch-off versions do not restart by themselves (OUT:159-176). | **Bounded in current and time on printed limits.** No periodic waveform of the part's own. There are two exceptions. First, a hard short at the limiter's own output may thermal-cycle it inside the timer; whether the timer completes across a cycle is NOT PRINTED. That waveform stays in the limiter, at most IOSmax, so the containment holds. Second, a peer-commanded restart through EN must bound its own rate: one attempt per T_r keeps the average at most 23.5 mJ / T_r. The reverse-voltage latch (95 to 190 mV for 3 to 7 ms, PRINTED) is not a credible trip in service (MODEL). |
| (4) T10-A3's headroom with the limiter's resistance in place of the 0.3 ohm sense | Each LDO's input over its requirement | The supply path is computed exactly as T10 does: the pre-regulator's least 3.9063 V, a 2 % budget, 0.04252 ohm at the total current, and a 0.0681 V shift. The model reproduces T10's 3.6524 V against 3.5213 V first (OUT:180). (a) At T10's point, 0.2452 A on all three, with 0.135 ohm: 3.6936 V against 3.5213 V. (b) At IOSmax on all three: M-A at 184 C/W reads 3.6791 V against 3.5595 V; the companion reads 3.6082 V against 3.7486 V on the AP2112's dropout rows (INFERRED between 300 and 600 mA, as T10). (c) The other two, while one sits at the companion's IOSmax: 3.6929 V against 3.4798 V. (d) U601 and the lead at three limiters' maxima: 1.7111 A against 3 A and 10 A (PRINTED, T10:241). (e) S3' on all three in one bit: +0.0005 V. | **(a) holds, +0.1723 V.** (b) holds for M-A at 184 C/W (+0.1196 V). For the companion it fails on the AP2112's rows (-0.1404 V), so the companion regulator's PRINTED dropout at 0.5704 A must be at most 0.2399 V. (c) holds, +0.2131 V. (d) holds. (e) is a bit-time peak, shown and not judged. |

## 2. The candidates

Each candidate is an integrated current-limited switch with a PRINTED limit near 0.2 to 0.6 A and a PRINTED fault timer with latch-off (OUT:59-83):

| Id | Part, maker's sheet | Printed limit rows | Fault timer, latch | rDS(on), theta |
|---|---|---|---|---|
| C1 | TI TPS2553-1 (TPS2552-1 is the active-low twin), SLVS841F Rev. F, August 2016; SOT-23-6 | 49.9 kOhm: 0.475 / 0.520 / 0.565 A over -40 to 125 C TJ; 210 kOhm: 0.110 / 0.130 / 0.150 A (7.5, p.7). Equations: IOSmin = 25230 / R^1.016 and IOSmax = 22980 / R^0.94 mA (p.15). | Deglitch 5 / 7.5 / 10 ms, PRINTED (p.7). It latches when the deglitch is reached (9.3.1, p.14) and is cleared only by power or EN (p.13). Its restart on a momentary clearing is NOT PRINTED (9.3.3, p.14). | 0.135 ohm at most, -40 to 125 C TJ; 182.6 C/W (DBV), 72 C/W (DRV) |
| C2 | Diodes AP22653A (AP22652A is the active-low twin), DS41186 Rev. 5 - 2, March 2026; SOT26 | 49.9 kOhm: 0.441 / 0.490 / 0.539 A over -40 to 85 C TA; 210 kOhm at 25 C only: 0.095 / 0.125 / 0.155 A (p.5). Best-fit equations on p.10. | tBLANK 2 / 6 / 20 ms, PRINTED (p.6). The latch-off is described on p.9; that it uses tBLANK is INFERRED. | 0.135 ohm at most, -40 to 85 C TA; 120 C/W on high-K |
| not taken | TI TPS2596 (SLVSET8A, in the tree at `v2/vendor/power/tps2596.pdf`) | +-10.4 % range-wide | It latches only at thermal shutdown (157 C, TYPICAL, p.7) and exits the limit when the load falls (p.22). No printed fault timer. | |
| not taken | TI TPS25200 (SLVSCJ0F) | precision rows | Constant current until "the device begins to thermal cycle" (p.12). No latch, and the cycling is a periodic waveform. | |
| not read | ADI MAX4995A | | analog.com refused this host and the Internet Archive was offline (7 October 2026, about 05:00). Nothing is claimed from it. | |

The sheets: C1, TPS25200 and C2 are held back by their terms (TI: no redistribution grant read; Diodes' notice item 8 prohibits unauthorized distribution). They are fetched by `fetch_held_back.py` into `v2/vendor/ti/held/` and `v2/vendor/diodes/held/` (gitignored, checked by sha256).

## 3. The line for L4A-56

**CHANGE-METHOD** (OUT:194-207). M-A as registered, a limiter ahead of the AP2112K at 184 C/W, has no window on printed limits:

- The LDO's 125 C current, 0.3056 A, is only 7.7 % over normal service's own peak (S2, 0.2839 A) and is under row 7's peak (S3', 0.4240 A).
- Serving those peaks by limiting them needs more capacitance than the latch-off limiter can start into, and a latch timer that neither maker prints.

**Take the thermal-headroom companion (SESSION W135-1):**

- **The limiter:** C1, TI TPS2553-1 (SLVS841F; DBV), with RILIM 49.9 kOhm. IOS is 0.470 to 0.570 A, and it latches off after 5 to 10 ms. One goes at each supervisor LDO's input.
- **The regulator:** a part in place of the AP2112K, with these PRINTED figures:
  - junction-to-ambient at most 98.6 C/W at the 14.0k corner;
  - rated output and current limit at least 0.570 A;
  - dropout at 0.570 A at most 0.240 V;
  - input rated to at least 4.12 V;
  - output band inside the TCAN334's 3.0 to 3.6 V supply range (PRINTED, SLLSEQ7F 5.3); its own band and load regulation replace the AP2112's in T10-A3.
- **Second source:** C2, Diodes AP22653A, RLIM 49.9 kOhm. IOS is 0.436 to 0.545 A, theta must be at most 103.3 C/W, and it latches after 2 to 20 ms.

**Why the companion, and not K1:**

- It keeps the drafted structure: the pre-regulator, a private LDO for each supervisor, and CON-004's own branch.
- It keeps T10's acceptance (T10-A2, T10-A3).
- It adds one SOT-23-6 and one resistor per supervisor.
- No served row is limited, so nothing rests on a timer's unprinted restart, on the protocol or on the firmware.

**The fallback is K1**, a buck for each supervisor (U25's AP63203), if no regulator with those printed figures fits board B's pockets. K1 was set aside for its area and for the switching ripple on VDD and VDDA, not because it failed (T10 section 8).

**What the companion gives up:** its IOSmin (0.470 A) is over the H743's own 125 C current, 0.328 A (T10:70). So a firmware fault outside FW-B20 can still take the controller past its rating, as before (T10 10h (3)). M-A at 184 C/W would have held the controller, had it had a window. HO-E is uncovered either way.

**For the register:** L4A-56's task becomes the limiter plus the regulator swap, drafted on board B with its composition and mutations. The regulator part must be chosen from makers' sheets against the requirements above.

## 4. SESSION decisions (each under the owner's standing rule of 26 September 2026)

- **W135-1: the companion over K1, and C1 over C2.**
  - Why the companion: section 3.
  - Why C1 first: its 49.9 kOhm row is tested over the junction range up to 125 C. C2's row is over the ambient range only, C2's timer minimum (2 ms) gives the least start-up capacitance, and its maximum (20 ms) doubles a latched event's energy.
  - Reverse by: taking K1, or C2, or a limiter class that prints +-3.7 % at 0.29 A (none of the four sheets read does).
- **W135-2: the output short under the limiter's limit is excluded from the LDO-junction criterion, not bounded.**
  - Why: the branch is already lost (IOHA row 3), and the containment holds on the limiter's printed maximum.
  - Reverse by: a regulator part that prints its short-circuit current with a maximum, or the peers' EN disconnection made a hardware timer.
- **W135-3: S3' includes the healthy fabric's transceiver dominant in the same bit.**
  - Why: row 7 serves the other fabric while the faulted one is live.
  - Reverse by: a contract row that forbids simultaneous transmission. That is a firmware means, and it would not be credited to a hardware window.
- **W135-4: the interval models are taken from T10 and TI.** The frame model and 500 kbit/s are T10's. The 11-bit run is TI's printed protocol worst case (SLLSEQ7F p.9 note 1).
- **W135-5: the AP22652/53 sheet is held back.** It goes into a new `v2/vendor/diodes/held/` (one `.gitignore` line), because Diodes' notice prohibits unauthorized distribution.
- **W135-6: the test is placed under `v2/ecad/tools/tests/`.** That is where `run.py` finds it; the record folder holds the script, its output and the fetch.

## 5. Findings for other authors

- **L4A-54** (the CAN vote, M-B): two items.
  - The vote outputs could drive each supervisor's limiter EN. That disconnects a dead or shorted branch within a bounded interval (row 2 (ii)), and gives the latched-off limiter its restart.
  - Any peer restart must bound its own rate (row 3).
- **L4A-57**: its acceptance becomes the LDO's junction at constant power at IOSmax on the regulator's PRINTED steady theta. That is a bound for every waveform under it, so E-17's transient Zth is no longer needed for the sustained bound. Realising the printed theta on board B's copper remains a Layer 10 means.
- **L4A-58**: C1 holds FAULT asserted while latched (SLVS841F 9.3.3). The in-service over-limit test can read it. The limiter's latent loss of its limit is still HO-D's question.
- **L4A-59 (HO-E)**: the companion's limit is over the H743's own 125 C current. The controller's rating in a firmware fault, and VOS0, stay with HO-E and FW-B20.
- **The coordinator:** two items.
  - The register's L4A-56 and L4A-57 text names the AP2112K implicitly. Section 3's requirements re-scope both.
  - The brief's (f1) 0.3726 A is round 4's rev Y figure. The screen also carries rev V's held rows and S3'.

## 6. What this screen does not do

- It drafts no circuit, and selects no regulator part.
- It runs no check.
- It does not compute either limiter's junction during a latched event, because no transient thermal impedance is printed.
- It did not read MAX4995A.
- It does not settle whether either maker's timer restarts on a momentary clearing. Neither sheet prints it. The companion makes the question moot for served states.

## 7. Reproduce

```
python3 v2/docs/records/l4lim/fetch_held_back.py          # the three held sheets, checked by sha256
python3 v2/docs/records/l4lim/l4lim_screen.py             # prints l4lim_screen.out (about 3 s; pdftotext needed)
env -C v2/ecad/tools python3 tests/run.py l4lim
```

The constitution was read and is acknowledged (sections 3 to 6 and 8). This screen is the bounded closure contract's design-choice comparison (section 4): three approaches were compared, the most it allows (M-A at 184 C/W, the companion, K1), and the selection is within authority.
