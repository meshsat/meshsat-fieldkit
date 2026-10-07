**DONE:** the remaining 45.88 K/W statements of L4-E9's page written as twelve exact rows (P-01 to P-12) for the coordinator, each with its old and new text at the base `53a68c7c`, its paired generator data and its source; every occurrence of 45.88 K/W in records l4e11 and l4e10's hand pages classified (section 4: none is stated outside its dated history as the current per-FET bar, so none is edited). **NOT DONE:** nothing applied: the page, the register, the generator and its output are the integration's files; the regeneration and its pins are the coordinator's. **NEXT:** the coordinator applies P-01 to P-12 in the next set, regenerates `l4e9_power_path.out` (its lines 614, 655 and 1650 change; the page's gen:classes block with it) and re-pins what pins the page.

# L4-E9's remaining 45.88 K/W statements: the patch for the coordinator (W7, MESHSAT-1357, 6 October 2026)

**What this is.** A list of exact text corrections to L4-E9's page `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md` and to the
generator data that renders or checks the same texts, `v2/docs/records/l4e9/l4e9_power_path.py`, written by worker W7 on branch
`fnd/w7rem` from set 30's integration commit 2c, `53a68c7ce8a8b964d8d3905b4a769b50db096040`. Neither file is edited here: the page is
the integration's file, and every row below is for the coordinator to apply in the next set. The rows narrow or label a claim; none
designs anything, computes a figure, consumes a review or changes a verdict. Prototype framing: nothing in the kit is built, bought,
powered or measured; every figure below is desk arithmetic printed by a record (MODEL or INFERRED as that record labels it).

**The finding it answers.** Slot H's set 31 record left "45.88 K/W outside PC-05's stated places: 8a's D-14 row and data, the exit
table's D-14 row, U-04's choice row, UDC-1's comparison and the 8a history paragraph still state set 29's per-FET bar"
(`v2/docs/records/l4e9/SET31-CHANGES.md:120-122`); the DESK-gate draft carries it as K-06 (branch `fnd/dgate` at `249e9e47`,
`v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.draft.md:316`, cited as text only). Those are exactly the places below.

## 1. The figure, its date, and what superseded it

- **45.88 K/W** is record l9stk's even-split per-FET bar (its E-1, section 15.5), taken by L4-E11's round 9 as E11-29's junction
  limit: "the installed three, each FET's (Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart, R17's coupling into each
  junction at most 1 K/W" (`v2/docs/records/l4e11/l4e11_power.out:1174`, 19c), under the heading "## 19. Round 9: record l9stk's
  protection and record l8p's breaker (4 October 2026; out 19)" (`v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md:1817`). It
  entered L4-E9 with set 29: the page at set 29's commit `aa76c894` (4 October 2026, 15:24) prints it, the page at set 27's
  `94971c8c` and at set 28's `d834e6a7` does not (read with `git grep`; the test of this record re-reads it where those commits are in
  the object store). **SESSION reading:** the brief named it "the superseded set 27/28 figure"; the tree dates it to set 29, 4 October
  2026, and every row below says set 29. Reversed by: a commit of set 27 or 28 shown to print it on L4-E9's page.
- **Superseded as the per-FET bar** by L4-E11's round 11 (21d: "E-1's installed acceptance becomes the worst split's, (Zself + 2 Zmut)
  at most 40.78 K/W", `v2/docs/records/l4e11/l4e11_power.out:1522`) and, as it now stands, by E11-29's row
  (`v2/docs/records/l4e11/l4e11_power.out:568`): "each junction's worst-split figure at its OWN m_k ... at most 45.88 K/W, so each
  (Zself + 2 Zmut) at most 40.78 K/W without m", and the design target (round 16) "each junction's worst-split figure Zw at most 37.59
  K/W (Zself 30.07 K/W for three side by side at m 0.1)". The register's R-159 already reads that row word for word since set 31
  (`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:255`).
- **What 45.88 K/W still is, and stays:** the bound on each junction's worst-split figure at its own m (line 1 of E11-29's acceptance,
  the row above), and section 21b's bar at m of 1/4 or more. Every new text below keeps it only in those two roles, or labelled
  "set 29's ... SUPERSEDED as the per-FET bar". Labels as L4-E11 gives them: 40.78 K/W is round 11's "SESSION selection; CONDITIONAL
  on E11-29 (coupon) and E11-36" (`v2/docs/records/l4e11/README.md:110`); 37.59 K/W is round 16's design target at the SESSION
  allowance of 10 mW a lead, "(INFERRED; the coupling at its bound for planning)"
  (`v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md:3233`). No row below claims either is achievable (L4-E11: "whether 40.78 K/W
  can be met at all (no printed or measured figure shows it)", `v2/docs/records/l4e11/README.md:79`).

## 2. How to apply

Apply P-01 to P-12 together in one commit of the next set: the page's tables are tested equal to the generator's data
(`v2/ecad/tools/tests/test_l4e9.py`: `t_the_two_categories_are_kept_apart_on_the_page_and_in_the_register` for 8a and 8b, the exit
table in `t_consolidation_the_handover_the_exit_and_the_status`), so a page row applied without its data row fails that test. Each
Old text occurs exactly once in its file at `53a68c7c` (a whole line where the Kind reads line or lines, else a fragment of the named
line); the New text replaces it. Then regenerate `l4e9_power_path.out` through `_bin/regen_out.py` (its lines 614, 655 and 1650
change, and the page's `gen:classes` block is rendered again with P-09's text) and re-pin what pins the page (records l4e10 and
l4e11) at the freeze. The module `v2/ecad/tools/tests/test_w7rem.py` holds every row: the Old text where it is said to be, each page
row equal to its data row once both are applied (the format strings rendered with the figures the generator reads), the generator's
own checks still met by the new data, and the predicate the rows serve (every statement of the per-FET bar names 40.78 K/W without m;
45.88 K/W only at its own m or labelled set 29's and SUPERSEDED), which the Old texts fail.

## 3. The rows

### P-01. Section 8a, D-14's Options cell (the page)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 1030
- Kind: fragment
- Pairs with: P-02
- Source: out:500 (E11-29's row), out:1106 (round 9, 19c), page 19's heading (4 October 2026); the set 29 date by git (section 1)
- Class: CLAIM CHANGE (narrows: the per-FET bar labelled SUPERSEDED, E11-29's current row and target added)
- Old:

```text
(Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart, the pair's 20.39 K/W the fallback (the pair's earlier
```

- New:

```text
(Zself + 2 Zmut) at most 40.78 K/W without m (E11-29 as L4-E11's row restates it, its rounds 11 to 16; each junction's worst-split figure at its own m at most 45.88 K/W) with R17 placed apart, the design target Zw at most 37.59 K/W (set 29's per-FET bar of 4 October 2026, 45.88 K/W steady with R17 placed apart (L4-E11's round 9, 19c), SUPERSEDED as the per-FET bar by that row), the pair's 20.39 K/W the fallback (the pair's earlier
```

### P-02. The generator's DEFECTS entry D-14, its options (one literal line)

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 4329
- Kind: line
- Pairs with: P-01
- Source: as P-01; the generator's own check (D-13 to D-15's figures printed by L4-E11, lines 2041 to 2045) holds: 40.78, 45.88, 37.59 and 20.39 are printed by L4-E11's output after its section 15
- Class: CLAIM CHANGE (data of P-01)
- Old:

```text
                "(Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart, the pair's 20.39 K/W the fallback (the pair's earlier "
```

- New:

```text
                "(Zself + 2 Zmut) at most 40.78 K/W without m (E11-29 as L4-E11's row restates it, its rounds 11 to 16; each junction's worst-split figure at its own m at most 45.88 K/W) with R17 placed apart, the design target Zw at most 37.59 K/W (set 29's per-FET bar of 4 October 2026, 45.88 K/W steady with R17 placed apart (L4-E11's round 9, 19c), SUPERSEDED as the per-FET bar by that row), the pair's 20.39 K/W the fallback (the pair's earlier "
```

### P-03. Section 8b, U-04's Constraint cell (the page)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 1193
- Kind: fragment
- Pairs with: P-04
- Source: as P-01
- Class: CLAIM CHANGE (narrows, as P-01)
- Old:

```text
for each FET's installed (Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart (E11-29; the pair's (Zself + Zmut) at most 20.39 K/W the fallback; the pair's earlier
```

- New:

```text
for each FET's installed (Zself + 2 Zmut) at most 40.78 K/W without m (E11-29 as L4-E11's row restates it, its rounds 11 to 16; each junction's worst-split figure at its own m at most 45.88 K/W; the design target Zw at most 37.59 K/W) with R17 placed apart (set 29's per-FET bar of 4 October 2026, each FET's (Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart (L4-E11's round 9, 19c), SUPERSEDED as the per-FET bar by that row; E11-29; the pair's (Zself + Zmut) at most 20.39 K/W the fallback; the pair's earlier
```

### P-04. The generator's CHOICES entry U-04, its constraint (two literal lines become five)

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 4129
- Kind: lines
- Pairs with: P-03
- Source: as P-01; the expectation fx_u04_expect (line 3399) still finds its phrase '(Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart' inside the SUPERSEDED clause, and the test t_choice_and_defect_figures_are_printed_by_the_reconciliation finds 40.78, 45.88, 37.59 and 20.39 printed outside the gate (out 20 and 27)
- Class: CLAIM CHANGE (data of P-03)
- Old:

```text
                   "largest limit, from 76.25 C with the band and R17 in place, for each FET's installed (Zself + 2 Zmut) at most 45.88 K/W "
                   "steady with R17 placed apart (E11-29; the pair's (Zself + Zmut) at most 20.39 K/W the fallback; the pair's earlier "
```

- New:

```text
                   "largest limit, from 76.25 C with the band and R17 in place, for each FET's installed (Zself + 2 Zmut) at most 40.78 K/W "
                   "without m (E11-29 as L4-E11's row restates it, its rounds 11 to 16; each junction's worst-split figure at its own m at most "
                   "45.88 K/W; the design target Zw at most 37.59 K/W) with R17 placed apart (set 29's per-FET bar of 4 October 2026, each FET's "
                   "(Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart (L4-E11's round 9, 19c), SUPERSEDED as the per-FET bar by "
                   "that row; E11-29; the pair's (Zself + Zmut) at most 20.39 K/W the fallback; the pair's earlier "
```

### P-05. The generator's expectation of U-04's figures (fx_u04_expect): E11-29's bar added beside the round's

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 3399
- Kind: line
- Pairs with: P-04
- Renders with: 40.78
- Source: E11-29's bar as the generator already reads it (g['z3m'], line 2059, from L4-E11's row); with it the generator refuses the old U-04 text (exit 4, 'U-04 does not quote the round's figure')
- Class: CHECK (a predicate added; no figure changed)
- Old:

```text
            "(Zself + 2 Zmut) at most %s K/W steady with R17 placed apart" % fmt(F["f02"]["z3"]),
```

- New:

```text
            "(Zself + 2 Zmut) at most %s K/W steady with R17 placed apart" % fmt(F["f02"]["z3"]), "(Zself + 2 Zmut) at most %s K/W without m" % fmt(F["f02"]["z3m"]),
```

### P-06. Section 6, the exit table's D-14 row (the page)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 837
- Kind: fragment
- Pairs with: P-07, P-08
- Source: as P-01
- Class: CLAIM CHANGE (narrows, as P-01)
- Old:

```text
for each FET's installed (Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart (the pair's 20.39 K/W the fallback)
```

- New:

```text
for each FET's installed (Zself + 2 Zmut) at most 40.78 K/W without m (E11-29 as L4-E11's row restates it; each junction's worst-split figure at its own m at most 45.88 K/W) with R17 placed apart, the design target Zw at most 37.59 K/W (set 29's 45.88 K/W per FET of 4 October 2026, L4-E11's round 9, SUPERSEDED as the per-FET bar) (the pair's 20.39 K/W the fallback)
```

### P-07. The generator's exit row D-14 (cons_exit_table's data), its format string

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 7399
- Kind: fragment
- Pairs with: P-06, P-08
- Renders with: 40.78, 45.88, 37.59, 45.88, 20.39
- Source: as P-01; test_l4e9's t_consolidation_the_handover_the_exit_and_the_status requires the page's exit table to equal the script's
- Class: CLAIM CHANGE (data of P-06)
- Old:

```text
for each FET's installed (Zself + 2 Zmut) at most %s K/W steady with R17 placed apart (the pair's %s K/W the fallback)
```

- New:

```text
for each FET's installed (Zself + 2 Zmut) at most %s K/W without m (E11-29 as L4-E11's row restates it; each junction's worst-split figure at its own m at most %s K/W) with R17 placed apart, the design target Zw at most %s K/W (set 29's %s K/W per FET of 4 October 2026, L4-E11's round 9, SUPERSEDED as the per-FET bar) (the pair's %s K/W the fallback)
```

### P-08. The generator's exit row D-14, its arguments

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 7400
- Kind: line
- Pairs with: P-07
- Source: z3m (40.78), z3 (45.88), zw (37.59) as lines 2056 to 2061 read them
- Class: CLAIM CHANGE (data of P-06)
- Old:

```text
         % (fmt(F["f02"]["allow"]), fmt(F["f02"]["held_lim"][0]), fmt(F["f02"]["held_lim"][1]), fmt(F["f02"]["z3"]), fmt(F["f02"]["z2_fb"]), F["f02"]["at_allow"][1], fmt(F["f02"]["dock_tj"][1])),
```

- New:

```text
         % (fmt(F["f02"]["allow"]), fmt(F["f02"]["held_lim"][0]), fmt(F["f02"]["held_lim"][1]), fmt(F["f02"]["z3m"]), fmt(F["f02"]["z3"]), fmt(F["f02"]["zw"]), fmt(F["f02"]["z3"]), fmt(F["f02"]["z2_fb"]), F["f02"]["at_allow"][1], fmt(F["f02"]["dock_tj"][1])),
```

### P-09. Section 8f, UDC-1's Current cell (inside gen:classes; regenerated, never hand-edited)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 1401
- Kind: fragment
- Pairs with: P-10, P-11
- Source: as P-01
- Class: CLAIM CHANGE (narrows, as P-01)
- Old:

```text
each FET's installed (Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart, the hottest junction at most 150 C held at 23.93 A from 76.25 C (E11-29; the pair's 20.39 K/W the fallback)
```

- New:

```text
each FET's installed (Zself + 2 Zmut) at most 40.78 K/W without m (E11-29 as L4-E11's row restates it; each junction's worst-split figure at its own m at most 45.88 K/W) with R17 placed apart, the design target Zw at most 37.59 K/W (set 29's 45.88 K/W per FET of 4 October 2026, L4-E11's round 9, SUPERSEDED as the per-FET bar), the hottest junction at most 150 C held at 23.93 A from 76.25 C (E11-29; the pair's 20.39 K/W the fallback)
```

### P-10. The generator's comparison UDC-1 (cons_comparisons), its format string

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 5534
- Kind: line
- Pairs with: P-09, P-11
- Renders with: 40.78, 45.88, 37.59, 45.88, 23.93
- Source: as P-01
- Class: CLAIM CHANGE (data of P-09)
- Old:

```text
                    "FET's installed (Zself + 2 Zmut) at most %s K/W steady with R17 placed apart, the hottest junction at most 150 C held at %s A "
```

- New:

```text
                    "FET's installed (Zself + 2 Zmut) at most %s K/W without m (E11-29 as L4-E11's row restates it; each junction's worst-split figure at its own m at most %s K/W) with R17 placed apart, the design target Zw at most %s K/W (set 29's %s K/W per FET of 4 October 2026, L4-E11's round 9, SUPERSEDED as the per-FET bar), the hottest junction at most 150 C held at %s A "
```

### P-11. The generator's comparison UDC-1, its arguments

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 5537
- Kind: line
- Pairs with: P-10
- Source: as P-08
- Class: CLAIM CHANGE (data of P-09)
- Old:

```text
                    "near 0 V, against TI's below 5 nF)" % (fmt(g["z3"]), fmt(g["held_lim"][0]), fmt(g["held_lim"][1]), fmt(g["z2_fb"]), fmt(g["allow"]),
```

- New:

```text
                    "near 0 V, against TI's below 5 nF)" % (fmt(g["z3m"]), fmt(g["z3"]), fmt(g["zw"]), fmt(g["z3"]), fmt(g["held_lim"][0]), fmt(g["held_lim"][1]), fmt(g["z2_fb"]), fmt(g["allow"]),
```

### P-12. Section 8a, the paragraph 'The Layer 4 review adds D-13 and D-14' (history of what round 9 restated; labelled)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 1130
- Kind: line
- Pairs with: none (hand text)
- Source: as P-01
- Class: PRESENTATION OR BINDING (history kept, the superseded figure labelled with its date and its successor)
- Old:

```text
76.25 C with the band and R17 in place, for each FET's installed (Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart
```

- New:

```text
76.25 C with the band and R17 in place, for each FET's installed (Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart (set 29's per-FET bar of 4 October 2026; SUPERSEDED as the per-FET bar by E11-29's row as L4-E11 restates it, its rounds 11 to 16: each (Zself + 2 Zmut) at most 40.78 K/W without m, each junction's worst-split figure at its own m at most 45.88 K/W, the design target Zw at most 37.59 K/W)
```


## 4. Records l4e11 and l4e10: every 45.88 K/W, classified (nothing edited)

Read on `53a68c7c` in every Markdown page of `v2/docs/records/l4e11/` and `v2/docs/records/l4e10/` (their `checks/` and
`clarification/` folders included). Record l4e10 prints no 45.88 K/W in any hand page. Record l4e11's pages print it on the lines
below; each is either inside a dated round (its section or round heading carries the round and its date) or a current statement
that uses 45.88 K/W in one of its two standing roles (section 1). **None states 45.88 K/W as the current per-FET bar outside a dated
history, so none is edited** (the brief's item 1 has no place in these two records). The test reads every line of these pages that
prints 45.88 and refuses one this table does not list.

| File | Line | Where | Class | The words on the line |
|---|---|---|---|---|
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 105 | In short, round 9's bullet | DATED HISTORY, labelled in place ("40.78 K/W for any split since round 11") | "Zself + 2 Zmut at most 45.88 K/W with R17 apart, 40.78 K/W for" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 123 | In short, round 11's bullet | DATED HISTORY (the even split's defect) | "at record l9stk's 45.88 K/W its" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 719 | section 8, row E11-29 (current; the script's row word for word) | STANDING ROLE (round 11's derivation and 21b's bar; the row's bar is 40.78 K/W without m) | "record l9stk's even-split 45.88 K/W is taken times 8/9" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 1560 | 17d, block E11-29 (current) | STANDING ROLE (21b's bar; the block's bar is 40.78 K/W) | "record l9stk's even-split 45.88 K/W times 8 (1 - m)(1 +" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 1561 | 17d, block E11-29 (current) | STANDING ROLE (21b's bar at m of 1/4 or more) | "45.88 K/W at or over it" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 1848 | 19b, round 9 (4 October 2026) | DATED HISTORY | "**45.88 K/W**" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 1865 | 19c, round 9 | DATED HISTORY, labelled in place (line 1869: "Round 11 (21d) restates the bar at 40.78 K/W for any split") | "at most 45.88 K/W steady with R17 placed apart" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2016 | 19g, status of round 9 | DATED HISTORY | "restated** as the junction limit, 45.88 K/W with R17 apart" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2295 | 20i, round 10 (4 October 2026) | DATED HISTORY (the even split recorded OPEN) | "Record l9stk's E-1 limit (45.88 K/W" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2301 | 20i, round 10 | DATED HISTORY | "the allowance's 45.88 K/W puts that junction at" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2302 | 20i, round 10 | DATED HISTORY | "**45.88 K/W is NOT" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2360 | 21a, round 11 (4 October 2026) | DATED HISTORY | "Zmut) at most **45.88 K/W** with R17 apart" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2364 | 21a, round 11 | DATED HISTORY | "at record l9stk's 45.88 K/W the hottest junction" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2383 | 21b, round 11 | DATED HISTORY (the formula's derivation) | "record l9stk's even-split 45.88 K/W times 8 (1 - m)(1 + 2 m) / 9" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2388 | 21b, round 11 | DATED HISTORY (21b's table) | "45.88" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2433 | 21e, round 11 | DATED HISTORY (a mutation that fails) | "the even split's 45.88 K/W, a bar 1 % over 40.78" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2456 | 21g, round 11 | DATED HISTORY (a finding for record l9stk) | "its even-split 45.88 K/W is not the bar for three" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2700 | 23c, round 13 (4 October 2026) | DATED HISTORY | "(40.78 and 45.88 K/W)" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2740 | 23e, round 13 | DATED HISTORY (21b's bar at m of 1/4 or more) | "45.88 K/W" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2919 | 24d, round 14 (5 October 2026) | DATED HISTORY (the worst-split figure at its own m) | "Zw_k at most 45.88 K/W is exactly S_k" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2926 | 24d, round 14 | DATED HISTORY (line 1, the worst-split figure) | "45.88 K/W" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2951 | 24e, round 14 | DATED HISTORY (the search's specimens) | "worst-split figure lies near 45.88 K/W" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 2984 | 24f, round 14 | DATED HISTORY (an illustration) | "44.34 against 45.88 K/W" |
| `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` | 3149 | 25g, round 15 (5 October 2026) | DATED HISTORY (line 1, the worst-split figure) | "line 1 at 45.88 K/W" |
| `v2/docs/records/l4e11/README.md` | 43 | round 14's table (5 October 2026) | DATED HISTORY (line 1, the FETs' allocation) | "the FETs' allocation (45.88 K/W)" |
| `v2/docs/records/l4e11/README.md` | 51 | round 14's state | DATED HISTORY (a finding for L4-E9, answered by set 31's PC-05: `v2/docs/records/l4e9/SET31-CHANGES.md:44`) | "R-159 still carries 45.88 K/W" |
| `v2/docs/records/l4e11/README.md` | 64 | round 13's table (4 October 2026) | DATED HISTORY (21b's bar at m of 1/4 or more) | "44.45 against 45.88 K/W for m at or over 1/4" |
| `v2/docs/records/l4e11/README.md` | 82 | round 13's notes for others | DATED HISTORY (a finding for L4-E9, answered by set 31's PC-05) | "still carries round 9's 45.88 K/W" |
| `v2/docs/records/l4e11/README.md` | 83 | round 13's notes for others | DATED HISTORY (a test anchor of set 29) | ""45.88 K/W steady by the body diode"" |
| `v2/docs/records/l4e11/README.md` | 108 | round 11's claims (4 October 2026) | DATED HISTORY | "157.7 C held at 23.93 A at 45.88 K/W" |
| `v2/docs/records/l4e11/README.md` | 110 | round 11's claims | DATED HISTORY (the derivation of 40.78 K/W) | "(45.88 x 8 (1 - m)(1 + 2 m) / 9" |
| `v2/docs/records/l4e11/README.md` | 118 | round 11's findings for others | DATED HISTORY | "record l9stk's E-1 bar 45.88 K/W is the even split's" |

## 5. What this file leaves to others, and its SESSION decisions

- **Not in this file's scope:** the register's dated set 29 paragraph (`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:59`) and
  L4-E9's README paragraph of set 29 (`v2/docs/records/l4e9/README.md:160`) state 45.88 K/W inside their dated history and are left
  as written; R-159 already labels "round 9's 45.88 K/W per FET" as history (`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:255`);
  5d's E11-29 row (`v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:750`) already reads "at most 40.78 K/W without m (each junction's
  worst-split figure at its own m at most 45.88 K/W)" since set 31, and its "R17's coupling at most 0.29 K/W" is the row's two-place
  print of the one target L4-E11 prints as 0.294 K/W (K-12, answered on the annex's side by W3 on `fnd/w3annex` at `686de0a2`).
- **K items of the DESK-gate draft's section 5 touched here:** K-06's L4-E9 side (P-01 to P-12). K-08 (one identifier E-1 for two
  items): every new text above names the junction limit as E11-29's row or record l9stk's and adds no bare "E-1". Left to their files:
  K-03, K-04 and K-15 (the P0 list and LH-12: K-04 and K-15 in `v2/docs/records/l4close/P0-POWER-LIST.rev3.patch.md`), K-09, K-12,
  K-13, K-14, K-16, K-17, K-20 to K-24, K-26, K-28; K-01, K-02, K-05, K-07, K-10, K-11, K-18, K-19, K-25 and K-27 read NO in the
  draft's own column.
- **SESSION decisions** (under the owner's standing rule of 26 September 2026):
  1. *The set 29 date* in place of the brief's "set 27/28" (section 1). Reversed by: a set 27 or 28 commit printing it on the page.
  2. *Label, do not delete:* each place keeps 45.88 K/W once, labelled "set 29's ... SUPERSEDED as the per-FET bar", so the
     generator's expectation of U-04's figures (`fx_u04_expect`) still finds the round's figure and the page keeps its history; P-05
     adds E11-29's bar to that expectation so the old text is refused. Reversed by: deleting the labelled clause with P-05's old
     expectation line in the same commit.
  3. *The 8a paragraph annotated* (P-12), not rewritten: it narrates what round 9 restated, which stays true as history. Reversed by:
     the coordinator rewriting the paragraph from E11-29's row.
  4. *No edit of records l4e11 and l4e10* (section 4). Reversed by: a line of theirs shown to state 45.88 K/W as the current per-FET
     bar outside a dated round.
