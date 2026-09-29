mergeable: yes

# Third check of stream w5identc (board C's part identities), MESHSAT-1357

AI review, labelled as such: an independent check by a Claude session that did not write the work. It is not a
qualified engineering review. 29 September 2026, 21:16 to 21:30 CEST (read from `date`).

Branch `fnd/w5identc` at `ff69f6fe` (confirmed), two commits on `633697a7`, authored and committed as the owner, no
trailer. Checked in a new shared clone at `_scratch/chk-w5identc` (sparse: `v1/`, `v2/images/` and `v2/release/` left
out except `v2/release/handover/_generated/`) and in a second sparse clone of `fnd/int15` at `1bafab8c` with the branch
merged (clean, tree `553ef257`). Both clones are removed. The Uniroyal sheet was fetched afresh with
`fetch_held_back.py` (sha256 matched).

## Blocking items

None.

## Minors

1. A cited row may begin inside a token of the page. Uniroyal's quantity row cut to `D=B/B-20000pcs` (from
   `BD=B/B-20000pcs`) or `C=T/R-10000pcs` (from `TC=...`) reads DECODED with D or C given the Chip Product meaning. Both
   are real quantity codes and no property is decoded from quantity, so no part number outside the scheme is accepted
   on these two pages. Still, read the entries from the page's own segment, or require the cited row to start at a
   token boundary on the page.
2. The PRINTED design part rule strips a trailing `T` or `R` as a reel suffix. Some makers use such a letter for another
   package: `printed_is_the_design_part(["2N7002"], {"C8545"}, "2N7002T")` is True. The value also wins over a
   disagreeing order code: a value naming PCA9555PW with C15850, a Samsung capacitor in this tree's reading, is True.
   Neither is reachable today: no held page prints such a sibling of board C's printed parts. Decision 59's outcome still
   defines PRINTED without the design part condition that rule D-2 and the tool now carry.
3. The H1 to H8 and BZ1 reasons read only the netlist value, where ASSEMBLY.md says more:
   * line 55 gives the backer screws as "M3 x 6 A2" into PEM SO-M3-10 standoffs, 0.4 N m, Loctite 243. The next action
     still asks for the material.
   * line 72 fits the sounder as "Floyd Bell MC-09-530-Q ... two leads to the lands", which accepts the blades with
     leads.
   Both statuses (CHOICE_OWED) stand; cite the lines as J_MAINSW and J_PIJ2 now do.
4. The filed `checks/check-w5identc-2.md`, minor 4, now reads "cites `v2/docs/records/w5identc/checks/check-w5identc-1.md`,
   which is outside the repository". The scrub replaced the scratch path, so the sentence is false as filed. Keep the
   original words, or add a note that the finding is answered.
5. In the sparse clone, `test_public_tables` (2) and one `test_driver_hygiene` test skip for want of `v2/release/`. That
   is my set up, not the stream's; the box suite covers them.

## Answers to the five questions

1. **BB1.** Refused on the makers' pages:
   * the V and E probes of the second check, as bindings and as table edits;
   * prefixes of real codes (`T` of TC, `B` of BD);
   * `W4` claimed on the `W=Normal Size` row;
   * codes cited on a neighbouring row: K on the packing row, D on the Chip Product row, F on the power row, 8 claiming
     250 V from `Y = 250 V 8 = 25 V`;
   * meanings spanning two entries (`± 10% M = ± 20%`, `6.3 V 0 = 100 V`);
   * a truncated meaning (`± 5`).

   The true parts still decode (CC0603KRX7R8BB105 on C37, 0603WAF1002T5E on R50, W4 at 1/4 W). The 27 probes of the
   second check are still as expected, and the metric size row is refused. Accepted: minor 1 only.
2. **BB2.** J_PIJ2 is UNRESOLVED CHOICE_OWED on ASSEMBLY.md line 127 ("24 AWG | soldered, beaded"), and J_MAINSW cites
   line 126. The builder refuses if either line's words change. Every NOT_A_PART and CHOICE_OWED reason, read against
   the tree:
   * true: JP1 and JP2 (solder jumpers, nothing bought), the 17 lamps (ASSEMBLY.md line 58), both jacks (line 69 and
     the scan), J_MAINSW, J_PIJ2 and C28;
   * true but incomplete: H1 to H8 and BZ1 (minor 3).

   Counts from the table: CHOICE_OWED 24, NOT_A_PART 2.
3. **PRINTED.** Siblings that the cited pages print are refused as table edits: TLV75528PDBVR and TLV75533PDQNR (TI
   p. 28) for U5, PCA9555DBR (p. 31) for U1. So are C28 bound to PCA9555PWR and the 24 way J_EPD bound to
   FH34SRJ-26S-0.5SH(50). PCA9555PW (the tube of the same part) holds, correctly. An order code whose reading names
   another part refuses where the value does not name the part (C1 and C2 as CC0805KKX7R7BB106 with C15850), and binds
   the code's own part (CL21A106KAYNNNE). Latent reach: minor 2. All 21 PRINTED bindings read "the value names ...", and
   each netlist code present reads as the same part in this tree's catalogue.
4. **The chain on `1bafab8c` plus the branch:**
   * before: `rules_lib.py requirements` 0 errors, 0 warnings, and the check reading is byte identical;
   * `apply_decision_decoded.py --check` then the write: decision 59, CFL-016 rebound from `a41df5d12ff95995` to
     `823a6b32baf41481` (the decisions file's new sha256);
   * second runs of it and of `apply_rebind_decisions_w5identc.py` refused;
   * after: `requirements` 0 errors, 0 warnings; `decisions_render.py`;
   * `apply_identities_c.py` opened S-125, and a second run was refused;
   * `validate` 0 errors, `rules_render.py --requirements` wrote;
   * test_requirements, test_layout_entry_stages, test_decision_register and test_part_identities: 105 passed, 0
     failed, 3 skipped.
5. **Replay.** All byte for byte:
   * `build_table.py` rewrites the table (`bea90e3c...`) and its document reads;
   * `check` writes the reading `45d8f109...` (the sha256 pinned in `apply_identities_c.py`);
   * `render` rewrites BOARD-C-SELECTIONS.md;
   * `scan_vendor.py` (fixed list: 429 PDFs read, 11 without text, 51 part numbers, 19 with a hit) matches the committed
     reading.

   test_part_identities 27 of 27; nine lint and sweep modules pass (skips as in minor 5).

## Counts

Blocking 0, minors 5.
* Probes on the makers' pages: 27 of 27 as expected from the second check; of the 15 new ones, 13 as expected and 2
  accepted (minor 1, meaning only).
* Table edits through `check`: 18 run. 15 refused, 2 held correctly (a scheme edit ignored, the tube variant), and 1
  held under the carried range table limit.
* PRINTED design part function probes: 6, 2 of them latent (minor 2).
* Reasons checked by hand: every NOT_A_PART and CHOICE_OWED reason (8 distinct reason texts covering 26 selections).
* The box suite was not run.
