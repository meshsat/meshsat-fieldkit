### 20c. The thresholds and their tolerances (MAKER: TI SNVSBJ1E, VITP and VITN 0.792 / 0.800 / 0.808 V, the variant's 2 % hysteresis within +-1.5 %, ISENSE 100 nA at 800 mV and 2 uA its largest row; resistors at their tolerances, each at its worst sign; INFERRED)

| Reading | Where it switches | Against |
|---|---|---|
| the return held (U48 channel 1, its OV release) | under **0.7755 V** at least; read closed over 0.84 V at most | board P's pull, 0.055 V: **0.72 V of margin**; the closed return reads closed for any RT1 under 269 kOhm at 10.6 V (2.894 V at RT1 47 kOhm, which bounds nothing: round 13, 23g) |
| the loop powered (U48 channel 2, its UV release) | over **1.981 V** at most (1.825 V at least); unpowered under 1.789 V at least | the interface's 2.0 V; the held DOCK_EN_OUT (RT1 at 5 kOhm, R106 +1 %, board A's 984 kOhm on it): **2.545 V at 7.6 V, 3.535 V at 10.6 V, 5.581 V at 16.8 V**, 0.564 V or more over the powered reading |
| CELL+ alive (U47 channel 2, read only while an inhibit is asked and the loop is powered) | dead under **4.076 V** at least, alive over **4.774 V** at most (the foot at RESET's 0.060 V, VOL read as 60 ohm) | the breaker's restart drives CELL+ to the pack's 10.6 to 16.8 V; the latch holds CELL+ at 0.154 V (below) |

**The load on DOCK_EN_RET** is SENSE1 alone, at most 2 uA: over 8.7 MOhm at the return's 17.4 V clamp, against the interface's 1 MOhm.
**The loop at 10.6 V and RT1 47 kOhm** (record l9stk's former "bound point"; **withdrawn as a bound by round 13, 23g:** 47 kOhm is
not a point of this part): the first inverter's gate reads 2.952 V unloaded, 2.939 V with round 9's 2 MOhm, **2.894 V** with round
10's loads (R109 and R144 on DOCK_EN_OUT, 2 uA on the return), against its 2.5 V; board A reads it closed with 2.054 V to spare.
Board A's loads move the loop's levels by 0.058 V there, and no more is claimed of it.

**The interface's literal box, and why board A reads the return held under 0.7755 V and not up to 1.0 V (SESSION; finding
L4E11-R10-F1 for record l8p).** The box "RET under 1.0 V with OUT at 2.0 V or over" holds every state board P produces (the return
at 0.055 V). It also holds a CLOSED loop: RET/OUT is 22 / (22 + RT1), under 0.5 for RT1 over 22 kOhm, at BRK_VIN under 2.82 V (RT1
30 kOhm) or 3.59 V (RT1 47 kOhm). Every ramp of a closed loop (a docking, the gauge's wake, a precharge back-fed through the breaker's
body diodes) passes through it, and a trigger there stops a dead pack's precharge (the hold and the inhibit while BRK_VIN rises,
then again on every rise). Board A's reading is therefore narrower than the box and holds the state board P produces with 0.72 V
of margin. The 1.0 V figure is a 2N7002's least threshold (l8p 12f).

**No window.** A ramping closed loop never reads held while RT1 is under **25.8 kOhm** (RET/OUT over 0.4603 when OUT reads powered).
Murata prints RT1 at most 15 kOhm at 25 C and 100 kOhm only above 110 C (DM-SA16-E056 Rev.1 p.4, MAKER); a back-fed precharge
carries at most 0.33616 A, so the FETs' copper sits at the air. At the precharge's floor (BRK_VIN 4.70 V, RT1 at 15 kOhm) the return
reads 2.20 V, 1.36 V over the closed reading; it would read held there only past RT1 91.1 kOhm.

**Against board P's guard.** Board A reads a closed return as held only past RT1 269 kOhm at 10.6 V (445 kOhm at 16.8 V); board P's
first inverter turns off (its gate 2.5 to 1.0 V) from 61.3 to 201.2 kOhm at 10.6 V: board A never reads held before the guard's own
trip.

