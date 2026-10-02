# T-H1, the empty-case heat balance: test procedure (DRAFT)

MESHSAT-1478 under MESHSAT-1357, task L4-E12, 2 October 2026; revised the same day for the thermal reconciliation (the owner's
amendment of 2 October 2026, 14:20, item 1; the record's section 16). **A draft for the bench, not run; prototype design:
nothing has been bought, built, powered or measured.** It implements TEST-PLAN section 8's row T-H1 (the enclosure half; the
PA patch half stays `feasibility/POWER-THERMAL.md` section 10's) with the hardware of `reviews/READY-TO-ACT.md` section 5.2.
Every figure is printed by `l4e12_thermal.py` in `l4e12_thermal.out`: sections 8 (the record's 13) and 11 (the record's 16).

## 0. Authorisation and acceptance (separate)

- **Authorisation to perform** the test (the bench, the people, the spend on the case, frame, plate blank, heaters, fans and
  loggers) is the owner's. The session drafts; it does not run or buy anything.
- **Acceptance of a result** goes through the coordinator's check of the filed record (section 7 below) against the record's
  section 16: each point's endpoint, its P, its rise, its expanded uncertainty and its verdict. A point is accepted or not on
  that check; the owner's authorisation does not accept it, and a passing point does not authorise anything further.
- **No temperature requirement is relaxed to make a point pass.** A point that fails is reported as failing, with the record's
  fallbacks (section 6).

## 1. Who, where, what hardware

- **Who:** the prototype bench, as Layer 9's physical verification, once the owner authorises it (READY-TO-ACT section 5.3
  lists what is missing: "who runs the test and where (the session cannot)"). A laboratory only if a chamber run is wanted (an
  optional confirming point at +40 C, or E5's +60 C); that is the owner's spend.
- **The configuration:** a current-moulding Peli 1450 with the 1450PF frame and a 3 mm aluminium plate blank in the face's
  place; the case on its feet on a bench, in still room air, shaded (no lamp or window sun on it); the lid open for every point
  but K5, closed for K5.
- **The heat:** resistive heaters on aluminium blanks at the boards' outlines on the kit's standoffs (READY-TO-ACT's stack
  heaters: aluminium-housed wirewound resistors, 50 W class, 6.8 ohm, 21.2 W at 12.0 V); the heaters never touch the PP walls.
- **The fans:** the five fans (the picked fans once D-18 is picked; until then stand-ins of the same class, the mixers Same Sky
  CFM-6025BG68, 12 V, the -22 variant) in their places: the three modules' coolers and the two mixers. Each point runs the fans
  its mode runs: the profile all five (2.970 W in the model), the heat stage and the hold slot 3's cooler and the two mixers
  (1.950 W). **The fans run from their own bench supply channel**, its voltage and current logged.
- **The loggers:** the PicoLog TC-08 of READY-TO-ACT 5.2 plus a second one (sixteen channels, section 3). No electronics are
  needed.

## 2. The heat, counted once, and where it goes

**P = the heaters + the fans, never the heaters alone.** All of each supply's electrical power stays inside the case. To stand
for a mode, the heaters are set to the mode's heat less the fans' **measured** draw, so the fans' real power replaces their
modeled share and nothing is counted twice. The heaters' count is the nearest whole number of READY-TO-ACT's 21.2 W heaters,
each set by V = sqrt(P_heater x 6.8 ohm); the figures below use the model's fan draw and are recomputed from the measured one.

| Point | Mode | Heat into the case | Heaters (model's fans) | Setting |
|---|---|---|---|---|
| K1, K5 (K9) | the heat stage on shore with L4-E8's ballasts | 27.086 W | 25.136 W (1.950 W) | one heater at 13.07 V |
| K10 | E5's hold with the ballasts | 21.587 W | 19.637 W (1.950 W) | one heater at 11.56 V |
| K6 | the profile PS-IDLE-SPEC on the pack | 43.413 W | 40.443 W (2.970 W) | two heaters at 11.73 V each |
| K7, K8 | the profile with a charge on shore | 46.859 W | 43.889 W (2.970 W) | two heaters at 12.22 V each |

**The heaters' distribution.** Spread the heaters' total over the places in proportion (W, plan; the fans excluded, being
real): one resistor per place sized for its share on the same supply, or the heaters on blanks at the largest places with the
smaller places' shares added to the nearest one (record which).

| Place | K1, K5 | K10 | K6 | K7, K8 |
|---|---|---|---|---|
| board B (slot 3, its switch, hubs, supervisors, the device rail; slots 1 and 2 in the profile) | 14.972 | 12.057 | 26.234 | 26.234 |
| board A (converters, logic, distribution, L4-E8's ballasts where counted) | 4.284 | 3.903 | 3.464 | 3.464 |
| the front end and the charger (boards E and A, on shore) | 1.725 | 1.345 | none | 3.446 |
| board C and the face | 1.500 | 1.500 | 7.500 | 7.500 |
| board D and the PA | 1.500 | none | 1.500 | 1.500 |
| board E | 1.155 | 0.832 | 1.155 | 1.155 |
| the pack (its own I2R, at the dummy pack block) | none | none | 0.590 | 0.590 |

## 3. Instrumentation (sixteen channels)

| Channel | Where |
|---|---|
| 1 to 4 | the mixed inside air, mid-height, spread over the stack, away from heaters and fan outlets (the node of G) |
| 5 | the hold's reference place today: board B's TMP117 under the coolers |
| 6 | the air by the +70 C parts' places (the RockBLOCK, board D) |
| 7, 8 | the plate's inner face (centre, edge) |
| 9 | the plate's outer face |
| 10, 11 | a PP wall's inner face (one on the east wall in the pack pocket) |
| 12 | a PP wall's outer face |
| 13 | the floor's inner face |
| 14, 15 | the ambient, about 0.5 m from the case, shaded from it (the other node of G) |
| 16 | the dummy pack block (FEA-008's) |

Before each series, compare every junction at one temperature (an hour's isothermal soak of the open, unpowered case, or a
stirred bath), record the offsets and subtract them; the budget takes each channel at +-0.2 K after that.

## 4. Run order and duration

The points, in this order: **K1** first (it closes the most), then **K5** (lid closed), **K10**, **K6**, and **K7 and K8**
(one point: one heat, two needs). Optional: the fans-off case at K1's heat (the failure case, no pass line), and a confirming
point in a chamber at +40 C.

Each point's time constant is tau = C / G, with C = 10 kJ/K (appendix 32.53's upper bound for the kit, and so for the empty
case). At its pass line a point is steady within 1 % of its rise at ln(100) tau, then one hour is averaged:

| Point | tau at the pass line | Steady at | The fit's three time constants |
|---|---|---|---|
| K1, K5 | 1.42 h | 6.5 h | 4.3 h |
| K10 | 1.13 h | 5.2 h | 3.4 h |
| K6 | 1.84 h | 8.5 h | 5.5 h |
| K7, K8 | 1.64 h | 7.5 h | 4.9 h |

A case as poor as the conservative bound takes up to 21.1 h a point. Points run unattended between settings; a point starts
from the previous one's steady state or from room temperature, and its own first-order transient is what the fit reads.

## 5. Endpoint and data reduction

**The endpoint**, either of:
- **steady state:** the mixed air (the mean of channels 1 to 4) drifts at most 0.1 K/h over an hour; then one hour is averaged;
- **a transient fit:** theta(t) = theta_ss + (theta_0 - theta_ss) exp(-t/tau) fitted to the mixed air's rise over at least three
  time constants, with residuals at most 0.05 K RMS and the fitted tau within a factor 2 of C/G (C 8 to 10 kJ/K, G the
  point's reading); theta_ss's fitted standard error joins the rise's uncertainty.

**The reduction:**
- P: the heaters' electrical power plus the fans' (both supplies' V x I, averaged over the hour); all of it inside the case.
- The rise: the mean of channels 1 to 4 less the mean of channels 14 and 15 (or theta_ss from the fit).
- G = P / rise, per point.
- The plate fraction (channels 7, 8 over the rise), the wall fraction (10, 11), the floor fraction (13): they replace W4's
  0.465 to 0.725, 0.541 to 0.781 and 0.588 to 0.898.
- The hold reference's offset: channel 5 less channel 6.
- Uncertainty (standard, k = 1): each channel 0.2 K, the mixed air's spread 0.3 K (replace it by the measured standard
  deviation of the mean of channels 1 to 4), the ambient's drift 0.3 K, the steady-state residual 0.129 K (or the fit's
  standard error); the power 0.7 %, the leads 0.5 %. Expanded (k = 2) at each point's own rise: 7.8 % at K1's 13.8 K, 12.1 % at
  K10's 8.8 K, 4.0 % at K6's 28.8 K.
- No translation credit is taken: at the same rise the model gives the +40 C conductance 1.6 to 3.7 % above the room's, so the
  room reading is the conservative side.

## 6. Pass, fail, inconclusive, and what each result decides

Per point: **pass** when the reading less its expanded uncertainty is at or over the condition's need (the reading at or over
the threshold below); **fail** when it is under; **inconclusive** when the endpoint is not met, or in the averaging hour the
supply or a fan's draw moves by more than 1 % or the ambient by more than 1 K (the point is repeated).

| Point (lid open, fans on unless named) | Need | Pass at a reading of at least | Decides |
|---|---|---|---|
| K1 at 27.086 W | 1.806 W/K | 1.958 W/K | closes K1, K3, K4 and K9: REQ-024 and E3-A at +40 C (the heat stage's air under the SGP41's +55 C, the +70 C class, the module's intake) and E3-O's +70 C class at +55 C (K3 needs 0.903 W/K, read at 0.941 W/K; K4 0.602 W/K, read at 0.620 W/K; both under K1's threshold) |
| the same point | 2.709 W/K | 3.081 W/K | also meets K2 (the SGP41 on Table 4) and E5 without the hold (27.086 W over 10 K); K2 itself stays the owner's (CFL-002) |
| K5 at 27.086 W, lid closed | 1.806 W/K | 1.958 W/K | closes K5: REQ-052 and E3-L at +40 C |
| K10 at 21.587 W | 2.159 W/K | 2.455 W/K | U-02's line in E5: the hold keeps the +70 C class |
| K6 at 43.413 W | 1.447 W/K | 1.508 W/K | the profile unshed at REQ-014's +20 C (under C1's +50 C) |
| K7, K8 at 46.859 W | 1.627 W/K and 1.977 W/K | 1.698 W/K and 2.081 W/K | charging with the profile on SC-37's design day, cold and warm ends; the cells' own rise over the air stays U-01's |
| fans off, K1's heat | none | none | the failure case: the coupled parts' plate at most 69.82 C on W4's still values; the controls act on the air in any case |
| channel 5 less channel 6 within +-0.899099 K | | | the hold's trigger window exists with the reference where it is; otherwise the reference moves to the mixed air |

**If K10 fails** (under 2.455 W/K): the session's fallbacks of the record's section 13 apply (the plate coupling F4, holding E5
to 1.564 W/K; the deeper hold F3, to 1.552 W/K; both together to 1.125 W/K; fins F1 sized from the measured split). **If K1
fails** (under 1.958 W/K): the plate coupling holds E3-O's +70 C class to 1.399 W/K (1.309 W/K with the +80 C connectors out of
the exhaust), but the SGP41's +55 C at +40 C (K1) then stays unmet, and a deviation or a device-set re-pick is the owner's.
U-02's line in E5 is 2.159 W/K throughout.

**What this revision replaces:** the earlier single pass line of 2.416 W/K at a 10 K rise (2.285 W/K at 20 K) at one heater's
21.2 W, and the eight-point matrix at 21.2 W and 42.4 W (3.6 to 10.5 h a point, 29 to 84 h in all). They took P at the
heaters' setting rather than each mode's heat with the fans counted; the points above read each condition at its own heat.

## 7. The record to keep

A dated record in the tree, in a format the runner can read, per point:
- the logger's files (all sixteen channels, the sampling interval, the junction offsets of the soak);
- both supplies' voltage and current over the whole point, and the fans' draw per fan where measurable;
- the configuration: lid open or closed, which fans ran, the heaters' places and settings, photographs of the heaters and the
  junctions' places, the room and the ambient channels' placement;
- the endpoint met (drift or fit, with the fit's tau, theta_ss, its standard error and the residual RMS);
- P, the rise, G, the expanded uncertainty and the verdict (pass, fail or inconclusive), with the reduction script's output;
- who ran it, where and when, under which authorisation.

The coordinator's check reads that record against the record's section 16 before any point counts. The supplies are
current-limited.
