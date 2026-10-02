# l5pwr: Layer 4's power results written into Layer 5's interface contracts (MESHSAT-1357, set 27, 3 October 2026)

Prototype design: nothing here has been built, powered or measured. This folder is the record of Layer 5's power pass: the
handover entries LH-01 to LH-11 of `../l4e9/LAYER5-HANDOVER.md`, the set 27 rows (the dock's pin 1 as VSYS_DOCK behind U42, the
fans' start stagger, R-176's six bench rows) and the power lines' reset, default and cable-out states (criteria 5.6 and 5.7)
written into the three files Layer 5 owns: `v2/ecad/tools/pcb_interfaces.yaml`, `v2/docs/HW-FW-CONTRACT.md` and `v2/docs/PANEL.md`
section 10. Every figure is Layer 4's and is marked as its source marks it; an entry resting on an open condition is PROVISIONAL
with its invalidation trigger named; a figure true of a release-guarded draft that no generator carries says DRAFTED with the
register row that applies it, and the drawn board is stated first where it differs. No requirement is changed; no L4 record and
no generator is edited.

| File | What it is |
|---|---|
| `L5-POWER-CONTRACTS.md` | The one page: what was written and where, the table (contract, field, text written, L4 source row, mark, invalidation trigger, criterion 5.x moved), check_contracts.py's reading before and after, the criteria moved, the PROVISIONAL entries, the decisions taken, the findings for other layers, what is not claimed |
| `l5pwr_contracts.py` | The reader: it reads the three contract files and the Layer 4 records, refuses if an excerpt of the table is not in its target or a cited figure is not printed by a cited source, and prints the table with every file's sha256. Run from anywhere: `python3 v2/docs/records/l5pwr/l5pwr_contracts.py`; the committed output is regenerated only through `regen_out.py <worktree> v2/docs/records/l5pwr/l5pwr_contracts.py v2/docs/records/l5pwr/l5pwr_contracts.out` |
| `l5pwr_contracts.out` | Its output, committed; section 4 is the page's table, byte for byte |
| `apply_l5pwr.py` | The patch script that wrote the three targets, run once on the tree by the Layer 5 author (who owns them) and kept as the exact statement of the change: `apply_l5pwr.py <target> --check` on the tree now refuses "already applied"; on the files as committed at `2c240414` (the contract after `../l4e5/apply_fw_a16.py`) it checks OK. It asserts after patching that every anchor of `../l4e11/apply_pcb_interfaces_dock.py` still occurs once, so that draft applies unchanged when the generator drafts apply |
| `apply_conops_l5pwr.py` | DRAFT for the CONOPS owner, not applied by Layer 5 (CONOPS.md is not in its brief): the margin hold as a mode (LH-11, R-138) and the source-only statement (R-133) at the end of CONOPS 4c; the owner who applies it rebinds the registry's and L4-E12's readings of CONOPS.md afterwards |
| `../../../ecad/tools/tests/test_l5pwr.py` | The test: the output reproduced, every excerpt in its target and every figure in a source, the marks and triggers well formed, the pins map equal to the committed netlists', the drafted pin 1 its own field, the eleven power lines present, the new rows with their tables' cell counts and unique ids, PANEL.md's sentence, the page's table equal to the script's, the apply scripts refusing a second run and applying once to the base, no dash in the record |

## Run order (what was run, in this order, on 3 October 2026)

1. `python3 v2/docs/records/l4e5/apply_fw_a16.py v2/docs/HW-FW-CONTRACT.md --write` (L4-E5's draft: FW-A16 restated, FW-A18, V-A06 to V-A10, FW-E04, FW-C01's step 5; its application is register row R-23's, assigned to Layer 5).
2. `python3 v2/docs/records/l5pwr/apply_l5pwr.py <target> --write` for `pcb_interfaces.yaml`, `HW-FW-CONTRACT.md` and `PANEL.md`.
3. `python3 _bin/regen_out.py <worktree> v2/docs/records/l5pwr/l5pwr_contracts.py v2/docs/records/l5pwr/l5pwr_contracts.out`.
4. `env -C v2/ecad VERDICT_DIR=<scratch> python3 tools/check_contracts.py v2/ecad` before and after, the two stdouts compared (section 5 of the page).
5. `env -C v2/ecad/tools/tests python3 run.py test_l5pwr test_public_hygiene test_l4e5 test_interfaces`.

## What this pass changes for other records (the integrator's actions, listed in the page's section 9)

The three files are pinned by sha256 in `../l4e9/l4e9_power_path.py` (hwfw, ifaces), `../l4e11/l4e11_power.py` (hwfw, panel) and
`../l4e5/l4e5_source_control.py` (hwfw), and five readings of the requirements registry are bound to `PANEL.md`'s content
(CFL-001, CFL-005, CFL-014, CFL-015, CFL-016); `pcb_interfaces.yaml` is a configuration input of `interfaces.py` (CONFIG_INPUTS).
Those records re-pin and those readings are rebound and re-taken after this pass merges, as the integration recipe says; until
then their scripts refuse ("is not the pinned file") and their tests fail at that refusal, which is the expected re-pin, not a
defect in the contracts.
