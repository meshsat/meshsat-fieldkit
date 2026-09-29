mergeable: no

# AI review: re-check of integration set 13 after the answers, fnd/int14 at bd1cbb07 (MESHSAT-1357)

This is an AI review, not a qualified engineering review. Checked 29 September 2026 from 18:09 to 18:17 CEST (times read
with `date`).

**Set-up**
* The same clone, `<scratch>/chk-int14`, now detached at `bd1cbb0798fd78c2424cd704c991d1595b516809`. This was still the
  tip of `fnd/int14` at 18:16.
* The same archive, `int14-evidence-a906b932.tar`, re-installed after the checkout. `git status` shows only my two
  reports.
* Replay clone `c14/r5` (scratchpad) at a906b932. Every tool ran from a scratch cwd with `VERDICT_DIR` in the
  scratchpad. Nothing committed or pushed.

**Counts: 2 blocking, 3 minor.** Both blocking items are text in `apply_check14_fixes.py`. Everything else holds:
* the replay is byte for byte;
* the new CFL-016 entry's facts;
* CFL-016's FAIL;
* the links from CON-023 and CON-024;
* the edits for minors 4, 5 and 8, and the four carried minors;
* the validators and the pages.

## Blocking items

**R2-B1. S-122's closing condition still does not take the PANEL.md rows, and the new CFL-016 entry says it does.**

*Where:* `v2/ecad/tools/pcb_requirements.yaml`.
* Line 3562 on: S-122's added sentence, `S122_ADD` in `apply_check14_fixes.py`.
* Lines 13894 and 13895: the CFL-016 entry's "waits on S-122, whose closure re-reads the named documents against the
  netlists of the set that carries it; the rows are added to S-122".

*Why:*
* S-122 closes "when every statement of those documents about the EMCON line and the parts it gates is re-derived from
  the committed netlists ...; CFL-016 is then re-read".
* The added sentence comes after that condition. It records the rows as a finding but does not put them into the
  condition. The pin map rows for GPIO 2 to 5 are not EMCON statements.
* So S-122 can close by its own words with PANEL.md lines 89 and 90 unchanged. That is the hazard B1 named. The CFL-016
  entry describes S-122's closure as broader than it is.
* The fact itself is now carried twice, in S-122's title and in CFL-016's evidence. A careful closer would see it, so
  the risk is lower than at B1.

*Fix:* end `S122_ADD` with a closing clause, for example "S-122 closes only when these rows, like the EMCON statements,
are re-derived from the committed netlists". Or reword the CFL-016 entry to say what S-122's condition covers. Then
re-run the script on a906b932.

**R2-B2. S-123 states two things the code does not bear out.** (The item and its links are otherwise right; see
item 3.)

*Where:* `v2/ecad/tools/pcb_requirements.yaml`, S-123's title (from line 3565), `S123` in `apply_check14_fixes.py`.

1. **"tools/return_via.py, tools/ref_change.py and tools/via_audit.py read a board's signal classes from
   tools/boards/<letter>.json".** True of two of the three, not of via_audit.
   * return_via calls `signal_class.classify` at line 153 and `boardtable.value(..., "return_reach_mm")` at lines 406
     to 408.
   * ref_change calls `signal_class.classify` at line 107 and reads boardtable at line 177.
   * via_audit calls only `signal_class.board_letter` (line 100). From the table (`_board_table`, lines 43 to 45) it
     reads `annular_min_mm` and `via_ring_min_mm`. It classifies no net.
   * Set 13 did not change those two values on board C (0.2 and 0.05 mm at main and at the tip), so the reclass does
     not stale via_audit's reading.
   * The error comes from the csi README (section 5, lines 136 to 138: "via_audit, per the check"). My first report's
     m2 repeated it by listing via_audit's re-take as owed, and that part of my m2 was wrong.
2. **"so a class change leaves their readings stale with nothing to flag it".** False as the tree stands.
   * `rules_status._config_state` (lines 1123 to 1130) gives every reading whose writer is not in `CONFIG_INPUTS` the
     cause CONFIG_UNDECLARED, which can never be current.
   * CURRENT-EVIDENCE.md, "Writers whose configuration is not declared yet", lists `ref_change.py` (RET-003),
     `return_via.py` (RET-004) and `via_audit.py` (VIA-001, VIA-002).
   * The real gap is the future one: when these writers are declared, the board table must be among their inputs.

*True in S-123:*
* The readings of the three record only the board. ref_change also records `stitch_cap_mm`, and via_annular the two
  minimum values, never the table file.
* `CONFIG_INPUTS` has no entry for any of the three.
* Set 13 added Q3_G and EMCON_HW_DRV as LOW_SPEED_OR_DC. Q3_G was HIGH_SPEED_DIGITAL through `Q?_G`; EMCON_HW_DRV had
  no class. Set 13 also added the four `EPD_*_R` classes.
* Board C's return_via (21 September, 19:40Z) and via_audit (12:50Z) readings were not re-taken. So was ref_change's
  `return_stitch` (12:50Z), which the item does not name.
* The closing condition is sound.

*Fix:*
* Say that return_via and ref_change read the table's signal classes (and return_reach_mm and the stitch figures), and
  via_audit its annular and via ring minimums.
* Replace "with nothing to flag it" with the state as it is: the three writers are CONFIG_UNDECLARED today, so none of
  their readings can be current, and when they are declared the table must be among their inputs.
* Drop via_audit from the reclass sentence, or say that its inputs did not move in set 13.

## The five questions

**1. The new texts, sentence by sentence.**
* CFL-016's entry:
  * The withdrawal is right.
  * The PANEL.md rows are as quoted (lines 89 and 90 in section 3). The script finds them by their prefix and counts
    two.
  * The pins and values are as quoted. The script asserts U3 pins 4 to 7, R53 to R56 pins 1 and 2 and the four 27R
    values on the committed netlist, and I read the same.
  * Two facts it types without reading are true and are in my first report: the sha c9f7394594201045 and "(GPIO 2 to
    5)".
  * "The rest of that entry stands: the R53 ... is board E's" is true.
  * The closure clause: R2-B1.
* S-122's added sentence is true as a finding (R2-B1 for its place).
* S-123: R2-B2.

**2. CFL-016's FAIL is right.** Its acceptance is that each named document describes the circuit as generated.
PANEL.md lines 89 and 90 do not, besides S-122's EMCON passages. The record reads FAIL, waits on S-122 and binds the
current files.

**3. S-123's links are right; its text is not (R2-B2).**
* By the coverage map (`pcb_rules_coverage.yaml`), the three tools decide RET-003 (ref_change), RET-004 (return_via),
  VIA-001 and VIA-002 (via_audit).
* The registry's only records resting on those rules are CON-023 (VIA-001, VIA-002) and CON-024 (RET-003, RET-004).
  Both are NOT_JUDGED BLOCKERs, and each now waits on S-123 alone.
* The script found them by searching `pcb_rules.yaml`'s text, which hits only RET-003 and VIA-002. It reached the right
  two records, but not by the coverage map (minor n1).

**4. Minors 4, 5 and 8, and the carried ones.**
* **Minor 4:** walkmin README lines 5 to 7 now say what the script answers and what f9bc2f6f edited, and that the
  check's items 3 to 6 are carried.
* **Minor 5:** both docstrings are corrected. The source it names, `records/int13/apply_rebind_after_circuit.py`,
  exists.
* **Minor 8:** three index rows (csi, walkmin, int14), accurate.
* **Carried:** `records/int14/README.md` states m1, m3, m6 and m7 accurately.
  * m1: six parts on A, B and D; blocking 0.
  * m3: "12" and integers.
  * m6: N2 to N5 and N7 with their places.
  * m7: U3's pin 32.
* The filed `checks/check-int14-1.md` equals my CHECK.md apart from the scratch path.

**5. Validators and pages.**
* `apply_check14_fixes.py` replayed on a906b932 gives the committed registry, walkmin README, two docstrings, records
  index and trace page byte for byte. A second run refuses (exit 2).
* The parsed registry diff:
  * CFL-016 gains 1 evidence entry and stays FAIL on S-122;
  * CON-023 and CON-024 gain `waits_on` S-123;
  * S-122's title is extended, its old text kept as a prefix;
  * S-123 is added;
  * closed_items are identical, and nothing else moved.
* **`rules_status.py`, three times:** exit 1 and identical stdout, the same as at a906b932: FAIL of 338 (PASS 195,
  INCONCLUSIVE 104, FAIL 39). Runs 2 and 3 equal the archive's audit. Run 1 differs only in SGN-001's `writers`,
  the self-reference noted before.
* **`rules_render.py`, twice:** clean.
* **Checks:** `--check` reads 16 documents, 0 out of date; `--requirements --check` reads current;
  `decisions_render.py --check` exits 0; `constraints_bound.py` reads PASS.
* **`rules_lib.py`:** 59 rules and `requirements` 144 records, each with 0 errors and 0 warnings.
* **Pages:** against a906b932 only REQUIREMENTS-TRACE.md moves: 86 open items (was 85), "waits on S-123" on CON-023
  and CON-024, CFL-016's entry, S-122's row and S-123's row. CURRENT-EVIDENCE.md, the status pages and
  OWNER-DECISIONS-OPEN.md do not move.
* **The commit:** 9 files, the owner's identity, no trailer, no em or en dash, `git diff --check` clean.

## Minor items

* **n1.** `apply_check14_fixes.py` finds the tools' rules by searching `pcb_rules.yaml`'s text (RET-003 and VIA-002
  only), and its comment names CON-024 by RET-003 alone. The coverage map gives four rules: RET-003, RET-004, VIA-001
  and VIA-002. Fix: read `pcb_rules_coverage.yaml`'s `verification.tool`, and name all four in the comment.
* **n2.** S-123 does not name board C's `return_stitch` reading (ref_change, 21 September) among those not re-taken.
  Name it with the other two.
* **n3.** The csi README section 5 (line 137 and 138) says via_audit reads the new class. It does not (R2-B2). Correct
  it, or note it in `records/int14/README.md`.

## Counts

* **Items:** blocking 2 (R2-B1, R2-B2); minor 3.
* **Replay:** 1 script, 6 generated files byte for byte, second run refused.
* **Registry:** 3 records changed (CFL-016 evidence; CON-023 and CON-024 `waits_on`), 0 results moved; S-122 extended,
  S-123 opened, 0 closed items moved.
* **Validators:** 0 errors, 0 warnings. **Status:** stable three times. **Render:** clean twice. **Pages:** only the
  trace page moved.
* **Readings:** none changed; the same archive.
