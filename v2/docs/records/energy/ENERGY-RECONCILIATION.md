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

**Second issue (28 September 2026), after an independent AI review of the first (`fc8cf808`).** The review
reproduced sections 1 to 5 and the conflict with its own code and found three blocking items, corrected here: the
west pocket's second pack was written as nearly fitting where A06's own tool says its board P does not fit (B1,
section 6d, now judged with `packfit_west.py`); set 2 said the stage's 100 W window was unchanged where nothing in
the stage holds it to 100 W (B2, section 6e, two routes); and the owner's paragraph presented set 2 as meeting the
mission (B3, section 7 and `DECISION-PARAGRAPH.md`). Its minor items are answered in place: the night state's panel
row at its declaration's share and a low-to-high bound on the tree's model, with the relay's traffic added (m1,
m2, `night_bounds.py`; 16.20 W where the first issue had 15.70), the hour-by-hour margin and its conditions (m3),
the 2.80 V line named in the paragraph (m4), the window's ceiling (m5), the wording (m6 to m10) and the files that
exist only on `fnd/d4energy` with the merge order (m11, section 7's last paragraph).

**Third issue (28 September 2026), after the re-check of `7697c172`.** Two narrow corrections: four universal
sentences are replaced by their supported scope, with the bounds that establish or limit each (R1, sections 5d, 7
and the new 7b); and Route B's setting (ii) moves from 9.1 to 10 mOhm, because at 9.1 mOhm the stage reaches
100.9 W at 0.93 and 104.3 W at 0.90 with TRK_OUT at its reference-tolerance maximum of 15.56 V (R2, section 6e).
The fault-current margin is stated as 1.25 times the short-circuit current, with no standard for it held here.

**Section 8 (29 September 2026), the integrator's follow-up.** The second 4S3P block in the west pocket wired in
parallel with the first under the one board P (one 4S6P pack): board P's protection with its additions, the
harness, the energy re-run with one charge current, and the consequences; `energy_4s6p.py` and `.out`, and the
options sheet `DECISION-OPTIONS.md`. Sections 1 to 7 are unchanged by it.

**Correction (29 September 2026).** Sections 5d, 6a and 7, `energy_budget.out`'s labels and `DECISION-PARAGRAPH.md`
said the night state runs "at night"; every run holds it for all 72 hours, day included. Each place now says so, and
section 7c gives the sun-following schedule (full power only while the panel alone carries it) with its hours a day
per month and set. No figure of sections 1 to 7 changed.

**The inputs this rests on, pinned by sha256** (`energy_budget.py` refuses to run if any changed): the PVGIS
monthly irradiation file, the two Samsung INR18650-35E documents, the tree's power model outputs
(`records/rv-pwr/pwr_budget.out`, `records/hc2/pwr_red2.out`), board E's generator, this page's two helper
outputs (`night_bounds.out` and `packfit_west.out`, each written by a script that imports a committed tool unchanged
and pinned: `records/rv-pwr/pwr_budget.py` and A06's `pack_fit.py`), and `energy_inputs.yaml` itself. Stream d4energy's `energy_data.yaml` (branch `fnd/d4energy`, commit `9b43e274`) was read in full and
found sound; its load citations, its pack figures, its readings of the makers' curves and the PVGIS mean-day
profile it filed (commit `71be4943`) are reused and cited, not duplicated; those files exist only on
`fnd/d4energy` and land with or before this record (section 7, last paragraph). Its `energy_budget.py` (untracked
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

The night state of section 6a is computed on the tree's model itself (`night_bounds.py` imports `pwr_budget.py`
unchanged and reproduces PS-SURV-R's 12.78 / 23.27 / 46.94 W exactly): **LOW 11.02, PLAN 16.20, HIGH 39.67 W**;
the recount of its rows reads 16.63 W (S 10 loads, R 4, D 6, T 1), 13.77 W with the D rows at the makers' figures.

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
| PS-NIGHT-RELAY (6a) | 16.2 | +20 C | 0.37 | 1.0000 | 1.000 | 3.624 | 0.937 | 136.5 | 109.2 | 81.9 | 8.43 / 6.74 / 5.06 |

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
declination by Spencer's (1971) Fourier series (a fit for no particular year: for 15 September 2026 it gives +3.34
degrees where the Meeus low-precision method gives +2.91, the independent review's comparison, which moves that
night by about 0.04 h) and the sunrise
equation cos(w0) = (sin h0 - sin lat sin dec) / (cos lat cos dec), with h0 = -0.833 degrees (refraction and the
sun's half-diameter, the usual sunrise and sunset) and h0 = -6 degrees (civil twilight), at 52.160 N. The night
is accurate to within about 3 minutes from the declination and 2 to 4 minutes from the weather's effect on
refraction. "Sun down" is
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

**Window and chain:** at most 100 W into the stage (REQ-016, SC-36); the model clips there. That clip is a MODEL
assumption, conservative for the energy: as generated nothing in the stage holds it to 100 W (section 6e). Into the node:
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

**What a larger panel cannot do:** the window's own ceiling, a panel large enough to be clipped at 100 W in every
lit hour (20 kWp on this profile), is **1356 Wh a day at the node in June, 1024 in September and 624 in December**;
a 400 Wp panel reaches 834 Wh in September. Against PS-IDLE-SPEC's 1027 Wh a day the window's ceiling is above it
in June and under it in September and December; in every month the night binds first (section 5c). And a panel above about 150 Wp of the 12 V class exceeds F2's
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
11.28 x 42.8 = 483 Wh of the pack (471 Wh over the profile's 11 zero hours, 514 Wh with its twelfth, lit at only
0.42 W/m2); the aged pack holds 107.9
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
| PS-NIGHT-RELAY | 16.2 | September | 06:00 | 109.2 | 11.3 | 16 | 259 | 17 | 47 | NOT MET |
| PS-NIGHT-RELAY | 16.2 | June | 06:00 | 109.2 | 7.3 | 14 | 227 | 18 | 52 | NOT MET |
| PS-NIGHT-RELAY | 16.2 | December | 06:00 | 77.1 | 16.2 | 22 | 356 | 10 | 20 | NOT MET |

"h sun below the load" is longer than the astronomical night because a 100 Wp panel exceeds 42.8 W at the node
only above about 536 W/m2 (never on the September mean day) and exceeds 16.2 W only above 203 W/m2.

**The conflict, demonstrated.** On D-06's one 4S3P pack and REQ-016's 100 W window, M1 as written fails twice
over, and the first failure is enough on its own: (1) the night: a September night asks 483 to 514 Wh at 42.8 W
and the aged pack holds 108 Wh (a fifth of it; 135 Wh new, a quarter), so the kit stops 2.5 h into any night
whatever the panel; (2) the day: 72 hours ask 3082 Wh, a 100 Wp panel gives 320 Wh a day in September, and the
100 W window's own ceiling is 1024 Wh a day in September, under the 1027 Wh the day asks. The mission's first night is not reached
from a morning start and is 2.5 h long from an evening one.

**5c. Sensitivity: which input it depends on, and how far each would have to move alone** (the design case;
`energy_budget.out` 5c):

| input | value now | value that closes M1 alone | meaning |
|---|---|---|---|
| load at the pack | 42.8 W | **8.4 W** | the whole kit at 20 percent of PS-IDLE-SPEC, below the heat stage's 21.7 W and below this page's night state (16.2 W) |
| usable pack energy | 108 Wh aged | **2120 Wh** | 19.7 packs of the ruled size aged (15.7 new): with a 100 Wp panel the pack carries almost the whole 72 h |
| panel rating in the 100 W window | 100 Wp | **none passes** | the night binds first: a 20 kWp panel in the window still leaves 12 h below the load, asking 507 Wh of a 108 Wh pack; the ceiling, 1024 Wh a day, is also under the 1027 the day asks |
| panel rating with no window at all | 100 Wp | **none passes** | the night binds whatever the day gives: 42.8 W for 13 h of sun below the load asks 556 Wh of a 108 Wh pack |
| the night the pack carries at 42.8 W | 2.52 h | | against 11.3 h of sun-down in September and 7.3 h in June |

No single input closes M1 as written; the night and the window bind independently. **REQ-072's verdict on these
figures is FAIL, unchanged.** The arithmetic on verified figures moves the aged usable energy by under 1 Wh
(107.9 against the record's 108.1) and confirms the record's 2.5 h; it does not move the verdict.

**5d. Combinations inside the approved constraints** (`energy_budget.out` 5d, 96 rows; each state is held for
all 72 hours, day and night, as in every run of 5d and 7): with ONE pack and the night state at its PLAN of 16.20 W, no combination of the 2.80 V line (b) and the panels and windows examined (e)
meets 72 hours in any of the three months; the best one-pack case (2.80 V, 330 Wp on a 300 W path, September)
stops at hour 18, in the first night, and leaves 261 Wh of the 72 hours' 1166 Wh unserved. **That is the scope,
not an impossibility:** at the night state's LOW of 11.02 W one aged pack with the 2.80 V line and the cells at
+20 C carries June for 72 hours (200 Wp in the 100 W window: lowest point 3.2 Wh; 330 Wp on a 300 W path:
10.7 Wh; 400 Wp with no window: 12.8 Wh), though no September (section 7b). With TWO packs (section 6d) the night
state at 2.80 V meets June on 100 Wp and September on 200 Wp or more, under conditions (section 7); December
with the cells at +5 C is not met by any combination examined (section 7b gives the +20 C case).

## 6. Options within the approved constraints, with numbers and ranked

Every option keeps the Peli 1450 (the ruling of 7 September 2026), the cell (D-06) and the missions as written.
Costs are ESTIMATES with no quotation held; nothing is ordered. Ranked by how much of M1 each recovers per unit
of change; nothing is rejected silently. `energy_budget.out` section 6 prints every figure below.

**Rank 1, option (a), the night state PS-NIGHT-RELAY, 16.20 W PLAN (11.02 LOW, 39.67 HIGH).** It is named for the
night, but every run of 5d and 7 holds it for all 72 hours, day included; section 7c gives the schedule that runs
PS-IDLE-SPEC while the panel alone carries it and this state in every other hour. The
lowest-power state found that still meets M1's must-hold (a message typed on a handheld reaches a remote
correspondent over at least one bearer; the kit keeps running). It is the heat stage after BANK-R1 (slot 3 alone,
the one module that carries the owner's D-02b example with the SOS path) with six loads lowered or off, computed on
the tree's own model (`night_bounds.py`, `records/rv-pwr/pwr_budget.py` imported unchanged; the same script
reproduces PS-SURV-R's 12.78 / 23.27 / 46.94 W exactly). **ON:** CM5 slot 3 at the maker's typical 900 mA, its
fan, PCIe switch and drive; the three supervisors at 200 MHz (DS12110 Table 30, 33 mA); the Ethernet switch in
energy-detect (DS00002330D's low row; two of its ports have no module); the LoRa module receiving with the planning
duty's 9 percent airtime (0.3 W, the relay passing traffic); the RockBLOCK at one session in ten minutes (0.1 W);
board D with the SA868 receiving; the APRS beacons at the fixed-site rate, one beacon in ten minutes (0.125 W);
the GNSS; the panel at NIGHT lighting at its declaration's own logic share (0.82 W: a declaration, not the makers'
figure); the hubs, bridges and logic rows. **OFF in every hour the state runs, stated in full:** the monitor (messages show on the
e-paper and the lamps only); two of the three compute modules, so the kit has no running spare module while it runs (a
fault of slot 3 is met by the panel controller powering slot 1 again, `CONOPS.md` 4c, not by a module already
running); the kit-to-kit WiFi link (both cards); 5G (its data lane is slot 2's), leaving Iridium, APRS and the
LoRa mesh as the bearers while it runs; Zigbee and Thread (the E72 pair); the SDR, the camera, the QMX and the Geiger
(the last two deferred by D-01); the mixer fans (a shaded, cool night; on in the heat). The recount of its rows
reads 16.63 W (S 10 loads, R 4, D 6 carrying 4.9 W, T 1); with the D rows at the makers' figures 13.77 W. The
aged pack carries it 6.7 h at +20 C (9.9 h at LOW, 2.7 h at HIGH) against September's 11.3 h of sun-down and
16 h of sun below the load on 100 Wp: not a September night alone. What it changes: **M1's operating state, for all 72
hours as sets 1 to 3 run it (16 of 24 hours of a September day and 14 of June's under 7c's schedule with 200 Wp),
and so REQ-072's energy basis (PS-IDLE-SPEC for 72 hours): a reduction of the kit's capability in every hour the
state runs, presented for the owner's decision and not taken.** On the boards: firmware and operator settings only (the
switch's energy-detect mode and the supervisors' clock are firmware items to confirm), and BANK-R1 in board B's
generator (`CONOPS.md` 4c). Cost: none in parts.

**Rank 2, option (d), a second pack of the ruled size** (D-01 deferred it: "no location found"). It doubles every
usable figure of section 2 (216 Wh aged at PS-IDLE-SPEC, 218 at the night state). Where it was looked for, with
A06's own tool this time (`packfit_west.py` imports `v2/docs/records/adj/A06-pack-geometry/drafts/pack_fit.py`
unchanged, pinned, and uses its pockets, board B's underside zones, the heater mat's bases and its placement
search; output `packfit_west.out`):

- **east pocket** (58 x 240 x 47.9): taken by the ruled group (block, 2 mm, board P: 205.50 long). A second board
  P needs its 44.0 plus 2.0 in the 34.50 left in Y, or more than the 1.35 left in X: NO. Nothing larger than the
  ruled block fits with board P beside the cells (4S4P 18650: X spare -17.42; 4S3P 21700: -4.87).
- **west pocket** (58 x 160 x 47.9, X -178 to -120, Y -40 to 120): **the 4S3P block alone fits** (56.65 x 133.50
  x 38.10: X spare 1.35, Y spare 26.50, Z clear 5.20 at the nominal base and 3.99 at the worst, under C33 on board
  B's underside). **Board P does not fit with it:** on top of the block the Z clearance is -11.47 mm with its
  Keystone 3568 holder and blade (16.17 mm), -5.10 mm with only its JST XH (9.80 mm), and -1.70 mm even at the
  8 mm board the first issue of this page assumed (-12.68, -6.31, -2.91 at the worst base; the first issue left
  out the heater mat's base, board B's underside parts and board P's real heights, and its "about 2 mm clear" was
  wrong); at the block's end the group is 205.50 long against 160 (Y spare -45.50); at its side 75.42 wide against
  58 (X spare -17.42). So a west block needs its board P somewhere else, over a harness carrying the pack current
  and the cell taps, and **no place for it is found**: the tool models only the two pockets, the floor between them
  is the dock strip under board A's blind-mate gap of 13.4 mm (`CASE-MARGINS.md` section 3.1), against board P's
  19.8 mm with its holder, and no other volume was checked. The west pocket stays a CANDIDATE with board P unplaced.
- **the lid**: the flat ceiling is 346 x 232 and the depth 44.45 at the worst; the QMX tray r2 takes X 83.2 to
  171.0 and stands 33.95 below the ceiling. A one-layer 4S3P block, two rows of six cells (113.3 x 133.5 x 19.55)
  or one row of twelve (223.6 x 66.25 x 19.55), on a 2 mm lid plate as the tray's, over the lid's west 256 mm of
  its 346 (X -173 to 83, where D-01's deferred tablet bracket was to go) leaves 22.9 mm over the face parts; board
  P rides with the block in the lid. About 0.65 kg in the lid; a lid harness across the hinge (the QMX's crossing is
  already open, S-95, EQ-31); the drop and vibration hold-down (`TEST-PLAN.md` E1, E2) and the lid's strength are
  new items. A06's tool has no lid pocket and the face parts' heights under the lid are TBD (`CASE-MARGINS.md` T9),
  so it **cannot be checked in the tree today**: a CANDIDATE, not a finding.

Cost ESTIMATE: 12 cells about 50 EUR, a second board P about 30 EUR, strip, wrap and plate, under 150 EUR; a
second pack build and protection commissioning (`TEST-PLAN.md` section 5 twice). What it displaces: the tablet
bracket (deferred) or, in the west, the cable drop zone (`CASE-MARGINS.md` section 3.4) and a second heater mat.
**Reopens D-01's deferral: the owner's. No location is proven.**

**Rank 3, option (e), the panel and the stage** (S-53's route, the session's). A 200 Wp panel gives 641 Wh a day
at the node in September and 180 in December on the model's 100 W clip (its mean-day peak is 98.1 W); a 300 W
path with 330 Wp gives 807 / 297 Wh (1057 in September with no window at all). What it cannot do: carry any
night. **What bounds the stage as generated: nothing at 100 W.** Board E's U5 pin map (`gen_sch_e.py:482-484`)
ties pins 29 to 31 (EXTVCC, CSNOUT, CSPOUT on the 38-lead QFN) to TRK_OUT and pins 32 to 34 (CSNIN, CSPIN, VIN)
to PV_P, which is how the maker says to leave a current monitor "not in use" (LT8705A 8705af, PDF pages 11 and
12), so neither current loop can act; the tracker "delivers the panel's power" (`gen_sch_e.py:99-101`, 580-583)
and only board A's front end bounds it, at 126.9 W drawn (lines 104 to 107), 136 W into the stage at 0.93. A
200 Wp panel on a clear day, on pack and solar alone, can therefore put about 136 W into the stage: 7.8 A at
17.6 V and 8.4 A on TRK_OUT at 15.1 V. **The 100 W in this page's model is a model assumption, conservative for
the energy; it is not a property of the stage.** Two routes, both presented, and set 2 takes one of them:

- **Route A, the window restated.** REQ-016's "at most 100 W into the stage" becomes at most 136 W; PV_P and PV_IN
  go from 5.68 A typical and 6.25 A peak to 7.8 A and about 12.5 A (two 100 Wp panels' short circuit); TRK_OUT
  from 6.16 A at 15.1 V to 8.4 A (its 10.33 A declaration at the 9 V floor to 14.1 A, which VIN_RAW's 14.10 A
  already carries on board A); F2 and J_SOLAR at 1.25 times the short-circuit current or more, about 15.6 A for a
  200 Wp panel (the usual photovoltaic practice; no standard for it is held in the tree; a JST-VH is a 10 A part:
  another connector, pick TBD); L1's saturation current, the four FETs' dissipation and R5's range re-judged (the inductor valley
  limit is 69 mV over 5 mOhm, 13.8 A, `gen_sch_e.py:103`). D4 and the 25 V window are unchanged. Consequence: it
  restates a core requirement (REQ-016, session choice SC-36) and board E's declarations and ratings; more energy
  on clear days, none on the mean day. Cost ESTIMATE: under 40 EUR of parts on board E.
- **Route B, a designed limit that keeps REQ-016's 100 W.** The LT8705A's own output current loop (8705af PDF
  pages 4, 5, 11, 12, 19): a sense resistor RSENSE2 between the stage's output and TRK_OUT, CSPOUT (pin 31) on the
  stage side and CSNOUT (pin 30) on TRK_OUT, both untied from TRK_OUT; the loop regulates when IMON_OUT reaches
  1.208 V (1.187 to 1.229, page 4), with I(IMON_OUT) = gm x V(sense), gm 1.00 mmho (0.94 to 1.085 for the E and I
  grades over temperature, page 5; the fitted part is LT8705AEUHF; the sheet characterises gm at VCSPOUT 5.025 V
  only, so at 15.1 V it is a bench item, T-P3), and R17 (IMON_OUT to ground, 10k as generated) at 24.3k 1 percent.
  The worst case takes TRK_OUT at its highest as well: FBOUT 1.193 / 1.207 / 1.222 V (page 4) on R10 115k and R11
  10.0k at 1 percent (`gen_sch_e.py:576`) gives 15.56 V (15.09 V typical), and the stage at this record's low
  efficiency bracket, 0.90 (`energy_budget.out` section 6e):

  | RSENSE2 | limit, low / typical / high | into the stage at 15.1 V and 0.93 | worst, 15.56 V and 0.93 | worst, 15.56 V and 0.90 | 100 W at every worst |
  |---|---|---|---|---|---|
  | 8.0 mOhm, setting (i) | 5.52 / 6.21 / 6.86 A | 90 / 101 / 111 W | 114.8 W | 118.6 W | no |
  | 9.1 mOhm (the second issue's setting (ii)) | 4.85 / 5.46 / 6.03 A | 79 / 89 / 98 W | 100.9 W | 104.3 W | **no** |
  | **10.0 mOhm, setting (ii)** | 4.41 / 4.97 / 5.49 A | 72 / 81 / 89 W | 91.8 W | **94.9 W** | yes |

  The second issue's "9.1 mOhm holds REQ-016's 100 W at the sheet's worst" was false: it held only at TRK_OUT's
  nominal 15.1 V and the declared 0.93. The least RSENSE2 that holds 100 W at every worst is 9.49 mOhm, so
  **setting (ii) is 10 mOhm: at most 94.9 W into the stage in every worst case, 81 W typical, 72 W at its low
  end.** At that setting PV_P and PV_IN keep their 5.68 A typical (the stage draws at most 94.9 W, so at most
  5.39 A at 17.6 V or above); their peak (the panel's short-circuit current, a fault) rises from 6.25 to about
  12.5 A, so F2 and J_SOLAR are still re-rated for a 200 Wp panel (at 1.25 times, about 15.6 A, as route A). With
  the bus held lower by a vehicle the limit is a lower power, which the vehicle covers. Parts: one 2512 sense
  resistor, R17's value, two pins untied, under 2 EUR. Consequence: board E's schematic changes (a layer-5 item)
  and the host contract (FW-A16) must keep the constant-power front end inside what a current-limited stage gives,
  which is the case the design already has whenever a panel gives less than the front end draws
  (`gen_sch_e.py:99-103`). On the mean September day set 2 is MET under setting (ii) at its typical 81 W, its low
  72 W and its worst 94.9 W, with the same lowest point, 12.1 Wh (section 7).

**Rank 4, option (b), the usable depth of discharge.** The graceful line at 2.80 V under load instead of 3.00 V
(still above the gauge's 2.50 V trip, the maker's 2.50 V terminate line and its 2.65 V cut-off) gains 1.9 Wh aged
at PS-IDLE-SPEC (107.9 to 109.7 Wh; the 5 percent RSOC reserve then ends the run first at low currents): about
3 minutes more at 42.8 W, 7 at the night state. In set 2 it moves the lowest point from 9.1 to 12.1 Wh and the
cell threshold from 17.88 C to 17.21 C. Cost: none (a gauge image and a bridge setting). Cycle life below 3.0 V is
the maker's question (its cycle test discharges to 2.65 V).

**Rank 5, option (c), cells in the east pocket.** Nothing larger than the ruled 4S3P 18650 fits with board P
beside the cells; a 4S2P 21700 (about 144 Wh with a representative 5 Ah cell, no 21700 sheet held) fits at the
same energy. Gain: none. Cost: none.

**Option (f), an external DC source on the 9 to 36 V entry, OPTIONAL and not the mission's basis.** The entry
guarantees 4.85 A and carries 6.15 A (`gen_sch_e.py:66-76`: the LM5069 U6 with R19 = 10 mOhm) through F1 10 A,
the LM74700 diode, the hot-swap FET and the choke into board A's front end (chain 0.911 to the node). At 12 V the
guaranteed 4.85 A is 58 W at the source and 53 W at the node, above every state M1 uses (42.8 W needs 3.9 A at
12 V, 2.0 A at 24 V). Energy a source must give per night (the sun-down hours): PS-IDLE-SPEC 530 Wh in September
(44 Ah at 12 V) and 760 Wh in December (63 Ah); the reduced mode 388 / 557 Wh; the heat stage 288 / 413 Wh; the
night state 200 / 288 Wh (17 / 24 Ah at 12 V). A vehicle's 70 Ah lead-acid battery gives about 35 Ah before half
discharge, a 100 Ah LiFePO4 about 80 Ah: PS-IDLE-SPEC takes a vehicle battery below half in one night, the night
state does not. No board change (EQ-13's route b). It changes M1's setting from "pack and solar", which is why it
is stated as optional and not taken as the basis, as the owner instructed on 28 September 2026.

## 7. The smallest justified changes, for the owner's decision

**REQ-072 as written (PS-IDLE-SPEC for 72 hours on pack and solar) reads FAIL under every set below.** On one
aged pack no combination of (a), (b) and (e) meets it; in the design case (September, 100 Wp in the 100 W window,
the 3.00 V line) the night binds at every kit load above 8.4 W (5c), and that figure is the design case's only:
with 400 Wp, no window and the 2.80 V line one aged pack carries at most 9.24 W for 72 hours in September and
12.30 W in June (10.13 W in June with 100 Wp in the window), all far below PS-IDLE-SPEC's 42.8 W (section 7b). With
two packs PS-IDLE-SPEC is still NOT MET (set 6). The sets that meet M1's must-hold do so by **changing M1's
operating state to the night state of section 6a for all 72 hours, day and night** (16.20 W PLAN, 11.02 to 39.67 W;
every set below holds its state constant, and 7c gives the sun-following schedule), with the capability listed
there switched off in every one of those hours: a change presented for the owner's decision, not a fulfilment of REQ-072. From a full
aged pack, cells at +20 C in September and June and +5 C in December; MET is the hour-by-hour run ending above
the graceful threshold with no stop, and its **lowest point** is the least energy left in the packs over the 72
hours (the margin); "asks" and "holds" are the one-night arithmetic beside it (`energy_budget.out` section 7):

| change set (two 4S3P packs in every row) | September | June | December |
|---|---|---|---|
| 1. night state (a) for all 72 h + 2.80 V line (b) + second pack (d), 100 Wp | NOT MET, stops at hour 44 (asks 259 Wh, holds 221) | MET, lowest point 32.3 Wh | NOT MET, hour 15 (asks 356, holds 156) |
| **2. as 1 with a 200 Wp panel, and route A or B of 6e for the stage** | **MET, lowest point 12.1 Wh** (asks 227, holds 221) | MET, 51.7 Wh | NOT MET, hour 18 (asks 292, holds 156) |
| 3. as 1 with a 300 W path and a 330 Wp panel | MET, 23.4 Wh | MET, 67.8 Wh | NOT MET, hour 18 |
| 4. the heat stage PS-SURV-R for all 72 h (23.3 W) + (b) + 300 W path, 330 Wp | NOT MET, hour 21 (asks 326) | NOT MET, hour 22 | NOT MET, hour 15 |
| 5. the reduced mode PS-RED2 for all 72 h (31.4 W) + (b) + 300 W path, 330 Wp | NOT MET, hour 18 (asks 439) | NOT MET, hour 19 | NOT MET, hour 14 |
| 6. PS-IDLE-SPEC as written + (b) + 300 W path, 330 Wp | NOT MET, hour 16 (asks 599, holds 219) | NOT MET, hour 17 | NOT MET, hour 10 |

**Set 2's conditions** (September, start 06:00, the hour-by-hour run):

| case | result | lowest point | first stop |
|---|---|---|---|
| as stated: night state 16.20 W for all 72 h, cells +20 C, 2.80 V line, the mean September day | MET | 12.1 Wh | none |
| **cells at +15 C (the counter-case)** | **NOT MET** | 0 | **hour 23** |
| without the 2.80 V line (graceful at 3.00 V) | MET | 9.1 Wh | none |
| the night state at its LOW, 11.02 W | MET | 84.6 Wh | none |
| the night state at its HIGH, 39.67 W | NOT MET | 0 | hour 16 |
| route B setting (ii) at 10 mOhm, 81 W into the stage (typical) | MET | 12.1 Wh | none |
| route B setting (ii) at 10 mOhm, 72 W into the stage (its low end) | MET | 12.1 Wh | none |
| route B setting (ii) at 10 mOhm, 94.9 W into the stage (its worst high) | MET | 12.1 Wh | none |

**Set 2 meets September only with the cells at or above 17.21 C (17.88 C without the 2.80 V line) and the night
state at or below 17.06 W (0.86 W, 5.3 percent, above its PLAN), on the mean September day and planning loads.**
The independent review computed 15.61 C on the first issue's 15.70 W night state; the night state now carries
the panel row at its declaration's share (m1) and the relay's LoRa and Iridium traffic on the model's own
conversion, 16.20 W, and the threshold tightens accordingly. The cells' temperature through a September night in
this state is not computed in the tree (the +20 C is inferred) and decides the result.

**The smallest justified change is set 2**, stated with everything it changes: (1) M1's operating state
becomes the night state of 6a for all 72 hours as run (under 7c's sun-following schedule the same September result
with the state in 16 of 24 hours), with the monitor, 5G, the WiFi link, Zigbee and two of the three compute modules
off; (2) a second 4S3P pack, with no location proven (the lid block cannot be checked in the tree today; the west
pocket takes the block but not its board P, and no place for board P is found); (3) a 200 Wp panel, with either
route B (REQ-016's 100 W kept by a designed limit on the LT8705A's output current loop, about 2 EUR of parts and
board E's schematic changed) or route A (REQ-016 and board E's declarations restated to 136 W); in both routes F2,
J_SOLAR and the peak current of PV_P and PV_IN are re-rated for the panel's fault current; (4) the graceful line
at 2.80 V. The session's recommendation within set 2 is route B setting (ii) at 10 mOhm, because it keeps a core
requirement as written at every worst case and costs the least; set 2's September result is the same under it. **The next smallest is set 3**,
which re-rates the stage's path to 300 W and buys margin (23.4 Wh against 12.1) but no further month. **With
the cells at +5 C no set examined meets December** on pack and solar, not even the night state at its LOW of
11.02 W with two packs and any panel examined (section 7b): at +5 C two packs hold 156 Wh against a night's
292 Wh at the planned night state, and a third pack has no location found. With the cells at +20 C, set 3 does
meet December at the LOW of 11.02 W (lowest point 30.0 Wh; 31.4 Wh with 400 Wp and no window), and at the PLAN of
16.20 W it does not; the December night's cell temperature is not computed in the tree. December is a residual for
the owner to accept or to cover with option (f) (24 Ah at 12 V per night at the night state). **If the owner keeps
M1's basis at PS-IDLE-SPEC**, no change examined meets a single night: up to two packs (the second with no proven
location), the 2.80 V line and a panel with no window at all still stop in the first night even at PS-IDLE-SPEC's
model LOW of 33.1 W (hour 18 in September, 606 Wh unserved; hour 19 in June, 379 Wh; section 7b). A third or later
pack has no location FOUND, which is not the same as no location possible. The statement is then that prototype 1
does not meet M1 on pack and solar alone within the changes examined (M-02's residual), with option (f) as the way
through a night.

**7b. The scope of the universal statements** (`energy_budget.out` section 7b, computed by this page's own tool
at the tree's documented bounds; the independent review's phase 3 found the same figures). A statement of
impossibility is kept only where these bounds establish it; elsewhere the supported scope is stated. Established:
at PS-IDLE-SPEC's model LOW, two packs and a panel with no window fail the first night; with the cells at +5 C no
set examined meets December, even at the night state's LOW. Scoped: one pack meets no month at the night state's
PLAN (at its LOW it carries June, not September); the 8.4 W of 5c is the design case's; December at +20 C is met
by set 3 at the night state's LOW; a third pack has no location found.

**7c. The sun-following schedule** (`energy_budget.out` section 7c; added 29 September 2026). PS-IDLE-SPEC (42.8 W)
in every hour the panel alone carries it at the node on the month's mean day, the night state (16.20 W) in every
other hour; the 2.80 V line, aged, start 06:00, the record's charge rule (section 8: the charge current binds in none
of these runs). The tree holds a mean-day profile for June, September and December only. In every reduced hour the
monitor, 5G, the WiFi link, Zigbee and Thread, and two of the three compute modules are off (6a).

| set | month | hours a day at PS-IDLE-SPEC (UTC) | hours a day REDUCED | two packs (4S6P) | one pack |
|---|---|---|---|---|---|
| 1: 100 Wp, 100 W | September | 0 | 24 | NOT MET, hour 44 | NOT MET, hour 18 |
| 1: 100 Wp, 100 W | June | 5 (10:00 to 14:59) | 19 | NOT MET, hour 44 | NOT MET, hour 19 |
| 1: 100 Wp, 100 W | December (+5 C) | 0 | 24 | NOT MET, hour 15 | NOT MET, hour 10 |
| **2: 200 Wp, 100 W** | **September** | **8 (08:00 to 15:59)** | **16** | **MET, lowest 12.1 Wh** | NOT MET, hour 18 |
| 2: 200 Wp, 100 W | June | 10 (07:00 to 16:59) | 14 | MET, lowest 51.7 Wh | NOT MET, hour 19 |
| 2: 200 Wp, 100 W | December (+5 C) | 0 | 24 | NOT MET, hour 18 | NOT MET, hour 13 |
| 3: 330 Wp, 300 W | September | 10 (07:00 to 16:59) | 14 | MET, lowest 23.4 Wh | NOT MET, hour 18 |
| 3: 330 Wp, 300 W | June | 11 (07:00 to 17:59) | 13 | MET, lowest 67.8 Wh | NOT MET, hour 20 |
| 3: 330 Wp, 300 W | December (+5 C) | 4 (10:00 to 13:59) | 20 | NOT MET, hour 18 | NOT MET, hour 13 |

So with two packs sets 2 and 3 meet September and June on the mean day with the kit reduced 14 to 16 hours a day,
at the same lowest points as the constant runs; set 1 now fails June (its constant run met it); December is met by
no set; one pack meets nothing. **REQ-072 reads FAIL under this schedule**: the kit runs reduced in every hour the
table counts.

**What must be verified at the bench before any of this is relied on** (section 1's T-P1 to T-P4): the power of the
night state and of PS-IDLE-SPEC at the pack terminals (the D rows carry 4.9 W of the night state's recount as
declarations; at the makers' figures the state reads 13.77 W); the cells' temperature through a night in the night
state (set 2 needs 17.21 C or more); the WiFi card's idle and the monitor's typical, which nobody has published;
the LT8705A stage's efficiency at 17.6 V in and 15.1 V out and the front end's at 20 V out (both declared 0.93,
neither plotted), and under route B the output current limit's setting; the pack's delivered energy to the 3.00 V
line new at +20 C and 0 C; and the switch's energy-detect mode and the supervisors' 200 MHz clock in firmware.

**Draft apply scripts for the shared files (none executed):** `apply_records_readme_row.py` adds this folder's
row to `v2/docs/records/README.md`; `apply_req072_evidence_note.py` adds one evidence line to REQ-072 in
`v2/ecad/tools/pcb_requirements.yaml` citing this record, leaving its FAIL and its statement untouched.
`DECISION-PARAGRAPH.md` is the owner's sheet (at most 120 words). **Merge order (m11):** the files this page cites
from stream d4energy exist only on `fnd/d4energy` (its data file `v2/docs/records/d4energy/energy_data.yaml` and
readings at `9b43e274`; the PVGIS daily profile, the PVcalc answer and `v2/vendor/solar/sources.txt` at
`71be4943`); they land with or before this record. The daily profile's three months used here are copied into
`energy_inputs.yaml` with that file's sha256, which the independent review verified at `71be4943`. For the
integrator: diff this stream against `038037ed`, not `main` (the branch carries set 7's registry commits).

## 8. One 4S6P pack under one board P: the alternative the record did not examine

Added 29 September 2026 on the integrator's follow-up (the owner's instruction of 28 September stands: M1 and
REQ-072 preserved with their duration and conditions, external DC optional and never the overnight basis). Every
figure below is printed by `energy_4s6p.py` (beside this page; output `energy_4s6p.out`), which pins its inputs by
sha256, imports `energy_budget.py` unchanged for the discharge chain, the profiles and the hour-by-hour rule (its
own scheduled run reproduces `energy_budget.simulate` on four cases before anything is printed) and imports A06's
`pack_fit.py` unchanged for the pockets. **Prototype design, AI review: nothing built, ordered or measured.**

**The configuration.** Section 6d found that the second 4S3P block fits the west pocket alone (X spare 1.35, Y
spare 26.50, Z clear 5.20 nominal and 3.99 at the worst base, `packfit_west.out`) and that its own board P fits
nowhere found. This section examines the case section 6d did not: the west block wired **in parallel** with the east
block at every series node, under the **one** board P in the east pocket, so the kit carries one 4S6P pack of 24
cells, 289.4 Wh nominal (24 x 3.35 Ah x 3.60 V), with one gauge, one second level and one pair of FETs.

**The answer in brief.** (1) Board P can protect it with named additions (8a); nothing on board P's power path
changes rating, because the pack current is the kit's load. (2) The harness has a candidate route but no drawn one,
and the west block takes the west RF jumpers' drop zone, an open mechanical conflict (8b). (3) **M1 as written
(PS-IDLE-SPEC, 42.8 W, 72 h) is met in no month examined**, with any panel examined and from either start; the
largest constant load the aged 4S6P pack carries for 72 hours is 18.3 W in September and 22.6 W in June at best
(8c). With the night state, the 4S6P pack reproduces the record's sets 1 to 3 exactly: the energy result of section
7's two packs does not need a second board P. (4) The pack passes 160 Wh, weighs 600 g more in cells, halves the
cells' key-down heating rate per cell to a quarter, and needs a second heater mat that board A's heater branch cannot
carry as generated (8d). **REQ-072 reads FAIL, unchanged.**

### 8a. Electrical: what board P does with two parallel 3P blocks, and what must change

**What it already does.** `gen_sch_p.py` states that "nothing below depends on the parallel count except the per-cell
currents, which are the worst case at three". The BQ4050 senses and balances per series group (VC1 to VC4 through
R1 to R4; SLUSC67B pin table: each VCx is the sense input and the balance current path of its cell), and the
BQ7720700 second level U2 reads the same four nodes through its own filters. So a 4S6P pack is a 4S pack to both,
**provided every series node of the west block is joined to the same node of the east block**: the pack ends (B+
and B-) and the three middle nodes, five inter-pocket power conductors. Paralleled at the ends only, the west
block's three middle nodes would be sensed by nothing, balanced by nothing and protected by neither level; that is
not a configuration this study offers.

**The hazard the ONE gauge cannot see, and the addition that covers it.** If one of the three middle links opens
(a crimp, a solder joint, a chafe), the west group on that node sits in a series string that no tap reads: the
gauge's taps and U2's read the east group, the gauge's balancing reaches the west group only through that link
(at 9.75 mA, through RCB 200 ohm and two 100 ohm filters, SLUSC67B 6.10 and 8.2.2.3.1), and a west cell can then
be over-charged or over-discharged with every protection reading normal. **Taken by the session (authority SESSION,
reversible by removing the parts; reason: without it the west block has no protection of its own against a single
link failure):** a second BQ7720700DSSR, U2B, on the west block's OWN taps (a JST-XH 1x5 J_CELL2 on board P, five
sense wires from the west block), with its own 1 kohm and 0.1 uF filters, 300 ohm and 0.1 uF supply, its own Semitec
103AT-2 on a JST-PH 1x2 J_TS3 behind its own 270 ohm and 18 kohm network, its COUT into FUSE_G through its own
resistor beside R29 (the resistor OR that already joins U2's COUT and the gauge's FUSE), and its DOUT on a second
2N7002 holding DSG_G as Q5 does. The parts are U2's set as `gen_sch_p.py` codes it (C3681715, C25810, C22966,
C131337, C8545). U2B's open-wire detection covers its own five wires; each of them, a sense run of about half a
metre across the case, gets a fusible element at the cell end (part TBD). Whether all of it fits board P's 44 x 70
outline is not checked here: it is board P's four-layer regeneration's question (O-11).

**The fuses.** Board P's F1 (25 A MINI) sits after the point where the two strings join. A short inside the
inter-pocket harness is fed by BOTH blocks without passing F1, so each string needs its own fuse at its own B+
(the west block's at the block, the east block's where the harness lands), and each middle link is fused at both
ends. The string fuse is F1's part, a Littelfuse 297 25 A MINI: it holds 27.5 A for 360,000 s at least, so one
string can carry the whole 18 A peak if the other is open. The negative conductor is left unfused, as board P's
negative is (the high-side design, `gen_sch_p.py` PACK_N). The equalising links carry balancing and imbalance
current in service, but the whole string share (up to 8.8 A at the peak) if a series strip opens inside one block,
so they are 12 AWG like the leads. Inline holder parts: TBD (the held Littelfuse inline sheet is for the ATO size).

**Currents: the pack current is shared, the ratings do not rise.** The kit draws the same 10 A continuous and 18 A
for 60 s (PWR-F12) from 4S6P as from 4S3P, so F1 (25 A), F2 (SCF9550-30-05, 30 A), Q1 and Q2 (CSD17570Q5B), R10
(2 mOhm) and the pack leads keep their ratings and their findings (BAT-F20's body-diode loss at 10 A is unchanged).
Per cell the peak falls from 6.00 A to 3.00 A with an even share; the east string takes 51.1 to 52.9 percent (the
west string's harness, 3.6 to 5.7 mOhm, against a block's 46.7 to 80.0 mOhm), 3.17 A a cell at the peak. **The
gauge's current thresholds stay at the 3P values** (OCD1 20 A, OCC1 5.0 A; `parallel_min` stays 3), because a
string with its fuse open, or a west block not fitted, leaves a 4S3P pack behind the same gauge.

**The capacity words.** Design Capacity 20100 mAh at the sheet's minimum (20700 at its typical 3.45 Ah) and 28944
cWh, inside the data-flash maximum of 32767 for both (SLUUAQ3A 14.13.5.1 and 14.13.5.2); the CEDV gauging then
learns the pack at commissioning (a `TEST-PLAN.md` section 5 item, twice as long). Balancing moves 1 percent of a
group in 20.6 h instead of 10.3 h.

**The charge.** One charger (board A's BQ25731) and one gauge. FW-A02 writes at most 3.0 A (the 3P cycle-life
figure). At 6P the cells' cycle-life figure would allow 6.12 A, which is also what section 7's two-pack runs assumed;
one gauge refuses it: OCC1 at 5.0 A trips, and raising OCC1 above 6.12 A would let an isolated 3P block be charged
at 2.04 A a cell, over the sheet's 2.0 A maximum. **The session's setting (authority SESSION; reversible to 3.0 A):
ChargeCurrent at most 4.0 A**, the setting `pcb_pack_protection.yaml`'s own OCC test names as not tripping: 0.67 A a
cell at 6P, 1.33 A for an isolated block, OCC1 unchanged. From the graceful line to 95 percent: 4.0 h aged and 5.0 h
new at 4.0 A (5.4 and 6.7 h at 3.0 A), the model's charge rule. **The charge current binds in none of the runs**:
0 of the 32 runs of M1 as written change with 3.0, 4.0 or 6.12 A, and every night-state run gives the same verdict and stop hour at
all three; the pack either refills before evening or is emptied by the night whatever the rate. The pre-charge
stays 1.0 A: 0.048C of 4S6P, under the guideline's 0.1C to 0.5C window on the gentle side, 0.097C of an isolated block.

**The thermistors.** The gauge has four TS inputs and reads them as cell temperatures; one per series group becomes
**two per block** (TS1 and TS2 on the east block's two cells expected hottest, TS3 and TS4 on the west block's), and
the hot stop (`CONOPS.md` 4c, the hottest of TS1 to TS4) and OTD then read both blocks. The error budget's TBD term
"the sensed cell to the hottest cell" (`THERMAL-COORDINATION.md` section 3, `TEST-PLAN.md` P14) is judged per block
on half the sensors: a bench item. U2's NTC stays on the east block and U2B's goes on the west block.

**S-85 (BAT-001's three hardware gaps).** (1) W4DP-F1, the second level's 2.25 V under-voltage: unchanged, and it
applies to U2B as well. (2) BAT-F16, the second level's fixed 70 C: unchanged for each block; without U2B the west
block would have no firmware-independent over-temperature at all, so U2B is what keeps S-85 from growing. (3)
W4DP-F2: for the healthy 4S6P pack **F1 opens below the cells' limit** (from 33.75 A, where the east block's cells
reach their 8.0 A only at 45.4 A of pack current); with a block isolated the pack is 4S3P again and the gap returns
(24 A against 33.75 A). S-85 stays open with its three items and gains a fourth: the equalising links' integrity,
covered by U2B.

**What must change** (none of it done here; the shared files are the integrator's). Board P: U2B's set, J_CELL2,
J_TS3, the west string's lands and its fuse (a second Keystone 3568 or an inline holder), its outline and layout at
O-11. The pack harness: five 12 AWG power conductors (B-, the three middle nodes, B+), fused as above; five west
sense wires fused at the cell end; two gauge NTC leads and U2B's NTC pair. `pcb_pack_protection.yaml`: the topology,
`parallel_max` 6 with `parallel_min` 3, and the new devices. `HW-FW-CONTRACT.md` FW-A02: 4.0 A. The golden image:
the Design Capacity words. Board A's heater branch (8d). A pack-build step: the two blocks at the same voltage
before any link is joined (the joining current is the voltage difference over a few milliohms; the tolerance is TBD).

### 8b. Mechanical: the route between the pockets, the hold-down and the heater mat

**No route is drawn** (the floor plan is `CASE-MARGINS.md` section 6's, not drawn). The pockets are 240 mm apart in
X (west X -178 to -120, east X 120 to 178). **The candidate corridor** runs along the back wall at the floor,
outboard of board A (Y 80) and inboard of the flat floor's edge (Y 114.49), 34.49 mm wide, under board B (underside Z
47.90 less its parts; U51 hangs 1.60 at Y 68.3 to 85.8), shared with the RJ45 patch lead and the connector plate's
lead drops between X -57 and 57 (`CASE-MARGINS.md` 3.3). The record's 13.4 mm is the blind-mate gap above the dock
strip, which lies along the front wall (Y -113 to -45); the floor under the rest of board A is the RF jumpers' lane
to board E's clamps (3.4) and is not taken. Length 0.35 to 0.55 m (ESTIMATE: 240 between the pockets, up to 26.5 in
the west pocket and up to 205.5 along the east group to board P).

**The conductors.** 12 AWG, the gauge of the pack lead (`ASSEMBLY.md` section 3, 12 AWG silicone): 5.21 mOhm/m on
the annealed-copper constant (no wire standard is held), a loop of 3.6 to 5.7 mOhm. At the 18 A peak carried by the
west string alone (the east string open) the loop drops 66 to 103 mV and dissipates 1.2 to 1.9 W; the copper's
adiabatic rise over the 60 s is 8.9 K; at an even share 32 to 50 mV and 0.3 to 0.4 W; at PS-IDLE-SPEC 0.01 W, which
this section does not subtract from the energy.

**The conflict it creates: the west jumpers' drop zone.** "The drop zone, X -165 to the west wall at |Y| up to 98
from the floor to Z 54, is the jumpers'" (`CASE-MARGINS.md` 3.4, West, written because "no pack stands under the west
plugs"). The west pocket overlaps it over 13 mm of X, and a 56.65 mm block in a 58 mm pocket cannot leave it. The
seven west jumpers' ferrules end at Z 43.0, so their fall meets the block's top at Z 39.50 (40.71 at the worst), 3.5
mm (2.3) lower, or passes in the slot between the block and the wall, which the floor fillet closes below Z 15.32.
That is the east wall's M17 case (OPEN, FAILS AS ASSUMED there with five jumpers) moved to the west wall with seven.
**It is not solved here**: the west RF entry and its jumpers must be re-planned before the west block is taken
(the class of rows M17a to M17x, OPEN), a case-layout item.

**The hold-down and the mat.** S-27 is open for the east block too (`v2/cad/pack_4s.py` still draws the 4S4P block);
the west block takes the same hold-down once S-27 answers, and a strap over its top must keep off C33's 1812 site on
board B's underside (Y 62.77 to 69.38), the zone that sets the 5.20 and 3.99 mm. A second RS PRO 245-556 mat (50 x 150
mm) lies under it in the pocket's 26.50 mm of free Y; A06's bases already carry a mat (1.40 nominal, 2.61 at the
worst). Its supply is 8d.

### 8c. Energy: 4S6P on the record's model, with one charge current

**Usable energy** (the chain of section 2 at 24 cells): **273.0 Wh new and 218.4 Wh aged at PS-IDLE-SPEC, cells
+20 C** (221.5 with the 2.80 V line; 163.8 at the 60 percent bracket), 154.3 aged at +5 C, 90.1 at -10 C; the same at
the night state. The aged pack carries PS-IDLE-SPEC 5.10 h at +20 C and the night state 13.48 h.

**Hand calculation** (checked against the output): new = 24 x 3.35 Ah x f_rate 1.000 (0.50 A a cell, under the
sheet's 0.68 A point) x f_T 1.000 x V_mean 3.6244 V (clamped at the 0.2C point) x f_dod 0.937 (clamped at the 0.7 A
reading) = 80.40 x 3.6244 x 0.937 = 273.0 Wh; aged x 0.80 = 218.4 Wh. A September night at 42.8 W asks 11.28 h x 42.8 W
= 482.8 Wh, so the aged 4S6P pack carries 218.4 / 42.8 = 5.10 h of it: less than half the night, whatever the panel.

**M1 as written, PS-IDLE-SPEC 42.8 W for 72 hours** (`energy_4s6p.out` 3a; aged, 2.80 V line, ChargeCurrent 4.0 A):

| month (cells) | 100 Wp in the window | 200 Wp, 100 W (route B) | 330 Wp, 300 W path | 400 Wp, no window | largest 72 h load |
|---|---|---|---|---|---|
| September (+20 C) | NOT MET, stops h 12 | NOT MET, h 16 | NOT MET, h 16 | NOT MET, h 16, 1004 Wh unserved | 13.9 to 18.3 W |
| June (+20 C) | NOT MET, h 15 | NOT MET, h 17 | NOT MET, h 17 | NOT MET, h 17, 728 Wh unserved | 18.1 to 22.6 W |
| December (+5 C) | NOT MET, h 3 | NOT MET, h 4 | NOT MET, h 10 | NOT MET, h 11 | 5.3 to 9.2 W |
| December (+20 C, a bound) | NOT MET, h 6 | NOT MET, h 9 | NOT MET, h 12 | NOT MET, h 13 | 6.3 to 12.8 W |

From 18:00 every case stops at hour 3 to 5, in the first night. The design case at the 3.00 V line stops at hour 12. A
NEW 4S6P pack with 400 Wp and no window stops at hour 17 in September; PS-IDLE-SPEC's model LOW, 33.1 W, with 400 Wp
and no window in June stops at hour 19. **So M1 as written is met in no month, panel or start examined; the scope is
one or two 3P blocks, panels to 400 Wp with no window, the 2.80 V line, cells at +20 C (+5 C in December).**

**With the night state, as in the record's sets 1 to 3** (the night state held for all 72 hours; 3b): the 4S6P pack
gives section 7's two-pack results exactly, at 3.0, 4.0 and 6.12 A alike. Set 2 (200 Wp, the stage at 100 W, 2.80 V):
September MET, lowest point 12.1 Wh; June MET, 51.7 Wh; December NOT MET (stop h 18 at +5 C, h 22 at +20 C). Its
conditions are the record's: the cells at or above 17.21 C and the night state at or below 17.06 W; at +15 C it
stops at hour 23. Set 1 (100 Wp) meets June only; set 3 meets September and June; the night state's LOW with set 3
meets December only at +20 C (lowest 30.0 Wh); its HIGH, 39.67 W, meets nothing.

**What the sets hold, stated exactly** (3c; this section's reading of the record). Sections 5d and 7 run the night
state for all 72 hours, day included; the record called it "M1's operating mode at night" until the correction of
29 September 2026, which states it throughout and adds 7c for sets 1 to 3. Two schedules test that
wording on 4S6P: with **PS-IDLE-SPEC in every lit hour** of the mean day and the night state otherwise, no panel
examined meets any month (September with 400 Wp stops at hour 22); with **PS-IDLE-SPEC only in the hours the panel
alone carries it** at the node (sun-following), 200 Wp and above meet September (8 hours a day at PS-IDLE-SPEC with
200 Wp, 10 with 330 or 400 Wp) and June (10 to 12 hours), with the same lowest points as set 2 and set 3 (12.1 and
23.4 Wh in September), and December is not met. So the night state is the mission's state whenever the panel alone
does not carry PS-IDLE-SPEC, about 16 of 24 hours in September: the reduction of capability is larger than "at
night" says, and the owner's sheet must say so.

### 8d. Consequences

**Transport.** 289.4 Wh nominal in one pack. The tree holds no regulation text: the ADR could not be fetched on 27
September 2026 (UNECE refused this host, `records/hc3/blocked-questions-layer-3.md`), and no air or carrier rule is
filed; this study had no network. The 145 Wh pack was already above the 100 Wh the tree's EQ row names for special
provision 188 (`handover/ENGINEERING-QUESTIONS.md`, S-52's row, not a held text), and 289.4 Wh is above the 160 Wh
passenger figure the follow-up names, which is not verified here. What changes cannot be stated from the tree; S-52
carries it. A lever to put to S-52, not a finding: a disconnect in the inter-pocket harness would let the kit travel
with the west block apart, two 145 Wh units; whether that changes the classification is the regulation's question.

**Mass.** 12 more cells at 50 g maximum (spec 3.10): +600 g, 1200 g of cells in all; the harness, second mat, fuses,
U2B's parts, strip and wrap add an ESTIMATED under 150 g (12 AWG copper alone is 29.7 g a metre a conductor).

**Heat.** At the 18 A peak the cells' own heating falls from 1.37 to 3.24 K a minute (4S3P) to 0.34 to 0.81 (even
share) and 0.38 to 0.91 on the east block at its share, adiabatic on 50 g cells at 0.8 to 1.1 J/gK and 35 to 60 mOhm
(POWER-THERMAL 7.2's method): the 5 K between 55 and 60 C lasts 331 to 780 s instead of 93 to 218 s. The hot stop's
thresholds do not move; its sensors are halved per block (8a). The west block's top sits 3.99 to 5.20 mm under board B's
underside parts at C33 (the IOCTRL logic over part of it), a heat environment no tool in the tree computes.

**The heater.** Two mats (7.5 W each at 12 V) draw 1.25 A on VHEAT and 1.16 A (14.4 V) to 1.39 A (12.0 V) on
VHEAT_IN, above the 0.98 A that U22's 909 ohm ILM gives (TPS2596 equation 7, as `gen_sch_a.py` quotes it); a 2.0 A
limit needs 449 ohm, the 453R the same comment lists, and VHEAT's and VHEAT_IN's declarations follow (board A, a
layer-5 item; L12's 2.9 A and U33's 3 A carry 1.25 A). At full duty, an upper bound (the duty is the loss, which no
held figure gives), the second mat costs 135 Wh a December night at the pack, where the second block adds 77 Wh aged
at the night state with its cells at +5 C and 45 Wh at -10 C: **in deep cold the second mat can take more than the
second block gives.** M1's month rows do not run the heater (cells at +5 C and +20 C).

**Cost, ESTIMATE** (no quotation held but the JLC figures `gen_sch_p.py` quotes): 12 cells about 50 EUR; U2B's set
under 10 EUR; string and link fuses with holders under 25 EUR; the harness under 20 EUR; the second mat (no price
held) under 30 EUR; wrap, strip and hold-down under 15 EUR: under 150 EUR of parts, plus a second block build and
the protection commissioning. Nothing is ordered.

**For the owner** (`DECISION-OPTIONS.md`, at most 250 words): the second block reopens D-01's deferral and the night
state changes M1's operating state, both the owner's; REQ-072 as written reads FAIL under every option.

## Sources

Samsung SDI INR18650-35E specification Ver. 1.1 (9 July 2015) and Technical Report (June 2015), distributors'
copies, `v2/vendor/battery/samsung-35e-orbtronic.pdf` and `samsung-35e-conrad.pdf`; PVGIS 5.2 (European Commission
JRC), MRcalc monthly 2015 to 2020 (pinned), DRcalc mean-day profile and PVcalc 100 Wp answer (on `fnd/d4energy`,
`v2/vendor/solar/sources.txt` there gives URLs, dates and sha256); `records/rv-pwr/pwr_budget.py` and `.out`
(PS-IDLE-SPEC's loads), `records/hc2/pwr_red2.out` (the reduced states); `records/d4energy/energy_data.yaml`
(d4energy, `9b43e274`: the makers' documents and pages for each load, the curve readings, the A06 re-run);
`v2/ecad/tools/gen_sch_e.py` (the solar stage, U5's pin map and the vehicle entry), `gen_sch_a.py` (the front end);
Linear Technology LT8705A datasheet 8705af, `v2/vendor/power/lt8705a.pdf` (PDF pages 4, 5, 11, 12 and 19: the
IMON regulation voltage, the output monitor's gm, the current-sense pins and the output current loop);
`v2/docs/records/adj/A06-pack-geometry/drafts/pack_fit.py` (A06, imported unchanged by `packfit_west.py`);
`v2/ecad/tools/pcb_pack_protection.yaml` and `v2/docs/review-packets/battery/PROTECTION-ARCHITECTURE.md` (the
protection window); `v2/docs/CONOPS.md` sections 3, 4a, 4c, 5, 6 and 7; `v2/docs/feasibility/POWER-THERMAL.md`
sections 2 to 6; `v2/docs/CASE-MARGINS.md` sections 2, 3.2 and 3.4; `v2/docs/ASSEMBLY.md` steps 7, 10 and 11;
`v2/docs/handover/ENGINEERING-QUESTIONS.md` EQ-13; the registry's REQ-014, REQ-016, REQ-072, S-53, M-02, SC-21,
SC-23, SC-36, SC-37; owner rulings D-01, D-02b, D-02d, D-02e, D-06, D-15 and the case ruling of 7 September 2026.
Section 8 adds: TI BQ4050 datasheet SLUSC67B (6.10 RCB; 8.2.2.3.1) and technical reference manual SLUUAQ3A
(14.13.5), `v2/vendor/battery/`; `gen_sch_p.py`, `pcb_pack_protection.yaml`, `gen_sch_a.py` (the heater branch),
`panel1450.py` (the outlines), `HW-FW-CONTRACT.md` FW-A02, the RS PRO 245-556 sheet, `CASE-MARGINS.md` 2.1, 3.3 and 3.4,
`records/hc3/blocked-questions-layer-3.md`.
Spencer, J. W. (1971), "Fourier series representation of the position of the sun", Search 2(5), 172: the
declination series (not held in the tree; a standard formula, its coefficients typed from the literature).
