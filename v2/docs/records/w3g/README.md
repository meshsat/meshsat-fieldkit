# drafts/w3g: what the diagram rebuild could not write itself

Stream w3g (MESHSAT-1357, 27 September 2026) owns `v2/docs/diagrams/` and the diagram reference lines of
`v2/docs/ARCHITECTURE.md`. Everything else it found is here, each with its reason.

| Draft | For | Why it is a draft |
|---|---|---|
| `apply_handover_labels.py` | the handover editor | START-HERE, LAYER-STATUS (the layer 4 row and integrator line), `pack.yaml` and CONTINUATION-BRIEF still say the diagrams were drawn at `e3aedb25`, before round 8, and list their rebuild as remaining; after the rebuild is integrated those lines are wrong. The script edits the seven passages with asserted old text (`--dry-run` passes on `38dcd764`). |
| `finding-pcb-e-fet-symbol.md` | the board E author | board E's six N-channel FETs are drawn with KiCad's P-channel IRF7404 symbol; the fix is in `gen_sch_e.py`, which this stream does not own. |

Not drafted because it is already on record: board A's R74 and R133 with both pins on one net (R4T-F3,
`v2/docs/records/r4t/r4-decisions.md`), which `power_tree.py` now prints on every build.
