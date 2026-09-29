# a1solar running log (MESHSAT-1357, stream a1solar, author session of 29 September 2026)

Prototype design: nothing bought, built or measured. AI work; times CEST.

- 03:40 read the brief, WORKER-RULES, the coordinator's README (state 02:45), energy section 9 (9g way (i)), section 4
  (panel model and performance ratio), energy_inputs.yaml's solar block, a1elec's CHARGER.md and TOPOLOGY.md (on
  fnd/a1elec, read with git show), gen_sch_e.py's tracker stage (J_SOLAR, F2, D4, C11 to C15, Q3, R8/R9 FBIN 17.6 V,
  TRK_OUT 15.1 V) and REQ-016 (100 W, 25 V cold Voc, 17.6 V, F2 and J_SOLAR 10 A). Deadline 05:40 with everything committed.
- 03:45 filed under v2/vendor/solar/ with sources.txt lines: Renogy RNG-100DB-H sheet (2018, retailer copy), SunPower
  SPR-E-Flex-100 datasheet 523809 Rev D and the flex Safety and Installation Instructions 524958 Rev F (the maker's 1.25
  clause on Isc and Voc, IP67 box, -40 to +85 C, the 45 V system voltage and the not-IEC-certified note), PowerFilm's
  120 W foldable sheets (15.4 V F16-7200 and 30.8 V), and a transcription of BLUETTI's PV420 page (no VMPP, no
  coefficient, -10 to +65 C). Renogy's own page renders by script: no current sheet from the maker's site.
- 03:52 array_calc.py written and run (2.6 s, exit 0): the six candidates, every wiring near 400 Wp, single-diode fits
  (Victron and SunPower exact, Renogy by the Rs = 0 fallback, the two PowerFilm a-Si panels not fitted because a no-shunt
  model misplaces their fill factor), the fixed-voltage ratio on the September mean day. First reading: 2S2P of the
  Renogy holds 0.9913 of the MPP energy at its best fixed point (33.9 V) with a 5 m lead; 4P at board E's 17.6 V holds
  0.9517; flat panels get 0.7936 of the 40 degree plane in September. The DRcalc mean-day file is copied from fnd/a1elec
  into inputs/ (same sha256 as energy_inputs.yaml names). a1elec's energy_two_pack.py reproduced byte-identical from a
  scratch root (symlinks to this worktree plus fnd/a1elec's folder at 06568798).
- 03:53 energy_runs.py written and run (0.7 s, exit 0, two runs byte-identical, exit 3 without a1elec's script): both
  scripts' published design-case figures reproduced first (91.0 / 26.8 Wh; 31.1 Wh), then run at the 2S2P drafted point
  (R8 205k / R9 7.50k, 34.14 V): ratio 0.9910, PR 0.9332, all at once 0.9078; flat panels 0.7406. Both design cases
  still MEET at 0.9332 and 0.9078 (two-pack lowest 30.7 and 29.8 Wh, the lid's own margin 0.5 and 0.0 Wh); flat panels
  do NOT meet the two-pack case (stops at h 47 / 36, 82.8 Wh unserved). The packs are full by early afternoon, so a few
  percent of ratio moves the lowest point by under 2 Wh; the plane (deployment angle) is the lever that matters.
- 03:55 SELECTION.md committed (design basis A1SOLAR-01: four Renogy RNG-100DB-H in 2S2P, authority SESSION). Found
  while writing it: SunPower's own 45 V maximum system voltage excludes its 2S2P (48.1 V cold); BLUETTI's range stops at
  -10 C; the PowerFilm 15 V model also keeps REQ-016's 25 V (24.86 V).
- 03:57 ARRAY.md committed. Found while writing it: board E's F2 is a MINI 297 class blade, 32 V DC by the held
  Littelfuse sheet, so a 2S2P array needs another fuse type; D5 (BAT54, 30 V) blocks about the input voltage; the wall's
  solar pair and its 18 AWG lead are sized for 10 A.
- 03:58 README.md replaces the coordinator's state record; apply_records_readme_row.py drafted and tested on a scratch
  copy of v2/docs/records/README.md (one row added; second run refused, exit 2), not run in the tree.
- 03:59 SunPower's installation guide Rev A filed beside Rev F (entry added in the second issue; the first issue's log
  had none for commit c90e10f4).
- 04:01 the plane's tolerance: PVGIS MRcalc for slopes 10 to 90 degrees (2015 to 2020, the pinned file's period) and
  PVcalc at 40 degrees for azimuths 0, +-45, +-90 (MRcalc takes no azimuth; its four aspect answers were identical to
  the optimum and were deleted unfiled) filed under v2/vendor/solar/pvgis-planes/ with sources lines. energy_runs.py
  section 6 (pinned): the two-pack case meets down to 0.8590 of the 40 degree plane's September irradiation (0.8831 in
  the adverse case); flat, vertical and east or west facing fail; slopes 30 to 60 within 45 degrees of south pass even
  combined and adverse (worst product 0.899). Scaling the 40 degree mean-day shape is an approximation, labelled.
- 04:02 array_calc.py section 11, the fit sensitivity: a second Renogy fit with its maximum at the maker's 18.9 V gives
  0.9914 for 2S2P at 34.14 V (first fit 0.9910); sections 0 to 10 unchanged, energy_runs.out unchanged. ARRAY.md 1 and 7
  and README updated with the fit check and the deployment rule (30 to 60 degrees, within 45 degrees of south).
- 04:03 review pass over SELECTION.md, ARRAY.md and README (the fuse sentence, the worst corner 0.899, the 400 Wp's
  source, the file lists, the certification note's date). Stopped with everything committed; no process left running.
  Open for the integrator: merge after fnd/a1elec (energy_runs.py finds energy_two_pack.py in the tree then), run
  apply_records_readme_row.py, hand ARRAY.md 6 to board E's writer and ARRAY.md 5 to the owner's sheet.

## Second issue, after the independent AI check of 9f93a9fc (mergeable no: 2 blocking, 10 minor)

Labels above corrected from the commit times (check minor 9). SUPERSEDED in the entries above: the 04:01 plane rule
(slopes 30 to 60 within 45 degrees of south, from factors multiplied on a scaled day; check B1), the adverse ratio 0.9078
of the 03:53 entry (check B2) and the filing of SunPower's documents (minor 8).
- 04:22 read the check record and the coordinator's list (90 minutes, to 05:51).
- 04:23 49 PVGIS DRcalc answers fetched for the grid (slopes 0 to 70 by 10, azimuths -45 to +45 by 15); the 40/0 answer
  came back byte-identical to the anchor file.
- 04:28 array_calc.py: the hotter cells' own MPP loss printed and charged in the adverse case (model 0.9765, maker's
  0.9778, the lower charged), the set-point window with R8 and R9 at 1 percent, the Rs 0.1 and 0.2 ohm fits (0.9866 to
  0.9923 at the draft), the E96 divider choice (232k over 8.45k, 34.29 V, best worst case), REQ-016 at -20 and -40 C.
  energy_runs.py rewritten: B typical 0.9326, C adverse 0.8573; both design cases MEET at 40/0 (two-pack 30.7 and 27.9
  Wh); the grid on each plane's own day: both cases meet at 20 to 50 degrees within 15 degrees of south, flat meets in
  neither. The MRcalc and PVcalc proxy answers of 04:01 removed with their sources lines. Committed 4c611d51 (04:28).
- 04:30 SunPower's three documents held back by their terms (git rm; `v2/vendor/solar/held/` ignored; fetch_held_back.py
  tested into a scratch folder, all three sha256 matched; array_calc.py identical with them present and absent), a
  publication decision per file in sources.txt, the pinned monthly PVGIS file given its missing sources line, `solar` in
  vendor-status.txt and the vendor README. Committed 6fa0f576 (04:30).
- 04:33 ARRAY.md, SELECTION.md and README restated: the plane grid's rule, the corrected adverse figures, the 20 A fuse
  and the entry at or above it, F2's DC interrupting rating, the gate on REQ-016, the -40 C reading, the maximum valley
  threshold and the missing current sense for board E's writer, "on this model" where a result is stated.
- 04:34 array_calc.py section 3's note corrected (the model's Pmax slope is steeper than SunPower's, not milder than
  every maker's); the records-README row updated to the second issue and tested again on a scratch copy.
