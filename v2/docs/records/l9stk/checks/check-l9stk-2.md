accepted: no

# Record l9stk: the independent checker's check 2, PROTECTION: NOT CONFIRMED (filed as received)

MESHSAT-1357. An AI review by a fresh Claude session that authored none of the record (an independent checker, not a qualified engineering review, not an Astra check), read-only in a disposable scratch clone at `3ab55e8d50ea638cb5d4a13e9a60dbb253c85feb` (branch `fnd/l9stk`). Time: 4 October 2026, 01:45 to 02:00 CEST. Nothing in the kit has been built, bought or measured.

Scope, from the coordinator's brief: the targeted recheck of the copper corrections (B1 to B3 of check 1) and the new protection design: section 14 re-derived, section 15 (W4DP-F2's element), `l9stk_protection.py` and its output, the closure text and findings L9C-F3 and L9C-F16 to F19, against the owner's current-and-time criterion; TI's SLVA673A fetched into the scratch clone by the record's fetch script.

Filed by the integrator of set 29 from the checker's final message for the round, without edits to its content. The record's author answered it in the next round (`L9-STACKUPS.md` sections 14 and 15 name each revision); this note is the checker's own record of what it read and found.

## The checker's report, as received

**PROTECTION: NOT CONFIRMED**

The breaker's arithmetic reproduces at its sources, the copper corrections B1 to B3 hold, and the claim that board P's existing protection cannot meet the criterion with its FETs welded is right. Two things block it: every live docking takes the breaker past the controller's own limits by the record's own statements, and Q39/Q40's correction target leaves out the heat of the band and R17 around them.

In the scratch clone at 3ab55e8d I fetched SLVA673A (sha matched), ran `test_l9stk` and `test_energy_chain` (63 passed, 0 failed, 0 skipped, so the protection tests ran), and ran all three drafts with `--check` only. Nothing in the tree changed, and the clone is deleted.

**Blockers**

- **B-P1. Docking a live pack pushes the breaker past its limits, and docking is a normal event.**
  - The record itself says VIN to SENSE passes the LM5069's 0.3 V absolute maximum above 116.8 A, and that docking reaches that before the gate is low. At the 242.9 A docking peak the sense reads 242.9 × 2.6087 mΩ = 0.634 V, more than twice the limit.
  - The SOA figure for docking ("0.99 of the 10 us line") is read against the 25 °C line, without the equation 5 derating the record applies everywhere else. With its own 103 °C case (factor 0.376) the line is 91.8 A, so the docking peak is 2.65 times it; at E-3's 75 °C base (factor 0.6) it is 1.66 times.
  - The owner's criterion keeps the protection element inside its own ratings, so a known excursion in a normal event needs a design correction, not E-3 and Q-TI-L9S-1.
  - TI's own remedy is in the LM5069 sheet (11.1.1, Figure 45): a make-last contact into UVLO, so every docking becomes a dv/dt start at no more than 0.659 A. The alternative is an inrush element at board A's dock entry.
  - Owners: board P's generator with the battery stream, and L4-E11 or Layer 7 for the dock contact.
  - The hot-short case alone can stay (c): it passes SLVA673A's method (IDM against the breaker threshold, 0.13), and only the 0.3 V question is left for TI.
- **B-P2. DD-2's 24.37 K/W target is not enough.** That figure is FET heating only, the way L4-E11 section 16b defines Zself + Zmut. The FETs sit on the band, which itself rises 9.16 K at 23.93 A (the record's prot 4), and R17 dissipates 2.86 W right next to them.
  - At 24.37 K/W: 76.25 + 9.16 + 3.026 W × 24.37 = 159.2 °C, over 150 °C.
  - The FET-only target has to be at most 21.35 K/W, before R17's share, which no record bounds.
  - DD-2 and E-1 should be stated as a junction limit: TJ at most 150 °C at 23.93 A from 76.25 °C, with the band and R17 carrying the current. A third parallel FET would be the robust alternative.

**Minors**

- The dock-pin acceptance appears twice with different numbers: 0.593 in 14.6 (at 25 A) and 0.553 in E-4 (at 23.93 A). Both are right for their current; pick one.
- The 18.32 to 23.93 A window counts only the parts' ±1.5 %, not the trace and Kelvin error of two paralleled shunts. The top edge is just 0.07 A under the cells' 24 A. Add an evidence item that measures the specimen's actual limit current at -40, 25 and 125 °C.
- At 23.93 A the cells sit at 1.00 of 8 A (0.997) with an unknown parallel split. E-5 can pass only if the groups share within about 0.3 %; name the fallback now.
- The LM5069's minimum and maximum limits are printed at VIN 48 V. The record uses them at 10.6 to 16.8 V without saying so. Add this to Q-TI-L9S-1 and to E-2 and E-3.
- The 18 A service clears the lowest limit by only 0.32 A. Nothing bounds the instantaneous pack current at key-down (ripple, the key-on step) over the 0.28 ms timer.
- The charge direction is not stated: the LM5069 does not limit reverse current, and below POREN the precharge flows through the FETs' body diodes. That works out to 0.75 W at 1 A, which is benign.
- Prot 4's Q1/Q2 reading assumes Q1 is on during discharge. Open finding BAT-F20 (Q1's body diode, about 7 W at 10 A) has to be cited.
- The path for the lead's inductive current at turn-off (TI 11.1.2 B) is board P's existing D1 SMBJ20A. Its forward rating is not checked.
- E-3 runs at a 75 °C base, below the 103 °C case the derating uses. E-7's acceptance should be the service itself: 18 A for 60 s after 10 A held at 76.25 °C, without opening.
- IF-2's two 1 in² 2 oz pads take about 1290 mm² of board P's 3080 mm² per face. That they fit is not shown, and the 0.376 derating rests on them.
- The new SMCJ18A sits ahead of the breaker. If it shorts while board P's FETs are welded, only F1 clears that fault.
- The not-taken list leaves out a controller with a tighter limit tolerance and a third FET in parallel for Q39/Q40.

**Points 1 to 6**

1. **Copper corrections: CONFIRMED AS CONDITIONAL.**
   - The widths reproduce: 38.79 and 39.14 mm a face at 1 oz, 19.39 and 19.57 mm at 2 oz, the shore at 25.78 and 26.02 mm, and every 14.5 reading (116.60, 115.94, 87.42 and 99.56 °C).
   - B1 to B3 are fixed: DC_HS now at the shore widths, the limits at 105 °C as fitted and 120 °C once the plating is pinned, and the plating draft passes `--check`.
   - On the ruled method, with the return run beside the band, 1 oz cannot fit: 78.29 mm a face against board E's 68 mm. One zero-cost route was not tried: the return laid apart at a derived spacing, roughly 44 mm plus the gap. The record gives that no credit for lack of a separation rule.
2. **Board P's existing protection with the FETs welded: CONFIRMED.**
   - The gauge's levels, the AFE's comparators and the PTC all act through the welded Q1/Q2.
   - The second-level protector U2 has no current input.
   - F2's heater is fired only through FUSE_G, from the gauge's firmware or U2's COUT (`gen_sch_p.py` R29 and R30).
   - Nothing assures opening below 33.75 A.
   - I also checked board A: the charger's BATOC stops its converter but leaves the battery FETs on (L4-E11, p.37).
3. **The LM5069-2 breaker: NOT CONFIRMED (B-P1).** Everything else reproduces:
   - limit 18.32 / 21.08 / 23.93 A, breaker threshold 30.21 to 50.59 A;
   - RPWR 8.34 kΩ rounding to 8.45 kΩ, giving 32.52 W at 5.05 mV;
   - timer 0.282 to 0.897 ms, total clearing 1.292 ms;
   - inrush 0.659 A over 40.7 ms;
   - SOA use 0.57 for the fault pulse and 0.58 for the start (my own reading of Figure 10 matches);
   - retry at 1.33 % duty with a 0.222 s dwell;
   - the SMCJ18A clamp.

   On the two reliances: the power limit at 5.05 mV is acceptable under SLVA673A as a condition proven by E-2. The 0.3 V limit is not acceptable as evidence alone for docking.
4. **Q39/Q40 (DD-2): NOT CONFIRMED (B-P2).** The 18.74 to 23.90 A band and 176.5 °C reproduce, and classing it as a design defect owned by L4-E11 rather than a coupon item is right.
5. **The protection table: NOT CONFIRMED for the docking row** (wrong margin, a known rating violation). The other rows, the rejected alternatives (the 15.71 A and 15.21 A arithmetic) and the supported envelope are CONFIRMED AS CONDITIONAL; the envelope must also name B-P1 as a condition.
6. **DD-3, DD-4, IF-1 to IF-4, E-1 to E-8: CONFIRMED AS CONDITIONAL.**
   - DD-3 and DD-4 are right, and IF-1's 40.7 ms is right.
   - E-1 needs restating per B-P2.
   - E-3 records VIN to SENSE but has no acceptance for it.
   - E-4 and E-5 as in the minors.
   - Two evidence items are missing: the installed limit current, and the peak current at key-down.

**Smallest next action.** One revision of section 15, then a targeted recheck:
- correct docking with the make-last contact into UVLO and recompute that row with the derating;
- restate DD-2 and E-1 as a junction limit;
- fold in the minors.

**Owner decision.** L9STK CU, the outer copper weight, is genuinely his: every listed option costs money (the 2 oz surcharge, which is not readable from the public pages, or an in-line holder). It should go to him with the return-apart route listed beside it. Sending Q-TI-L9S-1 to TI is an outside contact, so it is his to send unless the supplier carries it.
