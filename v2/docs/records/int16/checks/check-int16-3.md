mergeable: yes

# Check 3 (delta confirmation) of integration set 15, `fnd/int16` at `e5322674` (MESHSAT-1357)

AI review, labelled as such: an independent check by a Claude session that did not build this integration. It is not a
qualified engineering review. 30 September 2026, 02:22 to 02:26 CEST (read from `date`). Scope: `git diff
4012429e..e5322674` against check 2's R1 and minors. Everything below is what I read or ran myself, in a shared clone
`_scratch/chk-int16c` with `archives/int16-evidence-e5322674.tar` extracted (`git status` clean after extraction), now
removed. No commits to real branches, no pushes, no box.

`fnd/int16` = `e53226748d88`, one commit on `4012429e`, 6 files.

## Blocking

None.

## Minors

1. Carried from check 2 (minor 3, cosmetic): S-125's title keeps one long YAML line, 197 characters at
   `pcb_requirements.yaml` line 3609. It parses and renders.

## Check 2's items

* **R1: answered.**
  * `records/w5identc/readings/check-board-c-b874b744.json` hashes to `29840bee91216e59`. S-125 in
    `pcb_requirements.yaml` and its row in REQUIREMENTS-TRACE.md both name `sha256 29840bee91216e59`, and neither file
    still carries `42ce2b3ea2c1a406`.
  * Both read "decision 59, written by apply_decision_decoded.py".
  * `apply_check16b_fixes.py` reads the sha from the file (it does not type it in) and refuses a second run.
* **Replay.** Replayed on `4012429e`, the script followed by `rules_render.py --requirements` reproduces every changed
  file of `e5322674`. The only files left over are the script itself and the filed check 2.
* **Minor 1: answered.**
  * Neither `apply_check16_fixes.py` nor the new script carries a literal U+2013 or U+2014. In both, the strings that
    match TI's row hold the en dash only through the backslash u2013 escape; parsed, they still carry it at run time.
  * No added line of the commit has a dash, and none of the whole set's added lines (`2f0b034a..e5322674`) has one
    either.
* **Minor 2: answered.** README step 4 names `apply_decision_decoded.py` (decision 59 and CFL-016's rebind) and
  `apply_identities_c.py` (S-125).
* **Filing: done.** `records/int16/checks/check-int16-2.md` is byte identical to my CHECK-2.md.

## Also confirmed

* **Validators.** 0 errors on all five:
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings;
  * `rules_lib.py`: 59 rules, 0 errors, 0 warnings;
  * `rules_render.py --check`: 16 documents, 0 out of date;
  * `rules_render.py --requirements --check`: current;
  * `decisions_render.py --check`: rc 0.
* **Bindings.** All `evidence_bound_to` bindings match their files.
* **Full render order.** `rules_render.py --requirements`, `rules_status.py` x3, `rules_render.py` x2: CURRENT-EVIDENCE.md
  reads `c9b98931` at every step and `git status` is clean. CON-010 and REQ-044 are both bound to
  `CURRENT-EVIDENCE.md@c9b98931fd7cb960`. `rules_lib.py requirements` then reads 0 warnings.
* **Tests.** `tests/run.py requirement close claims decisions identit`: 175 passed, 0 failed, 2 skipped (no pcbnew).
* **Text.** The added lines carry no host name or user path.
* **Commit identity.** The commit is authored and committed by Kyriakos Papadopoulos <ncpjfuzl@mxmx.email>, with no
  trailer.
* **Box suite.** The box result on `e5322674` is the coordinator's and was still running. I did not see it.

## Counts

Blocking 0. Minors 1 (carried, cosmetic). Check 2's items: R1 and minors 1 and 2 answered, check 2 filed byte identical.
Replay: 1 script, identical. Test runs: 175/0/2. Render order: stable at `c9b98931`.
