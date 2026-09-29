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
- 02:00 to 02:20 Board C's L1 lamp row first. New read-only tool `tools/lamp_check.py` (parses C's and B's committed
  netlists, classifies parts with the instrument's own firmware classes): L-1 to L-4 PASS on C `3fddbb3edcd4248a` and B
  `21a1f74a3ec1ae28` (`readings/set9/lamp-check-set9.txt`). One firmware pin sits one resistor from the path (GPIO26
  behind R15 10 k on `LED_RAIL_SW`): it can neither light the lamp nor darken it in DAY or NIGHT.
- 02:10 `tools/fault_levels.py` fixed: a FET's gate current is now looked up by the part's identity (the value's
  leading token), not by any word of its description. Board C's Q7 (Si2300DS, whose value says "like the 2N7002
  symbol") had been read with the JSCJ 2N7002's 25 C row; it now reads the Vishay row (also 25 C only, so the row's
  verdict is unchanged, UNDECIDED). The only line that moved is the lamp's (b) row. `--tag` names the output files.
- 02:20 Finding D4E-F1 (new, L4 case (2) on board C): with board C's +3V3 in its 0 to 1.65 V band and the toggle at
  EMCON, U9's output is unspecified up to 1.65 V on `EMCON_HW`, which board B's readers (VIL 0.8 V at VCC 3 to 3.6 V)
  cannot be shown to read LOW; every board B row reads `EMCON_HW` alone. EMCON.md's L4 row lists C's U9 among the parts
  of case (2) but no section closes or assigns it. Remedy drafted for board C's author (see README and the apply script).
