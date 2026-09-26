# Manifest of the battery and protection review packet

Written by the stream's manifest script from the files themselves (review stream BAT, MESHSAT-1357, 26 September 2026,
third cycle). Prototype design: nothing listed here has been built or measured. **Release check:**
`python3 v2/docs/review-packets/battery/evidence/check_manifest.py` must print `RELEASE CHECK PASS` at the commit that
is sent (`REVIEW-REQUEST.md` section 5).

## Revision

| Item | Value |
|---|---|
| Base commit | main `1f614233` (the packet's own commit adds this folder, the generator change, the fixture and two vendor files) |
| Board P generator | `v2/ecad/tools/gen_sch_p.py`, sha256 `e111e10a047f587eee8e32d005440d527d630d68b9a1970028b39c87fc12fd7a`, generator identity `4ce12f9caae757d0` (`sch_prov.generator_sha('p')`; TS network 270 ohm / 18 kohm) |
| Main's generator it replaces | sha256 `d66ae0a15be1dc4e8a755dab6e5996a1ece5bd2bc2d9a6c93b365c1b75e53714` |
| Regeneration | vast.ai box 52646493, KiCad 9.0.9, 2026-09-26T13:32:48Z to 2026-09-26T13:33:16Z, driver `evidence/regeneration/bat_box.sh`; log, parity, change records, gate verdicts and output hashes in `evidence/regeneration/`; the regenerated files in `candidate/` |
| Fixture | `v2/ecad/tools/tests/test_pack_secondary_ts.py` (new, sha256 `26316ddfe7fc1e1bb6ef2605aa57cba3fde1f213739a07503baf604a4f24222f`): FAIL on main's generator and committed netlist and on the first cycle's netlist, PASS on the candidate generator and netlist (`evidence/regeneration/test-pack-secondary-ts-runs.txt`) |
| Parity of main's committed board P files with main's generator | schematic PARITY, netlist PARITY_AFTER_NOISE, BOM PARITY, ERC PARITY_AFTER_NOISE, intent PARITY_AFTER_NOISE (`evidence/regeneration/parity_*.json`) |
| Board A charger revisions read | main `1f614233` `v2/ecad/tools/gen_sch_a.py` (sha256 `02271970ab6aec2acc55253c1edec8de490f16a0225cec31e345acccc36b25b8`); round-6 candidate `wt/r4a` `gen_sch_a.py` (sha256 `a0452054ec04cf5d9f5b7590acaf6b95131e0ba30bedd67146f04978e455a83c` when this manifest was written, uncommitted and still moving; first read `17c204ad4fb0cddb8dbb58c1320ecb4ae79c1bc6fe1bc4857aebb0732734e272`, second `a0452054ec04cf5d9f5b7590acaf6b95131e0ba30bedd67146f04978e455a83c`) |

## Files of this packet

Paths relative to this folder.

| File | Bytes | sha256 |
|---|---|---|
| `CHARGER-STATE-SEQUENCE.md` | 18939 | `df84d98b9e47160cecd42a3c736b246b2da363871a668775d90ed5f1dc2fe1d9` |
| `FUSE-INTERPRETATION.md` | 19638 | `c2fa9df36a9776ff08edf30b10983b528bbfdc1763ae7b0ec99689cd78c23f6f` |
| `PRIMARY-CONFIGURATION.md` | 26834 | `45c0267f7277abc1ccced4fc8c5be1d9baf92426900b38ad14d43aeefedd9f66` |
| `PROTECTION-ARCHITECTURE.md` | 25065 | `21b0535ecafa9aa046f0ee4cc2a80a796b04aaaab6a72922ca36bb7999c14ce7` |
| `README.md` | 790 | `68f059b840bb6a13f6e21399ffc821602d327c3dd745d87cfaa5fca58ad94a83` |
| `REVIEW-REQUEST.md` | 26743 | `e36ebfd98c2ead3a5c2b4529ab7ba78bd3d5db901eebf2ef16a62143faa0d0db` |
| `SECONDARY-OT-DECISION.md` | 31849 | `5a784f1731b9db1fe1b9a0ac917b2275110d1c418fac7cfc2ab41f897543fab3` |
| `candidate/netlist-diff-vs-first-cycle.txt` | 384 | `09bcb21d687c3e4f9b3ae968205f68b8c37521b6fc46ca75bbffc09745ee4fef` |
| `candidate/netlist-diff-vs-main.txt` | 1004 | `79c8e0ece3bb125ccf0ba52ae9d4d5429980e51dd4ff4f9d88ebaac1b5c03465` |
| `candidate/pcb-p-pack-bom.csv` | 3785 | `2e3980dc2a769db2f2793b0c317a6f8551c5ac658a99b72f4b3bda7037f2a617` |
| `candidate/pcb-p-pack-erc.rpt` | 18778 | `a7b62efd2dc8eeee77c7ba3cac36f0304ce28af2069164b6e0087fa9cdc4c9a9` |
| `candidate/pcb-p-pack-intent.json` | 3729 | `3ba1e58f688bc3abd6e91c4715c040bf268f25c09d90939eeaf2b80a63a5ec22` |
| `candidate/pcb-p-pack-jlc-bom.filled.csv` | 3058 | `96800431d8c436104dd1f2eb7fe789c587ec0910ea6f0d12efadca32898cc814` |
| `candidate/pcb-p-pack-schematic.pdf` | 240695 | `0e4e637011d1711ce13993a9acc16b214e912a2efef8ba47d47b618e3404c204` |
| `candidate/pcb-p-pack.kicad_sch` | 274432 | `2dba8588613db426d28afc126961542f3cc7e60644adead99b08eb887c69d911` |
| `candidate/pcb-p-pack.net` | 92058 | `4342c4cbe1b43dc43dd2ef28817e7f3c027baecf829ddf340ccf01fbab4b0fa5` |
| `candidate/pcb-p-pack.net.prov.json` | 8498 | `0b6843036ca941a2bd10080190569960cd74a4b379cbf29a5da750d10876e895` |
| `candidate/ts_network.out` | 3438 | `4d986756daf09ab854417d1d6b87acd4f25ac3a3e2e2d447fd490605d67ecde0` |
| `candidate/ts_network.py` | 10374 | `2a6925c4c62c030efb3c128a9ab563fdb41bc49bcd36745072abfea13adc6bbd` |
| `evidence/check_manifest.py` | 2419 | `7f501f8a2de4cf42fb53add0dab4e77a28cb0c7507e59bb758de8eb0ac8e06c7` |
| `evidence/jlc-queries-bat.json` | 8925 | `69ba9104f80d94b2ed8e79ba26c40f1fe9760d42d4f0442eb94606d46f4d52aa` |
| `evidence/trm_defaults_check.out` | 8517 | `b04e2438d09cbf4a514c854dc215e8252cf0b1290839095af11709bb3ed6b0c4` |
| `evidence/trm_defaults_check.py` | 12770 | `870eecc2f324fcd38268afcde63a012ebf9f36931bd0970eafb0d15980f99500` |
| `evidence/regeneration/bat_box.sh` | 8197 | `ebfbb319abc08d530b05e8b047d29e36f392645abf123db50fbf7a0d2c0b2b10` |
| `evidence/regeneration/bom_diff.txt` | 876 | `517b96a2453b23f73e0951fd030a0b12fe4d8b1645889b0650fcbc904886474c` |
| `evidence/regeneration/change_bom.json` | 1104 | `3fb0d3832c2cbb5585bdbe8328cff419a6c72f89af17838db4b6cd0b68c21734` |
| `evidence/regeneration/change_erc.json` | 814 | `a4164c9d445358715777d5502f3c10f5622f809ebdf7a9cff057116b66b26312` |
| `evidence/regeneration/change_net.json` | 5818 | `755f4f54b62a30526bb354862029994b3a041b042247439daeefe833c08c8955` |
| `evidence/regeneration/env.txt` | 192 | `8b1712b908411a51ebb9679887b1f2bb09139cb86a1f0ca0f5831ec66439c1b5` |
| `evidence/regeneration/generator-sha256.txt` | 229 | `e2fb67eed59d1ec85065a399e0d4e4a657fdd8e19512983adf93c516c2ef8893` |
| `evidence/regeneration/netdiff.py` | 3612 | `233d391292bd69c27d227c0c99d59c38ae95cd9d52cf5cf26a432287befd3515` |
| `evidence/regeneration/overlay-files.txt` | 27 | `cb8fdd018ce1631e0433a650329c6d3de768a9865fbbb7675a9db9d4e1e69d0d` |
| `evidence/regeneration/parity_bom.json` | 66 | `cb06effee90d3015e2072f4e4501d9955cae6b42b056aec707a75d573202706d` |
| `evidence/regeneration/parity_erc.json` | 281 | `1c991cfae6347800c939a6e90fe17fe11e826d9024e42cefc83de7a0884ba420` |
| `evidence/regeneration/parity_intent.json` | 76 | `607f2e1b7adb75dc66267217a7334114126f37ea6ca8cab0548736b90c1ba3d4` |
| `evidence/regeneration/parity_net.json` | 710 | `38232469c3f70134cacf5560ede7728daf73a4226cea020143cfac35454f8900` |
| `evidence/regeneration/parity_sch.json` | 345 | `f466f68f3e846502aa2ed1a2474c0294577ce676326e266ae941e3725e161453` |
| `evidence/regeneration/run.log` | 3594 | `6178dc6af090f9cb3c3ecd085cba18427d293c8bb1c86e9c8e76f10c9c165ca9` |
| `evidence/regeneration/sha256.txt` | 3376 | `b19fc501b6011523fcf7d61b09719f781c33bb19f1b1fb23731973474d6b22b2` |
| `evidence/regeneration/test-pack-secondary-ts-runs.txt` | 4894 | `e30f054450f2198571691dcdd6e31d7a62f0b678bcf1b19dda46753eb14ba722` |
| `evidence/regeneration/gates-base/check_contracts.log` | 6358 | `23dff7ee905e6949e27b538d3998e737e1d498b9fd1415b2057f96cb154c44da` |
| `evidence/regeneration/gates-base/check_contracts.verdict.json` | 1613 | `c02269c6430fc22a97e50c7c9913854eac5eb6c82fe4085f30914220aec27ed0` |
| `evidence/regeneration/gates-base/check_contracts_a.verdict.json` | 2609 | `a87aff3bfd65c3fd14b66904a59edc8ee51a6a0a4923fc441942cc136a4b4c59` |
| `evidence/regeneration/gates-base/check_contracts_b.verdict.json` | 2690 | `fecf21ab7071a329612f97eaf4f508fecd59a6a00110d0af58b7f92f06653e71` |
| `evidence/regeneration/gates-base/check_contracts_c.verdict.json` | 1188 | `c2524a50536f738c8b4ad7edc7ddbc771a35a2a381066b09f7737d793b77c382` |
| `evidence/regeneration/gates-base/check_contracts_d.verdict.json` | 1328 | `db47db021c1caaf6b33d4bc437f25265e6f3220edacee3b040feeaad1214c8ae` |
| `evidence/regeneration/gates-base/check_contracts_e.verdict.json` | 1123 | `0c1676539349c4cd215583754c4ab478265097def4b67cfa9c86e23257bf53ae` |
| `evidence/regeneration/gates-base/check_contracts_p.verdict.json` | 723 | `054d9116e8a941519178e5ed7b063459a9a2d304533273638a0f0a0489f35918` |
| `evidence/regeneration/gates-base/derate.log` | 599 | `4ffcc40839e4f894ea14b01794650fa63c46f655487e68ce8a97ffdaef20e423` |
| `evidence/regeneration/gates-base/derate.verdict.json` | 975 | `d352c611ff034fcbb19d2da659e5ea9ddb88898e369cf18621fe1ebc88c28e4c` |
| `evidence/regeneration/gates-base/energy_chain.log` | 3460 | `400f7c926a45882ef89dddf5aa5d0157dac2d2c97302485a5035dd5d9d1595b7` |
| `evidence/regeneration/gates-base/energy_chain.verdict.json` | 1945 | `61f7c5facc2de48c5e3797ffb2e891a33550c341391e5ca17d3cd4f077b57138` |
| `evidence/regeneration/gates-base/energy_chain_a.verdict.json` | 1012 | `0c1eabca0d74eb4a0c0acda25786c0d9ab484a1e56d0dc1a4334fe390ba9cef0` |
| `evidence/regeneration/gates-base/energy_chain_b.verdict.json` | 1636 | `2a4f7fff07f4b782a37336eff56b6d73000068c8714ec7196714a60283c6589d` |
| `evidence/regeneration/gates-base/energy_chain_e.verdict.json` | 899 | `15da9acdf5e7ce5afac83c7740f4359177c25af339bc2b9b9e8debb788b1fa88` |
| `evidence/regeneration/gates-base/energy_chain_e5.verdict.json` | 963 | `aff2185c374ea56bb54395d6ecdb3ed7f93dd337b76188da203a170a8087701d` |
| `evidence/regeneration/gates-base/energy_chain_p.verdict.json` | 897 | `27fd30401bc8ea10684ccf958a9ba155d2f890b532bb7ca7e759401f8663d48c` |
| `evidence/regeneration/gates-base/erc_gate.log` | 342 | `3ff8d86ec8da8b492a774a4ba76ea994b836852a1d3bf224c6871414e7123153` |
| `evidence/regeneration/gates-base/inhibit_chain_a.verdict.json` | 1212 | `2c929d72f7e0820ce3ba175315bf6335eccfb075c3d7e45dcc2c42b69074ce3e` |
| `evidence/regeneration/gates-base/inhibit_chain_b.verdict.json` | 1096 | `038784edf25a5db94deb6d0ee0a3006d927d12f9f68b7c5d8a31b5880ea2265d` |
| `evidence/regeneration/gates-base/inhibit_chain_c.verdict.json` | 837 | `f271ddd5ef0dfeca74354a893ee3e9fae3b495ab944bd3db9e9d9901101ea45a` |
| `evidence/regeneration/gates-base/inhibit_chain_d.verdict.json` | 837 | `62c86e32c0e289f55324844d2db5cd09a483e931b10c1e6d3879264d851aae17` |
| `evidence/regeneration/gates-base/lcsc_fill.log` | 288 | `2c1c4447073cfe1ffd020aaf87ff52e7f5f030a5a7bf60b226c2c28124095242` |
| `evidence/regeneration/gates-base/lcsc_fill.verdict.json` | 1287 | `e56921a8b75590c889c9adf84a479b098c8689c24a81b672ef096968527be696` |
| `evidence/regeneration/gates-base/pack_protection.log` | 832 | `de1aa29fbfacb46e90bb2340e7c1e33175747b84e71ae60fc0fab174a76c9d70` |
| `evidence/regeneration/gates-base/pin_map_lands.log` | 319 | `d0e607262cffa2f38809a00d3ee10b2101db935c4d196caf64b866b4710fb153` |
| `evidence/regeneration/gates-base/pin_map_lands_p.verdict.json` | 842 | `fa501bb824fd7cf6353e2a9a0c16ef80e72d453530f14ff63baa2458cb8de13b` |
| `evidence/regeneration/gates-base/port_protect.log` | 487 | `af43a31121fa1a64117a5c8f4da49d4d67bee97020174b94ab458e97913c0864` |
| `evidence/regeneration/gates-base/port_protect.verdict.json` | 974 | `4945b7a2c9782a1668640f1dc8c29ab92fff80d72b16a8c718128bfee7dc5509` |
| `evidence/regeneration/gates-base/port_protect_p.verdict.json` | 1053 | `166ccf5b81d15d61333d094b6d36a3b0627f8cf3f78e7f26d72e5c392816108d` |
| `evidence/regeneration/gates-base/power_path.log` | 1048 | `905c6f0c122f7bf2b76b625196ae4f9ac7f06846434871851bbe7d5626f92267` |
| `evidence/regeneration/gates-base/power_path.verdict.json` | 890 | `bd78fb54c9277257f8f0a79b4909b0d92b9d60c41dbfa816b6f77237f62b7aac` |
| `evidence/regeneration/gates-base/review_nets.log` | 124 | `f373dceaf6003c0d38568cadcb941485e8e2cc8047c2e89f1efb8530cdf79d02` |
| `evidence/regeneration/gates-new/check_contracts.log` | 6358 | `95a4315b25f123f1ce84a4b995f00effdedb1cb158fad328d69689e71ead852f` |
| `evidence/regeneration/gates-new/check_contracts.verdict.json` | 1613 | `0b25995885378d727788d5b6b949914354aaa258b7cc7100b4fa69cdd4416f6d` |
| `evidence/regeneration/gates-new/check_contracts_a.verdict.json` | 2609 | `a01afdb7f958f97fd62f6a9d27202b251d44edd267de24ea99f3c92017ae31a2` |
| `evidence/regeneration/gates-new/check_contracts_b.verdict.json` | 2690 | `141786b486cde4b9cf413aae1ef53b67f34dc4928ae5f7c4ce782dc5a2cf5de5` |
| `evidence/regeneration/gates-new/check_contracts_c.verdict.json` | 1188 | `11f78aea3e2f54aef1cbea2a8b905e0eb456174b18d2252bc84e0c544a5d5270` |
| `evidence/regeneration/gates-new/check_contracts_d.verdict.json` | 1328 | `df6449c9910ff0be854d1b4b97a0cb33d1e7e7f82bcf826980b9c333d160cc85` |
| `evidence/regeneration/gates-new/check_contracts_e.verdict.json` | 1123 | `2c77ef378d5922abcaf2172192c9b1532f8e127326eb56f92b56bce17aa82c0f` |
| `evidence/regeneration/gates-new/check_contracts_p.verdict.json` | 723 | `012699cc991d5d985489438df9bf955dd8d75a35019f293274fe14d6d285926d` |
| `evidence/regeneration/gates-new/derate.log` | 599 | `4ffcc40839e4f894ea14b01794650fa63c46f655487e68ce8a97ffdaef20e423` |
| `evidence/regeneration/gates-new/derate.verdict.json` | 974 | `92b02edd7c462406dc5e694fa0f41211bb4fc67e600f63f37c0c999fc547d9f0` |
| `evidence/regeneration/gates-new/energy_chain.log` | 3460 | `400f7c926a45882ef89dddf5aa5d0157dac2d2c97302485a5035dd5d9d1595b7` |
| `evidence/regeneration/gates-new/energy_chain.verdict.json` | 1945 | `7ab450e7f0f78f336f6faf00a0b2550c1ec68aaa03baa796f58727c4f1569026` |
| `evidence/regeneration/gates-new/energy_chain_a.verdict.json` | 1012 | `d1b00ece220c01d970952b8ce09f695bd8dc851c37fe4cec5dea5512884b26d4` |
| `evidence/regeneration/gates-new/energy_chain_b.verdict.json` | 1636 | `8645b84d3035eb4c02b189968bd33136644be79290277d0bc0dbc83013f3b74f` |
| `evidence/regeneration/gates-new/energy_chain_e.verdict.json` | 899 | `d636934c489cc77b0a0059cc18c32d288817a902da3aaa98051526769e8d3174` |
| `evidence/regeneration/gates-new/energy_chain_e5.verdict.json` | 963 | `9126a9834b2208ecbd2f971674d9cbcd00100b7d69fd021495ee14fd34fd3feb` |
| `evidence/regeneration/gates-new/energy_chain_p.verdict.json` | 897 | `af441ae272a3ef53324f1cbc4cb644f45ff0a8191bea49c7baefe83bfead9e2f` |
| `evidence/regeneration/gates-new/erc_gate.log` | 342 | `e2cd0a9beceac3bf73cb67d46bf62ddac68df74cbeebf77ccbad49f0b53c2c76` |
| `evidence/regeneration/gates-new/inhibit_chain_a.verdict.json` | 1212 | `0c4ef631f559859022923ff49552e6afb1e7a5f22194a225c6f3ff558b7abbb3` |
| `evidence/regeneration/gates-new/inhibit_chain_b.verdict.json` | 1096 | `a04b0bf060fa3d2fc1f9488b7f7acb57e2a5e5ed50bba37f1b84d7f05fbc0fcb` |
| `evidence/regeneration/gates-new/inhibit_chain_c.verdict.json` | 837 | `14463dd387e262f3a809807da71cf9d2e51e20da33cd14fa2205ede95eef94b7` |
| `evidence/regeneration/gates-new/inhibit_chain_d.verdict.json` | 837 | `3adb5c157a2343ad6221b5bdeb2e8e21692d5f66ca16f75b0f9032e5a7dff306` |
| `evidence/regeneration/gates-new/lcsc_fill.log` | 288 | `762c54dbde241ddcfa786aae17e28bab09f08f5346d29e9acf7763aaf11002da` |
| `evidence/regeneration/gates-new/lcsc_fill.verdict.json` | 1287 | `df0c7edd4ab4efe0a7f5cc22493c48a5ffed28debf9d33ec1592f71470bf3cad` |
| `evidence/regeneration/gates-new/pack_protection.log` | 832 | `de1aa29fbfacb46e90bb2340e7c1e33175747b84e71ae60fc0fab174a76c9d70` |
| `evidence/regeneration/gates-new/pin_map_lands.log` | 319 | `94eaf3b3d4246f71e29ec3677db6c69be7168a56b96866af883fee592451a8e7` |
| `evidence/regeneration/gates-new/pin_map_lands_p.verdict.json` | 841 | `72031a379cdb7368ca0393be38efd4b86e2d203f6b9fb9db7c6d5eaaa987dd65` |
| `evidence/regeneration/gates-new/port_protect.log` | 487 | `af43a31121fa1a64117a5c8f4da49d4d67bee97020174b94ab458e97913c0864` |
| `evidence/regeneration/gates-new/port_protect.verdict.json` | 973 | `899de5d1e685d0cf92f627950e9ff6e38ac7bbe19de81302423145a00d8c73a4` |
| `evidence/regeneration/gates-new/port_protect_p.verdict.json` | 1052 | `b3604f1f796588bfe5d93c2259fdad7817a6f50186e40fcb83e3e2a133120fb7` |
| `evidence/regeneration/gates-new/power_path.log` | 1047 | `310bf2e7305e1df3b77a1b8a5da11319a7adfe763ce5a6ec847c18718e6bfe6e` |
| `evidence/regeneration/gates-new/power_path.verdict.json` | 890 | `6b03b699bc8c60a59a8a002d42d80006db26a3add415651899f10572e1a7a4f6` |
| `evidence/regeneration/gates-new/review_nets.log` | 123 | `f05a4c14dcadb948f1732e8043e741898346242808802c3df97a6d79e782195f` |
| `evidence/regeneration/lcsc_fill-runner/base-lcsc_fill.log` | 248 | `928006e11b8ec35a03cc0ed42b406ed574f7ba4624e5252ba0dedcc290c3df69` |
| `evidence/regeneration/lcsc_fill-runner/base-lcsc_fill.verdict.json` | 894 | `96a14f7e018aa272b2a98797351d19f0dd257ebe92b2b980832aa14a627e352e` |
| `evidence/regeneration/lcsc_fill-runner/new-lcsc_fill.log` | 248 | `85492144ce0cfbce7d6f3ac99351b79a02cab17904052d6ff94dcd3e6cc84cae` |
| `evidence/regeneration/lcsc_fill-runner/new-lcsc_fill.verdict.json` | 894 | `7e7585fa4916de91fb07e6cac83a679f504fa5a779880c7af42c3523f71d9164` |

## Documents cited

Paths relative to the repository root. Every document the packet cites is filed under `v2/vendor/` with its source in
`v2/vendor/sources.txt` and `v2/vendor/SOURCES.yaml`. Rows marked "filed by stream PKT" arrive with that stream's merge;
their sha256 here is that of this stream's byte-identical copy, compared on 26 September 2026 with the copy stream PKT
filed. HTML files are snapshots of a dynamic page: the sha256 identifies the copy, the quoted words are the evidence.

| File | Filed | sha256 |
|---|---|---|
| `v2/vendor/battery/ti-bq4050.pdf` | on main `1f614233` | `2664e33fe6d6ebed3a0f58153d8ba8ce66cb84f07741f6708ae11a224f443f5e` |
| `v2/vendor/battery/samsung-35e-orbtronic.pdf` | on main `1f614233` | `5ec577b952b9dc5106593a4e4c3a6e8cea64f6f72b8faaf1bb512155c29dc516` |
| `v2/vendor/battery/samsung-35e-akkuzentrum.pdf` | on main `1f614233` | `d2a7c686941c1f4237240ee140127e6828f6d590170cf5a7f30d945d1aab50a1` |
| `v2/vendor/battery/semitec-at-p12-13.pdf` | on main `1f614233` | `389dc527ed8d783cbbf94db460504e26d17993020d8d3627056499a9264b3262` |
| `v2/vendor/battery/ti-csd17570q5b.pdf` | on main `1f614233` | `596555c33dce1fcac6de3b6ecc3eeb443f202382b3e2091fd6e1c27d129f2436` |
| `v2/vendor/battery/littelfuse-287-atof.pdf` | on main `1f614233` | `c02ee0e20cdd5fb0f213cee2bad742b7c6a6f63fb50eb70e89574b48c467015e` |
| `v2/vendor/keystone/M65p42.pdf` | on main `1f614233` | `caa141ea51ac68cf80ab6e14ad2075fcfc76206451f4bfe45330005c0deaf395` |
| `v2/vendor/keystone/littelfuse-297-ficcorp.pdf` | on main `1f614233` | `98a7e99bc5bbdf2abc9f329de5b779ea97fc78a3ba9aa8d8fecc0ec5b9c3a778` |
| `v2/vendor/ti/bq25731-datasheet.pdf` | on main `1f614233` | `3e5e927fdf63cf6a2397630987c58e947ebc80d5a1cfc93fb1fb58d98bb58973` |
| `v2/vendor/nexperia/nexperia-pesd5v0s1ba.pdf` | on main `1f614233` | `6546e415b8885ea3790c91629034c6b4e5c6961d5fde734e55dfa479dd8dc49a` |
| `v2/vendor/battery/ti-bq77207.pdf` | filed by stream PKT (same review; pending merge); not in this tree yet | `45c1c99e2d303be8bcf1a2b1eea8275f657c7c80170bda7c2778042a688295cb` |
| `v2/vendor/battery/ti-sffs317a-bq77207-fusa.pdf` | filed by stream PKT (same review; pending merge); not in this tree yet | `fe429cf90332c2bba2eb3d456036312982ff25eba4f0f370a2107b67ed4812b3` |
| `v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf` | filed by stream PKT (same review; pending merge); not in this tree yet | `525d16b2bdee44e5b587ccf6800b9967bc524772d0b5a20937957ea2e738b7ad` |
| `v2/vendor/battery/eaton-scf9550-elx1135.pdf` | filed by stream PKT (same review; pending merge); not in this tree yet | `3ecc2424acfa1753c2aec0b62d5706d4f25b7a08e731795c0d84d59938a3158e` |
| `v2/vendor/battery/littelfuse-itv9550-30a.pdf` | filed by stream PKT (same review; pending merge); not in this tree yet | `018e0d53243b986d0f089eb210728452c94cf2bbbcd09fd160e6a36ff2ff72ed` |
| `v2/vendor/battery/murata-prf-series.pdf` | filed by stream PKT (same review; pending merge); not in this tree yet | `a29cd6200c656636fd69bf525d365cfa50432a2fe696ee8ee9e172a4b7cba27a` |
| `v2/vendor/battery/ti-sluubf9-bq4050evm.pdf` | filed by stream PKT (same review; pending merge); not in this tree yet | `917c0db25428865ac1124aedfa315343fa9cee6bf54db8bae967cec7deb029d1` |
| `v2/vendor/power/aos-ao3400a-n-mosfet.pdf` | filed by stream PKT (same review; pending merge); not in this tree yet | `9c60d0b6c1ddc7609a4b788a91181468d8ffe6c3e9ba425c3d8ffc5ba88c5033` |
| `v2/vendor/power/jscj-2n7002-c8545.pdf` | filed by stream PKT (same review; pending merge); not in this tree yet | `7941fb423af7c6c6c8979063a7e8819bb19217ece275efcce18948950a41d9f6` |
| `v2/vendor/connectors/jst-ph-catalogue.pdf` | filed by stream PKT (same review; pending merge); not in this tree yet | `447624f4f2f7d37c58c1eaa7ee314ad757fe7aff48f6186491ef6f69fbc00b96` |
| `v2/vendor/ti/ti-e2e-1316778-bq25731-chargecurrent-por.html` | filed by this stream | `96c511cf238d00182bcd82c5e7bdce3d25571c49cbd77f6b57a9171159f0d8c4` |
| `v2/vendor/battery/ti-e2e-1421182-bq77207-application.html` | filed by this stream | `2038e7af80b8c35e3b0a92c07f9d0edd482e146bb0e0bf80072c0c2b6428610c` |

## Route evidence and the session's record (not part of the packet)

The reviewer-candidate pages behind `REVIEW-REQUEST.md` section 5 were saved as HTML snapshots on 26 September 2026. They
are third-party web pages the reviewer does not need, so they stay in the session's record with the integration notes
and are not published; their URL and sha256 are listed so the quoted words can be traced.

| Page | sha256 of the snapshot |
|---|---|
| https://accutronics.co.uk/ | `b3de90eb0f5c1b2c8ca7ce6453268ec87e205baeaebfd4cb323232cf6dff5b98` |
| https://accutronics.co.uk/custom-battery-and-or-charger/ | `b347ae18c3e9f2c9734e619a3b1f0c1078481438bb04208582f2ba816ce7bd23` |
| https://accutronics.co.uk/product/nd4054hd50/ | `69c2d86d61938aafe7986d6f852f8b159bd7691f055f2545ca746b868d6e7cbf` |
| https://engineering-spirit.nl/en/ | `2e95e148a49b0c76680762b493d8466a091e1cc6d56c15921718c4deeed14f60` |
| https://engineering-spirit.nl/en/bms/custom-bms-battery-management-system/ | `85d5a985cec90daa887578862d1664ace0d5e5dbb0703300dae799d54fece1a2` |
| https://www.jauch.com/en-INT/products/battery_technology | `921997fbac265ec27607228c1d84c0dafd766b7077c1a3b99d00cbea134a3a3e` |
| https://www.ti.com/design-development/partner-directory.html | `165faea3ff6dd944489550b97cf7113d5c0ed4a95bcd21027893fbb67213e438` |

| Session record file | sha256 |
|---|---|
| `drafts/bat-integration-notes.md` | `af4516bccc528c3e309a9237fa060357ac26961de499458f0b19a6f9f640bc5b` |
| `drafts/vendor-files.txt` | `f3c546e124cc2b27f89dba24d7283e7329508a258642f3bcbceebcb4b33aac36` |
| `drafts/datasheets/SOURCES.txt` | `fa0399eb8bfcf2a9c9d0fb1a3bf9306836f6b6cd8194742a7fd5099d35d2e576` |
| `drafts/box/bat/suite-worktree.log` | `b10fecd057ba0aff6bc53aad1a7e4d5cea3aee4c071177e08ddaf256aafc2629` |
| `drafts/box/bat/suite-worktree-cycle3.log` | `239a5d3e3d1fd06459627ce8bd081aecd534629520b50a16a9da1cca29cf7fec` |
| `drafts/box/bat-cycle1/run.log` | `9bffc3191029b7f528e42f8e9302f3d2b1ba00ad34a2ccfe0efafde5702d99e7` |
