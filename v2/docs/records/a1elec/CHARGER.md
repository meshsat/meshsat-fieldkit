# CHARGER: board A's charger and entry figures that follow from Option A(i) (stream a1elec, MESHSAT-1357)

29 September 2026. **Prototype design, AI review. DRAFTS for board A's generator owner and the firmware contract's
writer: nothing here is applied to a generator, and nothing is measured.** Figures are `energy_two_pack.out` (named by
section) or quoted from the maker's document with its section and page.

## 1. What the design case asks of board A

The design case is 400 Wp into a 200 W stage (the energy record's 9g way (i)), the lid at 13.23 C, the allocation
'ah', start 06:00 UTC (`.out` 7). At the hour U3 delivers most (hour 30, 12:00 UTC):

| quantity | figure | as generated | verdict |
|---|---|---|---|
| sun offered at the node | 166.3 W | | |
| front end (LM5176 U2) output | 169.6 W = **8.20 A** on VBUS20 at 20.7 V | limit 5.7 A (VSNS 57 mV over R11 10 mOhm) = 118.0 W | **exceeded** |
| U3's input (through R16) | 8.20 A | R16 10 mOhm, RSNS_RAC = 0b: IIN_HOST clamped at 6.35 A (SLUSE66A 9.3.5, page 25) | **exceeded** |
| U3's output at the node | 166.3 W = **11.47 A** at 14.50 V: load 42.8 W, base 41.2 W (2.84 A), U3B 82.3 W (5.68 A) | | |
| U3's L2 peak (buck, 3.3 uH) | 13.11 A at 400 kHz (ripple 3.29 A p-p); 12.29 A at 800 kHz | XAL6030-332ME, Isat 12.2 A by its value text | **exceeded at both** |
| VBUS20 | 8.20 A continuous for the hours around noon | declared 6.0 A typical, 8.0 A peak | **exceeded** |
| U3B's input from VBAT | 5.68 A (82.3 W) at this hour; 8.0 A nominal ceiling | new part | |
| lid charge | 5.48 A into the lid (the node's surplus binds, not U3B's 7.936 A) | new | |

**What each entry case gives on the model** (`.out` 5, lid at 13.23 C, base +20 C):
- **E0, FW-A16 as written** (U3's input at most 0.80 x 4.80 A x 0.93 x VIN_RAW / 20.7 V, which with the panel's
  tracker on VIN_RAW at 15.1 V is 53.9 W): **NOT MET**, stops at hour 38 / 26, 869 Wh unserved. FW-A16 was written for
  the vehicle entry's LM5069 (O-33 records the panel reduction); with the panel it throttles the charger to about a
  third of what the design needs.
- **E1, board A as generated with FW-A16 revised for the panel** (U3's IIN_HOST at 5.40 A, about 5 percent under the
  front end's 5.7 A so that U3's loop, not the front end's current limit, holds the bus: 111.8 W in, 109.5 W at the
  node): **NOT MET**, stops at hour 48 / 59, 35.8 Wh unserved; it meets only with the lid at **+17.4 C** or warmer, or
  with **650 Wp** (lowest 52.9 Wh).
- **E2, the entry re-rated** (nothing under the stage's window caps the node): **MEETS**, lowest 31.1 Wh, down to a lid
  at +9.6 C.

So the entry of board A must be re-rated for Option A(i) at 400 Wp, or the array must grow to about 650 Wp with the entry
as generated. **Taken by the session: re-rate the entry** (reason: the array is carried by a person and its area is the
kit's claimed form, 9i of the energy record; the entry is a few parts on one board; reverse by 650 Wp and E1).

## 2. The drafted settings and changes (E2)

**U3 (the base's charger, as today):**
- **R16 5 mOhm** (RAC) with **RSNS_RAC = 1b**, and the **IADPT resistor 169 k** (SLUSE66A 9.3.11 and Table 9-4: 169 k
  for 3.3 uH, "recommended for 800 kHz"; the resistor is missing today, open item O-24 of round 4): with RSNS_RAC = 1b
  and 3.3 uH, Table 9-1 (page 26) allows **10 A** of input current.
- **PWM_FREQ 800 kHz** (ChargeOption0; TI pairs 3.3 uH with 800 kHz in Table 9-4), with Table 9-5's 800 kHz
  compensation network (O-24): this answers S-117's frequency question in the direction the maker's table points.
- **IIN_HOST 8.6 A nominal** (code 86, SLUSE66A 9.6.22 Table 9-50, page 80; 8.8 A maximum with the register text's
  200 mA), above the design case's 8.20 A and under the front end's new limit.
- **L2 Coilcraft XAL1010-332ME** (3.3 uH, DCR 3.70 / 4.10 mOhm, Isat 27.4 A, Irms 18.2 A at a 20 C rise; held
  `v2/vendor/power/coilcraft-xal1010.pdf`) in place of XAL6030-332ME: the design case's 12.29 A peak at 800 kHz is 45
  percent of its Isat; its copper loss at 11.47 A is 0.54 W at the maximum DCR.
- **ChargeCurrent at most 3.968 A** (code 31 x 128 mA, Table 9-7, page 40; section 8a's 4.0 A for the 4S6P base).
- **FW-A16 revised**: its 80 percent rule applies to the vehicle entry; with the panel's tracker feeding VIN_RAW
  (board E's VIN_MON and the tracker's state tell which), IIN_HOST follows the tracker's power instead.

**The front end (LM5176 U2)**: **R11 6.0 mOhm** (57 mV / 6.0 mOhm = 9.5 A at 20.7 V, 197 W out), with its inductor,
FETs and output capacitors re-checked at 9.5 A by the generator owner against the held `v2/vendor/ti/lm5176-datasheet.pdf`
(this stream has not read the LM5176's VSNS tolerance or its power stage; the 57 mV is the figure `energy_inputs.yaml`
quotes). **VBUS20** re-declared at 8.2 A continuous, 9.5 A at the limit.

**U3B (the lid's charger, new)**: TOPOLOGY.md 3b: R16B and R17B 5 mOhm (RSNS_RAC = RSNS_RSR = 1b), 169 k on IADPT,
800 kHz, L2B XAL1010-332ME, ChargeVoltage 16.8 V, ChargeCurrent at most 7.936 A (code 62) and never above 2 x the lid
gauge's ChargingCurrent(), IIN_HOST 8.0 A nominal (code 80; 8.2 A maximum), VINDPM 12.0 V, the HiZ interlock. A
deeply discharged lid is charged at the charger's battery low-voltage clamp, **384 mA** (SLUSE66A 9.3.5, page 25),
until its cells recover: gentler than the gauge's 4.2 A pre-charge figure, and the gauge's PCHGC (500 mA true over the
request) does not trip on a smaller current.

**Board E, listed and not designed here** (its owner's): the 200 W stage itself. At 200 W in and 0.93, TRK_OUT carries
12.3 A at 15.1 V against its declared 6.16 A and F2's and J_SOLAR's 10 A; the panel wiring of 9g way (i) (two series
pairs, about 50 V open circuit cold) is above REQ-016's 25 V, a requirement the owner rules on (9i of the energy record).

## 3. The losses at those settings and the thermal load on board A

At the design case's busiest hour (`.out` 7; the chain's own figures, 0.93 for the front end, 0.98 for U3, 0.975 for U3B):

| element | as generated, at its limit | design case, E2 |
|---|---|---|
| front end U2 | 8.9 W (118.0 W out at 0.93) | **12.8 W** (169.6 W out) |
| U3 | 2.2 W (111.8 W in at 0.98, E1) | **3.4 W** (169.6 W in) |
| R16 | 0.29 W (5.40 A, 10 mOhm) | **0.34 W** (8.20 A, 5 mOhm) |
| L2 copper | (inside U3's 0.98) | 0.54 W at 4.10 mOhm (inside U3's 0.98) |
| R17 | 0.04 W | 0.04 W (2.84 A) |
| U3B | none | **2.1 W** (82.3 W in at 0.975) |
| R16B, R17B | none | 0.16 W, 0.15 W |
| lid path at night (1.97 A) | none | 0.065 W (LM74700 0.039, FET 0.004, 5.6 mOhm 0.022) |
| **board A, charging peak** | **about 11.4 W** | **about 19.0 W** |

At the lid path's largest current (its limit's maximum, 11.0 A, a join or a peak) the ideal diode dissipates 0.22 W, the
LM5069's FET 0.12 W and its sense 0.68 W (`.out` 7), for the fault timer's duration. Over the 72 hours the lid chain
costs the model 22.7 to 32.7 Wh in U3B, 8.1 to 11.7 Wh in the charge loop and 5.5 Wh in the discharge path (`.out` 3c),
all inside the balance that meets M1.

**Not computed here:** the temperature those watts produce. Board A sits in the closed base; the added heat is about 7.6
W at midday, while the sun is up and the base's inside air is warmest. `feasibility/POWER-THERMAL.md`'s inside-air figure
(+10 K with one module, +16 K with three, lid open, fans on) does not include it; that page's owner re-runs it with
board A at 19 W at the charging peak. No part's rating is claimed against a temperature in this record.

## 4. What remains a bench item

U3's and U3B's efficiencies at these points (the 0.98 and 0.975 are plot readings at other conditions: 5 mOhm sense,
4.7 uH, 400 kHz); the IADPT detection at 169 k; the 800 kHz compensation; U3B's input loop holding the node while the
base supplies the load (the allocation loop's reaction time); the LM5069's fault timer at the kit's 18 A peak; the
ideal diode's reverse response on a harness short.
