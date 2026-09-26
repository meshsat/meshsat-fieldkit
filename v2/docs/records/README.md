# Session records cited by the committed pages

MESHSAT-1357, filed 26 September 2026 (stream `records`, from main `45bde541`). The MeshSat field kit V2 is a prototype design: no board of the set has been built, and nothing in this folder has been measured on hardware.

## What this folder is

The foundation session of 25 and 26 September 2026 worked in git worktrees, one per stream (branches `fnd/<name>`), and kept its working files in each worktree's untracked `drafts/` folder: the scripts it ran, their outputs, the netlist readings, the decision logs of each board's author and the lists of documents it fetched. Committed pages cite those files, and no reader of the repository could open them. They are filed here so an outside reviewer can.

- **Layout.** `v2/docs/records/<worktree>/<the same path below drafts/>`: `drafts/dec_loop.py` of worktree `fnd/rv-dec` is `rv-dec/dec_loop.py` here.
- **Records, not repository tools.** No test, gate or generator runs them. A script here keeps its original text, including paths into `drafts/` or onto the rented build box (`/root/...`) that only existed where it ran; the table below maps every such `drafts/` path to its place here.
- **Byte for byte**, with two exceptions: in `rv-dec/PCB-OPEN-PAIRS.decision-42.isolated.diff` and `r4b/box/r6-run6/check_pcb_b/emul-r6-gate-on-round6.txt` the absolute path of the session's scratch directory on the build host is replaced by `$SP` (the notation `MESHSAT-709-geometry-appendix.md` already uses for it). The table gives the filed sha256, and the section *Rewritten on filing* gives the worktree file's.
- **Not filed here** (sections below): maker documents, which belong in `v2/vendor/` with the parts stream; netlists and box run directories that are over 1 MB or that the repository's history already holds, each with its sha256 and the command that rebuilds it; third-party web page snapshots the battery packet chose not to publish. Nothing filed holds a credential or personal data; the only mail addresses in the folder are two companies' published functional ones (AsiaRF's sales address in `rv-pwr/pwr-maker-questions.md`, Jauch's battery-technology address quoted from its web page in `rv-bat/datasheets/SOURCES.txt`).
- **The session's choices in this filing** (taken by the session under the owner's standing rule of 26 September 2026): a file whose bytes the repository already holds is not filed twice, it is pointed to; a netlist that differs from a committed one only in its `(source ...)` and `(date ...)` header lines is rebuilt by a command whose output hash is checked here, not filed; the outputs of the scripts `DECOUPLING.md` section 11 cites are filed with them, because that page cites the scripts "and their outputs"; the two box scripts that `r4b/box/r6-run6/README.txt` names as the run's driver are filed with it.
- **A decision log is filed whole**, as its worktree held it when this was filed. `r4t/r4-decisions.md` is a snapshot of a file another loop was still editing (worktree file modified 20:50 CEST); see *Cited but not found*.

Worktrees:

| folder | whose records |
|---|---|
| `r4a/` | board A's author, rounds 4 to 6 (round-6 candidate, fix-ups 3 and 4) |
| `r4b/` | board B's author, rounds 4 to 6 (round-6 candidate, box run 6) |
| `r4e/` | board E's author, round 4 |
| `r4p/` | board P's author, round 4 |
| `r4t/` | the shared tools' author, rounds 4 to 7 (still being edited when this was filed) |
| `r6d/` | board D's author, round 6 |
| `rv-bat/` | review stream BAT, the battery and protection review packet |
| `rv-dec/` | review stream DEC, decision 42 (decoupling placement) |
| `rv-emc/` | review stream EMC, the per-transmitter EMCON table |
| `rv-pwr/` | review stream PWR, the power and thermal budget |
| `rv-zer/` | review stream ZER, the ZEROIZE key and slot lifecycle |
| `w2/` | foundation workstream 2 (power and runtime), 25 September |
| `w4/` | foundation workstream 4 (mechanical, thermal and RF), 25 September |
| `w6/` | foundation workstream 6 (findings review), 25 September |

## Filed files

Paths are relative to this folder; the source is the same path below `drafts/` in the worktree named. sha256 is of the file as filed.

| file | sha256 | bytes | source worktree and path | cited by |
|---|---|---:|---|---|
| `r4a/r4-decisions.md` | `2e5a0c20fc9d4f25d70d3defda2aaee056ed6b340584447fddc711898377bee2` | 101439 | `fnd/r4a` `drafts/r4-decisions.md` | `v2/docs/feasibility/EMCON.md`<br>`v2/docs/feasibility/POWER-THERMAL.md` |
| `r4a/r4-open-items.md` | `0c58f8a3574801b15b39ae06e377710e4c41646fe71d2dd81c8257733d259c91` | 27963 | `fnd/r4a` `drafts/r4-open-items.md` | `v2/docs/feasibility/POWER-THERMAL.md` |
| `r4b/box/r6-run6/README.txt` | `3977a8c3646ec82921c9bb2be1103f2c3ad55b192178ed2ac849e1d999ecbfae` | 1877 | `fnd/r4b` `drafts/box/r6-run6/README.txt` | `v2/docs/feasibility/FAILOVER-FABRIC.md` |
| `r4b/box/r6-run6/SHA256SUMS` | `eab4a7fbb05cfec2d88d4dbb52e67d85b8800698e2aeadc573580df558c08e0e` | 14282 | `fnd/r4b` `drafts/box/r6-run6/SHA256SUMS` | `v2/docs/feasibility/FAILOVER-FABRIC.md` |
| `r4b/box/r6-run6/check_pcb_b/emul-r6-gate-on-round6.txt` | `3ed0cc3868ff2b40e768a4bbfb2453bf1e28e2b4661db74e6b5ddd458861a7ab` | 19470 | `fnd/r4b` `drafts/box/r6-run6/check_pcb_b/emul-r6-gate-on-round6.txt` | `v2/docs/feasibility/FAILOVER-FABRIC.md` |
| `r4b/box/r6-run6/parity_netlist_t6_tint.json` | `4b7e4a072b4d6a964a8d60e36a64cb2566d8422f9f27d114d354305fc5fa9091` | 716 | `fnd/r4b` `drafts/box/r6-run6/parity_netlist_t6_tint.json` | `v2/docs/feasibility/FAILOVER-FABRIC.md` |
| `r4b/box/r6-run6/run.log` | `a1b51495cf05f4961997bf4537eb87e0d50ce6881125a6cfcb67ebd22702a1a2` | 17735 | `fnd/r4b` `drafts/box/r6-run6/run.log` | `v2/docs/feasibility/FAILOVER-FABRIC.md` |
| `r4b/box/r6-run6/tint/set.sha256` | `ad88fa59804dcf32afcf212a48669425070064447b0babaed845d94f6684d7de` | 1090 | `fnd/r4b` `drafts/box/r6-run6/tint/set.sha256` | `v2/docs/feasibility/FAILOVER-FABRIC.md` |
| `r4b/box/r6b_box6.sh` | `002275ffe884ab774b1f40d1a17ceec352d9f447f762c11f3565703aecf847a6` | 15476 | `fnd/r4b` `drafts/box/r6b_box6.sh` | `v2/docs/feasibility/FAILOVER-FABRIC.md` |
| `r4b/box/r6b_post6.sh` | `dcaf39a37f83f0b81f2306af04829d1c10107c53e5f0b450972e61087c5819f6` | 2084 | `fnd/r4b` `drafts/box/r6b_post6.sh` | `v2/docs/feasibility/FAILOVER-FABRIC.md` |
| `r4b/pin_parity.py` | `a36a9ffe82fbffd103795f241a5f5116bf595b413062d1edf48c20f8723a6f66` | 2157 | `fnd/r4b` `drafts/pin_parity.py` | `v2/docs/ARCHITECTURE.md`<br>`v2/docs/feasibility/FAILOVER-FABRIC.md`<br>`v2/ecad/tools/gen_sch_b.py` |
| `r4b/r4-decisions.md` | `27023b76fce3d48dd198c64a43952f4e5632730bb9087cf7b793dcaf3166e671` | 103862 | `fnd/r4b` `drafts/r4-decisions.md` | `v2/docs/feasibility/EMCON.md`<br>`v2/docs/feasibility/FAILOVER-FABRIC.md`<br>`v2/ecad/tools/gen_sch_b.py` |
| `r4b/r4-interfaces.md` | `dafa398fa1c82e471c5292acc3e0e566727ea0a355856d4a56b40bb745349922` | 11702 | `fnd/r4b` `drafts/r4-interfaces.md` | `v2/docs/feasibility/FAILOVER-FABRIC.md`<br>`v2/ecad/tools/gen_sch_b.py` |
| `r4e/footprints/gen_footprint_sgp41.py` | `18555d1d239862def79025888cee91424869a440674d4148e37de4fb59e22a67` | 5516 | `fnd/r4e` `drafts/footprints/gen_footprint_sgp41.py` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/jlc/jlc-SMCJ40CA.json` | `03d24c92aaf89b4c576244fd18fde13a7134b19261b8de9fe30c3cc24eea396f` | 64805 | `fnd/r4e` `drafts/jlc/jlc-SMCJ40CA.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/jlc/jlc-SRF1260.json` | `312a2b79bf8b6083789373d8356965b70fc6f4c36f726a1884d7bfc2c5b93919` | 50446 | `fnd/r4e` `drafts/jlc/jlc-SRF1260.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/jlc/jlc-SRF1260_1R0Y.json` | `abf447d72049bd2e716141a329383095f9189eb5873359b5c2b6ac6f0e960096` | 4046 | `fnd/r4e` `drafts/jlc/jlc-SRF1260_1R0Y.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/jlc/jlc-SRF1260_1R5Y.json` | `813915919dbdb06595e93bd61128881e008b95d365ee7da8889e95b4b1561061` | 4056 | `fnd/r4e` `drafts/jlc/jlc-SRF1260_1R5Y.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/jlc/jlc-SRF1260_2R2Y.json` | `40d3db2d4cd918a333958d6b673b99c92a9aa8516c88df7864d1dbe352f46664` | 88 | `fnd/r4e` `drafts/jlc/jlc-SRF1260_2R2Y.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/jlc/jlc-SRF1260_4R7Y.json` | `571681216f60a8429888d8633300343b614e9a9edf7041a8c9a825ac965da450` | 4057 | `fnd/r4e` `drafts/jlc/jlc-SRF1260_4R7Y.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/jlc/jlc-SRF1260_R47Y.json` | `e42554d2b11ae1eca2c3956350e8336d9a22bb49bba813b90a0884976586c793` | 4050 | `fnd/r4e` `drafts/jlc/jlc-SRF1260_R47Y.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/jlc/jlc-SRF1280.json` | `ca5dcc1a57c5195ad721a2d21056b54f7ce00038302361df7d56c6e4cf64d617` | 51488 | `fnd/r4e` `drafts/jlc/jlc-SRF1280.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/lcsc/C158012.json` | `cde2f69a427c8dba96daff2170dfbce1fa19f0ccebe35a37a5d36a45f81bffe5` | 49788 | `fnd/r4e` `drafts/lcsc/C158012.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/lcsc/C224047.json` | `ccb876725c2b9c137f5c49f3dcfc7f2a3de018d72ad1bed82cf0c7ce9cfb7351` | 5903 | `fnd/r4e` `drafts/lcsc/C224047.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/lcsc/C224052.json` | `9acc3b7108f79cf4236161071172e6188da0df239a72b55e273daa183a7e65d7` | 5941 | `fnd/r4e` `drafts/lcsc/C224052.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/lcsc/C22935.json` | `e7728cf5be7be716a55badd66dc259883b6f2da81ec92f3d6b6c4704ba676f0f` | 32715 | `fnd/r4e` `drafts/lcsc/C22935.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/lcsc/C3659325.json` | `a86e135fd9e76049a75c577cf98b0b67134bf05ac5638e61ac1583ded0e2f901` | 47 | `fnd/r4e` `drafts/lcsc/C3659325.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/lcsc/C374030.json` | `a9b666c5696b401c642388fe91382eb8712c56f01ed2ac69137210f949e2c29a` | 5675 | `fnd/r4e` `drafts/lcsc/C374030.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/lcsc/C527679.json` | `a8801ce55f07efa4260cbca20fe99e5f34ffefc24384ce298c5bf2b17d38f382` | 12519 | `fnd/r4e` `drafts/lcsc/C527679.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/lcsc/C594232.json` | `8e3fc7b9b96afa00f1962da7129a8ece1a4c0d8b989f31bce6636490013871e1` | 48514 | `fnd/r4e` `drafts/lcsc/C594232.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/lcsc/C7320434.json` | `0373b93f0dcfff998c5cdca69fcdddace6d73b2ddb55665e46f3e4547521a7b0` | 31301 | `fnd/r4e` `drafts/lcsc/C7320434.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/lcsc/C80273.json` | `e19c409d1d5cc11dfcffee7c5ca7e5657250e6789205a175b3aaa7a8ce1051f7` | 5683 | `fnd/r4e` `drafts/lcsc/C80273.json` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` |
| `r4e/r4-decisions.md` | `e05a31a54cfe5b9ec1159a110dc3bd6f0f0bbb8ed87cdd753d0e81fdd012f450` | 62162 | `fnd/r4e` `drafts/r4-decisions.md` | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py`<br>`v2/ecad/tools/gen_pcb_e.py` |
| `r4p/datasheets/SOURCES.txt` | `dc8f584ca53c085dcd3fa7634cbc8ae2f72b3b3b3cdd6496292acb318bcc812f` | 9785 | `fnd/r4p` `drafts/datasheets/SOURCES.txt` | `v2/release/review-packets/P-P4-1f614233` (`native/gen_sch_p.py`, `changes/gen_sch_p.diff`, `changes/changes.json`)<br>`v2/ecad/tools/gen_sch_p.py` |
| `r4p/datasheets/lcsc-urls.txt` | `20b48c3ee78175d919793a67181aab69693569e0c566427182c7d6eecc26732a` | 742 | `fnd/r4p` `drafts/datasheets/lcsc-urls.txt` | `v2/release/review-packets/P-P4-1f614233` (`native/gen_sch_p.py`, `changes/gen_sch_p.diff`, `changes/changes.json`)<br>`v2/ecad/tools/gen_sch_p.py` |
| `r4p/r4-decisions.md` | `bab45c321c0c367561fdffc11d56c04a5a6c07497ce3d11fb28dd7868b4e49a0` | 43964 | `fnd/r4p` `drafts/r4-decisions.md` | `v2/docs/feasibility/POWER-THERMAL.md`<br>`v2/release/review-packets/P-P4-1f614233` (`native/gen_sch_p.py`, `changes/gen_sch_p.diff`, `changes/changes.json`)<br>`v2/ecad/tools/gen_sch_p.py`<br>`v2/ecad/tools/gen_pcb_p3.py` |
| `r4p/scripts/netdiff.py` | `a3b05ba1fc0d9b13f8034169a26dbb48d3d284e00be6a96ba27b495777b421be` | 3534 | `fnd/r4p` `drafts/scripts/netdiff.py` | `v2/docs/review-packets/battery/evidence/regeneration/netdiff.py` |
| `r4p/scripts/r5p2_box.sh` | `af7d59d6a8da41beb8cfa21b0e14b17652afb395863b623797d6eb026e90bdcd` | 10587 | `fnd/r4p` `drafts/scripts/r5p2_box.sh` | `v2/docs/review-packets/battery/evidence/regeneration/bat_box.sh` |
| `r4t/r4-decisions.md` | `833218028f012e008d20db38204d574e1b511661ae92be353f4f564578b6fcda` | 216568 | `fnd/r4t` `drafts/r4-decisions.md` | `v2/docs/feasibility/EMCON.md` |
| `r6d/r6-decisions.md` | `959ee8c6b9bf4e6622a81d858775b099e5e8637d6fc19d8dc263b13accac3ca1` | 32654 | `fnd/r6d` `drafts/r6-decisions.md` | `v2/docs/feasibility/EMCON.md` |
| `rv-bat/bat-integration-notes.md` | `af4516bccc528c3e309a9237fa060357ac26961de499458f0b19a6f9f640bc5b` | 12303 | `fnd/rv-bat` `drafts/bat-integration-notes.md` | `v2/docs/review-packets/battery/MANIFEST.md` |
| `rv-bat/box/bat-cycle1/new/files/pcb-p-pack.net` | `4df605c1c9a9d2dbf17b4758cb1fe65205800668a19e30fb6f70b0daa1c4bfc4` | 91969 | `fnd/rv-bat` `drafts/box/bat-cycle1/new/files/pcb-p-pack.net` | `v2/docs/review-packets/battery/evidence/regeneration/test-pack-secondary-ts-runs.txt` |
| `rv-bat/box/bat-cycle1/new/files/pcb-p-pack.net.prov.json` | `e6fe22a3cc3df7d6d08c2a0de930d6de4a4eca1bc5e876bccf967717b3f95638` | 8498 | `fnd/rv-bat` `drafts/box/bat-cycle1/new/files/pcb-p-pack.net.prov.json` | `v2/docs/review-packets/battery/evidence/regeneration/test-pack-secondary-ts-runs.txt` |
| `rv-bat/box/bat-cycle1/run.log` | `9bffc3191029b7f528e42f8e9302f3d2b1ba00ad34a2ccfe0efafde5702d99e7` | 3548 | `fnd/rv-bat` `drafts/box/bat-cycle1/run.log` | `v2/docs/review-packets/battery/MANIFEST.md` |
| `rv-bat/box/bat/suite-worktree-cycle3.log` | `239a5d3e3d1fd06459627ce8bd081aecd534629520b50a16a9da1cca29cf7fec` | 153630 | `fnd/rv-bat` `drafts/box/bat/suite-worktree-cycle3.log` | `v2/docs/review-packets/battery/MANIFEST.md` |
| `rv-bat/box/bat/suite-worktree.log` | `b10fecd057ba0aff6bc53aad1a7e4d5cea3aee4c071177e08ddaf256aafc2629` | 153623 | `fnd/rv-bat` `drafts/box/bat/suite-worktree.log` | `v2/docs/review-packets/battery/MANIFEST.md` |
| `rv-bat/datasheets/SOURCES.txt` | `fa0399eb8bfcf2a9c9d0fb1a3bf9306836f6b6cd8194742a7fd5099d35d2e576` | 9648 | `fnd/rv-bat` `drafts/datasheets/SOURCES.txt` | `v2/docs/review-packets/battery/MANIFEST.md` |
| `rv-bat/vendor-files.txt` | `f3c546e124cc2b27f89dba24d7283e7329508a258642f3bcbceebcb4b33aac36` | 4272 | `fnd/rv-bat` `drafts/vendor-files.txt` | `v2/docs/review-packets/battery/MANIFEST.md` |
| `rv-dec/PCB-OPEN-PAIRS.decision-42.isolated.diff` | `1fc433e865bff5de41aa43fd8c0776821f58cb3e2f2698bf204b0a3ecd3b91fb` | 3703 | `fnd/rv-dec` `drafts/PCB-OPEN-PAIRS.decision-42.isolated.diff` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/datasheets/SOURCES.txt` | `05deb9062aaf96f8092e1664cc4b9c84faa3db89543caf3eac0d1a3094144af7` | 1616 | `fnd/rv-dec` `drafts/datasheets/SOURCES.txt` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec-request-diodes-pi7c9x2g404sl.md` | `3429e1ebdaec77d45c08c8ee82edf6884f4b46514723b8f8790bc1ea3472bf2c` | 1974 | `fnd/rv-dec` `drafts/dec-request-diodes-pi7c9x2g404sl.md` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_escset.out` | `1b6b5f7adda5e92d900d2100dbb5856b7d04c662fb97fbc2a0c13fa32aa1dad8` | 25200 | `fnd/rv-dec` `drafts/dec_escset.out` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_escset.py` | `14aa6aab298f8711873dbab4f3521cba2214bac886beb5c8a88503009f9412e1` | 3847 | `fnd/rv-dec` `drafts/dec_escset.py` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_escvias.out` | `18eb109b0761515e8f5fe5431ffb18c2c20c4ee3638eda014c4d35813b98330c` | 584 | `fnd/rv-dec` `drafts/dec_escvias.out` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_escvias.py` | `2a9c5f76e50565715d68490fe0310d457203d7929d534d004fdf1b0326f2652d` | 2168 | `fnd/rv-dec` `drafts/dec_escvias.py` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_fanwin.py` | `0db8b66f971b33c9220fe7112aa710ee9558492de3d9f323195a066f4d411167` | 3910 | `fnd/rv-dec` `drafts/dec_fanwin.py` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_farside.before-17h15.out` | `58bdc3b166bad755de3ee5382d23ba2e2cf8900a853fd6d14a33f1ff3bc96d45` | 9619 | `fnd/rv-dec` `drafts/dec_farside.before-17h15.out` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_farside.out` | `3173557d0cf6f590f365227d1a631edbaae9bd84cfc213517e8bd23b2cec45dd` | 9825 | `fnd/rv-dec` `drafts/dec_farside.out` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_farside.py` | `22d3ab7f5e12776341084e4e346b336ff7cb856755f1405bd3ad1dc8d545a14c` | 5114 | `fnd/rv-dec` `drafts/dec_farside.py` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_finesets.before-17h15.out` | `1f671a942967e4abd0aca55c71e3b413a08c58391a82ca5215f5c2d9a34c2a2c` | 291 | `fnd/rv-dec` `drafts/dec_finesets.before-17h15.out` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_finesets.out` | `3a4db397e9047965ae24e799ad3b45588ac74a5738b7eb30818b840bc04c5093` | 292 | `fnd/rv-dec` `drafts/dec_finesets.out` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_finesets.py` | `96069898ef19c835ef14a60c7b2b4bc4bae9c665f6ff45daffdc4a3b4b281ff4` | 1377 | `fnd/rv-dec` `drafts/dec_finesets.py` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geom_pcb-a-power-a23.json` | `e9dbb38eaab141f271bea175966539cd5659d13f1672e14cdfe09f8fb3e78f9b` | 18862 | `fnd/rv-dec` `drafts/dec_geom_pcb-a-power-a23.json` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geom_pcb-a-power-a23.txt` | `bdda040348795966c26060405f614438d2c1d8f1423d8da07fa70792fbbf8c53` | 7111 | `fnd/rv-dec` `drafts/dec_geom_pcb-a-power-a23.txt` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geom_pcb-b-compute-b19.json` | `126e7667ff3dfe26e087c888d97e732645c4593f278aa06f64109a9cdb040c5e` | 17583 | `fnd/rv-dec` `drafts/dec_geom_pcb-b-compute-b19.json` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geom_pcb-b-compute-b19.txt` | `0e54ea8e684e857bd04d1a5ac82cd85c1cc2a5ed3a49b740007c7757030c4028` | 6711 | `fnd/rv-dec` `drafts/dec_geom_pcb-b-compute-b19.txt` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geom_pcb-c-display-c8.json` | `90e52bf8c6e969afa8ff20dba649936fcd1936e6cba7176b850c423a967b885f` | 10553 | `fnd/rv-dec` `drafts/dec_geom_pcb-c-display-c8.json` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geom_pcb-c-display-c8.txt` | `37699f7ad0c6703fada5a57395f3362578ab36db33a9174ee70ace5ad9950e50` | 4065 | `fnd/rv-dec` `drafts/dec_geom_pcb-c-display-c8.txt` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geom_pcb-d-aprs-d9.json` | `fb39a416968ae18a38a59faab04831f32c7dc05e8a05f9d319976038a5964897` | 13856 | `fnd/rv-dec` `drafts/dec_geom_pcb-d-aprs-d9.json` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geom_pcb-d-aprs-d9.txt` | `c2b93acd520861403bbb7a0fbd6f134889d8f55df0d931e15f5d0e43ef3d3c6a` | 5444 | `fnd/rv-dec` `drafts/dec_geom_pcb-d-aprs-d9.txt` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geom_pcb-e1-dock-e7.json` | `d94ee632c3204fc251d4514323d76e3ba108fe2580afe5b74f414a4c772e871f` | 10729 | `fnd/rv-dec` `drafts/dec_geom_pcb-e1-dock-e7.json` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geom_pcb-e1-dock-e7.txt` | `f04d47c2f6181b0e8dd9334d4b6118fcf21c9a5788f79bd14921b6dc9a6b909f` | 4133 | `fnd/rv-dec` `drafts/dec_geom_pcb-e1-dock-e7.txt` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geom_pcb-p-pack-p2.json` | `b6263d87a0aab0006fbca673192343e65c8f8516ca3cf5b1a93cd04dd3cf9a50` | 1848 | `fnd/rv-dec` `drafts/dec_geom_pcb-p-pack-p2.json` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geom_pcb-p-pack-p2.txt` | `d2754f45088e73c16f967810bac1904324ae221b57f3986e940e4af6627d1505` | 708 | `fnd/rv-dec` `drafts/dec_geom_pcb-p-pack-p2.txt` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geom_table.md` | `a485552f8f4162e57141596afaecfa52a9f9a95121c2f916d73f6f7cf2f14314` | 4281 | `fnd/rv-dec` `drafts/dec_geom_table.md` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_geometry.py` | `fc926ba59d982b6f109c99b5a72d6a8ea130ca1d6cdb8dd1c54d28e40671ee30` | 11642 | `fnd/rv-dec` `drafts/dec_geometry.py` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_loop.out` | `85dc41584ef9aaab3e5d1db5c3d5e26830cd60432709d01c8f78cb3a2b9c5f67` | 5158 | `fnd/rv-dec` `drafts/dec_loop.out` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_loop.py` | `eed91e6beb8b1fdb8de067667c434f799f20117c61c48ac08ef9633bf202c051` | 6319 | `fnd/rv-dec` `drafts/dec_loop.py` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_mmscan.err` | `e1f317bb966d63ee6869e9c744c6208a1807842953ff49082165d073b25f07ab` | 27 | `fnd/rv-dec` `drafts/dec_mmscan.err` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_mmscan.out` | `0ce71790d660874aee17670ae03be9f86f36e8c90733fd9bfd560863981b01a0` | 1628 | `fnd/rv-dec` `drafts/dec_mmscan.out` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_mmscan.py` | `4cba5432e38b426fac5bb4de458fb59079232a3a894d24ee4be1a0bae5d209bf` | 1601 | `fnd/rv-dec` `drafts/dec_mmscan.py` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_newfans.out` | `2c6e0e762020c71bdb62d872c1c93b1abda7515adac0d5b4b68910dfb294c4c3` | 1467 | `fnd/rv-dec` `drafts/dec_newfans.out` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_newfans.py` | `b7b8cf6284e7f17307322b74a5978f82434ce7e7accdacdb78b19edfe7621cde` | 2077 | `fnd/rv-dec` `drafts/dec_newfans.py` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_planes.out` | `11f7337a77ac81e091dde17e8121bf07196cfa8b5707620b1e036045bb6d10ca` | 4806 | `fnd/rv-dec` `drafts/dec_planes.out` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_planes.py` | `a6d0256b4ad8c8d2dece39f3dce98fd5354ea87db61b2dc40e815bcba1224479` | 1561 | `fnd/rv-dec` `drafts/dec_planes.py` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_sides.out` | `9fd3a9dc45c09e1a52cbcceb71f3bdd28bdd4fcbdd2321e2f6c5c509ccf33d60` | 40378 | `fnd/rv-dec` `drafts/dec_sides.out` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_sides.py` | `3730e4328f4d10411cdde4b3796cc3c3a470a568e6da519e6864e6c56c3fb15b` | 1991 | `fnd/rv-dec` `drafts/dec_sides.py` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_sides_decl.out` | `ab69cedf2f86fe58e10e17d0a5bdcd1a198f27030b8e2e5eacb00056a609da83` | 16961 | `fnd/rv-dec` `drafts/dec_sides_decl.out` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-dec/dec_sides_decl.py` | `a788a9365159eb57531b7d8126eda712b528eb1a6c46cedc750badf63ea47076` | 1583 | `fnd/rv-dec` `drafts/dec_sides_decl.py` | `v2/docs/feasibility/DECOUPLING.md` |
| `rv-emc/datasheets/SHA256SUMS` | `c911282e3cccf6b594cac97e03449d169fa0259680fb91b00f13a335fcb52961` | 1793 | `fnd/rv-emc` `drafts/datasheets/SHA256SUMS` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/datasheets/SOURCES.txt` | `e31f8043723f3e74c1662aaaee2286e4e80c10268c075c7c1bc530708869466e` | 4619 | `fnd/rv-emc` `drafts/datasheets/SOURCES.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/netlists/A-r6cand-pcb-a-power.net` | `e7c50a4f212a510a7df37693bd600af64539b2f3077ef7cb8e96bb150beb96c5` | 592776 | `fnd/rv-emc` `drafts/netlists/A-r6cand-pcb-a-power.net` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/netlists/A-r6cand-pcb-a-power.net.prov.json` | `aadf6aea8234396188573205233cc052d0638a5301ac34bf7dd8651b226efc84` | 8499 | `fnd/rv-emc` `drafts/netlists/A-r6cand-pcb-a-power.net.prov.json` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/netlists/B-r6cand-pcb-b-compute.net.prov.json` | `4c1d9b2665324943f35830cb6161e0694c8178c98abcfba25e406d4472e2cd55` | 8501 | `fnd/rv-emc` `drafts/netlists/B-r6cand-pcb-b-compute.net.prov.json` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/netlists/D-r6cand-pcb-d-aprs.net` | `9aae5bf93a104abcbf14568657b79d11704cb243971415fd0bc0ac6911263a94` | 247232 | `fnd/rv-emc` `drafts/netlists/D-r6cand-pcb-d-aprs.net` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/netlists/D-r6cand-pcb-d-aprs.net.prov.json` | `71f4a2068f25c87a890070c617e67a724b59e800aabd77bab4e7dcde081e457f` | 8498 | `fnd/rv-emc` `drafts/netlists/D-r6cand-pcb-d-aprs.net.prov.json` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/netlists/SHA256SUMS` | `40d7131f3e0e932b9747c5f7c12fec93577acec1c9c16e603865697a1312fc3c` | 798 | `fnd/rv-emc` `drafts/netlists/SHA256SUMS` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/A-nets.txt` | `0ca1600212a5bd2158048189dcacd05d2fb50385eefd3f084ef1670f9cbeeb5b` | 4132 | `fnd/rv-emc` `drafts/readings/A-nets.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/B-e22-e72.txt` | `4fdb45beef9332f93fe02634e4278d0cf6c3694f1526af491b47f6bfca9350c3` | 5864 | `fnd/rv-emc` `drafts/readings/B-e22-e72.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/B-m2c2-sdemc1.txt` | `72fdc8b2a92561cdaf70869cf9ce42791b4caa408150c09e695f95a591a744d0` | 11583 | `fnd/rv-emc` `drafts/readings/B-m2c2-sdemc1.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/B-nets-1.txt` | `8fe20f994c243e92c64af02e923a92fb326b9bcb63da6a32077056155f7d38d7` | 7718 | `fnd/rv-emc` `drafts/readings/B-nets-1.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/B-nets-cm5.txt` | `1858194cca83a4ad4c8c80ff81b36b8486949a200475e9e32e361c95bb200f00` | 3892 | `fnd/rv-emc` `drafts/readings/B-nets-cm5.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/B-nets-m2-io.txt` | `33e7527b2e34026b660e11269e6e7bb8e90be8711ad646390d90ad9f42bc6da3` | 9480 | `fnd/rv-emc` `drafts/readings/B-nets-m2-io.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/B-nets-m2.txt` | `1f46803581ebe2abfd160c77ed2c3a7e66f01eb4f4ed52309883cd78c154870a` | 4154 | `fnd/rv-emc` `drafts/readings/B-nets-m2.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/B-rb-lime.txt` | `b8b6f5a78c9d437bb747a5400de409411447e876dbb9f06d518a4f3f51f58e20` | 2062 | `fnd/rv-emc` `drafts/readings/B-rb-lime.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/B-refs-gates.txt` | `610dc419377e7d95f6b524fd4fbe4dc77c99cea15c137ae39eaefdee3bcbbb5d` | 2430 | `fnd/rv-emc` `drafts/readings/B-refs-gates.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/B-refs-m2.txt` | `6d646b7465fa33b8f5b88042074cb2e9db6150e297ccd6202fde3909b4ee7f19` | 1676 | `fnd/rv-emc` `drafts/readings/B-refs-m2.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/B-refs-pulls.txt` | `6bbcec8721bb8d82fd3a1cb4f020797725b8bec96de78c775bb3d8504dce5bfb` | 1602 | `fnd/rv-emc` `drafts/readings/B-refs-pulls.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/B-refs-sockets.txt` | `60a04732a7204aae72dd50c0790037e704d81a20f910edee4600167d3d27343e` | 2312 | `fnd/rv-emc` `drafts/readings/B-refs-sockets.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/C-lamp-nets.txt` | `dd860919f792dbce068ef86bf2dca524588b6ff2401c423c82198f5dc1c5e549` | 1766 | `fnd/rv-emc` `drafts/readings/C-lamp-nets.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/C-nets.txt` | `a1fc241f310dd40a98323f3f42e0cf6df51ed98ace7838f0ea3cd4748900741a` | 1634 | `fnd/rv-emc` `drafts/readings/C-nets.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/D-nets.txt` | `3bc4ebd855e014e8a665d3d9e5b5fe3595a68aeb360e4a53314bb7cfe3e990b7` | 4712 | `fnd/rv-emc` `drafts/readings/D-nets.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/D-refs.txt` | `da92ccc287b733e2098ce16afc4bf9650715e29daa02259169fa2c1ef5192b92` | 2351 | `fnd/rv-emc` `drafts/readings/D-refs.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/candidates-vs-main-458b2873.txt` | `6848d919a39d7602a73edcbc0b2c75a2cae095127ba1ca9e0b01f2d00151f5bf` | 2024 | `fnd/rv-emc` `drafts/readings/candidates-vs-main-458b2873.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/candidates-vs-r6int-1629.txt` | `fd7b8ee080a431bb24e033fe655bc3e62cd9e7c3832834e97928cf4e8b4d8588` | 1758 | `fnd/rv-emc` `drafts/readings/candidates-vs-r6int-1629.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/claims_check_on_EMCON.judged.txt` | `10d08aea859fc2c6a88ebeb9070e27ef5fde2fcc0078496a3bd6aeaef8105181` | 505 | `fnd/rv-emc` `drafts/readings/claims_check_on_EMCON.judged.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/claims_check_on_EMCON.verdict.json` | `3e4fe0049c342ed2e059d27a677726ab3cb5e5cf05c8b4895462779cc7f91397` | 794 | `fnd/rv-emc` `drafts/readings/claims_check_on_EMCON.verdict.json` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/main-01469100-drift.txt` | `7d0875902eb8e72440cf83c871b9fcfaad93b77b2b55cb62190f64ac497aa18a` | 1974 | `fnd/rv-emc` `drafts/readings/main-01469100-drift.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/main-b69f20db-drift.txt` | `53f19df4b06db4448cde975ade6ccb559be528a4face306bb793fbfbd743e7fa` | 1574 | `fnd/rv-emc` `drafts/readings/main-b69f20db-drift.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/main-ccf5808e-drift.txt` | `dc5c72304e5a891a2b1db6b85187266a87922fdf0b7a29d01a31da5c6a2b169b` | 3106 | `fnd/rv-emc` `drafts/readings/main-ccf5808e-drift.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/tx-inhibit-conductor.txt` | `b950ee353e29ff62969480921b749b4c51aa01e49893b936e68468af1134fcf6` | 8800 | `fnd/rv-emc` `drafts/readings/tx-inhibit-conductor.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/tx_inhibit_r4t-0795c5de_on_main_by_r6d.txt` | `b323525d4e7abece07673643341d633e1363c092705f2fdaebf6fdb4af53bbd7` | 11044 | `fnd/rv-emc` `drafts/readings/tx_inhibit_r4t-0795c5de_on_main_by_r6d.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/tx_inhibit_r4t-5aece264_on_candidate_set.txt` | `3b95f0fab9795f03cc99193dad8966463bbbf796c4a5ce0aad5e12599ebea743` | 9546 | `fnd/rv-emc` `drafts/readings/tx_inhibit_r4t-5aece264_on_candidate_set.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/tx_inhibit_r4t-853f3082_on_candidate_set.txt` | `6aeff06e3a721bf7c474242d9cd9289e8f874cd365986c921e1c2b787ff53897` | 8616 | `fnd/rv-emc` `drafts/readings/tx_inhibit_r4t-853f3082_on_candidate_set.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/readings/tx_inhibit_r4t-e88aa46b_on_candidate_set.txt` | `29b02fdedcf588ea1fb512b3010e848787b37f0bb0598944432fc31f82d73292` | 9588 | `fnd/rv-emc` `drafts/readings/tx_inhibit_r4t-e88aa46b_on_candidate_set.txt` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/tools/netcompare.py` | `ec843a6b9e7074478359819ef42bb488344025eb122dfffb83191b0412e859d3` | 940 | `fnd/rv-emc` `drafts/tools/netcompare.py` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/tools/netdump.py` | `eedd50ce04d88dbe354621fb48561785e50f4e9257d9b67015584427be2cb42b` | 938 | `fnd/rv-emc` `drafts/tools/netdump.py` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/tools/netline.py` | `9097f2d8b9d6857e4dc54f22b02cb77a280409ebc818f617f583eab0e9c7d306` | 479 | `fnd/rv-emc` `drafts/tools/netline.py` | `v2/docs/feasibility/EMCON.md` |
| `rv-emc/tools/refdump.py` | `98c1b6016a00d79ed76ce5bff49aff14fa439d690bddf67db1fd3dbd584d3184` | 901 | `fnd/rv-emc` `drafts/tools/refdump.py` | `v2/docs/feasibility/EMCON.md` |
| `rv-pwr/datasheets/README.md` | `3d119538584511a80717c65082d5488926d570e62f976856a18bbbdbed3770a5` | 4131 | `fnd/rv-pwr` `drafts/datasheets/README.md` | `v2/docs/feasibility/POWER-THERMAL.md` |
| `rv-pwr/pwr-chain-redeclaration.yaml` | `039c72aa6f451dbdb9b68d6ae6946fb3ca02b70cd76f8390569fc39f178f5f45` | 11663 | `fnd/rv-pwr` `drafts/pwr-chain-redeclaration.yaml` | `v2/docs/feasibility/POWER-THERMAL.md` |
| `rv-pwr/pwr-maker-questions.md` | `6d2e5d29b957c80ffe8b973a3cc705a034694f1ef1bb947c8e6574d02850c293` | 2301 | `fnd/rv-pwr` `drafts/pwr-maker-questions.md` | `v2/docs/feasibility/POWER-THERMAL.md` |
| `rv-pwr/pwr-part-temps-rows.yaml` | `cee34b52c6b452593d0f3a7f5ab6b2e4feb4cd1615b9af7e540dd8e90d2cec5e` | 5229 | `fnd/rv-pwr` `drafts/pwr-part-temps-rows.yaml` | `v2/docs/feasibility/POWER-THERMAL.md` |
| `rv-pwr/pwr_budget.json` | `5a616902d2ddab82f25d34ab55d848d06011fb6fbe48c147221d6b442783e462` | 76863 | `fnd/rv-pwr` `drafts/pwr_budget.json` | `v2/docs/feasibility/POWER-THERMAL.md` |
| `rv-pwr/pwr_budget.out` | `58e40cf604804cc9d70c7fbeb1012be4552563fcc8ae7ef6755003c33acb902f` | 47499 | `fnd/rv-pwr` `drafts/pwr_budget.out` | `v2/docs/feasibility/POWER-THERMAL.md` |
| `rv-pwr/pwr_budget.py` | `469d0820b046ef6ff5aceadf422b4166de3d6a02bc50fa5b0c3644704f0f9556` | 67785 | `fnd/rv-pwr` `drafts/pwr_budget.py` | `v2/docs/feasibility/POWER-THERMAL.md` |
| `rv-zer/ZEROIZE-integration.md` | `ea8afca20dcac2f8f0585200ef0383d2b860826141af0cd669c467196e27f5e3` | 14289 | `fnd/rv-zer` `drafts/ZEROIZE-integration.md` | `v2/docs/feasibility/ZEROIZE.md` |
| `rv-zer/datasheets/SOURCES.md` | `e37862cd151f74af7dea3fa29cf920717279a836cd12985e7ab72c5f4118a1ee` | 7306 | `fnd/rv-zer` `drafts/datasheets/SOURCES.md` | `v2/docs/feasibility/ZEROIZE.md` |
| `rv-zer/prices/jlc-ATECC608B-SSHDA-T.json` | `1b75f8c933d888608a11927a2df2335326ff852da6cf0cb35ae1a90c7891848e` | 11976 | `fnd/rv-zer` `drafts/prices/jlc-ATECC608B-SSHDA-T.json` | `v2/docs/feasibility/ZEROIZE.md` |
| `rv-zer/zeroize/zer_budget.py` | `8cdad0569ec3d8140d291da79361ccc9b519592e91decb1bc1547f21624bca9e` | 20269 | `fnd/rv-zer` `drafts/zeroize/zer_budget.py` | `v2/docs/feasibility/ZEROIZE.md` |
| `rv-zer/zeroize/zer_config.py` | `3d4271b2b9aec3e069ebc8d005f802abb07c7e90b186afc50ef5281725f4b795` | 11519 | `fnd/rv-zer` `drafts/zeroize/zer_config.py` | `v2/docs/feasibility/ZEROIZE.md` |
| `w2/w2-power.md` | `960e46bdd58bf857aeb436dc9239ee11b30060fad978ba557f560e1be50a53ec` | 27952 | `fnd/w2` `drafts/w2-power.md` | `v2/docs/feasibility/POWER-THERMAL.md` |
| `w2/w2-runtime.md` | `2b203982023f6fe63a1eecc1103cc3ceb1b6e51f4a858fbe0e79ce365626c9db` | 16780 | `fnd/w2` `drafts/w2-runtime.md` | `v2/docs/feasibility/POWER-THERMAL.md` |
| `w4/w4-mech-thermal-rf.md` | `ba590c405b672995eee2094ec302eb08ddfed9ca49a7411d71041ffd459bd42e` | 52637 | `fnd/w4` `drafts/w4-mech-thermal-rf.md` | `v2/docs/feasibility/POWER-THERMAL.md` |
| `w4/w4-scratch-thermal.py` | `6c83da5f7e3e4f0f5393bfe0f609ba02c423adbadfa3661a245d0a9b778e65c3` | 9871 | `fnd/w4` `drafts/w4-scratch-thermal.py` | `v2/docs/feasibility/POWER-THERMAL.md` |
| `w6/w6-findings.md` | `4cde4801efe8aeb2c0a1942240553d2da8bd623a012486dee0730a41ffb04bf8` | 40483 | `fnd/w6` `drafts/w6-findings.md` | `v2/docs/feasibility/DECOUPLING.md` |

### Rewritten on filing

| file | sha256 in the worktree | sha256 filed | what changed |
|---|---|---|---|
| `rv-dec/PCB-OPEN-PAIRS.decision-42.isolated.diff` | `6786bdb3010b9ecfa4f791cd76e38dac27a64b09dd9884f35cec28c0d9b45927` | `1fc433e865bff5de41aa43fd8c0776821f58cb3e2f2698bf204b0a3ecd3b91fb` | the scratch directory's absolute path replaced by `$SP` |
| `r4b/box/r6-run6/check_pcb_b/emul-r6-gate-on-round6.txt` | `b45b628010c5210eeb20a440e05f483802201e144ce7d2548313aa1851ff9aa7` | `3ed0cc3868ff2b40e768a4bbfb2453bf1e28e2b4661db74e6b5ddd458861a7ab` | the scratch directory's absolute path replaced by `$SP` |

## Cited but not filed: netlists and a box run directory

A KiCad netlist is regenerated by its generator; each one below is also rebuilt, byte for byte, from a file the repository holds, and the output's sha256 was checked when this was filed. The header lines 3 and 4 of a netlist name the box directory it was written in and the time; they are the only lines that differ.

| cited file | sha256 | bytes | cited by | how it is rebuilt |
|---|---|---:|---|---|
| `fnd/r4b` `drafts/box/r6-run6/tint/regen/pcb-b-compute.net` (the same bytes as `fnd/rv-emc` `drafts/netlists/B-r6cand-pcb-b-compute.net`) | `af8a9186f981210c48104eaf5742fb4cd4f80d12aa0f13bc5d887e75c922a380` | 1449732 | `v2/docs/feasibility/EMCON.md`<br>`v2/docs/feasibility/FAILOVER-FABRIC.md`<br>`v2/docs/evidence/WRONG-MODEL-RECONCILIATION.md`<br>`v2/docs/feasibility/fab/out/pulldowns.txt` | command N1; over 1 MB. Written by `gen_sch_b.py` sha256 `6e3d8809...`, main's generator since `458b2873`, whose committed netlist differs from it in lines 3 and 4 alone |
| `fnd/rv-emc` `drafts/netlists/B-r6cand-pcb-b-compute.net` | `af8a9186f981210c48104eaf5742fb4cd4f80d12aa0f13bc5d887e75c922a380` | 1449732 | `v2/docs/feasibility/EMCON.md` | command N1; its sidecar is filed as `rv-emc/netlists/B-r6cand-pcb-b-compute.net.prov.json` |
| `fnd/r6d` `drafts/box/run/new/pcb-d-aprs.net` | `88aee4e209809f9e88ae6253e17617c7285de6b2bb3366b2268cb7b582d3d37d` | 247232 | `v2/docs/feasibility/EMCON.md` | command N2; it differs from the filed `rv-emc/netlists/D-r6cand-pcb-d-aprs.net` in its date line alone (`EMCON.md` section 1.1) |
| `fnd/r4a` `drafts/box/fixup4-run3/x6main/pcb-a-power.net` | `f0258b5ba24d21f0f3e3ca43ed8d482414232c6a11ecc7a19a72239ceb51b1a4` | 616015 | `v2/docs/feasibility/EMCON.md` | command N3; generator `gen_sch_a.py` `a0452054...`, main's since `458b2873` |
| `fnd/r4a` `drafts/box/fixup3-run2/repo/pcb-a-power.net` | `daf132b22fad985422f5b4b799da0defa029faff2d1374f667b8927e3fc512b1` | 592771 | `v2/docs/feasibility/FAILOVER-FABRIC.md`<br>`v2/docs/evidence/WRONG-MODEL-RECONCILIATION.md` | command N4; it differs from the filed candidate `rv-emc/netlists/A-r6cand-pcb-a-power.net` in lines 3 and 4 alone |
| `fnd/r4b` `drafts/box/r6-run6/` (the run directory, 157 files) | its list: `r4b/box/r6-run6/SHA256SUMS` (filed) | 44471087 | `v2/docs/feasibility/FAILOVER-FABRIC.md` | the directory is over 1 MB (schematics, netlists, ERC reports). Its README, run log, list, the netlist parity record, the integration set's hashes and the gate emulation the page cites are filed under `r4b/box/r6-run6/`. It was written by `r4b/box/r6b_box6.sh` (filed) on the rented box from main `faf8c981` with `gen_sch_b.py` `6e3d8809...` and `check_pcb_b.py` `28904a37...`, both main's since `458b2873`; `r4b/box/r6b_post6.sh` (filed) is the runner-side reading. The box copy was deleted after the fetch (its README) |

The commands, run from the repository root; each output's sha256 equals the table's (checked on filing):

```sh
# N1: board B round-6 candidate (af8a9186...)
git show 458b2873:v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net \
  | sed -e '3s|.*|    (source "/root/r6/b/tint/v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_sch")|' \
        -e '4s|.*|    (date "2026-09-26T11:15:35+0000")|' > r6cand-pcb-b-compute.net

# N2: board D round-6 regeneration of 12:53 UTC (88aee4e2...)
git show 458b2873:v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net \
  | sed -e '3s|.*|    (source "/root/r6/d/new/v2/ecad/pcb-d-aprs-d9/pcb-d-aprs.kicad_sch")|' \
        -e '4s|.*|    (date "2026-09-26T12:53:06+0000")|' > run-new-pcb-d-aprs.net

# N3: board A fourth fix-up (f0258b5b...)
git show 458b2873:v2/ecad/pcb-a-power-a23/out/pcb-a-power.net \
  | sed -e '3s|.*|    (source "/root/r6/a/run7/x6run/faf8c981/v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_sch")|' \
        -e '4s|.*|    (date "2026-09-26T13:33:31+0000")|' > fixup4-pcb-a-power.net

# N4: board A round-6 candidate as written in the box's repo tree (daf132b2...)
sed -e '3s|.*|    (source "/root/r6/a/run2/repo/v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_sch")|' \
    -e '4s|.*|    (date "2026-09-26T12:03:37+0000")|' \
    v2/docs/records/rv-emc/netlists/A-r6cand-pcb-a-power.net > repo-pcb-a-power.net
```

## Cited but not filed: already in the repository

| cited file | sha256 | cited by | the same bytes in this repository |
|---|---|---|---|
| `fnd/rv-emc` `drafts/netlists/main-pcb-a-power.net` | `aa1372ba3932610f27c3fd5aac5a5e1663600c1cae4a5f92712b9710f114d4f4` | `v2/docs/feasibility/EMCON.md` | `git show 0d1e2ef6:v2/ecad/pcb-a-power-a23/out/pcb-a-power.net` |
| `fnd/rv-emc` `drafts/netlists/main-pcb-a-power.net.prov.json` | `267b65dd2d1908d20310bafe44d247b3e69ac7b0bdf0f20518ef7d165ead2dcf` | `v2/docs/feasibility/EMCON.md` | `git show 0d1e2ef6:v2/ecad/pcb-a-power-a23/out/pcb-a-power.net.prov.json` |
| `fnd/rv-emc` `drafts/netlists/main-pcb-b-compute.net` | `0e72edb5d755316f6a55ce915c1c23103ecc11054904f813ec2942aca7e975c9` | `v2/docs/feasibility/EMCON.md` | `git show 8ce0b892:v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net` |
| `fnd/rv-emc` `drafts/netlists/main-pcb-b-compute.net.prov.json` | `6af876891fa79b4edb75cc38fcf4d8171e4fb19c79c742ffa48c00d4ca79e29f` | `v2/docs/feasibility/EMCON.md` | `git show 8ce0b892:v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net.prov.json` |
| `fnd/rv-emc` `drafts/netlists/main-pcb-c-display.net` | `2834f0d8c4071d56c28c8b081357bd91f7d79b6e8fefeef7cd2aa33d38e1913b` | `v2/docs/feasibility/EMCON.md` | `git show faf8c981:v2/ecad/pcb-c-display-c8/out/pcb-c-display.net` (unchanged at `45bde541`: `v2/ecad/pcb-c-display-c8/out/pcb-c-display.net`) |
| `fnd/rv-emc` `drafts/netlists/main-pcb-c-display.net.prov.json` | `184a37704ba1282596b0ce533c88cd927848a4dfcbd463c5c5f98ff646c7c693` | `v2/docs/feasibility/EMCON.md` | `git show faf8c981:v2/ecad/pcb-c-display-c8/out/pcb-c-display.net.prov.json` |
| `fnd/rv-emc` `drafts/netlists/main-pcb-d-aprs.net` | `e2534f5e34c1f5bff6141d201c326f001e1a4d3af42423db49ab64777e8b690f` | `v2/docs/feasibility/EMCON.md` | `git show faf8c981:v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net` |
| `fnd/rv-emc` `drafts/netlists/main-pcb-d-aprs.net.prov.json` | `7e21f4b5fad79d708cc9e82d296aa8d579a60ef3382f0b0aa8a124f614f0c05f` | `v2/docs/feasibility/EMCON.md` | `git show faf8c981:v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net.prov.json` |
| `fnd/rv-emc` `drafts/netlists/main-pcb-e1-dock.net` | `d910e49c5f5f50b271a56113b15af7178dbeac583510ea0412dca87d3a37385d` | `v2/docs/feasibility/EMCON.md` | `git show faf8c981:v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net` (unchanged at `45bde541`: `v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net`) |
| `fnd/rv-emc` `drafts/netlists/main-pcb-e1-dock.net.prov.json` | `7c67af4ec83e09c7060ecb2825f181582c1ab88ed7bcfd26fe95cfe55e26b8a7` | `v2/docs/feasibility/EMCON.md` | `git show faf8c981:v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net.prov.json` |
| `fnd/rv-emc` `drafts/netlists/main-pcb-p-pack.net` | `3c925191447136ac5ec22f251bf608b76744849d953bffa0488734e21b358103` | `v2/docs/feasibility/EMCON.md` | `git show faf8c981:v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net` |
| `fnd/rv-emc` `drafts/netlists/main-pcb-p-pack.net.prov.json` | `8680ff98d5f54d28502c9993325ed6fb9addd58fbb8aa98c2305947583e2da2d` | `v2/docs/feasibility/EMCON.md` | `git show faf8c981:v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net.prov.json` |
| `fnd/r4a` `drafts/box/fixup3-run2/x6main/pcb-a-power.net` | `e7c50a4f212a510a7df37693bd600af64539b2f3077ef7cb8e96bb150beb96c5` | `v2/docs/feasibility/EMCON.md` | `v2/docs/records/rv-emc/netlists/A-r6cand-pcb-a-power.net` (filed from `fnd/rv-emc`) |
| `fnd/r6d` `drafts/box/rf002/new/pcb-d-aprs.net` | `9aae5bf93a104abcbf14568657b79d11704cb243971415fd0bc0ac6911263a94` | `v2/docs/evidence/WRONG-MODEL-RECONCILIATION.md` | `v2/docs/records/rv-emc/netlists/D-r6cand-pcb-d-aprs.net` (filed from `fnd/rv-emc`) |
| `fnd/rv-fab` `drafts/fab/` (scripts and `out/`) | per file in `v2/docs/feasibility/fab/out/SHA256SUMS-scripts.txt` | `v2/docs/feasibility/FAILOVER-FABRIC.md` | filed by the integration of 26 September 2026 in `v2/docs/feasibility/fab/`, byte for byte except `out/fabmap.json`, whose two scratch paths were elided on filing; its `drafts/fab/txt/` extractions derive from PDFs held in `v2/vendor/` and were not filed |

## Cited but not filed: maker documents, for `v2/vendor/`

Datasheets, manuals, maker web pages and the text extractions and crops made from them belong in `v2/vendor/`, which the parts stream owns. The fetch record of each stream (URL, date, sha256) is filed: `rv-dec/datasheets/SOURCES.txt`, `rv-emc/datasheets/SOURCES.txt` and `SHA256SUMS`, `rv-pwr/datasheets/README.md`, `rv-zer/datasheets/SOURCES.md`, `rv-bat/datasheets/SOURCES.txt`, `r4p/datasheets/SOURCES.txt` and `lcsc-urls.txt`.

| cited file | sha256 | bytes | cited by | in `v2/vendor/` |
|---|---|---:|---|---|
| `fnd/r4b` `drafts/datasheets/cj-2N7002_C8545.pdf` | `7941fb423af7c6c6c8979063a7e8819bb19217ece275efcce18948950a41d9f6` | 1575038 | `v2/docs/feasibility/EMCON.md` | `v2/vendor/power/jscj-2n7002-c8545.pdf` (the same bytes) |
| `fnd/r4e` `drafts/datasheets/littelfuse-59140-reed-sensor-2022-03-25.pdf` | `c54b8c66982b3ebd90d52a74f005a06815c80ba9b0561f67f13d6dede3e0d27b` | 427176 | `v2/release/review-packets/E-E17-1f614233` (`native/gen_sch_e.py`, `changes/gen_sch_e.diff`)<br>`v2/ecad/tools/gen_sch_e.py` | not yet |
| `fnd/r4p` `drafts/datasheets/eaton-scf9550-elx1135.pdf` | `3ecc2424acfa1753c2aec0b62d5706d4f25b7a08e731795c0d84d59938a3158e` | 738112 | `v2/docs/feasibility/POWER-THERMAL.md` | `v2/vendor/battery/eaton-scf9550-elx1135.pdf` (the same bytes) |
| `fnd/r4p` `drafts/datasheets/lcsc-C8545.pdf` | `7941fb423af7c6c6c8979063a7e8819bb19217ece275efcce18948950a41d9f6` | 1575038 | `v2/release/review-packets/P-P4-1f614233` (`native/gen_sch_p.py`, `changes/gen_sch_p.diff`, `changes/changes.json`)<br>`v2/ecad/tools/gen_sch_p.py` | `v2/vendor/power/jscj-2n7002-c8545.pdf` (the same bytes) |
| `fnd/r4p` `drafts/datasheets/nexperia-pesd5v0s1ba.pdf` | `6546e415b8885ea3790c91629034c6b4e5c6961d5fde734e55dfa479dd8dc49a` | 223015 | `v2/release/review-packets/P-P4-1f614233` (`native/gen_sch_p.py`, `changes/gen_sch_p.diff`, `changes/changes.json`)<br>`v2/ecad/tools/gen_sch_p.py` | `v2/vendor/nexperia/nexperia-pesd5v0s1ba.pdf` (the same bytes) |
| `fnd/rv-bat` `drafts/datasheets/ti-sluuaq3-bq4050-trm.pdf` | `525d16b2bdee44e5b587ccf6800b9967bc524772d0b5a20937957ea2e738b7ad` | 3381192 | `v2/docs/review-packets/battery/evidence/trm_defaults_check.py`<br>`v2/docs/review-packets/battery/evidence/trm_defaults_check.out` | `v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf` (the same bytes) |
| `fnd/rv-dec` `drafts/datasheets/intel-an574.pdf` | `9c6cb94e3dcc9fdc1d2dd49dd56a1a7d1b47c35b29b4abaaef850a49c48b37d0` | 949869 | `v2/docs/feasibility/DECOUPLING.md` | not yet |
| `fnd/rv-dec` `drafts/datasheets/ti-bq77207.pdf` | `45c1c99e2d303be8bcf1a2b1eea8275f657c7c80170bda7c2778042a688295cb` | 1167707 | `v2/docs/feasibility/DECOUPLING.md` | `v2/vendor/battery/ti-bq77207.pdf` (the same bytes) |
| `fnd/rv-emc` `drafts/datasheets/kernel/head.json` | `17a1bb915f136f4ed0dcf41aceb6aa7f31ed2813f0b42b6095337e5207322c2b` | 33560 | `v2/docs/feasibility/EMCON.md` | not yet; Linux source (GPL-2.0) or its GitHub commit record, at the commit `EMCON.md` section 1.2 names |
| `fnd/rv-emc` `drafts/datasheets/kernel/mt7915_mcu.c` | `e3cc6c75c355e7e2ede45f946113dc1371b7652f3fb3a740581503b434ebeb2d` | 108231 | `v2/docs/feasibility/EMCON.md` | not yet; Linux source (GPL-2.0) or its GitHub commit record, at the commit `EMCON.md` section 1.2 names |
| `fnd/rv-emc` `drafts/datasheets/kernel/mt7915_mt7915.h` | `b11e1fc5910e4a7035fa180cd996d4bf10d751481aa0a197b64188e7901700a5` | 19134 | `v2/docs/feasibility/EMCON.md` | not yet; Linux source (GPL-2.0) or its GitHub commit record, at the commit `EMCON.md` section 1.2 names |
| `fnd/rv-emc` `drafts/datasheets/myriadrf-limesdr-mini-2-0-page-20260925.html` | `f1146105a3c09ebcf786d217fbf0053f8e6df3c5192efcf666e731281be4c4f1` | 59824 | `v2/docs/feasibility/EMCON.md` | not yet |
| `fnd/rv-emc` `drafts/datasheets/qmx-crops/rev1a-p2-J201.png` | `f0081d5dea26ae5ba429f34832d09a4bf1b67d0e161b348c3fc43ccd0a019970` | 107032 | `v2/docs/feasibility/EMCON.md` | not yet; a crop of a QRP Labs schematic listed above |
| `fnd/rv-emc` `drafts/datasheets/qmx-crops/rev3-left-rev2-right-p2-J201.png` | `a41e8f6377b0c4f615b0a47241ac0a3858fd477173b352844603a40da02a117d` | 295430 | `v2/docs/feasibility/EMCON.md` | not yet; a crop of a QRP Labs schematic listed above |
| `fnd/rv-emc` `drafts/datasheets/qmx-crops/rev5-p1-power-supplies.png` | `c1868c030058c00f5fe3cef181471e8fa7afaaa9785434a5f192d76c45ba31fc` | 486194 | `v2/docs/feasibility/EMCON.md` | not yet; a crop of a QRP Labs schematic listed above |
| `fnd/rv-emc` `drafts/datasheets/qmx-crops/rev5-p2-J201.png` | `8f357b2b0efdacda704d402517f62bf6b35fe9cb65f4f0a14809674203dbe9b5` | 143136 | `v2/docs/feasibility/EMCON.md` | not yet; a crop of a QRP Labs schematic listed above |
| `fnd/rv-emc` `drafts/datasheets/qrplabs-qmx-rev1-searchable-schematic-1b.pdf` | `dd7c32c85ffc2586856d653a0c785b94d7b6bc08f8a36fa26f5bc092d035be25` | 943212 | `v2/docs/feasibility/EMCON.md` | not yet |
| `fnd/rv-emc` `drafts/datasheets/qrplabs-qmx-rev1-searchable-schematic-1b.txt` | `f835b57fd9561c0ad834e28af6fa32b525fac5708351560927178f135f4a097b` | 73653 | `v2/docs/feasibility/EMCON.md` | not yet; a text extraction of the PDF beside it |
| `fnd/rv-emc` `drafts/datasheets/qrplabs-qmx-schematics-rev1-a.pdf` | `11be4f699e85f0399893e969fe8b9c1e81258b0914ade40df6a1a721a8a661e6` | 3431101 | `v2/docs/feasibility/EMCON.md` | not yet |
| `fnd/rv-emc` `drafts/datasheets/qrplabs-qmx-schematics-rev1-a.txt` | `c5e5d39229ce869dcd994fa0943325bf1b97be3c00e1dff8f81fb908450c20f1` | 314 | `v2/docs/feasibility/EMCON.md` | not yet; a text extraction of the PDF beside it |
| `fnd/rv-emc` `drafts/datasheets/qrplabs-qmx-schematics-rev2.pdf` | `36a1941918e59e59772e3c758647d066a7166d9dee3c9f7a08a4b6a62dac79cc` | 3434389 | `v2/docs/feasibility/EMCON.md` | not yet |
| `fnd/rv-emc` `drafts/datasheets/qrplabs-qmx-schematics-rev3.pdf` | `6a1072939603ea9b8c9eae9e4a9268a5a76227129ba5d1127582ceb054a93a8a` | 3422207 | `v2/docs/feasibility/EMCON.md` | not yet |
| `fnd/rv-emc` `drafts/datasheets/qrplabs-qmx-schematics-rev5.pdf` | `83e911e666e6cfba3e7705d353376577f147f55601188cf8ed4a717ec232e488` | 3355330 | `v2/docs/feasibility/EMCON.md` | not yet |
| `fnd/rv-emc` `drafts/datasheets/quectel-ec2x-eg2x-eg9x-em05-qcfg-at-commands-manual-v1.1-sixfab.pdf` | `0280b1af1cfa627e232014c7d12c6544115014cb24143b91bd63ae290e03be8e` | 968989 | `v2/docs/feasibility/EMCON.md` | not yet |
| `fnd/rv-emc` `drafts/datasheets/quectel-ec2x-eg2x-eg9x-em05-qcfg-at-commands-manual-v1.1-sixfab.txt` | `7e498cbd121eee92d9013dac32c35d562b62882c5e9787381d6241ddc9661ceb` | 252312 | `v2/docs/feasibility/EMCON.md` | not yet; a text extraction of the PDF beside it |
| `fnd/rv-emc` `drafts/datasheets/quectel-rg50xq-rm5xxq-at-commands-manual-v1.1.1-quectelforums.pdf` | `ef90013314f828b82e1e6f7b024590b2f77a3dc617ff7dd2fd0f15a01410abf7` | 1747091 | `v2/docs/feasibility/EMCON.md` | not yet |
| `fnd/rv-emc` `drafts/datasheets/quectel-rg50xq-rm5xxq-at-commands-manual-v1.1.1-quectelforums.txt` | `c5a24d85cb405fdefcae262bc0e1a60c84b0c623ba209026c679f7aed1be297a` | 517530 | `v2/docs/feasibility/EMCON.md` | not yet; a text extraction of the PDF beside it |
| `fnd/rv-emc` `drafts/datasheets/quectel-rm520n-at-commands-manual-v1.0.0-prelim-20220812-waveshare.pdf` | `0e940dbc5957dbda2cafd30c1306e5b2b8f6534610f5b08d1c271d9538f017dd` | 2145643 | `v2/docs/feasibility/EMCON.md` | not yet |
| `fnd/rv-emc` `drafts/datasheets/quectel-rm520n-at-commands-manual-v1.0.0-prelim-20220812-waveshare.txt` | `7c7ca0c4acc7a4910922aa57ce439e40a033464e0d45abefeca9cebc60f55d61` | 599070 | `v2/docs/feasibility/EMCON.md` | not yet; a text extraction of the PDF beside it |
| `fnd/rv-emc` `drafts/datasheets/quectel-rm5x0n-at-commands-manual-v1.0-digikey.pdf` | `6ed74e7e61da55211002cacc7075bc0a6051e81eeb7bb12848926fbc69f96c8c` | 1757874 | `v2/docs/feasibility/EMCON.md` | not yet |
| `fnd/rv-emc` `drafts/datasheets/quectel-rm5x0n-at-commands-manual-v1.0-digikey.txt` | `62def9b85b485ed7e62ec48296403047f692f367acb2349351bf364d0f2940f2` | 553596 | `v2/docs/feasibility/EMCON.md` | not yet; a text extraction of the PDF beside it |
| `fnd/rv-pwr` `drafts/datasheets/advantech-sqflash-720-d-m2-2242-v1.9.pdf` | `4176a46e8474f74102cf139b4fd61dea45f2f46c7062d1ddb786732c2107b7ba` | 707692 | `v2/docs/feasibility/POWER-THERMAL.md` | not yet |
| `fnd/rv-pwr` `drafts/datasheets/asiarf-AW7915-AED_V1.pdf` | `af1a93ef3b484a3da4354779f0b2a8a2537c94d71025eb68b82a4d4879f8e8db` | 322159 | `v2/docs/feasibility/POWER-THERMAL.md` | not yet |
| `fnd/rv-pwr` `drafts/datasheets/asiarf-aw7915-aed-product-page.html` | `b153fe713673d0f6df7936038333096e8fc14842609d90e8d8b1e7694c120846` | 427240 | `v2/docs/feasibility/POWER-THERMAL.md` | not yet |
| `fnd/rv-pwr` `drafts/datasheets/cervoz-m2-2242-nvme-titan.pdf` | `30b3c59cd3332952f91eb825cd6bb9ebcbea3281fca4bd6a3277ddd03ce032b9` | 1159075 | `v2/docs/feasibility/POWER-THERMAL.md` | not yet |
| `fnd/rv-pwr` `drafts/datasheets/keystone-m65-p42-mini-fuse-holders.pdf` | `caa141ea51ac68cf80ab6e14ad2075fcfc76206451f4bfe45330005c0deaf395` | 263884 | `v2/docs/feasibility/POWER-THERMAL.md` | `v2/vendor/keystone/M65p42.pdf` (the same bytes) |
| `fnd/rv-pwr` `drafts/datasheets/limesdr-mini-v2-introduction.html` | `f1146105a3c09ebcf786d217fbf0053f8e6df3c5192efcf666e731281be4c4f1` | 59824 | `v2/docs/feasibility/POWER-THERMAL.md` | not yet |
| `fnd/rv-pwr` `drafts/datasheets/limesdr-mini-v2-user-setup.html` | `87b2e5605196b5c5f48e9175991c63143152dbb694d6f4faeba85d6cdaeca3b3` | 59456 | `v2/docs/feasibility/POWER-THERMAL.md` | not yet |
| `fnd/rv-pwr` `drafts/datasheets/sunon-dc-fan-catalogue-240A-pp18-40-extract.pdf` | `fae7e21365939be5c3bbf156be3522b364037a637590f5079538d63456bca63b` | 273117 | `v2/docs/feasibility/POWER-THERMAL.md` | not yet |
| `fnd/rv-pwr` `drafts/datasheets/ti-bq4050-trm-sluuaq3a.pdf` | `525d16b2bdee44e5b587ccf6800b9967bc524772d0b5a20937957ea2e738b7ad` | 3381192 | `v2/docs/feasibility/POWER-THERMAL.md` | `v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf` (the same bytes) |
| `fnd/rv-pwr` `drafts/datasheets/xenarc-709gnk-product-page.html` | `dc32f6556d6ddc398064e3a15eec0c600937b2235138cbd10e0ed344d708bf93` | 66845 | `v2/docs/feasibility/POWER-THERMAL.md` | not yet |
| `fnd/rv-zer` `drafts/datasheets/infineon-slb9673-fw26-datasheet-rev1.4.pdf` | `0750aaaba4f59ef5208c97af10b89bc616dd69a075ebda0225b57109b9d24001` | 516054 | `v2/docs/feasibility/ZEROIZE.md` | not yet |
| `fnd/rv-zer` `drafts/datasheets/microchip-atecc508a-complete-20005927A.pdf` | `3e79484ff38cde1980159af097487ea336774016d4e64965b0ba666bb8d66bc0` | 841710 | `v2/docs/feasibility/ZEROIZE.md` | not yet |
| `fnd/rv-zer` `drafts/datasheets/microchip-atecc608a-40001977A.pdf` | `3e971d6d284ebc64fc81d168788b9abd32da81a90ce1e0bb56037b0ca16a4a26` | 335784 | `v2/docs/feasibility/ZEROIZE.md` | not yet |
| `fnd/rv-zer` `drafts/datasheets/microchip-atecc608b-tflxtls-DS40002249.pdf` | `b4601f1c2dc395af532d556010ace8b19ca792368d4cda8bfc960a6d3018646d` | 1489345 | `v2/docs/feasibility/ZEROIZE.md` | not yet |
| `fnd/rv-zer` `drafts/datasheets/microchip-atecc608b-tngtls-DS40002250.pdf` | `db25050e016b887c578795e79c0ece0532dc176c5ef3ef4fb2f46b3eae0127b5` | 1201389 | `v2/docs/feasibility/ZEROIZE.md` | not yet |
| `fnd/rv-zer` `drafts/datasheets/microchip-dm320118-users-guide-DS50002921A.pdf` | `6951ca754fad1f9e78c9f63a5f788fe183e21ca01b5358f10ee4cfa6001df3b1` | 768268 | `v2/docs/feasibility/ZEROIZE.md` | not yet |
| `fnd/rv-zer` `drafts/datasheets/nxp-an12413-se050-apdu.pdf` | `e98a72e4215ba2886d777509f066ff620925ae65999d9c28cbcf24b7f2cf5622` | 1625193 | `v2/docs/feasibility/ZEROIZE.md` | not yet |
| `fnd/rv-zer` `drafts/datasheets/nxp-se050-datasheet.pdf` | `b47c8a5d40191f31b78e48f6c60c6ba17c3eac56bf97976212ade786ee3ee83c` | 377642 | `v2/docs/feasibility/ZEROIZE.md` | not yet |
| `fnd/rv-zer` `drafts/datasheets/tcg-tpm2-r1p59-part1-architecture.pdf` | `18e393ef8f61d4c5deebb578cc4220b025fdaff2c28a7e3264f16e37796c3d9b` | 3790735 | `v2/docs/feasibility/ZEROIZE.md` | not yet |
| `fnd/rv-zer` `drafts/datasheets/tcg-tpm2-r1p59-part3-commands.pdf` | `d2e5e7187574d383b00ff966c33b30a96e3f5165cbfae20a4d094e5794f3b9bb` | 3839615 | `v2/docs/feasibility/ZEROIZE.md` | not yet |

## Withheld

- `fnd/rv-bat` `drafts/datasheets/reviewers/` (7 files): third-party web page snapshots; the packet itself decided not to publish them (MANIFEST.md, last section). Cited by `v2/docs/review-packets/battery/MANIFEST.md`; each page's URL and sha256 are listed there.

## Cited but not found

- **`fnd/r4t` `drafts/r4-decisions.md` at sha256 `e5efdc619832e46a...`** (15:43 CEST) and its earlier edition `1e3fe2800c3b33db...` (14:55), both named by `v2/docs/feasibility/EMCON.md` section 1.1. The log is rewritten in place, not appended to, and no copy with either hash is left in the session's scratch directory. The file filed as `r4t/r4-decisions.md` (sha256 above, worktree file modified 20:50 CEST) is a later edition of the same log; the IDs `EMCON.md` quotes from it (R4T-D29, D30, D32, D36, D37, D38, D39, D40, D41, F5, F8, F9, F12, F14) are all in it, and it carries a later round's amendments that the page did not read. Replace it with r4t's final log when that stream merges.

Other `drafts/` citations outside the pages this round edits (for the integrator): the committed generators `v2/ecad/tools/gen_sch_a.py`, `gen_sch_b.py`, `gen_sch_e.py`, `gen_sch_p.py`, `gen_pcb_e.py`, `gen_pcb_p3.py`, `gen_footprints_e.py`, `kisch.py` and `tests/test_pack_secondary_ts.py` name records in the round-4 and round-6 authors' `drafts/` folders. The decision logs among them are filed here (`r4a`, `r4b`, `r4e`, `r4p`); the scripts, JLC records and images they also name (for example `fnd/r4a` `drafts/scripts/loop_design.py`, `fnd/r4p` `drafts/scripts/ts_network.py`) are not, because those files are owned by the tools and board streams, whose comments would have to be re-pointed in the same change.
