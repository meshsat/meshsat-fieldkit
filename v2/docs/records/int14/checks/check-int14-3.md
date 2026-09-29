mergeable: yes

# AI review: third check of integration set 13, fnd/int14 at 32f26b41 (MESHSAT-1357)

This is an AI review, not a qualified engineering review. Checked 29 September 2026 from 18:21 to 18:25 CEST (times read
with `date`).

**Set-up**
* **Tip.** `fnd/int14` is `32f26b41b8fc0035b81126c4c0f26857546a2fe1`, one commit on a906b932, which is its parent.
  bd1cbb07 is not on the branch. It was still the tip at 18:24.
* **Clone.** `<scratch>/chk-int14`, detached at 32f26b41, with `int14-evidence-a906b932.tar` re-installed. `git status`
  shows only my three reports.
* **Replay clone.** `c14/r6` in the scratchpad, at a906b932.
* Tools ran from a scratch cwd with `VERDICT_DIR` in the scratchpad. Nothing committed or pushed.

**Counts: 0 blocking, 1 minor.** R2-B1, R2-B2 and n1 to n3 are answered.

## Blocking items

None.

## 1. Every sentence the script writes

**CFL-016's new entry** (unchanged from bd1cbb07):
* **The withdrawal.** It is right.
* **PANEL.md.** The quoted rows are PANEL.md lines 89 and 90, in section 3.
* **The netlist.** The committed netlist c9f7394594201045 matches the entry: U3 pins 4 to 7 on `EPD_*_R`, R53 to R56
  27R pin 1 on `EPD_*_R` and pin 2 on each line.
* **Board E's R53.** True.
* **FAIL on S-122.** The record still reads FAIL and waits on S-122.
* **The S-122 clause.** "whose closure re-reads the named documents against the netlists ...; the rows are added to
  S-122" is now borne out by S-122's own text (below).
* **The script refuses on changed inputs.** I tested two mutants on the replay clone:
  * PANEL.md's GPIO 2 and 3 row renamed to the `_R` nets: refused, "rows are not as read (1 found)".
  * R55 pin 2 moved in the netlist: refused, "R55 pin 2 is None, not EPD_DC".

**S-122's addition:**
* It keeps the old title as a prefix.
* It gains the finding, which is true.
* It gains the closing clause "S-122 closes only when these rows, like the EMCON statements, are re-derived from the
  committed netlists of the set that carries it". The rows are now part of how S-122 closes (R2-B1 answered).

**S-123, sentence by sentence against the code:**

| Claim | Where I read it | Holds |
|---|---|---|
| return_via and ref_change read a board's signal classes from `boards/<letter>.json` | `return_via.py` 153 and `ref_change.py` 107 call `signal_class.classify`, which calls `declarations(letter)` (`signal_class.py` 110 and 111), reading `boards/<letter>.json`'s `signal_classes` | yes |
| via_audit reads `annular_min_mm` and `via_ring_min_mm` from the same file | `via_audit.py` 43 to 45 and 100 to 103; no `classify` call | yes |
| none of the three records that file | recorded inputs: `board`; ref_change also `stitch_cap_mm`; via_annular also the two values; never the file (`return_via.py` 430, `ref_change.py` 183 and 218, `via_audit.py` 118 to 148) | yes |
| none is in `rules_status.CONFIG_INPUTS`, so their readings never count as current | no entry for any of the three; a writer not declared "cannot be current at all" (`rules_status.py` 711, `_config_state` 1127 to 1130) | yes (the wording of "read CONFIG_UNDECLARED" is m1) |
| set 13 reclassed Q3_G and EMCON_HW_DRV and added the `EPD_*_R` classes | `boards/c.json` main to tip: Q3_G, EMCON_HW_DRV (LOW_SPEED_OR_DC) and four `EPD_*_R` (CLOCKED_DIGITAL) added; nothing removed or changed | yes |
| board C's return_via and return_stitch readings are dated 21 September 2026, not re-taken | 2026-09-21T19:40:34Z and 12:50:14Z, identical to main | yes |
| via_audit reads neither class, and its two values did not change on board C | 0.2 and 0.05 mm at main and at the tip | yes |
| the closing condition | sound, and names the two readings that owe the re-take | yes |

## 2. Replay on a906b932

`apply_check14_fixes.py` from 32f26b41, run once on a clean a906b932 clone, then `rules_render.py --requirements`. It
gives these files byte for byte:
* `pcb_requirements.yaml`;
* `records/README.md` and `csi/README.md`;
* `walkmin/README.md`;
* the two docstrings;
* `REQUIREMENTS-TRACE.md`.

A second run refuses (exit 2). The three hand-written files match the commit: `int14/README.md` and the two filed
checks. Each filed check equals my report apart from the scratch path.

**Registry, parsed a906b932 to 32f26b41:**
* **Records:** CFL-016 gains 1 evidence entry, its old list kept as a prefix, and stays FAIL on S-122. CON-023 and
  CON-024 gain `waits_on` S-123; both stay NOT_JUDGED.
* **Items:** S-122 is extended and S-123 added last in `open_items`. `closed_items` are identical, and nothing else
  moved.
* **The links (n1).** The script now reads the coverage map and asserts RET-003, RET-004, VIA-001 and VIA-002 against
  the three tools. It refuses unless the records resting on those rules are exactly CON-023 and CON-024, which matches
  my own reading of the registry.

## 3. Validators and pages

* **`rules_status.py`, three times:** exit 1, stdout identical to every earlier run: FAIL of 338 (PASS 195,
  INCONCLUSIVE 104, FAIL 39). Runs 2 and 3 equal the archive's audit. Run 1 differs only in SGN-001's `writers`, the
  self-reference noted before.
* **`rules_render.py`, twice:** no output, clone clean.
* **Checks:** `--check` reads 16 documents, 0 out of date; `--requirements --check` reads current;
  `decisions_render.py --check` exits 0; `constraints_bound.py` reads PASS.
* **`rules_lib.py`:** 59 rules, 0 errors, 0 warnings. `requirements`: 144 records, 0 errors, 0 warnings.
* **Pages:** against a906b932 only REQUIREMENTS-TRACE.md moves:
  * the header, 85 to 86 open items;
  * "waits on S-123" on CON-023 and CON-024;
  * CFL-016's entry;
  * S-122's row and the new S-123 row.

  CURRENT-EVIDENCE.md, the status pages and OWNER-DECISIONS-OPEN.md do not move.
* **The commit:** 11 files, the owner's identity, no trailer, no em or en dash in added text, `git diff --check`
  clean.

## 4. Earlier findings

| Finding | Answer | Holds |
|---|---|---|
| B1 (check 1) | clause withdrawn with the rows read and asserted; rows in S-122 with a closing clause | yes |
| m1, m3, m6, m7 (check 1) | carried in `records/int14/README.md`, stated accurately | yes |
| m2 (check 1) | S-123 | yes |
| m4, m5, m8 (check 1) | walkmin README, both docstrings, three index rows | yes |
| R2-B1 | S-122's closing clause | yes |
| R2-B2 | S-123 reworded from the code | yes, with m1 below |
| n1 | the coverage map, asserted | yes |
| n2 | return_stitch named | yes |
| n3 | csi README section 5 corrected: via_audit reads no signal class, only the two ring minimums | yes |

## Minor items

* **m1. S-123: "their readings read CONFIG_UNDECLARED and never count as current".**
  * "Never count as current" is true.
  * Today the rows read TOOL_CHANGED first. Board C's RET-003, RET-004, VIA-001 and VIA-002 rows all carry
    `evidence_cause` TOOL_CHANGED, and a re-take would read LAYOUT_NOT_CURRENT.
  * CONFIG_UNDECLARED applies once those checks pass, as CURRENT-EVIDENCE.md says ("once every earlier check passes").
  * My CHECK-2 put it the same imprecise way.
  * Fix, at the item's next edit: "so none of their readings can count as current (CONFIG_UNDECLARED once the earlier
    checks pass)".

## Counts

* **Items:** blocking 0; minor 1.
* **Replay:** 1 script, 7 files it writes plus the trace page, byte for byte. The second run and 2 input mutants are
  refused.
* **Registry:** 3 records changed (CFL-016 evidence; CON-023 and CON-024 `waits_on`), 0 results moved. S-122 extended
  with its closing clause, S-123 opened, 0 closed items moved.
* **Validators:** 0 errors, 0 warnings. **Status:** stable three times. **Render:** clean twice. **Pages:** only the
  trace page moved.
* **Readings:** none changed; the same archive.
