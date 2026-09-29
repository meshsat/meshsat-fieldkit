mergeable: no

# Independent check of stream s120 (S-120, board A's charge bus against the 30 V charger FETs)

AI review (desk arithmetic on the makers' documents and the committed netlists, done by running and reproducing), not a
qualified engineering review. 29 September 2026, 18:42 CEST. Checker did not write the work.

Checked: branch `fnd/s120`, tip `0004b8a716b0ffc87bfdc437b2db843fdb386152` (confirmed with `git rev-parse`), three commits
on main `e57a7365` (5a868570, 3ca20d5a, 0004b8a7), six files under `v2/docs/records/s120/`. Shared clone
`<scratch>/chk-s120` at the tip; detached shared clone `<scratch>/chk-s120/_int14` at `fnd/int14` `32f26b41` (excluded
locally). The four held TI FET sheets were copied from `int14/v2/vendor/ti/held/` into the clone's ignored
`v2/vendor/ti/held/` (`git check-ignore`: `.gitignore:47`); their sha256 equal `v2/vendor/sources.txt` lines 454 to 457
(f1aad251 SLPS526, c8595fa8 SLPS516, 05fea7ab SLPS524, 99d50d88 SLPS630). No commit, no push, no agent, no box.

The answer (a) stands on what was read: VBUS20's in service ceiling is set by the LM5176's own FB comparator, the figure
23.19 V reproduces, and nothing else drives the bus. The three blocking items are about numbers and labels that the
registry script would write, not about the answer.

## Blocking

**B1. Q7's drain to source voltage is the bus plus Q8's body diode, so its margin is 1.0 V smaller than every table says.**
In buck mode L2's current flows SW1 to SW2; in each dead time after Q7 turns off it freewheels through Q8's body diode, so
CH_SW1 sits at minus VSD and Q7 (drain CH_ACN, source CH_SW1) holds the bus plus VSD (CSD17577Q5A VSD 0.8 typical, 1.0 V
maximum at 18 A, SLPS516 5.1 p.3). The record says so itself for the dump (`vbus20_bound.out` line 56 to 57: 23.14 V), yet
the margin row gives the dump 7.86 V and the bound 6.81 V, and the ringing budget and its allowances take 30 V minus the
bus alone. Reproduced: Q7 margin 8.04 V (DC band), 6.86 V (dump), **5.81 V (bound)**; the 30 V allowance of the first
loop becomes 0.82 nH at A2, 0.92 nH at G1, 1.21 nH at A1 (not 0.92, 1.03, 1.36). Q8's figures (VDS equals SW1) are right.
Where: `vbus20_bound.py` line 321 (one row for "Q7, Q8"), lines 353 to 355 and 369 (budget and allowances);
`vbus20_bound.out` lines 87, 106, 114 to 116, 134, 136; `README.md` lines 17, 77, 100, 107 to 108, 136;
`apply_registry_s120.py` lines 100 to 101 and 104 to 105 (new item: "9.04 V to the FETs' 30 V", "about 0.92 nH"), line 124
with its argument on line 133 (closing evidence: "6.81 V to the FETs' 30 V").
Fix: split the row into Q8 (bus) and Q7 (bus plus VSD 1.0 V, SLPS516 p.3), carry the Q7 figure into the budget and the
allowances, regenerate `.out`, and let the registry texts say 6.81 V for Q8 and 5.81 V for Q7 at the bound.

**B2. The bound's keystone is INFERRED, and that label and its follow up do not reach the registry.** SNVSAI1D 6.5 p.8
gives VOVP as "Measured with respect to VREF", 10 percent in the TYP column only, hysteresis 2.5 percent, and the table's
footnote gives limits only where printed; so 23.06 V and 23.19 V rest on a typical figure. The `.out` labels 23.055 V
INFERRED (line 38) but prints "BOUND, every mechanism" (line 83) and the answer (lines 133 to 134) without it. The
closing evidence says "a typical figure only" but gives 23.06 V and 23.19 V unlabelled and then "That bound holds whatever
the load, the line or the loop does" (`apply_registry_s120.py` lines 117 to 121); the new item says "S-120 bounds the bus
VBUS20 at 23.19 V" (line 96). The one remedy the README names, a bench reading of the trip level (README lines 166 to
167), is carried by no registry item once S-120 closes, and the new item's bench closure does not include it.
Fix: in the closing evidence and the new item write the bound as INFERRED from a typical only threshold with the
sensitivity the record already computes (30 V is reached only at an OVP 42.5 percent over VREF at VREF maximum and the
worst ratio), and add "the front end's OVP trip read on the prototype (FB driven through R6 and R7)" to the new item's
bench closure or to a separate item.

**B3. The new switch node item can close on a model and does not name the bus level its readings are judged at.** Its
closing condition (`apply_registry_s120.py` lines 105 to 109; README lines 112 to 115) accepts "a routed-board reading
of both loops' inductance ... keeps each FET's VDS and U3's SW pins inside their absolute ratings". An inductance reading
reaches a VDS only through section 10's model, which the same text calls "not a bound" (typical driver resistance
1.3 Ohm, SLUSE66A p.16; plateau INFERRED); that is closure by analysis. The measurement branch says "at the charger's
largest current" but not at which bus: a prototype read at its own bus (near 20.0 V) leaves 0.96 V to the DC band top and
3.19 V to the bound unaccounted, which is the whole of the difference between the two budget columns the record prints.
Fix: close on the prototype measurement (a routed-board inductance reading may be recorded as the layout step, not as
closure); state that each measured overshoot over the measured bus is added to 20.96 V for steady service and to 23.19 V
for the OVP excursion (Q7 also carrying VSD, B1), each against 30 V for the FETs and 32 V for SW1 and SW2.

## Minors

m1. Single faults, mechanism (`vbus20_bound.py` lines 384 to 385; README lines 123 to 124): with Q7 and Q8 off they do
not "share the bus through their leakage". L2 carries DC and Q10's body diode (source CH_SW2, drain VBAT) pins SW1 near
VBAT plus VSD, so Q7 holds VBUS20 minus VBAT minus VSD and Q8 about VBAT plus VSD. For the Q2 short the conclusion stands
(U3 passes 32 V at VIN_RAW 32.8 V; Q7 would need VBUS20 at 30 V plus VBAT plus VSD). For the FB faults the closing
evidence's "take U3 past its own 32 V before the FETs" (`apply_registry_s120.py` lines 129 to 131) is not shown: ACOV's
rising threshold is up to 27.7 V with a 100 us deglitch (SLUSE66A p.14), the charger switches until it trips, and Q7 then
holds at least 28.7 V (27.7 V plus VSD) before any ramp in the deglitch or any ringing. Hold the ordering to the Q2 short.

m2. Closing evidence, margins (`apply_registry_s120.py` lines 124 to 126): SW2 is listed among the pins with 8.81 V at
the bound, but SW2 sits on the pack side (VBAT in buck mode, Table 9-3 p.27); its worst in this record is the pack open
event, 24.27 V, 7.73 V under 32 V. The SW1, SW2 and ACN margins lack the "before ringing" the README table carries.
"BTST1 ... sits 2.51 V under 32 V" is the RECOMMENDED 32 V; say so (absolute 38 V: 8.51 V, p.8).

m3. `closed_by` is written as typed: `close 0004b8a7` wrote "commit 0004b8a7" (my run), where every other closed item
carries 40 characters. Resolve with `git rev-parse` before writing (`apply_registry_s120.py` lines 60, 113, 179).

m4. The largest L1 current inside U2's ratings is not the boost peak limit. In buck mode the peak is the valley limit
(94 mV over 4.95 mOhm, 18.99 A, p.7) plus the ripple: with the script's own ripple formula at VOUT 23.06 V it is 24.91 A at
36 V, 28.55 A at 55 V and 29.13 A at 60 V, over the 28.28 A used. The CS and CSG pins also sit behind R150 and R151 (100
Ohm each, C123 1 nF across), where IOFFSET(CS/CSG) of up to 19 uA (p.7) moves the threshold by up to about 1.9 mV. The
bound moves to 23.194 V at 29.13 A and about 23.198 V with the offset: 23.19 V stands at the printed decimals. Say which
mode sets the current (`vbus20_bound.py` lines 220 to 223; README line 52).

m5. TI gives no OVP response time. The record could state why none is needed: at the 28.28 A limit into 1.584 mF the bus
rises at most 17.9 V per ms, so 0.39 ms of full current past the trip would be needed to reach 30 V (README line 51).

m6. The load dump MODEL adds L1's 1.57 mJ at 16.2 A (the 6.45 A draw at 9 V, `gen_sch_a.py` line 751) to a declared
8.0 A step; at 8.0 A L1 carries more. With L1's energy at the peak limit (4.80 mJ) the model reads 22.23 V, still under
the trip (`vbus20_bound.py` lines 250 to 255; README line 53).

m7. The section 10 model covers Q7's turn off only. Q8's VDS (SW1's overshoot) comes at Q7's turn on against Q8's
reverse recovery (Qrr 8.2 nC at 18 A, SLPS516 p.3) with the 6 Ohm turn on driver (RDS_HI_ON_Q1, SLUSE66A p.16), which the
model and the item do not address. U3's VBUS pin (pin 1, directly on VBUS20) is not among the nodes the item reads; U3's
ACN pin reaches CH_ACN through R146 10 Ohm and C121 10 nF to CH_ACP_F, and Figure 10-3's CACP and CACN (33 nF to ground,
p.85) are not drawn on board A (`vbus20_bound.py` lines 353 to 374; `apply_registry_s120.py` lines 102 to 109).

m8. Citations: p.86's "10 nF + 1 nF" sentence refers to Figure 10-3 (p.85), not Figure 10-1 (p.83) (README line 95,
`vbus20_bound.py` line 350, `apply_registry_s120.py` line 100). The pin table p.6 names OTG and FRS only; VAP's pin high
condition is in the IN_VAP register row (p.49), OTG's in 9.3.9 (p.27) and EN_OTG (p.64) (README lines 25 and 41). ACOV,
SYSOVP and BATOVP are all on p.14, not "pp.13 and 14" (README line 25).

m9. Fact gate (`vbus20_bound.py`): the detail strings of "U2 pins", "U3 pins" and "board E clamps" (lines 120 to 122, 143
to 146, 165 to 168) are fixed text, so a FAIL repeats the expected wiring (my mutant with U3 pin 5 moved printed "pin 5
on GND" on its FAIL line). The gate does not check VBUS20's full membership (a new source on the bus without a diode
passes; I read all 39 members: bank, bleeds R202 to R205, R6, R11, R16, R147, R161, R197 to U34, TP12, U2 pins 12 and 24,
U3 pin 1, nothing else drives it) nor the CELL_BATPRESZ divider on which the pack side's SYSOVP 20.0 V rests (R26 13.3k
over R27 40.2k, 75.1 percent of VDDA, inside TI's 4S window 68.4 to 81.5 percent, p.18).

m10. S number: on main the script opens S-123 (as the dry run records), a number the set 13 line already uses for a
different item. README section 10 (lines 145 to 160) should tell the integrator to apply on the line that carries set 13,
where it opens S-124.

m11. `LOG.md` lines 32, 35 and 36 carry backslash escaped backticks that render as literal backticks.

## The seven items, as reproduced

1. VOVP is typical only (p.8, TYP column, no MIN or MAX; 7.3.11 p.18 "turns off the gate drives", 7.1 p.13 "the
   high-side drivers"; either stops VIN_RAW since Q2's body diode blocks it, read on the netlist). 23.06 V is labelled
   INFERRED in the `.out` (not in the registry texts, B2) and is a sensible reading: the 10 percent held at VREF maximum
   (0.812 V, p.6) and the worst divider ratio. Sensitivities reproduce: 13.9, 23.4, 42.5 (42.66 with L1's residue
   recomputed at 30 V) and 52.1 percent over VREF. They use the datasheet's own unit; the datasheet neither bounds nor
   contradicts them (PGOOD's rising window on the same page is the same 10 percent typical).
2. Load dump: L2's energy goes to VBAT, not the bus (GND, Q8 body diode, SW1, L2, SW2, Q10 on or its body diode, VBAT;
   Q7's body diode is reverse biased with SW1 at minus VSD), read on the netlist pins. The dump and line models are
   first order MODELs (valley current mode confirmed, 7.3.1; CCM both directions, 7.3.8 p.17), labelled MODEL and not used
   for the bound; figures 22.137 V and 21.207 V reproduce (m6 on the pairing).
3. The 18 facts hold on the committed netlists of A (`6c40250c47195ebb`) and E (`2ed95a0e8069ebf8`), identical on main
   and on `fnd/int14`: re-read with my own S expression reader (not `netlist_sexp.py`), and pin numbers checked against
   the LM5176 HTSSOP-28, BQ25731 RSN and LM5069 MSOP pin tables. `vbus20_bound.py` reprints the committed `.out` byte for
   byte (exit 0); three mutants of my own (R6 249k, Q7 as CSD18510Q5B, U3 pin 5 off GND) each read FAIL, exit 1.
4. SLUSE66A 8.1 and 8.3 p.8 read: VBUS, ACP, ACN, SRP, SRN, VSYS 32 V absolute; SW1, SW2 minus 2 to 32 V and minus 4 V for
   25 ns; BTST, HIDRV 38 V; BTST to SW 7 V; recommended VBUS, ACP, ACN 26 V, SRN, SRP, VSYS 23.15 V, SW 26 V, BTST 32 V,
   BTST to SW 6.5 V; REGN 6.3 V maximum p.11; ACOV 26.0 / 26.8 / 27.7 V, SYSOVP 4S 19 / 19.5 / 20 V, BATOVP 105 percent
   p.14; charge voltage 0.5 percent p.9. Every margin reproduces except Q7 (B1) and the SW2 and BTST wording (m2).
   FETs: VDS 30 V and EAS 23 and 39 mJ p.1; BVDSS 30 V, Qgs, Qg(th), RG, Coss, VSD p.3, as quoted.
5. The ringing item carries a budget, an owner and remedies, and nothing in the stream claims ringing is bounded
   (README 7 and 12, `.out` 10 and 12, closing evidence all say INCONCLUSIVE or "not bounded at desk"). It lacks Q7's VSD
   (B1), a model free closure and a reference bus level (B3), the OVP reading (B2), and the turn on mechanism (m7).
6. Registry script: on main's registry (`e57a7365`, sha256/16 c88d75284c96a02a) `--check` writes nothing; a scratch copy
   takes one write (S-120 closed, S-123 opened, REQ-015 on S-106, S-107, S-111, S-123, S-111's title extended), the diff
   equals `dryrun.out` section 9 apart from the commit, a second run refuses. On the set 13 line's registry (`32f26b41`,
   S-121 closed, S-122 and S-123 open) a scratch copy opens **S-124**, REQ-015 waits on S-106, S-107, S-111, S-124, S-120 is
   appended after S-121 in closed_items, a second run refuses. `rules_lib.py requirements` reads 144 records, 0 errors,
   0 warnings on all four copies (main's tools for main, `_int14`'s tools for set 13). Refusals reproduced: e57a7365 and
   5a868570 (records not carried), 3ca20d5a (README differs from HEAD's).
7. Claimed as met but resting on less: the bus bound on a typical only threshold (B2); the item's layout branch on a
   model (B3); Q7's margin on the bus alone (B1). The dump, line and D1 figures are labelled MODEL or INFERRED correctly.

## Counts

Blocking 3. Minor 11. Circuit facts 18 of 18 reproduced by an independent reader. Mutants 3 of 3 FAIL. Held sheets 4 of 4
sha256 match. Registry runs 2 lines (S-123 on main, S-124 on set 13), 4 of 4 copies at 0 errors and 0 warnings, 4 refusals
reproduced. Maker pages read 32 (LM5176 10, BQ25731 16, FETs 4, LM5069 1, Littelfuse 1). Every figure of `.out` sections 2
to 11 re-derived; all agree at the printed decimals except the Q7 rows of B1.
