# L4-E7: qualification of the 100 W bound (layer 4, MESHSAT-1357)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured. The owner's instruction of 1 October
2026: qualify the 96.25 W result precisely. Every figure here is printed by `l4e7_stage_settings.py`, section 9 of
`l4e7_stage_settings.out` (which reproduces `../l4e/l4e_replay.out` and `../l4e5/l4e5_source_control.out` byte for byte
first). The decisions and the corner check are on `L4E7-STAGE-SETTINGS.md`.

## The sheet

The owner names https://www.analog.com/media/en/technical-documentation/data-sheets/8705af.pdf. The live site resets this
runner's connection; the Internet Archive's snapshot **20250322064938** of that exact URL, fetched with the id_ form, has
sha256 **8f552a0b57677bfa7e4a5d5d0fac56d56fbbd1a6f65a9ee7aaaf8743cd534ec3**, byte-identical to the held
`v2/vendor/power/lt8705a.pdf` (`inputs/ia-8705af-20250322064938.json`). The sheet prints its document code **8705af** on
each of its 44 pages and carries no revision table. Only its rows are used.

## The classification

| id | Unprinted value | Bound | Loop stability | Protection | Other |
|---|---|---|---|---|---|
| EA2 | EA2's gain and VC's operating range | **Y** | **Y** | N (only under 4.68 V/V, and then on the safe side: a fault stops switching) | energy, only in hours the limit binds |
| LINE | the IMON_IN reference's line regulation while switching and at temperature | **Y** | N (a static shift, no gain or pole) | N (the fault would need 402 times the printed value) | energy, a fraction of a percent, only when it binds |
| TCR | RSENSE1's TCR below +25 C | **Y** | N (a fraction of a percent of loop gain) | N (the fault and the limit both act on IMON_IN; their ratio does not depend on RSENSE1) | as LINE |
| HOLD | EA3's gain and the FBIN bias | N (they set the envelope's low end, where the corner reads 63.7897 W against 99.6739 W at 25 V) | **Y** (the input-voltage loop) | N (a regulation, not a protection) | **energy (the hold band)** |
| TJ | U5's junction temperature | **Y**, as a condition only: every LT8705A row the corner uses is full range for the I grade, -40 to 125 C junction (p.6 Note 3) | N (inside EA2's row) | **Y** (overtemperature at approximately 165 C, p.34: 59.6 K away) | lifetime (Note 3: derated above 125 C) |

## Guaranteed limits searched, and what stands in where none exists

| id | What the sheet gives | Conservative assumption | Qualification it requires | Margin kept, break-even |
|---|---|---|---|---|
| EA2 | p.5: gain 130 V/V and gm 185 umho, typical only; p.4: the IMON_IN regulation full range at VC = 1.2 V; p.2: VC's absolute maximum -0.3 to 2.2 V; p.7 and p.8 curves plot VC within 0.5 to 2.0 V (**TYPICAL**, TA = 25 C); p.31 names 1.208 V typical and no gain bound. **No guaranteed limit** | EA2 at least 65 V/V, VC anywhere in its absolute range | Analog Devices' statement of EA2's minimum gain, or of the IMON_IN regulation point's guaranteed shift with VC, over -40 to 125 C junction (a production limit). 7b.10 checks the design, it is not that limit | 2.8579 W under it alone; 25.026426 V/V (stack A, cold), 55.191656 V/V (stack C's other terms) |
| LINE | p.4: 0.005 %/V maximum, 25 C, not switching; the regulation row itself is full range at VIN = 12 V (its temperature drift there is guaranteed); p.7 "Feedback Voltages" against temperature is **TYPICAL**. **The VIN dependence while switching and away from 25 C is not printed** | twice the printed maximum, either sign, at every temperature and while switching | Analog Devices' statement of the line regulation while switching over -40 to 125 C junction | 3.6906 W under it alone; 61.6 times the printed maximum (stack A, cold), 47.1 with EA2 at 65 V/V |
| TCR | HoJLR2512 Ho-A0 p.2: +-50 ppm/K; p.4: tested +25 to +125 C only. **No guaranteed limit below +25 C** | +-100 ppm/K below +25 C (twice the printed value) | Milliohm's statement of the TCR from -55 (or -40) to +25 C, or its production characterization. 7b.14 (R59 at -20 and +25 C) checks the design only | 3.5350 W under it alone; 882.027 ppm/K (stack A), 122.295 ppm/K (stack C) |
| HOLD | p.4: EA3 90 V/V and the FBIN bias 10 nA typical; FBIN regulation full range | EA3 at half with the drifts: the hold inside 16.420 to 18.813 V; the bias at ten times moves the lower corner by -9.2 mV | none for the bound; energy sensitivities on the page, 7b.12 reads the hold | does not move the bound |
| TJ | p.2: theta-JA 34 C/W (a package figure on the maker's board); p.6 Notes 3 and 8; p.34 the CLKOUT method (+-10 C), shutdown at approximately 165 C | TJ at most 105.4 C (maximum gate charge at 10 V, highest oscillator frequency, VIN quiescent maximum, EXTVCC at L4-E5's 30.15 V, 62.1 C air) | a design verification of board E's thermal path (7b.13 by p.34's method) | 19.6 K to 125 C |

The clarification requests are drafted for the owner to send; the session contacts no outside party:
`clarification/analog-devices-lt8705a.txt` (EA2's minimum gain and the VC dependence of the IMON_IN regulation point, the
line regulation while switching and over temperature) and `clarification/milliohm-hojlr2512.txt` (the HoJLR TCR below
+25 C).

## The result: CONDITIONAL

**96.2474 W (cold end) and 96.2291 W (hot end) are calculated results, CONDITIONAL on EA2, LINE, TCR and TJ.** Under each
row's conservative assumption alone the cold corner reads 97.1421 W (EA2), 96.3094 W (LINE) and 96.4650 W (TCR); TJ moves no
figure while the junction stays inside -40 to 125 C. All of them together with the resistors' soldering and life drifts read
**99.8992 W: margin 0.1008 W**. The design floor stack C reads 99.6739 / 99.6549 W (cold / hot).

The assumptions of 96.25 W (stack A), in one list:

1. 8705af's full-range rows for the I grade (the IMON_IN regulation 1.187 / 1.229 V, A7's gm 0.94 / 1.06 mmho), with U5's
   junction inside -40 to 125 C (estimated at most 105.4 C).
2. The IMON_IN line regulation at its printed maximum (0.005 %/V, 25 C, not switching), applied while switching and at both
   ends (ASSUMPTION).
3. EA2's gain at its typical 130 V/V as its bound, with VC anywhere in its absolute maximum range (ASSUMPTION).
4. RSENSE1 15 mOhm +-1 % and +-50 ppm/K, the TCR printed for +25 to +125 C applied at -20 C (ASSUMPTION); its hot end 70.1 C
   by the derating line (INFERRED).
5. RIMON_IN 23.2k +-0.1 %, +-25 ppm/K (tested from -55 to +125 C); the resistors' drifts not stacked (they are in C and D).
6. The envelope: the input from the hold's lowest 16.420 V to REQ-016's 25 V, ambient -20 to +40 C (REQ-024), inside air at
   most 62.1 C.
7. Nothing in series with CSPIN or CSNIN (p.30): R59's pads are their Kelvin taps (a layout obligation).
8. Steady state; transients are 7b.9t's.
9. The setting realised as drafted (R59, R16 23.2k, C65).

## Why the corners bound the permitted range

- **The input voltage.** The power's slope in v is I_set [Vref (1 + ls lam (2v - 12)) + es dVC / G] / (Vref_typ gm r1 r2);
  its bracket is at least 1.173206 V (stack A) and 1.159412 V (stack C) at every vertex from 16.420 to 25 V, so the power
  rises with v and 25 V is the worst. No loaded voltage exceeds REQ-016's 25 V open circuit: the panel is PV_P's only source,
  and in discontinuous mode M4 is held off on reverse current (p.18). The dense 0.01 V check of every stack finds its worst
  at 25 V; the hold's lowest is the floor.
- **Every tolerance direction.** The power is monotonic in each term (up in Vref, in the line term above 12 V and in the EA2
  term; down in gm, RSENSE1 and RIMON_IN), so the 64 vertices an end hold the extremes. A resistor's low end 1 - a|T - 25| is
  least at the end of its temperature span farthest from 25 C, so the two ends are enough.
- **Temperature.** The air from -20 C (where self-heating only moves a part toward 25 C) to 62.1 C plus RSENSE1's own rise
  (70.1 C). The LT8705A rows are full range, so U5's junction enters only as the condition. RSENSE1 would have to pass its
  170 C rating (stack A) or reach 139.0 C (stack C) before the corner reaches 100 W, which covers a board hot spot beside L1
  and the FETs.

## States outside the corners

| State | Treatment |
|---|---|
| Below -20 C ambient | Outside REQ-024's -20 to +40 C. Computed for information at -40 C: the candidate's open circuit reaches 25.23 V, outside REQ-016's window; the corner there with both resistors at -40 C reads 97.2744 W (stack A) |
| A source step (a panel plugged in live) | TRK_VIN's 224.8 uF charges through R59 at most at the panel's short circuit, 70.2 mJ at 25 V; start-up ramps VC by the soft start (p.15). Bench 7b.9t |
| An irradiance step | The candidate panel can give up to 110.2 W (100 W +6 % at 1000 W/m2, cells 13.8 C in -20 C air, -0.35 %/K; INFERRED) until the IMON_IN loop settles through CIMON_IN (tau 2.32 ms). Bench 7b.9t |
| The hold transition | VC passes between EA3 and EA2 (the diode-AND, p.14); each side's steady state is bounded. Bench 7b.9t |
| An unstable current loop | Would break the steady-state premise. Bench 7b.9t with p.33's load and line steps |

## The design option that removes an unknown (SESSION decision: not taken)

Of the stocked 15 mOhm 1 % 2512 parts read, only Vishay Dale's WSL2512R0150FEA (LCSC C844695; Document 30100, Revision
23-Nov-2023, p.2) states its TCR from -55 C: +-75 ppm/K (HoJLR, YAGEO PA V.10 p.9 and RALEC LR IE-SP-060 p.10 test only the
hot side). Its solder-heat and life limits each carry 0.5 mOhm (p.3): 3.83 % and 4.33 % of 15 mOhm. With it, stack A reads
96.4763 W, but the design floor reads 106.9760 W at 23.2k, and the same rule would move RIMON_IN to 24.9k (3.2343 A): 6.8 %
less input in every hour the limit binds. **Not taken:** the swap trades an unknown with a large margin (122.295 ppm/K under
stack C, 2.4 times the printed value) for a certain loss of setting. Milliohm's statement qualifies the unknown instead. No
part changes in this round.

## Prototype measurements: downstream obligations, not blockers

No architecture decision depends on 7b.9 (the steady-state sweep), 7b.9t (transients, loop), 7b.10 (EA2's gain), 7b.11
(the line row), 7b.12 (the hold), 7b.13 (U5's junction) or 7b.14 (R59 at -20 and +25 C). The current-limit mechanism holds
its bound under the conservative assumptions above; an adverse reading changes a value (RIMON_IN, the compensation), not the
mechanism or the architecture.
