# OD-01: the package an engineer needs, by path and sha256

MESHSAT-1357, stream od01b, 29 September 2026. Written by `make_package.py` beside this file (stdlib; it refuses to run if a
listed file is missing) at tree `d8992d4e` plus the working files it hashed; the same list in `sha256sum` form is `PACKAGE.sha256`.
Prototype: nothing in the package has been made, bought, sent or run. **Export:** copy every path below keeping the
repository paths, then from the repository root `sha256sum -c v2/docs/records/od01/PACKAGE.sha256` reads OK for all 74 files
(14.8 MB in all). Groups A to G are what a shop needs for the quotes (each part's drawing PDF governs its DXF and STEP); A, H, I and J
what the operator needs for the tests; K regenerates H1; L holds the later independent checks and the records the documents cite. This file, `PACKAGE.sha256` and `LOG-od01b.md` are not in the list.


### A. Read first

| Path | Bytes | sha256 | For |
|---|---|---|---|
| `v2/docs/records/od01/README.md` | 6038 | `31c019e73786b7252dbbd8aaf5fce6296ef68185541616065f639bb57d0eca67` | the package's index and what remains |
| `v2/docs/records/od01/TEST-BRIEF.md` | 9663 | `81ffdb45977af14c452032c5108d6cabc07792e993cdfa6794180aa7adc44af2` | the operator's two-page brief |
| `v2/docs/records/od01/TEST-PROCEDURE.md` | 39339 | `31545380c4629456510422d89b2ac6391311c9016e14a9654ba1c5f83ebd3650` | the complete procedure: what the heat test proves, the shutdown and its verification, set-up, steps, patch runs, test B, stop limits, records |
| `v2/docs/records/od01/MACHINING-RFQ.md` | 20773 | `f12c13949b0c6b284a57bc1cfefe48b55bf522e486a8071e2cde3e67c7275c78` | the request for quote (NOT SENT) and section 6, the receipt checks R1 to R8 that gate cutting |
| `v2/docs/records/od01/CHECKOUT-LIST.md` | 30994 | `81c4ae18e84efaa158af2b9dc3e879d14cdc44f1ad1e682e6d8b87d4d6f3886b` | what to buy, priced, with sources; lines 10 to 15 the shutdown |
| `v2/docs/records/od01/checks/check-1.md` | 5919 | `c0fe6fbabb7ac861e37a1ff7172b4496d71014fbd0bde5b26153ccd39efd1be7` | independent AI check 1 of the package (28 Sep) |
| `v2/docs/records/od01/checks/check-2.md` | 8584 | `2cd0f10fee406e0ba1fc3018d9c4a938701779cb529b437321075680c70ee7bf` | independent AI check 2: the lead exit's bias under 1 percent, H2's size |

### B. Quote: H1 (heat test)

| Path | Bytes | sha256 | For |
|---|---|---|---|
| `v2/release/case-2026-09-27/h1-heat-test-plate/h1-heat-test-plate-drawing.pdf` | 73447 | `f737c08588fabdf5e14706c530f12c8c0361a3d568947a8b3303681942e78406` | sheet H1-1, governs |
| `v2/release/case-2026-09-27/h1-heat-test-plate/h1-heat-test-plate.step` | 138325 | `e5b3ca495dcfc2389c7951da4a8edf5438960d42afd02500602897dbf9105d22` | H1 solid |
| `v2/release/case-2026-09-27/h1-heat-test-plate/h1-heat-test-plate.dxf` | 21329 | `c499bd35844f6c560abb88e9f7cdd2dd5dbd93c64e43e9b1d8af2251f5de5ca4` | H1 outline and features by layer |
| `v2/release/case-2026-09-27/h1-heat-test-plate/h1-heat-test-plate.stl` | 409084 | `7697959db5cf696fa22d0f268fdaa4403238c348effdc330f2993d7833080b6e` | H1 mesh (viewing) |
| `v2/release/case-2026-09-27/h1-heat-test-plate/h1-heat-test-plate-check.out` | 1853 | `b2a51e79375580cac389a14f7e7286056af7ba28797663244c655b2514863511` | the generator's check against C1's DXF (PASS of 15) |
| `v2/release/case-2026-09-27/h1-heat-test-plate/README.md` | 8439 | `3ebea915030020441c74b697aadf8a0a005722c81b3728e22a966427f2475907` | H1's definition, choices and provenance |
| `v2/release/case-2026-09-27/h1-heat-test-plate/MANIFEST.sha256` | 701 | `150e284bbd7faada56e8cd216b59497fece7f82a91af1716b1518eec58cd1ae5` | H1 folder manifest |

### C. Quote: C6 legs

| Path | Bytes | sha256 | For |
|---|---|---|---|
| `v2/release/case-2026-09-27/drawings/frame-and-legs-drawing.pdf` | 79476 | `792143ed01c0be6b29c4627fc2470014844fb22fe473e41182ad27239c45dd46` | sheet 2 |
| `v2/release/case-2026-09-27/frame-legs/frame-leg.dxf` | 18083 | `68a33b0a6a46d51cff61db70436aa908f943296f5cc78982bf9a13d2e516dc04` | the leg profile, 4 off |
| `v2/release/case-2026-09-27/frame-legs/frame-leg.step` | 47922 | `2c23e390147fe8e56f6d03852b4c329be9edd9181577431d37227ccc314e3711` | the leg solid |
| `v2/release/case-2026-09-27/frame-legs/frame-legs-4.step` | 201602 | `c0079f4253d7b41bb953a664778f9cc24cabef08f275a36d3b69431476b77c3e` | all four legs in place |
| `v2/release/case-2026-09-27/frame-legs/leg-locator.stl` | 9884 | `5d40b356cd7991ee710d0f07bb6ab4e08867b6be2f8ff603a8f26e93265a3d62` | printed locator (operator's) |
| `v2/release/case-2026-09-27/frame-legs/wedge.stl` | 4284 | `8c49cb7a62813694d4d8970d6b3761e14bbeac6381128b189d8078195c2e3bcb` | printed centring wedge (operator's) |

### D. Quote: C1 face plate

| Path | Bytes | sha256 | For |
|---|---|---|---|
| `v2/release/case-2026-09-27/drawings/face-plate-drawing.pdf` | 80622 | `ef9a2fb1df36deef74b5959633dd15583ea7388d8e48bd0f087f9f086fa4d061` | sheet 1 |
| `v2/release/case-2026-09-27/face-plate/face-plate.step` | 426383 | `48343402a8370f36eb8a0474de6eb3cdee50e1df127c515781736e2ada8ca696` | C1 solid |
| `v2/release/case-2026-09-27/face-plate/face-plate.dxf` | 30671 | `19703fa5838f9e4acbe0dc4021a77ca34b38e8b3c2fbe840678c53dfc6e3c551` | C1 outline and features by layer |
| `v2/release/case-2026-09-27/templates/face-plate-1to1-A3.pdf` | 8089 | `4cf3f68b88d8af9ea47b3c25473e72c52ad62484c7b5aa1e3ddf12a5253f7ee1` | 1:1 check print (optional) |

### E. Quote: C4 entry plates and gaskets

| Path | Bytes | sha256 | For |
|---|---|---|---|
| `v2/release/case-2026-09-27/drawings/rf-entry-plates-drawing.pdf` | 89052 | `81379c5092c1646d99b91b919b7eb94fb4da88fa3faf17c06f997e634ec0110c` | sheet 4 |
| `v2/release/case-2026-09-27/rf-entry-plates/rf-entry-plate-east.step` | 103556 | `0d2652add80c7f206240f74e9fcddd040b11ed29bd7e41b6271c1a43b1f801aa` | C4-E solid |
| `v2/release/case-2026-09-27/rf-entry-plates/rf-entry-plate-east.dxf` | 20634 | `97cb168a79c6b37feee6fab2d6865913f48d45250eeadeb75c393b42d2466307` | C4-E profile |
| `v2/release/case-2026-09-27/rf-entry-plates/rf-entry-plate-west.step` | 119237 | `bfb47212c0606870166168806fac40f9d7619ada3b7205acdaaf7b828697ae10` | C4-W solid |
| `v2/release/case-2026-09-27/rf-entry-plates/rf-entry-plate-west.dxf` | 21374 | `088b58c8347e2839599f1db0c1942511dbe7d1c92718927fd2aecc25c9170a56` | C4-W profile |
| `v2/release/case-2026-09-27/rf-entry-plates/rf-entry-gasket-east.dxf` | 19196 | `b5b1532e0c8f324775b5a8730dff2f76f5f1925acba086c22b9fd270975d0158` | G2 |
| `v2/release/case-2026-09-27/rf-entry-plates/rf-entry-gasket-west.dxf` | 19402 | `8a92c75721efd029a9147595866f79dba6b23b569af5e8d1d8a5a56c3a4db4d0` | G3 |

### F. Quote: C3 connector plate (quote only)

| Path | Bytes | sha256 | For |
|---|---|---|---|
| `v2/release/case-2026-09-27/drawings/connector-plate-drawing.pdf` | 82484 | `94d6561a437a6412ee8958073cabf27adaa51b1183b1b022d3695e20eadec7d2` | sheet 3 |
| `v2/release/case-2026-09-27/connector-plate/connector-plate.step` | 125567 | `fe4af0f61d5446ad8dd495dd5e1fdef73af9cd7904db39852a0c5280fc079717` | C3 solid |
| `v2/release/case-2026-09-27/connector-plate/connector-plate.dxf` | 23103 | `4b838b95ceb7dadbce590953223d0174280a947ca7070a06422765c393d5853f` | C3 profile |
| `v2/release/case-2026-09-27/connector-plate/connector-plate-gasket.dxf` | 18907 | `e316017eba5b6b29ab1fb0f7a0c171e77805456fa4742e6fa15fd3f71982ee99` | G1 |

### G. Quote: L1 lid plate (optional)

| Path | Bytes | sha256 | For |
|---|---|---|---|
| `v2/release/case-2026-09-27/lid-tray-qmx-r2/lid-tray-qmx-r2-drawing.pdf` | 128278 | `17cad64bc581548aefa3acdc827e371fbce7df59912834b20f39084048b08d35` | sheets 14r2-1 to 14r2-3 |
| `v2/release/case-2026-09-27/lid-tray-qmx-r2/lid-plate-qmx-r2.step` | 67481 | `a292846b390f7193aa3bf82b82b7b1c66281e7455c81f50c92220c1275160601` | L1 solid |
| `v2/release/case-2026-09-27/lid-tray-qmx-r2/lid-plate-qmx-r2.dxf` | 18049 | `b0b61b1402f620988715a66b44236a1df64a1a799580e5366239aabc91d2b7fc` | L1 profile |
| `v2/release/case-2026-09-27/lid-tray-qmx-r2/lid-tray-qmx-r2.stl` | 890484 | `b5c817fbe08b6d2e7789978310babfa35cf9694dc5846f92602e9b625e655346` | the printed tray (build stage) |
| `v2/release/case-2026-09-27/lid-tray-qmx-r2/lid-tray-qmx-r2-frame.stl` | 155684 | `9494a91024d4fc96ebbde26244bf57055e7e90db1b23be3692fe17895d0f5c3a` | the printed tray's frame (build stage) |

### H. Tests: drilling, stand-ins, margins

| Path | Bytes | sha256 | For |
|---|---|---|---|
| `v2/release/case-2026-09-27/templates/case-templates-1to1.pdf` | 23984 | `0f28f0ed21f2c1172e7c205d150a818a079f54ea2cc60fd3ad5c0bcd99f69cc3` | 1:1 wall templates and check prints (T5, T6, R8) |
| `v2/release/case-2026-09-27/drawings/case-drawings-2-to-14.pdf` | 381729 | `fc8d2ae9c721e7b0eb802a15f8415a8bb26490fa092582bf16322d157142f263` | sheets 2 to 14 in one file (stack, plan, envelopes) |
| `v2/release/case-2026-09-27/drawings/board-envelope-a.pdf` | 83087 | `2f6da4b1e22ecee3600cbe8bb244ddfcd393ba0732399f29387eb52ddf122b35` | board A stand-in (T4) |
| `v2/release/case-2026-09-27/drawings/board-envelope-b.pdf` | 111899 | `d14bffcb85ac5d8c68fa6e707c366150787bc9c74831383994eda49d82d6f87f` | board B stand-in (T4) |
| `v2/release/case-2026-09-27/drawings/board-envelope-e.pdf` | 81718 | `62883526a721bf7009b254094b3661a62c4b3bb4971f0a3769fa5148d7562f68` | board E stand-in (T4) |
| `v2/release/case-2026-09-27/zstack/zstack.json` | 841987 | `b4fb79d90d2f3ee1d8e1782419ea11437f573411f5292a5c2e46da47b42230d6` | the pack pocket and the stack heights (H2's and H3's places) |
| `v2/release/case-2026-09-27/margins/CASE-FIT-UNCERTAINTIES.md` | 34839 | `efc66afe9140e0228a76f8c685c87087724c186a7ff75f59ace499e4fe953d89` | the OPEN rows each check closes |
| `v2/release/case-2026-09-27/margins/frame_seat.out` | 29921 | `214e915b985518cbfe246d3e1e04a933034600825481d078a58a48cd890e449a` | the 70 margins and their verdicts |
| `v2/release/case-2026-09-27/README.md` | 13601 | `531af606ced9885969fd8194d50611f3654349e327d2eba959e4ac966066e168` | the case release's README |
| `v2/release/case-2026-09-27/MANIFEST.sha256` | 5027 | `cfd1078ef84929369f328b73a63e65a3de83f718854b173bc9662ccb98347cec` | the case release's manifest |

### I. Makers' documents

| Path | Bytes | sha256 | For |
|---|---|---|---|
| `v2/vendor/peli/1450/1451-931-customer-drawing-2025-01-15.pdf` | 428928 | `389facc842e41397c89a64395e2839b4153a93382499329c96f2a95e10d37356` | Peli's customer drawing 1451-931 (the moulding the design targets, D-08a) |
| `v2/vendor/peli/1450/1450_pf.pdf` | 121126 | `4681c0525a3cf605a0cdf669573917b75d849170eff2ae2372a958c87ffbdd27` | Peli's 1450PF frame sheet (1453-314-000 rev A) |
| `v2/vendor/peli/panel-frame-inst.pdf` | 51110 | `797a2ed6f9809d0b22d78a2e5c1b740edf444a591ef623b7d2c8fe92f6b8f05c` | Peli's panel frame mounting instructions |
| `v2/vendor/arcol/arcol-hs-datasheet-12-14-08.pdf` | 329717 | `ec17870c5a92d11e72bcee363471313909a5c1a6cd13401018684198b75ab1f0` | Arcol HS resistors: ratings, heatsinks, hole sizes |
| `v2/vendor/elmwood/honeywell-commercial-thermostats-2455r.pdf` | 795643 | `4d6ea7a29117349d28f52f86ec234c68d980d39265d3938a87b8a24b0acfdf1a` | the 2455R thermostats: tolerance bands, AC-only ratings |
| `v2/vendor/finder/finder-40-series-en.pdf` | 4564164 | `c4c8a69d0497c9c3e32be9998edbea1a3356ff80819f189864fca9361f311226` | the Finder 40.52 relay: 8 A, DC1 8 A at 30 V |
| `v2/vendor/polyphaser/polyphaser-gth-sff-al-sma-surge-protector.pdf` | 380612 | `ae3f031d7ecb8783bacd3cb57e3de76a70953645c5bf39a8b537e566e71516b0` | the arrestor (T11) |
| `v2/vendor/xenarc/xenarc-709gnk-dimensional-drawing-v3.pdf` | 1151306 | `3949bd9f618bbda8522c6df19cdfefc5effcd6d37666e14818466927e7f47f73` | the monitor's outline and depth for its stand-in (T4) |

### J. Sources of the procedures

| Path | Bytes | sha256 | For |
|---|---|---|---|
| `v2/docs/feasibility/POWER-THERMAL.md` | 137909 | `ad3ba27cef9e0f684f28ce81815afa86d44c4114b9bc10ff474308d875ba5788` | section 10: the heat-balance experiment |
| `v2/docs/CASE-MARGINS.md` | 169815 | `55244f94aace54ca09d98c100b9830cba75c70a4774c3ba375a14903fcaf6376` | sections 2, 5 and 7: Peli's figures, checks T1 to T11, when each runs |

### K. Generators (to regenerate H1)

| Path | Bytes | sha256 | For |
|---|---|---|---|
| `v2/cad/h1_heat_test_plate.py` | 13615 | `9e949f9e1b9237a20e4fbf89c0a6f27881c1187be31a1c24c00ba6226f382b00` | H1's DXF, STEP, STL and check |
| `v2/cad/h1_heat_test_plate_drawing.py` | 13846 | `8e0d56a6a030240f0651942dc97864b361ae33a11d7794eb937c86ce809c33c5` | sheet H1-1 |
| `v2/cad/drawing_kit.py` | 9640 | `49e7f00d7d57893fe2543e4d71571c2eb965993661bc1ae9d848f79ac4e87ca6` | the sheets' shared helpers |
| `v2/ecad/tools/panel1450.py` | 38937 | `3bdb88df9826024484326e8e7d67c74789ae20f610ce3e4ed69988bfc9f0340f` | the single geometry source of C1 and H1 |
| `v2/cad/case_manifest.py` | 1860 | `5433e025c0bcadb4b3607fd80bf551b491c5e1df1ef7b1481d248d571e1e50ed` | writes a release folder's manifest |
| `v2/cad/requirements-cad.lock` | 1374 | `32f887be3a68bb56b9ad9a1978c0c43ae9fdc27e40611d318c3fb054b504c5d9` | the pinned CAD venv |

### L. Independent checks 3 to 6, and the records the documents cite

| Path | Bytes | sha256 | For |
|---|---|---|---|
| `v2/docs/records/od01/checks/check-3.md` | 13523 | `445f092220cd3f67e2612be2a1a755d33d34e4b5a13de8a65e9e1d16ea5fa96c` | independent AI check 3 (29 Sep) of the corrected package; its items answered by patch_od01c.py |
| `v2/docs/records/od01/checks/check-4.md` | 9601 | `0cbfcf7701c5d8d81bef1e6eca232e9e72277a146858a614ad104bd750840140` | independent AI check 4 (29 Sep): N1 and N2 and the minor items answered by patch_od01d.py, n6 carried |
| `v2/docs/records/od01/checks/check-5.md` | 10585 | `b728ca03c369caf6b1cb548aaa6844c096507f64f5897294d806aeb1360abb7b` | independent AI check 5 (29 Sep): B1 (V4) and the minor items answered by patch_od01e.py |
| `v2/docs/records/od01/checks/check-6.md` | 12396 | `45860065af4409b81bba5b446cc046bce0de2285ce3f481e3b19ab8a4e5f22f4` | independent AI check 6 (29 Sep), the first end-to-end: B1 to B3 and q1 to q16 answered by patch_od01f.py |
| `v2/docs/reviews/READY-TO-ACT.md` | 73938 | `bdaf61a4991afb8ca1c45d0c1f71330dd8954e493af357503e01e350b8ed8fff` | the ready-to-act review the checkout list and RFQ cite |
| `v2/docs/ASSEMBLY.md` | 66445 | `ee4eff52fc5df3070f0871021380c3e9a75b12c83314ec16b78916d3399658dc` | the assembly steps the RFQ and the procedure cite |
| `v2/release/case-2026-09-27/lid-tray-qmx-r2/README.md` | 20290 | `3d3bbcfe240596398783956c15d850e36d9dc31495e8a86b49f9bcc386d2e558` | the lid tray r2 the RFQ names as printed, not machined |
| `v2/vendor/pem/pem-cl-self-clinching-nuts-bulletin.pdf` | 1237643 | `8296128324e3954db753661ce257e5b01cbe98a364964af1d4f862e9cc04fe0e` | PEM bulletin CL: the S-M3-2 nut, its 4.22 +0.08 hole, insertion after finishing |
