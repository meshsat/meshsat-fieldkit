# Supplier request P1-1, narrowed by P0-7: the remaining engineering item E-1 (D-10) and four qualification rows (DRAFT, UNSENT)

Prepared 5 October 2026 by task P0-7 of MESHSAT-1357 (record l4e7, `L4E7-P0SOL.md`, `l4e7_p0sol.out`). UNSENT: no supplier is
engaged, nothing is ordered, and no outside party has been contacted; the owner decides whether, when and to whom this goes.
Prototype design: nothing of board E has been built, bought, powered or measured.

**Set 30 note (6 October 2026; record text only, on branch `fnd/w4l4e7` from set 30's integration commit 2c `53a68c7c`; adopted in
the NEXT set, where the coordinator regenerates; the promoted sha `__INTEGRATED__`).** What moved since this draft was written: the
candidate merged set 31 (`6fe398e9`; `v2/docs/records/l4e9/SET31-CHANGES.md`), whose register row R-240 keeps D-16's correction
PROVISIONAL ("A7's zero-differential output PROVISIONAL (the supplier's S3)", `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:336`) and
whose page reads D-16 "PROVISIONAL in A7's zero-differential output (S3) and in the regulation at 25 V (S4)"
(`v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:841`); and the remaining-engineering ledger's HO-F
(`v2/docs/records/l4close/REMAINING-ENGINEERING.md` on `fnd/ledgerfix` `99bbc0c6`, cited as text only; its section 6, item E) places
the lower-source back-feed as REMAINING ENGINEERING inside E-1 with S1's row (b) its later validation, on the owner's part 23
(`v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:680`). This draft now says the same: D-16's correction is ADDRESSED IN DRAFTS and
PROVISIONAL, not completed (E-1 (d)); the back-feed is an open case inside E-1 (E-1 (a)), S1's row (b) its later validation; E-1 is
named apart from record l9stk's E-1; S1's row (a), the source in parallel with a connected panel, is read as the later validation of
E-1's guard-on step (SESSION: it is that step, cases F1 to F3; reversed by the coordinator's revision). No figure, limit, specimen
or quantity is changed, and nothing here is sent.

## What changed since P1-1 was written

L4-E9's P1-1 asked a supplier's engineer for the solar input stage's whole guard and current-sense question (D-10's guard-on
case, B6-ENG-1; D-16, B6-ENG-2). P0-7 answers the current-sense half at the desk: the LT8705A's own input sense is no longer
used (CSPIN and CSNIN tied to VIN, its differential 0 V by construction), and the input-current regulation reads the
backstop's sense bank through a second INA169 (U23) into IMON_IN (`apply_gen_sch_e_p0sol.py`, drafted, not applied). What a
supplier is still asked for is narrower, and its first item is engineering, not test: **D-10 is an unresolved protection
defect in the present model** (E-1 below: the guard's own port-level transient when a stiff source steps onto the port with the
guard closed, and one open case not yet computed, the lower-source back-feed), which needs a correction or a justified model
revision before any passing claim; then the qualification of that correction (S1), the cold connection's margin lines (S2), and
two bench rows that confirm the new sense arrangement's unprinted terms (S3, S4).

## REMAINING ENGINEERING E-1 (D-10): the solar guard's port-level protection defect

Owner's review of checkpoint 4 (part 23), 5 October 2026: D-10 is an UNRESOLVED PROTECTION DEFECT in the present model, not a case
that merely lacks evidence. This item is the receiving company's remaining engineering; no measurement listed below closes it by
itself, and route B2 (`B2-PRESENCE.md`, UNSELECTED and WITHDRAWN AS DRAFTED) does not resolve it. E-1 is record l4e7's E-1 (the
register's R-240: "item l4e7's E-1", `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:336`), not record l9stk's E-1, the battery FETs'
junction limit that R-159 carries ("l9stk's E-1", `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:255`): one identifier, two items, named
apart here without renaming either (set 30 note).

**(a) The failing cases, the parts and the claims each hits** (MODELED, record l4e7's own transient model, `l4e7_p0sol.out`
sections 0d, 2b and 5d; the selected sense arrangement C2 composed; a stiff 36 V source, no source resistance credited at a fault
at the connector):

| Case | What the model reads | Parts hit (rating, PRINTED LIMIT unless stated) | Claims hit |
|---|---|---|---|
| F1, the source steps onto the port with the guard on, at the envelope's least loop 0.30 uH | PV_F 321.9 V; Q12's VDS 307.4 V; INP 64.3 V; TRK_VS 37.83 V with D4 carrying 16.1 A; the sense bank's differential 2.57 V; Q12 turning off about 457 A (the as-drafted network's figure) | U21's VS, CS+, CS- and ISCP (100 V absolute) and its INP and EN/UVLO (20 V); the port bank C131, C132, C135, C136 (100 V); Q12 CSD19532Q5B (100 V); D4 SMCJ30A (driven into conduction under a sustained source); U18 and U23 INA169 (+2 V differential); D11 SMCJ40CA (its clamp far exceeded) | IF-01's protection of the solar entry against D-10's single fault; R-173's solar guard as a protection; the backstop's sensing (U18) through the event |
| F2, the same at about 1.04 uH | PV_F 118.5 V; Q12's VDS 108.5 V; INP 23.7 V; TRK_VS 31.58 V (0.22 V under D4's least breakdown); the bank 1.16 V | U21 (100 V, 20 V), the port bank, Q12 (100 V) | as F1 |
| F3, the same at the record's 3.30 uH reference loop | PV_F 83.48 V; every other rating inside its 10 % line (the bank 0.48 V, corner search 0.55 V; INP 16.67 V; VDS 74.85 V; TRK_VS 29.14 V) | U21's recommended operating VS row, 80 V (L6P-F10) | the port's operation inside the controller's recommended conditions during the event |
| F4, a source arriving with the guard off (the cold connection), at the least loop | slew 56.10 V/us; PV_F 84.62 V | U21's drain-side pins' slew, 60 V/us absolute held, the 54 V/us SESSION line not; the recommended 80 V row (held from 0.78 uH) | the SESSION margin rule on the guard's pins |

The port's own ratings hold their lines only above source loops the model prints (PV_F's 90 V line from 2.44 uH, the recommended
80 V row from 4.03 uH, Q12's VDS from 1.83 uH, EN and D4 from 1.04 uH, on the drafted network); no document bounds a stiff source's
loop or resistance at the connector, so these are not passing floors.

**One open case inside E-1 that is not a failing case: the lower-source back-feed** (set 30 note, 6 October 2026). A stiff source
below the stage's voltage arriving after a withdrawal: while the guard is off, PV_P back-feeds PV_F through Q12's body diode, and the
source draws the stage's charge back through it (`B2-PRESENCE.md` section 7; `l4e7_p0sol.out` 5g). No record computes it, so it
neither fails nor passes and is not a row of the table above. It is REMAINING ENGINEERING inside E-1: the receiving company computes
it on E-1's corrected circuit as part of E-1's correction, against (b)'s requirement that every part stays within its makers'
absolute maximum ratings during the fault, with S1's own criterion for the case (Q12's body-diode current inside its pulsed rating);
S1's added row (b) is the later validation of that computation, not a substitute for it. Sources: the remaining-engineering ledger's
HO-F (`fnd/ledgerfix` `99bbc0c6`); the owner's part 23, "Supplier item S1 must carry that engineering problem, rather than presenting
it solely as an unperformed validation test." (`v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:680`); cx46, "D-10's E-1 retains
F1-F4 and the lower-source back-feed case." (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:95`).

**(b) The applicable requirements, unchanged, with no new exclusion:** D-10 is L4-E9's single fault "a stiff 36 V source on the
solar port" (a vehicle or shore lead in the panel's receptacle), from the kit's declared 9 to 36 V source class (REQ-015); the
owner's amendment of 2 October 2026, item 3: a selected remedy with "a bounded analysis against the approved fault exposure and
component ratings", the approved normal window kept and "fault protection does not extend the permitted operating range"
(REQ-016's window unchanged); every part within its makers' absolute maximum ratings during the fault (cases F1, F2), the
controller inside its recommended operating conditions while it must act (F3), and the record's SESSION 10 % margin lines (F4).
The envelope stays the record's: a stiff 36 V source, loops from 0.30 to 10.20 uH, a fault at the connector with no lead
resistance credited and at the lead's far end, every start the guard is on in. Not adopted, and not to be adopted to obtain a
pass: a least loop above 0.30 uH, a credited source resistance at the connector, an exclusion of the guard-on starts or of a
source added in parallel with a connected panel.

**(c) The correction or justified model revision needed before any passing claim**, then its qualification. The defect's
mechanism: with Q12 closed, the current the source drives into every capacitor behind Q12 rises at a rate only the source's loop
sets, and when U21 opens Q12 that current is turned into the port's voltage; nothing in the drafted circuit bounds it
independently of the loop. A correction must bound that current or the energy and voltage it delivers to the port, at every loop
of the envelope; a model revision is acceptable only on measured evidence of the loops and resistances the requirement admits.
What the desk found and what a supplier may investigate (none selected; each must be shown against cases F1 to F4, with the
lower-source back-feed computed on the corrected circuit):

1. **A series element ahead of the stage's capacitance (B1):** rejected at the desk with the board's XAL1510-103 (the cut
   current 31.1 A over its 26.3 A Isat; its resonance with the entry at 2.7 to 3.2 kHz inside CS101's band where M2 is decided).
   A choke rated over the cut current, damped against CS101 and against the converter's negative input resistance, is open to
   investigation, with M2 re-run on it.
2. **Route B2, the presence pair (UNSELECTED, WITHDRAWN AS DRAFTED, no protection credit; no owner item, the approved interface
   stands):** its cold-connection guarantee is withdrawn after Astra's check cx45 (no sequenced connector chosen, no worst-case
   contact and control timing proof, BST kept charged from the back-fed VS; `B2-PRESENCE.md` section 5a), and its pair faults are
   not fail-safe (the two cores shorted together defeat it silently; a presence core shorted to a positive core of the lead puts
   INP over its 20 V absolute maximum; section 5b). **P2 and P3 are REMAINING ENGINEERING outside the baseline:** a supplier who
   takes up any presence-pair route does so as a new route with its own check, and owes monitored or fault-tolerant detection,
   INP's protection and the timing proof first. It would leave a source added in parallel with a connected panel and a lower
   stiff source arriving after a withdrawal, and it would not change the port's response when the step happens. It does not
   resolve D-10.
3. **The port's energy absorption:** a clamp with a lower dynamic resistance than D11, or an RC snubber or absorber at PV_F sized
   for the energy the loop holds at Q12's turn-off, keeping PV_F under 80 V (recommended) and 100 V (absolute) at every loop, with
   the port bank's own energy and its parts' pulse ratings shown.
4. **A different cut-off element or method:** a faster short-circuit path (the TPS48111-Q1's 1.6 us was evaluated by the record
   and still fails at 1.00 uH), an active current limit that responds faster than the loop's di/dt, a detector of PV_F's rise that
   opens Q12 before the current builds, or a guard that closes onto the stage only through a current-limited precharge path
   whenever the port's voltage steps.
5. **A justified model revision:** the loop inductance and resistance measured on the kit's own leads and on the stiff sources
   the requirement admits (vehicle and shore leads, the NATO plug cable), and the source's own resistance bounded by a document or
   a measurement; the model re-run on those figures. A revision changes the envelope only on that evidence and never by assertion.

The qualification evidence follows the correction, not before it: S1 below on the corrected circuit, S2, and M2 (CS101) and M3
(CS114) re-run wherever the correction changes the port.

**(d) What stays PROVISIONAL, and what can be completed independently** (the owner's part 23 asks which stable outputs "can be
completed independently", `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:708`; none of them is completed yet). PROVISIONAL until
E-1's correction and S1: IF-01's protection claim for D-10; R-173's solar guard as a protection (its cut-off band and the cold
connection's absolute ratings stand as computed); R-176 rows 2 and 3; R-180 (a loop bound); the port's parts (D11, the port bank, Q12,
C126, R96 and R97 as protection) and their Layer 6 rows; board E's port layout and its Layer 8 fault table; the guard's Layer 9
bench rows. Independent of E-1 (they do not wait on its correction), on the present port network, and ADDRESSED IN DRAFTS,
PROVISIONAL, not completed (set 30 note, 6 October 2026, in place of "Completed independently of E-1": the drafts are not applied
and not independently accepted; D-16's correction PROVISIONAL in S3 and S4, the register's R-240,
`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:336`, and `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:841`, `:1031`; set 31's reading,
`v2/docs/records/l4e9/SET31-CHANGES.md:70-72`, `:113`): D-16's correction (U5's input sense
retired, 0 V on its pins by construction; U23 on the bank; R16 34.0k; the regulation's band; the correlated margin to the trip;
the 100 W static bound 93.5783 W and check (b)'s 1.052 ms); M2 with the selected sensing (to be re-run only if E-1's correction
changes the port or the bulk); the INP divider's ratio (INP under 18 V wherever PV_F is under 90 V).

## The claims each item supports, and the provisional choice in force until it is done

| Item | Claim it supports | Affected files and decisions | Bounded provisional choice (scope amendment, point 2) |
|---|---|---|---|
| S1, the guard-on step, on E-1's corrected circuit | the qualification of E-1's correction (no S1 run on the present circuit can make a passing claim: the model fails it, cases F1 to F3); its added rows (a) and (b), the later validation of the parallel source and of the lower-source back-feed that E-1's correction computes first | `apply_gen_sch_e_solar_guard.py` (R-173), E-1's correction, R-176 rows 2 and 3, R-180, IF-01 | none for D-10: it is an unresolved protection defect (E-1); the outputs E-1 (d) lists stay PROVISIONAL |
| S2, the cold connection (a source arriving with the guard off) | D-10's arriving-source case | R-176 row 2 | the cold connection (MODELED, cold=True; no route B2 credit, B2 withdrawn as drafted): every absolute rating held over the whole envelope (PV_F 84.62 V, slew 56.10 V/us, INP 16.90 V with R97 24.9k); the 54 V/us SESSION line holds from 0.33 uH and the recommended 80 V VS row from 0.78 uH |
| S3, A7 at zero differential | the regulation's lower band (energy) and, for a sink the sheet's text excludes, its margin to the trip | `apply_gen_sch_e_p0sol.py`, IF-02 | the regulation's band is computed with A7 at 0 uA; any current A7 sources lowers the regulated input current (8705af p.31); a sink (INFERRED absent) is covered by the margin up to 3.67 uA |
| S4, the regulation at 25 V | D-16's regulation row (R-189 as rewritten) | IF-02, R-20 | the computed band, nominal 2.538 A, at most 2.921 A, at least 2.184 A with A7 at 0 uA |

## Specimen, quantities and pass limits

**Specimen (S1, S2, S4):** the controlled first prototype of board E's solar stage with the drafted guard (R-173) and P0-7's
draft applied, or a coupon of the same parts and layout from J_SOLAR to U5's input: F2, D11, the port bank C131, C132, C135
and C136, U21 with R87 and Q12, Q13, the bulk C11, C12 and C69, C133 and C134, the sense bank R60 to R64 with U18 and U23,
C71 to C74, C13 to C15, C64, D4 and U5. Three specimens.

**S1, a stiff 36 V source stepping onto the port with the guard on, on E-1's corrected circuit** (run after the correction
exists; on the present circuit it would only confirm the failure the model computes). A 36 V source able to deliver at least 500 A for 20 us
(a low-ESR capacitor bank charged to 36 V) switched onto J_SOLAR by a low-inductance switch, through three measured loops:
0.30 uH, 1.0 uH and 3.3 uH (each loop measured first at 100 kHz, the switch and the source included). The stage held with the
guard on at 7.5 V, at 17.0 V and at 25 V before the step, idle and at 3.74 A drawn. Five steps per combination per specimen
(3 x 3 x 2 x 5 = 90 steps a specimen). Measured at the pins with Kelvin differential probes: PV_F at U21's VS and CS+; INP;
EN/UVLO; Q12's VDS and current (a Rogowski probe of at least 500 A); TRK_VS; D4's current; the bank's differential at U18's and
U23's pins; U5's CSPIN to CSNIN. **Pass:** PV_F under 80 V (the TPS4811-Q1's recommended operating VS row) and under 90 V
always; INP under 18 V; CS+, CS- and ISCP slew under 54 V/us; Q12's VDS under 90 V and its current inside its derated safe
operating area for the measured time; TRK_VS under 31.8 V and D4 carrying no current; the bank's differential under 1.8 V;
U5's CSPIN to CSNIN under 10 mV in magnitude (0 V by construction; the reading checks the layout). **Added rows, each the later
validation of a case E-1's correction answers at the desk first, not a substitute for that engineering** (set 30 note, 6 October
2026, in place of "Added, whatever happens to route B2": B2 is withdrawn as drafted and changes neither row; the ledger's HO-F; the
owner's part 23): (a) the 36 V source added at the solar tail in parallel with a connected bench panel (E-1's guard-on step, cases
F1 to F3, with the source in parallel), the same loops and pass limits; (b) the lower-source back-feed, computed inside E-1's
correction (E-1 (a)): the panel withdrawn with the stage at 17 V and a 12 V source of the same capability mated at once (PV_P
back-feeding PV_F through Q12's body diode): Q12's body-diode current inside its pulsed rating and PV_P's fall recorded.

**S2, the cold connection.** The same rig with the guard off and its CBST discharged; the 36 V source stepped onto J_SOLAR from
0 V and from 25 V through the 0.30 uH loop, five steps per specimen. **Pass:** the slew at CS+, CS- and ISCP under 54 V/us,
INP under 18 V, PV_F under 85 V. No route B2 rows: B2 is withdrawn as drafted, and a presence-pair route taken up again would
bring its own engineering (P2 and P3, detection, INP protection, the timing proof; `B2-PRESENCE.md` sections 5a and 5b) before any
validation row.

**S3, A7's output at zero differential.** Five LT8705AIUHF#PBF on a test fixture, CSPIN = CSNIN = VIN at 16 V and 25 V,
IMON_IN held at 1.20 V by a source-measure unit, the current out of IMON_IN measured at -20 C, +25 C and +62 C (case).
**Pass:** from -0.5 uA (sinking) to +1.0 uA (sourcing) at every point (the regulation then within 3 % of its computed setting, and its margin to the trip at least 0.33 A).

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
the unfavourable side. E-1 is accepted only when a correction or a justified model revision exists, every case F1 to F4 reads
inside its requirement on the makers' printed limits with the revised model, the lower-source back-feed is computed on the
corrected circuit inside (b)'s requirements with S1's criterion for it (Q12's body-diode current inside its pulsed rating; set 30
note: the ledger's HO-F; no new limit), and S1 and S2 then pass on the corrected specimen;
until then D-10 stays an unresolved protection defect. A failure of S3 or S4 lowers the regulation's energy claim and changes no
protection.

## Cost and schedule

Not known: no supplier has quoted. The quotation request is the owner's to send.
