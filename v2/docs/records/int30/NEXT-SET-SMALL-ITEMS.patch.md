**DONE:** the next set's small items (Q-19, Q-21, Q-27 with W8's, W11's and W14's left-outs, REVIEW-2B findings 4 to 7, the L4-E9 `[OWN:n]` citations after part 26, W15's and W13's left-outs) written as 24 exact rows W20-01 to W20-24 and three NEEDS THE COORDINATOR items W20-N1 to W20-N3 (six old texts), every Old text read once at the integration's `c4492dd3`; four items answered with no row and the reason. **NOT DONE:** nothing applied: every file named is the integration's or another record's. **NEXT:** the next set's coordinator applies section 3 in the order of section 5, decides section 4, and regenerates as section 5 says.

# The next set's small items: exact patch rows for the coordinator (W20, MESHSAT-1357, 6 October 2026)

**What this is.** One file of exact text corrections for the next set's coordinator, written by worker W20 on branch `fnd/w20oneliners` from `fnd/w15class` `57bcdbfce095c461b4c3b6804ea8cc3508762577`. The rows are read against the integration, `fnd/p0pwr` at `c4492dd370c592e9899a8e526113958f4dc20554` (2b `d83d9f2d` with the l6r2 correction `33efca07` and W19's merge), through `git show` only; no file a row names is edited here. Each row: the file, the line or lines at `c4492dd3`, the kind (a fragment of the named line, one whole line, or consecutive lines), what it pairs with, the source the new words are copied from, the class (PRESENTATION OR BINDING, CLAIM CHANGE with its reason, TEST, or BINDING), the Old text exactly as it stands (once in the file) and the New text. A row that needs a judgement this author cannot source is in section 4 as NEEDS THE COORDINATOR with both candidates. The rows design nothing, compute no figure, change no verdict and close nothing. Prototype framing: nothing in the kit is built, bought, powered or measured; every figure quoted is a record's desk figure as that record labels it.

**Inputs read** (the coordinator's INBOX for W20): `_runs/int30/QUEUE.md` rows Q-19, Q-21, Q-27 and the dated completion lines of W8 (03:59), W11 (04:19), W13 (04:40), W14 (04:36) and W15 (04:42), with the coordinator's 04:38 to 04:43 entry (the `[OWN:n]` item and W15's line 975); `_runs/int30/REVIEW-2B.md` findings 4 to 7; W7's row format (`fnd/w7rem` `3e566c55`, `v2/docs/records/l4e9/L4E9-4588-PATCH.md`); W13's left-outs (`fnd/w13l4e9` `56ab0d01`, `v2/docs/records/l4e9/L4E9-W5-PATCH.md` section 7); W11's left-outs (`fnd/w11l9t5` `85b6f258`, `v2/docs/records/l9t5/README.md` lines 461 to 466); W12's draft 2 section 10 (`fnd/dgate2` `150e908b`, `v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.draft2.md` lines 552 to 567: its left-outs are its own draft's and none is a row here).

## 1. Rows per file

| File | Rows | NEEDS THE COORDINATOR | Forces a regeneration when applied |
|---|---|---|---|
| `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md` | 7 (W20-01, W20-03, W20-04, W20-05, W20-06, W20-07, W20-08) | 1 (W20-N2c) | yes: a pinned page (12 files print or pin its digest) |
| `v2/docs/records/l4e9/l4e9_power_path.py` | 5 (W20-02, W20-09, W20-10, W20-11, W20-12) | 1 (W20-N2b) | yes: the generator (its output; l6r2_passives.out and l9t5_connected.out print its digest) |
| `v2/docs/records/l4close/REMAINING-ENGINEERING.md` | 2 (W20-13, W20-14) | 0 | no (no output pins it; test_remeng reads it) |
| `v2/docs/records/l9t5/l9t5_connected.py` | 2 (W20-15, W20-16) | 0 | yes: the generator (its output; l8r2_dist.out pins it) |
| `v2/docs/records/l9t5/apply_l4e9_changelist_p0.py` | 1 (W20-17) | 0 | yes: a pinned script (l9t5_connected.out pins it) |
| `v2/ecad/tools/tests/test_l5pwr.py` | 1 (W20-18) | 0 | no (a test) |
| `v2/ecad/tools/tests/test_l9t5.py` | 3 (W20-19, W20-20, W20-21) | 0 | no (a test) |
| `v2/ecad/tools/tests/test_remeng.py` | 1 (W20-22) | 2 (W20-N3a, W20-N3b) | no (a test) |
| `v2/ecad/tools/pcb_interfaces.yaml` | 1 (W20-23) | 0 | yes: a pinned file (10 files print or pin its digest) |
| `v2/docs/HW-FW-CONTRACT.md` | 1 (W20-24) | 0 | yes: a pinned file (8 files print or pin its digest) |
| `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md` | 0 (none) | 2 (W20-N1a, W20-N2a) | yes: a pinned page (4 files print its digest) |
| **Total** | **24** | **6 old texts in 3 items** | |

## 2. How to apply

Each Old text occurs exactly once in its file at `c4492dd3` (the module `v2/ecad/tools/tests/test_w20oneliners.py` reads every one there through git, and at the tip of the branch a row waits for wherever that branch rewrites the file). A row marked "after" a branch is applied once that branch is merged (where the branch leaves the file alone, the merge keeps the integration's text). Pairs are applied in the same commit (the page's generated blocks are tested equal to the generator's data). Kinds: "fragment" replaces the Old text inside the named line; "line" and "lines" replace whole lines; New texts keep the file's indentation as written in the block.

## 3. The rows

### W20-01. Q-19: section 4e's guard-on row (the page)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 621
- Kind: fragment
- After: none
- Pairs with: W20-02
- Source: the page's own 8a, line 1045: "Since P0-7, B6-ENG-2 is answered at the desk and B6-ENG-1 becomes E-1, the port's remaining engineering ([P0SOL:157])"; the D-10 row of section 6, line 839: "the receiving company's remaining engineering item E-1"; the ledger's HO-F heading (`REMAINING-ENGINEERING.md:499`, "D-10 / E-1"); the words "set 29's B6-ENG-1 as P0-7 restates it" are W8's (`HW-FW-CONTRACT.md:261` at `fnd/w14l5` 910f08ef); W1's finding (`fnd/w1l5pwr` 6ab17e21, `v2/docs/records/l5pwr/L5-POWER-CONTRACTS.md:150`)
- Class: PRESENTATION OR BINDING (the current identifier the page's own 8a gives; the row's OPEN and its figures unchanged)
- Regeneration: pinned page (section 1's count)
- Old:

```text
the stage question is the engineer's (B6-ENG-1; R-176 row 3)
```

- New:

```text
the stage question is the receiving company's E-1 (set 29's B6-ENG-1 as P0-7 restates it, 8a; R-176 row 3)
```

### W20-02. Q-19: the generator's 4e row (cons of section 4's fault table)

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 6831
- Kind: fragment
- After: none
- Pairs with: W20-01
- Source: the page's own 8a, line 1045: "Since P0-7, B6-ENG-2 is answered at the desk and B6-ENG-1 becomes E-1, the port's remaining engineering ([P0SOL:157])"; the D-10 row of section 6, line 839: "the receiving company's remaining engineering item E-1"; the ledger's HO-F heading (`REMAINING-ENGINEERING.md:499`, "D-10 / E-1"); the words "set 29's B6-ENG-1 as P0-7 restates it" are W8's (`HW-FW-CONTRACT.md:261` at `fnd/w14l5` 910f08ef); W1's finding (`fnd/w1l5pwr` 6ab17e21, `v2/docs/records/l5pwr/L5-POWER-CONTRACTS.md:150`); the output's line 1562 prints the same cell
- Class: PRESENTATION OR BINDING (data of W20-01)
- Regeneration: generator (output line 1562)
- Old:

```text
the stage question is the engineer's (B6-ENG-1; R-176 row 3)
```

- New:

```text
the stage question is the receiving company's E-1 (set 29's B6-ENG-1 as P0-7 restates it, 8a; R-176 row 3)
```

### W20-03. item 5: [OWN:476] in the page (hand text (section 8's head))

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 965
- Kind: fragment
- After: none
- Pairs with: none
- Source: `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:477` at `c4492dd3` reads "Keep sequential layer-by-layer DESK acceptance."; the file's line 476 before part 26 (`git diff 0d5f855e b0a67a45`: one table row inserted, `@@ -23,6 +23,7 @@`, the new line 26)
- Class: PRESENTATION OR BINDING (a line-number move; the quoted words unchanged)
- Regeneration: pinned page (section 1's count)
- Old:

```text
[OWN:476]
```

- New:

```text
[OWN:477]
```

### W20-04. item 5: [OWN:788] in the page (hand text (section 8's head))

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 965
- Kind: fragment
- After: none
- Pairs with: none
- Source: `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:789` at `c4492dd3` reads "The Layer 4 desk-handover gate can then be assessed against the agreed supplier-takeover scope. It must not claim technical closure of open defects."; the file's line 788 before part 26 (`git diff 0d5f855e b0a67a45`: one table row inserted, `@@ -23,6 +23,7 @@`, the new line 26)
- Class: PRESENTATION OR BINDING (a line-number move; the quoted words unchanged)
- Regeneration: pinned page (section 1's count)
- Old:

```text
[OWN:788]
```

- New:

```text
[OWN:789]
```

### W20-05. item 5: [OWN:784] in the page (gen:check2 block)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 1288
- Kind: fragment
- After: none
- Pairs with: W20-09
- Source: `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:785` at `c4492dd3` reads "Stopping an unsuccessful method after cx46 is reasonable."; the file's line 784 before part 26 (`git diff 0d5f855e b0a67a45`: one table row inserted, `@@ -23,6 +23,7 @@`, the new line 26)
- Class: PRESENTATION OR BINDING (a line-number move; the quoted words unchanged)
- Regeneration: pinned page (section 1's count)
- Old:

```text
[OWN:784]
```

- New:

```text
[OWN:785]
```

### W20-06. item 5: [OWN:850] in the page (gen:check2 block)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 1288
- Kind: fragment
- After: none
- Pairs with: W20-10
- Source: `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:851` at `c4492dd3` reads "A review limit stops an unsuccessful method; it does not make an unresolved defect disappear."; the file's line 850 before part 26 (`git diff 0d5f855e b0a67a45`: one table row inserted, `@@ -23,6 +23,7 @@`, the new line 26)
- Class: PRESENTATION OR BINDING (a line-number move; the quoted words unchanged)
- Regeneration: pinned page (section 1's count)
- Old:

```text
[OWN:850]
```

- New:

```text
[OWN:851]
```

### W20-07. item 5: [OWN:786] in the page (gen:classes block)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 1332
- Kind: fragment
- After: none
- Pairs with: W20-11
- Source: `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:787` at `c4492dd3` reads "Qualification-only items remain separately identified."; the file's line 786 before part 26 (`git diff 0d5f855e b0a67a45`: one table row inserted, `@@ -23,6 +23,7 @@`, the new line 26)
- Class: PRESENTATION OR BINDING (a line-number move; the quoted words unchanged)
- Regeneration: pinned page (section 1's count)
- Old:

```text
[OWN:786]
```

- New:

```text
[OWN:787]
```

### W20-08. item 5: [OWN:730] in the page (gen:supplier block)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 1409
- Kind: fragment
- After: none
- Pairs with: W20-12
- Source: `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:731` at `c4492dd3` reads "Physical work belongs to the receiving supplier."; the file's line 730 before part 26 (`git diff 0d5f855e b0a67a45`: one table row inserted, `@@ -23,6 +23,7 @@`, the new line 26)
- Class: PRESENTATION OR BINDING (a line-number move; the quoted words unchanged)
- Regeneration: pinned page (section 1's count)
- Old:

```text
[OWN:730]
```

- New:

```text
[OWN:731]
```

### W20-09. item 5: [OWN:784] in the generator (the check2 block's data)

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 5142
- Kind: fragment
- After: none
- Pairs with: W20-05
- Source: `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:785` at `c4492dd3` reads "Stopping an unsuccessful method after cx46 is reasonable."; the file's line 784 before part 26 (`git diff 0d5f855e b0a67a45`: one table row inserted, `@@ -23,6 +23,7 @@`, the new line 26)
- Class: PRESENTATION OR BINDING (a line-number move; the quoted words unchanged)
- Regeneration: generator (renders the page's block; the output prints no [OWN:n])
- Old:

```text
[OWN:784]
```

- New:

```text
[OWN:785]
```

### W20-10. item 5: [OWN:850] in the generator (the check2 block's data)

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 5142
- Kind: fragment
- After: none
- Pairs with: W20-06
- Source: `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:851` at `c4492dd3` reads "A review limit stops an unsuccessful method; it does not make an unresolved defect disappear."; the file's line 850 before part 26 (`git diff 0d5f855e b0a67a45`: one table row inserted, `@@ -23,6 +23,7 @@`, the new line 26)
- Class: PRESENTATION OR BINDING (a line-number move; the quoted words unchanged)
- Regeneration: generator (renders the page's block; the output prints no [OWN:n])
- Old:

```text
[OWN:850]
```

- New:

```text
[OWN:851]
```

### W20-11. item 5: [OWN:786] in the generator (the classes block's data)

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 5146
- Kind: fragment
- After: none
- Pairs with: W20-07
- Source: `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:787` at `c4492dd3` reads "Qualification-only items remain separately identified."; the file's line 786 before part 26 (`git diff 0d5f855e b0a67a45`: one table row inserted, `@@ -23,6 +23,7 @@`, the new line 26)
- Class: PRESENTATION OR BINDING (a line-number move; the quoted words unchanged)
- Regeneration: generator (renders the page's block; the output prints no [OWN:n])
- Old:

```text
[OWN:786]
```

- New:

```text
[OWN:787]
```

### W20-12. item 5: [OWN:730] in the generator (the supplier block's data)

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 5150
- Kind: fragment
- After: none
- Pairs with: W20-08
- Source: `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:731` at `c4492dd3` reads "Physical work belongs to the receiving supplier."; the file's line 730 before part 26 (`git diff 0d5f855e b0a67a45`: one table row inserted, `@@ -23,6 +23,7 @@`, the new line 26)
- Class: PRESENTATION OR BINDING (a line-number move; the quoted words unchanged)
- Regeneration: generator (renders the page's block; the output prints no [OWN:n])
- Old:

```text
[OWN:730]
```

- New:

```text
[OWN:731]
```

### W20-13. Q-21: HO-F's "changes no record's text"

- File: `v2/docs/records/l4close/REMAINING-ENGINEERING.md`
- Line: 532
- Kind: fragment
- After: fnd/w4l4e7 (786aed2f) merged
- Pairs with: W20-14
- Source: `fnd/w4l4e7` at 786aed2f, `v2/docs/records/l4e7/L4E7-P0SOL.md` lines 141 to 149 (section 4 (a): "**E-1 also carries one OPEN case that is not a failing case: the lower-source back-feed**" ... "It is REMAINING ENGINEERING inside E-1", lines 144 to 145); the queue's Q-21 row; W4's subject line (786aed2f: "the lower-source back-feed REMAINING ENGINEERING inside E-1 with S1 row (b) its later validation")
- Class: PRESENTATION OR BINDING (a dated note; the ledger's reading and classes unchanged)
- Regeneration: no pin (test_remeng only)
- Old:

```text
sets no new limit and changes no record's text.
```

- New:

```text
sets no new limit and, as written, changes no record's text (6 October 2026: once `fnd/w4l4e7` at `786aed2f` is adopted, record l4e7's own page places the back-feed the same way, "It is REMAINING ENGINEERING inside E-1" ([P0SOL:144-145] at `786aed2f`)).
```

### W20-14. Q-21: section 6, item E's contradiction left to the next set

- File: `v2/docs/records/l4close/REMAINING-ENGINEERING.md`
- Line: 726 to 727
- Kind: lines
- After: fnd/w4l4e7 (786aed2f) merged
- Pairs with: W20-13
- Source: as W20-13
- Class: PRESENTATION OR BINDING (a dated note; item E's reading unchanged)
- Regeneration: no pin (test_remeng only)
- Old:

```text
it is not this ledger's file, and the contradiction between that text and this reading is the
  coordinator's to carry to the next set.
```

- New:

```text
it is not this ledger's file, and the contradiction between that text and this reading is the
  coordinator's to carry to the next set. (6 October 2026: once `fnd/w4l4e7` at `786aed2f` is adopted, record l4e7's L4E7-P0SOL.md
  section 4 (a) carries this reading ([P0SOL:141-149] at `786aed2f`), which answers the contradiction on record l4e7's side.)
```

### W20-15. W11's line 518 and REVIEW-2B finding 7: section 2's head

- File: `v2/docs/records/l9t5/l9t5_connected.py`
- Line: 517 to 518
- Kind: lines
- After: none (fnd/w11l9t5 85b6f258 leaves these two lines as they are)
- Pairs with: none
- Source: 7070f106's subject ("the L4-E9 change-list rows R-220 to R-245 applied by records/l9t5/apply_l4e9_changelist_p0.py (117 changes; no R-241: B2 out of the baseline)"); W11-01's words (`fnd/w11l9t5` 85b6f258, `v2/docs/records/l9t5/README.md:451` table, "APPLIED since, by the integrator, at 7070f106 ... the draft's applied state and its `--check`"); REVIEW-2B section 1 (iii) ("CHANGE_ORDER in l4e9_power_path.py has 117 entries at 7070f106 and 118 at 6bc4424e and d83d9f2d") and its finding 7; W11's left-out (README.md:461 to 463 at 85b6f258)
- Class: PRESENTATION OR BINDING (the list's provenance restated; the count is computed, not typed; the same two lines)
- Regeneration: generator (output lines 60 to 62; l8r2_dist.out pins this file)
- Old:

```text
        w("   script with this record's text draft apply_l4e9_changelist_p0.py applied in memory (V6-m11: rows R-220 to R-245 for the drafts")
        w("   that had none; the tree's files unchanged until the integrator applies it with the re-takes the draft names): %d changes, every" % n_ch)
```

- New:

```text
        w("   script, which carry this record's text draft apply_l4e9_changelist_p0.py (V6-m11: rows R-220 to R-245 for the drafts that had none)")
        w("   as the integrator applied it at 7070f106, read from the tree (the draft's applied state), set 31's R-246 with them: %d changes, every" % n_ch)
```

### W20-16. W11's line 843: the rev Y row

- File: `v2/docs/records/l9t5/l9t5_connected.py`
- Line: 843
- Kind: fragment
- After: none (W11 changed lines 1002 to 1004 and 1013 to 1014 only)
- Pairs with: none
- Source: `l9t5_t10.out` lines 645 to 647 at `c4492dd3` ("revision X is HELD with no admission route (round 5's V-B20 route ... SUPERSEDED)"); W11-04's new text for the same words at lines 1002 to 1004 (`fnd/w11l9t5` 85b6f258, README.md:451); K-26; W11's left-out (README.md:463)
- Class: CLAIM CHANGE (narrows: no admission route, as T10 states it; the count and the C figures unchanged)
- Regeneration: generator (output line 216)
- Old:

```text
rev X stays on V-B20
```

- New:

```text
revision X stays HELD with no admission route (round 5's V-B20 route SUPERSEDED, 10j (f))
```

### W20-17. W11's lines 28 to 29 (at 53a68c7c; the same words stand lower here): the applier's docstring

- File: `v2/docs/records/l9t5/apply_l4e9_changelist_p0.py`
- Line: 31
- Kind: fragment
- After: none
- Pairs with: none
- Source: W11-02's words (`fnd/w11l9t5` 85b6f258, README.md:451 table: "L4-E9's generator re-pinned at bbba3e53 and its output regenerated in set 31 with its four cascade pins at commit 2b's digests"); REVIEW-2B section 2 (the four pins of l4e9_power_path.py at d83d9f2d, each equal to the committed file's sha256); W11's left-out (README.md:465)
- Class: PRESENTATION OR BINDING (the docstring's history; no code changed)
- Regeneration: pinned script (l9t5_connected.out pins this file's sha256)
- Old:

```text
output once its L4-E11 pin is re-taken (it refuses on this tree since the P0 base).
```

- New:

```text
output once its L4-E11 pin is re-taken (it refused on the tree from the P0 base until set 31: the generator re-pinned at bbba3e53,
its four cascade pins at commit 2b, d83d9f2d).
```

### W20-18. W14's left-out: test_l5pwr's module docstring

- File: `v2/ecad/tools/tests/test_l5pwr.py`
- Line: 18
- Kind: line
- After: fnd/w14l5 (910f08ef) merged
- Pairs with: none
- Source: W14's comment block at `fnd/w14l5` 910f08ef, `v2/ecad/tools/tests/test_l5pwr.py` lines 320 to 335 ("W8_ROW = \"| 2 (W8, L5-F14) |\"", "W8_RESTATED = (\"L5-F09 a\", \"L5-F09 b\", \"L5-F09 c\", \"L5-F09 d\", \"F11-09\")", "three properties in its place", "apply_l5f11's refusal is right but its ORDER reason is not (decision (b)): test_w14l5.py carries the proposed correction PATCH_L5F11_ORDER"); the queue's W14 completion line (04:36)
- Class: PRESENTATION OR BINDING (a docstring; no predicate changed)
- Regeneration: none (a test docstring)
- Old:

```text
were applied ("already applied"; their Layer 4 reads pinned at a49a2b13 since W1), each script applies once to the files it was
```

- New:

```text
were applied ("already applied"; their Layer 4 reads pinned at a49a2b13 since W1) on every text W8 did not restate, and on the five
W8 restated (L5-F09 a to d, F11-09; its change record row "| 2 (W8, L5-F14) |") three properties in their place (W14, 6 October
2026: on that tree the first script refuses by its docstring's rule and the second at its ORDER check, whose proposed correction is
test_w14l5.PATCH_L5F11_ORDER), each script applies once to the files it was
```

### W20-19. REVIEW-2B finding 4: test_l9t5's seven rows by prefix

- File: `v2/ecad/tools/tests/test_l9t5.py`
- Line: 1079 to 1081
- Kind: lines
- After: none
- Pairs with: none
- Source: REVIEW-2B finding 4 and section 4; the register at `c4492dd3`, lines 321, 323, 328, 334, 337, 339 and 340 (column 9 of R-225, R-227, R-232, R-238, R-242, R-244, R-245: "item RE-4", "item RE-2", "item RE-4", "item RE-2", "item RE-7", "item RE-10", "items RE-5, RE-6, RE-7"); `SET31-CHANGES.md:48` (row 17: "ASSIGNED to the ledger's RE-2, RE-4, RE-5 to RE-7 and RE-10"); the generator's RE_ROWS, line 5475
- Class: TEST (a predicate restored: the RE item per row; nothing weakened)
- Regeneration: none (a test)
- Old:

```text
            if r[0] in ("R-225", "R-227", "R-232", "R-238", "R-242", "R-244", "R-245"):
                assert r[1] == "IMPLEMENTATION" and r[8] == "KNOWN ENGINEERING DEFECT", r[0]
                assert r[9].startswith("ASSIGN to the receiving company's remaining engineering item") and "REMAINING-ENGINEERING.md" in r[9], r[0]
```

- New:

```text
            # the RE item per row as the register's column 9 names it (lines 321 to 340 at c4492dd3; RE_ROWS in the generator; the
            # union RE-2, RE-4, RE-5 to RE-7 and RE-10 is SET31-CHANGES.md row 17's): REVIEW-2B finding 4
            RE_OF = {"R-225": "item RE-4", "R-227": "item RE-2", "R-232": "item RE-4", "R-238": "item RE-2", "R-242": "item RE-7",
                     "R-244": "item RE-10", "R-245": "items RE-5, RE-6, RE-7"}
            if r[0] in RE_OF:
                assert r[1] == "IMPLEMENTATION" and r[8] == "KNOWN ENGINEERING DEFECT", r[0]
                assert r[9].startswith("ASSIGN to the receiving company's remaining engineering %s (records/l4close/REMAINING-ENGINEERING.md "
                                       "section 5): " % RE_OF[r[0]]), r[0]
                assert "the draft itself stays in its step" in r[9] and r[9].endswith("(DRAFTED)"), r[0]
```

### W20-20. REVIEW-2B finding 5: the D-10 expectation's cited bases

- File: `v2/ecad/tools/tests/test_l9t5.py`
- Line: 1086 to 1087
- Kind: lines
- After: none
- Pairs with: W20-21
- Source: REVIEW-2B finding 5; `v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:188` at `c4492dd3` ("This disposition is correct; D-10 itself remains OPEN REMAINING ENGINEERING."); `v2/docs/records/l4e7/L4E7-P0SOL.md:142` at `c4492dd3` ("it does not resolve D-10.") and line 187 at `786aed2f`; `SET31-CHANGES.md` lines 33 and 54 (rows 2 and 23)
- Class: TEST (a comment's bases corrected)
- Regeneration: none (a test)
- Old:

```text
    # set 31 (SET31-CHANGES.md rows 2 and 23; L4E7-P0SOL.md section 4) words it "OPEN (REMAINING ENGINEERING)" and names route B2
    # UNSELECTED and WITHDRAWN AS DRAFTED in place of set 30's "does not resolve D-10"; never a resolution either way
```

- New:

```text
    # set 31 (SET31-CHANGES.md rows 2 and 23) restates D-10's state and names route B2 UNSELECTED and WITHDRAWN AS DRAFTED; the words
    # "OPEN (REMAINING ENGINEERING)" are cx46's (CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md line 188: "D-10 itself remains OPEN
    # REMAINING ENGINEERING"), which the generator's state quotes; L4E7-P0SOL.md section 4 still reads "it does not resolve D-10" (line
    # 142 at c4492dd3, line 187 once fnd/w4l4e7 is adopted), held below as the state's "with no protection credit"; never a resolution
```

### W20-21. REVIEW-2B finding 5: the B2 non-resolution asserted again

- File: `v2/ecad/tools/tests/test_l9t5.py`
- Line: 1090
- Kind: line (one line added after it)
- After: none
- Pairs with: W20-20
- Source: REVIEW-2B finding 5 ("the state's 'with no protection credit' is present (l4e9_power_path.py, D-10's state) but not asserted"); D-10's state in the generator at `c4492dd3` (line 4232 onward: "Route B2 (not a baseline row) is UNSELECTED and " "WITHDRAWN AS DRAFTED, with no protection credit and no owner item.")
- Class: TEST (a predicate restored: B2's non-resolution)
- Regeneration: none (a test)
- Old:

```text
    assert "remaining engineering item E-1" in dd["D-10"]["state"] and "Route B2 (not a baseline row) is UNSELECTED and WITHDRAWN AS DRAFTED" in dd["D-10"]["state"]
```

- New:

```text
    assert "remaining engineering item E-1" in dd["D-10"]["state"] and "Route B2 (not a baseline row) is UNSELECTED and WITHDRAWN AS DRAFTED" in dd["D-10"]["state"]
    assert "WITHDRAWN AS DRAFTED, with no protection credit" in dd["D-10"]["state"], "route B2 resolves nothing of D-10"
```

### W20-22. REVIEW-2B finding 6: test_remeng's comment

- File: `v2/ecad/tools/tests/test_remeng.py`
- Line: 250
- Kind: fragment
- After: none
- Pairs with: none
- Source: `git diff 0d5f855e b0a67a45 -- v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md`: the hunk `@@ -23,6 +23,7 @@`, the added row is the file's line 26 ("| 26. The MeshSat communications bootstrap ..."); REVIEW-2B finding 6
- Class: TEST (a comment; the two citations it explains stand)
- Regeneration: none (a test)
- Old:

```text
with a table row at line 29); the ledger's
```

- New:

```text
with a table row at line 26); the ledger's
```

### W20-23. W8's (a): R97 under R-240 in IF-EXT-DC

- File: `v2/ecad/tools/pcb_interfaces.yaml`
- Line: 1254
- Kind: fragment
- After: fnd/w14l5 (910f08ef, which carries fnd/w8l5 1ab30f35) merged
- Pairs with: none
- Source: the register's R-240 at `c4492dd3`, line 336 ("R16 34.0k (C705770), R97 24.9k (C136967): `apply_gen_sch_e_p0sol.py` (13 edits)", state DRAFTED); `v2/docs/records/l4e7/L4E7-P0SOL.md` lines 163 to 164 at `c4492dd3` ("**R-173**: its R97 superseded by R-NEW"); the queue's Q-27 row (W8's left-out)
- Class: BINDING (names the drafted change beside the drawn value; no figure computed)
- Regeneration: pinned file (section 1's count; the box's interface readings)
- Old:

```text
R97 28.0k, C126 330 pF
```

- New:

```text
R97 28.0k (24.9k under R-240, drafted, not applied), C126 330 pF
```

### W20-24. W8's (c): section 4.1's row for R-240

- File: `v2/docs/HW-FW-CONTRACT.md`
- Line: 262
- Kind: fragment (a row inserted before it)
- After: fnd/w14l5 (910f08ef, which carries fnd/w8l5 1ab30f35) merged
- Pairs with: none
- Source: the register's R-240 at `c4492dd3`, line 336 (its text, its acceptance "A7's zero-differential output PROVISIONAL (the supplier's S3)", state DRAFTED); `v2/docs/records/l4e7/L4E7-P0SOL.md` line 167 at `c4492dd3` ("**R-176 row 3**: U5's +-0.240 V line replaced by U5 under 10 mV (layout"); this contract at `c4492dd3` names neither TRK_VIN nor IMON_IN (read: no occurrence); the queue's Q-27 row (W8's left-out)
- Class: BINDING (a drafted change listed where section 4.1 lists the drafts; no state claimed beyond the register's)
- Regeneration: pinned file (section 1's count)
- Old:

```text
| R-02 R138 5 mOhm (`records/l4e4/apply_gen_sch_a_r138.py`) |
```

- New:

```text
| R-240 board E's solar input sense moved off U5 onto the backstop's bank (`records/l4e7/apply_gen_sch_e_p0sol.py`, 13 edits: R59 and TRK_VIN removed, U5's pins 32 to 34 on TRK_VS, U23 INA169 on the bank into IMON_IN with C79, R16 34.0k, R97 24.9k) | V-E16 (R-176 row 3) | no row of this contract reads TRK_VIN or IMON_IN; R-176 row 3's U5 line is record l4e7's to restate under R-240 (L4E7-P0SOL.md section 5: U5 under 10 mV, a layout check; W20-N1); A7's zero-differential output PROVISIONAL (the supplier's S3); DRAFTED, not applied (L4-E9's register R-240) |
| R-02 R138 5 mOhm (`records/l4e4/apply_gen_sch_a_r138.py`) |
```

## 4. NEEDS THE COORDINATOR (both candidates, their sources; no row applied by default)

### W20-N1. R-176 row 3's U5 line under R-240 (W8's (b); `SET31-CHANGES.md:123`)

Record l4e7's P0 page replaces the line when R-240 applies (`v2/docs/records/l4e7/L4E7-P0SOL.md:167` at `c4492dd3`: "**R-176 row 3**: U5's +-0.240 V line replaced by U5 under 10 mV (layout"); set 31 left it ("neither draft carries it (a finding for the next set)", `SET31-CHANGES.md:123`); R-240 is DRAFTED, not applied (register line 336). Whether the register restates row 3 before R-240 is applied is a judgement on what the row describes (the drawn circuit or the drafted one), so both are given. Candidate A annotates (narrower: the drawn line stays, the drafted line is named with its condition); candidate B leaves the row as it is. With A, the same words stand in `HW-FW-CONTRACT.md` V-E16 (line 313 at `c4492dd3`; restated by W8 on `fnd/w8l5`, so the coordinator's text follows W8's there) and in the page's 5d row (line 757, "U5 within +-0.240 V at the IC pins").

- **W20-N1a**, `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md` line 272, Old:

```text
U5's CSPIN to CSNIN within +-0.240 V, U21 turning Q12 off
```

  Candidate A:

```text
U5's CSPIN to CSNIN within +-0.240 V (under R-240, drafted, not applied: under 10 mV in magnitude, a layout check, L4E7-P0SOL.md section 5), U21 turning Q12 off
```

  Candidate B:

```text
no edit (the present circuit's line stands until R-240 is applied)
```

  Sources: A, `L4E7-P0SOL.md:167` (as quoted) and the register's R-240 (line 336); B, `SET31-CHANGES.md:123`.

### W20-N2. R-217's release words (W13's left-out; `fnd/w13l4e9` `56ab0d01`, `L4E9-W5-PATCH.md` section 7, line 1191)

DD-7's change-list row and register row say "three" drafts of record l8p, as their source still does: record l4e11's E11-43 (`v2/docs/records/l4e11/l4e11_power.py:7128`, `l4e11_power.out:514`, `L4E11-SOURCE-ONLY-AND-ENTRY.md:733` at `c4492dd3`) and the DD-7 draft's own line 50 ("released with l8p's three drafts and this record's charger draft"), while record l8p's `L8P-BREAKER.md` section 6 item 1 names six (W5 on `fnd/w5l8p` `cd19df59`, lines 266 to 289; W13's WP-27 restates the draft's line 50 to "record l8p's six drafts"). Candidate A (W13's reading): no L4-E9 text runs ahead of its source; L4-E9's three texts follow record l4e11's restatement of E11-43. Candidate B: restate them now, in the commit that applies WP-27 and restates E11-43, with the six named in the register's order as W13's WP rows name them. The register's "Applied after" cell and the order constraints stay as they are under either.

- **W20-N2a**, `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md` line 313, Old:

```text
released with l8p's three drafts (R-206 to R-208)
```

  Candidate A:

```text
no edit until record l4e11 restates E11-43
```

  Candidate B:

```text
released with record l8p's six drafts (R-206, R-207, R-208, R-222, R-244, R-246; L8P-BREAKER.md section 6 item 1)
```

- **W20-N2b**, `v2/docs/records/l4e9/l4e9_power_path.py` line 6469, Old:

```text
in the release of R-206 to R-208 (L4-E11 19h)
```

  Candidate A:

```text
no edit until record l4e11 restates E11-43
```

  Candidate B:

```text
in the release of record l8p's six drafts, R-206, R-207, R-208, R-222, R-244 and R-246 (L8P-BREAKER.md section 6 item 1; L4-E11 19h)
```

- **W20-N2c**, `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md` line 458, Old:

```text
in the release of R-206 to R-208 (L4-E11 19h)
```

  Candidate A:

```text
no edit until record l4e11 restates E11-43
```

  Candidate B:

```text
in the release of record l8p's six drafts, R-206, R-207, R-208, R-222, R-244 and R-246 (L8P-BREAKER.md section 6 item 1; L4-E11 19h)
```

  Sources: A, W13 (`L4E9-W5-PATCH.md:1191` at `56ab0d01`); B, `L8P-BREAKER.md` section 6 item 1 (`cd19df59`, lines 266 to 289) and W13's WP-27. N2b and N2c are applied together (the page's section 3 table equals the generator's CHANGE_ORDER), and the generator's output line 1344 moves with them.

### W20-N3. The ledger's citations into record l4e7's three pages after W4's adoption (found here; not in W10's list)

W4 (`fnd/w4l4e7` `786aed2f`) rewrites `L4E7-P0SOL.md`, `SUPPLIER-P1-1-P0SOL.md` and `B2-PRESENCE.md`, so once it is adopted 29 of the ledger's 30 citation strings into them (aliases P0SOL, P11 and B2) name other lines: the map below was computed by matching the unchanged lines of each file at `c4492dd3` and at `786aed2f` (difflib, equal blocks only; "changed" means a cited line was itself rewritten and needs a reading). test_remeng's AMENDMENT_CITES then fails on two entries: at `786aed2f` `B2-PRESENCE.md` lines 168 to 170 do not read "below the stage's voltage" (the phrase stands at line 181) and `SUPPLIER-P1-1-P0SOL.md` lines 120 to 123 do not read "back-feeding PV_F through Q12's body diode" (line 160). W10's 145 tests expected to fail before regeneration (`_runs/int31/PLAN.draft.md`) do not name test_remeng. The ledger binds its line numbers to the revisions it read (its header: `1c6d56f5`, and `6fe398e9` for the amendment's citations), so two remedies stand: A, re-cite the ledger to the adopted pages in the adoption commit (as commit 2b re-cited its 13 `[OWN:n]`), with test_remeng's two entries moved; B, keep the ledger's declared revisions and let test_remeng read the three aliases at `6fe398e9` by `git show`.

| Alias | Citation at `c4492dd3` | Times | At `786aed2f` |
|---|---|---|---|
| P0SOL | `[P0SOL:132-143]` | 1 | `[P0SOL:176-188]` |
| P0SOL | `[P0SOL:99-121]` | 1 | changed (a cited line rewritten; a reading) |
| P0SOL | `[P0SOL:117-121]` | 1 | changed (a cited line rewritten; a reading) |
| P0SOL | `[P0SOL:179]` | 1 | `[P0SOL:233]` |
| P11 | `[P11:62-70]` | 1 | `[P11:91-99]` |
| P11 | `[P11:25-34]` | 1 | `[P11:42-51]` |
| P11 | `[P11:40-49]` | 1 | `[P11:68-77]` |
| P11 | `[P11:58-70]` | 1 | `[P11:87-99]` |
| P11 | `[P11:51-80]` | 1 | `[P11:79-109]` |
| P11 | `[P11:85-89]` | 2 | changed (a cited line rewritten; a reading) |
| P11 | `[P11:89-92]` | 1 | changed (a cited line rewritten; a reading) |
| P11 | `[P11:51-56]` | 1 | changed (a cited line rewritten; a reading) |
| P11 | `[P11:110-120]` | 1 | changed (a cited line rewritten; a reading) |
| P11 | `[P11:120-123]` | 3 | changed (a cited line rewritten; a reading) |
| P11 | `[P11:44]` | 1 | `[P11:72]` |
| P11 | `[P11:123]` | 1 | `[P11:160]` |
| P11 | `[P11:149-152]` | 1 | `[P11:186-191]` |
| P11 | `[P11:19-92]` | 1 | `[P11:33-126]` |
| P11 | `[P11:29-34]` | 2 | `[P11:46-51]` |
| B2 | `[B2:4-6]` | 1 | `[B2:4-6]` |
| B2 | `[B2:27-29]` | 1 | `[B2:39-41]` |
| B2 | `[B2:22-25]` | 3 | `[B2:34-37]` |
| B2 | `[B2:145-152]` | 4 | `[B2:157-164]` |
| B2 | `[B2:173-174]` | 1 | `[B2:193-194]` |
| B2 | `[B2:24-25]` | 1 | `[B2:36-37]` |
| B2 | `[B2:168-170]` | 4 | changed (a cited line rewritten; a reading) |
| B2 | `[B2:136-140]` | 1 | `[B2:148-152]` |
| B2 | `[B2:151]` | 1 | `[B2:163]` |
| B2 | `[B2:110-129]` | 1 | `[B2:122-141]` |
| B2 | `[B2:131-152]` | 1 | `[B2:143-164]` |

- **W20-N3a**, `v2/ecad/tools/tests/test_remeng.py` line 248, Old:

```text
("B2", 168, 170, "below the stage's voltage")
```

  Candidate A:

```text
("B2", 181, <the end line the coordinator reads>, "below the stage's voltage") with the ledger re-cited
```

  Candidate B:

```text
no edit; test_remeng reads B2-PRESENCE.md at 6fe398e9 by git
```

- **W20-N3b**, `v2/ecad/tools/tests/test_remeng.py` line 249, Old:

```text
("P11", 120, 123, "back-feeding PV_F through Q12's body diode")
```

  Candidate A:

```text
("P11", <the start line the coordinator reads>, 160, "back-feeding PV_F through Q12's body diode") with the ledger re-cited
```

  Candidate B:

```text
no edit; test_remeng reads SUPPLIER-P1-1-P0SOL.md at 6fe398e9 by git
```

  Sources: A, the map above; B, the ledger's own header (`REMAINING-ENGINEERING.md` lines 46 to 48 at `c4492dd3`).

## 5. Items answered with no row, and the reasons

- **README 220 of record l9t5 (W11's left-out):** the file table's row says what `apply_l4e9_changelist_p0.py` IS, "a text draft for the integrator", true of the file after 7070f106 applied it (W11: "the file table: 'a text draft for the integrator', what the file is", README.md:466 at `85b6f258`), and "it refuses a second run" stays true of `--write` (REVIEW-2B section 3: "`--write` refuses with exit 3 and writes nothing"). One observation for the coordinator, no row: the same cell lists "R-220 to R-239 and R-242 to R-244" where the draft's REG_ADD adds R-220 to R-239 and R-242 to R-245 (the draft's docstring line 9 at `c4492dd3`, "R-242 to R-245 after R-240"; REVIEW-2B section 3, "the 24 ids").
- **83.47 V (register) against 83.48 V (page), W8's (d): both kept.** The register's R-176 (line 272) and the page's 5d bench row (757), 8a's D-10 row (1026, its first figure) and B6-ENG-1's row (1095) print 83.47 V from L4-E7's round 5 at `1a73f5b4` (`v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md` lines 620 and 1024: "PV_F 83.47 V at that loop"). The page's F3 (lines 37, 134, 839, 875, 1026, 1765) prints 83.48 V from record l4e7's P0-7 (`SUPPLIER-P1-1-P0SOL.md:33`, "PV_F 83.48 V"; `L4E7-P0SOL.md:151`; cx46 quotes it, `CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:95`, "F3's 83.48 V is a MODEL result"). This file does not decide which rounding or which case each is; it names the record each line cites.
- **`l4e9_power_path.out:975`, "criterion 2 CONDITIONAL" (W15's finding):** the block carries its dated marker. Its heading is line 944, "13. UPDATE ROUND 3 (2 October 2026): L4-E13 ACCEPTED; U-03 A CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC)", printed by the generator's line 3534 block; line 1017's "criterion 2 FAIL with 2 defects open" sits under section 14's heading (line 978, "14. UPDATE ROUND 5"). No marker is added.
- **REVIEW-2B finding 7 (`l9t5_connected.out` lines 60 to 62):** answered by W20-15, the generator literal that prints them (`l9t5_connected.py` lines 517 to 518); the output changes only through the cascade.

## 6. Apply order and what each application forces

1. **After `fnd/w4l4e7` is merged** (W10's order puts it first): W20-13 and W20-14 (the ledger; no regeneration), with the coordinator's choice on W20-N3 in the same commit (A: the ledger's l4e7 citations and test_remeng's two entries; B: test_remeng's reader), then test_remeng.
2. **After `fnd/w14l5` is merged** (it carries `fnd/w8l5`): W20-23 (`pcb_interfaces.yaml`) and W20-24 (`HW-FW-CONTRACT.md`) in the commit that adopts W8's text, so their pins move once (the typed-in pins `l4e9_power_path.py` lines 75 to 76 and `l4e11_power.py` line 54 W8 named, and the outputs that print the files' digests); W20-18 (test_l5pwr's docstring; no regeneration).
3. **L4-E9 in one commit:** W20-01 to W20-12 (page and generator together), with W20-N1 and W20-N2 as decided and W7's and W13's rows; then `_bin/regen_out.py` for `l4e9_power_path.out` (line 1562 moves with W20-02; the `[OWN:n]` rows change the page's generated blocks, not the output) and the page's pins (records l4e10 and l4e11 and the ten outputs that print its digest).
4. **Record l9t5:** W20-15, W20-16 and W20-17 together, after `fnd/w11l9t5` (its lines 1002 to 1004 and 1013 to 1014 do not overlap); then `l9t5_connected.out` through regen_out (lines 60 to 62 and 216 change; `l8r2_dist.out` pins the generator, `l9t5_connected.out` the applier).
5. **Tests, any time after their files' merges:** W20-19, W20-20, W20-21 (test_l9t5), W20-22 (test_remeng); none forces a regeneration.

**Force a regeneration (a generator or a pinned page or file):** W20-01 to W20-12, W20-15 to W20-17, W20-23, W20-24, and W20-N1a, W20-N2a to W20-N2c if candidate A or B edits them. **Do not:** W20-13, W20-14, W20-18 to W20-22 (tests and the ledger's prose, which no output pins), and W20-N3 (a test or the ledger).

## 7. Left out, and why

- **W4's own citation of the owner file** (`L4E7-P0SOL.md` line 148 at `786aed2f`: "the owner's part 23, `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:680`"): written on W4's base before part 26, so after the merge it names line 680 where the quoted part 23 words stand at 681 (`[OWN:681]` in the ledger at `c4492dd3`). Not a row: the text is not in the integration's commit; the coordinator corrects it in the merge of `fnd/w4l4e7` (680 to 681).
- **B6-ENG-1 elsewhere on the page** (read in passing; Q-19 names section 4e only, so no row): lines 534 and 541 (section 3, R-180's and R-187's routes), 656 (section 5's head), 757 (5d's bench row), 878 (section 6), 931 (7a), all before 8a's history note (line 1045), and 1320, 1563, 1674 and 1847 after it, outside 8a; each names set 29's identifier and is the coordinator's to read with W20-01.
- **Q-22 and Q-23** (W5's findings): W13's rows WP-01 to WP-27. **W1's two "already applied" tests:** W14's branch.
- **No generator, regen_out, suite or box job was run**; the line numbers are `c4492dd3`'s and the map of section 4 was computed from `git show` texts.
