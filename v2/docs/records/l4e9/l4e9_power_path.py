#!/usr/bin/env python3
"""l4e9_power_path.py: layer 4 task L4-E9 (MESHSAT-1357, 1 October 2026). The connected power architecture and Layer 4's
closure gate for it: the executable reconciliation of every interface between the blocks of the selected architecture
(A1, the owner's D-06 single 4S3P; A2 recorded as a proposal), with the simultaneous-operation, startup and fault traces
that are computed here and the closure gate's predicate.

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured. No generator, registry, rendered page,
Layer 3 file, pcb_interfaces.yaml, HW-FW-CONTRACT.md or other record is edited. Every figure is READ, never retyped:
  - from the generators (gen_sch_a.py, gen_sch_e.py, gen_sch_p.py) by their syntax tree: the rail declarations and the
    part value texts;
  - from board A's committed netlist (the VBAT capacitors, U17's sense nets);
  - from the records' committed outputs (L4-E4 to L4-E8, the energy replay, s120, the power budget, the load trace) by a
    pattern on the line that prints the figure;
  - from the makers' documents by pdftotext on the cited page;
  - from pcb_pack_protection.yaml, pcb_envelope.yaml, pcb_interfaces.yaml and HW-FW-CONTRACT.md by their text.
Each input is pinned by sha256 (exit 2 otherwise). L4-E8's record is read from the tree if it is there and otherwise from
the accepted commit L4E8_COMMIT on fnd/l4e8 (the coordinator's check 3); the bytes are pinned either way. The accepted records
of L4-E7R, L4-E10, L4-E11 and L4-E12 (and the drafts and outside-contact texts this record cites from them) are read from the
tree when the tree's file is the pinned one and otherwise from their named commits (FROM_COMMIT).

Update round (2 October 2026, the coordinator's instruction): the architecture and its gate brought up to date with the accepted
results of L4-E10 (FEA-008, final), L4-E11 (the vehicle entry replaced by a TPS48110-Q1 breaker with a CSD19536KTT, D-06's
interconnect, U-04's arrangement) and L4-E12 (the electronics against the inside air, T-H1's binding line); E11-19, every finding
that rested on the LM5069's power limit, re-judged for the selected entry (section 12); L4-E13 (U-03) was then pending.
Update round 3 (2 October 2026): L4-E13 accepted (check 3 at fae419d1, its update after set 25 by check 4 at 33b6b7be, read
from the tree): U-03 becomes a CONDITIONAL
DOWNSTREAM UNIT SELECTION (PANEL-ACC), leaves the choices that could overturn the architecture and enters the register
(section 13).

The few figures this record sets itself are named where they are used (the copper constants of the F1 bound, the
capacitance retained under bias in the pack-open bound, the back-feed diode's drop taken as zero). Evidence classes, from
strongest to weakest: MAKER, NETLIST (and the generator's declarations), MODELED, INFERRED, CONDITIONAL (a calculated result
resting on an unwarranted assumption or an open measurement), ASSUMPTION (a figure no document gives), PENDING (waits on a
record not yet landed). A row's class is its weakest check's.

Run from the repository root:  python3 v2/docs/records/l4e9/l4e9_power_path.py > v2/docs/records/l4e9/l4e9_power_path.out
Needs pdftotext and PyYAML. A few seconds. Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed;
4: a predicate failed (a check's arithmetic, the gate's rule, the register's or the handover's form)."""
import ast
import glob
import hashlib
import math
import os
import re
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
L4E8_COMMIT = "3c8f7a1fe0995b1d37f03fcace44544c6c17dcbe"     # fnd/l4e8, the coordinator's check 3 (accepted), figures as a282c8b7
L4E7R = ("none: L4-E7R is accepted (the coordinator's check 4, fnd/l4e7 91e9a4b5; its figures at 675b8068): the CS101 correction moved the "
         "bulk ahead of the sense bank and filtered the trip input, so defect D-01 is resolved in design (drafted, not applied)")

PINS = {
    "gen_a": ("v2/ecad/tools/gen_sch_a.py", "6a136feec6c9cf4e2011ed8c45a1f2e0adc3e263718c355b4b909872ee5d3c4b"),
    "gen_e": ("v2/ecad/tools/gen_sch_e.py", "f846e138cb53a8c63247efb3ad7b5cc44a68cb73e71699c65fd53b63c01af186"),
    "gen_p": ("v2/ecad/tools/gen_sch_p.py", "740817ada5c8e14af8c8e001b775e09cbae94d6a03ad462ee2e1c1755bc935a3"),
    "net_a": ("v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "6c40250c47195ebb7b2ae1388e284dc7f2fba9f2e683f654a47c98444290e8c5"),
    "l4e4": ("v2/docs/records/l4e4/l4e4_limits.out", "f68bf6951a6361caf6c41db14d86d735f9e3e9736723984ef61234aa10a80694"),
    "l4e5": ("v2/docs/records/l4e5/l4e5_source_control.out", "f9c98ec5c43ada0e1a5a033a794c98b45f110ffcb0a67ff8c81a31fede134e71"),
    "l4e6": ("v2/docs/records/l4e6/l4e6_fault_handling.out", "4f7cefb270f326d1956a7c5b1e11c8901e4f21a0ff3feb4fcb6d66fb78728c66"),
    "l4e8": ("v2/docs/records/l4e8/ripple_dense.out", "3b751989b8b70345469f2fdc14640fe041415b7333d669b205d2c675b046ab84"),
    "replay": ("v2/docs/records/l4e/l4e_replay.out", "59c6eeab16da98f8ddf16880ddcdc1d2a2c910f4256be9b69aade49dd4d2726d"),
    "s120": ("v2/docs/records/s120/vbus20_bound.out", "35c3e2e30fc637e0321daa1111e02aba84ab94fe789c59466e1f12c61470f823"),
    "budget": ("v2/docs/records/rv-pwr/pwr_budget.out", "58e40cf604804cc9d70c7fbeb1012be4552563fcc8ae7ef6755003c33acb902f"),
    "trace": ("v2/docs/records/l3batt/load_trace.out", "e35e62483b67fbe71bf89b819f6be46173ce708a8a62c683905d55a37ad4c218"),
    "packprot": ("v2/ecad/tools/pcb_pack_protection.yaml", "ab1dbc3f3f69aa4687a4fa9745c0cbdc96d0521146dc5d3f84698656e33c484b"),
    "envelope": ("v2/ecad/tools/pcb_envelope.yaml", "35cf43a2b7098a76abb4919685ece4d6e352331628f5f242c1492d9fcbbf2864"),
    "hwfw": ("v2/docs/HW-FW-CONTRACT.md", "1c211e467d81b8b70546bc4435c65d4bd2dcd0d2fc3606714a746b4d8d0ac1fa"),
    "ifaces": ("v2/ecad/tools/pcb_interfaces.yaml", "9ec50ccfae3b70a0b27c1f32fdf0461eadd99012cfe8954409bc2573771680c0"),
    "lm5176": ("v2/vendor/ti/lm5176-datasheet.pdf", "98191bec36d43771affa3e1540f6e1737347c19a1602747ffb4327509550a820"),
    "lm74700": ("v2/vendor/ti/ti-lm74700-q1.pdf", "e16b3a8c0023201fafa5825436f5f2dd6f885b92b84e65602b3f50d741c58b6f"),
    "csd19532": ("v2/vendor/power/ti-csd19532q5b-n-fet.pdf", "353ce937cff0b719e730010829720d25c2ece3637ed92fb7ad8cc370438559d1"),
    "bsc039": ("v2/vendor/infineon/infineon-bsc039n06ns-rev2.4-c534330.pdf", "8d95c1da9c78b3afb037e1f80c3bea1ed0f874f689e3a0c96d926dafe6a437b9"),
    "smcj": ("v2/vendor/power/littelfuse-smcj-series-tvs.pdf", "6e610db955ed876306999009c62b242f7de9bb05e2cd9717288a96586a5093ea"),
    "tps2596": ("v2/vendor/power/tps2596.pdf", "66f6bae4494f7bfe7dfdc314e508f0291d9ca1e87265cca9b6fdfeaa5cb19fe9"),
    "lm5069": ("v2/vendor/ti/ti-lm5069.pdf", "d60d8106a6e8113900ff8b9576dd959942fa7169742baf0beeb30684d4d64681"),
    "ina226": ("v2/vendor/ti/ti-ina226.pdf", "c9b67f886d4a5241a5e070723f7b61867409eeb27eed768b9cdd9cb17e03ca2d"),
    "bq25731": ("v2/vendor/ti/bq25731-datasheet.pdf", "3e5e927fdf63cf6a2397630987c58e947ebc80d5a1cfc93fb1fb58d98bb58973"),
    "fuse297": ("v2/vendor/keystone/littelfuse-297-ficcorp.pdf", "98a7e99bc5bbdf2abc9f329de5b779ea97fc78a3ba9aa8d8fecc0ec5b9c3a778"),
    "vh": ("v2/vendor/connectors/jst-vh-catalogue.pdf", "d51e669c597988b20c0963daf5bef7356cbd2104c1f867e9107c6fa6cd2b899c"),
    "millmax": ("v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf", "8ef40cd98d95c653ce506a1af457656b287a475342684ac110cf594f923782d6"),
    "xt60": ("v2/vendor/battery/amass-xt60-spec-tme.pdf", "c2cbb5962c1f37da89e76e505c75184dd07e84eec3a6fe5f24569dafc6f6b9e9"),
    "dec31": ("v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md", "094817023210d1b09d92e62716ba550d0fb5b11affc75fe18986bfc6ebae3609"),
    "fuse997": ("v2/vendor/power/held/littelfuse-997-mini58v-rev2025-11-18.pdf", "437b1fd2c8cb3ef16107ec14d096b31ef3c3cb83893325234e880deb7540393e"),
    "keystone": ("v2/vendor/keystone/M65p42.pdf", "caa141ea51ac68cf80ab6e14ad2075fcfc76206451f4bfe45330005c0deaf395"),
    "l4e7r": ("v2/docs/records/l4e7/l4e7_stage_settings.out", "b0d0953e965a983c9b16271bcf476f1f6b3f88ad9fc995cd8436edeb8f5dd055"),
    "l4e10": ("v2/docs/records/l4e10/l4e10_cell_thermal.out", "0eb554285580b8f20f05440f2810300cf5c65e9b8b2ea93830474f0d83df2283"),
    "d38999": ("v2/vendor/d38999/amphenol-d38999-iii-federal.pdf", "13a19268ba5939d9e4df5a20f9db84bb72e86525b82f0586c85696e42c126a2b"),
    "reqs": ("v2/ecad/tools/pcb_requirements.yaml", "b624ac495650a3592c45a37610375fb05bf7b775042cf3de7ec8979bc46a6e50"),
    "chgseq": ("v2/docs/review-packets/battery/CHARGER-STATE-SEQUENCE.md", "44fdf9a022c49337d60eeefd15b7e7267fb5a4659449f7dc5c38153a9786548f"),
    "yageo": ("v2/vendor/passives/yageo-cc-series.pdf", "61a606825ab314ea318cfb5362848a62fdffb851efa9818d642e9a541c56a648"),
    "lcsc": ("v2/ecad/tools/lcsc_fill.py", "6888362e4a3295d0e1d595f65c03d5c13353d4785d7821c86e91f470a1cf6410"),
    "ecss": ("v2/vendor/standards/ecss-q-st-30-11c-rev2-2021-06-23.md", "576256819950c4432b48769e5f642ee5bfb0eed4f025c03fb9727de7dbeabeea"),
    "chain": ("v2/ecad/tools/pcb_energy_chain.yaml", "a09ca0293afd1f7c553cbffb5b95bc33ae58688a4c20b8de65ec47c15d45996c"),
    # the update round: L4-E10's page, L4-E11's output, page and entry draft, L4-E12's output and page
    "l4e10md": ("v2/docs/records/l4e10/L4E10-CELL-THERMAL.md", "0be7bf53a380b58d109623ce96176e6d24601cd2e180c9fd1a04b5a2cfaa6a2c"),
    "l4e11": ("v2/docs/records/l4e11/l4e11_power.out", "93de40df68d0b88e1eb281db133c240bdbfe81762056f62a72a6b3b1a0f25c59"),
    "l4e11md": ("v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md", "f8d214548f24be8f3fe66f505caedb8de946f95e9c712d5865a891a701c52ced"),
    "e11entry": ("v2/docs/records/l4e11/apply_gen_sch_e_entry.py", "418ea548a833b49f2fe923cb5ff776938bf73759521df781b4716c71536c4d32"),
    "l4e12": ("v2/docs/records/l4e12/l4e12_thermal.out", "a240910031996ab9260f6f09672cc7df3dfe515350d40079a2e2e1bc4b80fe45"),
    "l4e12md": ("v2/docs/records/l4e12/L4E12-ELECTRONICS-THERMAL.md", "f7b568e072b8a7b33396900e12f304b30858da6d79ac9fedf0879539508cbf08"),
    # the outside-contact texts the owner's list names (drafts the owner sends; the session contacts no one)
    "cl_topwell": ("v2/docs/records/l4e10/clarification/topwell-hl18650v.txt", "1ca762d83bbb58b2fa493970878970e173c23f91ce7d7bb4518dbc147a07e5e9"),
    "cl_eaton": ("v2/docs/records/l4e10/clarification/eaton-scf9550.txt", "9dffb95e8b4874fc0d08824b39d6174372a64e0cbda066241900d6ffdcdc5cb2"),
    "cl_pdi": ("v2/docs/records/l4e12/clarification/pervasive-displays-e2370ks0c1.txt", "4f7db1348cc0b4aca473c17f010085ca9095bf538f580c48804be5602418c117"),
    "cl_sensirion": ("v2/docs/records/l4e12/clarification/sensirion-sgp41.txt", "43c47549235fe6e8162b200324cedd7b34a342bb2a1cb0abf97311f39a48da83"),
    "cl_adi": ("v2/docs/records/l4e7/clarification/analog-devices-lt8705a.txt", "97d8217092eae7ac41cc7c3a7303696cf9494bfc8df14171fcc69c6862f86cfa"),
    "cl_milliohm": ("v2/docs/records/l4e7/clarification/milliohm-hojlr2512.txt", "e920420419a677e0b723f8c09b26dc817efcc29124dc742fc4e813c4279ff8f6"),
    "cl_vishay": ("v2/docs/records/l4e7/clarification/vishay-wsl2512.txt", "5d96017a5051257bff5571e27ece120240d8710383a400a6acfed59cd3726b08"),
    "cl_ti": ("v2/docs/records/l4e7/clarification/texas-instruments-ina169.txt", "405fb3988f41d8ac98dce3d5ec1cb4af1a0b5d635b109cf71772557c25ab3854"),
    "ti_review": ("v2/docs/review-packets/battery/REVIEW-REQUEST.md", "91a257430cbeb53a672ca57592bb75092a98a761d1c8ee7bbaefa95e339b102e"),
    "cl_gc": ("v2/docs/records/l4e12/clarification/ground-control-rockblock-9704.txt", "738245875bec70c55d1ec105fb566248c98351095a268ffcd25d2b76e3bea85f"),
    "cl_nicerf": ("v2/docs/records/l4e12/clarification/nicerf-sa868.txt", "92324668c17d4f6c7b45b6f9528d08a7c2ae4df1c1839fc82fb6eeb9f7a585b7"),
    "cl_bulgin": ("v2/docs/records/l4e12/clarification/bulgin-pxp4043c.txt", "c7accd3dd6dc1d8993de6ffc37e4febba71302e878b3cdf0f3f2f30bc2a4457e"),
    # update rounds 3 and 4: L4-E13 (U-03), accepted by the coordinator's check 3 at fae419d1 and, after set 25 (L4-E7R
    # accepted), check 4 at 33b6b7be; read from the tree
    "l4e13": ("v2/docs/records/l4e13/l4e13_panel.out", "7d2f15547dd6a4abec7449657004d5039913e8dc329b1d5886cf4f26ed2b925b"),
    "l4e13md": ("v2/docs/records/l4e13/L4E13-PANEL.md", "1c7f11716db4c2f2d1fa31327050afac8eb225c8ed8552091845cbdb090bf191"),
    "l4e13chk": ("v2/docs/records/l4e13/checks/check-l4e13-3.md", "88539c7aeaf2f99d8ed0364ac86f0cb312b9322eeeb6ac860ffa3d35e53ec306"),
    "l4e13chk4": ("v2/docs/records/l4e13/checks/check-l4e13-4.md", "5a08480af4695e61752d04852d8647e0276f292771596281968acf8903bc73e8"),
    "cl_sunpower": ("v2/docs/records/l4e13/clarification/sunpower-spr-e-flex-100.txt", "453a5a957648a322dc6b011c4c0a601c4af7a41d527f7ef4ab3cd0b79538e08c"),
    "cl_solbian": ("v2/docs/records/l4e13/clarification/solbian-sx-156.txt", "fb66bfb76e7e252ce9df361cd59dcc756be2764a1dcfbd5ef8632346b7a36b1f"),
    # update round 5 (the owner's instruction of 2 October 2026, Layer 4's remaining dependencies): the three dependency rounds,
    # each accepted by the coordinator's check 4 (L4-E10 at e464ff88, L4-E12 at c933724e, L4-E11 at f1856bfd), and the drafts they
    # add; read from the tree
    "l4e10chk4": ("v2/docs/records/l4e10/checks/check-l4e10-4.md", "eb1fe2846e37cf52db8dc1475c0064bb1b37112e669ba3667ca0e0c8c05f4fc1"),
    "l4e12chk4": ("v2/docs/records/l4e12/checks/check-l4e12-4.md", "2c4607d59756da7967ac4b68b6870a8e89f972469135b33deaf0ae634ceacb6b"),
    "l4e11chk4": ("v2/docs/records/l4e11/checks/check-l4e11-4.md", "b0a03440a9bb9a75806a7ba692fde8bc6e72ec4d419b39e8fe92f1ad469f6e65"),
    "th1proc": ("v2/docs/records/l4e12/T-H1-PROCEDURE-DRAFT.md", "c537143762940314a2693c6bc06c0537e7b1c8cab99d7610e3c980312288cfc3"),
    "cl_tiq": ("v2/docs/records/l4e11/clarification/TI-QUESTIONS.md", "a01be397bb01642386c074aedc4c8a69e16bea14f6441e2909d6c599b3e065fd"),
    # the consolidation: the tablet's service budget (a PROPOSAL, l3batt), the one budget input not read above
    "tablet": ("v2/docs/records/l3batt/tablet.out", "d71429a9bd6d60a51662f1a4826db398c629cb3675b8c6668e3aba1fb60a8194"),
    # the consolidation's results: L4-E11's charger selection (B1), check 5 at 5aa18a69, and L4-E12's thermal verdict (T-H1
    # decides), check 5 at 7f41632d; read from the tree
    "l4e11chk5": ("v2/docs/records/l4e11/checks/check-l4e11-5.md", "46f993e88a7622221d0c321ea6bb206e20070d82def06dc82620fdd3d5b8c337"),
    "l4e12chk5": ("v2/docs/records/l4e12/checks/check-l4e12-5.md", "12f3ceb053d6e6b5b27912943688ae03c7718dc04bcc752c7d45a4f6191eaeaf"),
    "e11charger": ("v2/docs/records/l4e11/apply_gen_sch_a_charger.py", "8adf97ade0cf11ec5b292527cbd2733adaf3b7a60292644a686bd5c4d2782620"),
    # the third result: L4-E10's cell route (U-01), checks 4 and 5 at 1c321773, with its drafted request to Saft; read from the tree
    "l4e10chk5": ("v2/docs/records/l4e10/checks/check-l4e10-5.md", "cdaa7429e99b6c71235fd21d16431f76cb8533751c575a25909b5f96821b7e67"),
    "cl_saft": ("v2/docs/records/l4e10/clarification/saft-mp176065xtd.txt", "6a47b9b803041549bbde1f8de1915f4289bfd5720fab4c61aaa79393fb36752d"),
    # the fourth result: L4-E12's heat-rejection comparison (U-02 a closure condition, one bench point), check 6 at 589f18ac;
    # read from the tree
    "l4e12chk6": ("v2/docs/records/l4e12/checks/check-l4e12-6.md", "c1b41234def44747535389cc5561aa22471cf970500680b6156d53f15ad9c711"),
    # the owner's amendment of 2 October 2026, 14:20: L4-E12's thermal reconciliation (check 7 at 6f8fd652), L4-E10's battery
    # comparison (check 6 at e2d20bf2) and the findings ledger's resumed verification (fnd/l4close at 65be2c2c); read from the tree
    "l4e12chk7": ("v2/docs/records/l4e12/checks/check-l4e12-7.md", "ec5ee21523560a719a0e2ff79d98b0bf84f9277629590757f66b4bd8c722906d"),
    "l4e10chk6": ("v2/docs/records/l4e10/checks/check-l4e10-6.md", "2bd4287f3736da75a0dd3d730666362f62b6371aa5d305c99781ef1679c7697e"),
    "ledger": ("v2/docs/records/l4close/FINDINGS-LEDGER.md", "9ed580a8dd2f35c80ca86fbebf0ef6ff1cb5617f48e730a68ecfed16094666d1"),
    "verify": ("v2/docs/records/l4close/verify_risks.out", "fd2dc6b2c1e723be2316052ec0dc76127605e2334fb80d5dc4e587b387df257c"),
    # the last add-on: L4-E7's solar-fault remedies (check 5 at 573fd5b8), its page and its drafted guard; read from the tree
    "l4e7md": ("v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md", "3928e30da2d008a55aa64eaf91b65d55b34d22b16d2b9e93cbc8fec33b9ac308"),
    "e7guard": ("v2/docs/records/l4e7/apply_gen_sch_e_solar_guard.py", "c383718b93c0efadcf6251b2e87fc41eb81a573069b0ce7cb64e185446233469"),
    "l4e7chk5": ("v2/docs/records/l4e7/checks/check-l4e7r-5.md", "eec75531f82ced65b7c082e7ffc0c2037a55c24b38104d63bb92c866d3eeaeaf"),
    # the review's fix round (Astra's cx36 on set 27's 8fbb68b6, B1 to B7): L4-E11's two new drafts; read from the tree
    "e11aux": ("v2/docs/records/l4e11/apply_gen_sch_e_aux.py", "16fe449358e0b009294158a133b3a2c18e774971bc27e516741b1cf884eee71a"),
    "e11dock": ("v2/docs/records/l4e11/apply_pcb_interfaces_dock.py", "d9a128c469cd7674530a107cd9708c208300cbcf9e4f3092f0d12f51929b038e"),
}
# Read from the tree when the tree's file is the pinned one, else from the named commit: L4-E7R's selected solution (fnd/l4e7,
# accepted, check 4 at 91e9a4b5), L4-E10's final record (fnd/l4e10, closing check 573c8b8f), L4-E11's (fnd/l4e11, accepted,
# closing check a15ab384) and L4-E12's (fnd/l4e12, accepted, closing check db41c95d)
COMMIT_LABEL = {"675b8068": "fnd/l4e7, accepted, closing check 91e9a4b5", "79b2f568": "fnd/l4e10, final, closing check 573c8b8f",
                "3298d1f1": "fnd/l4e11, accepted, closing check a15ab384", "a86be47b": "fnd/l4e12, accepted, closing check db41c95d",
                "e464ff88": "fnd/l4e10, dependency round, check 4", "c933724e": "fnd/l4e12, dependency round, check 4",
                "f1856bfd": "fnd/l4e11, dependency round, check 4", "5aa18a69": "fnd/l4e11, the charger selection, check 5",
                "7f41632d": "fnd/l4e12, the thermal verdict, check 5", "1c321773": "fnd/l4e10, the cell route, check 5",
                "589f18ac": "fnd/l4e12, the heat-rejection comparison, check 6", "6f8fd652": "fnd/l4e12, the thermal reconciliation, check 7",
                "e2d20bf2": "fnd/l4e10, the battery comparison, check 6", "573fd5b8": "fnd/l4e7, the solar-fault remedies, check 5",
                "656fc540": "fnd/l4e11, the review's fix round (B1, B2)", "b1cd32ba": "fnd/l4e12, the review's fix round (B3, B4, B7)",
                "ee09aa09": "fnd/l4e10, the review's fix round (B5)", "11339ec7": "fnd/l4e7, the review's fix round (B6)"}
FROM_COMMIT = {"l4e7r": "11339ec7", "l4e10": "ee09aa09", "l4e10md": "ee09aa09", "l4e11": "656fc540", "l4e11md": "656fc540",
               "e11entry": "3298d1f1", "l4e12": "b1cd32ba", "l4e12md": "b1cd32ba", "cl_topwell": "e464ff88", "cl_eaton": "79b2f568",
               "cl_pdi": "a86be47b", "cl_sensirion": "a86be47b", "cl_gc": "a86be47b", "cl_nicerf": "a86be47b", "cl_bulgin": "a86be47b",
               "cl_adi": "675b8068", "cl_milliohm": "675b8068", "cl_vishay": "675b8068", "cl_ti": "675b8068"}
FROM_LABEL = {k: COMMIT_LABEL[c] for k, c in FROM_COMMIT.items()}
FROM_L4E8 = {"l4e8"}       # read from L4E8_COMMIT when the path is not in the tree

# The few figures this record sets itself (each an input, named where it is used)
CU_RHO_20C = 0.01724      # ASSUMPTION: standard annealed copper, ohm mm2 / m at 20 C (a physical constant; no document held)
CU_ALPHA = 0.00393        # ASSUMPTION: copper's temperature coefficient, 1 / K (the constant r11dep's C-1 uses)
AWG18_MM2 = 0.823         # ASSUMPTION: the cross-section of an 18 AWG conductor, mm2 (the gauge's definition)
T_COLD = -20.0            # REQ-024's use boundary (D-02a), C: the cold copper gives the larger prospective current
BIAS_KEEP = 0.2           # ASSUMPTION: the fraction of a ceramic's nominal capacitance kept under DC bias (the review of
                          # decision 31's 'a fifth'); the pack-open bound states the fraction it actually needs
VF_BACKFEED = 0.0         # the body diode's drop on the back-feed path taken as zero: the larger DC_P, an upper bound
L2_TOL = 0.20             # Coilcraft XAL family inductance tolerance (+-20 %), as r11dep carries it for L1
# Read from the CSD19532Q5B sheet's figures by eye (INFERRED from the figure; SLPS414B p.6), named here as this record's inputs:
CSD_RDS_NORM_150C = 1.95   # Figure 8, normalized RDS(on) at TC 150 C, VGS 10 V (typical curve): the junction bound uses it
CSD_SOA_10MS_36V_A = 3.0   # Figure 10, the 10 ms single-pulse line at VDS 36 V, TC 25 C, RthetaJC 0.8 C/W max
SOA_TC_HOT = 100.0         # ASSUMPTION: Q7's case at most 100 C in the hot swap's fault; the line derated by (150 - TC) / 125
R23_NEW_K = 6.42           # SESSION: E192's 6.42k, the OVLO resolution (ii) for CS101 at a 36 V source, with R22 100k, both 0.1 %
R24_NEW_K = 22.0           # SESSION (fix round, B1): R24 22k 1 %, the power limit's sense voltage at least 5 mV at the OVLO maximum
R24_TOL = 0.01             # its tolerance (the draft's value text)
TI_SOA_MARGIN = 1.3        # SNVS452G 9.2.1.2.5: the FET to handle at least 1.3 times the hot-short's power (the maker's own margin)
PWRLIM_SPREAD = 31.0 / 25.0  # LM5069 PWRLIM-1 row 19 / 25 / 31 mV carried as the power limit's spread (INFERRED scaling)


_C_TEXT = {}     # the pinned text inputs of the last compute(), for part A's readers


def refuse(code, msg):
    sys.stderr.write("l4e9_power_path: %s; refusing\n" % msg)
    sys.exit(code)


def raw(key):
    rel, _ = PINS[key]
    p = os.path.join(TOP, rel)
    if key in FROM_COMMIT:
        if os.path.exists(p) and hashlib.sha256(open(p, "rb").read()).hexdigest() == PINS[key][1]:
            return open(p, "rb").read(), "tree"      # the selected solution's file already in the tree
        r = subprocess.run(["git", "show", "%s:%s" % (FROM_COMMIT[key], rel)], cwd=TOP, capture_output=True)
        if r.returncode != 0:
            refuse(3, "%s is not at %s" % (rel, FROM_COMMIT[key]))
        return r.stdout, "commit %s" % FROM_COMMIT[key]
    if os.path.exists(p):
        return open(p, "rb").read(), "tree"
    if key in FROM_L4E8:
        r = subprocess.run(["git", "show", "%s:%s" % (L4E8_COMMIT, rel)], cwd=TOP, capture_output=True)
        if r.returncode != 0:
            refuse(3, "%s is neither in the tree nor at %s" % (rel, L4E8_COMMIT[:12]))
        return r.stdout, "commit %s" % L4E8_COMMIT[:12]
    refuse(3, "%s is missing" % rel)


def load_inputs():
    B, where = {}, {}
    for key, (rel, want) in PINS.items():
        b, w = raw(key)
        h = hashlib.sha256(b).hexdigest()
        if want is not None and h != want:
            refuse(2, "%s is not the pinned file (%s)" % (rel, h[:16]))
        B[key], where[key] = b, (w, h)
    return B, where


def pdf_text(key, first=None, last=None):
    rel = PINS[key][0]
    cmd = ["pdftotext", "-layout"]
    if first:
        cmd += ["-f", str(first), "-l", str(last or first)]
    r = subprocess.run(cmd + [os.path.join(TOP, rel), "-"], capture_output=True)
    if r.returncode != 0:
        refuse(3, "pdftotext failed on %s" % rel)
    return r.stdout.decode("utf-8", "replace")


def need(text, pat, what, flags=re.M):
    m = re.search(pat, text, flags)
    if not m:
        refuse(3, "%s not found" % what)
    return m


def f(m, i=1):
    return float(m.group(i))


# ------------------------------------------------------------------------------------------ the generators' declarations
class Gen:
    """A generator read by its syntax tree: module-level constants, the _intent.rail() declarations (also those inside a
    for loop over constant tuples) and the part value texts (part, r, c, ic, nfet; and the part a helper function draws)."""
    FUNCS = {"part": 3, "r": 1, "c": 1, "ic": 2, "nfet": 1}

    def __init__(self, text):
        self.tree = ast.parse(text)
        self.env, self.rails, self.values, self.helpers = {}, {}, {}, {}
        self._walk(self.tree.body, {})

    def ev(self, n, env):
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.Name):
            if n.id in env:
                return env[n.id]
            if n.id in self.env:
                return self.env[n.id]
            raise ValueError(n.id)
        if isinstance(n, ast.Tuple):
            return tuple(self.ev(e, env) for e in n.elts)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -self.ev(n.operand, env)
        if isinstance(n, ast.BinOp):
            a, b = self.ev(n.left, env), self.ev(n.right, env)
            ops = {ast.Add: lambda: a + b, ast.Sub: lambda: a - b, ast.Mult: lambda: a * b, ast.Div: lambda: a / b,
                   ast.Mod: lambda: a % b}
            return ops[type(n.op)]()
        if isinstance(n, ast.IfExp):
            raise ValueError("ifexp")
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("round", "min", "max"):
            args = [self.ev(a, env) for a in n.args]
            return {"round": round, "min": min, "max": max}[n.func.id](*args)
        raise ValueError(type(n).__name__)

    def _call(self, call, env):
        fn = call.func
        if isinstance(fn, ast.Attribute) and fn.attr == "rail" and isinstance(fn.value, ast.Name) and fn.value.id == "_intent":
            try:
                name = self.ev(call.args[0], env)
            except (ValueError, KeyError, TypeError):
                return
            vals = []
            for a in call.args[1:4]:
                try:
                    vals.append(self.ev(a, env))
                except (ValueError, KeyError, TypeError):
                    vals.append(None)
            kw = {}
            for k in call.keywords:
                if k.arg in ("v_work", "v_max", "efficiency"):
                    try:
                        kw[k.arg] = self.ev(k.value, env)
                    except (ValueError, KeyError, TypeError):
                        kw[k.arg] = None
            self.rails.setdefault(name, {"volts": vals[0], "typ": vals[1], "peak": vals[2], **kw})
        elif call.args and isinstance(call.args[0], ast.Constant) and (
                (isinstance(fn, ast.Name) and fn.id in self.FUNCS) or (isinstance(fn, ast.Attribute) and fn.attr == "tvs")):
            i = self.FUNCS[fn.id] if isinstance(fn, ast.Name) else 1
            if len(call.args) > i and isinstance(call.args[i], ast.Constant):
                self.values.setdefault(call.args[0].value, call.args[i].value)

    def _walk(self, body, env):
        for st in body:
            if isinstance(st, ast.Assign) and not env:
                for tgt in st.targets:
                    try:
                        v = self.ev(st.value, env)
                    except (ValueError, KeyError, TypeError, ZeroDivisionError):
                        continue
                    if isinstance(tgt, ast.Name):
                        self.env[tgt.id] = v
                    elif isinstance(tgt, ast.Tuple) and isinstance(v, tuple) and len(v) == len(tgt.elts):
                        for t, x in zip(tgt.elts, v):
                            if isinstance(t, ast.Name):
                                self.env[t.id] = x
            elif isinstance(st, ast.FunctionDef):
                for n in ast.walk(st):
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "part" and len(n.args) > 3 \
                            and isinstance(n.args[0], ast.Name) and isinstance(n.args[3], ast.Constant):
                        self.helpers.setdefault(st.name, []).append((n.args[0].id, n.args[3].value))
            elif isinstance(st, ast.For) and isinstance(st.target, (ast.Name, ast.Tuple)):
                try:
                    seq = self.ev(st.iter, env)
                except (ValueError, KeyError, TypeError):
                    seq = None
                if seq is None:
                    continue
                for item in seq:
                    e2 = dict(env)
                    if isinstance(st.target, ast.Name):
                        e2[st.target.id] = item
                    else:
                        for t, x in zip(st.target.elts, item):
                            e2[t.id] = x
                    for n in st.body:
                        for c in ast.walk(n):
                            if isinstance(c, ast.Call):
                                self._call(c, e2)
            for n in ([st] if isinstance(st, (ast.Expr,)) else []):
                for c in ast.walk(n):
                    if isinstance(c, ast.Call):
                        self._call(c, env)

    def rail(self, name):
        if name not in self.rails:
            refuse(3, "rail %s not declared" % name)
        return self.rails[name]

    def value(self, ref):
        if ref not in self.values:
            refuse(3, "part %s not found" % ref)
        return self.values[ref]


def amps_in(text, what):
    m = re.search(r"(\d+(?:\.\d+)?)\s*A\b", text)
    if not m:
        refuse(3, "no current in %s's value '%s'" % (what, text))
    return float(m.group(1))


def volts_in(text, what):
    m = re.search(r"(\d+(?:\.\d+)?)\s*V\b", text)
    if not m:
        refuse(3, "no voltage in %s's value '%s'" % (what, text))
    return float(m.group(1))


def cap_uf(v):
    m = re.match(r"\s*(\d+(?:\.\d+)?)\s*([pnu])", v)
    if not m:
        return None
    return float(m.group(1)) * {"p": 1e-6, "n": 1e-3, "u": 1.0}[m.group(2)]


# ------------------------------------------------------------------------------------------------------- the checks
ORDER = {"MAKER": 0, "NETLIST": 0, "MODELED": 1, "INFERRED": 2, "CONDITIONAL": 3, "ASSUMPTION": 4, "PENDING": 5}


class Chk:
    """One comparison across an interface: a (what is asked) against b (what is available or rated), with the relation
    that must hold, the evidence class of its weakest figure and the scope: 'selected' (the selected architecture, the
    Layer 4 decisions applied) or 'drawn' (the committed netlist, shown where a defect is found and resolved)."""

    def __init__(self, what, a, rel, b, unit, cls, src, scope="selected", verdict=None):
        self.what, self.a, self.rel, self.b, self.unit, self.cls, self.src, self.scope = what, a, rel, b, unit, cls, src, scope
        if verdict is not None:
            self.met = verdict      # a verdict the source record states on figures with no numeric pair (D-11's forward drop)
        elif cls == "PENDING" or a is None or b is None:
            self.met = None
        else:
            self.met = {"<=": a <= b, "<": a < b, ">=": a >= b, ">": a > b}[rel]
        if cls not in ORDER:
            refuse(4, "unknown class %s" % cls)

    def line(self):
        if self.met is None:
            v = "PENDING" if self.cls == "PENDING" else "OPEN"
        else:
            v = "MEETS" if self.met else "NOT MET"
        ab = "%s %s %s %s" % (fmt(self.a), self.rel, fmt(self.b), self.unit) if self.met is not None and self.a is not None and self.b is not None else "(%s)" % self.unit
        tag = {"drawn": " [as drawn]", "alternative": " [the alternative: the LM5069 kept]"}.get(self.scope, "")
        return "%s: %s: %s; %s (%s)%s" % (v, self.what, ab, self.cls, self.src, tag)


def fmt(x):
    if isinstance(x, float):
        s = ("%.4f" % x).rstrip("0").rstrip(".")
        return s
    return str(x)


def row_status(r):
    sel = [c for c in r["checks"] if c.scope == "selected"]
    worst = max((ORDER[c.cls] for c in sel), default=0)
    cls = [k for k, v in ORDER.items() if v == worst][0] if worst else "MAKER"
    if worst == ORDER["NETLIST"]:
        cls = "MAKER/NETLIST"
    if any(c.met is None and c.cls == "PENDING" for c in sel):
        st = "PENDING"
    elif any(c.met is False for c in sel):
        st = "NOT MET"
    elif worst >= ORDER["CONDITIONAL"]:
        st = "CONDITIONAL"
    else:
        st = "MEETS"
    return cls, st


# --------------------------------------------------------------------------------------------------------- the compute
def compute():
    B, where = load_inputs()
    T = {k: B[k].decode("utf-8", "replace") for k in B if not PINS[k][0].endswith(".pdf")}
    _C_TEXT.clear()
    _C_TEXT.update(T)
    F = {}

    # ===================================================================================== 1: the makers' rows
    t = pdf_text("lm5176", 5)
    F["u2_vin_abs"] = f(need(t, r"VIN, EN/UVLO, VISNS, VOSNS, ISNS\(\+\), ISNS\(.\)\s+.0\.3\s+(\d+)", "LM5176 VIN absolute maximum"))
    t = pdf_text("lm74700", 5)
    F["ld_ca_abs"] = f(need(t, r"CATHODE to ANODE\s+.5\s+(\d+)", "LM74700-Q1 CATHODE to ANODE absolute"))
    F["ld_anode_abs"] = f(need(t, r"ANODE to GND\s+.65\s+(\d+)", "LM74700-Q1 ANODE absolute"))
    F["ld_ac_rec"] = f(need(t, r"ANODE to CATHODE\s+.(\d+)", "LM74700-Q1 ANODE to CATHODE recommended minimum"))
    t = pdf_text("csd19532", 1)
    F["csd19532_vds"] = f(need(t, r"Drain-to-Source Voltage\s+(\d+)", "CSD19532Q5B VDS"))
    t = pdf_text("bsc039", 1)
    F["bsc039_vds"] = f(need(t, r"VDS\s+(\d+)\s+V", "BSC039N06NS VDS"))
    t = pdf_text("smcj")
    for part in ("SMCJ18A", "SMCJ22A", "SMCJ28A", "SMCJ36A", "SMCJ40A"):
        m = need(t, r"%s\s+\S+\s+\S+\s+\S+\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+\d+\s+([\d.]+)\s+([\d.]+)" % part, part + " row")
        F[part] = {"vr": f(m, 1), "vbr_min": f(m, 2), "vbr_max": f(m, 3), "vc": f(m, 4), "ipp": f(m, 5)}
    t = pdf_text("tps2596")
    F["tps2596_abs"] = f(need(t, r"Maximum Input Voltage Range\s+.0\.3\s+(\d+)\s+V", "TPS2596 VIN absolute"))
    t = pdf_text("lm5069")
    F["lm5069_vin_abs"] = f(need(t, r"VIN to GND \(3\)\s+.0\.3\s+(\d+)", "LM5069 VIN absolute"))
    m = need(t, r"VCL\s+Threshold voltage\s+VIN-SENSE voltage\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+mV", "LM5069 VCL")
    F["vcl"] = (f(m, 1), f(m, 2), f(m, 3))
    t = pdf_text("ina226")
    F["ina_abs"] = f(need(t, r"VVBUS\s+.0\.3\s+(\d+)\s+V", "INA226 VBUS absolute"))
    F["ina_cm_op"] = f(need(t, r"0 V . VIN\+ . (\d+) V", "INA226 CMRR common-mode condition"))
    F["ina_fs_mv"] = f(need(t, r"Full-scale range = ([\d.]+)mV", "INA226 shunt full scale"))
    t = pdf_text("bq25731", 8)
    F["u3_abs"] = f(need(t, r"SRN, SRP, ACN, ACP, VBUS, VSYS\s+.0\.3\s+(\d+)", "BQ25731 VBUS and VSYS absolute"))
    t = pdf_text("bq25731", 14)
    m = need(t, r"VSYSOVP_RISE\s+rising threshold to\s+\S+\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "BQ25731 SYSOVP")
    F["sysovp"] = (f(m, 1), f(m, 2), f(m, 3))
    t = pdf_text("fuse297")
    F["f297_v"] = f(need(t, r"Voltage Rating:\s+(\d+)\s*VDC", "297 voltage rating"))
    F["f297_i"] = f(need(t, r"Interrupting Rating:[\s\x07]+(\d+)A @", "297 interrupting rating"))
    t = pdf_text("vh", 1)
    F["vh_16"] = f(need(t, r"Current rating:\s+(\d+) A", "VH rating"))
    need(t, r"AWG #16 with the standard type header", "VH AWG 16 condition")
    F["vh_18"] = f(need(t, r"^\s+(\d+)A\s+AC/DC", "VH AWG 18 shrouded rating"))
    need(t, r"AWG #18 with the shrouded type header", "VH AWG 18 condition")
    t = subprocess.run(["pdftotext", os.path.join(TOP, PINS["millmax"][0]), "-"], capture_output=True).stdout.decode()
    F["millmax_a"] = f(need(t, r"carrying (\d+) amps continuous current", "Mill-Max continuous current"))
    t = pdf_text("xt60")
    F["xt60_a"] = f(need(t, r"额定电流\s+(\d+)A", "XT60 rated current"))

    # ===================================================================================== 2: the generators
    gA, gE, gP = Gen(T["gen_a"]), Gen(T["gen_e"]), Gen(T["gen_p"])
    F["vbat"] = gA.rail("VBAT")
    F["vin_raw_a"] = gA.rail("VIN_RAW")
    F["vbus20"] = gA.rail("VBUS20")
    F["pa"] = gA.rail("+13V8_PA")
    F["hf"] = gA.rail("+12V_HF")
    F["poe"] = gA.rail("+54V_POE")
    F["pd"] = gA.rail("PD_VBUS")
    F["vmon"] = gA.rail("VMON")
    F["vheat"] = gA.rail("VHEAT")
    F["s2"] = gA.rail("+5V_S2")
    F["dev"] = gA.rail("+5V_DEV")
    F["a_f1"] = amps_in(gA.value("F1"), "A F1")
    F["a_d1"] = gA.value("D1")
    F["a_d2"] = gA.value("D2")
    F["vin_raw_e"] = gE.rail("VIN_RAW")
    F["pv"] = gE.rail("PV_P")
    F["trk"] = gE.rail("TRK_OUT")
    F["cell_f"] = gE.rail("CELL_F")
    F["veh_t"] = gE.env["_VEH_T"]
    F["e_f1"] = gE.value("F1")
    F["e_f2"] = gE.value("F2")
    F["e_d10"], F["e_d1"], F["e_d2"], F["e_d4"] = gE.value("D10"), gE.value("D1"), gE.value("D2"), gE.value("D4")
    F["e_q7"] = gE.value("Q7")
    F["e_r19"] = gE.value("R19")
    F["e_r21"], F["e_r23"] = gE.value("R21"), gE.value("R23")
    F["e_r10"] = gE.value("R10")
    F["e_jdcin"], F["e_jsolar"] = gE.value("J_DCIN"), gE.value("J_SOLAR")
    F["e_l2"] = gE.value("L2")
    idl = dict(gE.helpers.get("ideal_diode", []))
    if "qref" not in idl:
        refuse(3, "board E's ideal_diode helper draws no FET")
    F["e_q1"] = idl["qref"]
    F["p_pack"] = gP.rail("PACK_P")
    F["p_f1"], F["p_f2"] = gP.value("F1"), gP.value("F2")
    for k in ("e_q1", "e_q7"):
        if not re.search(r"\b(\d+) V\b", F[k]):
            refuse(3, "%s's value states no voltage" % k)
    F["e_q1_v"] = volts_in(F["e_q1"], "E Q1")
    F["e_q7_v"] = volts_in(F["e_q7"], "E Q7")
    if "BSC039N06NS" not in F["e_q1"] or "CSD19532Q5B" not in F["e_q7"]:
        refuse(3, "board E's Q1 and Q7 are not the parts the makers' rows were read for")

    # board A's netlist: VBAT's capacitors and U17's sense nets
    na = T["net_a"]
    m = need(na, r'\(net \(code "\d+"\) \(name "/?VBAT"\)', "VBAT net")
    blk = na[m.start(): na.find("(net (code", m.start() + 5)]
    caps = sorted(set(r for r, _ in re.findall(r'\(node \(ref "(C\d+)"\) \(pin "(\d+)"\)', blk)), key=lambda s: int(s[1:]))
    tot = 0.0
    for c in caps:
        mv = need(na, r'\(comp \(ref "%s"\)\s*\(value "([^"]+)"\)' % c, c + " value")
        u = cap_uf(mv.group(1))
        tot += u or 0.0
    F["vbat_caps"] = (len(caps), tot)
    F["vbat_d1_on_net"] = '(ref "D1")' in blk
    u17 = {}
    for net in ("POE_OUT", "+54V_POE"):
        mm = re.search(r'\(net \(code "\d+"\) \(name "/?%s"\)' % re.escape(net), na)
        if not mm:
            refuse(3, "net %s" % net)
        b2 = na[mm.start(): na.find("(net (code", mm.start() + 5)]
        u17[net] = re.findall(r'\(node \(ref "U17"\) \(pin "(\d+)"\)', b2)
    F["u17_nets"] = u17

    # ===================================================================================== 3: the records' figures
    t = T["l4e4"]
    m = need(t, r"declared\s+0\.93 x 0\.93: ([\d.]+) W, at least ([\d.]+) A: setting ([\d.]+) A \(minimum ([\d.]+) A, maximum ([\d.]+) A, through R11 ([\d.]+) A\)", "L4-E4 setting line")
    F["win_w"], F["win_need"], F["iin_host"], F["u3_min"], F["u3_max_board"], F["r11_need"] = (f(m, i) for i in range(1, 7))
    F["u3_max_u3"] = f(need(t, r"U3's own maximum ([\d.]+) A", "U3's own maximum"))
    m = need(t, r"HoJLR2512-3W-8mR-1%\s+C2904240 stock\s+\d+: band ([\d.]+) / ([\d.]+) / ([\d.]+) A", "8 mOhm band")
    F["r11_8"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(t, r"HoJLR2512-3W-7mR-1%\s+C2904239 stock\s+\d+: band ([\d.]+) / ([\d.]+) / ([\d.]+) A", "7 mOhm band")
    F["r11_7"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(t, r"^\s+62\.1 C\s+[\d.]+\.\.[\d.]+\s+([\d.]+) A, margin \+([\d.]+) A\s+([\d.]+) A, margin \+([\d.]+) A\s+([\d.]+) A, margin \+([\d.]+) A", "62.1 C margins")
    F["r11_min_62_alone"], F["r11_min_62_full"], F["r11_margin_62_full"] = f(m, 1), f(m, 5), f(m, 6)
    m = need(t, r"TRIP WINDOW at 5 mOhm: ([\d.]+) to ([\d.]+) A", "R138 trip window")
    F["trip"] = (f(m, 1), f(m, 2))
    F["recept_a"] = f(need(t, r"Bulgin PXP4043/C \(CASE-MARGINS.md\): (\d+) A", "receptacle rating"))
    F["q27_a"] = f(need(t, r"Q27 CSD18510Q5B .*?: (\d+) A continuous", "Q27 rating"))
    m = need(t, r"the stage ahead \(U19, R81 10 mOhm.*?: ([\d.]+) / ([\d.]+) / ([\d.]+) A", "U19 limit")
    F["u19_lim"] = (f(m, 1), f(m, 2), f(m, 3))
    F["pdo_a"] = f(need(t, r"Largest PDO current ([\d.]+) A", "PDO current"))

    t = T["l4e5"]
    h3 = {}
    for v in ("9.0", "12.0", "24.0", "36.0"):
        m = need(t, r"^\s+%s V \|.*\| ([\d.]+) A \| ([\d.]+) A \(\s*([\d.]+) %%\)\s*$" % re.escape(v), "H3 row %s V" % v)
        h3[float(v)] = (f(m, 1), f(m, 2), f(m, 3))
    F["h3"] = h3
    m = need(t, r"certainly in HIZ below ([\d.]+) V of VIN_RAW", "HIZ certain")
    F["hiz_below"] = f(m)
    F["hiz_out_above"] = f(need(t, r"out of HIZ \(with EN_HIZ = 0,\s+REG0x35 bit 7, reset 0b, p\.64; p\.27\) above ([\d.]+) V", "HIZ out"))
    F["pin_reg_from"] = f(need(t, r"VIN_RAW ([\d.]+) V at the band's top", "regulation from"))
    F["u3_at_9"] = f(need(t, r"At the 9 V floor U3 still gets at least ([\d.]+) A", "U3 at 9 V"))
    m = need(t, r"so E96 232 k: ceiling ([\d.]+) / ([\d.]+) / ([\d.]+) V", "raised ceiling")
    F["trk_ceiling"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(t, r"as drawn\s+([\d.]+) / ([\d.]+) / ([\d.]+) V: FBOUT", "drawn ceiling")
    F["trk_drawn"] = (f(m, 1), f(m, 2), f(m, 3))
    F["c26_pct"] = f(need(t, r"C26 10u 25V at (\d+) % of its 25 V", "C26 stress"))
    F["c24_pct"] = f(need(t, r"C24 39u 35V Panasonic 35SVPF39M polymer at (\d+) % of its 35 V", "C24 stress"))
    m = need(t, r"UV falling ([\d.]+) / ([\d.]+) / ([\d.]+) V", "restart guard")
    F["latch"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(t, r"LM5069 limits at ([\d.]+) to ([\d.]+) A \(([\d.]+) A with R19's 1 %\)", "entry limit")
    F["entry_lim"], F["entry_basis"] = (f(m, 1), f(m, 2)), f(m, 3)
    m = need(t, r"fault timeout of ([\d.]+) / ([\d.]+) / ([\d.]+) ms", "fault timer")
    F["timer_ms"] = (f(m, 1), f(m, 2), f(m, 3))
    F["vin_uf"] = f(need(t, r"VIN_RAW and TRK_OUT hold ([\d.]+) uF nominal", "VIN_RAW capacitance"))
    m = need(t, r"86\.5 W at VBUS20: VIN_RAW ([\d.]+) V nominal \(([\d.]+) V to ([\d.]+) V\)", "solar settle")
    F["settle_865"] = (f(m, 1), f(m, 2), f(m, 3))
    F["eff_floor_9v"] = f(need(t, r"it reaches 4\.80 A only if the front end's efficiency at 9 V falls to ([\d.]+)", "9 V efficiency floor"))
    m = need(t, r"at most ([\d.]+) A in\s+board current, ([\d.]+) A through R11", "pin path")
    F["pin_path"] = f(m, 2)
    F["pin_err_allow"] = f(need(t, r"pin's error at 10 mOhm is at most ([\d.]+) A in that band", "V-A07 allowance"))
    ms = list(re.finditer(r"H3\s+taken\s+([\d.]+) to\s+([\d.]+) Wh a day, given up\s+([\d.]+) to\s+([\d.]+) Wh; A2 unserved ([\d.]+) to ([\d.]+) Wh \(48 h\), ([\d.]+) to ([\d.]+) Wh \(72 h\)", t))
    if len(ms) != 2:
        refuse(3, "H3's two energy rows")
    F["h3_cand_given"] = (f(ms[1], 3), f(ms[1], 4))
    F["h3_cand_a2"] = (f(ms[1], 5), f(ms[1], 6), f(ms[1], 7), f(ms[1], 8))
    F["fwa16"] = tuple(float(x) for x in need(t, r"its own figures ([\d.]+) / ([\d.]+) / ([\d.]+) A at 9 / 12 / 24 V", "FW-A16 figures").groups())

    t = T["l4e6"]
    m = need(t, r"HoJLR2512-3W-12mR-1%\s+C2904242: peak ([\d.]+) / ([\d.]+) / ([\d.]+) A, valley ([\d.]+) / ([\d.]+) / ([\d.]+) A; service \+([\d.]+)", "R12 row")
    F["r12_peak"], F["r12_valley"], F["r12_service"] = (f(m, 1), f(m, 2), f(m, 3)), (f(m, 4), f(m, 5), f(m, 6)), f(m, 7)
    F["svc_peak"] = f(need(t, r"H3's highest boost peak ([\d.]+) A", "service peak"))
    sec = t[t.find("R11 8 mOhm, 7.262 A:\n      9.0 V"):]
    m = need(sec, r"9\.0 V \(boost, set by the cycle-by-cycle limit\): L1 ([\d.]+) A average.*?output ([\d.]+) A", "9 V closure", re.S)
    F["fe_in_9v"], F["fe_out_9v"] = f(m, 1), f(m, 2)
    m = need(sec, r"15\.1 V \(boost, set by the average limit\): L1 ([\d.]+) A average", "15.1 V closure")
    F["fe_in_151"] = f(m)
    m = need(sec, r"B-1: the peak bound over 9 to 36 V ([\d.]+) A \(at ([\d.]+) V\), ([\d.]+) % of the typical ([\d.]+) A", "B-1")
    F["l1_peak"], F["l1_pct"], F["l1_isat"] = f(m, 1), f(m, 3), f(m, 4)
    F["l1_need"] = f(need(sec, r"Isat there is at least [\d.]+ % of its 25 C value, ([\d.]+) A", "C-5 need"))
    F["l1_qual"] = f(need(sec, r"the qualifying temperature is (\d+) C", "qualifying temperature"))
    F["fet_tj"] = f(need(sec, r"B-2: every FET at most (\d+) C: MET on the ASSUMED RthetaJA", "B-2"))
    F["avg_from"] = f(need(sec, r"above ([\d.]+) V the average limit, not the peak limit, sets the fault current", "average limit onset"))
    F["vbus_max_r11"] = f(need(t, r"VBUS20 at ([\d.]+) V, efficiency ([\d.]+) DECLARED", "r11_dep bus"))
    F["eta_fe"] = f(need(t, r"VBUS20 at [\d.]+ V, efficiency ([\d.]+) DECLARED", "front end efficiency"))

    t = T["l4e7r"]      # L4-E7R's selected solution, (C) at R66 8.25k and RIMON_IN 30k
    m = need(t, r"the selected solution is \(C\) at R66 ([\d.]+k) and RIMON_IN ([\d.]+k)", "L4-E7R's selected solution")
    F["r66"], F["rimon"] = m.group(1), m.group(2)
    m = need(t, r"regulation at RIMON_IN [\d.]+k, ([\d.]+) A nominal and ([\d.]+) A at its highest on\s+the hold's corners \(([\d.]+) W at the nominal hold, ([\d.]+) W at most there\)", "L4-E7R's regulation")
    F["reg"], F["reg_w"] = (f(m, 1), f(m, 2)), (f(m, 3), f(m, 4))
    m = need(t, r"the backstop's static bound, ([\d.]+) W \(CONDITIONAL on G_CM and the VIN\+ bias, break-\s*evens\s+above\), with the regulation's own 25 V corner at ([\d.]+) W", "the static bound")
    F["static_bound"], F["reg_corner"] = f(m, 1), f(m, 2)
    F["isc_hot_tol"] = f(need(t, r"is\s+([\d.]+) A with the sheet's power tolerance \(still under J_SOLAR's nearest stated [\d.]+ A\)", "the hot short circuit with tolerance"))
    m = need(t, r"the filtered peak is at most ([\d.]+) A at (\d+) Hz \(S1\) against the margin\s+([\d.]+) A, at the filter's least time constant \(([\d.]+) ms", "the CS101 ripple and margin")
    F["m2_ripple"], F["m2_hz"], F["m2_margin"], F["tau_min_ms"] = f(m, 1), int(m.group(2)), f(m, 3), f(m, 4)
    m = need(t, r"(\d) x 100 nF, the loop branch ([\d.]+) times, the response ([\d.]+) times \(chosen\)", "the filter's selection")
    F["filt_n"], F["loop_breakeven"] = int(m.group(1)), f(m, 2)
    m = need(t, r"times its largest time constant \(([\d.]+) ms\) at 25 V, is ([\d.]+) J", "the filter's held charge")
    F["tau_max_ms"], F["held_j"] = f(m, 1), f(m, 2)
    F["bulk_ripple_x"] = f(need(t, r"a can carries up to ([\d.]+) times its ripple rating", "the bulk's ripple under CS101"))
    m = need(t, r"CONDITIONAL on G_CM \(break-even (\d+) %\) and the VIN\+ bias \((\d+)\s+mA\)", "the two assumptions' break-evens")
    F["gcm_be"], F["vinb_be"] = f(m, 1), f(m, 2)
    need(t, r"M2 \(the laboratory validation of CS101, downstream", "M2's procedure")
    m = need(t, r"against ([\d.]+) to ([\d.]+) A at 25 V, at commissioning", "the backstop's trip window")
    F["bs_trip"] = (f(m, 1), f(m, 2))
    F["bs_allow_ms"] = f(need(t, r"at most 10 J in any 0\.1 s for a response up to ([\d.]+) ms", "the dynamic allowance"))
    F["swen_v"] = f(need(t, r"Below ([\d.]+) V on\s+TRK_LDO33 SWEN cannot reach", "SWEN off by default"))
    F["u5_diff"] = f(need(t, r"U5's sense differential, the rating that bounded the second round: at most ([\d.]+) V", "U5's differential"))
    F["u5_diff_lim"] = f(need(t, r"CS114, against ([\d.]+) V \(8705af p\.2\)", "U5's differential limit"))
    m = need(t, r"THE ENERGY: on SC-37's day ([\d.]+) / ([\d.]+) / ([\d.]+) Wh at the lower, nominal and upper hold corners", "L4-E7R's energy")
    F["e7r_day"] = (f(m, 1), f(m, 2), f(m, 3))
    F["e7r_bright"] = f(need(t, r"on the\s+bright day ([\d.]+) Wh \(\d+ h bound\)", "the bright day"))
    m = need(t, r"costs ([\d.]+) Wh on SC-37's day and\s+([\d.]+) Wh on the bright day", "the bank's conduction")
    F["bank_wh"] = (f(m, 1), f(m, 2))
    F["cs101_pv"] = f(need(t, r"under CS101 the input reaches ([\d.]+) V at most", "CS101 at the panel input"))
    F["trk_vs_max"] = f(need(t, r"TRK_VS ([\d.]+) V against the ceramics' 50 V", "TRK_VS at its worst"))
    m = need(t, r"PV_P ([\d.]+) V against the bulk's 50 V \(on PV_P\) and U18's VIN\+ and V\+ (\d+) V", "PV_P at its worst")
    F["pv_p_max"], F["u18_vin"] = f(m, 1), f(m, 2)
    F["backstop_edits"] = int(need(t, r"apply_gen_sch_e_backstop\.py, (\d+) edit\(s\)", "the backstop draft").group(1))
    m = need(t, r"EA3 at its typical 90 V/V:\s+([\d.]+) / ([\d.]+) / ([\d.]+) V", "hold band")
    F["hold"] = (f(m, 1), f(m, 2), f(m, 3))
    m = re.search(r"(16\.41\d+) .*?(18\.81\d+)", t)
    if not m:
        refuse(3, "the conditioned hold envelope")
    F["hold_cond"] = (f(m, 1), f(m, 2))
    F["u5_tj"] = f(need(t, r"TJ estimated about ([\d.]+) C \(INFERRED\)", "U5 junction"))
    m = need(t, r"NEW nominal \(hold 17\.593 V, limit 3\.471 A\), A1: ([\d.]+) Wh a day; first interruption h (\d+)/(\d+); unserved ([\d.]+) / ([\d.]+) at 48 h, ([\d.]+) / ([\d.]+) at 72 h; least addition \+([\d.]+) / \+([\d.]+) Wh", "A1 nominal")
    F["a1_cand"] = tuple(f(m, i) for i in range(1, 10))
    m = need(t, r"NEW nominal \(hold 17\.593 V, limit 3\.471 A\), A2: ([\d.]+) Wh a day; first interruption h (\d+)/(\d+); unserved ([\d.]+) / ([\d.]+) at 48 h, ([\d.]+) / ([\d.]+) at 72 h; least addition \+([\d.]+) / \+([\d.]+) Wh", "A2 nominal")
    F["a2_cand"] = tuple(f(m, i) for i in range(1, 10))

    t = T["l4e8"]
    m = need(t, r"R11 8 mOhm, 7\.262 A: every can at most ([\d.]+) A against ([\d.]+) A \(meets\)", "bank 8 mOhm")
    F["can8"] = (f(m, 1), f(m, 2))
    m = need(t, r"R11 7 mOhm, 8\.300 A: every can at most ([\d.]+) A against ([\d.]+) A \(meets\)", "bank 7 mOhm")
    F["can7"] = (f(m, 1), f(m, 2))
    need(t, r"CHOSEN: six EEHZK1V331P as drawn, each in series with a 45 mOhm 1 % 2512 ballast, Milliohm HoJLR2512-3W-45mR-1%, LCSC C2903491", "ballast")
    F["ballast_w"] = f(need(t, r"Upper\s+sum at the bound's worst corner ([\d.]+) W", "ballast energy term"))
    F["ballast_nom_w"] = f(need(t, r"fch 400 kHz: ([\d.]+) W\s+\(not a measurement\)\. Not to be counted twice once a measured converter efficiency includes it", "the ballast at nominal parts"))
    need(t, r"CHOSEN: Cc2 3\.3n \(C1613", "Cc2")

    t = T["replay"]
    m = need(t, r"A1 D-06's 4S3P: usable ([\d.]+) Wh at \+20 C, ([\d.]+) Wh at -10 C: ([\d.]+) h and ([\d.]+) h", "A1 battery-only")
    F["a1_bat"] = tuple(f(m, i) for i in range(1, 5))
    m = need(t, r"A2 base 4S6P \+ lid 4S9P: usable ([\d.]+) Wh at \+20 C, ([\d.]+) Wh at -10 C: ([\d.]+) h and ([\d.]+) h", "A2 battery-only")
    F["a2_bat"] = tuple(f(m, i) for i in range(1, 5))
    m = need(t, r"against 48 h: A1 short by ([\d.]+) h .*?, A2 short by ([\d.]+) h .*?; against 72 h: A1 ([\d.]+) h .*?,\n\s+A2 ([\d.]+) h", "shortfalls", re.S)
    F["short"] = tuple(f(m, i) for i in range(1, 5))
    m = need(t, r"A1   CORRECTED, HYPOTHETICAL, WE\s+48 h TYP: pack \S+;\s+\+([\d.]+) Wh", "A1 screening 48 h")
    m2 = need(t, r"A1   CORRECTED, HYPOTHETICAL, WE\s+72 h TYP: pack \S+;\s+\+([\d.]+) Wh", "A1 screening 72 h")
    F["a1_scr_add"] = (f(m), f(m2))
    m = need(t, r"A2   CORRECTED, HYPOTHETICAL, WE\s+48 h TYP: lid \S+;\s+\+([\d.]+) Wh", "A2 screening 48 h")
    m2 = need(t, r"A2   CORRECTED, HYPOTHETICAL, WE\s+72 h TYP: lid \S+;\s+\+([\d.]+) Wh", "A2 screening 72 h")
    F["a2_scr_add"] = (f(m), f(m2))
    blk = t[t.find("A1 D-06's 4S3P             CORRECTED, HYPOTHETICAL, WE"):]
    m = need(blk, r"TYP from 06 UTC: first interruption h\s+(\d+) \((\d+) UTC\); unserved\s+([\d.]+) Wh at 48 h,\s+([\d.]+) Wh at 72 h", "A1 screening 06")
    m2 = need(blk, r"TYP from 18 UTC: first interruption h\s+(\d+) \((\d+) UTC\); unserved\s+([\d.]+) Wh at 48 h,\s+([\d.]+) Wh at 72 h", "A1 screening 18")
    F["a1_scr"] = (f(m, 1), f(m2, 1), f(m, 3), f(m2, 3), f(m, 4), f(m2, 4))
    blk = t[t.find("A2 base 4S6P + lid 4S9P    CORRECTED, HYPOTHETICAL, WE"):]
    m = need(blk, r"TYP from 06 UTC: first interruption h\s+(\d+) \((\d+) UTC\); unserved\s+([\d.]+) Wh at 48 h,\s+([\d.]+) Wh at 72 h", "A2 screening 06")
    m2 = need(blk, r"TYP from 18 UTC: first interruption h\s+(\d+) \((\d+) UTC\); unserved\s+([\d.]+) Wh at 48 h,\s+([\d.]+) Wh at 72 h", "A2 screening 18")
    F["a2_scr"] = (f(m, 1), f(m2, 1), f(m, 3), f(m2, 3), f(m, 4), f(m2, 4))
    m = need(t, r"CORRECTED, O-2 nominal\s+A2 48 h ([\d.]+) W, 72 h ([\d.]+) W; A1 48 h ([\d.]+) W, 72 h ([\d.]+) W", "steady loads")
    F["steady"] = tuple(f(m, i) for i in range(1, 5))
    F["bus_low"] = f(need(t, r"CORRECTED  HYPOTHETICAL, ENERGY-BASIS 6c's WE: bus ([\d.]+) V", "lowest bus"))
    F["eta_u3"] = f(need(t, r"U3's limit [\d.]+ A, U3 ([\d.]+),", "U3 efficiency"))
    F["cand_voc_cold"] = f(need(t, r"the NOMINAL open circuit is ([\d.]+) V there", "candidate cold Voc"))
    F["cand_isc_hot"] = f(need(t, r"its hot short-circuit current about ([\d.]+) A", "candidate hot Isc"))
    F["cand_day"] = f(need(t, r"nominal hold\s+17\.593 V, limit nominal\s+([\d.]+) Wh", "candidate day"))

    t = T["l4e10"]      # L4-E10's final record (FEA-008 not closed; the recommendation and the conditioned corner)
    need(t, r"Closable now: none\.", "FEA-008 not closed")
    need(t, r"route CONDITIONAL: \(II\) RECOMMENDED: a wide-temperature 18650 \(the HL18650V class\)", "L4-E10's recommendation")
    F["th1"] = f(need(t, r"T-H1 must read at least ([\d.]+) W/K with the fans, lid closed AND lid open", "T-H1's floor"))
    m = need(t, r"at this corner the uncooled air settles at ([\d.]+) C in E3-O and tends to ([\d.]+) C in E5's 60 C dwell, at or past the \+(\d+) C", "the conditioned corner")
    F["corner_air"], F["parts_hot"] = (f(m, 1), f(m, 2)), f(m, 3)
    F["e3o_amb"] = f(need(t, r"ambient \+(\d+) C; duration 4 h; configuration deployed, monitor and radios on", "E3-O's ambient"))
    m = need(t, r"35E\s+([\d.]+) Wh usable, ([\d.]+) h battery-only", "the 35E's usable energy")
    m2 = need(t, r"HL18650V\s+([\d.]+) Wh usable, ([\d.]+) h battery-only \((-[\d.]+) % against S1\)", "the HL18650V's usable energy")
    F["cell_usable"], F["cell_hours"], F["cell_less_pct"] = (f(m, 1), f(m2, 1)), (f(m, 2), f(m2, 2)), -f(m2, 3)
    m = need(t, r"([\d.]+) Wh nominal against ([\d.]+)", "the nominal energy")
    F["cell_nom"] = (f(m, 2), f(m, 1))
    F["corner_heat"] = (F["corner_air"][0] - F["e3o_amb"]) * F["th1"]
    m = need(t, r"LO-01e ([\d.]+) C: ([\d.]+), ([\d.]+) and ([\d.]+) K;", "LO-01e's margins")
    F["lo01e"] = (f(m, 1), f(m, 2), f(m, 3), f(m, 4))
    F["cell_usd"] = f(need(t, r"USD ([\d.]+) \(a marketplace seller, not the maker", "the cell's price"))

    t = T["l4e11"]      # L4-E11's accepted record: the selected vehicle entry, D-06's interconnect, U-04's arrangement
    m = need(t, r"UVLO: on at ([\d.]+) / ([\d.]+) / ([\d.]+) V, off at ([\d.]+) / ([\d.]+) / ([\d.]+) V of DC_P; OV: off above ([\d.]+) / ([\d.]+) / ([\d.]+) V, on again under ([\d.]+) / ([\d.]+) / ([\d.]+) V", "the selected entry's UVLO and OV")
    F["e_uv_on"], F["e_uv_off"] = tuple(f(m, i) for i in (1, 2, 3)), tuple(f(m, i) for i in (4, 5, 6))
    F["e_ov_off"], F["e_ov_on"] = tuple(f(m, i) for i in (7, 8, 9)), tuple(f(m, i) for i in (10, 11, 12))
    m = need(t, r"overcurrent ([\d.]+) / ([\d.]+) / ([\d.]+) A \(the printed row.*?; short circuit ([\d.]+) / ([\d.]+) / ([\d.]+) A;", "the breaker's thresholds")
    F["e_oc"], F["e_sc"] = tuple(f(m, i) for i in (1, 2, 3)), tuple(f(m, i) for i in (4, 5, 6))
    m = need(t, r"the delay is taken as ([\d.]+) ms at least \(Equation 7's, the row's excess over it not counted\), ([\d.]+) ms typical \(the row\) and ([\d.]+) ms at most \(Equation 7's\s+maximum scaled by the row's ([\d.]+) over Equation 7\), retry ([\d.]+) s", "the breaker's delay")
    F["e_oc_ms"], F["e_retry_s"] = (f(m, 1), f(m, 2), f(m, 3)), f(m, 5)
    m = need(t, r"a first-order filter of ([\d.]+) / ([\d.]+) / ([\d.]+) us .*?then PD within (\d+) / (\d+) us", "the short-circuit filter", re.S)
    F["e_tau_us"], F["e_tsc_us"] = (f(m, 1), f(m, 2), f(m, 3)), (f(m, 4), f(m, 5))
    m = need(t, r"the start: slew ([\d.]+) / ([\d.]+) / ([\d.]+) V/ms \(.*?\); inrush ([\d.]+) to ([\d.]+) A into ([\d.]+) to ([\d.]+) uF; at most ([\d.]+) ms to ([\d.]+) V", "the start")
    F["e_slew"], F["e_inrush"], F["e_start_c"] = (f(m, 1), f(m, 2), f(m, 3)), (f(m, 4), f(m, 5)), (f(m, 6), f(m, 7))
    F["e_start_ms"], F["e_basis_v"] = f(m, 8), f(m, 9)
    m = need(t, r"at the clamps' ([\d.]+) V the pins see INP ([\d.]+) V, EN/UVLO ([\d.]+) V, OV ([\d.]+) V, under (\d+) V", "the pins at the clamp")
    F["e_pins"] = tuple(f(m, i) for i in range(1, 6))
    m = need(t, r"TPS4811-Q1 \(SLUSEE5E, held back\): VS 3\.5 to (\d+) V, (\d+) V absolute", "the TPS4811's VS")
    F["e_vs"] = (f(m, 1), f(m, 2))
    m = need(t, r"CSD19536KTT Figure 4-10 .*?at ([\d.]+) V 100 us ([\d.]+) A, 1 ms ([\d.]+) A, 10 ms ([\d.]+) A \(MAKER\);\s+derated by L4-E9's ([\d.]+) .*?this part's TJ is (\d+) C", "Q7's chart", re.S)
    F["e_q7_chart"], F["e_derate"], F["e_q7_tj"] = (f(m, 1), f(m, 2), f(m, 3), f(m, 4)), f(m, 5), f(m, 6)
    m = need(t, r"Rf ([\d.]+) to (\d+) Ohm on VIN_RAW", "the fault scan's range")
    F["e_rf_range"] = (f(m, 1), f(m, 2))
    m = need(t, r"CSD19536KTT \(selected\)\s+worst ([\d.]+) of the derated chart at Rf ([\d.]+) Ohm, ([\d.]+) ms, ended by the short-circuit trip .*?; the start itself ([\d.]+): MEETS", "the selected FET's resistive fault start")
    F["e_rf"] = tuple(f(m, i) for i in range(1, 5))
    m = need(t, r"CSD19532Q5B \(as drawn\)\s+worst ([\d.]+) of the derated chart at Rf ([\d.]+) Ohm, ([\d.]+) ms", "the drawn FET's resistive fault start")
    F["e_rf_drawn"] = tuple(f(m, i) for i in range(1, 4))
    m = need(t, r"at most ([\d.]+) A/us \(gfs (\d+) S.*?a peak of ([\d.]+) A after ([\d.]+) us, ([\d.]+) of the derated 100 us line", "the start into a hard short", re.S)
    F["e_hs_start"] = tuple(f(m, i) for i in range(1, 6))
    m = need(t, r"add at most tau \+ tSC = ([\d.]+) us.*?Q7's IDM (\d+) A derated by ([\d.]+) gives ([\d.]+) A; at the entry's highest on-voltage\s+\(the OV rise's ([\d.]+) V\) that holds for a loop inductance of ([\d.]+) uH or more", "the hard short in service", re.S)
    F["e_hs_svc"] = {"t_us": f(m, 1), "idm": f(m, 2), "der": f(m, 3), "lim": f(m, 4), "v": f(m, 5), "l_uh": f(m, 6)}
    m = need(t, r"the plug to DC_P ([\d.]+) mOhm, DC_P to VIN_RAW ([\d.]+) mOhm, ([\d.]+) mOhm in all", "the kit's series resistance")
    F["e_loop_mohm"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(t, r"VIN_RAW ([\d.]+) V, ([\d.]+) A from the plug, DC_P ([\d.]+) V; against the selected entry", "the in-service maximum")
    F["e_svc"] = (f(m, 1), f(m, 2), f(m, 3))
    F["e_dcp_noload"] = f(need(t, r"against DC_P at ([\d.]+) V or more before any current flows", "DC_P before any current"))
    F["e_margin_pct"] = f(need(t, r"overcurrent: [\d.]+ A at its lowest against [\d.]+ A, ([\d.]+) % in hand", "the breaker's margin"))
    F["e_eta_floor"] = f(need(t, r"\] = (0\.\d+); the front end's efficiency at the\s+operating point must be at least that", "the efficiency floor"))
    m = need(t, r"F1: the breaker's highest ([\d.]+) A against its 80 C column ([\d.]+) A \(MEETS, MAKER\); L2 at ([\d.]+) A: ([\d.]+) K over the ([\d.]+) C air, ([\d.]+) C under its (\d+) C", "F1 and L2 at the breaker")
    F["e_l2"] = (f(m, 3), f(m, 4), f(m, 6), f(m, 7))
    F["e_q7_w"] = f(need(t, r"Q7 at [\d.]+ A: ([\d.]+) W", "Q7's dissipation"))
    m = need(t, r"= ([\d.]+) V, under POREN's (\d+) V maximum", "the drawn LM5069 at a 9.00 V plug")
    F["lm_vin_9"], F["lm_poren"] = f(m, 1), f(m, 2)
    m = need(t, r"flat target ([\d.]+) A of board current \(the pin at [\d.]+ V\) from VIN_RAW ([\d.]+) V up to ([\d.]+) V", "the corrected knee")
    F["knee"] = (f(m, 1), f(m, 2), f(m, 3))
    F["knee_hiz"] = f(need(t, r"HIZ is certain below ([\d.]+) V", "the corrected knee's certain HIZ"))
    m = need(t, r"R14 91k over R15 10k as drawn falls at ([\d.]+) / ([\d.]+) / ([\d.]+) V; R14 76\.8k: falls at ([\d.]+) / ([\d.]+) / ([\d.]+) V", "the restart guard")
    F["guard_drawn"], F["guard_sel"] = (f(m, 1), f(m, 2), f(m, 3)), (f(m, 4), f(m, 5), f(m, 6))
    F["e_env"] = {}
    for v in (9, 12, 24, 36):
        m = need(t, r"^\s+%d V \| ([\d.]+) V \| ([\d.]+) to ([\d.]+) \| ([\d.]+) to ([\d.]+) \|" % v, "the source envelope at %d V" % v)
        F["e_env"][v] = (f(m, 1), f(m, 4), f(m, 5))
    F["e_p1"] = tuple(float(x) for x in need(t, r"P1 shed: [^\n]*?\s([\d.]+) / ([\d.]+) / ([\d.]+) \|", "P1").groups())
    F["e_p2"] = tuple(float(x) for x in need(t, r"P2 warm-up: P1 with the regulated mat on\s+([\d.]+) / ([\d.]+) / ([\d.]+) \|", "P2").groups())
    F["e_p2_hand"] = f(need(t, r"the warm-up with ([\d.]+) W in hand", "the warm-up's margin"))
    m = need(t, r"while P1's load is at most ([\d.]+) W \(the source's least\s+([\d.]+) W less the mat\)", "P1's bound")
    F["e_p1_max"], F["e_src_least"] = f(m, 1), f(m, 2)
    need(t, r"REQ-015 at 9\.00 V at the plug: CONDITIONAL CANDIDATE, on E11-06", "REQ-015 at 9 V a conditional candidate")
    m = need(t, r"in case \(i\) the charge power is at most ([\d.]+) A x ([\d.]+) V = ([\d.]+) W", "R-b's charge power")
    F["rb_w"] = f(m, 3)
    F["rb_q2_tj"] = f(need(t, r"so TJ ([\d.]+) C at the 62\.1 C inside air against 150 C \(CONDITIONAL", "Q2 under R-b"))
    m = need(t, r"at least ([\d.]+) mOhm \(([\d.]+) mOhm at -20 C\) and at most ([\d.]+) mOhm", "the loop's floor and ceiling")
    F["loop_floor"], F["loop_floor_cold"], F["loop_ceil"] = f(m, 1), f(m, 2), f(m, 3)
    m = need(t, r"corrected to 20 C: ([\d.]+) to ([\d.]+) mOhm", "the loop's acceptance")
    F["loop_acc"] = (f(m, 1), f(m, 2))
    m = need(t, r"the worst case stays (\d+) A, 10 % under F1's (\d+) A", "the specified worst stiff-source current")
    F["ipf_spec"] = f(m, 1)
    F["ipf_spec_ov"] = f(need(t, r"which would give ([\d.]+) A on the same floor", "the floor at the OV maximum"))
    m = need(t, r"AWG 14, 3\.05 m cable, 0\.5 m lead \(SELECTED\)\s+([\d.]+) ohm, ([\d.]+) A", "the selected construction")
    F["ipf_constr"] = f(m, 2)
    m = need(t, r"each carries (\d+) A continuous \(which covers the envelope to \d+ A\), (\d+) A for (\d+) s and\s+(\d+) A for ([\d.]+) s", "the withstand obligations")
    F["d06_oblig"] = tuple(f(m, i) for i in range(1, 6))
    m = need(t, r"J_DCIN, the board connector\s+a (\d+) A class \(Amass XT60 family", "J_DCIN's selected class")
    F["jdcin_sel_a"] = f(m)
    m = need(t, r"VCL's minimum: ([\d.]+) ms .*?TI's margin: the fault time's minimum at least ([\d.]+) ms", "the LM5069 alternative's start", re.S)
    F["alt_start"], F["alt_need"] = f(m, 1), f(m, 2)
    m = need(t, r"168 nF; fault time ([\d.]+) ms nominal, ([\d.]+) to ([\d.]+) ms stacked", "the alternative's timer")
    F["alt_tflt"] = (f(m, 2), f(m, 3))
    m = need(t, r"Figure 10: ([\d.]+) A against ([\d.]+) A at ([\d.]+) ms", "the alternative's pulse")
    F["alt_soa"], F["alt_pulse"] = f(m, 1), f(m, 2)
    F["alt_f1_i2t"] = f(need(t, r"F1 during the longest start: ([\d.]+) A2s against", "the alternative's start I2t"))
    F["e11_items"] = re.findall(r"^\s+(E11-\d\d) \| ([A-Z]+) \| ([^|]+?) \|", t, re.M)
    if [x[0] for x in F["e11_items"]] != ["E11-%02d" % i for i in range(1, 36)]:
        refuse(3, "L4-E11's downstream items are not E11-01 to E11-35")
    t = T["e11entry"]
    m = need(t, r'"CSD19536KTT (\d+) V N-FET', "the selected Q7's voltage in the entry draft")
    F["e_q7_sel_v"] = f(m)
    need(t, r"ORDER: apply it AFTER L4-E9's apply_gen_sch_e_hotswap\.py", "the entry draft's order")
    t = T["l4e11md"]
    need(t, r"\*\*Selected \(SESSION\): \(A\)\.\*\*", "U-04's arrangement (A)")
    need(t, r"\*\*D-06 is resolved in design\*\*", "D-06 resolved in design")
    need(t, r"\*\*D-09 is resolved in design for the LM5069\*\*", "D-09 for the LM5069")

    t = T["l4e12"]      # L4-E12's accepted record: the electronics against the inside air (U-02, MESHSAT-1478)
    m = need(t, r"so the line is G_c = ([\d.]+) W/K, set by E5 \(E3-O alone ([\d.]+) W/K\)", "T-H1's binding line")
    F["gc"], F["g_e3o"] = f(m, 1), f(m, 2)
    F["g_a"] = f(need(t, r"so the line is ([\d.]+) W/K \(0 K margin\)", "approach (a)'s line"))
    m = need(t, r"E3-O's steady mixed air with the radios on ([\d.]+) C; the mixed air by which E5 needs the hold ([\d.]+) C; window ([\d.]+) K", "the air at the line")
    F["e3o_line"], F["e5_line"], F["hold_win"] = f(m, 1), f(m, 2), f(m, 3)
    F["hold_ref"] = f(need(t, r"at most \+-([\d.]+) K \(INFERRED\)", "the hold reference's offset"))
    F["e5_hold_w"] = f(need(t, r"Heat in E5 under it: ([\d.]+) W", "E5's heat under the hold"))
    F["e3o_stage_w"] = f(need(t, r"([\d.]+) W into the case with the front end's and\s+charger's loss", "the heat stage"))
    m = need(t, r"E3-O ([\d.]+) C, E5's dwell ([\d.]+) C \(steady", "the air at the floor")
    F["floor_air"] = (f(m, 1), f(m, 2))
    F["lo01a_ball"] = f(need(t, r"LO-01a's floor with the ballasts counted is ([\d.]+) W/K", "LO-01a with the ballasts"))
    F["e3o_amb12"] = f(need(t, r"E3-O ambient ([\d.]+) C; mixed air", "E3-O's ambient"))
    F["e5_amb"] = f(need(t, r"E5   ambient ([\d.]+) C; mixed air", "E5's ambient"))
    m = need(t, r"set at ([\d.]+) C \(rounded down\).*?set at ([\d.]+) C: at most", "the SGP41's thresholds", re.S)
    F["sgp_off"], F["sgp_on"] = f(m, 1), f(m, 2)
    need(t, r"6a At the margins, a part with every route rejected or outside authority on held evidence: none\.", "no part forces a question at the margins")
    need(t, r"idles the running module \(no shutdown\) and powers off\s+board D \(APRS\), the PA rail, the RockBLOCK \(RB_SW_EN\), the LoRa module \(LORA_ON\), both E72 \(ZB_ON\) and the Geiger module\s+\(GEIGER_EN\)", "the hold's actions")
    need(t, r"6b Inside the envelope: the SGP41 \(5d\), RAISED\. The conflict is CFL-002's", "CFL-002 raised")
    m = need(t, r"7d The lines cleared only by an absolute rating .*?: (\d+); the least\s+clearance ([\d.]+) K", "the absolute-only lines", re.S)
    F["abs_only"] = (int(m.group(1)), f(m, 2))
    # L4-E12's line reproduced from its own heat and L4-E8's ballasts (counted once, inside its figures)
    F["e5_hold_wb"] = F["e5_hold_w"] + F["ballast_w"]
    F["e3o_wb"] = F["e3o_stage_w"] + F["ballast_w"]
    if abs(F["e5_hold_wb"] / (F["e5_line"] - F["e5_amb"]) - F["gc"]) > 0.0005 or abs(F["e3o_wb"] / (F["e5_line"] - F["e3o_amb12"]) - F["g_e3o"]) > 0.0005:
        refuse(3, "L4-E12's line does not reproduce from its heat, the ballasts and its ambients")
    t = T["l4e12md"]
    m = need(t, r"\*\*Owner question: which of these three\?\*\*\s+- \*\*A\. (.*?)\*\*.*?- \*\*B\. (.*?)\*\*.*?- \*\*C\. (.*?)\*\*", "CFL-002's options", re.S)
    F["cfl002"] = (m.group(1), m.group(2), m.group(3))
    need(t, r"The session's recommendation: \*\*A\*\*", "L4-E12's recommendation")

    t = T["l4e13"]      # L4-E13's accepted record: U-03 a conditional downstream unit selection (PANEL-ACC)
    need(t, r"U-03: CONDITIONAL DOWNSTREAM UNIT SELECTION \(PANEL-ACC\)\.", "U-03's class")
    need(t, r"Route 2, a controlled unit: .*?A-3\(b\) met at the specification: yes", "route 2 feasible", re.S)
    need(t, r"NO PHYSICAL UNIT IS ACCEPTED: none is bought or measured; the purchase and the measurement are the owner's actions", "no unit accepted")
    r1 = re.findall(r"^\s+(SunPower SPR-E-Flex-100|BougeRV [^\n]*?|Solbian SX 156)\s+bounded (yes|NO); hold (yes|NO); portable (yes|no) -> (does not qualify|qualifies)", t, re.M)
    if len(r1) != 3 or any(x[4] != "does not qualify" for x in r1):
        refuse(3, "route 1's three rows")
    F["e13_route1"] = [(x[0].split(" (")[0], x[1], x[2]) for x in r1]
    F["e13_unit"] = need(t, r"THE UNIT \(SESSION\): one (SunPower SPR-E-Flex-100), recorded by serial number", "PANEL-ACC's unit").group(1)
    F["e13_a1_lim"] = f(need(t, r"A-1 THE WINDOW: Vm20 \+ U_V <= ([\d.]+) V", "A-1's limit"))
    m = need(t, r"A-1 ([\d.]+) V: PASS, margin ([\d.]+) V", "A-1 on the typical rows")
    F["e13_a1"], F["e13_a1_margin"] = f(m, 1), f(m, 2)
    m = need(t, r"lower bound ([\d.]+) W: PASS \(above ([\d.]+) W\)", "A-2 on the typical rows")
    F["e13_a2"], F["e13_a2_line"] = f(m, 1), f(m, 2)
    m = need(t, r"A-3 \(a\) ([\d.]+) A: PASS; \(b\) ([\d.]+) A .*?: PASS; \(c\) ([\d.]+) A at G_T", "A-3's three cases")
    F["e13_a3"] = (f(m, 1), f(m, 2), f(m, 3))
    F["e13_gt"] = f(need(t, r"G_T = ([\d.]+) W/m2 is a\s+SESSION design level", "A-3(c)'s design level"))
    m = need(t, r"a 20 A part would cover the double contingency up to (\d+) W/m2, ([\d.]+) x E0", "a 20 A part's coverage")
    F["e13_20a"] = (f(m, 1), f(m, 2))
    m = need(t, r"Voc25 from ([\d.]+) V \(A-2's floor: [\d.]+ x rated\) to ([\d.]+) V \(A-1's ceiling: [\d.]+ x rated\); Vm20 at most ([\d.]+) V", "the route 2 window")
    F["e13_win"] = (f(m, 1), f(m, 2), f(m, 3))
    F["e13_vr"] = f(need(t, r"the SMCJ28A's\s+VR ([\d.]+) V", "D4's standoff"))
    m = need(t, r"n_max = 2 \(MODELLING_ASSUMPTION\): the decision row\s+n 2\.0000: [\d.]+ V per unit of ln G; (\d+) W/m2, ([\d.]+) x E0", "the disturbance threshold")
    F["e13_thr"] = (f(m, 1), f(m, 2))
    m = need(t, r"the typical unit's fit: n ([\d.]+), ([\d.]+) with U_A", "M3's n on the typical unit")
    F["e13_n"] = (f(m, 1), f(m, 2))
    F["e13_a4_w"] = f(need(t, r"the unit's\s+maximum at -20 C, 1000 W/m2 is ([\d.]+) W", "A-4's maximum with no limit"))
    m1 = need(t, r"the rated unit \(the typical rows\), the conditioned upper corner \(18\.813 V\): ([\d.]+) Wh a day", "the rated unit at the upper corner")
    m2 = need(t, r"the rated unit \(the typical rows\), the nominal hold \(17\.593 V\): ([\d.]+) Wh a day", "the rated unit at the nominal hold")
    m3 = need(t, r"the floor unit \(A-2's lower bound on the line\), the conditioned upper corner \(18\.813 V\): ([\d.]+) Wh a day", "the floor unit")
    F["e13_day"] = (f(m1), f(m2), f(m3))
    m = need(t, r"U_V ([\d.]+) V on each voltage .*?U_A (\d+) % of A25; U_I (\d+) % of a current; U_G (\d+) % of A-2's\s+irradiance setting; U_TC ([\d.]+) K", "the specification", re.S)
    F["e13_spec"] = tuple(f(m, i) for i in range(1, 6))
    if abs(F["e13_day"][1] - F["a1_cand"][0]) > 0.05:
        refuse(3, "L4-E13's rated unit does not reproduce the energy record's day")
    # update round 4: A-3(a) and A-4 on L4-E7R's two layers as L4-E13 states them, and the nominal hold's day under them
    m = need(t, r"The primary limit REGULATES it: the LT8705A at RIMON_IN 31\.6k \(C705766\), ([\d.]+) A nominal, at\s+most ([\d.]+) A at 25 V", "A-3(a)'s regulation")
    F["e13_reg"] = (f(m, 1), f(m, 2))
    m = need(t, r"The backstop does NOT limit: it turns the stage off \(SWEN low\) when the input current reaches its trip, at most\s+([\d.]+) A at 25 V \(([\d.]+) A at its lowest\)", "A-3(a)'s backstop")
    F["e13_trip"] = (f(m, 2), f(m, 1))
    F["e13_corner"] = f(need(t, r"LT8705A's regulation at RIMON_IN 31\.6k, its own 25 V corner ([\d.]+) W", "A-4's regulation corner"))
    m = need(t, r"static bound ([\d.]+) W, margin ([\d.]+) W, CONDITIONAL on G_CM \(break-even (\d+) %\) and U18's VIN\+ bias \(break-even (\d+) mA\)", "A-4's backstop")
    F["e13_static"] = (f(m, 1), f(m, 2))
    need(t, r"leaves the conditioned upper corner's rows unchanged: yes", "the upper corner unchanged")
    F["e13_day_e7r"] = f(need(t, r"it moves the nominal hold's\s+day to ([\d.]+) Wh \(L4-E7 out 10", "the nominal hold's day under L4-E7R"))
    if (F["e13_reg"][0], F["e13_trip"], F["e13_corner"], F["e13_static"][0], F["e13_day_e7r"]) != (F["reg"][0], F["bs_trip"], F["reg_corner"], F["static_bound"], F["e7r_day"][1]):
        refuse(3, "L4-E13's citation of L4-E7R does not read L4-E7R's own figures")
    if not (F["e13_reg"][0] < F["e13_reg"][1] < F["e13_trip"][1] < F["e13_a3"][0] <= 10.0):
        refuse(3, "A-3(a)'s ordering")
    t = T["l4e13chk"]
    if not t.startswith("accepted: yes\n"):
        refuse(3, "L4-E13's check 3 is not accepted")
    need(t, r"\*\*Owner decision required:\*\* none", "no owner decision")
    t = T["l4e13chk4"]
    if not t.startswith("accepted: yes\n"):
        refuse(3, "L4-E13's check 4 is not accepted")
    need(t, r"carry\s+336\.6 Wh in place of 350\.0 Wh where it cites the nominal hold under the accepted stage", "check 4's instruction")
    need(T["l4e13md"], r"\*\*U-03: CONDITIONAL DOWNSTREAM UNIT SELECTION \(PANEL-ACC\)\.\*\*", "U-03's class on the page")

    t = T["s120"]
    m = need(t, r"with 100 ppm/K over 65 K \(INFERRED\).*?\s+([\d.]+) to ([\d.]+) V\s+<- the DC band", "VBUS20 DC band")
    F["vbus_band"] = (f(m, 1), f(m, 2))
    F["vbus_bound"] = f(need(t, r"BOUND, INFERRED\s+([\d.]+) V", "VBUS20 bound"))
    m = need(t, r"opens its pass FET at OVLO ([\d.]+) / ([\d.]+) / ([\d.]+) V \(OVLOTH ([\d.]+) / ([\d.]+) / ([\d.]+) V", "OVLO")
    F["ovlo"] = (f(m, 1), f(m, 2), f(m, 3))
    th = (f(m, 4), f(m, 5), f(m, 6))
    r22 = float(re.match(r"([\d.]+)k", Gen(T["gen_e"]).value("R22")).group(1))
    # the selected band: R23 at E192's 6.42k with R22 and R23 both 0.1 % (SESSION, part A's CS101 finding; register R-94)
    F["ovlo_sel"] = (th[0] * (1 + r22 * 0.999 / (R23_NEW_K * 1.001)), th[1] * (1 + r22 / R23_NEW_K), th[2] * (1 + r22 * 1.001 / (R23_NEW_K * 0.999)))
    F["chg_v_max"] = f(need(t, r"ChargeVoltage 16\.8 V \+ 0\.5 % = ([\d.]+) V", "ChargeVoltage maximum"))
    F["batovp"] = f(need(t, r"BATOVP at most 105 % = ([\d.]+) V", "BATOVP"))
    F["u3_rec_vbus"] = f(need(t, r"U3 VBUS, ACP, ACN \((\d+) V recommended", "U3 recommended"))
    F["acov_min"] = f(need(t, r"U3 ACOV rising minimum \(([\d.]+) V", "ACOV"))

    t = T["budget"]
    m = need(t, r"^PS-IDLE-SPEC load\s+([\d.]+) \| battery\s+([\d.]+) /\s+([\d.]+) /\s+([\d.]+)", "IDLE-SPEC")
    F["idle"] = (f(m, 2), f(m, 3), f(m, 4))
    m = need(t, r"^PS-ALLTX\s+load\s+([\d.]+) \| battery\s+([\d.]+) /\s+([\d.]+) /\s+([\d.]+)", "ALLTX")
    F["alltx"] = (f(m, 2), f(m, 3), f(m, 4))
    m = need(t, r'^PS-IDLE-SPEC \{"battery_W_plan": [\d.]+, .*?"I_plan": \{"16\.8": ([\d.]+), "14\.4": ([\d.]+), "12\.0": ([\d.]+), "10\.0": ([\d.]+)\}', "IDLE-SPEC currents")
    F["idle_i"] = tuple(f(m, i) for i in range(1, 5))
    m = need(t, r'^PA keyed alone over PS-IDLE-SPEC, PA at 113 W \{"battery_W_plan": ([\d.]+), .*?"I_plan": \{"16\.8": ([\d.]+), "14\.4": ([\d.]+), "12\.0": ([\d.]+), "10\.0": ([\d.]+)\}', "PA keyed 113 W")
    F["pa113"] = tuple(f(m, i) for i in range(1, 6))
    m = need(t, r'^PS-TYP plus USB-C \{"battery_W_plan": ([\d.]+), "battery_W_high": ([\d.]+), "outside_W": ([\d.]+), .*?"I_plan": \{"16\.8": ([\d.]+), "14\.4": ([\d.]+)', "TYP plus USB-C")
    F["typ_usbc"] = tuple(f(m, i) for i in range(1, 6))
    m = need(t, r'^PS-TYP plus PoE \{"battery_W_plan": ([\d.]+), "battery_W_high": ([\d.]+), "outside_W": ([\d.]+)', "TYP plus PoE")
    F["typ_poe"] = tuple(f(m, i) for i in range(1, 4))
    m = need(t, r'^ALLTX plan \{"battery_W": ([\d.]+), "vbat_W": ([\d.]+), "V_vbat_at_18A": ([\d.]+), "V_stack_at_18A": ([\d.]+)', "D-11 basis")
    F["alltx_18a_stack"] = f(m, 4)
    line = need(t, r'^ALLTX plan \{.*$', "D-11 line").group(0)
    F["alltx_rest_need"] = max(float(x) for x in re.findall(r'"V_rest_pack": ([\d.]+)', line))
    F["alltx_20a_stack"] = f(need(line, r'"V_stack_at_I": \{[^}]*"20\.0": ([\d.]+)', "the 20 A stack"))
    F["d11_floor"] = f(need(T["hwfw"], r"SoC floors ([\d.]+) V and ([\d.]+) V rest", "D-11 floors"))
    F["pa_floor"] = f(need(T["hwfw"], r"SoC floors [\d.]+ V and ([\d.]+) V rest", "PA floor"))
    t = T["trace"]
    m = need(t, r"PLAN by tier, W:\s+S ([\d.]+), R ([\d.]+), D ([\d.]+), T ([\d.]+)", "tiers")
    F["undoc_w"] = f(m, 4)

    yaml.safe_load(T["packprot"])        # it parses (a malformed file refuses here)
    txt = T["packprot"]
    F["pp_cont"] = f(need(txt, r"declared_continuous_a: ([\d.]+)", "declared continuous"))
    F["pp_peak"] = f(need(txt, r"declared_peak_a: ([\d.]+)", "declared peak"))
    m = need(txt, r"prospective_fault_a: \{low: ([\d.]+), high: ([\d.]+)\}", "prospective fault")
    F["pp_fault"] = (f(m, 1), f(m, 2))
    F["ocd1"] = (f(need(txt, r"threshold: \{value: (20\.0), unit: A, per: pack, delay_s: (2\.0)\}", "OCD1")), 2.0)
    F["occ"] = f(need(txt, r"threshold: \{value: (5\.0), unit: A, per: pack, delay_s: 2\.0\}", "OCC"))
    F["scd"] = f(need(txt, r"threshold: \{value: (60\.0), unit: A, per: pack, delay_s: 0\.0002\}", "SCD"))
    F["cuv"] = f(need(txt, r"threshold: \{value: (2\.50), unit: V, per: cell", "CUV"))
    F["cov"] = f(need(txt, r"threshold: \{value: (4\.25), unit: V, per: cell", "COV"))
    F["cell_chg_ma"] = f(need(txt, r"max_charge_current_ma:\s+\{value: (\d+)", "cell charge maximum"))
    F["cell_dis_ma"] = f(need(txt, r"max_continuous_discharge_ma: \{value: (\d+)", "cell discharge maximum"))
    env = T["envelope"]
    m = need(env, r"worst_inside_air_c: \{lid_open: ([\d.]+), lid_closed: ([\d.]+)", "worst inside air")
    F["air"] = (f(m, 1), f(m, 2))
    hw = T["hwfw"]
    F["chg_set"] = f(need(hw, r"ChargeCurrent at most ([\d.]+) A \(the nearest code at or below\)", "FW-A02"))
    F["ina_fs_contract"] = f(need(hw, r"full scale (81\.92) mV over the shunt", "FW-A09 full scale"))
    m = need(T["dec31"], r"moves DC_F ([\d.]+) V at 8 kV and ([\d.]+) V at 15 kV", "E-F1's bound")
    F["ef1_dv"] = (f(m, 1), f(m, 2))
    m = need(T["dec31"], r"moves it 0\.06 V at\s+8 kV and ([\d.]+) V at 15 kV", "VIN_RAW's discharge bound")
    F["vinraw_esd_dv"] = f(m)
    ifc = T["ifaces"]
    m = need(ifc, r"Lapp OLFLEX ROBUST 210 (\d+) x ([\d.]+) or Alpha Wire 25064, (\d+) m", "the external DC cable")
    F["cable_mm2"], F["cable_m"] = f(m, 2), f(m, 3)
    m = need(ifc, r'harness: "inside: (\d+) AWG, (\d+) mm, VH crimp at E', "the inside DC lead")
    F["lead_awg"], F["lead_mm"] = f(m, 1), f(m, 2)
    m = need(ifc, r"([\d.]+) A per pin with four sharing,\s+([\d.]+) A with one open", "pack pins")
    F["pack_pin_share"] = (f(m, 1), f(m, 2))

    # ============================================= update round 5: the dependency rounds of L4-E10, L4-E12 and L4-E11 (2 October 2026)
    # Each read from the record's pinned output (strings kept as printed there); each record's check 4 must read accepted.
    for key, who in (("l4e10chk4", "L4-E10"), ("l4e12chk4", "L4-E12"), ("l4e11chk4", "L4-E11")):
        if not T[key].startswith("accepted: yes\n"):
            refuse(3, "%s's check 4 is not accepted" % who)
    need(T["l4e11chk4"], r"U-04's class stays ARCHITECTURE-LEVEL CHOICE", "check 4's U-04 class")
    need(T["l4e12chk4"], r"Only below E3-O's floor does\s+the remaining option become the owner's", "check 4's U-02 owner line")
    need(T["l4e10chk4"], r"FEA-008 stays open", "check 4's FEA-008 open")
    r5 = {}
    t = T["l4e10"]      # out 9: U-01 by mode
    need(t, r"^== 9\. U-01 BY MODE", "L4-E10's section 9")
    m = need(t, r"^   HL18650V \(II\): ([\d.]+) Wh at \+25 C \(([\d.]+) h;", "the chain's HL18650V usable energy")
    r5["hl"] = (m.group(1), m.group(2))
    m = need(t, r"^   35E \(D-06; the chain's inputs MAKER\): ([\d.]+) Wh at \+25 C \(([\d.]+) h\)", "the chain's 35E usable energy")
    r5["e35"] = (m.group(1), m.group(2))
    r5["hl_pct"] = need(t, r"the page gives none\), ([\d.]+) % less than the 35E\.", "the chain's difference").group(1)
    m = need(t, r"with the cells at -5\.52 C,\s+([\d.]+) to ([\d.]+) Wh", "the cold bracket at -5.52 C")
    r5["cold"] = (m.group(1), m.group(2))
    m = need(t, r"a cold start at -20 C,\s+([\d.]+) to ([\d.]+) Wh", "the cold start bracket")
    r5["start"] = (m.group(1), m.group(2))
    rng = re.findall(r"^   CH (Low Temp|Standard Temp low|Recommended and Standard Temp high) \((T\d) to (T\d)\)\s+(-?\d+) to (\d+) C \(page\): "
                     r"[\d.]+C = [\d.]+ A for the pack, set ([\d.]+) A; ([\d.]+) V a cell = ([\d.]+) V \(BATOVP ([\d.]+) V\)", t, re.M)
    if [x[0] for x in rng] != ["Low Temp", "Standard Temp low", "Recommended and Standard Temp high"]:
        refuse(3, "L4-E10's three charge ranges")
    r5["ranges"] = rng
    m = need(t, r"CH thresholds: UTC (-[\d.]+) C \(recovery (-[\d.]+) C\), T1 (-\d+) C, T2 (\d+) C, T5 (\d+) C; T3 (\d+) C, T4 (\d+) C and OTC ([\d.]+) C kept",
             "the charge thresholds")
    r5["thr"] = m.groups()
    r5["hold"] = need(t, r"the kit's hold below (-\d+) C;", "the kit's cold charge hold").group(1)
    m = need(t, r"the gauge's CUV from ([\d.]+) V to ([\d.]+) V a cell", "the CUV draft")
    r5["cuv"] = (m.group(1), m.group(2))
    r5["term"] = need(t, r"TI's default (\d+) mA kept \(ASSUMPTION\)", "the termination current").group(1)
    warm = re.findall(r"^      to (T\d) \(([-+]\d+) C\): ([\d.]+) h, ([\d.]+) Wh at the low corner; (?:([\d.]+) h, ([\d.]+) Wh at the high corner|not reached \(the mat alone stops at ([\d.]+) C\) at the high corner)", t, re.M)
    if [w[0] for w in warm] != ["T1", "T2", "T5"]:
        refuse(3, "L4-E10's warm-up rows")
    r5["warm"] = warm
    m = need(t, r"under ([\d.]+) C H1 acts in E5's dwell.*?under ([\d.]+) C E5's cells pass the limit; under ([\d.]+) C E3-O loses 'no shutdown'; under ([\d.]+) C E3-S fails;\s+under ([\d.]+) C E3-O's cells pass it",
             "the idle limit's thresholds", re.S)
    r5["idle"] = m.groups()
    m = need(t, r"\(I\)'s cooler \(([\d.]+) to ([\d.]+) W at the conditioned corner", "(I)'s cooler")
    r5["cooler"] = (m.group(1), m.group(2))
    m = need(t, r"added energy storage, (\d+) to (\d+) Wh", "(III)'s added storage")
    r5["prim"] = (m.group(1), m.group(2))
    r5["per100"] = need(t, r"Minimum capacity: ([\d.]+) Wh of usable energy per 100 mAh", "usable energy per 100 mAh").group(1)
    r5["dis"] = need(t, r"Continuous discharge: at or above ([\d.]+) A a cell \(PS-ALLTX's 18 A\)", "the discharge threshold").group(1)
    r5["crate"] = need(t, r"Charge current from \+10 C: at or above ([\d.]+)C, the drawn 3\.0 A stands", "the charge-current threshold").group(1)
    m = need(t, r"L4-E9 section 10's U-01 bullet reads ([\d.]+) Wh against ([\d.]+) Wh .*?every\s+shortfall growing by at most ([\d.]+) Wh; this chain gives ([\d.]+) Wh, ([\d.]+) Wh less than the 35E's ([\d.]+) Wh, the same growth",
             "L4-E10's reading of this record's U-01 bullet", re.S)
    if (float(m.group(1)), float(m.group(2))) != (F["cell_usable"][1], F["cell_usable"][0]) or (m.group(4), m.group(6)) != (r5["hl"][0], r5["e35"][0]) \
            or m.group(3) != m.group(5):
        refuse(3, "L4-E10's two chains: its reading of this record's figures, or the growth, differs")
    r5["growth"] = m.group(3)
    m = need(t, r"The drafted request \(`clarification/topwell-hl18650v\.txt`, questions ([\d, ]+)\) gained 7 to 10", "the drafted request's questions")
    r5["tw_q"] = [int(x) for x in m.group(1).split(", ")]
    if r5["tw_q"] != [int(x) for x in re.findall(r"^(\d+)\. ", T["cl_topwell"], re.M)] or r5["tw_q"] != list(range(1, 11)):
        refuse(3, "the drafted request to Topwell does not carry questions 1 to 10")
    t = T["l4e12"]      # out 8: U-02 in depth
    need(t, r"^8 U-02 IN DEPTH", "L4-E12's section 8")
    m = need(t, r"E5, the hold\s+Q ([\d.]+) W \(([\d.]+) W \+ the ballasts ([\d.]+) W\) / \((\d+) - (\d+)\) K = ([\d.]+) W/K", "the line's basis")
    r5["basis"] = m.groups()
    if float(m.group(6)) != F["gc"]:
        refuse(3, "L4-E12's round reads another line than its record's 2.159 W/K")
    m = need(t, r"its line is ([\d.]+) to ([\d.]+) W/K \(0\.100 W/K per W\)", "the fans' spread on the line")
    r5["fans"] = (m.group(1), m.group(2))
    m = need(t, r"so a reading of at least\s+([\d.]+) W/K at a 10 K rise \(([\d.]+) W/K at 20 K\)", "T-H1's pass line")
    r5["pass"] = (m.group(1), m.group(2))
    m = need(t, r"Expanded \(k = 2\): ([\d.]+) % at a 10 K rise and ([\d.]+) % at 20 K", "T-H1's expanded uncertainty")
    r5["unc"] = (m.group(1), m.group(2))
    m = need(t, r"within 1 % of the rise after ([\d.]+) to ([\d.]+) h a point, (\d+) to (\d+) h", "T-H1's duration")
    r5["dur"] = m.groups()
    m = need(t, r"So F4 holds E5 down to ([\d.]+) W/K and E3-O down to ([\d.]+) W/K \(([\d.]+) with the\s+connectors out of the exhaust\); with F3, E5 down to ([\d.]+) W/K",
             "the plate coupling's floors")
    r5["f4"] = m.groups()
    m = need(t, r"takes E5's heat to ([\d.]+) W and its line to ([\d.]+) W/K", "the deeper hold")
    r5["f3"] = (m.group(1), m.group(2))
    m = need(t, r"outside fins of twice the area multiply it by ([\d.]+) to ([\d.]+) and fins of twice the area on both faces by ([\d.]+)\s+to ([\d.]+):", "the fins")
    r5["f1"] = m.groups()
    m = need(t, r"puts E5's mixed air at ([\d.]+) to ([\d.]+) C", "a stopped fan")
    r5["stop"] = (m.group(1), m.group(2))
    r5["plate_stop"] = need(t, r"With the fans stopped the coupled parts stay at most ([\d.]+)\s+C", "the coupled parts with the fans stopped").group(1)
    need(t, r"THE BEST FALLBACK: F4, the plate coupling, with F3 in E5: no owner ruling, no change to E3-O\. What needs the owner: a reading\s+under E3-O's F4 floor",
         "the fallback's ownership")
    m = need(t, r"Register row drafted for L4-E9's downstream register \(its owner\s+inserts it\): \"R-new \| (\w+) \| (.+?) \| (L4-E12 8c) \| (.+?) \| (.+?)\"", "the drafted fan row", re.S)
    r5["fanrow"] = tuple(" ".join(x.split()) for x in m.groups())
    t = T["th1proc"]
    need(t, r"\*\*A\s+draft\s+for\s+the\s+bench,\s+not\s+run;\s+prototype\s+design:\s+nothing\s+has\s+been\s+bought,\s+built,\s+powered\s+or\s+measured\.\*\*", "T-H1's procedure as a draft")
    # revised for L4-E12's reconciliation (check 7): the single 10 K pass line is replaced by each condition's point at its own heat
    if need(t, r"What\s+the\s+revisions\s+replace:\*\*\s+the\s+single\s+pass\s+line\s+of\s+([\d.]+)\s+W/K\s+at\s+a\s+10\s+K\s+rise", "the procedure's replaced pass line").group(1) != r5["pass"][0]:
        refuse(3, "T-H1's procedure replaces a pass line L4-E12's output does not print")
    r5["k10_pass"] = need(t, r"the LimeSDR's \+70 C storage row: 2\.159 W/K, ([\d.]+) W/K \(U-02's line\)", "the procedure's E5 row").group(1)
    t = T["l4e11"]      # out 9 to 11: U-04's dependency round
    need(t, r"^9\. THE DEPENDENCY ROUND", "L4-E11's section 9")
    r5["drows"] = re.findall(r"^   (D\d+) ", t, re.M)
    if r5["drows"] != ["D%d" % i for i in range(1, 11)]:
        refuse(3, "L4-E11's rows D1 to D10")
    m = need(t, r"VSYS needs only ([\d.]+) V against ChargeVoltage's floor ([\d.]+) V, a ([\d.]+) V margin that is large against any plausible unit spread", "D1's margin")
    r5["d1"] = m.groups()
    r5["por"] = need(t, r"\"The POR value is indeed (\d+)mA\"", "the POR value").group(1)
    m = need(t, r"the worst admitted step: (.+?), ([\d.]+) W, ([\d.]+) A at the floor", "the worst admitted step")
    r5["step"] = m.groups()
    r5["mj"] = need(t, r"([\d.]+) mJ in all, the MLCCs not counted", "the fallback's energy").group(1)
    m = need(t, r"against the worst admitted step: ([\d.]+) ms of hold, over the (\d+) ms assumed", "the fallback's hold")
    r5["hold_ms"] = (m.group(1), m.group(2))
    m = need(t, r"the bank charges through R_CH at ([\d.]+) mA at most, ([\d.]+) W at most", "the bank's charge")
    r5["chg"] = (m.group(1), m.group(2))
    m = need(t, r"narrows the architecture's dependence on TI from four statements \(([^)]+)\) to two\s+\(([^)]+)\)", "the narrowed dependence")
    r5["dep"] = (m.group(1), m.group(2))
    m = need(t, r"negative answers with a remedy inside arrangement \(A\): ([^;]+); with none: (D\d) and (D\d), whose negative answers return \(B\)", "the remedies")
    r5["remedy"] = m.groups()
    need(t, r"so U-04 STAYS AN ARCHITECTURE-LEVEL CHOICE", "U-04's class in L4-E11")
    need(t, r"one Panasonic EEHZK1V181P .*?4 x EEHZK1E471P.*?R_CH 330 Ohm.*?D_H, a Diodes B540C-13-F", "the fallback's parts", re.S)
    r5["tiq"] = re.findall(r"^- \*\*(Q-TI-\d+(?:, addendum)?) \(rows? ([^)]+)\)\.\*\*", T["cl_tiq"], re.M)
    if [q[0] for q in r5["tiq"]] != ["Q-TI-3, addendum", "Q-TI-11", "Q-TI-12", "Q-TI-13", "Q-TI-14", "Q-TI-15", "Q-TI-16"]:
        refuse(3, "TI-QUESTIONS.md's questions")
    need(T["cl_tiq"], r"\*\*Q-AOS-1 \(E11-30\)\.\*\*", "the battery FET maker's question")
    need(T["cl_tiq"], r"Q-AOS-1 is withdrawn: the fix round selects two Nexperia BUK6Y10-30P", "the AOS question withdrawn (L4-E11 15c)")
    need(T["cl_tiq"], r"\*\*Drafts for the owner to send\*\*", "the TI questions as the owner's drafts")
    F["r5"] = r5

    # ============================================= the consolidation (the owner's instruction of 2 October 2026, 11:25): the budget's
    # inputs not read above, each from its pinned file
    cb = {}
    t = T["budget"]
    m = need(t, r"^PS-IDLE-SPEC load\s+([\d.]+) \| battery\s+([\d.]+) /\s+([\d.]+) /\s+([\d.]+)", "PS-IDLE-SPEC's split")
    cb["idle_pins"] = f(m, 1)
    if (f(m, 2), f(m, 3), f(m, 4)) != F["idle"]:
        refuse(3, "pwr_budget.out's PS-IDLE-SPEC split is not the profile read above")
    m = need(t, r'^PS-IDLE-SPEC open_fans \{.*?"heat_plan_W": ([\d.]+), "heat_high_W": ([\d.]+), "pack_I2R_plan_W": ([\d.]+)', "PS-IDLE-SPEC's heat")
    cb["idle_heat"], cb["idle_heat_hi"], cb["idle_i2r"] = f(m, 1), f(m, 2), f(m, 3)
    m = need(t, r'^PS-IDLE-SPEC open_fans \{"enclosure": "open_fans", "G_bound": \[([\d.]+), ([\d.]+)\]', "W4's lid-open bound")
    cb["w4"] = (f(m, 1), f(m, 2))
    t = T["tablet"]
    cb["tab_cap"] = f(need(t, r"P_CAP, PEAK OUTPUT POWER: ([\d.]+) W at the outlet", "the outlet's cap"))
    cb["tab_out"] = f(need(t, r"E_OUT, ENERGY DELIVERED AT THE OUTLET: at most ([\d.]+) Wh a day", "the outlet's daily energy"))
    m = need(t, r"in a 2 h window: [\d.]+ / ([\d.]+) = ([\d.]+) Wh \(([\d.]+) W for 2 h\)", "the window's energy at VBAT")
    cb["tab_eta"], cb["tab_wh"], cb["tab_w"] = f(m, 1), f(m, 2), f(m, 3)
    cb["tab_any"] = f(need(t, r"ANY, the same Wh with the converter on all day: .*? = ([\d.]+) Wh", "the converter on all day"))
    m = need(t, r"IDLE DRAW, ENABLED AND NOT LOADED: ([\d.]+) W typ, ([\d.]+) W max", "the outlet converter's idle draw")
    cb["tab_idle"] = (f(m, 1), f(m, 2))
    m = need(t, r"the case is W13 \((\d+) to\s+(\d+) UTC\)", "the window's hours")
    cb["tab_win"] = (int(m.group(1)), int(m.group(2)))
    t = T["l4e12"]
    m = need(t, r"The heat stage after BANK-R1 \(PS-SURV-R\) on shore, plan: ([\d.]+) W at the pack, ([\d.]+) W into the case", "the heat stage")
    cb["stage_pack"], cb["stage_case"] = f(m, 1), f(m, 2)
    m = need(t, r"([\d.]+) W at the load\s+pins, ([\d.]+) W lost in the converters, ([\d.]+) W in the distribution \(fuses, FETs, shunt, leads\): ([\d.]+) W at the pack; on shore\s+the front end's and the charger's loss on it adds ([\d.]+) W",
             "E5's hold built up")
    cb["e5"] = tuple(f(m, i) for i in range(1, 6))
    m = need(t, r"PS-IDLE-SPEC \(the profile\)\s+(\d) fans: ([\d.]+) W at the pack of ([\d.]+) W", "the profile's fans")
    cb["fans_idle"] = (int(m.group(1)), f(m, 2), f(m, 3))
    cb["fans_stage"] = f(need(t, r"the heat stage \(PS-SURV-R\)\s+\d fans: ([\d.]+) W at the pack", "the heat stage's fans"))
    cb["fans_e5"] = f(need(t, r"E5's hold\s+\d fans: ([\d.]+) W at the pack", "E5's fans"))
    cb["chg_heat"] = f(need(t, r"A charge running on shore \(the pack outside, at room temperature, inside its window\): \+([\d.]+) W", "a charge's heat"))
    m = need(t, r"C1, module shedding \| inside air \+(\d+) C or any cell \+(\d+) C", "C1's trigger")
    cb["c1_air"], cb["c1_cell"] = f(m, 1), f(m, 2)
    m = need(T["l4e13"], r"the stage draws its own drive and quiescent power, ([\d.]+) mA, ([\d.]+) W", "the stage's own power")
    cb["stage_q"] = (f(m, 1), f(m, 2))
    m = need(T["l4e10"], r"35E \(D-06; the chain's inputs MAKER\): ([\d.]+) Wh at \+25 C \(([\d.]+) h\), ([\d.]+) Wh with the cells at -10 C \(([\d.]+) h, the replay's [\d.]+ / [\d.]+ Wh reproduced\), ([\d.]+) Wh at -5\.52 C",
             "the 35E on L4-E10's chain")
    if (f(m, 1), f(m, 3), f(m, 2), f(m, 4)) != F["a1_bat"]:
        refuse(3, "L4-E10's chain does not reproduce the replay's battery-only figures")
    cb["e35_552"] = f(m, 5)
    bh = {}
    bh["iin_reset"] = f(need(T["chgseq"], r"([\d.]+) A at each adapter removal", "IIN_HOST's reset"))
    m = need(T["l4e8"], r"the bleed ([\d.]+) to ([\d.]+) s to release", "the bank's bleed")
    bh["bleed"] = (f(m, 1), f(m, 2))
    bh["hold_trig"] = f(need(T["l4e12"], r"The trigger then sits at the window's middle, ([\d.]+) C of mixed air", "the hold's trigger"))
    m = need(T["l4e12"], r"restore (\d+) K under it after (\d+) minutes", "the hold's restore")
    bh["hold_restore"] = (f(m, 1), f(m, 2))
    bh["clamp_ma"] = f(need(T["l4e11"], r"(\d+) mA typical with no maximum printed", "the charger's clamp"))
    hw = T["hwfw"]
    bh["hwd"] = f(need(hw, r"host watchdog HWD (\d+) s", "the gauge's host watchdog"))
    bh["chg_wd"] = f(need(hw, r"its own (\d+) s watchdog", "the charger's watchdog"))
    m = need(hw, r"Holding MAIN about ([\d.]+) s \(([\d.]+) to ([\d.]+) s\)", "MAIN's forced off")
    bh["main"] = (f(m, 1), f(m, 2), f(m, 3))
    bh["fan_rep"] = f(need(hw, r"a stalled fan reported within (\d+) s", "a stalled fan's report"))
    bh["heat_below"] = f(need(hw, r"warm before charge below (-\d+) C at the cell", "the heater's policy"))
    m = need(hw, r"at most (\d+) s per key-down, (\d+) s apart; gates at \+(\d+) C cells, \+(\d+) C air, \+(\d+) C flange", "the key-down rules")
    bh["key"] = tuple(f(m, i) for i in range(1, 6))
    bh["graceful"] = f(need(T["l4e10"], r"graceful line at ([\d.]+) V under load", "the graceful line"))
    m = need(T["l4e11"], r"([\d.]+) A peak, over the image's ASCD\s+([\d.]+) A for ([\d.]+) us against its (\d+) us delay", "the pack's inrush")
    bh["inrush"] = (f(m, 1), f(m, 2), f(m, 3), f(m, 4))
    cb["bh"] = bh
    # the consolidation's two results: L4-E11's charger selection (B1) and L4-E12's thermal verdict, each with its check 5
    for key, who, pat in (("l4e11chk5", "L4-E11", r"U-04 becomes a downstream qualification test"), ("l4e12chk5", "L4-E12", r"U-02 is a closure condition, decided by one bounded experiment")):
        if not T[key].startswith("accepted: yes\n"):
            refuse(3, "%s's check 5 is not accepted" % who)
        need(T[key], pat, "%s's check 5 verdict" % who)
    t = T["l4e11"]
    b1 = {}
    need(t, r"SELECTED \(SESSION\): \(B1\), TI's BQ25730 in U3's land with Q39", "the charger selection")
    need(t, r"U-04 BY THE OWNER'S EXIT DEFINITION: A DOWNSTREAM QUALIFICATION TEST WITH BOUNDED EVIDENCE AND A WORKABLE FALLBACK, once E11-27 is applied", "U-04's class")
    b1["vsys_min"] = f(need(t, r"at least ([\d.]+) V at TJ -40 to 125 C", "VSYS with no battery"))
    m = need(t, r"VSRN \+ (\d+) mV within\s+\+-(\d+) %", "VSYS with the charge inhibited")
    b1["inhib"] = (f(m, 1), f(m, 2))
    b1["margin"] = f(need(t, r"([\d.]+) V, which a load step in S2 or S4 must not use up", "D2's margin"))
    m = need(t, r"on battery at PS-IDLE-SPEC, ([\d.]+) A: ([\d.]+) W in Q39, ([\d.]+) % of the pack's output", "Q39 at the profile")
    b1["q39_idle"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(t, r"\(B1\) Q39 ([\d.]+) W at PS-IDLE-SPEC and ([\d.]+) W at PS-TYP, ([\d.]+) W at 10 A", "Q39's heat")
    b1["q39_heat"] = (f(m, 1), f(m, 2), f(m, 3))
    if b1["q39_heat"][0] != b1["q39_idle"][1]:
        refuse(3, "L4-E11's two Q39 figures differ")
    b1["bar"] = f(need(t, r"installed RthJA of at most ([\d.]+) C/W", "Q39's thermal bar"))
    m = need(t, r"([\d.]+) A peak through\s+Q39's body diode into VSYS's (\d+) uF at most, over IDM's (\d+) A for ([\d.]+) us", "the docking pulse")
    b1["dock"] = (f(m, 1), f(m, 2), f(m, 3), f(m, 4))
    b1["strap"] = f(need(t, r"keeps the 4S strap \(([\d.]+) percent of VDDA\)", "the cell-count strap"))
    b1["vsys_max"] = f(need(t, r"to ([\d.]+) V \(the pack at ChargeVoltage's", "VSYS's top with the pack"))
    need(t, r"ChargeCurrent resets to 0000h, 0 A", "ChargeCurrent's reset")
    b1["rb_ma"] = f(need(t, r"ChargeCurrent 0x0080, 256 mA within \+-30 % at 0 to 85 C \(p\.11\), at\s+most ([\d.]+) mA", "R-b''s precharge"))
    b1["rb_v"] = f(need(t, r"no charge under ([\d.]+) V on SRN", "R-b''s floor"))
    m = need(t, r"\(A\) ([\d.]+) USD .*?\(B1\) ([\d.]+) USD", "the part cost", re.S)
    b1["cost"] = (f(m, 1), f(m, 2))
    m = need(t, r"(\d+) of the BQ25731's (\d+) row blocks are identical in the BQ25730's table", "the rows carried over")
    b1["rows_same"] = (int(m.group(1)), int(m.group(2)))
    cb["b1"] = b1
    t = T["l4e12"]
    tb = {}
    need(t, r"9e U-02'S CLASS: T-H1 DECIDES", "U-02's class")
    for k, pat in (("e5", r"E5\s+60 C, the air 10 K up: lid open ([\d.]+) \(the other coefficient ends ([\d.]+)\), lid closed ([\d.]+)"),
                   ("e3o", r"E3-O\s+55 C, the air 15 K up: lid open ([\d.]+) \(the other coefficient ends ([\d.]+)\), lid closed ([\d.]+)")):
        m = need(t, pat, "the bound at %s" % k)
        tb[k] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(t, r"The envelope's \+40 C, the air 15 K up: lid open ([\d.]+), lid closed ([\d.]+)", "the bound at +40 C")
    tb["env"] = (f(m, 1), f(m, 2))
    tb["cap"] = tuple(float(x) for x in re.findall(r"ANY inside film \(a 50 m/s flow\) ([\d.]+), the outside films' cap", t))
    for k, pat in (("air_e5", r"E5, the hold: the air ([\d.]+) C \(([\d.]+) W/K at ([\d.]+) K\)"), ("air_f3", r"E5, the deeper hold \(F3\): the air ([\d.]+) C \(([\d.]+) W/K at ([\d.]+) K\)"),
                   ("air_e3o", r"E3-O, the heat stage: the air ([\d.]+) C \(([\d.]+) W/K at ([\d.]+) K\)")):
        m = need(t, pat, k)
        tb[k] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(t, r"E5 with F4 and F3, with every session measure .*?needing ([\d.]+) W/K at its (\d+) K; the bound gives ([\d.]+) W/K: clears by ([\d.]+) W/K", "E5 with every measure", re.S)
    tb["all_e5"] = tuple(f(m, i) for i in range(1, 5))
    m = need(t, r"E3-O with F4, with every session measure .*?needing ([\d.]+) W/K at its (\d+) K; the bound gives ([\d.]+) W/K: GAP ([\d.]+) W/K", "E3-O with every measure", re.S)
    tb["all_e3o"] = tuple(f(m, i) for i in range(1, 5))
    m = need(t, r"the module's intake reaches ([\d.]+) C against its \+(\d+) C", "the module's intake")
    tb["intake"], tb["intake_lim"] = f(m, 1), f(m, 2)
    tb["flow"] = f(need(t, r"a forced flow across the inner faces of ([\d.]+) m/s alone would close it", "the flow that closes it"))
    tb["credits"] = f(need(t, r"internal radiation and the floor credited\s+([\d.]+); a forced flow across the inner faces of", "the credits together"))
    m = need(t, r"([\d.]+) h at the line's conductance, up to ([\d.]+) h if the case\s+is as poor as the bound", "the point's duration")
    tb["dur"] = (f(m, 1), f(m, 2))
    if t.count("\n9f THE SMALLEST EXPERIMENT") != 1 or t.count("\n10 THE HEAT-REJECTION QUESTION") != 1 or t.count("\n11 THE THERMAL RECONCILIATION") != 1:
        refuse(3, "L4-E12's sections 9f, 10 and 11")
    s9 = t.split("\n9f THE SMALLEST EXPERIMENT")[1].split("\n10 THE HEAT-REJECTION QUESTION")[0]     # the 21.2 W point (E5's hold)
    s10 = t.split("\n10 THE HEAT-REJECTION QUESTION")[1].split("\n11 THE THERMAL RECONCILIATION")[0]   # the 42.4 W point (withdrawn, section 11)
    band_pat = r"a reading of at least ([\d.]+) W/K \(([\d.]+) K rise\) meets ([\d.]+) W/K: ([^\n]+)"
    tb["bands"] = [(a, b, c, d.strip()) for a, b, c, d in re.findall(band_pat, s9)]
    if [float(x[0]) for x in tb["bands"]] != sorted([float(x[0]) for x in tb["bands"]], reverse=True) or len(tb["bands"]) != 6:
        refuse(3, "L4-E12's acceptance bands")
    need(s9, r"one heater's 21\.2 W spread as the hold spreads it", "the 21.2 W point's heater")
    cb["tb"] = tb
    # the fourth result: L4-E12's heat-rejection comparison (section 15, out 10), check 6: U-02 a closure condition decided by one
    # T-H1 point at the profile's heat; the combined route conditional on its reading; the owner's options if it still reads short
    if not T["l4e12chk6"].startswith("accepted: yes\n"):
        refuse(3, "L4-E12's check 6 is not accepted")
    need(T["l4e12chk6"], r"\*\*Accepted\*\* as U-02's statement: a closure condition", "L4-E12's check 6 verdict")
    hr = {}
    sp = lambda pat: pat.replace(" ", r"\s+")       # the output wraps its prose: a space in these patterns matches any run of white space
    m = need(s10, sp(r"PS-IDLE-SPEC puts ([\d.]+) W into the case lid open \(MODELED: its ([\d.]+) W at the pack"), "the profile's heat (10a)")
    hr["q"], hr["q_pack"] = f(m, 1), f(m, 2)
    hr["g_need"] = f(need(s10, sp(r"Its \+70 C class at REQ-024's \+40 C needs ([\d.]+) W/K;"), "the profile's need (10a)"))
    m = need(s10, sp(r"design day \(the air ([\d.]+) to ([\d.]+) C, the replay\) charging with the profile running \(([\d.]+) W into the case, the balance of 12b\) needs ([\d.]+) to ([\d.]+) W/K"), "charging's need (10a)")
    hr["q_chg"] = f(m, 3)
    hr["day"], hr["g_chg"] = (f(m, 1), f(m, 2)), (f(m, 4), f(m, 5))
    for pat in (r"no vent or opening anywhere \(32\.53\)", r"the Peli 1450 at any cost", r"the face a 3 mm aluminium plate carrying the UI \(32\.40\)"):
        need(s10, sp(pat), "the rulings (10a)")
    m = need(s10, sp(r"\(the plate ([\d.]+) m2 less the monitor window ([\d.]+) m2 and the e-paper lens ([\d.]+) m2: ([\d.]+) m2\)"), "the face's free area (10b)")
    hr["free"] = tuple(f(m, i) for i in range(1, 5))
    m = need(s10, sp(r"\(([\d.]+) mm nominal, ([\d.]+) mm with the unstated allowances doubled\)"), "M3's space (10b)")
    hr["m3"] = (f(m, 1), f(m, 2))
    m = need(s10, sp(r"effective area multiplier (\d+) to (\d+) \(ASSUMPTION"), "the fins' multiplier (10b)")
    hr["k"] = (int(m.group(1)), int(m.group(2)))
    hr["led"] = f(need(s10, sp(r"heat pipes, bars and gap pads, ([\d.]+) W at their pins"), "the loads led into the plate (10b)"))
    m = need(s10, sp(r"the lid's flat ceiling \(([\d.]+) m2, an upper bound: .*?\), ([\d.]+) m tall when open"), "the lid's skin (10b)", re.S)
    hr["lid"] = (f(m, 1), f(m, 2))
    m = need(s10, sp(r"\(([\d.]+) m, (\d+) mm2: ([\d.]+) K/W, ASSUMPTION"), "the braid (10b)")
    hr["braid"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(s10, r"approach\s+\| \+40 C: air, plate, G\s+\| design day ([\d.]+) C: air, G \| ([\d.]+) C: air, G", "the approaches' header (10b)")
    if (f(m, 1), f(m, 2)) != hr["day"]:
        refuse(3, "the approaches' design day is not 10a's")
    rows = re.findall(r"^\s{6}(\S.*?)\s+\|\s+([\d.]+) C\s+([\d.]+) C\s+([\d.]+) W/K \|\s+([\d.]+) C\s+([\d.]+) W/K\s+\|\s+([\d.]+) C\s+([\d.]+) W/K\s*$", s10, re.M)
    keys = ("none", "a2", "a3", "b", "ba", "c", "all")
    if len(rows) != 7 or not (rows[0][0].startswith("none") and rows[6][0].endswith("the best route")):
        refuse(3, "the approaches' table (10b)")
    hr["ap"] = {k: (r[0],) + tuple(r[1:]) for k, r in zip(keys, rows)}
    hr["strap"] = f(need(s10, sp(r"The open lid's strap carries ([\d.]+) W at \+40 C in the best route"), "the strap's heat (10b)"))
    m = need(s10, sp(r"\(a\): about ([\d.]+) kg of ([\d.]+) mm fins at an (\d+) mm pitch"), "the fins' mass (10c)")
    hr["fins"] = (f(m, 1), f(m, 2), f(m, 3))
    hr["lidkg"] = f(need(s10, sp(r"\(c\): about ([\d.]+) kg \(a 1 mm skin"), "the lid's mass (10c)"))
    m = need(s10, sp(r"spreaders and pads under the plate in the ([\d.]+) to ([\d.]+) mm between board B's tall parts and the face parts"), "(b)'s space (10c)")
    hr["gap"] = (f(m, 1), f(m, 2))
    need(s10, sp(r"all three passive: no power, no endurance change, the heat unchanged; costs TBD, no quote held"), "the approaches passive (10c)")
    need(s10, sp(r"the switches go to \+85 C parts"), "the switches (10c)")
    m = need(s10, sp(r"rejects ([\d.]+) W with the air at \+70 C against the profile's ([\d.]+) W, SHORT BY ([\d.]+) W \(([\d.]+) W/K\)"), "the best route's shortfall (10d)")
    hr["best"] = tuple(f(m, i) for i in range(1, 5))
    m = need(s10, sp(r"([\d.]+) and ([\d.]+) W/K short on the design day's cold and warm ends"), "charging's shortfall (10d)")
    hr["chg_short"] = (f(m, 1), f(m, 2))
    m = need(s10, sp(r"On the bound alone the case rejects ([\d.]+) W at \+40 C \(([\d.]+) W short\)"), "the bound alone (10d)")
    hr["bound_only"] = (f(m, 1), f(m, 2))
    m = need(s10, sp(r"\(PS-IDLE, the monitor dimmed and no beacon: ([\d.]+) W into the case, under the best route's ([\d.]+) W by ([\d.]+) W, and nothing fits on the bound alone\)"), "the alternative duty cycle (10d)")
    hr["alt"] = tuple(f(m, i) for i in range(1, 4))
    need(s10, sp(r"a requirement change \(the profile's ambient ceiling, or charging with the profile running on the design day\)"), "the requirement change (10d)")
    need(s10, sp(r"10e U-02 by the owner's exit definition: a CLOSURE CONDITION"), "U-02's class (10e)")
    hr["heaters"] = f(need(s10, sp(r"two heaters \(([\d.]+) W, about the profile's heat\) spread as the boards dissipate, room air, to steady state"), "the 42.4 W point (10e)"))
    hr["thr"] = [(a, b, c, d.strip()) for a, b, c, d in re.findall(band_pat, s10)]
    if len(hr["thr"]) != 3 or [float(x[0]) for x in hr["thr"]] != sorted(float(x[0]) for x in hr["thr"]):
        refuse(3, "L4-E12's thresholds at the profile's heat (10e)")
    if abs(float(hr["thr"][0][2]) - hr["g_need"]) > 5e-4 or (float(hr["thr"][1][2]), float(hr["thr"][2][2])) != hr["g_chg"]:
        refuse(3, "the thresholds' targets are not 10a's needs")
    need(s10, sp(r"Under the first, the route of 10d applies with its kit on the same bench point"), "the route under the first threshold (10e)")
    if abs(float(hr["ap"]["all"][3]) + hr["best"][3] - hr["g_need"]) > 1.5e-3 or abs(hr["q"] - hr["best"][1]) > 1e-9:
        refuse(3, "the best route's shortfall does not add up to the need")
    cb["hr"] = hr
    # the third result: L4-E10's cell route (U-01), check 5
    if not T["l4e10chk5"].startswith("accepted: yes\n"):
        refuse(3, "L4-E10's check 5 is not accepted")
    need(T["l4e10chk5"], r"a supported route exists on published manufacturer evidence", "L4-E10's check 5 verdict")
    t = T["l4e10"]
    u1 = {}
    need(t, r"U-01's class by the owner's exit definition: A SUPPORTED ROUTE EXISTS ON PUBLISHED MANUFACTURER EVIDENCE FOR THE TEMPERATURE WINDOWS \(the Saft MP 176065", "U-01's class")
    need(t, r"NOT YET ADOPTABLE: current and temperature together and the storage\s+dwell and recovery AWAIT Saft or the limited sample qualification \(10g\)", "U-01's adoption (B5)")
    m = need(t, r"Saft MP 176065 xtd \(MAKER, Doc\. n 31109-2-0625\): ([\d.]+) Ah typical .*?, ([\d.]+) V, ([\d.]+) Wh; (\d+) A continuous, (\d+) A pulses", "the Saft sheet")
    u1["sheet"] = tuple(f(m, i) for i in range(1, 6))
    for pat in (r"charge -30 to \+85 C", r"discharge -40 to \+85 C", r"allowable -40 to \+85 C"):
        need(t, pat, "the Saft limits")
    m = need(t, r"energy: ([\d.]+) Wh nominal \(typical\); ([\d.]+) to ([\d.]+) Wh usable, ([\d.]+) to ([\d.]+) h", "the Saft pack's energy")
    u1["energy"] = tuple(f(m, i) for i in range(1, 6))
    m = need(t, r"Along the axis ([\d.]+) mm would remain for wrap and spacers where the 35E block uses ([\d.]+) mm", "the axial fit")
    u1["wrap"] = (f(m, 1), f(m, 2))
    m = need(t, r"NZ\$ ([\d.]+) a cell .*?NZ\$ ([\d.]+) for four", "the Saft cost", re.S)
    u1["cost"] = (f(m, 1), f(m, 2))
    u1["charge_start"] = f(need(t, r"reaches T3's 42 C window only below (-?[\d.]+) C\s+ambient on the bound", "the charge start on the bound"))
    m = need(t, r"LO-01d \(\+55 C, D-02a, TEST-PLAN E3-O\): the cells reach ([\d.]+) to ([\d.]+) C, over \+60 C", "the 35E at E3-O")
    u1["e35_e3o"] = (f(m, 1), f(m, 2))
    u1["e35_e5"] = f(need(t, r"LO-01e \(E5's dwell, SC-03: the idle pack ([\d.]+) C at the conditioned corner\)", "the 35E at E5"))
    u1["room"] = f(need(t, r"The room as designed moves from [\d.]+ L to ([\d.]+) L", "the pocket's room"))
    need(t, r"\(III\)'s E5 route is REJECTED", "approach III's E5 route")
    m = need(t, r"about ten cells, USD ([\d.]+), .*?about (\d+) days for the soaks and (\d+) for the cycles", "the HL18650V soak", re.S)
    u1["soak"] = (f(m, 1), f(m, 2), f(m, 3))
    u1["pulse_cost"] = f(need(t, r"cost: NZ\$ ([\d.]+) a cell \(a distributor's listing archived in January 2025\)", "a Saft cell's cost"))
    need(t, r"10g The limited sample qualification that would substitute for Saft's answer", "the limited sample qualification (B5)")
    need(t, r"Equipment: a chamber from -40 to \+85 C, a 25 A load, a CC/CV source, a logger; about two weeks", "the qualification's equipment")
    need(t, r"Saft's currents 'Can vary depending on temperatures' \(footnote 2\): current at temperature AWAITING \(10g\)", "the Saft's current at temperature (B5)")
    need(T["cl_saft"], r"DRAFT for the owner to send", "the Saft request as a draft")
    cb["u1"] = u1
    # normal operation: the reduced mode's heat, the envelope's top, the case's time constant, the sun's day air
    m = need(T["budget"], r'^PS-RED, lid closed \{"battery_W_plan": ([\d.]+), .*?"heat_inside_plan_W": ([\d.]+)', "the reduced mode's heat")
    cb["red"] = (f(m, 1), f(m, 2))
    cb["env_top"] = f(need(T["l4e12"], r"The envelope's \+(\d+) C, the air 15 K up", "the envelope's top"))
    cb["tau"] = f(need(T["l4e12"], r"time constant ([\d.]+) h\)", "the case's time constant on the bound"))
    m = need(T["replay"], r"over SC-37's hourly air \(([\d.]+) to ([\d.]+) C\)", "the September day's air")
    cb["day_air"] = (f(m, 1), f(m, 2))
    if cb["hr"]["day"] != cb["day_air"] or abs(cb["hr"]["q"] - cb["idle_heat"]) > 0.05:
        refuse(3, "L4-E12's heat-rejection need is not on this record's design day and profile")
    F["cb"] = cb
    F["sv"] = surge_inputs(F, T)
    F["rc"] = reconciliation_inputs(F, T)
    F["fx"] = fixround_inputs(F, T)
    return F, where


def reconciliation_inputs(F, T):
    """The owner's amendment of 2 October 2026, 14:20: L4-E12's thermal reconciliation (its section 16, output section 11; check 7),
    L4-E10's battery comparison (its section 16, output section 11; check 6), the findings ledger's totals and the verification's
    item 5 (R-139's lag)."""
    sp = lambda pat: pat.replace(" ", r"\s+")
    rc = {}
    c7 = T["l4e12chk7"]
    if not c7.startswith("accepted: yes\n"):
        refuse(3, "L4-E12's check 7 is not accepted")
    need(c7, sp(r"So the owner's CFL-002 decides which thermal line the sealed case must meet at \+40 C"), "check 7's dependency")
    rc["k3_near"] = f(need(c7, sp(r"a bench pass line near ([\d.]+) W/K"), "check 7's K3 line"))
    t = T["l4e12"]
    s11 = t.split("\n11 THE THERMAL RECONCILIATION")[1].split("\n12 THE FIX ROUND")[0]
    need(s11, sp(r"REQ-024: \"on measured inside-air \(\+50 C\) and cell \(\+55 C\) temperatures the kit sheds to its reduced mode and then its heat stage \(C1\)\""), "REQ-024's shedding")
    need(s11, sp(r"D-02b: \"above \+35 C ambient the kit runs one module\""), "D-02b")
    need(s11, sp(r"\(an SGP41 above \+55 C fails\)"), "REQ-052's SGP41 line")
    m = need(s11, sp(r"the conductance after it is ([\d.]+) x \(1 - ([\d.]+)\) = ([\d.]+) W/K"), "the withdrawn claim (11a)")
    rc["x2_read"] = (f(m, 1), f(m, 3))
    sk = s11.split("Each condition:")[1].split("CORRECTED in the fix round (12a")[0]
    K = {}
    for blk in re.split(r"\n\s{6}(?=(?:K\d+|X\d)\s)", "\n" + sk.split("\n", 1)[1]):
        blk = " ".join(blk.split())
        if not blk:
            continue
        m = re.match(r"((?:K\d+|X\d))\s+(.*?); lid (open|closed); ([\d.]+) W at \+?(-?[\d.]+) C; (.*); needs ([\d.]+) W/K$", blk)
        if not m:
            refuse(3, "L4-E12 11c's condition %r" % blk[:40])
        K[m.group(1)] = {"what": m.group(2), "lid": m.group(3), "q": float(m.group(4)), "amb": float(m.group(5)), "limit": m.group(6), "need": m.group(7)}
    if sorted(K) != sorted(["K%d" % i for i in range(1, 11)] + ["X1", "X2", "X3"]):
        refuse(3, "L4-E12 11c's conditions")
    rc["K"] = K
    s11e = s11.split("\n11e THE MARGIN")[1].split("\n11f ")[0]
    R = {}
    for k, q, nd, rd, rise, u in re.findall(r"^\s+(K\d+)\s+at ([\d.]+) W: needs ([\d.]+) W/K; a reading of at least ([\d.]+) W/K \(rise ([\d.]+) K, U ([\d.]+) %\)", s11e, re.M):
        R[k] = {"q": float(q), "need": nd, "read": rd, "rise": rise, "u": u}
    if sorted(R) != sorted("K%d" % i for i in range(1, 11)) or any(R[k]["need"] != K[k]["need"] for k in R):
        refuse(3, "L4-E12 11e's readings")
    rc["R"] = R
    s11g = s11.split("\n11g THE PROCEDURE")[1]
    need(s11g, sp(r"the points of 12d \(one per mode's heat and lid state\)"), "the procedure's points (12d)")
    H = {}
    for pts, q, ht, fan in re.findall(r"^\s+(M2, M4, M6 \(K1, K5, K9\)|M1, M3|M7 \(K10\)|M5 \(K6\)|M8, M9 \(K7, K8\))\s+([\d.]+) W: the heaters ([\d.]+) W \(the fans ([\d.]+) W\)", s11g, re.M):
        for k in re.findall(r"[MK]\d+", pts):
            H[k] = (float(q), float(ht), float(fan))
    if sorted(H) != sorted(["M%d" % i for i in range(1, 10)] + ["K1", "K5", "K9", "K10", "K6", "K7", "K8"]):
        refuse(3, "L4-E12 11g's heaters")
    rc["H"] = H
    s11d = s11.split("\n11d THE RELATIONSHIP")[1].split("\n11e ")[0]
    m = need(s11d, sp(r"the bound k plate [\d.]+, walls [\d.]+, whole [\d.]+ W/m2K: A k = ([\d.]+) W/K the coefficients' other ends k plate [\d.]+, walls [\d.]+, whole [\d.]+ W/m2K: A k = ([\d.]+) W/K"), "the bound at K1's rise")
    rc["bound"] = (f(m, 1), f(m, 2))
    m = need(s11d, sp(r"With a 50 m/s inside flow \(a film near 45 W/m2K\) A k reaches ([\d.]+) W/K \(([\d.]+) at the coefficients' other ends\)"), "the 50 m/s figure at K1's rise")
    rc["cap"] = (f(m, 1), f(m, 2))          # NOT the outside capacity (L4-E12 12e corrects it): the bound with a 50 m/s inside flow
    rc["cap_gap"] = f(need(s11d, sp(r"K1's need lies over it at the conservative ends and under it, by ([\d.]+) W/K, at the other ends"), "K1 against that figure"))
    m = need(s11d, sp(r"with the inside resistance at zero it is ([\d.]+) W/K at K1's rise \(([\d.]+) at the optimistic ends with the floor\)"), "the capacity at K1's rise (12e)")
    rc["capk1"] = (f(m, 1), f(m, 2))
    m = need(s11d, sp(r"the operating ambient's conductance is ([\d.]+) to ([\d.]+) % above the room's at the same rise"), "the translation")
    rc["transl"] = (f(m, 1), f(m, 2))
    s11f = s11.split("\n11f ")[1].split("\n11g ")[0]
    need(s11f, sp(r"meets the conductance SCREENS K1, K3, K4 and K9 at the mixed air; it does not close REQ-024, E3-A or E3-O"), "what K1's point meets (screens only)")
    if abs(K["K1"]["q"] - F["e3o_wb"]) > 1e-3 or abs(K["K6"]["q"] - F["cb"]["hr"]["q"]) > 1e-9:
        refuse(3, "L4-E12 11c's heats are not this record's")
    # L4-E10's battery comparison
    c6 = T["l4e10chk6"]
    if not c6.startswith("accepted: yes\n"):
        refuse(3, "L4-E10's check 6 is not accepted")
    need(c6, sp(r"the evidence does not yet support adopting it: the fit mock-up, 18 A for 60 s, Saft's missing figures, the gauge data and T-H1 are AWAITING"), "check 6's verdict")
    need(c6, sp(r"the owner's approval of the cell change and of any purchase is required and is not given"), "check 6's approval line")
    e = T["l4e10"]
    s16 = e.split("== 11. THE BATTERY COMPARISON")[1]
    m = need(s16, sp(r"D-06's 'about 145 Wh' = 12 x ([\d.]+) Ah .*? x ([\d.]+) V = ([\d.]+) Wh \(GUARANTEED inputs\)"), "the 35E's nominal", re.S)
    rc["e35_nom"] = f(m, 3)
    rc["e35_typ"] = f(need(s16, sp(r"The 35E's typical 3\.45 Ah \(Samsung's Technical Report\) gives ([\d.]+) Wh"), "the 35E's typical"))
    rc["saft_nom"] = f(need(s16, sp(r"Saft: 4 x 5\.60 Ah \(typical, C/5 to 2\.5 V at \+25 C\) x 3\.65 V = ([\d.]+) Wh \(GUARANTEED as typical"), "the Saft's nominal"))
    m = need(s16, sp(r"35E 4S3P .*?-> ([\d.]+) Wh, ([\d.]+) h at \+20 C"), "the 35E's usable", re.S)
    rc["e35_use"] = (f(m, 1), f(m, 2))
    rows = re.findall(r"Saft 4S1P, \((a|b)\) same (?:current|C-rate), (assumed minimum|typical)\s.*?-> ([\d.]+) Wh, ([\d.]+) h at \+20 C", s16)
    if len(rows) != 4:
        refuse(3, "L4-E10's Saft rows")
    rc["saft_use"] = (min(float(r[2]) for r in rows), max(float(r[2]) for r in rows), min(float(r[3]) for r in rows), max(float(r[3]) for r in rows))
    rc["cell_tab"] = md_table(T["l4e10md"], "| | Approved pack (D-06) | Saft route (a proposal) |")
    if len(rc["cell_tab"]) < 10 or not all(len(r) == 3 for r in rc["cell_tab"]):
        refuse(3, "L4-E10's comparison table")
    # the findings ledger's totals and its still-open rows; the verification's item 5
    g = T["ledger"]
    m = need(g, r"^\| All \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|$", "the ledger's totals")
    rc["ledger"] = tuple(int(m.group(i)) for i in range(1, 6))
    if rc["ledger"][0] != sum(rc["ledger"][1:]):
        refuse(3, "the ledger's totals do not add up")
    need(g, sp(r"the panel lead's surge \(L4-E7R:1\.6, 2\.4\)"), "the ledger's surge rows")
    need(g, sp(r"the SGP41's shutdown bound \(L4-E12:1\.3, 2\.2\)"), "the ledger's SGP41 rows")
    v = T["verify"]
    m = need(v, sp(r"the lag: ([\d.]+) K/h x (\d+) s = ([\d.]+) K"), "the lag")
    rc["lag"] = (f(m, 1), f(m, 2), f(m, 3))
    rc["tau_max"] = (f(need(v, sp(r"at \+-0\.15 C: the sensor-to-SGP41 time constant at most ([\d.]+) s"), "the break-even at 0.15 C")),
                     f(need(v, sp(r"at \+-0\.20 C: the sensor-to-SGP41 time constant at most ([\d.]+) s"), "the break-even at 0.20 C")))
    need(v, sp(r"item 5 DIFFERS"), "item 5's verdict")
    need(v, sp(r"the TMP117N rows print \+-0\.2 C"), "the N grade")
    return rc


def fixround_inputs(F, T):
    """The fix round of the Layer 4 review (astra-check-l4close-1 at 8fbb68b6, NOT YET on B1 to B7): L4-E12's section 12 (out; its
    page's section 17: B3 the per-mode table, B4 the charging heat as a balance, B7 the battery-only run coupled to C1, the bench
    points and the outside capacity's classes), L4-E11's section 15 (B1 board E's auxiliary domain on VSYS_E, the start bounded, B2
    the battery FET pair, the charger minors) and L4-E10's B5 (read in compute's U-01 lines). Read, never recomputed."""
    sp = lambda pat: pat.replace(" ", r"\s+")
    one = lambda s: " ".join(s.split())
    fx = {}
    t = T["l4e12"]
    if t.count("\n12 THE FIX ROUND OF THE LAYER 4 REVIEW") != 1 or t.count("\n13 Predicates") != 1:
        refuse(3, "L4-E12's section 12")
    s12 = t.split("\n12 THE FIX ROUND OF THE LAYER 4 REVIEW")[1].split("\n13 Predicates")[0]
    need(s12, sp(r"\(astra-check-l4close-1 at 8fbb68b6, the owner's one authorised review: B3, B4 and B7\)"), "the fix round's review")
    s12a = s12.split("\n12a B3, THE SGP41 AND OPTION C, RESTATED.")[1].split("\n12b ")[0]
    a1 = one(s12a)
    for pat in (r"Sensing is supported to \+50 C only; the \+55 C row is an exclusion screen and never stands in for the sensor's function\.",
                r"Option C of CFL-002 \(section 6\) keeps the part and reports its channel as not covered while its reference reads over 49\.0 C",
                r"it switches the sensor off at a 54\.0 C reading, so it is never powered on the \+55 C line",
                r"Section 11's K1 and K5 used the \+55 C row as a line: withdrawn, they are screens \(11c, 11f\)\.",
                r"absolute ratings are listed as screens, never as lines\."):
        need(a1, pat, "12a's statement of the SGP41 and option C")
    m = need(a1, r"reports its channel as not covered while its reference reads over ([\d.]+) C .*? switches the sensor off at a ([\d.]+) C reading", "option C's two readings")
    fx["c_cover"], fx["c_off"] = f(m, 1), f(m, 2)
    fx["film"] = f(need(a1, r"over the pack block's lowest film, ([\d.]+) W/K", "the pack block's film"))
    modes = {}
    parts = re.split(r"\n   (?=M\d )", s12a)
    for blk in parts[1:]:
        b = one(blk.split("\n   CFL-002, restated")[0])
        m = re.match(r"(M\d) (.*?)\. Heat ([\d.]+) W \((.*?)\); \+?(-?[\d.]+) C; lid (open|closed)\. (.*)$", b)
        if not m:
            refuse(3, "L4-E12 12a's mode %r" % b[:30])
        md = {"what": m.group(2), "q": float(m.group(3)), "q_parts": m.group(4), "amb": float(m.group(5)), "lid": m.group(6)}
        body = m.group(7)
        md["lines"] = [(a, b_, c.strip()) for a, b_, c in re.findall(r"(inf|[\d.]+) W/K the air to ([\d.]+) C (.*?)(?= (?:inf|[\d.]+) W/K the air to | every other line)", body)]
        md["rest"] = f(need(body, r"every other line needs at most ([\d.]+) W/K", "%s's other lines" % m.group(1)))
        g = need(body, r"GOVERNING \(the route's measures\): (.*?) As designed \(no route measure; the SGP41 as ruled\): (.*?)\. REMAINING: (.*)$", "%s's governing line" % m.group(1))
        gov, md["designed"], md["remaining"] = g.group(1), g.group(2), g.group(3)
        m2 = re.match(r"as ruled: (.*?), ([\d.]+) W/K, a reading of at least ([\d.]+) W/K; C, A and B: (.*?), ([\d.]+) W/K, a reading of at least ([\d.]+) W/K\.$", gov)
        m3 = re.match(r"every option: (.*?), (no conductance \(the limit at or under the ambient\)|([\d.]+) W/K, a reading of at least ([\d.]+) W/K)\.(?: Without the INFERRED reading \(once the maker states the unpowered range at or over its operating top\): (.*?), ([\d.]+) W/K, a reading of at least ([\d.]+) W/K\.)?$", gov)
        if m2:
            md["ruled"] = (m2.group(1), m2.group(2), m2.group(3))
            md["cab"] = (m2.group(4), m2.group(5), m2.group(6))
        elif m3:
            md["ruled"] = md["cab"] = (m3.group(1), m3.group(3), m3.group(4)) if m3.group(3) else (m3.group(1), None, None)
            md["stated"] = (m3.group(5), m3.group(6), m3.group(7)) if m3.group(5) else None
        else:
            refuse(3, "L4-E12 12a's governing line of %s" % m.group(1))
        md.setdefault("stated", None)
        modes[m.group(1)] = md
    if sorted(modes) != ["M%d" % i for i in range(1, 10)]:
        refuse(3, "L4-E12 12a's modes M1 to M9")
    for k in ("M1", "M2", "M3", "M4"):
        if not modes[k]["ruled"][0].startswith("the SGP41's Table 4") or "hot stop H1" not in modes[k]["cab"][0]:
            refuse(3, "L4-E12 12a: %s's lines are not Table 4 as ruled and H1 under C" % k)
    if modes["M6"]["stated"] is None or modes["M7"]["stated"] is None or modes["M7"]["ruled"][1] is not None:
        refuse(3, "L4-E12 12a: the e-paper's lines of M6 and M7")
    for k, mk in (("H1", "M1"), ("H1", "M2"), ("H1", "M3"), ("H5", "M5")):
        pass
    fx["modes"] = modes
    cf = one(s12a.split("\n   CFL-002, restated with C as defined:")[1].split("\n   What a bench point closes.")[0])
    need(cf, r"C restricts REQ-042's channel inside the envelope, which D-02a does not grant today: CFL-002 stays the owner's\.", "CFL-002 restated")
    wb = one(s12a.split("\n   What a bench point closes.")[1])
    need(wb, r"It closes no mode's functionality", "what a bench point closes")
    need(wb, r"Lid-closed and fans-off states need their own points", "the lid-closed points")
    # 12b, the charging heat as a balance
    s12b = one(s12.split("\n12b B4, THE CHARGING HEAT AS A BALANCE")[1].split("\n12c ")[0])
    m = need(s12b, r"input ([\d.]+) W less stored ([\d.]+) W less exported ([\d.]+) W = ([\d.]+) W of heat, which is the profile's ([\d.]+) W at the battery node, the source path's ([\d.]+) W, the charge path's ([\d.]+) W and the charging cells' ([\d.]+) W", "the charging balance (12b)")
    fx["bal"] = tuple(f(m, i) for i in range(1, 9))
    if abs(fx["bal"][0] - fx["bal"][1] - fx["bal"][2] - fx["bal"][3]) > 1.5e-3 or abs(sum(fx["bal"][4:8]) - fx["bal"][3]) > 1.5e-3:
        refuse(3, "L4-E12 12b's balance does not add up")
    need(s12b, r"the reviewer's 50\.04367 W reproduced", "the reviewer's figure (12b)")
    m = need(s12b, r"L4-E8's ballasts add ([\d.]+) W at their worst corner \(the margins' rule\): ([\d.]+) W", "the charging heat with the ballasts")
    fx["bal_b"] = (f(m, 1), f(m, 2))
    fx["k78"] = [(f(a), float(b), c, d) for a, b, c, d in [(x,) + y for x, *y in []]] if False else \
        [(float(a), float(b), c, d) for a, b, c, d in re.findall(r"\+([\d.]+) C at ([\d.]+) W: needs ([\d.]+) W/K, a reading of at least ([\d.]+) W/K", s12b)]
    if len(fx["k78"]) != 4:
        refuse(3, "L4-E12 12b's K7 and K8")
    m = need(s12b, r"their own ([\d.]+) W over the block's film adding ([\d.]+) to ([\d.]+) K", "T4's local rise (12b)")
    fx["t4_rise"] = (f(m, 2), f(m, 3))
    # 12c, the battery-only run coupled to C1
    s12c = one(s12.split("\n12c B7, THE BATTERY-ONLY RUN COUPLED TO C1")[1].split("\n12d ")[0])
    need(s12c, r"^\(MODELED, energy-and-thermal\)", "12c's label")
    m = need(s12c, r"G ([\d.]+) W/K reaches C1 at ([\d.]+) h and, unshed, the air ([\d.]+) C at ([\d.]+) h; G ([\d.]+) W/K reaches C1 at ([\d.]+) h and, unshed, the air ([\d.]+) C at ([\d.]+) h", "the reviewer's constant-G check (12c)")
    fx["cg"] = tuple(f(m, i) for i in range(1, 9))
    runs = re.findall(r"(the bound|the coefficients' other ends) C ([\d.]+) kJ/K: (?:C1 at ([\d.]+) h, then the heat stage for ([\d.]+) h|C1 not reached); the run ([\d.]+) h; the air at most ([\d.]+) C, the cells at most ([\d.]+) C \(H1 at 56\.5 C not reached\)", s12c)
    if len(runs) != 4:
        refuse(3, "L4-E12 12c's four runs")
    fx["runs"] = runs
    m = need(s12c, r"C1 sheds the profile from ([\d.]+) to ([\d.]+) h where it acts, and the runtime with the shed states is ([\d.]+) to ([\d.]+) h, of which ([\d.]+) to ([\d.]+) h unshed; where C1 does not act, the profile runs its ([\d.]+) h\.", "the coupled run's result (12c)")
    fx["c1"] = tuple(f(m, i) for i in range(1, 8))
    m = need(s12c, r"unshed only from a constant ([\d.]+) W/K at C 8 kJ/K \(([\d.]+) W/K at 10 kJ/K\), and for any duration from K6's ([\d.]+) W/K", "the unshed conductance (12c)")
    fx["unshed"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(s12c, r"ENERGY ONLY: ([\d.]+) h \(([\d.]+) Wh at ([\d.]+) W\) stays labelled energy-only; it is not an established unshed PS-IDLE-SPEC endurance\.", "the energy-only label (12c)")
    fx["eonly"] = (f(m, 1), f(m, 2), f(m, 3))
    need(s12c, r"No hot stop on the bound\.", "no hot stop (12c)")
    m = need(s12c, r"stepped to the profile's heat less the fans' draw \(([\d.]+) W\) and, when the mixed air has risen (\d+) K, to the heat stage's battery-only heat less the fans' draw \(([\d.]+) W\)", "the transient point (12c)")
    fx["trans"] = (f(m, 1), f(m, 2), f(m, 3))
    need(s12c, r"a battery-only PS-IDLE-SPEC run from a 24 h soak at \+20 C, lid open, shaded, still air", "the built kit's run (12c)")
    # 12d, the bench points
    s12d = s12.split("\n12d THE BENCH POINTS")[1].split("\n12e ")[0]
    pts = []
    for blk in re.split(r"\n      (?=M\d)", s12d)[1:]:
        b = one(blk.split("\n   Then the fans-off case")[0])
        m = re.match(r"(M\d(?: and M\d)?) at ([\d.]+) W, lid (open|closed): (.*?); tau ([\d.]+) h, steady at ([\d.]+) h, the fit's three time constants ([\d.]+) h$", b)
        if not m:
            refuse(3, "L4-E12 12d's point %r" % b[:30])
        pts.append((m.group(1), float(m.group(2)), m.group(3), m.group(4), m.group(5), m.group(6), m.group(7)))
    if [p_[0] for p_ in pts] != ["M2 and M6", "M1", "M4", "M3", "M7", "M5", "M8 and M9"]:
        refuse(3, "L4-E12 12d's points")
    fx["pts"] = pts
    need(one(s12d), r"Then the fans-off case at M2's heat \(no pass line: the failure case\) and 12c's transient point\.", "the fans-off and transient points (12d)")
    # 12e, the outside capacity and the classes
    s12e = one(s12.split("\n12e THE OUTSIDE CAPACITY")[1])
    m = need(s12e, r"CORRECTION: section 9's 'cap' \(([\d.]+) W/K at E5's rise, ([\d.]+) at E3-O's\) is the bound with a 50 m/s inside flow, whose film is near 45 W/m2K; the capacity proper at those rises is ([\d.]+) and ([\d.]+) W/K on the conservative ends\.", "the capacity's correction (12e)")
    fx["capfix"] = tuple(f(m, i) for i in range(1, 5))
    cls = []
    for row in re.findall(r"(M\d), lid (open|closed), \+?(-?[\d.]+) C(?:, rise ([\d.]+) K)?: (.*?)(?= M\d, lid | The class \(iii\) lines)", s12e):
        mm = re.match(r"(.*?) needs ([\d.]+) W/K; capacity bare ([\d.]+) / ([\d.]+), with the route ([\d.]+) / ([\d.]+) W/K \(conservative / optimistic\): class \((i+)\)(.*)$", row[4])
        if mm:
            short = re.search(r"SHORT by ([\d.]+) W/K, ([\d.]+) W", mm.group(8))
            cons = re.search(r"\((i+)\) at the conservative ends", mm.group(8))
            cls.append({"mode": row[0], "lid": row[1], "amb": float(row[2]), "rise": row[3], "line": mm.group(1).strip(), "need": mm.group(2),
                        "bare": (mm.group(3), mm.group(4)), "route": (mm.group(5), mm.group(6)), "cls": mm.group(7), "cons": cons.group(1) if cons else mm.group(7),
                        "short": (short.group(1), short.group(2)) if short else None})
        else:
            mm = re.match(r"(.*?) at or under the ambient: no capacity at a zero rise; class \((i+)\), the whole ([\d.]+) W short$", row[4])
            if not mm:
                refuse(3, "L4-E12 12e's class row %r" % row[4][:40])
            cls.append({"mode": row[0], "lid": row[1], "amb": float(row[2]), "rise": None, "line": mm.group(1).strip(), "need": None, "bare": None, "route": None,
                        "cls": mm.group(2), "cons": mm.group(2), "short": (None, mm.group(3))})
    if len(cls) != 17:
        refuse(3, "L4-E12 12e's seventeen class rows")
    fx["cls"] = cls
    iii = [c for c in cls if c["cls"] == "iii"]
    if [c["mode"] for c in iii] != ["M3", "M4", "M6", "M7"]:
        refuse(3, "L4-E12 12e's class (iii) lines")
    fx["iii"] = iii
    m = need(s12e, r"the bay air holds Table 4's \+50 C lid closed only to an ambient of \+([\d.]+) to \+([\d.]+) C on the pack and \+([\d.]+) to \+([\d.]+) C on shore", "the VOC ceilings (12e)")
    fx["voc_ceil"] = tuple(f(m, i) for i in range(1, 5))
    m = need(s12e, r"at the bound's plate fraction ([\d.]+) it needs ([\d.]+) W/K and at W4's high fraction ([\d.]+) it needs ([\d.]+) W/K, both under the route's optimistic capacity, so the measured fraction decides", "the e-paper's window (12e)")
    fx["plate"] = tuple(f(m, i) for i in range(1, 5))
    m = need(s12e, r"charging only in the heat stage \(([\d.]+) W into the case\) would need ([\d.]+) and ([\d.]+) W/K at T4's line, class \(i\) at both ends", "charging in the heat stage (12e)")
    fx["chg_hs"] = (f(m, 1), f(m, 2), f(m, 3))
    for pat in (r"\(1\) E3-L at \+40 C with the lid closed as ruled \(M3 on the pack, M4 on shore\)", r"Options: CFL-002's C, A or B \(the owner's\)",
                r"a closed-lid ceiling on REQ-042's VOC channel \(a requirement change, the owner's", r"D-02b's closed-lid test at \+40 C restated \(a ruling change, the owner's\)",
                r"a closed-lid conduction path from the plate to the lid's inner face inside the seal \(the session's to develop at Layer 7; not modelled here, so it closes nothing yet\)",
                r"\(2\) E3-O at \+55 C \(M6\)", r"Options: PDi's storage statement \(the request is drafted in clarification/pervasive-displays-e2370ks0c1\.txt; sending it is the owner's\)",
                r"an e-paper with a held range at or over \+70 C \(CHO-001, the owner's\)", r"E3-O run with the e-paper's state as a recorded deviation \(TEST-PLAN's owner\)",
                r"\(3\) E5's \+60 C dwell \(M7\)", r"a different e-paper \(CHO-001, the owner's\)", r"E5 run with the e-paper out as a recorded deviation \(TEST-PLAN's owner\)",
                r"Charging \(M8, M9\) is not class \(iii\)"):
        need(s12e, pat, "12e's class (iii) options")
    # L4-E11's section 15
    t = T["l4e11"]
    if t.count("\n15. THE FIX ROUND FOR THE CONSOLIDATION REVIEW") != 1:
        refuse(3, "L4-E11's section 15")
    s15 = t.split("\n15. THE FIX ROUND FOR THE CONSOLIDATION REVIEW")[1].split("\nEND.")[0]
    a = one(s15.split("15a. B1:")[1].split("15b.")[0])
    for pat in (r"board A's J_DOCK pin 1 from GND to VBAT \(VSYS\), board E's J_BLK pin 1 to a new net VSYS_E, and U12's VIN and EN, C31, the fans' supply pins and D7 and D8 on VSYS_E",
                r"so no kit load is fed from the pack while the source carries it"):
        need(a, pat, "board E's feed (15a)")
    m = need(a, r"the contact: one 813 on pin 1, ([\d.]+) A declared, [\d.]+ % of its ([\d.]+) A", "the dock's pin 1")
    fx["aux_a"], fx["c813"] = f(m, 1), f(m, 2)
    m = need(a, r"VSYS_E's range: the supplement floor ([\d.]+) V to ([\d.]+) V", "VSYS_E's range")
    fx["vsys_rng"] = (f(m, 1), f(m, 2))
    m = need(a, r"the bounded drains total ([\d.]+) mA, and the bench reads the held pack current at most (\d+) mA \(E11-31's acceptance", "the held pack current")
    fx["held"] = (f(m, 1), f(m, 2))
    m = need(a, r"the pack monitor R42 \+ R43 \(122 kOhm at -1 %\): ([\d.]+) mA at ([\d.]+) V, intended", "the pack monitor")
    fx["mon"] = (f(m, 1), f(m, 2))
    m = need(a, r"7 x 813 ground, one open: ([\d.]+) A each, ([\d.]+) % of 3\.5 A, ([\d.]+) C at the 51 C air", "seven ground contacts, one open")
    fx["gnd7"] = (f(m, 1), f(m, 2), f(m, 3))
    need(a, r"the source-only sequence \(the pack absent or both its FETs open\)", "the source-only sequence (15a)")
    need(a, r"the held sequence: the flag set writes CHRG_INHIBIT 1; the battery FET turns off as the charge stops \(p\.38\); VSYS moves to VSRN \+ 150 mV; nothing on either board moves", "the held sequence (15a)")
    b = one(s15.split("15b.")[1].split("15c.")[0])
    need(b, r"the 502\.3 ms of 12c withdrawn: 0\.5 A is an input ceiling, not a delivered current", "the start's withdrawn figure (15b)")
    fx["latch_s"] = f(need(b, r"so on held evidence the start ends in VSYS_MIN or in a latch within ([\d.]+) s, never undefined", "the start's bound (15b)"))
    c = one(s15.split("15c.")[1].split("15d.")[0])
    m = need(c, r"SELECTED \(SESSION\): Nexperia BUK6Y10-30P, two in parallel, Q39 and Q40 \(LCSC (C\d+), (\d+) in stock, ([\d.]+) USD each at 10\)", "the FET pair (15c)")
    fx["pair"] = (m.group(1), int(m.group(2)), f(m, 3))
    qc = c.split("(Q-c) Nexperia BUK6Y10-30P")[1].split("SELECTED")[0]
    m = need(qc, r"the bar at 70 C air: ([\d.]+) C/W per FET, set by OCD2 24 A for 1 s after 20 A held the bar at 62\.1 C air: ([\d.]+) C/W per FET", "the pair's bar (15c)")
    fx["bar"] = (f(m, 1), f(m, 2))
    fx["rds"] = f(need(qc, r"gate factor [\d.]+, ([\d.]+) mOhm per FET", "the pair's RDS(on) bound"))
    qa = c.split("(Q-a) AOS AONS21357")[1].split("(Q-b)")[0]
    fx["qa_hot"] = f(need(qa, r"printed maxima: [\d.]+ mOhm at -10 V and 25 C, ([\d.]+) mOhm at -10 V and 125 C", "the AONS21357's hot row (Q-a)"))
    fx["qa_bar"] = f(need(qa, r"the bar at 70 C air: ([\d.]+) C/W per FET", "the AONS21357's bar (Q-a)"))
    m = need(c, r"its envelope at the bar, \+70 C air: TJ at most 150 C for every event of 15c; 18 A for 60 s after 10 A held: ([\d.]+) C", "the pair's envelope")
    fx["svc_tj"] = f(m, 1)
    m = need(c, r"the docking pulse: all of it in one FET at 25 C: ([\d.]+) A against ISM (\d+) A .*? met for a share of at most ([\d.]+) in one FET", "the docking pulse on the pair")
    fx["dock"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(c, r"the precharge in LDO mode with R17's 1 %: ([\d.]+) A at most .*? so R-b' allows no charge under ([\d.]+) V on SRN", "the precharge (15c)")
    fx["pre"] = (f(m, 1), f(m, 2))
    m = need(c, r"on battery at PS-IDLE-SPEC, ([\d.]+) A: ([\d.]+) W in the pair, ([\d.]+) % of the pack's output", "the pair at the profile")
    fx["pair_idle"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(c, r"on battery at PS-TYP, ([\d.]+) A: ([\d.]+) W in the pair", "the pair at PS-TYP")
    fx["pair_typ"] = (f(m, 1), f(m, 2))
    m = need(c, r"L2 with the pair: VSYS in supplement ([\d.]+) V .*?, ([\d.]+) A, peak ([\d.]+) A against Isat ([\d.]+) A", "L2 with the pair")
    fx["l2"] = tuple(f(m, i) for i in range(1, 5))
    d = one(s15.split("15d.")[1])
    m = need(d, r"SRN under ([\d.]+) V: LDO mode, VSYS at least ([\d.]+) V; SRN over ([\d.]+) V: VSRN \+ 150 mV within \+-2 %; between, either, so at least ([\d.]+) V", "the piecewise acceptance (15d)")
    fx["pw"] = tuple(f(m, i) for i in range(1, 5))
    need(d, r"is an assumed reading of TI's malformed maximum column \(A11-18\), not a printed limit", "the upper side's assumption (15d)")
    m = need(d, r"with the source overloaded VSYS follows the pack through the battery FETs and R17: ([\d.]+) V at CELL_FUSED's ([\d.]+) V and OCD1's (\d+) A; with no pack and an overloaded source there is no floor, R-c sheds", "the supplement floor (15d)")
    fx["supp"] = (f(m, 1), f(m, 2), f(m, 3))
    if fx["supp"][0] != fx["vsys_rng"][0] or fx["l2"][0] != fx["supp"][0]:
        refuse(3, "L4-E11 15's supplement floor differs between its sections")
    md = T["l4e11md"]
    e15 = md.split("### 15e. The texts drafted for L4-E9's record")[1].split("\nNot claimed:")[0]
    fx["e15"] = [tuple(x.strip() for x in r) for r in md_table(e15, "| Where | Now | Drafted |")]
    if len(fx["e15"]) != 8:
        refuse(3, "L4-E11 15e's drafted texts")
    return fx


def surge_inputs(F, T):
    """L4-E7's derivation of the panel lead's surge and sustained over-voltage (L4E7-CONTROL-DECISION.md, 'The panel lead's
    surge and sustained over-voltage, derived'; its output's section THE PANEL LEAD'S DISTURBANCES, DERIVED), set 27 at
    6d76453e; its SMCJ36A row checked against the held sheet. The remedies are L4-E7's to design (the owner's amendment of
    2 October 2026, 14:20): this record reads them as named and selects neither."""
    t = T["l4e7r"]
    if t.count("THE PANEL LEAD'S DISTURBANCES, DERIVED") != 1 or t.count("\n   THE BACKSTOP UNDER CS101 (") != 1:
        refuse(3, "L4-E7's panel-lead derivation is not in its output")
    if t.count("\n   THE SOLAR-FAULT REMEDIES (") != 1:
        refuse(3, "L4-E7's solar-fault remedies are not in its output")
    s = t.split("THE PANEL LEAD'S DISTURBANCES, DERIVED")[1].split("\n   THE SOLAR-FAULT REMEDIES (")[0]
    rs = t.split("\n   THE SOLAR-FAULT REMEDIES (")[1].split("\n   THE BACKSTOP UNDER CS101 (")[0]
    sp = lambda pat: pat.replace(" ", r"\s+")
    sv = {}
    for pat in (r"REQ-063 commits the kit's EMC characterisation to MIL-STD-461G \(11 December 2015\) and the 'Ground, Army' row of its Table V",
                r"CS116 A \(5\.14,", r"CS115 A \(5\.13,", r"CS117 S \(5\.15,", r"TEST-PLAN\.md runs M1 to M5 and no row runs CS115, CS116 or CS117",
                r"The alternative that also closes D5 is an input over-voltage and reverse disconnect ahead of PV_P",
                r"the residual beyond the basis: a direct or nearer strike", r"the kit's posture there is REQ-041's mast-down alarm",
                r"the sheet's typical failure mode is a short, which F2 then clears"):
        need(s, sp(pat), "L4-E7's basis")
    m = need(s, sp(r"a1solar's (\d+) m one way of (\d+) mm2 copper \(array_calc\.py, ESTIMATE\), ([\d.]+) Ohm in loop"), "the lead")
    sv["lead"] = (f(m, 1), f(m, 2), f(m, 3))
    sv["qwave"] = f(need(s, sp(r"The lead's quarter wave is ([\d.]+) MHz in free space"), "the lead's quarter wave"))
    m = need(s, sp(r"THE VERDICTS \(each against REQ-016's criterion on the drafted entry, (\d+) V; as drawn the lowest limit on PV_P is C11 and C12, (\d+) V\)"), "the limits")
    sv["lim"], sv["lim_drawn"] = f(m, 1), f(m, 2)
    m = need(s, sp(r"- D1, CS116, PV_IN and the cable: D4 at the disturbance's current ([\d.]+) V \((\d+) A, hot end\), D4 off in the loaded network: MEETS; as drawn, NOT MET"), "D1's verdict")
    sv["d1"] = (f(m, 1), f(m, 2))
    m = need(s, sp(r"- D2, CS115, the cable: D4 at the disturbance's current ([\d.]+) V \((\d+) A, hot end\), D4 off in the loaded network: CONDITIONAL: the loop current under ([\d.]+) A \(U5's bound\); as drawn, NOT MET"), "D2's verdict")
    sv["d2"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(s, sp(r"U5's rating is reached at ([\d.]+) A with the whole current through R59 \(the bound\) and at (\d+) A in the loaded network; D4's clamp reaches the drafted entry's (\d+) V at ([\d.]+) A"), "D2's currents")
    sv["d2_i"] = (f(m, 1), f(m, 2), f(m, 4))
    m = need(s, sp(r"- D3, the panel's cold open circuit: (\d+) V, under D4's (\d+) V standoff: MEETS \(CONDITIONAL on PANEL-ACC\)"), "D3's verdict")
    sv["d3"] = (f(m, 1), f(m, 2))
    rows = re.findall(r"the (least|highest) part (at the cold end|at 25 C|at the junction's maximum)\s+breakdown ([\d.]+) V:\s+([\d.]+) A,\s+([\d.]+) W", s)
    if len(rows) != 4:
        refuse(3, "L4-E7's 36 V rows")
    sv["d4_rows"] = [("the %s part %s" % (a, b), float(v), float(i), float(w)) for a, b, v, i, w in rows]
    m = need(s, sp(r"is ([\d.]+) W at the hot end's air and ([\d.]+) W at the cold end's"), "D4's capability on the board")
    sv["d4_cap"] = (f(m, 1), f(m, 2))
    m = need(s, sp(r"- D4, a 36 V source on the port: D4 conducts ([\d.]+) to ([\d.]+) A: NOT MET on the drafted entry: remedied below"), "D4's verdict")
    sv["d4_a"] = (f(m, 1), f(m, 2))
    sv["d4_cold"] = f(need(s, sp(r"The largest sustained source the drafted entry holds is D4's least breakdown at the cold end, ([\d.]+) V"), "the largest sustained source"))
    m = need(s, sp(r"the kit's declared source range, (\d+) to (\d+) V \(V2-SPEC line 21\)"), "the declared source range")
    sv["src"] = (f(m, 1), f(m, 2))
    m = need(s, sp(r"D5: D4's forward path carries ([\d.]+) A held; on the board it can dissipate ([\d.]+) W at the hot end, so it holds only below a forward drop of ([\d.]+) V"), "D5")
    sv["d5"] = (f(m, 1), f(m, 2), f(m, 3))
    need(s, sp(r"- D5, a reversed panel \(E-N1\): D4 forward, [\d.]+ A held: NOT MET on the drafted entry: remedied below"), "D5's verdict")
    m = need(s, sp(r"SMCJ36A \(VR ([\d.]+) V, VBR ([\d.]+) to ([\d.]+) V, ([\d.]+) V at the cold end; VC ([\d.]+) V at ([\d.]+) A\)"), "SMCJ36A")
    sv["s36"] = tuple(f(m, i) for i in range(1, 7))
    sm = F["SMCJ36A"]
    if (sm["vr"], sm["vbr_min"], sm["vbr_max"], sm["vc"], sm["ipp"]) != (sv["s36"][0], sv["s36"][1], sv["s36"][2], sv["s36"][4], sv["s36"][5]):
        refuse(3, "L4-E7's SMCJ36A row is not the held sheet's")
    m = need(s, sp(r"plateau puts its clamp at ([\d.]+) V at 25 C and ([\d.]+) V at the hot end"), "SMCJ36A's clamp at CS116's plateau")
    sv["s36_clamp"] = (f(m, 1), f(m, 2))
    m = need(s, sp(r"the 50 V parts are reached at ([\d.]+) A \(25 C\) and ([\d.]+) A \(hot end\), Q3's (\d+) V at ([\d.]+) A"), "the 50 V parts under SMCJ36A")
    sv["s36_50"] = (f(m, 1), f(m, 2), f(m, 3), f(m, 4))
    m = need(s, sp(r"EEHZA1J220XP \((\d+) uF (\d+) V in the same .*?\), which takes the bulk ahead of the bank from (\d+) uF to (\d+) uF and so re-opens the CS101 correction"), "(i)'s bulk", re.S)
    sv["bulk"] = (f(m, 1), f(m, 2), f(m, 3), f(m, 4))
    m = need(s, sp(r"the regulation's ([\d.]+) W to the trip's ([\d.]+) W at 36 V, outside REQ-016's window \(a single fault for layer 8\)"), "(i)'s stage at 36 V")
    sv["stage36"] = (f(m, 1), f(m, 2))
    m = need(s, sp(r"R-156's text names the INA250's (\d+) V, and the drafted U18 is the INA169 \((\d+) V\)"), "R-156's correction")
    sv["u18"] = (f(m, 1), f(m, 2))
    need(s, sp(r"a TEST row owed at layer 8: CS116 on PV_IN alone and on the J_SOLAR cable at the six frequencies and the lead's 15\.0 MHz, and CS115 on the cable, recording the cable's peak current"), "the test row")
    need(s, sp(r"at 0\.01, 0\.1, 1, 10, 30 and 100 MHz and the lead's 15\.0 MHz"), "CS116's frequencies")
    if sv["u18"][1] != F["u18_vin"]:
        refuse(3, "L4-E7's U18 rating is not this record's")
    # the solar-fault remedies (L4-E7's check 5 at 573fd5b8; the drafted guard apply_gen_sch_e_solar_guard.py)
    c5 = T["l4e7chk5"]
    if not c5.startswith("accepted: yes\n"):
        refuse(3, "L4-E7's check 5 is not accepted")
    need(c5, sp(r"both single faults have a selected remedy with a bounded analysis that MEETS"), "check 5's verdict")
    rm = {}
    need(rs, sp(r"\(3\) SELECTED \(SESSION\): one remedy for each fault"), "the selection")
    for pat in (r"\(1\) The TPS48110-Q1 alone driving back-to-back FETs", r"\(2\) The LM74700-Q1 ideal diode ahead of the TPS48110-Q1"):
        need(rs, sp(pat), "the remedies not taken")
    m = need(rs, sp(r"SMCJ30A \(VR ([\d.]+) V, VBR ([\d.]+) to ([\d.]+) V, ([\d.]+) V at the cold end; VC ([\d.]+) V at ([\d.]+) A\)"), "SMCJ30A")
    rm["s30"] = tuple(f(m, i) for i in range(1, 7))
    m = need(rs, sp(r"puts the cut-off at ([\d.]+) to ([\d.]+) V rising and ([\d.]+) to ([\d.]+) V falling, aged \(([\d.]+) to ([\d.]+) V new\): ([\d.]+) V over CS101's peak, ([\d.]+) V under the clamp, ([\d.]+) V over 25 V on the fall"), "the cut-off's band")
    rm["rise"], rm["fall"], rm["new"] = (f(m, 1), f(m, 2)), (f(m, 3), f(m, 4)), (f(m, 5), f(m, 6))
    rm["marg"] = (f(m, 7), f(m, 8), f(m, 9))
    m = need(rs, sp(r"the SMCJ30A clamps D1's 10 A plateau at ([\d.]+) V at the hot end and D2's 5 A at ([\d.]+) V"), "the SMCJ30A under CS116 and CS115")
    rm["d1d2"] = (f(m, 1), f(m, 2))
    for pat in (r"J_SOLAR\.2 becomes PV_RTN", r"D11 SMCJ40CA \(C80273\) across PV_F and PV_RTN",
                r"C131 and C132, two 10 uF 100 V X7R 1210 \(board E's C8 part text\), on PV_F", r"RISCP R89 3\.01k with C126 330 pF C0G 100 V",
                r"INP R96 100k over R97 30\.0k", r"C133 and C134, two 10 uF 50 V ceramics \(C13's part text and land\), on PV_P beside the bulk \(B6\)",
                r"U21 TPS48110AQDGXRQ1 \(C17556513\) with R87 4\.5 mOhm", r"Q12 CSD19532Q5B \(C473333\) from PV_SNS to PV_P",
                r"the OV divider R98, R99 and R100", r"Q13 CSD19532Q5B \(C473333\) from PV_RTN to GND", r"D12 BZT52C12-7-F \(C124196\)",
                r"D4 to SMCJ30A, its LCSC code owed", r"\(this record's hold, input limit and backstop, L4-E9's hot swap, L4-E11's entry\): 7 edits",
                r"Q12 holds 36 V of 100 V", r"MEETS, CONDITIONAL on Q13's leakage above 25 C",
                r"note E-N1 is closed", r"no protection here extends the permitted range"):
        need(rs, sp(pat), "the remedies' text")
    rm["divider"] = need(rs, sp(r"the divider (R98 90\.9k \+ R99 95\.3k over R100 7\.68k)"), "the OV divider").group(1)
    rm["t_off"] = f(need(rs, sp(r"since a pulse over the cut-off turns the block off within ([\d.]+) us"), "the turn-off"))
    m = need(rs, sp(r"([\d.]+) W at the regulation's highest ([\d.]+) A and ([\d.]+) W at the trip's highest ([\d.]+) A"), "the block's loss")
    rm["loss"] = tuple(f(m, i) for i in range(1, 5))
    m = need(rs, sp(r"on SC-37's day ([\d.]+) Wh of ([\d.]+) Wh \(([\d.]+) %\), on the bright day ([\d.]+) Wh of ([\d.]+) Wh"), "the block's energy")
    rm["day"] = tuple(f(m, i) for i in range(1, 6))
    m = need(rs, sp(r"U21 turns on at ([\d.]+) V at the most \(INP through R96 over R97 30\.0k .*?\) and off at ([\d.]+) V at the least"), "U21's UVLO", re.S)
    rm["uvlo"] = (f(m, 1), f(m, 2))
    m = need(rs, sp(r"([\d.]+) W \(([\d.]+) W without it\)"), "the static bound with the block")
    rm["static"] = (f(m, 1), f(m, 2))
    rm["resid"] = f(need(rs, sp(r"runs the stage under the backstop's current trip, at most ([\d.]+) W at the cut-off's highest"), "the residual"))
    m = need(rs, sp(r"the filtered peak ([\d.]+) A at (\d+) Hz .*? against the margin ([\d.]+) A"), "CS101 re-run", re.S)
    rm["cs101"] = (f(m, 1), int(m.group(2)), f(m, 3))
    m = need(rs, sp(r"the response allowance ([\d.]+) ms against 10 times the typical sum \(([\d.]+) ms\), the accepted ([\d.]+) ms"), "check (b) re-run")
    rm["chkb"] = (f(m, 1), f(m, 2), f(m, 3))
    rm["q13"] = (f(need(rs, sp(r"while Q13 leaks under ([\d.]+) uA"), "Q13's leakage bound")), f(need(rs, sp(r"against ([\d.]+) uA printed at 80 V and 25 C"), "Q13's printed leakage")))
    rm["d11"] = f(need(rs, sp(r"D11's own rating, ([\d.]+) A at 10/1000 us"), "D11's rating"))
    for pat in (r"D4\s+a stiff 36 V source, connected cold\s+MEETS\n", r"D5\s+a reversed panel\s+MEETS \(CONDITIONAL on Q13's leakage above 25 C\)",
                r"CS116/115 on\s+CS116 and CS115 with the block on\s+MEETS", r"CS116/115 off\s+CS116 and CS115 with the block off\s+MEETS",
                r"window\s+the window kept\s+MEETS"):
        need(rs, pat, "the remedies' verdicts")
    need(rs, sp(r"already on\s+a stiff 36 V source with the guard on \(B6\)\s+MEETS \(CONDITIONAL on the lead's loop inductance at least 2\.47 uH, R-176\)"), "B6's verdict")
    need(rs, sp(r"CS116/115 on\s+CS116 and CS115 with the block on\s+MEETS \(CS115 CONDITIONAL on R-174"), "CS115's condition with the block on")
    # B6 of the consolidation review: the guard already on (L4-E7 at 11339ec7, its output's THE GUARD ALREADY ON)
    if rs.count("- THE GUARD ALREADY ON (B6") != 1:
        refuse(3, "L4-E7's B6 section")
    ga = rs.split("- THE GUARD ALREADY ON (B6")[1].split("THE VERDICTS, with the remedies:")[0]
    one = lambda x: " ".join(x.split())
    b6 = {}
    b6["l_uh"] = f(need(ga, sp(r"AT ([\d.]+) uH, the worst over every start and corner"), "B6's inductance"))
    rat = re.findall(r"^\s+- (.+?)\s{2,}(-?[\d.]+) (of|against)\s+(-?[\d.]+), margin\s+([\d.]+); holds from (under )?([\d.]+) uH", ga, re.M)
    if len(rat) != 11:
        refuse(3, "B6's rating rows")
    b6["rows"] = [(n.strip(), float(w), float(l), float(mg), ("under " if u else "") + h) for n, w, _o, l, mg, u, h in rat]
    need(ga, r"D4's current, A \(SMCJ30A, least, cold end\)\s+none", "B6's D4 row")
    g1 = one(ga)
    m = need(g1, r"THE BINDING RATING: (.*?), at ([\d.]+) uH: two conductors whose centres stay at least ([\d.]+) mm apart over the (\d+) m", "B6's binding rating")
    b6["bind"], b6["mm"], b6["len_m"] = m.group(1), f(m, 3), f(m, 4)
    if f(m, 2) != b6["l_uh"]:
        refuse(3, "B6's binding inductance")
    m = need(g1, r"Below it the guard does not hold: at ([\d.]+) uH \(([\d.]+) mm apart\) .*? \(NOT MET\)", "B6's NOT MET below it")
    b6["below"] = (f(m, 1), f(m, 2))
    m = need(g1, r"at most ([\d.]+) of it, ([\d.]+) A at the turn-off", "Q12 in B6")
    b6["q12"] = (f(m, 1), f(m, 2))
    m = need(g1, r"Q13 in the third quadrant carries the lead's ([\d.]+) A at most, ([\d.]+) of its derated chart", "Q13 in B6")
    b6["q13"] = (f(m, 1), f(m, 2))
    m = need(g1, r"D11 at most ([\d.]+) A and ([\d.]+) mJ against ([\d.]+) mJ", "D11 in B6")
    b6["d11"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(g1, r"the closest TRK_VS comes to D4 is ([\d.]+) V at ([\d.]+) V/us .*?, ([\d.]+) V under its least breakdown at the cold end; D4 carries no current at any rate; U5 at most ([\d.]+) V", "B6's ramps")
    b6["ramp"] = (f(m, 1), f(m, 2), f(m, 3), f(m, 4))
    m = need(g1, r"THE COLD CONNECTION .*?: PV_F at most ([\d.]+) V, its slew ([\d.]+) V/us, INP ([\d.]+) V, EN/UVLO ([\d.]+) V; the ring through Q13's body diode at most ([\d.]+) A", "B6's cold connection")
    b6["cold"] = tuple(f(m, i) for i in range(1, 6))
    m = need(g1, r"as drafted in the remedies round \(C131 1 uF, R97 39k, CSCP 1 nF, no C133 and C134\): PV_F .*? ([\d.]+) of 100, PV_F's slew .*? ([\d.]+) of 60, U21's INP .*? ([\d.]+) of 20, U5's CSPIN to CSNIN, positive ([\d.]+) of 0\.3;", "the guard as drafted (B6)")
    b6["drafted"] = tuple(f(m, i) for i in range(1, 5))
    m = need(g1, r"The start: Q12 carries at most ([\d.]+) A into every capacitor behind it at the gate's fastest slew, under U21's overcurrent least ([\d.]+) A", "the start (B6)")
    b6["start"] = (f(m, 1), f(m, 2))
    m = need(one(rs), r"Q12 turns off at most ([\d.]+) A within ([\d.]+) us, PV_F reaches at most ([\d.]+) V \(slew ([\d.]+) V/us of 60\), PV_P ([\d.]+) V, TRK_VS ([\d.]+) V", "B6 in the bounded analysis")
    b6["sum"] = tuple(f(m, i) for i in range(1, 7))
    reg = one(rs.split("FOR L4-E9'S REGISTER")[1])
    m = need(reg, r"D-12: (CS116 MEETS with the block on and off; CS115 MEETS with the block off and, with it on, is CONDITIONAL on R-174 \(the cable's recorded loop current under [\d.]+ A, or U5's differential measured under [\d.]+ V); U5 reads ([\d.]+) V at CS115's 5 A calibration level", "D-12's text for L4-E9")
    b6["d12"] = m.group(1) + ")."
    b6["u5_cs115"] = f(m, 2)
    rows = re.findall(r"\((\d)\) (.*?)(?= \(\d\) |$)", reg.split("R-176's bench rows, REVISED: ")[1])
    if [r[0] for r in rows] != [str(i) for i in range(1, 8)]:
        refuse(3, "R-176's seven rows")
    b6["r176"] = [r[1].rstrip(";").strip() for r in rows]
    need(reg, r"D-10's source arriving with the guard on is bounded \(B6\) and CONDITIONAL on the lead's loop inductance at least 2\.47 uH", "D-10's condition (B6)")
    rm["b6"] = b6
    need(rs, sp(r"Owed with it: D4's LCSC code, U21's DGX-19 land, the regeneration and its gates, and R-176's bench rows, REVISED"), "what is owed")
    if not os.path.exists(os.path.join(TOP, PINS["e7guard"][0])):
        refuse(3, "the drafted guard is not in the tree")
    need(T["e7guard"], r"RELEASE", "the guard's release record")
    sv["rm"] = rm
    return sv


# ----------------------------------------------------------------------------------------------- the derived figures
def derived(F):
    D = {}
    vrev = F["vin_raw_e"]["v_work"]                                   # REQ-015's 36 V as board E declares VIN_RAW's work voltage
    D["vrev"] = vrev
    D["dcp_backfeed"] = F["trk_ceiling"][2] - VF_BACKFEED              # TRK_OUT's raised ceiling, through U4/Q2, L2 and Q7's body diode
    D["dcp_backfeed_drawn"] = F["trk_drawn"][2] - VF_BACKFEED
    D["q1_rev"] = D["dcp_backfeed"] + vrev
    D["q1_rev_drawn"] = D["dcp_backfeed_drawn"] + vrev
    # F1's bound: the kit's own cable (the external pair and the inside lead), copper alone, at REQ-024's cold end
    r20 = 2 * F["cable_m"] * CU_RHO_20C / F["cable_mm2"] + 2 * (F["lead_mm"] / 1000.0) * CU_RHO_20C / AWG18_MM2
    rc = r20 * (1 + CU_ALPHA * (T_COLD - 20.0))
    D["f1_v"] = F["ovlo_sel"][2]       # the highest steady input the selected entry admits (R23 6.42k, 0.1 %)
    D["f1_r20"], D["f1_rcold"] = r20, rc
    D["f1_ipf"] = D["f1_v"] / rc
    # the front end's VIN_RAW current at the onset of the average limit (L4-E6's boundary), the largest over 9 to 36 V
    D["vin_fault"] = F["r11_8"][2] * F["vbus_max_r11"] / (F["eta_fe"] * F["avg_from"])
    D["vin_fault_7"] = F["r11_7"][2] * F["vbus_max_r11"] / (F["eta_fe"] * F["avg_from"])
    # solar at the window: the tracker's output current at H3's lowest settle point
    D["trk_out_w"] = 100.0 * F["trk"]["efficiency"]
    D["trk_i_settle"] = D["trk_out_w"] / F["settle_865"][1]
    # U3's delivered power at VBAT
    D["vbat_avail_min"] = F["u3_min"] * F["bus_low"] * F["eta_u3"]
    D["vbat_avail_max"] = F["u3_max_board"] * F["vbus_band"][1] * F["eta_u3"]
    D["vbat_win"] = F["win_w"] * F["eta_u3"]
    D["vbat_at_9"] = (F["u3_at_9"] * F["bus_low"] * F["eta_u3"], F["h3"][9.0][0] * F["vbus_band"][1] * F["eta_u3"])
    D["vbat_at_12"] = F["h3"][12.0][0] * F["vbus_band"][1] * F["eta_u3"]
    D["vbat_at_24"] = F["h3"][24.0][0] * F["vbus_band"][1] * F["eta_u3"]
    D["entry_9v_vbat"] = F["entry_lim"][0] * 9.0 * F["eta_fe"] * F["eta_u3"]
    # the pack opening while charging: L2's energy at the converter's stop (SYSOVP maximum) into VBAT's capacitance
    l2 = 4.7e-6 * (1 + L2_TOL)
    p_in = F["u3_max_board"] * F["vbus_band"][1]
    i_out = p_in / F["batovp"]
    fsw_min = 340e3                                              # SLUSE66A 8.5 FSW at the 400 kHz setting, its minimum (FW-A17, V-A05)
    lmin = 4.7e-6 * (1 - L2_TOL)
    d = F["batovp"] / F["vbus_band"][1]
    ripple = (F["vbus_band"][1] - F["batovp"]) * d / (lmin * fsw_min)
    i_pk = i_out + ripple / 2.0
    e = 0.5 * l2 * i_pk ** 2
    n, cnom = F["vbat_caps"]
    ceff = cnom * BIAS_KEEP * 1e-6
    v0 = F["sysovp"][2]
    D["pack_open"] = {"i_pk": i_pk, "e_mj": e * 1e3, "c_nom_uf": cnom, "n": n, "c_eff_uf": ceff * 1e6,
                      "v_end": math.sqrt(v0 ** 2 + 2 * e / ceff), "c_need_uf": 2 * e / (F["tps2596_abs"] ** 2 - v0 ** 2) * 1e6}
    D["pack_open"]["keep_need"] = D["pack_open"]["c_need_uf"] / cnom
    # HF-F02's resolution: the PoE stage's input current at the pack's lowest stack (CUV), the shunt that keeps the INA226 in range
    vlow = 4 * F["cuv"]
    i_in = F["poe"]["peak"] * F["poe"]["volts"] / (F["poe"]["efficiency"] * vlow)
    D["poe_in"] = i_in
    D["poe_shunt_max_mohm"] = F["ina_fs_mv"] / i_in
    D["poe_shunt_mv"] = 5.0 * i_in     # R227 5 mOhm (part A)
    D["vbat_low"] = vlow
    return D


# ------------------------------------------------------------------------------------------- part A: Q1, F1 and U17
def source_only(F, D):
    """B4: what the BQ25731 sheet and the charger state record establish about a source with no usable pack."""
    t = subprocess.run(["pdftotext", "-layout", os.path.join(TOP, PINS["bq25731"][0]), "-"], capture_output=True).stdout.decode("utf-8", "replace")
    out = {}
    out["conv"] = need(t, r"Corresponding the default value of ChargeVoltage register .*?\n\s*•\s+(Converter powers up)\.", "9.3.1 converter powers up", re.S).group(1)
    out["nobatt"] = need(t, r"(\d-cell without battery)", "the power-up figures without battery").group(1)
    need(t, r"system load keeps increasing after the charge current drops down to zero, the\s+system\s+voltage starts to drop", "9.3.17 DPM")
    out["clamp_ma"] = f(need(t, r"VSYS_MIN\) then the charge current is clamped at (\d+) mA", "9.6.2.1 clamp"))
    cs = _C_TEXT["chgseq"]
    m = need(cs, r"input limit about ([\d.]+) to ([\d.]+) A at 20 V \(about (\d+) W into VSYS\)", "the host-free input limit")
    out["hostfree"] = "about %s to %s A at the 20 V bus, about %s W into VSYS" % (m.group(1), m.group(2), m.group(3))
    m = need(cs, r"\| Q-TI-2, Q-TI-3 \|.*?\| (prepared in `REVIEW-REQUEST.md`, not sent) \|", "Q-TI-3's state")
    out["qti3"] = m.group(1).replace("`", "")
    return out


def soa_lines():
    """CSD19532Q5B Figure 10 (SLPS414B p.6), the maximum safe operating area, read from the sheet's own vector drawing
    (pdftocairo -svg, the page as TI drew it) rather than by eye: the plot frame spans 0.1 to 1000 V and 0.1 to 10000 A
    (the axis labels), each line is identified by its colour against the legend, whose labels pdftotext reads in the
    legend's own row and column order. Two consistency checks refuse a misread: the IDM boundary must sit at 400 A and
    every pulse line must end at 100 V. Returns {label: [(log10 V, log10 A), ...]}."""
    pdf = os.path.join(TOP, PINS["csd19532"][0])
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
    frames = [pts for col, pts in paths if col == "rgb(0%,0%,0%)" and len(pts) == 5 and pts[0] == pts[-1]]
    if not frames:
        refuse(3, "Figure 10's frame")
    fr = max(frames, key=lambda q: (max(a for a, _ in q) - min(a for a, _ in q)) * (max(b for _, b in q) - min(b for _, b in q)))
    x0, x1 = min(q[0] for q in fr), max(q[0] for q in fr)
    y0, y1 = min(q[1] for q in fr), max(q[1] for q in fr)
    lv = lambda x: -1.0 + 4.0 * (x - x0) / (x1 - x0)
    li = lambda y: -1.0 + 5.0 * (y - y0) / (y1 - y0)
    idm = [pts for col, pts in paths if col == "rgb(0%,0%,0%)" and len(pts) == 3]
    if not idm or abs(10 ** li(idm[0][0][1]) - 400.0) > 4.0 or abs(10 ** lv(idm[0][1][0]) - 100.0) > 1.0:
        refuse(3, "Figure 10's IDM and 100 V boundary do not read 400 A and 100 V")
    txt = subprocess.run(["pdftotext", "-f", "6", "-l", "6", "-layout", pdf, "-"], capture_output=True).stdout.decode("utf-8", "replace")
    rows = [re.findall(r"(10us|100us|1ms|10ms|DC)\b", ln) for ln in txt.splitlines() if re.search(r"\b(10us|100us)\b", ln)]
    if len(rows) != 2:
        refuse(3, "Figure 10's legend")
    legend = sorted(((pts[0][1], pts[0][0], col) for col, pts in paths if len(pts) == 2 and pts[0][1] == pts[1][1]
                     and col not in ("rgb(0%,0%,0%)",) and 100 < pts[1][0] - pts[0][0] < 150 and pts[0][1] > 1200), key=lambda q: (-q[0], q[1]))
    labels = rows[0] + rows[1]
    if len(legend) < len(labels):
        refuse(3, "Figure 10's legend segments")
    out = {}
    for lab, (_y, _x, col) in zip(labels, legend):
        cands = [pts for c, pts in paths if c == col and len(pts) >= 3 and abs(10 ** lv(pts[-1][0]) - 100.0) < 1.0]
        if len(cands) != 1:
            refuse(3, "Figure 10's %s line" % lab)
        out[lab] = [(lv(x), li(y)) for x, y in cands[0]]
    return out


def soa_at(line, vds):
    lx = math.log10(vds)
    for (xa, ya), (xb, yb) in zip(line, line[1:]):
        if xa <= lx <= xb:
            return 10 ** (ya + (yb - ya) * (lx - xa) / (xb - xa))
    refuse(3, "Figure 10 has no line segment at %s V" % vds)


def partA(F, D, T):
    """The three datasheet-backed proposals. Every figure is read from the makers' sheets (pinned) or the records'
    outputs, except the constants named at the top (figure readings and two assumptions)."""
    A = {}
    flat = lambda t: re.sub(r"\s+", " ", t)
    # ---- the makers' rows
    c1 = flat(subprocess.run(["pdftotext", "-f", "1", "-l", "1", os.path.join(TOP, PINS["csd19532"][0]), "-"], capture_output=True).stdout.decode())
    m = need(c1, r"Gate-to-Source Voltage ±(\d+) V", "CSD19532Q5B VGS")
    A["vgs_max"] = f(m)
    m = need(c1, r"Continuous Drain Current (\d+) Pulsed Drain Current\(2\) (\d+) Power Dissipation\(1\) ([\d.]+)", "CSD19532Q5B ID, IDM, PD")
    A["id_cont"], A["idm"], A["pd"] = f(m, 1), f(m, 2), f(m, 3)
    A["tj_max"] = f(need(c1, r"Storage Temperature Range .55 to (\d+)", "CSD19532Q5B TJ"))
    A["eas"] = f(need(c1, r"ID = 74 A, L = 0\.1 mH, RG = 25 [\u2126\u03a9] (\d+) mJ", "CSD19532Q5B EAS"))
    c3 = pdf_text("csd19532", 3)
    m = need(c3, r"VGS\(th\)\s+Gate-to-Source Threshold Voltage\s+VDS = VGS, ID = 250 μA\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "CSD19532Q5B Vth")
    A["vth"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(c3, r"VGS = 10 V, ID = 17 A\s+([\d.]+)\s+([\d.]+)\s+m[\u2126\u03a9]", "CSD19532Q5B RDS(on) at 10 V")
    A["rds10"] = (f(m, 1), f(m, 2))
    m = need(c3, r"ISD = 17 A, VGS = 0 V\s+([\d.]+)\s+([\d.]+)\s+V", "CSD19532Q5B VSD")
    A["vsd_max"] = f(m, 2)
    A["rja"] = f(need(c3, r"Junction-to-Ambient Thermal Resistance \(1\) \(2\)\s+(\d+)", "CSD19532Q5B RthetaJA max"))
    m = need(c3, r"Gate Charge Total \(10 V\)\s+([\d.]+)\s+([\d.]+)\s+nC", "CSD19532Q5B Qg")
    A["qg_max"] = f(m, 2)
    l7 = pdf_text("lm74700")
    m = need(l7, r"Charge pump turn on voltage\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "LM74700 charge pump on")
    A["cp_on_min"] = f(m, 1)
    m = need(l7, r"Charge pump turn off voltage\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "LM74700 charge pump off")
    A["cp_off_max"] = f(m, 3)
    A["gate_src_min_ma"] = f(need(l7, r"Peak source current\s+(\d+)\s+\d+\s+mA", "LM74700 peak gate source current"))
    m = need(l7, r"ENTDLY\s+V\(VCAP\) > V\(VCAP UVLOR\)\s+(\d+)\s+(\d+)\s+µs", "LM74700 ENTDLY")
    A["entdly_max_us"] = f(m, 2)
    m = need(l7, r"tReverse delay\s+([\d.]+)\s+([\d.]+)\s+µs", "LM74700 reverse turn-off")
    A["trev_max_us"] = f(m, 2)
    need(l7, r"MOSFET with 15-V minimum VGS should be selected", "LM74700 VGS guidance")
    A["gate_rec"] = 15.0
    need(l7, r"gate threshold voltage Vth of 2-V to 2\.5-V", "LM74700 Vth guidance")
    A["vth_rec_max"] = 2.5
    need(l7, r"\(20 mV / ILoad\(Nominal\)\) ≤ RDS\(ON\) ≤ \( 50 mV / ILoad\(Nominal\)\)", "LM74700 RDS guidance")
    A["rds_guide_mv"] = (20.0, 50.0)
    l69 = pdf_text("lm5069")
    m = need(l69, r"PWRLIM-1\s+Power limit sense voltage\s+SENSE-OUT = 48 V, RPWR = 150 k[\u2126\u03a9]\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "LM5069 PWRLIM-1")
    A["pwrlim"] = (f(m, 1), f(m, 2), f(m, 3))
    need(l69, r"R PWR\s+1\.30 u 10 5 u R SNS \(PLIM 1\.18mV u", "LM5069 Equation 9")
    A["eq9"] = (1.30e5, 1.18e-3)
    m = need(l69, r"VCB\s+Threshold voltage\s+VIN to SENSE\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "LM5069 VCB")
    A["vcb_max"] = f(m, 3)
    A["tcb_max"] = f(need(l69, r"tCB\s+Response time\s+[\d.]+\s+([\d.]+)\s+µs", "LM5069 tCB"))
    A["ovlo_del_us"] = f(need(l69, r"OVLODEL\s+OVLO delay\s+Delay to GATE low\s+(\d+)", "LM5069 OVLO delay"), 1) if re.search(r"OVLODEL\s+OVLO delay\s+Delay to GATE low\s+(\d+)", l69) else \
        f(need(l69, r"Delay to GATE high\s+\d+\s+µs\s+OVLODEL\s+OVLO delay\s+Delay to GATE low\s+(\d+)", "LM5069 OVLO delay"))
    A["restart_duty"] = f(need(l69, r"DCFAULT\s+Fault restart duty cycle\s+LM5069-2 only\s+([\d.]+)%", "LM5069 restart duty")) / 100.0
    gE = Gen(T["gen_e"])
    A["rpwr"] = float(re.match(r"([\d.]+)k", gE.value("R24")).group(1)) * 1e3
    A["rs"] = float(re.match(r"([\d.]+)mOhm", gE.value("R19")).group(1)) * 1e-3
    fz = pdf_text("fuse997")
    A["f_v"] = f(need(fz, r"Voltage Rating:\s+(\d+) V DC", "0997 voltage rating"))
    A["f_int"] = f(need(fz, r"Interrupting Rating:\s+(\d+) A @ 58 V DC", "0997 interrupting rating"))
    need(fz, r"Same blade size and pitch as", "0997 blade size")
    m = need(fz, r"0997010_\s+10\s+1\s+(\d+)\s+([\d.]+)\s+(\d+)", "0997 10 A row")
    A["f_r_cold_mohm"], A["f_i2t"] = f(m, 2), f(m, 3)
    amb = [float(x) for x in re.findall(r"(-?\d+) °C", need(fz, r"(-40 °C\s+-20 °C\s+0 °C\s+20 °C\s+40 °C\s+60 °C\s+80 °C\s+100 °C)", "0997 derating columns").group(1))]
    row = [float(x) for x in need(fz, r"\n\s+10A\s+((?:[\d.]+\s+){7}[\d.]+)", "0997 10 A derating row").group(1).split()]
    A["f_amb"], A["f_der"] = amb, row
    tc = {}
    for pct in (110, 135, 200, 350, 600):
        mm = re.search(r"^\s*%d\s+(\d+(?:\.\d+)?(?: \d{3})?)\s*/\s*(\d+(?:\.\d+)?|-)\s*$" % pct, fz, re.M)
        if not mm:
            refuse(3, "0997 time-current row %d %%" % pct)
        tc[pct] = (float(mm.group(1).replace(" ", "")), None if mm.group(2) == "-" else float(mm.group(2)))
    A["f_tc"] = tc
    ks = flat(subprocess.run(["pdftotext", "-raw", os.path.join(TOP, PINS["keystone"][0]), "-"], capture_output=True).stdout.decode())
    need(ks, r"CAT\. NO\. 3568", "Keystone 3568")
    need(ks, r"For Littelfuse Mini 297 or 997 series/Bussmann ATM series or equivalent", "Keystone MINI holder text")
    ina = pdf_text("ina226")
    m = need(ina, r"Shunt offset voltage, RTI\(2\)\s+±([\d.]+)\s+±([\d.]+)\s+μV", "INA226 VOS")
    A["ina_vos_uv"] = f(m, 2)
    m = need(ina, r"Shunt voltage gain error\s+([\d.]+)%\s+([\d.]+)%", "INA226 gain error")
    A["ina_gain"] = f(m, 2) / 100.0
    need(ina, r"the bus voltage can be present with the supply\s+voltage off", "INA226 supply independence")
    need(ina, r"0\.00512", "INA226 Equation 1")
    A["ina_cal_k"] = 0.00512
    tv = flat(subprocess.run(["pdftotext", "-raw", os.path.join(TOP, PINS["smcj"][0]), "-"], capture_output=True).stdout.decode())
    m = need(tv, r"VBR @ TJ ?= VBR ?@25°C x \(1\+αT x \(TJ - 25\)\) \(αT:Temperature Coefficient, typical value is ([\d.]+)%\)", "SMCJ VBR temperature coefficient")
    A["tvs_alpha"] = f(m) / 100.0
    m = need(pdf_text("lm5176"), r"VCS\(BUCK\)\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "LM5176 VCS(BUCK)")
    A["vcs_buck_max"] = f(m, 3) * 1e-3
    # ---- the records' figures used here
    s120 = T["s120"]
    m = need(s120, r"boost mode, peak limit \((\d+) \+ ([\d.]+)\) mV", "LM5176 VCS(BOOST) maximum and the CS offset")
    A["vcs_boost_max"], A["cs_off"] = f(m, 1) * 1e-3, f(m, 2) * 1e-3
    A["poe_rcs"] = float(need(T["gen_a"], r'isns="20m", rcs="(\d+)m", bias="VBAT"', "U16's CS resistor").group(1)) * 1e-3
    l8 = T["l4e8"]
    m = need(l8, r"THE BALLAST \(MAKER, the HoJLR2512 sheet p\.2\): (\d+) W, derated from (\d+) C to zero at (\d+) C", "HoJLR2512 rating")
    A["hojlr"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(T["l4e4"], r"CHOSEN: R138 5 mOhm, HoJLR2512-3W-5mR-1%, LCSC (C\d+) \(Milliohm.*?\n.*?p\.2 TCR \+-(\d+) ppm/K", "R138's part and TCR", re.S)
    A["r5_lcsc"], A["r5_tcr"] = m.group(1), f(m, 2) * 1e-6
    A["r5_span_k"] = f(need(T["l4e4"], r"-20 C to the ASSUMED 100 C \((\d+) K from 25 C\)", "the shunt's temperature span"))
    r7 = T["l4e7r"]
    m = need(r7, r"curve 2 \(sources of (\d+) V or below\): 126 dBuV, ([\d.]+)\s+V rms", "CS101 curve 2")
    A["cs101_src_v"], A["cs101_vrms"] = f(m, 1), f(m, 2)
    m = need(T["s120"], r"OVLO ([\d.]+) / ([\d.]+) / ([\d.]+) V \(OVLOTH ([\d.]+) / ([\d.]+) / ([\d.]+) V", "the OVLO band and its threshold")
    A["ovloth"] = (f(m, 4), f(m, 5), f(m, 6))
    gE2 = Gen(T["gen_e"])
    A["r22_k"] = float(re.match(r"([\d.]+)k", gE2.value("R22")).group(1))
    A["r23_k"] = float(re.match(r"([\d.]+)k", gE2.value("R23")).group(1))
    A["cs114_ma"] = f(need(r7, r"curve 4's 103 dBuA \((\d+) mA rms", "CS114 curve 4"))

    # ---- Q1
    i_hi = F["entry_lim"][1]
    A["q1_p"] = i_hi ** 2 * A["rds10"][1] * 1e-3 * CSD_RDS_NORM_150C
    A["q1_tj"] = F["air"][1] + A["q1_p"] * A["rja"]
    t_on = A["entdly_max_us"] * 1e-6 + A["qg_max"] * 1e-9 / (A["gate_src_min_ma"] * 1e-3)
    A["q1_inrush_s"], A["q1_inrush_mj"] = t_on, i_hi * A["vsd_max"] * t_on * 1e3
    A["q1_rev"] = D["q1_rev"]
    A["cs101_pk"] = A["cs101_vrms"] * math.sqrt(2)
    A["cs101_top"] = D["vrev"] + A["cs101_pk"]
    A["cs101_top_src"] = A["cs101_src_v"] + A["cs101_pk"]
    ovlo = lambda th, r23, lo, tol=0.01: th * (1 + A["r22_k"] * (1 - tol if lo else 1 + tol) / (r23 * (1 + tol if lo else 1 - tol)))
    A["ovlo_check"] = (ovlo(A["ovloth"][0], A["r23_k"], True), ovlo(A["ovloth"][2], A["r23_k"], False))
    sm = F["SMCJ40A"]["vbr_min"]
    A["r23_win"] = (A["r22_k"] * 1.01 / (0.99 * (sm / A["ovloth"][2] - 1)), A["r22_k"] * 0.99 / (1.01 * (A["cs101_top"] / A["ovloth"][0] - 1)))
    A["r23_e192"] = R23_NEW_K
    A["ovlo_e192"] = (ovlo(A["ovloth"][0], A["r23_e192"], True), ovlo(A["ovloth"][2], A["r23_e192"], False))
    A["ovlo_new"] = (ovlo(A["ovloth"][0], A["r23_e192"], True, 0.001), ovlo(A["ovloth"][2], A["r23_e192"], False, 0.001))
    A["d10_cold_vbr"] = sm * (1 + A["tvs_alpha"] * (T_COLD - 25.0))
    A["cs114_pk"] = A["cs114_ma"] * 1e-3 * math.sqrt(2) / (2 * math.pi * 10e3 * 1e-6)
    A["m7_vds"] = D["vrev"] + F["ef1_dv"][1]
    sm40 = F["SMCJ40A"]
    A["cap_neg_vds"] = D["vrev"] + sm40["vc"]
    A["cap_dcp_ld_limit"] = F["ld_ca_abs"] - sm40["vc"]
    A["cap_dcp_q1_limit"] = F["csd19532_vds"] - sm40["vc"]
    A["cap_energy_mj"] = 0.5 * F["vin_uf"] * 1e-6 * D["vrev"] ** 2 * 1e3
    plim = lambda vds: A["rpwr"] / (A["eq9"][0] * A["rs"]) + A["eq9"][1] * vds / A["rs"]
    A["plim36"], A["plim_ovlo"] = plim(D["vrev"]), plim(F["ovlo_sel"][2])
    A["plim_hi"] = A["plim_ovlo"] * PWRLIM_SPREAD
    A["soa_36_w"] = CSD_SOA_10MS_36V_A * D["vrev"]
    A["soa_hot_w"] = A["soa_36_w"] * (A["tj_max"] - SOA_TC_HOT) / (A["tj_max"] - 25.0)
    A["cb_a"] = A["vcb_max"] * 1e-3 / A["rs"]
    A["dcp_short_s"] = A["f_i2t"] / D["f1_ipf"] ** 2
    inom = F["h3"][9.0][1]
    A["rds_guide"] = (A["rds_guide_mv"][0] / inom, A["rds_guide_mv"][1] / inom)
    A["rds_at_tj"] = A["rds10"][0] * (1 + (CSD_RDS_NORM_150C - 1) * (A["q1_tj"] - 25.0) / 125.0)
    # ---- F1
    A["f1_ipf_by_v"] = [(v, v / D["f1_rcold"]) for v in (9.0, 12.0, 24.0, D["vrev"], D["f1_v"])]
    col = [x for x in A["f_amb"] if x >= F["air"][1]][0]
    A["f_col"], A["f_allow"] = col, A["f_der"][A["f_amb"].index(col)]
    A["f_startup_i2t"] = i_hi ** 2 * F["timer_ms"][2] * 1e-3
    r_hot = D["f1_r20"] * (1 + CU_ALPHA * (F["air"][1] - 20.0))
    A["f_min_fault_9v"] = 9.0 / r_hot
    # ---- U17 at the PoE stage's input on 5 mOhm (R227)
    rsh = 0.005
    A["u17_rsh"] = rsh
    A["u17_in_norm"] = D["poe_in"]
    A["u17_mv_norm"] = D["poe_in"] * rsh * 1.01 * 1e3
    A["u17_fault_a"] = (A["vcs_boost_max"] + A["cs_off"]) / (A["poe_rcs"] * 0.99)
    A["u17_mv_fault"] = A["u17_fault_a"] * rsh * 1.01 * 1e3
    A["u17_p_fault"] = A["u17_fault_a"] ** 2 * rsh * 1.01
    A["u17_buck_valley_a"] = (A["vcs_buck_max"] + A["cs_off"]) / (A["poe_rcs"] * 0.99)
    A["hojlr_avail"] = A["hojlr"][0] if F["air"][1] <= A["hojlr"][1] else A["hojlr"][0] * (A["hojlr"][2] - F["air"][1]) / (A["hojlr"][2] - A["hojlr"][1])
    A["u17_fs_a"] = F["ina_fs_mv"] * 1e-3 / rsh
    A["u17_lsb"] = A["u17_fs_a"] / 32768.0
    A["u17_cal"] = A["ina_cal_k"] / (A["u17_lsb"] * rsh)
    A["u17_err_pct"] = (A["ina_gain"] + 0.01 + A["r5_tcr"] * A["r5_span_k"]) * 100.0
    A["u17_off_ma"] = A["ina_vos_uv"] * 1e-6 / rsh * 1e3
    # ---- fix round, minor: the INA226's drift rows (SBOS547C p.5) over the IC's range, -20 C to the hottest inside air the record holds
    m = need(ina, r"Shunt offset voltage, RTI\(2\) vs\s+.40°C ≤ TA ≤ 125°C\s+([\d.]+)\s+([\d.]+)\s+μV/°C", "INA226 offset drift")
    A["ina_vos_drift"] = f(m, 2)
    A["ina_gain_drift"] = f(need(ina, r"Shunt voltage gain error vs temperature\s+.40°C ≤ TA ≤ 125°C\s+\d+\s+(\d+)\s+ppm/°C", "INA226 gain drift")) * 1e-6
    A["t_hot"] = max(F["air"][1], F["corner_air"][1] + F["ballast_w"] / F["th1"])
    A["ic_dt"] = max(25.0 - T_COLD, A["t_hot"] - 25.0)
    A["u17_err_drift_pct"] = A["u17_err_pct"] + A["ina_gain_drift"] * A["ic_dt"] * 100.0
    A["u17_off_drift_ma"] = (A["ina_vos_uv"] + A["ina_vos_drift"] * A["ic_dt"]) * 1e-6 / rsh * 1e3
    A["u17_drift_m20"] = (A["ina_gain_drift"] * (25.0 - T_COLD) * 100.0, A["ina_vos_drift"] * (25.0 - T_COLD) * 1e-6 / rsh * 1e3)

    # ---- fix round B1: Q7's power limit at the selected OVLO maximum and the complete hot-short pulse against Figure 10
    vmax = F["ovlo_sel"][2]
    m = need(T["gen_e"], r'r\("R19", "10mOhm (\d+)% 2512', "R19's tolerance")
    rs_tol = f(m) / 100.0
    vsns = lambda rpwr, vds: rpwr / (A["eq9"][0] * vds) + A["eq9"][1]          # Equation 7 with Equation 9: PLIM x RSNS / VDS
    A["vsns_drawn"] = vsns(A["rpwr"], vmax)
    A["vsns_new_low"] = vsns(R24_NEW_K * 1e3 * (1 - R24_TOL), vmax)
    A["vsns_new_nom"] = vsns(R24_NEW_K * 1e3, vmax)
    need(l69, r"a VSNS of less than 5 mV is not recommended", "LM5069 5 mV guidance")
    A["vsns_min"] = 5e-3
    A["rpwr_min"] = A["eq9"][0] * (A["vsns_min"] - A["eq9"][1]) * vmax
    plim_c = lambda rpwr, rsn, vds: rpwr / (A["eq9"][0] * rsn) + A["eq9"][1] * vds / rsn
    A["plim_new_hi"] = plim_c(R24_NEW_K * 1e3 * (1 + R24_TOL), A["rs"] * (1 - rs_tol), vmax)
    A["plim_new_nom"] = plim_c(R24_NEW_K * 1e3, A["rs"], vmax)
    A["pulse_w"] = A["plim_new_hi"] * TI_SOA_MARGIN
    A["pulse_a"] = A["pulse_w"] / vmax
    A["tflt_max"] = F["timer_ms"][2] * 1e-3
    lines = soa_lines()
    A["soa_labels"] = sorted(lines)
    i10, i1, i10u = soa_at(lines["10ms"], vmax), soa_at(lines["1ms"], vmax), soa_at(lines["10us"], vmax)
    mexp = math.log(i1 / i10) / math.log(10.0)                     # SNVS452G Equations 15 to 18: I_SOA = a t^-m between 1 and 10 ms
    A["soa_10ms"], A["soa_1ms"], A["soa_10us"], A["soa_m"] = i10, i1, i10u, mexp
    A["soa_tflt_25"] = i10 * (10e-3 / A["tflt_max"]) ** mexp
    A["tc_max"] = A["t_hot"] + A["q1_p"] * A["rja"]                # Q7 is the part Q1 is: its case at most its junction at the entry's 6.15 A
    A["soa_derate"] = (A["tj_max"] - A["tc_max"]) / (A["tj_max"] - 25.0)   # SNVS452G Equation 19
    A["soa_tflt_hot"] = A["soa_tflt_25"] * A["soa_derate"]
    A["soa_tflt_hot_w"] = A["soa_tflt_hot"] * vmax
    A["cb_10us_hot"] = i10u * A["soa_derate"]
    A["soa_36_line"] = soa_at(lines["10ms"], 36.0)
    # final round (the recheck's B1): the breaker's threshold at R19's corner, and the timer's component envelope
    A["cb_thr"] = A["vcb_max"] * 1e-3 / (A["rs"] * (1 - rs_tol))
    ya = pdf_text("yageo")
    need(ya, r"K = ± 10%", "Yageo K tolerance")
    A["c_tol"] = 0.10
    A["c_temp"] = f(need(ya, r"Maximum capacitance change as a function of temperature\s*\n\s*\(temperature characteristic/coefficient\):\s+± (\d+)%", "X7R temperature characteristic")) / 100.0
    A["c_endur"] = f(need(ya, r"Endurance\s+IEC 60384-.*?X7R: ± (\d+)%", "X7R endurance change", re.S)) / 100.0
    lc = _C_TEXT["lcsc"]
    A["c5_code"] = need(lc, r'\(r"\^100n", "C_0603"\): "(C\d+)"', "C5's fill mapping").group(1)
    need(T["gen_e"], r"YAGEO CC0603KRX7R9BB104, LCSC %s" % A["c5_code"], "C5's part")
    hi_f = (1 + A["c_tol"]) * (1 + A["c_temp"]) * (1 + A["c_endur"])
    lo_f = (1 - A["c_tol"]) * (1 - A["c_temp"]) * (1 - A["c_endur"])
    A["c_hi_f"], A["c_lo_f"] = hi_f, lo_f
    A["tflt_k_only"] = F["timer_ms"][2] * (1 + A["c_tol"])
    A["tflt_env"] = (F["timer_ms"][0] * lo_f, F["timer_ms"][2] * hi_f)
    A["tfault_us"] = f(need(l69, r"tFAULT\s+Fault to GATE low delay\s+TIMER pin reaches 4 V\s+(\d+)\s+µs", "LM5069 tFAULT"))
    A["soa_tenv_25"] = i10 * (10e-3 / (A["tflt_env"][1] * 1e-3)) ** mexp
    A["soa_tenv_hot"] = A["soa_tenv_25"] * A["soa_derate"]
    A["soa_extrap"] = A["tflt_env"][1] / 10.0 - 1.0
    # the start into VIN_RAW (SNVS452G Equation 12), the capacitance on VIN_RAW from L4-E5's list (TRK_OUT's sit behind U4)
    m = need(T["l4e5"], r"VIN_RAW and TRK_OUT hold [\d.]+ uF nominal \(NETLIST: (.*?)\)", "VIN_RAW's capacitors", re.S)
    caps = re.findall(r"([AE]) (C\d+) ([\d.]+)u", re.sub(r"\s+", " ", m.group(1)))
    A["vr_caps"] = [(b, r, float(v)) for b, r, v in caps if not (b == "E" and r in ("C24", "C25", "C26", "C27"))]
    A["vr_c_uf"] = sum(v for _b, _r, v in A["vr_caps"])
    plim_lo = plim_c(R24_NEW_K * 1e3 * (1 - R24_TOL), A["rs"] * (1 + rs_tol), vmax) / TI_SOA_MARGIN
    tst = lambda cuf, pl, il: cuf * 1e-6 / 2.0 * (vmax ** 2 / pl + pl / il ** 2) * 1e3
    A["t_start_nom"] = tst(A["vr_c_uf"], A["plim_new_nom"], (F["entry_lim"][0] + F["entry_lim"][1]) / 2.0)
    A["t_start_hi"] = tst(A["vr_c_uf"] * hi_f, plim_lo, F["entry_lim"][0])
    A["plim_lo_margin"] = plim_lo
    A["start_need"] = 1.5 * A["t_start_hi"]                         # SNVS452G 9.2.1.2.4: the minimum fault time over the start by 50 %
    # an option, not selected: C5 150 nF C0G 5 % (no temperature or endurance class drift taken), against both the start and the SOA
    A["c0g_k"], A["c0g_tol"] = 1.5, 0.05
    A["c0g_env"] = (F["timer_ms"][0] * A["c0g_k"] * (1 - A["c0g_tol"]), F["timer_ms"][2] * A["c0g_k"] * (1 + A["c0g_tol"]))
    A["c0g_soa_hot"] = i10 * (10e-3 / (A["c0g_env"][1] * 1e-3)) ** mexp * A["soa_derate"]
    # the start: a higher limit only shortens the start into the bus's capacitance (Equation 12 falls with PLIM), so the timer's
    # minimum keeps its margin; stated, not recomputed (the downstream capacitance is L4-E5's)

    # ---- fix round B2: what F1 protects, traced (REQ-045, PWR-003 and the SHORE_INPUT stage), with the makers' ratings held
    A["req045"] = need(T["reqs"], r"- id: REQ-045\n.*?statement: >-\n\s+(.*?)\n\s+acceptance:", "REQ-045", re.S).group(1)
    A["req045"] = re.sub(r"\s+", " ", A["req045"])
    asm = re.sub(r"\s+", " ", need(T["reqs"], r"- id: ASM-001\n.*?statement: >-\n\s+(.*?)\n\s+acceptance:", "ASM-001", re.S).group(1))
    if "LoRa module" not in asm or "power" in asm.lower().split("bearers")[0]:
        refuse(3, "ASM-001's scope")
    A["asm001"] = asm[:110]
    ch = yaml.safe_load(T["chain"])
    st_si = [x for x in ch["stages"] if x["id"] == "SHORE_INPUT"][0]
    A["si_conductor_a"] = float(st_si["conductor"]["rating_a"])
    A["si_prospective_low"] = float(st_si["prospective_fault_a"]["low"])
    A["si_protects"] = st_si.get("protects")
    A["ecss_x"] = 3.0 if re.search(r"capable of delivering three times the specified fuse rated current", T["ecss"].replace("\n>   ", " ")) else None
    if A["ecss_x"] is None:
        refuse(3, "ECSS 6.17.3c")
    dz = pdf_text("d38999")
    dz = dz[need(dz, r"CONTACT RATING FOR TV III, HD, JT II, LJT I, SJT", "the D38999 contact rating table").start():]
    m = need(dz, r"\n\s+16\s+(\d+)\s+(\d+)\s+\d+\s+\d+\s+\d+", "D38999 size 16 contact test current")
    A["c16_a"] = f(m, 1)
    m = need(dz, r"\n\s+12\s+(\d+)\s+(\d+)\s+\d+\s+\d+\s+\d+", "D38999 size 12 contact test current")
    A["c12_a"] = f(m, 1)
    m = need(fz, r"0997010_\s+10\s+(\d+(?:\.\d+)?)\s+\d+", "0997 10 A test cable")
    A["f_test_cable_mm2"] = f(m)
    A["f_rating"] = 10.0
    A["f_i2"] = 135 / 100.0 * A["f_rating"]                                     # the 135 % row: opens within its maximum time
    A["f_200"] = 2.0 * A["f_rating"]
    # the weakest element F1 protects in the 10 to 20 A band and the time the fuse may leave current there
    A["wk"] = [("J_DCIN's VH contact, AWG 16 standard header (MAKER)", F["vh_16"]),
               ("the D38999 size 16 contact (Amphenol, test current; MAKER)", A["c16_a"]),
               ("board E's input bands at 2 oz (pcb_energy_chain.yaml SHORE_INPUT)", A["si_conductor_a"])]
    A["awg16_mm2"] = 1.31
    rc16 = (2 * F["cable_m"] * CU_RHO_20C / F["cable_mm2"] + 2 * F["lead_mm"] / 1000.0 * CU_RHO_20C / A["awg16_mm2"]) * (1 + CU_ALPHA * (T_COLD - 20.0))
    A["f1_ipf_awg16"] = vmax / rc16
    A["dcp_melt_ms"] = A["f_i2t"] / D["f1_ipf"] ** 2 * 1e3

    # ---- fix round B3: the transients through R227 (the capacitors the draft puts behind it)
    gA = T["gen_a"]
    cin = need(gA, r'cin="(\d+)u 50V X7R 1210", out_budget', "the helper's default input capacitor").group(1)
    poe_call = need(gA, r'lm5176\("POE", "U16".*?\)   # fix-up loop', "U16's call", re.S).group(0)
    if "cin=" in poe_call:
        refuse(3, "U16's call names its own input capacitor; read it")
    vc = need(poe_call, r'vin_cap=\("C\d+", "(\d+)n"', "U16's VIN capacitor")
    bc = need(gA, r'c\(bias_cap, "(\d+)n", bias or vout', "the BIAS capacitor")
    A["poe_c_uf"] = 2 * float(cin) + float(vc.group(1)) * 1e-3 + float(bc.group(1)) * 1e-3
    m = need(_C_TEXT["lcsc"], r'\(r"\^10u 50V X7R 1210\$", "C_1210"\): "(C\d+)",\s+# YAGEO (CC1210KKX7R9BB106)', "the 10 uF fill mapping")
    A["c10_code"], A["c10_part"] = m.group(1), m.group(2)
    vb_hi, vb_reg, vpk = round(D["pack_open"]["v_end"], 3), F["chg_v_max"], F["SMCJ18A"]["vc"]
    A["tr_steps"] = [("a hard connect, 0 to the regulated maximum", 0.0, vb_reg, True),
                     ("the pack opening mid-charge, regulated maximum to the pack-open bound", vb_reg, vb_hi, True),
                     ("D1's rated pulse on VBAT (a capability scenario, D-16)", vb_reg, vpk, False)]
    A["tr"] = []
    for nm, v0, v1, req in A["tr_steps"]:
        dv = v1 - v0
        A["tr"].append((nm, v0, v1, dv, v0 + 2 * dv, 0.5 * A["poe_c_uf"] * 1e-6 * dv ** 2 * 1e3, req))
    A["ina_diff_abs"] = f(need(ina, r"Differential \(VIN\+ . VIN-\)\(2\)\s+.40\s+(\d+)", "INA226 differential absolute"))
    # the buck fault: steady buck operation and one full on-time in a hard short
    fsw = need(pdf_text("lm5176"), r"fSW\(1\)\s+Switching frequency 1\s+RT = (\d+) k[\u2126\u03a9]\s+(\d+)\s+(\d+)\s+(\d+)", "LM5176 fSW(1)")
    rt_k = float(need(gA, r'r\(rrt, "([\d.]+)k \(206 kHz\)"', "U16's RT").group(1))
    A["fsw_min"] = f(fsw, 2) * 1e3 * f(fsw, 1) / rt_k
    A["t_max"] = 1.0 / A["fsw_min"]
    l_poe = float(need(gA, r'"L10", "(\d+)uH XAL1010-153ME \(Isat ([\d.]+) A\)"', "U16's inductor").group(1)) * 1e-6
    A["l10_isat"] = float(need(gA, r'"L10", "\d+uH XAL1010-153ME \(Isat ([\d.]+) A\)"', "U16's inductor Isat").group(1))
    A["l10_min"] = l_poe * (1 - L2_TOL)
    vin_hi = F["chg_v_max"]
    A["buck_ripple_max"] = vin_hi * A["t_max"] / (4 * A["l10_min"])          # VIN D (1 - D) T / L at D = 0.5
    A["buck_peak_steady"] = A["u17_buck_valley_a"] + A["buck_ripple_max"]
    A["buck_rms_bound"] = math.sqrt((A["u17_buck_valley_a"] + A["buck_ripple_max"] / 2.0) ** 2 + A["buck_ripple_max"] ** 2 / 12.0)
    A["buck_p"] = A["buck_rms_bound"] ** 2 * rsh * 1.01
    A["short_peak"] = A["u17_buck_valley_a"] + vin_hi * A["t_max"] / A["l10_min"]
    A["short_pulse_uj"] = A["short_peak"] ** 2 * rsh * 1.01 * A["t_max"] * 1e6
    m = need(pdf_text("lm5176"), r"VSNS\s+Average current loop regulation target\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "LM5176 VSNS")
    A["isns_max_mv"] = f(m, 3)
    A["poe_isns"] = float(need(gA, r'isns="(\d+)m", rcs="\d+m", bias="VBAT"', "U16's ISNS").group(1)) * 1e-3
    A["avg_out_limit"] = A["isns_max_mv"] * 1e-3 / (A["poe_isns"] * 0.99)
    return A


def partA_lines(F, D, A):
    L = []
    p = L.append
    p("11. PART A: Q1, F1 AND U17 AS DATASHEET-BACKED PROPOSALS (the applicable conditions, not only the headline rating)")
    p("   Q1, board E's vehicle-entry ideal-diode FET: TI CSD19532Q5B (SLPS414B, byte-identical to ti.com on 2 October 2026), LCSC C473333")
    p("     maker's rows: VDS %s V, VGS +-%s V, ID %s A (1 in2 2 oz), IDM %s A, EAS %s mJ, TJ to %s C; RDS(on) at VGS 10 V %s / %s mOhm;"
      % (fmt(F["csd19532_vds"]), fmt(A["vgs_max"]), fmt(A["id_cont"]), fmt(A["idm"]), fmt(A["eas"]), fmt(A["tj_max"]), fmt(A["rds10"][0]), fmt(A["rds10"][1])))
    p("       Vth %s / %s / %s V; VSD at most %s V; Qg at most %s nC; RthetaJA at most %s C/W (1 in2 2 oz; board E's copper an ASSUMPTION)"
      % (fmt(A["vth"][0]), fmt(A["vth"][1]), fmt(A["vth"][2]), fmt(A["vsd_max"]), fmt(A["qg_max"]), fmt(A["rja"])))
    p("     normal: %s A (the entry's highest) at RDS(on) %s mOhm x %s (Figure 8 at 150 C, read) = %s W; TJ at most %s C in %s C air "
      "(MEETS against %s C; INFERRED)" % (fmt(F["entry_lim"][1]), fmt(A["rds10"][1]), fmt(CSD_RDS_NORM_150C), fmt(round(A["q1_p"], 3)), fmt(round(A["q1_tj"], 1)), fmt(F["air"][1]), fmt(A["tj_max"])))
    p("       ID %s A against %s A: MEETS (MAKER); at hot plug the body diode carries the hot swap's limited current for at most "
      "%s ms (ENTDLY %s us plus Qg %s nC at the controller's %s mA): %s mJ (INFERRED)"
      % (fmt(F["entry_lim"][1]), fmt(A["id_cont"]), fmt(round(A["q1_inrush_s"] * 1e3, 3)), fmt(A["entdly_max_us"]), fmt(A["qg_max"]), fmt(A["gate_src_min_ma"]), fmt(round(A["q1_inrush_mj"], 3))))
    p("       SOA: Q1 runs fully enhanced or off (the ideal diode regulates only a 20 mV forward drop): no linear dwell to judge")
    p("     reverse (REQ-015, -%s V with DC_P back-fed from the raised tracker ceiling through Q7's body diode): VDS %s V against %s V: MEETS (INFERRED);"
      % (fmt(D["vrev"]), fmt(A["q1_rev"]), fmt(F["csd19532_vds"])))
    p("       the LM74700-Q1's cathode to anode %s V against %s V recommended and %s V absolute, its ANODE -%s V against -%s V: MEETS (MAKER)"
      % (fmt(A["q1_rev"]), fmt(F["ld_ac_rec"]), fmt(F["ld_ca_abs"]), fmt(D["vrev"]), fmt(F["ld_anode_abs"])))
    p("       the body diodes: Q1's reverse-biased (it blocks); Q7's forward at DC_P's own milliamps (the back-feed); D10 off (%s V under its %s V"
      % (fmt(D["vrev"]), fmt(F["SMCJ40A"]["vbr_min"])))
    p("       breakdown); D1 reverse-biased (cathode on DC_P); the input capacitor of E-F1 at -%s V on its 100 V rating" % fmt(D["vrev"]))
    p("     transients (TEST-PLAN M2 CS101, M3 CS114 and M7 at decision 34's level, as L4-E7R derived them for the solar entry; no surge level is")
    p("       ruled, D-16 and CHO-003): CS101 curve 2, %s V rms, %s V peak: Q1 conducts forward and blocks at most %s V when the controller opens it"
      % (fmt(A["cs101_vrms"]), fmt(round(A["cs101_pk"], 3)), fmt(round(2 * A["cs101_pk"], 2))))
    p("       in %s us; at the range's top the input reaches %s V, past the OVLO's %s V minimum: the hot swap may switch off under M2 (an upset"
      % (fmt(A["trev_max_us"]), fmt(round(A["cs101_top"], 2)), fmt(F["ovlo"][0])))
    p("       against M2's line at a 36 V source, not a rating); at curve 2's own boundary, a %s V source, the top is %s V, %s V under it: MEETS."
      % (fmt(A["cs101_src_v"]), fmt(round(A["cs101_top_src"], 2)), fmt(round(F["ovlo"][0] - A["cs101_top_src"], 2))))
    p("       TEST-PLAN M2 states no source voltage, so the finding is a defect at REQ-015's top with two resolutions on the same topology: (i) M2 at")
    p("       the source's nominal, stated by TEST-PLAN's owner; (ii) the OVLO moved so its minimum clears %s V and its maximum stays under D10's %s V breakdown"
      % (fmt(round(A["cs101_top"], 2)), fmt(F["SMCJ40A"]["vbr_min"])))
    p("       minimum: R23 from %s k down to %s k with R22 %s k at 1 %% (the band re-derived: %s to %s V for R23 %s k, as s120 prints); no E96"
      % (fmt(round(A["r23_win"][1], 3)), fmt(round(A["r23_win"][0], 3)), fmt(A["r22_k"]), fmt(round(A["ovlo_check"][0], 2)), fmt(round(A["ovlo_check"][1], 2)), fmt(A["r23_k"])))
    p("       value lies inside; E192's %s k at 1 %% gives %s to %s V (%s V and %s V of margin); with R22 and R23 both 0.1 %%: %s to %s V, %s V over the"
      % (fmt(A["r23_e192"]), fmt(round(A["ovlo_e192"][0], 2)), fmt(round(A["ovlo_e192"][1], 2)), fmt(round(A["ovlo_e192"][0] - A["cs101_top"], 2)),
         fmt(round(F["SMCJ40A"]["vbr_min"] - A["ovlo_e192"][1], 2)), fmt(round(A["ovlo_new"][0], 2)), fmt(round(A["ovlo_new"][1], 2)),
         fmt(round(A["ovlo_new"][0] - A["cs101_top"], 2))))
    p("       CS101 peak and %s V under D10's breakdown minimum at 25 C. D10's breakdown falls %s %%/K (typical): %s V at -20 C, under the present"
      % (fmt(round(F["SMCJ40A"]["vbr_min"] - A["ovlo_new"][1], 2)), fmt(A["tvs_alpha"] * 100), fmt(round(A["d10_cold_vbr"], 2))))
    p("       OVLO maximum already, so steady inputs above it reach D10 when cold; REQ-015 admits steady inputs to 40 V, under it: CONDITIONAL (a")
    p("       typical coefficient, not a warranted bound) for REQ-015's")
    p("       inputs. SESSION: (ii) at 0.1 % selected (it removes the finding whatever M2's source voltage; register R-94); (i) not taken (a test")
    p("       condition is not changed to fit the design); CS114 curve 4, %s mA rms into E-F1's 1 uF at 10 kHz: at most %s V peak, Q1 blocks"
      % (fmt(A["cs114_ma"]), fmt(round(A["cs114_pk"], 2))))
    p("       at most %s V; M7 with E-F1's capacitor: DC_F moves %s V, so Q1 stands off at most %s V: MEETS (INFERRED)"
      % (fmt(round(2 * A["cs114_pk"], 2)), fmt(F["ef1_dv"][1]), fmt(round(A["m7_vds"], 2))))
    p("       the capability scenario (D10 at its rated pulse, not a requirement): negative, Q1 at %s V with DC_P at %s V, past %s V by %s V; the"
      % (fmt(A["cap_neg_vds"]), fmt(D["vrev"]), fmt(F["csd19532_vds"]), fmt(round(A["cap_neg_vds"] - F["csd19532_vds"], 2))))
    p("       avalanche energy on the bus behind it at most %s mJ against EAS %s mJ; the LM74700-Q1's %s V is passed once DC_P exceeds %s V, and"
      % (fmt(round(A["cap_energy_mj"], 1)), fmt(A["eas"]), fmt(F["ld_ca_abs"]), fmt(A["cap_dcp_ld_limit"])))
    p("       Q1's once DC_P exceeds %s V: NOT MET, outside every requirement (D-16; DECISION-31 recorded it); positive: the controller's ANODE at"
      % fmt(A["cap_dcp_q1_limit"]))
    p("       %s V against %s V (E-N2)" % (fmt(F["SMCJ40A"]["vc"]), fmt(F["ld_anode_abs"])))
    vmax = F["ovlo_sel"][2]
    p("     faults, the hot swap's power limit (fix round, B1): with the drawn R24 %s Ohm the limit's sense voltage at the selected OVLO maximum %s V is"
      % (fmt(A["rpwr"]), fmt(round(vmax, 2))))
    p("       %s mV nominal (Equation 7 with Equation 9), under the %s mV SNVS452G 9.2.1.2.3 does not recommend (the PWRLIM rows are tested at 48 V and"
      % (fmt(round(A["vsns_drawn"] * 1e3, 4)), fmt(A["vsns_min"] * 1e3)))
    p("       150 kOhm, not at this setting): NOT MET as drawn. The least RPWR for 5 mV at %s V is %s Ohm (Equation 9); SESSION: R24 %s k %s %%, whose low"
      % (fmt(round(vmax, 2)), fmt(round(A["rpwr_min"])), fmt(R24_NEW_K), fmt(R24_TOL * 100)))
    p("       corner reads %s mV (nominal %s mV): MEETS (MAKER guidance). The hot-short pulse at the same voltage, by TI's own procedure"
      % (fmt(round(A["vsns_new_low"] * 1e3, 3)), fmt(round(A["vsns_new_nom"] * 1e3, 3))))
    p("       (9.2.1.2.5), in parts. THE BREAKER'S EVENT: VCB's maximum over R19 at -1 %% is a threshold, %s A, and tCB (%s us maximum) is"
      % (fmt(round(A["cb_thr"], 3)), fmt(A["tcb_max"])))
    p("       measured with GATE low and no load (SNVS452G p.6): neither bounds the event's peak current nor Q7's loaded turn-off. The current rises at")
    p("       the source's and wiring's V / L until the 230 mA pulldown has turned Q7 off, and REQ-015 states no source inductance: OPEN evidence, with")
    p("       a bounded investigation (R-118: the peak and the turn-off measured at a hot short from a stiff %s V source through the kit's cable; the 10 us"
      % fmt(round(vmax, 2)))
    p("       line derated as below allows %s A at %s V for pulses of 10 us or less). THE POWER LIMIT: %s W nominal, at R24 +%s %% and R19 -1 %%"
      % (fmt(round(A["cb_10us_hot"], 1)), fmt(round(vmax, 2)), fmt(round(A["plim_new_nom"], 3)), fmt(R24_TOL * 100)))
    p("       %s W, times TI's margin %s: %s W, %s A at %s V, for the fault time, then off after tFAULT (%s us typical) and the 2 mA pulldown, and a"
      % (fmt(round(A["plim_new_hi"], 3)), fmt(TI_SOA_MARGIN), fmt(round(A["pulse_w"], 2)), fmt(round(A["pulse_a"], 3)), fmt(round(vmax, 2)), fmt(A["tfault_us"])))
    p("       retry at %s %% duty. The fault time: L4-E5's %s / %s / %s ms take C5 at its nominal 100 nF; C5 is %s (Yageo CC0603KRX7R9BB104, K: +-%s %%;"
      % (fmt(A["restart_duty"] * 100), *[fmt(x) for x in F["timer_ms"]], A["c5_code"], fmt(A["c_tol"] * 100)))
    p("       X7R: +-%s %% over temperature and +-%s %% after endurance, the Yageo sheet V.26), so +%s %% alone gives %s ms and the printed rows stacked"
      % (fmt(A["c_temp"] * 100), fmt(A["c_endur"] * 100), fmt(A["c_tol"] * 100), fmt(round(A["tflt_k_only"], 3))))
    p("       give %s to %s ms (INFERRED; DC bias only lowers it). Figure 10 read from the sheet's vector drawing at %s V (lines %s): 10 ms %s A,"
      % (fmt(round(A["tflt_env"][0], 3)), fmt(round(A["tflt_env"][1], 3)), fmt(round(vmax, 2)), ", ".join(A["soa_labels"]), fmt(round(A["soa_10ms"], 3))))
    p("       1 ms %s A, 10 us %s A at TC 25 C; Equations 15 to 18 (m = %s) give %s A at L4-E5's %s ms and %s A at the envelope's %s ms (TI's power"
      % (fmt(round(A["soa_1ms"], 3)), fmt(round(A["soa_10us"], 1)), fmt(round(A["soa_m"], 3)), fmt(round(A["soa_tflt_25"], 3)), fmt(F["timer_ms"][2]),
         fmt(round(A["soa_tenv_25"], 3)), fmt(round(A["tflt_env"][1], 3))))
    p("       law carried %s %% past the 10 ms line); Q7's case at most %s C (the hottest inside air the record holds, %s C, plus its own %s W at"
      % (fmt(round(A["soa_extrap"] * 100, 1)), fmt(round(A["tc_max"], 1)), fmt(round(A["t_hot"], 2)), fmt(round(A["q1_p"], 3))))
    p("       6.15 A on %s C/W), so Equation 19 derates by %s: %s A at the timer's maximum against the pulse's %s A: it still fits (CONDITIONAL on"
      % (fmt(A["rja"]), fmt(round(A["soa_derate"], 4)), fmt(round(A["soa_tenv_hot"], 3)), fmt(round(A["pulse_a"], 3))))
    p("       board E's copper under Q7, RthetaJA an ASSUMPTION, and on the extrapolation). THE START: Equation 12 into VIN_RAW's %s uF (%s) at %s V"
      % (fmt(A["vr_c_uf"]), ", ".join("%s %s %s u" % (b, r, fmt(v)) for b, r, v in A["vr_caps"]), fmt(round(vmax, 2))))
    p("       takes %s ms at nominal values and %s ms with the capacitors at the printed rows' top (the same rows taken for board E's two, an"
      % (fmt(round(A["t_start_nom"], 3)), fmt(round(A["t_start_hi"], 3))))
    p("       ASSUMPTION) and the limit at its low corner over TI's 1.3 (%s W); TI asks the minimum fault time to exceed the start by half again,"
      % fmt(round(A["plim_lo_margin"], 2)))
    p("       %s ms, and the stacked minimum is %s ms: NOT MET at the stacked corners (the front end's own load during the start is not included"
      % (fmt(round(A["start_need"], 3)), fmt(round(A["tflt_env"][0], 3))))
    p("       either), defect D-09, OPEN, the timer's component bounds an investigation (R-119). An option, not selected (no part is read): C5")
    p("       %s nF C0G at %s %% gives %s to %s ms, over the start's %s ms and, at %s A, inside Figure 10's power law derated (carried %s %% past"
      % (fmt(A["c0g_k"] * 100), fmt(A["c0g_tol"] * 100), fmt(round(A["c0g_env"][0], 3)), fmt(round(A["c0g_env"][1], 3)), fmt(round(A["start_need"], 3)),
         fmt(round(A["c0g_soa_hot"], 3)), fmt(round((A["c0g_env"][1] / 10.0 - 1) * 100, 1))))
    p("       the 10 ms line) against the pulse's %s A. Round 2's %s A at 36 V read by eye is withdrawn: the drawing reads %s A there. Q1 carries at"
      % (fmt(round(A["pulse_a"], 3)), fmt(CSD_SOA_10MS_36V_A), fmt(round(A["soa_36_line"], 3))))
    p("       most 6.15 A in the power-limit part; in the breaker's event it carries the same open peak")
    p("       a short at DC_P, ahead of the hot swap (it needs a prior short of D10, D1, E-F1's capacitor or C4): only F1 limits, at most %s A"
      % fmt(round(D["f1_ipf"], 1)))
    p("       from a stiff source; %s ms is an illustration from the 10 A part's typical melting I2t (arcing excluded), not a clearing time. Q1 lies in"
      % fmt(round(A["dcp_melt_ms"], 3)))
    p("       that path and no figure shows it holds %s A against its IDM %s A for 100 us; it is not a conductor or connector of REQ-045, and the" % (fmt(round(D["f1_ipf"], 1)), fmt(A["idm"])))
    p("       entry is already failed: the disposition is traced under F1 below (no exemption is claimed; ASM-001 is the LoRa and cellular exception)")
    p("     gate drive and land: VGS %s to %s V (the charge pump's window) against +-%s V: MEETS; TI's guidance asks a VGS rating of %s V: MEETS;"
      % (fmt(A["cp_on_min"]), fmt(A["cp_off_max"]), fmt(A["vgs_max"]), fmt(A["gate_rec"])))
    p("       its Vth at most %s V against TI's recommended %s V: NOT MET as a recommendation (the drawn BSC039N06NS's 3.3 V also misses it;"
      % (fmt(A["vth"][2]), fmt(A["vth_rec_max"])))
    p("       effect: turn-on time and light-load regulation, bench R-112); RDS(on) %s mOhm typical at about %s C against TI's %s to %s mOhm at"
      % (fmt(round(A["rds_at_tj"], 2)), fmt(round(A["q1_tj"], 0)), fmt(round(A["rds_guide"][0], 2)), fmt(round(A["rds_guide"][1], 2))))
    p("       H3's %s A: MEETS (typical, INFERRED); TI recommends FETs to 60 V with this controller; the 100 V part is a deliberate departure (SESSION)"
      % fmt(F["h3"][9.0][1]))
    p("       whose reason, the controller's own pins, is checked above; the land is Q7's PowerPAK SO-8 / 5x6 SON for the same part")
    p("   F1, board E's vehicle-entry fuse: Littelfuse 0997010.WXN, MINI 58 V (the sheet revised 11/18/2025, held back; fetch_held_back.py)")
    p("     DC voltage rating %s V DC against the selected OVLO maximum %s V (R23 6.42k, 0.1 %%): MEETS (MAKER, a DC rating); interrupting %s A at 58 V DC against %s A: MEETS"
      % (fmt(A["f_v"]), fmt(round(D["f1_v"], 2)), fmt(A["f_int"]), fmt(round(D["f1_ipf"], 1))))
    p("     the prospective current by voltage (the kit's cable and lead, copper at -20 C, the source stiff: REQ-015 states no source impedance, so")
    p("       a vehicle battery and its wiring only lower it): %s" % "; ".join("%s V %s A" % (fmt(round(v, 2)), fmt(round(i, 1))) for v, i in A["f1_ipf_by_v"]))
    p("     no nuisance opening: the sheet's derating table (%s C columns) at the next column above %s C inside air, %s C: %s A against the entry's %s A: MEETS"
      % ("/".join(fmt(x) for x in A["f_amb"]), fmt(F["air"][1]), fmt(A["f_col"]), fmt(A["f_allow"]), fmt(F["entry_lim"][1])))
    p("       (the project's rule: the next higher column, never interpolated); 110 %% of rating opens no sooner than %s s; the hot swap's start-up"
      % fmt(A["f_tc"][110][0]))
    p("       at %s A for at most %s ms is %s A2s against the part's typical %s A2s (melting before arcing): MEETS (INFERRED)"
      % (fmt(F["entry_lim"][1]), fmt(F["timer_ms"][2]), fmt(round(A["f_startup_i2t"], 3)), fmt(A["f_i2t"])))
    p("     against what it protects: the time-current rows %s; the lowest stiff-source fault at 9 V with the copper at %s C is %s A, %s times"
      % ("; ".join("%d %% %s / %s s" % (k, fmt(v[0]), fmt(v[1]) if v[1] is not None else "-") for k, v in sorted(A["f_tc"].items())), fmt(F["air"][1]), fmt(round(A["f_min_fault_9v"], 1)), fmt(round(A["f_min_fault_9v"] / 10.0, 1))))
    p("       the rating, inside the 600 %% row (at most %s s)" % fmt(A["f_tc"][600][1]))
    p("     what F1 protects, traced (fix round, B2): REQ-045 asks '%s'" % A["req045"])
    p("       PWR-003 (pcb_energy_chain.yaml) carries the stage SHORE_INPUT: conductor %s A (board E's input bands), protects %s, prospective low %s A"
      % (fmt(A["si_conductor_a"]), A["si_protects"] or "no stage named", fmt(A["si_prospective_low"])))
    p("       ('not established'); the project's fuse criterion, ECSS-Q-ST-30-11C 6.17.3c, asks the source to deliver %s times the fuse's rating, %s A"
      % (fmt(A["ecss_x"]), fmt(A["ecss_x"] * A["f_rating"])))
    p("       the elements in the fault path, with their makers' ratings: %s" % "; ".join("%s %s A" % (nm, fmt(a)) for nm, a in A["wk"]))
    p("       and the kit's cable (Lapp OLFLEX ROBUST 210 4 x 1.0 or Alpha Wire 25064, 18 AWG) and the inside lead, whose held sheets print no current")
    p("       rating; the 0997's own test cable for its 10 A rating is %s mm2 (MAKER, ISO 8820-3 setup)" % fmt(A["f_test_cable_mm2"]))
    p("     a stiff source (the DC_P short above): F1 interrupts %s A against its %s A: MEETS; the conductors' short-time withstand against F1's"
      % (fmt(round(D["f1_ipf"], 1)), fmt(A["f_int"])))
    p("       let-through is CONDITIONAL on the total clearing I2t at 43 V DC, which the sheet does not print (a clarification to Littelfuse, R-115);")
    p("       with an AWG 16 inside lead (R-29) the stiff-source current is %s A, still under %s A" % (fmt(round(A["f1_ipf_awg16"], 1)), fmt(A["f_int"])))
    p("     a weak source (any source under %s A): F1 may leave %s to %s A flowing (its 110 %% row: no opening before %s s), %s A for up to %s s and %s A"
      % (fmt(A["ecss_x"] * A["f_rating"]), fmt(A["f_rating"]), fmt(1.1 * A["f_rating"]), fmt(A["f_tc"][110][0]), fmt(A["f_i2"]), fmt(A["f_tc"][135][1]), fmt(A["f_200"])))
    p("       for up to %s s, through elements stated at %s A: NOT ESTABLISHED. No held maker sheet gives a contact's or a conductor's time-current"
      % (fmt(A["f_tc"][200][1]), " / ".join(fmt(a) for _n, a in A["wk"])))
    p("       limit in that band, so it is an OPEN engineering question, defect D-06 (not an exemption): the alternatives are an interconnect rated to")
    p("       the fuse's %s A point (size 12 contacts, %s A test current; a %s A-class board connector such as the XT60-M board E already carries;"
      % (fmt(A["f_200"]), fmt(A["c12_a"]), fmt(30)))
    p("       a cable whose maker's rating covers it, which also raises the stiff-source current toward F1's %s A), the source's capability stated in"
      % fmt(A["f_int"]))
    p("       REQ-015 (ECSS 6.17.3c, the owner's), or the makers' overload data obtained (Lapp, JST, Amphenol)")
    p("     the holder: Keystone M65 p.42 names the 3568 'For Littelfuse Mini 297 or 997 series'; the sheet gives the same blade size and pitch:")
    p("       MEETS; the 58 V part's rejection feature works only in a 58 V keyed holder, so the 3568 also takes a 32 V MINI: the BOM, label and")
    p("       ASSEMBLY.md name the 0997 (R-18)")
    p("   U17, board A's PoE monitor: the INA226 (SBOS547C, byte-identical to ti.com on 2 October 2026) moved to R227, %s mOhm in the PoE stage's VBAT input"
      % fmt(A["u17_rsh"] * 1e3))
    p("     as drawn: IN+ and IN- at %s V against %s V absolute: NOT MET (HF-F02)" % (fmt(F["poe"]["volts"]), fmt(F["ina_abs"])))
    p("     common mode: VBAT at most %s V regulated, %s V at SYSOVP, %s V at the pack-open bound, %s V at D1's rated pulse, against %s V (CMRR row and"
      % (fmt(F["chg_v_max"]), fmt(F["sysovp"][2]), fmt(round(D["pack_open"]["v_end"], 3)), fmt(F["SMCJ18A"]["vc"]), fmt(F["ina_cm_op"])))
    p("       bus range) and %s V absolute: MEETS (MAKER); VBUS on POE_VIN likewise" % fmt(F["ina_abs"]))
    p("     differential: the stage's input at its 0.6 A at a %s V stack, %s A, %s mV; at its fault bound, U16's boost peak limit (%s + %s) mV over"
      % (fmt(D["vbat_low"]), fmt(round(A["u17_in_norm"], 3)), fmt(round(A["u17_mv_norm"], 2)), fmt(A["vcs_boost_max"] * 1e3), fmt(A["cs_off"] * 1e3)))
    p("       R72's %s mOhm at -1 %%, %s A, %s mV: both inside the %s mV full scale: MEETS (INFERRED); R227 then dissipates %s W against %s W at %s C"
      % (fmt(A["poe_rcs"] * 1e3), fmt(round(A["u17_fault_a"], 2)), fmt(round(A["u17_mv_fault"], 2)), fmt(F["ina_fs_mv"]), fmt(round(A["u17_p_fault"], 3)), fmt(round(A["hojlr_avail"], 2)), fmt(F["air"][1])))
    p("       (HoJLR2512: %s W derated from %s C to zero at %s C): MEETS" % (fmt(A["hojlr"][0]), fmt(A["hojlr"][1]), fmt(A["hojlr"][2])))
    p("       R227 is the part L4-E4 chose for R138, HoJLR2512-3W-5mR-1%%, LCSC %s (Milliohm; +-1 %%, TCR +-%s ppm/K, MAKER as L4-E4 read it)"
      % (A["r5_lcsc"], fmt(round(A["r5_tcr"] * 1e6))))
    p("     a PoE fault (an overload or a short on +54V_POE, fix round B3): U16 is a four-switch buck-boost; with its output pulled under its input")
    p("       it runs in buck operation, where the high-side current's valley is held at VCS(BUCK) %s mV maximum over R72 (%s A at -1 %%). Steady buck:"
      % (fmt(A["vcs_buck_max"] * 1e3), fmt(round(A["u17_buck_valley_a"], 2))))
    p("       the ripple VIN D (1 - D) T / L is largest at D = 0.5: %s A at %s V, T %s us (fSW(1)'s minimum scaled to RT %s k), L %s uH (-20 %%); the"
      % (fmt(round(A["buck_ripple_max"], 3)), fmt(F["chg_v_max"]), fmt(round(A["t_max"] * 1e6, 3)), fmt(40.2), fmt(round(A["l10_min"] * 1e6, 1))))
    p("       inductor's peak %s A (under its %s A Isat), its RMS at most %s A; R227 carries the high-side current, whose RMS is at most that: %s W"
      % (fmt(round(A["buck_peak_steady"], 2)), fmt(A["l10_isat"]), fmt(round(A["buck_rms_bound"], 2)), fmt(round(A["buck_p"], 3))))
    p("       against %s W; the peak reads %s mV, inside full scale: MEETS (INFERRED). A hard short (the output near 0 V): the valley is crossed rarely"
      % (fmt(round(A["hojlr_avail"], 2)), fmt(round(A["buck_peak_steady"] * 5.05, 2))))
    p("       and one on-time can last a full period: the peak reaches %s A, past the inductor's Isat, so a lower bound there (INCONCLUSIVE on L above"
      % fmt(round(A["short_peak"], 2)))
    p("       Isat, the L10 assignment R-120 and R-121); R227 then reads %s mV, past full scale: an ADC SATURATION of that sample, not damage (the differential stays"
      % fmt(round(A["short_peak"] * 5.05, 1)))
    p("       far under the %s V absolute); %s uJ in R227 per such period; the average output loop (VSNS %s mV maximum over R71) then holds the"
      % (fmt(A["ina_diff_abs"]), fmt(round(A["short_pulse_uj"], 2)), fmt(A["isns_max_mv"])))
    p("       output's average at %s A at most once the soft-start capacitor discharges; a port's own fault is board B's TPS23861's"
      % fmt(round(A["avg_out_limit"], 3)))
    p("     transients behind R227 (B3): the draft puts C81, C82 (two %s uF), U16's VIN and BIAS capacitors behind R227: %s uF nominal (NETLIST). For"
      % ("10", fmt(round(A["poe_c_uf"], 2))))
    p("       a step of VBAT the differential across R227 never exceeds the step (at the current's peak the loop's inductance carries no voltage), and")
    p("       POE_VIN rings to at most its start plus twice the step (an undamped bound; any resistance only lowers it):")
    for nm, v0, v1, dv, ring, e_mj, req in A["tr"]:
        p("       - %s: step %s V, differential at most %s V (%s V absolute: %s), POE_VIN at most %s V (pins %s V: %s), R227 %s mJ nominal"
          % (nm, fmt(round(dv, 3)), fmt(round(dv, 3)), fmt(A["ina_diff_abs"]), "MEETS" if dv <= A["ina_diff_abs"] else "NOT MET",
             fmt(round(ring, 2)), fmt(F["ina_abs"]), ("MEETS" if ring <= F["ina_abs"] else ("NOT MET in the undamped limit" if req else "past it in the undamped limit; outside every requirement")),
             fmt(round(e_mj, 3))))
    p("       the differential above %s mV only saturates the ADC's sample; damage needs %s V across the inputs or a pin outside -0.3 to %s V, which"
      % (fmt(F["ina_fs_mv"]), fmt(A["ina_diff_abs"]), fmt(F["ina_abs"])))
    p("       no required event reaches. R227's pulse energy at the hard connect is %s mJ NOMINAL (0.5 C dV2 at the nominal %s uF, all taken by R227);"
      % (fmt(round(A["tr"][0][5], 3)), fmt(round(A["poe_c_uf"], 2))))
    p("       the capacitors are K parts (%s, Yageo %s, and %s for the 100 nF ones): +%s %% alone gives %s mJ, and the printed rows stacked (K,"
      % (A["c10_code"], A["c10_part"], A["c5_code"], fmt(A["c_tol"] * 100), fmt(round(A["tr"][0][5] * (1 + A["c_tol"]), 3))))
    p("       +-%s %% over temperature, +-%s %% after endurance; DC bias only lowers an X7R's capacitance) %s mJ. The MAXIMUM stays UNRESOLVED until a"
      % (fmt(A["c_temp"] * 100), fmt(A["c_endur"] * 100), fmt(round(A["tr"][0][5] * A["c_hi_f"], 3))))
    p("       supported capacitance envelope (tolerance, temperature and bias at the step's voltage) and the step's real shape and duration meet")
    p("       Milliohm's pulse rating, which the HoJLR2512 sheet does not print (R-101, R-117); in service VBAT rises through the pack's precharge")
    p("       contact and the charger's soft start, far slower than the loop's ringing; the capability pulse's 10 us rise likewise")
    p("     U16's own input: its VIN and BIAS move with U17 to POE_VIN, at most %s V under VBAT in the boost current-limit case (the transients above"
      % fmt(round(A["u17_mv_fault"] * 1e-3, 3)))
    p("       exceed it while they last); its UVLO and BIAS window are read against VBAT less that drop (the helper refuses a BIAS rail other than the")
    p("       input without a blocking diode, so both move)")
    p("     startup: the sheet: 'the bus voltage can be present with the supply voltage off, and reciprocally': MEETS (MAKER)")
    p("     a load dump: the vehicle reaches VBAT only through the front end and the charger, so VBAT's own bounds above hold: MEETS")
    p("     accuracy: VOS %s uV, %s mA; gain %s %% with R227's 1 %% and %s ppm/K over %s K (L4-E4's span): %s %% plus %s mA (INFERRED)"
      % (fmt(A["ina_vos_uv"]), fmt(round(A["u17_off_ma"], 2)), fmt(A["ina_gain"] * 100), fmt(round(A["r5_tcr"] * 1e6)), fmt(A["r5_span_k"]),
         fmt(round(A["u17_err_pct"], 3)), fmt(round(A["u17_off_ma"], 2))))
    p("       with the drift rows (SBOS547C p.5: %s ppm/C gain, %s uV/C offset) over the IC's %s K from 25 C (-20 C to %s C): %s %% plus %s mA;"
      % (fmt(round(A["ina_gain_drift"] * 1e6)), fmt(A["ina_vos_drift"]), fmt(round(A["ic_dt"], 2)), fmt(round(A["t_hot"], 2)), fmt(round(A["u17_err_drift_pct"], 3)), fmt(round(A["u17_off_drift_ma"], 3))))
    p("       at -20 C the drift alone is %s %% and %s mA (INFERRED)" % (fmt(round(A["u17_drift_m20"][0], 3)), fmt(round(A["u17_drift_m20"][1], 3))))
    p("     for the firmware (FW-A09): the readings are the PoE stage's INPUT current and POE_VIN (VBUS pin 8 is on POE_VIN; VBAT is POE_VIN plus the")
    p("       shunt's drop); full scale %s A, Current_LSB %s mA, CAL %s; a full-scale sample is a saturated transient, not a current reading"
      % (fmt(round(A["u17_fs_a"], 3)), fmt(round(A["u17_lsb"] * 1e3, 3)), fmt(round(A["u17_cal"], 1))))
    p("       (0.00512 over Current_LSB x R); the PoE output power is inferred as the input power times the stage's efficiency (0.88, undocumented)")
    return L


# ------------------------------------------------------------------------- the update round: E11-19, the selected entry
def rejudge(F, D, A):
    """E11-19: every finding that rested on the LM5069's power limit, re-judged for the selected TPS48110-Q1 entry from L4-E11's
    fault scan and charts (read, never retyped), with the start's I2t through F1 and the hot short's inductance bound reproduced."""
    E = {}
    oc, sc, tau, tsc = F["e_oc"], F["e_sc"], F["e_tau_us"], F["e_tsc_us"]
    t_add = tau[2] + tsc[1]                                              # us, the filter's largest time constant and PD's maximum
    if abs(t_add - F["e_hs_svc"]["t_us"]) > 1e-6:
        refuse(4, "the hot short's added time does not reproduce L4-E11's")
    hs = F["e_hs_svc"]
    E["l_min_uh"] = hs["v"] * t_add / (hs["lim"] - sc[2])
    if abs(E["l_min_uh"] - hs["l_uh"]) > 0.005:
        refuse(4, "the hot short's inductance bound does not reproduce L4-E11's %s uH" % hs["l_uh"])
    if abs(hs["idm"] * hs["der"] - hs["lim"]) > 0.05 or abs(hs["der"] - F["e_derate"]) > 1e-9 or abs(F["e_derate"] - round(A["soa_derate"], 4)) > 1e-9:
        refuse(4, "Q7's derated IDM is not L4-E9's derating times the IDM")
    # Q7's chart derating carried from the CSD19532Q5B's case to the CSD19536KTT's 175 C rating: the case at which it stays conservative
    E["tc_break"] = F["e_q7_tj"] - F["e_derate"] * (F["e_q7_tj"] - 25.0)
    E["rja_break"] = (E["tc_break"] - A["t_hot"]) / F["e_q7_w"]
    # the start's I2t through F1 (rectangles: the largest current for the longest time of each pulse)
    rf_min = F["e_rf_range"][0]
    pk_rf = sc[2] + F["e_slew"][2] / rf_min * t_add * 1e-3             # A: the filtered threshold plus the ramp over the filter and PD
    E["i2t"] = [
        ("the start's inrush, %s A for %s ms" % (fmt(F["e_inrush"][1]), fmt(F["e_start_ms"])), F["e_inrush"][1] ** 2 * F["e_start_ms"] * 1e-3),
        ("an overcurrent pulse, %s A for %s ms" % (fmt(oc[2]), fmt(F["e_oc_ms"][2])), oc[2] ** 2 * F["e_oc_ms"][2] * 1e-3),
        ("a start into a resistive fault, at most %s A (the breaker's highest) for the start's %s ms, then at most %s A (%s A plus %s V/ms over %s Ohm"
         " for %s us) for %s ms" % (fmt(oc[2]), fmt(F["e_start_ms"]), fmt(round(pk_rf, 2)), fmt(sc[2]), fmt(F["e_slew"][2]), fmt(rf_min), fmt(t_add),
                                   fmt(round(F["e_oc_ms"][2] + t_add * 1e-3, 3))),
         oc[2] ** 2 * F["e_start_ms"] * 1e-3 + pk_rf ** 2 * (F["e_oc_ms"][2] + t_add * 1e-3) * 1e-3),
        ("a start into a hard short, %s A for %s us" % (fmt(F["e_hs_start"][2]), fmt(round(F["e_hs_start"][3] + tsc[1], 2))),
         F["e_hs_start"][2] ** 2 * (F["e_hs_start"][3] + tsc[1]) * 1e-6),
        ("a hard short in service, at most %s A (the specified loop floor at %s V) for %s us" % (fmt(F["ipf_spec"]), fmt(F["e_basis_v"]), fmt(t_add)),
         F["ipf_spec"] ** 2 * t_add * 1e-6),
    ]
    E["pk_rf"] = pk_rf
    E["i2t_max"] = max(x for _n, x in E["i2t"])
    E["i2t_pct"] = E["i2t_max"] / A["f_i2t"] * 100.0
    # Q1 at the selected breaker's highest current (the largest current it carries continuously)
    E["q1_p_sel"] = oc[2] ** 2 * A["rds10"][1] * 1e-3 * CSD_RDS_NORM_150C
    E["q1_tj_sel"] = F["air"][1] + E["q1_p_sel"] * A["rja"]
    # the entry's losses from a 9.00 V plug at the in-service maximum (L4-E11's hot loop), on the source's side
    i = F["e_svc"][1]
    E["loss_dcp"], E["loss_vr"] = i ** 2 * F["e_loop_mohm"][0] * 1e-3, i ** 2 * F["e_loop_mohm"][1] * 1e-3
    # D-02 on the selected over-voltage lockout, and D10 at its maximum
    E["cs101_margin"] = F["e_ov_off"][0] - A["cs101_top"]
    E["d10_margin"] = (F["SMCJ40A"]["vbr_min"] - F["e_ov_off"][2], A["d10_cold_vbr"] - F["e_ov_off"][2])
    E["guard_gap"] = F["knee_hiz"] - F["guard_sel"][2]
    return E


def rejudge_lines(F, D, A, E):
    L = []
    p = L.append
    hs, oc, sc = F["e_hs_svc"], F["e_oc"], F["e_sc"]
    p("12. THE UPDATE ROUND (2 October 2026): E11-19, THE SELECTED ENTRY, AND THE ACCEPTED RESULTS OF L4-E10, L4-E11 AND L4-E12")
    p("   the inputs: L4-E10 (79b2f568, closing check 573c8b8f: FEA-008 not closed, approach (II) CONDITIONAL); L4-E11 (3298d1f1, closing check")
    p("     a15ab384: the vehicle entry replaced, D-06 resolved in design, U-04's arrangement (A), REQ-015 at 9.00 V at the plug a CONDITIONAL CANDIDATE);")
    p("     L4-E12 (a86be47b, closing check db41c95d: U-02 CONDITIONAL, CFL-002 an owner question); L4-E13 (U-03) then pending, since accepted (section 13)")
    p("   12a. E11-19: THE FINDINGS THAT RESTED ON THE LM5069'S POWER LIMIT, RE-JUDGED FOR THE SELECTED ENTRY (TPS48110-Q1 with a CSD19536KTT,")
    p("     R19 4.5 mOhm, L2 SRF1260-1R0Y; L4-E11 3c, its fault scan and Q7's Figure 4-10 read from TI's vector drawing)")
    p("     what changes: the selected entry limits no power. It is a breaker: a timed overcurrent at %s / %s / %s A after %s / %s / %s ms and a"
      % (*[fmt(x) for x in oc], *[fmt(x) for x in F["e_oc_ms"]]))
    p("       short-circuit trip at %s / %s / %s A on a sense filtered at %s to %s us, then %s / %s us; retry %s s; the start is slew-limited"
      % (*[fmt(x) for x in sc], fmt(F["e_tau_us"][0]), fmt(F["e_tau_us"][2]), fmt(F["e_tsc_us"][0]), fmt(F["e_tsc_us"][1]), fmt(F["e_retry_s"])))
    p("       (%s to %s A for at most %s ms). So the LM5069's power-limit pulse (%s A at %s V for the fault time), its 5 mV sense floor (D-07), its fault"
      % (fmt(F["e_inrush"][0]), fmt(F["e_inrush"][1]), fmt(F["e_start_ms"]), fmt(round(A["pulse_a"], 3)), fmt(round(F["ovlo_sel"][2], 2))))
    p("       time against the start (D-09) and its breaker's event (VCB's %s A) do not exist in the selected entry; they stand only for the" % fmt(round(A["cb_thr"], 3)))
    p("       alternative while the LM5069 stays (R24 22k with C5 and C121, L4-E11's apply_gen_sch_e_timer.py)")
    p("     (1) the hot short at the start: a start into a resistive fault (%s to %s Ohm, the breaker at its slowest) reaches %s of Q7's derated chart"
      % (fmt(F["e_rf_range"][0]), fmt(F["e_rf_range"][1]), fmt(F["e_rf"][0])))
    p("       at %s Ohm, ended by the short-circuit trip at %s ms (the drawn CSD19532Q5B %s: NOT MET); the ordinary start %s; a start into a hard short"
      % (fmt(F["e_rf"][1]), fmt(F["e_rf"][2]), fmt(F["e_rf_drawn"][0]), fmt(F["e_rf"][3])))
    p("       %s A after %s us, %s of the derated 100 us line (CONDITIONAL on TI's typical %s S taken as the bound, A11-10): MEETS (INFERRED, L4-E11)"
      % (fmt(F["e_hs_start"][2]), fmt(F["e_hs_start"][3]), fmt(F["e_hs_start"][4]), fmt(F["e_hs_start"][1])))
    p("     (2) the hot short in service (Q7 on): the peak is at most %s A plus VIN x %s us / L and never more than VIN over the loop's resistance;"
      % (fmt(sc[2]), fmt(hs["t_us"])))
    p("       Q7's IDM %s A derated by %s is %s A, which at the OV maximum %s V holds for L at least %s uH (this record: %s V x %s us / (%s - %s) A;"
      % (fmt(hs["idm"]), fmt(hs["der"]), fmt(hs["lim"]), fmt(hs["v"]), fmt(round(E["l_min_uh"], 3)), fmt(hs["v"]), fmt(hs["t_us"]), fmt(hs["lim"]), fmt(sc[2])))
    p("       L4-E11 %s uH). No held document gives the loop's inductance, and the specified loop floor bounds only its resistance (%s A at %s V):"
      % (fmt(hs["l_uh"]), fmt(F["ipf_spec"]), fmt(F["e_basis_v"])))
    p("       OPEN, carried as E11-20 (R-134): the inductance at least %s uH, or the peak through Q7 measured at most %s A" % (fmt(hs["l_uh"]), fmt(round(hs["lim"]))))
    p("     (3) Q7's chart derating: L4-E9's %s (a %s C case on a 150 C part) applied to the CSD19536KTT (TJ %s C) stays conservative while its case is"
      % (fmt(F["e_derate"]), fmt(round(A["tc_max"], 1)), fmt(F["e_q7_tj"])))
    p("       at or under %s C, which at its %s W in the hottest inside air the record holds (%s C) needs a junction-to-air resistance under %s C/W (INFERRED)"
      % (fmt(round(E["tc_break"], 2)), fmt(F["e_q7_w"]), fmt(round(A["t_hot"], 2)), fmt(round(E["rja_break"], 1))))
    p("     (4) D-07 (the LM5069's power limit under TI's 5 mV): SUPERSEDED for the selected entry, which has no power limit; R24 22k stays the alternative's")
    p("     (5) R-118 (the breaker's event and the power limit on the bench): SUPERSEDED by E11-17, R-118 restated: the selected entry at 43 V, the trip")
    p("       thresholds apart from the peak currents, a start into a resistive fault near %s Ohm and into a hard short (at most %s A); D-09's rows only if"
      % (fmt(F["e_rf"][1]), fmt(round(F["e_hs_start"][2]))))
    p("       the LM5069 is kept")
    p("     (6) the start's I2t through F1 (the 0997's typical melting %s A2s, arcing excluded; rectangles, conservative):" % fmt(A["f_i2t"]))
    for nm, x in E["i2t"]:
        p("       %s: %s A2s" % (nm, fmt(round(x, 4))))
    p("       the largest is %s %% of %s A2s: F1 does not open first (INFERRED; the retry's repetition every %s s is not judged against a pulse-cycle"
      % (fmt(round(E["i2t_pct"], 2)), fmt(A["f_i2t"]), fmt(F["e_retry_s"])))
    p("       curve, none held); continuous currents up to the breaker's %s A sit under F1's 80 C column %s A (IF-04); the alternative's longest start %s A2s (L4-E11)"
      % (fmt(oc[2]), fmt(A["f_allow"]), fmt(F["alt_f1_i2t"])))
    p("     (7) IF-05: NOT MET (D-09 at C5's printed corners) becomes CONDITIONAL: every start inside Q7's derated chart, the in-service hard short OPEN (E11-20)")
    p("     (8) D-09 (the LM5069's fault time against its start): SUPERSEDED by the replacement; it applies only if the LM5069 is kept, where L4-E11")
    p("       resolved it with C5 GRM3195C1H104GA05 and C121 GRM3195C1H683JA05: %s to %s ms against %s ms (its start %s ms at the corners, 34 uF), the pulse"
      % (fmt(F["alt_tflt"][0]), fmt(F["alt_tflt"][1]), fmt(F["alt_need"]), fmt(F["alt_start"])))
    p("       %s A against %s A at the maximum (CONDITIONAL on the power law past 10 ms); this record's round-two figures (section 11) are that alternative's first reading"
      % (fmt(F["alt_pulse"]), fmt(F["alt_soa"])))
    p("     (9) D-02 (CS101 at 36 V against the over-voltage lockout): carried by the selected entry's OV, off above %s / %s / %s V: %s V under its %s V"
      % (*[fmt(x) for x in F["e_ov_off"]], fmt(round(A["cs101_top"], 2)), fmt(F["e_ov_off"][0])))
    p("       minimum, %s V in hand; its maximum %s V stays %s V under D10's %s V and %s V under its typical %s V at -20 C, so a steady input does not reach"
      % (fmt(round(E["cs101_margin"], 2)), fmt(F["e_ov_off"][2]), fmt(round(E["d10_margin"][0], 2)), fmt(F["SMCJ40A"]["vbr_min"]), fmt(round(E["d10_margin"][1], 2)), fmt(round(A["d10_cold_vbr"], 2))))
    p("       D10 cold (the alternative's %s V did); the prospective-current basis stays %s V (L4-E11 keeps it, conservative)" % (fmt(round(F["ovlo_sel"][2], 2)), fmt(F["e_basis_v"])))
    p("     new material defects from E11-19: none. Open evidence it leaves: the loop's inductance (E11-20), the transconductance bound of the start into")
    p("       a hard short (A11-10, E11-17) and the input current's transients against the breaker's %s ms (E11-06, E11-21)" % fmt(F["e_oc_ms"][0]))
    p("   12b. the selected entry's other figures (L4-E11 3c, 3e): UVLO on at %s / %s / %s V, off at %s / %s / %s V of DC_P; from a 9.00 V plug DC_P is %s V"
      % (*[fmt(x) for x in F["e_uv_on"]], *[fmt(x) for x in F["e_uv_off"]], fmt(F["e_dcp_noload"])))
    p("     before any current and %s V at %s A (VIN_RAW %s V), %s %% under the breaker's lowest, with the front end at least %s (CONDITIONAL, E11-06);"
      % (fmt(F["e_svc"][2]), fmt(F["e_svc"][1]), fmt(F["e_svc"][0]), fmt(F["e_margin_pct"]), "%s" % F["e_eta_floor"]))
    p("     the drawn LM5069 sees %s V there, under POREN's %s V maximum, so it cannot start (NOT MET as drawn); the losses from the plug at %s A: %s W to"
      % (fmt(F["lm_vin_9"]), fmt(F["lm_poren"]), fmt(F["e_svc"][1]), fmt(round(E["loss_dcp"], 3))))
    p("     DC_P (%s mOhm hot) and %s W on to VIN_RAW (%s mOhm), %s W, on the source's side; Q1 at the breaker's highest %s A: %s W, its junction at most"
      % (fmt(F["e_loop_mohm"][0]), fmt(round(E["loss_vr"], 3)), fmt(F["e_loop_mohm"][1]), fmt(round(E["loss_dcp"] + E["loss_vr"], 3)), fmt(oc[2]), fmt(round(E["q1_p_sel"], 3))))
    p("     %s C in %s C air (INFERRED); U6's VS at the clamps' %s V against %s V (%s V absolute), its pins at most %s V against %s V; Q7 (CSD19536KTT) %s V"
      % (fmt(round(E["q1_tj_sel"], 1)), fmt(F["air"][1]), fmt(F["e_pins"][0]), fmt(F["e_vs"][0]), fmt(F["e_vs"][1]), fmt(F["e_pins"][1]), fmt(F["e_pins"][4]), fmt(F["e_q7_sel_v"])))
    p("     the corrected knee (E11-09, a specification): a flat %s A of board current from VIN_RAW %s V to %s V, HIZ certain below %s V; the restart"
      % (fmt(F["knee"][0]), fmt(F["knee"][1]), fmt(F["knee"][2]), fmt(F["knee_hiz"])))
    p("     guard with R14 76.8k (E11-02) falls at %s / %s / %s V, %s V under it (as drawn %s / %s / %s V, over the 9.00 V plug's %s V: NOT MET as drawn)"
      % (*[fmt(x) for x in F["guard_sel"]], fmt(round(E["guard_gap"], 3)), *[fmt(x) for x in F["guard_drawn"]], fmt(F["e_svc"][0])))
    o = F["d06_oblig"]
    p("   12c. D-06 resolved in design (L4-E11 6): every element of the interconnect at least %s A continuous where installed, %s A for %s s and %s A"
      % (fmt(o[0]), fmt(o[1]), fmt(o[2]), fmt(o[3])))
    p("     for %s s, and from %s A to %s A at least F1's total clearing I2t at %s A and 58 V DC (not printed); the loop specified by its resistance, at least"
      % (fmt(o[4]), fmt(o[3]), fmt(F["ipf_spec"]), fmt(F["ipf_spec"])))
    p("     %s mOhm at 20 C (%s mOhm at -20 C: %s A at %s V, %s A at the OV maximum), at most %s mOhm, accepted four-wire at %s to %s mOhm (the"
      % (fmt(F["loop_floor"]), fmt(F["loop_floor_cold"]), fmt(F["ipf_spec"]), fmt(F["e_basis_v"]), fmt(F["ipf_spec_ov"]), fmt(F["loop_ceil"]), fmt(F["loop_acc"][0]), fmt(F["loop_acc"][1])))
    p("     construction, 3.05 m of AWG 14 and the 0.5 m lead, %s A); J_DCIN a %s A class; its evidence items E11-10 to E11-16 (R-129 to R-132, R-43, R-95,"
      % (fmt(F["ipf_constr"]), fmt(F["jdcin_sel_a"])))
    p("     R-113, R-115); the drawn interconnect (VH with AWG 18, size 16 contacts, the cable) stays NOT MET as drawn")
    env = F["e_env"]
    p("   12d. U-04 (L4-E11): arrangement (A) selected with rules R-a to R-d; at a 9.00 V plug the source delivers %s to %s W at VBAT (%s to %s W at"
      % (fmt(env[9][1]), fmt(env[9][2]), fmt(env[12][1]), fmt(env[12][2])))
    p("     12 V, %s to %s W at 24 V, %s to %s W at 36 V); the shedding sequence carries the warm-up (%s W at the plan figure) with %s W in hand while"
      % (fmt(env[24][1]), fmt(env[24][2]), fmt(env[36][1]), fmt(env[36][2]), fmt(F["e_p2"][1]), fmt(F["e_p2_hand"])))
    p("     P1 stays at most %s W (P1 %s / %s / %s W); R-b's dead-pack charge at most %s W from DPM's surplus, Q2's diode at most %s C (CONDITIONAL, E11-22);"
      % (fmt(F["e_p1_max"]), *[fmt(x) for x in F["e_p1"]], fmt(F["rb_w"]), fmt(F["rb_q2_tj"])))
    p("     REQ-015 at 9.00 V at the plug a CONDITIONAL CANDIDATE on E11-05, E11-06, E11-09, E11-22 and E11-23")
    p("   12e. U-02 (L4-E12): T-H1's binding line %s W/K lid open with the fans (E5 under the hold, %s W plus the ballasts' %s W = %s W over %s K);"
      % (fmt(F["gc"]), fmt(F["e5_hold_w"]), fmt(F["ballast_w"]), fmt(round(F["e5_hold_wb"], 3)), fmt(F["e5_line"] - F["e5_amb"])))
    p("     E3-O alone %s W/K (%s W plus %s W = %s W over %s K); %s W/K with no hold; at the line E3-O's mixed air %s C and E5's %s C; the hold's reference"
      % (fmt(F["g_e3o"]), fmt(F["e3o_stage_w"]), fmt(F["ballast_w"]), fmt(round(F["e3o_wb"], 3)), fmt(F["e5_line"] - F["e3o_amb12"]), fmt(F["g_a"]), "%.2f" % F["e3o_line"], "%.2f" % F["e5_line"]))
    p("     within +-%s K; LO-01a's floor %s W/K with the ballasts; at the floor with no hold %s / %s C (the design as it stands); the SGP41 off at %s C"
      % ("%s" % F["hold_ref"], fmt(F["lo01a_ball"]), "%.2f" % F["floor_air"][0], "%.2f" % F["floor_air"][1], "%.1f" % F["sgp_off"]))
    p("     and used at or under %s C on a TMP117; %d lines cleared only by an absolute rating (least clearance %s K); CFL-002 raised to the owner"
      % ("%.1f" % F["sgp_on"], F["abs_only"][0], fmt(F["abs_only"][1])))
    low = lambda s: s[0].lower() + s[1:]
    p("     (A, B or C: %s; %s; %s)" % (low(F["cfl002"][0]), low(F["cfl002"][1].rstrip(".")), low(F["cfl002"][2])))
    p("   12f. U-01 (L4-E10): unchanged; LO-01a's floor with the ballasts, %s W/K (L4-E12), lies under the binding line. U-03: section 13 (L4-E13)"
      % fmt(F["lo01a_ball"]))
    return L


def round5_expect(F):
    """The round's figures each architecture-level choice must quote as its record printed them (refused otherwise, exit 4)."""
    r = F["r5"]
    rg = r["ranges"]
    return {
        "U-01": ["%s A to %s V from T1" % (rg[0][5], rg[0][7]), "%s A to %s V from T2" % (rg[1][5], rg[1][7]),
                 "the drawn %s A to %s V from T5" % (rg[2][5], rg[2][7]), "UTC %s C" % r["thr"][0], "the kit's hold below %s C" % r["hold"],
                 "usable energy %s Wh (%s h) against the 35E's %s Wh (%s h) at +25 C, %s %% less" % (r["hl"] + r["e35"] + (r["hl_pct"],)),
                 "%s to %s Wh with the cells at -5.52 C" % r["cold"], "%s to %s Wh from a cold start at -20 C" % r["start"],
                 "under %s C makes H1 act" % r["idle"][0], "under %s C E5's cells pass it" % r["idle"][1], "under %s C\nE3-O" % r["idle"][2],
                 "under %s C E3-S fails" % r["idle"][3], "under %s C E3-O's cells pass it" % r["idle"][4], "(%s to %s W into the sealed case" % r["cooler"],
                 "%s to %s Wh of added storage" % r["prim"], "under %s A a cell back to (I)" % r["dis"], "(%s Wh\nper 100 mAh" % r["per100"],
                 "at least %sC" % r["crate"], "ten questions",
                 "%s Wh nominal, %s to %s Wh usable, %s to %s h battery-only" % tuple(fmt(x) for x in F["cb"]["u1"]["energy"]),
                 "at most %.2f mm of wrap" % F["cb"]["u1"]["wrap"][0], "NZ$ %s for" % fmt(F["cb"]["u1"]["cost"][1]),
                 "the cells at %s to %s C over its +60 C" % F["cb"]["u1"]["e35_e3o"], "the idle pack at %s C" % F["cb"]["u1"]["e35_e5"],
                 "the pocket's room as designed %s L" % F["cb"]["u1"]["room"], "NZ$ %s a cell; 10 A continuous" % F["cb"]["u1"]["pulse_cost"],
                 "'Can vary depending on temperatures' (its footnote 2)", "the limited sample qualification (L4-E10 10g)"],
        "U-02": fx_u02_expect(F),
        "U-04": fx_u04_expect(F),
    }


def fx_u02_expect(F):
    """U-02's figures as L4-E12's fix round printed them (12a to 12e; the review's B3, B4 and B7)."""
    fx, rc = F["fx"], F["rc"]
    M = fx["modes"]
    sh = {c["mode"]: c["short"] for c in fx["iii"]}
    k = fx["k78"]
    return ["%s W/K on the pack (M1 lid open, M3 lid closed; a reading of at least %s W/K)" % M["M1"]["ruled"][1:],
            "%s W/K on shore (M2, M4; at least %s W/K)" % M["M2"]["ruled"][1:],
            "%s W/K on the pack (at least %s W/K), %s W/K on shore (at least %s W/K)" % (M["M1"]["cab"][1:] + M["M2"]["cab"][1:]),
            "C1's air trigger, %s W/K (at least %s W/K)" % M["M5"]["ruled"][1:],
            "%s W/K (at least %s W/K), the maker-stated alternative the RB9704's +70 C, %s W/K (at least %s W/K)" % (M["M6"]["ruled"][1:] + M["M6"]["stated"][1:]),
            "LimeSDR's +70 C storage row, %s W/K (at least %s W/K)" % M["M7"]["stated"][1:],
            "%s and %s W/K (at least %s and %s W/K)" % (M["M8"]["ruled"][1], M["M9"]["ruled"][1], M["M8"]["ruled"][2], M["M9"]["ruled"][2]),
            "above a %.1f C reading and switches the sensor off at %.1f C" % (fx["c_cover"], fx["c_off"]),
            "%s W/K at K1's rise, correcting %s to %s W/K" % ("%.3f" % rc["capk1"][0], "%.3f" % rc["cap"][0], "%.3f" % fx["capfix"][1]),
            "short by %s W/K, %s W; M4" % sh["M3"], "short by %s W/K, %s W; M6" % sh["M4"], "short by %s W/K, %s W; M7" % sh["M6"], "the whole %s W" % sh["M7"][1],
            "%.3f W in less %.3f W stored = %.3f W, %.3f W with" % (fx["bal"][0], fx["bal"][1], fx["bal"][3], fx["bal_b"][1]),
            "needs %s and %s W/K (readings %s and %s W/K)" % (k[1][2], k[3][2], k[1][3], k[3][3]),
            "at %s to %s h on the bound, the run with the shed states %s to %s h" % tuple(fmt(x) for x in fx["c1"][:4]),
            "%s h unshed is energy only" % fmt(fx["eonly"][0]),
            "a plate fraction of %s needs %s W/K, %s needs %s W/K" % tuple(fmt(x) for x in fx["plate"]),
            "+%s to +%s C on the pack, +%s to +%s C on shore" % tuple(fmt(x) for x in fx["voc_ceil"]),
            "(%s W into the case) needs %s and %s W/K" % tuple(fmt(x) for x in fx["chg_hs"])]


def fx_u04_expect(F):
    """U-04's figures as L4-E11's fix round printed them (15a to 15d; the review's B1 and B2)."""
    fx, b1 = F["fx"], F["cb"]["b1"]
    return ["at least %s V (LDO mode)" % b1["vsys_min"], "SRN under %s V at least %s V, over %s V VSRN + %d mV within +-%d %%" % (fmt(fx["pw"][0]), fmt(fx["pw"][1]), fmt(fx["pw"][2]), b1["inhib"][0], b1["inhib"][1]),
            "between at least %s V" % fmt(fx["pw"][3]), "down to %s V: the system node %s to %s V" % (fmt(fx["supp"][0]), fmt(fx["vsys_rng"][0]), fmt(fx["vsys_rng"][1])),
            "drains total %s mA, the bench reads the held pack current at most %s mA" % (fmt(fx["held"][0]), fmt(fx["held"][1])),
            "a latch within %s s" % fmt(fx["latch_s"]), "at the %s C/W bar" % fmt(fx["bar"][0]), "at %s C (R-159's fallback" % fmt(fx["svc_tj"]),
            "%s A against each FET's ISM %s A" % (fmt(fx["dock"][0]), fmt(fx["dock"][1])), "a share of at most %s" % fmt(fx["dock"][2]),
            "at most %.5f A, no charge under %s V on SRN" % (fx["pre"][0], fmt(fx["pre"][1])),
            "%s W in the pair at PS-IDLE-SPEC (%s %% of the pack's output)" % (fmt(fx["pair_idle"][1]), fmt(fx["pair_idle"][2])),
            "L2 at %s A peak against Isat %s A" % (fmt(fx["l2"][2]), fmt(fx["l2"][3])), "%d of the %d row blocks" % b1["rows_same"],
            "the %s V margin" % b1["margin"], "LCSC %s" % fx["pair"][0], "Q-TI-3", "P1 at most %s W" % fmt(F["e_p1_max"]),
            "the source's least %s W at VBAT" % fmt(F["e_env"][9][1])]


def round5_lines(F, st, reg):
    r = F["r5"]
    L = []
    p = L.append
    p("14. UPDATE ROUND 5: LAYER 4'S REMAINING DEPENDENCIES (the owner's instruction of 2 October 2026; L4-E10, L4-E12 and L4-E11, each")
    p("   accepted by the coordinator's check 4: L4-E10 at e464ff88, L4-E12 at c933724e, L4-E11 at f1856bfd, merged into this line; their")
    p("   outputs and pages re-pinned in section 0 with the three checks, T-H1-PROCEDURE-DRAFT.md and TI-QUESTIONS.md)")
    p("   U-01, L4-E10 out 9 (the limits by mode MAKER-PAGE; the charge drafts SESSION, never applied; the energy INFERRED, its ageing an ASSUMPTION):")
    for nm, ta, tb, lo, hi, cur, vc, vp, ovp in r["ranges"]:
        p("     charge %s, %s to %s (%s to %s C on the page): %s A to %s V (%s V a cell; BATOVP %s V)" % (nm, ta, tb, lo, hi, cur, vp, vc, ovp))
    th = r["thr"]
    p("     thresholds: UTC %s C (recovery %s C), T1 %s C, T2 %s C, T5 %s C, T3 %s C, T4 %s C, OTC %s C; the kit's hold below %s C; CUV %s to %s V"
      % (th + (r["hold"],) + r["cuv"]))
    p("       a cell; the termination current %s mA (TI's default, ASSUMPTION)" % r["term"])
    p("     usable energy at +25 C (PS-IDLE-SPEC, aged 0.80): the HL18650V %s Wh (%s h) against the 35E's %s Wh (%s h), %s %% less; the cold end"
      % (r["hl"] + r["e35"] + (r["hl_pct"],)))
    p("       brackets only (ASSUMPTION): %s to %s Wh with the cells at -5.52 C, %s to %s Wh from a cold start at -20 C" % (r["cold"] + r["start"]))
    w = {x[0]: x for x in r["warm"]}
    p("     the warm-up of a cold-soaked block from -20 C, out of usable energy: to T1 %s to %s Wh; to T2 %s to %s Wh; to T5 %s Wh, or not reached"
      % (w["T1"][3], w["T1"][5], w["T2"][3], w["T2"][5], w["T5"][3]))
    p("       at the high corner (the mat alone stops at %s C)" % w["T5"][6])
    p("     this record keeps L4-E10's first chain in out 8 and the page's Appendix A (%s against %s Wh, which L4-E10 reads back from the page); the"
      % (fmt(F["cell_usable"][1]), fmt(F["cell_usable"][0])))
    p("       round's chain gives %s against %s Wh, the same %s Wh of growth in every shortfall: no figure of this record moves"
      % (r["hl"][0], r["e35"][0], r["growth"]))
    p("     what the signed specification would change: an idle hot limit under %s, %s, %s, %s or %s C (H1 acting in E5's dwell, E5's cells, E3-O's"
      % r["idle"])
    p("       'no shutdown', E3-S, E3-O's cells); (I)'s cooler %s to %s W into the sealed case; (III) %s to %s Wh of added storage; continuous"
      % (r["cooler"] + r["prim"]))
    p("       discharge under %s A a cell back to (I); the charge current from +10 C at least %sC; %s Wh of usable energy per 100 mAh a cell"
      % (r["dis"], r["crate"], r["per100"]))
    p("     the request to Yichun Topwell Power: questions %d to %d (OW-2)" % (r["tw_q"][0], r["tw_q"][-1]))
    b = r["basis"]
    p("   U-02, L4-E12 out 8:")
    p("     the line: %s W (%s W and the ballasts' %s W) over (%s - %s) K = %s W/K, at 0 K of margin; the fans are counted (pwr_budget.py's rows,"
      % b)
    p("       tier R), and the picked fans' power moves the line 0.100 W/K per W (%s to %s W/K over the representatives)" % r["fans"])
    p("     T-H1 by the drafted procedure: a pass at a reading of at least %s W/K at a 10 K rise (%s W/K at 20 K), the expanded uncertainty %s %%"
      % (r["pass"] + (r["unc"][0],)))
    p("       and %s %%; a point %s to %s h, the eight %s to %s h; the bench once the owner authorises it (OW-8)" % ((r["unc"][1],) + r["dur"]))
    f4 = r["f4"]
    p("     the fallbacks (the session's): F4 holds E5 down to %s W/K and E3-O down to %s W/K (%s W/K out of the exhaust); F3 (%s W) holds E5 to"
      % (f4[0], f4[1], f4[2], r["f3"][0]))
    p("       %s W/K; F4 with F3 holds E5 down to %s W/K; F1's fins multiply a reading by %s to %s or %s to %s; below E3-O's floor (%s W/K) the"
      % ((r["f3"][1], f4[3]) + r["f1"] + (f4[1],)))
    p("       remaining option is the owner's (a deviation of E3-O's configuration or a device-set re-pick, CHO-001)")
    p("     a stopped fan: E5's mixed air %s to %s C on W4's still values; the parts coupled to the plate at most %s C" % (r["stop"] + (r["plate_stop"],)))
    fr = [x for x in reg if x[0] == "R-150"]
    p("     L4-E12's drafted register row inserted as %s (%s, %s)" % (fr[0][0], fr[0][1], fr[0][4]))
    p("   U-04, L4-E11 out 9 to 11:")
    p("     rows %s to %s, each with what a maker's answer and what one bench sample can establish; ChargeCurrent at POR %s mA (TI's E2E answer)"
      % (r["drows"][0], r["drows"][-1], r["por"]))
    p("     D1: VSYS needs %s V against ChargeVoltage's floor %s V, a %s V margin once the mode is shown (one sample: that unit and revision)" % r["d1"])
    p("     the fallback E11-24 (R-152): %s mJ, %s ms of hold over the %s ms assumed for the worst admitted step (%s, %s W); the bank's charge"
      % (r["mj"], r["hold_ms"][0], r["hold_ms"][1], r["step"][0], r["step"][1]))
    p("       at most %s mA, %s W" % r["chg"])
    p("     the dependence on TI narrowed from %s to %s; remedies inside (A) for %s; none for %s and %s, whose negative answers return (B)"
      % (r["dep"] + r["remedy"]))
    p("     TI's questions (TI-QUESTIONS.md, OW-7): %s" % "; ".join("%s (%s)" % q for q in r["tiq"]))
    arch = [c["id"] for c in CHOICES if c["class"] == ARCH]
    p("   the choices (out 9 (b)): %s stay ARCHITECTURE-LEVEL CHOICES, each row with its question, its evidence by vendor, physical and owner,"
      % ", ".join(arch))
    p("     who supplies it, its fallback and what it could overturn; U-02's fallback is the session's down to %s W/K in E5 and %s W/K in E3-O,"
      % (f4[3], f4[1]))
    p("     the owner's below E3-O's floor; U-04 stays on %s and %s" % (r["remedy"][1], r["remedy"][2]))
    closed = all(g["verdict"] == "PASS" for g in GATE)
    p("   the gate: %s: criteria 1 and 5 on %s; criterion 2 %s with %d defects open (the rounds add none)"
      % ("CLOSED" if closed else "NOT CLOSED", ", ".join(arch), [g for g in GATE if g["n"] == 2][0]["verdict"], sum(1 for d in DEFECTS if d["state"] == "OPEN")))
    p("   the register: R-150 to R-154 new, R-114 restated (E11-25); from the findings ledger: R-102 (item 8), R-139 (item 5), R-155 (item 10)")
    p("     and R-156 (item 1, then PENDING L4-E7's surge round; restated in set 27, section 23); %d items" % len(reg))
    p("   the owner's items: OW-2 (ten questions), OW-7 (the TI request), OW-8 (T-H1's bench), OW-4 the other drafts: actions, not questions")
    return L


def round3_lines(F, D, A, E, st):
    L = []
    p = L.append
    a3, win, sp = F["e13_a3"], F["e13_win"], F["e13_spec"]
    p("13. UPDATE ROUND 3 (2 October 2026): L4-E13 ACCEPTED; U-03 A CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC)")
    p("   the input: L4-E13 at fae419d1 (accepted by the coordinator's check 3, 'Owner decision required: none'), updated after set 25 at")
    p("     33b6b7be (check 4: A-3(a) and A-4 on L4-E7R's regulation and backstop, the nominal hold's day 336.6 Wh); read from the tree and pinned")
    p("   route 1 (a maker's warranted band in the window, the hold inside the curve, portable), none qualifies today: %s"
      % "; ".join("%s bounded %s, hold %s" % x for x in F["e13_route1"]))
    p("     the drafts to SunPower and Solbian ask for a warranted band (OW-4); the owner sends them")
    p("   route 2 (one identified %s, recorded by serial number, measured), feasible on a unit equal to the typical rows:" % F["e13_unit"])
    p("     A-1 the window: Vm20 + U_V %s V against %s V at -20 C and 1000 W/m2, margin %s V; the window Voc25 %s to %s V, Vm20 at most %s V"
      % ("%s" % F["e13_a1"], "%.3f" % F["e13_a1_lim"], "%s" % F["e13_a1_margin"], "%s" % win[0], "%s" % win[1], "%.3f" % win[2]))
    p("     A-2 useful charging, measured on the conservative side: lower bound %s W above %s W" % ("%s" % F["e13_a2"], "%s" % F["e13_a2_line"]))
    p("     A-3 the entry: (a) %s A, the conservative bound kept, over L4-E7R's two layers as L4-E13 states them: the regulation (RIMON_IN 31.6k)"
      % ("%s" % a3[0]))
    p("       %s A nominal, at most %s A at 25 V under the joint assumptions; the backstop turns the stage off at its trip, at most %s A at 25 V"
      % ("%s" % F["e13_reg"][0], "%s" % F["e13_reg"][1], "%s" % F["e13_trip"][1]))
    p("       (%s A at its lowest); (b) %s A in a sustained input fault, inside F2's and J_SOLAR's 10 A;" % ("%s" % F["e13_trip"][0], "%s" % a3[1]))
    p("       (c) %s A in a double contingency at the design level %s W/m2, a COMPONENT_LIMITATION on J_SOLAR and PV_IN (a 20 A part covers it to"
      % ("%s" % a3[2], fmt(F["e13_gt"])))
    p("       %s W/m2, %s x E0)" % (fmt(F["e13_20a"][0]), fmt(F["e13_20a"][1])))
    p("     A-4 the 100 W on L4-E7R's two layers, both drafted: the regulation's own 25 V corner %s W, CONDITIONAL on its unprinted values; the"
      % ("%s" % F["e13_corner"]))
    p("       backstop's static bound %s W, margin %s W, CONDITIONAL on G_CM and the VIN+ bias (%s W at -20 C and 1000 W/m2 with no limit)"
      % ("%s" % F["e13_static"][0], "%s" % F["e13_static"][1], fmt(F["e13_a4_w"])))
    p("     the specification (k = 2): U_V %s V, U_A %s %%, U_I %s %%, U_G %s %%, U_TC %s K" % tuple(fmt(x) for x in sp))
    p("   the disturbance check, apart (TRN-001): a unit at A-1's ceiling reaches D4's %s V standoff at %s W/m2 (%s x E0) at n 2, a MODELLING_ASSUMPTION"
      % (fmt(F["e13_vr"]), fmt(F["e13_thr"][0]), fmt(F["e13_thr"][1])))
    p("     verified by M3's n (the typical unit's fit %s, %s with U_A); the irradiance below the threshold an ASSUMPTION" % (fmt(F["e13_n"][0]), fmt(F["e13_n"][1])))
    p("   the energy, each with its basis: the rated unit's nominal hold %s Wh a day under L4-E7R's accepted regulation (L4-E13 cites L4-E7 out"
      % ("%.1f" % F["e13_day_e7r"]))
    p("     10), %s Wh at L4-E7's first-round limit (the replay's basis, section 8's solar rows); the conditioned upper corner %s Wh on both"
      % ("%.1f" % F["e13_day"][1], "%.1f" % F["e13_day"][0]))
    p("     (the unit's current there under the regulation); a unit at A-2's floor %s Wh there; no figure is a measured unit's (R-52)" % ("%.1f" % F["e13_day"][2]))
    p("   what changes: U-03 leaves the choices that could overturn the architecture; criteria 1 and 5 name U-01, U-02 and U-04. It decides")
    p("     which unit, not the topology and not the source class: REQ-016's window, the stage, its hold and its 100 W control stay. It returns to")
    p("     an architecture-level choice only if route 2 proves infeasible with route 1 still closed (L4-E13's decision L4E13-06)")
    p("   IF-01 (%s): A-1 on the typical rows, A-3(b) inside F2 and inside J_SOLAR's VH at AWG 16 (R-29), A-3(c) OPEN (R-148), the disturbance" % st["IF-01"][1])
    p("     check CONDITIONAL on n (R-149)")
    if st["IF-01"][1] == "NOT MET":
        p("     (since set 27 IF-01 also carries the known defects D-10 and D-11 at the solar entry: section 23)")
    p("   the register: R-35 restated as PANEL-ACC, R-52 the unit's trace rerun, R-29 J_SOLAR's lead at A-3(b)'s current, R-148 A-3(c)'s rating")
    p("     for J_SOLAR and PV_IN (Layer 6; its interface text amends LH-02, no new handover row), R-149 M3's n at or under 2; the owner's items")
    p("     OW-6 (the purchase and the measurement) and the two route-1 drafts in OW-4")
    held = [g["n"] for g in GATE if g["verdict"] != "PASS"]
    arch = [c["id"] for c in CHOICES if c["class"] == ARCH]
    p("   the gate: NOT CLOSED (criteria %s): criteria 1 and 5 on %s, each still able to overturn the architecture on named evidence;"
      % (", ".join(str(n) for n in held), ", ".join(arch)))
    p("     criterion 2 CONDITIONAL on its rows' named evidence (no material defect open in this round; since set 27 the known defects D-10 and D-11,")
    p("     section 23); criteria 3 and 4 PASS")
    return L


# ------------------------------------------------------------------------------------------------------- the rows
def b1v(F):
    """The system node under (B1) after L4-E11's fix round (15d; E11-34's drafted IF text)."""
    fx = F["fx"]
    return ("; under (B1) VBAT %s to %s V (the supplement floor at OCD1's %s A; the held top), at least %s V with no pack and adequate input (L4-E11 15d)"
            % (fmt(fx["vsys_rng"][0]), fmt(fx["vsys_rng"][1]), fmt(fx["supp"][2]), fmt(fx["pw"][1])))


def rows(F, D, A, E):
    R = []
    sm40, sm28, sm18 = F["SMCJ40A"], F["SMCJ28A"], F["SMCJ18A"]
    pv = F["pv"]
    R.append({
        "id": "IF-01", "title": "the panel to board E's solar entry (J_SOLAR, F2, the sense bank, D4, C71 to C74, PV_IN, PV_P and TRK_VS)",
        "a": "the panel (PANEL-ACC: one %s by serial number, a CONDITIONAL DOWNSTREAM UNIT SELECTION, L4-E13; no unit bought or measured)" % F["e13_unit"], "b": "board E, PV_IN, PV_P and TRK_VS (L4-E7R's corrected entry)",
        "v": "panel: open circuit at most %s V at -20 C (REQ-016, gen PV_P v_max); PANEL-ACC's A-1 Vm20 + U_V at -20 C and 1000 W/m2 at most %s V, %s V on the typical rows (margin %s V), the window Voc25 %s to %s V; held at %s V nominal | entry: D4 %s standoff %s V on TRK_VS, reached by a unit at A-1's ceiling only above %s W/m2 at n 2; under CS101 the input at most %s V; TRK_VS at most %s V and PV_P %s V at the capability scenario"
             % (fmt(pv["v_max"]), "%.3f" % F["e13_a1_lim"], "%s" % F["e13_a1"], "%s" % F["e13_a1_margin"], "%s" % F["e13_win"][0], "%s" % F["e13_win"][1], fmt(F["hold"][1]), "SMCJ28A",
                fmt(sm28["vr"]), fmt(F["e13_thr"][0]), fmt(F["cs101_pv"]), fmt(F["trk_vs_max"]), fmt(F["pv_p_max"])),
        "i": "panel hot short circuit %s A with the sheet's power tolerance (L4-E7R; %s A nominal sheet); PANEL-ACC's A-3: (a) %s A in operation, the bound over L4-E7R's regulation and backstop, (b) %s A in a sustained input fault (SunPower's 1.25), (c) %s A in a double contingency at the design level %s W/m2 | F2 %s A blade, J_SOLAR VH (%s A at AWG 16, standard header; %s A at AWG 18, shrouded only; the lead is AWG 18 on a standard header: no stated rating); under CS101 the filtered ripple at the trip input at most %s A at %d Hz against the %s A margin"
             % (fmt(F["isc_hot_tol"]), fmt(F["cand_isc_hot"]), "%s" % F["e13_a3"][0], "%s" % F["e13_a3"][1], "%s" % F["e13_a3"][2], fmt(F["e13_gt"]), fmt(amps_in(F["e_f2"], "F2")), fmt(F["vh_16"]), fmt(F["vh_18"]),
                fmt(F["m2_ripple"]), F["m2_hz"], fmt(F["m2_margin"])),
        "loss": "the 5 m lead about 0.0465 Ohm (the replay's ESTIMATE); the sense bank %s Wh on SC-37's day, %s Wh on the bright day (L4-E7R)" % (fmt(F["bank_wh"][0]), fmt(F["bank_wh"][1])),
        "therm": "the entry at the worst inside air %s C (envelope, lid closed); the bulk cans' heating under CS101's bounding case, up to %s times their ripple rating, CONDITIONAL (M2 records it)" % (fmt(F["air"][1]), fmt(F["bulk_ripple_x"])),
        "prot_a": "none (a bare panel)", "prot_b": "D11 SMCJ40CA across the port and C131; F2; the solar guard (R-173, drafted): U21 TPS48110-Q1 over-voltage cut-off with Q12, Q13 in the return; the 50 V bulk on PV_P ahead of the sense bank; D4 (SMCJ30A drafted) one-way clamp and C71 to C74 on TRK_VS; the INB filter, %d x 100 nF C0G across R66 %s (%s to %s ms) (L4-E7R, drafted in apply_gen_sch_e_backstop.py)" % (F["filt_n"], F["r66"], fmt(F["tau_min_ms"]), fmt(F["tau_max_ms"])),
        "settled": "l4e (O-1), L4-E7R at 675b8068 (accepted, check 4 at 91e9a4b5), L4-E13 at fae419d1 (accepted, check 3; PANEL-ACC), L4-E7's panel-lead derivation at 6d76453e (set 27) and its solar-fault remedies (check 5 at 573fd5b8)", "checks": [
            Chk("PANEL-ACC A-1, the window: Vm20 + U_V at -20 C and 1000 W/m2 on a unit equal to the typical rows, within REQ-016's 25 V", F["e13_a1"], "<=", F["e13_a1_lim"], "V", "CONDITIONAL", "L4-E13 out 10 (INFERRED on the typical rows): the bought unit's own measurement M2 decides (R-35)"),
            Chk("D4's standoff above the window's 25 V", pv["v_max"], "<=", sm28["vr"], "V", "MAKER", "Littelfuse SMCJ row"),
            Chk("the panel's hot short circuit with the sheet's power tolerance inside F2", F["isc_hot_tol"], "<=", amps_in(F["e_f2"], "F2"), "A", "INFERRED", "L4-E7R out; gen F2"),
            Chk("PANEL-ACC A-3(b): a sustained input fault's current (Isc at +70 C, + U_I, x SunPower's 1.25) inside F2", F["e13_a3"][1], "<=", amps_in(F["e_f2"], "F2"), "A", "INFERRED", "L4-E13 out 10; gen F2"),
            Chk("A-3(b) inside J_SOLAR's VH rating with the lead at AWG 16 on the standard header (R-29's change; the drawn AWG 18 has no stated rating, the shrouded AWG 18 row's 7 A falls short)", F["e13_a3"][1], "<=", F["vh_16"], "A", "CONDITIONAL", "JST VH catalogue p.1; R-29"),
            Chk("PANEL-ACC A-3(c), a COMPONENT_LIMITATION: J_SOLAR and PV_IN carry %s A for a double contingency at the design level %s W/m2" % ("%s" % F["e13_a3"][2], fmt(F["e13_gt"])), None, "<=", None, "a rating or a bench row", "CONDITIONAL", "L4-E13 out 10 (JST VH prints 10 A, no short-time overload): R-148"),
            Chk("the disturbance check (TRN-001, apart from the window): A-3(c)'s design level, context and not a maximum, under the irradiance at which a unit at A-1's ceiling reaches D4's standoff at n 2", F["e13_gt"], "<", F["e13_thr"][0], "W/m2", "CONDITIONAL", "L4-E13 out 11: n <= 2 a MODELLING_ASSUMPTION verified by M3 (R-149); the irradiance below the threshold an ASSUMPTION"),
            Chk("D4 does not conduct under CS101 (the input's peak under its standoff)", F["cs101_pv"], "<", sm28["vr"], "V", "MODELED", "L4-E7R out (lumped model)"),
            Chk("TRK_VS at the capability scenario under the bulk's and the ceramics' 50 V", F["trk_vs_max"], "<=", 50.0, "V", "MODELED", "L4-E7R out (capability, not a requirement)"),
            Chk("PV_P at the capability scenario under U18's VIN+ %s V" % fmt(F["u18_vin"]), F["pv_p_max"], "<=", F["u18_vin"], "V", "MODELED", "L4-E7R out"),
            Chk("U5's sense differential under the approved disturbances and the capability scenario", F["u5_diff"], "<=", F["u5_diff_lim"], "V", "CONDITIONAL", "L4-E7R out: the lumped model, layout, M3, M7, bench 7b.18"),
            Chk("the backstop does not trip under TEST-PLAN M2 (CS101): the filtered ripple at its worst frequency under the margin (the trip's lowest less the regulation's highest)", F["m2_ripple"], "<=", F["m2_margin"], "A", "CONDITIONAL", "L4-E7R out (MODELED; the IMON_IN loop on typical rows, break-even %s times; M2 reads it)" % fmt(F["loop_breakeven"])),
            Chk("the 50 V bulk's heating under CS101's bounding case (up to %s times its ripple rating)" % fmt(F["bulk_ripple_x"]), None, "<=", None, "a measured temperature", "CONDITIONAL", "L4-E7R out; M2 records the cans' case temperature (R-122)"),
            Chk("the sense bank's pulse capability in the capability scenario", None, "<=", None, "a maker's pulse rating", "CONDITIONAL", "L4-E7R out; Vishay clarification (R-101)"),
            Chk("CS116 on PV_IN and the J_SOLAR cable (MIL-STD-461G 5.14 under REQ-063, L4-E7's D1), with the drafted guard and D4 the SMCJ30A (R-173): D4's clamp at %s A at the hot end at or under the drafted entry's %s V parts, the block on or off" % (fmt(F["sv"]["d1"][1]), fmt(F["sv"]["lim"])),
                F["sv"]["rm"]["d1d2"][0], "<=", F["sv"]["lim"], "V", "INFERRED", "L4-E7 out (the remedies: CS116 MEETS with the block on and off; check 5); D-12, R-156, R-174"),
            Chk("the same on the drawn entry's C11 and C12 (D4 the drawn SMCJ28A)", F["sv"]["d1"][0], "<=", F["sv"]["lim_drawn"], "V", "INFERRED", "L4-E7 out (D1); D-12", scope="drawn"),
            Chk("CS115 on the J_SOLAR cable (5.13, L4-E7's D2), with the guard: D4's clamp at %s A at the hot end at or under %s V" % (fmt(F["sv"]["d2"][1]), fmt(F["sv"]["lim"])),
                F["sv"]["rm"]["d1d2"][1], "<=", F["sv"]["lim"], "V", "INFERRED", "L4-E7 out (the remedies; the loop current recorded by R-174)"),
            Chk("CS115 with the block on: U5's differential at the generator's %s A calibration level, not a bound on the cable's current" % fmt(F["sv"]["d2"][1]),
                F["sv"]["rm"]["b6"]["u5_cs115"], "<=", F["u5_diff_lim"], "V", "CONDITIONAL", "L4-E7 out (B6's round): R-174, the cable's recorded loop current under 15.68 A, or U5's differential measured under 0.3 V; D-12"),
            Chk("a stiff %s V source stepping onto the port with the guard already on (the review's B6; D-10): U5's positive differential, the binding rating, at the lead's %s uH"
                % (fmt(F["sv"]["src"][1]), fmt(F["sv"]["rm"]["b6"]["l_uh"])),
                [r[1] for r in F["sv"]["rm"]["b6"]["rows"] if r[0] == F["sv"]["rm"]["b6"]["bind"]][0], "<=", F["u5_diff_lim"], "V", "CONDITIONAL",
                "L4-E7 out (THE GUARD ALREADY ON, MODELED): every rating MEETS from %s uH, NOT MET at %s uH; the lead's loop inductance is printed nowhere (R-176 row 2, R-180); D-10"
                % (fmt(F["sv"]["rm"]["b6"]["l_uh"]), fmt(F["sv"]["rm"]["b6"]["below"][0]))),
            Chk("a stiff %s V source on the port (L4-E7's D4; D-10) with the guard: the cut-off's highest rising threshold under the source, so the block never turns on" % fmt(F["sv"]["src"][1]),
                F["sv"]["rm"]["rise"][1], "<", F["sv"]["src"][1], "V", "INFERRED", "L4-E7 out (the remedies; TPS48110-Q1 SLUSEE5E 6.5, the divider aged); D-10, R-173 drafted"),
            Chk("the cut-off's highest rising threshold under D4's (the SMCJ30A's) least breakdown at the cold end", F["sv"]["rm"]["rise"][1], "<", F["sv"]["rm"]["s30"][3], "V", "INFERRED", "L4-E7 out (the remedies)"),
            Chk("the cut-off's least rising threshold over CS101's peak at the input (M2 never trips it)", F["sv"]["rm"]["rise"][0], ">", F["cs101_pv"], "V", "INFERRED", "L4-E7 out (the remedies)"),
            Chk("the cut-off's least falling threshold over REQ-016's %s V (a panel inside the window is never locked out)" % fmt(F["pv"]["v_max"]), F["sv"]["rm"]["fall"][0], ">", F["pv"]["v_max"], "V", "INFERRED", "L4-E7 out (the remedies)"),
            Chk("a reversed panel (E-N1, L4-E7's D5; D-11) with the guard: Q13 in the return off, its body diode reverse biased, no current; the high side's pins within 1 V of GND while Q13 leaks under %s uA, against %s uA printed at 80 V and 25 C only" % (fmt(F["sv"]["rm"]["q13"][0]), fmt(F["sv"]["rm"]["q13"][1])),
                None, "<=", None, "Q13's leakage above +25 C (no row printed)", "CONDITIONAL", "L4-E7 out (the remedies: MEETS, CONDITIONAL on Q13's leakage above 25 C); D-11, R-173 drafted", verdict=True),
            Chk("a stiff %s V source on the port without the guard (the drafted entry before R-173): D4's dissipation at the least it reaches inside its %s W on the board" % (fmt(F["sv"]["src"][1]), fmt(F["sv"]["d4_cap"][0])),
                F["sv"]["d4_rows"][3][3], "<=", F["sv"]["d4_cap"][0], "W", "INFERRED", "L4-E7 out (D4); D-10 as drawn", scope="drawn"),
            Chk("a reversed panel without the guard: D4 forward at %s A held inside %s W, which needs a forward drop under %s V" % (fmt(F["sv"]["d5"][0]), fmt(F["sv"]["d5"][1]), fmt(F["sv"]["d5"][2])),
                None, "<=", None, "no silicon junction drops under %s V at that current" % fmt(F["sv"]["d5"][2]), "INFERRED", "L4-E7 out (D5); D-11 as drawn", scope="drawn", verdict=False),
        ]})
    R.append({
        "id": "IF-02", "title": "PV_P to the LT8705A stage U5 (the hold, the regulation and the backstop on SWEN) to TRK_OUT",
        "a": "PV_P and TRK_VS (behind the sense bank, L4-E7R)", "b": "TRK_OUT",
        "v": "in: hold %s / %s / %s V (EA3 typical), %s to %s V conditioned (L4-E7), at most %s V; SWEN off by default below %s V on TRK_LDO33 | out: ceiling %s / %s / %s V (L4-E5, R10 232 k; as drawn %s / %s / %s V)"
             % (fmt(F["hold"][0]), fmt(F["hold"][1]), fmt(F["hold"][2]), fmt(F["hold_cond"][0]), fmt(F["hold_cond"][1]), fmt(pv["v_max"]), fmt(F["swen_v"]),
                fmt(F["trk_ceiling"][0]), fmt(F["trk_ceiling"][1]), fmt(F["trk_ceiling"][2]), fmt(F["trk_drawn"][0]), fmt(F["trk_drawn"][1]), fmt(F["trk_drawn"][2])),
        "i": "the regulation (RIMON_IN %s) %s A nominal, %s A at its highest on the hold's corners (%s W and %s W in); the backstop trips at %s to %s A at 25 V; the static bound %s W, the regulation's own 25 V corner %s W | out at the window %s W (stage %s DECLARED), a ceiling: the stage takes at most %s W in at the hold"
             % (F["rimon"], fmt(F["reg"][0]), fmt(F["reg"][1]), fmt(F["reg_w"][0]), fmt(F["reg_w"][1]), fmt(F["bs_trip"][0]), fmt(F["bs_trip"][1]), fmt(F["static_bound"]), fmt(F["reg_corner"]),
                fmt(D["trk_out_w"]), fmt(F["trk"]["efficiency"]), fmt(F["reg_w"][1])),
        "loss": "stage %s DECLARED (C-8, undocumented)" % fmt(F["trk"]["efficiency"]),
        "therm": "U5 junction about %s C (INFERRED) in %s C air against the I grade's 125 C" % (fmt(F["u5_tj"]), fmt(F["air"][1])),
        "prot_a": "the regulation (IMON_IN at RIMON_IN %s); the backstop on SWEN (the sense bank, U18 INA169, the INB filter, U19 TPS3701, U20 TPS3808), its response inside %s ms for 10 J in any 0.1 s after the filter's %s J held charge" % (F["rimon"], fmt(F["bs_allow_ms"]), fmt(F["held_j"])),
        "prot_b": "U4/Q2 ideal diode blocks the bus",
        "settled": "l4e7 (hold, grade), l4e5 (ceiling), L4-E7R at 675b8068 (accepted, check 4 at 91e9a4b5)", "checks": [
            Chk("the stage's input power at the 25 V corner, the backstop's static bound, against REQ-016's 100 W", F["static_bound"], "<=", 100.0, "W", "CONDITIONAL", "L4-E7R out: CONDITIONAL on G_CM and U18's VIN+ bias (break-evens %s %% and %s mA)" % (fmt(F["gcm_be"]), fmt(F["vinb_be"]))),
            Chk("the same at the panel entry with the solar guard's own currents around the bank (R-173, drafted)", F["sv"]["rm"]["static"][0], "<=", 100.0, "W", "CONDITIONAL", "L4-E7 out (the remedies, check 5): the same conditions"),
            Chk("the regulation's own 25 V corner against REQ-016's 100 W", F["reg_corner"], "<=", 100.0, "W", "INFERRED", "L4-E7R out"),
            Chk("the regulation's highest current under the backstop's lowest trip (no trip in normal operation)", F["reg"][1], "<", F["bs_trip"][0], "A", "CONDITIONAL", "L4-E7R out: the regulation's unprinted values inside the joint assumptions, else a hiccup"),
            Chk("the response from a step over the trip inside %s ms after the INB filter's %s J held charge (10 J in any 0.1 s; the 0.1 s interpretation is layer 8's; bench 7b.16)" % (fmt(F["bs_allow_ms"]), fmt(F["held_j"])), None, "<=", None, "an interpretation and a bench row", "CONDITIONAL", "L4-E7R out, check (b)"),
            Chk("U5's junction inside the I grade's 125 C", F["u5_tj"], "<=", 125.0, "C", "INFERRED", "l4e7 out 3"),
        ]})
    R.append({
        "id": "IF-03", "title": "TRK_OUT through U4/Q2 (ideal diode) onto VIN_RAW",
        "a": "TRK_OUT (C24, C25 35 V polymer; C26, C27 10u 25 V)", "b": "VIN_RAW (board E)",
        "v": "TRK_OUT at most %s V (raised ceiling) | VIN_RAW up to the vehicle's %s V basis with TRK_OUT at 0 (the selected OV maximum %s V; %s V as drawn)" % (fmt(F["trk_ceiling"][2]), fmt(round(F["ovlo_sel"][2], 2)), fmt(F["e_ov_off"][2]), fmt(F["ovlo"][2])),
        "i": "asked: at the window %s W out, at H3's lowest settle point (%s V) %s A | available: the declared _TRK_A %s A" % (fmt(D["trk_out_w"]), fmt(F["settle_865"][1]), fmt(round(D["trk_i_settle"], 3)), fmt(F["trk"]["typ"])),
        "loss": "Q2's RDS(on) (milliohms)", "therm": "inside air %s C" % fmt(F["air"][1]),
        "prot_a": "the stage's own limit", "prot_b": "U4 blocks VIN_RAW into TRK_OUT",
        "settled": "l4e5 (ceiling, C26/C27), this record (reverse)", "checks": [
            Chk("C26 and C27 (10u 25 V) at the raised ceiling", F["c26_pct"], "<=", 100.0, "% of rating", "NETLIST", "l4e5 out 3", scope="drawn"),
            Chk("C26 and C27 re-rated to a 50 V part (the drawn C13's 10u 50V) at the raised ceiling", F["trk_ceiling"][2], "<=", 50.0, "V", "NETLIST", "the owed re-rate, register R-14"),
            Chk("C24 and C25 (35 V polymer) at the raised ceiling, for the derating gate", F["c24_pct"], "<=", 100.0, "% of rating", "NETLIST", "l4e5 out 3"),
            Chk("Q2 (BSC039N06NS, 60 V) blocking the vehicle bus at the %s V basis (over the selected OV maximum) with TRK_OUT at 0" % fmt(round(F["ovlo_sel"][2], 2)), round(F["ovlo_sel"][2], 2), "<=", F["bsc039_vds"], "V", "MAKER", "out 11, out 12; Infineon p.1"),
            Chk("U4 (LM74700-Q1) cathode to anode at the %s V basis" % fmt(round(F["ovlo_sel"][2], 2)), round(F["ovlo_sel"][2], 2), "<=", F["ld_ca_abs"], "V", "MAKER", "TI SNOSD17G 6.1"),
        ]})
    E11 = "L4-E11 at 3298d1f1 (accepted, check a15ab384)"
    ovs = F["e_ov_off"]
    R.append({
        "id": "IF-04", "title": "the vehicle and shore input to board E's entry (the D38999 receptacle, J_DCIN, F1, D10, U3/Q1 LM74700 ideal diode) to DC_P",
        "a": "a vehicle or shore supply, 9 to 36 V at the kit's plug (REQ-015, the design basis L4-E11 took), reversed or at an over-voltage to 40 V", "b": "board E, DC_F and DC_P",
        "v": "9 to %s V in service, CS101's %s V peak on it under M2; reversed to -%s V | the selected entry's OV off above %s / %s / %s V (as drawn the LM5069's OVLO %s / %s / %s V; the alternative's %s / %s / %s V); D10 SMCJ40CA breakdown %s V minimum either way at 25 C, %s V at -20 C (typical coefficient)"
             % (fmt(D["vrev"]), fmt(round(A["cs101_pk"], 2)), fmt(D["vrev"]), *[fmt(x) for x in ovs], fmt(F["ovlo"][0]), fmt(F["ovlo"][1]), fmt(F["ovlo"][2]),
                *[fmt(round(x, 2)) for x in F["ovlo_sel"]], fmt(sm40["vbr_min"]), fmt(round(A["d10_cold_vbr"], 2))),
        "i": "asked: in service at most %s A from a 9.00 V plug; the breaker %s / %s / %s A; a stiff source's fault at most %s A (the specified loop floor, %s V basis; %s A with the drawn cable) | available: F1 Littelfuse 0997010.WXN 10 A (%s A at its %s C column), %s A at 58 V DC; Q1 CSD19532Q5B %s A; J_DCIN a %s A class (XT60 family) and the interconnect at least %s A continuous (D-06 resolved in design; the drawn VH with AWG %d has no stated rating)"
             % (fmt(F["e_svc"][1]), *[fmt(x) for x in F["e_oc"]], fmt(F["ipf_spec"]), fmt(F["e_basis_v"]), fmt(round(D["f1_ipf"], 1)), fmt(A["f_allow"]), fmt(A["f_col"]), fmt(A["f_int"]),
                fmt(A["id_cont"]), fmt(F["jdcin_sel_a"]), fmt(F["d06_oblig"][0]), int(F["lead_awg"])),
        "loss": "the plug to DC_P %s mOhm hot, %s W at %s A (L4-E11 3d); Q1 at most %s W at the breaker's %s A" % (fmt(F["e_loop_mohm"][0]), fmt(round(E["loss_dcp"], 3)), fmt(F["e_svc"][1]), fmt(round(E["q1_p_sel"], 3)), fmt(F["e_oc"][2])),
        "therm": "Q1's junction at most %s C in %s C air at %s A (INFERRED); the interconnect's elements at %s A continuous where installed (D-06; E11-10 to E11-14)" % (fmt(round(E["q1_tj_sel"], 1)), fmt(F["air"][1]), fmt(F["e_oc"][2]), fmt(F["d06_oblig"][0])),
        "prot_a": "the supply's own", "prot_b": "F1 (0997 blade, in a holder rated at least 20 A, E11-13); D10 (two-way, at the entry); U3/Q1 reverse block (CSD19532Q5B); D1 at DC_P; the selected entry's UVLO and OV (IF-05)",
        "settled": "d8dec31 (E-F1, E-F2), this record (part A: Q1, F1; out 12), %s, l4e5" % E11, "checks": [
            Chk("D10 does not conduct up to the selected OV maximum (25 C)", ovs[2], "<", sm40["vbr_min"], "V", "MAKER", "L4-E11 3c; Littelfuse SMCJ40A row"),
            Chk("D10 does not conduct up to the selected OV maximum at -20 C (the breakdown's typical coefficient, not a warranted bound)", ovs[2], "<", round(A["d10_cold_vbr"], 2), "V", "CONDITIONAL", "Littelfuse SMCJ sheet p.1, VBR at TJ, typical 0.1 %/K"),
            Chk("D10 does not conduct at REQ-015's 40 V at -20 C (the breakdown's typical coefficient)", 40.0, "<", round(A["d10_cold_vbr"], 2), "V", "CONDITIONAL", "Littelfuse SMCJ sheet p.1, VBR at TJ, typical 0.1 %/K"),
            Chk("D10 does not conduct on a reversed 36 V input (two-way part)", D["vrev"], "<", sm40["vbr_min"], "V", "MAKER", "Littelfuse SMCJ40CA row"),
            Chk("Q1 in reverse, DC_P back-fed from the drawn tracker ceiling (Q1 BSC039N06NS)", D["q1_rev_drawn"], "<=", F["bsc039_vds"], "V", "INFERRED", "l4e5 out 2, Q7's body diode; Infineon p.1", scope="drawn"),
            Chk("Q1 in reverse with L4-E5's raised ceiling, Q1 as drawn (BSC039N06NS)", D["q1_rev"], "<=", F["bsc039_vds"], "V", "INFERRED", "l4e5 ceiling; Infineon p.1", scope="drawn"),
            Chk("Q1 in reverse with the raised ceiling, Q1 the CSD19532Q5B (part A; register R-17)", D["q1_rev"], "<=", F["csd19532_vds"], "V", "INFERRED", "TI CSD19532Q5B p.1"),
            Chk("U3 (LM74700-Q1) cathode to anode in that reverse", D["q1_rev"], "<=", F["ld_ac_rec"], "V", "MAKER", "TI SNOSD17G 6.3, recommended; 75 V absolute"),
            Chk("Q1's junction at the selected breaker's highest current (%s A)" % fmt(F["e_oc"][2]), round(E["q1_tj_sel"], 1), "<=", A["tj_max"], "C", "INFERRED", "out 12 (Figure 8; RthetaJA on 1 in2 2 oz)"),
            Chk("F1's voltage rating (Littelfuse 297, the series the holder takes) against the highest steady input the drawn entry admits", F["ovlo"][2], "<=", F["f297_v"], "V", "MAKER", "Littelfuse 297 sheet; s120 OVLO", scope="drawn"),
            Chk("F1 (0997010.WXN) DC voltage rating against the %s V basis (over the selected OV maximum %s V)" % (fmt(F["e_basis_v"]), fmt(ovs[2])), F["e_basis_v"], "<=", A["f_v"], "V", "MAKER", "Littelfuse 0997 sheet (held back), DC rating; L4-E11 6"),
            Chk("F1's interrupting rating against the drawn cable's prospective current at -20 C from a stiff source", round(D["f1_ipf"], 1), "<=", A["f_int"], "A", "MAKER", "Littelfuse 0997 sheet; this record out 7", scope="drawn"),
            Chk("F1's interrupting rating against the specified worst stiff-source current (the loop's floor, %s mOhm at 20 C, at %s V)" % (fmt(F["loop_floor"]), fmt(F["e_basis_v"])), F["ipf_spec"], "<=", A["f_int"], "A", "CONDITIONAL", "L4-E11 6: the four-wire acceptance %s to %s mOhm on every assembly (E11-11, R-130)" % (fmt(F["loop_acc"][0]), fmt(F["loop_acc"][1]))),
            Chk("F1 at its derating table's next higher column above the inside air (%s C), against the selected breaker's highest" % fmt(A["f_col"]), F["e_oc"][2], "<=", A["f_allow"], "A", "INFERRED", "Littelfuse 0997 derating table, never interpolated; L4-E11 3c"),
            Chk("the selected breaker's highest inside F1 (10 A blade)", F["e_oc"][2], "<=", amps_in(F["e_f1"], "F1"), "A", "INFERRED", "L4-E11 3c; gen F1"),
            Chk("the entry's limit inside J_DCIN's nearest stated VH rating (AWG 18, shrouded header)", F["entry_lim"][1], "<=", F["vh_18"], "A", "ASSUMPTION", "JST VH catalogue p.1; the fitted header and gauge are not rated", scope="drawn"),
            Chk("the selected breaker's highest inside J_DCIN's selected class (an XT60-family board connector, %s A)" % fmt(F["jdcin_sel_a"]), F["e_oc"][2], "<=", F["jdcin_sel_a"], "A", "CONDITIONAL", "L4-E11 6 (Amass V1.2); the part named by E11-12 (R-131)"),
            Chk("the interconnect in F1's long-time band: every element at least %s A continuous where installed, against F1's %s A point (no maximum clearing time up to 13.5 A, 600 s to %s A)" % (fmt(F["d06_oblig"][0]), fmt(A["f_200"]), fmt(A["f_200"])), A["f_200"], "<=", F["d06_oblig"][0], "A", "CONDITIONAL", "L4-E11 6 (D-06 resolved in design): the makers' installed ratings filed (E11-10 to E11-14; R-129 to R-132, R-43)"),
            Chk("the interconnect's short-time capability above %s A (%s A for %s s, %s A for %s s, and F1's total clearing I2t at %s A and 58 V DC from 60 A to %s A)" % (fmt(F["d06_oblig"][0]), fmt(F["d06_oblig"][1]), fmt(F["d06_oblig"][2]), fmt(F["d06_oblig"][3]), fmt(F["d06_oblig"][4]), fmt(F["ipf_spec"]), fmt(F["ipf_spec"])), None, "<=", None, "the makers' short-time data and F1's clearing I2t", "CONDITIONAL", "L4-E11 6; E11-16 (R-113, R-115)"),
            Chk("the drawn interconnect in F1's long-time band (13.5 A with no time limit) against the D38999 size 16 contact's 13 A test current", 13.5, "<=", A["c16_a"], "A", "MAKER", "Amphenol D38999 contact table; L4-E11 6: NOT MET as drawn", scope="drawn"),
            Chk("the negative discharge at the ruled level (15 kV) with E-F1's 1 uF input capacitor: DC_F's rise against D10's breakdown", F["ef1_dv"][1], "<", sm40["vbr_min"], "V", "INFERRED", "DECISION-31 6.3 (d8dec31 apply_gen_sch_e_cin.py, register R-16)"),
            Chk("CS101 (M2) at REQ-015's 36 V: the input's peak under the drawn OVLO minimum", round(A["cs101_top"], 2), "<", F["ovlo"][0], "V", "INFERRED", "part A (L4-E7R's CS101 level)", scope="drawn"),
            Chk("CS101 (M2) at REQ-015's 36 V: the input's peak under the selected OV minimum (D-02)", round(A["cs101_top"], 2), "<", ovs[0], "V", "INFERRED", "part A; L4-E11 3c"),
            Chk("CS101 (M2) at REQ-015's 36 V: the input's peak under the alternative's OVLO minimum (R23 6.42k, 0.1 %; register R-94)", round(A["cs101_top"], 2), "<", round(F["ovlo_sel"][0], 2), "V", "INFERRED", "part A", scope="alternative"),
        ]})
    hs = F["e_hs_svc"]
    R.append({
        "id": "IF-05", "title": "DC_P through the selected entry U6/Q7 (TPS48110-Q1 breaker, CSD19536KTT, R19 4.5 mOhm) and the choke L2 (SRF1260-1R0Y) to VIN_RAW",
        "a": "DC_P", "b": "VIN_RAW (board E)",
        "v": "DC_P up to D1's clamping %s V at %s A; %s V before any current and %s V at %s A from a 9.00 V plug | U6 VS 3.5 to %s V (%s V absolute), its pins at most %s V at the clamp against %s V; Q7 %s V; the UVLO on at %s / %s / %s V, off at %s / %s / %s V of DC_P"
             % (fmt(sm40["vc"]), fmt(sm40["ipp"]), fmt(F["e_dcp_noload"]), fmt(F["e_svc"][2]), fmt(F["e_svc"][1]), fmt(F["e_vs"][0]), fmt(F["e_vs"][1]), fmt(F["e_pins"][1]), fmt(F["e_pins"][4]),
                fmt(F["e_q7_sel_v"]), *[fmt(x) for x in F["e_uv_on"]], *[fmt(x) for x in F["e_uv_off"]]),
        "i": "asked: in service at most %s A (a 9.00 V plug), up to %s A continuous under the breaker; the start %s to %s A for at most %s ms; a start into a resistive fault (worst at %s Ohm, %s ms); a start into a hard short (%s A after %s us); a hard short in service (%s A plus VIN x %s us / L) | available: the breaker %s / %s / %s A after %s / %s / %s ms, the short circuit %s / %s / %s A filtered %s to %s us then %s us, retry %s s; Q7's Figure 4-10 at %s V (100 us %s A, 1 ms %s A, 10 ms %s A) derated by %s, its IDM %s A derated %s A; L2 at %s A %s C against %s C"
             % (fmt(F["e_svc"][1]), fmt(F["e_oc"][2]), fmt(F["e_inrush"][0]), fmt(F["e_inrush"][1]), fmt(F["e_start_ms"]), fmt(F["e_rf"][1]), fmt(F["e_rf"][2]), fmt(F["e_hs_start"][2]), fmt(F["e_hs_start"][3]),
                fmt(F["e_sc"][2]), fmt(hs["t_us"]), *[fmt(x) for x in F["e_oc"]], *[fmt(x) for x in F["e_oc_ms"]], *[fmt(x) for x in F["e_sc"]], fmt(F["e_tau_us"][0]), fmt(F["e_tau_us"][2]), fmt(F["e_tsc_us"][1]),
                fmt(F["e_retry_s"]), *[fmt(x) for x in F["e_q7_chart"]], fmt(F["e_derate"]), fmt(hs["idm"]), fmt(hs["lim"]), fmt(F["e_l2"][0]), fmt(F["e_l2"][2]), fmt(F["e_l2"][3])),
        "loss": "DC_P to VIN_RAW %s mOhm hot, %s W at %s A; Q7 %s W at %s A (L4-E11)" % (fmt(F["e_loop_mohm"][1]), fmt(round(E["loss_vr"], 3)), fmt(F["e_svc"][1]), fmt(F["e_q7_w"]), fmt(F["e_l2"][0])),
        "therm": "L2 %s K over the %s C air at %s A; Q7's chart derating (%s) conservative while its case stays under %s C on its %s C rating (out 12)" % (fmt(F["e_l2"][1]), fmt(F["air"][1]), fmt(F["e_l2"][0]), fmt(F["e_derate"]), fmt(round(E["tc_break"], 2)), fmt(F["e_q7_tj"])),
        "prot_a": "D1 SMCJ40A at DC_P", "prot_b": "D2 SMCJ40A on VIN_RAW; the breaker (timed overcurrent, filtered short circuit, auto-retry), the UVLO and OV, the gate-slew start (L4-E11, apply_gen_sch_e_entry.py, E11-01)",
        "settled": "%s, this record (E11-19, out 12); the LM5069 drawn and as the alternative: gen_sch_e.py, l4e5, part A" % E11, "checks": [
            Chk("the UVLO's highest rise under DC_P before any current from a 9.00 V plug", F["e_uv_on"][2], "<", F["e_dcp_noload"], "V", "INFERRED", "L4-E11 3c, 3e"),
            Chk("the UVLO's highest fall under DC_P in service (%s A from a 9.00 V plug)" % fmt(F["e_svc"][1]), F["e_uv_off"][2], "<", F["e_svc"][2], "V", "INFERRED", "L4-E11 3e"),
            Chk("the in-service maximum from a 9.00 V plug under the breaker's lowest", F["e_svc"][1], "<", F["e_oc"][0], "A", "CONDITIONAL", "L4-E11 3e: the front end at least %s at 8.1 V, the pin's band and the transients measured (E11-06, R-85)" % "%s" % F["e_eta_floor"]),
            Chk("a start into a resistive fault (%s to %s Ohm) inside Q7's derated chart (the fraction of the chart used)" % (fmt(F["e_rf_range"][0]), fmt(F["e_rf_range"][1])), F["e_rf"][0], "<=", 1.0, "of the chart", "CONDITIONAL", "L4-E11 3c (every point held for the whole pulse); the derating's case and board E's copper (E11-14); E11-17"),
            Chk("the ordinary start inside Q7's derated chart", F["e_rf"][3], "<=", 1.0, "of the chart", "INFERRED", "L4-E11 3c"),
            Chk("a start into a hard short inside Q7's derated 100 us line", F["e_hs_start"][4], "<=", 1.0, "of the chart", "CONDITIONAL", "L4-E11 3c: TI's typical %s S taken as the bound (A11-10); E11-17" % fmt(F["e_hs_start"][1])),
            Chk("a hard short in service: the peak through Q7 inside its derated IDM (%s A), which needs the loop's inductance at least %s uH" % (fmt(hs["lim"]), fmt(hs["l_uh"])), None, "<=", None, "the loop's inductance", "CONDITIONAL", "OPEN evidence: L4-E11 3c, out 12 (E11-20, R-134)"),
            Chk("every start and fault pulse's I2t through F1 under its typical melting I2t (the largest, a hard short in service)", round(E["i2t_max"], 4), "<=", A["f_i2t"], "A2s", "INFERRED", "out 12 (rectangles); Littelfuse 0997 sheet"),
            Chk("U6's VS at D1's clamping voltage inside its operating range", sm40["vc"], "<=", F["e_vs"][0], "V", "MAKER", "TI SLUSEE5E (held back), through L4-E11 3b"),
            Chk("U6's input pins at D1's clamping voltage (INP the highest) inside their absolute rating", F["e_pins"][1], "<=", F["e_pins"][4], "V", "INFERRED", "L4-E11 3c"),
            Chk("Q7 (CSD19536KTT) at D1's clamping voltage", sm40["vc"], "<=", F["e_q7_sel_v"], "V", "NETLIST", "L4-E11 apply_gen_sch_e_entry.py, Q7's value text"),
            Chk("L2 (SRF1260-1R0Y) at the breaker's highest current under its temperature limit", F["e_l2"][2], "<=", F["e_l2"][3], "C", "INFERRED", "L4-E11 3e (Bourns' rows)"),
            Chk("the drawn LM5069 starting from a 9.00 V plug: its VIN before any current at least POREN's maximum", F["lm_vin_9"], ">=", F["lm_poren"], "V", "MAKER", "SNVS452G p.5; L4-E11 3a", scope="drawn"),
            Chk("the power limit's sense voltage at the OVLO maximum with the drawn R24 20k, against SNVS452G's 5 mV", round(A["vsns_drawn"] * 1e3, 4), ">=", A["vsns_min"] * 1e3, "mV", "MAKER", "SNVS452G 9.2.1.2.3, Equations 7 and 9", scope="drawn"),
            Chk("the LM5069's VIN at D1's clamping voltage", sm40["vc"], "<=", F["lm5069_vin_abs"], "V", "MAKER", "TI SNVS452G 7.1", scope="drawn"),
            Chk("Q7 (CSD19532Q5B) at D1's clamping voltage", sm40["vc"], "<=", F["e_q7_v"], "V", "MAKER", "TI CSD19532Q5B p.1", scope="drawn"),
            Chk("the entry's limit inside L2's Irms (SRF1260-1R5Y, its value text)", F["entry_lim"][1], "<=", 6.89, "A", "NETLIST", "gen_sch_e.py L2", scope="drawn"),
            Chk("the power limit's sense voltage at the OVLO maximum with R24 22k at its low corner", round(A["vsns_new_low"] * 1e3, 3), ">=", A["vsns_min"] * 1e3, "mV", "MAKER", "SNVS452G 9.2.1.2.3, Equations 7 and 9", scope="alternative"),
            Chk("the power-limit part (the limit at its corners times TI's 1.3) at the fault time's maximum with C5 and C121 (%s ms) inside Figure 10 derated to Q7's case" % fmt(F["alt_tflt"][1]), F["alt_pulse"], "<=", F["alt_soa"], "A", "CONDITIONAL", "L4-E11 7 (TI's power law past 10 ms)", scope="alternative"),
            Chk("the fault time's minimum with C5 and C121 against TI's half-again margin over the start into VIN_RAW at %s V" % fmt(round(F["ovlo_sel"][2], 2)), F["alt_tflt"][0], ">=", F["alt_need"], "ms", "INFERRED", "L4-E11 7 (34 uF, the front end held off by U34)", scope="alternative"),
            Chk("the breaker's event: its peak current and Q7's loaded turn-off (VCB's %s A is a threshold; tCB is measured with no GATE load)" % fmt(round(A["cb_thr"], 3)), None, "<=", None, "the source's and the gate's dynamics", "CONDITIONAL", "OPEN evidence, the alternative's bench rows (E11-17, R-118)", scope="alternative"),
        ]})
    R.append({
        "id": "IF-06", "title": "VIN_RAW over the dock (board E, E5, board A J_VR1 to J_VR4)",
        "a": "VIN_RAW (board E)", "b": "VIN_RAW (board A, U2's input)",
        "v": "solar: the corrected knee (HIZ certain below %s V, a flat %s A from %s V to %s V, L4-E11 E11-09; L4-E5's drawn-line figures %s / %s / %s V) to the ceiling %s V; vehicle 9 to %s V at the plug (VIN_RAW %s V at %s A from 9.00 V); at most %s V (the selected OV maximum; %s V the basis); under (B1) the dock's pin 1 carries VBAT (VSYS) to board E's VSYS_E, %s to %s V, %s A declared on one 813 contact (L4-E11 15a, E11-34) | U2 VIN %s V absolute"
             % (fmt(F["knee_hiz"]), fmt(F["knee"][0]), fmt(F["knee"][1]), fmt(F["knee"][2]), fmt(F["hiz_below"]), fmt(F["hiz_out_above"]), fmt(F["pin_reg_from"]), fmt(F["trk_ceiling"][2]), fmt(D["vrev"]), fmt(F["e_svc"][0]), fmt(F["e_svc"][1]),
                fmt(F["e_ov_off"][2]), fmt(round(F["ovlo_sel"][2], 2)), fmt(F["fx"]["vsys_rng"][0]), fmt(F["fx"]["vsys_rng"][1]), fmt(F["fx"]["aux_a"]), fmt(F["u2_vin_abs"])),
        "i": "in service at most %s A from a 9.00 V plug (L4-E11 3e; %s A at VIN_RAW 9 V under L4-E5's line); at the window %s A from the tracker; the front end's fault current at most %s A (R11 8 mOhm, R12 12 mOhm; %s A at 7 mOhm) | declared %s A; four Mill-Max pins at %s A each"
             % (fmt(F["e_svc"][1]), fmt(F["h3"][9.0][1]), fmt(round(D["trk_i_settle"], 2)), fmt(round(D["vin_fault"], 3)), fmt(round(D["vin_fault_7"], 3)), fmt(F["vin_raw_a"]["typ"]), fmt(F["millmax_a"])),
        "loss": "the dock's contacts and 12 AWG wires (IF-AE-DOCK)", "therm": "about 6 K rise of the pins at 14.10 A (IF-AE-DOCK, INFERRED)",
        "prot_a": "the entry (IF-04, IF-05); D2 on board E", "prot_b": "D2 SMCJ40A on board A; U34's restart guard",
        "settled": "l4e5, l4e6, IF-AE-DOCK, DECISION-31 (A-N1), L4-E11 (3e, 3f)", "checks": [
            Chk("the highest steady VIN_RAW (the %s V basis, over the selected OV maximum) inside U2's absolute rating" % fmt(round(F["ovlo_sel"][2], 2)), round(F["ovlo_sel"][2], 2), "<=", F["u2_vin_abs"], "V", "MAKER", "out 11, out 12; TI SNVSAI1D 6.1"),
            Chk("the in-service maximum from a 9.00 V plug inside the declared VIN_RAW current", F["e_svc"][1], "<=", F["vin_raw_a"]["typ"], "A", "INFERRED", "L4-E11 3e"),
            Chk("the front end's fault current at the onset of its average limit inside the declared VIN_RAW current", D["vin_fault"], "<=", F["vin_raw_a"]["typ"], "A", "INFERRED", "l4e6 out 5 (R11 band, 20.887 V, 0.93, %s V)" % fmt(F["avg_from"])),
            Chk("one Mill-Max pin with one of four open at that fault current", D["vin_fault"] / 3.0, "<=", F["millmax_a"], "A", "INFERRED", "Mill-Max p.28 (the 0850 to 0853 sibling figure)"),
            Chk("under (B1) the dock's pin 1, VBAT (VSYS) to board E's VSYS_E: its declared current on one 813 contact", F["fx"]["aux_a"], "<=", F["fx"]["c813"], "A", "INFERRED", "L4-E11 15a (E11-34, R-178)"),
            Chk("under (B1) the ground return on seven 813 contacts with one open at the 32.1 A coincidence, per contact", F["fx"]["gnd7"][0], "<=", F["fx"]["c813"], "A", "INFERRED", "L4-E11 15a: %s C at the 51 C air on w3de's ASSUMPTIONS" % fmt(F["fx"]["gnd7"][2])),
            Chk("the clamp D2 at its rated pulse against U2's 60 V (no surge level is ruled, D-16; at the ruled discharge the bus's capacitance holds it to 0.11 V)", sm40["vc"], "<=", F["u2_vin_abs"], "V", "MAKER", "DECISION-31 A-N1, S-111: a recorded residual outside the requirements", scope="drawn"),
        ]})
    r11_8 = F["r11_8"]
    R.append({
        "id": "IF-07", "title": "VIN_RAW through the front end U2 (LM5176), R11 and R12, to VBUS20",
        "a": "VIN_RAW (board A)", "b": "VBUS20",
        "v": "in %s V (the corrected knee's certain HIZ; %s V on L4-E5's drawn line) to %s V | out %s to %s V DC band, %s V bound (the typical-only OVP)" % (fmt(F["knee_hiz"]), fmt(F["hiz_below"]), fmt(round(F["ovlo_sel"][2], 2)), fmt(F["vbus_band"][0]), fmt(F["vbus_band"][1]), fmt(F["vbus_bound"])),
        "i": "asked in service %s A through R11 (U3 at %s A, %s A board current, plus 0.079 A) | R11 8 mOhm stacked minimum %s A at 62.1 C with C-1's taps; highest permitted %s A; R12 peak limit %s / %s / %s A"
             % (fmt(F["r11_need"]), fmt(F["iin_host"]), fmt(F["u3_max_board"]), fmt(F["r11_min_62_full"]), fmt(r11_8[2]), fmt(F["r12_peak"][0]), fmt(F["r12_peak"][1]), fmt(F["r12_peak"][2])),
        "loss": "front end %s DECLARED (C-8)" % fmt(F["eta_fe"]),
        "therm": "FETs at most %s C on the ASSUMED 50 C/W (C-3); L1 at most %s C (qualifying), its Isat there INCONCLUSIVE (C-5)" % (fmt(F["fet_tj"]), fmt(F["l1_qual"])),
        "prot_a": "U34 restart guard, R14 76.8k (E11-02): UV %s / %s / %s V falling (as drawn %s / %s / %s V); the clamp D2" % (*[fmt(x) for x in F["guard_sel"]], fmt(F["latch"][0]), fmt(F["latch"][1]), fmt(F["latch"][2])),
        "prot_b": "the average limit (R11), the cycle-by-cycle limit (R12), no hiccup; OVP on FB; no clamp on VBUS20 (S-111)",
        "settled": "l4e4, l4e5, l4e6, r11dep, s120", "checks": [
            Chk("R11's stacked minimum (8 mOhm, C-1's full taps, 62.1 C) above what U3 and the other loads ask", F["r11_need"], "<=", F["r11_min_62_full"], "A", "CONDITIONAL", "l4e4 out 2; U3's minimum rests on C-7"),
            Chk("the pin path's highest current (26.50 to 27.24 V on a stiff source) through R11 8 mOhm alone at 62.1 C", F["pin_path"], "<=", F["r11_min_62_alone"], "A", "INFERRED", "l4e5 out 7; l4e4 out 2"),
            Chk("the pin path with C-1's full tap allowance: holds only if bench V-A07 reads the pin's error at most %s A, else R11 7 mOhm (the bank and R12 serve both)" % fmt(F["pin_err_allow"]), None, "<=", None, "a measurement", "CONDITIONAL", "l4e5 out 7; l4e6 out 7; l4e8 check 3"),
            Chk("the in-service boost peak under the peak limit's minimum (R12 12 mOhm)", F["svc_peak"], "<", F["r12_peak"][0], "A", "INFERRED", "l4e6 out 5"),
            Chk("L1's peak bound at 90 % of its typical Isat at 25 C", F["l1_peak"], "<=", 0.9 * F["l1_isat"], "A", "MAKER", "l4e6 out 5; Coilcraft p.1"),
            Chk("L1's Isat at %s C at least %s A, so its peak bound stays at 90 %% of it (C-5: Coilcraft's derating or the L-versus-current sweep)" % (fmt(F["l1_qual"]), fmt(F["l1_need"])), None, "<=", None, "a maker figure or a measurement", "CONDITIONAL", "l4e6 out 5"),
            Chk("every FET's junction at the highest permitted current on the ASSUMED 50 C/W", F["fet_tj"], "<=", 150.0, "C", "CONDITIONAL", "l4e6 out 5: C-3"),
            Chk("U2's VIN at the highest steady input", round(F["ovlo_sel"][2], 2), "<=", F["u2_vin_abs"], "V", "MAKER", "TI SNVSAI1D 6.1"),
            Chk("the restart guard's highest fall, with L4-E5's 0.1 V, under the corrected knee's certain HIZ (R14 76.8k)", round(F["guard_sel"][2] + 0.1, 3), "<=", F["knee_hiz"], "V", "INFERRED", "L4-E11 3f (E11-02, E11-09; the knee drawn to its specification, R-03, R-128)"),
            Chk("the drawn restart guard's highest fall under VIN_RAW from a 9.00 V plug in service", F["guard_drawn"][2], "<", F["e_svc"][0], "V", "INFERRED", "L4-E11 3f", scope="drawn"),
        ]})
    R.append({
        "id": "IF-08", "title": "VBUS20's bulk bank (six EEHZK1V331P, each behind a 45 mOhm ballast; Cc2 3.3 nF)",
        "a": "the front end's output and U3's input pulses", "b": "the six cans",
        "v": "VBUS20 at most %s V | the cans' 35 V" % fmt(F["vbus_bound"]),
        "i": "every can at most %s A (R11 8 mOhm, 7.262 A); %s A at 7 mOhm | the rule's %s A; %s A at 7 mOhm" % (fmt(F["can8"][0]), fmt(F["can7"][0]), fmt(F["can8"][1]), fmt(F["can7"][1])),
        "loss": "the ballasts at most %s W at the bound's worst corner, %s W at L4-E8's nominal illustration: an operating-point term carried in the energy and thermal budgets (out 8), never added again once a measured efficiency includes it" % (fmt(F["ballast_w"]), fmt(F["ballast_nom_w"])),
        "therm": "the can's rise is a bench reading (lifetime CONDITIONAL); the cold ESR envelope INFERRED; the ballasts' heat at most %s K on the inside air at T-H1's floor, %s K at its binding line, inside L4-E12's figures (out 8)" % (fmt(round(F["ballast_w"] / F["th1"], 2)), fmt(round(F["ballast_w"] / F["gc"], 3))), "prot_a": "R12's peak limit and R11's average limit", "prot_b": "the ballasts",
        "settled": "l4e8 (accepted, check 3)", "checks": [
            Chk("every can at R11 8 mOhm (a conservative bound)", F["can8"][0], "<=", F["can8"][1], "A", "INFERRED", "l4e8 out 6"),
            Chk("every can at R11 7 mOhm (only if V-A07 fails; VIN and VBAT sampled)", F["can7"][0], "<=", F["can7"][1], "A", "CONDITIONAL", "l4e8 out 6; check 3"),
            Chk("the cans' voltage at the bus's bound", F["vbus_bound"], "<=", 35.0, "V", "INFERRED", "s120 out 8"),
            Chk("the cans' lifetime at their measured temperature rise (bench 7b.8 item 4); the cold ESR envelope at -20 C over life", None, "<=", None, "a measurement", "CONDITIONAL", "l4e8 out 6b; check 3"),
        ]})
    R.append({
        "id": "IF-09", "title": "VBUS20 through R16 and the charger U3 (BQ25731) to VBAT, the system node",
        "a": "VBUS20", "b": "VBAT (VSYS) and the pack's charge",
        "v": "VBUS20 %s to %s V, bound %s V | U3 VBUS and VSYS %s V absolute, VBUS %s V recommended; VBAT %s to %s V as drawn%s; SYSOVP %s / %s / %s V"
             % (fmt(F["vbus_band"][0]), fmt(F["vbus_band"][1]), fmt(F["vbus_bound"]), fmt(F["u3_abs"]), fmt(F["u3_rec_vbus"]), fmt(D["vbat_low"]), fmt(F["chg_v_max"]), b1v(F), fmt(F["sysovp"][0]), fmt(F["sysovp"][1]), fmt(F["sysovp"][2])),
        "i": "IIN_HOST %s A, minimum %s A, maximum %s A board current; the window needs %s A at %s V | delivered at VBAT %s to %s W; ChargeCurrent at most %s A"
             % (fmt(F["iin_host"]), fmt(F["u3_min"]), fmt(F["u3_max_board"]), fmt(F["win_need"]), fmt(F["bus_low"]), fmt(round(D["vbat_avail_min"], 1)), fmt(round(D["vbat_avail_max"], 1)), fmt(F["chg_set"])),
        "loss": "U3 %s (INFERRED)" % fmt(F["eta_u3"]), "therm": "the charger's own; inside air %s C" % fmt(F["air"][1]),
        "prot_a": "the H3 line on ILIM_HIZ (hardware), IIN_HOST, VINDPM about 18.5 V, ACOV", "prot_b": "BATOVP %s V, SYSOVP; the pack's OCC %s A" % (fmt(F["batovp"]), fmt(F["occ"])),
        "settled": "l4e4, l4e5, s120, FW-A02, L4-E11 (U-04, 3g and 3h)", "checks": [
            Chk("U3's minimum covers the window at the lowest bus (C-7: the 0.1 A is INFERRED)", F["win_need"], "<=", F["u3_min"], "A", "CONDITIONAL", "l4e4 out 1"),
            Chk("U3's VBUS at the bus's bound", F["vbus_bound"], "<=", F["u3_abs"], "V", "INFERRED", "s120 out 9; TI SLUSE66A p.8"),
            Chk("ACOV not reached at the bus's bound", F["vbus_bound"], "<", F["acov_min"], "V", "INFERRED", "s120 out 9"),
            Chk("ChargeCurrent inside REQ-075's 3.06 A", F["chg_set"], "<=", 3.06, "A", "NETLIST", "FW-A02"),
            Chk("ChargeCurrent inside the pack's OCC", F["chg_set"], "<", F["occ"], "A", "NETLIST", "pcb_pack_protection.yaml"),
            Chk("the charge per cell inside the cell maker's maximum charge current", F["chg_set"] / 3.0 * 1000.0, "<=", F["cell_chg_ma"], "mA", "MAKER", "Samsung 35E 3.7"),
            Chk("with no usable pack at a 9.00 V plug, the shed warm-up (P2 at its plan figure) under the least the source delivers at VBAT", F["e_p2"][1], "<=", F["e_src_least"], "W", "CONDITIONAL", "L4-E11 3g, 3h: arrangement (A), rules R-a to R-d; P1 at most %s W, E11-05, E11-06, E11-09, E11-22, E11-23; unresolved choice U-04" % fmt(F["e_p1_max"])),
        ]})
    R.append({
        "id": "IF-10", "title": "VBAT and the pack (board A F1 and R17, the dock's pack pins, board E F3, the XT60 lead, board P's chain)",
        "a": "VBAT (the kit's loads and U3)", "b": "the 4S3P pack (D-06) and board P",
        "v": "%s V (the gauge's CUV %s V a cell) to %s V as drawn%s; BATOVP %s V | D1 SMCJ18A standoff %s V, breakdown %s V minimum; the pack FETs 30 V; under (B1) the battery FET pair Q39 and Q40 (BUK6Y10-30P) 30 V"
             % (fmt(D["vbat_low"]), fmt(F["cuv"]), fmt(F["chg_v_max"]), b1v(F), fmt(F["batovp"]), fmt(sm18["vr"]), fmt(sm18["vbr_min"])),
        "i": "declared %s A continuous, %s A peak; PS-IDLE-SPEC %s / %s / %s / %s A at 16.8 / 14.4 / 12.0 / 10.0 V; the PA keyed at 113 W %s A at 10.0 V; PS-ALLTX's 18 A at a %s V stack (D-11); charge %s A | OCD1 %s A for %s s, SCD %s A; the pins %s / %s A; XT60 %s A"
             % (fmt(F["pp_cont"]), fmt(F["pp_peak"]), *[fmt(x) for x in F["idle_i"]], fmt(F["pa113"][4]), fmt(F["alltx_18a_stack"]), fmt(F["chg_set"]), fmt(F["ocd1"][0]), fmt(F["ocd1"][1]), fmt(F["scd"]),
                fmt(F["pack_pin_share"][0]), fmt(F["pack_pin_share"][1]), fmt(F["xt60_a"])),
        "loss": "R17, F1, the pins, F3, the lead, the pack's FETs and F2 (POWER-THERMAL 7.3's 22.5 mOhm)", "therm": "the cells' windows 0 to 45 C charge, -10 to 60 C discharge (REQ-046); FEA-008 not closed (L4-E10: approach (II) recommended, CONDITIONAL)",
        "prot_a": "D1 SMCJ18A on VBAT; A F1 25 A", "prot_b": "BQ4050 (COV %s V, CUV %s V, OCC, OCD1, SCD, temperatures); BQ7720700; F1 25 A; F2 SCF9550 30 A" % (fmt(F["cov"]), fmt(F["cuv"])),
        "settled": "pcb_pack_protection.yaml, POWER-THERMAL 7, FEA-004 (PWR-F12), L4-E10 (FEA-008, final at 79b2f568), L4-E11 (R-b)", "checks": [
            Chk("D1's standoff above VBAT's regulated maximum", F["chg_v_max"], "<=", sm18["vr"], "V", "MAKER", "Littelfuse SMCJ18A row; s120 out 7"),
            Chk("D1 not conducting at the SYSOVP maximum", F["sysovp"][2], "<=", sm18["vbr_min"], "V", "MAKER", "TI SLUSE66A p.14; Littelfuse"),
            Chk("the PA keyed alone at 113 W from the %s V rest floor, at a 10.0 V stack, inside the declared peak" % fmt(F["pa_floor"]), F["pa113"][4], "<=", F["pp_peak"], "A", "MODELED", "pwr_budget.out; FW-A05"),
            Chk("PS-ALLTX held under the 18 A peak through a 60 s key-down: the rest voltage it needs at the worst cell resistance under D-11's floor", F["alltx_rest_need"], "<=", F["d11_floor"], "V", "MODELED", "pwr_budget.out D-11 line; FW-A05's floor (PROVISIONAL thresholds)"),
            Chk("OCD1 (%s A for %s s) reached only below a %s V stack, under the 18 A point's %s V" % (fmt(F["ocd1"][0]), fmt(F["ocd1"][1]), fmt(F["alltx_20a_stack"]), fmt(F["alltx_18a_stack"])), F["alltx_20a_stack"], "<", F["alltx_18a_stack"], "V", "MODELED", "pwr_budget.out D-11 line"),
            Chk("the chain's short-time rating at 18 A for 60 s with F2 near +60 C (PWR-F12)", None, "<=", None, "a rating", "CONDITIONAL", "FEA-004: re-declaration and Eaton's answer or the bench owed"),
            Chk("the peak per pack pin with one of four open", F["pack_pin_share"][1], "<=", F["millmax_a"], "A", "MAKER", "IF-AE-DOCK; Mill-Max p.28"),
            Chk("the peak inside the XT60's rating", F["pp_peak"], "<=", F["xt60_a"], "A", "MAKER", "Amass XT60 sheet"),
            Chk("board P's charge FET Q2's body diode under rule R-b's case (i) (a dead pack's charge through it)", F["rb_q2_tj"], "<=", 150.0, "C", "CONDITIONAL", "L4-E11 2: R-b's case (i) and board P's copper (E11-22, R-136)"),
            Chk("the cells' temperature design against REQ-046 with the pack fitted (FEA-008, DR-06): L4-E10 recommends a wide-temperature 18650 in D-06's 4S3P, CONDITIONAL on its signed specification and the owner's approval (D-06 to about %s Wh nominal)" % fmt(F["cell_nom"][1]),
                None, "<=", None, "a design and the owner's two items", "CONDITIONAL", "L4-E10 out 5 (closing check 573c8b8f): FEA-008 not closed; LO-01a CONDITIONAL on T-H1 at least %s W/K, LO-01d to g OPEN; unresolved choice U-01" % fmt(F["th1"])),
        ]})
    R.append({
        "id": "IF-11", "title": "VBAT to the load converters (slot rails, device rail, logic, monitor, heater; board E's always-on on CELL_F as drawn, on VSYS_E under (B1))",
        "a": "VBAT", "b": "the 39 loads of PS-IDLE-SPEC and the PS-ALLTX set",
        "v": "%s to %s V as drawn%s | the converters assumed to run to %s V (SHORTLIST.md 2, not shown); under (B1) to %s V in supplement at OCD1's current (not shown; E11-31's step rows)"
             % (fmt(D["vbat_low"]), fmt(F["chg_v_max"]), b1v(F), fmt(D["vbat_low"]), fmt(F["fx"]["supp"][0])),
        "i": "asked: PS-IDLE-SPEC %s / %s / %s W; PS-ALLTX %s / %s / %s W (low / plan / high at the pack terminals); %s W of PS-IDLE-SPEC has no document | available: each converter's own rating (pwr_budget.py)"
             % (fmt(F["idle"][0]), fmt(F["idle"][1]), fmt(F["idle"][2]), fmt(F["alltx"][0]), fmt(F["alltx"][1]), fmt(F["alltx"][2]), fmt(F["undoc_w"])),
        "loss": "the converters' makers' floors (pwr_budget.py)",
        "therm": "the heat per state, POWER-THERMAL 9; each required mode's governing LOCAL limit sets its line (L4-E12 12a, U-02): at M7's maker-stated +70 C line %s W/K (lid open, fans) E3-O's mixed air %.2f C (%s W with the ballasts) and E5's %.2f C under the hold (%s W), screens at the mixed air (the parts' local air, the cooler's exhaust, is the line); at LO-01a's floor with no hold %.2f C and %.2f C (the design as it stands)"
             % (fmt(F["gc"]), F["e3o_line"], fmt(round(F["e3o_wb"], 3)), F["e5_line"], fmt(round(F["e5_hold_wb"], 3)), F["floor_air"][0], F["floor_air"][1]),
        "prot_a": "the eFuses (monitor %s A peak declared, heater) and the stages' limits" % fmt(F["vmon"]["peak"]), "prot_b": "each converter's own",
        "settled": "pwr_budget.out, load_trace.out, POWER-THERMAL, L4-E12 at a86be47b (accepted, check db41c95d)", "checks": [
            Chk("the profile's %s W with no document measured or bounded by a maker" % fmt(F["undoc_w"]), None, "<=", None, "a measurement", "ASSUMPTION", "load_trace.out; replay out 13"),
            Chk("E5's mixed inside air under the hold at M7's maker-stated line (%s W/K lid open with the fans) under the +%s C parts, a screen at the mixed air (their local air, the cooler's exhaust included, is the line: T-H2)" % (fmt(F["gc"]), fmt(F["parts_hot"])),
                F["e5_line"], "<=", F["parts_hot"], "C", "CONDITIONAL", "L4-E12 out 4c, 4d (MODELED): T-H1 at or over the line, the hold's reference within +-%s K, the fans' rating, the parts out of the exhaust; unresolved choice U-02" % "%s" % F["hold_ref"]),
            Chk("E3-O's mixed inside air with every radio on at that line under the +%s C parts (a screen)" % fmt(F["parts_hot"]), F["e3o_line"], "<=", F["parts_hot"], "C", "CONDITIONAL", "L4-E12 out 4d (MODELED; E3-O alone needs %s W/K); unresolved choice U-02" % fmt(F["g_e3o"])),
            Chk("the required modes' governing local limits (L4-E12 12a, 12e): T-H1's points decide every class (i) and (ii) line; four class (iii) lines (E3-L lid closed as ruled; E3-O and E5 on the e-paper's operating row read to cover it unpowered) no reading can pass", None, "<=", None, "a thermal decision", "CONDITIONAL", "L4-E12 out 12a, 12e; unresolved choice U-02; the owner's options OW-10"),
            Chk("the inside air at LO-01a's floor (%s W/K) with no hold, E5's +60 C dwell, under the +%s C parts" % (fmt(F["th1"]), fmt(F["parts_hot"])),
                F["floor_air"][1], "<=", F["parts_hot"], "C", "MODELED", "L4-E12 out 2c (L4-E10's corner plus the ballasts, MESHSAT-1478 as found)", scope="drawn"),
            Chk("every load converter runs to the 3.00 V line (10.0 V stack)", None, "<=", None, "a record", "ASSUMPTION", "SHORTLIST.md 2: no record"),
            Chk("TPS2596 eFuses (U21, U22) on VBAT at the SYSOVP maximum", F["sysovp"][2], "<=", F["tps2596_abs"], "V", "MAKER", "TI TPS2596 7.1"),
        ]})
    pd = F["pd"]
    R.append({
        "id": "IF-12", "title": "VBAT to the USB-C outlet (U19 LM5176, Q27, R138, J_USBC_OUT; U18 TPS25740A), the tablet's optional charge",
        "a": "VBAT", "b": "the outlet's sink (a tablet), 5, 9 and 15 V at 3 A",
        "v": "VBAT %s to %s V into U19 as drawn%s | 5 / 9 / %s V contracts, each held inside the maker's window (L4-E4 bench (a))" % (fmt(D["vbat_low"]), fmt(F["chg_v_max"]), b1v(F), fmt(pd["volts"])),
        "i": "asked: %s A each PDO; with PS-TYP %s W plan (%s W at the outlet), %s A at 14.4 V | available: R138 5 mOhm trip %s to %s A; U19's own limit %s to %s A; the Bulgin receptacle %s A; Q27 %s A; J_USBC_OUT no rating held"
             % (fmt(F["pdo_a"]), fmt(F["typ_usbc"][0]), fmt(F["typ_usbc"][2]), fmt(F["typ_usbc"][4]), fmt(F["trip"][0]), fmt(F["trip"][1]), fmt(F["u19_lim"][0]), fmt(F["u19_lim"][2]), fmt(F["recept_a"]), fmt(F["q27_a"])),
        "loss": "U19 0.93 DECLARED", "therm": "inside air %s C" % fmt(F["air"][1]),
        "prot_a": "OUTLET_OK interlock (off while the PA keys, CON-019); C2's shed at 9.0 A", "prot_b": "U18's OCP over R138 (15 us); fast and slow OVP",
        "settled": "l4e4 (R138, bench a and b)", "checks": [
            Chk("every PDO below the trip window's minimum (the 3 A row; bench (a) decides the row)", F["pdo_a"], "<", F["trip"][0], "A", "CONDITIONAL", "l4e4 out 3: VI(TRIP)'s label"),
            Chk("the trip maximum inside the receptacle", F["trip"][1], "<=", F["recept_a"], "A", "MAKER", "l4e4 out 3; Bulgin"),
            Chk("the trip maximum inside Q27", F["trip"][1], "<=", F["q27_a"], "A", "MAKER", "TI SLPS632"),
            Chk("J_USBC_OUT's VBUS pin with a maker's rating at or above the trip maximum (a 2.54 mm pin, no part number)", None, "<=", None, "a rating", "ASSUMPTION", "l4e4: INCONCLUSIVE; register R-30 (Layer 6)"),
            Chk("PS-TYP with the outlet inside the declared continuous pack current at 14.4 V", F["typ_usbc"][4], "<=", F["pp_cont"], "A", "MODELED", "pwr_budget.out"),
        ]})
    poe = F["poe"]
    R.append({
        "id": "IF-13", "title": "VBAT through R227 to the PoE stage (U16 LM5176 boost, R71, +54V_POE, J_54V to board B) and its monitor U17",
        "a": "VBAT", "b": "+54V_POE at %s A peak (REQ-017)" % fmt(poe["peak"]),
        "v": "VBAT %s to %s V regulated as drawn%s, %s V at the pack-open bound, %s V at D1's rated pulse, into R227 and U16 (POE_VIN at most %s V under VBAT in the boost current-limit case) | %s V; U17 (INA226) IN+ on VBAT, IN- and VBUS on POE_VIN (part A; as drawn on POE_OUT and +54V_POE, pins %s and %s); INA226 %s V absolute, %s V common mode"
             % (fmt(D["vbat_low"]), fmt(F["chg_v_max"]), b1v(F), fmt(round(D["pack_open"]["v_end"], 3)), fmt(F["SMCJ18A"]["vc"]), fmt(round(A["u17_mv_fault"] * 1e-3, 3)), fmt(poe["volts"]),
                "/".join(F["u17_nets"]["POE_OUT"]) or "none", "/".join(F["u17_nets"]["+54V_POE"]) or "none", fmt(F["ina_abs"]), fmt(F["ina_cm_op"])),
        "i": "asked: %s / %s A at 54 V, the stage's input at a %s V stack %s A (%s mV over R227), at its fault bound %s A (%s mV); PS-TYP plus PoE %s W plan (%s W outside) | available: R227 5 mOhm %s W (%s W at %s C); the INA226's %s mV full scale (%s A); U16's limits"
             % (fmt(poe["typ"]), fmt(poe["peak"]), fmt(D["vbat_low"]), fmt(round(D["poe_in"], 3)), fmt(round(A["u17_mv_norm"], 2)), fmt(round(A["u17_fault_a"], 2)), fmt(round(A["u17_mv_fault"], 2)),
                fmt(F["typ_poe"][0]), fmt(F["typ_poe"][2]), fmt(A["hojlr"][0]), fmt(round(A["hojlr_avail"], 2)), fmt(F["air"][1]), fmt(F["ina_fs_mv"]), fmt(round(A["u17_fs_a"], 3))),
        "loss": "U16 %s (the generator's figure outside the maker's plots); R227 at most %s W at the stage's peak input" % (fmt(poe["efficiency"]), fmt(round(D["poe_in"] ** 2 * 0.005 * 1.01, 4))),
        "therm": "inside air %s C" % fmt(F["air"][1]),
        "prot_a": "OUTLET_OK interlock", "prot_b": "U16's average limit (R71) and cycle limit (R72); board B's TPS23861 port limit",
        "settled": "HW-FW-CONTRACT HF-F02 (S-60), this record (part A, apply_gen_sch_a_u17.py)", "checks": [
            Chk("U17's inputs at the rail (HF-F02)", poe["volts"], "<=", F["ina_abs"], "V", "MAKER", "TI SBOS547 5.1", scope="drawn"),
            Chk("U17's common mode on VBAT at its highest bound (the pack-open bound, above SYSOVP's maximum)", round(max(F["sysovp"][2], D["pack_open"]["v_end"]), 3), "<=", F["ina_cm_op"], "V", "MAKER", "TI SBOS547 CMRR condition and bus range"),
            Chk("U17's common mode at D1's rated pulse on VBAT", F["SMCJ18A"]["vc"], "<=", F["ina_cm_op"], "V", "MAKER", "Littelfuse SMCJ18A row; TI SBOS547"),
            Chk("R227's drop at the stage's peak input at the lowest stack inside the full scale", round(A["u17_mv_norm"], 2), "<=", F["ina_fs_mv"], "mV", "INFERRED", "the declared 0.6 A at 54 V over 0.88; R227 at +1 %"),
            Chk("R227's drop at the stage's fault bound (U16's boost peak limit over R72) inside the full scale", round(A["u17_mv_fault"], 2), "<=", F["ina_fs_mv"], "mV", "INFERRED", "part A; SNVSAI1D VCS(BOOST)"),
            Chk("R227's dissipation at that bound inside its derated rating", round(A["u17_p_fault"], 3), "<=", round(A["hojlr_avail"], 2), "W", "MAKER", "HoJLR2512 p.2 (through L4-E8)"),
            Chk("POE_VIN (U17's IN- and VBUS) at a hard connect of VBAT, ringing at its undamped bound, inside the pins' 40 V", round(A["tr"][0][4], 2), "<=", F["ina_abs"], "V", "INFERRED", "part A, B3 (20.2 uF behind R227)"),
            Chk("the differential across R227 at that step inside the INA226's +-40 V", round(A["tr"][0][3], 3), "<=", A["ina_diff_abs"], "V", "MAKER", "SBOS547C 6.1 note 2; part A, B3"),
            Chk("R227's RMS dissipation in steady buck operation (a PoE fault) inside its rating", round(A["buck_p"], 3), "<=", round(A["hojlr_avail"], 2), "W", "INFERRED", "part A, B3 (VCS(BUCK), fSW(1), L10 at -20 %)"),
            Chk("R227's pulse energy at a hard connect (%s mJ nominal, %s mJ with the printed rows stacked; the maximum unresolved) inside the maker's pulse rating" % (fmt(round(A["tr"][0][5], 3)), fmt(round(A["tr"][0][5] * A["c_hi_f"], 3))), None, "<=", None, "a pulse rating and a capacitance envelope", "CONDITIONAL", "Milliohm prints none; R-101, R-117"),
            Chk("the hard output short's self-consistent peak with L10's L(I) at temperature, R227's pulse and RMS stress and U17's pins there", None, "<=", None, "the inductor's L(I)", "CONDITIONAL", "part A, B3: %s A at a constant %s uH against Isat %s A; the L10 assignment R-120 and R-121" % (fmt(round(A["short_peak"], 2)), fmt(round(A["l10_min"] * 1e6, 1)), fmt(A["l10_isat"]))),
        ]})
    pa = F["pa"]
    R.append({
        "id": "IF-14", "title": "VBAT to the PA rail (+13V8_PA, J_PA) with the PA keyed",
        "a": "VBAT", "b": "the RA30H1317M1 PA, %s V" % fmt(pa["volts"]),
        "v": "VBAT %s to %s V into U13 as drawn%s | %s V; PA_EN gated by EMCON and TX_INHIBIT_n" % (fmt(D["vbat_low"]), fmt(F["chg_v_max"]), b1v(F), fmt(pa["volts"])),
        "i": "asked: the drain 5.4 to 8.2 A, not characterised (F-PR-02); PS-IDLE-SPEC plus the PA at 113 W %s W, %s A at 10.0 V | available: declared %s / %s A, the stage's average loop 7.2 to 9.5 A"
             % (fmt(F["pa113"][0]), fmt(F["pa113"][4]), fmt(pa["typ"]), fmt(pa["peak"])),
        "loss": "U13 %s" % fmt(pa["efficiency"]), "therm": "key-down at most 60 s, flange gates +75 C and +85 C (D-11, PROVISIONAL)",
        "prot_a": "the K rules (FW-A05), the outlets dropped by OUTLET_OK", "prot_b": "the stage's limit",
        "settled": "POWER-THERMAL 7.2, FEA-004", "checks": [
            Chk("the PA keyed alone at 113 W within the pack's declared peak at the 10.0 V stack", F["pa113"][4], "<=", F["pp_peak"], "A", "MODELED", "pwr_budget.out"),
            Chk("the PA's drain current against the rail's declared peak (F-PR-02, not characterised)", 8.2, "<=", 9.5, "A", "ASSUMPTION", "POWER-THERMAL 7.3: the stage's loop band"),
        ]})
    return R


# ------------------------------------------------------------------------------------------------------- the gate
GATE = [
    {"n": 1, "criterion": "one architecture selected, its mandatory functions with a defensible feasibility basis",
     "rows": ["IF-02", "IF-04", "IF-05", "IF-07", "IF-09", "IF-10", "IF-11", "IF-12", "IF-13"], "choices": ["U-01", "U-02", "U-04"], "verdict": "CONDITIONAL",
     "constraint": "the solar function's 100 W bound is CONDITIONAL on G_CM and U18's VIN+ bias (L4-E7R) and its panel on PANEL-ACC (U-03, a CONDITIONAL "
                   "DOWNSTREAM UNIT SELECTION since L4-E13: no unit bought or measured, R-35); REQ-015 at "
                   "9.00 V at the plug is a CONDITIONAL CANDIDATE on E11-05, E11-06, E11-09, E11-22 and E11-23 (U-04; L4-E11's consolidation, "
                   "check 5 at 5aa18a69, selects (B1), the BQ25730 with the battery FET pair Q39 and Q40 and board E on VSYS_E after its "
                   "fix round, drafted: once applied U-04 is a downstream qualification test, on the board as drawn TI's D1 and D3 decide "
                   "it); thermal feasibility per required mode is U-02's (L4-E12's fix round: each mode's governing local limit, T-H1 "
                   "deciding every class (i) and (ii) line, four class (iii) lines (E3-L lid closed as ruled, E3-O and E5 on the e-paper's "
                   "row) the owner's, OW-10); the battery path's thermal design is FEA-008's (U-01; the Saft supported for the temperature "
                   "windows, not yet adoptable: current at temperature and the storage dwell AWAITING, L4-E10 10g); PS-ALLTX's chain at "
                   "18 A for 60 s (PWR-F12) is an open obligation",
     "overturn": "possibly, on named evidence only: U-01 on Saft's answer or the sample qualification and on the HL18650V's signed "
                 "specification (D-06's pack energy, protection settings and charge ranges), U-02 on its four class (iii) lines (the "
                 "rulings against E3-L lid closed, E3-O and E5: the owner's) and on a class (i) or (ii) point read short with the route "
                 "also short, U-04 on the board as drawn on TI's D1 or D3 (none once (B1) is applied); the rest, the panel unit included, "
                 "resolves by a value, a part or a measurement on the same topology"},
    {"n": 2, "criterion": "material power-path defects have engineering resolutions and bounded supporting calculations",
     "rows": ["IF-01", "IF-02", "IF-04", "IF-05", "IF-06", "IF-09", "IF-10", "IF-13"], "choices": [], "verdict": "CONDITIONAL",
     "constraint": "no material defect is open: the review's B1 and B2 on (B1)'s draft, D-13 (board E's auxiliary domain on the pack's side of "
                   "the battery FET) and D-14 (the FET bounded at an unprinted corner, a fallback lowering 18 A for 60 s), are addressed "
                   "in drafts by L4-E11's fix round (board E on VSYS_E, R-177 and R-178; the pair Q39 and Q40, R-157), CONDITIONAL on the "
                   "installed path (E11-29), the docking split (E11-30) and the bench rows (E11-31); the known defects at the solar entry, D-10 (a stiff 36 V source on the port) and D-11 (a reversed "
                   "panel), single faults, are addressed in drafts, a selected remedy each (L4-E7, check 5 at 573fd5b8: the over-voltage cut-off U21 "
                   "with Q12 and the return switch Q13, R-173, drafted, not applied), D-10 CONDITIONAL on the panel lead's loop inductance at least 2.47 uH "
                   "with the guard already on (the review's B6, L4-E7 at 11339ec7: four parts added, every rating MEETS from it; R-176, R-180), D-11 "
                   "CONDITIONAL on Q13's leakage above +25 C; the band between "
                   "25 V and the cut-off, where a stiff source still runs the stage, is a residual for layer 8 (R-175); D-12 (CS116 and CS115 on the drawn entry) is resolved in the drafted entry, CS115 CONDITIONAL on the cable's loop "
                   "current (L4-E7's derivation, set 27); D-01 to D-05 and D-08 are resolved in design (drafted or bounded), D-06 is resolved in design by "
                   "L4-E11's interconnect with its evidence items (E11-10 to E11-16), D-07 and D-09 are superseded by the replacement of the LM5069 "
                   "(E11-19 finds no new one); the resolutions rest on CONDITIONAL rows (the loop's typical rows, the makers' installed and "
                   "short-time ratings, R227's pulse rating, the start into a hard short's transconductance bound) and the hot short in service "
                   "on open evidence (the loop's inductance, E11-20); the dependency rounds add no defect: L4-E11's D9 and D10 are the "
                   "entry's delay and transconductance rows already CONDITIONAL here, and E11-24 is U-04's fallback, a register row (R-152), "
                   "not a defect's resolution",
     "overturn": "no: each resolves by a part, a rating or a measurement at the vehicle or the solar entry or on (B1)'s draft; D-10 and D-11 by "
                 "the drafted guard, which adds protection at the solar entry and changes no topology; D-13 and D-14 by a feed and a part "
                 "inside (B1)"},
    {"n": 3, "criterion": "remaining assumptions explicit, with their impact and verification method",
     "rows": [], "choices": [], "verdict": "PASS", "constraint": "", "overturn": ""},
    {"n": 4, "criterion": "downstream implementation changes, layout constraints and tests have named owners and acceptance criteria",
     "rows": [], "choices": [], "verdict": "PASS", "constraint": "", "overturn": ""},
    {"n": 5, "criterion": "no unresolved uncertainty could overturn the selected architecture while described as routine later testing",
     "rows": ["IF-09", "IF-10", "IF-11"], "choices": ["U-01", "U-02", "U-04"], "verdict": "CONDITIONAL",
     "constraint": "three unresolved choices could overturn it and are named as such, not as later testing, each with its question, evidence, "
                   "supplier and fallback stated by its dependency round: U-01 (FEA-008's cell: the signed specification and the owner's two "
                   "items; L4-E10, check 4 at e464ff88; its fix round: the Saft supported for the temperature windows, not yet adoptable), U-02 "
                   "(MESHSAT-1478: each required mode against its governing local limit, L4-E12's fix round at b1cd32ba; T-H1's points of "
                   "12d decide every class (i) and (ii) line, as ruled the heat stage at +40 C against the SGP41's Table 4, 2.905 W/K on the "
                   "pack and 3.081 W/K on shore, under CFL-002's C the cells' hot stop, 1.804 and 1.767 W/K; four class (iii) lines no "
                   "reading can pass, the owner's), U-04 ((B1) selected and drafted with the pair and board E on VSYS_E, a downstream "
                   "qualification test once applied; on the board as drawn TI's D1 and D3; L4-E11, check 5 at 5aa18a69, fix round at "
                   "656fc540); an "
                   "owner and an acceptance criterion do not close them. U-03 "
                   "left this category with L4-E13's acceptance: a CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC, R-35) that decides which "
                   "unit, not the topology or the source class",
     "overturn": "yes, on named evidence only: U-01 (D-06's pack energy and settings), U-02 (its four class (iii) lines, and any line read short "
                 "with the route also short: CFL-002, REQ-042's coverage, D-02b, the sealed case's thermal design or the device set, the "
                 "owner's), U-04 (on the board as drawn only, TI's D1 or D3: the charger's power path); U-03 no "
                 "longer can, unless route 2 proves infeasible with route 1 still closed (L4E13-06)"},
]

ARCH = "ARCHITECTURE-LEVEL CHOICE"                              # could overturn the architecture: named by criteria 1 and 5
DOWNSTREAM = "CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC)"  # U-03 since L4-E13: decides a unit, in the register as R-35
# The unresolved choices that could overturn the architecture (category b), and U-03, which left it with L4-E13's acceptance. An owner and an acceptance criterion close an
# assignment, never one of these: each stays open, and keeps every criterion that names it from PASS, until its evidence lands.
CHOICES = [
    {"id": "U-01", "title": "FEA-008: the battery path's cell and thermal design (L4-E10; the Saft MP 176065 xtd a supported route for the temperature windows on published evidence, not yet adoptable, a PROPOSAL)", "class": ARCH,
     "question": "which cell does D-06's pocket carry? The ruled 35E is UNSUITABLE on its own published evidence for LO-01d (E3-O: the cells at "
                 "61.26 to 72.42 C over its +60 C), LO-01e (E5's dwell: the idle pack at 74.73 C), LO-01f (+71 C storage) and LO-01g (-33 C "
                 "storage); the Saft MP 176065 xtd as 4S1P is supported on its published datasheet for the TEMPERATURE WINDOWS of every "
                 "cell-limit row (charge -30 to +85 C, discharge -40 to +85 C, storage allowable -40 to +85 C), not for current and "
                 "temperature together: its 11 A continuous and 22 A pulses 'Can vary depending on temperatures' (its footnote 2), so the "
                 "kit's 10 A continuous, 18 A for 60 s and the gauge's 20 A for 2 s at the modelled cells (-20 to +80 C) AWAIT Saft or the "
                 "limited sample qualification (L4-E10 10g), as do the storage dwell and recovery, and the fit awaits the mock-up; the "
                 "owner's approval is required; the HL18650V needs its signed specification to confirm the "
                 "rows L4-E10 holds only on its product page (MAKER-PAGE): the idle hot limit (+80 C, the 30-day storage row), storage at -33 C, "
                 "each storage row's state of charge and recovery, charge below 0 C, the charge current from +10 C (at least 0.357C), continuous "
                 "discharge (at least 6.0 A a cell for PS-ALLTX), the end voltages and the minimum capacity",
     "constraint": "LO-01d to LO-01g (E3-O, E5, E3-S, E4-S with the pack fitted) have no route that holds on held evidence with the ruled cell; LO-01a "
                   "holds only with T-H1 at least 1.666 W/K in both lid states (1.8058 W/K with L4-E8's ballasts counted, L4-E12). L4-E10's "
                   "dependency round (check 4 at e464ff88) states the HL18650V's limits by mode and drafts the charge for the 4S3P, never applied: "
                   "0.84 A to 16.40 V from T1 -9 C, 1.68 A to 16.80 V from T2 1 C, the drawn 3.00 A to 16.80 V from T5 11 C to T3 42 C, UTC -9.0 "
                   "C, the kit's hold below -7 C; usable energy 90.2 Wh (2.11 h) against the 35E's 107.9 Wh (2.52 h) at +25 C, 16.4 % less; at the "
                   "cold end only brackets (45.1 to 69.6 Wh with the cells at -5.52 C, 37.2 to 54.1 Wh from a cold start at -20 C, ASSUMPTION). "
                   "L4-E10's consolidation (check 5 at 1c321773): a supported route on published manufacturer evidence, the Saft MP 176065 xtd "
                   "(3.65 V, 5.6 Ah; charge -30 to +85 C, discharge -40 to +85 C at 11 A continuous and 22 A pulses with no duration, storage "
                   "allowable -40 to +85 C) as 4S1P: 81.6 Wh nominal, 53.5 to 55.1 Wh usable, 1.25 to 1.29 h battery-only, about NZ$ 954.88 for "
                   "four cells; its fix round for the review's B5 (L4-E10 at ee09aa09): the temperature windows SUPPORTED on published evidence; "
                   "NOT YET ADOPTABLE: current and temperature together and the storage dwell and recovery AWAIT Saft (the request expanded "
                   "to seven questions) or the limited sample qualification (10g), the fit the mock-up (at most 1.40 mm of wrap), LO-01a's "
                   "complete pass and LO-01e T-H1; approach (III)'s E5 route REJECTED (the pocket's room as designed 0.0865 L)",
     "evidence": ("Saft's published datasheet (Doc. 31109-2-0625, held) for the temperature windows of every cell-limit row of the MP 176065 "
                  "xtd; Saft's statement on the currents at the cells' temperatures, the storage dwell and recovery, the minimum capacity "
                  "and the thickness (the drafted request, expanded after the review's B5); Yichun Topwell Power's signed product specification answering the drafted request's ten "
                  "questions for the HL18650V; Eaton's statement on F2 above +60 C and in storage (R-103)",
                  "a printed mock-up of four Saft cells at the sheet's maximum dimensions in the pocket at the built stack (hours, no purchase; "
                  "R-167); in Saft's place the limited sample qualification (L4-E10 10g: one cell of the lot, a chamber from -40 to +85 C, a "
                  "25 A load, about two weeks; NZ$ 238.72 a cell; 10 A continuous, 18 A for 60 s and 20 A for 2 s at -20 to +80 C, the "
                  "storage soaks and cycles; R-168); the lot's minimum capacity at receipt (R-169); T-H1 in both lid states (R-104, R-151); for the HL18650V a lot soak (about ten "
                  "cells, USD 35.00, 4 and 12 days); with the cell chosen, L4-E10's margins re-run (1.06 K under H1 and 0.97 K under U2's "
                  "INFERRED trip at LO-01e) and each LO row's TEST-PLAN run with the pack fitted (R-47, R-109)",
                  "approve D-06's cell, energy and spend once the evidence supports it, which it does not yet: the Saft as 4S1P (about 145 to "
                  "about 82 Wh nominal, NZ$ 954.88; OW-3), or the HL18650V once its specification or a soak confirms; send the requests "
                  "and authorise the qualification (OW-2, OW-9); if declined, LO-01d to g stay a release gate"),
     "supplier": "Saft and Yichun Topwell Power, through the owner; Layer 7 (the mock-up); the prototype bench (the limited sample "
                 "qualification, T-H1, the LO rows); Layer 6 files the answers (R-103, R-168); the session re-runs L4-E10's margins (R-47); the owner approves the cell",
     "fallback": "the HL18650V, the higher-energy alternative (90.2 Wh usable), on its signed specification or a lot soak; with no answer and no "
                 "approval, U-01 stays a release gate and every row CONDITIONAL (no ruling needed). With a narrower signed HL18650V figure, at "
                 "L4-E10's thresholds: an idle limit under 78.94 C makes H1 act in E5's dwell, under 74.73 C E5's cells pass it, under 73.07 C "
                 "E3-O loses its 'no shutdown', under 71.00 C E3-S fails, under 68.86 C E3-O's cells pass it; E3-O and E5 then fall back to "
                 "(I)'s cooler (8.18 to 35.21 W into the sealed case, INCONCLUSIVE) and E3-S to requirement change A (the owner's); storage "
                 "warmer than -33 C to (III)'s primary-fed heater (470 to 940 Wh of added storage, an owner's ruling under D-06) or requirement "
                 "change A; continuous discharge under 6.0 A a cell back to (I); the charge current, the end voltage and the capacity (3.22 Wh "
                 "per 100 mAh a cell) move energy, not the architecture; or the 35E kept with (I), or a requirement change (the owner's, D-29)",
     "overturns": "D-06's pack energy, not the power path's topology: with the Saft 53.5 to 55.1 Wh usable against the 35E's 107.9 Wh, with the "
                  "HL18650V 16.4 % less (90.2 against 107.9 Wh at +25 C), each with its protection settings and charge ranges; with a narrower "
                  "idle limit and no requirement change, (I)'s powered cooling (up to 35.21 W into the sealed case) would reopen U-02's heat "
                  "budget, and a narrower storage floor would add 470 to 940 Wh of primary storage under D-06",
     "rows": ["IF-10"]},
    {"id": "U-02", "title": "MESHSAT-1478: the sealed case's heat rejection in each required mode against its governing local limit, and four class (iii) lines (L4-E12, the fix round)", "class": ARCH,
     "question": "what conductance does the sealed Peli 1450 with its 3 mm plate give, lid open and lid closed with the fans, in each required "
                 "mode of L4-E12 12a against that mode's governing local limit? As ruled (CFL-002 open: REQ-042's VOC channel sensing across "
                 "the envelope) the SGP41's Table 4 +50 C governs the heat stage at REQ-024's +40 C: 2.554 W/K on the pack (M1 lid open, M3 "
                 "lid closed; a reading of at least 2.905 W/K) and 2.709 W/K on shore (M2, M4; at least 3.081 W/K); under CFL-002's C, A or "
                 "B the cells' hot stop H1 governs: 1.666 W/K on the pack (at least 1.804 W/K), 1.642 W/K on shore (at least 1.767 W/K); M5, "
                 "REQ-014's profile at +20 C, C1's air trigger, 1.447 W/K (at least 1.508 W/K); M6, E3-O at +55 C, the e-paper's +60 C "
                 "operating row read to cover it unpowered (INFERRED), 5.417 W/K (at least 7.758 W/K), the maker-stated alternative the "
                 "RB9704's +70 C, 1.806 W/K (at least 1.958 W/K); M7, E5's +60 C dwell, the e-paper with no conductance, the alternative the "
                 "LimeSDR's +70 C storage row, 2.159 W/K (at least 2.455 W/K); M8 and M9, charging on the design day, T4 on the charging "
                 "cells, 2.025 and 2.525 W/K (at least 2.123 and 2.677 W/K). A dummy-load mixed-air point closes only the conductance it reads",
     "constraint": "L4-E12's fix round for the review's B3, B4 and B7 (12a to 12e at b1cd32ba): the SGP41's sensing is supported to +50 C "
                   "only (Table 4); its +55 C (Table 5) is an absolute rating, a screen, never a line; option C reports the VOC channel not "
                   "covered above a 49.0 C reading and switches the sensor off at 54.0 C, so section 11's K1 and K5 are screens, withdrawn as "
                   "lines; each local limit is categorised (the cells at the air plus their own I2R, the control thresholds that end or shed "
                   "a mode, the parts at their LOCAL air with the cooler's exhaust, the junctions, the unpowered parts' storage rows), absolute "
                   "ratings listed as screens. The outside capacity with the inside resistance at zero (12e; 1.810 W/K at K1's rise, "
                   "correcting 1.504 to 1.571 W/K, which were a bound with a 50 m/s inside flow): every line is class (i) or (ii), T-H1 "
                   "deciding bare or with the route, except four class (iii) lines, over the capacity even with the route at the optimistic "
                   "ends: M3 (E3-L lid closed on the pack, as ruled) short by 0.275 W/K, 2.749 W; M4 (on shore) short by 0.430 W/K, 4.300 W; "
                   "M6 (E3-O, the e-paper) short by 0.955 W/K, 4.775 W; M7 (E5's dwell, the e-paper) the whole 21.587 W. The charging heat as "
                   "a balance (B4): 95.944 W in less 45.900 W stored = 50.044 W, 52.134 W with L4-E8's ballasts; T3's start (K7, K8) needs "
                   "1.8102 and 2.1997 W/K (readings 1.8892 and 2.3150 W/K). The battery-only run coupled to C1 (B7): C1 sheds the profile at "
                   "2.01 to 2.51 h on the bound, the run with the shed states 2.52 to 2.95 h (energy and thermal); 2.52 h unshed is energy "
                   "only. The fans counted in the energy budget (pwr_budget.py's rows, tier R; D-18)",
     "evidence": ("Sensirion's statement of the SGP41's short-term storage duration (its survival unpowered above the 54.0 C reading, a "
                  "screen; drafted); PDi's storage statement for the E2370KS0C1 (drafted, clarification/pervasive-displays-e2370ks0c1.txt), "
                  "which moves M6 and M7 to the +70 C class; D-18's picked fans: their power, operating range (REQ-043) and, under (B1), "
                  "their supply to 17.375 V (R-142, R-150, E11-35)",
                  "T-H1's points (12d; R-104, R-151; T-H1-PROCEDURE-DRAFT.md as revised), each at its mode's heat with the heaters set to it "
                  "less the fans' measured draw: M2 and M6 at 27.086 W lid open, M1 at 25.536 W lid open, M4 and M3 lid closed, M7 at "
                  "21.587 W, M5 at 43.413 W, M8 and M9 at 52.134 W, each read against its governing line as ruled and under C; then the "
                  "fans-off case and 12c's transient point; under a class (ii) line the combined route (R-170 to R-172) read at the same "
                  "point; the e-paper's own temperature at its window (a T-H1 channel: a plate fraction of 0.362 needs 1.963 W/K, 0.725 "
                  "needs 3.926 W/K); the cells' rise in the pocket (U-01), the parts' local air in the built kit (T-H2), the junctions "
                  "(THM-001); on the built kit the battery-only run from a 24 h soak at +20 C (12c)",
                  "CFL-002 (OW-1); for the four class (iii) lines, one option each (OW-10): E3-L lid closed, CFL-002's C, A or B, a "
                  "closed-lid ceiling on REQ-042's VOC channel (an ambient of +31.3 to +38.8 C on the pack, +30.2 to +38.2 C on shore) or "
                  "D-02b's closed-lid test restated; E3-O and E5, PDi's statement sent (OW-4), a different e-paper (CHO-001) or a recorded "
                  "deviation (TEST-PLAN); authorise T-H1's bench (OW-8)"),
     "supplier": "the prototype bench, as Layer 9's physical verification, once the owner authorises it (the session cannot run it); Layer 6 "
                 "components for D-18's pick and the fans' rating (R-142, R-150, E11-35); Layer 7 mechanical for the combined route "
                 "(R-170 to R-172) and a closed-lid conduction path; the makers (Sensirion, PDi), through the owner",
     "fallback": "under a class (i) or (ii) line's point, the combined route inside the rulings (R-170 to R-172, passive: no power, no "
                 "endurance change) read at the same point; for a class (iii) line no measurement passes it: the session develops two "
                 "options, the e-paper's window temperature measured (the plate fraction decides) and a closed-lid conduction path from "
                 "the plate to the lid's inner face inside the seal (Layer 7; not modelled, it closes nothing yet); the rest are the "
                 "owner's (CFL-002, a requirement or ruling change, CHO-001, a recorded deviation). Charging is not class (iii): charging "
                 "only in the heat stage (31.133 W into the case) needs 1.209 and 1.508 W/K, class (i), at the cost of the profile while "
                 "charging (an owner's duty-cycle choice, not taken)",
     "overturns": "the sealed case's thermal design against four mode requirements (class (iii)): the rulings (no vent, the Peli 1450, the "
                  "device set) and E3-L lid closed, E3-O and E5 as stated cannot all stand; which gives way is the owner's (CFL-002, "
                  "REQ-042's coverage, D-02b, CHO-001, TEST-PLAN), never the power path's topology; a class (i) or (ii) line read short "
                  "with the route also short would join them",
     "rows": ["IF-11"]},
    {"id": "U-03", "title": "O-1: the solar panel inside REQ-016's window (L4-E13, accepted)", "class": DOWNSTREAM,
     "question": "which physical unit is inside REQ-016's window: a unit measured to PANEL-ACC and accepted on A-1 (Vm20 plus U_V at most "
                 "25.000 V at -20 C and 1000 W/m2), A-2 (at least 1.365591 W) and A-3(b); not whether the window can be met, which L4-E13 "
                 "shows on a unit equal to the typical rows",
     "constraint": "L4-E13 (accepted, checks 3 and 4 at fae419d1 and 33b6b7be): route 1, a maker's warranted band, closes nothing today; route 2, one identified "
                   "SunPower SPR-E-Flex-100 measured against A-1 to A-3, is feasible on a unit equal to the typical rows: A-1 Vm20 + U_V 24.1505 V "
                   "against 25.000 V at -20 C and 1000 W/m2 (margin 0.8495 V), the window Voc25 20.315 to 22.156 V; A-2 27.0849 W above "
                   "1.365591 W; A-3 (a) 3.987 A, the conservative bound over L4-E7R's regulation (2.5485 A nominal, at most 2.9337 A at 25 V) "
                   "and backstop (trip at most 3.7408 A), (b) 8.1817 A, (c) 13.82 A, a COMPONENT_LIMITATION on J_SOLAR and PV_IN; A-4 on "
                   "L4-E7R's two layers (the regulation's 25 V corner 73.3436 W; the backstop's static bound 93.5521 W, CONDITIONAL on G_CM and "
                   "the VIN+ bias); no physical unit accepted",
     "evidence": ("route 1, a maker's warranted Voc band inside the window (the drafts to SunPower and Solbian, OW-4); it closes nothing today",
                  "one unit bought, recorded by serial number and measured (M1 to M3 and A-2's reading at the specification) and accepted on A-1, "
                  "A-2 and A-3(b) (R-35); its trace rerun (R-52); J_SOLAR and PV_IN with a rating that covers A-3(c) (R-148); M3's n at or under "
                  "2 for the disturbance check (R-149); L4-E7R's regulation and backstop applied (drafted) for A-3(a) and A-4",
                  "the purchase and the measurement of one unit (OW-6) and sending the two route-1 drafts (OW-4): actions, not questions"),
     "supplier": "the owner (the purchase, the two drafts sent); the measurement to the specification under his authority; Layer 6 components "
                 "(PANEL-ACC's acceptance R-35, J_SOLAR and PV_IN R-148, M3's n R-149); the makers, if they answer",
     "fallback": "another unit of the same curve shape inside the window; route 1 if a maker warrants a band; REQ-016's window restated (the "
                 "owner's; not needed)",
     "overturns": "nothing of the architecture: it decides which unit, not the topology and not the source class; REQ-016's window, the stage, "
                  "its hold and its 100 W control stay; it returns to an architecture-level choice only if route 2 proves infeasible with "
                  "route 1 still closed (L4E13-06)",
     "rows": ["IF-01"]},
    {"id": "U-04", "title": "source-only and dead-pack operation (L4-E11: (B1) selected, the BQ25730 with the battery FET pair Q39 and Q40 and board E on VSYS_E, drafted; the drawn board is arrangement (A))", "class": ARCH,
     "question": "with (B1) selected and drafted, does the BQ25730's VSYS hold the kit's load steps inside the 2.054 V margin (D2), does each "
                 "FET of the pair meet its bar (junction to air at most 34.42 C/W at the +70 C mixed air, E11-29), does the docking pulse "
                 "split between the two body diodes within a share of 0.848 (E11-30), does the start from cold reach VSYS_MIN (E11-31), "
                 "and is the BQ25730 obtainable? On the board as drawn (arrangement (A)) D1 and D3 stay TI's",
     "constraint": "L4-E11's consolidation (check 5 at 5aa18a69) and its fix round for the review's B1 and B2 (section 15 at 656fc540): "
                   "(B1), TI's BQ25730 with two Nexperia BUK6Y10-30P in parallel as the battery FET (Q39, Q40; LCSC C3278350), drafted in "
                   "apply_gen_sch_a_charger.py, and board E's auxiliary domain (U12, its controller, the two mixer fans) moved from CELL_F "
                   "to VSYS_E over the dock's pin 1 (J_DOCK.1 to VBAT; apply_gen_sch_e_aux.py, apply_pcb_interfaces_dock.py; E11-33, E11-34), "
                   "none applied. SLUSE65A bounds VSYS: no pack, at least 12.054 V (LDO mode); the charge inhibited, piecewise: SRN under "
                   "12.054 V at least 12.054 V, over 12.546 V VSRN + 150 mV within +-2 % (12.546 V an assumed reading of TI's malformed "
                   "column, A11-18), between at least 11.96 V; with the source overloaded VSYS follows the pack through the pair and R17 "
                   "down to 9.688 V: the system node 9.688 to 17.375 V. In the held state no kit load is fed from the pack: its bounded "
                   "drains total 0.1408 mA, the bench reads the held pack current at most 1 mA (E11-31). The start is bounded on held "
                   "evidence to VSYS_MIN or a latch within 3.062 s (the earlier 502.3 ms withdrawn: 0.5 A is an input ceiling, not a "
                   "delivered current). The pair at the +70 C mixed air: every protection event at TJ 150 C or under at the 34.42 C/W bar "
                   "(E11-29), 18 A for 60 s kept, at 119.8 C (R-159's fallback, which lowered it, withdrawn); the docking pulse 242.9 A "
                   "against each FET's ISM 320 A at 25 C, met hot for a share of at most 0.848 (E11-30); the precharge at most 0.33616 A, "
                   "no charge under 5.7 V on SRN; 0.0934 W in the pair at PS-IDLE-SPEC (0.218 % of the pack's output); L2 at 14.55 A peak "
                   "against Isat 25.4 A; 98 of the 107 row blocks identical, so L4-E4 to L4-E8 carry over; still open: D2 against the "
                   "2.054 V margin, D6, D8, D9, D10, the BQ25730's supply (LCSC stock 0), the fans' rating to 17.375 V (E11-35), and "
                   "REQ-015 at 9.00 V at the plug, a CONDITIONAL CANDIDATE (P1 at most 20.51 W, the shed warm-up 28.12 W carried with 0.98 "
                   "W in hand; the source's least 29.09 W at VBAT does not sustain the 42.8 W profile without the pack or shedding; at the "
                   "load's hi corner P1 (35.24 W) exceeds the source's least); on the board as drawn the BQ25731 leaves D1 and D3 "
                   "(Q-TI-3) to TI",
     "evidence": ("TI's SLUSE65A (held) bounds the three modes; Q-TI-15 (D2) and Q-TI-16 (VSYS_MIN's maximum) to TI, drafted in "
                  "clarification/TI-QUESTIONS.md (Q-AOS-1 withdrawn: Nexperia prints the pair's ISM); the BQ25730's supply from an "
                  "authorised source (R-162); the fans' maximum supply voltage (E11-35)",
                  "the three modes, the held pack current, the start from cold and D2 on one BQ25730 build (E11-31, R-161), every step's "
                  "minimum over the converters' floor; each FET's installed path at most 34.42 C/W from the layout, read as its case rise "
                  "at 10 A (E11-29, R-159); the docking pulse's split on the pair (E11-30, R-160); R-85 extended at the plug (E11-06) and "
                  "E4-O's warm-up (E11-23, R-137)",
                  "send TI's questions (OW-7); the BQ25730 and the pair bought for the build (money, the owner's)"),
     "supplier": "Layer 8 board A applies R-157 and board E E11-33 under L4-E11's release record (R-147); the Layer 4 coordinator applies "
                 "E11-34's interface draft; the prototype bench (R-161); Layer 9 (R-159); Layer 6 (R-160, R-162, E11-35); TI through the "
                 "owner",
     "fallback": "inside (B1): R-c's step rule for D2; the pair's copper and Nexperia's Rth(j-mb) for the bar, never a lowered protection "
                 "or service (18 A for 60 s and 10 A continuous kept); the two diode paths matched by layout, or Nexperia's hot ISM, for "
                 "the docking pulse; if (B1) fails on these or on supply, arrangement (A) with its dependency round stands: E11-24's "
                 "hold-up (54.07 mJ, 1.117 ms for the worst admitted step, R-152) for D2 and D5, with TI's D1 and D3 deciding",
     "overturns": "once R-157, E11-33 and E11-34 are applied, nothing of the architecture: each open claim has a test or an analysis that "
                  "bounds it and a fallback inside (B1), so U-04 becomes a downstream qualification test (L4-E11 check 5); on the board as "
                  "drawn a negative D1 or D3 from TI changes the charger's power path, which (B1) already is; the efficiency, the pin's "
                  "band or P1's load move the knee or F1, not the topology",
     "rows": ["IF-06", "IF-09", "IF-10"]},
]
EVIDENCE_LABELS = ("vendor", "physical", "owner")


def evidence_text(c):
    """A choice's evidence in one line, by its three sources (the page's cell and the output's line)."""
    return "; ".join("(%s) %s" % (lab, x) for lab, x in zip(EVIDENCE_LABELS, c["evidence"]))


# The material power-path defects (criterion 2), with their state after the update round.
DEFECTS = [
    {"id": "D-01", "title": "the solar backstop trips under TEST-PLAN M2 (CS101)", "state": "RESOLVED (drafted)",
     "constraint": "CS101's injected current crossed the sense bank and its peaks over the trip less the operating current stopped the stage for "
                   "td each time, so solar charging stopped for the test, against M2's 'no upset' line (L4-E7R's check 3)",
     "options": "the bulk moved ahead of the sense bank, five 100 nF C0G across R66 (3.960 to 4.496 ms), R66 8.45k and RIMON_IN 31.6k: the "
                "filtered ripple at most 0.0585 A against the 0.1130 A margin, the response allowance 1.087 ms after the filter's 0.4205 J; "
                "CONDITIONAL on the loop's typical rows (break-even 2.51 times), the bulk's temperature, the bank's pulse capability, the 0.1 s window",
     "resolution": "L4-E7R accepted (check 4, fnd/l4e7 91e9a4b5, figures at 675b8068); register R-21 and R-98, apply_gen_sch_e_backstop.py; M2, R-122",
     "rows": ["IF-01", "IF-02"]},
    {"id": "D-02", "title": "the vehicle entry's over-voltage lockout opens under TEST-PLAN M2 (CS101) at REQ-015's 36 V", "state": "RESOLVED (drafted)",
     "constraint": "36 V plus CS101's 2.83 V peak reaches 38.83 V, past the drawn OVLO minimum 37.78 V",
     "options": "the selected entry's OV (TPS48110-Q1, R22 332k over R23 10.0k at 0.1 %): off above 39.6 / 40.36 / 41.22 V, 0.77 V over the peak "
                "and 3.18 V under D10's breakdown minimum (L4-E11, selected); for the LM5069 alternative R22 100k and R23 6.42k at 0.1 %: 39.71 / "
                "41.44 / 43.18 V; M2 at the source's nominal (not taken)",
     "resolution": "apply_gen_sch_e_entry.py (E11-01, R-123) after apply_gen_sch_e_hotswap.py (R-94)", "rows": ["IF-04"]},
    {"id": "D-03", "title": "Q1 over its rating on a reversed input with the raised ceiling", "state": "RESOLVED (drafted)",
     "constraint": "66.15 V across the drawn 60 V BSC039N06NS", "options": "the CSD19532Q5B (100 V)",
     "resolution": "register R-17, apply_gen_sch_e_q1.py", "rows": ["IF-04"]},
    {"id": "D-04", "title": "F1 cannot interrupt at the entry's highest steady input", "state": "RESOLVED (drafted)",
     "constraint": "the drawn 32 V DC MINI against 43.18 V", "options": "the Littelfuse 0997010.WXN (58 V DC, 1000 A at 58 V DC), in a holder "
                                                                         "rated at least 20 A (E11-13)",
     "resolution": "register R-18 and R-132, apply_gen_sch_e_f1.py", "rows": ["IF-04"]},
    {"id": "D-05", "title": "U17 on the 54 V rail (HF-F02)", "state": "RESOLVED (drafted)",
     "constraint": "54 V on the INA226's IN+ and IN- against its 40 V absolute", "options": "U17 on R227, 5 mOhm in the PoE stage's input",
     "resolution": "register R-06, apply_gen_sch_a_u17.py", "rows": ["IF-13"]},
    {"id": "D-06", "title": "the vehicle entry's interconnect in F1's long-time band from a weak source", "state": "RESOLVED (in design)",
     "constraint": "a source under 30 A (ECSS 6.17.3c's three times) can leave 10 to 11 A flowing indefinitely, 13.5 A for up to 600 s and 20 A for "
                   "up to 5 s through J_DCIN's VH contact (10 A), the D38999 size 16 contacts (13 A test current) and the kit's cable and lead, "
                   "whose held sheets print no current or time-current rating",
     "options": "L4-E11's option (i), selected: every element at least 20 A continuous where installed, 35 A for 5 s, 60 A for 0.5 s and F1's total "
                "clearing I2t at 900 A; size 12 contacts (insert 17-6), J_DCIN an XT60-class connector, a holder rated at least 20 A, AWG 14 cores, "
                "the loop specified by its resistance (at least 56.93 mOhm at 20 C, accepted four-wire at 58.51 to 64.21 mOhm) so a stiff source "
                "stays at 900 A against F1's 1000 A; (ii) a smaller fuse rejected (it fails 9 V); (iii) the source's capability in REQ-015 not needed",
     "resolution": "L4-E11 (accepted, check a15ab384), CONDITIONAL on its evidence items E11-10 to E11-16 (R-129 to R-132, R-43, R-95, R-113, R-115)",
     "rows": ["IF-04"]},
    {"id": "D-07", "title": "the hot swap's power limit under the sense voltage TI recommends", "state": "SUPERSEDED (the LM5069 alternative only)",
     "constraint": "R24 20k gives 4.7429 mV at 43.18 V, under SNVS452G's 5 mV, and the hot-short pulse was compared at 36 V with a by-eye reading",
     "options": "the selected entry limits no power (E11-19, out 12): its starts sit inside Q7's derated chart (0.704 into a resistive fault, 0.743 "
                "into a hard short); for the alternative R24 22k 1 %: 5.06 mV at its low corner",
     "resolution": "superseded by E11-01's entry (R-123); R-94's R24 stands only if the LM5069 is kept", "rows": ["IF-05"]},
    {"id": "D-08", "title": "R227's transients bypass U16's current control", "state": "RESOLVED (bounded, conditions named)",
     "constraint": "the capacitors behind R227 (20.2 uF) charge outside U16's cycle limit, so 72.38 mV did not bound every transient",
     "options": "bounded in part A: the differential at most the VBAT step, POE_VIN under 40 V in every required event, a saturated sample "
                "distinguished from damage; R227's pulse energy 2.879 mJ nominal, the maximum unresolved until a capacitance envelope and the "
                "pulse's shape meet Milliohm's rating; moving the capacitors ahead of R227 not taken (they close U16's input loop)",
     "resolution": "IF-13's checks; R-101 (Milliohm's pulse rating), R-117 (the loop's inductance), R-120 and R-121 (L10)", "rows": ["IF-13"]},
    {"id": "D-09", "title": "the hot swap's fault time against the start into VIN_RAW", "state": "SUPERSEDED (the LM5069 alternative only)",
     "constraint": "with C5 (100 nF, K, X7R) at its printed rows stacked the fault time's minimum is 2.035 ms, under TI's half-again margin over "
                   "the start into VIN_RAW at 43.18 V (3.814 ms; the start alone 2.542 ms at the corners, 1.324 ms nominal), the front end's own "
                   "load during the start not included",
     "options": "the replacement has no fault timer against a power limit (its start 0.382 to 1.219 A for at most 2.5 ms); with the LM5069 kept, "
                "L4-E11's C5 GRM3195C1H104GA05 with C121 GRM3195C1H683JA05 (apply_gen_sch_e_timer.py): 4.927 to 14.653 ms against 4.593 ms on a "
                "recomputed 3.062 ms start (34 uF)",
     "resolution": "superseded by E11-01's entry (R-123); R-119 only if the LM5069 is kept", "rows": ["IF-05"]},
    {"id": "D-10", "title": "a stiff 36 V source on the solar port (a single fault: a vehicle or shore lead in the panel's receptacle)",
     "state": "ADDRESSED IN DRAFTS (a selected remedy, drafted, not applied), CONDITIONAL on the panel lead's loop inductance at least 2.47 uH",
     "constraint": "without the guard D4, the drafted SMCJ28A, conducts 2.67 to 16.63 A and takes 95.9 to 585.8 W against its 1.17 W on the board at the hot end's air; "
                   "the largest sustained source the drafted entry holds is 29.70 V (L4-E7's D4)",
     "options": "L4-E7's three, each on its held sheet: the TPS48110-Q1 alone on back-to-back FETs (its -1 V input pins on a reversal: not taken); the "
                "LM74700-Q1 ahead of the TPS48110-Q1 (76.21 V across CATHODE to ANODE under CS116 against 75 V: not taken); SELECTED, U21 TPS48110-Q1 "
                "with Q12 CSD19532Q5B as an over-voltage cut-off, rising at 28.55 to 31.06 V and falling at 27.07 V or more, with D4 the SMCJ30A: the "
                "block never turns on and Q12 holds 36 of 100 V (the TVS-only change, SMCJ36A with the 63 V class, evaluated and not taken); with the "
                "guard already on (the review's B6, L4-E7 at 11339ec7) the network as first drafted failed four ratings when a 36 V source steps on "
                "(PV_F 102.1 V of 100, its slew 397.7 V/us of 60, INP 29.07 V of 20, U5 0.4218 V of 0.3), so C131 and C132 become two 10 uF 100 V, "
                "C133 and C134 two 10 uF 50 V on PV_P, C126 330 pF and R97 30.0k: every rating MEETS from a lead of 2.47 uH (U5's 0.2991 of 0.3 V "
                "binding; Q12 off at most 75.3 A within 10.1 us, D4 carrying nothing)",
     "resolution": "R-173: apply_gen_sch_e_solar_guard.py (7 edits, release-guarded), drafted, not applied (L4-E7, check 5 at 573fd5b8, B6 at "
                   "11339ec7); owed: the SMCJ30A's LCSC code, U21's DGX-19 land, the regeneration, R-176's seven bench rows, the panel lead's loop "
                   "inductance at least 2.47 uH measured or its conductors' centres at least 4.21 mm apart (R-180, Layer 7); the band 25 V to the "
                   "cut-off a layer 8 row (R-175)",
     "rows": ["IF-01"]},
    {"id": "D-11", "title": "a reversed panel (DECISION-31's E-N1, a single fault)",
     "state": "ADDRESSED IN DRAFTS (a selected remedy, drafted, not applied), CONDITIONAL on Q13's leakage above +25 C",
     "constraint": "without the guard D4 carries the panel's 6.802 A forward, held, and holds inside its 1.17 W on the board only below a 0.172 V "
                   "drop, which no silicon junction has at that current (INFERRED); the keyed receptacle was the only barrier (L4-E7's D5)",
     "options": "SELECTED, Q13 CSD19532Q5B in the panel's return (J_SOLAR.2 becomes PV_RTN), its gate from R101 and R102 with a D12 BZT52C12 clamp: "
                "it blocks a reversal with its 100 V rating and no controller; the high side's pins stay within 1 V of GND while Q13 leaks under "
                "32.0 uA, its sheet printing 1 uA at 25 C only (DECISION-31's E-N1 closed by it)",
     "resolution": "R-173 with D-10 (the same draft, not applied); Q13's hot leakage a bench row (R-176)", "rows": ["IF-01"]},
    {"id": "D-12", "title": "the panel lead's CS116 and CS115 (MIL-STD-461G under REQ-063) on the drawn entry", "state": "RESOLVED (drafted); CS115 with the block on CONDITIONAL on R-174",
     "constraint": "D4 clamps at 39.00 V at CS116's 10 A and 37.34 V at CS115's 5 A (hot end), over the drawn C11 and C12's 35 V (L4-E7's D1, D2)",
     "options": "the drafted entry's 50 V parts (L4-E7R) with the solar guard and D4 the SMCJ30A (R-173): D4 at 41.91 V (CS116) and 40.04 V (CS115) "
                "at the hot end, under 50 V; CS116 MEETS with the block on and off; CS115 MEETS with the block off and, with it on, is CONDITIONAL on "
                "R-174 (the cable's recorded loop current under 15.68 A, or U5's differential measured under 0.3 V).",
     "resolution": "R-21 (apply_gen_sch_e_backstop.py) and R-173 (apply_gen_sch_e_solar_guard.py); R-174 records the loop current; R-156 judges under TRN-001", "rows": ["IF-01"]},
    {"id": "D-13", "title": "(B1)'s draft left board E's auxiliary domain on the pack's side of the battery FET (the review's B1)",
     "state": "ADDRESSED IN DRAFTS (L4-E11's fix round, drafted, not applied)",
     "constraint": "U12, board E's controller rail and both mixer fans sat on CELL_F, behind R17 on the pack's side of Q39: with the charge "
                   "inhibited and a source present the battery FET is off (SLUSE65A p.38) and they still discharged the pack; with the pack "
                   "absent or isolated nothing fed them; the 502.3 ms start leaned on a 0.5 A input ceiling as a delivered current",
     "options": "SELECTED (L4-E11 15a): VSYS alone over the dock, J_DOCK pin 1 from GND to VBAT and board E's J_BLK pin 1 to VSYS_E, U12, C31, "
                "the fans and D7, D8 on VSYS_E (1 A on one 813 contact, the ground return on seven, 79.3 C at the 51 C air with one open); "
                "a diode or ideal-diode OR with CELL_F not taken (it takes the pack whenever VSYS sits under it, which the +-2 % row allows); "
                "the held pack's drains bounded at 0.1408 mA; the start bounded to VSYS_MIN or a latch within 3.062 s",
     "resolution": "R-177 (apply_gen_sch_e_aux.py, E11-33) and R-178 (apply_pcb_interfaces_dock.py, E11-34), not applied; the bench rows of "
                   "E11-31 (R-161: the held pack current at most 1 mA, the start from cold); the fans' rating to 17.375 V (R-179, E11-35)",
     "rows": ["IF-06", "IF-09", "IF-11"]},
    {"id": "D-14", "title": "(B1)'s battery FET bounded at a drive and temperature corner the sheets do not print, and a fallback that lowered the 18 A for 60 s service (the review's B2)",
     "state": "ADDRESSED IN DRAFTS (L4-E11's fix round, drafted, not applied), CONDITIONAL on the installed path and the docking split",
     "constraint": "Q39 (AONS21357) was bounded at 10.7 mOhm at VGS -10 V and 125 C while BATDRV gives 8.5 V at its least; 12 mOhm at the "
                   "real corner, the review's counterexample, puts TJ over 150 C; R-159's fallback limited 18 A to 0.916 s after 10 A held against IF-AE-DOCK's 18 A for 60 s",
     "options": "L4-E11's three on one basis (RDS(on) from the printed maxima at BATDRV's 8.5 V and the hot junction): (Q-a) one AONS21357, "
                "a bar of 10.1 C/W; (Q-b) one SQJ403EP, 9.49 C/W; SELECTED (Q-c) two Nexperia BUK6Y10-30P in parallel (Q39, Q40), 34.42 "
                "C/W per FET at the +70 C mixed air, every protection event at TJ 150 C or under, 18 A for 60 s at 119.8 C, ISM 320 A each "
                "over the 242.9 A docking pulse, Ciss 4.72 nF typical inside TI's 5 nF; R-159's fallback withdrawn",
     "resolution": "R-157 (apply_gen_sch_a_charger.py, the pair), not applied; E11-29 (R-159: each FET's installed path at most 34.42 C/W), "
                   "E11-30 (R-160: the docking split at most 0.848 hot), E11-32 (R-162: the parts' supply)",
     "rows": ["IF-09", "IF-10"]},
]
OWNERS = ["Layer 4 coordinator", "Layer 5 interfaces", "Layer 6 components", "Layer 7 mechanical", "Layer 8 board A generator owner",
          "Layer 8 board E generator owner", "Layer 8 board P generator owner", "Layer 9 pre-layout analysis", "prototype bench",
          "firmware owner", "TEST-PLAN owner", "Layer 8 board B generator owner", "Layer 8 board C generator owner", "CONOPS owner"]

# The owner's items: decisions and outside contacts only, kept apart from the engineering work (the register). Each names the
# pinned document it rests on; the session contacts no outside party, it prepares the texts.
OWNER_ITEMS = [
    {"id": "OW-1", "what": "CFL-002 (U-02): the SGP41 in the battery bay against REQ-042's VOC channel inside the envelope: A, a BME688-class "
                           "sensor in its place (L4-E12's recommendation); B, the VOC channel dropped; C, the SGP41 kept, its channel reported as "
                           "not covered above a 49.0 C reading and after storage outside 5 to 30 C, the sensor off from a 54.0 C reading; it also sets "
                           "the governing line at REQ-024's +40 C (L4-E12 12a): with no option taken, the SGP41's Table 4 +50 C, 2.554 W/K on the "
                           "pack and 2.709 W/K on shore, class (iii) with the lid closed; under C, A or B the cells' hot stop H1, 1.666 and "
                           "1.642 W/K",
     "docs": [("l4e12md", "L4-E12's page, section 8")]},
    {"id": "OW-2", "what": "U-01, item 1: send the drafted request for the HL18650V's signed product specification (Yichun Topwell Power), "
                           "ten questions since L4-E10's dependency round (7 to 10 added: the cold charge band and termination, the pulse "
                           "current, the cold capacity, the end-of-life capacity and self-discharge)",
     "docs": [("cl_topwell", "Yichun Topwell Power: the HL18650V's signed specification, ten questions (U-01)")]},
    {"id": "OW-3", "what": "U-01, item 2: approve D-06's cell, energy and spend: the Saft MP 176065 xtd as 4S1P (the supported route on published "
                           "evidence for the temperature windows: about 145 Wh to about 82 Wh nominal, 53.5 to 55.1 Wh usable, NZ$ 954.88 for four "
                           "cells; NOT YET ADOPTABLE: current at temperature, the storage dwell and recovery and the fit awaited), or the HL18650V in the 4S3P (about 121 Wh nominal, about USD 42 a pack) once its "
                           "specification or a soak confirms L4-E10's rows; REQ-046 and REQ-077 restated with the cell; if declined, LO-01d to g "
                           "stay a release gate",
     "docs": [("l4e10md", "L4-E10's page, sections 8 and 15")]},
    {"id": "OW-4", "what": "the other outside-contact drafts to send (the owner chooses the channel; Topwell's is OW-2, TI's OW-7)",
     "docs": [("cl_pdi", "Pervasive Displays: the E2370KS0C1's storage and operation (U-02)"),
              ("cl_sensirion", "Sensirion: the SGP41's duration, recovery and storage (U-02, CFL-002)"),
              ("cl_adi", "Analog Devices: the LT8705A's IMON_IN limits (the 100 W bound; R-33, R-101)"),
              ("cl_milliohm", "Milliohm: the HoJLR2512's temperature coefficient below +25 C (R-101)"),
              ("cl_vishay", "Vishay: the WSL2512's pulse capability (R-101)"),
              ("cl_ti", "Texas Instruments: the INA169's error envelope (R-101)"),
              ("cl_eaton", "Eaton: the SCF9550 above +60 C and in storage (PWR-F12; R-103)"),
              ("cl_sunpower", "SunPower (the module's maker): a warranted Voc band at STC for the SPR-E-Flex-100 (U-03's route 1)"),
              ("cl_solbian", "Solbian: a warranted Voc band for the SX 156 (U-03's route 1)")]},
    {"id": "OW-5", "what": "the fallbacks, to send only if T-H1 reads under a +70 C line that governs (M6's 1.806 W/K once PDi states the "
                           "e-paper's range, M7's 2.159 W/K; L4-E12 12a)",
     "docs": [("cl_gc", "Ground Control: the RockBLOCK 9704"), ("cl_nicerf", "NiceRF: the SA868"), ("cl_bulgin", "Bulgin: the PXP4043C")]},
    {"id": "OW-6", "what": "PANEL-ACC (U-03, L4-E13): buy one SunPower SPR-E-Flex-100, recorded by serial number, and have it measured to the "
                           "specification (M1 to M3 and A-2's reading); actions under the owner's authority (money), not questions",
     "docs": [("l4e13md", "L4-E13's page, PANEL-ACC")]},
    {"id": "OW-7", "what": "U-04: send TI the battery packet's questions (REVIEW-REQUEST.md section 4) with L4-E11's TI-QUESTIONS.md: under (B1) "
                           "Q-TI-15 (D2) and Q-TI-16 (VSYS_MIN's maximum) to TI (Q-AOS-1 withdrawn in L4-E11's fix round: the pair's ISM is printed); on the board as "
                           "drawn Q-TI-11 to Q-TI-14 and the addendum to Q-TI-3 (D1 and D3 decide U-04 there; E11-05, E11-25; R-114, R-160); "
                           "an action, not a question",
     "docs": [("ti_review", "Texas Instruments: the battery packet"), ("cl_tiq", "Texas Instruments and AOS: the dependency rounds' questions")]},
    {"id": "OW-8", "what": "U-02 (T-H1 decides every class (i) and (ii) line): authorise T-H1 on the bench, its points of L4-E12 12d (M2 and "
                           "M6 first: the heat stage lid open, one heater at 25.136 W plus the fans, one logger; then M1, M4 and M3 lid closed, "
                           "M7, M5, M8 and M9, the fans-off case and the transient point), the combined route's kit (R-170 to R-172) only if a "
                           "point reads under its line; "
                           "its purchase (a current-moulding Peli 1450 with the 1450PF frame, a 3 mm plate "
                           "blank, the heaters, the fans as stand-ins until D-18, a second PicoLog TC-08) and who runs it; a chamber run at +60 C "
                           "only if wanted, at a laboratory, his spend; the procedure is drafted and the session cannot run it (R-104, R-151); "
                           "an action, not a question",
     "docs": [("th1proc", "T-H1's procedure, drafted")]},
    {"id": "OW-9", "what": "U-01's smallest experiments and Saft's statement: send the drafted request to Saft (expanded after the review's "
                           "B5: the currents at the cells' temperatures, the pulses, charge below 0 C, the storage dwell and recovery, the minimum "
                           "capacity, the thickness, the charge termination); authorise the limited sample qualification in Saft's place (L4-E10 "
                           "10g: one cell, NZ$ 238.72, a chamber from -40 to +85 C and a 25 A load, about two weeks) and the printed mock-up of "
                           "four cells in the pocket (no purchase); actions, not questions",
     "docs": [("cl_saft", "Saft: the MP 176065 xtd in a 4S1P pack")]},
    {"id": "OW-10", "what": "U-02's four class (iii) lines (L4-E12 12e; no measurement can pass them): one option each, none lowering a "
                            "requirement silently; (1) E3-L at +40 C lid closed (M3, M4): CFL-002's C, A or B (OW-1), a closed-lid ceiling "
                            "on REQ-042's VOC channel (an ambient of +31.3 to +38.8 C on the pack, +30.2 to +38.2 C on shore), or D-02b's "
                            "closed-lid test at +40 C restated; (2) E3-O at +55 C (M6): PDi's statement (OW-4), an e-paper with a held range "
                            "at or over +70 C (CHO-001), or E3-O with the e-paper's state recorded as a deviation (TEST-PLAN); (3) E5's +60 C "
                            "dwell (M7): PDi's statement, a different e-paper (CHO-001), or E5 with the e-paper out as a recorded deviation; "
                            "the session's two options (the e-paper's window temperature measured, a closed-lid conduction path at Layer 7) "
                            "are engineering work, not his; decisions",
     "docs": [("l4e12md", "L4-E12's page, section 17.9")]},
]
OWNER_NOT_DRAFTED = ("not yet drafted (engineering work first, then the owner sends): Littelfuse, F1's total clearing I2t at 900 A and 58 V DC "
                     "(R-115, E11-16); Coilcraft, L10's inductance against current at temperature (R-120) and L1's Isat at 85 C (R-31); Milliohm, "
                     "R227's single-pulse rating (R-101)")
OWNER_MARK = {"l4e12md": r"\*\*Owner question: which of these three\?\*\*", "l4e10md": r"The recommendation needs the owner for exactly two things",
              "cl_tiq": r"\*\*Drafts for the owner to send\*\*", "th1proc": r"once the owner authorises it",
              "ti_review": r"Nothing in this file has been sent to anyone", "l4e13md": r"the purchase and the measurement are the owner's\s+actions"}

# The accepted records' downstream items mapped onto this register (deduplicated): L4-E11's E11-NN by its From column (every
# one but E11-19, which this record answers, out 12); L4-E10's and L4-E12's owner rows by these maps.
E11_ANSWERED_HERE = {"E11-19"}
E10_MAP = {"Session (layer 4)": ["R-103", "R-47"], "Layer 6, components": ["R-103"], "Layer 7, mechanical": ["R-111"],
           "Layer 8, generator owners": ["R-105"], "Layer 9, pre-layout": ["R-108"], "Prototype bench": ["R-104", "R-109"],
           "TEST-PLAN's owner": ["R-110"], "Firmware owner": ["R-106"], "Board B's owner": ["R-107"],
           "The kit's thermal owner (outside FEA-008)": ["R-111"], "Owner": ["OW-2", "OW-3", "OW-9"]}
E12_MAP = {"Owner": ["OW-1", "OW-10"], "Layer 4 coordinator": ["this record (IF-11, U-02, out 12e)"],
           "Layer 2 and 5 integrators, firmware owner": ["R-138", "R-139"], "TEST-PLAN's owner": ["R-140"],
           "Layer 6 components": ["R-141"], "Layer 6, architecture-level": ["R-142"], "Layer 6, downstream": ["R-143"],
           "Layer 7 mechanical": ["R-111"], "Layer 8, board E's generator owner": ["R-144"], "Layer 8, board C's generator owner": ["R-145"],
           "Layer 9 pre-layout": ["R-146"], "Prototype bench": ["R-104", "R-109"], "Owner (outside contacts)": ["OW-4", "OW-5"]}


def gate_violations(gate, st):
    """The criteria marked PASS that rest on a row not reading MEETS, or on an ASSUMPTION, CONDITIONAL or PENDING row; and
    the criteria naming a row the reconciliation does not print. The closure gate's rule, held by test_l4e9.py too."""
    bad = []
    for g in gate:
        for rid in g["rows"]:
            if rid not in st:
                bad.append((g["n"], "unknown row %s" % rid))
        if g["verdict"] == "PASS":
            for rid in g["rows"]:
                cls, s = st.get(rid, ("PENDING", "PENDING"))
                if s != "MEETS" or cls in ("ASSUMPTION", "CONDITIONAL", "PENDING"):
                    bad.append((g["n"], "%s reads %s, %s" % (rid, s, cls)))
        elif not g["constraint"] or not g["overturn"]:
            bad.append((g["n"], "a criterion not PASS names no constraint or no overturn answer"))
    if sorted(g["n"] for g in gate) != [1, 2, 3, 4, 5]:
        bad.append((0, "the gate does not cover the five criteria"))
    ids = {c["id"] for c in CHOICES}
    for g in gate:
        for cid in g.get("choices", []):
            if cid not in ids:
                bad.append((g["n"], "unknown choice %s" % cid))
            elif g["verdict"] == "PASS":
                bad.append((g["n"], "PASS while the unresolved choice %s stands" % cid))
        if g["n"] == 2 and g["verdict"] == "PASS" and any(d["state"] == "OPEN" for d in DEFECTS):
            bad.append((2, "PASS while a material defect is open"))
    for c in CHOICES:
        if not all(c.get(k) for k in ("question", "constraint", "evidence", "supplier", "fallback", "overturns", "rows", "class")):
            bad.append((0, "choice %s lacks a field" % c["id"]))
        elif len(c["evidence"]) != len(EVIDENCE_LABELS) or not all(c["evidence"]):
            bad.append((0, "choice %s does not give its evidence by vendor, physical and owner" % c["id"]))
    klass = {c["id"]: c.get("class") for c in CHOICES}
    arch = {c["id"] for c in CHOICES if c.get("class") == ARCH}
    for g in gate:
        for cid in g.get("choices", []):
            if cid in klass and klass[cid] != ARCH:
                bad.append((g["n"], "%s, a downstream selection, named as a choice that could overturn the architecture" % cid))
        if g["n"] in (1, 5) and set(g.get("choices", [])) != arch:
            bad.append((g["n"], "criterion %d does not name exactly the architecture-level choices %s" % (g["n"], sorted(arch))))
    return bad


def md_table(text, header_start):
    """The rows of the first markdown table whose header line starts with header_start."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith(header_start):
            out = []
            for l2 in lines[i + 2:]:
                if not l2.startswith("|"):
                    break
                out.append([c.strip() for c in l2.strip().strip("|").split("|")])
            return out
    return []


def main():
    F, where = compute()
    D = derived(F)
    A = partA(F, D, _C_TEXT)
    E = rejudge(F, D, A)
    R = rows(F, D, A, E)
    st = {r["id"]: row_status(r) for r in R}
    for r in R:
        for k in ("v", "i"):
            if r[k].count(" | ") != 1 or not all(x.strip() for x in r[k].split(" | ")):
                refuse(4, "%s's %s does not give both sides" % (r["id"], k))
        if not r["settled"] or not r["checks"] or not r["a"] or not r["b"]:
            refuse(4, "%s has no settling record, check or side" % r["id"])
    out = []
    p = out.append
    p("L4-E9: THE CONNECTED POWER ARCHITECTURE AND LAYER 4'S CLOSURE GATE (MESHSAT-1357, 1 October 2026; round 2 and the update round, 2 October")
    p("2026). Prototype")
    p("design, desk arithmetic:")
    p("nothing is bought, built, powered or measured. Every figure is read from a generator, a committed netlist, a record's committed")
    p("output or a maker's document, each pinned by sha256; the few this record sets itself are named. Classes: MAKER, NETLIST, MODELED,")
    p("INFERRED, CONDITIONAL, ASSUMPTION, PENDING.")
    p("")
    p("0. INPUTS (sha256/16, where read)")
    for key, (rel, _) in PINS.items():
        w, h = where[key]
        p("   %-9s %s  %s%s" % (key, h[:16], rel, "" if w == "tree" else "  (" + w + (", fnd/l4e8 accepted)" if key in FROM_L4E8 else ", " + FROM_LABEL[key] + ")")))
    p("   pending: %s" % L4E7R)
    p("   L4-E13 (U-03, the panel) accepted by the coordinator's check 3 at fae419d1 and, after set 25, check 4 at 33b6b7be: section 13")
    p("   this record's own figures: copper %s ohm mm2/m at 20 C and %s /K, 18 AWG %s mm2 (ASSUMPTION, constants); the cold end %s C (REQ-024);"
      % (fmt(CU_RHO_20C), fmt(CU_ALPHA), fmt(AWG18_MM2), fmt(T_COLD)))
    p("     capacitance kept under bias %s (ASSUMPTION; the bound states the fraction it needs); the back-feed diode's drop %s V (an upper bound);"
      % (fmt(BIAS_KEEP), fmt(VF_BACKFEED)))
    p("     the charger's L2 +-%s %% (Coilcraft XAL family)" % fmt(L2_TOL * 100))
    p("")
    p("1. THE MAKERS' ROWS (pdftotext, the page cited)")
    p("   LM5176 (SNVSAI1D 6.1): VIN, VISNS %s V absolute. LM74700-Q1 (SNOSD17G 6.1, 6.3): CATHODE to ANODE %s V absolute, ANODE to"
      % (fmt(F["u2_vin_abs"]), fmt(F["ld_ca_abs"])))
    p("     CATHODE -%s V recommended, ANODE %s V. CSD19532Q5B %s V; BSC039N06NS %s V. LM5069 (SNVS452G 7.1, 7.5): VIN %s V absolute, VCL %s / %s / %s mV."
      % (fmt(F["ld_ac_rec"]), fmt(F["ld_anode_abs"]), fmt(F["csd19532_vds"]), fmt(F["bsc039_vds"]), fmt(F["lm5069_vin_abs"]), fmt(F["vcl"][0]), fmt(F["vcl"][1]), fmt(F["vcl"][2])))
    for part in ("SMCJ18A", "SMCJ22A", "SMCJ28A", "SMCJ36A", "SMCJ40A"):
        q = F[part]
        p("   Littelfuse %s: VR %s V, VBR %s to %s V at 1 mA, VC %s V at %s A" % (part, fmt(q["vr"]), fmt(q["vbr_min"]), fmt(q["vbr_max"]), fmt(q["vc"]), fmt(q["ipp"])))
    p("   TPS2596 (7.1): VIN %s V absolute. INA226 (SBOS547 5.1): VBUS, IN+ and IN- %s V absolute; common mode %s V (CMRR row); full scale %s mV."
      % (fmt(F["tps2596_abs"]), fmt(F["ina_abs"]), fmt(F["ina_cm_op"]), fmt(F["ina_fs_mv"])))
    p("   BQ25731 (SLUSE66A p.8, p.14): VBUS, VSYS %s V absolute; SYSOVP %s / %s / %s V. Littelfuse 297 MINI: %s V DC, %s A interrupting."
      % (fmt(F["u3_abs"]), fmt(F["sysovp"][0]), fmt(F["sysovp"][1]), fmt(F["sysovp"][2]), fmt(F["f297_v"]), fmt(F["f297_i"])))
    p("   JST VH p.1: %s A at AWG 16 with the standard header; %s A at AWG 18 with the shrouded header only. Mill-Max p.28: %s A continuous (0850 to"
      % (fmt(F["vh_16"]), fmt(F["vh_18"]), fmt(F["millmax_a"])))
    p("     0853, the 0858's sibling figure). Amass XT60: %s A rated." % fmt(F["xt60_a"]))
    p("")
    p("2. THE GENERATORS' DECLARATIONS (syntax tree)")
    for k, nm in (("vbat", "A VBAT"), ("vin_raw_a", "A VIN_RAW"), ("vbus20", "A VBUS20"), ("pa", "A +13V8_PA"), ("hf", "A +12V_HF"), ("poe", "A +54V_POE"),
                  ("pd", "A PD_VBUS"), ("vmon", "A VMON"), ("vheat", "A VHEAT"), ("vin_raw_e", "E VIN_RAW"), ("pv", "E PV_P"), ("trk", "E TRK_OUT"),
                  ("cell_f", "E CELL_F"), ("p_pack", "P PACK_P")):
        r = F[k]
        extra = "".join(", %s %s" % (kk, fmt(r[kk])) for kk in ("v_work", "v_max", "efficiency") if r.get(kk) is not None)
        p("   %-11s %s V, %s A typical, %s A peak%s" % (nm, fmt(r["volts"]), fmt(r["typ"]), fmt(r["peak"]), extra))
    p("   parts: A F1 '%s'; A D1 '%s'; A D2 '%s'" % (F["a_f1"], F["a_d1"][:40], F["a_d2"][:40]))
    p("     E F1 '%s'; E F2 '%s'; E D10 '%s'" % (F["e_f1"], F["e_f2"], F["e_d10"][:40]))
    p("     E Q1 (ideal_diode) '%s'; E Q7 '%s'" % (F["e_q1"][:44], F["e_q7"][:44]))
    p("     E R19 '%s'; R21 '%s'; R23 '%s'; R10 '%s'" % (F["e_r19"][:30], F["e_r21"], F["e_r23"], F["e_r10"]))
    p("     P F1 '%s'; P F2 '%s'" % (F["p_f1"][:44], F["p_f2"][:44]))
    p("   board A's netlist: VBAT carries %d capacitors, %s uF nominal; D1 on VBAT: %s; U17's pins on POE_OUT %s and on +54V_POE %s"
      % (F["vbat_caps"][0], fmt(round(F["vbat_caps"][1], 2)), "yes" if F["vbat_d1_on_net"] else "no", F["u17_nets"]["POE_OUT"], F["u17_nets"]["+54V_POE"]))
    p("")
    p("3. THE RECORDS' FIGURES (each read from the line that prints it)")
    p("   L4-E4: the window %s W at VBUS20 needs %s A; IIN_HOST %s A (minimum %s A, maximum %s A board current, %s A through R11); U3's own %s A"
      % (fmt(F["win_w"]), fmt(F["win_need"]), fmt(F["iin_host"]), fmt(F["u3_min"]), fmt(F["u3_max_board"]), fmt(F["r11_need"]), fmt(F["u3_max_u3"])))
    p("     R11 8 mOhm band %s / %s / %s A, 7 mOhm %s / %s / %s A; at 62.1 C with C-1's taps %s A (+%s A); R138 trip %s to %s A; U19 %s / %s / %s A"
      % (*[fmt(x) for x in F["r11_8"]], *[fmt(x) for x in F["r11_7"]], fmt(F["r11_min_62_full"]), fmt(F["r11_margin_62_full"]), fmt(F["trip"][0]), fmt(F["trip"][1]), *[fmt(x) for x in F["u19_lim"]]))
    p("   L4-E5 (H3): U3 effective maximum and the front end's input maximum at 9 / 12 / 24 / 36 V: %s"
      % "; ".join("%s A, %s A (%s %%)" % (fmt(F["h3"][v][0]), fmt(F["h3"][v][1]), fmt(F["h3"][v][2])) for v in (9.0, 12.0, 24.0, 36.0)))
    p("     HIZ certain below %s V, out of HIZ above %s V, regulation by the pin from %s V; U3 at least %s A at 9.0 V; ceiling %s / %s / %s V (drawn %s / %s / %s V)"
      % (fmt(F["hiz_below"]), fmt(F["hiz_out_above"]), fmt(F["pin_reg_from"]), fmt(F["u3_at_9"]), *[fmt(x) for x in F["trk_ceiling"]], *[fmt(x) for x in F["trk_drawn"]]))
    p("     the entry %s to %s A (basis %s A), timer %s / %s / %s ms; restart guard %s / %s / %s V; pin path %s A (V-A07 %s A); FE input under 4.80 A while the 9 V efficiency is at least %s"
      % (fmt(F["entry_lim"][0]), fmt(F["entry_lim"][1]), fmt(F["entry_basis"]), *[fmt(x) for x in F["timer_ms"]], *[fmt(x) for x in F["latch"]], fmt(F["pin_path"]), fmt(F["pin_err_allow"]), fmt(F["eff_floor_9v"])))
    p("     on the candidate panel H3 gives up %s to %s Wh a day; A2 unserved %s to %s Wh (48 h), %s to %s Wh (72 h)"
      % (fmt(F["h3_cand_given"][0]), fmt(F["h3_cand_given"][1]), *[fmt(x) for x in F["h3_cand_a2"]]))
    p("   L4-E6: R12 12 mOhm peak %s / %s / %s A; service peak %s A; 9 V: L1 %s A average, output %s A; 15.1 V L1 %s A; average limit above %s V;"
      % (*[fmt(x) for x in F["r12_peak"]], fmt(F["svc_peak"]), fmt(F["fe_in_9v"]), fmt(F["fe_out_9v"]), fmt(F["fe_in_151"]), fmt(F["avg_from"])))
    p("     L1 peak bound %s A (%s %% of %s A), Isat needed %s A at %s C; FETs at most %s C; the bus %s V, efficiency %s"
      % (fmt(F["l1_peak"]), fmt(F["l1_pct"]), fmt(F["l1_isat"]), fmt(F["l1_need"]), fmt(F["l1_qual"]), fmt(F["fet_tj"]), fmt(F["vbus_max_r11"]), fmt(F["eta_fe"])))
    p("   L4-E7R (675b8068, accepted): the regulation %s A nominal, %s A highest (%s / %s W in at the hold); the backstop trips at %s to %s A at 25 V; static bound"
      % (fmt(F["reg"][0]), fmt(F["reg"][1]), fmt(F["reg_w"][0]), fmt(F["reg_w"][1]), fmt(F["bs_trip"][0]), fmt(F["bs_trip"][1])))
    p("     %s W (CONDITIONAL), the regulation's 25 V corner %s W; %s ms allowance; SWEN off below %s V; U5's differential %s V; the hot short circuit %s A;"
      % (fmt(F["static_bound"]), fmt(F["reg_corner"]), fmt(F["bs_allow_ms"]), fmt(F["swen_v"]), fmt(F["u5_diff"]), fmt(F["isc_hot_tol"])))
    p("     energy %s / %s / %s Wh (SC-37), %s Wh (bright day); the bank %s / %s Wh; R66 %s, RIMON_IN %s, %d x 100 nF C0G on INB (%s to %s ms);"
      % (*[fmt(x) for x in F["e7r_day"]], fmt(F["e7r_bright"]), fmt(F["bank_wh"][0]), fmt(F["bank_wh"][1]), F["r66"], F["rimon"], F["filt_n"], fmt(F["tau_min_ms"]), fmt(F["tau_max_ms"])))
    p("     CS101's filtered ripple %s A at %d Hz against a %s A margin (break-even %s times); held charge %s J; the bulk up to %s times its ripple rating;"
      % (fmt(F["m2_ripple"]), F["m2_hz"], fmt(F["m2_margin"]), fmt(F["loop_breakeven"]), fmt(F["held_j"]), fmt(F["bulk_ripple_x"])))
    p("     G_CM and the VIN+ bias break-evens %s %% and %s mA; hold %s / %s / %s V, conditioned" % (fmt(F["gcm_be"]), fmt(F["vinb_be"]), *[fmt(x) for x in F["hold"]]))
    p("     %s to %s V; U5 about %s C" % (fmt(F["hold_cond"][0]), fmt(F["hold_cond"][1]), fmt(F["u5_tj"])))
    p("   L4-E10 (79b2f568): FEA-008 not closed; (II) recommended, CONDITIONAL; T-H1 at least %s W/K; the conditioned corner's air %.2f C (E3-O), %.2f C (E5),"
      % (fmt(F["th1"]), F["corner_air"][0], F["corner_air"][1]))
    p("     the +%s C parts; usable %s Wh (35E) and %s Wh (HL18650V, %s %% less), %s Wh nominal against %s; the kit's heat at E3-O's corner %s W (INFERRED)"
      % (fmt(F["parts_hot"]), fmt(F["cell_usable"][0]), fmt(F["cell_usable"][1]), fmt(F["cell_less_pct"]), fmt(F["cell_nom"][1]), fmt(F["cell_nom"][0]), fmt(round(F["corner_heat"], 2))))
    p("     LO-01e under (II): the cells %s C, %s K under the page's limit, %s K under the re-derived H1 and %s K under U2's INFERRED trip;"
      % (fmt(F["lo01e"][0]), fmt(F["lo01e"][1]), fmt(F["lo01e"][2]), fmt(F["lo01e"][3])))
    p("     USD %s a cell, so about USD %s a 4S3P pack of 12 (a marketplace price)" % (fmt(F["cell_usd"]), fmt(round(F["cell_usd"] * 12))))
    p("   L4-E11 (3298d1f1, accepted): the entry TPS48110-Q1 with a CSD19536KTT, R19 4.5 mOhm, L2 SRF1260-1R0Y: UVLO on %s / %s / %s V, off %s / %s / %s V;"
      % (*[fmt(x) for x in F["e_uv_on"]], *[fmt(x) for x in F["e_uv_off"]]))
    p("     OV off above %s / %s / %s V, on under %s / %s / %s V; overcurrent %s / %s / %s A after %s / %s / %s ms; short circuit %s / %s / %s A; retry %s s"
      % (*[fmt(x) for x in F["e_ov_off"]], *[fmt(x) for x in F["e_ov_on"]], *[fmt(x) for x in F["e_oc"]], *[fmt(x) for x in F["e_oc_ms"]], *[fmt(x) for x in F["e_sc"]], fmt(F["e_retry_s"])))
    p("     the loop %s / %s / %s mOhm (plug to DC_P, on to VIN_RAW, in all, hot); in service %s A at a 9.00 V plug, %s %% under the trip, front end at least %s;"
      % (*[fmt(x) for x in F["e_loop_mohm"]], fmt(F["e_svc"][1]), fmt(F["e_margin_pct"]), "%s" % F["e_eta_floor"]))
    p("     the knee %s A flat from %s V, HIZ certain below %s V; the guard falls at %s to %s V (R14 76.8k); D-06: the loop's floor %s mOhm, %s A at %s V"
      % (fmt(F["knee"][0]), fmt(F["knee"][1]), fmt(F["knee_hiz"]), fmt(F["guard_sel"][0]), fmt(F["guard_sel"][2]), fmt(F["loop_floor"]), fmt(F["ipf_spec"]), fmt(F["e_basis_v"])))
    p("   L4-E12 (a86be47b, accepted): T-H1's binding line %s W/K (E3-O alone %s, no hold %s); at the line %s C (E3-O) and %s C (E5, hold); hold reference"
      % (fmt(F["gc"]), fmt(F["g_e3o"]), fmt(F["g_a"]), "%.2f" % F["e3o_line"], "%.2f" % F["e5_line"]))
    p("     +-%s K; E5's heat under the hold %s W, the heat stage %s W into the case; at the floor %s / %s C; LO-01a with the ballasts %s W/K"
      % ("%s" % F["hold_ref"], fmt(F["e5_hold_w"]), fmt(F["e3o_stage_w"]), "%.2f" % F["floor_air"][0], "%.2f" % F["floor_air"][1], fmt(F["lo01a_ball"])))
    p("   L4-E8: every can at most %s A against %s A (8 mOhm), %s against %s A (7 mOhm); ballasts at most %s W (%s W at the nominal illustration)"
      % (fmt(F["can8"][0]), fmt(F["can8"][1]), fmt(F["can7"][0]), fmt(F["can7"][1]), fmt(F["ballast_w"]), fmt(F["ballast_nom_w"])))
    p("   s120: VBUS20 %s to %s V, bound %s V; OVLO %s / %s / %s V; ChargeVoltage at most %s V; BATOVP %s V; ACOV %s V minimum"
      % (fmt(F["vbus_band"][0]), fmt(F["vbus_band"][1]), fmt(F["vbus_bound"]), *[fmt(x) for x in F["ovlo"]], fmt(F["chg_v_max"]), fmt(F["batovp"]), fmt(F["acov_min"])))
    p("     the selected OVLO (R23 6.42k, R22 100k, both 0.1 %%): %s / %s / %s V (this record, part A)" % tuple(fmt(round(x, 2)) for x in F["ovlo_sel"]))
    p("   the budget: PS-IDLE-SPEC %s / %s / %s W; PS-ALLTX %s / %s / %s W; the PA keyed alone at 113 W %s W, %s A at 10.0 V; PS-TYP plus USB-C %s W"
      % (*[fmt(x) for x in F["idle"]], *[fmt(x) for x in F["alltx"]], fmt(F["pa113"][0]), fmt(F["pa113"][4]), fmt(F["typ_usbc"][0])))
    p("   the pack: %s A continuous, %s A peak; prospective %s to %s A; OCD1 %s A for %s s; OCC %s A; SCD %s A; COV %s V, CUV %s V; inside air %s / %s C (lid open / closed)"
      % (fmt(F["pp_cont"]), fmt(F["pp_peak"]), fmt(F["pp_fault"][0]), fmt(F["pp_fault"][1]), fmt(F["ocd1"][0]), fmt(F["ocd1"][1]), fmt(F["occ"]), fmt(F["scd"]), fmt(F["cov"]), fmt(F["cuv"]), fmt(F["air"][0]), fmt(F["air"][1])))
    p("")
    p("4. THE INTERFACE ROWS (the selected architecture: A1, with L4-E4 to L4-E8, L4-E11 and L4-E12 applied and this record's changes; 'as drawn' checks show a defect")
    p("   the selected design resolves, 'the alternative' checks the LM5069 kept instead of L4-E11's entry). Each row: both sides' ranges, the currents at the")
    p("   modes, losses, thermal, protection, the record that settles it.")
    for r in R:
        cls, s = st[r["id"]]
        p("   %s  %s  [%s, %s]" % (r["id"], r["title"], s, cls))
        p("     sides: %s | %s" % (r["a"], r["b"]))
        p("     voltage: %s" % r["v"])
        p("     current: %s" % r["i"])
        p("     losses: %s; thermal: %s" % (r["loss"], r["therm"]))
        p("     protection: %s | %s" % (r["prot_a"], r["prot_b"]))
        p("     settled by: %s" % r["settled"])
        for c in r["checks"]:
            p("       - " + c.line())
    counts = {}
    for r in R:
        counts[st[r["id"]][1]] = counts.get(st[r["id"]][1], 0) + 1
    p("   rows: %d; %s" % (len(R), ", ".join("%s %d" % (k, counts[k]) for k in sorted(counts))))
    p("")
    p("5. SIMULTANEOUS OPERATION (solar at the window, a vehicle at 24 V, the full load, charging)")
    p("   the front end's input is the H3 line's at VIN_RAW whatever the sources share: at 24 V at most %s A, %s %% of the breaker's lowest %s A; the tracker's"
      % (fmt(F["h3"][24.0][1]), fmt(round(F["h3"][24.0][1] / F["e_oc"][0] * 100, 1)), fmt(F["e_oc"][0])))
    p("   ceiling (%s V minimum) is above 24 V, so the panel carries the bus first and the vehicle supplies only what the panel does not give"
      % fmt(F["trk_ceiling"][0]))
    p("   delivered at VBAT: %s to %s W (U3 between its minimum at the lowest bus and its board-current maximum at the bus's top, U3 %s)"
      % (fmt(round(D["vbat_avail_min"], 1)), fmt(round(D["vbat_avail_max"], 1)), fmt(F["eta_u3"])))
    for nm, w in (("PS-IDLE-SPEC plan", F["idle"][1]), ("PS-TYP plus USB-C plan", F["typ_usbc"][0]), ("the PA keyed alone at 113 W, plan", F["pa113"][0]), ("PS-ALLTX plan", F["alltx"][1]), ("PS-ALLTX high", F["alltx"][2])):
        short = w - D["vbat_avail_min"]
        if short <= 0:
            p("   %-34s %6s W: carried by the sources, up to %s W left to charge (at most %s A ChargeCurrent)" % (nm, fmt(w), fmt(round(-short, 1)), fmt(F["chg_set"])))
        else:
            p("   %-34s %6s W: the pack supplies at least %s W, %s A at a 14.4 V stack; no charge" % (nm, fmt(w), fmt(round(short, 1)), fmt(round(short / 14.4, 2))))
    p("   no stage is pushed past its limit: the entry stays under its breaker's lowest (H3), R11 carries at most %s A, every can at most %s A, the pack's"
      % (fmt(F["r11_need"]), fmt(F["can8"][0])))
    p("   current falls by what the sources give (PS-ALLTX's floors of D-11 hold as on the pack alone), and the outlets drop while the PA keys")
    env = F["e_env"]
    p("   per source at VBAT, L4-E11's envelope at the plug (the losses hot, the corrected knee): 9 V %s to %s W; 12 V %s to %s W; 24 V %s to %s W;"
      % (fmt(env[9][1]), fmt(env[9][2]), fmt(env[12][1]), fmt(env[12][2]), fmt(env[24][1]), fmt(env[24][2])))
    p("     36 V %s to %s W (round 2's figures at VIN_RAW with no loss and L4-E5's drawn knee: 9 V %s to %s W, 12 V up to %s W, 24 V up to %s W)"
      % (fmt(env[36][1]), fmt(env[36][2]), fmt(round(D["vbat_at_9"][0], 1)), fmt(round(D["vbat_at_9"][1], 1)), fmt(round(D["vbat_at_12"], 1)), fmt(round(D["vbat_at_24"], 1))))
    p("   so at a 9.00 V plug the vehicle runs PS-IDLE-SPEC (%s W) with the pack supplementing, and charges only while the kit draws under %s W"
      % (fmt(F["idle"][1]), fmt(env[9][1])))
    p("")
    p("6. STARTUP")
    p("   source arriving: the selected entry (L4-E11) turns on at %s V of DC_P at the most and slews the bus up (%s to %s A for at most %s ms; the drawn"
      % (fmt(F["e_uv_on"][2]), fmt(F["e_inrush"][0]), fmt(F["e_inrush"][1]), fmt(F["e_start_ms"])))
    p("     LM5069, R21 '%s', cannot start from a 9.00 V plug); U3 is in HIZ below %s V (certain, the corrected knee; %s V on L4-E5's drawn line); the H3 line"
      % (F["e_r21"], fmt(F["knee_hiz"]), fmt(F["hiz_below"])))
    p("     bounds U3 from its first cycle with no host; the panel: the stage's own UVLO and soft start, the hold at %s V; SWEN stays off while"
      % fmt(F["hold"][1]))
    p("     TRK_LDO33 is under %s V, whatever the ramp (L4-E7R), and each backstop trip restarts through the soft start" % fmt(F["swen_v"]))
    p("   source leaving: VBAT is the system node (as drawn the pack's own node; under (B1) behind the battery FETs Q39 and Q40, which the charger turns")
    p("     on as an ideal diode when the source leaves, SLUSE65A p.38), so the pack carries the loads without a break; IIN_HOST resets to 3.25 A")
    p("     and firmware writes %s A again (FW-A16 restated); VIN_RAW falls through the restart guard (%s V at the highest with R14 76.8k; %s V as drawn)"
      % (fmt(F["iin_host"]), fmt(F["guard_sel"][2]), fmt(F["latch"][2])))
    p("     and the front end stops")
    B4 = source_only(F, D)
    p("   SOURCE-ONLY AND DEAD-PACK OPERATION (the focused check's B4; U-04)")
    p("     what the maker's sheet establishes (SLUSE66A): after VBUS qualification '%s' (9.3.1), with no battery condition, and its power-up"
      % B4["conv"])
    p("       figures are drawn '%s' (Figures 10-4, 10-5): U3 supplies VSYS with no battery; DPM gives the system priority and, past the input's"
      % B4["nobatt"])
    p("       limit, 'the system voltage starts to drop' (9.3.17); below VSYS_MIN the charge is clamped at %s mA (9.6.2.1). Board A straps" % fmt(B4["clamp_ma"]))
    p("       CELL_BATPRESZ for 4S (R26/R27), so U3 never sees 'battery removal': with the pack absent it regulates VBAT at ChargeVoltage, at most %s V"
      % fmt(F["chg_v_max"]))
    p("       (INFERRED: no current in R17, so the voltage loop sets VSRN); with the pack's discharge FET open at CUV it charges through that FET's")
    p("       body diode at the clamp, and VBAT sits at the pack's %s V or so plus the diode (INFERRED), against the converters' assumed %s V floor (A-14)"
      % (fmt(D["vbat_low"]), fmt(D["vbat_low"])))
    p("     the source envelope with no usable pack (round 2, at VIN_RAW with no loss; L4-E11's at the plug in section 5): 9 V %s to %s W, 12 V up to %s W, 24 V up to %s W, against PS-IDLE-SPEC"
      % (fmt(round(D["vbat_at_9"][0], 1)), fmt(round(D["vbat_at_9"][1], 1)), fmt(round(D["vbat_at_12"], 1)), fmt(round(D["vbat_at_24"], 1))))
    p("       %s W: at 9 V the kit cannot run its profile on the source alone (it sheds or stops); at 12 V and 24 V the line's maximum is above it"
      % fmt(F["idle"][1]))
    p("       (no minimum is printed there, so CONDITIONAL on the charger's limit tolerance); before the host writes")
    p("       IIN_HOST the input limit gives %s (CHARGER-STATE-SEQUENCE.md, INFERRED), so the boot load must stay under it until FW-A16, which"
      % B4["hostfree"])
    p("       FW-C01's order (the charger before any slot) intends but no record measures")
    p("     not resolvable from the held documents in round 2: whether the drawn converter (the BQ25731, its battery path a single node) keeps VSYS up with charge inhibited (Q-TI-3,")
    p("       %s); whether the gauge lets a pack at or below CUV take charge through its FETs with no precharge FET; whether every load" % B4["qti3"])
    p("       converter runs at the dead pack's VBAT (A-14). Board E's always-on comes up on CELL_F from VBAT (as drawn; under (B1) on VSYS_E, L4-E11 15a)")
    p("     L4-E11 (accepted) selects arrangement (A), the drawn charger with rules R-a to R-d (the holds as a state table, R-b's two charge settings,")
    p("       the shedding sequence, the image's pre-charge); at a 9.00 V plug the shed warm-up (%s W plan) is carried with %s W in hand while P1 stays"
      % (fmt(F["e_p2"][1]), fmt(F["e_p2_hand"])))
    p("       at most %s W; REQ-015 at 9.00 V at the plug is a CONDITIONAL CANDIDATE (E11-05, E11-06, E11-09, E11-22, E11-23): U-04 stays an unresolved"
      % fmt(F["e_p1_max"]))
    p("       choice until that evidence lands (section 12d)")
    p("")
    p("7. FAULTS, TRACED ACROSS THE STAGES")
    p("   reversed vehicle input (REQ-015): DC_P is back-fed from VIN_RAW through Q7's body diode (L4-E5's finding), so Q1 holds DC_P plus the")
    p("     reversed input: %s V with the drawn ceiling, %s V with L4-E5's raised ceiling, against BSC039N06NS %s V; a CSD19532Q5B (%s V) holds it,"
      % (fmt(D["q1_rev_drawn"]), fmt(D["q1_rev"]), fmt(F["bsc039_vds"]), fmt(F["csd19532_vds"])))
    p("     and U3's cathode to anode stays under its %s V recommended and %s V absolute" % (fmt(F["ld_ac_rec"]), fmt(F["ld_ca_abs"])))
    p("   a short behind F1: F1 must interrupt at up to %s V (the basis L4-E11 keeps; the selected OV maximum %s V); the drawn cable (%s m of %s mm2 a way)"
      % (fmt(round(D["f1_v"], 2)), fmt(F["e_ov_off"][2]), fmt(F["cable_m"]), fmt(F["cable_mm2"])))
    p("     and lead (%s mm of AWG %d)" % (fmt(F["lead_mm"]), int(F["lead_awg"])))
    p("     give %s Ohm at 20 C and %s Ohm at %s C, so a stiff source drives at most %s A (copper alone); the drawn 297 is rated %s V DC: NOT MET"
      % (fmt(round(D["f1_r20"], 5)), fmt(round(D["f1_rcold"], 5)), fmt(T_COLD), fmt(round(D["f1_ipf"], 1)), fmt(F["f297_v"])))
    p("     as drawn; the selected 0997010.WXN is rated %s V DC and %s A at 58 V DC: MEETS (part A, section 11); the selected interconnect (D-06) is"
      % (fmt(A["f_v"]), fmt(A["f_int"])))
    p("     specified by its loop's floor, %s mOhm at 20 C, so a stiff source drives at most %s A (L4-E11 6; the construction %s A): MEETS, CONDITIONAL"
      % (fmt(F["loop_floor"]), fmt(F["ipf_spec"]), fmt(F["ipf_constr"])))
    p("     on the four-wire acceptance (E11-11)")
    p("   VBUS20 shorted: the front end holds the output at %s A at 9 V (R12) and %s A above %s V (R11 8 mOhm); VIN_RAW then carries at most %s A;"
      % (fmt(F["fe_out_9v"]), fmt(F["r11_8"][2]), fmt(F["avg_from"]), fmt(round(D["vin_fault"], 3))))
    p("     the vehicle entry's breaker opens on overcurrent (%s to %s A) after %s to %s ms, or on its filtered short-circuit sense (%s to %s A), and"
      % (fmt(F["e_oc"][0]), fmt(F["e_oc"][2]), fmt(F["e_oc_ms"][0]), fmt(F["e_oc_ms"][2]), fmt(F["e_sc"][0]), fmt(F["e_sc"][2])))
    p("     retries every %s s (the drawn LM5069 limited at %s to %s A for %s to %s ms); the panel's stage regulates at %s A at most and its backstop trips"
      % (fmt(F["e_retry_s"]), fmt(F["entry_lim"][0]), fmt(F["entry_lim"][1]), fmt(F["timer_ms"][0]), fmt(F["timer_ms"][2]), fmt(F["reg"][1])))
    p("     at %s A at most (SWEN, inside %s ms); the restart guard cycles the front end" % (fmt(F["bs_trip"][1]), fmt(F["bs_allow_ms"])))
    p("   VBAT shorted: the pack's SCD (%s A in 0.2 ms), OCD2, the 25 A blades and F2 against %s to %s A prospective; U3 at its input limit"
      % (fmt(F["scd"]), fmt(F["pp_fault"][0]), fmt(F["pp_fault"][1])))
    po = D["pack_open"]
    p("   the pack's charge FET opening mid-charge (a designed event, REQ-046): VBAT is held at ChargeVoltage (%s V at most), BATOVP stops switching"
      % fmt(F["chg_v_max"]))
    p("     at %s V, SYSOVP at %s V; L2's energy at the stop, %s mJ (peak %s A, L +20 %%), into VBAT's %d capacitors (%s uF nominal, %s uF kept at %s)"
      % (fmt(F["batovp"]), fmt(F["sysovp"][2]), fmt(round(po["e_mj"], 4)), fmt(round(po["i_pk"], 3)), po["n"], fmt(round(po["c_nom_uf"], 2)), fmt(round(po["c_eff_uf"], 2)), fmt(BIAS_KEEP)))
    p("     ends at %s V from the SYSOVP maximum, under the TPS2596's %s V; %s uF would do (%s of the nominal)"
      % (fmt(round(po["v_end"], 3)), fmt(F["tps2596_abs"]), fmt(round(po["c_need_uf"], 2)), fmt(round(po["keep_need"], 4))))
    p("   U2 failed (Q2 short or FB open) and U3 lost, a single fault: s120 section 11 and S-111 carry it with its options; this record claims no")
    p("     exemption for it (ASM-001 is the LoRa and cellular exception; R-48's decision stays an engineering one, open) and the")
    p("     options (an SMCJ22A on VBUS20: VR %s V over the %s V band; an independent over-voltage trip)" % (fmt(F["SMCJ22A"]["vr"]), fmt(F["vbus_band"][1])))
    p("   PoE monitor (HF-F02): U17's inputs at %s V against the INA226's %s V absolute: NOT MET as drawn; on R227, 5 mOhm in the stage's input"
      % (fmt(poe_v(F)), fmt(F["ina_abs"])))
    p("     (part A): %s A at a %s V stack, %s mV; %s A at the stage's fault bound, %s mV, against %s mV full scale; common mode at most %s V"
      % (fmt(round(D["poe_in"], 3)), fmt(D["vbat_low"]), fmt(round(A["u17_mv_norm"], 2)), fmt(round(A["u17_fault_a"], 2)), fmt(round(A["u17_mv_fault"], 2)), fmt(F["ina_fs_mv"]),
         fmt(round(max(F["sysovp"][2], D["pack_open"]["v_end"]), 3))))
    p("   the solar entry (L4-E7R): CS101 keeps the input at %s V under D4's %s V standoff; the capability scenario holds TRK_VS at %s V and PV_P at %s V;"
      % (fmt(F["cs101_pv"]), fmt(F["SMCJ28A"]["vr"]), fmt(F["trk_vs_max"]), fmt(F["pv_p_max"])))
    p("     a reversed panel conducts through D4 (DECISION-31 E-N1); the LT8705A's single faults are layer 8's list (a shorted INB filter capacitor")
    p("     defeats the backstop); under CS101 the filtered ripple, %s A, stays under the %s A margin (D-01, resolved in design, CONDITIONAL on the loop's"
      % (fmt(F["m2_ripple"]), fmt(F["m2_margin"])))
    p("     typical rows)")
    p("   the vehicle entry under CS101 (M2) at REQ-015's 36 V: %s V against the drawn OVLO minimum %s V (NOT MET as drawn), the selected OV minimum %s V:"
      % (fmt(round(A["cs101_top"], 2)), fmt(F["ovlo"][0]), fmt(F["e_ov_off"][0])))
    p("     MEETS (the alternative's %s V likewise)" % fmt(round(F["ovlo_sel"][0], 2)))
    p("   a hot short behind the selected entry: the breaker's short-circuit trip; at the start every fault inside Q7's derated chart; in service the")
    p("     peak OPEN on the loop's inductance (E11-20); F1's I2t at most %s A2s, %s %% of its typical melting I2t (section 12a)"
      % (fmt(round(E["i2t_max"], 4)), fmt(round(E["i2t_pct"], 2))))
    p("")
    p("8. THE ENDURANCE STATEMENT (A1 selected; A2 a proposal; DR-01)")
    a1b, a2b, sh = F["a1_bat"], F["a2_bat"], F["short"]
    p("   battery only: A1 %s Wh usable at +20 C, %s Wh at -10 C: %s h and %s h (short of 48 h by %s h, of 72 h by %s h); A2 %s h and %s h"
      % (fmt(a1b[0]), fmt(a1b[1]), fmt(a1b[2]), fmt(a1b[3]), fmt(sh[0]), fmt(sh[2]), fmt(a2b[2]), fmt(a2b[3])))
    c1, c2 = F["a1_cand"], F["a2_cand"]
    p("   solar-assisted on the panel at its typical rows (PANEL-ACC's unit, none measured; L4-E7's settings, %s Wh a day): A1 first interruption"
      % fmt(c1[0]))
    p("     h %d / %d (06 / 18 UTC starts); unserved %s / %s Wh at 48 h, %s / %s Wh at 72 h; least storage to add +%s / +%s Wh"
      % (int(c1[1]), int(c1[2]), *[fmt(x) for x in c1[3:9]]))
    p("     A2: h %d / %d; unserved %s / %s and %s / %s Wh; +%s / +%s Wh; steady load carried A1 %s W, A2 %s / %s W (48 / 72 h)"
      % (int(c2[1]), int(c2[2]), *[fmt(x) for x in c2[3:9]], fmt(F["steady"][2]), fmt(F["steady"][0]), fmt(F["steady"][1])))
    s1, s2 = F["a1_scr"], F["a2_scr"]
    p("   the 100 W screening stimulus (a conditional comparison): A1 h %d / %d, unserved %s / %s and %s / %s Wh, +%s / +%s Wh; A2 h %d / %d, +%s / +%s Wh"
      % (int(s1[0]), int(s1[1]), fmt(s1[2]), fmt(s1[3]), fmt(s1[4]), fmt(s1[5]), fmt(F["a1_scr_add"][0]), fmt(F["a1_scr_add"][1]), int(s2[0]), int(s2[1]), fmt(F["a2_scr_add"][0]), fmt(F["a2_scr_add"][1])))
    p("   what moves these: H3 gives up %s to %s Wh a day on the candidate's trace; the ballasts at most %s W at the bound's worst corner; C-8"
      % (fmt(F["h3_cand_given"][0]), fmt(F["h3_cand_given"][1]), fmt(F["ballast_w"])))
    dd = F["a1_cand"][0] - F["e7r_day"][1]
    p("   the selected solar control (L4-E7R): the day's energy %s / %s / %s Wh on SC-37 (lower / nominal / upper hold corner) and %s Wh on the"
      % (*[fmt(x) for x in F["e7r_day"]], fmt(F["e7r_bright"])))
    p("     bright day; the solar rows above are at L4-E7's %s Wh nominal and the replay is not re-run here: at the nominal hold the unserved energy"
      % fmt(F["a1_cand"][0]))
    p("     grows by at most %s Wh a day, %s Wh at 48 h and %s Wh at 72 h (INFERRED: harvest lost can at most add to it); the sense bank's %s Wh a day"
      % (fmt(round(dd, 1)), fmt(round(2 * dd, 1)), fmt(round(3 * dd, 1)), fmt(F["bank_wh"][0])))
    p("     is carried beside it (L4-E7R prints it apart from the day's energy; if the day's figure already holds it, this counts it twice, the")
    p("     conservative side)")
    p("   L4-E8's ballasts in the budgets: at most %s W while U3 runs at the bound's worst corner, %s W at L4-E8's nominal illustration; a loss on"
      % (fmt(F["ballast_w"]), fmt(F["ballast_nom_w"])))
    p("     the charge path only (battery-only endurance does not carry it: U3 is idle), outside the DECLARED efficiencies (C-8), and dropped once a")
    p("     measured efficiency with the ballasts fitted includes it (R-51). Thermal: at most %s W more into the sealed case, %s K on the inside air"
      % (fmt(F["ballast_w"]), fmt(round(F["ballast_w"] / F["th1"], 2))))
    p("     at T-H1's %s W/K floor (INFERRED: the same conductance), on top of L4-E10's conditioned corner (%s / %s C; about %s W of the kit's heat at"
      % (fmt(F["th1"]), "%.2f" % F["corner_air"][0], "%.2f" % F["corner_air"][1], fmt(round(F["corner_heat"], 1))))
    p("     E3-O, which predates the ballasts); L4-E12 counts them once inside its own figures (below)")
    p("   THE THERMAL BUDGET (L4-E12, the update round): T-H1's binding line is %s W/K lid open with the fans, set by E5 under the hold: %s W of"
      % (fmt(F["gc"]), fmt(F["e5_hold_w"])))
    p("     heat plus the ballasts' %s W, %s W, over E5's %s K to the +70 C parts; E3-O with every radio on carries %s W (%s W plus %s W) over %s K,"
      % (fmt(F["ballast_w"]), fmt(round(F["e5_hold_wb"], 3)), fmt(F["e5_line"] - F["e5_amb"]), fmt(round(F["e3o_wb"], 3)), fmt(F["e3o_stage_w"]), fmt(F["ballast_w"]), fmt(F["e5_line"] - F["e3o_amb12"])))
    p("     %s W/K; with no hold %s W/K. At the line the mixed air is %s C in E3-O and %s C in E5, the ballasts %s K of it; the hold powers off board"
      % (fmt(F["g_e3o"]), fmt(F["g_a"]), "%.2f" % F["e3o_line"], "%.2f" % F["e5_line"], fmt(round(F["ballast_w"] / F["gc"], 3))))
    p("     D, the PA rail, the RockBLOCK, the LoRa module, both E72 and the Geiger module, idles the running module and holds the charge (L4-E12 4c),")
    p("     on a reference within +-%s K of the mixed air; it narrows U-02 to T-H1 and its conditions (section 9)" % "%s" % F["hold_ref"])
    p("   THE ENERGY BUDGET (the update round): the battery-only and solar figures above are unchanged by L4-E10 to L4-E12; the vehicle entry's loop")
    p("     costs %s W at a 9.00 V plug (%s A through %s mOhm hot), on the source's side; a dead pack's charge under R-b takes at most %s W, and only"
      % (fmt(round(E["loss_dcp"] + E["loss_vr"], 3)), fmt(F["e_svc"][1]), fmt(F["e_loop_mohm"][2]), fmt(F["rb_w"])))
    p("     from DPM's surplus; L4-E12's hold is a state at the margins (E5), not an endurance state")
    p("   the cell under L4-E10's recommendation (U-01, CONDITIONAL on the signed specification and the owner's approval; not taken here): usable")
    p("     %s Wh against the 35E's %s Wh (%s %% less), %s h against %s h battery-only at PS-IDLE-SPEC (L4-E10's own basis); D-06's about 145 Wh becomes"
      % (fmt(F["cell_usable"][1]), fmt(F["cell_usable"][0]), fmt(F["cell_less_pct"]), fmt(F["cell_hours"][1]), fmt(F["cell_hours"][0])))
    p("     about %s Wh nominal; every storage shortfall above grows by at most the usable energy lost, %s Wh (INFERRED)"
      % (fmt(F["cell_nom"][1]), fmt(round(F["cell_usable"][0] - F["cell_usable"][1], 1))))
    p("   the panel (U-03, L4-E13): the solar rows above are the rated unit's at L4-E7's first-round limit (%s Wh a day at the nominal hold);"
      % ("%.1f" % F["e13_day"][1]))
    p("     under L4-E7R's accepted regulation its nominal hold gives %s Wh (the L4-E7R lines above carry the difference); PANEL-ACC accepts"
      % ("%.1f" % F["e13_day_e7r"]))
    p("     any unit inside the window down to A-2's floor, whose day at the conditioned upper corner is %s Wh (the rated unit's %s Wh): the"
      % ("%.1f" % F["e13_day"][2], "%.1f" % F["e13_day"][0]))
    p("     unserved energy then grows; no figure here is a measured unit's (R-52)")
    p("   the objective of 48 to 72 h is unmet by A1 on every trace (DR-01); no mandatory function is reduced to narrow it")
    p("")
    p("9. THE CLOSURE GATE (a criterion reads PASS only on rows that read MEETS; ASSUMPTION, CONDITIONAL and PENDING rows cannot carry a PASS)")
    bad = gate_violations(GATE, st)
    for g in GATE:
        p("   %d. %s: %s; rows %s%s" % (g["n"], g["criterion"], g["verdict"], ", ".join("%s %s" % (r, st[r][1]) for r in g["rows"]) or "none (the registers)",
                                    "; choices " + ", ".join(g["choices"]) if g.get("choices") else ""))
        if g["constraint"]:
            p("      constraint: %s" % g["constraint"])
            p("      could it overturn the architecture: %s" % g["overturn"])
    if bad:
        refuse(4, "the gate's rule fails: %s" % bad)
    for cid, exp in round5_expect(F).items():
        c = [x for x in CHOICES if x["id"] == cid][0]
        whole = " ".join([c["question"], c["constraint"], evidence_text(c), c["supplier"], c["fallback"], c["overturns"]])
        for s in exp:
            if " ".join(s.split()) not in whole:
                refuse(4, "%s does not quote the round's figure: %r" % (cid, " ".join(s.split())))
    closed = all(g["verdict"] == "PASS" for g in GATE)
    p("   Layer 4's power architecture closes: %s" % ("YES" if closed else "NO, criteria %s are not PASS" % ", ".join(str(g["n"]) for g in GATE if g["verdict"] != "PASS")))
    opn = [d["id"] for d in DEFECTS if d["state"] == "OPEN"]
    adr = [d["id"] for d in DEFECTS if d["state"].startswith("ADDRESSED IN DRAFTS")]
    p("   MATERIAL POWER-PATH DEFECTS (criterion 2): %d, %d open; %d addressed in drafts (%s: a selected remedy, drafted, not applied)" % (len(DEFECTS), len(opn), len(adr), ", ".join(adr)))
    for d in DEFECTS:
        p("     %s %s [%s]; rows %s" % (d["id"], d["title"], d["state"], ", ".join("%s %s" % (r, st[r][1]) for r in d["rows"])))
        p("        the constraint: %s" % d["constraint"])
        p("        the options: %s; resolution: %s" % (d["options"], d["resolution"]))
    p("   (b) UNRESOLVED CHOICES THAT COULD OVERTURN THE ARCHITECTURE: %d (no owner or acceptance criterion closes one; each keeps every"
      % sum(1 for c in CHOICES if c["class"] == ARCH))
    p("       criterion that names it from PASS until its evidence lands); %s moved downstream (class printed with each)"
      % ", ".join(c["id"] for c in CHOICES if c["class"] != ARCH))
    for c in CHOICES:
        p("     %s %s [%s]; rows %s" % (c["id"], c["title"], c["class"], ", ".join("%s %s" % (r, st[r][1]) for r in c["rows"])))
        p("        the exact unresolved question: %s" % c["question"])
        p("        the present state: %s" % c["constraint"])
        for lab, x in zip(EVIDENCE_LABELS, c["evidence"]):
            p("        the evidence (%s): %s" % (lab, x))
        for k, lab in (("supplier", "who supplies it"), ("fallback", "the fallback"), ("overturns", "what it could overturn")):
            p("        %s: %s" % (lab, c[k]))
    p("   (a) DOWNSTREAM IMPLEMENTATION AND VERIFICATION TASKS: the register of section 10; an owner and an acceptance criterion close the")
    p("       ASSIGNMENT, not the item: each stays OWED, DRAFTED, MISSING DRAFT or PENDING until its acceptance is met on the built prototype")
    p("   (c) THE OWNER'S ITEMS (decisions and outside contacts only, kept apart from the engineering work; the session contacts no outside party)")
    for o in OWNER_ITEMS:
        p("     %s %s" % (o["id"], o["what"]))
        for key, label in o["docs"]:
            rel = PINS[key][0]
            txt = _C_TEXT[key]
            mark = OWNER_MARK.get(key, r"(?i)draft for the owner to send")
            if not re.search(mark, txt):
                refuse(4, "%s does not read as %s" % (rel, "a draft for the owner" if key not in OWNER_MARK else "the owner's item"))
            src = "in the tree" if where[key][0] == "tree" else "at %s (%s)" % (FROM_COMMIT[key], COMMIT_LABEL[FROM_COMMIT[key]].split(",")[0])
            p("        %s: %s, %s, sha256 %s" % (label, rel, src, where[key][1][:16]))
    p("     %s" % OWNER_NOT_DRAFTED)
    p("")
    p("10. THE REGISTERS (this folder's DOWNSTREAM-REGISTER.md and LAYER5-HANDOVER.md, read and checked)")
    reg_text = open(os.path.join(HERE, "DOWNSTREAM-REGISTER.md"), encoding="utf-8").read() if os.path.exists(os.path.join(HERE, "DOWNSTREAM-REGISTER.md")) else ""
    reg = md_table(reg_text, "| ID | Kind |")
    by_owner, by_kind = {}, {}
    for r in reg:
        if len(r) < 8 or r[4] not in OWNERS or not r[5]:
            refuse(4, "register row %s has no named owner or acceptance" % (r[0] if r else "?"))
        by_owner[r[4]] = by_owner.get(r[4], 0) + 1
        by_kind[r[1]] = by_kind.get(r[1], 0) + 1
    p("   register: %d items; by owner: %s" % (len(reg), "; ".join("%s %d" % (o, by_owner[o]) for o in OWNERS if o in by_owner)))
    p("     by kind: %s" % "; ".join("%s %d" % (k, by_kind[k]) for k in sorted(by_kind)))
    by_state = {}
    for r in reg:
        if r[1] == "IMPLEMENTATION":
            by_state[r[6]] = by_state.get(r[6], 0) + 1
    p("     implementation changes by state: %s" % "; ".join("%s %d" % (k, by_state[k]) for k in sorted(by_state)))
    ids = {r[0] for r in reg}
    for eid, kind, owner in F["e11_items"]:
        if eid in E11_ANSWERED_HERE:
            continue
        if not any(re.search(r"\b%s\b" % eid, r[3]) for r in reg):
            refuse(4, "L4-E11's %s is not in the register's From column" % eid)
    fr = [r for r in reg if r[0] == "R-150"]
    k, what, frm, own, acc = F["r5"]["fanrow"]
    if not fr or fr[0][1] != k or what not in fr[0][2] or frm not in fr[0][3] or not own.startswith(fr[0][4]) or acc.lower() not in fr[0][5].lower():
        refuse(4, "L4-E12's drafted fan row is not the register's R-150")
    for nm, mp in (("L4-E10", E10_MAP), ("L4-E12", E12_MAP)):
        for owner, refs in mp.items():
            for x in refs:
                if x.startswith("R-") and x not in ids:
                    refuse(4, "%s's %s maps to %s, not in the register" % (nm, owner, x))
                if x.startswith("OW-") and x not in {o["id"] for o in OWNER_ITEMS}:
                    refuse(4, "%s's %s maps to %s, not an owner item" % (nm, owner, x))
    p("     the accepted records' items, deduplicated: L4-E11's E11-01 to E11-35 each named in a row's From column (E11-19 answered here, out 12);")
    p("       L4-E10 by owner: %s" % "; ".join("%s -> %s" % (k, ", ".join(v)) for k, v in E10_MAP.items()))
    p("       L4-E12 by owner: %s" % "; ".join("%s -> %s" % (k, ", ".join(v)) for k, v in E12_MAP.items()))
    h_text = open(os.path.join(HERE, "LAYER5-HANDOVER.md"), encoding="utf-8").read() if os.path.exists(os.path.join(HERE, "LAYER5-HANDOVER.md")) else ""
    ho = md_table(h_text, "| ID | Target |")
    for r in ho:
        for rid in re.findall(r"IF-\d\d", r[3] if len(r) > 3 else ""):
            if rid not in st:
                refuse(4, "handover %s names an unknown row %s" % (r[0], rid))
    p("   Layer 5 handover: %d interface entries drafted (pcb_interfaces.yaml and HW-FW-CONTRACT.md, drafts only)" % len(ho))
    p("")
    for ln in partA_lines(F, D, A):
        p(ln)
    p("")
    for ln in rejudge_lines(F, D, A, E):
        p(ln)
    p("")
    for ln in round3_lines(F, D, A, E, st):
        p(ln)
    p("")
    for ln in round5_lines(F, st, reg):
        p(ln)
    p("")
    N, Ed, Cd, NP = cons_diagram(F, st)
    svg = cons_svg(N, Ed, Cd, NP, st)
    svg_path = os.path.join(HERE, SVG_NAME)
    if "--write-svg" in sys.argv:
        open(svg_path, "w", encoding="utf-8").write(svg)
    if not os.path.exists(svg_path) or open(svg_path, encoding="utf-8").read() != svg:
        refuse(4, "the committed %s is not the script's (run it with --write-svg)" % SVG_NAME)
    for ln in cons_diagram_lines(N, Ed, Cd, NP, st, hashlib.sha256(svg.encode("utf-8")).hexdigest()):
        p(ln)
    p("")
    recon_check(_C_TEXT)
    for ln in cons_budget_lines(F, st):
        p(ln)
    p("")
    for ln in cons_change_lines(reg):
        p(ln)
    p("")
    for ln in cons_behaviour_lines(F, D, st):
        p(ln)
    p("")
    for ln in cons_handover_lines(F, reg):
        p(ln)
    p("")
    for ln in cons_exit_lines(F):
        p(ln)
    p("")
    p("21. IN SHORT (the page's summary, generated)")
    for b in cons_in_short(F, D, st, reg):
        p("   - %s" % b.replace("**", ""))
    p("")
    for ln in cons_results_lines(F):
        p(ln)
    p("")
    for ln in cons_surge_lines(F):
        p(ln)
    p("")
    for ln in cons_amend_lines(F):
        p(ln)
    p("")
    for ln in cons_fix_lines(F):
        p(ln)
    p("")
    p("END. Desk arithmetic on read figures; nothing is measured.")
    return "\n".join(out) + "\n", F, D, R, st


# ======================================================================================================== THE CONSOLIDATION
# The owner's instruction of 2 October 2026 (11:25 and his corrections of 12:00): one connected, implementable design. Every
# table below is built from figures this script read above; the page's tables are these, and test_l4e9.py holds them equal.
STATUS = "known defects addressed in drafts; feasibility conditions remain open"
SVG_NAME = "L4-POWER-DIAGRAM.svg"


def cons_diagram(F, st):
    """The one connected figure: nodes (blocks with their settings and limits), power edges (each with its IF row), the
    control edges (who acts on which element) and the path the figure notes but does not carry power on."""
    hs = F["hold"]
    N = [
        ("SRC_PV", 0, 70, "Panel (REQ-016)", ["Voc at most 25 V at -20 C", "at most 100 W into the stage", "PANEL-ACC unit: none accepted (U-03)"]),
        ("SRC_DC", 0, 380, "Vehicle or shore DC (REQ-015)", ["9 to 36 V at the plug, -36 V reversed", "D38999 size 12, loop >= %s mOhm" % fmt(F["loop_floor"]),
                                                             "XT60-class J_DCIN (drafted, R-131)"]),
        ("SRC_USB", 0, 620, "USB-C input: none (D-12)", ["the USB-C port is an outlet only"]),
        ("SOL_IN", 1, 70, "Solar entry, board E", ["J_SOLAR VH %s A; F2 %s" % (fmt(F["vh_16"]), F["e_f2"].split(" (")[0]), "D11 SMCJ40CA across the port",
                                                   "guard U21/Q12 off %s to %s V" % (fmt(F["sv"]["rm"]["rise"][0]), fmt(F["sv"]["rm"]["rise"][1])),
                                                   "Q13 in the return (drafted)", "D4 SMCJ30A; the 50 V bulk", "ahead of the sense bank", "(L4-E7R, L4-E7: drafted)", "R59 15 mOhm on TRK_VIN"]),
        ("DC_IN", 1, 380, "Vehicle entry, board E", ["F1 0997010.WXN 58 V DC (drafted)", "D10 SMCJ40CA, D1 SMCJ40A",
                                                     "Q1 CSD19532Q5B 100 V (drafted)", "U3/Q1 LM74700-Q1 ideal diode"]),
        ("U5", 2, 70, "U5 LT8705AI stage", ["hold %s / %s / %s V" % ("%.3f" % hs[0], "%.3f" % hs[1], "%.3f" % hs[2]),
                                            "regulation RIMON_IN %s" % F["rimon"], "%s A nominal, %s A highest" % (fmt(F["reg"][0]), fmt(F["reg"][1])),
                                            "backstop on SWEN %s to %s A" % (fmt(F["bs_trip"][0]), fmt(F["bs_trip"][1])),
                                            "TRK_OUT ceiling %s to %s V" % (fmt(F["trk_ceiling"][0]), fmt(F["trk_ceiling"][2])), "U4/Q2 ideal diode out"]),
        ("ENTRY", 2, 380, "Entry breaker (L4-E11, drafted)", ["U6 TPS48110-Q1, Q7 CSD19536KTT",
                                                              "UVLO on %s to %s V" % (fmt(F["e_uv_on"][0]), fmt(F["e_uv_on"][2])),
                                                              "OV off %s to %s V" % (fmt(F["e_ov_off"][0]), fmt(F["e_ov_off"][2])),
                                                              "%s to %s A after %s to %s ms" % (fmt(F["e_oc"][0]), fmt(F["e_oc"][2]), fmt(F["e_oc_ms"][0]), fmt(F["e_oc_ms"][2])),
                                                              "short %s to %s A, retry %s s" % (fmt(F["e_sc"][0]), fmt(F["e_sc"][2]), fmt(F["e_retry_s"])),
                                                              "R19 4.5 mOhm, L2 SRF1260-1R0Y"]),
        ("VINRAW", 3, 240, "VIN_RAW (board E to A)", ["D2 SMCJ40A clamp", "four Mill-Max %s A dock pins" % fmt(F["millmax_a"]),
                                                      "declared %.2f A" % F["vin_raw_a"]["typ"], "basis %s V maximum" % fmt(F["e_basis_v"])]),
        ("FE", 4, 70, "U2 LM5176 front end, board A", ["R11 8 mOhm, R12 12 mOhm (drafted)", "U34 guard R14 76.8k (drafted)",
                                                       "VBUS20 %s to %s V" % (fmt(F["vbus_band"][0]), fmt(F["vbus_band"][1])),
                                                       "efficiency 0.93 declared (C-8)"]),
        ("BANK", 4, 245, "VBUS20 bank (L4-E8, drafted)", ["six EEHZK1V331P, 45 mOhm each", "every can at most %s A" % fmt(F["can8"][0]),
                                                           "rule %s A; Cc2 3.3 nF" % fmt(F["can8"][1])]),
        ("CHG", 4, 395, "U3 charger, board A", ["(B1) BQ25730, drafted (drawn: BQ25731)", "BATDRV on pin 21 drives Q39, Q40",
                                                "R16 10 mOhm; IIN_HOST %.2f A" % F["iin_host"],
                                                "H3 line: flat %s A, HIZ < %s V" % (fmt(F["knee"][0]), fmt(F["knee_hiz"])),
                                                "ChargeCurrent at most %.1f A" % F["chg_set"], "BATOVP %s V; the 4S strap fixed" % fmt(F["batovp"])]),
        ("VBAT", 5, 395, "VBAT = VSYS node", ["%s to %s V (B1)" % (fmt(F["fx"]["vsys_rng"][0]), fmt(F["fx"]["vsys_rng"][1])), "D1 SMCJ18A clamp",
                                              "no pack: at least %s V;" % fmt(F["fx"]["pw"][1]), "inhibited: piecewise (15d)",
                                              "Q39, Q40 BUK6Y10-30P", "to CH_BATQ (drafted;", "%s W at the profile)" % fmt(F["fx"]["pair_idle"][1])]),
        ("PACK", 6, 60, "Pack, board P (D-06 4S3P; U-01)", ["Samsung 35E x 12 (ruled cell)", "BQ4050 gauge and its FETs",
                                                            "BQ7720700 -> F2 SCF9550", "F1 %s A; OCD1 %s A for %s s" % (fmt(F["a_f1"]), fmt(F["ocd1"][0]), fmt(F["ocd1"][1])),
                                                            "usable %s Wh at +20 C" % fmt(F["a1_bat"][0])]),
        ("LOADS", 6, 225, "Load converters", ["PS-IDLE-SPEC %s W at the pack" % fmt(F["idle"][1]), "slot, device, logic, monitor",
                                              "heater U22/U33 12.0 V 7.5 W", "eFuses TPS2596 %s V" % fmt(F["tps2596_abs"])]),
        ("USBC", 6, 370, "USB-C outlet U19 + U18", ["5 / 9 / 15 V at %s A" % fmt(F["pdo_a"]), "OCP %s to %s A" % (fmt(F["trip"][0]), fmt(F["trip"][1])),
                                                    "tablet budget %s W cap (proposal)" % fmt(F["cb"]["tab_cap"])]),
        ("POE", 6, 500, "PoE stage", ["R227 5 mOhm, U17 on it (drafted)", "U16 boost %s V at %s A" % (fmt(F["poe"]["volts"]), fmt(F["poe"]["peak"]))]),
        ("PA", 6, 600, "PA and HF rails", ["U13 %s V; key-down at most 60 s" % fmt(F["pa"]["volts"]), "U15 %s V to the QMX" % fmt(F["hf"]["volts"]),
                                           "outlets off while the PA keys"]),
        ("CTL_PANEL", 1, 690, "Panel controller C:U3 RP2040", ["the kit I2C: the charger,", "the expanders, the INA226s", "and the key-down rules"]),
        ("CTL_SENS", 3, 690, "Sensor controller E:U10 RP2040", ["the gauge's SMBus, the mixer", "fans, VIN_MON; on VSYS_E (B1)"]),
        ("CTL_HW", 5, 690, "Hardware, no firmware", ["comparators, the gauge, the", "breaker, the knee, OUTLET_OK"]),
    ]
    E = [
        ("P01", "SRC_PV", "SOL_IN", ["IF-01"], "J_SOLAR, D11, F2, the guard (U21, Q12, Q13), D4, the bulk, the sense bank"),
        ("P02", "SOL_IN", "U5", ["IF-02"], "PV_P to TRK_VIN, U5's input"),
        ("P03", "U5", "VINRAW", ["IF-03"], "TRK_OUT through U4/Q2"),
        ("P04", "SRC_DC", "DC_IN", ["IF-04"], "the plug, the interconnect, J_DCIN, F1, Q1"),
        ("P05", "DC_IN", "ENTRY", ["IF-05"], "DC_P into U6/Q7"),
        ("P06", "ENTRY", "VINRAW", ["IF-05"], "R19, L2 to VIN_RAW"),
        ("P07", "VINRAW", "FE", ["IF-06", "IF-07"], "the dock's pins, U2's input"),
        ("P08", "FE", "BANK", ["IF-07"], "VBUS20"),
        ("P09", "BANK", "CHG", ["IF-08", "IF-09"], "VBUS20 through R16 into U3"),
        ("P10", "CHG", "VBAT", ["IF-09"], "U3's output, VSYS"),
        ("P11", "VBAT", "PACK", ["IF-10"], "(B1) Q39 and Q40 to CH_BATQ, then R17, A F1, the pack pins, board P"),
        ("P12", "VBAT", "LOADS", ["IF-11"], "the converters' inputs"),
        ("P13", "VBAT", "USBC", ["IF-12"], "U19's input, R138"),
        ("P14", "VBAT", "POE", ["IF-13"], "R227 to POE_VIN"),
        ("P15", "VBAT", "PA", ["IF-14"], "U13's and U15's inputs"),
        ("P16", "VBAT", "CTL_SENS", ["IF-06", "IF-11"], "(B1) VSYS over the dock's pin 1 to board E's VSYS_E: U12, the controller, the mixer fans (drafted, L4-E11 15a)"),
    ]
    C = [
        ("C01", "CTL_PANEL", "CHG", "FW-A01 to A03, A16, A17: RSNS_RAC, IIN_HOST %.2f A, ChargeCurrent at most %.1f A, the charger's 175 s watchdog; CHG_INHIBIT (FW-A14) and rules R-a to R-d (R-126); under (B1) EN_OOA 0 at boot, ChargeCurrent 0 A at POR, R-b' (R-158)" % (F["iin_host"], F["chg_set"]), "firmware"),
        ("C02", "CTL_PANEL", "LOADS", "the expanders (FW-A08): SLOT_EN, DEV_EN, HEAT_EN; the margin hold (R-138, R-139); MAIN and PI_KILL (FW-A10 to A12)", "firmware"),
        ("C03", "CTL_PANEL", "USBC", "PD_SW_EN AND OUTLET_OK (FW-A06); the tablet's window (a proposal)", "firmware and hardware"),
        ("C04", "CTL_PANEL", "POE", "POE_SW_EN AND OUTLET_OK (FW-A06); U17 read on R227 (FW-A09, R-27)", "firmware and hardware"),
        ("C05", "CTL_PANEL", "PA", "the key-down rules K1 to K5 and C4 (FW-A05, D-11): at most 60 s, the rest floors %s and %s V" % (fmt(F["d11_floor"]), fmt(F["pa_floor"])), "firmware"),
        ("C06", "CTL_SENS", "PACK", "the gauge's SMBus (FW-E01): its ranges relayed to the charger by the host; SHUTDOWN for storage (FW-E09); HWD 10 s", "firmware"),
        ("C07", "CTL_SENS", "LOADS", "the mixer fans (FW-E07), the Geiger supply (FW-E08), VIN_MON for FW-A16 (FW-E04)", "firmware"),
        ("C08", "CTL_HW", "U5", "the hold (FBIN divider R8, R9 at 0.1 %%), the regulation (IMON_IN, RIMON_IN %s), the backstop comparators on SWEN, off below %s V of TRK_LDO33" % (F["rimon"], fmt(F["swen_v"])), "hardware"),
        ("C09", "CTL_HW", "ENTRY", "the TPS48110-Q1's own UVLO, OV, breaker and short-circuit trip; the LM74700-Q1 blocks reverse current", "hardware"),
        ("C10", "CTL_HW", "FE", "U34's restart guard (R14 76.8k: %s to %s V); R11's average and R12's cycle-by-cycle limits" % (fmt(F["guard_sel"][0]), fmt(F["guard_sel"][2])), "hardware"),
        ("C11", "CTL_HW", "CHG", "the H3 line on ILIM_HIZ (the corrected knee), the charger's VINDPM, ACOV, BATOVP and SYSOVP; under (B1) BATDRV drives Q39 and Q40 (LDO mode below VSYS_MIN)", "hardware"),
        ("C12", "CTL_HW", "PACK", "the BQ4050's protections on its FETs (COV, CUV, OCC %s A, OCD, SCD %s A, UTC, OTC); the BQ7720700 drives F2" % (fmt(F["occ"]), fmt(F["scd"])), "hardware (the gauge's own firmware)"),
        ("C13", "CTL_HW", "USBC", "OUTLET_OK = NOT (TR_APRS AND PA_EN), A:U30, drops both outlets while the PA keys; U18's OCP", "hardware"),
    ]
    NOPOWER = [("N01", "VINRAW", "DC_IN", "the tracker back-feeds DC_P through Q7's body diode (no power is delivered this way)")]
    ids = {n[0] for n in N}
    for e in E + [(c[0], c[1], c[2]) for c in C] + [(x[0], x[1], x[2]) for x in NOPOWER]:
        if e[1] not in ids or e[2] not in ids:
            refuse(4, "diagram edge %s names an unknown block" % e[0])
    covered = sorted({r for e in E for r in e[3]})
    if covered != sorted(st):
        refuse(4, "the diagram's power edges cover %s, not every interface row %s" % (covered, sorted(st)))
    return N, E, C, NOPOWER


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def cons_svg(N, E, C, NOPOWER, st):
    """The diagram as an SVG, generated here and committed beside the page (deterministic text). Power edges are solid and
    carry their interface rows; the control edges are the blue tags on the blocks a controller acts on, listed on each
    controller's block (the page's control table gives each in full)."""
    CW, X0, BW, LH, WIDTH, HEIGHT = 276, 20, 206, 13, 1900, 840
    box = {}
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="DejaVu Sans, Arial, sans-serif">'
           % (WIDTH, HEIGHT, WIDTH, HEIGHT),
           '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (WIDTH, HEIGHT),
           '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           '<path d="M0,0 L10,5 L0,10 z" fill="#1f2937"/></marker></defs>',
           '<text x="20" y="24" font-size="15" font-weight="bold" fill="#111827">L4-E9: the connected power design (A1 under D-06). '
           'Solid lines carry power, each labelled with its interface row; blue tags C01 to C13 are the controls (the page\'s table).</text>',
           '<text x="20" y="42" font-size="12" fill="#b91c1c">Status: %s.</text>' % _esc(STATUS)]
    ctl = {}
    for cid, a, b, _w, _k in C:
        ctl.setdefault(b, []).append(cid)
        ctl.setdefault(a + "#acts", []).append(cid)
    for nid, col, y, title, lines in N:
        x = X0 + col * CW
        extra = []
        if nid.startswith("CTL"):
            ids = ctl.get(nid + "#acts", [])
            extra = ["acts through " + ", ".join(ids[i:i + 4]) if i == 0 else "  " + ", ".join(ids[i:i + 4]) for i in range(0, len(ids), 4)]
        lines = list(lines) + extra
        h = 24 + LH * len(lines) + 8
        box[nid] = (x, y + 10, BW, h)
        fill = "#eef2ff" if nid.startswith("CTL") else ("#f3f4f6" if nid == "SRC_USB" else "#ffffff")
        out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="%s" stroke="#374151" stroke-width="1.2"/>' % (x, y + 10, BW, h, fill))
        out.append('<text x="%d" y="%d" font-size="12" font-weight="bold" fill="#111827">%s</text>' % (x + 7, y + 28, _esc(title)))
        for i, ln in enumerate(lines):
            out.append('<text x="%d" y="%d" font-size="10.5" fill="#1f2937">%s</text>' % (x + 7, y + 44 + i * LH, _esc(ln)))
        tags = ctl.get(nid, [])
        if tags:
            t = " ".join(tags)
            tw = int(6.2 * len(t)) + 8
            out.append('<rect x="%d" y="%d" width="%d" height="13" rx="3" fill="#2563eb"/>' % (x + BW - tw, y - 4, tw))
            out.append('<text x="%d" y="%d" font-size="9.5" font-weight="bold" fill="#ffffff">%s</text>' % (x + BW - tw + 4, y + 6, t))

    def label(x, y, text):
        w = int(6.0 * len(text)) + 6
        out.append('<rect x="%d" y="%d" width="%d" height="13" fill="#ffffff" stroke="#b91c1c" stroke-width="0.6"/>' % (x - w // 2, y - 10, w))
        out.append('<text x="%d" y="%d" font-size="10" font-weight="bold" fill="#b91c1c" text-anchor="middle">%s</text>' % (x, y, _esc(text)))

    def rows_text(rows):
        return "/".join([rows[0]] + [r[3:] for r in rows[1:]])
    vertical = {"P08", "P09"}
    into = {"P03": 22, "P06": -22}
    bus_x = None
    for eid, a, b, rows, _via in E:
        xa, ya, wa, ha = box[a]
        xb, yb, wb, hb = box[b]
        if eid in vertical:
            x = xa + wa // 2
            out.append('<path d="M%d,%d L%d,%d" fill="none" stroke="#1f2937" stroke-width="1.6" marker-end="url(#a)"/>' % (x, ya + ha, x, yb))
            label(x + 40, (ya + ha + yb) // 2 + 4, rows_text(rows))
            continue
        y1 = ya + ha // 2
        if eid == "P16":        # (B1)'s feed of board E's VSYS_E: down from VBAT's box, over column 4, into the sensor controller
            xs = xa + 20
            yr = yb - 20
            xc = xb + wb // 2
            out.append('<path d="M%d,%d L%d,%d L%d,%d L%d,%d" fill="none" stroke="#1f2937" stroke-width="1.6" marker-end="url(#a)"/>'
                       % (xs, ya + ha, xs, yr, xc, yr, xc, yb))
            label((xs + xc) // 2, yr - 4, rows_text(rows) + " (B1) VSYS_E")
            continue
        if a == "VBAT":
            bus_x = xa + wa + 16
            y2 = yb + hb // 2
            mk = ' marker-start="url(#a)"' if eid == "P11" else ""
            out.append('<path d="M%d,%d L%d,%d" fill="none" stroke="#1f2937" stroke-width="1.6" marker-end="url(#a)"%s/>' % (bus_x, y2, xb, y2, mk))
            label((bus_x + xb) // 2, y2 - 4, rows_text(rows))
            continue
        off = into.get(eid, 0)
        y2 = yb + (hb // 2 if off == 0 else (off if off > 0 else hb + off))
        x1, x2 = xa + wa, xb
        xm = (x1 + x2) // 2
        if abs(y2 - y1) < 3:
            out.append('<path d="M%d,%d L%d,%d" fill="none" stroke="#1f2937" stroke-width="1.6" marker-end="url(#a)"/>' % (x1, y1, x2, y1))
            label(xm, y1 - 5, rows_text(rows))
        else:
            out.append('<path d="M%d,%d L%d,%d L%d,%d L%d,%d" fill="none" stroke="#1f2937" stroke-width="1.6" marker-end="url(#a)"/>'
                       % (x1, y1, xm, y1, xm, y2, x2, y2))
            label(xm, (y1 + y2) // 2 + 4, rows_text(rows))
    if bus_x is not None:
        ys = [box[b][1] + box[b][3] // 2 for _e, a, b, _r, _v in E if a == "VBAT" and _e != "P16"]
        xv, yv, wv, hv = box["VBAT"]
        yvm = yv + hv // 2
        out.append('<path d="M%d,%d L%d,%d" fill="none" stroke="#1f2937" stroke-width="1.6"/>' % (xv + wv, yvm, bus_x, yvm))
        out.append('<path d="M%d,%d L%d,%d" fill="none" stroke="#1f2937" stroke-width="2.2"/>' % (bus_x, min(ys), bus_x, max(ys)))
    for nid, a, b, _what in NOPOWER:
        xa, ya, wa, ha = box[a]
        xn, yn, wn, hn = box["ENTRY"]
        yl = ya + ha + 18
        xe = xn + wn - 40
        out.append('<path d="M%d,%d L%d,%d L%d,%d L%d,%d" fill="none" stroke="#9ca3af" stroke-width="1.2" stroke-dasharray="2,3"/>'
                   % (xa + wa // 2, ya + ha, xa + wa // 2, yl, xe, yl, xe, yn - 6))
        out.append('<text x="%d" y="%d" font-size="9.5" fill="#6b7280">%s: back-feed into DC_P through Q7\'s body diode (no power delivered)</text>'
                   % (X0 + CW + 10, yl - 4, nid))
    out.append('<text x="20" y="%d" font-size="10" fill="#374151">Every figure is printed by l4e9_power_path.py (out 15) from its pinned inputs; '
               'prototype design: nothing bought, built, powered or measured; the drafted changes are not applied.</text>' % (HEIGHT - 12))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def cons_diagram_lines(N, E, C, NOPOWER, st, svg_sha):
    L = []
    p = L.append
    p("15. THE CONNECTED DESIGN: ONE DIAGRAM (the consolidation; %s, sha256 %s, generated here and committed beside the page)" % (SVG_NAME, svg_sha[:16]))
    p("   blocks (settings and limits as read above):")
    for nid, _c, _y, title, lines in N:
        p("     %-9s %s: %s" % (nid, title, "; ".join(lines)))
    p("   power edges (each with its interface row and the row's status):")
    for eid, a, b, rows, via in E:
        p("     %s %s -> %s (%s): %s" % (eid, a, b, via, ", ".join("%s %s" % (r, st[r][1]) for r in rows)))
    covered = sorted({r for e in E for r in e[3]})
    p("     every interface row is on an edge: %s (%s)" % ("yes" if covered == sorted(st) else "NO", ", ".join(covered)))
    p("   control edges (who acts on which block):")
    for cid, a, b, what, kind in C:
        p("     %s %s -> %s [%s]: %s" % (cid, a, b, kind, what))
    for nid, a, b, what in NOPOWER:
        p("     %s %s -> %s: %s" % (nid, a, b, what))
    return L


def _rt(e_wh, p_w, extra_w=0.0, window_h=0.0):
    """Battery-only runtime (h) of a store of e_wh at p_w, with an extra extra_w for the first window_h hours (the tablet's
    window at the start, the worst placement): INFERRED arithmetic."""
    if extra_w and e_wh / (p_w + extra_w) <= window_h:
        return e_wh / (p_w + extra_w)
    if extra_w:
        return window_h + (e_wh - window_h * (p_w + extra_w)) / p_w
    return e_wh / p_w


def cons_budget(F, st):
    """ONE BUDGET on one input set: power per mode, energy (battery-only and solar-assisted, separately), heat into the
    sealed case per mode against T-H1's lines, and the reconciliation of every figure that differs between records."""
    cb, r5 = F["cb"], F["r5"]
    prof = F["idle"][1]
    tab_w, tab_wh = cb["tab_w"], cb["tab_wh"]
    out_w = cb["tab_cap"]
    tab_in = round(tab_w - out_w, 2)
    e5 = cb["e5"]
    modes = [
        ("M1", "PS-IDLE-SPEC, the approved profile (the tablet not charged)",
         "%s W at the load pins; %s W in the converters and the distribution" % (fmt(cb["idle_pins"]), fmt(round(prof - cb["idle_pins"], 2))),
         "%s W (low %s, high %s W, every load at its maximum)" % (fmt(prof), fmt(F["idle"][0]), fmt(F["idle"][2])),
         "inside the %s W: %d fans %s W at the pack; %s W of loads with no document (tier T); the board logic rows carry the power path's quiescent draws (not itemized by part); with (B1), the battery FET pair %s W more on battery (%s %% of the pack's output; drafted)"
         % (fmt(prof), cb["fans_idle"][0], fmt(cb["fans_idle"][1]), fmt(F["undoc_w"]), fmt(F["fx"]["pair_idle"][1]), fmt(F["fx"]["pair_idle"][2])),
         "%s W (the pack's I2R %s W inside), plus the pair's %s W with (B1)" % (fmt(cb["idle_heat"]), fmt(cb["idle_i2r"]), fmt(F["fx"]["pair_idle"][1])), "0 W",
         "pwr_budget.out, load_trace.out, L4-E12 out 8c, L4-E11 out 15c"),
        ("M2", "the same with the tablet charged in its window (a PROPOSAL: %02d to %02d UTC, the outlet capped at %s W)" % (cb["tab_win"][0], cb["tab_win"][1], fmt(out_w)),
         "the outlet %s W for 2 h, at %s through U19" % (fmt(out_w), fmt(cb["tab_eta"])),
         "%s W plus %s W at VBAT for 2 h: %s Wh a day" % (fmt(prof), fmt(tab_w), fmt(tab_wh)),
         "the outlet converter's idle %s to %s W only while enabled (on all day: %s Wh a day)" % (fmt(cb["tab_idle"][0]), fmt(cb["tab_idle"][1]), fmt(cb["tab_any"])),
         "%s W plus the converter's %s W in the window" % (fmt(cb["idle_heat"]), fmt(tab_in)), "%s W to the tablet in the window" % fmt(out_w), "tablet.out (l3batt)"),
        ("M3", "E3-O: the heat stage on shore (PS-SURV-R), every radio C1 leaves on",
         "one module running; the shed set off", "%s W at the pack" % fmt(cb["stage_pack"]),
         "%d fans %.3f W at the pack; the ballasts at most %s W (the bound's worst corner)" % (2, cb["fans_stage"], fmt(F["ballast_w"])),
         "%s W on shore (the front end's and the charger's loss on the loads), %s W with the ballasts" % (fmt(cb["stage_case"]), fmt(F["e3o_wb"])), "0 W",
         "L4-E12 out 2a, 8a"),
        ("M4", "E5: the hold at the +60 C dwell, on shore",
         "%s W at the load pins; %s W in the converters; %s W in the distribution" % (fmt(e5[0]), fmt(e5[1]), fmt(e5[2])),
         "%s W at the pack" % fmt(e5[3]),
         "%d fans %.3f W at the pack; the ballasts at most %s W" % (2, cb["fans_e5"], fmt(F["ballast_w"])),
         "%s W on shore (+%s W), %s W with the ballasts" % (fmt(F["e5_hold_w"]), fmt(e5[4]), fmt(F["e5_hold_wb"])), "0 W", "L4-E12 out 8a"),
        ("M5", "source-only at a 9.00 V plug, no usable pack (state S4; U-04)",
         "P1 at VBAT %s W plan (%s to %s W), at most %s W by the rule; the shed warm-up P2 %s W plan" % (fmt(F["e_p1"][1]), fmt(F["e_p1"][0]), fmt(F["e_p1"][2]),
                                                                                                   fmt(F["e_p1_max"]), fmt(F["e_p2"][1])),
         "the source delivers %s to %s W at VBAT" % (fmt(F["e_env"][9][1]), fmt(F["e_env"][9][2])),
         "the entry's loop %s W at %s A (on the source's side); the front end at least %s there" % ("%.3f" % (F["e_svc"][1] ** 2 * F["e_loop_mohm"][2] / 1000.0), fmt(F["e_svc"][1]), "%s" % F["e_eta_floor"]),
         "%s W at the rule's bound (the loads, U3 at %s and the front end at %s)" % ("%.2f" % (F["e_p1_max"] / F["eta_u3"] / F["e_eta_floor"]), "%s" % F["eta_u3"], "%s" % F["e_eta_floor"]),
         "0 W", "L4-E11 out 3g, 3h"),
        ("M6", "solar charging at the window (the source's side)",
         "the stage takes at most %s W in at the hold (%s W nominal) under L4-E7R's regulation" % (fmt(F["reg_w"][1]), fmt(F["reg_w"][0])),
         "into VBUS20 through U4/Q2", "the stage's own drive and quiescent %s W (from the panel); the sense bank %s Wh a day; the ballasts at most %s W while U3 runs (%s W at nominal parts)"
         % (fmt(cb["stage_q"][1]), fmt(F["bank_wh"][0]), fmt(F["ballast_w"]), fmt(F["ballast_nom_w"])),
         "a charge on shore adds %s W" % fmt(cb["chg_heat"]), "0 W", "L4-E7R, L4-E13 out (A-2), L4-E8, L4-E12 out 2d"),
    ]
    # energy: battery-only and solar-assisted separately; the ruled cell, the proposed cell beside it
    bat20, batc, h20, hc = F["a1_bat"]
    cand = F["a1_cand"]
    d48, d72 = 48 * prof, 72 * prof
    lost_day = round(F["a1_cand"][0] - F["e13_day_e7r"], 1)
    st48 = F["steady"][2]
    tab_steady = round(tab_wh / 24.0, 2)
    e7r_steady = round(lost_day / 24.0, 2)
    hl, e35 = (float(r5["hl"][0]), float(r5["hl"][1])), (float(r5["e35"][0]), float(r5["e35"][1]))
    cold_lo, cold_hi = float(r5["cold"][0]), float(r5["cold"][1])
    st_lo, st_hi = float(r5["start"][0]), float(r5["start"][1])
    e35_552 = F["cb"]["e35_552"]
    u1 = F["cb"]["u1"]
    win = lambda h: 2 if h == 48 else 3
    fx = F["fx"]
    pair = fx["pair_idle"][1]
    energy = [
        ("B1", "ruled 35E, D-06 4S3P", "battery-only, room temperature (the chain's +20 C)", "%s Wh usable" % fmt(bat20),
         "%s h ENERGY ONLY (%.3f h with (B1)'s pair); ENERGY AND THERMAL (L4-E12 12c, the bound, C 8 to 10 kJ/K): C1 sheds the profile at %s to %s h, the run with the shed states %s to %s h; unshed for its whole energy only from a constant %s W/K"
         % (fmt(h20), bat20 / (prof + pair), fmt(fx["c1"][0]), fmt(fx["c1"][1]), fmt(fx["c1"][2]), fmt(fx["c1"][3]), "%.3f" % fx["unshed"][0]),
         "%.2f h (the window at the start, the worst placement; energy only)" % _rt(bat20, prof, tab_w, 2.0),
         "%.2f W over 48 h, %.2f W over 72 h" % (bat20 / 48.0, bat20 / 72.0), "l4e_replay.out 2 (MODELED); L4-E12 out 12c"),
        ("B2", "ruled 35E", "battery-only, the cells at -10 C (the 35E's discharge floor)", "%s Wh usable" % fmt(batc),
         "%s h ENERGY ONLY (%.3f h with (B1)'s pair)" % (fmt(hc), batc / (prof + pair)), "%.2f h (energy only)" % _rt(batc, prof, tab_w, 2.0), "%.2f W over 48 h, %.2f W over 72 h" % (batc / 48.0, batc / 72.0), "l4e_replay.out 2"),
        ("B3", "ruled 35E", "battery-only, the cells at -5.52 C (REQ-024's -20 C with the kit's heat, LO-01b)", "%.1f Wh usable" % e35_552,
         "%.2f h ENERGY ONLY" % (e35_552 / prof), "%.2f h (energy only)" % _rt(e35_552, prof, tab_w, 2.0), "%.2f W over 48 h, %.2f W over 72 h" % (e35_552 / 48.0, e35_552 / 72.0), "L4-E10 out 9c"),
        ("S1", "ruled 35E", "solar-assisted, room temperature, the candidate panel's day (%.1f Wh into the stage, L4-E7's first round)" % cand[0],
         "first stop at h %d (06 UTC start) / h %d (18 UTC start)" % (int(cand[1]), int(cand[2])),
         "unserved %s / %s Wh at 48 h (%.1f %% of the profile's %s Wh served at most), %s / %s Wh at 72 h (%.1f %% served)"
         % (fmt(cand[3]), fmt(cand[4]), 100.0 * (1 - max(cand[3], cand[4]) / d48), fmt(round(d48, 1)), fmt(cand[5]), fmt(cand[6]), 100.0 * (1 - max(cand[5], cand[6]) / d72)),
         "unserved at most %s / %s Wh more at 48 / 72 h (%s Wh a day for %d / %d windows; INFERRED bound); the first stops unchanged (they precede the %02d UTC window)"
         % (fmt(round(tab_wh * 2, 1)), fmt(round(tab_wh * 3, 1)), fmt(tab_wh), 2, 3, cb["tab_win"][0]),
         "%.1f W at both horizons; with the tablet at most %s W lower (%.1f to %.1f W)" % (st48, fmt(tab_steady), st48 - tab_steady, st48),
         "l4e_replay.out 12 (MODELED; the corrected path, WE)"),
        ("S2", "ruled 35E", "solar-assisted, L4-E7R's accepted stage (%s Wh a day at the nominal hold)" % fmt(F["e13_day_e7r"]),
         "as S1 (not re-run); the drafted solar guard takes %s Wh more of SC-37's %s Wh a day (%s %%; %s W at the regulation's highest current; L4-E7's remedies, check 5)"
         % (fmt(F["sv"]["rm"]["day"][0]), fmt(F["sv"]["rm"]["day"][1]), fmt(F["sv"]["rm"]["day"][2]), fmt(F["sv"]["rm"]["loss"][0])),
         "unserved at most %s / %s Wh more than S1 (%s Wh a day less into the stage; INFERRED bound)" % (fmt(round(lost_day * 2, 1)), fmt(round(lost_day * 3, 1)), fmt(lost_day)),
         "as S1, plus S1's tablet bound", "%.1f to %.1f W; with the tablet %.1f to %.1f W (INFERRED bounds)" % (st48 - e7r_steady, st48, st48 - e7r_steady - tab_steady, st48),
         "L4-E13 check 4, l4e_replay.out 12"),
        ("S3", "ruled 35E", "solar-assisted at the cold end", "NOT COMPUTED: no cold-day sun trace is held, and the cells' temperature through the day is not modelled",
         "not computed", "not computed", "%.1f W if the steady load scales with the store as at room temperature (%s Wh against %s Wh; INFERRED, an estimate, not a run)" % (st48 * batc / bat20, fmt(batc), fmt(bat20)),
         "this record (the method stated)"),
        ("S4", "ruled 35E", "solar-assisted: whether the sealed case admits the charge (the cells at or under the gauge's %s C start)" % r5["thr"][5],
         "the solar rows assume the pack accepts charge at +20 C", "with the profile running, on the bound only below %s C ambient (L4-E10); on SC-37's design day "
         "the charge's heat is %s W (L4-E12 12b, the balance with the ballasts): T3's start needs %s to %s W/K (readings %s to %s W/K), T4 on the charging "
         "cells governs a running charge at %s to %s W/K (readings %s to %s W/K), class (i) at the optimistic ends and (ii) at the conservative (12e); "
         "T-H1's M8 and M9 decide (12d)"
         % (fmt(u1["charge_start"]), fmt(fx["bal_b"][1]), fx["k78"][1][2], fx["k78"][3][2], fx["k78"][1][3], fx["k78"][3][3],
            fx["modes"]["M8"]["ruled"][1], fx["modes"]["M9"]["ruled"][1], fx["modes"]["M8"]["ruled"][2], fx["modes"]["M9"]["ruled"][2]),
         "the window adds %s W of heat in the case" % fmt(tab_in), "where the case does not admit the charge the battery-only rows apply: S1 to S3 are CONDITIONAL on T-H1 (U-02)",
         "L4-E10 out 10c, this record 2c (out 16e)"),
        ("P1", "proposed HL18650V (a PROPOSAL, U-01; not adopted)", "battery-only, room temperature (L4-E10's chain at +25 C)", "%s Wh usable" % r5["hl"][0],
         "%s h ENERGY ONLY" % r5["hl"][1], "%.2f h (energy only)" % _rt(hl[0], prof, tab_w, 2.0), "%.2f W over 48 h, %.2f W over 72 h" % (hl[0] / 48.0, hl[0] / 72.0), "L4-E10 out 9c"),
        ("P2", "proposed HL18650V (a PROPOSAL)", "battery-only at the cold end (brackets, ASSUMPTION)", "%s to %s Wh with the cells at -5.52 C; %s to %s Wh from a cold start at -20 C" % (r5["cold"] + r5["start"]),
         "%.2f to %.2f h; %.2f to %.2f h ENERGY ONLY" % (cold_lo / prof, cold_hi / prof, st_lo / prof, st_hi / prof), "less, by the same arithmetic",
         "%.2f to %.2f W over 48 h at -5.52 C" % (cold_lo / 48.0, cold_hi / 48.0), "L4-E10 out 9c"),
        ("P4", "the Saft MP 176065 xtd as 4S1P (a PROPOSAL, U-01's route supported for the temperature windows; not yet adoptable, not adopted)", "battery-only, room temperature (L4-E10's chain, aged 0.80)",
         "%s to %s Wh usable (%s Wh nominal; MODELLED: Saft prints no curve; the current at temperature AWAITING, 10g)" % (fmt(F["rc"]["saft_use"][0]), fmt(F["rc"]["saft_use"][1]), fmt(F["rc"]["saft_nom"])),
         "%s to %s h ENERGY ONLY" % (fmt(F["rc"]["saft_use"][2]), fmt(F["rc"]["saft_use"][3])), "%.2f to %.2f h" % (_rt(F["rc"]["saft_use"][0], prof, tab_w, 2.0), _rt(F["rc"]["saft_use"][1], prof, tab_w, 2.0)),
         "%.2f to %.2f W over 48 h, %.2f to %.2f W over 72 h" % (F["rc"]["saft_use"][0] / 48.0, F["rc"]["saft_use"][1] / 48.0, F["rc"]["saft_use"][0] / 72.0, F["rc"]["saft_use"][1] / 72.0),
         "L4-E10 out 11c (check 6)"),
        ("P5", "the Saft MP 176065 xtd (a PROPOSAL)", "solar-assisted, room temperature; and the cold end", "not run by the replay; no cold capacity is printed",
         "not computed", "as S1's bound", "%.1f to %.1f W if the steady load scales with the store (INFERRED estimate)" % (st48 * F["rc"]["saft_use"][0] / bat20, st48 * F["rc"]["saft_use"][1] / bat20),
         "L4-E10 out 11c"),
        ("P3", "proposed HL18650V (a PROPOSAL)", "solar-assisted, room temperature", "not run by the replay",
         "not computed", "as S1's bound", "%.1f W if the steady load scales with the store (INFERRED estimate); every storage shortfall grows by at most %s Wh" % (st48 * hl[0] / bat20, r5["growth"]),
         "L4-E10 out 9c"),
    ]
    energy_facts = {"short48": cand[7], "short72": cand[8], "profile": prof, "steady": st48, "deficit": prof - st48}
    # heat into the sealed case per mode, against T-H1's lines (the rise Q / G is INFERRED, W4's lumped model)
    gc, th1 = F["gc"], F["th1"]
    w4 = cb["w4"]
    src_case = F["e_p1_max"] / F["eta_u3"] / F["e_eta_floor"]
    tb, b1 = cb["tb"], cb["b1"]
    hr = cb["hr"]
    ap = hr["ap"]
    g_lo, g_hi = tb["env"][0], tb["air_e3o"][1]

    def on_bound(q):
        return "%.0f to %.0f K over the bound's one-node lid-open points (%.3f to %.3f W/K; INFERRED, computed at smaller rises)" % (q / g_hi, q / g_lo, g_lo, g_hi)
    nc = "not computed: L4-E12 15 takes the profile's heat alone"
    rc = F["rc"]
    hr_h1 = ("not a required state at +40 C (C1 sheds it; D-02b); at its heat on the bound (two nodes, +%s C) %s W/K; fins on the face's free strips %s (k %d) to %s W/K "
             "(k %d); the large loads led into the plate %s W/K, %s W/K with the fins; the open lid's skin %s W/K; all three %s W/K against its own line K6 at REQ-014's "
             "+20 C, %s W/K: %s W (%s W/K) short; a reading at K6 of at least %s W/K needs no route (L4-E12 15 and 11, checks 6 and 7)"
             % (fmt(cb["env_top"]), ap["none"][3], ap["a2"][3], hr["k"][0], ap["a3"][3], hr["k"][1], ap["b"][3], ap["ba"][3], ap["c"][3], ap["all"][3],
                rc["K"]["K6"]["need"], fmt(hr["best"][2]), fmt(hr["best"][3]), rc["R"]["K6"]["read"]))
    heat = cons_heat_modes(F) + [
        ("A1", "the profile with the tablet's window (M5 plus the window)", cb["idle_heat"] + tab_in, "lid open, +20.0 C",
         "C1's air trigger: %.3f W/K with the window's %s W (M5's %s W/K without it)" % ((cb["idle_heat"] + tab_in) / (cb["c1_air"] - fx["modes"]["M5"]["amb"]), fmt(tab_in), fx["modes"]["M5"]["ruled"][1]),
         "as ruled", "none", "not computed (12e has no row for it)", "a PROPOSAL's window; T-H1 at M5's point reads the conductance it needs"),
        ("A2", "source-only at a 9.00 V plug (state S4; U-04)", round(src_case, 2), "the envelope's state", "not a mode of L4-E12 12a: at REQ-024's +40 C C1 sheds to the heat stage, M2's lines",
         "as M2", "none", "M2's", "the loads and the two stages' losses at the rule's bound (INFERRED)"),
        ("A3", "(B1)'s battery FET pair on battery (added to a mode; drafted)", fx["pair_idle"][1], "added to M5",
         "%s W at PS-IDLE-SPEC, %s W at PS-TYP; +%.4f W/K on M5's line" % (fmt(fx["pair_idle"][1]), fmt(fx["pair_typ"][1]), fx["pair_idle"][1] / (cb["c1_air"] - fx["modes"]["M5"]["amb"])),
         "as ruled", "none", "M5's", "each FET's installed path (E11-29)"),
    ]
    return modes, energy, energy_facts, heat


HEAT_KEY = (("SGP41", "SGP41"), ("hot stop", "hot stop"), ("C1's air", "C1's trigger +50"), ("EPAPER", "EPAPER"), ("RB9704", "RB9704"), ("LIME", "LIME"), ("T4", "T4's stop"))


def _heat_line(md, gl):
    """A governing line (name, need, reading) with its category, read from the mode's own table in L4-E12 12a."""
    name, need, read = gl
    key = [k for n, k in HEAT_KEY if n in name]
    for nd, lim, txt in md["lines"]:
        if (nd == need or (need is None and nd == "inf")) and key and key[0] in txt:
            cat = re.search(r"\[([^\]]*)\]$", txt).group(1)
            if need is None:
                return "%s: no conductance (the limit at or under the ambient) [%s]" % (name, cat)
            return "%s (the air to %s C): %s W/K, a reading of at least %s W/K [%s]" % (name, lim, need, read, cat)
    refuse(4, "L4-E12 12a's line %r has no categorised row" % name)


def cons_heat_modes(F):
    """THE HEAT INTO THE SEALED CASE PER REQUIRED MODE (L4-E12 12a, the fix round for the review's B3): each mode's heat balance, its
    ambient and lid, the governing local limit as ruled and under CFL-002's C, A or B (categorised), the maker-stated alternative where
    the governing row is an operating row read to cover an unpowered part, the capacity class of 12e and what remains. Read, not
    recomputed."""
    fx = F["fx"]
    rows = []
    for k in ["M%d" % i for i in range(1, 10)]:
        md = fx["modes"][k]
        ruled = _heat_line(md, md["ruled"])
        cab = "as ruled (every option)" if md["cab"] == md["ruled"] else _heat_line(md, md["cab"])
        stated = (_heat_line(md, md["stated"]) + " (once the maker states the unpowered range)") if md["stated"] else "none"
        cl = []
        for c in fx["cls"]:
            if c["mode"] != k:
                continue
            t = "%s: (%s)" % (c["line"], c["cls"])
            if c["cons"] != c["cls"]:
                t += ", (%s) at the conservative ends" % c["cons"]
            if c["short"]:
                t += ", SHORT by %s" % ("%s W/K, %s W" % c["short"] if c["short"][0] else "the whole %s W" % c["short"][1])
            cl.append(t)
        rem = md["remaining"].split("; the parts' local air in the built kit")[0]
        rows.append((k, md["what"], md["q"], "lid %s, %+.1f C" % (md["lid"], md["amb"]), ruled, cab, stated, "; ".join(cl),
                     rem + "; the parts' local air (T-H2), the junctions (THM-001), the 33 lines an absolute rating alone clears, the fans' rating (D-18)"))
    return rows


APPROACH_TEXT = {"none": ("the bound: the inside by natural convection, the fans' film credited at zero", "R-104 (T-H1 reads it)"),
                 "a2": ("fins on the face's free strips, effective area multiplier k %d (ASSUMPTION)", "R-170"),
                 "a3": ("fins on the face's free strips, k %d", "R-170"),
                 "b": ("the large loads, %s W at their pins, led into the plate", "R-171"),
                 "ba": ("(b) with (a)'s fins, k %d", "R-170, R-171"),
                 "c": ("a skin on the open lid's ceiling (at most %s m2) on a %s K/W braid (ASSUMPTION)", "R-172"),
                 "all": ("(b) + (a) + (c): the combined route", "R-170 to R-172")}


def cons_approaches(F):
    """L4-E12's heat-rejection approaches beside the conservative bound, at the profile's heat (read from out 10b to 10d)."""
    hr = F["cb"]["hr"]
    ap = hr["ap"]
    fill = {"a2": (hr["k"][0],), "a3": (hr["k"][1],), "b": (fmt(hr["led"]),), "ba": (hr["k"][1],), "c": (fmt(hr["lid"][0]), fmt(hr["braid"][2]))}
    rows = []
    for k in ("none", "a2", "a3", "b", "ba", "c", "all"):
        what, reg = APPROACH_TEXT[k]
        what = what % fill[k] if k in fill else what
        r = ap[k]
        rc = F["rc"]
        M = F["fx"]["modes"]
        t4 = "T4's %s and %s W/K on the charging cells (M8, M9)" % (M["M8"]["ruled"][1], M["M9"]["ruled"][1])
        if k == "all":
            against = "short by %s W (%s W/K) of M5's (K6) %s W/K; under T3's start (K7, K8) %s and %s W/K and %s (10d's %s and %s W/K short were against the uncorrected needs)" % (
                fmt(hr["best"][2]), fmt(hr["best"][3]), rc["K"]["K6"]["need"], rc["K"]["K7"]["need"], rc["K"]["K8"]["need"], t4, fmt(hr["chg_short"][0]), fmt(hr["chg_short"][1]))
        else:
            against = "under M5's (K6) %s W/K, T3's start (K7, K8) %s to %s W/K and %s" % (rc["K"]["K6"]["need"], rc["K"]["K7"]["need"], rc["K"]["K8"]["need"], t4)
        rows.append((k, what, "%s C / %s C / %s W/K" % r[1:4], "%s C / %s W/K" % r[4:6], "%s C / %s W/K" % r[6:8], against, reg))
    rc = F["rc"]
    need = ("need", "the profile's %s W: K6, C1's +50 C at REQ-014's +20 C (once read as the +70 C class at +40 C, X2, no requirement)" % fmt(hr["q"]),
            "K6: %s W/K" % rc["K"]["K6"]["need"], "K7, the charge path counted: %s W/K" % rc["K"]["K7"]["need"], "K8: %s W/K" % rc["K"]["K8"]["need"],
            "readings of at least %s (K6), %s (K7) and %s W/K (K8)" % (rc["R"]["K6"]["read"], rc["R"]["K7"]["read"], rc["R"]["K8"]["read"]), "R-104")
    return rows + [need]


def cons_approach_lines(F):
    hr = F["cb"]["hr"]
    L = ["16c' THE HEAT-REJECTION APPROACHES BESIDE THE BOUND (L4-E12 section 15, check 6 at 589f18ac; read from its out 10b to 10d, not recomputed;"
         " the profile's heat, on the conservative bound, two nodes; inside the rulings: no vent (32.53), the Peli 1450, the 3 mm face (32.40))"]
    for r in cons_approaches(F):
        L.append("   %s %s: +40 C %s; design day %s C %s; %s C %s; %s; %s" % (r[0], r[1], r[2], fmt(hr["day"][0]), r[3], fmt(hr["day"][1]), r[4], r[5], r[6]))
    L.append("   all three passive (no power, no endurance change, the heat unchanged; costs TBD, no quote held); the strap of (c) carries %s W in the route;"
             " the bound alone rejects %s W at +40 C (%s W short)" % (fmt(hr["strap"]), fmt(hr["bound_only"][0]), fmt(hr["bound_only"][1])))
    L.append("   the need beside them since L4-E12's check 7: K6, the profile at REQ-014's +20 C under C1's +50 C (%s W/K, the same figure as the withdrawn"
             " X2), and K7 and K8 with the charge path counted; 10d's owner's options (a labelled duty cycle at +40 C, PS-IDLE's %s W; a requirement change)"
             " answered the profile at +40 C, a state no requirement asks for" % (F["rc"]["K"]["K6"]["need"], fmt(hr["alt"][0])))
    return L


# The figures that differ between records, each kept with its basis or merged with the reason (the owner's instruction:
# "a figure that differs because its basis differs is kept with its basis stated, not merged"). Each figure is checked to
# be printed by the pinned file named beside it.
RECON = [
    ("R01", "the 35E pack's usable energy at room temperature", [("107.9", "replay", "the energy chain (energy_budget.py: the 35E's rate, mean-voltage and end-fraction curves, aged 0.80, to the graceful 3.00 V line) at PS-IDLE-SPEC"),
                                                                ("108.1", "budget", "pwr_budget.py's derating chain (12 x 3.35 Ah x 3.60 V, rate 0.997, sag, ageing 0.80, the 5 % reserve)")],
     "107.9 Wh", "the endurance runs (battery-only and solar-assisted) rest on the energy chain; 108.1 Wh stays only as L4-E10's first-chain comparison and in the U-01 bullet L4-E10 reads back (Appendix A)"),
    ("R02", "the proposed HL18650V pack's usable energy", [("90.2", "l4e10", "L4-E10's chain, the same as R01's 107.9 Wh"), ("90.4", "l4e10", "L4-E10's first chain, the same as R01's 108.1 Wh")],
     "90.2 Wh", "one chain with the ruled cell; the difference to the 35E is 17.7 Wh on both chains"),
    ("R03", "the panel's day into the stage at the nominal hold", [("350.0", "replay", "the candidate's trace with no input limit (L4-E7's first round); every solar-assisted run of the replay"),
                                                                  ("336.6", "l4e7r", "the same day under L4-E7R's accepted regulation (RIMON_IN 31.6k)")],
     "336.6 Wh for the design", "the replay is not re-run: its solar rows stay on 350.0 Wh, bounded at most 13.4 Wh a day worse at the accepted stage (S2)"),
    ("R04", "the hold corners' days", [("344.0", "l4e7r", "L4-E7R, the hold 16.970 to 18.221 V with the regulation"), ("373.5", "replay", "L4-E7's first round, the hold 16.695 to 18.490 V, no limit"),
                                       ("307.9", "l4e7r", "L4-E7R's upper corner"), ("280.6", "replay", "L4-E7's first round's upper corner")],
     "L4-E7R's 344.0 / 336.6 / 307.9 Wh", "the accepted stage; the replay's corners are the first round's window"),
    ("R05", "L4-E7R's highest regulated current", [("2.9318", "l4e7r", "at the hold's corners, the stage's operating range"), ("2.9337", "l4e13", "at REQ-016's 25 V ceiling, A-3(a)'s conservative input")],
     "both", "two operating points of the same regulation; neither replaces the other"),
    ("R06", "the 100 W bound's layers", [("73.3436", "l4e13", "the regulation's own 25 V corner"), ("93.5521", "l4e7r", "the backstop's static bound, CONDITIONAL on G_CM and U18's VIN+ bias"),
                                        ("93.5957", "l4e7r", "the same at the panel entry with the solar guard's own currents (the remedies, B6's parts)"),
                                        ("96.25", "l4e7r", "L4-E7's stack A, CONDITIONAL on five unprinted values")],
     "all three, each with its layer", "the regulation acts first, the backstop second; 96.25 W is the earlier qualification, kept as context"),
    ("R07", "A1's steady load through the horizon", [("8.0", "replay", "on the candidate panel's trace (350.0 Wh a day)"), ("8.8", "replay", "on the 100 W screening stimulus (a 400 Wp series REQ-016 does not admit)")],
     "8.0 W", "the screening stimulus is not a source REQ-016 admits"),
    ("R08", "the profile's power", [("42.8", "trace", "the profile's stated figure"), ("42.82", "trace", "load_trace's sum of 39 loads"), ("42.824", "l4e12", "L4-E12's reproduction of the same sum")],
     "42.8 W", "one quantity at three roundings"),
    ("R09", "the enclosure lines (W/K)", [("1.666", "l4e10", "LO-01a's floor: the inside air at the SGP41's +55 C at +40 C on shore, the heat stage"),
                                         ("1.8058", "l4e12", "LO-01a's floor with L4-E8's ballasts counted"), ("1.806", "l4e12", "E3-O alone: the heat stage with the ballasts, +55 to +70 C"),
                                         ("2.159", "l4e12", "E5 under the hold, +60 to +70 C: the BINDING line"), ("2.709", "l4e12", "E5 with no hold"),
                                         ("2.416", "l4e12", "T-H1's pass reading at a 10 K rise: 2.159 W/K plus its expanded uncertainty")],
     "all, each with its criterion", "different states and limits; since L4-E12's fix round each mode's governing local limit (12a) sets its line: 2.159 W/K is M7's maker-stated alternative (the e-paper's row governs E5), 1.806 W/K M6's, 1.666 W/K the cells' hot stop under CFL-002's C"),
    ("R10", "E5's heat under the hold", [("18.152", "l4e12", "at the pack"), ("19.497", "l4e12", "into the case on shore"), ("21.587", "l4e12", "with L4-E8's ballasts")],
     "21.587 W for the line", "three boundaries of one budget"),
    ("R11", "E3-O's heat", [("24.996", "l4e12", "into the case on shore"), ("27.086", "l4e12", "with the ballasts")], "27.086 W", "the ballasts counted once"),
    ("R12", "the charge current", [("3.0 A", "hwfw", "the drawn ChargeCurrent limit (FW-A02)"), ("3.06 A", "replay", "energy_inputs.yaml's D-06 figure (1.02 A a cell), the replay's runs")],
     "3.0 A for the design", "the replay's solar rows charge 2 % faster than the drawn limit allows, so they lean optimistic (not re-run)"),
    ("R13", "the 35E's usable energy cold", [("44.5", "replay", "the cells at -10 C, the 35E's discharge floor"), ("54.0", "l4e10", "the cells at -5.52 C, REQ-024's -20 C with the kit's heat (LO-01b)")],
     "both, each at its cell temperature", "two temperatures"),
    ("R14", "the hold's point", [("17.6 V", "l4e7r", "REQ-016's stated point"), ("17.593", "l4e7r", "the FBIN divider's nominal (R8 102 k, R9 7.50 k at 0.1 %)")],
     "17.593 V nominal", "the divider's own value; 17.6 V is the requirement's rounded point"),
    ("R15", "ChargeCurrent at the charger's POR", [("256 mA", "l4e11", "the drawn BQ25731: TI's E2E answer (the register's reset code)"), ("0 A", "l4e11", "the BQ25731's register description"),
                                                   ("0000h", "l4e11", "the selected BQ25730 (B1): its printed reset, 0 A")],
     "256 mA on the board as drawn; 0 A once (B1) is applied", "two parts; L4-E11 corrected the drawn part's figure, and SLUSE65A prints the BQ25730's"),
    ("R16", "the ballasts' loss", [("2.09", "l4e8", "at the bound's worst corner"), ("0.0093", "l4e8", "at L4-E8's nominal illustration")],
     "2.09 W in every heat budget", "the worst corner is what the thermal lines carry"),
    ("R17", "the pack heater", [("7.5 W into the cells", "l4e10", "the mat's output"), ("8.5 W at the pack", "l4e10", "with its buck's loss")],
     "both, each at its boundary", "one heater, two boundaries"),
    ("R18", "P1, the kit's shed state with no usable pack", [("19.57", "l4e11", "the plan figure at VBAT"), ("20.51", "l4e11", "the rule's bound"), ("35.24", "l4e11", "the loads' high corner")],
     "20.51 W as the bound", "the high corner exceeds the source's least, which is why REQ-015 at 9.00 V is a CONDITIONAL CANDIDATE"),
    ("R19", "the panel's day at the conditioned upper corner", [("240.0", "l4e13", "the rated unit"), ("52.3", "l4e13", "a unit at A-2's floor")],
     "both", "PANEL-ACC accepts any unit inside the window; the unserved energy grows toward the floor's unit"),
    ("R20", "T-H1's pass reading for E5's +70 C line (M7's maker-stated alternative)", [("2.416", "l4e12", "the eight-point procedure at a 10 K rise, one heater's 21.2 W"), ("2.462", "l4e12", "9f's point at its 8.6 K rise"),
                                                         ("2.455", "l4e12", "K10: E5's own heat, 21.587 W with the fans counted (11e)")],
     "2.455 W/K", "the same 2.159 W/K plus the expanded uncertainty; M7's point at E5's own heat replaces the 21.2 W lines (L4-E12 16.8, 12d); the e-paper's row governs E5 with no conductance (class (iii))"),
    ("R22", "the Saft pack's nominal energy", [("81.6", "l4e10", "four times the sheet's 20.4 Wh"), ("81.8", "l4e10chk5", "4 x 3.65 V x 5.6 Ah"),
                                               ("81.76", "l4e10", "the comparison: 4 x 5.60 Ah x 3.65 V (11b)")],
     "81.76 Wh", "three roundings of the sheet's typical figures; the usable 53.5 to 58.8 Wh (MODELLED) is what the budget uses"),
    ("R21", "the case's conductance lid open with the fans", [("1.22", "budget", "W4's lumped low case, the fans' inside film assumed (10 W/m2K)"),
                                                             ("0.566", "l4e12", "the conservative bound at E5, the fans' flow credited at zero"),
                                                             ("0.607", "l4e12", "the conservative bound at E3-O")],
     "the bound for feasibility; W4's range as a sensitivity", "W4's low end already assumes the fans' film, which no held document bounds (L4-E12 9c)"),
    ("R23", "the conservative bound lid open at +40 C", [("0.598", "l4e12", "one node at the envelope's +40 C, the air 15 K up (9b)"),
                                                         ("0.720", "l4e12", "one node at E3-O's heat, its 37.6 K rise (9d)"),
                                                         ("0.767", "l4e12", "two nodes, the inside air and the plate, at the profile's 43.413 W (10b)")],
     "all three, each at its rise and model", "the conductance grows with the rise; 2c' and the heat table keep the one-node points as the conservative side and name 0.767 W/K at the profile's own heat"),
    ("R24", "T-H1's readings near 1.5 W/K", [("1.509", "l4e12", "at 42.4 W, the fans left out: X2, the profile's +70 C class at +40 C, no requirement (10e, withdrawn in 11a)"),
                                           ("1.508", "l4e12", "K6: the profile at REQ-014's +20 C under C1's +50 C, 43.413 W with the fans (11e)"),
                                           ("1.516", "l4e12", "at E5's hold's 21.2 W: E3-O with F4, a fallback line (9f)")],
     "1.508 W/K for the profile; 1.516 W/K as a conservative fallback line", "the 1.509 W/K reading established X2 only and is withdrawn (L4-E12 check 7)"),
    ("R26", "the charging need with the profile running on the design day (T3's start)", [("1.7376", "l4e12", "12b: the balance's 50.044 W on the reviewer's boundary, cold end"),
                                                                             ("2.1115", "l4e12", "12b: the same, warm end"),
                                                                             ("1.8102", "l4e12", "12b: with L4-E8's ballasts, 52.134 W, cold end (K7)"),
                                                                             ("2.1997", "l4e12", "12b: the same, warm end (K8)")],
     "1.8102 to 2.1997 W/K (T3's start; a running charge is governed by T4 on the charging cells, 2.025 and 2.525 W/K, M8 and M9)",
     "section 11's charging heat (46.859 W) and its needs added only the charge increment and left out the source path's loss on the profile's power (the review's B4); 10a's 1.507 and 1.832 W/K left the charge path out"),
    ("R32", "the charging heat with the profile running", [("50.044", "l4e12", "12b: input less stored less exported on the model's boundary"),
                                                          ("52.134", "l4e12", "12b: with L4-E8's ballasts at their worst corner (the solar stage charges)")],
     "52.134 W for the lines", "the balance replaces section 11's 46.859 W (the review's B4)"),
    ("R33", "the battery-only runtime at PS-IDLE-SPEC", [("2.52", "l4e12", "12c: ENERGY ONLY, 107.9 Wh at 42.8 W"),
                                                         ("2.01", "l4e12", "12c: C1 sheds the profile at 2.01 to 2.51 h on the bound (energy and thermal)"),
                                                         ("2.95", "l4e12", "12c: the run with the shed states, 2.52 to 2.95 h (energy and thermal)")],
     "each with its label: energy only, or energy and thermal", "2.52 h is not an established unshed PS-IDLE-SPEC endurance (the review's B7): the profile runs unshed for its whole energy only from a constant 0.960 W/K at 8 kJ/K"),
    ("R27", "K3's bench pass line", [("0.941", "l4e12", "11e: at K3's own rise, 28.8 K, U 4.0 %"), ("0.98", "l4e12chk7", "check 7: 'near', K1's uncertainty applied")],
     "0.941 W/K, a component screen at the mixed air", "the expanded uncertainty is taken at the reading's own rise; check 7's figure is an approximation; the +70 C class needs each part's LOCAL air, the cooler's exhaust included, not the mean of the air probes (L4-E12 12a)"),
    ("R28", "the case's outside capacity", [("1.540", "l4e12", "9b: at E5's rise, a bound with a 50 m/s inside flow (12e), not the capacity"), ("1.571", "l4e12", "9b: at E3-O's rise, the same"),
                                            ("1.504", "l4e12", "11d: at K1's rise, the same 50 m/s figure"), ("1.856", "l4e12", "12e: the capacity proper at E5's rise, conservative ends"),
                                            ("1.906", "l4e12", "12e: at E3-O's rise"), ("1.810", "l4e12", "12e: at K1's rise")],
     "12e's capacity (the inside resistance at zero), per line in its class table", "the earlier 'cap' figures were the bound with a 50 m/s inside flow (L4-E12 12e's correction); the classes (i) to (iii) are read against the capacity with the route at the optimistic ends"),
    ("R30", "D4's clamp at CS116's 10 A at the hot end", [("39.00", "l4e7r", "the drafted SMCJ28A (D1)"), ("41.91", "l4e7r", "the SMCJ30A with the guard (the remedies)")],
     "41.91 V", "D4 changes to the SMCJ30A with the guard; both under the drafted entry's 50 V"),
    ("R31", "the solar cut-off's rising band", [("29.11", "l4e7r", "new parts"), ("28.55", "l4e7r", "aged by the divider's printed load-life, with the pin's leakage")],
     "28.55 to 31.06 V", "the record's convention for a protection threshold: the aged band"),
    ("R29", "the 35E pack's nominal energy", [("145", "l4e10", "D-06's 'about 145 Wh'"), ("144.72", "l4e10", "12 x 3.35 Ah (the minimum) x 3.60 V (11b)"),
                                             ("149.04", "l4e10", "on the typical 3.45 Ah (11b)")],
     "144.72 Wh", "D-06's figure is the minimum capacity's; the usable 107.9 Wh is what the budget uses"),
    ("R25", "the approved profile's heat into the case", [("43.4", "l4e12", "this record's figure at a0212d9e, as L4-E12 10a quotes it"),
                                                         ("43.413", "l4e12", "L4-E12 10a: 42.824 W at the pack plus the pack's own I2R")],
     "43.4 W in this record's tables; 43.413 W in L4-E12's thresholds", "one quantity at two roundings; 1.447 W/K either way"),
]


def recon_check(T):
    """Each reconciled figure is printed by its named file; refuse otherwise."""
    for rid, _q, figs, _k, _w in RECON:
        for val, key, _basis in figs:
            if not re.search(r"(?<![\d.])%s(?![\d])" % re.escape(val), T[key]):
                refuse(4, "%s: %s is not printed by %s" % (rid, val, PINS[key][0]))


def cons_budget_lines(F, st):
    modes, energy, ef, heat = cons_budget(F, st)
    L = []
    p = L.append
    p("16. THE BUDGET: ONE INPUT SET (every figure read above; MODELED unless named; the approved profile PS-IDLE-SPEC is kept, alternatives labelled)")
    p("16a POWER PER MODE (the loads, the conversion losses, the auxiliaries, into the case and out of it)")
    for row in modes:
        p("   %s %s" % (row[0], row[1]))
        for lab, x in zip(("the loads", "at the pack or VBAT", "auxiliaries", "into the case", "leaves the case", "read from"), row[2:]):
            p("      %s: %s" % (lab, x))
    p("16b ENERGY: battery-only and solar-assisted, SEPARATELY; the ruled cell, the proposed cell beside it (a proposal)")
    for row in energy:
        p("   %s %s; %s" % (row[0], row[1], row[2]))
        for lab, x in zip(("the store", "runtime, the tablet not charged", "with the tablet's window", "the steady load each horizon carries", "read from"), row[3:]):
            p("      %s: %s" % (lab, x))
    p("   ENDURANCE, apart from electrical feasibility: the objective of 48 to 72 h is NOT MET by A1 (DR-01): the steady load the store and the sun")
    p("     carry is %.1f W against the profile's %s W, a deficit of %.1f W (%.0f %% of the profile); the least storage to add is +%s / +%s Wh at 48 / 72 h."
      % (ef["steady"], fmt(ef["profile"]), ef["deficit"], 100.0 * ef["deficit"] / ef["profile"], fmt(ef["short48"]), fmt(ef["short72"])))
    p("     A charger change does not close it: the deficit is the store and the day's harvest, not a conversion efficiency. No mandatory function is reduced.")
    p("16c HEAT INTO THE SEALED CASE PER REQUIRED MODE (L4-E12 12a and 12e, the fix round): each mode's governing LOCAL limit, categorised; absolute")
    p("    ratings are screens, never lines; a T-H1 point closes only the conductance it reads")
    for hid, mode, q, la, ruled, cab, stated, cls, rem in heat:
        p("   %s %s: %s W, %s; as ruled: %s; under C, A or B: %s; maker-stated: %s; class: %s; remaining: %s"
          % (hid, mode, "%.4g" % q if q < 1 else "%.3f" % q, la, ruled, cab, stated, cls, rem))
    L.extend(cons_approach_lines(F))
    p("16d THE RECONCILIATION (each figure printed by the file named; kept with its basis, or merged with the reason)")
    for rid, q, figs, kept, why in RECON:
        p("   %s %s: %s" % (rid, q, "; ".join("%s (%s: %s)" % (v, PINS[k][0].split("/")[-1], b) for v, k, b in figs)))
        p("      kept: %s; why: %s" % (kept, why))
    L.extend(cons_normal_lines(F))
    return L


def cons_budget_tables(F, D, st):
    modes, energy, ef, heat = cons_budget(F, st)
    T = {}
    T["| Mode | "] = ["| Mode | State | The loads | At the pack or VBAT | Auxiliaries | Into the case | Leaves the case | Read from |", "|---|---|---|---|---|---|---|---|"] + \
        ["| %s |" % " | ".join(r) for r in modes]
    T["| Case | "] = ["| Case | Cell | Basis | The store | Runtime, the tablet not charged | With the tablet's window | The steady load each horizon carries | Read from |",
                      "|---|---|---|---|---|---|---|---|"] + ["| %s |" % " | ".join(r) for r in energy]
    T["| Heat | "] = ["| Heat | Mode | Into the case (W) | Lid, ambient | The governing local limit as ruled [category]: needs, a reading of at least | Under CFL-002's C, A or B | "
                      "The maker-stated alternative | The capacity class (12e: the optimistic ends; the conservative beside) | What remains |",
                      "|---|---|---|---|---|---|---|---|---|"] + ["| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (h[0], h[1], "%.4g" % h[2] if h[2] < 1 else "%.3f" % h[2], h[3], h[4], h[5], h[6], h[7], h[8]) for h in heat]
    hr = F["cb"]["hr"]
    T["| Approach | "] = ["| Approach | Its change, inside the rulings | +40 C: the air / the plate / G | Design day %s C: the air / G | %s C: the air / G | Against the need | Register |"
                          % (fmt(hr["day"][0]), fmt(hr["day"][1])), "|---|---|---|---|---|---|---|"] + ["| %s |" % " | ".join(r) for r in cons_approaches(F)]
    T["| Figure | "] = ["| Figure | Quantity | The figures, each with its basis and the file that prints it | Kept | Why |", "|---|---|---|---|---|"] + \
        ["| %s | %s | %s | %s | %s |" % (rid, q, "; ".join("%s (%s: %s)" % (v, PINS[k][0].split("/")[-1], b) for v, k, b in figs), kept, why) for rid, q, figs, kept, why in RECON]
    return T


# THE CIRCUIT-CHANGE LIST in application order: every implementation row of the register (L4-E4 to L4-E13, this record, the
# U-01 and U-04 drafts), with its board and generator, apply script, dependency, release guard and state. Nothing is APPLIED.
GA, GE, GB, GC, GP = "board A, gen_sch_a.py", "board E, gen_sch_e.py", "board B, gen_sch_b.py", "board C, gen_sch_c.py", "board P, gen_sch_p.py"
G_L4E4 = "L4-E4's RELEASE.md (R-90: accepted checks of L4-E4, L4-E5, L4-E6 and L4-E8)"
G_L4E7 = "L4-E7's RELEASE.md (R-92: L4-E7R's check 4)"
G_L4E8 = "L4-E8's RELEASE.md (R-91: check-l4e8-3.md), and the draft refuses a generator without R12"
G_L4E9 = "this record's RELEASE.md (R-93, after its check)"
G_L4E11 = "L4-E11's RELEASE.md (R-147: check-l4e11-3.md at a15ab384)"
CHANGE_ORDER = [
    ("1", "R-23", "HW-FW-CONTRACT.md (Layer 5)", "with board A's H3 line", "the draft refuses a second application"),
    ("1", "R-24", "pcb_interfaces.yaml, HW-FW-CONTRACT.md (Layer 5)", "with the release records", "a text draft"),
    ("1", "R-125", "HW-FW-CONTRACT.md, PANEL.md (Layer 5)", "with the release records", "a text draft"),
    ("1", "R-133", "CONOPS", "with the release records", "a text draft"),
    ("1", "R-135", "L4-E5's V-A08 (Layer 4)", "with the release records", "a text draft"),
    ("1", "R-138", "CONOPS 4, HW-FW-CONTRACT.md (Layer 5)", "with the release records", "a text draft"),
    ("3a", "R-01", GA, "first in board A's round, together with R-03 and R-124: L4-E6 forbids R12 before the H3 line", "none: L4-E6's draft carries no release guard"),
    ("3a", "R-02", "board A, lcsc_fill.py", "with R-01", "none"),
    ("3a", "R-03", GA, "with R-01 and R-124 (the corrected knee)", "no draft yet"),
    ("3a", "R-124", GA, "with R-03 (the guard under the corrected knee)", G_L4E11),
    ("3a", "R-157", GA, "U-04's selected charger (B1): the BQ25730 and the battery FET pair Q39 and Q40 in U3's land, J_DOCK pin 1 on VBAT, with R-124 in either order; the strap kept fixed", G_L4E11 + " and its check 5 at 5aa18a69 (the pair: its fix round at 656fc540)"),
    ("3a", "R-178", "pcb_interfaces.yaml (IF-AE-DOCK; the Layer 4 coordinator)", "with R-157 and R-177: the dock's pin 1 VBAT and VSYS_E, seven ground contacts", G_L4E11),
    ("3b", "R-04", GA, "after R-01: R11 never before R12", G_L4E4),
    ("3c", "R-07", GA, "after R-01: the ballasts and Cc2 only with R12", G_L4E8),
    ("3c", "R-08", "board A, lcsc_fill.py", "with R-07", "no draft yet"),
    ("3d", "R-05", GA, "independent", G_L4E4),
    ("3e", "R-06", GA, "after 3a to 3d", G_L4E9),
    ("3f", "R-09", GA, "with R-07", "a text draft"),
    ("3f", "R-10", "board A, the declarations", "with R-04", "no draft yet"),
    ("3g", "R-11", "board A, regenerated on the box", "after 3a to 3f", "the gates and the evidence re-taken"),
    ("4a", "R-16", GE, "no later than R-13", "none: d8dec31's draft carries no release guard"),
    ("4a", "R-17", GE, "no later than R-13", G_L4E9),
    ("4b", "R-13", GE, "only in the same release as board A's H3 line (R-03)", "no draft yet"),
    ("4b", "R-14", GE, "with R-13", "no draft yet"),
    ("4b", "R-15", "board E, the declarations", "with R-13", "no draft yet"),
    ("4c", "R-12", GE, "board E's round", G_L4E7),
    ("4c", "R-19", GE, "board E's round", G_L4E7),
    ("4c", "R-20", GE, "after R-19", G_L4E7),
    ("4c", "R-144", GE, "U-02's board E changes", "no draft yet"),
    ("4d", "R-21", GE, "on the texts R-19 and R-20 leave", G_L4E7),
    ("4d", "R-98", GE, "with R-21 (the same draft)", G_L4E7),
    ("4e", "R-18", GE, "after 4c and 4d", G_L4E9),
    ("4e", "R-95", "board E, pcb_energy_chain.yaml", "with R-18", "no draft yet"),
    ("4e", "R-96", "pcb_fuse_derating.yaml", "with R-18", "no draft yet"),
    ("4e", "R-132", GE, "with R-18 (F1's holder)", "no draft yet"),
    ("4e", "R-94", GE, "after R-18: the base the entry draft applies on", G_L4E9),
    ("4e", "R-123", GE, "AFTER R-94 (its old texts are that draft's results) and INSTEAD of the timer draft (R-119)", G_L4E11),
    ("4e", "R-116", "board E, lcsc_fill.py", "with R-123", "no draft yet"),
    ("4e", "R-173", GE, "AFTER L4-E7's three drafts (R-19, R-20, R-21), L4-E9's hot swap (R-94) and L4-E11's entry draft (R-123): it uses their texts and the DGX19 land, and refuses a generator without them",
     G_L4E7 + " and its check 5 at 573fd5b8"),
    ("4e", "R-177", GE, "with R-157 (board A's J_DOCK pin 1 on VBAT) and in the same release: J_BLK pin 1 on VSYS_E, U12, C31 and the fans off CELL_F", G_L4E11),
    ("4f", "R-22", "board E, regenerated on the box", "after 4a to 4e", "the gates and the evidence re-taken"),
    ("B", "R-107", GB, "board B's round", "no draft yet"),
    ("B", "R-163", GB, "U-02's F3: board B's round", "no draft yet"),
    ("B", "R-166", GB, "U-02's +85 C connectors and HX magnetics, after R-165's picks", "no draft yet"),
    ("C", "R-145", GC, "board C's round", "no draft yet"),
    ("5", "R-25", "firmware", "only on a board A with the H3 line (else the derated limit)", "firmware"),
    ("5", "R-26", "firmware", "with R-23", "firmware"),
    ("5", "R-27", "firmware", "after R-06", "firmware"),
    ("5", "R-28", "firmware", "with the D-11 rules", "firmware"),
    ("5", "R-126", "firmware", "with R-125", "firmware"),
    ("5", "R-139", "firmware", "with R-138", "firmware"),
    ("5", "R-158", "firmware", "only on a board A carrying R-157 (the BQ25730's register rules)", "firmware"),
    ("5", "R-164", "firmware", "with R-163 (F3's switches)", "firmware"),
    ("8", "R-129", "Layer 7, the DC receptacle and plug", "before the harness is built", "no draft yet"),
    ("8", "R-130", "Layer 7, the interconnect", "with R-129", "no draft yet"),
    ("8", "R-131", "Layer 7, the inside lead and J_DCIN", "with R-129", "no draft yet"),
    ("8", "R-111", "Layer 7, the enclosure", "U-02: to T-H1's line", "no draft yet"),
    ("8", "R-180", "Layer 7, the panel lead (the harness)", "before the harness is built; with R-176's row 2 (the lead's measured loop inductance)", "no draft yet"),
    ("8", "R-170", "Layer 7, the face plate's fins", "U-02's combined route, only under a T-H1 point reading under its line (R-104); with R-171 and R-172, read together at the same point",
     "no draft yet; conditional on T-H1's reading (R-104)"),
    ("8", "R-171", "Layer 7, the plate's conduction kit (heat pipes, bars and pads from board B's and the face's parts)", "with R-170 (the plate the kit loads carries the fins)",
     "no draft yet; conditional on T-H1's reading (R-104)"),
    ("8", "R-172", "Layer 7, the open lid's skin and its braid", "with R-170 and R-171", "no draft yet; conditional on T-H1's reading (R-104)"),
    ("U-01", "R-105", GP, "only under U-01's approach (II), after the owner's approval", "no draft yet"),
    ("U-01", "R-106", "firmware, the gauge image", "only under (II)", "firmware"),
    ("U-01", "R-154", "firmware, the gauge image and the host", "only under (II), with R-106", "a text draft"),
    ("ALT", "R-119", GE, "the LM5069 alternative only: refuses once the selected entry (R-123) has run", G_L4E11),
    ("ALT", "R-152", GA, "arrangement (A) only: withdrawn once R-157 is applied (its zone and height Layer 9's)", "no draft yet"),
]
ORDER_CONSTRAINTS = [
    ("R-90 before every board A circuit change", "R-90", "R-04"),
    ("R12 (R-01) before R11 (R-04)", "R-01", "R-04"),
    ("R12 (R-01) before the ballasts and Cc2 (R-07)", "R-01", "R-07"),
    ("the H3 line (R-03) with R12, before R11", "R-03", "R-04"),
    ("Q1 and E-F1's capacitor (R-17, R-16) no later than R10 (R-13)", "R-17", "R-13"),
    ("the hot-swap settings (R-94) before the selected entry's draft (R-123)", "R-94", "R-123"),
    ("F1 (R-18) before the hot-swap settings (R-94)", "R-18", "R-94"),
    ("L4-E7's hold and input limit (R-19, R-20) before its backstop (R-21)", "R-20", "R-21"),
    ("U17's move (R-06) before its firmware recalibration (R-27)", "R-06", "R-27"),
    ("board A regenerated (R-11) after its circuit changes, the charger (R-157) among them", "R-157", "R-11"),
    ("the BQ25730's firmware rules (R-158) after the charger (R-157)", "R-157", "R-158"),
    ("board E regenerated (R-22) after its circuit changes", "R-116", "R-22"),
    ("L4-E7's backstop and corrected entry (R-21) before the solar guard (R-173)", "R-21", "R-173"),
    ("the hot-swap settings (R-94) before the solar guard (R-173)", "R-94", "R-173"),
    ("L4-E11's entry draft (R-123) before the solar guard (R-173)", "R-123", "R-173"),
    ("the solar guard (R-173) before board E's regeneration (R-22)", "R-173", "R-22"),
    ("board A's dock pin on VBAT (R-157) before board E's VSYS_E feed (R-177)", "R-157", "R-177"),
    ("board E's VSYS_E feed (R-177) before board E's regeneration (R-22)", "R-177", "R-22"),
]
CHANGE_SCRIPTS = ["l4e4/apply_gen_sch_a_r11.py", "l4e4/apply_gen_sch_a_r138.py", "l4e5/apply_fw_a16.py", "l4e6/apply_gen_sch_a_r12.py", "l4e6/apply_lcsc_fill_r12.py",
                  "l4e7/apply_gen_sch_e_backstop.py", "l4e7/apply_gen_sch_e_hold.py", "l4e7/apply_gen_sch_e_input_limit.py", "l4e7/apply_gen_sch_e_u5_grade.py",
                  "l4e7/apply_gen_sch_e_solar_guard.py",
                  "l4e8/apply_gen_sch_a_bank.py", "l4e9/apply_gen_sch_a_u17.py", "l4e9/apply_gen_sch_e_f1.py", "l4e9/apply_gen_sch_e_hotswap.py", "l4e9/apply_gen_sch_e_q1.py",
                  "l4e11/apply_gen_sch_a_guard.py", "l4e11/apply_gen_sch_e_entry.py", "l4e11/apply_gen_sch_e_timer.py", "l4e11/apply_gen_sch_a_charger.py",
                  "l4e11/apply_gen_sch_e_aux.py", "l4e11/apply_pcb_interfaces_dock.py",
                  "d8dec31/apply_gen_sch_e_cin.py"]


def cons_changes(reg):
    """The change list from the register's rows; refuses a list that misses an implementation row, an apply script of L4-E4
    to L4-E13 (and d8dec31's input capacitor), or breaks a named order constraint."""
    rows = {r[0]: r for r in reg}
    impl = [r[0] for r in reg if r[1] == "IMPLEMENTATION"]
    listed = [c[1] for c in CHANGE_ORDER]
    if len(listed) != len(set(listed)) or sorted(set(impl) - set(listed)) or any(x not in rows for x in listed):
        refuse(4, "the change list is not every implementation row once: missing %s" % sorted(set(impl) - set(listed)))
    out = []
    for i, (step, rid, bg, dep, guard) in enumerate(CHANGE_ORDER, 1):
        r = rows[rid]
        scripts = re.findall(r"`?(apply_[a-z0-9_]+\.py)`?", r[3]) or re.findall(r"`?(apply_[a-z0-9_]+\.py)`?", r[2])
        if r[6] == "MISSING DRAFT":
            script = "none: a missing draft"
        else:
            script = ", ".join(scripts) if scripts else ("none: %s work" % r[6].lower() if r[6] != "DRAFTED" else "a text draft (%s)" % r[3].split(",")[0])
        state = "%s (not applied)" % r[6] if rid != "R-119" else "DRAFTED, the alternative only (not applied)"
        out.append((i, step, rid, bg, script, dep, guard, r[2], state))
    named = " ".join(c[4] for c in out)
    for s in CHANGE_SCRIPTS:
        if os.path.basename(s) not in named:
            refuse(4, "the change list misses %s" % s)
    have = set(re.sub(r"^.*/records/", "", p) for p in glob.glob(os.path.join(TOP, "v2/docs/records/l4e*/apply_*.py")))
    if sorted(have - set(CHANGE_SCRIPTS)):
        refuse(4, "an apply script of L4-E4 to L4-E13 is not in the change list: %s" % sorted(have - set(CHANGE_SCRIPTS)))
    pos = {c[2]: c[0] for c in out}
    pos["R-90"] = 0
    for what, a, b in ORDER_CONSTRAINTS:
        if not pos[a] < pos[b]:
            refuse(4, "the change list breaks: %s" % what)
    return out


def cons_change_lines(reg):
    ch = cons_changes(reg)
    L = ["17. THE CIRCUIT-CHANGE LIST, IN APPLICATION ORDER (every implementation row of the register; %d changes; none APPLIED)" % len(ch)]
    L.append("   the release records first: R-90 (L4-E4's, naming L4-E4 to L4-E6 and L4-E8), R-91 (L4-E8's), R-92 (L4-E7's), R-93 (this record's), R-147 (L4-E11's)")
    for i, step, rid, bg, script, dep, guard, what, state in ch:
        L.append("   %2d [%s] %s %s; %s; depends: %s; guard: %s; %s" % (i, step, rid, bg, script, dep, guard, state))
    L.append("   the order constraints, each checked on the list:")
    for what, _a, _b in ORDER_CONSTRAINTS:
        L.append("     %s: holds" % what)
    states = {}
    for c in ch:
        states[c[8].split(" (")[0].split(",")[0]] = states.get(c[8].split(" (")[0].split(",")[0], 0) + 1
    L.append("   by state: %s; APPLIED 0" % "; ".join("%s %d" % (k, states[k]) for k in sorted(states)))
    return L


def cons_change_table(F, D, st):
    reg = md_table(open(os.path.join(HERE, "DOWNSTREAM-REGISTER.md"), encoding="utf-8").read(), "| ID | Kind |")
    ch = cons_changes(reg)
    return {"| # | Step | Row | ": ["| # | Step | Row | Board and generator | Apply script | Depends on | Release guard | What it changes (the register's item) | State |",
                                "|---|---|---|---|---|---|---|---|---|"] + ["| %d | %s | %s | %s | %s | %s | %s | %s | %s |" % c for c in ch]}


BEH_HEAD = [("4a", "| Source change |", "| Source change | What acts | The figure | Record |"),
            ("4b", "| Together |", "| Together | What acts | The figure | Record |"),
            ("4c", "| Start |", "| Start | What acts | The figure | Record |"),
            ("4d", "| Stop |", "| Stop | What acts | The figure | Record |"),
            ("4e", "| Trip |", "| Trip | What acts, its threshold and time | What it isolates | The recovery | Record |"),
            ("4f", "| Thermal |", "| Thermal | What acts | The figure | Record |"),
            ("4g", "| If it stalls |", "| If it stalls | What still acts with no firmware | What does not (not fail-safe) | Record |")]


def cons_behaviour(F, D, st):
    """THE OPERATING BEHAVIOUR, one table per item; every row tied to a record and a figure read above."""
    bh, cb, r5 = F["cb"]["bh"], F["cb"], F["r5"]
    b1 = cb["b1"]
    B = {}
    B["4a"] = [
        ("plug in (vehicle or shore)", "the entry's UVLO, then its slewed start; U3 in HIZ under the knee; the H3 line from the first cycle; U34 releases the front end",
         "on at %s / %s / %s V of DC_P; %s to %s A for at most %s ms; HIZ certain below %s V; the flat %s A from %s V" % (fmt(F["e_uv_on"][0]), fmt(F["e_uv_on"][1]), fmt(F["e_uv_on"][2]),
                                                                                                                     fmt(F["e_inrush"][0]), fmt(F["e_inrush"][1]), fmt(F["e_start_ms"]),
                                                                                                                     fmt(F["knee_hiz"]), fmt(F["knee"][0]), fmt(F["knee"][1])), "L4-E11 3c, 3f"),
        ("plug out", "the LM74700-Q1 blocks; the pack carries VBAT with no break, under (B1) through the battery FETs Q39 and Q40 (ideal-diode supplement, SLUSE65A p.38; their body diodes conduct first), as drawn (A) the pack and VBAT one node; U3 resets IIN_HOST and firmware rewrites it; U34's guard stops the front end; the bank bleeds",
         "IIN_HOST %s A at removal, %.2f A rewritten (FW-A16); the guard %s to %s V; the bleed %s to %s s" % (fmt(bh["iin_reset"]), F["iin_host"], fmt(F["guard_sel"][0]), fmt(F["guard_sel"][2]),
                                                                                                         fmt(bh["bleed"][0]), fmt(bh["bleed"][1])), "CHARGER-STATE-SEQUENCE.md, L4-E11, L4-E8"),
        ("panel at dawn", "U5's own UVLO and soft start; SWEN off while TRK_LDO33 is low; the hold; the regulation",
         "SWEN off below %s V; the hold %s V; %s A nominal, at most %s A (%s / %s W in)" % (fmt(F["swen_v"]), "%.3f" % F["hold"][1], fmt(F["reg"][0]), fmt(F["reg"][1]), fmt(F["reg_w"][0]), fmt(F["reg_w"][1])),
         "L4-E7R"),
        ("panel at dusk", "the panel falls under the hold and the stage stops delivering; U4/Q2 blocks VIN_RAW from TRK_OUT; with no other source VIN_RAW falls into the knee's HIZ",
         "HIZ below %s V; the guard %s to %s V" % (fmt(F["knee_hiz"]), fmt(F["guard_sel"][0]), fmt(F["guard_sel"][2])), "L4-E7R, L4-E11 3f"),
        ("pack connected", "the gauge's FETs close onto VBAT; under (B1) board E's always-on comes up on VSYS_E (board A's VSYS over the dock's pin 1, L4-E11 15a), as drawn on CELL_F; the inrush into VBAT's capacitors, under (B1) through the pair's body diodes (E11-30)",
         "%s A peak, over ASCD's %s A for %s us against its %s us delay (with E11-24's direct can; the drawn VBAT holds less); under (B1) %s A against each FET's ISM %s A at 25 C, met from the +70 C air for a share of at most %s in one FET (E11-30)"
         % (fmt(bh["inrush"][0]), fmt(bh["inrush"][1]), fmt(bh["inrush"][2]), fmt(bh["inrush"][3]), fmt(F["fx"]["dock"][0]), fmt(F["fx"]["dock"][1]), fmt(F["fx"]["dock"][2])),
         "L4-E11 out 10, 15c"),
        ("pack disconnected, or both FETs open, with a source", "(B1): the BQ25730 regulates VSYS at VSYS_MIN (at least %s V with adequate input); board E's auxiliary domain runs on VSYS_E from the source (L4-E11 15a); as drawn (A): U3 holds VBAT at ChargeVoltage, CONDITIONAL on TI's D1" % b1["vsys_min"],
         "(B1) at least %s V (SLUSE65A p.10, printed; EN_OOA written 0 first); with no pack and an overloaded source no floor, R-c sheds; as drawn VSYS at least %s V against VSYS_MIN %s V once the mode is shown" % (b1["vsys_min"], r5["d1"][1], r5["d1"][0]),
         "L4-E11 12c, 15a, 15d, 9 (D1)"),
        ("the charge inhibited (the hold's flag), the pack present", "(B1): Q39 and Q40 off, VSYS piecewise; board E on VSYS_E; the pack feeds no kit load, its monitor %s mA (L4-E11 15a, 15d); as drawn (A): D3 open" % fmt(F["fx"]["mon"][0]),
         "(B1) SRN under %s V: VSYS at least %s V; SRN over %s V: VSRN + %d mV within +-%d %% (the upper side an assumed reading of TI's column, A11-18); between: at least %s V; the held pack current at most %s mA on the bench (the bounded drains %s mA; E11-31)"
         % (fmt(F["fx"]["pw"][0]), fmt(F["fx"]["pw"][1]), fmt(F["fx"]["pw"][2]), b1["inhib"][0], b1["inhib"][1], fmt(F["fx"]["pw"][3]), fmt(F["fx"]["held"][1]), fmt(F["fx"]["held"][0])),
         "L4-E11 15a, 15d"),
        ("the pack present, the source on", "(B1): the battery FETs fully on while charging or supplementing; VSYS_MIN the floor with adequate input; with the source overloaded VSYS follows the pack through the pair and R17",
         "VSYS from %s V to %s V with adequate input; down to %s V in supplement at CELL_FUSED's %s V and OCD1's %s A" % (b1["vsys_min"], b1["vsys_max"], fmt(F["fx"]["supp"][0]), fmt(F["fx"]["supp"][1]), fmt(F["fx"]["supp"][2])),
         "L4-E11 12c, 15d"),
    ]
    rows = [("the profile with solar at the window and a 24 V vehicle", "the two sources OR-connected onto VIN_RAW feed ONE shared charger input limit (U3's IIN_HOST), not two additive charger capacities; the tracker's ceiling above 24 V: the panel carries the bus first; the H3 line at VIN_RAW",
             "at most %s A at 24 V, %s %% of the breaker's lowest %s A" % (fmt(F["h3"][24.0][1]), fmt(round(F["h3"][24.0][1] / F["e_oc"][0] * 100, 1)), fmt(F["e_oc"][0])), "L4-E5, L4-E11"),
            ("what reaches VBAT from the sources", "U3 between its minimum at the lowest bus and its board-current maximum",
             "%s to %s W" % (fmt(round(D["vbat_avail_min"], 1)), fmt(round(D["vbat_avail_max"], 1))), "this record out 5")]
    for nm, w in (("PS-IDLE-SPEC", F["idle"][1]), ("PS-TYP with the USB-C outlet at 45 W", F["typ_usbc"][0]), ("the PA keyed alone at 113 W", F["pa113"][0]), ("PS-ALLTX (plan)", F["alltx"][1])):
        short = w - D["vbat_avail_min"]
        rows.append(("%s, %s W" % (nm, fmt(w)), "the loads take the sources first, the pack the rest; the outlets drop while the PA keys (OUTLET_OK)",
                     ("up to %s W left to charge, at most %.1f A" % (fmt(round(-short, 1)), F["chg_set"])) if short <= 0 else ("the pack supplies at least %s W" % fmt(round(short, 1))),
                     "this record out 5"))
    rows.append(("a 9.00 V plug with the profile", "the pack supplements: the source's least cannot sustain the %s W profile without the pack, and with no usable pack the kit sheds (R-c, P0 to P3); it charges only while the kit draws under the source's least" % fmt(F["idle"][1]),
                 "%s to %s W at VBAT from the plug, against the profile's %s W" % (fmt(F["e_env"][9][1]), fmt(F["e_env"][9][2]), fmt(F["idle"][1])), "L4-E11 3h"))
    B["4b"] = rows
    B["4c"] = [
        ("cold start on the pack", "MAIN brings up board A's +3V3; DEV_EN on by its pull-up; the panel controller runs FW-C01's order: PI_KILL low, the expanders' outputs before their configuration, the charger with FW-A01 first, then SLOT_EN one at a time",
         "before the host writes IIN_HOST the input limit gives about 31 W into VSYS (INFERRED)", "ARCHITECTURE.md 4.3, HW-FW-CONTRACT, CHARGER-STATE-SEQUENCE.md"),
        ("power-on under (B1)", "ChargeCurrent 0 A until firmware writes it; EN_OOA resets to 1 and is written 0 at boot (the printed VSYS accuracy holds only after that write, E11-31); CELL_BATPRESZ a fixed 4S strap, never wired to battery presence; the docking inrush through the pair's body diodes",
         "the strap %s %% of VDDA; %s A against each FET's ISM %s A at 25 C, met from the +70 C air for a share of at most %s in one FET (E11-30)" % (b1["strap"], fmt(F["fx"]["dock"][0]), fmt(F["fx"]["dock"][1]), fmt(F["fx"]["dock"][2])),
         "L4-E11 12a, 15c, 15d (R-157, R-160)"),
        ("a source-only start under (B1) (no pack, or both FETs open)", "the source and the entry; the front end to VBUS20; U3's POR, ChargeCurrent 0 A; the converter up; VSYS through VSYS_UVP's start to VSYS_MIN; board A's always-on and board E's U12 on VSYS_E; board E's controller up and driving HOT-R1; firmware: EN_OOA 0, IIN_HOST %.2f A, CHRG_INHIBIT from the hold flag" % F["iin_host"],
         "on held evidence the start ends in VSYS_MIN or in a latch within %s s (the hiccup's 500 ms off and 10 ms retries; the 7th failure inside 90 s latches; a re-plug clears it); whether the first window succeeds is not bounded: 0.5 A is an input ceiling, not a delivered current (the earlier 502.3 ms withdrawn); E11-31 at -20, 25 and 62.1 C" % fmt(F["fx"]["latch_s"]),
         "L4-E11 15a, 15b (R-161)"),
        ("a dead pack (at or under CUV)", "the gauge's CUV holds; U3 charges through the open discharge FET's body diode at its clamp (as drawn); under (B1) R-b' precharges through one FET of the pair in LDO mode; rules R-a to R-d; the image's pre-charge",
         "CUV %.2f V a cell; as drawn the clamp %s mA typical (no maximum printed: D7) and ChargeCurrent %s mA at POR; (B1) 0x0080, at most %s A with R17's 1 %% (all of it in one FET), no charge under %s V on SRN"
         % (F["cuv"], fmt(bh["clamp_ma"]), r5["por"], "%.5f" % F["fx"]["pre"][0], fmt(F["fx"]["pre"][1])), "L4-E11 2, 4, 9, 15c"),
        ("a cold pack", "UTC holds the charge FET; the mat warms the block first (FW-A13); under U-01's (II) the kit's hold moves to %s C" % r5["hold"],
         "warm before charge below %s C at the cell; the mat 12.0 V, 7.5 W" % fmt(bh["heat_below"]), "HW-FW-CONTRACT FW-A13, L4-E10 14b"),
        ("source-only at a 9.00 V plug", "the shedding sequence P0 to P3 (L4-E11 3g): P1 kept, the warm-up P2 on the source's headroom; the profile does not run there (the source's least is under it)",
         "P1 at most %s W; P2 %s W plan carried with %s W in hand; the source %s to %s W at VBAT" % (fmt(F["e_p1_max"]), fmt(F["e_p2"][1]), fmt(F["e_p2_hand"]), fmt(F["e_env"][9][1]), fmt(F["e_env"][9][2])),
         "L4-E11 3g, 3h (U-04)"),
    ]
    B["4d"] = [
        ("graceful, on battery", "the firmware's graceful line ends the run before either cell's end voltage", "%.2f V a cell under load" % bh["graceful"], "L4-E10 9b, 9c"),
        ("the gauge's under-voltage", "CUV opens the discharge FET", "%.2f V a cell (%s V under U-01's (II))" % (F["cuv"], r5["cuv"][1]), "pcb_pack_protection.yaml, L4-E10 14b"),
        ("MAIN pressed", "an ordinary press asks the modules to shut down (PI_SHDN_REQ), then PI_KILL; held, the LTC2954 forces the kit off",
         "forced off after about %.1f s (%.1f to %.1f s)" % bh["main"], "HW-FW-CONTRACT FW-A10 to A12"),
        ("C1 at the inside air", "module shedding: normal to the reduced mode, then the heat stage; restores 5 K below",
         "inside air +%s C or any cell +%s C" % (fmt(cb["c1_air"]), fmt(cb["c1_cell"])), "CONOPS 4 via L4-E12 1f"),
    ]
    B["4e"] = [
        ("the vehicle entry's breaker", "%s / %s / %s A after %s / %s / %s ms" % (fmt(F["e_oc"][0]), fmt(F["e_oc"][1]), fmt(F["e_oc"][2]), fmt(F["e_oc_ms"][0]), fmt(F["e_oc_ms"][1]), fmt(F["e_oc_ms"][2])),
         "the vehicle source from VIN_RAW (Q7 off)", "retry every %s s" % fmt(F["e_retry_s"]), "L4-E11 3c"),
        ("the entry's short-circuit trip", "%s / %s / %s A filtered" % (fmt(F["e_sc"][0]), fmt(F["e_sc"][1]), fmt(F["e_sc"][2])), "the same", "retry every %s s; a hard short in service inside Q7's derated %s A only with the loop's inductance at least %s uH (OPEN, R-134)" % (fmt(F["e_retry_s"]), fmt(F["e_hs_svc"]["lim"]), fmt(F["e_hs_svc"]["l_uh"])), "L4-E11, out 12"),
        ("the entry's OV and UVLO", "off above %s / %s / %s V; off under %s / %s / %s V" % (fmt(F["e_ov_off"][0]), fmt(F["e_ov_off"][1]), fmt(F["e_ov_off"][2]), fmt(F["e_uv_off"][0]), fmt(F["e_uv_off"][1]), fmt(F["e_uv_off"][2])),
         "the vehicle source", "on again inside the window", "L4-E11 3c"),
        ("F1, the vehicle fuse", "the 0997010.WXN (58 V DC, drafted); a stiff source's fault at most %s A by the specified loop" % fmt(F["ipf_spec"]), "the vehicle lead", "replace the fuse", "part A, L4-E11 6"),
        ("the solar backstop", "trips at %s to %s A, inside %s ms after the filter" % (fmt(F["bs_trip"][0]), fmt(F["bs_trip"][1]), fmt(F["bs_allow_ms"])), "the panel (SWEN off)",
         "restarts through the stage's soft start", "L4-E7R"),
        ("F2, the panel fuse", F["e_f2"].split(":")[0], "the panel lead", "replace the fuse", "board E as drawn"),
        ("the front end's limits", "R11's average and R12's cycle-by-cycle limit (peak %s A, L1 at most %s A)" % (fmt(F["r12_peak"][0]), fmt(F["l1_peak"])), "nothing: they limit, no hiccup",
         "U34 cycles the front end when VIN_RAW falls", "L4-E4, L4-E6"),
        ("U18's outlet OCP", "%s to %s A" % (fmt(F["trip"][0]), fmt(F["trip"][1])), "the USB-C outlet", "the PD contract renegotiated", "L4-E4"),
        ("OUTLET_OK", "while the PA keys (a key-down at most %s s)" % fmt(bh["key"][0]), "both outlets", "on again when the key ends", "HW-FW-CONTRACT FW-A05, FW-A06"),
        ("the gauge's SCD and OCD", "SCD %s A; OCD1 %s A for %s s" % (fmt(F["scd"]), fmt(F["ocd1"][0]), fmt(F["ocd1"][1])), "the pack from VBAT (its FETs)", "the gauge's own recovery", "pcb_pack_protection.yaml"),
        ("the gauge's OCC", "%s A" % fmt(F["occ"]), "the charge path", "the gauge's own recovery", "pcb_pack_protection.yaml"),
        ("A F1, the pack fuse", "%s A" % fmt(F["a_f1"]), "the pack from VBAT", "replace the fuse", "board A as drawn"),
        ("F2 SCF9550, the BQ7720700", "the second level drives %s" % F["p_f2"].split(":")[0], "the pack, for good (a chemical fuse)", "none: the pack is replaced", "pcb_pack_protection.yaml"),
        ("BATOVP and SYSOVP", "BATOVP %s V; SYSOVP %.1f to %.1f V" % (fmt(F["batovp"]), F["sysovp"][0], F["sysovp"][2]), "U3's switching", "U3 resumes", "SLUSE66A via this record"),
        ("the charge FET opening mid-charge (a designed event)", "U3's voltage loop holds VBAT; BATOVP stops switching", "nothing: VBAT reaches %.3f V at a fifth of the capacitance (ASSUMPTION), under the TPS2596's %s V" % (D["pack_open"]["v_end"], fmt(F["tps2596_abs"])),
         "the charge resumes when the FET closes", "this record out 7"),
        ("the vehicle input reversed (-36 V)", "D10 does not conduct; the LM74700-Q1 and Q1 block", "Q1 sees %s V (the raised ceiling plus the reversed input) against the CSD19532Q5B's %s V (the drawn 60 V part fails: NOT MET as drawn)" % (fmt(D["q1_rev"]), fmt(F["csd19532_vds"])),
         "none needed", "part A (R-17, drafted)"),
        ("a disturbance (M2 CS101, M3 CS114, M7)", "the entry's OV stays off above CS101's peak at 36 V; the solar input stays under D4", "the OV minimum %s V; the solar input at most %s V; the backstop's filtered ripple %s A against %s A" % (fmt(F["e_ov_off"][0]), fmt(F["cs101_pv"]), fmt(F["m2_ripple"]), fmt(F["m2_margin"])),
         "no trip, no upset (CONDITIONAL on the loop's typical rows)", "part A, L4-E7R (D-01, D-02)"),
        ("a short behind F1 from a weak source", "F1's long-time band", "every element of the interconnect at least %s A continuous where installed (D-06, CONDITIONAL on the makers' ratings)" % fmt(F["d06_oblig"][0]),
         "replace the fuse", "L4-E11 6 (R-129 to R-132)"),
        ("U2's single faults (Q2 short, FB open)", "nothing: VBUS20 follows VIN_RAW past U3's %s V" % fmt(F["u3_abs"]), "no clamp on VBUS20", "S-111's decision is open (R-48)", "s120 11"),
        ("U5's regulation failing", "the backstop on SWEN", "trip at most %s A" % fmt(F["bs_trip"][1]), "the stage restarts; a fault defeating both is Layer 8's analysis (R-100)", "L4-E7R"),
        ("the panel lead's surge (CS116, CS115; D-12)", "D4 (the SMCJ30A, drafted) on PV_P under the drafted entry's %s V parts; with the block off D11 clamps the port" % fmt(F["sv"]["lim"]),
         "D4 at most %s V at CS116's %s A and %s V at CS115's %s A (hot end); a pulse over the cut-off turns the block off within %s us" % (fmt(F["sv"]["rm"]["d1d2"][0]), fmt(F["sv"]["d1"][1]), fmt(F["sv"]["rm"]["d1d2"][1]), fmt(F["sv"]["d2"][1]), fmt(F["sv"]["rm"]["t_off"])),
         "no trip; %s" % F["sv"]["rm"]["b6"]["d12"], "L4-E7 (D1, D2, the remedies, B6's round)"),
        ("the solar guard's over-voltage cut-off (D-10, a single fault: a stiff %s V source on the solar port)" % fmt(F["sv"]["src"][1]),
         "U21 (TPS48110-Q1) holds Q12 off: rising %s to %s V, falling %s V or more (aged); its UVLO on at %s V at most, under the stage's enable" % (fmt(F["sv"]["rm"]["rise"][0]), fmt(F["sv"]["rm"]["rise"][1]), fmt(F["sv"]["rm"]["fall"][0]), fmt(F["sv"]["rm"]["uvlo"][0])),
         "the panel port from PV_P: the block never turns on, Q12 holds %s of 100 V, D4 and the bulk see nothing" % fmt(F["sv"]["src"][1]),
         "on again once the input falls under the falling threshold (drafted, R-173, not applied)", "L4-E7 (the remedies, check 5)"),
        ("a stiff %s V source stepping onto the port with the guard already on (the review's B6; D-10)" % fmt(F["sv"]["src"][1]),
         "the short-circuit trip (C126 330 pF) or the OV path turns Q12 off: at most %s A within %s us; C131 and C132 (2 x 10 uF 100 V) take the lead's current, C133 and C134 (2 x 10 uF 50 V) the turn-off's charge on PV_P"
         % (fmt(F["sv"]["rm"]["b6"]["sum"][0]), fmt(F["sv"]["rm"]["b6"]["sum"][1])),
         "the port from PV_P: PV_F at most %s V (slew %s V/us), PV_P %s V, TRK_VS %s V: D4 carries nothing; U5 at most %s of 0.3 V"
         % (fmt(F["sv"]["rm"]["b6"]["sum"][2]), fmt(F["sv"]["rm"]["b6"]["sum"][3]), fmt(F["sv"]["rm"]["b6"]["sum"][4]), fmt(F["sv"]["rm"]["b6"]["sum"][5]),
            fmt([r[1] for r in F["sv"]["rm"]["b6"]["rows"] if r[0] == F["sv"]["rm"]["b6"]["bind"]][0])),
         "on again under the falling threshold; CONDITIONAL on the panel lead's loop inductance at least %s uH (R-176 row 2, R-180), NOT MET at %s uH"
         % (fmt(F["sv"]["rm"]["b6"]["l_uh"]), fmt(F["sv"]["rm"]["b6"]["below"][0])), "L4-E7 (THE GUARD ALREADY ON, B6)"),
        ("a reversed panel (D-11, a single fault)", "Q13 in the return stays off, its body diode reverse biased", "the reversed panel: no current; the high side within 1 V of GND",
         "none needed (drafted, R-173; CONDITIONAL on Q13's leakage above +25 C)", "L4-E7 (the remedies); DECISION-31 E-N1 closed"),
        ("a stiff source between %s V and the cut-off (the residual band, R-175)" % fmt(F["pv"]["v_max"]), "nothing at the entry: the backstop's current trip only",
         "the stage runs, at most %s W, outside REQ-016's window" % fmt(F["sv"]["rm"]["resid"]), "layer 8's TRN-001 judgement (R-175)", "L4-E7 (the remedies)"),
    ]
    B["4f"] = [
        ("the margin hold (E5)", "off board D, the PA rail, the RockBLOCK, the LoRa module, both E72 and the Geiger module; the running module idled; the charge held",
         "trigger %s C of mixed air plus the calibrated offset (the reference within +-%s K); restore %s K under after %s minutes (PROVISIONAL)" % ("%.2f" % bh["hold_trig"], F["hold_ref"], fmt(bh["hold_restore"][0]), fmt(bh["hold_restore"][1])),
         "L4-E12 6 (R-138, R-139)"),
        ("C1, module shedding", "normal to the reduced mode, reached again to the heat stage", "inside air +%s C or any cell +%s C; restores 5 K below" % (fmt(cb["c1_air"]), fmt(cb["c1_cell"])), "CONOPS 4"),
        ("the SGP41's own shutdown", "its load switch from board E's controller; under CFL-002's option C its VOC channel is reported not covered above a %.1f C reading (sensing supported to Table 4's +50 C only; Table 5's +55 C an absolute rating, a screen)" % F["fx"]["c_cover"],
         "off at %.1f C on the TMP117, used at or under %.1f C; the lag assumed 61 s (R-139, restated)" % (F["sgp_off"], F["sgp_on"]), "L4-E12 6, 12a"),
        ("the pack heater", "the mat on U22/U33 at 12.0 V; UTC holds the charge FET until the block warms", "warm before charge below %s C at the cell; %s Wh to T1 from -20 C (the HL18650V class)" % (fmt(bh["heat_below"]), r5["warm"][0][3]),
         "FW-A13, L4-E10 14b"),
        ("the fans", "two mixers on board E from the inside climate (under (B1) on VSYS_E, up to %s V: their maximum supply voltage owed, E11-35); each running slot's cooler; a stalled fan reported" % fmt(F["fx"]["vsys_rng"][1]), "the hold's 2 fans %.3f W; a stall reported within %s s; with the fans stopped E5's air %s to %s C" % (cb["fans_e5"], fmt(bh["fan_rep"]), r5["stop"][0], r5["stop"][1]),
         "FW-E07, V-E07, L4-E12 8b"),
        ("the PA's key-down", "the K rules and OUTLET_OK", "at most %s s a key-down, %s s apart; gates at +%s C cells, +%s C air, +%s C flange" % tuple(fmt(x) for x in bh["key"]), "FW-A05, D-11 (PROVISIONAL)"),
    ]
    B["4g"] = [
        ("the panel controller (C:U3)", "the charger falls back after its %s s watchdog (as drawn to 256 mA; under (B1) to 0 A); the H3 line, U34, the entry, the backstop, OUTLET_OK, the eFuses, BATOVP and SYSOVP; the RP2040's own watchdog restarts it" % fmt(bh["chg_wd"]),
         "the margin hold (E5's +70 C class goes unprotected); the key-down time limit (OUTLET_OK still drops the outlets); the expanders keep their last outputs", "HW-FW-CONTRACT FW-A03, FW-A05, FW-A08; L4-E12"),
        ("the sensor controller (E:U10)", "the gauge stops charging after its host watchdog's %s s; the gauge's protections and the second level act alone; the RP2040's watchdog restarts it" % fmt(bh["hwd"]),
         "the mixer fans' control (a stopped fan is the fans-off case, %s to %s C in E5); VIN_MON for FW-A16's diagnostic; the SGP41's switch" % (r5["stop"][0], r5["stop"][1]), "HW-FW-CONTRACT FW-E01, FW-E07, FW-E09"),
        ("both controllers", "every hardware limit of 4e acts; the source bound holds with no firmware (the H3 line and the knee)", "the charge ranges relayed from the gauge (UTC still holds the charge FET); the hold; the heater's policy",
         "this record out 7"),
        ("the gauge's own firmware", "the BQ7720700 and F2 (hardware)", "COV, CUV, OCD, SCD and the temperature limits, which are the gauge's", "pcb_pack_protection.yaml"),
    ]
    return B


def cons_behaviour_lines(F, D, st):
    B = cons_behaviour(F, D, st)
    L = ["18. THE OPERATING BEHAVIOUR (one table per item; each row tied to a record and a figure read above)"]
    names = {"4a": "source changes", "4b": "simultaneous operation", "4c": "startup", "4d": "shutdown", "4e": "faults: each trip, what it isolates, the recovery",
             "4f": "thermal management", "4g": "control dependencies: what still acts if the firmware stalls"}
    for key, _h, _hh in BEH_HEAD:
        L.append("%s %s" % (key, names[key].upper()))
        for r in B[key]:
            L.append("   %s: %s" % (r[0], " | ".join(r[1:])))
    return L


def cons_behaviour_tables(F, D, st):
    B = cons_behaviour(F, D, st)
    T = {}
    for key, start, head in BEH_HEAD:
        n = head.count("|") - 1
        T[start] = [head, "|" + "---|" * n] + ["| %s |" % " | ".join(r) for r in B[key]]
    return T


# THE IMPLEMENTATION HANDOVER: the selected parts with their document revisions (each revision checked on the pinned file
# that prints it), and every register row grouped by the later layer that receives it, drafted or applied.
PARTS = [
    ("U5", "LT8705AIUHF#PBF", "the solar stage: hold, regulation RIMON_IN 31.6k, backstop on SWEN", "8705af", "l4e7r", "DRAFTED (R-12, R-19 to R-21, R-98)"),
    ("U6, Q7", "TPS48110-Q1 with CSD19536KTT", "the vehicle entry's breaker and its pass FET", "SLUSEE5E", "l4e11", "DRAFTED (R-123)"),
    ("U21, Q12 (board E)", "TPS48110AQDGXRQ1 with CSD19532Q5B", "the solar guard's over-voltage cut-off (off above 28.55 to 31.06 V) and its FET", "SLUSEE5E", "l4e7r", "DRAFTED (R-173); U21's DGX-19 land owed"),
    ("Q13 (board E)", "CSD19532Q5B", "the solar guard's return switch (a reversed panel blocked)", "SLPS414B", "csd19532", "DRAFTED (R-173); its leakage above +25 C CONDITIONAL"),
    ("D4 (board E)", "SMCJ30A", "the solar entry's clamp, from the SMCJ28A", "SMCJ30A", "smcj", "DRAFTED (R-173); its LCSC code owed"),
    ("D11 (board E)", "SMCJ40CA", "the solar port's two-way clamp", "SMCJ40CA", "smcj", "DRAFTED (R-173)"),
    ("Q7's sheet", "CSD19536KTT", "the pass FET's safe operating area", "SLPS540C", "l4e11", "DRAFTED (R-123)"),
    ("Q1", "CSD19532Q5B", "the ideal diode's FET, 100 V", "SLPS414B", "csd19532", "DRAFTED (R-17)"),
    ("U3 (board E)", "LM74700-Q1", "the vehicle entry's ideal-diode controller", "SNOSD17G", "lm74700", "as drawn"),
    ("U2", "LM5176", "the front end to VBUS20", "SNVSAI1D", "lm5176", "as drawn; R11, R12 DRAFTED (R-04, R-01)"),
    ("U3 (board A)", "BQ25731", "the charger onto VBAT = VSYS, as drawn", "SLUSE66A", "bq25731", "as drawn; replaced in (B1) by the BQ25730 (R-157)"),
    ("U3 (board A), (B1)", "BQ25730RSNR", "the selected charger: VSYS bounded in all three modes; BATDRV on pin 21", "SLUSE65A", "l4e11", "DRAFTED (R-157), not applied; LCSC stock 0 (R-162)"),
    ("Q39, Q40 (board A), (B1)", "Nexperia BUK6Y10-30PX, two in parallel", "the battery FET pair between VBAT and CH_BATQ (L4-E11's fix round; the AONS21357 replaced)", "2020-04-17", "l4e11",
     "DRAFTED (R-157); each FET's installed path R-159 (at most 34.42 C/W), the docking split R-160, the supply R-162"),
    ("U17 and five more", "INA226", "the rail monitors; U17 moved onto R227", "SBOS547C", "ina226", "DRAFTED (R-06)"),
    ("eFuses", "TPS2596", "the load converters' inputs, 21 V absolute", "SLVSET8A", "tps2596", "as drawn"),
    ("U1 (board P)", "BQ4050", "the pack's gauge and its FETs", "SLUUAQ3A", "l4e11", "as drawn; U-01's (II) re-derives it (R-106)"),
    ("U2 (board P)", "BQ7720700", "the second-level protector", "BQ7720700", "gen_p", "as drawn; BQ7720704 under U-01's (II) (R-105)"),
    ("F2 (board P)", "SCF9550-30-05", "the self-control fuse", "SCF9550-30-05", "gen_p", "as drawn; Eaton's statement owed (R-103)"),
    ("F1 (board E)", "Littelfuse 0997010.WXN", "the vehicle fuse, 58 V DC", "rev2025-11-18", "fuse997", "DRAFTED (R-18), its 20 A holder owed (R-132)"),
    ("the bank", "Panasonic EEHZK1V331P with HoJLR2512 45 mOhm", "VBUS20's six cans and their ballasts", "EEHZK1V331P", "l4e8", "DRAFTED (R-07)"),
    ("the cells", "Samsung INR18650-35E, 4S3P", "D-06's ruled cell", "INR18650-35E", "packprot", "as ruled (144.72 Wh nominal, 107.9 Wh, 2.52 h energy only); the Saft MP 176065 xtd 4S1P a PROPOSAL compared in 2b' (81.76 Wh nominal, 53.5 to 58.8 Wh, 1.25 to 1.37 h energy only, MODELLED): supported for the temperature windows, not yet adoptable (current at temperature and the storage dwell AWAITING, L4-E10 10g), the owner's approval required; the HL18650V a PROPOSAL (U-01)"),
    ("the alternative only", "LM5069", "the drawn hot swap, kept only as the alternative", "SNVS452G", "lm5069", "superseded by R-123"),
]
LAYER_OF = {"Layer 4 coordinator": "4 (release records)", "Layer 5 interfaces": "5", "CONOPS owner": "5", "firmware owner": "5 (firmware, by the contract)",
            "Layer 6 components": "6", "Layer 7 mechanical": "7", "Layer 8 board A generator owner": "8", "Layer 8 board B generator owner": "8",
            "Layer 8 board C generator owner": "8", "Layer 8 board E generator owner": "8", "Layer 8 board P generator owner": "8",
            "Layer 9 pre-layout analysis": "9", "prototype bench": "9 (the bench)", "TEST-PLAN owner": "9 (the test plan)"}


def cons_parts(F):
    out = []
    for ref, part, role, rev, key, state in PARTS:
        txt = pdf_text(key, 1, 2) if PINS[key][0].endswith(".pdf") else (_C_TEXT[key] if key in _C_TEXT else "")
        where = PINS[key][0]
        if key in ("fuse997",):
            txt = where
        if rev not in txt:
            refuse(4, "%s's revision %s is not printed by %s" % (part, rev, where))
        out.append((ref, part, role, rev, os.path.basename(where), state))
    return out


def cons_handover(reg):
    layers = {}
    for r in reg:
        lay = LAYER_OF.get(r[4])
        if lay is None:
            refuse(4, "register owner %s has no later layer" % r[4])
        d = layers.setdefault(lay, {"owners": [], "rows": [], "kinds": {}, "states": {}})
        if r[4] not in d["owners"]:
            d["owners"].append(r[4])
        d["rows"].append(r[0])
        d["kinds"][r[1]] = d["kinds"].get(r[1], 0) + 1
        d["states"][r[6]] = d["states"].get(r[6], 0) + 1
    rows = []
    for lay in sorted(layers, key=lambda x: (x[0], x)):
        d = layers[lay]
        rows.append((lay, ", ".join(d["owners"]), "%d: %s" % (len(d["rows"]), ", ".join(d["rows"])),
                     "; ".join("%s %d" % (k, d["kinds"][k]) for k in sorted(d["kinds"])),
                     "; ".join("%s %d" % (k, d["states"][k]) for k in sorted(d["states"])) + "; APPLIED 0"))
    return rows


def cons_th1(F):
    """T-H1's points at Layer 9 (R-104): the points of L4-E12 12d, one per mode's heat and lid state, each read against its mode's
    governing line as ruled and under CFL-002's C (12a); the fans-off case and 12c's transient point after them. A point closes only
    the conductance it reads."""
    fx, rc = F["fx"], F["rc"]
    H = rc["H"]
    rows = []
    for name, q, lid, txt, tau, steady, fit in fx["pts"]:
        m0 = name.split(" ")[0]
        ht, fan = H[m0][1], H[m0][2]
        rows.append((name, "lid %s; the heaters %s W plus the fans' %s W (P %s W); room air; tau %s h, steady at %s h, the fit's three time constants %s h"
                     % (lid, fmt(ht), fmt(fan), fmt(q), tau, steady, fit), txt,
                     "the conductance for this heat and lid state only; the modes' functions, the cells' rise, the parts' local air and the junctions keep their own evidence (U-01, T-H2, THM-001)",
                     "L4-E12 12d, 12a"))
    rows += [
        ("the route, only under a class (ii) line", "the same point with the combined route fitted (R-170 to R-172; lid open only)", "the point's own line",
         "the route's effect at that heat; still short, the line joins the owner's (OW-10)", "L4-E12 12e, 15"),
        ("the fans-off case", "at M2's heat, the fans stopped", "no pass line (the failure case)", "what a stopped fan costs (L4-E12 8e)", "L4-E12 12d"),
        ("the transient point (12c)", "the empty case soaked at room temperature; the heaters stepped to %s W, then, once the mixed air has risen %d K, to %s W, logged to the run's end"
         % (fmt(fx["trans"][0]), int(fx["trans"][1]), fmt(fx["trans"][2])), "the time to C1 and the air after it",
         "the battery-only run's shed point on the bench (the empty case's thermal mass under the kit's: the conservative side); then the built kit's run (Layer 9)", "L4-E12 12c"),
        ("open after the points", "none on this bench", "none",
         "the four class (iii) lines (no reading passes them: OW-10); the cells' rise in the pocket (U-01), the parts' local air (T-H2), the junctions (THM-001), the fans' rating (D-18), full sun (D-02e)", "L4-E12 12a, 12e"),
    ]
    note = ("**T-H1 at Layer 9 (the bench, R-104): the points of L4-E12 12d, one per mode's heat and lid state** (the fix round; "
            "the order K1, K5, K10, K6, K7 and K8 of section 11 superseded). Each point runs at its mode's heat with the heaters set to it "
            "less the fans' measured draw (P = the heaters + the fans), and its reading is judged against the mode's governing line as "
            "ruled and under CFL-002's C (2c). It is a dummy-load, mixed-air measurement: it establishes the conductance between the mixed "
            "air and the ambient for its own configuration and closes no mode's function. Lid-closed and fans-off states have their own "
            "points. Authorising the bench is the owner's (OW-8); accepting a result goes through the coordinator's check.")
    return rows, note


def cons_handover_lines(F, reg):
    L = ["19. THE IMPLEMENTATION HANDOVER (the selected parts with their revisions; every register row by the later layer that receives it)"]
    for p_ in cons_parts(F):
        L.append("   %s: %s, %s; document %s (%s); %s" % p_)
    for r in cons_handover(reg):
        L.append("   layer %s (%s): %s; by kind %s; by state %s" % r)
    L.append("   the interface limits for Layer 5: LAYER5-HANDOVER.md LH-01 to LH-11 (drafts; pcb_interfaces.yaml and HW-FW-CONTRACT.md are not edited)")
    rows, note = cons_th1(F)
    L.append("   " + note.replace("**", ""))
    for r in rows:
        L.append("     %s: %s; the reading %s; %s (%s)" % r)
    return L


def cons_handover_tables(F, D, st):
    reg = md_table(open(os.path.join(HERE, "DOWNSTREAM-REGISTER.md"), encoding="utf-8").read(), "| ID | Kind |")
    T = {"| Ref | Part |": ["| Ref | Part | Role | Document revision | Read from | State |", "|---|---|---|---|---|---|"] + ["| %s | %s | %s | %s | %s | %s |" % p_ for p_ in cons_parts(F)],
         "| Layer | Owners |": ["| Layer | Owners | Register rows | By kind | By state |", "|---|---|---|---|---|"] + ["| %s | %s | %s | %s | %s |" % r for r in cons_handover(reg)],
         "| T-H1 point |": ["| T-H1 point | Configuration | The reading | Settles | Read from |", "|---|---|---|---|---|"] + ["| %s | %s | %s | %s | %s |" % r for r in cons_th1(F)[0]]}
    return T


OWNER_DEFINITION = ("Layer 4 power closure requires a selected architecture whose mandatory operating requirements have a defensible feasibility "
                    "basis, consistent interfaces, and explicit implementation obligations. A downstream qualification test may remain open where the "
                    "design already has bounded supporting evidence and a workable fallback. An unknown that could invalidate the selected "
                    "architecture stays a closure condition.")
QUALIFICATION = "(i) a downstream qualification test with bounded evidence and a workable fallback"
CONDITION = "(ii) a closure condition"
QUALIFICATION_ONCE = "(i) once R-157, R-177 and R-178 are applied ((B1) with the battery FET pair and board E on VSYS_E); (ii) on the board as drawn"
SUPPORTED = ("(ii) as ruled (the 35E unsuitable on its own published evidence); a route supported on published evidence for the temperature windows "
             "(the Saft MP 176065 xtd), NOT YET ADOPTABLE: current at temperature and the storage dwell and recovery await Saft or the limited sample "
             "qualification, the fit the mock-up; the owner's approval required")
CONDITION_U02 = ("(ii) a closure condition for every class (i) and (ii) line, T-H1 deciding; four class (iii) lines (E3-L lid closed as ruled, E3-O "
                 "and E5 on the e-paper's row) are a contradiction between the rulings and those requirements that no measurement resolves: the owner's (OW-10)")
EXIT_PENDING = {"U-01": "integrated: L4-E10's cell route (checks 4 and 5 at 1c321773) and its fix round for the review's B5 (ee09aa09: the temperature windows supported, not yet adoptable)",
                "U-02": "integrated: L4-E12's verdict, heat-rejection comparison and reconciliation (checks 5 to 7) and its fix round for the review's B3, B4 and B7 (b1cd32ba: each mode's governing local limit, the classes of 12e)",
                "U-04": "integrated: L4-E11's charger selection (check 5 at 5aa18a69) and its fix round for the review's B1 and B2 (656fc540: the battery FET pair, board E on VSYS_E)"}


def cons_exit(F):
    """The exit statement per architecture-level choice, on this record's reading with the consolidation's results and the fix round
    of the Layer 4 review integrated."""
    r5, cb, fx = F["r5"], F["cb"], F["fx"]
    tb, b1, u1 = cb["tb"], cb["b1"], cb["u1"]
    rc = F["rc"]
    M = fx["modes"]
    sh = {c["mode"]: c["short"] for c in fx["iii"]}
    c40 = [c for c in fx["cls"] if c["mode"] == "M1"][0]
    c40c = [c for c in fx["cls"] if c["mode"] == "M3"][0]
    return [
        ("U-01", SUPPORTED,
         "with the ruled 35E, LO-01d to LO-01g UNSUITABLE on its own published evidence (E3-O's cells %s to %s C over +60 C; E5's idle pack %s C; +71 C and -33 C storage); with the Saft MP 176065 xtd: the current at temperature (10 A continuous, 18 A for 60 s and the gauge's 20 A for 2 s on one string at the modelled cells, -20 to +80 C; its %s A and %s A 'Can vary depending on temperatures', footnote 2), the storage dwell and recovery, whether four cells fit along the pocket's axis with at most %.2f mm of wrap, and T-H1 for LO-01a's complete pass and LO-01e"
         % (u1["e35_e3o"][0], u1["e35_e3o"][1], u1["e35_e5"], fmt(u1["sheet"][3]), fmt(u1["sheet"][4]), u1["wrap"][0]),
         "Saft's statement (the request expanded after the review's B5; drafted, the owner sends: OW-9), or the limited sample qualification in its place (L4-E10 10g: one cell, a chamber from -40 to +85 C, a 25 A load, about two weeks, NZ$ %s; R-168); a printed mock-up of four cells (hours, no purchase; R-167); T-H1 (R-104); for the higher-energy HL18650V its signed specification or a lot soak (USD %s, %s to %s days)"
         % (fmt(u1["pulse_cost"]), "%.2f" % u1["soak"][0], fmt(u1["soak"][1]), fmt(u1["soak"][2])),
         "Saft's published datasheet supports the temperature windows of every cell-limit row (charge -30 to +85 C, discharge -40 to +85 C, storage allowable -40 to +85 C), not current and temperature together; L4-E10's comparison (check 6): %s Wh nominal against the 35E's %s Wh, %s to %s Wh usable and %s to %s h battery-only, energy only, against %s Wh and %s h (MODELLED: Saft prints no curve)"
         % (fmt(rc["saft_nom"]), fmt(rc["e35_nom"]), fmt(rc["saft_use"][0]), fmt(rc["saft_use"][1]), fmt(rc["saft_use"][2]), fmt(rc["saft_use"][3]), fmt(rc["e35_use"][0]), fmt(rc["e35_use"][1])),
         "the HL18650V (90.2 Wh usable) on its specification or a soak; with no approval U-01 stays a release gate; (I)'s powered cooling is INCONCLUSIVE (%s to %s W into the sealed case)" % r5["cooler"],
         "the owner's adoption of D-06's cell, energy (%s to %s Wh nominal) and spend (NZ$ %s for four), NOT YET ADOPTABLE: current at temperature, the storage dwell and recovery, the fit, the gauge data and T-H1 awaited, the owner's approval required; the topology stays; missing evidence is not proof that no cell meets the rows"
         % (fmt(rc["e35_nom"]), fmt(rc["saft_nom"]), fmt(u1["cost"][1]))),
        ("U-02", CONDITION_U02,
         "the sealed case's conductance with the fans, lid open and lid closed, at each required mode's heat against that mode's governing local limit (L4-E12 12a): as ruled the SGP41's Table 4 in the heat stage at +40 C (%s W/K on the pack, %s W/K on shore), under CFL-002's C, A or B the cells' hot stop H1 (%s and %s W/K); M5, C1's air trigger, %s W/K; M8 and M9, T4 on the charging cells, %s and %s W/K; the four class (iii) lines need a decision, not a reading"
         % (M["M1"]["ruled"][1], M["M2"]["ruled"][1], M["M1"]["cab"][1], M["M2"]["cab"][1], M["M5"]["ruled"][1], M["M8"]["ruled"][1], M["M9"]["ruled"][1]),
         "T-H1's points of L4-E12 12d (R-104, R-151): M2 and M6 at %s W lid open first (the heaters %s W plus the fans), then M1, M4 and M3 lid closed, M7, M5, M8 and M9, the fans-off case and the transient point; under a class (ii) line the combined route (R-170 to R-172) read at the same point; the e-paper's window temperature as a T-H1 channel; PDi's and Sensirion's statements (OW-4); CFL-002 (OW-1); one option per class (iii) line (OW-10); OW-8 authorises the bench"
         % (fmt(M["M2"]["q"]), fmt(rc["H"]["M2"][1])),
         "the conservative bound (%s to %s W/K at K1's rise; the fans' film at zero); the outside capacity with the inside resistance at zero (12e; %s W/K at K1's rise): at +40 C lid open bare %s / %s, with the route %s / %s W/K, lid closed %s / %s W/K (conservative / optimistic): every line class (i) or (ii) but four, M3 short by %s W/K (%s W), M4 by %s W/K (%s W), M6 by %s W/K (%s W), M7 the whole %s W; the charging heat %s W (12b, the balance); the battery-only run sheds at C1 at %s to %s h on the bound (12c)"
         % (fmt(rc["bound"][0]), fmt(rc["bound"][1]), "%.3f" % rc["capk1"][0], c40["bare"][0], c40["bare"][1], c40["route"][0], c40["route"][1], c40c["bare"][0], c40c["bare"][1],
            sh["M3"][0], sh["M3"][1], sh["M4"][0], sh["M4"][1], sh["M6"][0], sh["M6"][1], sh["M7"][1], fmt(fx["bal_b"][1]), fmt(fx["c1"][0]), fmt(fx["c1"][1])),
         "under a class (i) or (ii) line, the combined route (R-170 to R-172, passive); for the class (iii) lines the session's two options (the e-paper's window temperature: a plate fraction of %s needs %s W/K, %s needs %s W/K; a closed-lid conduction path at Layer 7, not modelled, closing nothing yet) and the owner's (CFL-002's C, A or B; a closed-lid ceiling on REQ-042's VOC channel, +%s to +%s C on the pack and +%s to +%s C on shore; D-02b restated; PDi's statement; CHO-001; a recorded deviation)"
         % (tuple(fmt(x) for x in fx["plate"]) + tuple(fmt(x) for x in fx["voc_ceil"])),
         "at or over each class (i) or (ii) line's reading the architecture stands for that mode (with the route where needed); the class (iii) lines are a contradiction between the rulings (no vent, the Peli 1450, the device set) and E3-L lid closed, E3-O and E5 as stated, the owner's to resolve (OW-10); never the power path's topology; T-H1 decides, it does not merely confirm; missing evidence is not proof of a shortfall"),
        ("U-04", QUALIFICATION_ONCE,
         "with (B1): D2 (load steps against the %s V margin), each FET's installed path (at most %s C/W at the +70 C mixed air, E11-29), the docking pulse's split on the pair (a share of at most %s hot, E11-30), the start from cold into VSYS_MIN and the held pack current (E11-31), the fans' rating to %s V (E11-35), D6, D8, D9, D10 and the BQ25730's supply; on the board as drawn, TI's D1 and D3"
         % (b1["margin"], fmt(fx["bar"][0]), fmt(fx["dock"][2]), fmt(fx["vsys_rng"][1])),
         "apply R-157, R-177 and R-178 (after L4-E11's release record); then the three modes, the held pack current, the start and D2 on one build (R-161), each FET's case rise at 10 A against the layout's path (R-159), the docking split on the pair (R-160); Q-TI-15 and Q-TI-16 sent (OW-7; Q-AOS-1 withdrawn)",
         "SLUSE65A bounds VSYS: at least %s V with no pack; inhibited, piecewise (VSRN + %d mV within +-%d %% over %s V, at least %s V under %s V, at least %s V between); the system node %s to %s V; the pair %s W at the profile, every protection event at TJ 150 C or under at the bar, 18 A for 60 s at %s C; the start bounded to VSYS_MIN or a latch within %s s; the held pack's drains %s mA"
         % (b1["vsys_min"], b1["inhib"][0], b1["inhib"][1], fmt(fx["pw"][2]), fmt(fx["pw"][1]), fmt(fx["pw"][0]), fmt(fx["pw"][3]), fmt(fx["vsys_rng"][0]), fmt(fx["vsys_rng"][1]),
            fmt(fx["pair_idle"][1]), fmt(fx["svc_tj"]), fmt(fx["latch_s"]), fmt(fx["held"][0])),
         "R-c's step rule (D2); the pair's copper for the bar, never a lowered protection or service; the diode paths matched by layout or Nexperia's hot ISM (the docking pulse); arrangement (A) with E11-24's hold-up if (B1) fails",
         "once R-157, R-177 and R-178 are applied, nothing of the architecture (L4-E11 check 5 and its fix round); on the board as drawn TI's D1 and D3 decide the charger's power path"),
    ]


def cons_deciding(F):
    """The top of the exit statement, on L4-E12's fix round for the review's B3, B4 and B7 (12a to 12e): the SGP41 and option C as
    defined, each required mode's governing local limit, which lines a reading can pass at all, and the resolution path. The earlier
    framings (the profile at +40 C; K1, the SGP41's +55 C, deciding under option C) are withdrawn."""
    fx, rc = F["fx"], F["rc"]
    M = fx["modes"]
    sh = {c["mode"]: c["short"] for c in fx["iii"]}
    g = lambda k, w: "%s W/K (a reading of at least %s W/K)" % M[k][w][1:]
    return [
        "**The thermal question (U-02), restated by L4-E12's fix round for the review's B3, B4 and B7 (`b1cd32ba`).** The SGP41's "
        "sensing is supported to +50 C only (Table 4); its +55 C (Table 5) is an absolute rating, an exclusion screen that never stands "
        "in for the sensor's function. The earlier statement that option C keeps the SGP41 powered with its +55 C as the deciding line "
        "(K1, %s W/K) is WITHDRAWN: K1 and K5 are screens. Option C as defined reports the VOC channel not covered above a %.1f C "
        "reading and switches the sensor off at %.1f C. At REQ-024's +40 C the required state is the heat stage (C1 sheds the %s W "
        "profile; D-02b runs the reduced mode above +35 C), and each required mode has its own governing LOCAL limit: the cells at the "
        "air plus their own I2R, the control thresholds that end or shed the mode, the parts at their local air with the cooler's "
        "exhaust, the junctions and the unpowered parts' storage rows (2c)."
        % (rc["K"]["K1"]["need"], fx["c_cover"], fx["c_off"], fmt(F["idle"][1])),
        "**The governing lines** (with the route's measures; as ruled, then under CFL-002's C, A or B): M1 and M3, the heat stage on "
        "the pack, lid open and closed, %s W: the SGP41's Table 4, %s; the cells' hot stop H1, %s. M2 and M4, on shore, %s W: %s; the "
        "idle cells' H1, %s. M5, REQ-014's profile at +20 C, %s W: C1's air trigger, %s. M6, E3-O at +55 C, %s W: the e-paper's "
        "+60 C operating row read to cover it unpowered (INFERRED), %s; once PDi states its range, the RB9704's +70 C, %s. M7, E5's "
        "+60 C dwell, %s W: the e-paper, no conductance; then the LimeSDR's +70 C storage row, %s. M8 and M9, charging on the design "
        "day, %s W (the balance of 12b): T4 on the charging cells, %s and %s. A T-H1 point is a dummy-load, mixed-air reading: it "
        "closes the conductance it reads and no mode's function."
        % (fmt(M["M1"]["q"]), g("M1", "ruled"), g("M1", "cab"), fmt(M["M2"]["q"]), g("M2", "ruled"), g("M2", "cab"), fmt(M["M5"]["q"]), g("M5", "ruled"),
           fmt(M["M6"]["q"]), g("M6", "ruled"), "%s W/K (a reading of at least %s W/K)" % M["M6"]["stated"][1:], fmt(M["M7"]["q"]),
           "%s W/K (a reading of at least %s W/K)" % M["M7"]["stated"][1:], fmt(M["M8"]["q"]), g("M8", "ruled"), g("M9", "ruled")),
        "**Which lines a reading can pass at all** (12e: the outside capacity with the inside resistance at zero, %s W/K at K1's "
        "rise, correcting the %s to %s W/K that were a bound with a 50 m/s inside flow). Every line is class (i) (reachable bare: T-H1 "
        "decides) or (ii) (reachable with the combined route R-170 to R-172: T-H1 with the route decides), except **four class (iii) "
        "lines**, over the capacity even with the route at the optimistic ends: **M3**, E3-L lid closed on the pack as ruled, short by "
        "%s W/K (%s W); **M4**, on shore, %s W/K (%s W); **M6**, E3-O on the e-paper's row, %s W/K (%s W); **M7**, E5's dwell on the "
        "e-paper's row, the whole %s W. No measurement can pass them: each is a contradiction between the rulings (no vent, the Peli "
        "1450, the device set) and that mode's requirement, with its options (OW-10): E3-L, CFL-002's C, A or B (the line moves to H1, "
        "class (i)), a closed-lid ceiling on REQ-042's VOC channel (+%s to +%s C ambient on the pack, +%s to +%s C on shore) or D-02b "
        "restated; E3-O, PDi's statement (the +70 C class, class (i)), the e-paper's window temperature measured (a plate fraction of "
        "%s needs %s W/K, %s needs %s W/K), CHO-001 or a recorded deviation; E5, PDi's statement (%s W/K, class (i)), a different e-paper "
        "or a recorded deviation. **Its executable resolution path:** the owner rules CFL-002 (OW-1), picks an option per class (iii) "
        "line (OW-10) and authorises T-H1 (OW-8); the bench runs 12d's points (R-104, 5c)."
        % ("%.3f" % rc["capk1"][0], "%.3f" % rc["cap"][0], "%.3f" % fx["capfix"][1], sh["M3"][0], sh["M3"][1], sh["M4"][0], sh["M4"][1], sh["M6"][0], sh["M6"][1],
           sh["M7"][1], *[fmt(x) for x in fx["voc_ceil"]], *[fmt(x) for x in fx["plate"]], M["M7"]["stated"][1]),
    ]


def cons_exit_lines(F):
    L = ["20. THE EXIT STATEMENT (the owner's definition, quoted; each U on this record's reading, the consolidation's results integrated)"]
    for s in cons_deciding(F):
        L.append("   " + s.replace("**", ""))
    L.append("   the definition: %s" % OWNER_DEFINITION)
    for u, cls, fact, exp, ev, fb, ov in cons_exit(F):
        L.append("   %s: %s (%s)" % (u, cls, EXIT_PENDING[u]))
        for lab, x in (("the exact missing fact", fact), ("the smallest resolution", exp), ("the bounded evidence today", ev), ("the fallback", fb), ("what it decides", ov)):
            L.append("      %s: %s" % (lab, x))
    L.append("   the known defects beside them (L4-E7's derivation, set 27):")
    for d in cons_exit_defects(F):
        L.append("      %s %s: %s; the missing step: %s; the evidence still needed: %s; what it decides: %s" % d)
    L.append("   " + cons_ledger(F).replace("**", "").replace("`", ""))
    n = [e[0] for e in cons_exit(F) if e[1] != QUALIFICATION]
    L.append("   the exit: Layer 4 power closure is NOT reached on this reading: closure conditions on the board as drawn %s (U-04 becomes a qualification test once R-157, R-177"
             " and R-178 are applied; U-02's four class (iii) lines are the owner's); the review's B1 and B2 on (B1)'s draft, D-13 and D-14, and the known defects D-10 and"
             " D-11 at the solar entry are addressed in drafts (R-157, R-177, R-178 and R-173, not applied; D-11 CONDITIONAL on Q13's hot leakage), the band"
             " between 25 V and the cut-off a residual for layer 8 (R-175); status: %s" % (", ".join(n), STATUS))
    return L


def cons_exit_table(F, D, st):
    return {"| U | Class |": ["| U | Class | The exact missing fact | The smallest experiment or manufacturer clarification | The bounded evidence today | The fallback | What it decides | The result |",
                              "|---|---|---|---|---|---|---|---|"] + ["| %s | %s | %s | %s | %s | %s | %s | %s |" % (e + (EXIT_PENDING[e[0]],)) for e in cons_exit(F)],
            "| Defect | Its fault |": ["| Defect | Its fault | State | The missing step | The evidence still needed | What it decides |", "|---|---|---|---|---|---|"]
            + ["| %s | %s | %s | %s | %s | %s |" % d for d in cons_exit_defects(F)]}


def cons_results_lines(F):
    """The consolidation's two accepted results as this record reads them (each figure from its pinned output)."""
    b1, tb = F["cb"]["b1"], F["cb"]["tb"]
    u1 = F["cb"]["u1"]
    L = ["22. THE CONSOLIDATION'S RESULTS (L4-E11's charger selection, check 5 at 5aa18a69; L4-E12's thermal verdict, check 5 at 7f41632d;"
         " L4-E10's cell route, check 5 at 1c321773; L4-E12's heat-rejection comparison, check 6 at 589f18ac; as accepted then, the fix round's corrections"
         " in section 25)"]
    p = L.append
    p("   U-04, (B1) as check 5 accepted it: TI's BQ25730 with the battery FET Q39 (AOS AONS21357), drafted in apply_gen_sch_a_charger.py (R-157), not applied;")
    p("     the fix round (section 25) replaces Q39 by the pair Q39 and Q40 (BUK6Y10-30P), moves board E's auxiliary domain to VSYS_E and restates the bounds")
    p("     the three modes bounded by SLUSE65A: the pack absent, VSYS at least %s V (LDO mode); the charge inhibited, VSRN + %d mV within +-%d %%;"
      % (b1["vsys_min"], b1["inhib"][0], b1["inhib"][1]))
    p("       the pack present, VSYS_MIN the floor, up to %s V; D1, D3 and D4 removed; D2 open against a %s V margin" % (b1["vsys_max"], b1["margin"]))
    p("     %d of the BQ25731's %d row blocks identical, so L4-E4 to L4-E8 carry over; the cell-count strap fixed at %s %% of VDDA, never wired to"
      % (b1["rows_same"][0], b1["rows_same"][1], b1["strap"]))
    p("       battery presence; ChargeCurrent 0 A at POR; R-b': 0x0080, at most %s mA, no charge under %s V on SRN" % (b1["rb_ma"], b1["rb_v"]))
    p("     Q39: %s W at PS-IDLE-SPEC on battery (%s A, %s %% of the pack's output), %s W at PS-TYP, %s W at 10 A; its installed thermal bar at most"
      % (b1["q39_idle"][1], b1["q39_idle"][0], b1["q39_idle"][2], b1["q39_heat"][1], b1["q39_heat"][2]))
    p("       %s C/W; the docking pulse %s A for %s us through its body diode (IDM %s A; no pulse rating printed); parts %s USD against (A)'s %s USD"
      % (b1["bar"], b1["dock"][0], b1["dock"][3], fmt(b1["dock"][2]), b1["cost"][1], b1["cost"][0]))
    p("     the register: R-157 to R-162 (E11-27 to E11-32); R-152 (E11-24) withdrawn once R-157 is applied; R-114's D1 and D3 answers then not needed")
    p("   U-02, T-H1 DECIDES: the conservative bound lid open (the fans' flow, the boards' radiation and the floor's support credited at zero):")
    p("     E5 %s W/K, E3-O %s W/K, the envelope's +40 C %s W/K; lid closed %s, %s and %s W/K; with a 50 m/s inside flow %.3f and %.3f W/K (a bound, not the"
      % (tb["e5"][0], tb["e3o"][0], tb["env"][0], tb["e5"][2], tb["e3o"][2], tb["env"][1], F["fx"]["capfix"][0], F["fx"]["capfix"][1]))
    p("       capacity: L4-E12 12e puts the capacity proper at %s and %s W/K on the conservative ends)" % (fmt(F["fx"]["capfix"][2]), fmt(F["fx"]["capfix"][3])))
    p("     on the bound: E5 under the hold %s C (%.3f W/K at %s K), with F3 %s C; E3-O %s C (%.3f W/K at %s K)"
      % (tb["air_e5"][0], tb["air_e5"][1], tb["air_e5"][2], tb["air_f3"][0], tb["air_e3o"][0], tb["air_e3o"][1], tb["air_e3o"][2]))
    p("     with every session measure the module's +85 C intake binds: E5 needs %s W/K, the bound gives %s (holds by %.3f); E3-O needs %s W/K, the bound"
      % (tb["all_e5"][0], tb["all_e5"][2], tb["all_e5"][3], tb["all_e3o"][0]))
    p("       gives %s: a gap of %s W/K, the intake at %s C; a flow of %s m/s at the inner faces, or the radiation and the floor together (%s W/K), would close it"
      % (tb["all_e3o"][2], tb["all_e3o"][3], tb["intake"], tb["flow"], tb["credits"]))
    p("     the deciding point: lid open, the fans at full duty, 21.2 W spread as E5's hold, room temperature, %s to %s h:" % (fmt(tb["dur"][0]), fmt(tb["dur"][1])))
    for a, rise, tgt, what in tb["bands"]:
        p("       at least %s W/K (%s K rise) meets %s W/K: %s" % (a, rise, tgt, what))
    p("     under %s W/K the owner decides (a deviation of E3-O or a device-set re-pick); the register: R-104 restated, R-163 to R-166" % tb["bands"][4][0])
    hr = F["cb"]["hr"]
    ap = hr["ap"]
    p("   U-02, THE HEAT-REJECTION QUESTION (L4-E12 section 15, out 10; check 6 at 589f18ac): if T-H1 reads under the profile's need, what restores it inside the rulings?")
    p("     the need: the profile puts %s W into the case (%s W at the pack); its +70 C class at +40 C needs %s W/K; charging with it on SC-37's design day (the air %s to %s C) %s to %s W/K"
      % (fmt(hr["q"]), fmt(hr["q_pack"]), fmt(hr["g_need"]), fmt(hr["day"][0]), fmt(hr["day"][1]), fmt(hr["g_chg"][0]), fmt(hr["g_chg"][1])))
    p("     the rulings kept: no vent or opening anywhere (32.53), the Peli 1450 at any cost, the face a 3 mm aluminium plate carrying the UI (32.40); every figure on the conservative bound, two nodes")
    p("     (a) fins on the face's free %s m2 (the plate %s m2 less the monitor window %s m2 and the e-paper lens %s m2), under M3's %s mm (%s mm with the allowances doubled),"
      % (fmt(hr["free"][3]), fmt(hr["free"][0]), fmt(hr["free"][1]), fmt(hr["free"][2]), fmt(hr["m3"][0]), fmt(hr["m3"][1])))
    p("       k %d to %d (ASSUMPTION), about %s kg of %s mm fins at an %s mm pitch" % (hr["k"][0], hr["k"][1], fmt(hr["fins"][0]), fmt(hr["fins"][1]), fmt(hr["fins"][2])))
    p("     (b) the large loads, %s W at their pins, led into the plate in the %s to %s mm between board B's tall parts and the face parts; the switches to +85 C parts"
      % (fmt(hr["led"]), fmt(hr["gap"][0]), fmt(hr["gap"][1])))
    p("     (c) the open lid as a second radiator: a skin on its ceiling (at most %s m2, %s m tall open) on a braid %.2f m, %s mm2, %s K/W (ASSUMPTION); about %s kg; the strap carries %s W"
      % (fmt(hr["lid"][0]), fmt(hr["lid"][1]), hr["braid"][0], fmt(hr["braid"][1]), fmt(hr["braid"][2]), fmt(hr["lidkg"]), fmt(hr["strap"])))
    p("     at the profile's heat on the bound (+40 C: the air, the plate, G | %s C: the air, G | %s C: the air, G):" % (fmt(hr["day"][0]), fmt(hr["day"][1])))
    for k in ("none", "a2", "a3", "b", "ba", "c", "all"):
        p("       %s: %s C, %s C, %s W/K | %s C, %s W/K | %s C, %s W/K" % ap[k])
    p("     the best route rejects %s W with the air at +70 C against %s W: short by %s W (%s W/K); charging %s and %s W/K short; the bound alone rejects %s W at +40 C (%s W short)"
      % (fmt(hr["best"][0]), fmt(hr["best"][1]), fmt(hr["best"][2]), fmt(hr["best"][3]), fmt(hr["chg_short"][0]), fmt(hr["chg_short"][1]), fmt(hr["bound_only"][0]), fmt(hr["bound_only"][1])))
    p("     all three passive: no power, no endurance change, the heat unchanged; costs TBD, no quote held")
    p("     as check 6 accepted it: T-H1's point at the profile's heat, P1 (two heaters %s W), %s W/K for the profile at +40 C, %s and %s W/K for charging;"
      % (fmt(hr["heaters"]), hr["thr"][0][0], hr["thr"][1][0], hr["thr"][2][0]))
    p("     WITHDRAWN by check 7 (section 24): P1 established X2, a state no requirement asks for, and left the fans out; the profile's own line is K6 at +20 C")
    p("   U-01, A SUPPORTED ROUTE ON PUBLISHED EVIDENCE: the Saft MP 176065 xtd (%s V, %s Ah, %s Wh a cell; %s A continuous, %s A pulses with no duration)"
      % (fmt(u1["sheet"][1]), fmt(u1["sheet"][0]), fmt(u1["sheet"][2]), fmt(u1["sheet"][3]), fmt(u1["sheet"][4])))
    p("     as 4S1P: %s Wh nominal, %s to %s Wh usable, %s to %s h battery-only; NZ$ %s a cell, NZ$ %s for four; a PROPOSAL, the owner's to adopt"
      % (fmt(u1["energy"][0]), fmt(u1["energy"][1]), fmt(u1["energy"][2]), fmt(u1["energy"][3]), fmt(u1["energy"][4]), fmt(u1["cost"][0]), fmt(u1["cost"][1])))
    p("     supported for the temperature windows only; NOT YET ADOPTABLE after the fix round (B5, section 25): current at temperature and the storage dwell")
    p("       and recovery AWAIT Saft or the limited sample qualification (10g), the axial fit the mock-up (at most %.2f mm of wrap where the 35E block uses"
      % u1["wrap"][0])
    p("       %.2f mm), and T-H1 (LO-01a's complete pass, LO-01e)" % u1["wrap"][1])
    p("     the ruled 35E UNSUITABLE on its own published evidence: E3-O's cells %s to %s C over +60 C, E5's idle pack %s C, +71 C and -33 C storage"
      % (u1["e35_e3o"][0], u1["e35_e3o"][1], u1["e35_e5"]))
    p("     the HL18650V the higher-energy alternative on its signed specification or a soak (USD %.2f, %s to %s days); the pocket's room %s L; (III)'s E5 route REJECTED"
      % (u1["soak"][0], fmt(u1["soak"][1]), fmt(u1["soak"][2]), u1["room"]))
    p("     on the conservative bound a kit running the profile reaches the cells' 42 C charge start only below %s C ambient (L4-E10): 2c's normal operation"
      % fmt(u1["charge_start"]))
    p("     the register: R-167 to R-169 (the mock-up, the current at temperature and the storage dwell, the lot's capacity); the owner's items OW-3 and OW-9")
    return L


SURGE_HEAD = ("| Disturbance |", "| Disturbance | Source, waveform and duration | D4 at its current | The drafted entry | As drawn | Defect and register |")
REMEDY_HEAD = ("| Remedy |", "| Remedy | What it changes (as L4-E7 compared it) | D-10, a 36 V source | D-11, a reversed panel | L4-E7's verdict |")


def cons_surge(F):
    """L4-E7's verdicts on the panel lead (set 27) and its solar-fault remedies (check 5 at 573fd5b8), read from its output: the
    drafted entry with the guard against the entry as drawn; the remedies as L4-E7 compared them, the third selected by L4-E7."""
    sv = F["sv"]
    rm = sv["rm"]
    lim, ld = fmt(sv["lim"]), fmt(sv["lim_drawn"])
    r4 = sv["d4_rows"]
    verdicts = [
        ("D1", "CS116 on PV_IN alone and on the J_SOLAR cable (MIL-STD-461G 5.14): damped sinusoids, Ip to %s A from 1 to 30 MHz, the lead's %s MHz added; five minutes"
         % (fmt(sv["d1"][1]), "%.1f" % sv["qwave"]), "%.2f V with the SMCJ30A (%s A, hot end; %.2f V with the drawn SMCJ28A)" % (rm["d1d2"][0], fmt(sv["d1"][1]), sv["d1"][0]),
         "MEETS (its %s V parts; the block on or off)" % lim, "NOT MET (%.2f > %s V)" % (sv["d1"][0], ld), "D-12 (R-21, R-173); R-174"),
        ("D2", "CS115 on the cable (5.13): %s A, 30 ns, 30 Hz for one minute; the loop current recorded, not limited" % fmt(sv["d2"][1]),
         "%.2f V with the SMCJ30A (%s A, hot end)" % (rm["d1d2"][1], fmt(sv["d2"][1])),
         "MEETS with the block off; with it on CONDITIONAL on R-174 (U5 %s V at the 5 A calibration level; a pulse over the cut-off turns it off within %s us)" % (fmt(rm["b6"]["u5_cs115"]), fmt(rm["t_off"])),
         "NOT MET (%.2f > %s V)" % (sv["d2"][0], ld), "D-12; R-174"),
        ("D3", "the panel's cold open circuit, %s V at most at -20 C, held" % fmt(sv["d3"][0]), "%s V, under its %s V standoff (the SMCJ30A's %s V drafted)" % (fmt(sv["d3"][0]), fmt(sv["d3"][1]), fmt(rm["s30"][0])),
         "MEETS (CONDITIONAL on PANEL-ACC)", "MEETS", "R-35"),
        ("D4", "a stiff source on the port (the declared %s to %s V) through the lead's %s Ohm loop and F2, held" % (fmt(sv["src"][0]), fmt(sv["src"][1]), fmt(sv["lead"][2])),
         "nothing with the guard; without it conducts %s to %s A, %s to %s W against %s W on the board" % (fmt(sv["d4_a"][0]), fmt(sv["d4_a"][1]), fmt(r4[3][3]), fmt(r4[0][3]), fmt(sv["d4_cap"][0])),
         "MEETS with the guard: the cut-off rises at %s to %s V, the block never turns on, Q12 holds %s of 100 V" % (fmt(rm["rise"][0]), fmt(rm["rise"][1]), fmt(sv["src"][1])),
         "NOT MET", "D-10; R-173 (drafted)"),
        ("already on (B6)", "the same source stepping or rising onto the port while the guard is on, through the lead (its %s Ohm at the cold end's copper)" % fmt(sv["lead"][2]),
         "nothing: TRK_VS at most %s V, %s V under the SMCJ30A's least breakdown; ramps at least %s V under it" % (fmt(rm["b6"]["rows"][-1][1]), fmt(rm["b6"]["rows"][-1][3]), fmt(rm["b6"]["ramp"][2])),
         "MEETS with B6's four parts (C131 and C132, C133 and C134, C126, R97), CONDITIONAL on the lead's loop inductance at least %s uH (U5 %s of 0.3 V binding)"
         % (fmt(rm["b6"]["l_uh"]), fmt([r[1] for r in rm["b6"]["rows"] if r[0] == rm["b6"]["bind"]][0])),
         "the guard as first drafted fails PV_F, its slew, INP and U5", "D-10; R-173, R-176 row 2, R-180"),
        ("D5", "a reversed panel (DECISION-31's E-N1), the panel's %s A forward, held" % fmt(sv["d5"][0]),
         "nothing with the guard; without it forward, inside %s W only below a %s V drop" % (fmt(sv["d5"][1]), fmt(sv["d5"][2])),
         "MEETS with Q13 in the return, CONDITIONAL on its leakage above +25 C", "NOT MET", "D-11; R-173 (drafted)"),
        ("the residual band", "a stiff source between %s V and the cut-off (outside REQ-016's window, a single fault)" % fmt(F["pv"]["v_max"]),
         "nothing: the block stays on", "the stage runs under the backstop's current trip, at most %s W: not claimed, a residual for layer 8" % fmt(rm["resid"]),
         "the same", "R-175 (TRN-001's judgement)"),
        ("beyond the basis", "a direct strike, or one nearer than MIL-STD-464's nearby lightning (CS117 S, not taken)",
         "D11's own rating with the guard, %s A at 10/1000 us" % fmt(rm["d11"]), "a residual outside every requirement", "D4's own rating", "R-156; REQ-041's mast-down alarm"),
    ]
    remedies = [
        ("(1)", "the TPS48110-Q1 alone driving back-to-back FETs (SLUSEE5E Figure 9-14)", "closed", "its VS, CS+ and ISCP pins rated -1 V see the reversal",
         "not taken (L4-E7)"),
        ("(2)", "the LM74700-Q1 ideal diode ahead of the TPS48110-Q1 (the vehicle entry's pair)", "closed", "closed",
         "not taken: CATHODE to ANODE 76.21 V under CS116's negative lobes against 75 V, and CS101's ripple rectified inside M2's band (L4-E7)"),
        ("(3)", "U21 TPS48110AQDGXRQ1 with Q12 CSD19532Q5B and R87 4.5 mOhm (L4-E11's network but the OV divider, %s); Q13 CSD19532Q5B in the return (PV_RTN) "
         "with R101, R102 and D12 BZT52C12; D11 SMCJ40CA across the port; C131 and C132, two 10 uF 100 V, on PV_F; C133 and C134, two 10 uF 50 V, on PV_P; R97 30.0k; C126 330 pF; D4 to SMCJ30A" % rm["divider"],
         "closed: off above %s to %s V rising, back under %s V or more" % (fmt(rm["rise"][0]), fmt(rm["rise"][1]), fmt(rm["fall"][0])),
         "closed, CONDITIONAL on Q13's leakage above +25 C",
         "SELECTED by L4-E7 (SESSION; check 5): the path linear when on, no control on a reverse current; drafted in apply_gen_sch_e_solar_guard.py (7 edits), not applied"),
        ("TVS only", "SMCJ36A with the entry's 50 V parts at the 63 V class", "closed at D4", "not closed",
         "evaluated and not taken: it re-opens the CS101 correction and runs the stage at %s to %s W from 36 V" % (fmt(sv["stage36"][0]), fmt(sv["stage36"][1]))),
    ]
    if rm["b6"]["d12"] not in [d for d in DEFECTS if d["id"] == "D-12"][0]["options"]:
        refuse(4, "D-12's row does not carry L4-E7's text")
    sel = ("**The remedies are selected and drafted, not applied** (L4-E7, its check 5 at `573fd5b8`, B6 at `11339ec7`). D-10: the over-voltage cut-off, "
           "U21 with Q12, rises at %s to %s V and falls back at %s V or more (aged), %s V over CS101's peak at the input, %s V under the "
           "SMCJ30A's least breakdown at the cold end and %s V over 25 V on the fall, so it never trips inside REQ-016's window and the "
           "block never turns on under a %s V source. D-11: Q13 in the return blocks a reversed panel, CONDITIONAL on its leakage above "
           "+25 C (printed at 25 C only). %s **With the guard already on** (the review's B6, L4-E7 at `11339ec7`) a 36 V source "
           "stepping on is cut, Q12 off at most %s A within %s us and D4 carrying nothing, once B6's four drafted parts are in (C131 and "
           "C132 two 10 uF 100 V, C133 and C134 two 10 uF 50 V on PV_P, C126 330 pF, R97 30.0k): every rating MEETS, CONDITIONAL on the "
           "panel lead's loop inductance at least %s uH (its conductors' centres at least %s mm apart over its length), which no document "
           "gives (R-176 row 2, R-180). Re-run: the start's inrush %s A under U21's %s A; CS101's worst ripple %s A "
           "against the %s A margin; check (b)'s allowance %s ms (the accepted %s ms); the static bound %s W (%s W without it). The "
           "block's loss: %s W at the regulation's highest current, %s Wh on SC-37's day (%s %%). **Named for layer 8:** a stiff source "
           "between 25 V and the cut-off is outside the window but still runs the stage, at most %s W under the backstop's current "
           "trip (R-175); the cut-off cannot go below CS101's %s V input peak without a different immunity basis. Owed: the SMCJ30A's "
           "LCSC code, U21's DGX-19 land, the regeneration and the bench rows (R-176). The guard adds protection and changes no topology."
           % (fmt(rm["rise"][0]), fmt(rm["rise"][1]), fmt(rm["fall"][0]), fmt(rm["marg"][0]), fmt(rm["marg"][1]), fmt(rm["marg"][2]), fmt(sv["src"][1]),
              rm["b6"]["d12"], fmt(rm["b6"]["sum"][0]), fmt(rm["b6"]["sum"][1]), fmt(rm["b6"]["l_uh"]), fmt(rm["b6"]["mm"]),
              fmt(rm["b6"]["start"][0]), fmt(rm["b6"]["start"][1]),
              fmt(rm["cs101"][0]), fmt(rm["cs101"][2]), fmt(rm["chkb"][0]), fmt(rm["chkb"][2]), fmt(rm["static"][0]), fmt(rm["static"][1]),
              fmt(rm["loss"][0]), fmt(rm["day"][0]), fmt(rm["day"][2]), fmt(rm["resid"]), fmt(F["cs101_pv"])))
    return verdicts, remedies, sel


def cons_surge_lines(F):
    verdicts, remedies, sel = cons_surge(F)
    sv = F["sv"]
    rm = sv["rm"]
    L = ["23. THE PANEL LEAD'S SURGE AND THE SOLAR-FAULT REMEDIES (L4-E7's derivation, set 27 at 6d76453e, and its remedies, check 5 at 573fd5b8: MIL-STD-461G"
         " CS116 and CS115 under REQ-063, both A; the sustained over-voltage and the reversed panel): the verdicts, D-10 to D-12, the remedies, the residual"]
    p = L.append
    p("   the lead: %s m one way of %s mm2, %s Ohm in loop, unshielded, the kit floating; its quarter wave %.1f MHz added to CS116's frequencies; TEST-PLAN runs M1 to M5 only"
      % (fmt(sv["lead"][0]), fmt(sv["lead"][1]), fmt(sv["lead"][2]), sv["qwave"]))
    p("   the criterion (REQ-016's): D4's clamp at the disturbance's current, with its tolerance, at or under the lowest limit on PV_P: %s V drafted, %s V as drawn"
      % (fmt(sv["lim"]), fmt(sv["lim_drawn"])))
    for v in verdicts:
        p("   %s %s; D4: %s; the drafted entry %s; as drawn %s; %s" % v)
    p("   D4 under a stiff %s V source without the guard (L4-E7's rows, INFERRED straight line from each breakdown at the printed slope):" % fmt(sv["src"][1]))
    for nm, vb, ia, pw in sv["d4_rows"]:
        p("     %s: breakdown %.2f V, %.2f A, %.1f W" % (nm, vb, ia, pw))
    p("   the SMCJ30A (held row): VR %s V, VBR %s to %s V, %s V at the cold end; VC %s V at %s A; the cut-off new %s to %s V, aged %s to %s V rising, %s to %s V falling"
      % (tuple(fmt(x) for x in rm["s30"]) + tuple(fmt(x) for x in rm["new"] + rm["rise"] + rm["fall"])))
    p("   U21's UVLO on at %s V at most, off at %s V at least, under the stage's own enable; the block's loss %s W at %s A and %s W at the trip's %s A;"
      % (fmt(rm["uvlo"][0]), fmt(rm["uvlo"][1]), fmt(rm["loss"][0]), fmt(rm["loss"][1]), fmt(rm["loss"][2]), fmt(rm["loss"][3])))
    p("     %s Wh of %s Wh on SC-37's day (%s %%), %s Wh of %s Wh on the bright day; CS101 re-run %s A at %d Hz; Q13's leakage bound %s uA (%s uA printed at 25 C)"
      % (fmt(rm["day"][0]), fmt(rm["day"][1]), fmt(rm["day"][2]), fmt(rm["day"][3]), fmt(rm["day"][4]), fmt(rm["cs101"][0]), rm["cs101"][1], fmt(rm["q13"][0]), fmt(rm["q13"][1])))
    b6 = rm["b6"]
    p("   THE GUARD ALREADY ON (the review's B6; L4-E7 at 11339ec7, MODELED): a stiff %s V source stepping or rising onto the port through the lead; at %s uH, the"
      % (fmt(sv["src"][1]), fmt(b6["l_uh"])))
    p("     worst over every start and corner, against each printed rating (and the least inductance it holds at):")
    for nm, w, lim_, mg, hold in b6["rows"]:
        p("       %s: %s of %s, margin %s; holds from %s uH" % (nm, fmt(w), fmt(lim_), fmt(mg), hold))
    p("     D4's current: none. The binding rating: %s; the lead qualifies at %s uH, its conductors' centres at least %s mm apart over its %s m; at %s uH (%s mm)"
      % (b6["bind"], fmt(b6["l_uh"]), fmt(b6["mm"]), fmt(b6["len_m"]), fmt(b6["below"][0]), fmt(b6["below"][1])))
    p("     the guard does not hold (NOT MET). Q12 at most %s of its derated chart, %s A at the turn-off; Q13 %s A, %s of its chart; D11 %s A and %s mJ against %s mJ"
      % (fmt(b6["q12"][0]), fmt(b6["q12"][1]), fmt(b6["q13"][0]), fmt(b6["q13"][1]), fmt(b6["d11"][0]), fmt(b6["d11"][1]), fmt(b6["d11"][2])))
    p("     ramps: TRK_VS at most %s V at %s V/us, %s V under D4's least breakdown, U5 at most %s V; the cold connection: PV_F at most %s V, slew %s V/us, INP %s V,"
      % (fmt(b6["ramp"][0]), fmt(b6["ramp"][1]), fmt(b6["ramp"][2]), fmt(b6["ramp"][3]), fmt(b6["cold"][0]), fmt(b6["cold"][1]), fmt(b6["cold"][2])))
    p("     EN/UVLO %s V, Q13's body diode %s A; as first drafted (C131 1 uF, R97 39k, CSCP 1 nF, no C133 and C134) PV_F %s of 100 V, its slew %s of 60 V/us,"
      % (fmt(b6["cold"][3]), fmt(b6["cold"][4]), fmt(b6["drafted"][0]), fmt(b6["drafted"][1])))
    p("     INP %s of 20 V, U5 %s of 0.3 V: four ratings failed, fixed by C131 and C132 (two 10 uF 100 V), C133 and C134 (two 10 uF 50 V on PV_P), C126 330 pF"
      % (fmt(b6["drafted"][2]), fmt(b6["drafted"][3])))
    p("     and R97 30.0k; the start %s A under U21's %s A; the static bound %s W" % (fmt(b6["start"][0]), fmt(b6["start"][1]), fmt(rm["static"][0])))
    p("     D-12 corrected (L4-E7's text): %s" % b6["d12"])
    p("     R-176's acceptance, seven rows: %s" % "; ".join("(%d) %s" % (i, r) for i, r in enumerate(b6["r176"], 1)))
    p("   the remedies as L4-E7 compared them:")
    for r in remedies:
        p("   %s %s; D-10 %s; D-11 %s; %s" % r)
    p("   " + sel.replace("**", "").replace("`", ""))
    p("   the register: R-156 restated (its input is this derivation; U18 the INA169 at %s V, not the INA250's %s V), R-173 the drafted guard"
      " (apply_gen_sch_e_solar_guard.py), R-174 the CS116 and CS115 test at layer 8, R-175 the residual band (layer 8), R-176 the guard's bench rows"
      % (fmt(sv["u18"][1]), fmt(sv["u18"][0])))
    return L


def cons_surge_tables(F, D, st):
    verdicts, remedies, sel = cons_surge(F)
    return {SURGE_HEAD[0]: [SURGE_HEAD[1], "|---|---|---|---|---|---|"] + ["| %s |" % " | ".join(v) for v in verdicts],
            REMEDY_HEAD[0]: [REMEDY_HEAD[1], "|---|---|---|---|---|"] + ["| %s |" % " | ".join(r) for r in remedies]}


def cons_exit_defects(F):
    """The known defects beside U-01, U-02 and U-04 in the exit statement (L4-E7's derivation and remedies, check 5)."""
    sv = F["sv"]
    rm = sv["rm"]
    adr = "ADDRESSED IN DRAFTS: a selected remedy (L4-E7, check 5), drafted in apply_gen_sch_e_solar_guard.py (R-173), not applied"
    owed = "the SMCJ30A's LCSC code, U21's DGX-19 land, the regeneration and its gates, the bench rows (R-176)"
    topo = "nothing of the topology: protection added at the solar entry"
    fx = F["fx"]
    return [
        ("D-13", "(B1)'s draft left board E's auxiliary domain on the pack's side of the battery FET (the review's B1)",
         "ADDRESSED IN DRAFTS: board E on VSYS_E over the dock's pin 1 (L4-E11 15a; R-177, R-178), not applied; the held pack's drains %s mA, the start bounded to VSYS_MIN or a latch within %s s"
         % (fmt(fx["held"][0]), fmt(fx["latch_s"])),
         "the drafts applied with R-157 under L4-E11's release record", "the held pack current at most %s mA and the start from cold (R-161); the fans' rating to %s V (R-179)" % (fmt(fx["held"][1]), fmt(fx["vsys_rng"][1])),
         "nothing of the topology: a feed inside (B1)"),
        ("D-14", "(B1)'s battery FET bounded at an unprinted corner and a fallback lowering 18 A for 60 s (the review's B2)",
         "ADDRESSED IN DRAFTS: the pair Q39 and Q40 (two BUK6Y10-30P; L4-E11 15c; R-157), not applied; every protection event at TJ 150 C or under at %s C/W per FET, 18 A for 60 s at %s C"
         % (fmt(fx["bar"][0]), fmt(fx["svc_tj"])),
         "the draft applied (R-157)", "each FET's installed path at most %s C/W (R-159), the docking split at most %s hot (R-160)" % (fmt(fx["bar"][0]), fmt(fx["dock"][2])),
         "nothing of the topology: a part inside (B1)"),
        ("D-10", "a stiff %s V source on the solar port (a single fault)" % fmt(sv["src"][1]),
         adr + "; the cut-off rises at %s to %s V, falls back at %s V or more; with the guard already on (B6) every rating MEETS with its four added parts, CONDITIONAL on the panel lead's loop inductance at least %s uH"
         % (fmt(rm["rise"][0]), fmt(rm["rise"][1]), fmt(rm["fall"][0]), fmt(rm["b6"]["l_uh"])),
         "the draft applied after its release record (R-92's L4-E7 RELEASE.md)", owed + "; the lead's inductance measured, or its conductors' centres at least %s mm apart (R-176 row 2, R-180)" % fmt(rm["b6"]["mm"]), topo),
        ("D-11", "a reversed panel (E-N1, a single fault)", adr + "; CONDITIONAL on Q13's leakage above +25 C", "the same draft", "Q13's leakage at the hot end (R-176)", topo),
        ("D-12", "CS116 and CS115 on the panel lead, as drawn", "RESOLVED in the drafted entry (R-21, R-173): %s" % rm["b6"]["d12"],
         "the loop current recorded (R-174)", "the test of R-174 at layer 8", "nothing: the drafted entry's parts"),
        ("residual", "a stiff source between %s V and the cut-off (outside the window)" % fmt(F["pv"]["v_max"]), "a residual named for layer 8: the stage runs, at most %s W under the backstop's trip" % fmt(rm["resid"]),
         "TRN-001's judgement whether the single fault needs more (R-175)", "the cut-off cannot go below CS101's %s V input peak without a different immunity basis" % fmt(F["cs101_pv"]), "not the topology"),
    ]


def cons_cell_rows(F):
    """L4-E10's battery comparison (its section 16, check 6), carried as the budget's and the handover's cell row: its table's
    rows as filed, each item classed GUARANTEED, MODELLED or AWAITING by L4-E10."""
    return [tuple(c.strip() for c in r) for r in F["rc"]["cell_tab"]]


def cons_cell_tables(F, D, st):
    return {"| Item | Approved pack (D-06) |": ["| Item | Approved pack (D-06) | Saft route (a proposal) |", "|---|---|---|"] + ["| %s | %s | %s |" % r for r in cons_cell_rows(F)]}


def cons_ledger(F):
    """The findings ledger's totals as the ledger files them, with the Layer 4 review's E6 beside them (the ledger file is the
    coordinator's: this record cites E6 and claims none of those rows closed)."""
    lg = F["rc"]["ledger"]
    head = ("**The findings ledger** (`records/l4close/FINDINGS-LEDGER.md`, set 27's integration, as filed): %d rows of rejected "
            "collaborator findings, %d CLOSED, %d CLOSED AS CONDITIONAL, %d OPEN DOWNSTREAM and %d STILL OPEN." % lg)
    e6 = (" The Layer 4 review of set 27's candidate (astra-check-l4close-1, its E6) found L4-E12:2.1 and L4-E12:1.2 REGRESSED (the "
          "SGP41's absolute +55 C line used again for a powered option C; restated in the fix round, L4-E12 12a and U-02 here), and "
          "L4-E7R:1.6 and L4-E7R:2.4 needing B6's condition (the solar guard's already-on over-voltage transient), which L4-E7's B6 round "
          "now bounds, CONDITIONAL on the panel lead's loop inductance at least 2.47 uH (11339ec7); this record does not claim those four "
          "rows closed, and updating the ledger is the coordinator's.")
    if lg[4] == 0:
        return head + (" As filed, L4-E12:1.3 and 2.2 close on R-139's restated bench test (item 5's DIFFERS resolved by that correction, "
                       "recorded in VERIFICATION-2026-10-02.md).") + e6
    return head + (" The still-open rows are named in the ledger's count section; this record does not restate them.") + e6


def cons_amend_lines(F):
    rc = F["rc"]
    K, R = rc["K"], rc["R"]
    L = ["24. THE OWNER'S AMENDMENT OF 2 OCTOBER 2026, 14:20: L4-E12'S THERMAL RECONCILIATION (check 7 at 6f8fd652), L4-E10'S BATTERY COMPARISON"
         " (check 6 at e2d20bf2), THE FINDINGS LEDGER (fnd/l4close at 65be2c2c) AND R-139"]
    p = L.append
    p("   the thermal framing corrected: this record's statement that the approved profile is not thermally feasible at +40 C, with %s W/K as the deciding"
      % K["X2"]["need"])
    p("     reading, is WITHDRAWN (the reading %s W/K established X2 only); at +40 C C1 sheds the profile (REQ-024) and D-02b runs the reduced mode above +35 C"
      % fmt(rc["x2_read"][0]))
    p("   the conditions (L4-E12 11c, 11e; read, not recomputed):")
    for k in ["K%d" % i for i in range(1, 11)] + ["X1", "X2", "X3"]:
        c = K[k]
        p("     %s %s; lid %s; %s W at %+.1f C; %s; needs %s W/K%s" % (k, c["what"], c["lid"], fmt(c["q"]), c["amb"], c["limit"], c["need"],
                                                                     "; a reading of at least %s W/K (rise %s K, U %s %%)" % (R[k]["read"], R[k]["rise"], R[k]["u"]) if k in R else ""))
    p("   as stated in this amendment, CORRECTED by the fix round (section 25: K1 and K5 are screens, option C switches the SGP41 off, each mode has its own line):")
    p("   CFL-002 decides the line at +40 C: option C, K1 %s W/K (at or over the outside films' cap %s W/K at the conservative ends, %s W/K at the other"
      % (K["K1"]["need"], fmt(rc["cap"][0]), fmt(rc["cap"][1])))
    p("     ends, K1 under it there by %s W/K); options A and B, K3 %s W/K, read at %s W/K (check 7 puts its bench line near %s W/K); the bound at K1's rise"
      % (fmt(rc["cap_gap"]), K["K3"]["need"], R["K3"]["read"], fmt(rc["k3_near"])))
    p("     %s to %s W/K; the room reading the conservative side (+%s to +%s %% at +40 C)" % (fmt(rc["bound"][0]), fmt(rc["bound"][1]), fmt(rc["transl"][0]), fmt(rc["transl"][1])))
    p("   the procedure's points since the fix round: 12d's, one per mode's heat and lid state; heaters (W) plus the fans' draw: %s"
      % "; ".join("%s %s + %s" % (k, fmt(rc["H"][k][1]), fmt(rc["H"][k][2])) for k in ("M2", "M1", "M7", "M5", "M8")))
    p("   the battery comparison (L4-E10 11, its page's section 16): the approved 35E 4S3P %s Wh nominal (%s Wh on the typical capacity), %s Wh, %s h at +20 C;"
      % (fmt(rc["e35_nom"]), fmt(rc["e35_typ"]), fmt(rc["e35_use"][0]), fmt(rc["e35_use"][1])))
    p("     the Saft MP 176065 xtd 4S1P %s Wh nominal, %s to %s Wh, %s to %s h (MODELLED: Saft prints no curve); each item GUARANTEED, MODELLED or AWAITING:"
      % (fmt(rc["saft_nom"]), fmt(rc["saft_use"][0]), fmt(rc["saft_use"][1]), fmt(rc["saft_use"][2]), fmt(rc["saft_use"][3])))
    for r in cons_cell_rows(F):
        p("     %s: approved %s | Saft %s" % (r[0], r[1].replace("**", ""), r[2].replace("**", "")))
    p("     adoption not supported yet: the fit mock-up, 18 A for 60 s, Saft's missing figures, the gauge data and T-H1 AWAITING; the owner's approval required")
    p("   " + cons_ledger(F).replace("**", "").replace("`", ""))
    p("   R-139 restated (the ledger's item 5, DIFFERS): its lag test measured the reading's crossing to the off state, about 1 s of the %s s; restated to the"
      % fmt(rc["lag"][1]))
    p("     TMP117 reading's lag behind a thermocouple at the SGP41 on a ramp of at least %s K/h, at most %s K at 54.0 C; without that test the 54.0 C setting"
      % (fmt(rc["lag"][0]), "%.6f" % rc["lag"][2]))
    p("     holds only while the sensor's time constant is at most %s s (%s s on the TMP117N grade)" % ("%.1f" % rc["tau_max"][0], "%.1f" % rc["tau_max"][1]))
    return L


def cons_fix_lines(F):
    """Section 25: the fix round of the Layer 4 review (astra-check-l4close-1, NOT YET on set 27's 8fbb68b6), as the three records
    answered it and this record carries it; read, not recomputed."""
    fx, rc, b1 = F["fx"], F["rc"], F["cb"]["b1"]
    M = fx["modes"]
    L = ["25. THE FIX ROUND OF THE LAYER 4 REVIEW (astra-check-l4close-1 at 8fbb68b6, NOT YET on B1 to B7): L4-E11 at 656fc540 (B1, B2, the charger"
         " minors), L4-E12 at b1cd32ba (B3, B4, B7, the capacity addendum), L4-E10 at ee09aa09 (B5); B6 (L4-E7, the solar guard's already-on transient)"
         " follows as an add-on"]
    p = L.append
    p("25a B1, BOARD E'S AUXILIARY DOMAIN ON A SOURCE-CAPABLE FEED (L4-E11 15a, 15b; D-13)")
    p("   board A's J_DOCK pin 1 from GND to VBAT (VSYS); board E's J_BLK pin 1 to VSYS_E; U12, C31, both mixer fans, D7 and D8 on VSYS_E (%s A on one 813"
      % fmt(fx["aux_a"]))
    p("     contact; the ground return on seven, %s A each with one open, %s %% of 3.5 A, %s C at the 51 C air); VSYS_E %s to %s V (the fans' rating owed, E11-35)"
      % (fmt(fx["gnd7"][0]), fmt(fx["gnd7"][1]), fmt(fx["gnd7"][2]), fmt(fx["vsys_rng"][0]), fmt(fx["vsys_rng"][1])))
    p("   the held state (the charge inhibited, a source, the pack present): no kit load fed from the pack; its bounded drains %s mA (the monitor %s mA at"
      % (fmt(fx["held"][0]), fmt(fx["mon"][0])))
    p("     %s V); the bench reads the held pack current at most %s mA (E11-31, R-161)" % (fmt(fx["mon"][1]), fmt(fx["held"][1])))
    p("   the start: the 502.3 ms withdrawn (0.5 A is an input ceiling, not a delivered current); on held evidence VSYS_MIN or a latch within %s s; the first"
      % fmt(fx["latch_s"]))
    p("     window's success not bounded: E11-31 at -20, 25 and 62.1 C (the source-only and held sequences: 4a, 4c)")
    p("   the register: R-177 (apply_gen_sch_e_aux.py, E11-33), R-178 (apply_pcb_interfaces_dock.py, E11-34), R-179 (E11-35); R-161 restated")
    p("25b B2, THE BATTERY FET (L4-E11 15c; D-14)")
    p("   SELECTED: two Nexperia BUK6Y10-30P in parallel, Q39 and Q40 (LCSC %s, %d in stock, %s USD each at 10); RDS(on) bounded at BATDRV's 8.5 V and the"
      % (fx["pair"][0], fx["pair"][1], fmt(fx["pair"][2])))
    p("     hot junction, %s mOhm per FET; the bar %s C/W per FET at the +70 C mixed air (%s C/W at 62.1 C), every protection event at TJ 150 C or under"
      % (fmt(fx["rds"]), fmt(fx["bar"][0]), fmt(fx["bar"][1])))
    p("   withdrawn: one AONS21357 bounded at its printed %s mOhm (-10 V, 125 C), a corner BATDRV's 8.5 V does not reach; on L4-E11's one basis it needs"
      % fmt(fx["qa_hot"]))
    p("     %s C/W, which a board pour does not give one part" % fmt(fx["qa_bar"]))
    p("   18 A for 60 s after 10 A held: %s C (kept; R-159's fallback, which lowered it to 0.916 s, withdrawn); the docking pulse %s A against each FET's"
      % (fmt(fx["svc_tj"]), fmt(fx["dock"][0])))
    p("     ISM %s A at 25 C, met from the +70 C air for a share of at most %s in one FET (E11-30); the precharge at most %.5f A, no charge under %s V on SRN"
      % (fmt(fx["dock"][1]), fmt(fx["dock"][2]), fx["pre"][0], fmt(fx["pre"][1])))
    p("   the pair on battery: %s W at PS-IDLE-SPEC (%s A, %s %% of the pack's output), %s W at PS-TYP; L2 in supplement %s V, %s A, peak %s A against Isat %s A"
      % (fmt(fx["pair_idle"][1]), fmt(fx["pair_idle"][0]), fmt(fx["pair_idle"][2]), fmt(fx["pair_typ"][1]), *[fmt(x) for x in fx["l2"]]))
    p("25c THE CHARGER MINORS (L4-E11 15d) AND E11-34'S TEXTS (15e), CARRIED HERE")
    p("   inhibited, piecewise: SRN under %s V, VSYS at least %s V; over %s V, VSRN + %d mV within +-%d %% (the upper side an assumed reading of TI's"
      % (fmt(fx["pw"][0]), fmt(fx["pw"][1]), fmt(fx["pw"][2]), b1["inhib"][0], b1["inhib"][1]))
    p("     malformed column, A11-18); between, at least %s V; with the source overloaded VSYS follows the pack down to %s V (CELL_FUSED %s V, OCD1 %s A);"
      % (fmt(fx["pw"][3]), fmt(fx["supp"][0]), fmt(fx["supp"][1]), fmt(fx["supp"][2])))
    p("     with no pack and an overloaded source no floor, R-c sheds; the system node %s to %s V" % (fmt(fx["vsys_rng"][0]), fmt(fx["vsys_rng"][1])))
    for where, now, drafted in fx["e15"]:
        p("   carried: %s: '%s'" % (where, drafted))
    p("25d B3, EACH REQUIRED MODE'S GOVERNING LOCAL LIMIT (L4-E12 12a; read: the line as ruled / under CFL-002's C, A or B / maker-stated)")
    for k in ["M%d" % i for i in range(1, 10)]:
        md = M[k]
        r_ = md["ruled"]
        p("   %s %s W, lid %s, %+.1f C: %s %s; %s; %s" % (k, fmt(md["q"]), md["lid"], md["amb"], r_[0], "%s W/K read at %s" % r_[1:] if r_[1] else "no conductance",
                                                     "under C %s %s W/K read at %s" % md["cab"] if md["cab"] != md["ruled"] else "every option",
                                                     "stated: %s %s W/K read at %s" % md["stated"] if md["stated"] else "no stated alternative"))
    p("   the SGP41: sensing supported to +50 C only (Table 4); +55 C (Table 5) a screen; option C reports the channel not covered above %.1f C and switches"
      % fx["c_cover"])
    p("     the sensor off at %.1f C; K1 and K5 (section 24) are screens, withdrawn as lines" % fx["c_off"])
    p("25e B4, THE CHARGING HEAT AS A BALANCE (L4-E12 12b)")
    p("   input %.3f W less stored %.3f W less exported %s W = %s W (the profile %s W, the source path %s W, the charge path %s W, the charging cells %s W);"
      % (fx["bal"][0], fx["bal"][1], fmt(fx["bal"][2]), fmt(fx["bal"][3]), fmt(fx["bal"][4]), "%.5f" % fx["bal"][5], "%.5f" % fx["bal"][6], "%.3f" % fx["bal"][7]))
    p("     %s W with the ballasts' %s W; T3's start: %s" % (fmt(fx["bal_b"][1]), fmt(fx["bal_b"][0]),
                                                         "; ".join("+%s C at %s W needs %s W/K, read at %s" % (fmt(a), fmt(b), c, d) for a, b, c, d in fx["k78"])))
    p("25f B7, THE BATTERY-ONLY RUN COUPLED TO C1 (L4-E12 12c; ENERGY AND THERMAL)")
    p("   the reviewer's constant G: %s W/K reaches C1 at %s h, unshed %s C at %s h; %s W/K at %s h, unshed %s C at %s h" % tuple(fmt(x) for x in fx["cg"]))
    for r in fx["runs"]:
        p("   %s, C %s kJ/K: %s; the run %s h; the air at most %s C, the cells at most %s C"
          % (r[0], r[1], ("C1 at %s h, then the heat stage for %s h" % (r[2], r[3])) if r[2] else "C1 not reached", r[4], r[5], r[6]))
    p("   so C1 sheds the profile at %s to %s h where it acts, the run with the shed states %s to %s h; ENERGY ONLY %s h (%s Wh at %s W), not an unshed endurance"
      % (fmt(fx["c1"][0]), fmt(fx["c1"][1]), fmt(fx["c1"][2]), fmt(fx["c1"][3]), fmt(fx["eonly"][0]), fmt(fx["eonly"][1]), fmt(fx["eonly"][2])))
    p("25g THE BENCH POINTS (L4-E12 12d; R-104, R-151)")
    for name, q, lid, txt, tau, steady, fit in fx["pts"]:
        p("   %s at %s W, lid %s: tau %s h, steady at %s h, the fit %s h" % (name, fmt(q), lid, tau, steady, fit))
    p("25h WHICH LINES A READING CAN PASS (L4-E12 12e; the capacity proper %s W/K at K1's rise; 9's %s and %s W/K were a 50 m/s inside-flow bound)"
      % ("%.3f" % rc["capk1"][0], "%.3f" % fx["capfix"][0], "%.3f" % fx["capfix"][1]))
    for c in fx["cls"]:
        if c["need"] is None:
            p("   %s %s: no capacity at a zero rise; class (iii), the whole %s W" % (c["mode"], c["line"], c["short"][1]))
        else:
            p("   %s %s: needs %s W/K; bare %s / %s, route %s / %s; class (%s)%s%s" % (c["mode"], c["line"], c["need"], c["bare"][0], c["bare"][1], c["route"][0], c["route"][1], c["cls"],
                                                                             ", (%s) conservative" % c["cons"] if c["cons"] != c["cls"] else "", ", SHORT by %s W/K, %s W" % c["short"] if c["short"] else ""))
    p("   the class (iii) options (OW-10): E3-L, CFL-002's C, A or B, a closed-lid VOC ceiling (+%s to +%s C on the pack, +%s to +%s C on shore) or D-02b restated;"
      % tuple(fmt(x) for x in fx["voc_ceil"]))
    p("     E3-O, PDi's statement, the e-paper's window temperature (plate fraction %s: %s W/K; %s: %s W/K), CHO-001 or a deviation; E5, PDi's statement, a"
      % tuple(fmt(x) for x in fx["plate"]))
    p("     different e-paper or a deviation; charging is not class (iii) (in the heat stage alone %s W, %s and %s W/K, class (i))" % tuple(fmt(x) for x in fx["chg_hs"]))
    p("25i B5, THE SAFT'S CURRENT AT TEMPERATURE (L4-E10 10f, 10g)")
    p("   supported on published evidence for the temperature windows; current and temperature together, the storage dwell and recovery AWAIT Saft (the request")
    p("     expanded) or the limited sample qualification (one cell, a chamber from -40 to +85 C, a 25 A load, about two weeks, NZ$ %s); NOT YET ADOPTABLE;"
      % fmt(F["cb"]["u1"]["pulse_cost"]))
    p("     the owner's approval required (OW-3, OW-9; R-168)")
    p("25j THE REVIEW'S E2 AND E4, WHERE THEY CORRECT THIS RECORD")
    p("   the two sources are OR-connected onto VIN_RAW and share ONE charger input limit, not additive charger capacities (4b)")
    p("   at a 9.00 V plug the source's least, %s W at VBAT, does not sustain the %s W profile without the pack or shedding (4b, 4c, U-04)"
      % (fmt(F["e_env"][9][1]), fmt(F["idle"][1])))
    p("   the +70 C class needs each part's LOCAL air (the cooler's exhaust included), not the mean of the air probes: K3, K4 and K9 are screens (IF-11, 2c')")
    p("25k THE LEDGER (the review's E6): L4-E12:2.1 and 1.2 REGRESSED; L4-E7R:1.6 and 2.4 need B6's condition; not claimed closed here; the ledger is the")
    p("     coordinator's")
    p("25l WITHDRAWN IN THIS RECORD: K1 (the SGP41's +55 C) as option C's line; the texts that named no FET in (B1)'s battery path, and the system node")
    p("     10.0 to 16.884 V under (B1);")
    p("     the 502.3 ms start; R-159's fallback; Q39 as one AONS21357; the charging heat 46.859 W; 2.52 h as an unshed endurance; the Saft as covering every")
    p("     cell-limit row")
    b6 = F["sv"]["rm"]["b6"]
    p("25m B6, THE SOLAR GUARD ALREADY ON (L4-E7 at 11339ec7; section 23 carries its figures): as first drafted the guard failed four ratings when a")
    p("     36 V source steps on with it on; C131 and C132 become two 10 uF 100 V, C133 and C134 two 10 uF 50 V on PV_P, C126 330 pF, R97 30.0k (R-173):")
    p("     every rating MEETS, CONDITIONAL on the panel lead's loop inductance at least %s uH (its conductors' centres at least %s mm apart; R-176 row 2, R-180,"
      % (fmt(b6["l_uh"]), fmt(b6["mm"])))
    p("     Layer 7); re-run: the start %s A, CS101 %s A, check (b) %s ms, the static bound %s W; D-12's text and R-176's seven rows as L4-E7 gives them"
      % (fmt(b6["start"][0]), fmt(F["sv"]["rm"]["cs101"][0]), fmt(F["sv"]["rm"]["chkb"][0]), fmt(F["sv"]["rm"]["static"][0])))
    return L


def cons_in_short(F, D, st, reg):
    """The page's 'In short', generated: electrical feasibility, thermal feasibility and endurance apart, the change list and the exit."""
    cnt = {}
    for r in st.values():
        cnt[r[1]] = cnt.get(r[1], 0) + 1
    modes, energy, ef, heat = cons_budget(F, st)
    ch = cons_changes(reg)
    chs = {}
    for c in ch:
        k = c[8].split(" (")[0].split(",")[0]
        chs[k] = chs.get(k, 0) + 1
    tab = F["cb"]["tab_wh"]
    fx = F["fx"]
    M = fx["modes"]
    sh = {c["mode"]: c["short"] for c in fx["iii"]}
    bat20, batc, h20, hc = F["a1_bat"]
    prof = F["idle"][1]
    cand = F["a1_cand"]
    e = {x[0]: x for x in energy}
    return [
        "**The design.** A1 under D-06: one 4S3P pack inside the case, fed by the panel through board E's LT8705A stage and by "
        "the vehicle or shore supply through its ideal diode and the TPS48110-Q1 breaker, ORed onto VIN_RAW, converted once to "
        "VBUS20 by board A's LM5176 and once more by the charger onto VBAT, from which every load converter and both outlets run "
        "(section 1). The two sources share ONE charger input limit; their capacities do not add. The charger is (B1), TI's BQ25730 "
        "with the battery FET pair Q39 and Q40 (two BUK6Y10-30P) and board E's auxiliary domain on VSYS_E over the dock's pin 1, "
        "drafted (the board as drawn carries the BQ25731); the system node %s to %s V. A2 stays a proposal. There is no USB-C input."
        % (fmt(fx["vsys_rng"][0]), fmt(fx["vsys_rng"][1])),
        "**Electrical feasibility** (apart from thermal feasibility and endurance): %d interfaces, %d MEET, %d CONDITIONAL, %d NOT MET, %d "
        "PENDING (1d). The review's B1 and B2 on (B1)'s draft are D-13 (board E's auxiliary domain on the pack's side of the battery FET) "
        "and D-14 (the FET bounded at an unprinted corner, a fallback lowering 18 A for 60 s), ADDRESSED IN DRAFTS by L4-E11's fix round "
        "(board E on VSYS_E, R-177 and R-178; the pair, R-157; the held pack current at most %s mA, the start bounded to VSYS_MIN or a "
        "latch within %s s; every protection event at TJ 150 C or under at %s C/W per FET, 18 A for 60 s kept). IF-01 carries the "
        "KNOWN DEFECTS at the solar entry, single faults from L4-E7's panel-lead derivation: D-10, a stiff %s V source on the port, and "
        "D-11, a reversed panel, ADDRESSED IN DRAFTS by L4-E7's selected remedies (the over-voltage cut-off U21 with Q12, the return "
        "switch Q13, and for the guard already on, the review's B6, C131 and C132, C133 and C134, C126 and R97; R-173, "
        "apply_gen_sch_e_solar_guard.py, not applied; D-10 CONDITIONAL on the panel lead's loop inductance at least %s uH, D-11 on Q13's "
        "leakage above +25 C), and a residual band between 25 V and the cut-off named for layer 8 (R-175); D-12, CS116 and CS115 on the "
        "panel lead, is resolved in the drafted entry with the guard: %s D-01 to D-05 and D-08 are resolved in design, D-06 by L4-E11, "
        "D-07 and D-09 superseded (8a); every resolution is a DRAFT or a register row, none applied."
        % (len(st), cnt.get("MEETS", 0), cnt.get("CONDITIONAL", 0), cnt.get("NOT MET", 0), cnt.get("PENDING", 0), fmt(fx["held"][1]), fmt(fx["latch_s"]),
           fmt(fx["bar"][0]), fmt(F["sv"]["src"][1]), fmt(F["sv"]["rm"]["b6"]["l_uh"]), F["sv"]["rm"]["b6"]["d12"]),
        "**Endurance** (apart from feasibility; the approved profile %s W kept): battery-only %s h ENERGY ONLY (%.3f h with (B1)'s pair; "
        "%s with the tablet's window at the start) at room temperature and %s h with the cells at -10 C (energy only); ENERGY AND "
        "THERMAL (L4-E12 12c): on the conservative bound C1 sheds the profile at %s to %s h and the run with the shed states lasts %s "
        "to %s h; 2.52 h is not an established unshed endurance (2c'). Solar-assisted on the candidate panel's day: %s, %s; the steady "
        "load carried %s. The objective of 48 to 72 h is NOT MET: a deficit of %.1f W against the profile, +%s / +%s Wh of storage to "
        "add; a charger change does not close it. The tablet's optional charging takes at most %s Wh a day. The cold end's solar case "
        "is not computed. The proposed cells (PROPOSALS, energy only): the HL18650V %s, the Saft MP 176065 xtd %s to %s h (MODELLED; 2b')."
        % (fmt(prof), fmt(h20), bat20 / (prof + fx["pair_idle"][1]), e["B1"][5].split(" (")[0], fmt(hc), fmt(fx["c1"][0]), fmt(fx["c1"][1]),
           fmt(fx["c1"][2]), fmt(fx["c1"][3]), e["S1"][3], e["S1"][4].split(" (33")[0], e["S1"][6], ef["deficit"], fmt(ef["short48"]),
           fmt(ef["short72"]), fmt(tab), e["P1"][4].split(" ENERGY")[0], fmt(F["rc"]["saft_use"][2]), fmt(F["rc"]["saft_use"][3])),
        "**The change list:** %d changes in application order, none APPLIED (%s), each with its board, generator, apply "
        "script, dependency and release guard; the release records first (section 3)." % (len(ch), "; ".join("%s %d" % (k, chs[k]) for k in sorted(chs))),
        "**Thermal feasibility** (apart from both; L4-E12's fix round for the review's B3, B4 and B7): each required mode has its "
        "governing LOCAL limit (2c). At REQ-024's +40 C the required state is the heat stage; as ruled the SGP41's Table 4 +50 C "
        "governs it, %s W/K on the pack and %s W/K on shore; under CFL-002's C, A or B the cells' hot stop H1, %s and %s W/K (the "
        "SGP41's +55 C is an absolute rating, a screen, never a line). The profile's own line is M5, C1's air trigger at REQ-014's +20 C, "
        "%s W/K; charging on the design day (%s W, a balance) is governed by T4 on the charging cells, %s and %s W/K. T-H1 decides "
        "every class (i) and (ii) line; **four class (iii) lines no reading can pass**: E3-L lid closed as ruled (M3 short by %s W/K, "
        "M4 by %s W/K) and E3-O and E5 on the e-paper's operating row read to cover it unpowered (M6 short by %s W/K, M7 the whole "
        "%s W), each with its options for the owner (OW-10; 2c, section 6)."
        % (M["M1"]["ruled"][1], M["M2"]["ruled"][1], M["M1"]["cab"][1], M["M2"]["cab"][1], M["M5"]["ruled"][1], fmt(fx["bal_b"][1]),
           M["M8"]["ruled"][1], M["M9"]["ruled"][1], sh["M3"][0], sh["M4"][0], sh["M6"][0], sh["M7"][1]),
        "**The exit** (section 6, the owner's definition): Layer 4 power closure is not reached on this reading. U-02 is a closure "
        "condition T-H1's points decide for every class (i) and (ii) line (as ruled at +40 C a reading of at least %s W/K on the pack "
        "and %s W/K on shore; under C %s and %s W/K), its four class (iii) lines the owner's (OW-10); U-04 becomes a downstream "
        "qualification test once R-157, R-177 and R-178 are applied and stays a closure condition on the board as drawn; U-01 has a "
        "route supported on published evidence for the temperature windows (the Saft MP 176065 xtd), NOT YET ADOPTABLE (current at "
        "temperature and the storage dwell await Saft or the limited sample qualification; the owner's approval required), and the "
        "ruled 35E is unsuitable on its own published evidence for the margins. Beside them D-13 and D-14 (the review's B1 and B2) and "
        "the solar faults D-10 and D-11 are addressed in drafts, none applied (D-10 CONDITIONAL on the panel lead's loop inductance at "
        "least 2.47 uH, measured or specified by its conductors' spacing, R-180; D-11 on Q13's hot leakage), the band between "
        "25 V and the cut-off a residual for layer 8 (R-175). Each has its exact missing fact and the smallest experiment or "
        "manufacturer clarification that resolves it. The findings ledger, as filed: %d rows, %d CLOSED, %d CLOSED AS CONDITIONAL, %d "
        "OPEN DOWNSTREAM, %d STILL OPEN; the review's E6 found L4-E12:2.1 and 1.2 regressed and L4-E7R:1.6 and 2.4 needing B6's "
        "condition, and this record does not claim them closed. **Status: %s.**"
        % ((M["M1"]["ruled"][2], M["M2"]["ruled"][2], M["M1"]["cab"][2], M["M2"]["cab"][2]) + F["rc"]["ledger"] + (STATUS,)),
    ]


def cons_normal_op(F):
    """NORMAL OPERATION in the in-use envelope: section 11's conditions of L4-E12 (its output 11), each with its KIND since the fix
    round (12a): a screen at the mixed air, a mode's governing line, or no requirement; and the statements of the fix round on the
    profile, the battery-only run coupled to C1 and the charging heat."""
    cb, rc, fx = F["cb"], F["rc"], F["fx"]
    K, R = rc["K"], rc["R"]
    M = fx["modes"]
    gov = {"K1": "a SCREEN (the SGP41's Table 5, absolute; option C switches it off at %.1f C)" % fx["c_off"],
           "K2": "M2's governing line as ruled (CFL-002 open)", "K3": "a component SCREEN at the mixed air (the parts' local air is the line, T-H2)",
           "K4": "a SCREEN (the module's intake)", "K5": "a SCREEN, lid closed (M4's governing line as ruled is K2's, class (iii))",
           "K6": "M5's governing line (REQ-014 at +20 C)", "K7": "T3's start under M8 (T4 governs a running charge, 12a)",
           "K8": "T3's start under M9", "K9": "a SCREEN at the mixed air (M6: the e-paper's row governs; the RB9704's +70 C once PDi states)",
           "K10": "M7's maker-stated alternative (the e-paper's row governs E5, class (iii))",
           "X1": "no requirement: C1 sheds the profile", "X2": "no requirement: the withdrawn framing", "X3": "no requirement's mode"}
    rows = []
    for k in ["K%d" % i for i in range(1, 11)] + ["X1", "X2", "X3"]:
        c = K[k]
        rows.append((k, c["what"], c["lid"], "%.3f" % c["q"], "%+.1f C" % c["amb"], c["limit"], c["need"], R[k]["read"] if k in R else "none: no requirement", gov[k]))
    stmt = [
        "**The 42.8 W profile is not a required state at +40 C** (L4-E12's reconciliation, check 7; the earlier framing withdrawn). REQ-024's C1 sheds it on +50 C "
        "inside air or a +55 C cell to the reduced mode and the heat stage, and D-02b runs the reduced mode above +35 C ambient. The X "
        "rows show what no requirement asks: the profile under C1's +50 C at +40 C needs %s W/K (X1), its +70 C class %s W/K (X2, the "
        "reading %s W/K once read as deciding), the owner's conditional 42.4 W under +55 C %s W/K (X3)."
        % (K["X1"]["need"], K["X2"]["need"], fmt(rc["x2_read"][0]), K["X3"]["need"]),
        "**Section 11's conditions, each with its kind since the fix round** (L4-E12 12a): K1 and K5 (the SGP41's Table 5 +55 C, an "
        "absolute rating) and K3, K4 and K9 (the +70 C class and the module's intake at the MIXED air) are screens: a reading over them "
        "is necessary, never sufficient, since each part's LOCAL air, the cooler's exhaust included, is its line (T-H2). K2 is M2's "
        "governing line as ruled; K6 is M5's; K7 and K8 are T3's start under M8 and M9; K10 is M7's maker-stated alternative. The "
        "per-mode governing lines and their classes are 2c's table.",
        "**The profile's own line is M5 (K6), at REQ-014's +20 C:** %s W under C1's +50 C needs %s W/K, a reading of at least %s W/K; "
        "class (i). **The battery-only run coupled to C1** (L4-E12 12c, ENERGY AND THERMAL, the bound, C %s to %s kJ/K): C1 sheds the "
        "profile at %s to %s h and the run with the shed states lasts %s to %s h, the cells under H1; 2.52 h is ENERGY ONLY, not an "
        "established unshed endurance: the profile runs its whole energy unshed only from a constant %s W/K at 8 kJ/K (%s W/K at 10 "
        "kJ/K), and for any duration from M5's %s W/K. The bench shows it on T-H1's transient point and the built kit's run (5c)."
        % (fmt(M["M5"]["q"]), M["M5"]["ruled"][1], M["M5"]["ruled"][2], fx["runs"][0][1], fx["runs"][1][1], fmt(fx["c1"][0]), fmt(fx["c1"][1]),
           fmt(fx["c1"][2]), fmt(fx["c1"][3]), "%.3f" % fx["unshed"][0], "%.3f" % fx["unshed"][1], fmt(fx["unshed"][2])),
        "**Charging with the profile running** (M8, M9; L4-E12 12b, the review's B4): %.3f W in less %.3f W stored less %s W exported "
        "is %s W of heat (the profile's %s W at the battery node, the source path's %s W, the charge path's %s W, the charging cells' %s "
        "W), %s W with L4-E8's ballasts; section 11's 46.859 W had left the source path's loss on the profile out. T3's start needs %s "
        "to %s W/K (readings %s to %s W/K); T4 on the charging cells governs a running charge, %s and %s W/K (readings %s and %s W/K). "
        "The solar-assisted rows of 2b assume a charge the sealed case may not admit, so their solar part stays CONDITIONAL on M8 and "
        "M9; on the bound the profile charges only below %s C ambient (L4-E10)."
        % (fx["bal"][0], fx["bal"][1], fmt(fx["bal"][2]), fmt(fx["bal"][3]), fmt(fx["bal"][4]), fmt(fx["bal"][5]), fmt(fx["bal"][6]), fmt(fx["bal"][7]),
           fmt(fx["bal_b"][1]), fx["k78"][1][2], fx["k78"][3][2], fx["k78"][1][3], fx["k78"][3][3], M["M8"]["ruled"][1], M["M9"]["ruled"][1],
           M["M8"]["ruled"][2], M["M9"]["ruled"][2], fmt(cb["u1"]["charge_start"])),
        "**Electrical feasibility is a separate question** (1d, 8a): every interface row MEETS or is CONDITIONAL; D-10 to D-14 "
        "addressed in drafts or resolved. Thermal feasibility in normal operation is U-02's, decided per mode by T-H1's points, with "
        "four class (iii) lines the owner's.",
    ]
    return rows, stmt


def cons_normal_lines(F):
    rows, stmt = cons_normal_op(F)
    L = ["16e NORMAL OPERATION IN THE IN-USE ENVELOPE, on L4-E12's thermal reconciliation (its output 11, check 7) with each condition's kind since"
         " the fix round (12a): its need, the bench reading that meets it and what it governs (read, not recomputed)"]
    for r in rows:
        L.append("   %s %s; lid %s; %s W at %s; %s; needs %s W/K; a reading of at least %s; governs: %s" % r)
    for s_ in stmt:
        L.append("   " + s_.replace("**", ""))
    return L


def cons_normal_tables(F, D, st):
    rows, stmt = cons_normal_op(F)
    return {"| Condition |": ["| Condition | Requirement and mode | Lid | Heat (W) | Ambient | The limit | Needs (W/K) | A bench reading of at least (W/K) | Its kind since the fix round |",
                              "|---|---|---|---|---|---|---|---|---|"] + ["| %s |" % " | ".join(r) for r in rows]}


def poe_v(F):
    return F["poe"]["volts"]


if __name__ == "__main__":
    text, *_ = main()
    sys.stdout.write(text)
