accepted-so-far: no

# CHECK-2: scoped re-check of the Layer 3 handover L3-R2, rounds 2 and 3 (item C27), the held energy figures excluded

MESHSAT-1357, 30 September 2026, about 03:30 CEST. **An AI check, not a qualified review.** The checker wrote none of
L3-R2.

**What was checked:**
* Branch `fnd/l3r2` at `325859b5` (confirmed). Its four commits sit on `fnd/int16` `4012429e`: `6071b410`, `3ee9fc62`,
  `72be7c14` and `325859b5`.
* Round 1 is kept as `fnd/l3r2-r1` at `9c26a641` (confirmed).
* Scope, per the owner: the changed sections and affected dependencies. The energy figures of rows L3-OD1, L3-OD2, L3-OD4
  and L3-OD6 are excluded as HELD. Those rows' structure, options, flags and scripts are in scope.

**Why "no".** Round 2 and round 3 close most of CHECK-1. Four items remain that the owner's instructions or the
coordinator's list make blocking:
* B1: row order can select the average-day benchmark without the owner.
* B2: the rows can be decided on a store that does not match the weather basis chosen, and the gate still reads MET.
* B3: the gate's filed-file conditions accept any check verdict and any ruling id.
* B4: fact CF-01 states the bus range as established while leaving out the brackets its own evidence gives below 19.08 V.

Each is a small fix.

## What was run (throwaway shared clone at `325859b5`, removed after this check)

* **Setup.** `int16-evidence-e5322674.tar` installed; the tree was clean after it. The branch is its own integration set,
  so per the README only the renders and tests remain.
* **Gates:**
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings.
  * `rules_render.py --requirements --check`: current.
  * `render_l3r2.py --check`: 3 pages, 0 out of date.
  * `dryrun.py`: rerun **byte identical** to `dryrun.out`.
  * `run.py test_requirements test_l3r2`: **83 passed, 0 failed**.
* **A real, unheld answer applied to the tree.** `od_l3_5 reading-c` wrote the registry. The tree then validated, both
  pages rendered, and the tests read 82 passed, 1 skipped ("L3-OD5 is decided"). CHECK-1 minor 2 is answered.
* **Holds on the tree.** `od_l3_1 approve` and `od_l3_6 mean-day` are refused on the tree ("held ... energy_basis is not
  filed"). `od_l3_3` is refused until L3-OD1 is decided.
* **Merge with main** (`6cd331ef`): clean. After the merge, `REQUIREMENTS-L3-R2.md` goes out of date by its header line
  only (the registry's sha). After a re-render the tests read 83 passed. This is closure item L3-C28's step.
* **My own paths on copies of the registry** (A, B, C), plus two gate tests in the clone:
  * the registry of path B with a fake energy basis;
  * a `definition_reissue` entry.
  The clone was reset after each.
* **Text rules** on the 12930 lines L3-R2 adds (`4012429e..325859b5`):
  * 0 lines with U+2013 or U+2014.
  * One line matches a host or path word: my own filed CHECK-1, which says "the session scratchpad" (a word, not a
    path).
  * CONOPS.md, PRODUCT-BRIEF.md and `v2/release/` are unchanged against `4012429e` and against main.
  * The 42 relative links on the three L3 pages all resolve.
  * `checks/check-l3r2-1.md` is my CHECK-1, byte for byte (sha256/16 `bbb8c97a165850cf`).
  * `checks/energy-basis-check-1/CHECK-1.md` is byte identical to its report (sha256/16 `845858d6c3059f77`).

## Blocking items

### B1. Deciding row L3-OD4 before row L3-OD6 selects the average-day benchmark without the owner (D-23)

* **The rules.** `od_l3_4.py adopt` requires only that L3-OD6 is not `coverage`; an undecided L3-OD6 passes. After that,
  `od_l3_6.py coverage` refuses with "row L3-OD4 is answered again first". No script re-answers a decided row, because
  `cond.require` refuses "already decided".
* **Path A, run on a copy.** approve, qmx-out, 2s2p, adopt (L3-OD6 undecided), then:
  * coverage: **REFUSED**;
  * mean-day: written.
* **The effect.** Once a band is adopted, the only weather basis left is the benchmark, although the owner never chose it.
  The README's own order (`od_l3_N.py` by row) applies row 4 before row 6.
* **What D-23 says.** "An average-day benchmark may be an option; do not select it automatically because the current
  design passes it."
* **Fix.** `adopt` requires `L3-OD6:mean-day`, stated in the row's dependencies. The band is mean-day grids, so it follows
  the owner's L3-OD6 answer and never precedes it.

### B2. The rows can be decided on a store that does not carry the weather basis chosen, and the gate reads MET

The owner asked that the gate need a coherent set (CHECK-1 B1). `coherent()` in `render_l3r2.py` and the scripts check
four rules. None of them compares row L3-OD6's weather basis with the lid chosen in row L3-OD2, and row L3-OD6's table
cannot express it.

* **Path B, run on a copy.** A coverage target with fixture figures (50 %, 2000 Wh usable, `fits: YES`); then approve,
  tablet-out (4S20P, 964.8 Wh nominal), 2s2p, reject, reading-c. Every script wrote and the validator read 0 errors.
* **Rendered in the clone with a fake `energy_basis`:** "Target unambiguous: **MET** ... coherence holds; energy basis
  filed". No conflict is recorded.
* **Why this is not only a fixture artefact.** `od_l3_6.py` records a conflict only when `fits` is NO, and `fits` is one
  value per target (`quantified.rows`). The basis the table is to be filled from answers per lid:
  * ENERGY-BASIS.md section 8a, `fnd/l3plane` `868c321f`, for the mean day: "yes: tablet out, QMX out" (TYP) and "yes: QMX
    out only" (WAB).
  * So the benchmark with the tablet-out lid would read coherent in the WAB build with no flag.
  * `mean-day` records no conflict in any case.
* **Overstated closure claims.** L3-C32 (CLOSED) says the gate reads a decided set against the coherence rules, and
  LAYER-STATUS says "the scripts and the gate refuse a combination the evidence does not cover". Paths A and B show both
  overstate it.
* **Fix.**
  * Give each weather option's row a fits column per lid (and per build, if both stay).
  * Add a coherence rule, enforced by the scripts and by `coherent()`, that the lid of L3-OD2 carries the store of the
    L3-OD6 answer. Otherwise record an open conflict.
  * Restate L3-C32 to what is enforced.

### B3. The gate's filed-file conditions accept any check verdict and any ruling id

This concerns the D-22 hold and CHECK-1 B6.

* **The energy basis hold.** `cond.hold()` compares only `energy_basis.record` and its sha. `filed()` in the renderer also
  compares the check file's sha, but not its verdict.
  * **Run in the clone:** a fake `ENERGY-BASIS.md` and a fake check file that reads "accepted: no", named in
    `energy_basis`. The gate then read "energy basis filed" and condition 1 MET.
  * **What D-22 says:** "Hold decisions 1, 2 and 4 until the corrected, independently checked comparison arrives."
* **The re-issue approval.** The gate needs only that `definition_reissue.approved_by` is some ruling id in
  `owner_rulings`.
  * **Run in the clone** (the path B registry): `{record: v2/docs/CONOPS.md, sha16: <its sha>, approved_by: D-21}`, that is
    the unchanged baselined CONOPS and a ruling of the morning. The gate read "the definition documents re-issued and
    approved (L3-C26): **yes**" and condition 3 **MET**.
* **Fix.**
  * `energy_basis` carries the check's verdict, and the hold and condition 1 require ACCEPTED, as `independent_check`
    already does.
  * `definition_reissue` names a ruling that decides it (for example `decides: "definition_reissue"`, dated after the
    rows' rulings) and a record other than the baselined files.

### B4. Fact CF-01 states the charge bus range as established and narrowing s120's band, leaving out the brackets its cited check gives below 19.08 V

This is the coordinator's item 5 and the owner's D-22 first paragraph.

* **What CF-01 says:**
  * 19.146 / 20.000 / 20.887 V;
  * "Not yet in the figure: the resistors' ageing and the divider's own heating above the air (the check's minors 1 and
    2)";
  * "It narrows stream s120's DC band of 19.080 to 20.960 V".
* **What the filed CHECK-1 it cites gives:**
  * minor 1: 18.782 V with the makers' endurance limits, and "the page should carry the figure beside the exclusion";
  * minor 2: 19.072 V with a 20 K board rise.
* **What the basis's current issue (`868c321f`, section 2) gives.** It keeps the steady-state range unchanged and carries
  both terms as **brackets beside it, not in it**:
  * 19.101 V (a 20 K rise at the hot end, an ASSUMPTION);
  * 18.782 V (the endurance limits, a bound);
  * 18.738 V (both together).
* **So is the fact still worded truly?**
  * "Not yet in the figure" is literally true, since the terms are outside the steady-state figure by the basis's choice.
    But "yet" reads as pending, and the fact omits figures now computed.
  * "narrows ... 19.080" holds only for the steady-state range: with the brackets the low end is below 19.080 V.
  * F-01 and LAYER-STATUS call the range "established".
  * The owner's words are "If 19.08 V is permitted, mission claims must account for it". The L3 pages give him the
    impression that the bus never reaches it.
* **Fix.** Restate CF-01, F-01 and LAYER-STATUS's F-01 sentence:
  * the steady-state range as the basis gives it;
  * the two brackets with their figures and kinds, beside it;
  * "narrows" limited to the steady state;
  * cited to the checked issue once energy CHECK-2 is filed.

## CHECK-1's items, as re-checked

| CHECK-1 | State now |
|---|---|
| **B1 coherent rows** | Largely closed. L3-OD1 fixes the store only (its ruling: "The solar input is row L3-OD3's"). L3-OD3 alone fixes the array and replaces REQ-072's marked phrase. `adopt` needs `2s2p`. Refused in the dry run: my CHECK-1 path (keep then adopt), 1s4p with adopt, both-kept with adopt, a coverage target with adopt (either order), and row 2 after reject. `keep` refuses without the basis's array, entry current and evidence. The gate reads an incoherent set NOT MET (test). Open: B1 and B2 above |
| **B2 (not energy)** | Closed as far as not energy: SC-76 withdrawn, the band HELD for the checked basis, and the recommendation says the band is written "with U3's 6.0 A bracket at the low end of the supply range". The script does not enforce the bracket (the band is free text with an evidence file) |
| **B3 M1 narrowing** | **Closed.** "no M1 claim ... less energy" appears only in P-23 (WITHDRAWN) and my filed CHECK-1. Section 4 and L3-C25 now read "M1 carries no season ... a month with less sun asks more of the array" |
| **B4 SC-76** | **Closed.** No SC-76 in the registry (last is SC-75); P-22 WITHDRAWN; open item S-127 carries the energy basis; REQ-072 `waits_on: [S-53, M-02, S-127]`. The classification now puts the supply range at IMPLEMENTATION (layer 4, an engineering input) and the rule "every load-holding limit at its minimum across the supply range" at REQUIREMENT, entering REQ-072 only through row L3-OD1. Residual: B4 above (CF-01) |
| **B5 REQ-054** | **Closed.** The acceptance reads "at most 14 dBm ERP on every configured channel outside 869.4 to 869.65 MHz, and at most 27 dBm ERP at a duty cycle of at most 10 % on a channel inside 869.4 to 869.65 MHz", with the prototype line judged "at or under the limit of the band the channel is in". It is taken from the statement; the history says "no limit added or removed" |
| **B6 gate and L3-C26** | Closed in structure: condition 3 needs `definition_reissue` filed with an owner ruling, and the target text renders the decided rows once condition 1 holds. Open: the ruling is not bound to the re-issue (B3) |
| **Item 2 (settled vs proposed)** | Closed except minor 1. `proposal_only` is stated on the pages. L3-OD4's conditions are "narrower conditions the owner approves (D-22), never a closure". REQ-078's draft states the stability, not the stay, and is core. P-03 names ARRAY.md's 200 W sentence as an engineering instruction |
| **Item 3 ("adverse")** | Closed on the L3 pages and in l3r2.yaml: the word appears only inside the owner's quoted D-22, and "typical" only for power modes (PS-TYP) in unchanged records. `test_l3r2` holds it. Residual: minor 4 |
| **Item 4 (displaced items)** | Closed, per row L3-OD2 option: see below |
| **Minors 1 to 14** | All answered. Minor 2 is confirmed by the run above. Minor 10: the pattern set now includes "exists yet" and "open", and REQ-045 is classified (its sentence is still in the acceptance). Minor 6: the "every hour" pass line is in the script's REQ-072 note, not in the row's consequences (minor 5 below) |

**Item 4 in detail, row L3-OD2's options:**
* qmx-out: HF leaves the kit, stated as the owner's explicit removal.
* qmx-outside: HF kept only with a place and lead that no record establishes; HELD with the flag "NO LOCATION
  ESTABLISHED".
* tablet-out: the bracket's function leaves the kit; the tablet's use stays outside the case (REQ-017 deferred, stated);
  "no record establishes how the tablet travels with the kit".
* both-kept: flagged CANNOT MEET M1, with an open conflict.

**Item 4, the other rows:**
* L3-OD1's ruling names the west RF re-plan and that one lid function leaves.
* L3-OD3 states that the panels and stand travel flat beside the case.

## The coordinator's items

1. **B1.** L3-OD1 fixes the store only, L3-OD3 fixes the array, and `od_l3_4 adopt` needs 2S2P: verified in the scripts
   and in the dry run. The incoherent combinations the author listed are refused and the tests pass. My own paths:
   * A: row 4 before row 6. It is not refused and it selects the benchmark (B1).
   * B: a coverage store above the chosen lid. It is not refused and the gate reads MET (B2).
   * C: keep without the basis's figures. Refused, correctly.
2. **B3.** Gone everywhere. P-23 is WITHDRAWN.
3. **B5.** Holds, derived without a change in substance.
4. **B6.** The gate holds on L3-C26 in structure. `definition_reissue` accepts any ruling id (B3).
5. **B2 and B4, not energy:**
   * SC-76 is withdrawn; S-127 is open; REQ-072 waits on S-127.
   * CF-01 to CF-04 cite the energy CHECK-1 correctly:
     * CF-01: the range reproduced (19.1458 / 20.8871 V; 19.2050 / 20.8226 V) and "the worst case stack is sound"; minors
       1 and 2.
     * CF-02: GEN, "every lid fails by 326 to 523 Wh"; the front end at 6.935 A minimum.
     * CF-03: 11520 rows, 864 windows, 0.005 W/m2, 3.17 / 7.36 / 11.45 kWh/m2, the re-fetch equal.
     * CF-04: the relocation facts.
   * CF-01's wording, the coordinator's question: see B4.
6. **Items 2 to 4 and D-23:**
   * Proposals only: yes, except minor 1.
   * No "adverse" or "typical" on the pages.
   * Displaced items: stated.
   * The benchmark is not preselected on the pages (L3-OD6's recommendation reads HELD and "not selected because the
     current design passes it"), but the scripts preselect it by order (B1).
   * Flags in capitals: L3-OD1 approve (CANNOT MEET M1 on the held circuit), L3-OD1 reject, L3-OD2 both-kept, L3-OD2
     qmx-outside (NO LOCATION ESTABLISHED), L3-OD6 coverage.
   * R11: the OWNER-DECISIONS page carries a two-column table (held circuit R11 10 mOhm against the drafted 6.2 mOhm, the
     latter HELD). L3-C34 (implementation, layer 8) and L3-C35 (physical verification, prototype) are DOWNSTREAM and
     separate, and are not prerequisites.
7. **D-22 and D-23.**
   * I compared each quoted paragraph of the registry's rulings with the blockquotes of
     `OWNER-INSTRUCTION-2026-09-30.md`: D-22's 5 and D-23's 4 are identical, word for word.
   * D-21's quote splits at its marked elisions into segments that are all in the file.
   * D-21's title is now "finish layer 3 ...".
   * No page claims completion: the gate reads NOT MET on all four conditions, "Status of L3-R2: IN_PROGRESS".
8. **My minors.** Each is answered (table above).
9. **Coverage targets, a finding for alignment** (minor 7 below):
   * `l3r2.yaml`'s illustrative targets are 50, 80, 90 and 100 %; ENERGY-BASIS.md section 8a computes 50, 80 and 95 %.
   * `od_l3_6.py` refuses a share the table does not list, so 95 % cannot be answered and 90 and 100 % cannot be filled.
   * The energy CHECK-1 is filed as NOT_ACCEPTED under `checks/energy-basis-check-1/`, and `energy_basis_checks` lists
     only it.
   * The energy CHECK-2 (`_scratch/_reports/chk-energy/CHECK-2.md`, "accepted: yes") is not filed, and `energy_basis`
     is null.
10. **Gates.** All pass (above).

## Minors

1. **qmx-outside's enclosure change is not named as the owner's.**
   * The classification table (c) classes "a sealed case-wall lead for a QMX carried outside" as IMPLEMENTATION (layer 7).
   * The option's ruling says "placed as l3r2.yaml's relocation facts state", without naming the ruled constraint it
     changes (the connector plate that "does not carry" such a lead, or the sealed case).
   * D-23 lists enclosure constraints among the owner's proposals. The flag says it, but the change should be named in
     the option and its affected list, and classed as the owner's.
2. **Wrong ruling in a refusal.** `cond.hold()` refuses row L3-OD6 as "held (D-22)"; D-23 holds it.
3. **"Recommended" wording for held rows.** The `dryrun.py` chain "recommended where recommended ... the average-day
   benchmark shown" and the test phrase "the recommended set" include `mean-day` while L3-OD6's recommendation is HELD.
   Name them example chains.
4. **Old wording in REQ-072's evidence.** REQ-072's s119 evidence entry still says "93.7 Wh typical and 85.5 Wh adverse"
   (rendered, REQUIREMENTS-TRACE.md line 1351). The new qualifying entry covers the 20.7 V bus but not the two words.
5. **The pass line change is not in the row.** L3-OD1's consequences do not name the pass-line change "every hour of the
   72" (the script's REQ-072 note does).
6. **Weak bindings in the scripts:**
   * `od_l3_3 keep` asserts "N Wp" and "N A" anywhere in the evidence file;
   * `od_l3_4 adopt` accepts any `--band-evidence` file, not the filed `energy_basis` record;
   * `od_l3_6` asserts figures by substring.
7. **Alignment of row L3-OD6's table with the basis** (item 9):
   * targets 50 / 80 / 95 against 50 / 80 / 90 / 100;
   * two builds (TYP, WAB) per target against one row;
   * the basis's mass is the cells' only, and its volume is two figures (cylinders / footprint), against one `mass_kg`
     and one `volume_l`;
   * `fits` is per lid in the basis (B2).
   * The basis's "TYP" must be defined by its exact assumptions when copied, or the pages reintroduce "typical".
8. **Pre-existing unit ambiguity.** REQ-054's prototype line adds "the antenna's gain" to a conducted output to judge ERP,
   without saying dBd.

## What the final delta check must cover once the figures are filled

1. **The fixes for B1 to B4 and minors 1 to 7:**
   * `adopt` needs `mean-day`;
   * the L3-OD6 against L3-OD2 coherence rule and per-lid fits;
   * the verdict-bound `energy_basis` and the decides-bound `definition_reissue`;
   * CF-01, F-01 and LAYER-STATUS restated with the brackets;
   * L3-C32 and LAYER-STATUS's coherence sentence restated to what is enforced.
2. **The energy basis named with its ACCEPTED check filed byte for byte** (the energy CHECK-2 or a later one), and CF-01 to
   CF-04 re-cited to that checked issue.
3. **Every HELD cell filled from the checked basis:**
   * rows L3-OD1, L3-OD2, L3-OD4, L3-OD6;
   * the R11 table's conditional column;
   * F-01;
   * each row's recommendation.
   Each figure must be traced to its section.
4. **Every case named by its exact weather and operating assumptions** (TYP, WAB, WE), with no "typical" or "adverse".
5. **Each option that cannot meet M1 flagged** in each build, the lid-dependent fits included (for example the mean day
   at WAB fitting the QMX-out lid only).
6. **`od_l3_4.py`'s `BAND` table written from the basis** at the supply range's low end with U3's 6.0 A bracket, bound to
   the filed record.
7. **Row L3-OD6's table aligned with the basis's targets and builds**, and the recommendation stated without taking the
   benchmark because the design passes it.
8. **The gates again, on the tree the owner will read** (main merged and re-rendered):
   * `rules_lib` 0 errors;
   * both renders pass `--check`;
   * the tests pass;
   * `dryrun.py` byte identical;
   * no dashes, host names or paths;
   * CONOPS, PRODUCT-BRIEF and H3 unchanged.
9. **This check recorded** in `independent_check` with its sha and verdict, and the next check's verdict read by
   condition 4.
