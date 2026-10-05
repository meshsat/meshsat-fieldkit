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

## C-DEV rev 1
Layer 9's budget (`records/l9pwr`, round 2 at `51821143`), the device rail U7 at the least load voltage: 7.472 A demanded (4.9019 V,
every load at constant power; 7.181 A at 5.1 V) against the LM5176 stage's 7.0957 A loop minimum. Connected: L9P-F04 (the PA rail,
8.188 A against the same minimum), the JST-VH lead's 10 A rating (cx40 Q4: a resistor-only change has no value that both supplies
C-DEV and keeps the loop's maximum under 10 A). Consumers: T5, V3.

## C-SHORE rev 1
L4-E11 19e (DD-3) at `e60a94a8`: 7.136 A held by the input breaker from 76.25 C air. Consumers: T3, V2.

## C-CU rev 1
Record l9stk 14.6, the coordination table: continuous, transient and fault current until protection clears, per conductor.
Unsettled: the fabricator's stackups and prices. Consumers: T6.
