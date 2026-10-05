# EFUSE-SETTINGS: every eFuse and current-limit setting against its exact part's sheet (task T12, MESHSAT-1357)

**Status: round 2 (5 October 2026, P0 Slot C, branch `fnd/p0t10` from `fnd/p0base` `e132db0e`) after the independent check V6
(item D: CONFIRMED AS CONDITIONAL; minors m3 to m6), on round 1 (branch `fnd/efuse` from main `aa32332c`). Round 2 is not
reviewed.** Round 2 in one paragraph: the composition is the P0 candidate's full one and board B regenerates whole (V6-m3; R36 750 R
on U23 pin 7 and R43 1.21 k on U24 pin 7 read on it, 301 R and 909 R fail); board A's U23 is a defect by EF-F01's rule, EF-F03, with
its draft (V6-m6); the downstream ratings are read at the inside air as well, two rows PROVISIONAL with the supplier's task (V6-m4);
the RockBLOCK's charge pads are a build condition drafted for ASSEMBLY.md (V6-m5). Prototype
design: nothing in this kit has been built, bought, powered or measured, and no figure here is a measurement. Every figure is
printed by `efuse_check.py` into `efuse_check.out` ("out N" is its section); this page restates them, and the test
`v2/ecad/tools/tests/test_efuse.py` holds the page to the output. Labels: PRINTED is a limit the maker prints; TYPICAL a
maker's typical; INFERRED a step this record takes between printed figures; ASSUMPTION an input no document gives; CITED a
figure of another record, not re-derived here.

## The defects (the brief's table first)

| Id | Kind | Instance (tree) | What fails | Correction | State |
|---|---|---|---|---|---|
| EF-F01 | DESIGN DEFECT (SDR3-F04 confirmed) | board B U23, TPS259631DDAR, +5V_DEV to +5V_LIME (the LimeSDR Mini 2.4), DRAWN and DRAFTED | (a) R36 301 Ohm is outside the recommended 453 to 7869 Ohm and its 3.011 A outside the 0.125 to 2 A range, so (b) is UNDEFINED (the sheet prints no limit there) and (c) fails on the extrapolated 3.011 A against J_LIME's 1.8 A; (d) the label "3.0 A" states a limit the sheet does not print | `apply_gen_sch_b_u23ilm.py`: R36 750 Ohm 1 % (the code board A's U21 carries): 1.0718 / 1.2152 / 1.3631 A against the demand 0.9534 A and the receptacle's 1.8 A | OPEN; correction DRAFTED, composed, netlist read with mutations; electrical acceptance holds on C-DEV rev 1 on printed figures (below); not reviewed |
| EF-F02 | DESIGN DEFECT (new, the same setting) | board B U24, TPS259631DDAR, +5V_DEV to +5V_RB (the RockBLOCK 9704), DRAWN and DRAFTED | the same (a), (b), (d); (c) fails on the extrapolated 3.011 A against the one 5 V conductor's 1 A (IDC socket and flat cable) | `apply_gen_sch_b_u24ilm.py`: R43 1.21 kOhm 1 %: 0.6681 / 0.7575 / 0.8496 A against the maker's 500 mA and the conductor's 1 A | OPEN; as EF-F01 |
| EF-F03 | DESIGN DEFECT (round 2, V6-m6: round 1's EF-O03 judged by EF-F01's rule) | board A U23, TPS259631DDAR, +5V_D8IN to +5V_D8 (board D), DRAWN and DRAFTED | (a) R98 453 Ohm is the recommended minimum itself; its corners (1 %, 100 ppm/K over -20 to +85 C) reach 445.8 Ohm, outside 453 to 7869 Ohm, and the band's top 2.1816 A is over the switch's 2 A continuous rating | `apply_gen_sch_a_u23ilm.py`: R98 511 Ohm 1 %: 1.5684 / 1.7783 / 1.9949 A against board D's 0.6858 A, the switch's 2 A and the JST VH's 10 A | OPEN; correction DRAFTED after board A's 20 pending drafts, netlist read with three mutations that fail; (a) to (c) hold on printed figures; not reviewed |
| DR-03 | DESIGN DEFECT (known, record l4e4) | board A U18, TPS25740A, the USB-C outlet's OCP through R138, DRAWN | (b) R138 10 mOhm trips at 1.8953 to 2.2897 A, under every 3 A PDO | record l4e4's `apply_gen_sch_a_r138.py` (5 mOhm, L4-E9 R-05): 3.7906 to 4.5794 A in the DRAFTED tree | OPEN on main; its draft DRAFTED (l4e4's) |

No other instance fails (a), (b) or (c) in either tree (out 6, out 7: "unregistered defects: 0").

## What was checked (out 2, out 3)

The generators' own part tables, each generator run through record l8p's `gen_netlist.py` (no KiCad), on main (DRAWN) and with
its board's pending drafts composed in L4-E9's change-list order (DRAFTED); every `apply_gen_sch_*.py` under the records parsed
for a current-limiting part (out 2b). The setting component is found by its pins (the ILM pin's resistor to ground, the sense
resistor across a controller's VIN and SENSE pins), and its value, tolerance and label read from its own value text.

**Round 2 (V6-m3): the full composition.** Board B's order is now the P0 candidate's: gnd002, fans12, fandec, panel5v, ph4, rt500,
gndret, gndrtn (record l8r2), iocbuck, iocpre and T10 round 5's canshdn (record l9t5); board A's gains record l8p's thguard after
L4-E11's dd7, record l9t5's iocbuck and iocpre and record l8r2's gndrtn (20 drafts). Board B's chain regenerates whole (round 1 ran
it without fans12, EF-O02, which l8r2's rounds 7 and 8 answered), so the fans' three eFuses are read from the generator's own table,
no longer from the draft's text, and the EFUSE netlist reads R36 750 Ohm on U23 pin 7 and R43 1.21 kOhm on U24 pin 7 on the FULL
composition (out 8; R36 at 301 Ohm and R43 at 909 Ohm fail). Board C and board D have no pending draft that names a current-limiting
part.

| Tree | Board, ref | Part (code) | Path | Setting | Band min / nom / max | Basis | Verdict |
|---|---|---|---|---|---|---|---|
| DRAWN | A U18 | TPS25740ARGER (C544309) | PD_SW to PD_VBUS | R138 10 mOhm | 1.8953 / - / 2.2897 A | PRINTED VI(TRIP), the 3 A row (l4e4's reading) | DEFECT (b): DR-03 |
| DRAWN | A U21 | TPS259631DDAR (C2155778) | VBAT to VMON (the monitor) | R90 750 Ohm | 1.0718 / 1.2152 / 1.3631 A | PRINTED range-wide +-10.4 % | PASS |
| DRAWN | A U22 | TPS259631DDAR | VBAT to VHEAT_IN (the heater buck) | R94 909 Ohm | 0.9342 / 1.0046 / 1.0678 A | PRINTED row (909 Ohm) | PASS |
| DRAWN | A U23 | TPS259631DDAR | +5V_D8IN to +5V_D8 (board D) | R98 453 Ohm | 1.8015 / 2.0046 / 2.1816 A | PRINTED row (453 Ohm) | DEFECT (a): EF-F03 (round 1 read PASS, EDGE) |
| DRAWN | A U32 | TPS259631DDAR | +5V_DEV to VBUS_WALL (USB 2.0 host port) | R186 1 kOhm | 0.8063 / 0.9142 / 1.0254 A | PRINTED range-wide | PASS |
| DRAWN | A U39 | TPS259631DDAR | +3V3 to +3V3_EMCON_EF | R209 4.7 kOhm | 0.1795 / 0.2033 / 0.2279 A | PRINTED range-wide | PASS |
| DRAWN | B U5 | TPS23861PWR (C93245) | the PoE port 1 | R12 0.25 Ohm | 0.6152 / 0.6580 / 0.7021 A (ICUT, Class 4) | PRINTED ICUT 0b110 | PASS (EF-O05) |
| DRAWN | B U21, U22 | TPS22810DRV (C527679) | +5V_LORA, +3V3_ZB | none | no limit | the part has none | n/a (EF-O01) |
| DRAWN | B U23 | TPS259631DDAR | +5V_DEV to +5V_LIME | R36 301 Ohm | none printed (3.0112 A extrapolated) | NONE | DEFECT: EF-F01 |
| DRAWN | B U24 | TPS259631DDAR | +5V_DEV to +5V_RB | R43 301 Ohm | none printed (3.0112 A extrapolated) | NONE | DEFECT: EF-F02 |
| DRAWN | B U28 | TPS2065CDBV (C353882) | +5V_DEV to +5V_CAM | fixed | 1.2000 / 1.5500 / 1.9000 A | PRINTED IOS | PASS |
| DRAWN | D U21 | TPS22810DRV | +5V_D8 to +5V_TX | none | no limit | the part has none | n/a (EF-O01) |
| DRAWN | E U6 | LM5069MM-2 (C111822) | the vehicle and shore entry | R19 10 mOhm | 4.7876 / 5.5000 / 6.2308 A | PRINTED VCL / RS | PASS |
| DRAWN | E U16 | TPS22810DRV | +5V_E6 to +5V_GEIGER | none | no limit | the part has none | n/a (EF-O01) |
| DRAFTED | A U18 | TPS25740ARGER | as DRAWN | R138 5 mOhm (l4e4) | 3.7906 / - / 4.5794 A | PRINTED VI(TRIP) | PASS |
| DRAFTED | A U42 | TPS16630PWPR (no code) | VBAT to VSYS_DOCK (L4-E11) | R228 11 kOhm 0.1 % | 1.4625 / 1.6364 / 1.8127 A | INFERRED +-10.0 % (the bracketing rows) | PASS |
| DRAFTED | A U44 | TPS259631DDAR | +3V3 to +3V3_A2D (l8r2) | R234 3.83 kOhm | 0.2206 / 0.2470 / 0.2732 A | PRINTED row (3.83 kOhm) | PASS |
| DRAFTED | A U45 | TPS48110AQDGXRQ1 | VBUS20's over-voltage cut-off (l8r2) | IWRN to GND | no current limit used | the sheet's pin table | n/a |
| DRAFTED | B U702, U732, U762 | TPS259631DDAR | the coolers' 12 V leads (l8r2's fans12; read from the generator's table since round 2) | R706, R736, R766 1.87 kOhm | 0.4359 / 0.4941 / 0.5541 A | PRINTED range-wide | PASS (EF-L05) |
| DRAFTED | B U901 | TPS259631DDAR | +5V_DEV to PANEL_5V_EF (l8r2) | R901 604 Ohm | 1.3284 / 1.5062 / 1.6896 A | PRINTED range-wide | PASS (EF-L05) |
| DRAFTED | E U6 | TPS48110AQDGXRQ1 (C17556513) | the entry (L4-E11) | R19 4.5 mOhm, RSET 100 Ohm, RIWRN 39.7 kOhm | 6.4054 / 6.8000 / 7.0920 A | PRINTED V(SNS_WRN) at the printed point; the short-circuit trip 10.38 to 13.84 A INFERRED (RISCP R81 3.01 kOhm, Equation 11; the draft says 10.36 to 13.87 A), not judged | PASS |
| DRAFTED | E U21 | TPS48110AQDGXRQ1 | the panel cut-off (L4-E7) | R87 4.5 mOhm | 6.4054 / 6.8000 / 7.0920 A | PRINTED V(SNS_WRN) | PASS (EF-O06) |
| DRAFTED | P U101 | LM5069MM-1 (no code) | the pack breaker (l8p) | R101 4 mOhm parallel R102 7.5 mOhm | 18.3525 / 21.0833 / 23.8848 A | PRINTED VCL / RS | PASS |
| EFUSE | B U23 | TPS259631DDAR | +5V_DEV to +5V_LIME | R36 750 Ohm | 1.0718 / 1.2152 / 1.3631 A | PRINTED range-wide | PASS |
| EFUSE | B U24 | TPS259631DDAR | +5V_DEV to +5V_RB | R43 1.21 kOhm | 0.6681 / 0.7575 / 0.8496 A | PRINTED range-wide | PASS |
| EFUSE | A U23 | TPS259631DDAR | +5V_D8IN to +5V_D8 | R98 511 Ohm | 1.5684 / 1.7783 / 1.9949 A | PRINTED range-wide | PASS (round 2) |

## The sheets (out 0, out 1)

Each figure is written once, as the sentence or row the maker prints, its numbers parsed from it and the quote found in the
sheet's own text layer: 56 quotes, every one VERIFIED on this host. TI's current download of each of the eight TI sheets
(plain GET of `www.ti.com/lit/ds/symlink/<part>.pdf`, 5 October 2026) is byte for byte the held copy: TPS2596 SLVSET8A (the
TPS259631 is its adjustable-OVLO, auto-retry variant, the device comparison table p.3), TPS2065C SLVSAU6I, TPS22810 SLVSDH0C,
LM5069 SNVS452G, TPS23861 SLUSBX9I, TPS25740A SLVSDG8B, TPS1663 SLVSET9G and TPS4811-Q1 SLUSEE5E (the last two held back
under `v2/vendor/ti/held/`, fetched by `v2/docs/records/l4e11/fetch_held_back.py`, pinned by sha256).

**The TPS2596's band, and why it is wider than the drafts' interpolations.** Equation 5 (p.21; Equation 7's worked example p.28
fixes the sign the text layer loses): ILIM = 903 / RILM + 0.0112 A. At a printed row (453, 909, 3830 and 7870 Ohm, p.6) the
row's minimum and maximum are used, scaled to the resistor's corners (the scaling INFERRED). Between rows the band is the
equation at the resistor's corners times the Features' "+-10.4 % (maximum) across current range" (p.1), which Figure 21 draws
"Across Process, Voltage and Temperature Corners": a printed bound for any setting in the range, at the input voltages these
boards use (5.1 V and 3.3 V, outside the electrical table's 12 V test condition). The bracketing rows' worst deviation (8.7 to
9.3 %) is printed beside it as INFERRED and is not used to judge. The 7.87 kOhm row is printed for TA at most 80 C only; U39's
4.7 kOhm lies between it and the 3.83 kOhm row, and U39's load is 2 mA against a 0.18 A foot, so nothing turns on it.

**The variant (brief item 2):** no TPS2596-family part has a fixed limit or a range above 2 A (the TPS25962x and TPS25963x
differ in their over-voltage response and the x0 and x1 in latch-off or auto-retry). The sibling TPS2595xx (held,
`v2/vendor/power/ti-tps2595-efuse.pdf`, Rev. C) prints 0.5 to 4 A with RILM 487 to 5000 Ohm and would be the part for a limit near
3 A; the loads here need at most 0.9534 A, so the TPS259631 stays and only its resistor changes (out 8).

**The resistor's corners:** the value text's tolerance (1 % unless written), its TCR from Layer 6's catalogue reading of the
code where one is read (+-100 ppm/K for the UNI-ROYAL codes), else +-100 ppm/K (ASSUMPTION A-TCR), the sense resistors
+-50 ppm/K (record l4e4's reading of the HoJLR2512 sheet) or their value text, over -20 to +85 C (ASSUMPTION A-T).

## The loads, by case and state (out 5)

Each eFuse's load is taken from record l9pwr's committed budget (section 5, every state, the HIGH column, which puts every load at
its maximum at once) or from the maker's printed maximum, the larger, and converted to current at the case's least voltage:
C-DEV rev 1's 4.9019 V for the device rail, behind the eFuse's own 0.131 Ohm (PRINTED, VIN above 4 V, TJ to 125 C), at constant
power (the upper reading). The LimeSDR Mini 2.4: "Maximum Power 4.5 W" and the host's "5V, 900 mA" (PRINTED), behind U23 and
J_LIME's two contacts at their printed 30 mOhm maximum each, 0.9534 A; the
RockBLOCK 9704's DC input "at a maximum of 500mA" (PRINTED); the monitor 10 W at VBAT's 9.688 V floor (l9pwr, S); board D 3.30 W
(PS-ALLTX); the panel 5.00 W (D); the camera 2.50 W (T, a placeholder). Board E's entry: L4-E9 IF-07's figures (CITED): 4.629 A
on the drawn LM5069's line, 5.983 A with the corrected knee for L4-E11's TPS48110; board P's breaker: C-PROT rev 1's "18 A for
60 s never interrupted" (the case's band 18.32 to 23.93 A takes the resistors at the band's own temperature, record l9stk).

**Start-up** (out 6, "(b, start)"): the output's fastest rise is IDVDT 2.33 uA times GDVDT 21.5 over the 10 nF dVdt capacitor
at -10 % (ASSUMPTION A-C), 5.57 V/ms; the band's minimum less the load's draw during the rise leaves an allowance for the
load's own input capacitance. EFUSE U23: 143.6 uF beside C58's 22 uF with the LimeSDR drawing 150 mA unconfigured, against an
assumed 10 uF (ASSUMPTION: a device inside the USB standard's limits; the standard is not held): PASS. EFUSE U24: 8.2 uF with the RockBLOCK drawing
its full 500 mA during the rise: a CONDITION, because the module's input capacitance is not printed; above it the start passes
through the eFuse's current limit, the sheet's dVdt-limited start (Figures 48 and 49), which this record does not count as a
failure.

## The corrections' evidence (out 8)

- **Composition:** each draft applies on main's generator alone, after board B's pending drafts in L4-E9's order, and in either
  order with the other (the same text); a second run is refused; the repository's own generator is refused for writing until a
  `RELEASE.md` here names an accepted check (none exists).
- **Netlist:** the EFUSE generator (board B's runnable chain, then both drafts) run through `gen_netlist.py`; the check parses the
  netlist and finds U23 pin 7 on a net with R36 alone, R36's other pin on GND, and its value's band 1.0718 to 1.3631 A inside 0.9534
  to 1.8 A; U24 pin 7 with R43 alone, 0.6681 to 0.8496 A inside 0.5 to 1.0 A.
- **Mutations that fail:** the DRAFTED netlists without the corrections; R36 back to 301 Ohm; R43 at 909 Ohm (the band's top over
  1 A); R43 at 1.87 kOhm (the band's foot under 500 mA); R36's ground pin moved onto +5V_LIME. Every one reads as required.
- **Electrical acceptance on C-DEV rev 1, on printed figures:** EF-F01 (b) 1.0718 A at or above 0.9534 A, margin +0.118 A; (c)
  1.3631 A at or below the receptacle's 1.8 A and the switch's 2 A. EF-F02 (b) 0.6681 A at or above 0.5 A, margin +0.168 A; (c)
  0.8496 A at or below 1 A. Physical conditions stay open: no part is bought or measured, the even sharing is not an issue here
  (one conductor each), and the RockBLOCK's start is a CONDITION (above).

## Round 2: the downstream ratings at the inside air (V6-m4, out 5b) and the RockBLOCK's charge pads (V6-m5)

Section 6's (c) judges each eFuse's band top against the printed ratings, which the makers state without an ambient. Record l8r2
reads the same parts at the inside air on the same candidate, so round 2 carries both readings. The method is l8r2's least-rating
reading (each sheet's range includes its own rise and prints no rise at current and no derating curve, so the rise at the printed
rating is taken as the whole span from 25 C to the range's top, the most severe reading the sheet allows; heating as the current
squared): MODEL on PRINTED figures, the rating's own 25 C an ASSUMPTION. Air: L4-E12 E5's mixed 76.25 C (81.89 C in the exhaust).

| eFuse | Downstream part | Printed, range | At 76.25 C (81.89 C) | Its load's own demand | The band's top | Largest air for the demand / the top |
|---|---|---|---|---|---|---|
| B U23 (LimeSDR) | J_LIME, Wurth 692122030100 VBUS contact | 1.800 A, -20 to +85 C including the rise | 0.6874 A (0.4098 A) | 0.9534 A: NOT COVERED | 1.3631 A: NOT COVERED | 68.2 C / 50.6 C |
| B U24 (RockBLOCK) | J_RB9704's IDC socket contact, Wurth 61201623021 | 1.000 A, -40 to +105 C | 0.5995 A (0.5375 A) | 0.5000 A: covered | 0.8496 A: NOT COVERED | 85.0 C / 47.3 C |
| B U24 (RockBLOCK) | the 16-way flat cable conductor, Wurth 63911615521CAB | 1.000 A at 25 C, -25 to +105 C, "may decrease due to the derating effect" | 0.5995 A (0.5375 A) | 0.5000 A: covered | 0.8496 A: NOT COVERED | 85.0 C / 47.3 C |

What it means, under the owner's amendment of 5 October 2026 (part 19):
- **The fact not established at the desk:** each maker's rise at current (no derating curve is printed). It supports EF-F01's and
  EF-F02's (c) at the inside air. The (c) of section 6 (printed ratings) stands; at the inside air both rows are **PROVISIONAL**.
- **Bounded provisional choice:** keep the parts drawn; EF-F01 and EF-F02 stay as drafted (no eFuse setting answers U23's row,
  because the LimeSDR's own demand is above the receptacle's full-span reading; for U24 no TPS2596 setting can put its top under
  0.5995 A while its foot stays at 0.500 A, the band's top-to-foot ratio being 1.272).
- **The supplier's validation task:** specimen, the J_LIME receptacle on board B's land (three pieces) and the RockBLOCK harness as
  built (the 2x8 IDC socket on the 16-way cable, three pieces); quantity, each contact's temperature with the current through VBUS
  and its return at the eFuse's band top (1.3631 A for J_LIME, 0.8496 A for the harness) in a 76 C chamber, held to steady state;
  pass limit, at or under the part's range top (85 C for the receptacle, 105 C for the socket and cable).
- **Redesign task if the measurement fails:** a USB receptacle whose printed rating holds at the inside air (a range to +105 C or a
  printed derating curve), or J_LIME placed where the local air is bounded at or under 50.6 C (the band's top) or 68.2 C (the demand);
  for the harness, a conductor with a printed rating at the inside air.

**The RockBLOCK's charge-current pads (V6-m5):** Ground Control prints the supercapacitors' default DC input charge current as about
0.460 A and "can be increased to ~800mA" with two pads bridged (L_RB_CHG, L_RB_CHG_UP). U24's foot 0.6681 A holds the default and not
the bridged figure, so the pads stay OPEN as a build condition: drafted for `ASSEMBLY.md`'s RockBLOCK row in
`apply_assembly_rb_pads.py` (unapplied; on a scratch copy it applies once and refuses a second run, out 8).

## Labelling findings and observations (out 7)

| Id | Owner | Finding |
|---|---|---|
| EF-L01 | board B's generator owner | +5V_LIME declares 1.2 A typical and 3.0 A peak and `_DEV_LOADS` gives U23 1.2 A, with no source; the maker prints 4.5 W at most and a 5 V, 900 mA host supply. The declared figures are left as drawn (conservative for the copper); the owner sources or restates them |
| EF-L02 | board B's generator owner | +5V_RB declares a 2.00 A peak against the maker's 500 mA and the one conductor's 1 A; after EF-F02 the eFuse passes at most 0.8496 A |
| EF-L03 | Layer 6 (part identities) | Layer 6's board B table keys R36 and R43 on "301R 1% (ILM: 3.0 A)" (C25192); after the corrections R36 is 750 Ohm (C23241 by `lcsc_fill.py`'s map, the code Layer 6 read for board A's R90) and R43 1.21 kOhm, for which no code is read |
| EF-L04 | Layer 6 (part identities) | the pending drafts place U42 TPS16630PWPR (L4-E11) and U101 LM5069MM-1 (l8p) with no LCSC code |
| EF-L05 | record l8r2's owner | fans12's text says 0.448 to 0.538 A and panel5v's 1.375 to 1.614 A, interpolated between the printed rows (INFERRED); the printed bound across the range gives 0.4359 to 0.5541 A and 1.3284 to 1.6896 A, and (b) and (c) still hold |
| EF-O01 | generator owners, Layers 8 and 9 | the TPS22810 switches (B U21, U22; D U21; E U16) limit no current (thermal protection only); a fault behind one is limited by the stage feeding it, and no record may count it as a current limit |
| EF-O02 | record l8r2's owner | RESOLVED IN ROUND 2: with l8r2's rounds 7 and 8 composed, board B's chain regenerates whole (round 1: it stopped after `apply_gen_sch_b_fans12.py` at the GND rail, 21.51 A against 21.00 A) |
| EF-O03 | board A's generator owner | SUPERSEDED IN ROUND 2 by EF-F03 (V6-m6): the observation that U23's R98 453 Ohm reaches 445.8 Ohm at its corners is now judged by EF-F01's rule, a defect, with its draft |
| EF-O04 | board A's generator owner, Layer 9 | U21's foot 1.0718 A clears the monitor's 10 W at VBAT's 9.688 V floor (1.0470 A) by 0.025 A; the monitor's start current and input capacitance are not printed |
| EF-O05 | board B's generator owner | the PoE port's ICUT foot 0.6152 A clears the declared 0.60 A by 0.015 A with R12 at 250 mOhm; at TI's 255 mOhm it would be 0.6031 A |
| EF-O06 | record l4e7's owner | R87's text says "its breaker at 6.36 to 7.14 A, over the panel's 6.8 A"; the printed band 6.4054 to 7.0920 A straddles 6.8 A; the text is right only if the cut-off may trip on the panel's 6.8 A |

**For Layer 6 (part identities), in one place:** EF-L03 and EF-L04; the drafts' parts are the tree's own (the TPS259631DDAR
C2155778 on every eFuse; R36's 750 Ohm is C23241, already read by Layer 6).

## Decisions this record takes (authority: SESSION, under the owner's standing rule of 26 September 2026)

1. **R36 = 750 Ohm for EF-F01.** Why: the maker's printed demand (4.5 W, 900 mA) governs, the band 1.0718 to 1.3631 A sits between
   it and the receptacle's 1.8 A with margin on both sides, and the value and code are the tree's own (board A's R90, C23241), so
   no new part identity is needed. The generator's unsourced 1.2 A typical is not a requirement (EF-L01). Reverse: any E96 value
   from 576 to 825 Ohm holds (b) and (c) (out 8); should the owner source the 1.2 A, 649 Ohm (1.2370 to 1.5733 A) clears it.
2. **R43 = 1.21 kOhm for EF-F02.** Why: the only constraint pair is the module's printed 500 mA and the conductor's 1 A; 909 Ohm
   and 1 kOhm put the top over 1 A and 1.87 kOhm the foot under 500 mA (out 8's mutations); 1.21 kOhm leaves +0.168 A and
   -0.150 A. Reverse: any E96 value from 1.05 to 1.62 kOhm holds both (out 8); 1.21 kOhm sits nearest the middle.
3. **The declared rail figures (+5V_LIME, +5V_RB) are not changed in the drafts.** Why: they are conservative for the copper and
   the owner's to source; the drafts change one component's value and the notes that name it.
4. **The band between printed rows is the range-wide printed +-10.4 %, not an interpolation.** Why: the printed bound is the
   maker's for any setting in the range; an interpolation is an inference (EF-L05).
5. **Board B's DRAFTED netlist is run without fans12** (EF-O02), its eFuses read from its text. Why: the generator does not run with
   it on this tree, and its lines are not the ones this record changes. SUPERSEDED in round 2: the full chain runs.
6. **R98 = 511 Ohm for EF-F03 (round 2).** Why: the least E96 value whose corners stay inside 453 to 7869 Ohm, so it keeps the most of
   the band board D had; 1.5684 to 1.9949 A clears board D's 0.6858 A and stays under the switch's 2 A. Reverse: any E96 value from
   511 to 576 Ohm and above holds (out 8 lists them); the declared +5V_D8 peak of 2.0 A is the generator owner's.
7. **The inside-air rows are carried beside (c), not in it (round 2).** Why: (c) is the setting's check on the makers' printed
   ratings; the inside-air reading is a vendor condition no eFuse setting answers (U23's demand itself exceeds it), so folding it into
   (c) would turn a receptacle question into an eFuse verdict. Reverse: judge (c) at the inside air (out 5b gives the figures).
8. **The composition is the P0 candidate's full one (round 2, V6-m3)**, in the order record l9t5's `l9t5_drafts.py` and the check V6
   composed it, with T10 round 5's canshdn on board B. Why: a setting is read on the design that would be released. Reverse: ORDER in
   `efuse_check.py`.

## Not done, and why

- Round 1 had one independent check (V6, item D, CONFIRMED AS CONDITIONAL); round 2 has none (the next step: the targeted recheck
  of EF-F03, the inside-air rows and the composition).
- The converters' own current limits (the LM5176 stages, the AP64500 and TPS62933 bucks, the TPS61089 step-ups, the LT8705A's
  input limit, the LTC3115), the charger's input limit (record l4e4), the gauge's protections and the polyfuses are not power
  switches and are outside T12's list; the device rail's capacity is C-DEV's (T5).
- (c) is NOT RATED HERE where no record rates the conductor (A U22, A U39, B U5, E U6 drawn, A U42, E U21); none of these is a
  defect: the brief's (c) needs a rating to judge against.
- The USB standards are not held; the 150 mA unconfigured draw, the 10 uF device capacitance and the 500 mA USB 2.0 port are
  labelled ASSUMPTION or D.
- No KiCad on this host: the netlists are `gen_netlist.py`'s (the generator's own part table), not the box's export, which stays
  the reading of record.
