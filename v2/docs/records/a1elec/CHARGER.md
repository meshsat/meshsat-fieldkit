# CHARGER: board A's charger and entry figures that follow from Option A(i) (stream a1elec, MESHSAT-1357)

29 September 2026, second issue after the independent AI check (`_scratch/chk-a1elec/CHECK.md`, items B1, M1 to M4, M8).
**Prototype design, AI review. DRAFTS for board A's generator owner and the firmware contract's writer: nothing here is
applied to a generator, and nothing is measured.** Figures are `energy_two_pack.out` (named by section) or quoted from
the maker's document with its section and page. **Rule used throughout: a limit that must hold a load is taken at its
minimum, and a setting that must stay under a limit is taken at its maximum.**

## 1. The entry as generated, and what the design case needs

**The front end (LM5176 U2) regulates its output current at VSNS 43 / 50 / 57 mV min / typ / max** (TI SNVSAI1D 6.5,
PDF page 7, the constant current loop; held `v2/vendor/ti/lm5176-datasheet.pdf`), over R11 10 mOhm: **4.3 / 5.0 / 5.7 A**
at 20.7 V, 89.0 / 103.5 / 118.0 W. `gen_sch_e.py:104-107` quotes the same triple and uses the 57 mV maximum to size
copper. The first issue of this page took 5.7 A as the limit; that was wrong (check item B1).

**The entry requirement** (`.out` 5, lid at 13.23 C, base +20 C, 400 Wp into a 200 W stage): the current into U3 at
VBUS20's 20.7 V that a limit must hold at its minimum is **at least 5.56 A (115.1 W) to meet M1 at all**, and **5.81 A
(120.3 W) to keep the lowest point the unconstrained case reaches, 31.1 Wh**. That is what board A's re-rate must
guarantee; nothing in M1 needs more.

**What each entry case gives on the model** (`.out` 5):
- **E0, FW-A16 as written** (53.9 W into U3 with the panel's tracker on VIN_RAW): **NOT MET**, stops at hour 38 / 26,
  869.1 Wh unserved. FW-A16's 80 percent rule was written for the vehicle entry's LM5069 (O-33 records the panel case).
- **E1, board A as generated with FW-A16 revised for the panel**: U3's IIN_HOST at **4.15 A** nominal (code 83; **4.25 A
  maximum** with the 100 mA the register text adds at 10 mOhm, SLUSE66A 9.6.22, page 80), under the front end's 4.3 A
  minimum, so U3's input loop holds the bus: 85.9 W into U3. **NOT MET**, stops at hour 44 / 32, 374.5 Wh unserved, at
  any lid temperature up to +40 C, and still NOT MET with 650 or 800 Wp. The as-generated front end with U3 set just
  under each of its limits: 4.3 A NOT MET (329.4 Wh unserved), 5.0 A NOT MET (119.1 Wh), 5.7 A MEETS (18.6 Wh). So board
  A as generated does not carry Option A(i) with a minimum or a typical part.
- **E2, the entry re-rated as drafted** (section 2: R11 6.2 mOhm, U3's IIN_HOST 6.2 A): 128.3 W into U3. **MEETS**,
  lowest 31.1 Wh, down to a lid at +9.6 C.
- **E3, no cap under the stage's window** (the unconstrained reference): MEETS with the same 31.1 Wh; its busiest hour
  asks 8.20 A, which E2 does not need to supply (both packs are full by 13 UTC each day, so the lowest point is one night
  from full whatever the midday peak).

**Taken by the session: re-rate the entry** (reason: E1 fails even at 800 Wp, and the array is carried by a person;
the entry is a few parts on one board; the threshold above, 5.56 A at the minimum, is the figure the generator owner
sizes to).

## 2. The drafted settings and changes

**Needed for M1** (the minimum re-rate):
- **R11 6.2 mOhm** on the front end: 43 / 50 / 57 mV over 6.2 mOhm = **6.94 / 8.06 / 9.19 A** (143.6 W at the minimum).
  The generator owner checks the LM5176 stage (inductor, FETs, output capacitors, copper) at the **9.19 A maximum**
  against SNVSAI1D; this stream has not. **VBUS20** re-declared at 6.2 A continuous (U3's setting) and 9.19 A at the
  front end's maximum limit.
- **U3 IIN_HOST 6.2 A nominal** (code 124 at 50 mA with R16 as generated, 10 mOhm and RSNS_RAC = 0b; **6.3 A maximum**
  with the register text's 100 mA, under the 6.35 A clamp of SLUSE66A 9.3.5, page 25, and **under the re-rated front
  end's 6.94 A minimum**, so U3's loop holds the bus in every part), above the requirement's 5.81 A.
- **FW-A16 revised**: its 80 percent rule stays for the vehicle entry; with the panel's tracker feeding VIN_RAW (board E's
  VIN_MON and the tracker's state tell which), IIN_HOST is 6.2 A.
- **ChargeCurrent at most 3.968 A** (code 31 x 128 mA, Table 9-7, page 40; section 8a's 4.0 A for the 4S6P base).

**Margin choices, not M1 needs** (check item M4): at E2's busiest hour U3 delivers 125.8 W = **8.68 A** at the model's
14.5 V node, so **U3's L2 peaks at 10.32 A at 400 kHz** (ripple 3.29 A p-p) and 9.50 A at 800 kHz (`.out` 7), under the
12.2 A of its value text. Replacing L2 with a Coilcraft **XAL1010-332ME** (3.3 uH, Isat 27.4 A, Irms 18.2 A, DCR 3.70 /
4.10 mOhm; held `v2/vendor/power/coilcraft-xal1010.pdf`), moving to **800 kHz** (Table 9-4 pairs 3.3 uH with 800 kHz;
the direction S-117 points, its decision stays with board A's owner) and **R16 to 5 mOhm** (RSNS_RAC = 1b) are margin
and loss choices for board A's owner. **L2 as generated** carries the value text "3.3uH XAL6030-332ME (Isat 12.2 A)" on
footprint key L6060 (XAL6060 class), and no Coilcraft XAL6030 or XAL6060 sheet is held: a pre-existing generator
mismatch for board A's owner (`gen_sch_a.py:861`), not an a1elec change (check item M8). The **IADPT resistor, 169 k**
(Table 9-4; missing today, round 4's O-24) is needed for the inductance detection whatever is chosen.

**U3B (the lid's charger, new; second issue, stream s119, by the session decision of `records/s119/apply_decision_s119.py`)**,
TOPOLOGY.md 3b: U3's 400 kHz row, R16B 10 mOhm (RSNS_RAC = 0b) and R17B 5 mOhm (RSNS_RSR = 1b), 191 k on IADPT, L2B
XAL1010-472ME, Q7B and Q9B CSD17578Q5A, Q8B and Q10B CSD17577Q5A, Table 9-5's 400 kHz compensation, ChargeVoltage 16.8 V,
ChargeCurrent at most **7.936 A** (code 62) and never above 2 x the lid gauge's ChargingCurrent(), IIN_HOST **6.2 A**
nominal (code 124; 6.3 A maximum; the 6.35 A clamp of 9.3.5, page 25), VINDPM 12.0 V, the fail-safe HiZ enable with the
ILIM_HIZ divider at 3.48 V (6.2 A on 10 mOhm). The first issue's instruction to write EN_FAST_5MOHM 0b on U3B lapses with
its 5 mOhm sense (SLUSE66A Table 9-1, page 26, gives 6.35 A at RSNS_RAC = 0b whatever the bit); it still applies to U3 if
its R16 ever becomes 5 mOhm (check item M1). The first issue's U3B (5 mOhm, 169 k, XAL1010-332ME, 8.0 A, CSD18510Q5B) is
superseded: its REGN could not drive those FETs. A deeply discharged lid is charged at the charger's battery
low-voltage clamp, 384 mA (SLUSE66A 9.3.5, page 25), until its cells recover.

**Board E, listed and not designed here** (its owner's): the 200 W stage itself. At 200 W in and 0.93, TRK_OUT carries
12.3 A at 15.1 V against its declared 6.16 A and F2's and J_SOLAR's 10 A; the panel wiring of 9g way (i) (two series
pairs, about 50 V open circuit cold) is above REQ-016's 25 V, a requirement the owner rules on (9i of the energy record).

## 3. The losses at those settings and the thermal load on board A

At E2's busiest hour (`.out` 7), second issue (stream s119): the chain's figures are 0.93 for the front end, 0.979 for U3
and 0.972 for U3B, each by TI's method with its sense resistors INSIDE it (the first issue's table, at 0.98 and 0.975,
also listed R16, R17, R16B and R17B beside the chargers and so counted them twice; the independent check of stream s119,
item M3):

| element | E1, as generated (U3 at 4.15 A, 85.9 W) | E2, drafted (U3 at 6.2 A, 128.3 W) | E3, unconstrained peak (8.20 A) |
|---|---|---|---|
| front end U2 | 6.5 W | **9.7 W** | 12.8 W |
| U3 (R16 and R17 inside) | 1.8 W | **2.7 W** (R16 0.38 W, R17 0.02 W) | 3.6 W |
| U3B (R16B and R17B inside) | none | **1.5 W** (55.2 W in; R16B 0.15 W, R17B 0.07 W) | not re-derived |
| **board A, charging peak** | **about 8.3 W** | **about 13.9 W** | at least 16.4 W with U3B |

The lid path at night (1.97 A): LM74700 0.039 W, the LM5069's FET 0.004 W, its 5.6 mOhm sense 0.022 W. **In current
limit the LM5069 holds its FET linear**, so the FET takes the gap less the loops' drop: 1.0 W at a 1.0 V gap, 12.0 W at
2.0 V and **42.7 W at 4.8 V** (`.out` 8), until its power limit and fault timer (PWR and TIMER, sized by board A's owner
with SNVS452G's procedure) turn it off; the -2 variant retries (check item M3; the first issue's 0.12 W was the fully
enhanced FET). Over the 72 hours the lid chain costs the model 25.1 to 35.6 Wh in U3B, 4.7 to 6.7 Wh in the charge loop
(second issue; the first issue's 22.3 to 31.7 and 5.7 to 8.2 Wh are superseded) and **6.0 Wh** in the discharge path (`.out` 3c; the first issue's 5.5 Wh was a stale reading, check item M2), all
inside the balance that meets M1.

**Not computed here:** the temperature those watts produce. Board A sits in the closed base; E2 adds about 5.6 W to the
as-generated charging peak, at midday, while the base's inside air is warmest. `feasibility/POWER-THERMAL.md`'s owner
re-runs it with board A at about 13.9 W at the charging peak (second issue; the first issue's 14.2 W is superseded). No part's rating is claimed against a temperature in this record.

## 4. What remains a bench item

U3's and U3B's efficiencies at these points (second issue: 0.979 and 0.972 by TI's method on the makers' figures, the
inductors' core loss excluded; the first issue's 0.98 and 0.975 were plot readings at other conditions); the front end's
0.93 at 6.2 A and its current limit at the re-rated R11; the IADPT detection at 191 k (U3 and U3B);
the compensation at the chosen frequency; U3B's input loop holding the node while the base supplies the load (the
allocation loop's reaction time); the LM5069's power limit and timer at a join and at the kit's 18 A peak; the ideal
diode's reverse response on a harness short.
