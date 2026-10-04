# int29: the result of integration set 29 (the candidate, the gate, the promotion)

Prototype design: nothing here has been built, bought, powered or measured. This page is written after the gate, as
`README.md` of this folder says. **Promotion of this set is an integration milestone only: it closes no power item, is not
power-design closure, completes no layer and releases nothing for fabrication.** The states the set carries are in `README.md`,
section "What this set changes nothing about".

## 1. The candidate

| What | Value |
|---|---|
| Candidate | `aa76c89448ec943e3a37357ebc11ce3322fa4020` on `fnd/int29`, 91 commits on main `64cd25ee` (set 28 with its record) |
| Its manifest (`v2/ecad/tools/candidate_guard.py record`, kept outside the tree) | the commit and its tree; 990 evidence files, each with its sha256; four historical outputs declared unbound by path (`records/cx1/checks/check-1-phase1.out`, `records/h2/handover_counts.out`, `records/h3/handover_counts.out`, `records/s99/dev_stage.out`); L4-E7's results cache frozen |
| Changed after the freeze | nothing: the commit that was gated is the commit that was promoted |

## 2. The gate, on that exact commit

`_bin/suite_gate.py` on three passes, as for set 28, with the guard's check before each pass:

```
suite_gate: candidate aa76c89448ec; totals tests: 2838 passed, 0 failed, 14 skipped + tests: 48 passed, 0 failed, 0 skipped + tests: 51 passed, 0 failed, 1 skipped; result lines 2952 (2937 PASS, 15 SKIP, 0 FAIL); modules 232 of 232 ran
suite_gate: PASS
```

| Pass | Where | Modules | Result | Guard before the pass |
|---|---|---|---|---|
| A | the rented box, Python 3.12 with KiCad's pcbnew | every module but the three below | 2838 passed, 0 failed, 14 skipped | PASS, 990 evidence files present and unchanged |
| B | the rented box, Python 3.11 | `test_l4e10`, `test_l4e12` | 48 passed, 0 failed, 0 skipped | the same check |
| C | the runner, Python 3.11 | `test_l4e7` (its results cache is keyed on the runner's interpreter and pdftotext) | 51 passed, 0 failed, 1 skipped | PASS, 990 evidence files |

The tree was unchanged after each pass (`git status --short` empty). **The 15 skips, each explained:** `test_fw_panel` 11 (the
box has no C compiler or make, so the panel firmware's host tests and contract probes do not run there; accepted at set 28, and
set 30 installs a compiler so that they run in the gate), `test_finish_order` 1 (the box holds a second clone at the path the
profiles pin), `test_pairsearch` 1 (no numba on the box; the two other kernels are compared), `test_per_board_contract_verdict` 1
(the test of a host without pcbnew cannot run where pcbnew exists), `test_l4e7` 1 (the solver's own re-run, gated by design).

**Measured durations (4 October 2026, UTC stamps of the box).** Passes A and B together, from launch to the done stamp,
including the clone, the evidence install and the guard: 17:26:09 to 18:00:17, 34 min 8 s. The prepared instance was resumed, so
no host setup time is in that figure; the resume took about 20 s and the transfer of the 180 MB evidence archive under a minute.
Pass C took about one minute. Set 28's same run took at most 34 minutes.

## 3. A first run that was not gated (the coordinator's error, kept here as such)

The first box run on this candidate (16:48:52 to 17:22:29 UTC, 33 min 37 s) read 2778 passed, 0 failed, 74 skipped in pass A.
Sixty of those skips were tests of three records that could not run: `test_l4e11` 53, `test_l8p` 6 and `test_l8r2` 1, each for a
held maker's sheet absent from the evidence archive (four San Ace catalogue pages, the HOLLR2512 shunt's sheet, TI's OPA187
sheet). The manifest had been recorded with set 28's list of 984 evidence files, while the candidate's checkout held 990: the six
sheets this set's records added were not on the list. The gate's conditions G1 to G6 all held on that run, because the gate did
not judge skips. It was not used. Corrected in three steps:

1. the manifest recorded again at the same commit with every ignored file of the checkout (990: the 984 unchanged, the six added;
   the commit, its tree, the declared unbound outputs and the frozen cache equal to the first manifest's), and the archive built
   from that manifest's own list;
2. passes A, B and C run again against it (section 2);
3. the gate given a seventh condition, G7: every SKIP line must match a declared explanation, and a skip whose reason names a
   missing input is refused whatever is declared. Its regression reproduces this failure (the earlier gate passes the same log);
   on the real logs it refuses the first run and passes both set 28's promoted run and this set's second run.

## 4. The promotion

Main was fast-forwarded from `64cd25ee` to `aa76c89448ec943e3a37357ebc11ce3322fa4020` on 4 October 2026 at 20:01 CEST and pushed;
the public mirror read the same commit a few seconds later. `candidate_guard.py check` passed on main after the fast-forward, with
the 990 evidence files installed. The governance commit that follows it on main (`d16bb2c3`: the owner's execution constitution,
his instructions of 4 October as received, the plan entry) is outside the candidate and was checked by its affected modules only
(`test_handover_pack`, `test_public_hygiene`, `test_l4e7`: 71 passed, 0 failed, 1 skipped).

## 5. Five claims, apart

| Claim | State after this set |
|---|---|
| Documents and editable artifacts of the merged rounds | on main, as drafts |
| Design reviewed and accepted | no, beyond the named checks, each quoted as given in `README.md` and `LAYER-STATUS.md` |
| Circuit changes implemented | none: every change is a release-guarded draft; no generator changed, no board regenerated |
| Physical qualification | none |
| Fabrication release | BLOCKED; the power-design closure gate BLOCKED |

Open after this set, each until its checked correction or its named evidence: F01 / D-17, I-03 / L9P-F03, L9P-F04, E-1's sharing,
E11-37, DD-3, DD-5, B6 (D-10, D-16), U-01, U-02, U-04, the outer copper weight of boards A and E (the owner's decision), and the
residues S29-R1 to R4 and R6 to R8 of `README.md`. The corrections of set 30 are on branches and are not in this commit.
