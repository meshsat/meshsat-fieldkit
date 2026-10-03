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
| `apply_l5pwr2_contracts.py` | Set 28 (decision 9 of the page): the integrator's script that restates the six contract texts of findings L5-F09 and L5-F10 (`pcb_interfaces.yaml` IF-AE-DOCK `pin1_vsys_dock`'s hard short and fan stagger, IF-EXT-DC's guard `protection` and `bench`; `HW-FW-CONTRACT.md` section 4.1's R-173 row and V-E16's rows 2 and 3) to the Layer 4 text that replaced them, every figure parsed from L4-E9's page, the register and L4-E11's output; idempotent (`--check` on the tree reads "already applied"); applied on `fnd/l5pwr2` |
| `apply_l5f11_contracts.py` | Set 28 (decision 10 of the page): the integrator's script after `apply_l5pwr2_contracts.py` (it refuses before it): finding L5-F11 and the sweep's rows restated the same way (IF-AE-DOCK `pin1_vsys_dock` to L4-E11 18b and R-177, `FAN1_SW_FAN2_SW.start` to E11-39, IF-EXT-DC `l4_defects` to L4-E9 8a, FW-E11's verification and V-E11 to R-188, section 4.1's R-177 row, HF-F05 answered, a change-record row); idempotent; applied on `fnd/l5pwr2` |
| `../../../ecad/tools/tests/test_l5pwr.py` | The test: the output reproduced, every excerpt in its target and every figure in a source, the marks and triggers well formed, the pins map equal to the committed netlists', the drafted pin 1 its own field, the eleven power lines present, the new rows with their tables' cell counts and unique ids, PANEL.md's sentence, the page's table equal to the script's, the apply scripts refusing a second run and applying once to the base, no dash in the record |

**Since Layer 5's second round (record `../l5r2/`, 3 October 2026)** the reader reads the three targets as this pass committed them (`L5PWR_COMMIT = 1e18a1ca`, in this branch's own history) and the Layer 4 sources from the tree: the second round restated some of this pass's texts in place (FW-E11, the fans' start rule, the SLOT_EN line), and a reader of the current tree would refuse the day its subject moved on. `test_l5pwr.py` compares the apply script's result with that commit's files for the same reason.

**Since set 28 (finding F-12 of `../int28b/RESULT.md`, 3 October 2026)** the reader restates six rows whose cited figures set 27's
Layer 4 corrections changed (L4-E7's round 5: the solar guard's reference loop withdrawn as a passing floor; L4-E11's section 18:
the mixer fans on U22's regulated rail, the hard short's figure a test target): S27-B6, S27-01, S27-02a, S27-02b, S27-03 and
SEQ-08. The table keeps the text written; `RESTATED` in the script names the figures that no longer stand (checked as printed by
the row's sources at `L4_BASE = 2c240414`, the pass's base, in this branch's history), the Layer 4 text that replaced them (a
pattern with no typed number, matched once in the tree's source; its figures parsed from the match), the restated mark, trigger
and where, the contract value that changes, and the targets as set 28 carries them (`SET28_COMMIT = 5515ecc0`, read from this
branch's history): restated in place by record l5r2 or a withdrawn text still there (findings L5-F09 and L5-F10 of the page).
Output section 1a and the page's section 4a carry it. No target and no Layer 4 record is edited.

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
