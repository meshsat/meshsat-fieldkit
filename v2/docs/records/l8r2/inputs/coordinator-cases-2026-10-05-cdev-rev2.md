# Shared case rows (coordinator; plan of 4 October 2026, section 4a; PLAN-01). Local working copy; the plan entry carries them.

Sources read at set 29's line (`e58e906a` when first fixed; the records named below are unchanged at the later tips unless a row says so).
A needed change is a new revision of the row, announced to every consumer. Nothing has been built, bought or measured.

## C-PROT rev 1 (14:19 CEST)
Record l9stk `L9-STACKUPS.md` 15.1 (the owner's criterion), 15.6, 15.7 at `0d72880b`; L4-E11 section 19 at `e60a94a8`.
Fixed: 10 A held and 18 A for 60 s never interrupted; every series part within its limits below and above the trip; board P's FETs
welded, no firmware; the breaker's band 18.32 to 23.93 A; start at L4-E12's 76.25 C plus own heating; docking included; each source
(shore, solar, vehicle) present or absent. Unsettled: current sharing between the battery FETs; the LM5069's internal 1 MOhm tolerance.
Consumers: T1 (L4-E11 round 10), T2, T4 (board P, with CHGIN = 1 above T3 in discharge), V1, V2, the Layer 9 refresh.

## C-ALLTX rev 2 (14:50 CEST; rev 1 withdrawn)
Rev 1 said "the loads of PS-ALLTX at HIGH". That was the coordinator's error: it is not the requirement's case. Astra's advisory
challenge (cx40, 14:35) computed both readings and showed the difference; the authoritative texts are:
- REQ-018's acceptance: PS-ALLTX (every transmitter keyed, the outlets off at 0 W, the pack heater and the standby WiFi card off)
  supplied with every rail in regulation through a 60 s key-down begun at a pack rest voltage of 15.5 V or more, every cell at most +55 C.
- CONOPS 4a's row PS-ALLTX: every transmitter keyed at once, monitor full, fans (running), outlets off, the standby WiFi card off,
  the other loads at typical.
- Decision D-11's basis (SC-10, SC-35; rv-pwr's `typ_nontx`): the transmitters at their HIGH figures, the non-transmit loads typical.
Fixed: that state and no other: transmitters keyed at HIGH, monitor full, FANS RUNNING, outlets 0 W, heater off, standby card off,
every other load at typical; 60 s from 15.5 V rest; cells at most +55 C; K2's gates at key-on (air under +50 C, flange at most +75 C);
K1's repeat (the next key-down 2 s after the last); the service limit 18 A indicated.
On Layer 9's final drafts this case needs 16.214 V rest (253.61 W at VBAT): F01 / D-17 OPEN.
Labelled UNSETTLED (each is an input a correction must bound, never assume):
- the compute modules at typical (4.5 W each) is CONOPS's definition, but nothing drawn holds them there: K4's "no compute stress" is a
  provisional session control with no numerical ceiling in FW-A05, and the CM5's 0.9 A is typical data with no printed maximum.
  Sensitivity: at the budget's 8 W a module the need is 16.863 V fans on and about 15.96 V fans off (Astra's arithmetic);
- R_cell 0.06 Ohm is an ASSUMPTION (the maker prints 35 mOhm initial AC impedance only);
- the gauge's current error (up to 0.486 A one-sided on the 2 mOhm shunt, uncalibrated) against the 18 A indicated limit;
- the path's resistance tolerance;
- Layer 9's raw PS-ALLTX HIGH row powers the standby card (9.1 W), which REQ-018 requires off: a budget defect, not this case.
FAN_OK changes this case's text (CONOPS lists the fans as running): adopting it is a controlled amendment of an accepted Layer 2
page, the owner's to approve, and only after its electrical and thermal support exists. It is NOT supported as proposed (cx40).
Consumers: T5, V3. (W3 ran on rev 1 and reported both readings.)

## C-ALLTX rev 3 (15:45 CEST; rev 2's quoted figure withdrawn)
Rev 2's definition stands; its quoted figure did not belong to it. "16.214 V (253.61 W at VBAT)" is decision D-11's basis as rv-pwr
models it (rv-pwr's `typ_nontx`), which keeps the STM32 supervisors, the hubs' cores, the QMX's USB/HDMI, board E's controller and the
Geiger at their HIGH figures, while REQ-018 with CONOPS 4a says every other load at typical. Layer 9's T5 round (record l9pwr round 4,
`fnd/l9t5` at `cce21ca7`, section 7b) computes the case from its own text, each pack-fed converter at the case's VBAT:
- THE CASE (REQ-018 + CONOPS 4a): 241.039 W at VBAT, need 15.5162 V at 18 A and R_cell 0.06 Ohm: deficit +0.0162 V nominal. F01 OPEN.
- With the printed uncertainties bounded (the gauge's uncalibrated error, the dock contacts at their printed maximum): 16.0684 V.
- Labelled scenarios, never substituted for the case: D-11's basis as rv-pwr models it (16.1825 V at the case's VBAT; 16.214 V
  with every converter at 16.8 V, L9P-F01's figure); the compute modules at 8 W (16.1718 V); R_cell 0.07 / 0.08 Ohm (15.7562 /
  15.9962 V); the PA stage at 0.95 or the 5.1 V stages at 0.85 (15.7479 / 15.8190 V).
- Not bounded: the rest voltage's fall during the 60 s (R-214, no curve held).
Consumers: T5, V3; the set 30 records restate L9P-F01's figure as the scenario it is.

## C-DEV rev 1
Layer 9's budget (`records/l9pwr`, round 2 at `51821143`), the device rail U7 at the least load voltage: 7.472 A demanded (4.9019 V,
every load at constant power; 7.181 A at 5.1 V) against the LM5176 stage's 7.0957 A loop minimum. Connected: L9P-F04 (the PA rail,
8.188 A against the same minimum), the JST-VH lead's 10 A rating (cx40 Q4: a resistor-only change has no value that both supplies
C-DEV and keeps the loop's maximum under 10 A). Consumers: T5, V3.

## C-DEV rev 2 (5 October 2026, 16:00 CEST; rev 1's SUPERVISOR term replaced, everything else of rev 1 stands)
Issued by the coordinator from Slot C's T10 round 5 (`fnd/p0t10` `5d772b24`, `T10-ROUND5.md` section 6, `l9t5_t10.out` 10g). Rev 1
carried rv-pwr's HIGH for the three STM32 supervisors (0.400 A a controller plus 0.060 A of its other parts, 0.46 A a regulator;
+5V_IOC 1.3800 A), the unbounded state that put the composed AP2112K LDOs at 160.1 C. Rev 2 carries the BOUNDED state of T10-A1's
contract row (FW-B20, FW-B21: VOS3, HCLK at most 144 MHz, the enabled peripherals named, each supervisor's own TXD dominant at most 2 %
of every 100 ms window per fabric; rev Y's rows as the cover, rev V smaller):
- for the thermal and the regulator rows: **0.2558 A a regulator** (rev Y; 0.1732 A rev V) with FW-B21's share and the circuit's own
  auxiliaries (0.0069 A at most, every resistor from the rail at the full rail, from the composed netlist); the controller alone
  0.2396 A at TJ 111.8 C at 76.25 C air;
- in the budget's own form (power only, conservative): 3 x (0.2396 + 0.060) x 3.3 = **2.966 W at +3V3_IOCx** in place of 4.554 W;
  **+5V_IOC 0.8989 A** in place of 1.3800 A (read as a regulator figure it would give 130.9 C because the declared 0.060 A over-covers
  the auxiliaries: it is not the thermal figure).
CONDITION: rev 2 holds only with FW-B20 and FW-B21 applied to `HW-FW-CONTRACT.md` (drafted in `records/l9t5/apply_hw_fw_contract_t10.py`,
unapplied, a Layer 5 row brought forward as a named prerequisite of the power gate) and the SHDN draft composed; until Layer 5 applies
them, a result on rev 2 is labelled "C-DEV rev 2 (conditional on FW-B20/B21)". A result on rev 1's HIGH is a LABELLED SCENARIO.
Clarification 16:25 CEST (Slot C's round 5 answer to the owner's part 21, `fnd/p0t10` 8da64910): at the LDO's worst drop corner (1.0402 V,
191.4 K/A) rev Y's rows MISS the 125 C criterion (125.2 C bounded, 126.5 C both fabrics faulted), so the FITTED supervisor is REVISION V
(SESSION decision L9T5-D7; CON-017 already restricts to V or X): the regulator rows use 0.1732 A (rev V, 109.4 C, margin +15.60 K, lost
at a local air of 84.20 C); rev Y's 0.2558 A stays the COVER for a rev X part, whose current waits on the vendor row V-B20 (0.2318 A
provisional). The budget form (2.966 W, 0.8989 A) is unchanged as the conservative figure.
Consumers: P0-2 (the device rail I-03 and the return: Slot A recomputes U7's demand with the supervisor term of rev 2; rev 1's 7.472 A
at 4.9019 V is superseded for that term only), P0-3, P0-4 (eFuse U23/U24 downstream demands if the IOC rail is among them), P0-6, the
focused check cx45. L9P-F03's figures on rev 1 stay as given in the records that cite rev 1.

## C-SHORE rev 1
L4-E11 19e (DD-3) at `e60a94a8`: 7.136 A held by the input breaker from 76.25 C air. Consumers: T3, V2.

## C-CU rev 1
Record l9stk 14.6, the coordination table: continuous, transient and fault current until protection clears, per conductor.
Unsettled: the fabricator's stackups and prices. Consumers: T6.
