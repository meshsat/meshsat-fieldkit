#!/usr/bin/env python3
"""l4e11_power.py: layer 4 task L4-E11 (MESHSAT-1357, 2 October 2026). Three items the connected power architecture (L4-E9)
left open, resolved as engineering choices with their bounds:

  U-04  source-only and dead-pack operation (the kit on a vehicle or shore source with the pack absent, at or below its
        protection cutoff, or with its FETs open);
  D-06  the vehicle-entry interconnect in F1's long-time band from a weak source;
  D-09  the hot swap's fault time against its own start into VIN_RAW (added by the coordinator on 2 October 2026).

The fix round (2 October 2026) answers the collaborator's focused check (checks/astra-check-l4e11-1.md): the LM5069's UVLO by
SNVS452G Equations 38 to 40 and its POREN at the IC from a 9.00 V plug, so the entry is replaced (B1); the charge holds as a
state table of charge and discharge permission (B2); the source envelope with the kit's own losses and a functional warm-up
(B3); the weak-source envelope as monotone intervals and the interconnect specified by its resistance (B4); R-b's register
value and its actual-current bound (B5).

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured. No generator, registry, interface or
Layer 3 file is edited here; the circuit changes are the release-guarded drafts beside this file. Every printed figure
carries its class: MAKER (a maker's row, page named), CATALOGUE (a filed distributor reading), NETLIST (the committed
netlists or generators), REQUIREMENT (the registry's text), RECORD (another record's committed output, its own class
kept where it states one), INFERRED (method stated), CONDITIONAL (a calculated result on an unwarranted assumption or an
open measurement), ASSUMPTION (a figure no document gives), SESSION (a choice this record takes, with its reason).

Inputs are pinned by sha256 (PINS); L4-E9's output and hot-swap draft are read from its commit (GIT_PINS), never retyped.
Run from the repository root:  python3 v2/docs/records/l4e11/l4e11_power.py > v2/docs/records/l4e11/l4e11_power.out
Needs pdftotext and pdftocairo (poppler), PyYAML, git, and the held documents (fetch_held_back.py beside this file).
The consolidation round (2 October 2026, the owner's instructions of 11:25 and 12:00) evaluates TI's BQ25730 against board A's
circuit (its pins, the settings L4-E4 to L4-E8 drafted, startup and protection in each mode, the affected budgets with the battery
FET it adds), compares it with the drawn arrangement and with any other implementation a maker's sheet supports, selects one and
classifies U-04 (sections 12 to 14). The fix round (2 October 2026) answers the consolidation review cx36 (set 27, NOT YET): board
E's auxiliary domain moved to a VSYS feed over the dock (B1), the start bounded by the input clamp, the retries and a bench
acceptance, and the battery FET re-selected on its maker's printed maxima at BATDRV's least drive, a pair of Nexperia BUK6Y10-30P
(B2), with the charger minors (section 15).
Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a predicate this record rests on failed."""
import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REC = "v2/docs/records/l4e11"

PINS = {
    "reqs": ("v2/ecad/tools/pcb_requirements.yaml", "c8956b14b0e78aa43c47ddb835514a4cb92ec16f334f9b3ef8bbef76986b394c"),
    "rules": ("v2/ecad/tools/pcb_rules.yaml", "14ea032a7fdd86ac877a51ec7bdc804d95c1c639ddbca4035338da5a09d8b83f"),
    "testplan": ("v2/docs/TEST-PLAN.md", "42a3dff33442c86089a2c6c9dee841e8e2c8b9cbc1222a4adc311902b3c316f7"),
    "hwfw": ("v2/docs/HW-FW-CONTRACT.md", "12b6ea059a68b5c5f0eb4d67513283af2bd8a011f9e80bea7d047e5955b1e99a"),
    "panel": ("v2/docs/PANEL.md", "c4820a453aa7a159ee2641bd921e39023737c3eefe8dcbe7bfca3bd36420b90d"),
    "assembly": ("v2/docs/ASSEMBLY.md", "29dbe3a0c4938274b3fe780d27c565737adf9dd506b8c8c81e72f3776ef75fed"),
    "gen_a": ("v2/ecad/tools/gen_sch_a.py", "6a136feec6c9cf4e2011ed8c45a1f2e0adc3e263718c355b4b909872ee5d3c4b"),
    "gen_e": ("v2/ecad/tools/gen_sch_e.py", "f846e138cb53a8c63247efb3ad7b5cc44a68cb73e71699c65fd53b63c01af186"),
    "gen_p": ("v2/ecad/tools/gen_sch_p.py", "740817ada5c8e14af8c8e001b775e09cbae94d6a03ad462ee2e1c1755bc935a3"),
    "net_a": ("v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "6c40250c47195ebb7b2ae1388e284dc7f2fba9f2e683f654a47c98444290e8c5"),
    # round 17 (the check V6's V6-m2): record l8p's thermal guard, drafted in its round 8 and judged in its rounds 8 and 9
    "l8p_c4": ("v2/docs/records/l8p/l8p_c4.out", "5cc3eedafd987a7474d3be1f9646ffec0928d6dd6e7a9693bf5d97143f1ade89"),
    "l8p_thgfs": ("v2/docs/records/l8p/apply_gen_sch_a_thgfs.py", "19af759a934be6cc07390a43873ce1d1d6ef754a58dcac202c89063974e0d23c"),
    "l8p_thguard": ("v2/docs/records/l8p/apply_gen_sch_a_thguard.py", "544a462a9031862a953748a631023f59491203198aa4810321baed121606ecab"),
    "net_e": ("v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net", "2ed95a0e8069ebf8ad31f4567a14015e863182a83b6de7b3b13218488d8316d4"),
    "packprot": ("v2/ecad/tools/pcb_pack_protection.yaml", "ab1dbc3f3f69aa4687a4fa9745c0cbdc96d0521146dc5d3f84698656e33c484b"),
    "primcfg": ("v2/docs/review-packets/battery/PRIMARY-CONFIGURATION.md", "6726f23778f48e1017d29fffe923c4b07b9e196d4636e3e90432774d9f922aac"),
    "chain": ("v2/ecad/tools/pcb_energy_chain.yaml", "a09ca0293afd1f7c553cbffb5b95bc33ae58688a4c20b8de65ec47c15d45996c"),
    "l4e5": ("v2/docs/records/l4e5/l4e5_source_control.out", "f9c98ec5c43ada0e1a5a033a794c98b45f110ffcb0a67ff8c81a31fede134e71"),
    "budget": ("v2/docs/records/rv-pwr/pwr_budget.out", "58e40cf604804cc9d70c7fbeb1012be4552563fcc8ae7ef6755003c33acb902f"),
    "red2": ("v2/docs/records/hc2/pwr_red2.out", "835910e807d588c481951dc879e030b55d893453bd124872b9310a99bed46db6"),
    "ecss": ("v2/vendor/standards/ecss-q-st-30-11c-rev2-2021-06-23.md", "576256819950c4432b48769e5f642ee5bfb0eed4f025c03fb9727de7dbeabeea"),
    "bq25731": ("v2/vendor/ti/bq25731-datasheet.pdf", "3e5e927fdf63cf6a2397630987c58e947ebc80d5a1cfc93fb1fb58d98bb58973"),
    "sluuaq3a": ("v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf", "525d16b2bdee44e5b587ccf6800b9967bc524772d0b5a20937957ea2e738b7ad"),
    "csd17570": ("v2/vendor/battery/ti-csd17570q5b.pdf", "596555c33dce1fcac6de3b6ecc3eeb443f202382b3e2091fd6e1c27d129f2436"),
    "cell": ("v2/vendor/battery/samsung-35e-orbtronic.pdf", "5ec577b952b9dc5106593a4e4c3a6e8cea64f6f72b8faaf1bb512155c29dc516"),
    "lm5069": ("v2/vendor/ti/ti-lm5069.pdf", "d60d8106a6e8113900ff8b9576dd959942fa7169742baf0beeb30684d4d64681"),
    "csd19532": ("v2/vendor/power/ti-csd19532q5b-n-fet.pdf", "353ce937cff0b719e730010829720d25c2ece3637ed92fb7ad8cc370438559d1"),
    "d38999": ("v2/vendor/d38999/amphenol-d38999-iii-federal.pdf", "13a19268ba5939d9e4df5a20f9db84bb72e86525b82f0586c85696e42c126a2b"),
    "vh": ("v2/vendor/connectors/jst-vh-catalogue.pdf", "d51e669c597988b20c0963daf5bef7356cbd2104c1f867e9107c6fa6cd2b899c"),
    "xt60": ("v2/vendor/battery/amass-xt60-spec-tme.pdf", "c2cbb5962c1f37da89e76e505c75184dd07e84eec3a6fe5f24569dafc6f6b9e9"),
    "keystone": ("v2/vendor/keystone/M65p42.pdf", "caa141ea51ac68cf80ab6e14ad2075fcfc76206451f4bfe45330005c0deaf395"),
    "lapp": ("v2/vendor/d38999/cables/lapp-olflex-robust-210-product-information.pdf", "535cc7900e32bed34ea2dcb277708650bb90e06eb39f41d7dfb4ced4660ec2ba"),
    "alpha": ("v2/vendor/d38999/cables/alpha-25064-spec.pdf", "232d6661444a7e3a75819a61d57df4a83735353c4c8ea3ac204450a59e77d300"),
    "lm5176": ("v2/vendor/ti/lm5176-datasheet.pdf", "98191bec36d43771affa3e1540f6e1737347c19a1602747ffb4327509550a820"),
    "bq25798": ("v2/vendor/power/bq25798.pdf", "631d541679512116b5cf7ade0516000e78bc95f060b8b958e726c1b6eb74c27f"),
    "srf1260": ("v2/vendor/power/bourns-srf1260-common-mode-choke.pdf", "93b2dc7565d07e727adb658843b52ec227a2c05f1ee21e117d7057d03ba1aea6"),
    "yageo": ("v2/vendor/passives/yageo-cc-series.pdf", "61a606825ab314ea318cfb5362848a62fdffb851efa9818d642e9a541c56a648"),
    "fuse997": ("v2/vendor/power/held/littelfuse-997-mini58v-rev2025-11-18.pdf", "437b1fd2c8cb3ef16107ec14d096b31ef3c3cb83893325234e880deb7540393e"),
    "mur104": ("v2/vendor/passives/held/murata-grm3195c1h104ga05-01a-2026-06-11.pdf", "4457e5ec41c25d29a47f9201bd903f0f4abf98c7566d84a81aae7028e2d7a188"),
    "mur683": ("v2/vendor/passives/held/murata-grm3195c1h683ja05-01a-2026-06-11.pdf", "89cfedda1a8d61d5cf5371ab274a8c033e2bd9157d959ddd27d4e8963a934fde"),
    "lm74700": ("v2/vendor/ti/ti-lm74700-q1.pdf", "e16b3a8c0023201fafa5825436f5f2dd6f885b92b84e65602b3f50d741c58b6f"),
    "tps4811": ("v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf", "3cfe41fef1407b85abaaee1e27a95ac3cf2cb1bdf218209b8578a835c4c9497f"),
    "csd19536": ("v2/vendor/ti/held/ti-csd19536ktt-slps540c.pdf", "19e1a9660fac8577743f40acc2cdc791539afd5232bbc1fc350e15fec735d78d"),
    "tps1663": ("v2/vendor/ti/held/ti-tps1663-slvset9g.pdf", "8f91a0db2daf2da35abd335420ff9f8b4ac9a99c93dac93e215e0a75e9a866fe"),
    "red2_py": ("v2/docs/records/hc2/pwr_red2.py", "5790bc7e444bebc4b6b7b6616c4641dfe602185631992d19aeb223eb51e9feec"),
    "budget_py": ("v2/docs/records/rv-pwr/pwr_budget.py", "469d0820b046ef6ff5aceadf422b4166de3d6a02bc50fa5b0c3644704f0f9556"),
    "loopdesign": ("v2/docs/records/l4e8/inputs/recovered/loop_design-r4a-fixup-A-1024.py", "fe0d946bc020d4b68c3a4e417b4c2e7dfd98eeabd2352ff849de4ef0d781d7da"),
    "zk": ("v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf", "5455014606c0b676ca1df345f1969ee1b056403b8ee424bb29245115facda389"),
    "b540c": ("v2/vendor/power/held/diodes-b520c-b560c-ds13012-rev18-2.pdf", "1b1de94df0a7729f4a69a885edd54213594acdce3cd6d4fa072961431ddf71ff"),
    "yageo_rc": ("v2/vendor/passives/yageo-rc-l-series-v12.pdf", "e7dbabb0611925227ccfc429c14c8833a7b1f2c755684444124446f20b22a229"),
    "e2e_por": ("v2/vendor/ti/ti-e2e-1316778-bq25731-chargecurrent-por.html", "96c511cf238d00182bcd82c5e7bdce3d25571c49cbd77f6b57a9171159f0d8c4"),
    "bq25730": ("v2/vendor/ti/held/ti-bq25730-sluse65a.pdf", "e41ef289ce1de377d7b92bce609177d924e149099d9c4424d88f6b21ad57153f"),
    "aons21357": ("v2/vendor/power/held/aos-aons21357-rev2.1-2023-11.pdf", "1a6460e7c63596ca7d48fe1660ee3a3ee48c33d6e345ef41d7c94c21cd7642d9"),
    "bq4050": ("v2/vendor/battery/ti-bq4050.pdf", "2664e33fe6d6ebed3a0f58153d8ba8ce66cb84f07741f6708ae11a224f443f5e"),
    "bq25792": ("v2/vendor/power/bq25792.pdf", "cc451e71123d24d4580bf867fcda0f000b5cf343622b5101f693137ac7be0c15"),
    "sqj403": ("v2/vendor/power/held/vishay-sqj403ep-67109-reva.pdf", "6005efe139fc94e3e855c2beeef8fcaaa5dc71d3c4a6e82f8e8ce82c5506961c"),
    "buk6y10": ("v2/vendor/nexperia/held/nexperia-buk6y10-30p-2020-04-17.pdf", "ba928dfe6a85134423562bd378bdfafafb26d857ba08b50560ce5aacb956da40"),
    "ap63200": ("v2/vendor/diodes/diodes-ap63200-series-buck.pdf", "ef99daa3789d835bc025dfcb4c605c5c2e6d3e7223e86d40b33e6b497ea5a722"),
    "smcj": ("v2/vendor/power/littelfuse-smcj-series-tvs.pdf", "6e610db955ed876306999009c62b242f7de9bb05e2cd9717288a96586a5093ea"),
    "dock_py": ("v2/docs/records/w3de/dock_contacts.py", "acd932cbb9e31f8f0fd4563fc97d7ece21e0ce531e133040afb911da3c513b41"),
    "msmf": ("v2/vendor/power/bourns-mf-msmf-pptc.pdf", "a84b990157dd1d755b5c7a413156ddf8792a3a95cff56f09a95d10754e9e49ed"),
    "ltc3115": ("v2/vendor/power/held/adi-ltc3115-1-rev-e.pdf", "bbcd4991d9b86c100cf8da775a358740b3c524325d18251d56ec6e40a2014a03"),
    "tps55340": ("v2/vendor/ti/held/ti-tps55340-slvsbd4e.pdf", "e579aa4fcb549eab29e889f7f6dcbd0fd88cac2647082c65f102e411c3f666ca"),
    "tps63070": ("v2/vendor/ti/held/ti-tps63070-slvsc58b.pdf", "a88ef66f3493156ff6e7da0849de0e0e1068647f2553d08c1844d4a90c5c65ef"),
    "xal60": ("v2/vendor/coilcraft/coilcraft-xal60xx-series.pdf", "236888dabe560055e7eb40e24b8bf938db132b66a0e9f1a3c512fb3b04361681"),
    "spra953": ("v2/vendor/ti/held/ti-spra953c-thermal-metrics.pdf", "8ab81b5a351132ae8ab049d984e7cc72f1eb3dd3e4d9d8e063be6fcd841080a9"),
    "an11158": ("v2/vendor/nexperia/held/nexperia-an11158-rev7.pdf", "9e3211549d0bcd774b265d0598588b3b221b13b9c528b7374445fd0f21d47aec"),
    "gen_b": ("v2/ecad/tools/gen_sch_b.py", "3698cc04d8eaf75ba2104e6a246352ec12a092e107eee8ee554321fa95040cb8"),
    "arch": ("v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md", "8890e94fdb94ffef0e7eeb7c840039a0ec055a27f82938c296d0ed9d2c6f28bc"),
    # round 9 (4 October 2026, section 19): R19's maker sheet (held back), the VSYS hold's parts, RAIL_EN's controller and buck
    "hollr2512": ("v2/vendor/passives/held/moolee-hollr2512-ho-a0-2022-01-06.pdf", "5dac9ede82062791abe6128aa7cad87c1422993820fbd21efa33dbea2ce04005"),
    "tps37": ("v2/vendor/ti/ti-tps37-snvsbj1e.pdf", "d6aed9d98fbf7f16f4dea2d6edf7c889e5fd3fa862f4072da656fb3fe7cef545"),
    "ltc2954": ("v2/vendor/power/ltc2954.pdf", "1e9e2567d15e569ecc95023a40e4fb99eb0288db842803ff78cd14fdd621d8ae"),
    "tps62933": ("v2/vendor/ti/ti-tps62933.pdf", "16ec2eac43c7374eb9e7edd7df7bdb24de6862f695e1582c68716ced4820e5f6"),
    "n2n7002": ("v2/vendor/power/jscj-2n7002-c8545.pdf", "7941fb423af7c6c6c8979063a7e8819bb19217ece275efcce18948950a41d9f6"),
    "bzt52c": ("v2/vendor/diodes/diodes-bzt52c-ds18004.pdf", "0fbd7d137524820f0160594065cbceb8c6b3188757c328416d08fceb7418202f"),
    "tps2596": ("v2/vendor/power/tps2596.pdf", "66f6bae4494f7bfe7dfdc314e508f0291d9ca1e87265cca9b6fdfeaa5cb19fe9"),
    "ap64500": ("v2/vendor/diodes/diodes-ap64500.pdf", "d3bcdc7dd4ca44cb36ef893d3dbfabbd1742dfc736557777868f6ead5d0a98e8"),
    # round 10 (4 October 2026, section 20): the arm's P-FET and diode
    "ao3401": ("v2/vendor/power/aos-ao3401a-p-mosfet.pdf", "0d8e3261ae280e007b5837fff60c55142f2d92af71edc4d02aee6f7a760a785c"),
    "n4148w": ("v2/vendor/power/st-semtech-1n4148w-c81598.pdf", "54de8e4089bb8221cf6cf191ee3acc2bdb20c9933cf59e7b5de3ef4ee291ce3f"),
}
# W34 (Q-41 item 1, adopted in set 32): the makers' PDFs this script reads as text, each with its pdftotext options ([] is pdftotext's
# plain reading order). Each text is a verbatim input taken once on the runner by v2/docs/records/_lib/retake_pdf_text.py beside its
# PDF (a held-back sheet's text is held back with it, under held/); _lib/pdftext.py returns it byte for byte and refuses when it is
# absent, so this script never runs pdftotext; section 0 prints each text's sha256 after the PDFs' own pins, which stay.
# Re-take after a sheet changes: python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l4e11
PDFTEXT = {
    "v2/vendor/battery/amass-xt60-spec-tme.pdf": [["-layout"]],
    "v2/vendor/battery/samsung-35e-orbtronic.pdf": [["-layout"]],
    "v2/vendor/battery/ti-bq4050.pdf": [["-layout"]],
    "v2/vendor/battery/ti-csd17570q5b.pdf": [["-layout"]],
    "v2/vendor/battery/ti-csd18510q5b.pdf": [["-layout"]],
    "v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf": [[]],
    "v2/vendor/coilcraft/coilcraft-xal60xx-series.pdf": [["-layout"]],
    "v2/vendor/connectors/jst-vh-catalogue.pdf": [["-layout"]],
    "v2/vendor/d38999/amphenol-d38999-iii-federal.pdf": [[], ["-layout"]],
    "v2/vendor/d38999/cables/alpha-25064-spec.pdf": [["-layout"]],
    "v2/vendor/d38999/cables/lapp-olflex-robust-210-product-information.pdf": [["-layout"]],
    "v2/vendor/diodes/diodes-ap63200-series-buck.pdf": [[]],
    "v2/vendor/diodes/diodes-ap64500.pdf": [["-layout"]],
    "v2/vendor/diodes/diodes-bzt52c-ds18004.pdf": [["-layout"]],
    "v2/vendor/keystone/M65p42.pdf": [[]],
    "v2/vendor/nexperia/held/nexperia-an11158-rev7.pdf": [["-layout"]],
    "v2/vendor/nexperia/held/nexperia-buk6y10-30p-2020-04-17.pdf": [[], ["-layout"]],
    "v2/vendor/nexperia/held/nexperia-pxp9r1-30ql.pdf": [[], ["-layout"]],
    "v2/vendor/passives/held/moolee-hollr2512-ho-a0-2022-01-06.pdf": [[]],
    "v2/vendor/passives/held/murata-grm3195c1h104ga05-01a-2026-06-11.pdf": [["-layout"]],
    "v2/vendor/passives/held/murata-grm3195c1h683ja05-01a-2026-06-11.pdf": [["-layout"]],
    "v2/vendor/passives/yageo-cc-series.pdf": [["-layout"]],
    "v2/vendor/passives/yageo-rc-l-series-v12.pdf": [["-layout"]],
    "v2/vendor/power/aos-ao3401a-p-mosfet.pdf": [["-layout"]],
    "v2/vendor/power/bourns-mf-msmf-pptc.pdf": [["-layout"]],
    "v2/vendor/power/bourns-srf1260-common-mode-choke.pdf": [[], ["-layout"]],
    "v2/vendor/power/bq25792.pdf": [["-layout"]],
    "v2/vendor/power/bq25798.pdf": [[], ["-layout"]],
    "v2/vendor/power/held/adi-ltc3115-1-rev-e.pdf": [["-layout"]],
    "v2/vendor/power/held/aos-aons21357-rev2.1-2023-11.pdf": [[], ["-layout"]],
    "v2/vendor/power/held/diodes-b520c-b560c-ds13012-rev18-2.pdf": [["-layout"]],
    "v2/vendor/power/held/littelfuse-997-mini58v-rev2025-11-18.pdf": [["-layout"]],
    "v2/vendor/power/held/vishay-sqj403ep-67109-reva.pdf": [["-layout"]],
    "v2/vendor/power/held/vishay-sqj407ep-62806-revb.pdf": [["-layout"]],
    "v2/vendor/power/jscj-2n7002-c8545.pdf": [[], ["-layout"]],
    "v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf": [["-layout"]],
    "v2/vendor/power/littelfuse-smcj-series-tvs.pdf": [["-layout"]],
    "v2/vendor/power/ltc2954.pdf": [[], ["-layout"]],
    "v2/vendor/power/st-semtech-1n4148w-c81598.pdf": [["-layout"]],
    "v2/vendor/power/ti-csd19532q5b-n-fet.pdf": [["-layout"]],
    "v2/vendor/power/tps2596.pdf": [["-layout"]],
    "v2/vendor/ti/bq25731-datasheet.pdf": [[], ["-layout"]],
    "v2/vendor/ti/held/ti-bq25730-sluse65a.pdf": [[], ["-layout"]],
    "v2/vendor/ti/held/ti-csd19536ktt-slps540c.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-spra953c-thermal-metrics.pdf": [[], ["-layout"]],
    "v2/vendor/ti/held/ti-tps1663-slvset9g.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tps55340-slvsbd4e.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tps63070-slvsc58b.pdf": [["-layout"]],
    "v2/vendor/ti/lm5176-datasheet.pdf": [["-layout"]],
    "v2/vendor/ti/ti-lm5069.pdf": [[], ["-layout"]],
    "v2/vendor/ti/ti-lm74700-q1.pdf": [[], ["-layout"]],
    "v2/vendor/ti/ti-tps37-snvsbj1e.pdf": [[], ["-layout"]],
    "v2/vendor/ti/ti-tps62933.pdf": [["-layout"]],
}
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(TOP, "v2", "docs", "records", "_lib", "pdftext.py"))
PT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PT)
INPUTS = ["lcsc-C907944-2026-10-02.json", "lcsc-C3847777-2026-10-02.json", "lcsc-C363929-2026-10-02.json",
          "lcsc-C3873338-2026-10-02.json", "jlc-search-c0g-150nf-2026-10-02.json", "murata-reference-sheets-2026-10-02.json",
          "ia-littelfuse-997-mini58v-20251210045250.json",
          "lcsc-C17556513-2026-10-02.json", "lcsc-C2687963-2026-10-02.json", "lcsc-C2985708-2026-10-02.json", "lcsc-C7084461-2026-10-02.json",
          "lcsc-C861872-2026-10-02.json", "lcsc-C97929-2026-10-02.json", "lcsc-C184799-2026-10-02.json", "lcsc-C23107-2026-10-02.json",
          "lcsc-C242138-2026-10-02.json", "lcsc-C242139-2026-10-02.json", "lcsc-C72264-2026-10-02.json", "lcsc-C137025-2026-10-02.json"]
CONS_INPUTS = ["lcsc-C5219071-2026-10-02.json", "lcsc-C2871872-2026-10-02.json", "lcsc-C404364-2026-10-02.json",
               "lcsc-C242138-price-2026-10-02.json", "lcsc-C242139-price-2026-10-02.json", "lcsc-C72264-price-2026-10-02.json",
               "lcsc-C137025-price-2026-10-02.json"]          # the consolidation round's catalogue readings (with prices)
FIX_INPUTS = ["lcsc-C3278350-2026-10-02.json", "lcsc-C3289491-2026-10-02.json"]   # the fix round's FET candidates (with prices)
R9_INPUTS = ["lcsc-C98734-2026-10-04.json", "jlc-search-xt60f-2026-10-04.json"]   # round 9: J_DCIN's XT60-F (catalogue readings)
INPUTS = INPUTS + CONS_INPUTS + FIX_INPUTS + ["nexperia-buk6y10-30p-figure-readings-2026-10-02.json"] + R9_INPUTS
L4E9_COMMIT = "3c09b3daaa48d0a9f16b833b949d7d9ab8ecd496"
GIT_PINS = {
    "l4e9": ("v2/docs/records/l4e9/l4e9_power_path.out", "07d8fb6e828cb15b5589f13983a76bde97c9048ab46ea193c528a28d59a7bbd3"),
    "l4e9_hotswap": ("v2/docs/records/l4e9/apply_gen_sch_e_hotswap.py", "ed228968916764468fada2e8317a908216d5a1e835d81bccb156952ab8397cbb"),
}

# ---- the figures this record sets itself (each named where it is used)
CU_RHO_20 = 0.01724          # ohm mm2 / m, annealed copper at 20 C (ASSUMPTION, a constant, as L4-E9)
CU_ALPHA = 0.00393           # 1/K (ASSUMPTION, a constant, as L4-E9)
CU_CV = 3.45                 # J / (cm3 K), copper's volumetric heat capacity (ASSUMPTION, a constant)
T_COLD = -20.0               # C, REQ-024's cold end, as L4-E9 takes it
AWG14_MM2, AWG12_MM2, AWG16_MM2, AWG18_MM2 = 2.081, 3.309, 1.309, 0.823   # nominal AWG cross-sections (ASSUMPTION, constants)
LEAD_M = 0.5                 # the inside lead, a way (L4-E9's 500 mm, read below for the drawn lead's gauge)
SEL_CABLE_M = 3.05           # SESSION (D-06, final round): the DC pair's run, a construction inside the measured window below
SEL_MM2 = AWG14_MM2          # SESSION (D-06): the class of core that fits a MIL-DTL-38999 size 12 crimp barrel
CONT_CLASS_A = 20.0          # SESSION (D-06): every element of the vehicle entry's interconnect rated at least this, continuous
PLUG_V = 9.0                 # REQ-015's floor, taken at the kit's plug (SESSION, the most demanding reading)
RULE_SRN_V = 14.0            # SESSION (U-04 rule R-b): the charger's own SRN reading under which R-b holds without the gauge's report
STEP_N = 40000               # the start integration's voltage steps (deterministic)
CAP_STACK_PARTS = 2          # SESSION (D-09): a timer capacitor of at most two parts in parallel
# ---- the fix round's own figures (2 October 2026, the focused check cx30's B1 to B5)
T_OUT_HOT = 40.0             # C, REQ-024's +40 C ambient for the outside cable (REQUIREMENT; sun loading not counted, named)
I_PF_TARGET = 900.0          # A, SESSION (D-06, final round): the specified worst stiff-source current, 10 % under F1's 1000 A
U_MEAS = 0.02                # SESSION (D-06): the loop measurement's instrument and fixture uncertainty, of reading
DT_MEAS = 2.0                # K, SESSION (D-06): the conductor temperature's uncertainty when the loop is measured
LOOP_CEIL20 = 0.066          # ohm, SESSION (D-06): the measured loop's actual ceiling at 20 C (copper, the D38999 pair, J_DCIN)
T_RESP = 1.0e-3             # s, ASSUMPTION (dependency round): the time the charger could take to restore VSYS after a step, no battery
K_COLD_HYB = 0.90            # ASSUMPTION: a hybrid polymer can's capacitance at -20 C over its 20 C value (the ZK sheet prints none)
VF_COLD_ADD = 0.10           # V, ASSUMPTION: a Schottky's forward drop at -20 C over its 25 C maximum
BANK_N = 4                   # SESSION (dependency round): the hold-up bank's cans (EEHZK1E471P)
R_CH = 330.0                 # ohm, SESSION: the hold-up bank's charge resistor (RC2512 1 W)
S2_ETA = 0.90                # ASSUMPTION: the slot rail's efficiency (gen_sch_a.py declares 0.90 for +5V_DEV and none for +5V_S2)
SHED_OFF = ("two mixer fans", "QMX USB and HDMI 5 V", "Geiger module", "5G RM520N-GL")   # SESSION (B3): held in the warm-up
HOLDER_R = 0.0010            # ohm, F1's holder (two clips): the 3568 prints nothing (ASSUMPTION)
BOARD_R = 0.0050             # ohm, board E's and board A's copper and the dock's VIN_RAW pins in the loop (ASSUMPTION)
FET_HOT = 1.8                # a MOSFET's RDS(on) at the hot end over its 25 C maximum (ASSUMPTION, for TJ up to about 125 C)
FIX_KNEE_IT, FIX_RLOOP = 1.89, 0.141525   # the fix round's knee and loop (RECORD: checks/astra-check-l4e11-2.md reproduces them)
PIN_ERR = 0.200              # A, the ILIM_HIZ pin's error at R16 10 mOhm (INFERRED by L4-E5 from TI's 0.4 A at 5 mOhm)
NET_TOL = 0.01               # the knee network's error on the pin voltage (ASSUMPTION, L4-E5's 1 %)
KNEE_IT = 1.82               # A board current, SESSION (final round): the flat target, between the warm-up's need and the trip
KNEE_TOP = 7.95              # V of VIN_RAW, SESSION (B3): where the flat target begins to fall; L4-E5's knee slope kept
GUARD_R14_K = 76.8           # kOhm, SESSION (B3): board A R14, the restart guard under the corrected knee
ENTRY = dict(rsns=4.5e-3, rsns_tcr=50e-6, prec=0.001, drift=2 * 50e-6 * 50.0, rset=100.0, riwrn=39.7e3, riscp=3010.0, ctmr=22e-9,
             r1=36.5e3, c1=10e-9, r2=10.0, cbst=1e-6, uv_top=59.0e3, uv_bot=10.0e3, ov_top=332e3, ov_bot=10.0e3,
             inp_top=100e3, inp_bot=39e3, rvs=100.0, cvs=100e-9, cscp=1e-9)   # SESSION (B1): the selected entry's values


def refuse(code, msg):
    sys.stderr.write("l4e11_power: %s; refusing\n" % msg)
    sys.exit(code)


def sha_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def read(key):
    rel, want = PINS[key]
    path = os.path.join(TOP, rel)
    if not os.path.isfile(path):
        refuse(2, "%s is not here (%s)" % (rel, "fetch_held_back.py" if "/held/" in rel else "the tree"))
    if sha_file(path) != want:
        refuse(2, "%s is not the pinned file" % rel)
    return path


def text(key):
    return open(read(key), encoding="utf-8").read()


def git_text(key):
    rel, want = GIT_PINS[key]
    r = subprocess.run(["git", "-C", TOP, "show", "%s:%s" % (L4E9_COMMIT, rel)], capture_output=True)
    if r.returncode != 0:
        refuse(2, "L4-E9's commit %s is not in this repository" % L4E9_COMMIT[:8])
    if hashlib.sha256(r.stdout).hexdigest() != want:
        refuse(2, "%s at %s is not the pinned file" % (rel, L4E9_COMMIT[:8]))
    return r.stdout.decode("utf-8")


_PDF = {}


def pdf_pages(key, layout=False):
    k = (key, layout)
    if k not in _PDF:
        read(key)
        _PDF[k] = PT.pdf_text(TOP, PINS[key][0], ["-layout"] if layout else [], PDFTEXT, "v2/docs/records/l4e11").split("\f")
    return _PDF[k]


def flat(t):
    return " ".join(t.split())


def find(key, pat, what, layout=False, flags=0):
    """The first page (1-based) whose text matches; the match. Flat text unless layout is asked."""
    for i, t in enumerate(pdf_pages(key, layout)):
        m = re.search(pat, t if layout else flat(t), flags)
        if m:
            return i + 1, m
    refuse(3, "%s not found in %s" % (what, PINS[key][0]))


def need(t, pat, what, flags=0):
    m = re.search(pat, t, flags)
    if not m:
        refuse(3, "%s not found" % what)
    return m


def f(m, i=1):
    return float(m.group(i).replace(",", ""))


def fmt(x, nd=3):
    s = ("%." + str(nd) + "f") % x
    return s.rstrip("0").rstrip(".") if "." in s else s


def netlist_nodes(t, name):
    m = re.search(r'\(net \(code "?\d+"?\) \(name "/?%s"\)(.*?)\n\s*\(net ' % re.escape(name), t, re.S)
    if not m:
        refuse(3, "net %s not in the netlist" % name)
    return re.findall(r'\(node \(ref "?([^" )]+)"?\) \(pin "?([^" )]+)"?', m.group(1))


def netlist_value(t, ref):
    m = re.search(r'\(comp \(ref "?%s"?\)\s*\(value "([^"]*)"' % re.escape(ref), t)
    if not m:
        refuse(3, "%s not in the netlist" % ref)
    return m.group(1)


def soa_lines():
    """CSD19532Q5B Figure 10 (SLPS414B p.6) read from the sheet's vector drawing, L4-E9's method (its soa_lines(), the
    same frame, legend and consistency checks), so the 10 ms, 1 ms and DC lines are TI's own coordinates."""
    pdf = read("csd19532")
    svg = subprocess.run(["pdftocairo", "-svg", "-f", "6", "-l", "6", pdf, "-"], capture_output=True).stdout.decode("utf-8", "replace")
    tr = "matrix(0.097966,0,0,-0.097966,64.4,445.1)"
    paths = []
    for m in re.finditer(r"<path[^>]*>", svg):
        # poppler 22 writes the stroke as a style property and "rgb(0%,0%,0%)", "matrix(a,b,...)"; poppler 24 writes a stroke
        # attribute and puts a space after each comma: the reader takes both, the path coordinates being the same
        t = re.sub(r",\s+", ",", m.group(0))
        st = re.search(r'stroke(?::|=")(rgb\([^)]*\))', t)
        if tr not in t or not st:
            continue
        pts = [(float(a), float(b)) for a, b in re.findall(r"[ML] ([-\d.]+) ([-\d.]+)", re.search(r' d="([^"]*)"', t).group(1))]
        paths.append((st.group(1), pts))
    frames = [p for c, p in paths if c == "rgb(0%,0%,0%)" and len(p) == 5 and p[0] == p[-1]]
    if not frames:
        refuse(3, "Figure 10's frame")
    fr = max(frames, key=lambda q: (max(a for a, _ in q) - min(a for a, _ in q)) * (max(b for _, b in q) - min(b for _, b in q)))
    x0, x1 = min(q[0] for q in fr), max(q[0] for q in fr)
    y0, y1 = min(q[1] for q in fr), max(q[1] for q in fr)
    lv = lambda x: -1.0 + 4.0 * (x - x0) / (x1 - x0)
    li = lambda y: -1.0 + 5.0 * (y - y0) / (y1 - y0)
    idm = [p for c, p in paths if c == "rgb(0%,0%,0%)" and len(p) == 3]
    if not idm or abs(10 ** li(idm[0][0][1]) - 400.0) > 4.0 or abs(10 ** lv(idm[0][1][0]) - 100.0) > 1.0:
        refuse(3, "Figure 10's IDM and 100 V boundary")
    txt = pdf_pages("csd19532", True)[5]
    rows = [re.findall(r"(10us|100us|1ms|10ms|DC)\b", ln) for ln in txt.splitlines() if re.search(r"\b(10us|100us)\b", ln)]
    if len(rows) != 2:
        refuse(3, "Figure 10's legend")
    legend = sorted(((p[0][1], p[0][0], c) for c, p in paths if len(p) == 2 and p[0][1] == p[1][1] and c != "rgb(0%,0%,0%)"
                     and 100 < p[1][0] - p[0][0] < 150 and p[0][1] > 1200), key=lambda q: (-q[0], q[1]))
    labels = rows[0] + rows[1]
    if len(legend) < len(labels):
        refuse(3, "Figure 10's legend segments")
    out = {}
    for lab, (_y, _x, col) in zip(labels, legend):
        cands = [p for c, p in paths if c == col and len(p) >= 3 and abs(10 ** lv(p[-1][0]) - 100.0) < 1.0]
        if len(cands) != 1:
            refuse(3, "Figure 10's %s line" % lab)
        out[lab] = [(lv(x), li(y)) for x, y in cands[0]]
    return out


def soa_at(line, vds):
    lx = math.log10(vds)
    for (xa, ya), (xb, yb) in zip(line, line[1:]):
        if xa <= lx <= xb:
            return 10 ** (ya + (yb - ya) * (lx - xa) / (xb - xa))
    refuse(3, "Figure 10 has no segment at %s V" % vds)


# ============================================================================================ the computation
def compute():
    R = {}
    T = {k: text(k) for k in ("reqs", "rules", "testplan", "hwfw", "panel", "assembly", "gen_a", "gen_e", "gen_p", "net_a",
                              "net_e", "packprot", "primcfg", "chain", "l4e5", "budget", "red2", "ecss")}
    for k in ("bq25731", "sluuaq3a", "csd17570", "cell", "lm5069", "csd19532", "d38999", "vh", "xt60", "keystone", "lapp",
              "alpha", "lm5176", "srf1260", "yageo", "fuse997", "mur104", "mur683", "bq25798", "lm74700", "tps4811", "csd19536", "tps1663",
              "bq25730", "aons21357", "bq4050", "bq25792", "sqj403", "buk6y10", "ap63200", "smcj", "dock_py", "arch", "msmf",
              "ltc3115", "tps55340", "tps63070", "xal60", "gen_b", "spra953", "an11158", "hollr2512", "tps37", "ltc2954", "tps62933",
              "n2n7002", "bzt52c", "tps2596", "ap64500"):
        read(k)
    L9 = git_text("l4e9")
    R["inputs"] = [(k, PINS[k][0], sha_file(os.path.join(TOP, PINS[k][0]))) for k in PINS]
    R["git_inputs"] = [(k, "%s:%s" % (L4E9_COMMIT[:8], GIT_PINS[k][0]), GIT_PINS[k][1]) for k in GIT_PINS]
    R["filed"] = []
    for name in INPUTS:
        p = os.path.join(TOP, REC, "inputs", name)
        if not os.path.isfile(p):
            refuse(2, "inputs/%s is not filed" % name)
        R["filed"].append((name, sha_file(p)))
    J = {n: json.load(open(os.path.join(TOP, REC, "inputs", n), encoding="utf-8")) for n in INPUTS}

    # ------------------------------------------------------------------ 1. what the requirements demand (quoted)
    reg = yaml.safe_load(T["reqs"])
    recs = {r["id"]: r for r in reg["records"] if "id" in r}
    q = lambda s: flat(str(s))
    R["req015"] = (q(recs["REQ-015"]["statement"]), q(recs["REQ-015"]["acceptance"]))
    R["req014_clause"] = need(q(recs["REQ-014"]["statement"]), r"missions longer than the pack rely on vehicle or solar input \(D-06\)", "REQ-014's input clause").group(0)
    R["req024_clause"] = need(q(recs["REQ-024"]["statement"]), r"a pack cold-soaked below about -10 C at the cells is not started from \(shore or vehicle power, or warming, first; D-02d\)", "REQ-024's D-02d clause").group(0)
    R["req046"] = q(recs["REQ-046"]["statement"])
    R["req046_hold"] = need(q(recs["REQ-046"]["acceptance"]), r"the bridge's own hold clears above 3 C \(PANEL\.md section 10\)", "REQ-046's hold").group(0)
    R["req077_clause"] = need(q(recs["REQ-077"]["acceptance"]), r"the charge held by the charger's CHRG_INHIBIT with the charger still carrying the kit on shore", "REQ-077's shore clause").group(0)
    R["req072_obl"] = recs["REQ-072"].get("obligation")
    R["req072_clause"] = need(q(recs["REQ-072"]["acceptance"]), r"after a permitted pack cutoff the remaining supply carries the loads, D-26", "REQ-072's cutoff clause").group(0)
    R["e4o"] = need(flat(T["testplan"]), r"started warm or from shore or vehicle input \(D-02d: a cold start from the pack below about -10 C cell temperature is out of scope; inside the envelope, so an acceptance test\)", "TEST-PLAN E4-O's start").group(0)
    names_state = lambda s: bool(re.search(r"\bPS-[A-Z]", s))
    ob = lambda rid: recs[rid].get("obligation") or "MANDATORY"
    R["req_rows"] = [
        ("REQ-015", ob("REQ-015"), "9 to 36 V, where measured not stated", names_state(" ".join(R["req015"])), "operates and charges; the pack's state not named"),
        ("REQ-014", ob("REQ-014"), "none", False, "missions longer than the pack rely on vehicle or solar input"),
        ("REQ-024 (D-02d)", ob("REQ-024"), "shore or vehicle (9 to 36 V by REQ-015)", names_state(R["req024_clause"]), "a cold-soaked pack: both FETs open below -9 C, the kit started on the source"),
        ("REQ-046", ob("REQ-046"), "none", names_state(R["req046"]), "below 0 C the pack warmed by its heater before charge; the bridge's hold clears above 3 C"),
        ("REQ-077", ob("REQ-077"), "on shore", names_state(R["req077_clause"]), "the charge held by CHRG_INHIBIT while the charger carries the kit (a pack present)"),
        ("REQ-072", ob("REQ-072"), "solar", True, "after a permitted pack cutoff the remaining supply carries the loads (PS-IDLE-SPEC is the objective's profile)"),
    ]
    R["no_mandatory_state"] = not any(st for rid, ob, v, st, _ in R["req_rows"] if ob != "OBJECTIVE")
    if not R["no_mandatory_state"]:
        refuse(4, "a mandatory requirement names a load state for source-only operation; this record's reading is wrong")

    # ------------------------------------------------------------------ 2. the charger with no usable pack (SLUSE66A)
    B = {}
    B["nobatfet"] = find("bq25731", r"No battery MOSFET for saving cost", "no battery MOSFET")[0]
    B["powerup"] = find("bq25731", r"Power up sequence when the charger is powered up from VBUS:.*?Converter powers up\.", "9.3.1", flags=re.S)[0]
    B["fig104"] = find("bq25731", r"2-cell without battery.*?Figure 10-4\. Power Up From 20 V.*?Figure 10-5\. Power Up From 5 V", "Figures 10-4 and 10-5", flags=re.S)[0]
    p, m = find("bq25731", r"When CHRG_OK goes HIGH, the system is powered from adapter through the charger\. When adapter is removed, the system is connected to battery\.", "section 11")
    B["sec11"], B["sec11_text"] = p, m.group(0)
    p, m = find("bq25731", r"CHRG_OK is an active HIGH open drain indicator\. It indicates the charger is in normal operation when the following conditions are valid: (.*?) 9\.3\.5", "9.3.4")
    B["chrgok"], B["chrgok_text"] = p, flat(m.group(1).replace("\u2022", " "))
    if re.search(r"batter", B["chrgok_text"], re.I):
        refuse(4, "CHRG_OK's conditions name the battery")
    p, m = find("bq25731", r"the charger decreases the charge current to provide priority to the system load\..*?If the system load keeps increasing after the charge current drops down to zero, the system voltage starts to drop\. As the system voltage drops below the battery voltage, the battery will discharge to supplement the heavy system load\.", "9.3.17", flags=re.S)
    B["dpm"] = p
    p, m = find("bq25731", r"4S\s+75%\s+([\d.]+) V\s+([\d.]+) V\s+([\d.]+) V\s+([\d.]+) V", "Table 9-2's 4S row", layout=True)
    B["t92"], B["cv4s"], B["sysovp4s"], B["vsysmin4s"] = p, f(m, 1), f(m, 2), f(m, 3)
    p, m = find("bq25731", r"CELL\(≥2 S\),VSRN < VSYS_MIN\s+(\d+)\s+mA", "ICLAMP", layout=True)
    B["iclamp_p"], B["iclamp"] = p, f(m) / 1000.0
    p, m = find("bq25731", r"BATOVP rising condition is triggered: if charge is enabled \(charge current is not 0A\) converter should shut down with both HS MOSFET and LS MOSFET turned off; if charge is disabled the converter should keep operating without disturbance", "9.3.21.5")
    B["batovp"] = p
    p, m = find("bq25731", r"the charger can enter HIZ mode \(converter shuts off\) when ILIM_HIZ pin voltage is below ([\d.]+) V", "9.3.8")
    B["hiz_p"], B["hiz_v"] = p, f(m)
    p, m = find("bq25731", r"when VSYS is lower than ([\d.]+) V, there is 2-ms deglitch time, the IIN_DPM is set to 0\.5 A by the charger itself\. After 2-ms deglitch time, the charger should shut down and latched off\.", "9.3.21.8")
    B["uvp_p"], B["uvp_v"] = p, f(m)
    p, m = find("bq25731", r"Overall (\d+)-.F effective capacitance on VSYS net is necessary \(POSCAP is preferred\)", "10.1")
    B["csys_p"], B["csys_uf"] = p, f(m)
    p, m = find("bq25731", r"0b: Enable Charge <default at POR>\s+1b: Inhibit Charge", "CHRG_INHIBIT", flags=re.S)
    B["inhibit_p"] = p
    p, m = find("bq25731", r"host terminates charge by setting CHRG_INHIBIT bit to 1b, or setting ChargeCurrent\(\) to zero", "9.4.1")
    B["term_p"] = p
    p, m = find("bq25731", r"Auto Wakeup Enable When this bit is HIGH, if the battery is below VSYS_MIN , the device should automatically enable (\d+)-mA charging current for (\d+) mins\.(.*?)0b: Disable <default at POR>", "AUTO_WAKEUP_EN")
    if len(m.group(3)) > 400:
        refuse(3, "AUTO_WAKEUP_EN's default is not on its own row")
    B["wake_p"], B["wake_ma"], B["wake_min"] = p, f(m, 1), f(m, 2)
    R["B"] = B
    # the netlists' facts behind it
    ga = T["gen_a"]
    m = need(ga, r'r\("R26", "([\d.]+)k 1% \(CELL_BATPRESZ: 4S, (\d+) percent of VDDA\)", "CH_VDDA", "CH_CELL", lcsc="C\d+"\); r\("R27", "([\d.]+)k 1%"', "the cell-count strap")
    R["strap"] = (f(m, 1), f(m, 3), 100.0 * f(m, 3) / (f(m, 1) + f(m, 3)))
    need(ga, r'r\("R17", "5mOhm 1% 2512 \(RSR, charge current sense\)", "VBAT", "CELL_FUSED", "RS2512"\)', "R17 between VSYS and the pack")
    need(ga, r'part\("Q6", "Transistor_FET", "2N7002", "2N7002: CHG_INHIBIT high = ILIM_HIZ low = charger in HiZ", "SOT23", \{"1": "CHG_INHIBIT", "2": "GND", "3": "CHG_ILIM"\}\)', "Q6 on ILIM_HIZ")
    ge = T["gen_e"]
    need(ge, r'part\("Q8", "Transistor_FET", "2N7002", "2N7002: SHORE_INHIBIT high pulls UVLO low = input off \(1 G, 2 S, 3 D\)", "SOT23", \{"1": "SHORE_INHIBIT", "2": "GND_V", "3": "HS_UVLO"\}\)', "Q8 on the hot swap's UVLO")
    gp = T["gen_p"]
    need(gp, r'27: "PACK_F", 28: "DSG_G", 29: "GND", 30: "NC", 31: "CHG_G"', "board P's gauge with PCHG not connected")
    need(gp, r'pfet5\("Q2", "CSD17570Q5B 30 V N-FET, discharge switch", "DSG_G", "SW", "PACK_P"', "Q2 the discharge FET")
    need(gp, r'r\("R7", "1k", "PACK_P", "VCC_F"\)', "the gauge's VCC from the pack terminal")
    R["fwc08"] = need(flat(T["hwfw"]), r"\| FW-C08 \| (.*?) \| (Boot low\. Asserted only on the operator's 'inputs off' and on the water\-on\-floor isolation, never for a temperature or 'no charge' hold \(those are FW\-A19's flag and the charger's CHRG_INHIBIT bit\)\. When the pack cannot discharge \(states S2 and S4: the gauge's XDSG, no pack, or both FETs open\) the bridge first warns that asserting it removes the kit's supply \(L4\-E11 7a, rule R\-a; LH\-10\)) \|", "FW-C08").group(2)
    R["fwa14"] = need(flat(T["hwfw"]), r"\| FW-A14 \| (CHG_INHIBIT .*?) \| (Held low \(charger enabled\) at power\-up; asserted only by firmware, never as a charge hold \(a hold is the CHRG_INHIBIT bit or ChargeCurrent 0, FW\-A19\), and never while the pack cannot discharge \(S2, S4: HIZ stops the converter and removes the kit's only supply\) \(L4\-E11 7a; LH\-10\)) \|", "FW-A14").group(2)
    R["panel10"] = need(flat(T["panel"]), r"high = the shore and vehicle inputs are held off at the front end, so nothing charges\.", "PANEL.md section 10").group(0)
    R["panel10_cold"] = need(flat(T["panel"]), r"Every charge hold \(cold, hot, the margin hold, or the operator's 'no charge'\) is a flag the firmware keeps until its own condition clears it \(the cold hold, read from the pack gauge's own thermistor by the sensor controller on E6 and reported over USB, below 0 C and cleared with hysteresis above 3 C\), whatever the pack's state\.", "PANEL.md's cold hold").group(0)
    # the pack (SLUUAQ3A, the pack's own tables)
    P = {}
    P["cuv_p"] = find("sluuaq3a", r"2\.2 Cell Undervoltage Protection.*?Trip Min cell voltage1\.\.4 ≤ CUV:Threshold for CUV:Delay duration SafetyAlert\(\)\[CUV\] = 0 SafetyStatus\(\)\[CUV\] = 1 BatteryStatus\(\)\[FD\] = 1,\[TDA\] = 0 OperationStatus\(\)\[XDSG\] = 1 Condition 1", "2.2 CUV trip", flags=re.S)[0]
    P["xdsg_p"] = find("sluuaq3a", r"SafetyStatus\(\)\[OCD1\] or \[OCD2\] or \[CUV\] or \[CUVC\] or \[AOLD\] or \[AOLDL\] or \[ASCD\] or \[ASCDL\] or \[UTD\] = 1", "4.12 XDSG")[0]
    P["xchg_p"] = find("sluuaq3a", r"SafetyStatus\(\)\[UTC\] = 1 OR", "4.12 XCHG")[0]
    P["pchg_p"] = find("sluuaq3a", r"Depending on the FET Options\[PCHG_COMM\] settings, the external precharge FET or CHG FET can be used in PRECHARGE mode", "4.9")[0]
    P["pchgbit_p"] = find("sluuaq3a", r"PCHG_COMM \(Bit 0\): Precharge FET selection 1 = CHG FET 0 = PCHG FET \(default\)", "14.2.1.1")[0]
    pc = flat(T["primcfg"])
    need(pc, r"\*\*0x3D\*\*: PACK_FUSE 0, SLEEPCHG 0, CHGFET 1, CHGIN 1, CHGSU 1, OTFET 1, PCHG_COMM 1", "the image's FET Options")
    P["shutdown_mv"] = f(need(pc, r"\| Shutdown Voltage \(14\.5\.2\.1\) \| 1750 mV \| (\d+) mV \|", "the image's Shutdown Voltage"))
    pp = yaml.safe_load(T["packprot"])
    fn = {x["id"]: x for x in pp["functions"]}
    P["cuv"] = float(fn["CELL_UNDER_VOLTAGE"]["threshold"]["value"])
    P["cuv_rec"] = float(re.search(r"([\d.]+) V", fn["CELL_UNDER_VOLTAGE"]["threshold"]["recovery"]).group(1))
    P["utd"] = float(fn["DISCHARGE_TEMPERATURE_WINDOW"]["threshold"]["low"])
    P["utc"] = float(fn["CHARGE_TEMPERATURE_WINDOW"]["threshold"]["low"])
    P["pre_a"] = float(fn["PRECHARGE_WINDOW"]["threshold"]["current_a"])
    P["pre_hi"] = float(fn["PRECHARGE_WINDOW"]["threshold"]["high"])
    P["cells"] = 4
    # Q2's body diode (CSD17570Q5B, SLPS...: page 3 rows)
    p, m = find("csd17570", r"VSD\s+Diode Forward Voltage\s+ISD = (\d+) A, VGS = 0 V\s+([\d.]+)\s+([\d.]+)\s+V", "Q2's VSD", layout=True)
    P["vsd_p"], P["vsd_i"], P["vsd_max"] = p, f(m, 1), f(m, 3)
    p, m = find("csd17570", r"RθJA\s+Junction-to-Ambient Thermal Resistance \(1\) \(2\)\s+(\d+)", "Q2's RthetaJA", layout=True)
    P["rja_p"], P["rja"] = p, f(m)
    p, m = find("csd17570", r"Operating Junction and.{0,600}?[\u2013-]55 to (\d+)\s*°C", "Q2's TJ", layout=True, flags=re.S)
    P["tj_max"] = f(m)
    P["q2"] = [(i, i * P["vsd_max"], i * P["vsd_max"] * P["rja"]) for i in (B["iclamp"], 3.0)]
    # the cell maker's precharge rows
    p, m = find("cell", r"Pre-charging voltage range\*+\s+(1\.0)V ~ (3\.0)V", "the precharge window", layout=True)
    P["cell_p"], P["pre_win"] = p, (f(m, 1), f(m, 2))
    m = find("cell", r"Current range of Pre-charging\s+(0\.1)C ~ (0\.5)C", "the precharge current range", layout=True)[1]
    P["pre_c"] = (f(m, 1), f(m, 2))
    m = find("cell", r"Charge : 0\.5C\(([\d,]+)mA\)", "the cell's C", layout=True)[1]
    P["c_a"] = f(m) / 1000.0 / 0.5
    P["clamp_c"] = B["iclamp"] / 3.0 / P["c_a"]
    P["cc_c"] = 3.0 / 3.0 / P["c_a"]
    # VSYS with the pack at its cutoff, and below it
    P["vsys_cuv"] = (P["cells"] * P["cuv"], P["cells"] * P["cuv"] + P["vsd_max"])
    P["vsys_shut"] = (P["cells"] * P["shutdown_mv"] / 1000.0, P["cells"] * P["shutdown_mv"] / 1000.0 + P["vsd_max"])
    P["release_stack"] = B["vsysmin4s"] - P["vsd_max"]            # SRN reaches VSYS_MIN with the stack this far up (worst VSD)
    P["window"] = (P["release_stack"] / P["cells"], P["cuv_rec"])
    P["rb_stack"] = RULE_SRN_V - P["vsd_max"]                    # with SRN at R-b's threshold the stack is at least this
    P["rb_imbalance"] = P["rb_stack"] / P["cells"] - P["cuv_rec"]   # a cell this far under the average is still covered
    R["P"] = P
    R["cv_max"] = f(need(L9, r"ChargeVoltage at most ([\d.]+) V", "the written ChargeVoltage's maximum"))

    # ------------------------------------------------------------------ 3. the source envelope at VIN_RAW and at the plug
    l5 = T["l4e5"]
    rows = {}
    for m in re.finditer(r"^\s+([\d.]+) V \|\s+([\d.]+) A\s+\|.*?\|\s+([\d.]+) V \| ([\d.]+) / ([\d.]+) A \| ([\d.]+) A \| ([\d.]+) A", l5, re.M):
        rows[float(m.group(1))] = dict(line=f(m, 2), pin_lo=f(m, 4), pin_hi=f(m, 5), hmax=f(m, 6), fe=f(m, 7))
    if sorted(rows) != [9.0, 12.0, 24.0, 36.0]:
        refuse(3, "L4-E5's envelope table")
    E = {"rows": rows}
    E["floor_min"] = f(need(l5, r"At the 9 V floor U3 still gets at least ([\d.]+) A", "L4-E5's floor minimum"))
    E["slope"] = f(need(l5, r"Its line: 1\.000 V \+ ([\d.]+) V/V x VIN_RAW at R16 10 mOhm", "L4-E5's line"))
    E["k0"] = f(need(l5, r"zero-current target, the pin at 1\.0 V .*?: VIN_RAW ([\d.]+) V \(", "the knee's zero"))
    E["hiz_lo"] = f(need(l5, r"So U3 is certainly in HIZ below ([\d.]+) V of VIN_RAW", "the HIZ entry"))
    E["oth"] = f(need(l5, r"VBUS20's other loads ([\d.]+) A\)", "VBUS20's other loads"))
    E["vb_nom"] = f(need(l5, r"VBUS20 nominal ([\d.]+) V", "VBUS20 nominal"))
    E["eta_fe"] = f(need(l5, r"the front end at ([\d.]+) and\s+VBUS20", "the front end's efficiency"))
    m = need(L9, r"per source at VBAT \(U3 ([\d.]+), VBUS20 ([\d.]+) V top, ([\d.]+) V lowest\): vehicle at 9 V ([\d.]+) to ([\d.]+) W \(the entry itself bounds 9 V at ([\d.]+) W\); at 12 V up to ([\d.]+) W; at 24 V up to ([\d.]+) W", "L4-E9's per-source line")
    E["eta_u3"], E["vb_top"], E["vb_low"] = f(m, 1), f(m, 2), f(m, 3)
    E["l9"] = dict(min9=f(m, 4), max9=f(m, 5), entry9=f(m, 6), max12=f(m, 7), max24=f(m, 8))
    m = need(L9, r"IIN_HOST ([\d.]+) A \(minimum ([\d.]+) A, maximum ([\d.]+) A board current", "IIN_HOST's band")
    E["iin_min"], E["iin_max"] = f(m, 2), f(m, 3)
    m = need(L9, r"the entry ([\d.]+) to ([\d.]+) A \(basis", "the entry's limit")
    E["entry"] = (f(m, 1), f(m, 2))
    E["r16_tol"] = f(need(ga, r'r\("R16", "10mOhm (\d+)% 2512', "R16's tolerance")) / 100.0
    env = {}
    for v in (9.0, 12.0, 24.0, 36.0):
        lo = (E["floor_min"] if v == 9.0 else rows[v]["pin_lo"]) / (1 + E["r16_tol"])
        lo = min(lo, E["iin_min"])
        hi = rows[v]["hmax"]
        env[v] = dict(board_lo=lo, board_hi=hi, w_lo=lo * E["vb_low"] * E["eta_u3"], w_hi=hi * E["vb_top"] * E["eta_u3"])
    E["env"] = env
    E["entry9_w"] = E["entry"][0] * 9.0 * E["eta_fe"] * E["eta_u3"]
    # the load states (the budget's battery-terminal figures, taken at VBAT)
    bu = T["budget"]
    st = {}
    for name in ("PS-RED", "PS-IDLE-SPEC", "PS-TYP"):
        m = need(bu, r"^%s\s+load\s+[\d.]+ \| battery\s+([\d.]+) /\s+([\d.]+) /\s+([\d.]+)" % re.escape(name), name, re.M)
        st[name] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(bu, r"PS-RED plus the heater \(cold overlay\), lid closed \{\"battery_W_plan\": ([\d.]+)", "PS-RED with the heater")
    st["PS-RED with the heater"] = (None, f(m), None)
    rd = T["red2"]
    m = need(rd, r'"PS-IDLE-SPEC, link cards held off, heater on": \{\s+"battery_W_plan": ([\d.]+)', "the cold idle with heater")
    st["PS-IDLE-SPEC cold, heater on"] = (None, f(m), None)
    m = need(rd, r'"warm-up: PS-TYP, link cards and SDR held off, heater on, three modules loaded": \{\s+"battery_W_plan": ([\d.]+)', "the cold warm-up")
    st["the cold warm-up (CONOPS 4c)"] = (None, f(m), None)
    E["states"] = st
    cls = {}
    for name, (lo, plan, hi) in st.items():
        for v in (9.0, 12.0, 24.0, 36.0):
            e = env[v]
            cls[(name, v)] = "carried at every corner" if plan <= e["w_lo"] else ("only above the line's minimum" if plan <= e["w_hi"] else "not carried")
    E["cls"] = cls
    # the dead pack's charge share inside the envelope
    E["dead_charge_w"] = B["iclamp"] * P["vsys_cuv"][1]
    # the entry's UVLO band (U4-F2)
    l69 = flat("".join(pdf_pages("lm5069", True)))
    m = need(l69, r"UVLOTH UVLO threshold ([\d.]+) ([\d.]+) ([\d.]+) V UVLOHYS UVLO hysteresis current UVLO = 1 V (\d+) (\d+) (\d+) µA", "LM5069 UVLO rows")
    uv = (f(m, 1), f(m, 2), f(m, 3)); hy = (f(m, 4) * 1e-6, f(m, 5) * 1e-6, f(m, 6) * 1e-6)
    E["uvlo_page"] = find("lm5069", r"UVLOTH\s+UVLO threshold", "the UVLO row", layout=True)[0]
    m = need(ge, r'r\("R20", "(\d+)k (\d+)%", "DC_P", "HS_UVLO"\); r\("R21", "([\d.]+)k (\d+)% \(UVLO: 9 V\)", "HS_UVLO", "GND_V"\)', "R20 and R21")
    E["uv_rows"], E["hy_rows"] = uv, hy
    E["r20"], E["r21"] = f(m, 1) * 1e3, f(m, 3) * 1e3            # the corrected thresholds (Equations 38 to 40) are entry_round's
    # the 9 V at the kit's plug (U4-F3): the kit's own series resistance
    m = need(L9, r"the kit's cable \(([\d.]+) m of ([\d.]+) mm2 a way\) and lead \((\d+) mm of AWG (\d+)\)\s+give ([\d.]+) Ohm at 20 C and ([\d.]+) Ohm at -20 C, so a stiff source drives at most ([\d.]+) A", "L4-E9's cable", re.S)
    E["cable_drawn"] = dict(m=f(m, 1), mm2=f(m, 2), lead_mm=f(m, 3), awg=int(m.group(4)), r20=f(m, 5), rcold=f(m, 6), ipf=f(m, 7))
    srf = flat(pdf_pages("srf1260", True)[0])
    m = need(srf, r"SRF1260-1R5Y 1\.5 ±30 ([\d.]+) ([\d.]+) ([\d.]+) 6 ±30 ([\d.]+) ([\d.]+) ([\d.]+)", "SRF1260-1R5Y's row")
    E["l2_dcr"] = f(m, 4)
    c19 = flat(pdf_pages("csd19532", True)[2])
    m = need(c19, r"VGS = 10 V, ID = 17 A ([\d.]+) ([\d.]+) m", "CSD19532Q5B RDS(on)")
    E["q_rds"] = f(m, 2) * 1e-3
    fz = flat("".join(pdf_pages("fuse997", True)))
    m = need(fz, r"0997010_ 10 (\d+) (\d+) ([\d.]+) (\d+)", "the 0997 10 A ratings row")
    E["f1_test_mm2"], E["f1_rcold"], E["f1_i2t"] = f(m, 1), f(m, 3) * 1e-3, f(m, 4)
    E["r_e"] = E["l2_dcr"] + 0.010 * (1 + 0.01) + 2 * E["q_rds"] + E["f1_rcold"]
    sel_r20 = (2 * SEL_CABLE_M + 2 * LEAD_M) * CU_RHO_20 / SEL_MM2
    E["r_plug"] = {"drawn": E["cable_drawn"]["r20"] + E["r_e"], "selected": sel_r20 + E["r_e"]}

    def line_board(v):                                     # H3's nominal target (L4-E5): the line from 9 V, the knee below
        if v >= 9.0:
            return E["slope"] / (40 * 0.010) * v
        if v <= E["k0"]:
            return 0.0
        return E["slope"] / (40 * 0.010) * 9.0 * (v - E["k0"]) / (9.0 - E["k0"])

    def fe_in(board, v):
        return (board + E["oth"]) * E["vb_nom"] / (E["eta_fe"] * v)
    plug = {}
    for k, rr in E["r_plug"].items():
        lo, hi = E["k0"], PLUG_V
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if PLUG_V - mid > fe_in(line_board(mid), mid) * rr:
                lo = mid
            else:
                hi = mid
        v = 0.5 * (lo + hi)
        b = line_board(v)
        plug[k] = dict(r=rr, vin=v, board=b, w=b * E["vb_nom"] * E["eta_u3"], knee_top=PLUG_V - rows[9.0]["fe"] * rr)
    E["plug"] = plug
    E["line9_nom_w"] = line_board(9.0) * E["vb_nom"] * E["eta_u3"]
    R["E"] = E

    # ------------------------------------------------------------------ 4. the comparison's own figures
    C = {}
    C["pack_peak"] = f(need(ga, r'_intent\.rail\("VBAT", [\d.]+, [\d.]+, ([\d.]+), "R17"', "VBAT's declared peak"))
    C["batfet_w_per_mohm_18a"] = C["pack_peak"] ** 2 * 1e-3
    C["idle_a"] = st["PS-IDLE-SPEC"][1] / 14.4
    C["batfet_w_per_mohm_idle"] = C["idle_a"] ** 2 * 1e-3
    C["pre_i_01c"] = P["pre_c"][0] * P["c_a"] * 3
    C["pre_r_01c"] = (B["cv4s"] - P["vsys_shut"][0]) / C["pre_i_01c"]
    C["pre_w_01c"] = (B["cv4s"] - P["vsys_shut"][0]) * C["pre_i_01c"]
    C["pre_r_clamp"] = (B["cv4s"] - P["vsys_shut"][0]) / B["iclamp"]
    C["pre_w_clamp"] = (B["cv4s"] - P["vsys_shut"][0]) * B["iclamp"]
    C["pre_w_cuv_01c"] = (B["cv4s"] - P["vsys_cuv"][0]) ** 2 / C["pre_r_01c"]
    C["nvdc_p"] = find("bq25798", r"It uses NVDC power path management, regulating the system not dropping below a configurable minimum system voltage\.", "BQ25798's NVDC")[0]
    p_, m = find("bq25798", r"RMS discharge current \(continuously\)\s+(\d+)\s+A", "BQ25798's battery FET RMS", layout=True)
    C["bq98_rms"], C["bq98_p"] = f(m), p_
    C["bq98_pk"] = f(find("bq25798", r"Peak discharge current \(upto 1 sec\)\s+(\d+)\s+A", "BQ25798's battery FET peak", layout=True)[1])
    R["C"] = C

    # ------------------------------------------------------------------ 5. the owner-question test (U-04)
    F = {}
    m = need(fz, r"10A 10 10 ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)", "the 0997 10 A derating row")
    F["der"] = dict(zip((-40, -20, 0, 20, 40, 60, 80, 100), (10.0, 10.0, f(m, 1), f(m, 2), f(m, 3), f(m, 4), f(m, 5), f(m, 6))))
    F["air_hot"] = f(need(L9, r"inside air ([\d.]+) / ([\d.]+) C \(lid open / closed\)", "the hottest inside air"), 2)
    col = [c for c in sorted(F["der"]) if c >= F["air_hot"]][0]
    F["f_col"], F["f_hot_a"] = col, F["der"][col]
    F["cap9_hot_w"] = F["f_hot_a"] * 9.0 * E["eta_fe"] * E["eta_u3"]
    F["cap9_cold_w"] = F["der"][0] * 9.0 * E["eta_fe"] * E["eta_u3"]
    F["cap9_interconnect_w"] = CONT_CLASS_A * 9.0 * E["eta_fe"] * E["eta_u3"]
    m = need(fz, r"15A 15 15 (\d+) (\d+) (\d+) (\d+) (\d+) ([\d.]+)", "the 0997 15 A derating row")
    F["der15_hot"] = f(m, 5)
    F["cap9_15a_hot_w"] = F["der15_hot"] * 9.0 * E["eta_fe"] * E["eta_u3"]
    F["over_hot"] = [(n, pl) for n, (lo, pl, hi) in st.items() if pl > F["cap9_hot_w"] and "cold" not in n and "warm-up" not in n]
    F["cold_over"] = [(n, pl) for n, (lo, pl, hi) in st.items() if ("cold" in n or "warm-up" in n) and pl > F["cap9_cold_w"]]
    named_loads = [(rid, st_) for rid, ob, v, st_, _ in R["req_rows"] if ob != "OBJECTIVE" and st_]
    F["owner_question"] = bool(named_loads)
    R["F"] = F

    # ------------------------------------------------------------------ 6. D-06: the weak-source band and the interconnect
    D = {}
    m = need(fz, r"110 360 000 / - 135 ([\d.]+) / (\d+) 200 ([\d.]+) / (\d+) 350 ([\d.]+) / ([\d.]+) 600 ([\d.]+) / ([\d.]+)", "the 0997's time-current rows")
    D["tc"] = [(1.10, 360000.0, None), (1.35, f(m, 1), f(m, 2)), (2.00, f(m, 3), f(m, 4)), (3.50, f(m, 5), f(m, 6)), (6.00, f(m, 7), f(m, 8))]
    D["rating"] = 10.0
    D["band"] = [(D["rating"] * pct, tmax) for pct, _tmin, tmax in D["tc"][1:]]
    D["cont_need"] = D["rating"] * D["tc"][1][0]                       # under 135 % no maximum time is printed
    D["interrupt_v"], D["interrupt_a"] = 58.0, 1000.0
    need(fz, r"Voltage Rating: 58 V DC Interrupting Rating: 1000 A @ 58 V DC", "the 0997's ratings")
    dz = flat("".join(pdf_pages("d38999", True)))
    dz = dz[need(dz, r"CONTACT RATING FOR TV III, HD, JT II, LJT I, SJT", "the D38999 contact table").start():]
    m = need(dz, r" 16 (\d+) (\d+) (\d+) \d+ \d+", "size 16")
    D["c16"], D["c16_mv"] = f(m, 1), f(m, 3)
    m = need(dz, r" 12 (\d+) (\d+) (\d+) \d+ \d+", "size 12")
    D["c12"], D["c12_mv"] = f(m, 1), f(m, 3)
    D["d38999_p"] = find("d38999", r"CONTACT RATING FOR TV III, HD, JT II, LJT I, SJT", "the contact table")[0]
    p, m = find("d38999", r"Series III TV\s+13-4\s+13-8\s+13-26\s+13-32 HD\s+13-35", "the shell 13 arrangements", layout=True)
    D["ins13_p"] = p
    p, m = find("d38999", r"Series III TV\s+17-2\s+17-6\s+17-8", "the shell 17 arrangements", layout=True)
    D["ins17_p"] = p
    asm = flat(T["assembly"])
    need(asm, r"Glenair D38999/26FC4SN plug \(shell 13, insert 13-4, four M39029/56-352 size 16 socket contacts", "the drawn DC plug")
    need(asm, r"Lapp OLFLEX ROBUST 210 4 x 1\.0 \(article 0021917, 6\.6 mm, TPE, outdoor\), or Alpha Wire 25064 \(18 AWG 4C, TPU, 6\.58 mm\); 2 m", "the drawn DC lead")
    vh = find("vh", r"Current rating: (\d+) A", "the VH rating", layout=True)
    D["vh"] = f(vh[1])
    need(flat(pdf_pages("vh", True)[0]), r"When using AWG #16 with the standard type header", "the VH condition")
    D["vh_max_awg"] = int(need(flat(pdf_pages("vh", True)[0]), r"Conductor size/ AWG #(\d+) to AWG #(\d+)", "the VH conductor range").group(2))
    xt = flat(pdf_pages("xt60", True)[0])
    D["xt60"], D["xt60_inst"] = f(need(xt, r"额定电流 (\d+)A", "XT60 rated")), f(need(xt, r"瞬时电流 (\d+)A", "XT60 instantaneous"))
    D["xt60_awg"] = int(need(xt, r"推荐线规 (\d+)AWG", "XT60 wire").group(1))
    read("keystone")
    ks = flat(PT.pdf_text(TOP, PINS["keystone"][0], [], PDFTEXT, "v2/docs/records/l4e11"))
    m = need(ks, r"CAT\. NO\. 3568 HORIZONTAL FUSE ENTRY ® For Littelfuse Mini 297 or 997 series/Bussmann ATM series or equivalent SPECIFICATIONS Contacts: \.012 \(\.30\) Brass Insulator: Nylon 6/6, UL Rated 94V-0 UL Temperature Rating: (.*?)\(-50°C to\+145°C\)", "the 3568 entry")
    D["holder_rating_printed"] = bool(re.search(r"Current Rating", m.group(0)))
    D["keystone_ratings"] = sorted(set(int(x) for x in re.findall(r"UL Current Rating: (\d+) Amps", ks)))
    for k in ("lapp", "alpha"):
        t = flat("".join(pdf_pages(k, True)))
        if re.search(r"(current[- ]carrying|ampacity|rated current|current rating)", t, re.I):
            refuse(4, "%s prints a current rating; this record says it does not" % PINS[k][0])
    D["cable_rating_printed"] = False
    ch = yaml.safe_load(T["chain"])
    si = [x for x in ch["stages"] if x["id"] == "SHORE_INPUT"][0]
    D["band_board_a"] = float(si["conductor"]["rating_a"])
    D["drawn"] = [("J_DCIN's VH contact (the lead AWG %d)" % E["cable_drawn"]["awg"], None, "VH prints %s A at AWG 16 with the standard header and 7 A at AWG 18 with the shrouded one; the drawn lead is AWG %d on the standard header: none stated" % (fmt(D["vh"]), E["cable_drawn"]["awg"]), "MAKER"),
                  ("the D38999 size 16 contact, insert 13-4", D["c16"], "Amphenol's test current", "MAKER"),
                  ("F1's holder, Keystone 3568", None, "the page prints a UL current rating for other MINI clips and holders (%s A) and none for the 3568" % ", ".join(str(x) for x in D["keystone_ratings"]), "MAKER"),
                  ("the DC lead, Lapp OLFLEX ROBUST 210 4 x 1.0 or Alpha Wire 25064", None, "no current rating printed in either sheet", "MAKER"),
                  ("the inside lead, %d mm of AWG %d" % (E["cable_drawn"]["lead_mm"], E["cable_drawn"]["awg"]), None, "no part and no rating", "NETLIST"),
                  ("board E's input bands at 2 oz", D["band_board_a"], "pcb_energy_chain.yaml SHORE_INPUT", "RECORD")]
    D["drawn_met"] = all(r is not None and r >= D["cont_need"] for _n, r, _s, _c in D["drawn"])
    D["selected"] = [("receptacle and plug contacts", "MIL-DTL-38999 size 12 (insert 17-6, or 13-26 with the solar pair on rated contacts elsewhere)", D["c12"], "Amphenol test current, MAKER"),
                     ("J_DCIN, the board connector", "a %d A class (Amass XT60 family, gender opposite J_BATT's), or soldered lead lands" % D["xt60"], D["xt60"], "Amass V1.2: %d A rated, %d A instantaneous, %d AWG recommended, MAKER" % (D["xt60"], D["xt60_inst"], D["xt60_awg"])),
                     ("F1's holder", "a MINI 297/997 holder whose maker prints at least %d A" % CONT_CLASS_A, None, "the 3568 prints none: Layer 7/8 picks"),
                     ("the DC lead and the inside lead", "cores of %.3f mm2 (AWG 14) whose maker states at least %d A continuous each" % (SEL_MM2, CONT_CLASS_A), None, "no held sheet: an acceptance for Layer 7"),
                     ("board E's copper J_DCIN to F1 to the clamps", "at least %d A continuous" % CONT_CLASS_A, None, "a layout constraint (Layer 9)")]
    # the stiff source again (copper alone at the cold end; the source's own resistance zero, A-12)
    vmax = f(need(L9, r"the selected OVLO \(R23 6\.42k, R22 100k, both 0\.1 %\): ([\d.]+) / ([\d.]+) / ([\d.]+) V", "the OVLO maximum"), 3)
    D["vmax"] = vmax
    rho_c = CU_RHO_20 * (1 + CU_ALPHA * (T_COLD - 20.0))
    cd = E["cable_drawn"]
    drawn_r = (2 * cd["m"] / cd["mm2"] + 2 * cd["lead_mm"] / 1000.0 / AWG18_MM2) * rho_c
    D["stiff"] = [("as drawn: %s m of %s mm2 and %d mm of AWG 18 (L4-E9)" % (fmt(cd["m"]), fmt(cd["mm2"]), cd["lead_mm"]), drawn_r, vmax / drawn_r)]
    for lab, cm, mm2 in (("AWG 14, 2.0 m cable, 0.5 m lead", 2.0, AWG14_MM2), ("AWG 14, %s m cable, 0.5 m lead (SELECTED)" % fmt(SEL_CABLE_M), SEL_CABLE_M, AWG14_MM2),
                         ("AWG 12, %s m cable, 0.5 m lead" % fmt(SEL_CABLE_M), SEL_CABLE_M, AWG12_MM2)):
        rr = (2 * cm + 2 * LEAD_M) * rho_c / mm2
        D["stiff"].append((lab, rr, vmax / rr))
    if abs(D["stiff"][0][2] - cd["ipf"]) > 0.6:
        refuse(4, "the drawn stiff-source current does not reproduce L4-E9's %s A" % cd["ipf"])
    D["r_floor"] = vmax / D["interrupt_a"]
    D["min_len_14"] = (D["r_floor"] * AWG14_MM2 / rho_c - 2 * LEAD_M) / 2.0
    D["sel_ipf"] = D["stiff"][2][2]
    if not D["sel_ipf"] <= D["interrupt_a"]:
        refuse(4, "the selected interconnect's stiff-source current passes F1's interrupting rating")
    rho_hot = CU_RHO_20 * (1 + CU_ALPHA * (F["air_hot"] - 20.0))
    D["min_fault_9v"] = 9.0 / ((2 * SEL_CABLE_M + 2 * LEAD_M) * rho_hot / SEL_MM2)
    D["min_fault_9v_x"] = D["min_fault_9v"] / D["rating"]
    # the short-time points: adiabatic rise of a 2.081 mm2 core, and the contact's I2t at its rated current
    s_cm2 = SEL_MM2 / 100.0
    D["adiabatic"] = [(i, t, i * i * t * CU_RHO_20 * 1e-4 / (s_cm2 ** 2 * CU_CV)) for i, t in D["band"][1:]]
    D["contact_eq_s"] = [(i, t, i * i * t / D["c12"] ** 2) for i, t in D["band"][1:]]
    D["sel_ok"] = D["c12"] >= CONT_CLASS_A >= D["band"][1][0] >= D["cont_need"] and D["xt60"] >= CONT_CLASS_A
    R["D"] = D

    # ------------------------------------------------------------------ 7. D-09: the fault timer against the start
    T9 = {}
    m = need(l69, r"VTMRH Upper threshold ([\d.]+) ([\d.]+) ([\d.]+) V", "VTMRH")
    T9["vtmrh"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(l69, r"Fault detection current (\d+) (\d+) (\d+) µA", "ITIMER")
    T9["itimer"] = (f(m, 1) * 1e-6, f(m, 2) * 1e-6, f(m, 3) * 1e-6)
    m = need(l69, r"VCL Threshold voltage VIN-SENSE voltage ([\d.]+) ([\d.]+) ([\d.]+) mV", "VCL")
    T9["vcl"] = (f(m, 1) * 1e-3, f(m, 2) * 1e-3, f(m, 3) * 1e-3)
    need(l69, r"TI recommends setting the minimum fault time \(tflt\) to be greater than the start time \(tstart\) by adding an additional margin of 50% of the fault time", "TI's 50 % margin")
    T9["eq12_p"] = find("lm5069", r"9\.2\.1\.2\.4 Set Fault Timer", "9.2.1.2.4")[0]
    m = need(l69, r"R PWR 1\.30 u 10 5 u R SNS \(PLIM 1\.18mV u", "Equation 9")
    T9["k9"], T9["v9"] = 1.30e5, 1.18e-3
    m = need(L9, r"the power limit with R24 22 k: ([\d.]+) W nominal, ([\d.]+) W at its corners, ([\d.]+) W with TI's 1\.3 margin, ([\d.]+) A at ([\d.]+) V", "L4-E9's power limit")
    T9["plim_nom_l9"], T9["pulse_a"] = f(m, 1), f(m, 4)
    T9["rpwr"] = 22e3
    T9["rs"] = 0.010
    T9["rs_tol"] = f(need(ge, r'r\("R19", "10mOhm (\d+)% 2512 \(hot-swap sense\)"', "R19")) / 100.0
    plim = lambda rpwr, rs, vds: rpwr / (T9["k9"] * rs) + T9["v9"] * vds / rs
    T9["plim_nom"] = plim(T9["rpwr"], T9["rs"], vmax)
    if abs(T9["plim_nom"] - T9["plim_nom_l9"]) > 0.01:
        refuse(4, "Equation 9 does not reproduce L4-E9's %s W" % T9["plim_nom_l9"])
    m = need(L9, r"Equation 19 derates by ([\d.]+)", "L4-E9's derating")
    T9["derate"] = f(m)
    T9["tc_case"] = f(need(L9, r"Q7's case at most ([\d.]+) C", "Q7's case"))
    # the capacitance the start charges: DC_HS and VIN_RAW on board E, VIN_RAW and the guard's two filters on board A
    na, ne = T["net_a"], T["net_e"]
    caps = []
    for net, t_, b in (("DC_HS", ne, "E"), ("VIN_RAW", ne, "E"), ("VIN_RAW", na, "A"), ("FE_VINP", na, "A"), ("FE_GVDD", na, "A")):
        for ref, _pin in netlist_nodes(t_, net):
            if ref.startswith("C"):
                mv = re.match(r"([\d.]+)u", netlist_value(t_, ref))
                if mv:
                    caps.append((b, ref, net, float(mv.group(1))))
    T9["caps"] = caps
    T9["c_uf"] = sum(x[3] for x in caps)
    # the resistive load during the start (each path bounded by its resistor alone to ground): LED1 behind R27, R40, R14, R200
    loads = []
    for t_, b, ref in ((ne, "E", "R27"), (ne, "E", "R40"), (na, "A", "R14"), (na, "A", "R200")):
        nodes = netlist_nodes(t_, "VIN_RAW")
        if (ref, "1") not in nodes and (ref, "2") not in nodes:
            refuse(3, "%s is not on VIN_RAW" % ref)
        loads.append((b, ref, float(re.match(r"([\d.]+)k", netlist_value(t_, ref)).group(1)) * 1e3))
    T9["loads"] = loads
    T9["g_load"] = sum(1.0 / r for _b, _r, r in loads)
    m = find("lm5176", r"IQ\s+VIN shutdown current\s+VEN/UVLO = 0 V\s+([\d.]+)\s+(\d+)\s+µA", "LM5176 shutdown", layout=True)[1]
    T9["u2_sd"] = f(m, 2) * 1e-6
    # the front end's enable: U34's release delay (gen_sch_a.py's derivation from SNVSBJ1E)
    m = need(flat(ga), r"C212\W+100 nF on CTR2 holds the release (\d+) / (\d+) / (\d+) ms", "U34's release delay")
    T9["ctr2_ms"] = (f(m, 1), f(m, 2), f(m, 3))
    # the X7R rows L4-E9 stacked (Yageo V.26) for the start's capacitors
    ya = flat("".join(pdf_pages("yageo", True)))
    need(ya, r"K = ± 10%", "Yageo K")
    T9["x7r"] = (0.10, f(need(ya, r"\(temperature characteristic/coefficient\): ± (\d+)%", "X7R temperature")) / 100.0,
                 f(need(ya, r"Endurance IEC 60384-.*?X7R: ± (\d+)%", "X7R endurance")) / 100.0)
    hi_f = (1 + T9["x7r"][0]) * (1 + T9["x7r"][1]) * (1 + T9["x7r"][2])

    def t_start(c_f, rpwr, rs, ilim, margin, g):
        n, dv, t, v = STEP_N, vmax / STEP_N, 0.0, 0.0
        for _ in range(n):
            vm = v + 0.5 * dv
            vds = vmax - vm
            i = min(plim(rpwr, rs, vds) / margin / vds, ilim)
            il = vm * g + (T9["u2_sd"] if g else 0.0)
            if i <= il:
                refuse(4, "the start stalls at %.2f V" % vm)
            t += c_f * dv / (i - il)
            v += dv
        return t
    T9["eq12_nom"] = T9["c_uf"] * 1e-6 / 2 * (vmax ** 2 / T9["plim_nom"] + T9["plim_nom"] / (T9["vcl"][1] / T9["rs"]) ** 2)
    T9["start_nom"] = t_start(T9["c_uf"] * 1e-6, T9["rpwr"], T9["rs"], T9["vcl"][1] / T9["rs"], 1.0, T9["g_load"])
    rs_hi = T9["rs"] * (1 + T9["rs_tol"])
    T9["start_max"] = t_start(T9["c_uf"] * 1e-6 * hi_f, T9["rpwr"] * 0.99, rs_hi, T9["vcl"][0] / rs_hi, 1.3, T9["g_load"])
    T9["start_max_noload"] = t_start(T9["c_uf"] * 1e-6 * hi_f, T9["rpwr"] * 0.99, rs_hi, T9["vcl"][0] / rs_hi, 1.3, 0.0)
    m = need(L9, r"takes ([\d.]+) ms at nominal values and ([\d.]+) ms with the capacitors at the printed rows' top", "L4-E9's start", re.S)
    T9["start_l9"] = (f(m, 1) * 1e-3, f(m, 2) * 1e-3)
    T9["need"] = 1.5 * T9["start_max"]
    T9["ctr2_over_start"] = T9["ctr2_ms"][0] * 1e-3 / T9["start_max"]
    # Figure 10 at the OVLO maximum (TI's vector drawing), TI's power law between 1 and 10 ms carried past 10 ms
    lines = soa_lines()
    i10, i1, idc = soa_at(lines["10ms"], vmax), soa_at(lines["1ms"], vmax), soa_at(lines["DC"], vmax)
    T9["i10"], T9["i1"], T9["idc"] = i10, i1, idc
    T9["m"] = math.log(i1 / i10) / math.log(10.0)
    soa = lambda t, mexp=None: i10 * (10e-3 / t) ** (T9["m"] if mexp is None else mexp) * T9["derate"]
    T9["t_soa_max"] = 10e-3 * (i10 * T9["derate"] / T9["pulse_a"]) ** (1.0 / T9["m"])
    # the Murata C0G rows (both reference sheets) and the catalogue readings
    mur = {}
    for k in ("mur104", "mur683"):
        tx = flat("".join(pdf_pages(k, True)))
        m = need(tx, r"(GRM3195C1H\d{3}[GJ]A05)_\(3216M\(1206\), C0G\(EIA\), ([\d.]+)(μF|pF), DC (\d+)V\)", "the Murata part line")
        val = f(m, 2) * (1e-6 if m.group(3) == "μF" else 1e-12)
        mm = need(tx, r"0\+/-(\d+) ppm/℃ 25 to 125℃ 25℃ DC (\d+)V [\d.]+(?:μF|pF) \+/-(\d+)% -55 to 125℃", "the rated values")
        ta = need(tx, r"Table A Capacitance Change between at Reference Temp\. and at each Temp\. \(%\) -55℃ -30℃ -10℃ Char\. Max\. Min\. Max\. Min\. Max\. Min\. 5C ([\d.]+) -([\d.]+)", "Table A")
        en = need(tx, r"Endurance Visual examination No defects or abnormalities\. Mounting method Solder the capacitor on the test substrate Capacitance Change Within \+/-(\d+)%", "the endurance row")
        dh = need(tx, r"Damp heat, steady state Visual examination No defects or abnormalities\. Mounting method Solder the capacitor on the test substrate Capacitance Change Within \+/-([\d.]+)%", "the damp heat row")
        mur[m.group(1)] = dict(c=val, v=f(m, 4), ppm=f(mm, 1) * 1e-6, tol=f(mm, 3) / 100.0, ta_up=f(ta, 1) / 100.0, ta_dn=f(ta, 2) / 100.0,
                               endur=f(en) / 100.0, damp=f(dh) / 100.0, page=find(k, r"Endurance\s+Visual examination", "endurance page", layout=True)[0])
    T9["mur"] = mur
    lc = {J[n]["code"]: J[n] for n in INPUTS if n.startswith("lcsc-")}
    code_of = {lc[c]["model"][:-1]: c for c in lc}
    for pn in mur:
        if pn not in code_of or lc[code_of[pn]]["stock"] < 1000:
            refuse(4, "%s has no filed LCSC reading with stock" % pn)
    T9["search150"] = (J["jlc-search-c0g-150nf-2026-10-02.json"]["count"], J["jlc-search-c0g-150nf-2026-10-02.json"]["stocked_count"])
    temp_up = max(next(iter(mur.values()))["ta_up"], 0.0)
    temp_dn = max(next(iter(mur.values()))["ta_dn"], 100.0 * next(iter(mur.values()))["ppm"])

    def env_of(parts, extra):
        lo = sum(mur[p]["c"] * (1 - mur[p]["tol"]) for p in parts) * (1 - temp_dn) * (1 - extra)
        hi = sum(mur[p]["c"] * (1 + mur[p]["tol"]) for p in parts) * (1 + temp_up) * (1 + extra)
        return lo, hi
    pA, pB = sorted(mur, key=lambda p: -mur[p]["c"])           # the 100 nF G part and the 68 nF J part
    cand = [("one %s" % pA, [pA]), ("one %s" % pB, [pB]), ("two %s" % pA, [pA, pA]), ("two %s" % pB, [pB, pB]), ("%s with %s" % (pA, pB), [pA, pB])]
    rows9 = []
    for lab, parts in cand:
        endur = max(mur[p]["endur"] for p in parts)
        lo, hi = env_of(parts, endur)
        tmin = lo * T9["vtmrh"][0] / T9["itimer"][2]
        tmax = hi * T9["vtmrh"][2] / T9["itimer"][0]
        rows9.append(dict(lab=lab, parts=parts, c=sum(mur[p]["c"] for p in parts), lo=lo, hi=hi, tmin=tmin, tmax=tmax,
                          start_ok=tmin >= T9["need"], soa=soa(tmax), soa_ok=soa(tmax) >= T9["pulse_a"]))
    T9["cands"] = rows9
    sel = [r for r in rows9 if r["start_ok"] and r["soa_ok"] and len(r["parts"]) <= CAP_STACK_PARTS]
    if [r["lab"] for r in sel] != ["%s with %s" % (pA, pB)]:
        refuse(4, "the stocked C0G sets meeting both ends are %s, not the one this record selects" % [r["lab"] for r in sel])
    S = sel[0]
    T9["sel"] = S
    T9["sel_codes"] = (code_of[pA], code_of[pB])
    T9["sel_nom_ms"] = S["c"] * T9["vtmrh"][1] / T9["itimer"][1]
    T9["sel_extrap"] = S["tmax"] / 10e-3 - 1.0
    T9["sel_soa_m05"] = soa(S["tmax"], 0.5)
    lo, hi = env_of(S["parts"], max(mur[p]["damp"] for p in S["parts"]))
    T9["damp"] = (lo * T9["vtmrh"][0] / T9["itimer"][2], hi * T9["vtmrh"][2] / T9["itimer"][0])
    T9["damp_soa"] = soa(T9["damp"][1])
    T9["typ_basis"] = (T9["sel_nom_ms"], 1.5 * T9["start_nom"])
    T9["c5_l9"] = (100e-9 * (1 - 0.10) * (1 - 0.15) * (1 - 0.15) * T9["vtmrh"][0] / T9["itimer"][2],
                   100e-9 * hi_f * T9["vtmrh"][2] / T9["itimer"][0])
    T9["f1_i2t_start"] = E["entry"][1] ** 2 * S["tmax"]
    T9["dc_hot"] = idc * T9["derate"]
    R["T9"] = T9
    R["N"] = entry_round(R, T, L9)
    R["G"] = dependency_round(R, T)
    R["H"] = consolidation_round(R, T)
    T["arch"] = text("arch")
    R["K"] = fix_round(R, T)
    R["L"] = fix16_round(R, T)
    R["M"] = fix17_round(R, T)
    R["N18"] = fix18_round(R, T)
    R["S19"] = fix19_round(R, T)
    R["S20"] = fix20_round(R, T)
    R["S21"] = fix21_round(R, T)
    R["S22"] = fix22_round(R, T)
    R["S23"] = fix23_round(R, T)
    R["S24"] = fix24_round(R, T)
    R["S25"] = fix25_round(R, T)
    R["S26"] = fix26_round(R, T)
    R["S27"] = fix27_round(R, T)
    R["S28"] = fix28_round(R, T)
    return R


# ============================================================================================ the fix round (2 October 2026)
def soa_lines_ktt():
    """CSD19536KTT Figure 4-10 (SLPS540C p.6) read from the sheet's vector drawing by L4-E9's method (soa_lines above): the
    plot's own frame and transform, its legend order from the page text, and two anchors checked (the 400 A IDM line and the
    100 V boundary), so the 100 us, 1 ms, 10 ms and DC lines are TI's own coordinates. The plot spans 0.1 to 1000 V and A."""
    pdf = read("csd19536")
    svg = subprocess.run(["pdftocairo", "-svg", "-f", "6", "-l", "6", pdf, "-"], capture_output=True).stdout.decode("utf-8", "replace")
    tr = "matrix(0.0972764,0,0,-0.09741,67.961,231.544)"
    paths = []
    for m in re.finditer(r"<path[^>]*>", svg):
        # poppler 22 writes the stroke as a style property and "rgb(0%,0%,0%)", "matrix(a,b,...)"; poppler 24 writes a stroke
        # attribute and puts a space after each comma: the reader takes both, the path coordinates being the same
        t = re.sub(r",\s+", ",", m.group(0))
        st = re.search(r'stroke(?::|=")(rgb\([^)]*\))', t)
        if tr not in t or not st:
            continue
        pts = [(float(a), float(b)) for a, b in re.findall(r"[ML] ([-\d.]+) ([-\d.]+)", re.search(r' d="([^"]*)"', t).group(1))]
        paths.append((st.group(1), pts))
    frames = [p for c, p in paths if c == "rgb(0%,0%,0%)" and len(p) == 5 and p[0] == p[-1]]
    if not frames:
        refuse(3, "Figure 4-10's frame")
    fr = max(frames, key=lambda q: (max(a for a, _ in q) - min(a for a, _ in q)) * (max(b for _, b in q) - min(b for _, b in q)))
    x0, x1 = min(q[0] for q in fr), max(q[0] for q in fr)
    y0, y1 = min(q[1] for q in fr), max(q[1] for q in fr)
    lv = lambda x: -1.0 + 4.0 * (x - x0) / (x1 - x0)
    li = lambda y: -1.0 + 4.0 * (y - y0) / (y1 - y0)
    txt = flat(pdf_pages("csd19536", True)[5])
    if not re.search(r"DC 1 ms 10 ms 100 .s", txt):
        refuse(3, "Figure 4-10's legend text")
    labels = ["DC", "1ms", "10ms", "100us"]                           # the legend's two rows, left to right, top to bottom
    legend = sorted(((p[0][1], p[0][0], c) for c, p in paths if len(p) == 2 and p[0][1] == p[1][1] and c != "rgb(0%,0%,0%)"
                     and 10 ** lv(p[1][0]) < 2.0 and 10 ** li(p[0][1]) < 0.5), key=lambda q: (-q[0], q[1]))
    if len(legend) != 4:
        refuse(3, "Figure 4-10's legend segments")
    out = {}
    for lab, (_y, _x, col) in zip(labels, legend):
        cands = [p for c, p in paths if c == col and len(p) >= 2 and abs(10 ** lv(p[-1][0]) - 100.0) < 1.0]
        if len(cands) != 1:
            refuse(3, "Figure 4-10's %s line" % lab)
        out[lab] = [(lv(x), li(y)) for x, y in cands[0]]
    tops = [10 ** max(y for _x, y in v) for k, v in out.items() if k != "DC"]
    if any(abs(t - 400.0) > 4.0 for t in tops):
        refuse(3, "Figure 4-10's IDM line")
    return out


def soa_t(lines, vds, t):
    """The line's current at vds for a pulse of t s: log-log between the printed lines in time; under the shortest line its
    value (a longer pulse's, so lower); past 10 ms the power law of the last two lines carried (L4-E9's method)."""
    ts = sorted(lines)
    val = lambda k: soa_at(lines[k], vds) if math.log10(vds) >= lines[k][0][0] else 10 ** lines[k][0][1]
    if t <= ts[0]:
        return val(ts[0])
    for a, b in zip(ts, ts[1:]):
        if a <= t <= b:
            ia, ib = val(a), val(b)
            return 10 ** (math.log10(ia) + (math.log10(ib) - math.log10(ia)) * (math.log10(t) - math.log10(a)) / (math.log10(b) - math.log10(a)))
    ia, ib = val(ts[-2]), val(ts[-1])
    return ib * (ts[-1] / t) ** (math.log10(ia / ib) / math.log10(ts[-1] / ts[-2]))


def fault_scan(lines, vin, s, c, ioc, isc, toc, tau, tsc, derate):
    """A start into a resistive fault Rf under gate-slew inrush and a circuit breaker (no power limit). The output follows the
    gate at the slew s (V/s): the FET carries c x s plus Vout / Rf with VIN - Vout across it until Vout reaches VIN (then it is
    fully on and VIN / Rf flows at a small VDS). The breaker acts on two paths: the overcurrent comparator, whose delay toc
    (TI's row, loaded) runs while the current stays over ioc; the short-circuit comparator, which sees the sense voltage through
    the RISCP x CSCP filter (first order, time constant tau) and then turns the FET off within tsc (TI's loaded propagation).
    The current keeps following its trajectory through every delay. Every point of the pulse is held against the chart for the
    WHOLE pulse's duration (conservative: no thermal-impedance superposition). Returns the worst ratio of current to the derated
    line, its Rf, its duration and which path ended it."""
    worst = (0.0, None, None, None)
    for k in range(241):
        rf = 10 ** (-1.0 + 4.0 * k / 240)
        i0, a, tf, iend = c * s, s / rf, vin / s, vin / rf
        t_oc = None
        if i0 >= ioc:
            t0 = 0.0
        elif i0 + a * tf >= ioc:
            t0 = (ioc - i0) / a
        else:
            t0 = None
        if t0 is not None and (t0 + toc <= tf or iend >= ioc):
            t_oc = t0 + toc
        filt = lambda x: i0 * (1 - math.exp(-x / tau)) + a * (x - tau * (1 - math.exp(-x / tau)))
        ftf, t1 = filt(tf), None
        if ftf >= isc:
            lo_, hi_ = 0.0, tf
            for _ in range(80):
                mid = 0.5 * (lo_ + hi_)
                lo_, hi_ = (lo_, mid) if filt(mid) >= isc else (mid, hi_)
            t1 = hi_
        elif iend > isc:
            t1 = tf + tau * math.log((iend - ftf) / (iend - isc))
        t_sc = None if t1 is None else t1 + tsc
        ends = [(x, how) for x, how in ((t_oc, "the overcurrent delay"), (t_sc, "the short-circuit trip")) if x is not None]
        t_off, how = min(ends) if ends else (None, "the start completes")
        t_end = tf if t_off is None or t_off >= tf else t_off
        if t_off is not None and t_off >= tf:
            how = "the start completes, then %s" % how
        r = 0.0
        for jj in range(121):
            x = t_end * jj / 120
            vds = vin - s * x
            if vds < 2.2:
                continue
            r = max(r, (i0 + a * x) / (derate * soa_t(lines, vds, t_end)))
        if r > worst[0]:
            worst = (r, rf, t_end, how)
    return worst


def start_into_short(lines, vin, a_g, isc, tau, tsc, derate):
    """A start into a hard short: VDS stays at VIN and the drain current follows the gate at a_g (A/s, the transconductance
    times the gate slew) from the threshold; the filtered sense reaches isc, then tsc. Returns the peak, the pulse and the ratio
    to the derated chart at that pulse."""
    g = lambda x: a_g * (x - tau * (1 - math.exp(-x / tau)))
    lo_, hi_ = 0.0, isc / a_g + 10 * tau
    for _ in range(80):
        mid = 0.5 * (lo_ + hi_)
        lo_, hi_ = (lo_, mid) if g(mid) >= isc else (mid, hi_)
    tp = hi_ + tsc
    ip = a_g * tp
    return ip, tp, ip / (derate * soa_t(lines, vin, tp))


def red2_model():
    """hc2's pwr_red2.py with rv-pwr's pwr_budget.py, both pinned, imported as hc2 imports them: its own printing discarded."""
    read("red2_py")
    read("budget_py")
    import contextlib
    import importlib.util
    import io
    spec = importlib.util.spec_from_file_location("pwr_red2_for_l4e11", os.path.join(TOP, PINS["red2_py"][0]))
    mod = importlib.util.module_from_spec(spec)
    argv = sys.argv
    sys.argv = [os.path.join(TOP, PINS["red2_py"][0]), os.path.join(TOP, PINS["budget_py"][0])]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    return mod


def entry_round(R, T, L9):
    """B1 to B5 of the focused check (cx30, 2 October 2026): the entry at a 9.00 V plug, the source envelope with the kit's own
    losses, the weak-source envelope as monotone intervals, the charge bounds. Every figure carries its class."""
    B, P, E, D, F, T9 = R["B"], R["P"], R["E"], R["D"], R["F"], R["T9"]
    N = {}
    l69 = flat("".join(pdf_pages("lm5069", True)))
    ge, ga = T["gen_e"], T["gen_a"]
    # ---- B1: the drawn LM5069 at a 9.00 V plug (SNVS452G)
    m = need(l69, r"PORIT VIN increasing ([\d.]+) ([\d.]+) V VIN to trigger insertion timer Power-On reset threshold at POREN VIN increasing ([\d.]+) ([\d.]+) V VIN to enable all functions POREN-HYS POREN hysteresis VIN decreasing (\d+) mV", "PORIT and POREN")
    N["porit"], N["poren"], N["poren_hys"] = (f(m, 1), f(m, 2)), (f(m, 3), f(m, 4)), f(m, 5) * 1e-3
    N["vin_range"] = (f(need(l69, r"Wide operating range: (\d+) V to (\d+) V", "the operating range"), 1), 80.0)
    need(l69, r"VCL Threshold voltage VIN-SENSE voltage", "VIN as the sense reference")
    need(ge, r'ic\("U6", 10, "LM5069MM-2 hot-swap controller: [^"]*", "VSSOP10", \{"1": "HS_S", "2": "DC_P"', "U6's VIN on DC_P")
    lm7 = flat("".join(pdf_pages("lm74700", True)))
    m = need(lm7, r"V\(AK REG\) Regulated Forward V\(AK\) Threshold (\d+) (\d+) (\d+) mV", "LM74700 V(AK REG)")
    N["vak"] = (f(m, 1) * 1e-3, f(m, 2) * 1e-3, f(m, 3) * 1e-3)
    N["vin_ic_max"] = PLUG_V - N["vak"][0]                       # before the hot swap conducts, nothing larger than this reaches VIN
    N["poren_met"] = N["vin_ic_max"] >= N["poren"][1]
    # the UVLO by Equations 38 to 40: falling UVLOTH (1 + R20/R21); rising that plus UVLOHYS x R20
    uv, hy, r20 = E["uv_rows"], E["hy_rows"], E["r20"]
    def uvlo(r21x, tol=0.01):
        fall = (uv[0] * (1 + r20 * (1 - tol) / (r21x * (1 + tol))), uv[1] * (1 + r20 / r21x), uv[2] * (1 + r20 * (1 + tol) / (r21x * (1 - tol))))
        rise = (fall[0] + hy[0] * r20 * (1 - tol), fall[1] + hy[1] * r20, fall[2] + hy[2] * r20 * (1 + tol))
        return rise, fall
    need(l69, r"VUVH = 2\.5V \+ \[R1 x \(2\.5V \+ 21 .A\)\]", "Equation 38")
    N["uvlo_drawn"] = uvlo(E["r21"])
    N["uvlo_withdrawn"] = uvlo(42.2e3)
    # ---- the kit's own series resistance, hot and cold (each element's class named in the output)
    cold_f = 1 + CU_ALPHA * (T_COLD - 20.0)
    N["c12_r"] = D["c12_mv"] * 1e-3 / D["c12"]
    xt = flat(pdf_pages("xt60", True)[0])
    N["xt60_r"] = f(need(xt, r"接触电阻 ([\d.]+)mΩ", "XT60 contact resistance")) * 1e-3
    N["loop_floor20"] = D["vmax"] / (I_PF_TARGET * cold_f)          # the loop's actual floor at 20 C (copper and contacts)
    N["loop_floor_cold"] = N["loop_floor20"] * cold_f
    N["i_pf_spec"] = D["vmax"] / N["loop_floor_cold"]
    N["u_meas"] = U_MEAS + CU_ALPHA * DT_MEAS
    N["acc"] = (N["loop_floor20"] * (1 + N["u_meas"]), LOOP_CEIL20 / (1 + N["u_meas"]))   # the measured value's acceptance window
    N["loop_ceil20"] = LOOP_CEIL20
    N["cu_nom20"] = (2 * SEL_CABLE_M + 2 * LEAD_M) * CU_RHO_20 / SEL_MM2
    N["contacts_max"] = 2 * N["c12_r"] + 2 * N["xt60_r"]
    N["constr"] = (N["cu_nom20"], N["cu_nom20"] + N["contacts_max"])
    if not (N["acc"][0] < N["constr"][0] and N["constr"][1] < N["acc"][1]):
        refuse(4, "the selected construction does not sit inside the measured window")
    N["min_len_floor"] = (N["loop_floor20"] * SEL_MM2 / CU_RHO_20 - 2 * LEAD_M) / 2.0
    out_share = SEL_CABLE_M / (SEL_CABLE_M + LEAD_M)
    N["hot_f"] = out_share * (1 + CU_ALPHA * (T_OUT_HOT - 20.0)) + (1 - out_share) * (1 + CU_ALPHA * (F["air_hot"] - 20.0))
    N["cable_hot"] = N["loop_ceil20"] * N["hot_f"]
    fz = flat("".join(pdf_pages("fuse997", True)))
    m = need(fz, r"0997010_ 10 1 (\d+) ([\d.]+) (\d+)", "the 0997010 drop")
    N["f1_hot"] = f(m, 1) * 1e-3 / 10.0
    N["q1_rds"] = f(need(ge, r'"BSC039N06NS 60 V ([\d.]+) mOhm N-FET', "Q1's RDS(on)")) * 1e-3
    kt = flat("".join(pdf_pages("csd19536", True)))
    m = need(kt, r"VGS = 10V, ID = 100A ([\d.]+) ([\d.]+)", "CSD19536KTT RDS(on)")
    N["q7_rds"] = f(m, 2) * 1e-3
    m = need(kt, r"Qg Gate charge total \(10V\) (\d+) (\d+) nC", "CSD19536KTT Qg")
    N["q7_qg"] = f(m, 2) * 1e-9
    N["q7_tj"] = f(need(kt, r"Operating Junction, \S55 to (\d+) \S?C", "CSD19536KTT TJ"))
    srf = flat(pdf_pages("srf1260", True)[0])
    m = need(srf, r"SRF1260-1R0Y 1\.0 ±30 ([\d.]+) ([\d.]+) ([\d.]+) 4 ±30 ([\d.]+) ([\d.]+) ([\d.]+)", "SRF1260-1R0Y's row")
    N["l2_dcr"], N["l2_irms"] = f(m, 4), f(m, 5)
    # ---- the candidates' rows (held TI sheets)
    t63 = flat("".join(pdf_pages("tps1663", True)))
    N["t63_range"] = (f(need(t63, r"Operating voltage: ([\d.]+)V to (\d+)V", "TPS1663 range"), 1), f(need(t63, r"Operating voltage: ([\d.]+)V to (\d+)V", "TPS1663 range"), 2))
    N["t63_abs"] = f(need(t63, r"Absolute maximum: (\d+)V", "TPS1663 absolute"))
    m = need(t63, r"R\(ILIM\) = 3k\S*\s+V\(IN\) \S V\(OUT\) = 1V ([\d.]+) ([\d.]+) ([\d.]+) A", "TPS1663 at 3k")
    N["t63_ilim"] = (f(m, 1), f(m, 2), f(m, 3))
    t48 = flat("".join(pdf_pages("tps4811", True)))
    rows = lambda pat, what, n=3: tuple(f(need(t48, pat, what), i) for i in range(1, n + 1))
    N["t48_vs"] = rows(r"V\(VS\) Operating input voltage ([\d.]+) ([\d.]+) V", "VS range", 2)
    N["t48_abs"] = f(need(t48, r"3\.5V to 80V input range \((\d+)V absolute maximum\)", "TPS4811 absolute"))
    N["t48_por"] = rows(r"V\(VS_PORR\) VS POR threshold, rising ([\d.]+) ([\d.]+) ([\d.]+) V", "VS POR")
    N["t48_uvr"] = rows(r"V\(UVLOR\) UVLO threshold voltage, rising ([\d.]+) ([\d.]+) ([\d.]+) V", "UVLOR")
    N["t48_uvf"] = rows(r"V\(UVLOF\) UVLO threshold voltage, falling ([\d.]+) ([\d.]+) ([\d.]+) V", "UVLOF")
    N["t48_enleak"] = f(need(t48, r"I\(EN/UVLO\) Enable input leakage current V\(EN/UVLO\) = 12V (\d+) (\d+) nA", "EN leakage"), 2) * 1e-9
    N["t48_ovr"] = rows(r"V\(OVR\) Overvoltage threshold input, ris[Ii]ng ([\d.]+) ([\d.]+) ([\d.]+) V", "OVR")
    N["t48_ovf"] = rows(r"V\(OVF\) Overvoltage threshold input, falling ([\d.]+) ([\d.]+) ([\d.]+) V", "OVF")
    N["t48_ovleak"] = f(need(t48, r"I\(OV\) OV Input leakage current 0V < V\(OV\) < 5V (\d+) (\d+) nA", "OV leakage"), 2) * 1e-9
    N["t48_cp_on"] = rows(r"Charge Pump Turn ON voltage ([\d.]+) ([\d.]+) ([\d.]+) V", "charge pump on")
    N["t48_cp_off"] = rows(r"Charge Pump Turn OFF voltage ([\d.]+) ([\d.]+) ([\d.]+) V", "charge pump off")
    m = need(t48, r"RSET = 100 ., RIWRN = 39\.7k. ([\d.]+) ([\d.]+) ([\d.]+) mV", "the OCP row at 39.7k")
    N["t48_wrn"] = (f(m, 1) * 1e-3, f(m, 2) * 1e-3, f(m, 3) * 1e-3)
    N["t48_iscp"] = tuple(x * 1e-6 for x in rows(r"I\(ISCP\) SCP Input Bias current ([\d.]+) ([\d.]+) ([\d.]+) .A", "ISCP bias"))
    need(t48, r"\u2212 464", "Equation 11's offset")
    N["t48_tmr_i"] = tuple(x * 1e-6 for x in rows(r"I\(TMR_SRC_CB\) TMR source current ([\d.]+) ([\d.]+) ([\d.]+) .A", "TMR source"))
    N["t48_tmr_v"] = rows(r"V\(TMR_OC\) ([\d.]+) ([\d.]+) ([\d.]+) V", "TMR threshold")
    m = need(t48, r"tSC Short-circuit protection propagation \S+ \S \S+ \S V\(SNS_SCP\) to PD \S, (\d+) (\d+) \Ss Delay CL = 47nF, TPS48110\SQ1 Only", "tSC of the TPS48110")
    N["t48_tsc"] = (f(m, 1) * 1e-6, f(m, 2) * 1e-6)
    m = need(t48, r"Over current protection delay (\d+) (\d+) \Ss = 47nF, CTMR = 0nF tOC .{0,80}?Over current protection delay (\d+) \Ss = 47nF, CTMR = 22nF", "tOC's rows")
    N["t48_toc0"], N["t48_toc22"] = (f(m, 1) * 1e-6, f(m, 2) * 1e-6), f(m, 3) * 1e-6
    need(t48, r"0\.63 \u00d7 V BST \u2212 SRC \u00d7 CLOAD", "Equation 3")
    need(t48, r"tRETRY = 22\.7 \u00d7 106 \u00d7 CTMR", "Equation 9")
    need(t48, r"After 32 charging, discharging cycles", "the auto-retry count")
    N["t48_inp_h"] = f(need(t48, r"V\(INP_H\) ([\d.]+) ([\d.]+) V", "INP high"), 2)
    N["t48_pin_abs"] = f(need(t48, r"Input Pins OV, EN/UVLO, INP, INP_G, FLT_I , FLT_T to GND \S1 (\d+)", "the input pins' maximum"))
    need(t48, r"TI recommends RVS value around 100\u03a9", "TI's VS filter")
    need(t48, r"add filter capacitor of 1nF \(CSCP\)", "TI's CSCP")
    need(t48, r"External VS to GND 22 nF Capacitor BST to SRC 0\.1 .F", "the external capacitors")
    # ---- the in-service current at a 9.00 V plug, the knee and the functional state (B3)
    st = E["states"]
    rd = T["red2"]
    m = need(rd, r'"PS-SURV \(slot 2 alone\)": \{\s+"battery_W_lo": ([\d.]+),\s+"battery_W_plan": ([\d.]+),\s+"battery_W_hi": ([\d.]+)', "PS-SURV slot 2 alone")
    surv = (f(m, 1), f(m, 2), f(m, 3))
    m1 = need(rd, r'"PS-IDLE-SPEC, link cards held off": \{\s+"battery_W_plan": ([\d.]+)', "the idle without the heater")
    N["heater_w"] = st["PS-IDLE-SPEC cold, heater on"][1] - f(m1)
    N["surv"] = surv
    M2 = red2_model()
    pbm = M2.pb
    if [round(pbm.state_full("RED", s_, M2.SURV)["pb"], 2) for s_ in ("lo", "plan", "hi")] != list(surv):
        refuse(4, "the budget model does not reproduce pwr_red2.out's PS-SURV")
    shed = dict(M2.SURV)
    names = {nm for (nm, _nd, _v, _s) in pbm.LOADS}
    for k_ in SHED_OFF:
        if k_ not in names:
            refuse(3, "the budget has no load %r" % k_)
        shed[k_] = pbm.OFF
    heat_ov = {**shed, M2.HEATER: M2.HEAT_REG}
    N["shed_held"] = [(k_, tuple(M2.SURV[k_][:3]) if k_ in M2.SURV else tuple(next(v for (nm, _nd, v, _s) in pbm.LOADS if nm == k_)["RED"][:3])) for k_ in SHED_OFF]
    N["shed"] = tuple(pbm.state_full("RED", s_, shed)["pb"] for s_ in ("lo", "plan", "hi"))
    N["func"] = tuple(pbm.state_full("RED", s_, heat_ov)["pb"] for s_ in ("lo", "plan", "hi"))
    fh = pbm.state_full("RED", "plan", heat_ov)
    N["func_heat_in"] = fh["pb"] - fh["outside"] + pbm.pack_i2r(fh["pb"])
    N["g_cold"] = tuple(pbm.G_3253["open_fans"])
    N["air_m20"] = (-20.0 + N["func_heat_in"] / N["g_cold"][1], -20.0 + N["func_heat_in"] / N["g_cold"][0])
    l5 = T["l4e5"]
    N["knee_slope"] = f(need(l5, r"The knee's slope at the pin is ([\d.]+) V/V", "the knee's slope"))
    m = need(l5, r"zero-current target, the pin at 1\.0 V .*?: VIN_RAW ([\d.]+) V \(([\d.]+) to ([\d.]+) V\)", "the knee's zero band")
    N["knee_tol"] = (f(m, 3) - f(m, 2)) / 2.0 / f(m, 1)
    gain = 40 * 0.010                                             # V/A at the pin with R16 10 mOhm (SLUSE66A p.6, RECORD L4-E5)
    def band(it):                                                 # U3's board current at a pin target it (INFERRED, L4-E5's components)
        pin = 1.0 + gain * it
        return ((it - PIN_ERR - NET_TOL * pin / gain) / (1 + E["r16_tol"]), (it + PIN_ERR + NET_TOL * pin / gain) / (1 - E["r16_tol"]))
    N["band"] = band
    need_lo = N["func"][1] / (E["vb_low"] * E["eta_u3"])
    N["it_need"] = (need_lo * (1 + E["r16_tol"]) + PIN_ERR + NET_TOL / gain) / (1 - NET_TOL)
    if KNEE_IT < N["it_need"]:
        refuse(4, "the knee's flat target %s A is under the functional state's need %s A" % (KNEE_IT, N["it_need"]))
    N["it_band"] = band(KNEE_IT)
    line = lambda v: E["slope"] / gain * v
    N["v_join"] = KNEE_IT / (E["slope"] / gain)
    def target(v):                                                # the corrected H3 shape: the line above v_join, flat to KNEE_TOP, the knee below
        if v >= N["v_join"]:
            return line(v)
        if v >= KNEE_TOP:
            return KNEE_IT
        return max(0.0, KNEE_IT - (KNEE_TOP - v) * N["knee_slope"] / gain)
    N["target"] = target
    N["v_zero"] = KNEE_TOP - KNEE_IT * gain / N["knee_slope"]
    N["v_hiz_in"] = N["v_zero"] - (1.0 - 0.4) / N["knee_slope"]
    N["v_hiz_out"] = N["v_zero"] - (1.0 - 0.8) / N["knee_slope"]
    N["hiz_certain"] = N["v_hiz_in"] * (1 - N["knee_tol"])
    N["top_max"] = KNEE_TOP * (1 + N["knee_tol"])
    # ---- the selected entry's settings (SESSION, ENTRY): thresholds and bands
    en = ENTRY
    rs_lo = en["rsns"] * (1 - 0.01) * (1 + en["rsns_tcr"] * (T_COLD - 25.0))
    rs_hi = en["rsns"] * (1 + 0.01) * (1 + en["rsns_tcr"] * (75.0 - 25.0))
    N["rs"] = (rs_lo, rs_hi)
    w0 = N["t48_wrn"][0] * (1 - 2 * en["prec"] - en["drift"]); w2 = N["t48_wrn"][2] * (1 + 2 * en["prec"] + en["drift"])
    N["ioc"] = (w0 / rs_hi, N["t48_wrn"][1] / en["rsns"], w2 / rs_lo)
    N["isc"] = (N["t48_iscp"][0] * (en["riscp"] * 0.99 + 464.0) / rs_hi, N["t48_iscp"][1] * (en["riscp"] + 464.0) / en["rsns"],
                N["t48_iscp"][2] * (en["riscp"] * 1.01 + 464.0) / rs_lo)
    mur = T9["mur"]
    any_m = next(iter(mur.values()))
    c_lo = en["ctmr"] * (1 - 0.05) * (1 - any_m["endur"]) * (1 - any_m["ta_dn"])
    c_hi = en["ctmr"] * (1 + 0.05) * (1 + any_m["endur"]) * (1 + any_m["ta_up"])
    if abs(en["ctmr"] - 22e-9) > 1e-12:
        refuse(4, "CTMR is not TI's characterised 22 nF")
    N["toc_eq7"] = (N["t48_tmr_v"][0] * c_lo / N["t48_tmr_i"][2], N["t48_tmr_v"][1] * en["ctmr"] / N["t48_tmr_i"][1], N["t48_tmr_v"][2] * c_hi / N["t48_tmr_i"][0])
    N["toc_k"] = N["t48_toc22"] / N["toc_eq7"][1]             # TI's loaded row over Equation 7 at the same capacitor
    N["toc"] = (N["toc_eq7"][0], N["t48_toc22"], max(N["toc_eq7"][2] * N["toc_k"], N["toc_eq7"][2] + N["t48_toc22"] - N["toc_eq7"][1]))
    N["tau"] = (en["riscp"] * 0.99 * en["cscp"] * 0.95 * (1 - any_m["endur"]) * (1 - any_m["ta_dn"]), en["riscp"] * en["cscp"],
                en["riscp"] * 1.01 * en["cscp"] * 1.05 * (1 + any_m["endur"]) * (1 + any_m["ta_up"]))
    N["q7_ceq"] = N["q7_qg"] / 12.0                               # Q7's gate charge as a capacitor at the 12 V drive
    N["filt_14"] = -N["tau"][1] * math.log(1 - N["isc"][2] / 14.0)   # the check's example: a 14 A step against the highest threshold
    N["tretry"] = 22.7e6 * en["ctmr"]
    def div(top, bot, th, leak, tol=0.01):
        lo = th[0] * (1 + top * (1 - tol) / (bot * (1 + tol)))
        nom = th[1] * (1 + top / bot)
        hi = th[2] * (1 + top * (1 + tol) / (bot * (1 - tol))) + leak * top * (1 + tol)
        return lo, nom, hi
    N["uv_rise"] = div(en["uv_top"], en["uv_bot"], N["t48_uvr"], N["t48_enleak"])
    N["uv_fall"] = div(en["uv_top"], en["uv_bot"], N["t48_uvf"], N["t48_enleak"])
    N["ov_rise"] = div(en["ov_top"], en["ov_bot"], N["t48_ovr"], N["t48_ovleak"], en["prec"])
    N["ov_fall"] = div(en["ov_top"], en["ov_bot"], N["t48_ovf"], N["t48_ovleak"], en["prec"])
    N["cs101_peak"] = 36.0 + f(need(L9, r"9 to 36 V in service, CS101's ([\d.]+) V peak on it under M2", "CS101's peak"))
    m = need(L9, r"D10 SMCJ40CA breakdown ([\d.]+) V minimum either way at 25 C, ([\d.]+) V at -20 C", "D10's breakdown")
    N["d10"] = (f(m, 1), f(m, 2))
    N["inp_ratio"] = (en["inp_bot"] * 0.99 / (en["inp_top"] * 1.01 + en["inp_bot"] * 0.99), en["inp_bot"] * 1.01 / (en["inp_top"] * 0.99 + en["inp_bot"] * 1.01))
    N["inp_on_at"] = N["t48_inp_h"] / N["inp_ratio"][0]
    N["clamp"] = 64.5
    N["pins_at_clamp"] = (N["clamp"] * N["inp_ratio"][1], N["clamp"] * en["uv_bot"] / (en["uv_top"] + en["uv_bot"]), N["clamp"] * en["ov_bot"] / (en["ov_top"] + en["ov_bot"]))
    vbst = (N["t48_cp_on"][0], N["t48_cp_off"][2])
    c1_lo = en["c1"] * 0.95 * (1 - any_m["endur"]) * (1 - any_m["ta_dn"]); c1_hi = en["c1"] * 1.05 * (1 + any_m["endur"]) * (1 + any_m["ta_up"])
    N["slew"] = (0.63 * vbst[0] / (en["r1"] * 1.01 * c1_hi), 0.63 * 12.0 / (en["r1"] * en["c1"]), 0.63 * vbst[1] / (en["r1"] * 0.99 * c1_lo))
    hi_f = (1 + T9["x7r"][0]) * (1 + T9["x7r"][1]) * (1 + T9["x7r"][2])
    lo_f = (1 - T9["x7r"][0]) * (1 - T9["x7r"][1]) * (1 - T9["x7r"][2])
    N["c_load"] = (T9["c_uf"] * 1e-6 * lo_f, T9["c_uf"] * 1e-6, T9["c_uf"] * 1e-6 * hi_f)
    N["inrush"] = (N["c_load"][0] * N["slew"][0], N["c_load"][1] * N["slew"][1], N["c_load"][2] * N["slew"][2])
    N["t_start"] = D["vmax"] / N["slew"][0]
    N["cbst_need"] = N["q7_qg"] / 1.0 + 10 * c1_hi
    # ---- the series resistance from the plug, hot (the in-service maximum) and its elements
    N["r_l2_hot"] = N["l2_dcr"] * (1 + CU_ALPHA * (F["air_hot"] + 40.0 * (N["ioc"][2] / N["l2_irms"]) ** 2 - 20.0))
    N["r_plug_dcp"] = [("the measured loop at its actual ceiling %s mOhm at 20 C (the cable, the D38999 pair, the inside lead, J_DCIN), %s m outside at %s C and %s m inside at %s C"
                        % (fmt(LOOP_CEIL20 * 1e3, 1), fmt(2 * SEL_CABLE_M, 1), fmt(T_OUT_HOT, 0), fmt(2 * LEAD_M, 1), fmt(F["air_hot"], 1)), N["cable_hot"], "SESSION ceiling, INFERRED"),
                       ("the NATO plug's pair, taken as a size 12 contact each (%s mV at %s A)" % (fmt(D["c12_mv"], 0), fmt(D["c12"], 0)), 2 * N["c12_r"], "ASSUMPTION"),
                       ("F1 at its rated current (typical drop)", N["f1_hot"], "MAKER"),
                       ("F1's holder, two clips", HOLDER_R, "ASSUMPTION"),
                       ("Q1 (BSC039N06NS) hot", N["q1_rds"] * FET_HOT, "NETLIST x ASSUMPTION")]
    N["r_dcp_vin"] = [("R19 4.5 mOhm at +1 %% and %s ppm/K at 75 C" % fmt(en["rsns_tcr"] * 1e6, 0), rs_hi, "CATALOGUE"),
                      ("Q7 (CSD19536KTT) hot", N["q7_rds"] * FET_HOT, "MAKER x ASSUMPTION"),
                      ("L2 (SRF1260-1R0Y series DCR) at the air plus its rise at the breaker's maximum", N["r_l2_hot"], "MAKER, INFERRED"),
                      ("board E's and board A's copper and the dock's VIN_RAW pins", BOARD_R, "ASSUMPTION")]
    N["r1_hot"] = sum(x for _n, x, _c in N["r_plug_dcp"])
    N["r2_hot"] = sum(x for _n, x, _c in N["r_dcp_vin"])
    N["r_hot"] = N["r1_hot"] + N["r2_hot"]
    pw_hi = lambda it: (band(it)[1] + E["oth"]) * E["vb_top"] / E["eta_fe"]
    def settle(vplug, rr, fe_power):                               # VIN_RAW where the plug, the resistance and a constant input power meet
        disc = vplug ** 2 - 4 * rr * fe_power(vplug)
        if disc <= 0:
            return None
        v = (vplug + math.sqrt(disc)) / 2.0
        for _ in range(60):
            disc = vplug ** 2 - 4 * rr * fe_power(v)
            v = (vplug + math.sqrt(max(disc, 0.0))) / 2.0
        return v
    N["vin9"] = settle(PLUG_V, N["r_hot"], lambda v: pw_hi(target(v)))
    N["i9"] = (PLUG_V - N["vin9"]) / N["r_hot"]
    N["dcp9"] = PLUG_V - N["i9"] * N["r1_hot"]
    N["ioc_margin"] = N["ioc"][0] / N["i9"] - 1.0
    N["pout9"] = (band(target(N["vin9"]))[1] + E["oth"]) * E["vb_top"]
    N["eta_floor"] = N["pout9"] / (N["ioc"][0] * (PLUG_V - N["ioc"][0] * N["r_hot"]))
    N["i_at_eta"] = lambda eta: (PLUG_V - math.sqrt(PLUG_V ** 2 - 4 * N["r_hot"] * N["pout9"] / eta)) / (2 * N["r_hot"])
    if abs(N["i_at_eta"](N["eta_floor"]) - N["ioc"][0]) > 1e-9 or abs(N["i_at_eta"](E["eta_fe"]) - N["i9"]) > 1e-6:
        refuse(4, "the coupled efficiency floor does not reproduce the trip and the operating point")
    N["fix_pout"] = (band(FIX_KNEE_IT)[1] + E["oth"]) * E["vb_top"]
    N["fix_eta"] = N["fix_pout"] / (N["ioc"][0] * (PLUG_V - N["ioc"][0] * FIX_RLOOP))
    N["fix_i"] = (PLUG_V - math.sqrt(PLUG_V ** 2 - 4 * FIX_RLOOP * N["fix_pout"] / round(N["fix_eta"], 6))) / (2 * FIX_RLOOP)
    i_tr = N["ioc"][0]
    N["board_at_trip"] = E["eta_fe"] * i_tr * (PLUG_V - i_tr * N["r_hot"]) / E["vb_top"] - E["oth"]
    N["board_excess"] = N["board_at_trip"] - band(target(N["vin9"]))[1]
    N["r19_f1"] = w2 / (F["f_hot_a"] * 0.99 * (1 + en["rsns_tcr"] * (T_COLD - 25.0)))
    N["trip_min_r19_f1"] = w0 / (N["r19_f1"] * 1.01 * (1 + en["rsns_tcr"] * (75.0 - 25.0)))
    N["top_margin"] = N["vin9"] - N["top_max"]
    N["dcp_noload"] = PLUG_V - N["vak"][2]
    N["l2_rise"] = 40.0 * (N["ioc"][2] / N["l2_irms"]) ** 2
    N["q7_w"] = N["ioc"][2] ** 2 * N["q7_rds"] * FET_HOT
    # the guard (board A U34) under the new knee
    m = need(ga, r"both channels at VIT ([\d.]+) V \(([\d.]+) to ([\d.]+)\) with (\d+) percent hysteresis", "U34's VIT")
    vit = (f(m, 2), f(m, 1), f(m, 3)); hys = f(m, 4) / 100.0
    r15 = f(need(ga, r'r\("R15", "(\d+)k 1%", "FE_UVS", "GND"', "R15")) * 1e3
    r14d = f(need(ga, r'r\("R14", "(\d+)k 1%", "VIN_RAW", "FE_UVS"', "R14")) * 1e3
    def guard(r14):
        fall = (vit[0] * (1 + r14 * 0.99 / (r15 * 1.01)), vit[1] * (1 + r14 / r15), vit[2] * (1 + r14 * 1.01 / (r15 * 0.99)))
        return fall, tuple(x * (1 + hys) for x in fall)
    N["guard_drawn"], N["guard_new"] = guard(r14d), guard(GUARD_R14_K * 1e3)
    N["guard_r"] = (r14d, r15)
    N["guard_margin"] = N["hiz_certain"] - N["guard_new"][0][2]
    gaf = flat(ga.replace("#", " "))
    m = need(gaf, r"Running at the lowest UV fall: FE_VZ ([\d.]+) V, FE_RUN ([\d.]+) V \(Q36 and Q37's VGS\(th\) is ([\d.]+) V at most\), EN ([\d.]+) V", "the guard's running levels")
    k = N["guard_new"][0][0] / N["guard_drawn"][0][0]
    N["guard_levels"] = (f(m, 1) * k, f(m, 2) * k, f(m, 3), f(m, 4) * k)
    N["ven_op"] = f(need(gaf, r"VEN\(OP\) ([\d.]+) to ([\d.]+) V\)", "U2's VEN(OP)"), 2)
    # ---- the envelope at the plug with the losses (B3): low side hot, high side with no loss
    env = {}
    for v in (9.0, 12.0, 24.0, 36.0):
        lo_pw = lambda vv: (min(band(target(vv))[0], E["iin_min"]) + E["oth"]) * E["vb_low"] / E["eta_fe"]   # noqa: E731
        vr = settle(v, N["r_hot"], lo_pw)
        blo = min(band(target(vr))[0], E["iin_min"])
        bhi = min(band(target(v))[1], E["iin_max"])
        vmx = settle(v, N["r_hot"], lambda vv: (min(band(target(vv))[1], E["iin_max"]) + E["oth"]) * E["vb_top"] / E["eta_fe"])
        imx = (min(band(target(vmx))[1], E["iin_max"]) + E["oth"]) * E["vb_top"] / E["eta_fe"] / vmx
        env[v] = dict(vin_lo=vr, board_lo=blo, board_hi=bhi, w_lo=blo * E["vb_low"] * E["eta_u3"], w_hi=bhi * E["vb_top"] * E["eta_u3"], i_max=imx, vin_imax=vmx)
    N["env"] = env
    N["cls"] = {}
    for name, (lo, plan, hi) in list(st.items()) + [("the functional warm-up (one module and the heater)", N["func"])]:
        for v in env:
            e = env[v]
            N["cls"][(name, v)] = "carried at every corner" if plan <= e["w_lo"] else ("only above the minimum" if plan <= e["w_hi"] else "not carried")
    N["func_ok"] = (N["func"][1] <= env[9.0]["w_lo"], N["func"][2] <= env[9.0]["w_hi"])
    e9 = env[9.0]
    N["phases"] = []
    for lab, ld in (("P0 start: the bridge boots on slot 2 (PS-SURV)", surv), ("P1 shed: PS-SURV with %s held" % ", ".join(SHED_OFF), N["shed"]),
                    ("P2 warm-up: P1 with the regulated mat on", N["func"])):
        N["phases"].append((lab, ld, [("carried at every corner" if x <= e9["w_lo"] else ("only above the minimum" if x <= e9["w_hi"] else "not carried")) for x in ld]))
    N["surplus"] = (e9["w_lo"] - N["shed"][1], e9["w_lo"] - N["shed"][2])
    N["shed_room"] = e9["w_lo"] - N["heater_w"]
    N["func_margin"] = e9["w_lo"] - N["func"][1]
    N["imax_all"] = max(e["i_max"] for e in env.values())
    if not N["imax_all"] < N["ioc"][0] or not N["ioc"][2] <= F["f_hot_a"]:
        refuse(4, "the breaker's band does not sit between the in-service maximum and F1's hot column")
    if not (N["uv_rise"][2] < N["dcp_noload"] and N["uv_fall"][2] < N["dcp9"] and N["top_margin"] > 0 and N["guard_margin"] >= 0.1):
        refuse(4, "an entry or knee threshold does not clear the 9.00 V plug's operating point")
    # ---- the owner-question caps with the losses (B3): F1's columns at a 9.00 V plug, the auxiliary loads taken off
    def cap(ia, rr):
        vr = PLUG_V - ia * rr
        return vr, (vr * ia * E["eta_fe"] - E["oth"] * E["vb_top"]) * E["eta_u3"]
    N["r_cold"] = (N["loop_floor_cold"] + 2 * N["c12_r"] + E["f1_rcold"] + HOLDER_R + N["q1_rds"] + rs_lo + N["q7_rds"]
                   + N["l2_dcr"] * cold_f + BOARD_R)
    N["caps"] = [("F1's %s C column, %s A, the losses hot" % (fmt(F["f_col"], 0), fmt(F["f_hot_a"], 1)), F["f_hot_a"], N["r_hot"]) + cap(F["f_hot_a"], N["r_hot"]),
                 ("F1's 0 C column, %s A, the losses cold" % fmt(F["der"][0], 1), F["der"][0], N["r_cold"]) + cap(F["der"][0], N["r_cold"]),
                 ("a 15 A MINI's %s C column, %s A, the losses hot" % (fmt(F["f_col"], 0), fmt(F["der15_hot"], 0)), F["der15_hot"], N["r_hot"]) + cap(F["der15_hot"], N["r_hot"])]
    N["check_ref"] = [(ia, (PLUG_V - ia * 0.115511) * ia * E["eta_fe"] * E["eta_u3"]) for ia in (F["f_hot_a"], F["der"][0], F["der15_hot"])]
    # ---- the smaller fuse, with the tolerances shown (minor)
    m = need(fz, r"7\.5A 7\.5 ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)", "the 0997 7.5 A derating row")
    N["f75_hot"] = f(m, 6)
    vcl = T9["vcl"]
    N["f75_lm"] = N["f75_hot"] * (vcl[0] / vcl[2]) * (0.99 / 1.01)
    N["f75_tps"] = N["f75_hot"] * (w0 / w2) * (rs_lo / rs_hi)
    # ---- SOA: a start into a resistive fault under the breaker (no power limit), both FETs, the conservative whole-pulse reading
    kl = soa_lines_ktt()
    N["ktt_lines"] = kl
    k_lines = {1e-4: kl["100us"], 1e-3: kl["1ms"], 1e-2: kl["10ms"]}
    q_lines = soa_lines()
    d_lines = {1e-5: q_lines["10us"], 1e-4: q_lines["100us"], 1e-3: q_lines["1ms"], 1e-2: q_lines["10ms"]}
    N["ktt_at"] = {k: soa_at(v, D["vmax"]) for k, v in kl.items() if k != "DC"}
    scan = []
    for fet, lines in (("CSD19532Q5B (as drawn)", d_lines), ("CSD19536KTT (selected)", k_lines)):
        worst = max((fault_scan(lines, D["vmax"], s, c, N["ioc"][2], N["isc"][2], N["toc"][2], N["tau"][2], N["t48_tsc"][1], T9["derate"]) + (s, c))
                    for s in (N["slew"][0], N["slew"][2]) for c in (N["c_load"][0], N["c_load"][2]))
        start = max(c * s / (T9["derate"] * soa_t(lines, D["vmax"], D["vmax"] / s)) for s in (N["slew"][0], N["slew"][2]) for c in (N["c_load"][0], N["c_load"][2]))
        scan.append((fet, worst, start))
    N["scan"] = scan
    N["gfs"] = f(need(kt, r"gfs Transconductance VDS = 10V, ID = 100A (\d+) S", "CSD19536KTT gfs"))
    N["idm"] = f(need(kt, r"IDM Pulsed Drain Current\(1\) (\d+) A", "CSD19536KTT IDM"))
    N["a_g"] = N["gfs"] * N["slew"][2]
    N["hs_start"] = start_into_short(k_lines, D["vmax"], N["a_g"], N["isc"][2], N["tau"][2], N["t48_tsc"][1], T9["derate"])
    N["t_d"] = N["tau"][2] + N["t48_tsc"][1]                       # a ramp's filter lag bound plus the loaded propagation
    N["i_allow"] = N["idm"] * T9["derate"]
    N["v_on_max"] = N["ov_rise"][2]
    N["l_min"] = N["v_on_max"] * N["t_d"] / (N["i_allow"] - N["isc"][2])
    if not scan[1][1][0] < 1.0 or not scan[1][2] < 1.0 or not N["hs_start"][2] < 1.0:
        refuse(4, "the selected FET's fault start is not under its derated chart")
    # ---- B5: R-b's register value and its actual-current bound; the dead pack's charge
    bq = flat("".join(pdf_pages("bq25731", True)))
    m = need(bq, r"REG0x03/02\(\) = 0x0200H \S(\d+)% ([\d.]+)%", "the 0x0200 accuracy row")
    N["rb_err"] = (f(m, 1) / 100.0, f(m, 2) / 100.0)
    need(bq, r"With 5-m. sense resistor, the charger provides charge current range of 0 A to 16\.256 A, with a 128-mA step resolution", "the 5 mOhm LSB")
    need(bq, r"5-m. RSR sensing", "the accuracy rows' sense resistor")
    m = need(bq, r"resistor, VBAT above 2048 mA VSYS_MIN\((\d+)°C to REG0x03/02\(\) = 0x0400H (\d+)°C\)", "the accuracy rows' condition")
    N["rb_temp"] = (f(m, 1), f(m, 2))
    N["rb_set"] = 1.024
    N["rb_max"] = N["rb_set"] * (1 + N["rb_err"][1]) / (1 - 0.01)
    N["rb_min"] = N["rb_set"] * (1 - N["rb_err"][0]) / (1 + 0.01)
    N["q2_w"] = N["rb_max"] * P["vsd_max"]
    N["q2_rise"] = N["q2_w"] * P["rja"]
    N["q2_tj"] = F["air_hot"] + N["q2_rise"]
    N["dead_charge_w"] = N["rb_max"] * RULE_SRN_V
    N["dead_charge_w_max"] = N["rb_max"] * R["cv_max"]
    need(bq, r"Upon POR, ChargeCurrent\(\) is 0 A", "ChargeCurrent at POR")
    # ---- B4: the weak-source envelope as monotone intervals, its energies, and the elements' obligations
    tc = D["tc"]
    rating = D["rating"]
    edges = [rating * tc[1][0], rating * tc[2][0], rating * tc[3][0], rating * tc[4][0]]
    N["intervals"] = [(None, edges[0], None), (edges[0], edges[1], tc[1][2]), (edges[1], edges[2], tc[2][2]), (edges[2], edges[3], tc[3][2]), (edges[3], N["i_pf_spec"], tc[4][2])]
    N["i2t_top"] = [(lo, hi, t, (hi ** 2 * t) if t else None) for lo, hi, t in N["intervals"]]
    s_cm2 = SEL_MM2 / 100.0
    N["adiab"] = [(lo, hi, t, hi * hi * t * CU_RHO_20 * 1e-4 / (s_cm2 ** 2 * CU_CV)) for lo, hi, t in N["intervals"][2:]]
    N["contact_eq"] = [(lo, hi, t, hi * hi * t / D["c12"] ** 2) for lo, hi, t in N["intervals"][1:4]]
    m = need(fz, r"Note: The typical I2t is an average value calculated from the breaking capacity tests by using the melting time before the arcing occurs\.", "the I2t note")
    N["f1_melt"] = E["f1_i2t"]
    N["sel_ipf_cold"] = D["vmax"] / ((N["constr"][0]) * cold_f)
    return N


# ============================================================================================ the dependency round (2 October 2026)
def dependency_round(R, T):
    """The owner's instruction of 2 October 2026 (the coordinator's dependency round): each missing specification apart, the
    claim it affects, what a maker's answer and what a bench sample could establish; and the bounded fallback for VSYS's
    hold-up with no battery (E11-07, VSYS's capacitance first), sized so it does not lean on the charger's transient response."""
    B, P, E, F, N = R["B"], R["P"], R["E"], R["F"], R["N"]
    G = {}
    ga = T["gen_a"]
    # ---- the charger's regulation rows and the POR answer
    bq9 = flat(pdf_pages("bq25731", True)[8])
    need(bq9, r"REG0x05/04\(\) = 0x41A0H \S0\.5% 0\.5%", "the 16.8 V ChargeVoltage accuracy row")
    need(bq9, r"VBAT_REG_ACC regulation accuracy REG0x05/04\(\) = 0x5208H \(0°C to 85°C\)", "the ChargeVoltage rows' temperature condition")
    G["cv_acc"] = 0.005
    G["cv_min"] = B["cv4s"] * (1 - G["cv_acc"])
    G["v_floor"] = B["vsysmin4s"]
    G["heat_en_v"] = f(need(ga, r"it starts at about ([\d.]+) V \(VEN_RISE", "the heater buck's enable divider"))
    for st_ in ("SLOT_EN2", "DEV_EN", "PA_EN", "HF_EN", "POE_EN", "PD_EN"):
        need(ga, r'lm5176\("\w+", "U\d+", "VBAT", "[^"]+", "%s"' % st_, "the VBAT stage enabled by %s" % st_)
    e2e = re.sub(r"<[^>]+>", " ", open(read("e2e_por"), encoding="utf-8", errors="replace").read())
    e2e = flat(e2e)
    G["por_ma"] = f(need(e2e, r"Looks like there is a mistake in the description\. The POR value is indeed (\d+)mA", "TI's E2E answer on the POR value"))
    need(flat("".join(pdf_pages("bq25731", True))), r"Upon POR, ChargeCurrent\(\) is 0 A", "the register description's POR text")
    # ---- the kit's declared load steps (r4a's loop design, recovered by L4-E8; session targets, INFERRED there)
    ld = text("loopdesign")
    eff = lambda net: f(need(ga, r'_intent\.rail\("%s",(?:(?!_intent\.rail\().){0,600}?efficiency=([\d.]+)' % re.escape(net), "%s's declared efficiency" % net, re.S))
    steps = []
    m = need(ld, r"# S2: VBAT 10 to 16\.8 V -> ([\d.]+) V .*?29\.5 W; step (\d+) A \(a 5G burst, INFERRED\)", "the S2 step", re.S)
    steps.append(("S2 slot rail (+5V_S2, a 5G burst)", f(m, 2), f(m, 1), S2_ETA, "ASSUMPTION (+5V_DEV's declared 0.90)"))
    m2 = need(ld, r"35 W; step (\d+) A\.", "the SD step")
    steps.append(("SD device rail (+5V_DEV)", f(m2, 1), f(m, 1), eff("+5V_DEV"), "NETLIST"))
    m = need(ld, r"# PA: VBAT -> ([\d.]+) V .*?step ([\d.]+) A \(key-up of a 30 W carrier at 40 percent\)", "the PA step", re.S)
    steps.append(("PA rail (+13V8_PA, a 30 W carrier keyed)", f(m, 2), f(m, 1), eff("+13V8_PA"), "NETLIST"))
    m = need(ld, r"# HF: VBAT -> ([\d.]+) V .*?24 W; step (\d+) A\.", "the HF step", re.S)
    steps.append(("HF rail (+12V_HF)", f(m, 2), f(m, 1), eff("+12V_HF"), "NETLIST"))
    m = need(ld, r"# POE: VBAT -> ([\d.]+) V .*?step ([\d.]+) A\.", "the PoE step", re.S)
    steps.append(("PoE rail (+54V_POE)", f(m, 2), f(m, 1), eff("+54V_POE"), "NETLIST"))
    m = need(ld, r"45 W at 15 V, 15 W at 5 V; step (\d+) A\.", "the PD step")
    steps.append(("USB-C PD outlet at 15 V (PD_VPWR)", f(m, 1), 15.0, eff("PD_VPWR"), "NETLIST"))
    heat = f(need(text("red2_py"), r'HEAT_REG = same\(([\d.]+), "S"\)', "the regulated mat"))
    G["steps"] = [(nm, i, v, eta, i * v / eta, cl) for nm, i, v, eta, cl in steps] + [("the pack heater mat, regulated (on)", None, None, None, heat, "RECORD")]
    base = N["shed"][1]
    env36, env9 = N["env"][36.0]["w_lo"], N["env"][9.0]["w_lo"]
    G["admit"] = [(nm, dp, base + dp <= env36) for nm, _i, _v, _e, dp, _c in G["steps"]]
    adm = [(nm, dp) for nm, dp, ok in G["admit"] if ok]
    G["worst"] = max(adm, key=lambda x: x[1])
    # ---- the hybrid polymer parts (Panasonic ZK sheet), the diode (Diodes DS13012), the resistor (Yageo RC_L V.12)
    z1, z2 = flat(pdf_pages("zk", True)[0]), flat(pdf_pages("zk", True)[1])
    m = need(z2, r"470\s+10\.0\s+10\.2\s+10\.5\s+G\s+(\d+)\s+(\d+)\s+([\d.]+)\s+EEHZK1E471P", "the ZK 471P row")
    G["c471"], G["esr471"] = 470e-6, f(m, 2) * 1e-3
    m = need(z2, r"180\s+8\.0\s+10\.2\s+10\.5\s+F\s+(\d+)\s+(\d+)\s+([\d.]+)\s+EEHZK1V181P", "the ZK 181P row")
    G["c181"], G["esr181"] = 180e-6, f(m, 2) * 1e-3
    G["zk_tol"] = f(need(z1, r"Capacitance tolerance\s+±(\d+) %", "the ZK tolerance")) / 100.0
    G["zk_end"] = f(need(z1, r"\+125 ℃ ± 2 ℃, 4000 h, apply the rated ripple current without exceeding the rated voltage\. Capacitance change Within ±(\d+)% of the initial value", "the ZK endurance row")) / 100.0
    need(z1, r"I ≦ 0\.01 CV \(μA\)", "the ZK leakage row")
    G["zk_leak"] = 0.01 * 470 * 25 * 1e-6
    need(z1, r"Characteristics dependencies in frequency and low temperature are as small as polymer type", "the ZK low-temperature sentence")
    G["k_eff"] = (1 - G["zk_tol"]) * (1 - G["zk_end"]) * K_COLD_HYB
    dz = flat("".join(pdf_pages("b540c", True)))
    m = need(dz, r"B520C, B530C, B540C \S ([\d.]+) ([\d.]+) Forward Voltage Drop VF", "B540C VF")
    G["vf25"] = f(m, 2)
    need(dz, r"IF = 5\.0A, TA = \+25°C", "B540C VF condition")
    G["io"] = f(need(dz, r"Average Rectified Output Current IO ([\d.]+)", "B540C IO"))
    G["vf"] = G["vf25"] + VF_COLD_ADD
    yr = flat("".join(pdf_pages("yageo_rc", True)))
    need(yr, r"Each type rated power at 70", "RC_L rated at 70 C")
    G["p_rc2512"] = f(need(yr, r"RC2512=(\d)W, 2W", "RC2512's rating"))
    # ---- the hold-up arithmetic (no battery, the charger delivering only its pre-step power for T_RESP)
    G["c_can_eff"] = G["c471"] * G["k_eff"]
    G["c_bank_eff"] = BANK_N * G["c_can_eff"]
    G["v1b"] = G["cv_min"] - BANK_N * G["zk_leak"] * R_CH
    v2b = G["v_floor"] + G["vf"]
    G["v2b"] = v2b
    per = 0.5 * (G["v1b"] ** 2 - v2b ** 2) - G["vf"] * (G["v1b"] - v2b)          # J per farad delivered into VSYS
    G["e_bank"] = G["c_bank_eff"] * per
    G["c_dir_eff"] = G["c181"] * G["k_eff"]
    G["e_dir"] = 0.5 * G["c_dir_eff"] * (G["cv_min"] ** 2 - G["v_floor"] ** 2)
    G["e_tot"] = G["e_bank"] + G["e_dir"]
    G["hold"] = [(nm, dp, G["e_tot"] / dp, ok) for nm, dp, ok in G["admit"]]
    G["worst_hold"] = G["e_tot"] / G["worst"][1]
    G["cans_for"] = [(t, max(0, math.ceil((G["worst"][1] * t - G["e_dir"]) / (G["c_can_eff"] * per)))) for t in (0.25e-3, 0.5e-3, 1e-3, 2e-3, 5e-3)]
    G["i_step_floor"] = G["worst"][1] / G["v_floor"]
    # ---- inrush and placement
    G["i_ch_pk"] = R["cv_max"] / R_CH
    G["p_ch_pk"] = R["cv_max"] ** 2 / R_CH
    G["c_bank_max"] = BANK_N * G["c471"] * (1 + G["zk_tol"])
    G["tau_ch"] = R_CH * G["c_bank_max"]
    G["e_ch"] = 0.5 * G["c_bank_max"] * R["cv_max"] ** 2
    na = T["net_a"]
    def nom_uf(net):
        s = 0.0
        for ref, _p in netlist_nodes(na, net):
            if ref.startswith("C"):
                v = netlist_value(na, ref)
                mm = re.match(r"([\d.]+)(u|n)", v)
                if mm:
                    s += float(mm.group(1)) * (1.0 if mm.group(2) == "u" else 1e-3)
        return s * 1e-6
    G["c_ceramic_nom"] = nom_uf("VBAT") + nom_uf("CELL_FUSED")
    G["c_pack_side_max"] = G["c_ceramic_nom"] * 1.1 + G["c181"] * (1 + G["zk_tol"])
    pc = flat(T["primcfg"])
    m = need(pc, r"about ([\d.]+) or ([\d.]+) A \(RSNS = 1 steps of 22\.2 mV over 2 mOhm\) at about (\d+) to (\d+) us", "the image's ASCD")
    G["ascd_a"], G["ascd_us"] = f(m, 1), f(m, 3) * 1e-6
    M2 = red2_model()
    G["r_loop"] = 4 * M2.pb.R_CELL["lo"] / 3 + M2.pb.R_DIST
    G["i_conn_pk"] = 4 * 4.2 / G["r_loop"]
    G["tau_conn"] = G["r_loop"] * G["c_pack_side_max"]
    G["t_over_ascd"] = G["tau_conn"] * math.log(G["i_conn_pk"] / G["ascd_a"])
    G["t_to_1v6"] = G["c_pack_side_max"] * 1.6 / 0.5
    # ---- the 9 V plug and the warm-CUV state
    s2 = [dp for nm, _i, _v, _e, dp, _c in G["steps"] if nm.startswith("S2")][0]
    G["s9_deficit"] = base + s2 - env9
    G["s9_time"] = G["e_tot"] / G["s9_deficit"] if G["s9_deficit"] > 0 else None
    G["s2_vsys"] = P["vsys_cuv"]
    # ---- the dependency rows' figures
    G["q2_i_lim"] = (P["tj_max"] - F["air_hot"]) / (P["vsd_max"] * P["rja"])
    G["clamp_x"] = N["rb_max"] / B["iclamp"]
    G["gfs_x"] = 1.0 / N["hs_start"][2]
    G["por_w"] = G["por_ma"] * 1e-3 * P["vsd_max"]
    return G


def dep_rows(R):
    """The dependency table: one row per specification the record leaves to a maker (TI for every row but N4), with what a
    maker's answer and what a bench sample can establish. The figures are this record's; the record's table repeats the rows."""
    B, P, N, G = R["B"], R["P"], R["N"], R["G"]
    return [
        dict(id="D1", name="N1a, VSYS's DC regulation with no battery",
             missing="no row gives VSYS's regulation with no battery current: VBAT_REG_ACC +-%s %% holds for a charge voltage at 0 to 85 C (p.9); section 11 (p.92) says the system is powered through the charger; Figures 10-4 and 10-5 (p.89) are typical power-up curves of a 2-cell system without battery" % fmt(G["cv_acc"] * 100, 1),
             claim="section 2's row 'absent, or both FETs open: VSYS at ChargeVoltage' and every S4 figure of 3g and 3h (U-04 in S4 at all)",
             maker="that the voltage loop holds VSYS at ChargeVoltage with no battery current, with the +-%s %% row applying: production-wide if TI states it as a limit" % fmt(G["cv_acc"] * 100, 1),
             bench="that one unit enters and holds the mode at the conditions tried; the mode is a design behaviour, and VSYS needs only %s V against ChargeVoltage's floor %s V, a %s V margin that is large against any plausible unit spread once the mode is shown (an engineering margin)" % (fmt(G["v_floor"], 1), fmt(G["cv_min"], 3), fmt(G["cv_min"] - G["v_floor"], 3)),
             cannot="that every unit and silicon revision enters the mode, or the accuracy below 0 C, where the +-%s %% row stops" % fmt(G["cv_acc"] * 100, 1),
             method="pack absent, P1's load and the envelope's maximum on VSYS, VBUS20 from 19.1 to 21 V, VSYS on a calibrated meter at -20, 25 and 62 C ambient",
             negative="arrangement (A) does not run S4: (B), a charger with a battery FET that regulates VSYS by design (an architecture change; five records reopen)"),
        dict(id="D2", name="N1b, VSYS's load-step response with no battery",
             missing="no load-transient figure or limit for the system output (Figure 10-17, p.91, is the OTG output's)",
             claim="S4 operation through the kit's load steps (3g, R-c): the declared steps of section 10, up to %s W" % fmt(G["worst"][1], 2),
             maker="a characterised deviation and recovery, or a minimum loop bandwidth; production-wide only if TI states a limit",
             bench="one unit's deviation and recovery at the steps tried; with the bank sized for %s ms, a measured recovery of %s ms or less is a five-fold margin, large against a loop's plausible spread (L, C and gain tolerances): an engineering margin" % (fmt(T_RESP * 1e3, 1), fmt(T_RESP * 1e3 / 5, 1)),
             cannot="a recovery time bounded for every unit",
             method="pack absent, an electronic load stepping VSYS by each declared step with a 1 us edge, VSYS and the inductor current on a scope, at the three ambients",
             negative="the bank of section 10 carries the step for %s ms with no help from the charger; a longer recovery needs more cans (%s for 2 ms) or (B)" % (fmt(G["worst_hold"] * 1e3, 3), [n for t, n in G["cans_for"] if abs(t - 2e-3) < 1e-9][0])),
        dict(id="D3", name="N2 (Q-TI-3), VSYS with CHRG_INHIBIT = 1 or ChargeCurrent 0 and no battery current",
             missing="9.4.1 (p.35) lets the host end a charge by CHRG_INHIBIT or ChargeCurrent 0; 9.3.21.5 (p.34) keeps the converter operating with charge disabled only in the BATOVP paragraph; nothing states what VSYS does in either state with no battery current",
             claim="R-a's S2 row and REQ-077's hold in every state (section 4): the charger still carrying the kit while the charge is held",
             maker="the control mode with charge inhibited, production-wide (a design behaviour)",
             bench="one unit's mode with the bit set and with ChargeCurrent 0, pack absent and in S2: a deterministic logic behaviour, so one sample is strong evidence for that silicon revision",
             cannot="that no later revision changes the mode, nor how a temperature-dependent comparator moves it",
             method="the pack emulated in S2 (a supply behind a diode), the bit set and cleared under P1's load, VSYS and the switch node recorded",
             negative="REQ-077's hold cannot use the bit with this charger; ChargeCurrent 0 is tried; if both fail, (B) or a requirement change to REQ-077's acceptance (the owner's)"),
        dict(id="D4", name="N3 (Q-TI-2), whether the charger charges before any host write",
             missing="9.6.3 says the charge starts when the host writes ChargeCurrent(); the register's reset value encodes 256 mA and its description says 0 A at POR. TI's expert on E2E thread 1316778 (held) answers: the POR value is %s mA, the description is in error; 9.6.3 is not addressed" % fmt(G["por_ma"], 0),
             claim="section 2's ChargeCurrent at POR (corrected in this round), R-a's persistence after a charger POR, CONOPS's hostless %s mA" % fmt(G["por_ma"], 0),
             maker="a datasheet erratum: production-wide (a forum answer is TI's word but not a revised document)",
             bench="one unit's SRP-SRN current after POR with no host: a logic behaviour, strong for that revision",
             cannot="other revisions",
             method="no host, the pack at 3.6 V a cell, the SRP-SRN current read for 200 s after POR",
             negative="a hostless charge at %s mA is safe (inside the gauge's window; Q2's diode %s W); no hostless charge leaves a hostless kit's dead pack uncharged: a stated limitation, no change" % (fmt(G["por_ma"], 0), fmt(G["por_w"], 3))),
        dict(id="D5", name="N4, VSYS's effective capacitance at 16.884 V against TI's 50 uF",
             missing="TI states %s uF effective necessary (10.1, p.83); the fitted MLCCs' capacitance at 16.9 V of DC bias is not printed in the held Yageo CC sheet (a capacitor maker's item, not TI's)" % fmt(B["csys_uf"], 0),
             claim="N1's premise (stable regulation) and E11-07",
             maker="the capacitor makers' DC-bias curves: typical per part number, not limits",
             bench="one board's VSYS capacitance at 16.8 V of bias: a sample",
             cannot="lot-to-lot spread",
             method="an LCR meter with DC bias on the populated node, or each part number on a bias fixture",
             negative="none needed: one EEHZK1V181P on VSYS gives %s uF at its stacked worst, with no DC-bias dependence, over %s uF by design" % (fmt(G["c_dir_eff"] * 1e6, 2), fmt(B["csys_uf"], 0))),
        dict(id="D6", name="Q-TI-7, 0-V charging before the gauge's SUV check",
             missing="SLUUAQ3A 4.9: with PCHG_COMM = 1 the hardware 0-V charging circuit is enabled below the minimum operation voltage; nothing states its timing against the SUV check of 3.2.1",
             claim="R-d (the image keeps PCHG_COMM 1 and the SUV check): no cell below 1.0 V charged (Samsung)",
             maker="the gauge's sequence, production-wide",
             bench="one gauge with a cell simulator: a logic sequence, strong for that firmware and revision",
             cannot="other firmware revisions",
             method="a cell simulator at 0.8 V a cell, the charger enabled, the stack current logged from the gauge's wake",
             negative="ZVCHG Exit Threshold set to stop 0-V charging, or a precharge FET (arrangement (C)'s part) with PCHG_COMM 0"),
        dict(id="D7", name="the clamp's maximum under VSYS_MIN",
             missing="8.5 (p.10) prints the clamp under VSYS_MIN, %s mA, as typical only" % fmt(B["iclamp"] * 1000, 0),
             claim="R-b's case (iii) and Q2's diode below VSYS_MIN (section 4)",
             maker="a maximum, production-wide",
             bench="one unit's clamp current; Q2 reaches %s C only at %s A on its %s C/W, %s times the typical clamp, so a sample near typical is a large engineering margin" % (fmt(P["tj_max"], 0), fmt(G["q2_i_lim"], 3), fmt(P["rja"], 0), fmt(G["q2_i_lim"] / B["iclamp"], 2)),
             cannot="a maximum for every unit",
             method="SRN held at 11 V by a sink, ChargeCurrent 0x0200, the current read at -20, 25 and 62 C",
             negative="a maximum over %s A: Q2's copper improved, or arrangement (C)" % fmt(G["q2_i_lim"], 3)),
        dict(id="D8", name="ChargeCurrent's accuracy at 0x0200 outside 0 to 85 C, and under 0x0200",
             missing="p.10's rows hold for VBAT above VSYS_MIN at %s to %s C; no accuracy outside that range, nor for any setting under 0x0200" % (fmt(N["rb_temp"][0], 0), fmt(N["rb_temp"][1], 0)),
             claim="R-b's case (ii) and Q2's %s C (section 4, CONDITIONAL)" % fmt(N["q2_tj"], 1),
             maker="limits outside the range, production-wide",
             bench="one unit at -20 and 62 C ambient: a sample; Q2's limit %s A is %s times R-b's %s A, so a sample within about 1.3 A is an engineering margin" % (fmt(G["q2_i_lim"], 3), fmt(G["q2_i_lim"] / N["rb_max"], 2), fmt(N["rb_max"], 4)),
             cannot="production limits",
             method="as D7 with SRN at 13 V",
             negative="the charger's temperature bounded inside the row by layout (E11-22), or Q2's copper improved"),
        dict(id="D9", name="the TPS48110-Q1's overcurrent delay at CTMR 22 nF",
             missing="SLUSEE5E p.10 prints %s us typical only" % fmt(N["t48_toc22"] * 1e6, 0),
             claim="V-A08's %s ms (the nuisance margin) and the fault scan's %s ms (A11-11)" % (fmt(N["toc"][0] * 1e3, 3), fmt(N["toc"][2] * 1e3, 3)),
             maker="a minimum and a maximum over temperature, production-wide",
             bench="one unit's delay: a sample; the scan's worst fault ends on the short-circuit trip (3c), so the delay's maximum does not decide it; its minimum sets V-A08",
             cannot="the spread across units",
             method="a current step over the threshold at three temperatures, the sense step to PD timed",
             negative="V-A08's allowance re-derived on TI's minimum, or CTMR raised"),
        dict(id="D10", name="the CSD19536KTT's transconductance bound",
             missing="SLPS540C p.3 prints gfs %s S typical only" % fmt(N["gfs"], 0),
             claim="the start into a hard short (3c, %s of the derated chart)" % fmt(N["hs_start"][2], 3),
             maker="a maximum, or the transfer curve's spread",
             bench="one unit's transfer curve; the headroom (%s times) is not large against a plausible transconductance spread, so a sample is no margin" % fmt(G["gfs_x"], 3),
             cannot="a bound across units",
             method="a pulsed transfer curve at VDS 10 V, 10 to 100 A",
             negative="a slower gate slew for the start (C1 larger) or a power-limiting controller"),
    ]


def render_dependency(R, p):
    G, N, E, P, B = R["G"], R["N"], R["E"], R["P"], R["B"]
    p("9. THE DEPENDENCY ROUND: EACH MISSING SPECIFICATION, THE CLAIM IT DECIDES, WHO CAN SETTLE IT (2 October 2026)")
    p("   the held answer on the POR value: TI's expert on E2E thread 1316778: \"The POR value is indeed %smA\" (the register description's 0 A is in error) (MAKER, forum)" % fmt(G["por_ma"], 0))
    for r in dep_rows(R):
        p("   %s %s (MAKER, INFERRED)" % (r["id"], r["name"]))
        for k, lab in (("missing", "missing"), ("claim", "the claim"), ("maker", "a maker's answer would establish"), ("bench", "a bench sample could establish"),
                       ("cannot", "a bench sample cannot establish"), ("method", "the bench method"), ("negative", "if the answer is negative")):
            p("     %s: %s" % (lab, r[k]))
    p("")
    p("10. THE BOUNDED FALLBACK (E11-07, VSYS's capacitance first): A HOLD-UP THAT DOES NOT LEAN ON THE CHARGER'S TRANSIENT RESPONSE")
    p("   the criterion: with no battery (S4) VSYS sits at ChargeVoltage, at least %s V (16.8 V less TI's %s %%, p.9, MAKER), and must stay above VSYS_MIN %s V"
      % (fmt(G["cv_min"], 3), fmt(G["cv_acc"] * 100, 1), fmt(G["v_floor"], 1)))
    p("     through a step while the charger delivers only its pre-step power for %s ms (ASSUMPTION: the time the charger could take to respond;" % fmt(T_RESP * 1e3, 1))
    p("     D2's bench reading turns it into a margin); the VBAT stages' EN/UVLO pins are driven by logic (the slot, device, PA, HF, PoE and PD stages)")
    p("     and the heater buck's divider starts it at about %s V, so no VSYS divider sets a line above VSYS_MIN; A-14's assumed 10.0 V converter floor" % fmt(G["heat_en_v"], 1))
    p("     is under it too (NETLIST, INFERRED)")
    p("   the kit's declared steps (r4a's loop design, INFERRED there; efficiencies from gen_sch_a.py; the mat from hc2) at VSYS, and whether R-c's envelope")
    p("     admits each on top of P1's plan %s W at the widest source (36 V, %s W) (INFERRED):" % (fmt(N["shed"][1], 2), fmt(N["env"][36.0]["w_lo"], 2)))
    for nm, i, v, eta, dp, cl in G["steps"]:
        adm = [ok for n2, d2, ok in G["admit"] if n2 == nm][0]
        hold = [h for n2, d2, h, ok in G["hold"] if n2 == nm][0]
        src = ("%s A at %s V over %s (%s)" % (fmt(i, 1), fmt(v, 2), fmt(eta, 2), cl)) if i is not None else "%s W (%s)" % (fmt(dp, 2), cl)
        p("     %-44s %s: %s W at VSYS; %s; the fallback holds it %s ms (INFERRED)" % (nm, src, fmt(dp, 2), "admitted in S4" if adm else "not admitted in S4 (R-c holds it)", fmt(hold * 1e3, 3)))
    p("   the worst admitted step: %s, %s W, %s A at the floor (INFERRED)" % (G["worst"][0], fmt(G["worst"][1], 2), fmt(G["i_step_floor"], 3)))
    p("   THE FALLBACK (SESSION; a register row, E11-24, never applied):")
    p("     a direct can on VSYS: one Panasonic EEHZK1V181P (180 uF 35 V, F size 8.0 x 10.2 mm, ESR %s mOhm; LCSC C242139); and a hold-up bank: %d x EEHZK1E471P"
      % (fmt(G["esr181"] * 1e3, 0), BANK_N))
    p("     (470 uF 25 V, G size 10.0 x 10.2 mm, ESR %s mOhm; C242138), charged from VSYS through R_CH %s Ohm (Yageo RC2512FK-07330RL, %s W at 70 C, C137025) and"
      % (fmt(G["esr471"] * 1e3, 0), fmt(R_CH, 0), fmt(G["p_rc2512"], 0)))
    p("     discharging into VSYS through D_H, a Diodes B540C-13-F (40 V, %s A, VF at most %s V at 5 A and 25 C; C72264) (MAKER, CATALOGUE)" % (fmt(G["io"], 1), fmt(G["vf25"], 2)))
    p("   the capacitance's derating (Panasonic ZK sheet): +-%s %% tolerance, endurance within +-%s %%, no DC-bias dependence (an aluminium hybrid polymer part, its class),"
      % (fmt(G["zk_tol"] * 100, 0), fmt(G["zk_end"] * 100, 0)))
    p("     the low-temperature change not printed (\"as small as polymer type\"): %s at -20 C (ASSUMPTION); so %s of nominal at the stacked worst (MAKER, ASSUMPTION)"
      % (fmt(K_COLD_HYB, 2), fmt(G["k_eff"], 3)))
    p("   the bank: %s uF effective; it sits at %s V (the leakage, 0.01 CV uA a can, across R_CH) and gives into VSYS down to %s V (VSYS_MIN plus D_H's"
      % (fmt(G["c_bank_eff"] * 1e6, 1), fmt(G["v1b"], 3), fmt(G["v2b"], 2)))
    p("     %s V: its 25 C maximum plus %s V at -20 C, ASSUMPTION): %s mJ net of the diode; the direct can %s uF effective from %s to %s V: %s mJ;"
      % (fmt(G["vf"], 2), fmt(VF_COLD_ADD, 2), fmt(G["e_bank"] * 1e3, 2), fmt(G["c_dir_eff"] * 1e6, 2), fmt(G["cv_min"], 3), fmt(G["v_floor"], 1), fmt(G["e_dir"] * 1e3, 2)))
    p("     %s mJ in all, the MLCCs not counted (N4) (INFERRED)" % fmt(G["e_tot"] * 1e3, 2))
    p("   against the worst admitted step: %s ms of hold, over the %s ms assumed (MEETS, CONDITIONAL on T_RESP); the least cans for a hold of: %s (INFERRED)"
      % (fmt(G["worst_hold"] * 1e3, 3), fmt(T_RESP * 1e3, 1), ", ".join("%s ms %d" % (fmt(t * 1e3, 2), n) for t, n in G["cans_for"])))
    p("   size: four G cans (10.3 mm square lands, 10.5 mm tall at most), one F can, an SMC diode and a 2512: about 5.5 cm2 of board A (INFERRED)")
    p("   placement: board A, on VBAT (the charger's VSYS); board P is behind the pack's FETs, which are open in S4, so it cannot hold VSYS there (NETLIST, INFERRED);")
    p("     the height and the zone are Layer 9's (L4-E8 placed six G cans on board A's VBUS20, so the class fits the board) (INFERRED)")
    p("   inrush, the entry and F1: the bank charges through R_CH at %s mA at most, %s W at most against the resistor's %s W at 70 C (the inside air %s C), with"
      % (fmt(G["i_ch_pk"] * 1e3, 1), fmt(G["p_ch_pk"], 3), fmt(G["p_rc2512"], 0), fmt(R["F"]["air_hot"], 1)))
    p("     a time constant of %s s and %s J per full charge; the direct can charges with VSYS under the charger's own start (0.5 A until 1.6 V, 3 min allowed,"
      % (fmt(G["tau_ch"], 3), fmt(G["e_ch"], 3)))
    p("     9.3.21.8; %s ms to 1.6 V at that current); the entry's start ends before U34 releases the front end (79 ms at least), so neither the entry's"
      % fmt(G["t_to_1v6"] * 1e3, 2))
    p("     inrush nor F1's I2t changes (MEETS, INFERRED)")
    p("   inrush from the pack (S1 from cold, VSYS discharged, the discharge FET switching at once): the direct can and the MLCCs (%s uF nominal, %s uF at"
      % (fmt(G["c_ceramic_nom"] * 1e6, 1), fmt(G["c_pack_side_max"] * 1e6, 1)))
    p("     most) through the pack's least loop %s mOhm (four cells at %s mOhm over three, and pwr_budget's distribution): %s A peak, over the image's ASCD"
      % (fmt(G["r_loop"] * 1e3, 2), fmt(0.035 * 1e3, 0), fmt(G["i_conn_pk"], 1)))
    p("     %s A for %s us against its %s us delay (MEETS, INFERRED); the bank behind R_CH adds %s mA, so it cannot trip ASCD (INFERRED)"
      % (fmt(G["ascd_a"], 1), fmt(G["t_over_ascd"] * 1e6, 1), fmt(G["ascd_us"] * 1e6, 0), fmt(G["i_ch_pk"] * 1e3, 1)))
    p("   what it does not do (INFERRED):")
    p("     a step beyond the source's headroom is a deficit, not a transient: at a 9.00 V plug the slot rail's step on P1's plan leaves %s W short, which the"
      % fmt(G["s9_deficit"], 2))
    p("       fallback only delays by %s ms; R-c's measured headroom must therefore count the largest uncontrolled step of the loads P1 keeps (E11-06 measures P1's peaks)"
      % fmt(G["s9_time"] * 1e3, 2))
    p("     in S2 (a warm CUV) VSYS is the stack plus Q2's diode, %s to %s V, at A-14's assumed 10.0 V floor: no droop is left to hold, so S2 still rests on"
      % (fmt(G["s2_vsys"][0], 1), fmt(G["s2_vsys"][1], 1)))
    p("       the charger's response (D2 for S2) and on the converters' real minimum inputs (E11-08)")
    p("     it settles neither D1 (the steady mode) nor D3 (the inhibited mode): no capacitance answers what the converter regulates")
    p("")
    p("11. WHAT CHANGES FOR U-04'S CLASSIFICATION (INFERRED)")
    p("   made independent of TI by the fallback: D2 for every admitted step in S4 within the bank's %s ms (with D2's bench margin), and D5 (VSYS's" % fmt(G["worst_hold"] * 1e3, 3))
    p("     effective capacitance) by the direct can (INFERRED)")
    p("   still depending on TI: D1 (S4 at all), D3 (REQ-077's hold and R-a's S2), D4 (low consequence), D6 (the image's 0-V charging), D7 and D8 (R-b's")
    p("     cases (iii) and (ii)); and on the entry's makers: D9 and D10")
    p("   negative answers with a remedy inside arrangement (A): D4, D5, D6, D7, D8, D9, D10; with none: D1 and D3, whose negative answers return (B)")
    p("   so U-04 STAYS AN ARCHITECTURE-LEVEL CHOICE: the fallback narrows the architecture's dependence on TI from four statements (D1, D2, D3, D5) to two")
    p("     (D1, D3), but those two decide whether arrangement (A) can run on a source with no usable pack and hold a charge while carried, and no part,")
    p("     rule or capacitance inside (A) answers them; one bench sample can show the mode on that silicon revision, not a production-wide behaviour")
    p("")


# ============================================================================================ the consolidation round
EC_SKIP = re.compile(r"Copyright|Submit Document|Product Folder|SLUSE6|www\.ti\.com|^\s*BQ2573\d\s*$|Electrical Characteristics|"
                     r"VVBUS_UVLOZ <|PARAMETER|Timing Requirements|MIN\s+NOM\s+MAX")
EC_SYM = re.compile(r"^\s{0,4}([A-Z][A-Za-z0-9_]{2,})(?:\s|$)")
# the electrical rows L4-E4 to L4-E8, this record and the charger's drawn parts rest on (ChargeVoltage, the input limit and the
# ILIM_HIZ line, VINDPM, REGN, the protections, the converter's current limits, HIZ, the cell strap, PROCHOT and PSYS)
EC_RESTS_ON = ("VBAT_REG_ACC", "VIREG_CHG_RNG", "IIIN_DPM_REG_ACC", "VIREG_DPM_RNG_ILIM", "IIIN_DPM_REG_ACC_ILIM", "VDPM_REG_ACC",
               "VREGN_REG", "VVBUSOV_RISE", "VVBUSOV_FALL", "VACOC_FLOOR", "VACOC_CEILING", "VSYSOVP_RISE", "VSYSOVP_FALL",
               "VBATOVP_RISE", "VBATOVP_FALL", "VOCP_lim_ACX", "VOCP_lim_Q2", "VOCP_lim_SYSSHRT_ACX", "VOCP_lim_SYSSHRT_Q2",
               "TSHUT_RISE", "VHIZ_", "VCELL_4S", "VCELL_BATPRESZ_FALL", "IDCHG_TH1", "IDCHG_TH2", "VPSYS_ACC", "VIADPT_ACC",
               "IIBAT_CHG_ACC", "VVBUS_CONVEN", "VVBAT_UVLOZ")
# the rows whose numbers differ between the sheets, by kind: the script refuses a sheet in which any other row differs
EC_CHANGED = {"VSYS_UVLOZ": "changed", "VSYS_UVLO": "changed", "IDCHG_DEG1": "a typical figure reprinted",
              "ICHRG_REG_ACC": "the condition text and the 1S row's 3.6 V written as VSYS_MIN; the precharge rows follow",
              "IREGN_LIM": "a footnote marker", "VVBUS_OTG_OV": "a heading's text", "VINDEP_CMP_HYS": "a footnote marker",
              "ILEAK_COMP2": "a section number"}


def pin_table(key):
    t = "\f".join(pdf_pages(key, True))
    i = t.find("Pin Functions")
    seg = t[i:t.find("Specifications", i)]
    d = {}
    for m in re.finditer(r"^\s{0,6}([A-Z][A-Z0-9_/]+)\s+(\d{1,2})\s+(PWR|I/O|I|O|GND|NA)\b", seg, re.M):
        d[int(m.group(2))] = m.group(1)
    if sorted(d) != list(range(1, 33)):
        refuse(3, "%s's pin table" % PINS[key][0])
    return d


def ec_blocks(key, head):
    t = "\f".join(pdf_pages(key, True))
    i = t.find(head, t.find(head) + 1)
    j = t.find("Typical Characteristics", i)
    if i < 0 or j < 0:
        refuse(3, "%s's electrical characteristics" % PINS[key][0])
    out, cur = {}, "(head)"
    out[cur] = []
    for ln in t[i:j].split("\n"):
        if EC_SKIP.search(ln):
            continue
        m = EC_SYM.match(ln)
        if m and "_" in m.group(1):
            cur = m.group(1)
            out.setdefault(cur, [])
            out[cur].append([])
        elif not out[cur]:
            out[cur].append([])
        out[cur][-1] += re.findall(r"-?\d+(?:\.\d+)?%?", ln.replace("\u2013", "-"))
    return out


def z_ja_aons():
    """AONS21357 Figure 14 (Rev 2.1 p.5), the single-pulse power junction-to-ambient on the maker's 1 in2 2 oz board at TA 25 C
    (Note H), read from the sheet's vector drawing: the plot's own frame (1E-05 to 1000 s, 1 to 10000 W, log axes) and its one
    curve (a cubic path whose segment ends are the curve's points). ZthJA(t) = (150 - 25) / P(t), checked against the table's
    'Maximum Junction-to-Ambient, t <= 10 s' 25 C/W."""
    pdf = read("aons21357")
    svg = subprocess.run(["pdftocairo", "-svg", "-f", "5", "-l", "5", pdf, "-"], capture_output=True).stdout.decode("utf-8", "replace")
    paths = []
    for m in re.finditer(r"<path[^>]*>", svg):
        t = re.sub(r",\s+", ",", m.group(0))
        d = re.search(r' d="([^"]*)"', t)
        w = re.search(r'stroke-width(?::|=")([\d.]+)', t)
        if d and w and "matrix(0.998658,0,0,-0.998658,0,840.955329)" in t:
            paths.append((float(w.group(1)), d.group(1)))
    frames = []
    for w, d in paths:
        pts = [(float(a), float(b)) for a, b in re.findall(r"[ML] ([-\d.]+) ([-\d.]+)", d)]
        if len(pts) == 5 and "C" not in d and pts[0] == pts[-1] and 340 < max(x for x, _ in pts) - min(x for x, _ in pts) < 360 \
                and 400 < min(y for _, y in pts) < 450:
            frames.append(pts)
    if len(frames) != 1:
        refuse(3, "Figure 14's frame")
    x0, x1 = min(x for x, _ in frames[0]), max(x for x, _ in frames[0])
    y0, y1 = min(y for _, y in frames[0]), max(y for _, y in frames[0])
    def inside(d):                                            # the curve's segment ends inside the frame's power span
        ys = sorted(float(nums.split()[-1]) for _c, nums in re.findall(r"([MC])((?: [-\d.]+)+)", d))
        return bool(ys) and y0 <= ys[len(ys) // 2] <= y1
    curves = [d for w, d in paths if w > 1.5 and d.count("C ") > 100 and inside(d)]
    if len(curves) != 1:
        refuse(3, "Figure 14's curve")
    pts = []
    for cmd, nums in re.findall(r"([MC])((?: [-\d.]+)+)", curves[0]):
        v = [float(x) for x in nums.split()]
        pts.append((-5.0 + 8.0 * (v[-2] - x0) / (x1 - x0), 4.0 * (v[-1] - y0) / (y1 - y0)))
    pts = [p for p in pts if p[0] >= -5.0]
    if any(b[0] <= a[0] for a, b in zip(pts, pts[1:])):
        refuse(3, "Figure 14's curve is not monotone in time")

    def p_of(t):
        lt = math.log10(t)
        for (a, b), (c, e) in zip(pts, pts[1:]):
            if a <= lt <= c:
                return 10 ** (b + (e - b) * (lt - a) / (c - a))
        refuse(3, "Figure 14 has no point at %s s" % t)
    return (lambda t: 125.0 / p_of(t)), (10 ** pts[0][0], 10 ** pts[-1][0])


def consolidation_round(R, T):
    """The owner's instructions of 2 October 2026 11:25 (compare at most three credible approaches, prefer adequate margin and
    fewer interacting controls, quantify power, heat, space, cost and endurance, select the best-supported route) and 12:00
    (the charger: the implementation that supports the battery-present, battery-absent and charging-inhibited modes; TI's
    BQ25730 evaluated against its datasheet and board A's circuit: interfaces, settings, startup, protection, budgets)."""
    B, P, E, F, N, G, C = R["B"], R["P"], R["E"], R["F"], R["N"], R["G"], R["C"]
    ga = T["gen_a"]
    gaf = re.sub(r"\n#\s*", " ", ga)
    H = {}
    # ---- the sheet itself
    p_, m = find("bq25730", r"(SLUSE65A) . FEBRUARY 2021 . REVISED JANUARY 2024", "the BQ25730's literature number")
    H["lit"], H["pages"] = m.group(1), sum(1 for t in pdf_pages("bq25730") if t.strip())
    H["feat_p"] = find("bq25730", r"Power path control through battery MOSFET implementing independent system voltage instant-?\s?on with no battery or depleted battery", "p.1's power path")[0]
    # ---- the pins against U3's netlist
    p31, p30 = pin_table("bq25731"), pin_table("bq25730")
    H["pins_diff"] = [(k, p31[k], p30[k]) for k in range(1, 33) if p31[k] != p30[k]]
    if H["pins_diff"] != [(21, "NC", "BATDRV")]:
        refuse(4, "the two pin tables differ elsewhere than pin 21")
    m = need(ga, r'ic\("U3", 33, "BQ25731RSNR[^"]*", "QFN32_04", \{(.*?)\}, "(C\d+)"\)', "U3's call", re.S)
    u3 = dict(re.findall(r'"(\d+)": "([^"]+)"', m.group(1)))
    H["u3_code"] = m.group(2)
    if u3.get("21") != "NC" or u3.get("22") != "VBAT" or u3.get("18") != "CH_CELL" or u3.get("6") != "CHG_ILIM":
        refuse(4, "U3's pins 6, 18, 21 and 22 are not as this round reads them")
    H["u3"] = u3
    H["batdrv_p"] = find("bq25730", r"P-channel battery FET \(BATFET\) gate driver output\. It is shorted to VSYS to turn off the BATFET\. It goes 10 V below VSYS to fully turn on BATFET\. BATFET is in linear mode to regulate VSYS at minimum system voltage when battery is depleted\. BATFET is fully on during fast charge and works as an ideal-diode in supplement mode\.", "the BATDRV pin")[0]
    H["vsys_pin_p"] = find("bq25730", r"The system voltage regulation maximum limit is programmed in ChargeVoltage register plus 150 mV and regulation minimum limit is programmed in VSYS_MIN register\.", "the VSYS pin")[0]
    p_, m = find("bq25730", r"When CELL_BATPRESZ pin is pulled down to GND \(because of battery removal\) at the beginning of startup process, VSYS_MIN = ([\d.]+) V and SYS_OVP = (\d+) V and Maximum charge voltage \(REG0x05/04\)\) follow 1 cell default setting ([\d.]+) V\.", "8.3.7")
    H["rm_p"], H["rm"] = p_, (f(m, 1), f(m, 2), f(m, 3))
    need(ga, r'r\("R148", "10R", "CELL_FUSED", "CH_SRN_F"\)', "R148 on the pack side")
    need(ga, r'r\("R149", "10R", "VBAT", "CH_SRP_F"\)', "R149 on VSYS")
    # ---- the electrical rows, sheet against sheet
    b31 = ec_blocks("bq25731", "8.5 Electrical Characteristics(BQ25731)")
    b30 = ec_blocks("bq25730", "7.5 Electrical Characteristics(BQ25730)")
    H["ec_n31"] = len([k for k in b31 if k != "(head)"])
    H["ec_added"] = [k for k in b30 if k not in b31]
    H["ec_gone"] = [k for k in b31 if k not in b30]
    H["ec_same"] = [k for k in b31 if k in b30 and b31[k] == b30[k] and k != "(head)"]
    H["ec_diff"] = [k for k in b31 if k in b30 and b31[k] != b30[k]]
    if sorted(H["ec_diff"]) != sorted(EC_CHANGED):
        refuse(4, "the electrical rows differ elsewhere than this round reads: %s" % sorted(set(H["ec_diff"]) ^ set(EC_CHANGED)))
    miss = [k for k in EC_RESTS_ON if k not in H["ec_same"]]
    if miss:
        refuse(4, "a row the drafted settings rest on differs: %s" % miss)
    pc31 = [x for x in b31["ICHRG_REG_ACC"][0] if x.endswith("%")]
    pc30 = [x for x in b30["ICHRG_REG_ACC"][0] if x.endswith("%")]
    if pc30[:len(pc31)] != pc31:
        refuse(4, "ChargeCurrent's accuracy rows differ")
    H["ichg_pct"] = pc31
    if b30["IREGN_LIM"][0][:len(b31["IREGN_LIM"][0])] != b31["IREGN_LIM"][0]:
        refuse(4, "the REGN rows differ")
    fs = lambda b: any(b["VINDEP_CMP_HYS"][0][i:i + 3] == ["340", "400", "460"] for i in range(len(b["VINDEP_CMP_HYS"][0])))
    if not (fs(b31) and fs(b30)):
        refuse(4, "the 400 kHz switching row differs")
    H["uvlo31"] = (b31["VSYS_UVLOZ"][0][:3], b31["VSYS_UVLO"][0][:3])
    H["uvlo30"] = (b30["VSYS_UVLOZ"][0][:3], [x for x in b30["VSYS_UVLO"][0] if "." in x][:3])
    H["idchg"] = ([x for x in b31["IDCHG_DEG1"][0] if x.startswith("24.")][0], [x for x in b30["IDCHG_DEG1"][0] if x.startswith("24.")][0])
    # ---- the registers that change
    H["ichg_por"] = find("bq25730", r"8\.6\.2 ChargeCurrent Register \(I2C address = 03/02h\) \[reset = (\w+)h\]", "ChargeCurrent's reset")[1].group(1)
    H["ichg_por_p"] = find("bq25730", r"8\.6\.2 ChargeCurrent Register \(I2C address = 03/02h\) \[reset = (\w+)h\]", "ChargeCurrent's reset")[0]
    H["wd_p"] = find("bq25730", r"except ChargeCurrent\(\) resets to 0 A \.", "the watchdog's reset")[0]
    find("bq25730", r"New non-zero charge current value has to be written to ChargeCurrent\(\) register to resume charging after watchdog timer expires\.", "the watchdog's resume")
    H["wd_s"] = f(find("bq25730", r"Watchdog timeout period, REG0x01\[6:5\]=11\s+(\d+)\s+(\d+)\s+(\d+)\s+s", "the watchdog's period", layout=True)[1], 2)
    H["vmin_reg_p"] = find("bq25730", r"Upon POR, the VSYS_MIN register is 3\.6 V for 1 S, 6\.6V for 2 S and 9\.2 V for 3 S, and 12\.3 V for 4 S, and 15\.4 V for 5S\.", "VSYS_MIN's POR")[0]
    regs = {}
    for name, pat in (("EN_LDO", r"2 EN_LDO R/W (\d)b LDO Mode Enable"), ("EN_OOA", r"2 EN_OOA R/W (\d)b Out-of-Audio Enable"),
                      ("CHRG_INHIBIT", r"0 CHRG_INHIBIT R/W (\d)b Charge Inhibit"), ("EN_PORT_CTRL", r"2 EN_PORT_CTRL R/W (\d)b Enable BATFET control"),
                      ("BATFET_ENZ", r"7 BATFET_ENZ R/W (\d)b Turn off BATFET under battery only mode\."),
                      ("BATFETOFF_HIZ", r"1 BATFETOFF_HIZ R/W (\d)b Control BATFET on/off during charger HIZ mode\. 0b: BATFET on during charger HIZ mode <default at POR>")):
        p_, m = find("bq25730", pat, name)
        regs[name] = (int(m.group(1)), p_)
    if (regs["EN_LDO"][0], regs["EN_PORT_CTRL"][0], regs["BATFET_ENZ"][0], regs["BATFETOFF_HIZ"][0], regs["CHRG_INHIBIT"][0]) != (1, 1, 0, 0, 0):
        refuse(4, "a BATFET or charge register's reset is not as this round reads it")
    H["regs"] = regs
    H["devid"] = find("bq25730", r"Device ID \(DeviceAddress\) Register \(I2C address = 2Fh\) \[reset = (\w+)h\]", "the device ID")[1].group(1)
    H["devid31"] = find("bq25731", r"Device ID \(DeviceAddress\) Register \(I2C address = 2Fh\) \[reset = (\w+)h\]", "BQ25731's device ID")[1].group(1)
    # ---- the three modes: the statements that bound VSYS
    H["nvdc_p"] = find("bq25730", r"The device employs Narrow VDC architecture \(NVDC\) with BATFET separating the system from the battery\. The minimum system voltage is set by VSYS_MIN register REG0x0D/0C\(\)\. Even with a depleted battery, the system is regulated above the minimum system voltage\. When the battery is below minimum system voltage setting, the BATFET operates in linear mode \(LDO mode\), and the system is regulated at VSYS_MIN register value\. As the battery voltage rises above the minimum system voltage, system voltage is regulated 150 mV above battery voltage when BATFET is turned off \(no charging or no supplement current\)\. When in charging or in supplement mode, the voltage difference between the system and battery is the VDS of the BATFET and the BATFET is fully on\.", "8.4.1.1")[0]
    p_, m = find("bq25730", r"REG0x05/04\(\) = 0x41A0H \(16\.800 V\)\s+150 mV\s+.\s*(\d)%\s+(\d)%", "VSYSMAX_ACC at 16.8 V", layout=True)
    H["smax_p"], H["smax_acc"] = p_, (f(m, 1) / 100.0, f(m, 2) / 100.0)
    find("bq25730", r"VSYSMAX_ACC\s+REG0x05/04\(\) = 0x5208H \(21\.000 V\)\s*\n\s+\(charge disabled and\s*\n\s+OOA disabled\)", "VSYSMAX_ACC's condition", layout=True)
    p_, m = find("bq25730", r"(\d+\.\d+)\s+V\s*\n\s*REG0x0D/0C\(\) = 0x7B00H\s*\n\s*(.)(\d)%\s+(.)(\d)%", "VSYS_MIN_REG_ACC at 12.3 V", layout=True)
    H["smin_p"], H["smin"], H["smin_lo"] = p_, f(m, 1), f(m, 3) / 100.0
    H["smin_max_printed"] = ("-" if m.group(4) in "\u2013-" else "+") + m.group(5)
    if m.group(2) not in "\u2013-":
        refuse(3, "VSYS_MIN_REG_ACC's minimum is not negative")
    find("bq25730", r"VSYS_MIN_REG_ACC\s+Accuracy \(VBAT\s+REG0x0D/0C\(\) = 0x9A00H\s*\n\s+below REG0x0D/0C\(\)", "VSYS_MIN_REG_ACC's condition", layout=True)
    m = find("bq25730", r"VVBUS_UVLOZ < VVBUS < VVBUSOV_FALL , TJ = (-\d+)°C to \+(\d+)°C", "the electrical table's temperature", layout=True)[1]
    H["ec_tj"] = (f(m, 1), f(m, 2))
    p_, m = find("bq25730", r"REG0x03/02\(\) = 0x0080H\s+(\d+)\s+mA\s*\n\s*setting \(0°C to 85°C\)\s+≥2S\s+.(\d+\.\d)%\s+(\d+\.\d)%", "the 256 mA precharge row", layout=True)
    H["pre_p"], H["pre256"] = p_, (f(m, 1) / 1000.0, f(m, 2) / 100.0, f(m, 3) / 100.0)
    m = find("bq25730", r"REG0x03/02\(\) = 0x00C0H\s+(\d+)\s+mA\s*\n.*?≥2S\s+.(\d+\.\d)%\s+(\d+\.\d)%", "the 384 mA precharge row", layout=True, flags=re.S)[1]
    H["pre384"] = (f(m, 1) / 1000.0, f(m, 2) / 100.0, f(m, 3) / 100.0)
    H["inhibit_p"] = regs["CHRG_INHIBIT"][1]
    # the bounds (INFERRED from the rows above; the pack's window from the image)
    H["floor"] = H["smin"] * (1 - H["smin_lo"])
    H["smin_hi"] = H["smin"] * (1 + H["smin_lo"])                 # ASSUMPTION: the MAX column's "-2 %" read as +2 %
    H["vsys_top"] = (R["cv_max"] + 0.150) * (1 + H["smax_acc"][1])
    H["vsys_inh_cuv"] = max(H["floor"], (P["vsys_cuv"][0] + 0.150) * (1 - H["smax_acc"][0]))
    H["margin_floor"] = H["floor"] - 10.0
    # ---- startup in each mode
    H["bat_only_p"] = find("bq25730", r"If only battery is present and the voltage is above VVBAT_UVLOZ , charger wakes up and the BATFET is turned on and connecting the battery to system\.", "8.3.1, battery only")[0]
    m = find("bq25730", r"VVBAT_UVLOZ\s+VSRN rising\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "VVBAT_UVLOZ", layout=True)[1]
    H["vbat_uvloz"] = (f(m, 1), f(m, 3))
    H["pu_p"] = find("bq25730", r"Battery CELL configuration is read at CELL_BATPRESZ pin voltage and compared to VDDA to determine cell configuration\. Corresponding the default value of ChargeVoltage register \(REG0x05/04\(\)\), ChargeCurrent register \(Reg0x03/02\), VSYS_MIN register \(Reg0x0D/0C\) and SYSOVP threshold are loaded\. Converter powers up\.", "8.3.1, from VBUS")[0]
    find("bq25730", r"This protection is mainly defined to protect converter from system short circuit under both startup and steady state process\.", "8.3.21.8")
    p_, m = find("bq25730", r"than ([\d.]+) V \(configurable through VSYS_UVP register bits\), there is (\d)-ms deglitch time, the IIN_DPM is clamped to ([\d.]+) A by the charger itself\. If hiccup mode is enabled with VSYS_UVP_NO_HICCUP = 0b, after 2-ms deglitch time, the charger should shut down for (\d+) ms\.The charger will restart for (\d+) ms if VSYS is still lower than [\d.]+ V, the charger should shut down again\. This hiccup mode will be tried continuously, if the charger restart failed for (\d) times in (\d+) second, the charger will be latched off\.", "VSYS_UVP and hiccup")
    H["uvp_p"], H["uvp"] = p_, dict(v=f(m, 1), deg=f(m, 2) * 1e-3, iin=f(m, 3), off=f(m, 4) * 1e-3, on=f(m, 5) * 1e-3, n=int(m.group(6)), win=f(m, 7))
    na = T["net_a"]

    def nom_uf(net):
        s = 0.0
        for ref, _p in netlist_nodes(na, net):
            if ref.startswith("C"):
                mm = re.match(r"([\d.]+)(u|n)", netlist_value(na, ref))
                if mm:
                    s += float(mm.group(1)) * (1.0 if mm.group(2) == "u" else 1e-3)
        return s * 1e-6
    H["c_vsys_nom"] = nom_uf("VBAT")
    H["c_vsys_max"] = H["c_vsys_nom"] * 1.1 + G["c181"] * (1 + G["zk_tol"])
    H["t_2v4"] = H["c_vsys_max"] * H["uvp"]["v"] / H["uvp"]["iin"]
    H["hiccups"] = 0 if H["t_2v4"] <= H["uvp"]["deg"] else (1 if H["t_2v4"] <= H["uvp"]["on"] else None)
    if H["hiccups"] is None:
        refuse(4, "VSYS's capacitance cannot reach VSYS_UVP's threshold inside the restart window")
    H["start_bound"] = H["hiccups"] * H["uvp"]["off"] + H["t_2v4"]
    # ---- the rest of the BATFET's place in the circuit (TI's guidance and the gate drive)
    p_, m = find("bq25730", r"P-channel MOSFETs is used for battery charging BATFET\. The gate drivers are internally integrated into the IC with 10 V of gate drive voltage\. (\d+) V or higher voltage rating MOSFETs are preferred for 1- to 4-cell battery application, 30 V or higher voltage rating MOSFETs are preferred for 5-cell battery application, the Ciss of P-channel MOSFET should be chosen less than (\d) nF\.", "the BATFET's selection")
    H["bf_p"], H["bf_v"], H["bf_ciss"] = p_, f(m, 1), f(m, 2) * 1e-9
    m = find("bq25730", r"VBATDRV_ON\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s+V", "VBATDRV_ON", layout=True)
    H["drv_p"], H["drv"] = m[0], (f(m[1], 1), f(m[1], 2), f(m[1], 3))
    H["drv_diode_mv"] = f(find("bq25730", r"VBATDRV_DIODE\s+on BATFET during\s+(\d+)\s+mV", "VBATDRV_DIODE", layout=True)[1])
    m = find("bq25730", r"RBATDRV_ON\s+sourcing 10 µA\s+(\d)\s+(\d)\s+(\d)\s+kΩ", "RBATDRV_ON", layout=True)[1]
    H["rdrv"] = (f(m, 1) * 1e3, f(m, 3) * 1e3)
    H["csys_p"], H["csys_uf"] = find("bq25730", r"Overall (\d+)-.F effective capacitance on VSYS net is necessary \(POSCAP is preferred\)", "9.1")[0], \
        f(find("bq25730", r"Overall (\d+)-.F effective capacitance on VSYS net is necessary \(POSCAP is preferred\)", "9.1")[1])
    H["pk_p"] = find("bq25730", r"When battery is depleted in which VBAT is lower than VSYS_MIN setting or battery is removed, host need to set EN_PKPWR_VSYS=1b to enable peak power mode triggered by system voltage undershoot\.", "8.3.19")[0]
    H["f922_p"] = find("bq25730", r"Figure 9-22\. Peak Power Mode VSYS Trigger", "Figure 9-22")[0]
    find("bq25730", r"ISYS = 1 to 6 A ICHG = 0 A", "Figure 9-22's conditions")
    H["depl_p"] = find("bq25730", r"Typically the battery depletion threshold should be greater than the VSYS_MIN so that the battery capacity can be fully utilized for maximum battery run time\.", "10")[0]
    H["batoc_p"] = find("bq25730", r"BATFET status is not impacted if need to supplement power to system\.", "8.3.21.6")[0]
    H["hiz_v"] = f(find("bq25730", r"the charger can enter HIZ mode \(converter shuts off\) when ILIM_HIZ pin voltage is below ([\d.]+) V", "8.3.8")[1])
    m = find("bq25730", r"7\.3 Recommended Operating Conditions \(continued\).*?Junction temperature range, TJ\s+(\S+)\s+(\d+)", "the recommended TJ", layout=True, flags=re.S)[1]
    H["tj_rec"] = (f(m, 1) if m.group(1)[0].isdigit() else -float(m.group(1)[1:]), f(m, 2))
    # ---- the battery FET Q39: AOS AONS21357 (Rev 2.1, November 2023), held
    aos = lambda pat, what, fl=0: find("aons21357", pat, what, layout=True, flags=fl)
    H["q_rev"] = find("aons21357", r"Rev\.(\d\.\d): November 2023", "the AOS revision")[1].group(1)
    Q = {}
    Q["vds"] = f(aos(r"Drain-Source Voltage\s+VDS\s+-(\d+)", "VDS")[1])
    Q["vgs"] = f(aos(r"Gate-Source Voltage\s+VGS\s+±(\d+)", "VGS")[1])
    Q["idm"] = f(aos(r"Pulsed Drain Current\s+IDM\s+-(\d+)", "IDM")[1])
    m = aos(r"t ≤ 10s\s+(\d+)\s+(\d+)\s+°C/W", "RthJA 10 s")[1]
    Q["rja10"] = f(m, 2)
    m = aos(r"Steady-State\s+(\d+)\s+(\d+)\s+°C/W", "RthJA steady")[1]
    Q["rja_ss"] = f(m, 2)
    m = aos(r"VGS=-10V, ID=-20A\s+([\d.]+)\s+([\d.]+)\s*\n.*?TJ=125°C\s+([\d.]+)\s+([\d.]+)", "RDS(on)", re.S)[1]
    Q["rds25"], Q["rds125"] = f(m, 2) * 1e-3, f(m, 4) * 1e-3
    Q["ciss"] = f(aos(r"Ciss\s+Input Capacitance\s+(\d+)\s+pF", "Ciss")[1]) * 1e-12
    m = aos(r"IS=-1A, VGS=0V\s+-([\d.]+)\s+-(\d)\s+V", "VSD")[1]
    Q["vsd"] = f(m, 2)
    Q["is"] = f(aos(r"IS\s+Maximum Body-Diode Continuous Current G\s+-(\d+)", "IS")[1])
    find("aons21357", r"H\. These tests are performed with the device mounted on 1 in2 FR-4 board with 2oz\. Copper, in a still air environment with TA=25°C\.", "Note H")
    find("aons21357", r"Figure 14: Single Pulse Power Rating Junction-to-Ambient \(Note H\)", "Figure 14")
    Q["fig9_p"] = find("aons21357", r"Figure 9: Maximum Forward Biased Safe Operating Area \(Note F\)", "Figure 9")[0]
    find("aons21357", r"F\. These curves are based on the junction-to-case thermal impedance which is measured with the device mounted to a large heatsink, assuming a maximum junction temperature of TJ\(MAX\)=150°C\. The SOA curve provides a single pulse rating\.", "Note F")
    zja, Q["z_span"] = z_ja_aons()
    Q["z10"] = zja(10.0)
    if abs(Q["z10"] - Q["rja10"]) > 0.02 * Q["rja10"]:
        refuse(3, "Figure 14 does not read the table's 10 s junction-to-ambient figure")
    air = F["air_hot"]
    Q["vgs_use"] = H["drv"][2] / Q["vgs"]
    Q["vds_use"] = B["sysovp4s"] / Q["vds"]
    # loss on battery at the profile states (the budget's battery-terminal watts at 14.4 V), RDS(on) at its 125 C maximum
    Q["prof"] = []
    for name in ("PS-IDLE-SPEC", "PS-TYP"):
        i_ = E["states"][name][1] / 14.4
        Q["prof"].append((name, i_, i_ ** 2 * Q["rds125"], i_ ** 2 * Q["rds125"] / (i_ * 14.4)))
    # the pack's own currents through Q39 (fully on), from the inside air and from 10 A held
    pf = yaml.safe_load(T["packprot"])
    fn = {x["id"]: x for x in pf["functions"]}
    th = lambda k: (float(fn[k]["threshold"]["value"]), float(fn[k]["threshold"]["delay_s"]))
    ocd1, aold = th("PACK_OVER_CURRENT_DISCHARGE"), th("PACK_OVER_CURRENT_DISCHARGE_2")
    m = need(flat(T["primcfg"]), r"\| OCD2 \(14\.9\.7\) \| -8000 mA, 3 s \| -(\d+) mA, (\d) s", "the image's OCD2")
    ocd2 = (f(m, 1) / 1000.0, f(m, 2))
    Q["i_cont"], Q["i_peak"] = 10.0, C["pack_peak"]
    p10 = Q["i_cont"] ** 2 * Q["rds125"]
    Q["tj_10a_60s"] = air + p10 * zja(60.0)
    Q["tj_10a_ss"] = air + p10 * Q["rja_ss"]
    p18 = Q["i_peak"] ** 2 * Q["rds125"]
    Q["p18"] = p18

    def t_lim(p_add, base):
        lo, hi = math.log10(Q["z_span"][0]) + 1e-6, math.log10(Q["z_span"][1]) - 1e-6
        if base + p_add * zja(10 ** hi) <= 150.0:
            return None
        if base + p_add * zja(10 ** lo) > 150.0:
            return 0.0
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if base + p_add * zja(10 ** mid) <= 150.0:
                lo = mid
            else:
                hi = mid
        return 10 ** lo
    Q["t18_air"] = t_lim(p18, air)
    Q["t18_hot"] = t_lim(p18 - p10, Q["tj_10a_ss"])
    Q["prot"] = []
    for lab, (i_, t_) in (("the gauge's OCD1", ocd1), ("the image's OCD2", ocd2), ("the AFE's AOLD", aold), ("the image's ASCD", (G["ascd_a"], 244e-6))):
        p_ = i_ ** 2 * Q["rds125"]
        Q["prot"].append((lab, i_, t_, i_ * Q["rds125"], air + p_ * zja(t_), Q["tj_10a_ss"] + (p_ - p10) * zja(t_)))
    Q["rja_need_20"] = (150.0 - air) / (ocd1[0] ** 2 * Q["rds125"])
    Q["rja_need_18"] = (150.0 - air) / p18
    Q["ocd1"] = ocd1
    # the docking inrush through Q39's body diode (the dependency round's pack-loop model: the discharge FET at once, no drop credited)
    Q["c_behind"] = H["c_vsys_max"]
    Q["tau"] = G["r_loop"] * Q["c_behind"]
    Q["i_dock"] = G["i_conn_pk"]
    Q["t_over_idm"] = Q["tau"] * math.log(Q["i_dock"] / Q["idm"]) if Q["i_dock"] > Q["idm"] else 0.0
    Q["q_dock"] = Q["c_behind"] * 4 * 4.2
    m = find("bq4050", r"VDSG from 0% to 35% VDSG\(ON\)\(TYP\).*?(\d+)\s+(\d+)\s*\n", "the gauge's DSG rise time", layout=True, flags=re.S)
    Q["dsg_rise"] = (m[0], f(m[1], 1) * 1e-6, f(m[1], 2) * 1e-6)
    # the LDO-mode precharge (VSYS at VSYS_MIN, the pack under it): Q39 linear
    i_pre = H["pre256"][0] * (1 + H["pre256"][2])
    i_pre3 = H["pre384"][0] * (1 + H["pre384"][2])
    Q["i_pre"], Q["i_pre3"] = i_pre, i_pre3
    Q["ldo_floor"] = H["smin_hi"] - (150.0 - air) / (Q["rja_ss"] * i_pre)
    Q["ldo_floor3"] = H["smin_hi"] - (150.0 - air) / (Q["rja_ss"] * i_pre3)
    Q["tj_ldo_cuv"] = air + (H["smin_hi"] - P["vsys_cuv"][0]) * i_pre * Q["rja_ss"]
    Q["tj_ldo_shut"] = air + (H["smin_hi"] - P["vsys_shut"][0]) * i_pre * Q["rja_ss"]
    Q["q2_pre"] = (i_pre * P["vsd_max"], air + i_pre * P["vsd_max"] * P["rja"])
    H["Q"] = Q
    # ---- the inductor in supplement mode (S-117's bound with Q39's drop at OCD1's 20 A)
    m = need(gaf, r"the front end's ([\d.]+) A at ([\d.]+) V into a pack at its ([\d.]+) V CUV puts ([\d.]+) A through this inductor", "S-117's inductor bound")
    s117 = (f(m, 1), f(m, 2), f(m, 3), f(m, 4))
    H["l_s117"] = s117
    H["l_pk117"] = f(need(gaf, r"peaks at ([\d.]+) A worst at that bound", "S-117's peak"))
    H["l_isat"] = f(need(gaf, r"The XAL1010-472ME \(4\.7 uH, Isat ([\d.]+) A", "the XAL1010's Isat"))
    H["l_vsys"] = s117[2] - ocd1[0] * Q["rds125"]
    H["l_i"] = s117[0] * s117[1] / H["l_vsys"]
    H["l_pk"] = H["l_pk117"] * H["l_i"] / (s117[0] * s117[1] / s117[2])
    # ---- the second NVDC sheet held and the other held candidates (B2)
    m = find("bq25792", r"RMS discharge current \(continuously\)\s+(\d+)\s+A", "BQ25792's battery FET RMS", layout=True)
    H["bq92"] = (f(m[1]), f(find("bq25792", r"Peak discharge current \(upto 1 sec\)\s+(\d+)\s+A", "BQ25792's peak", layout=True)[1]), m[0])
    H["lm747_p"] = find("lm74700", r"Low IQ Reverse Battery Protection Ideal Diode Controller", "the LM74700-Q1's title")[0]
    # ---- the parts' catalogue readings (LCSC, 2 October 2026) and the comparison's cost
    J = {n: json.load(open(os.path.join(TOP, REC, "inputs", n), encoding="utf-8")) for n in CONS_INPUTS}

    def price(n):
        lad = J[n]["price_usd"]
        k = "10" if "10" in lad else sorted(lad, key=lambda s: int(s))[0]
        return int(k), float(lad[k])
    H["cat"] = {J[n]["model"]: (J[n]["code"], J[n]["stock"], price(n)) for n in CONS_INPUTS}
    cA = H["cat"]["BQ25731RSNR"][2][1] + BANK_N * H["cat"]["EEHZK1E471P"][2][1] + H["cat"]["B540C-13-F"][2][1] \
        + H["cat"]["RC2512FK-07330RL"][2][1] + H["cat"]["EEHZK1V181P"][2][1]
    cB = H["cat"]["BQ25730RSNR"][2][1] + H["cat"]["AONS21357"][2][1] + H["cat"]["EEHZK1V181P"][2][1]
    H["cost"] = (cA, cB)
    # E11-24's bank and direct can at (B1)'s floor: charged to it less the bank's leakage across R_CH, giving into VSYS down to
    # A-14's 10.0 V plus D_H's drop, for the worst admitted step: what the bank would still buy under (B1)
    v1 = H["floor"] - BANK_N * G["zk_leak"] * R_CH
    v2 = 10.0 + G["vf"]
    e = G["c_bank_eff"] * (0.5 * (v1 ** 2 - v2 ** 2) - G["vf"] * (v1 - v2)) + 0.5 * G["c_dir_eff"] * (H["floor"] ** 2 - 10.0 ** 2)
    H["bank_b1"] = e / G["worst"][1]
    return H


def cons_rows(R):
    """D1 to D10 under each option: (row, (A), (B1)). The figures are this record's; section 13 prints them."""
    H, Q, G = R["H"], R["H"]["Q"], R["G"]
    return [
        ("D1", "OPEN (TI): no row bounds VSYS with no battery current", "REMOVED: VSYS_MIN_REG_ACC %s V, at least %s V at TJ %s to %s C (p.%d), with p.%d's LDO mode and p.%d's instant-on" % (fmt(H["smin"], 2), fmt(H["floor"], 3), fmt(H["ec_tj"][0], 0), fmt(H["ec_tj"][1], 0), H["smin_p"], H["nvdc_p"], H["feat_p"])),
        ("D2", "bank E11-24: %s ms against T_RESP %s ms (ASSUMPTION)" % (fmt(G["worst_hold"] * 1e3, 3), fmt(T_RESP * 1e3, 1)), "OPEN (no transient limit; Figure 9-22, p.%d, a typical waveform at 4 ms a division): a bench test against the converters' floor with R-c's step rule as the fallback" % H["f922_p"]),
        ("D3", "OPEN (TI): no statement of VSYS with charge inhibited and no battery current", "REMOVED: VSYSMAX_ACC, VSRN + 150 mV within +-%s %% with charge disabled (p.%d), the BATFET off with no charge or supplement current (p.%d)" % (fmt(H["smax_acc"][1] * 100, 0), H["smax_p"], H["nvdc_p"])),
        ("D4", "E2E answer (forum): 256 mA at POR", "REMOVED: ChargeCurrent's reset printed %sh, 0 A (p.%d); the watchdog returns it to 0 A (p.%d)" % (H["ichg_por"], H["ichg_por_p"], H["wd_p"])),
        ("D5", "the direct EEHZK1V181P (by design)", "the same can (TI's %s uF, p.%d)" % (fmt(H["csys_uf"], 0), H["csys_p"])),
        ("D6", "OPEN (the gauge's 0-V sequence)", "OPEN, unchanged (the gauge's)"),
        ("D7", "OPEN: the clamp typical only", "REMOVED inside 0 to 85 C: IPRECHRG_REG_ACC %s mA within +-%s %% (p.%d)" % (fmt(H["pre256"][0] * 1e3, 0), fmt(H["pre256"][2] * 100, 0), H["pre_p"])),
        ("D8", "OPEN (0x0200 outside 0 to 85 C)", "OPEN, the same row"),
        ("D9", "OPEN (the entry's delay)", "OPEN, unchanged (board E)"),
        ("D10", "OPEN (the entry's transconductance)", "OPEN, unchanged (board E)"),
    ]


def render_consolidation(R, p):
    H, Q, G, B, P, F, C, E = R["H"], R["H"]["Q"], R["G"], R["B"], R["P"], R["F"], R["C"], R["E"]
    air = F["air_hot"]
    p("12. THE U-04 QUESTION FOR THE CONSOLIDATION: TI'S BQ25730 AGAINST BOARD A'S CIRCUIT (2 October 2026)")
    p("   the owner's instructions of 2 October 2026: 11:25, compare at most three credible approaches, prefer adequate margin and fewer interacting")
    p("     controls, quantify power, heat, space, cost and endurance, select the best-supported route, retain the work done unless the change affects it;")
    p("     12:00, the charger that supports the battery-present, battery-absent and charging-inhibited modes, the BQ25730 against TI's sheet and")
    p("     board A's circuit: interfaces, settings, startup, protection and the affected budgets (REQUIREMENT, the owner's)")
    p("   the sheet: TI BQ25730, %s (February 2021, revised January 2024), %d pages, held back under TI's terms (fetch_held_back.py); p.%d: \"Power path"
      % (H["lit"], H["pages"], H["feat_p"]))
    p("     control through battery MOSFET implementing independent system voltage instant-on with no battery or depleted battery\" (MAKER)")
    p("   12a. THE PINS AGAINST U3'S NETLIST (gen_sch_a.py, U3 %s)" % H["u3_code"])
    p("     the two pin tables (SLUSE66A and SLUSE65A, pp.5 to 7) name 31 of 32 pins alike; the one difference: pin %d, %s on the BQ25731 (\"must be"
      % (H["pins_diff"][0][0], H["pins_diff"][0][1]))
    p("       floating\", U3 draws it NC) and %s on the BQ25730, the P-channel BATFET's gate drive, \"shorted to VSYS to turn off ... 10 V below VSYS"
      % H["pins_diff"][0][2])
    p("       to fully turn on\" (p.%d) (MAKER, NETLIST)" % H["batdrv_p"])
    p("     added: Q39, a P-channel FET, source on VBAT (pin 22, VSYS), drain on a new node CH_BATQ, gate on CH_BATDRV (pin 21); R17 (the 5 mOhm RSR)")
    p("       moves to CH_BATQ to CELL_FUSED and R149 (SRP's 10 Ohm) to CH_BATQ, as TI's Figure 9-1 draws the BATFET between VSYS and RSR (SESSION)")
    p("     same pin, new function: VSYS (22) becomes a regulated output, \"maximum limit ... ChargeVoltage register plus 150 mV and regulation minimum")
    p("       limit ... VSYS_MIN register\" (p.%d); SRP (20) reads the BATFET's side of RSR; every other pin keeps its net and function (MAKER, NETLIST)" % H["vsys_pin_p"])
    p("     CELL_BATPRESZ (18) keeps the 4S strap (%s percent of VDDA): pulled low it would load VSYS_MIN %s V, SYSOVP %s V and ChargeVoltage %s V"
      % (fmt(R["strap"][2], 2), fmt(H["rm"][0], 1), fmt(H["rm"][1], 0), fmt(H["rm"][2], 1)))
    p("       (p.%d), so battery presence is never wired to it (SESSION, MAKER)" % H["rm_p"])
    p("   12b. THE SETTINGS L4-E4 TO L4-E8 DRAFTED, SHEET AGAINST SHEET (the electrical tables of SLUSE66A 8.5 and SLUSE65A 7.5, read row by row)")
    p("     %d of the BQ25731's %d row blocks are identical in the BQ25730's table; the rows the drafted settings rest on are among them (MAKER, INFERRED):"
      % (len(H["ec_same"]), H["ec_n31"]))
    p("       %s" % ", ".join(EC_RESTS_ON[:10]))
    p("       %s" % ", ".join(EC_RESTS_ON[10:20]))
    p("       %s; ChargeCurrent's accuracy %s, the 400 kHz row and REGN's limit the same (MAKER)" % (", ".join(EC_RESTS_ON[20:]), " / ".join(H["ichg_pct"])))
    p("     rows whose numbers differ: VSYS_UVLOZ %s V to %s V and VSYS_UVLO %s V to %s V (changed); IDCHG_TH2's typical %s A reprinted %s A;"
      % ("/".join(H["uvlo31"][0]), "/".join(H["uvlo30"][0]), "/".join(H["uvlo31"][1]), "/".join(H["uvlo30"][1]), H["idchg"][0], H["idchg"][1]))
    p("       %d more differ only in text (a condition, a heading, footnote markers, a section number); rows added: %s (MAKER)"
      % (len(H["ec_diff"]) - 3, ", ".join(sorted(set(H["ec_added"])))))
    p("     so these carry over unchanged (RECORD, INFERRED): ChargeVoltage 16.8 V written at most %s V; IIN_HOST 4.70 A with RSNS_RAC 0 and EN_EXTILIM 1"
      % fmt(R["cv_max"], 3))
    p("       (L4-E4, L4-E5); the ILIM_HIZ line and its knee (L4-E5, section 3f's %s A); VINDPM; SYSOVP %s V, BATOVP, ACOV, ACOC, the converter's"
      % (fmt(KNEE_IT, 2), fmt(B["sysovp4s"], 1)))
    p("       OCP rows; HIZ under %s V; PROCHOT and PSYS (R23, R24); the 400 kHz row with R219 191k, the compensation and L2 (S-117); Q7 to Q10 on"
      % fmt(H["hiz_v"], 1))
    p("       REGN; R11 and R12 and L4-E8's bank with its ballasts, which sit on VBUS20 ahead of the charger's input and see the same input current")
    p("     registers that change (MAKER): ChargeCurrent resets to %sh, 0 A, where the BQ25731's resets to 0080h (p.%d); the watchdog (%s s at POR)"
      % (H["ichg_por"], H["ichg_por_p"], fmt(H["wd_s"], 0)))
    p("       returns it to 0 A and a non-zero write resumes the charge (p.%d); VSYS_MIN becomes a register, 12.3 V at POR for 4S (p.%d); EN_LDO %d,"
      % (H["wd_p"], H["vmin_reg_p"], H["regs"]["EN_LDO"][0]))
    p("       EN_PORT_CTRL %d, BATFET_ENZ %d and BATFETOFF_HIZ %d at POR (pp.%d, %d, %d): the BATFET driven, on in HIZ; EN_OOA %d at POR (p.%d); the device"
      % (H["regs"]["EN_PORT_CTRL"][0], H["regs"]["BATFET_ENZ"][0], H["regs"]["BATFETOFF_HIZ"][0], H["regs"]["EN_LDO"][1], H["regs"]["EN_PORT_CTRL"][1],
         H["regs"]["BATFETOFF_HIZ"][1], H["regs"]["EN_OOA"][0], H["regs"]["EN_OOA"][1]))
    p("       ID reads %sh, not %sh; I2C address 6Bh the same (MAKER)" % (H["devid"], H["devid31"]))
    p("   12c. THE THREE MODES: THE STATEMENT THAT BOUNDS VSYS IN EACH (the acceptance)")
    p("     the table's conditions: TJ %s to %s C unless a row says otherwise (p.9); the two VSYS rows hold \"OOA disabled\", and EN_OOA is %d at POR,"
      % (fmt(H["ec_tj"][0], 0), fmt(H["ec_tj"][1], 0), H["regs"]["EN_OOA"][0]))
    p("       so the firmware writes EN_OOA 0 at boot for the printed accuracy to apply (SESSION; before that the modes are stated, their accuracy not) (MAKER)")
    p("     (1) battery present, the source on: p.%d, \"system voltage is regulated 150 mV above battery voltage when BATFET is turned off\", the BATFET"
      % H["nvdc_p"])
    p("       fully on while charging or supplementing, VSYS_MIN the floor; VSYS from %s V (the floor), or, with the source overloaded, the pack less"
      % fmt(H["floor"], 3))
    p("       Q39's drop as it supplements (%s V at the CUV stack and OCD1's %s A, 12e, as (A)'s pack sits on VSYS less R17's drop),"
      % (fmt(H["l_vsys"], 3), fmt(Q["ocd1"][0], 0)))
    p("       to %s V (the pack at ChargeVoltage's %s V plus 150 mV, +%s %%, p.%d): BOUNDED (MAKER, INFERRED)" % (fmt(H["vsys_top"], 3), fmt(R["cv_max"], 3), fmt(H["smax_acc"][1] * 100, 0), H["smax_p"]))
    p("       startup: from VBUS the registers, the cell count from CELL_BATPRESZ, then \"Converter powers up\" (p.%d); with only the battery, above"
      % H["pu_p"])
    p("       VVBAT_UVLOZ (%s to %s V on SRN), \"charger wakes up and the BATFET is turned on\" (p.%d); no charge until ChargeCurrent is written (p.%d) (MAKER)"
      % (fmt(H["vbat_uvloz"][0], 2), fmt(H["vbat_uvloz"][1], 2), H["bat_only_p"], H["ichg_por_p"]))
    p("     (2) battery absent (or both of the pack's FETs open), the source on: p.%d's instant-on; p.%d, below VSYS_MIN \"the BATFET operates in linear"
      % (H["feat_p"], H["nvdc_p"]))
    p("       mode (LDO mode), and the system is regulated at VSYS_MIN\"; VSYS_MIN_REG_ACC %s V, minimum -%s %% (p.%d): at least %s V at TJ %s to %s C;"
      % (fmt(H["smin"], 2), fmt(H["smin_lo"] * 100, 0), H["smin_p"], fmt(H["floor"], 3), fmt(H["ec_tj"][0], 0), fmt(H["ec_tj"][1], 0)))
    p("       at most %s V by the VSYS pin's maximum limit and VSYSMAX_ACC (p.%d, p.%d): BOUNDED (MAKER, INFERRED)" % (fmt(H["vsys_top"], 3), H["vsys_pin_p"], H["smax_p"]))
    p("       the exact gap: VSYS_MIN_REG_ACC prints %s %% in its maximum column as well (p.%d), so the row's upper side is not printed; no claim here rests on it"
      % (H["smin_max_printed"], H["smin_p"]))
    p("       (the floor decides every claim); where a figure needs it, %s V is taken (+%s %%, ASSUMPTION) (MAKER)" % (fmt(H["smin_hi"], 3), fmt(H["smin_lo"] * 100, 0)))
    p("       startup: the same power-up from VBUS (p.%d); VSYS_UVP clamps the input to %s A while VSYS is under %s V and, after %s ms, shuts the"
      % (H["pu_p"], fmt(H["uvp"]["iin"], 1), fmt(H["uvp"]["v"], 1), fmt(H["uvp"]["deg"] * 1e3, 0)))
    p("       converter for %s ms and retries for %s ms, latching after %d failures in %s s (p.%d) (MAKER); VSYS's capacitance at most %s uF (the VBAT net's"
      % (fmt(H["uvp"]["off"] * 1e3, 0), fmt(H["uvp"]["on"] * 1e3, 0), H["uvp"]["n"], fmt(H["uvp"]["win"], 0), H["uvp_p"], fmt(H["c_vsys_max"] * 1e6, 1)))
    p("       %s uF of ceramics plus 10 %%, and the direct can at +%s %%); WITHDRAWN by the fix round: the %s A is the input clamp, not a delivered"
      % (fmt(H["c_vsys_nom"] * 1e6, 1), fmt(G["zk_tol"] * 100, 0), fmt(H["uvp"]["iin"], 1)))
    p("       current, so no start time follows from it; the start is bounded in 15b (INFERRED)")
    p("     (3) battery present, charging inhibited: CHRG_INHIBIT 1 inhibits the charge (p.%d); VSYSMAX_ACC with charge disabled: VSRN + 150 mV within"
      % H["inhibit_p"])
    p("       +-%s %% (p.%d), the BATFET off, so no battery current unless the load exceeds the source (supplement, p.%d); with the pack at its CUV stack VSYS"
      % (fmt(H["smax_acc"][1] * 100, 0), H["smax_p"], H["batdrv_p"]))
    p("       is at least %s V: BOUNDED (MAKER, INFERRED); startup as (1), the bit at 0 by POR, written from the hold flag (section 14)" % fmt(H["vsys_inh_cuv"], 3))
    p("     so each mode has the maker's printed bound on VSYS (D1 and D3 removed); the margin from the floor to A-14's assumed 10.0 V converter floor:")
    p("       %s V, which a load step in S2 or S4 must not use up (D2, no transient limit printed) (INFERRED)" % fmt(H["margin_floor"], 3))
    p("   12d. PROTECTION (MAKER)")
    p("     the input, system and battery over-voltage, input over-current, converter OCP and thermal rows are the same (12b); VSYS_UVP moves to %s V with"
      % fmt(H["uvp"]["v"], 1))
    p("       hiccup (12c); BATOC stops the converter and \"BATFET status is not impacted if need to supplement power to system\" (p.%d); in HIZ the BATFET"
      % H["batoc_p"])
    p("       stays on (BATFETOFF_HIZ %d), so CHG_INHIBIT's HIZ leaves the kit on the pack exactly as with the BQ25731 (R-a's rule on the line holds);"
      % H["regs"]["BATFETOFF_HIZ"][0])
    p("       BATFET_ENZ would force the BATFET off on battery and the kit would run through its body diode: never written (SESSION)")
    p("     for a pack below VSYS_MIN with the source overloaded, TI's peak power mode on VSYS undershoot is the one meant \"when ... battery is removed\"")
    p("       (p.%d); Figure 9-22 (p.%d) draws that mode (1 to 6 A on VSYS at VSYS_MIN 12.3 V, ICHG 0 A) at a scale that resolves no transient (MAKER)"
      % (H["pk_p"], H["f922_p"]))
    p("   12e. THE AFFECTED BUDGETS")
    p("     the inductor L2: with the pack at CUV supplementing at the gauge's OCD1 %s A, VSYS is %s V (Q39's drop), so S-117's %s A at %s V becomes %s A"
      % (fmt(Q["ocd1"][0], 0), fmt(H["l_vsys"], 3), fmt(H["l_s117"][3], 1), fmt(H["l_s117"][2], 1), fmt(H["l_i"], 3)))
    p("       and its worst peak %s A against Isat %s A (S-117: %s A): re-derived, %s %% up (INFERRED)"
      % (fmt(H["l_pk"], 2), fmt(H["l_isat"], 1), fmt(H["l_pk117"], 1), fmt((H["l_i"] / (H["l_s117"][0] * H["l_s117"][1] / H["l_s117"][2]) - 1) * 100, 2)))
    p("     L4-E8's bank, its ballasts, R11 and R12: on VBUS20, ahead of R16; the charger's input current and switching are the same rows: unchanged (INFERRED)")
    p("     the battery FET Q39 as first selected (SUPERSEDED by 15c: its -10 V rows do not bound BATDRV's 8.5 V drive): AOS AONS21357, %s V,"
      % fmt(Q["vds"], 0))
    p("       VGS +-%s V, RDS(on) at -10 V at most %s mOhm at 25 C and %s mOhm at 125 C, Ciss %s nF"
      % (fmt(Q["vgs"], 0), fmt(Q["rds25"] * 1e3, 1), fmt(Q["rds125"] * 1e3, 1), fmt(Q["ciss"] * 1e9, 2)))
    p("       typical, IDM %s A, IS %s A, RthJA %s C/W at 10 s and %s C/W steady on a 1 in2 2 oz board (Rev %s, pp.1 and 2) (MAKER); LCSC %s, stock %d (CATALOGUE)"
      % (fmt(Q["idm"], 0), fmt(Q["is"], 0), fmt(Q["rja10"], 0), fmt(Q["rja_ss"], 0), H["q_rev"], H["cat"]["AONS21357"][0], H["cat"]["AONS21357"][1]))
    p("       TI's selection (p.%d): P-channel, %s V or more for 1 to 4 cells, Ciss under %s nF: %s nF typical, %s %% of it (no maximum printed); VDS at"
      % (H["bf_p"], fmt(H["bf_v"], 0), fmt(H["bf_ciss"] * 1e9, 0), fmt(Q["ciss"] * 1e9, 2), fmt(Q["ciss"] / H["bf_ciss"] * 100, 1)))
    p("       SYSOVP %s V is %s %% of %s V; BATDRV's %s V at most is %s %% of VGS's rating (MAKER, INFERRED)"
      % (fmt(B["sysovp4s"], 1), fmt(Q["vds_use"] * 100, 1), fmt(Q["vds"], 0), fmt(H["drv"][2], 1), fmt(Q["vgs_use"] * 100, 1)))
    p("     the SOA: Figure 9 (p.%d) is junction-to-case on a large heatsink at TC 25 C (Note F, a single pulse), so on board A's copper the"
      % Q["fig9_p"])
    p("       junction-to-ambient single-pulse rating of Figure 14 decides; every protection current below sits at VDS under %s V, in Figure 9's RDS(on) region"
      % fmt(max(v for _l, _i, _t, v, _a, _h in Q["prot"]) + 0.005, 2))
    p("       and under IDM %s A (the docking inrush is not: below), and the LDO precharge's DC point (under 5 V at %s mA) is judged on RthJA (MAKER, INFERRED)"
      % (fmt(Q["idm"], 0), fmt(Q["i_pre"] * 1e3, 0)))
    p("     Figure 14 (Rev %s p.5, junction to ambient, single pulse, TA 25 C, Note H) read from the sheet's drawing: ZthJA(10 s) %s C/W against the"
      % (H["q_rev"], fmt(Q["z10"], 3)))
    p("       table's %s (MAKER, read); RDS(on) at its 125 C maximum above 125 C (ASSUMPTION); from the inside air %s C (L4-E9, RECORD):" % (fmt(Q["rja10"], 0), fmt(air, 1)))
    for name, i_, w, fr in Q["prof"]:
        p("       on battery at %s, %s A: %s W in Q39, %s %% of the pack's output, the endurance it costs (INFERRED)" % (name, fmt(i_, 3), fmt(w, 4), fmt(fr * 100, 3)))
    p("       10 A for 60 s: TJ %s C (MEETS); 10 A held: %s C at the steady %s C/W (MEETS) (INFERRED)" % (fmt(Q["tj_10a_60s"], 1), fmt(Q["tj_10a_ss"], 1), fmt(Q["rja_ss"], 0)))
    p("       the pack's %s A peak (%s W): from the air for at most %s s; after 10 A held, for at most %s s (INFERRED)"
      % (fmt(Q["i_peak"], 0), fmt(Q["p18"], 3), fmt(Q["t18_air"], 2), fmt(Q["t18_hot"], 3)))
    for lab, i_, t_, vds, tj_air, tj_hot in Q["prot"]:
        dur = ("%s s" % fmt(t_, 2)) if t_ >= 0.1 else (("%s ms" % fmt(t_ * 1e3, 1)) if t_ >= 1e-3 else ("%s us" % fmt(t_ * 1e6, 0)))
        p("       %s, %s A for %s (VDS %s V, deep in the SOA's RDS(on) region): TJ %s C from the air, %s C after 10 A held: %s (INFERRED)"
          % (lab, fmt(i_, 1), dur, fmt(vds, 3), fmt(tj_air, 1), fmt(tj_hot, 1), "MEETS" if tj_hot <= 150.0 else "NOT MET"))
    p("       so the sheet's own board does not carry the pack's protection envelope: below OCD1's %s A the gauge never trips, and %s A held needs an"
      % (fmt(Q["ocd1"][0], 0), fmt(Q["ocd1"][0], 0)))
    p("       installed RthJA of at most %s C/W (%s C/W for %s A held), against the sheet's %s: a Layer 9 bar (E11-29, CONDITIONAL); the fallback is the"
      % (fmt(Q["rja_need_20"], 2), fmt(Q["rja_need_18"], 2), fmt(Q["i_peak"], 0), fmt(Q["rja_ss"], 0)))
    p("       gauge's OCD1 set to what the installed path carries, or the bridge shedding on PROCHOT's IDCHG (INFERRED)")
    p("     the docking inrush (S1 from cold, the dependency round's pack loop, the discharge FET at once, no diode drop credited): %s A peak through"
      % fmt(Q["i_dock"], 1))
    p("       Q39's body diode into VSYS's %s uF at most, over IDM's %s A for %s us (time constant %s us): the sheet prints no body-diode pulse rating, only"
      % (fmt(Q["c_behind"] * 1e6, 1), fmt(Q["idm"], 0), fmt(Q["t_over_idm"] * 1e6, 1), fmt(Q["tau"] * 1e6, 1)))
    p("       IS %s A continuous: the exact gap (E11-30); the gauge's DSG drive rises in %s to %s us typical to maximum (bq4050 p.%d), with no minimum, so"
      % (fmt(Q["is"], 0), fmt(Q["dsg_rise"][1] * 1e6, 0), fmt(Q["dsg_rise"][2] * 1e6, 0), Q["dsg_rise"][0]))
    p("       it bounds nothing (MAKER, INFERRED); the same peak passes R17, F1 and the pack's FETs in arrangement (A)")
    p("     the precharge in LDO mode (a pack under VSYS_MIN with the source on): ChargeCurrent 0x0080, %s mA within +-%s %% at 0 to 85 C (p.%d), at"
      % (fmt(H["pre256"][0] * 1e3, 0), fmt(H["pre256"][2] * 100, 0), H["pre_p"]))
    p("       most %s mA; Q39 drops VSYS_MIN's %s V to the pack: TJ %s C at the CUV stack (%s V) and %s C at the Shutdown Voltage's %s V; TJ reaches"
      % (fmt(Q["i_pre"] * 1e3, 1), fmt(H["smin_hi"], 3), fmt(Q["tj_ldo_cuv"], 1), fmt(P["vsys_cuv"][0], 1), fmt(Q["tj_ldo_shut"], 1), fmt(P["vsys_shut"][0], 1)))
    p("       150 C at %s V; at 0x00C0 (%s mA at most) already at %s V, so R-b' takes 0x0080 and no charge under %s V on SRN (SESSION, INFERRED, the"
      % (fmt(Q["ldo_floor"], 3), fmt(Q["i_pre3"] * 1e3, 0), fmt(Q["ldo_floor3"], 3), fmt(math.ceil(Q["ldo_floor"] * 10) / 10, 1)))
    p("       steady %s C/W on the sheet's board, CONDITIONAL on E11-29); Q2's diode then carries %s W, TJ %s C (INFERRED)"
      % (fmt(Q["rja_ss"], 0), fmt(Q["q2_pre"][0], 3), fmt(Q["q2_pre"][1], 1)))
    p("     TI's own note: \"Typically the battery depletion threshold should be greater than the VSYS_MIN\" (p.%d); the pack's CUV (%s V) is under it,"
      % (H["depl_p"], fmt(P["vsys_cuv"][0], 1)))
    p("       so LDO-mode precharge is a normal state after a deep discharge, budgeted above (MAKER, INFERRED)")
    p("")
    p("13. THREE APPROACHES COMPARED (each complete; INFERRED unless marked)")
    p("   (A) the drawn BQ25731 with E11-24's hold-up; (B1) TI's BQ25730 with Q39, as 12; (B2) one other implementation whose maker's sheet states the")
    p("     property that removes D1 and D3: NONE FOUND. Looked at, held: the BQ25798 and BQ25792 (NVDC, both statements, but an integrated BATFET of")
    p("     %s A RMS and %s A for 1 s, BQ25798 p.%d, BQ25792 p.%d, under the pack's %s A); the LM74700-Q1 (p.%d, an ideal-diode controller: it blocks"
      % (fmt(C["bq98_rms"], 0), fmt(C["bq98_pk"], 0), C["bq98_p"], H["bq92"][2], fmt(C["pack_peak"], 0), H["lm747_p"]))
    p("     reverse current and regulates no node); the LT8705A (a buck-boost regulator with no battery FET); the TPS2595, TPS2596 and TPS1663 (eFuses).")
    p("     TI's external-FET NVDC parts other than the BQ25730 are its family and architecture, not a different implementation (MAKER, INFERRED)")
    p("   row | (A) | (B1)")
    for rid, a, b in cons_rows(R):
        p("     %s | %s | %s (MAKER, INFERRED)" % (rid, a, b))
    p("   carried over unchanged in (B1): every L4-E4 to L4-E8 figure on VBUS20 and the input (IIN_HOST 4.70 A, RSNS_RAC, EN_EXTILIM, the ILIM_HIZ line")
    p("     and knee, VINDPM, R11 8 mOhm, R12 12 mOhm, C147, L4-E8's six cans and 45 mOhm ballasts), ChargeVoltage, SYSOVP, BATOVP, ACOV, the converter's")
    p("     parts (Q7 to Q10, L2's part, R219, the compensation), R16, R17's value, R-b's case (i) (the 0x0200 row is the same), section 3 (RECORD, MAKER)")
    p("   re-derived in (B1): VSYS's range per mode (12c); L2's supplement current (%s A, 12e); the start (VSYS_UVP, 12c); ChargeCurrent's POR and"
      % fmt(H["l_i"], 3))
    p("     watchdog (R-a's persistence); R-b' under VSYS_MIN; Q39's loss, thermal bar and inrush; VSYS's capacitance split (CELL_FUSED's 104 uF now")
    p("     behind Q39); E11-24's bank withdrawn (12c's floor is %s V, where four cans would hold %s ms; the bank leaned on T_RESP) (INFERRED)"
      % (fmt(H["floor"], 3), fmt(H["bank_b1"] * 1e3, 3)))
    p("   power and heat into the case on battery: (A) none added; (B1) Q39 %s W at PS-IDLE-SPEC and %s W at PS-TYP, %s W at 10 A (INFERRED)"
      % (fmt(Q["prof"][0][2], 4), fmt(Q["prof"][1][2], 4), fmt(10.0 ** 2 * Q["rds125"], 3)))
    p("   endurance on battery: (A) none lost; (B1) %s %% at PS-IDLE-SPEC, %s %% at PS-TYP (INFERRED)" % (fmt(Q["prof"][0][3] * 100, 3), fmt(Q["prof"][1][3] * 100, 3)))
    p("   area on board A: (A) the bank and the direct can, about 5.5 cm2 (section 10); (B1) Q39's 5 x 6 mm land and the direct can, about 1 cm2 of parts,")
    p("     with Q39's copper sized by E11-29's bar (at least the sheet's 1 in2 of 2 oz copper, on any layer) (INFERRED)")
    p("   part cost at LCSC's 10-piece price (CATALOGUE, 2 October 2026): (A) %s USD (BQ25731, four EEHZK1E471P, B540C, RC2512, EEHZK1V181P); (B1) %s USD"
      % (fmt(H["cost"][0], 4), fmt(H["cost"][1], 4)))
    p("     (BQ25730, AONS21357, EEHZK1V181P): %s USD less; stock: BQ25731 %d, BQ25730 %d at LCSC (a supply item, E11-32) (CATALOGUE)"
      % (fmt(H["cost"][0] - H["cost"][1], 4), H["cat"]["BQ25731RSNR"][1], H["cat"]["BQ25730RSNR"][1]))
    p("   interacting controls: (A) four run-time rules, two of them tied to the gauge's FET state (R-a's S4 exception, R-b), R-c, the hold's flag, and the")
    p("     bank's reliance on T_RESP; (B1) three run-time rules (R-a with no exception, R-b' tied to the gauge, R-c), the flag, and two boot writes")
    p("     (EN_OOA 0, ChargeCurrent with the watchdog); the BATFET's registers stay at POR (SESSION, INFERRED)")
    p("")
    p("14. THE SELECTION, THE DRAFT AND U-04'S CLASS")
    p("   SELECTED (SESSION): (B1), TI's BQ25730 in U3's land with Q39 (the fix round, 15c: Q39 and Q40, two BUK6Y10-30P; 15a: board E on VSYS).")
    p("     Why: it is the only option whose maker prints a bound on VSYS in all three modes")
    p("     (12c), removing D1, D3 and D4 and bounding D7 inside 0 to 85 C, where (A) leaves D1 and D3 to TI and holds D2 with compensating parts on an")
    p("     assumed 1 ms; every setting L4-E4 to L4-E8 drafted rests on rows the two sheets print alike (12b); it costs less and removes the bank; its")
    p("     costs are named and bounded: Q39's thermal bar (E11-29), the docking pulse (E11-30), %s %% of the pack's output at PS-IDLE-SPEC, and"
      % fmt(Q["prof"][0][3] * 100, 3))
    p("     the BQ25730's stock (E11-32). No protected line changes and no money beyond parts (reserved.json names no schematic part) (SESSION)")
    p("   the draft: apply_gen_sch_a_charger.py (release-guarded, never applied here): U3 BQ25730RSNR (%s), pin 21 CH_BATDRV, Q39 AONS21357 (%s) between"
      % (H["cat"]["BQ25730RSNR"][0], H["cat"]["AONS21357"][0]))
    p("     VBAT and CH_BATQ, R17 and R149 moved to CH_BATQ, C236 EEHZK1V181P (C242139) on VBAT, CH_BATQ declared a segment of the pack path (SESSION)")
    p("   what it changes downstream: E11-27 to E11-32 added; E11-24 withdrawn and E11-05 not needed once E11-27 is applied; E11-22's case (iii) bounded")
    p("     inside 0 to 85 C; Q-TI-11's D1 and Q-TI-3's addendum fall away (D2's question stays); R-a's S4 exception withdrawn; section 3 unchanged (INFERRED)")
    p("   U-04's claims still open with (B1): D2 (S2 and S4 load steps against the %s V margin: bench E11-31, fallback R-c's step rule); Q39's thermal"
      % fmt(H["margin_floor"], 3))
    p("     bar (E11-29) and docking pulse (E11-30); D6, D8 (R-b's case (ii)); REQ-015 at 9.00 V at the plug as section 3g (E11-06, E11-09, E11-23); and")
    p("     on board E D9 and D10 (INFERRED)")
    p("   U-04 BY THE OWNER'S EXIT DEFINITION: A DOWNSTREAM QUALIFICATION TEST WITH BOUNDED EVIDENCE AND A WORKABLE FALLBACK, once E11-27 is applied:")
    p("     the three modes rest on the maker's printed rows; each open claim has a test or analysis that bounds it and a fallback that needs no new")
    p("     architecture (R-c's step rule; OCD1 set to the installed path; a slower DSG turn-on on board P). On the drawn board (A) it stays the")
    p("     architecture-level choice of section 11 (INFERRED)")
    p("")

# ============================================================================================ the fix round (cx36's B1, B2)
TJ_LIM_175 = 150.0       # C, SESSION (fix round): the junction limit for a part rated 175 C (25 K under its rating)
FIX_HELD_ACC = 1.0e-3    # A, SESSION (fix round): the held state's pack current acceptance on the bench (E11-31)
FIX_DOCK_CONTACTS = 1    # SESSION (fix round): 813 contacts carrying VSYS to board E (pin 1); seven stay ground
FIX_OCD1_HELD = True     # the sustained worst: just under the gauge's OCD1, which never trips below its threshold


def fet_bound(r10_25, r10_hot, t_hot, r45_25, vg, tj, r10_mid=None, t_mid=None):
    """An upper bound on a P-channel FET's RDS(on) at |VGS| = vg and junction tj from the maker's printed maxima only:
    the chord between the printed maxima at -4.5 V and -10 V (25 C) bounds the value at vg (each unit's RDS(on) is convex and
    falling in |VGS|, and so is their pointwise maximum: INFERRED), and the chord between the printed -10 V maxima bracketing
    tj bounds the temperature factor (convex rising in TJ: INFERRED); the gate ratio is taken from 25 C, where the threshold
    sits highest (it falls with temperature, so the hot ratio is no larger: INFERRED). Refuses a tj above the last printed row."""
    if tj > t_hot + 1e-9:
        refuse(4, "no printed RDS(on) maximum at %s C" % tj)
    kg = (r10_25 + (r45_25 - r10_25) * (10.0 - vg) / (10.0 - 4.5)) / r10_25
    if r10_mid is not None and tj >= t_mid:
        r10 = r10_mid + (r10_hot - r10_mid) * (tj - t_mid) / (t_hot - t_mid)
    else:
        r10 = r10_25 + (r10_hot - r10_25) * (tj - 25.0) / (t_hot - 25.0)
    return kg, r10 * kg


def fix_round(R, T):
    """The consolidation review cx36 (filed in set 27: records/l4close/checks/astra-check-l4close-1.md), read NOT YET. B1: board
    E's auxiliary domain sits on CELL_F, on the pack side of R17, so with Q39 off it still drains the pack and with the pack
    absent nothing feeds it; the 502.3 ms start rested on a 0.5 A input ceiling read as a delivered current. B2: Q39's thermal
    acceptance used RDS(on) at -10 V where BATDRV may give 8.5 V. And the charger minors (E1)."""
    H, Q0, G, B, P, E, F, C = R["H"], R["H"]["Q"], R["G"], R["B"], R["P"], R["E"], R["F"], R["C"]
    K = {}
    ge, ga = T["gen_e"], T["gen_a"]
    # ---- B1: board E's auxiliary domain as drawn (NETLIST)
    need(ge, r'ic\("U12", 6, "AP63205WU-7[^"]*", "TSOT6", \{"1": "\+5V_E6", "2": "CELL_F", "3": "CELL_F"', "U12 on CELL_F")
    need(ge, r'c\("C31", "10u 25V 1210", "CELL_F", "GND", "C1210"\)', "C31 on CELL_F")
    need(ge, r'ph\("J_FAN%s" % n, 3, "mixer fan %s under the plate \(12 V class fan on the pack node, low-side PWM, tachometer\)" % n, \{"1": "CELL_F"', "the fans on CELL_F")
    m = need(ge, r'_intent\.rail\("CELL_F", 14\.4, 10\.0, 18\.0, "F3".*?loads=\{"P_CP": ([\d.]+), "U12": ([\d.]+), "J_FAN1": ([\d.]+), "J_FAN2": ([\d.]+)\}', "CELL_F's loads", re.S)
    K["aux"] = dict(U12=f(m, 2), J_FAN1=f(m, 3), J_FAN2=f(m, 4))
    K["aux_a"] = sum(K["aux"].values())
    m = need(ge, r'r\("R42", "(\d+)k 1%", "CELL_F", "CELL_MON"\); r\("R43", "(\d+)k 1% \(ADC2: 0\.18 x pack\)", "CELL_MON", "GND"\)', "the pack monitor divider")
    K["div_r"] = (f(m, 1) + f(m, 2)) * 1e3
    K["i_div"] = R["cv_max"] / (K["div_r"] * 0.99)
    need(ge, r'part\("J_BLK", "Connector_Generic", "Conn_01x12", "[^"]*", "POGO_T6",\s+\{"1": "GND", "2": "GND"', "J_BLK pin 1 on GND")
    need(ga, r'part\("J_DOCK", "Connector_Generic", "Conn_01x12", "[^"]*", "POGO12",\s+\{"1": "GND", "2": "GND"', "J_DOCK pin 1 on GND")
    need(ge, r'"U12 is an AP63205 whose EN pin is tied to CELL_F, the pack node it runs from', "U12's EN on CELL_F")
    # the AP63205's input range (Diodes DS41326, held) and the SMCJ18A's leakage (Littelfuse SMC series, held)
    K["ap_vin"] = find("ap63200", r"VIN (\d+\.\d)V to (\d+)V", "the AP63205's input range")[1]
    K["ap_vin"] = (f(K["ap_vin"], 1), f(K["ap_vin"], 2))
    m = find("smcj", r"SMCJ18A\s+SMCJ18CA\s+\S+\s+\S+\s+(18\.0)\s+([\d.]+)\s+([\d.]+)\s+1\s+([\d.]+)\s+([\d.]+)\s+(\d+)", "SMCJ18A's row", layout=True)[1]
    K["d3_ir_ua"] = f(m, 6)
    # the dock's 813 contacts (w3de's model, pinned): the supply contact and the ground return with one contact fewer
    sp = importlib.util.spec_from_file_location("dock_contacts_pinned", read("dock_py"))
    dc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(dc)
    K["c813_max"] = dc.PD_MAX
    K["aux_share"] = K["aux_a"] / FIX_DOCK_CONTACTS / dc.PD_MAX
    K["aux_rise"] = dc.rise_813(K["aux_a"] / FIX_DOCK_CONTACTS)
    ret = []
    for n813 in (8, 8 - FIX_DOCK_CONTACTS):
        for opened in (0, 1):
            g_mm = dc.MM_RMAX / 8 + dc.R_POUR + dc.R_12AWG / 2
            n = n813 - opened
            g813 = dc.R_813_PATH / n
            i8 = (dc.I_VIN + dc.I_PACK_P) * (g_mm / (g_mm + g813)) / n
            ret.append((n813, opened, i8, 100 * i8 / dc.PD_MAX, dc.AIR["envelope 51 C"] + dc.rise_813(i8), dc.AIR["margin 65 C"] + dc.rise_813(i8)))
    K["ret"] = ret
    # the held state: the pack current with the charge inhibited and the source carrying the kit
    K["held_dv"] = R["cv_max"] - (R["cv_max"] + 0.150) * (1 - H["smax_acc"][0])     # VSYS may sit this far under VSRN
    K["held_bounded_a"] = K["i_div"] + K["d3_ir_ua"] * 1e-6
    # ---- the piecewise acceptance (the review's minor and E1)
    K["lo_v"] = H["smin"] * 0.98                       # VBAT_VSYS_MIN_RISE at least 98 %: below it, LDO mode
    K["hi_v"] = H["smin"] * 1.02                       # at most 102 %: above it, the battery-tracking mode
    m = find("bq25730", r"VBAT_VSYS_MIN_RISE\s+as percentage of 0x0D/0C\(\)\s+(\d+)%\s+(\d+)%\s+(\d+)%", "VBAT_VSYS_MIN_RISE", layout=True)[1]
    if (f(m, 1), f(m, 3)) != (98.0, 102.0):
        refuse(4, "VBAT_VSYS_MIN_RISE is not 98 to 102 %")
    K["track_floor_at_lo"] = (K["lo_v"] + 0.150) * (1 - H["smax_acc"][0])
    K["inh_floor"] = min(H["floor"], K["track_floor_at_lo"])
    K["review_case"] = (10.0 + 0.150) * (1 + H["smax_acc"][1])
    # ---- the start (VSYS_UVP), bounded where held evidence bounds it
    u = H["uvp"]
    K["uvlo30"] = [float(x) for x in H["uvlo30"][0]]
    K["e_start"] = 0.5 * H["c_vsys_max"] * K["uvlo30"][2] ** 2
    K["p_in_cap"] = u["iin"] * E["vb_top"]
    na = T["net_a"]
    rs = []
    for ref, _p in netlist_nodes(na, "VBAT"):
        if ref.startswith("R") and ref not in ("R17", "R149"):
            mm = re.match(r"([\d.]+)k", netlist_value(na, ref))
            if mm:
                rs.append((ref, float(mm.group(1)) * 1e3))
    K["start_rs"] = rs
    K["i_res_start"] = K["uvlo30"][2] * sum(1.0 / r for _r, r in rs)
    K["t_latch"] = u["deg"] + (u["n"] - 1) * (u["off"] + u["on"])
    K["por_p"] = find("bq25730", r"5 ms after either VBUS or VBAT becomes valid, the charger resets all the registers to the default state\.", "8.3.1's reset")[0]
    # ---- B2: three battery-FET options on one basis (MAKER rows; the bound of fet_bound)
    vg = H["drv"][0]
    air = {"route": None, "l4e9": F["air_hot"]}
    m = need(T["arch"], r"\| K9 \| E3-O, D-02a's \+55 C AMBIENT margin: the heat stage, every radio C1 leaves on \| open \| [\d.]+ \| \+55\.0 C \| \+(\d+) C \(U-02\)", "the consolidation's +70 C line")
    air["route"] = f(m)
    K["air"] = air
    zja, span = z_ja_aons()
    zss = Q0["rja_ss"]
    z = lambda t: min(1.0, zja(t) / zss)                # the board's transient shape, AOS Figure 14 over its steady 55 C/W
    K["z"] = {t: z(t) for t in (2.44e-4, 0.02, 1.0, 60.0)}
    vs = flat(pdf_pages("sqj403", True)[1])
    m = need(vs, r"VGS = -10 V ID = -10 A - ([\d.]+) ([\d.]+) VGS = -10 V ID = -10 A, TJ = 125 °C - - ([\d.]+) Drain-Source On-State Resistance a RDS\(on\)\s*\S?\s*VGS = -10 V ID = -10 A, TJ = 175 °C - - ([\d.]+) VGS = -4\.5 V ID = -7 A - [\d.]+ ([\d.]+)", "SQJ403EP's RDS(on) rows")
    sq = dict(r10_25=f(m, 2) * 1e3, r10_mid=f(m, 3) * 1e3, t_mid=125.0, r10_hot=f(m, 4) * 1e3, t_hot=175.0, r45_25=f(m, 5) * 1e3)
    sq["ciss_max"] = f(need(vs, r"Input Capacitance Ciss - (\d+) (\d+)", "SQJ403EP's Ciss"), 2) * 1e-12
    sq["ism"] = f(need(vs, r"Pulsed Current a ISM - - -(\d+)", "SQJ403EP's ISM"))
    v1 = flat(pdf_pages("sqj403", True)[0])
    sq["idm"] = f(need(v1, r"Pulsed Drain Current b IDM -(\d+)", "SQJ403EP's IDM"))
    sq["vgs"] = f(need(v1, r"Gate-Source Voltage VGS ± (\d+)", "SQJ403EP's VGS"))
    sq["rja"] = f(need(v1, r"Junction-to-Ambient PCB Mount c RthJA (\d+)", "SQJ403EP's RthJA"))
    sq["tj"] = f(need(v1, r"TJ, Tstg -55 to \+(\d+)", "SQJ403EP's TJ"))
    sq["rev"] = need(v1, r"(S15-2089-Rev\. A, 31-Aug-15)", "SQJ403EP's revision").group(1)
    nx = "\n".join(pdf_pages("buk6y10", True))
    m = need(nx, r"VGS = -10 V; ID = -13\.5 A; Tj = 25 °C\s+-\s+(\d+)\s+(\d+)\s+mΩ\s*\n\s+resistance\s+VGS = -10 V; ID = -13\.5 A; Tj = (\d+) °C\s+-\s+(\d+)\s+(\d+)\s+mΩ\s*\n\s+VGS = -4\.5 V; ID = -8\.5 A; Tj = 25 °C\s+-\s+(\d+)\s+(\d+)", "BUK6Y10-30P's RDSon rows")
    nxp = dict(r10_25=f(m, 2), t_hot=f(m, 3), r10_hot=f(m, 5), r45_25=f(m, 7))
    nxp["ciss"] = f(need(nx, r"Ciss\s+input capacitance\s+VDS = -15 V; f = 1 MHz; VGS = 0 V;\s+-\s+(\d+)\s+-", "BUK6Y10-30P's Ciss")) * 1e-12
    nxp["idm"] = f(need(nx, r"IDM\s+peak drain current\s+single pulse; tp ≤ 10 µs; Tmb = 25 °C\s+-\s+-(\d+)", "BUK6Y10-30P's IDM"))
    nxp["ism"] = f(need(nx, r"ISM\s+peak source current\s+single pulse; tp ≤ (\d+) µs; Tmb = 25 °C\s+-\s+-(\d+)", "BUK6Y10-30P's ISM"), 2)
    nxp["ism_tp"] = f(need(nx, r"ISM\s+peak source current\s+single pulse; tp ≤ (\d+) µs", "BUK6Y10-30P's ISM width")) * 1e-6
    nxp["vgs"] = f(need(nx, r"VGS\s+gate-source voltage\s+\[1\]\s+-(\d+)\s+(\d+)\s+V", "BUK6Y10-30P's VGS"))
    nxp["tj"] = f(need(nx, r"Tj\s+junction temperature\s+-55\s+(\d+)", "BUK6Y10-30P's Tj"))
    nxp["rthmb"] = f(need(nx, r"Rth\(j-mb\)\s+thermal resistance from\s+-\s+([\d.]+)\s+([\d.]+)", "BUK6Y10-30P's Rth(j-mb)"), 2)
    nxp["date"] = need(nx, r"(17 April 2020)\s+Product data sheet", "BUK6Y10-30P's date").group(1)
    aos = dict(r10_25=Q0["rds25"] * 1e3, r10_hot=Q0["rds125"] * 1e3, t_hot=125.0,
               r45_25=f(find("aons21357", r"VGS=-4\.5V, ID=-20A\s+([\d.]+)\s+([\d.]+)\s+mΩ", "AONS21357's -4.5 V row", layout=True)[1], 2))
    cands = [
        dict(key="a", lab="(Q-a) AOS AONS21357, one", n=1, tjlim=aos["t_hot"], rdef=aos, ciss=Q0["ciss"], ciss_kind="typical",
             pulse=Q0["idm"], pulse_kind="IDM only; no body-diode pulse rating", rboard=Q0["rja_ss"], vgs=Q0["vgs"], vds=Q0["vds"], tjr=150.0),
        dict(key="b", lab="(Q-b) Vishay SQJ403EP, one", n=1, tjlim=TJ_LIM_175, rdef=sq, ciss=sq["ciss_max"], ciss_kind="maximum",
             pulse=sq["ism"], pulse_kind="ISM (300 us test pulse)", rboard=sq["rja"], vgs=sq["vgs"], vds=30.0, tjr=sq["tj"]),
        dict(key="c", lab="(Q-c) Nexperia BUK6Y10-30P, two in parallel", n=2, tjlim=TJ_LIM_175, rdef=nxp, ciss=2 * nxp["ciss"], ciss_kind="typical, two",
             pulse=nxp["ism"], pulse_kind="ISM, tp at most 10 us, each", rboard=None, vgs=nxp["vgs"], vds=30.0, tjr=nxp["tj"]),
    ]
    ocd1 = Q0["ocd1"]
    ocd2 = [(i_, t_) for lab, i_, t_, _v, _a, _h in Q0["prot"] if lab == "the image's OCD2"][0]
    aold = [(i_, t_) for lab, i_, t_, _v, _a, _h in Q0["prot"] if lab == "the AFE's AOLD"][0]
    ascd = [(i_, t_) for lab, i_, t_, _v, _a, _h in Q0["prot"] if lab == "the image's ASCD"][0]
    for cd in cands:
        rd = cd["rdef"]
        kg, rb = fet_bound(rd["r10_25"], rd["r10_hot"], rd["t_hot"], rd["r45_25"], vg, cd["tjlim"], rd.get("r10_mid"), rd.get("t_mid"))
        cd["kg"], cd["rb"] = kg, rb * 1e-3                              # ohm, per FET, at the junction limit and 8.5 V
        n = cd["n"]
        pw = lambda i: (i / n) ** 2 * cd["rb"]                          # per FET: the even split bounds each FET's power
        cd["p"] = dict(p10=pw(10.0), p18=pw(Q0["i_peak"]), p20=pw(ocd1[0]), p24=pw(ocd2[0]), p30=pw(aold[0]), pscd=pw(ascd[0]))
        bud = {}
        for a_lab, ta in air.items():
            b = cd["tjlim"] - ta
            lim = {
                "10 A held": b / cd["p"]["p10"],
                "18 A for 60 s after 10 A held": b / (cd["p"]["p10"] + (cd["p"]["p18"] - cd["p"]["p10"]) * z(60.0)),
                "20 A held (under OCD1)": b / cd["p"]["p20"],
                "OCD2 24 A for 1 s after 20 A held": b / (cd["p"]["p20"] + (cd["p"]["p24"] - cd["p"]["p20"]) * z(1.0)),
                "AOLD 30 A for 20 ms after 20 A held": b / (cd["p"]["p20"] + (cd["p"]["p30"] - cd["p"]["p20"]) * z(0.02)),
                "ASCD 55.6 A for 244 us after 20 A held": b / (cd["p"]["p20"] + (cd["p"]["pscd"] - cd["p"]["p20"]) * z(2.44e-4)),
            }
            bud[a_lab] = lim
        cd["bars"] = bud
        cd["bar"] = {a: min(v.values()) for a, v in bud.items()}
        cd["bind"] = {a: min(v, key=v.get) for a, v in bud.items()}
        cd["board_ok"] = (cd["rboard"] is not None and cd["rboard"] <= cd["bar"]["route"])
        cd["ciss_ok"] = cd["ciss"] < H["bf_ciss"]
        cd["dock_peak"] = Q0["i_dock"]
        cd["dock_ok_cold"] = Q0["i_dock"] <= cd["pulse"] * n if cd["key"] != "a" else False
    K["cands"] = cands
    sel = cands[2]
    K["sel"] = sel
    # the selected pair's docking pulse: the ISM rectangle against the decaying pulse, all of it in one FET at 25 C, and from the
    # route's inside air with ISM derated linearly to the 175 C rating (ASSUMPTION A11-22), the largest share one FET may take
    i2t_pulse = Q0["i_dock"] ** 2 * Q0["tau"] / 2.0
    i2t_rect = nxp["ism"] ** 2 * nxp["ism_tp"]
    der = (nxp["tj"] - air["route"]) / (nxp["tj"] - 25.0)
    K["dock"] = dict(i2t_pulse=i2t_pulse, i2t_rect=i2t_rect, der=der, ism_hot=nxp["ism"] * der,
                     s_max=min(1.0, math.sqrt(i2t_rect * der / i2t_pulse), nxp["ism"] * der / Q0["i_dock"]))
    # the LDO-mode precharge with R17's tolerance, all of it in one FET of the pair (linear-mode sharing not assumed)
    r17_tol = 0.01
    K["i_pre"] = H["pre256"][0] * (1 + H["pre256"][2]) / (1 - r17_tol)
    K["ldo_floor"] = H["smin_hi"] - (sel["tjlim"] - air["route"]) / (sel["bar"]["route"] * K["i_pre"])
    K["rb_floor"] = max(math.ceil(K["ldo_floor"] * 10) / 10.0, P["cells"] * P["pre_win"][0])
    K["q2_pre"] = (K["i_pre"] * P["vsd_max"], air["route"] + K["i_pre"] * P["vsd_max"] * P["rja"])
    # the inductor in supplement mode and VSYS's supplement floor with the pair and R17
    r17 = 0.005 * (1 + r17_tol)
    K["vsys_sup"] = P["vsys_cuv"][0] - ocd1[0] * (r17 + sel["rb"] / sel["n"])
    K["l_i"] = H["l_s117"][0] * H["l_s117"][1] / K["vsys_sup"]
    K["l_pk"] = H["l_pk117"] * K["l_i"] / (H["l_s117"][0] * H["l_s117"][1] / H["l_s117"][2])
    K["prof"] = [(nm, i_, i_ ** 2 * sel["rb"] / sel["n"], i_ * sel["rb"] / sel["n"] / 14.4) for nm, i_, _w, _f in Q0["prof"]]
    K["turn_tau"] = (H["rdrv"][1] * sel["ciss"])
    J = {n: json.load(open(os.path.join(TOP, REC, "inputs", n), encoding="utf-8")) for n in FIX_INPUTS}
    K["cat"] = {J[n]["model"]: (J[n]["code"], J[n]["stock"], float(J[n]["price_usd"]["10"])) for n in FIX_INPUTS}
    return K


def render_fix(R, p):
    K, H, Q0, P, F = R["K"], R["H"], R["H"]["Q"], R["P"], R["F"]
    sel = K["sel"]
    p("15. THE FIX ROUND FOR THE CONSOLIDATION REVIEW (cx36, read NOT YET on set 27's 8fbb68b6: its B1, B2 and the charger minors)")
    p("   15a. B1: BOARD E'S AUXILIARY DOMAIN ON A SOURCE-CAPABLE FEED")
    p("     as drawn (NETLIST): U12 (the AP63205, its VIN and EN), C31 and both mixer fans (J_FAN1, J_FAN2, D7, D8) sit on CELL_F, the pack node")
    p("       before board A's R17 and the battery FET; CELL_F declares them at %s A (U12 %s, fans %s and %s); the counterexample holds: with"
      % (fmt(K["aux_a"], 2), fmt(K["aux"]["U12"], 2), fmt(K["aux"]["J_FAN1"], 2), fmt(K["aux"]["J_FAN2"], 2)))
    p("       the charge inhibited the battery FET is off (p.%d) and they still drain the pack, and with the pack absent nothing feeds them (NETLIST, MAKER)"
      % H["nvdc_p"])
    p("     the feed (SESSION): from VSYS alone, over the dock: board A's J_DOCK pin 1 from GND to VBAT (VSYS), board E's J_BLK pin 1 to a new net")
    p("       VSYS_E, and U12's VIN and EN, C31, the fans' supply pins and D7 and D8 on VSYS_E; CELL_F keeps the pack path to board A, D3, C1 and")
    p("       the pack monitor (R42 and R43). Why VSYS and no OR: VSYS exists whenever the pack or a source does (the battery FET on with the")
    p("       battery alone, p.%d, and its body diode under any fault of the drive), and a diode or ideal-diode OR with CELL_F would take the pack"
      % H["bat_only_p"])
    p("       whenever VSYS sits under it, which the +-%s %% row allows in the held state (INFERRED)" % fmt(H["smax_acc"][0] * 100, 0))
    p("     the contact: one 813 on pin 1, %s A declared, %s %% of its %s A, %s K by w3de's assumed I2 rise; the seven 813 ground contacts left carry,"
      % (fmt(K["aux_a"], 2), fmt(K["aux_share"] * 100, 1), fmt(K["c813_max"], 1), fmt(K["aux_rise"], 2)))
    p("       at the 32.1 A coincidence with every Mill-Max pin at 20 mOhm (w3de's model, pinned):")
    for n813, opened, i8, pct, t51, t65 in K["ret"]:
        p("       %d x 813 ground%s: %s A each, %s %% of 3.5 A, %s C at the 51 C air and %s C at the margin's 65 C (INFERRED, w3de's ASSUMPTIONS)"
          % (n813, ", one open" if opened else "", fmt(i8, 3), fmt(pct, 1), fmt(t51, 1), fmt(t65, 1)))
    p("       so taking one ground contact moves W3DE-DOCK-R1's residual by one contact's step and keeps the 51 C envelope under 85 C with one open;")
    p("       a second supply contact would leave six, %s C with one open at 51 C: one contact is taken (SESSION); losing it unpowers board E's"
      % fmt(dock_six_open(K), 1))
    p("       controller, which board A reads on HOT-R1 as the detector lost (IF-AE-DOCK hot_r1), a detected state (INFERRED)")
    p("     VSYS_E's range: the supplement floor %s V to %s V (15d); the AP63205 takes %s to %s V (Diodes DS41326 p.1); the fans, rated as 12 V class"
      % (fmt(K["vsys_sup"], 3), fmt(H["vsys_top"], 3), fmt(K["ap_vin"][0], 1), fmt(K["ap_vin"][1], 0)))
    p("       on CELL_F's 16.884 V, now see up to %s V: their maximum supply voltage is owed (E11-35) (MAKER, INFERRED)" % fmt(H["vsys_top"], 3))
    p("     the held state (the charge inhibited, an adequate source, the pack present): the battery FET off with no charging or supplement current")
    p("       (p.%d); board E on VSYS_E from the source; what the pack still feeds, by element (MAKER, NETLIST, INFERRED):" % H["nvdc_p"])
    p("       the pack monitor R42 + R43 (%s kOhm at -1 %%): %s mA at %s V, intended (the controller's own pack reading)"
      % (fmt(K["div_r"] / 1e3, 0), fmt(K["i_div"] * 1e3, 4), fmt(R["cv_max"], 3)))
    p("       D3, SMCJ18A: IR at most %s uA at 18 V and 25 C (Littelfuse SMC series, held); its hot leakage is not printed" % fmt(K["d3_ir_ua"], 0))
    p("       the battery FETs' body diodes: VSYSMAX_ACC's -%s %% lets VSYS sit up to %s V under the pack at %s V, a forward bias at which the sheets"
      % (fmt(H["smax_acc"][0] * 100, 0), fmt(K["held_dv"], 3), fmt(R["cv_max"], 3)))
    p("       print no current (VSD only at 80 A): not bounded on held evidence; and the charger's SRN pin, whose leakage row prints a mismatch only")
    p("     so no kit load is fed from the pack while the source carries it; the bounded drains total %s mA, and the bench reads the held pack"
      % fmt(K["held_bounded_a"] * 1e3, 4))
    p("       current at most %s mA (E11-31's acceptance; board E's aux drew about 0.5 to 1.5 W from the pack before) (SESSION, CONDITIONAL)" % fmt(FIX_HELD_ACC * 1e3, 1))
    p("     the source-only sequence (the pack absent or both its FETs open): the source and the entry (3c); the front end to VBUS20; U3's POR (p.%d),"
      % K["por_p"])
    p("       ChargeCurrent 0 A; the converter up; VSYS through VSYS_UVP's start (15b) to VSYS_MIN; board A's always-on and board E's U12 on VSYS_E;")
    p("       E's controller up and driving HOT-R1; firmware: EN_OOA 0, IIN_HOST 4.70 A, CHRG_INHIBIT from the hold flag (INFERRED, MAKER)")
    p("     the held sequence: the flag set writes CHRG_INHIBIT 1; the battery FET turns off as the charge stops (p.%d); VSYS moves to VSRN + 150 mV;"
      % H["nvdc_p"])
    p("       nothing on either board moves; the flag cleared writes 0 and ChargeCurrent by R-b' (INFERRED)")
    p("   15b. THE START, BOUNDED WHERE THE HELD SHEETS BOUND IT (the 502.3 ms of 12c withdrawn: 0.5 A is an input ceiling, not a delivered current)")
    p("     the input limits (MAKER, p.%d): under %s V of VSYS (VSYS_UVLO; rising %s/%s/%s V, p.13) the input is clamped to %s A, at most %s W from VBUS20's"
      % (H["uvp_p"], fmt(H["uvp"]["v"], 1), fmt(K["uvlo30"][0], 2), fmt(K["uvlo30"][1], 1), fmt(K["uvlo30"][2], 2), fmt(H["uvp"]["iin"], 1), fmt(K["p_in_cap"], 2)))
    p("       %s V top; the sheet prints no minimum delivered current below that voltage (MAKER)" % fmt(R["E"]["vb_top"], 2))
    p("     the loads below %s V: the converters on VSYS held off by their enables or their UVLOs (the LM5176 stages by logic, U12 on board E under"
      % fmt(K["uvlo30"][2], 2))
    p("       its %s V start, the heater buck by its divider); the resistors on VBAT (%s): at most %s mA at %s V; the ICs' currents under UVLO are not"
      % (fmt(K["ap_vin"][0], 1), ", ".join("%s %s k" % (r_, fmt(v / 1e3, 0)) for r_, v in K["start_rs"]), fmt(K["i_res_start"] * 1e3, 4), fmt(K["uvlo30"][2], 2)))
    p("       all held (NETLIST, INFERRED); the energy to bring VSYS's %s uF to %s V: %s mJ (INFERRED)"
      % (fmt(H["c_vsys_max"] * 1e6, 1), fmt(K["uvlo30"][2], 2), fmt(K["e_start"] * 1e3, 3)))
    p("     the retries (MAKER): each failed start shuts the converter for %s ms and retries for %s ms; the %dth failure inside %s s latches it, at"
      % (fmt(H["uvp"]["off"] * 1e3, 0), fmt(H["uvp"]["on"] * 1e3, 0), H["uvp"]["n"], fmt(H["uvp"]["win"], 0)))
    p("       most %s s after the first window (INFERRED); with no pack only a POR clears it (VBUS re-plugged: \"5 ms after either VBUS or VBAT becomes"
      % fmt(K["t_latch"], 3))
    p("       valid, the charger resets all the registers\", p.%d), with a pack the host does (it runs on the pack through the battery FET) (MAKER)" % K["por_p"])
    p("     so on held evidence the start ends in VSYS_MIN or in a latch within %s s, never undefined; whether the first window succeeds is not"
      % fmt(K["t_latch"], 3))
    p("       bounded (no minimum delivered current): BENCH E11-31, acceptance: from cold, at VBUS20 %s and %s V, with VSYS's maximum capacitance and the"
      % (fmt(R["E"]["vb_low"], 2), fmt(R["E"]["vb_top"], 2)))
    p("       declared always-on loads (board E on VSYS_E), at -20, 25 and %s C, VSYS reaches %s V with Fault VSYS_UVP clear; the hiccup's %s/%s ms and"
      % (fmt(F["air_hot"], 1), fmt(H["floor"], 3), fmt(H["uvp"]["off"] * 1e3, 0), fmt(H["uvp"]["on"] * 1e3, 0)))
    p("       the latch shown on a shorted VSYS and cleared by a re-plug (SESSION)")
    p("   15c. B2: THE BATTERY FET, THREE OPTIONS ON ONE BASIS (the drive BATDRV gives at its least, %s V, p.17; RDS(on) from the makers' printed"
      % fmt(H["drv"][0], 1))
    p("     [SUPERSEDED IN PART by section 16: fet_bound's figure is an allowance, not a bound; AOS's shape, the Ciss reading and the docking I2t")
    p("     are replaced; the selection of the pair stands] (SESSION)")
    p("     maxima only, bounded by fet_bound: the gate chord between -4.5 and -10 V, the temperature chord between the printed -10 V rows) (MAKER, INFERRED)")
    p("     the inside air: the consolidation's +%s C mixed-air line for the parts that must work in the heat stage (L4-POWER-ARCHITECTURE K9, E3-O"
      % fmt(K["air"]["route"], 0))
    p("       at +55 C ambient; K3 at +40 C), reconciled with L4-E9's %s C, which it covers; the board's transient shape from AOS Figure 14 over its"
      % fmt(K["air"]["l4e9"], 1))
    p("       steady %s C/W for every option: z(244 us) %s, z(20 ms) %s, z(1 s) %s, z(60 s) %s (ASSUMPTION A11-21 for the other packages) (MAKER, read)"
      % (fmt(Q0["rja_ss"], 0), fmt(K["z"][2.44e-4], 5), fmt(K["z"][0.02], 4), fmt(K["z"][1.0], 4), fmt(K["z"][60.0], 4)))
    p("     the events, each from a hot state, per FET (the even split bounds each FET's power for any split of the RDS(on) spread): 10 A held; 18 A")
    p("       for 60 s after 10 A held (PWR-F12's service); 20 A held, under the gauge's OCD1, which never trips below it; from it OCD2's 24 A for 1 s,")
    p("       the AFE's AOLD 30 A for 20 ms and the image's ASCD 55.6 A for 244 us; the bar is the installed junction-to-air resistance per FET at")
    p("       which every event keeps TJ at the limit or under (INFERRED)")
    for cd in K["cands"]:
        rd = cd["rdef"]
        p("     %s (MAKER, INFERRED):" % cd["lab"])
        p("       printed maxima: %s mOhm at -10 V and 25 C, %s mOhm at -10 V and %s C, %s mOhm at -4.5 V and 25 C; the bound at %s V and the junction"
          % (fmt(rd["r10_25"], 1), fmt(rd["r10_hot"], 1), fmt(rd["t_hot"], 0), fmt(rd["r45_25"], 1), fmt(H["drv"][0], 1)))
        p("         limit %s C (the sheet's last printed temperature or 25 K under a 175 C rating): gate factor %s, %s mOhm per FET"
          % (fmt(cd["tjlim"], 0), fmt(cd["kg"], 4), fmt(cd["rb"] * 1e3, 3)))
        p("       Ciss %s nF (%s) against TI's %s nF: %s; VGS +-%s V against BATDRV's %s V; VDS %s V against SYSOVP's %s V"
          % (fmt(cd["ciss"] * 1e9, 2), cd["ciss_kind"], fmt(H["bf_ciss"] * 1e9, 0), "MEETS" if cd["ciss_ok"] else "NOT MET", fmt(cd["vgs"], 0),
             fmt(H["drv"][2], 1), fmt(cd["vds"], 0), fmt(R["B"]["sysovp4s"], 1)))
        for a_lab, ta in (("route", K["air"]["route"]), ("l4e9", K["air"]["l4e9"])):
            p("       the bar at %s C air: %s C/W per FET, set by %s" % (fmt(ta, 1), fmt(cd["bar"][a_lab], 2), cd["bind"][a_lab]))
        p("       the maker's reference board: %s; the docking pulse, %s A peak: %s A %s (MAKER, INFERRED)"
          % (("%s C/W, %s" % (fmt(cd["rboard"], 0), "inside the bar" if cd["board_ok"] else "over the bar")) if cd["rboard"] is not None else "none printed (LFPAK56, a junction-to-mounting-base %s K/W)" % fmt(rd["rthmb"], 1),
             fmt(Q0["i_dock"], 1), fmt(cd["pulse"], 0), cd["pulse_kind"]))
    d = K["dock"]
    p("   SELECTED (SESSION): %s, Q39 and Q40 (LCSC %s, %d in stock, %s USD each at 10). Why: the only option inside TI's Ciss (%s nF typical"
      % (sel["lab"][6:], K["cat"]["BUK6Y10-30PX"][0], K["cat"]["BUK6Y10-30PX"][1], fmt(K["cat"]["BUK6Y10-30PX"][2], 4), fmt(sel["ciss"] * 1e9, 2)))
    p("     for the two) with a bar of the order a board pour gives: %s C/W per FET at +%s C air, %s of AOS's 1 in2 figure for the same 5 x 6 mm class,"
      % (fmt(sel["bar"]["route"], 2), fmt(K["air"]["route"], 0), fmt(sel["bar"]["route"] / Q0["rja_ss"], 3)))
    p("       where (Q-a) needs %s C/W (%s of its maker's board) and (Q-b) %s C/W (%s of its maker's), which a pour does not give one part; a printed RDS(on)"
      % (fmt(K["cands"][0]["bar"]["route"], 2), fmt(K["cands"][0]["bar"]["route"] / K["cands"][0]["rboard"], 3),
         fmt(K["cands"][1]["bar"]["route"], 2), fmt(K["cands"][1]["bar"]["route"] / K["cands"][1]["rboard"], 3)))
    p("     maximum to 175 C, a 175 C rating, and a printed body-diode pulse rating (ISM %s A each) over the docking pulse; a third FET would put"
      % fmt(sel["rdef"]["ism"], 0))
    p("     Ciss at %s nF typical, over TI's %s nF (SESSION, INFERRED)" % (fmt(3 * sel["rdef"]["ciss"] * 1e9, 2), fmt(R["H"]["bf_ciss"] * 1e9, 0)))
    p("     its envelope at the bar, +%s C air: TJ at most %s C for every event of 15c; 18 A for 60 s after 10 A held: %s C (INFERRED, CONDITIONAL on E11-29)"
      % (fmt(K["air"]["route"], 0), fmt(sel["tjlim"], 0), fmt(sel_tj_18(K), 1)))
    p("     the docking pulse: all of it in one FET at 25 C: %s A against ISM %s A and %s A2s against the ISM rectangle's %s A2s (MEETS); from the"
      % (fmt(Q0["i_dock"], 1), fmt(sel["rdef"]["ism"], 0), fmt(d["i2t_pulse"], 4), fmt(d["i2t_rect"], 4)))
    p("       +%s C air, ISM derated linearly to the 175 C rating (x%s, ASSUMPTION A11-22): %s A and %s A2s, met for a share of at most %s in one FET;"
      % (fmt(K["air"]["route"], 0), fmt(d["der"], 4), fmt(d["ism_hot"], 1), fmt(d["i2t_rect"] * d["der"], 4), fmt(d["s_max"], 3)))
    p("       the split of two body diodes is not printed: E11-30 (the bench pulse on the pair, or a layout matching the two paths) (INFERRED)")
    p("     the drive: BATDRV's %s kOhm at most into %s nF: a %s us time constant (MAKER, INFERRED)" % (fmt(H["rdrv"][1] / 1e3, 0), fmt(sel["ciss"] * 1e9, 2), fmt(K["turn_tau"] * 1e6, 2)))
    p("     the precharge in LDO mode with R17's 1 %%: %s A at most (0.256 x 1.30 / 0.99, the review's minor), all of it in one FET (linear-mode sharing"
      % fmt(K["i_pre"], 5))
    p("       not assumed): TJ reaches %s C at the bar and +%s C air with SRN at %s V, so R-b' allows no charge under %s V on SRN (the cells' 1.0 V a"
      % (fmt(sel["tjlim"], 0), fmt(K["air"]["route"], 0), fmt(K["ldo_floor"], 3), fmt(K["rb_floor"], 1)))
    p("       cell floor is %s V); Q2's diode then %s W, TJ %s C (SESSION, INFERRED; R17's drift with temperature not held)"
      % (fmt(P["cells"] * P["pre_win"][0], 1), fmt(K["q2_pre"][0], 4), fmt(K["q2_pre"][1], 1)))
    for nm, i_, w, fr in K["prof"]:
        p("     on battery at %s, %s A: %s W in the pair, %s %% of the pack's output (INFERRED)" % (nm, fmt(i_, 3), fmt(w, 4), fmt(fr * 100, 3)))
    p("     L2 with the pair: VSYS in supplement %s V (CELL_FUSED's 10.0 V less R17 and the pair at OCD1's 20 A), %s A, peak %s A against Isat %s A (INFERRED)"
      % (fmt(K["vsys_sup"], 3), fmt(K["l_i"], 3), fmt(K["l_pk"], 2), fmt(H["l_isat"], 1)))
    p("   15d. THE CHARGER MINORS (E1)")
    p("     the inhibited acceptance, piecewise (VBAT_VSYS_MIN_RISE 98 to 102 %% of VSYS_MIN, p.14): SRN under %s V: LDO mode, VSYS at least %s V;"
      % (fmt(K["lo_v"], 3), fmt(H["floor"], 3)))
    p("       SRN over %s V: VSRN + 150 mV within +-%s %%; between, either, so at least %s V; the review's case, SRN at 10 V, is the LDO region, and"
      % (fmt(K["hi_v"], 3), fmt(H["smax_acc"][0] * 100, 0), fmt(K["inh_floor"], 3)))
    p("       (10 + 0.15) x 1.02 = %s V belongs to no region (MAKER, INFERRED)" % fmt(K["review_case"], 3))
    p("     the upper side in the LDO region, %s V, is an assumed reading of TI's malformed maximum column (A11-18), not a printed limit (MAKER)"
      % fmt(H["smin_hi"], 3))
    p("     every floor above holds with adequate input power; with the source overloaded VSYS follows the pack through the battery FETs and R17:")
    p("       %s V at CELL_FUSED's 10.0 V and OCD1's 20 A; with no pack and an overloaded source there is no floor, R-c sheds (INFERRED)" % fmt(K["vsys_sup"], 3))
    p("     EN_OOA resets to %d (p.%d): the printed accuracy covers VSYS only after the firmware writes 0; the pre-firmware start has no printed accuracy"
      % (H["regs"]["EN_OOA"][0], H["regs"]["EN_OOA"][1]))
    p("       (E11-31 records it) (MAKER)")
    p("     the text that still says \"no battery FET\" in L4-E9's record and the system node's label are drafted for their owner (E11-34) (INFERRED)")
    p("")


def dock_six_open(K):
    """The 51 C figure with six 813 ground contacts and one of them open (a second supply contact), from w3de's model."""
    sp = importlib.util.spec_from_file_location("dock_contacts_pinned6", read("dock_py"))
    dc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(dc)
    g_mm = dc.MM_RMAX / 8 + dc.R_POUR + dc.R_12AWG / 2
    n = 5
    i8 = (dc.I_VIN + dc.I_PACK_P) * (g_mm / (g_mm + dc.R_813_PATH / n)) / n
    return dc.AIR["envelope 51 C"] + dc.rise_813(i8)


def sel_tj_18(K):
    sel, z60 = K["sel"], K["z"][60.0]
    r = sel["bar"]["route"]
    return K["air"]["route"] + r * (sel["p"]["p10"] + (sel["p"]["p18"] - sel["p"]["p10"]) * z60)

# ============================================================================================ the review of the provisional fixes (L4-F02, L4-F03)
F16_RA = 21.136e-3      # ohm per FET, SESSION: the RDS(on) ALLOWANCE at BATDRV's least 8.5 V and the 150 C limit the design is sized to;
                        # section 15c's figure, no longer called a bound (no sheet prints a maximum there); confirmed by E11-36 or reversed
F16_RA_ALT = 25.0e-3    # ohm, the sheet's largest printed maximum (-4.5 V, 25 C): the sensitivity printed beside the allowance
F16_TJ_HELD = 140.0     # C, SESSION: the held fault's (20 A under OCD1) junction ceiling, 10 K under the limit kept for the pulses from it
F16_READ = "nexperia-buk6y10-30p-figure-readings-2026-10-02.json"
F16_RILIM_K = 11.0      # kOhm 0.1 %, SESSION: the eFuse's ILIM resistor
F16_RILIM_TOL = 0.001
F16_CDVDT = 22e-9       # F, SESSION: the eFuse's dVdT capacitor (TI's characterised 22 nF row)
F16_CDVDT_TOL = 0.10
F16_OVL = (5.0, 14.4)   # the review's counterexample: 5 A drawn from 14.4 V (2.88 Ohm) on VSYS_E
F16_SPREAD = 2.0        # w3de's assumed 2:1 spread of a contact's static resistance (dock_contacts.py)


def zjmb_table(J):
    """BUK6Y10-30P Fig. 4 (the duty-cycle 0.01 curve, above any single pulse), read on the rendered page (inputs/F16_READ), scaled so
    its plateau is Table 6's maximum Rth(j-mb); log-log interpolation; below the first point it is held at the first point's value
    (Z rises with the pulse, so this bounds it from above)."""
    pts, top = [], 0.0
    for t, z in J["fig4"]["points_s_kw"]:
        top = max(top, float(z))                      # Z never falls with a longer pulse: the reading's dips past the plateau are not used
        pts.append((float(t), top))
    return pts


def zjmb_at(pts, scale, rmax, t):
    if t <= pts[0][0]:
        return pts[0][1] * scale
    if t >= pts[-1][0]:
        return rmax
    for (t0, z0), (t1, z1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            fr = (math.log(t) - math.log(t0)) / (math.log(t1) - math.log(t0))
            return min(rmax, scale * math.exp(math.log(z0) + fr * (math.log(z1) - math.log(z0))))
    return rmax


def dock_rise(zf, i0, tau, vsd, is_t, k, dt=0.2e-6, span=300e-6):
    """The junction rise of ONE FET carrying the whole docking pulse i0 exp(-t/tau) through its body diode (no sharing assumed),
    P = k VF(i) i with VF(i) at most max(VSD, VSD i / IS_test): VF is concave in i through the origin, so VF(i)/i does not rise with
    i above the printed point (INFERRED); k scales the printed 25 C point for a hot junction. Superposition on zf. Returns the
    largest rise, the energy and the peak power."""
    n = int(span / dt)
    P = []
    for j in range(n):
        i = i0 * math.exp(-j * dt / tau)
        P.append(k * max(vsd, vsd * i / is_t) * i)
    zg = [zf((j + 1) * dt) for j in range(n)]
    dP = [P[0]] + [P[j] - P[j - 1] for j in range(1, n)]
    best, t_best = 0.0, 0.0
    for m in range(n):
        s = 0.0
        for j in range(m + 1):
            s += dP[j] * zg[m - j]
        if s > best:
            best, t_best = s, (m + 1) * dt
    return best, sum(P) * dt, P[0], t_best


def fix16_round(R, T):
    """The review of the provisional fixes (2 October 2026): L4-F02 keeps B2 open (RDS(on) at 8.5 V inferred, the transient shape
    borrowed from AOS, Ciss typical against TI's 5 nF, the docking pulse converted into an I2t the sheet does not print) and
    L4-F03 finds the dock's new VSYS contact without branch protection."""
    H, Q0, K = R["H"], R["H"]["Q"], R["K"]
    sel = K["sel"]
    nxp = sel["rdef"]
    L = {}
    J = json.load(open(os.path.join(TOP, REC, "inputs", F16_READ), encoding="utf-8"))
    if J["sha256"] != PINS["buk6y10"][1]:
        refuse(4, "the figure readings name another BUK6Y10-30P sheet")
    nx = "\n".join(pdf_pages("buk6y10", True))
    L["rthmb"] = nxp["rthmb"]
    m = need(nx, r"VSD\s+source-drain voltage\s+IS = -(\d+) A; VGS = 0 V; Tj = 25 °C\s+-\s+-([\d.]+)\s+-([\d.]+)\s+V", "BUK6Y10-30P's VSD")
    L["vsd_is"], L["vsd_max"] = f(m, 1), f(m, 3)
    m = need(nx, r"IS\s+source current\s+Tmb = 25 °C\s+-\s+-(\d+)\s+A", "BUK6Y10-30P's IS")
    L["is_dc"] = f(m)
    need(nx, r"Fig\. 4\.\s+Transient thermal impedance from junction to mounting base as a function of pulse duration", "Fig. 4")
    need(nx, r"Fig\. 12\. Input, output and reverse transfer capacitances", "Fig. 12")
    pts = zjmb_table(J)
    L["plateau"] = float(J["fig4"]["plateau_kw"])
    if abs(max(z for _t, z in pts) - L["plateau"]) > 1e-9 or not all(a[1] <= b[1] + 1e-9 for a, b in zip(pts, pts[1:9])):
        refuse(4, "the Fig. 4 reading is not a rising curve with the stated plateau")
    L["zscale"] = L["rthmb"] / L["plateau"]
    zf = lambda t: zjmb_at(pts, L["zscale"], L["rthmb"], t)
    L["zf"] = zf
    L["z"] = {t: zf(t) for t in (2.44e-4, 0.02, 1.0, 60.0)}
    # ---- objection 1: what the sheet prints, and the allowance
    L["r10_hot"], L["r45_25"], L["r10_25"] = nxp["r10_hot"] * 1e-3, nxp["r45_25"] * 1e-3, nxp["r10_25"] * 1e-3
    L["ra"] = F16_RA
    if abs(F16_RA - sel["rb"]) > 1e-6:
        refuse(4, "the allowance is not section 15c's figure")
    # ---- objection 2: the events on the device's own Zth(j-mb) and the installed pair's self and mutual impedance
    ocd1 = Q0["ocd1"]
    ocd2 = [(i_, t_) for lab, i_, t_, _v, _a, _h in Q0["prot"] if lab == "the image's OCD2"][0]
    aold = [(i_, t_) for lab, i_, t_, _v, _a, _h in Q0["prot"] if lab == "the AFE's AOLD"][0]
    ascd = [(i_, t_) for lab, i_, t_, _v, _a, _h in Q0["prot"] if lab == "the image's ASCD"][0]
    air = K["air"]["route"]

    def plan(ra, zsum=None):
        pb = lambda i: (i / 2.0) ** 2 * ra                     # per FET: the even split bounds each FET's power (section 15c)
        if zsum is None:
            zsum = (F16_TJ_HELD - air) / pb(ocd1[0])            # (Zself + Zmut) steady: 20 A held reaches the held ceiling
        pre10 = air + pb(10.0) * zsum
        tj18 = pre10 + (pb(Q0["i_peak"]) - pb(10.0)) * zsum     # no transient credit at 60 s
        ev = []
        for lab, (i_, t_) in (("OCD2 %s A for %s s" % (fmt(ocd2[0], 0), fmt(ocd2[1], 0)), ocd2), ("AOLD %s A for %s ms" % (fmt(aold[0], 0), fmt(aold[1] * 1e3, 0)), aold),
                              ("ASCD %s A for %s us" % (fmt(ascd[0], 1), fmt(ascd[1] * 1e6, 0)), ascd)):
            dp = pb(i_) - pb(ocd1[0])
            allow = (150.0 - F16_TJ_HELD) / dp
            ev.append((lab, i_, t_, pb(i_), allow, zf(t_), allow - zf(t_)))
        return dict(pb10=pb(10.0), pb18=pb(Q0["i_peak"]), pb20=pb(ocd1[0]), zsum=zsum, pre10=pre10, tj18=tj18, ev=ev,
                    tj20=air + pb(ocd1[0]) * zsum,
                    pre_ldo=(150.0 - air) / zsum / K["i_pre"])
    L["plan"] = plan(F16_RA)
    L["plan_alt"] = plan(F16_RA_ALT)
    L["plan_miss"] = plan(F16_RA_ALT, L["plan"]["zsum"])       # parts at 25 mOhm on a board built to the allowance's sum
    L["ldo_floor16"] = H["smin_hi"] - L["plan"]["pre_ldo"]
    # ---- objection 3: Ciss
    L["ciss_t"] = nxp["ciss"]
    L["ciss_0"] = float(J["fig12"]["ciss_typ_pf_at_vds_minus_0v1"]) * 1e-12
    m = find("bq25730", r"RBATDRV_OFF\s+10 µA current from\s+([\d.]+)\s+([\d.]+)\s+kΩ", "RBATDRV_OFF", layout=True)
    L["roff"] = (f(m[1], 1) * 1e3, f(m[1], 2) * 1e3)
    L["ciss_p"] = find("bq25730", r"the Ciss of\s+P-channel MOSFET should be chosen less than 5 nF\.", "TI's Ciss rule", layout=True)[0]
    L["tau_on"] = (H["rdrv"][1] * 2 * L["ciss_t"], H["rdrv"][1] * 2 * L["ciss_0"])
    L["tau_off"] = L["roff"][1] * 2 * L["ciss_0"]
    L["one_rja"] = (F16_TJ_HELD - air) / (ocd1[0] ** 2 * F16_RA)
    # ---- objection 4: the docking pulse, the whole of it in one FET, from the hot air
    L["dock_k1"] = dock_rise(zf, Q0["i_dock"], Q0["tau"], L["vsd_max"], L["vsd_is"], 1.0)
    L["k_max"] = (150.0 - air) / L["dock_k1"][0]
    L["vf_pk_bound"] = L["vsd_max"] * Q0["i_dock"] / L["vsd_is"]
    L["t_over_is"] = Q0["tau"] * math.log(Q0["i_dock"] / L["is_dc"])
    L["i_at_tp"] = Q0["i_dock"] * math.exp(-nxp["ism_tp"] / Q0["tau"])
    # ---- L4-F03: the branch protection for the dock's VSYS contact
    tp = "\n".join(pdf_pages("tps1663", True))
    m = need(tp, r"R\(ILIM\) = 30kΩ, V\(IN\) \u2013 V\(OUT\) = 1V\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+A", "I(OL) at 30 kOhm")
    r30 = (f(m, 1), f(m, 2), f(m, 3))
    m = need(tp, r"R\(ILIM\) = 9kΩ, V\(IN\) \u2013 V\(OUT\) = 1V\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+A", "I(OL) at 9 kOhm")
    r9 = (f(m, 1), f(m, 2), f(m, 3))
    need(tp, r"IOL = R 18", "Equation 6")
    m = need(tp, r"IN to OUT total ON resistance\s+(\d+)\s+([\d.]+)\s+(\d+)\s+mΩ", "RON over temperature")
    L["ron"] = (f(m, 1) * 1e-3, f(m, 2) * 1e-3, f(m, 3) * 1e-3)
    m = need(tp, r"tCL_PLIM\(dly\)\s+(\d+)\s+(\d+)\s+(\d+)\s+ms", "tCL_PLIM(dly)")
    L["tcl"] = (f(m, 1) * 1e-3, f(m, 3) * 1e-3)
    m = need(tp, r"t\(TSD_retry\)\s+Retry delay in TSD\s+MODE = GND\s+(\d+)\s+(\d+)\s+(\d+)\s+ms", "t(TSD_retry)")
    L["tretry"] = (f(m, 1) * 1e-3, f(m, 3) * 1e-3)
    m = need(tp, r"Soft short response\s+I\(FASTTRIP\) < I\(OUT\) < I\(SCP\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+µs", "the soft-short response")
    L["tsoft"] = f(m, 3) * 1e-6
    L["iscp"] = f(need(tp, r"I\(SCP\)\s+Short Circuit Protect current\s+(\d+)\s+A", "I(SCP)"))
    L["thot"] = f(need(tp, r"Hot-short response time\s+I\(OUT\) > I\(SCP\)\s+(\d+)\s+µs", "the hot-short response")) * 1e-6
    L["iq"] = f(need(tp, r"Enabled: V\(SHDN\) = 2V\s+([\d.]+)\s+([\d.]+)\s+mA", "IQ(ON)"), 2) * 1e-3
    m = need(tp, r"T\(J_REG\)\s+Thermal regulation set point\s+(\d+)\s+(\d+)\s+(\d+)", "T(J_REG)")
    L["tjreg"] = (f(m, 1), f(m, 3))
    need(tp, r"tdVdT = 20\.8 × 103 × V IN × C dVdT", "Equation 2")
    need(tp, r"auto-retries after a\s.*?delay of t\(TSD_retry\)", "Table 8-1, MODE to GND", re.S)
    need(tp, r"UL 2367 recognized", "UL 2367")
    L["ilim_typ"] = 18.0 / F16_RILIM_K
    rel = max(r9[2] / r9[1] - 1, r30[2] / r30[1] - 1, 1 - r9[0] / r9[1], 1 - r30[0] / r30[1])
    L["ilim_rel"] = rel
    L["ilim"] = (L["ilim_typ"] * (1 - rel) / (1 + F16_RILIM_TOL), L["ilim_typ"] * (1 + rel) / (1 - F16_RILIM_TOL))
    sp = importlib.util.spec_from_file_location("dock_contacts_pinned16", read("dock_py"))
    dc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(dc)
    L["c813"] = dc.PD_MAX
    L["r813"] = dc.R_813_PATH * 1e-3
    L["rise_lim"] = dc.rise_813(L["ilim"][1])
    L["t_lim"] = {k: a + L["rise_lim"] for k, a in dc.AIR.items()}
    L["duty"] = L["tcl"][1] / (L["tcl"][1] + L["tretry"][0])
    vt, it = F16_OVL[1], F16_OVL[0]
    L["ovl_r"] = vt / it
    L["ovl_p"] = (vt - L["ilim"][1] * L["ovl_r"]) * L["ilim"][1]
    L["c_e"] = 10e-6                                  # C31 10 uF 25 V 1210 (gen_sch_e.py; the only capacitor on VSYS_E)
    L["t_ramp"] = (20.8e3 * K["vsys_sup"] * F16_CDVDT * (1 - F16_CDVDT_TOL), 20.8e3 * H["vsys_top"] * F16_CDVDT * (1 + F16_CDVDT_TOL))
    L["i_inrush"] = L["c_e"] / (20.8e3 * F16_CDVDT * (1 - F16_CDVDT_TOL))
    # the 2 A MINI 58 V fuse (0997, held) and the PTC MF-MSMF150/24X (Bourns, held) on their printed rows
    fz = flat(text_pdf("fuse997"))
    m = need(fz, r"0997002_ 2 0\.5 (\d+) ([\d.]+) ([\d.]+)", "the 0997 2 A row")
    L["fuse_r"], L["fuse_i2t"] = f(m, 2) * 1e-3, f(m, 3)
    m = need(fz, r"110 360 000 / - 135 ([\d.]+) / (\d+) 200 ([\d.]+) / (\d+) 350 ([\d.]+) / ([\d.]+)", "the 0997 time-current rows")
    L["fuse_tc"] = dict(t135=f(m, 2), t200=f(m, 4), t350=f(m, 6))
    m = need(fz, r"2A 2\.0 2\.0 2\.0 1\.9 1\.7 (1\.6) (1\.4) 1\.3", "the 0997 2 A derating row")
    L["fuse_der"] = (f(m, 1), f(m, 2))
    pt = flat(text_pdf("msmf"))
    m = need(pt, r"MF-MSMF150/24X (\d+) (\d+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)", "MF-MSMF150/24X's row")
    L["ptc"] = dict(vmax=f(m, 1), imax=f(m, 2), ihold=f(m, 3), itrip=f(m, 4), r1max=f(m, 6))
    m = need(pt, r"MF-MSMF150/24X ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) MF", "MF-MSMF150/24X's derating")
    L["ptc_h"] = {-40: f(m, 1), 70: f(m, 8)}
    L["ptc_trip_cold"] = L["ptc"]["itrip"] * L["ptc_h"][-40] / L["ptc"]["ihold"]
    # the feed's drop at the supplement floor: the eFuse, the 813 path at w3de's 2:1 spread, and the ground return's shift
    i_g = K["ret"][3][2]
    L["drop"] = K["aux_a"] * (L["ron"][2] + L["r813"] * F16_SPREAD) + i_g * L["r813"]
    L["vsys_e_min"] = K["vsys_sup"] - L["drop"]
    L["vsys_e_start"] = H["floor"] - L["drop"]
    return L


def text_pdf(key):
    return "\n".join(pdf_pages(key, True))


def render_fix16(R, p):
    K, H, Q0, L = R["K"], R["H"], R["H"]["Q"], R["L"]
    sel, pl, pa = K["sel"], R["L"]["plan"], R["L"]["plan_alt"]
    air = K["air"]["route"]
    p("16. THE FIX ROUND FOR THE REVIEW OF THE PROVISIONAL FIXES (L4-F02 and L4-F03; a qualification gap, not a demonstrated failure)")
    p("   16a. L4-F02 OBJECTION 1: RDS(on) AT BATDRV'S LEAST DRIVE (BATDRV %s / %s / %s V, SLUSE65A p.17; the source on VSYS, so VGS is minus that)"
      % (fmt(H["drv"][0], 1), fmt(H["drv"][1], 0), fmt(H["drv"][2], 1)))
    p("     printed by the BUK6Y10-30P (17 April 2020, Table 7, p.6): at most %s mOhm at -10 V and 25 C, %s mOhm at -10 V and 175 C, %s mOhm at -4.5 V"
      % (fmt(L["r10_25"] * 1e3, 0), fmt(L["r10_hot"] * 1e3, 0), fmt(L["r45_25"] * 1e3, 0)))
    p("       and 25 C; no maximum at a gate drive under 10 V above 25 C, so no printed point bounds the operating point (-8.5 V, hot) (MAKER)")
    p("     the %s mOhm of 15c is WITHDRAWN AS A BOUND: it is kept as the ALLOWANCE each FET is sized to (SESSION), and E11-36 confirms it on"
      % fmt(L["ra"] * 1e3, 3))
    p("       parts (RDS(on) at -8.5 V and 150 C, at most %s mOhm) or reverses it; at the sheet's largest printed maximum, %s mOhm, every figure below"
      % (fmt(L["ra"] * 1e3, 3), fmt(F16_RA_ALT * 1e3, 0)))
    p("       scales by %s (printed beside it); parts at %s mOhm on a board built to the allowance would take 20 A held to %s C and the service to"
      % (fmt(F16_RA_ALT / L["ra"], 4), fmt(F16_RA_ALT * 1e3, 0), fmt(L["plan_miss"]["tj20"], 1)))
    p("       %s C, so E11-36 gates E11-29 (SESSION, CONDITIONAL)" % fmt(L["plan_miss"]["tj18"], 1))
    p("     searched: SQJ403EP (held), AONS21357 (held), SQJ407EP (Vishay 62806 Rev. B, filed held) and PXP9R1-30QL (Nexperia, 5 January 2021, filed")
    p("       held) print their hot maxima at -10 V only; no part read prints one at |VGS| of 8.5 V or less above 25 C (MAKER)")
    p("     STATUS: CONDITIONAL on E11-36 (the measurement, or Nexperia's maximum at the point, filed) (SESSION)")
    p("   16b. L4-F02 OBJECTION 2: THE DEVICE'S OWN TRANSIENT IMPEDANCE AND THE TWO FETS' COUPLING")
    p("     Fig. 4 (p.5), the duty-cycle 0.01 curve (above any single pulse), read on the rendered page (inputs/%s): its plateau %s K/W, scaled by"
      % (F16_READ, fmt(L["plateau"], 4)))
    p("       %s to Table 6's maximum Rth(j-mb) %s K/W: Zth(j-mb) %s K/W at 244 us, %s at 20 ms, %s at 1 s, %s at 60 s (MAKER, read; INFERRED scale)"
      % (fmt(L["zscale"], 4), fmt(L["rthmb"], 1), fmt(L["z"][2.44e-4], 4), fmt(L["z"][0.02], 4), fmt(L["z"][1.0], 4), fmt(L["z"][60.0], 4)))
    p("     AOS's Figure 14 shape is no longer used for these FETs. The installed path is stated as what a bench reads: each FET's self impedance")
    p("       Zself(t) (heat one, read its own junction) and the mutual Zmut(t) (heat one, read the other); then for any split of the pair's current")
    p("       TJ <= air + Pb x (Zself + Zmut)(t), Pb the even split's per-FET power at the allowance (it bounds each FET's power, 15c); Zself includes")
    p("       the device's own Zth(j-mb); the coupling is in the sum, not assumed away (INFERRED)")
    p("     the plan at the +%s C mixed air (SESSION): 20 A held under OCD1 reaches %s C at most (10 K under the 150 C limit kept for the pulses), so"
      % (fmt(air, 0), fmt(F16_TJ_HELD, 0)))
    p("       the installed (Zself + Zmut) at steady state at most %s K/W (%s at %s mOhm); per-FET power %s W at 10 A, %s W at 18 A, %s W at 20 A (INFERRED)"
      % (fmt(pl["zsum"], 2), fmt(pa["zsum"], 2), fmt(F16_RA_ALT * 1e3, 0), fmt(pl["pb10"], 4), fmt(pl["pb18"], 4), fmt(pl["pb20"], 4)))
    p("     THE SERVICE, 18 A FOR 60 S FROM THE HOT STATE (10 A held at the +%s C air, no board capacity credited, so 60 s counts as steady): TJ %s C,"
      % (fmt(air, 0), fmt(pl["tj18"], 1)))
    p("       from %s C at 10 A held, %s K under the limit; the 18 A for 60 s is kept and no protection is lowered (INFERRED, CONDITIONAL on E11-29, E11-36)"
      % (fmt(pl["pre10"], 1), fmt(150.0 - pl["tj18"], 1)))
    p("     the fault histories from the held 20 A (each a step from the %s C ceiling to the 150 C limit): the allowance on the installed sum at the" % fmt(F16_TJ_HELD, 0))
    p("       event's width, against the device's own Zth(j-mb) at that width (INFERRED):")
    for (lab, i_, t_, pb, allow, zd, room), alt in zip(pl["ev"], pa["ev"]):
        p("       %s: per FET %s W; (Zself + Zmut) at %s s at most %s K/W (%s at %s mOhm), the device alone %s K/W, so %s K/W for the board and the coupling"
          % (lab, fmt(pb, 3), fmt(t_, 6), fmt(allow, 3), fmt(alt[4], 3), fmt(F16_RA_ALT * 1e3, 0), fmt(zd, 4), fmt(room, 3)))
    p("     the LDO-mode precharge, one FET linear with %s A: under the plan's steady sum it stays at 150 C down to SRN %s V, so R-b' (no charge under"
      % (fmt(K["i_pre"], 5), fmt(L["ldo_floor16"], 3)))
    p("       %s V) keeps its margin (INFERRED)" % fmt(K["rb_floor"], 1))
    p("     STATUS: the analysis basis is the device's own and the coupling explicit; the qualification is CONDITIONAL on E11-29's measured Zself and")
    p("       Zmut at the five widths (SESSION)")
    p("   16c. L4-F02 OBJECTION 3: Ciss AGAINST TI'S 5 nF (SLUSE65A p.%d), FROM PRINTED DATA" % L["ciss_p"])
    p("     the BUK6Y10-30P prints Ciss as a typical only: %s nF at -15 V (Table 7), no maximum, no spread; Fig. 12 (typical) reads about %s nF at -0.1 V,"
      % (fmt(L["ciss_t"] * 1e9, 2), fmt(L["ciss_0"] * 1e9, 2)))
    p("       the battery FET's working point (on, or an ideal diode at 30 mV): the pair %s nF at -15 V and about %s nF near 0 V (MAKER, read)"
      % (fmt(2 * L["ciss_t"] * 1e9, 2), fmt(2 * L["ciss_0"] * 1e9, 2)))
    p("     TI states the drive, not the requirement behind 5 nF: RBATDRV_ON at most %s kOhm, RBATDRV_OFF at most %s kOhm; into the pair's typical"
      % (fmt(H["rdrv"][1] / 1e3, 0), fmt(L["roff"][1] / 1e3, 1)))
    p("       Ciss the turn-on time constant is %s us at -15 V and %s us near 0 V, the turn-off %s us; no printed limit to compare them with (MAKER, INFERRED)"
      % (fmt(L["tau_on"][0] * 1e6, 2), fmt(L["tau_on"][1] * 1e6, 2), fmt(L["tau_off"] * 1e6, 2)))
    p("     so the pair's 4.72 nF meets TI's figure only at the maker's test point and as a typical; near 0 V the typical curve is over it: NOT SHOWN")
    p("       on printed data (MAKER, INFERRED)")
    p("     the three approaches (at most three): (S1) the pair, kept: Ciss open (E11-37); (S2) one BUK6Y10-30P, Ciss about %s nF near 0 V (%s %% of 5 nF,"
      % (fmt(L["ciss_0"] * 1e9, 2), fmt(100 * L["ciss_0"] / H["bf_ciss"], 0)))
    p("       typical), but its installed junction-to-air at most %s K/W for 20 A held at the allowance, a path through the case rather than a board"
      % fmt(L["one_rja"], 2))
    p("       pour, with the docking pulse unchanged; (S3) a part whose sheet prints both: none found among the parts read (16a) (INFERRED)")
    p("     STATUS: OPEN; the pair stays selected (SESSION, it is the only arrangement whose heat a board can carry); E11-37: TI's statement of what")
    p("       5 nF bounds (Q-TI-17, drafted, not sent) or the bench's BATDRV behaviour with the pair, and an engineer's decision on (S1) or (S2) (SESSION)")
    p("   16d. L4-F02 OBJECTION 4: THE DOCKING PULSE (15c's reading of ISM's 320 A for 10 us as an I2t of 1.024 A2s is WITHDRAWN)")
    p("     the waveform: %s A peak, time constant %s us (the dependency round's pack loop, the discharge FET at once); it is over the continuous IS"
      % (fmt(Q0["i_dock"], 1), fmt(Q0["tau"] * 1e6, 1)))
    p("       %s A (Tmb 25 C) for %s us and still %s A when ISM's 10 us ends (MAKER, INFERRED)" % (fmt(L["is_dc"], 0), fmt(L["t_over_is"] * 1e6, 1), fmt(L["i_at_tp"], 1)))
    p("     no sharing is credited: the whole pulse in one FET (the sheet prints VSD's maximum, no minimum, so the split is not bounded) (SESSION)")
    p("     its junction from the +%s C air: P = VF x i with VF at most max(%s V, %s V x i / %s A), the printed 25 C maximum carried up by VF's"
      % (fmt(air, 0), fmt(L["vsd_max"], 1), fmt(L["vsd_max"], 1), fmt(L["vsd_is"], 0)))
    p("       concavity (%s V at the peak); superposed on Fig. 4 (scaled), the board below not added: a rise of %s K, TJ %s C, %s mJ, %s W at the peak (INFERRED)"
      % (fmt(L["vf_pk_bound"], 3), fmt(L["dock_k1"][0], 2), fmt(air + L["dock_k1"][0], 1), fmt(L["dock_k1"][1] * 1e3, 2), fmt(L["dock_k1"][2], 0)))
    p("       the largest rise comes at %s us: Fig. 4 is held at its first read point (12 us, %s K/W, %s %% of its steady value) below that width,"
      % (fmt(L["dock_k1"][3] * 1e6, 1), fmt(L["zf"](1.2e-5), 4), fmt(100 * L["zf"](1.2e-5) / L["rthmb"], 1)))
    p("       a bound and not a waveform; within 12 us the heat is still inside the package, so the board below cannot add to it (INFERRED)")
    p("     [HISTORICAL, overridden by 17b: this round judged the waveform past ISM's 10 us on the junction temperature alone; a temperature does")
    p("       not extend a printed pulse rating, so the whole hot waveform is accepted by 17b's qualification instead] (INFERRED)")
    p("     what the sheet does not print: VF above %s A or at a hot junction (TJ stays under 150 C while VF is at most %s times that bound), and ISM"
      % (fmt(L["vsd_is"], 0), fmt(L["k_max"], 3)))
    p("       at a mounting base over 25 C (the pulse's %s A peak is %s %% of 320 A at 25 C) (MAKER, INFERRED)" % (fmt(Q0["i_dock"], 1), fmt(100 * Q0["i_dock"] / sel["rdef"]["ism"], 1)))
    p("     STATUS: CONDITIONAL on E11-30 (VF at the docking current from +70 C and ISM's amplitude at a hot mounting base, from Nexperia or the")
    p("       bench); the constraint that would remove both, a slower discharge-FET turn-on on board P, interacts with the pack's ASCD turn-off and")
    p("       belongs to board P's owner (E11-30) (SESSION)")
    p("   16e. L4-F03: THE DOCK'S VSYS CONTACT, ITS BRANCH PROTECTION")
    p("     the branch: VSYS (VBAT) on board A to J_DOCK pin 1, one Preci-Dip 813 (%s A operating maximum; 85 C with its music-wire spring), 24 AWG"
      % fmt(L["c813"], 1))
    p("       and board E's copper to VSYS_E; 1.0 A declared; the review's counterexample %s A from %s V (%s Ohm) is over the contact and under every"
      % (fmt(F16_OVL[0], 0), fmt(F16_OVL[1], 1), fmt(L["ovl_r"], 2)))
    p("       upstream threshold, in source-only and battery operation alike (RECORD, INFERRED)")
    p("     (F) a fuse, Littelfuse 0997 MINI 2 A 58 V (held, rev. 11/18/2025): %s mOhm cold, I2t %s A2s; 110 %% never opens (360000 s minimum), 135 %%"
      % (fmt(L["fuse_r"] * 1e3, 2), fmt(L["fuse_i2t"], 1)))
    p("       within %s s, 200 %% within %s s, 350 %% within %s s; load allowed %s A at 60 C and %s A at 80 C: from 3.5 A (175 %%) to 4 A it may carry for up to"
      % (fmt(L["fuse_tc"]["t135"], 0), fmt(L["fuse_tc"]["t200"], 0), fmt(L["fuse_tc"]["t350"], 1), fmt(L["fuse_der"][0], 1), fmt(L["fuse_der"][1], 1)))
    p("       %s s (the 135 %% row's maximum) over the contact's 3.5 A, and under 2.7 A it need never open: it does not protect the contact (MAKER, INFERRED)"
      % fmt(L["fuse_tc"]["t135"], 0))
    p("     (P) a PTC, Bourns MF-MSMF150/24X (held): Vmax %s V, Imax %s A, hold %s A and trip %s A at 23 C; hold %s A at 70 C, under the 1.0 A load;"
      % (fmt(L["ptc"]["vmax"], 0), fmt(L["ptc"]["imax"], 0), fmt(L["ptc"]["ihold"], 2), fmt(L["ptc"]["itrip"], 2), fmt(L["ptc_h"][70], 2)))
    p("       hold %s A at -40 C, so trip about %s A there, over 3.5 A; and its %s A interrupt is under the pack's prospective current (MAKER, INFERRED)"
      % (fmt(L["ptc_h"][-40], 2), fmt(L["ptc_trip_cold"], 2), fmt(L["ptc"]["imax"], 0)))
    p("     (E) an eFuse, TI TPS16630 (SLVSET9G, held; 60 V, 31 mOhm, UL 2367 recognized): I(OL) = 18 / R(ILIM) (Equation 6, p.20); with R(ILIM)")
    p("       %s kOhm %s %%, %s A typical and, at the wider of the printed rows' spreads (9 and 30 kOhm, +-%s %% over TJ -40 to 125 C), %s to %s A"
      % (fmt(F16_RILIM_K, 1), fmt(F16_RILIM_TOL * 100, 1), fmt(L["ilim_typ"], 4), fmt(L["ilim_rel"] * 100, 1), fmt(L["ilim"][0], 4), fmt(L["ilim"][1], 4)))
    p("       (MAKER, INFERRED between rows); RON at most %s mOhm over TJ; current limiting for at most %s ms, then auto-retry after %s to %s ms (MODE"
      % (fmt(L["ron"][2] * 1e3, 0), fmt(L["tcl"][1] * 1e3, 0), fmt(L["tretry"][0] * 1e3, 0), fmt(L["tretry"][1] * 1e3, 0)))
    p("       to GND, Table 8-1); thermal regulation %s to %s C; a soft short off within %s us, a hot short (over %s A typical) in %s us typical (MAKER)"
      % (fmt(L["tjreg"][0], 0), fmt(L["tjreg"][1], 0), fmt(L["tsoft"] * 1e6, 1), fmt(L["iscp"], 0), fmt(L["thot"] * 1e6, 0)))
    p("     SELECTED (SESSION): (E) on board A between VBAT and J_DOCK pin 1 (a new net VSYS_DOCK; drafted in apply_gen_sch_a_charger.py); in a")
    p("       sustained overload the contact, the 24 AWG and the copper downstream see at most %s A (%s %% of 3.5 A); by w3de's assumed I2 rise, %s C at the 51 C air and %s C at the"
      % (fmt(L["ilim"][1], 3), fmt(100 * L["ilim"][1] / L["c813"], 1), fmt(L["t_lim"]["envelope 51 C"], 1), fmt(L["t_lim"]["margin 65 C"], 1)))
    p("       65 C margin, under the spring's 85 C; the load's 1.0 A is %s %% of the least limit (INFERRED, ASSUMPTION w3de)" % fmt(100 * 1.0 / L["ilim"][0], 1))
    p("     the cases, source-only and battery alike (the eFuse limits whatever feeds VSYS): overload (the 2.88 Ohm counterexample) held at %s A at most,"
      % fmt(L["ilim"][1], 3))
    p("       %s W in the eFuse until its timer, then off for at least %s ms: a duty of at most %s; a short, applied while on or present at the"
      % (fmt(L["ovl_p"], 1), fmt(L["tretry"][0] * 1e3, 0), fmt(L["duty"], 3)))
    p("       start, and the retry: section 17a (the first version's soft-short figure, built on the typical 45 A, is WITHDRAWN);")
    p("       inrush with C(dVdT) %s nF +-%s %%: %s to %s ms ramps (Equation 2), %s mA into C31's %s uF; recovery: auto-retry, board A reads"
      % (fmt(F16_CDVDT * 1e9, 0), fmt(F16_CDVDT_TOL * 100, 0), fmt(L["t_ramp"][0] * 1e3, 2), fmt(L["t_ramp"][1] * 1e3, 2), fmt(L["i_inrush"] * 1e3, 1), fmt(L["c_e"] * 1e6, 0)))
    p("       HOT-R1 lost meanwhile; the eFuse draws at most %s mA from VSYS: on the source while one carries the kit, on the pack otherwise, an"
      % fmt(L["iq"] * 1e3, 1))
    p("       addition to the always-on load, never to the held pack's drain (MAKER, INFERRED)")
    p("     the drop at the supplement floor %s V with 1.0 A: the eFuse %s mOhm, the 813 path %s mOhm at w3de's 2:1 spread, and the return's shift"
      % (fmt(K["vsys_sup"], 3), fmt(L["ron"][2] * 1e3, 0), fmt(L["r813"] * F16_SPREAD * 1e3, 1)))
    p("       (%s A on an 813 ground contact with one open): %s V, so VSYS_E at least %s V (%s V at VSYS_MIN's start); the AP63205 takes %s V and up;"
      % (fmt(K["ret"][3][2], 3), fmt(L["drop"], 4), fmt(L["vsys_e_min"], 3), fmt(L["vsys_e_start"], 3), fmt(K["ap_vin"][0], 1)))
    p("       the fans' least operating voltage is owed with their maximum (E11-35) (INFERRED, ASSUMPTION w3de)")
    p("     the held-pack drain (15a corrected): %s mA is the QUANTIFIED SUBSET (the monitor and D3 at 25 C); D3's hot leakage and the body diodes'"
      % fmt(K["held_bounded_a"] * 1e3, 4))
    p("       current are not bounded on held evidence; the bench acceptance stays at most %s mA (E11-31) (SESSION, CONDITIONAL)" % fmt(FIX_HELD_ACC * 1e3, 1))
    p("     check_contracts.py, the interface draft's second target, is in this tree (v2/ecad/tools/check_contracts.py) and the alias edit applies")
    p("       to it; the alias is now VSYS_DOCK and VSYS_E (RECORD)")
    p("     STATUS: sustained-overload remedy drafted; fault qualification open (section 17a, E11-38) (SESSION)")
    p("")

# ============================================================================================ the second review (L4-CP01 to L4-CP03) and the specimens
F17_L_IN = 20e-9        # H, SESSION (a layout requirement): U42's IN within 20 nH of C236 and C23 to C25
F17_FAN_RUN = 0.1       # A, each fan running (CELL_F's declaration, now VSYS_E's)
F17_DOCK_MARGIN = 1.1   # SESSION: the pulse qualification's margin on the docking waveform's peak and time constant
F17_DOCK_N = (2000, 6, 10.0)   # SESSION: pulses per part (a lifetime allowance of 1000 docking events, twice), parts, seconds apart
F17_TMB = 75.0          # C, SESSION: the qualification's mounting base, 5 K over the +70 C mixed air


def fix17_round(R, T):
    """The second external review (of the 22:30 checkpoint): L4-CP01 (U42's fault envelope: TI's 45 A is typical, a limiter's steady
    setting is no instantaneous ceiling, and the start into a short times out at 1.5 s, not 202 ms), L4-CP02 (a junction temperature
    does not extend a printed pulse rating: the whole hot docking waveform needs an applicable basis) and L4-CP03 (the charger draft's
    text); and the specimens for the measurement rows."""
    H, K, L, G = R["H"], R["K"], R["L"], R["G"]
    M = {}
    tp = "\n".join(pdf_pages("tps1663", True))
    m = need(tp, r"Hot-short response time\s+I\(OUT\) > I\(SCP\)\s+(\d+)\s+µs", "the hot-short response")
    M["hot_typ_only"] = True
    need(tp, r"I\(FASTRIP\)\s+Fast-trip comparator threshold\s+2xI\(OL\)\s+A", "I(FASTTRIP), a typical only")
    need(tp, r"I\(SCP\)\s+Short Circuit Protect current\s+45\s+A", "I(SCP), a typical only")
    m = need(tp, r"t\(Treg_timeout\)\s+Thermal Regulation Timeout\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+s", "t(Treg_timeout)")
    M["treg"] = (f(m, 1), f(m, 3))
    need(tp, r"When the device is started with short-circuit on the output, the current begins to limit at I\(OL\)\.", "8.3.4.2.1")
    need(tp, r"The fast-trip circuit holds the internal FET off for only a few microseconds, after which the device\s+turns back on slowly, allowing the current-limit loop to regulate the output current to I\(OL\)\.", "8.3.4.2")
    need(tp, r"Using a Schottky diode across the output and GND to absorb negative spikes", "9.4.1")
    need(tp, r"IN, P_IN, OUT\s+0\.1\s+µF", "the 0.1 uF minimum at IN, P_IN and OUT")
    m = need(tp, r"IN, P_IN, OUT, UVLO, FLT, PGOOD\s+\u20130\.3\s+(\d+)", "the absolute maximum at IN and OUT")
    M["abs_in"] = f(m)
    # case 2, a short applied while on: the resistive bound (no inductance credited, the contact's own resistance taken as 0)
    sp = importlib.util.spec_from_file_location("dock_contacts_pinned17", read("dock_py"))
    dc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(dc)
    M["r_path_min"] = (dc.R_813_PATH - dc.PD_R) * 1e-3
    M["i_pk"] = H["vsys_top"] / (L["ron"][0] + M["r_path_min"])
    M["i2t_pk"] = M["i_pk"] ** 2 * L["tsoft"]
    M["fast_typ"] = 2.0 * L["ilim"][1]
    # the input spike (TI's Equation 14) at the bound, with C236's stacked effective capacitance and printed ESR next to U42
    M["c_in"], M["esr_in"] = G["c_dir_eff"], G["esr181"]
    M["v_in_pk"] = H["vsys_top"] + M["i_pk"] * (math.sqrt(F17_L_IN / M["c_in"]) + M["esr_in"])
    # case 3, a start into a short, and case 4, the retry: the duty and the contact's average heating
    M["duty_start"] = M["treg"][1] / (M["treg"][1] + L["tretry"][0])
    M["duty_ovl"] = L["duty"]
    M["rise_retry"] = dc.rise_813(L["ilim"][1]) * max(M["duty_start"], M["duty_ovl"])
    M["rise_steady"] = dc.rise_813(L["ilim"][1])
    # the fans' start against U42's least limit and VSYS_E's floor at that current
    i_u12 = K["aux"]["U12"]
    M["fan_simul"] = (L["ilim"][0] - i_u12) / 2.0
    M["fan_stag"] = L["ilim"][0] - i_u12 - F17_FAN_RUN
    i_g = K["ret"][3][2]
    M["vsys_e_lim"] = K["vsys_sup"] - (L["ilim"][0] * (L["ron"][2] + L["r813"] * F16_SPREAD) + i_g * L["r813"])
    # CP02: the docking waveform's qualification envelope
    Q0 = H["Q"]
    M["dock_q"] = (Q0["i_dock"] * F17_DOCK_MARGIN, Q0["tau"] * F17_DOCK_MARGIN)
    M["dock_q_t80"] = M["dock_q"][1] * math.log(M["dock_q"][0] / L["is_dc"])
    # L4-QR01 (the owner's review of 3 October): what a specimen's result is (TI SPRA953D 1.2 and 1.8; Nexperia AN11158 2.4)
    M["spra_rev"] = need(text_pdf("spra953"), r"(SPRA953D) \u2013 DECEMBER 2003 \u2013 REVISED MARCH 2024", "SPRA953's revision").group(1)
    M["spra_p"] = (find("spra953", r"RθJA is not a constant", "SPRA953 1.2")[0], find("spra953", r"is a system-level\s+parameter that depends strongly on system parameters", "SPRA953 1.8", layout=True)[0])
    M["an_p"] = find("an11158", r"Operation outside of these conditions is not \w+, so it is recommended that these values", "AN11158 2.4", layout=True)[0]
    need(text_pdf("an11158"), r"Rev\. 7\.0 \u2014 18 February 2025", "AN11158's revision")
    # CP03: the claims the charger draft must no longer write
    M["withdrawn"] = ("bounded at 21.1", "34.4 C/W", "split between their body diodes")
    return M


def render_fix17(R, p):
    K, H, L, M = R["K"], R["H"], R["L"], R["M"]
    Q0 = H["Q"]
    p("17. THE SECOND REVIEW (L4-CP01 TO L4-CP03, of the 22:30 checkpoint) AND THE EVIDENCE SPECIMENS")
    p("   17a. L4-CP01: U42'S FAULT ENVELOPE BY CASE (G = printed limit, I = inferred, T = typical only; SLVSET9G pp.7 to 10, 20 to 22, 26, 30, 31)")
    p("     the setting: I(OL) %s to %s A at R(ILIM) %s kOhm (I: between the printed 9 and 30 kOhm rows, each G over TJ -40 to 125 C at VIN - VOUT"
      % (fmt(L["ilim"][0], 4), fmt(L["ilim"][1], 4), fmt(F16_RILIM_K, 1)))
    p("       1 V); a regulated, steady setting, NOT an instantaneous ceiling; the fast-trip threshold 2 x I(OL) and I(SCP) 45 A are T only (MAKER)")
    p("     (1) operating overload, I(OL) < I < I(FASTTRIP): held at the setting once the loop settles (the settling's peak is not printed); limiting for")
    p("       at most %s ms (G), then off %s to %s ms (G) and a retry; a duty of at most %s; the contact at most %s A steady, %s K by w3de's rise (I)"
      % (fmt(L["tcl"][1] * 1e3, 0), fmt(L["tretry"][0] * 1e3, 0), fmt(L["tretry"][1] * 1e3, 0), fmt(M["duty_ovl"], 3), fmt(L["ilim"][1], 3), fmt(M["rise_steady"], 2)))
    p("     (2) a short applied while on: the current rises from VSYS's local capacitance (C236 and C23 to C25, the source's impedance behind them)")
    p("       until the fast trip; turn-off %s to %s us under I(SCP) (G, from a threshold that is T), about 1 us over it (T); then the device turns back"
      % (fmt(2.2, 1), fmt(L["tsoft"] * 1e6, 1)))
    p("       on slowly into case (1) (p.21). A resistive EXTRAPOLATION, not a bound (I): %s A would flow if VSYS's %s V stood over RON's printed"
      % (fmt(M["i_pk"], 1), fmt(H["vsys_top"], 3)))
    p("       least %s mOhm and the path's %s mOhm with the contact at 0 and no inductance; TI prints RON at 0.6 to 6 A only (p.9), not at hundreds of"
      % (fmt(L["ron"][0] * 1e3, 0), fmt(M["r_path_min"] * 1e3, 1)))
    p("       amperes, so the FET's resistance there, its saturation and the loop's inductance are not printed: %s A for %s us (%s A2s) is E11-38's TEST"
      % (fmt(M["i_pk"], 1), fmt(L["tsoft"] * 1e6, 1), fmt(M["i2t_pk"], 3)))
    p("       TARGET for the recorded peak, and a reading over it revises the figure; the 813 prints no pulse rating, so the contact, the 24 AWG and the")
    p("       clamp are left to the bench's qualification (E11-38), not bounded (MAKER, INFERRED)")
    p("     the pins: IN at most %s V by TI's Equation 14 at that extrapolation with U42 within %s nH of C236 (%s uF effective, ESR %s mOhm printed) against"
      % (fmt(M["v_in_pk"], 1), fmt(F17_L_IN * 1e9, 0), fmt(M["c_in"] * 1e6, 1), fmt(M["esr_in"] * 1e3, 0)))
    p("       the absolute %s V (I; the 20 nH a layout requirement, SESSION); OUT's negative spike through the output loop's inductance clamped by a"
      % fmt(M["abs_in"], 0))
    p("       Schottky D23 at OUT (TI 9.4.1, 9.5.1); OUT's -0.3 V absolute minimum is not shown under a clamp at hundreds of amperes: left to the bench (E11-38,")
    p("       Q-TI-18) (MAKER, INFERRED)")
    p("     (3) a start into a pre-existing short: limited at I(OL) from the start until the junction reaches T(J_REG) %s to %s C (G), then regulated"
      % (fmt(L["tjreg"][0], 0), fmt(L["tjreg"][1], 0)))
    p("       to a lower current for the TIMEOUT t(Treg_timeout) %s to %s s (G), then off (p.22). The timeout starts when regulation begins; the time"
      % (fmt(M["treg"][0], 2), fmt(M["treg"][1], 1)))
    p("       to reach it (VIN x I(OL) into the package from the air) and the regulated current are NOT PRINTED, so the TOTAL duration and the energy")
    p("       into the contact are not bounded by printed data; the setting's row is printed at VIN - VOUT 1 V, not at the %s V a short puts across U42:"
      % fmt(H["vsys_top"], 1))
    p("       the current at that bias, the pre-regulation interval and the regulated current are E11-38's (d) (MAKER, INFERRED)")
    p("     (4) repeated retry into a persistent short: each cycle is case (3), off at least %s ms (G) between; the cycle's on-time is not bounded (3),"
      % fmt(L["tretry"][0] * 1e3, 0))
    p("       so no duty is claimed (the %s of the first version, from the timeout alone, is WITHDRAWN); what is bounded: after the first microseconds the"
      % fmt(M["duty_start"], 3))
    p("       current never exceeds the setting, so at any duty the contact's heating is at most case (1)'s %s K by w3de's rise (I); an intermittent"
      % fmt(M["rise_steady"], 2))
    p("       short applied and removed faster than the retry, and the recovery between, are not bounded by the device's timers: E11-38's (h) (INFERRED)")
    p("     the fans' start, against U42's least limit %s A with U12's %s A: both together at most %s A each, one at a time at most %s A (one other"
      % (fmt(L["ilim"][0], 3), fmt(K["aux"]["U12"], 1), fmt(M["fan_simul"], 4), fmt(M["fan_stag"], 4)))
    p("       running at %s A); VSYS_E at that current at least %s V at the supplement floor: the fans must start at or under it (E11-35, E11-39) (INFERRED)"
      % (fmt(F17_FAN_RUN, 1), fmt(M["vsys_e_lim"], 3)))
    p("     the hotter interval: the current U42 regulates while at T(J_REG) is NOT PRINTED (under the setting, how far unknown): E11-38's (d) (MAKER)")
    p("     STATUS: sustained-overload remedy drafted; fault qualification open (E11-38: histories a to h, the pin excursions, the wiring's and copper's")
    p("       integrity, the contact body at or under 85 C); not evidence of a failure (SESSION)")
    p("   17b. L4-CP02: THE WHOLE HOT DOCKING WAVEFORM (a junction temperature does not extend ISM's printed 10 us at Tmb 25 C)")
    p("     the waveform to accept: %s A peak, time constant %s us, over IS's %s A for %s us, from a +%s C mounting base, once per docking event"
      % (fmt(Q0["i_dock"], 1), fmt(Q0["tau"] * 1e6, 1), fmt(L["is_dc"], 0), fmt(L["t_over_is"] * 1e6, 1), fmt(K["air"]["route"], 0)))
    p("     (D1) Nexperia's written acceptance of that waveform (Q-NXP-1, drafted, not sent): no circuit change; outside this project's control")
    p("     (D2) a defined pulse qualification on parts: %s A peak and %s us (x%s), mounting base %s C, %d pulses %s s apart on each of %d parts"
      % (fmt(M["dock_q"][0], 1), fmt(M["dock_q"][1] * 1e6, 1), fmt(F17_DOCK_MARGIN, 1), fmt(F17_TMB, 0), F17_DOCK_N[0], fmt(F17_DOCK_N[2], 0), F17_DOCK_N[1]))
    p("       (over IS for %s us); no circuit change; within its stated scope (a sample, not a production limit) (SESSION)" % fmt(M["dock_q_t80"] * 1e6, 1))
    p("     (D3) board P bounds the inrush (a slower discharge-FET turn-on or a precharge path): changes the pack's protection path, whose ASCD")
    p("       turn-off and normal charging must be re-shown; board P's owner, a draft for board P's generator (INFERRED)")
    p("     SELECTED (SESSION): (D2), with (D1) asked in parallel; (D3) only if (D2) fails, as E11-30 states; STATUS: CONDITIONAL on E11-30 (SESSION)")
    p("   17d. L4-QR01 (the owner's review of 3 October): a junction-to-air figure belongs to the board and its environment (TI %s 1.2, p.%d: \"RθJA"
      % (M["spra_rev"], M["spra_p"][0]))
    p("     is not a constant\"; 1.8, p.%d: \"a system-level parameter\"), and a maker's limiting value holds under its stated conditions only (Nexperia"
      % M["spra_p"][1])
    p("     AN11158 Rev. 7.0 2.4, p.%d: operation outside the stated conditions carries no assurance from the maker): each specimen's transfer rule is the record's 17d"
      % M["an_p"])
    p("     block (thermal boundaries, uncertainty, permitted extrapolation, the comparison rule, the re-test triggers); the six-sample pulse test is")
    p("     prototype evidence for its lot and conditions, not a production limit (MAKER, RECORD)")
    p("   17c. L4-CP03: apply_gen_sch_a_charger.py's text now writes the allowance, the 33.12 K/W self-plus-mutual target and no sharing credited;")
    p("     the three withdrawn statements are absent from the text it writes (tested) (RECORD)")
    p("")

# ============================================================================================ the fans' feed (Layer 7's F-L7-01, F-L7-02, F-L7-04)
# Layer 7's record (fnd/l7pwr 2087060b, v2/docs/records/l7pwr/L7-FANS-AND-TH1.md sections 2d, 2e, 2f and 5; not in this tree, cited,
# not pinned): the mixers Sanyo Denki 9WL0612P4H001 (two, board E J_FAN1 and J_FAN2) and the coolers 9WPA0412P6G001 (three, board B),
# both 12 V with a printed operating range of 10.8 to 13.2 V, 0.17 A each at 12 V, pulse sensor and PWM input, IP68, -20 to +70 C;
# no fan read prints a range covering VSYS_E's 9.494 to 17.375 V. RECORD (Layer 7), MAKER through it.
L7_FAN = dict(mpn_mixer="9WL0612P4H001", mpn_cooler="9WPA0412P6G001", v=12.0, v_lo=10.8, v_hi=13.2, i=0.17, n_mixer=2, n_cooler=3,
              rec="v2/docs/records/l7pwr/L7-FANS-AND-TH1.md", commit="2087060b")
F18_ETA = 0.85          # ASSUMPTION (SESSION): the fan rail's efficiency at the floor, read 5 points under the LTC3115-1's typical TA04b curves
F18_IQ_PWM = 0.016      # A, the LTC3115-1's PWM-mode no-load input current at VOUT 12 V near 9 V in (Figure G11, typical, read)
F18_RUN = (1.5e6, 255e3)   # ohm, SESSION: the RUN divider (TA04's 255k kept; R1 1.5M for an enable under the floor)
F18_FB = (1.0e6, 90.9e3)   # ohm, TA04's divider: 12.0 V from the 1.000 V reference
F18_FB_TOL = 0.01          # the drafted 1 % divider resistors
F18_PLAN_W = 1.44       # W, the plan's power for both mixers (Layer 7 2f, from pwr_budget.py's rows)


def fix18_round(R, T):
    """Layer 7 settled D-18 on 12 V IP68 fans whose printed range no supply in the kit covers as drawn: the mixers get a regulated 12.0 V
    rail on board E from VSYS_E (this record's B1 topology kept), the branch's declared current and U42's setting are re-derived with the
    rail's input at the floor, and board B's cooler feed is answered as a finding for its owner."""
    H, K, L, M = R["H"], R["K"], R["L"], R["M"]
    N = {}
    lt = "\n".join(pdf_pages("ltc3115", True))
    m = need(lt, r"Input Operating Voltage\s+l\s+([\d.]+)\s+(\d+)", "the LTC3115-1's input range")
    N["vin"] = (f(m, 1), f(m, 2))
    m = need(lt, r"Inductor Current Limit\s+\(Note 3\)\s+l\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+A", "the inductor current limit")
    N["ilim"] = (f(m, 1), f(m, 2), f(m, 3))
    N["tss"] = f(need(lt, r"Soft-Start Duration\s+(\d+)\s+ms", "the soft-start")) * 1e-3
    m = need(lt, r"Feedback Voltage\s+l\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "the feedback voltage")
    N["vfb"] = (f(m, 1) * 1e-3, f(m, 2) * 1e-3, f(m, 3) * 1e-3)
    m = need(lt, r"RUN Pin Comparator Threshold\s+VRUN Rising\s+l\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "the RUN threshold")
    N["vrun"] = (f(m, 1), f(m, 2), f(m, 3))
    N["run_ihys"] = f(need(lt, r"RUN Pin Hysteresis Current\s+(\d+)\s+nA", "the RUN hysteresis current")) * 1e-9
    N["run_vhys"] = f(need(lt, r"RUN Pin Hysteresis Voltage\s+(\d+)\s+mV", "the RUN hysteresis voltage")) * 1e-3
    m = need(lt, r"TJMAX = (\d+)°C, θJA = (\d+)°C/W, θJC = (\d+)°C/W", "the FE package's thermal line")
    N["fe"] = (f(m, 1), f(m, 2), f(m, 3))
    need(lt, r"Industrial 12V 1MHz Regulator with Custom Input Undervoltage Lockout Thresholds", "TA04")
    need(lt, r"LTC3115EFE-1#PBF\s+LTC3115EFE-1#TRPBF\s+LTC3115FE-1\s+20-Lead Plastic TSSOP\s+\u201340°C to 125°C", "the E-grade FE part")
    N["rev"] = need(lt, r"(Rev\. E)", "the revision").group(1)
    tp = "\n".join(pdf_pages("tps55340", True))
    m = need(tp, r"VIN\s+Input voltage range\s+([\d.]+)\s+(\d+)\s+V", "the TPS55340's input range")
    N["t55_vin"] = (f(m, 1), f(m, 2))
    m = need(tp, r"ILIM\s+N-channel MOSFET current limit\s+D = Dmax\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+A", "the TPS55340's current limit")
    N["t55_ilim"] = (f(m, 1), f(m, 3))
    N["t55_rja"] = f(need(tp, r"RθJA\s+Junction-to-ambient thermal resistance\s+([\d.]+)\s+([\d.]+)", "the TPS55340's RthJA"))
    need(tp, r"A design example of SEPIC converter is provided in the next section\.", "the SEPIC section")
    t6 = "\n".join(pdf_pages("tps63070", True))
    m = need(t6, r"VIN\s+Input voltage range\s+once started; Vout ≥ 3\.0 V\s+([\d.]+)\s+(\d+)\s+V", "the TPS63070's input range")
    N["t63_vin"] = (f(m, 1), f(m, 2))
    m = need(t6, r"IIN,max\s+Average, positive input current limit\s+(\d+)\s+(\d+)\s+(\d+)\s+mA", "the TPS63070's input current limit")
    N["t63_iin"] = (f(m, 1) * 1e-3, f(m, 3) * 1e-3)
    cc = flat(text_pdf("xal60"))
    m = need(cc, r"XAL6060-103ME_ 10 ([\d.]+) ([\d.]+) (\d+) ([\d.]+) ([\d.]+) ([\d.]+)", "the XAL6060-103 row")
    N["l_dcr"], N["l_isat"], N["l_irms"] = f(m, 2) * 1e-3, f(m, 5), f(m, 6)
    # the fans' power and the rail's input at the floor, iterated with the feed's drop (the drop of 16e at the new current)
    N["p_fans"] = L7_FAN["n_mixer"] * L7_FAN["v"] * L7_FAN["i"]
    i_g = K["ret"][3][2]
    v = K["vsys_sup"]
    for _ in range(8):
        N["i_reg"] = N["p_fans"] / (F18_ETA * v) + F18_IQ_PWM
        N["i_decl"] = K["aux"]["U12"] + N["i_reg"]
        N["drop"] = N["i_decl"] * (L["ron"][2] + L["r813"] * F16_SPREAD) + i_g * L["r813"]
        v = K["vsys_sup"] - N["drop"]
    N["vsys_e_floor"] = v
    N["vsys_e_at_lim"] = K["vsys_sup"] - (L["ilim"][0] * (L["ron"][2] + L["r813"] * F16_SPREAD) + i_g * L["r813"])
    N["share_lim"] = N["i_decl"] / L["ilim"][0]
    N["room"] = L["ilim"][0] - N["i_decl"]
    N["i_plan"] = K["aux"]["U12"] + F18_PLAN_W / (F18_ETA * N["vsys_e_floor"]) + F18_IQ_PWM
    sp = importlib.util.spec_from_file_location("dock_contacts_pinned18", read("dock_py"))
    dc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(dc)
    N["c813_share"] = N["i_decl"] / dc.PD_MAX
    N["c813_rise"] = dc.rise_813(N["i_decl"])
    # the rail: the divider, the RUN thresholds, the loss and the junction
    r1, r2 = F18_RUN
    rp = r1 * r2 / (r1 + r2)
    N["run_on"] = tuple(vt * (1 + r1 / r2) for vt in N["vrun"])
    N["run_off"] = tuple((vt - N["run_vhys"] - N["run_ihys"] * rp) * (1 + r1 / r2) for vt in N["vrun"])
    N["vout"] = (N["vfb"][0] * (1 + F18_FB[0] * (1 - F18_FB_TOL) / (F18_FB[1] * (1 + F18_FB_TOL))), N["vfb"][1] * (1 + F18_FB[0] / F18_FB[1]),
                 N["vfb"][2] * (1 + F18_FB[0] * (1 + F18_FB_TOL) / (F18_FB[1] * (1 - F18_FB_TOL))))   # FB's limits with the 1 % divider
    N["loss_full"] = N["p_fans"] / F18_ETA - N["p_fans"]
    N["loss_plan"] = F18_PLAN_W / F18_ETA - F18_PLAN_W
    N["tj_full"] = K["air"]["route"] + N["loss_full"] * N["fe"][1]
    # the one-fan start against the regulator's capability and U42's room (the start current is NOT READ: Layer 7)
    N["start_room_w"] = N["room"] * N["vsys_e_at_lim"] * F18_ETA        # the power one fan may add at its start before U42 limits
    N["start_mult"] = (N["start_room_w"] + L7_FAN["v"] * L7_FAN["i"]) / (L7_FAN["v"] * L7_FAN["i"])
    # board B: the cooler headers' pin 1 net and the slot rail as drawn (NETLIST)
    gb = text("gen_b")
    need(gb, r'part\("J_FAN%d" % s, "Connector_Generic", "Conn_01x04", "IP68 cooler fan of S%d \(JST-SH 1\.0\): 5V GND TACHO PWM" % s, "SH4", \{"1": n5,', "board B's fan header on n5")
    need(gb, r'n5 = "\+5V_S%d" % s;', "n5 is the slot rail")
    m = need(gb, r'_intent\.rail\("\+5V_S%d" % _n, ([\d.]+), ', "the slot rail's voltage")
    N["b_slot_v"] = f(m)
    N["b_fan_a"] = f(need(gb, r'"J_FAN%d" % s: ([\d.]+),\s+# the slot\'s IP68 cooler fan', "the slot's fan row"))
    N["b_has_12v"] = bool(re.search(r'"\+12V[A-Z0-9_]*"', gb))         # a +12V net declared on board B
    return N


def render_fix18(R, p):
    K, L, N = R["K"], R["L"], R["N18"]
    p("18. THE FANS' FEED AFTER LAYER 7'S SELECTION (F-L7-01, F-L7-02, F-L7-04; the B1 topology kept)")
    p("   the facts (RECORD: Layer 7's %s at %s, sections 2d, 2e, 2f and 5): the mixers %s (two, board E) and the coolers %s (three, board B),"
      % (L7_FAN["rec"], L7_FAN["commit"], L7_FAN["mpn_mixer"], L7_FAN["mpn_cooler"]))
    p("     12 V, printed range %s to %s V, %s A each at 12 V, four wires (12 V, GND, pulse sensor, PWM), IP68, -20 to +70 C; no fan read prints a"
      % (fmt(L7_FAN["v_lo"], 1), fmt(L7_FAN["v_hi"], 1), fmt(L7_FAN["i"], 2)))
    p("     range covering VSYS_E's %s to %s V, so 15a's fans directly on VSYS_E is WITHDRAWN (MAKER through Layer 7)" % (fmt(N["vsys_e_at_lim"], 3), fmt(R["H"]["vsys_top"], 3)))
    p("   18a. THE MIXERS' 12.0 V RAIL ON BOARD E, THREE CANDIDATES (a buck cannot hold 12.0 V from the %s V floor; a boost cannot from %s V: a buck-boost)"
      % (fmt(K["vsys_sup"], 3), fmt(R["H"]["vsys_top"], 3)))
    p("     (V1) ADI LTC3115-1 (%s, held): monolithic four-switch buck-boost, input %s to %s V, inductor current limit %s / %s / %s A, internal soft start"
      % (N["rev"], fmt(N["vin"][0], 1), fmt(N["vin"][1], 0), fmt(N["ilim"][0], 1), fmt(N["ilim"][1], 1), fmt(N["ilim"][2], 1)))
    p("       %s ms, FB %s / %s / %s V, RUN comparator %s / %s / %s V rising with %s mV and %s nA of hysteresis; FE (TSSOP-20 EP) thetaJA %s C/W, TJ %s C (E grade"
      % (fmt(N["tss"] * 1e3, 0), fmt(N["vfb"][0], 3), fmt(N["vfb"][1], 3), fmt(N["vfb"][2], 3), fmt(N["vrun"][0], 2), fmt(N["vrun"][1], 2), fmt(N["vrun"][2], 2),
         fmt(N["run_vhys"] * 1e3, 0), fmt(N["run_ihys"] * 1e9, 0), fmt(N["fe"][1], 0), fmt(N["fe"][0], 0)))
    p("       -40 to 125 C); TA04 is a 12 V 1 MHz application (L 10 uH, CIN 10 uF, CO 22 uF, FB 1M / 90.9k, VC 40.2k and 820 pF, FF 10k and 33 pF, RT 35.7k);")
    p("       TA04b's efficiency at 0.34 A reads about 93 percent at 10.6 and 12 V in (typical, read); maximum load at 12 V out near 9.5 V in about 1.2 A (G12, 22 uH")
    p("       500 kHz, typical, read); price NOT READ (LCSC's search refused this host) (MAKER, read)")
    p("     (V2) TI TPS55340 (SLVSBD4E, held) as a SEPIC: input %s to %s V, switch limit %s to %s A, RthJA %s C/W; a coupled inductor and a coupling capacitor;"
      % (fmt(N["t55_vin"][0], 1), fmt(N["t55_vin"][1], 0), fmt(N["t55_ilim"][0], 2), fmt(N["t55_ilim"][1], 2), fmt(N["t55_rja"], 1)))
    p("       its efficiency is printed for a boost only: the SEPIC's is NOT PRINTED; a limit three times (V1)'s (MAKER)")
    p("     (V3) TI TPS63070 (SLVSC58B, held): input %s to %s V, under VSYS_E's %s V: FAILS the range (MAKER)" % (fmt(N["t63_vin"][0], 1), fmt(N["t63_vin"][1], 0), fmt(R["H"]["vsys_top"], 3)))
    p("     SELECTED (SESSION): (V1), U22 LTC3115EFE-1 on board E as TA04 with L4 Coilcraft XAL6060-103ME (10 uH, DCR %s mOhm, Isat %s A over the %s A limit,"
      % (fmt(N["l_dcr"] * 1e3, 2), fmt(N["l_isat"], 1), fmt(N["ilim"][2], 1)))
    p("       Irms %s A; Coilcraft 887-1, held), PWM/SYNC to VCC (fixed 1 MHz); the output %s V (%s to %s V at FB's limits with the 1 %% divider) inside the fans' %s to %s V (MAKER, INFERRED)"
      % (fmt(N["l_irms"], 1), fmt(N["vout"][1], 3), fmt(N["vout"][0], 3), fmt(N["vout"][2], 3), fmt(L7_FAN["v_lo"], 1), fmt(L7_FAN["v_hi"], 1)))
    p("     its RUN divider R103 %s M / R104 %s k: enabled at %s V (%s to %s), disabled at %s V (%s to %s): under the floor and over U12's %s V start, so a"
      % (fmt(F18_RUN[0] / 1e6, 1), fmt(F18_RUN[1] / 1e3, 0), fmt(N["run_on"][1], 2), fmt(N["run_on"][0], 2), fmt(N["run_on"][2], 2),
         fmt(N["run_off"][1], 2), fmt(N["run_off"][0], 2), fmt(N["run_off"][2], 2), fmt(K["ap_vin"][0], 1)))
    p("       fan fault that drives U22 to its %s A limit against U42's limit lets VSYS_E fall only to U22's disable, where U22 stops and VSYS_E recovers:"
      % fmt(N["ilim"][0], 1))
    p("       the controller stays up and the fault appears as a rail hiccup, not a controller reset (INFERRED; the model of TA04's own 10.6 / 8.7 V within 0.15 V)")
    p("     heat into the case: %s W at full speed (%s W of fans at %s), %s W at the plan's %s W; TJ %s C at +%s C air on thetaJA %s (MODELED, ASSUMPTION eta)"
      % (fmt(N["loss_full"], 3), fmt(N["p_fans"], 2), fmt(F18_ETA, 2), fmt(N["loss_plan"], 3), fmt(F18_PLAN_W, 2), fmt(N["tj_full"], 1), fmt(K["air"]["route"], 0), fmt(N["fe"][1], 0)))
    p("     its protection: U22's own current limit and soft start, behind U42 (the branch's limiter); no fuse of its own (SESSION)")
    p("   18b. THE BRANCH'S DECLARED CURRENT AND U42'S SETTING, RE-DERIVED")
    p("     at the floor, both fans at full speed: U22's input %s A (%s W over %s at %s V, plus %s mA quiescent), with U12's %s A: %s A DECLARED on IF-AE-DOCK"
      % (fmt(N["i_reg"], 4), fmt(N["p_fans"], 2), fmt(F18_ETA, 2), fmt(N["vsys_e_floor"], 3), fmt(F18_IQ_PWM * 1e3, 0), fmt(K["aux"]["U12"], 1), fmt(N["i_decl"], 4)))
    p("       pin 1 (was 1.0 A; Layer 7's 1.277 A at eta 0.90); at the plan's duty %s A (MODELED, ASSUMPTION)" % fmt(N["i_plan"], 4))
    p("     against U42's least limit %s A: %s %%, %s A in hand: NOT EXCEEDED, so R228 stays %s kOhm (I(OL) %s to %s A); the contact at %s %% of 3.5 A, %s K"
      % (fmt(L["ilim"][0], 4), fmt(100 * N["share_lim"], 1), fmt(N["room"], 4), fmt(F16_RILIM_K, 1), fmt(L["ilim"][0], 4), fmt(L["ilim"][1], 4), fmt(100 * N["c813_share"], 1), fmt(N["c813_rise"], 2)))
    p("       by w3de's rise; the sustained-overload figures of 16e and the retry duty of 17a are unchanged (INFERRED, ASSUMPTION w3de)")
    p("     the drop at the floor with %s A: %s V, VSYS_E %s V; at U42's least limit %s V; U22 holds 12.0 V from %s V up, so VSYS_E's floor no longer"
      % (fmt(N["i_decl"], 4), fmt(N["drop"], 4), fmt(N["vsys_e_floor"], 3), fmt(N["vsys_e_at_lim"], 3), fmt(N["vin"][0], 1)))
    p("       reaches the fans (INFERRED)")
    p("     the fans' start (NOT READ, Layer 7): with one fan running and U12 on, U42's room %s A leaves %s W at the rail for the other fan's start, %s times its"
      % (fmt(N["room"], 4), fmt(N["start_room_w"], 2), fmt(N["start_mult"], 2)))
    p("       running power, before U42 limits; U22 delivers about 1.2 A at the floor (G12): the fan, not the rail, is the unknown (E11-35, E11-38 f) (INFERRED)")
    p("   18c. THE STAGGER (E11-39) RESTATED: U22's %s ms soft start covers the rail's own rise only; a fan's start surge comes when its PWM duty rises, so the"
      % fmt(N["tss"] * 1e3, 0))
    p("     stagger stays: one fan at a time, each by a PWM-duty ramp into the fan's PWM input (Layer 7's F-L7-05), never while U12 starts (SESSION)")
    p("   18d. BOARD B'S COOLER FANS (NETLIST): J_FAN1 to J_FAN3's pin 1 is the slot rail +5V_Sn at %s V, the fan declared %s A on it; no 12 V net exists on"
      % (fmt(N["b_slot_v"], 1), fmt(N["b_fan_a"], 1)))
    p("     board B (%s): the feed does NOT cover the coolers' %s to %s V and needs the same regulated 12.0 V: a FINDING for board B's owner (E11-40), not a"
      % ("no +12V net is declared" if not N["b_has_12v"] else "a +12V net IS declared: re-read", fmt(L7_FAN["v_lo"], 1), fmt(L7_FAN["v_hi"], 1)))
    p("     draft of this record: a per-slot step-up from +5V_Sn (Layer 7's 0.436 A each at full speed) or a 12 V feed from board A over the bay harness (RECORD)")
    p("")

# ============================================================================================ round 9 (4 October 2026)
# Record l9stk's protection section (15 at 0d72880b: checked CONFIRMED AS CONDITIONAL at 2c8b29fb; 15.4b, the -1 and C-1c added since) and record l8p's breaker drafts (at
# b1295c1e) are read from their commits by sha256, never retyped: the junction limit, the start, the hold, IF-1, DD-3 and C3 from l9stk's
# output and page; the findings L8P-F02 and L8P-F03 from l8p's page.
R9_COMMITS = {"l9stk": "0d72880b34e337a6f2e26c1420507b813784b533", "l8p": "b1295c1e4fcfe03ea4d021067b6b9433e8133006"}
R9_GIT = {
    "l9stk_out": ("l9stk", "v2/docs/records/l9stk/l9stk_protection.out", "d97f94a0fa1f25598a26458276334b53505b065f350eb75a4d01cdfd91716eac"),
    "l9stk_page": ("l9stk", "v2/docs/records/l9stk/L9-STACKUPS.md", "2e053ee48a4558a4e33d70f77b36ebdef0e9878600ae9ea30735597cf639ee5c"),
    "l8p_page": ("l8p", "v2/docs/records/l8p/L8P-BREAKER.md", "ad2eacf9f18aac324899fd56f8221f4e58388afcc933c23816f60caa86efebd6"),
}
R9_BAND_RISE = 10.0        # K, ASSUMPTION: board E's input bands are sized to a 10 K rise at 20 A (E11-14), taken as R19's local ambient over the air
R9_C105 = 100e-9           # F, SESSION: U46's CTR2 capacitor (C14663, the part U34's C212 is)
R9_C_TOL = (0.10, 0.15)    # ASSUMPTION: C105's tolerance and X7R's swing over temperature, U34's C212 basis (its 79 to 201 ms)
R9_SUP = (91e3, 10e3)      # ohm, SESSION: U46's SENSE2 divider R86 over R87 (U34's R14 / R15 pair), 1 %
R9_EF = (100e3, 22e3)      # ohm, SESSION: U42's UVLO divider R88 over R89, 1 %
R9_RTOL = 0.01
R9_RAIL_EN = (100e3, 39e3)  # ohm, NETLIST: R2 over R184 on RAIL_EN (gen_sch_a.py)
R9_VOL = 0.3               # V, MAKER (SNVSBJ1E 7.5): the TPS37A's RESET VOL at most, at 5 mA


def git_at(key):
    who, rel, want = R9_GIT[key]
    c = R9_COMMITS[who]
    r = subprocess.run(["git", "-C", TOP, "show", "%s:%s" % (c, rel)], capture_output=True)
    if r.returncode != 0:
        refuse(2, "record %s's commit %s is not in this repository" % (who, c[:8]))
    if hashlib.sha256(r.stdout).hexdigest() != want:
        refuse(2, "%s at %s is not the pinned file" % (rel, c[:8]))
    return r.stdout.decode("utf-8")


def fix19_round(R, T):
    """Round 9 (record l9stk 15 and record l8p): L8P-F02 and L8P-F03 corrected in the drafts; the third battery FET Q42 on l9stk's
    junction limit, E11-29 restated and E11-37 rebound to three; DD-3 on the shore input judged by the owner's current-and-time criterion
    (one design-out attempt); IF-1, every board A load on VSYS held through the pack breaker's start by a VBAT supervisor."""
    N, L, H, D = R["N"], R["L"], R["H"], R["D"]
    S = {}
    o9 = git_at("l9stk_out")
    p9 = flat(git_at("l9stk_page"))
    p8 = flat(git_at("l8p_page"))
    ga = text("gen_a")
    # ---- the two findings
    need(p8, r"L8P-F02 \| A \| L4-E11 \(`apply_gen_sch_a_charger\.py`\) \| VSYS_DOCK names U42 as its source without `source_ic`", "L8P-F02")
    need(p8, r"L8P-F03 \| E \| L4-E11 \(`apply_gen_sch_e_aux\.py`\) \| \+12V_FAN names L4 as its source, and L4 is not on that net", "L8P-F03")
    need(p8, r"Q41 is\s+record l8r2's VIN_RAW cut-off FET", "Q41's owner")
    # ---- the junction limit (l9stk 15.5, prot 4) and the three FETs
    m = need(o9, r"held at ([\d.]+) A from ([\d.]+) C, the band carrying the current \(([\d.]+) K", "the junction limit")
    S["i"], S["t0"], S["band"] = f(m, 1), f(m, 2), f(m, 3)
    m = need(o9, r"and R17 dissipating ([\d.]+) W in place; the budget for the FETs and R17's coupling is ([\d.]+) K", "R17 and the budget")
    S["pr17_rec"], S["budget_rec"] = f(m, 1), f(m, 2)
    rec = {}
    for n_, pat in ((2, r"the pair \(Zself \+ Zmut\)\s+([\d.]+) W each: FETs only ([\d.]+) K/W; R17 apart ([\d.]+) K/W; R17 anywhere ([\d.]+) K/W"),
                    (3, r"three \(Zself \+ 2 Zmut\)\s+([\d.]+) W each: FETs only ([\d.]+) K/W; R17 apart ([\d.]+) K/W; R17 anywhere ([\d.]+) K/W")):
        m = need(o9, pat, "the %d FETs' allowance" % n_)
        rec[n_] = tuple(f(m, k) for k in range(1, 5))
    S["rec"] = rec
    S["r17_allow"] = f(need(p9, r"Designed apart \(off the FETs' pour\), it is held to ([\d.]+) K/W", "R17's coupling"))
    r17 = f(need(ga, r'r\("R17", "(\d+)mOhm 1% 2512 \(RSR', "R17")) * 1e-3
    S["pr17"] = S["i"] ** 2 * r17
    S["budget"] = 150.0 - S["t0"] - S["band"]
    for n_ in (2, 3):
        pe = (S["i"] / n_) ** 2 * F16_RA
        S[n_] = dict(p=pe, fet_only=S["budget"] / pe, apart=(S["budget"] - S["r17_allow"] * S["pr17"]) / pe, anywhere=S["budget"] / (pe + S["pr17"]))
        got = (S[n_]["p"], S[n_]["fet_only"], S[n_]["apart"], S[n_]["anywhere"])
        if any(abs(x - y) > max(0.0015 if k == 0 else 0.011, 0.001 * y) for k, (x, y) in enumerate(zip(got, rec[n_]))):   # the printed inputs are rounded
            refuse(4, "the %d FETs' allowance does not reproduce record l9stk's (%s against %s)" % (n_, got, rec[n_]))
    if abs(S["pr17"] - S["pr17_rec"]) > 0.006 or abs(S["budget"] - S["budget_rec"]) > 0.006:
        refuse(4, "R17's loss or the budget does not reproduce record l9stk's")
    m = need(o9, r"at the allowances: ([\d.]+) C at 10 A, ([\d.]+) C at the 18 A service, ([\d.]+) C at ([\d.]+) A", "the service at the allowances")
    S["tj_rec"] = (f(m, 1), f(m, 2), f(m, 3))
    S["zsum_pair_old"] = L["plan"]["zsum"]                      # the pair's former E11-29 target (+70 C air, FETs only)
    S["ratio3"], S["ratio2"] = S[3]["apart"] / S["zsum_pair_old"], S[2]["apart"] / S["zsum_pair_old"]
    S["jmb"] = f(need(o9, r"a junction leads its copper by ([\d.]+) K at", "the junction's lead on its copper"))
    # ---- E11-37 with three (Ciss against TI's 5 nF; BATDRV's drive)
    S["ciss3"] = (3 * L["ciss_t"], 3 * L["ciss_0"])
    m = need(o9, r"C3 the third battery FET's Ciss, ([\d.]+) nF typical \(about ([\d.]+) near 0 V\)", "C3")
    if abs(round(S["ciss3"][0] * 1e9, 2) - f(m, 1)) > 0.005 or abs(round(S["ciss3"][1] * 1e9, 2) - f(m, 2)) > 0.005:
        refuse(4, "the three FETs' Ciss does not reproduce record l9stk's C3")
    S["ciss_ratio"] = (S["ciss3"][0] / H["bf_ciss"], S["ciss3"][1] / H["bf_ciss"])
    S["tau3_on"] = (H["rdrv"][1] * S["ciss3"][0], H["rdrv"][1] * S["ciss3"][1])
    S["tau3_off"] = L["roff"][1] * S["ciss3"][1]
    # ---- IF-1: the breaker's start (l9stk prot 3 and 3a)
    m = need(o9, r"dv/dt start: (\d+) nF \(\+-(\d+) %\) into (\d+) uF \(VSYS's (\d+) uF, CELL_FUSED's (\d+) uF\), gate (\d+) to (\d+) uA: inrush ([\d.]+) A at most, ([\d.]+) ms at most", "the start")
    cdv, tol = f(m, 1) * 1e-9, f(m, 2) / 100.0
    S["start"] = dict(cdv=cdv, tol=tol, cout=f(m, 3) * 1e-6, c_vsys=f(m, 4) * 1e-6, ig=(f(m, 6) * 1e-6, f(m, 7) * 1e-6), inrush=f(m, 8), tmax=f(m, 9) * 1e-3)
    S["dvdt"] = (S["start"]["ig"][0] / (cdv * (1 + tol)), S["start"]["ig"][1] / (cdv * (1 - tol)))      # V/s, the slowest and the fastest
    S["vmax"] = S["start"]["tmax"] * S["dvdt"][0]
    if abs(S["vmax"] - 16.8) > 0.05:
        refuse(4, "the start's 40.7 ms does not read as the 16.8 V ramp at the slowest slope")
    S["plim"] = (f(need(o9, r"its spread: ([\d.]+) to ([\d.]+) W with the table's", "the power limit's spread")), )   # its least
    m = need(o9, r"the start: ([\d.]+) W for ([\d.]+) ms against ([\d.]+) W derated", "the start's SOA")
    S["start_w"], S["dc_line"] = f(m, 1), f(m, 3)
    m = need(o9, r"hold makes ([\d.]+) to ([\d.]+) s after the enable mates", "the RC hold")
    S["grace"] = (f(m, 1), f(m, 2))
    m = need(p9, r"the pack ([\d.]+) to ([\d.]+) V; OVLO to ground", "the pack's range")
    S["pack_lo"], S["vpk"] = f(m, 1), f(m, 2)
    need(o9, r"IF-1 CRITICAL TO THE SERVICE under the -1", "IF-1")
    S["if1_room"] = f(need(o9, r"leaves room for at most ([\d.]+) A of load at full VDS", "IF-1's room"))
    # what IF-1 names, read on the drafts as they stood: U42 on from its IN's operating floor, at its overload limit's maximum
    vin_min = f(find("tps1663", r"IN, P_IN\s+([\d.]+)\s+60", "IN's operating floor", layout=True)[1])
    S["u42_vin"] = vin_min
    S["u42_vds"] = S["vpk"] - vin_min
    S["u42_w"] = S["u42_vds"] * (S["start"]["inrush"] + L["ilim"][1])
    # ---- the hold: U46, the TPS37A010122 (SNVSBJ1E), on VBAT
    m = find("tps37", r"\(Undervoltage\)\s+VIT = 800 mV \(3\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "VITN at 800 mV", layout=True)[1]
    vit = (f(m, 1), f(m, 2), f(m, 3))
    hys = f(need(flat(ga.replace("#", " ")), r"both channels at VIT [\d.]+ V \([\d.]+ to [\d.]+\) with (\d+) percent hysteresis", "the TPS37A's hysteresis")) / 100.0
    m = find("tps37", r"RCTR\s+(\d+)\s+(\d+)\s+(\d+)\s+Kohms", "RCTR", layout=True)[1]
    rctr = (f(m, 1) * 1e3, f(m, 2) * 1e3, f(m, 3) * 1e3)
    k_lo = f(find("tps37", r"tCTRx \(min\) = -ln \(([\d.]+)\) x RCTRx \(min\)", "Equation 2")[1])
    k_ty = f(find("tps37", r"tCTRx \(typ\) = -ln \(([\d.]+)\) x RCTRx \(typ\)", "Equation 1")[1])
    k_hi = f(find("tps37", r"tCTRx \(max\) = -ln \(([\d.]+)\) x RCTRx \(max\)", "Equation 3")[1])
    m = find("tps37", r"VIT = 800 mV\s+CCTS1 = CCTS2 = Open\s+(\d+)\s+(\d+)\s+µs", "tCTS at 800 mV", layout=True)[1]
    S["tcts"] = (f(m, 1) * 1e-6, f(m, 2) * 1e-6)
    S["tctr_open"] = f(find("tps37", r"VIT = 800 mV\s+CCTR1 = CCTR2 = Open\s+(\d+)\s+µs", "tCTR open at 800 mV", layout=True)[1]) * 1e-6
    S["tsd"] = f(find("tps37", r"tSD\s+Startup Delay \(4\)\s+(\d+)\s+ms", "tSD", layout=True)[1]) * 1e-3
    m = find("tps37", r"VDD\s+Supply Voltage\s+([\d.]+)\s+(\d+)\s+V", "VDD", layout=True)[1]
    S["vdd"] = (f(m, 1), f(m, 2))
    a_, b_ = R9_SUP
    S["fall"] = (vit[0] * (1 + a_ * (1 - R9_RTOL) / (b_ * (1 + R9_RTOL))), vit[1] * (1 + a_ / b_), vit[2] * (1 + a_ * (1 + R9_RTOL) / (b_ * (1 - R9_RTOL))))
    S["rise"] = tuple(x * (1 + hys) for x in S["fall"])
    c_lo, c_hi = R9_C105 * (1 - R9_C_TOL[0]) * (1 - R9_C_TOL[1]), R9_C105 * (1 + R9_C_TOL[0]) * (1 + R9_C_TOL[1])
    S["hold"] = (-math.log(k_lo) * rctr[0] * c_lo, -math.log(k_ty) * rctr[1] * R9_C105, -math.log(k_hi) * rctr[2] * c_hi + S["tctr_open"])
    S["hold_margin"] = S["hold"][0] - S["start"]["tmax"]
    S["vbat_clamp"] = f(need(ga, r"an SMCJ18A that clamps at ([\d.]+) V", "VBAT's clamp"))
    S["sense_clamp"] = S["vbat_clamp"] * b_ * (1 + R9_RTOL) / (a_ * (1 - R9_RTOL) + b_ * (1 + R9_RTOL))
    # U42's own UVLO through R88 / R89, and EF_UVLO's levels
    m = find("tps1663", r"V\(UVLOR\)\s+UVLO threshold voltage, rising\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "UVLO rising", layout=True)[1]
    S["uvlor"] = (f(m, 1), f(m, 2), f(m, 3))
    m = find("tps1663", r"V\(UVLOF\)\s+UVLO threshold voltage, falling\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "UVLO falling", layout=True)[1]
    S["uvlof"] = (f(m, 1), f(m, 2), f(m, 3))
    m = find("tps1663", r"UVLO_toff\(dly\)\s+UVLO switch turnoff delay\s+UVLO↓\(20mV below V\(UVLOF\)\) to FLT↓\s+(\d+)\s+(\d+)\s+(\d+)\s+µs", "UVLO's turn-off", layout=True)[1]
    S["uvlo_toff"] = f(m, 3) * 1e-6
    t_, b2 = R9_EF
    S["ef_k"] = (b2 * (1 - R9_RTOL) / (t_ * (1 + R9_RTOL) + b2 * (1 - R9_RTOL)), b2 / (t_ + b2), b2 * (1 + R9_RTOL) / (t_ * (1 - R9_RTOL) + b2 * (1 + R9_RTOL)))
    S["own_on_max"] = S["uvlor"][2] / S["ef_k"][0]
    S["own_off_min"] = S["uvlof"][0] / S["ef_k"][2]
    S["ef_release"] = S["rise"][0] * S["ef_k"][0]
    S["ef_clamp"] = S["vbat_clamp"] * S["ef_k"][2]
    S["ef_sink"] = S["vbat_clamp"] / (t_ * (1 - R9_RTOL))
    S["ov_fall_min"] = vit[0] * (1 - hys)
    # Q43, D24 and RAIL_EN
    m = find("n2n7002", r"Gate-Threshold Voltage\s+Vth\(GS\)\s+VDS=VGS, ID=250 µA\s+(\d+)\s+([\d.]+)\s+([\d.]+)", "the 2N7002's threshold", layout=True)[1]
    S["vth"] = (f(m, 1), f(m, 2), f(m, 3))
    S["vgs_max"] = f(find("n2n7002", r"Gate-Source Voltage\s+VGS\s+±(\d+)\s+V", "the 2N7002's VGS", layout=True)[1])
    m = find("bzt52c", r"BZT52C12\s+WH\s+12\s+([\d.]+)\s+([\d.]+)", "the BZT52C12's band", layout=True)[1]
    S["vz"] = (f(m, 1), f(m, 2))
    m = find("tps62933", r"VEN_FALL\s+Disable threshold\s+Falling disable threshold\s+([\d.]+)\s+([\d.]+)\s+V", "VEN_FALL", layout=True)[1]
    S["ven_fall"] = f(m, 1)
    need(ga, r'r\("R2", "100k", "RAIL_EN", "VBAT"\); r\("R184", "39k 1%", "RAIL_EN", "GND"', "RAIL_EN's divider")
    S["rail_k"] = R9_RAIL_EN[1] / (R9_RAIL_EN[0] + R9_RAIL_EN[1])
    S["rail_vbat_on"] = S["ven_fall"] / S["rail_k"]                 # the lowest VBAT at which RAIL_EN can reach the buck's least disable threshold
    S["rail_held_vdd"] = S["vdd"][0] * S["rail_k"]                  # RAIL_EN with U46 under its 2.7 V UVLO (both outputs asserted, Q43 off)
    S["q43_overdrive"] = S["rail_vbat_on"] - S["vth"][2]
    # LTC2954 (U1): the power-up hold, the PB debounce and the KILL window
    m = find("ltc2954", r"tDB, ON\s+Internal Turn-On Debounce Time\s+ONT Pin Float, PB Falling → Enable Asserted\s+l\s+(\d+)\s+(\d+)\s+(\d+)\s+ms", "tDB,ON", layout=True)[1]
    S["tdb"] = (f(m, 1) * 1e-3, f(m, 3) * 1e-3)
    m = find("ltc2954", r"KILL Turn-On Blanking \(Note 3\)\s+KILL = Low, Enable Asserted → Enable Released\s+l\s+(\d+)\s+(\d+)\s+(\d+)\s+ms", "the KILL blanking", layout=True)[1]
    S["kill"] = (f(m, 1) * 1e-3, f(m, 3) * 1e-3)
    m = find("ltc2954", r"VUVL\s+VIN Undervoltage Lockout\s+VIN Falling\s+l\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "VUVL", layout=True)[1]
    m2 = find("ltc2954", r"VUVL\(HYST\)\s+VIN Undervoltage Lockout\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "VUVL's hysteresis", layout=True)[1]
    S["u1_on_min"] = f(m, 1) + f(m2, 1) * 1e-3
    find("ltc2954", r"When power is first applied to the LTC2954, the part initializes the output pins\. Any DC/DC converters connected to the EN/EN pin will therefore be held off\.", "the power-up hold")
    # MAIN held through a docking: without the hold (the drawn RAIL_EN) and with it (the KILL window)
    s_lo = S["dvdt"][0]
    S["en_early"] = S["u1_on_min"] / s_lo + S["tdb"][0]
    S["en_vds"] = S["vpk"] - s_lo * S["en_early"]
    loss = []
    for s_ in S["dvdt"]:
        rel = S["rise"][2] / s_ + S["hold"][2] + S["tsd"]
        en = S["u1_on_min"] / s_ + S["tdb"][0]
        loss.append(rel - en)
    S["kill_left"] = S["kill"][0] - max(loss)
    # a quick redocking with VBAT held up: the least aux load that takes VBAT under U46's highest fall before the breaker can start, and
    # the most the breaker FET carries if a smaller load leaves U42 on and then steps to U42's limit during the start
    S["redock_i"] = S["start"]["c_vsys"] * (S["vpk"] - S["fall"][2]) / S["grace"][0]
    S["redock_w"] = (S["vpk"] - S["fall"][0]) * (S["start"]["inrush"] + L["ilim"][1])
    # a source present: the excess over the charger's input limit that the breaker may carry before its power limit acts
    S["src_vds"] = S["vpk"] - H["floor"]
    S["src_excess"] = S["plim"][0] / S["src_vds"] - S["start"]["inrush"]
    # ---- IF-1's guarantee, explicit: what board A still draws from VBAT while U46 holds (RAIL_EN low, +3V3 down, every enable on its
    # pull-down: NETLIST), at the pack's 16.8 V top, each part at its sheet's largest printed figure (a typical where only that is printed)
    vb = S["vpk"]
    q = lambda key, pat, what, k=2: f(find(key, pat, what, layout=True)[1], k)
    st = [("U3 BQ25730, battery only, performance mode (SLUSE65A, the largest row)", q("bq25730", r"= 00b, REGN on, Enable PSYS, In performance\s+(\d+)\s+(\d+)\s+µA", "U3's quiescent") * 1e-6, "MAKER"),
          ("U42 TPS16630, held by UVLO (IQ(ON) taken as the bound: no row with UVLO low)", q("tps1663", r"Enabled: V\(SHDN\) = 2V\s+([\d.]+)\s+([\d.]+)\s+mA", "U42's IQ(ON)") * 1e-3, "MAKER"),
          ("U1 LTC2954", q("ltc2954", r"IIN\s+VIN Supply Current\s+System Power-On, VIN = 2.7V to 24V\s+l\s+(\d+)\s+(\d+)\s+\S+A", "U1's IIN") * 1e-6, "MAKER"),
          ("U46 TPS37A", q("tps37", r"VIT = 800 mV\s+([\d.]+)\s+([\d.]+)\s+µA", "U46's IDD") * 1e-6, "MAKER"),
          ("U5, U7, U13, U15, U19 LM5176 in shutdown, five", 5 * q("lm5176", r"VIN shutdown current\s+VEN/UVLO = 0 V\s+([\d.]+)\s+(\d+)\s+µA", "the LM5176's shutdown") * 1e-6, "MAKER"),
          ("U4, U6 AP64500 in shutdown, two", 2 * q("ap64500", r"Shutdown Supply Current\s+VEN = 0V\s+\u2014\s+(\d+)\s+(\d+)\s+\S+A", "the AP64500's shutdown") * 1e-6, "MAKER"),
          ("U12, U41 TPS62933 in shutdown, two (typical only)", 2 * q("tps62933", r"ISHDN\s+Shutdown supply current\s+VEN = 0 V\s+([\d.]+)\s+µA", "the TPS62933's shutdown", 1) * 1e-6, "MAKER, typical"),
          ("U21, U22 TPS259631 in shutdown, two", 2 * q("tps2596", r"VIN ≥ 4 V, VEN/UVLO < VSD\s+([\d.]+)\s+([\d.]+)\s+µA", "the TPS25963's shutdown") * 1e-6, "MAKER"),
          ("R2 (RAIL_EN held low by Q43)", vb / R9_RAIL_EN[0], "NETLIST"),
          ("R86 and R87 (U46's SENSE2)", vb / (R9_SUP[0] + R9_SUP[1]), "SESSION"),
          ("R88 (EF_UVLO held low by RESET2)", vb / R9_EF[0], "SESSION"),
          ("R105 into D24's clamp", (vb - S["vz"][0]) / 100e3, "SESSION"),
          ("R82 and R83 (the charge inhibit, when it holds)", vb / 300e3, "SESSION"),
          ("R92 and R96 (U21's and U22's OVLO dividers, their 143k tops as the bound)", 2 * vb / 143e3, "NETLIST"),
          ("R107 and R108 on CELL+", vb / 200e3, "SESSION")]
    S["static"] = st
    S["static_sum"] = sum(x for _l, x, _c in st)
    S["static_frac"] = S["static_sum"] / S["if1_room"]
    S["redock_room"] = S["plim"][0] / (S["vpk"] - S["fall"][0]) - S["start"]["inrush"]
    # ---- DD-7 (l9stk 15.4b, read at 0d72880b): the latch-off -1, the input-return reset, the charger's hold (IF-7) and E-14
    need(o9, r"SELECTED: the -1 \(latch-off\)", "the -1 selected")
    S["timer_reenable"] = f(need(o9, r"the timer falls under 0\.3 V in ([\d.]+) ms at most", "the timer's re-enable")) * 1e-3
    S["inv2_on"] = f(need(o9, r"the second on in ([\d.]+) us and UVLO falls at once", "the second inverter")) * 1e-6
    S["uvlo_fall"] = f(need(o9, r"C_U drains in ([\d.]+) ms behind it", "C_U's drain when the loop opens")) * 1e-3
    need(o9, r"read at the falling edge, a pulse within\s+([\d.]+) ms of a latch does not restart, which fails safe", "the UVLO edge")
    need(o9, r"C-1c SELECTED: a restart inhibit on the breaker pad", "C-1c")
    S["dd7_restart"] = f(need(o9, r"restarts within ([\d.]+) s \(the hold and the start\)", "DD-7's restart"))
    need(o9, r"IF-7 the bridge reports a tripped breaker", "IF-7")
    need(o9, r"E-14 the charge through a latched breaker", "E-14")
    m = need(o9, r"precharge in one diode ([\d.]+) W \(VSD ([\d.]+) V at most\), TJ ([\d.]+) C", "the charge direction")
    S["vsd"] = f(m, 2)
    S["rja_brk"] = f(need(o9, r"IF-2 each breaker FET's installed RthJA at most ([\d.]+) C/W", "IF-2"))
    need(ga, r'c\("C212", "100n", "FE_CTR2", "GND", lcsc="C14663"\)', "U34's CTR2 capacitor")
    S["pulse"] = S["hold"]                       # U34's CTR2: C212 is C105's part and value on the same TPS37A010122, so its release is S["hold"]
    S["pulse_margin"] = S["pulse"][0] / S["uvlo_fall"]
    S["pulse_vs_timer"] = S["pulse"][0] + S["grace"][0] - S["timer_reenable"]
    S["dd7_total"] = S["pulse"][2] + S["grace"][1] + S["start"]["tmax"]
    S["guard_rise"] = R["N"]["guard_new"][1]     # U34's UV rising threshold on VIN_RAW with this record's R14 (3f)
    k_lo = (1 - R9_RTOL) / ((1 + R9_RTOL) + (1 - R9_RTOL))
    k_hi = (1 + R9_RTOL) / ((1 - R9_RTOL) + (1 + R9_RTOL))
    S["alive_on"] = S["vth"][2] / k_lo                # CELL+ over which Q46 is on at its threshold's maximum
    S["alive_off"] = S["vth"][0] / k_hi               # CELL+ under which Q46 cannot conduct: the pulse forms
    S["alive_clamp"] = S["vbat_clamp"] * k_hi
    # the hardware charge inhibit (the checker's B-R2): the loop's state and the terminal's, read on record l8p's values (its page)
    m = need(p8, r"\| R106 \| (\d+) kOhm \(BRK_VIN to the loop\) \|", "l8p's R106")
    S["r_feed"] = f(m) * 1e3
    S["r_ret"] = f(need(p8, r"\| R107 \| (\d+) kOhm \(the loop's return to the return\) \|", "l8p's R107")) * 1e3
    m = need(p9, r"The kit's PRF15BB103 chip PTC: (\d+) kOhm plus or minus (\d+) %, (\d+) kOhm at 130 C", "the PTC")
    S["rt1"] = (f(m, 1) * 1e3 * (1 - f(m, 2) / 100.0), f(m, 1) * 1e3, f(m, 3) * 1e3)
    S["loop_out_lo"] = S["pack_lo"] * (S["rt1"][0] + S["r_ret"]) / (S["r_feed"] + S["rt1"][0] + S["r_ret"])
    k_sns = 1e6 * (1 - R9_RTOL) / (1e6 * (1 + R9_RTOL) + 1e6 * (1 - R9_RTOL))
    S["inh_g_lo"] = S["loop_out_lo"] * k_sns
    gl = lambda load: 1.0 / S["r_feed"] / (1.0 / S["r_feed"] + 1.0 / (S["rt1"][2] + S["r_ret"]) + load)
    S["ret_bound"] = (S["pack_lo"] * gl(0.0) * S["r_ret"] / (S["rt1"][2] + S["r_ret"]), S["pack_lo"] * gl(1.0 / 2e6) * S["r_ret"] / (S["rt1"][2] + S["r_ret"]))
    S["q49_vgs"] = (H["floor"] * (1 + R9_RTOL) * 100e3 / ((1 + R9_RTOL) * 100e3 + (1 - R9_RTOL) * 200e3), S["vbat_clamp"] * (1 - R9_RTOL) * 100e3 / ((1 - R9_RTOL) * 100e3 + (1 + R9_RTOL) * 200e3))
    S["q49_vgs"] = (S["q49_vgs"][0], S["vbat_clamp"] * (1 + R9_RTOL) * 100e3 / ((1 + R9_RTOL) * 100e3 + (1 - R9_RTOL) * 200e3))
    m = find("bq25730", r"VBATDRV_ON\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "VBATDRV_ON", layout=True)[1]
    S["batdrv_on"] = f(m, 3)
    m = find("bq25730", r"RBATDRV_ON\s+sourcing 10 µA\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+kΩ", "RBATDRV_ON", layout=True)[1]
    S["rbatdrv_on_min"] = f(m, 1) * 1e3
    S["batdrv_sink"] = S["batdrv_on"] / S["rbatdrv_on_min"]
    S["idss"] = f(need(flat(text_pdf("buk6y10")), r"IDSS drain leakage current VDS = -30 V; VGS = 0 V; Tj = 25 °C - - -(\d+) µA", "the BUK6Y10-30P's IDSS")) * 1e-6
    # the inhibit's reach (B-R2): it sets only when CELL+ falls under Q48's release; with a source present at a latch, the battery FETs
    # tie CELL+ to VSYS, which the charger holds up into a resistive fault; and the breaker's PGD reads high with reverse current (its VDS
    # negative), so no board A signal and no PGD tells a latched -1 passing charge from an -1 that is on
    m = need(ga, r"its (\d+\.\d) A ISNS maximum at (\d+\.\d) V", "the front end's ISNS maximum")
    S["p_src"] = f(m, 1) * f(m, 2)
    S["r_fault"] = f(need(o9, r"at ([\d.]+) ohm \(just over the least limit at full voltage\)", "the worst resistive fault"))
    S["v_fault"] = math.sqrt(S["p_src"] * S["r_fault"])
    S["r_assert"] = S["alive_off"] ** 2 / S["p_src"]
    lm = flat("".join(pdf_pages("lm5069")))
    need(lm, r"When the voltage at OUT increases to within 1\.25 V of the SENSE pin \(VDS <1\.25 V\), PGD switches high", "PGD's rule")
    S["capwin"] = (N["rb_max"], (150.0 - S["t0"]) / (S["vsd"] * S["rja_brk"]))
    G = R["G"]
    S["e14"] = [(lab, i_, i_ * S["vsd"], S["t0"] + i_ * S["vsd"] * S["rja_brk"])
                for lab, i_ in (("the charger's ChargeCurrent at POR (TI's E2E answer, D4)", G["por_ma"] * 1e-3),
                                ("R-b's largest actual current, 0x0200 inside TI's row condition", N["rb_max"]))]
    # ---- DD-3 (l9stk 14.6 and 15.7): the shore input under the owner's criterion
    m = need(p9, r"\*\*J_DCIN OVER \(20 of 10 A\); R19 OVER \(([\d.]+) W of (\d+) W from ([\d.]+) A\)\*\*", "DD-3's R19 row")
    S["dd3_r19"] = (f(m, 1), f(m, 2), f(m, 3))
    S["dd3_r19_mohm"] = S["dd3_r19"][1] / S["dd3_r19"][2] ** 2 * 1e3
    need(o9, r"DD-3 R19 passes its 3 W and J_DCIN its VH rating inside F1's envelope", "DD-3")
    hz = flat("".join(pdf_pages("hollr2512")))
    need(hz, r"LLR2512 2W、3W", "the HoLLR2512's power rows")
    S["r19_tmax"] = f(need(hz, r"-55~\+(\d+)", "the HoLLR2512's operating range"))
    S["r19_tknee"] = f(need(hz, r"超过 (\d+)°C", "the derating's knee"))
    m = need(hz, r"额定功率 (\d)W 额定功率倍数 X(\d)倍", "the short-time overload")
    S["r19_p"], S["r19_stol"] = f(m, 1), f(m, 2)
    need(hz, r"施加过负荷5秒", "the overload's 5 s")
    S["r19_stol_s"] = 5.0
    en = ENTRY
    S["r19_hot"] = en["rsns"] * 1.01 * (1 + en["rsns_tcr"] * (S["r19_tmax"] - 25.0))
    S["t_r19"] = S["t0"] + R9_BAND_RISE
    S["r19_der"] = S["r19_p"] * (S["r19_tmax"] - S["t_r19"]) / (S["r19_tmax"] - S["r19_tknee"])
    S["r19_rows"] = []
    # F1's monotone envelope (section 6): (13.5 A, 600 s), (20 A, 5 s), (35 A, 0.5 s), (60 A, 0.1 s) as each row's lower current and the
    # interval's longest time; an interval's top is the next row's current. 600 s is taken as held (the parts' thermal time constants are
    # seconds to minutes: ASSUMPTION)
    rows9 = [("the breaker's highest, held (Q7 working)", N["ioc"][2], None), ("F1's 135 %, held", D["cont_need"], None),
             ("F1's 600 s interval top", D["band"][1][0], None)]
    rows9 += [("F1's %s s interval top" % fmt(D["band"][k][1], 1), D["band"][k + 1][0], D["band"][k][1]) for k in (1, 2)]
    for lab, i_, t_s in rows9:
        w = i_ * i_ * S["r19_hot"]
        if t_s is None:
            S["r19_rows"].append((lab, i_, t_s, w, w / S["r19_der"], "of the derated %s W" % fmt(S["r19_der"], 3)))
        else:
            stol_w = S["r19_stol"] * S["r19_p"]
            S["r19_rows"].append((lab, i_, t_s, w, w * t_s / (stol_w * S["r19_stol_s"]), "of the 5 s overload's energy (%s W for %s s, a room-temperature test)" % (fmt(stol_w, 1), fmt(S["r19_stol_s"], 0))))
    xt = "\n".join(pdf_pages("xt60", True))
    m = need(xt, r"XT60-F[\s\S]*?工作温度\s+\.?-(\d+)℃ to (\d+)℃", "the XT60-F's working range")
    S["xt60f_t"] = (-f(m, 1), f(m, 2))
    S["xt60_rows"] = [(i_, i_ / D["xt60"]) for i_ in (N["ioc"][2], D["cont_need"], 20.0)]
    # L2 at the breaker's highest held current from L4-E12's air (the criterion's initial temperature)
    sz = flat("".join(pdf_pages("srf1260")))
    S["l2_rise_rated"] = f(need(sz, r"Temperature Rise \.+ (\d+) °C at rated Irms", "SRF1260's rated rise"))
    S["l2_tmax"] = f(need(sz, r"-40 °C to \+(\d+) °C \(Temperature rise included\)", "SRF1260's operating range"))
    S["l2_t_trip"] = S["t0"] + S["l2_rise_rated"] * (N["ioc"][2] / N["l2_irms"]) ** 2
    S["l2_i_max"] = N["l2_irms"] * math.sqrt((S["l2_tmax"] - S["t0"]) / S["l2_rise_rated"])
    S["l2_irms_need"] = N["ioc"][2] * math.sqrt(S["l2_rise_rated"] / (S["l2_tmax"] - S["t0"]))
    S["l2_t_service"] = S["t0"] + S["l2_rise_rated"] * (N["i9"] / N["l2_irms"]) ** 2
    S["l2_t_135"] = S["t0"] + S["l2_rise_rated"] * (D["cont_need"] / N["l2_irms"]) ** 2
    # Q1 and Q7 at the breaker's highest held current, and Q1 in F1's 600 s row
    S["q1_w"] = (N["ioc"][2] ** 2 * N["q1_rds"] * FET_HOT, 20.0 ** 2 * N["q1_rds"] * FET_HOT)
    S["q7_w"] = N["ioc"][2] ** 2 * N["q7_rds"] * FET_HOT
    # the coordination selected: a second pass FET on Q7's gate, its cost to the 9 V operating point (the knee flat, a constant input power)
    S["r_add"] = N["q7_rds"] * FET_HOT
    pin = N["i9"] * N["vin9"]
    rr = N["r_hot"] + S["r_add"]
    S["i9_2"] = (PLUG_V - math.sqrt(PLUG_V ** 2 - 4 * rr * pin)) / (2 * rr)
    S["vin9_2"] = PLUG_V - S["i9_2"] * rr
    if S["vin9_2"] < KNEE_TOP:
        refuse(4, "with the second pass FET VIN_RAW leaves the knee's flat band at the plug's 9 V")
    S["eta_2"] = N["pout9"] / (N["ioc"][0] * (PLUG_V - N["ioc"][0] * rr))
    S["margin_2"] = N["ioc"][0] / S["i9_2"] - 1.0
    S["gate_load_2"] = 2 * N["q7_qg"] / 12.0
    return S


def render_fix19(R, p):
    S, N, L, H, D = R["S19"], R["N"], R["L"], R["H"], R["D"]
    p("19. ROUND 9: RECORD l9stk'S PROTECTION AND RECORD l8p'S BREAKER (L8P-F02, L8P-F03, B-P2, E11-29, E11-37, DD-3, IF-1)")
    p("   the inputs (RECORD, read from their commits by sha256): record l9stk's l9stk_protection.out and L9-STACKUPS.md at %s (section 15, independently"
      % R9_COMMITS["l9stk"][:8])
    p("     checked CONFIRMED AS CONDITIONAL), record l8p's L8P-BREAKER.md at %s (its findings L8P-F02 and L8P-F03, run-time refusals of this record's drafts)"
      % R9_COMMITS["l8p"][:8])
    p("   19a. L8P-F02 AND L8P-F03, CORRECTED IN THE DRAFTS (RECORD; the composition proof is the tests' and the page's)")
    p("     L8P-F02: apply_gen_sch_a_charger.py declared VSYS_DOCK with U42 as its source and no source_ic, ahead of VBAT, the rail it is fed from;")
    p("       intent.rail refuses both. The draft now declares VSYS_DOCK after VBAT's declaration with source_ic (U42's OUT pins 18 to 20 are the internal")
    p("       FET's source, the branch's whole current) (RECORD, SESSION)")
    p("     L8P-F03: apply_gen_sch_e_aux.py named L4 as +12V_FAN's source; L4 sits between U22's SW1 and SW2. The draft names U22 with source_ic (the")
    p("       LTC3115-1's VOUT pins carry the rail; its four switches are inside the IC) (RECORD, SESSION)")
    p("   19b. B-P2: THE THIRD BATTERY FET Q42 ON RECORD l9stk'S JUNCTION LIMIT (15.5, SELECTED there; its designator this record's)")
    p("     the limit: the hottest battery FET's junction at most 150 C held at %s A from %s C, the band carrying the current (%s K) and R17 dissipating"
      % (fmt(S["i"], 2), fmt(S["t0"], 2), fmt(S["band"], 2)))
    p("       %s W (%s mOhm at %s A); the budget for the FETs and R17's coupling %s K; R17's coupling into a junction at most %s K/W when placed apart (RECORD)"
      % (fmt(S["pr17"], 2), fmt(S["pr17"] / S["i"] ** 2 * 1e3, 1), fmt(S["i"], 2), fmt(S["budget"], 2), fmt(S["r17_allow"], 1)))
    p("     reproduced on this record's RDS(on) allowance %s mOhm (section 16a) (INFERRED, the record's figures reproduced within rounding):" % fmt(F16_RA * 1e3, 3))
    for n_, lab in ((2, "the pair, (Zself + Zmut)"), (3, "three, (Zself + 2 Zmut)")):
        x = S[n_]
        r_ = S["rec"][n_]
        p("       %s: %s W each at %s A; FETs only %.2f K/W; R17 apart %.2f K/W; R17 anywhere %.2f K/W (INFERRED); record l9stk: %.3f W, %.2f, %.2f, %.2f (RECORD)"
          % (lab, fmt(x["p"], 3), fmt(S["i"] / n_, 3), x["fet_only"], x["apart"], x["anywhere"], r_[0], r_[1], r_[2], r_[3]))
    p("     the three's allowance is %s times the pair's former target of %s K/W (+70 C air, the FETs' heating only), the pair's %s times it (INFERRED)"
      % (fmt(S["ratio3"], 3), fmt(S["zsum_pair_old"], 2), fmt(S["ratio2"], 3)))
    p("     the allowances this record takes are record l9stk's printed ones: %.2f K/W for the three and %.2f K/W for the pair, both with R17 apart (RECORD)"
      % (S["rec"][3][2], S["rec"][2][2]))
    p("     at the allowances (RECORD, l9stk): %.1f C at 10 A, %.1f C at the 18 A service, %.1f C held at %s A; a junction leads its copper by %s K there"
      % (S["tj_rec"][0], S["tj_rec"][1], S["tj_rec"][2], fmt(S["i"], 2), fmt(S["jmb"], 2)))
    p("     DRAFTED (SESSION): Q42, a third BUK6Y10-30PX (C3278350) on the LFPAK56 land, gate CH_BATDRV, drain CH_BATQ, source VBAT, in")
    p("       apply_gen_sch_a_charger.py; Q41 is record l8r2's VIN_RAW cut-off FET and Q42 is free in every board A draft composed in L4-E9's order")
    p("     the layout requirement (SESSION, Layer 9 and board A's PCB generator): the three side by side on one CH_BATQ drain pour and one VBAT source")
    p("       pour, gates from one CH_BATDRV node by equal branches; R17 off that pour; record l8p's enable-loop PTC at the three drain tabs' centroid,")
    p("       within 3 mm of each tab's edge, so it reads the hottest tab's copper within the pour's spread (the thermal guard, l9stk 15.5)")
    p("     the fallback (RECORD, l9stk): the pair at %.2f K/W with R17 apart, if E11-37 refuses three" % S["rec"][2][2])
    p("   19c. E11-29 RESTATED AS THE JUNCTION LIMIT (SESSION, on record l9stk's E-1)")
    p("     the installed three, each FET's (Zself + 2 Zmut) at most %.2f K/W steady with R17 placed apart, R17's coupling into each junction at most %s K/W"
      % (S["rec"][3][2], fmt(S["r17_allow"], 1)))
    p("       (heat R17 alone): so the hottest junction stays at most 150 C held at %s A from %s C with the band and R17 in place (CONDITIONAL on E11-29)"
      % (fmt(S["i"], 2), fmt(S["t0"], 2)))
    p("     the pair's former steady target %s K/W at +70 C air and its 1 s, 20 ms and 244 us targets are WITHDRAWN: with record l8p's breaker (drafted)"
      % fmt(S["zsum_pair_old"], 2))
    p("       no current over %s A lasts longer than its clearing, and the held limit governs; without the breaker DD-1 stays open (RECORD, l9stk)" % fmt(S["i"], 2))
    p("   19d. E11-37 REBOUND TO THE THREE-DEVICE NETWORK (the owner's reviewer, 4 October: the procedure covered the pair only)")
    p("     gate loading: Ciss %s nF typical at -15 V and about %s nF near 0 V for the three (%s and %s times TI's %s nF, SLUSE65A p.%d); no maximum"
      % (fmt(S["ciss3"][0] * 1e9, 2), fmt(S["ciss3"][1] * 1e9, 2), fmt(S["ciss_ratio"][0], 3), fmt(S["ciss_ratio"][1], 3), fmt(H["bf_ciss"] * 1e9, 0), L["ciss_p"]))
    p("       printed; BATDRV's time constants into it %s us on (-15 V), %s us on near 0 V, %s us off (MAKER, INFERRED)"
      % (fmt(S["tau3_on"][0] * 1e6, 2), fmt(S["tau3_on"][1] * 1e6, 2), fmt(S["tau3_off"] * 1e6, 2)))
    p("     what the bench must now cover besides the gate: the three's current sharing in LDO mode and as an ideal diode (one gate node, three")
    p("       thresholds), and their thermal coupling on one pour (each junction read); thermal improvement does not close the gate-drive question")
    p("     STATUS: OPEN, condition: Q-TI-17 (extended to three devices, drafted, not sent) or E11-37's bench with the three; production conformance")
    p("       needs one of them (record l9stk's C3) (SESSION)")
    p("   19e. DD-3, THE SHORE INPUT, BY THE OWNER'S CURRENT-AND-TIME CRITERION (ONE DESIGN-OUT ATTEMPT)")
    p("     the defect as stated (RECORD, l9stk 14.6): R19 at %.1f W at 20 A, over its %s W from %s A (the drawn %s mOhm part), and J_DCIN's JST VH at 10 A,"
      % (S["dd3_r19"][0], fmt(S["dd3_r19"][1], 0), fmt(S["dd3_r19"][2], 2), fmt(S["dd3_r19_mohm"], 1)))
    p("       inside F1's 600 s interval; R-123's R19 is 4.5 mOhm, which l9stk's table did not read (RECORD)")
    p("     the criterion's initial temperature: L4-E12's %s C (RECORD), the parts' own heating on top; R19's local ambient %s C with the band's %s K (ASSUMPTION)"
      % (fmt(S["t0"], 2), fmt(S["t_r19"], 2), fmt(R9_BAND_RISE, 0)))
    p("     THE ATTEMPT (SESSION): coordinate the protection and strengthen the parts DD-3 names:")
    p("       (1) J_DCIN DRAFTED as the Amass XT60-F (C98734, apply_gen_sch_e_entry.py), D-06's selection: %s A rated, %s A instantaneous, %s to %s C (MAKER)"
      % (fmt(D["xt60"], 0), fmt(D["xt60_inst"], 0), fmt(S["xt60f_t"][0], 0), fmt(S["xt60f_t"][1], 0)))
    p("       (2) R19 as R-123 drafts it, the HoLLR2512 4.5 mOhm 3 W (C2985708), judged on its maker's sheet (held): %s W to %s C, derated linearly to %s C;"
      % (fmt(S["r19_p"], 0), fmt(S["r19_tknee"], 0), fmt(S["r19_tmax"], 0)))
    p("           a 5 s short-time overload at %s times the rated power; hot %s mOhm (+1 %%, 50 ppm/K to %s C): %s W at %s C (MAKER, INFERRED)"
      % (fmt(S["r19_stol"], 0), fmt(S["r19_hot"] * 1e3, 3), fmt(S["r19_tmax"], 0), fmt(S["r19_der"], 3), fmt(S["t_r19"], 2)))
    p("       (3) a second pass FET in series with Q7 on its gate (the same CSD19536KTT, same orientation), so one welded FET leaves the other to open")
    p("           and every series part sees the breaker's envelope, not F1's, after a single fault (SESSION, the coordination)")
    p("     R19, row by row (INFERRED):")
    for lab, i_, t_s, w, frac, basis in S["r19_rows"]:
        p("       %s: %s A%s, %s W, %s %s" % (lab, fmt(i_, 3), "" if t_s is None else " for %s s" % fmt(t_s, 1), fmt(w, 3), fmt(frac, 3), basis))
    p("       a 35 A, 5 s row from %s C is not the maker's room-temperature test: CONDITIONAL on E11-16's short-time data; over 60 A, F1's clearing I2t (E11-16)" % fmt(S["t_r19"], 2))
    p("     J_DCIN (XT60-F): %s (MAKER, INFERRED); 35 A and 60 A within the 60 A instantaneous figure, its duration unstated (E11-16)"
      % "; ".join("%s A at %s of %s A" % (fmt(i_, 3), fmt(fr, 3), fmt(D["xt60"], 0)) for i_, fr in S["xt60_rows"]))
    p("     the other series parts by the same criterion (INFERRED):")
    p("       Q7 at the breaker's highest held %s A: %s W; Q1 (BSC039N06NS) %s W, and %s W at F1's 20 A, which no held installed path bounds: the coordination"
      % (fmt(N["ioc"][2], 3), fmt(S["q7_w"], 3), fmt(S["q1_w"][0], 3), fmt(S["q1_w"][1], 2)))
    p("         (3) keeps it at the breaker's figure after a single fault")
    p("       L2 (SRF1260-1R0Y, %s A Irms at a %s K rise, %s C including the rise; MAKER): at the breaker's highest held %s A from %s C it reaches %s C,"
      % (fmt(N["l2_irms"], 2), fmt(S["l2_rise_rated"], 0), fmt(S["l2_tmax"], 0), fmt(N["ioc"][2], 3), fmt(S["t0"], 2), fmt(S["l2_t_trip"], 2)))
    p("         OVER its %s C; it carries at most %s A held from that air (the breaker's least threshold %s A, its highest %s A); a part rated at least %s A"
      % (fmt(S["l2_tmax"], 0), fmt(S["l2_i_max"], 3), fmt(N["ioc"][0], 3), fmt(N["ioc"][2], 3), fmt(S["l2_irms_need"], 2)))
    p("         at a %s K rise is needed; at the 9 V in-service maximum %s A it reads %s C, within (MAKER, INFERRED); section 3e's %s C was at the %s C air"
      % (fmt(S["l2_rise_rated"], 0), fmt(N["i9"], 3), fmt(S["l2_t_service"], 2), fmt(N["l2_rise"] + R["F"]["air_hot"], 1), fmt(R["F"]["air_hot"], 1)))
    p("       F1's holder, the Keystone 3568, prints no current rating: record l9stk's DD-4, Layer 6 and 7's (RECORD)")
    p("     the coordination's cost (INFERRED): %s mOhm hot in the loop; at a 9.00 V plug %s A (was %s A), VIN_RAW %s V, %s %% under the lowest trip;"
      % (fmt(S["r_add"] * 1e3, 2), fmt(S["i9_2"], 3), fmt(N["i9"], 3), fmt(S["vin9_2"], 3), fmt(S["margin_2"] * 100, 1)))
    p("       the efficiency floor %s (was %s); the gate load %s nF for the two, under the %s nF load TI's short-circuit row is printed at (MAKER, INFERRED)"
      % (fmt(S["eta_2"], 4), fmt(N["eta_floor"], 4), fmt(S["gate_load_2"] * 1e9, 2), "47"))
    p("     RESULT: the attempt FAILS on L2 (and F1's holder stays DD-4): DD-3 stays OPEN, owner L4-E11 with board E's generator owner (SESSION);")
    p("       condition E11-41: L2's winding at most %s C held at %s A from %s C on board E's land, or a choke whose rating covers it with the input filter's attenuation"
      % (fmt(S["l2_tmax"], 0), fmt(N["ioc"][2], 3), fmt(S["t0"], 2)))
    p("       shown again; the second pass FET is drafted with that choke in one board E change (one recomputation of section 3's loop); J_DCIN's")
    p("       XT60-F is drafted now, independent of it (SESSION)")
    p("   19f. IF-1: EVERY BOARD A LOAD ON VSYS HELD THROUGH THE PACK BREAKER'S START (SESSION; record l9stk's IF-1, owner this record with board A's generator)")
    p("     the start (RECORD, l9stk): dv/dt %s nF +-%s %% into %s uF, gate %s to %s uA: %s to %s V/ms, %s A at most, %s ms at most to %s V; the enable's hold"
      % (fmt(S["start"]["cdv"] * 1e9, 0), fmt(S["start"]["tol"] * 100, 0), fmt(S["start"]["cout"] * 1e6, 0), fmt(S["start"]["ig"][0] * 1e6, 0), fmt(S["start"]["ig"][1] * 1e6, 0),
         fmt(S["dvdt"][0] * 1e-3, 3), fmt(S["dvdt"][1] * 1e-3, 3), fmt(S["start"]["inrush"], 3), fmt(S["start"]["tmax"] * 1e3, 1), fmt(S["vmax"], 1)))
    p("       %s to %s s after the enable mates; the power limit's least %s W; the start's own %s W against the %s W DC line (RECORD)"
      % ("%.3f" % S["grace"][0], "%.3f" % S["grace"][1], fmt(S["plim"][0], 2), "%.1f" % S["start_w"], "%.1f" % S["dc_line"]))
    p("     the drawn loads: every converter on VBAT is enabled by RAIL_EN or behind it (U12, U41, U39 and what +3V3 enables), and U1 (LTC2954-1) holds")
    p("       RAIL_EN low from power-up until MAIN has been held %s ms at least (MAKER); U42's branch to board E is always on (NETLIST, drafts)" % fmt(S["tdb"][0] * 1e3, 0))
    p("     the defect IF-1 names (INFERRED): U42 on from its IN's %s V floor feeds board E's U12 and U22 through the start; at that point the breaker FET"
      % fmt(S["u42_vin"], 1))
    p("       drops %s V and carries the inrush plus up to U42's %s A: %s W, over the power limit's least %s W, so the timer runs and the -1 latches;"
      % (fmt(S["u42_vds"], 2), fmt(L["ilim"][1], 3), fmt(S["u42_w"], 1), fmt(S["plim"][0], 2)))
    p("       and MAIN held through a docking asserts RAIL_EN %s ms after the ramp begins at the slowest slope, with %s V across the breaker FET"
      % (fmt(S["en_early"] * 1e3, 1), fmt(S["en_vds"], 2)))
    p("     THE HOLD (SESSION, drafted in apply_gen_sch_a_charger.py): U46, the TPS37A010122DSKR U34 already is (C3685740), on VBAT (VDD %s to %s V; MAKER):"
      % (fmt(S["vdd"][0], 1), fmt(S["vdd"][1], 0)))
    p("       channel 2 (UV) through R86 %s k over R87 %s k at 1 %%: VBAT falling %s / %s / %s V, rising %s / %s / %s V (MAKER, INFERRED)"
      % (fmt(R9_SUP[0] / 1e3, 0), fmt(R9_SUP[1] / 1e3, 0), fmt(S["fall"][0], 3), fmt(S["fall"][1], 3), fmt(S["fall"][2], 3), fmt(S["rise"][0], 3), fmt(S["rise"][1], 3), fmt(S["rise"][2], 3)))
    p("       CTR2 C105 100 nF (+-%s %%, X7R +-%s %%, ASSUMPTION): the release %s / %s / %s ms after VBAT passes the rising threshold (SNVSBJ1E Equations 1 to 3);"
      % (fmt(R9_C_TOL[0] * 100, 0), fmt(R9_C_TOL[1] * 100, 0), fmt(S["hold"][0] * 1e3, 1), fmt(S["hold"][1] * 1e3, 1), fmt(S["hold"][2] * 1e3, 1)))
    p("         a fall re-asserts within %s us (tCTS at 800 mV, MAKER) (INFERRED)" % fmt(S["tcts"][1] * 1e6, 0))
    p("       RESET2 pulls U42's UVLO (EF_UVLO) under %s V, below its %s V falling threshold: U42 off within %s us (MAKER); released, R88 %s k over R89 %s k give"
      % (fmt(R9_VOL, 1), fmt(S["uvlof"][0], 2), fmt(S["uvlo_toff"] * 1e6, 0), fmt(R9_EF[0] / 1e3, 0), fmt(R9_EF[1] / 1e3, 0)))
    p("         U42 its own UVLO at %s V on at most and %s V off at least, under U46's, and EF_UVLO %s V at VBAT %s V, over %s V and SENSE1's %s V;"
      % ("%.2f" % S["own_on_max"], "%.2f" % S["own_off_min"], fmt(S["ef_release"], 3), fmt(S["rise"][0], 3), fmt(S["uvlor"][2], 3), "0.808"))
    p("         %s V at VBAT's %s V clamp (60 V pin); RESET2 sinks %s mA there (INFERRED)" % (fmt(S["ef_clamp"], 2), fmt(S["vbat_clamp"], 1), fmt(S["ef_sink"] * 1e3, 3)))
    p("       channel 1 (OV) reads EF_UVLO: held (%s V at most) is under its %s V falling threshold, so RESET1 is released, R105 100 k lifts SYS_HOLD_G (D24"
      % (fmt(R9_VOL, 1), fmt(S["ov_fall_min"], 3)))
    p("         BZT52C12, %s to %s V: Q43's VGS under its %s V) and Q43 (2N7002, threshold %s to %s V) pulls RAIL_EN low (MAKER, INFERRED)"
      % (fmt(S["vz"][0], 1), fmt(S["vz"][1], 1), fmt(S["vgs_max"], 0), fmt(S["vth"][0], 1), fmt(S["vth"][2], 1)))
    p("       RAIL_EN can reach the TPS62933's %s V disable threshold only from VBAT %s V up, where Q43's gate is %s V over its %s V threshold maximum; under"
      % (fmt(S["ven_fall"], 2), fmt(S["rail_vbat_on"], 3), fmt(S["q43_overdrive"], 2), fmt(S["vth"][2], 1)))
    p("         U46's %s V both outputs assert and Q43 is off, RAIL_EN then at most %s V (MAKER, INFERRED)" % (fmt(S["vdd"][0], 1), fmt(S["rail_held_vdd"], 3)))
    p("     THE RESULT (INFERRED): the start ends at most %s ms after VBAT begins to rise; the hold releases at least %s ms after VBAT passes the rising"
      % (fmt(S["start"]["tmax"] * 1e3, 1), fmt(S["hold"][0] * 1e3, 1)))
    p("       threshold, %s ms later at the least: no board A load on VSYS draws through the start; a quick undocking and redocking with VBAT held up:"
      % fmt(S["hold_margin"] * 1e3, 1))
    p("       through board E's load: more than %s mA takes VBAT under %s V before the breaker can start (VSYS's %s uF over %s s), U46 asserts and the"
      % (fmt(S["redock_i"] * 1e3, 1), fmt(S["fall"][2], 3), fmt(S["start"]["c_vsys"] * 1e6, 0), "%.3f" % S["grace"][0]))
    p("       start is held; a smaller load leaves the hold released, and the guarantee below bounds that start")
    p("     PGD NOT USED (SESSION): it needs an eighth J_SMB position and a dock contact through two connectors from board P (record l8p); a supervisor")
    p("       on board A acts on what board A's loads see, for every start (a docking, the gauge's FET, a retry, a source-only rise), with no new interface")
    p("     the residuals (INFERRED):")
    p("       MAIN held through a docking: U1 asserts first and RAIL_EN follows the hold; the panel controller keeps at least %s ms of U1's %s ms KILL"
      % (fmt(S["kill_left"] * 1e3, 1), fmt(S["kill"][0] * 1e3, 0)))
    p("         blanking to raise KILL; if it needs more, U1 releases EN and a second press starts the kit (E11-42 c)")
    p("       a source present: VSYS at %s V at least holds U46 released, the loads stay on, and the breaker carries only what the charger does not, at"
      % fmt(H["floor"], 3))
    p("         %s V across its FET at most: under %s A of excess its power limit never acts; over it the -1 latches (record l9stk 15.4b) while the"
      % (fmt(S["src_vds"], 3), fmt(S["src_excess"], 2)))
    p("         source carries the kit, and 19h's inhibit keeps the charge off the latched FET")
    p("       a VBAT under %s V in service holds every RAIL_EN converter and the dock branch (was each converter's own UVLO, about 4.3 V for U12): VBAT"
      % fmt(S["fall"][2], 3))
    p("         is at least the pack's %s V less the path's drop or VSYS_MIN's %s V in every mode, so only a collapse reaches it" % (fmt(S["pack_lo"], 1), fmt(H["floor"], 3)))
    p("       record l9stk's IF-5: once record l8p's drafts are applied the docking pulse E11-30 qualifies no longer arises; E11-30 is kept until then")
    p("     THE GUARANTEE UNDER THE -1 (record l9stk 15.4b: a start that meets the power limit latches and the kit stays dark; IF-1 CRITICAL TO THE")
    p("       SERVICE: the start leaves room for at most %s A of load at full VDS; INFERRED):" % fmt(S["if1_room"], 2))
    p("       what board A still draws from VBAT while U46 holds (RAIL_EN low, +3V3 down, every enable on its pull-down: NETLIST), at %s V,"
      % fmt(S["vpk"], 1))
    p("         each part at its sheet's largest printed figure:")
    for lab, x, cl in S["static"]:
        p("           %s: %s mA (%s)" % (lab, "%.4f" % (x * 1e3), cl))
    p("         in all %s mA, %s %% of the %s A room; board E's VSYS_E is off behind U42" % ("%.2f" % (S["static_sum"] * 1e3), "%.2f" % (S["static_frac"] * 100), fmt(S["if1_room"], 2)))
    p("       every start from a VBAT under %s V (a docking, a redocking after the kit went dark, the input-return restart of 19h, the guard's cycle):"
      % fmt(S["fall"][0], 3))
    p("         no board A load draws (the hold outlasts the start by %s ms at the least); the breaker FET carries the inrush alone, %s W"
      % (fmt(S["hold_margin"] * 1e3, 1), "%.1f" % S["start_w"]))
    p("       a start with VBAT held over %s V by board A's capacitance (a quick redocking, the whole load under %s mA to hold it 0.110 s): the"
      % (fmt(S["fall"][0], 3), fmt(S["redock_i"] * 1e3, 1)))
    p("         breaker carries up to %s A of load before its power limit acts (VDS at most %s V); a step past that within the start latches the -1"
      % (fmt(S["redock_room"], 2), fmt(S["vpk"] - S["fall"][0], 3)))
    p("         and the kit goes dark until a redock or an input (a residual of a quick redock with a load stepping; U42's 1.802 A alone: %s W)"
      % fmt(S["redock_w"], 1))
    p("       a start with a source carrying VSYS: at most %s A of excess over the charger before the power limit acts; beyond that the pack"
      % fmt(S["src_excess"], 2))
    p("         latches while the source carries the kit, which stays up (not dark)")
    p("   19h. DD-7: THE LATCH-OFF -1, THE INPUT-RETURN RESET AND THE HARDWARE CHARGE INHIBIT (record l9stk 15.4b at %s; the checker's B-R2)"
      % R9_COMMITS["l9stk"][:8])
    p("     the -1 (RECORD, l9stk): selected over the -2; after a trip it stays off until UVLO or VIN cycles; the timer falls under 0.3 V in %.1f ms at"
      % (S["timer_reenable"] * 1e3))
    p("       most; when the loop opens the second inverter is on in %s us and UVLO falls at once, C_U draining in %s ms behind it; a restart within"
      % (fmt(S["inv2_on"] * 1e6, 1), "%.2f" % (S["uvlo_fall"] * 1e3)))
    p("       %s s once the loop closes (the hold and the start), later while C-1c, the restart inhibit on the breaker pad, holds a hot pad (RECORD)"
      % fmt(S["dd7_restart"], 3))
    p("     THE INPUT-RETURN RESET (SESSION, drafted in apply_gen_sch_a_dd7.py, after record l8p's PTC draft): Q44 (2N7002) pulls DOCK_EN_RET low,")
    p("       which opens the loop as an undocking does; its gate DD7_G is VIN_RAW through R106 1M, clamped by D25 (BZT52C12, %s to %s V);"
      % (fmt(S["vz"][0], 1), fmt(S["vz"][1], 1)))
    p("       Q45 (gate FE_RUN) ends the pulse when U34 releases the front end, %s / %s / %s ms after VIN_RAW passes U34's UV threshold (%s to %s V"
      % (fmt(S["pulse"][0] * 1e3, 1), fmt(S["pulse"][1] * 1e3, 1), fmt(S["pulse"][2] * 1e3, 1), fmt(S["guard_rise"][0], 3), fmt(S["guard_rise"][2], 3)))
    p("       rising with this record's R14), C212 being C105's part and value on the same TPS37A010122; Q46 (gate DD7_ALIVE, CELL+ over R107 /")
    p("       R108) holds the gate low while CELL+ is over %s V, and cannot conduct under %s V: an input arriving on a live pack opens nothing"
      % (fmt(S["alive_on"], 2), fmt(S["alive_off"], 2)))
    p("       (MAKER, INFERRED)")
    p("     the pulse against what it must do (INFERRED): at least %s ms, %s times C_U's %.2f ms drain; the timer's %.1f ms re-enable falls inside the"
      % (fmt(S["pulse"][0] * 1e3, 1), fmt(S["pulse_margin"], 0), S["uvlo_fall"] * 1e3, S["timer_reenable"] * 1e3))
    p("       pulse and the hold, %s ms to spare; from VIN_RAW passing U34's threshold to the restart's end at most %s s (the pulse %s ms, the hold"
      % (fmt(S["pulse_vs_timer"] * 1e3, 1), fmt(S["dd7_total"], 3), fmt(S["pulse"][2] * 1e3, 1)))
    p("       %s s, the start %s ms), longer while C-1c holds a hot pad (its cooling time NOT HELD, record l9stk's E-15)"
      % (fmt(S["grace"][1], 3), fmt(S["start"]["tmax"] * 1e3, 1)))
    p("     the UVLO edge (RECORD, l9stk): read at the falling edge, an input arriving within %.1f ms of a latch does not restart the breaker; that"
      % (S["timer_reenable"] * 1e3))
    p("       fails safe (the breaker stays off, the hardware inhibit below holds the charge); the input's next return or a redocking restarts it")
    p("     THE HARDWARE CHARGE INHIBIT (SESSION, the same draft; the checker's B-R2: a persistent fault latches the -1 again with the input still")
    p("       present and no second pulse comes): Q47 (gate SYS_INH_G, DOCK_EN_OUT over R109 1M and R144 1M) turns Q49 (AO3401A) on through R82")
    p("       100k and R83 200k; Q49 holds CH_BATDRV at VBAT, so Q39, Q40 and Q42 are off and their body diodes point from the pack to VSYS: no")
    p("       charge leaves VSYS for the pack; Q48 (gate DD7_ALIVE) releases it once CELL+ is over %s V. The signal: the loop powered (DOCK_EN_OUT"
      % fmt(S["alive_on"], 2))
    p("       alive: the pack's cells reach board P's breaker) and the terminal dead (CELL+ under %s V): exactly the breaker off (latched, in its"
      % fmt(S["alive_off"], 2))
    p("       hold or starting) with the cells present; no firmware (MAKER, INFERRED)")
    p("     its levels (INFERRED): DOCK_EN_OUT at least %s V docked (the pack's %s V, RT1 at its cold least %s kOhm, l8p's %s k and %s k), SYS_INH_G at"
      % (fmt(S["loop_out_lo"], 3), fmt(S["pack_lo"], 1), fmt(S["rt1"][0] / 1e3, 0), fmt(S["r_feed"] / 1e3, 0), fmt(S["r_ret"] / 1e3, 0)))
    p("       least %s V over Q47's %s V threshold maximum; Q49's VGS %s V at VSYS_MIN's %s V (threshold -1.3 V at most) and %s V at the %s V"
      % (fmt(S["inh_g_lo"], 3), fmt(S["vth"][2], 1), "%.2f" % -S["q49_vgs"][0], fmt(H["floor"], 3), "%.2f" % -S["q49_vgs"][1], fmt(S["vbat_clamp"], 1)))
    p("       clamp (12 V absolute); BATDRV meanwhile sinks at most %s mA (%s V over its %s kOhm least RBATDRV_ON, SLUSE65A; MAKER, INFERRED)"
      % (fmt(S["batdrv_sink"] * 1e3, 2), fmt(S["batdrv_on"], 1), fmt(S["rbatdrv_on_min"] / 1e3, 0)))
    p("     the loop's load (INFERRED, an interface effect for records l9stk and l8p): the 2 MOhm sense at DOCK_EN_OUT moves the first inverter's gate")
    p("       at l9stk's bound point (%s V, RT1 at %s kOhm) from %s V to %s V, against its 2.5 V threshold"
      % (fmt(S["pack_lo"], 1), fmt(S["rt1"][2] / 1e3, 0), "%.3f" % S["ret_bound"][0], "%.3f" % S["ret_bound"][1]))
    p("     not inhibited, by design: with the loop unpowered (the gauge's FETs off, a pack absent, undocked) a pack's wake and precharge pass the")
    p("       breaker's body diodes at the gauge's own current (record l9stk's charge direction); source-only operation (U-04) is untouched (RECORD)")
    p("     E-14, EXTENDED TO A SECOND LATCH WITH THE INPUT PRESENT (INFERRED): with the inhibit the charge into a latched breaker is the battery")
    p("       FETs' off leakage (IDSS %s uA at 25 C each, the hot value not printed); without it, at the breaker FET's VSD %s V at most and IF-2's %s C/W:"
      % (fmt(S["idss"] * 1e6, 0), fmt(S["vsd"], 1), fmt(S["rja_brk"], 1)))
    for lab, i_, w_, tj_ in S["e14"]:
        p("         %s, %s A: %s W, TJ %s C held" % (lab, fmt(i_, 4), fmt(w_, 3), fmt(tj_, 1)))
    p("       so the inhibit is what holds a commanded charge beyond R-b off the FET (the checker's 4 A, 4 W, 276 C) wherever it sets (its reach")
    p("       below); E11-45 measures it (INFERRED)")
    p("     the charger-side hold (SESSION): hardware, the inhibit above, until the terminal is alive where it sets; the firmware's IF-7 reports the trip and writes")
    p("       ChargeCurrent only after the restart (E11-44); the hold does not wait on it")
    p("     ITS REACH, READ AFTER DRAFTING (INFERRED; the one design-out attempt): the inhibit sets only when CELL+ falls under %s V. A latch while"
      % fmt(S["alive_off"], 2))
    p("       a source is present (the pack supplementing into the fault, the battery FETs on) leaves CELL+ tied to VSYS, which the charger holds")
    p("       into a resistive fault at sqrt(P x R): %s V at the breaker's least-limit fault of %s ohm with the front end's %s W (its %s A ISNS maximum)"
      % (fmt(S["v_fault"], 1), fmt(S["r_fault"], 3), fmt(S["p_src"], 1), "5.7"))
    p("       so the inhibit sets only for faults under %s mOhm; when such a fault clears with the -1 latched, a charge passes the breaker's body"
      % fmt(S["r_assert"] * 1e3, 0))
    p("       diode with CELL+ reading alive. The breaker's PGD reads high in that state too (its VDS negative; LM5069 8.3.6 switches on VDS alone),")
    p("       so no board A signal tells a latched -1 passing charge from an -1 that is on: that case needs board P's gate state or a reverse-blocking")
    p("       element (route R1, board P's generator with record l9stk), or a hardware cap on the charge current on board A (route R2: above R-b's")
    p("       %s A and under %s A, the latched FET's body diode at 150 C held from %s C at VSD %s V and %s C/W; a high-side current-sense part with"
      % (fmt(S["capwin"][0], 4), fmt(S["capwin"][1], 3), fmt(S["t0"], 2), fmt(S["vsd"], 1), fmt(S["rja_brk"], 1)))
    p("       a timed off-state, none held). Until one is drawn, a charge past R-b in that state rests on the firmware (R-b and IF-7); at R-b's")
    p("       largest the FET reads the E-14 row above (SESSION: R1 preferred; R2 the fallback)")
    p("     residuals (INFERRED): Q49 shorted holds the battery FETs off (their body diodes carry the discharge, and record l8p's PTC trips the breaker")
    p("       before their junctions pass 150 C); Q47, Q48 or Q49 open loses the inhibit or never releases it (both found by E11-45); a Q46 open lets")
    p("       an input's arrival drop a live pack for the pulse and the restart (E11-45 b); Q44 shorted holds the breaker off (fail-safe, revealed)")
    p("     STATUS: DD-7 DRAFTED for the first restart and for every latch whose fault takes CELL+ dead (the dark kit, a hard short, the input's")
    p("       return), CONDITIONAL on E11-45 and TI's answer on BATDRV held at VSYS (Q-TI-17's addendum); B-R2 OPEN for a latch with a source")
    p("       present into a resistive fault (route R1, owner board P's generator with record l9stk; R2 this record's fallback); IF-7 the firmware")
    p("       owner's (SESSION)")
    p("")

# ---- round 10 (4 October 2026): record l8p's round 3 (fnd/l8p2 at a46597e2) and its findings L8P-F04 and L8P-F05 for DD-7's board A side
R9_COMMITS["l8p2"] = "a46597e2257018bb4fdb749a57902bd7b78663a3"
R9_GIT["l8p2_page"] = ("l8p2", "v2/docs/records/l8p/L8P-BREAKER.md", "6b6cd75ca947c8df065c9a2dd3a61b9a9225a32174b5caa804634ed911986a30")
R9_GIT["l8p2_out"] = ("l8p2", "v2/docs/records/l8p/l8p_drafts.out", "4bed261029cdcabb85b96b8882e51fdc2710b536e00a0350641c3db304948145")
R10_OUT = (562e3, 422e3)       # ohm, SESSION: R109 over R144 (0.1 %), U48's SENSE2 on DOCK_EN_OUT
R10_OUT_TOL = 0.001
R10_CS = (464e3, 100e3)        # ohm, SESSION: R107 over R108 (1 %), U47's SENSE2 on CELL+
R10_CS_TOL = 0.01
R10_RH, R10_RH_TOL = 1.2e6, 0.01           # ohm, SESSION: R85, the hold's discharge
R10_CH = 1e-6                  # F, SESSION: C241, FS32X105K101EFG (C382212, the part of C207), 1 uF 100 V X7R 1210, K
R10_CH_TOL = (0.10, 0.15)      # ASSUMPTION: K (+-10 %) and X7R's +-15 % over temperature (the record's C105 basis)
R10_CH_BIAS = 0.15             # ASSUMPTION: C241's loss under DC bias at 12 V or less on its 100 V rating (no curve held); E11-45 times the hold
R10_CH_IR = 100e6 * 1e-6       # ohm F, ASSUMPTION: insulation resistance 100 MOhm uF (a fifth of the usual 500 MOhm uF)
R10_CTS, R10_CTS_TOL = 3.9e-9, 0.05        # F, SESSION: C248, C0G J on U47's CTS1
R10_RA, R10_RK, R10_RBL = 56.0, 10e3, 4.7e3  # ohm, SESSION: R84 (1206, pulse-rated), R253, R256 (1206; 4.7k in round 10, 6.8k in round 11 on V1's minor, 4.7k again in round 12 on V2-B1: section 22)
R10_RAG = (100e3, 200e3)       # ohm, SESSION: R251 over R252 (1 %), Q51's VGS
R10_RPU = (100e3, 1e6, 1e6, 1e6)           # ohm, SESSION: R249 (DD7_LP), R250 (DD7_T), R255 (DD7_N), R254 (DD7_REF), from DD7_VC
R10_RVC = 100e3                # ohm, SESSION: R233, VBAT to DD7_VC (D27 BZT52C12)
R10_T_SMALL = 10.0             # K, ASSUMPTION: the small parts' leakage read 10 K over L4-E12's air (R19's band basis)
R10_C_T = 2 * 50e-12 + 10e-12  # F, ASSUMPTION: DD7_T's node, Q50's Ciss (50 pF typical, JSCJ prints no maximum) doubled, and U48's pin
R10_CISS_X = 1.5               # ASSUMPTION: an AO3401A's typical Ciss (645 pF) taken 1.5 times (no maximum printed)
R10_VOL_R = None               # set in the round from the sheet: RESET's VOL at most over its 5 mA row, an on-resistance bound
R10_T2 = 9.0 / 8.0             # the most one of three paralleled FETs dissipates against the even split (r / (R + 2 r)^2 at r = R/2)


def fix20_round(R, T):
    """Round 10 (record l8p's round 3, route R1): board A's side of the breaker's latch redrawn against L8P-F04 and L8P-F05 on the same
    failure cases (C-PROT): the return held at BRK_VIN 7.6 and 10.6 V, CELL+ with the breaker off at 16.8 V and the 29.2 V clamp, the breaker
    latched into a resistive fault with a source present; thresholds, tolerances and delays from the makers' printed figures."""
    S9, H = R["S19"], R["H"]
    S = {}
    o8 = git_at("l8p2_out")
    p8 = flat(git_at("l8p2_page"))
    # ---- what board P drives, and the interface it asks (record l8p 12c and 12f; its output 3b)
    S["held"] = f(need(o8, r"DOCK_EN_RET held at ([\d.]+) V at most", "the pull's level"))
    m = need(o8, r"DOCK_EN_OUT falls to ([\d.]+) V at BRK_VIN 7\.6 V and ([\d.]+) V at\s+10\.6 V", "the held DOCK_EN_OUT")
    S["out_held_rec"] = (f(m, 1), f(m, 2))
    m = need(o8, r"reads ([\d.]+) and ([\d.]+) V, under the 2N7002's ([\d.]+) V: L8P-F04", "L8P-F04's readings")
    S["f04"] = (f(m, 1), f(m, 2), f(m, 3))
    S["pull_t"] = f(need(o8, r"([\d.]+) ms at most to the pull", "the pull's delay")) * 1e-3
    S["restart"] = f(need(o8, r"the breaker restarts within ([\d.]+) s", "the restart"))
    m = need(o8, r"least ([\d.]+) A against the LDO-mode precharge's ([\d.]+) A at most", "the threshold's least")
    S["thr_lo"], S["ldo"] = f(m, 1), f(m, 2)
    m = need(o8, r"most ([\d.]+) A against the latched FET's ([\d.]+) A", "the threshold's most")
    S["thr_hi"], S["fet_safe"] = f(m, 1), f(m, 2)
    S["under_thr_tj"] = f(need(o8, r"a charge the detector lets pass holds the FET at ([\d.]+) C at most", "the detector's floor"))
    S["pulse_k"] = f(need(o8, r"raises its\s+junction ([\d.]+) K over the case", "10 ms at 23.93 A"))
    m = need(o8, r"with board A's (\d+) kOhm \(R107, R108\) alone CELL\+ reads ([\d.]+) V at BRK_VIN ([\d.]+) V, over L4-E11's ([\d.]+) V 'dead' point", "L8P-F05")
    S["f05"] = dict(r_a=f(m, 1) * 1e3, v=f(m, 2), vin=f(m, 3), dead=f(m, 4))
    m = need(o8, r"with U104's divider\s+\(([\d.]+) kOhm\) also on PACK_P, ([\d.]+) V \(([\d.]+) V at the 29\.2 V clamp\)", "L8P-F05 with U104")
    S["u104"], S["f05"]["v_u104"], S["f05"]["v_clamp"] = f(m, 1) * 1e3, f(m, 2), f(m, 3)
    S["r_int"] = f(need(o8, r"the LM5069's internal (\d+) MOhm from SENSE to OUT", "the LM5069's internal resistor")) * 1e6
    need(p8, r"Set its charge inhibit \(the battery FETs held off, BATDRV at VBAT\) while DOCK_EN_RET is under 1\.0 V and DOCK_EN_OUT is at 2\.0 V or over, whatever CELL\+ reads", "12f's set")
    need(p8, r"Set it within 1 ms of the return falling", "12f's 1 ms")
    need(p8, r"Hold it at least 1\.0 s after DOCK_EN_RET rises over 2\.5 V", "12f's hold")
    need(p8, r"Load DOCK_EN_RET with 1 MOhm or more", "12f's load")
    S["if_ret_lo"], S["if_out"], S["if_hold"], S["if_ret_hi"], S["if_load"] = 1.0, 2.0, 1.0, 2.5, 1e6
    r_feed, r_ret = S9["r_feed"], S9["r_ret"]
    # ---- the parts (makers' sheets)
    m = find("tps37", r"\(Overvoltage\)\s+VIT\s+= 800 mV \(3\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "VITP at 800 mV", layout=True)[1]
    vitp = (f(m, 1), f(m, 2), f(m, 3))
    m = find("tps37", r"\(Undervoltage\)\s+VIT = 800 mV \(3\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "VITN at 800 mV", layout=True)[1]
    vitn = (f(m, 1), f(m, 2), f(m, 3))
    hys = f(find("tps37", r"typically meant to monitor a 0\.8 V rail with ±(\d+)% voltage threshold\s+hysteresis", "the variant's hysteresis")[1]) / 100.0
    hacc = f(find("tps37", r"VHYS Range = 2% to 13% \(1% step\) -([\d.]+) ([\d.]+) %", "the hysteresis accuracy")[1]) / 100.0
    i_s = f(find("tps37", r"Input current\s+ISENSE\s+VIT = 800 mV\s+(\d+)\s+nA", "ISENSE at 800 mV", layout=True)[1]) * 1e-9
    i_s_hi = f(find("tps37", r"Input current\s+VIT > 26 V\s+ISENSE\s+(\d+)\s+µA", "ISENSE's largest row", layout=True)[1]) * 1e-6
    m = find("tps37", r"RCTS\s+(\d+)\s+(\d+)\s+(\d+)\s+Kohms", "RCTS", layout=True)[1]
    rcts = (f(m, 1) * 1e3, f(m, 2) * 1e3, f(m, 3) * 1e3)
    k5 = f(find("tps37", r"tCTSx \(min\) = -ln \(([\d.]+)\) x RCTSx \(min\)", "Equation 5")[1])
    k6 = f(find("tps37", r"tCTSx \(max\) = -ln \(([\d.]+)\) x RCTSx \(max\)", "Equation 6")[1])
    vol = f(find("tps37", r"VOL \(5\)\s+Low level output voltage\s+(\d+)\s+mV", "RESET's VOL", layout=True)[1]) * 1e-3
    S["i_rec"] = f(find("tps37", r"Current\s+IRESET1, IRESET2, IRESET1, IRESET2\s+0\s+±(\d+)\s+mA", "RESET's recommended current", layout=True)[1]) * 1e-3
    i_vol = f(find("tps37", r"IRESET = (\d+) mA", "VOL's current", layout=True)[1]) * 1e-3
    find("tps37", r"SENSE and RESET pins are 65 V graded", "the 65 V pins")
    S["vol_r"] = vol / i_vol
    S["tps"] = dict(vitp=vitp, vitn=vitn, hys=hys, hacc=hacc, i_s=i_s, i_s_hi=i_s_hi, rcts=rcts, k5=k5, k6=k6, vol=vol, i_vol=i_vol)
    ov_rel = (vitp[0] - hys * (1 + hacc) * vitp[2], vitp[2] - hys * (1 - hacc) * vitp[0])     # OV release (VITP - VHYS)
    uv_rel = (vitn[0] + hys * (1 - hacc) * vitn[0], vitn[2] + hys * (1 + hacc) * vitn[2])     # UV release (VITN + VHYS)
    S["ov_rel"], S["uv_rel"] = ov_rel, uv_rel
    L = lambda key, pat, what: find(key, pat, what, layout=True)[1]
    m = L("ao3401", r"VGS\(th\)\s+Gate Threshold Voltage\s+VDS=VGS ID=-250mA\s+-([\d.]+)\s+-([\d.]+)\s+-([\d.]+)\s+V", "the AO3401A's threshold")
    S["p_vth"] = (f(m, 1), f(m, 3))
    S["p_vgs"] = f(L("ao3401", r"Gate-Source Voltage\s+VGS\s+±(\d+)\s+V", "the AO3401A's VGS"))
    S["p_vds"] = f(L("ao3401", r"Drain-Source Voltage\s+VDS\s+-(\d+)\s+V", "the AO3401A's VDS"))
    S["p_idm"] = f(L("ao3401", r"Pulsed Drain Current\s+IDM\s+-(\d+)", "the AO3401A's IDM"))
    m = L("ao3401", r"VDS=-30V, VGS=0V\s+-(\d+)\s+IDSS\s+Zero Gate Voltage Drain Current\s+mA\s+TJ=55°C\s+-(\d+)", "the AO3401A's IDSS")
    S["p_idss"] = (f(m, 1) * 1e-6, f(m, 2) * 1e-6)                # uA: the sheet's micro sign prints as "m" in its text layer (its ID=-250mA row is 250 uA too)
    S["p_ciss"] = f(L("ao3401", r"Ciss\s+Input Capacitance\s+(\d+)\s+pF", "the AO3401A's Ciss")) * 1e-12
    m = L("n4148w", r"at IF = 1 mA\s+-\s+([\d.]+)\s+at IF = 10 mA\s+VF\s+-\s+([\d.]+)\s+V\s+at IF = 50 mA\s+-\s+([\d.]+)\s+at IF = 150 mA\s+-\s+([\d.]+)", "1N4148W's VF")
    S["vf"] = (f(m, 1), f(m, 2), f(m, 3), f(m, 4))
    m = L("n4148w", r"at VR = 20 V\s+IR\s+-\s+(\d+)\s+nA\s+at VR = 75 V, TJ = 150℃\s+-\s+(\d+)\s+µA\s+at VR = 25 V, TJ = 150℃\s+-\s+(\d+)\s+µA", "1N4148W's IR")
    S["ir"] = (f(m, 1) * 1e-9, f(m, 3) * 1e-6)
    m = L("n4148w", r"at t = 1 s\s+([\d.]+)\s+at t = 1 ms\s+IFSM\s+(\d+)\s+A\s+at t = 1 μs\s+(\d+)", "1N4148W's surge")
    S["ifsm"] = (f(m, 1), f(m, 2), f(m, 3))
    nn = flat("".join(pdf_pages("n2n7002")))
    S["n_id"] = f(need(nn, r"Continuous Drain Current ID ([\d.]+) A", "the 2N7002's ID"))
    S["n_vds"] = f(need(nn, r"Drain-Source Voltage VDS (\d+) V", "the 2N7002's VDS"))
    S["n_rds5"] = f(need(nn, r"VGS=5 V, ID=50mA ([\d.]+) (\d+)", "the 2N7002's RDS(on) at 5 V"), 2)
    S["n_ciss"] = f(L("n2n7002", r"Input Capacitance \*\s+Ciss\s+(\d+)", "the 2N7002's Ciss")) * 1e-12
    S["n_igss"] = f(need(nn, r"VGS=±20 V ±(\d+) nA", "the 2N7002's IGSS")) * 1e-9
    m = L("bzt52c", r"BZT52C12\s+WH\s+12\s+11\.4\s+12\.7\s+5\s+25\s+150\s+1\.0\s+([\d.]+)\s+([\d.]+)", "the BZT52C12's leakage")
    S["z_ir"], S["z_ir_v"] = f(m, 1) * 1e-6, f(m, 2)
    yr = "\n".join(pdf_pages("yageo_rc", True))
    need(yr, r"1/4 W\s+-55℃ to 155℃", "RC1206's rating")
    S["r1206"] = (0.25, 70.0, 155.0)      # W, C, C: the rated power to its knee, then linear to 155 C (Yageo's derating figure; the knee read as 70 C)
    vb_lo, vb_hi = H["floor"], S9["vbat_clamp"]
    t_hot = S9["t0"] + R10_T_SMALL
    S["t_hot"] = t_hot
    # ---- the loop with board A's loads: OUT and RET by nodal analysis (R106 on board P at +-1 %, R107 22 kOhm)
    k_lo = R10_OUT[1] * (1 - R10_OUT_TOL) / (R10_OUT[0] * (1 + R10_OUT_TOL) + R10_OUT[1] * (1 - R10_OUT_TOL))
    k_hi = R10_OUT[1] * (1 + R10_OUT_TOL) / (R10_OUT[0] * (1 - R10_OUT_TOL) + R10_OUT[1] * (1 + R10_OUT_TOL))
    r_oload = R10_OUT[0] + R10_OUT[1]
    rth_o = R10_OUT[0] * R10_OUT[1] / r_oload
    def loop(vin, rt1, held=None, i_ret=0.0, rfeed=r_feed):
        go = 1 / rfeed + 1 / r_oload
        if held is not None:          # the return held at `held`
            vout = (vin / rfeed + held / rt1) / (go + 1 / rt1)
            return vout, held
        # two nodes: OUT (R106 from VIN, RT1 to RET, the divider to ground) and RET (RT1 from OUT, R107 to ground, i_ret drawn)
        a11, a12, b1 = go + 1 / rt1, -1 / rt1, vin / rfeed
        a21, a22, b2 = -1 / rt1, 1 / rt1 + 1 / r_ret, -i_ret
        det = a11 * a22 - a12 * a21
        return (b1 * a22 - a12 * b2) / det, (a11 * b2 - a21 * b1) / det
    S["loop"] = loop
    S["out_held"] = [(vin, loop(vin, S9["rt1"][0], S["held"], rfeed=r_feed * 1.01)[0]) for vin in (7.6, 10.6, 16.8)]
    S["out_rel"] = ((uv_rel[0] - i_s * rth_o) / k_hi, (uv_rel[1] + i_s * rth_o) / k_lo)       # the loop read powered over (rising)
    S["out_ast"] = ((vitn[0] - i_s * rth_o) / k_hi, (vitn[2] + i_s * rth_o) / k_lo)           # the loop read unpowered under (falling)
    S["out_k"] = (k_lo, k_hi)
    i_ret = i_s_hi
    S["ret_low"] = ov_rel[0] - i_ret * 50.0          # the return read held under (falling); the held node's source 50 ohm at most (2 x 7 x 2 hot, l8p)
    S["ret_high"] = vitp[2] + i_ret * 16e3           # the return read closed over (rising); the closed node's Thevenin under 16 kOhm
    S["ret_low_margin"] = S["ret_low"] - S["held"]
    out_b, ret_b = loop(S9["pack_lo"], S9["rt1"][2], i_ret=i_ret)
    out_0, ret_0 = loop(S9["pack_lo"], S9["rt1"][2], i_ret=0.0)
    S["bound"] = (S9["ret_bound"][0], ret_b, out_b)
    S["bound_margin"] = ret_b - S["ret_high"]
    # the window: a closed loop ramping (a docking, the gauge's wake, a back-fed precharge) reads held only if OUT is read powered while RET
    # is still under the closed reading, RET/OUT = 22 / (22 + RT1): none for RT1 up to this bound
    r_need = S["ret_high"] / S["out_rel"][0]
    S["window_rt1"] = r_ret * (1 / r_need - 1)
    # the interface's literal box (RET under 1.0 V with OUT at 2.0 V or over) reached by a closed loop: RT1 over 22 kOhm
    S["box_rt1"] = r_ret * (S["if_out"] / S["if_ret_lo"] - 1)
    S["box_vin"] = [(rt, S["if_ret_lo"] * (r_feed + rt + r_ret) / r_ret) for rt in (30e3, S9["rt1"][2])]
    ldo_vin = (5.7 - 1.0)
    S["ldo_vin"] = ldo_vin
    S["ldo_ret"] = ldo_vin * r_ret / (r_feed + S9["rt1"][1] * 1.5 + r_ret)        # RT1 at its printed 25 C most, 15 kOhm
    S["ldo_rt1_max"] = r_ret * (ldo_vin / S["ret_high"]) - r_feed - r_ret
    S["guard_rt1"] = [(vin, vin * r_ret / S["ret_low"] - r_feed - r_ret) for vin in (S9["pack_lo"], S9["vpk"])]   # board A reads held past these
    S["inv_rt1"] = [(vin, vin * r_ret / 2.5 - r_feed - r_ret, vin * r_ret / 1.0 - r_feed - r_ret) for vin in (S9["pack_lo"], S9["vpk"])]
    # ---- the trigger's set (from the return falling) and its parts
    tctr_open = S9["tctr_open"]
    vc_lo = 8.0                                          # DD7_VC at its least: the zener leaks under 0.1 uA at 8 V (ten times hot through R233)
    vlp = vc_lo * R10_RPU[1] / (R10_RPU[0] + R10_RPU[1])
    tau_t = R10_RPU[1] * R10_C_T
    S["t_trig"] = tau_t * math.log(vc_lo / (vc_lo - S9["vth"][2]))
    rag = R10_RAG[0] * R10_RAG[1] / (R10_RAG[0] + R10_RAG[1])
    vgs_a = vb_lo * R10_RAG[0] / (R10_RAG[0] + R10_RAG[1])
    tau_g = rag * S["p_ciss"] * R10_CISS_X
    S["t_qa"] = tau_g * math.log(vgs_a / (vgs_a - S["p_vth"][1]))
    c_hi = R10_CH * (1 + R10_CH_TOL[0]) * (1 + R10_CH_TOL[1])
    c_lo = R10_CH * (1 - R10_CH_TOL[0]) * (1 - R10_CH_TOL[1]) * (1 - R10_CH_BIAS)
    S["c_h"] = (c_lo, c_hi)
    S["tau_arm"] = R10_RA * 1.01 * c_hi
    S["arm_peak"] = (vb_hi - S["vf"][0]) / (R10_RA * 0.99)
    S["arm_peak_168"] = (S9["vpk"] - S["vf"][0]) / (R10_RA * 0.99)
    S["arm_i2t"] = S["arm_peak"] ** 2 * S["tau_arm"] / 2
    S["t_cross"] = S["tau_arm"] * math.log((vb_lo - S["vf"][3]) / (vb_lo - S["vf"][3] - vitp[2]))
    c_cts = (R10_CTS * (1 - R10_CTS_TOL), R10_CTS * (1 + R10_CTS_TOL))
    S["tcts1"] = (-math.log(k5) * rcts[0] * c_cts[0], -math.log(k6) * rcts[2] * c_cts[1] + S9["tcts"][1])
    rinh = 100e3 * 200e3 / 300e3
    vgs_i = (vb_lo - vol) * 100e3 / 300e3
    S["t_q49"] = rinh * S["p_ciss"] * R10_CISS_X * math.log(vgs_i / (vgs_i - S["p_vth"][1]))
    S["t_set"] = tctr_open + S["t_trig"] + S["t_qa"] + S["t_cross"] + S["tcts1"][1] + 1e-6 + S["t_q49"] + 1e-6
    S["t_set_min"] = S["tcts1"][0]
    S["arm_frac"] = 1 - math.exp(-S["t_set_min"] / S["tau_arm"])
    S["v0"] = (vb_lo - S["vf"][1]) * S["arm_frac"]           # the hold's start at its least: VSYS_MIN less D26 at 10 mA, the arm's fraction
    S["v0_hi"] = vb_hi
    S["charge_end"] = S["pull_t"] + S["t_set"]
    # ---- the hold: DD7_H from V0 through R85 to U47's OV release, against every sink on the node
    def ir_diode(t):          # 1N4148W reverse leakage, log-linear between the sheet's 25 C (20 V) and 150 C (25 V) rows: INFERRED
        return S["ir"][0] * (S["ir"][1] / S["ir"][0]) ** ((t - 25.0) / 125.0)
    S["ir_hot"] = ir_diode(t_hot)
    i_cap = vb_hi / (R10_CH_IR / R10_CH)
    S["i_x"] = (S["ir_hot"] + i_s, S["ir_hot"], i_s, i_cap)
    rh_lo, rh_hi = R10_RH * (1 - R10_RH_TOL), R10_RH * (1 + R10_RH_TOL)
    def hold(v0, vrel, ix, r, c):
        return r * c * math.log((v0 + ix * r) / (vrel + ix * r))
    ixm = S["i_x"][0] + i_cap
    S["hold_min"] = hold(S["v0"], ov_rel[1], ixm, rh_lo, c_lo)
    S["hold_max"] = hold(S["v0_hi"], ov_rel[0], -i_s, rh_hi, c_hi) + tctr_open
    lo, hi_ = 1.0, 200.0
    for _ in range(80):
        mid = (lo + hi_) / 2
        if hold(S["v0"], ov_rel[1], S["ir_hot"] * mid + i_s + i_cap, rh_lo, c_lo) > S["if_hold"]:
            lo = mid
        else:
            hi_ = mid
    S["leak_x"] = lo                # the factor on D26's inferred hot leakage at which the hold falls to 1.0 s
    S["hold_margin"] = S["hold_min"] - S["if_hold"]
    S["hold_vs_restart"] = S["hold_min"] - S["restart"]
    idss_hot = S["p_idss"][1] * 2 ** ((t_hot - 55.0) / 10.0)       # INFERRED: the 55 C row doubled every 10 K
    S["k_rest"] = (idss_hot, idss_hot * R10_RK)
    S["rest_margin"] = ov_rel[0] - S["k_rest"][1]
    # ---- the release on CELL+ alive (U47 channel 2), the latch and the bleeder (L8P-F05)
    a_, b_ = R10_CS
    kc_lo = b_ * (1 - R10_CS_TOL) / (a_ * (1 + R10_CS_TOL) + b_ * (1 - R10_CS_TOL))
    kc_hi = b_ * (1 + R10_CS_TOL) / (a_ * (1 - R10_CS_TOL) + b_ * (1 + R10_CS_TOL))
    rth_c = a_ * b_ / (a_ + b_)
    S["cs_k"] = (kc_lo, kc_hi)
    i_n = lambda vcell: vcell / R10_RBL + vb_hi / 300e3 + 12.7 / R10_RPU[2] + vcell / (a_ + b_) + 12.7 / R10_RPU[3]
    def dead_at(vref):          # CELL+ under which channel 2 asserts (dead) with the foot at vref, at its least
        return (vitn[0] - i_s * rth_c - (1 - kc_hi) * vref) / kc_hi
    v_ref = S["vol_r"] * i_n(dead_at(0.0))
    for _ in range(5):
        v_ref = S["vol_r"] * i_n(dead_at(v_ref))
    S["latch_vref"] = v_ref
    S["dead"] = dead_at(v_ref)
    S["alive"] = (uv_rel[1] + i_s * rth_c) / kc_lo                # CELL+ over which channel 2 releases (alive), at its most (the foot at 0 V)
    S["isrc_max"] = (S["dead"] - v_ref) / (R10_RBL * 1.01)        # the most current anything may push into CELL+ while the latch still reads dead
    S["rint_min"] = [(vin, vin / S["isrc_max"]) for vin in (S["f05"]["vin"], vb_hi)]
    S["known_src"] = [(vin, vin / S["r_int"] + 3 * S9["idss"]) for vin in (S["f05"]["vin"], vb_hi)]
    S["latch_cell"] = [(vin, v_ref + (vin / S["r_int"] + 3 * S9["idss"]) * R10_RBL * 1.01) for vin in (S["f05"]["vin"], vb_hi)]
    S["fet_idss_allow"] = (S["isrc_max"] - vb_hi / S["r_int"]) / 3
    vs_max = 17.375                                               # VSYS's top (the record's system node, 9.688 to 17.375 V)
    S["vs_max"] = vs_max
    c_cell = S9["start"]["cout"] - S9["start"]["c_vsys"]
    S["c_cell"] = c_cell
    S["bleed_t"] = R10_RBL * 1.01 * c_cell * 1.2 * math.log(vs_max / S["dead"])
    S["bleed_w"] = ((S9["vpk"] - v_ref) ** 2 / R10_RBL, (vb_hi - v_ref) ** 2 / R10_RBL)
    S["r1206_hot"] = S["r1206"][0] * (S["r1206"][2] - t_hot) / (S["r1206"][2] - S["r1206"][1])
    S["n_sink"] = (i_n(S9["vpk"]), i_n(vb_hi))
    S["start_room"] = S9["if1_room"]
    S["bleed_start"] = S9["vpk"] / R10_RBL
    # round 9's readings, the failure reproduced on the same cases
    S["r9_out_gate"] = [(vin, o / 2.0) for vin, o in S["out_held"]]
    # ---- the parts within their limits
    S["vgs_n_max"] = 12.7
    S["vgs_p"] = (vb_lo * R10_RAG[0] / (R10_RAG[0] + R10_RAG[1]), vb_hi * R10_RAG[0] * 1.01 / (R10_RAG[0] * 1.01 + R10_RAG[1] * 0.99))
    S["z_i"] = (vb_hi - S9["vz"][0]) / (R10_RVC * 0.99)
    S["z_w"] = S["z_i"] * S9["vz"][1]
    S["ra_w"] = 0.5 * c_hi * vb_hi ** 2
    S["ra_pk"] = (vb_hi - S["vf"][0]) ** 2 / (R10_RA * 0.99)
    S["ra_pk_168"] = (S9["vpk"] - S["vf"][0]) ** 2 / (R10_RA * 0.99)
    need(yr, r"2\.5 times RCWV or maximum overload voltage\s+[^\n]*\n\s*Overload\s+which is less for 5 seconds", "RC's short-time overload")
    S["ra_sto"] = (2.5 * math.sqrt(S["r1206"][0] * R10_RA)) ** 2 / R10_RA * 5.0
    # ---- IF-1's static draw restated with round 10's parts (round 9's 19f table, its R107 and R108 row replaced)
    vb = S9["vpk"]
    S["static_add"] = [("U47 and U48 TPS37A, two (IDD at 800 mV)", 2 * S9["static"][3][1], "MAKER"),
                       ("R233 into D27 (DD7_VC), its bound VBAT / R233", vb / R10_RVC, "SESSION"),
                       ("Q51's off leakage into R253 (the 55 C row)", S["p_idss"][1], "MAKER"),
                       ("R107 and R108 on CELL+ into DD7_VC through R254 (bound: CELL+ over the three)", vb / (a_ + b_ + R10_RPU[3]), "SESSION")]
    S["static_drop"] = vb / 200e3
    S["static_sum"] = S9["static_sum"] - S["static_drop"] + sum(x for _l, x, _c in S["static_add"])
    S["static_frac"] = S["static_sum"] / S9["if1_room"]
    # ---- T2, recorded now: E-1's even split (record l9stk 15.5) against an uneven one
    S["t2"] = R10_T2
    S["t2_tj"] = S9["t0"] + S9["band"] + (S9["budget"] - S9["r17_allow"] * S9["pr17"]) * R10_T2 + S9["r17_allow"] * S9["pr17"]
    return S


def render_fix20(R, p):
    S, S9, H = R["S20"], R["S19"], R["H"]
    T = S["tps"]
    p("20. ROUND 10: BOARD A'S SIDE OF THE BREAKER'S LATCH AGAINST RECORD l8p'S ROUTE R1 (L8P-F04, L8P-F05; record l8p at %s, 4 October 2026)" % R9_COMMITS["l8p2"][:8])
    p("   20a. THE FAILURE CASES (C-PROT), REPRODUCED ON ROUND 9'S DRAFT (RECORD, l8p; INFERRED)")
    p("     L8P-F04: with the return held at %s V, DOCK_EN_OUT %s V at BRK_VIN 7.6 V and %s V at 10.6 V (record l8p); round 9's Q47 read half of it,"
      % (fmt(S["held"], 3), fmt(S["f04"][0] * 2, 2), fmt(S["f04"][1] * 2, 2)))
    p("       %s and %s V against the 2N7002's %s V: the inhibit did not set with the return held" % (fmt(S["f04"][0], 2), fmt(S["f04"][1], 2), fmt(S["f04"][2], 1)))
    p("     L8P-F05: with the breaker off the LM5069's internal %s MOhm holds CELL+ at %s V at BRK_VIN %s V against board A's %s kOhm (%s V with"
      % (fmt(S["r_int"] / 1e6, 0), fmt(S["f05"]["v"], 2), fmt(S["f05"]["vin"], 1), fmt(S["f05"]["r_a"] / 1e3, 0), fmt(S["f05"]["v_u104"], 2)))
    p("       U104's %s kOhm, %s V at the 29.2 V clamp), over round 9's %s V dead point: the inhibit could release with the breaker off"
      % (fmt(S["u104"] / 1e3, 1), fmt(S["f05"]["v_clamp"], 2), fmt(S["f05"]["dead"], 2)))
    p("   20b. THE REDRAWN CIRCUIT (SESSION, apply_gen_sch_a_dd7.py; the makers' figures: TI SNVSBJ1E, AOS AO3401A, ST/Semtech 1N4148W, JSCJ 2N7002,")
    p("     Diodes DS18004)")
    p("     U48 TPS37A010122 on VBAT: SENSE1 (OV) on DOCK_EN_RET directly; SENSE2 (UV) on DOCK_EN_OUT over R109 562k / R144 422k (0.1 %); RESET1 is")
    p("       DD7_T, pulled up from RESET2 (DD7_LP) through R250: DD7_T high = the return held AND the loop powered (the trigger)")
    p("     the arm: Q50 (2N7002, gate DD7_T) turns Q51 (AO3401A) on through R251 100k / R252 200k; Q51 charges DD7_H from VBAT through R84 56R and")
    p("       D26 (1N4148W); R253 10k bleeds Q51's off leakage; C241 1 uF 100 V X7R and R85 1.2 MOhm hold DD7_H")
    p("     U47 TPS37A010122 on VBAT: SENSE1 (OV) on DD7_H, CTS1 on C248 3.9 nF C0G (the set delay); SENSE2 (UV) on CELL+ over R107 464k / R108 100k,")
    p("       the divider's foot DD7_REF on Q52 to DD7_N while the loop is powered, else lifted by R254; RESET1 and RESET2 on DD7_N (the inhibit asked)")
    p("     the inhibit: Q47 (gate DD7_LP) passes DD7_N to SYS_INH_D, Q49 holds CH_BATDRV at VBAT (R82 / R83 as round 9); the bleeder Q48 (gate DD7_LP)")
    p("       loads CELL+ with R256 4.7k into DD7_N; Q46's gate moves to DD7_N; DD7_VC is VBAT through R233 100k under D27 (BZT52C12)")
    p("   20c. THE THRESHOLDS AND THEIR TOLERANCES (MAKER: VITP and VITN %s / %s / %s V, hysteresis %s %% +-%s %%, ISENSE %s nA at 800 mV, %s uA"
      % (fmt(T["vitp"][0], 3), fmt(T["vitp"][1], 3), fmt(T["vitp"][2], 3), fmt(T["hys"] * 100, 0), fmt(T["hacc"] * 100, 1), fmt(T["i_s"] * 1e9, 0), fmt(T["i_s_hi"] * 1e6, 0)))
    p("     its largest row; resistors at their tolerances, each at its worst sign; INFERRED)")
    p("     the return (U48 channel 1): read held under %s V at least, closed over %s V at most (OV release %s to %s V, assert under %s V); board"
      % (fmt(S["ret_low"], 4), fmt(S["ret_high"], 4), fmt(S["ov_rel"][0], 4), fmt(S["ov_rel"][1], 4), fmt(T["vitp"][2], 3)))
    p("       P's pull holds %s V: %s V of margin; its load on DOCK_EN_RET is SENSE1 alone, at most %s uA (over %s MOhm at the 17.4 V clamp of the"
      % (fmt(S["held"], 3), fmt(S["ret_low_margin"], 3), fmt(T["i_s_hi"] * 1e6, 0), fmt(17.4 / T["i_s_hi"] / 1e6, 1)))
    p("       return), against the interface's 1 MOhm or more")
    p("     the loop (U48 channel 2): read powered over %s V at most (%s V at least), unpowered under %s V at least (UV release %s to %s V, R109 / R144"
      % (fmt(S["out_rel"][1], 3), fmt(S["out_rel"][0], 3), fmt(S["out_ast"][0], 3), fmt(S["uv_rel"][0], 4), fmt(S["uv_rel"][1], 4)))
    p("       %s to %s, ISENSE through %s kOhm); with the return held, DOCK_EN_OUT (RT1 at %s kOhm, R106 +1 %%, board A's %s kOhm on it):"
      % (fmt(S["out_k"][0], 5), fmt(S["out_k"][1], 5), fmt(R10_OUT[0] * R10_OUT[1] / (R10_OUT[0] + R10_OUT[1]) / 1e3, 1), fmt(S9["rt1"][0] / 1e3, 0),
         fmt((R10_OUT[0] + R10_OUT[1]) / 1e3, 0)))
    for vin, o in S["out_held"]:
        p("         BRK_VIN %5s V: %s V, %s V over the powered reading's most (half of it, which round 9's Q47 read, %s V against its 2.5 V)" % (fmt(vin, 1), fmt(o, 3), fmt(o - S["out_rel"][1], 3), fmt(o / 2.0, 2)))
    p("     the interface's literal box (RET under %s V, OUT at %s V or over) holds every state board P produces (the return at %s V); board A reads"
      % (fmt(S["if_ret_lo"], 1), fmt(S["if_out"], 1), fmt(S["held"], 3)))
    p("       the return as held under %s V, not up to %s V, because the box also holds a CLOSED loop: RET/OUT is 22 / (22 + RT1), under 0.5 for RT1"
      % (fmt(S["ret_low"], 3), fmt(S["if_ret_lo"], 1)))
    p("       over %s kOhm, at BRK_VIN under %s V (RT1 30 kOhm) or %s V (RT1 47 kOhm); every ramp of a closed loop (a docking, the gauge's wake, a back-fed"
      % (fmt(S["box_rt1"] / 1e3, 0), fmt(S["box_vin"][0][1], 2), fmt(S["box_vin"][1][1], 2)))
    p("       precharge through the breaker's body diodes) passes through it, and a trigger there stops a dead pack's precharge (SESSION, the reason)")
    p("     no window: a ramping closed loop never reads held while RT1 is under %s kOhm (RET/OUT over %s); RT1 is at most %s kOhm at 25 C and"
      % (fmt(S["window_rt1"] / 1e3, 1), fmt(S["ret_high"] / S["out_rel"][0], 4), fmt(S9["rt1"][1] * 1.5 / 1e3, 0)))
    p("       reaches 100 kOhm only above 110 C (Murata DM-SA16-E056, MAKER); a back-fed precharge carries at most %s A, so the FETs' copper sits at"
      % fmt(S["ldo"], 5))
    p("       the air; the precharge's floor (BRK_VIN %s V, RT1 at 15 kOhm) puts the return at %s V, %s V over the closed reading; it would read"
      % (fmt(S["ldo_vin"], 2), fmt(S["ldo_ret"], 3), fmt(S["ldo_ret"] - S["ret_high"], 3)))
    p("       held there only past RT1 %s kOhm (INFERRED)" % fmt(S["ldo_rt1_max"] / 1e3, 1))
    p("     against board P's guard: board A reads the closed return as held only past RT1 %s kOhm at %s V and %s kOhm at %s V; board P's first"
      % (fmt(S["guard_rt1"][0][1] / 1e3, 0), fmt(S["guard_rt1"][0][0], 1), fmt(S["guard_rt1"][1][1] / 1e3, 0), fmt(S["guard_rt1"][1][0], 1)))
    p("       inverter turns off (RET 2.5 to 1.0 V) from %s to %s kOhm at %s V: board A never reads held before the guard's own trip (INFERRED)"
      % (fmt(S["inv_rt1"][0][1] / 1e3, 1), fmt(S["inv_rt1"][0][2] / 1e3, 1), fmt(S["inv_rt1"][0][0], 1)))
    p("     the loop at %s V and RT1 %s kOhm (record l9stk's former 'bound point'; WITHDRAWN as a bound by round 13, section 23g: 47 kOhm is not a"
      % (fmt(S9["pack_lo"], 1), fmt(S9["rt1"][2] / 1e3, 0)))
    p("       point of this part): the first inverter's gate %s V unloaded (%s V with round 9's 2 MOhm), %s V with round 10's (R109 + R144 on"
      % ("%.3f" % S["bound"][0], "%.3f" % S9["ret_bound"][1], "%.3f" % S["bound"][1]))
    p("       DOCK_EN_OUT, %s uA on the return), against its 2.5 V; board A reads it closed with %s V to spare: board A's loads move the loop's"
      % (fmt(T["i_s_hi"] * 1e6, 0), fmt(S["bound_margin"], 3)))
    p("       levels by %s V there, and no more is claimed of it (INFERRED)" % fmt(S["bound"][0] - S["bound"][1], 3))
    p("     CELL+ (U47 channel 2, read only while an inhibit is asked and the loop is powered): dead under %s V at least, alive over %s V at most"
      % (fmt(S["dead"], 3), fmt(S["alive"], 3)))
    p("       (k %s to %s, the foot at RESET's %s V at its sink, VOL %s mV at %s mA read as %s ohm)"
      % (fmt(S["cs_k"][0], 5), fmt(S["cs_k"][1], 5), fmt(S["latch_vref"], 4), fmt(T["vol"] * 1e3, 0), fmt(T["i_vol"] * 1e3, 0), fmt(S["vol_r"], 0)))
    p("   20d. THE DELAYS (INFERRED; each element's bound named)")
    p("     the set, from the return falling under %s V: U48's release %s us (tCTR, no capacitor, MAKER) + DD7_T to Q50's %s V %s us (R250 1 MOhm into"
      % (fmt(S["ret_low"], 3), fmt(S9["tctr_open"] * 1e6, 0), fmt(S9["vth"][2], 1), fmt(S["t_trig"] * 1e6, 1)))
    p("       %s pF, ASSUMPTION) + Q51 on %s us (R251 || R252 into 1.5 x its typical %s pF) + DD7_H over %s V %s us + CTS1 %s to %s ms (Equations 5 and 6,"
      % (fmt(R10_C_T * 1e12, 0), fmt(S["t_qa"] * 1e6, 1), fmt(S["p_ciss"] * 1e12, 0), fmt(T["vitp"][2], 3), fmt(S["t_cross"] * 1e6, 1),
         fmt(S["tcts1"][0] * 1e3, 3), fmt(S["tcts1"][1] * 1e3, 3)))
    p("       C248 +-5 %%, RCTS %s to %s kOhm) + Q49 on %s us: at most %s ms, under the interface's 1 ms" % (fmt(T["rcts"][0] / 1e3, 0), fmt(T["rcts"][2] / 1e3, 0),
      fmt(S["t_q49"] * 1e6, 1), fmt(S["t_set"] * 1e3, 3)))
    p("     the arm completes before the set: the set comes at least %s ms after DD7_H passes %s V, while board P's pull holds the trigger (the"
      % (fmt(S["t_set_min"] * 1e3, 3), fmt(T["vitp"][2], 3)))
    p("       charge flows until the inhibit stops it); the arm's time constant at most %s us (R84 into C241's %s uF most): %s of the way, so the hold"
      % (fmt(S["tau_arm"] * 1e6, 1), fmt(S["c_h"][1] * 1e6, 3), "%.5f" % S["arm_frac"]))
    p("       starts from at least %s V (VSYS_MIN's %s V less D26's %s V at 10 mA)" % (fmt(S["v0"], 3), fmt(H["floor"], 3), fmt(S["vf"][1], 3)))
    p("     the charge through the off breaker ends within %s ms of passing the threshold (board P's pull %s ms and board A's set), against E-14's 10 ms"
      % (fmt(S["charge_end"] * 1e3, 3), fmt(S["pull_t"] * 1e3, 2)))
    p("     the hold: DD7_H from %s V through R85 (1 %%) and C241 (%s uF least: K, X7R's 15 %% and 15 %% DC bias, ASSUMPTION) to U47's OV release, %s V"
      % (fmt(S["v0"], 3), fmt(S["c_h"][0] * 1e6, 4), fmt(S["ov_rel"][1], 4)))
    p("       at most, against every sink on the node: D26's reverse leakage %s uA at %s C (INFERRED: log-linear between the sheet's %s nA at 25 C and %s uA"
      % (fmt(S["ir_hot"] * 1e6, 3), fmt(S["t_hot"], 2), fmt(S["ir"][0] * 1e9, 0), fmt(S["ir"][1] * 1e6, 0)))
    p("       at 150 C), SENSE1's %s nA (MAKER), C241's insulation %s uA (ASSUMPTION): at least %s s after the return rises, %s s over the interface's"
      % (fmt(T["i_s"] * 1e9, 0), fmt(S["i_x"][3] * 1e6, 3), fmt(S["hold_min"], 3), fmt(S["hold_margin"], 3)))
    p("       %s s and %s s over the breaker's restart (%s s, record l8p); at most %s s (the clamp's VBAT, the sinks reversed); the hold reaches 1.0 s with"
      % (fmt(S["if_hold"], 1), fmt(S["hold_vs_restart"], 3), fmt(S["restart"], 4), fmt(S["hold_max"], 2)))
    p("       D26's leakage %s times the inferred figure" % fmt(S["leak_x"], 2))
    p("     the hold always ends: Q51's off leakage %s uA at %s C (the 55 C row doubled every 10 K, INFERRED) into R253 holds DD7_K at %s V, under the"
      % (fmt(S["k_rest"][0] * 1e6, 1), fmt(S["t_hot"], 2), fmt(S["k_rest"][1], 3)))
    p("       OV release's least %s V by %s V" % (fmt(S["ov_rel"][0], 4), fmt(S["rest_margin"], 3)))
    p("   20e. L8P-F05 CORRECTED: THE RELEASE ON CELL+ ALIVE (INFERRED)")
    p("     a dead CELL+ never sets the inhibit (U47's channel 2 reads alive while R254 lifts its foot, i.e. while no inhibit is asked); it keeps one")
    p("       that is set, and Q48 then loads CELL+ through R256 into DD7_N, so CELL+ reads alive only when the breaker drives it")
    p("     the latch reads dead while every source into CELL+ stays under %s mA (CELL+ under %s V less the foot's %s V, through R256 at +1 %%):"
      % (fmt(S["isrc_max"] * 1e3, 3), fmt(S["dead"], 3), fmt(S["latch_vref"], 4)))
    for (vin, rmin), (_v, ks), (_v2, vc) in zip(S["rint_min"], S["known_src"], S["latch_cell"]):
        p("         BRK_VIN %4s V: the LM5069's internal resistor may be as low as %s kOhm (%s of its 1 MOhm); at 1 MOhm with the three FETs' %s uA"
          % (fmt(vin, 1), fmt(rmin / 1e3, 1), "%.3f" % (rmin / S["r_int"]), fmt(3 * S9["idss"] * 1e6, 0)))
        p("           (25 C) CELL+ sits at %s V, %s V under the dead reading (was %s V against %s V)" % (fmt(vc, 3), fmt(S["dead"] - vc, 3),
          fmt(S["f05"]["v"] if vin < 20 else S["f05"]["v_clamp"], 2), fmt(S["f05"]["dead"], 2)))
    S22 = R["S22"]
    p("       the battery FETs' off leakage (Nexperia prints at most %s uA each at 25 C and %s uA at Tj 125 C, nothing over 125 C: MAKER) may reach"
      % (fmt(S22["bat"][0] / 3 * 1e6, 0), fmt(S22["bat"][1] / 3 * 1e6, 0)))
    p("       %s uA each before this static limit; the breaker pair's leakage enters CELL+ too (record l8p's L8P-F06): section 22b counts all five"
      % fmt(S["fet_idss_allow"] * 1e6, 0))
    p("     by the hold's end CELL+ has fallen under the dead reading unless the breaker drives it: from VSYS's %s V through R256 into CELL_FUSED's %s uF"
      % (fmt(S["vs_max"], 3), fmt(S["c_cell"] * 1e6, 0)))
    p("       (+20 %%, ASSUMPTION) within %s s with the sources at their hot bound (%s uA, section 22b), inside the hold's least %s s while the"
      % (fmt(S22["sel"]["t_hot"], 3), fmt(S22["src"]["hot"] * 1e6, 1), fmt(S["hold_min"], 3)))
    p("       sources total under %s uA (the coupled limit, round 12; %s s is the figure with no source, which rounds 10 and 11 printed alone)"
      % (fmt(S22["sel"]["lim"] * 1e6, 1), fmt(S["bleed_t"], 3)))
    p("     the release: the breaker's restart drives CELL+ over %s V against R256's %s mA at %s V, inside IF-1's %s A room"
      % (fmt(S["alive"], 3), fmt(S["bleed_start"] * 1e3, 2), fmt(S9["vpk"], 1), fmt(S["start_room"], 2)))
    p("   20f. THE SERVICE UNTOUCHED (INFERRED)")
    p("     10 A held, 18 A for 60 s and every current-limit excursion: while the breaker is on, board A reads the return closed for any RT1 under"
      % ())
    p("       %s kOhm at the pack's %s V (%s kOhm at %s V), past the guard's own trip (20c): %s V at RT1 %s kOhm, which bounds nothing (round 13, 23g:"
      % (fmt(S["guard_rt1"][0][1] / 1e3, 0), fmt(S9["pack_lo"], 1), fmt(S["guard_rt1"][1][1] / 1e3, 0), fmt(S["guard_rt1"][1][0], 1), fmt(S["bound"][1], 3),
         fmt(S9["rt1"][2] / 1e3, 0)))
    p("       whether the guard itself stays closed in the service is not printed, record l8p's L8P-F07); board P's detector never pulls a running")
    p("       breaker (record l8p 12e): no trigger, no hold, no request;")
    p("       Q47, Q48 and Q52 idle; Q46 blocks the input-return pulse (DD7_N high): no board A part acts on a running breaker or its loop")
    p("     the precharge and the gauge's wake (a closed loop back-fed through the body diodes): never read held while RT1 is under %s kOhm; CELL+ never"
      % fmt(S["window_rt1"] / 1e3, 1))
    p("       sets the inhibit: a dead pack's precharge passes (round 9's inhibit set on CELL+ under its dead point whenever the loop read powered,")
    p("       which a back-fed precharge reaches on the way up: at its threshold corners it could stop the precharge; withdrawn)")
    p("     a docking: OUT and RET rise together at RET/OUT of %s or more (RT1 under %s kOhm): no trigger; with no source board A is unpowered until"
      % (fmt(S["ret_high"] / S["out_rel"][0], 4), fmt(S["window_rt1"] / 1e3, 1)))
    p("       the breaker's start feeds VBAT, and at power-up U47 and U48 hold their outputs asserted for tSD, %s ms at most (the inhibit at most"
      % fmt(S9["tsd"] * 1e3, 0))
    p("       that long, then on CELL+ as read)")
    p("   20g. THE PARTS WITHIN THEIR LIMITS (MAKER limits; INFERRED readings)")
    p("     U47, U48: VDD %s to %s V against VBAT %s to %s V; SENSE and RESET 65 V graded against %s V; RESET sinks at most %s mA (the breaker restarted, %s V)"
      % (fmt(S9["vdd"][0], 1), fmt(S9["vdd"][1], 0), fmt(H["floor"], 3), fmt(S9["vbat_clamp"], 1), fmt(S9["vbat_clamp"], 1), fmt(R["S22"]["sel"]["sink"]["run"] * 1e3, 2), fmt(S9["vpk"], 1)))
    p("       and %s mA with CELL+ following VBAT at SYSOVP (R256 at -1 %%), against VOL's %s mA row and TI's recommended %s mA at most; %s mA only"
      % (fmt(R["S22"]["sel"]["sink"]["ovp"] * 1e3, 2), fmt(T["i_vol"] * 1e3, 0), fmt(S["i_rec"] * 1e3, 0), fmt(R["S22"]["sel"]["sink"]["clamp"] * 1e3, 2)))
    p("       with CELL+ at the 29.2 V clamp, under the absolute %s mA: a state that needs a second fault (V1's minor; the states in section 22d)"
      % fmt(R["S22"]["i_abs"] * 1e3, 0))
    p("     2N7002 (Q44 to Q48, Q50, Q52): VGS at most %s V (DD7_VC) against %s V; VDS at most %s V against %s V; currents at most %s mA against %s A"
      % (fmt(S["vgs_n_max"], 1), fmt(S9["vgs_max"], 0), fmt(S9["vbat_clamp"], 1), fmt(S["n_vds"], 0), fmt(R["S22"]["sel"]["sink"]["clamp"] * 1e3, 2), fmt(S["n_id"], 3)))
    p("     AO3401A (Q49, Q51): VGS %s to %s V against +-%s V; VDS %s V against %s V; Q51's arm peak %s A (%s A at %s V) against IDM %s A"
      % (fmt(S["vgs_p"][0], 2), fmt(S["vgs_p"][1], 2), fmt(S["p_vgs"], 0), fmt(S9["vbat_clamp"], 1), fmt(S["p_vds"], 0), fmt(S["arm_peak"], 3),
         fmt(S["arm_peak_168"], 3), fmt(S9["vpk"], 1), fmt(S["p_idm"], 0)))
    p("     D26 (1N4148W): the arm's peak %s A decaying in %s us, I2t %s A2s, against its surge rows %s A for 1 us and %s A for 1 ms (I2t %s A2s);"
      % (fmt(S["arm_peak"], 3), fmt(S["tau_arm"] * 1e6, 1), "%.2e" % S["arm_i2t"], fmt(S["ifsm"][2], 0), fmt(S["ifsm"][1], 0), "%.0e" % (S["ifsm"][1] ** 2 * 1e-3)))
    p("       at most once a hold, so at least 1.0 s apart")
    p("     R84 (56R 1206): the arm's %s mJ at the clamp, %s W peak decaying in %s us (%s W at %s V): no held sheet prints a pulse rating for it"
      % (fmt(S["ra_w"] * 1e3, 3), fmt(S["ra_pk"], 1), fmt(S["tau_arm"] * 1e6, 1), fmt(S["ra_pk_168"], 1), fmt(S9["vpk"], 1)))
    p("       (Yageo's short-time overload is a 5 s test, no basis for a 71 us pulse: V1's minor, the comparison withdrawn); R84 is SPECIFIED as a")
    p("       pulse-rated part whose maker prints a single-pulse curve covering %s W for %s us once a second, its code owed to Layer 6 (CONDITIONAL)"
      % (fmt(S["ra_pk"], 1), fmt(S["tau_arm"] * 1e6, 0)))
    p("     R256 (4.7k 1206; 6.8k in round 11 only, section 22): %s W at %s V while the inhibit holds after a restart," % (fmt(S["bleed_w"][0], 4), fmt(S9["vpk"], 1)))
    p("       %s W at the 29.2 V clamp, against RC1206's %s W derated to %s W at %s C (Yageo, the knee read as 70 C)"
      % (fmt(S["bleed_w"][1], 4), fmt(S["r1206"][0], 2), fmt(S["r1206_hot"], 3), fmt(S["t_hot"], 2)))
    p("     D27 (BZT52C12): at most %s mA, %s mW, from the 29.2 V clamp through R233" % (fmt(S["z_i"] * 1e3, 3), fmt(S["z_w"] * 1e3, 2)))
    p("   20h. IF-1'S STATIC DRAW RESTATED (19f's table; R107 and R108's %s mA row replaced)" % fmt(S["static_drop"] * 1e3, 4))
    for lab, x, cl in S["static_add"]:
        p("     %s: %s mA (%s)" % (lab, fmt(x * 1e3, 4), cl))
    p("     in all %s mA, %s %% of the %s A room (round 9's %s mA)" % (fmt(S["static_sum"] * 1e3, 2), fmt(S["static_frac"] * 100, 2), fmt(S9["if1_room"], 2), fmt(S9["static_sum"] * 1e3, 2)))
    p("   20i. T2 RECORDED (OPEN against E-1's acceptance; its comparison is the next task): record l9stk's E-1 limit (%s K/W, %s W a FET at %s A)"
      % (fmt(S9["rec"][3][2], 2), fmt(S9["rec"][3][0], 3), fmt(S9["i"], 2)))
    p("     assumes the current splits evenly between Q39, Q40 and Q42. With one FET at r and two at R, the one carries I R / (R + 2 r) and dissipates")
    p("       I^2 R^2 r / (R + 2 r)^2; over r this is largest at r = R / 2, I^2 R / 8, which is 9/8 of the even split's I^2 R / 9: an uneven split")
    p("       can put %s times the even loss in one FET (with two FETs the even split is the worst case; with three it is not). The other two then"
      % fmt(S["t2"], 3))
    p("       carry I / 4 each (9/16 of the even loss), so that FET's rise is (9/8) (Zself + Zmut) against E-1's (Zself + 2 Zmut): over E-1's figure")
    p("       at that split wherever Zmut is under Zself / 7, and at the worst split, one FET at R / (2 - 4 m) for m = Zmut / Zself, wherever Zmut")
    p("       is under Zself / 4 (round 11's correction of this line, section 21a: %s at m = 0.2, where R / 2 gives %s); with the coupling"
      % (fmt(worst_share(0.2)[0], 4), fmt(split_share(2.0, 0.2), 4)))
    p("       negligible, the allowance's 45.88 K/W puts that junction at %s C held at %s A where" % (fmt(S["t2_tj"], 1), fmt(S9["i"], 2)))
    p("       E-1 states 150 C (INFERRED; the spread of RDS(on) between parts is not printed). 45.88 K/W is NOT SETTLED: OPEN against E-1's acceptance")
    p("   20j. E-14 AND E11-45 AS THEY NOW READ (record l9stk's E-14 with record l8p's 12g; this record's E11-45, section 8; RECORD, INFERRED)")
    p("     E-14 (b), board A's part: with the return held the inhibit sets within %s ms, so the charge through the off breaker ends within %s ms of"
      % (fmt(S["t_set"] * 1e3, 2), fmt(S["charge_end"] * 1e3, 2)))
    p("       passing board P's threshold (%s to %s A), under E-14's 10 ms, the junction's rise inside record l8p's %s K for 10 ms; (c), board A's part:"
      % (fmt(S["thr_lo"], 3), fmt(S["thr_hi"], 3), fmt(S["pulse_k"], 1)))
    p("       the battery FETs stay off at least %s s after the return rises (the breaker restarts within %s s), then are released once CELL+ reads alive"
      % (fmt(S["hold_min"], 3), fmt(S["restart"], 3)))
    p("     E11-45 rows (c2), (e), (f), (g) and (h) carry round 10's acceptances; (c2) is B-R2's case with route R1 (no longer open on board A's side)")
    p("   20k. FINDINGS FOR OTHER RECORDS (each is its owner's; nothing of theirs is edited here)")
    p("     L4E11-R10-F1, record l8p (12f, the interface): the box 'RET under 1.0 V with OUT at 2.0 V or over' also contains a closed loop, RET/OUT")
    p("       22 / (22 + RT1) under 0.5 for RT1 over 22 kOhm at BRK_VIN under about 3.6 V, which every back-fed ramp passes; board A reads the return")
    p("       held under %s V (board P holds %s V); the interface's figure is a 2N7002's least threshold, and the state board P produces is 'held'"
      % (fmt(S["ret_low"], 3), fmt(S["held"], 3)))
    p("     L4E11-R10-F2, record l8p (check_l8p_netlist.py, its EN group on board A): it wants DOCK_EN_OUT and DOCK_EN_RET to reach J_DOCK and RT1")
    p("       alone, so it reads FAIL on any board A that carries DD-7 (round 9's Q44 and R109 already, round 10's U48 and R109): the group should")
    p("       allow DD-7's loads (this record's check_dd7_netlist.py reads them)")
    p("     L4E11-R10-F3, record l9stk (15.5, the thermal guard) with record l8p (RT1): Murata's PRF15BB103RB6RC prints 10 kOhm +-50 %% at 25 C, 100 kOhm"
      % ())
    p("       at a sensing temperature over 110 C (no upper bound) and 4.7 MOhm at 130 +-3 C (DM-SA16-E056 Rev.1 p.4); '47 kOhm at 130 C' is the 470 ohm")
    p("       group's column. The guard's trip lies under 133 C (4.7 MOhm far over 338 kOhm), but its no-trip side in the 18 A service (the FETs at")
    p("       118.0 C) rests on no printed point: RT1 may pass the first inverter's 61.3 kOhm (2.5 V at 10.6 V) anywhere over 110 C (MAKER, INFERRED)")
    p("   20l. WHAT STAYS OPEN (MAKER, INFERRED, ASSUMPTION as named in 20c to 20e)")
    p("     physical: the hold's capacitor under DC bias and D26's hot leakage (E11-45 h); U47's and U48's thresholds as the lot reads them; the")
    p("       latch with the breaker held off (E11-45 f); board P's own conditions (record l8p: E-14b, R10's tolerance, E-12c)")
    p("     T2 (20i): E-1's even split, OPEN against its acceptance; E11-37 OPEN (Q-TI-17 or the bench with three)")
    p("     the -1 latched with a source present and no charge over board P's threshold stays latched (nothing asks an inhibit and Q46 blocks the")
    p("       pulse): it restarts on board P's detector at a charge over %s to %s A, on a redocking, or on the input's return to a dark kit (record"
      % (fmt(S["thr_lo"], 3), fmt(S["thr_hi"], 3)))
    p("       l9stk's DD-7 reach, unchanged; RECORD)")
    p("     the window's bound (RT1 under %s kOhm) rests on RT1 staying under it while the FETs' copper sits at the air: Murata prints no point"
      % fmt(S["window_rt1"] / 1e3, 1))
    p("       between 25 C and 110 C (its curve is typical)")
    p("   20m. STATUS (SESSION): L8P-F04 CORRECTED IN THE DRAFT (U48 reads the held return and the powered loop; set within %s ms; held at least %s s;"
      % (fmt(S["t_set"] * 1e3, 2), fmt(S["hold_min"], 3)))
    p("     released on CELL+ alive); L8P-F05 CORRECTED IN THE DRAFT (a dead CELL+ never sets the inhibit; the bleeder holds the latch for any source")
    p("     under %s mA, the LM5069's resistor down to %s of its value at 16.8 V); B-R2 with route R1 DRAFTED on both boards; composes in L4-E9's"
      % (fmt(S["isrc_max"] * 1e3, 3), "%.3f" % (S["rint_min"][0][1] / S["r_int"])))
    p("     order and reads DRAWN on the regenerated netlist; nothing measured")
    p("")


# ---- round 11 (4 October 2026, task T2): E-1 under an uneven split of the RDS(on) spread, and E11-37, compared over three approaches
R11_PINS = {"pxp9r1": ("v2/vendor/nexperia/held/nexperia-pxp9r1-30ql.pdf", "88a7b67bfcec9ba7dbf4619be60cfaa883f61b7c9a93a19affc3a5278d91513f"),
            "sqj407": ("v2/vendor/power/held/vishay-sqj407ep-62806-revb.pdf", "1c1038b032b5bf378878473ba170cdbbd640ce1597fbb9c23be20adeaea663e8")}
PINS.update(R11_PINS)
R11_DERATE = 25.0              # K, the record's convention (15c): a part's junction limit 25 K under its rated maximum (the BUK6Y10-30P's 150 C under 175 C)


def worst_share(m):
    """The factor by which the hottest of three paralleled FETs' junction rise can exceed the even split's, over every split of their
    RDS(on) with each at most the allowance R (two at R, one at r = R / x, x >= 1), for m = Zmut / Zself: the rise of the one at r is
    I^2 R (Zself x + 2 Zmut) / (x + 2)^2, largest at x = 2 - 4 m while m < 1/4; the even split's is I^2 R (Zself + 2 Zmut) / 9."""
    if m >= 0.25:
        return 1.0, 1.0
    x = 2.0 - 4.0 * m
    return split_share(x, m), x


def split_share(x, m):
    """The hottest of three FETs' junction rise over the even split's, two at R and one at R / x, for m = Zmut / Zself."""
    return 9.0 * (x + 2.0 * m) / ((x + 2.0) ** 2 * (1.0 + 2.0 * m))


def fix21_round(R, T):
    """T2 of the approved plan: E-1 (record l9stk 15.5) at its own case with the sharing NOT assumed even, and E11-37 (the three FETs'
    Ciss against TI's 5 nF), over three approaches: (i) three FETs kept, (ii) two FETs under 5 nF, (iii) a buffer on BATDRV."""
    S9, L, H, S20 = R["S19"], R["L"], R["H"], R["S20"]
    S = {}
    i_, t0, band = S9["i"], S9["t0"], S9["band"]
    r17k = S9["r17_allow"] * S9["pr17"]
    S["fet_budget"] = 150.0 - t0 - band - r17k                     # K the three FETs' own rise may take, R17 placed apart
    ra = F16_RA
    S["ra"] = ra
    # the allowance is taken at the charger's printed least gate drive (SLUSE65A VBATDRV_ON's minimum) and E-1's 150 C: section 15c's
    # two-chord figure for the BUK6Y10-30P, reproduced here; at the typical 10 V drive the figure (and so the loss) would be lower
    S["vg"] = H["drv"][0]
    cbk = R["K"]["cands"][2]
    if "BUK6Y10-30P" not in cbk["lab"] or abs(cbk["rb"] - ra) > 0.0005e-3 or abs(cbk["tjlim"] - 150.0) > 1e-9:
        refuse(4, "the RDS(on) allowance is not section 15c's figure at the charger's least drive and 150 C")
    rd = cbk["rdef"]
    S["ra_10v"] = fet_bound(rd["r10_25"], rd["r10_hot"], rd["t_hot"], rd["r45_25"], 10.0, 150.0)[1] * 1e-3
    S["p_even"] = (i_ / 3.0) ** 2 * ra
    S["p_worst"] = i_ ** 2 * ra / 8.0                               # m = 0: the one at R / 2 carries I / 2
    S["bar_old"] = S9["rec"][3][2]                                  # record l9stk's 45.88 K/W, the even split's
    S["tj_old_worst"] = t0 + band + r17k + S["bar_old"] * S["p_even"] * worst_share(0.0)[0]
    S["bar_new"] = S["bar_old"] / worst_share(0.0)[0]               # on record l9stk's printed 45.88 K/W, the even split's bar
    S["bar_m"] = [(m_, S["bar_old"] / worst_share(m_)[0], worst_share(m_)[1]) for m_ in (0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.4)]
    S["bar_check"] = S["fet_budget"] / (S["p_even"] * worst_share(0.0)[0])  # the same from this record's rounding (within 0.1 %)
    if abs(S["bar_check"] - S["bar_new"]) > 0.001 * S["bar_new"] + 0.02:
        refuse(4, "the worst-split bar does not reproduce from the budget")
    # the service rows at the corrected bar with the worst split, as round 9 printed them at the even split (identical by construction)
    S["tj_rows"] = S9["tj_rec"]
    # a bounded spread, for information only: the sheet's typical is no printed minimum
    bk = flat(text_pdf("buk6y10"))
    m = need(bk, r"RDSon drain-source on-state VGS = -10 V; ID = -13\.5 A; Tj = 25 °C - (\d+) (\d+) mΩ", "the BUK6Y10-30P's RDS(on) at 25 C")
    S["bk_typ_max"] = f(m, 1) / f(m, 2)
    xb = 1.0 / S["bk_typ_max"]
    S["bounded"] = split_share(xb, 0.0)
    S["bk_qg"] = f(need(bk, r"QG\(tot\) total gate charge VDS = -15 V; ID = -12 A; VGS = -10 V; - ([\d.]+) (\d+) nC", "the BUK6Y10-30P's QG(tot)"), 2) * 1e-9
    # ---- (i)-b: three of another part of the class, PXP9R1-30QL (Nexperia, held), by the record's own bound and convention
    Lp = lambda pat, what: find("pxp9r1", pat, what, layout=True)[1]
    m = Lp(r"VGS = -10 V; ID = -10\.8 A; Tj = 25 °C\s+-\s+([\d.]+)\s+([\d.]+)\s+mΩ\s+resistance\s+VGS = -10 V; ID = -10\.8 A; Tj = 150 °C\s+-\s+([\d.]+)\s+([\d.]+)\s+mΩ\s+VGS = -4\.5 V; ID = -9\.1 A; Tj = 25 °C\s+-\s+([\d.]+)\s+([\d.]+)\s+mΩ", "PXP9R1-30QL's RDS(on)")
    px = dict(r10_25=f(m, 2), r10_hot=f(m, 4), t_hot=150.0, r45_25=f(m, 6))
    px["tj_rated"] = f(Lp(r"Tj\s+junction temperature\s+-55\s+(\d+)\s+°C", "PXP9R1-30QL's junction rating"))
    px["tj_lim"] = px["tj_rated"] - R11_DERATE
    px["kg"], px["r"] = fet_bound(px["r10_25"], px["r10_hot"], px["t_hot"], px["r45_25"], S["vg"], px["tj_lim"])
    px["r"] *= 1e-3
    px["ciss"] = f(Lp(r"Ciss\s+input capacitance\s+VDS = -15 V; f = 1 MHz; VGS = 0 V;\s+-\s+(\d+)", "PXP9R1-30QL's Ciss")) * 1e-12
    find("pxp9r1", r"MLPAK33 \(SOT8002\)", "PXP9R1-30QL's package")
    px["budget"] = px["tj_lim"] - t0 - band - r17k
    px["p_even"] = (i_ / 3.0) ** 2 * px["r"]
    px["bar"] = px["budget"] / (px["p_even"] * worst_share(0.0)[0])
    px["ciss3"] = 3 * px["ciss"]
    S["px"] = px
    # ---- (ii) two FETs under TI's 5 nF: each part's Ciss from its held sheet against 2.5 nF; the pair's bar (two: the even split is the worst)
    two = []
    for lab, key, pat, k in (("BUK6Y10-30P (Nexperia)", None, None, None),
                             ("PXP9R1-30QL (Nexperia)", None, None, None),
                             ("AONS21357 (AOS)", "aons21357", r"Ciss\s+Input Capacitance\s+(\d+)\s+pF", 1),
                             ("SQJ403EP (Vishay)", "sqj403", r"Input Capacitance\s+Ciss\s+-\s+(\d+)\s+(\d+)", 2),
                             ("SQJ407EP (Vishay)", "sqj407", r"Input capacitance\s+Ciss\s+-\s+(\d+)\s+(\d+ \d+)", 2)):
        # the figure judged is the sheet's MAXIMUM where it prints one (Vishay's two, group 2; V2-m1: round 11 took their typical column and
        # called it the maximum), the typical figure where the sheet prints no maximum (Nexperia, AOS)
        if key is None:
            c = L["ciss_t"] if lab.startswith("BUK") else px["ciss"]
            typ, kind = c, "typical, no maximum printed"
        else:
            mm = find(key, pat, lab + "'s Ciss", layout=True)[1]
            c = float(mm.group(k).replace(" ", "")) * 1e-12
            typ, kind = (c, "typical, no maximum printed") if k == 1 else (float(mm.group(1).replace(" ", "")) * 1e-12, "maximum")
            if k == 2 and not c > typ:
                refuse(4, "%s's Ciss maximum is not over its typical figure" % lab)
        two.append((lab, c, 2 * c, 2 * c < H["bf_ciss"]))
        S.setdefault("two_note", {})[lab] = (typ, kind)
    S["two"] = two
    S["pair_bar"] = S9["rec"][2][2]                                 # record l9stk's 20.39 K/W for the BUK6Y10-30P pair (Zself + Zmut)
    S["pair_ciss"] = (2 * L["ciss_t"], 2 * L["ciss_0"])
    S["pair_tau"] = (H["rdrv"][1] * 2 * L["ciss_t"], H["rdrv"][1] * 2 * L["ciss_0"], L["roff"][1] * 2 * L["ciss_0"])
    S["pair_vs_three"] = S["pair_bar"] / S["bar_new"]
    # the class's figure of merit: RDS(on) maximum at -10 V and 25 C times Ciss, per held part (MAKER rows), against the pair's need
    S["fom_bk"] = 10e-3 * L["ciss_t"]
    # ---- (iii) a buffer between BATDRV and the FETs: what TI prints about BATDRV
    tb = flat("".join(pdf_pages("bq25730")))
    need(tb, r"BATDRV 21 O P-channel battery FET \(BATFET\) gate driver output\. It is shorted to VSYS to turn off the BATFET\. It goes 10 V below VSYS to fully turn on BATFET\. BATFET is in linear mode to regulate VSYS at minimum system voltage when battery is depleted\. BATFET is fully on during fast charge and works as an ideal-diode in supplement mode\.", "BATDRV's pin text")
    need(tb, r"P-channel MOSFETs is used for battery charging BATFET\. The gate drivers are internally integrated into the IC with 10 V of gate drive voltage\.", "the BATFET's driver text")
    need(tb, r"the Ciss of P-channel MOSFET should be chosen less than 5 nF", "TI's 5 nF")
    S["buffer_mentions"] = len([s_ for s_ in tb.split(". ") if "BATDRV" in s_ and ("buffer" in s_ or "external driver" in s_)])
    if S["buffer_mentions"]:
        refuse(4, "SLUSE65A names a buffer or an external driver on BATDRV: read it before rejecting approach (iii)")
    # ---- the connected path of the selected approach (unchanged parts)
    S["tau3"] = (S9["tau3_on"][0], S9["tau3_on"][1], S9["tau3_off"])
    S["q49_q"] = 3 * S["bk_qg"]
    return S


def render_fix21(R, p):
    S, S9, H, L = R["S21"], R["S19"], R["H"], R["L"]
    px = S["px"]
    p("21. ROUND 11 (TASK T2): E-1 WITH THE SHARING NOT ASSUMED EVEN, AND E11-37, OVER THREE APPROACHES (4 October 2026)")
    p("   21a. THE DEFECT ON C-PROT rev 1 (record l9stk's E-1 at 23.93 A held from L4-E12's 76.25 C, MODELED; the band %s K, R17's %s K apart; INFERRED)"
      % (fmt(S9["band"], 2), fmt(S9["r17_allow"] * S9["pr17"], 2)))
    p("     E-1 sized each FET at the even split, %s W at the RDS(on) allowance %s mOhm, and set (Zself + 2 Zmut) at most %s K/W. Every FET's"
      % (fmt(S["p_even"], 4), fmt(S["ra"] * 1e3, 3), fmt(S["bar_old"], 2)))
    p("     RDS(on) is at most the allowance; Nexperia prints no minimum. With two at R and one at R / x the hottest one's rise is I^2 R (Zself x")
    p("     + 2 Zmut) / (x + 2)^2: largest at x = 2 - 4 m (m = Zmut / Zself) while m is under 1/4, the even split's otherwise; over the even")
    p("     split it is 9 (x + 2 m) / ((x + 2)^2 (1 + 2 m)): %s at m = 0 (one FET at R / 2 takes I / 2 and %s W). At record l9stk's %s K/W the"
      % (fmt(worst_share(0.0)[0], 4), fmt(S["p_worst"], 4), fmt(S["bar_old"], 2)))
    p("     hottest junction reads %s C held at %s A where E-1 states 150 C: E-1 fails at its own case (round 10's 20i, corrected in place: at the"
      % (fmt(S["tj_old_worst"], 1), fmt(S9["i"], 2)))
    p("     split R / 2 the even split's figure is exceeded wherever Zmut is under Zself / 7, at the worst split wherever it is under Zself / 4:")
    p("     at m = 0.2 the worst split gives %s where R / 2 gives %s)" % (fmt(worst_share(0.2)[0], 4), fmt(split_share(2.0, 0.2), 4)))
    p("     the allowance is section 15c's two-chord figure at the charger's printed least gate drive, VBATDRV_ON %s V (SLUSE65A p.%s), and 150 C;"
      % (fmt(S["vg"], 1), H["drv_p"]))
    p("       at a 10 V drive it would read %s mOhm and the bar would loosen by that ratio: the printed least drive is the one taken (MAKER, INFERRED)"
      % fmt(S["ra_10v"] * 1e3, 3))
    p("     with the spread bounded at the sheet's typical over its maximum (%s at -10 V and 25 C, no printed minimum: INFERRED, information only)"
      % fmt(S["bk_typ_max"], 2))
    p("     the factor would be %s" % fmt(S["bounded"], 4))
    p("   21b. THE THREE APPROACHES (MAKER rows; the bars are installed per-FET figures at E-1's limit; INFERRED)")
    p("     (i) THREE FETS KEPT. (a) The BUK6Y10-30P, E-1's installed acceptance taken over the worst split: (Zself + 2 Zmut) at most %s K/W"
      % fmt(S["bar_new"], 2))
    p("       for any m (the even split's %s K/W times 8 (1 - m)(1 + 2 m) / 9 for a measured m under 1/4):" % fmt(S["bar_old"], 2))
    for m_, b_, x_ in S["bar_m"]:
        p("         m %4s: (Zself + 2 Zmut) at most %s K/W (the worst one at R / %s)" % (fmt(m_, 2), fmt(b_, 2), fmt(x_, 3)))
    p("       Ciss %s nF typical (%s near 0 V), %s times TI's 5 nF: E11-37 stays on TI's answer or the bench; no land, net or part changes"
      % (fmt(S9["ciss3"][0] * 1e9, 2), fmt(S9["ciss3"][1] * 1e9, 2), fmt(S9["ciss_ratio"][0], 2)))
    p("       (b) another part of the class, PXP9R1-30QL (MLPAK33, rated %s C, so the record's convention puts its limit at %s C): RDS(on) %s"
      % (fmt(px["tj_rated"], 0), fmt(px["tj_lim"], 0), fmt(px["r"] * 1e3, 3)))
    p("       mOhm at %s V and %s C (printed %s mOhm at -10 V and 150 C, the gate chord x%s); the worst-split bar %s K/W, under (a)'s; Ciss"
      % (fmt(S["vg"], 1), fmt(px["tj_lim"], 0), fmt(px["r10_hot"], 1), fmt(px["kg"], 4), fmt(px["bar"], 2)))
    p("       %s nF typical for three, %s times TI's 5 nF; a new land: worse on its bar (printed maxima) and on Ciss (typical)"
      % (fmt(px["ciss3"] * 1e9, 2), fmt(px["ciss3"] / H["bf_ciss"], 2)))
    p("     (ii) TWO FETS UNDER TI'S 5 nF (two: the even split is the worst split for any coupling): each part's Ciss against 2.5 nF, at each")
    p("       sheet's own VDS: the printed maximum where the sheet prints one (Vishay's two), the typical figure where it prints none (MAKER):")
    for lab, c, c2, ok in S["two"]:
        typ, kind = S["two_note"][lab]
        p("         %s: %s nF %s%s, two %s nF: %s" % (lab, fmt(c * 1e9, 2), kind, " (%s nF typical)" % fmt(typ * 1e9, 2) if kind == "maximum" else "",
                                                    fmt(c2 * 1e9, 2), "under 5 nF" if ok else "over 5 nF"))
    p("       only the BUK6Y10-30P pair stays under 5 nF, on a TYPICAL figure (%s nF at the sheet's -15 V; about %s near 0 V, over it; no maximum"
      % (fmt(S["pair_ciss"][0] * 1e9, 2), fmt(S["pair_ciss"][1] * 1e9, 2)))
    p("       printed: CONDITIONAL, Q-TI-17 (e)); its E-1 bar is record l9stk's (Zself +")
    p("       Zmut) at most %s K/W, %s of (i)'s; BATDRV's time constants %s / %s us on and %s us off; Q42 and its land leave the draft"
      % (fmt(S["pair_bar"], 2), fmt(S["pair_vs_three"], 3), fmt(S["pair_tau"][0] * 1e6, 2), fmt(S["pair_tau"][1] * 1e6, 2), fmt(S["pair_tau"][2] * 1e6, 2)))
    p("     (iii) A BUFFER BETWEEN BATDRV AND THE FETS: SLUSE65A prints BATDRV as the gate driver of linear-mode regulation of VSYS_MIN and of the")
    p("       ideal diode in supplement ('BATFET is in linear mode to regulate VSYS at minimum system voltage when battery is depleted ... works as")
    p("       an ideal-diode in supplement mode'), the driver 'internally integrated into the IC', and names no external driver or buffer on")
    p("       BATDRV in any sentence: a buffer would sit inside loops whose gain and compensation TI does not print, and a follower loses")
    p("       its own drop from BATDRV's least %s V drive (raising every RDS(on) bound); no printed figure supports it (MAKER, INFERRED;"
      % fmt(S["vg"], 1))
    p("       Q-TI-17 (f) asks)")
    p("   21c. THE CONNECTED PATH (INFERRED)")
    p("     the charger's gate drive: (i) BATDRV into the three, %s / %s us on and %s us off (round 9); (ii) %s / %s us and %s us; (iii) not bounded"
      % (fmt(S["tau3"][0] * 1e6, 2), fmt(S["tau3"][1] * 1e6, 2), fmt(S["tau3"][2] * 1e6, 2), fmt(S["pair_tau"][0] * 1e6, 2), fmt(S["pair_tau"][1] * 1e6, 2),
         fmt(S["pair_tau"][2] * 1e6, 2)))
    p("     IF-1 (U46's hold) and DD-7 (Q49 on CH_BATDRV) do not depend on the count: Q49 moves at most %s nC (three QG(tot) maxima) and BATDRV"
      % fmt(S["q49_q"] * 1e9, 0))
    p("       sinks at most %s mA while it holds; the breaker's band (%s A) and R17 are untouched; (i)(a) keeps the land, the pour and RT1 at the"
      % (fmt(S9["batdrv_sink"] * 1e3, 2), fmt(S9["i"], 2)))
    p("       three's centroid; (ii) removes Q42 and moves RT1 to the pair's centroid; (iii) adds a supply below VSYS less 10 V, which board A has not")
    p("   21d. THE SELECTION (SESSION, on printed figures)")
    p("     (i)(a): the three BUK6Y10-30P stay; E-1's installed acceptance becomes the worst split's, (Zself + 2 Zmut) at most %s K/W (or the"
      % fmt(S["bar_new"], 2))
    p("       measured pair (Zself, Zmut) by the formula of 21b), so the hottest junction is at most 150 C held at %s A for any split of the"
      % fmt(S9["i"], 2))
    p("       RDS(on) spread under the allowance, the service rows unchanged (%s C at 10 A, %s C in the 18 A service, %s C held at %s A); E-1's"
      % (fmt(S["tj_rows"][0], 1), fmt(S["tj_rows"][1], 1), fmt(S["tj_rows"][2], 1), fmt(S9["i"], 2)))
    p("       limit, the 23.93 A, the 18 A for 60 s and 76.25 C are not lowered. Why: (ii)'s bar is %s of (i)'s and (iii) has no printed basis;"
      % fmt(S["pair_vs_three"], 3))
    p("       (i)(b) is worse on its bar and on Ciss. No circuit change: the charger draft's layout requirement carries the corrected bar")
    p("     E11-37 STAYS OPEN: no printed figure decides a three-device gate load against TI's 5 nF; Q-TI-17 (clarification/TI-QUESTIONS.md,")
    p("       drafted, NOT SENT) gains (e), the 5 nF's VDS and the pair's %s / %s nF typical (the fallback rests on that typical figure), and"
      % (fmt(S["pair_ciss"][0] * 1e9, 2), fmt(S["pair_ciss"][1] * 1e9, 2)))
    p("       (f), the gate load TI does accept on BATDRV (Ciss or QG(tot), over -20 to 70 C) and whether any buffer is supported; the bench row")
    p("       E11-37 stands; on a negative answer the supplier's correction scope is (ii): the pair, its bar %s K/W measured on the coupon, Q42"
      % fmt(S["pair_bar"], 2))
    p("       removed (a draft then owed)")
    p("   21e. STATUS: E-1's defect CORRECTED IN THE ACCEPTANCE (the bar %s K/W; CONDITIONAL on E11-29 at that bar and E11-36's allowance);"
      % fmt(S["bar_new"], 2))
    p("     E11-37 OPEN (TI or the bench); no net changed, so a netlist reading does not apply to this correction; no printed figure shows")
    p("     %s K/W achievable: E11-29's coupon decides (the bar %s %% under the even split's) (INFERRED)"
      % (fmt(S["bar_new"], 2), fmt((1.0 - S["bar_new"] / S["bar_old"]) * 100.0, 1)))
    S20 = R["S20"]
    a68 = R["S22"]["opts"]["a"]
    p("   21f. V1'S MINORS OF ROUND 10 (R84 stands; R256's part is SUPERSEDED by round 12, section 22)")
    p("     R256: round 11 moved it from 4.7k to 6.8k so that U47's RESET stayed under TI's recommended %s mA at the 29.2 V clamp (%s mA against"
      % (fmt(S20["i_rec"] * 1e3, 0), fmt(a68["v"]["sink"](R["S19"]["vbat_clamp"]) * 1e3, 2)))
    p("       %s mA), and printed its cost as a static limit of %s mA beside a bleed of %s s, %s s inside the hold. The check V2 (V2-B1) showed"
      % (fmt(S20["n_sink"][1] * 1e3, 2), fmt(a68["v"]["isrc_max"] * 1e3, 3), fmt(a68["v"]["bleed_zero"], 3), fmt(a68["v"]["hold_min"] - a68["v"]["bleed_zero"], 3)))
    p("       that bleed counted no source: at 6.8k it ends inside the hold only for sources under %s uA. Those figures are WITHDRAWN; round 12"
      % fmt(a68["lim"] * 1e6, 1))
    p("       compares V2's three corrections and selects 4.7k again (section 22), so section 20 prints round 10's values (INFERRED)")
    p("     R84 56R: SPECIFIED pulse-rated (its value text carries it; a part whose maker prints a single-pulse curve covering %s W for %s us,"
      % (fmt(S20["ra_pk"], 1), fmt(S20["tau_arm"] * 1e6, 0)))
    p("       its code owed to Layer 6: CONDITIONAL); the 5 s overload comparison is withdrawn (MAKER, INFERRED)")
    p("")


# ---- round 12 (4 October 2026): the independent check V2 of round 11 (an AI review, as the coordinator received it): V2-B1, the cost of
# R256, as an unresolved design choice over V2's three corrections, and the minors that are this record's (V2-m1 to m5, m9)
R12_PINS = {"csd18510": ("v2/vendor/battery/ti-csd18510q5b.pdf", "cb747de812f6685995917335ec78c663fbf1cee0942db9a3e5b1c375147a601a"),
            "l8p_f06": ("v2/docs/records/l4e11/inputs/l8p-section12j-f06-69156072.md", "aa4e1fe9a3ec164c03cd2be06d77d6c7433e7005149ae67f9c17879ddccafcd0")}
PINS.update(R12_PINS)
R12_DBL = 10.0                 # K, ASSUMPTION (record l8p's L8P-F06, OPEN): the breaker FETs' off leakage doubles every 10 K from TI's one printed row
R12_RBL = {"a": 6.8e3, "b": 4.7e3, "c": 6.8e3}   # ohm, R256 in V2's three corrections: (a) round 11's value kept, (b) round 10's value back, (c) round 11's kept
R12_C_CH = 2.2e-6              # F, (c)'s lever on C241: a 2.2 uF 100 V X7R of the same case (the comparison's value; no part read)
R12_C_RH = 2.4e6               # ohm, (c)'s other lever: R85 doubled
R12_SELECT = "b"               # SESSION (round 12): the correction selected; fix22_round refuses unless it meets both needs and R10_RBL is its value
# the check V2's figures as received (CHECK-V2-AS-RECEIVED.md section 2, V2-B1, and 4.2): what this script must reproduce, never an input
R12_V2 = dict(zero68=1.228, t25_68=1.257, lim68=88e-6, lim68_loads=122e-6, air68=1.339, air68_loads=1.295, held68=2.06, held68_loads=1.95,
              foot47=0.866, lim47=521e-6, held47=1.18, sink68=(4.47e-3, 4.51e-3), sink47=6.39e-3, sink47_off=(3.7e-3, 3.9e-3))


def bleed_time(r, c, v0, vdead, vinf):
    """The time CELL+ takes to fall from v0 under vdead through r into c, the sources into the node holding the level it falls towards at
    vinf (the check V2's V2-B1: t = R C ln((V0 - Vinf) / (Vdead - Vinf))); None when the node never gets under vdead."""
    if vinf >= vdead:
        return None
    return r * c * math.log((v0 - vinf) / (vdead - vinf))


def dd7_variant(R, rbl, rh=None, ch=None, ra=None):
    """DD-7's hold and latch for a bleeder rbl (R256), a hold resistor rh (R85), a hold capacitor ch (C241) and an arm resistor ra (R84):
    section 20's own arithmetic as a function of those four, so the three corrections are judged on one basis."""
    S9, H, S20 = R["S19"], R["H"], R["S20"]
    T = S20["tps"]
    rh, ch, ra = R10_RH if rh is None else rh, R10_CH if ch is None else ch, R10_RA if ra is None else ra
    vb_lo, vb_hi = H["floor"], S9["vbat_clamp"]
    V = dict(rbl=rbl, rh=rh, ch=ch, ra=ra)
    c_hi = ch * (1 + R10_CH_TOL[0]) * (1 + R10_CH_TOL[1])
    c_lo = ch * (1 - R10_CH_TOL[0]) * (1 - R10_CH_TOL[1]) * (1 - R10_CH_BIAS)
    V["tau_arm"] = ra * 1.01 * c_hi
    t_cross = V["tau_arm"] * math.log((vb_lo - S20["vf"][3]) / (vb_lo - S20["vf"][3] - T["vitp"][2]))
    V["t_set"] = S9["tctr_open"] + S20["t_trig"] + S20["t_qa"] + t_cross + S20["tcts1"][1] + 1e-6 + S20["t_q49"] + 1e-6
    V["arm_frac"] = 1 - math.exp(-S20["tcts1"][0] / V["tau_arm"])
    V["v0"] = (vb_lo - S20["vf"][1]) * V["arm_frac"]
    i_cap = vb_hi / (R10_CH_IR / ch)
    ixm = S20["ir_hot"] + T["i_s"] + i_cap
    hold = lambda v0, vrel, ix, r, c: r * c * math.log((v0 + ix * r) / (vrel + ix * r))
    V["hold_min"] = hold(V["v0"], S20["ov_rel"][1], ixm, rh * (1 - R10_RH_TOL), c_lo)
    V["hold_max"] = hold(vb_hi, S20["ov_rel"][0], -T["i_s"], rh * (1 + R10_RH_TOL), c_hi) + S9["tctr_open"]
    V["ra_w"] = 0.5 * c_hi * vb_hi ** 2
    V["arm_peak"] = (vb_hi - S20["vf"][0]) / (ra * 0.99)
    V["arm_i2t"] = V["arm_peak"] ** 2 * V["tau_arm"] / 2
    # the latch: every pull into DD7_N while U47 holds it low (R256 from CELL+ through Q48, R82 and R83 from VBAT through Q47, R255, R107
    # and R108 from CELL+ and R254 through Q52)
    a_, b_ = R10_CS
    kc_hi = b_ * (1 + R10_CS_TOL) / (a_ * (1 - R10_CS_TOL) + b_ * (1 + R10_CS_TOL))
    rth_c = a_ * b_ / (a_ + b_)
    sink = lambda vcell, vbat=vb_hi, tol=0.0: vcell / (rbl * (1 + tol)) + vbat / 300e3 + 12.7 / R10_RPU[2] + vcell / (a_ + b_) + 12.7 / R10_RPU[3]
    dead_at = lambda vref: (T["vitn"][0] - T["i_s"] * rth_c - (1 - kc_hi) * vref) / kc_hi
    v_ref = S20["vol_r"] * sink(dead_at(0.0))
    for _ in range(5):
        v_ref = S20["vol_r"] * sink(dead_at(v_ref))
    V["v_ref"], V["dead"], V["sink"] = v_ref, dead_at(v_ref), sink
    V["isrc_max"] = (V["dead"] - v_ref) / (rbl * 1.01)
    r, c, v0 = rbl * 1.01, S20["c_cell"] * 1.2, S20["vs_max"]
    g = 1 / r + 1 / (a_ + b_) + 1 / S20["u104"]                    # with board P's U104 divider and R107 with R108 credited as loads

    def bleed(i_src, credit=False, v_start=v0):
        if credit:
            return bleed_time(1 / g, c, v_start, V["dead"], (i_src + v_ref / r + v_ref / (a_ + b_)) / g)
        return bleed_time(r, c, v_start, V["dead"], v_ref + i_src * r)

    def limit(t, credit=False):                                   # the sources' total at which the bleed takes t
        e = math.exp(t / ((1 / g if credit else r) * c))
        vinf = (e * V["dead"] - v0) / (e - 1)
        return vinf * g - v_ref / r - v_ref / (a_ + b_) if credit else (vinf - v_ref) / r
    V["bleed"], V["limit"] = bleed, limit
    V["bleed_zero"] = r * c * math.log(v0 / V["dead"])             # rounds 10 and 11's figure: CELL+ taken to fall towards 0 V (no source)
    V["tau_bleed"] = r * c
    return V


def fix22_round(R, T):
    """Round 12: the check V2's blocking finding V2-B1 (round 11 gave the bleed of CELL+ as if no source fed the node, beside a static limit
    of 0.597 mA), reproduced, then V2's three corrections compared on C-PROT rev 1 against both needs: the bleed inside the hold's least
    value with the sources at their hot bound, and U47's RESET sink within TI's recommended current in every state where it sinks."""
    S9, H, S20, B = R["S19"], R["H"], R["S20"], R["B"]
    S = {}
    if not bleed_time(1.0, 1.0, 10.0, 5.0, 4.0) > bleed_time(1.0, 1.0, 10.0, 5.0, 0.0) or bleed_time(1.0, 1.0, 10.0, 5.0, 5.0) is not None:
        refuse(4, "the bleed does not count the sources into CELL+ (V2-B1)")
    base = dd7_variant(R, R10_RBL)
    for k_, want in (("hold_min", S20["hold_min"]), ("hold_max", S20["hold_max"]), ("dead", S20["dead"]), ("isrc_max", S20["isrc_max"]),
                     ("t_set", S20["t_set"]), ("v_ref", S20["latch_vref"]), ("bleed_zero", S20["bleed_t"])):
        if abs(base[k_] - want) > 1e-9 * abs(want):
            refuse(4, "dd7_variant does not reproduce section 20's %s" % k_)
    # ---- the sources into CELL+ with the breaker off and the inhibit held (the battery FETs off)
    vin, vb_hi = S20["f05"]["vin"], S9["vbat_clamp"]
    S["lm"] = (vin / S20["r_int"], vb_hi / S20["r_int"])              # the LM5069's internal 1 MOhm, SENSE to OUT (its tolerance not printed)
    m = need(flat(text_pdf("buk6y10")), r"IDSS drain leakage current VDS = -30 V; VGS = 0 V; Tj = 25 °C - - -(\d+) µA VDS = -30 V; VGS = 0 V; Tj = 125 °C - - -(\d+) µA",
             "the BUK6Y10-30P's two IDSS rows")
    S["bat"] = (3 * f(m, 1) * 1e-6, 3 * f(m, 2) * 1e-6)              # the three battery FETs: Nexperia's printed maxima at 25 C and at 125 C
    if abs(f(m, 1) * 1e-6 - S9["idss"]) > 1e-12:
        refuse(4, "the BUK6Y10-30P's 25 C row is not round 9's")
    S["bat_t"] = (25.0, 125.0)
    S["bat_150"] = S["bat"][1] * (S["bat"][1] / S["bat"][0]) ** (25.0 / 100.0)   # INFERRED: the sheet's own two rows' slope carried to E-1's 150 C
    pg, m = find("csd18510", r"IDSS\s+Drain-to-source leakage current\s+VGS = 0 V, VDS = (\d+) V\s+(\d+)\s+[µμ]A", "the CSD18510Q5B's IDSS", layout=True)
    S["brk_p"], S["brk_vds"], S["brk25"] = pg, f(m, 1), 2 * f(m, 2) * 1e-6
    if len(re.findall(r"\bIDSS\b", "\n".join(pdf_pages("csd18510", True)))) != 1:
        refuse(4, "SLPS632 prints more than one IDSS row: read the hot one")
    brk = lambda t: S["brk25"] * 2 ** ((t - 25.0) / R12_DBL)
    f06 = text("l8p_f06")
    m1 = need(f06, r"\| ([\d.]+) C, the inside air \| ([\d.]+) uA \|", "L8P-F06's air row")
    m2 = need(f06, r"\| ([\d.]+) C, the held case \(record l9stk 15\.4\) \| ([\d.]+) uA \|", "L8P-F06's held row")
    need(f06, r"\*\*ASSUMED:\*\* the off leakage doubles every 10 K from the 25 C row", "L8P-F06's assumption")
    need(f06, r"\*\*Verdict: OPEN\.\*\*", "L8P-F06's verdict")
    S["t_air"], S["t_held"] = f(m1, 1), f(m2, 1)
    S["brk"] = (brk(S["t_air"]), brk(S["t_held"]))
    if abs(S["t_air"] - S9["t0"]) > 1e-9 or abs(S["brk"][0] * 1e6 - f(m1, 2)) > 0.05 or abs(S["brk"][1] * 1e6 - f(m2, 2)) > 0.05:
        refuse(4, "record l8p's L8P-F06 rows do not reproduce from TI's printed row and its assumed doubling")
    S["src"] = dict(v2_25=S["lm"][0] + S["bat"][0], v2_air=S["lm"][0] + S["brk"][0], v2_held=S["lm"][0] + S["brk"][1],
                    air=S["lm"][0] + S["bat"][1] + S["brk"][0], hot=S["lm"][0] + S["bat"][1] + S["brk"][1],
                    hot_clamp=S["lm"][1] + S["bat"][1] + S["brk"][1], hot150=S["lm"][0] + S["bat_150"] + S["brk"][1])
    # ---- V2's arithmetic reproduced (6.8 kOhm as round 11 left it, 4.7 kOhm as round 10 drew it)
    v68, v47 = dd7_variant(R, R12_RBL["a"]), dd7_variant(R, R12_RBL["b"])
    hm = v68["hold_min"]
    S["hold_min"] = hm
    rep = [("6.8 kOhm, no source, CELL+ taken to fall towards 0 V (round 11's figure)", v68["bleed_zero"], R12_V2["zero68"], "s"),
           ("6.8 kOhm, the record's 25 C sources, %s uA" % fmt(S["src"]["v2_25"] * 1e6, 1), v68["bleed"](S["src"]["v2_25"]), R12_V2["t25_68"], "s"),
           ("6.8 kOhm, the sources at which the bleed takes the hold's least %s s" % fmt(hm, 3), v68["limit"](hm), R12_V2["lim68"], "uA"),
           ("6.8 kOhm, the same with U104's divider and R107 with R108 credited as loads", v68["limit"](hm, True), R12_V2["lim68_loads"], "uA"),
           ("6.8 kOhm, the breaker pair at the %s C air on L8P-F06 and the 1 MOhm, %s uA" % (fmt(S["t_air"], 2), fmt(S["src"]["v2_air"] * 1e6, 1)),
            v68["bleed"](S["src"]["v2_air"]), R12_V2["air68"], "s"),
           ("6.8 kOhm, the same with the loads credited", v68["bleed"](S["src"]["v2_air"], True), R12_V2["air68_loads"], "s"),
           ("6.8 kOhm, the breaker pair at the held %s C case and the 1 MOhm, %s uA" % (fmt(S["t_held"], 1), fmt(S["src"]["v2_held"] * 1e6, 1)),
            v68["bleed"](S["src"]["v2_held"]), R12_V2["held68"], "s"),
           ("6.8 kOhm, the same with the loads credited", v68["bleed"](S["src"]["v2_held"], True), R12_V2["held68_loads"], "s"),
           ("4.7 kOhm, no source, towards the foot (round 10 printed %s s towards 0 V)" % fmt(v47["bleed_zero"], 3), v47["bleed"](0.0), R12_V2["foot47"], "s"),
           ("4.7 kOhm, the sources at which the bleed takes %s s" % fmt(hm, 3), v47["limit"](hm), R12_V2["lim47"], "uA"),
           ("4.7 kOhm, the breaker pair at the held case and the 1 MOhm", v47["bleed"](S["src"]["v2_held"]), R12_V2["held47"], "s")]
    for lab, mine, theirs, unit in rep:
        if mine is None or abs(mine - theirs) > 0.012 * theirs:
            refuse(4, "V2's figure is not reproduced: %s" % lab)
    S["rep"] = rep
    for (lo, hi), val in ((R12_V2["sink68"], (v68["sink"](vb_hi), v68["sink"](vb_hi, tol=-0.01))),):
        if abs(val[0] - lo) > 0.005e-3 or abs(val[1] - hi) > 0.005e-3:
            refuse(4, "V2's RESET sink at the clamp is not reproduced")
    if abs(v47["sink"](vb_hi) - R12_V2["sink47"]) > 0.005e-3:
        refuse(4, "V1's 6.39 mA is not reproduced")
    # ---- the three corrections, each a full variant, against both needs
    i_rec = S20["i_rec"]
    S["i_abs"] = f(find("tps37", r"7\.1 Absolute Maximum Ratings.*?Current\s+IRESET1, IRESET2, IRESET1, IRESET2\s+(\d+)\s+mA", "RESET's absolute maximum",
                        layout=True, flags=re.S)[1]) * 1e-3
    vs, vpk, sysovp = S20["vs_max"], S9["vpk"], B["sysovp4s"]
    S["v_states"] = dict(vs=vs, vpk=vpk, sysovp=sysovp, clamp=vb_hi, pack_diode=vpk + S9["vsd"])
    opts = []
    for key, lab, kw in (("a", "(a) text only: R256 6.8 kOhm, the hold as drawn", {}),
                         ("b", "(b) R256 back to 4.7 kOhm, the hold as drawn", {}),
                         ("c", "(c) R256 6.8 kOhm, the hold lengthened by C241 %s uF" % fmt(R12_C_CH * 1e6, 1), dict(ch=R12_C_CH)),
                         ("c2", "(c) with R85 %s MOhm instead" % fmt(R12_C_RH / 1e6, 1), dict(rh=R12_C_RH))):
        v = dd7_variant(R, R12_RBL[key[0]], **kw)
        o = dict(key=key, lab=lab, v=v)
        o["t_hot"], o["t_air"], o["t_hot150"] = v["bleed"](S["src"]["hot"]), v["bleed"](S["src"]["air"]), v["bleed"](S["src"]["hot150"])
        o["t_hot_loads"] = v["bleed"](S["src"]["hot"], True)
        o["lim"] = v["limit"](v["hold_min"])
        o["pair_allow"] = o["lim"] - S["lm"][0] - S["bat"][1]
        o["pair_t"] = 25.0 + R12_DBL * math.log(o["pair_allow"] / S["brk25"], 2) if o["pair_allow"] > S["brk25"] else None
        o["pair_dbl"] = (S["t_held"] - 25.0) / math.log(o["pair_allow"] / S["brk25"], 2) if o["pair_allow"] > S["brk25"] else None
        o["need1"] = o["t_hot"] is not None and o["t_hot"] < v["hold_min"]
        o["margin"] = None if o["t_hot"] is None else v["hold_min"] - o["t_hot"]
        # RESET's sink, R256 at -1 %: the instant of setting (CELL+ follows VBAT to VSYS's top), the breaker restarted while the hold runs
        # (the pack's most), VBAT at the charger's SYSOVP with CELL+ following it, and the state that needs more than one fault
        o["sink"] = dict(set=v["sink"](vs, vs, -0.01), run=v["sink"](vpk, vs, -0.01), ovp=v["sink"](sysovp, sysovp, -0.01), clamp=v["sink"](vb_hi, vb_hi, -0.01))
        o["need2"] = max(o["sink"]["set"], o["sink"]["run"], o["sink"]["ovp"]) <= i_rec
        o["need2_all"] = o["sink"]["clamp"] <= i_rec
        a_, b_ = R10_CS
        o["v_5ma"] = (i_rec - vb_hi / 300e3 - 12.7 / R10_RPU[2] - 12.7 / R10_RPU[3]) / (1 / (v["rbl"] * 0.99) + 1 / (a_ + b_))
        o["t_over"] = 0.0 if o["v_5ma"] >= vb_hi else v["tau_bleed"] * math.log((vb_hi - v["v_ref"]) / (o["v_5ma"] - v["v_ref"]))
        opts.append(o)
    S["opts"] = {o["key"]: o for o in opts}
    S["order"] = [o["key"] for o in opts]
    # (c)'s reach: a still longer hold (C241 3.3 uF) moves its coupled limit towards its static limit, never past it
    v3 = dd7_variant(R, R12_RBL["c"], ch=3.3e-6)
    S["c_reach"] = dict(ch=3.3e-6, hold=(v3["hold_min"], v3["hold_max"]), lim=v3["limit"](v3["hold_min"]), static=v3["isrc_max"],
                        t_hot=v3["bleed"](S["src"]["hot"]))
    S["c_reach"]["pair_allow"] = S["c_reach"]["lim"] - S["lm"][0] - S["bat"][1]
    S["c_reach"]["pair_t"] = 25.0 + R12_DBL * math.log(S["c_reach"]["pair_allow"] / S["brk25"], 2)
    if not S["c_reach"]["lim"] < S["c_reach"]["static"] < S["opts"]["b"]["v"]["isrc_max"]:
        refuse(4, "(c)'s coupled limit is not under its static limit, or its static limit is not under (b)'s")
    sel = S["opts"][R12_SELECT]
    if not (sel["need1"] and sel["need2"]):
        refuse(4, "the selected correction does not meet both needs")
    if abs(sel["v"]["rbl"] - R10_RBL) > 1e-9 or abs(sel["v"]["ch"] - R10_CH) > 1e-15 or abs(sel["v"]["rh"] - R10_RH) > 1e-9:
        refuse(4, "section 20 is not drawn with the selected correction's values")
    if sel["sink"]["clamp"] >= S["i_abs"]:
        refuse(4, "the selected correction passes RESET's absolute maximum at the clamp")
    S["sel"] = sel
    # what the hold's readers would see under (c): the hold's most, the arm, R84's pulse
    S["base_hold_max"], S["base_arm"] = v68["hold_max"], v68["arm_frac"]
    # ---- V1's minor that no record carried (V2-m4): the TPS37's hysteresis accuracy read as +-1.5 percentage points, not relative
    tp = S20["tps"]
    hpt = tp["hacc"]
    k_lo, k_hi = S20["out_k"]
    rth_o = R10_OUT[0] * R10_OUT[1] / (R10_OUT[0] + R10_OUT[1])
    S["hys_alt"] = dict(ret_low=tp["vitp"][0] * (1 - (tp["hys"] + hpt)) - tp["i_s_hi"] * 50.0,
                        out_hi=(tp["vitn"][2] * (1 + tp["hys"] + hpt) + tp["i_s"] * rth_o) / k_lo)
    out_lo = (tp["vitn"][0] * (1 + tp["hys"] - hpt) - tp["i_s"] * rth_o) / k_hi
    S["hys_alt"]["window"] = S9["r_ret"] * (out_lo / S20["ret_high"] - 1)
    S["hys_alt"]["held_margin"] = dict(S20["out_held"])[7.6] - S["hys_alt"]["out_hi"]
    for k_, want, tol in (("ret_low", 0.7643, 0.0006), ("out_hi", 2.008, 0.001), ("window", 25.1e3, 60.0)):
        if abs(S["hys_alt"][k_] - want) > tol:
            refuse(4, "V1's hysteresis-accuracy figure %s is not reproduced" % k_)
    if not (S["hys_alt"]["ret_low"] - S20["held"] > 0.7 and S["hys_alt"]["held_margin"] > 0.5 and S["hys_alt"]["window"] > 1.5 * S9["rt1"][1]):
        refuse(4, "a margin does not survive the percentage-point reading of the hysteresis accuracy")
    return S


def render_fix22(R, p):
    S, S9, S20, H = R["S22"], R["S19"], R["S20"], R["H"]
    ua = lambda x, nd=1: fmt(x * 1e6, nd)
    ma = lambda x, nd=2: fmt(x * 1e3, nd)
    sec = lambda x: "never" if x is None else fmt(x, 3)
    sel, O = S["sel"], S["opts"]
    vst = S["v_states"]
    p("22. ROUND 12: THE CHECK V2'S FINDING V2-B1 (THE COST OF R256) AS A DESIGN CHOICE, AND ITS MINORS FOR THIS RECORD (4 October 2026; C-PROT rev 1)")
    p("   22a. THE CLAIM THAT DID NOT STAND, AND V2'S ARITHMETIC REPRODUCED (V2 is an AI review, as received; INFERRED)")
    p("     round 11 (21f) gave CELL+'s bleed with the breaker off as %s s, inside the hold's least %s s, beside a static limit of %s mA for the"
      % (fmt(O["a"]["v"]["bleed_zero"], 3), fmt(S["hold_min"], 3), fmt(O["a"]["v"]["isrc_max"] * 1e3, 3)))
    p("       sources into CELL+: the bleed was taken towards 0 V, as if no source fed the node. A source I lifts the level CELL+ falls towards to")
    p("       the foot plus I x R256, so t = R C ln((V0 - Vinf) / (Vdead - Vinf)), from VSYS's %s V into CELL_FUSED's %s uF at +20 %% (ASSUMPTION):"
      % (fmt(S20["vs_max"], 3), fmt(S20["c_cell"] * 1e6, 0)))
    for lab, mine, theirs, unit in S["rep"]:
        p("         %s: %s %s (V2: %s)" % (lab, fmt(mine * 1e6, 1) if unit == "uA" else fmt(mine, 3), unit, fmt(theirs * 1e6, 0) if unit == "uA" else fmt(theirs, 3)))
    p("     so the two limits of 21f could not both be used: with R256 at 6.8 kOhm the bleed ends inside the hold only while the sources total under")
    p("       %s uA, and V1's minor was applied by spending that margin (V2-B1, reproduced)" % ua(O["a"]["lim"]))
    p("   22b. THE SOURCES INTO CELL+ WITH THE BREAKER OFF AND THE INHIBIT HELD (each labelled)")
    p("     the LM5069's internal %s MOhm, SENSE to OUT: %s uA at BRK_VIN %s V, %s uA at the %s V clamp (MAKER value; its tolerance not printed)"
      % (fmt(S20["r_int"] / 1e6, 0), ua(S["lm"][0]), fmt(S20["f05"]["vin"], 1), ua(S["lm"][1]), fmt(S9["vbat_clamp"], 1)))
    p("     the three battery FETs: Nexperia prints IDSS at most %s uA at 25 C and %s uA at Tj 125 C, VDS -30 V (BUK6Y10-30P, 17 April 2020, Table 7"
      % (ua(S["bat"][0] / 3, 0), ua(S["bat"][1] / 3, 0)))
    p("       p.6): %s and %s uA for the three (MAKER, printed maxima; V2-m2: rounds 10 and 11 called the hot figure 'not printed'); over 125 C"
      % (ua(S["bat"][0], 0), ua(S["bat"][1], 0)))
    p("       nothing is printed: on the sheet's own two rows' slope E-1's 150 C would read %s uA for the three (INFERRED, information only)" % ua(S["bat_150"]))
    p("     the breaker pair Q101 and Q102 (CSD18510Q5B): TI SLPS632 (March 2017) p.%d prints IDSS %s uA at VGS 0 V, VDS %s V, TA 25 C, its only"
      % (S["brk_p"], ua(S["brk25"] / 2, 0), fmt(S["brk_vds"], 0)))
    p("       row (MAKER); record l8p's L8P-F06 (OPEN; fnd/l8p2 at 69156072, 12j, copied in inputs/) ASSUMES a doubling every %s K: %s uA at the"
      % (fmt(R12_DBL, 0), ua(S["brk"][0])))
    p("       %s C air, %s uA at the held %s C case (ASSUMPTION, not a printed figure)" % (fmt(S["t_air"], 2), ua(S["brk"][1]), fmt(S["t_held"], 1)))
    p("     THE HOT BOUND on C-PROT rev 1 (the pack at %s V, the battery FETs on their printed 125 C row, the breaker pair at its held case):"
      % fmt(S20["f05"]["vin"], 1))
    p("       %s + %s + %s = %s uA (%s uA at the air; %s uA with BRK_VIN at the clamp; %s uA with the battery FETs at 150 C, INFERRED)"
      % (ua(S["lm"][0]), ua(S["bat"][1], 0), ua(S["brk"][1]), ua(S["src"]["hot"]), ua(S["src"]["air"]), ua(S["src"]["hot_clamp"]), ua(S["src"]["hot150"])))
    p("   22c. V2'S THREE CORRECTIONS ON ONE BASIS (need 1: the bleed at the hot bound inside the hold's least; need 2: U47's RESET sink within")
    p("     TI's recommended %s mA, SNVSBJ1E 7.3 p.6, in every state where it sinks; the absolute maximum %s mA, 7.1 p.6; R256 at -1 %% for the sink)"
      % (ma(S20["i_rec"], 0), ma(S["i_abs"], 0)))
    for k in S["order"]:
        o = O[k]
        v = o["v"]
        p("     %s: R256 %s kOhm, R85 %s MOhm, C241 %s uF" % (o["lab"], fmt(v["rbl"] / 1e3, 1), fmt(v["rh"] / 1e6, 1), fmt(v["ch"] * 1e6, 1)))
        p("       the hold %s s at least, %s s at most; the latch reads dead (static) for sources under %s mA; the dead reading %s V"
          % (fmt(v["hold_min"], 3), fmt(v["hold_max"], 2), fmt(v["isrc_max"] * 1e3, 3), fmt(v["dead"], 3)))
        p("       the bleed: %s s with no source (towards 0 V), %s s at the air's %s uA, %s s at the hot bound's %s uA (%s s with the loads credited;"
          % (fmt(v["bleed_zero"], 3), sec(o["t_air"]), ua(S["src"]["air"]), sec(o["t_hot"]), ua(S["src"]["hot"]), sec(o["t_hot_loads"])))
        p("         %s s with the battery FETs at 150 C, INFERRED)" % sec(o["t_hot150"]))
        p("       the coupled limit: the bleed ends inside the hold's least while the sources total under %s uA, which leaves the breaker pair %s uA:"
          % (ua(o["lim"]), ua(o["pair_allow"])))
        p("         on the ASSUMED doubling a case of %s C (the held case %s C), or a doubling no faster than every %s K at the held case"
          % (fmt(o["pair_t"], 1), fmt(S["t_held"], 1), fmt(o["pair_dbl"], 2)))
        p("       NEED 1: %s" % ("HOLDS at the hot bound, %s s inside the hold (on the ASSUMED leakage of the breaker pair: no printed hot figure)" % fmt(o["margin"], 3)
                               if o["need1"] else "FAILS at the hot bound (%s s against the hold's %s s)%s"
                               % (sec(o["t_hot"]), fmt(v["hold_min"], 3), "; it fails at the air too" if o["t_air"] is None or o["t_air"] > v["hold_min"] else "")))
        p("       RESET sinks %s mA at the instant of setting (CELL+ at VSYS's %s V), %s mA with the breaker restarted while the hold runs (the pack's"
          % (ma(o["sink"]["set"]), fmt(vst["vs"], 3), ma(o["sink"]["run"])))
        p("         %s V), %s mA with CELL+ following VBAT at the charger's SYSOVP %s V, %s mA at VBAT's %s V clamp; it reaches %s mA at CELL+ %s V"
          % (fmt(vst["vpk"], 1), ma(o["sink"]["ovp"]), fmt(vst["sysovp"], 1), ma(o["sink"]["clamp"]), fmt(vst["clamp"], 1), ma(S20["i_rec"], 0),
             fmt(o["v_5ma"], 2) if o["v_5ma"] < 40 else "over 40"))
        p("       NEED 2: %s" % ("HOLDS in every state, the clamp included" if o["need2_all"] else
                               ("HOLDS in every state without a second fault (22d); over %s mA only with CELL+ over %s V, at most %s mA, under the absolute %s mA"
                                % (ma(S20["i_rec"], 0), fmt(o["v_5ma"], 2), ma(o["sink"]["clamp"]), ma(S["i_abs"], 0))) if o["need2"] else "FAILS"))
    c, c2 = O["c"], O["c2"]
    p("     what (c) moves for the hold's readers (20d, 20g, E-14 (c), E11-45 (h)): the hold's most %s s (from %s s: the battery FETs held off that long"
      % (fmt(c["v"]["hold_max"], 2), fmt(S["base_hold_max"], 2)))
    p("       after every set, a false set at a docking included); the arm completes %s of the way before the set (from %s), so the hold starts"
      % ("%.4f" % c["v"]["arm_frac"], "%.5f" % S["base_arm"]))
    p("       from %s V; R84's pulse %s mJ and D26's I2t %s A2s (from %s mJ and %s A2s); a 2.2 uF 100 V part and its DC bias not read. With R85"
      % (fmt(c["v"]["v0"], 3), fmt(c["v"]["ra_w"] * 1e3, 3), "%.2e" % c["v"]["arm_i2t"], fmt(S20["ra_w"] * 1e3, 3), "%.2e" % S20["arm_i2t"]))
    p("       %s MOhm instead the hold's least is only %s s (D26's leakage and C241's insulation take more of it): %s"
      % (fmt(R12_C_RH / 1e6, 1), fmt(c2["v"]["hold_min"], 3), "need 1 fails" if not c2["need1"] else "need 1 holds by %s s" % fmt(c2["margin"], 3)))
    cr = S["c_reach"]
    p("     (c)'s reach: with C241 %s uF the hold is %s to %s s and the coupled limit %s uA (the pair %s uA, a case of %s C on the ASSUMED"
      % (fmt(cr["ch"] * 1e6, 1), fmt(cr["hold"][0], 2), fmt(cr["hold"][1], 1), ua(cr["lim"]), ua(cr["pair_allow"]), fmt(cr["pair_t"], 1)))
    p("       doubling): wider than (b)'s by %s uA, never past its static %s mA, where (b)'s static room is %s mA (INFERRED)"
      % (ua(cr["pair_allow"] - O["b"]["pair_allow"]), fmt(cr["static"] * 1e3, 3), fmt(O["b"]["v"]["isrc_max"] * 1e3, 3)))
    p("   22d. THE STATES IN WHICH U47'S RESET SINKS, FROM THE DRAFT'S NETLIST (INFERRED from the netlist; TI's limits MAKER)")
    p("     DD7_N is pulled low by U47's RESET1 and RESET2 alone. Into it, while the loop reads powered (Q47, Q48 and Q52 on): R256 from CELL+ (Q48),")
    p("       R107 with R108 from CELL+ (Q52), R82 with R83 from VBAT (Q47), R254 and R255 from DD7_VC; with the loop unpowered only R255 (%s uA)"
      % ua(12.7 / R10_RPU[2]))
    p("     the battery FETs Q39, Q40 and Q42 have their source on VBAT and their drain on CH_BATQ (check_dd7_netlist.py's BODY group reads it; a")
    p("       reversed FET reads FAIL): a P-channel FET's body diode conducts from drain to source, here from CELL+ towards VBAT, so once the inhibit")
    p("       holds their gates at VBAT nothing on VBAT can lift CELL+; it only bleeds, or is driven by the pack through the breaker")
    p("     state 1, the instant of setting: the FETs were on, a charge passing the off breaker's body diodes into the cells; CELL+ is at most VBAT,")
    p("       regulated to VSYS's %s V (and held within the breaker FETs' VSD of the cells, %s V at most): %s mA, falling with the bleed"
      % (fmt(vst["vs"], 3), fmt(vst["pack_diode"], 1), ma(sel["sink"]["set"])))
    p("     state 2, the breaker restarted while the hold runs (%s s at most): CELL+ at the pack's %s V at most: %s mA" % (fmt(sel["v"]["hold_max"], 2), fmt(vst["vpk"], 1), ma(sel["sink"]["run"])))
    p("     state 3, a charger regulating high: CELL+ following VBAT up to SYSOVP's %s V (SLUSE65A, the 4S row): %s mA, still under %s mA"
      % (fmt(vst["sysovp"], 1), ma(sel["sink"]["ovp"]), ma(S20["i_rec"], 0)))
    p("     the states over %s mA need CELL+ over %s V, %s V over SYSOVP: (i) a surge: VBAT at the SMCJ18A's %s V clamp at the very instant of a set,"
      % (ma(S20["i_rec"], 0), fmt(sel["v_5ma"], 2), fmt(sel["v_5ma"] - vst["sysovp"], 2), fmt(vst["clamp"], 1)))
    p("       with CELL+ lifted %s V over the cells and their body-diode drop while the charge that set it flows: at most %s mA, under the"
      % (fmt(sel["v_5ma"] - vst["pack_diode"], 2), ma(sel["sink"]["clamp"])))
    p("       absolute %s mA, and over %s mA for at most %s s of the bleed (a surge coinciding with the set: a second condition, V1's 'transient"
      % (ma(S["i_abs"], 0), ma(S20["i_rec"], 0), fmt(sel["t_over"], 3)))
    p("       only'), or board P's BRK_VIN at its own %s V clamp with the breaker restarted while a hold runs (the same bound, the pack pulling"
      % fmt(vst["clamp"], 1))
    p("       CELL+ back at once); (ii) sustained: a battery FET failed short AND VBAT held over")
    p("       %s V, which SYSOVP stops: two faults. At %s mA VOL on the 60 ohm reading is about %s V: the inhibit still holds (Q49's VGS under -9 V)"
      % (fmt(sel["v_5ma"], 2), ma(sel["sink"]["clamp"]), fmt(S20["vol_r"] * sel["sink"]["clamp"], 2)))
    p("   22e. THE SELECTION (SESSION) AND WHAT IT COSTS")
    a, b = O["a"], O["b"]
    p("     no correction holds need 1 on printed figures alone: the breaker pair's hot leakage has no printed row, so each depends on record l8p's")
    p("       L8P-F06 (E-14c). (a) fails need 1 at the hot bound and at the air; (c) holds it by %s s with a pair allowance of %s uA, at the cost of"
      % (fmt(c["margin"], 3), ua(c["pair_allow"])))
    p("       a new part, an arm that reaches %s of the way and a hold of up to %s s; (b) holds it by %s s with a pair allowance of %s uA and the"
      % ("%.2f" % c["v"]["arm_frac"], fmt(c["v"]["hold_max"], 2), fmt(b["margin"], 3), ua(b["pair_allow"])))
    p("       larger static room (%s mA against %s mA), with no part beyond round 10's checked circuit" % (fmt(b["v"]["isrc_max"] * 1e3, 3), fmt(a["v"]["isrc_max"] * 1e3, 3)))
    p("     SELECTED: (b), R256 back to 4.7 kOhm: at the hold as drawn it has the widest allowance for the unprinted leakage, and the higher")
    p("       ceiling if the hold is ever lengthened; (c) buys %s uA more only with a hold of up to %s s, about %s K of case temperature on an"
      % (ua(S["c_reach"]["pair_allow"] - b["pair_allow"]), fmt(S["c_reach"]["hold"][1], 0), fmt(S["c_reach"]["pair_t"] - b["pair_t"], 1)))
    p("       assumed rate, which does not remove the dependence on E-14c; need 2 holds on TI's printed rows in every state without a second")
    p("       fault. It costs: U47's RESET over TI's recommended %s mA in the named states of 22d" % ma(S20["i_rec"], 0))
    p("       (never over the absolute %s mA), where 6.8 kOhm kept it under %s mA in every state; and a margin of %s s on an ASSUMED leakage"
      % (ma(S["i_abs"], 0), ma(S20["i_rec"], 0), fmt(b["margin"], 3)))
    p("     reversed by: E-14c reading the breaker pair over %s uA at its held case, or E11-45 (f2) reading the bleed outside the unit's hold; the next"
      % ua(b["pair_allow"]))
    p("       lever is then the hold on top of 4.7 kOhm (the static %s mA is its ceiling), a new round with both checks' arithmetic beside it"
      % fmt(b["v"]["isrc_max"] * 1e3, 3))
    p("   22f. V1'S AND V2'S ARITHMETIC SIDE BY SIDE (R256 has moved twice: 4.7 kOhm in round 10, 6.8 kOhm on V1's minor in round 11, 4.7 kOhm now; INFERRED)")
    p("     V1 (round 10's check, the sink at the clamp): 4.7 kOhm %s mA, over TI's recommended %s mA, 'transient only'; 6.8 kOhm %s mA"
      % (ma(b["v"]["sink"](vst["clamp"])), ma(S20["i_rec"], 0), ma(a["v"]["sink"](vst["clamp"]))))
    p("     V2 (round 11's check, the bleed with the sources): 4.7 kOhm ends inside the hold for sources under %s uA (%s s at the hot bound); 6.8 kOhm"
      % (ua(b["lim"]), sec(b["t_hot"])))
    p("       only under %s uA (%s s at the hot bound, %s s at the air)" % (ua(a["lim"]), sec(a["t_hot"]), sec(a["t_air"])))
    p("     this round (the sink by state): 4.7 kOhm %s mA at the most without a second fault; 6.8 kOhm %s mA"
      % (ma(max(b["sink"]["set"], b["sink"]["run"], b["sink"]["ovp"])), ma(max(a["sink"]["set"], a["sink"]["run"], a["sink"]["ovp"]))))
    p("   22g. WHAT STAYS OPEN, AND E11-45 (f) AND (h) (the rows in section 8 carry the acceptances)")
    p("     V2-B1's claim is CORRECTED (the bleed counts the sources; one coupled limit, %s uA, beside the static %s mA); the latch's timing with the"
      % (ua(b["lim"]), fmt(b["v"]["isrc_max"] * 1e3, 3)))
    p("       breaker off at the hot bound stays OPEN on record l8p's E-14c (the breaker pair's IDSS hot; TI's question drafted there, unsent) and on")
    p("       E11-45 (f) (the bleed timed against the unit's own hold, the leakage into CELL+ read hot); CELL_FUSED's %s uF at +20 %% is an ASSUMPTION"
      % fmt(S20["c_cell"] * 1e6, 0))
    p("     between %s uA and %s mA (not reached at the hot bound): the hold may end with CELL+ still read alive and the breaker off, the inhibit"
      % (ua(b["lim"]), fmt(b["v"]["isrc_max"] * 1e3, 3)))
    p("       releases, and a charge over board P's threshold (%s to %s A) sets it again within %s ms, once a hold; under the threshold it is the"
      % (fmt(S20["thr_lo"], 3), fmt(S20["thr_hi"], 3), fmt(S20["charge_end"] * 1e3, 2)))
    p("       named residual of 20l (the latched FET at most %s C, record l8p); that repeated cycle is not analysed further (INFERRED)" % fmt(S20["under_thr_tj"], 1))
    p("     FOR RECORD l8p (L8P-F06 and E-14c; nothing of its is edited here): the latch's budget is two limits, the static %s mA (round 10's"
      % fmt(b["v"]["isrc_max"] * 1e3, 3))
    p("       again, so its 12j figures stand for the static room) and the timing %s uA, which the pair alone fills from a %s C case, %s K over"
      % (ua(b["lim"]), fmt(b["pair_t"], 1), fmt(b["pair_t"] - S["t_held"], 1)))
    p("       its held case; E-14c's acceptance (the pair at most %s uA at %s C) keeps the timing with %s uA in hand; its copies of 20c to 20e"
      % (ua(S["brk"][1], 0), fmt(S["t_held"], 0), ua(b["lim"] - S["src"]["hot"])))
    p("       and of this record's drafts are round 10's and are taken again at this round (the check V2's V2-B2, its owner's) (RECORD, INFERRED)")
    h = S["hys_alt"]
    p("   22h. THE MINORS (V2-m1 to m5 and m9, this record's part; RECORD, INFERRED)")
    p("     V2-m1: 21b (ii) now takes Vishay's printed MAXIMA for the SQJ403EP and SQJ407EP and prints the typical figures beside them")
    p("     V2-m2: Nexperia's hot IDSS row quoted in 20e and 22b; V2-m3: the dd7 draft's comment restated from 22c's figures")
    p("     V2-m4, V1's two minors that no record carried: (1) the TPS37's hysteresis accuracy (+-%s %%) read as percentage points, not relative: the"
      % fmt(S20["tps"]["hacc"] * 100, 1))
    p("       return read held under %s V (board P holds %s V), the loop read powered over %s V at most (%s mV over the interface's 2.0 V; the"
      % (fmt(h["ret_low"], 4), fmt(S20["held"], 3), fmt(h["out_hi"], 3), fmt((h["out_hi"] - S20["if_out"]) * 1e3, 0)))
    p("       held loop reads %s V over it at 7.6 V), the window's bound %s kOhm: every margin still holds (V1's figures reproduced); OWNER this record,"
      % (fmt(h["held_margin"], 3), fmt(h["window"] / 1e3, 1)))
    p("       NEXT Q-TI-19 (drafted, NOT SENT) and E11-45 (e); (2) the CONOPS wording of the named residual (a breaker latched with a source present")
    p("       and no charge over board P's threshold stays latched: the pack stays isolated while the source carries the kit): OWNER the CONOPS")
    p("       owner with record l9stk, NEXT the sentence drafted in the record's 22h goes to L4-E9's next round as a register row (a controlled")
    p("       amendment of an accepted Layer 2 page is the coordinator's)")
    p("     V2-m5: E11-29's coupon reads the PTC's site against each junction with one FET heated alone (the row and block 17d)")
    p("     V2-m9: the tests compose board A in main's order, with record l8r2's d8v3 and vbus20ov; the candidate's change list (L4-E9 rows 24 to 33)")
    p("       names l8r2's packrtn, slotlm and fb01 instead, which are NOT in this branch's tree (fnd/l8r3 at 89924e40): the tests keep the order")
    p("       this tree can show. On a scratch copy of the candidate's files (fnd/v2cand at dfa1eef2) with this round's drafts laid over them,")
    p("       compose_in_list_order.py composed the list's order (16 drafts, each exit 0), the generator ran to its end (778 parts, intent")
    p("       written), check_dd7_netlist.py read DRAWN and three mutations read FAIL (a scratch run of 4 October 2026, not a committed test)")
    p("   22i. STATUS (SESSION): V2-B1 answered by correction (b); need 1 CONDITIONAL on E-14c and E11-45 (f2), OPEN until one reads; need 2 holds")
    p("     on TI's printed rows without a second fault; R84 stays specified pulse-rated (CONDITIONAL, Layer 6); the netlist reads DRAWN at 4.7 kOhm;")
    p("     the round is the author's answer to V2's first negative check of the 6.8 kOhm value and is UNVERIFIED until its targeted recheck")
    p("")


# ---- round 13 (4 October 2026): the owner's supplier-delta review of that day, finding DELTA-02 (P1): E11-29 heats "each FET alone"
# through its body diode and reads each junction by its own VSD, on three devices whose drains share one pour and whose sources share
# another: the three body diodes are in parallel, so neither is defined. Three executable methods compared, one selected, E11-29 restated;
# and section 20c restated on Murata's printed points (record l9stk's round 4)
R13_PINS = {"l9stk_guard": ("v2/docs/records/l4e11/inputs/l9stk-section15.5-guard-43da41ca.md", "90ae3c25377af1177634164e94badbdd42daf01fce1786a7f3d39d52f83164c5")}
PINS.update(R13_PINS)
R13_CHARGER = "v2/docs/records/l4e11/apply_gen_sch_a_charger.py"
R13_SELECT = "B"               # SESSION (round 13): the method selected; fix23_round refuses a method that does not address one device
R13_TERMS = dict(k=0.02, p=0.01, air=1.0)   # RECORD (block E11-29, round 9): the K-factor, the heating power (relative) and the air (K), as expanded limits
R13_B = dict(i_m=1e-3, rep=0.5, leak=0.3, slot=2.44e-4)   # SESSION proposals for method B, the supplier's to confirm: the sense current (A), the
                               # threshold reading's repeatability between two calibrations (K), the off devices' leakage in the sense current (K), the slot (s)
R13_C = dict(n=1.0, k=2.0e-3)  # ASSUMPTION for method C's bracket only: a diode ideality of at least 1 and a K-factor of about 2 mV/K (not printed)
# each method as data: the path a step drives through a device, the terminal that selects one device (None: a diode has none), the
# direction, and the terminals the specimen gives a net of its own per device
R13_METHODS = {
    "old": dict(lab="rounds 9 to 12 and TP-E11-29: each FET heated through its body diode alone, each junction by its own VSD, on the pours as drafted",
                heat=dict(path="body diode", terminals=("D", "S"), select=None, direction="drain to source"),
                sense=dict(path="body diode", terminals=("D", "S"), select=None, direction="drain to source"), private=()),
    "A": dict(lab="(A) a coupon whose three sources sit on islands of their own behind links, each gate on its own island: body-diode heating, VSD sensing",
              heat=dict(path="body diode", terminals=("D", "S"), select=None, direction="drain to source"),
              sense=dict(path="body diode", terminals=("D", "S"), select=None, direction="drain to source"), private=("S", "G")),
    "B": dict(lab="(B) the pours as board A's, the three gates brought out apart: one channel at a time selected by its gate, heated source to drain, its threshold read with the gate on the drain",
              heat=dict(path="channel", terminals=("S", "D"), select="G", direction="source to drain"),
              sense=dict(path="channel at threshold", terminals=("S", "D"), select="G", direction="source to drain"), private=("G",)),
    "C": dict(lab="(C) the three body diodes heated and read together on the pours as drafted: the total power and one voltage",
              heat=dict(path="body diode", terminals=("D", "S"), select=None, direction="drain to source"),
              sense=dict(path="body diode", terminals=("D", "S"), select=None, direction="drain to source"), private=()),
}


def per_device(step, private):
    """Whether a heating or sensing step addresses ONE of several devices: (a) a terminal of the path it drives sits on a net of the
    device's own; or (b) the path is a channel that a terminal on a net of the device's own selects, and the current enters at the
    source of this P-channel part, so every unselected device is off and its body diode reverse-biased. A body diode has no selecting
    terminal: with both its terminals on common nets the diodes are in parallel and no source sets one diode's current (DELTA-02)."""
    if any(t in private for t in step["terminals"]):
        return True, "a terminal of the path is on a net of the device's own"
    if step["select"] is not None and step["select"] in private and step["path"].startswith("channel") and step["direction"] == "source to drain":
        return True, "the channel is selected by a gate of the device's own, the unselected body diodes reverse-biased"
    return False, "both terminals of the path are common and nothing selects one device: the three are in parallel"


def charger_fets():
    """The battery FETs as apply_gen_sch_a_charger.py draws them, read by ast from the statement the draft writes into the generator:
    the references, the value text and the gate, drain and source nets; and the draft's sha256 (the reading is bound to its bytes)."""
    import ast
    path = os.path.join(TOP, R13_CHARGER)
    src = open(path, encoding="utf-8").read()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and "nfet(_qb" in node.value:
            for line in node.value.split("\n"):
                if line.startswith("for _qb in"):
                    st = ast.parse(line).body[0]
                    call = st.body[0].value
                    if not (isinstance(st, ast.For) and isinstance(call, ast.Call) and call.func.id == "nfet" and call.args[0].id == "_qb"):
                        refuse(4, "the charger draft's battery FET statement is not the one this record reads")
                    val, g, d, s = [a.value for a in call.args[1:5]]
                    return dict(refs=[e.value for e in st.iter.elts], value=val, G=g, D=d, S=s, sha=sha_file(path))
    refuse(4, "the charger draft draws no battery FET statement")


def fix23_round(R, T):
    """Round 13: DELTA-02. The topology read from the charger draft and Nexperia's sheet; the old method shown undefined on it; three
    executable methods judged for per-device heating power and junction temperature; the selection; E11-29's acceptance and its
    uncertainty budget on the selected method; section 20c restated on the PTC's printed points."""
    S9, S20, S21, S22, L = R["S19"], R["S20"], R["S21"], R["S22"], R["L"]
    S = {}
    # ---- the topology: the draft's statement and the maker's sheet
    fets = charger_fets()
    if fets["refs"] != ["Q39", "Q40", "Q42"] or "P-FET" not in fets["value"] or (fets["G"], fets["D"], fets["S"]) != ("CH_BATDRV", "CH_BATQ", "VBAT"):
        refuse(4, "the charger draft's battery FETs are not the three P-channel devices on CH_BATDRV, CH_BATQ and VBAT")
    S["fets"] = fets
    S["board_private"] = ()        # one statement draws the three on the same gate, drain and source nets: no terminal has a net of its own
    pg, _m = find("buk6y10", r"Table 2\. Pinning information", "Table 2")
    t2 = flat(pdf_pages("buk6y10")[pg - 1])
    need(t2, r"1 S source 2 S source 3 S source 4 G gate mb D mounting base; connected to drain", "the LFPAK56's pinning")
    S["pin_p"] = pg
    pg, m = find("buk6y10", r"IS source current Tmb = 25 °C - -(\d+) A", "the source-drain diode's IS")
    S["is_p"], S["is"] = pg, f(m, 1)
    S["id100"] = f(find("buk6y10", r"VGS = -10 V; Tmb = 100 °C - -(\d+) A", "ID at a 100 C mounting base")[1])
    pg, m = find("buk6y10", r"VSD source-drain voltage IS = -(\d+) A; VGS = 0 V; Tj = 25 °C - -([\d.]+) -([\d.]+) V", "the body diode's VSD row")
    S["vsd_p"], S["vsd"] = pg, (f(m, 1), f(m, 2), f(m, 3))
    pg, m = find("buk6y10", r"VGSth gate-source threshold voltage ID = -(\d+) µA; VDS=VGS; Tj = 25 °C -([\d.]+) -([\d.]+) -([\d.]+) V", "the threshold row")
    S["vth_p"], S["vth"] = pg, (f(m, 1) * 1e-6, f(m, 2), f(m, 3), f(m, 4))
    S["fig11_p"] = find("buk6y10", r"Fig\. 11\. Gate-source threshold voltage as a function of junction temperature", "Fig. 11")[0]
    m = need(flat(text_pdf("buk6y10")), r"RDSon drain-source on-state VGS = -10 V; ID = -13\.5 A; Tj = 25 °C - (\d+) (\d+) mΩ", "RDS(on) at 25 C")
    r_typ = f(m, 1) * 1e-3
    # ---- the defect, reproduced on the drafted topology (and with the gates alone brought out: a diode has no selecting terminal)
    old = R13_METHODS["old"]
    S["defect"] = dict(heat=per_device(old["heat"], S["board_private"]), sense=per_device(old["sense"], S["board_private"]),
                       heat_gates=per_device(old["heat"], ("G",)), sense_gates=per_device(old["sense"], ("G",)))
    if any(v[0] for v in S["defect"].values()):
        refuse(4, "DELTA-02 is not reproduced: the body-diode method reads as per-device on common nets")
    # ---- the three methods, each on its own specimen's nets and on board A's as drafted
    S["judge"] = {}
    for key in ("A", "B", "C"):
        mth = R13_METHODS[key]
        S["judge"][key] = dict(heat=per_device(mth["heat"], mth["private"]), sense=per_device(mth["sense"], mth["private"]),
                               heat_board=per_device(mth["heat"], S["board_private"]), sense_board=per_device(mth["sense"], S["board_private"]))
    if R13_SELECT not in S["judge"]:
        refuse(4, "the selected method is not one of the three compared: the body-diode method on common nets is the defect")
    sel = S["judge"][R13_SELECT]
    if not (sel["heat"][0] and sel["sense"][0]):
        refuse(4, "the selected method does not address one device: it heats or senses 'alone' on common nets")
    # ---- the powers E11-29 imposes (C-PROT rev 1, record l9stk's E-1 at the breaker's largest limit), and the rises at the bar
    i_, ra = S9["i"], S21["ra"]
    S["p"] = dict(even=S21["p_even"], hot=S21["p_worst"], other=i_ ** 2 * ra / 16.0)
    if abs(S["p"]["hot"] + 2 * S["p"]["other"] - i_ ** 2 * ra / 4.0) > 1e-12:
        refuse(4, "the worst split's powers do not add to a quarter of I^2 R")
    S["bar"], S["bar_even"] = S21["bar_new"], S21["bar_old"]
    S["rise_bar"] = S["bar"] * S["p"]["even"]                     # the rise at the bar with the three heated evenly
    S["budget"] = S21["fet_budget"]                               # the FETs' own rise E-1 leaves, R17 apart
    S["rise_total"] = 150.0 - S9["t0"]                            # with the band carrying its current and R17 dissipating in place
    S["bar_gap"] = 1.0 - S["bar"] / S["bar_even"]
    # ---- method B's heating currents (one channel conducting at a time, so each device's power is the supply's current times its own VDS)
    cur = lambda p_: (math.sqrt(p_ / ra), math.sqrt(p_ / r_typ))  # at the allowance (hot, least drive) and at the typical 25 C figure
    S["r_typ"] = r_typ
    S["i_single"] = cur(S["p"]["hot"])
    S["slot_w"] = (3 * S["p"]["even"], S["p"]["hot"] + 2 * S["p"]["other"])
    S["i_td"] = (cur(S["slot_w"][0]), cur(S["slot_w"][1]))
    if max(S["i_single"][1], S["i_td"][0][1], S["i_td"][1][1]) >= S["id100"]:
        refuse(4, "method B's heating current passes the part's ID at a 100 C mounting base")
    zslot = L["z"][R13_B["slot"]]
    S["zslot"] = zslot
    S["ripple"] = (S["slot_w"][0] * zslot, S["slot_w"][1] * zslot)  # at most: the device's Zth(j-mb) at the slot's width (16b's reading) times the slot's power
    S["duty_worst"] = (S["p"]["hot"] / S["slot_w"][1], S["p"]["other"] / S["slot_w"][1])
    S["leak_frac"] = 2 * (S22["bat"][1] / 3) / R13_B["i_m"]         # the two off devices' printed IDSS at 125 C against the sense current
    S["sense_k"] = R13_B["i_m"] * S["vth"][3] * S["bar"]            # the sense current's own heating, at the threshold's largest row
    # ---- the uncertainty budgets on (Zself + 2 Zmut) at the bar: expanded terms combined in quadrature, as the block states its own three
    rise = S["rise_bar"]
    comb = lambda terms: math.sqrt(sum(x * x for _l, x in terms))
    base = [("the K-factor", R13_TERMS["k"]), ("the heating power", R13_TERMS["p"]), ("the air within %s K" % fmt(R13_TERMS["air"], 0), R13_TERMS["air"] / rise)]
    S["terms"] = {"A": base,
                  "B": base + [("the threshold reading repeated between two calibrations, %s K" % fmt(R13_B["rep"], 1), R13_B["rep"] / rise),
                               ("the off devices' leakage in the sense current, %s K" % fmt(R13_B["leak"], 1), R13_B["leak"] / rise),
                               ("half the time-division ripple, %s K" % fmt(S["ripple"][0] / 2, 2), S["ripple"][0] / 2 / rise)]}
    S["u"] = {k_: comb(v) for k_, v in S["terms"].items()}
    S["pass"] = {k_: S["bar"] / (1 + u_) for k_, u_ in S["u"].items()}
    S["pass_even"] = S["bar_even"] / (1 + S["u"]["B"])
    S["pass_rise"] = S["rise_total"] / (1 + S["u"]["B"])
    # method C: one voltage across three diodes in parallel reads between the mean and the hottest; the bracket on the hottest junction
    vt = 8.617333e-5 * (150.0 + 273.15)
    S["c_bracket"] = R13_C["n"] * vt * math.log(3.0) / R13_C["k"]
    S["c_frac"] = S["c_bracket"] / rise
    if not (S["u"]["B"] < S["bar_gap"] / 2 < S["c_frac"]):
        refuse(4, "method B's budget does not resolve the bar's two forms, or method C's bracket does")
    # ---- section 20c on the PTC's printed points (record l9stk's round 4, its reading of Murata's DM-SA16-E056 Rev.1 p.4, copied to inputs/)
    g = flat(text("l9stk_guard"))
    need(g, r"The kit's PRF15BB103 chip PTC, 10 kOhm plus or minus 50 %", "the PTC's 25 C row")
    need(g, r"\*\*100 kOhm at a sensing temperature over 110 C\*\* \(no upper bound\) and \*\*4\.7 MOhm at 130 plus or minus 3 C\*\*", "the PTC's printed points")
    need(g, r"The 47 kOhm column stands over the 470 ohm groups only", "the misread's correction")
    need(g, r"\*\*Finding L8P-F07, OPEN\.\*\*", "L8P-F07's state")
    m = need(g, r"a factory-set temperature switch \(no trip under ([\d.]+) C, tripped from ([\d.]+) C\) that pulls the loop's return, with a fixed resistor in RT1's place", "l9stk's selected guard")
    S["switch"] = (f(m, 1), f(m, 2))
    if abs(S9["rt1"][2] - 47e3) > 1e-6:
        refuse(4, "round 9's reading of l9stk's page is not the 47 kOhm this round withdraws")
    loop, i_ret = S20["loop"], S20["tps"]["i_s_hi"]
    rows = []
    for lab, rt in (("25 C, at least 5 kOhm", 5e3), ("25 C, at most 15 kOhm", 15e3), ("100 kOhm, reached somewhere over 110 C", 100e3), ("4.7 MOhm at 130 +-3 C", 4.7e6)):
        for vin in (S9["pack_lo"], S9["vpk"]):
            out, ret = loop(vin, rt, i_ret=i_ret)
            inv = "on" if ret > 2.5 else ("off" if ret < 1.0 else "not defined")
            a = "closed" if ret > S20["ret_high"] else ("held" if ret < S20["ret_low"] else "between")
            rows.append(dict(lab=lab, rt=rt, vin=vin, out=out, ret=ret, inv=inv, a=a, powered=out > S20["out_rel"][1]))
    S["ptc_rows"] = rows
    by = {(r_["rt"], r_["vin"]): r_ for r_ in rows}
    if not (by[(15e3, S9["pack_lo"])]["inv"] == "on" and by[(15e3, S9["pack_lo"])]["a"] == "closed" and by[(4.7e6, S9["vpk"])]["inv"] == "off"
            and by[(4.7e6, S9["vpk"])]["a"] == "held" and by[(4.7e6, S9["pack_lo"])]["powered"] and by[(100e3, S9["pack_lo"])]["inv"] == "not defined"):
        refuse(4, "section 20c's readings on the PTC's printed points are not the ones this round states")

    def rt_at(vin, level):                                        # the RT1 at which the loaded return reads `level`
        lo, hi = 1e3, 1e7
        for _ in range(80):
            mid = math.sqrt(lo * hi)
            if loop(vin, mid, i_ret=i_ret)[1] > level:
                lo = mid
            else:
                hi = mid
        return lo
    S["inv_loaded"] = [(vin, rt_at(vin, 2.5), rt_at(vin, 1.0)) for vin in (S9["pack_lo"], S9["vpk"])]
    m = need(g, r"With the tolerances and board A's loads: ([\d.]+) and ([\d.]+) kOhm, ([\d.]+) and ([\d.]+) kOhm", "l9stk's loop levels")
    S["l9_inv"] = (f(m, 1), f(m, 2), f(m, 3), f(m, 4))
    mine = (S["inv_loaded"][0][1], S["inv_loaded"][1][1], S["inv_loaded"][0][2], S["inv_loaded"][1][2])
    if any(abs(a_ / 1e3 - b_) > 0.10 * b_ for a_, b_ in zip(mine, S["l9_inv"])):
        refuse(4, "the first inverter's levels are not within a tenth of record l9stk's")
    S["withdrawn"] = (S20["bound"][0], S20["bound"][1], S20["bound_margin"])
    # what the selected guard (not drafted here) would hand DD-7: the return pulled low with a fixed 15 kOhm in RT1's place
    S["sw_rows"] = [(vin, loop(vin, 15e3, held=0.0)[0], loop(vin, 15e3, i_ret=i_ret)[1]) for vin in (7.6, S9["pack_lo"], S9["vpk"])]
    if not all(o > S20["out_rel"][1] and r_ > S20["ret_high"] for _v, o, r_ in S["sw_rows"]):
        refuse(4, "with a fixed 15 kOhm the pulled loop does not read powered or the closed loop does not read closed")
    return S


def e11_29_method13(R):
    """E11-29's method and acceptance as round 13 stated them (printed in 23e as its history; round 14 restates the lines, e11_29_method)."""
    S, S9 = R["S23"], R["S19"]
    return ("the method (round 13, section 23, after the owner's supplier-delta review's DELTA-02: the three body diodes are in parallel, so "
            "the earlier 'each FET heated through its body diode alone, each junction by its own VSD' is WITHDRAWN): on a coupon with board A's "
            "drain and source pours unchanged and the three gates brought out apart, one channel conducts at a time, selected by its gate, the "
            "current entering at the source so the other two are off and their body diodes reverse-biased; each device's heating power is the "
            "supply's current times that device's own source-to-drain voltage on four-wire taps; each junction is read by that device's "
            "threshold voltage at %s mA with its gate switched to the drain, the other gates on the source, against a K-factor calibrated in "
            "an oven in the same connection; cases: each FET alone at %s W and at %s W (the 3 x 3 matrix of Zself and Zmut, its reciprocity "
            "checked), the three evenly at %s W each and the worst split (%s W in one, %s W in each other, each FET in turn) by time division "
            "in slots of at most %s us, the band carrying %s A and R17 dissipating in place; acceptance: each FET's (Zself + 2 Zmut) at most "
            "%s K/W less the budget's %s %% (a reading of %s K/W or under), or by the measured m as section 21b; the worst split's hottest "
            "junction at most %s K over the air (%s K less the budget); R17's coupling at most %s K/W; the PTC's site (RT1's land at the drain "
            "tabs' centroid) read by a thermocouple in every case and its gradient to the hottest junction RECORDED for record l9stk's guard"
            % (fmt(R13_B["i_m"] * 1e3, 0), fmt(S["p"]["even"], 3), fmt(S["p"]["hot"], 3), fmt(S["p"]["even"], 3), fmt(S["p"]["hot"], 3), fmt(S["p"]["other"], 3),
               fmt(R13_B["slot"] * 1e6, 0), fmt(S9["i"], 2), "%.2f" % S["bar"], fmt(S["u"]["B"] * 100, 2), "%.2f" % S["pass"]["B"], fmt(S["pass_rise"], 2),
               fmt(S["rise_total"], 2), fmt(S9["r17_allow"], 1)))


def render_fix23(R, p):
    S, S9, S20, S21 = R["S23"], R["S19"], R["S20"], R["S21"]
    J = S["judge"]
    yn = lambda v: ("YES: " if v[0] else "NO: ") + v[1]
    ft = S["fets"]
    p("23. ROUND 13: DELTA-02, E11-29'S METHOD ON THREE PARALLELED BODY DIODES, AND SECTION 20c ON MURATA'S PRINTED POINTS (4 October 2026; C-PROT rev 1)")
    p("   23a. THE DEFECT (the owner's supplier-delta review of 4 October 2026, DELTA-02, P1; NETLIST, MAKER, INFERRED)")
    p("     the draft: %s %s" % (ft["sha"][:16], R13_CHARGER))
    p("       draws %s, %s and %s by one statement: every gate on %s, every drain on %s, every source on %s: no terminal has a net of its own"
      % (ft["refs"][0], ft["refs"][1], ft["refs"][2], ft["G"], ft["D"], ft["S"]))
    p("     the part (Nexperia BUK6Y10-30P, 17 April 2020): Table 2 (p.%d) pins 1 to 3 source, 4 gate, the mounting base the drain, the symbol's diode"
      % S["pin_p"])
    p("       from drain to source of this P-channel part; the source-drain diode rows IS %s A (p.%d) and VSD %s V typical, %s V at most at %s A"
      % (fmt(S["is"], 0), S["is_p"], fmt(S["vsd"][1], 1), fmt(S["vsd"][2], 1), fmt(S["vsd"][0], 0)))
    p("       (p.%d): so the three body diodes are in parallel between CH_BATQ and VBAT (MAKER, INFERRED)" % S["vsd_p"])
    p("     E11-29 as rounds 9 to 12 wrote it, and TP-E11-29 after it: heating one diode alone: %s" % yn(S["defect"]["heat"]))
    p("       reading one junction by its own VSD: %s" % yn(S["defect"]["sense"]))
    p("       three sources on the same two nets do not set one diode's current, and four-wire taps remove lead drops, they isolate nothing;")
    p("       rounds 11 and 12 moved the limit to %s K/W and kept this method: the limit was not the defect (DELTA-02, reproduced; INFERRED)" % ("%.2f" % S["bar"]))
    p("   23b. THREE METHODS: THE CURRENT PATHS IN CALIBRATION, HEATING AND SENSING (SESSION; INFERRED)")
    p("     (A) a coupon whose three sources sit on islands of their own, island k joined to the VBAT pour by a link Lk, gate k on island k")
    p("       calibration (oven; links open):  source k (+) -> CH_BATQ pour (the common anode) -> body diode k -> island k -> source k (-), at the sense current")
    p("       heating (links open):            the same path at the heating current, one source a device; P_k = I_k x V(drain tab k, island k)")
    p("       sensing (links open):            source k back to the sense current; VSD_k read on its own taps, the three at once")
    p("       the coupon's electrical test:    links closed (the three in parallel, as board A)")
    p("     (B) the pours as board A's; only the gates apart: gate k to a driver, the other gates on VBAT (off)")
    p("       calibration (oven):   I_M %s mA (+) -> VBAT pour (the common source) -> channel k at threshold, GATE k ON CH_BATQ -> CH_BATQ pour -> (-)"
      % fmt(R13_B["i_m"] * 1e3, 0))
    p("                             (VDS = VGS, the connection of the sheet's own threshold row);")
    p("                             the other two off, their body diodes reverse-biased (the source positive); V(source tap k, drain tap k) is device k's threshold")
    p("       heating:              I_H (+) -> VBAT pour -> channel k, gate k driven 10 V under VBAT -> CH_BATQ pour -> shunt -> (-); P_k = I_H x V(source tap k, drain tap k)")
    p("       sensing:              I_H off, gate k switched to CH_BATQ, I_M as in calibration; then gate j, then gate l in turn (one device read at a time)")
    p("       several heated:       time division: the channels conduct in turn in slots of at most %s us, so each device's power is still I_H x its own VDS over its slots"
      % fmt(R13_B["slot"] * 1e6, 0))
    p("     (C) the pours as board A's, the gates on VBAT")
    p("       calibration, heating, sensing:  one source (+) -> CH_BATQ pour -> THREE body diodes in parallel -> VBAT pour -> (-): the total power and one voltage")
    p("   23c. EACH METHOD JUDGED (per-device heating power and junction temperature; MAKER rows, INFERRED, ASSUMPTION as named)")
    for key in ("A", "B", "C"):
        p("     %s" % R13_METHODS[key]["lab"])
        p("       heating one device, on its specimen: %s" % yn(J[key]["heat"]))
        p("       reading one junction, on its specimen: %s" % yn(J[key]["sense"]))
        p("       on board A as drafted (no gate, drain or source of a device's own): heating %s, reading %s (INFERRED)"
          % ("YES" if J[key]["heat_board"][0] else "NO", "YES" if J[key]["sense_board"][0] else "NO"))
        if key == "A":
            p("       power: each source's current times its own VSD, within the block's %s %% (INFERRED); temperature: VSD at a fixed sense current, the K-factor within %s %%"
              % (fmt(R13_TERMS["p"] * 100, 0), fmt(R13_TERMS["k"] * 100, 0)))
            p("       budget on (Zself + 2 Zmut): %s %% (the block's three terms), a reading of %s K/W or under; Zself and Zmut separable electrically"
              % (fmt(S["u"]["A"] * 100, 2), "%.2f" % S["pass"]["A"]))
            p("       the copper: the VBAT source pour is cut into three islands behind links, and each gate leaves the common node: the source leads' heat")
            p("         path and the coupling through the source pour are not board A's. Transfer: joining the islands again adds conductance between the three")
            p("         and to the pour, which lowers the hottest junction for the FETs' own heat (the coupon is the safe side there), but Zmut reads LOW, so")
            p("         section 21b's relaxed bar cannot be fed, and heat reaching the FETs through the VBAT copper from its neighbours reads LOW: an allowance")
            p("         a second specimen would have to give (INFERRED; not a measurement uncertainty, so not in the %s %%)" % fmt(S["u"]["A"] * 100, 2))
        elif key == "B":
            p("       power: one channel conducts at a time, so P_k is the supply's current times device k's own VDS; the two off devices carry their leakage")
            p("         (Nexperia: IDSS at most %s uA each at 125 C); alone at %s W: %s to %s A (the allowance to the typical 25 C %s mOhm); the three evenly"
              % (fmt(R["S22"]["bat"][1] / 3 * 1e6, 0), fmt(S["p"]["hot"], 3), fmt(S["i_single"][0], 2), fmt(S["i_single"][1], 2), fmt(S["r_typ"] * 1e3, 0)))
            p("         by time division %s to %s A (%s W in the conducting one), the worst split %s to %s A (%s W; duties %s and %s), all under ID's %s A"
              % (fmt(S["i_td"][0][0], 2), fmt(S["i_td"][0][1], 2), fmt(S["slot_w"][0], 3), fmt(S["i_td"][1][0], 2), fmt(S["i_td"][1][1], 2), fmt(S["slot_w"][1], 3),
                 fmt(S["duty_worst"][0], 2), fmt(S["duty_worst"][1], 2), fmt(S["id100"], 0)))
            p("         at a 100 C mounting base (MAKER, p.3); the junction's ripple at most %s K (the device's %s K/W at %s us, section 16b's reading)"
              % (fmt(S["ripple"][0], 2), fmt(S["zslot"], 4), fmt(R13_B["slot"] * 1e6, 0)))
            p("       temperature: device k's threshold at %s mA with its gate on its drain (Table 7, p.%d: %s / %s / %s V at %s uA and 25 C; Fig. 11, p.%d, prints it"
              % (fmt(R13_B["i_m"] * 1e3, 0), S["vth_p"], fmt(S["vth"][1], 1), fmt(S["vth"][2], 0), fmt(S["vth"][3], 0), fmt(S["vth"][0] * 1e6, 0), S["fig11_p"]))
            p("         against junction temperature; no coefficient is printed: the K-factor is calibrated per device, as VSD's was); the sense current heats")
            p("         the junction by at most %s K; the two off devices divert at most %s %% of it at 125 C (MAKER, INFERRED)" % (fmt(S["sense_k"], 2), fmt(S["leak_frac"] * 100, 0)))
            p("       budget on (Zself + 2 Zmut), expanded terms in quadrature on the %s K rise at the bar:" % fmt(S["rise_bar"], 2))
            for lab, x in S["terms"]["B"]:
                p("         %s: %s %%" % (lab, fmt(x * 100, 2)))
            p("         in all %s %%: a reading of %s K/W or under passes the %s K/W bar (the last three terms are SESSION proposals, the supplier's to confirm)"
              % (fmt(S["u"]["B"] * 100, 2), "%.2f" % S["pass"]["B"], "%.2f" % S["bar"]))
            p("       Zself and Zmut: separable, device by device: k alone gives Zself k and the two Zmut into the others; the matrix's reciprocity (Zjk against")
            p("         Zkj) checks the method on the specimen; section 21b's formula is fed by the largest Zself and the largest Zmut (INFERRED)")
            p("       the copper: the drain pour, the source pour, R17, the band and RT1's land are board A's; only the three gate traces differ, which carry")
            p("         no heat of consequence. Transfer: block E11-29's comparison rule, unchanged (INFERRED)")
        else:
            p("       power: the total only, within %s %%; the split between the three follows each diode's own forward voltage, and the hotter diode takes"
              % fmt(R13_TERMS["p"] * 100, 0))
            p("         more: no device's power is known (INFERRED)")
            p("       temperature: one voltage; at the sense current it lies between the three evenly sharing and the hottest carrying it all, a bracket of")
            p("         n (kT/q) ln 3 over the K-factor = %s K at 150 C (ASSUMPTION: n %s, %s mV/K), %s %% of the %s K rise at the bar, against the %s %%"
              % (fmt(S["c_bracket"], 1), fmt(R13_C["n"], 0), fmt(R13_C["k"] * 1e3, 0), fmt(S["c_frac"] * 100, 0), fmt(S["rise_bar"], 2), fmt(S["bar_gap"] * 100, 1)))
            p("         between the bar's two forms (%s and %s K/W): it cannot decide the acceptance" % ("%.2f" % S["bar"], "%.2f" % S["bar_even"]))
            p("       Zself and Zmut: not separable; no split can be imposed, the worst split least of all. The copper is board A's. It can bound: the")
            p("         region's total power against one bracketed junction, a cross-check of (A) or (B), never the acceptance (INFERRED)")
    p("   23d. THE SELECTION (SESSION)")
    p("     SELECTED: (B). It is the only one of the three that leaves the copper as board A's, gives each device's power and junction with no")
    p("       assumption about sharing, and can impose the worst split itself; it costs a gate driver per device, a sequencer and a threshold")
    p("       calibration whose repeatability the specimen must show")
    p("     reversed by: the two threshold calibrations (before and after the runs) differing by more than %s K, or the matrix failing reciprocity"
      % fmt(R13_B["rep"], 1))
    p("       beyond the budget, or no supplier agreeing to the setup: then (A), judged on the %s K/W bar alone with the VBAT copper's allowance" % ("%.2f" % S["bar"]))
    p("       named as owed; (C) only as a cross-check (INFERRED)")
    p("     the first prototype of board A is NOT a specimen for (B) as drafted: its three gates share %s (heating %s); it becomes one only with"
      % (ft["G"], "YES" if J["B"]["heat_board"][0] else "NO"))
    p("       a removable link in each gate branch, a change to the charger draft and the layout NOT DRAFTED here (owed before the prototype's layout; RECORD)")
    p("   23e. E11-29'S ACCEPTANCE ON (B) (C-PROT rev 1: 23.93 A held from 76.25 C; the row of section 8 carries this text; RECORD, INFERRED)")
    p("     %s" % e11_29_method13(R))
    p("     (round 14: these lines are SUPERSEDED by section 24d, the recheck V2R's V2R-B2; the fixture by 24b, V2R-B1)")
    p("     the bar by form: %s K/W for any coupling (a reading of %s or under); %s K/W for m at or over 1/4 (%s or under); the direct case: the worst"
      % ("%.2f" % S["bar"], "%.2f" % S["pass"]["B"], "%.2f" % S["bar_even"], "%.2f" % S["pass_even"]))
    p("       split's hottest junction, the band and R17 on, at most %s K over the air less the budget, %s K (INFERRED)" % (fmt(S["rise_total"], 2), fmt(S["pass_rise"], 2)))
    p("   23f. THE CORRECTION SCOPE FOR TP-E11-29 (rewritten on it in this round, by the coordinator's instruction; it stays NOT EXECUTABLE; RECORD)")
    p("     1. replace the body-diode excitation and the VSD reading (its sections 2, 4, 5 and 6: 'each FET heated alone', 'the VSD sense taps', the")
    p("        K-factor by VSD) by method (B)'s three connections of 23b, with a fixture schematic showing the supply, the shunt, the three gate")
    p("        drivers, the sense source and each device's four-wire taps in calibration, heating and sensing; the gates switch make-before-break,")
    p("        so the heating supply never meets three channels off (round 14: a series switch isolates the supply for every reading, 24b; V2R-B1)")
    p("     2. the coupon: board A's region as before, with the three gate traces brought to the fixture apart and a tap pair at each device's source")
    p("        leads and drain tab; no source island, no cut in either pour")
    p("     3. the cases of 23e (each alone at two powers, the three evenly, the worst split with each FET in turn, R17 alone, the band on) and the")
    p("        thermocouple on RT1's land in every case")
    p("     4. the validity checks: two threshold calibrations within %s K; reciprocity; the off devices' leakage read at the run's temperature and under"
      % fmt(R13_B["rep"], 1))
    p("        1 % of the sense current, else a larger sense current with its own heating restated; the ripple at the slot chosen")
    p("     5. the limits of 23e with the uncertainty budget recomputed for the supplier's instruments; the register's R-159, which still carries")
    p("        round 9's 45.88 K/W, is L4-E9's to restate from E11-29's row")
    p("     6. it stays NOT EXECUTABLE until the method and the limits are independently checked and a supplier agrees to the setup")
    p("   23g. SECTION 20c RESTATED ON MURATA'S PRINTED POINTS (record l9stk's round 4, fnd/l9stk2 at 43da41ca, its 15.5 copied to inputs/; RECORD, INFERRED)")
    p("     the PRF15BB103 prints 10 kOhm +-50 % at 25 C, 100 kOhm at a sensing temperature over 110 C (no upper bound) and 4.7 MOhm at 130 +-3 C;")
    p("       '47 kOhm at 130 C' is the 470 ohm groups' column (this record's own finding L4E11-R10-F3; record l8p's L8P-F07, OPEN). With board A's loads:")
    for r_ in S["ptc_rows"]:
        p("         RT1 %-40s BRK_VIN %4s V: DOCK_EN_RET %s V, board P's first inverter %s, board A reads the return %s%s"
          % (r_["lab"] + ",", fmt(r_["vin"], 1), fmt(r_["ret"], 3), r_["inv"], r_["a"], " and the loop powered" if r_["a"] == "held" and r_["powered"] else ""))
    p("     the first inverter with board A's loads: on while RT1 is under %s kOhm at %s V (%s kOhm at %s V), off from %s kOhm (%s kOhm) (nominal resistors,"
      % (fmt(S["inv_loaded"][0][1] / 1e3, 1), fmt(S["inv_loaded"][0][0], 1), fmt(S["inv_loaded"][1][1] / 1e3, 1), fmt(S["inv_loaded"][1][0], 1),
         fmt(S["inv_loaded"][0][2] / 1e3, 1), fmt(S["inv_loaded"][1][2] / 1e3, 1)))
    p("       the return's %s uA drawn; record l9stk reads %s and %s kOhm, %s and %s kOhm with its tolerances: a consistency check, not an input)"
      % (fmt(S20["tps"]["i_s_hi"] * 1e6, 0), fmt(S["l9_inv"][0], 1), fmt(S["l9_inv"][1], 1), fmt(S["l9_inv"][2], 1), fmt(S["l9_inv"][3], 1)))
    p("     WHAT NO LONGER STANDS: 20c's 'bound point (l9stk, %s V, RT1 47 kOhm)' and the %s / %s V read on it, and 20f's 'the return at least %s V"
      % (fmt(S9["pack_lo"], 1), "%.3f" % S["withdrawn"][0], "%.3f" % S["withdrawn"][1], "%.3f" % S["withdrawn"][1]))
    p("       ... with RT1 to its 47 kOhm, read closed with %s V to spare': 47 kOhm is not a point of this part, so they bound nothing in service; they"
      % fmt(S["withdrawn"][2], 3))
    p("       stay only as the loop's reading at one resistance. Between 25 C and 110 C the part prints only 'under 100 kOhm', where the first")
    p("       inverter at %s V is not defined: whether the guard stays closed in the 10 A and 18 A service is not printed (L8P-F07)" % fmt(S9["pack_lo"], 1))
    p("     WHAT STANDS: board A's own thresholds; board A reads the closed return as held only past %s kOhm at %s V (%s kOhm at %s V), after the guard's"
      % (fmt(S20["guard_rt1"][0][1] / 1e3, 0), fmt(S20["guard_rt1"][0][0], 1), fmt(S20["guard_rt1"][1][1] / 1e3, 0), fmt(S20["guard_rt1"][1][0], 1)))
    p("       own trip; the window's bound (%s kOhm) with its condition of 20l; and a tripped PTC (4.7 MOhm) holds the return low with the loop powered,"
      % fmt(S20["window_rt1"] / 1e3, 1))
    p("       so a guard trip already sets DD-7's inhibit")
    p("     THE GUARD RECORD l9stk SELECTED (a factory-set temperature switch, no trip under %s C, tripped from %s C, pulling the return, a fixed"
      % (fmt(S["switch"][0], 1), fmt(S["switch"][1], 1)))
    p("       15 kOhm in RT1's place; NOT DRAFTED, its draft record l8p's with this record): a trip pulls DOCK_EN_RET low while DOCK_EN_OUT stays")
    p("       powered, which is DD-7's trigger: the inhibit sets at the trip itself (within %s ms), holds at least %s s after the return rises and"
      % (fmt(S20["t_set"] * 1e3, 2), fmt(S20["hold_min"], 3)))
    p("       keeps until CELL+ reads alive: a thermal trip takes the breaker AND the battery FETs off. With the fixed 15 kOhm this record's loop reads:")
    for vin, o, r_ in S["sw_rows"]:
        p("         BRK_VIN %4s V: the pulled loop's DOCK_EN_OUT %s V (powered over %s V at most), the closed return %s V (closed over %s V)"
          % (fmt(vin, 1), fmt(o, 3), fmt(S20["out_rel"][1], 3), fmt(r_, 3), fmt(S20["ret_high"], 2)))
    p("       OWED READING, once the guard is drafted (this record with record l8p; nothing drafted or checked here): the switch's pulled level against")
    p("       %s V; the release against the hold and section 22's bleed, a trip being the hot bound itself; the kit's state through a trip with a"
      % fmt(S20["ret_low"], 4))
    p("       source present; the 30 uA the switch adds on DOCK_EN_OUT against U48's divider (INFERRED)")
    p("   23h. STATUS (SESSION): DELTA-02 answered in the record and in the procedure: the method selected, E11-29 restated on it, TP-E11-29 rewritten on")
    p("     it and NOT EXECUTABLE until independently checked and a supplier agrees; E11-29 stays CONDITIONAL on its measurement; nothing is built or measured;")
    p("     no circuit changed, so no netlist reading applies; 20c restated; the guard's reading on DD-7 OWED (RECORD)")
    p("")


# ---- round 14 (5 October 2026): the independent recheck V2R's findings on TP-E11-29 (C-PROT rev 1): V2R-B1, the fixture never isolated the
# heating supply; V2R-B2, two pass rules could pass a specimen over the limit; and the minors m1 and m3 to m7
R14_SW = dict(v_block=20.0,     # V: the series switch blocks the heating supply's open-circuit limit (the procedure's section 3) in either polarity
              leak_s=1e-6,      # A: the series switch's off-state leakage at v_block, either polarity, at the laboratory's temperature
              r_s=5e-3,         # ohm: the series switch's on-resistance
              c_s=2e-9,         # F: the series switch's off-state capacitance
              leak_drv=1e-6,    # A: each gate driver's open switch at 15 V
              n_drv_open=6,     # the drivers' open switches that span the pours during a reading (two a driver)
              r_dig=10e6,       # ohm: each digitiser input pair, at least
              c_fix=1e-9,       # F: the fixture's own capacitance across the pours besides the series switch (cables, digitiser, drivers)
              r_leg=5e-3,       # ohm: the dummy leg with SW_B closed
              r_loop_old=20e-3, # ohm: the old bypass loop (the supply's leads and the shunt), V2R's example, for the defect's reading only
              t_bypass=10e-6, t_gate=2e-6, t_first=1e-4, t_read=1e-2, t_gap=1.0)   # s: the reading's sequence (the procedure's step 7)
# SESSION proposals, the supplier's to meet with parts whose makers print these limits; none is selected here
R14_TERMS = dict(bias=0.5, early=0.5, pickup=0.1)   # K, SESSION proposals (V2R-m4, V2R-m3): the control run's bound on a bias-induced
                                                    # threshold shift, the early-time correction's own U, the pickup step's subtraction
R14_LEAD = dict(k_cu=390.0, area=4e-6, dx=0.02, frac=0.02)  # the heavy leads (V2R-m7): copper's conductivity, W/(m K) (a handbook value,
                                                    # ASSUMPTION); the cross-section (m2) and the thermocouples' spacing (m) proposed; the
                                                    # validity limit on a lead's heat flow, a fraction of the heated FET's power (SESSION)
R14_POUR_EX = 0.2e-3           # ohm: an ILLUSTRATION only of the pours' path resistance (no layout exists); the procedure measures it
R14_SEARCH = dict(seed=20261005, n=20000)           # the search: its seed and the matrices in each of its four families
R14_LIMIT = 150.0              # C, E-1's junction limit


def bar_at(m_, bar_even):
    """Section 21b's bar on (Zself + 2 Zmut) at the coupling ratio m: the even split's bar times 8 (1 - m)(1 + 2 m) / 9 under 1/4,
    the even split's own at or over it."""
    return bar_even * 8.0 * (1.0 - m_) * (1.0 + 2.0 * m_) / 9.0 if m_ < 0.25 else bar_even


def worst_row(z):
    """The exact worst-split figure of ONE junction from its own row of the measured matrix (round 14, V2R-B2): z holds the junction's rise per
    watt in each of the three FETs (its own Zself and the two Zmut into it). With each RDS(on) at most the allowance R (conductances x_i / R,
    x_i at least 1), the FETs' share of the junction's rise is I^2 R sum(z_i x_i) / (sum x_i)^2. For a fixed sum s the numerator is linear on
    a simplex whose vertices put all of s - 2 on one FET, so the largest coefficient C takes it and the other two (their sum D) stay at R;
    (C (s - 2) + D) / s^2 is then largest at s = 4 - 2 D / C while D < C / 2 (so s > 3), else at the even split s = 3. Returned as 9 times
    the rise over I^2 R, the figure the even-split bar judges: 9 C^2 / (4 (2 C - D)) while D < C / 2, else C + D. With C = Zself this is
    9 Zself / (8 (1 - m_k)) for m_k = D / (2 Zself) under 1/4: S_k against 21b's bar at the junction's OWN m_k, exactly. Also returns x, the
    hot FET's conductance over 1 / R at the worst split, and m_k."""
    c = max(z)
    d = sum(z) - c
    m_ = d / (2.0 * c) if c > 0 else 0.0
    if 2.0 * d < c:
        return 9.0 * c * c / (4.0 * (2.0 * c - d)), 2.0 - 2.0 * d / c, m_
    return c + d, 1.0, m_


def r14_lines(Z, B, z17, u, K, extra=(0.0, 0.0, 0.0)):
    """Round 14's pass lines on one specimen's readings. Z[k][j]: junction k's rise over step 6's baseline per watt in FET j; B[k]: junction
    k's baseline rise over the air (the band and the neighbours' dummies on); z17[k]: R17's coupling into junction k; u: the achieved expanded
    uncertainty as a fraction of each figure; extra[k]: the bounded additions of V2R-m7 (the pours' service loss and the leads), K. Line 1, the
    FETs' allocation: each junction's worst-split figure at its own m_k, plus U, at most the even-split bar. Line 2, the limit itself: the
    baseline, R17's coupling at its power, the matrix's worst-split rise and the additions, plus U, at most 150 C less the air. Line R17: the
    coupling plus U at most its limit. Returns (pass, line 1's figure, line 2's hottest rise, R17's largest coupling)."""
    zw = [worst_row(Z[k])[0] for k in range(3)]
    t = [B[k] + z17[k] * K["p17"] + K["p_even"] * zw[k] + extra[k] for k in range(3)]
    l1, l2, l3 = max(zw) * (1.0 + u), max(t) * (1.0 + u), max(z17) * (1.0 + u)
    return (l1 <= K["bar_even"] and l2 <= K["rise"] and l3 <= K["z17"]), l1, l2, l3


def r13_step14(Z, u, K):
    """TP-E11-29's step 14 as round 13 wrote it (V2R-B2 (b)): each S_k with its actual mutual terms against the bar at m = the largest Zmut
    over the largest Zself."""
    zs = max(Z[k][k] for k in range(3))
    zm = max(Z[k][j] for k in range(3) for j in range(3) if j != k)
    bar = bar_at(zm / zs, K["bar_even"])
    return all(sum(Z[k]) * (1.0 + u) <= bar for k in range(3))


def r11_record_rule(Z, u, K):
    """The record's rule as round 11 wrote it (21b, block E11-29): the largest Zself plus twice the largest Zmut into any junction against the
    bar at their ratio."""
    zs = max(Z[k][k] for k in range(3))
    zm = max(Z[k][j] for k in range(3) for j in range(3) if j != k)
    return (zs + 2.0 * zm) * (1.0 + u) <= bar_at(zm / zs, K["bar_even"])


def r13_direct(Z, B, z17, u, K):
    """Round 13's direct line (V2R-B2 (a)): the split imposed at m = 0 (1.513 W in one, 0.756 W in each other, each FET hot in turn) with R17,
    the band and the dummies on, the hottest junction plus U at most 150 C less the air."""
    ph, po = K["p_hot0"], K["p_oth0"]
    worst = 0.0
    for h in range(3):
        p_ = [ph if j == h else po for j in range(3)]
        worst = max(worst, max(B[k] + z17[k] * K["p17"] + sum(Z[k][j] * p_[j] for j in range(3)) for k in range(3)))
    return worst * (1.0 + u) <= K["rise"], worst


def tj_exact(Z, B, z17, K):
    """The exact worst-split hottest junction (C) of a specimen whose TRUE matrix, baseline and coupling are given."""
    return K["t0"] + max(B[k] + z17[k] * K["p17"] + K["p_even"] * worst_row(Z[k])[0] for k in range(3))


def inv3(a):
    d = (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
         + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))
    c = [[a[1][1] * a[2][2] - a[1][2] * a[2][1], a[0][2] * a[2][1] - a[0][1] * a[2][2], a[0][1] * a[1][2] - a[0][2] * a[1][1]],
         [a[1][2] * a[2][0] - a[1][0] * a[2][2], a[0][0] * a[2][2] - a[0][2] * a[2][0], a[0][2] * a[1][0] - a[0][0] * a[1][2]],
         [a[1][0] * a[2][1] - a[1][1] * a[2][0], a[0][1] * a[2][0] - a[0][0] * a[2][1], a[0][0] * a[1][1] - a[0][1] * a[1][0]]]
    return [[c[i][j] / d for j in range(3)] for i in range(3)]


def r14_matrix(rnd, fam):
    """One random thermal matrix of a family: "net", a passive network of three nodes, each to the air and to each other, conductances drawn
    log-uniform (the Kron reduction of any linear conduction network onto three junctions is of this form, so these are the physical
    matrices: symmetric, positive, each mutual under both selfs); "row", three side by side, the ends joined only through the middle;
    "sym", V2R's kind, symmetric with each self 5 to 50 K/W and each mutual up to the smaller self; "free", NOT physical (asymmetric, a
    mutual up to 1.5 times its junction's self), for the rule's robustness only (check V2's reciprocity would refuse it)."""
    lu = lambda a, b: 10.0 ** rnd.uniform(a, b)
    if fam in ("net", "row"):
        ga = [lu(-2.0, -0.6) for _ in range(3)]
        g12, g23 = lu(-3.0, 0.3), lu(-3.0, 0.3)
        g13 = 0.0 if fam == "row" else (lu(-3.0, 0.3) if rnd.random() > 0.1 else 0.0)
        G = [[ga[0] + g12 + g13, -g12, -g13], [-g12, ga[1] + g12 + g23, -g23], [-g13, -g23, ga[2] + g13 + g23]]
        return inv3(G)
    zs = [rnd.uniform(5.0, 50.0) for _ in range(3)]
    if fam == "sym":
        z = [[zs[i] if i == j else 0.0 for j in range(3)] for i in range(3)]
        for i, j in ((0, 1), (0, 2), (1, 2)):
            z[i][j] = z[j][i] = rnd.uniform(0.0, 1.0) * min(zs[i], zs[j])
        return z
    return [[zs[i] if i == j else rnd.uniform(0.0, 1.5) * zs[i] for j in range(3)] for i in range(3)]


def r14_search(K, u, seed, n):
    """The proof by search of round 14's pass rule (V2R-B2): over n random thermal matrices in each of four families, each scaled so that its
    worst-split figure lies near the even-split bar, with a baseline of 0 to 20 K and R17's coupling 0 to 1.2 K/W per junction, the
    readings perturbed within the achieved uncertainty (each reading the truth over 1 + d, |d| at most u), the rule accepts NONE whose exact
    worst-split hottest junction exceeds 150 C. Round 13's step 14 and its direct line are counted on exact readings, as V2R counted them,
    against the FETs' allocation and against the limit; the record's own rule as written (round 11) the same."""
    import random
    rnd = random.Random(seed)
    c = dict(n=0, new_acc=0, new_over=0, new0_acc=0, new0_over=0, new0_miss=0, s14_acc=0, s14_over=0, s14_worst=0.0, rec_acc=0, rec_over=0,
             old_acc=0, old_over=0, old_worst=0.0, fam={})
    for fam in ("net", "row", "sym", "free"):
        cf = dict(n=0, new_acc=0, new_over=0, s14_acc=0, s14_over=0)
        for _ in range(n):
            Z = r14_matrix(rnd, fam)
            zw = max(worst_row(Z[k])[0] for k in range(3))
            sc = rnd.uniform(0.80, 1.15) * K["bar_even"] / zw
            Z = [[x * sc for x in r_] for r_ in Z]
            B = [rnd.uniform(0.0, 20.0) for _ in range(3)]
            z17 = [rnd.uniform(0.0, 1.2) for _ in range(3)]
            tj = tj_exact(Z, B, z17, K)
            over = tj > R14_LIMIT + 1e-9
            alloc_over = max(worst_row(Z[k])[0] for k in range(3)) > K["bar_even"] * (1 + 1e-12)
            per = lambda v: v / (1.0 + rnd.uniform(-u, u))
            Zr = [[per(x) for x in r_] for r_ in Z]
            ok = r14_lines(Zr, [per(b) for b in B], [per(z) for z in z17], u, K)[0]
            c["n"] += 1
            cf["n"] += 1
            if ok:
                c["new_acc"] += 1
                cf["new_acc"] += 1
                if over:
                    c["new_over"] += 1
                    cf["new_over"] += 1
            ok0 = r14_lines(Z, B, z17, 0.0, K)[0]
            if ok0:
                c["new0_acc"] += 1
                c["new0_over"] += over
            elif not over and not alloc_over and max(z17) <= K["z17"]:
                c["new0_miss"] += 1                 # meets the limit and both allocations, yet refused: the rule would be more than exact
            if fam == "free":
                continue
            if r13_step14(Z, 0.0, K):
                c["s14_acc"] += 1
                cf["s14_acc"] += 1
                if alloc_over:
                    c["s14_over"] += 1
                    cf["s14_over"] += 1
                    c["s14_worst"] = max(c["s14_worst"], max(worst_row(Z[k])[0] for k in range(3)) / K["bar_even"] - 1.0)
            if r11_record_rule(Z, 0.0, K):
                c["rec_acc"] += 1
                c["rec_over"] += alloc_over
            if r13_step14(Z, 0.0, K) and r13_direct(Z, B, z17, 0.0, K)[0] and max(z17) <= K["z17"]:
                c["old_acc"] += 1
                if over:
                    c["old_over"] += 1
                    c["old_worst"] = max(c["old_worst"], tj)
        c["fam"][fam] = cf
    return c


# the fixture as drawn (round 13) and as redrawn (round 14): each element (name, node, node, what it is, the states in which it is CLOSED);
# nodes: VB the VBAT pour (the three sources), CQ the CH_BATQ pour (the three drains), HP and HN the heating supply's terminals, CF CELL_FUSED
# (R17's far end); an element that is not closed in a state is open and carries at most its leakage. FET k is the device under test.
R14_FIXTURES = {
    "old": [("the heating supply's + lead", "HP", "VB", "lead", ("calibration", "heating", "sensing")),
            ("the shunt and the - lead", "CQ", "HN", "lead", ("calibration", "heating", "sensing")),
            ("the bypass switch across the heating supply", "HP", "HN", "switch", ("calibration", "sensing")),
            ("R17 with its own floating supply", "CQ", "CF", "lead", ("calibration", "heating", "sensing"))],
    "new": [("the series switch SW_S in the heating supply's + lead", "HP", "VB", "switch", ("heating",)),
            ("the shunt and the - lead", "CQ", "HN", "lead", ("calibration", "heating", "sensing")),
            ("the bypass SW_B onto the dummy leg, on the supply's side of SW_S", "HP", "HN", "switch", ("calibration", "sensing")),
            ("R17 with its own floating supply", "CQ", "CF", "lead", ("calibration", "heating", "sensing"))],
}


def r14_state(fix, state):
    """Whether, in a state, closed elements join the VBAT pour to the CH_BATQ pour outside the three FETs (a search over the closed elements'
    nodes); the elements of that path if so, else every closed element."""
    edges = [(name, a, b) for name, a, b, _kind, closed in R14_FIXTURES[fix] if state in closed]
    seen, todo = {"VB": []}, ["VB"]
    while todo:
        n = todo.pop(0)
        for name, a, b in edges:
            for x, y in ((a, b), (b, a)):
                if x == n and y not in seen:
                    seen[y] = seen[n] + [name]
                    todo.append(y)
    if "CQ" in seen:
        return True, seen["CQ"]
    return False, [name for name, _a, _b in edges]


def fix24_round(R, T):
    """Round 14: the recheck V2R's V2R-B1 (the fixture: the heating supply isolated by a series switch, the sequence, each state's current
    paths with their margins on the maker's printed figures), V2R-B2 (the pass lines at the worst split for the measured matrix, judged
    with the baseline; step 14 replaced by each junction's own m_k; the replacement proved by a search), the budget with V2R-m4's terms, the
    leads and the pours of V2R-m7, and the minors' figures."""
    S9, S21, S22, S23, L = R["S19"], R["S21"], R["S22"], R["S23"], R["L"]
    S = {}
    i_, ra = S9["i"], S21["ra"]
    i2r = i_ ** 2 * ra
    K = dict(bar_even=S21["bar_old"], p_even=S23["p"]["even"], p17=S9["pr17"], z17=S9["r17_allow"], rise=S23["rise_total"], t0=S9["t0"],
             p_hot0=S23["p"]["hot"], p_oth0=S23["p"]["other"], i2r=i2r)
    S["K"] = K
    # ---- the maker's rows this round reads (Nexperia BUK6Y10-30P, 17 April 2020, Table 7 p.6 and Table 5 p.3)
    pg, m = find("buk6y10", r"IDSS drain leakage current VDS = -30 V; VGS = 0 V; Tj = 25 °C - - -(\d+) µA VDS = -30 V; VGS = 0 V; Tj = 125 °C - - -(\d+) µA VGS = -20 V; VDS = 0 V; Tj = 25 °C - - -(\d+) nA",
                 "IDSS and IGSS")
    S["leak_p"], S["idss"], S["igss"] = pg, (f(m, 1) * 1e-6, f(m, 2) * 1e-6), f(m, 3) * 1e-9
    if abs(3 * S["idss"][1] - S22["bat"][1]) > 1e-12:
        refuse(4, "the IDSS row read here is not round 12's")
    S["vgs_abs"] = f(find("buk6y10", r"VGS gate-source voltage -(\d+) \d+ V", "VGS's limit")[1])
    vth_min, vth_max = S23["vth"][1], S23["vth"][3]
    i_m = R13_B["i_m"]
    # ---- V2R-B1: the old fixture reproduced, the new one in each state
    S["old"] = {st: r14_state("old", st) for st in ("calibration", "heating", "sensing")}
    S["new"] = {st: r14_state("new", st) for st in ("calibration", "heating", "sensing")}
    if not (S["old"]["sensing"][0] and S["old"]["calibration"][0]):
        refuse(4, "V2R-B1 is not reproduced: the old fixture's sensing state shows no path joining the pours")
    if S["new"]["sensing"][0] or S["new"]["calibration"][0] or S["new"]["heating"][0]:
        refuse(4, "the redrawn fixture joins the pours outside the FETs in a state: %s" % {k: v for k, v in S["new"].items() if v[0]})
    S["old_v"] = i_m * R14_SW["r_loop_old"]                       # the pours' voltage with the sense current in the old bypass loop
    S["clamp_p"] = (S23["i_td"][0][0] * vth_min, 13.8 * 3.5)       # the clamp: the whole heating current through a diode-connected FET
    # the sensing (and calibration) state: every conductor across the pours but the device under test, each with its bound
    lk = [("the two off FETs, IDSS at 125 C (printed, at VDS -30 V)", 2 * S["idss"][1], "MAKER"),
          ("the device under test's gate on its drain, IGSS at 25 C (printed, at 20 V)", S["igss"], "MAKER"),
          ("the series switch SW_S open", R14_SW["leak_s"], "PROPOSAL"),
          ("the gate drivers' open switches (%d)" % R14_SW["n_drv_open"], R14_SW["n_drv_open"] * R14_SW["leak_drv"], "PROPOSAL"),
          ("the three digitiser inputs at the threshold's largest 25 C row", 3 * vth_max / R14_SW["r_dig"], "PROPOSAL")]
    S["sense_leaks"] = lk
    S["sense_sum"] = sum(x for _l, x, _c in lk)
    S["sense_frac"] = S["sense_sum"] / i_m
    S["sense_ratio"] = i_m / max([S["idss"][1]] + [x for _l, x, _c in lk[1:]])   # against the largest single other conductor
    S["fixture_frac"] = sum(x for _l, x, c_ in lk if c_ == "PROPOSAL") / i_m
    # the heating state: the device under test fully on; the others
    S["vds_heat"] = (math.sqrt(S23["p"]["hot"] * S23["r_typ"]), math.sqrt(S23["slot_w"][0] * ra))   # the heated FET's VDS: the least and the most
    hk = [("the two off FETs, IDSS at 125 C", 2 * S["idss"][1]), ("the gate drivers' open switches", R14_SW["n_drv_open"] * R14_SW["leak_drv"]),
          ("the digitiser inputs at the largest heating VDS", 3 * S["vds_heat"][1] / R14_SW["r_dig"])]
    S["heat_leaks"] = hk
    S["heat_min_i"] = S23["i_single"][0]                           # the least heating current (one FET alone at the worst split's power)
    S["heat_ratio"] = S["heat_min_i"] / sum(x for _l, x in hk)
    S["sense_in_power"] = i_m / S["heat_min_i"]                    # the sense current's share of the conducting FET's current, so of its power
    S["v_sw_open"] = vth_max + S23["i_td"][0][1] * R14_SW["r_leg"]  # the most across SW_S open in a reading: the threshold and the dummy leg's drop
    # the settling before the first sample: the pours' node moved by the sense current alone
    S["c_node"] = 3 * L["ciss_0"] + R14_SW["c_s"] + R14_SW["c_fix"]
    S["t_settle"] = S["c_node"] * vth_max / i_m
    S["settle_margin"] = R14_SW["t_first"] / S["t_settle"]
    S["duty_lost"] = (R14_SW["t_bypass"] + R14_SW["t_gate"] + R14_SW["t_read"]) / R14_SW["t_gap"]
    if not (S["sense_frac"] < 0.05 and S["heat_ratio"] > 1e4 and S["settle_margin"] > 1.5 and S["v_sw_open"] < R14_SW["v_block"]):
        refuse(4, "the redrawn fixture does not leave the device under test alone in a state, or its reading does not settle")
    # ---- V2R-B2 (a): the imposed split against the worst split for the measured m; V2R's example
    S["imposed_short"] = [(m_, 1.0 - split_share(2.0, m_) / max(worst_share(m_)[0], 1.0)) for m_ in (0.0, 0.25, 0.5, 0.8)]
    ex = dict(zs=20.0, zm=12.0, z17=1.0, b=14.0)
    Zx = [[ex["zs"] if i == j else ex["zm"] for j in range(3)] for i in range(3)]
    S["ex"] = dict(ex, S=ex["zs"] + 2 * ex["zm"], case_f=r13_direct(Zx, [ex["b"]] * 3, [ex["z17"]] * 3, 0.0, K)[1],
                   even=ex["b"] + ex["z17"] * K["p17"] + K["p_even"] * (ex["zs"] + 2 * ex["zm"]),
                   tj=tj_exact(Zx, [ex["b"]] * 3, [ex["z17"]] * 3, K), new=r14_lines(Zx, [ex["b"]] * 3, [ex["z17"]] * 3, 0.0, K))
    if not (r13_step14(Zx, 0.0, K) and r13_direct(Zx, [ex["b"]] * 3, [ex["z17"]] * 3, 0.0, K)[0] and S["ex"]["tj"] > R14_LIMIT and not S["ex"]["new"][0]):
        refuse(4, "V2R's example is not reproduced (round 13's lines pass it over the limit) or round 14's lines pass it")
    # ---- the budget with V2R-m4's terms (the reading plus the achieved U is the rule; the figures below illustrate the record's proposal)
    rise = S23["rise_bar"]
    S["terms"] = S23["terms"]["B"] + [("a bias-induced threshold shift, bounded by the control run, %s K" % fmt(R14_TERMS["bias"], 1), R14_TERMS["bias"] / rise),
                                      ("the early-time correction's own uncertainty, %s K" % fmt(R14_TERMS["early"], 1), R14_TERMS["early"] / rise),
                                      ("the pickup step's subtraction, %s K" % fmt(R14_TERMS["pickup"], 1), R14_TERMS["pickup"] / rise)]
    S["u"] = math.sqrt(sum(x * x for _l, x in S["terms"]))
    S["pass_bar"] = S21["bar_new"] / (1 + S["u"])
    S["pass_even"] = K["bar_even"] / (1 + S["u"])
    S["pass_rise"] = K["rise"] / (1 + S["u"])
    # ---- the search (V2R-B2 (b)), at the budget's U with perturbed readings, and exact
    S["search"] = r14_search(K, S["u"], R14_SEARCH["seed"], R14_SEARCH["n"])
    sr = S["search"]
    if sr["new_over"] or sr["new0_over"] or sr["new0_miss"] or sr["rec_over"] or not sr["s14_over"] or not sr["old_over"]:
        refuse(4, "the search does not prove round 14's rule, or does not show round 13's lines failing: %s" % {k: v for k, v in sr.items() if k != "fam"})
    # ---- V2R-m7: the heavy leads and the pours
    ld = R14_LEAD
    S["lead_q"] = ld["frac"] * S23["p"]["hot"]
    S["lead_dt"] = S["lead_q"] * ld["dx"] / (ld["k_cu"] * ld["area"])
    S["lead_loss"] = S23["i_td"][0][1] ** 2 * 1.72e-8 / ld["area"]   # W/m in the lead at the largest heating current (copper at 20 C, ASSUMPTION)
    S["pour_service"] = i_ ** 2 * R14_POUR_EX                         # an illustration only: the pours' service loss at 0.2 mOhm
    S["pour_test"] = (S23["i_td"][0][0] ** 2 * R14_POUR_EX, S23["i_td"][0][1] ** 2 * R14_POUR_EX)
    S["pour_frac"] = ((S23["i_td"][0][0] / i_) ** 2, (S23["i_td"][0][1] / i_) ** 2)
    S["pour_term"] = S21["bar_new"] * S["pour_service"]                # its bound at a Zself of the bar, for scale (INFERRED)
    # ---- V2R-m3: a gate tie away from tap Dk
    S["tie_mv"] = 0.1e-3 * i_ * 1e3
    # ---- V2R-m6: what joins the pours on board A as drafted
    S["m6_c"] = 180e-6 * 104e-6 / (180e-6 + 104e-6)
    S["m6_dv"] = i_m * 0.2 / S["m6_c"]
    # ---- V2R-m1: one set of figures (R256 at -1 %, section 22c)
    S["m1"] = (S22["sel"]["sink"]["run"], S22["sel"]["sink"]["ovp"], S22["sel"]["sink"]["clamp"])
    return S


def render_fix24(R, p):
    S, S9, S21, S23 = R["S24"], R["S19"], R["S21"], R["S23"]
    K, sr = S["K"], S["search"]
    sw = R14_SW
    p("24. ROUND 14: THE RECHECK V2R'S FINDINGS ON TP-E11-29'S FIXTURE AND PASS RULES (5 October 2026; C-PROT rev 1; the first negative check of both)")
    p("   24a. V2R-B1 REPRODUCED: THE FIXTURE AS ROUND 13 DREW IT NEVER ISOLATES THE HEATING SUPPLY (INFERRED; MAKER rows)")
    for st in ("calibration", "heating", "sensing"):
        j, used = S["old"][st]
        p("     %-11s %s" % (st + ":", ("the pours JOINED outside the FETs through: %s" % "; ".join(used)) if j else "the pours apart outside the FETs"))
    p("     in sensing the %s mA sense current takes the bypass loop: %s uV across the pours (V2R's %s mOhm loop), where the threshold connection needs"
      % (fmt(R13_B["i_m"] * 1e3, 0), fmt(S["old_v"] * 1e6, 0), fmt(sw["r_loop_old"] * 1e3, 0)))
    p("       %s to %s V at 25 C (Table 7, p.%d): no FET reaches it, in sensing or calibration; 'or the supply is clamped' (23f) puts the whole heating"
      % (fmt(S23["vth"][1], 1), fmt(S23["vth"][3], 0), S23["vth_p"]))
    p("       current through the diode-connected FET: at least %s W at %s A over the threshold's least printed row (V2R reads Fig. 9: about 3.5 V,"
      % (fmt(S["clamp_p"][0], 1), fmt(S23["i_td"][0][0], 2)))
    p("       %s W at 13.8 A, typical, by eye). Both WITHDRAWN" % fmt(S["clamp_p"][1], 0))
    p("   24b. THE FIXTURE REDRAWN (SESSION): a series switch SW_S in the heating supply's + lead, the bypass SW_B onto a dummy leg on the supply's side")
    for st in ("calibration", "heating", "sensing"):
        j, used = S["new"][st]
        p("     %-11s %s; closed: %s" % (st + ":", "JOINED" if j else "the pours apart outside the FETs", "; ".join(used)))
    p("     the reading's sequence (proposal; times from SW_B's closing): SW_B closes; %s us later SW_S opens (t = 0, read on the shunt: the coupon's"
      % fmt(sw["t_bypass"] * 1e6, 0))
    p("       current falls to the sense current); %s us later gate k leaves its driver's -10 V output and is tied to tap Dk (interlocked: only with the"
      % fmt(sw["t_gate"] * 1e6, 0))
    p("       shunt under 10 mA); samples from %s us to %s ms; then the gate back to -10 V, SW_S closes, SW_B opens; one reading in %s s, so the"
      % (fmt(sw["t_first"] * 1e6, 0), fmt(sw["t_read"] * 1e3, 0), fmt(sw["t_gap"], 0)))
    p("       heating is off %s %% of the time and each power is averaged over the whole cycle; through every step the device under test's channel is"
      % fmt(S["duty_lost"] * 100, 2))
    p("       the only one conducting between the pours (its gate stays 10 V under VBAT until SW_S is open); in the %s us between SW_B's closing and"
      % fmt(sw["t_bypass"] * 1e6, 0))
    p("       SW_S's opening the current divides between the dummy leg and the coupon by their resistances, SW_S's on-resistance among them: those")
    p("       microseconds and the switch's own opening enter the early-time correction's term (24f), and t = 0 is SW_S's opening on the shunt")
    p("     SENSING AND CALIBRATION (the same connection): the device under test carries the %s mA; every other conductor across the pours:"
      % fmt(R13_B["i_m"] * 1e3, 0))
    for lab, x, c_ in S["sense_leaks"]:
        p("       %s: at most %s uA (%s)" % (lab, fmt(x * 1e6, 2), c_))
    p("       in all at most %s uA, %s %% of the sense current: the device under test carries at least %s %% of it, %s times the largest other"
      % (fmt(S["sense_sum"] * 1e6, 2), fmt(S["sense_frac"] * 100, 2), fmt(100 - S["sense_frac"] * 100, 2), fmt(S["sense_ratio"], 0)))
    p("       (Nexperia BUK6Y10-30P, 17 April 2020, Table 7 p.%d: IDSS %s uA at 25 C and %s uA at 125 C, IGSS %s nA; nothing printed over 125 C: check V3"
      % (S["leak_p"], fmt(S["idss"][0] * 1e6, 0), fmt(S["idss"][1] * 1e6, 0), fmt(S["igss"] * 1e9, 0)))
    p("       reads it). The fixture's part, %s %%, sits outside the chamber and the oven at the laboratory's temperature, the same in calibration and in a"
      % fmt(S["fixture_frac"] * 100, 2))
    p("       reading: it moves both alike (V3 reads it before and after the runs). The open SW_S sees at most %s V (the threshold's largest row and the"
      % fmt(S["v_sw_open"], 2))
    p("       dummy leg's drop) against its %s V; its body diode or any one-way element would conduct, so SW_S blocks both polarities (two MOSFETs"
      % fmt(sw["v_block"], 0))
    p("       source to source, or a relay; proposal)")
    p("     HEATING: the device under test carries %s to %s A at %s to %s V; the two off FETs see VGS 0 and VDS of that sign, their body diodes reverse-"
      % (fmt(S["heat_min_i"], 2), fmt(S23["i_td"][0][1], 2), fmt(S["vds_heat"][0], 3), fmt(S["vds_heat"][1], 3)))
    p("       biased; every other conductor at most %s uA: the device under test carries %s times the rest at the least heating current; the sense"
      % (fmt(sum(x for _l, x in S["heat_leaks"]) * 1e6, 2), "%.1e" % S["heat_ratio"]))
    p("       current flows in the conducting channel too, %s %% of its power (counted); the shunt and the taps sit inside SW_S, so its on-resistance"
      % fmt(S["sense_in_power"] * 100, 3))
    p("       is not in any power: it enters the supply's compliance only, logged (validity check V7)")
    p("     the settling before the first sample: the pours' node moves on the sense current alone across %s nF (three Ciss near 0 V, typical, %s nF each;"
      % (fmt(S["c_node"] * 1e9, 2), fmt(R["L"]["ciss_0"] * 1e9, 2)))
    p("       SW_S open %s nF and the fixture's %s nF, proposals): %s us to the threshold's largest row, %s times inside the first sample at %s us; the"
      % (fmt(sw["c_s"] * 1e9, 0), fmt(sw["c_fix"] * 1e9, 0), fmt(S["t_settle"] * 1e6, 1), fmt(S["settle_margin"], 2), fmt(sw["t_first"] * 1e6, 0)))
    p("       control run (V2R-m4) reads it on the specimen")
    p("     the gates: VGS within +-%s V (Table 5); the drivers clamped inside +-15 V (proposal); a gate is never left floating" % fmt(S["vgs_abs"], 0))
    p("   24c. V2R-B2 (a) REPRODUCED: THE IMPOSED SPLIT IS THE WORST ONLY AT m = 0, AND NOTHING JUDGED THE BASELINE (INFERRED)")
    for m_, sh in S["imposed_short"]:
        p("     m %s: the imposed split (x = 2) reads %s %% under the worst split's FET rise" % (fmt(m_, 2), fmt(sh * 100, 1)))
    e = S["ex"]
    p("     V2R's example: Zself %s, Zmut %s K/W (m %s, S %s), R17 %s K/W, the baseline %s K: round 13's case F reads %s K and passes; the even split,"
      % (fmt(e["zs"], 0), fmt(e["zm"], 0), fmt(e["zm"] / e["zs"], 1), fmt(e["S"], 1), fmt(e["z17"], 0), fmt(e["b"], 0), fmt(e["case_f"], 1)))
    p("       which is the worst split at that m, reads %s K: %s C, every round 13 line passed; round 14's line 2 reads %s K and FAILS"
      % (fmt(e["even"], 1), fmt(e["tj"], 1), fmt(e["new"][2], 1)))
    p("   24d. THE PASS LINES RESTATED (SESSION; INFERRED): each junction judged at the split worst for its OWN measured row, the baseline with it")
    p("     the matrix: Z[k][j] = junction k's rise over step 6's baseline per watt in FET j (cases A to C); in junction k's row C_k is the largest term")
    p("       (Zself,k in any physical reading) and D_k the sum of the other two; m_k = D_k / (2 C_k); the worst-split figure Zw_k = 9 C_k^2 / (4 (2 C_k")
    p("       - D_k)) while m_k is under 1/4, else C_k + D_k; the hot FET's share at that split x_k = 2 - 4 m_k (the even split from 1/4): P_hot =")
    p("       I^2 R x / (x + 2)^2, each other I^2 R / (x + 2)^2, I^2 R = %s W (23.93 A at the %s mOhm allowance). Zw_k at most %s K/W is S_k at most"
      % (fmt(K["i2r"], 3), fmt(S21["ra"] * 1e3, 3), "%.2f" % K["bar_even"]))
    p("       21b's bar at the junction's own m_k, exactly (the closed form is checked against a scan of every split in test_l4e11)")
    p("     line 1 (the FETs' allocation): the largest Zw_k plus its U at most %s K/W (without m: each S_k plus U at most %s K/W, safe as it stands)"
      % ("%.2f" % K["bar_even"], "%.2f" % S21["bar_new"]))
    p("     line 2 (THE LIMIT, by superposition): for each junction B_k + R17's coupling x %s W + %s W x Zw_k + the pours' and the leads' bounds"
      % (fmt(K["p17"], 2), fmt(K["p_even"], 4)))
    p("       (24f), plus U, at most %s K over the air (150 C from %s C)" % (fmt(K["rise"], 2), fmt(K["t0"], 2)))
    p("     line 3 (direct): case F for each FET hot in turn at its own row's worst split, R17, the band and the dummies on: the hottest junction plus U")
    p("       at most %s K; round 13's fixed split 1.513 / 0.756 / 0.756 W stays as cases W (m = 0) for the linearity check V4" % fmt(K["rise"], 2))
    p("     line R17: the largest coupling plus U at most %s K/W; the pair's fallback and RT1's land as before" % fmt(K["z17"], 0))
    p("     step 14's bar at m = the largest Zmut over the largest Zself is WITHDRAWN (V2R-B2 (b)); the record's own rule (the largest Zself plus twice")
    p("       the largest Zmut at their ratio) is safe and looser than needed; each line is the reading plus the achieved U, never a fixed figure")
    p("   24e. THE PROOF BY SEARCH (seed %d, %d matrices in each of four families; the readings perturbed within U = %s %%; INFERRED)"
      % (R14_SEARCH["seed"], R14_SEARCH["n"], fmt(S["u"] * 100, 2)))
    for fam in ("net", "row", "sym", "free"):
        cf = sr["fam"][fam]
        p("     %-5s %d: round 14 accepts %d, of which over 150 C: %d%s" % (fam, cf["n"], cf["new_acc"], cf["new_over"],
                                                                         "" if fam == "free" else "; round 13's step 14 accepts %d, over the allocation %d" % (cf["s14_acc"], cf["s14_over"])))
    p("     round 14's lines with the readings exact and U 0: accept %d, over 150 C %d; refused while meeting the limit and both allocations: %d"
      % (sr["new0_acc"], sr["new0_over"], sr["new0_miss"]))
    p("     round 13's step 14 (exact readings): accepts %d, of which %d exceed the FETs' allocation at the exact worst split, by up to %s %%"
      % (sr["s14_acc"], sr["s14_over"], fmt(sr["s14_worst"] * 100, 1)))
    p("     round 13's lines together (step 14, the direct line at m = 0, R17): accept %d, of which %d exceed 150 C, the hottest %s C"
      % (sr["old_acc"], sr["old_over"], fmt(sr["old_worst"], 1)))
    p("     the record's own rule as written (round 11): accepts %d, of which over the allocation %d" % (sr["rec_acc"], sr["rec_over"]))
    p("   24f. THE BUDGET, THE LEADS AND THE POURS (V2R-m4, V2R-m7; SESSION proposals; INFERRED)")
    for lab, x in S["terms"]:
        p("     %s: %s %%" % (lab, fmt(x * 100, 2)))
    p("     in all %s %% on the %s K rise at the bar: as an illustration, a reading of %s K/W or under passes %s K/W, %s against %s K/W, and line 2 at"
      % (fmt(S["u"] * 100, 2), fmt(S23["rise_bar"], 2), "%.2f" % S["pass_bar"], "%.2f" % S21["bar_new"], "%.2f" % S["pass_even"], "%.2f" % K["bar_even"]))
    p("       %s K or under against %s K; the rule is the reading plus the supplier's ACHIEVED U" % (fmt(S["pass_rise"], 2), fmt(K["rise"], 2)))
    ld = R14_LEAD
    p("     the heavy leads: each heating lead at least %s mm2 (proposal), joined where board A's own current joins its pour, two insulated thermocouples"
      % fmt(ld["area"] * 1e6, 0))
    p("       %s mm apart near its joint: the heat it carries q = k A dT / dx; at %s %% of the hot FET's %s W, %s W, dT reads %s K; a lead over that is"
      % (fmt(ld["dx"] * 1e3, 0), fmt(ld["frac"] * 100, 0), fmt(S23["p"]["hot"], 3), fmt(S["lead_q"], 3), fmt(S["lead_dt"], 2)))
    p("       redone (validity check V8), and the heat leaving through any heavy lead, times TWICE the junction's own Zself, is added to lines 2 and")
    p("       3: removing a lead that carries q from its joint raises junction k by q times the joint-to-junction impedance of the coupon without")
    p("       the lead, at most Zself,k / (1 - g Z_jj) by reciprocity and the maximum principle (g the lead's conductance, Z_jj the joint's own")
    p("       impedance); the factor is taken at 2, an ASSUMPTION that a lead takes at most half of any heat put in at its joint; the lead's own")
    p("       loss %s W/m at %s A" % (fmt(S["lead_loss"], 2), fmt(S23["i_td"][0][1], 2)))
    p("     the pours: the heating cases carry %s to %s of the service's loss in the pours' shared copper (V2R's third); line 2 adds the pours' service"
      % (fmt(S["pour_frac"][0], 3), fmt(S["pour_frac"][1], 3)))
    p("       loss, at most (23.93 A)^2 times the sum of the two pours' largest path resistances (each pour read four-wire from its heavy lead's")
    p("       joint to each FET's tap on it), times the junction's own Zself, crediting nothing for the share the cases already carry; for scale, at an")
    p("       ASSUMED %s mOhm path: %s W, %s K at a Zself of %s K/W" % (fmt(R14_POUR_EX * 1e3, 1), fmt(S["pour_service"], 3), fmt(S["pour_term"], 2), "%.2f" % S21["bar_new"]))
    p("   24g. THE MINORS (RECORD, INFERRED)")
    p("     m1: 20g now prints section 22c's set (R256 at -1 %%): %s mA with the breaker restarted, %s mA at SYSOVP, %s mA at the clamp; 21d's row"
      % (fmt(S["m1"][0] * 1e3, 2), fmt(S["m1"][1] * 1e3, 2), fmt(S["m1"][2] * 1e3, 2)))
    p("       'R256 6.8 kOhm' marked SUPERSEDED by round 12")
    p("     m3: gate k is tied at tap Dk's own line and the reading is V(tap Sk, tap Dk), the gate's VGS: a tie elsewhere on the pour adds its drop,")
    p("       0.1 mOhm x %s A = %s mV; the pickup step of step 6 is subtracted, its %s K in the budget" % (fmt(S9["i"], 2), fmt(S["tie_mv"], 1), fmt(R14_TERMS["pickup"], 1)))
    p("     m4: the control run C0 (the gate driven as in a run, SW_S open, the coupon isothermal in the oven at the top temperature, read in the same")
    p("       window) bounds a bias-induced shift and the settling; the early-time correction gets its own term; the row keeps the reading plus U")
    p("     m5: step 14's rise is the rise over step 6's baseline")
    p("     m6: on board A as drafted C236 and CELL_FUSED's 104 uF are %s uF in series across the sensed node: 1 mA moves it %s V in 0.2 s; the first"
      % (fmt(S["m6_c"] * 1e6, 1), fmt(S["m6_dv"], 2)))
    p("       prototype is a specimen only with its gate links AND populated as the coupon is (no part with a terminal on VBAT, CH_BATQ or CELL_FUSED")
    p("       but the three FETs and R17; the neighbours as insulated dummies), V3 passing; the coupon: no capacitor, load or dummy on either pour")
    p("     m7: the leads and the pours, 24f")
    p("   24h. STATUS (SESSION): V2R-B1 and V2R-B2 CORRECTED on the desk; TP-E11-29 NOT EXECUTABLE until the recheck of this fixture and these pass")
    p("     rules, the limits agreed and a supplier's agreement; a second negative check of either correction ends that loop; nothing built or measured")
    p("")


# ---- round 15 (5 October 2026): the final recheck V2RF's V2RF-B1 (the heavy leads) and its minors m1 to m5 (C-PROT rev 1)
R15_LEAD = dict(hp=(0.15, 0.25),   # W/(m K): h times perimeter of a 4 mm2 insulated lead in still air, V2RF's order (ASSUMPTION here)
                k_cu=390.0,        # W/(m K): copper, a handbook value (ASSUMPTION, as round 14)
                area=4e-6,         # m2: the lead (proposal)
                dx=0.03,           # m: the guard's thermocouple pair, under the guard's heater (proposal)
                dt0=0.05,          # K: the pair's offset left after its isothermal reading in the oven (proposal)
                dtc=0.05,          # K: the guard's control band, logged (proposal)
                rises=(5.0, 10.0, 20.0, 40.0),   # K: joints over the lead's own temperature, V2RF's cases
                rho=1.72e-8, n=2,  # ohm m: copper at 20 C (handbook, ASSUMPTION); the heavy leads of the heating supply
                lug_area=0.5e-4,   # m2: each lead's lug, its surface left outside the heater tape (the palm on the joint's pad), proposal
                lag=(0.01, 0.04),  # m and W/(m K): the lagging over the lug and the guarded length, closed-cell (proposal; k a handbook order)
                h_out=17.0,        # W/(m2 K): still air outside the lagging, the top of V2RF's order (ASSUMPTION)
                dt_joint=60.0)     # K: a joint's rise over the chamber's air, at most (under the limit's 73.75 K; the run reads it)
R15_PAIR_OLD = dict(dt=0.05)       # K: an unguarded pair's resolution, for option (b)'s reading
R15_U = dict(k=0.02, p=0.01, p17=0.01, air=1.0, band=0.02, pick=0.1, unit=0.05, rep=0.5, leak=0.3, early=0.5, c0=0.25, rip=0.52)
# the budget's sources, expanded (k = 2), each with its kind (round 15, V2RF-m4): k the K-factor, common to every reading of one junction
# (relative); p the FETs' heating powers (relative, taken common); p17 R17's power (relative); air 1 K, common to every reading over the
# air; band, the band's current within 1 % so its share of each reading within 2 % of the baseline; pick, the pickup's subtraction, common
# to one junction; unit, the lot correction of each Zself (K/W, proposal); per reading: rep, leak (every reading), early and c0 (the
# heated junction's readings only; c0 is what is left of the control run's measured correction once applied, proposal); rip, half the
# time-division ripple (direct readings only)
R15_RP = 0.1e-3                    # ohm: the pours' allowance (SESSION): each pour's largest path, joint to FET land, summed
R15_SEARCH = dict(seed=20261015, n=1200)
R15_BUDGET_SEED = 31


def r15_reduce(rd, K, rp, qres):
    """The procedure's step 14 on a set of readings: rd holds each junction's baseline rise over the air base[k], its rise over the air
    in each alone case alone[k][j], in R17's case r17[k], the measured powers P[j] and P17, and each Zself's lot correction unit[k].
    Returns (line 1's figure, line 2's hottest T_k, R17's largest coupling, the per-junction T_k)."""
    Z = [[(rd["alone"][k][j] - rd["base"][k]) / rd["P"][j] for j in range(3)] for k in range(3)]
    for k in range(3):
        Z[k][k] += rd["unit"][k]
    z17 = [(rd["r17"][k] - rd["base"][k]) / rd["P17"] for k in range(3)]
    zw = [worst_row(Z[k])[0] for k in range(3)]
    t = [rd["base"][k] + z17[k] * K["p17"] + K["p_even"] * zw[k] + Z[k][k] * (K["i2"] * rp + K["n_lead"] * qres) for k in range(3)]
    return max(zw), max(t), max(z17), t


def r15_readings(tr, e):
    """Readings from a TRUE specimen (tr: B, Z, z17, P, P17) and an error set e (each source's value, zero when absent)."""
    rd = dict(base=[], alone=[], r17=[], P=[p_ * (1 + e.get("p", 0.0)) for p_ in tr["P"]], P17=tr["P17"] * (1 + e.get("p17", 0.0)),
              unit=[e.get(("unit", k), 0.0) for k in range(3)])
    for k in range(3):
        com = e.get("air", 0.0) + e.get("band", 0.0) * tr["B"][k] + e.get(("pick", k), 0.0)
        g = 1.0 + e.get(("k", k), 0.0)
        rd["base"].append(tr["B"][k] * g + com + e.get(("b", k), 0.0))
        rd["alone"].append([(tr["B"][k] + tr["Z"][k][j] * tr["P"][j]) * g + com + e.get(("a", k, j), 0.0) for j in range(3)])
        rd["r17"].append((tr["B"][k] + tr["z17"][k] * tr["P17"]) * g + com + e.get(("r", k), 0.0))
    return rd


def r15_sources():
    """Each source of the budget with its expanded amplitude (R15_U)."""
    u = R15_U
    heated = math.sqrt(u["rep"] ** 2 + u["leak"] ** 2 + u["early"] ** 2 + u["c0"] ** 2)
    other = math.sqrt(u["rep"] ** 2 + u["leak"] ** 2)
    s = [("p", u["p"]), ("p17", u["p17"]), ("air", u["air"]), ("band", u["band"])]
    for k in range(3):
        s += [(("k", k), u["k"]), (("pick", k), u["pick"]), (("unit", k), u["unit"]), (("b", k), other), (("r", k), other)]
        s += [(("a", k, j), heated if j == k else other) for j in range(3)]
    return s


def r15_u(rd, K, rp, qres):
    """Each line's expanded uncertainty PROPAGATED through the reduction from the readings (V2RF-m4): every source moved by its expanded
    amplitude in turn, the lines recomputed, the changes combined in quadrature (absolute terms stay absolute; the K-factor is common to
    one junction's readings, the air and the band to every reading, so they cancel where the reduction takes differences)."""
    base = r15_reduce(rd, K, rp, qres)[:3]
    acc = [0.0, 0.0, 0.0]
    for src, a in r15_sources():
        r2 = dict(base=list(rd["base"]), alone=[list(r_) for r_ in rd["alone"]], r17=list(rd["r17"]), P=list(rd["P"]), P17=rd["P17"],
                  unit=list(rd["unit"]))
        if src == "p":
            r2["P"] = [p_ * (1 + a) for p_ in r2["P"]]
        elif src == "p17":
            r2["P17"] *= 1 + a
        elif src in ("air", "band"):
            for k in range(3):
                d = a if src == "air" else a * rd["base"][k]
                r2["base"][k] += d
                r2["r17"][k] += d
                r2["alone"][k] = [x + d for x in r2["alone"][k]]
        elif src[0] == "k":
            k = src[1]
            r2["base"][k] *= 1 + a
            r2["r17"][k] *= 1 + a
            r2["alone"][k] = [x * (1 + a) for x in r2["alone"][k]]
        elif src[0] == "pick":
            k = src[1]
            r2["base"][k] += a
            r2["r17"][k] += a
            r2["alone"][k] = [x + a for x in r2["alone"][k]]
        elif src[0] == "unit":
            r2["unit"][src[1]] += a
        elif src[0] == "b":
            r2["base"][src[1]] += a
        elif src[0] == "r":
            r2["r17"][src[1]] += a
        else:
            r2["alone"][src[1]][src[2]] += a
        new = r15_reduce(r2, K, rp, qres)[:3]
        acc = [acc[i] + (new[i] - base[i]) ** 2 for i in range(3)]
    return [math.sqrt(x) for x in acc]


def r15_verdict(rd, K, rp, qres):
    l1, l2, l17, _t = r15_reduce(rd, K, rp, qres)
    u1, u2, u17 = r15_u(rd, K, rp, qres)
    return (l1 + u1 <= K["bar_even"] and l2 + u2 <= K["rise"] and l17 + u17 <= K["z17"]), (l1, u1), (l2, u2), (l17, u17)


def r15_true_t(tr, K, pours, guard):
    """The service junction's rise over the air at its own worst split, with the pours' actual shortfall and the leads' actual residual."""
    return max(tr["B"][k] + tr["z17"][k] * K["p17"] + K["p_even"] * worst_row(tr["Z"][k])[0] + pours[k] + guard[k] for k in range(3))


def r15_coupon(s, m_, z17, b, p_alone):
    """A coupon at a given Zself s: three side by side, each pair coupled at m s (the ends at m s / 2), the baseline b, R17's coupling z17."""
    Z = [[s, m_ * s, m_ * s / 2.0], [m_ * s, s, m_ * s], [m_ * s / 2.0, m_ * s, s]]
    return dict(B=[b] * 3, Z=Z, z17=[z17] * 3, P=[p_alone] * 3, P17=None)


def r15_states(rules, drop=()):
    """Every state the fixture can reach from rest by single permitted steps (V2RF-m1): SW_S closed (1) or open, SW_B closed or open, the
    heating supply on or off, each gate off (on VBAT), on (10 V under VBAT) or tie (on its drain tap). rules is 'old' (round 14 as
    written: a tie only with the shunt under 10 mA, SW_S closing only with a gate on) or 'new' (round 15). Returns the reachable states,
    the hazardous ones among them and a path to the first."""
    import itertools
    def shunt(st):
        sws, swb, sup, g = st
        return sup and sws and any(x in ("on", "tie") for x in g)
    def ok(st, nx):
        sws, swb, sup, g = st
        nsws, nswb, nsup, ng = nx
        if rules == "old":
            if ng != g:
                k = [i for i in range(3) if ng[i] != g[i]][0]
                if ng[k] == "tie" and shunt(st):
                    return False
            if nsws and not sws and "on" not in g:
                return False
            return True
        if ng != g:
            k = [i for i in range(3) if ng[i] != g[i]][0]
            if "R1" not in drop and ng[k] == "tie" and (sws or shunt(st)):
                return False                      # R1: a tie only with SW_S open by its own state, and the shunt under 10 mA
            if "R3" not in drop and g[k] == "on" and sws and sum(1 for x in g if x == "on") == 1:
                return False                      # R3: the last conducting gate stays while SW_S is closed
        if "R2" not in drop and nsws and not sws and ("tie" in g or "on" not in g):
            return False                          # R2: SW_S closes only with no gate tied and a gate on
        if "R4" not in drop and not nswb and swb and not (sws and "on" in g):
            return False                          # R4: SW_B opens only while SW_S is closed and a gate is on
        if "R5" not in drop and not nsws and sws and not swb:
            return False                          # R5: SW_S opens only while SW_B is closed
        if "R6" not in drop and nsup and not sup and not (swb or (sws and "on" in g)):
            return False                          # R6: the supply starts only with a path
        return True
    def hazard(st):
        sws, swb, sup, g = st
        h = []
        if sws and "tie" in g:
            h.append("H1: a gate on its drain tap with SW_S closed (the clamp: the heating current through a diode-connected FET)")
        if sup and not (swb or (sws and "on" in g)):
            h.append("H2: the heating supply on with no path (at its compliance)")
        return h
    start = (0, 1, 0, ("off", "off", "off"))
    seen, order, todo, prev = {start}, [start], [start], {start: None}
    while todo:
        st = todo.pop(0)
        sws, swb, sup, g = st
        nexts = [(1 - sws, swb, sup, g), (sws, 1 - swb, sup, g), (sws, swb, 1 - sup, g)]
        for k in range(3):
            for v in ("off", "on", "tie"):
                if v != g[k]:
                    nexts.append((sws, swb, sup, g[:k] + (v,) + g[k + 1:]))
        for nx in nexts:
            if nx not in seen and ok(st, nx):
                seen.add(nx)
                order.append(nx)
                prev[nx] = st
                todo.append(nx)
    bad = [st for st in order if hazard(st)]          # in the order found: the first of each kind is the nearest to rest
    paths = {}
    for kind in ("H1", "H2"):
        first = [st for st in bad if any(h.startswith(kind) for h in hazard(st))][:1]
        if first:
            st, path = first[0], []
            while st is not None:
                path.append(st)
                st = prev[st]
            paths[kind] = (path[::-1], [h for h in hazard(first[0]) if h.startswith(kind)][0])
    return seen, bad, paths


def fix25_round(R, T):
    """Round 15: V2RF-B1, the heavy leads (the old treatment reproduced, two corrections compared, the guard selected and its residual
    bounded), and V2RF-m1 to m5: the interlock on SW_S's own state (a state search), the galvanic boundary and the census, SW_S's clamp,
    each line's uncertainty propagated through the reduction (a search with readings drawn from the budget), the pours' allowance in
    the sizing target, and a coupon at the target shown to pass under the limit and fail over it."""
    S9, S21, S23, S24 = R["S19"], R["S21"], R["S23"], R["S24"]
    S = {}
    K = dict(S24["K"])
    K["i2"] = S9["i"] ** 2
    K["n_lead"] = R15_LEAD["n"]
    S["K"] = K
    ld = R15_LEAD
    ka = ld["k_cu"] * ld["area"]
    # ---- V2RF-B1 reproduced: round 14's V8 and lead term
    S["g_fin"] = tuple(math.sqrt(h * ka) for h in ld["hp"])
    S["v8"] = R14_LEAD["frac"] * S23["p"]["hot"]
    S["v8_dt"] = tuple(S["v8"] / g for g in S["g_fin"])
    S["q_at"] = [(r_, S["g_fin"][0] * r_, S["g_fin"][1] * r_) for r_ in ld["rises"]]
    S["old_term"] = (2 * S21["bar_new"] * S["q_at"][0][1], 2 * S21["bar_new"] * S["q_at"][-1][2])
    i_hi = S23["i_td"][0][1]
    S["self_rise"] = [(i_, i_ ** 2 * ld["rho"] / ld["area"] / ld["hp"][1], i_ ** 2 * ld["rho"] / ld["area"] / ld["hp"][0])
                      for i_ in (S23["i_single"][0], S23["i_td"][0][0], i_hi)]
    def factor(zjj, zjk, share):
        g = share / zjj
        a, b = 1 - g * zjj, -g * zjk
        det = a * a - b * b
        return (a - b) / det                     # the column sum of (I - G Z_JJ)^-1 for two equal leads
    S["factor"] = (factor(20.0, 15.0, 0.5), factor(20.0, 2.0, 0.5))
    if not (abs(S["factor"][0] - 8.0) < 1e-9 and S["old_term"][0] > 6.0 and S["old_term"][1] > 60.0):
        refuse(4, "V2RF-B1's arithmetic is not reproduced")
    # ---- two corrections compared: (b) measure the correction on passive leads, (a) guard the leads
    S["b_curv"] = tuple(h * ld["dx"] * r_ / 2.0 for h in ld["hp"] for r_ in (ld["rises"][0], ld["rises"][-1]))
    S["b_res"] = ka * R15_PAIR_OLD["dt"] / ld["dx"]
    S["b_err"] = (S["b_res"] + min(S["b_curv"]), S["b_res"] + max(S["b_curv"]))
    S["a_pair"] = ka * (ld["dt0"] + ld["dtc"]) / ld["dx"]
    S["u_lag"] = 1.0 / (ld["lag"][0] / ld["lag"][1] + 1.0 / ld["h_out"])
    S["a_lug"] = S["u_lag"] * ld["lug_area"] * ld["dt_joint"]          # the lagged lug's own loss, which the joint supplies
    S["a_res"] = S["a_pair"] + S["a_lug"]
    S["a_term"] = K["n_lead"] * S["a_res"] * S21["bar_new"]
    S["a_heat"] = (S["q_at"][0][1], S["q_at"][-1][2])          # the guard's heater must supply what the passive lead would draw
    if not (S["a_res"] < 0.02 and S["a_term"] < 1.5 and S["b_err"][1] > 5 * S["a_res"]):
        refuse(4, "the guard does not leave a residual smaller than the measured correction's own error")
    # ---- V2RF-m1: the interlock, by a state search
    S["st_old"] = r15_states("old")
    S["st_new"] = r15_states("new")
    S["st_drop"] = [(r_, sorted(r15_states("new", (r_,))[2])) for r_ in ("R1", "R2", "R3", "R4", "R5", "R6")]
    if "H1" not in S["st_old"][2] or S["st_new"][1]:
        refuse(4, "the old interlock reaches no hazard, or the new one reaches one")
    S["leg_v"] = i_hi * R14_SW["r_leg"]
    S["vth_hot_min"] = 0.75                                    # V2RF's reading of Fig. 11's min curve at 150 C (T, by eye)
    # ---- V2RF-m2: the census with the galvanic boundary's elements (each a PROPOSAL the supplier's parts or readings must meet)
    i_m = R13_B["i_m"]
    vth_max = S23["vth"][3]
    S["m2_add"] = [("the thermocouples on live copper, each insulated at 100 MOhm or more, 12 of them in series pairs through a common logger",
                    12 * vth_max / 100e6),
                   ("the guard heaters' insulation from the live leads, two, at 100 MOhm or more", 2 * vth_max / 100e6),
                   ("the supplies' output-to-earth leakage through the one earth point, each at most 1 uA, five supplies", 5e-6),
                   ("the isolated interlock, sequencer and gate-drive barriers, at 1 GOhm or more, four", 4 * 15.0 / 1e9),
                   ("SW_S's clamp at the reading's 3.1 V, under its 20 V standoff row", 1e-6)]
    S["m2_sum"] = S24["sense_sum"] + sum(x for _l, x in S["m2_add"])
    S["m2_frac"] = S["m2_sum"] / i_m
    # ---- V2RF-m3: SW_S's interruption
    S["m3_e"] = [(l_, i_, 0.5 * l_ * i_ ** 2) for l_ in (0.6e-6, 1.2e-6) for i_ in (8.4, 17.4)]
    S["m3_t"] = 1.2e-6 * 17.4 / 30.0
    # ---- V2RF-m4: each line's U propagated, on a coupon at the target (below) and in a search with readings drawn from the budget
    p_alone = S23["p"]["hot"]
    qres = S["a_res"]
    def lines_at(s, z17, rp, m_=0.1, b=S9["band"]):
        tr = r15_coupon(s, m_, z17, b, p_alone)
        tr["P17"] = K["p17"]
        rd = r15_readings(tr, {})
        return tr, rd, r15_reduce(rd, K, rp, qres), r15_u(rd, K, rp, qres)
    # R17's design target: its line passes with twice its U (the guard band); then the FETs' target with the pours' allowance
    def solve(f, lo, hi):
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if f(mid):
                lo = mid
            else:
                hi = mid
        return lo
    s_ref = S21["bar_new"]
    S["z17_t"] = solve(lambda z: (lambda r_: r_[2][2] + 2 * r_[3][2] <= K["z17"])(lines_at(s_ref, z, R15_RP)), 0.0, 1.0)
    S["s_t"] = {}
    S["zw_t"] = {}
    for rp in (0.0, 0.05e-3, 0.1e-3, 0.15e-3, 0.2e-3):
        S["s_t"][rp] = solve(lambda s: (lambda r_: r_[2][1] + 2 * r_[3][1] <= K["rise"] and r_[2][0] + 2 * r_[3][0] <= K["bar_even"])(
            lines_at(s, S["z17_t"], rp)), 10.0, 60.0)
        S["zw_t"][rp] = lines_at(S["s_t"][rp], S["z17_t"], rp)[2][0]
    st = S["s_t"][R15_RP]
    tr, rd, red, u = lines_at(st, S["z17_t"], R15_RP)
    S["target"] = dict(s=st, S=st * 1.2, zw=red[0], l2=red[1], u=u, l17=red[2])
    uu = R15_U
    heated = math.sqrt(uu["rep"] ** 2 + uu["leak"] ** 2 + uu["early"] ** 2 + uu["c0"] ** 2)
    S["u3"] = math.sqrt((uu["k"] * red[1]) ** 2 + uu["air"] ** 2 + (uu["band"] * S9["band"]) ** 2 + uu["pick"] ** 2 + heated ** 2 + uu["rip"] ** 2)
    # the same coupon, the ILLUSTRATION round 14 printed (3.47 % on every line) against the propagated U
    S["u_illus"] = (u[0] / red[0], u[1] / red[1], u[2] / red[2])
    # the verdict table: the FETs' part moved so the TRUE hottest junction sits at chosen points; the reading of each line at its error edge
    S["table"] = []
    for lab, dt in (("the design target", None), ("the target's U under the limit", "U"), ("0.1 K under the limit", -0.1), ("0.1 K over the limit", 0.1),
                    ("1 K over the limit", 1.0)):
        if dt is None:
            s = st
        else:
            lev = K["rise"] - u[1] if dt == "U" else K["rise"] + dt
            s = solve(lambda s_: lines_at(s_, S["z17_t"], R15_RP)[2][1] <= lev, 10.0, 60.0)
        tr, rd, red, uu = lines_at(s, S["z17_t"], R15_RP)
        true2 = red[1]                              # the coupon's own figure (the pours and the guard at their bounds: the worst case)
        row = dict(lab=lab, s=s, true=true2, u=uu[1])
        for sgn, nm in ((1, "high"), (0, "exact"), (-1, "low")):
            row[nm] = (true2 + sgn * uu[1]) + uu[1] <= K["rise"] and red[0] + sgn * uu[0] + uu[0] <= K["bar_even"]
        S["table"].append(row)
    # the old lead term at the same target: a passive lead's flux at V2RF's joint rises, times twice Zself, on both leads
    S["old_at_target"] = (red[1] + 2 * K["n_lead"] * st * S["q_at"][0][1], red[1] + 2 * K["n_lead"] * st * S["q_at"][-1][2])
    # ---- the search: readings drawn from the budget (each source normal, its expanded amplitude two standard deviations)
    import random
    rnd = random.Random(R15_SEARCH["seed"])
    srcs = r15_sources()
    c = dict(n=0, acc=0, over=0, acc_over=0, near=0, near_acc=0, worst=0.0, under_refused_far=0)
    for fam in ("net", "row", "sym"):
        for _ in range(R15_SEARCH["n"]):
            Zt = r14_matrix(rnd, fam)
            zw = max(worst_row(Zt[k])[0] for k in range(3))
            sc = rnd.uniform(0.75, 1.05) * K["bar_even"] / zw
            Zt = [[x * sc for x in r_] for r_ in Zt]
            trs = dict(B=[rnd.uniform(4.0, 14.0) for _k in range(3)], Z=Zt, z17=[rnd.uniform(0.0, 0.9) for _k in range(3)], P=[p_alone] * 3,
                       P17=K["p17"])
            pours = [Zt[k][k] * K["i2"] * R15_RP * rnd.uniform(0.3, 1.0) for k in range(3)]
            guard = [Zt[k][k] * K["n_lead"] * qres * rnd.uniform(-1.0, 1.0) for k in range(3)]
            true_t = r15_true_t(trs, K, pours, guard)
            e = {src: rnd.gauss(0.0, a / 2.0) for src, a in srcs}
            ok = r15_verdict(r15_readings(trs, e), K, R15_RP, qres)[0]
            over = true_t > K["rise"] + 1e-9
            c["n"] += 1
            c["over"] += over
            c["acc"] += ok
            if ok and over:
                c["acc_over"] += 1
                c["worst"] = max(c["worst"], true_t - K["rise"])
            if over and true_t <= K["rise"] + 3.0:
                c["near"] += 1
                c["near_acc"] += ok
    S["search"] = c
    # ---- V2RF-m5: the pours' allowance in the target and the layout requirement
    S["m5"] = [(rp, S["s_t"][rp], S["zw_t"][rp]) for rp in sorted(S["s_t"])]
    S["pours_at_t"] = st * K["i2"] * R15_RP
    S["guard_at_t"] = st * K["n_lead"] * qres
    return S


def render_fix25(R, p):
    S, S21, S23, S24 = R["S25"], R["S21"], R["S23"], R["S24"]
    K, ld = S["K"], R15_LEAD
    p("25. ROUND 15: THE FINAL RECHECK V2RF'S FINDINGS ON TP-E11-29'S HEAVY LEADS AND THE FIXTURE'S MINORS (5 October 2026; C-PROT rev 1)")
    p("   25a. V2RF-B1 REPRODUCED: ROUND 14'S V8 AND LEAD TERM CANNOT BE MET (INFERRED; V2RF's heat-transfer order, ASSUMPTION)")
    p("     a long 4 mm2 lead offers its joint the fin conductance sqrt(h P k A) = %s to %s W/K (h P %s to %s W/(m K), k %s W/(m K))"
      % (fmt(S["g_fin"][0], 4), fmt(S["g_fin"][1], 4), fmt(ld["hp"][0], 2), fmt(ld["hp"][1], 2), fmt(ld["k_cu"], 0)))
    p("     V8's %s mW holds only while the joint sits within %s to %s K of the lead's own temperature; the lead's self-heating:"
      % (fmt(S["v8"] * 1e3, 1), fmt(S["v8_dt"][1], 2), fmt(S["v8_dt"][0], 2)))
    for i_, a, b in S["self_rise"]:
        p("       %s A: %s to %s K" % (fmt(i_, 2), fmt(a, 1), fmt(b, 1)))
    for r_, a, b in S["q_at"]:
        p("     a joint %s K over the lead draws %s to %s W, %s to %s times V8" % (fmt(r_, 0), fmt(a, 3), fmt(b, 3), fmt(a / S["v8"], 1), fmt(b / S["v8"], 1)))
    p("     round 14's term 2 x Zself x q at %s K/W: %s to %s K a lead; its factor 2 was derived for one lead: for two equal leads each taking"
      % ("%.2f" % S21["bar_new"], fmt(S["old_term"][0], 1), fmt(S["old_term"][1], 1)))
    p("       half the heat at its own joint the column sum of (I - G Z_JJ)^-1 is %s with the joints coupled at 15 of 20 K/W, %s at 2 K/W:"
      % (fmt(S["factor"][0], 2), fmt(S["factor"][1], 2)))
    p("       V8 and the lead term are WITHDRAWN")
    p("   25b. TWO CORRECTIONS COMPARED (SESSION; INFERRED)")
    p("     (b) MEASURE the correction on passive leads: q from a pair over an unheated section is biased by that section's own loss, h P dx dT / 2,")
    p("       %s to %s mW at joints %s to %s K over the lead, plus the pair's %s mW; the correction Z0 q then needs (I - F)^-1 measured too, F up to"
      % (fmt(min(S["b_curv"]) * 1e3, 1), fmt(max(S["b_curv"]) * 1e3, 0), fmt(ld["rises"][0], 0), fmt(ld["rises"][-1], 0), fmt(S["b_res"] * 1e3, 1)))
    p("       a half or more: an error of the order of the whole of round 14's V8 on each lead")
    p("     (a) GUARD each lead (SELECTED): a heater tape over the lug's barrel and the lead from it (no bare lead), the pair under it %s mm"
      % fmt(ld["dx"] * 1e3, 0))
    p("       apart, the first on the lug at the joint, an integral controller holding the pair's difference at zero, the lug and the guarded")
    p("       length lagged: with the lead held at its joint's temperature along the heated length, the joint supplies only the pair's offset and")
    p("       control band, %s K and %s K, %s mW a lead (k A dT / dx), and the lagged lug's own loss, %s mW (U %s W/(m2 K) through %s mm of"
      % (fmt(ld["dt0"], 2), fmt(ld["dtc"], 2), fmt(S["a_pair"] * 1e3, 1), fmt(S["a_lug"] * 1e3, 1), fmt(S["u_lag"], 2), fmt(ld["lag"][0] * 1e3, 0)))
    p("       lagging, %s cm2, a joint %s K over the air): %s mW a lead at most, whatever the joint's temperature within that;"
      % (fmt(ld["lug_area"] * 1e4, 1), fmt(ld["dt_joint"], 0), fmt(S["a_res"] * 1e3, 1)))
    p("       at steady state the guarded coupon IS the coupon without its leads plus a fixed source of at most that flux, so no factor and no")
    p("       assumption on the leads' share is needed; its effect on junction k is at most Z_kJ times it, Z_kJ read by reciprocity from the joint's")
    p("       thermocouple in cases A to C (Z_kJ = Z_Jk), at most Zself,k: both leads together %s K at the bar's %s K/W"
      % (fmt(S["a_term"], 2), "%.2f" % S21["bar_new"]))
    p("     the guard's heater supplies what the passive lead would draw, %s to %s W a lead; it can only heat, so each lead is sized so its own"
      % (fmt(S["a_heat"][0], 2), fmt(S["a_heat"][1], 2)))
    p("       self-heating stays under its joint's rise (V8 restated: the guard in control, its output never at zero or full, the pair's logged")
    p("       difference within the band; else INCONCLUSIVE and a larger lead)")
    p("   25c. V2RF-m1: THE INTERLOCK ON SW_S'S OWN STATE (a search of every state reachable from rest by single permitted steps; INFERRED)")
    for nm, lab in (("st_old", "round 14's rules (a tie with the shunt under 10 mA; SW_S closing with a gate on)"),
                    ("st_new", "round 15's rules R1 to R6")):
        seen, bad, paths = S[nm]
        p("     %s: %d states reachable, %d hazardous" % (lab, len(seen), len(bad)))
        for kind in ("H1", "H2"):
            if kind in paths:
                path, why = paths[kind]
                p("       %s" % why)
                p("         the nearest path: %s" % " -> ".join("SW_S %s, SW_B %s, supply %s, gates %s" % ("closed" if a else "open", "closed" if b else "open",
                                                                                                      "on" if c else "off", "/".join(g)) for a, b, c, g in path))
    p("     each rule dropped alone: %s; R6 is implied by R4 and R5 and kept as a second barrier"
      % "; ".join("%s %s" % (r_, ", ".join(h) if h else "no hazard") for r_, h in S["st_drop"]))
    p("     a failed-short SW_S with SW_B closed: the leg holds the pours at %s V at most (22.46 A x 5 mOhm), under the threshold's %s V (Fig. 11's"
      % (fmt(S["leg_v"], 3), fmt(S["vth_hot_min"], 2)))
    p("       min curve at 150 C, V2RF's reading, T): no FET takes the heating current, and the reading falls outside its calibration (INCONCLUSIVE)")
    p("   25d. V2RF-m2: THE GALVANIC BOUNDARY AND THE CENSUS (PROPOSALS for the supplier's parts; MAKER rows as round 14)")
    for lab, x in S["m2_add"]:
        p("     %s: %s uA" % (lab, fmt(x * 1e6, 2)))
    p("     with round 14's %s uA: %s uA, %s %% of the sense current; check V3 is repeated in the chamber with every supply, dummy, thermocouple and"
      % (fmt(R["S24"]["sense_sum"] * 1e6, 2), fmt(S["m2_sum"] * 1e6, 2), fmt(S["m2_frac"] * 100, 2)))
    p("       instrument connected as in a run, before the cases and after the last")
    p("   25e. V2RF-m3: SW_S's OPENING (V2RF's inductance and current, MINE in its terms: an ASSUMPTION here; the clamp's figures SESSION proposals)")
    for l_, i_, e_ in S["m3_e"]:
        p("     %s uH, %s A: %s uJ" % (fmt(l_ * 1e6, 1), fmt(i_, 1), fmt(e_ * 1e6, 0)))
    p("     SW_S is solid-state (no relay); a clamp across it (a bidirectional TVS, standoff 20 V or more, clamping under 0.8 of the MOSFETs' VDS")
    p("       rating, 0.2 mJ or more repetitive at 1 Hz; or MOSFETs with a printed repetitive avalanche rating of 0.2 mJ); the clamp ends the")
    p("       current in %s us at 30 V, before the tie at 2 us; its leakage is in the census (25d)" % fmt(S["m3_t"] * 1e6, 2))
    tg = S["target"]
    p("   25f. V2RF-m4: EACH LINE'S U PROPAGATED THROUGH THE REDUCTION (the budget's sources as R15_U; INFERRED)")
    p("     on a coupon at the design target (25g): line 1 %s K/W, U %s K/W (%s %%); line 2 %s K, U %s K (%s %%); R17 %s K/W, U %s K/W (%s %%)"
      % (fmt(tg["zw"], 2), fmt(tg["u"][0], 2), fmt(S["u_illus"][0] * 100, 2), fmt(tg["l2"], 2), fmt(tg["u"][1], 2), fmt(S["u_illus"][1] * 100, 2),
         fmt(tg["l17"], 3), fmt(tg["u"][2], 3), fmt(S["u_illus"][2] * 100, 1)))
    p("       against round 14's 3.47 %% on every line; line 3, one reading over the air with the ripple, %s K; the control run's measured difference"
      % fmt(S["u3"], 2))
    p("       is applied as a correction and only its own %s K stays in U (V9 still refuses a difference over 0.5 K)" % fmt(R15_U["c0"], 2))
    sr = S["search"]
    p("     the search (seed %d, %d matrices in each of three families; every source of the budget drawn normal, its expanded amplitude two"
      % (R15_SEARCH["seed"], R15_SEARCH["n"]))
    p("       standard deviations; each line's U propagated from the readings): %d accepted of %d; over 150 C %d; accepted over 150 C %d, the worst"
      % (sr["acc"], sr["n"], sr["over"], sr["acc_over"]))
    p("       %s K over; of the %d within 3 K over the limit, %d accepted. The claim, on this model: a specimen exactly at the limit passes with"
      % (fmt(sr["worst"], 2), sr["near"], sr["near_acc"]))
    p("       a probability of about 2.5 % (a guarded rule at k = 2) and one over it with less; round 14's 'none over 150 C' followed from the lines'")
    p("       monotony with each reading's error bounded by the U the rule adds, which is not the budget's model (V2RF-m4)")
    p("   25g. V2RF-m5 AND THE DESIGN TARGET: THE POURS' ALLOWANCE, R17'S AND THE FETs' TARGETS (SESSION; INFERRED)")
    p("     R17's coupling target: at most %s K/W (its line passes with twice its U)" % fmt(S["z17_t"], 3))
    for rp, s, zw in S["m5"]:
        p("     the pours' allowance %s mOhm: each junction's worst-split figure Zw at most %s K/W (for three side by side at m 0.1: Zself %s, S %s K/W)"
          % (fmt(rp * 1e3, 2), fmt(zw, 2), fmt(s, 2), fmt(s * 1.2, 2)))
    p("     SELECTED: %s mOhm, each pour's largest path from its current's joint to the FET lands, summed, at the operating temperature (a layout"
      % fmt(R15_RP * 1e3, 2))
    p("       requirement): the target Zw %s K/W (Zself %s, S %s K/W at m 0.1), line 2 with twice its U; the pours' term %s K and the guard's %s K"
      % (fmt(tg["zw"], 2), fmt(tg["s"], 2), fmt(tg["S"], 2), fmt(S["pours_at_t"], 2), fmt(S["guard_at_t"], 2)))
    p("     the verdict on a coupon whose TRUE line-2 figure sits at a chosen point, each line read at its error's edges (+U, exact, -U):")
    for r_ in S["table"]:
        yn = lambda v: "PASS" if v else "FAIL"
        p("       %-22s true %s K (U %s K): read high %s, exact %s, low %s" % (r_["lab"] + ":", fmt(r_["true"], 2), fmt(r_["u"], 2), yn(r_["high"]),
                                                                           yn(r_["exact"]), yn(r_["low"])))
    p("     round 14's lead term at the same target, both leads passive at V2RF's joints 5 to 40 K over them: line 2 %s to %s K: FAIL"
      % (fmt(S["old_at_target"][0], 1), fmt(S["old_at_target"][1], 1)))
    p("   25h. STATUS (SESSION): V2RF-B1 CORRECTED on the desk (the guard); m1 to m5 answered; TP-E11-29 NOT EXECUTABLE until R-159 is restated")
    p("     and a supplier agrees in writing; this is the answer to the FIRST negative check of the lead treatment: a second ends that loop")
    p("")


# ---- round 16 (5 October 2026): the check V2RG's V2RG-B1 ends the heavy-lead correction loop (two negative checks); the coordinator's
# diagnosis makes the lead heat an EXTERNAL QUALIFICATION task: a requirement on the supplier's fixture, demonstrated by the supplier;
# and V2RG's minors m1 to m6 (C-PROT rev 1)
R16_Q = (0.005, 0.01, 0.02, 0.03)  # W a lead: the allowances compared for the net heat at each heating lead's joint
R16_Q_SEL = 0.01                   # W a lead: SELECTED (SESSION)
R16_ZJ_PLAN = 1.0                  # the joint-to-junction impedance for PLANNING as a fraction of Zself: its bound (a run reads its own)
R16_DEMO = dict(dt=0.02, l=0.06)   # the three-thermocouple reading's match after an isothermal reading (K) and its span (m), proposals
R16_MC = dict(seed=20261016, n=2000)


def r16_lead_bounds(tr, K, rp, bk):
    """Each line's bound from the leads' net heat (V2RG-B1's allowance, a bound of EITHER sign): every reading of junction k may carry
    the leads' effect up to bk[k] = (the leads' net heat) x (the joint-to-junction impedance) in either direction, independently from
    reading to reading (no sign is known); each reading moved by it in turn and the absolute changes of each line SUMMED (a worst case,
    not a quadrature: the effect is a bound, not a random error). Returns the bounds of line 1, line 2 and R17's line."""
    rd = r15_readings(tr, {})
    base = r15_reduce(rd, K, rp, 0.0)[:3]
    acc = [0.0, 0.0, 0.0]
    keys = [("b", k) for k in range(3)] + [("r", k) for k in range(3)] + [("a", k, j) for k in range(3) for j in range(3)]
    for key in keys:
        new = r15_reduce(r15_readings(tr, {key: bk[key[1]]}), K, rp, 0.0)[:3]
        acc = [acc[i] + abs(new[i] - base[i]) for i in range(3)]
    return acc


def r16_u3(K, t3, b, zw, z17):
    """The direct line's U (V2RG-m2): one reading over the air of the hottest junction in a case F, with the FETs' and R17's 1 % powers
    and each Zself's lot correction, besides the K-factor, the air, the band, the pickup, the heated reading's terms and the ripple."""
    u = R15_U
    heated = math.sqrt(u["rep"] ** 2 + u["leak"] ** 2 + u["early"] ** 2 + u["c0"] ** 2)
    return math.sqrt((u["k"] * t3) ** 2 + u["air"] ** 2 + (u["band"] * b) ** 2 + u["pick"] ** 2 + heated ** 2 + u["rip"] ** 2
                     + (u["p"] * K["p_even"] * zw) ** 2 + (u["p17"] * z17 * K["p17"]) ** 2 + (u["unit"] * K["p_hot0"]) ** 2)


def fix26_round(R, T):
    """Round 16: the lead treatment as an external qualification (the fixture requirement, its demonstration, V8 on the measured
    residual, the targets restated for the allowance, the verdict table with the allowance a bound of either sign), and V2RG-m1 to m6."""
    S9, S21, S23, S25 = R["S19"], R["S21"], R["S23"], R["S25"]
    S = {}
    K = S25["K"]
    p_alone = S23["p"]["hot"]
    ka = R15_LEAD["k_cu"] * R15_LEAD["area"]
    # ---- the guard withdrawn as the qualification: V2RG-B1's mechanism, the curvature the record wrote for option (b) and not for (a)
    S["v2rg"] = dict(q_005=(0.031, 0.426), q_01=(0.010, 0.132), q_02=(0.002, 0.038), floor=(0.018, 0.054))   # W a lead, V2RG's fin model (as received)
    # ---- the demonstration's own reading: three thermocouples on the lead's copper over an unheated span, q0 = k A (3 T0 - 4 Tmid + TL) / L
    d = R16_DEMO
    S["demo_u"] = ka * math.sqrt(3 ** 2 + 4 ** 2 + 1 ** 2) * d["dt"] / d["l"]
    # ---- the allowance's cost: targets for each allowance (the joint-to-junction impedance at its bound, Zself, for planning)
    def coupon(s, z17):
        tr = r15_coupon(s, 0.1, z17, S9["band"], p_alone)
        tr["P17"] = K["p17"]
        return tr
    def lines(s, q, z17):
        tr = coupon(s, z17)
        rd = r15_readings(tr, {})
        red = r15_reduce(rd, K, R15_RP, 0.0)
        u = r15_u(rd, K, R15_RP, 0.0)
        bk = [K["n_lead"] * q * R16_ZJ_PLAN * tr["Z"][k][k] for k in range(3)]
        lb = r16_lead_bounds(tr, K, R15_RP, bk)
        return tr, red, u, lb, bk
    def solve(f, lo, hi):
        for _ in range(48):
            mid = 0.5 * (lo + hi)
            if f(mid):
                lo = mid
            else:
                hi = mid
        return lo
    z17_t = S25["z17_t"]
    def ok(s, q):
        _tr, red, u, lb, _bk = lines(s, q, z17_t)
        return red[1] + 2 * u[1] + 2 * lb[1] <= K["rise"] and red[0] + 2 * u[0] + 2 * lb[0] <= K["bar_even"]
    S["trade"] = []
    for q in (0.0,) + R16_Q:
        s = solve(lambda s_: ok(s_, q), 10.0, 60.0)
        tr, red, u, lb, bk = lines(s, q, z17_t)
        S["trade"].append(dict(q=q, s=s, zw=red[0], l2=red[1], u=u, lb=lb, b1=bk[1]))
    sel = [r_ for r_ in S["trade"] if r_["q"] == R16_Q_SEL][0]
    S["sel"] = sel
    S["amplify"] = sel["lb"][1] / sel["b1"]
    tr, red, u, lb, bk = lines(sel["s"], R16_Q_SEL, z17_t)
    S["l3_t"] = red[1]                                        # the direct reading at the target sits at line 2's figure (superposition)
    S["u3"] = r16_u3(K, red[1], S9["band"], red[0], z17_t)
    uu = R15_U
    heated = math.sqrt(uu["rep"] ** 2 + uu["leak"] ** 2 + uu["early"] ** 2 + uu["c0"] ** 2)
    S["u3_old"] = math.sqrt((uu["k"] * red[1]) ** 2 + uu["air"] ** 2 + (uu["band"] * S9["band"]) ** 2 + uu["pick"] ** 2 + heated ** 2
                            + uu["rip"] ** 2)                 # round 15's form at the same reading, without the power terms
    S["lb3"] = max(bk)                                        # one reading: the leads' bound enters once
    S["pours_t"] = sel["s"] * K["i2"] * R15_RP
    S["z17_t"] = z17_t
    if not (sel["lb"][1] > 3 * sel["b1"] and S["u3"] > S["u3_old"]):
        refuse(4, "the superposition line does not amplify the leads' bound, or line 3's U did not grow with its power terms")
    # ---- the verdict table: the TRUE line-2 figure (the pours at their bound, no lead effect) at chosen points; the reading's error at
    # its edges, the leads' effect at its bound of either sign with it
    S["table"] = []
    for lab, lev in (("the design target", None), ("the target's U + L under the limit", "UL"), ("0.1 K under the limit", -0.1),
                     ("0.1 K over the limit", 0.1), ("1 K over the limit", 1.0)):
        if lev is None:
            s = sel["s"]
        else:
            tgt = K["rise"] - (sel["u"][1] + sel["lb"][1]) if lev == "UL" else K["rise"] + lev
            s = solve(lambda s_: lines(s_, R16_Q_SEL, z17_t)[1][1] <= tgt, 10.0, 60.0)
        tr, red, u, lb, bk = lines(s, R16_Q_SEL, z17_t)
        row = dict(lab=lab, s=s, true=red[1], u=u[1], lb=lb[1])
        row["high"] = red[1] + lb[1] + u[1] + u[1] + lb[1] <= K["rise"] and red[0] + 2 * (u[0] + lb[0]) <= K["bar_even"]
        row["exact"] = red[1] + u[1] + lb[1] <= K["rise"] and red[0] + u[0] + lb[0] <= K["bar_even"]
        row["low"] = red[1] - lb[1] - u[1] + u[1] + lb[1] <= K["rise"] and red[0] <= K["bar_even"]
        S["table"].append(row)
    # ---- V2RG-m3: the probability that a coupon exactly at the limit passes, from the record's own functions
    import random
    rnd = random.Random(R16_MC["seed"])
    srcs = r15_sources()
    def coupon_lim(s):                                         # V2RG-m3's setting: lines 1 and R17 with room (a 20 K baseline, R17 at 0.1 K/W)
        tr_ = r15_coupon(s, 0.1, 0.1, 20.0, p_alone)
        tr_["P17"] = K["p17"]
        return tr_
    s_lim = solve(lambda s_: r15_reduce(r15_readings(coupon_lim(s_), {}), K, R15_RP, 0.0)[1] <= K["rise"], 10.0, 60.0)
    trl = coupon_lim(s_lim)
    S["mc_l1"] = r15_reduce(r15_readings(trl, {}), K, R15_RP, 0.0)[0]
    S["mc_true"] = r15_reduce(r15_readings(trl, {}), K, R15_RP, 0.0)[1]
    acc0 = 0
    for _ in range(R16_MC["n"]):
        rd = r15_readings(trl, {src: rnd.gauss(0.0, a / 2.0) for src, a in srcs})
        acc0 += r15_verdict(rd, K, R15_RP, 0.0)[0]
    S["mc"] = (acc0, R16_MC["n"])
    # ---- V2RG-m6: the census ratio at 34.48 uA
    i_m = R13_B["i_m"]
    S["ratio_m6"] = (i_m - S25["m2_sum"]) / R["S24"]["idss"][1]
    return S


def render_fix26(R, p):
    S, S25 = R["S26"], R["S25"]
    K = S25["K"]
    sel = S["sel"]
    p("26. ROUND 16: THE HEAVY LEADS AS AN EXTERNAL QUALIFICATION, AND THE CHECK V2RG'S MINORS (5 October 2026; C-PROT rev 1)")
    p("   26a. THE GUARD WITHDRAWN AS THE QUALIFICATION (V2RG-B1, the SECOND negative check of the lead treatment: the loop ENDS; RECORD)")
    p("     holding the pair's two thermocouples equal across a heated span does not null the flux at the joint: with equal ends the joint gives")
    p("       or takes half the span's net source, the curvature this record wrote for option (b) and left out of (a); V2RG's fin model (as")
    p("       received, its own orders): %s to %s mW a lead at a 0.05 m guard, %s to %s at 0.1 m, %s to %s at 0.2 m, against round 15's 14.9 mW;"
      % tuple(fmt(x * 1e3, 0) for x in S["v2rg"]["q_005"] + S["v2rg"]["q_01"] + S["v2rg"]["q_02"]))
    p("       further terms of the order of 10 to 70 mW of either sign (the span's heater density, TC2's placement, the crimp and the palm's")
    p("       contact heat, the palm's spread, the wires); round 15's V8 judged the controller's state, not the joint's heat flow. The guard")
    p("       stays only as construction guidance (26c); V2RG-B1 stays OPEN as a SUPPLIER QUALIFICATION item (the coordinator's diagnosis)")
    p("   26b. THE FIXTURE REQUIREMENT AND ITS DEMONSTRATION (SESSION; the requirement is the supplier's scope)")
    p("     REQUIREMENT: the net heat flow at each heating lead's joint into or out of the coupon, in calibration, heating and sensing, at most")
    p("       %s mW a lead, its measurement's own uncertainty included (SELECTED, SESSION; reversed by the supplier's demonstration: a smaller"
      % fmt(R16_Q_SEL * 1e3, 0))
    p("       demonstrated residual relaxes the target, a larger one re-trades the allowance against it)")
    p("     DEMONSTRATION, on the actual fixture before any coupon run, the supplier's choice of method with its uncertainty counted: (i) a")
    p("       measured residual, three thermocouples on each lead's copper over an unheated, lagged span, the joint's flux k A (3 T0 - 4 Tmid +")
    p("       TL) / L (with the ends equal V2RG's 4 k A (T0 - Tmid) / L), its resolution %s mW at a %s K match over %s mm (proposal); or (ii) a"
      % (fmt(S["demo_u"] * 1e3, 2), fmt(R16_DEMO["dt"], 2), fmt(R16_DEMO["l"] * 1e3, 0)))
    p("       reference coupon of known thermal impedance run in the fixture, the leads' effect read on it directly; at the run's currents (0 to")
    p("       22.46 A), its joint temperatures (up to 60 K over the air) and every state; the demonstration's instruments, or a run-time")
    p("       monitor the demonstration validates, stay on the fixture for the runs")
    p("     V8 RESTATED: in every case at its steady endpoint, each heating lead's measured net heat at its joint, plus its uncertainty, at most")
    p("       the requirement; else INCONCLUSIVE (it judges the residual, not a controller's state)")
    p("   26c. CONSTRUCTION GUIDANCE (recommendations from V2RF and V2RG, NOT the qualification; SESSION): a heater beyond the pair, the span from the")
    p("     joint unheated and lagged; TC2 on the copper under a thin film; a mid-span thermocouple; the palm's loss with its spread; the crimp's")
    p("     and the palm contact's heat read four-wire; the thermocouple wires routed along the lead; a DC (linear) drive from a floating supply,")
    p("     or the drive held through each reading window (V2RG-m5); a guard long enough (V2RG's model: under 4 mW at 0.5 m); the band supply's")
    p("     leads the service's pack conductors' stand-in (V2RG-m4)")
    p("   26d. THE ALLOWANCE'S COST: each reading may carry the leads' effect of either sign, (2 leads) x (the allowance) x Z_kJ, Z_kJ at")
    p("     its bound Zself for PLANNING (a run reads its own by reciprocity); line 2 takes differences against the baseline, so the bound")
    p("     enters it %s times a reading's; the direct line takes it once (INFERRED). Two levers relax the target, neither adopted here: a run's"
      % fmt(S["amplify"], 2))
    p("     own Z_kJ (read by reciprocity, likely well under Zself), and a supplier who reads the residual in every case and corrects each")
    p("     reading by it, leaving only that reading's uncertainty (the supplier's to propose)")
    for r_ in S["trade"]:
        p("     the allowance %s mW a lead: each junction's Zw at most %s K/W (Zself %s, S %s K/W at m 0.1); line 2 %s K, U %s K, the leads' bound %s K"
          % (fmt(r_["q"] * 1e3, 0), fmt(r_["zw"], 2), fmt(r_["s"], 2), fmt(r_["s"] * 1.2, 2), fmt(r_["l2"], 2), fmt(r_["u"][1], 2), fmt(r_["lb"][1], 2)))
    p("     SELECTED %s mW: the target Zw %s K/W (Zself %s, S %s K/W at m 0.1), R17 at most %s K/W, the pours %s mOhm (term %s K); line 2 at it"
      % (fmt(R16_Q_SEL * 1e3, 0), fmt(sel["zw"], 2), fmt(sel["s"], 2), fmt(sel["s"] * 1.2, 2), fmt(S["z17_t"], 3), fmt(R15_RP * 1e3, 2), fmt(S["pours_t"], 2)))
    p("       %s K, U %s K, the leads' bound %s K; line 1 U %s K/W, its bound %s K/W; the direct line U %s K (round 15's %s K without the power"
      % (fmt(sel["l2"], 2), fmt(sel["u"][1], 2), fmt(sel["lb"][1], 2), fmt(sel["u"][0], 2), fmt(sel["lb"][0], 2), fmt(S["u3"], 2), fmt(S["u3_old"], 2)))
    p("       terms at the same reading, V2RG-m2), its leads' bound %s K" % fmt(S["lb3"], 2))
    p("     the verdict, the TRUE line-2 figure at chosen points, each line read at its edges with the leads' effect at its bound (+, 0, -):")
    for r_ in S["table"]:
        yn = lambda v: "PASS" if v else "FAIL"
        p("       %-40s true %s K (U %s K, leads %s K): high %s, exact %s, low %s"
          % (r_["lab"] + ":", fmt(r_["true"], 2), fmt(r_["u"], 2), fmt(r_["lb"], 2), yn(r_["high"]), yn(r_["exact"]), yn(r_["low"])))
    p("   26e. THE MINORS (RECORD, INFERRED)")
    p("     m1: the page's row E11-29 written from e11_29_method; the target stated as Zw (Zself only for three side by side at m 0.1); a test")
    p("       compares every page row's figures with the script's")
    p("     m2: the direct line's U %s K with the FETs' and R17's 1 %% powers and the lot correction (%s K without them at the same reading;"
      % (fmt(S["u3"], 2), fmt(S["u3_old"], 2)))
    p("       round 15 printed %s K at its own target)" % fmt(R["S25"]["u3"], 2))
    p("     m3: a coupon exactly at the limit (line 2's true figure %s K) passes %d of %d draws from the budget (%s %%), from the record's own"
      % (fmt(S["mc_true"], 2), S["mc"][0], S["mc"][1], fmt(100.0 * S["mc"][0] / S["mc"][1], 2)))
    p("       functions with lines 1 and R17 passing with room; round 15's 'about 2.5 %' was a conservative misstatement")
    p("     m4: the band supply's leads stand for the service's pack conductors: their cross-section, insulation, length and termination a")
    p("       recorded boundary of the comparison rule (SESSION)")
    p("     m5: any heater on a lead driven by a floating DC supply, or its drive held through each reading window; any such heater in the")
    p("       pickup check of step 6, in the census and in V3")
    p("     m6: at 34.48 uA the device under test carries 965.5 uA, %s times the largest other conductor; the test docstrings restated"
      % fmt(S["ratio_m6"], 1))
    p("   26f. STATUS (SESSION): V2RG-B1 OPEN as a supplier qualification item (the fixture requirement, the supplier's scope); the minors")
    p("     answered; TP-E11-29 NOT EXECUTABLE until L4-E9 restates R-159 and a supplier agrees in writing, and ready to be PUT to a supplier")
    p("     for that agreement with the fixture requirement as its scope; the lead treatment's design loop is ended")
    p("")


def e11_29_method(R):
    """E11-29's method and acceptance as they now stand (round 13's method, round 14's fixture and pass lines): one text, for the row of
    section 8 and the page's row."""
    S, S9, S24, S21 = R["S23"], R["S19"], R["S24"], R["S21"]
    return ("the method (round 13, section 23, after the owner's supplier-delta review's DELTA-02: the three body diodes are in parallel, so "
            "the earlier 'each FET heated through its body diode alone, each junction by its own VSD' is WITHDRAWN): on a coupon with board A's "
            "drain and source pours unchanged and the three gates brought out apart, one channel conducts at a time, selected by its gate, the "
            "current entering at the source so the other two are off and their body diodes reverse-biased; each device's heating power is the "
            "supply's current times that device's own source-to-drain voltage on four-wire taps; each junction is read by that device's "
            "threshold voltage at %s mA with its gate tied to its own drain tap, the other gates on the source, against a K-factor calibrated in "
            "an oven in the same connection, the heating supply isolated from the pours by a series switch for every reading (round 14, section "
            "24b, the recheck V2R's V2R-B1: a bypass across the supply joined the pours and is WITHDRAWN), a gate tied only while that switch is "
            "open by its own state (round 15, section 25c), the net heat flow at each heating lead's joint at most %s mW a lead in "
            "calibration, heating and sensing, a REQUIREMENT ON THE SUPPLIER'S FIXTURE that the supplier demonstrates on the actual "
            "fixture before any coupon run (round 16, section 26b; the check V2RG's V2RG-B1 stays OPEN as that qualification; round 15's "
            "guard is construction guidance only); cases: each FET alone at %s W and at "
            "%s W (the 3 x 3 matrix of Zself and Zmut over step 6's baseline, its reciprocity checked), the three evenly, the worst split for "
            "each row of the measured matrix (each FET in turn) and the fixed split %s / %s / %s W by time division in slots of at most %s us, "
            "the band carrying %s A and R17 dissipating in place; acceptance (round 14, section 24d, V2R-B2), each line the reading plus its "
            "achieved expanded uncertainty: each junction's worst-split figure at its OWN m_k (C_k the largest term of its row, D_k the sum of "
            "the other two, m_k = D_k / (2 C_k): 9 C_k^2 / (4 (2 C_k - D_k)) under m_k 1/4, else C_k + D_k; that is, its S_k against section "
            "21b's bar at m_k) at most %s K/W, so each (Zself + 2 Zmut) at most %s K/W without m; THE LIMIT, each junction's baseline rise "
            "(the band and the neighbours' dummies on) plus R17's coupling times %s W plus %s W times its worst-split figure plus the bounds for "
            "the pours' service loss (Zself times (23.93 A)^2 times the pours' measured largest paths) and the leads' bound (each reading's "
            "net heat at the joints, of either sign, times the joint-to-junction impedance read by reciprocity, carried through the "
            "reduction), at most "
            "%s K over the air, and the same read directly at each row's worst split; R17's coupling at most %s K/W; step 14's bar at the "
            "largest Zmut over the largest Zself WITHDRAWN; each line's U propagated through the reduction from the budget's sources (round 15, "
            "section 25f; on a coupon at the design target %s %% on line 1, %s %% on line 2, %s K/W on R17's line, %s K on the direct line; "
            "round 14's single 3.47 %% withdrawn); the design target (round 16, section 26d, with the leads' allowance): the two pours' "
            "largest paths summed at most %s mOhm (a layout requirement), each junction's worst-split figure Zw at most %s K/W (Zself %s K/W "
            "for three side by side at m 0.1), R17's coupling at most %s K/W, so lines 1 and 2 pass with twice their U and twice the leads' "
            "bound; the PTC's site (RT1's land at the drain "
            "tabs' centroid) read by a thermocouple in every case and its gradient to the hottest junction RECORDED for record l9stk's guard"
            % (fmt(R13_B["i_m"] * 1e3, 0), fmt(R16_Q_SEL * 1e3, 0), fmt(S["p"]["even"], 3), fmt(S["p"]["hot"], 3), fmt(S["p"]["hot"], 3), fmt(S["p"]["other"], 3),
               fmt(S["p"]["other"], 3), fmt(R13_B["slot"] * 1e6, 0), fmt(S9["i"], 2), "%.2f" % S24["K"]["bar_even"], "%.2f" % S21["bar_new"],
               fmt(S24["K"]["p17"], 2), fmt(S24["K"]["p_even"], 3), fmt(S24["K"]["rise"], 2), fmt(S9["r17_allow"], 1),
               fmt(R["S26"]["sel"]["u"][0] / R["S26"]["sel"]["zw"] * 100, 1), fmt(R["S26"]["sel"]["u"][1] / R["S26"]["sel"]["l2"] * 100, 1),
               fmt(R["S26"]["sel"]["u"][2], 2), fmt(R["S26"]["u3"], 2), fmt(R15_RP * 1e3, 2), fmt(R["S26"]["sel"]["zw"], 2),
               fmt(R["S26"]["sel"]["s"], 2), fmt(R["S26"]["z17_t"], 2)))


R17_C_TOL = 0.10        # SESSION (round 17): the guard's capacitors at +-10 % (record l8p's C_TOL, an X7R K grade; the value text prints none)


def fix27_round(R, T):
    """Round 17 (the check V6's V6-m2, record l8p's L8P-R8-F1): DD-7 on a board A that carries record l8p's thermal guard in RT1's
    place. Section 20c's and 20f's rows restated for the guard's fixed pair, its shunt, its 30 uA and its input capacitor C261, the
    owed readings of 23g taken, and the DD-7 netlist check's LOOP group restated (check_dd7_netlist.py)."""
    S20 = R["S20"]
    S = {}
    c4 = flat(text("l8p_c4"))
    m = need(c4, r"the pair intact: \(a\) on: .*? \(c\) tripped: ([\d.]+) mA through the shunt at the clamp, the return ([\d.]+) mV", "the guard's tripped return (l8p 4)")
    S["trip"] = (float(m.group(1)) / 1e3, float(m.group(2)) / 1e3)
    m = need(c4, r"one of the pair shorted: \(a\) on: .*? \(c\) tripped: ([\d.]+) mA through the shunt at the clamp, the return ([\d.]+) mV", "one shorted (l8p 4)")
    S["trip1"] = (float(m.group(1)) / 1e3, float(m.group(2)) / 1e3)
    m = need(c4, r"the return at DOCK_EN_OUT ([\d.]+) V: ([\d.]+) V \(([\d.]+) V all doubled\) against ([\d.]+) V: HOLDS", "the window on the full count (l8p 3)")
    S["win"] = tuple(float(x) for x in m.groups())
    m = need(c4, r"board A's (\d+) kOhm and the guard's\s+(\d+) uA on DOCK_EN_OUT", "the guard's draw on DOCK_EN_OUT (l8p 4)")
    S["i_guard"] = float(m.group(2)) * 1e-6
    need(c4, r"\(L8P-D9\); that label is WITHDRAWN", "record l8p's round 9 (V6-m7, the owner's part 22)")
    need(c4, r"DISPOSITION \(10c, after the recheck cx46: CORRECTIONS NOT CLOSED, the method ends\)", "record l8p's round 9 delta (part 22, cx45 Q5, cx46)")
    g = flat(text("l8p_thguard"))
    need(g, r'r\("R260", "7\.5k 1%", "DOCK_EN_OUT", "THG_MID"\); r\("R261", "7\.5k 1%", "THG_MID", "DOCK_EN_RET"\)', "the guard's pair")
    m = need(g, r'c\("C261", "(\d+(?:\.\d+)?)u 50V X7R", "DOCK_EN_OUT", "GND"\); c\("C262", "(\d+(?:\.\d+)?)u 16V X7R", "THG_VDD", "GND"\)', "the guard's capacitors")
    S["c261"], S["c262"] = float(m.group(1)) * 1e-6, float(m.group(2)) * 1e-6
    S["pair"] = 15e3
    r_feed = R["S19"]["r_feed"]
    r_oload = R10_OUT[0] + R10_OUT[1]
    # 20c: the pulled loop's DOCK_EN_OUT with the return held at the guard's tripped level, the guard's 30 uA drawn from DOCK_EN_OUT,
    # R106 at +1 %, the pair at -1 % (the most current into the held node), board A's divider on it (INFERRED)
    rows = []
    for vin in (7.6, 10.6, 16.8):
        rf = r_feed * 1.01
        rp = S["pair"] * 0.99
        held = max(S["trip"][1], S["trip1"][1])
        vout = (vin / rf + held / rp - S["i_guard"]) / (1 / rf + 1 / r_oload + 1 / rp)
        rows.append((vin, vout))
    S["pulled"] = rows
    # 20f: a docking with C261 on DOCK_EN_OUT and U61 in dropout passing its output capacitor (both at +10 %): the time constant (MODEL)
    S["tau"] = r_feed * 1.01 * (S["c261"] + S["c262"]) * (1 + R17_C_TOL)
    S["ratio"] = S["win"][2] / S["win"][0]
    S["sag"] = S["i_guard"] * r_feed * 1.01
    S["held_ok"] = max(S["trip"][1], S["trip1"][1]) < S20["ret_low"]
    S["powered_ok"] = all(v > S20["out_rel"][1] for _vin, v in rows)
    S["window_ok"] = S["win"][2] >= S20["ret_high"] - 5e-4 and S["win"][1] >= S20["ret_high"]
    return S


def render_fix27(R, p):
    S, S20 = R["S27"], R["S20"]
    p("")
    p("27. ROUND 17: DD-7 ON A BOARD A THAT CARRIES THE THERMAL GUARD (the check V6's V6-m2 on candidate 7a82e82a; record l8p's L8P-R8-F1; C-PROT rev 1)")
    p("   V6 (an AI review; RECORD) found this record's DD-7 netlist check reading FAIL on any board A that carries record l8p's guard (it")
    p("     required RT1 on DOCK_EN_RET and DOCK_EN_OUT), and the guard's C261 and 30 uA counted in no row of 20c or 20f. Record l8p's round 8")
    p("     drafted the guard (apply_gen_sch_a_thguard.py, after DD-7) and its rounds 8 and 9 judged it (l8p_c4.out). Nothing here changes a")
    p("     circuit (RECORD, INFERRED)")
    p("   27a. 20c RESTATED WITH THE GUARD (23g's OWED READINGS TAKEN)")
    p("     the guard's pulled level: tripped, the return %s V (%s V with one of its pair shorted; record l8p 4 (c), at the clamp, the shunt's" % (
        fmt(S["trip"][1], 4), fmt(S["trip1"][1], 4)))
    p("       on-resistance ASSUMED 17.2 ohm) against board A's held reading under %s V: %s; DOCK_EN_OUT stays powered, so a trip IS DD-7's trigger" % (
        fmt(S20["ret_low"], 4), "read held" if S["held_ok"] else "NOT read held"))
    p("     the pulled loop's DOCK_EN_OUT with the return at %s V, the guard's %s uA drawn from it, R106 +1 %%, the pair -1 %%, board A's %s kOhm:" % (
        fmt(max(S["trip"][1], S["trip1"][1]), 4), fmt(S["i_guard"] * 1e6, 0), fmt((R10_OUT[0] + R10_OUT[1]) / 1e3, 0)))
    for vin, v in S["pulled"]:
        p("       BRK_VIN %4s V: %s V against the powered reading's %s V at most: %s" % (fmt(vin, 1), fmt(v, 3), fmt(S20["out_rel"][1], 3),
                                                                                       "read powered" if v > S20["out_rel"][1] else "NOT read powered"))
    p("     the window with the guard (record l8p 3, on the full count of sinks, its shunt's off leakage among them): the return %s V (%s V all" % (
        fmt(S["win"][1], 3), fmt(S["win"][2], 3)))
    p("       doubled) at DOCK_EN_OUT %s V against the closed reading's %s V: a ramping closed loop never reads held (RET/OUT at least %s with every" % (
        fmt(S["win"][0], 3), fmt(S20["ret_high"], 2), fmt(S["ratio"], 4)))
    p("       sink doubled, over RT1's 0.4603 bound); the trigger at 20c's corner stops a dead pack's precharge only on record l8p's single")
    p("       failure of 10b (Q60's gate on its drain: the return 0.799 V there, RECORD); record l8p withdrew its label L8P-D9 (part 22) and")
    p("       drafts a cold clamp under which that short holds the return low and trips (its 10c; with its path 2, section 28 below)")
    p("     the release against the hold and section 22's bleed: a trip is the hot bound itself, already 22's case; the kit through a trip with a")
    p("       source present: the breaker off and the battery FETs inhibited until CELL+ reads alive and the guard cools under its release")
    p("       (record l8p 9 (e)); nothing new acts")
    p("   27b. 20f RESTATED WITH THE GUARD (C261 and the 30 uA on DOCK_EN_OUT)")
    p("     a docking: BRK_VIN steps through R106 onto DOCK_EN_OUT, which now carries C261 (%s uF) and, through U61 in dropout, its output's C262" % (
        fmt(S["c261"] * 1e6, 1)))
    p("       (%s uF): the rise's time constant about %s ms (both at +10 %%, MODEL), slower than RT1's loop; the return follows DOCK_EN_OUT through" % (
        fmt(S["c262"] * 1e6, 1), fmt(S["tau"] * 1e3, 0)))
    p("       the pair resistively, so RET/OUT stays at %s or more at every instant of the rise: no trigger. The 30 uA lowers DOCK_EN_OUT by at" % fmt(S["ratio"], 4))
    p("       most %s V (R106 +1 %%), counted in 27a's pulled readings; at power-up U47 and U48 still hold asserted for tSD (2 ms at most); the" % fmt(S["sag"], 3))
    p("       breaker's start comes no sooner than the RC hold's least 0.110 s after mating (record l8p 9 (e)), after the rise")
    p("     10 A held, 18 A for 60 s: the guard stays closed on the switch's printed no-trip side (record l8p 9 (a): 38.4, 9.8 and 6.0 K), so")
    p("       board A reads the return closed; 23g's 'whether the guard stays closed in the service is not printed' is read on the guard's")
    p("       printed limits, on record l9stk's junctions (RECORD; L8P-F07 stays OPEN in record l8p until its independent check)")
    p("   27c. THE DD-7 NETLIST CHECK'S LOOP GROUP RESTATED (check_dd7_netlist.py round 17): the loop's element is RT1 or the guard's pair, never")
    p("     both, never neither; with the guard DOCK_EN_RET reaches J_DOCK, R261, Q44, U48 and Q60, DOCK_EN_OUT J_DOCK, R260, R109, U61 and C261,")
    p("     THG_MID R260, R261 and TP62; R260 and R261 7.5k, Q60 a 2N7002 with its drain on the return, U61 a TPS70950 and C261 on DOCK_EN_OUT")
    p("     (test_l4e11 composes board A with the guard after DD-7 and reads DRAWN, and its mutations FAIL)")
    p("   27d. STATUS (SESSION): V6-m2 answered; the guard's reading on DD-7 (23g's OWED READING) taken: %s; no circuit changed by this record"
      % ("its pulled level read held with the loop powered at 7.6, 10.6 and 16.8 V, the window and the docking hold" if (S["held_ok"] and S["powered_ok"] and S["window_ok"]) else "A ROW DOES NOT HOLD"))


def fix28_round(R, T):
    """Round 18 (the check cx45's Q5, record l8p's round 9 for the owner's part 22): 20c and 20f restated with record l8p's fail-safe
    guard (apply_gen_sch_a_thgfs.py): path 1 (round 8's guard with a cold clamp) and path 2 (a second switch on VBAT whose shunt Q61
    pulls DOCK_EN_OUT), the guard's restated draw on DOCK_EN_OUT (cold and tripped) and U61's input capacitors C261 and C268."""
    S20, S27 = R["S20"], R["S27"]
    S = {}
    c4 = flat(text("l8p_c4"))
    m = need(c4, r"Allowances taken: (\d+) uA cold, (\d+) uA tripped", "the fail-safe guard's restated allowances (l8p 10c)")
    S["cold"], S["trip"] = float(m.group(1)) * 1e-6, float(m.group(2)) * 1e-6
    m = need(c4, r"path 2 tripped: Q61 pulls DOCK_EN_OUT; at the 29\.2 V clamp ([\d.]+) mA .*? DOCK_EN_OUT ([\d.]+) mV and the return ([\d.]+) mV",
             "path 2's pulled loop (l8p 10c)")
    S["p2"] = (float(m.group(1)) / 1e3, float(m.group(2)) / 1e3, float(m.group(3)) / 1e3)
    m = need(c4, r"the return ([\d.]+) mV, HELD: the breaker off, DD-7 reads board P's own pull: the fault TRIPS", "the clamp's held return (l8p 10c)")
    S["clamp"] = float(m.group(1)) / 1e3
    need(c4, r"DISPOSITION \(10c, after the recheck cx46: CORRECTIONS NOT CLOSED, the method ends\)", "record l8p's round 9 disposition (cx46)")
    g = flat(text("l8p_thgfs"))
    m = need(g, r'c\("C261", "(\d+)n 50V X7R", "DOCK_EN_OUT", "GND"\);', "the delta's C261")
    S["c261"] = float(m.group(1)) * 1e-9
    m = need(g, r'c\("C268", "(\d+)n 50V X7R", "DOCK_EN_OUT", "GND"\)', "the delta's C268")
    S["c268"] = float(m.group(1)) * 1e-9
    need(g, r'"1": "VBAT", "2": "GND", "3": "NC", "4": "NC", "5": "THG_VDD2"', "path 2's regulator on VBAT")
    need(g, r'\{"1": "THG_G2", "2": "GND", "3": "DOCK_EN_OUT"\}', "path 2's shunt on DOCK_EN_OUT")
    r_feed = R["S19"]["r_feed"]
    r_oload = R10_OUT[0] + R10_OUT[1]
    held = max(S27["trip"][1], S27["trip1"][1], S["clamp"])
    rows = []
    for vin in (7.6, 10.6, 16.8):
        rf = r_feed * 1.01
        rp = S27["pair"] * 0.99
        vout = (vin / rf + held / rp - S["trip"]) / (1 / rf + 1 / r_oload + 1 / rp)
        rows.append((vin, vout))
    S["pulled"] = rows
    S["held"] = held
    # the earlier case the P0 list named (the delta's first form, 50 uA cold and 180 uA tripped), executed on the same rows (cx46 9)
    S["early"] = (50e-6, 180e-6)
    S["pulled_early"] = [(vin, (vin / (r_feed * 1.01) + held / (S27["pair"] * 0.99) - S["early"][1]) / (1 / (r_feed * 1.01) + 1 / r_oload + 1 / (S27["pair"] * 0.99)))
                         for vin in (7.6, 10.6, 16.8)]
    S["sag_early"] = S["early"][0] * r_feed * 1.01
    S["tau"] = r_feed * 1.01 * (S["c261"] + S["c268"] + S27["c262"]) * (1 + R17_C_TOL)
    S["sag"] = S["cold"] * r_feed * 1.01
    S["held_ok"] = held < S20["ret_low"]
    S["powered_ok"] = all(v > S20["out_rel"][1] for _vin, v in rows)
    S["powered_early_ok"] = all(v > S20["out_rel"][1] for _vin, v in S["pulled_early"])
    S["dark_ok"] = S["p2"][1] < S20["out_ast"][0] and S["p2"][2] < S20["ret_low"]
    return S


def render_fix28(R, p):
    S, S20, S27 = R["S28"], R["S20"], R["S27"]
    p("")
    p("28. ROUND 18: 20c AND 20f WITH RECORD l8p's FAIL-SAFE GUARD (the check cx45's Q5 on candidate 06077cee; record l8p round 9, 10c)")
    p("   cx45 (an AI review; RECORD) found 27a and 27b still on round 8's 30 uA and C261 alone; its recheck cx46 read this section's first form")
    p("     CORRECTIONS NOT CLOSED: the method ends and this section is a DISPOSITION (every row PROVISIONAL, nothing closed).")
    p("   THE CHANGED CIRCUIT AND CASE, stated: 27a and 27b judge round 8's guard (one path, its draw 30 uA, C261 1 uF); this section judges")
    p("     record l8p's delta (apply_gen_sch_a_thgfs.py, after the guard, NOT APPLIED), which keeps round 8's shunt Q60 on the return (path 1)")
    p("     with a cold clamp, adds path 2 (a second switch on VBAT whose shunt Q61 pulls DOCK_EN_OUT) and splits U61's input capacitor into")
    p("     C261 and C268 (330 nF each). Its draw on DOCK_EN_OUT: %s uA cold and %s uA tripped (record l8p 10c, RECORD); the delta's FIRST form" % (
        fmt(S["cold"] * 1e6, 0), fmt(S["trip"] * 1e6, 0)))
    p("     (a diode OR, superseded) carried %s uA cold and %s uA tripped, the case the P0 list named: both are executed below. Layer 5's row and" % (
        fmt(S["early"][0] * 1e6, 0), fmt(S["early"][1] * 1e6, 0)))
    p("     record l9stk 15.9 still carry 30 uA: their restatement is the owners' (draft texts on record l8p's page 12o, L8P-R9-F2). Nothing")
    p("     here changes a circuit (INFERRED on 20c's and 27's figures)")
    p("   28a. 20c WITH PATH 1 TRIPPED: the return held at %s V at most (the guard's trip, or the clamp's %s V with Q60's gate on its drain;" % (
        fmt(S["held"], 4), fmt(S["clamp"], 4)))
    p("     RECORD) against the held reading under %s V: %s; the guard's %s uA drawn, R106 +1 %%, the pair -1 %%, board A's %s kOhm:" % (
        fmt(S20["ret_low"], 4), "read held" if S["held_ok"] else "NOT read held", fmt(S["trip"] * 1e6, 0), fmt((R10_OUT[0] + R10_OUT[1]) / 1e3, 0)))
    for vin, v in S["pulled"]:
        p("       BRK_VIN %4s V: DOCK_EN_OUT %s V against the powered reading's %s V at most: %s" % (fmt(vin, 1), fmt(v, 3), fmt(S20["out_rel"][1], 3),
                                                                                                 "read powered" if v > S20["out_rel"][1] else "NOT read powered"))
    p("     so a trip of path 1 IS DD-7's trigger, as in 27a; the earlier case (%s uA tripped), the same rows:" % fmt(S["early"][1] * 1e6, 0))
    for vin, v in S["pulled_early"]:
        p("       BRK_VIN %4s V: DOCK_EN_OUT %s V: %s" % (fmt(vin, 1), fmt(v, 3), "read powered" if v > S20["out_rel"][1] else "NOT read powered"))
    p("   28b. 20c WITH PATH 2 TRIPPED: Q61 holds DOCK_EN_OUT at %s mV and the return at %s mV at the 29.2 V clamp (record l8p 10c, RECORD, its" % (
        fmt(S["p2"][1] * 1e3, 1), fmt(S["p2"][2] * 1e3, 1)))
    p("     on-resistance ASSUMED): DOCK_EN_OUT under the unpowered reading's least %s V and the return under %s V: DD-7 reads the loop dark, the" % (
        fmt(S20["out_ast"][0], 3), fmt(S20["ret_low"], 4)))
    p("     state of an undocked pack: %s; board P's first inverter reads the return low and turns the breaker off" % (
        "no trigger" if S["dark_ok"] else "A ROW DOES NOT HOLD"))
    p("   28c. THE WINDOW: unchanged (27a): the clamp sits on Q60's gate and path 2's shunt on DOCK_EN_OUT, so the sinks on the return are 27a's;")
    p("     a sink on DOCK_EN_OUT does not move the return against DOCK_EN_OUT")
    p("   28d. 20f WITH THE DELTA (INFERRED): a docking steps BRK_VIN through R106 onto DOCK_EN_OUT, which carries C261 and C268 (%s and %s uF) and" % (
        fmt(S["c261"] * 1e6, 2), fmt(S["c268"] * 1e6, 2)))
    p("     through U61 in dropout C262 (%s uF): the rise's time constant about %s ms (all at +10 %%, MODEL); path 2's regulator is on VBAT and loads no" % (
        fmt(S27["c262"] * 1e6, 1), fmt(S["tau"] * 1e3, 0)))
    p("     docking; the return follows DOCK_EN_OUT through the pair resistively, so RET/OUT stays at %s or more: no trigger; the cold %s uA" % (
        fmt(S27["ratio"], 4), fmt(S["cold"] * 1e6, 0)))
    p("     lowers DOCK_EN_OUT by at most %s V (R106 +1 %%; %s V at the earlier case's %s uA); the breaker's start comes no sooner than" % (
        fmt(S["sag"], 3), fmt(S["sag_early"], 3), fmt(S["early"][0] * 1e6, 0)))
    p("     the RC hold's least 0.110 s (record l8p")
    p("     10c (e): a hot docking reaches path 1's shunt before it)")
    p("   28e. DISPOSITION (SESSION, after cx46): these rows %s on the delta's intact circuit at both allowance cases; PROVISIONAL, not closed:" % (
        "hold" if (S["held_ok"] and S["powered_ok"] and S["powered_early_ok"] and S["dark_ok"]) else "DO NOT ALL HOLD"))
    p("     record l8p's L8P-R9-F1 (a latent first failure and a second remove the trip; with path 1 lost, path 2's retry heating is unbounded)")
    p("     weakens every protection claim here, and the allowance consumers (Layer 5's row, record l9stk 15.9) are unrestated (L8P-R9-F2).")
    p("     REMAINING ENGINEERING: the replay of the dependent start-up and protection rows (20f's timing against U47's and U48's tSD at the")
    p("     owners' restated allowance, 22's bleed with path 2's VBAT load) once the owners restate the allowance")


# ============================================================================================ the output
def render(R):
    out = []
    p = out.append
    B, P, E, C, F, D, T9, N = R["B"], R["P"], R["E"], R["C"], R["F"], R["D"], R["T9"], R["N"]
    p("L4-E11: SOURCE-ONLY AND DEAD-PACK OPERATION (U-04), THE VEHICLE-ENTRY INTERCONNECT (D-06) AND THE HOT SWAP'S FAULT TIMER (D-09)")
    p("MESHSAT-1357, 2 October 2026. Prototype design, desk arithmetic: nothing is bought, built, powered or measured. Classes: MAKER,")
    p("CATALOGUE, NETLIST, REQUIREMENT, RECORD, INFERRED, CONDITIONAL, ASSUMPTION, SESSION.")
    p("")
    p("0. INPUTS (sha256/16)")
    for k, rel, s in R["inputs"]:
        p("   %-9s %s  %s" % (k, s[:16], rel))
    for k, rel, s in R["git_inputs"]:
        p("   %-9s %s  %s (L4-E9's commit, read with git show)" % (k, s[:16], rel))
    for k, (who, rel, s) in sorted(R9_GIT.items()):
        p("   %-9s %s  %s:%s (record %s's commit, read with git show; round 9)" % (k, s[:16], R9_COMMITS[who][:8], rel, who))
    for name, s in R["filed"]:
        p("   filed     %s  %s/inputs/%s" % (s[:16], REC, name))
    for t, h, _held in PT.inputs(TOP, PDFTEXT):
        p("   %-9s %s  %s" % ("pdftext", (h or "ABSENT")[:16], t))
    p("   this record's own figures: copper %s ohm mm2/m at 20 C and %s /K, %s J/cm3K (ASSUMPTION, constants); AWG 14 %s mm2, AWG 12 %s mm2,"
      % (CU_RHO_20, CU_ALPHA, CU_CV, AWG14_MM2, AWG12_MM2))
    p("     AWG 18 %s mm2 (ASSUMPTION, constants); the cold end %s C (REQ-024); the SESSION choices are named where they are used" % (AWG18_MM2, fmt(T_COLD)))
    p("")
    p("1. U-04, WHAT THE REQUIREMENTS DEMAND OF SOURCE-ONLY OPERATION (quoted, not reinterpreted)")
    p("   REQ-015 statement: \"%s\" (REQUIREMENT)" % R["req015"][0])
    p("   REQ-015 acceptance: \"%s\" (REQUIREMENT)" % R["req015"][1])
    p("   REQ-014: \"%s\" (REQUIREMENT)" % R["req014_clause"])
    p("   REQ-024: \"%s\" (REQUIREMENT)" % R["req024_clause"])
    p("   TEST-PLAN E4-O (REQ-024's acceptance): \"%s\" (REQUIREMENT)" % R["e4o"])
    p("   REQ-046: \"%s\"; its acceptance: \"%s\" (REQUIREMENT)" % (R["req046"], R["req046_hold"]))
    p("   REQ-077 acceptance: \"%s\" (REQUIREMENT)" % R["req077_clause"])
    p("   REQ-072 (obligation %s): \"%s\" (REQUIREMENT)" % (R["req072_obl"], R["req072_clause"]))
    p("   requirement | obligation | source voltage named | names a load state | the source-only content")
    for rid, ob, v, st, what in R["req_rows"]:
        p("     %-16s | %-9s | %s | %s | %s (REQUIREMENT)" % (rid, ob, v, "yes" if st else "no", what))
    p("   So: no mandatory requirement names a load state (a PS- profile or a wattage) for the kit on a source alone, at any")
    p("     source voltage; REQ-015's \"runs the kit and charges the pack\" names neither the load nor the pack's state, and \"9 V\"")
    p("     is not tied to a measuring point. PS-IDLE-SPEC enters only through REQ-072, an objective. What the mandatory text does")
    p("     demand of a source alone: a start and a warm-up of a cold-soaked pack whose FETs are open (REQ-024, D-02d, REQ-046,")
    p("     E4-O), and the charger carrying the kit with its charge held (REQ-077, a pack present). (INFERRED from the quotes)")
    p("")
    p("2. U-04, THE CHARGER AND THE PACK WITH NO USABLE PACK")
    p("   BQ25731 (SLUSE66A), what the sheet states:")
    p("     no battery MOSFET (p.%d); from VBUS: registers, cell count, then \"Converter powers up.\" with no battery condition (9.3.1, p.%d) (MAKER)" % (B["nobatfet"], B["powerup"]))
    p("     power-up curves drawn \"2-cell without battery\", Figures 10-4 and 10-5 (p.%d) (MAKER)" % B["fig104"])
    p("     \"%s\" (11, p.%d) (MAKER)" % (B["sec11_text"], B["sec11"]))
    p("     CHRG_OK's conditions name VBUS and the faults, not the battery: \"%s\" (9.3.4, p.%d) (MAKER)" % (B["chrgok_text"], B["chrgok"]))
    p("     DPM: the charge falls first, then \"the system voltage starts to drop\" and the battery supplements (9.3.17, p.%d) (MAKER)" % B["dpm"])
    p("     4S defaults: ChargeVoltage %s V, SYSOVP %s V, VSYS_MIN %s V (Table 9-2, p.%d); below VSYS_MIN at SRN the charge is clamped at %s mA, a typical figure with no minimum or maximum printed (8.5, p.%d) (MAKER)"
      % (fmt(B["cv4s"]), fmt(B["sysovp4s"]), fmt(B["vsysmin4s"]), B["t92"], fmt(B["iclamp"] * 1000), B["iclamp_p"]))
    p("     in the BATOVP paragraph: with charge enabled the converter shuts down; \"if charge is disabled the converter should keep operating without disturbance\"")
    p("       (9.3.21.5, p.%d): a statement about a battery over-voltage event, not a specification of VSYS's regulation or transient response with no battery (N1, N2) (MAKER, context kept)" % B["batovp"])
    p("     HIZ: \"converter shuts off\" with ILIM_HIZ under %s V (9.3.8, p.%d) (MAKER)" % (fmt(B["hiz_v"]), B["hiz_p"]))
    p("     VSYS under %s V for 2 ms in steady state: \"shut down and latched off\" until a host write (9.3.21.8, p.%d) (MAKER)" % (fmt(B["uvp_v"]), B["uvp_p"]))
    p("     \"Overall %s-uF effective capacitance on VSYS net is necessary\" (10.1, p.%d); CHRG_INHIBIT \"1b: Inhibit Charge\" (p.%d); the host ends a charge by CHRG_INHIBIT or ChargeCurrent 0 (9.4.1, p.%d) (MAKER)"
      % (fmt(B["csys_uf"]), B["csys_p"], B["inhibit_p"], B["term_p"]))
    p("     AUTO_WAKEUP_EN, 0 at POR: with it set, a battery under VSYS_MIN gets %s mA for %s min with no further host write (p.%d) (MAKER); it needs a host write first, so it does not answer N3"
      % (fmt(B["wake_ma"]), fmt(B["wake_min"]), B["wake_p"]))
    p("     ChargeCurrent at POR: the register description says 0 A, its reset value encodes 256 mA, and TI's expert on E2E thread 1316778 (held) states %s mA,"
      % fmt(R["G"]["por_ma"], 0))
    p("       the description being in error (the dependency round, D4) (MAKER)")
    p("     ChargeCurrent with the 5 mOhm RSR: 128 mA steps; REG0x03/02 = 0x0200 (1024 mA) regulates within -%s %% to +%s %%, a row printed for VBAT above VSYS_MIN (8.5, p.10) (MAKER)"
      % (fmt(N["rb_err"][0] * 100, 0), fmt(N["rb_err"][1] * 100, 1)))
    p("   board A and E as generated: the strap R26 %sk over R27 %sk, %s %% of VDDA, so U3 never sees \"battery removal\"; R17 between VBAT"
      % (fmt(R["strap"][0], 1), fmt(R["strap"][1], 1), fmt(R["strap"][2], 1)))
    p("     (VSYS, every load) and CELL_FUSED (the pack); CHG_INHIBIT pulls ILIM_HIZ low through Q6 (HIZ); SHORE_INHIBIT pulls the hot")
    p("     swap's UVLO low through Q8 (the input off); board P's gauge PCHG pin not connected; R7 1 k from PACK_P to its VCC (NETLIST)")
    p("     FW-C08 as written: \"%s\" (RECORD, HW-FW-CONTRACT)" % R["fwc08"])
    p("     FW-A14 as written: \"%s\" (RECORD); PANEL.md 10: \"%s\" (RECORD)" % (R["fwa14"], R["panel10"]))
    p("   the pack (SLUUAQ3A and this tree's image):")
    p("     a CUV trip sets OperationStatus()[XDSG] only (2.2, p.%d): the discharge FET opens, the charge FET stays (MAKER)" % P["cuv_p"])
    p("     XDSG also on UTD, XCHG on UTC (4.12, p.%d); the image's UTD %s C and UTC %s C (pcb_pack_protection.yaml): below %s C both FETs are open (MAKER, RECORD)"
      % (P["xdsg_p"], fmt(P["utd"]), fmt(P["utc"]), fmt(P["utd"])))
    p("     precharge by the external FET or the CHG FET per PCHG_COMM (4.9, p.%d), default 0 = PCHG FET (14.2.1.1, p.%d); board P has no PCHG FET and"
      % (P["pchg_p"], P["pchgbit_p"]))
    p("     the image writes FET Options 0x3D, PCHG_COMM 1 (PRIMARY-CONFIGURATION.md); Shutdown Voltage %s mV; CUV %s V, recovery %s V; pre-charge %s A (MAKER, RECORD)"
      % (fmt(P["shutdown_mv"]), fmt(P["cuv"], 2), fmt(P["cuv_rec"], 2), fmt(P["pre_a"])))
    p("     Q2's body diode carries the charge while XDSG: VSD at most %s V at %s A, RthetaJA at most %s C/W on 1 in2 2 oz, TJ %s C (CSD17570Q5B p.%d) (MAKER)"
      % (fmt(P["vsd_max"]), fmt(P["vsd_i"]), fmt(P["rja"]), fmt(P["tj_max"]), P["vsd_p"]))
    for i, w, dt in P["q2"]:
        p("       at %s A: at most %s W, %s K over the air (INFERRED: VSD's row at %s A bounds it at less current; board P's copper an ASSUMPTION)"
          % (fmt(i, 3), fmt(w, 3), fmt(dt, 1), fmt(P["vsd_i"])))
    p("       at R-b's %s A (below): at most %s W, %s K, so TJ %s C at the %s C inside air against %s C (CONDITIONAL: on R-b's bound holding, below, and"
      % (fmt(N["rb_max"], 3), fmt(N["q2_w"], 3), fmt(N["q2_rise"], 1), fmt(N["q2_tj"], 1), fmt(F["air_hot"], 1), fmt(P["tj_max"], 0)))
    p("         on board P's installed copper giving TI's %s C/W, which TI states for its own 1 in2 2 oz board; INFERRED)" % fmt(P["rja"]))
    p("     the cell maker: pre-charge between %s and %s V a cell at %s to %s C, C = %s A (Samsung 35E p.%d) (MAKER); the charger's %s mA is %s C a cell,"
      % (fmt(P["pre_win"][0], 1), fmt(P["pre_win"][1], 1), fmt(P["pre_c"][0], 1), fmt(P["pre_c"][1], 1), fmt(P["c_a"], 2), P["cell_p"], fmt(B["iclamp"] * 1000), fmt(P["clamp_c"], 3)))
    p("       under the range (a lower current; the maker states no consequence), and a 3.0 A ChargeCurrent is %s C a cell, inside it (INFERRED)" % fmt(P["cc_c"], 3))
    p("   what follows, by pack state (INFERRED from the rows above, the drawn topology and the image):")
    p("     pack absent, or both FETs open (below %s C, SHUTDOWN, a permanent fail): no current through R17, so the voltage loop holds" % fmt(P["utd"]))
    p("       SRN, and VSYS with it, at ChargeVoltage (at most %s V written, s120); the kit is carried up to the input limit (11, 9.3.17) (INFERRED)" % fmt(R["cv_max"], 3))
    p("     pack at CUV, charge FET on: charge through Q2's diode; VSYS = stack + VSD, %s to %s V; %s mA while SRN is under %s V (CONDITIONAL on A-14's 10.0 V floor)"
      % (fmt(P["vsys_cuv"][0], 2), fmt(P["vsys_cuv"][1], 2), fmt(B["iclamp"] * 1000), fmt(B["vsysmin4s"], 1)))
    p("     a pack self-discharged to the Shutdown Voltage: VSYS %s to %s V while it precharges, under the converters' assumed 10.0 V floor (A-14): the loads wait (CONDITIONAL)"
      % (fmt(P["vsys_shut"][0], 2), fmt(P["vsys_shut"][1], 2)))
    p("     the clamp lifts at SRN %s V, a stack of %s V or more (%s V a cell) with VSD at its maximum, before CUV recovers at %s V a cell: in that window"
      % (fmt(B["vsysmin4s"], 1), fmt(P["release_stack"], 2), fmt(P["window"][0], 3), fmt(P["window"][1], 2)))
    p("       ChargeCurrent crosses Q2's diode, so rule R-b (SESSION) permits exactly two settings while the charger's own SRN reading is under %s V or the"
      % fmt(RULE_SRN_V, 1))
    p("       gauge reports XDSG or PRECHARGE: ChargeCurrent() 0x0000 (no charge) and 0x0200 (1024 mA set); no other value, because TI prints no accuracy")
    p("       for any setting under 0x0200 (MAKER, SESSION). The bounds by case (B5; the row's condition: 5 mOhm RSR, VBAT above VSYS_MIN, %s to %s C):"
      % (fmt(N["rb_temp"][0], 0), fmt(N["rb_temp"][1], 0)))
    p("       (i) SRN at or above VSYS_MIN and the charger inside %s to %s C: %s to %s A actual (-%s / +%s %%, R17 at +-1 %%) (MAKER row, INFERRED: BOUNDED)"
      % (fmt(N["rb_temp"][0], 0), fmt(N["rb_temp"][1], 0), fmt(N["rb_min"], 4), fmt(N["rb_max"], 4), fmt(N["rb_err"][0] * 100, 0), fmt(N["rb_err"][1] * 100, 1)))
    p("       (ii) SRN at or above VSYS_MIN with the charger outside %s to %s C: no accuracy printed: INCONCLUSIVE until the charger's temperature in this"
      % (fmt(N["rb_temp"][0], 0), fmt(N["rb_temp"][1], 0)))
    p("            state is bounded inside the row (it sits in the inside air, -20 C at a cold start to %s C hot, plus its own rise, which no held record gives)," % fmt(F["air_hot"], 1))
    p("            or TI states the accuracy outside it, or the bench measures the current at the inside air's ends (E11-22)")
    p("       (iii) SRN under VSYS_MIN: the clamp, %s mA typical with no maximum printed: INCONCLUSIVE until TI states a maximum or the bench measures it (E11-22)"
      % fmt(B["iclamp"] * 1000))
    p("       without the gauge's report the %s V threshold covers a cell up to %s V under the stack's average (%s V a cell) (INFERRED); R-b also holds above %s V"
      % (fmt(RULE_SRN_V, 1), fmt(P["rb_imbalance"], 2), fmt(P["rb_stack"] / P["cells"], 2), fmt(RULE_SRN_V, 1)))
    p("       while the gauge reports XDSG or PRECHARGE, so in case (i) the charge power is at most %s A x %s V = %s W (at the %s V threshold, %s W) (INFERRED)"
      % (fmt(N["rb_max"], 4), fmt(R["cv_max"], 3), fmt(N["dead_charge_w_max"], 2), fmt(RULE_SRN_V, 1), fmt(N["dead_charge_w"], 2)))
    p("     CHG_INHIBIT (HIZ) or SHORE_INHIBIT asserted while the pack cannot discharge: the converter is off, so VSYS has no source and the")
    p("       kit stops; the controllers die, the pull-downs release the line and the kit restarts: a loop (INFERRED: 9.3.8, the UVLO, the netlists)")
    p("     FW-C08 asserts SHORE_INHIBIT below 0 C: with a pack below %s C the source start REQ-024 requires is cut by the hold itself (finding U4-F1, INFERRED)" % fmt(P["utd"]))
    p("   NOT STATED in any held document (named, not inferred): N1 VSYS's regulation and transient response with no battery under the")
    p("     kit's load steps; N2 what the converter regulates with CHRG_INHIBIT = 1 or ChargeCurrent 0 and no battery current (Q-TI-3);")
    p("     N3 whether the charger charges before any host write (Q-TI-2); N4 VSYS's effective capacitance at %s V against TI's %s uF (RECORD, MAKER);"
      % (fmt(R["cv_max"], 3), fmt(B["csys_uf"])))
    p("     N5 every load converter's minimum input (A-14, R-49); N6 0-V charging before the gauge's SUV check (Q-TI-7)")
    p("   THE PACK'S STATES BY PERMISSION (B2; the gauge's own FETs, SLUUAQ3A 2.2 and 4.12) and how a charge hold is made in each (INFERRED):")
    p("     S1 charge on, discharge on: the pack and the source share the kit; a hold by the CHRG_INHIBIT bit or ChargeCurrent 0 (9.4.1) leaves the converter")
    p("        carrying the kit from the source (11): REQ-077 as written")
    p("     S2 charge on, discharge off (a warm CUV trip, or an OCD, AOLD or SCD latch): the source alone carries the kit and the pack can still take charge")
    p("        through Q2's diode, so the gauge does NOT hold the charge; a hold only by the bit or ChargeCurrent 0; whether VSYS stays regulated with charge")
    p("        inhibited while the pack cannot discharge is N2 (Q-TI-3): OPEN, the bench proves it (E11-06)")
    p("     S3 charge off, discharge on (between UTD %s C and UTC %s C; OTC; COV): the gauge holds the charge; a requested hold by the bit as in S1 (REQ-077)" % (fmt(P["utd"]), fmt(P["utc"])))
    p("     S4 charge off, discharge off (below %s C, SHUTDOWN, a permanent fail, or no pack): the source alone carries the kit and the gauge already holds" % fmt(P["utd"]))
    p("        the charge. THE ONE EXCEPTION: in S4 the bit is NOT set and ChargeCurrent() is not written 0, so N2 never arises where the source alone carries")
    p("        the kit with no charge possible; the hold is the gauge's own")
    p("     THE HOLD PERSISTS ACROSS STATES: it is a flag in the firmware, set and cleared only by its own condition (the cold hold above 3 C with hysteresis,")
    p("        the operator, REQ-077's hold), never by a state change; in S1, S2 and S3 the bit follows the flag; on leaving S4 (a FET closing, a pack fitted)")
    p("        the bit is written from the flag at once, and in the firmware's reaction time only the gauge's window acts, which keeps the cells inside their")
    p("        charge window; after a charger POR ChargeCurrent() is %s mA by TI's E2E answer (D4), so a charge at %s mA can begin before the firmware writes the"
      % (fmt(R["G"]["por_ma"], 0), fmt(R["G"]["por_ma"], 0)))
    p("        flag's bit: in that window too only the gauge's window acts, and %s mA is under R-b's bound (INFERRED)" % fmt(R["G"]["por_ma"], 0))
    p("     in S2 and S4 the CHG_INHIBIT line (HIZ, 9.3.8) and SHORE_INHIBIT each remove the kit's only supply: neither is ever a charge hold (rule R-a)")
    p("")
    p("3. U-04, THE ENTRY AT A 9.00 V PLUG, THE KIT'S OWN LOSSES AND THE SOURCE ENVELOPE (the focused check's B1 and B3)")
    p("   3a. the drawn LM5069 against a 9.00 V plug (finding U4-F2, corrected in the fix round)")
    p("     UVLOTH %s / %s / %s V, UVLOHYS %s / %s / %s uA (SNVS452G p.%d); Equations 38 to 40 (p.24): the falling threshold is UVLOTH x (1 + R20/R21),"
      % (tuple(fmt(x, 2) for x in E["uv_rows"]) + tuple(fmt(x * 1e6, 0) for x in E["hy_rows"]) + (E["uvlo_page"],)))
    p("       the rising one that plus UVLOHYS x R20 (MAKER); the first round put the hysteresis on the falling edge, so its numbers and its R21 draft were wrong")
    for lab, (rise, fall) in (("as drawn (R20 %sk, R21 %sk, 1 %%)" % (fmt(E["r20"] / 1e3, 0), fmt(E["r21"] / 1e3, 1)), N["uvlo_drawn"]), ("the withdrawn first-round draft (R21 42.2k)", N["uvlo_withdrawn"])):
        p("     %s: on at %s / %s / %s V rising, off at %s / %s / %s V falling: NOT MET at 9.00 V (INFERRED)" % ((lab,) + tuple(fmt(x, 2) for x in rise) + tuple(fmt(x, 2) for x in fall)))
    p("     POREN (all functions enabled, VIN increasing) %s typical, %s V maximum; PORIT %s / %s V; POREN's hysteresis %s mV typical; the operating range %s to %s V (SNVS452G p.1, p.5) (MAKER)"
      % (fmt(N["poren"][0], 1), fmt(N["poren"][1], 1), fmt(N["porit"][0], 1), fmt(N["porit"][1], 1), fmt(N["poren_hys"] * 1e3, 0), fmt(N["vin_range"][0], 0), fmt(N["vin_range"][1], 0)))
    p("     U6's VIN (pin 2) is DC_P behind the ideal diode (NETLIST); before the hot swap conducts, VIN is at most 9.00 V less the LM74700's regulated drop")
    p("       (%s / %s / %s mV, SNOSD17G) = %s V, under POREN's %s V maximum: no divider makes a 9.00 V plug start the LM5069 (NOT MET, INFERRED)"
      % (fmt(N["vak"][0] * 1e3, 0), fmt(N["vak"][1] * 1e3, 0), fmt(N["vak"][2] * 1e3, 0), fmt(N["vin_ic_max"], 3), fmt(N["poren"][1], 1)))
    p("     with the in-service current flowing DC_P falls further, to %s V at the 9.00 V plug's maximum (3e), under POREN less its %s mV typical hysteresis (INFERRED)"
      % (fmt(N["dcp9"], 2), fmt(N["poren_hys"] * 1e3, 0)))
    p("     the IC cannot be supplied from elsewhere: VIN is the current-sense reference (VCL is the VIN-SENSE voltage, p.5), so it sits at R19's top (MAKER, NETLIST)")
    p("   3b. what a replacement must do (INFERRED; the figures are 3d to 3e's):")
    p("     (1) operate and enable below its own supply at the in-service maximum from a 9.00 V plug, DC_P %s V hot; (2) act on overcurrent between" % fmt(N["dcp9"], 2))
    p("       the in-service maximum at 9 V (%s A) and F1's %s C column (%s A); (3) keep the pass FET inside its derated chart in every start, a start into a"
      % (fmt(N["i9"], 3), fmt(F["f_col"], 0), fmt(F["f_hot_a"], 1)))
    p("       resistive fault included; (4) lock out over-voltage above CS101's %s V peak and under D10's %s V breakdown at -20 C (L4-E9), with a 100 V rating"
      % (fmt(N["cs101_peak"], 2), fmt(N["d10"][1], 1)))
    p("     TPS1663 (SLVSET9G, held back): %s to %s V, %s V absolute; its highest limit (RILIM 3 k) %s / %s / %s A: under %s A, fails (2) (MAKER)"
      % (fmt(N["t63_range"][0], 1), fmt(N["t63_range"][1], 0), fmt(N["t63_abs"], 0), fmt(N["t63_ilim"][0], 2), fmt(N["t63_ilim"][1], 0), fmt(N["t63_ilim"][2], 2), fmt(N["i9"], 2)))
    p("     TPS4811-Q1 (SLUSEE5E, held back): VS %s to %s V, %s V absolute, VS POR %s / %s / %s V; EN/UVLO %s / %s / %s V rising and %s / %s / %s V falling,"
      % ((fmt(N["t48_vs"][0], 1), fmt(N["t48_vs"][1], 0), fmt(N["t48_abs"], 0)) + tuple(fmt(x, 2) for x in N["t48_por"]) + tuple(fmt(x, 2) for x in N["t48_uvr"]) + tuple(fmt(x, 2) for x in N["t48_uvf"])))
    p("       %s nA leakage at most; OV the same thresholds (TPS48110 only); OCP %s / %s / %s mV at RSET 100 Ohm and RIWRN 39.7 k; ISCP bias %s / %s / %s uA (Equation 11,"
      % ((fmt(N["t48_enleak"] * 1e9, 0),) + tuple(fmt(x * 1e3, 1) for x in N["t48_wrn"]) + tuple(fmt(x * 1e6, 1) for x in N["t48_iscp"])))
    p("       464 Ohm); TMR %s / %s / %s uA to %s / %s / %s V, retry 22.7e6 x CTMR after 32 cycles; short-circuit response %s / %s us (TPS48110); charge pump %s to %s V;"
      % (tuple(fmt(x * 1e6, 0) for x in N["t48_tmr_i"]) + tuple(fmt(x, 3) for x in N["t48_tmr_v"]) + (fmt(N["t48_tsc"][0] * 1e6, 0), fmt(N["t48_tsc"][1] * 1e6, 0), fmt(N["t48_cp_on"][0], 0), fmt(N["t48_cp_off"][2], 0))))
    p("       gate-slew inrush 0.63 x V(BST-SRC) x CLOAD / (R1 x C1) (Equation 3); input pins to %s V absolute; TI's 100 Ohm VS filter and 1 nF CSCP (MAKER)" % fmt(N["t48_pin_abs"], 0))
    p("       it meets (1), (2) and (4); it limits no power, so (3) rests on the pass FET (3c)")
    p("     a power-limiting controller that operates under 9 V: none among the held sheets (TI's power-limiting hot-swap family starts at 9 V or above); not drafted (named)")
    en = ENTRY
    p("   3c. SELECTED (SESSION; draft apply_gen_sch_e_entry.py): U6 TPS48110AQDGXRQ1 (LCSC C17556513), Q7 CSD19536KTT (C2687963, D2PAK), R19 %s mOhm 1 %% %s ppm/K"
      % (fmt(en["rsns"] * 1e3, 1), fmt(en["rsns_tcr"] * 1e6, 0)))
    p("     (C2985708), L2 SRF1260-1R0Y (C7084461); RSET %s Ohm and RIWRN %s k at 0.1 %% (C861872), RISCP %s k, CTMR %s nF C0G (C97929), R1 %s k, C1 %s nF C0G 100 V"
      % (fmt(en["rset"], 0), fmt(en["riwrn"] / 1e3, 1), fmt(en["riscp"] / 1e3, 2), fmt(en["ctmr"] * 1e9, 0), fmt(en["r1"] / 1e3, 1), fmt(en["c1"] * 1e9, 0)))
    p("     (C184799), R2 %s Ohm, CBST %s uF; UVLO %s k over %s k, OV %s k over %s k at 0.1 %%, INP %s k over %s k, RVS %s Ohm with %s nF, CSCP %s nF (SESSION, CATALOGUE)"
      % (fmt(en["r2"], 0), fmt(en["cbst"] * 1e6, 0), fmt(en["uv_top"] / 1e3, 1), fmt(en["uv_bot"] / 1e3, 1), fmt(en["ov_top"] / 1e3, 0), fmt(en["ov_bot"] / 1e3, 1),
         fmt(en["inp_top"] / 1e3, 0), fmt(en["inp_bot"] / 1e3, 0), fmt(en["rvs"], 0), fmt(en["cvs"] * 1e9, 0), fmt(en["cscp"] * 1e9, 0)))
    p("     UVLO: on at %s / %s / %s V, off at %s / %s / %s V of DC_P; OV: off above %s / %s / %s V, on again under %s / %s / %s V (INFERRED, the leakage included)"
      % (tuple(fmt(x, 2) for x in N["uv_rise"]) + tuple(fmt(x, 2) for x in N["uv_fall"]) + tuple(fmt(x, 2) for x in N["ov_rise"]) + tuple(fmt(x, 2) for x in N["ov_fall"])))
    p("     overcurrent %s / %s / %s A (the printed row, the 0.1 %% parts, %s %% of their drift, R19's tolerance and drift); short circuit %s / %s / %s A;"
      % (fmt(N["ioc"][0], 3), fmt(N["ioc"][1], 2), fmt(N["ioc"][2], 3), fmt(en["drift"] * 100, 1), fmt(N["isc"][0], 2), fmt(N["isc"][1], 2), fmt(N["isc"][2], 2)))
    p("     the breaker's delay (item 2 of the final round): Equation 7 gives %s / %s / %s ms (CTMR on the GRM3195 family's rows, an ASSUMPTION for this part);"
      % (fmt(N["toc_eq7"][0] * 1e3, 3), fmt(N["toc_eq7"][1] * 1e3, 3), fmt(N["toc_eq7"][2] * 1e3, 3)))
    p("       TI's loaded row prints %s us typical at CTMR 22 nF (and %s / %s us at 0 nF), from the sense crossing to PD at CL 47 nF (SLUSEE5E p.10, MAKER), so"
      % (fmt(N["t48_toc22"] * 1e6, 0), fmt(N["t48_toc0"][0] * 1e6, 0), fmt(N["t48_toc0"][1] * 1e6, 0)))
    p("       the delay is taken as %s ms at least (Equation 7's, the row's excess over it not counted), %s ms typical (the row) and %s ms at most (Equation 7's"
      % (fmt(N["toc"][0] * 1e3, 3), fmt(N["toc"][1] * 1e3, 3), fmt(N["toc"][2] * 1e3, 3)))
    p("       maximum scaled by the row's %s over Equation 7), retry %s s (INFERRED)" % (fmt(N["toc_k"], 3), fmt(N["tretry"], 2)))
    p("     the short-circuit path: the sense reaches the comparator through RISCP x CSCP, a first-order filter of %s / %s / %s us (RISCP 1 %%, CSCP C0G 5 %% on the"
      % (fmt(N["tau"][0] * 1e6, 2), fmt(N["tau"][1] * 1e6, 2), fmt(N["tau"][2] * 1e6, 2)))
    p("       GRM3195 rows, ASSUMPTION), then PD within %s / %s us (tSC at CL 47 nF; Q7's %s nC at 12 V is %s nF, under the test load, so the row covers Q7) (MAKER,"
      % (fmt(N["t48_tsc"][0] * 1e6, 0), fmt(N["t48_tsc"][1] * 1e6, 0), fmt(N["q7_qg"] * 1e9, 0), fmt(N["q7_ceq"] * 1e9, 2)))
    p("       INFERRED); the filter's delay depends on the overdrive: a 14 A step against the highest %s A takes %s us before tSC (the check's example), a ramp"
      % (fmt(N["isc"][2], 4), fmt(N["filt_14"] * 1e6, 2)))
    p("       lags by at most tau, so the threshold is where the trip begins and the peak current is where the trajectory has moved by the delay (INFERRED)")
    p("     INP high from DC_P %s V, under the UVLO's lowest rise; at the clamps' %s V the pins see INP %s V, EN/UVLO %s V, OV %s V, under %s V (INFERRED)"
      % (fmt(N["inp_on_at"], 2), fmt(N["clamp"], 1), fmt(N["pins_at_clamp"][0], 2), fmt(N["pins_at_clamp"][1], 2), fmt(N["pins_at_clamp"][2], 2), fmt(N["t48_pin_abs"], 0)))
    p("     the start: slew %s / %s / %s V/ms (Equation 3, V(BST-SRC) %s to %s V, R1 and C1 tolerances); inrush %s to %s A into %s to %s uF; at most %s ms to %s V;"
      % (fmt(N["slew"][0] / 1e3, 2), fmt(N["slew"][1] / 1e3, 2), fmt(N["slew"][2] / 1e3, 2), fmt(N["t48_cp_on"][0], 0), fmt(N["t48_cp_off"][2], 0),
         fmt(N["inrush"][0], 3), fmt(N["inrush"][2], 3), fmt(N["c_load"][0] * 1e6, 1), fmt(N["c_load"][2] * 1e6, 1), fmt(N["t_start"] * 1e3, 2), fmt(D["vmax"], 2)))
    p("       U34 holds the front end off for %s ms at least, so the start's load is the bias network (section 7); CBST %s uF against Equation 4's %s nF (INFERRED)"
      % (fmt(T9["ctr2_ms"][0], 0), fmt(en["cbst"] * 1e6, 0), fmt(N["cbst_need"] * 1e9, 0)))
    p("     Q7's chart: CSD19536KTT Figure 4-10 from TI's vector drawing (SLPS540C p.6, single pulse, TC 25 C): at %s V 100 us %s A, 1 ms %s A, 10 ms %s A (MAKER);"
      % (fmt(D["vmax"], 2), fmt(N["ktt_at"]["100us"], 1), fmt(N["ktt_at"]["1ms"], 2), fmt(N["ktt_at"]["10ms"], 3)))
    p("       derated by L4-E9's %s (a 150 C part at a %s C case; this part's TJ is %s C, so it is conservative) (RECORD, INFERRED)" % (fmt(T9["derate"], 4), fmt(T9["tc_case"], 1), fmt(N["q7_tj"], 0)))
    p("     A START INTO A RESISTIVE FAULT (Rf 0.1 to 1000 Ohm on VIN_RAW at %s V; the breaker at its slowest: overcurrent %s A for %s ms, the short-circuit"
      % (fmt(D["vmax"], 2), fmt(N["ioc"][2], 2), fmt(N["toc"][2] * 1e3, 3)))
    p("       sense filtered at tau %s us against %s A and then %s us; the current follows its trajectory through every delay; both slew and capacitance"
      % (fmt(N["tau"][2] * 1e6, 2), fmt(N["isc"][2], 2), fmt(N["t48_tsc"][1] * 1e6, 0)))
    p("       corners; every point held against the chart for the whole pulse, conservative, no thermal-impedance superposition) (INFERRED):")
    for fet, (r, rf, dur, how, s, c), start in N["scan"]:
        p("       %-24s worst %s of the derated chart at Rf %s Ohm, %s ms, ended by %s (slew %s V/ms, %s uF); the start itself %s: %s"
          % (fet, fmt(r, 3), fmt(rf, 2), fmt(dur * 1e3, 3), how, fmt(s / 1e3, 2), fmt(c * 1e6, 1), fmt(start, 3), "MEETS" if r < 1.0 and start < 1.0 else "NOT MET"))
    hp, ht, hr = N["hs_start"]
    p("     A START INTO A HARD SHORT: VDS stays at %s V and the current follows the gate at most %s A/us (gfs %s S, TI's typical at 100 A taken as the bound,"
      % (fmt(D["vmax"], 2), fmt(N["a_g"] * 1e-6, 2), fmt(N["gfs"], 0)))
    p("       times the highest slew); the filtered sense reaches %s A and PD follows: a peak of %s A after %s us, %s of the derated 100 us line (MEETS,"
      % (fmt(N["isc"][2], 2), fmt(hp, 1), fmt(ht * 1e6, 2), fmt(hr, 3)))
    p("       CONDITIONAL on the transconductance bound) (INFERRED)")
    p("     A HARD SHORT IN SERVICE (Q7 fully on): the current rises at VIN / L; the filter and PD add at most tau + tSC = %s us, so the peak is at most %s A"
      % (fmt(N["t_d"] * 1e6, 2), fmt(N["isc"][2], 2)))
    p("       plus VIN x %s us / L, and never more than VIN over the loop's resistance. Q7's IDM %s A derated by %s gives %s A; at the entry's highest on-voltage"
      % (fmt(N["t_d"] * 1e6, 2), fmt(N["idm"], 0), fmt(T9["derate"], 4), fmt(N["i_allow"], 1)))
    p("       (the OV rise's %s V) that holds for a loop inductance of %s uH or more from the source to the fault: the threshold is %s to %s A; the PEAK is set"
      % (fmt(N["v_on_max"], 2), fmt(N["l_min"] * 1e6, 2), fmt(N["isc"][0], 2), fmt(N["isc"][2], 2)))
    p("       by the inductance, which no document gives (L4-E9's open item, carried as E11-20 with this bound) (CONDITIONAL)")
    p("   3d. the kit's series resistance from the plug, at the hot end (the low side of the envelope and the in-service maximum):")
    for n, x, cl in N["r_plug_dcp"] + N["r_dcp_vin"]:
        p("     %-104s %s mOhm (%s)" % (n, fmt(x * 1e3, 3), cl))
    p("     the plug to DC_P %s mOhm, DC_P to VIN_RAW %s mOhm, %s mOhm in all (INFERRED); the first round's 20 C copper-only model gives %s mOhm for this"
      % (fmt(N["r1_hot"] * 1e3, 2), fmt(N["r2_hot"] * 1e3, 2), fmt(N["r_hot"] * 1e3, 2), fmt(E["r_plug"]["selected"] * 1e3, 3)))
    p("       construction: it left out the hot values and the contacts")
    p("   3e. the in-service maximum at a 9.00 V plug (the corrected knee's high band, VBUS20 at %s V, the front end at %s, the losses hot) (INFERRED):"
      % (fmt(E["vb_top"], 2), fmt(E["eta_fe"], 2)))
    p("     VIN_RAW %s V, %s A from the plug, DC_P %s V; against the selected entry:" % (fmt(N["vin9"], 3), fmt(N["i9"], 3), fmt(N["dcp9"], 3)))
    p("       UVLO: its highest rise %s V against DC_P at %s V or more before any current flows (MEETS); its highest fall %s V against DC_P %s V in service (MEETS)"
      % (fmt(N["uv_rise"][2], 2), fmt(N["dcp_noload"], 3), fmt(N["uv_fall"][2], 2), fmt(N["dcp9"], 2)))
    p("       overcurrent: %s A at its lowest against %s A, %s %% in hand (INFERRED). The efficiency floor (item 1 of the final round), with the current and"
      % (fmt(N["ioc"][0], 3), fmt(N["i9"], 3), fmt(N["ioc_margin"] * 100, 1)))
    p("         the voltage coupled: Pout / [Itrip x (9 - Itrip x Rloop)] = %s W / [%s A x (9 - %s A x %s mOhm)] = %s; the front end's efficiency at the"
      % (fmt(N["pout9"], 3), fmt(N["ioc"][0], 5), fmt(N["ioc"][0], 5), fmt(N["r_hot"] * 1e3, 3), fmt(N["eta_floor"], 6)))
    p("         operating point must be at least that (L4-E5 takes %s, undocumented: C-8) (CONDITIONAL); the same margin read as U3's board current: %s A over"
      % (fmt(E["eta_fe"], 2), fmt(N["board_excess"], 3)))
    p("         the knee's high band, against the pin's inferred +-%s A (INFERRED)" % fmt(PIN_ERR, 1))
    p("         the fix round's own point (knee %s A, loop %s mOhm, the check's reproduction) gives %s W and a floor of %s, and at that efficiency the equation"
      % (fmt(FIX_KNEE_IT, 2), fmt(FIX_RLOOP * 1e3, 3), fmt(N["fix_pout"], 3), fmt(N["fix_eta"], 6)))
    p("         returns %s A, the trip's lowest: the fix round's 0.906 scaled the current inversely with the efficiency at a fixed voltage and is withdrawn (INFERRED)"
      % fmt(N["fix_i"], 5))
    p("         judged: the static margin rests on three things no held document bounds (the front end's efficiency at 8.1 V, the pin's real band, and the")
    p("         input current's excursions in transients, which the breaker passes only for under %s ms); the component temperatures and losses are bounded"
      % fmt(N["toc"][0] * 1e3, 3))
    p("         (the hot case is the worst). R19 cannot buy more: its least value keeping the breaker's highest under F1's %s A is %s mOhm (no stocked part),"
      % (fmt(F["f_hot_a"], 1), fmt(N["r19_f1"] * 1e3, 3)))
    p("         which would move the lowest trip only to %s A. So the margin was moved on the other side: the knee's flat target %s A (3f) instead of the"
      % (fmt(N["trip_min_r19_f1"], 3), fmt(KNEE_IT, 2)))
    p("         fix round's 1.89 A; what closes it is E11-06's measurement of those three at a 9.00 V plug (SESSION, CONDITIONAL)")
    p("       F1: the breaker's highest %s A against its %s C column %s A (MEETS, MAKER); L2 at %s A: %s K over the %s C air, %s C under its 105 C (MEETS, MAKER)"
      % (fmt(N["ioc"][2], 3), fmt(F["f_col"], 0), fmt(F["f_hot_a"], 1), fmt(N["ioc"][2], 2), fmt(N["l2_rise"], 1), fmt(F["air_hot"], 1), fmt(F["air_hot"] + N["l2_rise"], 1)))
    p("       Q7 at %s A: %s W (INFERRED); the highest in-service current over 9 to 36 V is the 9 V one, %s A (INFERRED)" % (fmt(N["ioc"][2], 2), fmt(N["q7_w"], 3), fmt(N["imax_all"], 3)))
    p("   3f. THE CORRECTED KNEE (SESSION, specification for L4-E5's undrawn network) AND THE RESTART GUARD (draft apply_gen_sch_a_guard.py):")
    p("     flat target %s A of board current (the pin at %s V) from VIN_RAW %s V up to %s V, where L4-E5's line (%s A/V) takes over; below %s V L4-E5's knee slope"
      % (fmt(KNEE_IT, 2), fmt(1 + 0.4 * KNEE_IT, 3), fmt(KNEE_TOP, 2), fmt(N["v_join"], 3), fmt(E["slope"] / 0.4, 6), fmt(KNEE_TOP, 2)))
    p("       (%s V/V at the pin): zero at %s V, HIZ entry %s V, exit %s V; with L4-E5's +-%s %% the knee's top is at most %s V, %s V under the 9 V plug's VIN_RAW,"
      % (fmt(N["knee_slope"], 3), fmt(N["v_zero"], 3), fmt(N["v_hiz_in"], 3), fmt(N["v_hiz_out"], 3), fmt(N["knee_tol"] * 100, 2), fmt(N["top_max"], 3), fmt(N["top_margin"], 3)))
    p("       and HIZ is certain below %s V (SESSION, INFERRED); the warm-up's plan figure (3g) sets the target at %s A or more, and %s A leaves the rest of"
      % (fmt(N["hiz_certain"], 3), fmt(N["it_need"], 4), fmt(KNEE_IT, 2)))
    p("       the window to the breaker (3e) (SESSION)")
    p("     the guard (U34, board A): R14 %sk over R15 %sk as drawn falls at %s / %s / %s V; R14 %sk: falls at %s / %s / %s V and rises at %s / %s / %s V (SNVSBJ1E, INFERRED)"
      % ((fmt(N["guard_r"][0] / 1e3, 0), fmt(N["guard_r"][1] / 1e3, 0)) + tuple(fmt(x, 3) for x in N["guard_drawn"][0]) + (fmt(GUARD_R14_K, 1),)
         + tuple(fmt(x, 3) for x in N["guard_new"][0]) + tuple(fmt(x, 3) for x in N["guard_new"][1])))
    p("       %s V under the knee's certain HIZ (L4-E5's rule: 0.1 V or more; MEETS); at its lowest fall the running levels scale to FE_VZ %s V, FE_RUN %s V"
      % (fmt(N["guard_margin"], 3), fmt(N["guard_levels"][0], 2), fmt(N["guard_levels"][1], 2)))
    p("       (Q36 and Q37 need %s V at most) and EN %s V (VEN(OP) %s V at most): MEETS (INFERRED: the network is resistive under the zener's knee)"
      % (fmt(N["guard_levels"][2], 1), fmt(N["guard_levels"][3], 2), fmt(N["ven_op"], 2)))
    p("   3g. THE FUNCTIONAL WARM-UP AT A 9.00 V PLUG, AS A SHEDDING SEQUENCE (item 3 of the final round): REQ-024's start with the pack cold-soaked (both")
    p("     FETs open, S4), REQ-046's heater before any charge and the charge held while the charger carries the kit (REQ-077), done by the bridge on slot 2.")
    p("     The loads, battery-side, from hc2's pwr_red2.py and rv-pwr's pwr_budget.py run as hc2 runs them (pinned; RECORD, INFERRED); held in P1 (SESSION):")
    for k_, v_ in N["shed_held"]:
        p("       %-24s %s / %s / %s W at the load (RECORD)" % (k_, fmt(v_[0], 3), fmt(v_[1], 3), fmt(v_[2], 3)))
    p("     phase | lo / plan / hi W at VBAT | against 9.00 V at the plug, %s to %s W (3h)" % (fmt(N["env"][9.0]["w_lo"], 2), fmt(N["env"][9.0]["w_hi"], 2)))
    for lab, ld, cl in N["phases"]:
        p("       %-96s %s / %s / %s | %s (INFERRED)" % (lab, fmt(ld[0], 2), fmt(ld[1], 2), fmt(ld[2], 2), " / ".join(cl)))
    p("       P3 charge: the cells over 3 C, the cold hold cleared; the source's surplus over P1 goes to the charge by DPM: %s W at the plan figure, %s at"
      % (fmt(N["surplus"][0], 2), "none" if N["surplus"][1] <= 0 else fmt(N["surplus"][1], 2) + " W"))
    p("         the hi corner, whose P1 exceeds the source's least (INFERRED); the charge then within R-b's bounds (section 2)")
    p("     the mat runs on measured headroom (SESSION): on only while the source's measured headroom over the load is at least the mat's %s W, else it is"
      % fmt(N["heater_w"], 2))
    p("       cycled, so control is kept whenever P1 alone is carried; the warm-up completes on that rule while P1's load is at most %s W (the source's least"
      % fmt(N["shed_room"], 2))
    p("       %s W less the mat) (INFERRED)" % fmt(N["env"][9.0]["w_lo"], 2))
    p("     the result: at the plan figure every phase is carried at every source corner, the warm-up with %s W in hand; at the hi corner P1 (%s W) exceeds the"
      % (fmt(N["func_margin"], 2), fmt(N["shed"][2], 2)))
    p("       source's least, so neither control nor the warm-up is bounded there (NOT BOUNDED by held evidence: E11-06 measures P1)")
    p("     the thermal side: P2 puts %s W of heat inside; with hc2's lid-open conductance (%s to %s W/K, the fans on; P1 holds the mixer fans, so the air runs"
      % (fmt(N["func_heat_in"], 1), fmt(N["g_cold"][0], 1), fmt(N["g_cold"][1], 1)))
    p("       warmer than this) the inside air at -20 C ambient is %s to %s C, so the cells are warmed by the mat alone; the time from the cold soak to 3 C"
      % (fmt(N["air_m20"][0], 1), fmt(N["air_m20"][1], 1)))
    p("       needs the mat-to-cell coupling and the pack's loss to the air, which no held record gives (NOT BOUNDED: E11-23 measures it) (INFERRED)")
    p("     REQ-015 at 9.00 V at the plug: CONDITIONAL CANDIDATE, on E11-06 (P1's load, the front end's efficiency, the pin's band, the transients), E11-09")
    p("       (the knee drawn), E11-23 (the warm-up time), E11-05 (N1, and N2 for S2) and E11-22 (R-b's bounds); not closed (INFERRED)")
    p("   3h. THE SOURCE ENVELOPE AT THE PLUG (the low side with the losses hot and VBUS20 at %s V, the high side with no loss and %s V; U3 %s) (INFERRED):"
      % (fmt(E["vb_low"], 3), fmt(E["vb_top"], 2), fmt(E["eta_u3"], 4)))
    p("   plug | VIN_RAW at the low side | U3 board current, A | at VBAT, W | L4-E9 at VIN_RAW (no loss) (INFERRED)")
    for v in (9.0, 12.0, 24.0, 36.0):
        e = N["env"][v]
        l9 = {9.0: "%s to %s W" % (fmt(E["l9"]["min9"], 1), fmt(E["l9"]["max9"], 1)), 12.0: "up to %s W" % fmt(E["l9"]["max12"], 1), 24.0: "up to %s W" % fmt(E["l9"]["max24"], 1), 36.0: "(the window)"}[v]
        p("     %5s V | %s V | %s to %s | %s to %s | %s" % (fmt(v, 1), fmt(e["vin_lo"], 3), fmt(e["board_lo"], 3), fmt(e["board_hi"], 3), fmt(e["w_lo"], 2), fmt(e["w_hi"], 2), l9))
    p("   the states at their plan figure against it:")
    for name, (lo, plan, hi) in list(E["states"].items()) + [("the warm-up (P2)", N["func"])]:
        key = name if name != "the warm-up (P2)" else "the functional warm-up (one module and the heater)"
        cl = " | ".join("%s V: %s" % (fmt(v, 0), N["cls"][(key, v)]) for v in (9.0, 12.0, 24.0, 36.0))
        p("     %-32s %s W | %s (RECORD, INFERRED)" % (name, fmt(plan, 2), cl))
    p("   a dead pack's charge on top: at most %s A x %s V = %s W under R-b in case (i) (section 2; %s W at its %s V threshold), taken only from what DPM"
      % (fmt(N["rb_max"], 3), fmt(R["cv_max"], 3), fmt(N["dead_charge_w_max"], 2), fmt(N["dead_charge_w"], 2), fmt(RULE_SRN_V, 1)))
    p("     leaves after the system (9.3.17): it never pushes the kit out of the envelope (INFERRED; the first round's 4.22 W took the typical 384 mA as a bound)")
    p("   3i. the first round's finding U4-F3 as found (the DRAWN knee at the plug, the 20 C model): a 9.00 V plug settles VIN_RAW at %s V and gives %s W (selected"
      % (fmt(E["plug"]["selected"]["vin"], 3), fmt(E["plug"]["selected"]["w"], 1)))
    p("     interconnect) or %s V and %s W (drawn), against %s W at VIN_RAW 9 V: the drawn knee caps the plug's 9 V; 3f replaces it (INFERRED)"
      % (fmt(E["plug"]["drawn"]["vin"], 3), fmt(E["plug"]["drawn"]["w"], 1), fmt(E["line9_nom_w"], 1)))
    p("")
    p("4. U-04, THE COMPARISON'S OWN FIGURES")
    p("   (B) a battery FET in the pack path carries the pack's peak: %s W per mOhm at %s A, %s mW per mOhm at PS-IDLE-SPEC's %s A (INFERRED)"
      % (fmt(C["batfet_w_per_mohm_18a"], 3), fmt(C["pack_peak"]), fmt(C["batfet_w_per_mohm_idle"] * 1000, 1), fmt(C["idle_a"], 2)))
    p("     the one NVDC charger held, TI's BQ25798, states NVDC regulation (p.%d) but its integrated battery FET carries %s A RMS and %s A for 1 s (p.%d),"
      % (C["nvdc_p"], fmt(C["bq98_rms"]), fmt(C["bq98_pk"]), C["bq98_p"]))
    p("     under the pack's %s A peak (the declared VBAT peak, NETLIST): (B) needs an external-FET part whose sheet is not held (MAKER, INFERRED)" % fmt(C["pack_peak"]))
    p("   (C) a pre-charge resistor on board P from VSYS at %s V into a pack at the Shutdown Voltage (%s V): for the cell maker's 0.1 C (%s A for 3P)"
      % (fmt(B["cv4s"], 1), fmt(P["vsys_shut"][0], 1), fmt(C["pre_i_01c"], 2)))
    p("     %s ohm and %s W, %s W at CUV; for the charger's own %s mA, %s ohm and %s W (INFERRED)"
      % (fmt(C["pre_r_01c"], 2), fmt(C["pre_w_01c"], 2), fmt(C["pre_w_cuv_01c"], 2), fmt(B["iclamp"] * 1000), fmt(C["pre_r_clamp"], 1), fmt(C["pre_w_clamp"], 2)))
    p("")
    p("5. U-04, IS AN OWNER QUESTION FORCED?")
    p("   a mandatory requirement naming a load state for source-only operation: %s (section 1); the warm-up sequence of 3g is carried at its plan figure" % ("yes" if F["owner_question"] else "none"))
    p("   what the source path itself admits at a 9.00 V plug, the kit's losses included and VBUS20's other loads taken off (INFERRED; the first round's")
    p("     %s / %s / %s W left the losses out):" % (fmt(F["cap9_hot_w"], 1), fmt(F["cap9_cold_w"], 1), fmt(F["cap9_15a_hot_w"], 1)))
    for lab, ia, rr, vr, w in N["caps"]:
        p("     %-46s %s mOhm: VIN_RAW %s V, %s W at VBAT (MAKER, INFERRED)" % (lab, fmt(rr * 1e3, 2), fmt(vr, 3), fmt(w, 2)))
    p("     (the check's reference, 115.511 mOhm with no auxiliary load: " + ", ".join("%s A %s W" % (fmt(ia, 1), fmt(w, 2)) for ia, w in N["check_ref"]) + ")")
    p("   these are the path's ceilings with the electronics set to use all of them; the breaker's band and the knee's spread keep the least delivered")
    p("     figure lower (3h: %s W at 9 V) (INFERRED). REQ-015 states no source current capability: every figure takes the source as holding its voltage (named)" % fmt(N["env"][9.0]["w_lo"], 2))
    typ, cwu = E["states"]["PS-TYP"][1], E["states"]["the cold warm-up (CONOPS 4c)"][1]
    (_l0, _i0, _r0, _v0, c_hot), (_l1, _i1, _r1, _v1, c_cold), (_l2, _i2, _r2, _v2, c_15) = N["caps"]
    cmp_ = lambda x, c: "over" if x > c else "under"
    p("   so NO owner question is forced: no approved requirement names a load REQ-015's 9 V must carry beyond the functional sequence, which 3c to 3g carry at")
    p("     its plan figure (CONDITIONAL, 3g). Against the ceilings: PS-TYP %s W is %s F1's hot ceiling %s W and %s its cold %s W; the CONOPS cold warm-up"
      % (fmt(typ, 2), cmp_(typ, c_hot), fmt(c_hot, 2), cmp_(typ, c_cold), fmt(c_cold, 2)))
    p("     %s W (a cold state, so F1's cold column applies) is %s its cold ceiling %s W; a 15 A part's hot ceiling %s W is %s both. So the kit at 9 V with F1 as"
      % (fmt(cwu, 2), cmp_(cwu, c_cold), fmt(c_cold, 2), fmt(c_15, 2), "over" if c_15 >= max(typ, cwu) else "not over"))
    p("     fitted does not carry PS-TYP hot or the CONOPS warm-up cold: a design envelope stated, not a conflict with an approved requirement (INFERRED)")
    p("")
    p("6. D-06, F1'S WEAK-SOURCE BAND AND THE INTERCONNECT")
    p("   0997010.WXN time-current (MAKER, held sheet p.3): " + "; ".join("%s %%: %s to %s s" % (fmt(pct * 100, 0), fmt(tmin, 2), "-" if tmax is None else fmt(tmax, 2)) for pct, tmin, tmax in D["tc"]))
    p("   the envelope a source can leave, read monotone (a larger current clears no later than a smaller one; INFERRED), with each interval's top I2t:")
    for lo, hi, tt, i2t in N["i2t_top"]:
        if tt is None:
            p("     up to %s A: no maximum time printed: carried with no time limit" % fmt(hi, 1))
        elif hi == N["i_pf_spec"]:
            p("     from %s A up to the specified worst stiff-source current %s A (the loop's floor, below): at most %s s by the 600 %% row, which bounds the energy"
              % (fmt(lo, 1), fmt(hi, 1), fmt(tt, 2)))
            p("       only by %s A2s; F1's total clearing I2t at 58 V DC is not printed (the sheet's %s A2s is a typical melting figure from its breaking tests),"
              % (fmt(i2t, 0), fmt(N["f1_melt"], 0)))
            p("       so above %s A the elements are judged" % fmt(lo, 0))
            p("       against F1's total clearing I2t at %s A once filed (R-115, E11-16) (MAKER, INFERRED)" % fmt(hi, 0))
        else:
            p("     from %s A up to %s A: up to %s s, %s A2s at the interval's top" % (fmt(lo, 1), fmt(hi, 1), fmt(tt, 2), fmt(i2t, 0)))
    p("   the elements in that fault loop, as drawn:")
    for n, r, src, cls in D["drawn"]:
        p("     %-58s %s (%s; %s)" % (n, ("%s A" % fmt(r, 1)) if r is not None else "no rating", src, cls))
    p("   as drawn: NOT MET (every element needs at least %s A with no time limit; one is %s A, four state none) (INFERRED)" % (fmt(D["cont_need"], 1), fmt(D["c16"], 0)))
    p("   option (ii), a smaller fuse, with the tolerances shown: the 7.5 A MINI's %s C column is %s A; an LM5069 limit whose maximum is that has its minimum at"
      % (fmt(F["f_col"], 0), fmt(N["f75_hot"], 1)))
    p("     %s A (VCL %s over %s mV, R19 at +-1 %%), the selected breaker's at %s A: both under the in-service %s A at 9 V (and L4-E5's 4.629 A): rejected (INFERRED)"
      % (fmt(N["f75_lm"], 3), fmt(T9["vcl"][0] * 1e3, 1), fmt(T9["vcl"][2] * 1e3, 1), fmt(N["f75_tps"], 3), fmt(N["i9"], 3)))
    p("   SELECTED (SESSION): every element of the interconnect rated at least %s A continuous where installed, which covers the envelope to 20 A for"
      % fmt(CONT_CLASS_A, 0))
    p("     any time; above it, the short-time obligations below:")
    for n, cl, r, src in D["selected"]:
        p("     %-46s %s%s (%s) (SESSION)" % (n, cl, (" : %s A" % fmt(r, 0)) if r is not None else "", src))
    p("     D38999 contact table p.%d (MAKER); shell 13's Series III arrangements 13-4, 13-8, 13-26, 13-32, 13-35 (p.%d), shell 17's 17-2, 17-6, 17-8 (p.%d) (MAKER)"
      % (D["d38999_p"], D["ins13_p"], D["ins17_p"]))
    p("   the interval tops against a %s mm2 core, adiabatic (INFERRED: copper's resistivity and volumetric heat):" % fmt(SEL_MM2, 3))
    for lo, hi, tt, dt in N["adiab"]:
        p("     %s A for %s s: %s K%s (INFERRED)" % (fmt(hi, 1), fmt(tt, 2), fmt(dt, 2), "; the monotone bound only, F1's clearing I2t decides it" if hi == N["i_pf_spec"] else ""))
    p("   and against the size 12 contact's %s A, which Amphenol prints as a crimp-contact test current (p.%d), not an installed rating: the same I2t as %s"
      % (fmt(D["c12"], 0), D["d38999_p"], "; ".join("%s A for %s s = %s s at %s A" % (fmt(hi, 0), fmt(tt, 2), fmt(e, 3), fmt(D["c12"], 0)) for lo, hi, tt, e in N["contact_eq"][1:])))
    p("     (INFERRED; the contact's installed continuous rating and its short-time limit are not printed: E11-10 and E11-16)")
    p("   THE WITHSTAND OBLIGATIONS of every element the fault current passes (the receptacle and plug contacts, the NATO plug, the cable's and the inside lead's")
    p("     cores, J_DCIN, F1's holder, board E's copper to F1): each carries %s A continuous (which covers the envelope to %s A), %s A for %s s and"
      % (fmt(CONT_CLASS_A, 0), fmt(N["intervals"][1][1], 0), fmt(N["intervals"][2][1], 0), fmt(N["intervals"][2][2], 0)))
    p("     %s A for %s s, and from %s A to %s A has a short-time capability of at least F1's total clearing I2t at %s A and 58 V DC, which is not printed; until it is filed the only"
      % (fmt(N["intervals"][3][1], 0), fmt(N["intervals"][3][2], 1), fmt(N["intervals"][4][0], 0), fmt(N["i_pf_spec"], 0), fmt(N["i_pf_spec"], 0)))
    p("     bound is the 600 %% row's %s A2s, which no element's held data is shown to withstand (E11-16 files both sides) (MAKER, INFERRED)" % fmt(N["i2t_top"][4][3], 0))
    p("   THE INTERCONNECT BY ITS RESISTANCE (SESSION; final round): a larger or purer conductor raises a stiff fault, so the check rests on a measured floor,")
    p("     not on copper constants, and the floor is set so the worst case stays %s A, %s %% under F1's %s A, on L4-E9's %s V basis (kept: it is over"
      % (fmt(N["i_pf_spec"], 0), fmt((1 - N["i_pf_spec"] / D["interrupt_a"]) * 100, 0), fmt(D["interrupt_a"], 0), fmt(D["vmax"], 2)))
    p("     REQ-015's 40 V over-voltage test and the new entry's OV maximum %s V, which would give %s A on the same floor):"
      % (fmt(N["ov_rise"][2], 2), fmt(N["ov_rise"][2] / N["loop_floor_cold"], 1)))
    p("     the loop from the NATO plug's pins to J_DCIN's board pins (the cable, the D38999 pair, the inside lead, J_DCIN), its actual resistance at 20 C")
    p("       at least %s mOhm (%s mOhm at %s C) and at most %s mOhm (the 9 V envelope's basis, 3d) (SESSION, INFERRED)"
      % (fmt(N["loop_floor20"] * 1e3, 2), fmt(N["loop_floor_cold"] * 1e3, 2), fmt(T_COLD, 0), fmt(N["loop_ceil20"] * 1e3, 1)))
    p("     the acceptance, four-wire on every assembly and every replacement, with the instrument and fixture within %s %% of reading and the conductor's"
      % fmt(U_MEAS * 100, 0))
    p("       temperature known within %s K (%s %% with copper's coefficient), the reading corrected to 20 C: %s to %s mOhm (SESSION, INFERRED)"
      % (fmt(DT_MEAS, 0), fmt(N["u_meas"] * 100, 2), fmt(N["acc"][0] * 1e3, 2), fmt(N["acc"][1] * 1e3, 2)))
    p("     the selected construction: %s m of AWG 14 with the 0.5 m lead, copper %s mOhm at 20 C, with the D38999 pair and J_DCIN at most %s mOhm more:"
      % (fmt(SEL_CABLE_M, 2), fmt(N["cu_nom20"] * 1e3, 2), fmt(N["contacts_max"] * 1e3, 2)))
    p("       %s to %s mOhm, inside the window; copper alone reaches the floor from %s m (INFERRED); a reading outside the window is corrected by length"
      % (fmt(N["constr"][0] * 1e3, 2), fmt(N["constr"][1] * 1e3, 2), fmt(N["min_len_floor"], 2)))
    p("   THE STIFF SOURCE AGAIN (copper alone at %s C, the source's own resistance zero, A-12; at the OVLO maximum %s V):" % (fmt(T_COLD, 0), fmt(D["vmax"], 2)))
    for lab, rr, ipf in D["stiff"]:
        p("     %-48s %s ohm, %s A against %s A: %s (INFERRED)" % (lab, fmt(rr, 5), fmt(ipf, 1), fmt(D["interrupt_a"], 0), "MEETS" if ipf <= D["interrupt_a"] else "NOT MET"))
    p("   so a heavier interconnect needs a resistance floor: F1's 1000 A alone would need %s ohm at %s C (AWG 14 from %s m); the specified floor above"
      % (fmt(D["r_floor"], 5), fmt(T_COLD, 0), fmt(D["min_len_14"], 2)))
    p("     keeps %s A with the margin and the measurement's uncertainty; the selected construction's own figure is %s A; a shorter or heavier lead needs"
      % (fmt(N["i_pf_spec"], 0), fmt(N["sel_ipf_cold"], 1)))
    p("     a fuse with a larger interrupting rating at 58 V DC, of which no sheet is held (named) (INFERRED)")
    p("   F1's other checks with it: the selected breaker's highest %s A (the drawn LM5069's 6.15 A) against its %s C column %s A (MEETS, MAKER);"
      % (fmt(N["ioc"][2], 3), fmt(F["f_col"], 0), fmt(F["f_hot_a"], 1)))
    p("     the lowest stiff fault at 9 V with the copper at %s C, %s A, %s times the rating, inside the 600 %% row's 0.1 s (MEETS, INFERRED);"
      % (fmt(F["air_hot"], 1), fmt(D["min_fault_9v"], 1), fmt(D["min_fault_9v_x"], 2)))
    p("     the start's I2t: the LM5069's longest at its timer's maximum in section 7, the selected entry's inrush %s A for %s ms (MEETS, INFERRED)"
      % (fmt(N["inrush"][2], 2), fmt(N["t_start"] * 1e3, 2)))
    p("")
    p("7. D-09, THE HOT SWAP'S FAULT TIME AGAINST ITS START")
    p("   LM5069 (SNVS452G): VTMRH %s / %s / %s V, ITIMER %s / %s / %s uA, VCL %s / %s / %s mV; Equation 9 (1.30e5, 1.18 mV); TI's half-again margin (9.2.1.2.4, p.%d) (MAKER)"
      % (tuple(fmt(x, 2) for x in T9["vtmrh"]) + tuple(fmt(x * 1e6, 0) for x in T9["itimer"]) + tuple(fmt(x * 1e3, 1) for x in T9["vcl"]) + (T9["eq12_p"],)))
    p("   the power limit with R24 22k (L4-E9's draft) and R19 10 mOhm %s %%: %s W at %s V, falling with VDS (Equation 9) (MAKER, NETLIST; L4-E9 reads %s W)"
      % (fmt(T9["rs_tol"] * 100, 0), fmt(T9["plim_nom"], 3), fmt(D["vmax"], 2), fmt(T9["plim_nom_l9"], 2)))
    p("   what the start charges (NETLIST): " + ", ".join("%s %s %s uF on %s" % (b, ref, fmt(c, 1), net) for b, ref, net, c in T9["caps"]) + " = %s uF nominal" % fmt(T9["c_uf"], 1))
    p("     (L4-E9 counted 31 uF: C6 on DC_HS, and C207 and C210 behind D19 and R196, are added); the X7R rows stacked as L4-E9: K %s %%, %s %%, %s %% (Yageo V.26, MAKER; an ASSUMPTION for parts of other makers)"
      % (fmt(T9["x7r"][0] * 100, 0), fmt(T9["x7r"][1] * 100, 0), fmt(T9["x7r"][2] * 100, 0)))
    p("   the resistive load on VIN_RAW during the start, each path bounded by its resistor alone: " + ", ".join("%s %s %s k" % (b, r, fmt(x / 1e3, 1)) for b, r, x in T9["loads"])
      + ", %s mA at %s V, and U2's shutdown %s uA (MAKER LM5176 IQ) (NETLIST, INFERRED)" % (fmt(T9["g_load"] * D["vmax"] * 1e3, 1), fmt(D["vmax"], 2), fmt(T9["u2_sd"] * 1e6, 0)))
    p("   THE FRONT END'S OWN LOAD: U2 is held off by U34 until its release, %s / %s / %s ms after VIN_RAW passes the UV rise (gen_sch_a.py's"
      % tuple(fmt(x, 0) for x in T9["ctr2_ms"]))
    p("     derivation from SNVSBJ1E), %s times the start's maximum: the soft start never overlaps the hot swap's start, so its load during the"
      % fmt(T9["ctr2_over_start"], 1))
    p("     start is the bias network above (INFERRED, NETLIST)")
    p("   the start (TI's Equation 12 with the power limit following VDS, integrated; the load included) (INFERRED):")
    p("     nominal: %s ms (Equation 12 with the limit held at its %s V value: %s ms; L4-E9 %s ms on 31 uF) (INFERRED)"
      % (fmt(T9["start_nom"] * 1e3, 3), fmt(D["vmax"], 2), fmt(T9["eq12_nom"] * 1e3, 3), fmt(T9["start_l9"][0] * 1e3, 3)))
    p("     corners: the capacitors at the stacked top, R24 -1 %%, R19 +%s %%, the limit over TI's 1.3, VCL's minimum: %s ms (%s ms without the load; L4-E9 %s ms) (INFERRED)"
      % (fmt(T9["rs_tol"] * 100, 0), fmt(T9["start_max"] * 1e3, 3), fmt(T9["start_max_noload"] * 1e3, 3), fmt(T9["start_l9"][1] * 1e3, 3)))
    p("     TI's margin: the fault time's minimum at least %s ms (1.5 x the corner start) (INFERRED)" % fmt(T9["need"] * 1e3, 3))
    p("   C5 as drawn (100 nF K X7R, L4-E9's stack from the timer rows): %s to %s ms (L4-E9 2.035 to 11.871 ms from L4-E5's rounded times): NOT MET against %s ms (INFERRED)" % (fmt(T9["c5_l9"][0] * 1e3, 3), fmt(T9["c5_l9"][1] * 1e3, 3), fmt(T9["need"] * 1e3, 3)))
    p("   Q7's Figure 10 at %s V from TI's vector drawing: 10 ms %s A, 1 ms %s A, DC %s A at TC 25 C; m %s; derated to Q7's %s C case by %s (L4-E9) (MAKER, RECORD)"
      % (fmt(D["vmax"], 2), fmt(T9["i10"], 3), fmt(T9["i1"], 3), fmt(T9["idc"], 4), fmt(T9["m"], 4), fmt(T9["tc_case"], 1), fmt(T9["derate"], 4)))
    p("     the pulse %s A (the limit at its corners times TI's 1.3, L4-E9) fits the power law carried past 10 ms up to %s ms (CONDITIONAL on the law past 10 ms)"
      % (fmt(T9["pulse_a"], 3), fmt(T9["t_soa_max"] * 1e3, 2)))
    p("   no single C0G part of 150 nF is stocked: %d surface-mount 150 nF C0G or NP0 rows read, %d with stock (CATALOGUE, inputs/jlc-search-c0g-150nf)" % T9["search150"])
    p("   the stocked GRM3195 C0G parts read (Murata reference sheets, Jun.11,2026): " + "; ".join(
        "%s %s nF +-%s %%, %s V, 0+-%s ppm/K, Table A +%s/-%s %% at -55 C, endurance +-%s %%, damp heat +-%s %% (p.%d)"
        % (pn, fmt(v["c"] * 1e9, 0), fmt(v["tol"] * 100, 0), fmt(v["v"], 0), fmt(v["ppm"] * 1e6, 0), fmt(v["ta_up"] * 100, 2), fmt(v["ta_dn"] * 100, 2), fmt(v["endur"] * 100, 0), fmt(v["damp"] * 100, 1), v["page"])
        for pn, v in T9["mur"].items()) + " (MAKER)")
    p("   candidate | C nF | stacked C nF (tolerance, temperature, endurance) | fault time ms | start | Figure 10 at its maximum (CONDITIONAL)")
    for r in T9["cands"]:
        p("     %-42s | %s | %s to %s | %s to %s | %s | %s A against %s A: %s (INFERRED)"
          % (r["lab"], fmt(r["c"] * 1e9, 0), fmt(r["lo"] * 1e9, 2), fmt(r["hi"] * 1e9, 2), fmt(r["tmin"] * 1e3, 3), fmt(r["tmax"] * 1e3, 3),
             "MEETS" if r["start_ok"] else "NOT MET", fmt(r["soa"], 4), fmt(T9["pulse_a"], 3), "MEETS" if r["soa_ok"] else "NOT MET"))
    S = T9["sel"]
    p("   SELECTED (SESSION): C5 %s (LCSC %s) with C121 %s (LCSC %s), both 1206 C0G 50 V, on HS_TIMER: %s nF; fault time %s ms nominal, %s to %s ms stacked"
      % (S["parts"][0], T9["sel_codes"][0], S["parts"][1], T9["sel_codes"][1], fmt(S["c"] * 1e9, 0), fmt(T9["sel_nom_ms"] * 1e3, 3), fmt(S["tmin"] * 1e3, 3), fmt(S["tmax"] * 1e3, 3)))
    p("     start: %s ms against %s ms, %s ms in hand, so the margin holds while the start stays under %s ms (MEETS, INFERRED); Figure 10: %s A against %s A at %s ms, %s %% past the 10 ms line (MEETS, CONDITIONAL)"
      % (fmt(S["tmin"] * 1e3, 3), fmt(T9["need"] * 1e3, 3), fmt((S["tmin"] - T9["need"]) * 1e3, 3), fmt(S["tmin"] / 1.5 * 1e3, 3), fmt(S["soa"], 4), fmt(T9["pulse_a"], 3), fmt(S["tmax"] * 1e3, 3), fmt(T9["sel_extrap"] * 100, 1)))
    p("     sensitivities: a steeper law past 10 ms (m 0.5) gives %s A (MEETS); the damp-heat row stacked instead of endurance: %s to %s ms, %s A (MEETS) (INFERRED);"
      % (fmt(T9["sel_soa_m05"], 4), fmt(T9["damp"][0] * 1e3, 3), fmt(T9["damp"][1] * 1e3, 3), fmt(T9["damp_soa"], 4)))
    p("     TI's own basis (typical values, 1.5 x the typical start): %s ms against %s ms (MEETS, INFERRED); the DC line derated, %s A, is under the pulse:"
      % (fmt(T9["typ_basis"][0] * 1e3, 3), fmt(T9["typ_basis"][1] * 1e3, 3), fmt(T9["dc_hot"], 4)))
    p("     the pulse is bounded by the fault time, not by a steady rating (INFERRED); F1 during the longest start: %s A2s against %s A2s (MEETS)"
      % (fmt(T9["f1_i2t_start"], 3), fmt(E["f1_i2t"], 0)))
    p("   D-09 stands for the LM5069 as drawn: the selected entry of 3c removes the LM5069 and its timer, so apply_gen_sch_e_timer.py is the alternative to")
    p("     apply_gen_sch_e_entry.py while the LM5069 stays, and the two drafts refuse each other (SESSION)")
    p("")
    p("8. THE DOWNSTREAM ITEMS (each with one owner and an acceptance; L4E11-SOURCE-ONLY-AND-ENTRY.md section 8 is the same table)")
    for it in downstream(R):
        p("   %s | %s | %s | %s" % (it[0], it[1], it[2], it[3]))
    p("")
    render_dependency(R, p)
    render_consolidation(R, p)
    render_fix(R, p)
    render_fix16(R, p)
    render_fix17(R, p)
    render_fix18(R, p)
    render_fix19(R, p)
    render_fix20(R, p)
    render_fix21(R, p)
    render_fix22(R, p)
    render_fix23(R, p)
    render_fix24(R, p)
    render_fix25(R, p)
    render_fix26(R, p)
    render_fix27(R, p)
    render_fix28(R, p)
    p("END. Desk arithmetic; nothing is measured. Drafts: apply_gen_sch_e_entry.py (the entry, 3c; J_DCIN's XT60-F, 19), apply_gen_sch_a_guard.py")
    p("(R14, 3f), apply_gen_sch_e_timer.py (C5 and C121, the alternative while the LM5069 stays), apply_gen_sch_a_charger.py (the BQ25730, its three")
    p("battery FETs, the dock's VSYS contact and the VSYS hold U46, 14, 15 and 19), apply_gen_sch_a_dd7.py (DD-7 on board A, 19h and 20; its netlist")
    p("check check_dd7_netlist.py), apply_gen_sch_e_aux.py and apply_pcb_interfaces_dock.py (board E's VSYS feed, 15a); the")
    p("first round's apply_gen_sch_e_uvlo.py is withdrawn; the knee is a specification (3f); the interface and firmware texts are drafts for Layer 5")
    p("in the record. Software tests establish this record's own behaviour only.")
    return "\n".join(out) + "\n"




def downstream(R):
    E, D, T9, N = R["E"], R["D"], R["T9"], R["N"]
    return [
    ("E11-01", "IMPLEMENTATION", "Layer 8 board E generator owner", "apply_gen_sch_e_entry.py applied after L4-E9's apply_gen_sch_e_hotswap.py, instead of apply_gen_sch_e_timer.py: U6 TPS48110AQDGXRQ1, Q7 CSD19536KTT, R19 4.5 mOhm, L2 SRF1260-1R0Y and the network of section 3c; the DGX-19 land added to meshsat.pretty from TI's DGX0019A drawing and the D2PAK land checked against TI's KTT drawing; _VEH_T restated to the breaker's %s A; the regenerated netlist reads every value of 3c" % fmt(N["ioc"][2], 2)),
    ("E11-02", "IMPLEMENTATION", "Layer 8 board A generator owner", "apply_gen_sch_a_guard.py applied together with the corrected knee (E11-09): R14 %sk (C23107); U34's fall recomputed from the fitted parts reads %s to %s V" % (fmt(GUARD_R14_K, 1), fmt(N["guard_new"][0][0], 2), fmt(N["guard_new"][0][2], 2))),
    ("E11-03", "INTERFACE", "Layer 5 interfaces", "FW-C08, FW-A14 and PANEL.md section 10 restated as the record's section 7a (rule R-a's state table: every charge hold by the CHRG_INHIBIT bit or ChargeCurrent 0, never by the CHG_INHIBIT line or SHORE_INHIBIT, and neither line asserted while the pack cannot discharge); DCIN_PGD restated as the entry's fault flag (FLT_I and FLT_T, low on a fault); REQ-046's hold still clears above 3 C"),
    ("E11-04", "FIRMWARE", "firmware owner", "rules R-a to R-d implemented (section 7a): R-a's state table with its S4 exception and the hold's persistence across states; R-b's two settings (ChargeCurrent() 0x0000 or 0x0200, no other) while U3's SRN reading is under %s V or the gauge reports XDSG or PRECHARGE; R-c's shed to the envelope at the measured input and the VSYS_UVP recovery; R-d; checked on the bench (E11-06)" % fmt(RULE_SRN_V, 1)),
    ("E11-05", "EVIDENCE", "Layer 6 components", "TI's answers filed: Q-TI-3 restated as N2 for state S2 (VSYS's regulation with CHRG_INHIBIT = 1 while the pack can take charge but cannot discharge, under a 5 A load step) and N1, and Q-TI-2; U-04's N1 to N3 re-judged on them; not needed once E11-27 is applied (SLUSE65A prints the bounds, section 12)"),
    ("E11-06", "TEST", "prototype bench", "R-85 extended: at 9.00 V at the plug with the interconnect at its resistance ceiling, and at 12 and 24 V: the shedding sequence of section 3g (P0 to P3) with the pack cold-soaked (S4), at a warm CUV (S2, the charge held by the bit: VSYS stays up) and absent; P1's load measured at most %s W at VBAT; the front end's efficiency at the operating point at least %s; U3's board current at the knee's flat target inside its band; the entry's current over the kit's load steps and source changes above the breaker's lowest %s A for less than %s ms and its filtered short-circuit sense under %s A; VSYS's step response; Q2's case at R-b's current; the latch recovery by a re-plug" % (fmt(N["shed_room"], 2), fmt(N["eta_floor"], 4), fmt(N["ioc"][0], 2), fmt(N["toc"][0] * 1e3, 3), fmt(N["isc"][0], 2))),
    ("E11-07", "ANALYSIS", "Layer 9 pre-layout analysis", "VSYS's effective capacitance at 16.884 V from the makers' DC-bias curves at least 50 uF (SLUSE66A 10.1), or the direct EEHZK1V181P of E11-24, which gives it by design (TI prefers POSCAP)"),
    ("E11-08", "EVIDENCE", "Layer 9 pre-layout analysis", "every load converter's and the controllers' minimum input read from their sheets against 10.0 V (A-14, R-49) and against 8.0 V for a pack at its Shutdown Voltage"),
    ("E11-09", "ANALYSIS", "Layer 4 coordinator", "L4-E5's undrawn H3 network drawn to section 3f's specification (flat %s A from VIN_RAW %s V to %s V, the knee slope kept, zero %s V, HIZ certain below %s V) with E11-02's guard; L4-E5's low-light settle, the solar line and its V-A09 sweep re-run on it" % (fmt(KNEE_IT, 2), fmt(KNEE_TOP, 2), fmt(N["v_join"], 3), fmt(N["v_zero"], 3), fmt(N["hiz_certain"], 3))),
    ("E11-10", "IMPLEMENTATION", "Layer 7 mechanical", "the DC receptacle and plug on MIL-DTL-38999 size 12 contacts (shell 17, insert 17-6: DC and solar pairs on four contacts, two unassigned between power and return; or 13-26 with the solar pair on rated contacts elsewhere), with the insert's installed continuous rating of at least 20 A at the case's air from the maker's derating, or a measured rise at 20 A, filed; the plate cut-out checked against CASE-MARGINS 3.3"),
    ("E11-11", "IMPLEMENTATION", "Layer 7 mechanical", "the DC interconnect specified by its loop, from the NATO plug's pins to J_DCIN's board pins: its reading, four-wire with the instrument and fixture within %s %% of reading and the conductor's temperature known within %s K, corrected to 20 C, between %s and %s mOhm on every assembly and every replacement (the actual floor %s mOhm keeps a stiff source under %s A); cores and the NATO plug with a maker's rating of at least 20 A; the sheets filed" % (fmt(U_MEAS * 100, 0), fmt(DT_MEAS, 0), fmt(N["acc"][0] * 1e3, 2), fmt(N["acc"][1] * 1e3, 2), fmt(N["loop_floor20"] * 1e3, 2), fmt(N["i_pf_spec"], 0))),
    ("E11-12", "IMPLEMENTATION", "Layer 7 mechanical", "the inside lead (a maker's rating of at least 20 A) ending in an Amass XT60-M on J_DCIN, which apply_gen_sch_e_entry.py now draws as the Amass XT60-F (C98734; round 9, section 19e; the gender opposite J_BATT's XT60-M, so the pack lead cannot mate it); the lead's polarity matched to J_DCIN's pad 1 (+) as read on KiCad's AMASS land at board E's regeneration"),
    ("E11-13", "IMPLEMENTATION", "Layer 8 board E generator owner", "F1's holder: a MINI 297/997 holder whose maker prints a current rating of at least 20 A (the 3568 prints none); its sheet filed"),
    ("E11-14", "LAYOUT", "Layer 9 pre-layout analysis", "board E's copper from J_DCIN through F1 to D10, C4 and Q1 sized for 20 A continuous at the rise this project judges at, and Q7's D2PAK land with its copper"),
    ("E11-15", "IMPLEMENTATION", "Layer 8 board E generator owner", "pcb_energy_chain.yaml SHORE_INPUT restated with L4-E9's R-95: conductor %s A, the breaker's %s A, protects the interconnect, the prospective high %s A (the specified floor's worst case); the energy chain gate reads it" % (fmt(CONT_CLASS_A, 0), fmt(N["ioc"][2], 2), fmt(N["i_pf_spec"], 0))),
    ("E11-16", "EVIDENCE", "Layer 6 components", "F1's total clearing I2t at %s A and 58 V DC from Littelfuse (R-115), and against it, and against the monotone envelope (35 A for 5 s, 60 A for 0.5 s), the short-time withstand of every element the fault passes: the size 12 contacts, the NATO plug, the cable's and the inside lead's cores, J_DCIN, F1's holder and board E's copper to F1; filed" % fmt(N["i_pf_spec"], 0)),
    ("E11-17", "TEST", "prototype bench", "R-118 for the selected entry at 43 V, the TRIP THRESHOLDS apart from the PEAK CURRENTS: the start inside %s ms with at most %s A; the breaker's thresholds on a slow ramp (overcurrent %s to %s A after %s to %s ms, short circuit %s to %s A on the filtered sense); the peaks recorded and held under the chart: a start into a resistive fault near %s Ohm, a start into a hard short (at most %s A), Q7 unharmed; with the LM5069 kept, D-09's rows (the fault time inside %s to %s ms, the start inside %s ms)" % (fmt(N["t_start"] * 1e3, 2), fmt(N["inrush"][2], 2), fmt(N["ioc"][0], 2), fmt(N["ioc"][2], 2), fmt(N["toc"][0] * 1e3, 3), fmt(N["toc"][2] * 1e3, 3), fmt(N["isc"][0], 2), fmt(N["isc"][2], 2), fmt(N["scan"][1][1][1], 1), fmt(N["hs_start"][0], 0), fmt(T9["sel"]["tmin"] * 1e3, 3), fmt(T9["sel"]["tmax"] * 1e3, 3), fmt(T9["start_max"] * 1e3, 3))),
    ("E11-18", "DOCUMENT", "CONOPS owner", "the source-only statement in CONOPS (section 7b's text): with no usable pack the kit runs within the source envelope at the plug; a pack below about 2.4 V a cell holds VSYS under the converters' floor while it precharges; a brown-out on the source alone may latch the charger off until the source is re-plugged"),
    ("E11-19", "ANALYSIS", "Layer 4 coordinator", "L4-E9's entry findings that rest on the LM5069 (IF-05's hot short, D-07's power limit, R-118, the start's I2t) re-judged for the selected entry, with section 3c's figures"),
    ("E11-20", "EVIDENCE", "Layer 9 pre-layout analysis", "a hard short in service: the loop inductance from the source to a fault on DC_HS or VIN_RAW at least %s uH, or the peak through Q7 measured at most %s A (Q7's IDM derated), the trip threshold (%s to %s A) being only where the turn-off begins; with L4-E9's open item" % (fmt(N["l_min"] * 1e6, 2), fmt(N["i_allow"], 0), fmt(N["isc"][0], 2), fmt(N["isc"][2], 2))),
    ("E11-21", "INTERFACE", "Layer 4 coordinator", "L4-E5's V-A08 and its source-change transient row restated as the record's section 7a draft: the entry's breaker never trips (its current over %s A for less than %s ms, its filtered short-circuit sense under %s A) and VIN_RAW never under %s V (the guard's highest fall plus 0.1 V), in place of the LM5069's 3.13 ms timer and 8.41 V" % (fmt(N["ioc"][0], 2), fmt(N["toc"][0] * 1e3, 3), fmt(N["isc"][0], 2), fmt(N["guard_new"][0][2] + 0.1, 2))),
    ("E11-22", "EVIDENCE", "Layer 6 components", "R-b's cases (ii) and (iii) closed: the charger's temperature while R-b holds bounded inside %s to %s C (Layer 9 thermal), or TI's 0x0200 accuracy outside it and the clamp's maximum under VSYS_MIN (Q-TI), or the bench's current at 0x0200 and under VSYS_MIN at the inside air's ends; board P's copper under Q2 for TI's %s C/W" % (fmt(N["rb_temp"][0], 0), fmt(N["rb_temp"][1], 0), fmt(R["P"]["rja"]))),
    ("E11-23", "TEST", "prototype bench", "TEST-PLAN E4-O at the plug: the kit cold-soaked at -20 C with the pack inside, started from 9.00 V at the plug through the interconnect at its ceiling; the shedding sequence of section 3g runs, the mat on measured headroom: the cells reach 3 C, the hold clears and the charge begins; the time recorded and accepted against CONOPS's warm-up"),
    ("E11-24", "IMPLEMENTATION", "Layer 8 board A generator owner", "the dependency round's fallback on VBAT (a register row, never applied by this record): one EEHZK1V181P direct (C242139) and a hold-up bank of %d EEHZK1E471P (C242138) charged through R_CH %s Ohm RC2512FK-07330RL (C137025) and discharging through D_H B540C-13-F (C72264); the regenerated netlist carries them; the bank's hold recomputed from the fitted parts reads at least %s ms for the worst admitted step (%s W); withdrawn once E11-27 is applied (section 14: B1 carries the direct can, and the bank is not drawn)" % (BANK_N, fmt(R_CH, 0), fmt(R["G"]["worst_hold"] * 1e3, 3), fmt(R["G"]["worst"][1], 2))),
    ("E11-25", "EVIDENCE", "Layer 6 components", "the clarification questions of clarification/TI-QUESTIONS.md (Q-TI-11 to Q-TI-14 and the addendum to Q-TI-3) sent by the owner and answered, each answer filed against its dependency row D1 to D10 and judged: a limit closes a row production-wide, a typical figure does not"),
    ("E11-26", "TEST", "prototype bench", "the bench methods of rows D1 to D10 run on one unit each, every reading filed as a sample with its uncertainty and conditions, never as a limit; D2's recovery at most %s ms against the bank's %s ms assumption gives the engineering margin the record names" % (fmt(T_RESP * 1e3 / 5, 1), fmt(T_RESP * 1e3, 1))),
    ("E11-27", "IMPLEMENTATION", "Layer 8 board A generator owner", "apply_gen_sch_a_charger.py applied (sections 14 and 15): U3 BQ25730RSNR (%s) with pin 21 on CH_BATDRV; Q39 and Q40, two Nexperia BUK6Y10-30PX (%s) in parallel, sources on VBAT, drains on CH_BATQ, gates on CH_BATDRV; R17 and R149 on CH_BATQ; C236 EEHZK1V181P (C242139) on VBAT; U42 TPS16630PWPR from VBAT to VSYS_DOCK with R228 %sk 0.1 %%, C237 %s nF, MODE to GND, C238 1 uF at IN, C239 0.1 uF at OUT and D23 B540C from GND to OUT, within 20 nH of C236, J_DOCK pin 1 on VSYS_DOCK for board E's VSYS_E (section 16e), the HTSSOP-20 land checked against TI's PWP0020 drawing; CH_BATQ declared a segment of the pack path; the LFPAK56 lands checked against Nexperia's SOT669 drawing, seated by R17 with matched paths; the regenerated netlist reads each" % (R["H"]["cat"]["BQ25730RSNR"][0], R["K"]["cat"]["BUK6Y10-30PX"][0], fmt(F16_RILIM_K, 1), fmt(F16_CDVDT * 1e9, 0))),
    ("E11-28", "FIRMWARE", "firmware owner", "the BQ25730's register rules (section 14): EN_OOA 0 at boot; ChargeCurrent written for any charge (0 A at POR and after the watchdog's %s s), the watchdog serviced or WDTMR_ADJ 00; VSYS_MIN, EN_LDO, EN_PORT_CTRL, BATFET_ENZ and BATFETOFF_HIZ never written from their power-on values; the device ID %sh checked; R-a's bit following the hold flag in every state (S4's exception withdrawn); R-b' under VSYS_MIN: 0x0080 only, and no charge under %s V on SRN (section 15c)" % (fmt(R["H"]["wd_s"], 0), R["H"]["devid"], fmt(R["K"]["rb_floor"], 1))),
    ("E11-29", "LAYOUT", "Layer 9 pre-layout analysis", "the junction limit of record l9stk 15.5 (E-1; round 9, section 19c), sized before layout and measured on the specimen of section 17d (a coupon; the first prototype only once its three gates can be driven apart, section 23d; it blocks only the final release): the installed three Q39, Q40 and Q42 on one pour with R17 placed apart, each FET's (Zself + 2 Zmut) at most %.2f K/W steady with the band carrying %s A and R17 dissipating in place, R17's coupling into each junction at most %s K/W (heat R17 alone), so the hottest junction stays at most 150 C held at %s A from %s C for ANY split of the RDS(on) spread under the allowance (round 11, section 21: one FET at R / 2 takes 9/8 of the even split's loss, so record l9stk's even-split %.2f K/W is taken times 8/9; with Zself and Zmut read apart, the largest of each into any junction, (Zself + 2 Zmut) at most %.2f x 8 (1 - m)(1 + 2 m) / 9 for m = Zmut / Zself under 1/4, %.2f at or over it) (the pair's fallback, its Zself + Zmut at most %.2f K/W, the even split its worst); the pair's former %s K/W target and its 1 s, 20 ms and 244 us targets withdrawn with record l8p's breaker; the 18 A for 60 s and 10 A continuous kept, no protection lowered; the case-rise reading at 10 A alone does not close it; recorded OPEN in round 10 (section 20i) on the even split, corrected in this acceptance by round 11 (section 21d), CONDITIONAL on this measurement; the coupon also reads the PTC's site (RT1 at the drain tabs' centroid) against each junction with one FET heated alone at the worst split's %s W, so the thermal guard's trip side is judged on the hottest FET and not on the even split (round 12, the check V2's V2-m5; record l8p's guard); %s" % (R["S21"]["bar_new"], fmt(R["S19"]["i"], 2), fmt(R["S19"]["r17_allow"], 1), fmt(R["S19"]["i"], 2), fmt(R["S19"]["t0"], 2), R["S21"]["bar_old"], R["S21"]["bar_old"], R["S21"]["bar_old"], R["S19"]["rec"][2][2], fmt(R["L"]["plan"]["zsum"], 2), fmt(R["S21"]["p_worst"], 3), e11_29_method(R))),
    ("E11-30", "EVIDENCE", "Layer 6 components", "the WHOLE hot docking waveform accepted (sections 16d and 17b): %s A peak, time constant %s us, from a +%s C mounting base, once per docking event, taken whole in one FET's body diode; by the pulse qualification selected in 17b: %d parts, each %d pulses %s s apart at %s A peak and %s us (x%s), mounting base %s C, every part passing VSD at 80 A pulsed within +5 %% of its first reading, IDSS at -30 V and 25 C at most the printed 1 uA, RDS(on) at -10 V and 25 C within +5 %% and at most the printed 10 mOhm, IGSS at most the printed 100 nA; or Nexperia's written acceptance of the same waveform (Q-NXP-1); a sample result is not a production limit; on a failure board P's owner bounds the inrush (a slower discharge-FET turn-on or a precharge path, its normal charging and its ASCD turn-off re-shown)" % (fmt(R["H"]["Q"]["i_dock"], 1), fmt(R["H"]["Q"]["tau"] * 1e6, 1), fmt(R["K"]["air"]["route"], 0), F17_DOCK_N[1], F17_DOCK_N[0], fmt(F17_DOCK_N[2], 0), fmt(R["M"]["dock_q"][0], 1), fmt(R["M"]["dock_q"][1] * 1e6, 1), fmt(F17_DOCK_MARGIN, 1), fmt(F17_TMB, 0))),
    ("E11-31", "TEST", "prototype bench", "the three modes on the BQ25730 build (EN_OOA 0), piecewise (section 15d): pack absent, VSYS at least %s V; CHRG_INHIBIT 1 with SRN over %s V, VSRN plus 150 mV within 2 percent, under %s V at least %s V, between at least %s V; the held pack current at most %s mA with board E on VSYS_E; the start from cold at VBUS20 %s and %s V, VSYS's maximum capacitance and the always-on loads, at -20, 25 and %s C, with Fault VSYS_UVP clear, the hiccup and latch on a shorted VSYS and the re-plug; VSYS before EN_OOA's write recorded; VSYS's step response in S2 and S4 for each declared step against the converters' floor (D2, %s V of margin), the outlets held by R-c where a step uses more" % (fmt(R["H"]["floor"], 3), fmt(R["K"]["hi_v"], 3), fmt(R["K"]["lo_v"], 3), fmt(R["H"]["floor"], 3), fmt(R["K"]["inh_floor"], 3), fmt(FIX_HELD_ACC * 1e3, 1), fmt(R["E"]["vb_low"], 2), fmt(R["E"]["vb_top"], 2), fmt(R["F"]["air_hot"], 1), fmt(R["H"]["margin_floor"], 3))),
    ("E11-32", "EVIDENCE", "Layer 6 components", "the BQ25730RSNR's supply for the build quantity (five boards) from an authorised source, filed: LCSC read stock %d on 2 October 2026 (the Layer 6 author's L6P-F05: a procurement fact for the owner's list, not a reselection; TI and its distributors are the next sources to read), and the two battery FETs' (BUK6Y10-30PX, LCSC stock %d)" % (R["H"]["cat"]["BQ25730RSNR"][1], R["K"]["cat"]["BUK6Y10-30PX"][1])),
    ("E11-33", "IMPLEMENTATION", "Layer 8 board E generator owner", "apply_gen_sch_e_aux.py applied with E11-27 (sections 15a and 18): J_BLK pin 1 on VSYS_E; U12's VIN and EN and C31 on VSYS_E; the mixers' 12.0 V rail +12V_FAN from VSYS_E: U22 LTC3115EFE-1 as ADI's TA04 (L4 XAL6060-103ME 10 uH, C142 10 uF in, C143 22 uF out, C144 4.7 uF PVCC, C145 and C146 100 nF bootstraps, R105 1M and R106 90.9k FB, R107 40.2k and C147 820 pF on VC, R108 10k and C148 33 pF feed-forward, R109 35.7k RT, R103 1.5M and R104 255k RUN, PWM/SYNC to VCC); J_FAN1 and J_FAN2 four pins (12 V, GND, PWM, TACH) with Q9 and Q10 as open-drain PWM drivers and D7 and D8 removed; VSYS_E declared (source J_BLK, %s A: U12 %s, U22 %s at the floor, always on); +12V_FAN declared (source L4, %s A: two fans at %s); CELL_F's loads the pack path alone; E6_SW and E6_BST re-declared to VSYS's %s V; the FE and XAL6060 lands checked against ADI's FE20 and Coilcraft's drawings; the regenerated netlist and check_contracts read the dock's pin 1 as VSYS_DOCK and VSYS_E" % (fmt(R["N18"]["i_decl"], 2), fmt(R["K"]["aux"]["U12"], 2), fmt(R["N18"]["i_reg"], 2), fmt(2 * L7_FAN["i"], 2), fmt(L7_FAN["i"], 2), fmt(R["H"]["vsys_top"], 3))),
    ("E11-34", "INTERFACE", "Layer 4 coordinator", "apply_pcb_interfaces_dock.py applied (IF-AE-DOCK: pin 1 VSYS_DOCK and VSYS_E behind U42's eFuse, the alias, BAT-F06's charge_share replaced by the VSYS feed, the ground return with seven 813 contacts) and section 15e's texts for L4-E9's record: the IF rows of VBAT and the dock, the source-change rows, the two sentences that say no battery FET and the diagram's system-node label (%s to %s V)" % (fmt(R["K"]["vsys_sup"], 3), fmt(R["H"]["vsys_top"], 3))),
    ("E11-35", "EVIDENCE", "Layer 6 components", "the mixers %s (Layer 7's %s at %s, 2e): their starting current, PWM input level and hole pattern from the maker's manual M0011876C or the bench (Layer 7's F-L7-11); against the rail: the start on a 12.0 V bench channel recorded, and against U42's room %s A at the floor (section 18b: %s W at the rail, %s times one fan's running power); the supply range %s to %s V is met by the rail's %s to %s V (section 18a), no longer by VSYS_E" % (L7_FAN["mpn_mixer"], L7_FAN["rec"], L7_FAN["commit"], fmt(R["N18"]["room"], 4), fmt(R["N18"]["start_room_w"], 2), fmt(R["N18"]["start_mult"], 2), fmt(L7_FAN["v_lo"], 1), fmt(L7_FAN["v_hi"], 1), fmt(R["N18"]["vout"][0], 3), fmt(R["N18"]["vout"][2], 3))),
    ("E11-36", "EVIDENCE", "Layer 6 components", "the battery FETs' RDS(on) at VGS -8.5 V and a 150 C junction at most %s mOhm (the allowance of section 16a): Nexperia's maximum at that point filed, or a pulsed Kelvin reading on parts from the build lot in an oven at 150 C (a sample, not a production limit: only the maker's maximum closes it for every part); a reading over it reverses the allowance and E11-29 is re-sized before layout" % fmt(F16_RA * 1e3, 3)),
    ("E11-37", "EVIDENCE", "Layer 6 components", "BATDRV with the three-device network Q39, Q40 and Q42 (round 9, section 19d; record l9stk's C3): TI's statement of what the BATFET's 5 nF bounds for three P-channel FETs on one BATDRV (Ciss at which VDS, or a gate charge; Q-TI-17 extended to three, drafted in clarification/TI-QUESTIONS.md, not sent), or the bench's BATDRV behaviour with the three (Ciss %s nF typical at -15 V, about %s nF near 0 V) at -20, 25 and 70 C: supplement entry, the ideal diode's 30 mV regulation without oscillation, LDO mode at VSYS_MIN within its printed band, each FET's share of the current in LDO mode and as an ideal diode, and each junction on the shared pour; a result with the pair does not transfer; Q-TI-17 (e) and (f) (round 11, section 21d) ask the 5 nF's drain-source voltage, the pair's typical figure and the gate load TI accepts; on a negative answer the supplier's correction scope is round 11's (ii): the pair at its fallback, its bar measured on the coupon, Q42 removed (a draft then owed; sections 16c, 19d and 21d)" % (fmt(R["S19"]["ciss3"][0] * 1e9, 2), fmt(R["S19"]["ciss3"][1] * 1e9, 2))),
    ("E11-38", "TEST", "prototype bench", "the dock's VSYS branch, the whole fault envelope (sections 16e, 17a and 18), at -20, 25 and 70 C and at VSYS 9.688 and 17.375 V, ten times each: (a) U42's limit on a slow ramp at VIN - VOUT 1 V between %s and %s A, and recorded at 17 V; (b) an operating overload (2.88 Ohm, and a load just under 2 x I(OL)): settled at or under %s A within 1 ms, off within %s ms, retry after %s to %s ms; (c) a 10 mOhm short applied at board E's VSYS_E while on: the peak through J_DOCK pin 1 recorded against the %s A extrapolation (a target: a reading over it revises 17a) and over %s A for at most %s us, U42's IN at most 60 V, OUT's least recorded against -0.3 V (Q-TI-18); (d) a start into that short: at most %s A after the first 100 us, the time to thermal regulation and the regulated current recorded, off within %s s of regulation's start, the total on-time recorded; (e) one hour of retry into it at 70 C: the 813's body at most 85 C; (h) an intermittent short applied and removed at 10 Hz, 1 Hz and 0.1 Hz for ten minutes each at 70 C, and removed once during limiting and once during the retry's off-time: the recovery of VSYS_E and U22's rail recorded, the 813's body at most 85 C; for every case the 813's resistance at 1 A four-wire within +10 %% of its first reading and at most 20 mOhm, the plunger free, the 24 AWG's body at or under the rating its maker states (F-L7-08; 85 C until one is named) and its insulation unmarked, board A's and board E's copper at the contact lands and under U42 unmarked and at or under 85 C, D23 (VF at 5 A within +5 %%) unchanged; (f) with the fans %s on the 12.0 V rail (section 18): U12, U22 and both fans started one at a time by the PWM-duty ramp, and both fans' duty stepped 0 to 100 percent together, at VSYS 9.688 V: U42 never limits (FLT high), VSYS_E at least %s V, U22 never disables (the rail never under %s V), the branch's current at full speed recorded against the declared %s A; (g) one fan stalled and the 12 V rail shorted at the header, each at 70 C: U22 limits or disables and recovers, VSYS_E never under U12's 3.8 V, the controller keeps running, U42's retry seen or not and recorded" % (fmt(R["L"]["ilim"][0], 3), fmt(R["L"]["ilim"][1], 3), fmt(R["L"]["ilim"][1], 3), fmt(R["L"]["tcl"][1] * 1e3, 0), fmt(R["L"]["tretry"][0] * 1e3, 0), fmt(R["L"]["tretry"][1] * 1e3, 0), fmt(R["M"]["i_pk"], 0), fmt(R["M"]["fast_typ"], 1), fmt(R["L"]["tsoft"] * 1e6, 1), fmt(R["L"]["ilim"][1], 3), fmt(R["M"]["treg"][1], 1), L7_FAN["mpn_mixer"], fmt(R["N18"]["vsys_e_at_lim"], 3), fmt(L7_FAN["v_lo"], 1), fmt(R["N18"]["i_decl"], 4))),
    ("E11-39", "FIRMWARE", "firmware owner", "board E's mixer fans (four-wire, on the 12.0 V rail) started one at a time, each by a PWM-duty ramp into the fan's PWM input, never both within 1 s and never while U12 or U22 starts (sections 17a and 18c; Layer 7's F-L7-05): U22's %s ms soft start covers the rail's rise only, and the fans' start current is NOT READ, so the ramp is what keeps the start near the running current under U42's least limit %s A" % (fmt(R["N18"]["tss"] * 1e3, 0), fmt(R["L"]["ilim"][0], 3))),
    ("E11-40", "IMPLEMENTATION", "Layer 8 board B generator owner", "a FINDING, not a draft (section 18d; Layer 7's F-L7-02): board B's J_FAN1 to J_FAN3 carry +5V_Sn (%s V) on pin 1 and declare the fan at %s A, and no 12 V net exists on the board; the coolers %s print %s to %s V: a regulated 12.0 V feed per slot (a step-up from +5V_Sn, Layer 7's 0.436 A each at full speed, keeping an empty slot off) or a 12 V feed from board A over the bay harness; the header's pin 1 becomes 12 V, the slot budget's fan row 2.0 W at 12 V, the module's Fan_PWM and Fan_Tacho kept" % (fmt(R["N18"]["b_slot_v"], 1), fmt(R["N18"]["b_fan_a"], 1), L7_FAN["mpn_cooler"], fmt(L7_FAN["v_lo"], 1), fmt(L7_FAN["v_hi"], 1))),
    ("E11-41", "TEST", "prototype bench", "DD-3's condition (round 9, section 19e; record l9stk's DD-3): L2 (SRF1260-1R0Y) on board E's land at the TPS48110 breaker's highest held current, %s A, its winding's hot spot read by resistance or a thermocouple in still air at %s C (or referred to it), three samples: at most %s C including the rise; or Bourns's statement of the rise in this connection; or a choke rated at least %s A at a %s K rise with board E's input filter shown again to its attenuation; a reading over it returns to L4-E11 for the choke, and the second pass FET of section 19e is drafted with the choke in one board E change" % (fmt(R["N"]["ioc"][2], 3), fmt(R["S19"]["t0"], 2), fmt(R["S19"]["l2_tmax"], 0), fmt(R["S19"]["l2_irms_need"], 2), fmt(R["S19"]["l2_rise_rated"], 0))),
    ("E11-42", "TEST", "prototype bench", "IF-1's hold (round 9, section 19f) on board A's first prototype docked onto a board P carrying record l8p's breaker, with no source: (a) twenty dockings, U42's output and RAIL_EN low until at least %s ms after VBAT passes %s V, and the breaker's start ending with its TIMER under the fault threshold, each recorded; (b) an undocking and redocking after 0.5, 1 and 2 s with VBAT held up by board A's capacitance: U46 asserting as VBAT falls under %s V and the following start held the same way; (c) MAIN held through a docking: the release to KILL recorded, at least %s ms of U1's blanking left; (d) with a source present at the plan load, the breaker's start completing, or the -1 latching while the source keeps the kit up, as section 19f bounds; (e) the static draw from VBAT while U46 holds at most %s mA at 16.8 V" % ( fmt(R["S19"]["hold"][0] * 1e3, 1), fmt(R["S19"]["rise"][2], 3), fmt(R["S19"]["fall"][2], 3), fmt(R["S19"]["kill_left"] * 1e3, 1), "%.0f" % (10 * R["S19"]["static_sum"] * 1e3))),
    ("E11-43", "IMPLEMENTATION", "Layer 8 board A generator owner", "apply_gen_sch_a_dd7.py applied after record l8p's apply_gen_sch_a_ptc.py and this record's charger draft, released with l8p's three drafts (rounds 9 and 10, sections 19h and 20; record l9stk's DD-7, record l8p's route R1 and its L8P-F04 and L8P-F05): the input-return reset Q44 to Q46, R106 and D25 on DOCK_EN_RET (Q46's gate on DD7_N); the loop reader U48 with R109, R144, R249 and R250; the hold and the release on CELL+ alive U47 with C241, R85, C248, R107, R108, Q52, R254 and R255, the arm Q50, Q51, R251, R252, R253, R84 and D26; the charge inhibit Q47, Q49, R82 and R83 on CH_BATDRV and the bleeder Q48 and R256 on CELL+; DD7_VC from R233 and D27; TP1 and TP2; the layout keeps Q49 within 10 mm of the battery FETs' gate node and U47 and U48 beside C238, their VDD bypass; R249 to R256 and C248 sit above the main-based order's highest, so d8dec31's mainpb takes the next ones; check_dd7_netlist.py reads DRAWN on the regenerated netlist; L4-E9's change list keeps the draft after l8p's PTC and before mainpb (the integrator's)"),
    ("E11-44", "FIRMWARE", "firmware owner", "record l9stk's IF-7 with section 19h's hardware: the bridge reports a tripped breaker (the BQ25730's ADC reads SRN dead while the gauge reports its FETs on, or the charge inhibit holding) and writes ChargeCurrent only after the terminal reads alive; R-b's bound kept; the hardware inhibit holds the charge whether or not this rule runs"),
    ("E11-45", "TEST", "prototype bench", "DD-7 and E-14 (rounds 9 and 10, sections 19h and 20) on board A's first prototype with board P's -1 breaker and record l8p's reverse-charge detector: (a) the -1 latched by a fault, no source, then an input applied as a step and as a 1 V/ms ramp at 9, 12, 24 and 36 V: DOCK_EN_RET low for at least %s ms and the breaker restarting within %s s of VIN_RAW passing U34's threshold (the pad under C-1c's trip); (b) with the pack alive, an input's arrival leaves DOCK_EN_RET unchanged and the kit up; (c) E-14 extended: a hard short kept on VSYS, so the -1 latches again with the input present, and ChargeCurrent forced to its register maximum by the host: the current into PACK_P at most 1 mA and the breaker FET's junction (VSD method) within 2 K of its case for 10 minutes; (c2) the same with a %s ohm fault removed after the latch (B-R2, route R1): the charge into PACK_P ends within %s ms of passing board P's threshold, TP2 (DD7_N) low within %s ms of DOCK_EN_RET falling, the battery FETs held off at least %s s after DOCK_EN_RET rises (TP1 over 0.79 V), then released once CELL+ reads alive, the breaker restarted within %s s; (d) failures, each found by its row: U47's RESET1 held high (the hold lost, (c2)), Q48 opened (the latch reads the leak, (f)), Q49's gate opened (the inhibit lost, (c)); (e) L8P-F04's interface alone: DOCK_EN_RET pulled under 0.06 V by a stand-in at BRK_VIN 7.6, 10.6 and 16.8 V with RT1 replaced by 5 kOhm: CH_BATDRV at VBAT within 1 ms whatever CELL+ reads, released no earlier than 1.0 s after the release; the loop closed at RET 0.9 V and DOCK_EN_OUT 2.0 V: nothing inhibited (section 20c); (f) L8P-F05: the breaker held off with BRK_VIN at 16.8 V and, from a bench supply through 10 mA, at 29.2 V: CELL+ under %s V while the inhibit holds and the inhibit kept until the breaker is enabled; (f2, round 12, the check V2's V2-B1) the bleed timed: CELL_FUSED charged to %s V, the inhibit set and the breaker held off, the battery FETs' pour at 125 C and the breaker FETs' case at %s C (or %s uA injected into CELL+ on a cold board): CELL+ under %s V at least 0.1 s before the same unit's hold ends as (h) times it; the current into CELL+ with both FET groups hot read, at most %s uA; U47's RESET current read at the set and with the breaker restarted, at most %s mA; (g) a back-fed precharge (the gauge's FETs off, the charger in LDO mode) at 25 and 70 C: CH_BATDRV follows BATDRV and nothing is inhibited; (h) the hold timed from five triggers at -20, 25 and 85 C: at least 1.0 s each, and each at least 0.1 s longer than (f2)'s bleed on the same unit" % (fmt(R["S19"]["pulse"][0] * 1e3, 1), fmt(R["S19"]["dd7_total"], 3), fmt(R["S19"]["r_fault"], 3), fmt(R["S20"]["charge_end"] * 1e3, 2), fmt(R["S20"]["t_set"] * 1e3, 2), fmt(R["S20"]["hold_min"], 3), fmt(R["S20"]["restart"], 3), fmt(R["S20"]["dead"] - 0.5, 2), fmt(R["S20"]["vs_max"], 1), fmt(R["S22"]["t_held"], 0), fmt(R["S22"]["src"]["hot"] * 1e6, 0), fmt(R["S20"]["dead"], 3), fmt(R["S22"]["sel"]["lim"] * 1e6, 0), fmt(R["S20"]["i_rec"] * 1e3, 0))),
]


def main():
    try:
        os.nice(10)
    except OSError:
        pass
    sys.stdout.write(render(compute()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
