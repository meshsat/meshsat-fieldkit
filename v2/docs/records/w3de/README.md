# Drafts of board D and E stream w3de (MESHSAT-1357, 27 September 2026)

Files outside w3de's own (gen_sch_d.py, gen_sch_e.py, boards/d.json, boards/e.json and the D and E schematic-phase
files regenerated from them). Each patch script edits by asserted old text and refuses a file that changed under it;
each takes the tree root holding `v2/` as its only argument. No em dashes; prototype framing: nothing is built.

**EQ-16 LANDS IN ONE INTEGRATION (pass 2 of the independent check).** Board E's half of EQ-16 is in w3de's own
`gen_sch_e.py` (J_BLK pins 1 to 4 to GND, P_VR, P_VN) and cannot land alone: with only w3de's files `check_contracts.py`
reads FAIL, "dock 2x6 contact map identical on A (J_DOCK) and E (J_BLK)" DIFFERENT on pins 1 to 4 (A VIN_RAW, E GND),
and the committed set would join board A's VIN_RAW to board E's GND across four 813 contacts. So board A's half is
delivered as ready files (`a-half/`, regenerated on the KiCad box with parity) and `apply_registry.py` refuses to rebind
unless board A's files are in the tree beside D's and E's. If board A's half cannot land in the same integration, hold
w3de's `gen_sch_e.py` hunk for J_BLK, P_VR and P_VN (and E's netlist with it) until it can: never land E's half alone.

## Integration order (as run in the scratch clone below)

1. w3de's own files from the worktree (`git diff --name-only 38dcd764`: gen_sch_d.py, gen_sch_e.py, boards/e.json, and
   the D and E schematic, netlist, prov and intent files).
2. `patch_pcb_sensitive_e.py`, `patch_test_rails_census.py`, `patch_energy_chain.py`, `patch_gen_pcb_e3.py`.
3. `a-half/install_a_half.py <tree> --check`, then `a-half/install_a_half.py <tree>` (runs `patch_gen_sch_a_dock.py`,
   copies board A's four regenerated files; every sha256/16 asserted before and after).
4. `patch_check_contracts_dock.py`, `patch_interfaces_if_ae_dock.py`; `patch_assembly_dock.py` waits for E5's holes
   (the scratch run below was taken both with and without it).
5. `apply_registry.py <tree>` LAST, then `rules_lib.py requirements` and `rules_render.py --requirements`.

| Draft | For the owner of | Why | Apply |
|---|---|---|---|
| `patch_pcb_sensitive_e.py` | `v2/ecad/tools/pcb_sensitive.yaml` (board e) | S-47 removed the net TRK_LSENSE: the switch list takes **TRK_CS** in its place (the common source of the bottom FETs Q4 and Q5 above R5, carrying their chopped current, declared as board A declares its LM5176 CS nodes under F-PR-04), and the two Kelvin rows follow (R5.1/R6.1 on TRK_CS, R5.2/R7.1 on GND). Without it `test_kelvin_check` fails on the regenerated netlist and `switch_list` reads FAIL, "CANDIDATE WEAK TRK_CS: Q4,Q5" | with w3de's files |
| `patch_test_rails_census.py` | `tests/test_rails_census.py` | the replay test asserted AMP_HPVSS and TRK_LDO33 stay undeclared (a rule about history); it now removes the missed supply from its copy of the intent first | with w3de's files |
| `patch_energy_chain.py` | `pcb_energy_chain.yaml`, `tests/test_energy_chain.py` | SHORE_INPUT 8.0/10.0 A to 6.15/6.15 A (F-IN-02), its stale clamp note, the DOCK_BLOCK citation of the Mill-Max page; a test holds the stage to gen_sch_e.py's `_VEH_T`/`_VEH_P` (ast); and a synthetic FUSED-stage fixture at the table limit (10 A atof287 fuse, 8.0 A at 56 C, read at the 65 C column) holds the "no margin against the maker's own figure" note, with 7.5 A as its no-note side | any time |
| `patch_gen_pcb_e3.py` | `gen_pcb_e3.py` (board E layout) | PATTERNS TRK_LSENSE to TRK_CS, C63 and C64 in the TRKS region, a marker for P_VR/P_VN's FIXED places (chosen with E5's holes) | before E's next placement |
| `patch_gen_sch_a_dock.py` | `gen_sch_a.py` (board A) | board A's half of EQ-16: J_VR1-4, J_VN1-4, J_DOCK 1-4 to GND, VIN_RAW's source, and VIN_RAW's figure 12.31 to 14.10 A with its note (R8E-N01; unconditional since pass 2, so both ends of IF-AE-DOCK declare one figure) | through `a-half/install_a_half.py` |
| `a-half/` (`install_a_half.py` and board A's four regenerated files) | board A (`pcb-a-power.kicad_sch`, `out/pcb-a-power.net`, `.net.prov.json`, `-intent.json`) | written by `handover_exports.py regen --letters a` (full.sh's schematic chain, PHASE=A65) in an extraction of 38dcd764 with the patch applied; the same command on the untouched extraction reproduced main's files (`parity/a-draft/main-reproduces-main/`) | in the same integration as w3de's files |
| `patch_check_contracts_dock.py` | `check_contracts.py` | three dock checks for EQ-16 (A's eight power pins, E's two pads, no VIN_RAW on an 813 contact) | with board A's half |
| `patch_interfaces_if_ae_dock.py` | `pcb_interfaces.yaml` (IF-AE-DOCK) | the contract after EQ-16, finding W3DE-DOCK-R1 (ground-current sharing) | with board A's half |
| `patch_assembly_dock.py` | `v2/docs/ASSEMBLY.md` | the block's second 12 AWG pair; J_BLK 1-4 carry no VIN_RAW | with E5's half (it describes E5's two new holes) |
| `apply_registry.py` | `pcb_requirements.yaml` | three session choices (EQ-16; the tracker's MODE and bypasses; PWR-001's kinds), three open items (what of EQ-16 is still in flight, W3DE-DOCK-R1, PWR-001's three undecided nets), S-47's progress, and the rebinding of the ELEVEN records bound to board D's or E's netlist, gen_sch_e.py, board A's netlist or gen_sch_a.py (CON-010, CON-016, CON-018, CON-019, CFL-002, CFL-005, CFL-013, CFL-014, CFL-015, CFL-016, REQ-036), with the `source` lines of CON-018, CON-019, CFL-005 and CFL-014 following gen_sch_a.py's moved lines (and CFL-015's two other files when the drafts above changed them); it refuses unless every regenerated file, board A's included, is at its asserted sha | LAST; then `rules_render.py --requirements` |
| `ecss-6.11-transcription.md` | `v2/vendor/standards/ecss-q-st-30-11c-rev2-2021-06-23.md` | the connector clause EQ-16 cites (Table 6-10) | any time |
| `EQ16-dock-vin-raw.md`, `dock_contacts.py` | the record and its arithmetic | the decision, the alternatives with the one-open case and temperature, the E5, layer 7 and ARCHITECTURE.md items | reference |
| `net_compare.py`, `intent_compare.py`, `parity/` | the parity proof | an independent netlist comparison (every component, every net's pins) and the intent diff; `expected-{a,d,e}-netlist.json`; `a-draft/` board A's regeneration records | reference |
| `run_gates.sh` | the readings | the schematic-phase gates on D and E into a verdict directory, on a scratch tree | reference |

## Verified (pass 2, 27 September 2026, in a shared scratch clone of main at 38dcd764, which has a git index)

Every draft above applied in the order above, board A's half included. Readings are in the worktree's `scratch/pass2/`.

- `rules_lib.py requirements`: 132 records, 0 errors, 0 warnings; `rules_render.py --requirements` wrote
  REQUIREMENTS-TRACE.md; `apply_registry.py`: SC-17, SC-18, SC-19 added, S-48, S-49, S-50 opened, 11 records rebound.
- Tests that read the touched files (`run.py` test_requirements test_kelvin_check test_rails_census test_energy_chain
  test_switch_list test_sensitive_nodes test_prelay test_interfaces test_contract_attribution test_block_contract
  test_netlist_provenance test_sch_prov test_stale_netlist test_signal_class test_board_file_format
  test_smbus_lead_contract): 211 passed, 0 failed, 7 skipped (pcbnew-only fixtures and the gitignored rule-audit).
- `check_contracts.py`: PASS 99 of 99 (A 34, B 60, C 7, D 11, E 14, P 9). Negative control, main plus w3de's own files
  only: FAIL 1 of 96, the dock map DIFFERENT on pins 1 to 4; main alone PASS 96 of 96.
- `switch_list.py` board E: main PASS of 2 (6 declared); w3de's files without the sensitive patch FAIL of 3 ("CANDIDATE
  WEAK TRK_CS: Q4,Q5"); with it PASS of 3, 6 declared, 0 undeclared. Board A unchanged by the dock half (FAIL of 24 on
  FE_BLEED_G on main and after: a pre-existing candidate, not this stream's).
- `energy_chain.py`: PASS of 98, SHORE_INPUT "F1 carries 6.2 A where atof287 allows 8.0 A at its 65 C column", no
  no-margin note. The at-limit fixture fails when energy_chain.py's `_margin` branch is deleted (mutation run) and
  passes on main's yaml; the two stage fixtures fail on main's yaml for their intended reason (8.0/10.0 A).
- Board A's gates on the regenerated files against main's: intent_rails FAIL 9 of 39 on both (pre-existing, board A's
  own undeclared nodes), VIN_RAW "source J_VR1, J_VR2, J_VR3, J_VR4 and 3 load(s)" PASS; power_path, power_sequence and
  derate PASS on both.
- `apply_registry.py` in a tree with w3de's files and no board A half: refused at the rebind ("pcb-a-power.net is at
  3a786cf31614fe63 ... install ... board A's half ... first"), the registry untouched.
