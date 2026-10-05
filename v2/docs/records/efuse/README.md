# efuse: every eFuse and current-limit setting checked against its exact part's datasheet (task T12, MESHSAT-1357)

Record `efuse`, 5 October 2026, branch `fnd/efuse` from main `aa32332c`. Driven by finding SDR3-F04 (the three-SDR research,
confirmed by the collaborator's challenge cx42 and recheck cx43): board B's U23, a TPS259631 eFuse feeding the LimeSDR's USB, has
its current-limit resistor at 301 Ohm labelled "3.0 A", while TI's TPS2596 sheet (SLVSET8A) prints a 0.125 to 2 A range and a
453 to 7869 Ohm recommended resistance.

Prototype design, desk arithmetic: nothing in this kit has been built, bought, powered or measured. Nothing here is applied to
the tree; both drafts refuse the repository's own generator until a `RELEASE.md` beside them names an accepted check (none exists).

**STATE (5 October 2026, 12:15 CEST): DONE for its scope, not reviewed.** SDR3-F04 is confirmed as EF-F01, and the same setting
on board B's U24 (the RockBLOCK 9704) is a second design defect, EF-F02; both OPEN, each with a one-component DRAFT that composes,
is read in the netlist with mutations that fail, and holds (b) and (c) on C-DEV rev 1 on printed figures. DR-03 (record l4e4) is
reproduced as known. Every other instance passes (a) to (c) in both trees. NOT DONE: no independent check (the coordinator's to
schedule); the box's KiCad netlist export. NEXT ACTION: one focused check of EF-F01 and EF-F02 by the collaborator, then the
owners' items below.

| File | What it is |
|---|---|
| `EFUSE-SETTINGS.md` | The page: the defects first, the inventory and bands of both trees, the sheets, the loads by case, the corrections' evidence, the labelling findings and observations with their owners, the SESSION decisions, what is not done |
| `efuse_check.py`, `efuse_check.out` | The check: the generators' own part tables (record l8p's `gen_netlist.py`, main and the boards' pending drafts in L4-E9's order), the makers' figures as quotes found in the sheets' own text, the loads from record l9pwr, the judgement (a) to (d), the findings, this record's drafts on the netlist with mutations, the E96 alternatives. Regenerate with `_bin/regen_out.py <worktree> v2/docs/records/efuse/efuse_check.py v2/docs/records/efuse/efuse_check.out` |
| `apply_gen_sch_b_u23ilm.py` | DRAFT (EF-F01): board B's R36 301 Ohm to 750 Ohm (1.0718 to 1.3631 A), the call's label and the notes that name it |
| `apply_gen_sch_b_u24ilm.py` | DRAFT (EF-F02): board B's R43 301 Ohm to 1.21 kOhm (0.6681 to 0.8496 A), the call's label and the note |

Inputs read from this tree only: the generators, the drafts under `v2/docs/records/*/apply_gen_sch_*.py`, record l9pwr's output,
Layer 6's catalogue reading, `lcsc_fill.py`, and the sheets under `v2/vendor/` (the TPS1663 and TPS4811-Q1 sheets are held back
by TI's notice in the ignored `v2/vendor/ti/held/`, fetched and pinned by `v2/docs/records/l4e11/fetch_held_back.py`). Branch
drafts named as text only: record l8r2's round 8 on `fnd/l8r4` (`c935542f`, the GND return that restates board B's GND rail),
record l9t5's I-03 drafts on `fnd/l9t5` (U32's note only), record l8p's round on `fnd/l8p2` and L4-E11's rounds on
`fnd/l4e11r11` (the same LM5069-1 and TPS16630 instances as main's drafts); none changes a setting judged here.

Tests: `v2/ecad/tools/tests/test_efuse.py`. Run `python3 run.py test_efuse test_public_hygiene` from the tests folder.
