# Stream w4r drafts (MESHSAT-1357, 27 September 2026)

Stream w4r owns four files: `v2/ecad/tools/pcb_rules_coverage.yaml` (the INT-001 row only),
`v2/ecad/tools/block_contract.py`, `v2/ecad/tools/tests/test_block_contract.py` and the new
`v2/ecad/tools/tests/test_per_board_contract_verdict.py`. Everything else it needs is here, each script editing its
file by asserted old text. Usage of each: `python3 <script> <tree root holding v2/ecad>`.

## Required for E5's INT-001 to bind (apply with the four files, in this order)

1. `patch_rules_status.py` (owner: rules_status.py). `_names` reads `verification.verdict_by_board`, `result_for`
   asks `_names`, and `CONFIG_INPUTS["block_contract.py"] = ("meshsat.pretty/*.kicad_mod",)`. Without it, E5's
   INT-001 still reads the set verdict (UNBOUND) and every check_contracts_e5 reading reads CONFIG_UNDECLARED
   (shown: `readings/rules_status_before_after.json`, `files_only`). Cost: rules_status.py is in jlc_certify.py's code
   bundle, and it writes rules_complete, so SGN-001 reads TOOL_CHANGED on all seven boards until the next full
   rules_status/render run (re-take class CURRENT_CANDIDATE), and jlc_certify's readings until re-taken or vouched.
2. `patch_retake_schematic_phase.py` (owner: retake_schematic_phase.py). E5's `check_contracts_<letter>` is
   block_contract.py's (check_contracts.py writes nothing for E5), with a new `needs` value "pcbnew" that SKIPs on a
   host without KiCad's Python module. Without it the driver plans check_contracts.py for check_contracts_e5 and the
   step ends NOT WRITTEN.

## Optional, same integration

3. `patch_coverage_sch003.py` (owner: the coverage map's SCH-003 row): one sentence in SCH-003's note saying what the
   reading now compares. Decides nothing.
4. `apply_registry.py` (owner: pcb_requirements.yaml): one sentence appended to S-74's title (stays OPEN); no SC-nn or
   S-nn is taken. REQUIREMENTS-TRACE.md must be re-rendered after it (test_requirements fails until then).
5. `patch_rules_render_coverage_page.py` (owner: rules_render.py): PCB-RULE-COVERAGE.md shows `; on E5 -> ...` for a
   per-board line. Same cost as 1 (rules_render.py is a writer and in jlc_certify's bundle); apply both together.

## Order for the integrator

Commit the four files and the applied drafts (the coverage map is a config input: committed before rules_status),
re-take board E5 on the box (`retake_schematic_phase.py --run --board e5 --in-place` in a clone, or `--verdict-dir`
outside the repository), install `check_contracts_e5` as the consolidated re-take did, then rules_status and the render.

## Readings (scratch, never the tree's evidence)

- `readings/check_contracts_e5.before-main-tool.verdict.json`: main's block_contract.py on main 91894cd7's files, on
  the box, as gate_sweep.sh runs it: PASS 33 of 33, against board A's board file 58e26c67987b1daa.
- `readings/check_contracts_e5.after.verdict.json`: w4r's tool through the re-take driver on the box: FAIL, 28 of 38,
  against board A's netlist da05dc02bc1e612f; rules INT-001 and SCH-003 with their digests.
- `readings/geom_parity.py` and `.out.txt`: the J_DOCK land mounted as DOCK_MOUNT says gives the same twelve offsets
  and the same target-to-pin map as J_DOCK on board A's committed board file.
- `readings/rules_status_before_after.json`: every rule-board row whose result or class moved (E5 INT-001, E5 SCH-003,
  SGN-001 on seven boards) and the E5-only run without drafts.
