mergeable: yes
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026): the focused re-check of 066e6b97; N1 to N3 answered by records/a1int/apply_a1solar_minors.py, N4 labelled in energy_runs.out. -->

# AI review: focused re-check of stream a1solar, fnd/a1solar at 066e6b97 (MESHSAT-1357)

This is an AI review, not a qualified engineering review, made on 29 September 2026 at 04:41 CEST by the checker of
`CHECK.md` (9f93a9fc), who wrote none of the work. Read-only: the scratch clone was detached at `w/a1solar` = 066e6b97
(five commits after 9f93a9fc: 4c611d51, 6fa0f576, 69480571, 6e1d72ac, 066e6b97). Nothing here is a measurement.

**Merge condition (not a defect of the content):** the merge must be a squash of **559a072d..066e6b97**, the stream's 13
commits with 18863a97 included, on every step to `main` (fnd/a1int, then main). The branch must never be merged with its
history or pushed. See answer 5: the range 18863a97..066e6b97 named in the request does not apply.

## Blocking items

None. B1 and B2 of `CHECK.md` are answered and reproduce; minor items 1 to 10 are answered as the record says.

## Answers

**1. B1, the planes.** Both scripts reproduce byte for byte (commands below). `energy_runs.py` section 6 loads each
plane from its own filed PVGIS DRcalc answer: `plane_file()` names the file; the loader asserts the file's own slope and
azimuth; all 49 files are sha256-pinned, and every pin matches with none left unpinned. The 40/0 plane is the anchor
input. The script refuses (exit 4) unless the anchor, scaled by 1.007820, reproduces the model's September profile. It
also computes each plane's typical and adverse ratios on that plane's own day and cell temperatures.
Live PVGIS spot checks: 30 of the 49 filed answers are byte-identical to answers I queried from PVGIS myself (25 before
the stream filed its own, 5 fresh at 04:35). They include the east planes 60/-45, 50/-45, 40/-45, 30/-45, 10/-45, 70/-30,
60/-30, 50/-30, 20/-15 and 60/-15.
An independent run of six grid cells with my own fit and composition code, on the live profiles, gives the stream's
verdicts and lowest points exactly:
- 20/-15: 31.6 / 3.3 Wh.
- 60/+15: 27.1 / 9.5 Wh.
- 40/+30: 29.3 / 15.5 Wh.
- 60/-15, 50/+30 and 70/0: NOT MET in the adverse case.

The restated rule follows from the output table (`energy_runs.out` 6). Both cases meet at:
- slope 20: -15, 0, +15;
- slopes 30 and 40: -15 to +30;
- slope 50: -15, 0, +15;
- slope 60: 0 and +15.

Flat, 10 and 70 meet in neither case. So "20 to 50 degrees within 15 degrees of south" is a rectangle whose every grid
point meets both cases. The rule is stated as a model result in ARRAY.md 7 ("on this model"), SELECTION.md 4 ("on this
model") and README's "shown at desk (model and arithmetic, not measurement)" block. The README's CONOPS line (line 83)
does not say so: minor N3. The withdrawn proxies (multiplied factors, the scaled day, 0.859 / 0.883 / 0.899, 30 to 60
within 45) appear only as history, marked withdrawn.

**2. B2, the adverse case.** The composition is right, and the hotter cells are not counted twice. `Ratios.adverse()`
takes the worst of three things:
- the three fits (Rs 0, 0.1, 0.2 ohm);
- the window's two ends (33.05 and 35.57 V);
- the fixed energy at NOCT +10 K through a 10 m lead, over the maximum-power energy at the SAME hot cells: 0.9322.

It then multiplies by the hot over typical maximum-power energy (model 0.9765, maker's -0.42 %/K 0.9778; the lower is
charged). The product is fixed energy at hot cells over maximum-power energy at typical cells. I recomputed it directly
per fit, without the factorisation, and got the same 0.9103. Then 0.9417 x 0.9103 = 0.8573. PVGIS's 0.9417 carries only
the free-standing (typical) temperature, so the +10 K loss is charged once. Reproduced at 40/0:
- two-pack adverse case: MEETS, 27.9 Wh, lid 0.0 Wh, down to a lid at +10.8 C;
- 4S18P: 87.8 / 23.7 Wh (+20 / +15 C).

**3. Minor items.** All ten are answered as the record says:
1. The maximum valley threshold of 102 mV and the ~130 mV rise at higher duty are in the draft (8705af p.22 confirmed),
   and L1 is "not shown adequate". The missing current sense is stated: on the QFN, pins 30 and 31 (CSNOUT, CSPOUT) are
   on TRK_OUT and 32 and 33 (CSNIN, CSPIN) on PV_P (8705af pin functions, netlist confirmed). The 200 W window is the
   model's clip.
2. There is an Rs > 0 bracket (0.9866 to 0.9923 at 34.29 V), and "errs low" is withdrawn.
3. The fuse is 20 A, with J_SOLAR, the wall pair and the lead at or above it, and F2's DC interrupting rating is a need.
4. The gate is written in README 56 to 58, the ARRAY.md header and section 6, and SELECTION.md 4. A1SOLAR-01 "stands
   only once REQ-016 is restated", 1S4P SunPower stays a standing option, and the decision is not entered in
   `pcb_decisions.yaml` before the owner's ruling. REQ-016 and REQ-072 are untouched.
5. The -20 C reading is stated, and the -40 C figures are in `array_calc.out` 13 (54.07, 25.23, 26.17 V, all
   recomputed).
6. The window with 1 percent resistors is 33.05 / 34.29 / 35.57 V (recomputed).
7. `solar current` is in vendor-status.txt, and the README row agrees with it under kb_verify's rule (no "kept for the
   record").
8. Every `solar/` line of sources.txt has a publication decision. The three SunPower documents are held back ("All
   rights reserved" and a re-branded issue) and fetched by sha256 into the ignored `held/`. The other lines' sha256
   values match their files.
9. The LOG labels match the commit times (04:01, 04:02, 04:03; second issue 04:28 to 04:34).
10. "On this model" is present where results are stated.

**4. New in the corrections.** Nothing that sets a rating or a verdict. The minor points are N1 to N4 below. Scans: no
dash characters in the changed text files or `.gitignore`, no host names, user paths or addresses (but see N2 for the
scratch-path citation). Changes outside the stream's folder are limited to `.gitignore` (the `v2/vendor/solar/held/`
line), `v2/vendor/README.md`, `vendor-status.txt` and `sources.txt`. The authors are the owner, with no trailer.
`apply_records_readme_row.py` adds one row on copies from w/a1int and origin/main and refuses a second run (exit 2).

**5. The SunPower PDFs and the squash.**
- **With the history kept**, these would reach the public mirror:
  - `sunpower-spr-e-flex-100-datasheet-523809-revd.pdf` (989,926 bytes) and
    `sunpower-flex-safety-installation-524958-revf.pdf` (278,154 bytes), both added in ab7f85d2;
  - `sunpower-flex-safety-installation-524958-reva.pdf` (242,086 bytes), added in c90e10f4;
  - all three deleted in 6fa0f576.

  The twelve MRcalc and PVcalc JSONs the stream later removed would also be kept. They are PVGIS data (reuse with
  attribution), so they are harmless.
- **Where the branch is now:** GitLab `origin` holds only `main` (`ls-remote`), and ab7f85d2 is in neither w/a1int nor
  origin/main. So nothing of the branch is public yet.
- **Which files a squash leaves:** the net diff has no SunPower path, and neither 18863a97's tree nor 066e6b97's tree
  holds one.
- **But 18863a97..066e6b97 is the wrong range.** 18863a97 itself (the Victron sheet, its sources line, the first
  README) is in neither w/a1int nor main. A patch of that range fails on both lines (README.md not in the index;
  sources.txt context at line 389). Even applied by hand, it would drop the Victron PDF that `array_calc.py` pins (exit 3).
- **The right range is 559a072d..066e6b97 (18863a97's parent).** `git apply --cached --check` against temporary indexes
  shows it applies cleanly to both w/a1int and origin/main. It carries no SunPower file.
- **Do not use `git merge --squash fnd/a1solar` onto fnd/a1int.** It would also carry d41f85ec..559a072d, the set 10
  re-take commits that are on main but not on a1int, because the merge base is 13b5352b.

## Minor items (new)

- N1. ARRAY.md 80 and `array_calc.py` 64 call 232k over 8.45k "the best worst case". But 187k over 6.81k prints 0.9663
  against 0.9662 (`array_calc.out` 12): the two ratios agree to 0.02 percent. Say "equal best".
- N2. README 4, ARRAY.md 4 and SELECTION.md 3 cite `_scratch/chk-a1solar/CHECK.md`, a local scratch path that is not in
  the repository. File `CHECK.md` and `CHECK-2.md` under `v2/docs/records/a1solar/checks/`, as a1elec's checks were on
  fnd/a1int, and cite them there.
- N3. README 82 to 84 (the CONOPS line) should say it is the grid's model result. The rule's thinnest margins should be
  stated where it is quoted: 20/-15 adverse 3.3 Wh, 50/-15 8.9 Wh, 20/+15 9.5 Wh. Planes between grid points are not
  run (stated).
- N4. PVGIS's non-thermal losses of the 40/0 plane (angle of incidence, spectrum) are kept for every plane. This is
  labelled in `energy_runs.out` 6. At 20 degrees or turned 15 degrees they differ a little; the bench item 5 harvest
  comparison covers it.

## Reproduced

- `python3 v2/docs/records/a1solar/array_calc.py` from the clone root: exit 0, 1.5 s, byte-identical to `array_calc.out`
  (`held/` absent).
- `A1ELEC_ROOT=the checker's scratch root python3 v2/docs/records/a1solar/energy_runs.py`: exit 0, 8.4 s, byte-identical
  to `energy_runs.out`. The root is the one of `CHECK.md`: symlinks into the clone, plus a1elec's pinned script from
  w/a1int. Without the root the script exits 3 as documented.
- Checker's own scripts in the scratchpad: live PVGIS DRcalc queries, the six-cell grid, the direct B2 composition, and
  the patch-apply checks of both squash ranges with a temporary index. The clone's own index and tree are untouched
  apart from this file.

| claim | source | checker's value | agrees |
|---|---|---|---|
| window 33.05 / 34.29 / 35.57 V (232k / 8.45k, 1 %) | 8705af p.4 FBIN; E96 | same | yes |
| typical ratio 0.9903, PR 0.9326 | energy_runs.out 1, 2 | same | yes |
| adverse 0.9322 x 0.9765 = 0.9103, PR 0.8573 | energy_runs.out 1, 2 | direct per-fit 0.9103 | yes |
| two-pack 40/0: typical 30.7 Wh (lid 0.5), adverse 27.9 Wh (lid 0.0) | energy_runs.out 4 | same | yes |
| 4S18P adverse 87.8 / 23.7 Wh | energy_runs.out 3 | same | yes |
| plane grid verdicts (six cells) | own PVGIS profiles | same verdicts and Wh | yes |
| rule 20 to 50 degrees within 15 degrees of south, flat none | energy_runs.out 6 | follows | yes |
| Voc at -40 C: 54.07 (2S2P), 25.23 (SunPower 1S4P), 26.17 V (PowerFilm 15 V) | makers' coefficients | same | yes |
| buck valley 69 / 86 / 102 mV, ~130 mV at higher duty | 8705af pp.3, 22 | same | yes |
| QFN pins 29 EXTVCC, 30 CSNOUT, 31 CSPOUT, 32 CSNIN, 33 CSPIN, 34 VIN | 8705af pin functions; netlist | same | yes |
| L1 ripple 4.18 A (34.29 to 15.1 V, 10 uH, 202 kHz) | arithmetic | 4.18 A | yes |
