# Q-B-ESC-1 results, 26 September 2026 (EXPERIMENTAL)

**EXPERIMENTAL.** These are the filed outputs of board B's bounded escape trial Q-B-ESC-1 (`v2/docs/B-FEASIBILITY.md`
section 7; its reading is section 7.8, the next test section 7.9) and the read-only analysis of them. Nothing here is a
phase, a promotion, a layout candidate or a gate verdict, and nothing here authorises layout (the owner's condition 7 of
25 September 2026). The trial routed slot 3's net group S3 of the **pre-correction B21 board** (931 components) alone;
the corrected netlist on `main` (1,103 components) is on no placed board and was not routed. Prototype design: no V2
board has been built, and board B has never been routed to completion.

## Provenance

| Item | Value |
|---|---|
| Box | vast.ai instance 52646493 (64 vCPU), KiCad 9.0.9, OpenJDK 25.0.4.1, `freerouting-1.9.0-mesh.jar` sha256/16 `82753043cb9da3ae` |
| Commit on the box | `44cfa0450c74e26e7e8d48261d9f7209404ccd98` (tools tree `ee1906fab4cbaad78133316d1f06176288e1d8d0`); the trial scripts' sha256/16 are in `JOURNAL.md` |
| Trial run | 2026-09-26 18:48:19 to 21:21:46 UTC (9,207 s), both arms at once from 18:50:31 UTC |
| Input board | `pcb-b-compute-b19/routed/pcb-b-compute-preroute.kicad_pcb` sha256 `62facf0952ff4c01cb0a47698ec6870b5fae0f0d9b836bf95db6c3c7bae166dd` (A6 as is); A8 written by `make_arm8.py`, sha256 `c858ef17f05d59f57e1777ea1edf775a69fa2e54fa61524b0985d943841bbd45` |
| Fetch | `besc1-results.tgz` sha256 `814dc16dfa62571c9ce6cadf6fed7a83ff5cf1a964c3539a153c6624f8196a92` plus `besc1-run.log`; every file of the tarball was compared by sha256 with the box copy and with the copy filed here (all equal) |
| Judge | `outcome.json`: **INCONCLUSIVE**, by the pre-registered table of section 7.5: A6 was cut by its job cap while its count was still falling |
| Operator act | both routers sat on Freerouting's modal "DSN file reader" warning from 18:50:37 to 19:47:04 UTC; Return was sent to each display by hand (the operator line in `JOURNAL.md`); the watchdog fix is commit `d2cde4ff` |

## What is not filed here, and where it is

Kept on the box under `/root/besc1/v2/ecad/out/routeflow/b-esc1/` until the box is destroyed (the operator's act), and
named by sha256 so that a copy can be recognised; `analysis/box-files.sha256` lists all 40 of them in full (taken on
the box at 21:48:57 UTC):

| File | sha256 | Why not filed |
|---|---|---|
| `a6/s3.kicad_pcb` (the six-layer arm's final board) | `682d567e24b43582cb0a3eeab29c68b327bff1c89be430aa2c86c5f3712f638d` | a board file (9.9 MB) |
| `a8/s3.kicad_pcb` (the eight-layer arm's final board) | `b6d1d7af26611c9fdfea373cad0aadd162f057cde3b6132f8fc51e9afd9fa516` | a board file (9.7 MB) |
| `a6/s3-drc.json` | `dda1eab778572d82d949eb5721355979eec0b81501b58d45a73aa426ef233891` | 607 kB, almost all of it the board-wide unconnected list at KiCad's 499 cap; its counts are in `aN/hardset.log` |
| `a8/s3-drc.json` | `fba99de963a94a7755e9c8bec9cadd035562f1c4f19550297632f00391a5af9a` | the same |
| `aN/part.dsn`, `aN/run/S3/job.dsn` | a6 `e9aa73d4...`, `e64f2f22...`; a8 `413505eb...`, `95d41448...` | 1 MB inputs, rebuilt by the driver |
| `aN/run/S3/route.ses` | a6 `bf8e2516...` (= `watch/pass-012.ses`), a8 `45ec191c...` (= `watch/pass-014.ses`) | the router's last sessions |
| `aN/watch/pass-NNN.ses` (26 sessions) | in `analysis/box-files.sha256` | the per-pass sessions the watcher copied |

The two fetched `s3-drc.json` files are also inside the tarball named above, which stays with the session record. A
copy of each final board (`a6/s3.kicad_pcb`, `a8/s3.kicad_pcb`) is kept with the session record outside git, named by
the sha256 above, so the `pcbnew` readings of `analysis/` can be re-run after the box is destroyed.

## Files

- `JOURNAL.md`, `outcome.json`, `integrity.json`, `arm8.json`, `besc1-run.log`: the driver's own journal, verdict,
  arm-integrity record, the eight-layer arm's census and the driver's console log.
- `a6/`, `a8/` per arm, as the driver wrote them: `base.json` (pass-0 count), `final.json` (count on the final board),
  `s3-counts.txt` (hard and unrouted, `H U`), `place_audit.txt`, `route.log`, `watch.log`, `watch/passes.csv`,
  `watch/watch.json`, `watch/pass-NNN.log` (the per-pass count output), `run/S3/fr.log` (Freerouting's log), and the
  driver's intermediate logs `import.log`, `hardset.log`, `drc.log`, `dsn.log`, `part.log` with the partition `part.json`.
- `analysis/`, all read-only: `besc1_residue.py`, `besc1_passes.py`, `besc1_viasite.py`, `besc1_rows.py` and
  `besc1_copper.py` read the boards with `pcbnew` on the box, from `/root/besc1-analysis/` (the first readings) and
  `/root/besc1-fix/` (the second versions of 27 September 2026), both deleted afterwards. The second readings changed no
  file in the trial directory: afterwards no file there had a newer modification time, the 40 files of
  `analysis/box-files.sha256` and the 60 filed here still matched their sha256, and only the two arm folders' own times
  had moved (KiCad's transient lock files). `besc1_timesplit.py` and `besc1_causes.py` are plain Python over the files
  filed here and ran on the runner.
  - `besc1_timesplit.py` writes `time-split.csv` and `pass-times.csv` from the files filed here only.
  - `besc1_residue.py` read each arm's final board with `pcbnew`: every split S3 net's copper clusters, the missing
    connections between them, and the facts at each end (`residue-a6.json`, `residue-a8.json`). Its totals equal the
    driver's: 33 open over 23 nets and 18 over 16.
  - `besc1_passes.py` (second version) re-imported every per-pass session into a fresh load of the arm's input board,
    as `count_open.py --ses` does, recorded every pad-bearing copper cluster of every split S3 net, and gives each
    missing connection of the final board its history: open after a pass when no pad of the final board's cluster at
    one end shares a cluster with any pad of the final board's cluster at the other (`passes-a6.json`,
    `passes-a8.json`). Its per-pass totals equal `watch/passes.csv` on every pass.
  - `besc1_viasite.py` (second version) searched for via sites near each end pad on the input and the final board
    with KiCad's own shapes and collision test (`viasite-a6.json`, `viasite-a8.json`; the method and its limits, both
    ways, are in the file).
  - `besc1_rows.py` read which pads each side of U301 and U302 carries on the input board, with each pad's net and
    escape (`rows.json`); its `function` field is empty, because the board's pads carry no pin function, so the pin
    names the page gives come from B21's netlist (`82dd1e4d`, sha256 `0e72edb5...`).
  - `besc1_copper.py` measured group S3's copper on each final board per layer, per DSN class and per pair or
    single-ended member, and lists the members of `DIFF100_S3` and `USB_S3` (`copper.json`).
  - `besc1_causes.py` joined the three readings with B21's netlist (`82dd1e4d`, sha256 `0e72edb5...`) and the corrected
    one (`fc144600`, sha256 `669d02d0...`) into one row per missing connection with its cause (`residue-a6.csv`,
    `residue-a8.csv`; the rules are in the script's header).
- **Corrected on 27 September 2026, after the independent check.** The first `besc1_passes.py` counted a pad as open
  only outside its net's largest cluster, so a tie between equal clusters hid a pad (A6's `PCIE_PWR_EN3` read 1 of 12
  open where it was open after 6); the first `besc1_viasite.py` modelled every pad as its bounding rectangle and
  skipped any track whose two ends lay more than 8 mm from the pad. Both were replaced by the second versions above,
  and `besc1_causes.py` was re-run on their outputs: the history column changed on seven rows and three causes moved,
  each on a via site of one to five grid points (B-FEASIBILITY.md section 7.8). The first versions' outputs are not
  kept here; the per-pass totals, the residue and `residue-aN.json` are unchanged.

## sha256 of every file in this folder

This README is the only file not listed (it cannot name its own hash).

| File | Bytes | sha256 |
|---|---:|---|
| `JOURNAL.md` | 3516 | `3a27bb74c8cb4b0563c60059323ada418328128884473ac82d75ebad9b877c2b` |
| `a6/base.json` | 10471 | `7a56020c8d1b00c8c62c97150084e5aaae4c6b2623f0ea4ba46a5793805063d8` |
| `a6/drc.log` | 51 | `9f1f5169a821815a5af5782c944780629edc8cd547850d37fc5d901be113e0c3` |
| `a6/dsn.log` | 1208 | `73c32b038f7d81254dbc16d8149b56b5b4408f52e3fa0ad7d5146302691422de` |
| `a6/final.json` | 2353 | `19eda8f328ee2f374dfbaa28e66a2bcb0664c7df3858055bd757eb662f28d7aa` |
| `a6/hardset.log` | 738 | `e9119e3183dfb54b477bc0e7e625626d2e9422764051107ebd0837a271d15292` |
| `a6/import.log` | 3110 | `1110be803d57af4a98f5b6aca5352bbd14589f8b6b558ec0182a80cec3ce3796` |
| `a6/part.json` | 15557 | `0d54fe1b87d1496825f867a8375c5ee869551652288f629ce9647d4e7b7e0a92` |
| `a6/part.log` | 747 | `5ffcfbf82456d70661bcd4c3be9293995bfa9ba551ca80fa2a7d2f4e0d13f581` |
| `a6/place_audit.txt` | 5827 | `e63bcb33aff2e90e1ac3e8e35f88e142118b96a71f727964d2c9aae84fc4417d` |
| `a6/route.log` | 253 | `8ba12a2881933004a5ccc1e73fa331a7595a90feb7bbcf81f960af3ab9109bdf` |
| `a6/run/S3/fr.log` | 16560 | `325042eb8e7a0fff6a6ee68ddf11db9cd9e0bfd48f3207d8d86c5e4169b31a04` |
| `a6/s3-counts.txt` | 6 | `bc6db581da7ab69ce7af72b6053f3ab66ca991910c42e3ff359d19575e22a963` |
| `a6/watch.log` | 109 | `0a0288365d7c2130136b3de42227568e3103261a1bb1ed3bcbeb793923f71a61` |
| `a6/watch/pass-001.log` | 261 | `152f25ce03b7f8da9c0025b9c82f2edb64a5487b50ff65fc966b33b2dbb4966e` |
| `a6/watch/pass-002.log` | 264 | `79e04e7b6412c63c9ba6a280d4ea1352139dd3d8fc860ed7df113b6e2b355b16` |
| `a6/watch/pass-003.log` | 262 | `ed9eb1c35bd6bc30e395edda07f99ef15105e6f68c79639a82170a4865f58618` |
| `a6/watch/pass-004.log` | 261 | `892f5f7073a72d916a648b8f09e9c9dd51ed7dd1ad76595663942c3f74faa9b2` |
| `a6/watch/pass-005.log` | 260 | `4233283bfb65c49882aadf62f247d4ba73cf5d9851065dfb2e0c6e6541a31e35` |
| `a6/watch/pass-006.log` | 260 | `f18124bd16514ee3ba13d2b8ef4e4c196d95249b746cca0db2920b01ca0fdfa7` |
| `a6/watch/pass-007.log` | 261 | `69d1903ed9b650473f5878bb4b6836c43e953bc160573a53bca94728aab3957f` |
| `a6/watch/pass-008.log` | 260 | `276162a02e4ae30a9b8fd32aa5ef211850baab91fc72ca8f80489ca2b3ae4eac` |
| `a6/watch/pass-009.log` | 260 | `1171c724395c9491b5cc7600c03369edfcc1ec7bf09ae10224b2f5340beff0b0` |
| `a6/watch/pass-010.log` | 260 | `e0b617d7f13783df784b4dba0abfba5a8230af980c0406cf14c9f391ce43ca55` |
| `a6/watch/pass-011.log` | 249 | `abf92b2fdb4548216cb56672ee46ad5c5e981daaf9024d272445a7236fdc022a` |
| `a6/watch/pass-012.log` | 260 | `15bb4c15ce60ef780813eccddc6c84f4601c16e4a2267b0eb712c3ada747da7e` |
| `a6/watch/passes.csv` | 297 | `c2bedf0114d40c2898b0a588d412e533828d7e8d3a2e32971b0c7fff60050339` |
| `a6/watch/watch.json` | 1609 | `2fdb4be3ee258e3454f4af04b87395630676148fe5c9cd58a97cd53826373539` |
| `a8/base.json` | 10471 | `44546f3c53a9a1f94ba41d7c130317988d70c097c0500e51fe4baa01ef436103` |
| `a8/drc.log` | 52 | `d8c27fd317bebc6231d53b11f5ec2c001fc1fc73ba9ece9f28fcc5f42e199773` |
| `a8/dsn.log` | 1208 | `a11fe863dd462cee199a1b70febb68b7597de5f7f53f159c39c9070352cbcf10` |
| `a8/final.json` | 2025 | `58f9dd938d7e86e172a16aa6deb853cfcf4d2f5e12b660585af9c05aa6c0e5eb` |
| `a8/hardset.log` | 738 | `2a177dfd8ca80908d4c3806ef30dcffbc6f9041c2bcb79ce1d556959dad81432` |
| `a8/import.log` | 3110 | `139381f214d9128ebec592fe7c8b70191fabfb6a20c29874e0bb4fc506848a34` |
| `a8/part.json` | 15557 | `0d54fe1b87d1496825f867a8375c5ee869551652288f629ce9647d4e7b7e0a92` |
| `a8/part.log` | 747 | `117b891f02b193e5c10e7c07b38c3a1505e15026978166d12164eb52f7239e72` |
| `a8/place_audit.txt` | 5827 | `e63bcb33aff2e90e1ac3e8e35f88e142118b96a71f727964d2c9aae84fc4417d` |
| `a8/route.log` | 211 | `6a77c7425011504c2b22dc239b8551880eeac23c54e7e22ba79562f185325344` |
| `a8/run/S3/fr.log` | 16686 | `3973c0cd89f8e4bd587982bbb9a8d82e15532750e5f37c7eeeff0edd23e327b0` |
| `a8/s3-counts.txt` | 6 | `bc6db581da7ab69ce7af72b6053f3ab66ca991910c42e3ff359d19575e22a963` |
| `a8/watch.log` | 114 | `65e8fa3416222f383ec87e03b604dfb98993d00a8267b38211ebed4994d51478` |
| `a8/watch/pass-001.log` | 261 | `ea33e1097bf8fc4dda899548cef3a87a0d6ce18903533fcc79ae0e14eeed194d` |
| `a8/watch/pass-002.log` | 260 | `38ccd4a24fee13defa1d2acecac8d8596d95ab6a59618d2b78e089fdb2e8b4ac` |
| `a8/watch/pass-003.log` | 249 | `37abcee739b45b109b76d3a4f93611631af4963602464b67bc3bc72fb8368035` |
| `a8/watch/pass-004.log` | 249 | `ab1a6abf09cf1cd5626af2e50260146093a245ecbc63d209d5d25f586ad68a2a` |
| `a8/watch/pass-005.log` | 249 | `464625231e389f78deaf604c6462ae5cb90d507c478f426dd8c7bf5ffbea8b66` |
| `a8/watch/pass-006.log` | 249 | `210cacc55f3e9235e21b8c42d50a29dad58785605e38c6bc906afa7dea6efe40` |
| `a8/watch/pass-007.log` | 238 | `f6d7a074770e7fa6c8608e19ac38a3d3f3a4a1de3f1e7f0303bcd46db14f5ce6` |
| `a8/watch/pass-008.log` | 249 | `e5c96539daff22370f019bdd346fb3069214144d63158d958ae9289730025ae2` |
| `a8/watch/pass-009.log` | 249 | `96ac4c8ac97b07662a1cc75b1c0de18b59bccdec17bd01cb84ed4258cb7398aa` |
| `a8/watch/pass-010.log` | 238 | `ee5d4be41dd51c8f265c425733cb1955f9ca30c1e02c98bc7f4f9e358de165e1` |
| `a8/watch/pass-011.log` | 238 | `7b2b6405e40d67aee6e617e428c405fca1b72668819b7e5acc7d65929ab07c73` |
| `a8/watch/pass-012.log` | 260 | `54e0bcb83058eae4dd6b8f3b5f664d0ff24a635cd9a40bd69b18af36334e959e` |
| `a8/watch/pass-013.log` | 238 | `b7d5f956cf908503c7380749bf2472f91708c83101a423ce3746e5879dac9fca` |
| `a8/watch/pass-014.log` | 238 | `9f29e284d84821331e13e27ec024d5c4d0eec829017777330efa0943cd7309e4` |
| `a8/watch/passes.csv` | 340 | `0c6fec1302c3d7d02a6b081dcaf1dc55435d023577de88f7856b3655954bfb4c` |
| `a8/watch/watch.json` | 1888 | `a79531d4714414f41fae7d1b481dfe6ed2b96572da5e979d82ad1f8e06445de2` |
| `analysis/besc1_causes.py` | 10371 | `bcf520d6ca8554f80f0006c2ff6736bd9f9eb387f736ff97d4fc553e68d1ffc5` |
| `analysis/besc1_copper.py` | 2913 | `e86d70e8fab65850abc7acc0e024b9788b4f37a3e83edc2fc73585b6d9888344` |
| `analysis/besc1_passes.py` | 7877 | `8860b233470f142703266d49677db1003de0fbf17de732330ab857ac80311bc1` |
| `analysis/besc1_residue.py` | 9794 | `4b87b546309e7a5117e18b7dae92f88bb3bf95db5d330be98891ee3f68e0658c` |
| `analysis/besc1_rows.py` | 3668 | `096e5ee165e53126fcda5cb23413ffe827ad782014b64688e801ea5f6112f4f4` |
| `analysis/besc1_timesplit.py` | 3592 | `a52f77ec562918f72bb2a8cb9315de98e8acccd32a7393a0c0bcce3a4e96701c` |
| `analysis/besc1_viasite.py` | 9285 | `cffdde24a552398f637e4d287c81b47732634358032c370cc27b88f0bc8c7be6` |
| `analysis/box-files.sha256` | 3574 | `114656d0fc9b2712b786f9c78ab01b6ac1adf11240e7f4ec7bf71033875065da` |
| `analysis/copper.json` | 8406 | `096cf7bc325e8d6dcc6c6b6d31047874654db74f94e478d299d363ba9cdcdbdb` |
| `analysis/pass-times.csv` | 535 | `d4f3521d6f5b26ea1ecb582cf324866acbd4af194d245aa82b93bca4a1d6ac4c` |
| `analysis/passes-a6.json` | 106611 | `c5c367b9a6281edf1203517d2f6c1eaab0a3f14415ac7a9638a8a5871e5d5975` |
| `analysis/passes-a8.json` | 85753 | `12a4f8cd9f08fc4e43caaa1861e6069451f030ea9978564d9adbdf06c157e66c` |
| `analysis/residue-a6.csv` | 9166 | `9ab43adb713c94424b7477f5f63f4f2eb2fea741cddc79658d37018bdbbc5147` |
| `analysis/residue-a6.json` | 113058 | `d5ce5cef2e5a4cab5d4e74d6134edd906600f3785d9775a2c3264e6212a2fe58` |
| `analysis/residue-a8.csv` | 4935 | `310a5cba8ee1785336bd4c9a6fccd3a67a3385f93b222b8dac59714909a438ed` |
| `analysis/residue-a8.json` | 71798 | `d85b25ab440f97093e2d75b8f7c2c5005d3db72514d74ca6689d6c00b71ebee5` |
| `analysis/rows.json` | 51920 | `8a9742e9991d269f45c7a4c765d7fb8bbbf1b2ebef781bd02d0a334084a31794` |
| `analysis/time-split.csv` | 404 | `1ffd6db6b41596a93d229dfb6761a09e11df0de15a1af496e8ad4d703d023b7c` |
| `analysis/viasite-a6.json` | 72834 | `78b3d744dc454476a0b9c74e2c1ceff2092739eeca957e78f474440fcbccc46c` |
| `analysis/viasite-a8.json` | 38142 | `e2eba9b65154eab252ba0df9e1e76ee7d791eabf540f6d656aed8e2434afbd58` |
| `arm8.json` | 2928 | `03fd353ea652aee53fcbc49c337d7a8772286195a5123b0afac3bf68010d2225` |
| `besc1-run.log` | 2313 | `af3b5ddca5a6edf4d076a8002dd582ddec9ae27ccb723aa40665b2dbd15048fd` |
| `integrity.json` | 301 | `3a0a2a39896b64f4ca1eed24fde10ee099a1a8cfcaebd45b10663108ab52f32e` |
| `outcome.json` | 1301 | `9f07a20512320a57523193975457966bd6944948b2b3b933d2187fe2c66ed2e7` |

