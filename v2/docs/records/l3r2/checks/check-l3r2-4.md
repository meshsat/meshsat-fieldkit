accepted: no

# CHECK-4: final delta check of the Layer 3 handover L3-R2 (item C27), the six owner decisions pending

MESHSAT-1357, 30 September 2026, about 05:40 CEST. **An AI check, not a qualified review.** The checker wrote none of
L3-R2.

**Scope.** Branch `fnd/l3r2` at `9493847c` (confirmed), two commits on `6b2e4035`: round 3c `b0ccff61` and the fill
`9493847c`. The energy basis is `fnd/l3plane` `cd8720a1` (confirmed). Judged on `git diff 6b2e4035..9493847c` against:
* CHECK-3's final delta scope;
* the owner's words quoted in the brief.

**Why "no".**
* Round 3c and the fill close CHECK-3's blocking item. The binding now holds against every attempt I made.
* The figures trace to the checked outputs. The flags are plain. The gate reads NOT MET for the right reasons. Every gate
  passes, on main and on set 16.
* **One blocking item remains, a consistency fix in text:** row L3-OD6's recommendation (the mean day in the WAB build)
  settles row L3-OD2's function question (the QMX leaves the kit) without saying so, while row L3-OD2 recommends no option.
* The rest are minors. Most are text left over from before the fill.

## What was run (throwaway shared clone at `9493847c`, `int16-evidence-e5322674.tar` installed; removed afterwards)

* **Gates at the tip:**
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings.
  * `rules_render.py --requirements --check`: current.
  * `render_l3r2.py --check`: 3 pages, 0 out of date.
  * `dryrun.py`: byte identical.
  * `run.py test_requirements test_l3r2`: **89 passed, 0 failed, 1 skipped**.
* **Merged with main** (`6cd331ef`): clean.
  * `rules_lib` 0 errors; `rules_render --check` current.
  * `REQUIREMENTS-L3-R2.md` goes out of date by its header line only (the registry's sha). After a re-render, `--check`
    reads 0 out of date.
  * `dryrun.py` byte identical; tests 89 passed and 1 skipped.
* **Set 16** (`fnd/int17` `72b91c91`, which contains main and `cd8720a1`). `fnd/l3r2` merges into it cleanly. I also ran
  the README's integrator run order exactly as written on a branch from `72b91c91`:
  * Every apply script wrote.
  * `rules_lib` 0 errors; `render_l3r2.py --check` 0 out of date; tests 89 passed and 1 skipped.
  * `dryrun.out` equals the branch's, and the three pages equal the branch's but for the registry sha.
  * The `records/l3plane`, `records/r11dep` and vendor files the run order checks out equal set 16's (no diff).
* **Text rules** on the 103698 added lines:
  * 0 lines with U+2013 or U+2014.
  * No host name or absolute path. Five lines name relative scratch folders (`_scratch/chk-energy3` to `5` in the filed
    energy checks, and `_scratch/_reports/...` and "the session scratchpad" in my own filed checks); none is a host or a
    user path.
  * CONOPS.md, PRODUCT-BRIEF.md and `v2/release/` are unchanged against `6b2e4035` and against main.
* **Filed checks.** `checks/energy-basis-check-5/CHECK-5.md` is byte identical to its report: "accepted: yes", "tip:
  cd8720a1...".

## Verified

### 1. The binding

* **The filed files match the checked tip.** All 26 files CHECK-5 lists by sha256 equal both the tree and `git show
  cd8720a1:<path>`.
* **`energy_basis`** names ENERGY-BASIS.md with `weather_basis.out`, `energy_basis.out` and `three_cases.out`.
* **`power_path_check`** names R11-DEPENDENCY.md with `r11_dep.out` and `three_cases.out`.
* Each carries `tip: cd8720a1...` and CHECK-5.
* `basis_binding.verify()` is used by `set_energy_basis.py`, the hold (`cond.basis_state`) and the gate (`basis_ok`), and
  re-reads each file against `git show <tip>:<path>` on every run.
* **Refusals I produced:**
  * CHECK-3's failing path (868c321f files, CHECK-2, `--tip ec415c09`): **REFUSED**, "not byte identical to the file of
    that path at the checked tip ec415c09".
  * A check naming another tip (CHECK-4 with `--tip cd8720a1`): **REFUSED**, "does not name tip".
  * The same check with `--tip 06b8ecea` and the cd8720a1 files: **REFUSED**, "not byte identical".
  * `weather_basis.out` changed after the check, with the sha left unchanged: gate and hold both **refuse**, "not held at
    8cc6...".
  * The same change with the sha updated in `l3r2.yaml`: both **refuse**, "differs from the file of that path at the
    checked tip cd8720a1".
  * The tip rewritten to 06b8ecea, or to an unknown sha: **refused**.
  * The as-filed entries verify: (True, '').

### 2. Reader coverage

`basis_reader.py` reads cd8720a1's three outputs whole:
* 8 sizing rows;
* 15 coverage rows;
* 3 stores and 2 allowances;
* 27 reference-plane cases;
* 24 four-case rows (8 blocks by 3 lids);
* 16 four-case coverage rows.

The derated setting reads **4.00**. A deleted row is refused in each output I tried:
* `weather_basis.out` A: "reads 14 coverage rows, not the 15";
* `energy_basis.out` 5: "reads 26 case rows, not the 27";
* `three_cases.out` 2: "reads 23 rows, not the 24".

### 3. The filled figures, traced to their lines at cd8720a1 (18 spot checks, all equal)

| Figure on the pages | Line |
|---|---|
| (a) as drawn, NOM 326.6 to 522.4 Wh unserved; WE 422.1 to 616.7 | `three_cases.out` 2, AS DRAWN blocks |
| (a') derated 4.00 A, NOM 369.9 to 566.0; WE 462.9 to 657.8 in the table | DERATED blocks; the setting in section 1 |
| (b) resistor-only lower bound, NOM 622.1 to 1079.9; WE 719.4 to 900.9 | RESISTOR-ONLY blocks |
| (c) NOM 4S15P 125.2 / 106.8, 4S14P 93.7 / 75.7, 4S9P NOT MET 165.7 / 172.6 | CORRECTED NOM |
| (c) WE 4S15P 74.3 / 19.5 (lid 0.0 in WAB, Y/N), 4S14P 44.0 Y/N / NOT MET 10.8, 4S9P 169.2 / 176.1 | CORRECTED WE |
| 4S15P WAB at U3's 6.0 A bracket 0.6 Wh unserved; at 18.782 V 3.7 Wh | `energy_basis.out` 5, rows WE60 and WEL |
| Coverage at WE: 4S15P 22.0 / 17.5 %, 4S14P 19.2 / 14.0 %; 0 of 864 as drawn and derated | `weather_basis.out` A (190, 151, 166, 121 of 864); `three_cases.out` 3 |
| L3-OD6: mean day 619.0 / 676.2 Wh, 4S13P / 4S15P, 76 / 84 cells, 3.80 / 4.20 kg, fits [tablet-out, qmx-out] / [qmx-out] | `weather_basis.out` B |
| Coverage targets 981.8 to 1760.5 Wh, 128 to 228 cells, 6.40 to 11.40 kg, 1.42 to 2.54 and 1.52 to 2.71 times, fits none | `weather_basis.out` B |
| L3-OD4 band: 4S15P WE COMB slope 30 to 50, south to 15 W, least 5.3 Wh at 50/+15 WAB; 4S14P none; EACH none; WE60 none for either lid | `energy_basis.out` 6 |
| Efficiency thresholds 0.936 to 0.949 and 0.907 to 0.929 | ENERGY-BASIS.md section 1 (lines 91 to 93); `energy_basis.out` 444 and 450 |
| Front end 4.212 / 5.000 / 5.810 A; derated margins +0.052 / +0.033 A | `three_cases.out` 1; CHECK-5 What holds 1 |
| C-1: at most 0.29 mOhm at 25 C (0.371 at the working temperature); bench 0.29 mOhm x I, 1.7 mV at 6.0 A | R11-DEPENDENCY.md 2c C-1, closure item 3 and bench item 3 |
| REQ-015 case: 11.00 V floor; vehicle entry 6.15 A, 55 W against about 104 W | `r11_dep.out` 222 and 193; energy CHECK-4 lines 142 and 143 |
| B-1 schedule 5.05 A, peak 15.68 A, 89.6 % | R11-DEPENDENCY.md 2b; CHECK-5 What holds 2 |
| CF-01: 19.146 / 20.000 / 20.887 V; 19.205 / 20.823 V; brackets 19.101 / 18.782 / 18.738 V | ENERGY-BASIS.md section 2 table; filed energy CHECK-2 minor 8 (19.101 V) |
| CF-02 history: 4e9fa869 not accepted (CHECK-3); 3ef5987e accepted (CHECK-4 of 06b8ecea); cd8720a1 accepted (CHECK-5) | the filed checks' first lines |
| F-01: "at most 22.0 percent"; the as-drawn, derated and resistor-only ranges | as above |

### 4. Flags and recommendations

* **Flags, all plain:**
  * L3-OD1 `approve`: "CANNOT MEET M1 on the circuit as drawn, nor in its derated variant ...; INCONCLUSIVE on the
    resistor-only proposal; ... only on the HYPOTHETICAL corrected power path".
  * L3-OD1 `reject`: CANNOT MEET M1.
  * L3-OD2 `tablet-out`: "CANNOT MEET M1 at the worst established inputs in the WAB build, even on the hypothetical
    corrected path (NOT MET, 10.8 Wh unserved)".
  * L3-OD2 `qmx-out`: "MEETS M1 ONLY on the hypothetical corrected path ... NOT at U3's 6.0 A bracket or the 18.782 V
    endurance bracket in the WAB build".
  * L3-OD2 `both-kept`: CANNOT MEET M1 in any case.
  * L3-OD2 `qmx-outside`: NO LOCATION ESTABLISHED.
  * L3-OD4 `adopt`: NO PLANE BAND EXISTS.
  * L3-OD6 `coverage`: CANNOT MEET M1 inside the Peli 1450.
  * L3-OD6 `mean-day`: the lids that carry it per build, and the 4S9P lid CANNOT MEET it.
* **L3-OD1's recommendation is honest** and rests on more than energy. It reads "approve, as the only store inside the
  fixed case under which M1 is not already shown to fail; not as a feasible design". It names the sixteen open findings.
  Its reasons beyond energy are D-20 and D-21: keeping D-06 leaves a conflict no engineering can close, and approving buys
  or authorises nothing.
* **L3-OD2 recommends no option as feasible.** It recommends against `both-kept` and `qmx-outside` and states the QMX
  against tablet trade-off both ways: energy against function and deployment, with 3 degrees and 11.7 N against 1 degree
  and 6.1 N.
* **L3-OD4 recommends only the stability requirement** and proposes no band. Its reason is mechanical. REQ-078's figures
  match a1mech README section 5:
  * QMX out: 1 degree (1.2 at the interim feet basis) and a 6.1 N press at the tablet's far edge;
  * tablet out: 3 degrees (3.6) and 11.7 N at the QMX's controls.
  * The push the kit must stand stays the owner's number.
* **L3-OD6** recommends the mean day in the WAB build "as a design benchmark and not a weather promise", with its
  limitation beside it (22.0 / 17.5 percent at WE). Its stated reason is capacity and fit: every coverage target needs 128
  to 228 cells against the 84 of the largest established store, in the case the owner fixed. On D-23: the recommendation
  is explicit, reasoned by the case's capacity and the conservative build, and carries its limitation, so it is not the
  automatic selection D-23 forbids. But see B1 and minor 5.

### 5. The power-path classes

* **The sixteen findings** are closure items L3-C37 to L3-C44 and L3-C46 to L3-C53, all DOWNSTREAM, each with a correction
  and a measurable criterion: A-1 and A-2 (existing defects), B-1 to B-5 (introduced by the resistor-only proposal), C-1 to
  C-9 (missing evidence).
* **Kelvin sensing is C-1**, an implementation requirement tied away from A32, with the bench line "at most 0.29 mOhm x I
  (1.7 mV at 6.0 A)".
* **CHECK-5's minor 1** is carried into A-2's criterion ("run first at E1's fixed 4.15 A to confirm the collapse").
* **The REQ-015 11.00 V case** is conditional (the engineering form, the 5.05 A schedule, changes no requirement) and
  quantified.
* **No owner question fails the owner's test.** The three conditional cases (REQ-015, REQ-072 capped, CON-006 or REQ-019)
  are listed and not asked.

### 6. Facts, the gate and S-127

* **The facts.** CF-01 to CF-04 and F-01 cite the files at cd8720a1 and the checks that accepted them (CHECK-2 minor 8 for
  19.101 V; CHECK-4 and CHECK-5 for the r11dep issues). F-01 states plainly that no lid meets M1 on the power path as
  drawn.
* **The gate reads NOT MET on all four conditions for the right reasons:**
  * condition 1: no row decided (coherence holds; energy basis and power path filed with accepted checks);
  * condition 2: 0 of 6 rows decided, none held;
  * condition 3: CFL-017 open and L3-C26 not filed;
  * condition 4: CHECK-1 to CHECK-3 read NOT_ACCEPTED.
* **S-127 should close now,** by a session script, not wait for the owner.
  * It is a SESSION item whose own closing condition is met: the energy basis is filed and checked (cd8720a1, CHECK-5
    accepted) and bound in `l3r2.yaml`.
  * Nothing the owner answers changes it.
  * L3-C31 (OPEN) and LAYER-STATUS already name "S-127 closed in the registry with REQ-072 re-read on the filed basis" as
    the session's remaining step.
  * Until then REQ-072 lists S-127 among its waits, which tells an engineer the basis is still owed.
  * Close it by commit, with REQ-072 given an evidence entry reading the basis (REQ-072 stays FAIL: as drawn, every lid
    fails).
  * The gate does not depend on it, so this is a minor, not a blocking item.
* **The skipped test is justified.** `t_l3r2_a_held_row_is_never_written_into_the_tree` skips because the basis is filed
  and the hold is lifted, and the binding that lifts it is tested by
  `t_l3r2_an_accepted_check_is_bound_to_the_files_of_its_tip`. A version that passes a copy of `l3r2.yaml` with
  `energy_basis` null would keep the hold itself under test (minor 6).

## Blocking items

### B1. Row L3-OD6's recommendation decides row L3-OD2's function question without saying so, while row L3-OD2 recommends no option

* **What L3-OD6 recommends.** The mean day in the WAB build. By its own flag and by `weather_basis.out` B, that store is
  carried by the QMX-out lid only (fits `[qmx-out]`, 84 cells).
* **What that means for L3-OD2.** Taking the recommendation leaves only `qmx-out`, which removes HF from the kit (REQ-002,
  REQ-067, REQ-068), or `qmx-outside`, which has no place. With `tablet-out` the scripts record an open conflict.
* **What L3-OD2 says instead.** "No option is recommended as feasible, and which approved function leaves is the owner's",
  and "the function and the deployment favour the tablet out".
* **Neither the L3-OD6 recommendation nor its owner test names the function consequence.** The owner test names REQ-072
  only. The WAB against TYP choice is argued only as "the worst conforming array build", although TYP keeps both lids open
  (fits `[tablet-out, qmx-out]`).
* **Why this blocks.** This is the owner's own points: "moving equipment out of the lid must not silently remove its
  function from the kit" (D-22), "one consistent decision table" (D-22), and each question "must name the affected
  requirement and quantify the consequence" (D-25).
* **Fix, text only.**
  * L3-OD6's recommendation and owner test say that the WAB benchmark is carried only by the QMX-out lid, so taking it with
    row L3-OD1 removes HF from the kit (REQ-002, REQ-067, REQ-068) unless `qmx-outside` finds a place, and that TYP keeps
    both lids.
  * L3-OD2's recommendation names the dependency both ways.
  * Or recommend the build neutrally and leave it to the owner with that consequence stated.

## Minors

1. **Stale text after the fill:**
   * OWNER-DECISIONS' paragraph above the findings still reads "PROVISIONAL ... the list below is restated from the second
     issue once l3r2.yaml's power_path_check is filed and verified". In fact it is filed, verified and restated from the
     third issue at cd8720a1 (CHECK-5, accepted).
   * L3-C45 renders CLOSED, but its text still names "CHECK-3" and "PP-01 to PP-08".
   * L3-C34, the classification row for the power-path correction, and LAYER-STATUS (twice) still say "PP-01 to PP-08,
     closure items L3-C37 to L3-C44". The list is now A-1 to C-9 at L3-C37 to L3-C44 and L3-C46 to L3-C53.
   * The `l3r2.yaml` comment above `energy_basis_checks` still says "None is ACCEPTED yet, so energy_basis stays null".
2. **S-127 is still open.** Close it now with REQ-072 re-read on the basis (section 6). L3-C31 then closes.
3. **L3-OD3's `keep` and `1s4p` carry no flag.** They have no M1 figure ("no grid and no figures"). A plain "NOT SHOWN: no
   figure computed" in capitals would match the owner's "flag ... plainly" for options not shown to meet M1. On the
   circuit as drawn, every L3-OD3 option inherits L3-OD1's CANNOT MEET, which the row could say.
4. **`both-kept`'s range is partial.** Its flag gives "NOT MET by 165.7 to 176.1 Wh", the NOM and WE rows. WEL and WA
   reach 177.2 and 246.8 Wh (`energy_basis.out` 5). Say "at least 165.7 Wh".
5. **L3-OD6's closing sentence argues the wrong reason.** "It is not recommended because the design passes it: on the power
   path as drawn nothing passes it" rests on the as-drawn failure. The real reason, which the row already gives, is that
   no coverage target fits the fixed case. On the hypothetical path the QMX-out lid does pass the benchmark,
   conditionally. Rewording keeps it clearly within D-23.
6. **The hold test only skips.** Passing a copy of `l3r2.yaml` with `energy_basis` null would keep the hold test live after
   the basis is filed.
7. **Binding completeness.** `basis_binding.listed_sha256` compares a file with the check's list only when the check lists
   it. Requiring every named file to be listed, when a check lists any, would close that gap. All six named files are
   listed in CHECK-5 today.

## The delta scope after the owner's answers

1. **Each answer applied by its script with his words and date,** in an order the coherence rules allow:
   * row 6 before row 4's `adopt`;
   * row 2's lid carrying row 6's answer, or the open conflict recorded;
   * the registry validates;
   * both renders pass `--check`;
   * the tests are green on the decided state;
   * the gate's condition 1 reads MET only on a coherent set.
2. **B1's fix and minors 1 to 7,** if they are not done before the owner reads the table.
3. **S-127 closed** by the session with REQ-072 re-read on the basis (if not done before). L3-C31 then closes.
4. **L3-C26: the CONOPS and PRODUCT-BRIEF passages the decided rows change,** re-issued through layers 1 and 2 or as a
   change record, named in `definition_reissue`. It must differ from `baseline_definition` and be approved by an owner
   ruling that decides it, dated on or after the rows. The gate refuses anything less, as CHECK-3 showed.
5. **The gates again, on the tree merged with main or the set that carries it:**
   * `rules_lib` 0 errors;
   * the renders current;
   * `dryrun.py` byte identical;
   * no dashes, host names or paths;
   * H3 unchanged, with CONOPS and PRODUCT-BRIEF changed only by their own re-issue.
6. **The narrow independent check** of those deltas, named in `independent_check`, whose verdict condition 4 reads.
