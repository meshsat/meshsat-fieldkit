MESHSAT-1357 round 6, board B author (r6b), box run 6 (vast.ai 52646493, /root/r6/b/out6, 26 Sep 2026 10:51 to 11:33 UTC).
Generator sha256 6e3d880901fd30306c0fa8bda35a86da6450d7e4bb15217f9cc3225da8d5faef, check_pcb_b.py 28904a37f2f1810399e553f522d73fcc7848afc4d6ce3cce21556bffd70ccd4d.
Script: ../r6b_box6.sh; runner reading: ../r6b_post6.sh. PDFs were not fetched. /root/r6/b was deleted after the fetch.
- tclean/: main faf8c981 as committed: rules_render/decisions_render --check (the reference refusals), assembly_set
  --checklist to a scratch path (equal to the committed page byte for byte), then B regenerated with main's generator.
- committed-*: faf8c981's committed B files; parity_*_committed_tclean.json: main's generator reproduces them.
- t6/: main + the two files: regen/ and v/ (every schematic-phase gate; check_pcb_b with pcbnew on the committed B21
  board as this round, as pass 3 (720892ae) and as committed; fails.*.txt, new_vs_pass3.txt, lost_*.txt).
- tint/: THE INTEGRATION TREE (main + the two files + drafts/sch_pages-popups-r5.patch, B regenerated in place):
  rotation-checklist.diff, docs-rerender.diff (PCB-BRING-UP.md), the render logs, suite.log (1472 passed, 0 failed,
  12 skipped), status-1-before-suite.txt = status-2-after-suite.txt, tint-tracked.diff/.stat, and set/ with set.sha256:
  the files O-18 commits (set/v2/docs/PCB-BRING-UP.md was added after SHA256SUMS was written; its sha256 is
  50b60255cad15c04406fb6f54c315dce527f0f427c5a6c05fca0fc554c724fe6).
- parity_*_t6_tint.json: the O-19 patch changes none of the four artefacts.
- regen_compare_committed_new.json, regen_compare_pass3_new.json: W7's comparator, DIFFERENT as intended.
- check_pcb_b/: runner-side emulation of the gate's net section and the two mutation controls.
SHA256SUMS is the box's list (PDFs and run.log excluded), verified on the runner after the fetch.
