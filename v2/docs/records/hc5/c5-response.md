# Targeted fixer c5: response to hc5 review 2 (MESHSAT-1357, 27 September 2026, about 11:25 CEST)

Layer 5 closer hc5, worktree `fnd/hc5` (base `e3aedb25`), after its second full review failed. Per the owner's execution
prompt (section 4, a change of method after two unsuccessful attempts), this pass fixes only the review's two blocking
items and re-checks that every draft still applies to `main` at `a8652172` (H1). Nothing is committed, pushed or run in
the main tree; the KiCad box was not used. Prototype framing: nothing here is built, ordered, powered or measured.

## Item 1. SC-HF-06's touch lead to board D's `J_USB3`, carried consistently

**Finding (review 2, blocking 1).** IF-MON and SC-HF-06 put the monitor's touch USB on board D's `J_USB3`, but once the
drafts were applied three places disagreed: section 12's draft listed `J_USB3` under "Not given a contract, deliberately
... (no lead is defined)"; `ASSEMBLY.md` build step 9 still sent the touch lead to "the slot hub header" on B16; and
`PANEL.md` section 1's Pass-throughs row sent all three monitor leads "to B16 and A22".

**What changed.**
- `drafts/hc5/ARCHITECTURE-section-12.md`, the closing "Not given a contract" paragraph: `J_USB3` is removed from the
  list, and a sentence now says it is the board end of the touch lead under SC-HF-06, contracted in IF-MON, `ASSEMBLY.md`
  section 4 and build step 9, and `PANEL.md` section 1.
- `drafts/hc5/apply_docs.py`: two new edits outside hc5's own sections, each with its reason in a comment and in the
  docstring.
  - `ASSEMBLY.md` build step 9: "... to B16 `J_HDMI`, the slot hub header and A22 `J_MON`" becomes "... to B16
    `J_HDMI`, D8 `J_USB3` (the touch lead through its USB A to PH 1x4 adapter, section 4; the session's choice SC-HF-06
    ...) and A22 `J_MON`".
  - `PANEL.md` section 1's Pass-throughs row: HDMI and 12 V go to B16 `J_HDMI` and A22 `J_MON`, and the USB touch
    lead goes to D8 `J_USB3` through the adapter of `ASSEMBLY.md` section 4 (SC-HF-06).
  - The rebinding follows the same pattern as before. The CHANGED texts for `PANEL.md` and `ASSEMBLY.md` name the new
    edits. CFL-016's note, and CFL-001's note on `PANEL.md` (a new per-page note), say that section 1 changed only in
    its Pass-throughs row, which they do not cite. CFL-001's note on `ARCH-PCB-B-IOHA.md` now names only that page's
    cited sections. CFL-015's `ASSEMBLY.md` note still holds: its Pack SMBus row and build step 7 are unchanged.
- `drafts/hc5/pcb_interfaces-new-contracts.yaml` IF-MON `harness`: the dangling pointer "ASSEMBLY.md's row is corrected
  by drafts/hc5/apply_docs.py" (a drafts path in data that gets committed) is replaced by the pages that name D8 `J_USB3`
  (section 4's row, build step 9, `PANEL.md` section 1).
- `v2/docs/HW-FW-CONTRACT.md`: the SC-HF-06 row lists every page that carries the board end, and section 10 gains a
  "1 (second review fixes)" row.

**Evidence.**
- Board D netlist `v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net` (sha256/16 `0dad82b4b6a79290`, unchanged from `84e52461` to
  `a8652172`) gives `J_USB3` pin 1 `/+5V_D8`, pin 2 `/USB3_N` (R21, R23), pin 3 `/USB3_P` (R20, R22) and pin 4 `GND`.
  `gen_sch_d.py:509` reads "spare hub port 3, 5V D- D+ GND (the lead is made up at build)", and its budget line at `:58`
  is `"J_USB3": 0.05`.
- `ASSEMBLY.md` build step 5 puts D8 on A22's standoffs before step 9. Step 9 already runs the PA bias and headset leads
  to D8, so the touch lead reaches `J_USB3` at the same step.
- After the five scripts on a scratch clone of `a8652172`, the phrase "slot hub header" is left only in the historical
  sentence of `HW-FW-CONTRACT.md` SC-HF-06 ("`ASSEMBLY.md` named ..."), and "no lead is defined" is gone from
  `ARCHITECTURE.md`. No generator or netlist changed, so no board B change is implied, as SC-HF-06 states.

**Outcome: CLOSED** in the drafts (worktree hc5), to be applied by the integrator. SC-HF-06's costs stay where pass 2
put them: HF-F06 on board D (a VBUS limit on `J_USB3`, and the 0.05 A budget line set from the draw that V-B19
measures). That is an open design item already recorded, as the registry's next free S number on `a8652172`: S-50.

## Item 2. IF-BA-RF's D-07 note

**Finding (review 2, blocking 2).** The RM520N-GL path note said "ANT3 under owner ruling D-07 needs board A's site at X
+46 and board E's clamp: in no generator". Since `45f6d83f` board E's generator draws the twelfth cavity at X 46, so the
note told a recipient that board E's half of D-07 was still owed.

**What changed.**
- `drafts/hc5/pcb_interfaces-new-contracts.yaml` IF-BA-RF:
  - the path note now says that board A's site at X +46 is in no generator (`gen_pcb_a.py` and `gen_pcb_a3.py` `RF_X`
    hold eleven sites, none at 46), and that board E's cavity at X 46 has been drawn since `45f6d83f` (`gen_pcb_e.py`
    `RF_SITES` (46.0, "5G ANT3"), checked by `check_pcb_e.py` `_D07_X`);
  - the first `tbd` entry says the same, with its effect: the third 5G antenna has no path until board A carries its
    receptacle and SMA jack;
  - `findings` stays `[D-07]`, with a comment directly above it that says the same thing.
- `drafts/hc5/ARCHITECTURE-section-12.md`, IF-BA-RF row, open items column: the same sentence.

**Evidence** (at `a8652172`):
- `gen_pcb_a.py:38` and `gen_pcb_a3.py:65`: `RF_X = [-52, -38, -24, -10, 4, 18, 32, 60, 74, 88, 100]`.
- `gen_pcb_e.py:44`: `RF_SITES` includes `(46.0, "5G ANT3")`.
- `check_pcb_e.py:81`: `_D07_X = 46.0`, required whether or not board A carries the site.
- Commit `45f6d83f` ("the blind-mate float clamps become one bar with twelve cavities, D-07's at X 46 among them").
- `ARCHITECTURE.md` section 1.3's D-07 row already reads the same ("board A carries eleven sites; board E's clamp at X
  +46 is drawn since round 8").

**Outcome: CLOSED** in the drafts. The design gap the note describes, board A's third site, is not new. It stays open
under D-07 and CON-015, owned by board A's author, and this pass changes no record of it.

## Item 3. Every draft re-checked against `main` at `a8652172`

**Finding (task).** `main` moved from `84e52461` to `a8652172`. Its registry holds S-47 (HC9-E1) and SC-13 to SC-16, and
the layer 6 closer (`99cde56b`) rewrote S-41 and three IOHA sentences that hc5 corrects. On `a8652172`,
`apply_registry.py` stopped at the S-41 anchor and `apply_docs.py` stopped at the IOHA section 6 anchor.

**What changed.**
- `apply_registry.py`: S-41's edit is skipped when S-41 already reads 0x34 to 0x36 and no longer 0x30 to 0x32 (hc6's
  wording). New records still take the next free numbers where the script is applied, never a hard-coded number:
  - on `a8652172`: S-48 and S-49 (SC-HF-02 to draw, HF-F02), CON-023, and S-50 and S-51 (SC-HF-06 with HF-F06, HF-F07);
  - on `84e52461`: S-47 to S-50;
  - on `e3aedb25`: S-46 to S-49.

  CON-023's `waits_on` follows the number taken. The drafts create no session_choices record, so they take no SC-nn
  number.
- `apply_docs.py`:
  - `edit()` accepts a tuple of markers, one of which may be another stream's wording of the same fact.
  - The IOHA section 6 part edit and 10a's two H743 sentences are skipped where hc6's wording is present.
  - The SC-HF-02 and FW-B08 sentences go after hc6's "CORRECTED at `458b2873`" heading.
  - The address block and 10a's per-controller part are edited as before.
- `apply_architecture.py` docstring and README step 4: board E's `r8e-4-docs` patch has been on `main` since `45f6d83f`,
  and nothing is left to drop. Section 12 is byte-identical from `84e52461` to `a8652172`, so the whole-section
  replacement drops nothing that `main` added.
- `v2/docs/records/hc5/check_contract_fields.out.txt`: re-run on `a8652172` after the five scripts, exit 0. The header
  names `a8652172`, and the body is byte-identical to the pass 2 run. `apply_index.py`'s row text follows.
- `drafts/hc5/hc5-shared-files.on-a8652172.patch`, the result of steps 1 to 5, replaces the withdrawn `84e52461` patch.
  `git apply --check` passes on a pristine export of `a8652172`.
- `drafts/hc5/README.md`: a c5 paragraph at the top, the ids on `a8652172`, steps 3 and 4, the checks, and two
  hand-offs (below).

**Evidence** (all on scratch clones under `scratchpad/c5/`; nothing written in the main tree):
- The five scripts apply on `a8652172`, `84e52461` and `e3aedb25`, and a second run changes nothing on each.
  `rules_lib.py requirements` reads 133 records, 0 errors and 0 warnings on each. On `a8652172` it reads the same again
  after `rules_render.py --requirements`, and `rules_render.py --requirements --check` then reads current.
- `check_contract_fields.py --all`: 18 of 18.
- `tests/run.py test_interfaces test_requirements test_review_packet test_artefact_recording`: 103 passed, 0 failed, 1
  skipped. The skip needs `out/rule-audit`, which is gitignored; in a run where the audit had been produced, the same
  set read 104 passed.
- `tests/run.py test_certify_identity test_order_codes test_safe_lines test_spacing test_handover_pack
  test_decision_register test_stale_readings`: 90 passed, 0 failed, 3 skipped. All three skips are on the same kind of
  gitignored evidence.
- The full suite was not run; it is the integrator's.
- `main` moved to `84d0a527` (H1.1, handover pages only) while this pass ran. Of the nine files the scripts edit, only
  `v2/docs/records/README.md` changed, by one `handover/` folder row, and `apply_index.py` applies to it, twice, on
  an export of `84d0a527`. Nothing else the drafts read or cite changed: the generators, board D's netlist,
  `check_pcb_e.py`, the registry and the pages are all byte-identical to `a8652172`.

**Outcome: CLOSED.**

## Choices taken in this pass (the session's, under the owner's standing rule of 26 September 2026; not the owner's)

- **IF-BA-RF `findings` stays an id list (`[D-07]`), with the sentence in a YAML comment above it.** A descriptive
  string was not put in the list.
  - Why: the file's header says that finding IDs are defined in `ARCHITECTURE.md` sections 13 and 14, and every other
    contract's `findings` holds ids only.
  - Reversal: the integrator's re-anchor may give board A's X +46 site its own finding id and list that id instead.
- **IF-AE-RF, one of the first twelve contracts, is not edited here**, although its `five_g_ports`, `nests`, board E end
  and `judged_by` still describe board E's clamp as not drawn.
  - Why: review 2 assigns the first twelve contracts' staleness at round 8 to the integrator's re-anchor, outside this
    closer's list, and this fixer may fix only the named findings.
  - Reversal: the integrator edits IF-AE-RF, with `ARCHITECTURE.md` section 13's W4-F10 row, in the re-anchor. It is
    written up as a hand-off in `drafts/hc5/README.md`.
- **The touch lead is routed at build step 9 through the adapter of section 4.** It is not a new step.
  - Why: D8 is fitted at step 5, and step 9 already runs D8's PA bias and headset leads.
  - Reversal: move the clause to a later step if the build order changes.

## Review 2's minor items: not in c5's list, unchanged, carried for the integrator or the next pass

The following stay as review 2 states them:
- V-B19's placement in section 3.3.
- IF-E-WATER's "and above".
- IF-E-SENSORS' judged_by: check_contracts section 16 for R48, topology only.
- SC-HF-01 to 06 in the registry's session_choices or `pcb_decisions.yaml`.
- Filing the ZEROIZE 90 kHz re-run (`drafts/hc5/zer/`) as a records/hc5 entry, and the stale `F_I2C` comment.
- HF-F06's severity, its layout-entry carriage and IF-MON's D8_EN sequencing.
- IF-EXT-DC and D-16.
- IF-DA-VHF's "key-down rule K1".
- FW-A08's count of six PCA9555.
- The first twelve contracts' round 8 staleness.

The README's `r8e-4-docs` note was fixed under item 3, because it is part of re-applying on `a8652172`. None of the
minor items is a blocker of the two closed items.

## Hand-offs added

- Integrator, re-anchor: IF-AE-RF and `ARCHITECTURE.md` section 13's W4-F10 row, as above.
- Integrator, at the merge: the handover pages still say the touch USB has no board end:
  - `v2/docs/handover/LAYER-STATUS.md` lines 694, 719, 735, 742, 754, 783 and 809 at H1.1 (`84d0a527`); lines 680 to
    795 at `a8652172`;
  - `v2/docs/handover/CONTINUATION-BRIEF.md` line 203 at H1.1; line 186 at `a8652172`.

  After this merge they cite SC-HF-06 and HF-F06, at the next snapshot. The frozen `v2/release/handover/H1/` copy is not
  edited.
