# l8gnd: GND-002's four board changes and the SLOT_EN hold, drafted into the generators (Layer 8, MESHSAT-1357)

Layer 8 record `l8gnd`, 3 October 2026, branch `fnd/l8gnd` from the Layer 4 consolidation line at `22cb4c16`. Prototype design,
generator text and netlists: nothing is built, powered or measured, and **nothing here is applied to the tree**. Every apply
script refuses the repository's own generator until a `RELEASE.md` beside it names an accepted check of this record; none exists.

| File | What it is |
|---|---|
| `L8-GND002-SLOTEN.md` | the record: the two Layer 5 items (LAYER-STATUS rows 5.12 and 5.6) and their definitions; GND-002's four changes drawn on boards A and B with their makers' bases and the check its tool reads; the SLOT_EN hold as three keepers on board A with its arithmetic, its states through the hot stop, and the firmware and contract texts drafted; the composition proof; the proposed row texts; findings for other owners; what stays owed |
| `apply_gen_sch_a_gnd002.py` | DRAFT, board A: the CHASSIS net with its 0 Ohm link R229 to GND (change 1) and the strap pad H1 on the land below (change 4); release-guarded |
| `apply_gen_sch_b_gnd002.py` | DRAFT, board B: C33 (1n 2kV) and J_ETH's shield from GND to CHASSIS (changes 2 and 3, Microchip DS00004151A p.10); release-guarded |
| `apply_gen_sch_a_hotr1.py` | DRAFT, board A: the SLOT_EN hold, U43 (SN74LVC08A) with R230 to R232 (4.7 k) and C240 as keepers on SLOT_EN1..3; release-guarded |
| `footprints/ChassisLug_M4_CHASSIS.kicad_mod` | the land H1 names: plated hole 4.3, 12.0 ring both sides, pad 1; copied into `meshsat.pretty` at release |
| `check_gnd002_netlist.py` | the check GND-002's tool reads on a netlist, parsed, board by board; NOT DRAWN on the committed netlists today |
| `inputs/` | Layer 5's SLOT_EN1..3 and HOT_R1 rows of `power_line_states`, copied byte for byte from `fnd/l5pwr` at `1e18a1ca` (`inputs/SOURCES.txt`: lines, sha256 of the excerpt and of the whole file) so that the record reads them from its own tree |
| `l8gnd_drafts.py`, `l8gnd_drafts.out` | what each draft adds, the keeper's arithmetic, the composition on board A in L4-E9's order and in reverse with the tree's other board A drafts (s117's two in the base, d8dec31's mainpb last), the designator disjointness, board B, the netlist check; inputs pinned by sha256; regenerated with `_bin/regen_out.py` |

Tests: `v2/ecad/tools/tests/test_l8gnd.py` (`python3 run.py test_l8gnd test_public_hygiene` from the tests folder). No held-back
sheet: every document quoted is in `v2/vendor/`.
