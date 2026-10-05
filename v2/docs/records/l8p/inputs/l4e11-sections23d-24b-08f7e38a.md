### 23d. The selection (SESSION)

| Decision | Authority | Why no owner judgement stands | Reversed by |
|---|---|---|---|
| **(B).** It is the only one of the three that leaves the copper as board A's, gives each device's power and junction with no assumption about sharing, and can impose the worst split itself. It costs a gate driver per device, a sequencer and a threshold calibration whose repeatability the specimen must show | SESSION (ruled by the L4-E11 author, 4 October 2026, under the owner's standing rules of 21 and 26 September 2026) | a measurement method inside the task: no money committed, no requirement changed, no reserved line; (C) cannot decide the acceptance and (A) changes the copper it measures | the two threshold calibrations (before and after the runs) differing by more than 0.5 K, or the matrix failing reciprocity beyond the budget, or no supplier agreeing to the setup: then (A), judged on the 40.78 K/W bar alone with the VBAT copper's allowance named as owed; (C) only as a cross-check |

**The first prototype of board A is not a specimen for (B) as drafted:** its three gates share CH_BATDRV. It becomes one only with a
removable link in each gate branch, a change to the charger draft and the layout that is **not drafted here** (owed before the
prototype's layout).

### 24b. The fixture redrawn (SESSION; MAKER rows; the switch figures are PROPOSALS for the supplier's parts)

A series switch **SW_S** in the heating supply's + lead, between the supply and the VBAT pour; the bypass **SW_B** onto a dummy leg
(proposal: 5 mOhm with SW_B) across the supply's terminals on the supply's side of SW_S; the shunt in the supply's - lead from the
CH_BATQ pour. Gate k is tied for a reading to **tap Dk's own line** (V2R-m3), and the reading is V(tap Sk, tap Dk), which is then the
gate's VGS. The current paths:

| State | SW_S | SW_B | Gate k | The other gates | Current path |
|---|---|---|---|---|---|
| calibration (oven) | open | closed (the supply off or on into the dummy leg) | tied to tap Dk | on VBAT | I_M (+) -> VBAT pour -> channel k at threshold -> CH_BATQ pour -> I_M (-) |
| heating | closed | open | 10 V under VBAT | on VBAT | I_H (+) -> SW_S -> VBAT pour -> channel k -> CH_BATQ pour -> shunt -> I_H (-); I_M also flows in channel k |
| sensing | open | closed (I_H into the dummy leg) | tied to tap Dk | on VBAT | as calibration; I_H circulates through SW_B and never reaches the pours |

**The reading's sequence** (proposal; the procedure's step 7): SW_B closes; 10 us later SW_S opens (t = 0, read on the shunt: the coupon's
current falls to the sense current); 2 us later gate k leaves its driver's -10 V output and is tied to tap Dk, interlocked so it can only
happen with the shunt under 10 mA; samples from 100 us to 10 ms; then the gate back to -10 V, SW_S closes, SW_B opens. One reading in
1 s: the heating is off 1 % of the time, and each power is averaged over the whole cycle. The interlock is the hardware form of the
safety rule: a gate in the threshold connection never meets a closed SW_S (the clamp state of 24a). Through every step the device under
test's channel is the only one conducting between the pours: its gate stays 10 V under VBAT until SW_S is open. In the 10 us between
SW_B's closing and SW_S's opening the current divides between the dummy leg and the coupon by their resistances, SW_S's on-resistance
among them: those microseconds and the switch's own opening enter the early-time correction's term (24f), and t = 0 is SW_S's opening
as the shunt reads it.

**Each state, the device under test alone, with its margin:**

| Sensing and calibration (the same connection): every conductor across the pours but the device under test | At most | Label |
|---|---|---|
| the two off FETs, IDSS at 125 C (printed at VDS -30 V; at most 3.1 V here) | 20 uA | MAKER (Table 7 p.6: 1 uA at 25 C, 10 uA at 125 C each) |
| the device under test's gate on its drain, IGSS | 0.1 uA | MAKER (Table 7 p.6: 100 nA at 20 V, 25 C) |
| SW_S open | 1 uA | PROPOSAL (at 20 V, either polarity, the laboratory's temperature) |
| the gate drivers' six open switches | 6 uA | PROPOSAL (1 uA each at 15 V) |
| the three digitiser inputs | 0.9 uA | PROPOSAL (10 MOhm at the threshold's largest 25 C row) |
| **in all** | **28 uA, 2.8 % of the 1 mA** | the device under test carries at least 97.2 % of the sense current, 100 times the largest other conductor |

- Over 125 C Nexperia prints no leakage: check V3 reads it at the top calibration temperature with the fixture connected.
- **The fixture's part, 0.79 %,** sits outside the chamber and the oven at the laboratory's temperature, so it is the same in calibration
  and in a reading and moves both alike; V3 reads it before and after the runs.
- **SW_S open sees at most 3.11 V** (the threshold's largest row and the dummy leg's drop at 22.46 A) against its 20 V rating. A one-way
  element (a single MOSFET's body diode) would conduct in one polarity, so SW_S blocks both: two MOSFETs source to source, or a relay
  (proposal).
- **Heating:** the device under test carries 8.46 to 22.46 A at 0.11 to 0.292 V. The two off FETs see VGS 0 and that VDS, so their
  body diodes are reverse-biased, and every other conductor carries at most 26.1 uA: the device under test carries 3.2e5 times the rest at
  the least heating current. The sense current also flows in the conducting channel, 0.012 % of its power, counted. The shunt and the taps
  sit inside SW_S, so SW_S's on-resistance enters no power: only the supply's compliance, logged (validity check V7).
- **The settling before the first sample:** the pours' node moves on the sense current alone across about 11.6 nF (three Ciss near 0 V,
  typical, 2.87 nF each, Fig. 12 as read in 16b; SW_S open 2 nF and the fixture's 1 nF, proposals): 34.8 us to the threshold's largest
  row, 2.87 times inside the first sample at 100 us. The control run (V2R-m4, below) reads it on the specimen.

