# ENERGY-BASIS: the energy basis of layer 3's decisions L3-OD1, L3-OD2 and L3-OD4 (stream l3plane, MESHSAT-1357)

30 September 2026, branch `fnd/l3plane` (from `fnd/int16` at `d2084904`). **Evidence for the owner's decisions, not a
decision: no requirement, record or decision is changed (`pcb_requirements.yaml` is untouched), and every operating
condition below is PROPOSED, for the owner's approval, not accepted.** Prototype design: nothing is built, bought, powered or
measured. AI arithmetic on the record's model, not a qualified review. Every figure carries its basis: **MAKER** (a maker's
document and page, read by the script from its text layer), **NETLIST** (board A's committed netlist), **MODELED** (the
energy model's arithmetic) or **INFERRED** (a figure no document states; the reason is given). The figures are printed by
`vbus20_range.py` into `vbus20_range.out` and by `energy_basis.py` into `energy_basis.out` (sections named); this page
transcribes them.

It answers the owner's review of the decision table: the charge bus voltage as an engineering input established from the
design, an independent check of how voltage, current limits and losses move the energy result, the word "adverse" defined
and replaced, the weather stated exactly, the displaced lid function accounted for, and every narrower condition proposed
explicitly.

## 1. The corrected comparison table (decisions L3-OD1, L3-OD2 and L3-OD4)

All energy figures are MODELED, on SC-37's reference day (section 4), on the 40 degree south plane unless a band is named,
as the lowest store of both packs over 72 hours in Wh; "NOT MET" gives the energy left unserved. TYP and WAB are the two
array builds on the same mean day (section 4b). The cases NOM, WE, WE60, WA and GEN are defined exactly in section 4c.

| | 4S9P lid: both lid functions kept (4S15P in all) | 4S14P lid: the tablet bracket out (4S20P in all) | 4S15P lid: the QMX HF set out (4S21P in all) |
|---|---|---|---|
| **The displaced lid function** (section 6) | none displaced | **the tablet bracket's function leaves the kit unless a location is found**: the records establish no place for it in the kit; the tablet itself can be used outside the case over the kit's WiFi and USB-C outlet | **the HF function leaves the kit unless a location is found**: the records establish that the base has no volume for the QMX and that outside the case it would need a back-wall lead the ruled connector plate does not carry |
| **NOM**, nominal inputs (`energy_basis.out` 4): TYP / WAB | NOT MET, 165.7 / 172.6 Wh unserved | 93.7 / 75.7 Wh | 125.2 / 106.8 Wh |
| **WE**, the established worst electrical inputs: TYP / WAB | NOT MET, 166.2 / 173.0 Wh unserved | 51.1 Wh / **NOT MET, 3.9 Wh unserved** | 81.7 / 26.7 Wh |
| WE60, WE with U3 at the 6.0 A bracket: TYP / WAB | NOT MET, 166.2 / 173.0 Wh unserved | 30.9 Wh / NOT MET, 24.1 Wh unserved | 61.4 / 6.4 Wh |
| WA, every bracket unfavourable at once: TYP / WAB | NOT MET, 190.9 / 245.4 Wh unserved | NOT MET, 70.3 / 120.5 Wh unserved | NOT MET, 40.0 / 91.8 Wh unserved |
| GEN, board A **as generated** (R11 10 mOhm): TYP / WAB | NOT MET, 494.7 / 522.4 Wh unserved | NOT MET, 357.5 / 383.8 Wh unserved | NOT MET, 326.6 / 352.8 Wh unserved |
| **Deployment band at WE** (both builds meet, every store above 4.2 Wh; INFERRED from the grid; `energy_basis.out` 5) | none | **none**: no grid plane meets with the worst array build | **slope 30 to 50 degrees, facing between south and 15 degrees west** (6 grid points; least store 12.6 Wh at 50/+15, WAB); at WE60 only 40/0 remains (6.4 Wh) |
| Band at NOM, for reference | none | slope 20 to 50, 15 E to 30 W (least 18.3 Wh at 50/+30, WAB); within 15 of south 20 to 50 | slope 20 to 60, 15 E to 30 W (least 6.6 Wh at 60/+30, WAB); within 15 of south 10 to 60 |
| Laid flat (slope 0) | not met | NOM: neither build meets; WE: neither | NOM: the TYP build only; WE: neither |
| INFORMATIVE: September's 72 hour windows 2005 to 2020 at 40/0 that meet M1 (section 5): NOM TYP / WE TYP / WE WAB | not run (fails on the mean day) | 24.0 / 19.6 / 14.8 % of 864 | 27.2 / 23.0 / 18.2 % of 864 |

**What the table says, on this model:**

- **No option keeps both approved lid functions and meets M1.** The 4S9P lid does not meet M1 in any case, including NOM.
- **The tablet-out lid (4S14P) does not meet M1 at the established worst electrical inputs** once the array's worst build is
  taken: NOT MET by 3.9 Wh on the reference plane itself, so no deployment band exists for it at WE. It meets at nominal
  inputs (93.7 and 75.7 Wh).
- **The QMX-out lid (4S15P) meets at WE** on the reference plane (81.7 and 26.7 Wh) and over a band of 30 to 50 degrees
  facing south to 15 degrees west. With U3 at its 6.0 A bracket the band shrinks to the 40 degree south plane alone, 6.4 Wh
  above empty. With every bracket unfavourable at once (WA) nothing meets.
- **Every Option A(i) result rests on board A's entry as drafted, not as generated.** As generated (R11 10 mOhm) the front
  end limits at 4.30 A, under U3's setting, and no option meets M1 (GEN).
- **These runs establish M1 on one mean day only.** On September's actual weather (INFORMATIVE), M1 is met in about one
  72 hour window in four to seven at 40/0. Whether M1 must hold in worse weather is the owner's call; nothing here proposes it.

**Against the table on `fnd/l3r2` (L3-OD1, L3-OD2, L3-OD4).** That table took the bus at SC-76's 19.08 V with U3 and U3B at
their central efficiencies (case SC76 here: QMX-out 95.9 and 40.1 Wh, band 20 to 50 degrees facing south to 15 degrees west,
at least 9.1 Wh; tablet-out 65.1 and 9.4 Wh). The established worst case (WE) takes the bus at 19.146 V (section 2, a little
above SC-76's figure) but U3 and U3B at the lower ends of their brackets, which the owner asked to be included: the
QMX-out lid's figures fall to 81.7 and 26.7 Wh and its band to 30 to 50 degrees, and the tablet-out lid no longer meets with
the worst array build. The published figures (93.7 and 125.2 Wh typical, case M207) rest on the model's 20.7 V.

### 1a. What is PROPOSED for the owner's approval (none of it is accepted, and nothing here applies it)

1. **The basis of M1's energy claim:** case WE (the bus at the design's established minimum, U3 at its 6.1 A minimum, U3 and
   U3B at the lower ends of their efficiency brackets) with both array builds, on SC-37's reference day. This replaces SC-76's
   19.08 V session choice with an established input (section 2).
2. **For the QMX-out lid (4S15P), M1's deployment condition:** the array's plane at a slope of 30 to 50 degrees, facing
   between south and 15 degrees west of south (the grid's points; section 7 states what the grid does not show). This is
   narrower than the 20 to 50 degrees on `fnd/l3r2`. At the 6.0 A bracket only 40 degrees due south remains.
3. **For the tablet-out lid (4S14P):** no deployment condition can be proposed at WE. On the model it needs more power into
   U3 at the bus minimum or a different operating condition. These changes are not analysed here and would each be the
   owner's to approve (section 3 gives the knee: about 8 to 22 Wh of margin per 2 W into U3 between 110 and 122 W).
4. **The displaced function:** either option removes an approved function from the kit unless a location is found (section
   6). Keeping both (4S9P) does not carry M1. The owner's authorisation is needed for whichever function leaves.

## 2. VBUS20 at U3's input, established from the design (`vbus20_range.out`)

**The circuit (NETLIST, board A `pcb-a-power.net`, sha256/16 `6c40250c47195ebb`).** U2 (LM5176) regulates VBUS20 through
R6 240k 1 % (VBUS20 to FE_FB) over R7 10k 1 % (FE_FB to GND) into its pin 11. R11, the front end's shunt, runs from FE_OUT
to VBUS20, so its drop is **inside** the loop and does not lower VBUS20. R16 (RAC) runs from VBUS20 to CH_ACN, and U3's pin 1
is on VBUS20. The netlist carries no purchase code for R6 or R7.

**The parts.** lcsc_fill.py's map, applied as that script applies it, gives R6 C137765 and R7 C25804, as the released A24
BOM does. **R6 is YAGEO RC0603FR-07240KL.** YAGEO RC_L V.12 p.2 decodes it as 1 %, standard power. Its p.5 Table 2 gives
RC0603 at 1 % and 10 Ohm to 10 MOhm **100 ppm/K**, from +25 C (p.8). The sheet is now filed as
`v2/vendor/passives/yageo-rc-l-series-v12.pdf`. **R7 is UNI-ROYAL 0603WAF1002T5E.** UNI-ROYAL V.3 p.2 decodes it as 1/10 W,
1 %. Its p.6 gives 0603 above 10 Ohm **100 ppm/K**, from +25 C. That sheet is held back and was read here from its pinned
copy, not committed.

**The terms at the regulation point** (the envelope's temperature, against the nominal 20.000 V):

| Term | Low / high, V | Basis | Kind |
|---|---|---|---|
| VREF 0.788 / 0.800 / 0.812 V at FB = COMP, over TJ -40 to 125 C | -0.300 / +0.300 | MAKER SNVSAI1D 6.5 p.6 | part to part AND temperature: TI prints one band and no reference curve (pp.9 to 12 read), so a unit may sit at either end at any temperature |
| R6 and R7 at 1 %, in opposite directions | -0.380 / +0.388 | MAKER YAGEO p.2, UNI-ROYAL p.2; NETLIST values | part to part: a fixed offset per unit |
| R6 and R7 at 100 ppm/K each over 45.0 K from +25 C, opposite directions | -0.172 / +0.174 | MAKER YAGEO p.5, UNI-ROYAL p.6; the directions INFERRED (the makers give no tracking figure, and the parts are two makers') | temperature |
| IBIAS(FB) at most 25 nA through R6, either direction | -0.006 / +0.006 | MAKER SNVSAI1D p.6 (maximum; direction not stated) | part to part and temperature |
| the error amplifier's finite DC gain, COMP anywhere up to VCC's 7.88 V | -0.008 / +0.008 | INFERRED: gm 1.31 mS x ROUT 20 MOhm = 26200, TI's TYPICAL figures (p.6), no minimum printed; TI specifies no load or line regulation | load and line |
| the copper from R6's tap to R16's pin, at U3's input current | not established | board A has no layout of this netlist (its routed file was last committed on 15 September, A32) | load: 6.3 mV per mOhm at 6.3 A |

**The range (min, nominal, max) at the regulation point** (all terms together, tolerance and TCR in opposite directions):

| Condition (the divider's temperature) | Min | Nominal | Max |
|---|---|---|---|
| the envelope, any in-use condition: -20.0 to +62.1 C (the in-use ambient minimum, the divider at the air before any warm-up; the worst inside air in use, lid closed, `pcb_envelope.yaml`; both INFERRED there) | **19.146 V** | **20.000 V** | **20.887 V** |
| M1 on the reference day: +26.4 to +53.9 C (the day's air 13.23 to 18.33 C plus PS-IDLE-SPEC's lid-open inside-air rise, 13.16 to 35.58 K, both bounds, INFERRED) | 19.205 V | 20.000 V | 20.823 V |
| the printed figures alone (VREF and 1 %) | 19.326 V | 20.000 V | 20.694 V |
| stream s120's band (65 K of TCR assumed, no amplifier term) | 19.080 V | | 20.960 V |

**The kinds.** Part to part (a fixed offset per unit): the resistors' 1 % (about 1.9 %) and VREF's band (1.5 %) as far as TI
separates it, which it does not. Temperature: the resistors' TCR (at most 0.9 % over the envelope). Load and line: the
amplifier's finite gain (under 0.1 %) and the copper to R16 (not established). The energy basis takes the envelope's
minimum, **19.146 V**, which covers every in-use temperature; the reference day's own minimum, 19.205 V, is 59 mV higher.
The model's 20.7 V sits near the top of the band. SC-76's 19.08 V is below any combination the makers' figures allow, but
the copper term and the resistors' long-term drift are not in the figure.

**Under load (the decisive point for the design as generated).** U3's IIN_HOST is 6.2 A nominal and 6.3 A maximum. **As
generated, R11 is 10 mOhm and the front end's own constant-current loop holds 4.30 / 5.00 / 5.70 A** (VSNS 43 / 50 / 57 mV,
SNVSAI1D p.7, over R11). That is below U3's setting, so at U3's full input current **the bus is not in voltage regulation
as generated**: the front end limits its current and VBUS20 falls below the band. Every Option A(i) figure uses the
**drafted** re-rate R11 6.2 mOhm (a1elec TOPOLOGY.md section 7; not in the generator). It limits at 6.94 / 8.06 / 9.19 A,
above U3's 6.3 A maximum, so the bus stays in regulation and the range above applies at the regulation point. Not included:
the resistors' long-term drift. The makers' endurance limits, YAGEO p.8 and UNI-ROYAL p.7, are test limits of
+-(1 % + 0.05 Ohm) after 1000 h at 70 C, not an in-service rate.

## 3. Sensitivity: how voltage, current limits and losses move M1 (`energy_basis.out` 2, 3, 3b)

**U3's efficiency barely depends on the bus.** Recomputed by stream s117's method at each bus and limit (0b proves the
method reproduces the carried 0.972 / 0.979 / 0.983 at 20.7 V and 6.2 A exactly), TI's reading is 0.9796 at 19.146 V and
0.9790 at 20.887 V (6.1 A). The bus acts almost wholly through the power U3 may take: 116.8 W at 6.1 A at the minimum
against 126.3 W at the model's 20.7 V.

**The power into U3 is the dominant electrical input, and the response has a knee** (`energy_basis.out` 3b; every other
input at NOM, 40/0):

| Into U3 | 4S14P TYP | 4S14P WAB | 4S15P TYP | 4S15P WAB |
|---|---|---|---|---|
| 110.0 W | NOT MET, 3.6 Wh unserved | NOT MET, 59.2 Wh unserved | 27.1 | NOT MET, 28.5 Wh unserved |
| 114.0 W | 39.7 | NOT MET, 15.9 Wh unserved | 70.5 | 14.8 |
| 116.0 W | 61.4 | 5.7 | 92.2 | 36.4 |
| 118.0 W | 76.1 | 27.4 | 107.2 | 58.1 |
| 120.0 W | 85.4 | 49.0 | 116.6 | 79.8 |
| 122.0 W | 93.7 | 66.7 | 125.2 | 97.8 |
| 124.0 W (NOM) | 93.7 | 75.7 | 125.2 | 106.8 |

Between about 110 and 122 W every 2 W into U3 moves the lowest store by 8 to 22 Wh. The bus's established range, 19.146 to
20.887 V, spans 116.8 to 127.4 W at 6.1 A and 114.9 to 125.3 W at 6.0 A: **across the knee**.

**One input at a time from NOM, 40/0, TYP build** (`energy_basis.out` 3; the change in the lowest store at each input's
unfavourable end):

| Input and its unfavourable end | 4S14P | 4S15P | Its basis |
|---|---|---|---|
| the array build, WAB | -18.0 Wh | -18.4 Wh | a1solar's fits, window, cell heat and lead (section 4b) |
| the pack's charge efficiency, 0.90 (0.95 carried) | -15.6 Wh | -16.0 Wh | `energy_inputs.yaml`: INFERRED from the cell's DC resistance, "no held document gives it" |
| VBUS20 at 19.146 V (and U3's TI reading there) | -14.0 Wh | -14.4 Wh | section 2 |
| U3's input limit at 6.0 A | -8.0 Wh | -8.3 Wh | s119's bracket |
| the stage's and the front end's efficiency, each 0.90 (0.93 carried) | -1.1 Wh each | -1.1 Wh each | declared, NOT PLOTTED at these ratios |
| the lid's discharge loop, 0.045 Ohm | -0.8 Wh | -0.8 Wh | ESTIMATE bracket |
| U3's efficiency, the makers' maxima | -0.2 Wh | -0.2 Wh | s117's method |
| the ideal diode's V(AK), 29 mV | -0.2 Wh | -0.3 Wh | MAKER LM74700-Q1 |
| U3B's efficiency, 0.963; the lid's charge loop, 0.040 Ohm | 0.0 Wh | 0.0 Wh | at NOM on 40/0 neither binds |

The one-at-a-time changes do not add up. Near the knee the inputs compound: NOM to WE moves the 4S14P TYP store from 93.7 to
51.1 Wh, and its WAB store from 75.7 Wh to NOT MET. **Which input dominates:** on the mean day, the power U3 may take (the bus
times U3's limit), the array build and the pack's charge efficiency, in that order of leverage near the knee. The last is a
bracket no held document supports. Beyond the mean day, **the weather dominates every one of them** (section 5). The 4S9P lid
is NOT MET by 162.0 to 172.6 Wh in every single-input case.

## 4. The cases, exactly

### 4a. The weather: SC-37's reference day, and nothing worse

- **Resource:** PVGIS 5.2, PVGIS-SARAH2 monthly means 2015 to 2020 at Leiden, latitude 52.160, longitude 4.497
  (`v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json`). It is the September mean day on the 40 degree, azimuth 0 plane
  (PVGIS's optimum), **4.014 kWh/m2 a day**.
- **Shape:** PVGIS DRcalc's September mean-day profile, PVGIS-SARAH2 2005 to 2020, hourly, UTC, on that plane
  (`v2/docs/records/a1solar/inputs/pvgis-leiden-daily-profile-2005-2020.json`, 3.983 kWh/m2), **scaled by 1.007820** to the
  monthly mean.
- **Duration and starts:** the same 24 hours repeated for 72 hours, run from 06 and from 18 UTC, each from a full pack. Both
  must end the 72 hours without a stop.
- **Temperatures:** air 13.23 to 18.33 C (the profile's T2m). The lid pack is held at 13.23 C (the day's minimum) and the base
  pack at +20 C for all 72 hours.
- **Other planes:** each plane's own DRcalc September mean day (`v2/vendor/solar/pvgis-planes/`), scaled by the same factor.
- **No worse-weather case is established by any run on this page or in the records it cites.** A mean day is not a cloudy
  day. Section 5 is informative only.

### 4b. The array build: TYP and WAB, both on the same mean day

Four Renogy RNG-100DB-H in 2S2P, 400 Wp, held at a fixed input point by board E's stage. The ratio multiplies PVGIS's 0.9417
(the 40/0 plane's angle, spectral and temperature losses, kept for every plane).

- **TYP, the typical build:** single-diode fit "Rs 0", the FBIN point at 34.29 V, NOCT 45 C, a 5 m lead (0.0465 Ohm loop).
  At 40/0: 0.9903 of the tracked energy.
- **WAB, the worst array build:** the earlier records' case C, which they called "adverse". It is an installation and
  component worst case on the SAME mean day, **not a weather case**. Its terms:
  - the worst of the three single-diode fits (Rs 0, 0.1 and 0.2 Ohm);
  - the FBIN point at the worse end of its window (33.05 or 35.57 V, from FBIN over temperature and R8 and R9 at 1 %);
  - cells 10 K above the NOCT model;
  - a 10 m lead (twice the loop);
  - the hotter cells' own loss of maximum-power energy (the lower of the model's figure and the maker's -0.42 %/K).

  At 40/0: 0.9103.

### 4c. The electrical and loss inputs

| Case | Bus | U3 limit | U3 | U3B | Other losses |
|---|---|---|---|---|---|
| **NOM** | 20.000 V, nominal | 6.2 A, IIN_HOST's nominal | 0.9793, TI's reading at that bus | 0.972 | nominal (below) |
| **WE**, the established worst electrical inputs | **19.146 V**, the envelope's minimum | **6.1 A**, its minimum | **0.9733**, the makers' maxima at that bus | **0.963**, its lower bracket | nominal |
| **WE60** | 19.146 V | 6.0 A, the bracket | 0.9734 | 0.963 | nominal |
| **WA**, every bracket unfavourable | 19.146 V | 6.0 A | 0.9734 | 0.963 | unfavourable ends (below) |
| **GEN**, board A as generated | 20.000 V | 4.15 A under the front end's 4.30 A limit (entry E1) | 0.9810 | 0.972 | nominal |
| M207, for comparison (the model as published) | 20.7 V | 6.1 A | 0.979 carried | 0.972 | nominal |
| SC76, for comparison (SC-76's basis) | 19.08 V | 6.1 A | 0.979 carried | 0.972 | nominal |

The other losses, nominal and (unfavourable end) as the model's own sources print them:

- the stage 0.93 (0.90) and the front end 0.93 (0.90);
- the pack's charge efficiency 0.95 (0.90);
- the lid's discharge loop 0.030 Ohm (0.045) and charge loop 0.023 Ohm (0.040);
- the ideal diode's V(AK) 20 mV (29 mV).

**Common to every case:**

- 400 Wp into a 200 W stage window;
- the drafted entry R11 6.2 mOhm, whose front end limit (6.94 A minimum) lies above U3's; GEN excepted;
- U3B at code 62 (7.936 A);
- PS-IDLE-SPEC 42.8 W at the pack terminals;
- the cells aged to 80 percent, with the 3.00 V line and the 5 percent reserve;
- the charge and the discharge split between the packs by capacity;
- U3's input power is its limit times the bus. The front end's own limit is its current times the same bus.

## 5. INFORMATIVE ONLY: M1 in September's actual weather, 2005 to 2020 (`energy_basis.out` 6)

**Not a requirement proposal.** Whether M1 must hold in worse weather than SC-37's mean day is the owner's call.

**Data.** PVGIS 5.2 seriescalc: hourly global irradiance on the 40 degree south plane at Leiden, PVGIS-SARAH2 2005 to 2020,
the database, years, site and plane of the reference day. Its September rows are filed as
`v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json` by `fetch_pvgis_series.py`,
with the whole answer's size and sha256 and a `v2/vendor/sources.txt` line. Its mean September day is 3.983 kWh/m2, hour
by hour equal to the DRcalc profile the reference day is built from: the reference day is this record's average.

**Method** (one site, one plane, one method):

- every 72 hour window that starts at 06 or 18 UTC on 1 to 27 September of each year: 864 windows;
- the series as PVGIS gives it, not scaled to the 2015 to 2020 monthly mean;
- each calendar day's own TYP or WAB ratio folded into its hours;
- the lid pack at the window's own minimum air, a full pack at each window's start;
- the rest as section 4.

Check 0d proves that feeding a series hour by hour reproduces the mean-day runs exactly.

**Results.** The 72 hour irradiation over the windows is 3.17 at the lowest, 7.36 at the 10th percentile and 11.45 kWh/m2 at
the median, against the reference day's 12.04 over three days.

| Lid | Case | Windows meeting M1 | The darkest window (2019-09-23 18h, 3.17 kWh/m2) | The 10th percentile window (2011-09-19 18h, 7.36 kWh/m2) | Lowest irradiation that meets / highest that fails |
|---|---|---|---|---|---|
| 4S14P | NOM TYP | 207 of 864 (24.0 %) | NOT MET, 1461 Wh unserved | NOT MET, 846 Wh | 9.86 / 18.23 kWh/m2 |
| 4S14P | WE TYP | 169 of 864 (19.6 %) | NOT MET, 1468 Wh | NOT MET, 861 Wh | 11.24 / 18.36 |
| 4S14P | WE WAB | 128 of 864 (14.8 %) | NOT MET, 1569 Wh | NOT MET, 953 Wh | 11.80 / 19.22 |
| 4S15P | NOM TYP | 235 of 864 (27.2 %) | NOT MET, 1436 Wh | NOT MET, 815 Wh | 9.86 / 18.23 |
| 4S15P | WE TYP | 199 of 864 (23.0 %) | NOT MET, 1443 Wh | NOT MET, 830 Wh | 9.86 / 18.23 |
| 4S15P | WE WAB | 157 of 864 (18.2 %) | NOT MET, 1545 Wh | NOT MET, 922 Wh | 11.45 / 18.68 |

A window of more than 18 kWh/m2 can still fail. INFERRED from the model's structure, not traced window by window: one dark
day inside a window leaves a night the packs cannot bridge, whatever the other days bring. So M1 on solar, as the model has
it, needs every day of the window to be near a mean day or better, and September gives that in about one window in four to
seven.

**Limits of this case:**

- PVGIS's 0.9417 is an average loss, applied here to single days;
- one plane only;
- the base pack at +20 C;
- a full pack at each window's start, with no carry-over from the days before;
- SARAH2's hourly averages as given.

## 6. The displaced lid function (the records; nothing designed here)

Read from `v2/docs/records/a1mech/README.md` section 3 and `DECISION-A1.md` (stream a1mech), with CASE-MARGINS and appendix
32.60, which a1mech cites:

- **QMX HF set out (4S15P):** "HF inside (16a) is lost, because the base has no volume for it (appendix 32.60: no bay on B16
  cleared the unit, the reason it went to the lid; the west pocket now takes the second block); outside the case it would
  need a lead through the back wall, which the ruled connector plate does not carry." **No location is established
  elsewhere in the kit: the HF function leaves the kit unless a location is found.** Cost: an approved function (appendix
  32.50 item 16a, deferred from prototype 1 by D-01 but not withdrawn) and the kit's only HF bearer. The records put no
  figure on another location's cost, because none is established.
- **Tablet bracket out (4S14P):** "the tablet is carried outside the case and still works on the kit's WiFi and the USB-C
  outlet; REQ-011's bracket is not met." **No location for the bracket is established in the kit.** The tablet's use as a
  display continues outside the case, but the bracket's function (a tablet held in the lid, item 16d) **leaves the kit
  unless a location is found**. Cost: REQ-011's bracket not met. How the tablet is transported with the kit is not
  established by any record read here.
- **Both kept (4S9P):** no function displaced, and M1 is NOT MET in every case (section 1).

## 7. What the grid does not show, and the other limits

- **The grid.** 10 degree slope and 15 degree azimuth steps. A band's edges are grid points that were run: the boundary
  between an edge that counts and the next point that does not is not located, and nothing between grid points is run. The
  operator has no angular tolerance beyond a band's edge on this evidence. No plane steeper than 70 degrees or turned more
  than 45 degrees from south is run.
- **The floor of 4.2 Wh** is the model's hourly-step sensitivity, measured once at 40/0 at an earlier issue's settings. It
  is applied as a floor, not a bound.
- **The site and day.** Every day, the scale, the lid basis and the ratio come from Leiden. A condition for another site
  needs its own grid of DRcalc days, monthly mean, PVcalc losses and air temperature, and SC-37 restated (PLANES.md section 6).
- **The model's structure.** One reference day repeated; hourly steps; the base at +20 C and the lid at the day's minimum air
  for 72 hours. The chargers' efficiencies exclude their inductors' core loss (s117, s119), so they are high by it. PVGIS's
  40/0 losses are carried to every plane. The stage's and the front end's 0.93 are declared, not plotted at these ratios.
  The pack's charge efficiency 0.95 is INFERRED with a 0.90 to 0.98 bracket and no held document.
- **The bus.** The copper between the divider's tap and R16 is not established (no layout of this netlist). The resistors'
  long-term drift is excluded. VREF's split between part to part and temperature is not given by TI. The amplifier's gain
  is TI's typical.
- **The entry.** Every Option A(i) figure needs board A's entry re-rated as drafted (R11 6.2 mOhm and IIN_HOST 6.2 A). As
  generated no option meets.

## 8. Tools, outputs, commands and the proof that nothing committed moved

| File | What it is |
|---|---|
| `vbus20_range.py`, `vbus20_range.out` | section 2: reads the netlist, `lcsc_fill.py`'s map, the A24 BOM, the LCSC reading, the YAGEO (filed) and UNI-ROYAL (held, read when present) sheets, TI SNVSAI1D, `pcb_envelope.yaml` and the reference day's T2m; refuses (exit 3) if a fact it rests on is not as expected |
| `fetch_pvgis_series.py` | files the September hourly series (section 5); `--check` re-fetches and compares |
| `energy_basis.py`, `energy_basis.out` | sections 1, 3, 4 and 5; imports `energy_two_pack.py`, `energy_runs.py`, `efficiency.py`, `reconcile_lid_panel.py` and `vbus20_range.py`, each pinned by sha256, and refuses (exit 4) unless its reproduction checks hold |
| `plane_grid.py`, `plane_grid.out`, `PLANES.md` | the first issue's grid. "Adverse" is renamed WAB, and its figures are unchanged (only the wording moved) |
| `v2/vendor/passives/yageo-rc-l-series-v12.pdf` | R6's maker sheet, filed with its `v2/vendor/sources.txt` line (publication: filed, by its terms) |
| `v2/vendor/solar/pvgis-series/...september-slope40-aspect0.json` | the September series, filed with its `sources.txt` line |

**Commands, from the repository root.** Two documents must be present before any run, ignored and never committed:
- the UNI-ROYAL sheet in `v2/vendor/passives/held/`, fetched by `v2/docs/records/w5identc/fetch_held_back.py`;
- the SunPower sheets in `v2/vendor/solar/held/`, fetched by `a1solar/fetch_held_back.py`.

Without the UNI-ROYAL sheet, `vbus20_range.out`'s R7 line reads "NOT PRESENT" and uses the LCSC reading.

```
python3 v2/docs/records/l3plane/vbus20_range.py > v2/docs/records/l3plane/vbus20_range.out
python3 v2/docs/records/l3plane/energy_basis.py > v2/docs/records/l3plane/energy_basis.out
python3 v2/docs/records/l3plane/plane_grid.py > v2/docs/records/l3plane/plane_grid.out
python3 v2/docs/records/a1int/reconcile_lid_panel.py | cmp - v2/docs/records/a1int/reconcile_lid_panel.out
python3 v2/docs/records/a1solar/energy_runs.py | cmp - v2/docs/records/a1solar/energy_runs.out
python3 v2/docs/records/l3plane/fetch_pvgis_series.py --check
```

**No committed output of another stream moved.** No script outside this folder was changed in this issue.
`reconcile_lid_panel.out` and `energy_runs.out` rerun byte identical. `energy_basis.out` reproduces them from its own runs:
- **0a:** all 21 rows of `reconcile_lid_panel.out`, byte for byte at 20.7 V;
- **0b:** the U3 figure of `efficiency.out` section 7, exactly;
- **0c:** all 100 case P cells of `plane_grid.out`;
- **0d:** the series path against the mean-day path.

`energy_basis.out` and `vbus20_range.out` rerun byte identical.
