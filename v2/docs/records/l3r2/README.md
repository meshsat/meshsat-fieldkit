# l3r2: layer 3's second issue, the requirements for the current target (MESHSAT-1357)

Branch `fnd/l3r2`, 30 September 2026, on the owner's instruction of that day and his review of the draft decision table
(`v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md`, owner rulings D-21 and D-22). **Prototype design: no V2 board
has been fabricated, ordered, assembled or powered, and no kit has been field deployed.** AI work, not a qualified review.
The deliverables are the pages of `v2/docs/handover/layer3/`; this folder holds the scripts that change the registry and
the layer status page, the prepared scripts for the owner's answers, and the independent checks of L3-R2.

**Round 2** (after the first independent check, `checks/check-l3r2-1.md`, accepted: no, and D-22): the branch was
re-run on integration set 15's line `fnd/int16` at `4012429e` (S-122 closed there); the first round's commits stay on
the local branch `fnd/l3r2-r1` (`9c26a641`). The first round's SC-76 is withdrawn: the charge bus is an engineering
input, carried by open item S-127 (the energy basis, stream l3plane, then its independent check), and rows L3-OD1,
L3-OD2 and L3-OD4 are held until it is filed.

## Files

| File | What it is |
|---|---|
| `l3edit.py` | the registry's text-level editing helpers: an entry found by id (optionally inside one top-level list), a field by name, folded text written at the registry's width, every added text screened for dash characters and claim words, the result re-parsed and validated |
| `apply_l3r2_session.py` | the session's closures, applied once (a second run refuses): D-21 and D-22 recorded; S-114 closed by commit `1b9f543c`, its evidence qualified by the model's 20.7 V bus; the energy basis opened as the next free S item (S-127 on set 15), which REQ-072 waits on, and REQ-072 given a qualifying evidence entry; M-02 and S-53 restated; CFL-006 re-read; CFL-002 corrected; seven acceptances made measurable (REQ-008, REQ-012, REQ-029, REQ-054 with its 27 dBm allowance kept, REQ-057, REQ-068, CHO-003); a header paragraph. Every document sentence it writes is asserted in the document first |
| `read_cfl006.py`, `read_cfl006.out` | the re-read of CFL-006's four bound files, fact by fact (exit 0 only if every fact holds) |
| `apply_layer_status_l3.py` | `v2/docs/handover/LAYER-STATUS.md`: the head sentence, layer 3's section restated with its H2 and H3 text kept word for word, the L3-R2 step of appendix A.3's integrator line; it refuses unless S-122 is closed and D-22 is in the registry |
| `apply_records_readme_row.py` | DRAFT for the integrator: this folder's row in `v2/docs/records/README.md`, after the `s119/` row; not run in the branch |
| `conditional/cond.py`, `od_l3_1.py` to `od_l3_5.py` | PREPARED, NOT APPLIED: the exact registry change each answer of the owner to rows L3-OD1 to L3-OD5 makes. Each takes `--option`, the owner's own `--words` and `--date`, records an owner ruling carrying `decides: <row>:<option>`, applies its edits by id and asserted text, closes M-02 once rows 1 to 4 are decided with row 1 approved, and validates; `--check` writes nothing. Coherent by construction: row L3-OD1 fixes the store only, row L3-OD3 alone fixes the array, row L3-OD4 adopts a band only on 2S2P, and a row whose prerequisites fail is refused. Rows L3-OD1, L3-OD2 and L3-OD4 refuse to write the tree's registry while `l3r2.yaml`'s `energy_basis` is not filed (D-22); `qmx-outside` also waits on `relocation_facts` |
| `dryrun.py`, `dryrun.out` | every chain of the prepared scripts run on copies of the registry, the incoherent ones refused; the band and the keep figures come from a fixture standing in for the energy basis |
| `checks/check-l3r2-1.md` | the first independent check of L3-R2 (an AI check, accepted: no), filed byte for byte; its items are answered in round 2 |

The renderer is `v2/docs/handover/layer3/render_l3r2.py` (with `l3r2.yaml` and `h3_registry_digest.json` beside it); its
tests are `v2/ecad/tools/tests/test_l3r2.py`.

## Preconditions

- The set carries S-122's closure (`845a4fd1` or later) and D-20; `apply_layer_status_l3.py` refuses otherwise.
- The branches `fnd/e200c`, `fnd/e200r` and `fnd/e200r2` resolve in the repository, as local refs or as `origin/` refs:
  `apply_l3r2_session.py` asserts that board E's 200 W stage exists only on them, unmerged. In a clone that carries
  neither, create the local refs at `14c0c343`, `3fa7f4ff` and `e5e8a6ba`.
- The set's ignored evidence is installed (the suite's readings); the scripts themselves read only tracked files.

## Run order on the integration set (the integrator)

From the repository root. If the set is `fnd/l3r2` itself (it is re-run on `4012429e`), only the renders and the tests
remain; otherwise take the branch's own files and run the scripts on the set:

```
git checkout fnd/l3r2 -- v2/docs/handover/layer3 v2/docs/records/l3r2 v2/ecad/tools/tests/test_l3r2.py
python3 v2/docs/records/l3r2/read_cfl006.py > v2/docs/records/l3r2/read_cfl006.out
python3 v2/docs/records/l3r2/apply_l3r2_session.py --check && python3 v2/docs/records/l3r2/apply_l3r2_session.py
python3 v2/docs/records/l3r2/apply_layer_status_l3.py --check && python3 v2/docs/records/l3r2/apply_layer_status_l3.py
python3 v2/docs/records/l3r2/apply_records_readme_row.py
env -C v2/ecad/tools python3 rules_lib.py requirements
env -C v2/ecad/tools python3 rules_render.py --requirements
python3 v2/docs/handover/layer3/render_l3r2.py && python3 v2/docs/handover/layer3/render_l3r2.py --check
python3 v2/docs/records/l3r2/dryrun.py > v2/docs/records/l3r2/dryrun.out
env -C v2/ecad/tools/tests python3 run.py test_requirements test_l3r2
```

The renderer lists any open item the set adds as UNCLASSIFIED (closure item L3-C23 then reads OPEN) until `l3r2.yaml`'s
`open_items_layer` gives it a layer.

## When the energy basis arrives

1. File stream l3plane's `ENERGY-BASIS.md` and its independent check; name both in `l3r2.yaml`'s `energy_basis` (record,
   sha16, check, check_sha16). Close S-127 by commit with REQ-072 re-read on the basis.
2. Restate rows L3-OD1, L3-OD2 and L3-OD4 in `l3r2.yaml` from it (their energy cells, the case names in place of the
   first draft's words, the recommendations), and finding F-01.
3. Write `od_l3_4.py`'s `BAND` table from the basis (with U3's bracket at the supply range's low end), and file the
   relocation facts in `l3r2.yaml`'s `relocation_facts`.
4. Re-render; hold a further independent check; present the table to the owner.

## Applying an owner's answer (only once he has answered, and only rows the hold no longer holds)

```
python3 v2/docs/records/l3r2/conditional/od_l3_N.py --option <option> --words "<his words>" --date <YYYY-MM-DD> [row extras]
env -C v2/ecad/tools python3 rules_lib.py requirements
env -C v2/ecad/tools python3 rules_render.py --requirements
python3 v2/docs/handover/layer3/render_l3r2.py
```

Row extras: row L3-OD3 `keep` takes `--array-wp`, `--entry-a` and `--evidence` from the checked basis; row L3-OD4 `adopt`
takes `--push-n` (the owner's number) and, until the `BAND` table is written, `--band` and `--band-evidence`. Row L3-OD2
needs row L3-OD1 approved; row L3-OD3 needs row L3-OD1 approved; row L3-OD4 needs rows L3-OD1 to L3-OD3 (adopt: L3-OD3
answered 2s2p); row L3-OD5 needs nothing. After the rows are decided, the CONOPS and product brief passages
`L3-RECONCILIATION.md` lists are prepared for the owner's approval and named in `l3r2.yaml`'s `definition_reissue`
(closure item L3-C26), and a further independent check of L3-R2 is held and named in `independent_check` (L3-C27).
