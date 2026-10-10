accepted: yes
tip: cd8720a1ab6eed891b1afd8b5df3b8ceedf36c0f

# CHECK-5: delta confirmation of the energy basis's final issue (fnd/l3plane, MESHSAT-1357)

**An AI check, not a qualified review.** 30 September 2026, 04:40 CEST.
- **The tip** is `cd8720a1ab6eed891b1afd8b5df3b8ceedf36c0f` on `fnd/l3plane`, confirmed with `git rev-parse`. Its
  parent is `a751e4d8`, on `06b8ecea` (CHECK-4, accepted: yes).
- **Scope:** only `git diff 06b8ecea..cd8720a1`, against CHECK-4's minors 1 to 5. The checker wrote none of it.
  Prototype design: nothing is built, powered or measured.
- **The clone:** a shared clone at the tip (`_scratch/chk-energy5`, removed after the check), with the int16 worktree's
  held files copied in as ignored files and never committed.
- **The checker's figures:** `indep_round5.py` (output beside it), on the checker's own balance. No record script is
  imported.

## Blocking items

None.

## Minors

1. **Bench row 7b.7 as written is the closure test.** It checks that VIN_RAW settles above 12 V and FE_PGOOD never drops
   when a source steps below U3's demand. That confirms the correction. It confirms A-2 itself only if it is first run at
   E1's fixed 4.15 A, where the collapse is expected. One clause in 7b.7 ("run first at E1's setting, then with the
   VIN_RAW rule") makes "7b.7 confirms it" literal.
2. **Cosmetic:** the printed "5.20 / 1.025 = 5.077 A" divides the unrounded 5.204 A. With the displayed 5.20 A it is
   5.073 A. The 5.05 A step is unaffected.

## What holds

**1. The derated variant.**
- **The setting.** U3 is at 4.00 A: maximum 4.100 A. The margin is +0.052 A on 0.060 A of other loads and +0.033 A on
  0.079 A, recomputed. 4.05 A (+0.001 / -0.018 A) is kept only as the reason it was not chosen, in R11-DEPENDENCY 2a,
  `r11_dep.out` 3 and the `three_cases.py` constant.
- **The re-run.** The energy was re-run at 4.00 A (NOM) and 3.90 A (WE). On the checker's balance, with U3's efficiency
  bracketed because it is not recomputed:
  - NOM, U3 0.9810 to 0.9815: 4S15P 369.4 to 370.1 / 395.7 to 396.4 Wh against 369.9 / 396.2; 4S14P 400.4 to 401.1 /
    426.7 to 427.4 against 400.9 / 427.2; 4S9P 537.7 to 538.5 / 565.5 to 566.2 against 538.3 / 566.0;
  - WE, U3 0.9750: 4S15P 463.8 / 489.7 against 462.9 / 488.9; 4S14P 494.6 / 520.5 against 493.7 / 519.7.
  
  Every verdict is NOT MET.
- **Coverage** at 4.00 A NOM, TYP: 0 / 0 / 0 of 864 for each lid, recomputed.
- **Labelling.** It is "coordination only" throughout: R11-DEPENDENCY 0, 1 and 2a, the `three_cases.py` docstring,
  `three_cases.out` and ENERGY-BASIS section 0. No stale 4.05 A derated figure remains. The one 4.05 A left in a table is
  the as-drawn case's INFERRED WE minimum, 4.15 minus 0.1 A, which is correct.

**2. L1's schedule.**
- **The register setting** is 5.05 A, the 50 mA step at or under 5.204 / 1.025 = 5.077 A.
- **Its maximum** is 5.176 A. With 0.060 A of other loads, the front end draws 13.07 A at 9 V.
- **The peak**, with L at minus 20 % and Isat's 30 % drop, is 15.68 A: 89.6 % of the typical 17.5 A. Recomputed.
- **5.20 A** is described as U3's actual input at 90 %, not a setting.
- **The caveat** that it rests on the 25 C Isat and is recomputed once C-5 is held is on the page, in `.out` 6 and in 7a.5.

**3. The collapse-bound notes.** They sit in R11-DEPENDENCY B-5, ENERGY-BASIS section 0 and the `three_cases.py`
docstring, and each checks against its source:
- **The restart latch.** gen_sch_a.py (the U34 note) reads: "a restart waits for the bleed (0.6 to 1.2 s) plus the soft
  start (0.4 to 1.3 s), so a dip under 8 V interrupts charging for about 1 to 2.5 s".
- **U3's reset.** SLUSE66A p.80 (9.6.22) reads: "Upon adapter removal, the input current limit is reset to the default
  value of 3.25 A". p.26 reads: "when adapter is removed IIN_HOST will be reset one time to 3.25 A, under battery only host
  is still able to overwrite". 3.25 A x 20 V = 65 W. "Until the host rewrites it" matches the host's ability to rewrite
  during battery-only operation.
- **Hourly means only.** The sub-hour dip is named as the way the bound is not strict.

**4. A-2's wording.**
- 2a now reads: "A-2 is established from the netlist and the makers' documented behaviour, with its mechanism INFERRED;
  bench row 7b.7 confirms it".
- A-2 names the defect as sitting "in the E1 setting (a fixed 4.15 A), not in FW-A16 as written".
- Bench row 7b.7 exists (7b item 7: "A source stepped below U3's demand ... VIN_RAW settles above 12 V and FE_PGOOD never
  drops (A-2, B-5)"). See minor 1.
- The section heading is now "Existing defects", and A-1 is "confirmed on the makers' figures".

**5. B-2's remedies.**
- Hiccup, marked partial, "catches only parts whose peak limit sits under the fault's peak".
- Or FETs and cooling rated for the fault, for example FETs in parallel.
- "Input-side limit" is withdrawn, with the right reason: "the LM5176's one average loop senses input or output, and R11
  must sense the output" (SNVSAI1D 7.1: "configured for either input or output current limiting").
- A firmware schedule does not bound the fault.
- "Neither remedy, nor B-4's, is yet shown to fit on board A", repeated in 7a.6 and 7a.7.

**6. The output formats.**
- `energy_basis.out` and `weather_basis.out` are not in the diff: unchanged.
- `three_cases.out` keeps every line, the order and the columns. The diff changes only the derated values, two labels
  (4.05 to 4.00 A, 3.95 to 3.90 A) and the settings sentence of section 1. No table header changed.
- `r11_dep.out` rewrites the section 3 derated passage (four lines to three) and adds three section 6 lines on the 5.05 A
  setting. No header changed.
- All nine committed outputs rerun byte identical at the tip: `r11_dep`, `three_cases`, `vbus20_range`,
  `curve_readings`, `energy_basis`, `weather_basis`, `plane_grid`, `reconcile_lid_panel` and `energy_runs`.

**7. Hygiene.**
- The added lines carry no U+2013 or U+2014, no host names and no user paths.
- No ignored or held file is committed. The diff touches six files under `v2/docs/records/`, and nothing under `v2/ecad/`
  (`pcb_requirements.yaml` untouched).
- Both commits are in the owner's name with no trailer.

## Files verified at the tip

Each working-tree file equals its blob at `cd8720a1`. The outputs are the ones that rerun byte identical.

```
7bbca138a02bd32facc2a277283218c6bccc2f257c787b374fbf42483d90d132  v2/docs/records/l3plane/ENERGY-BASIS.md
c776efb8e40333e244c5e86eba531356d0b200f78b23035fc507171a9bfa837f  v2/docs/records/l3plane/PLANES.md
c4d6c05fc027a232e1c869b4c2fd2041e1fe839af3e5a10d50edb8c9bc90afdc  v2/docs/records/l3plane/curve_readings.out
dacb57cebd73d16f16f2247720de683082fb035fea170c425686c170b2afffa2  v2/docs/records/l3plane/curve_readings.py
73fd16915ddf8edf217090a4c221f879d34b5c50c4f6ddc8ff950adb6b3b2633  v2/docs/records/l3plane/energy_basis.out
7e2f19bff6b63ba5bfdb7ce430dc32e143613f2339cd1bc88e15f71dd022fb47  v2/docs/records/l3plane/energy_basis.py
686a74156ab4fc7ea8561472c4d1f9795a61e04cbd94b4689661887249953f81  v2/docs/records/l3plane/fetch_pvgis_series.py
40facb734c8558add0958f377d784ca1bdbb857a06bbd9354a8620fb8dc10307  v2/docs/records/l3plane/plane_grid.out
4200101cb7c75bbb61ebcd2ba846c468a5f22ebd08b2cbef563854f23130fa25  v2/docs/records/l3plane/plane_grid.py
8119987a20fad08cae0edc928726c847b1f5ec41f81cfd9552849793567e96be  v2/docs/records/l3plane/three_cases.out
2395d75e48c9787773373aefcd02aeaeb04f5cfcf9d7c4a948617e1547bfab68  v2/docs/records/l3plane/three_cases.py
2ce0b0f41b074ea6e132d57ae6a92bd20954f792c7539b7f50ef3a410953f049  v2/docs/records/l3plane/vbus20_range.out
f4eabc3536334604b007acc34c4ac78ac218a7cfb294f4352a9baaaeff78ff01  v2/docs/records/l3plane/vbus20_range.py
8cc676433f4e3fb84240ddcdd55ae818e7d8b64a3a7ef8e710e7afd5c4e59961  v2/docs/records/l3plane/weather_basis.out
e8fe1d745f53a1553b43692aa5084b128373bb640446f53c6bacd9a58799e15e  v2/docs/records/l3plane/weather_basis.py
50171547951aa9a45df1fd95fc45665919a2cee5e2f315c10dd2838f62343427  v2/docs/records/r11dep/R11-DEPENDENCY.md
a3c763a522cb608c4a4122325feecb75cb7dbe4f33bfec46a9d6adb9b408f62c  v2/docs/records/r11dep/inputs/lcsc-C2903468-2026-09-30.json
f9d2c6f23fab3edcb48ad0116366fe588a514f755aafe56ebd62a0fe9495a209  v2/docs/records/r11dep/r11_dep.out
6636a7489d3d1406ec8e4ea68c48169466edeb244ce0de4c350a8aca7161fb56  v2/docs/records/r11dep/r11_dep.py
031ab3f99779f657be720b36c9ea71c9933175b14bc6883e927df2937b31fd8a  v2/docs/records/a1int/reconcile_lid_panel.py
085b7566b3ee72ace2fa52ad3847f7b7167837e2f53e25d135d6996da182bde6  v2/docs/records/a1int/reconcile_lid_panel.out
d65d2403e3e27e63e56e0b0e2ba50baf8a811807074e11a4d14c9cb545fb963b  v2/docs/records/a1solar/energy_runs.out
e7dbabb0611925227ccfc429c14c8833a7b1f2c755684444124446f20b22a229  v2/vendor/passives/yageo-rc-l-series-v12.pdf
3224518dbc8bdc858a96cfde88de2611494550f95406f6b65130c232cdfc93fb  v2/vendor/passives/milliohm-hojlr2512-series.pdf
c5f0363a9d97b6db6e5ef10fa89904fd55e30aca67007760b9d77caa3b0debd7  v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json
f1450d603cfd80954d0367ed8d20b73e797c56d76ab17e6b36fe45880ebfca07  v2/vendor/sources.txt
```

## Figures beside theirs

| Figure | Theirs | Checker |
|---|---|---|
| Derated 4.00 A: U3 maximum; margins on 0.060 / 0.079 A | 4.100 A; +0.052 / +0.033 A | 4.100 A; +0.052 / +0.033 A |
| Derated NOM, 4S15P TYP / WAB | 369.9 / 396.2 | 369.4 to 370.1 / 395.7 to 396.4 (U3 0.9815 to 0.9810) |
| Derated NOM, 4S14P; 4S9P | 400.9 / 427.2; 538.3 / 566.0 | 400.4 to 401.1 / 426.7 to 427.4; 537.7 to 538.5 / 565.5 to 566.2 |
| Derated WE, 4S15P; 4S14P | 462.9 / 488.9; 493.7 / 519.7 | 463.8 / 489.7; 494.6 / 520.5 (U3 0.9750, not recomputed) |
| Derated coverage, NOM TYP | 0 of 864 | 0 / 0 / 0 of 864, each lid |
| L1 at the 5.05 A setting | maximum 5.18 A, peak 15.68 A, 89.6 % | 5.176 A, 15.68 A, 89.6 % |

Rerun from this folder against a checkout of the tip with the held files present: `python3 indep_round5.py <checkout>`.
