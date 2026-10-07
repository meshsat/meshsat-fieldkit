DONE: the K table re-read on main be07863b (K-TABLE-be07863b.md: 7 STANDING, 20 RESOLVED, 1 SUPERSEDED, each with its verbatim evidence); K-16 resolved in record efuse's page; the assessment's section 5 restated as section 11; five apply scripts for set 33 (K-03, K-13, K-15, K-17, K-20, K-21, K-23, K-24), each checked on set 32's files and verified applied in this worktree (then restored); test_l4k. NOT DONE: the apply scripts are not applied on this branch (set 33's); K-22 left STANDING (register task L4A-61); no independent check has read this record. NEXT: the coordinator adopts, edits or rejects; set 33 runs the five scripts and regenerates the outputs named below.

# Record l4k: the DESK-gate assessment's K table re-read on main and its standing contradictions resolved (MESHSAT-1357)

Register task L4A-87 (`_runs/l4ai/REGISTER.draft.md`, draft 2, section 9 item 2; a runner-local file). Worker W131, branch `fnd/l4k`
from main `be07863bbca206a81ab42b9f96a7684c5c10a746`, 7 October 2026 from 04:17 CEST. Record text, a desk task: it closes no cx46
item and upgrades no state (cx46 CORRECTIONS NOT CLOSED; Layer 4's DESK gate NOT PASSED; power-design closure and fabrication
release BLOCKED). Prototype framing: nothing in the kit has been built, bought, powered or measured.

## What is here

| File | What it is |
|---|---|
| `K-TABLE-be07863b.md` | the deliverable (1): each of K-01 to K-28 with its state on `be07863b` and its evidence as `be07863b:<path>:<line>` with the words; findings F-1 and F-2 |
| `_l4k_apply.py` | the one engine of the apply scripts: every check before any write, in-place edits only (no line moves, no table cell added), a partial state refused, a second run exit 3 |
| `apply_l4k_lh12.py` | K-03: LH-12 restated to R-28 (LAYER5-HANDOVER.md) and test_l4e9's one line that held the old text |
| `apply_l4k_p0sol.py` | K-13 and K-23: two sentences of record l4e7's generator l4e7_p0sol.py brought to its pages' reading |
| `apply_l4k_p0list.py` | K-13: the P0 list's quotation of the superseded wording dated, the page's present words beside it |
| `apply_l4k_remeng.py` | K-15, K-17, K-20, K-21: the ledger's section 6 items A, B, C and F dated where their gap was answered |
| `apply_l4k_changelist.py` | K-24: the change-list applier's docstring sentence on route B2 marked as the text of `7070f106` |

Edited on this branch directly (neither file is changed by set 32 nor pinned by any output):
`v2/docs/records/efuse/EFUSE-SETTINGS.md` (K-16: two dated notes inside existing lines) and
`v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md` (deliverable 3: a dated pointer at the end of section 5's first paragraph and
the new section 11 at the end of the file; nothing above it rewritten, no line moved).

## For the integrator: set 33

Run on set 33's integrated tree (after set 32's merge), in any order, each from anywhere:
`python3 v2/docs/records/l4k/apply_l4k_<name>.py [--check]` for lh12, p0sol, p0list, remeng, changelist. Each was checked against the
files of set 32's lineage at `fnd/int32` `4c8196a0` (copied by `git show` into a scratch tree): every old text found once, every
script wrote, and a second run exited 3.

Outputs that move after the applies (named for set 33's regeneration; none regenerated here):
- `v2/docs/records/l5pwr/l5pwr_contracts.out`: the `hand` sha256 line (apply_l4k_lh12.py);
- `v2/docs/records/l4e7/l4e7_p0sol.out`: the two paragraphs' words, its line count unchanged (apply_l4k_p0sol.py; the generator reads
  makers' held curves, and its output is in the l9t5 stability cascade);
- `v2/docs/records/l9t5/l9t5_connected.out`: the sha256 lines of `l4e7_p0sol.py` and `apply_l4e9_changelist_p0.py`, and the cascade
  outputs that pin it;
- once `l4e7_p0sol.out` is regenerated, record l4e9's pin of it (`l4e9_power_path.py` PINS entry `l4e7p0`, printed at
  `l4e9_power_path.out` line 106 on `be07863b`), a tool-moved pin re-pinned by the L4 chain: the verification run found the generator
  refusing there ("l4e9_power_path: v2/docs/records/l4e7/l4e7_p0sol.out is not the pinned file (93cb7485380e7a0c); refusing").
apply_l4k_p0list.py and apply_l4k_remeng.py move no output.

## SESSION decisions (W131; authority SESSION, each with its reversal)

- **S-1, the three states.** STANDING, RESOLVED, SUPERSEDED as defined in the K table's head. Reversed by the coordinator's own
  definitions; the evidence lines stand either way.
- **S-2, apply scripts also for files a shared output pins.** LAYER5-HANDOVER.md, l4e7_p0sol.py's text and the applier's docstring
  are changed through scripts although set 32 does not change two of them, because outputs that set 32 regenerates pin their sha256:
  an edit here would leave those pins stale on this branch and collide with set 32's regeneration. Reversed by running the edits
  by hand on set 33's tree.
- **S-3, in-place edits only.** Every edit keeps its file's line count (an appended sentence inside an existing line, a trailing
  comment on a source line), so no citation by line number anywhere moves. Reversed by none needed; a later set may reflow.
- **S-4, the ledger's items A, B and F dated although their K rows are RESOLVED or SUPERSEDED.** The ledger reports each as a
  current gap in the present tense; the note says where it was answered and keeps the item as history. Reversed by dropping those
  three edits from apply_l4k_remeng.py.
- **S-5, K-22 left STANDING.** Two MODEL readings of the ended rail-trip method from two starting states; the filed check is never
  edited and the ledger already states both and that neither changes a state. Its restatement is register task L4A-61's, after the
  new method (L4A-56, L4A-57). Reversed by the coordinator naming a value to keep.
- **S-6, K-18 RESOLVED by reading.** base_commit and HEAD are two fields with two meanings (the P0 branches' base and the revision
  read); every record names cx45's revision 06077cee. Reversed by the coordinator reading the file otherwise.
- **S-7, K-24's scope.** Only the cited docstring sentence; the applier's data (what it applied at 7070f106) is history and kept;
  any other B2 wording is register task L4A-80's sweep. Reversed by widening L4A-80.
- **S-8, the generator's new words for K-13.** "Independent of E-1, ADDRESSED IN DRAFTS and PROVISIONAL:" (the pages' state words),
  chosen so the paragraph keeps its four printed lines at the generator's 130-column wrap (simulated). Reversed by the pages' fuller
  "ADDRESSED IN DRAFTS, PROVISIONAL, not completed", which prints a fifth line and moves every later line of l4e7_p0sol.out.

- **S-9, K-23's new words keep the annex's quotation.** The supplier validation annex's section 6.4 quotes "Validation: P1-1's S1"
  at `l4e7_p0sol.out` line 403 (held by test_w3annex); the restated sentence keeps those words at that place and adds "rows (a) and
  (b), after the first two are computed as REMAINING ENGINEERING inside E-1". A first wording that dropped them failed test_w3annex
  in the first verification run. Reversed by restating the annex's quotation with set 33.

## Verification (7 October 2026, in this worktree; the applied and regenerated files restored afterwards, none committed)

The 30 modules that read a file this record changes or would change (test_l4e9, test_dgate2, test_entrypage, test_lstat31,
test_recpack, test_w17p0list, test_w7rem, test_w30entry, test_dgate, test_lstat32, test_l9t5, test_remeng, test_w28q40,
test_w11l9t5, test_w3annex, test_w20oneliners, test_w9l9t5, test_w4l4e7, test_w23cite, test_w8l5, test_l4e7, test_l5pwr,
test_applier_state, test_w24l4e9, test_w14l5, test_l4k, test_efuse, test_res31, test_adopt31, test_w18result), run with
`tests/run.py` and the makers' held sheets installed (gitignored, not committed):
- on the branch head `05da9c1a` (before this README's last edit): `tests: 486 passed, 0 failed, 1 skipped` (the skip:
  test_l4e7.t_recompute_reproduces_the_committed_output, "the solver's own re-run: set L4E7_RECOMPUTE=1");
- with the five scripts applied (each exit 0) and `l5pwr_contracts.out` regenerated by `_bin/regen_out.py` (one line moved, the
  `hand` pin): `tests: 484 passed, 2 failed, 1 skipped; failed: test_l4e7.t_p0sol_committed_out_is_what_the_script_prints,
  test_l9t5.t_p0_connected_output_reproduced_pinned_and_every_predicate_holds`, the two outputs named above for set 33;
- then `l4e7_p0sol.out` regenerated by `_bin/regen_out.py` (R1 to R4 held): 10 diff lines, the two paragraphs only, the line count
  unchanged; its quoting readers test_w3annex, test_remeng, test_w4l4e7, test_dgate2 and test_dgate: `tests: 81 passed, 0 failed, 0
  skipped`;
- test_l4e9's restated line holds on the restated LH-12 row and refuses the old one (evaluated on both rows); the old line held on
  both, so it could not tell them apart;
- every apply script checked on the files of `fnd/int32` `4c8196a0` (exit 0), applied there (exit 0) and run again (exit 3).

## Findings

F-1 (record l9stk's 45.88 K/W), F-2 (the register's standing count) and F-3 (FW-A05's off-list against R-28's standby card) are in `K-TABLE-be07863b.md`.
