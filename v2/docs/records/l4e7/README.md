# l4e7: real component settings for board E's solar stage (layer 4 task L4-E7, MESHSAT-1357)

Prototype design, desk arithmetic. This folder takes implementable choice 3, REAL COMPONENT SETTINGS, of
`../l4e/L4-ENERGY-ARCHITECTURE.md` (finding O-2 and review L4-R01): the LT8705A's grade, RSENSE1 and RIMON_IN of its
input-current limit and R8 and R9 of its input-voltage hold, as catalogue parts with their makers' tolerance and TCR, and
section 11's 100 W corner check re-run on the values they achieve, at both temperature ends.

| File | What it is |
|---|---|
| `L4E7-STAGE-SETTINGS.md` | The one page: the decisions and reasons, the corner check at both ends, what stays INCONCLUSIVE with its measurement, the energy (the hold's and the margin's cost in Wh a day, A1 and A2 re-run), the interaction with L4-E5, the bench rows |
| `l4e7_stage_settings.py` | The script, run from the repository root: `python3 v2/docs/records/l4e7/l4e7_stage_settings.py > v2/docs/records/l4e7/l4e7_stage_settings.out`. Section 0 reproduces `../l4e/l4e_replay.out` and `../l4e5/l4e5_source_control.out` byte for byte in child processes, then runs `l4e_replay.main()` in-process with its locals captured (`l4e4_limits.run_main_captured`); every figure after it comes from the replay's own functions (`i_factor`, `ec_row`, `hold`, `trace`, `meanday`, `least`) and from the makers' rows read back from the PDFs. No git hash is compared. About five minutes |
| `l4e7_stage_settings.out` | Its output, committed |
| `apply_gen_sch_e_u5_grade.py` | DRAFT for board E's generator owner: U5 to the I grade, LT8705AIUHF#PBF, LCSC C674169 |
| `apply_gen_sch_e_hold.py` | DRAFT: R8 and R9 at their drawn 102k and 7.50k (REQ-016's 17.6 V point) as 0.1 % 25 ppm/K parts (C861068, C728597); the panel entry keeps 17.6 V |
| `apply_gen_sch_e_input_limit.py` | DRAFT: RSENSE1 (R59, 15 mOhm, C2903494) and the net TRK_VIN behind it, R16 23.2k (C861244), CIMON_IN (C65, C14663), the declarations |
| `fetch_held_back.py` | Fetches the two makers' documents read but not filed (YAGEO RT series V.16 into `v2/vendor/passives/held/`, Infineon BSC028N06NS Rev.2.1 into `v2/vendor/power/held/`), checked by sha256; never run by a test |
| `checks/astra-check-l4e7-1.md` | The engineering collaborator's one check of the first round at `2d7e331e` (NOT YET: B1, the 16.340 V hold changed REQ-016's 17.6 V point without the owner's ruling; minors M1 to M3), filed by the coordinator's instruction byte for byte from its result, `accepted: no`. The page's last section maps each item to its change |
| `checks/astra-check-l4e7-2.md` | The collaborator's targeted recheck at `379ea32f` (ACCEPT: B1 resolved, M1 to M3 reproduced; one nonblocking M2 wording residue, the EA2 break-even stated without its stack, fixed at the next commit), filed by the coordinator's instruction byte for byte from its result, `accepted: yes` |
| `inputs/` | The catalogue readings of 1 October 2026: LCSC answers for every chosen part and for the drawn U5 (with the sha256 of each linked sheet), JLCPCB's searches for LT8705A and the RT0603BRD07 family |
| `README.md` | This list |

The drafts default to `--check`, write only with `--write`, refuse a second application, and refuse the repository's own
`gen_sch_e.py` until a `RELEASE.md` here reads "released: yes" and names an accepted check. They were run only on scratch
copies. The predicates are held by `v2/ecad/tools/tests/test_l4e7.py`; run it with
`env -C v2/ecad/tools/tests python3 run.py test_l4e7`.
