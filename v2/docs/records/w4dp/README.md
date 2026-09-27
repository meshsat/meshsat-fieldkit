# Stream w4dp: boards D and P and the pack-protection table (MESHSAT-1357, 27 September 2026)

Prototype design: nothing here has been built, bought for assembly or measured. Every figure is a maker's, read from the
filed sheet named beside it. Worktree `wt/w4dp`, branch `fnd/w4dp` at main `91894cd7`, nothing committed (the integrator
commits). No em dashes.

## 1. The files this stream owns (in the worktree, uncommitted)

| File | sha256/16 | What changed |
|---|---|---|
| `v2/ecad/tools/gen_sch_d.py` | `54f17c8187d3bd19` | D2 carries LCSC C81598 (SEMTECH ELECTRONICS 1N4148W) with its sheet cited; RLY_K declared a node at 6.5 V (W4DP-D1, D2) |
| `v2/vendor/power/st-semtech-1n4148w-c81598.pdf` | `54de8e4089bb8221` | new: the maker's sheet as LCSC serves it for C81598 (Rev 05, 20/09/2016) |
| `v2/ecad/pcb-d-aprs-d9/pcb-d-aprs.kicad_sch` | `823b03952b3723ea` | regenerated: D2's LCSC property |
| `v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net` | `7a2c0ac2190b141a` | regenerated: D2's LCSC field and property only |
| `v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net.prov.json` | `45f72467c66308d7` | regenerated (generator identity `7115ba51403902b8`) |
| `v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs-intent.json` | `8d9f3b2256521b0d` | node RLY_K added |
| `v2/ecad/tools/gen_sch_p.py` | `740817ada5c8e14a` | PWR-001 block before the bypass entries: 5 rails, 7 nodes; no part, value, net or pin moved (W4DP-D3; FUSE_G and FUSE_GQ restated in pass 2) |
| `v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_sch` | `a58d0eecc7abe768` | regenerated: title-block date only (noise) |
| `v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net` | `760ac6f74d62d194` | regenerated: identical in every component and net's pins (content16 `efe60479293f0004`, as main's) |
| `v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net.prov.json` | `7db0b4941f33f92b` | regenerated (generator identity `d0b17cbd0f545abd`) |
| `v2/ecad/pcb-p-pack-p2/out/pcb-p-pack-intent.json` | `12f92bd3ce7a8264` | rails BAT_F, VCC_F, SEC_VDD, SW, SCP_HTR; nodes PBI, CELL1 to CELL3, FUSE_G (7.7 V), FUSE_GQ (7.6 V) |
| `v2/ecad/tools/pcb_pack_protection.yaml` | `ab1dbc3f3f69aa46` | brought to the drawn circuit (S-45); hardware level judged (W4DP-D4) |
| `v2/ecad/tools/tests/test_pack_protection.py` | `e428e2f9247b083e` | the table held to the netlist both ways; hardware rows and their open findings; main's fixture `t_a_device_the_board_does_not_carry_is_not_a_protection` kept verbatim (pass 2) |

`tools/boards/d.json` and `tools/boards/p.json` needed no change. D's and P's netlist provenance reads current
(`sch_prov.current`) in the worktree.

## 2. Integration order

1. The files of section 1.
2. `patch_test_plan.py <tree>` (TEST-PLAN.md section 5 rows 10 to 14; `test_pack_protection` needs it).
3. `patch_vendor_index.py <tree>` (sources.txt, vendor-status.txt lines for the new sheet).
4. `patch_coverage.py <tree>` (BAT-001 and PWR-001 notes), then COMMIT it before any `rules_status.py` run.
5. `apply_registry.py <tree>` LAST (it asserts every regenerated file's sha, and TEST-PLAN.md's either as main's or as
   patched), then `rules_lib.py requirements` and `rules_render.py --requirements`, then the re-take and `rules_render.py`.

Verified in a scratch copy of the worktree with 2 to 5 applied: `rules_lib.py requirements` 144 records, 0 errors;
`rules_render.py --requirements` and `rules_render.py` write; the suite subset (26 files, 538 passed, 6 skipped) fails only
`test_netlist_provenance`'s git-index fixture, which needs a `.git` the copy did not have and passes in the worktree. In the
worktree without the drafts: 508 passed, 1 failed (`t_every_protection_function_is_in_the_test_plan`, which waits on
step 2 by design).

## 3. Decisions (the session's, under the owner's standing rule of 26 September 2026; never the owner's)

- **W4DP-D1, D2's part.** LCSC C81598, SEMTECH ELECTRONICS LTD. 1N4148W (LCSC brand "ST(Semtech)"), SOD-123, JLC basic,
  stock 5,220,610 on the JLC API of 2026-09-27; the code `lcsc_fill.py` already filled and JLC-CERTIFIED.tsv lists for the
  row "1N4148W coil flyback" / D_SOD-123. Sheet pinning: 1 cathode, 2 anode = KiCad Diode:1N4148W on D_SOD-123; VR 75 V,
  IF(AV) 150 mA, VF at most 1.0 V at 50 mA and 1.25 V at 150 mA. Value text unchanged so the certified row still matches.
  Reversal: another maker's 1N4148W whose sheet this tree holds, if the ordering session prefers one.
- **W4DP-D2, RLY_K a node at 6.5 V.** +5V_TX's 5.23 V v_work plus the sheet's 1.25 V at 150 mA, which bounds the coil's
  at most about 30 mA (Omron G6K 5 VDC: 21.1 mA, 237 ohm +-10 % at 23 C; colder copper lower). Reversal: a load on RLY_K
  that takes its supply from it.
- **W4DP-D3, board P's PWR-001 kinds.** Rails for the supply branches fed through a board part (BAT_F from R5, VCC_F from
  R7, SEC_VDD from R23), for the protection FETs' common drain SW (10 A / 18 A, `series_of` SCP_OUT) and for the fuse
  heater return SCP_HTR (3.5 A declared typical as well as peak: a 60 s event is a steady state for copper, so PI-001 judges
  the heater path, the one current whose loss defeats a protection); nodes for PBI, CELL1 to CELL3 (4.375 V a cell at
  U2's widest OV accuracy, 4.20 V in service) and FUSE_G / FUSE_GQ (7.7 V / 7.6 V bounds: the gauge's FUSE output at its
  8.65 V maximum through its 2 kohm minimum impedance and R30 into R31, or R31 || R32 once JP1 is closed, 7.61 / 7.56 V with
  1 percent resistors at their worst, COUT taken as TI's Active High 6V drive, 'drive to 6V', SLUSEG7D 7.3.6 and 8.2, which
  keeps the node under the bound for any COUT high level up to 7.6 V; 4.25 V with COUT driving). Pass 2 replaced a first
  basis, COUT at its VDD, which fails in the over-voltage state that drives COUT (stack at about 17.3 to 17.5 V, FUSE_GQ
  12.25 to 12.4 V, past the AO3400A's +-12 V VGS). Reversal for the fuse gate: a TI maximum for the 6V drive above 7.6 V, or
  a bench reading of that output above it (TP11 with COUT driving, or TP12, DOUT's identical stage); Q3's gate would then
  need a clamp, a circuit change for the qualified battery review. No electrical change. Reversal per net: a load the declaration does not
  name; SCP_HTR's typical by a tool that judges an event current as such.
- **W4DP-D4, BAT-001's words kept literal.** The table declares decision 40's floor present (it is on the netlist since
  faf8c981), corrects F1 (25 A MINI, Littelfuse 297, not ATOF: BAT-F04) and R10 (the shunt; the thermistors move to J_TS),
  adds U2, F2, Q3, JP1, Q5, RT1, J_TS2, and judges BAT-001's five functions a second time on the parts that act without
  firmware (`level: hardware`) against the same cell limits. The alternative, reading "a protector independent of the gauge
  exists" as meeting BAT-001, would lower the requirement (handover prompt section 2); THERMAL-COORDINATION.md section 8
  already names BAT-001's words (S-45) as the reversal of the choice not to add the OT hold. Reversal: an owner ruling that
  restates BAT-001 for a second level, or the circuit changes of W4DP-F1, BAT-F16 and W4DP-F2.

## 4. Findings

- **W4DP-F1.** The BQ7720700's under-voltage, 2.25 V +-50 mV, is up to 100 mV below the Samsung guideline's 2.30 V
  over-discharge protection minimum (the only released variant whose OV clears the gauge's 4.25 V). Round 4 accepted it as a
  backstop; BAT-001's words do not.
- **BAT-F16** (the packet's, not new): the fixed 70 C (62.7 to 77.5 C, no cold trip) acts only above the cells' 60 C / 45 C.
- **W4DP-F2.** No element acting without firmware opens at or below the cells' 24 A at 3P (F1 opens from 33.75 A in up to
  600 s; F2 is 30 A; the gauge's AFE comparators take their thresholds from data flash).
- **BAT-F20** stays open as it stands (carried on Q1's row and in SW's note; not answered).

## 5. Parity (`parity/`)

- main reproduces main (`main-reproduces-main/`): `handover_exports.py regen --letters d,p` in a clone of 91894cd7 on the
  box: D PARITY (netlist, intent, ERC after noise), P PARITY (schematic, netlist, intent, ERC after noise); w3de's
  independent `net_compare.py` against an empty expected list: ONLY THE EXPECTED CHANGES on both.
- candidate against main (`candidate/`): D schematic, netlist and BOM DIFFERENT by D2's LCSC only, intent adds RLY_K; P
  schematic and netlist PARITY_AFTER_NOISE, intent adds the 12 declarations; `net_compare.py` against
  `expected-d-netlist.json` (D2 `field:LCSC`, `property:LCSC`) and `expected-p-netlist.json` (nothing): ONLY THE EXPECTED
  CHANGES; `intent_compare.txt` lists each added rail and node.
- candidate reproduces candidate (`candidate-reproduces-candidate/`): PARITY on both boards (the final P, after a comment
  tightening, was regenerated again and this run taken on it).
- **Pass 2 (board P only; D did not change).** The three P runs above were taken again on fresh clones of 91894cd7 on the
  box (main from a bundle of `fnd/w4dp`, since the box's own clone predates it) and replace the first pass's P folders,
  which are kept under `parity/pass1-p-superseded/`. main reproduces main: PARITY (schematic, netlist and intent after
  noise; intent identical apart from `written`); net_compare ONLY THE EXPECTED CHANGES. Candidate against main: schematic
  and netlist PARITY_AFTER_NOISE, BOM PARITY, ERC PARITY_AFTER_NOISE, intent DIFFERENT by the 12 declarations only
  (`candidate/p/intent_compare.txt`, with FUSE_G 7.7 V and FUSE_GQ 7.6 V); net_compare against `expected-p-netlist.json`
  (nothing): 85 components, 55 nets, 210 pins on both, ONLY THE EXPECTED CHANGES, content hash `efe60479293f0004` on both.
  Candidate reproduces candidate: PARITY. The netlist file differs from the first pass's only in its `(source ...)` path
  and `(date ...)`; the intent differs only in FUSE_G's and FUSE_GQ's `v_max` and `basis`.

## 6. Readings (`readings/`, schematic-phase re-take driver, `--verdict-dir` on the box, main against the final candidate)

See `readings/moved.txt`. D: PWR-001 (intent_rails) INCONCLUSIVE 0 of 7 to PASS of 7. P: PWR-001 FAIL 6 of 11 to PASS of 11;
BAT-001 (pack_protection) FAIL 1 of 45 ("no second protector") to FAIL 3 of 63 (the three hardware rows); PWR-002
(power_sequence) PASS of 5 to PASS of 10 rails; SI-001 (edge_length) INCONCLUSIVE of 44 signal nets to of 40 (four nets
became rails). Every other reading of the two boards unchanged, RF-002 on D (EQ-25) included.

Pass 2 re-took board P (`--run --board p --verdict-dir` on a box clone holding exactly this worktree's files, committed in
that throwaway clone because the driver refuses uncommitted inputs): the same fourteen readings with the same counts as the
first pass (intent_rails PASS of 11, pack_protection FAIL 3 of 63, power_sequence PASS of 10, edge_length INCONCLUSIVE of
40, derate PASS with 6 judged, the rest PASS). The fuse gate's lower bound moves no count: derate judges no part on FUSE_G
or FUSE_GQ (R29 to R32, C19, JP1 and Q3 are among its 20 unrated parts). `readings/after/pcb-p-pack-p2` is the pass-2
reading; the first pass's is under `readings/pass1-p-superseded/`.

Projection (`projection/`, a throwaway clone with the registry and TEST-PLAN drafts applied, in-place re-take of D and P,
rules_status three times, rules_render --check clean): D 7 layout-entry reasons (was 8), first SI-001; P 5 (was 6), BAT-001
FAIL among them; no board ready for layout.

Pass 2 verification (box clone, every draft applied in the section 2 order, then `rules_lib.py requirements`, 144 records,
0 errors, 0 warnings; `apply_registry.py` took SC-58, SC-59, SC-60 and S-77, S-78 at 91894cd7; `rules_render.py
--requirements` and `rules_render.py`): the 26-file suite subset of the first pass, 545 passed, 0 failed, 1 skipped. In the
worktree without the drafts: test_pack_protection, test_rails_census, test_rails_netlist, test_sch_prov and
test_netlist_provenance 90 passed, 1 failed (`t_every_protection_function_is_in_the_test_plan`, waiting on step 2 by design).
The restored fixture `t_a_device_the_board_does_not_carry_is_not_a_protection` kills the mutant that disables
pack_protection.judge's check 3 (the "no such reference" failure), which the first pass's test file let through.

## 7. Drafts for other owners

| Draft | Owner | Why | Apply |
|---|---|---|---|
| `patch_test_plan.py` | TEST-PLAN.md | rows 10 to 14 (the hardware level, by name) and section 5's closing paragraph | with the table |
| `apply_registry.py` | pcb_requirements.yaml | SC-a, SC-b, SC-c; S-x (the three hardware gaps), S-y (line citations, energy chain's F1); S-45 closed; S-76 progress; REQ-044 and FEA-005 wait on S-x; 12 records rebound | last |
| `patch_coverage.py` | pcb_rules_coverage.yaml | BAT-001's and PWR-001's notes; BAT-001's remediation | commit before rules_status |
| `patch_vendor_index.py` | sources.txt, vendor-status.txt | the new sheet's provenance and status lines | any time |

Not drafted, for their owners: the battery packet cites `pcb_pack_protection.yaml` by line (S-y has the map) and its
`candidate/pcb-p-pack-intent.json` is main's (the netlist's content is unchanged, the intent gains declarations only);
`ENGINEERING-QUESTIONS.md` EQ-19's attempts row (D and P PASS in scratch; E's FAN1_SW and FAN2_SW left) and EQ-10 (W4DP-F1,
W4DP-F2 beside BAT-F16, S-x); `pcb_energy_chain.yaml`'s F1 figures (BAT-F04's other half).

## 8. Open, not in this stream's scope

SI-001 stays INCONCLUSIVE on D and P (P: 20 undecided signal nets of 40, 15 with no signal-class declaration in `boards/p.json`); RF-002 on D (EQ-25);
S-76's board E half; the qualified battery review (D-09, L-03) that S-x's options go to first.

Integration against a moved main (seen at pass 2): main is at 62f26a44, where fnd/rel2 changed TEST-PLAN.md (9 lines,
sha256/16 `4f15bd02a6a8be46`) and pcb_rules_coverage.yaml (1 line) and took SC-58 to SC-63, S-77 to S-79 and M-02.
`patch_test_plan.py` and `patch_coverage.py` still apply there (checked on main's files in scratch; TEST-PLAN.md patched is
`14670f6fe9e3ef2b`). `apply_registry.py` takes the next free ids by itself (SC-64 onward, S-80 onward on that main) but
REFUSES there by design: its TEST-PLAN.md pair (`TP_OLD`, `TP_NEW`) and `DIFF_TP`'s line arithmetic are main 91894cd7's, and
records rel2 rebound may no longer carry the bindings REBIND expects. The integrator re-reads TEST-PLAN.md, sets the pair
to `4f15bd02a6a8be46` / `14670f6fe9e3ef2b` if the rebase is otherwise clean, and restates DIFF_TP from the patched diff.

## Corrected at integration (r8int6): derate's unrated list

The independent check (w4dp check 2, an AI check) read derate's unrated list on board P as C1 to C9, C13 to C19, D2, D3, F1 and F2: of the fuse-gate parts only C19 is on it, and R29 to R32, JP1 and Q3 are not rated kinds, so derate never looks at them. Where this record says they are among derate's unrated parts, that is the correction; its conclusion, that the lower fuse-gate bound moves no derate count, stands.

## Ids taken at the r8int6 integration (corrected at integration)

The registry script ran at the r8int6 integration of 27 September 2026 (set 6 of the handover), where other branches had taken the numbers this record names as drafted; the ids it took there, read back from the registry by each record's own text: SC_D2 is SC-72; SC_PWR_DP is SC-73; SC_BAT001 is SC-74; S_BAT001_HW is S-85; S_BAT001_DOCS is S-86. Where this record names another number for one of them, the id here is the one the registry holds.
