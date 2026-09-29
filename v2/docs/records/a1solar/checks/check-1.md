mergeable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026): the independent AI check of 9f93a9fc; its items answered in the second issue. -->

# AI review: independent check of stream a1solar, fnd/a1solar at 9f93a9fc (MESHSAT-1357)

This is an AI review, not a qualified engineering review, made on 29 September 2026 at 04:20 CEST by a checker that wrote
none of the work. Read-only on the stream's files; scratch clone the checker's scratch clone at `w/a1solar` 9f93a9fc
(12 stream commits on 18863a97; merge base with `fnd/a1int` 13b5352b). Nothing here is a measurement.

## Blocking items

**B1. The deployment rule and "45 degrees east or west passes alone" do not reproduce on PVGIS's own answers for those planes.**
Files: `ARRAY.md` 154 to 161 (section 7), `README.md` 42 to 47, `SELECTION.md` 93 to 95, `LOG.md` 35 to 40 and 43,
`energy_runs.py` 217 to 280 (section 6) and `energy_runs.out` section 6.
What is wrong: the rule (30 to 60 degrees, within 45 degrees of south) rests on two approximations: slope and azimuth
factors multiplied, and the 40 degree south mean day scaled by a factor. (a) The product is off at the corner that
decides it: PVGIS PVcalc for slope 60, azimuth -45 gives 0.8782 of the 40/0 plane in September, not 0.976 x 0.921 = 0.899
(60/+45: 0.8971), which is under the adverse threshold 0.8831: the two-pack case is NOT MET there (4.7 Wh unserved).
(b) The scaling is the bigger error. Because the packs are full by early afternoon (ARRAY.md 162), what decides the
night is the afternoon's sun, and an east-turned plane loses it. Running a1elec's two-pack case on each plane's own PVGIS
DRcalc mean-day profile (the same query as the pinned file, `localtime=0`; 40/0 comes back byte-identical in September;
each profile scaled by the model's own factor 1.0078, which reproduces the model's 40/0 profile exactly) gives:
NOT MET in the TYPICAL case at 40/-45, 50/-45, 60/-45, 60/-30 and 60/+45 (40/-45 stops at hour 71; 60/-45 119.3 Wh
unserved); NOT MET in the adverse case also at 30/-45 and 50/-30. MEETS in both cases at 10 to 70 degrees facing south,
30/+-30, 40/+-30, 40/-15, 30/-15, 50/-15, 60/-15, 40/+45, 50/+30. So "45 degrees east of south passes alone (0.921)" and
every east corner of the proposed rule are wrong on the model; the stream labelled the scaling as an approximation, but
the rule offered to the owner as a CONOPS line is built on it.
Exact fix: in `energy_runs.py` section 6, replace the factor method by runs on each plane's own DRcalc profile (file the
answers under `v2/vendor/solar/pvgis-planes/` with sources lines and pins; keep the 40/0 file as the scale anchor), drop
the "factors multiply" and "meets down to 0.859 / 0.883 of the plane's irradiation" claims as proxies for other planes,
and restate the rule from the grid in ARRAY.md 7, README, SELECTION.md 4 and LOG. On this check's runs, 30 to 50 degrees
facing between 15 degrees east and 30 degrees west of south meets in both cases, including B2's correction (60/+30 then
fails the adverse case).

**B2. The adverse performance ratio 0.9078 does not charge the hotter mounting it names.**
Files: `energy_runs.py` 167 and 178 to 183 (case C = 0.9417 x r_all), `array_calc.py` 177 to 181 (`e_hw / e_mpp_h`),
`ARRAY.md` 72 to 73 and 144 to 148, `README.md` 38 to 41, `LOG.md` 23 to 24.
What is wrong: "everything adverse at once" includes cells 10 K hotter than the NOCT model, but the ratio divides by the
maximum-power energy at those same hotter cells, so only the fixed point's extra penalty is charged; the panel's own loss
at the hotter cells (Renogy p.2: Pmax -0.42 %/K) is not, and PVGIS's 0.9417 carries only a free-standing mount's
temperature. On the September mean day that loss is a factor 0.9782 (maker's coefficient; the model gives 0.9765), so the
adverse ratio is about 0.888, not 0.9078. Verdicts: the two-pack case at 40/0 still MEETS (29.1 Wh, lid 0.0 Wh; 4S18P
89.0 / 24.8 Wh), but the adverse threshold for other planes moves from 0.8831 to 0.9027, which fails even the stream's
own product corner (0.899) and 60/+30 on its own profile.
Exact fix: multiply case C by the MPP-energy ratio hot over typical (print it in `array_calc.out` 6 and `energy_runs.out`
1), or drop the +10 K from the adverse case with a stated reason; re-run and restate 0.9078, 29.8 Wh and 0.883 wherever
quoted, and use the corrected adverse case in B1's grid.

## Minor items

1. `ARRAY.md` 132 and 133 (TRK_OUT, L1): the current-limit arithmetic uses the MINIMUM buck valley threshold (69 mV,
   8705af p.3); the MAXIMUM (102 mV) sets the stress: 20.4 A valley, peak about 24.6 A from 34.1 V and 25.7 A from 51.3 V
   at 15.1 V out, against the XAL1510-103's Isat 26.3 A (30 percent drop, 25 C, typical) and Irms 22 A (40 K rise), so
   "L1 unchanged" is not shown. The netlist ties CSPIN and CSNIN to PV_P and CSPOUT and CSNOUT to TRK_OUT: board E senses
   no input or output current, so the "200 W window" (ARRAY.md 80) is not a limit the stage implements. Add both to the
   writer's list.
2. `ARRAY.md` 37 to 43, `array_calc.py` section 11: both Renogy fits have Rs = 0. Fits through the maker's points with
   Rs 0.1 and 0.2 ohm (n 1.31 and 1.09 a cell) give 0.9916 and 0.9847 at the drafted 34.14 V (best points 34.6 and 35.3 V),
   so "the fixed-point ratio it gives errs low" is not shown for the drafted point. Add an Rs > 0 bracket and state the
   range; 34.6 to 34.9 V keeps 0.988 to 0.993 across the three fits on this check's runs.
3. `ARRAY.md` 88 to 93, `README.md` 54 and 63: F2 "at least 18.4 A (a 20 A value)" with J_SOLAR, the wall pair and the
   lead "at least 18.4 A": rate them at or above the fuse actually chosen; and state F2's interrupting rating at its DC
   voltage against the kit-side fault current (the MINI 297 is 1000 A at 32 VDC; SunPower 524958 Rev F p.2 footnote).
4. `ARRAY.md` 117 to 137, `README.md` 50 to 57: the drafts (PV_IN and PV_P at v_max 56.3 V and 34.14 V) contradict REQ-016's
   acceptance as written (declared at 25 V, 17.6 V). Add the gate: not applied to `gen_sch_e.py` before the owner restates
   REQ-016. A1SOLAR-01's `reversed_by` names the owner ruling, but the record should say the 2S2P basis stands only once
   REQ-016 is restated (1S4P SunPower remains a standing option); it is not entered in `tools/pcb_decisions.yaml`.
5. REQ-016 says "the panel's coldest operating temperature"; the stream reads the envelope's -20 C (pcb_envelope.yaml
   in_use min). State that reading: at the panels' own -40 C floor the SunPower gives 25.23 V and PowerFilm's 15 V model
   26.17 V, so "admits the SunPower" (README 65, ARRAY.md 112, SELECTION.md 63) holds only under it.
6. `ARRAY.md` 70: the set-point window 33.55 to 34.74 V omits R8 and R9's 1 percent (about 32.9 to 35.4 V with it).
7. `v2/vendor/vendor-status.txt` has no `solar` line and `v2/vendor/README.md` no `solar/` row (kb_verify reads an
   undeclared folder as FAIL). Add both at merge.
8. Publication (every `v2/vendor/solar/` file, below): no file states a redistribution grant. The two SunPower guides
   carry "All rights reserved" and are distributors' copies; datasheet 523809 Rev D is a distributor-branded issue; the
   Renogy sheet is a retailer's copy. They match the folder's standing practice (makers' published documents as-is,
   takedown on request), so none is judged unpublishable, but record the decision per file in `sources.txt` under the
   27 September rule, and consider citing the superseded Rev A by URL and sha256 instead of filing it.
9. `LOG.md`: the 04:05 and 04:08 entries were committed at 04:01 and 04:02 (ff73bec5, de50396a), and 04:04 follows
   04:08. Correct the labels from the commit times.
10. No verification claim beyond analysis was found; REQ-016 and REQ-072 are untouched (the stream's diff is
   `records/a1solar/`, `vendor/solar/` and `sources.txt` only). "No tracking loop is needed" (ARRAY.md 81) is a model
   result; say "on this model" there as section 3's bullet does.

## Reproduced

- `python3 v2/docs/records/a1solar/array_calc.py` from the clone root: exit 0, 1.2 s, output byte-identical to
  `array_calc.out`.
- `A1ELEC_ROOT=<scratch root> python3 v2/docs/records/a1solar/energy_runs.py`: exit 0, byte-identical to
  `energy_runs.out`. Root `the checker's scratch root`: symlinks to the clone's `v2/vendor`, `v2/ecad` and each
  `v2/docs/records/*`, plus `energy_two_pack.py`, `.out` and its input from `git show w/a1int:...` (sha256 81694b2b...,
  the pin); `energy_two_pack.py` there reproduces its own `.out` byte for byte. Without the root: exit 3, as documented.
- `apply_records_readme_row.py --file <copy>` on scratch copies of `v2/docs/records/README.md` from w/a1solar, w/a1int and
  origin/main: one row added each time. Every `sources.txt` sha256 matches its file (BLUETTI's names the HTML read).
- Checker's own runs (scratchpad scripts importing the stream's modules unchanged): PVGIS 5.2 PVcalc and DRcalc for
  Leiden at the planes named in B1 (live queries of 29 September; the 40/0 answers equal the filed ones), the two-pack
  case on each plane's profile, the hot-mount factor, and the Rs bracket of minor 2. No dash characters and no host
  names, user paths or addresses in the stream's text files (makers' own addresses in their sheets only).

## Figures checked

| claim | source | checker's value | agrees |
|---|---|---|---|
| Renogy 100 W, Vmp 18.9 V, Imp 5.29 A, Voc 22.5 V, Isc 5.75 A | renogy sheet p.2 | same | yes |
| Renogy -0.42 / -0.31 / +0.05 %/K, NOCT 45 +- 2 C, -40 to +85 C | p.2 | same | yes |
| Renogy 600 VDC, series fuse 15 A, box IP68, connectors 30 A 1000 V IP67, 1.9 kg | p.2 | same (Class A; CE, TUV logos) | yes |
| cold Voc 2S at -20 C cells 51.28 V | p.2; envelope in_use min -20 C | 2 x 22.5 x 1.1395 = 51.28 | yes |
| rating basis 56.25 V by the 1.25 clause | SunPower 524958 Rev F p.1, 3.0 | clause text as quoted | yes |
| hot Isc 11.76 A, x1.25 14.70 A, x1.25 18.37 A | p.2 | same (envelope +40 C gives 71 C cells: +0.06 %) | yes |
| back-feed 7.35 A (2S2P), 22.05 A (1S4P) against 15 A | p.2 | same | yes |
| 4S cold Voc 102.55 V over 80 V | 8705af p.2 VIN 80 V, SW1 81 V | same | yes |
| FBIN 1.184 / 1.205 / 1.226 V: 33.55 / 34.14 / 34.74 V | 8705af p.4 | same (resistor tolerance omitted, minor 6) | yes |
| buck valley threshold 69 mV gives the limit | 8705af p.3: 69 / 86 / 102 mV | max 102 mV sets stress | no (minor 1) |
| ratio 0.9910, FBIN 0.9866, all at once 0.9640 | energy_runs.out 1 | reproduced; Rs > 0 fits 0.9847 to 0.9916 | yes, bracket owed |
| adverse PR 0.9078 | 0.9417 x 0.9640 | about 0.888 with the hot-mount loss | no (B2) |
| design cases 90.7 / 26.5 Wh; two-pack 30.7 Wh, lid 0.5; adverse 29.8, lid 0.0 | energy_runs.out 3, 4 | reproduced | yes |
| flat 0.7936, two-pack NOT MET 82.8 Wh | pinned monthly Sept 95.57 / 120.42 | reproduced | yes |
| rule corner 60/-45: 0.899 | PVGIS PVcalc 60/-45 | 0.8782 (60/+45 0.8971) | no (B1) |
| 45 degrees east passes alone | PVGIS DRcalc 40/-45 own profile | NOT MET, typical case | no (B1) |
| REQ-016: 25 V cold Voc, 17.6 V, 100 W; F2, J_SOLAR 10 A | pcb_requirements.yaml REQ-016 statement, acceptance | same | yes |
| F2 MINI 297 32 VDC | littelfuse-297-ficcorp.pdf p.1 | 32 VDC, 1000 A interrupting | yes |
| Q3, Q4 60 V; C11, C12 35 V; C13 to C15 50 V; D4 SMCJ28A; D5 BAT54; J_SOLAR 10 A; R8 102k | gen_sch_e.py 436 to 627; pcb-e1-dock-e7 netlist | same; PV_P also carries R8, R14 (0603), TP5, U5 32 to 34 | yes |
| SunPower 100 W, 17.1 V, 5.9 A, 21.4 V, 6.3 A, -58.9 mV/K, 2.6 mA/K, 45 V, 15 A | 523809 Rev D p.1 | same | yes |
| SunPower Rev A 17.5 V, 21 V, 6.2 A, 45 V; Rev F cell left to the certification note | 524958 Rev A p.2, Rev F p.2 | same | yes |
| PowerFilm 15.4 V, 7.2 A, 21.9 V, 9.1 A; -0.300 / +0.109 / -0.200 %/K; 2.9 kg | F16-7200 sheet p.2 | same | yes |
| PowerFilm 30 V: 30.8 V, 3.6 A, 43.7 V, 4.6 A, part F32-3600 | 30V sheet p.2 | same | yes |
| Victron 150W-12V: 18.2 V, 8.25 A, 22.3 V, 8.69 A; -0.45 / -0.35 / +0.04 %/K; 1000 V; 11 kg | Victron sheet p.1 | same | yes |
| 4 x RNG-100DB-H: 7.6 kg, 2.7 m2, 52.6 Wp/kg | p.2 | 7.6 kg, 2.68 m2, 52.6 | yes |

Publication, per file (all under `v2/vendor/solar/`): Victron sheet (maker's site; no terms on file); Renogy 2018 sheet
(retailer's CDN copy of the maker's sheet; no terms); SunPower 523809 Rev D (distributor autosolar.es, Ecobat-branded;
no terms); SunPower 524958 Rev F and Rev A (distributors solarrun.com.au and unboundsolar; "All rights reserved", no
grant); PowerFilm two sheets (maker's site; no terms); BLUETTI (a transcription of specification facts, page not filed);
PVGIS answers under `pvgis-planes/` (JRC data, reuse with attribution, stated in each line). None states a prohibition;
see minor 8.
