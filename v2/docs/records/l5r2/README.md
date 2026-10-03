# l5r2: Layer 5's second round on the interface contracts (MESHSAT-1357, 3 October 2026)

Prototype design: nothing here has been built, powered or measured. Branch `fnd/l5r2` from set 28's prepared line `a1f696de`. The
round gives the eight first-twelve contracts their pass-2 fields (current, default_state, harness, hot_plug, judged_by, levels,
mating, sequencing, tbd and a part on every connector end), writes the picked fans (D-18, record l7pwr) and their regulated rail
(L4-E11 section 18 at `b929d8be`), writes record l8gnd's SLOT_EN keeper and GND-002 (at `226e9143`) into the contracts and the
firmware rows, and adds IF-A-CHASSIS. It owns `v2/ecad/tools/pcb_interfaces.yaml` and `v2/docs/HW-FW-CONTRACT.md`; it edits no L4
or L8 record and no generator, and changes no requirement.

| File | What it is |
|---|---|
| `L5-INTERFACES-R2.md` | The page: what was written per contract with its sources, the inputs, the method (no loss), the table, the readings before and after (check_contracts.py, hc5's field checker), the criteria moved, the PROVISIONAL entries, the TBD owners, the findings, the decisions |
| `apply_l5r2.py` | The patch script, run once on the tree by the Layer 5 author; on the tree it now refuses "already applied", on the files at `a1f696de` it checks OK. It refuses a lost leaf of any replaced block, a pass-2 field missing, a moved pins map, a lost dock-draft anchor |
| `l5r2_interfaces.py` | The reader: hc5's field contract before (`a1f696de`, read from this branch's history) and after, the fields gained, the no-loss proof, the table (every excerpt in its target, every figure in a cited source), every tbd entry with its owner, the PROVISIONAL entries. Needs pdftotext and PyYAML |
| `l5r2_interfaces.out` | Its output, regenerated only through `_bin/regen_out.py <worktree> v2/docs/records/l5r2/l5r2_interfaces.py v2/docs/records/l5r2/l5r2_interfaces.out` |
| `inputs/l4e11-section-18-b929d8be.md` | L4-E11 section 18 (the fans' feed), copied verbatim from `fnd/l4e11` at `b929d8be` (not in this branch), with the file's sha256 at that commit and the body's own |
| `inputs/l8gnd-sections-2-3-226e9143.md` | Record l8gnd's sections 2 (GND-002) and 3 (the SLOT_EN hold), copied verbatim from `fnd/l8gnd` at `226e9143`, likewise |
| `../../../ecad/tools/tests/test_l5r2.py` | The test |

Run order on 3 October 2026: `apply_l5r2.py <target> --write` for the two targets; `../l5pwr/l5pwr_contracts.py` made to read its
targets at `1e18a1ca` and its output regenerated; `regen_out.py` for this record's output; `env -C v2/ecad/tools/tests python3 run.py
test_l5r2 test_l5pwr test_public_hygiene test_interfaces test_l4e5 test_l4e11`.
