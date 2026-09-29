# a1elec running log (MESHSAT-1357, Option A(i) electrical work package)

Stream a1elec, branch `fnd/a1elec` from integration set 10's line `13b5352b`, worktree `a1elec`. One Claude author,
an AI; nothing here is a qualified review. Prototype design: nothing built, ordered or measured.

| time (CEST, 29 Sep 2026) | what |
|---|---|
| 02:11 | Brief and WORKER-RULES read. Read: `records/energy/` README, ENERGY-RECONCILIATION.md sections 8 and 9, `energy_architecture.py`, `energy_budget.py` (Pack, profile, simulate), `energy_inputs.yaml` (pack, chain, window), `gen_sch_a.py` charger block (U3, R16, R17, Q7 to Q10, L2), `pcb_pack_protection.yaml` (every threshold), `gen_sch_p.py` header and part lines, HW-FW-CONTRACT FW-A02, FW-A16, FW-E01, FW-P01, board E's J_SMB notes. |
| 02:15 | Makers' documents read from `v2/vendor/` (text extracted to the session scratchpad, nothing fetched): TI SLUSE66A (BQ25731) 9.3.5, Table 9-1, 9.3.6, 9.3.9, 8.7 Figure 8-3 and 8-4 (page image read); TI SLUUAQ3A (BQ4050 TRM) 12.1, 13.25, 13.27, 14.13.5.1, 14.13.5.2, 14.14.1.5, the Calibration rows (CC Gain, Capacity Gain); TI SLUUBF9 3.3.3 (current calibration); TI SLUSBZ5D (BQ34Z100-G1) 7.3.1.6 and 7.3.1.8 (SCALED units through calibration); TI SNOSD17G (LM74700-Q1) 6.5; TI CSD17570Q5B and CSD18510Q5B RDS(on) rows. |
| 02:22 | The PVGIS mean-day profile (hourly T2m for the lid's temperature basis) copied byte for byte from `71be4943` into `inputs/`; sha256 4d974567... equals the value `energy_inputs.yaml` names. |
| 02:25 | `energy_two_pack.py` written and run (0.25 s, deterministic: a second run byte-identical). Equivalence with `energy_budget.simulate()` at 4S18P exact on eight cases (largest difference 2.9e-13 Wh). First readings: the design case (400 Wp, 200 W, entry re-rated) meets M1 with the lid at the mean day's minimum air, 13.23 C (lowest 31.2 Wh, the lid's own 0.9 Wh), down to a lid at +9.6 C; board A's entry as generated (U3 input held at 5.40 A) does not meet at 13.23 C (needs the lid at +17.4 C, or 650 Wp); FW-A16 as written fails outright. |
