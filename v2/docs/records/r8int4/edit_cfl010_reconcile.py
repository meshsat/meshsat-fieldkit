"""V2-SPEC correction 28 (main's board B round 8) and line 41, and the brief's SIM row, reconciled with CFL-010 being
resolved on correction 22's description (registry writer, Review B finding B6) and with round 8 drawing the SIM TVS
array (verify c23, first new contradiction). Run from the worktree root."""
def sub(t, a, b, n=1):
    assert t.count(a) == n, (t.count(a), a[:100]); assert a != b
    return t.replace(a, b)
p = 'v2/docs/V2-SPEC.md'; t = open(p).read()
t = sub(t, """    for, on board B's schematic (board B's SIM TVS constraint in the registry, read FAIL until it is drawn), and the
    eSIM variant's order code""", """    for, on board B's schematic (board B's SIM TVS constraint in the registry, drawn since board B's round 8, correction
    28), and the eSIM variant's order code""")
t = sub(t, """two locating holes of TE drawing C-2199119 rev F sheet 3 (S-12), and each SIM holder carries a TI TPD4E001 (1.5 pF,
    the TVS half of S-13 and correction 22; the eSIM variant's order code is still owed, so CFL-010 stays open). Nothing
    is built.""", """two locating holes of TE drawing C-2199119 rev F sheet 3 (S-12), and each SIM holder carries a TI TPD4E001 (1.5 pF,
    board B's SIM TVS constraint of correction 22). The eSIM variant's order code is still owed (open item S-13, the
    components layer's); it is not part of conflict CFL-010, which the requirements registry resolves on correction 22's
    description. Nothing is built.""")
t = sub(t, "and the eSIM variant's order code is owed (open item S-13, conflict CFL-010) |",
        "and the eSIM variant's order code is owed (open item S-13; conflict CFL-010 is resolved on this description, correction 22) |")
open(p, 'w').write(t)
p = 'v2/docs/PRODUCT-BRIEF.md'; t = open(p).read()
t = sub(t, "| The description is settled (SC-13); the TVS array is board B's schematic work (layer 8) and the variant's code is a procurement item for an eSIM build only. |",
        "| The description is settled (SC-13) and CFL-010 is resolved on it; the TVS array is drawn on board B since its round 8 (`V2-SPEC.md` correction 28), and the variant's code is a procurement item for an eSIM build only (S-13). |")
open(p, 'w').write(t)
print("edit_cfl010_reconcile: V2-SPEC 3 edits, PRODUCT-BRIEF 1 edit")
