mergeable: yes

# Check 1 of integration set 16, `fnd/int17` at `3f69af66` against main `6cd331ef` (MESHSAT-1357)

AI review, labelled as such: an independent check by a Claude session that did not build this integration. It is not a
qualified engineering review. 30 September 2026, 06:54 to 07:13 CEST (read from `date`). Scope: the integration only,
not the content that the energy stream's CHECK-5 and the handover's CHECK-5 already accepted. Everything below is what I
read or ran myself.

Refs confirmed: `fnd/int17` = `3f69af66c5ab`, main = `6cd331effee9`, merge base = main, `fnd/l3r2` = `de524ec8`.
The set is 27 commits. Two clones, both removed:
* a shared clone `_scratch/chk-int17`, with `int17-evidence-de11cc4e.tar` extracted (`git status` clean after it);
* a single-branch clone `_scratch/chk-int17s`, made with `git clone --no-local --single-branch --branch fnd/int17`. It
  holds only `fnd/int17` and 3286 commits.

## Blocking

None.

## Minors

1. **LAYER-STATUS.md's gate row for the independent check is stale against the live page.** Line 291 reads "NOT MET",
   citing CHECK-1 to CHECK-3 of L3-R2 as "accepted: no" and a further check as owed. REQUIREMENTS-L3-R2.md section 2
   (line 25), rendered on the set, reads "MET", with check-l3r2-5 ACCEPTED for the handover as prepared at `028531e4`.
   * This is what the scripts wrote: round 3e updated `l3r2.yaml` and the pages, and no LAYER-STATUS script followed it.
   * The section says its states are "this writing's" and names the live page, so it is not false as dated.
   * An `apply_layer_status_l3_r3e.py` that restates the row would remove the contradiction.
2. **Path history on main will not show the branch's commits by default.** The `-s ours` merge is TREESAME to its
   first parent, so `git log -- v2/docs/handover/layer3/l3r2.yaml` (and `git blame`) on main follow `de11cc4e` and
   `e2e6af95`, not `9493847c` or the other branch commits. They are reachable (`git log --full-history`, or the merge's
   second parent). This is an observation for readers, not a defect.
3. **One intermediate branch commit carries literal dashes that the merge brings into main's history.** `6071b410`,
   the first `fnd/l3r2` commit, added a screening constant `DASHES` holding a literal U+2013 and U+2014. Later
   commits replaced it, and the final tree has none. It is a code constant, not drafted text, and exists in history only.

## Registry

* **Replay of the apply commit.** On `72b91c91` I took `fnd/l3r2`'s files at `028531e4` by the README's first line and
  ran the run order as written:
  * `read_cfl006.py`;
  * the session, `d23`, `d24`, `d25` and `r3b` scripts;
  * `apply_layer_status_l3`, `_r3`, `_r3b`, `_r3c` and `_fill`;
  * `apply_l3r2_s127`, `apply_layer_status_l3_r3d` and `apply_records_readme_row`;
  * then `rules_lib.py requirements` (0 errors, 0 warnings), `rules_render.py --requirements`, `render_l3r2.py` (and its
    `--check`: 3 pages, 0 out of date) and `dryrun.py`.

  Each script's `--check` and write returned 0. The resulting tree is **identical to `de11cc4e`'s**, with no file
  different, so the set's `pcb_requirements.yaml`, REQUIREMENTS-TRACE.md, LAYER-STATUS.md and the records README row are
  exactly what the scripts write.
* **Against the branch.** The set's registry differs from `de524ec8`'s in one place only: S-125's title ("written by",
  sha `29840bee91216e59`). Those two lines come from set 15's `e5322674`, which the branch lacks.
  * Across the whole tree, `de524ec8` and the set differ in set 15's `4012429e..6cd331ef` changes only (EXECUTION-PLAN,
    REQUIREMENTS-TRACE, `records/int16` and the S-125 lines), plus the REQUIREMENTS-L3-R2.md header sha and the `l3r2/`
    records README row, which the branch never ran on itself.
  * No other difference.
* **What the registry changes against main.**
  * Records changed: CFL-002, CFL-006, CHO-003, REQ-008, REQ-012, REQ-016, REQ-029, REQ-054, REQ-057, REQ-068 and
    REQ-072.
  * Open items: S-114 moves to closed, and M-02 and S-53 change. S-127 is added closed.
  * Owner rulings D-21 to D-25 are added.
  * No record is added or removed, and nothing at the top level changes.
  * Every `closed_by` commit is an ancestor of `3f69af66`, including S-114's `1b9f543c` and S-127's `9493847c`.

## Pages

* Round 3e's nine files at `de524ec8` equal the set's blobs, except REQUIREMENTS-L3-R2.md. That file differs from the
  branch's in its header line only: registry sha16 `bd30f8b5fa50b1ab`, which is the set's registry, against the
  branch's `dc58519b0f8130d0`.
* L3-RECONCILIATION.md, OWNER-DECISIONS-L3.md, `l3r2.yaml`, `render_l3r2.py`, the l3r2 README, check-l3r2-4 and -5, and
  `test_l3r2.py` are byte identical to the branch.
* LAYER-STATUS.md, the records README, the registry and REQUIREMENTS-TRACE.md are unchanged from `de11cc4e` to the tip.

## Energy files

* All 26 files that the energy stream's CHECK-5 lists pass `sha256sum -c` in the set, and each blob equals its blob at
  `cd8720a1`. That covers `records/l3plane`, `records/r11dep`, `a1int/reconcile_lid_panel.py` and `.out`,
  `a1solar/energy_runs.out`, the three vendor files and `sources.txt`.
* The `l3plane` merge `72b91c91` equals `git merge-tree`'s clean result.
* **`l3r2.yaml`'s 21 bindings all verify:**
  * `energy_basis` and `power_path_check`, with their records, outputs and check;
  * the five energy checks and the five L3-R2 checks;
  * the two baseline definitions (CONOPS `6cb7b241`, PRODUCT-BRIEF `85513b92`, both unchanged).

  The H3 digest's `member_sha256` equals the sha256 of `H3/v2/ecad/tools/pcb_requirements.yaml` inside `H3.zip`.
* **Filed checks.** All ten filed checks (energy-basis-check-1 to -5, check-l3r2-1 to -5) are byte identical to the
  checkers' reports under `_reports/chk-energy` and `_reports/chk-l3r2`.

## The `-s ours` merge

* **It changes no file.** `3f69af66`'s tree equals its first parent `e2e6af95`'s (`ae3bf06c`). `9493847c` is reachable
  from the tip, and not from `e2e6af95`.
* **Sound.** A real merge of `e2e6af95` and `de524ec8` (`git merge-tree`, base `4012429e`) auto-merges every file to the
  set's content. Its one conflict is REQUIREMENTS-L3-R2.md's header line, which differs only in the registry sha. So
  `-s ours` discards nothing but the branch's own header sha, and gives the tree a real merge would give with that
  conflict taken from the set.
* **Why it is needed.** The registry validator checks that a `closed_by` commit exists (`rules_lib.py`: `git cat-file -e
  <sha>^{commit}`, line 702). Without the merge, a clone of the set alone lacks `9493847c`, which is the failure the
  first box suite saw.
* **What it brings into main's history.** It adds the nine `fnd/l3r2` commits `6071b410` to `de524ec8`, based on
  `4012429e`, which is on main. Across all 27 of the set's commits:
  * each is authored and committed by Kyriakos Papadopoulos <ncpjfuzl@mxmx.email>, with no trailer and no dash in any
    message, and every subject carries `[MESHSAT-1357]`;
  * no commit's tree tracks a `held/` file or an `.ibs`;
  * no commit touches CONOPS.md, PRODUCT-BRIEF.md or any H3 file. The one H3-named file is the new
    `layer3/h3_registry_digest.json`, a digest read from `H3.zip`; the H3 snapshot and `records/h3` are untouched;
  * the largest blob added is 3.98 MB (the Milliohm sheet);
  * the only dash is minor 3.

## Single-branch clone

With `int17-evidence-de11cc4e.tar` installed (`git status` clean after it):
* **The full render order** (`rules_render.py --requirements`, `rules_status.py` x3, `rules_render.py` x2) leaves
  `git status` clean, with CURRENT-EVIDENCE.md at `c9b98931` throughout.
  * `rules_status.py` exits 1 on its own gate verdict: FAIL of 338 (39 FAIL, 104 INCONCLUSIVE, 195 PASS), the same
    counts as set 15.
* **All five validators give 0 errors:**
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings;
  * `rules_lib.py`: 59 rules, 0 errors, 0 warnings;
  * `rules_render.py --check`: 16 documents, 0 out of date;
  * `rules_render.py --requirements --check`: current;
  * `decisions_render.py --check`: rc 0.
* **The layer 3 checks:** `render_l3r2.py --check`: 3 pages, 0 out of date. `dryrun.py` is byte identical to
  `dryrun.out`.
* **Tests.** `tests/run.py requirement close claims decisions identit l3r2`: 202 passed, 0 failed, 2 skipped (no
  pcbnew). The tree is clean after it.

## Hygiene

* **Added lines against main.** None carries a U+2013 or U+2014, and none carries a host name or user path (`/home/`,
  the runner, `nllei`, `/tmp/claude`, `ankh`, a private address, `root@`).
* **Tracked files at the tip.** No `held/` file and no `.ibs` is tracked.
* **The two new vendor PDFs.** Neither the Milliohm nor the Yageo RC_L text layer has a copyright, rights or
  reproduction term, as their `sources.txt` lines say.

## Counts

Blocking 0. Minors 3 (one stale status row, two history observations). Replays: the apply commit reproduced byte
identical. Bindings: 21 of 21. Energy files: 26 of 26. Filed checks: 10 of 10 identical. Tests: 202/0/2 in the
single-branch clone. Box suite on `3f69af66`: not seen by me.
