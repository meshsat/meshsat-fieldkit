### 19h. DD-7: the latch-off breaker, the input-return reset and the hardware charge inhibit

**Superseded in its board A sensing by round 10 (section 20):** the loop's sense (Q47 on half of DOCK_EN_OUT) and the dead point
(Q48 on half of CELL+) below are round 9's; record l8p's L8P-F04 and L8P-F05 found them failing, and section 20 redraws them. The
input-return reset and Q49 stand.

**The change** (record l9stk 15.4b, read at `0d72880b`, the coordinator's addition): the automatic-retry LM5069-2 fails its own breaker FET under
a persistent fault (0.79 of the derated SOA in a hard short; over 150 C in a resistive fault on VSYS), so board P's breaker is now the
**latch-off LM5069-1**. After a trip it stays off until its UVLO or its VIN cycles; on battery the kit goes dark. **DD-7** (owners board
A's generator with this record): when an input returns, the charger could push charge current through the latched breaker's body
diodes. **The checker's B-R2** on that recheck: the pulse covers only the first restart; if the fault persists the -1 latches again with
the input still present, no second pulse comes, and only the firmware stands between a commanded charge and the FET's body diode (4 A at
1 V is 4 W, 276 C settled). The owner's criterion asks firmware independence. Record l9stk's `0d72880b` adds **C-1c**, a restart inhibit
on the breaker pad (an NTC bridge gated by PGD, blocking restarts from 83.2 C), which widens the RC hold to 0.110 to 0.907 s and DD-7's
restart to 0.948 s from the loop's closing, later while a hot pad cools (its time NOT HELD, its E-15).

**The input-return reset (SESSION, drafted in `apply_gen_sch_a_dd7.py`, after record l8p's PTC draft):**

| Part | Value | What it does |
|---|---|---|
| Q44 (2N7002) | drain on DOCK_EN_RET | pulls the enable loop's return low: the loop opens as an undocking does, board P's second inverter pulls UVLO at once (on in 16 us; C_U drains in 1.10 ms behind it), the -1's latch resets |
| R106, D25 | 1M from VIN_RAW; BZT52C12 (11.4 to 12.7 V) | Q44's gate DD7_G follows an input on the dock, clamped |
| Q45 (2N7002) | gate FE_RUN | ends the pulse when U34 releases the front end: **78.6 / 127.3 / 201.2 ms** after VIN_RAW passes U34's UV threshold (6.889 to 7.282 V rising with this record's R14); C212 is C105's part and value on the same TPS37A010122 |
| Q46 (2N7002) | gate DD7_ALIVE, CELL+ over R107 / R108 (100k each) | holds the gate low while CELL+ is over 5.05 V (cannot conduct under 1.98 V): an input arriving on a live pack opens nothing |

The pulse is at least 78.6 ms, 71 times C_U's 1.10 ms drain; the -1's timer falls under its 0.3 V re-enable within 34.0 ms, inside the
pulse and the hold with 154.6 ms to spare. From VIN_RAW passing U34's threshold to the restart's end: **at most 1.149 s** (the pulse
201.2 ms, the hold 0.907 s, the start 40.7 ms); from the loop's closing, record l9stk's 0.948 s; longer while C-1c holds a hot pad, the
hardware inhibit below holding the charge meanwhile. **The UVLO edge** (record l9stk): read at the falling edge, an input arriving within
34.0 ms of a latch does not restart the breaker; that fails safe (the breaker stays off, the inhibit holds the charge), and the input's
next return or a redocking restarts it.

**The hardware charge inhibit (SESSION, the same draft), for the later latches:**

| Part | Value | What it does |
|---|---|---|
| R109, R144 | 1M each, DOCK_EN_OUT to SYS_INH_G to ground | **the signal**: the loop powered, i.e. the pack's cells reach board P's breaker (BRK_VIN alive); docked, DOCK_EN_OUT is at least 7.735 V (the pack's 10.6 V, RT1 at its cold least 5 kOhm, l8p's 10k and 22k), so SYS_INH_G at least 3.829 V |
| Q47 (2N7002) | gate SYS_INH_G | on while the loop is powered |
| Q48 (2N7002) | gate DD7_ALIVE | **the threshold**: releases the inhibit once CELL+ (the pack's terminal) is over 5.05 V; under 1.98 V it cannot conduct |
| R82, R83 | 100k from VBAT, 200k to Q47's drain | Q49's VGS -VBAT/3: -4.07 V at VSYS_MIN's 12.054 V (its threshold -1.3 V at most), -9.86 V at the 29.2 V clamp (12 V absolute) |
| Q49 (AO3401A, C15127) | source VBAT, drain CH_BATDRV | **where it acts**: holds the battery FETs' gates at VBAT, so Q39, Q40 and Q42 are off and their body diodes point from the pack to VSYS; no charge leaves VSYS for the pack while the source keeps carrying the kit |

The inhibit acts exactly while the loop is powered and the terminal is dead: the breaker off (latched, in its hold or starting) with the
cells present. **No firmware.** BATDRV meanwhile sinks at most 3.83 mA (its 11.5 V over its 3 kOhm least RBATDRV_ON, SLUSE65A): an
addendum to Q-TI-17 asks TI whether holding BATDRV at VSYS is acceptable. **Not inhibited, by design:** with the loop unpowered (the gauge's
FETs off, the pack absent, undocked) a pack's wake and precharge pass the breaker's body diodes at the gauge's own current (record l9stk's
charge direction), and source-only operation (U-04) is untouched.

**The loop's load** (an interface effect for records l9stk and l8p): the 2 MOhm sense at DOCK_EN_OUT moves the first inverter's gate at
l9stk's bound point (10.6 V, RT1 at 47 kOhm) from 2.952 V to 2.939 V against its 2.5 V threshold (47 kOhm is not a point of this
part: withdrawn as a bound by round 13, 23g).

**E-14, extended to a second latch with the input present.** With the inhibit, the charge into a latched breaker is the battery FETs' off
leakage (IDSS 1 uA at 25 C each; the hot value not printed). Without it, at the breaker FET's VSD 1 V and IF-2's 52.5 C/W, held:

| Charge current | Body diode | TJ from 76.25 C |
|---|---|---|
| the charger's ChargeCurrent at POR (TI's E2E answer, D4), 0.256 A | 0.256 W | 89.7 C |
| R-b's largest actual current, 1.2567 A | 1.257 W | 142.2 C |
| the checker's commanded 4 A (outside R-b) | 4 W | 286 C at 52.5 C/W (276 C at the sheet's 50) |

So the inhibit is what holds a commanded charge beyond R-b off the FET, wherever it sets. **E11-45** measures it: a hard short kept, the -1
latched again with the input present and ChargeCurrent forced to its register maximum, the current into PACK_P at most 1 mA and the FET's
junction within 2 K of its case for 10 minutes; and (c2) the open case below, recorded.

**Its reach, read after drafting (the one design-out attempt):** the inhibit sets only when CELL+ falls under 1.98 V. A latch while a source
is present (the pack supplementing into the fault, the battery FETs on) leaves CELL+ tied to VSYS, which the charger holds into a resistive
fault at sqrt(P x R): **10.4 V** at the breaker's least-limit fault of 0.915 ohm with the front end's 118 W, so the inhibit sets only for
faults under **33 mOhm**. When such a resistive fault clears with the -1 latched, a charge passes the breaker's body diode with CELL+ reading
alive. **The breaker's PGD reads high in that state too:** the LM5069 switches PGD on VDS alone (8.3.6), and a reverse current makes VDS
negative. So no board A signal, and no PGD, tells a latched -1 passing charge from an -1 that is on. **B-R2 stays OPEN for that case**:

| Route | What it is | Owner |
|---|---|---|
| **R1 (SESSION: preferred)** | board P tells the latch by the breaker's gate state (a gate-below-OUT comparator brought to board A), or blocks reverse current in the breaker (a reverse-blocking element), so a latched -1 passes no charge | board P's generator (record l8p) with record l9stk |
| R2 (the fallback) | a hardware cap on the charge current on board A, above R-b's largest 1.2567 A and under 1.405 A (the latched FET's body diode at 150 C held from 76.25 C at VSD 1 V and 52.5 C/W): a high-side current-sense part at R17 with a timed off-state on Q49, none of whose parts is held; an 11.8 % window | this record with board A's generator |

Until one is drawn, a charge past R-b in that state rests on the firmware (R-b, IF-7); at R-b's largest the FET reads 142.2 C held.

**The charger-side hold** is the inhibit itself where it sets, until the terminal is alive; the firmware's IF-7 reports the trip and writes ChargeCurrent
only after the restart (**E11-44**); the hold does not wait on it.

**Residuals:** Q49 shorted holds the battery FETs off (their body diodes carry the discharge, and record l8p's PTC trips the breaker before
their junctions pass 150 C); Q47, Q48 or Q49 open loses the inhibit or never releases it (E11-45 d); a Q46 open lets an input's arrival
drop a live pack for the pulse and the restart (E11-45 b); Q44 shorted holds the breaker off (fail-safe, revealed at commissioning).

**Status:** DD-7 **DRAFTED** for the first restart and for every latch whose fault takes CELL+ dead (the dark kit on battery, a hard short,
the input's return), CONDITIONAL on E11-45 and on TI's answer on BATDRV held at VSYS; **B-R2 OPEN** for a latch with a source present into a
resistive fault (route R1, owner board P's generator with record l9stk; R2 this record's fallback); IF-7 the firmware owner's. New board A designators: Q44 to Q49, R82, R83, R106 to R109, R144, D25. The
draft is a new apply script in this record: L4-E9's change list gains it after record l8p's PTC draft (the integrator's).

Not claimed: nothing here is verified, built or measured; software tests establish this record's own behaviour only.

