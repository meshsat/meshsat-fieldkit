# Set 31: the entry pages' rows for the adoption (START-HERE.md and SUPPLIER-HANDOVER.md; MESHSAT-1357)

**DONE:** 24 exact rows (S-01 to S-11 for `v2/docs/handover/START-HERE.md`, U-01 to U-13 for
`v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`) that bring the two entry pages from set 30 to set 31. **NOT DONE:** nothing is
applied; the pages are the coordinator's files. **NEXT:** at set 31's adoption the coordinator fills `__PROMOTED__` and `__ADOPTION__`,
applies the rows, and restates the tests that pin the replaced lines (on main: `test_entrypage.py` and `test_w30entry.py`).

Drafted by worker W39 on branch fnd/res31 on 6 October 2026 for queue item Q-58. Record text only: it changes no state of the pages,
accepts nothing and closes nothing; prototype framing: nothing in the kit has been built, bought, powered or measured.

**What the rows are read against.** The two pages as main holds them at `eff28be3` (set 30's adoption with W33's corrections),
copied verbatim under `v2/docs/records/int31/inputs/` (`START-HERE-eff28be3.md`, `SUPPLIER-HANDOVER-eff28be3.md`; `inputs/SOURCES.txt`
gives each copy's source, git blob and sha256), because `eff28be3` is not in this branch's history. Every "Old text" is on the line
named at `eff28be3`, exactly once on that line; every "New text" differs from it. A row whose new text begins with the whole old line
inserts the lines after it. `test_res31.py` reads each row against the copies.

**The revision rows, as set 30's pages define them.** Tested: the promoted revision, the commit the gated release suite and the
promotion gate ran on (set 31's `__PROMOTED__`, equal to its candidate when main is fast-forwarded, as on set 30). Adopted: the adoption
commit to which main is fast-forwarded after the promotion (`__ADOPTION__`). Packaged: the commit the next supplier delta's README names
in its header, unchanged as a definition, so no row changes it. Reviewed: the candidate the last independent check read, `4d0ff8a2`
(cx46), unchanged because no independent check read a later revision. The two placeholders are the only ones; the coordinator fills
them from the promotion's log and the adoption commit.

**The three claims are not rows here.** Layer 4's DESK gate (NOT PASSED) and the three completion claims stand on both pages as set
30's adoption wrote them, in the coordinator's words; set 31 changes none of them (`v2/docs/records/int31/RESULT.md`, section 6).

## START-HERE.md

### S-01. `v2/docs/handover/START-HERE.md`, line 3: the current revision

Old text:
```text
**Current revision: set 30 (6 October 2026), the revision `dd1aed00d0a0a521063b5792550bc510c4707c59`. Read section 0 first.**
```
New text:
```text
**Current revision: set 31 (6 October 2026), the revision `__PROMOTED__`, an adoption of record text over set 30's `dd1aed00d0a0a521063b5792550bc510c4707c59`. Read section 0 first.**
```
Basis: `v2/docs/records/int31/RESULT.md`, section 1 (the PROMOTED row) and its paragraph "What set 31 is".

### S-02. `v2/docs/handover/START-HERE.md`, line 5: the edition history's list

Old text:
```text
2026, set 30); sections 1 to 9
```
New text:
```text
2026, set 30, set 31); sections 1 to 9
```
Basis: row S-03 adds set 31's paragraph to the history it lists.

### S-03. `v2/docs/handover/START-HERE.md`, after line 89: set 31's paragraph in the edition history

Old text:
```text
accepts, closes or promotes a design claim.
```
New text:
```text
accepts, closes or promotes a design claim.

**Set 31** (6 October 2026; the revision `__PROMOTED__`). An adoption of record text over set 30: the restatements its authors wrote
during set 30's integration (record l4e7's P0 pages, record l8p's release page, records l9t5's and l8r2's hand pages, the supplier
validation annex, Layer 5's contract restatement, the filed patch rows applied to L4-E9's page, register and generator, the citation
re-takes), regenerated to convergence, with the coordinator's items and two tooling corrections. "Set 31 closes NO power item."
(`v2/docs/records/int31/RESULT.md`, section 6); no circuit draft, board generator or netlist changed.
```
Basis: `v2/docs/records/int31/RESULT.md`, sections 2 and 6; `v2/docs/records/int31/CLASSIFICATION.md`, section 2.

### S-04. `v2/docs/handover/START-HERE.md`, after line 100: what set 31 changes in section 0

Old text:
```text
has been built, bought, powered or measured.
```
New text:
```text
has been built, bought, powered or measured.

**Set 31 over set 30 (6 October 2026).** This section was written for set 30. Set 31 changes the Tested and Adopted revisions below,
adds its integration record to the list of what set 30 adds, and changes none of the states: Layer 4's DESK gate and the three
completion claims stand as the assessment gives them on set 30. Its classification counts 14 commits that change a file cx46 read,
each "UNREVIEWED since cx46" (`v2/docs/records/int31/CLASSIFICATION.md`, section 2).
```
Basis: `v2/docs/records/int31/RESULT.md`, section 6 (the three claims unchanged) and section 2.

### S-05. `v2/docs/handover/START-HERE.md`, line 106: the Tested row

Old text:
```text
| Tested | `dd1aed00d0a0a521063b5792550bc510c4707c59` | the promoted revision:
```
New text:
```text
| Tested | `__PROMOTED__` | set 31's promoted revision (set 30's was `dd1aed00d0a0a521063b5792550bc510c4707c59`, kept as dated history):
```
Basis: the Tested row's definition on this page; `v2/docs/records/int31/RESULT.md`, section 1.

### S-06. `v2/docs/handover/START-HERE.md`, line 107: the Adopted row

Old text:
```text
| Adopted | `836f711b` (`836f711b406be48d9eb58c9cf6f7491fbcf7c5ec`) | the adoption commit (6 October 2026, 11:25 CEST), to which main was fast-forwarded after the promotion: the first revision of main that holds these pages and the set 30 records as adopted |
```
New text:
```text
| Adopted | `__ADOPTION__` | set 31's adoption commit, to which main was fast-forwarded after the promotion: the first revision of main that holds these pages and the set 31 records as adopted (set 30's was `836f711b406be48d9eb58c9cf6f7491fbcf7c5ec`, 6 October 2026, 11:25 CEST, kept as dated history) |
```
Basis: the Adopted row's definition on this page.

### S-07. `v2/docs/handover/START-HERE.md`, line 109: the Reviewed row

Old text:
```text
"the second negative on the method, which ends it" (`:3`) |
```
New text:
```text
"the second negative on the method, which ends it" (`:3`); unchanged in set 31: no independent check read a later revision (`v2/docs/records/int31/RESULT.md`, section 1) |
```
Basis: `v2/docs/records/int31/RESULT.md`, section 1 (no independent check read `dd1aed00` or the lineage).

### S-08. `v2/docs/handover/START-HERE.md`, line 117: the unreviewed changes

Old text:
```text
(14 over the 45 commits of `4d0ff8a2..dd1aed00`; 13 of them in W15's range `4d0ff8a2..6bc4424e`).
```
New text:
```text
(14 over the 45 commits of `4d0ff8a2..dd1aed00`; 13 of them in W15's range `4d0ff8a2..6bc4424e`). Set 31 adds its own: 14 commits that change a file cx46 read over the 73 commits of `dd1aed00..f0748b49`, each "UNREVIEWED since cx46" (`v2/docs/records/int31/CLASSIFICATION.md`, section 2), with the rows after `f0748b49` as that file gives them at the adoption.
```
Basis: `v2/docs/records/int31/CLASSIFICATION.md`, section 2.

### S-09. `v2/docs/handover/START-HERE.md`, line 123: the documents row

Old text:
```text
| Documents and editable artifacts | on main as a DESK candidate (`dd1aed00d0a0a521063b5792550bc510c4707c59`) |
```
New text:
```text
| Documents and editable artifacts | on main as a DESK candidate (`__PROMOTED__`, set 31) |
```
Basis: `v2/docs/records/int31/RESULT.md`, section 6 (kept apart from the three claims).

### S-10. `v2/docs/handover/START-HERE.md`, after line 158: set 31's record in the list

Old text:
```text
  `v2/docs/records/int30/CLASSIFICATION.md`.
```
New text:
```text
  `v2/docs/records/int30/CLASSIFICATION.md`.
- `v2/docs/records/int31/RESULT.md`: set 31's integration record, with `v2/docs/records/int31/CLASSIFICATION.md`, its classification
  of every commit after set 30's promoted revision.
```
Basis: `v2/docs/records/int31/RESULT.md`, section 7.

### S-11. `v2/docs/handover/START-HERE.md`, line 170: the checkout to reproduce from

Old text:
```text
From a full git checkout at `dd1aed00d0a0a521063b5792550bc510c4707c59`:
```
New text:
```text
From a full git checkout at `__PROMOTED__`:
```
Basis: the Tested row (S-05).

## SUPPLIER-HANDOVER.md

### U-01. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 8: the page's current set

Old text:
```text
**Brought to set 30 on 6 October 2026: read section 0 first.**
```
New text:
```text
**Brought to set 31 on 6 October 2026: read section 0 first.**
```
Basis: `v2/docs/records/int31/RESULT.md`, section 1.

### U-02. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 22: section 0's heading

Old text:
```text
## 0. This revision: set 30 (6 October 2026)
```
New text:
```text
## 0. This revision: set 31 over set 30 (6 October 2026)
```
Basis: row U-03.

### U-03. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, after line 30: what set 31 changes in section 0

Old text:
```text
framing: nothing in the kit has been built, bought, powered or measured.
```
New text:
```text
framing: nothing in the kit has been built, bought, powered or measured.

**Set 31 over set 30 (6 October 2026).** This section was written for set 30. Set 31 is an adoption of record text over it: the
restatements its authors wrote during set 30's integration, the filed patch rows applied to L4-E9's page, register and generator, and
the citation re-takes, regenerated to convergence. It changes the Tested and Adopted revisions of 0a, adds its integration record to
0c, and changes none of the states of 0b: "Set 31 closes NO power item." (`records/int31/RESULT.md`, section 6). Its classification
counts 14 commits that change a file cx46 read, each "UNREVIEWED since cx46" (`records/int31/CLASSIFICATION.md`, section 2).
```
Basis: `v2/docs/records/int31/RESULT.md`, sections 2 and 6.

### U-04. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 36: the Tested row

Old text:
```text
| Tested | `dd1aed00d0a0a521063b5792550bc510c4707c59` | the promoted revision:
```
New text:
```text
| Tested | `__PROMOTED__` | set 31's promoted revision (set 30's was `dd1aed00d0a0a521063b5792550bc510c4707c59`, kept as dated history):
```
Basis: as S-05.

### U-05. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 37: the Adopted row

Old text:
```text
| Adopted | `836f711b` (`836f711b406be48d9eb58c9cf6f7491fbcf7c5ec`) | the adoption commit (6 October 2026, 11:25 CEST), to which main was fast-forwarded after the promotion: the first revision of main that holds these pages and the set 30 records as adopted |
```
New text:
```text
| Adopted | `__ADOPTION__` | set 31's adoption commit, to which main was fast-forwarded after the promotion: the first revision of main that holds these pages and the set 31 records as adopted (set 30's was `836f711b406be48d9eb58c9cf6f7491fbcf7c5ec`, 6 October 2026, 11:25 CEST, kept as dated history) |
```
Basis: as S-06.

### U-06. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 39: the Reviewed row

Old text:
```text
"the second negative on the method, which ends it" (`:3`) |
```
New text:
```text
"the second negative on the method, which ends it" (`:3`); unchanged in set 31: no independent check read a later revision (`records/int31/RESULT.md`, section 1) |
```
Basis: as S-07.

### U-07. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 51: the unreviewed changes

Old text:
```text
(14 over the 45 commits of `4d0ff8a2..dd1aed00`; 13 of them in W15's range `4d0ff8a2..6bc4424e`).
```
New text:
```text
(14 over the 45 commits of `4d0ff8a2..dd1aed00`; 13 of them in W15's range `4d0ff8a2..6bc4424e`). Set 31 adds its own: 14 commits that change a file cx46 read over the 73 commits of `dd1aed00..f0748b49`, each "UNREVIEWED since cx46" (`records/int31/CLASSIFICATION.md`, section 2), with the rows after `f0748b49` as that file gives them at the adoption.
```
Basis: as S-08.

### U-08. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 57: the documents row

Old text:
```text
| Documents and editable artifacts | on main as a DESK candidate (`dd1aed00d0a0a521063b5792550bc510c4707c59`) |
```
New text:
```text
| Documents and editable artifacts | on main as a DESK candidate (`__PROMOTED__`, set 31) |
```
Basis: as S-09.

### U-09. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, after line 94: set 31's record in 0c

Old text:
```text
| `v2/docs/records/int30/RESULT.md`, with `v2/docs/records/int30/CLASSIFICATION.md` | the integration record: the reviewed and the integrated revisions bound, every intervening commit classified (the classification), the gate lines |
```
New text:
```text
| `v2/docs/records/int30/RESULT.md`, with `v2/docs/records/int30/CLASSIFICATION.md` | the integration record: the reviewed and the integrated revisions bound, every intervening commit classified (the classification), the gate lines |
| `v2/docs/records/int31/RESULT.md`, with `v2/docs/records/int31/CLASSIFICATION.md` | set 31's integration record: set 30's promoted revision and set 31's bound, every intervening commit classified, the gate lines |
```
Basis: `v2/docs/records/int31/RESULT.md`, section 7.

### U-10. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 135: the checkout to reproduce from

Old text:
```text
From a full git checkout at `dd1aed00d0a0a521063b5792550bc510c4707c59`
```
New text:
```text
From a full git checkout at `__PROMOTED__`
```
Basis: as S-11.

### U-11. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 150: the suite's line

Old text:
```text
The gated release suite's line for `dd1aed00d0a0a521063b5792550bc510c4707c59` is in the package's `README.md` and in
```
New text:
```text
The gated release suite's line for `__PROMOTED__` is in the package's `README.md` and in
```
Basis: `v2/docs/records/int31/RESULT.md`, section 4 (the gate lines).

### U-12. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 151: the record that carries it

Old text:
```text
   `records/int30/RESULT.md`.
```
New text:
```text
   `records/int31/RESULT.md` (set 30's, for `dd1aed00`, in `records/int30/RESULT.md`).
```
Basis: as U-11.

### U-13. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, after line 396: the dated entry

Old text:
```text
  `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1005`) and the DESK-gate assessment kept apart from it. No circuit change is applied, and nothing in it accepts, closes or promotes a design claim.
```
New text:
```text
  `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1005`) and the DESK-gate assessment kept apart from it. No circuit change is applied, and nothing in it accepts, closes or promotes a design claim.
- **6 October 2026: set 31, the revision `__PROMOTED__`** (section 0). An adoption of record text over set 30: the authors'
  restatements written during set 30's integration, the filed patch rows applied, the citations re-taken, regenerated to convergence
  (`v2/docs/records/int31/RESULT.md`). No circuit change is applied, and nothing in it accepts, closes or promotes a design claim;
  Layer 4's DESK gate and the three completion claims stand as set 30's assessment gives them.
```
Basis: `v2/docs/records/int31/RESULT.md`, sections 1 and 6.
