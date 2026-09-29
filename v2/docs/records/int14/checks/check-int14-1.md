mergeable: no

# AI review: independent integration check of set 13, fnd/int14 at a906b932 (MESHSAT-1357)

This is an AI review, not a qualified engineering review. Checked 29 September 2026 from 17:34 to 18:02 CEST (times read
with `date`).

**Set-up**
* Tip clone: `<scratch>/chk-int14`, a shared clone detached at `a906b932f826d34fc17e326c66a7f1a331f27d79` (still the tip
  of `fnd/int14` at 18:01). Archive `int14-evidence-a906b932.tar` installed: sha256 `dae5201ad41d5dc4...`, 939 files.
  `ibis_fetch.py --check` reads 13 PRESENT of 13; the four held TI sheets match `v2/vendor/sources.txt` lines 454 to 457
  by full sha256.
* Main clone: `<scratch>/chk-int14-base`, detached at `e57a7365`, with `int13-evidence-69156cad.tar` (sha256
  `5f2ee6236328b915...`, 939 files).
* Replay clones (throwaway, in the session scratchpad under `c14/`): `r1` at 3309c9fa, `r2` at 266ee532, `r3` at
  407bf3a3, `r4` at 4f4fd31d. My scripts and outputs are there too.
* Every rule tool ran from a scratch cwd with `VERDICT_DIR` in the scratchpad. `git status` of both check clones is
  clean apart from this file. Nothing committed or pushed; no box, no agent, no other model.

**Counts: 1 blocking, 8 minor.**

## Blocking items

**B1. CFL-016's new circuit rebind entry says no document it names describes the driver side of board C's e-paper
lines. PANEL.md, which it names and binds, does.**

*Where:* `v2/ecad/tools/pcb_requirements.yaml` lines 13865 to 13868 (CFL-016's last evidence entry), written by
`v2/docs/records/int14/apply_rebind_after_circuit_set13.py` from the hand reason passed on its command line. The clause
at fault: "none of the documents it names describes the driver side of board C's e-paper lines".

*Why it is false:*
* CFL-016 names PANEL.md in its statement and binds `v2/docs/PANEL.md@4647782f5aca7c13`, the file at the tip.
* PANEL.md section 3, "Controller pin map (RP2040 `U3`)", lines 89 and 90, gives GPIO 2 and 3 as nets `EPD_SCL`,
  `EPD_SDA` and GPIO 4 to 7 as `EPD_DC`, `EPD_CS`, `EPD_RST`, `EPD_BUSY`. That is the driver side of those lines.
* On the netlist this set regenerated (`c9f7394594201045`, parsed with `tx_inhibit.parse_netlist`), U3 pins 4 to 7
  (GPIO2 to GPIO5) sit on `EPD_SCL_R`, `EPD_SDA_R`, `EPD_DC_R` and `EPD_CS_R`, each through 27R (R53 to R56) to the
  line. Pins 8 and 9 stay on `EPD_RST` and `EPD_BUSY`.
* So this set's own circuit change made two rows of a document CFL-016 names stale, and the entry records the
  opposite.
* S-122, which CFL-016 waits on, closes on "every statement of those documents about the EMCON line and the parts it
  gates". It does not reach the e-paper pin map, so nothing in the tree carries the correction.

*The rest of the reason is true:*
* The R53 CFL-016's evidence names (entry 9, the round 8 board E regeneration) is board E's: on board E's netlist R53
  is 10k from `TAMPER_LEAD` (J_TAMP pin 1, R52) to `TAMPER_IO` (U10 pin 27).
* CFL-016 reads FAIL and waits on S-122 before and after; nothing moves it.

*Why it blocks:* CFL-016 is a BLOCKER record whose acceptance is that each named document describes the circuit as
generated. Main's d0717859 already withdrew a third overclaim in its entries. A fourth would let CFL-016 later close
on S-122 with PANEL.md section 3 still naming the wrong nets, in the firmware contract for MESHSAT-837.

*Fix (either):*
1. Correct PANEL.md lines 89 and 90. GPIO 2 to 5 go on `EPD_SCL_R`, `EPD_SDA_R`, `EPD_DC_R`, `EPD_CS_R`, each through
   27R R53 to R56 to its line; GPIO 6 and 7 stay on `EPD_RST` and `EPD_BUSY`. Then rebind the five records bound to
   PANEL.md (CFL-001, CFL-005, CFL-014, CFL-015, CFL-016) and append the correcting entry below.
2. Or leave PANEL.md as it is. Open an S item for lines 89 and 90, add it to CFL-016's `waits_on`, and append the
   correcting entry below.

Either way, append to CFL-016 a correcting entry, asserted on the netlist, that withdraws the clause and names
PANEL.md lines 89 and 90. The existing entry is append-only.

## What was checked, item by item

### 1. Replays (all byte for byte)

| Commit | Replayed on | Result |
|---|---|---|
| 1b9f543c | r1 at 3309c9fa | 14 of 14 files identical. The steps: `apply_decision_s119.py` (35 to 36 decisions); `decisions_render.py`; `apply_registry_s119.py close 3309c9fabe4b...` with its full re-run of the chain (1 min 44 s, every output reproduced, so the entry's "each reproduced byte for byte" holds); the eight notes and the index row; `apply_rebind_decisions_set13.py`; `rules_render.py --requirements`. A second run of the rebind refuses. |
| 63d64238 | r2 at 266ee532 | `gen_sch_c.py` and `boards/c.json` identical. The dry run writes nothing; a second run refuses. |
| 4f4fd31d | r3 at 407bf3a3, the tip archive installed | `pcb_reliability.yaml`, `C.md` and `calc/rail_widths.out` identical. The inventory is unchanged (74 candidates, 24 classed, 50 excluded, 0 refused), `constraints_bound` reads PASS on all seven sheets and the set, and a second sheets run refuses. |
| a906b932 | r4 at 4f4fd31d, with the tip's 96 reading files and archive | Without a reason, the circuit rebind refuses on CFL-016 (names R53). With the hand reason it rebinds REQ-012, CON-021, CFL-016 and CON-016. Then status, render, the page rebind and a second render. `pcb_requirements.yaml`, `CURRENT-EVIDENCE.md`, `PCB-RULE-STATUS-C.md`, `REQUIREMENTS-TRACE.md` and both scripts are identical to a906b932. |
| 407bf3a3 (box, not replayable) | the tip | Parsed with `tx_inhibit.parse_netlist` and my own parser. Main 87b69472 to tip c9f73945: 221 to 225 parts, exactly R53 to R56 added (27R, R_0603), none removed or changed in value, footprint or fields. Four nets added (`EPD_*_R`); 12 pin moves, all U3 pins 4 to 7 and the eight new resistor pins. `readback_board_c_epd_series.py` HOLDS (0 failing); on main's netlist it FAILS 16. `readback-C-epd.txt` reproduces byte for byte. The provenance file's 69 file hashes match the tip's files, and its schematic sha is the committed schematic's. |

The three merges are exact `git merge-tree` results. Each brings exactly its branch's files at the checked tip:
606708d2 (s119 checks 1 and 2), 29f24a7e (csi checks 1 to 3) and f9bc2f6f (walkmin).

### 2. Readings against main

* **Routed:** 615 against 615, none on one side only. **0 verdicts moved.** 525 are byte identical. 90 differ, the same
  90 files set 12 re-took (git_head a46db71b on main, 4f4fd31d at the tip). Beyond volatile fields and input shas, the
  counts move only as follows:
  * SI-001 on A, B, C, D, E and P gains `allowed_nets` (0 except C). Their tables gain empty `length_limits` rows. E5
    has no SI-001 row in the audit, so "all boards" is these six.
  * Board C's SI-001: layout-bound 23 to 7, allowed 11, answered 10 to 29, signal nets 135 to 139, undecided 1 to 0.
    `models_asked` goes 6 to 5, with `sn74lvc1g00.ibs` leaving; csi README section 5 lines 135 to 138 state this. The
    counts and evidence equal the committed `csi/readings/si001-c-after.reading.json` exactly.
  * Board C's ERC, 334 to 337:
    * Added: `lib_symbol_issues` on R53, R54, R55 and R56.
    * Gone: the one on H1. **Why H1's went:** I could not find the cause in the files.
      * H1 is still in the schematic and the netlist, with the same lib_id, value, footprint and fields. No other
        marker or symbol sits at its position, and the schematic holds no duplicate UUID.
      * The same effect is already on main: the ERC JSON leaves out this warning for #PWR224, C138, C156 and R204 on
        A, C537 on B and LED6 on D, both on main and at the tip.
      * So it is KiCad 9.0.9's reporting, not a change in the circuit. Blocking stays 0.
  * Board C's census: 154 to 158 nets and 74 to 78 unmarked (the four `EPD_*_R`). Pin map: 221 to 225 judged.
    Reliability: only the artefact sha moves; the inventory counts are unchanged.
* **Unrouted (`out/`, ignored):** 427 against 427, 0 moved; counts change on the same ten readings. `summary.json` and
  `tools/out` are identical.
* On the tip, `edge_length` reads the models PRESENT on A, B, C and D and NOT_ASKED on E and P. Board A's
  `intent_rails` records the two held sheets (c8595fa8, f1aad251).
* Board C's check_contracts reads PASS of 99 and interfaces_c 0 disagreements, as the commit states.

### 3. Registry (parsed, main against the tip)

* **Records:** 144, same order. Seven changed, each keeping its old evidence as a prefix. No `evidence_result` moved.
  * REQ-012, CON-021, CON-016: evidence +1 and board C's netlist binding.
  * CFL-016: evidence +2 and two bindings (decisions a41df5d1, board C's netlist).
  * CON-010, REQ-044: evidence +1 and the page binding (dbd82cdd to c9b98931).
  * REQ-072: evidence +1, and `waits_on` drops S-119, leaving S-53, M-02 and S-114 (all open). It stays FAIL.
* **Items:** open_items 86 to 85 (S-119 out); closed_items 65 to 67 (S-119, then S-121). S-122 is identical. Nothing
  else at top level moved; `needs_document_sha256` still matches CONOPS.md.
* Every binding in the registry matches the file at the tip (0 stale).
* **Reasons:**
  * The decisions rebind is true. CFL-016 reads decisions 28 and 40, both identical; only 58 is added. No generator
    carries U3B, L2B, R16B or Q7B, and none of PANEL, CONOPS, V2-SPEC, OPERATING-ENVELOPE or TEST-PLAN mentions the lid
    charger.
  * REQ-012, CON-021 and CON-016 are true. They name U3 only for its pin 32 (GPIO21, unmoved) and EPD_VCC (unchanged).
    CON-016's clamps are untouched; the added parts are resistors.
  * CON-010 and REQ-044's section and row claims are computed by the script and reproduced.
  * CFL-016's circuit reason: B1.
* **S-119 and S-121:** closed on their stated evidence.
  * The close script's preconditions all passed in my replay, including the re-runs.
  * S-121's figures match the outputs: 32.6 mA (`efficiency.out` line 80), 9.74 A peak and 8.00 A RMS against 25.4 and
    17.5 A (`inductor_u3b.out` lines 22, 31 and 33), 0.972.

### 4. f9bc2f6f (walkmin minors, not checked before)

* **The lug check:** `tx_inhibit.py` line 1726 refuses None, a single lug, three lugs and ("1", "1").
  * On b4a34ffa's tool the tip's new test fails at exactly the ("1", "1") assertion. On the tip it passes.
  * `test_tx_inhibit`: 143 passed, 0 failed. The kit's declaration ("1", "2") is unchanged, and RF-002's readings
    moved on no board.
  * The string "12" and integer lugs still pass the check: m3.
* **The README citation:** it now cites `records/int13/checks/check-set12-3.md`, which exists at the tip.
  * Its items 1 (lugs) and 3 (board key default) are the two answered. Item 2 (the SW prefix contact rule) is named
    open.
  * The filed `checks/check-walkmin-1.md` equals `<scratch>/chk-walkmin/CHECK.md` apart from the scratch path.
* **The tests are still right** for what they claim. The README's new wording of the test claim (lines 20 to 22)
  answers the check's minor 3.

### 5. Validators and pages

* **`rules_status.py`, three times:**
  * Exit 1 each time with identical stdout: FAIL of 338 (PASS 195, INCONCLUSIVE 104, FAIL 39), NOT_READY. That is
    the status the commit states.
  * Runs 2 and 3 equal the archive's audit once the clone path is normalised. Run 1 differs only in SGN-001's
    `writers` (rules_render.py, read from the render left in the archive, against rules_status.py). That
    self-reference predates this set.
* **`rules_render.py`, twice:** exit 0, `git status` clean.
* **Renderer checks:** `--check` reads 16 documents, 0 out of date; `--requirements --check` reads current;
  `decisions_render.py --check` exits 0; `constraints_bound.py` reads PASS.
* **`rules_lib.py`:** 59 rules, 0 errors, 0 warnings. `requirements`: 144 records, 0 errors, 0 warnings.
* **Tests:** test_requirements 66, test_edge_length 46, test_decision_register 5 and test_rules_registry 5, which is
  122 passed and 0 failed. With test_tx_inhibit's 143 above, 0 failed in all.
* **How the pages moved:**
  * CURRENT-EVIDENCE.md moves only board C's netlist sha, in three sections (the candidate table, the PASS table's
    seven C rows and REL-001's desk row). Layout entry reasons stay at 34.
  * PCB-RULE-STATUS-C.md moves only ERC 334 to 337 and pin map 221 to 225.
  * REQUIREMENTS-TRACE.md moves only by the seven records' entries and bindings, REQ-072's waits, the S-119 and S-121
    rows, and the header count (86 open and 65 closed to 85 and 67).
  * OWNER-DECISIONS-OPEN.md gains decision 58's row.

### 6. Every changed file

`e57a7365..a906b932` changes 202 files (146 modified, 56 added). Each belongs to one of the eight first parent
commits. Five files are touched twice:
* CHARGER.md and TOPOLOGY.md: 3309c9fa, then 1b9f543c's notes.
* `boards/c.json`: 266ee532 and 63d64238.
* `pcb_requirements.yaml` and REQUIREMENTS-TRACE.md: 1b9f543c and a906b932.

No vendor, held, IBIS or Claude file is committed. All 35 commits carry the owner's identity as author and committer,
[MESHSAT-1357] in the subject, no trailer, and no em or en dash in added text. Nothing is unexplained.

## Minor items

* **m1. The H1 ERC warning** (a906b932's message): see section 2. Say in the set's record that the ERC JSON leaves
  out the library warning for some symbols on A, B, C and D, so the warning count is not a symbol census.
* **m2. Board C's `return_via`, `ref_change` and `via_audit` re-takes are owed and carried nowhere.**
  * csi README section 6 step 3 (lines 147 and 148) and section 5 (lines 136 to 138) say they are owed.
  * The set did not take them. They run on the board file, which did not change, and they stay AWAITING_REVALIDATION
    (21 September readings). No record or plan line carries them.
  * Fix: carry them with board C's next regeneration.
* **m3. `tx_inhibit.py` line 1726 still accepts the string "12"** (two distinct characters that match pins 1 and 2
  by accident) and integer lugs (never match, which is conservative). The walkmin check's minor 2 asked for a tuple of
  two distinct strings. Fix: require `isinstance(lugs, tuple)`, both items `str` and distinct, and add "12" and (1, 2)
  to the test's bad list.
* **m4. `records/walkmin/README.md` line 5 still says `apply_walk_minors.py` answers the minors.** f9bc2f6f's lug line
  and the test edits are direct edits, so the script replayed on a1f8ec70 no longer gives the committed file. "Minors 3
  to 6 are carried" appears only in the commit message. Fix: one line in the README for each.
* **m5. Stale docstrings.**
  * `records/int14/apply_rebind_after_circuit_set13.py` lines 2 and 3 describe set 13 as "stream d4emcon's FEA-002
    remedies on boards B and C", which was set 12's change. Its CHANGE default and its output are right.
  * `apply_rebind_page_set13.py` lines 3 to 5 list an older set's re-render.
* **m6. s119 CHECK-2's minors N2 to N5 and N7 are neither answered nor carried in the tree.**
  * CHARGER.md line 101 still ends "all inside the balance that meets M1".
  * Decision 58's `authority_why` still says "one option stands clear".
  * TOPOLOGY.md has no ACX_OCP setting.
  * The Table 9-1 citation stands at CHARGER.md line 72 and TOPOLOGY.md line 98.
  * Fix: answer them, or list them in the s119 README's open items.
* **m7. The comparator in `apply_rebind_after_circuit_set13.py` lists as changed only parts added, removed, or
  changed in value or footprint.** U3, whose pins 4 to 7 moved, is not listed, and three rebound records name U3. They
  rest on pin 32, so their reason holds this time. Fix: list parts whose pins moved.
* **m8. `v2/docs/records/README.md` has no rows for `csi/`, `walkmin/` or `int14/`.** The same holds for int12,
  int13, rf2walk, s117, s118 and e200c on main.

## Counts

* **Items:** blocking 1 (B1); minor 8.
* **Replays:** 27 of 27 files byte for byte (14, 2, 5 and 6), plus the read back file. The box regeneration's netlist
  carries exactly R53 to R56.
* **Routed readings:** 615 compared, 0 moved, 525 identical, 90 re-taken, count changes on 10, all explained (H1's lost
  ERC warning a pre-existing KiCad reporting effect). **Unrouted:** 427 compared, 0 moved.
* **Registry:** 7 records changed, 0 results moved, S-119 and S-121 closed, REQ-072 FAIL waiting on S-53, M-02 and
  S-114, S-122 untouched.
* **Validators:** 0 errors, 0 warnings. **Renderers:** current.
* **Tests:** 265 passed, 0 failed.
* **Files:** 202 changed, all explained.
