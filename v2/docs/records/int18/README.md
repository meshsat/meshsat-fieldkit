# Integration set 17 (MESHSAT-1357, branch `fnd/int18`, 30 September 2026)

Prototype design: nothing is bought, built or measured. The integrating session's records for set 17, on main
`8fec0733` (set 16's milestone and its follow-up).

| Step | Commit | What it did |
|---|---|---|
| 1 | `96692afc` | merge of `fnd/scrub` at `5899d7c7`: the public-file cleanup (171 hits in 71 files to 22 in 14), snapshots H1, H1.1, H2 and H3 reissued as H1-R1, H1.1-R1, H2-R1 and H3-R1 with the originals untouched, the guard test; no history rewrite (`records/scrub/`, checked twice, the second check filed with the stream) |
| 2 | `ca4f4f9f` | merge of `fnd/l3r4` at `e8e3ef57`: the L3-C26 preparation (the passage map of CONOPS and PRODUCT-BRIEF per row and option, the re-issue generator that runs only on decided rows and never writes a baselined file, LAYER-STATUS layer 3 brought current) |
| 3 | `1f34bf92` | merge of `fnd/l3r4` round 4d at `a547fe1d`: the pack and cell passage lists complete by pattern, the link tests on copies only |
| 4 | `checks/check-int18-1.md` | the set's integration check (an AI check): mergeable, one minor (the l3r4 stream's four checks filed in the tree: done in `records/l3r4/checks/`) |
