# M1 energy reconciliation: the pack, the panel, the night and the mission as written

Stream `energy`, branch `fnd/energy` from the integration set's tip `038037ed`, MESHSAT-1357, 28 September 2026.
**Prototype design: nothing in this kit has been built, ordered or measured.** Every figure on this page is
arithmetic on makers' figures, on generator declarations and on stated assumptions, computed by
`energy_budget.py` from `energy_inputs.yaml` (both beside this page; the output is `energy_budget.out`, and
every number quoted below is taken from that output). The readings of the makers' documents are an AI's:
**this is an AI review, not a qualified review.** No dash of any kind is used on this page.

**What the owner asked (28 September 2026), and what this page does with it.** M1 (`CONOPS.md` section 3) and
REQ-072 (`pcb_requirements.yaml`) are preserved as written: 72 hours in PS-IDLE-SPEC on pack and solar from a
full aged pack on the reference day. Nothing in either is rewritten here. External DC stays an option (section 6f)
and is not the mission's basis. The budget is reconciled against the loads as they are sourced (section 1), the
usable battery energy (section 2), the night (section 3) and the solar contribution (section 4); the balance and
the conflict are shown hour by hour with the numbers (section 5); the options inside the approved constraints are
listed with numbers and ranked (section 6); the smallest justified changes are presented explicitly for the
owner's decision (section 7 and `DECISION-PARAGRAPH.md`). Unmet criteria are left visible: REQ-072 reads FAIL
before and after this page.

**The inputs this rests on, pinned by sha256** (`energy_budget.py` refuses to run if any changed): the PVGIS
monthly irradiation file, the two Samsung INR18650-35E documents, the tree's power model outputs
(`records/rv-pwr/pwr_budget.out`, `records/hc2/pwr_red2.out`), board E's generator, and `energy_inputs.yaml`
itself. Stream d4energy's `energy_data.yaml` (branch `fnd/d4energy`, commit `9b43e274`) was read in full and
found sound; its load citations, its pack figures, its readings of the makers' curves and the PVGIS mean-day
profile it filed (commit `71be4943`) are reused and cited, not duplicated. Its `energy_budget.py` (untracked
there, 1320 lines) did not finish in 240 s in a read-only scratch run on this host and was not run again (the
host rule); nothing here depends on it.

---

## 1. Verified loads: what the state powers are made of

**Kinds.** S: a maker's own figure, with its document and page. R: a figure inside a maker's bound at a stated
duty (the maker publishes a range or a maximum). D: a generator's declaration read from a board's intent, a
copper-sizing allocation and not a consumption figure. T: a placeholder with no document. **MEASURED: none.**
The tree holds no measurement of any load, converter or pack; every figure below is a planning figure.

**1a. PS-IDLE-SPEC, 42.8 W at the pack terminals** (`CONOPS.md` 4a; `POWER-THERMAL.md` section 4; computed by
`records/rv-pwr/pwr_budget.py`, PLAN scenario at 14.4 V with each converter's loss off its own datasheet curve
and 22.5 mOhm of distribution counted once). Its 39 loads, battery-side, are listed one by one in
`energy_budget.out` section 1a with their kind and source; the sum is **42.82 W** against the model's 42.80.
The kind split: **S 20 loads, 16.8 W; R 8 loads, 11.3 W; D 8 loads, 6.3 W; T 3 loads, 8.4 W.** The largest
single figures: the monitor 6.03 W (T: Xenarc states only "at most 10 W", product manual v2 page 4); the live
WiFi link card 4.80 W (R: AsiaRF's "average 4 to 8 W", no idle figure); the three CM5 at 2.17 to 2.22 W each
(S: "idle typically 400 mA", CM5 datasheet section 3.3); the three supervisors 2.16 W (R: STM32H743 71 mA at
400 MHz, DS12110 Table 30, plus a declared 0.06 A each); the Ethernet switch 3.44 W over three rails (S: KSZ9897R
DS00002330D Table 6-1, every port at 1000 Mb/s, the maker's only such figure; energy-detect is 0.37 W).

**The declarations, and what the makers say for the same parts.** Five D rows (panel board C 1.62 W, other
+3V3_DEV logic 1.54 W, board E controller and sensors 0.83 W, board A logic 0.57 W, four CP2102N bridges 0.43 W)
carry 4.99 W battery-side (4.20 W at the loads) of copper-sizing allocations where d4energy's reading of the
makers' typical supply currents for the same parts sums to about 1.3 W at the loads (`energy_inputs.yaml`,
`maker_w_at_load`). The board D row runs
the other way (declared 0.60 W at the load, the makers' parts sum to 0.94 W). With the D rows at the makers'
figures PS-IDLE-SPEC reads **39.7 W** instead of 42.8. **The balance below runs at the model's 42.8 W and never
at the lower figure**: nothing is lowered to obtain a result; the difference is the bench's to settle.

**1b. The other three states, recounted from the same components** (the state rules of `CONOPS.md` 4c applied
to the PS-IDLE-SPEC rows with each row's own conversion factor; `energy_budget.out` 1b):

| state | definition (CONOPS 4c) | at the loads W | recount, battery W | the model's PLAN W | difference | kinds on |
|---|---|---|---|---|---|---|
| PS-IDLE-SPEC | three modules idle, monitor on, radios receiving, APRS beacons, link card up | 36.42 | 42.82 | 42.80 | +0.02 | S 20 / R 8 / D 8 / T 3 |
| PS-RED2, the reduced mode | slots 2 and 3 at the maker's typical 900 mA, slot 1 off, monitor off, both link cards off, 5G idle, beacons | 26.39 | 31.56 | 31.38 | +0.18 | S 16 / R 6 / D 8 / T 1 |
| PS-SURV-R, the heat stage after BANK-R1 | slot 3 alone, 5G off, beacons | 19.64 | 23.73 | 23.27 | +0.46 | S 11 / R 5 / D 8 / T 1 |
| PS-SURV, the heat stage as generated | slot 2 alone, LoRa and APRS off | 18.89 | 22.94 | 21.73 | +1.21 | S 11 / R 5 / D 8 / T 0 |

The recount does not re-solve the distribution I2R at the lower current (the model's I2R is about 0.2 W at
43 W and 0.1 W at 22 W) and keeps each row's conversion factor at its PS-IDLE-SPEC operating point, which
explains the +0.2 to +1.2 W. The states agree with `CONOPS.md` 4a and `POWER-THERMAL.md` section 4 to within
that. The T share falls from 8.4 W to 1.1 W once the monitor and the standby card are off: the reduced states
rest almost entirely on makers' figures and on the D allocations.

**What the bench must measure** (no `TEST-PLAN.md` row measures a power state today; T-H2 measures the inside-air
rise per state, not the power). Proposed rows, for the test plan's owner: **T-P1** the power at the pack
terminals in PS-IDLE-SPEC, PS-RED2, PS-SURV-R and PS-NIGHT-RELAY (section 6a) at +20 C, each to steady state,
with the D rows' parts read separately (the +3V3_DEV, +3V3_E6 and +3V3 rails on their INA226 monitors); **T-P2**
the pack's delivered energy from full to the graceful line at each state's constant power, new, at +20 C and at
0 C; **T-P3** board E's LT8705A stage and board A's front end on a panel emulator at 17.6 V in and 15.1 V out,
efficiency against current from 0.5 to 5.7 A; **T-P4** is REQ-072's own prototype acceptance (the 72 h run on a
panel emulator following the reference day's profile), unchanged.

## 2. Usable battery energy

From the cell maker's sheet (Samsung INR18650-35E specification Ver. 1.1, `v2/vendor/battery/samsung-35e-orbtronic.pdf`,
and the Technical Report of June 2015, `samsung-35e-conrad.pdf`), the pack's configuration (4S3P, D-06), the
protection window that sets the depth of discharge, REQ-014's ageing and the states' currents:

E = 12 cells x C_min x f_rate(I) x f_T x V_mean(I) x f_dod x f_age, where

- C_min = 3.35 Ah (spec 3.1 and 7.2: "Min 3,350mAh", 0.2C to 2.65 V at 23 C); nominal 12 x 3.35 x 3.60 = 144.7 Wh;
- f_rate from spec 7.8 (100 percent at 0.68 A, 97 at 3.4 A, 95 at 6.8 A, 92 at 8 A; linear between);
- f_T from spec 7.5 (40 percent at -10 C against 97 at 23 C and 40 C, all at 3.4 A: 0.412 at -10 C; 1.00 at
  20 C, inside the standard condition 23 plus or minus 3 C); between -10 and 20 C linear, INFERRED, and a lower
  bound at the kit's 0.5 to 1.0 A a cell;
- V_mean(I) from the Technical Report's printed energy and capacity of a typical cell: 12.62 Wh / 3.482 Ah =
  3.624 V at 0.2C and 11.94 Wh / 3.468 Ah = 3.443 V at 3.5 A, linear in current (a typical cell's voltage applied
  to the minimum capacity, labelled);
- f_dod: the graceful shutdown (`CONOPS.md` 4c, PROVISIONAL) ends the run at the lowest cell at 3.00 V under
  load for 10 s or at 5 percent RSOC, whichever comes first. From d4energy's reading of the Technical Report's
  room-temperature traces (0.7 A and 3.5 A, to 2.5 V) the cell reaches 3.00 V under load at 93.7 percent of its
  capacity at 0.7 A and 90.5 percent at 3.5 A, so the voltage line comes first at every current here (0.934 at
  PS-IDLE-SPEC's 0.99 A a cell). Behind it the gauge's cell under-voltage trip is 2.50 V
  (`pcb_pack_protection.yaml`) and board P's second level holds the FET off below 2.25 V (D-15): the protection
  window does not set the usable depth, the graceful line does;
- f_age = 0.80 (REQ-014 and SC-23: "aged" is 80 percent of the specification minimum, 8.04 Ah for the 3P block,
  the pack replaced below it) or 0.60 (spec 7.9, the sheet's floor after 500 cycles, the lower bracket).

| state | W at the pack | cells | A a cell | f_rate | f_T | V_mean | f_dod | **new Wh** | **aged 80 Wh** | aged 60 Wh | h new / aged 80 / aged 60 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PS-IDLE-SPEC | 42.8 | +20 C | 0.99 | 0.9966 | 1.000 | 3.604 | 0.934 | **134.8** | **107.9** | 80.9 | 3.15 / 2.52 / 1.89 |
| PS-IDLE-SPEC | 42.8 | 0 C | 0.99 | 0.9966 | 0.608 | 3.604 | 0.934 | 82.0 | 65.6 | 49.2 | 1.92 / 1.53 / 1.15 |
| PS-IDLE-SPEC | 42.8 | -10 C | 0.99 | 0.9966 | 0.412 | 3.604 | 0.934 | 55.6 | 44.5 | 33.4 | 1.30 / 1.04 / 0.78 |
| PS-RED2 | 31.4 | +20 C | 0.72 | 0.9995 | 1.000 | 3.622 | 0.937 | 136.3 | 109.1 | 81.8 | 4.34 / 3.48 / 2.61 |
| PS-SURV-R | 23.3 | +20 C | 0.54 | 1.0000 | 1.000 | 3.624 | 0.937 | 136.5 | 109.2 | 81.9 | 5.87 / 4.69 / 3.52 |
| PS-SURV | 21.7 | +20 C | 0.50 | 1.0000 | 1.000 | 3.624 | 0.937 | 136.5 | 109.2 | 81.9 | 6.28 / 5.03 / 3.77 |
| PS-NIGHT-RELAY (6a) | 15.7 | +20 C | 0.36 | 1.0000 | 1.000 | 3.624 | 0.937 | 136.5 | 109.2 | 81.9 | 8.69 / 6.95 / 5.22 |

(The full table with the 0 C and -10 C rows of every state is `energy_budget.out` section 2.) **Check against
the tree:** `POWER-THERMAL.md` section 6 reads 108.1 Wh aged for PS-IDLE-SPEC by a different route (rate factor,
a 0.05 Ohm sag, a 5 percent reserve, no voltage line); this chain reads 107.9 Wh. The two agree within 1 Wh, and
`CONOPS.md` 4a's aged runtimes (2.5 h, 3.5 h, 4.7 h, 5.0 h) are reproduced (2.52, 3.48, 4.69, 5.03).

**The cold end the mission allows.** The cells' own discharge window is -10 to 60 C at the cell surface (spec
3.12). D-02d's "use down to -20 C once warm" is an AMBIENT: the pack heater (RS PRO 245-556, 7.5 W at 12 V on
board A's regulated VHEAT, about 8.3 W at the pack through its buck) must hold the cells at or above -10 C
there, and that 8.3 W is added to the state's load in the cold (`CONOPS.md` 4a's heater overlay). At -10 C at
the cells the aged pack holds 44.5 Wh at PS-IDLE-SPEC (the maker's 40 percent at 3.4 A, a lower bound at the
kit's 1 A). The December case of section 5 takes the cells at +5 C (f_T 0.706), above the gauge's 0 C charge
window, so the charge is not held off on the mean day; a cold snap below 0 C at the cells holds every charge off.

## 3. Night duration at 52 N

No ephemeris is held in the tree, so the day length is computed (`energy_budget.py` section 3) from the solar
declination by Spencer's (1971) Fourier series (within about 0.05 degrees of the ephemeris) and the sunrise
equation cos(w0) = (sin h0 - sin lat sin dec) / (cos lat cos dec), with h0 = -0.833 degrees (refraction and the
sun's half-diameter, the usual sunrise and sunset) and h0 = -6 degrees (civil twilight), at 52.160 N. The day
length is accurate to about 2 to 4 minutes (the series and the weather's effect on refraction). "Sun down" is
24 h less sunrise-to-sunset; "dark" is 24 h less twilight-to-twilight (a panel gives almost nothing in twilight:
PVGIS's first and last lit hours in September carry 0 to 57 W/m2).

| month | declination on the 15th | mean day h | **mean sun-down h** | mean dark h |
|---|---|---|---|---|
| January | -21.3 | 8.30 | 15.70 | 14.39 |
| February | -13.0 | 9.88 | 14.12 | 12.94 |
| March | -2.4 | 11.83 | 12.17 | 11.04 |
| April | +9.5 | 13.87 | 10.13 | 8.92 |
| May | +18.7 | 15.67 | 8.33 | 6.91 |
| **June** | +23.3 | 16.67 | **7.33** | 5.71 |
| July | +21.7 | 16.24 | 7.76 | 6.23 |
| August | +14.3 | 14.68 | 9.32 | 8.04 |
| **September (design month)** | +3.3 | 12.72 | **11.28** | 10.13 |
| October | -8.2 | 10.70 | 13.30 | 12.16 |
| November | -18.3 | 8.85 | 15.15 | 13.89 |
| **December** | -23.2 | 7.82 | **16.18** | 14.82 |

**Shortest night 7.33 h** (June's mean; 7.23 h at the solstice), **design month 11.28 h** sun down (10.13 h
dark), **longest night 16.18 h** (December's mean; 16.28 h at the solstice). Cross-check: PVGIS's mean-day
profile has any irradiance from 04:00 to 19:59 UTC in June (16 h), 06:00 to 18:59 in September (13 h, the last
hour at 0.4 W/m2) and 08:00 to 15:59 in December (8 h, the last at 1.9), against 16.7, 12.7 and 7.8 h of sun
here; the hourly grid rounds outward by up to an hour each side. `CONOPS.md` M1's "about 7 hours at midsummer
and about 16 at midwinter (INFERRED from the latitude)" is confirmed.

## 4. Solar contribution

**Resource:** the PVGIS-SARAH2 monthly irradiation 2015 to 2020 on the optimally inclined plane (40 degrees,
south) at Leiden (`v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json`, pinned): the mean day is 5.49 kWh/m2 in
June, **4.01 in September** (SC-37's reference day) and **1.13 in December**. The day's shape is PVGIS's DRcalc
mean-day profile (2005 to 2020, filed on `fnd/d4energy` at `71be4943`, its 24 hourly values for the three months
copied into `energy_inputs.yaml` with that file's sha256), scaled by 1.006 to 1.008 to the pinned monthly mean.

**Panel model:** a 36-cell 12 V class crystalline panel as board E's generator describes the entry (about 22 V
open circuit at 25 C, 25 V cold, maximum-power point near 17.6 V; `gen_sch_e.py:436-474`); a 100 Wp panel of
that class is the size that fits the entry (its short-circuit current about 6.25 A, under F2's and J_SOLAR's
10 A; its peak at the node under the 100 W window on every mean day). Power = rating x G / 1000 x 0.9417, the
panel's own losses from PVGIS's PVcalc answer for the site (angle of incidence -2.99 percent, spectral +1.74,
temperature and low irradiance -4.57; the 14 percent system loss removed because the chain below counts the
kit's own stages). PVcalc's own September yield for 100 Wp at 14 percent loss, 0.32 kWh a day, is reproduced.
**Caveat, labelled:** that yield assumes maximum-power-point tracking; board E's stage holds the panel at a fixed
17.6 V (R8, R9), so a hot panel whose maximum-power voltage falls under 17.6 V gives less. No panel curve is held;
the low bracket takes 0.80.

**Window and chain:** at most 100 W into the stage (REQ-016, SC-36); above it the stage clips. Into the node:
the LT8705A stage 0.93 (the intent's declaration, `gen_sch_e.py:606`; the datasheet plots a 48 V design, not this
ratio) x board A's front end 0.93 (declared, `gen_sch_a.py:103`, not plotted at 20 V out) x the BQ25731 charger
0.98 (SLUSE66A Figure 8-4, d4energy's reading) = **0.848** (bracket 0.782 to 0.926).

| month | mean day kWh/m2 | panel Wp | panel Wh/day | peak W | hours clipped | **into the node Wh/day, 100 W window** | no window | low bracket |
|---|---|---|---|---|---|---|---|---|
| June | 5.49 | 100 | 517 | 61.5 | 0 | **438** | 438 | 343 |
| June | 5.49 | 200 | 1034 | 123 | 5 | 813 | 876 | 637 |
| June | 5.49 | 330 | 1706 | 203 | 8 | 956 | 1446 | 749 |
| **September** | 4.01 | **100** | 378 | 49.0 | 0 | **320** | 320 | 251 |
| September | 4.01 | 200 | 756 | 98.1 | 0 | 641 | 641 | 502 |
| September | 4.01 | 266 | 1006 | 130 | 6 | 751 | 852 | 588 |
| September | 4.01 | 330 | 1247 | 162 | 8 | 807 | 1057 | 632 |
| September | 4.01 | 400 | 1512 | 196 | 8 | 834 | 1282 | 654 |
| **December** | 1.13 | **100** | 106 | 21.4 | 0 | **90** | 90 | 70 |
| December | 1.13 | 330 | 350 | 70.7 | 0 | 297 | 297 | 233 |

**What a larger panel cannot do:** with the stage clipping at 100 W the most the window passes is 85 W at the
node for the lit hours, about 1100 Wh on a September day and 680 Wh on a December day with a panel large enough
to hold the clip all day; a 400 Wp panel reaches 834 Wh in September. The 100 W window alone therefore cannot
carry PS-IDLE-SPEC's 1027 Wh a day in any month. And a panel above about 150 Wp of the 12 V class exceeds F2's
and J_SOLAR's 10 A at its short circuit (about 6.25 A per 100 Wp), so it re-declares the entry (F2, J_SOLAR, D4,
PV_P's copper) even where the stage's 100 W is not reached: that is S-53's route (section 6e).

## 5. The balance and the conflict

M1 as written: 72 hours in PS-IDLE-SPEC from a full aged pack, the reference day (September), a 100 Wp panel in
the 100 W window, the loads at the model's PLAN figures, run hour by hour by `energy_budget.py` (section 5). Each
hour the solar path feeds the node first, the surplus charges the cells at the charger's limit (3.06 A for cycle
life, D-06's session item, tapering above 85 percent, at 0.95 energy efficiency, only inside the cells' 0 to 45 C
window) and the deficit comes from the cells; when the usable energy is gone the kit stops (the graceful
shutdown) and is restarted by the operator once the sun carries the load or the pack is half recharged (the kit
does not restart by itself, `CONOPS.md` 4c). "Load unserved" is the load the stopped kit did not serve over the run.

**5a. The design case in full** (`energy_budget.out` 5a lists all 72 hours): start 06:00 UTC, usable 107.9 Wh.
The pack gives 38.2 W at 06:00 (the panel 4.6 W at the node), 27.5 at 07:00, 16.5 at 08:00, 7.6 at 09:00, 2.7 at
10:00, 1.6 at 11:00, 1.2 at 12:00 and 4.2 at 13:00: 99.5 Wh by 14:00, when 8.3 Wh are left and the deficit is
10.3 W. **The kit stops at hour 8, at 14:00 on the first day, in daylight.** The panel never exceeds the load
(its peak at the node is 41.6 W against 42.8 W), so the pack drains from the first hour. Over the 72 hours the
kit runs 23 hours, restarted by the operator on each recharged pack, and leaves 1870 Wh of the 3082 Wh asked
unserved; it never sees a night running.

**One night by hand.** From sunset to sunrise in September the sun gives nothing for 11.28 h: the night asks
11.28 x 42.8 = 483 Wh of the pack (514 Wh over the 12 h of the profile's zero hours); the aged pack holds 107.9
Wh, so it carries 107.9 / 42.8 = 2.52 h of that night. The new pack holds 134.8 Wh, 3.15 h. Neither figure
depends on the panel. The mean day's whole solar input at the node, 320 Wh, is less than the night alone asks.

**5b. Every state, both months, both start hours** (`energy_budget.out` 5b):

| state | W | month | start | usable Wh | sun-down h | h sun below the load | Wh a night at that load | first stop h | h run of 72 | 72 h |
|---|---|---|---|---|---|---|---|---|---|---|
| PS-IDLE-SPEC | 42.8 | September | 06:00 | 107.9 | 11.3 | 24 | 1027 | 8 | 23 | NOT MET |
| PS-IDLE-SPEC | 42.8 | September | 18:00 | 107.9 | 11.3 | 24 | 1027 | 2 | 23 | NOT MET |
| PS-IDLE-SPEC | 42.8 | December | 06:00 | 76.2 | 16.2 | 24 | 1027 | 1 | 5 | NOT MET |
| PS-IDLE-SPEC | 42.8 | June | 06:00 | 107.9 | 7.3 | 19 | 813 | 12 | 32 | NOT MET |
| PS-RED2 | 31.4 | September | 06:00 | 109.1 | 11.3 | 18 | 565 | 13 | 33 | NOT MET |
| PS-RED2 | 31.4 | December | 06:00 | 77.0 | 16.2 | 24 | 753 | 2 | 8 | NOT MET |
| PS-SURV-R | 23.3 | September | 06:00 | 109.2 | 11.3 | 16 | 372 | 15 | 41 | NOT MET |
| PS-SURV-R | 23.3 | December | 06:00 | 77.1 | 16.2 | 24 | 559 | 3 | 12 | NOT MET |
| PS-SURV | 21.7 | September | 06:00 | 109.2 | 11.3 | 16 | 348 | 15 | 41 | NOT MET |
| PS-NIGHT-RELAY | 15.7 | September | 06:00 | 109.2 | 11.3 | 16 | 251 | 18 | 50 | NOT MET |
| PS-NIGHT-RELAY | 15.7 | June | 06:00 | 109.2 | 7.3 | 14 | 220 | 19 | 55 | NOT MET |
| PS-NIGHT-RELAY | 15.7 | December | 06:00 | 77.1 | 16.2 | 22 | 346 | 10 | 20 | NOT MET |

"h sun below the load" is longer than the astronomical night because a 100 Wp panel exceeds 42.8 W at the node
only above about 536 W/m2 (never on the September mean day) and exceeds 15.7 W only above 197 W/m2.

**The conflict, demonstrated.** On D-06's one 4S3P pack and REQ-016's 100 W window, M1 as written fails twice
over, and the first failure is enough on its own: (1) the night: a September night asks 483 to 514 Wh at 42.8 W
and the aged pack holds 108 Wh (a fifth of it; 135 Wh new, a quarter), so the kit stops 2.5 h into any night
whatever the panel; (2) the day: 72 hours ask 3082 Wh, a 100 Wp panel gives 320 Wh a day in September, and no
panel size inside the 100 W window gives more than about 830 Wh a day. The mission's first night is not reached
from a morning start and is 2.5 h long from an evening one.

**5c. Sensitivity: which input it depends on, and how far each would have to move alone** (the design case;
`energy_budget.out` 5c):

| input | value now | value that closes M1 alone | meaning |
|---|---|---|---|
| load at the pack | 42.8 W | **8.4 W** | the whole kit at 20 percent of PS-IDLE-SPEC, below the heat stage's 21.7 W and below this page's night state (15.7 W) |
| usable pack energy | 108 Wh aged | **2120 Wh** | 19.7 packs of the ruled size aged (15.7 new): with a 100 Wp panel the pack carries almost the whole 72 h |
| panel rating in the 100 W window | 100 Wp | **none passes** | the window's ceiling (about 830 Wh a day) is under the 1027 Wh the day asks |
| panel rating with no window at all | 100 Wp | **none passes** | the night binds whatever the day gives: 42.8 W for 13 h of sun below the load asks 556 Wh of a 108 Wh pack |
| the night the pack carries at 42.8 W | 2.52 h | | against 11.3 h of sun-down in September and 7.3 h in June |

No single input closes M1 as written; the night and the window bind independently. **REQ-072's verdict on these
figures is FAIL, unchanged.** The arithmetic on verified figures moves the aged usable energy by under 1 Wh
(107.9 against the record's 108.1) and confirms the record's 2.5 h; it does not move the verdict.

**5d. Combinations inside the approved constraints** (`energy_budget.out` 5d, 96 rows): with ONE pack no
combination of the night state (a), the 2.80 V line (b) and any panel and window (e) meets 72 hours in any of
the three months; the best one-pack case (the night state, 2.80 V, 330 Wp on a 300 W path, September) stops at
hour 18, in the first night, and leaves 241 Wh of the 72 hours' 1130 Wh unserved. With TWO packs (section 6d) the
night state at 2.80 V meets June on 100 Wp and September on 200 Wp or more; December is not met by any
combination (section 7).

## 6. Options within the approved constraints, with numbers and ranked

Every option keeps the Peli 1450 (the ruling of 7 September 2026), the cell (D-06) and the missions as written.
Costs are ESTIMATES with no quotation held; nothing is ordered. Ranked by how much of M1 each recovers per unit
of change; nothing is rejected silently.

**Rank 1, option (a), operating modes at night: PS-NIGHT-RELAY, 15.7 W.** The lowest-power state that still
meets M1's must-hold (a message typed on a handheld reaches a remote correspondent over at least one bearer; the
kit keeps running). Built on the heat stage after BANK-R1 (slot 3 alone, the one module that carries the owner's
D-02b example with the SOS path). ON, with its battery-side watts (`energy_budget.out` 6a lists each load):
CM5 slot 3 at the maker's typical 900 mA (4.95 W); its fan, PCIe switch and drive (2.52 W); the three supervisors
at 200 MHz (1.53 W, DS12110's 33 mA); the Ethernet switch in energy-detect (0.47 W, DS00002330D's low row, two of
its ports have no module); the LoRa module receiving (0.08 W); the RockBLOCK idle (0.07 W); board D with the SA868
receiving and the APRS beacons at the fixed-site rate of one a minute in ten (0.65 + 0.15 W); the GNSS (0.39 W);
the panel at NIGHT lighting (0.27 W); the hubs, bridges and logic rows (4.62 W, of which 3.37 W are D rows). OFF:
slots 1 and 2 with their fans, switches and drives; both WiFi link cards; the 5G module (its data lane is slot
2's); the monitor and HDMI 5 V; the SDR, the camera, the QMX and the Geiger (deferred by D-01); the E72 pair (not
a bearer of M1); the mixer fans (a shaded, cool night; on in the heat). **15.7 W PLAN, 13.1 W with the D rows at
the makers' figures** (S 10 loads, R 4, D 6, T 1). The aged pack carries it 7.0 h at +20 C (8.4 h at the sourced
figure) against September's 11.3 h of sun-down and 16 h of sun below the load: it does not carry a September
night alone, and it does carry a June night on two packs. What it changes: firmware and operator settings only
(the switch's energy-detect mode and the supervisors' clock are firmware items to confirm on the generated
boards); it needs BANK-R1 in board B's generator (`CONOPS.md` 4c). Cost: none in parts. Mission: at night the
monitor, the WiFi link, 5G and Zigbee are dark; the e-paper and the lamps carry the status; a message still
reaches its correspondent over Iridium or APRS. **It is a change to M1's energy basis (REQ-072 names
PS-IDLE-SPEC), presented for the owner's decision, not taken.**

**Rank 2, option (d), a second pack of the ruled size** (D-01 deferred it: "no location found"). It doubles every
usable figure of section 2 (216 Wh aged at PS-IDLE-SPEC, 218 at the night state). Where it was looked for and
what is free (`CASE-MARGINS.md`; A06's fit study on the committed board B underside, re-run unchanged by d4energy
on 28 September 2026): the **east pocket** (58 x 240 x 47.9) is taken by the ruled pack, and nothing larger fits
it with board P beside the cells (4S4P 18650: X spare -17.42; 4S3P 21700: -4.87). The **west pocket** (58 x 160 x
47.9, X -178 to -120, Y -40 to 120): A06 found no arrangement with board P BESIDE the cells (X spare -17.42), which
is D-01's "no location found". NOT tried by A06: the 4S3P block alone (56.65 x 133.5 x 38.1) with its board P on
top of the block or remote over a cell-tap harness: 133.5 fits the 160, 56.65 the 58 (1.35 spare, as the east),
and 38.1 plus a board P of about 8 mm assembled is about 46 against the 47.9 (about 2 mm, under the 3.32 the east
block keeps at the worst base). A candidate to CHECK with A06's script, not a finding; it displaces the west
cable drop zone (`CASE-MARGINS.md` section 3.4) and needs a second heater mat. The **lid**: the flat ceiling is
346 x 232 and the depth 44.45 at the worst; the QMX tray r2 takes X 83.2 to 171.0 and stands 33.95 below the
ceiling. A one-layer 4S3P block, two rows of six cells (113.3 x 133.5 x 19.55) or one row of twelve (223.6 x
66.25 x 19.55), on a 2 mm lid plate as the tray's, over the west third of the lid (X -173 to 83, where D-01's
deferred tablet bracket was to go) leaves 22.9 mm over the face parts, more than the tray's own room. About
0.65 kg in the lid; a lid harness across the hinge (the QMX's crossing is already open, S-95, EQ-31); the drop
and vibration hold-down (`TEST-PLAN.md` E1, E2) and the lid's strength are new items. A candidate to CHECK against
`CASE-MARGINS.md` M3 and M19 and the face parts' heights (T9), not a finding. Cost ESTIMATE: 12 cells about 50
EUR, a second board P about 30 EUR, strip, wrap and plate, under 150 EUR; a second pack build and protection
commissioning (`TEST-PLAN.md` section 5 twice). What it displaces: the tablet bracket (deferred) or the west drop
zone. **Reopens D-01's deferral: the owner's.**

**Rank 3, option (e), the panel and the window** (S-53's route, the session's). A 200 Wp panel gives 641 Wh a
day at the node in September and 180 in December without reaching the stage's 100 W on the mean day (peak 98 W;
it clips on a clear day), but its short-circuit current of about 12.5 A exceeds F2 and J_SOLAR at 10 A, so the
entry is re-declared (F2, J_SOLAR, D4, PV_P). A path re-rated to 300 W with a 330 Wp panel gives 807 / 297 Wh a
day (1057 in September with no window at all). What it cannot do: carry any night. Cost ESTIMATE: the stage's
inductor, FETs and sense resistor for three times the current, a 20 A fuse and connector, under 40 EUR on board
E; the panel 100 to 300 EUR per 100 Wp class. Mission: nothing removed; a bigger panel to carry and deploy.

**Rank 4, option (b), the usable depth of discharge.** The graceful line at 2.80 V under load instead of 3.00 V
(still above the gauge's 2.50 V trip, the maker's 2.50 V terminate line and its 2.65 V cut-off) gains 1.9 Wh aged
(107.9 to 109.7 Wh at PS-IDLE-SPEC; the 5 percent RSOC reserve then ends the run first at low currents): about
3 minutes more at 42.8 W, 7 at the night state. Cost: none (a gauge image and a bridge setting, the PROVISIONAL
threshold of `CONOPS.md` 4c). Cycle life below 3.0 V is the maker's question (its cycle test discharges to 2.65 V).

**Rank 5, option (c), cells in the east pocket.** Nothing larger than the ruled 4S3P 18650 fits with board P
beside the cells; a 4S2P 21700 (about 144 Wh with a representative 5 Ah cell, no 21700 sheet held) fits at the
same energy. Gain: none. Cost: none.

**Option (f), an external DC source on the 9 to 36 V entry, OPTIONAL and not the mission's basis.** The entry
guarantees 4.85 A and carries 6.15 A (`gen_sch_e.py:66-76`: the LM5069 U6 with R19 = 10 mOhm) through F1 10 A,
the LM74700 diode, the hot-swap FET and the choke into board A's front end (chain 0.911 to the node). At 12 V the
guaranteed 4.85 A is 58 W at the source and 53 W at the node, above every state M1 uses (42.8 W needs 3.9 A at
12 V, 2.0 A at 24 V). Energy a source must give per night (the sun-down hours): PS-IDLE-SPEC 530 Wh in September
(44 Ah at 12 V) and 760 Wh in December (63 Ah); the reduced mode 388 / 557 Wh; the heat stage 288 / 413 Wh; the
night state 194 / 279 Wh (16 / 23 Ah at 12 V). A vehicle's 70 Ah lead-acid battery gives about 35 Ah before half
discharge, a 100 Ah LiFePO4 about 80 Ah: PS-IDLE-SPEC takes a vehicle battery below half in one night, the night
state does not. No board change (EQ-13's route b). It changes M1's setting from "pack and solar", which is why it
is stated as optional and not taken as the basis, as the owner instructed on 28 September 2026.

## 7. The smallest justified changes, for the owner's decision

**M1 as written is not met by any combination of (a), (b) and (e) alone** (section 5d): on one aged pack the
night binds at every kit load above 8.4 W, and the lowest state that meets the must-hold reads 15.7 W. The
smallest change that meets M1's must-hold through the design month's night from a full aged pack, and the next
smallest, each with its consequences (`energy_budget.out` section 7; MET is the hour-by-hour run ending above
the graceful threshold with no stop; the ask and the hold beside it are the one-night arithmetic):

| change set | September | June | December | what it changes |
|---|---|---|---|---|
| **1. the night state (a) as M1's energy basis at night + the 2.80 V line (b) + a second 4S3P pack (d), 100 Wp, 100 W window** | NOT MET: the night asks 251 Wh (15.7 W x 16 h), two packs hold 221 | MET: 220 asked, 221 held | NOT MET: 345 asked, 156 held (cold cells) | M1's energy basis at night (REQ-072 restated for the owner, not by the session); D-01's deferral reopened; a pack location shown (6d); firmware for the night state and BANK-R1 |
| **2. as 1 with a 200 Wp panel, F2 and J_SOLAR re-rated for its 12.5 A** | **MET**: 220 asked, 221 held | MET: 188 asked, 221 held | NOT MET: 283 asked, 156 held | as 1, plus the entry's fuse and connector (S-53's smaller half); the stage's 100 W stays |
| 3. as 1 with the path re-rated to 300 W and a 330 Wp panel (e) | MET: 220 asked, 221 held | MET: 173 asked, 221 held | NOT MET: 283 asked, 156 held | as 2, plus the stage (S-53 in full) |
| 4. the heat stage PS-SURV-R at night (23.3 W) + (b) + second pack + re-rated path and 330 Wp | NOT MET: 326 asked, 221 held | NOT MET: 279 asked, 221 held | NOT MET: 419 asked, 156 held | keeps 5G off only; needs a third pack, which has no location |
| 5. the reduced mode PS-RED2 at night (31.4 W) + (b) + second pack + re-rated path and 330 Wp | NOT MET: 439 asked, 221 held | NOT MET: 377 asked, 221 held | NOT MET: 565 asked, 156 held | two modules and 5G at night; needs four packs |
| 6. PS-IDLE-SPEC as written + (b) + second pack + re-rated path and 330 Wp | NOT MET: 599 asked, 219 held | NOT MET: 556 asked, 219 held | NOT MET: 856 asked, 155 held | the mission's basis unchanged; needs six packs and a 300 W path, neither of which fits |

**The smallest justified change is set 2:** the night state as M1's energy basis between sunset and sunrise, a
second 4S3P pack (location to be shown: the lid's west third or the west pocket with board P on top, both to be
checked, 6d), the 2.80 V graceful line, and a 200 Wp panel with the solar entry's fuse and connector re-rated
(the stage's 100 W window unchanged). It meets M1's must-hold through the September and June nights from a full
aged pack and leaves REQ-072 as written FAIL until the owner restates its basis. **The next smallest is set 3**,
which adds the stage's re-rating and buys nothing more in September or June. **No set inside the case meets
December** on pack and solar: at +5 C two packs hold 156 Wh against a night's 283 Wh at the lowest state, and a
third and fourth pack have no location; December on pack and solar alone is a residual for the owner to accept or
to cover with option (f) (23 Ah at 12 V per night at the night state). **If the owner keeps M1's basis at
PS-IDLE-SPEC**, no change inside the case and the cell ruling meets a single night (set 6), and the honest
statement is that prototype 1 does not meet M1 on pack and solar alone (M-02's residual), with option (f) as the
way through a night.

**What must be verified at the bench before any of this is relied on** (section 1's T-P1 to T-P4): the power of
the night state and of PS-IDLE-SPEC at the pack terminals (the D rows carry 4.3 W of the night state's 15.7 W as
declarations; at the makers' figures they read about 1.7 W and the state 13.1 W); the WiFi card's idle and the
monitor's typical, which nobody
has published; the LT8705A stage's efficiency at 17.6 V in and 15.1 V out and the front end's at 20 V out (both
declared 0.93, neither plotted); the pack's delivered energy to the 3.00 V line new at +20 C and 0 C; and the
switch's energy-detect mode and the supervisors' 200 MHz clock in firmware.

**Draft apply scripts for the shared files (none executed):** `apply_records_readme_row.py` adds this folder's
row to `v2/docs/records/README.md`; `apply_req072_evidence_note.py` adds one evidence line to REQ-072 in
`v2/ecad/tools/pcb_requirements.yaml` citing this record, leaving its FAIL and its statement untouched.
`DECISION-PARAGRAPH.md` is the owner's sheet (at most 120 words).

## Sources

Samsung SDI INR18650-35E specification Ver. 1.1 (9 July 2015) and Technical Report (June 2015), distributors'
copies, `v2/vendor/battery/samsung-35e-orbtronic.pdf` and `samsung-35e-conrad.pdf`; PVGIS 5.2 (European Commission
JRC), MRcalc monthly 2015 to 2020 (pinned), DRcalc mean-day profile and PVcalc 100 Wp answer (on `fnd/d4energy`,
`v2/vendor/solar/sources.txt` there gives URLs, dates and sha256); `records/rv-pwr/pwr_budget.py` and `.out`
(PS-IDLE-SPEC's loads), `records/hc2/pwr_red2.out` (the reduced states); `records/d4energy/energy_data.yaml`
(d4energy, `9b43e274`: the makers' documents and pages for each load, the curve readings, the A06 re-run);
`v2/ecad/tools/gen_sch_e.py` (the solar stage and the vehicle entry), `gen_sch_a.py` (the front end);
`v2/ecad/tools/pcb_pack_protection.yaml` and `v2/docs/review-packets/battery/PROTECTION-ARCHITECTURE.md` (the
protection window); `v2/docs/CONOPS.md` sections 3, 4a, 4c, 5, 6 and 7; `v2/docs/feasibility/POWER-THERMAL.md`
sections 2 to 6; `v2/docs/CASE-MARGINS.md` sections 2, 3.2 and 3.4; `v2/docs/ASSEMBLY.md` steps 7, 10 and 11;
`v2/docs/handover/ENGINEERING-QUESTIONS.md` EQ-13; the registry's REQ-014, REQ-016, REQ-072, S-53, M-02, SC-21,
SC-23, SC-36, SC-37; owner rulings D-01, D-02b, D-02d, D-02e, D-06, D-15 and the case ruling of 7 September 2026.
Spencer, J. W. (1971), "Fourier series representation of the position of the sun", Search 2(5), 172: the
declination series (not held in the tree; a standard formula, its coefficients typed from the literature).
