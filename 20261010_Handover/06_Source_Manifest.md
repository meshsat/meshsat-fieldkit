# Source manifest (handover of 10 October 2026)

Prepared 10 October 2026 (Europe/Amsterdam) by the coordinating agent session of MESHSAT-1357. Every copied file is byte-identical
to the file at its source commit (copied with `git show <commit>:<path>`); **no packaging edit was made to any copied file**. The
section folders mirror the repository path of each file. Source commits:

- `c20c4b629ff4f4d06f82ef3fe98d59d313bab497`: `main` = `origin/main` at preparation (integration set 33), the source of every file but one.
- `a6274bf77f2c6d3ffa898e34f7bfa47aede3bda4`: set 34's candidate (branch `fnd/int34`, never promoted), the source of the owner-instruction filing of 9 October 2026 only.
- Accepted baselines named in the files: Layer 1 and 2 `a9f212c7` (definition baselines `6b2a9965`, `79963b3b`); Layer 3 `3b4b92cf`.

Repository-path citations written in backticks inside these files are citations, not links: they resolve in this repository at
the source commit. Makers' datasheets under `v2/vendor/` are not copied. Some copied records quote part-price indications and
describe the programme's hosts; they are copied unchanged from the public `main` and add nothing new to it. One acceptance-supporting record is **not copied**: `v2/docs/reviews/REVIEW-A-LAYER-1-2026-09-27.md` (Review A of
Layer 1, an AI review) names the programme's hosts and is exempted from the repository's public-hygiene test only at its
own path; it stays in the repository at the source commit. Layer 1's release evidence (the targeted check and the second
release review) is copied.

## Copied files

| Section | Repository path | Source commit | Git blob | sha256 | Acceptance status |
|---|---|---|---|---|---|
| 01_Product_Definition | `v2/docs/PRODUCT-BRIEF.md` | `c20c4b629ff4` | `be567b85a654` | `85513b92ed0daf553b3225f325dc205bb9d6b8b3e08faf9e201d7f57ee9a0e4c` | Layer 1 accepted baseline (BASELINED at a9f212c7; definition baseline 6b2a9965); amendments A-1, A-2 |
| 01_Product_Definition | `v2/docs/handover/DEFINITION-STATUS.md` | `c20c4b629ff4` | `f90191976904` | `e8f9b415e39f855b3c7e52da903c7f7849018c69daf3ac0d2f30d55023e3cd19` | Layer 1 and 2 status page and glossary (supporting) |
| 01_Product_Definition | `v2/docs/handover/GLOSSARY.md` | `c20c4b629ff4` | `499882d5736e` | `6bb222ee7136eac764c04836cd09676f853582dff35f7c771fec9440d7bbb6bd` | Layer 1 and 2 status page and glossary (supporting) |
| 01_Product_Definition | `v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md` | `c20c4b629ff4` | `8e078991b1d4` | `ae70b1a7811ecea172029b55c070dfd86f7f668640109635362e785bf230b8aa` | acceptance evidence (AI review or AI check) |
| 01_Product_Definition | `v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md` | `c20c4b629ff4` | `843f67ad8b45` | `a0d8e6be2dcebcf68e800d666f85afe3c35f5395cd1ad20d2080297b0830f908` | acceptance evidence (AI review or AI check) |
| 01_Product_Definition | `v2/docs/reviews/DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md` | `c20c4b629ff4` | `fbe343cf44a3` | `4c09af64cb214448681a4424719bb88fe4e8bcca75a84821db088ea8cc164e33` | acceptance evidence (AI review or AI check) |
| 02_Concept_of_Operations | `v2/docs/CONOPS.md` | `c20c4b629ff4` | `4390ae0616c9` | `6cb7b241cb84d7290caffa74df2622c64222dd66a2de66693e480e3a18e44281` | Layer 2 accepted baseline (BASELINED at a9f212c7; definition baseline 79963b3b); amendments A-1, A-2 |
| 02_Concept_of_Operations | `v2/docs/OPERATING-ENVELOPE.md` | `c20c4b629ff4` | `ae93d9ad820c` | `26e98ecfd2e4ec2f29f374486a050df7bab2153bcf030eb373439e9e79f247ff` | Layer 2 supporting document cited by the baseline |
| 02_Concept_of_Operations | `v2/docs/TEST-PLAN.md` | `c20c4b629ff4` | `3cfb10e0dc23` | `42a3dff33442c86089a2c6c9dee841e8e2c8b9cbc1222a4adc311902b3c316f7` | Layer 2 supporting document cited by the baseline |
| 02_Concept_of_Operations | `v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md` | `c20c4b629ff4` | `f35a495e09cd` | `a4f0e88e48c304ee7e82b84fdbd23de7d12733872f98138669be3cec53081c67` | acceptance evidence (AI review or AI check) |
| 02_Concept_of_Operations | `v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27.md` | `c20c4b629ff4` | `c7408fc92b71` | `77b20ca4042f0855d9da1b9ede91028c28c66b9ebeedff3b79caf6b22801f5dd` | acceptance evidence (AI review or AI check) |
| 02_Concept_of_Operations | `v2/docs/reviews/DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md` | `c20c4b629ff4` | `fbe343cf44a3` | `4c09af64cb214448681a4424719bb88fe4e8bcca75a84821db088ea8cc164e33` | acceptance evidence (AI review or AI check) |
| 03_Requirements | `v2/docs/handover/layer3/REQUIREMENTS-L3-R2.md` | `c20c4b629ff4` | `5eb2f2f1eac4` | `a631fcb73a3618d30f0c18365c37ff916adfb6f077a4d890a05d69f6b18730fb` | Layer 3 rendered registry pages (re-rendered since acceptance; section 2.6 stale, I-03) |
| 03_Requirements | `v2/docs/handover/layer3/l3r2.yaml` | `c20c4b629ff4` | `e936a0db60e7` | `ee2efadf269994ce90830989714d3d48fecf0868b673e9f43e44b25b48fb091c` | Layer 3 registry, accepted baseline at 3b4b92cf (baseline_acceptance); amendments A-1, A-2 |
| 03_Requirements | `v2/docs/handover/layer3/OWNER-DECISIONS-L3.md` | `c20c4b629ff4` | `dc9f350aaf34` | `e4d6b6adc0b7bbea5e55de8daebc684df5e0f29263e7bdf6b37aea85be2cedba` | Layer 3 baseline record (accepted with the registry at 3b4b92cf) |
| 03_Requirements | `v2/docs/handover/layer3/L3-RECONCILIATION.md` | `c20c4b629ff4` | `615699269daf` | `db128fdc1216f87cbd4f5777400e9100a45a28c57cb0bc17238a05a1aa7a178e` | Layer 3 baseline record (accepted with the registry at 3b4b92cf) |
| 03_Requirements | `v2/docs/handover/layer3/DEFINITION-REISSUE-DRAFT.md` | `c20c4b629ff4` | `968880b58782` | `a04b0a6cc74006353f560e854929fbed9b9ab6944e4a010b0f462a88e1e3edbd` | Layer 3 baseline record (accepted with the registry at 3b4b92cf) |
| 03_Requirements | `v2/docs/handover/layer3/DEFINITION-CHANGE-RECORD-L3.md` | `c20c4b629ff4` | `6007c6145db9` | `681f37b665a57d03f1ffe6cf0a00aacabf2e6d620a6c4d5d02b34fee33761ccc` | Layer 3 baseline record (accepted with the registry at 3b4b92cf) |
| 03_Requirements | `v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md` | `c20c4b629ff4` | `3deeb2267ddd` | `f39c7f2b08dae370c68fa9e5ed189317722ff64c784423d246b3f17f1befee62` | Layer 3 baseline record (accepted with the registry at 3b4b92cf) |
| 03_Requirements | `v2/docs/REQUIREMENTS-TRACE.md` | `c20c4b629ff4` | `00308763baed` | `45ee58fa2d170d1cd1684117c424da69210f44980c21e94f3fe705b2010998ff` | Layer 3 trace (generated; rebinds since acceptance) |
| 03_Requirements | `v2/docs/handover/ENGINEERING-QUESTIONS.md` | `c20c4b629ff4` | `769c4af43fba` | `e315a9f2d5bba72d7d1d1b149e0dae91d58d39f2fee59a0c0f807aca0878556e` | open engineering questions register (supporting) |
| 03_Requirements | `v2/docs/handover/LAYER-STATUS.md` | `c20c4b629ff4` | `c55d6356b36f` | `df0221866b359598e088f2615b5535479c7b7d10b111c5c7c97816e954e5eed8` | status record of all layers (Layer 4 onward NOT accepted) |
| 03_Requirements | `v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md` | `c20c4b629ff4` | `0722a9fab760` | `7831358b96b6f5cae0141a3a80f6b4b1a2acb16671f06311ae91b626eb8fc186` | acceptance evidence (AI review or AI check) |
| 03_Requirements | `v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md` | `c20c4b629ff4` | `89a05fc19eff` | `7a6c679f446b1baad520cf8b26bad7e2d75f39eece148fffbec5df512ba4c72d` | acceptance evidence (AI review or AI check) |
| 03_Requirements | `v2/docs/records/l3am/checks/check-l3am-4.md` | `c20c4b629ff4` | `a3cf6785e979` | `d42a4879714f8cfff029c3e4791de87d3201dfa979eae768cf0b1d9591e7fe63` | acceptance evidence (AI review or AI check) |
| 03_Requirements | `v2/docs/records/l3am/REVIEW-UNIFIED-AS-RECEIVED.md` | `c20c4b629ff4` | `073d7f0496fc` | `1a8d728ad6fabf2d83118f3d25b4de17c12a03adca18b82e5373e518a10acab1` | acceptance evidence (AI review or AI check) |
| 03_Requirements | `v2/docs/handover/OWNER-INSTRUCTION-2026-10-09-AS-RECEIVED.md` | `a6274bf77f2c` | `000409431842` | `6057df88d356796de9c02517d6ad0a82a72d1af283ef668fd8db6c2ac5fc0466` | owner rulings filed as received; Part 6 = amendment A-1 (source: unpromoted candidate) |
| 03_Requirements | `v2/docs/records/l3batt/runtime.out` | `c20c4b629ff4` | `63d40810daf4` | `87d9c1ee590597638c57aa97c384c217af9eb36044a2db39e27194a88047fc13` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3r2/checks/energy-basis-check-1/CHECK-1.md` | `c20c4b629ff4` | `33abd2ee41fb` | `845858d6c3059f770ad0b8721693c177a5d018f9ab0af9280024ed885f690d57` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3r2/checks/energy-basis-check-2/CHECK-2.md` | `c20c4b629ff4` | `cceaf1bad62f` | `f5db20597e22b3ba0621879f8ac9ee6fdf601cb28c3cf7924950d37de5343220` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3r2/checks/energy-basis-check-3/CHECK-3.md` | `c20c4b629ff4` | `dae0e71c3a57` | `7c81f4fed407097a0dbe7cd2d2bf893e072199738d361e7e79374e1e6b9f8a87` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3r2/checks/energy-basis-check-4/CHECK-4.md` | `c20c4b629ff4` | `d57a5f47f768` | `6e98b2e19cb1d89bc4ab9faa195f7e634592037ca10337fd0de6b248ec5f9b05` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3r2/checks/energy-basis-check-5/CHECK-5.md` | `c20c4b629ff4` | `3d6576b0ed33` | `bf3aace0457d19ee007c990f94cfcdaf296a503d174837fb5ab5ecdb3e3fbbcb` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3plane/ENERGY-BASIS.md` | `c20c4b629ff4` | `1f56b7b84f0a` | `7bbca138a02bd32facc2a277283218c6bccc2f257c787b374fbf42483d90d132` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3plane/vbus20_range.out` | `c20c4b629ff4` | `f820a3a86d3d` | `2ce0b0f41b074ea6e132d57ae6a92bd20954f792c7539b7f50ef3a410953f049` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/r11dep/R11-DEPENDENCY.md` | `c20c4b629ff4` | `1f8eae3d5931` | `50171547951aa9a45df1fd95fc45665919a2cee5e2f315c10dd2838f62343427` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/r11dep/r11_dep.out` | `c20c4b629ff4` | `3fb4c23e3106` | `f9d2c6f23fab3edcb48ad0116366fe588a514f755aafe56ebd62a0fe9495a209` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3plane/three_cases.out` | `c20c4b629ff4` | `7de31fae059a` | `8119987a20fad08cae0edc928726c847b1f5ec41f81cfd9552849793567e96be` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3plane/weather_basis.out` | `c20c4b629ff4` | `6616eac24c3e` | `8cc676433f4e3fb84240ddcdd55ae818e7d8b64a3a7ef8e710e7afd5c4e59961` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/a1mech/README.md` | `c20c4b629ff4` | `566aaef639f6` | `22ed96b7f7bbe160f9359a8edfa68e793e60f46d3cc3dfc9fea50e9c82752121` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/a1mech/DECISION-A1.md` | `c20c4b629ff4` | `f4e6d0c63be4` | `3dc2e2d934dc46a69a38a525c43538b420d8c385d6accba3d2414d2fbb103aa1` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3batt/COMPARISON.md` | `c20c4b629ff4` | `b27170bd2e28` | `e84f3a45f57355cf1695c6ad8d286c8ae307e8509e6c007743ab2b9171874d8c` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/energy/ENERGY-RECONCILIATION.md` | `c20c4b629ff4` | `57f89c63675e` | `dfc85ef1c0ac9e789b9f1f4e90e0147bb891997dfcb82295de72bfc3d0062443` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3plane/energy_basis.out` | `c20c4b629ff4` | `389fb350260a` | `73fd16915ddf8edf217090a4c221f879d34b5c50c4f6ddc8ff950adb6b3b2633` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3feas/L3-FEASIBILITY.md` | `c20c4b629ff4` | `80260f55de5a` | `d6c15694322dfbe315db7a0efdbf131e08fe28ea76445b6d887e0b85409f1f8b` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/a1solar/ARRAY.md` | `c20c4b629ff4` | `812876220121` | `c4938e4a7598aedc0060d20a4b4ec02f9b3e93cf26fe7c0c0bf12bd1c4f65320` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3batt/SHORTLIST.md` | `c20c4b629ff4` | `6feda6ca1501` | `6a943a1fb0d47edf1977e39b0c1801f9319abdb8087015ccbea3a1c4a784e28c` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3batt/PROVENANCE.md` | `c20c4b629ff4` | `84685e780f6f` | `9b92e4213445652a3a1d5d693b727338b5e88f7e943536047b20814d45820695` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/a1elec/TOPOLOGY.md` | `c20c4b629ff4` | `c2ec6594588c` | `a4d7f26dddb39bbdcb67c1b177f58be1b5d1cbe76874e8cf6abb13bb7100ec31` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/energy/DECISION-OPTIONS.md` | `c20c4b629ff4` | `d35bfae17e2e` | `cfd949fd7136ca4d9adc8c1e610dda8eee896a02d0d310723f8ff6ef9114ae1a` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/review-packets/battery/THERMAL-COORDINATION.md` | `c20c4b629ff4` | `f822ccaee8fe` | `0d4d60f03260f004cd7af9d738e41bbdb5f5a1d4818fa33775328d0d264d41ec` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/feasibility/POWER-THERMAL.md` | `c20c4b629ff4` | `7fc86270a989` | `ad3ba27cef9e0f684f28ce81815afa86d44c4114b9bc10ff474308d875ba5788` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3r5/checks/l3feas-check-1/CHECK-1.md` | `c20c4b629ff4` | `d3910930e41e` | `f1c5f8c5e97940fef458715fd989834b0eeecc8e9d362a809e8e4cd232a08dc5` | record linked from the requirement pages (supporting; not itself a requirement) |
| 03_Requirements | `v2/docs/records/l3r5/checks/l3feas-check-2/CHECK-2.md` | `c20c4b629ff4` | `6803fb723571` | `5992b91e3c4278f62107f54ec0f3e39fccc437b48be35299299575df28b9b105` | record linked from the requirement pages (supporting; not itself a requirement) |

## Written for this handover (provenance: this preparation, not in any earlier commit)

| File | Purpose |
|---|---|
| `00_START_HERE.md` | introduction, statuses, reading order, takeover scope |
| `03_Requirements/APPROVED-AMENDMENTS.md` | the approved amendments A-1 (second battery) and A-2 (definition re-issue) with their exact scope and status |
| `04_Review_and_Open_Issues.md` | this handover's final review and the material issues |
| `05_Engineer_Takeover.md` | next steps and the Layer 4 working material with exact revisions |
| `06_Source_Manifest.md` | this manifest |
| `CHECKSUMS.sha256` | sha256 of every supplied file except itself (`sha256sum -c CHECKSUMS.sha256` from inside the folder) |

Full Git SHAs of the Layer 4 working branches named in `05_Engineer_Takeover.md` are listed there.
