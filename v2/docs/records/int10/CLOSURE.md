# Integration set 9: closure record (MESHSAT-1357, 29 September 2026)

Branch `fnd/int10` onto main `9147db5d`; the final candidate is the commit that carries this file. Prototype design: nothing here has been built, ordered or
measured. The checks named below are AI reviews, not qualified reviews.

## What the set changes, by class

| Class | Change | Commits |
|---|---|---|
| Circuit | S-99's corrected D8 split on board A (decision 55): the TPS62933 buck U41 from VBAT on the new rail `+5V_D8IN` (56.2k over 10.7k at 0.1 percent, 4.872 to 5.133 V) feeds the eFuse U23 and board D; the LM5176 device stage keeps board B's 6.0 A and the wall host port; the TPS2596 limit resistors unchanged, their printed limits re-read by equation 7's true sign (U32 0.9142 A, U39 0.20 A). Board A regenerated on the KiCad box: ten parts added, none removed, ERC exit 0, check_contracts PASS of 99, the five A to B leads AGREE | `605ece61` (stream s99a), `c1137542` |
| Declaration | board A's intent: `+5V_DEV` 4.10 A typical and 6.9142 A peak (5.10 and 6.90 before), `+5V_D8IN` 1.0 and 2.0 A, `VBUS_WALL` peak 0.91 A; the IF-AB-POWER, IF-AD-HARNESS and IF-AB-WALL rows and their generator line citations; the wall port at 0.9142 A in `HW-FW-CONTRACT.md` and `ASSEMBLY.md` | `c1137542`, `0763c01f` |
| Registry | S-99 re-stated and left OPEN with what decides each remaining part; S-115 (board A's layout generator, LAYOUT_STAGE) and S-116 (board D's codec floor at the 2.0 A peak) opened; decision 55 recorded (SESSION); REQ-072's energy note (FAIL unchanged); S-98's lead-drop figure corrected in its own records (0.248441 V, 4.87 percent of 5.1 V) | `0763c01f` |
| Pins and bindings | the netlist pins of the decision 31 hold, the reliability list and the reviewed port set moved on a parsed proof (22 reviewed external pins on the same nets, the reliability inventory 82/57/25/0 unchanged); layout constraint sheet A re-bound with every moved or new row explained (`+5V_DEV` 2.84 to 2.10 mm on an outer face); four records bound to `gen_sch_a.py` rebound on a parsed (ast) proof that no call they read differs between set 8's generator and set 9's, eight bound to board A's netlist on judged reasons; CON-010 and REQ-044 rebound to the final evidence page | `01b6d9bb`, `a2033760`, `0763c01f`, `03237888` |
| Evidence | one consolidated re-take at `cef7cb77` (re-authored as `ad9f53c7`, the same tree; see Identity below): 73 steps, 0 errors (the two FAIL verdicts are INT-001 on E5 and BAT-001 on P, as on main); board A's seven moved readings follow its ten new parts and one new rail with no verdict changed; 34 layout-entry reasons, as on main | `a7e411ec`, `03237888` |
| EMC | board A's EMC sheet declares the new buck U41 (TPS62933, RT open, 500 kHz, TI SLUSEA4D Table 7-1), which the suite's completeness test found missing | `27d8a129`, re-authored `20e7f7b4` |
| Records | stream energy (the reconciliation of M1 and REQ-072, accepted after four checks) and stream od01 (the case package, accepted after two checks) merged; the records index lists all 64 folders | `3ea5a994`, `8eca1ef3`, `589d7394` |

No checker was corrected in this set.

## Gates

| Gate | Result |
|---|---|
| Validators on the candidate | rules_lib 59 rules and 144 records, 0 errors, 0 warnings; every `--check` exit 0 |
| Isolated clone at `03237888` with only the evidence archive (`int10-evidence-03237888.tar`, 929 files, sha256/16 `88714d4257a48fcd`) | status 0 lines after status x3 and render x2; CURRENT-EVIDENCE.md `f1050e398b6bc2e0` and REQUIREMENTS-TRACE.md `2f113a1c81973416` byte-identical |
| Full suite on the box | at `03237888`: 2170 passed, 1 failed (test_emc_sheet: U41 undeclared), 3 skipped; fixed by the EMC row. At `27d8a129` (the tree of `20e7f7b4`): 2171 passed, 0 failed, 3 skipped. At `40dd2690`: 2170 passed, 1 failed (test_constraints_bound's real-tree test: the sheet tool wrote a sheet input's last commit with git's automatic abbreviation, which grew to 9 characters in the box's larger repository, so every re-emitted sheet read as moved; a tool defect the re-authoring's new objects exposed, not a change of any sheet). Fixed in `constraints_bound.py` (the full hash cut to 8) with a regression test that forces git's abbreviation to 12 and fails on the unfixed tool. The run on the commit that carries the fix is recorded in `v2/docs/EXECUTION-PLAN.md`'s milestone entry for set 9 |
| Fresh AI check (`CHECK.md`, at `27d8a129`) | mergeable: no, on one blocking item (B1, below); the engineering reproduced: the netlist change, U41's pins and divider (4.8718 to 5.1329 V), equation 7 (0.9142 and 0.2033 A), the +5V_DEV margins, sheet A byte-identical, 34 layout-entry reasons, no verdict moved |

## Identity (the check's blocking item B1)

Four merge commits of this set (`3ea5a994`, `8eca1ef3`, `b11e6a16`, `cef7cb77`) were made without the owner's identity
flags and carried the runner's service identity, which the repository's rule forbids and which a fast-forward would have
published. They were re-created with identical trees under the owner's identity and every later commit carried across
(`box/reauthor.map`, old and new sha per commit; each new tree asserted equal to the old). The re-take's readings record
`git_head` `cef7cb77c420`, the commit they ran at; its re-authored twin is `ad9f53c7`, with the same tree, so the readings
describe exactly the tracked content of the published history. No tracked file outside the readings names a rewritten sha.
The side branches `fnd/energy2` and `fnd/diag` were moved onto the rewritten line the same way.

## The check's minor items

Answered in this set (`apply_check_minors_s99.py`): **M1**, four judged rebind entries (CFL-005, CON-010, CFL-016,
CFL-014) said U39 and R209 appear "only" in an earlier rebind entry, where U39 also appears in each record's re-read of
PANEL.md or EMCON.md about its overvoltage lockout and fault line; corrected, the conclusion unchanged. **M7**, S-99's
closing list no longer names the work this set did. **M4**, the erratum no longer calls a board A review owed by the
regeneration.

## What it does not claim

S-99 stays OPEN: the declared demand sits under the LM5176 average loop's conditional minimum, which is a statement about
declarations, not a demonstration of capacity; the mode currents, the M and P tiers against the loop, the output
capacitors' bias derating and U41's thermal reading on copper stay open with what decides each. No layer closes; layer 10
stays BLOCKED (0 of 7 boards pass layout entry) and layer 11 NOT STARTED.

## Carried to the next set

| Item | What | Where it goes |
|---|---|---|
| M2 | IF-AB-POWER's +5V_DEV row cites "gen_sch_a.py, the S-99 lines" instead of line 140 | the next set's interface edit (the file is a pinned input of the interface readings, so it moves with a re-take) |
| M3 | "4.872 to 5.133 V over every tolerance" (decision 55, the intent note, sheet A) is a DC set-point band without PFM ripple and load-step overshoot | S-99 item (d) already carries the ripple and overshoot; the wording in the generator's note and decision 55 at board A's next generator change |
| M5 | the pin proof would not catch a non-connector part added to an external net (checked directly here: no external net changed) | `apply_repin_circuit_s99.py`'s successor for the next circuit change |
| M6 | board D's +5V_D8 note (4.90 V) and the SA_PTT_n band at `gen_sch_d.py:430-434` quote the old source (shifts of 9 and 54 mV) | board D's next generator change, with S-116 |
| M8 | ASSEMBLY.md bring-up step 3 does not list +5V_D8IN | the next set (ASSEMBLY.md is pinned by CFL-015, so it moves with that record's rebind) |
| M9 | IF-AB-POWER's "7.2 to 9.5 A", the "22u 10V" part text against a 25 V part, the certification lines owed | as recorded by stream s99reg |
| M10 | board A's EMC sheet does not declare U3, the BQ25731 charger (400 or 800 kHz with dithering, SLUSE66A); `emc_sheet.py`'s switcher list has no BQ25731, so its test cannot see it; main has the same gap | a tool item and a sheet row, next set |
| M11 | the U41 row could carry its spread (SLUSEA4D 8.5 and 9.3.10) and name J_MEZZ_PWR1; the sheet's prose still says "five LM5176" and "all five converters" | with M10 |
| diagrams | `build.py --check` reads 2 of 11 current (drawn at `b7f96784`); the power tree still draws board D's feed from +5V_DEV | branch `fnd/diag` (the power tree re-typed and checked by its own walk); rendering on the box after promotion |
