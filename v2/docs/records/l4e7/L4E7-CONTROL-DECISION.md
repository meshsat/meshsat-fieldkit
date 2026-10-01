# L4-E7R: the control decision for REQ-016's 100 W (layer 4, MESHSAT-1357)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured. The owner's instruction of 1 October
2026: establish whether the proposed control supports REQ-016's retained limit, "at most 100 W into the stage", across the
permitted operating range, and if it does not do so on warranted evidence, choose a defensible approach. Every figure
below is printed by section 10 of `l4e7_stage_settings.out` (the script `l4e7_stage_settings.py`, after its
reproductions of section 0). Evidence classes: **warranted** (a limit the maker prints, with its page), **typical** (a
typical-only row), **inferred** (a reading the session derives), **assumption** (a value the session sets where nothing is
printed), **requirement**. The decision is the session's, taken under the owner's standing rule of 26 September 2026
(`ruled_by: SESSION`): it changes no requirement, spends no money and buys nothing, and after the comparison below one
option is left standing, so no owner judgement is needed.

## The verdict on the present control: NOT SHOWN on warranted limits alone

The LT8705A's input-current limit as set (RIMON_IN 23.2k, RSENSE1 15 mOhm, `L4E7-STAGE-SETTINGS.md`) holds 100 W only
under values no maker warrants. Each is classified in `L4E7-QUALIFICATION.md`; the break-even is how far it may move
before the 25 V corner reaches 100 W:

| Value | What 8705af (or Milliohm) prints | Break-even |
|---|---|---|
| EA2 | voltage gain 130 V/V, typical only (p.5) | 25.026426 V/V (stack A, cold); 55.191656 V/V (stack C's other terms) |
| A7 | gm 0.94 / 1.06 mmho, only at 50 mV differential and CSPIN = 5.025 V (p.5) | 0.904726 mmho (stack A), 0.936935 (stack C), 0.939053 (every conservative assumption together) |
| LINE | 0.005 %/V at 25 C, not switching (p.4) | 61.6 times the printed maximum (stack A); 47.1 with EA2 at 65 V/V |
| TCR | HoJLR2512: +-50 ppm/K tested +25 to +125 C only (Ho-A0 pp.2, 4) | 882.027 ppm/K (stack A), 122.295 ppm/K (stack C) |
| TJ | the I grade's -40 to 125 C (p.3); U5's junction is an INFERRED estimate | 125 C junction, 19.6 K above the estimate |

Under all their conservative assumptions together the corner reads **99.8992 W (margin 0.1008 W)**: CONDITIONAL, not
shown. The margin depends on A7 most: 0.1008 % below its printed minimum gm, applied away from its test point, is
enough to reach 100 W.

## The comparison (three approaches)

Each bound is the highest input power the approach lets through, at the 25 V corner. The energy is SC-37's mean September
day on the pinned SunPower SPR-E-Flex-100 through the replay's `trace()`, at the kept hold's lower, nominal and upper
corners, the regulating limit at its lowest; the hours are the hours the limit binds. "Bright hours" is the input in an
hour the limit binds, against 23.2k.

| | (A) present control, argued margins | (B) hardware 100 W backstop | (C) firmware trim with (B)'s backstop |
|---|---|---|---|
| Bound | 97.8269 W | 99.1059 W | 99.1059 W |
| Bound's evidence | warranted: IMON_IN fault maximum 1.67 V (p.5, full range), the resistors' tolerance and drifts; **assumption**: A7 at its test-point limits away from the test point, the fault threshold's line dependence at twice the reference's, RSENSE1's cold TCR at 100 ppm/K | warranted: TI's INA250 and TPS3701 rows, YAGEO's RT rows, the netlist's dividers; typical: the INA250's typical-only gain rows at twice their typical; inferred: the common-mode referral, REF at ground, the gain rows at VS = 3.23 V, D4's leakage across temperature (term by term below) | as (B): the backstop holds the bound in every firmware state |
| Regulating setting | RIMON_IN 31.6k (C705766), 2.5485 A | RIMON_IN 26.1k (C728586), 3.0856 A | 23.2k (C861244), 3.4713 A, trimmed |
| Wh a day, lower / nominal / upper (h bound) | 344.0 (5) / 336.6 (5) / 307.9 (0) | 368.1 (3) / 350.0 (0) / 307.9 (0) | 369.7 (0) / 350.0 (0) / 307.9 (0) |
| Bright hours | -26.6 % | -11.1 % | +0.0 % |
| Parts and board E | none added; R16 to 31.6k | U18 INA250A2PWR, U19 TPS3701DDCR, R60 28k, R61 7.87k, R62 100k, C66 and C67 100n, C68 1u; SWEN off INTVCC; R16 to 26.1k | (B)'s parts, a monitor on U10's bus and a trim element on RIMON_IN (not selected) |
| New failure mode | a regulation point past the fault minimum turns limiting into fault hiccup (switching stops: energy, not the bound) | a hiccup if the regulation's high corner passes the backstop's low corner (energy, not the bound); a failed U18 or U19 leaves the conditional regulation alone (a single fault the bound does not cover) | a stale or wrong trim, an I2C fault, a reset or boot window, a firmware update: each bounded by (B)'s backstop, none by firmware |
| Depends on a maker's answer | yes: Analog Devices (A7 away from its test point, the fault threshold away from VIN = 12 V) and Milliohm (the cold TCR) | no Analog Devices or Milliohm answer for the bound; Texas Instruments is asked to warrant its inferred readings and typical-only rows; the coordination and the energy stay with Analog Devices' and Milliohm's answers | as (B) |
| Independent of the clarification answers | no | **yes** | yes |

(A) needs no EA2 gain: in any steady state with switching IMON_IN stays under the IMON_IN fault comparator (p.5, full
range), so the regulated point is at most 1.67 V. Taken with the line term at twice the printed reference's, A7 at its
printed limits, RSENSE1's cold TCR at 100 ppm/K and the drifts, the setting must be at least 30540 Ohm, so 31.6k. The bound
still rests on A7 away from its test point, the fault threshold away from VIN = 12 V and the cold TCR, all assumptions, and
the setting costs 26.6 % of every limited hour and 13.4 Wh at the nominal hold on SC-37's day.

(C): REQ-016's verification methods are CALCULATION and PROTOTYPE_MEASUREMENT. A loop that is partly firmware is bounded
by calculation only in the states the firmware is in. A reset, a boot window before the first trim, an I2C fault, a
stale reading and an update are states it is not in, so its bound must rest on hardware beneath it, which is (B)'s
backstop; on a controller fault the trim keeps its last or power-up value while the backstop holds the bound. What (C)
adds is energy in hours the limit binds. On SC-37's day 23.2k binds in no hour at any hold corner, so any trim at or above
it gives the panel's whole output: 369.7 Wh at the lower corner against (B)'s 368.1 Wh, and the same at the nominal and
upper corners. A monitor, a trim element and firmware for 1.6 Wh at one corner of the design day.

## The choice: (B), a hardware 100 W backstop (SESSION)

U18, a TI INA250A2 with its own 2 mOhm shunt (500 mV/A, SBOS511C p.6), carries the stage's whole input from PV_P to a new
net TRK_VS, ahead of RSENSE1. R60 28k over R61 7.87k (YAGEO RT0603, 0.1 %, 25 ppm/K) divide its output into U19, a TI
TPS3701, whose INB rising threshold is 397 / 400 / 403 mV over -40 to 125 C junction (SBVS240C p.5). Past it OUTB pulls
the LT8705A's SWEN (QFN pin 36, today tied to INTVCC) low and switching stops (8705af p.11). The LT8705A's input-current
limit stays, as the regulation, coordinated below the backstop at RIMON_IN 26.1k (3.0856 A nominal).

**Why (B):** it is the only approach whose bound needs no Analog Devices or Milliohm answer at a cost the design day
barely sees, and it keeps the regulation that holds the stage below the bound in normal operation. **EA2's finite gain no
longer enters the bound:** the backstop acts on SWEN, a logic input, not through VC and the error amplifiers; EA2 sets only
where the regulation sits below the backstop. An external amplifier feeding IMON_IN instead would have removed A7 and the
cold TCR but left EA2's typical-only gain inside the bound, which is why the external amplifier drives a comparator here.

**How it acts.** OUTB low holds SWEN at most 250 mV (TPS3701 p.5) against SWEN's rising threshold's least 1.156 V
(8705af p.4, full range). SWEN low puts the LT8705A in its switcher off state; its return passes the initialize state with
SS pulled low, so every restart is a soft start (8705af p.14, Figure 2). INB's hysteresis (2 to 12 mV) releases OUTB once
the current falls; R62 100k and C68 1 uF then hold SWEN under its threshold for about 46 ms (MODELED), so a fault the
regulation does not hold becomes a hiccup at a low duty, never a steady current over the trip.

**Its supply.** U18 and U19 run from TRK_LDO33, 3.23 to 3.35 V in regulation (8705af p.3, full range), regulated whenever
SHDN is high and unaffected by SWEN (p.14). The LT8705A stops switching when LDO33 falls under its undervoltage lockout,
2.96 to 3.12 V (p.3, printed at 25 C; across temperature INFERRED), above U18's least supply 2.7 V (INA250 p.6) and U19's
1.8 V (TPS3701 p.5): whenever the stage can switch, the backstop is powered. U18's output at the highest trip, 1.873 V,
stays under its swing limit, 3.03 V at LDO33's least (p.6). U18 draws at most 300 uA.

## The bound and its margin

**99.1059 W at 25 V** (the backstop's highest trip current 3.9637 A there), **margin 0.8941 W**. Every term sits in it at
the end that raises the trip, summed, not combined statistically:

| Term | Value | Class | Source |
|---|---|---|---|
| INA250A2 system gain error (amplifier and shunt), -40 to 125 C | +-0.75 % | warranted | INA250 SBOS511C p.6 |
| INA250A2 offset at 25 C, and its drift over 45 K at most | +-50 mA; +-11.25 mA | warranted | p.5 |
| common-mode rejection from 12 V to 25 V, 97 dB minimum | +-91.8 mA | warranted (referred to the input through the 2 mOhm shunt, INFERRED) | p.5 |
| supply rejection from 5 V to LDO33's 3.23 V | +-1.77 mA | warranted | p.5; 8705af p.3 |
| TPS3701 INB rising threshold, -40 to 125 C junction | 397 to 403 mV | warranted | TPS3701 SBVS240C p.5 |
| TPS3701 input current through the divider's Thevenin resistance | +-25 nA | warranted | p.5 |
| R60 and R61: 0.1 %, 25 ppm/K over 45 K, and the printed solder-heat and life limits in opposite directions | ratio; +-(0.5 % + 0.05 Ohm) each | warranted (printed test limits) | YAGEO RT V.16 pp.2, 7, 8 |
| the INA250's shunt stress rows (overload, thermal shock, solder heat, high temperature, cold storage) | 0.425 % summed | typical | INA250 p.5 |
| the INA250's nonlinearity, 0.5 to 10 A | 0.03 % | typical | p.6 |
| the INA250's output impedance into the divider (26 kOhm at least) | 1.5 Ohm, 0.0058 % | typical | p.6 |
| the three typical-only gain terms together | 0.461 %, carried at 2 times: 0.922 % | typical (SESSION: twice, this record's floor) | |
| the gain rows at VS = 3.23 V (printed at VS = 5 V) | 0 | inferred | pp.5, 6 |
| REF at ground (the rows are printed at VREF = 2.5 V) | 0 | inferred | p.15, the unidirectional configuration |
| PV_P's two dividers, bypassing U18's shunt: R8 and R9, R14 and R15, at their 1 % | 11.26 mW | warranted (netlist values at their tolerance) | the netlist |
| D4's reverse current, 1 uA at 25 C, carried at 13.1 times for 62 C air | 13.1 uA | inferred | Littelfuse SMCJ p.2, SMCJ28A |
| U18's VIN+ bias, 35 uA at most at 25 C, carried at twice | 70 uA | warranted (printed at 25 C; twice across temperature, SESSION) | INA250 p.5 |
| the input voltage | at most 25 V | requirement | REQ-016 |

**The margin, justified against each uncertainty (SESSION).** Every warranted term is inside the bound at its limit, so
none needs margin beyond it. The terms no maker bounds, the INA250's three typical-only gain rows, are carried at twice
their typical (the floor this record gives every typical-only row), and the margin is sized to them: the divider is the
stocked pair with the highest lowest trip whose bound would still hold with them at four times their typical (99.9998 W).
They may grow to 4.00 times their typical before 100 W. With them at their typical the bound reads 98.6651 W, without
them 98.2284 W. The inferred terms are zero or small by the maker's own configuration (REF, VS) or carried at a multiple
(D4, VIN+ bias); the common-mode referral is the one inferred reading of size (91.8 mA), and Texas Instruments is
asked to confirm it.

**The trip against the day.** The lowest trip at 25 V is 3.4239 A (new parts) and 3.3524 A (with the divider's printed
limits and the typical-only terms at their floor); at the hold's voltages it stays at or above 3.4003 A, against the
panel's highest current on SC-37's day, 2.8779 A at the lower hold corner: **the backstop never acts that day**.

## The coordination and the energy

**The coordination (SESSION):** the largest stocked RIMON_IN whose stack A highest current (3.4221 A at 25 V) stays at or
under the backstop's lowest trip with new parts at every input voltage: **26.1k** (YAGEO RT0603BRD0726K1L, LCSC C728586).
Against the backstop's lowest with its drifts (3.3524 A) the regulation may meet it after ageing: a hiccup in bright hours
(energy), never on SC-37's day; bench row 7b.17 reads it.

**The energy cost:** 11.1 % less input in every hour the limit binds, against 23.2k. On SC-37's day: 368.1 Wh at the lower
hold corner (3 h bound), 350.0 Wh at the nominal hold (0 h) and 307.9 Wh at the upper (0 h), against 369.7 / 350.0 /
307.9 Wh with 23.2k: **1.6 Wh at the lower corner, nothing at the nominal and upper**. The INA250's shunt and package path
add about 0.27 Wh a day of conduction at the nominal hold (INFERRED: its 4.5 mOhm package path is typical).

## Board E changes (drafted, nothing applied)

`apply_gen_sch_e_backstop.py`, six edits on the text `apply_gen_sch_e_input_limit.py` leaves (it refuses a generator
without R59, refuses a second application, and refuses the tree's generator until `RELEASE.md` names an accepted check):

- U18 INA250A2PWR (C2859736), TSSOP-16: IN+ (14 to 16) on PV_P, IN- (1 to 3) on the new net TRK_VS, SH+ to VIN+ (TRK_ISP)
  and SH- to VIN- (TRK_ISN) unfiltered (p.3), REF and GND on GND (p.15), VS on TRK_LDO33 with C66 100n;
- R59 (RSENSE1) and U5's CSPIN (pin 33) move from PV_P to TRK_VS; CSNIN (pin 32) and VIN (pin 34) stay on TRK_VIN, so U18
  carries everything into the converter, all but PV_P's own dividers, D4 and TP5 (in the bound above);
- R60 28k (C705756) over R61 7.87k (C861565) from U18's OUT to U19's INB;
- U19 TPS3701DDCR (C132788): INA tied to TRK_LDO33 (OUTA released, left open), VDD on TRK_LDO33 with C67 100n, OUTB on the
  new net TRK_SWEN;
- U5's SWEN (pin 36) from TRK_INTVCC to TRK_SWEN, with R62 100k (C25803) from TRK_LDO33 and C68 1 uF to GND;
- R16 from 23.2k to 26.1k (C728586);
- the declarations: PV_P's load is U18; TRK_VS a series segment of PV_P from U18 to R59 (U18 named with its reason, a
  15 A shunt path, p.5); TRK_ISP and TRK_ISN as nodes at the panel's 25 V; the tracker section's list; the TSSOP16 key.

Owed beside it: U18's placement in the panel current path and R59's Kelvin taps (board E's layout constraints), the
regeneration and its gates. The record reads the draft back on top of the input limit draft (section 6 and section 10).

## New failure modes, and the exposure U18 shares

- A hiccup (SWEN low, then a soft start) if the regulation's high corner passes the backstop's low corner: energy, not the
  bound.
- A failed U18 or U19 (open, stuck) leaves the conditional regulation alone: a single fault the bound does not cover; it
  goes to layer 8's fault analysis.
- An LDO33 sag stops the stage before the backstop loses its supply (above).
- U18's inputs share U5's exposure on the panel entry: its common-mode absolute maximum is 40 V and GND - 0.3 V (SBOS511C
  p.4), against U5's -0.3 to 80 V for VIN and the sense pins (8705af p.2). A reversed panel puts PV_P at D4's forward drop
  (DECISION-31 note E-N1), as it already does for U5; 40 V is above the 35 V of the bulk capacitors that set PV_P's lowest
  limit under TRN-001 (REQ-016's acceptance), so U18 does not lower it.

## What would overturn the choice

- Analog Devices warranting EA2's gain and A7 away from its test point, and Milliohm the cold TCR: the present limit would
  then hold the bound itself and the backstop could go.
- The INA250A2's supply: LCSC stock 359 on 1 October 2026; U18 is one per board.
- TRN-001 finding U18's 40 V common-mode absolute maximum unworkable on the panel entry (the SMCJ28A clamps at up to
  45.4 V at its full pulse, as for the 35 V bulk capacitors).
- A bench nuisance trip under the coordinated setting (7b.17).

## What remains conditional

The bound rests on the makers' printed limits (TI's INA250 and TPS3701, YAGEO's RT, 8705af's SWEN and LDO33 rows,
Littelfuse's SMCJ28A row), the INA250's typical-only gain rows carried at twice their typical with the margin sized to
four times, and inferred readings (the common-mode rejection referred through the 2 mOhm shunt, REF at ground, the gain
rows at VS = 3.23 V, D4's leakage across temperature); none of them is an Analog Devices or Milliohm answer. The bound
covers U18 and U19 working. The regulation's own corner (96.25 W at 23.2k) stays CONDITIONAL on EA2, A7, LINE, TCR and TJ;
those now set the coordination (whether the regulation or the backstop holds the stage in the bright hours) and the
energy, not the bound. The transient (the INA250's 50 kHz bandwidth and TPS3701's 9.9 us delay are typical) is 7b.9t's.

## The clarification drafts (adjusted)

Analog Devices' and Milliohm's answers now decide the coordination and the energy, not the bound.
`clarification/analog-devices-lt8705a.txt` gains item 5: SWEN's delay and restart, and LDO33's undervoltage lockout
across temperature, which the backstop's supply reads as INFERRED. A third draft,
`clarification/texas-instruments-ina250.txt`, asks Texas Instruments for the INA250's rows at VS = 3.3 V and VREF = 0 V,
the common-mode referral, a warranted limit for its shunt's stress rows, and whether the nonlinearity and output impedance
sit inside the system gain error. `clarification/milliohm-hojlr2512.txt` is unchanged. The session contacts no one; the
texts are for the owner to send.

## Prototype measurements (REQ-016's second method; downstream obligations, not blockers)

- **7b.15** on each built board, the input current at which SWEN falls, at 17.6 V and 25 V, against the band 3.3524 to
  3.9637 A at 25 V;
- **7b.16** with R16 shorted (IMON_IN held at 0 V, so neither the regulation nor its fault comparator acts), the input
  power stays at or under 100 W averaged over the hiccup, and the restart passes the soft start;
- **7b.17** the regulation at 26.1k on a bench panel curve does not trip the backstop at 25 C and at the cold end.

The predicates are held by `v2/ecad/tools/tests/test_l4e7.py`: the chosen bound rests only on the classes it states and
names no value the clarification answers decide; the comparison holds at most three approaches, each with a bound, an
energy row per hold corner, parts, a failure mode and its dependence; at least one approach is independent of the
answers; the backstop never acts on SC-37's day and the regulation sits under it; the backstop's draft applies only after
the input limit draft.
