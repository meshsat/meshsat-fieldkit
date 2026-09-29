mergeable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026); B1 and M9 answered by apply_s117_restate.py, the rest carried in CLOSURE.md. -->

# AI review of integration set 10: fnd/int11 at 2cbbef38 onto main c5f93464 (MESHSAT-1357, 29 September 2026)

This is an AI review by a checker that wrote none of the candidate. It is not a qualified review. Prototype design:
nothing here has been built, ordered or measured. Scratch clone at 2cbbef38, the int11 worktree's gitignored readings
copied in (927 files, caches left out); nothing was written outside this clone and this file, and the clone's
tracked tree is clean.

One blocking item, the U3 row and S-117 (brief item 5). The tools, the registry text, the regeneration, the rebinds,
the pages and the merged records otherwise check out; the minor items below can follow in the next set.

## Blocking

**B1. Board A's charger row (pcb_emc.yaml U3) and S-117 misread SLUSE66A, and they hide a schematic omission.**
The row and S-117 say U3 "switches at the frequency its PWM_FREQ bit selects: 400 kHz at power-on" and that the maker
recommends "4.7 uH at 400 kHz and 2.2 uH at 800 kHz". They open S-117 on a 400 kHz against 3.3 uH mismatch, a
firmware choice at LAYOUT_STAGE, "no schematic-phase record rests on the frequency". The held datasheet
(v2/vendor/ti/bq25731-datasheet.pdf, SLUSE66A, June 2020, revised January 2021) says more:
- 9.3.11 (p.27): "The charger reads both converter operation frequency and the inductance value through the
  resistance tied to IADPT pin before the converter starts up." Table 9-4 (p.27): 2.2 uH (800 kHz) 137 or 140 kOhm,
  **3.3 uH (recommended for 800 kHz) 169 kOhm**, 4.7 uH (400 kHz) 191 or 187 kOhm. "A surface mount chip resistor
  with +/-3% or better tolerance must to be used for an accurate inductance detection."
- Pin table, IADPT pin 8 (p.6): "This pin is also used to program the inductance used in the application." It also
  asks for a 100 pF or smaller capacitor from IADPT to ground.
- Table 9-9 (p.43), PWM_FREQ: 1b = 400 kHz is the register's POR default, as the row says. The row leaves out the
  mechanism above and the 3.3 uH row.

**Counter-example, from the committed netlist** (`pcb-a-power-a23/out/pcb-a-power.net`, parsed): net IADPT carries
only U3 pin 8 and TP19. Board A has no resistor and no capacitor on it. L2 (XAL6030-332ME, 3.3 uH, CH_SW1 to
CH_SW2) is the charger's inductor. The maker lists 3.3 uH, at 800 kHz with 169 kOhm, so the fitted part is not in
itself the mismatch S-117 describes. The operating frequency with no IADPT resistor is not stated by the maker, so
the row's `f_khz: 400` has no basis. S-117's closing condition (a firmware setting plus L2 against the ripple
guidance) could close with the maker-required resistor still absent.

**Fix, all text plus one new item:**
1. Restate the U3 row's basis with 9.3.11, Table 9-4 and Table 9-9, with pages. Mark `f_khz` as undetermined until
   the IADPT resistor is drawn, or state it as a bound.
2. Restate S-117's title and closing condition the same way.
3. Open a schematic-phase item for board A's writer: the IADPT resistor (169 kOhm at 1 percent for 3.3 uH at
   800 kHz, or 187/191 kOhm with a 4.7 uH part) and the 100 pF or smaller capacitor.

This defect exists on main already, and this set did not introduce it. What this set adds is the record that
describes it wrongly.

## Minor

- **M1. PASS with zero passes.** `intent_checks.py` writes `intent_decoupling` PASS when every entry is justified
  or recorded. The fixtures lock this in: `g_far_named` asserts PASS with {pass 0, justified 1}, and `g_recorded`
  asserts PASS with {pass 0, recorded 1}. `verdict.py` and `rules_status.py` know no justified class, so a board
  whose every entry is a deviation, or board P with only class A entries, would read DEC-001 PASS in the pages.
  8.2 says "a justified deviation is counted as such and never as a pass". Take and record a decision: either the
  verdict reads other than PASS when pass is 0, or the pages carry the justified and recorded counts.
- **M2. The placer skips the far-side refusal for a capacitor it leaves in place.** In `bypass_place.py`, the
  "already within its class's limit" shortcut (`st0 == "pass"`) never calls `far_side()`. A capacitor already on
  the far side, inside a fanned part's fan box or over a through-hole part, with loop-equivalent distance within the
  screen, is counted near and not moved. The gate refuses the same capacitor. Separately, `bypass_search.Context`
  counts declared far-side capacitors when it decides whether a board is two-sided, and the gate excludes them. No
  false pass results, because the gate decides.
- **M3. One cause at a time in the escape cost.** `escape_cost.Cost.ask` tries the three causes one by one. A pad
  refused jointly, for example by a window capacitor and a far-side one, is filed under "refused for another
  reason", so T4's per-cause cost can under-report. Ask the union last and name the causes jointly.
- **M4. Stale text in DEC-001's coverage row.** `_classes_why` in `pcb_rules_coverage.yaml` says `bypass_seats.py`
  "still walks to a flat 3.0 mm measured to the capacitor's centre". Since 91e7649e it takes each class's screen
  and the rail pad (`bypass_seats.py:84-90`, `:204-206`, and the d6dec README's T2 row). The fingerprint comment
  above `rule_set_fingerprint` still names only the move of 26 September; it does not name the move of
  29 September from 635ff031f210f48c. DECOUPLING.md 8.1 T8's "the fingerprint does not move" also proved wrong,
  as c65ee303 explains.
- **M5. The closure does not say what a re-read gives now.** CLOSURE.md says DEC-001 reads INCONCLUSIVE "until
  each board's next placement" and that measured failures move from 40 to 39. It does not say that the d6dec
  README's out-of-tree read under the new text is FAIL on all six committed placements (0 pass on A, B and P).
  Add that sentence, or take the six `intent_decoupling` re-reads on the placed boards on the box, so that the
  drop is not read as progress. Nothing claims DEC-001 passed, which I checked.
- **M6. Two merged diagrams are stale at the candidate.** `v2/docs/diagrams/tools/build.py --check` reads 9 of 11
  current: control-lines and power-tree have inputs changed (the six netlists and `pcb_interfaces.yaml`, moved
  after 2781cee6). In my clone, `power_tree.py`, which has no check mode and wrote, changed only its netlist sha and
  commit labels; I restored the files. Rebuild both on the box, or record the staleness in the closure.
- **M7. An owner acceptance with no record in the tree.** CLOSURE.md says section 9 is "the reference analysis the
  owner accepted on 29 September" and that the owner assigned both slots to Option A(i). Nothing in the tree
  records those words; EXECUTION-PLAN.md at main still lists OD-02 as "Owner decisions required". Record the
  owner's words with their date, or attribute the statement to the integrator.
- **M8. `apply_repin_netlists_int11.py` guards less than its docstring says.** The docstring says it refuses "an
  old sha that no file carries", but the code refuses only when the new sha is already present. It parses the
  texts before writing and does not re-read what it wrote. The result is correct (below).
- **M9. The U41 row is loose about which net leaves board A.** It says "Its output leaves board A on J_MEZZ_PWR1".
  U41's output is +5V_D8IN (through L13), which reaches J_MEZZ_PWR1 as +5V_D8 through the eFuse U23 (netlist).
  Name U23.

## What I verified

1. **Identity.** All 46 commits in c5f93464..2cbbef38, the merges included, have the owner as author and as
   committer (`Kyriakos Papadopoulos`, `ncpjfuzl@mxmx.email`). No co-author trailer. c5f93464 is an ancestor
   of the candidate.
2. **d6dec's tools against DECOUPLING.md 8.1.**
   - T1: `fan_select` and `decoupling_rules.escaped`, `copper_fanned` and `fanned` carry escape.py's old
     selection unchanged. The paste apertures are dropped from the copper term only. The AST test holds escape.py,
     both placers and bypass_seats to one selection. Every fixture of the text is present, on committed lands.
   - T2: one `limit()` keyed by class. Rail pad to pin is measured in the gate, in `bypass_search` (both placers)
     and in bypass_place's current-position read. `maker_mm` 5.0 is declared on D's C31 and C32.
   - T3: four rotations at every seat.
   - T4: `fan_blocks` opens only the own-pin window and the converter's own fan. The cost and the closure are
     recorded with a staleness guard.
   - T5: `intent.write` refuses no class or no basis. Class L and R fields are noted, not refused: decision S-1,
     recorded with its reversal.
   - T6: `parse_allow`. The blanket lines are gone from all twelve files, including the phase folders; decision
     S-4, recorded.
   - T9: the gate's far-side rules and the via allowance from the stackup row. 3.54 mm against the page's 3.7 is
     decision S-3, recorded.
   - T10: `own_via`, with no own via read as justified, never pass.
   - The four B1 entries are declared against a buck's inductor output pad (B) and an LDO's output pin (D), as
     8.2 asks.
   - Tests run here: test_decoupling_rules 31 passed, test_escape_cost 11, test_intent_bypass_class 6,
     test_exposed_pad_vias 9, test_emc_sheet 7, test_rule_gate_mapping 18, test_interfaces 10, all with 0 failed.
     test_decoupling_board: 28 skipped (no pcbnew here).
3. **T7 and the coverage stamp.**
   - DEC-001's sources, source_status, acceptance and rationale match DECOUPLING.md 8.2 word for word; the four
     sha256 values are written whole.
   - All four source files are tracked and hash to the stated sha256, `intel-an574.pdf` included.
   - The coverage row keeps HEURISTIC_AS_LAW and names bypass_seats.py.
   - `rule_set_fingerprint` equals what rules_lib computes: a9b1e7f7412f9c0c.
   - DEC-001 reads INCONCLUSIVE on A, B, C, D, E and P with the rule-version reason. No page or record claims it
     passed.
4. **Regeneration.**
   - Parity: regen-summary.txt reads PARITY_AFTER_NOISE for schematic, netlist, intent and ERC, and PARITY for the
     BOM, on all six boards. check_contracts PASS of 99.
   - Netlists: parsed as s-expressions with every `(date ...)` and `(source ...)` node dropped, all six are equal
     to main's, and `netlist_sexp` pins are equal.
   - Intents: only `written` differs.
   - Schematics: parsed with every date string normalised, all six are equal.
   - The provenance sidecars' per-file hashes match the candidate's files.
   - `apply_rebind_netlists_int11.py`: its guards are sound (field diff, results unchanged, other sections
     unchanged, re-parse).
   - Registry: 25 records have moved bindings (CHO-001, CON-003, CON-010, CON-015 to CON-019, CON-021, CON-022,
     CFL-002, CFL-004, CFL-005, CFL-013 to CFL-016, FEA-002, REQ-012, REQ-030, REQ-032, REQ-036, REQ-044, REQ-071,
     REQ-077). Every moved binding goes from main's sha to the tree's sha of the same file; no evidence_result
     moved; no record was added.
   - The 15 configuration pins (holds, port reviews, reliability list) move exactly from old to new.
   - The six sheets differ only in their bound block and `read` line.
   - `constraints_bound.py` PASS, including rail_widths.out byte for byte against a fresh run.
5. **Carried items.**
   - M2: gen_sch_a.py line 140 is the `+5V_DEV` rail call.
   - M11: seven LM5176 are declared on A.
   - U41's pin 1 is unconnected.
   - M10 and S-117: see B1.
6. **Pages.**
   - rules_lib: 59 rules, 144 records, 0 errors.
   - rules_render --check: 16 documents, 0 out of date.
   - rules_render --requirements --check and decisions_render --check both exit 0.
   - 34 layout-entry reasons (13 + 21), as on main.
   - The moved rows are explained by this set:
     - The netlist shas.
     - DEC-001: A from FAIL, and B to P from PASS, to INCONCLUSIVE (open pairs 138 to 143, PASS 200 to 195, FAIL
       40 to 39, NOT_CURRENT_EVIDENCE 14 to 20).
     - "Changed only their first failing cause" 108 to 102: the same six DEC-001 rows.
   - The 90 re-taken verdicts differ from main's only in bundle, inputs, timestamps and netlist shas; no status
     moved. E5's check_contracts_e5 FAIL is also FAIL on main.
   - CON-010 and REQ-044 bind the final page, 545ec33794283272.
7. **Merged records.** Energy section 9 is labelled a model result on the reference day, with "REQ-072 stays FAIL
   until a design is built and tested". The diagrams carry "design diagram of an unbuilt prototype". Neither claims
   physical verification. No em dash in any added prose, and no host name or address in the added text.
