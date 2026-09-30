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

**Round 3b** (30 September 2026), on the scoped check CHECK-2 of L3-R2 (accepted so far: no), the energy basis's second
check (`checks/energy-basis-check-2/`, accepted: yes, of `fnd/l3plane` `ec415c09`) and the owner's addendum D-24 and
corrections D-25 (both recorded by their own scripts, quoted in `OWNER-INSTRUCTION-2026-09-30.md`):
- B1: row L3-OD4's adopt requires row L3-OD6 answered mean-day first; an undecided row L3-OD6 refuses it.
- B2: row L3-OD6's table carries the basis's figures per build case (TYP, WAB) and which lids carry each; the lid of row
  L3-OD2 must carry the answer's store (od_l3_6.py and od_l3_2.py record an open conflict otherwise, and the gate reads
  the set incoherent; an unfilled fit is incoherent too). L3-C32 and LAYER-STATUS say exactly what is enforced.
- B3: the hold and the gate verify the energy basis's check (its file at its sha, first line "accepted: yes") and a
  definition re-issue's own approving ruling (`decides: definition_reissue`, dated after the rows; D-21 does not qualify;
  the baselined text does not count).
- B4: fact CF-01, F-01 and LAYER-STATUS state the bus's steady-state range with its brackets (19.101, 18.782, 18.738 V).
- The minors: the QMX-outside lead named as an enclosure constraint; row L3-OD6's hold cites D-23; no "recommended" chain;
  REQ-072's older wording qualified by a new evidence entry and REQ-054's gain named in dBd (`apply_l3r2_r3b.py`); the
  pass line change named in row L3-OD1; figures and bands bind exactly, and on the tree only to the filed basis.
- D-24 and D-25: board A's front end in four cases (as drawn; a derated variant, coordination only; the resistor-only
  proposal, conditional; a hypothetical corrected power path, with its implementation requirements and corrections
  PP-01 to PP-08 as downstream closure items L3-C37 to L3-C44); rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6 also wait on the
  power path's independent check (`power_path_check`, L3-C45); every row names the requirement it changes with the
  consequence quantified; Kelvin sensing is an implementation requirement.
- Prepared for the fill, not run: `basis_reader.py`, `set_energy_basis.py`, `fill_l3r2_from_basis.py` (below).

**Round 3c** (30 September 2026), on the narrow check CHECK-3 of L3-R2 (accepted so far: no; it closes CHECK-2 and
confirms D-24 and D-25):
- B1: an accepted check is bound to the files filed. `basis_binding.py` compares every named file with `git show
  <tip>:<path>` of the tip the check names; `set_energy_basis.py` refuses a file that differs, and the hold and the gate
  verify it again every time, for `energy_basis` and `power_path_check` alike. The check's failing path (the third
  issue's files with the second issue's check) is a test.
- The reader covers `three_cases.out` (the four front-end cases and their coverage, and the derated setting) at the
  fourth issue's format (`06b8ecea`), every table checked whole; `fill_l3r2_from_basis.py` fills `four_cases` from it and
  row L3-OD1's four-case cells are rendered from that by exact keys.
- The minors: the history of stream r11dep's record stated as it is; REQ-072's prepared acceptance names the steady-state
  range with the brackets beside the result; PP-02's bench threshold (0.29 mOhm x I at 25 C); LAYER-STATUS's integrator
  line and the impacts table (`apply_layer_status_l3_r3c.py`); the REQ-015 owner case in figures (`conditional_owner_cases`).
- Prepared, not run: `prepared/power_path_classes.yaml` and `restate_power_path.py` restate the power-path list from the
  second issue's classes (A-1 and A-2, B-1 to B-5, C-1 to C-9) once `power_path_check` is filed and verified.

## Files

| File | What it is |
|---|---|
| `l3edit.py` | the registry's text-level editing helpers: an entry found by id (optionally inside one top-level list), a field by name, folded text written at the registry's width, every added text screened for dash characters and claim words, the result re-parsed and validated |
| `apply_l3r2_session.py` | the session's closures, applied once (a second run refuses): D-21 and D-22 recorded; S-114 closed by commit `1b9f543c`, its evidence qualified by the model's 20.7 V bus; the energy basis opened as the next free S item (S-127 on set 15), which REQ-072 waits on, and REQ-072 given a qualifying evidence entry; M-02 and S-53 restated; CFL-006 re-read; CFL-002 corrected; seven acceptances made measurable (REQ-008, REQ-012, REQ-029, REQ-054 with its 27 dBm allowance kept, REQ-057, REQ-068, CHO-003); a header paragraph. Every document sentence it writes is asserted in the document first |
| `read_cfl006.py`, `read_cfl006.out` | the re-read of CFL-006's four bound files, fact by fact (exit 0 only if every fact holds) |
| `apply_l3r2_d23.py` | the owner's instruction on the six-row table recorded as owner ruling D-23, applied once (a second run refuses); every quote asserted in `OWNER-INSTRUCTION-2026-09-30.md` first; no record changes |
| `apply_l3r2_d24.py`, `apply_l3r2_d25.py` | the owner's addendum on the power path (D-24) and his corrections to round 3b (D-25), each recorded once as the pattern of `apply_l3r2_d23.py`, every quote asserted in `OWNER-INSTRUCTION-2026-09-30.md`; no record changes |
| `apply_l3r2_r3b.py` | round 3b's session closures, applied once: REQ-072 gains a qualifying evidence entry for the s119 entry's 'typical' and 'adverse' (history not edited), and REQ-054's acceptance names the antenna's gain in dBd (the limits are ERP) |
| `apply_layer_status_l3.py` | `v2/docs/handover/LAYER-STATUS.md`: the head sentence, layer 3's section restated with its H2 and H3 text kept word for word, the L3-R2 step of appendix A.3's integrator line; it refuses unless S-122 is closed and D-22 is in the registry |
| `apply_layer_status_l3_r3.py` | round 3: the same page's layer 3 sentences brought to D-23, row L3-OD6 and the confirmed facts, each sentence replaced by its own text; it refuses unless `apply_layer_status_l3.py` has run and D-23 is recorded, and a second run is refused |
| `apply_layer_status_l3_r3b.py` | round 3b: the page's coherence sentence says what is enforced, F-01 carries the bus's brackets and board A's front end in four cases, and the rows wait on the power path's check too; refuses unless round 3 ran and D-24 and D-25 are recorded |
| `basis_binding.py` | binds a filed record, its outputs and its accepted check to the tip the check checked (`git show <tip>:<path>`, byte identical), for the hold, the gate and `set_energy_basis.py` |
| `restate_power_path.py`, `prepared/power_path_classes.yaml` | PREPARED, NOT RUN: the power-path list restated from the checked classes of stream r11dep's second issue, every anchor asserted in the filed record; refuses until `power_path_check` is verified, and a second run |
| `apply_layer_status_l3_fill.py` | the fill: the page's layer 3 states the checked basis at `cd8720a1` and its result; refuses unless both checked files are named and verified |
| `apply_layer_status_l3_r3c.py` | round 3c: the integrator line says what the scripts enforce, and F-01 states the history of stream r11dep's record |
| `basis_reader.py` | reads the filed energy basis's outputs by exact keys (weather_basis.out A and B, energy_basis.out 5), each figure as the text the output prints; refuses any other format (written for the basis's third issue, `868c321f`) |
| `set_energy_basis.py` | PREPARED, NOT RUN: names the basis, its outputs and its check in `l3r2.yaml`'s `energy_basis`; refuses unless each file is in the tree, the check reads "accepted: yes" and names the tip it checked |
| `fill_l3r2_from_basis.py` | PREPARED, NOT RUN: fills row L3-OD6's table and `basis_figures` from the filed outputs by exact keys, reads them back, and refuses a second run; writes no prose |
| `apply_records_readme_row.py` | DRAFT for the integrator: this folder's row in `v2/docs/records/README.md`, after the `s119/` row; not run in the branch |
| `conditional/cond.py`, `od_l3_1.py` to `od_l3_6.py` (round 3b: `od_l3_6.py` takes `--build TYP|WAB` and `--share 50|80|95`; rows 2 and 6 take `--table` on a copy) | PREPARED, NOT APPLIED: the exact registry change each answer of the owner to rows L3-OD1 to L3-OD6 makes. Each takes `--option`, the owner's own `--words` and `--date`, records an owner ruling carrying `decides: <row>:<option>`, applies its edits by id and asserted text, closes M-02 once rows 1 to 4 are decided with row 1 approved, and validates; `--check` writes nothing. Coherent by construction: row L3-OD1 fixes the store only, row L3-OD3 alone fixes the array, row L3-OD4 adopts a band only on 2S2P, and a row whose prerequisites fail is refused. Rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6 refuse to write the tree's registry while `l3r2.yaml`'s `energy_basis` is not filed (D-22, D-23); `qmx-outside` also waits on `relocation_facts`. Row L3-OD4 adopts no band for `both-kept` nor beside a coverage target; row L3-OD6's `coverage` reads its figures only from the row's filled table and records an open conflict where the store does not fit; `both-kept` records one against REQ-072; `od_l3_1.py` carries a coverage target over when it restates REQ-072 |
| `dryrun.py`, `dryrun.out` | every chain of the prepared scripts run on copies of the registry, the incoherent ones refused; the band, the keep figures and the coverage figures come from fixtures standing in for the energy basis |
| `checks/check-l3r2-1.md` | the first independent check of L3-R2 (an AI check, accepted: no), filed byte for byte; its items are answered in round 2 |
| `checks/energy-basis-check-2/` | the second independent check of the energy basis (`fnd/l3plane` at `ec415c09`; an AI check, accepted: yes), its report `CHECK-2.md`, its tools and outputs and the two modules of the first check they import, filed byte for byte |
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
git checkout fnd/l3r2 -- v2/docs/handover/layer3 v2/docs/records/l3r2 v2/ecad/tools/tests/test_l3r2.py \
  v2/docs/records/l3plane v2/docs/records/r11dep v2/docs/records/a1int/reconcile_lid_panel.py \
  v2/vendor/passives/milliohm-hojlr2512-series.pdf v2/vendor/passives/yageo-rc-l-series-v12.pdf \
  v2/vendor/solar/pvgis-series v2/vendor/sources.txt
python3 v2/docs/records/l3r2/read_cfl006.py > v2/docs/records/l3r2/read_cfl006.out
python3 v2/docs/records/l3r2/apply_l3r2_session.py --check && python3 v2/docs/records/l3r2/apply_l3r2_session.py
python3 v2/docs/records/l3r2/apply_l3r2_d23.py --check && python3 v2/docs/records/l3r2/apply_l3r2_d23.py
python3 v2/docs/records/l3r2/apply_l3r2_d24.py --check && python3 v2/docs/records/l3r2/apply_l3r2_d24.py
python3 v2/docs/records/l3r2/apply_l3r2_d25.py --check && python3 v2/docs/records/l3r2/apply_l3r2_d25.py
python3 v2/docs/records/l3r2/apply_l3r2_r3b.py --check && python3 v2/docs/records/l3r2/apply_l3r2_r3b.py
python3 v2/docs/records/l3r2/apply_layer_status_l3.py --check && python3 v2/docs/records/l3r2/apply_layer_status_l3.py
python3 v2/docs/records/l3r2/apply_layer_status_l3_r3.py --check && python3 v2/docs/records/l3r2/apply_layer_status_l3_r3.py
python3 v2/docs/records/l3r2/apply_layer_status_l3_r3b.py --check && python3 v2/docs/records/l3r2/apply_layer_status_l3_r3b.py
python3 v2/docs/records/l3r2/apply_layer_status_l3_r3c.py --check && python3 v2/docs/records/l3r2/apply_layer_status_l3_r3c.py
python3 v2/docs/records/l3r2/apply_layer_status_l3_fill.py --check && python3 v2/docs/records/l3r2/apply_layer_status_l3_fill.py
python3 v2/docs/records/l3r2/apply_records_readme_row.py
env -C v2/ecad/tools python3 rules_lib.py requirements
env -C v2/ecad/tools python3 rules_render.py --requirements
python3 v2/docs/handover/layer3/render_l3r2.py && python3 v2/docs/handover/layer3/render_l3r2.py --check
python3 v2/docs/records/l3r2/dryrun.py > v2/docs/records/l3r2/dryrun.out
env -C v2/ecad/tools/tests python3 run.py test_requirements test_l3r2
```

The renderer lists any open item the set adds as UNCLASSIFIED (closure item L3-C23 then reads OPEN) until `l3r2.yaml`'s
`open_items_layer` gives it a layer.

## The fill procedure (run in round 3c, 30 September 2026, against `fnd/l3plane` `cd8720a1`)

Run once in the branch with `<TIP>` = `cd8720a1ab6eed891b1afd8b5df3b8ceedf36c0f` and CHECK-N = the energy stream's CHECK-5
(filed as `checks/energy-basis-check-5/`, with CHECK-1 to CHECK-4 beside it so that the chain is readable). The files of
`records/l3plane/` and `records/r11dep/`, the three vendor files and `sources.txt` the stream added, and
`records/a1int/reconcile_lid_panel.py` were checked out at that tip, byte identical to it. Every step refuses a second
run; an integrator whose set is not `fnd/l3r2` takes the branch's files (the first line of the run order) instead.

1. **Bring the checked files into the tree and read them:**
   ```
   git checkout <TIP> -- v2/docs/records/l3plane v2/docs/records/r11dep
   python3 v2/docs/records/l3r2/basis_reader.py v2/docs/records/l3plane/weather_basis.out \
     v2/docs/records/l3plane/energy_basis.out v2/docs/records/l3plane/three_cases.out
   ```
   It must read every table whole (exit 0). A header the reader refuses is reported, never guessed around; the reader is
   written for the fourth issue's format (`06b8ecea`).
2. **File the accepting check byte for byte** under `v2/docs/records/l3r2/checks/energy-basis-check-N/`, with its tools
   and outputs.
3. **Name the energy basis**, first with `--check-only`. It refuses unless every file is byte identical to `<TIP>`'s, the
   check reads "accepted: yes" and it names `<TIP>`:
   ```
   python3 v2/docs/records/l3r2/set_energy_basis.py --record v2/docs/records/l3plane/ENERGY-BASIS.md \
     --outputs v2/docs/records/l3plane/weather_basis.out,v2/docs/records/l3plane/energy_basis.out,v2/docs/records/l3plane/three_cases.out \
     --check v2/docs/records/l3r2/checks/energy-basis-check-N/CHECK-N.md --tip <TIP>
   ```
4. **Name the power path's check**, the same way:
   ```
   python3 v2/docs/records/l3r2/set_energy_basis.py --key power_path_check \
     --record v2/docs/records/r11dep/R11-DEPENDENCY.md \
     --outputs v2/docs/records/r11dep/r11_dep.out,v2/docs/records/l3plane/three_cases.out \
     --check v2/docs/records/l3r2/checks/energy-basis-check-N/CHECK-N.md --tip <TIP>
   ```
5. **Restate the power-path list** from the checked classes, and **fill the figures by exact keys**:
   ```
   python3 v2/docs/records/l3r2/restate_power_path.py --check && python3 v2/docs/records/l3r2/restate_power_path.py
   python3 v2/docs/records/l3r2/fill_l3r2_from_basis.py --check && python3 v2/docs/records/l3r2/fill_l3r2_from_basis.py
   ```
   The fill writes row L3-OD6's table, `basis_figures` and `four_cases` (row L3-OD1's four-case cells render from it), and
   reads everything back.
6. **The session restates the prose from the filled figures**, each cited to its line:
   - rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6: their consequences, and the recommendations, with no option taken as
     feasible on its idealised balance;
   - finding F-01, and CF-01 to CF-04 cited to the checked issue;
   - `od_l3_4.py`'s `BAND` table from the basis at the supply range's low end with U3's 6.0 A bracket.
7. **Re-render and re-check:**
   - `rules_lib.py requirements` at 0 errors, `rules_render.py --requirements`, `render_l3r2.py` and its `--check`;
   - `dryrun.py > dryrun.out` and the tests;
   - then a further independent check of L3-R2 (L3-C27), named in `independent_check`.

## Applying an owner's answer (only once he has answered, and only rows the hold no longer holds)

```
python3 v2/docs/records/l3r2/conditional/od_l3_N.py --option <option> --words "<his words>" --date <YYYY-MM-DD> [row extras]
env -C v2/ecad/tools python3 rules_lib.py requirements
env -C v2/ecad/tools python3 rules_render.py --requirements
python3 v2/docs/handover/layer3/render_l3r2.py
```

Row extras: row L3-OD3 `keep` takes `--array-wp`, `--entry-a` and `--evidence` from the checked basis (the filed basis
only, figures as whole tokens); row L3-OD4 `adopt` takes `--push-n` (the owner's number) and, until the `BAND` table is
written, `--band` and `--band-evidence` (the filed basis only, the band as a whole line, cell or quoted phrase); row L3-OD6
takes `--build TYP|WAB` and, for `coverage`, `--share 50|80|95`, reading only the row's filled table.
Row L3-OD2 needs row L3-OD1 approved; row L3-OD3 needs row L3-OD1 approved; row L3-OD4 needs rows L3-OD1 to L3-OD3
(adopt: L3-OD3 answered 2s2p, L3-OD2 not both-kept, L3-OD6 answered mean-day); rows L3-OD5 and L3-OD6 need nothing. After the rows are decided, the CONOPS and product brief passages
`L3-RECONCILIATION.md` lists are prepared for the owner's approval and named in `l3r2.yaml`'s `definition_reissue`
(closure item L3-C26), and a further independent check of L3-R2 is held and named in `independent_check` (L3-C27).
