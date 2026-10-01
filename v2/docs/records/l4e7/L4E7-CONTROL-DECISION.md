# L4-E7R: the control decision for REQ-016's 100 W (layer 4, MESHSAT-1357)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured. The owner's instruction of 1 October
2026: establish whether the proposed control supports REQ-016's retained limit, "at most 100 W into the stage", across the
permitted operating range, and if it does not do so on warranted evidence, choose a defensible approach. This is the
second round, after the check `checks/astra-check-l4e7r-1.md` (NOT YET, B1 to B6 and minors; the last section maps each to
its change). Every figure below is printed by section 10 of `l4e7_stage_settings.out` (the script `l4e7_stage_settings.py`,
after its reproductions of section 0); the sheet values quoted in the verdict's table are section 9's. Evidence classes:
**warranted** (a limit the maker prints for the condition it is used at, with its page; "printed test limits" for a
passive's drift rows; "the pin's absolute maximum" where only the rating bounds a term), **typical**, **inferred**,
**assumption**, **requirement**, **MODELED**. The decision is the session's, taken under the owner's standing rule of
26 September 2026 (`ruled_by: SESSION`): it changes no requirement, spends no money and buys nothing.

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

Under all their conservative assumptions together the corner reads **99.8992 W (margin 0.1008 W)**: CONDITIONAL.

## The comparison (three approaches)

Each bound is the highest static input power the approach lets through, at 25 V. The energy is the stage's input on
SC-37's mean September day on the pinned SunPower SPR-E-Flex-100 through the replay's `trace()`, at the kept hold's lower,
nominal and upper corners, and on the check's own bright day (a twelve-hour sine to 1000 W/m2, 18.1 C air, the nominal
hold; this model reproduces the check's 495.3165 Wh at 26.1k and 465.6367 Wh at 28.7k), the regulation at its lowest;
hours the limit binds in brackets. "Noon" is the reduction against 23.2k at bright noon: the regulating current's, then
the input power's (the panel's voltage rises as its current falls, so the power falls less than the current).

| | (A) present control, argued margins | (B) INA250A2 sensor, the trip chain of C | (C) WSL bank, INA169, TPS3701, TPS3808 |
|---|---|---|---|
| Bound | 97.8269 W | 98.2217 W (every row at its printed value) | **98.1890 W** |
| Status | CONDITIONAL | CONDITIONAL | **UNCONDITIONAL** (static bound) |
| Evidence | warranted: IMON_IN fault maximum 1.67 V, RSENSE1 1 %, RIMON_IN 0.1 %, the drifts; **assumption**: A7 away from its test point, the fault threshold's line dependence at twice the reference's, RSENSE1's cold TCR at 100 ppm/K, the fault's timing | warranted: the TPS3701, TPS3808 and RT rows, the offset's supply and common-mode rows at 0 A; **conditional**: the gain error and offset at VS = 3.3 V and VREF = 0 V (printed at 5 V and 2.5 V), the CMR away from 0 A, the shunt's stress rows (typical, 0.425 %), the nonlinearity and output impedance (typical), the VIN+ bias across temperature (25 C row) | warranted, every term at its operating condition (below); requirement: 25 V |
| Regulating setting | 31.6k (C705766), 2.5485 A | 28k (C705756), 2.8762 A | 29.4k (C861288), 2.7392 A |
| SC-37 Wh, lower / nominal / upper (h) | 344.0 (5) / 336.6 (5) / 307.9 (0) | 361.2 (4) / 349.8 (2) / 307.9 (0) | 355.0 (5) / 345.5 (3) / 307.9 (0) |
| Bright day Wh (h) | 431.9 (9) | 473.2 (7) | 457.4 (9) |
| Noon, current / power | -26.6 / -24.6 % | -17.1 / -15.6 % | -21.1 / -19.4 % |
| Parts and board E | none added; R16 to 31.6k | U18 INA250A2PWR, the trip chain of C, R60 28k, R61 7.87k; R16 to 28k | five WSL2512R0700FEA, INA169NA/3K, TPS3701DDCR, TPS3808G33DBVR, eight RT resistors, three 100n, the 50 V bulk; R16 to 29.4k |
| New failure mode | limiting past the fault minimum becomes the fault's hiccup (energy) | as C | a hiccup if the regulation's unprinted values exceed the joint assumptions (energy); the single faults below |
| Depends on a maker's answer | Analog Devices (A7, the fault threshold, its timing), Milliohm (the cold TCR) | Texas Instruments (the rows at its own supply and reference, the stress rows); the coordination on Analog Devices and Milliohm | **none for the bound**; the coordination and the energy on Analog Devices and Milliohm |
| The derived disturbance (below) | no part added; the bulk needs C's correction | **fails**: U18's inputs are rated 40 V, the clamp reaches 45.4 V | passes |

With 23.2k the day reads 369.7 / 350.0 / 307.9 Wh and the bright day 534.7 Wh (594.4 Wh with no limit at all).

(B)'s unprinted gain terms together may add 1.371 % before 100 W with an event (they print 0.459 % typical, not a limit);
the conduction of its 4.5 mOhm package path, the shunt included, is 0.1855 Wh on SC-37's day and 0.5166 Wh on the bright
day.

## The choice: (C), UNCONDITIONAL in its static bound (SESSION)

**The arrangement.** R60 to R64, five Vishay Dale WSL2512R0700FEA (C2076144) in parallel, 14 mOhm, carry everything
entering the stage but R8, R9 and U18's VIN+ pin, from PV_P to a new net TRK_VS ahead of RSENSE1. U18, a TI INA169, turns
their voltage into a current into R65 16.9k and R66 8.06k, together its 25 kOhm test load (SBOS181F p.6). U19, a TPS3701,
trips at INB on R66 and watches TRK_VS at INA (R67 110k over R68 9.53k); either output pulls the MR of U20, a TPS3808G33,
whose RESET holds the LT8705A's SWEN low through R70 22k over R71 33k. The LT8705A's own limit stays, as the regulation,
coordinated under the trip at RIMON_IN 29.4k (2.7392 A nominal).

**Why (C).** It is the one arrangement whose bound rests on printed limits at its own operating condition. (A) rests on
assumptions; (B) on rows printed at another supply, reference or current and on typical-only rows, and its sensor's 40 V
inputs fail the derived disturbance. The INA169 prints its transconductance, offset and nonlinearity over -40 to 85 C,
and its common-mode and supply rejection at VSENSE = 50 mV over VIN+ and V+ from 2.7 to 60 V: the board's 9 to 25 V at the
trip's 49.6 mV. The two rejection rows are carried at the larger of their offset reading and their gain reading, so no row
is extended past its condition. An external amplifier feeding IMON_IN would have left EA2's typical-only gain inside the
bound; the trip acts on SWEN, a logic input, so EA2's finite gain sets only where the regulation sits.

**The static bound: 98.1890 W at 25 V** (the highest trip current 3.9173 A, the trip's sense voltage 52.537 mV at most),
**margin 1.8110 W**. Every term sits at the end that raises the trip, summed; no common multiplier, no typical row, no term
assigned zero:

| Term | Value | Class | Source |
|---|---|---|---|
| U19 TPS3701 INB rising threshold, TJ -40 to 125 C, VDD 1.8 to 36 V | 397 to 403 mV | warranted | TPS3701 SBVS240C p.5 |
| U19 input current at INB, through R66 | +-25 nA | warranted | p.5 |
| U18 INA169 transconductance, VSENSE 10 to 150 mV, TA -40 to 85 C | 990 to 1010 uA/V | warranted | INA169 SBOS181F p.6 |
| its nonlinearity; its offset, referred to the input | +-0.1 %; +-1 mV | warranted | p.6 |
| its common-mode rejection, VIN+ 12 to 25 V, at VSENSE = 50 mV | 100 dB minimum: 130 uV | warranted | p.6, VIN+ 2.7 to 60 V |
| its supply rejection, V+ 5 to 25 V, at VSENSE = 50 mV | 10 uV/V: 200 uV | warranted | p.6, V+ 2.7 to 60 V |
| the two rejections at the larger of their offset and gain readings | x 1.0507 | warranted (the rows, read both ways) | p.6 |
| R66 8.06k: 0.1 %, 25 ppm/K over 45 K, solder heat and life | +-(0.5 % + 0.05 Ohm) each | warranted (printed test limits) | YAGEO RT V.16 pp.2, 7, 8 |
| the bank, 5 x WSL2512R0700FEA: 1 %, 75 ppm/K from -55 to +155 C | 14.0000 mOhm | warranted | Vishay WSL 30100 pp.1, 2 |
| the bank's solder-heat and load-life test limits | +-(0.5 % + 0.0005 Ohm), +-(1.0 % + 0.0005 Ohm) per part | warranted (printed test limits) | WSL 30100 p.3 |
| R8 and R9 (the hold draft's RT parts) across 25 V, bypassing the bank | 5.78 mW | warranted | YAGEO RT V.16 |
| U18's VIN+ pin current, bypassing the bank (its bias prints no maximum) | at most 10 mA: 250 mW | warranted (the pin's absolute maximum) | INA169 p.4 |
| the input voltage | at most 25 V | requirement | REQ-016 |

The margin covers the dynamic term below; the static terms are each at their limit and need none.

**The trip against the day.** Its lowest at the hold's voltages is 3.2119 A with the parts aged (3.2026 A at 25 V; 3.3311 A
new), against the panel's highest current on SC-37's day at any hold corner, 2.8779 A: the trip never acts that day. One
bank part carries at most 0.043 W (its P70 is 1 W).

## The dynamics and the averaging basis (B2)

**Basis (SESSION):** REQ-016's "at most 100 W into the stage" is judged as the mean input power over any 0.1 s. The limit
sizes the stage's power parts, F2, J_SOLAR and the pack's charge, whose thermal and charge time constants are seconds and
longer; a sub-millisecond event of tens of mJ is TRN-001's and the inrush's matter.

**The sequence.** Sense (U18, about 4.5 us typical), trip (U19's INB rising edge, 28.1 us typical: the input edge, SBVS240C
p.6, at 10 mV overdrive and a 100 kOhm load), MR to RESET (0.15 us typical), the last switching edge after SWEN falls (one
period, INFERRED): 38.4 us together. After the trip the input current decays to the charge of the entry's capacitors, at
most 146.1 uF to 25 V, 45.7 mJ; U20 then holds SWEN low at least 180 ms (CT to VDD through R69, SBVS050N p.7, full range),
so any 0.1 s holds one event at most, and every restart passes the initialize state with SS pulled low (8705af p.14 and
Figure 2, p.15). No capacitor sits on SWEN or on U20's output: the off-time is U20's own and needs no discharge.

**The bound with the event:** 98.1890 W + (45.7 mJ + 156.25 W x 38.4 us) / 0.1 s = **98.7054 W**. It holds for a response
up to **0.867 ms** (22 times the typical sum); bench row 7b.16 reads it. A slower response would overturn the 0.1 s basis,
not the arrangement: a longer basis or a lower trip restores it. A plug-in or a source step is the same event: the
capacitors' charge is bounded by their 45.7 mJ and the panel's current by REQ-016's 6.25 A.

## The supply sequencing (B3)

The stage is held off whenever the sensing chain is unsupplied, on printed rows and no Analog Devices answer:

- U20 asserts RESET whenever TRK_LDO33 is under its threshold, 3.024 to 3.116 V, and releases it only above 3.194 V (VIT
  3.07 V, 1.5 %, its 2.5 % hysteresis; SBVS050N pp.3, 6), under LDO33's least in regulation, 3.23 V (8705af p.3, full range),
  then holds it a further 180 ms at least, past U19's 150 us start (SBVS240C p.6, typical).
- Where RESET is released, U19 (from 1.8 V) and U20 (from 1.7 V) are inside their ranges, and U19's INA holds MR low
  whenever TRK_VS is under 4.960 V (U18 works from 2.7 V), releasing it by 5.200 V at most.
- R70 over R71 keep SWEN under its least threshold (1.156 V, 8705af p.4) until TRK_LDO33 reaches 1.923 V, above both
  parts' least supply; with RESET released at LDO33's least SWEN reads 1.935 V, over its highest threshold 1.256 V; RESET
  sinks at most 0.152 mA (its VOL row 0.4 V at 1 mA).
- Below 1.3 V on TRK_LDO33 the VOL rows end: SWEN could rise only if its pin sourced 28.4 uA (8705af p.12 describes a logic
  input; no current row: INFERRED), and TRK_LDO33 under 1.3 V with INTVCC above its 4.45 V lockout is an LDO33 failure, a
  single fault (below). The power-up reset (VPOR 0.8 V) holds for a rise no faster than 66667 V/s; LDO33's 22 mA limit into
  C20's 1 uF gives 22000 V/s (INFERRED: C20's capacitance at bias has no row); bench row 7b.19.

## The coordination and the energy (B4)

**One basis at both corners (SESSION):** the smallest stocked RIMON_IN whose regulation at its highest under the joint
assumptions (EA2 and EA3 at half gain, the line at twice, RSENSE1's cold TCR at 100 ppm/K, the drifts, each resistor at its
worst end) stays at or under C's lowest trip with its parts aged, at every input voltage: **29.4k**, 3.1533 A at 25 V
against 3.2026 A. If the regulation's unprinted values were worse than those assumptions the overlap would be a hiccup:
each trip stops the stage 180 to 420 ms and restarts it through the soft start. The bright day's hours whose panel current
at the nominal hold exceeds C's lowest trip are 09 to 15, 462.4 Wh: the energy such an overlap would put at risk.

**The energy cost:** on SC-37's day 355.0 / 345.5 / 307.9 Wh at the lower, nominal and upper corners (5 / 3 / 0 h bound)
against 369.7 / 350.0 / 307.9 Wh with 23.2k: **4.5 Wh at the nominal hold, 14.7 Wh at the lower corner**; on the bright day
457.4 Wh against 534.7 Wh, **77.3 Wh**; at bright noon the input power falls 19.4 % (the current 21.1 %). The bank's
conduction costs 0.5773 Wh on SC-37's day and 1.6072 Wh on the bright day; R59 stays.

## The solar entry's protection (B6)

**The derived disturbance (SESSION).** No surge level is ruled (DECISION-31 section 3, D-04, D-16) and the tree holds no
surge standard. TRN-001 asks the clamp to clamp below every protected part's absolute maximum, and D4's maker prints its
clamping only at its rated pulse. So the design disturbance is that pulse: **10/1000 us (Littelfuse SMCJ p.1), 33.1 A at
D4, clamped at 45.4 V at most (p.2)**; any source of impedance Z gives it with an open-circuit 45.4 V + 33.1 A x Z. **The
assumption:** no surge on the panel lead inside the kit's use exceeds D4's rating. A larger ruled level would need a larger
clamp and parts rated above its clamping voltage: that changes ratings, not the arrangement (U18's inputs are rated 75 V,
U5's 80 V).

**The correction (drafted):** D4 and the bulk move behind the sense bank onto TRK_VS, and the bulk becomes three Panasonic
EEHZA1H330XP, 50 V, 33 uF (ZA p.2; the same 6.3 x 7.7 mm land; 1600 mA ripple, 40 mOhm); the 35 V parts were under the
clamp. Every part on the entry against it:

- TRK_VS and TRK_VIN at 45.4 V at most: the bulk 50 V; C13 to C15 50 V by the generator's value text (their maker parts are
  the regeneration's); C64 and C66 50 V (C14663); U5's VIN and sense pins 80 V; Q3 60 V; U18's V+ and VIN- 75 V; R67 75 V
  (RT); R14 39.5 V across it (the generator's 100k 1 %: its maker part is the regeneration's); SHDN 5.92 V and FBIN 3.14 V
  against their 30 V; PV_P 45.88 V at most (the bank's drop added): U18's VIN+ and R8 75 V (RT).
- U18's differential: the whole pulse crosses the bank, 0.483 V at most against its 2 V. U5's sense differential: R59
  carries only the ceramics' share, 0.165 V with the bulk new at 20 C and 0.268 V after endurance at -40 C (MODELED: the ZA's
  ESR 40 mOhm new and 0.8 Ohm after endurance at -40 C, p.1, three in parallel, its capacitance at its least, the ceramics at
  their largest, the clamp left out), against 0.3 V (8705af p.2); bench row 7b.18.
- Electrostatic discharge (decision 34): its 2.25 uC moves the entry by 0.029 V at most and puts 0.665 V across the bank. A
  reversed panel conducts through D4 as DECISION-31's note E-N1 records, now with U18's inputs near -1 V as well (its sheet
  allows a pin past its rating while the pin's current stays under 10 mA, p.4: INFERRED for its gain resistor's path),
  board E's owner's note.

The input capacitance falls from 200 uF of bulk to 99 uF: its ripple and its damping with the panel lead are owed to the
regeneration.

## The series disconnect: evaluated, not taken (SESSION)

The LM5069 class hot-swap controller prints its current limit (VCL 48.5 / 55 / 61.5 mV) at VIN = 48 V, not at the panel's
17 to 25 V, and its spread (12 % from typical to either end) would push the regulation further down than C's. SWEN already
removes the path from the panel to the pack (the four switches stop and M1's body diode blocks the input), and the input
capacitors' charge is bounded as an event. A series FET would cover a shorted switch of the LT8705A, a single fault layer 8
judges.

## The single faults (assigned to layer 8)

- **Defeat the backstop:** U18's output stuck low or open, or R65 open; R66 shorted; U19's OUTB stuck open; U20's RESET stuck
  open or its MR stuck high; a short across the sense bank; U5's SWEN input failed active.
- **Stop charging:** U19's OUTA or OUTB stuck low; U20's RESET stuck low; R70 open; U18's output stuck high; the whole bank
  open (one part open only raises the bank's resistance: the trip falls, charging continues); TRK_LDO33 lost.
- **Acceptance (for layer 8):** each fault listed with its effect; no single fault both defeats the backstop and removes the
  LT8705A's own limit; every fault that defeats the backstop is found by the commissioning and periodic trip test (7b.15) at
  an interval layer 8 sets.

## Board E changes (drafted, nothing applied)

`apply_gen_sch_e_backstop.py`, nine edits on the text the hold and input limit drafts leave (it refuses a generator without
them, refuses a second application, and refuses the tree's generator until `RELEASE.md` names an accepted check):

- R60 to R64 (C2076144) from PV_P to TRK_VS; R59 and U5's CSPIN (pin 33) behind them on TRK_VS; CSNIN and VIN stay on TRK_VIN;
- U18 INA169NA/3K (C44322) with C66; R65 16.9k (C861156) and R66 8.06k (C861587); R67 110k (C326736) and R68 9.53k (C705800);
- U19 TPS3701DDCR (C132788) with C67; U20 TPS3808G33DBVR (C43698) with C68 and R69 100k (C122538);
- U5's SWEN (pin 36) from TRK_INTVCC to TRK_SWEN, with R70 22k (C469656) and R71 33k (C705768);
- C11 and C12 to EEHZA1H330XP (C178637) and C69 a third, on TRK_VS; D4 to TRK_VS; R14 to TRK_VS;
- R16 from 23.2k to 29.4k (C861288);
- the declarations: PV_P's loads are the bank, TRK_VS a series segment of PV_P from the bank to R59, the tracker section.

Owed beside it: the bank's Kelvin taps to U18 and R59's to U5 (board E's layout constraints), the regeneration and its
gates, the input capacitance's ripple and damping check, and the requirement records that name "the 35 V bulk capacitors"
and "the 225 uF on PV_P" (their owners restate them).

## What would overturn the choice

- a measured response over 0.867 ms (the averaging basis, not the arrangement);
- a stock change of the bank part (LCSC 1970 on 1 October 2026; five per board), of U18 (61878) or U20 (36047);
- a ruled surge level above D4's rating (the clamp and the ratings, not the arrangement);
- Analog Devices warranting EA2, A7 and the line row, and Milliohm the cold TCR (the regulation would then hold the bound
  itself and C would be redundant protection);
- layer 8 finding a single fault that both defeats the backstop and removes the regulation.

## What remains conditional

Nothing in C's static bound. The dynamic bound rests on the response's typical rows (bench row 7b.16, tolerance 0.867 ms
against 38.4 us typical) and the 0.1 s basis (SESSION); the supply sequencing below 1.3 V on TRK_LDO33 only through a fault
(SWEN's pin current INFERRED); the surge protection on the stated design disturbance; the coordination and the energy on
Analog Devices' and Milliohm's answers (EA2, A7, LINE, TCR, TJ), whose failure costs energy, not the bound.

## The clarification drafts (adjusted)

No answer moves C's bound. Analog Devices' and Milliohm's answers set the coordination and the energy. Analog Devices'
item 5 now asks SWEN's input current and its delay to the last switching edge (the sequencing's one inference and bench
row 7b.16). `clarification/texas-instruments-ina169.txt` asks the INA169's VIN+ pin current, carried meanwhile at its
absolute maximum (supporting). The INA250 draft is withdrawn with approach B; `clarification/milliohm-hojlr2512.txt` is
unchanged. The session contacts no one; the texts are for the owner to send.

## Prototype measurements (REQ-016's second method; downstream obligations, not blockers)

- **7b.15** on each built board, the input current at which SWEN falls, at 17.6 V and 25 V, against 3.2026 to 3.9173 A at
  25 V, at commissioning and at layer 8's interval;
- **7b.16** the response from a current step over the trip to the last switching edge, against 0.867 ms; and with R16
  shorted (IMON_IN at 0 V, so neither the regulation nor its fault acts) the mean input over 0.1 s at or under 100 W, each
  restart through the soft start;
- **7b.17** the regulation at 29.4k on a bench panel curve does not trip at 25 C and at the cold end;
- **7b.18** R59's differential under a 10/1000 us pulse at D4's rating, against 0.3 V;
- **7b.19** TRK_LDO33's rise at power-up, against 66667 V/s.

## The check, and what changed

| Item of `checks/astra-check-l4e7r-1.md` | Change |
|---|---|
| B1, the margin | No common multiplier: each term is a printed limit at its own condition (the table above); a term with no printed limit is CONDITIONAL and named ((B)'s list), never multiplied; U18's VIN+ current is carried at its absolute maximum, classed as such |
| B5, the comparison | (C) replaces the old (C), a scenario: a sense bank read by an INA169 whose rows cover the operating condition, a TPS3701 and a TPS3808; its bound rests on printed limits only; chosen on that evidence |
| B3, supply sequencing | A TPS3808 supervisor on TRK_LDO33 holds the stage off whenever the sensing chain is unsupplied, on its printed rows; the LDO33 lockout row of 8705af is no longer used |
| B2, dynamics | The rising INB edge (28.1 us typical); no capacitor on SWEN or on an output (U20's own 180 ms off-time, warranted); the sequence, the capacitors' 45.7 mJ and the 0.1 s basis bounded; bench row 7b.16 with its 0.867 ms tolerance |
| B4, coordination | One basis at both corners (C's lowest with its parts aged against the regulation's highest under the joint assumptions): 29.4k; the bright-day exposure stated |
| B6, the surge | The disturbance derived from TRN-001 and D4's rating; D4 and a 50 V bulk behind the bank; every part on the entry against 45.4 V; R59's share MODELED |
| Minors | The INA250's 4.5 mOhm is the package total: 0.1855 Wh; the noon reductions printed as current and power (A 24.6 %, B at 26.1k 10.06 %); "the smallest stocked RIMON_IN"; the single faults assigned to layer 8 with an acceptance |
