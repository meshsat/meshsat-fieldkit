accepted: yes

# Layer 4, L4-E9: Claude's check of update round 4 at 2661c1ef (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026. Round 4 re-pins L4-E13 after that record's update on set 25's L4-E7R (L4-E13 check 4 at
`33b6b7be`): `f8a328c9` merges it and `2661c1ef` carries the changes.

**Verified by the coordinator:**
- *Reproduction:* `l4e9_power_path.py` re-run at `2661c1ef`, its output equal to the committed `.out` byte for byte. Tests:
  `test_l4e9`, `test_l4e_svg_readers` and `test_public_hygiene` give 42 passed, 0 failed, 1 skipped. The skip is L4-E11's
  reader, whose held sheet is not in this worktree. No em or en dash.
- *The pins:* L4-E13's output and page are re-pinned and its check 4 is newly pinned. The script refuses to run if L4-E13's
  citation of L4-E7R differs from L4-E7R's own output: 2.5485 A, the trip at 3.0468 to 3.7408 A, the 25 V corner at
  73.3436 W, 93.5521 W and 336.6 Wh.
- *The figures in the output's changed lines* are the ones L4-E13 and L4-E7R print: 8.1817, 3.987, 13.82, 3.7408 and 2.9337 A;
  93.5521 and 73.3436 W; 350.0, 336.6 and 52.3 Wh. No new computed figure appears.
- *The two bases are kept apart:*
  - 336.6 Wh where the figure is the accepted stage's (L4-E7R, its output line 734);
  - 350.0 Wh where it is the replay's first-round basis, labelled as such;
  - 240.0 Wh at the conditioned upper corner, unchanged on both bases.
- *2.9337 A against 2.9318 A:* both are L4-E7R's own figures. 2.9337 A is the regulation's highest at 25 V under the joint
  assumptions (the coordination, lines 726 to 730), as L4-E13's A-3(a) quotes it. 2.9318 A is its highest on the hold's corners
  (line 743), as IF-02 carries it. Neither moved.

**The gate is unchanged:** NOT CLOSED on U-01, U-02 and U-04. U-03 is a CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC).
The register holds 139 items.
