accepted: yes

# CHECK-2: the energy basis, second round, and the owner's weather addendum (stream l3plane, MESHSAT-1357)

**An AI check, not a qualified review.** 30 September 2026, 03:03 CEST. Branch `fnd/l3plane`, tip `ec415c09` (confirmed),
three commits on `6a283b25` (`ac81f847`, `24acb9dc`, `ec415c09`). Scope: the changed sections and what they rest on. The
checker wrote none of the stream. Prototype design: nothing is built, powered or measured.

**How it was checked.** A shared clone at the tip (`_scratch/chk-energy2`, removed after the check) with the int16
worktree's held files copied in as ignored files, never committed. The checker read `git diff 6a283b25..ec415c09`, the new
`ENERGY-BASIS.md`, `weather_basis.py`, `curve_readings.py` and the changed parts of `energy_basis.py` and
`vbus20_range.py`. It also read the makers' pages: LT8705A 8705af p.41, SNVSAI1D p.9 Figure 6-2, the Samsung 35E
report pp.3 and 7, and POWER-THERMAL.md section 4. It checked board E's netlist for Q3 and Q4, and the table of
a1mech README section 2.

All figures were recomputed on the checker's own balance (`indep_balance.py`, CHECK-1), extended by
`indep_round2.py` and `indep_round2b.py` (outputs beside them). It imports no record script. The array ratios are the
one input taken from another stream: per plane as `plane_grid.out` prints them, per day from a1solar's model (cached
in `dayratios.json`).

## Blocking items

None. CHECK-1's B1 and B2 are answered (below). Every figure recomputed agrees within 0.1 Wh or one window.

## Minors

1. **The cell sheet's charge-efficiency bound for the base uses the wrong discharge current.** `energy_basis.py` line
   444 divides by `NP_B + n_p` with n_p = 6 for the base row, i.e. 12 cells in parallel, giving 0.246 A a cell. In the
   4S20P and 4S21P kits the base cells discharge at 0.148 and 0.141 A a cell. So the bound is 0.9924 to 0.9925, not
   0.9915, and the range is 0.9924 to 0.9937 (section 3, `energy_basis.out` 2). WE-MKR carries 0.9915; at 0.9925 its
   coverage moves by at most one window (4S14P 215 to 216 of 864, 4S15P unchanged). Conservative and negligible, but a
   slip in a MAKER-derived figure.
2. **The sizing takes the percentile of usable Wh, then reports the cell count of that one window.** Windows differ in
   lid temperature, so the X-th percentile of the store is not the X-th percentile of the lid count. The count that
   covers X % of windows is the percentile of the per-window count:

   | Target | Page's cells | Percentile of the count |
   |---|---|---|
   | TYP 50 % | 132 | 128 |
   | TYP 80 % | 168 | 172 |
   | TYP 95 % | 228 | 220 |
   | WAB 50 % | 136 | 136 |
   | WAB 80 % | 192 | 184 |
   | WAB 95 % | 232 | 228 |

   The cells, nominal Wh, mass and volume of section 8a are therefore off by up to 8 cells (0.4 kg) either way. For
   example, 168 cells covers less than 80 % of the windows. No verdict changes: every target stays far above 84 cells.
3. **The multiples are stated in usable Wh at mixed temperatures.** The 692.1 Wh base is the 4S21P kit at the mean
   day's 13.23 C. Each window's need is at its own, usually colder, lid air, and the extra cells go in the colder lid
   (0.655 of nominal against the kit's 0.683). In cells or mass, the physical quantity, the multiples of the 84-cell kit
   are 1.57 / 2.00 / 2.71 (TYP) and 1.62 / 2.29 / 2.76 (WAB), not 1.4 to 2.5. Both figures belong beside "several times"'
   replacement. Growing the store on the lid side is otherwise a fair assumption: the base pockets are fixed, and U3B's
   unchanged code 62 does not bind, since the node's surplus stays under the lid path's input limit.
4. **Option (i)'s limitation quotes only the QMX-out lid.** "It carries 17.5 to 22.0 percent of the past windows" is
   the 4S15P lid's STOP figure. For the two Option A(i) lids it is 14.0 to 22.0 % (STOP), or 13.2 to 21.5 % on COMB,
   the line the sizing uses. Option (i)'s own TYP store, 4S13P, is smaller than either lid and carries fewer windows
   still.
5. **The dominance list (section 4, "Which input dominates") leaves out U3's own efficiency.** From WE, TI's reading
   against the makers' maxima is worth 12.2 to 12.6 Wh (`energy_basis.out` 4). That is larger than any other term in
   item 5, which is "under about 15 Wh" only without it.
6. **Section 3's LM5176 row compares the wrong currents.** "Board A's input current at 122 W is about 8 A, above the
   plot's 6 A x 9 V": the plot's load current is its OUTPUT current. At 6 A out, 12 V, 97.8 %, the 9 V curve's input
   current is about 8.2 A, about board A's (8.7 A at 122 W over 0.93). Reword. The row's verdict, NOT ESTABLISHED,
   stands.
7. **Wording tension in 1a.** Item 1 proposes "WE as restated" as the basis of M1's energy claim, while section 1 and
   item 3 say that a band built on WE "is conditional, not a basis for a requirement". Both hold if item 1 is read as the
   case definition; say so in one clause.
8. **For the record, CHECK-1's minor 2 was wrong and the page's correction is right.** A rise at the divider warms only
   the hot end, 62.1 C plus 20 K, 57.1 K from +25 C. That gives 19.101 V, not the 19.072 V CHECK-1 printed. The checker
   gets minus 2.9 Wh from it at WE, the page minus 2.8 Wh.

## What holds

**B1, the sensitivity at the binding case.** The NOM TYP table is withdrawn, and the new table from WE (TYP and WAB)
and from NOM WAB reproduces on the checker's balance, every row within 0.1 Wh. From WE, 40/0:

| Input | Page, 4S14P / 4S15P | Checker, 4S14P / 4S15P |
|---|---|---|
| charge efficiency 0.90, TYP / WAB | -55.7 / -53.1; -55.7 / -53.1 | -55.7 / -53.1; -55.7 / -53.1 |
| the other array build (TYP to WAB) | -54.8; -54.8 | -54.8; -54.8 |
| bus at the endurance bracket 18.782 V | -23.2; -23.3 | -23.2; -23.3 |
| stage or front end 0.90, TYP | -21.8; -22.0 | -21.8; -22.0 |
| U3's limit 6.0 A | -20.1; -20.2 | -20.1; -20.2 |
| divider-rise bracket 19.101 V | -2.8 | -2.9 |
| U3B 0.972; loops nominal; no drain; V(AK) 20 mV (favourable) | +6.5 to +6.9; +4.7 to +5.2; +1.5; +0.7 | same |

**B2, the undocumented efficiencies.**
- WE is restated in section 6c and `energy_basis.out` 1c, each term labelled, and named CONDITIONAL on the stage 0.93,
  front end 0.93 and charge 0.95. Section 1 says it plainly: "A band built on them is conditional, not a basis for a
  requirement", as do 1a item 3 and section 7.
- The makers' readings are on the pages cited:
  - **LT8705A p.41** ("12V, 15A Output Converter"): M1 BSC028N06NS and M2 BSC039N06NS are board E's Q3 and Q4 in
    `pcb-e1-dock.net`. The 35 V curve reads about 96 to 97 % from 6 to 12 A.
  - **SNVSAI1D p.9 Figure 6-2**: the 9 V curve (12 V out, 300 kHz, 4.7 uH) reads about 97.8 % near 6 A.
  - **Samsung pp.3 and 7**: 3,482 mAh, 12.62 Wh; initial DC-IR 34.5 mOhm.
- Each is labelled typical, another circuit, INFERRED, NOT ESTABLISHED. That is correct: other ratios, frequencies,
  inductors and output voltages, not weighted over the day. The page also notes that ARRAY.md's draft replaces Q3 and
  Q4 for 2S2P.
- Thresholds, recomputed by the checker's own bisection:

  | Point, line | Charge efficiency | Stage | U3's limit |
  |---|---|---|---|
  | 4S15P 50/+15, COMB | 0.949 | 0.929 | 6.093 A |
  | 4S15P 40/0, COMB | 0.936 | 0.907 | 6.025 A |
  | 4S15P 30/0, COMB | 0.941 | 0.917 | |
  | 4S15P 40/0, EACH | 0.981 | 0.980 | 6.264 A (page 6.265) |
  | 4S14P 40/0, COMB | 0.964 | 0.952 | 6.173 A (page 6.174) |
  | 4S14P 50/0, COMB | 0.971 | 0.963 | |
  | 4S14P 40/0, EACH | none | none | none |

**The minors of CHECK-1.** All ten are answered:
1. The endurance bracket, 18.782 V, is carried as case WEL.
2. The divider's rise is 19.101 V (see minor 8 above).
3. The range is named steady state. The soft start is 0.59 to 1.00 s (C7 4.7 uF, ISS 3.75 to 6.35 uA). The transients
   and the ground offset are named.
4. COMB and EACH appear in every table. The checker's grid confirms: at WE, 4S15P COMB is slope 30 to 50, south to
   15 W; EACH has no band for either lid; 4S14P has no band on either line.
5. U3's 6.1 A is labelled INFERRED; 2.5 % of 6.2 A gives 6.045 A.
6. The knee is split into TYP and WAB.
7. PLANES.md's conditions are marked SUPERSEDED, proposals only.
8. The drain is carried as 1.8 Wh of load.
9. The page calls itself "not the independent check".
10. GEN's 50 mA margin and R11's other currents are named.

At the restated WE the hourly step still moves the stores by at most 0.1 Wh.

**The coverage (section 8, `weather_basis.out` A).** The checker built its own 864 windows:
- starts at 06 and 18 UTC on 1 to 27 September of 2005 to 2020;
- the last window ends 2020-09-30 17:11 UTC;
- full aged packs at each start, the base at +20 C, the lid at the window's minimum air;
- 42.8 W plus the 0.025 W drain in the WE cases.

It recomputed all 15 cases of the three lids on all three lines, 45 cells, including 4S9P (0 in every case) and every
EACH cell. Every count is equal but one: 4S15P WE WAB STOP is 152 against the page's 151 (17.6 against 17.5 %), a window
at the margin; that case's COMB (146) and EACH (108) are equal. The label "MODELLED HISTORICAL COVERAGE, not a
probability of success" is on the page and in the output. Every item of the owner's list is recorded: the dataset
(PVGIS 5.2 seriescalc, SARAH2 and ERA5, DEM horizon), the years, the windows and their overlap, the start times, the
initial charge, the ageing and temperatures, the load, the orientation, the three failure criteria, and all three lids
compared on the same cases.

**L3-OD6 (section 8a).** The store per window by bisection and its percentiles are reproduced:

| Figure | TYP | WAB |
|---|---|---|
| (i) mean day | 618.8 Wh, 4S13P | 676.1 Wh, 4S15P |
| 50 % | 981.6 Wh | 1055.3 Wh |
| 80 % | 1331.0 Wh | 1420.4 Wh |
| 95 % | 1688.7 Wh | 1760.3 Wh |
| Median need | 982.2 Wh | |
| Largest need | 2174.3 Wh | |

The 4S21P base is 692.1 Wh. Also confirmed:
- 12.06 Wh (3.35 Ah x 3.60 V) and 50 g a cell, on sheet 3.1, 3.3 and 3.10;
- the places 39 / 56 / 61, so at most 60 / 80 / 84 cells;
- "several times" is withdrawn and replaced by figures (see minor 3 for the cell multiple).

**The improvements (section 8b).** Two rows were recomputed exactly:
- the link-off load: COMB 45.6 / 48.4 %, margins 175.4 / 172.6 and 206.9 / 204.1 Wh;
- 600 Wp: 41.0 / 43.5 %, margins 109.3 / 105.1 and 140.8 / 136.6 Wh.

The service labels are right. Holding both link cards off is POWER-THERMAL.md's variant "no peer kit linked", while
PS-IDLE-SPEC is computed with the link card up, so the row reduces service. 600 Wp keeps the service but lies outside
the stated array. The 6.35 A setting is the SLUSE66A 9.6.22 clamp: its 6.45 A maximum stays under the drafted front
end's 6.935 A. The stage at 0.965 is marked a figure to establish. The 33.1 W LOW is correctly left out: it is every
load at its lowest documented figure at once, a bound and not a state.

**Reruns and hygiene.** In the clone, with the held sheets present, all seven outputs rerun byte identical:
`vbus20_range`, `curve_readings`, `energy_basis`, `weather_basis`, `plane_grid`, `reconcile_lid_panel` and
`energy_runs`. The added lines carry no U+2013 or U+2014, no host names and no user paths. "adverse" is in no output.
No ignored or held file is committed, and the diff touches only `v2/docs/records/l3plane/`. `pcb_requirements.yaml` is
untouched. The three commits are in the owner's name with no trailer.

## Independent figures beside theirs

| Figure | Theirs | Checker |
|---|---|---|
| 4S15P WE TYP / WAB (base, lid) | 74.3 (52.4, 19.4) / 19.5 (19.5, 0.0) | 74.4 (52.4, 19.5) / 19.6 (19.6, 0.0) |
| 4S14P WE TYP / WAB | 44.0 (44.0, 0.0) / NOT MET 10.8 | 44.0 (44.0, 0.0) / NOT MET 10.7 |
| 4S15P WE60; WEL (TYP / WAB) | 54.1 / NOT MET 0.6; 51.0 / NOT MET 3.7 | 54.2 / NOT MET 0.6; 51.1 / NOT MET 3.6 |
| 4S14P WE60; WEL | 23.9 / NOT MET 30.9; 20.8 / NOT MET 34.0 | 23.9 / NOT MET 30.9; 20.9 / NOT MET 33.9 |
| WA 4S15P; 4S14P; 4S9P | NOT MET 41.5/93.2; 71.8/122.0; 192.1/246.8 | NOT MET 41.4/93.2; 71.8/121.9; 192.1/246.8 |
| 4S9P WE; WEL | NOT MET 169.2/176.1; 169.2/177.2 | same |
| WE band, 4S15P COMB; least point | 30 to 50, S to 15 W; 5.3 Wh at 50/+15 WAB | same map; 5.4 Wh |
| Coverage 4S14P WE TYP: STOP / COMB / EACH | 166 / 164 / 115 | 166 / 164 / 115 |
| Coverage 4S14P WE WAB | 121 / 114 / 85 | 121 / 114 / 85 |
| Coverage 4S15P WE TYP | 190 / 186 / 141 | 190 / 186 / 141 |
| Coverage 4S15P WE WAB | 151 / 146 / 108 | 152 / 146 / 108 |
| Coverage NOM TYP 4S14P; 4S15P | 207/200/145; 235/232/177 | same |
| Coverage WE-LO TYP 4S14P; 4S15P | 118/114/79; 139/136/104 | same |
| Coverage WE-MKR TYP 4S14P; 4S15P | 215/212/147; 255/252/188 | same |
| Coverage 4S9P, every case | 0 | 0 (four cases run) |
| Sizing TYP: (i) / 50 / 80 / 95 % | 619.0 / 981.8 / 1331.0 / 1688.9 Wh | 618.8 / 981.6 / 1331.0 / 1688.7 Wh |
| Sizing WAB | 676.2 / 1055.5 / 1420.6 / 1760.5 Wh | 676.1 / 1055.3 / 1420.4 / 1760.3 Wh |
| Cells for 50 / 80 / 95 %, TYP; WAB | 132 / 168 / 228; 136 / 192 / 232 | same by the page's method; 128 / 172 / 220; 136 / 184 / 228 by the count's percentile |
| Multiples of the 4S21P (usable Wh); in cells | 1.42 to 2.54; not given | 1.42 to 2.54; 1.57 to 2.76 |
| Link-off coverage COMB 4S14P / 4S15P | 45.6 / 48.4 % | 45.6 / 48.4 % |
| 600 Wp coverage COMB | 41.0 / 43.5 % | 41.0 / 43.5 % |
| Cell resistive bound, base; lids | 0.9915; 0.9933, 0.9937 | 0.9924 to 0.9925; 0.9933, 0.9937 |
| Step error at WE restated (1 h against 0.01 h) | not re-measured | at most 0.1 Wh |

Rerun from this folder against a checkout of `fnd/l3plane` with the held files present (pure Python, about a minute
each): `python3 indep_round2.py <checkout>` and `python3 indep_round2b.py <checkout>`.
