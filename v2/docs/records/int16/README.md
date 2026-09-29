# Integration set 15 (MESHSAT-1357, branch `fnd/int16`, 29 and 30 September 2026)

Prototype design: nothing is bought, built or measured. The integrating session's records for set 15, on main `2f0b034a`
(set 14's milestone).

| Step | Commit or file | What it did |
|---|---|---|
| 1 | `apply_hold_back_panjit.py`, `fetch_held_back.py` | PANJIT's SS2020FL series sheet held back from the public tree by its terms (page 4: reproduction prohibited without permission): untracked, moved to the ignored `v2/vendor/power/held/`, cited by URL and sha256 `92544a83...`, fetched by `fetch_held_back.py` |
| 2 | merge of `fnd/w5identc` | board C's part identities (21 printed, 23 decoded under decision 59, 41 unresolved with reasons, 2 not a part), checked three times |
| 3 | `apply_panjit_path_w5identc.py` | the identity table rebuilt against the held path |
| 4 | `records/w5identc/apply_identities_c.py` | decision 59 recorded, CFL-016 rebound, S-125 opened |
| 5 | merge of `fnd/s122c` (`b1fb815f`) | stream s122 rounds 4 to 8, the definition documents re-read against the netlists, checked eight times (`records/s122/checks/`) |
| 6 | `records/s122/apply_registry_s122_r4.py`; `apply_rebind_page_set15.py` | five records rebound, S-126 opened (PROCESS), S-122's outputs re-run on the decisions pin, CON-010 and REQ-044 rebound to the page |
| 7 | `records/s122/checks/check-s122-8.md`; `records/s122/close_s122.py` | S-122 closed by its filed closing check; CFL-016 from FAIL to PASS |
| 8 | `apply_rebind_page_set15b.py` | CON-010 and REQ-044 rebound after the closure to the page the full render order reaches |
| 9 | `checks/check-int16-1.md` | the set's integration check (an AI check): mergeable no, B1 and B2 and nine minors |
| 10 | `apply_panjit_held_w5identc.py` | B1 and B2: the three PANJIT bindings marked held back, the table rebuilt, the reading re-pinned, BOARD-C-SELECTIONS.md re-rendered |
| 11 | `apply_check16_fixes.py` | minors 6 and 8 (minor 7 is recorded below) |

**The check's minors, and where each is answered.** m1: the first page entry (step 6) says "the re-take's evidence
installed" beside "no reading re-taken in this set"; read it as set 14's evidence archive installed (no reading of this
set was re-taken). The page the full order reaches after the closure (step 8) is `c9b98931`, the same page as set 14's:
the set's changes moved the page only while one status pass lagged a configuration change (the check found a lag of one
pass, not a cycle; the integrator's rule since: bind only after the full order, render with requirements, status three
times, render twice, has run twice with the same page). m2: this README and the index rows in `records/README.md`.
m3: stream w5identc's third check, the accepting one, is filed as `records/w5identc/checks/check-w5identc-3.md`. Its
minor 4 notes that the filed `check-w5identc-2.md`, minor 4, names a path that the stream's scrub rewrote, so that
sentence is not true as filed; the finding it stated is answered (check 3 says so), and the filed bytes are kept as
filed. m4: the four UNRESOLVED "far" rows of board C's table (Fenghua twice, Arlitech L1, Uniroyal CS03) give reasons
that cite documents absent from this tree, typed into `build_table.py` rather than asserted, and read from `fnd/w5ident`
`c08f4d5a`, which is on no remote; the check read the four sheets and found the facts true. Carried by S-125 (board C's
identities): file the three sheets whose terms allow it (Arlitech, Fenghua, Murata; the Uniroyal CS03 sheet reads "All
rights reserved" and is held back), then bind each row or keep it UNRESOLVED with an openable document. m5: the vendor
scan reading names the PANJIT sheet's old path; it is not re-run here (429 PDFs) and is carried with m4. m6 and m8:
`apply_check16_fixes.py`. m7: decision 59's ask says "20 part numbers"; the check counts 20 identities of 14
distinct part numbers, which is the correct statement. It is not edited here, because `tools/pcb_decisions.yaml` is the
file CFL-016's reading and S-122's outputs are bound to (an edit made CFL-016's reading stale); the correction is
carried to the next change of that file. m9: cosmetic, not changed.
