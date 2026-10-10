accepted: no

# CHECK-1: the energy basis of L3-OD1, L3-OD2 and L3-OD4 (stream l3plane, MESHSAT-1357)

**An AI check, not a qualified review.** 30 September 2026, 02:19 CEST. Branch `fnd/l3plane`, tip `6a283b25` (confirmed
with `git rev-parse`), three commits on `d2084904` (`fnd/int16`). The checker wrote none of the stream. Prototype design:
nothing is built, powered or measured, and nothing below is a measurement.

**How it was checked.** A shared clone at the tip, with the 23 held files of the int16 worktree copied in as ignored files
(none committed). The checker read the netlist of board A (`pcb-a-power.net`, sha256/16 `6c40250c47195ebb`), TI SNVSAI1D
pages 5 to 7 and 9 to 12, TI SLUSE66A (the input current rows, 9.6.22 p.80, REGN), YAGEO RC_L V.12 pages 2, 5 and 8,
UNI-ROYAL pages 6 and 7, `energy_inputs.yaml`, `pcb_envelope.yaml`, the a1mech records and appendix 32.60, and wrote its
own tools beside this file:

- `indep_vbus.py`: the VBUS20 worst case stack, typed from the pages read;
- `indep_balance.py`: a two pack hourly balance written from the model's stated rules and the data files, with no record
  script imported; it also runs 0.1 h and 0.01 h sub steps;
- `indep_grid_weather.py`: the full plane grid on that balance, and its own 72 h windows from the filed series;
- `indep_extra.py`: one input at a time from WE and from NOM WAB, and the thresholds of the proposed band.

Inputs taken, not recomputed: the array ratios (a1solar's model; per plane as `plane_grid.out` 1.1 prints them to four
places, per day in the weather case by importing a1solar's `array_calc.py` only to supply that input) and U3's efficiency
per case (s117's method, as `energy_basis.out` 1c and 2 print it). Their scripts were also rerun, only to confirm the
committed outputs.

## Blocking items

### B1. The sensitivity that answers "how losses affect the energy calculation" is taken at a saturated point and understates the loss terms by an order of magnitude at the case proposed as M1's basis

ENERGY-BASIS section 3 (and `energy_basis.out` 3) moves one input at a time from **NOM with the TYP build**. At that point
both lids' packs fill before dusk: the lowest store is flat from 122 W upward (4S14P 93.7 Wh, 4S15P 125.2 Wh at 122, 124,
126, 128 and 130 W; `energy_basis.out` 3b, reproduced). Every loss on the charge side is therefore masked there. The
page reads that as "the stage's and the front end's efficiency ... -1.1 Wh each", "U3's efficiency, the makers'
maxima -0.2 Wh", "U3B's efficiency, 0.963; the lid's charge loop 0.040 Ohm: 0.0 Wh ... neither binds", and ranks the
dominant inputs as "the power U3 may take, the array build and the pack's charge efficiency".

Counter examples on the checker's balance, 40/0, 4S15P (4S14P within 0.4 Wh of the same changes; the NOM TYP column
reproduces the page's own rows exactly):

| One input at its unfavourable end | Page: from NOM TYP | Checker: from NOM WAB | Checker: from WE TYP | Checker: from WE WAB |
|---|---|---|---|---|
| stage efficiency 0.90 (0.93 declared, not plotted) | down 1.1 Wh | down 16.8 Wh | down 22.0 Wh | down 20.2 Wh |
| front end efficiency 0.90 (0.93 declared, not plotted) | down 1.1 Wh | down 16.8 Wh | down 22.0 Wh | down 20.2 Wh |
| pack charge efficiency 0.90 (0.95 INFERRED, no document) | down 16.0 Wh | down 47.6 Wh | down 56.0 Wh | down 53.4 Wh, NOT MET |
| U3 at the makers' maxima (0.9727) | down 0.2 Wh | down 6.8 Wh | (already in WE) | (already in WE) |
| U3B 0.963 against its carried 0.972 | 0.0 Wh | | down 7.0 Wh | down 6.6 Wh |
| lid charge loop 0.040 Ohm | 0.0 Wh | | down 2.7 Wh | down 2.6 Wh |
| U3's input limit 6.0 A (WE60 against WE) | down 8.3 Wh | | down 20.3 Wh | down 20.3 Wh |

So at the operating point proposed as M1's basis, the stage and the front end efficiency each move the store by about as
much as U3's 6.0 A bracket, and the charge efficiency by about as much as the array build (down 55.0 Wh, WE TYP to WE
WAB). The page's own caveat ("the one at a time changes do not add up") does not repair this: the table and the ranking
are the page's answer to the owner's question, and they are wrong for WE.

**Needed:** the one at a time table from WE (both builds) and from NOM WAB, and the dominance statement restated from it.

### B2. WE is called "the established worst electrical inputs" and is proposed as M1's basis while it holds three undocumented loss figures at nominal, and the proposed 4S15P band survives only within about one percentage point of two of them

WE holds the stage and the front end at 0.93 (`energy_inputs.yaml`: "the intent's declared 0.93 ... NOT PLOTTED"),
both of them electrical conversion efficiencies, and the pack charge efficiency at 0.95 ("INFERRED ... no held document
gives it"). Section 1a item 1 proposes WE as the basis of M1's energy claim and item 2 proposes the 4S15P band from it.

Counter examples (checker's balance, WE otherwise, 40/0):

- charge efficiency 0.90: 4S15P WAB **NOT MET, 26.6 Wh unserved**; 4S15P TYP 25.8 Wh; 4S14P TYP **NOT MET, 4.8 Wh**;
- stage (or front end) efficiency 0.90: 4S15P WAB 6.6 Wh; in WE60, 4S15P WAB **NOT MET, 13.7 Wh**.

Where the band's points stop counting (both builds meet, lowest combined store above 4.2 Wh; WE otherwise):

| The band point | charge efficiency at least | stage (or front end) efficiency at least | VBUS20 at least |
|---|---|---|---|
| 40/0 | 0.929 | 0.897 | 18.800 V |
| 30/0 | 0.934 | | |
| 50/+15 (the band's least point) | 0.942 | 0.921 | 18.992 V |

So the "slope 30 to 50, south to 15 W" band needs a charge efficiency no document gives within 0.008 of its nominal, and a
stage efficiency no maker plots within 0.009 of its declared value. The owner cannot see this from the page: WA lumps
every bracket together, and the sensitivity of B1 hides it.

**Needed:** either name WE for what it holds (the worst bus, U3 limit and charger efficiencies; the stage, front end and
charge efficiencies nominal) and state these thresholds beside the proposed band in section 1 and 1a, or add the cases
that take those three brackets one at a time from WE. The proposal must say that the band, and the tablet out against
QMX out verdict at WE, turn on figures no held document supports.

## Minors

1. **The resistors' long term drift is excluded** (disclosed in sections 2 and 7). With the makers' endurance limits
   (YAGEO p.8 and UNI-ROYAL p.7: plus or minus (1 % + 0.05 Ohm) after 1000 h at 70 C) taken in opposite directions, the
   envelope's minimum is 18.782 V; at WE otherwise the 4S15P 40/0 WAB store is 3.0 Wh (under the floor), TYP 58.0 Wh;
   4S14P TYP 27.5 Wh. The limits are test limits at far more stress than the divider sees (about 80 uA), so this is a
   bound, not an expectation; the page should carry the figure beside the exclusion.
2. **Board A's local rise at the divider is taken as zero** (INFERRED, disclosed). A 20 K rise gives 19.072 V and moves
   the 4S15P 40/0 WAB store from 26.8 to 21.9 Wh at WE. Worth one line.
3. **The range is a DC range.** Soft start (C7 4.7 uF charged at 3.75 to 6.35 uA to the 0.8 V reference: 0.6 to 1.0 s) and
   line and load transients (TI Figures 6-15 to 6-18) last about a second or less and do not move the energy result, but the page does not say so; call the range a
   steady state range. The ground offset between R7's return and U2's AGND is a layout term like the copper to R16 and is
   not named.
4. **"every store above 4.2 Wh" / "every lowest store above the floor"** (section 1 table, `energy_basis.out` 5): the code
   counts only the combined store of both packs. At the band's reference point (4S15P, WE, WAB, 40/0) and in WE60 the lid
   pack's lowest store is 0.0 Wh: the lid is run to its cutoff (`energy_basis.out` 4, reproduced). Say "the lowest
   combined store" and that the lid empties there; "6.4 Wh above empty" is the base alone.
5. **Labels.** U3's 6.1 A "minimum" is INFERRED: SLUSE66A 9.6.22 p.80 gives only the maximum (100 mA above the nominal
   for 10 mOhm); the printed accuracy rows are for 5 mOhm (plus or minus 200 mA), and the front page's 2.5 % gives
   6.045 A. U3's and U3B's efficiencies are INFERRED by TI's method (`energy_inputs.yaml`'s own label) and appear on the
   page as "TI's reading" or "the makers' maxima" with no label.
6. **The knee.** "a knee between 110 and 122 W" holds for the TYP build. With WAB the store keeps rising to 128 W (4S15P
   106.8, 115.4, 122.4 Wh at 124, 126, 128 W), so NOM's 124 W sits on the WAB slope.
7. **PLANES.md still states derived conditions on the superseded 20.7 V basis** (4S14P "slope 20 to 50, 15 E to 30 W";
   "one condition written for either option") without PROPOSED; at WE the 4S14P has no band. The header's supersession
   note exists; mark the conditions themselves superseded so they cannot be read into the owner's table.
8. **An excluded loss is not in section 7:** the lid path's standby drain (1.5 to 1.8 Wh over 72 h, outside the 42.8 W)
   and board PL's own supply (`reconcile_lid_panel.out` NOTES). As 1.8 Wh of load: 4S15P WE WAB 26.8 to 25.3 Wh, WE60
   6.5 to 5.0 Wh (still above the floor).
9. **Line 13** says the page answers the owner's call for "an independent check of how voltage, current limits and losses
   move the energy result". The page is the author's analysis; reword so it does not read as the independent check.
10. **GEN's margin.** E1's IIN_HOST maximum, 4.25 A, is 50 mA under the front end's 4.30 A minimum, and R11 also carries
    the VBUS20 currents that do not pass R16 (U3 pin 1, U2 pin 24 BIAS, R197, the divider; netlist). Not quantified
    here. It can only make GEN worse and does not change its verdict.

## What holds

- **The circuit (NETLIST).** R6 240k 1 % from /VBUS20 to /FE_FB, R7 10k 1 % to GND, U2 pin 11 on FE_FB; R11 from FE_OUT
  to VBUS20 with ISNS+ (R160) at FE_OUT and ISNS minus (R161) at VBUS20; R16 from VBUS20 to CH_ACN; U3 pin 1 on VBUS20.
  So R11's drop is inside the loop and VBUS20 is the regulated node. The bleed (4 x 510 Ohm) is off while FE_RUN is
  high. R17 (RSR) sits between VBAT and CELL_FUSED, so U3's ChargeCurrent limit applies to the base cells only and the
  load and U3B hang on VBAT, as the model assumes. U3's ILIM_HIZ divider (16.5k over 34.8k from REGN) sets about 7.2 A
  nominal at REGN's 5.7 V minimum (SLUSE66A: 1 V + 40 x IDPM x RAC), so it does not bind under 6.3 A.
- **The parts and pages (MAKER).** R6 = C137765, YAGEO RC0603FR-07240KL (lcsc_fill.py line 193, the A24 BOM); RC0603 1 %,
  10 Ohm to 10 MOhm, 100 ppm/K, t1 +25 C (p.5, p.8). R7 = C25804, UNI-ROYAL 0603WAF1002T5E; 0603 above 10 Ohm 100 ppm/K
  (p.6). VREF 0.788 / 0.800 / 0.812 V at FB = COMP over TJ minus 40 to 125 C; IBIAS(FB) 25 nA maximum; gm 1.31 mS and
  ROUT 20 MOhm typical only; VCC 7.88 V maximum (p.6); VSNS 43 / 50 / 57 mV (p.7); no reference curve on pp.9 to 12.
- **The range.** Recomputed exactly (table below). The worst case stack is sound: linear, every term at its unfavourable
  end at once, tolerance and TCR opposite on the two resistors; nothing is double counted (the amplifier's offset is inside
  VREF's FB = COMP test; the finite gain term is taken conservatively at COMP = VCC maximum).
- **The GEN finding (major, for the owner).** As generated R11 is 10 mOhm and the LM5176's constant current loop holds
  4.300 / 5.000 / 5.700 A, below U3's drafted 6.2 A: the bus cannot carry U3's limit. It is a1elec's finding (TOPOLOGY.md
  section 7), surfaced correctly. Every Option A(i) figure uses entry E2's drafted 6.2 mOhm (6.935 A minimum): the front
  end cap in `reconcile_lid_panel.py`, `plane_grid.py` and `energy_basis.py` is E2's. With the generated R11 at its
  minimum, every lid fails by 326 to 523 Wh (checker's GEN).
- **The energy model's cases.** The checker's balance reproduces every combined case of `energy_basis.out` 4 within
  0.1 Wh (the ratios rounded to four places), the knee table 3b and the NOM one at a time rows. The step error: at WE and
  WE60 a 0.01 h step moves the stores by at most 0.1 Wh; at NOM by 2.4 to 3.1 Wh, inside the stated 4.2 Wh floor.
- **The bands.** All six maps of `energy_basis.out` 5 (4S14P and 4S15P at NOM, WE, WE60) are identical on the checker's
  grid, and twelve plane cells were spot checked with values, edges included (table below). 4S14P has no WE band: confirmed.
- **The weather case.** 16 Septembers, 11520 rows, 864 windows; the series' mean day 3.9830 kWh/m2, within 0.005 W/m2 of
  the DRcalc profile hour by hour; lowest, 10th percentile and median 72 h irradiation 3.17, 7.36, 11.45 kWh/m2. All six
  percentages reproduced exactly on the checker's windows and balance with a1solar's per day ratios. With the 40/0 mean
  day ratios on every day instead: 24.1 / 19.6 / 16.3 % and 27.4 / 23.0 / 20.0 %. `fetch_pvgis_series.py --check`
  re-fetched PVGIS: "September rows equal the filed ones". The JSON (1489129 bytes, sha256 `c5f0363a...`) and the YAGEO
  sheet (467972 bytes, `e7dbabb0...`, no copyright or redistribution term in its text layer) match their `sources.txt`
  lines. No held or ignored file is committed; the largest added file is 1.49 MB.
- **Relocation facts.** a1mech README section 3 item 2 and DECISION-A1.md say what the page quotes: the base has no
  volume for the QMX (appendix 32.60: it left B16's west bay for the lid), and outside the case it would need a back wall
  lead the ruled connector plate does not carry. Tablet out: "carried outside the case ... REQ-011's bracket is not met";
  the records establish no in kit location. Nothing is designed on the page.
- **Wording and hygiene.** "adverse" appears in no output, only as an explained rename and as `energy_runs.py`'s method
  name; WAB is defined as a build case on the same mean day, not weather. Section 1a carries the narrower conditions and
  function losses as PROPOSED. No U+2013 or U+2014 and no host names or user paths in any added line.
  `pcb_requirements.yaml` is untouched. The second issue's change to `plane_grid.py` and `plane_grid.out` is wording only.
  Commits are in the owner's name with no trailer. Rerun in the clone: `vbus20_range.out`, `energy_basis.out`,
  `plane_grid.out`, `reconcile_lid_panel.out` and `energy_runs.out` are byte identical.

## Independent figures beside theirs

| Figure | Theirs | Checker |
|---|---|---|
| VBUS20 nominal | 20.000 V | 20.0000 V |
| VBUS20, VREF and 1 % only | 19.326 to 20.694 V | 19.3255 to 20.6937 V |
| VBUS20, envelope (45.0 K) | 19.146 / 20.887 V | 19.1458 / 20.8871 V |
| VBUS20, M1's day (28.9 K) | 19.205 / 20.823 V | 19.2050 / 20.8226 V |
| amplifier and IBIAS terms | 8 and 6 mV | 7.52 and 6.00 mV |
| VBUS20 minimum with a 20 K board rise; with the endurance limits | not given | 19.072 V; 18.782 V |
| front end limit, R11 10 mOhm | 4.30 / 5.00 / 5.70 A | 4.300 / 5.000 / 5.700 A |
| front end limit, R11 6.2 mOhm (draft) | 6.94 / 8.06 / 9.19 A | 6.935 / 8.065 / 9.194 A |
| 4S15P NOM, TYP / WAB | 125.2 / 106.8 Wh | 125.2 / 106.8 Wh |
| 4S15P WE | 81.7 / 26.7 Wh | 81.8 / 26.8 Wh (lid 26.5 / 0.0) |
| 4S15P WE60 | 61.4 / 6.4 Wh | 61.5 / 6.5 Wh (lid 12.2 / 0.0) |
| 4S15P WA | NOT MET 40.0 / 91.8 Wh | NOT MET 40.0 / 91.7 Wh |
| 4S15P GEN | NOT MET 326.6 / 352.8 Wh | NOT MET 326.7 / 352.9 Wh |
| 4S14P NOM | 93.7 / 75.7 Wh | 93.7 / 75.7 Wh |
| 4S14P WE | 51.1 Wh / NOT MET 3.9 Wh | 51.2 Wh / NOT MET 3.8 Wh |
| 4S14P WE60 | 30.9 Wh / NOT MET 24.1 Wh | 30.9 Wh / NOT MET 24.1 Wh |
| 4S14P WA | NOT MET 70.3 / 120.5 Wh | NOT MET 70.3 / 120.5 Wh |
| 4S14P GEN | NOT MET 357.5 / 383.8 Wh | NOT MET 357.6 / 383.9 Wh |
| 4S9P NOM; WE; WA; GEN | NOT MET 165.7/172.6; 166.2/173.0; 190.9/245.4; 494.7/522.4 | NOT MET 165.7/172.6; 166.2/173.0; 190.8/245.3; 494.8/522.5 |
| SC76: 4S15P; 4S14P | 95.9 / 40.1; 65.1 / 9.4 Wh | 95.8 / 40.1; 65.1 / 9.4 Wh |
| knee: 4S14P TYP at 110 / 112 W | NOT MET 3.6 / 18.1 Wh | NOT MET 3.6 / 18.1 Wh |
| knee: 4S15P WAB at 112 / 114 W | NOT MET 6.9 / 14.8 Wh | NOT MET 6.8 / 14.8 Wh |
| one at a time from NOM TYP, 4S15P: bus 19.146 V; 6.0 A; charge 0.90; WAB | down 14.4; 8.3; 16.0; 18.4 Wh | down 14.3; 8.3; 16.0; 18.4 Wh |
| 4S15P WE band | slope 30 to 50, 0 to 15 W; least 12.6 Wh at 50/+15 | same map; least 12.7 Wh at 50/+15 |
| 4S15P WE edges TYP / WAB: 30/0; 30/+15; 40/+15; 50/0 | 74.5/20.7; 70.5/16.8; 73.6/22.1; 74.4/19.8 | 74.5/20.8; 70.6/16.9; 73.7/22.2; 74.5/19.9 |
| 4S15P WE, just outside: 20/0; 60/0; 40/+30; 40/-15 (WAB) | T only (map) | NOT MET 4.5; 0.1 (under floor); NOT MET 19.3; NOT MET 6.1 Wh |
| 4S15P WE60 band; 30/0; 40/+15; 50/0 (WAB) | 40/0 only, 6.4; 0.4; 1.9; NOT MET | 40/0 only, 6.5; 0.5; 2.0; NOT MET 0.4 Wh |
| 4S14P WE, best planes WAB: 40/0; 40/+15; 30/0 | NOT MET (map) | NOT MET 3.8; 8.3; 9.8 Wh |
| step error at WE (0.01 h against 1 h) | not measured (floor from an earlier issue) | at most 0.1 Wh |
| weather: windows; 4S14P NOM TYP / WE TYP / WE WAB | 864; 24.0 / 19.6 / 14.8 % | 864; 24.0 / 19.6 / 14.8 % |
| weather: 4S15P NOM TYP / WE TYP / WE WAB | 27.2 / 23.0 / 18.2 % | 27.2 / 23.0 / 18.2 % |
| weather: 72 h irradiation lowest / p10 / median | 3.17 / 7.36 / 11.45 kWh/m2 | 3.17 / 7.36 / 11.45 kWh/m2 |

Rerun (pure Python, under a second except the per day weather run, about a minute), from this folder, against a checkout
of `fnd/l3plane` with the held files present: `python3 indep_vbus.py`, `python3 indep_balance.py <checkout>`,
`python3 indep_grid_weather.py <checkout> fixed` (and `perday`), `python3 indep_extra.py <checkout>`. Outputs are filed
beside each script. The clone was removed after the check.
