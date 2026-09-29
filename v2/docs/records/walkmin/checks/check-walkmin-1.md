mergeable: yes

# AI review: independent check of fnd/walkmin at b4a34ffa (RF-002's walk: the EMCON toggle's lugs and the board key; MESHSAT-1357)

This is an AI review, not a qualified engineering review. Read on 29 Sep 2026 from 16:57 to 17:10 CEST (times from `date`).

* **Clones:** shared scratch clones detached at `b4a34ffa` (`<scratch>/chk-walkmin`, this file's directory) and at `a1f8ec70` (`<scratch>/chk-walkmin-base`), and a replay clone at `a1f8ec70` (`<scratch>/chk-walkmin-replay`).
* **Nothing written outside scratch:** no worktree and not the main checkout. `git status` of both check clones is empty apart from this file.
* **Rule tools:** run from a scratch cwd with `VERDICT_DIR` under `<scratch>/chk-walkmin-run/`. My scripts and outputs are there: `per_assert.py`, `kit_mutants.py`, `cross.py`, `spy.py`, `callers.py`, `kbind.py`, `cmpvd.py`, `walk/`, `cc/`.
* **The maker's sheet:** read with `pdftotext -layout` and as a rendered image of page 6 (`apem6top-06.png`).

**Counts: 0 blocking, 6 minor.** The predicate does what the record says, and every miswire the brief names is refused, on direct calls and on the whole walk over the kit's own netlists. No production path can reach the walk without a board key. The kit's RF-002 readings are identical at both commits. The new test covers every predicate case the round 3 check named, and all 143 tests pass. The minors are about record text and hardening.

## Blocking items

None.

## 1. The maker's words

* **APEM 5000 series sheet, page 6** (`v2/vendor/seals/apem-5000-series-datasheet-rs-copy.pdf`), SOLDER LUG TERMINALS, SINGLE POLE:
  * Row 5636 reads ON, none, ON.
  * The column for lever position I prints lugs 1 and 2 closed, the column for position III prints lugs 2 and 3.
  * Lug 2 is in both pairs, so it is the common. The declaration's `lugs_src` states exactly this.
  * The order code 5636ADKB 2V decodes on page 5: AD is silver, gold plated; K is the front panel seal; B is epoxy sealed terminals; 2V is two locked positions. Page 13 lists the 2V lever as "(function 6)", so the 5636 row is the right row.
* **`v2/ecad/tools/gen_sch_c.py` line 306** wires SW_EMCON `{"1": "TX_INHIBIT_n", "2": "GND", "3": "NC"}`: lug 1 is on TX_INHIBIT_n and lug 2 on GND. The committed netlist agrees (`v2/ecad/pcb-c-display-c8/out/pcb-c-display.net`): pin 1 on /TX_INHIBIT_n, pin 2 on GND, pin 3 on its own unconnected net.
* **The cover:** nothing in the change claims to know which lever position the hinged cover forces.
  * `lugs_src` (tx_inhibit.py line 1707) ends with "Which position the hinged cover forces is an assembly item".
  * The README, the docstrings and the test name position I only as the sheet's position for lugs 1 and 2.
  * Note: a toggle across 2 and 3 would still assert the inhibit, in position III. Refusing it holds the netlist to the declared design (gen_sch_c.py lines 302 to 304), which is the conservative reading. The change describes it accurately as "the other lever position's contact".

## 2. The predicate

**Direct calls to `_is_toggle`** (`per_assert.py`, built with the test file's own `_nl`; "refused" means None or ValueError as intended):

* line on 1, GND on 2: the toggle at b4a34ffa; the toggle at a1f8ec70.
* line on 2, GND on 1 (symmetric): the toggle at both commits.
* 1 and 3, 3 and 1, 3 and 2, 2 and 3: refused, all four, at b4a34ffa; read as the toggle, all four, at a1f8ec70.
* a third lug on a net, or lug 3 also on GND: refused at both commits.
* the same part on board B: refused at both commits.
* +3V3 instead of GND: refused at both commits.
* both lugs on the line; the toggle on EMCON_HW; another value: refused at both commits.
* `_is_toggle(None, ...)` and `_switch_board(nl, None)`: ValueError at b4a34ffa; the toggle and True at a1f8ec70.
* a declaration with `lugs=None` or a single lug: ValueError at b4a34ffa; the toggle at a1f8ec70.

**The whole walk on the kit** (`kit_mutants.py`): A to D's committed netlists, with board C's SW_EMCON rewired in memory and passed through `judge`. Each item gives EMCON_HW, TX_INHIBIT_n, then the transmitters as PASS/FAIL/UNDECIDED.

* as committed (1 line, 2 GND, 3 open): PASS, PASS, 7/0/11 at both commits.
* symmetric (2 line, 1 GND): PASS, PASS, 7/0/11 at both commits.
* 1 line, 3 GND, the common open (round 3's T2a): FAIL, FAIL, 0/18/0 at b4a34ffa; PASS, PASS, 7/0/11 at a1f8ec70.
* 3 line, 1 GND: FAIL, FAIL, 0/18/0 at b4a34ffa; PASS, PASS, 7/0/11 at a1f8ec70.
* 3 line, 2 GND: FAIL, FAIL, 0/18/0 at b4a34ffa; PASS, PASS, 7/0/11 at a1f8ec70.
* 2 line, 3 GND: FAIL, FAIL, 0/18/0 at b4a34ffa; PASS, PASS, 7/0/11 at a1f8ec70.
* lug 2 on +3V3: FAIL, FAIL, 0/18/0 at both commits.
* lug 3 also on GND: FAIL, FAIL, 0/18/0 at both commits.

* **The symmetric contact is right for this part.** In position I, lugs 1 and 2 are one closed contact, whichever of them carries which net. In position III the line, on the common, meets only the dead lug 3. The function is the same.
* **The board key:**
  * `_is_toggle` raises on None (line 1723).
  * `_switch_board`, `_source_output`, `drive_net` and `_line_sources` lost their default, so leaving the key out is a TypeError.
  * An explicit None raises wherever it reaches `_is_toggle`. `drive_net` returns None early for a net of the wrong shape, which makes no source.
* **Production callers, traced with `ast` over every .py under `v2/`** (`callers.py`, `kbind.py`): nine call sites, all in tx_inhibit.py.
  * census, lines 1385, 1392 and 1503: k comes from the walk queue, seeded with board letters.
  * `_network`, line 2247.
  * `fail_safe`, line 2300: k comes from `cond`, which holds board letters.
  * `_fs_base`, line 2475: `x[0]` of the `src` keys, which are board letters.
  * `judge` is fed by `check_contracts.py` line 483 (the keys of NETS, which are letters) and by `report` (only a truthy letter from the file name).
  * No other module calls the five functions. `v2/docs/records/w4b/tools/emcon_block_harness.py` only parses netlists, and the H1 handover copy is a frozen tool.
  * At a1f8ec70 the same trace shows that production already passed the key and only 13 test calls did not, as the README says.

## 3. The kit's readings are unchanged

* **The same netlists at both commits.** Board A to D's tracked netlists have the same sha256 at both commits (A 6c40250c47195ebb, B 3ef9b8c49a01b728, C 87b69472ac83ca5a, D a2d48972d171aad1). No netlist changed on main e57a7365 or fnd/int14 3309c9fa since a1f8ec70.
* **The walk's own CLI** (`tx_inhibit.py <netlist>...`, which prints a table and writes no verdict):
  * The A to D output is identical at both commits (sha256 9b9de585a26e40ed): 13 PASS, 11 UNDECIDED, 0 FAIL.
  * Run on all six boards, the output is also identical (48930f5d9f8711cf).
* **The RF-002 readings** (`check_contracts.py`, `VERDICT_DIR` in scratch, 3.8 s per run): every deciding field of all 13 verdicts is identical at both commits, and so is stdout. The inhibit_chain counts:

* A: INCONCLUSIVE, PASS 7, UNDECIDED 2.
* B: INCONCLUSIVE, PASS 12, UNDECIDED 8.
* C: PASS, PASS 6, UNDECIDED 0.
* D: INCONCLUSIVE, PASS 8, UNDECIDED 1.
* E: PASS, PASS 1.
* P: PASS, PASS 1.
* FAIL 0 and unjudged 0 on every board, at both commits.

## 4. Tests

* **The suite** (`run.py test_tx_inhibit`): 143 passed, 0 failed at b4a34ffa; 142 passed, 0 failed at a1f8ec70.
* **The new test on the old tool** (`cross.py`):
  * 138 of the file's 139 tests pass. The new test fails at line 4043 with KeyError 'lugs', before it reaches any case.
  * Taken one assertion at a time on the old predicate (the table in section 2), every negative assertion fails: the four lug cases, the two keyless calls and the declaration without lugs.
  * The two positive controls hold on both tools, as they should.
* **No existing fixture changed meaning** (`spy.py`). It compared the old and new predicates on all 28,138 `_is_toggle` calls the suite makes (124 tests). They disagree only on the new test's seven deliberate calls. The key arguments added to 13 older test calls change no outcome: the branch's test file passes on the old tool except for the new test.
* **The record script replays exactly.** `apply_walk_minors.py` run on a clean a1f8ec70 clone gives a tx_inhibit.py identical byte for byte to b4a34ffa's. A second run is refused (exit 2).

## 5. Nothing else changed

* `git diff a1f8ec70 b4a34ffa --stat`: four files, 172 insertions and 20 deletions. They are the README, the record script, tx_inhibit.py and test_tx_inhibit.py.
* **The commit:** it is authored as the owner and carries no trailer. There is no em or en dash and `git diff --check` is clean.
* **Merging:** `git merge-tree` merges b4a34ffa cleanly onto main e57a7365, fnd/int13 d0717859 and fnd/int14 3309c9fa. The tool and its test file are unchanged on those lines since a1f8ec70.

## Minor items

1. **`v2/docs/records/walkmin/README.md` lines 3 and 4 cite the wrong check and understate it.**
   * `records/int13/checks/check-set12-1.md` is rf2walk round 1's check (fnd/rf2walk at a444cb37), and it contains neither minor.
   * The minors are items 1 and 3 of `v2/docs/records/int13/checks/check-set12-3.md` (on main, fnd/int13 and fnd/int14; no `int13/checks` directory exists on this branch).
   * That check also carries a third minor on tx_inhibit.py, item 2: the ordinary contact rule is keyed on the SW prefix. It stays open, and the README's "two minors on tx_inhibit.py" hides it.
   * Fix: cite `check-set12-3.md`, map m1 and m2 to its items 1 and 3, and add one line saying that item 2 is not answered here.
2. **`v2/ecad/tools/tx_inhibit.py` line 1726 checks only the length of `lugs`.**
   * `("1", "1")` or integer lugs pass the check and then never match. That is conservative (the line then FAILS on the whole walk), but it is not the refusal the docstring promises.
   * The string `"12"` passes and matches by accident.
   * Fix: refuse unless `lugs` is a tuple of two distinct strings, and consider validating `_TOGGLES_NOW` once at `judge()` entry.
3. **README lines 19 and 20** say the new test "fails on the previous predicate for every miswired case".
   * On the old tool the test stops at line 4043 (KeyError 'lugs') and never reaches the cases. The per case claim is true of the predicate (I reproduced it), not of the test as a file. This is the same shape as round 3's minor 5.
   * Fix: say that the cases were read one by one on the old predicate, or keep the declaration assertion apart from the wiring cases.
4. **No whole walk fixture for T2a.** Round 3 asked for "T2a as a defective fixture". The new test (`test_tx_inhibit.py` lines 4035 to 4067) calls the predicate only.
   * Fix: add a `_line_of` case on `_panel_clamped` with a three lug SW_EMCON wired 1 and 3 (and 2 and 3), asserting that both lines FAIL, as the `kit_mutants.py` runs above show.
5. **README line 4 says `apply_walk_minors.py` "answers them",** but the script edits only tx_inhibit.py. The 51 line test diff has no script and no note of how it was made.
   * Fix: one line saying that the tests were edited directly, or a companion script like w4b's `apply_tx_inhibit_tests_w4b.py`.
6. **No readings are committed with the record,** where stream rf2walk kept before and after contract readings under `records/rf2walk/readings/`. The README leaves the comparison to the integrator's retake.
   * The comparison in section 3 above shows no movement on any board. Filing it, or the retake, beside the README would make the record carry its own evidence.
