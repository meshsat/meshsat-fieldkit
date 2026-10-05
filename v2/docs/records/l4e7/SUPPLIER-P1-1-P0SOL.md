# Supplier request P1-1, narrowed by P0-7: the solar guard's port-level transient and two bench rows (DRAFT, UNSENT)

Prepared 5 October 2026 by task P0-7 of MESHSAT-1357 (record l4e7, `L4E7-P0SOL.md`, `l4e7_p0sol.out`). UNSENT: no supplier is
engaged, nothing is ordered, and no outside party has been contacted; the owner decides whether, when and to whom this goes.
Prototype design: nothing of board E has been built, bought, powered or measured.

## What changed since P1-1 was written

L4-E9's P1-1 asked a supplier's engineer for the solar input stage's whole guard and current-sense question (D-10's guard-on
case, B6-ENG-1; D-16, B6-ENG-2). P0-7 answers the current-sense half at the desk: the LT8705A's own input sense is no longer
used (CSPIN and CSNIN tied to VIN, its differential 0 V by construction), and the input-current regulation reads the
backstop's sense bank through a second INA169 (U23) into IMON_IN (`apply_gen_sch_e_p0sol.py`, drafted, not applied). What a
supplier is still asked for is narrower: the guard's own port-level transient when a stiff source arrives with the guard
closed, the cold connection's slew margin, and two bench rows that confirm the new arrangement's unprinted terms.

## The claims each item supports, and the provisional choice in force until it is done

| Item | Claim it supports | Affected files and decisions | Bounded provisional choice (scope amendment, point 2) |
|---|---|---|---|
| S1, the guard-on step | D-10 closed for the port (PV_F, Q12's VDS, INP, EN, D4, TRK_VS, U18 and U23) | `apply_gen_sch_e_solar_guard.py` (R-173), R-176 rows 2 and 3, R-180, IF-01 | the port's ratings hold their lines from the source loops the record prints (PV_F's 90 V line from 2.44 uH, the 80 V recommended row from 4.03 uH; on the selected circuit U18 and U23 hold their 1.8 V line at 1.04 uH, 1.16 V, and fail at the envelope's least 0.30 uH, 2.57 V); below them the guard-on event must be removed (route B2, a presence contact on the solar receptacle, Layer 7) or the source's loop bounded by the kit's rules (R-180) |
| S2, the cold connection | D-10's cold-connection margin line | R-176 row 2 | the absolute 60 V/us holds over the whole envelope (at most 56.1 V/us, MODELED); the 54 V/us SESSION line holds from 0.53 uH |
| S3, A7 at zero differential | the regulation's lower band (energy only) | `apply_gen_sch_e_p0sol.py`, IF-02 | the regulation's band is computed with A7 sourcing 0 uA; any current A7 sources only lowers the regulated input current (8705af p.31) |
| S4, the regulation at 25 V | D-16's regulation row (R-189 as rewritten) | IF-02, R-20 | the computed band, nominal 2.538 A, at most 2.921 A, at least 2.184 A with A7 at 0 uA |

## Specimen, quantities and pass limits

**Specimen (S1, S2, S4):** the controlled first prototype of board E's solar stage with the drafted guard (R-173) and P0-7's
draft applied, or a coupon of the same parts and layout from J_SOLAR to U5's input: F2, D11, the port bank C131, C132, C135
and C136, U21 with R87 and Q12, Q13, the bulk C11, C12 and C69, C133 and C134, the sense bank R60 to R64 with U18 and U23,
C71 to C74, C13 to C15, C64, D4 and U5. Three specimens.

**S1, a stiff 36 V source stepping onto the port with the guard on.** A 36 V source able to deliver at least 500 A for 20 us
(a low-ESR capacitor bank charged to 36 V) switched onto J_SOLAR by a low-inductance switch, through three measured loops:
0.30 uH, 1.0 uH and 3.3 uH (each loop measured first at 100 kHz, the switch and the source included). The stage held with the
guard on at 7.5 V, at 17.0 V and at 25 V before the step, idle and at 3.74 A drawn. Five steps per combination per specimen
(3 x 3 x 2 x 5 = 90 steps a specimen). Measured at the pins with Kelvin differential probes: PV_F at U21's VS and CS+; INP;
EN/UVLO; Q12's VDS and current (a Rogowski probe of at least 500 A); TRK_VS; D4's current; the bank's differential at U18's and
U23's pins; U5's CSPIN to CSNIN. **Pass:** PV_F under 80 V (the TPS4811-Q1's recommended operating VS row) and under 90 V
always; INP under 18 V; CS+, CS- and ISCP slew under 54 V/us; Q12's VDS under 90 V and its current inside its derated safe
operating area for the measured time; TRK_VS under 31.8 V and D4 carrying no current; the bank's differential under 1.8 V;
U5's CSPIN to CSNIN under 10 mV in magnitude (0 V by construction; the reading checks the layout).

**S2, the cold connection.** The same rig with the guard off and its CBST discharged; the 36 V source stepped onto J_SOLAR from
0 V and from 25 V through the 0.30 uH loop, five steps per specimen. **Pass:** the slew at CS+, CS- and ISCP under 54 V/us,
INP under 18 V, PV_F under 85 V.

**S3, A7's output at zero differential.** Five LT8705AIUHF#PBF on a test fixture, CSPIN = CSNIN = VIN at 16 V and 25 V,
IMON_IN held at 1.20 V by a source-measure unit, the current out of IMON_IN measured at -20 C, +25 C and +62 C (case).
**Pass:** at most 1.0 uA at every point (the regulation then within 3 % of its computed setting).

**S4, the regulation at REQ-016's 25 V corner.** A PV emulator set to the panel's curve with 25 V open circuit, the stage into
a 12.0 V bus and into a 15.1 V bus, cold-soaked at -20 C and in 62.1 C air. **Pass:** the regulated input current inside 2.18
to 2.92 A at every point, the backstop not tripping, and the IMON_IN voltage under 1.55 V.

## Capability needed

A power-electronics laboratory with: a 36 V pulsed source of at least 500 A and a low-inductance switching fixture; an
oscilloscope of at least 200 MHz with differential probes rated 100 V and a Rogowski current probe of at least 500 A; an
impedance analyser for the loop measurement; a source-measure unit with nanoampere resolution; a thermal chamber from -20 C
to +65 C; a PV emulator of 25 V and 7 A. The report states each instrument, its uncertainty, the specimens' serial numbers and
every waveform.

## Acceptance

Each item is accepted when its pass limits hold on every specimen and repetition, with the measurement uncertainty added on
the unfavourable side. A failure of S1 at a loop the kit's rules admit makes route B2 (or a series element) mandatory for
D-10; a failure of S3 or S4 lowers the regulation's energy claim and changes no protection.

## Cost and schedule

Not known: no supplier has quoted. The quotation request is the owner's to send.
