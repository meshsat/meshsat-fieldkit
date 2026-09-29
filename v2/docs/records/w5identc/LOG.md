# Log, stream w5identc (29 September 2026, times CEST, read from `date`)

- 19:20 worktree `fnd/w5identc` from `b874b744`. Read the brief, WORKER-RULES, w5ident's README and the results of its
  three checks (grouping, identity, drafts) from the integrator's workflow journal wf_c058de22-937.
- 19:25 board C's netlist parsed: 225 parts, 50 exclude_from_bom, 175 BOM parts; the committed BOM export has 167 rows
  and lacks D23, R50 to R56, and reads R14 as 10k (the netlist 2.2k 1%).
- 19:28 `adapt_tool.py` applied eight edits to w5ident's tool (parsed netlist, V-1 (a') and (g), imports); rows, check,
  render and main rewritten; docstring rewritten.
- 19:30 probe of every document w5ident bound for board C: the eight IC and discrete documents on main print their part
  numbers (pages recorded); none of the passive series sheets on fnd/w5ident prints a complete part number.
- 19:31 `build_table.py` first run; `part_identities.py check` 0 problems. Checkpoint `6542fcdf`.
- 19:36 fetched Vishay's VEML7700 sheet and AOS's AO3401A sheet (both name their parts; Vishay's reads "ALL RIGHTS
  RESERVED"); Winbond's W25Q16JV URL gave 404, Abracon's ABM8-272-T3 404, Hirose's FH34SRJ 403. Then found that the
  tree already holds AO3401A, VEML7700, TLV755P and W25Q16JV documents (read every PDF of 21 vendor folders for each
  owed part number): the fetched copies were deleted, nothing was filed, nothing is held back.
- 19:38 Abracon's sheet tried at the archive: 404 twice.
- 19:39 held documents bound (5 selections); maker name of the 2N7002 as its sheet prints it; table 87 selections,
  RESOLVED 20, UNRESOLVED 63, NOT_A_PART 4; check HOLDS; tests 16 of 16; `apply_identities_c.py --check` holds; applied
  once and refused a second time on a scratch copy. Commit `b0a2b61c`.
- 19:40 V-1 on board C measured (`readings/v1-on-board-c.txt`): no floor net; rule (g) moves 21 nets, 0 keys.
- Lint tests run once each on this tree: test_rule_windows 6/0, test_import_before_use 3/0, test_documented_options
  6/0, test_swallowed 6/0, test_shipped_strings 5/0, test_driver_hygiene 78/0, test_public_tables 2/0. The full suite
  was not run (the integrator's, on the box).

## Round 2 (the coordinator's message after round 1)

- 19:43 read the two asks: the DECODED rule, taken by the session, drafted for pcb_decisions.yaml; the stale BOM
  export's facts.
- BOM export: `git log` on the file (one commit, `6dc4e708`); its writer read in `handover_exports.py` (`exports`,
  line 138) and ruled out in `build_sch.sh` (line 34, `out/<stem>-bom.csv`) and `finish_board.sh` (`out/jlc/`); parsed
  against the netlist at nine commits (`readings/bom-export-history.txt`): agrees until `e28f91a6`.
- `read_decoded` added to the tool; four fixture tests; 21 of 21.
- Terms screen of w5ident's series sheets: Yageo, Fenghua and Arlitech carry no reproduction or rights wording in their
  text; Uniroyal's two read "all rights reserved"; Murata's catalogue prints the word "Prohibited" once (line 20849 of its text, a column heading beside "Correct"; not read further).
- 17:49Z (UTC) `fetch_held_back.py` fetched Uniroyal's thick film sheet from LCSC's datasheet server, sha256 matched.
- Builder: decode specs for Yageo CC X7R (page 2) and Uniroyal 0603WAF (page 2); 23 selections DECODED, every one read
  by `read_binding`. Fenghua, Murata, Arlitech and the CS03 shunt not decoded.
- `apply_decision_decoded.py`: the first draft's second-run guard searched the raw text, where the folded title splits
  the marker, and a scratch copy took the decision twice (59 and 60); the guard now reads the parsed titles, and the
  scratch copy took it once and refused the second run. `apply_identities_c.py`'s guard read the parsed items the same
  way from then on; re-pinned to the new reading; applied once and refused once on a scratch copy.
- The check without the held sheet: 13 UNREAD, 13 problems; with `--unfetched-ok` 0 problems.
- 19:53 commit `ebe2a084`.

## Round 3 (the independent check of `6b03ef6f`: 5 blocking, 12 minor)

- 20:25 read `_scratch/chk-w5identc/CHECK.md` whole. `scan_vendor.py` run once, niced, over every PDF under v2/vendor
  (429 read, 11 without text): the part numbers the table leaves UNRESOLVED and a few named in values.
- B1: `check` derives requirements from the rows; the mutant test. B2: `SCHEMES` in the tool, layouts read from the
  pages, positional slicing, kind and property coverage; the first positional version still accepted Uniroyal's
  packaging and special swapped (each row was only asked to be on the page), so each row is now tied to its own
  position's part of the page; the check's probes as tests; 24 of 24.
- 20:31 checkpoint `c78c70d1`.
- B4 and B5 in the builder (`reread`, every fact asserted); J_MAINSW to UNRESOLVED under rule N-1; C31's new reason class.
- B3: `apply_rebind_decisions_w5identc.py` on the int14 pattern, called by `apply_decision_decoded.py`.
- Minors: decision text, the disposition, Yageo's sources line, `HOLDS_WITH_UNREAD`, `draft_gen_c_c1_c2.py` (check mode
  only), order-code notes per selection.
- 20:39 commit `3f9fe6f6`. Scratch clone of int15 `097d2517`, branch merged clean, the chain run (results in the README), then
  the same on the tip; the clone removed (disk 7.0 GB free after, 20:42).
