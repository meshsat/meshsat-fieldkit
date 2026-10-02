# T-H1, the empty-case heat balance: test procedure (DRAFT)

MESHSAT-1478 under MESHSAT-1357, task L4-E12, 2 October 2026. **A draft for the bench, not run; prototype design: nothing
has been bought, built, powered or measured.** It implements TEST-PLAN section 8's row T-H1 (the enclosure half; the PA
patch half stays `feasibility/POWER-THERMAL.md` section 10's) with the hardware of `reviews/READY-TO-ACT.md` section 5.2.
Every figure is printed by `l4e12_thermal.py` in `l4e12_thermal.out` section 8 (the record's section 13).

## 1. Who, where, what hardware

- **Who:** the prototype bench, as Layer 9's physical verification, once the owner authorises it (READY-TO-ACT section 5.3
  lists what is missing: "who runs the test and where (the session cannot)"). A laboratory only if a chamber run at E5's
  +60 C is wanted; that is the owner's spend.
- **Hardware:** a current-moulding Peli 1450 with the 1450PF frame and a 3 mm aluminium plate blank; resistive heaters on
  aluminium blanks at the boards' outlines on the kit's standoffs; the five fans (the picked fans once D-18 is picked;
  until then stand-ins of the same class, the mixers Same Sky CFM-6025BG68, 12 V, the -22 variant); a bench supply with
  its voltage and current logged; the PicoLog TC-08 of READY-TO-ACT 5.2 plus a second one (sixteen channels, section 3).
  No electronics are needed.

## 2. The heat and where it goes

The first power point is E5's hold as the model spreads it (W, plan; `l4e12_thermal.out` 8d):

| Place | W |
|---|---|
| board B (slot 3, its switch, hubs, supervisors, the device rail) | 12.06 |
| board A (converters, logic, distribution) | 1.81, plus L4-E8's ballasts 2.09 |
| board C and the face | 1.50 |
| the front end and the charger (boards E and A, on shore) | 1.35 |
| board E | 0.83 |
| the fans themselves (run from the bench supply) | 1.95 |

One stack heater of READY-TO-ACT's (6.8 ohm at 12.0 V, 21.2 W) carries about that heat; spread it over the places above in
proportion, or use one resistor per place sized for its share. The second power point is two heaters, 42.4 W. The fans'
own electrical power is heat inside the case and counts in P.

## 3. Instrumentation (sixteen channels)

| Channel | Where |
|---|---|
| 1 to 4 | the mixed inside air, mid-height, spread over the stack, away from heaters and fan outlets |
| 5 | the hold's reference place today: board B's TMP117 under the coolers |
| 6 | the air by the +70 C parts' places (the RockBLOCK, board D) |
| 7, 8 | the plate's inner face (centre, edge) |
| 9 | the plate's outer face |
| 10, 11 | a PP wall's inner face (one on the east wall in the pack pocket) |
| 12 | a PP wall's outer face |
| 13 | the floor's inner face |
| 14, 15 | the ambient, about 0.5 m from the case, shaded from it |
| 16 | the dummy pack block (FEA-008's) |

Before each series, compare every junction at one temperature (an hour's isothermal soak of the open, unpowered case, or a
stirred bath), record the offsets and subtract them; the budget below takes each channel at +-0.2 K after that.

## 4. Run matrix and steady state

Eight points: lid open and lid closed, fans on and fans off, at 21.2 W and 42.4 W. Run lid open with the fans first (the
pass line). A point ends when the mixed air drifts at most 0.1 K/h over the last hour, then one hour is averaged. The
case's time constant C/G is 0.78 to 2.27 h (appendix 32.53's 8 to 10 kJ/K for the kit, an upper bound for the empty case,
over W4's lid-open 1.22 to 2.85 W/K), so a point takes 3.6 to 10.5 h to come within 1 % of its rise and the eight take
29 to 84 h, unattended between points.

## 5. Data reduction

- P: the heaters' electrical power plus the fans'; all of it inside the case.
- The rise: the mean of channels 1 to 4 less the mean of channels 14 and 15.
- G = P / rise, per point; interpolate between the two powers to E5's 10 K rise (the line's 21.2 W gives about 9.8 K).
- The plate fraction (channels 7, 8 over the rise), the wall fraction (10, 11), the floor fraction (13): they replace W4's
  0.465 to 0.725, 0.541 to 0.781 and 0.588 to 0.898.
- The hold reference's offset: channel 5 less channel 6.
- Uncertainty (standard, k = 1): each channel 0.2 K, the mixed air's spread 0.3 K (replace it by the measured standard
  deviation of the mean of channels 1 to 4), the ambient's drift 0.3 K, the steady-state residual 0.129 K; the power 0.7 %,
  the leads 0.5 %. Expanded (k = 2): 10.7 % at a 10 K rise, 5.5 % at 20 K.

## 6. Pass lines and what each result decides

| Result (lid open, fans on unless named) | Decides |
|---|---|
| G less its expanded uncertainty at or over 2.159 W/K: a reading of at least 2.416 W/K at a 10 K rise (2.285 W/K at 20 K) | U-02's line met: E5 under the hold holds the +70 C class |
| at or over 2.709 W/K, after the same deduction | no hold is needed in E5 |
| between 1.806 and 2.159 W/K | E3-O holds as stated, E5 does not: the session's fallbacks of L4-E12 section 13 (the plate coupling F4, holding E5 to 1.564 W/K; the deeper hold F3, to 1.552 W/K; both together to 1.125 W/K; fins F1 sized from the measured split) |
| under 1.806 W/K | E3-O fails as well: the plate coupling holds E3-O to 1.399 W/K (1.309 W/K with the +80 C connectors out of the exhaust); under that, a deviation of E3-O or a device-set re-pick, the owner's |
| fans off | the failure case: the coupled parts' plate at most 69.82 C on W4's still values; the controls act on the air in any case |
| lid closed | E3-L's inside air, and where the SGP41's channel stops if the owner takes option C (L4-E12 section 8) |
| channel 5 less channel 6 within +-0.899099 K | the hold's trigger window exists with the reference where it is; otherwise the reference moves to the mixed air |

The run is at room temperature. The outside films' radiation grows from the room to E5's +60 C, so the margin's conductance
is 1.15 to 1.20 times the room's on W4's films (INFERRED); the pass line does not take that credit. A chamber run at +60 C
would let the bench take it.

## 7. Records

The logger's files per point, the supply's voltage and current, the fans' drawn power, and photographs of the heaters and
the junctions' places go to a dated record in the tree, in a format the runner can read. Heaters sit on aluminium blanks and
never touch the PP walls; the supply is current-limited.
