# Stream s98: the interim I-03 alignment applied in boards A and B (open item S-98)

MESHSAT-1357, 28 September 2026, branch `fnd/s98` from the integration set's tip `dcf04c90`. Prototype design: no V2 board
has been built, ordered or measured. This is AI engineering work by the generator owner of boards A and B for the circuit
round; every check named here is an AI check, not a professional engineering review. Plain English, no dashes.

The subject is `S-98` in `tools/pcb_requirements.yaml` (finding I-03 on the contract `IF-AB-POWER`): the two ends of the
board A to board B power leads declared different currents on `+5V_S2` and `+5V_DEV`. The pilot's record
(`v2/docs/records/cx1/ANALYSIS.md`, `CORRECTION.md`) and its two independent checks (`cx1/checks/check-1-RESULT.md`,
`check-2-RESULT.md`) found no held document that decides the PS-ALLTX mode current of any of the five leads, so the
alignment is INTERIM: the end that derives its figure from held maker pages (board B) is the one aligned to, and the
mode figures stay INCONCLUSIVE until the bench (TEST-PLAN power tests at J_5V_S2 and J_5V_DEV).

## 1. What was changed, and why each figure

### 1.1 The four entries of the draft, applied as delivered (commit `c098b8f3`)

`records/cx1/apply_declarations_draft.py --check` passed (six PASS lines, `readings/draft-check.out`), then the draft was
applied (`readings/draft-apply.out`; a second run is refused: `Refused: this draft has already been applied or
attempted.`). Its marker `records/cx1/apply_declarations_draft.applied` is left UNTRACKED and uncommitted, as instructed.
The diff (`readings/draft-applied.diff`) is exactly the four call lines plus the draft's own seven comment lines:

| generator, line at `c098b8f3` | was | is | basis (CORRECTION.md B1 and B2, both checks reproduce the sums) |
|---|---|---|---|
| `gen_sch_a.py:113` (`+5V_S%s`, slot 2 only) | 2.5 A typical, 5.0 A peak, load J_5V_S2 5.0 A | 4.2 / 5.63 A, J_5V_S2 5.63 A | board B's derivation: CM5 0.9 A typical (release 3, Table 9, no maximum published) with the card buck's 3.0 A at 3.456 V over 0.88, the other children and the fan = 4.157 A; the coincidence with the CM5 at its 1.6 A allowance and the RM520N-GL at 4 A (Hardware Design v1.1, PDF p.30) = 5.628 A |
| `gen_sch_a.py:48` (VBAT load Q28) | 2.0 A | 2.22 A | 5.63 x 5.1 / (0.90 x 14.4) = 2.2155 A, the stage's input at A's nominal node voltage and assumed efficiency (not a low-battery bound) |
| `gen_sch_b.py:85` (`+5V_S%d`, slot 2 only) | peak 5.0 A | peak 5.63 A | B's own comment derived 5.63 A and its call declared 5.0 A |
| `gen_sch_a.py:135` (`+5V_DEV`) | typical 4.0 A, loads J_5V_DEV 3.2, U23 0.5, U32 0.3 | typical 5.1 A, loads J_5V_DEV 3.8, U23 1.0, U32 0.3 | B declares 3.8 A typical arriving; the D8 mezzanine declares 1.0 A typical at both ends (`gen_sch_a.py` +5V_D8, `gen_sch_d.py:56`); the parent's wall allocation 0.3 A; 3.8 + 1.0 + 0.3 = 5.1. **The 6.9 A peak is unchanged**: S-99 (stream s99) decides it |

Slots 1 and 3 keep 2.5 / 5.0 A at both ends (their converters are AP64500 5 A parts, DS41979 p.1).

### 1.2 The notes and comments the second check flagged as stale (`edit_generators_s98.py`, same commit)

Run once, refuses a second run (`readings/edit-generators.out`). Byte-exact old and new text is in the script.

- **A1** the slot rails' intent note said "5 A peak at the module" for every slot. It is per slot now: slot 2 carries the
  INTERIM statement (the maker pages, the INCONCLUSIVE mode current, the 7.28 A all-peak conditional bound above the
  LM5176 stage's 7.10 to 7.17 A loop minimum); slots 1 and 3 keep 5 A and name it as the AP64500's rating.
- **A2** the draft's comment above the `+5V_DEV` call said the peak is stale and "a SESSION decision is owed"; it now says
  the 6.9 A peak is held as is and that S-99 decides it, with the coincident figures (7.9 A with D8 at its typical, 8.9 A
  at every declared limit) against the loop's 7.10 A minimum.
- **A3** the `+5V_DEV` intent note ended "the Glenair port's 0.9 A takes the peak to 6.9 A"; it now says what the figures
  are (INTERIM typical 5.1 A and its three branches, the mode current INCONCLUSIVE, the 6.9 A peak held pending S-99, the
  loop minimum's two figures with their source, SNVSAI1D VSNS 43 mV over 6 mOhm).
- **B1** three comment lines above board B's slot-rail call still said "the peak stays the source's 5.0 A" and "I-03 is
  open"; they now say the peak is 5.63 A on slot 2 since S-98 and I-03 was answered INTERIM.
- **B2** the shared note said the receptacle carries 2.5 A; it says "(4.2 A typical on slot 2)".
- **B6** the `+3V3_DEV` comment said "the loads below sum to 1.38 A"; they sum to 1.582 A since round 8 and w3b (U11 at
  0.165 A, the thirty-six single gates at 0.002 A each; computed from the tracked intent, `readings/` and the check in
  this record's session).

### 1.3 Board B's three M7 findings (CORRECTION.md item M7), each from the held source

| finding | held basis read | what was done | why |
|---|---|---|---|
| U40, U50, U60 (the AP2112K-3.3 LDOs) allocated 0.05 A each on `+5V_DEV` against their child rails `+3V3_IOCx` at 0.12 A typical, 0.25 A peak | Diodes AP2112 datasheet DS39724 Rev. 2-2, `v2/vendor/diodes/diodes-ap2112-ldo.pdf`, pp.4 to 6: quiescent current 55 uA typical, 80 uA maximum at IOUT = 0 mA; the tables give no ground current at load | **0.05 -> 0.12 A each** (`gen_sch_b.py:105`, B5) | an LDO's input is its output plus its ground current; the child declares 0.12 A typical, and 0.12 A holds for any ground current under 5 mA at 0.12 A out (a figure the tables do not state, so named as the bound it is). The typical, not the 0.25 A peak, because every sibling entry of this load map that has a declared child rail sits at the child's typical (U23 1.2 = +5V_LIME's typical, U28 0.25 = +5V_CAM's, U25 0.90 = +3V3_DEV's typical converted) |
| U21 (the TPS22810 load switch to the LoRa module) allocated 0.60 A "at 1 W transmit" against Ebyte's 0.65 A | Ebyte E22-900M30S user manual v1.20, `v2/vendor/lora/ebyte-e22-900m30s-user-manual-en-v1.20.pdf`, section 2.2 operating parameters, PDF p.3: TX current 650 mA typical, "Instant power consumption", no maximum stated | **0.60 -> 0.70 A** (`gen_sch_b.py:95`, B4) | this branch is declared for the transmit state by its own comment, so it must be at least what the child rail `+5V_LORA` declares for that state, 0.70 A (its load U12 at 0.70 A "on a transmit burst at 30 dBm"), which bounds Ebyte's 650 mA typical with no maximum published |
| U25's comment "1.4 A at 3.3 V through it" against `+3V3_DEV`'s declared 1.2 A typical | the generator itself: `+3V3_DEV` declares 1.2 A typical, 2.0 A peak (the AP63203's rating), efficiency 0.88 from 5.0 V | **comment corrected, the 0.90 A allocation stands** (`gen_sch_b.py:92`, B3) | 1.2 x 3.3 / (0.88 x 5.0) = 0.90 A: the allocation already matched the declared typical; the 1.4 A was an older sum of that rail's loads (1.38 A when written, 1.58 A now, B6) |

The `+5V_DEV` load map of board B sums to 5.49 A after these (was 5.18), under its 6.0 A declared peak, so `intent.rail()`'s
invariant (loads sum at most 1.02 x peak, `intent.py:170-172`) holds; `dc_drop` sinks the map's absolute figures, so the
copper of that rail is judged at 0.31 A more than before, the conservative direction. Checked on a projection of the
intent files (`readings/lead-ends-projection.out`), not on a regenerated file: see section 4.

## 2. What the integrator runs, in order (each script asserts, re-parses, refuses a second run)

1. Merge `fnd/s98` (the generators and this record).
2. `python3 v2/docs/records/s98/apply_contract_i03.py` from the integration worktree's root: rewrites the four `currents`
   rows of `IF-AB-POWER` in `tools/pcb_interfaces.yaml` (the +5V_S2 and +5V_DEV rows read AGREE since S-98, INTERIM, the
   mode figures INCONCLUSIVE; the S1/S3 and +54V_POE rows' generator line numbers re-numbered: A 48, 113, 135, 147; B 85,
   111, 271). It reads the generators at run time and refuses if a cited line does not hold its declaration (so run it on
   the tree that carries `c098b8f3`). The `converters` line and its "7.2 to 9.5 A" are deliberately untouched: the
   nominal-shunt arithmetic reproduces (43 and 57 mV over 6 mOhm, SNVSAI1D VSNS p.7, = 7.17 and 9.5 A) but the stage's
   actual limits with the shunt's tolerance are what stream s99 computes, and this stream does not pre-empt it.
   Dry run on scratch copies: `readings/apply-scripts-dryrun.out` (applied, then `REFUSED: already applied`; the parsed
   document differs only in that contract's `currents`).
3. `python3 v2/docs/records/s98/apply_architecture_i03.py`: rewrites the IF-AB-POWER row of `v2/docs/ARCHITECTURE.md`
   (line 1187 at dcf04c90) to the aligned statement and to the held JST VH catalogue. **The premise "ARCHITECTURE.md is
   bound by sha in the registry" does not hold on this tree**: no record of `pcb_requirements.yaml` carries
   `v2/docs/ARCHITECTURE.md@<sha>`, and `git log -S"docs/ARCHITECTURE.md@"` finds none in the file's history (the
   integrator's notes of 28 September say otherwise; the tree decides). The script therefore refuses to run if such a
   binding exists (naming the record, so a rebind entry on the pattern of `records/int7/apply_rebind_final_page.py` is
   written first) and otherwise states that no record is rebound; it asserts that exactly one line changes and reports
   that of the page's 64 sections only "12. Interface contracts" differs, 63 byte-identical. Dry run: same file.
4. The box job `records/s98/box_regen_ab.sh <dir> <commit> <evidence tar> <bundle> <ref>` at the commit carrying 1 to 3;
   then `_bin/install_pack.sh`. Section 3 says what it does and what changes class.
5. The registry closure of S-98 from `registry_s98_closure.md`, with the pack's readings; the LAYER-STATUS rows from
   `LAYER-ROWS.md`.

**Why 1 to 4 belong in one set:** the generators' content changed, so the tracked netlists' provenance sidecars name
generators the tree no longer holds (`sch_prov: pcb-a-power.net was written by generator b3ba8f977ea264e2 and this
tree's generator is 6fa6de3616f33dec`, `readings/sch_prov-read-after-generator-edit.out`). `check_contracts.py` then reads
A and B as MISSING and every contract that names them UNJUDGED (`readings/check_contracts-current-intents.out`:
`check_contracts INCONCLUSIVE of 63, missing_boards 2`), so INT-001 and SCH-003 read INCONCLUSIVE on every board between
the merge and the pack.

## 3. The box job (`box_regen_ab.sh`) and what it changes

Modelled on `_bin/box_retake.sh` (the set 6 re-take) and the schematic phase of `tools/full.sh` (lines 56 to 86) as stream
w5i2c drove it on 27 September. In a throwaway clone at the given commit: for A and B (phase directories from
`rules_status.manifest`, `v2/ecad/pcb-a-power-a23` and `v2/ecad/pcb-b-compute-b19`), the committed schematic, netlist,
intent and provenance are kept as `ref/`, the declared footprint generators run, `gen_sch_<L>.py` with the committed
schematic's Phase label (A65, B21) and the board table's `gen_env`, `build_sch.sh`, `erc_gate.py --run`, and
`regen_compare.py pair` for schematic, netlist, intent, provenance, BOM and ERC. Schematic phase only: no placement, no
route. Then the consolidated re-take driver on EVERY board (`retake_schematic_phase.py --run --in-place --routed --json`),
`reliability.py` per board and `claims_check.py`, the explicit `check_contracts.py`, `interfaces.py` and `lead_ends.py`
readings into `checks/`, and the pack (`tracked.patch`, `tracked-changed.lst`, `ignored-readings.tar`, `MANIFEST`,
`SHA256SUMS`, `REGEN-SUMMARY.txt`, plus `regen/` and `checks/`).

Which files change and which readings bind them:

- `out/pcb-a-power-intent.json` and `out/pcb-b-compute-intent.json` (tracked): the declarations. Readings that record
  them by sha (from the tracked `routed/*.verdict.json` of A and B): `check_contracts` (every board's copy), `inhibit_chain_<letter>`
  (A to E), `interfaces_a`, `interfaces_b`, `intent_rails`, `edge_length`, `port_protect_a/b`, `power_sequence`, `safe_lines_a/b`,
  `switch_list`. All re-taken by the driver; their results are expected unchanged (no tool judges these figures against
  a limit at the schematic phase; `dc_drop`, which judges copper at the declared current, is a routed-phase reading).
- `out/pcb-a-power.net`, `out/pcb-b-compute.net` and their `.net.prov.json` (tracked): the netlist CONTENT is expected
  identical (parity PARITY_AFTER_NOISE: no part, pin or net moves), its sha changes with the export date, and the
  sidecar names the new generator sha. Every reading bound to the old netlist sha is re-taken for that reason. If
  `regen_compare` reads DIFFERENT for a netlist, stop: the generators were meant to change declarations only.
- `tools/pcb_interfaces.yaml` (the integrator's step 2): `interfaces` and `interfaces_<letter>` record it as `spec`;
  re-taken, they read CURRENT again (INT-001 reads CONFIG_CHANGED until then).
- Boards C, D, E, E5 and P: nothing but their copies of the set-level readings above. That is why the driver runs on
  every board: a run on A and B alone would leave those copies recording the old `intent_a` and `intent_b`.

## 4. What was run here, with the exact result lines

- `apply_declarations_draft.py --check`: six PASS lines, `CHECK ONLY: 4 entries, 2 generators; no writes, no marker.`,
  exit 0; the application exit 0; the second run `Refused: this draft has already been applied or attempted.` exit 1.
- `edit_generators_s98.py`: `gen_sch_a.py: 3 edit(s) applied, parses`, `gen_sch_b.py: 7 edit(s) applied, parses`; second
  run `REFUSED: A1 is already applied in gen_sch_a.py`.
- `ast.parse` of both generators: `PASS ast: both generators parse`; the chain's compile pre-check (`python3 -W error`
  compile): `compile ok` both; `tests/test_swallowed_calls.py`: exit 0 on both (`readings/swallowed-calls.out`).
- The CM5 lesson (every module pin listed in `CM5.update`): the diff of `gen_sch_b.py` reaches lines 73 to 117 only; the
  CM5 pin table is at lines 526 onward and is untouched (no pin, part or net is added or moved by this stream).
- `tests/run.py` one group at a time (`readings/tests-*.out`): `contract` `88 passed, 0 failed, 4 skipped` (the two
  "contracts: 2 FAIL of 42" and "final_gate FAIL" lines in that output are fixture output printed by the tests, not this
  tree's readings; run.py's own evidence guard did not fire); `interfaces` `11 passed, 0 failed, 0 skipped`; `power_path`
  `13 passed, 0 failed`; `rail_loads` `10 passed, 0 failed`; `current_model` `4 passed, 0 failed`; `netlist_classes`
  `3 passed, 0 failed`; `shell_parses` `1 passed, 0 failed`. No test file name contains "intent"; `rail_loads` and
  `current_model` are the intent declaration fixtures (PWR-001's fixtures per the coverage map).
- `check_contracts.py` into a scratch `VERDICT_DIR` against the tree's committed netlists and current intents:
  `MISSING netlist for A (pcb-a-power), run its chain first`, the same for B, `check_contracts INCONCLUSIVE of 63
  {missing_boards 2, pass 23, unjudged 40}`, exit 3: the provenance guard, section 2. Before the generator edits the
  same files read PASS 99 of 99 (the tracked reading at dcf04c90), so this is the expected state until the box run.
- `interfaces.py` into scratch: `interfaces: 12 interface assignment(s) over 7 board(s) ... 0 disagreement(s)`, PASS of
  12 (it judges impedance targets, not declarations; it reads the current intents as `spec` inputs unchanged).
- `lead_ends.py` on the tracked intents (before the regeneration): `3 of 5 leads AGREE` (+5V_S2 and +5V_DEV DISAGREE,
  as I-03 found), exit 1. On the PROJECTION (the committed intents with the new declarations written in by hand):
  `5 of 5 leads AGREE`, exit 0, and every rail's loads sum is under 1.02 x its peak (`readings/lead-ends-projection.out`).
- Dry runs of both apply scripts on scratch copies: applied once, refused the second time, the diffs in
  `readings/apply-scripts-dryrun.out`; the worktree's shared files untouched (`git status` clean for them).
- `bash -n box_regen_ab.sh`: ok; the record's four Python scripts parse.
- Dash scan (U+2013, U+2014) of the generators' added lines and of this record: none (`readings/dash-scan.out`).

## 5. What could not be done here, and why

- **No regeneration on this host.** `gen_sch_a.py` and `gen_sch_b.py` read KiCad's symbol libraries
  (`/usr/share/kicad/symbols/*.kicad_sym`, `kisch.py:169`) and the tree's lands; the runner has no KiCad, so a scratch
  run stopped at `FileNotFoundError: Connector_Generic.kicad_sym` before the intent file is written (it is written last,
  `gen_sch_a.py:1649`). The intent preview in section 4 is therefore a projection, labelled as one; the box job produces
  the files.
- **No contract reading AGREE can be shown before the box run**: the provenance guard (section 2) makes the tree's
  contract reading INCONCLUSIVE until the netlists are regenerated with the new generators.
- **The `converters` line's "7.2 to 9.5 A"** was not rewritten: the stage limits with the shunt's tolerance are stream
  s99's; only the nominal arithmetic was reproduced here.

## 6. Residuals (for the integrator; none changes a figure declared here)

- **R1** Board A's `+5V_DEV` allocates 0.3 A to U32 while the child rail `VBUS_WALL` declares 0.5 A typical
  (`gen_sch_a.py`, the VBUS_WALL rail). CORRECTION.md B2 names it ("the 0.3 A parent allocation is not silently
  presented as the child's declaration"). Not changed here because S-98's text and the contract row state 5.1 = 3.8 +
  1.0 + 0.3; it belongs to S-99's re-sum of the branches, whose decision changes this rail's declaration anyway.
- **R2** The contract's `ends` src line numbers (gen_sch_a.py:967-968, 1038; gen_sch_b.py:434, 831, 875) were stale before
  this stream: the connectors are at `gen_sch_a.py:1037-1038` (J_5V_Sx, J_5V_DEV) and `1135` (J_54V), and
  `gen_sch_b.py:551` (J_5V_S%d), `1119` (J_5V_DEV), `1210` (J_54V) at `c098b8f3`. Outside `apply_contract_i03.py`'s scope
  (the `currents` rows), left to the integrator.
- **R3** The lead's own drop is in no board's share of the 2 percent budget (both checks); a contract or budget item, no
  id. At 5.63 A the four VH contacts alone at their 10 mOhm initial maximum give 5.63 x 4 x 0.010 = 0.2252 V (4.42
  percent of 5.1 V); with the pair's copper (150 mm supply and 150 mm return of 16 AWG, 1.25 mm2 at the tree's rho20:
  0.004128 ohm, `records/cx1/ANALYSIS.md`) the lead gives 5.63 x (0.004128 + 0.040) = 0.248441 V, 4.87 percent of 5.1 V
  (0.252094 V, 4.94 percent, with the copper at 60 C). Corrected at integration set 9 (stream s99reg,
  `records/int10/apply_pages_s99.py`): this item first gave 0.225 V as the wire plus the contacts, which is the contacts
  alone.
- **R4** `records/cx1/apply_declarations_draft.applied`, the draft's marker, is untracked by instruction and not
  gitignored (`git check-ignore` exit 1); it will show in `git status` of any tree that ran the draft.

## 7. Decisions taken (authority SESSION, under the owner's standing rule of 26 September)

- **D1** U40/U50/U60 at the child rails' typical (0.12 A), not their peak (0.25 A): the load map's convention on this
  rail (section 1.3). Reversal: set 0.25 if the map is re-based on peaks; the sum would be 5.88 A, still under 6.0.
- **D2** U21 at 0.70 A (the child's declared burst), not Ebyte's 0.65 A typical: a typical with no published maximum is
  bounded by the figure the child rail already declares for the same state. Reversal: 0.65 if a maker maximum below it
  is filed.
- **D3** The 6.9 A `+5V_DEV` peak untouched and its comment pointed at S-99, as the task and S-98's text require.
- **D4** The box job re-takes every board, not A and B alone (section 3, the set-level copies). Reversal: `--board a`
  and `--board b` on the driver, at the cost of stale copies in the other five boards' `routed/`.
- **D5** `apply_architecture_i03.py` makes no rebind because the tree binds the page nowhere, and refuses if that
  changes. Reversal: none needed; the refusal names the record to rebind.
- **D6** The intent preview is a hand projection, labelled as one, because the host cannot regenerate (section 5).

## Files

| file | what |
|---|---|
| `edit_generators_s98.py` | the note and comment rewrites beyond the draft, byte-exact, run once |
| `apply_contract_i03.py` | the integrator's script for `tools/pcb_interfaces.yaml` (IF-AB-POWER `currents` rows) |
| `apply_architecture_i03.py` | the integrator's script for `v2/docs/ARCHITECTURE.md` (the IF-AB-POWER row) |
| `box_regen_ab.sh` | the box job: regenerate A and B (schematic phase), re-take, check, pack |
| `lead_ends.py` | declaration consistency of the five leads from the two intent files; writes nothing |
| `LAYER-ROWS.md` | draft rows for LAYER-STATUS items 4.10 and 5.5, consistency and adequacy apart |
| `registry_s98_closure.md` | what closes S-98 after the box run and what stays open |
| `readings/` | every output named in section 4 |
