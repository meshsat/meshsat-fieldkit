# l4e4: board A's current-limit coordination and the outlet's trip (layer 4 task L4-E4, MESHSAT-1357)

Prototype design, desk arithmetic. Items 2 and 5 of `../l4e/L4-ENERGY-ARCHITECTURE.md` ("The next implementable
power-path choices") turned into checkable values: U3's IIN_HOST, R11 and R138.

| File | What it is |
|---|---|
| `L4E4-CURRENT-LIMITS.md` | The one page: the chosen values, each with its reason and closure criterion, what stays INCONCLUSIVE and why, and the bench rows |
| `l4e4_limits.py` | The script. Section 0 reproduces `../r11dep/r11_dep.out` byte for byte, first in a child process and then in-process with its locals captured. Then it prints the setting, R11's choice and margins, C-1, and R138's trip window. Run from the repository root: `python3 v2/docs/records/l4e4/l4e4_limits.py > v2/docs/records/l4e4/l4e4_limits.out` |
| `l4e4_limits.out` | Its output, committed |
| `inputs/lcsc-C2904240-2026-10-01.json` | LCSC's answer for the chosen R11, HoJLR2512-3W-8mR-1%, with the sha256 of its datasheet link, which is the held series sheet |
| `inputs/lcsc-C2904239-2026-10-01.json` | LCSC's answer for the 7 mOhm a 5.05 A setting would need (not chosen) |
| `inputs/lcsc-C2903482-2026-10-01.json` | LCSC's answer for the chosen R138, HoJLR2512-3W-5mR-1% |
| `inputs/jlc-search-hojlr2512-3w-2026-10-01.json` | JLCPCB's public search for the HoJLR2512-3W family: the catalogue the R11 choice is made from |
| `apply_gen_sch_a_r11.py` | DRAFT for the generator owner: R11 to 8 mOhm with LCSC C2904240 in `v2/ecad/tools/gen_sch_a.py`. Default `--check`, writes only with `--write`, refuses a second application. Never applied to the tree here |
| `apply_gen_sch_a_r138.py` | DRAFT for the generator owner: R138 to 5 mOhm with LCSC C2903482, the PD_SW note, and a comment. Same contract |

The predicates are held by `v2/ecad/tools/tests/test_l4e4.py`. Run it with
`env -C v2/ecad/tools/tests python3 run.py test_l4e4`; it reports 9 tests.
