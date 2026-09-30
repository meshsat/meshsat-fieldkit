# The public-file scrub (MESHSAT-1357, 30 September 2026)

Branch `fnd/scrub` from main `8fec0733`, one author, never pushed by the author. The MeshSat field kit V2 is an unbuilt
prototype design: nothing here changes a design file, and nothing has been built, ordered, powered or measured.

## What was asked

The repository is public: GitLab project 64 mirrors to `github.com/meshsat/meshsat-fieldkit` within minutes. The
owner's standing rule is that public files carry **no internal host names, user paths or addresses**. The owner's words
of 29 September 2026: *"Complete the public-file cleanup as a bounded task. Preserve engineering provenance. Reissue
affected handover snapshots with new version records and hashes rather than silently modifying accepted releases. This
instruction does not authorize rewriting Git history."*

**Git history was not rewritten.** Every value removed here is still in the repository's history (every commit up to
`8fec0733`), on the public mirror, and in the four accepted snapshots `H1.zip`, `H1.1.zip`, `H2.zip`, `H3.zip` and the
unzipped `H1/`, which stay byte for byte as published. Removing them from history is the owner's decision and was not
taken.

## Counts, before and after

`count_hits.py` prints them (`counts-before.out` at `8fec0733`, `counts-after.out` on this branch's tree). An instance
is one path or one name; the ZIPs are read entry by entry.

| Token class | Before: instances (files) | Replaced or derived | After: instances (files) |
|---|---|---|---|
| runner path prefix | 70 (46) | 60 | 10 (8) |
| session temp path | 84 (21) | 79 | 5 (5) |
| host name | 7 (5) | 2 | 5 (3) |
| laptop host name | 4 (3) | 3 | 1 (1) |
| laptop user path | 6 (5) | 5 | 1 (1) |
| **all tracked files** | **171 (71)** | **149 in 57 files** | **22 (14)** |

The 22 left are in the 7 files of "What was left" below and in the 7 files of the accepted release `H1/`. In the ZIPs:
the four accepted snapshots keep their 7, 8, 6 and 8 entries; the four reissues carry 2, 3, 2 and 3, exactly the files
the tree leaves. `MAP.md` has 148 rows for the 149 instances (one script line held two).

## Every file, by class

The 71 tracked files that carried a pattern at `8fec0733` (`counts-before.out` lists them), and what was done with each;
`MAP.md` names every replacement by file and line, with the treatment.

| Class | Files | Treatment |
|---|---|---|
| live document | 11: `EXECUTION-PLAN.md`, the appendix, `respin-footprints-2026-09-04.md`, `revA/order/ORDER-LOG.md`, `v1/cad/FIXES.md`, `v2/vendor/aioc/aioc-net.xml` (our own export of a maker's schematic), and the records `d6dec/README.md`, `w5si/RECOVERY.md`, `rf2walk/LOG.md`, `s117/LOG.md`, `s120/LOG.md` | tokens |
| reading or log | 19: six DOC-002 verdicts of boards C, P and E5, and the records `d4emcon/readings/`, `d6rel/apply-script-test.txt`, `int10/box/config-apply.log`, `int10/dryrun.out`, `r8int6/fix/validators-760d7f41.txt`, `retake6/analysis/` (two), `retake6/worktree/run.txt`, `s98/readings/` (three), two recovered author results of w5si and w5tray | edited as text, not re-taken (decision 3) |
| filed check, not cited by sha | 18 (listed in decision 4; one of them, `cx1/checks/check-1-phase1.py`, is also a script) | tokens and a filing note at the end |
| script whose path does work | 10: `d6dec/box/to_box.sh`, `int7/box/int7_install_pack.sh`, `r8int6/commit_r8int6.sh`, `r8int6/copy_evidence.sh`, `int10/dryrun.py`, `w5si/recovery/replay.py`, `w5tray/recovery/replay.py`, `cx1/checks/check-1-phase1.py`, `v1/cad/inspect_doc.py`, `v1/cad/render.py` | path derived, comments tokened, each run by `script_tests.py` |
| left | 7 (the table "What was left") | untouched, disclosed |
| accepted release | 7 files of `v2/release/handover/H1/`, and the four snapshot ZIPs | untouched; reissued |

## Decisions (authority SESSION)

Every decision below is the session's, ruled under the owner's standing rules of 21 September 2026 (engineering
decisions are the session's) and 26 September 2026 (never ask; take the recommended answer), with `ruled_by: SESSION`.
**Why no owner judgement was standing:** the owner's instruction fixed the outcome (no such values in public files),
the method for accepted releases (reissue with new records and hashes) and the limit (no history rewrite); what
remained was bookkeeping with one conservative option each, and none spends money, changes what the kit is claimed to
be or accepts a risk. Each is reversible by a later scrub or by the owner.

1. **Scope.** The five classes of `scrub_lib.py`: the runner's user path prefix, session scratch paths under the
   runner's temporary directory, the runner's host name, the laptop's host name, and the laptop's user path. The brief
   named the first four and private addresses; the laptop's user path is a user path of our own host, so the standing
   rule covers it. No private address of our own hosts was found: every private-range address in the tree is a
   maker's own (`v2/vendor/cluster/super4c.*`, `v2/vendor/zigbee/*`, the default cluster ranges of
   `v2/vendor/cluster/k3s-requirements.md`, the maker's own page address in `v2/vendor/rockblock/`) or a datasheet
   section number. The runner's account name alone (without the path) remains in five apply scripts
   (`int13/apply_cfl016_set12.py`, `int15/apply_check15*_fixes.py`, `od01/patch_od01f.py`) as the pattern those scripts
   refuse or replace; it is not a path, a host or an address, and the guard does not look for it.
2. **Tokens.** `<worktrees>`, `<repo>`, `<projects>`, `<runner home>`, `/tmp/<scratchpad>`, `/tmp/<session temp>`, "the
   runner", "the laptop", `<laptop home>` (`MAP.md`, "Token classes"). A session scratch path keeps its `/tmp/` root:
   `rules_status.py` classes a reading whose input sits under a temporary directory `TEMP_INPUT`, and three readings
   (DOC-002 on boards C, P and E5) are in that class; with the root kept, their class is unchanged and only the text of
   the reason differs (`rule-audit` compared before and after). In Markdown a token is written in a code span, so a
   renderer does not drop it as an unknown tag.
3. **Readings are edited as text, not re-taken.** Every reading that carried a hit read a tree, a scratch folder or a
   box run that no longer exists, so no tool can take the same reading again. The six verdicts of DOC-002
   (`doc_provenance_*`, `ledger_verify` on C, P and E5) have their tools, but a re-take would read this tree instead of
   the one recorded and move DOC-002's evidence class: a new engineering reading, not a redaction. Each is listed in
   `MAP.md` with that reason.
4. **Filed checks.** A filed check whose bytes no file cites by sha (18 of them: `cx1/checks/`, `int7/CHECK*.md`,
   `int7/checks/`, `int8/CHECK-notes.md`, `int8/checks/`, `w5si/check-1/RESULT-w5si-check-1.json`) is redacted with a
   filing note at its end, as `int16/checks/check-int16-1.md` does; the JSON check carries it as its last key. A filed
   check cited by sha is left (below).
5. **Scripts.** Ten scripts used a typed-in path to work. Each now derives it: an environment variable whose default
   sits under the home directory (`$WORKTREES`, default `~/worktrees/meshsat-fieldkit`; `$SCRATCH` and `$TMPDIR`;
   `$BOX_BIN`; `$CX1_WORKTREE`; `$W5SI_RECOVERED`; `$FIELD_KIT_STEP`, `$FIELD_KIT_RENDERS`), git (`$PRECOMMIT_CHECK` and
   `$MAIN_CLONE` from the common git directory), or the transcript the script replays (the two recovery replays find
   the lost worktree's path in the commands they run). `script_tests.py` ran every one (`script_tests.out`: 12 of 12):
   in a sandbox under `<worktrees>/_scratch/`, with the box reached only through stubs, and where the filed script can
   still run (w5si's replay, cx1's phase 1, int10's dry run) the output equals the filed script's line for line; w5si's
   replay still ends with three IDENTICAL at the transcript's command 158.
6. **Re-pins.** Two scripts of `r8int6/` are pinned by sha256 in `v2/docs/records/README.md`; `apply_scrub.py` re-pinned
   both rows and wrote the filed sha256 and size into each row, so the filed bytes stay findable in history.
7. **The appendix is redacted** although three records cite its sha256/16 `5e942dd41e9e4ed0` (`LAYER-STATUS.md` with
   commit `b69f20db`, and the layer 2 and layer 3 reviews as what they read): each names the commit it read, no
   registry binds the file, and it is the living design record (the three lines are not `### 32.` headings, which
   `reserved.json` protects). The bytes those records read are at every commit up to `8fec0733`.
8. **Snapshots.** All four accepted snapshots carried hits, so all four are reissued (below). A file the tree leaves is
   left in the reissue too, so every hash a page or a check inside the snapshot cites for it still holds.
9. **The guard** (`v2/ecad/tools/tests/test_public_hygiene.py`) keeps its patterns base64-encoded, as `scrub_lib.py`
   does, so that the guard is not itself a public copy of the values it keeps out. The encoding hides nothing from a
   reader who decodes it; it keeps the values out of a plain search. It reads every tracked file (binaries included)
   with `git grep` and every tracked ZIP entry by entry, in about 8 s on the runner.

## What was left, and why (disclosure for the owner)

| File | Why it is left |
|---|---|
| `v2/docs/reviews/REVIEW-A-LAYER-1-2026-09-27.md` | a filed review record of layer 1 (host name, runner path, session path); its sha256/16 `d469a268fe0b8768` is cited by `RELEASE-H2.md`, `RELEASE-H3.md`, `records/h2/handover_counts.out`, `records/h3/handover_counts.out`, `records/handover/H3-COHERENCE-CHECK.md`, `REVIEW-B-LAYER-3`, `REVIEW-LAYER-1-RELEASE` and `candidates/hc3.patch` |
| `v2/docs/records/handover/H2-USABILITY-CHECK.md` | a filed check (session path); `v2/docs/records/README.md` pins its sha256 |
| `v2/docs/records/handover/H3-COHERENCE-CHECK.md` | a filed check (runner path); `v2/docs/records/README.md` pins its sha256 |
| `v2/docs/records/handover/H3-USABILITY-CHECK.md` | a filed check (runner path); `v2/docs/records/README.md` pins its sha256 |
| `v2/docs/handover/candidates/hc3.patch` | the H1.1 candidate as it was reviewed (session path); `candidates/README.md` pins its sha256 |
| `v2/docs/feasibility/fab/out/pulldowns.txt` | a reading (runner path) that `FAILOVER-FABRIC.md` cites by sha256 (`895f8df0...`); the requirements registry binds that page (`FAILOVER-FABRIC.md@a0ad3d7436cd126d`), so a re-pin would change the baselined layer 3 registry and the L3-R2 pages rendered from it |
| `v2/cad/render/meshsat-v2-concept.blend` | a binary Blender scene that stores the laptop's last-used folder; a re-save in Blender is the only clean edit, and it rewrites the scene file |
| `v2/release/handover/H1/` (7 files) and `H1.zip`, `H1.1.zip`, `H2.zip`, `H3.zip` | accepted releases, never edited; superseded by the reissues |

An owner re-issue of the four filed checks and the review record (each with its citing rows re-pinned) would remove the
rest from the tree; it is not taken here because it breaks the hashes the release records cite.
`v2/docs/CONOPS.md` and `v2/docs/PRODUCT-BRIEF.md` (baselined) carry no hit and are untouched.

## The reissued snapshots

| Version | ZIP sha256 | Bytes | Redaction commit (only parent: the source commit) | Supersedes |
|---|---|---|---|---|
| H1-R1 | `f8566e274af3371ea0cb3b98b1a18af4daf64078eb751e76ddd8a14d8f312686` | 47,072,838 | `a256fb5e48fa2b34c89ddd18d71824ae0d5ff678` (`8a19fe29`) | `H1.zip` `10598fc8...` |
| H1.1-R1 | `5d6d018b8698aacf095ac06090d295b5cd494331901838c46a64970e96c44994` | 51,145,129 | `8dfdcb6217a045e09f2d0ad6d2a938c1fccc8b81` (`98ce9f83`) | `H1.1.zip` `fc563395...` |
| H2-R1 | `e12a6f1cc0066e0a195210ae1fd0323d4309fa3c046a5ae937941106b341a7ee` | 51,910,286 | `b290170750bf26fb04a12aad0fbd01a38fa7e1d7` (`b89b50b4`) | `H2.zip` `20072be7...` |
| H3-R1 | `3b5d9b79883adf43837b19cb50ee083de1be8238480179724e6ac3dc205e7525` | 52,203,750 | `329fcfa64bdf27b86175ecdced361d954cab48e4` (`75ad6ee5`) | `H3.zip` `6922a96d...` |

Each has its version record `v2/docs/handover/RELEASE-<version>.md`, its `MANIFEST.tsv` (every file's sha256) inside
the ZIP and as `<version>.MANIFEST.tsv` beside it, its `.zip.sha256`, and a START-HERE that opens with a box naming
the version it supersedes, why, each changed file with its sha256/16 before and after, and each file left with the
reason. `reissue_snapshots.py commits` makes the four redaction commits with git plumbing (no checkout) as the owner
at a fixed date, so a second run makes the same ids; each commit's diff passed the pre-commit check. `reissue_snapshots.py
build` builds each with `handover_pack.py build --zip-only`, runs `handover_pack.py verify`, and asserts that every
manifest row equals the superseded snapshot's except the changed files, START-HERE (root copy and source) and
`SOURCE.txt`, that only the files the tree leaves carry a pattern, and that the ZIP is under the cap (H3-R1 is 225,050
bytes under it). A second build on the runner gave the same four ZIPs byte for byte.

**Reproducibility.** The packer of main (`handover_pack.py` sha256 `fd7e353f...`, the one that built H3) rebuilt H1,
H1.1, H2 and H3 from their source commits on the runner on 30 September 2026 with every manifest row identical except
`SOURCE.txt` (the builder named, and the "public" column of the commit timeline, which reads the building clone's
remote branch); H3's ZIP differed from the published one only in that entry.

**The redaction commits in history.** They are on no branch when made. The set's merge commit records all four in this
branch's history with `git merge -s ours` (the tree stays this branch's), the way `3f69af66` recorded `fnd/l3r2`. That
adds history and rewrites none; once main carries it and is pushed, the reissues' source commits are public.

## Validators and tests on this branch

- `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings. `rules_lib.py`: 59 rules, 0 errors, 0 warnings.
  `rules_render.py --check`: 16 documents, 0 out of date. `rules_render.py --requirements --check`: current.
  `decisions_render.py --check`: rc 0. `handover/layer3/render_l3r2.py --check`: 3 pages, 0 out of date.
- The render order (`rules_render.py --requirements`, `rules_status.py` three times, `rules_render.py` twice), run
  twice: no tracked page changed. The rule audits differ from main's only in the reason text of DOC-002 on C, P and E5.
- `tests/run.py public_hygiene`: 4 passed. The guard fails on main at `8fec0733` (57 files).
- The full suite on the runner (no KiCad), on the tree of the first commit of the set: 2245 passed, 0 failed, 92
  skipped (a skip is not a pass). After the reissues: `public_hygiene`, `handover_pack`, `requirements`, `l3r2`,
  `rule_gate_mapping` and `reserved` again (the integration check of the set gives the counts).

## For the integrator

The set is five commits on `fnd/scrub` from main `8fec0733` (first parent): the tree's scrub, the guard, the merge that
records the four redaction commits, the four reissues with their records, and this README with the map, the counts
after and the records index row. From the main clone, with no `cd`:

```
git -C <repo> log --oneline 8fec0733..fnd/scrub
git -C <repo> merge --ff-only fnd/scrub                 # main has not moved since 8fec0733; else merge and re-run below
python3 <repo>/v2/docs/records/scrub/render_map.py --check
python3 <repo>/v2/ecad/tools/tests/run.py public_hygiene
python3 <repo>/v2/docs/records/scrub/count_hits.py      # 22 instances in 14 files, as counts-after.out
for v in H1-R1 H1.1-R1 H2-R1 H3-R1; do python3 <repo>/v2/ecad/tools/handover_pack.py verify <repo>/v2/release/handover/$v.zip; done
env -C <repo>/v2/release/handover sha256sum -c H1-R1.zip.sha256 H1.1-R1.zip.sha256 H2-R1.zip.sha256 H3-R1.zip.sha256
python3 <repo>/v2/ecad/tools/rules_lib.py requirements && python3 <repo>/v2/ecad/tools/rules_lib.py
python3 <repo>/v2/ecad/tools/rules_render.py --check && python3 <repo>/v2/ecad/tools/rules_render.py --requirements --check
python3 <repo>/v2/ecad/tools/decisions_render.py --check && python3 <repo>/v2/docs/handover/layer3/render_l3r2.py --check
python3 <repo>/v2/docs/records/scrub/script_tests.py    # optional: 12 of 12, sandbox under <worktrees>/_scratch/
```

The four redaction commits are reachable from `fnd/scrub` only through the merge; a bundle of the branch
(`git bundle create <file> 8fec0733..fnd/scrub`) carries them. Pushing main publishes them with the reissues. Nothing in
this set touches a board, a netlist, a generator, a registry entry or a verdict class.
