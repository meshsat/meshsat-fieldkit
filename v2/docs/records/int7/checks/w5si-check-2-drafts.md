# Fresh check, lens drafts, of stream w5si at 7f7721c4 (AI review), 28 September 2026

**AI review, lens "drafts", of fnd/w5si at 7f7721c4. This is not a qualified engineering review. Prototype design: nothing built, ordered or measured.**

`mergeable: no` as the branch and drafts stand. The engineering content holds and all five drafts apply at int7. What blocks is publication of the 13 IBIS models and two drafts that write wrong text at int7.

Tested against int7 at 1c4235ec as instructed. int7 moved to 85ad1193 during the check; of the files involved only `pcb_requirements.yaml` changed, and the CFL-016 binding below is still there.

## blocking

**B1. The 13 IBIS models are tracked on the branch, and the drafts assume they are committed.**
- problem: a merge carries the 13 files into history, so a push publishes them. int7's standing decision holds them back (`v2/docs/EXECUTION-PLAN.md` lines 311 and 322 at 1c4235ec). No fetch script or ignore rule exists on either line.
- evidence: `git -C .../w5si ls-tree -r --name-only 7f7721c4 -- v2/vendor/ti/ibis v2/vendor/st/ibis` lists 13; they enter in the first commit da0f6266, so every commit of the branch carries them. fnd/int7, fnd/r8int6, fnd/h3 and main hold 0.
- header wording, `sn74lvc08a.ibs` lines 32-33 and 52-54: "Property of Texas Instruments Incorporated. Unauthorized reproduction and/or distribution is strictly prohibited." and "You and your company shall not distribute, sell or give these models to anyone else without prior written permission from TI." `pca9555.ibs` lines 35-36 and 55-57 say the same.
- that wording is in 5 of the 13 (pca9555, sn74lvc08a, sn74lvc1g04, sn74lvc1g57, sn74lvc32a). The other 7 TI files and ST's carry only a copyright line ("All rights reserved"; ST line 13), with no grant.
- counter_example: simulated `rules_status._config_state` in memory on board C's scratch reading, with the CONFIG_INPUTS draft applied and git answers patched:

| State of the models | Result |
|---|---|
| committed before the reading | BOUND |
| present, never committed | CONFIG_CHANGED, `../vendor/ti/ibis/sn74lvc08a.ibs` "cannot be dated by a commit" |
| absent | CONFIG_CHANGED, "the reading recorded sha 0fb7767c1ee034db and the file is absent" |

- so the only state that reads current is the one that publishes. Board C's reading records 6 of the 13 models; the draft declares all 13 for every board.
- needed: integrate by a squash that leaves the 13 files out, add an ignore rule and a fetch manifest, and re-issue the CONFIG_INPUTS and SOURCES drafts.

**B2. `apply_coverage_si001.py` writes two false sentences when the models are withheld.**
- problem: it does not refuse; the sentence about the models and the reason given for the undecided nets are typed, not derived.
- counter_example: on the merged scratch tree with both `ibis` folders moved away, `--dry-run` exits 0 and would write "13 models filed under v2/vendor/ti/ibis and v2/vendor/st/ibis" and "undecided A 43, B 390, C 11, D 11, E 0, P 15 (470, the nets no signal-class declaration names)". Only 73 of the 470 have that reason; 397 are undecided because a model file is not in the tree.

**B3. `apply_decisions_w5si.py` applies silently at int7 with two stale pointers in its third row (decision 50).**
- problem: the evidence reads "the committed netlist of board B (sha256/16 8b78c59754a6a0c7), gen_sch_b.py line 1151".
- counter_example: at 1c4235ec the netlist is 028997a6c5e8810f, line 1151 is `elif nm in ("GND", "E_PAD"): k[n] = "GND"`, and the BOB line is 1191. The facts themselves hold on set 6 (BOB = R9.2, R10.2, C33.1; 75, 75, 1n 2kV). A two-token fix.

## minor

- **M1.** After the decisions draft, `pcb_requirements.yaml` stops validating: CFL-016 is bound to `pcb_decisions.yaml@b5f7162443d5ad91` and the file becomes 1248e9013306edc1. It fails loudly; a rebind is owed. It is the only one of 52 bindings that moves.
- **M2.** After the coverage draft, `PCB-GOLDEN-RULES.md` and `PCB-GAP-REGISTER.md` go out of date (`rules_render.py --check` in scratch: 1 out of date before, 3 after). The draft does not say a re-render is owed.
- **M3.** With the models absent, `test_edge_length` reads 35 passed, 1 failed (`t_si001_the_data_file_holds_against_its_documents_its_models_and_the_committed_netlists`). A clean clone without the models would fail the suite.
- **M4.** No draft asserts that the stream is merged. On int7 without the merge, the board B and decisions drafts apply; the other three stop on AttributeError or FileNotFoundError and write nothing.
- **M5.** The SOURCES draft gives URL and full sha256 for 9 models. The other 4 (sn74lvc08a, sn74lvc32a, ina226, tmp117) get only an owed line. Each sha is of the extracted `.ibs`, while most URLs are zips.
- **M6.** The 13 new `sources.txt` lines say each file "carries the maker's copyright and redistribution notice, held under this folder's README terms". Eight carry no redistribution notice, and those terms are publish-as-is. Record sections 12.1 and 12.5 need the same amendment.
- **M7.** Coverage paragraph wording: "after an independent check" lacks the AI review label. "Decided by a maker's figure on every driver (138)" includes 64 nets decided by the USB 2.0 class records (56 at 0.5 ns, 8 at 4.0 ns); 74 are by IBIS cells.
- **M8.** PCA9555_INT_33 `[Ramp]` gives 0.121 ns while its own V-t table gives 0.605 ns. It errs short and governs no net.
- **M9.** The CONFIG_INPUTS entry names netlists by phase directory, so board C's next phase needs `--refresh`. The author states this limit.
- **M10.** `F-BOB-common-mode-termination.md` cites the same line 1151 and base sha as B3.

## verified

1. **Inventory.** Five drafts plus `_pyedit.py`. All assert anchors, re-parse, compare structure before and after, and refuse a second run. Two have no explicit "differs" assert, but their length checks imply it. `selftest.py`: 11 checks, 0 failures.

| Draft | Edits | Change |
|---|---|---|
| `apply_rules_status_config_inputs.py` | `rules_status.py` | `CONFIG_INPUTS["edge_length.py"]` 6 to 76 inputs |
| `apply_sources_yaml_ibis.py` | `v2/vendor/SOURCES.yaml` | 9 document rows, 1 owed line |
| `apply_board_b_declarations.py` | `boards/b.json`, `gen_pcb_b3.py` | 3 entries; PATTERNS 40 to 41 |
| `apply_coverage_si001.py` | `pcb_rules_coverage.yaml` | SI-001 note +2802 characters, remediation action |
| `apply_decisions_w5si.py` | `pcb_decisions.yaml` | rows 48 to 51 |

2. **Apply tests.** `git merge-tree` of 1c4235ec and 7f7721c4 conflicts only in `v2/vendor/sources.txt` and `vendor-status.txt`. `edge_length.py`, `gen_pcb_b3.py` and `pcb_decisions.yaml` are byte-identical at base and int7. Every anchor stands exactly once at int7.

| Draft | Base | int7 merged, models present | int7 merged, models absent | Second run refused |
|---|---|---|---|---|
| config inputs | yes | yes | refuses | yes (and `--refresh`) |
| sources | yes | yes | refuses | yes |
| board B | yes | yes | yes | yes |
| coverage | yes | yes, set 6 counts | applies, false text (B2) | yes |
| decisions | yes | yes, stale pointers (B3) | same | yes |

3. **Declared edges.** The board B draft declares classes, not edges; its basis text holds (SKY13351 datasheet: INPUT pin 5, OUTPUT pins 1 and 3; C500 to C505 are 22p; LG290P RF_IN is pin 11; intent holds RF z_se 50).
   - I checked 15 figures with my own reader: all 13 IBIS family cells equal their files at the cited sha, and both USB figures are in the held transcription.
   - The 138 maker-decided nets rest on six IBIS cells and two USB records. All six cells have dV at 0.60 to 0.64 of the V-t swing.
   - The first lens's M5 caveat applies only to TMP117 (0.15), which governs no net.

4. **Registries.** The four rows carry authority SESSION, authority_why, ruled_by, ruled_on 2026-09-27 and reversed_by. Decision 51's 82 nets on A, B, C, E recount as 57, 14, 1, 10.
   - With all five applied on both trees: `rules_lib.py` 59 rules, 0 errors; `decisions_render.py --check` passes once the page is regenerated.
   - Tests: test_decision_register 3 passed 2 skipped, test_rules_registry 5, test_edge_length 36, test_signal_class 8, test_netclass 8, test_rules_status (merged tree) 35 passed 1 skipped.

5. **CONFIG_INPUTS.** Adds the data file, 63 documents and models (13 `.ibs`), the search listing and six netlists. All exist when the models are in the tree. The re-take owed is SI-001 on a, b, c, d, e, p together, because the tool itself changes and the existing compatibility entry covers the old bundle.

6. **Fail closed.** With the models absent all six readings are INCONCLUSIVE and none passes. Counts go to maker 64, bound 293, undecided 470, each naming the absent file.

7. **Board C** on the set 6 netlist (3fddbb3edcd4248a), stream tool in the merged scratch tree, written to scratch: INCONCLUSIVE.

| | Models present | Models absent |
|---|---|---|
| Decided by a published figure | 4 | 4 |
| Decided by a bound | 29 | 22 |
| Undecided | 4 | 11 |

   - 134 signal nets, 97 slow, 37 non-slow. The committed int7 reading has 4 decided and 33 undecided.
   - The 4 by a figure are USB_DM_R, USB_DP_R, USB_PNL_N, USB_PNL_P (USB 2.0 full speed, 4.0 ns).
   - The 4 undecided are EMCLAMP_G, EMCLAMP_Y, EMCON_RD, EMCON_RD_R, each "no signal-class declaration". The stream drafts no declaration for them.
   - Of the 33 decided, 10 are answered and 23 are layout-bound, all BOUND_DECIDES.
   - With the models absent, the 7 more undecided are EXP_INT, HB1 to HB3, Q3_G, SCL, SDA, through far-end parts on boards A and B.

8. **Prose.** No em dash or en dash in the records folder, the drafts, the data file or the tools. Prototype framing is present and bounds are named bounds. Exceptions are M6 and M7.

## not_done

- Anything that dates by commit on a real repository: the scratch trees were not git repositories, so CONFIG behaviour is from the code and the patched simulation.
- The full suite, KiCad and the rented box: not run.
- `edge-search.txt` was not re-derived, and the 39 bound families' documents were not re-searched.
- The USB-IF's own PDF is not held; the transcription was read.
- The signal-class declarations (738 slow nets) and what class the four undeclared board C nets should take.
- `recovery/replay.py`, the superseded first-pass drafts and the second half of `F-Q1-power-stage-nodes.md`.
- Whether int7 at 85ad1193 changes any result beyond the file comparison above.

The worktrees w5si and int7 and the main checkout are unchanged. Scratch evidence (1.5 MB, no model files) is kept in `/home/claude-runner/worktrees/meshsat-fieldkit/_scratch/chk-w5si-drafts-2/`.
