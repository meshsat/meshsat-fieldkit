# l4e5: source control for board A's charger on the ORed bus (layer 4 task L4-E5, MESHSAT-1357)

Prototype design, desk arithmetic. This folder takes implementable choice 1, SOURCE CONTROL, of
`../l4e/L4-ENERGY-ARCHITECTURE.md` (finding A-2 and its per-source closure) and turns it into a decision, per-source envelopes,
contract rows and bench rows.

| File | What it is |
|---|---|
| `L4E5-SOURCE-CONTROL.md` | The one page: the decision (H3, a hardware line on U3's ILIM_HIZ pin with a knee into HIZ, and the tracker's ceiling raised) and its reasons; the candidates not chosen; the per-source envelopes; the startup, source-change and stale-telemetry behaviours, steady state and transients apart; the consequence for L4-E4; what stays INCONCLUSIVE; the bench rows |
| `l4e5_source_control.py` | The script, run from the repository root: `python3 v2/docs/records/l4e5/l4e5_source_control.py > v2/docs/records/l4e5/l4e5_source_control.out`. Section 0 runs four checks before any figure: `../l4e4/l4e4_limits.out` and `../r11dep/r11_dep.out` reproduced byte for byte in child processes; `l4e4_limits.compute()` rendering its record in-process; `l4e_replay.main()` printing its record in-process with its locals captured. The figures that follow come from those functions, not from retyped constants: the netlist facts, the makers' rows read back from the held PDFs, each candidate's envelope, the solar energy each gives up through the replay's `run()` and `meanday()`, the chosen rule's values and the L4-E4 re-run. About three minutes |
| `l4e5_source_control.out` | Its output, committed |
| `apply_fw_a16.py` | DRAFT for the coordinator. It restates FW-A16 in `v2/docs/HW-FW-CONTRACT.md`, adds FW-A18 and V-A06 to V-A10, and touches FW-E04, FW-C01, section 3.1's heading and the change record. Usage: `apply_fw_a16.py TARGET [--check \| --write]`. The default `--check` writes nothing, and a second application is refused. It was run only on scratch copies, never on the tree |
| `checks/astra-check-l4e5-1.md` | The engineering collaborator's one check (NOT YET: B1, V-A09's HIZ thresholds; B2, a telemetry fault-injection row; B3, the 49.7 W boundary restricted to H3; two minors), filed by the coordinator. The page's last section, "The check, and what changed", maps each item to its change |
| `checks/astra-check-l4e5-2.md` | The collaborator's targeted recheck (NOT YET: HIZ release stated as conversion; V-A10's boot case forbidding FW-A16's initialization), filed by the coordinator; answered in the page's same section |
| `README.md` | This list |

The predicates are held by `v2/ecad/tools/tests/test_l4e5.py`. Run it with
`env -C v2/ecad/tools/tests python3 run.py test_l4e5`; it reports 17 tests.
