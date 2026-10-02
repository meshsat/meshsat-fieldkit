# L4-E11: source-only and dead-pack operation, the vehicle-entry interconnect and the hot swap's fault timer (MESHSAT-1357)

Layer 4 task L4-E11, 2 October 2026, on branch `fnd/l4e11`. Prototype design, desk arithmetic: nothing is bought, built,
powered or measured, and nothing here is applied to the tree.

| File | What it is |
|---|---|
| `L4E11-SOURCE-ONLY-AND-ENTRY.md` | the record: U-04 (the requirement text, the charger's behaviour, the comparison, the selection and its bounds, the owner-question test), D-06 (the band, the selected interconnect classes and ratings, the stiff source again), D-09 (the start recomputed, the timer pair), the interface and firmware drafts, the downstream items, what stays conditional |
| `l4e11_power.py`, `l4e11_power.out` | every figure, read from pinned inputs; the output reproduces byte for byte (`python3 v2/docs/records/l4e11/l4e11_power.py` from the repository root) |
| `apply_gen_sch_e_uvlo.py` | draft: board E's R21 to 42.2k 1 % (U-04's finding U4-F2), after L4-E9's `apply_gen_sch_e_hotswap.py`; release-guarded |
| `apply_gen_sch_e_timer.py` | draft: board E's C5 and C121, two Murata C0G parts on HS_TIMER (D-09); in either order with L4-E9's draft; release-guarded |
| `fetch_held_back.py` | fetches the three makers' sheets held back by their terms (Littelfuse 0997, Murata GRM3195C1H104GA05 and GRM3195C1H683JA05) and checks their sha256 |
| `inputs/` | the filed catalogue readings (LCSC, the JLCPCB search for 150 nF C0G) and the held sheets' provenance |

The tests are `v2/ecad/tools/tests/test_l4e11.py`. No `RELEASE.md` exists: both drafts refuse to write the tree's own generator
until one names an accepted check of this record.
