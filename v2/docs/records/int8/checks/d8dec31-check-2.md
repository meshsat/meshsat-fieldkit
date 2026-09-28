mergeable: yes
B1 closed: yes

Second fresh check of stream d8dec31 at 9057e668 (AI review, checker chk-d8dec31-2, 28 September 2026 19:54 to
20:15 CEST). Not a qualified engineering review; nothing of the kit has been built, ordered or measured. The worktree
`/home/claude-runner/worktrees/meshsat-fieldkit/d8dec31` was read only and is untouched; everything I wrote is under
`/home/claude-runner/worktrees/meshsat-fieldkit/_scratch/chk-d8dec31-2/` (`CHECK.md` is the working record).

**mergeable: yes** for the files (tool, tests, reviewed set, review page, records, two PDFs). **B1 closed: yes** at the
tool: the counter-example now reads INCONCLUSIVE by name. **Two of the apply scripts do not work on the tree they
are for** (B2, B3 below): neither blocks the merge, both block their step of the integrator's order.

**blocking (the apply order, not the merge):**
- id: B2. item: apply order step 3 (M5). problem: `apply_registry_d31.py` stage 1 ASSERTS on fnd/int8's registry and
  writes nothing. file: `v2/docs/records/d8dec31/apply_registry_d31.py` line 234, `t = old.replace(head,
  block.rstrip("\n") + "\n" + head)` with `head = "\nclosed_items:\n"`: the block is put before the newline that ends
  the last open item's line. On int8 S-97's folded title runs to line 3255 and `closed_items:` is line 3256 with no
  blank line between, so `  - id: S-98` is glued onto the title's last line, S-98 folds into S-97's title and the
  parse gives 80 items for 81. On main a blank line precedes `closed_items:`, which is why the rehearsal passed (S-95
  to S-108). counter_example: `python3 apply_registry_d31.py <clone at int8 + d8dec31> --check` prints
  `AssertionError: S-98` (`seq.log` step 3). fix, verified on a pristine copy of int8's registry: `t =
  old.replace(head, "\n" + block.rstrip("\n") + "\n" + head.lstrip("\n"))` gives `apply_registry_d31: 14 open items,
  S-98 to S-111, each linked from its record(s)`, `rules_lib: 144 requirement record(s), 0 error(s), 0 warning(s)`,
  second run refused, `ids-registry.json` under the root (top before S-97); the fixed copy is
  `_scratch/chk-d8dec31-2/apply_registry_d31_fixed.py`.
- id: B3. item: apply order step 5 (S-88's closure). problem: stage 2 reads only
  `<root>/v2/ecad/out/port_protect_a.verdict.json` (line 564). The tree's reading of TRN-001 on board A lives in the
  phase directory, `v2/ecad/pcb-a-power-a23/out/port_protect_a.verdict.json` (and `routed/`): `rules_status.py` line
  79 looks there first (`_phase_dir(letter)/out`, then `routed`, then `ECAD/out`), `_bin/box_retake.sh` line 35
  writes there (`VERDICT_DIR=$P/out`), and `v2/ecad/out/port_protect_a.verdict.json` is ABSENT from main's checkout
  (the phase reading there: PASS of 26, writer 2d69facd, the old tool). So after a real re-take the stage refuses "is
  not in the tree", and the only way to satisfy it is to copy the file to a path nothing else reads, which a closure
  gate should not invite; the `closing_evidence` text names that path too. counter_example: `seq.log` step 9a on a tree
  whose reading sits beside the netlist the stage itself resolves with `PA.netlist("a")`. fix: resolve the reading as
  the netlist is resolved (`os.path.join(os.path.dirname(PA.netlist("a")), "port_protect_a.verdict.json")`, with
  `routed/` and `ECAD/out` in rules_status's order) and name the path found in the evidence. Everything else in the
  stage is right: the five refusals (no reading; netlist sha; tool sha; an INCONCLUSIVE reading; a commit not in this
  checkout's history), the closure, the second run refused, validator 0 errors after (80 open, 61 closed).

**minor:**
- N1 (2d, d1): the reviewed set edited to match a reclassification WITHOUT a `changes` entry or reason (J_USBW
  deleted from board A's `external`, J_USBW moved to `internal_ports`) reads `PASS of 38`, "0 change(s) recorded":
  the tool enforces the shape of a change only when one is written. What stands behind a two-file edit is the file's
  sha in every reading's inputs (staleness) and the test `t_the_committed_reviewed_sets_are_explicit_and_rest_on_a_
  review_in_the_tree`, which pins COUNTS only (18/22, 4/8, 3/5). `port_protect.py` docstring, the README and review
  section 10 say the set is changed "with its reason and the review it rests on", which is more than is enforced.
  fix: pin the per-board external map (or its sha) in that test, and/or have `reconcile` read the review document's
  connector tables (the EXTERNAL rows with their pins), so the set cannot drift from the review the holds pin; say
  in the three texts what is enforced. (The set edited with the table as is reads INCONCLUSIVE NOT REVIEWED; a review
  file that does not exist, a duplicate connector key, a fabricated change, the file absent, a short `why`: all refuse.)
- N2 (2d, d3): J_USBW listed TWICE in `external_ports` reads `PASS of 46, ports 19` (was 42, 18): the denominator and
  the ports count inflate in silence; the existing refusal covers a pin in both lists, not a ref twice in one.
  fix: `cover()` refuses a ref that appears twice in either list.
- N3 (2d, d3c): `reviews()` uses `json.load`, which keeps the last of duplicate keys in silence (a pin or a connector
  listed twice inside the set). fix: `object_pairs_hook` that refuses a duplicate key.
- N4 (2d, d2b): a record's `review` may name any existing file (`README.md` passed); existence is the only check.
- N5 (item 5): the tests do not clean up: 46 `mkdtemp`, 0 `rmtree`; one run left 45 `/tmp/port-*` directories (0
  before; removed). fix: `shutil.rmtree(d, ignore_errors=True)` in each test's `finally`, or one module-level
  `tempfile.TemporaryDirectory` that `run.py` closes.
- N6 (M10): `make_pin_tables.py` line 47 passes board A's table through `D.a_external(...)` unconditionally, so it
  runs only on the COMMITTED shape of a.json; on the corrected table (after step 1) it asserts in `a_external`
  (`AssertionError: [the 18 refs]`) before the by-pin stop. The by-pin stop itself is right (on the committed shape
  with J_USBW `pins: ["1"]`: `AssertionError: board A: J_USBW.2 carries USB_WALL_N and no entry covers it`; untouched
  it reproduces `readings/pin-tables.md`). fix: take the table as is when its refs are already the 18, as
  `make_port_reviews.py` does.
- N7 (note): with the reviews file absent, a declared zero with its reason (board P) reads INCONCLUSIVE of 3 where it
  read PASS: stricter, not silent, but item T-2 and the README do not say the file's absence now blocks every board.

**M1 to M10:** M1 yes (pdftotext page 5: 6.1 ANODE to GND -65 to 65 V, CATHODE to ANODE -5 to 75 V; 6.2 HBM +-2000;
page 4 is the pin table; the ledger row reads 5). M2 yes: 13 rows read "protection claimed off this board, not judged
here" in `readings/pin-tables.md` and the review (J_BM1 to J_BM11, J_ANT, J_PAOUT), J_MAINSW reads "protected off this
board (read on board C's netlist)"; 12 of 18 is right, the corrected A declaration carries 12 off_board entries
(J_MAINSW and J_BM1 to J_BM11, counted from the applied a.json), the first check's 11 left out J_MAINSW; section 10
states TRN-001's PASS of 42 believes those 12 on their text, 6 entries on 10 pins judged. M3 yes (E-F3 "BOUND, a
conservative model's answer", a BOUND legend row, section 2 split 3 plus 1, the registry item says "by a conservative
bound and not a demonstrated defect"). M4 yes (five parts named in table, item and docstring; SDA1 on E re-read: D9,
J_LTG.3, J_POD.3, R36, U10, U14, U15, U17). M5 in part (mapping printed, `ids-registry.json` under the root, the
closure a separate refusing stage; B2 and B3). M6 yes (`apply_interfaces_mainsw.py` refuses: "board A's netlist has
J_MAINSW.1 on MAIN_PB, not MAIN_PB_LEAD", rc 1; `--force-netlist --check` rc 0; the a_mainpb docstring names it; the
`src` line stays 278 with a note). M7 yes (C382212 is C207's, gen_sch_a.py 665, 729, 800; C6 and C7 carry none,
gen_sch_e.py 399; the item and README agree). M8 yes (the review's new paragraph and the README name H3-02, erratum f,
S-88 and the H3 review; both H3 files exist in the merged tree, RELEASE-H3.md line 114 carries erratum f). M9 yes
(`apply_sources_d31.py` rc 0 after checking both shas, 2 entries, second run refused; parts entries said owed). M10
yes (above, with N6).

**The apply order** (README's six steps), rehearsed on the merged clone with a status snapshot after each: step 1
edits `boards/a.json`, `d.json`, `e.json` (old text asserted, second run "already declares internal_ports"),
`make_port_reviews.py --check` reads "exactly what this script would write"; step 2 edits `rules_status.py` (shared;
OLD asserted once, the json required in the tree, the patched module imported from a copy, second run refused); step
3 edits `pcb_requirements.yaml` (shared) and writes `records/d8dec31/ids-registry.json`, FAILS as committed (B2), works
with the fix; step 4 edits `v2/vendor/SOURCES.yaml` (shas checked, marker) and `pcb_board_holds.yaml` (shared; pins
the review as `094817023210d1b0`, the review at 9057e668, read at apply time; second run "found 0"); step 5 is the
box's then the closure (B3); step 6 the four circuit scripts (not re-run by me; the diff since f8e61f05 changes the
docstrings of a_mainpb and e_cin only) then `apply_interfaces_mainsw.py`, which refuses until the netlist moves.

**The merge result:** one conflict, `v2/vendor/sources.txt`, mechanical: both sides appended after the same line 348
(int8 12 lines, w5tray's materials and QMX sheets and the MIL-STD-810H transcription; d8dec31 2 lines, the Infineon
and TI sheets); resolved in the clone as base plus both blocks (362 lines, 0 markers). 58 files auto-merged
otherwise; the stream touches neither the registry nor the trace page nor `vendor-status.txt`, so those conflicts do
not arise. Merge base of int8 and d8dec31: `73ae2f21`.

**What I ran, exact last lines:**
- `env -C <clone>/v2/ecad/tools python3 tests/run.py port_protect`: `tests: 61 passed, 0 failed, 0 skipped`.
- `repro.py` on tree2 (corrected tables, VERDICT_DIR in scratch): baselines `PASS of 42` (22 reviewed, 22 declared),
  `PASS of 21` (8, 8), `PASS of 13` (5, 5); B1 `INCONCLUSIVE of 38 ... disagreements 3` with `RECLASSIFIED J_USBW.1
  on VBUS_WALL`, `.2`, `.3`; J_USBW on pin 4 `FAIL of 42` (`FAIL DECLARATION J_USBW.4 is on GND`); J_USBW removed
  `INCONCLUSIVE of 38` (UNCOVERED and REVIEWED named); section 2f: the set EQUAL to the corrected declarations' live
  external pins on A, D and E, computed with port_protect's own reader.
- `regress_reclassify.py tree2`: `regress_reclassify: 0 case(s) failed` (21 ok lines).
- `apply_registry_d31.py tree2 --check` on int8's registry: `AssertionError: S-98`; the fixed copy: `apply_registry_d31:
  14 open items, S-98 to S-111, each linked from its record(s)`; `rules_lib: 144 requirement record(s), 0 error(s), 0
  warning(s)`.
- `--close-s88`: five `REFUSED` lines, then `apply_registry_d31: S-88 closed by commit 9057e668 on the re-taken
  reading (PASS of 42, netlist 0a2b59087bcc2678, tool 7acd5333fc59f8d0); waits_on dropped from REQ-015, REQ-017,
  REQ-029, CON-018`; second run `S-88 is already closed`; validator `0 error(s), 0 warning(s)`.
- `make_pin_tables.py` on the committed shape with J_USBW pins ["1"]: `AssertionError: board A: J_USBW.2 carries
  USB_WALL_N and no entry covers it`.
- `pdftotext -f 5 -l 5 -layout v2/vendor/ti/ti-lm74700-q1.pdf`: the 6.1 and 6.2 lines above.
- 22 files in the diff stat as claimed; 0 em or en dashes in added lines; "AI review" in the review's title and first
  paragraph and in the README; "Nothing of this kit has been built, ordered or measured" at review lines 4 to 5; no
  protection lowered (the circuit scripts add parts only); every number the author claims that I re-ran came out the
  same (61 tests, 21 cases, 0 errors on the rehearsal, which was on MAIN plus the branch and so could not see B2).

**Not checked and why:** no generator, KiCad, full suite or box re-take (the rules); the four circuit apply scripts
not re-run (docstring-only diffs, the first check ran them on copies); the author's neighbouring test files not
re-run; the ledger's other 43 page citations not re-opened (the first check did); the set's `netlist_sha256_16` as
a note after a circuit change not exercised; the review's prose outside the diff hunks not re-read.

Scratch: `_scratch/chk-d8dec31-2/` holds `CHECK.md`, `RESULT.md`, `seq.log`, `repro.py`, `repro2.py`, `seq.sh`,
`apply_registry_d31_fixed.py`, `int8-registry.yaml`, `sources.merged.txt`, `chk-verdicts/` (the scratch readings);
the two scratch clones were removed; `/tmp/port-*` is empty; the d8dec31 worktree is clean.
