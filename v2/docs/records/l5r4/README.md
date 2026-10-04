# l5r4: Layer 5's round 4, a compute module lost while running (MESHSAT-1357, set 29, 3 October 2026)

Prototype design: nothing here has been built, powered or measured. The panel firmware's finding F-14 decided: one slot-fault rule
for a compute module lost at start-up and one lost while running, written into `v2/docs/PANEL.md` section 5 and
`v2/docs/HW-FW-CONTRACT.md` (FW-C05, FW-C02, V-C05, the change record) with `CONOPS.md` section 4e as its source. Branch `fnd/l5r4`
from set 28's `92a5c7d8`; Layer 5's author of the panel contract. The same day's follow-up (the panel firmware's F-15 and S-37, from
`fnd/fw-r4` at `8d396dfd`): a power-on reset is read as `CHIP_RESET`'s `HAD_POR` set and the watchdog's `REASON` zero (RP2040 datasheet
2.12.1, 2.12.7, 4.7.1, Table 548), and the slot record sits beside the wipe journal, never inside it; `apply_l5r4.py` carries the
final texts.

| File | What it is |
|---|---|
| `L5-R4-SLOT-FAULTS.md` | The page: the finding, the evidence in order (generators, netlist, CONOPS, requirements, the keeper, the RP2040's resets), the rule as written, the decision (SESSION, F-14) with what was rejected, what changed, the registry's rebind, what the firmware must change, the checks |
| `apply_l5r4.py` | The patch script, run once on the tree by the author; idempotent (`--check` on the tree reads "already applied"; on the files at `92a5c7d8` it checks OK) |
| `apply_l5r4_rebind.py` | The integrator's script: CFL-001, CFL-005, CFL-014, CFL-015 and CFL-016 rebound to the new PANEL.md, refusing unless only section 5 differs and every reading's ground is byte-identical; not run on this branch |
| `../../../ecad/tools/tests/test_l5r4.py` | The test: CONOPS and PANEL.md agree, FW-C05 states the same rule, REQ-062's case is in it, the scripts behave |

Run order on 3 October 2026: `apply_l5r4.py --write`; `regen_out.py` for `../l5r2/l5r2_interfaces.out` and `../l5r2/l5r3_panel.out`
(their pin lines); `env -C v2/ecad/tools/tests python3 -B run.py test_l5r4 test_l5r2 test_l5pwr test_fw_panel test_public_hygiene`.
The integrator then runs `apply_l5r4_rebind.py --write` and the re-pins of the records that pin `PANEL.md` or `HW-FW-CONTRACT.md`
(L4-E9 `hwfw`, L4-E11 `hwfw` and `panel`).
