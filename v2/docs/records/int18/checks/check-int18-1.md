mergeable: yes

# Check 1 of integration set 17, `fnd/int18` at `1f34bf92` against main `8fec0733` (MESHSAT-1357)

AI review, labelled as such: an independent check by a Claude session that did not build this integration. It is not a
qualified review. 30 September 2026, 13:10 to 13:24 CEST (read from `date`).

**Scope.** The integration only: the scrub is accepted by its CHECK-2, and l3r4 by its CHECK-3 and CHECK-4 (the last
reads `mergeable: yes` for `a547fe1d`). Everything below is what I read or ran myself.

**Refs and setup.**
* `fnd/int18` = `1f34bf92fcb4`, main = `8fec0733`, merge base = main, `fnd/scrub` = `5899d7c7`, `fnd/l3r4` =
  `a547fe1d`.
* The set holds 18 commits: the scrub's 11, l3r4's 4 (`3afdc2d6`, `fcfc6007`, `e8e3ef57`, `a547fe1d`) and three merges.
* One `--no-local --single-branch` clone of `fnd/int18` (`_scratch/chk-int18s`), with `int18-evidence-1f34bf92.tar`
  installed (`git status` clean after it). It holds the redaction commits, `9493847c`, `cd8720a1` and `b42e1827`, and is
  removed.

## Blocking

None.

## Minors

1. **l3r4's four checks are not filed in the tree.** `records/l3r4/` has no `checks/` folder. The stream's README (line
   4) and both merge messages ("checked three times", "checked four times") cite CHECK-1 to CHECK-4, which exist only
   under the scratch reports. l3r2, s122 and w5identc filed theirs, byte for byte. Filing the four under
   `records/l3r4/checks/`, as is done for the others, would make the citation openable.

## Merges

* **All three merges are clean and equal `git merge-tree`'s automatic result, with no conflict:**
  * `96692afc` (main + `5899d7c7`): its tree `fe02c8ec` is exactly the scrub tip's tree;
  * `ca4f4f9f` (+ `e8e3ef57`) gives `1a220f0c`;
  * `1f34bf92` (+ `a547fe1d`) gives `3bfd66f5`.
* **No stray change.** A direct merge of `5899d7c7` and `a547fe1d` gives the same tree, `3bfd66f5`.
* **`records/README.md`, auto-merged.** Every line the scrub adds is present, and so is every line l3r4 adds (the
  `scrub/` and `l3r4/` rows and the two re-pinned `r8int6` rows). The two lines the scrub replaced are gone. No line is
  in the set that is in none of main, the scrub or l3r4.
* **l3r4's three shared files equal l3r4's tip in the set, and the scrub touched none of them:** LAYER-STATUS.md,
  L3-RECONCILIATION.md and `l3r2.yaml`.
* **`apply_layer_status_l3_r4.py` refuses a second run on the set** as designed: exit code 2, "this script has run", no
  file written. The page carries its row once ("MET for the handover as prepared") and the old "NOT MET" row nowhere.
  This also answers set 16's check 1, minor 1.

## Scrub, reissues, registry

* **The scrub.**
  * `count_hits.py` reads 22 instances in 14 files, byte identical to `counts-after.out`.
  * `tests/run.py public_hygiene` passes as part of the test run below.
  * l3r4's added lines hold no pattern: I searched them for the runner's and the laptop's user paths, the session
    temporary root, the mangled project folder name, the host prefix, the laptop's name, its address range, the
    account name and the worktree folder.
* **The reissues.** `handover_pack.py verify` gives OK for H1-R1, H1.1-R1, H2-R1 and H3-R1. `sha256sum -c` gives OK
  for them and for the four originals. `H1/`, the original ZIPs, CONOPS.md and PRODUCT-BRIEF.md are unchanged against
  main.
* **The registry.** `pcb_requirements.yaml` and `pcb_decisions.yaml` are unchanged against main.
* **The pages.** `render_l3r2.py --check` reads 3 pages, 0 out of date, with l3r4's `l3r2.yaml` edit and its
  L3-RECONCILIATION row. `reissue.py --map --check` reads PASSAGE-MAP.md current (rc 0).

## Single-branch clone

* **Render order.** The full order (`rules_render.py --requirements`, `rules_status.py` x3, `rules_render.py` x2), run
  twice: CURRENT-EVIDENCE.md is `c9b98931` both times, and `git status` is clean.
* **Validators.**
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings;
  * `rules_lib.py`: 59 rules, 0 errors, 0 warnings;
  * `rules_render.py --check`: 16 documents, 0 out of date;
  * `rules_render.py --requirements --check`: current;
  * `decisions_render.py --check`: rc 0;
  * `render_l3r2.py --check`: current;
  * `reissue.py --map --check`: rc 0;
  * `render_map.py --check`: current;
  * `count_hits.py`: 22 in 14.
* **Tests.** `tests/run.py requirement close claims decisions identit l3r2 l3r4 public_hygiene handover_pack`: 235
  passed, 0 failed, 2 skipped (no pcbnew). The tree is clean after it.
* **Commits.** All 18 reachable from the set and not from main are authored and committed by Kyriakos Papadopoulos
  <ncpjfuzl@mxmx.email>. None carries a trailer or a dash, and every subject carries `[MESHSAT-1357]`.

## Hygiene

* No U+2013 or U+2014 in the set's added lines against main.
* No host name, user path or private address of ours in them, by the same patterns as above.
* This report names those patterns in words only.

## Counts

Blocking 0. Minors 1. Merges: 3 of 3 clean and equal to the automatic result. Tests: 235/0/2. Render order: stable at
`c9b98931`, run twice. Box suite on `1f34bf92`: not seen by me.
