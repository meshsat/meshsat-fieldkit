# Drafts of stream w4c (board C: EQ-25 and PWR-001; MESHSAT-1357, 27 September 2026)

Stream w4c's own files are in the worktree's diff against 91894cd7: `v2/ecad/tools/gen_sch_c.py`,
`v2/ecad/tools/boards/c.json` and board C's four regenerated files (`v2/ecad/pcb-c-display-c8/pcb-c-display.kicad_sch`,
`out/pcb-c-display.net`, `out/pcb-c-display.net.prov.json`, `out/pcb-c-display-intent.json`). Everything here belongs to
another writer or is a record; each script edits by asserted old text, refuses a file that changed under it, and is
idempotent by its own marker. No em dashes; prototype framing: nothing is built, every reading is a desk reading.
The decisions, figures, readings and parity are in `w4c-decisions.md`.

## Integration order (as run in scratch clones of main 91894cd7 and of main 62f26a44 with w4c's files, on the KiCad box)

1. w4c's six files from the worktree.
2. `apply_registry.py <tree>` (`--dry-run` first): one open item at the next free S-nn, W4C-F5 (U5's headroom under the
   e-paper boost's 0.5 A class figure, and with it +5V's peak, read at bring-up), three session choices at the next free
   SC-nn, S-64 closed by the first, the four records bound to board C's netlist rebound (REQ-012, CON-021, CFL-016,
   CON-016), and RF-002's coverage row given the reading with board C's fix. The ids are taken where it runs: S-77 and
   SC-58 to SC-60 on 91894cd7, S-80 and SC-64 to SC-66 on 62f26a44 (`fnd/rel2`'s records are there). It refuses a board C
   netlist other than 3fddbb3edcd4248a (the pass-2 regeneration).
3. `patch_docs.py <tree>` (after step 2; it reads the ids from the registry): PANEL.md (section 1's EMCON logic row,
   section 3's GPIO 26 row, section 6's TX_INHIBIT_n row), EMCON.md (section 2's Source, conductor and pull-down
   bullets, section 4.1's Default bullet, section 4b's W3T-F1 paragraph), ARCHITECTURE.md (section 6.2's TX_INHIBIT_n
   row), ENGINEERING-QUESTIONS.md (EQ-25's index row, attempts and next action; EQ-19's board C sentence with W4C-F5's
   item), HW-FW-CONTRACT.md (section 4's `fnd/w4c` row), and the rebinding of every record bound to an edited document,
   which the script finds itself and refuses to leave stale: the five on PANEL.md and the seven on EMCON.md on both
   trees; none binds ARCHITECTURE.md, ENGINEERING-QUESTIONS.md or HW-FW-CONTRACT.md.
4. File `vendor/ultrachip-uc8253c-a0.6.pdf` as `v2/vendor/pdi/ultrachip-uc8253c-a0.6.pdf` with `sources-w4c.yaml`'s
   entry before `owed:` in `v2/vendor/SOURCES.yaml` (the session choice for PWR-001 on board C cites that path).
5. `python3 rules_lib.py requirements` then `python3 rules_render.py --requirements` in `v2/ecad/tools`; then the
   integration recipe (commit the config inputs, then rules_status and rules_render), and the consolidated re-take of
   board C and of RF-002 on boards A to D in the tree.
6. For the diagrams writer: `v2/docs/diagrams/tools/build.py` (the arch-* diagrams read ARCHITECTURE.md, control-lines
   and power-tree read board C's netlist; see `tests-run.txt` for `build.py --check` before and after).

Verified in both scratch clones (pass 2, after the independent check): `rules_lib.py requirements` 144 records, 0 errors,
0 warnings; `rules_render.py --requirements` wrote REQUIREMENTS-TRACE.md; a second run of both scripts changes nothing;
`extract_mermaid.py --check` reads every Mermaid source current (the edit touches no diagram block). Tests that read the
touched files (70 modules by name, pcbnew importable): 1258 passed, 0 failed, 10 skipped on 91894cd7 and 1262 passed, 0
failed, 10 skipped on 62f26a44, every skip for want of gitignored or box-absent evidence (`tests-run.txt`).
`applied-preview.diff` and `applied-preview-62f26a44.diff` are what steps 2 to 5 wrote in those clones, for review before
applying.

| Draft | For the owner of | Why not applied by w4c | Apply |
|---|---|---|---|
| `apply_registry.py` | `v2/ecad/tools/pcb_requirements.yaml`, `pcb_rules_coverage.yaml` | one owner per file | step 2 |
| `patch_docs.py` | `v2/docs/PANEL.md`, `feasibility/EMCON.md`, `ARCHITECTURE.md`, `handover/ENGINEERING-QUESTIONS.md`, `HW-FW-CONTRACT.md`, and the rebinding in `pcb_requirements.yaml` | one owner per file | step 3 |
| `vendor/ultrachip-uc8253c-a0.6.pdf`, `sources-w4c.yaml` | `v2/vendor/pdi/`, `v2/vendor/SOURCES.yaml` | the vendor tree's owner | step 4 |
| `w4c-decisions.md` | the record (file under `v2/docs/records/w4c/`) | a record | with the rest |
| `readings/` | the record: every verdict before (main 91894cd7) and after (candidate) for boards A to D, the walk's report, every fail-safe state of TX_INHIBIT_n, the re-take driver's logs | scratch readings, never the tree's evidence | with the rest |
| `applied-preview.diff`, `applied-preview-62f26a44.diff`, `tests-run.txt` | the record: what steps 2 to 5 wrote in the scratch clones of 91894cd7 and 62f26a44 (board C's generated files left out), and the test runs | a record | reference |
| `parity/` | the record: regen.json of main and candidate, regen_compare pairs, `netcmp_w4c.py` with its expected-change lists and results (candidate against main and against pass 1), `intent-diff.json`, the box drivers `p2_run.sh` and `p2_pack.sh`, `fs_levels.py`, `rt_table.py` | a record | with the rest |

## Not done here, and why

- The consolidated re-take in the tree: the readings in `readings/` were taken under `--verdict-dir` in a scratch clone
  on the box, so rules_status reads none of them; the integrator's re-take makes them current.
- EPD_VCC's typical current is 20.2 mA from the driver's maker plus 10 mA INFERRED, and what U5 carries through a
  refresh (W4C-F5) is not stated by any held document: the open item `apply_registry.py` adds is read at bring-up (a
  TEST-PLAN row for its owner). +5V's 1.0 A peak and `pcb_energy_chain.yaml`'s B_PANEL_5V peak_a follow that reading,
  not this stream (a 1.21 A figure would read board B's F1 opening in normal use on a microsecond current).
- The diagrams (step 6): `build.py` renders through mermaid-cli and a browser, which this stream does not run; the
  arch-* diagrams' Mermaid blocks are not touched by the ARCHITECTURE.md edit, and `control-lines.md` still lists R14 10k
  and no R50 until the diagrams writer re-renders it from the new netlist.
- The firmware threshold for RAIL_SENSE ('present above 1.25 V') is drafted into PANEL.md for its writer; the panel
  firmware (MESHSAT-837) reads it.
- C25804's stock read 0 on 27 September 2026 (W4C-F3): the order owner's, nothing changed here.

## Ids taken at the r8int6 integration (corrected at integration)

The registry script ran at the r8int6 integration of 27 September 2026 (set 6 of the handover), where other branches had taken the numbers this record names as drafted; the ids it took there, read back from the registry by each record's own text: EQ-25 (W4C-D1) is SC-67; PWR-001 on board C (W4C-D2) is SC-68; W4C-F1 (W4C-D3) is SC-69; W4C-F5 is S-83. Where this record names another number for one of them, the id here is the one the registry holds.
