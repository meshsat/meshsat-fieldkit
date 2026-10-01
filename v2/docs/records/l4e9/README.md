# l4e9: the connected power architecture and Layer 4's closure gate (layer 4 task L4-E9, MESHSAT-1357)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured. This folder takes the selected power
architecture (A1 under the owner's D-06, A2 recorded as a proposal) as one connected design: every interface between its blocks
reconciled (voltages, currents at the modes, losses, thermal basis, protection on each side, the record that settles it), the
simultaneous-operation, startup and fault traces across the stages, Layer 4's closure gate for the power architecture, the
downstream register and the Layer 5 handover. It edits no generator, registry record, Layer 3 file, `pcb_interfaces.yaml`,
`HW-FW-CONTRACT.md` or other record.

| File | What it is |
|---|---|
| `L4-POWER-ARCHITECTURE.md` | The page: the selected architecture and its block diagram, the interface table, simultaneous operation, startup, faults, the decisions this record takes (SESSION), the closure gate, the assumptions register, the register's summary and release order, the endurance statement, what stays PENDING or CONDITIONAL |
| `l4e9_power_path.py` | The executable reconciliation. It reads every figure from the generators (syntax tree), board A's netlist, the records' committed outputs (L4-E4 to L4-E8, the energy replay, s120, the power budget, the load trace), the makers' documents (pdftotext) and the tree's configuration and contract files, each pinned by sha256; L4-E8's output is read from the tree or from `fnd/l4e8` at `3c8f7a1f` (accepted). It prints each interface row with its checks and their evidence classes, the computed traces, the endurance statement and the gate, and refuses (exit 4) a row without both sides, a gate whose PASS rests on a conditional row, or a register row without an owner and an acceptance. Run from the repository root: `python3 v2/docs/records/l4e9/l4e9_power_path.py > v2/docs/records/l4e9/l4e9_power_path.out`. A few seconds; needs pdftotext and PyYAML |
| `l4e9_power_path.out` | Its output, committed; the script reproduces it byte for byte |
| `DOWNSTREAM-REGISTER.md` | Every implementation change, layout constraint, test, piece of evidence and release record the architecture hands downstream, each with one named owner, an acceptance, a state and its step in the release order |
| `LAYER5-HANDOVER.md` | The interfaces this architecture creates or changes, each with the text proposed for `pcb_interfaces.yaml` or `HW-FW-CONTRACT.md` (drafts for Layer 5; neither file is edited) |
| `apply_gen_sch_e_q1.py` | DRAFT for board E's generator owner: the vehicle entry's ideal-diode FET Q1 to the CSD19532Q5B (100 V, C473333) on Q7's land, because L4-E5's raised tracker ceiling puts up to 66.15 V across it on a reversed input. Default `--check`, writes only with `--write`, refuses a second application and the tree's own generator until a `RELEASE.md` here reads "released: yes" and names an accepted check. Composes with d8dec31's `apply_gen_sch_e_cin.py` and L4-E7's three drafts in either order. Never applied to the tree |
| `README.md` | This list |

**PENDING:** L4-E7R (the 100 W control decision on board E and the solar entry's surge protection, `fnd/l4e7`) is not yet
landed; the rows and register items that wait on it read PENDING and are re-run when it lands.

The predicates are held by `v2/ecad/tools/tests/test_l4e9.py`. Run it with
`env -C v2/ecad/tools/tests python3 run.py test_l4e9 test_public_hygiene`; `test_l4e9` reports 15 tests.
