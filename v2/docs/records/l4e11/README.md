# L4-E11: source-only and dead-pack operation, the vehicle-entry interconnect and the hot swap's fault timer (MESHSAT-1357)

Layer 4 task L4-E11, 2 October 2026, on branch `fnd/l4e11`, with its fix round of the same day. Prototype design, desk
arithmetic: nothing is bought, built, powered or measured, and nothing here is applied to the tree.

| File | What it is |
|---|---|
| `L4E11-SOURCE-ONLY-AND-ENTRY.md` | the record: U-04 (the requirement text, the charger's behaviour, the entry at a 9.00 V plug and its replacement, the kit's own losses, the corrected knee and guard, the functional warm-up, the source envelope at the plug, the comparison, the selection, the rules with R-a as a state table, the owner-question test), D-06 (the monotone envelope, the selected interconnect classes and obligations, the interconnect by its resistance, the stiff source again), D-09 (the start recomputed, the timer pair, for the LM5069), the interface and firmware drafts, the downstream items, what stays conditional |
| `l4e11_power.py`, `l4e11_power.out` | every figure, read from pinned inputs; the output reproduces byte for byte (`python3 v2/docs/records/l4e11/l4e11_power.py` from the repository root) |
| `apply_gen_sch_e_entry.py` | draft (fix round): board E's entry with the TPS48110-Q1, a CSD19536KTT pass FET, R19 4.5 mOhm, L2 SRF1260-1R0Y and their network (U-04's B1), after L4-E9's `apply_gen_sch_e_hotswap.py` and instead of the timer draft; two footprints owed (E11-01); release-guarded |
| `apply_gen_sch_a_guard.py` | draft (fix round): board A's R14 to 76.8k, the restart guard under the corrected knee (U-04's B3), applied with the knee (E11-09); release-guarded |
| `apply_gen_sch_e_timer.py` | draft: board E's C5 and C121, two Murata C0G parts on HS_TIMER (D-09), the alternative to the entry draft while the LM5069 stays; in either order with L4-E9's draft; release-guarded |
| `fetch_held_back.py` | fetches the six makers' sheets held back by their terms (Littelfuse 0997, Murata GRM3195C1H104GA05 and GRM3195C1H683JA05, TI TPS4811-Q1, CSD19536KTT and TPS1663) and checks their sha256 |
| `inputs/` | the filed catalogue readings (LCSC, the JLCPCB search for 150 nF C0G) and the held sheets' provenance |
| `checks/astra-check-l4e11-1.md` | The collaborator's focused check of round 1 (job cx30-l4e11-check, run 20261002T024127Z-317909, on `3f9cf283`), filed as returned: NOT YET, blockers B1 (the UVLO's equations and POREN), B2 (the charge holds), B3 (the source bounds and a functional acceptance), B4 (the weak-source envelope), B5 (the charge bounds) and three minors; the fix round answers it |

The first round's `apply_gen_sch_e_uvlo.py` (R21 42.2k) is withdrawn by the fix round: it placed the LM5069's UVLO hysteresis
on the wrong edge, and no divider can make the LM5069 start from a 9.00 V plug (section 3a). The tests are
`v2/ecad/tools/tests/test_l4e11.py`. No `RELEASE.md` exists: every draft refuses to write the tree's own generator until one
names an accepted check of this record.
