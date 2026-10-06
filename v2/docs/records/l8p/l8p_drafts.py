#!/usr/bin/env python3
"""l8p_drafts.py: Layer 8 record l8p, W4DP-F2's breaker drafted for boards P, E and A, proved on scratch copies (MESHSAT-1357,
4 October 2026).

It prints, deterministically and without touching the tree:
  1. the inputs, each pinned by sha256 (the generators and the engine, every other draft it composes with, record l9stk's copies
     of 0d72880b, L4-E7's backstop draft of fnd/l4e7r6 at 914a2f5a, L4-E11's drafts and sections 20c to 20e and 22b, 22c, 22g and
     22h of fnd/p0t10 at ecb598c5 (its round 17; round 6b copied round 13 at 4def5975, round 6 round 12 at ac72e730), the committed netlists, the lands, the makers' sheets read, the held OPA187 sheet,
     this record's own files);
  2. the values: each value the drafts draw found in record l9stk's own text by its section (refused when a phrase no longer
     matches), and this record's SESSION choices;
  3. C-1c's budget: the restart inhibit's window from the record, the NTC's figures from Murata's sheet, the OPA187's offset over
     temperature, bias and offset currents and supply rejection read from TI's held sheet (never typed), the bridge resistors,
     the NTC's own heating and the hysteresis computed for the drawn values, and the remainder left for the pad's gradient;
  3b. B-R2's detector (round 3, route R1): why no existing element tells board A a latched breaker passing a charge, the charge
     threshold and the reverse threshold with every tolerance, the delays, the protector's own limits, what board A must read
     (L4-E11's DD-7 interface, as its section 20c reads it at ecb598c5) and E-14 as it now reads, from task L4-E11's copies
     (fnd/l4e11r9 at e60a94a8, fnd/p0t10 at ecb598c5) and the makers' sheets;
  3c. DD-5 (round 4): the charge switch's body diode in discharge under CHGIN = 1, the three approaches, the ideal diode beside
     Q1 (apply_gen_sch_p_idealdiode.py) and its acceptance on case row C-PROT, from the BQ4050's, the CSD17570Q5B's and the
     LM74700-Q1's sheets;
  3d. rounds 5 and 6 (the check V1's minor and condition C3; the check V2's V2-B2 and V2-B3): L8P-F06, the breaker FETs' hot off
     leakage against BOTH limits of L4-E11's latch (the static 0.846 mA and the timing 520.7 uA of its round 12, sections 20e, 22b
     and 22c, copied; the timing limit reproduced here), and L8P-F07, the guard RT1's printed points (Murata's PRF sheet, read from
     its text) against the loop's levels, then on Murata's typical curve as read_prf_typical.py reads it (INFERRED), and the
     alternative parts named, TDK's window for the loop's scale k with the sure-off as its LOWER bound;
  4. each draft on a scratch copy: checked, applied once, refused twice, and refused on the tree's own generator (NOT RELEASED);
  5. the composition of each board in L4-E9's change-list order (the candidate's list, rows 24 to 33 for board A) with the drafts
     this record's tree holds, this record's draft in its place, first and last (L4-E11's DD-7 draft, which requires this record's
     board A draft, right after it and after the drafts it requires); the list's rows whose drafts are not in this tree are named
     (record l8r2's packrtn, slotlm and fb01), and the tree's drafts the list does not name (l8r2's d8v3 and vbus20ov) are composed
     in a second pass;
  6. the designators each draft adds, pairwise disjoint, and every literal part call drawn once in the composed generators;
  7. the regeneration on the runner (gen_netlist.py: the generator's own part table, no KiCad): the unpatched generators
     reproduce the committed KiCad netlists pin for pin; the netlist check (check_l8p_netlist.py) on the committed netlists
     (NOT DRAWN), on the three boards with this record's drafts alone and composed in L4-E9's order (DRAWN, board A with
     DD-7's readers on the loop), and on ten mutated netlists (FAIL);
  8. the declarations the patched board P generator writes into its intent for the new nets;
  9. the findings for other authors and their state.
Run from the repository root:  python3 v2/docs/records/l8p/l8p_drafts.py  (l8p_drafts.out is its output, regenerated with
_bin/regen_out.py). Nothing here is built or measured: every statement is about generator text, netlists and record text."""
import ast
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
RECS = os.path.join(ROOT, "v2", "docs", "records")
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import check_l8p_netlist as CHK  # noqa: E402
import gen_netlist as GN  # noqa: E402

GEN = {b: os.path.join(TOOLS, "gen_sch_%s.py" % b) for b in "pea"}
NET = {b: os.path.join(ROOT, p) for b, p in CHK.COMMITTED.items()}
PROJECT = {"p": "pcb-p-pack", "e": "pcb-e1-dock", "a": "pcb-a-power"}
MINE = {"p": os.path.join(HERE, "apply_gen_sch_p_breaker.py"), "e": os.path.join(HERE, "apply_gen_sch_e_enable.py"),
        "a": os.path.join(HERE, "apply_gen_sch_a_ptc.py")}
# board P's second draft (round 4, DD-5): applied after the breaker draft, which it requires
MINE2 = {"p": [os.path.join(HERE, "apply_gen_sch_p_idealdiode.py")]}
# Round 8: board A's thermal guard as record l9stk's round 5 re-selected it (C4), which replaces the PTC draft's block. It goes AFTER
# the drafts of FOLLOW (L4-E11's DD-7 refuses a target without RT1's call) and, where none is composed, right after this record's
# own; never in mine_seq(), whose drafts FOLLOW's come after
MINE_AFTER = {"a": [os.path.join(HERE, "apply_gen_sch_a_thguard.py")]}


def mine_seq(b):
    return [MINE[b]] + MINE2.get(b, [])


def mine_all(b):
    """Every draft of this record for board b, in its order (round 8: the guard after the PTC draft it replaces)."""
    return mine_seq(b) + MINE_AFTER.get(b, [])


def order(b, where):
    """The scripts composed on board b: 'fwd' this record's drafts in their SLOT, 'first', 'last', or 'without' them; 'tree' is
    'fwd' with the tree's drafts the list does not name (TREE_ONLY) before this record's; FOLLOW's drafts right after this
    record's and after the drafts they require (left out 'without', and left out 'last': L4-E11's dd7 must precede d8dec31's
    mainpb by the list, R-217 before R-193, and after it the draft refuses, because mainpb, a next-free taker, then holds R233
    and C241; so 'last' shows this record's own draft, which adds no R or C, after everything)."""
    seq = [draft(r, n, b) for r, n in ORDER[b]]
    extra = [draft(r, n, b) for r, n in TREE_ONLY.get(b, ())]
    out = {"fwd": seq[:SLOT[b]] + mine_seq(b) + seq[SLOT[b]:], "first": mine_seq(b) + seq, "last": seq + mine_seq(b), "without": seq,
           "tree": seq[:SLOT[b]] + extra + mine_seq(b) + seq[SLOT[b]:]}[where]
    if where not in ("without", "last"):
        for f, after in FOLLOW.get(b, ()):
            i = max([out.index(x) for x in mine_seq(b)] + [out.index(draft(r, n, b)) for r, n in after])
            out = out[:i + 1] + [f] + out[i + 1:]
    if where != "without":
        for f in MINE_AFTER.get(b, ()):
            i = max([out.index(x) for x in mine_seq(b)] + [out.index(x) for x, _a in FOLLOW.get(b, ()) if x in out])
            out = out[:i + 1] + [f] + out[i + 1:]
    return out


def list_order_full(b):
    """L4-E9's list order for board b with every row's draft: (the scripts, the rows whose drafts this tree does not hold). The
    rows of LIST_ABSENT go right before this record's drafts (the list's place for them: 3g on board A, 4e on board E), each
    only where the tree holds its draft. In this record's own tree the second value names all of them."""
    out = order(b, "fwd")
    held, missing = [], []
    for r, n, row in LIST_ABSENT.get(b, ()):
        p = os.path.join(RECS, r, "apply_gen_sch_%s_%s.py" % (b, n))
        (held if os.path.isfile(p) else missing).append((r, n, row, p))
    i = out.index(mine_seq(b)[0])
    return out[:i] + [p for _r, _n, _row, p in held] + out[i:], [(r, n, row) for r, n, row, _p in missing]


# L4-E9's change list (records/l4e9/L4-POWER-ARCHITECTURE.md section 3) for each board's round, in application order; d8dec31's
# drafts take the board's committed netlist as their second argument; Layer 6's l6r2 drafts are order-independent tables.
# Round 6 (the check V2's V2-m9): board A follows the list as the candidate carries it (fnd/v2cand at dfa1eef2, rows 24 to 33:
# 3g is gnd002, hotr1, packrtn, slotlm, fb01, this record's ptc, L4-E11's dd7; 3h is mainpb), with the drafts this record's tree
# holds. LIST_ABSENT names the list's rows whose drafts are NOT in this tree (the tree is main's at 64cd25ee; they are record
# l8r2's rounds 4 to 6 on fnd/l8r3 at 89924e40): they are left out here, and list_order_full() takes them in wherever a tree holds
# them (test_l8p then requires the whole list's order to compose and read DRAWN). TREE_ONLY names the board A drafts the tree
# holds and the list does not name: composed in a second pass, before this record's draft, where rounds 1 to 5 had them.
ORDER = {
    "p": [("l6r2", "intent"), ("l6r2", "lcsc")],
    "e": [("l4e9", "q1"), ("l4e7", "u5_grade"), ("l4e7", "hold"), ("l4e7", "input_limit"), ("l4e7", "backstop"), ("l4e9", "f1"),
          ("l4e9", "hotswap"), ("l4e11", "entry"), ("l4e7", "solar_guard"), ("l4e11", "aux"), ("d8dec31", "cin"), ("l6r2", "xal_land"),
          ("l6r2", "lcsc")],
    "a": [("l4e6", "r12"), ("l4e11", "guard"), ("l4e11", "charger"), ("l4e4", "r11"), ("l4e8", "bank"), ("l4e4", "r138"), ("l4e9", "u17"),
          ("l8gnd", "gnd002"), ("l8gnd", "hotr1"), ("d8dec31", "mainpb"), ("l6r2", "lcsc")],
}
# where this record's draft goes in the forward order: after the board's circuit drafts, before the last-taker and the tables
SLOT = {"p": 0, "e": 10, "a": 9}
LIST_ABSENT = {"a": [("l8r2", "packrtn", "R-201"), ("l8r2", "slotlm", "R-199"), ("l8r2", "fb01", "R-200")], "e": [("l8r2", "packrtn", "R-202")]}
TREE_ONLY = {"a": [("l8r2", "d8v3"), ("l8r2", "vbus20ov")]}
# Task L4-E11's round copied here, branch fnd/l4e11r11: every copy of its text and drafts is this commit's, and their file names
# are built from these two values, so taking the copies again is these two lines, SOURCES_SHA and inputs/SOURCES.txt.
# Round 6: round 12 at ac72e730. Round 6b: round 13 at 4def5975 (of the eleven copies only section 20c changed). Round 9 (P0 Slot C,
# the check V6's V6-m2): round 17 at ecb598c5 on fnd/p0t10 (of the thirteen copies only the charger draft changed, in L4-E11's
# rounds 15 and 16: its layout comment at Zw 37.59 K/W; the sections and the other three drafts are byte for byte round 13's)
L4E11_AT, L4E11_ROUND = "ecb598c5", 17
INPUT_FILES = {"page": "inputs/l9stk-section15-0d72880b.md", "out": "inputs/l9stk_protection-0d72880b.out.txt",
               "constants": "inputs/l9stk_protection-constants-0d72880b.txt", "l4e11": "inputs/l4e11-section19h-%s.md" % L4E11_AT,
               "l4e11pre": "inputs/l4e11-section15c-precharge-%s.md" % L4E11_AT, "l4e11c": "inputs/l4e11-section20c-%s.md" % L4E11_AT,
               "l4e11d": "inputs/l4e11-section20d-%s.md" % L4E11_AT, "l4e11e": "inputs/l4e11-section20e-%s.md" % L4E11_AT,
               "l4e11_22b": "inputs/l4e11-section22b-%s.md" % L4E11_AT, "l4e11_22c": "inputs/l4e11-section22c-%s.md" % L4E11_AT,
               "l4e11_22g": "inputs/l4e11-section22g-%s.md" % L4E11_AT, "l4e11_22h": "inputs/l4e11-section22h-%s.md" % L4E11_AT,
               "l9g": "inputs/l9stk-section15.9-bb6d2c8f.md"}
# the copies of L4-E11's page (INPUT_FILES key, its section heading's start) and of its drafts (the copy, records/l4e11's file):
# test_l8p compares each with records/l4e11/ wherever the tree holds L4-E11's round 10 or later (V2-B2: a copy a round behind).
# Round 7 (the recheck V2R's V2R-m8): section 19h and the excerpt of 15c, round 9's copies until now and outside this list, are taken
# again at L4E11_AT and listed (the excerpt by its first words: it is a paragraph of 15c, not a whole section)
L4E11_SECTIONS = (("l4e11c", "### 20c. "), ("l4e11d", "### 20d. "), ("l4e11e", "### 20e. "), ("l4e11_22b", "### 22b. "),
                  ("l4e11_22c", "### 22c. "), ("l4e11_22g", "### 22g. "), ("l4e11_22h", "### 22h. "), ("l4e11", "### 19h. "),
                  ("l4e11pre", "**The precharge in LDO mode, with R17's tolerance (the review's minor):**"))
L4E11_DRAFTS = (("inputs/l4e11r%d-apply_gen_sch_a_charger-%s.py" % (L4E11_ROUND, L4E11_AT), "apply_gen_sch_a_charger.py"),
                ("inputs/l4e11r%d-apply_gen_sch_a_dd7-%s.py" % (L4E11_ROUND, L4E11_AT), "apply_gen_sch_a_dd7.py"),
                ("inputs/l4e11r%d-apply_gen_sch_e_aux-%s.py" % (L4E11_ROUND, L4E11_AT), "apply_gen_sch_e_aux.py"),
                ("inputs/l4e11r%d-apply_gen_sch_e_entry-%s.py" % (L4E11_ROUND, L4E11_AT), "apply_gen_sch_e_entry.py"))
SOURCES_SHA = {"inputs/l9stk-section15-0d72880b.md": "a96099193dd92e8eecbb4ea444ee345bd87eb9af3146f005c507f14961f3ac80",
               "inputs/l9stk_protection-0d72880b.out.txt": "d97f94a0fa1f25598a26458276334b53505b065f350eb75a4d01cdfd91716eac",
               "inputs/l9stk_protection-constants-0d72880b.txt": "ed559399fd3b2f2d7c502b16e3296b5266ee5f4d1638b0a235342bde4e5f5c3e",
               "inputs/l4e7r6-apply_gen_sch_e_backstop-914a2f5a.py": "dc560d0de51ac782800eb1be0cc18d8c506b047fc7891ad5efe432b2d72fa544",
               "inputs/l4e11-section19h-%s.md" % L4E11_AT: "b4bd0832b4f89385a94ddf08db6f8cf482ded968089f1dc3861337d505d8f051",
               "inputs/l4e11-section15c-precharge-%s.md" % L4E11_AT: "ee11d230d11e1298e6ec49782e8890c669df1d7b1b573874b2e7b56b33d32146",
               "inputs/l4e11-section20c-%s.md" % L4E11_AT: "b3619bd411f5b64f2ae8efa3580041e2789513ccf5cda147b762df5cc4d2e9dc",
               "inputs/l4e11-section20d-%s.md" % L4E11_AT: "a5b5b306dadd2a147dfc18acc3fc9f31f0ba97ec00f25859054507b45bf96241",
               "inputs/l4e11-section20e-%s.md" % L4E11_AT: "9f3d4e017226d18f9579599137c132521094f976a48c01bd83e23b8dd61f9e3a",
               "inputs/l4e11-section22b-%s.md" % L4E11_AT: "583a346a0d2fa2119790f637ceb40bb90fb5cd9b05b806433fc5e960e66f9a45",
               "inputs/l4e11-section22c-%s.md" % L4E11_AT: "a90a69fa982e8db857efc37aa00fc54063740f660061c9c60840eeffe41278ec",
               "inputs/l4e11-section22g-%s.md" % L4E11_AT: "0595a5a24a5bbc34c1bb49fb5f464cf5e553f129fbf06dee098d0d145e3ee704",
               "inputs/l4e11-section22h-%s.md" % L4E11_AT: "b65f1dcdb0f61d3cbceb955c4d4e14e82827ec0c596c3b3b6b85866f9652c15f",
               "inputs/l4e11r%d-apply_gen_sch_a_charger-%s.py" % (L4E11_ROUND, L4E11_AT): "0e215988ba2a929bd2eb91b7eb80fa20040da28d10c08a9c36e1022e81a789c0",
               "inputs/l4e11r%d-apply_gen_sch_a_dd7-%s.py" % (L4E11_ROUND, L4E11_AT): "bc3fb88bae6a166fe1b15919410cace441806419f8e10c6711d03eddc9613034",
               "inputs/l4e11r%d-apply_gen_sch_e_aux-%s.py" % (L4E11_ROUND, L4E11_AT): "3d0a7b1d7d0bd8bfc417351d2efe6c469e31dd6e873119ea2a4d591dba68cf47",
               "inputs/l4e11r%d-apply_gen_sch_e_entry-%s.py" % (L4E11_ROUND, L4E11_AT): "a859aa4a63339f3aab927bc14afd7077cb66668e68858e41fcd53a926c7551f1",
               # round 8: record l9stk's round 5 (fnd/l9stk2 at bb6d2c8f), the selection C4 this record's guard draft draws
               "inputs/l9stk-section15.9-bb6d2c8f.md": "08a656ab0230986dbac4ec0c33c7f6c00f876eecb5792cf0343591796093cb9b",
               "inputs/l9stk_guard-bb6d2c8f.out.txt": "d84dcb3bab2f1f6009eafa5aec98533d59ee9513e89f574595d7080020ffa79c",
               "inputs/l9stk-readme-round5-bb6d2c8f.md": "03274200411401fe5cc48a3a75d4e2f51a9b8908c08e6dc84f34d174d37822c5"}
# L8P-F01 is closed by L4-E7's backstop draft on fnd/l4e7r6 at 914a2f5a (not on main): board E's composition uses that draft,
# copied byte for byte into inputs/, in place of main's
# Rounds 5 and 6: L4-E11's rounds 9 and 10 correct L8P-F02 and L8P-F03 and redraw DD-7 against route R1 (L8P-F04, L8P-F05); its
# round 13 (fnd/l4e11r11 at 4def5975, not on main) is the round copied here since round 6b (the check V2's V2-B2: round 5's copies
# were round 10's, a round behind the candidate; round 6 took round 12, and round 13 followed it). Its charger, aux and entry drafts are used the same way, copied byte for byte,
# so the output reads alike on this branch and on a line where records/l4e11/ holds the same bytes
REPLACED = {("l4e7", "backstop", "e"): os.path.join(HERE, "inputs", "l4e7r6-apply_gen_sch_e_backstop-914a2f5a.py"),
            ("l4e11", "charger", "a"): os.path.join(HERE, "inputs", "l4e11r%d-apply_gen_sch_a_charger-%s.py" % (L4E11_ROUND, L4E11_AT)),
            ("l4e11", "aux", "e"): os.path.join(HERE, "inputs", "l4e11r%d-apply_gen_sch_e_aux-%s.py" % (L4E11_ROUND, L4E11_AT)),
            ("l4e11", "entry", "e"): os.path.join(HERE, "inputs", "l4e11r%d-apply_gen_sch_e_entry-%s.py" % (L4E11_ROUND, L4E11_AT))}
# Other authors' drafts that require this record's draft (L4-E11's DD-7 refuses a target without RT1 and DOCK_EN_RET): each goes
# right after this record's drafts and after every draft it names as required (its docstring's ORDER), in every order composed
# here; a composition without this record's draft leaves it out. The copy is L4E11_AT's, byte for byte.
FOLLOW = {"a": [(os.path.join(HERE, "inputs", "l4e11r%d-apply_gen_sch_a_dd7-%s.py" % (L4E11_ROUND, L4E11_AT)), (("l4e11", "charger"),))]}
OPA187 = os.path.join(ROOT, "v2", "vendor", "ti", "held", "ti-opa187-sbos807e.pdf")
NTC_SHEET = os.path.join(ROOT, "v2", "vendor", "battery", "murata-nxrt15xh103fa1b.pdf")
D4148_SHEET = os.path.join(ROOT, "v2", "vendor", "power", "st-semtech-1n4148w-c81598.pdf")
LM5069_SHEET = os.path.join(ROOT, "v2", "vendor", "ti", "ti-lm5069.pdf")
CSD_SHEET = os.path.join(ROOT, "v2", "vendor", "battery", "ti-csd18510q5b.pdf")
N7002_SHEET = os.path.join(ROOT, "v2", "vendor", "power", "jscj-2n7002-c8545.pdf")
BZT_SHEET = os.path.join(ROOT, "v2", "vendor", "diodes", "diodes-bzt52c-ds18004.pdf")
TRM_SHEET = os.path.join(ROOT, "v2", "vendor", "battery", "ti-sluuaq3a-bq4050-trm.pdf")
BQ4050_SHEET = os.path.join(ROOT, "v2", "vendor", "battery", "ti-bq4050.pdf")
CSD17570_SHEET = os.path.join(ROOT, "v2", "vendor", "battery", "ti-csd17570q5b.pdf")
LM74700_SHEET = os.path.join(ROOT, "v2", "vendor", "ti", "ti-lm74700-q1.pdf")
# C-1c as drawn (apply_gen_sch_p_breaker.py): the bridge, the reference, the hysteresis, and the bounds the budget applies
R_BRIDGE, R_REF_T, R_REF_B, R_HYST = 150e3, 147e3, 1.62e3, 15e6
R_TOL, R_TCR, HYST_TOL = 0.001, 25e-6, 0.01     # the bridge and reference parts: 0.1 %, at most 25 ppm/K; the hysteresis part 1 %
T_RES = (25.0, 101.0)                           # the resistors anywhere between 25 C and the held 101.0 C case (l9stk 15.4)
V_CLAMP = 29.2                                  # BRK_VIN's clamp (l9stk 15.4, the clamps row), the supply span for PSRR
CHECKER_GRADIENT = 0.9                          # the pad-to-NTC gradient the checker asked the split to leave room for, K
# B-R2's detector as drawn (apply_gen_sch_p_breaker.py, round 3, route R1)
R118, R119, R129, R120, C109 = 1.15e6, 200.0, 47e3, 200.0, 470e-9
R121, R122, R123, R124, C110 = 332e3, 33.2e3, 328e3, 33.2e3, 1e-9
TOL_REF, TCR_REF = 0.001, 25e-6                 # R118 and R119, as C-1c's bridge
TOL_DIV, TCR_DIV = 0.0005, 10e-6                # R121 to R124
TOL_FEED, TCR_FEED = 0.01, 100e-6               # R129, a 1 % part; its 100 ppm/K ASSUMED
R10_TOL, R10_TCR = 0.01, 75e-6                  # board P's R10, the gauge's sense: no tolerance or TCR is printed in the generator; ASSUMED, owed to Layer 6
R106_TOL = 0.01                                 # R106 10 kOhm, ASSUMED 1 %
STRETCH_MIN = 1.0                               # the least time board A holds its inhibit after the return rises (the interface), s
# the interface's levels as board A reads them (L4-E11 section 20c at L4E11_AT, U48 TPS37A010122 on TI SNVSBJ1E, finding
# L4E11-R10-F1): DOCK_EN_OUT read powered over 1.981 V at most; DOCK_EN_RET read held under 0.7755 V at least and closed over
# 0.84 V at most, V. Not retyped: section 3b refuses unless the copy reads each
OUT_POWERED, RET_LOW, RET_HIGH = 1.981, 0.7755, 0.84
# readings of TI's plotted typical curves (no figure has a text layer), INFERRED: E-14b measures them on the specimen
CSD_RDS_150 = 1.8                               # CSD18510Q5B Figure 8: normalized RDS(on) at VGS 10 V and 150 C
CSD_VSD = {25: (0.575, 0.632), 125: (0.368, 0.432)}   # Figure 9: typical VSD at 0.1 A and at 1 A, by case temperature
CSD_ZTH_10MS = 0.54                             # Figure 1: the single pulse's normalized ZthJC at 10 ms
N7002_HOT = 2.0                                 # the 2N7002's RDS(on) taken as twice its 25 C maximum when hot (a bound, no figure read)
# DD-5's ideal diode as drawn (apply_gen_sch_p_idealdiode.py, round 4)
C111, C111_TOL, C111_BIAS = 220e-9, 0.10, 0.20  # U105's VCAP capacitor: X7R 50 V 0805, 10 %; its loss of capacitance at 13.9 V taken as 20 % (ASSUMED, Layer 6's part)
R130, R131 = 10e6, 1e6                          # Q109's gate to source; EN to ground
IGSS_17570, IDSS_17570 = 100e-9, 1e-6           # CSD17570Q5B SLPS471D 5.1: IGSS at 20 V and IDSS at 24 V, the printed maxima at 25 C
CSD17570_RDS_150 = 1.68                         # CSD17570Q5B Figure 8: normalized RDS(on) at VGS 10 V and 150 C (typical, read by eye, INFERRED)
# Round 5 (the check V1's minor and condition C3): L8P-F06, the breaker FETs' hot off leakage into CELL+, and L8P-F07, the guard RT1's
# printed points. Murata's PRF sheet is committed; TDK's is held back by its notice (fetch_held_back.py)
PRF_SHEET = os.path.join(ROOT, "v2", "vendor", "battery", "murata-prf-series.pdf")
TDK_SHEET = os.path.join(ROOT, "v2", "vendor", "battery", "held", "tdk-ptc-limit-sensors-smd-superior-2019-08.pdf")
IDSS_DOUBLING = 10.0                            # ASSUMPTION: the off leakage doubles every 10 K from the sheet's 25 C row (the convention L4-E11 20d applies to Q51); no hot row is printed
R107_TOL = 0.01                                 # R107 22 kOhm, ASSUMED 1 % as R106 (the draft prints no tolerance)
# Murata DM-SA16-E056 Rev.1, 3.2 (p.5): the BB characteristic's typical R/R25 against T, read by read_prf_typical.py at 400 dpi
# (INFERRED: a TYPICAL curve, normalised to R25, drawn per characteristic code and not per resistance group); two points the
# reader takes where the stroke crosses a grid line (111.82 and 112.62 C) are left out
PRF_BB_TYP = ((77.62, 0.9908), (79.63, 1.0092), (83.40, 1.0763), (86.16, 1.1249), (88.17, 1.1865), (89.18, 1.2197), (90.93, 1.2771),
              (92.94, 1.3721), (95.71, 1.5435), (97.72, 1.7172), (99.73, 1.9676), (101.82, 2.3005), (103.91, 2.7650), (106.38, 3.5118),
              (108.01, 4.2208), (109.69, 4.9806), (111.15, 5.8772), (113.25, 7.7442), (114.71, 9.3422), (115.76, 10.9834), (116.60, 12.0412),
              (117.22, 13.2010), (117.85, 14.4725), (118.48, 15.8664), (119.74, 18.7225), (121.41, 25.5005), (123.46, 36.8378),
              (125.72, 53.2155), (127.61, 68.8429), (129.57, 100.5533), (131.79, 131.0425), (133.68, 172.6714), (136.19, 249.4393),
              (138.07, 328.6799), (140.54, 466.1550))
PRF_LOWEST = 0.749                              # 3.2: the figure's lowest stroke, any curve, -20 to 125 C (read, typical)
PRF_TOP_M20 = 1.515                             # 3.2: the curve bundle's top edge at -19.5 C (read, typical): every B curve under it there
# TDK superior series, EIA 0805, B59721A0xxxA062 (the held sheet, August 2019, p.4 table; typed here, read against the held sheet
# by test_l8p when it is present): RR at TR = 25 C, its tolerance, the printed limits around Tsense,1, Vmax, the measurement power
TDK_B59721 = {"rr": 680.0, "drr": 0.50, "tsense": (90, 100, 110, 120, 130), "r_m5": 5.5e3, "r_p5": 13.3e3, "r_p15": 40e3, "vmax": 32.0,
              "p_meas": 6e-3, "page": 4,
              # round 6: p.29, the B59721A0130A062's own table, headed "Rmin and Rmax values are typical values for reference only":
              # its least Rmin, 212 ohm at 100 C (340 ohm at 25 C, the printed RR less 50 %); TYPICAL, reference only
              "rmin_ref": 212.0, "t_rmin_ref": 100, "rmin25_ref": 340.0, "page_ref": 29}
SESSION = [
    ("designators", "the free 100 block on board P (U101, U102, Q101 to Q106, D101, D102, RT101, R101 to R117, C101 to C106, TP101 to TP106); RT1 on board A, which carries no RT designator"),
    ("net names", "BRK_VIN (Q2's source, the breaker's input), BRK_SNS, BRK_GATE, BRK_TMR, BRK_PWR, BRK_UVLO, BRK_G2, BRK_H, BRK_HD, BRK_PGD, BRK_CMID, INH_NTC, INH_REF, INH_OUT, INH_G; DOCK_EN_OUT and DOCK_EN_RET on all three boards"),
    ("J_SMB pins", "a JST-XH 1x7 at both ends: 1 to 4 unchanged, 5 DOCK_EN_RET, 6 the return (the ground between), 7 DOCK_EN_OUT at the row's end"),
    ("dock positions", "J_DOCK and J_BLK pins 3 (DOCK_EN_RET) and 5 (DOCK_EN_OUT), pin 4 ground between them; pin 5's neighbours 4, 6 and 11 are all ground"),
    ("input bypass", "C104 and C105, 2.2 uF 50 V X7R in series (1.1 uF) at the sense pair: TI SNVS452G section 10 ('a 1-uF ceramic capacitor to ground close to the drain of the hot swap MOSFET') and 11.1.1; in series as C11 and C12 are (board P's O-12)"),
    ("comparator", "U102, TI OPA187IDBVR, a zero-drift amplifier on BRK_VIN used as the comparator: 4.5 to 36 V, its input range from 0.1 V under its negative rail, its offset over temperature read from the held sheet (section 3); C106 its bypass"),
    ("reference", "R111 147 kOhm over R112 1.62 kOhm (1653.06 ohm against the trip's 1653), R113 15 MOhm of hysteresis, all from BRK_VIN as the NTC's bridge is (ratiometric)"),
    ("PGD gating", "U101's PGD on BRK_PGD at half BRK_VIN (R116, R117 1 MOhm); Q106 holds Q105's gate low while PGD is high; Q105 pulls UVLO; R114 and R115 halve U102's output for Q105's gate"),
    ("test points", "TP101 BRK_VIN, TP102 BRK_UVLO, TP103 DOCK_EN_OUT, TP104 DOCK_EN_RET (E-12); TP105 INH_NTC, TP106 INH_OUT (E-12b)"),
    ("lands", "the VSSOP-10, SMC, SOD-123, SOT-23-5 and 2512 lands the kit already uses; the 7-circuit XH header of the same row; RT1 on board P's 0402; RT101's 10 mm leads on the project's LeadLands_1x02"),
    ("DD-5 ideal diode", "round 4: Q109 CSD17570Q5B beside Q1 (source SCP_OUT, drain SW) under U105 LM74700QDBVRQ1 (ANODE SCP_OUT, CATHODE SW, GND the cells' negative); C111 220 nF 50 V on VCAP; R130 10 MOhm gate to source; EN from BRK_VIN through D104 1N4148W with R131 1 MOhm to ground; C112 and C113 100 nF in series at the anode, C114 and C115 470 nF in series at the cathode; TP109 on the gate (E-12d); a second FET beside Q1, not a second driver on Q1's gate"),
    ("B-R2 detector", "round 3, route R1: U103 and U104 (OPA187, U102's part), U103 on R10's cell side through R120 200 ohm and C109 470 nF against R118 1.15 MOhm over R119 200 ohm from REV_VZ (BRK_VIN through R129 47 kOhm under D103, the BZT52C12 board A's D25 uses); U104 on PACK_P over R121 332 kOhm and R122 33.2 kOhm against BRK_SNS over R123 328 kOhm and R124 33.2 kOhm (0.05 %, 10 ppm/K), C110 1 nF; Q107 and Q108 2N7002 in series on DOCK_EN_RET, their gates at half of each output (R125 to R128); C107, C108; TP107, TP108 (E-12c)"),
]


# SCRATCH STAND-INS for run-time defects of OTHER records' drafts that stop the composed generators (section 9 lists them as
# findings for their owners). Each is applied to a scratch copy only when its old text is there; none is a draft, none is applied
# anywhere else, and each says only that the generator then runs on. None since round 5: L8P-F02 and L8P-F03 are corrected in
# L4-E11's drafts (REPLACED; the round L4E11_ROUND names), which the compositions use.
STANDINS = {}

# W34 (Q-41 item 1, adopted in set 32): the makers' PDFs this script reads as text, each with its pdftotext options ([] is pdftotext's
# plain reading order). Each text is a verbatim input taken once on the runner by v2/docs/records/_lib/retake_pdf_text.py beside its
# PDF (a held-back sheet's text is held back with it, under held/); _lib/pdftext.py returns it byte for byte and refuses when it is
# absent, so this script never runs pdftotext; section 1 prints each text's sha256 among the inputs.
# Re-take after a sheet changes: python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l8p
PDFTEXT = {
    "v2/vendor/battery/murata-nxrt15xh103fa1b.pdf": [["-layout"]],
    "v2/vendor/battery/murata-prf-series.pdf": [["-layout"]],
    "v2/vendor/battery/ti-bq4050.pdf": [["-layout"]],
    "v2/vendor/battery/ti-csd17570q5b.pdf": [["-layout"]],
    "v2/vendor/battery/ti-csd18510q5b.pdf": [["-layout"]],
    "v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf": [["-layout"]],
    "v2/vendor/diodes/diodes-bzt52c-ds18004.pdf": [["-layout"]],
    "v2/vendor/power/jscj-2n7002-c8545.pdf": [["-layout"]],
    "v2/vendor/power/st-semtech-1n4148w-c81598.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-opa187-sbos807e.pdf": [["-layout"]],
    "v2/vendor/ti/ti-lm5069.pdf": [["-layout"]],
    "v2/vendor/ti/ti-lm74700-q1.pdf": [["-layout"]],
}
import importlib.util  # noqa: E402  (the helper's loader; W34)
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PT)
def pdftext(path):
    return PT.pdf_text(ROOT, rel(path), ["-layout"], PDFTEXT, "v2/docs/records/l8p")


def need(text, pat, what, flags=re.M):
    m = re.search(pat, text, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its input" % what)
    return m


def budget(page):
    """C-1c's window from the record, the parts' figures from their makers' sheets, and the split of the +-1.95 K."""
    N = r"([0-9.]+)"
    W = {}
    W["allow"] = float(need(page, r"Allow\s+from\s+%s\s+C" % N, "the allow edge").group(1))
    W["block"] = float(need(page, r"block\s+from\s+%s\s+C\." % N, "the block edge").group(1))
    m = need(page, r"trip\s+is\s+%s\s+C\s+plus\s+or\s+minus\s+%s\s+K,\s+with\s+the\s+NTC\s+at\s+%s\s+ohm" % (N, N, N), "the trip")
    W["trip"], W["half"], W["r_trip"] = float(m.group(1)), float(m.group(2)), float(m.group(3))
    W["ntc_k"] = float(need(page, r"The\s+NTC\s+takes\s+plus\s+or\s+minus\s+%s\s+K" % N, "the NTC's share").group(1))
    W["rest"] = float(need(page, r"leaves\s+plus\s+or\s+minus\s+%s\s+K\s+for\s+the\s+comparator" % N, "the budget left").group(1))
    W["air"] = float(need(page, r"L4-E12's\s+%s\s+C" % N, "the inside air").group(1))
    m = need(page, r"the\s+pack\s+%s\s+to\s+%s\s+V" % (N, N), "the pack's range")
    W["vmin"], W["vmax"] = float(m.group(1)), float(m.group(2))
    W["case_held"] = float(need(page, r"case\s+%s\s+C\s+with\s+both\s+losses\s+through\s+one\s+pad" % N, "the held case").group(1))
    need(page, r"PGD\s+is\s+low:\s+the\s+breaker\s+off,\s+starting\s+or\s+in\s+a\s+fault\s+\(VDS\s+over\s+1\.62\s+to\s+3\.4\s+V\)", "the PGD gate")
    nt = pdftext(NTC_SHEET)
    W["r25"] = float(need(nt, r"Resistance \(25\u2103\)\s+(\d+)k\u03a9", "the NTC's R25").group(1)) * 1e3
    W["b85"] = float(need(nt, r"B-Constant\(25/85\u2103\)\s+(\d+)K", "the NTC's B25/85").group(1))
    W["imax"] = float(need(nt, r"Maximum Operating Current\s+([0-9.]+)mA", "the NTC's current").group(1)) * 1e-3
    W["delta"] = float(need(nt, r"Typical Dissipation Constant\s+([0-9.]+)mW/\u2103", "the NTC's dissipation constant").group(1)) * 1e-3
    need(nt, r"Lead Shape\s+Lead Wire type", "the NTC's leads"); need(nt, r"Size Code \(in mm\)\s+010", "the NTC's 10 mm leads")
    need(nt, r"Reference Value", "B25/85 printed as a reference value")
    op = pdftext(OPA187)
    U = "\u03bc"
    need(op, r"SBOS807E", "the OPA187 sheet's revision")
    W["vos"] = float(need(op, r"\u00b11\s+\u00b1(10)\s+%sV" % U, "the OPA187's VOS").group(1)) * 1e-6
    W["drift"] = float(need(op, r"TA = \u201340\u00b0C to \+125\u00b0C\s+\u00b10\.001\s+\u00b1([0-9.]+)\s+%sV/\u00b0C" % U, "its drift").group(1)) * 1e-6
    W["ib"] = float(need(op, r"TA = \u201340\u00b0C to \+125\u00b0C\s+\u00b1([0-9.]+)\s+nA\n\s+\u00b1100\s+\u00b1500\s+pA", "its IB").group(1)) * 1e-9
    W["ios"] = float(need(op, r"IOS\s+Input offset current\n\s+TA = \u201340\u00b0C to \+125\u00b0C\s+\u00b1([0-9.]+)\s+nA", "its IOS").group(1)) * 1e-9
    W["psrr"] = float(need(op, r"\u00b10\.01\s+\u00b1([0-9.]+)\s+%sV/V" % U, "its PSRR").group(1)) * 1e-6
    m = need(op, r"^\(V\+\) \u2013 \(V\u2013\)\s+Supply voltage\s+([0-9.]+) \(\u00b12\.25\)\s+(\d+) \(\u00b118\)\s+V", "its supply range")
    W["vs"] = (float(m.group(1)), float(m.group(2)))
    W["vs_abs"] = float(need(op, r"Supply, VS = \(V\+\) \u2013 \(V\u2013\)\s+(\d+)", "its absolute supply").group(1))
    need(op, r"\(V\u2013\) \u2013 0\.1\s+\(V\+\) \u2013 2\s+V", "its input range from under its negative rail")
    need(op, r"protected from excessive differential voltage with back-to-back diodes", "its input diodes")
    need(op, r"Low-ESR, 0\.1-\u00b5F ceramic bypass capacitors must be connected between each supply pin and ground", "its bypass clause")
    W["tj_max_spec"] = 125.0 if re.search(r"All versions are specified for\s+operation from \u201340\u00b0C to \+125\u00b0C", op) else refuse("its specified range")
    # the arithmetic
    tk = W["trip"] + 273.15
    sens = W["b85"] / tk ** 2                                          # d(ln R)/dT at the trip, per K (B25/85, the record's)
    rt = W["r_trip"]
    vn = W["vmin"] * rt / (R_BRIDGE + rt)                              # the NTC's node at the trip and the least VIN
    slope = vn * sens * R_BRIDGE / (R_BRIDGE + rt)                     # V per K there
    rsrc_n = R_BRIDGE * rt / (R_BRIDGE + rt)
    rsrc_r = 1.0 / (1.0 / R_REF_T + 1.0 / R_REF_B + 1.0 / R_HYST)
    v_op = (W["vos"] + W["drift"] * (W["tj_max_spec"] - 25.0) + W["ios"] * max(rsrc_n, rsrc_r) + W["ib"] * abs(rsrc_n - rsrc_r)
            + W["psrr"] * (V_CLAMP - W["vmin"]))
    W.update(sens=sens, vn=vn, slope=slope, v_op=v_op, k_op=v_op / slope)

    def x_eq(rt_, rb_, rf_, vo):
        g = 1.0 / rt_ + 1.0 / rb_ + 1.0 / rf_
        r = (1.0 / rt_ + vo / rf_) / g
        return R_BRIDGE * r / (1.0 - r)
    x_low = x_eq(R_REF_T, R_REF_B, R_HYST, 0.0)
    W["x_low"] = x_low
    W["k_nominal"] = math.log(rt / x_low) / sens                      # positive: the drawn trip sits hotter than the record's
    W["hyst_nom"] = math.log(x_eq(R_REF_T, R_REF_B, R_HYST, 1.0) / x_low) / sens
    W["hyst_max"] = max(math.log(x_eq(R_REF_T * a, R_REF_B * b, R_HYST * (1 - HYST_TOL), 1.0) / x_eq(R_REF_T * a, R_REF_B * b, R_HYST * (1 - HYST_TOL), 0.0)) / sens
                        for a in (1 - R_TOL, 1 + R_TOL) for b in (1 - R_TOL, 1 + R_TOL))
    e = R_TOL + R_TCR * (T_RES[1] - T_RES[0])
    worst = 0.0
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            for s3 in (-1, 1):
                rb_, rr_t, rr_b = R_BRIDGE * (1 + s1 * e), R_REF_T * (1 + s2 * e), R_REF_B * (1 + s3 * e)
                g = 1.0 / rr_t + 1.0 / rr_b + 1.0 / R_HYST
                r = (1.0 / rr_t) / g
                worst = max(worst, abs(math.log((rb_ * r / (1.0 - r)) / x_low)) / sens)
    W["k_res"], W["res_e"] = worst, e
    i_br = W["vmax"] / (R_BRIDGE + rt)
    W["i_bridge"] = i_br
    W["k_self"] = i_br * i_br * rt / W["delta"]                        # the NTC reads hotter by its own heating
    allow_used = W["k_op"] + W["k_res"] + W["k_self"] + W["hyst_max"] + max(0.0, -W["k_nominal"])
    block_used = W["k_op"] + W["k_res"] + max(0.0, W["k_nominal"])
    W.update(allow_used=allow_used, block_used=block_used, grad_allow=W["rest"] - allow_used, grad_block=W["rest"] - block_used)
    W["closes"] = W["grad_allow"] >= CHECKER_GRADIENT and W["grad_block"] >= CHECKER_GRADIENT and W["hyst_max"] <= 0.5 and W["k_op"] <= 0.47
    # the record prints each figure to two decimals, so the window's sums agree within two of their last digits
    W["window_ok"] = abs(W["trip"] - W["half"] - W["allow"]) <= 0.02 and abs(W["trip"] + W["half"] - W["block"]) <= 0.02 \
        and abs(W["half"] - W["ntc_k"] - W["rest"]) <= 0.02
    W["lockout"] = W["allow"] - W["air"]
    W["iq_max"] = float(need(op, r"IO = 0 mA, TA = \u201340\u00b0C to \+125\u00b0C\s+([0-9.]+)\s+%sA" % U, "its quiescent current over temperature").group(1)) * 1e-6
    return W


def r_div_k():
    return (R121 + R122) / 1e3


def rev_budget(page, l4, pre, W):
    """B-R2's detector (route R1, round 3): the figures read from record l9stk's and task L4-E11's copies and from the makers'
    sheets; the three readings of plotted typical curves are marked; the thresholds, their tolerances, the delays and the limits
    computed for the drawn values."""
    N = r"([0-9.]+)"
    R = {}
    # record l9stk (0d72880b), section 15
    R["i_lim"] = float(need(page, r"\*\*%s\s+A\s+largest\*\*" % N, "l9stk: the breaker's largest limit").group(1))
    need(page, r"\*\*0\.110\s+to\s+0\.907\s+s\s+after\s+the\s+enable\s+mates\*\*", "l9stk: the hold")
    R["hold"] = 0.907
    R["start"] = float(need(page, r"\*\*inrush\s+at\s+most\s+0\.659\s+A\*\*\s+for\s+at\s+most\s+%s\s+ms" % N, "l9stk: the start").group(1)) * 1e-3
    R["t_timer"] = float(need(page, r"The\s+timer\s+falls\s+under\s+its\s+0\.3\s+V\s+re-enable\s+threshold\s+in\s+%s\s+ms\s+at\s+most" % N,
                              "l9stk: the timer's re-enable").group(1)) * 1e-3
    R["rja"] = float(need(page, r"installed\s+RthJA\s+of\s+\*\*%s\s+C/W\s+per\s+FET\*\*" % N, "l9stk: IF-2's RthJA").group(1))
    # task L4-E11, sections 19h and 15c (round 9's figures; copied at L4E11_AT since round 7, where 19h carries two later notes)
    R["i_por"] = float(need(l4, r"ChargeCurrent\s+at\s+POR\s+\(TI's\s+E2E\s+answer,\s+D4\),\s+%s\s+A" % N, "L4-E11: the power-on charge").group(1))
    m = need(l4, r"R-b's\s+largest\s+actual\s+current,\s+%s\s+A\s+\|\s+[0-9.]+\s+W\s+\|\s+%s\s+C" % (N, N), "L4-E11: R-b's largest")
    R["i_rb"], R["tj_rb"] = float(m.group(1)), float(m.group(2))
    R["alive"] = float(need(l4, r"the\s+inhibit\s+sets\s+only\s+when\s+CELL\+\s+falls\s+under\s+%s\s+V" % N, "L4-E11: the inhibit's CELL+ threshold").group(1))
    m = need(l4, r"under\s+%s\s+A\s+\(the\s+latched\s+FET's\s+body\s+diode\s+at\s+150\s+C\s+held\s+from\s+%s\s+C\s+at\s+VSD\s+%s\s+V\s+and\s+%s\s+C/W\)" % (N, N, N, N),
             "L4-E11: the latched FET's safe level")
    R["i_safe"], R["air"], R["vsd_b"], R["rja_l4"] = (float(m.group(k)) for k in (1, 2, 3, 4))
    R["p_fe"] = float(need(l4, r"the\s+front\s+end's\s+%s\s+W" % N, "L4-E11: the front end's power").group(1))
    m = need(l4, r"\*\*%s\s+V\*\*\s+at\s+the\s+breaker's\s+least-limit\s+fault\s+of\s+%s\s+ohm" % (N, N), "L4-E11: the reach's resistive case")
    R["v_fault"], R["r_fault"] = float(m.group(1)), float(m.group(2))
    R["reach"] = float(need(l4, r"faults\s+under\s+\*\*%s\s+mOhm\*\*" % N, "L4-E11: the inhibit's reach").group(1))
    need(l4, r"The\s+breaker's\s+PGD\s+reads\s+high\s+in\s+that\s+state\s+too", "L4-E11: PGD high in reverse")
    need(l4, r"\*\*B-R2\s+stays\s+OPEN\s+for\s+that\s+case\*\*", "L4-E11: B-R2 open")
    m = need(l4, r"DOCK_EN_OUT\s+is\s+at\s+least\s+%s\s+V\s+\(the\s+pack's\s+%s\s+V,\s+RT1\s+at\s+its\s+cold\s+least\s+%s\s+kOhm" % (N, N, N),
             "L4-E11: the inhibit's loop sense")
    R["out_l4"], R["v_pack_min"], R["rt1_min"] = float(m.group(1)), float(m.group(2)), float(m.group(3)) * 1e3
    need(l4, r"\|\s+R109,\s+R144\s+\|\s+1M\s+each,\s+DOCK_EN_OUT\s+to\s+SYS_INH_G\s+to\s+ground", "L4-E11: Q47's gate at half of DOCK_EN_OUT")
    R["i_ldo"] = float(need(pre, r"\*\*%s\s+A\*\*\s+at\s+most,\s+all\s+of\s+it\s+in\s+one\s+FET" % N, "L4-E11 15c: the LDO-mode precharge").group(1))
    R["srn_floor"] = float(need(pre, r"no\s+charge\s+under\s+\*\*%s\s+V\*\*\s+on\s+SRN" % N, "L4-E11 15c: R-b''s floor").group(1))
    # board P's sense R10, read from the tree's generator
    g = open(GEN["p"], encoding="utf-8").read()
    m = need(g, r'r\("R10",\s+"(\d+)m 2512 2W \(sense\)",\s+"GND",\s+"PACK_N"', "board P's R10")
    R["r10"] = float(m.group(1)) * 1e-3
    # TI LM5069 (SNVS452G)
    lm = pdftext(LM5069_SHEET)
    m = need(lm, r"Normal operation, GATE-OUT = 5 V\s+%s\s+%s\s+%s\s+\u00b5A" % (N, N, N), "LM5069: IGATE")
    R["igate"] = (float(m.group(1)), float(m.group(3)))
    m = need(lm, r"UVLO < 2\.5 V\s+%s\s+%s\s+%s\s+mA" % (N, N, N), "LM5069: the gate's 2 mA sink")
    R["isink"] = (float(m.group(1)), float(m.group(3)))
    m = need(lm, r"POREN\s+VIN increasing\s+%s\s+%s\s+V" % (N, N), "LM5069: POREN")
    R["poren"] = (float(m.group(1)), float(m.group(2)))
    R["porit"] = float(need(lm, r"PORIT\s+VIN increasing\s+%s\s+%s\s+V" % (N, N), "LM5069: PORIT").group(1))
    need(lm, r"When the external MOSFET VDS decreases below 1\.25 V,", "LM5069: PGD on VDS alone")
    need(lm, r"The gate-to-source voltage is limited by an internal 12-V Zener diode", "LM5069: the internal gate clamp")
    need(lm, r"momentarily pulling the UVLO pin below\s+2\.5 V", "LM5069: the -1's reset by UVLO")
    need(lm, r"The voltage at the TIMER pin must be\s+<0\.3 V for the restart procedure to be effective", "LM5069: the timer's condition")
    R["r_so"] = float(need(lm, r"OUT bias current \(disabled\) due to leakage current through an internal (\d+)-M\u03a9 resistance from SENSE to VOUT",
                           "LM5069: the internal SENSE to OUT resistance while disabled").group(1)) * 1e6
    m = need(l4, r"CELL\+\s+over\s+R107\s+/\s+R108\s+\((\d+)k\s+each\)", "L4-E11: DD7_ALIVE's divider")
    R["r_alive"] = 2 * float(m.group(1)) * 1e3
    R["dead"] = float(need(l4, r"under\s+%s\s+V\s+it\s+cannot\s+conduct" % N, "L4-E11: CELL+ read dead").group(1))
    # TI CSD18510Q5B (SLPS632)
    cs = pdftext(CSD_SHEET)
    R["rds_max"] = float(need(cs, r"VGS = 10 V, ID = 32 A\s+0\.79\s+%s" % N, "CSD18510Q5B: RDS(on)").group(1)) * 1e-3
    R["vsd_max"] = float(need(cs, r"ISD = 32 A, VGS = 0 V\s+0\.8\s+%s" % N, "CSD18510Q5B: VSD").group(1))
    R["rjc"] = float(need(cs, r"Junction-to-case thermal resistance \(1\)\s+%s" % N, "CSD18510Q5B: RthJC").group(1))
    for f in ("Figure 1. Transient Thermal Impedance", "Figure 8. Normalized On-State Resistance vs Temperature", "Figure 9. Typical Diode Forward Voltage"):
        need(cs, re.escape(f), "CSD18510Q5B: %s" % f)
    # JSCJ 2N7002 (C8545)
    nj = pdftext(N7002_SHEET)
    R["n_rds"] = float(need(nj, r"VGS=5 V, ID=50mA\s+1\.1\s+%s" % N, "2N7002: RDS(on) at 5 V").group(1))
    m = need(nj, r"Vth\(GS\)\s+VDS=VGS, ID=250 \u00b5A\s+%s\s+%s\s+%s" % (N, N, N), "2N7002: the threshold")
    R["n_vth"] = (float(m.group(1)), float(m.group(3)))
    R["n_vgs"] = float(need(nj, r"Gate-Source Voltage\s+VGS\s+\u00b1(\d+)", "2N7002: VGS").group(1))
    # Diodes BZT52C (DS18004)
    bz = pdftext(BZT_SHEET)
    m = need(bz, r"BZT52C12\s+WH\s+12\s+%s\s+%s\s+5\s+25\s+150\s+1\.0\s+%s\s+%s\s+%s\s+%s" % (N, N, N, N, N, N), "BZT52C12's row")
    R["vz"], R["ir"], R["vr"], R["tcz_min"], R["tcz"] = (float(m.group(1)), float(m.group(2))), float(m.group(3)) * 1e-6, float(m.group(4)), \
        float(m.group(5)) * 1e-3, float(m.group(6)) * 1e-3
    # the arithmetic: the charge threshold (U103)
    t_hi = W["case_held"]
    e_ref = 2 * (TOL_REF + TCR_REF * (t_hi - 25.0))
    e_feed = TOL_FEED + TCR_FEED * (t_hi - 25.0)
    e_r10 = R10_TOL + R10_TCR * (t_hi - 25.0)
    rdiv = R118 + R119
    ratio = rdiv / (rdiv + R129)
    k = R119 / rdiv
    e_ratio = R129 / (rdiv + R129) * (e_feed + TOL_REF + TCR_REF * (t_hi - 25.0))
    v_op = W["vos"] + W["drift"] * (W["tj_max_spec"] - 25.0) + W["ios"] * max(R120, R119) + W["ib"] * abs(R120 - R119) + W["psrr"] * (V_CLAMP - W["vmin"])
    vz_hot = R["vz"][1] + R["tcz"] * (t_hi - 25.0)
    vz_low = R["vr"] - R["ir"] * 10 * R129          # the zener under 0.1 uA at 8.0 V (ten times that hot): the node at least this
    R.update(ratio=ratio, k=k, c=k / R["r10"], v_op=v_op, e_ref=e_ref, e_ratio=e_ratio, e_r10=e_r10, vz_hot=vz_hot, vz_low=vz_low)

    def i_min(v):
        node = min(v * ratio * (1 - e_ratio), vz_low)
        return (k * node * (1 - e_ref) - v_op) / (R["r10"] * (1 + e_r10))

    def i_max(v):
        node = min(v * ratio * (1 + e_ratio), vz_hot)
        return (k * node * (1 + e_ref) + v_op) / (R["r10"] * (1 - e_r10))
    R["v_floor"] = R["srn_floor"] - R["vsd_max"]
    R["v_run"] = R["porit"]
    R["table_i"] = [(v, i_min(v), i_max(v)) for v in (R["v_floor"], R["v_run"], R["v_pack_min"], 13.7, W["vmax"], V_CLAMP)]
    R["i_th_min"] = min(x[1] for x in R["table_i"])
    R["i_th_max"] = max(x[2] for x in R["table_i"])
    R["tj_at_max"] = R["air"] + R["i_th_max"] * R["vsd_b"] * R["rja_l4"]
    R["m_lo"] = R["i_th_min"] / R["i_ldo"]
    R["m_hi"] = R["i_safe"] / R["i_th_max"]
    # the reverse threshold (U104)
    r1, r2 = R122 / (R121 + R122), R124 / (R123 + R124)
    eps = r2 / r1 - 1.0
    e_div = TOL_DIV + TCR_DIV * (t_hi - 25.0)
    er = (1 - r1) * 2 * e_div + (1 - r2) * 2 * e_div
    rs1, rs2 = R121 * R122 / (R121 + R122), R123 * R124 / (R123 + R124)
    v_op2 = W["vos"] + W["drift"] * (W["tj_max_spec"] - 25.0) + W["ios"] * max(rs1, rs2) + W["ib"] * abs(rs1 - rs2) + W["psrr"] * (V_CLAMP - W["vmin"])
    R.update(eps=eps, er=er, v_op2=v_op2, rs=(rs1, rs2))
    R["table_v"] = [(v, eps * v - (v * er + v_op2 / r1), eps * v + (v * er + v_op2 / r1)) for v in (R["v_run"], R["v_pack_min"], W["vmax"])]
    R["vt_min"] = min(x[1] for x in R["table_v"])
    R["vt_max"] = max(x[2] for x in R["table_v"])
    R["v_chan"] = R["i_lim"] * R["rds_max"] * CSD_RDS_150 / 2.0
    # the body diodes at the threshold's least current, split between the two FETs, from TI's typical Figure 9 (read)
    i_fet = min(i_min(v) for v in (R["v_run"], R["v_pack_min"], W["vmax"])) / 2.0

    def vsd_typ(t, i):
        lo, hi = CSD_VSD[t]
        return lo + (hi - lo) * math.log10(i / 0.1)
    slope = (vsd_typ(125, i_fet) - vsd_typ(25, i_fet)) / 100.0
    R["i_fet"] = i_fet
    R["vsd_125"] = vsd_typ(125, i_fet)
    R["vsd_150"] = vsd_typ(125, i_fet) + slope * 25.0
    R["vsd_case"] = vsd_typ(25, i_fet) + slope * (t_hi - 25.0)
    # the pull on the return, and what board A then reads on the loop's outgoing conductor
    i_loop = V_CLAMP / (10e3 * (1 - R106_TOL) + R["rt1_min"])
    R["v_ret"] = 2 * R["n_rds"] * N7002_HOT * i_loop
    R["gate_run"] = R["v_run"] / 2.0
    R["out_run"] = R["v_run"] * R["rt1_min"] / (10e3 * (1 + R106_TOL) + R["rt1_min"])
    R["out_pack"] = R["v_pack_min"] * R["rt1_min"] / (10e3 * (1 + R106_TOL) + R["rt1_min"])
    # CELL+ with the breaker off: the LM5069's internal SENSE to OUT resistance feeds PACK_P (L8P-F05)
    r_div = R121 + R122
    R["cell_off_a"] = W["vmax"] * R["r_alive"] / (R["r_so"] + R["r_alive"])
    r_both = R["r_alive"] * r_div / (R["r_alive"] + r_div)
    R["cell_off_ap"] = W["vmax"] * r_both / (R["r_so"] + r_both)
    R["cell_off_clamp"] = V_CLAMP * r_both / (R["r_so"] + r_both)
    # the delays and the burst
    R["tau_i"], R["tau_v"] = R120 * C109, C110 * (rs1 + rs2)
    t_amp = 10 * (5.0 / 0.2e6 + 8e-6)                                # the OPA187's printed typical slew and recovery, taken ten times slower
    R["t_d"] = max(R["tau_i"], R["tau_v"]) * math.log(1.1 / 0.1) + t_amp
    R["t_restart"] = R["hold"] + R["start"]
    R["i_chg_fe"] = R["p_fe"] / R["v_pack_min"]
    R["dT_burst"] = R["i_lim"] * R["vsd_max"] * CSD_ZTH_10MS * R["rjc"]
    # what the detector draws from BRK_VIN
    R["i_standby"] = 2 * W["iq_max"] + (W["vmax"] - R["vz"][0]) / R129 + R["vz"][1] / rdiv + W["vmax"] / (R123 + R124)
    R["ok"] = (R["m_lo"] > 1.0 and R["m_hi"] > 1.0 and R["vt_min"] > R["v_chan"] and R["vt_max"] < R["vsd_150"]
               and R["gate_run"] > R["n_vth"][1] and V_CLAMP / 2.0 < R["n_vgs"] and R["t_restart"] < STRETCH_MIN
               and R["tj_at_max"] < 150.0 and R["v_floor"] >= W["vs"][0] and R["out_run"] >= OUT_POWERED + 0.5)
    return R


def dd5_budget(page, W, R):
    """DD-5 (round 4): the charge switch Q1's body diode in discharge under CHGIN = 1, and the ideal diode beside it. Case row
    C-PROT (record l9stk 15.1 at 0d72880b) with CHGIN = 1 above T3, in discharge. Every figure is read from record l9stk's
    copy or from a maker's sheet; the one reading of a plotted typical curve is marked."""
    N = r"([0-9.]+)"
    D = {}
    # the case row and the defect, record l9stk section 15
    need(page, r"the\s+service\s+is\s+never\s+interrupted:\s+10\s+A\s+held\s+and\s+18\s+A\s+for\s+60\s+s", "l9stk 15.1: the service")
    m = need(page, r"Q1/Q2\s+on\s+board\s+P,\s+both\s+enhanced\s+\|\s+%s\s+W\s+each;\s+TJ\s+%s\s+C\s+on\s+its\s+own\s+pad,\s+%s\s+C\s+with\s+both\s+losses\s+through\s+one\s+pad" % (N, N, N),
             "l9stk 15.5: Q1 and Q2 enhanced")
    D["p_enh"], D["tj_own_l9"], D["tj_one_l9"] = (float(m.group(k)) for k in (1, 2, 3))
    D["k_hot"] = float(need(page, r"the\s+x%s\s+is\s+the\s+CSD18510Q5B's\s+\(ASSUMPTION,\s+E-8\)" % N, "l9stk 15.5: the hot factor").group(1))
    D["p_diode_l9"] = float(need(page, r"its\s+body\s+diode\s+%s\s+W\*\*\s+\(VSD\s+1\s+V\s+at\s+most\)" % N, "l9stk 15.5: Q1's body diode").group(1))
    D["p_pad"] = float(need(page, r"7\s+to\s+10\s+W\s+against\s+the\s+%s\s+W\s+its\s+pad\s+holds" % N, "l9stk 15.6: Q1's pad").group(1))
    D["over"] = float(need(page, r"\*\*Q1\s+OVER\s+\(%s\s+x\)\*\*" % N, "l9stk 15.6: Q1 over").group(1))
    D["tj_retry"] = float(need(page, r"\*\*TJ\s+(\d+)\s+C\*\*\s+\|\s+150\s+C\s+\(1\.48\s+W\s+on\s+its\s+pad\)", "l9stk 15.4b: Q1 in the retry table").group(1))
    m = need(page, r"Breaker\s+\|\s+%s\s+to\s+%s\s+A" % (N, N), "l9stk 15.4: the breaker's threshold")
    D["i_cb"] = float(m.group(2))
    D["t_clear"] = float(need(page, r"\*\*clearing\s+at\s+most\s+%s\s+ms\*\*" % N, "l9stk 15.4: the clearing time").group(1)) * 1e-3
    D["hold_min"] = float(need(page, r"\*\*%s\s+to\s+0\.907\s+s\s+after\s+the\s+enable\s+mates\*\*" % N, "l9stk 15.4: the hold's least").group(1))
    air, i_lim = W["air"], R["i_lim"]
    # TI BQ4050: the technical reference SLUUAQ3A and the data sheet SLUSC67B
    trm, ds = pdftext(TRM_SHEET), pdftext(BQ4050_SHEET)
    need(trm, r"Literature Number: SLUUAQ3A", "the BQ4050 reference's revision"); need(ds, r"SLUSC67B", "the BQ4050 sheet's revision")
    need(trm, r"Not charging AND \(ChargingStatus\(\)\[HT\] = 1", "SLUUAQ3A 4.13: the inhibit's trip while not charging")
    need(trm, r"OperationStatus\(\)\[XCHG\] = 1 if FET Options\[CHGIN\] = 1\.", "SLUUAQ3A 4.13: the FET action under CHGIN")
    need(trm, r"CHGIN \(Bit 4\): FET action in CHARGE INHIBIT mode\s+1 = Charging and Precharging disabled, FETs off\s+0 = FET active \(default\)",
         "SLUUAQ3A 14.2.1.1: CHGIN")
    need(trm, r"CHG FET off AND Current\(\) continuously \u2265 CFET:OFF Threshold", "SLUUAQ3A 3.10: the charge FET's permanent fail")
    D["body_diode_hits"] = len(re.findall(r"body[\s-]*diode", trm, re.I)) + len(re.findall(r"body[\s-]*diode", ds, re.I))
    # TI CSD17570Q5B (SLPS471D): Q1's part, and Q109's
    cs = pdftext(CSD17570_SHEET)
    need(cs, r"SLPS471D", "the CSD17570Q5B sheet's revision")
    m = need(cs, r"VGS = 10 V, ID = 50 A\s+%s\s+%s\s+m\u2126" % (N, N), "CSD17570Q5B: RDS(on) at 10 V")
    D["rds_typ"], D["rds_max"] = float(m.group(1)) * 1e-3, float(m.group(2)) * 1e-3
    D["vsd_max"] = float(need(cs, r"ISD = 50 A, VGS = 0 V\s+0\.8\s+(\d+)\s+V", "CSD17570Q5B: VSD").group(1))
    D["rjc"] = float(need(cs, r"Junction-to-Case Thermal Resistance \(1\)\s+%s" % N, "CSD17570Q5B: RthJC").group(1))
    D["rja"] = float(need(cs, r"Junction-to-Ambient Thermal Resistance \(1\) \(2\)\s+(\d+)", "CSD17570Q5B: RthJA").group(1))
    D["rja_typ"] = float(need(cs, r"Typical R\u03b8JA = (\d+)\u00b0C/W on a 1 inch2", "CSD17570Q5B: the typical RthJA").group(1))
    m = need(cs, r"VDS = VGS, ID = 250 \u03bcA\s+%s\s+%s\s+%s\s+V" % (N, N, N), "CSD17570Q5B: the threshold")
    D["vth"] = (float(m.group(1)), float(m.group(3)))
    D["ciss_max"] = float(need(cs, r"Ciss\s+Input Capacitance\s+(\d+)\s+(\d+)\s+pF", "CSD17570Q5B: Ciss").group(2)) * 1e-12
    D["qg45_max"] = float(need(cs, r"Qg\s+Gate Charge Total \(4\.5 V\)\s+(\d+)\s+(\d+)\s+nC", "CSD17570Q5B: Qg").group(2)) * 1e-9
    D["vgs_abs"] = float(need(cs, r"VGS\s+Gate-to-Source Voltage\s+\u00b1(\d+)\s+V", "CSD17570Q5B: VGS").group(1))
    D["tj_max"] = float(need(cs, r"\u201355 to (\d+)", "CSD17570Q5B: the junction's range").group(1))
    need(cs, r"Figure 8\. Normalized On-State Resistance vs Temperature", "CSD17570Q5B: Figure 8")
    # TI LM74700-Q1 (SNOSD17G): U105
    lm = pdftext(LM74700_SHEET)
    U, DASH = "\u00b5", "\u2013"
    need(lm, r"SNOSD17G", "the LM74700-Q1 sheet's revision")
    m = need(lm, r"Regulated Forward V\(AK\) Threshold\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "LM74700: V(AK REG)")
    D["vreg"] = tuple(float(m.group(k)) * 1e-3 for k in (1, 2, 3))
    m = need(lm, r"threshold for full conduction\s+V\(AK\)\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "LM74700: the full conduction threshold")
    D["vfull"] = tuple(float(m.group(k)) * 1e-3 for k in (1, 2, 3))
    m = need(lm, r"threshold for reverse current\s+V\(AK REV\)\s+%s(\d+)\s+%s(\d+)\s+%s(\d+)\s+mV" % (DASH, DASH, DASH), "LM74700: V(AK REV)")
    D["vrev"] = tuple(-float(m.group(k)) * 1e-3 for k in (1, 2, 3))
    D["gm_min"] = float(need(lm, r"Gm\s+(\d+)\s+(\d+)\s+(\d+)\s+%sA/V" % U, "LM74700: the error amplifier").group(1)) * 1e-6
    D["i_src_min"] = float(need(lm, r"Peak source current\s+(\d+)\s+(\d+)\s+mA", "LM74700: the gate's source current").group(1)) * 1e-3
    m = need(lm, r"Regulation max sink current\s+(\d+)\s+(\d+)\s+%sA" % U, "LM74700: the regulation's sink")
    D["i_sink"] = (float(m.group(1)) * 1e-6, float(m.group(2)) * 1e-6)
    D["i_pump_min"] = float(need(lm, r"V\(VCAP\) %s V\(ANODE\) = 7 V\s+(\d+)\s+(\d+)\s+(\d+)\s+%sA" % (DASH, U), "LM74700: the charge pump's current").group(1)) * 1e-6
    D["vcap_on_min"] = float(need(lm, r"Charge pump turn on voltage\s+%s\s+%s\s+%s\s+V" % (N, N, N), "LM74700: the pump's turn on").group(1))
    D["vcap_off_max"] = float(need(lm, r"Charge pump turn off voltage\s+%s\s+%s\s+%s\s+V" % (N, N, N), "LM74700: the pump's turn off").group(3))
    D["uvlor_max"] = float(need(lm, r"UV release at rising\s+V\(ANODE\) %s V\(CATHODE\) = 100 mV\s+%s\s+%s\s+%s\s+V" % (DASH, N, N, N), "LM74700: VCAP's release").group(3))
    D["uvlof_max"] = float(need(lm, r"UV threshold at\s+V\(ANODE\) %s V\(CATHODE\) = 100 mV\s+%s\s+%s\s+(\d+)\s+V" % (DASH, N, N), "LM74700: VCAP's lockout").group(3))
    D["i_shdn"] = float(need(lm, r"Shutdown Supply Current\s+V\(EN\) = 0 V\s+%s\s+%s\s+%sA" % (N, N, U), "LM74700: the shutdown current").group(2)) * 1e-6
    m = need(lm, r"Operating Quiescent Current\s+(\d+)\s+(\d+)\s+%sA" % U, "LM74700: the quiescent current")
    D["iq"] = (float(m.group(1)) * 1e-6, float(m.group(2)) * 1e-6)
    D["en_il_min"] = float(need(lm, r"Enable input low threshold\s+%s\s+%s\s+%s" % (N, N, N), "LM74700: EN low").group(1))
    D["en_ih_max"] = float(need(lm, r"Enable input high threshold\s+%s\s+%s\s+%s" % (N, N, N), "LM74700: EN high").group(3))
    D["i_en"] = float(need(lm, r"Enable sink current\s+V\(EN\) = 12 V\s+(\d+)\s+(\d+)\s+%sA" % U, "LM74700: EN's sink").group(2)) * 1e-6
    D["entdly"] = float(need(lm, r"ENTDLY\s+V\(VCAP\) > V\(VCAP UVLOR\)\s+(\d+)\s+(\d+)\s+%ss" % U, "LM74700: ENTDLY").group(2)) * 1e-6
    D["t_rev"] = float(need(lm, r"tReverse delay\s+%s\s+%s\s+%ss" % (N, N, U), "LM74700: the reverse delay").group(2)) * 1e-6
    D["t_fwd"] = float(need(lm, r"tForward recovery\s+%s\s+%s\s+%ss" % (N, N, U), "LM74700: the forward recovery").group(2)) * 1e-6
    D["i_cath"] = float(need(lm, r"V\(ANODE\) %s V\(CATHODE\) = %s100 mV\s+1\.2\s+%s\s+%sA" % (DASH, DASH, N, U), "LM74700: the cathode's current").group(1)) * 1e-6
    D["en_abs"] = (-0.3, float(need(lm, r"EN to GND, V\(ANODE\) > 0 V\s+%s0\.3\s+(\d+)\s+V" % DASH, "LM74700: EN's rating").group(1)))
    D["gate_abs"] = float(need(lm, r"GATE to ANODE\s+%s0\.3\s+(\d+)\s+V" % DASH, "LM74700: GATE's rating").group(1))
    need(lm, r"ensures\s+zero\s+DC\s+reverse\s+current\s+flow", "LM74700: zero DC reverse current")
    need(lm, r"VCAP: Minimum 0\.1 %sF is required; recommended value of VCAP \(%sF\) \u2265 10 x CISS\(MOSFET\)\(%sF\)" % (U, U, U), "LM74700: VCAP's capacitor")
    need(lm, r"CIN: minimum 22 nF of input capacitance", "LM74700: CIN"); need(lm, r"COUT: minimum 100 nF of output capacitance", "LM74700: COUT")
    need(lm, r"As a guideline, it is suggested to choose \(20 mV / ILoad\(Nominal\)\) \u2264 RDS\(ON\) \u2264 \( 50 mV / ILoad\(Nominal\)\)", "LM74700: the FET guideline")
    need(lm, r"During forward regulation mode the ANODE\s+to CATHODE voltage is regulated to 20 mV by adjusting the GATE to ANODE voltage", "LM74700: the regulated mode")
    need(lm, r"forward current flow through the external MOSFET is not interrupted but is conducted through\s+the MOSFET.s body diode", "LM74700: shutdown")
    # the 1N4148W (D104), read at 1 mA
    d4 = pdftext(D4148_SHEET)
    D["vf_d"] = float(need(d4, r"at IF = 1 mA\s+-\s+%s" % N, "1N4148W: VF at 1 mA").group(1))
    # the arithmetic: Q109's loss, with Q2's on the same pour
    r_hot = D["rds_max"] * D["k_hot"]
    D["r_hot"] = r_hot
    D["v_leak"] = (D["vcap_off_max"] / R130 + IGSS_17570) / D["gm_min"]          # R130's and the gate's leakage through the error amplifier
    v_reg = D["vreg"][2] + D["v_leak"]
    D["v_reg_max"] = v_reg
    rows = []
    for i in (10.0, 18.0, i_lim):
        v_ir = i * r_hot
        vak = max(v_reg, v_ir)
        p109, p2 = i * vak, i * i * r_hot
        rows.append({"i": i, "v_ir": v_ir, "vak": vak, "p109": p109, "p2": p2, "p_before": i * D["vsd_max"],
                     "tj_own": air + p109 * D["rja"], "tj_one": air + (p109 + p2) * D["rja"],
                     "p_hunt": i * max(D["vfull"][2], v_ir), "tj_hunt": air + (i * max(D["vfull"][2], v_ir) + p2) * D["rja"]})
    D["rows"] = rows
    D["rth_need"] = (D["tj_max"] - air) / (rows[2]["p109"] + rows[2]["p2"])
    D["rth_robust"] = (D["tj_max"] - air) / (rows[2]["p_hunt"] + rows[2]["p2"])
    # the typical basis, for scale: typical RDS(on) at Figure 8's 150 C factor (read), the regulation's 20 mV, the typical path
    rt = D["rds_typ"] * CSD17570_RDS_150
    vt = max(D["vreg"][1], i_lim * rt)
    D["tj_typ"] = air + (i_lim * vt + i_lim * i_lim * rt) * D["rja_typ"]
    # the breaker's largest threshold until it clears; the body diodes before U105 drives
    D["p_cb"] = D["i_cb"] ** 2 * r_hot
    D["dt_cb"] = D["p_cb"] * D["rjc"]
    D["dt_diode"] = i_lim * D["vsd_max"] * D["rjc"]
    c111_min = C111 * (1 - C111_TOL) * (1 - C111_BIAS)
    D["c111_min"] = c111_min
    D["t_drv_en"] = D["entdly"] + C111 * (1 + C111_TOL) * D["uvlor_max"] / D["i_pump_min"]
    D["qg_full"] = D["qg45_max"] + D["ciss_max"] * (D["vcap_off_max"] - 4.5)       # a model: Ciss above the plateau
    D["droop"] = D["qg_full"] / c111_min
    D["t_on"] = D["t_fwd"] + D["qg_full"] / D["i_src_min"]
    # reverse: the fast comparator and, under it, the regulation's sink
    D["i_rev_fast"] = -D["vrev"][0] / D["rds_typ"]
    D["t_rev_slow"] = D["qg_full"] / D["i_sink"][0]
    D["q_rev"] = R["i_chg_fe"] * D["t_rev_slow"]
    # EN and the standby
    D["en_on"] = D["en_ih_max"] + D["vf_d"]
    D["i_run"] = D["iq"][1] + W["vmax"] / R131 + D["i_en"]
    D["i_off"] = D["i_shdn"] + IDSS_17570
    # TI's guideline window against the kit's currents
    D["win"] = [(i, 0.020 / i, 0.050 / i) for i in (10.0, 18.0, i_lim)]
    D["p_window_fet"] = i_lim ** 2 * (0.020 / 10.0) * D["k_hot"]
    # round 6 (the check V2's V2-m8): the board's whole loss at the held current, from the drawn values, against the area the
    # makers' test boards assume: the sheet's 50 C/W is one device on 1 in2 of 2 oz on a 1.5 in x 1.5 in board (SLPS471D 5.2 notes)
    need(cs, r"mounted on a 1 inch2 \(6\.45 cm2\), 2 oz\. \(0\.071 mm thick\) Cu pad on a 1\.5 inches \u00d7 1\.5 inches", "CSD17570Q5B: the RthJA test board")
    gp = open(os.path.join(TOOLS, "gen_pcb_p.py"), encoding="utf-8").read()
    m = need(gp, r"^BOARD_L, BOARD_W, BOARD_R = ([0-9.]+), ([0-9.]+), ", "board P's outline")
    D["board_in2"] = float(m.group(1)) * float(m.group(2)) / 645.16
    brk = open(MINE["p"], encoding="utf-8").read()
    rs = [float(need(brk, r'r\("%s", "([0-9.]+)m 1%% 2512 \(breaker sense' % ref, "the breaker draft's %s" % ref).group(1)) * 1e-3 for ref in ("R101", "R102")]
    v_rs = i_lim * rs[0] * rs[1] / (rs[0] + rs[1])
    D["joint"] = (("Q109", rows[2]["p109"]), ("Q2", rows[2]["p2"]), ("Q101 and Q102", 2 * (i_lim / 2.0) ** 2 * R["rds_max"] * CSD_RDS_150),
                  ("R10", i_lim ** 2 * R["r10"]), ("R101", v_rs ** 2 / rs[0]), ("R102", v_rs ** 2 / rs[1]))
    D["p_joint"] = sum(p_ for _n, p_ in D["joint"])
    D["pads_in2"] = 3 * 1.5 * 1.5                                    # the SW pour's test board and IF-2's two for the breaker FETs
    D["ok"] = (all(r_["tj_one"] <= D["tj_max"] for r_ in rows) and all(r_["p109"] <= D["p_pad"] for r_ in rows)
               and all(r_["p_before"] > D["p_pad"] for r_ in rows)
               and D["t_drv_en"] < D["hold_min"] and D["vcap_on_min"] - D["droop"] > D["uvlof_max"]
               and c111_min >= 10 * D["ciss_max"] and D["vcap_off_max"] <= min(D["vgs_abs"], D["gate_abs"])
               and D["vth"][1] <= 2.0 and V_CLAMP <= D["en_abs"][1] and D["en_on"] < W["vmin"] and D["body_diode_hits"] == 0)
    return D


def typ_ratio(t):
    """Murata 3.2's typical BB curve, R/R25 at t (log-linear between the read points; INFERRED)."""
    pts = PRF_BB_TYP
    if not pts[0][0] <= t <= pts[-1][0]:
        refuse("the typical curve is read from %.2f to %.2f C only, not at %.2f C" % (pts[0][0], pts[-1][0], t))
    for (t0, r0), (t1, r1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            return r0 * (r1 / r0) ** ((t - t0) / (t1 - t0))


def typ_temp(ratio):
    """The inverse: the temperature at which the typical BB curve reads ratio (INFERRED)."""
    pts = PRF_BB_TYP
    for (t0, r0), (t1, r1) in zip(pts, pts[1:]):
        if r0 <= ratio <= r1:
            return t0 + (t1 - t0) * math.log(ratio / r0) / math.log(r1 / r0)
    refuse("the typical curve does not reach R/R25 %.3f in its read span" % ratio)


def stale_copies(l4dir):
    """The check V2's V2-B2, as a guard: this record's copies of task L4-E11 against a tree's records/l4e11/. It returns the copies
    that are not that tree's: a copied section that is not in the tree's page word for word, a copied draft whose bytes differ.
    A tree whose L4-E11 page predates its round 10 (no section 20c: this record's own base, main at 64cd25ee) holds nothing the
    copies could be behind, and returns nothing."""
    page = os.path.join(l4dir, "L4E11-SOURCE-ONLY-AND-ENTRY.md")
    text = open(page, encoding="utf-8").read() if os.path.isfile(page) else ""
    if "\n### 20c. " not in text:
        return []
    bad = []
    for key, head in L4E11_SECTIONS:
        copy = open(os.path.join(HERE, INPUT_FILES[key]), encoding="utf-8").read()
        if not copy.startswith(head) or copy not in text:
            bad.append("%s is not the tree's section %s" % (INPUT_FILES[key], head.strip()))
    for copy_rel, name in L4E11_DRAFTS:
        t = os.path.join(l4dir, name)
        if not os.path.isfile(t) or open(t, "rb").read() != open(os.path.join(HERE, copy_rel), "rb").read():
            bad.append("%s is not the tree's %s" % (copy_rel, name))
    return bad


def tdk_window(k_low, k_trip, k_notrip):
    """The scale k of the enable loop (R106, R107 and the guard divided by k together) for a guard part of lower resistance: the
    loop sees k x R. No trip asks k x R(no trip) at most the first inverter's stay-on level: an UPPER bound, k_notrip. Surely off
    asks k x R(off) at least its sure-off level: a LOWER bound, k_trip. A held DOCK_EN_OUT read powered asks k x R(least) at least
    board A's level: a LOWER bound, k_low. So the window is max(k_low, k_trip) to k_notrip; it exists when the first is not over
    the second. (Round 5 took k_trip as an upper bound: the check V2's V2-B3.)"""
    return max(k_low, k_trip), k_notrip


def round5(texts, W, R):
    """Rounds 5 and 6: the interface of 12f restated from L4-E11's 20c and 20d; L8P-F06 (the breaker FETs' hot off leakage against
    BOTH limits of L4-E11's latch as its round 12 states them (copied at L4E11_AT): the static limit and the timing limit, with its own
    source list) and L8P-F07 (the guard RT1's printed points against the loop's levels), from the copies, Murata's and TI's
    sheets, and Murata's typical curve as read (INFERRED); the alternative guard part's limits as typed from TDK's held sheet."""
    N = r"([0-9.]+)"
    F = {}
    page, l10c, l10d, l10e = texts["page"], texts["l4e11c"], texts["l4e11d"], texts["l4e11e"]
    l22b, l22c, l22g, l22h = texts["l4e11_22b"], texts["l4e11_22c"], texts["l4e11_22g"], texts["l4e11_22h"]
    # 12f restated: L4-E11 20c (the levels; section 3b reads them) and 20d (the delays)
    F["t_set"] = float(need(l10d, r"\|\s+\*\*the\s+inhibit\s+set\*\*\s+\|\s+\*\*%s\s+ms\*\*,\s+under\s+the\s+interface's\s+1\s+ms" % N,
                            "L4-E11 20d: the inhibit set").group(1)) * 1e-3
    F["t_end"] = float(need(l10d, r"\*\*The\s+charge\s+through\s+the\s+off\s+breaker\s+ends\s+within\s+%s\s+ms\*\*\s+of\s+passing\s+board\s+P's\s+threshold" % N,
                            "L4-E11 20d: the charge ended").group(1)) * 1e-3
    F["hold_min"] = float(need(l10d, r"It\s+lasts\s+\*\*at\s+least\s+%s\s+s\*\*\s+after\s+the\s+return\s+rises" % N, "L4-E11 20d: the hold").group(1))
    m = need(l10d, r"%s\s+s\s+over\s+the\s+interface's\s+1\.0\s+s\s+and\s+%s\s+s\s+over\s+the\s+breaker's\s+restart\s+\(%s\s+s\)" % (N, N, N),
             "L4-E11 20d: the hold against the restart")
    F["over_if"], F["over_rs"], F["restart_l4"] = float(m.group(1)), float(m.group(2)), float(m.group(3))
    F["load_ret"] = float(need(l10c, r"\*\*The\s+load\s+on\s+DOCK_EN_RET\*\*\s+is\s+SENSE1\s+alone,\s+at\s+most\s+%s\s+uA" % N,
                               "L4-E11 20c: the load on the return").group(1)) * 1e-6
    F["load_out"] = float(need(l10c, r"board\s+A's\s+%s\s+kOhm\s+on\s+it" % N, "L4-E11 20c: the load on DOCK_EN_OUT").group(1)) * 1e3
    m = need(l10c, r"board\s+P's\s+first\s+inverter\s+turns\s+off\s+\(its\s+gate\s+2\.5\s+to\s+1\.0\s+V\)\s+from\s+%s\s+to\s+%s\s+kOhm\s+at\s+%s\s+V" % (N, N, N),
             "L4-E11 20c: the first inverter's turn-off band")
    F["l4_on"], F["l4_off"], F["l4_v"] = float(m.group(1)) * 1e3, float(m.group(2)) * 1e3, float(m.group(3))
    F["window"] = float(need(l10c, r"never\s+reads\s+held\s+while\s+RT1\s+is\s+under\s+\*\*%s\s+kOhm\*\*" % N, "L4-E11 20c: the window").group(1)) * 1e3
    need(l10c, r"Murata\s+prints\s+RT1\s+at\s+most\s+15\s+kOhm\s+at\s+25\s+C\s+and\s+100\s+kOhm\s+only\s+above\s+110\s+C", "L4-E11 20c: Murata's points")
    # the 2N7002's off leakage (Q107 on the return): JSCJ C8545
    nj = pdftext(N7002_SHEET)
    F["n_idss"] = float(need(nj, r"Zero Gate Voltage Drain Current\s+IDSS\s+VDS=60 V, VGS=0 V\s+(\d+)\s+nA", "2N7002: IDSS").group(1)) * 1e-9
    # the first inverter's gate (the loop's return) against RT1, with board A's loads: node OUT carries the 984 kOhm, node RET the
    # sinks; R106 and R107 at their ASSUMED 1 %, each at the sign that is worse for the side judged
    i_s = F["load_ret"] + F["n_idss"]
    v_on, v_off = R["n_vth"][1], R["n_vth"][0]

    def rt_on(v):          # the largest RT1 that still holds the gate at the 2N7002's most threshold: no trip under it
        r6, r7 = 10e3 * (1 + R106_TOL), 22e3 * (1 - R107_TOL)
        out = (v / r6 - v_on / r7 - i_s) / (1.0 / r6 + 1.0 / F["load_out"])
        return (out - v_on) / (v_on / r7 + i_s)

    def rt_off(v):         # the least RT1 that surely turns the first inverter off (its gate at the least threshold, no loads)
        r6, r7 = 10e3 * (1 - R106_TOL), 22e3 * (1 + R107_TOL)
        return v * r7 / v_off - r6 - r7

    def rt_low(v):         # the least RT1 for which a held DOCK_EN_OUT still reads powered (the return taken at 0 V)
        r6 = 10e3 * (1 + R106_TOL)
        rp = OUT_POWERED * r6 / (v - OUT_POWERED)
        return rp * F["load_out"] / (F["load_out"] - rp)
    F["nom_on"] = F["l4_v"] * 22e3 / v_on - 32e3
    F["nom_off"] = F["l4_v"] * 22e3 / v_off - 32e3
    F["on"] = {v: rt_on(v) for v in (F["l4_v"], W["vmax"])}
    F["off"] = {v: rt_off(v) for v in (F["l4_v"], W["vmax"])}
    F["low"] = {v: rt_low(v) for v in (R["v_run"], F["l4_v"])}
    # ---- L8P-F06: the breaker FETs' off leakage into CELL+ while the breaker is off (L4-E11 20e's budget)
    cs = pdftext(CSD_SHEET)
    need(cs, r"5\.1 Electrical Characteristics\s*\nTA = 25\u00b0C \(unless otherwise stated\)", "CSD18510Q5B: 5.1 at 25 C")
    m = need(cs, r"^IDSS\s+Drain-to-source leakage current\s+VGS = 0 V, VDS = (\d+) V\s+([0-9.]+)\s+\u03bcA", "CSD18510Q5B: IDSS")
    F["idss_v"], F["idss"] = float(m.group(1)), float(m.group(2)) * 1e-6
    F["idss_rows"] = len(re.findall(r"^IDSS\s", cs, re.M))
    # L4-E11's round 12, unchanged in the round copied: TWO limits on the sources into CELL+ while the inhibit holds and the breaker is off
    F["i_static"] = float(need(l10e, r"The\s+latch\s+reads\s+dead\s+while\s+every\s+source\s+into\s+CELL\+\s+stays\s+under\s+\*\*%s\s+mA\*\*\s+together\s+\(the\s+static\s+limit\)" % N,
                               "L4-E11 20e: the static limit").group(1)) * 1e-3
    F["l4_each"] = float(need(l10e, r"may\s+reach\s+(\d+)\s+uA\s+each\s+before\s+that\s+limit", "L4-E11 20e: the battery FETs' static room").group(1)) * 1e-6
    m = need(l10e, r"\*\*within\s+%s\s+s\s+with\s+the\s+sources\s+at\s+their\s+hot\s+bound\s+\(%s\s+uA,\s+22b\),\s+inside\s+the\s+hold's\s+least\s+%s\s+s\s+while\s+the\s+sources\s+total\s+under\s+%s\s+uA\*\*" % (N, N, N, N),
             "L4-E11 20e: the bleed and the timing limit")
    F["bleed_hot"], F["hot_bound"], hold_e, F["i_timing"] = float(m.group(1)), float(m.group(2)) * 1e-6, float(m.group(3)), float(m.group(4)) * 1e-6
    if abs(hold_e - F["hold_min"]) > 1e-9:
        refuse("L4-E11's 20e and 20d no longer print the same least hold")
    m = need(l10e, r"from\s+VSYS's\s+%s\s+V\s+through\s+R256\s+into\s+CELL_FUSED's\s+%s\s+uF\s+\(\+%s\s+%%,\s+ASSUMPTION\)" % (N, N, N), "L4-E11 20e: the bleed's start and capacitance")
    F["v0"], F["c_fused"], F["c_tol"] = float(m.group(1)), float(m.group(2)) * 1e-6, float(m.group(3)) / 100.0
    m = need(l10c, r"dead\s+under\s+\*\*%s\s+V\*\*\s+at\s+least,\s+alive\s+over\s+\*\*%s\s+V\*\*\s+at\s+most\s+\(the\s+foot\s+at\s+RESET's\s+%s\s+V" % (N, N, N), "L4-E11 20c: the dead reading")
    F["v_dead"], F["v_alive"], F["v_foot"] = float(m.group(1)), float(m.group(2)), float(m.group(3))
    dd7 = open(os.path.join(HERE, L4E11_DRAFTS[1][0]), encoding="utf-8").read()
    m = need(dd7, r'r\("R256", "([0-9.]+)k (\d+)%", "CELL\+", "DD7_BL"', "L4-E11's DD-7 draft: R256")
    F["r256"], F["r256_tol"] = float(m.group(1)) * 1e3, float(m.group(2)) / 100.0
    # its source list (22b), each as it labels it
    m = need(l22b, r"\|\s+the\s+LM5069's\s+internal\s+1\s+MOhm,\s+SENSE\s+to\s+OUT\s+\|\s+%s\s+uA\s+at\s+BRK_VIN\s+%s\s+V\s+\(%s\s+uA\s+at\s+the\s+%s\s+V\s+clamp\)" % (N, N, N, N), "L4-E11 22b: the 1 MOhm")
    l4_so = {float(m.group(2)): float(m.group(1)) * 1e-6, float(m.group(4)): float(m.group(3)) * 1e-6}
    m = need(l22b, r"\|\s+the\s+three\s+battery\s+FETs\s+Q39,\s+Q40,\s+Q42\s+\|\s+%s\s+uA\s+at\s+25\s+C,\s+\*\*%s\s+uA\s+at\s+Tj\s+125\s+C\*\*\s+\(1\s+and\s+10\s+uA\s+each,\s+VDS\s+-30\s+V\)\s+\|\s+MAKER,\s+printed\s+maxima:\s+Nexperia\s+BUK6Y10-30P\s+\(17\s+April\s+2020\)\s+Table\s+7\s+p\.6" % (N, N),
             "L4-E11 22b: the battery FETs' printed rows")
    F["bat25"], F["bat125"] = float(m.group(1)) * 1e-6, float(m.group(2)) * 1e-6
    m = need(l22b, r"\*\*%s\s+uA\s+at\s+the\s+%s\s+C\s+air,\s+%s\s+uA\s+at\s+the\s+held\s+%s\s+C\s+case\*\*" % (N, N, N, N), "L4-E11 22b: the breaker pair as it takes this record's F06")
    l4_pair_air, l4_air, l4_pair_case, l4_case = (float(m.group(k)) for k in (1, 2, 3, 4))
    l4_hot = float(need(l22b, r"=\s+\*\*%s\s+uA\*\*\s+\(%s\s+uA\s+at\s+the\s+air;\s+%s\s+uA\s+with\s+BRK_VIN\s+at\s+the\s+clamp" % (N, N, N), "L4-E11 22b: the hot bound").group(1)) * 1e-6
    l4_pair_room = float(need(l22c, r"\|\s+what\s+that\s+leaves\s+the\s+breaker\s+pair\s+\|\s+%s\s+uA\s+\|\s+\*\*%s\s+uA\*\*\s+\|" % (N, N), "L4-E11 22c: the pair's timing room").group(2)) * 1e-6
    m = need(l22c, r"\|\s+%s\s+C;\s+every\s+%s\s+K\s+\|\s+%s\s+C;\s+every\s+%s\s+K\s+\|\s+%s\s+C;\s+every\s+%s\s+K\s+\|" % ((N,) * 6), "L4-E11 22c: the pair's case and doubling at the timing limit")
    l4_t_fill, l4_d_fill = float(m.group(3)), float(m.group(4))
    l4_hand = float(need(l22g, r"E-14c's\s+acceptance\s+\(the\s+pair\s+at\s+most\s+388\s+uA\s+at\s+101\s+C\)\s+keeps\s+the\s+timing\s+with\s+%s\s+uA\s+in\s+hand" % N, "L4-E11 22g: E-14c against the timing").group(1)) * 1e-6
    need(l22g, r"\*\*Between\s+520\.7\s+uA\s+and\s+0\.846\s+mA\*\*\s+\(not\s+reached\s+at\s+the\s+hot\s+bound\):\s+the\s+hold\s+may\s+end\s+with\s+CELL\+\s+still\s+read\s+alive\s+and\s+the\s+breaker\s+off", "L4-E11 22g: between the two limits")
    F["i_so"] = {v: v / R["r_so"] for v in (W["vmax"], V_CLAMP)}
    if any(abs(F["i_so"][v] - l4_so.get(v, -1.0)) > 0.06e-6 for v in F["i_so"]):
        refuse("L4-E11 22b's figures for the LM5069's 1 MOhm are not this record's (%r against %r)" % (l4_so, F["i_so"]))
    idss_t = lambda t, d=IDSS_DOUBLING: F["idss"] * 2.0 ** ((t - 25.0) / d)
    F["t_case"], F["t_air"] = W["case_held"], W["air"]
    F["pair_case"], F["pair_air"], F["pair_125"] = 2 * idss_t(W["case_held"]), 2 * idss_t(W["air"]), 2 * idss_t(125.0)
    if abs(F["pair_case"] * 1e6 - l4_pair_case) > 0.06 or abs(F["pair_air"] * 1e6 - l4_pair_air) > 0.06 or (l4_air, l4_case) != (W["air"], W["case_held"]):
        refuse("L4-E11 22b no longer carries this record's F06 figures for the breaker pair")
    # what each limit leaves the breaker pair, the 1 MOhm and the battery FETs' printed 125 C row counted first
    F["room_static"] = {v: F["i_static"] - F["i_so"][v] - F["bat125"] for v in F["i_so"]}
    F["room_timing"] = {v: F["i_timing"] - F["i_so"][v] - F["bat125"] for v in F["i_so"]}
    F["l4_each_re"] = (F["i_static"] - F["i_so"][V_CLAMP]) / 3.0     # L4-E11's 272 uA a battery FET: the static limit less the clamp's 1 MOhm, over three
    fill_t = lambda room: 25.0 + IDSS_DOUBLING * math.log2(room / (2 * F["idss"]))
    fill_d = lambda room: (W["case_held"] - 25.0) / math.log2(room / (2 * F["idss"]))
    F["left_static"] = F["room_static"][V_CLAMP] - F["pair_case"]
    F["left_timing"] = {v: F["room_timing"][v] - F["pair_case"] for v in F["i_so"]}
    F["t_fill_static"], F["d_fill_static"] = fill_t(F["room_static"][V_CLAMP]), fill_d(F["room_static"][V_CLAMP])
    F["t_fill_timing"] = {v: fill_t(F["room_timing"][v]) for v in F["i_so"]}
    F["d_fill_timing"] = {v: fill_d(F["room_timing"][v]) for v in F["i_so"]}
    F["hot_bound_re"] = F["i_so"][W["vmax"]] + F["bat125"] + F["pair_case"]
    # with the pair at its ASSUMED held-case figure, what each limit leaves a battery FET (Nexperia's printed 125 C row: bat125 / 3)
    F["each_left_static"] = (F["i_static"] - F["i_so"][V_CLAMP] - F["pair_case"]) / 3.0
    F["each_left_timing"] = (F["i_timing"] - F["i_so"][W["vmax"]] - F["pair_case"]) / 3.0
    # L4-E11's own derived figures, read from its copies, against this record's arithmetic: refused when they part
    for what, mine, theirs, tol in (("the hot bound", F["hot_bound_re"], F["hot_bound"], 0.06e-6), ("the hot bound of 22b", F["hot_bound_re"], l4_hot, 0.06e-6),
                                    ("the pair's timing room", F["room_timing"][W["vmax"]], l4_pair_room, 0.06e-6),
                                    ("the case that fills the timing room", F["t_fill_timing"][W["vmax"]], l4_t_fill, 0.06),
                                    ("the doubling that fills it", F["d_fill_timing"][W["vmax"]], l4_d_fill, 0.006),
                                    ("E-14c's margin to the timing limit", F["left_timing"][W["vmax"]], l4_hand, 0.06e-6)):
        if abs(mine - theirs) > tol:
            refuse("%s: this record computes %g where L4-E11's copy prints %g" % (what, mine, theirs))
    # the timing limit reproduced from L4-E11's printed inputs (its 22a form: the sources lift the level CELL+ falls towards)
    r_bl, c_bl = F["r256"] * (1 + F["r256_tol"]), F["c_fused"] * (1 + F["c_tol"])

    def bleed(i):
        vinf = F["v_foot"] + i * r_bl
        return r_bl * c_bl * math.log((F["v0"] - vinf) / (F["v_dead"] - vinf)) if vinf < F["v_dead"] else float("inf")
    F["bleed_hot_re"] = bleed(F["hot_bound"])
    lo, hi = 0.0, (F["v_dead"] - F["v_foot"]) / r_bl
    for _ in range(80):
        mid = (lo + hi) / 2.0
        lo, hi = (mid, hi) if bleed(mid) < F["hold_min"] else (lo, mid)
    F["i_timing_re"] = lo
    F["i_static_re"] = (F["v_dead"] - F["v_foot"]) / r_bl
    F["bleed_none_re"], F["bleed_pair_case"] = bleed(0.0), bleed(F["i_so"][W["vmax"]] + F["bat125"] + F["pair_case"])
    if abs(F["bleed_hot_re"] - F["bleed_hot"]) > 0.002 or abs(F["i_timing_re"] / F["i_timing"] - 1.0) > 0.005 or abs(F["i_static_re"] / F["i_static"] - 1.0) > 0.005:
        refuse("L4-E11's bleed is not reproduced from its printed inputs: %.4f s against %.3f s, %.1f uA against %.1f uA, %.1f uA against %.1f uA" % (
            F["bleed_hot_re"], F["bleed_hot"], F["i_timing_re"] * 1e6, F["i_timing"] * 1e6, F["i_static_re"] * 1e6, F["i_static"] * 1e6))
    F["bleed_fn"] = bleed
    F["f06_static"] = F["pair_case"] < F["room_static"][V_CLAMP]
    F["f06_timing"] = F["pair_case"] < F["room_timing"][W["vmax"]]
    F["f06_holds"] = F["f06_static"] and F["f06_timing"] and F["idss_v"] >= V_CLAMP
    # ---- L8P-F07: RT1's printed points (Murata DM-SA16-E056 Rev.1, p.4) against the loop
    mt = pdftext(PRF_SHEET)
    need(mt, r"Doc\.\.No\. DM-SA16-E056 Rev\.1 201608\s+4 / 16", "Murata PRF: the sheet's revision and page 4")
    need(mt, r"3\.2 Resistance-Temperature Characteristics Typical Curve", "Murata PRF: 3.2 is a typical curve")
    need(mt, r"The resistance change with\s+Resistance at each ambient temperature is\s*\n\s+characteristics\s+temperature typical curve", "Murata PRF: 3.3.2")
    need(mt, r"4\.1 Resistance - Temperature characteristics Range \(Reference\)\s*\nExample PRF18 Series / BB Type", "Murata PRF: 4.1, a reference range for PRF18 BB")
    hdrs = [(h.start(), h.group(1), h.group(2)) for h in re.finditer(r"\*at ([0-9.]+[kM]?ohm)\s+\*at ([0-9.]+[kM]?ohm)", mt)]
    row = r"%s\s+(\d+)k?\+/-(\d+)%%\s+([>\uff1e]?)(\d+)(?:\+/-(\d+))?\s+(\d+)\+/-(\d+)\s+(\d+)V\s+-(\d+)\S\s*\+\s*(\d+)"
    P = {}
    for pn in ("PRF15BB103RB6RC", "PRF15BB102RB6RC", "PRF15BA102RB6RC"):
        m = need(mt, row % pn, "Murata PRF: the row %s" % pn)
        h = [x for x in hdrs if x[0] < m.start()][-1]
        unit = lambda t: float(re.match(r"[0-9.]+", t).group(0)) * {"k": 1e3, "M": 1e6}.get(re.sub(r"[0-9.]", "", t)[0], 1.0)
        P[pn] = {"r25": float(m.group(1)) * (1e3 if "k+" in m.group(0) else 1.0), "tol": float(m.group(2)) / 100.0, "gt": m.group(3) != "",
                 "t1": float(m.group(4)), "t1_tol": float(m.group(5)) if m.group(5) else None, "t2": float(m.group(6)), "t2_tol": float(m.group(7)),
                 "vmax": float(m.group(8)), "tmin": -float(m.group(9)), "tmax": float(m.group(10)), "r1": unit(h[1]), "r2": unit(h[2])}
    F["prf"] = P
    g = P["PRF15BB103RB6RC"]
    F["l9_47k"] = bool(re.search(r"PRF15BB103\s+chip\s+PTC:\s+10\s+kOhm\s+plus\s+or\s+minus\s+50\s+%,\s+47\s+kOhm\s+at\s+130\s+C\s+plus\s+or\s+minus\s+3\s+C", page))
    F["hdr_47k"] = [h[1] for h in hdrs if h[2] == "47kohm"]          # the 470 ohm groups' columns: at 4.7 kOhm and at 47 kOhm
    # l9stk 15.5's junction readings at the allowances (held), and the junction's lead over its copper
    m = need(page, r"-\s+%s\s+C\s+at\s+10\s+A;\s*\n-\s+%s\s+C\s+in\s+the\s+18\s+A\s+service;\s*\n-\s+%s\s+C\s+at\s+23\.93\s+A,\s+by\s+construction" % (N, N, N),
             "l9stk 15.5: the junction at the allowances")
    F["tj10"], F["tj18"], F["tj24"] = float(m.group(1)), float(m.group(2)), float(m.group(3))
    F["lead24"] = float(need(page, r"A\s+junction\s+leads\s+its\s+copper\s+by\s+%s\s+K\s+at\s+23\.93\s+A" % N, "l9stk 15.5: the junction's lead").group(1))
    F["static"] = float(need(page, r"the\s+loop's\s+static\s+%s\s+mA" % N, "l9stk: the loop's static draw").group(1)) * 1e-3
    F["cu10"], F["cu18"] = (F["tj10"] - F["lead24"] * (10.0 / R["i_lim"]) ** 2, F["tj18"] - F["lead24"] * (18.0 / R["i_lim"]) ** 2)
    r25_lo, r25_hi = g["r25"] * (1 - g["tol"]), g["r25"] * (1 + g["tol"])
    F["r25"] = (r25_lo, r25_hi)
    # the printed bounds, each read as a single crossing (INFERRED: the sheet defines the sensing temperature where R reaches the value)
    F["print"] = {"under_r1_to": g["t1"], "under_r2_to": g["t2"] - g["t2_tol"], "over_r2_from": g["t2"] + g["t2_tol"]}
    lo, hi = F["l4_v"], V_CLAMP                                      # the pack voltage from which the printed r1 bound keeps the guard closed
    for _ in range(60):
        mid = (lo + hi) / 2.0
        lo, hi = (mid, hi) if rt_on(mid) < g["r1"] else (lo, mid)
    F["v_print"] = hi
    F["notrip10_print_low"] = g["r1"] <= F["on"][F["l4_v"]] and F["tj10"] <= g["t1"]
    F["notrip10_print_high"] = g["r1"] <= F["on"][W["vmax"]] and F["tj10"] <= g["t1"]
    F["notrip18_print"] = F["tj18"] <= g["t1"] and g["r1"] <= F["on"][F["l4_v"]]
    # the typical curve (3.2, INFERRED), the PTC taken at the junction's reading (the copper is cooler: the side judged is the hot one)
    F["typ10"], F["typ18"] = typ_ratio(F["tj10"]), typ_ratio(F["tj18"])
    F["typ18_cu"] = typ_ratio(F["cu18"])
    F["r10_typ"] = F["typ10"] * r25_hi
    F["r18_typ"] = (F["typ18"] * r25_lo, F["typ18"] * g["r25"], F["typ18"] * r25_hi)
    F["r18_typ_cu_lo"] = F["typ18_cu"] * r25_lo
    F["onset"] = {lab: typ_temp(F["on"][F["l4_v"]] / r) for lab, r in (("most", r25_hi), ("nominal", g["r25"]), ("least", r25_lo))}
    F["r25_max_16v8"] = F["on"][W["vmax"]] / F["typ18"]
    F["win_typ"] = PRF_TOP_M20 * r25_hi
    F["low_typ"] = PRF_LOWEST * r25_lo
    F["curve_x10"], F["curve_x100"] = typ_temp(10.0), typ_temp(100.0)
    F["curve_at_r2"] = typ_ratio(F["print"]["over_r2_from"])           # the curve where the 10 kOhm part prints at least 4.7 MOhm
    F["print_at_r2"] = g["r2"] / r25_hi                                # that point as a ratio, with R25 at its printed most
    rise = F["tj18"] - F["tj10"]
    F["tau_need"] = {lab: -60.0 / math.log(1.0 - (t - F["tj10"]) / rise) for lab, t in F["onset"].items() if t < F["tj18"]}
    F["f07_typ_10"] = F["r10_typ"] < F["on"][F["l4_v"]] and F["r10_typ"] < F["window"]
    F["f07_typ_18"] = F["r18_typ"][0] < F["on"][F["l4_v"]]
    # the alternative parts (named, not selected)
    b = P["PRF15BA102RB6RC"]
    F["ba102_notrip"] = F["tj18"] <= b["t1"] - b["t1_tol"] and b["r1"] <= F["on"][F["l4_v"]]
    F["ba102_trip"] = b["r2"] >= F["off"][W["vmax"]]
    F["ba102_low"] = b["r25"] * (1 - b["tol"]) >= F["low"][R["v_run"]]
    # V2-m5: the junction over the sensor's copper on the guard's trip side, with L4-E11's worst split (its round 11; 22h)
    F["p_worst"] = float(need(l22h, r"one\s+FET\s+heated\s+alone\s+at\s+the\s+worst\s+split's\s+%s\s+W" % N, "L4-E11 22h: the worst split's loss").group(1))
    F["rth_jmb"] = float(need(page, r"A\s+junction\s+leads\s+its\s+copper\s+by\s+[0-9.]+\s+K\s+at\s+23\.93\s+A\s+\(Rth\(j-mb\)\s+%s\s+K/W\)" % N, "l9stk 15.5: Rth(j-mb)").group(1))
    F["p_even"] = float(need(page, r"\|\s+three,\s+\(Zself\s+\+\s+2\s+Zmut\)\s+\|\s+%s\s+W\s+\|" % N, "l9stk 15.5: the even split's loss a FET").group(1))
    if abs(F["rth_jmb"] * F["p_even"] - F["lead24"]) > 0.006 or abs(F["p_worst"] / F["p_even"] - 9.0 / 8.0) > 0.001:
        refuse("the even split's lead (%.2f K) or the worst split's 9/8 no longer follow from the copies" % F["lead24"])
    F["lead_worst"] = F["rth_jmb"] * F["p_worst"]                      # the hottest junction over ITS OWN mounting base
    F["trip_tj_worst"] = F["print"]["over_r2_from"] + F["lead_worst"]  # with the mounting base taken at the sensor's copper: NOT BOUNDED
    F["trip_room"] = 150.0 - F["trip_tj_worst"]                        # what is left for the mounting base over the sensor's copper
    F["trip_print"] = g["r2"] >= F["off"][W["vmax"]]                   # the resistance side alone is printed; the junction's reading is not bounded
    # TDK's B59721A0130A062: the loop's scale k (tdk_window: the sure-off is a LOWER bound; the check V2's V2-B3)
    T5 = TDK_B59721
    F["tdk_k_notrip"] = F["on"][F["l4_v"]] / T5["r_m5"]
    F["tdk_k_trip"] = F["off"][W["vmax"]] / T5["r_p15"]
    F["tdk_k_low"] = {v: F["low"][v] / (T5["rr"] * (1 - T5["drr"])) for v in F["low"]}
    F["tdk_win"] = {v: tdk_window(F["tdk_k_low"][v], F["tdk_k_trip"], F["tdk_k_notrip"]) for v in F["low"]}
    F["tdk_fits"] = {v: lo_ <= hi_ for v, (lo_, hi_) in F["tdk_win"].items()}
    F["tdk_width"] = {v: hi_ / lo_ - 1.0 for v, (lo_, hi_) in F["tdk_win"].items()}
    k_all = sorted({k_ for v in F["tdk_win"] if F["tdk_fits"][v] for k_ in F["tdk_win"][v]})
    p_at = lambda k_: (W["vmax"] / ((32e3 / k_) + T5["r_m5"])) ** 2 * T5["r_m5"]
    i_at = lambda k_: W["vmax"] / (32e3 / k_ + T5["rr"] * (1 - T5["drr"]))
    F["tdk_k_span"] = (k_all[0], k_all[-1]) if k_all else None
    F["tdk_p"] = (p_at(k_all[0]), p_at(k_all[-1])) if k_all else None        # in the part at its printed R(Tsense - 5 C), the pack at its most
    F["tdk_static"] = (i_at(k_all[0]), i_at(k_all[-1])) if k_all else None   # the loop's draw with the part at its least R25
    # TDK's own reference table (p.29, typical): the part's least resistance is not at 25 C
    F["tdk_k_low_ref"] = {v: F["low"][v] / T5["rmin_ref"] for v in F["low"]}
    F["tdk_fits_ref"] = {v: max(F["tdk_k_low_ref"][v], F["tdk_k_trip"]) <= F["tdk_k_notrip"] for v in F["low"]}
    F["tdk_trip_tj"] = 130 + 15 + F["lead_worst"]
    return F


def rel(p):
    return os.path.relpath(p, ROOT)


def sha(p, n=16):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:n]


def refuse(msg):
    sys.stderr.write("l8p_drafts: REFUSED: %s\n" % msg)
    sys.exit(2)


def draft(rec, name, board):
    return REPLACED.get((rec, name, board)) or os.path.join(RECS, rec, "apply_gen_sch_%s_%s.py" % (board, name))


def run(script, target, board):
    """(returncode, the last line it printed): d8dec31's drafts take the committed netlist, the others --write."""
    args = [script, target, NET[board]] if "/d8dec31/" in script.replace(os.sep, "/") else [script, target, "--write"]
    r = subprocess.run([sys.executable, "-B"] + args, capture_output=True)
    out = (r.stdout.decode("utf-8", "replace").strip().splitlines() or [""])[-1] if r.returncode == 0 else \
        (r.stderr.decode("utf-8", "replace").strip().splitlines() or [""])[-1]
    return r.returncode, out


def scrub(s, d):
    return s.replace(d, "<scratch>")


def compose(board, seq, d, tag):
    p = os.path.join(d, tag + "_gen_sch_%s.py" % board)
    shutil.copy(GEN[board], p)
    res = []
    for s in seq:
        rc, msg = run(s, p, board)
        name = os.path.relpath(s, RECS)
        res.append((name, "OK" + (" (%s)" % msg if "/d8dec31/" in s.replace(os.sep, "/") and "mainpb" in s else "") if rc == 0 else "REFUSED (%s)" % scrub(msg, d)))
        if rc:
            break
    return p, res


STMT = re.compile(r'^\s*(ic|part|c|r|tp|nfet|vh2|synth|q|esd|efuse|pfet5|ph|_tvs)\(\s*"([A-Z#][A-Z0-9_]*)"')
TOKEN = re.compile(r"\b(RT\d{1,3}|[RCDLQUHF]\d{1,3}|J_[A-Z0-9]+|TP\d{1,3}|W_[A-Z0-9]+)\b(?!-)")


def strip_comments(s):
    return "\n".join("" if l.lstrip().startswith("#") else l.split("#")[0] for l in s.splitlines())


def literal_calls(text):
    out = []
    for line in strip_comments(text).splitlines():
        for stmt in line.split(";"):
            m = STMT.match(stmt)
            if m:
                out.append(m.groups())
    return out


def tokens(text):
    """Designator strings where the generator DRAWS or LISTS a part: a call's first argument, or an element of a list or tuple,
    read with ast; prose and dict keys count for nothing."""
    out = set()
    for n in ast.walk(ast.parse(text)):
        cands = []
        if isinstance(n, ast.Call) and n.args:
            cands.append(n.args[0])
        elif isinstance(n, (ast.List, ast.Tuple)):
            cands.extend(n.elts)
        for c in cands:
            if isinstance(c, ast.Constant) and isinstance(c.value, str) and TOKEN.fullmatch(c.value):
                out.add(c.value)
    return out


def declared_adds(script):
    import importlib.util
    try:
        sp = importlib.util.spec_from_file_location("adds_" + re.sub(r"\W", "_", script), script)
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        return set(getattr(m, "ADDS", ()))
    except Exception:
        return set()


def added(before, after, script):
    cb = {r for _h, r in literal_calls(before)}; ca = {r for _h, r in literal_calls(after)}
    return (ca - cb) | (tokens(after) - tokens(before)) | declared_adds(script)


def _draws(node):
    """{designator: count} of the literal part calls under an ast node; the two branches of an `if _tvs:` (the generators' one
    clamp drawn either by kisch.tvs or by its fallback) are alternatives, so a designator counts once across them."""
    from collections import Counter
    if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "_tvs":
        a, b = Counter(), Counter()
        for x in node.body:
            a += _draws(x)
        for x in node.orelse:
            b += _draws(x)
        return a | b
    c = Counter()
    if isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
        f = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
        if f in ("ic", "part", "c", "r", "tp", "nfet", "pfet5", "ph", "q", "esd", "efuse", "synth", "vh2", "_tvs", "tvs") and TOKEN.fullmatch(node.args[0].value):
            c[node.args[0].value] += 1
    for ch in ast.iter_child_nodes(node):
        c += _draws(ch)
    return c


def duplicates(text):
    return sorted(r for r, n in _draws(ast.parse(text)).items() if n > 1)


def pins_of(nl):
    return {(r, p): n for r, d in nl["pins"].items() for p, n in d.items()}


def netlist_text(board, generator, d, tag):
    """(rc, netlist path or the generator's last line, table)."""
    out = os.path.join(d, "%s_%s.net" % (tag, board))
    rc, log, table = GN.run(generator, out, PROJECT[board])
    if rc:
        return rc, scrub((log.strip().splitlines() or [""])[-1], d), None
    return 0, out, table


def mutate_ops(path, d, tag, ops):
    """A copy of a netlist with the edits ops, each one of: ("move", ref, pin, net) the node to another net (made if absent);
    ("repin", ref, pin, new_pin) the node's pin number; ("value", ref, value) a component's value; ("drop", ref) a component with
    every node of it. Round 8: the guard's mutations (L9S5-F1) are no exchanges of two nodes."""
    lines = open(path, encoding="utf-8").read().split("\n")

    def node(ref, pin):
        return ' (node (ref "%s") (pin "%s"))' % (ref, pin)
    for op in ops:
        if op[0] == "move":
            _k, ref, pin, net = op
            hit = [i for i, l in enumerate(lines) if node(ref, pin) in l]
            if len(hit) != 1:
                refuse("mutation: %s.%s is not on one net" % (ref, pin))
            lines[hit[0]] = lines[hit[0]].replace(node(ref, pin), "")
            tgt = [i for i, l in enumerate(lines) if '(name "%s")' % net in l or '(name "/%s")' % net in l]
            if tgt:
                lines[tgt[0]] = lines[tgt[0]][:-1] + node(ref, pin) + ")"
            else:
                k = max(i for i, l in enumerate(lines) if l.startswith("    (net "))
                lines.insert(k + 1, '    (net (code "9999") (name "/%s")%s)' % (net, node(ref, pin)))
        elif op[0] == "repin":
            _k, ref, pin, new = op
            hit = [i for i, l in enumerate(lines) if node(ref, pin) in l]
            if len(hit) != 1:
                refuse("mutation: %s.%s is not on one net" % (ref, pin))
            lines[hit[0]] = lines[hit[0]].replace(node(ref, pin), node(ref, new))
        elif op[0] == "value":
            _k, ref, value = op
            hit = [i for i, l in enumerate(lines) if l.startswith('    (comp (ref "%s") (value ' % ref)]
            if len(hit) != 1:
                refuse("mutation: component %s is not listed once" % ref)
            lines[hit[0]] = re.sub(r'\(value "(?:[^"\\]|\\.)*"\)', '(value "%s")' % value, lines[hit[0]], count=1)
        elif op[0] == "drop":
            _k, ref = op
            n0 = len(lines)
            lines = [l for l in lines if not l.startswith('    (comp (ref "%s") ' % ref)]
            if len(lines) != n0 - 1:
                refuse("mutation: component %s is not listed once" % ref)
            lines = [re.sub(r' \(node \(ref "%s"\) \(pin "[^"]*"\)\)' % re.escape(ref), "", l) for l in lines]
        else:
            refuse("mutation: unknown edit %r" % (op,))
    q = os.path.join(d, tag + ".net")
    open(q, "w", encoding="utf-8").write("\n".join(lines))
    return q


# The seven mutations record l9stk's round 5 names for the guard's draft (L9S5-F1; its page 15.9 (b)), each on the composed board A
GUARD_MUTATIONS = (
    ("the shunt on DOCK_EN_OUT", [("move", "Q60", "3", "DOCK_EN_OUT")]),
    ("the open-drain output used", [("repin", "U60", "5", "3")]),
    ("the regulator fed from VBAT", [("move", "U61", "1", "VBAT")]),
    ("the pair's sum outside 3.574 to 25.8 kOhm (two 15 kOhm)", [("value", "R260", "15k 1%"), ("value", "R261", "15k 1%")]),
    ("one resistor in place of the pair (R260 at 15 kOhm from DOCK_EN_OUT to DOCK_EN_RET, R261 gone)",
     [("drop", "R261"), ("move", "R260", "2", "DOCK_EN_RET"), ("value", "R260", "15k 1%")]),
    ("the shunt drawn as an AO3400A", [("value", "Q60", "AO3400A: THG_G high = the thermal guard tripped, DOCK_EN_RET held low (1 G, 2 S, 3 D)")]),
    ("the gate capacitor removed", [("drop", "C260")]),
)


def mutate(path, d, tag, swaps):
    """A copy of a netlist with the nets of two (ref, pin) nodes exchanged."""
    raw = open(path, encoding="utf-8").read()
    for (ra, pa), (rb, pb) in swaps:
        a = '(node (ref "%s") (pin "%s"))' % (ra, pa); b = '(node (ref "%s") (pin "%s"))' % (rb, pb)
        if raw.count(a) != 1 or raw.count(b) != 1:
            refuse("the mutation's nodes are not in the netlist once: %s %s" % (a, b))
        raw = raw.replace(a, "\0A").replace(b, a).replace("\0A", b)
    p = os.path.join(d, tag + ".net")
    open(p, "w", encoding="utf-8").write(raw)
    return p


def main():
    w = sys.stdout.write
    w("l8p_drafts: Layer 8 record l8p, W4DP-F2's breaker, its make-last dock enable loop and its restart inhibit drafted for boards P, E and A (MESHSAT-1357)\n")
    w("prototype design; nothing built, bought or measured; nothing applied to the tree; the values are record l9stk's (fnd/l9stk at 0d72880b)\n\n")
    # 1. inputs
    others = [draft(r, n, b) for b in "pea" for r, n in ORDER[b]] + [draft(r, n, b) for b in "pea" for r, n in TREE_ONLY.get(b, ())] \
        + [f for b in "pea" for f, _a in FOLLOW.get(b, ())]
    inputs = [GEN["p"], GEN["e"], GEN["a"], os.path.join(TOOLS, "kisch.py"), os.path.join(TOOLS, "intent.py"), os.path.join(TOOLS, "idc_pads.py")]
    inputs += others + [NET["p"], NET["e"], NET["a"]]
    inputs += [os.path.join(HERE, f) for f in sorted(SOURCES_SHA)] + [os.path.join(HERE, "inputs", "SOURCES.txt")]
    inputs += [os.path.join(CHK.PRETTY, l + ".kicad_mod") for l in sorted(set(CHK.LANDS.values()) | {"LeadLands_1x02"})]
    inputs += [LM5069_SHEET, NTC_SHEET, D4148_SHEET, OPA187, CSD_SHEET, N7002_SHEET, BZT_SHEET, TRM_SHEET, BQ4050_SHEET, CSD17570_SHEET, LM74700_SHEET,
               PRF_SHEET, os.path.join(HERE, "fetch_held_back.py"), os.path.join(HERE, "read_prf_typical.py")]
    inputs += [MINE["p"]] + MINE2["p"] + [MINE["e"], MINE["a"]] + MINE_AFTER["a"] + [os.path.join(HERE, "check_l8p_netlist.py"), os.path.join(HERE, "gen_netlist.py")]
    inputs += [os.path.join(ROOT, t) for t, _h, _held in PT.inputs(ROOT, PDFTEXT)]
    w("1. INPUTS, pinned by sha256\n")
    for p in inputs:
        if not os.path.isfile(p):
            refuse("input %s is missing%s" % (rel(p), " (TI's held sheet: python3 v2/docs/records/l8p/fetch_held_back.py)" if p == OPA187 else ""))
        w("   %s %s\n" % (sha(p), rel(p)))
    for f, full in sorted(SOURCES_SHA.items()):
        if sha(os.path.join(HERE, f), 64) != full:
            refuse("the copy %s is not the file SOURCES.txt pins" % f)
    w("   record l9stk's, L4-E7's and L4-E11's copies (rounds 9 and %d) equal the sha256 SOURCES.txt pins: yes\n\n" % L4E11_ROUND)
    # 2. the values
    texts = {k: open(os.path.join(HERE, v), encoding="utf-8").read() for k, v in INPUT_FILES.items()}
    w("2. THE VALUES, each found in record l9stk's own text (fnd/l9stk at 0d72880b), and this record's SESSION choices\n")
    for b, ref, pre, src, pat, key in CHK.VALUES:
        if not re.search(CHK.phrase_rx(pat), texts[key]):
            refuse("record l9stk no longer reads the %s value (%s)" % (ref, src))
        w("   %s %-5s %-16s l9stk %s\n" % (b.upper(), ref, pre, src))
    for pat, what in (("**IF-6** the gauge's PACK and VCC taps stay on Q2's source node, and the clamp and the controller return to PACK_N", "IF-6"),
                      ("OVLO to ground", "the controller row: OVLO to ground"),
                      ("SELECTED: the -1 (latch-off).", "15.4b: the -1, latch-off, selected"),
                      ("a ground contact between them in J_SMB and on the block", "condition C2: the ground between, in J_SMB and on the block"),
                      ("crosses the dock on two contacts 1 mm short of the power pins", "C-1b: two contacts 1 mm short (Layer 7's)"),
                      ("makes that **0.110 to 0.907 s after the enable mates**", "C-1b: the hold, 0.110 to 0.907 s"),
                      ("**0.41 ms in all**", "C-1b: the undocking, 0.41 ms"),
                      ("**C-1c SELECTED: a restart inhibit on the breaker pad**", "15.4b: C-1c selected"),
                      ("It is gated so that it acts only while PGD is low", "C-1c: gated by PGD"),
                      ("its designator L4-E11's", "15.5: the third battery FET's designator is L4-E11's"),
                      ("In the enable loop on the battery FETs' copper", "15.5: the PTC on the battery FETs' copper (board A)")):
        if not re.search(CHK.phrase_rx(pat), texts["page"]):
            refuse("record l9stk no longer reads %s" % what)
        w("   l9stk reads: %s\n" % what)
    if not re.search(r"R_E1, R_E2 = 10e3, 22e3", texts["constants"]) or not re.search(r"R_DIS = 150\.0", texts["constants"]) \
            or not re.search(r"R_U = 200e3", texts["constants"]):
        refuse("l9stk_protection.py's constants no longer read R_E1, R_E2, R_DIS and R_U as the page states them")
    w("   l9stk_protection.py's constants agree with the page: R_E1 10 kOhm, R_E2 22 kOhm, R_DIS 150 ohm, R_U 200 kOhm; R_G 1 MOhm\n")
    for k, v in SESSION:
        w("   SESSION %-15s %s\n" % (k, v))
    w("\n")
    # 3. C-1c's budget
    B = budget(texts["page"])
    w("3. C-1c'S BUDGET (DD-8): the window from l9stk 15.4b, the NTC from Murata's sheet, the comparator from TI's held OPA187 sheet (SBOS807E)\n")
    w("   the window: allow from %.2f C, block from %.2f C, trip %.2f C +-%.2f K with the NTC at %.0f ohm; the NTC's +-%.2f K and +-%.2f K left: %s\n" % (
        B["allow"], B["block"], B["trip"], B["half"], B["r_trip"], B["ntc_k"], B["rest"], "consistent" if B["window_ok"] else "INCONSISTENT"))
    w("   the NTC (Murata NXRT15XH103FA1B010): R25 %.0f ohm, B25/85 %.0f K printed as a reference value, %.2f mA at most, %.1f mW/K, 10 mm leads;\n" % (
        B["r25"], B["b85"], B["imax"] * 1e3, B["delta"] * 1e3))
    w("     its tolerance at 80 C (the record's +-%.2f K) is ASSUMED from the product search sheet: to be confirmed by Murata's approval sheet or E-15\n" % B["ntc_k"])
    w("   the bridge at the trip: R110 %.0f kOhm over the NTC, %.4f V at the pack's least %.1f V, %.3f mV/K there (B/T^2 %.5f per K); %.3f mA at %.1f V\n" % (
        R_BRIDGE / 1e3, B["vn"], B["vmin"], B["slope"] * 1e3, B["sens"], B["i_bridge"] * 1e3, B["vmax"]))
    w("   the reference: R111 %.0f kOhm over R112 %.2f kOhm with R113 %.0f MOhm at the output low: %.2f ohm against %.0f (%+.3f K); hysteresis %.3f K nominal, %.3f K at most\n" % (
        R_REF_T / 1e3, R_REF_B / 1e3, R_HYST / 1e6, B["x_low"], B["r_trip"], B["k_nominal"], B["hyst_nom"], B["hyst_max"]))
    w("   the comparator, U102 OPA187 (read, high-voltage table): VOS %.0f uV, drift %.3f uV/K to %.0f C, IB %.1f nA and IOS %.1f nA over temperature, PSRR %.0f uV/V;\n" % (
        B["vos"] * 1e6, B["drift"] * 1e6, B["tj_max_spec"], B["ib"] * 1e9, B["ios"] * 1e9, B["psrr"] * 1e6))
    w("     supply %.1f to %.0f V (absolute %.0f V) against BRK_VIN's %.1f V clamp; input range from 0.1 V under its negative rail; at most %.1f uV in all: %.3f K\n" % (
        B["vs"][0], B["vs"][1], B["vs_abs"], V_CLAMP, B["v_op"] * 1e6, B["k_op"]))
    w("   the bridge and reference resistors: %.1f %% and at most %.0f ppm/K between %.0f and %.1f C, each at %.3f %%, the worst of all signs: %.3f K\n" % (
        R_TOL * 100, R_TCR * 1e6, T_RES[0], T_RES[1], B["res_e"] * 100, B["k_res"]))
    w("   the NTC's own heating at %.3f mA: %.3f K (it reads hot)\n" % (B["i_bridge"] * 1e3, B["k_self"]))
    w("   THE SPLIT OF +-%.2f K: allow side %.3f K used (comparator, resistors, own heating, hysteresis, nominal), %.3f K left for the pad-to-NTC gradient;\n" % (
        B["rest"], B["allow_used"], B["grad_allow"]))
    w("     block side %.3f K used, %.3f K left; the checker's split asked about %.1f K for the gradient, the comparator at most 0.47 K, the hysteresis at most 0.5 K: %s\n" % (
        B["block_used"], B["grad_block"], CHECKER_GRADIENT, "the split closes" if B["closes"] else "THE SPLIT DOES NOT CLOSE"))
    w("   THE LOCKOUT AT THE ALLOW EDGE: a unit tripping at %.2f C needs its pad within %.2f K of the %.2f C inside air before it restarts; at that air the cells' hot stop has already shut the kit down\n" % (
        B["allow"], B["lockout"], B["air"]))
    w("   E-10 gains: VDS under 1.62 V during current-limit excursions (PGD stays high, so the inhibit stays gated)\n\n")
    if not (B["closes"] and B["window_ok"]):
        refuse("C-1c's split does not close or the window is inconsistent")
    # 3b. B-R2's detector
    R = rev_budget(texts["page"], texts["l4e11"], texts["l4e11pre"], B)
    F = round5(texts, B, R)
    w("3b. B-R2, THE CHARGE THROUGH A LATCHED BREAKER (route R1, round 3): task L4-E11 19h and 15c (round 9's; copied at %s), the makers' sheets\n" % L4E11_AT)
    w("   the open case (L4-E11 19h): a latch while a source holds VSYS keeps CELL+ tied to it, %.1f V into the %.3f ohm fault, so the\n" % (R["v_fault"], R["r_fault"]))
    w("     inhibit (CELL+ under %.2f V) sets only for faults under %.0f mOhm; the latched FET at %.4f A (R-b's largest) is held at %.1f C, %.3f A is its\n" % (
        R["alive"], R["reach"], R["i_rb"], R["tj_rb"], R["i_safe"]))
    w("     safe level (150 C held from %.2f C at VSD %.0f V and %.1f C/W); a charge over it rested on the firmware\n" % (R["air"], R["vsd_b"], R["rja_l4"]))
    w("   NO EXISTING ELEMENT TELLS BOARD A (read from the sheets and the drafts):\n")
    w("     PGD switches on VDS alone (SNVS452G pin 8: active when VDS decreases below 1.25 V); a reverse charge makes VDS negative, so PGD reads good\n")
    w("     the -1 has no fault pin: its latch holds GATE low on the %.2f to %.1f mA sink until UVLO or VIN cycles (8.4.3); its GATE to OUT clamp is an\n" % R["isink"])
    w("       internal 12 V zener (8.4.2), and a divider on GATE draws from the %.0f to %.0f uA charge pump that sets l9stk's %.1f ms start (IF-1)\n" % (R["igate"][0], R["igate"][1], R["start"] * 1e3))
    w("     the enable loop's two conductors: board A reads DOCK_EN_OUT and DOCK_EN_RET only, both ratiometric to BRK_VIN through RT1; their ratio is\n")
    for rt in (R["rt1_min"], 47e3, 338e3):
        w("       RT1 %5.0f kOhm: RET/OUT %.4f with R106 in the loop and %.4f with R106 bypassed (a change of the loop's source scales both alike)\n" % (
            rt / 1e3, (22e3 / (10e3 + rt + 22e3)) / ((rt + 22e3) / (10e3 + rt + 22e3)), 22e3 / (rt + 22e3)))
    w("       a changed return resistor is confounded with RT1's own %.0f kOhm to 338 kOhm span, a raised return enables the breaker undocked (Q103 on\n" % (R["rt1_min"] / 1e3))
    w("       with no dock), and only the return held LOW is distinct: Q103 then reads the loop open, Q104 pulls UVLO, the -1 resets\n")
    w("     C-1c's NTC reads the pad, too slow and gated by PGD (high in reverse); the gauge's charge FET Q1 could block a charge, but the owner's\n")
    w("       criterion takes Q1 and Q2 welded\n")
    w("   ROUTE R1 SELECTED: board P detects the charge itself and holds the loop's return low, which J_DOCK pin 3 already carries to board A;\n")
    w("     a reset is harmless exactly then: a charge flows backwards only while the source holds CELL+ above the cells, and board A's inhibit holds\n")
    w("     the battery FETs off through the restart, so the dv/dt start meets CELL_FUSED alone and no forward current\n")
    w("   U103, THE CHARGE INTO THE CELLS on R10 (%.0f mOhm, read from gen_sch_p.py): %.4g A per volt of REV_VZ; REV_VZ is BRK_VIN x %.5f under\n" % (
        R["r10"] * 1e3, R["c"], R["ratio"]))
    w("     D103 (BZT52C12: %.1f to %.1f V at 5 mA, %.1f to %.1f mV/K, under %.1f uA at %.1f V; %.2f V at most at the held %.1f C case)\n" % (
        R["vz"][0], R["vz"][1], R["tcz_min"] * 1e3, R["tcz"] * 1e3, R["ir"] * 1e6, R["vr"], R["vz_hot"], B["case_held"]))
    w("     REV_VZ at least %.2f V wherever BRK_VIN puts it over that (the zener's knee under 1 mA is not printed: its leakage at %.1f V, ten times hot, through R129)\n" % (
        R["vz_low"], R["vr"]))
    w("     tolerances: R118 and R119 %.2f %% together, R129's share %.3f %%, R10 %.2f %% (its %.0f %% and %.0f ppm/K ASSUMED, owed to Layer 6), U103 %.1f uV\n" % (
        R["e_ref"] * 100, R["e_ratio"] * 100, R["e_r10"] * 100, R10_TOL * 100, R10_TCR * 1e6, R["v_op"] * 1e6))
    w("       (VOS, drift to 125 C, IOS through 200 ohm each side, PSRR over %.1f to %.1f V)\n" % (B["vmin"], V_CLAMP))
    for v, lo, hi in R["table_i"]:
        w("     BRK_VIN %5.2f V: the threshold %.3f to %.3f A\n" % (v, lo, hi))
    w("     least %.3f A against the LDO-mode precharge's %.5f A at most (L4-E11 15c), x%.3f; most %.3f A against the latched FET's %.3f A, x%.3f;\n" % (
        R["i_th_min"], R["i_ldo"], R["m_lo"], R["i_th_max"], R["i_safe"], R["m_hi"]))
    w("     the power-on charge %.3f A and R-b's %.4f A pass a running breaker untouched; a charge the detector lets pass holds the FET at %.1f C at most\n" % (
        R["i_por"], R["i_rb"], R["tj_at_max"]))
    w("     the floor: SRN %.1f V (R-b', L4-E11 15c) less VSD %.1f V: BRK_VIN %.2f V, over the OPA187's least supply %.1f V\n" % (
        R["srn_floor"], R["vsd_max"], R["v_floor"], B["vs"][0]))
    w("   U104, THE BODY DIODES CONDUCTING: PACK_P x %.6f against BRK_SNS x %.6f: high when PACK_P exceeds BRK_SNS by %.4f of it;\n" % (
        R122 / (R121 + R122), R124 / (R123 + R124), R["eps"]))
    w("     tolerances: R121 to R124 at %.2f %% and %.0f ppm/K, %.3f %% of BRK_SNS in all; U104 %.0f uV (IOS through %.1f kOhm), %.1f mV referred\n" % (
        TOL_DIV * 100, TCR_DIV * 1e6, R["er"] * 100, R["v_op2"] * 1e6, R["rs"][0] / 1e3, R["v_op2"] * (R121 + R122) / R122 * 1e3))
    for v, lo, hi in R["table_v"]:
        w("     BRK_VIN %5.2f V: the reverse threshold %.4f to %.4f V\n" % (v, lo, hi))
    w("     a running breaker at the pack path's %.2f A charge: %.1f mV (RDS(on) %.2f mOhm at most, x%.1f at 150 C, Figure 8 read, two in parallel)\n" % (
        R["i_lim"], R["v_chan"] * 1e3, R["rds_max"] * 1e3, CSD_RDS_150))
    w("       under the least threshold %.4f V: U104 never reads a running breaker (the charger's own bound is under it: %.0f W over %.1f V, %.1f A)\n" % (
        R["vt_min"], R["p_fe"], R["v_pack_min"], R["i_chg_fe"]))
    w("     the body diodes at the threshold's least current, %.3f A a FET: %.3f V at 125 C and %.3f V at 150 C (Figure 9, typical, read), %.3f V at the\n" % (
        R["i_fet"], R["vsd_125"], R["vsd_150"], R["vsd_case"]))
    w("       held %.1f C case; over the most threshold %.4f V: a charge over U103's threshold always crosses U104's (INFERRED from a typical figure; E-14b)\n" % (
        B["case_held"], R["vt_max"]))
    w("   THE PULL: Q107 and Q108 in series, gates at half of each output: %.1f V at BRK_VIN %.1f V (PORIT, under which the -1 runs nothing) against the\n" % (
        R["gate_run"], R["v_run"]))
    w("     2N7002's %.1f V threshold at most, %.1f V at the %.1f V clamp against its %.0f V; DOCK_EN_RET held at %.3f V at most (2 x %.0f ohm x %.0f, %.2f mA)\n" % (
        R["n_vth"][1], V_CLAMP / 2.0, V_CLAMP, R["n_vgs"], R["v_ret"], R["n_rds"], N7002_HOT, V_CLAMP / (10e3 * (1 - R106_TOL) + R["rt1_min"]) * 1e3))
    l10 = texts["l4e11c"]
    for pat, what in ((r"under \*\*%s V\*\* at least; read closed over %s V at most" % (re.escape("%.4f" % RET_LOW), re.escape("%.2f" % RET_HIGH)), "the return held and closed"),
                      (r"over \*\*%s V\*\* at most" % re.escape("%.3f" % OUT_POWERED), "the loop powered"),
                      (r"why board A reads the return held under %s V and not up to 1\.0 V" % re.escape("%.4f" % RET_LOW), "the box restated"),
                      (r"The 1\.0 V figure is a 2N7002's least threshold \(l8p 12f\)", "the 1.0 V figure's origin")):
        need(l10, pat, "L4-E11 20c at %s: %s" % (L4E11_AT, what))
    m13 = need(l10, r"the\s+closed\s+return\s+reads\s+closed\s+for\s+any\s+RT1\s+under\s+([0-9.]+)\s+kOhm\s+at\s+([0-9.]+)\s+V\s+\(([0-9.]+)\s+V\s+at\s+RT1\s+47\s+kOhm,\s+which\s+bounds\s+nothing:\s+round\s+13,\s+23g\)",
               "L4-E11 20c at %s: the closed return as round 13 restates it" % L4E11_AT)
    need(l10, r"record\s+l9stk's\s+former\s+\"bound\s+point\";\s+\*\*withdrawn\s+as\s+a\s+bound\s+by\s+round\s+13,\s+23g:\*\*\s+47\s+kOhm\s+is\s+not\s+a\s+point\s+of\s+this\s+part",
         "L4-E11 20c at %s: the 47 kOhm bound point withdrawn" % L4E11_AT)
    need(l10, r"Board\s+A\s+reads\s+a\s+closed\s+return\s+as\s+held\s+only\s+past\s+RT1\s+%s\s+kOhm\s+at\s+%s\s+V" % (re.escape(m13.group(1)), re.escape(m13.group(2))),
         "L4-E11 20c at %s: the closed return held only past that resistance" % L4E11_AT)
    w("   WHAT BOARD A READS (L4-E11's DD-7 as it draws it since its round 10: section 20c at %s, U48 TPS37A010122 on TI SNVSBJ1E; L4E11-R10-F1):\n" % L4E11_AT)
    w("     the return held under %.4f V at least (read closed over %.2f V at most) while the loop reads powered, over %.3f V at most;\n" % (
        RET_LOW, RET_HIGH, OUT_POWERED))
    w("     the copy of 20c reads each figure and why the reading is narrower than round 3's 1.0 V box: yes\n")
    w("     20c AS L4-E11's ROUND 13 RESTATES IT ON MURATA'S PRINTED POINTS (its 23g): record l9stk's former 'bound point' (RT1 47 kOhm, the gate at\n")
    w("       %s V) is WITHDRAWN as a bound, 47 kOhm not being a point of this part; the closed return reads closed for any RT1 under %s kOhm at %s V;\n" % (
        m13.group(3), m13.group(1), m13.group(2)))
    w("       every level this record reads of 20c (the held and powered readings, the dead and alive readings, the load on the return, the window,\n")
    w("       the first inverter's band) is unchanged from its round 12\n")
    w("     board P's pull holds the return at %.3f V at most, %.3f V under board A's held reading; with the return held, DOCK_EN_OUT falls to\n" % (
        R["v_ret"], RET_LOW - R["v_ret"]))
    w("     %.2f V at BRK_VIN %.1f V and %.2f V at %.1f V (RT1 at %.0f kOhm, R106 +1 %%, the return taken at 0 V), %.3f V over the powered reading\n" % (
        R["out_run"], R["v_run"], R["out_pack"], R["v_pack_min"], R["rt1_min"] / 1e3, R["out_run"] - OUT_POWERED))
    w("     round 9's Q47 read half of it, %.2f and %.2f V, under the 2N7002's %.1f V (L8P-F04): answered by round 10's U48 on the return itself\n" % (
        R["out_run"] / 2, R["out_pack"] / 2, R["n_vth"][1]))
    w("     the inhibit sets within 1 ms and holds at least %.1f s after the return rises (read closed); the breaker restarts within %.4f s (the hold\n" % (
        STRETCH_MIN, R["t_restart"]))
    w("       %.3f s and the start %.1f ms); the timer re-enables %.1f ms after a latch\n" % (R["hold"], R["start"] * 1e3, R["t_timer"] * 1e3))
    w("     THE DELAYS AS BOARD A DRAWS THEM (L4-E11 20d at %s, quoted): the inhibit set within %.2f ms of the return falling, under the\n" % (L4E11_AT, F["t_set"] * 1e3))
    w("       interface's 1 ms; the charge through the off breaker ends within %.2f ms of passing board P's threshold (board P's pull %.2f ms plus\n" % (
        F["t_end"] * 1e3, R["t_d"] * 1e3))
    w("       board A's set %.2f ms: %s); the hold at least %.3f s after the return rises, %.3f s over the interface's 1.0 s and %.3f s over the\n" % (
        F["t_set"] * 1e3, "the sum agrees" if abs(round(R["t_d"] * 1e3, 2) + F["t_set"] * 1e3 - F["t_end"] * 1e3) < 0.011 else "THE SUM DISAGREES",
        F["hold_min"], F["over_if"], F["over_rs"]))
    w("       breaker's restart (%.4f s, this record's %.4f s: %s)\n" % (F["restart_l4"], R["t_restart"], "the same" if abs(F["restart_l4"] - R["t_restart"]) < 5e-5 else "DIFFERENT"))
    w("   THE DELAYS: U103's filter %.0f us, U104's %.0f us, each to a 10 %% overdrive x%.2f, the OPA187's typical slew and recovery taken ten times\n" % (
        R["tau_i"] * 1e6, R["tau_v"] * 1e6, math.log(1.1 / 0.1)))
    w("     slower: %.2f ms at most to the pull; a charge over the threshold for %.0f ms at the pack path's %.2f A and VSD %.1f V in one FET raises its\n" % (
        R["t_d"] * 1e3, 10, R["i_lim"], R["vsd_max"]))
    w("     junction %.1f K over the case (Figure 1, single pulse, %.2f x %.1f C/W at 10 ms, read)\n" % (R["dT_burst"], CSD_ZTH_10MS, R["rjc"]))
    w("   THE PROTECTOR'S OWN LIMITS: U103 and U104 on BRK_VIN, %.1f to %.0f V (%.0f V absolute) against %.2f to %.1f V; their inputs within (V-) - 0.1 V\n" % (
        B["vs"][0], B["vs"][1], B["vs_abs"], R["v_floor"], V_CLAMP))
    w("     to (V+) - 2 V; it draws %.2f mA from BRK_VIN at %.1f V (two %.0f uA amplifiers, the reference's feed, the dividers): a standby load for\n" % (
        R["i_standby"] * 1e3, B["vmax"], B["iq_max"] * 1e6))
    w("     the battery stream\n")
    w("   B-R2 BY THE CRITERION: %s\n" % ("MEETS ON PAPER (drafted; nothing measured)" if R["ok"] else "DOES NOT CLOSE"))
    w("\n")
    if not R["ok"]:
        refuse("B-R2's detector does not close")
    # 3c. DD-5
    D = dd5_budget(texts["page"], B, R)
    w("3c. DD-5, THE CHARGE SWITCH'S BODY DIODE IN DISCHARGE (round 4): case row C-PROT (l9stk 15.1 at 0d72880b) with CHGIN = 1 above T3, in discharge\n")
    w("   THE DEFECT (l9stk 15.5 to 15.7; BAT-F20): SLUUAQ3A 4.13 trips the inhibit while 'Not charging' and sets XCHG = 1 if FET Options[CHGIN] = 1\n")
    w("     (14.2.1.1: 'Charging and Precharging disabled, FETs off'), so Q1 is off in discharge above T3 and its body diode carries the pack:\n")
    for r_ in D["rows"]:
        w("     %5.2f A: %5.2f W in Q1's diode (VSD %.0f V at most, SLPS471D, printed) against the %.2f W its pad holds from %.2f C: %.1f times\n" % (
            r_["i"], r_["p_before"], D["vsd_max"], D["p_pad"], B["air"], r_["p_before"] / D["p_pad"]))
    w("     record l9stk reads %.1f W at the held current, OVER by %.1f times at 10 A, and %.0f C in its retry table\n" % (D["p_diode_l9"], D["over"], D["tj_retry"]))
    w("   APPROACH (i), THE GAUGE: 'body diode' occurs %d times in SLUUAQ3A and SLUSC67B: no function is printed that turns the charge FET on while\n" % D["body_diode_hits"])
    w("     discharge current flows; CHGIN = 0 ('FET active', the default) is printed, and it removes the inhibit's FET action above T3 (the pack\n")
    w("     ladder's level L4a), leaving the charge start to the charger's obedience and to OTC: a protection reduced, and outside the case row: DROPPED\n")
    w("   APPROACH (ii), A DIODE THAT MAY CARRY THE SERVICE: on Q1's pad (%.0f C/W at most, %.2f W) the forward drop may be %.3f V at 10 A, %.3f V at 18 A\n" % (
        D["rja"], D["p_pad"], D["p_pad"] / 10.0, D["p_pad"] / 18.0))
    w("     and %.3f V at %.2f A; with Q2's loss on the same pour %.4f V at %.2f A; no junction diode prints that (a Schottky's 0.3 to 0.5 V is a\n" % (
        D["p_pad"] / R["i_lim"], R["i_lim"], ((D["tj_max"] - B["air"]) / D["rja"] - D["rows"][2]["p2"]) / R["i_lim"], R["i_lim"]))
    w("     statement of the class, no sheet held, ASSUMPTION), and a pad for it (6 to 10 K/W) does not exist on a 70 x 44 mm board: NOT SELECTED\n")
    w("   APPROACH (iii), SELECTED: an ideal diode beside Q1: Q109 (CSD17570Q5B, Q1's part) under U105 (LM74700-Q1, board E's U3 part), SNOSD17G:\n")
    w("     printed: V(AK REG) %.0f / %.0f / %.0f mV; full conduction above %.0f / %.0f / %.0f mV; reverse blocking at %.0f / %.0f / %.0f mV within %.2f us;\n" % (
        D["vreg"][0] * 1e3, D["vreg"][1] * 1e3, D["vreg"][2] * 1e3, D["vfull"][0] * 1e3, D["vfull"][1] * 1e3, D["vfull"][2] * 1e3,
        D["vrev"][0] * 1e3, D["vrev"][1] * 1e3, D["vrev"][2] * 1e3, D["t_rev"] * 1e6))
    w("       the gate drive %.1f to %.1f V over the anode (the FET's VGS %.0f V, U105's GATE %.0f V); 'ensures zero DC reverse current flow'\n" % (
        D["vcap_on_min"], D["vcap_off_max"], D["vgs_abs"], D["gate_abs"]))
    w("     printed: Q109's RDS(on) %.2f mOhm typical, %.2f at most at VGS 10 V and 25 C; taken x%.1f hot as l9stk takes it (ASSUMPTION, E-8): %.4f mOhm;\n" % (
        D["rds_typ"] * 1e3, D["rds_max"] * 1e3, D["k_hot"], D["r_hot"] * 1e3))
    w("       the part's own Figure 8 reads x%.2f at 150 C (typical, read by eye, INFERRED); RthJA %.0f C/W at most on 1 in2 of 2 oz, %.0f typical\n" % (
        CSD17570_RDS_150, D["rja"], D["rja_typ"]))
    w("     model: Q109's loss is I x max(the regulated drop, I x RDS(on) hot); the regulated drop at most %.0f mV plus %.2f mV for R130 and the gate's\n" % (
        D["vreg"][2] * 1e3, D["v_leak"] * 1e3))
    w("       leakage through the error amplifier (%.0f uA/V at least): %.2f mV\n" % (D["gm_min"] * 1e6, D["v_reg_max"] * 1e3))
    w("   THE ACCEPTANCE ON C-PROT WITH CHGIN = 1 (from %.2f C; Q109 and Q2 on the SW pour, both losses through one pad of %.0f C/W, l9stk's bound):\n" % (B["air"], D["rja"]))
    for r_, lab in zip(D["rows"], ("10 A held", "18 A for 60 s (taken as held)", "the breaker's %.2f A held" % R["i_lim"])):
        w("     %-30s Q109 %.2f mV, %.3f W (was %.2f W); Q2 %.3f W; TJ %.1f C on its own pad, %.1f C with both through one pad, against %.0f C\n" % (
            lab + ":", r_["vak"] * 1e3, r_["p109"], r_["p_before"], r_["p2"], r_["tj_own"], r_["tj_one"], D["tj_max"]))
    w("     the installed path this asks: %.1f K/W or better for the hottest junction with both losses counted (E-8, restated with Q109)\n" % D["rth_need"])
    w("     THE JOINT CASE (the check V2's V2-m8): at %.2f A held the board dissipates %.2f W in all (%s);\n" % (
        R["i_lim"], D["p_joint"], ", ".join("%s %.3f" % x for x in D["joint"])))
    w("       the sheet's %.0f C/W is one device on 1 in2 of 2 oz on a 1.5 in x 1.5 in board, and IF-2 takes two more such pads for the breaker FETs:\n" % D["rja"])
    w("       three test boards are %.2f in2, board P is %.2f in2 a face, and it carries R10 and the sense pair too: the pads' figures cannot all be the\n" % (
        D["pads_in2"], D["board_in2"]))
    w("       sheet's at once without another heat path (the leads, the bottom face); E-8's specimen carries the current through every part and so\n")
    w("       measures the joint case\n")
    w("     on the typical basis (RDS(on) %.2f mOhm x%.2f, the regulation's %.0f mV, %.0f C/W): %.1f C at %.2f A held\n" % (
        D["rds_typ"] * 1e3, CSD17570_RDS_150, D["vreg"][1] * 1e3, D["rja_typ"], D["tj_typ"], R["i_lim"]))
    w("     at the breaker's largest threshold %.2f A until it clears (%.3f ms): %.2f W in Q109, its junction at most %.1f K over its case (RthJC %.1f C/W)\n" % (
        D["i_cb"], D["t_clear"] * 1e3, D["p_cb"], D["dt_cb"], D["rjc"]))
    w("     with Q1 on (below T3) the two share, and the pair's loss is at most Q1's alone, l9stk's %.3f W at %.2f A: no row of l9stk 15.5 is worsened\n" % (D["p_enh"], R["i_lim"]))
    w("   IF THE REGULATION DID NOT SETTLE (not a printed guarantee with a FET under TI's window): the drop is bounded by the full conduction threshold,\n")
    for r_ in D["rows"]:
        w("     %5.2f A: at most %.3f W in Q109, %.1f C with both through one pad%s\n" % (r_["i"], r_["p_hunt"], r_["tj_hunt"], "" if r_["tj_hunt"] <= D["tj_max"] else ": OVER at %.0f C/W, so this row rests on E-16" % D["rja"]))
    w("     THE LAYOUT'S TARGET: %.1f K/W or better for the SW pour with both losses counted makes the %.2f A row hold on that bound too (the bottom face is free)\n" % (
        D["rth_robust"], R["i_lim"]))
    w("     TI's guideline (10.1.1.2.2): RDS(on) between 20 mV and 50 mV over the nominal current: " + "; ".join(
        "%.2f to %.2f mOhm at %.2f A" % (lo * 1e3, hi * 1e3, i) for i, lo, hi in D["win"]) + ";\n")
    w("       Q109's %.2f to %.2f mOhm is under it at 10 A (U105 then holds it in regulated conduction, its light-load mode), at its edge above 18 A; a FET\n" % (
        D["rds_typ"] * 1e3, D["r_hot"] * 1e3))
    w("       inside the window at 10 A (2 mOhm) would dissipate %.2f W at %.2f A hot, over the pad\n" % (D["p_window_fet"], R["i_lim"]))
    w("   DELAYS: U105 drives %.2f ms at most after EN (ENTDLY %.0f us, C111 +%.0f %% to %.1f V at %.0f uA), against the breaker's hold of %.3f s at least before\n" % (
        D["t_drv_en"] * 1e3, D["entdly"] * 1e6, C111_TOL * 100, D["uvlor_max"], D["i_pump_min"] * 1e6, D["hold_min"]))
    w("       any load; Q1 turned off under load: the gate is up within %.1f us (%.1f us and %.0f nC at %.0f mA; the charge a model), the body diodes carrying\n" % (
        D["t_on"] * 1e6, D["t_fwd"] * 1e6, D["qg_full"] * 1e9, D["i_src_min"] * 1e3))
    w("       the current meanwhile at %.1f K over the case at most (VSD x RthJC); C111 at least %.3f uF derated (-%.0f %%, and -%.0f %% for its bias, ASSUMED)\n" % (
        D["dt_diode"], D["c111_min"] * 1e6, C111_TOL * 100, C111_BIAS * 100))
    w("       against ten times Ciss, %.3f uF; VCAP falls %.2f V as the gate connects, from %.1f V at least to %.2f V, over its %.1f V lockout\n" % (
        10 * D["ciss_max"] * 1e6, D["droop"], D["vcap_on_min"], D["vcap_on_min"] - D["droop"], D["uvlof_max"]))
    w("   THE CHARGE BLOCKING, unchanged: the gauge's drive of Q1 is not touched; Q109 off in reverse (Q1's and Q109's IDSS, U105's cathode %.1f uA to ground);\n" % (D["i_cath"] * 1e6))
    w("       a reversal faster than the regulation follows is ended by the comparator within %.2f us from %.1f A (typical RDS(on), no minimum printed) or,\n" % (
        D["t_rev"] * 1e6, D["i_rev_fast"]))
    w("       under it, by the regulation's sink (%.0f uA at least): %.1f ms and %.2f C at board A's largest %.1f A, a model; Q109 welded reads as a welded Q1\n" % (
        D["i_sink"][0] * 1e6, D["t_rev_slow"] * 1e3, D["q_rev"], R["i_chg_fe"]))
    w("       (SLUUAQ3A 3.10, CFETF)\n")
    w("   EN AND THE STANDBY: EN on from BRK_VIN %.2f V (EN high %.1f V at most, D104 %.3f V at 1 mA), off under %.1f V; U105 %.0f uA typical, %.0f at most,\n" % (
        D["en_on"], D["en_ih_max"], D["vf_d"], D["en_il_min"], D["iq"][0] * 1e6, D["iq"][1] * 1e6))
    w("       %.0f uA with R131 and EN at %.1f V while the gauge holds the discharge FET on; %.1f uA at most with the gauge shut down (U105 %.1f, Q109's IDSS 1)\n" % (
        D["i_run"] * 1e6, B["vmax"], D["i_off"] * 1e6, D["i_shdn"] * 1e6))
    w("   DD-5 BY THE CASE ROW: %s\n" % ("CORRECTED IN THE DRAFT (the acceptance holds on printed limits; E-8, E-16 and E-12d stay open; nothing measured)" if D["ok"] else "DOES NOT CLOSE"))
    w("\n")
    if not D["ok"]:
        refuse("DD-5's correction does not close on its case row")
    # 3d. round 5: L8P-F06 and L8P-F07
    g = F["prf"]["PRF15BB103RB6RC"]
    w("3d. ROUNDS 5 AND 6, THE CHECKS V1 AND V2: L8P-F06 (the breaker FETs' hot off leakage) and L8P-F07 (the guard RT1's printed points)\n")
    w("   L8P-F06, ON L4-E11's LATCH AS ITS ROUND 12 STATES IT (copied at its round %d, fnd/l4e11r11 at %s, where sections 20e, 22b, 22c and 22g are\n" % (L4E11_ROUND, L4E11_AT))
    w("     unchanged; the check V2's V2-B1 and V2-B2):\n")
    w("     TWO limits on the sources into CELL+ while the inhibit holds and the breaker is off (quoted): the static limit %.3f mA (the latch reads\n" % (F["i_static"] * 1e3))
    w("       dead) and the timing limit %.1f uA (the bleed of CELL+ through R256 ends inside the hold's least %.3f s); between the two the hold may end\n" % (
        F["i_timing"] * 1e6, F["hold_min"]))
    w("       with CELL+ still read alive and the breaker off (L4-E11 22g)\n")
    w("     reproduced here from its printed inputs (R256 %.1f kOhm +%.0f %%, CELL_FUSED %.0f uF +%.0f %% ASSUMED by L4-E11, from %.3f V to the dead reading\n" % (
        F["r256"] / 1e3, F["r256_tol"] * 100, F["c_fused"] * 1e6, F["c_tol"] * 100, F["v0"]))
    w("       %.3f V, the foot %.3f V, the sources lifting the level it falls towards): static %.1f uA, timing %.1f uA (L4-E11 prints %.1f), the bleed\n" % (
        F["v_dead"], F["v_foot"], F["i_static_re"] * 1e6, F["i_timing_re"] * 1e6, F["i_timing"] * 1e6))
    w("       %.3f s at its hot bound (it prints %.3f s) and %.3f s with no source\n" % (F["bleed_hot_re"], F["bleed_hot"], F["bleed_none_re"]))
    w("     its source list (22b, quoted): the LM5069's internal %.0f MOhm %.1f uA at %.1f V (%.1f uA at the %.1f V clamp; MAKER value, the tolerance not\n" % (
        R["r_so"] / 1e6, F["i_so"][B["vmax"]] * 1e6, B["vmax"], F["i_so"][V_CLAMP] * 1e6, V_CLAMP))
    w("       printed); the three battery FETs %.0f uA at 25 C and %.0f uA at Tj 125 C (Nexperia BUK6Y10-30P, 17 April 2020, Table 7 p.6, printed maxima\n" % (
        F["bat25"] * 1e6, F["bat125"] * 1e6))
    w("       as L4-E11 and the check V2 read them; that sheet is held back and not read by this record); the breaker pair Q101 and Q102, this finding\n")
    w("     the breaker pair is a source because, with the breaker off, BRK_SNS sits at BRK_VIN and PACK_P at CELL+: each FET's drain-to-source off\n")
    w("       leakage flows into PACK_P and CELL+\n")
    w("     printed (TI SLPS632, March 2017, 5.1, TA = 25 C unless stated): IDSS %.0f uA at most at VGS 0 V and VDS %.0f V (against the %.1f V clamp);\n" % (
        F["idss"] * 1e6, F["idss_v"], V_CLAMP))
    w("       %d IDSS row, no hot figure\n" % F["idss_rows"])
    w("     ASSUMPTION, the leakage doubling every %.0f K from the 25 C row (L4-E11 20d's convention for Q51): the pair %.1f uA at the %.2f C air, %.1f uA\n" % (
        IDSS_DOUBLING, F["pair_air"] * 1e6, F["t_air"], F["pair_case"] * 1e6))
    w("       at the held %.1f C case (l9stk 15.4), %.3f mA at TI's 125 C; the sources at the hot bound %.1f uA (L4-E11's %.1f uA: the same)\n" % (
        F["t_case"], F["pair_125"] * 1e3, F["hot_bound_re"] * 1e6, F["hot_bound"] * 1e6))
    w("     AGAINST THE TIMING LIMIT (the pack at %.1f V, L4-E11's basis): it leaves the pair %.1f uA, %.2f uA a breaker FET; at the held case the pair's\n" % (
        B["vmax"], F["room_timing"][B["vmax"]] * 1e6, F["room_timing"][B["vmax"]] * 1e6 / 2.0))
    w("       %.1f uA leaves %.1f uA in hand and %.1f uA a battery FET (Nexperia prints %.0f uA each at 125 C); the pair alone fills it from a %.1f C\n" % (
        F["pair_case"] * 1e6, F["left_timing"][B["vmax"]] * 1e6, F["each_left_timing"] * 1e6, F["bat125"] / 3.0 * 1e6, F["t_fill_timing"][B["vmax"]]))
    w("       case, %.1f K over the held case, or at the held case if the leakage doubles every %.2f K or faster; at the assumed %.1f uA the bleed takes\n" % (
        F["t_fill_timing"][B["vmax"]] - F["t_case"], F["d_fill_timing"][B["vmax"]], F["pair_case"] * 1e6))
    w("       %.3f s of the hold's least %.3f s\n" % (F["bleed_pair_case"], F["hold_min"]))
    w("       with BRK_VIN at the %.1f V clamp: the pair %.1f uA, %.1f uA in hand, filled from %.1f C or by a doubling every %.2f K\n" % (
        V_CLAMP, F["room_timing"][V_CLAMP] * 1e6, F["left_timing"][V_CLAMP] * 1e6, F["t_fill_timing"][V_CLAMP], F["d_fill_timing"][V_CLAMP]))
    w("     AGAINST THE STATIC LIMIT (the %.1f V clamp): it leaves the pair %.1f uA, %.1f uA a breaker FET; at the held case %.1f uA in hand and %.1f uA a\n" % (
        V_CLAMP, F["room_static"][V_CLAMP] * 1e6, F["room_static"][V_CLAMP] * 1e6 / 2.0, F["left_static"] * 1e6, F["each_left_static"] * 1e6))
    w("       battery FET (L4-E11's %.0f uA each is that limit less the clamp's 1 MOhm over three, %.1f uA: reproduced); the pair alone fills it from a\n" % (
        F["l4_each"] * 1e6, F["l4_each_re"] * 1e6))
    w("       %.1f C case, or at the held case if the leakage doubles every %.2f K or faster\n" % (F["t_fill_static"], F["d_fill_static"]))
    w("     L8P-F06: %s on the ASSUMED doubling (nothing printed above 25 C): %s;\n" % (
        "both limits hold at the held case" if F["f06_holds"] else "A LIMIT DOES NOT HOLD AT THE HELD CASE",
        "the timing limit is the nearer one, %.1f uA and %.1f K away" % (F["left_timing"][B["vmax"]] * 1e6, F["t_fill_timing"][B["vmax"]] - F["t_case"])))
    w("       E-14c measures IDSS of Q101 and Q102 hot and keeps the pair at most %.0f uA at the held case, inside BOTH limits (OPEN)\n" % (F["pair_case"] * 1e6))
    w("   L8P-F07, THE GUARD RT1 (Murata PRF15BB103RB6RC; DM-SA16-E056 Rev.1, p.4, read from the sheet's text):\n")
    w("     printed: R25 %.0f kOhm +-%.0f %%; %.0f kOhm at a sensing temperature %s%.0f C (no upper bound); %.1f MOhm at %.0f +-%.0f C; %.0f V; %.0f to +%.0f C\n" % (
        g["r25"] / 1e3, g["tol"] * 100, g["r1"] / 1e3, "over " if g["gt"] else "", g["t1"], g["r2"] / 1e6, g["t2"], g["t2_tol"], g["vmax"], g["tmin"], g["tmax"]))
    w("     record l9stk 15.5 reads '47 kOhm at 130 C plus or minus 3 C': %s; the sheet's 47 kOhm column is its 470 ohm groups' (the header '*at %s *at 47kohm')\n" % (
        "yes" if F["l9_47k"] else "no", ", ".join(F["hdr_47k"])))
    w("     read as single crossings (INFERRED: the sheet defines a sensing temperature as where R reaches the value): RT1 under %.0f kOhm to %.0f C,\n" % (
        g["r1"] / 1e3, F["print"]["under_r1_to"]))
    w("       under %.1f MOhm to %.0f C, over %.1f MOhm from %.0f C; at 25 C only, %.0f to %.0f kOhm\n" % (
        g["r2"] / 1e6, F["print"]["under_r2_to"], g["r2"] / 1e6, F["print"]["over_r2_from"], F["r25"][0] / 1e3, F["r25"][1] / 1e3))
    w("     what the loop asks of RT1 (the first inverter's gate DOCK_EN_RET, with board A's %.0f kOhm on DOCK_EN_OUT and %.2f uA on the return,\n" % (
        F["load_out"] / 1e3, (F["load_ret"] + F["n_idss"]) * 1e6))
    w("       R106 and R107 at 1 %%, ASSUMED, each at its worse sign; the 2N7002's threshold %.1f to %.1f V):\n" % (R["n_vth"][0], R["n_vth"][1]))
    w("       no trip while RT1 is under %.1f kOhm at %.1f V and %.1f kOhm at %.1f V (L4-E11 20c's %.1f kOhm at %.1f V is the nominal: %.2f here)\n" % (
        F["on"][F["l4_v"]] / 1e3, F["l4_v"], F["on"][B["vmax"]] / 1e3, B["vmax"], F["l4_on"] / 1e3, F["l4_v"], F["nom_on"] / 1e3))
    w("       surely off from %.1f kOhm at %.1f V and %.1f kOhm at %.1f V (L4-E11 20c's %.1f kOhm nominal: %.1f here)\n" % (
        F["off"][F["l4_v"]] / 1e3, F["l4_v"], F["off"][B["vmax"]] / 1e3, B["vmax"], F["l4_off"] / 1e3, F["nom_off"] / 1e3))
    w("       a ramping closed loop never read held while RT1 is under %.1f kOhm (L4-E11 20c), the copper at the air, %.2f C or under\n" % (F["window"] / 1e3, B["air"]))
    w("       a held DOCK_EN_OUT read powered while RT1 is at least %.2f kOhm at %.1f V and %.2f kOhm at %.1f V (the return taken at 0 V; the check V1\n" % (
        F["low"][R["v_run"]] / 1e3, R["v_run"], F["low"][F["l4_v"]] / 1e3, F["l4_v"]))
    w("         took it at its 0.055 V most and read 3.46 kOhm)\n")
    w("     where the PTC sits (l9stk 15.5 at the allowances, held): the junction %.1f C at 10 A, %.1f C in the 18 A service, %.1f C at 23.93 A; the copper\n" % (
        F["tj10"], F["tj18"], F["tj24"]))
    w("       is cooler by up to %.2f K at 23.93 A (%.2f and %.2f C), so the junction's reading is the hot side for the no-trip judgement\n" % (
        F["lead24"], F["cu10"], F["cu18"]))
    w("     ON THE PRINTED POINTS:\n")
    w("       the trip side: over %.1f MOhm from %.0f C, against the %.1f kOhm that turns the first inverter off at %.1f V: the breaker is off before the\n" % (
        g["r2"] / 1e6, F["print"]["over_r2_from"], F["off"][B["vmax"]] / 1e3, B["vmax"]))
    w("         PTC's copper passes %.0f C: %s. The junction over that copper is NOT BOUNDED (the check V2's V2-m5): with L4-E11's worst split the\n" % (
        F["print"]["over_r2_from"], "PRINTED" if F["trip_print"] else "NOT PRINTED"))
    w("         hottest FET dissipates %.3f W (9/8 of the even split's %.3f W), %.2f K over ITS OWN mounting base (Rth(j-mb) %.1f K/W; round 5 added the\n" % (
        F["p_worst"], F["p_even"], F["lead_worst"], F["rth_jmb"]))
    w("         even split's %.2f K), %.2f C if that base sat at the sensor's copper; how far the base leads the sensor's copper no record bounds:\n" % (
        F["lead24"], F["trip_tj_worst"]))
    w("         %.2f K are left for it to 150 C; E11-29's coupon reads the PTC's site against each junction with one FET heated alone (L4-E11 22h)\n" % F["trip_room"])
    w("       no trip at 10 A (%.1f C): under %.0f kOhm against %.1f kOhm at %.1f V: %s; at a pack of %.2f V or more the printed bound suffices: %s\n" % (
        F["tj10"], g["r1"] / 1e3, F["on"][F["l4_v"]] / 1e3, F["l4_v"], "PRINTED" if F["notrip10_print_low"] else "NOT PRINTED",
        F["v_print"], "PRINTED" if F["notrip10_print_high"] else "NOT PRINTED"))
    w("       no trip in the 18 A service (%.1f C): nothing printed under %.1f MOhm between %.0f and %.0f C: %s at any pack voltage\n" % (
        F["tj18"], g["r2"] / 1e6, g["t1"], F["print"]["under_r2_to"], "PRINTED" if F["notrip18_print"] else "NOT PRINTED"))
    w("       the window (%.1f kOhm, the copper from -20 to %.2f C) and the held reading (%.2f kOhm): nothing printed but the 25 C row: NOT PRINTED\n" % (
        F["window"] / 1e3, B["air"], F["low"][R["v_run"]] / 1e3))
    w("     ON THE TYPICAL CURVE (3.2, the BB characteristic normalised to R25, read by read_prf_typical.py; INFERRED): it reads x10 at %.1f C and x100\n" % F["curve_x10"])
    w("       at %.1f C, the 1 kOhm group's printed 115 +-5 and 130 +-3 C; at %.0f C, where PRF15BB103 prints at least x%.0f (R25 at its most), it reads\n" % (
        F["curve_x100"], F["print"]["over_r2_from"], F["print_at_r2"]))
    w("       x%.0f: the curve is not the 10 kOhm part's own above x10, the only curve the maker draws for it\n" % F["curve_at_r2"])
    w("       10 A, %.1f C: x%.3f, RT1 at most %.1f kOhm (R25 at its most): no trip at any pack voltage, inside the window: %s\n" % (
        F["tj10"], F["typ10"], F["r10_typ"] / 1e3, "HOLDS" if F["f07_typ_10"] else "DOES NOT HOLD"))
    w("       the window: at most x%.3f from -20 C (the curves' top at -19.5 C), %.1f kOhm against %.1f kOhm; the held reading: at least x%.3f (the figure's\n" % (
        PRF_TOP_M20, F["win_typ"] / 1e3, F["window"] / 1e3, PRF_LOWEST))
    w("         lowest stroke), %.3f kOhm against %.3f kOhm\n" % (F["low_typ"] / 1e3, F["low"][R["v_run"]] / 1e3))
    w("       the 18 A service held, %.1f C: x%.2f, RT1 %.1f / %.1f / %.1f kOhm (R25 least, nominal, most), every one over the %.1f kOhm at %.1f V; at\n" % (
        F["tj18"], F["typ18"], F["r18_typ"][0] / 1e3, F["r18_typ"][1] / 1e3, F["r18_typ"][2] / 1e3, F["on"][F["l4_v"]] / 1e3, F["l4_v"]))
    w("         %.1f V the %.1f kOhm holds only for R25 under %.2f kOhm; at the copper's %.2f C, x%.2f, %.1f kOhm at R25's least: still over\n" % (
        B["vmax"], F["on"][B["vmax"]] / 1e3, F["r25_max_16v8"] / 1e3, F["cu18"], F["typ18_cu"], F["r18_typ_cu_lo"] / 1e3))
    w("       so on the typical curve the guard may turn the breaker off in the 18 A service held at l9stk's reading: %s\n" % (
        "it does NOT keep C-PROT's 18 A for 60 s uninterrupted there" if not F["f07_typ_18"] else "it does not"))
    w("       its onset at %.1f V on the typical curve: %.1f C (R25 at its most), %.1f C (nominal), %.1f C (least); from 10 A held (%.1f C) the 60 s\n" % (
        F["l4_v"], F["onset"]["most"], F["onset"]["nominal"], F["onset"]["least"], F["tj10"]))
    w("         service stays under it if the copper's first-order time constant (an ASSUMED form) is at least %.1f s, %.1f s, %.1f s: no record holds it\n" % (
        F["tau_need"]["most"], F["tau_need"]["nominal"], F["tau_need"]["least"]))
    w("     L8P-F07: OPEN; the trip side's resistance printed (the junction over the sensor's copper not bounded), the no-trip side at 10 A printed only\n")
    w("       from a %.2f V pack, the 18 A no-trip side not printed and on the\n" % F["v_print"])
    w("       typical curve reached at l9stk's held reading; l9stk 15.5's '9.0 to 15.0 K under the band' rests on the 470 ohm column's 47 kOhm\n")
    w("   THE ALTERNATIVE PARTS (named, NOT SELECTED; SESSION):\n")
    b = F["prf"]["PRF15BA102RB6RC"]
    w("     Murata PRF15BA102RB6RC (the same sheet, p.4): R25 %.0f ohm +-%.0f %%, %.0f kOhm at %.0f +-%.0f C, %.0f kOhm at %.0f +-%.0f C, %.0f to +%.0f C: under\n" % (
        b["r25"], b["tol"] * 100, b["r1"] / 1e3, b["t1"], b["t1_tol"], b["r2"] / 1e3, b["t2"], b["t2_tol"], b["tmin"], b["tmax"]))
    w("       %.0f kOhm to %.0f C prints the no-trip side at 10 and 18 A (%s); its %.0f kOhm point is under the %.1f kOhm sure-off (%s) and its least R25\n" % (
        b["r1"] / 1e3, b["t1"] - b["t1_tol"], "yes" if F["ba102_notrip"] else "no", b["r2"] / 1e3, F["off"][B["vmax"]] / 1e3, "trip printed" if F["ba102_trip"] else "trip NOT printed"))
    w("       %.0f ohm under the %.2f kOhm held reading (%s): not a part swap\n" % (b["r25"] * (1 - b["tol"]), F["low"][R["v_run"]] / 1e3,
                                                                            "holds" if F["ba102_low"] else "fails"))
    T5 = TDK_B59721
    w("     TDK B59721A0130A062 (superior series, EIA 0805, August 2019, p.%d; the sheet held back by its notice): RR %.0f ohm +-%.0f %% at 25 C;\n" % (
        T5["page"], T5["rr"], T5["drr"] * 100))
    w("       R(Tsense - 5 C) %.1f kOhm at most, R(Tsense + 5 C) %.1f kOhm and R(Tsense + 15 C) %.0f kOhm at least: limits on both sides, as condition C3\n" % (
        T5["r_m5"] / 1e3, T5["r_p5"] / 1e3, T5["r_p15"] / 1e3))
    w("       asks; Tsense 130 C: no trip to 125 C, off by 145 C (the hottest junction %.2f C over its own base at the worst split, the base against the\n" % F["tdk_trip_tj"])
    w("       sensor not bounded); its printed %.0f kOhm is under the loop's sure-off, so the loop scales by k (R106, R107 and the guard together keep\n" % (T5["r_p15"] / 1e3))
    w("       every level of L4-E11's 20c). The bounds on k (round 5 took the sure-off as an upper bound; it is a LOWER bound: the check V2's V2-B3):\n")
    w("         no trip to 125 C: k x %.1f kOhm at most %.1f kOhm: k at most %.2f\n" % (T5["r_m5"] / 1e3, F["on"][F["l4_v"]] / 1e3, F["tdk_k_notrip"]))
    w("         surely off by 145 C: k x %.0f kOhm at least %.1f kOhm (at %.1f V): k at least %.2f\n" % (T5["r_p15"] / 1e3, F["off"][B["vmax"]] / 1e3, B["vmax"], F["tdk_k_trip"]))
    for v in sorted(F["tdk_win"]):
        w("         the held reading at %.1f V on its least R25 (%.0f ohm): k at least %.2f: the window %.2f to %.2f%s\n" % (
            v, T5["rr"] * (1 - T5["drr"]), F["tdk_k_low"][v], F["tdk_win"][v][0], F["tdk_win"][v][1],
            ", %.1f %% wide: A k EXISTS" % (F["tdk_width"][v] * 100) if F["tdk_fits"][v] else ": NO k EXISTS"))
    w("       so on the sheet's printed limits a window exists at both voltages (the resistors' 1 % is already in the loop's levels). NOT SELECTED, on:\n")
    w("         (1) dissipation: in the part at its printed %.1f kOhm, %.1f to %.1f mW over the window (k %.2f to %.2f, the pack at %.1f V), against the\n" % (
        T5["r_m5"] / 1e3, F["tdk_p"][0] * 1e3, F["tdk_p"][1] * 1e3, F["tdk_k_span"][0], F["tdk_k_span"][1], B["vmax"]))
    w("             sheet's note (p.%d): 'the electrical power during measurement should be below %.0f mW for EIA case size 0805': its printed\n" % (
        T5["page"], T5["p_meas"] * 1e3))
    w("             resistance limits are read under that power; the loop runs the part at three times it or more, so they are not its limits there\n")
    w("         (2) static draw: %.2f to %.2f mA in the loop (the part at its least R25), against record l9stk's %.2f mA\n" % (
        F["tdk_static"][0] * 1e3, F["tdk_static"][1] * 1e3, F["static"] * 1e3))
    w("         (3) the sheet's own reference table (p.%d, 'Rmin and Rmax values are typical values for reference only'; TYPICAL): the part's least\n" % T5["page_ref"])
    w("             resistance is not at 25 C: Rmin %.0f ohm at %d C asks k at least %.2f at %.1f V and %.2f at %.1f V, over the %.2f no trip allows:\n" % (
        T5["rmin_ref"], T5["t_rmin_ref"], F["tdk_k_low_ref"][R["v_run"]], R["v_run"], F["tdk_k_low_ref"][F["l4_v"]], F["l4_v"], F["tdk_k_notrip"]))
    w("             on that table %s (round 5 applied the dip to Murata's part and not to TDK's)\n" % (
        "no k exists at either voltage" if not any(F["tdk_fits_ref"].values()) else "A k EXISTS"))
    w("     SESSION: RT1 stays PRF15BB103RB6RC in the A draft; L8P-F07 goes to record l9stk (15.5) with L4-E11; the question to Murata is drafted, unsent\n")
    w("\n")
    with tempfile.TemporaryDirectory(prefix="l8p_") as d:
        # 4. each draft alone
        w("4. EACH DRAFT ON A SCRATCH COPY (check, apply once, refuse twice, refuse the tree's own generator)\n")
        before = {b: sha(GEN[b], 64) for b in "pea"}
        for b in "pea":
            s = MINE[b]
            t = os.path.join(d, "alone_gen_sch_%s.py" % b); shutil.copy(GEN[b], t); pre = sha(t, 64)
            r1 = subprocess.run([sys.executable, "-B", s, t], capture_output=True)
            ok1 = r1.returncode == 0 and b"CHECK OK" in r1.stdout and sha(t, 64) == pre
            r2 = subprocess.run([sys.executable, "-B", s, t, "--write"], capture_output=True)
            ok2 = r2.returncode == 0 and b"WRITTEN" in r2.stdout
            r3 = subprocess.run([sys.executable, "-B", s, t, "--write"], capture_output=True)
            r4 = subprocess.run([sys.executable, "-B", s, GEN[b], "--write"], capture_output=True)
            w("   %s: check %s; applied %s; second application %s; the tree's gen_sch_%s.py %s\n" % (
                os.path.basename(s), "OK" if ok1 else "FAILED", "OK" if ok2 else "FAILED",
                "refused" if r3.returncode == 3 else "NOT REFUSED", b, "refused (NOT RELEASED)" if r4.returncode == 3 and b"NOT RELEASED" in r4.stderr else "NOT REFUSED"))
        for b, extra in sorted(MINE2.items()) + sorted(MINE_AFTER.items()):
            for s in extra:
                t0 = os.path.join(d, "bare_gen_sch_%s.py" % b); shutil.copy(GEN[b], t0)
                r0 = subprocess.run([sys.executable, "-B", s, t0, "--write"], capture_output=True)
                t = os.path.join(d, "second_gen_sch_%s.py" % b); shutil.copy(GEN[b], t)
                if run(MINE[b], t, b)[0] != 0:
                    refuse("this record's first board %s draft refused a clean copy" % b)
                pre = sha(t, 64)
                r1 = subprocess.run([sys.executable, "-B", s, t], capture_output=True)
                ok1 = r1.returncode == 0 and b"CHECK OK" in r1.stdout and sha(t, 64) == pre
                r2 = subprocess.run([sys.executable, "-B", s, t, "--write"], capture_output=True)
                ok2 = r2.returncode == 0 and b"WRITTEN" in r2.stdout
                r3 = subprocess.run([sys.executable, "-B", s, t, "--write"], capture_output=True)
                r4 = subprocess.run([sys.executable, "-B", s, GEN[b], "--write"], capture_output=True)
                w("   %s (after %s): without it %s; check %s; applied %s; second application %s; the tree's gen_sch_%s.py %s\n" % (
                    os.path.basename(s), os.path.basename(MINE[b]), "refused" if r0.returncode == 3 and sha(t0, 64) == before[b] else "NOT REFUSED",
                    "OK" if ok1 else "FAILED", "OK" if ok2 else "FAILED", "refused" if r3.returncode == 3 else "NOT REFUSED", b,
                    "refused" if r4.returncode == 3 else "NOT REFUSED"))
        if any(sha(GEN[b], 64) != before[b] for b in "pea"):
            refuse("a draft wrote into the tree")
        w("   the tree's generators are unchanged: yes\n\n")
        # 5. composition
        w("5. COMPOSITION IN L4-E9'S CHANGE-LIST ORDER (records/l4e9/L4-POWER-ARCHITECTURE.md section 3; board A as the candidate's list carries it,\n")
        w("   fnd/v2cand at dfa1eef2, rows 24 to 33: gnd002, hotr1, packrtn, slotlm, fb01, this record's ptc, L4-E11's dd7, then mainpb; the check V2's V2-m9)\n")
        for b in sorted(LIST_ABSENT):
            w("   board %s, the list's rows whose drafts are NOT in this record's tree (main at 64cd25ee; record l8r2's rounds 4 to 6 on fnd/l8r3 at 89924e40): %s;\n" % (
                b.upper(), ", ".join("%s (%s)" % (n, row) for _r, n, row in LIST_ABSENT[b])))
            w("     left out below; their place is right before this record's draft; test_l8p composes the whole list wherever a tree holds them\n")
        composed = {}
        for b in "pea":
            fwd = order(b, "fwd")
            p, res = compose(b, fwd, d, "fwd")
            composed[b] = p if all(v.startswith("OK") for _s, v in res) and len(res) == len(fwd) else None
            w("   board %s, this record's draft%s in its place:\n" % (b.upper(), "s" if len(mine_seq(b)) > 1 else ""))
            for s, v in res:
                w("     %-44s %s\n" % (s, v))
            first = order(b, "first")
            _p, res = compose(b, first, d, "rev")
            w("   board %s, this record's draft first, then the order: %s\n" % (b.upper(), "every step OK" if all(v.startswith("OK") for _s, v in res) and len(res) == len(first)
                                                                      else "; ".join("%s %s" % x for x in res if not x[1].startswith("OK"))))
            last = order(b, "last")
            _p, res = compose(b, last, d, "last")
            w("   board %s, the order, then this record's draft last: %s\n" % (b.upper(), "every step OK" if all(v.startswith("OK") for _s, v in res) and len(res) == len(last)
                                                                       else "; ".join("%s %s" % x for x in res if not x[1].startswith("OK"))))
            for f, _after in FOLLOW.get(b, ()):
                # on the order with this record's own drafts last but without the round 8 guard, which would remove RT1 first
                _p, _res = compose(b, [x for x in last if x not in MINE_AFTER.get(b, ())], d, "last_nothg")
                rc_f, why_f = run(f, _p, b)
                w("     (without %s there: the list puts it before d8dec31's mainpb, R-217 before R-193; applied after mainpb\n" % os.path.relpath(f, RECS))
                w("      it is %s)\n" % ("refused, mainpb having taken its R233 and C241 as the next free: %s" % scrub(why_f, d) if rc_f else "NOT REFUSED"))
            if TREE_ONLY.get(b):
                tre = order(b, "tree")
                tp, res = compose(b, tre, d, "tree")
                composed[b + "+"] = tp if all(v.startswith("OK") for _s, v in res) and len(res) == len(tre) else None
                w("   board %s, the same with the tree's drafts the list does not name (%s), before this record's: %s\n" % (
                    b.upper(), ", ".join("%s's %s" % x for x in TREE_ONLY[b]), "every step OK" if composed[b + "+"]
                    else "; ".join("%s %s" % x for x in res if not x[1].startswith("OK"))))
        w("\n")
        # 6. designators
        w("6. DESIGNATORS EACH DRAFT ADDS (the forward order, with the tree's drafts the list does not name; part calls, listed tokens and each draft's declared ADDS)\n")
        for b in "pea":
            fwd = order(b, "tree")
            p = os.path.join(d, "desig_gen_sch_%s.py" % b); shutil.copy(GEN[b], p)
            before_t = open(p, encoding="utf-8").read(); adds = {}
            for s in fwd:
                if run(s, p, b)[0] != 0:
                    break
                after_t = open(p, encoding="utf-8").read()
                adds[os.path.relpath(s, RECS)] = added(before_t, after_t, s)
                before_t = after_t
            own = {os.path.relpath(x, RECS) for x in mine_all(b)}
            mine = set().union(*[adds.get(k, set()) for k in own])
            if len(own) > 1 and sum(len(adds.get(k, set())) for k in own) != len(mine):
                refuse("this record's board %s drafts share a designator" % b)
            w("   board %s, this record's: %s\n" % (b.upper(), ", ".join(sorted(mine, key=lambda x: (re.sub(r"\d", "", x), int(re.sub(r"\D", "", x) or 0)))) or "none (nets only)"))
            meets = {k: sorted(v & mine) for k, v in adds.items() if k not in own and v & mine}
            w("   board %s, this record's against every other draft's: %s\n" % (b.upper(), "DISJOINT" if not meets else "MEETS %s" % meets))
            dup = duplicates(before_t)
            w("   board %s, literal part calls drawn twice in the composed generator: %s\n" % (b.upper(), ", ".join(dup) if dup else "none"))
        w("\n")
        # 7. regeneration and the netlist check
        w("7. REGENERATION ON THE RUNNER (gen_netlist.py: the generator's own part table, no KiCad) AND THE NETLIST CHECK\n")
        for b in "pea":
            rc, path, _t = netlist_text(b, GEN[b], d, "base")
            if rc:
                refuse("board %s's own generator did not run: %s" % (b, path))
            a, k = CHK.read_netlist(open(path, "rb").read()), CHK.read_netlist(open(NET[b], "rb").read())
            pa, pk = pins_of(a), pins_of(k)
            diff = [x for x in sorted(set(pa) | set(pk)) if pa.get(x) != pk.get(x)]
            nc = [x for x in diff if pa.get(x) is None and str(pk.get(x)).startswith("unconnected-")]
            fpd = [r for r in sorted(set(a["comps"]) | set(k["comps"])) if a["comps"].get(r, {}).get("footprint") != k["comps"].get(r, {}).get("footprint")]
            w("   board %s unpatched: %d connected pins against the committed KiCad netlist's %d; differences %d, all KiCad's names for "
              "open pins: %s; footprints differing: %d\n" % (b.upper(), len(pa), len(pk), len(diff), "yes" if len(nc) == len(diff) else "NO", len(fpd)))
        w("   the netlist check on the committed netlists:\n")
        buf = io.StringIO(); kit, _v = CHK.run(NET, ROOT, buf)
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        alone = {}
        for b in "pea":
            t = os.path.join(d, "regen_gen_sch_%s.py" % b); shutil.copy(GEN[b], t)
            if any(run(x, t, b)[0] != 0 for x in mine_all(b)):
                refuse("this record's board %s draft refused a clean copy" % b)
            rc, path, table = netlist_text(b, t, d, "mine")
            if rc:
                refuse("board %s's generator with this record's draft did not run: %s" % (b, path))
            alone[b] = (path, table)
            w("   board %s with this record's draft alone: the generator ran to its end (%d parts, %d unplaced, intent written: %s)\n"
              % (b.upper(), len(table["parts"]), len(table["unplaced"]), "yes" if table["intent_written"] else "NO"))
        buf = io.StringIO(); CHK.run({b: alone[b][0] for b in "pea"}, ROOT, buf, label=lambda x: "regenerated board %s, this record's draft alone" % x.upper())
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        comp = {}
        for b in "pea":
            if not composed[b]:
                w("   board %s composed in L4-E9's order: the composition refused (section 4), not regenerated\n" % b.upper())
                continue
            rc, path, table = netlist_text(b, composed[b], d, "composed")
            if rc == 0:
                comp[b] = path
                w("   board %s composed in L4-E9's order: the generator ran to its end (%d parts, intent written: %s)\n"
                  % (b.upper(), len(table["parts"]), "yes" if table["intent_written"] else "NO"))
                continue
            w("   board %s composed in L4-E9's order: the generator refused: %s\n" % (b.upper(), path))
            # the same composition without this record's draft: the refusal is the other drafts' (a finding for their owners)
            q, res = compose(b, order(b, "without"), d, "without")
            rc2, line2, _t2 = netlist_text(b, q, d, "without")
            w("     without this record's draft the same composition's generator %s\n" % (
                "refuses with the same line: the refusal is another draft's (section 8)" if rc2 and line2 == path else
                "runs" if rc2 == 0 else "refuses otherwise: %s" % line2))
            # scratch stand-ins for the other drafts' run-time defects (never drafts, never applied), so this record's loop is
            # judged in the whole composition
            s = os.path.join(d, "standin_gen_sch_%s.py" % b); shutil.copy(composed[b], s)
            txt = open(s, encoding="utf-8").read(); used = []
            for fid, why, old, rep in STANDINS.get(b, ()):
                if txt.count(old) == 1:
                    txt = txt.replace(old, rep); used.append(fid)
            open(s, "w", encoding="utf-8").write(txt)
            rc3, path3, table3 = netlist_text(b, s, d, "standin")
            w("     with scratch stand-ins for %s (never drafts, never applied): %s\n" % (", ".join(used) or "none",
              "the generator ran to its end (%d parts, intent written: %s)" % (len(table3["parts"]), "yes" if table3["intent_written"] else "NO") if rc3 == 0 else "still refused: %s" % path3))
            if rc3 == 0:
                comp[b] = path3
        if comp:
            buf = io.StringIO(); CHK.run(comp, ROOT, buf, label=lambda x: "regenerated board %s, composed in L4-E9's order%s" % (x.upper(), "" if "standin" not in comp[x] else " with the stand-ins"))
            w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        for b in sorted(TREE_ONLY):
            if not composed.get(b + "+"):
                refuse("board %s with the tree's drafts the list does not name did not compose" % b)
            rc, path, table = netlist_text(b, composed[b + "+"], d, "tree")
            if rc:
                refuse("board %s with the tree's drafts the list does not name: the generator refused: %s" % (b, path))
            w("   board %s, the list's order with the tree's drafts it does not name (%s): the generator ran to its end (%d parts, intent written: %s)\n" % (
                b.upper(), ", ".join("%s's %s" % x for x in TREE_ONLY[b]), len(table["parts"]), "yes" if table["intent_written"] else "NO"))
            buf = io.StringIO(); CHK.run({b: path}, ROOT, buf, label=lambda x: "regenerated board %s, the list's order with those drafts" % x.upper())
            w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        # DD-7's readers admitted by pin (L4E11-R10-F2): mutations of the composed board A that a rule admitting U48, Q44 or R109 by
        # its reference alone would pass
        for tag, swaps, what in (("mut_a2", [(("U48", "2"), ("U48", "1"))], "U48's SENSE1 and VDD exchanged: VBAT's pin on the return"),
                                 ("mut_a3", [(("Q44", "3"), ("Q44", "2"))], "Q44's drain and source exchanged: the source on the return"),
                                 ("mut_a4", [(("R109", "2"), ("R144", "2"))], "R109 from DOCK_EN_OUT to the ground: U48's SENSE2 reads nothing")):
            if "a" not in comp:
                refuse("board A composed in L4-E9's order did not regenerate, so DD-7's readers cannot be mutated")
            m = mutate(comp["a"], d, tag, swaps)
            buf = io.StringIO(); CHK.run({"a": m}, ROOT, buf, label=lambda x, what=what: "mutated composed board A (%s)" % what)
            w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        # Round 8: every node the composed boards put on the loop's return, the count the guard's window rests on (l8p_c4.out section 3)
        for b in "pea":
            if b in comp:
                nl_ = CHK.read_netlist(open(comp[b], "rb").read())
                w("   board %s composed, the nodes on DOCK_EN_RET: %s\n" % (b.upper(), ", ".join("%s.%s" % x for x in sorted(CHK._nodes(nl_, "DOCK_EN_RET")))))
        # Round 8: the guard's seven mutations (record l9stk 15.9 round 5 (b), L9S5-F1), each on the composed board A, each read on THG
        for k_, (what, ops) in enumerate(GUARD_MUTATIONS, 1):
            m = mutate_ops(comp["a"], d, "mut_thg%d" % k_, ops)
            buf = io.StringIO(); CHK.run({"a": m}, ROOT, buf, label=lambda x, what=what: "mutated composed board A, the guard: %s" % what)
            w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        # Round 8: the old guard, board A with round 7's PTC draft and no guard (RT1 closes the loop): withdrawn, so it must not read DRAWN
        t = os.path.join(d, "ptc_only_gen_sch_a.py"); shutil.copy(GEN["a"], t)
        if run(MINE["a"], t, "a")[0] != 0:
            refuse("the PTC draft refused a clean copy")
        rc, path, _t = netlist_text("a", t, d, "ptc_only")
        if rc:
            refuse("board A with the PTC draft alone did not run: %s" % path)
        buf = io.StringIO(); CHK.run({"a": path}, ROOT, buf, label=lambda x: "regenerated board A, round 7's RT1 without the guard (the withdrawn PTC)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        m1 = mutate(alone["p"][0], d, "mut_p", [(("J_SMB", "6"), ("J_SMB", "7"))])
        buf = io.StringIO(); CHK.run({"p": m1}, ROOT, buf, label=lambda x: "mutated board P (J_SMB pins 6 and 7 exchanged)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        m2 = mutate(alone["a"][0], d, "mut_a", [(("J_DOCK", "3"), ("J_DOCK", "4"))])
        buf = io.StringIO(); CHK.run({"a": m2}, ROOT, buf, label=lambda x: "mutated board A (J_DOCK pins 3 and 4 exchanged)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        m3 = mutate(alone["p"][0], d, "mut_p2", [(("Q106", "1"), ("Q105", "1"))])
        buf = io.StringIO(); CHK.run({"p": m3}, ROOT, buf, label=lambda x: "mutated board P (Q105's and Q106's gates exchanged: the inhibit no longer gated by PGD)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        m4 = mutate(alone["p"][0], d, "mut_p3", [(("U104", "3"), ("U104", "4"))])
        buf = io.StringIO(); CHK.run({"p": m4}, ROOT, buf, label=lambda x: "mutated board P (U104's inputs exchanged: the detector reads a forward drop)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        m5 = mutate(alone["p"][0], d, "mut_p4", [(("R120", "1"), ("R119", "2"))])
        buf = io.StringIO(); CHK.run({"p": m5}, ROOT, buf, label=lambda x: "mutated board P (R120 on PACK_N and R119 on GND: U103 no longer reads R10)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        m6 = mutate(alone["p"][0], d, "mut_p5", [(("Q109", "1"), ("Q109", "5"))])
        buf = io.StringIO(); CHK.run({"p": m6}, ROOT, buf, label=lambda x: "mutated board P (Q109's source pin 1 and its drain exchanged: the ideal diode the wrong way round)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        m7 = mutate(alone["p"][0], d, "mut_p6", [(("U105", "5"), ("R16", "1"))])
        buf = io.StringIO(); CHK.run({"p": m7}, ROOT, buf, label=lambda x: "mutated board P (U105's GATE on Q1's gate: a second driver on the gauge's charge switch)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        t = os.path.join(d, "breaker_only_gen_sch_p.py"); shutil.copy(GEN["p"], t)
        if run(MINE["p"], t, "p")[0] != 0:
            refuse("the breaker draft refused a clean copy")
        rc, path, _t = netlist_text("p", t, d, "breaker_only")
        buf = io.StringIO(); CHK.run({"p": path}, ROOT, buf, label=lambda x: "regenerated board P, the breaker draft without the ideal diode (DD-5 uncorrected)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        w("\n")
        # 8. intent
        w("8. THE INTENT THE PATCHED BOARD P GENERATOR WRITES FOR THE NEW NETS\n")
        it = alone["p"][1]["intent"]
        for n in ("PACK_P", "BRK_VIN", "BRK_SNS", "VCC_F", "SCP_OUT", "SW"):
            r = it["rails"].get(n) or {}
            w("   rail %-8s source %s, loads %s, switch %s on %s%s%s\n" % (n, r.get("source"), json.dumps(r.get("loads"), sort_keys=True), r.get("switch", "-"),
                                                                      r.get("enable_net", "-"), ", series of %s" % r["series_of"] if r.get("series_of") else "",
                                                                      ", fed from %s" % r["fed_from"] if r.get("fed_from") else ""))
        for n in ("BRK_GATE", "BRK_UVLO", "BRK_H", "BRK_HD", "BRK_G2", "BRK_PGD", "BRK_CMID", "INH_NTC", "INH_REF", "INH_OUT", "INH_G", "DOCK_EN_OUT", "DOCK_EN_RET",
                  "REV_VZ", "REV_IREF", "REV_ISNS", "REV_IOUT", "REV_IG", "REV_VP", "REV_VN", "REV_VOUT", "REV_VG", "REV_MID",
                  "IDL_GATE", "IDL_VCAP", "IDL_EN", "IDL_AMID", "IDL_CMID"):
            r = it["nodes"].get(n) or {}
            w("   node %-11s v_max %s V%s%s\n" % (n, r.get("v_max"), ", v_min %s V" % r["v_min"] if r.get("v_min") else "",
                                             ", rides on %s by %s V" % (r["rides_on"], r["bias_v"]) if r.get("rides_on") else ""))
        cl = it.get("clamps", {}).get("D101") or {}
        w("   clamp D101: %s, protected %s, return %s\n" % (cl.get("direction"), cl.get("protected"), cl.get("return")))
        for cap in ("C106", "C107", "C108", "C111", "C112", "C114"):
            bp = [b_ for b_ in it.get("bypass", []) if b_.get("cap") == cap]
            w("   decoupling %s: %s\n" % (cap, "class %s at %s.%s on %s" % (bp[0].get("class"), bp[0].get("part"), bp[0].get("pin"), bp[0].get("net")) if bp else "ABSENT"))
        # round 8: what the patched board A generator writes for the guard's nets
        ia = alone["a"][1]["intent"]
        w("   board A (round 8, the thermal guard):\n")
        for n in ("DOCK_EN_OUT", "DOCK_EN_RET", "THG_MID", "THG_VDD", "THG_OT", "THG_G", "THG_TT", "THG_VT"):
            r = ia["nodes"].get(n) or {}
            w("   node %-11s v_max %s V\n" % (n, r.get("v_max")))
        for cap in ("C261", "C262", "C263"):
            bp = [b_ for b_ in ia.get("bypass", []) if b_.get("cap") == cap]
            w("   decoupling %s: %s\n" % (cap, "class %s at %s.%s on %s%s" % (bp[0].get("class"), bp[0].get("part"), bp[0].get("pin"), bp[0].get("net"),
              ", value_floor %s, value_ceiling %s, esr_max %s" % (bp[0].get("value_floor"), bp[0].get("value_ceiling"), bp[0].get("esr_max")) if bp[0].get("class") == "L" else "") if bp else "ABSENT"))
    w("\n9. FINDINGS FOR OTHER AUTHORS (run-time refusals of the composed generators that no text-level composition test reads; and B-R2's interface)\n")
    w("   L8P-F01 board E: l4e7's backstop draft: C66, C67 and C68 carried no G14 decoupling class: CLOSED by L4-E7's fnd/l4e7r6 at 914a2f5a\n")
    w("     (class D with each maker's clause); board E's composition above uses that draft, copied byte for byte into inputs/, and needs no stand-in for it\n")
    w("   L8P-F02 board A: l4e11's charger draft: VSYS_DOCK named U42 as its source without source_ic, fed from VBAT before VBAT was declared:\n")
    w("     CLOSED by L4-E11's round 9 (fnd/l4e11r9) and carried to its round %d (fnd/l4e11r11 at %s); board A's composition above uses that round's\n" % (L4E11_ROUND, L4E11_AT))
    w("     draft, copied byte for byte into inputs/, and needs no stand-in\n")
    w("   L8P-F03 board E: l4e11's aux draft: +12V_FAN named L4 as its source, which is not on that net: CLOSED the same way (the aux draft\n")
    w("     at %s, copied byte for byte); board E's composition needs no stand-in\n" % L4E11_AT)
    w("   L8P-F04 board A: round 9's DD-7 read the loop powered at half of DOCK_EN_OUT; with the return held DOCK_EN_OUT falls to %.2f V at BRK_VIN\n" % R["out_run"])
    w("     %.1f V: ANSWERED since L4-E11's round 10 (round %d at %s, not on main): U48 reads the return held and the loop powered (section 3b); composed above\n" % (R["v_run"], L4E11_ROUND, L4E11_AT))
    w("   L8P-F05 board A: with the breaker off, the LM5069's internal %.0f MOhm from SENSE to OUT (SNVS452G 7.5, note 1) feeds PACK_P and so CELL+:\n" % (R["r_so"] / 1e6))
    w("     with board A's %.0f kOhm (R107, R108) alone CELL+ reads %.2f V at BRK_VIN %.1f V, over L4-E11's %.2f V 'dead' point; with U104's divider\n" % (
        R["r_alive"] / 1e3, R["cell_off_a"], B["vmax"], R["dead"]))
    w("     (%.1f kOhm) also on PACK_P, %.2f V (%.2f V at the %.1f V clamp); the 1 MOhm's tolerance is not printed: ANSWERED since L4-E11's round 10\n" % (
        r_div_k(), R["cell_off_ap"], R["cell_off_clamp"], V_CLAMP))
    w("     (round %d at %s, not on main) with a bleeder on CELL+ while the inhibit holds: R256 %.1f kOhm; the latch then has two limits on the\n" % (L4E11_ROUND, L4E11_AT, F["r256"] / 1e3))
    w("     sources into CELL+, the static %.3f mA and the timing %.1f uA (L4-E11 20e)\n" % (F["i_static"] * 1e3, F["i_timing"] * 1e6))
    w("   L8P-F06 board P with L4-E11 (the check V1's minor, round 5; restated in round 6 on the two limits of L4-E11's round 12): the breaker FETs' off leakage feeds PACK_P\n")
    w("     and CELL+ with the breaker off, a source inside BOTH of L4-E11's limits (static %.3f mA, timing %.1f uA); the CSD18510Q5B prints IDSS %.0f uA at\n" % (
        F["i_static"] * 1e3, F["i_timing"] * 1e6, F["idss"] * 1e6))
    w("     %.0f V and 25 C only; on the ASSUMED doubling every %.0f K the pair is %.1f uA at the held %.1f C case: %.1f uA inside the timing limit's %.1f uA for\n" % (
        F["idss_v"], IDSS_DOUBLING, F["pair_case"] * 1e6, F["t_case"], F["left_timing"][B["vmax"]] * 1e6, F["room_timing"][B["vmax"]] * 1e6))
    w("     the pair (filled from a %.1f C case, or by a doubling every %.2f K) and %.1f uA inside the static limit's %.1f uA (%.1f C; %.2f K):\n" % (
        F["t_fill_timing"][B["vmax"]], F["d_fill_timing"][B["vmax"]], F["left_static"] * 1e6, F["room_static"][V_CLAMP] * 1e6, F["t_fill_static"], F["d_fill_static"]))
    w("     OPEN (section 3d; page 12j; E-14c keeps both limits)\n")
    w("   L8P-F07 board A with record l9stk (condition C3): Murata prints RT1 (PRF15BB103RB6RC) at %.0f kOhm +-%.0f %% at 25 C, %.0f kOhm over %.0f C and %.1f MOhm\n" % (
        g["r25"] / 1e3, g["tol"] * 100, g["r1"] / 1e3, g["t1"], g["r2"] / 1e6))
    w("     at %.0f +-%.0f C (DM-SA16-E056 Rev.1, p.4): the trip side's resistance is printed (the junction over the sensor's copper is not bounded);\n" % (
        g["t2"], g["t2_tol"]))
    w("     the no-trip side at 10 A only from a %.2f V pack and in the 18 A service not\n" % F["v_print"])
    w("     at all; on the typical curve RT1 reaches %.1f kOhm or more at l9stk's held %.1f C, over the first inverter's %.1f kOhm: OPEN (section 3d; page 12j;\n" % (
        F["r18_typ"][0] / 1e3, F["tj18"], F["on"][F["l4_v"]] / 1e3))
    w("     the question to Murata drafted, unsent; TDK's B59721A named, not selected: a window for k exists on its printed limits, and it is left on\n")
    w("     its dissipation, its static draw and its own typical reference table). The guard's redesign is record l9stk's next round, not this one\n")
    w("\nl8p_drafts: done\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
