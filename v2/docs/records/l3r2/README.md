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

**Round 3** (30 September 2026): the first check of stream l3plane's energy basis (`checks/energy-basis-check-1/`,
accepted: no) is filed here, and the four facts it confirmed are used as `l3r2.yaml`'s CF-01 to CF-04 (the charge bus's
range, board A as generated, the September weather record, the relocation facts); no figure of its cases WE, WE60 or WA
is used. The owner's instruction on the six-row table is recorded as D-23 (`apply_l3r2_d23.py`): row L3-OD6 (M1's
weather basis) is added as a quantified choice between the average-day benchmark and historical-coverage targets, its
recommendation and figures held for the checked basis; every row carries its options (an option that cannot meet M1
flagged plainly; row L3-OD2 gains `both-kept`), recommendation, quantified consequences with the evidence linked, and
dependencies; board A's R11 is carried as two results (the held circuit and the drafted 6.2 mOhm), its implementation
and physical verification tracked as two downstream closure items.

## Files

| File | What it is |
|---|---|
| `l3edit.py` | the registry's text-level editing helpers: an entry found by id (optionally inside one top-level list), a field by name, folded text written at the registry's width, every added text screened for dash characters and claim words, the result re-parsed and validated |
| `apply_l3r2_session.py` | the session's closures, applied once (a second run refuses): D-21 and D-22 recorded; S-114 closed by commit `1b9f543c`, its evidence qualified by the model's 20.7 V bus; the energy basis opened as the next free S item (S-127 on set 15), which REQ-072 waits on, and REQ-072 given a qualifying evidence entry; M-02 and S-53 restated; CFL-006 re-read; CFL-002 corrected; seven acceptances made measurable (REQ-008, REQ-012, REQ-029, REQ-054 with its 27 dBm allowance kept, REQ-057, REQ-068, CHO-003); a header paragraph. Every document sentence it writes is asserted in the document first |
| `read_cfl006.py`, `read_cfl006.out` | the re-read of CFL-006's four bound files, fact by fact (exit 0 only if every fact holds) |
| `apply_l3r2_d23.py` | the owner's instruction on the six-row table recorded as owner ruling D-23, applied once (a second run refuses); every quote asserted in `OWNER-INSTRUCTION-2026-09-30.md` first; no record changes |
| `apply_layer_status_l3.py` | `v2/docs/handover/LAYER-STATUS.md`: the head sentence, layer 3's section restated with its H2 and H3 text kept word for word, the L3-R2 step of appendix A.3's integrator line; it refuses unless S-122 is closed and D-22 is in the registry |
| `apply_layer_status_l3_r3.py` | round 3: the same page's layer 3 sentences brought to D-23, row L3-OD6 and the confirmed facts, each sentence replaced by its own text; it refuses unless `apply_layer_status_l3.py` has run and D-23 is recorded, and a second run is refused |
| `apply_records_readme_row.py` | DRAFT for the integrator: this folder's row in `v2/docs/records/README.md`, after the `s119/` row; not run in the branch |
| `conditional/cond.py`, `od_l3_1.py` to `od_l3_6.py` | PREPARED, NOT APPLIED: the exact registry change each answer of the owner to rows L3-OD1 to L3-OD6 makes. Each takes `--option`, the owner's own `--words` and `--date`, records an owner ruling carrying `decides: <row>:<option>`, applies its edits by id and asserted text, closes M-02 once rows 1 to 4 are decided with row 1 approved, and validates; `--check` writes nothing. Coherent by construction: row L3-OD1 fixes the store only, row L3-OD3 alone fixes the array, row L3-OD4 adopts a band only on 2S2P, and a row whose prerequisites fail is refused. Rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6 refuse to write the tree's registry while `l3r2.yaml`'s `energy_basis` is not filed (D-22, D-23); `qmx-outside` also waits on `relocation_facts`. Row L3-OD4 adopts no band for `both-kept` nor beside a coverage target; row L3-OD6's `coverage` reads its figures only from the row's filled table and records an open conflict where the store does not fit; `both-kept` records one against REQ-072; `od_l3_1.py` carries a coverage target over when it restates REQ-072 |
| `dryrun.py`, `dryrun.out` | every chain of the prepared scripts run on copies of the registry, the incoherent ones refused; the band, the keep figures and the coverage figures come from fixtures standing in for the energy basis |
| `checks/check-l3r2-1.md` | the first independent check of L3-R2 (an AI check, accepted: no), filed byte for byte; its items are answered in round 2 |
| `checks/energy-basis-check-1/` | the first independent check of stream l3plane's energy basis (branch `fnd/l3plane` at `6a283b25`; an AI check, accepted: no), its report `CHECK-1.md` and its own tools and outputs, filed byte for byte so that the facts CF-01 to CF-04 cite a file in the tree; its blocking items are the stream's to answer in its second round. Its tools read a checkout of that branch with its held files; they are not run here |

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
python3 v2/docs/records/l3r2/apply_l3r2_d23.py --check && python3 v2/docs/records/l3r2/apply_l3r2_d23.py
python3 v2/docs/records/l3r2/apply_layer_status_l3.py --check && python3 v2/docs/records/l3r2/apply_layer_status_l3.py
python3 v2/docs/records/l3r2/apply_layer_status_l3_r3.py --check && python3 v2/docs/records/l3r2/apply_layer_status_l3_r3.py
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
2. Restate rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6 in `l3r2.yaml` from it (their consequences, the R11 table's
   conditional column, the case names in place of the first draft's words, the recommendations), and finding F-01.
3. Write `od_l3_4.py`'s `BAND` table from the basis (with U3's bracket at the supply range's low end); fill row
   L3-OD6's `quantified.rows` (usable Wh, nominal Wh, mass, volume, fits, evidence with its section) from the basis; and
   file in `relocation_facts` a record that establishes the QMX's place outside the case, if one is ever written.
4. Re-render; hold a further independent check; present the table to the owner.

## Applying an owner's answer (only once he has answered, and only rows the hold no longer holds)

```
python3 v2/docs/records/l3r2/conditional/od_l3_N.py --option <option> --words "<his words>" --date <YYYY-MM-DD> [row extras]
env -C v2/ecad/tools python3 rules_lib.py requirements
env -C v2/ecad/tools python3 rules_render.py --requirements
python3 v2/docs/handover/layer3/render_l3r2.py
```

Row extras: row L3-OD3 `keep` takes `--array-wp`, `--entry-a` and `--evidence` from the checked basis; row L3-OD4 `adopt`
takes `--push-n` (the owner's number) and, until the `BAND` table is written, `--band` and `--band-evidence`; row L3-OD6
`coverage` takes `--share N`, one of the row's filled targets, and `mean-day` optionally `--stat` and `--stat-evidence`.
Row L3-OD2 needs row L3-OD1 approved; row L3-OD3 needs row L3-OD1 approved; row L3-OD4 needs rows L3-OD1 to L3-OD3
(adopt: L3-OD3 answered 2s2p, L3-OD2 not both-kept, L3-OD6 not coverage); rows L3-OD5 and L3-OD6 need nothing. After the rows are decided, the CONOPS and product brief passages
`L3-RECONCILIATION.md` lists are prepared for the owner's approval and named in `l3r2.yaml`'s `definition_reissue`
(closure item L3-C26), and a further independent check of L3-R2 is held and named in `independent_check` (L3-C27).
