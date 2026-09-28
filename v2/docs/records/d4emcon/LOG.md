# Stream d4emcon, running log (MESHSAT-1357, FEA-002 layout-entry stage)

Newest last. Times CEST, read from `date`. Prototype framing: nothing is built; every reading is of a committed netlist
or a maker's document.

## Resumed 29 September 2026 (brief `_runs/claude/d4emcon/20260929T0200/BRIEF.md`)

- 01:56 Brief and WORKER-RULES read. Branch `fnd/d4emcon` at `88013380` (4 commits ahead of main, 175 behind).
- 01:55 Main (`c5f93464`, set 9) merged with `--no-ff` under the owner's identity: merge commit `fe501d26`, no conflict
  (main had touched none of `tools/tx_inhibit.py`, `tests/test_tx_inhibit.py`, `EMCON.md` or this folder since the
  branch point `73ae2f21`).
- 01:55 to 01:58 Re-run on main's committed netlists, on this host (pure Python, no KiCad needed: the netlists are
  committed files and the tools parse them with `tx_inhibit.parse_netlist`): `tools/path_walk.py`,
  `tools/walk_report.py` (RF-002's walk, `tx_inhibit.py` sha256/16 `326d0a4832273004`, this branch's) and
  `tools/fault_levels.py`. Output under `readings/set9/`. Every reading is byte-identical to the set 6 reading apart
  from the two netlist hashes that moved (A `0a2b59087bcc2678` to `599ee964a9c23d6e`, B `028997a6c5e8810f` to
  `21a1f74a3ec1ae28`). What moved on the netlists is in `readings/set9/WHAT-MOVED.md`.
