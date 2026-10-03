# l6r2: exact parts for the generic rows of the six boards (Layer 6 criterion 6.1, MESHSAT-1357)

Prototype design: nothing is bought, built, powered or measured. The rows are the committed netlists' fitted parts without an
LCSC field (the identity tool's reader, `part_identities.rows`), board by board in the order A, E, P, D, C, B. Each distinct
selection (the identity tool's key and requirements) is classified; the GENERIC ones (multilayer ceramic capacitors, resistors,
ferrite beads, small diodes of a generic type, 0603 indicator LEDs) get an exact part (maker, MPN, LCSC code) from a dated
public reading of JLCPCB's parts library, checked property by property; ICs, modules, transistors, named inductors, connectors and
mechanical parts are not re-selected and are listed as findings; a requirement the generator and the intent leave open is a
finding with its line, never a guess. Based on `fnd/int28` at `a1f696de`. No generator, Layer 4 record, `pcb_interfaces.yaml` or
`HW-FW-CONTRACT.md` is edited.

| File | What it is |
|---|---|
| `L6R2-PASSIVES.md` | The page: the method and its rules, per board the lines covered and open, the findings, the drafts and their composition, the criterion |
| `l6r2_passives.py` | The selector and its printer, run from the repository root: `python3 v2/docs/records/l6r2/l6r2_passives.py > v2/docs/records/l6r2/l6r2_passives.out` (regenerate only through `_bin/regen_out.py`). It reads only this tree: the netlists and intents through the identity tool, `lcsc_fill.py`'s MAP (by parsing), the certified table, the identity table, the catalogue reading in `inputs/`; it runs the copied BOM reader on the six netlists; it proves each draft's composition with the pending drafts of its generator on scratch copies. `--plan`, `--identities`, `--draft X`, `--write-drafts` |
| `l6r2_passives.out` | Its output, committed |
| `read_catalogue.py` | Takes the reading `inputs/jlc-parts-2026-10-03.json`: JLCPCB's public parts search for every code the design carries on an uncoded generic row and every keyword the selector builds (no login, no cart) |
| `inputs/bom_from_netlist.py` | A copy of `v2/docs/handover/supplier/bom_from_netlist.py` at `e2a8df59` on `fnd/int27` (the supplier package's per-board BOM reader), sha256 `687c4acafacd96d22fa89dd6cd4786280f7aeb3548c3537ece3d5389ab906cc1`; the script refuses a copy with another sha256 |
| `inputs/jlc-parts-2026-10-03.json` | The catalogue reading (codes and keyword searches with model, brand, package, stock, library, preferred flag, attributes, description and price tiers) |
| `l6r2_apply.py` | The six drafts' shared logic: the table inserted once before `import schlayout, time as _time`, keyed by designator and the committed value; the release guard; refusals |
| `apply_gen_sch_{a,e,p,d,c,b}_lcsc.py` | The six DRAFTS, one per board, each carrying its board's table (rendered by `--write-drafts`); release-guarded by `RELEASE.md`; NOT applied |
| `RELEASE.md` | The drafts' release record: `released: no` |
| `apply_part_identities_block.py` | Puts the block `drafted_identities_l6r2_passives` into `v2/ecad/tools/pcb_part_identities.yaml` outside `selections:` (applied on this branch), or removes this block only |
| `README.md` | This list |

Also on this branch: `v2/ecad/tools/tests/test_l6r2.py` (the predicates); the block in `pcb_part_identities.yaml`; round 1's
`l6pwr/apply_part_identities_block.py` now removes only its own block (it cut to the end of the file, which would have taken this
record's block with it).

Run the tests with `env -C v2/ecad/tools/tests python3 run.py test_l6r2 test_part_identities test_public_hygiene test_l6pwr`; on
3 October 2026 they read 56 passed, 0 failed, 0 skipped (with the Uniroyal sheet fetched by w5identc's `fetch_held_back.py`;
without it, the DECODED Uniroyal bindings read UNREAD and test_part_identities skips two).
