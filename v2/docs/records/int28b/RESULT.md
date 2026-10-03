# RESULT: integration set 28 (MESHSAT-1357, 3 October 2026, branch `fnd/int28b` from set 27's frozen candidate `94971c8c`)

Prototype design: nothing here has been built, powered or measured. This page records what integration set 28 merged and changed, the
checks and tests it ran, and what it leaves owed, for the coordinator who promotes it. Times are CEST. Every sha is read from the tree
at the time named. Nothing of any Layer 4 record's prose or figures was changed here: pins, and L4-E11's need() texts in Layer 5's
wording, only.

## 0. In short

- Eleven merges in the coordinator's order, the first with four pin conflicts (L4-E9's and L4-E11's scripts and outputs, resolved to
  set 27's frozen chain and then re-pinned from the tree), the other ten clean (section 1).
- Layer 5's debts (L5-F01, L5-F02, L5R3-F01): the five CFL readings rebound twice (at l5pwr's PANEL.md, carried by the merge, and at
  round 3's PANEL.md and ASSEMBLY.md, by `apply_set28b_rebind.py`); `rules_lib.py requirements` reads 0 errors. L4-E11 re-pinned to
  the contract, PANEL.md and ASSEMBLY.md with its need() texts in Layer 5's wording; L4-E9 to the contract and the interfaces.
- lcsc_fill.py's correction (Layer 6 round 2) re-pinned in L4-E8, L4-E9 and L4-E12. L4-E9 then refused on board E C5 (the table fills
  C113803 where `gen_sch_e.py:713` names C14663); L4-E9's round 6 (`fnd/l4e9r6`) reads C5 through the table's own rule: it regenerates on the merged tree and reads "already identical" in the freeze's stability pass.
- The chain frozen with `_bin/freeze_l4_chain.sh` three times (after the first re-pins, after round 3, after L4-E9's round 6).
- L4-E7's reader refused on its lead guard, fired by my superseded `records/int28/RESULT.md` row F-7 (F-11); its author's
  `fnd/l4e7g` compares each stated length with a1solar's as a number, and L4-E7 regenerates (merged `835d031b`, freeze `dd70029a`).
- l5pwr, l6pwr and l7pwr refused on content of set 27's Layer 4 records they were not written against (F-12 to F-14); their authors'
  rounds `fnd/l5pwr2` (merged `92a5c7d8`), `fnd/l6pwr2` and `fnd/l7pwr2` (NAMED_OWED).
- PCB-BRING-UP.md reads current under the merged renderer (no render needed); PCB-ETA.md stale is the worker-tree condition.

## 1. The merges and their resolutions

| Order | Branch, tip | Commit on fnd/int28b | Conflicts and resolution |
|---|---|---|---|
| 1 | `fnd/l5r2` 6902db8f (carries l5pwr, l6pwr, l7pwr and the superseded int28 preparation `a1f696de`) | `90e3a82d` | four: `l4e9_power_path.py` and `l4e11_power.py` (one block of PINS lines each: set 27's frozen chain against int28's re-pins), resolved to ours with `resolve_both_sides.py --ours` (refuses a block holding anything but PINS lines); `l4e9_power_path.out` and `l4e11_power.out` taken whole from ours (a generated file is never hand-mixed); every pin then re-read from the tree by `apply_set28b_repins.py` |
| 2 | `fnd/l6r2` 7633ae0a | `f23ce2e6` | none |
| 3 | `fnd/l7r2` 149de0ef | `518eb284` | none |
| 4 | `fnd/l8gnd` 226e9143 | `76766fd6` | none |
| 5 | `fnd/l8r2` 2ef3b943 | `d020eead` | none |
| 6 | `fnd/l9tp` ce69920c | `86f90ca8` | none |
| 7 | `fnd/l4e7` d562e75a | `20533dfa` | none |
| 8 | `fnd/fw-panel` 42c27369 | `a0042f6b` | none |
| 9 | `fnd/l8r2` 29ffb518 (its item 4, board C's PI button) | `1fea761a` | none |
| 10 | `fnd/l5r2` d077fb91 (Layer 5 round 3) | `de45a5b4` | none |
| 11 | `fnd/l4e9r6` 08658fcb (L4-E9 round 6) | `a234b33a` | none |
| 12 | `fnd/l4e7g` e6961b05 (L4-E7's lead guard) | `835d031b` | none |
| 13 | `fnd/l5pwr2` d33ea1c4 (Layer 5's F-12 round, L5-F09 to F11) | `92a5c7d8` | none |

Every merge: `git merge --no-ff --no-commit`, the staged diff through `pre-commit-check.sh --msg` (PASSED each time), then the commit as
the owner. The shared append-only files (SOURCES.yaml, sources.txt, vendor-status.txt, PROCUREMENT.md) merged without conflict (the
r2 branches carry the int28 resolution); every YAML re-parses.

## 2. The re-pins (file, key, old sha256/16, new sha256/16)

Rounds: A = after the merges, before Layer 5 round 3 (commits `5a6ad183` and the freeze `fa729b46`); B = after round 3 (`2d19e486`);
C = after L4-E9 round 6 (`56d6b457`). The freeze helper's own re-pins (the registry in L4-E10, E12, E13; L4-E9's page in L4-E10 and
L4-E11; the chain's outputs in L4-E12 and L4-E9) are listed with it. Every output regenerated through `_bin/regen_out.py`; every
regenerated Layer 4 output moved in its printed pin lines only, except L4-E11's two "as written" quotations (FW-C08, FW-A14, now
Layer 5's cells) and L4-E9's round 6 content, which its author regenerated.

| Round | File | Key | Before | After |
|---|---|---|---|---|
| A | `l4e8/ripple_dense.py` | LCSC_FILL | `6888362e4a3295d0` | `eb1f5e9f5e1ca9ae` (its output `3b751989` to `c6181037`, the pin line only; the Cc2 pick unchanged) |
| A | `l4e11/l4e11_power.py` | hwfw | `7b8cb44aeb554791` (int28's, carried by the merge) | `e5b4d65046f4ace5` |
| A | `l4e12/l4e12_thermal.py` | LCSC_FILL, L4E8_OUT | `6888362e`, `3b751989` | `eb1f5e9f`, `c6181037` |
| A | `l4e9/l4e9_power_path.py` | hwfw, ifaces, lcsc, l4e7md, l4e8, l4e11 | `7b8cb44a`, `22aeae75`, `6888362e`, `50f48017`, `3b751989`, `486e27ee` | `e5b4d650`, `4784a61a`, `eb1f5e9f`, `241d0cc5` (L4-E7's page at `d562e75a`, debt e), `c6181037`, `5effffae` |
| A (freeze) | `l4e10`, `l4e12`, `l4e13` | REG / reqs | `b624ac495650a359` | `435d515f6184f7bd` (the registry as int28's rebind left it) |
| B | `l4e11/l4e11_power.py` | hwfw, panel, assembly, reqs | `e5b4d650`, `3f380ef7`, `942d562e`, `435d515f` | `d683b31a`, `9fd2b4e3`, `29dbe3a0`, `07fec30d` |
| B | `l4e9/l4e9_power_path.py` | hwfw, reqs, l4e11 | `e5b4d650`, `435d515f`, `5effffae` | `d683b31a`, `07fec30d`, `269a9e36` |
| B (freeze) | `l4e10`, `l4e12`, `l4e13` | REG / reqs | `435d515f` | `07fec30d43271245` (after the round 3 rebind) |
| C | `l4e11/l4e11_power.py` | arch (L4-E9's page, round 6) | `677e7833de68f90f` | `a760101cde41633a` |
| C | `l4e9/l4e9_power_path.py` | l4e11 | `269a9e36` | `9a057f92` |
| C (freeze) | `l4e10/l4e10_cell_thermal.py` | the page | `677e7833` | `a760101c` |
| C (freeze) | `l4e12`, `l4e9` | the chain's outputs | | `l4e10` `cf38401a`, `l4e12` `d88aabc2` |

Final Layer 4 outputs against set 27's: `l4e8` `c6181037` (was `3b751989`), `l4e9` `e8ff8187` (`1d70beca`), `l4e10` `cf38401a`
(`62c3f34c`), `l4e11` `9a057f92` (`486e27ee`), `l4e12` `d88aabc2` (`aaf63b8d`), `l4e13` `ed8c9ae7` (`268667c3`); unchanged: `l4e5`
`f9c98ec5`, `l4e7` `058b8e76` (its reader refuses, owed). The inputs that moved: HW-FW-CONTRACT.md `1c211e46` to `d683b31a`, PANEL.md
`b396d028` to `9fd2b4e3`, ASSEMBLY.md `942d562e` to `29dbe3a0`, pcb_interfaces.yaml `9ec50ccf` to `4784a61a`, pcb_requirements.yaml
`b624ac49` to `07fec30d`, lcsc_fill.py `6888362e` to `eb1f5e9f`, L4-E9's page `677e7833` to `a760101c`, L4-E7's page `50f48017` to
`241d0cc5`.

Later outputs regenerated (their readers print these shas): `l5r2_interfaces.out` `fcc69658`, `l6r2_passives.out` `dfba6b7e` (its two
non-pin lines in round A are the draft-chain order it reads from L4-E9's register, which set 27 changed), `l7r2_items.out` `98d98306`,
`l8gnd_drafts.out` `1dcab639` (debt d), `l8r2_drafts.out` `a1b421fe`. Refused, committed outputs unchanged (F-12 to F-14):
`l5pwr_contracts.out`, `l6pwr_parts.out`, `l7pwr_fans_th1.out`.

The registry: CFL-001, 005, 014, 015 and 016 first bound to PANEL.md `3f380ef7` by int28's rebind (carried by the l5r2 merge), then
rebound by `apply_set28b_rebind.py` to PANEL.md `9fd2b4e3` and (CFL-015, CFL-016) ASSEMBLY.md `29dbe3a0`, seven bindings, one evidence
entry each, `evidence_result` PASS unchanged on all five; the trace and the Layer 3 R2 pages re-rendered (they print the entries, the
registry's sha and the evidence counts).

## 3. The check lines

On the committed tree at `56d6b457` (3 October 2026, 19:30):

| Check | Line |
|---|---|
| `rules_lib.py requirements` | `145 requirement record(s), 0 error(s), 0 warning(s)` (7 errors after the round 3 merge, 0 after the rebind) |
| `rules_lib.py` | `59 rule(s), 0 error(s), 0 warning(s), fingerprint a9b1e7f7412f9c0c` |
| `render_l3r2.py --check` | `3 page(s), 0 out of date` |
| `rules_render.py --requirements --check` | `REQUIREMENTS-TRACE.md is current` |
| `rules_render.py --check` | `7 document(s), 1 out of date`: PCB-ETA.md (rendered from gitignored journals a worker tree does not hold; the box's); CURRENT-EVIDENCE.md not rendered here (no audit); PCB-BRING-UP.md CURRENT under the merged renderer (`fnd/l9tp`'s `_with_bringup_preface`), so debt g needed no render |
| `decisions_render.py --check` | current (exit 0) |
| `part_identities.py check` | `boards c, 175 rows, 87 selections, 0 rows uncovered, RESOLVED bindings {'READ': 21, 'DECODED': 23}, 0 problems` |
| the two identity blocks (debt h) | `drafted_identities_l4_power` and `drafted_identities_l6r2_passives` present; no table regeneration happened, so nothing to re-apply |
| `scan_printed_pins.py` | 7 outputs do not bind: l5pwr, l6pwr, l7pwr (F-12 to F-14) and four historical snapshots unbound before set 28 (cx1's check, h2's and h3's counts, s99's stage) |
| `verify_l3am.py`, `verify_acceptance.py` | RUN with the module run on the final tip (section 4) |

## 4. The module tests

TESTS

## 5. The box re-takes owed (the coordinator's)

| Reading | Why |
|---|---|
| `interfaces.py` on every board (A, B, C, D, E, P, E5) | `pcb_interfaces.yaml` is a CONFIG_INPUT and moved from set 27's `9ec50ccfae3b70a0` to `4784a61af0840534` (Layer 5's power pass and round 2); the seven tracked readings pin the old sha |
| the identity readings (stream w5identc's `check-board-c-*.json`) | `pcb_part_identities.yaml` carries Layer 6's two drafted blocks (`drafted_identities_l4_power`, `drafted_identities_l6r2_passives`) outside `selections:`; `part_identities.py check` reads 0 problems here with the held sheets staged |
| `rules_status.py` (the audit, CURRENT-EVIDENCE.md, the per-board status pages, PCB-ETA.md) | the registry (`07fec30d43271245` after the second rebind), `pcb_interfaces.yaml` and `lcsc_fill.py` changed; PCB-ETA.md renders from gitignored journals a worker tree does not hold |
| TST-001 on PCB-BRING-UP.md | the page carries the hand-written procedure above the renderer's marker (`fnd/l9tp`); `rules_render.py --check` reads it current, TST-001's reading is owed on the box |
| the lcsc_fill.py table's effects | the next regeneration of each board fills the corrected codes (`records/l6r2`); the BOMs and the certification readings follow the regeneration, which waits on the drafts' releases |

## 6. Findings of this integration

| ID | Finding | Owner, next action |
|---|---|---|
| F-10 | Board E C5: `lcsc_fill.py`'s corrected table fills 100 nF 0603 with C113803 (YAGEO CC0603KRX7R0BB104, 100 V). L4-E9's reader need()ed `gen_sch_e.py` to name that code beside the 50 V MPN and refused; round 6 (`fnd/l4e9r6`) reads C5 through the table's own matching rule. **Corrected routing (the coordinator, 3 October 2026):** `gen_sch_e.py:713`'s comment is about C46 and C59, which carry C14663 explicitly in their own calls; C5's call carries no code and takes the table's fill, so the generator is consistent and no generator change is owed | closed by L4-E9 round 6; no Layer 8 action |
| F-11 | L4-E7's reader refuses (exit 3) on its prose guard ("a document now states the panel's lead length"), fired by my superseded `records/int28/RESULT.md` row F-7, which quoted R-180's figures; the r2 branches brought that file in. Not edited here, by the coordinator's instruction | L4-E7's author on `fnd/l4e7g`; then the final freeze and the module run |
| F-12 | `l5pwr_contracts.py` refused: "S27-02b: figures not printed by l4e11out, reg: ['PWM ramp']" (its table cited a figure set 27's L4-E11 output and register no longer print). **Corrected by its author:** the reader also refused S27-B6, which the first refusal hid (a reader stops at its first failing row); `fnd/l5pwr2` (d33ea1c4) restates six rows (S27-B6, S27-01, S27-02a, S27-02b, S27-03, SEQ-08) and closes L5-F09, L5-F10 and L5-F11 in the contract and the interfaces | merged (`92a5c7d8`), regenerated in section 2's round E |
| F-13 | `l6pwr_parts.py` refuses: "the INP line is not in l4e7_stage_settings.out" (set 27's L4-E7 rounds 3 to 5 restated the line) | Layer 6's author (record l6pwr) |
| F-14 | `l7pwr_fans_th1.py` refuses: "VSYS_E's drafted loads not parsed" (set 27's L4-E11 section 18 rewrote `apply_gen_sch_e_aux.py`'s fan rail) | Layer 7's author (record l7pwr) |
| F-15 | The three r2 branches were cut from the superseded `fnd/int28` (`a1f696de`), so set 28 carries `records/int28/` and int28's re-pins in its history; this record supersedes it | none: noted |

## 7. Proposed LAYER-STATUS rows


Each row is `| Item | Acceptance item (short) | After set 28 | Evidence, or what remains |`, composed from the merged records' own
"criteria moved" sections: Layer 5 from `records/l5pwr` section 6 and `records/l5r2` section 6, Layer 6 from `records/l6pwr` section 4
and `records/l6r2` section 6, Layer 7 from `records/l7pwr` section 6 and `records/l7r2` section 6, Layer 8 from `records/l8gnd` section
5 and `records/l8r2`, Layer 12 from `v2/firmware/panel/README.md`, `v2/docs/test-procedures/README.md` and `v2/docs/PCB-BRING-UP.md`.
Where two rounds moved one item, the later round's reading is the row and the earlier's evidence is kept in it. A row not listed keeps
its H2 text. No item is raised to MET by set 28; every circuit change named is a release-guarded DRAFT, not applied, and the box
re-takes of section 5 are owed before any reading counts as current.

### Layer 5. Partitioning and interfaces (header: "At set 28: IN_PROGRESS; Layer 5's power pass (records/l5pwr) and its round 2 (records/l5r2) wrote Layer 4's power results and the pass-2 fields of every contract; no release check has judged this layer")

| 5.2 | every interface owned at both ends with its connector | PARTLY | all 31 contracts carry both ends with a part on every board end and every pass-2 field (`records/l5r2`; hc5's `check_contract_fields.py --all`); not MET: no census shows every interface of the netlists has a contract, and the generators write no MPN (EQ-21) |
| 5.4 | electrical levels stated per interface | PARTLY | the power interfaces' levels with their Layer 4 basis and marks (`records/l5pwr`), the eight first-twelve contracts, the fans and the chassis bond (`records/l5r2`); the kit I2C bus's three segments owed (SC-59) |
| 5.5 | power capacity of each power interface with margin | PARTLY | IF-EXT-DC, IF-AE-DOCK, the outlet and the PoE monitor (`records/l5pwr`); PANEL_5V per conductor (F1's trip band TBD), the mezzanine's +3V3, the PA lead at 60 percent, the MAIN lead's microamps, the fans' branch 1.3208 A at 89.8 percent, DRAFTED (`records/l5r2`); open: I-03's PS-ALLTX, E5's targets and the ground share (S-74, S-75), the ribbon and SMP-MAX ratings, the 813's pulse capability (E11-38; Layer 7's bound and drafted maker question) |
| 5.6 | sequencing across interfaces | PARTLY (from OPEN) | L4-E9 section 4's sequencing fields, FW-E11, FW-A21, FW-A23, `power_line_states` (`records/l5pwr`); HOT-R1's line DRAWN on A and E since SC-70 (S-57 closed); the SLOT_EN hold DRAFTED on board A (`records/l8gnd`: U43, R230 to R232, C240, `apply_gen_sch_a_hotr1.py`, release-guarded) and written PROVISIONAL into the contracts and FW-C02 (`records/l5r2`); H2's item stays open until the keeper is in a generator, regenerated and at parity on the box; the panel firmware's F-03 (pico-sdk resets IO_BANK0 at boot, so FW-C02 cannot keep SLOT_EN alone) for the hold's owner |
| 5.7 | reset, default and cable-out states for every control line | PARTLY | every power line of L4-E9 section 4 with its states and firmware row (`records/l5pwr`); default_state for the eight, SLOT_EN's cable-out with the keeper, U22's RUN line (`records/l5r2`); TX_INHIBIT_n's fail-safe level (EQ-25) |
| 5.9 | harnesses defined and consistent | PARTLY | harness fields from ASSEMBLY.md and HC6-SC-7 (`records/l5r2`, its L5R2-F04); J_AB2 and MAIN at 128 and 480 mm, the fans on JST PH (`records/l7r2`); the jumper plug picked (Radiall R125.172.001, `records/l7r2`) |
| 5.10 | mechanical mating of every interface | **OPEN** | mating fields on every contract (`records/l5r2`); W4-F17 (re-measured at 3.10 into D, `records/l7r2`), J_QMX's land (L5R2-F04, drafted on PH by `records/l8r2`) and the fans' lead terminations keep it open |
| 5.11 | firmware obligations affecting hardware explicit | PARTLY | FW-A19 to FW-A23, FW-C15, FW-E11 to FW-E13 added, FW-A09, FW-A14, FW-A16, FW-C08 and PANEL.md section 10 restated (`records/l5pwr`); FW-C02, FW-C01, FW-C14, V-C02, FW-E07, FW-E11 (DRAFTED, PROVISIONAL, `records/l5r2`); the panel controller's firmware implements FW-C01 to FW-C15 on host tests (`v2/firmware/panel`) and its findings F-01 to F-13 go to their owners; the bridge wire format (F-02, MESHSAT-837) is defined nowhere |
| 5.12 | GND-002 implemented everywhere | PARTLY (from OPEN) | all four board changes DRAFTED (`records/l8gnd`: board A's CHASSIS net with R229 and the strap pad H1; board B's C33 and J_ETH shield on CHASSIS; release-guarded) and carried PROVISIONAL in IF-A-CHASSIS, IF-EXT-ETH, IF-EXT-DC, IF-AE-DOCK (`records/l5r2`); the bond's lugs and stud picked (JST R5.5-4, R5.5-6, M6 x 45, `records/l7r2`); open: the release and regeneration, the land in `meshsat.pretty`, the wall RJ45's shield path (no candidate read carries shield, PoE voltage and the envelope together, `records/l7r2` section 1), S-50's registry entry |
| 5.13 | interface contracts consistent with the tree | PARTLY | the drawn board first, every draft DRAFTED with its row; stale texts corrected with their history kept (`records/l5r2`); `check_contracts.py` PASS 99 of 99 unchanged; `pcb_interfaces.yaml` (now `4784a61af0840534`) is a CONFIG_INPUT of `interfaces.py`: its readings on every board are owed a re-take |

Not moved by set 28: 5.1, 5.3 (MET, the same reading), 5.8, 5.14, 5.15.

### Layer 6. Components (header: "At set 28: IN_PROGRESS; the power parts Layer 4 selected (records/l6pwr) and the generic parts of the six boards (records/l6r2) identified and sourced; lcsc_fill.py's table corrected to codes that meet the identity tool's requirements; nothing on a regenerated netlist yet")

| 6.1 | exact manufacturer, MPN, package and grade per fitted part | **OPEN**, toward PARTLY | the 28 power parts of L4-E5 to L4-E11 (14 RESOLVED on a page that prints the part number, 14 UNRESOLVED with their reason, `drafted_identities_l4_power`, `records/l6pwr`); 1440 of the 1657 uncoded fitted rows of the six boards given maker, MPN, package, code and grade (131 selections DECODED on the maker's table, 91 DOCUMENT_OWED, `drafted_identities_l6r2_passives`, `records/l6r2`); the five fans (`records/l7pwr`); both blocks sit outside `selections:` and are staged for the Layer 8 regeneration; no MPN field in the generators (EQ-21) |
| 6.2 | supporting documents with revision, source and currency | PARTLY | 17 makers' documents of the power parts (10 held back under their terms, fetched and matching) and Samsung's pages excerpted (`records/l6pwr`); the fans', cooler's and Preci-Dip's documents filed (`records/l7pwr`); JLCPCB's catalogue reading and KiCad's XAL footprints (`records/l6r2/inputs`); owed: the ZK sheet's URL, Samsung's MLCC catalogue, Milliohm's HoLLR sheet, Nexperia's packing legend, the 35E maker copy |
| 6.3 | selection rationale recorded | PARTLY | one sentence per power part (`records/l6pwr`); rule I-1's order for every generic selection (`records/l6r2`); the fans row by row (`records/l7pwr`) |
| 6.4 | compatibility findings; mismatches stay mismatches | PARTLY | the three Coilcraft rows of F4 proven on the maker's land, their footprint keys drafted, release-guarded (`records/l6r2` round 3); the standing wrong models as at H2 |
| 6.6 | procurement constraints and alternatives | PARTLY | dated stock and price per selection, the five-kit need, an alternative per selection (`PROCUREMENT.md` section 8 Layer 6's and Layer 7's sections, `records/l6pwr`, `records/l6r2`); two stock pools read |
| 6.7 | regenerated outputs preserve part decisions | PARTLY | `lcsc_fill.py`'s table corrected (eleven lines to the l6r2 selections, two X5R lines kept under rule C-D3b, held by `test_lcsc_fill_requirements.py`), so the next regeneration fills those codes; the generators' typed codes the certification refuses corrected through LCSC drafts (24 rows, `records/l6r2` round 4, release-guarded) (board E C5 now fills C113803; the generator's C14663 at line 713 belongs to C46 and C59, which carry it explicitly) |
| 6.8 | a current, versioned BOM with identity per board | PARTLY | NOT MOVED: the parts are on no committed BOM until a board is regenerated with its drafts |

Not moved by set 28: 6.5, 6.9, 6.10, 6.11.

### Layer 7. Mechanical and enclosure (header: "At set 28: IN_PROGRESS; records/l7pwr settled the fans (D-18) and specified the T-H1 mock-up; records/l7r2 decided the bond's lugs and stud, the jumper plug, the fans' terminations and the cooler fans' brackets; nothing built")

| 7.4 | mounting and retention | **OPEN**, toward PARTLY | the face's mounting drawn (C1); the cooler fans' cap bracket specified and their envelope drafted (`records/l7r2`, `apply_panel1450_coolers_r2.py`); the pack hold-down (S-27), the stack's retention and the mixers' sites undesigned |
| 7.5 | connector, cable and service access | PARTLY | the connector plate (C3) drawn; the right-angle jumper plug picked (Radiall R125.172.001: M17x met, M17g met with 5G MAIN at 26.5 degrees and IRIDIUM in the back bundle, M18 at 5G MAIN -0.04 at the worst, F-R2-03); the bond's lugs and stud picked (JST R5.5-4, R5.5-6, M6 x 45); the fans' terminations on JST PH; J_AB2 and MAIN 128 and 480 mm (`records/l7r2`); the dock lead's pulse capability bounded on published relations, the 813 contact's a drafted maker question (`records/l7pwr`); the sealed RJ45 open (no candidate read carries shield, PoE voltage and the plate's envelope together) |
| 7.8 | thermal interfaces specified | PARTLY | the PA flange sensor drawn on D (`76235aad`); the five IP68 fans picked (Sanyo Denki 9WL0612P4H001 mixers, 9WPA0412P6G001 cooler fans, `records/l7pwr`), the cooler fans placed on their brackets over the coolers with 3.46 to the PA and 13.36 to the plate (`records/l7r2`), their 12 V feeds drafted (board E's mixers L4-E11 section 18, board B's coolers `records/l8r2` item 1), the mixers' sites owed; the conductance (EQ-05) waits on T-H1 |
| 7.9 | critical fit uncertainties resolved by suitable evidence | **OPEN** | FEA-007: the mock-up (L-07, EQ-08) and the desk items; T-H1's empty-case mock-up specified with its bill (`records/l7pwr/T-H1-MOCKUP-SPEC.md`: EUR 639.76, GBP 887.00, USD 147.38 read), not evidence; new nominal fits awaiting the box: the cooler fans' plan margins 1.0 and 1.255 (F-R2-04), M18 at 5G MAIN (F-R2-03), the cooler fan's 2.76 mm to the backer; W4-F17 re-measured at 3.10 into D |
| 7.10 | later physical checks allocated, deferral justified | PARTLY | FEA-007's staging as before; T-H1 allocated to the prototype bench with its specimen, bill, pass lines and the owner's authorisation named (`records/l7pwr`, `records/l4e12/T-H1-PROCEDURE-DRAFT.md`); the qualification procedures of `v2/docs/test-procedures/` (PROPOSED) |

Not moved by set 28: 7.1 to 7.3, 7.6, 7.7, 7.11 to 7.17.

### Layer 8. Schematics (header: "At set 28: IN_PROGRESS on every board; records l8gnd and l8r2 drafted the known corrections as release-guarded apply scripts; no generator changed, no board regenerated")

| 8.5 | BOMs | PARTLY | two NOT_FOR_FAB BOMs per board as at H2; `lcsc_fill.py`'s table corrected (`records/l6r2`), so the next regeneration's BOMs fill those codes; the identity gap is Layer 6's (EQ-21) |
| 8.7 | exact part and land mapping | PARTLY | SCH-005 as at H2; the three Coilcraft XAL rows on another series' footprint, the maker's land proven and the keys drafted (`records/l6r2` round 3, release-guarded) |
| 8.10 | known schematic-affecting defects closed per board | **OPEN** | drafted, not applied (each release-guarded, refusing the generator until a RELEASE.md names an accepted check): GND-002's four changes and the SLOT_EN hold (`records/l8gnd`); board B's coolers on a per-slot 12 V step-up with an eFuse (E11-40, R-190, P1-2), VBUS20's over-voltage cut-off in VIN_RAW (S-111, R-48, P1-3), PANEL_5V behind an eFuse (L5R2-F03), board D's 3.3 V behind an eFuse as +3V3_A2D (L5R2-F05), J_QMX and J_CAM on the JST PH land (L5R2-F04), board C's PI button on U1 P1.3 (the panel firmware's F-01) (`records/l8r2`); P1-1 (the solar guard and sense) left to the supplier; still open as at H2: EQ-25 on C, PWR-001 on C, D, E, P, BAT-001 on P; `check_gnd002_netlist.py` and `check_l8r2_netlist.py` read NOT DRAWN on the committed netlists |
| 8.17 | condition 1: substitutions stay mismatches until proven | PARTLY | as at H2; the corrected table's substitutions each carry their rule (C-D2, C-D3, C-D3b, R-S1, R-P) in `lcsc_fill.py` and `records/l6r2` |

Not moved by set 28: 8.1 to 8.4, 8.6, 8.8, 8.9, 8.11 to 8.16, 8.18. (8.1 and 8.9 stay MET for the committed generators; a regeneration with the drafts applied re-opens their parity on the box.)

### Layer 12. Firmware, bring-up, test plans and build documentation (PROPOSED new section: LAYER-STATUS.md has none; its scope is the owner's instruction of 2 October 2026, "L12: firmware, bring-up procedures, test plans and build documentation in parallel wherever dependencies allow; physical results remain open until performed"; the item numbers are proposals)

| 12.1 | firmware for each controller, with tests of its stated behaviour | PARTLY | the panel controller (board C, U3 RP2040): a portable core with its hardware layer and pico-sdk port, 55 host unit tests under `-Werror` and `test_fw_panel.py` binding the code to the netlists and FW-C01 to FW-C15 (`v2/firmware/panel`); the target build NOT compiled (no arm toolchain here), nothing run on hardware; findings F-01 to F-13 to their owners (F-01 drafted by `records/l8r2` item 4); the sensor controller (board E), the bridge's side and the wire format (F-02, MESHSAT-837) not started |
| 12.2 | bring-up procedure per board | PARTLY | `v2/docs/PCB-BRING-UP.md`: the first-prototype bring-up of A, B, C, D, E, E5 and P written above the renderer's generated rail inventory (PROPOSED, for the design with its drafts applied, checked by `tp_check.py`); `rules_render.py --check` reads the page current; TST-001's reading on it owed a re-take |
| 12.3 | test procedures for the qualification route | PARTLY | ten procedures (TP-CELL, TP-E11-29, -30, -31, -35, -36, -37, -38, TP-EPAPER, TP-SOLAR), each quoting its register row and 5d route row, every quote held to its source by `tp_check.py`, PROPOSED for the supplier to review; none run |
| 12.4 | build documentation | NOT MOVED | BUILD.md and ASSEMBLY.md as at H2 |
| 12.5 | physical results recorded | **OPEN** | nothing built or run; every procedure's result is owed |

## 8. Decisions taken (authority: SESSION, under the owner's standing rule of 26 September 2026; none asks the owner)

| ID | Decision | Why | Reversed by |
|---|---|---|---|
| D-1 | The first merge's pin conflicts resolved to set 27's frozen chain, the two generated outputs taken whole from it, and every pin re-read from the tree afterwards | the frozen chain is the candidate being promoted; int28's pins were written against a tree that no longer exists; a generated output is regenerated, never mixed | re-running `apply_set28b_repins.py` after any other resolution |
| D-2 | L4-E5 keeps the int28 mechanism (the contract read at `2c240414`, its pin unchanged) carried by the merge | Layer 5 applied L4-E5's own draft; its "as written" texts exist only at that commit; its output is byte-identical | a round of L4-E5 restating its reading on the restated rows |
| D-3 | The CFL readings rebound by a script that asserts each record's ground (byte-identical sections, or sections changed only in PI-button lines) rather than by judgement in prose | the change of round 3 is wide (seven sections of PANEL.md); a mechanical assertion per record shows which ground moved and refuses otherwise | a reading re-decided by the registry's writer |
| D-4 | `stage_held_sheets.py` copies held sheets from sibling checkouts by their pinned sha (its sha pass corrected) | the readers refuse without them; nothing fetched | removing the ignored `held/` folders |
| D-5 | L4-E9's lcsc_fill pin re-pinned as the coordinator asked even though it then refused; the refusal reported, not forced, and a one-off diagnostic copy (deleted, nothing committed) showed C5 was its only refusal | the coordinator's instruction; the diagnostic told the author exactly what remained | L4-E9 round 6 |
