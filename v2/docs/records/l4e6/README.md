# l4e6: fault handling of board A's front end (layer 4 task L4-E6, MESHSAT-1357)

Prototype design, desk arithmetic. This folder takes implementable choice 4, FAULT HANDLING, of
`../l4e/L4-ENERGY-ARCHITECTURE.md` (findings B-1, B-2 and B-4) and turns it into a decision at both R11 outcomes that
L4-E4 and L4-E5 leave open (8 mOhm, 7.262 A; 7 mOhm, 8.300 A).

| File | What it is |
|---|---|
| `L4E6-FAULT-HANDLING.md` | The one page. The decision and its reasons: R12 12 mOhm bounds L1 and the FETs with U2's own cycle-by-cycle limit, C147 goes to 330 pF, hiccup stays off, and the VBUS20 bank is rated. Also: the candidates not chosen, the B-1, B-2 and B-4 closures at both R11 outcomes, what stays INCONCLUSIVE, the bench rows, the check and what changed, and the consequence for L4-E4 (8 mOhm supported, with V-A07's 0.071 A) |
| `l4e6_fault_handling.py` | The script, run from the repository root: `python3 v2/docs/records/l4e6/l4e6_fault_handling.py > v2/docs/records/l4e6/l4e6_fault_handling.out`. Section 0 reproduces `../l4e4/l4e4_limits.out`, `../l4e5/l4e5_source_control.out` and `../r11dep/r11_dep.out` byte for byte in child processes. It then runs `l4e4_limits.compute()` and `r11_dep.main()` in-process (both print their records) and takes their functions; r11_dep.py's FET loss relations are restated once and reprint its nine FET lines. Then it prints the makers' rows, candidate (a) hiccup alone, candidate (b) rating, the R12 scan over the held HoJLR2512 catalogue reading, the chosen closures, B-4 by r11_dep.py's per-can scaling of the generator's figures, and the consequence for L4-E4. About a minute and a half |
| `l4e6_fault_handling.out` | Its output, committed |
| `apply_gen_sch_a_r12.py` | DRAFT for board A's generator owner: `rcs="12m"` and `cslope=("330p", "C1664")` on the front end's `lm5176()` call in `v2/ecad/tools/gen_sch_a.py`; MODE is left as drawn. Composes with L4-E4's `apply_gen_sch_a_r11.py` in either order. Default `--check`, writes only with `--write`, refuses a second application. Never applied to the tree here |
| `apply_lcsc_fill_r12.py` | DRAFT for the same owner: the `lcsc_fill.py` line that buys "12mOhm 1% 2512" as HoJLR2512-3W-12mR-1%, LCSC C2904242. Same contract |
| `checks/astra-check-l4e6-1.md` | The engineering collaborator's one check (ACCEPTED as a provisional engineering decision, no blocking item, no owner decision; minors M1, L1's temperature over the full VIN grid, and M2, C-5 as an L-versus-current sweep), filed by the coordinator. The page's section "The check, and what changed" maps each minor to its change |
| `README.md` | This list |

The predicates are held by `v2/ecad/tools/tests/test_l4e6.py`. Run it with
`env -C v2/ecad/tools/tests python3 run.py test_l4e6`; it reports 13 tests.
