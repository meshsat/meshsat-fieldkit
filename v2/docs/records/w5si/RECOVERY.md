# Stream w5si: what was recovered from the transcripts, and how

Written 27 September 2026, 22:40 CEST (MESHSAT-1357, layer 9, rule SI-001). Prototype design work: nothing has been
built or measured. This page is the record of a recovery, not of a check: the recovered work is committed UNCHECKED at
this point, and the three blocking items of the independent check (AI review) of pass 1 are answered after it.

## What happened

Pass 1 of this stream worked on 27 September 2026 in a worktree under `/tmp`, committed nothing, and a reboot deleted
the worktree. An independent checker (AI review) had judged pass 1 not mergeable with three blocking items; a second
author pass read files for 20 commands and was cut off before it changed anything. What survived is under
`<worktrees>/_recovered/` (outside the repository): the files pass 1 wrote with
the Write tool, six Edit calls whose base file was not held, and the shell transcripts of both passes and of the check.

## What was recovered, and the evidence that it is what pass 1 held

| File | How it was rebuilt | Evidence |
|---|---|---|
| `v2/ecad/tools/ibis_read.py` | copied as recovered | sha256/16 `8fd2e9d1f6cb1f4c`, the value the transcript's command 158 printed; 182 lines, as pass 2 counted |
| `v2/ecad/tools/pcb_edge_rates.yaml` | the recovered first write (`d35130f1162a65ee`), then pass 1's ten patch commands run again in order (78, 88, 89, 94, 115, 119, 121, 132, 136, 137) | sha256/16 `26ef827a1d9ff277`, the value command 158 printed and the record names; 899 lines; 6 interface records, 58 families, 29 far ends, as command 159 counted |
| `v2/ecad/tools/edge_length.py` | `c23c5e76`'s file, the three Edit calls, then commands 74, 75, 85, 94, 97, 98, 111, 118, 132, 138, 160 | at command 158's point sha256/16 `ea1b2211c8ff4f7a`, the value it printed; after command 160 (a comment block) `6818fc98e88aa08b`, 1159 lines and a diff of 621 lines against `c23c5e76`, as pass 2's `git diff --stat` and `wc -l` showed |
| `v2/ecad/tools/tests/test_edge_length.py` | `c23c5e76`'s file, command 113's appended text, command 114's `sed`, the fourth Edit call, command 120 | 28 tests, 564 lines, 261 lines inserted, as commands 159 and pass 2's `git diff --stat` showed. No hash of this file is in any transcript |
| `v2/docs/records/w5si/recovery/pass1-drafts/apply_rules_status_config_inputs.py.superseded-do-not-run` | recovered write, then command 131 | 5117 bytes, the size pass 2's `ls -la` showed |
| `v2/docs/records/w5si/recovery/pass1-drafts/apply_sources_yaml_ibis.py.superseded-do-not-run` | copied as recovered | 6939 bytes, as pass 2 showed |
| `v2/docs/records/w5si/recovery/pass1-drafts/apply_coverage_si001.py.superseded-do-not-run` | recovered write, then command 149's `sed` | 6752 bytes, as pass 2 showed |
| `v2/docs/records/w5si/recovery/pass1-drafts/apply_board_b_declarations.py.superseded-do-not-run` | the recovered `apply_board_b_rf_classes.py` renamed (command 156), the fifth and sixth Edit calls, then command 157 | 6677 bytes, as pass 2 showed. THIS DRAFT IS THE ONE THE CHECK FOUND DEFECTIVE (blocking items 2 and 3); it is filed as it was and replaced later in this stream |
| `v2/docs/records/w5si/recovery/pass1-drafts/w5si-record.md` | recovered write, then command 160's one-line change | 15440 bytes. It carries the wrong "maker-held" counts of blocking item 1; it is filed as it was and superseded later in this stream |
| `v2/docs/records/w5si/recovery/pass1-drafts/readings/bound_decides.txt`, `compare.txt`, `headlines.txt` | cut out of pass 2's command 2, which printed the three files whole, one after the other | 7012, 696 and 4516 bytes, the sizes command 158 printed; `compare.txt` also equals command 146's printed output |
| `v2/vendor/ti/ibis/*.ibs` (12), `v2/vendor/st/ibis/stm32h742_743_750_753_lqfp100.ibs` | FETCHED AGAIN from the URLs in the transcript, 27 September 2026 20:33 UTC | see the table below: all 13 are the same bytes |
| `v2/vendor/sources.txt`, `v2/vendor/vendor-status.txt` | 13 lines appended to each, from command 71's tables | the `sources.txt` lines are NOT pass 1's text: each now also states the second fetch and the file's sha256/16. The `vendor-status.txt` lines are pass 1's |
| `v2/docs/records/w5si/check-1/` | the checker's result, and its two evidence files cut out of pass 2's command 3, which printed them | 4472 and 1945 bytes, the sizes its `ls -la` showed; the lost scratchpad's path is replaced by `<lost scratchpad>` in the diff's two header lines |
| `v2/docs/records/w5si/recovery/replay.py` | new | the replay itself: run on an empty staging directory it gives the files above byte for byte |

**The six Edit calls of `EDITS-NOT-APPLIED.txt`: all six applied, each old text found exactly once.** Three are on
`edge_length.py` and come before command 74, one is on the test file between commands 119 and 120, and two are on
`apply_board_b_declarations.py` between commands 156 and 157. Each place is fixed by what the next patch asserts.
Command 156's own Python raised `SyntaxError` in the transcript and changed nothing, so only its rename is repeated.

## The 13 IBIS models, fetched again

Twelve from ti.com directly, ST's through the Internet Archive because st.com refuses this host (capture
`20250911224858`, served gzip-wrapped, the wrapper's sha256/16 `d0ecb57c18b83077` both times).

| File | From | Bytes | sha256 | Against the transcript (command 133) and the SOURCES draft |
|---|---|---|---|---|
| `ti/ibis/sn74lvc08a.ibs` | `https://www.ti.com/lit/zip/SCEM010` | 193205 | `adb5d455adc3a057282075c94d7454b01a37d720ac993db1d1eeea9e5eda9779` | identical |
| `ti/ibis/sn74lvc32a.ibs` | `https://www.ti.com/lit/ibs/SCEM055` | 195184 | `396e2d220f1cc59f07c11d98a9294bcf5f44cc09db4802354ff318c7b99f4499` | identical |
| `ti/ibis/sn74lvc86a.ibs` | `https://www.ti.com/lit/zip/SCEM060` | 190085 | `0f9780c8d3fd9b898438a57c8624469e46df247ccbda073fc14db15b79a53eb8` | identical |
| `ti/ibis/sn74lvc1g00.ibs` | `https://www.ti.com/lit/zip/SCEM165` | 245022 | `e085986b1ed2969ed7312e201a68197865a8342e576793408dcd7e19ea92abb4` | identical |
| `ti/ibis/sn74lvc1g04.ibs` | `https://www.ti.com/lit/zip/SCEM216` | 254207 | `03033638d7fe8bf268428be133a5aad63aae0145980113561b20ab92063e2c00` | identical |
| `ti/ibis/sn74lvc1g57.ibs` | `https://www.ti.com/lit/ibs/SCEM292` | 247448 | `7abbc41dad6b027a0061534f7ba31dfa74e827b8d339381b1e9daf653078198d` | identical |
| `ti/ibis/pca9555.ibs` | `https://www.ti.com/lit/zip/SCPM035` | 551360 | `56c19a4da921e38cdfb67c3c24d2ea98ce63beae787de611d5e50378e497b300` | identical |
| `ti/ibis/tcan33x.ibs` | `https://www.ti.com/lit/zip/SLLM313` | 199181 | `0e5a9429146148c11252dcea4c5dacc3386634c4cb492bd641a24a1d31fe508b` | identical |
| `ti/ibis/ina226.ibs` | `https://www.ti.com/lit/zip/SBOM458` | 176240 | `fb4ebf43bde617c24a1a15d3c8ad57731e1cf5abf6ad66631f435248185396f8` | identical |
| `ti/ibis/tmp117.ibs` | `https://www.ti.com/lit/zip/SNOM652` | 217886 | `5c71fbcce9e138034fbe4d3053bbb2340af30e327053e3eb092144322d862391` | identical |
| `ti/ibis/ads1x1x.ibs` | `https://www.ti.com/lit/zip/SBAM025` | 109336 | `c9975d3cb6ad0161d4c41a26e18316c4d3c6fb61b839121032b1de16f68a1ac2` | identical |
| `ti/ibis/tusb8041rgc.ibs` | `https://www.ti.com/lit/zip/SLLC445` | 884316 | `925a6c7f6917401ed6252237ee8fc9c2e4106771d177832dfe5f7dabe11c2f7d` | identical |
| `st/ibis/stm32h742_743_750_753_lqfp100.ibs` | `https://web.archive.org/web/20250911224858id_/https://www.st.com/resource/en/ibis_model/stm32h7_ibis.zip` | 1935427 | `0fb7767c1ee034db0cd4d9c92334f4860ddb1980d3fba950c3109f0fc5bc1bc8` | identical |

**Differences: none.** The recovered `pcb_edge_rates.yaml` names no hash of an IBIS file (it names each file by path
and states the edge the model must give, which `edge_length.py` checks on every run); the hashes pass 1 recorded are
in the transcript's command 133 (all 13, in full) and in `apply_sources_yaml_ibis.py` (9 of them, in full). All agree
with the files fetched today.

## What was NOT recovered

- Pass 1's scratch readings (`before/`, `after/`, `r8preview/`: the verdict and table JSON per board). They were never
  in the worktree. They are taken again by this stream with the recovered tool, outside any tree.
- Pass 1's scratch analysis scripts (`analyse.py`, `answered.py`, `ibis_ramps.py`). Their text is in the transcripts;
  they decided nothing and are not rebuilt.
- The checker's scratch outputs other than its two evidence files.

## Moved

Pass 1 kept its drafts in `drafts/w5si/` at the repository root. At the checkpoint (commit `da0f6266`) they were filed
under the records folder's `drafts/`, byte for byte. Since commit `f4533205` they are under
`v2/docs/records/w5si/recovery/pass1-drafts/`, which is where the table above names them, and the four apply scripts
carry the suffix `.superseded-do-not-run`: one of them deletes four USB pair classes from `gen_pcb_b3.py` (the
independent check's second blocking item) and none may be run by mistake. Their bytes are unchanged;
`git show da0f6266:` gives each under its first name. The drafts the integrator runs are the re-issued ones under
`v2/docs/records/w5si/apply/`.

## After the checkpoint: what the recovered work gave when it was run

Run on 27 September 2026 after commit `da0f6266`, before anything of the second pass was written.

| What | Result |
|---|---|
| `python3 run.py test_edge_length.` from `v2/ecad/tools/tests`, in the worktree | 28 passed, 0 failed, 0 skipped: the count pass 1 reported |
| the ibis reader's tests | they are two of those 28 (`t_ibis_reader_*`); no separate test file exists |
| the recovered tool on the six committed netlists, written to scratch outside any tree | the six "after" headlines of pass 1's `headlines.txt`, word for word; the tree's own evidence untouched |
| the tool of `c23c5e76` on the same netlists, in a scratch extract | the six "before" headlines of the same file, word for word: decided 64, undecided 765 |

So the recovered instrument is the one pass 1 described and the independent check read. What the check found wrong
with it is answered in `w5si-record.md`.
