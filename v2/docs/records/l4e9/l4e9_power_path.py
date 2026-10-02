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
    "l4e7r": ("v2/docs/records/l4e7/l4e7_stage_settings.out", "a0ec073de05abe918e983384181f1b6538b5347d099b709ad75e15f0f74091a9"),
    "l4e10": ("v2/docs/records/l4e10/l4e10_cell_thermal.out", "ce2d11f11eecfceef696eac1d6cda66d448cdfb3703d2fc69062e3a1a3f2aeac"),
    "d38999": ("v2/vendor/d38999/amphenol-d38999-iii-federal.pdf", "13a19268ba5939d9e4df5a20f9db84bb72e86525b82f0586c85696e42c126a2b"),
    "reqs": ("v2/ecad/tools/pcb_requirements.yaml", "b624ac495650a3592c45a37610375fb05bf7b775042cf3de7ec8979bc46a6e50"),
    "chgseq": ("v2/docs/review-packets/battery/CHARGER-STATE-SEQUENCE.md", "44fdf9a022c49337d60eeefd15b7e7267fb5a4659449f7dc5c38153a9786548f"),
    "yageo": ("v2/vendor/passives/yageo-cc-series.pdf", "61a606825ab314ea318cfb5362848a62fdffb851efa9818d642e9a541c56a648"),
    "lcsc": ("v2/ecad/tools/lcsc_fill.py", "6888362e4a3295d0e1d595f65c03d5c13353d4785d7821c86e91f470a1cf6410"),
    "ecss": ("v2/vendor/standards/ecss-q-st-30-11c-rev2-2021-06-23.md", "576256819950c4432b48769e5f642ee5bfb0eed4f025c03fb9727de7dbeabeea"),
    "chain": ("v2/ecad/tools/pcb_energy_chain.yaml", "a09ca0293afd1f7c553cbffb5b95bc33ae58688a4c20b8de65ec47c15d45996c"),
    # the update round: L4-E10's page, L4-E11's output, page and entry draft, L4-E12's output and page
    "l4e10md": ("v2/docs/records/l4e10/L4E10-CELL-THERMAL.md", "e7d09066c77b6a84cc7870cb3acdf2acd0a768cdb8e7cc1a4fc169d0193b7642"),
    "l4e11": ("v2/docs/records/l4e11/l4e11_power.out", "7af3ab81b3e5a12ed54972ec77fe552fd80fd43e225b53e5e5040b030ce1e8ef"),
    "l4e11md": ("v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md", "ccf3e8a87b49ad87d19ef61305a62aa845c9c7a9b29230b1c18a1334db514eaa"),
    "e11entry": ("v2/docs/records/l4e11/apply_gen_sch_e_entry.py", "418ea548a833b49f2fe923cb5ff776938bf73759521df781b4716c71536c4d32"),
    "l4e12": ("v2/docs/records/l4e12/l4e12_thermal.out", "a73d0c7f73280c7a869b46ea1a78119590fa5db70a34a7671273f448fab976a0"),
    "l4e12md": ("v2/docs/records/l4e12/L4E12-ELECTRONICS-THERMAL.md", "d6f501457675091c65b50fe4d3fbf4943986848b444c317db09057fd792e3336"),
    # the outside-contact texts the owner's list names (drafts the owner sends; the session contacts no one)
    "cl_topwell": ("v2/docs/records/l4e10/clarification/topwell-hl18650v.txt", "5e81a4a215bcc7e66fd98d7756d3a1f6f6a5a4984b910f268ca8289e14451d56"),
    "cl_eaton": ("v2/docs/records/l4e10/clarification/eaton-scf9550.txt", "9dffb95e8b4874fc0d08824b39d6174372a64e0cbda066241900d6ffdcdc5cb2"),
    "cl_pdi": ("v2/docs/records/l4e12/clarification/pervasive-displays-e2370ks0c1.txt", "4f7db1348cc0b4aca473c17f010085ca9095bf538f580c48804be5602418c117"),
    "cl_sensirion": ("v2/docs/records/l4e12/clarification/sensirion-sgp41.txt", "43c47549235fe6e8162b200324cedd7b34a342bb2a1cb0abf97311f39a48da83"),
    "cl_adi": ("v2/docs/records/l4e7/clarification/analog-devices-lt8705a.txt", "97d8217092eae7ac41cc7c3a7303696cf9494bfc8df14171fcc69c6862f86cfa"),
    "cl_milliohm": ("v2/docs/records/l4e7/clarification/milliohm-hojlr2512.txt", "e920420419a677e0b723f8c09b26dc817efcc29124dc742fc4e813c4279ff8f6"),
    "cl_vishay": ("v2/docs/records/l4e7/clarification/vishay-wsl2512.txt", "0d91a42dfa59432b71ee5bd0f7abf707f28459a1197dc3c599ea9dce451ab11c"),
    "cl_ti": ("v2/docs/records/l4e7/clarification/texas-instruments-ina169.txt", "405fb3988f41d8ac98dce3d5ec1cb4af1a0b5d635b109cf71772557c25ab3854"),
    "ti_review": ("v2/docs/review-packets/battery/REVIEW-REQUEST.md", "91a257430cbeb53a672ca57592bb75092a98a761d1c8ee7bbaefa95e339b102e"),
    "cl_gc": ("v2/docs/records/l4e12/clarification/ground-control-rockblock-9704.txt", "738245875bec70c55d1ec105fb566248c98351095a268ffcd25d2b76e3bea85f"),
    "cl_nicerf": ("v2/docs/records/l4e12/clarification/nicerf-sa868.txt", "92324668c17d4f6c7b45b6f9528d08a7c2ae4df1c1839fc82fb6eeb9f7a585b7"),
    "cl_bulgin": ("v2/docs/records/l4e12/clarification/bulgin-pxp4043c.txt", "c7accd3dd6dc1d8993de6ffc37e4febba71302e878b3cdf0f3f2f30bc2a4457e"),
    # update rounds 3 and 4: L4-E13 (U-03), accepted by the coordinator's check 3 at fae419d1 and, after set 25 (L4-E7R
    # accepted), check 4 at 33b6b7be; read from the tree
    "l4e13": ("v2/docs/records/l4e13/l4e13_panel.out", "436344ef3c00df7d09509b01a27e4bd3b4ff42825b180d8dcbe14bc1bfb6773a"),
    "l4e13md": ("v2/docs/records/l4e13/L4E13-PANEL.md", "1c7f11716db4c2f2d1fa31327050afac8eb225c8ed8552091845cbdb090bf191"),
    "l4e13chk": ("v2/docs/records/l4e13/checks/check-l4e13-3.md", "88539c7aeaf2f99d8ed0364ac86f0cb312b9322eeeb6ac860ffa3d35e53ec306"),
    "l4e13chk4": ("v2/docs/records/l4e13/checks/check-l4e13-4.md", "5a08480af4695e61752d04852d8647e0276f292771596281968acf8903bc73e8"),
    "cl_sunpower": ("v2/docs/records/l4e13/clarification/sunpower-spr-e-flex-100.txt", "453a5a957648a322dc6b011c4c0a601c4af7a41d527f7ef4ab3cd0b79538e08c"),
    "cl_solbian": ("v2/docs/records/l4e13/clarification/solbian-sx-156.txt", "fb66bfb76e7e252ce9df361cd59dcc756be2764a1dcfbd5ef8632346b7a36b1f"),
}
# Read from the tree when the tree's file is the pinned one, else from the named commit: L4-E7R's selected solution (fnd/l4e7,
# accepted, check 4 at 91e9a4b5), L4-E10's final record (fnd/l4e10, closing check 573c8b8f), L4-E11's (fnd/l4e11, accepted,
# closing check a15ab384) and L4-E12's (fnd/l4e12, accepted, closing check db41c95d)
COMMIT_LABEL = {"675b8068": "fnd/l4e7, accepted, closing check 91e9a4b5", "79b2f568": "fnd/l4e10, final, closing check 573c8b8f",
                "3298d1f1": "fnd/l4e11, accepted, closing check a15ab384", "a86be47b": "fnd/l4e12, accepted, closing check db41c95d"}
FROM_COMMIT = {"l4e7r": "675b8068", "l4e10": "79b2f568", "l4e10md": "79b2f568", "l4e11": "3298d1f1", "l4e11md": "3298d1f1",
               "e11entry": "3298d1f1", "l4e12": "a86be47b", "l4e12md": "a86be47b", "cl_topwell": "79b2f568", "cl_eaton": "79b2f568",
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

    def __init__(self, what, a, rel, b, unit, cls, src, scope="selected"):
        self.what, self.a, self.rel, self.b, self.unit, self.cls, self.src, self.scope = what, a, rel, b, unit, cls, src, scope
        if cls == "PENDING" or a is None or b is None:
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
        ab = "%s %s %s %s" % (fmt(self.a), self.rel, fmt(self.b), self.unit) if self.met is not None else "(%s)" % self.unit
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
    for part in ("SMCJ18A", "SMCJ22A", "SMCJ28A", "SMCJ40A"):
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
    if [x[0] for x in F["e11_items"]] != ["E11-%02d" % i for i in range(1, 24)]:
        refuse(3, "L4-E11's downstream items are not E11-01 to E11-23")
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
    return F, where


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
    p("   the register: R-35 restated as PANEL-ACC, R-52 the unit's trace rerun, R-29 J_SOLAR's lead at A-3(b)'s current, R-148 A-3(c)'s rating")
    p("     for J_SOLAR and PV_IN (Layer 6; its interface text amends LH-02, no new handover row), R-149 M3's n at or under 2; the owner's items")
    p("     OW-6 (the purchase and the measurement) and the two route-1 drafts in OW-4")
    held = [g["n"] for g in GATE if g["verdict"] != "PASS"]
    arch = [c["id"] for c in CHOICES if c["class"] == ARCH]
    p("   the gate: NOT CLOSED (criteria %s): criteria 1 and 5 on %s, each still able to overturn the architecture on named evidence;"
      % (", ".join(str(n) for n in held), ", ".join(arch)))
    p("     criterion 2 CONDITIONAL with no material defect open, on its rows' named evidence; criteria 3 and 4 PASS")
    return L


# ------------------------------------------------------------------------------------------------------- the rows
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
        "prot_a": "none (a bare panel)", "prot_b": "F2; the 50 V bulk on PV_P ahead of the sense bank; D4 one-way clamp and C71 to C74 on TRK_VS; the INB filter, %d x 100 nF C0G across R66 %s (%s to %s ms) (L4-E7R, drafted in apply_gen_sch_e_backstop.py)" % (F["filt_n"], F["r66"], fmt(F["tau_min_ms"]), fmt(F["tau_max_ms"])),
        "settled": "l4e (O-1), L4-E7R at 675b8068 (accepted, check 4 at 91e9a4b5), L4-E13 at fae419d1 (accepted, check 3; PANEL-ACC)", "checks": [
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
        "v": "solar: the corrected knee (HIZ certain below %s V, a flat %s A from %s V to %s V, L4-E11 E11-09; L4-E5's drawn-line figures %s / %s / %s V) to the ceiling %s V; vehicle 9 to %s V at the plug (VIN_RAW %s V at %s A from 9.00 V); at most %s V (the selected OV maximum; %s V the basis) | U2 VIN %s V absolute"
             % (fmt(F["knee_hiz"]), fmt(F["knee"][0]), fmt(F["knee"][1]), fmt(F["knee"][2]), fmt(F["hiz_below"]), fmt(F["hiz_out_above"]), fmt(F["pin_reg_from"]), fmt(F["trk_ceiling"][2]), fmt(D["vrev"]), fmt(F["e_svc"][0]), fmt(F["e_svc"][1]),
                fmt(F["e_ov_off"][2]), fmt(round(F["ovlo_sel"][2], 2)), fmt(F["u2_vin_abs"])),
        "i": "in service at most %s A from a 9.00 V plug (L4-E11 3e; %s A at VIN_RAW 9 V under L4-E5's line); at the window %s A from the tracker; the front end's fault current at most %s A (R11 8 mOhm, R12 12 mOhm; %s A at 7 mOhm) | declared %s A; four Mill-Max pins at %s A each"
             % (fmt(F["e_svc"][1]), fmt(F["h3"][9.0][1]), fmt(round(D["trk_i_settle"], 2)), fmt(round(D["vin_fault"], 3)), fmt(round(D["vin_fault_7"], 3)), fmt(F["vin_raw_a"]["typ"]), fmt(F["millmax_a"])),
        "loss": "the dock's contacts and 12 AWG wires (IF-AE-DOCK)", "therm": "about 6 K rise of the pins at 14.10 A (IF-AE-DOCK, INFERRED)",
        "prot_a": "the entry (IF-04, IF-05); D2 on board E", "prot_b": "D2 SMCJ40A on board A; U34's restart guard",
        "settled": "l4e5, l4e6, IF-AE-DOCK, DECISION-31 (A-N1), L4-E11 (3e, 3f)", "checks": [
            Chk("the highest steady VIN_RAW (the %s V basis, over the selected OV maximum) inside U2's absolute rating" % fmt(round(F["ovlo_sel"][2], 2)), round(F["ovlo_sel"][2], 2), "<=", F["u2_vin_abs"], "V", "MAKER", "out 11, out 12; TI SNVSAI1D 6.1"),
            Chk("the in-service maximum from a 9.00 V plug inside the declared VIN_RAW current", F["e_svc"][1], "<=", F["vin_raw_a"]["typ"], "A", "INFERRED", "L4-E11 3e"),
            Chk("the front end's fault current at the onset of its average limit inside the declared VIN_RAW current", D["vin_fault"], "<=", F["vin_raw_a"]["typ"], "A", "INFERRED", "l4e6 out 5 (R11 band, 20.887 V, 0.93, %s V)" % fmt(F["avg_from"])),
            Chk("one Mill-Max pin with one of four open at that fault current", D["vin_fault"] / 3.0, "<=", F["millmax_a"], "A", "INFERRED", "Mill-Max p.28 (the 0850 to 0853 sibling figure)"),
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
        "v": "VBUS20 %s to %s V, bound %s V | U3 VBUS and VSYS %s V absolute, VBUS %s V recommended; VBAT %s to %s V; SYSOVP %s / %s / %s V"
             % (fmt(F["vbus_band"][0]), fmt(F["vbus_band"][1]), fmt(F["vbus_bound"]), fmt(F["u3_abs"]), fmt(F["u3_rec_vbus"]), fmt(D["vbat_low"]), fmt(F["chg_v_max"]), fmt(F["sysovp"][0]), fmt(F["sysovp"][1]), fmt(F["sysovp"][2])),
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
        "v": "%s V (the gauge's CUV %s V a cell) to %s V; BATOVP %s V | D1 SMCJ18A standoff %s V, breakdown %s V minimum; the pack FETs 30 V"
             % (fmt(D["vbat_low"]), fmt(F["cuv"]), fmt(F["chg_v_max"]), fmt(F["batovp"]), fmt(sm18["vr"]), fmt(sm18["vbr_min"])),
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
        "id": "IF-11", "title": "VBAT to the load converters (slot rails, device rail, logic, monitor, heater; board E's always-on on CELL_F)",
        "a": "VBAT", "b": "the 39 loads of PS-IDLE-SPEC and the PS-ALLTX set",
        "v": "%s to %s V | the converters assumed to run to %s V (SHORTLIST.md 2, not shown)" % (fmt(D["vbat_low"]), fmt(F["chg_v_max"]), fmt(D["vbat_low"])),
        "i": "asked: PS-IDLE-SPEC %s / %s / %s W; PS-ALLTX %s / %s / %s W (low / plan / high at the pack terminals); %s W of PS-IDLE-SPEC has no document | available: each converter's own rating (pwr_budget.py)"
             % (fmt(F["idle"][0]), fmt(F["idle"][1]), fmt(F["idle"][2]), fmt(F["alltx"][0]), fmt(F["alltx"][1]), fmt(F["alltx"][2]), fmt(F["undoc_w"])),
        "loss": "the converters' makers' floors (pwr_budget.py)",
        "therm": "the heat per state, POWER-THERMAL 9; at T-H1's binding line %s W/K (lid open, fans; L4-E12) E3-O's mixed air %.2f C (%s W with the ballasts) and E5's %.2f C under the hold (%s W); at LO-01a's floor with no hold %.2f C and %.2f C (the design as it stands)"
             % (fmt(F["gc"]), F["e3o_line"], fmt(round(F["e3o_wb"], 3)), F["e5_line"], fmt(round(F["e5_hold_wb"], 3)), F["floor_air"][0], F["floor_air"][1]),
        "prot_a": "the eFuses (monitor %s A peak declared, heater) and the stages' limits" % fmt(F["vmon"]["peak"]), "prot_b": "each converter's own",
        "settled": "pwr_budget.out, load_trace.out, POWER-THERMAL, L4-E12 at a86be47b (accepted, check db41c95d)", "checks": [
            Chk("the profile's %s W with no document measured or bounded by a maker" % fmt(F["undoc_w"]), None, "<=", None, "a measurement", "ASSUMPTION", "load_trace.out; replay out 13"),
            Chk("E5's mixed inside air under the hold at T-H1's binding line (%s W/K lid open with the fans) under the +%s C parts (MESHSAT-1478)" % (fmt(F["gc"]), fmt(F["parts_hot"])),
                F["e5_line"], "<=", F["parts_hot"], "C", "CONDITIONAL", "L4-E12 out 4c, 4d (MODELED): T-H1 at or over the line, the hold's reference within +-%s K, the fans' rating, the parts out of the exhaust; unresolved choice U-02" % "%s" % F["hold_ref"]),
            Chk("E3-O's mixed inside air with every radio on at that line under the +%s C parts" % fmt(F["parts_hot"]), F["e3o_line"], "<=", F["parts_hot"], "C", "CONDITIONAL", "L4-E12 out 4d (MODELED; E3-O alone needs %s W/K); unresolved choice U-02" % fmt(F["g_e3o"])),
            Chk("the inside air at LO-01a's floor (%s W/K) with no hold, E5's +60 C dwell, under the +%s C parts" % (fmt(F["th1"]), fmt(F["parts_hot"])),
                F["floor_air"][1], "<=", F["parts_hot"], "C", "MODELED", "L4-E12 out 2c (L4-E10's corner plus the ballasts, MESHSAT-1478 as found)", scope="drawn"),
            Chk("every load converter runs to the 3.00 V line (10.0 V stack)", None, "<=", None, "a record", "ASSUMPTION", "SHORTLIST.md 2: no record"),
            Chk("TPS2596 eFuses (U21, U22) on VBAT at the SYSOVP maximum", F["sysovp"][2], "<=", F["tps2596_abs"], "V", "MAKER", "TI TPS2596 7.1"),
        ]})
    pd = F["pd"]
    R.append({
        "id": "IF-12", "title": "VBAT to the USB-C outlet (U19 LM5176, Q27, R138, J_USBC_OUT; U18 TPS25740A), the tablet's optional charge",
        "a": "VBAT", "b": "the outlet's sink (a tablet), 5, 9 and 15 V at 3 A",
        "v": "VBAT %s to %s V into U19 | 5 / 9 / %s V contracts, each held inside the maker's window (L4-E4 bench (a))" % (fmt(D["vbat_low"]), fmt(F["chg_v_max"]), fmt(pd["volts"])),
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
        "v": "VBAT %s to %s V regulated, %s V at the pack-open bound, %s V at D1's rated pulse, into R227 and U16 (POE_VIN at most %s V under VBAT in the boost current-limit case) | %s V; U17 (INA226) IN+ on VBAT, IN- and VBUS on POE_VIN (part A; as drawn on POE_OUT and +54V_POE, pins %s and %s); INA226 %s V absolute, %s V common mode"
             % (fmt(D["vbat_low"]), fmt(F["chg_v_max"]), fmt(round(D["pack_open"]["v_end"], 3)), fmt(F["SMCJ18A"]["vc"]), fmt(round(A["u17_mv_fault"] * 1e-3, 3)), fmt(poe["volts"]),
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
        "v": "VBAT %s to %s V into U13 | %s V; PA_EN gated by EMCON and TX_INHIBIT_n" % (fmt(D["vbat_low"]), fmt(F["chg_v_max"]), fmt(pa["volts"])),
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
                   "9.00 V at the plug is a CONDITIONAL CANDIDATE on E11-05, E11-06, E11-09, E11-22 and E11-23 (U-04); the electronics at the margins "
                   "are CONDITIONAL on T-H1 at or over 2.159 W/K and L4-E12's conditions (U-02); the battery path's thermal design is FEA-008's (U-01); "
                   "PS-ALLTX's chain at 18 A for 60 s (PWR-F12) is an open obligation",
     "overturn": "possibly, on named evidence only: U-01 on the HL18650V's specification (D-06's pack energy and protection settings), U-02 on "
                 "T-H1's reading and the fans (the sealed case's thermal design or a device-set re-pick), U-04 on TI's N1 and the bench's VSYS "
                 "(the charger's power path); the rest, the panel unit included, resolves by a value, a part or a measurement on the same topology"},
    {"n": 2, "criterion": "material power-path defects have engineering resolutions and bounded supporting calculations",
     "rows": ["IF-01", "IF-02", "IF-04", "IF-05", "IF-13"], "choices": [], "verdict": "CONDITIONAL",
     "constraint": "no material defect is open: D-01 to D-05 and D-08 are resolved in design (drafted or bounded), D-06 is resolved in design by "
                   "L4-E11's interconnect with its evidence items (E11-10 to E11-16), D-07 and D-09 are superseded by the replacement of the LM5069 "
                   "(E11-19 finds no new one); the resolutions rest on CONDITIONAL rows (the loop's typical rows, the makers' installed and "
                   "short-time ratings, R227's pulse rating, the start into a hard short's transconductance bound) and the hot short in service "
                   "on open evidence (the loop's inductance, E11-20)",
     "overturn": "no: each resolves by a part, a rating or a measurement at the vehicle or the solar entry"},
    {"n": 3, "criterion": "remaining assumptions explicit, with their impact and verification method",
     "rows": [], "choices": [], "verdict": "PASS", "constraint": "", "overturn": ""},
    {"n": 4, "criterion": "downstream implementation changes, layout constraints and tests have named owners and acceptance criteria",
     "rows": [], "choices": [], "verdict": "PASS", "constraint": "", "overturn": ""},
    {"n": 5, "criterion": "no unresolved uncertainty could overturn the selected architecture while described as routine later testing",
     "rows": ["IF-09", "IF-10", "IF-11"], "choices": ["U-01", "U-02", "U-04"], "verdict": "CONDITIONAL",
     "constraint": "three unresolved choices could overturn it and are named as such, not as later testing: U-01 (FEA-008's cell; the owner's two "
                   "items), U-02 (MESHSAT-1478; CONDITIONAL on T-H1 at or over 2.159 W/K and L4-E12's conditions, CFL-002 the owner's question), "
                   "U-04 (a CONDITIONAL CANDIDATE with the evidence that closes it); an owner and an acceptance criterion do not close them. U-03 "
                   "left this category with L4-E13's acceptance: a CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC, R-35) that decides which "
                   "unit, not the topology or the source class",
     "overturn": "yes, on named evidence only: U-01 (D-06's pack energy and settings), U-02 (the sealed case's thermal design, the fans, the "
                 "device set), U-04 (the charger's power path); U-03 no longer can, unless route 2 proves infeasible with route 1 still "
                 "closed (L4E13-06)"},
]

ARCH = "ARCHITECTURE-LEVEL CHOICE"                              # could overturn the architecture: named by criteria 1 and 5
DOWNSTREAM = "CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC)"  # U-03 since L4-E13: decides a unit, in the register as R-35
# The unresolved choices that could overturn the architecture (category b), and U-03, which left it with L4-E13's acceptance. An owner and an acceptance criterion close an
# assignment, never one of these: each stays open, and keeps every criterion that names it from PASS, until its evidence lands.
CHOICES = [
    {"id": "U-01", "title": "FEA-008: the battery path's cell and thermal design (L4-E10, final)", "class": ARCH,
     "constraint": "LO-01d to LO-01g (E3-O, E5, E3-S, E4-S with the pack fitted) have no route that holds on held evidence; LO-01a holds only with "
                   "T-H1 at least 1.666 W/K in both lid states (1.8058 W/K with L4-E8's ballasts counted, L4-E12)",
     "settles": "the HL18650V's signed specification confirming storage at +71 C and -33 C at the stored charge and the +80 C idle limit, then L4-E10's "
                "margins re-run (1.06 K under H1 and 0.97 K under U2's INFERRED trip at LO-01e); T-H1 measured in both lid states",
     "alternatives": "(II) a wide-temperature 18650 in D-06's 4S3P (recommended, CONDITIONAL); (I) the 35E with powered cooling (INCONCLUSIVE: up to "
                     "35 W into the sealed case); (III) latent storage and a primary-fed heater (rejected at LO-01d to f; added energy storage under D-06); "
                     "a requirement change (the owner's, D-29)",
     "owner": "(1) send the drafted request for the specification; (2) once it confirms, approve the cell change (D-06's about 145 Wh to about 121 Wh "
              "nominal, REQ-046 and REQ-077 restated with the cell, about USD 42 a pack); if declined, LO-01d to g stay a release gate (OW-2, OW-3)",
     "overturns": "on the specification's answer: D-06's pack energy (16.4 % less usable) and the pack's protection settings under (II); with a "
                  "negative answer and no requirement change LO-01d to g keep no route on held evidence, and (I)'s powered cooling (up to 35 W into "
                  "the sealed case) would reopen U-02's heat budget; the power path's topology stays",
     "rows": ["IF-10"]},
    {"id": "U-02", "title": "MESHSAT-1478: the electronics against the inside air at D-02a's +55 C margin and E5's +60 C dwell (L4-E12)", "class": ARCH,
     "constraint": "L4-E12's route (c), E3-O as stated and the hold in E5 only, is CONDITIONAL on T-H1 lid open with the fans at or over 2.159 W/K "
                   "(E3-O alone 1.806 W/K; 2.709 W/K with no hold), the hold's reference within +-0.899099 K of the mixed air, the parts out of the "
                   "cooler's exhaust, the fans' rating (D-18), the pushbuttons and two regulators changed and PDi's statement; at the line E3-O's air "
                   "is 67.55 C and E5's 70.00 C, while the design as it stands (LO-01a's floor, no hold) reaches 76.25 C in E5; inside the envelope "
                   "no location holds the SGP41 to its maker's conditions (CFL-002)",
     "settles": "T-H1 measured in both lid states at or over 2.159 W/K with the picked fans; the forced hold and the SGP41's shutdown at room "
                "temperature; E3-O and E5 with thermocouples on the +70 C parts (R-104, R-109); PDi's and Sensirion's answers; the owner's answer "
                "to CFL-002",
     "alternatives": "(a) the enclosure alone at 2.709 W/K with no hold; (b) wider-rated parts (five are device-set parts, the owner's, CHO-001); "
                     "the plate coupling if T-H1 reads between 1.806 and 2.159 W/K; a device-set re-pick or a stated deviation of E3-O's "
                     "configuration (the owner's)",
     "owner": "CFL-002, the SGP41 in the envelope: A (a BME688-class sensor in its place, L4-E12's recommendation), B (the VOC channel dropped) or C "
              "(the SGP41 kept, its channel reported as not covered); send PDi's and Sensirion's requests (OW-1, OW-4); later, only on T-H1's "
              "reading, a re-pick or a deviation",
     "overturns": "on T-H1's reading and the fans: under 2.159 W/K E5 fails for the +70 C class unless the plate coupling holds, under 1.806 W/K E3-O "
                  "too, so the sealed case's thermal design (no vent, the ruling of 7 September 2026) or the device set (CHO-001) could change; a "
                  "stopped fan takes the enclosure to its fans-off conductance; CFL-002 changes a sensor, not the architecture; never the power "
                  "path's topology",
     "rows": ["IF-11"]},
    {"id": "U-03", "title": "O-1: the solar panel inside REQ-016's window (L4-E13, accepted)", "class": DOWNSTREAM,
     "constraint": "L4-E13 (accepted, checks 3 and 4 at fae419d1 and 33b6b7be): route 1, a maker's warranted band, closes nothing today; route 2, one identified "
                   "SunPower SPR-E-Flex-100 measured against A-1 to A-3, is feasible on a unit equal to the typical rows: A-1 Vm20 + U_V 24.1505 V "
                   "against 25.000 V at -20 C and 1000 W/m2 (margin 0.8495 V), the window Voc25 20.315 to 22.156 V; A-2 27.0849 W above "
                   "1.365591 W; A-3 (a) 3.987 A, the conservative bound over L4-E7R's regulation (2.5485 A nominal, at most 2.9337 A at 25 V) "
                   "and backstop (trip at most 3.7408 A), (b) 8.1817 A, (c) 13.82 A, a COMPONENT_LIMITATION on J_SOLAR and PV_IN; A-4 on "
                   "L4-E7R's two layers (the regulation's 25 V corner 73.3436 W; the backstop's static bound 93.5521 W, CONDITIONAL on G_CM and "
                   "the VIN+ bias); no physical unit accepted",
     "settles": "one unit bought and measured (M1 to M3 and A-2's reading at the specification) and accepted on A-1, A-2 and A-3(b) (R-35); its "
                "trace rerun (R-52); J_SOLAR and PV_IN with a rating that covers A-3(c) (R-148); M3's n at or under 2 for the disturbance check (R-149); "
                "L4-E7R's regulation and backstop applied (drafted) for A-3(a) and A-4",
     "alternatives": "route 1, a maker's warranted band inside the window (the drafts to SunPower and Solbian, OW-4); another unit of the same "
                     "curve shape inside the window; REQ-016's window restated (the owner's; not needed)",
     "owner": "the purchase and the measurement of one unit (OW-6) and sending the two route-1 drafts (OW-4): actions, not questions",
     "overturns": "nothing of the architecture: it decides which unit, not the topology and not the source class; REQ-016's window, the stage, "
                  "its hold and its 100 W control stay; it returns to an architecture-level choice only if route 2 proves infeasible with "
                  "route 1 still closed (L4E13-06)",
     "rows": ["IF-01"]},
    {"id": "U-04", "title": "source-only and dead-pack operation (L4-E11: arrangement (A), a CONDITIONAL CANDIDATE)", "class": ARCH,
     "constraint": "L4-E11 selects arrangement (A), the drawn charger with no battery FET, with rules R-a to R-d and the replaced entry: at a 9.00 V "
                   "plug the source delivers 29.09 to 42.52 W at VBAT and the shed warm-up (28.12 W plan) is carried with 0.98 W in hand while P1 "
                   "stays at most 20.51 W; REQ-015 at 9.00 V at the plug is a CONDITIONAL CANDIDATE, not closed: at the load's hi corner P1 "
                   "(35.24 W) exceeds the source's least, TI states neither VSYS's regulation with no battery under load steps (N1) nor what it "
                   "regulates with charge inhibited in state S2 (N2, Q-TI-3), the cells' warming time has no held model, and R-b's cases (ii) "
                   "and (iii) are INCONCLUSIVE",
     "settles": "E11-05 (TI's answers: N1, N2 for S2, Q-TI-2), E11-06 (R-85 extended: P1 at most 20.51 W, the front end at least 0.88021, the pin's "
                "band, the breaker never tripped, VSYS's step response), E11-09 (the knee drawn), E11-22 (R-b's cases), E11-23 (the warm-up time "
                "at the plug)",
     "alternatives": "(B) a charger with a battery FET power path (it reopens L4-E4 to L4-E8's settings on a part whose sheet is not held); (C) a "
                     "pre-charge path on board P (its resistor's heat in the sealed case); VSYS's capacitance first (E11-07); REQ-015's acceptance "
                     "restated (the owner's; not needed while (A) stands)",
     "owner": "none unless the evidence is negative and REQ-015 is restated; TI's questions are an outside contact the owner makes (REVIEW-REQUEST.md, "
              "Q-TI-3 restated as N2 with N1 added; OW-4)",
     "overturns": "on TI's N1 or the bench's VSYS under the kit's load steps with no battery: the charger's power path, VSYS's capacitance first "
                  "(E11-07) and only then (B); on the efficiency, the pin's band or P1's load, the knee or F1, not the topology",
     "rows": ["IF-09", "IF-10"]},
]

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
]
OWNERS = ["Layer 4 coordinator", "Layer 5 interfaces", "Layer 6 components", "Layer 7 mechanical", "Layer 8 board A generator owner",
          "Layer 8 board E generator owner", "Layer 8 board P generator owner", "Layer 9 pre-layout analysis", "prototype bench",
          "firmware owner", "TEST-PLAN owner", "Layer 8 board B generator owner", "Layer 8 board C generator owner", "CONOPS owner"]

# The owner's items: decisions and outside contacts only, kept apart from the engineering work (the register). Each names the
# pinned document it rests on; the session contacts no outside party, it prepares the texts.
OWNER_ITEMS = [
    {"id": "OW-1", "what": "CFL-002 (U-02): the SGP41 in the battery bay against REQ-042's VOC channel inside the envelope: A, a BME688-class "
                           "sensor in its place (L4-E12's recommendation); B, the VOC channel dropped; C, the SGP41 kept, its channel reported as "
                           "not covered above a 49.0 C reading and after storage outside 5 to 30 C",
     "docs": [("l4e12md", "L4-E12's page, section 8")]},
    {"id": "OW-2", "what": "U-01, item 1: send the drafted request for the HL18650V's signed product specification (Yichun Topwell Power)",
     "docs": [("cl_topwell", "the request")]},
    {"id": "OW-3", "what": "U-01, item 2, once that specification confirms L4-E10's rows: approve the cell change inside D-06's 4S3P (about 145 Wh "
                           "to about 121 Wh nominal, REQ-046 and REQ-077 restated with the cell, about USD 42 a pack); if declined, LO-01d to g stay a "
                           "release gate",
     "docs": [("l4e10md", "L4-E10's page, section 8")]},
    {"id": "OW-4", "what": "the outside-contact drafts to send (the owner chooses the channel)",
     "docs": [("cl_topwell", "Yichun Topwell Power: the HL18650V's signed specification (U-01)"),
              ("cl_pdi", "Pervasive Displays: the E2370KS0C1's storage and operation (U-02)"),
              ("cl_sensirion", "Sensirion: the SGP41's duration, recovery and storage (U-02, CFL-002)"),
              ("cl_adi", "Analog Devices: the LT8705A's IMON_IN limits (the 100 W bound; R-33, R-101)"),
              ("cl_milliohm", "Milliohm: the HoJLR2512's temperature coefficient below +25 C (R-101)"),
              ("cl_vishay", "Vishay: the WSL2512's pulse capability (R-101)"),
              ("cl_ti", "Texas Instruments: the INA169's error envelope (R-101)"),
              ("ti_review", "Texas Instruments: the battery packet's Q-TI-2 and Q-TI-3, with L4-E11's N1 and N2 for S2 added before sending (U-04; E11-05, R-114)"),
              ("cl_eaton", "Eaton: the SCF9550 above +60 C and in storage (PWR-F12; R-103)"),
              ("cl_sunpower", "SunPower (the module's maker): a warranted Voc band at STC for the SPR-E-Flex-100 (U-03's route 1)"),
              ("cl_solbian", "Solbian: a warranted Voc band for the SX 156 (U-03's route 1)")]},
    {"id": "OW-5", "what": "the fallbacks, to send only if T-H1 reads under 2.159 W/K (L4-E12)",
     "docs": [("cl_gc", "Ground Control: the RockBLOCK 9704"), ("cl_nicerf", "NiceRF: the SA868"), ("cl_bulgin", "Bulgin: the PXP4043C")]},
    {"id": "OW-6", "what": "PANEL-ACC (U-03, L4-E13): buy one SunPower SPR-E-Flex-100, recorded by serial number, and have it measured to the "
                           "specification (M1 to M3 and A-2's reading); actions under the owner's authority (money), not questions",
     "docs": [("l4e13md", "L4-E13's page, PANEL-ACC")]},
]
OWNER_NOT_DRAFTED = ("not yet drafted (engineering work first, then the owner sends): Littelfuse, F1's total clearing I2t at 900 A and 58 V DC "
                     "(R-115, E11-16); Coilcraft, L10's inductance against current at temperature (R-120) and L1's Isat at 85 C (R-31); Milliohm, "
                     "R227's single-pulse rating (R-101)")
OWNER_MARK = {"l4e12md": r"\*\*Owner question: which of these three\?\*\*", "l4e10md": r"The recommendation needs the owner for exactly two things",
              "ti_review": r"Nothing in this file has been sent to anyone", "l4e13md": r"the purchase and the measurement are the owner's\s+actions"}

# The accepted records' downstream items mapped onto this register (deduplicated): L4-E11's E11-NN by its From column (every
# one but E11-19, which this record answers, out 12); L4-E10's and L4-E12's owner rows by these maps.
E11_ANSWERED_HERE = {"E11-19"}
E10_MAP = {"Session (layer 4)": ["R-103", "R-47"], "Layer 6, components": ["R-103"], "Layer 7, mechanical": ["R-111"],
           "Layer 8, generator owners": ["R-105"], "Layer 9, pre-layout": ["R-108"], "Prototype bench": ["R-104", "R-109"],
           "TEST-PLAN's owner": ["R-110"], "Firmware owner": ["R-106"], "Board B's owner": ["R-107"],
           "The kit's thermal owner (outside FEA-008)": ["R-111"], "Owner": ["OW-2", "OW-3"]}
E12_MAP = {"Owner": ["OW-1"], "Layer 4 coordinator": ["this record (IF-11, U-02, out 12e)"],
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
        if not all(c.get(k) for k in ("constraint", "settles", "alternatives", "owner", "overturns", "rows", "class")):
            bad.append((0, "choice %s lacks a field" % c["id"]))
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
    for part in ("SMCJ18A", "SMCJ22A", "SMCJ28A", "SMCJ40A"):
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
    p("   source leaving: VBAT is the system node with no battery FET, so the pack carries the loads without a break; IIN_HOST resets to 3.25 A")
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
    p("     not resolvable from the held documents in round 2: whether the converter keeps VSYS up with charge inhibited and no battery FET (Q-TI-3,")
    p("       %s); whether the gauge lets a pack at or below CUV take charge through its FETs with no precharge FET; whether every load" % B4["qti3"])
    p("       converter runs at the dead pack's VBAT (A-14). Board E's always-on comes up on CELL_F from VBAT")
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
    closed = all(g["verdict"] == "PASS" for g in GATE)
    p("   Layer 4's power architecture closes: %s" % ("YES" if closed else "NO, criteria %s are not PASS" % ", ".join(str(g["n"]) for g in GATE if g["verdict"] != "PASS")))
    p("   MATERIAL POWER-PATH DEFECTS (criterion 2): %d, %d open" % (len(DEFECTS), sum(1 for d in DEFECTS if d["state"] == "OPEN")))
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
        for k, lab in (("constraint", "the exact constraint"), ("settles", "the evidence that settles it"), ("alternatives", "the alternatives"),
                       ("owner", "the owner's items"), ("overturns", "what it could overturn")):
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
    for nm, mp in (("L4-E10", E10_MAP), ("L4-E12", E12_MAP)):
        for owner, refs in mp.items():
            for x in refs:
                if x.startswith("R-") and x not in ids:
                    refuse(4, "%s's %s maps to %s, not in the register" % (nm, owner, x))
                if x.startswith("OW-") and x not in {o["id"] for o in OWNER_ITEMS}:
                    refuse(4, "%s's %s maps to %s, not an owner item" % (nm, owner, x))
    p("     the accepted records' items, deduplicated: L4-E11's E11-01 to E11-23 each named in a row's From column (E11-19 answered here, out 12);")
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
    p("END. Desk arithmetic on read figures; nothing is measured.")
    return "\n".join(out) + "\n", F, D, R, st


def poe_v(F):
    return F["poe"]["volts"]


if __name__ == "__main__":
    text, *_ = main()
    sys.stdout.write(text)
