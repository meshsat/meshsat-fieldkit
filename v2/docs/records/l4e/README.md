# records/l4e: layer 4 task L4-E2, the energy architecture comparison (MESHSAT-1357)

1 October 2026, branch `fnd/l4e` from main `b45d1705`; second and third issues the same day, answering the focused check and its recheck, both filed in `checks/`; fourth issue the same day, answering the independent power review filed as `REVIEW-POWER-ARCHITECTURE-AS-RECEIVED.md`. Prototype design: nothing is bought, built, powered or measured.
The author's analysis, AI arithmetic; not a qualified review and not the independent check. No registry record, no Layer 3
record and nothing under `v2/docs/handover/` is changed by this folder.

## Files

| File | What it is |
|---|---|
| `PACKET-POWER-ARCHITECTURE.md`, `PACKET-FILES.txt` | the electronics engineer's review packet (the entry point: questions, the power path as drawn, the decisions, one line each) and the exact files it needs, tracked or ignored; they point into the records and repeat none |
| `REVIEW-POWER-ARCHITECTURE-AS-RECEIVED.md` | the independent power-architecture review of the packet at `eb3849d5` (CONDITIONAL: L4-R01 to L4-R04), filed byte for byte as received, its own dash characters kept; answered by the fourth issue (L4-R03, the replay companion, is the coordinator's) |
| `L4-ENERGY-ARCHITECTURE.md` | the page: one table comparing A1 (D-06's single 4S3P) and A2 (base 4S6P plus a separately protected lid 4S9P, both lid functions kept) under one assumption set; the power-path corrections (A-1, A-2, B-1 to B-5, C-1 to C-9, R138, O-1, O-2) as architecture decisions; the next discriminating calculation and experiment; the Layer 3 finding restated |
| `l4e_replay.py` | the replay: reproduces the checked records first, then moves one input, the solar stage's input clip, from P-03's 200 W to REQ-016's 100 W, and prints both architectures on the drawn and the hypothetical corrected power paths |
| `l4e_replay.out` | its output; the page cites it as "out N" (its section numbers) |
| `checks/astra-check-l4e2-1.md` | the collaborator's focused check of the first issue (run `20260930T221538Z-809994` on `0e641bd3`, accepted: no; B1 the stopped-hour double count, B2 O-2's power bound, M1 a label), filed byte for byte; answered by the second issue |
| `checks/astra-check-l4e2-2.md` | the collaborator's recheck of the second issue (run `20260930T224030Z-833954` on `21a9a6fe`, accepted: no; B1, M1 and the Layer 3 recount pass; B2 fails again on the omitted IMON_IN line regulation, and the sweep's lower end), filed byte for byte; answered by the third issue |
| `checks/check-l4e2-3.md` | check 3: Claude's (the coordinator's) verification of B2 at `197350a7` against the recheck's own criterion, computed from the maker's table independently of the replay (accepted: yes); not a model review and not an Astra check |
| `ASTRA-L4E1.md` | the engineering collaborator's L4-E1 assessment (job `cx7-l4e1-dominant-constraints`), filed byte for byte; sha256 `36af43f1769c32c64b95528a69ca6972ee14723eae1d7dd21cf98442b3c6f83b`. It directs this task and accepts nothing |

## Run order

1. The held-back cell sheets must be present, because `l3batt/runtime.py` pins them: run
   `python3 v2/docs/records/l3batt/fetch_held_back.py` if `v2/vendor/battery/held/` is empty (it checks each sha256).
2. From the repository root: `python3 v2/docs/records/l4e/l4e_replay.py > v2/docs/records/l4e/l4e_replay.out`.
   It takes about one minute on one core, most of it check 0a, and lowers its own priority. Standard library plus PyYAML
   through the imported model, and poppler's `pdftotext` on the path (the imported `vbus20_range.py` already needs it).
3. `git diff --exit-code v2/docs/records/l4e/l4e_replay.out`: a clean diff is the reproduction of this record.

## The checks the script makes before it prints a result (exit 4 otherwise)

- **Pins (exit 2):** `l3batt/runtime.py` and `runtime.out`, `l3plane/energy_basis.py`, `three_cases.py` and
  `three_cases.out`, `energy/energy_budget.out` and `r11dep/r11_dep.out`, each by sha256. The imported model pins its own
  inputs in turn (`energy_basis.py`, `energy_two_pack.py`, `energy_budget.py`, `energy_runs.py`), and the parsed `.out`
  files must equal HEAD's.
- **0a:** `runtime.py` re-run in a child process gives `runtime.out` byte for byte.
- **0b:** this harness gives `runtime.out` section 1's D06 and A35 rows, the twenty cells of section 2 and the twelve
  least-lid lines of section 3, string for string.
- **0c:** `three_cases.out`'s AS DRAWN and DERATED VARIANT rows at WE inputs (both-kept lid, 72 h, TYP and WAB).
- **0d:** the single-pack use of the two-pack model (A1, the lid off) gives `energy_budget.out` 5b's two PS-IDLE-SPEC
  September rows: usable energy, first stop, hours run and unserved energy.
- **In every run (exit 4 otherwise):** the store account closes (start + stored - drawn - end); the SERVICE LEDGER's kit
  balance closes (node energy summed independently from the chain + start = served + spill + charge losses + discharge
  losses, the cutoff's included, + end); the legacy model metric differs from the ledger by exactly the stopped hours'
  credited sun; the ledger's lid-path loss outside the cutoff equals the model's; each within 1e-6 Wh; and the node power
  equals the model's in every hour to 1e-9 W.
- **Once:** the ledger reproduces the check's own flow-derived figures for A2 on the corrected path (270.132086 /
  286.306461 Wh at 48 h and 500.372955 / 516.547330 Wh at 72 h, 06 / 18 UTC) to the sixth decimal; the re-weighted U3
  efficiency reproduces `energy_basis.u3_day` at 200 W before it is used at 100 W; the input window read from
  `energy_inputs.yaml` must be REQ-016's 100 W; section 11 reads REQ-016's 25 V and 100 W from the registry and R8 and R9
  from `gen_sch_e.py` (which must equal HEAD's), and the LT8705A sheet is pinned by sha256.
- **Section 11, O-2's bound:** the LT8705A sheet is pinned by sha256; every row of its electrical characteristics
  (pp.3 to 6) whose parameter names the input-current mechanism or the input-voltage hold must be classified in
  `EC_ROWS`, and every tabled row must read back from the sheet, by column, as printed (exit 3 otherwise). The setting is
  sized from the rows the table classifies, rounded down to 1 mA; the check reads the limit's rows from the sheet
  independently of that classification and evaluates every corner (the loaded voltage from the hold's tolerance-adjusted
  lower corner to 25 V in 0.01 V steps, both temperature ends, every tolerance at its limits), and refuses (exit 4) if
  any corner exceeds 100 W.
- **The refusal, tested (1 October 2026, then the script restored and its sha256 compared):** with the line regulation
  reclassified NONE the sizing gives 3.550 A and the run exits 4, "O-2's setting 3.550 A lets the stage take 100.0548 W
  at 25.000 V"; with the row deleted from the table the run exits 3, the row "Line Regulation for IMON_IN and IMON_OUT
  Error Amp" unclassified.
- **Section 12, the compliant panel:** the held SunPower SPR-E-Flex-100 sheet is pinned by sha256 (fetched into the
  ignored `v2/vendor/solar/held/` by `../a1solar/fetch_held_back.py`; exit 2 if absent); its printed figures must equal
  a1solar's `CAND['SPR100']` (exit 3); its open circuit at -20 C must be inside REQ-016's 25 V (exit 4); a1solar's
  `array_calc.py` is pinned; and no hour of any trace may put more than 100 W into the stage (exit 4).
- **Section 13, the undocumented loads:** `load_trace.out`'s tier T rows must sum to its tier line and each must have an
  entry in `UNDOC` (exit 3).
- **Determinism:** two runs give the same bytes; no date, host or absolute path is printed.

## What the results do and do not show

The 100 W results rest on the checked 400 Wp 2S2P availability series, which REQ-016 does not admit: they are a
conditional screening stimulus (out 7), not the performance of a compliant panel. The corrected path is HYPOTHETICAL and
every WE figure is CONDITIONAL on the three undocumented efficiencies (C-8). Served and unserved energy is the service
ledger's; the model's own unserved counter, which credits a stopped hour's sun as served while charging with it, prints
only as the legacy model metric (sections 0, 5 and 9). O-2's conservative bound (section 11) is shown as its own case
beside the 100 W screening case, not in place of it. **B2: arithmetic corrected under stated assumptions (closed). O-2
physical compliance: OPEN:** the bound rests on EA2's and EA3's TYP-only gains, the line regulation printed at 25 C and
not switching, two 1 % resistors with tolerance and drift unselected, and temperature ends that repeat the same bounds
(EA2 at 120 V/V gives 100.0758831 W, the review's sensitivity); the engineer's grade, resistor values and tolerance
budget replace them. Section 12's compliant trace rests on one held sheet, a single-diode fit and an INFERRED NOCT, on
one mean day; neither architecture is approved or shown realizable. The AS DRAWN figures are bounds (the upper
bound keeps the model's `min(available, cap)`; the lower bound takes A-2's inferred collapse). Nothing here is
demonstrated capability.
