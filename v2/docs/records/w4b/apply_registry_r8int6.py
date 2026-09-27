#!/usr/bin/env python3
"""r8int6 re-derivation (the integrator of set 6 of the handover, 27 September 2026) of stream w4b's apply_registry.py,
beside it in this folder. Changed at integration, where the RF-002 walk's rows land in the same commit as board B's change:
every sentence that said the rows are drafted and not adopted says they landed; FEA-002's baselined statement is
left for its own review (layer 3's re-baseline); the open item on RF-002's instrument names
what is still unread by the walk; W4B-D1's firmware duty names the panel firmware (the kit I2C master that writes U6,
PANEL.md section 7), where it said the bridge; EMCON.md's re-read note names section 6's row E-04, which the integration
corrected (the independent check, an AI check); a draft path cites the filed record. The stream's text follows.

Stream w4b (MESHSAT-1357, 27 September 2026): the registry changes of board B's RF-002 work (W4B-D1 the RockBLOCK's ENABLE
forced low by EMCON, W4B-D2 the L4 case (2) enable dividers, W4B-D3 the card bucks' enables on each slot's own 5 V), for the
integrator to run on the tree the stream's files are committed in, AFTER page_drafts_w4b.py has been applied there (this
script refuses otherwise). Edits v2/ecad/tools/pcb_requirements.yaml as text (its formatting kept), by record id, with every
old text asserted; the new shas are read from that tree, never typed; SC and S numbers are the next free ones of that tree
(another branch, fnd/rel2, is adding records too). Usage: apply_registry.py <repo root>

What it does:
  1. Re-reads and rebinds every record bound to gen_sch_b.py@6957adda1bb5f23a or pcb-b-compute.net@8b78c59754a6a0c7 (15
     records), to v2/docs/feasibility/EMCON.md or v2/docs/PANEL.md at the shas they carry (12 records; page_drafts_w4b.py
     changes both), each with a note naming what changed and what its reading rests on (the integration recipe: a changed
     bound file is re-read and rebound; `rules_lib.py requirements` lists them). No result moves.
  2. Rewrites FEA-002's statement clause on the RockBLOCK's ENABLE, and restates S-01 (what is still open of it).
  3. Adds three session choices (W4B-D1 to W4B-D3) and one open item (RF-002's instrument after the rows drafted for the
     tools author), at the next free SC and S numbers."""
import hashlib, os, re, sys

T = sys.argv[1]
sys.path.insert(0, os.path.join(T, "v2/docs/records/r8int5"))
from edlib import rebind, wrap, _rec   # the r8int5 integration's helpers (rebind: a note starting with the path, the sha moved)
P = os.path.join(T, "v2/ecad/tools/pcb_requirements.yaml")
h16 = lambda p: hashlib.sha256(open(os.path.join(T, p), "rb").read()).hexdigest()[:16]
GEN, NET = "v2/ecad/tools/gen_sch_b.py", "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net"
EMC, PAN = "v2/docs/feasibility/EMCON.md", "v2/docs/PANEL.md"
OLD = {GEN: "6957adda1bb5f23a", NET: "8b78c59754a6a0c7"}
NEW = {GEN: h16(GEN), NET: h16(NET)}
assert NEW[GEN] != OLD[GEN] and NEW[NET] != OLD[NET], "the stream's board B files are not in this tree"
_net = open(os.path.join(T, NET), encoding="utf-8").read()
assert all(x in _net for x in ('(ref "U536")', '(ref "U116")', '(ref "U216")', '(ref "U316")', '"/LIME_UVLO"', '"/RB_SW_IEN"')), \
    "this tree's board B netlist is not stream w4b's"
assert "## 4c. Stream w4b, board B" in open(os.path.join(T, EMC), encoding="utf-8").read(), "apply page_drafts_w4b.py first"
assert "(17) The RockBLOCK's ENABLE is" in open(os.path.join(T, PAN), encoding="utf-8").read(), "apply page_drafts_w4b.py first"


def line_of(pattern):
    L = open(os.path.join(T, GEN), encoding="utf-8").read().split("\n")
    hits = [i + 1 for i, l in enumerate(L) if re.search(pattern, l)]
    assert len(hits) == 1, (pattern, hits)
    return hits[0]


RING = line_of(r"^\s+f = s % 3 \+ 1$")
EMC0, EMC1 = line_of(r"# L3 and L7 \(round 8, EMCON\.md section 3"), line_of(r"# PEWAKE# through R232")
SIM0, SIM1 = line_of(r"# S-13, 26 September 2026: each SIM per HD v1.1 Figure 18"), line_of(r'_intent\.node\(cd\(x\), 3\.3, "a SIM card line at the holder')
M2B = line_of(r'part\("J_M2C2", "Connector", "Bus_M\.2_Socket_B"')
IOC = line_of(r'synth\(U_\(1\), "STM32H743VI"')
PORTS = line_of(r"^    PORTS = \{1:")
U12 = line_of(r'synth\("U12", "E22_900M30S"')
U536 = line_of(r'lvc1g08\("U536", "EMCON_HW"')

W4B = "at stream w4b's merge of 27 September 2026 (MESHSAT-1357, board B: RF-002, W4B-D1 to W4B-D3)"
GEN_WHAT = ("%s re-read %s: three circuit changes and nothing else: W4B-D1, the RockBLOCK's I_EN (J_RB9704 pin 3) is RB_IEN = "
            "EMCON_HW AND RB_SW_IEN in U536 (SN74LVC1G08), U6 pin 19 now drives the request RB_SW_IEN, R527 10 k holds RB_IEN "
            "low and R528 4.7 k the request (line %d); W4B-D2, the enables of U23, U24 and U21 sit at 0.6 of their gates' "
            "outputs (R529 to R531 10 k 1 percent, R514 to R516 now 15 k 1 percent, nodes LIME_UVLO, RB_UVLO, E22_UVLO), with "
            "the three rails' intent naming their switch and enable net; W4B-D3, each slot's card buck enable S{s}A_EN is "
            "driven by U{s}16 (SN74LV1T08 on +5V_S{s}) = EMCON_HW AND PCIE_PWR_EN{s}, R{s}64 removed and U{s}15's second "
            "channel freed (2A on GND, 2Y open); lines above each cited range moved; at integration its comments' two "
            "maker-document paths point at v2/vendor/ and the RockBLOCK request's firmware duty names the panel "
            "firmware (comments only)" % (GEN, W4B, U536))
NET_WHAT = ("%s regenerated %s on the KiCad box with main's chain (main's own generator reproduces main's committed schematic "
            "PARITY and netlist, intent, provenance and ERC PARITY_AFTER_NOISE, BOM PARITY) and compared by the integration's "
            "own comparator (v2/docs/records/r8b/integration/indep_cmp.py) record by record and net by net: 13 parts added "
            "(U536, C559, R527 to R531, U116, U216, U316, C607, C637, C667), 3 removed (R164, R264, R364), 6 changed (R514 "
            "to R516's value and code, U115, U215 and U315's value text), 7 nets added (RB_SW_IEN, LIME_UVLO, RB_UVLO, "
            "E22_UVLO and the three freed U{s}15 pin 4 nets) and 19 changed, 0 unexplained against "
            "v2/docs/records/w4b/expected_w4b.json and refused when any decision's entries are dropped" % (NET, W4B))
PAN_WHAT = ("%s re-read %s with its page drafts applied (v2/docs/records/w4b/page_drafts_w4b.py): two places change, section "
            "6's EMCON_HW row (the three switch enables at 0.6 of their gates, U536 on the RockBLOCK's ENABLE, the card "
            "supplies' enables driven by U116, U216 and U316 from each slot's 5 V, where it said U115, U215 and U315 pulled "
            "them) and a new correction block (17) after (16); every other line is byte-identical" % (PAN, W4B))
EMC_WHAT = ("%s re-read %s with its page drafts applied (v2/docs/records/w4b/page_drafts_w4b.py): section 4c is new (the "
            "RockBLOCK's ENABLE, L4 case (2) on U501 to U504, fault F2 on the card rails, L2 with the new readers at 0.58 V, "
            "and RF-002's walk with and without the tool rows drafted for the tools author); section 0 gains one bullet; "
            "section 0a's rows 4 to 7, 14, 15 and 16 and 17, section 7's L4 and RockBLOCK rows and section 8's board B and "
            "tools hand-offs change, and section 6's bench row E-04 names the ENABLE request RB_SW_IEN where it said U6 "
            "drove RB_IEN (the independent check's correction, applied at the r8int6 integration); sections 1 to 4b, 5 "
            "and 5a are byte-identical, and section 6 is but for row E-04" % (EMC, W4B))

TAIL = {
 # gen_sch_b.py
 ("CHO-001", GEN): ": the device set is untouched (no device part added, removed or re-coded; the new parts are logic gates "
                   "and passives: U536 an SN74LVC1G08 on the code the set already buys, C7666, and U116, U216, U316 an "
                   "SN74LV1T08 on C2682144, which JLCPCB answered as 'SN74LV1T08DBVR, Texas Instruments, SOT-23-5', stock "
                   "7,904, on 27 September 2026, v2/docs/records/w4b/evidence/jlc-query-sn74lv1t08.txt, not yet in the certification "
                   "table), J_M2C2 is still on the key-B land at line %d and U9 is still the DS3231SN#, so the land half stays "
                   "closed at desk and the certification half stands, on the file at %s" % (M2B, NEW[GEN]),
 ("CON-017", GEN): ": U41, U51 and U61 are still STM32H743VIT6 (C114409) with the same pin table (line %d) and none of the "
                   "stream's changes touches a supervisor pin or its supply, so this reading stands INCONCLUSIVE on the file "
                   "at %s" % (IOC, NEW[GEN]),
 ("CFL-001", GEN): ": the ring is still f = s %% 3 + 1, now at line %d, and nothing of the bank fabric changed, so it stands "
                   "PASS on the file at %s" % (RING, NEW[GEN]),
 ("CFL-004", GEN): ": the block this reading cites is now at lines %d to %d; its WL_nDIS and BT_nDIS lines are byte-identical "
                   "(pulled low only through U113 and U114 and their slot 2 and 3 copies, run from +3V3_CM{s}; U6 drives only "
                   "the requests), and within it only U{s}15's call changes (its second channel freed, W4B-D3) and one comment "
                   "line is added, so it stands PASS on the file at %s" % (EMC0, EMC1, NEW[GEN]),
 ("REQ-052", GEN): ": the hub ports (PORTS, line %d), the bank ring (f = s %% 3 + 1, line %d) and the LoRa module on S3's SPI "
                   "(U12, line %d) are unchanged; the stream moves no device between banks, so the reading stands FAIL on the "
                   "file at %s" % (PORTS, RING, U12, NEW[GEN]),
 ("CON-025", GEN): ": the SIM block is at lines %d to %d and byte-identical (the holders, the 0 Ohm links, U222 and U223), so "
                   "the schematic half stands PASS on the file at %s" % (SIM0, SIM1, NEW[GEN]),
 ("CON-015", GEN): ": J_M2C2's socket, land and pin map are unchanged (line %d), so the land clause holds at desk and D-07's "
                   "third jack still waits, on the file at %s" % (M2B, NEW[GEN]),
 # the netlist
 ("CHO-001", NET): "; no device changes, so this reading stands on the file at %s",
 ("CON-003", NET): "; R480 to R500, R15 and R16 are still 10 k and the lock, arm and motion parts sit where FAILOVER-FABRIC.md "
                   "section 9a says; the stream touches no part or net of the fabric, so this reading stands on the file at %s",
 ("CON-022", NET): "; PG1 to PG3, their buffers and the qualifier muxes are on it unchanged, and the one new reader of a module "
                   "pin, U{s}16 on PCIE_PWR_EN{s} (a module output), is an input (II +-1 uA at VCC 0 to 5.5 V, TI SCLS739F "
                   "6.5) that drives nothing into the module, so this reading stands on the file at %s",
 ("CON-017", NET): "; U41, U51 and U61's pins are on the same nets, so this reading stands INCONCLUSIVE on the file at %s",
 ("REQ-030", NET): "; the RockBLOCK's ENABLE, the three switch enables and the card bucks' enables change (EMCON.md 4c), and "
                   "tools/tx_inhibit.py, with the rows that land in the same integration, read board B's walk FAIL 1, PASS 15, "
                   "UNDECIDED 4 in the stream's re-take in scratch (the FAIL TX_INHIBIT_n's W3T-F1; FAIL 11, PASS 3, "
                   "UNDECIDED 6 without them), so this reading stands FAIL on the file at %s",
 ("REQ-071", NET): "; RB_IEN now joins J_RB9704 pin 3, U536's output and R527 (U6 pin 19 drives RB_SW_IEN), so row 4's "
                   "ENABLE is forced low by hardware, and each card buck's enable is driven from its slot's 5 V (fault F2); "
                   "row 4's latency waits on the Iridium 9704's unpublished response to ENABLE and every row on its bench "
                   "test, so this reading stands FAIL on the file at %s",
 ("CFL-004", NET): "; WL_nDIS1..3 and BT_nDIS1..3 carry the same nodes, so this reading stands PASS on the file at %s",
 ("REQ-032", NET): "; every radio's hardware path is kept or strengthened (EMCON.md 4c) and the walk, with the rows that land "
                   "in the same integration, still read board B FAIL in the stream's re-take (TX_INHIBIT_n's W3T-F1), so "
                   "this reading stands FAIL on the file at %s",
 ("FEA-002", NET): "; the RockBLOCK's ENABLE is forced low by hardware and the card rails hold in fault F2 (EMCON.md 4c); the "
                   "RockBLOCK row stays open on its module's unpublished response to ENABLE, so this reading stands "
                   "INCONCLUSIVE on the file at %s",
 ("CFL-016", NET): "; the documents this reading binds are re-read with the stream's page drafts: PANEL.md section 6's "
                   "EMCON_HW row now names U116, U216 and U316 for the card supplies' enables, U536 and the three dividers, "
                   "which is the circuit as generated, so this reading stands PASS on the file at %s",
 ("CON-015", NET): "; J_M2C2's nets are unchanged, so this reading stands on the file at %s",
 ("CON-016", NET): "; board B's six one-way clamps (D1, D2, D101, D201, D301, D520) are unchanged, port_protect reads 0 "
                   "reversed on it and the stream adds no rectifier, so the record stays FAIL on the rectifier clause, on the "
                   "file at %s",
 # PANEL.md
 ("CFL-001", PAN): "; line 5 (bank 1's home and failover hosts), section 1 and section 2's ribbon table with its pin 15 row, "
                   "which this reading rests on, are byte-identical, so it stands PASS on the file at {NEW}",
 ("CFL-005", PAN): "; section 7's panel-absent paragraph, which this reading cites, is byte-identical, so it stands PASS on "
                   "the file at {NEW}",
 ("CFL-016", PAN): "; the changed row is section 6's, which this record's acceptance asks to describe the circuit as "
                   "generated, and it now describes board B's w4b netlist, where it named U115, U215 and U315 for the card "
                   "supplies' enables; section 1 is byte-identical, so it stands PASS on the file at {NEW}",
 ("CFL-014", PAN): "; section 10, which this reading cites, is byte-identical, so it stands PASS on the file at {NEW}",
 ("CFL-015", PAN): "; section 10's SMBus sentences, which this reading cites, are byte-identical, so it stands PASS on the file "
                   "at {NEW}",
 # EMCON.md
 ("REQ-012", EMC): "; the TX lamp's rows (section 4.1's and 4.2's lamp text, section 6's E-02) are byte-identical, so this "
                   "reading stands FAIL on the file at {NEW}",
 ("REQ-030", EMC): "; the page still closes no row end to end (section 0a), so this reading stands FAIL on the file at {NEW}",
 ("REQ-071", EMC): "; row 4 is still open locally (the module's response to ENABLE unpublished) and no row meets section 5a on "
                   "the bench, so this reading stands FAIL on the file at {NEW}",
 ("REQ-032", EMC): "; D-05's radios-dark rows keep their open items (section 0a), so this reading stands FAIL on the file at "
                   "{NEW}",
 ("CON-010", EMC): "; sections 4.2 and 4a (the PA's VGG and D's KEY gate), which this reading cites, are byte-identical, so it "
                   "stands FAIL on the file at {NEW}",
 ("CON-021", EMC): "; SD-EMC-6 and the lamp's rows (sections 0, 5 and 7) are unchanged but for section 7's L4 and RockBLOCK "
                   "rows, which are not the lamp's, so this reading stands FAIL on the file at {NEW}",
 ("FEA-002", EMC): "; the feasibility verdict's conditions stand and the RockBLOCK row's remedy is drawn, so this reading "
                   "stands INCONCLUSIVE on the file at {NEW}",
}

done = []
for (rid, path), tail in TAIL.items():
    if path == GEN: note = GEN_WHAT + tail
    elif path == NET: note = NET_WHAT + (tail % NEW[NET])
    elif path == PAN: note = PAN_WHAT + tail
    else: note = EMC_WHAT + tail
    old = rebind(P, rid, path, T, note)
    done.append((rid, path, old))
    print("%-8s %-45s %s" % (rid, path, "rebound from %s" % old if old else "already current"))

s = open(P, encoding="utf-8").read()
# 2a. FEA-002's statement clause
a = ("      drawn inhibit is a firmware-mediated airplane mode, the RockBLOCK 9704 keeps running on its own supercapacitors\n"
     "      with its ENABLE held by firmware, the shared lines have open items, and no row is shown on the bench.\n")
b = ("      drawn inhibit is a firmware-mediated airplane mode, the RockBLOCK 9704 keeps running on its own supercapacitors\n"
     "      after its supply gate opens (its ENABLE forced low by hardware since stream w4b, its response to it unpublished),\n"
     "      the shared lines have open items, and no row is shown on the bench.\n")
assert s.count(a) == 1, "FEA-002's statement is not the one this script was written against"
# r8int6: FEA-002's statement is part of the requirements baseline since layer 3's re-baseline (a54b793b, fnd/l3rb):
# "a later change to a record's statement ... is a change to the baseline and needs its own review; readings, notes and
# open items move without one" (the registry header). The clause is therefore not rewritten here; the rebind notes say
# the RockBLOCK row's remedy is drawn, and the stale clause is carried as an open item with the layer 1 and 2 pages'
# matching lines (v2/docs/records/r8int6/layers_r8int6.py).
# 2b. S-01 restated
i, j = _rec(s, "S-01"); r = s[i:j]
a = ("      stages; L1 remedied on boards B and C, L2 on boards A and B, L3 and L7 on board B, L4 on boards A and D): L4 case\n"
     "      (2), the gate supplies of U501 to U505 below their specified range on board B (bench E-11), and the back-feed\n")
b = ("      stages; L1 remedied on boards B and C, L2 on boards A and B, L3 and L7 on board B, L4 on boards A and D, and on\n"
     "      board B's U501 to U504 by stream w4b's enable dividers, EMCON.md 4c): L4 case (2) on U536, the RockBLOCK's ENABLE\n"
     "      gate, below its specified range with +5V_RB off there (bench E-11), the Iridium 9704's response to its ENABLE (a\n"
     "      maker's document owed; the ENABLE itself is forced low by hardware since stream w4b), and the back-feed\n")
assert r.count(a) == 1, "S-01's title is not the one this script was written against"
r = r.replace(a, b)
a = "      unchanged.\n"
b = ("      unchanged. Restated again by stream w4b (27 September 2026): the RockBLOCK's ENABLE and L4 case (2) on U501 to\n"
     "      U504 are drawn, and each slot's card supply enable is driven from its own 5 V (fault F2, EMCON.md 4c).\n")
assert r.count(a) == 1
r = r.replace(a, b); s = s[:i] + r + s[j:]


# 3. the next free SC and S numbers of this tree
def next_id(prefix):
    nums = [int(m) for m in re.findall(r"\n  - id: %s-(\d+)\n" % prefix, s)]
    return "%s-%02d" % (prefix, max(nums) + 1)


SCS = []
for key, q, taken, why, src in (
    ("W4B-D1",
     "How does EMCON reach the RockBLOCK 9704's ENABLE (J3 pin 3, I_EN), which U6 held alone while the module runs on its own "
     "supercapacitors after its supply gate opens (EMCON.md 4.4, 5a row 4)?",
     "RB_IEN = EMCON_HW AND RB_SW_IEN in U536, an SN74LVC1G08 on +3V3_DEV (Ioff stated), with R527 10 k holding RB_IEN low "
     "unpowered and R528 4.7 k holding U6's request low at power-on; the module's shutdown order (Ground Control's I_EN/I_BTD "
     "warning) is met by an EMCON during boot the way the maker's own divider meets every loss of external power, accepted as "
     "a stated residual; the panel firmware keeps the request low after an EMCON until RB_STATUS reads low (PANEL.md "
     "correction (17), HW-FW-CONTRACT.md FW-B13; the stream wrote 'the bridge', corrected at integration).",
     "Ground Control states I_EN initiates startup and shutdown and 'can be driven directly with an MCU pin, or an open-drain "
     "output' (hardware page, 27 September 2026; schematic rev 2B page 3). A single gate with Ioff is the part and the idiom "
     "board B's other enables already use (L2, L3). Options weighed: an open drain from EMCON_ON (fails with the module's "
     "rail, and a pull-up to the module's pre-cap supply is the maker's own); a gate on the supply rail (none is live under "
     "EMCON); the AND taken. Reversal: U6 pin 19 back on RB_IEN, U536, C559, R527 and R528 out.",
     ["v2/ecad/tools/gen_sch_b.py (U536, R527, R528; the comment block at the EMCON gates)", "v2/docs/feasibility/EMCON.md 4.4, 4c"]),
    ("W4B-D2",
     "How is L4 case (2) closed on U501 to U504, whose outputs are unspecified while +3V3_DEV is between 0 and 1.65 V and whose "
     "switches' turn-off thresholds are 1.08 V (EMCON.md section 3 L4, 5a fault F6)?",
     "Each switch's EN/UVLO on its own node at 0.6 of the gate's output: R529 to R531 10 k 1 percent in series, R514 to R516 "
     "15 k 1 percent to GND (LIME_UVLO, RB_UVLO, E22_UVLO), board A's SD-A8-3 values and codes; U505 needs none (its switch's "
     "input is +3V3_DEV).",
     "At the gate's 1.65 V band edge the node is at most 0.998 V, under VUVLO(F) and VENF 1.08 V minimum (SLVSET8A 7.5, "
     "SLVSDH0C 7.5); driven high it is at least 1.43 V (VOH 2.4 V, SCES217AA 5.5), over 1.22 V and 1.30 V maximum; unpowered "
     "0.15 V under VSD and VSHUTF. Options weighed: a supervisor on +3V3_DEV holding the enables (another part and its own "
     "band), a gate supply that is either up or zero (a switch's discharge still crosses the band); the divider taken, as on "
     "board A. Reversal: the enables back on the gate outputs, R514 to R516 at 10 k, R529 to R531 out.",
     ["v2/ecad/tools/gen_sch_b.py (R514 to R516, R529 to R531)", "v2/docs/feasibility/EMCON.md section 3 L4, 4c"]),
    ("W4B-D3",
     "What holds each card buck's enable (S{s}A_EN) off under EMCON when the module's own 3.3 V, which runs U{s}15, is down "
     "and the slot's 5 V is up (EMCON.md 5a fault F2; found by RF-002's walk once it read the SN74LVC2G06)?",
     "U{s}16, an SN74LV1T08 run from +5V_S{s}, the buck's own input, drives S{s}A_EN = EMCON_HW AND PCIE_PWR_EN{s} "
     "push-pull; R{s}64 is removed and U{s}15's second channel freed (2A on GND, 2Y open).",
     "The AP64500's EN sources 1.5 uA and, once on, 4 uA more, 5.5 uA typical with no maximum (DS41979), so 110 k could not "
     "be shown to turn a running buck off, and on slot 2 that is the RM520N-GL with its own firmware. A gate powered from the "
     "buck's own input has no unpowered state that matters and leaves no resistor for the EN current to lift (VOL 0.35 V at "
     "8 mA, SCLS739F 6.5); the LV1T08 reads a 3.3 V signal from a 5 V supply (VIH 2.03 V, VIL 0.8 V) with 5.5 V tolerant "
     "inputs (II +-1 uA at VCC 0 to 5.5 V). Options weighed: a stiffer pull-down (margin, not a stated bound); keeping U{s}15's "
     "2Y beside the gate through R{s}64 (the resistor brings the unbounded current back); the direct gate taken. What is given "
     "up: a second EMCON path onto the node that failed in exactly this state. Reversal: R{s}64 from PCIE_PWR_EN{s} to "
     "S{s}A_EN, U{s}15's 2Y back, U{s}16 out.",
     ["v2/ecad/tools/gen_sch_b.py (U116, U216, U316; the comment block at the card buck)", "v2/docs/feasibility/EMCON.md 4c"])):
    sc = next_id("SC")
    blk = ("  - id: %s\n    authority: SESSION\n    under: standing-rule\n    taken_on: \"2026-09-27\"\n    question: >-\n%s"
           "    taken: >-\n%s    why: >-\n%s    source:\n%s"
           % (sc, wrap(q, "      ", "      ", 118), wrap(taken, "      ", "      ", 118), wrap("%s (stream w4b). %s" % (key, why), "      ", "      ", 118),
              "".join('      - "%s"\n' % x for x in src)))
    anchor = "\n# What is still open."
    assert s.count(anchor) == 1
    s = s.replace(anchor, "\n" + blk.rstrip("\n") + "\n" + anchor, 1)
    SCS.append((key, sc))
    print("added", sc, "for", key)

sid = next_id("S")
title = ("RF-002's instrument after stream w4b (27 September 2026): the rows board B's circuit needs landed with it "
         "(tools/tx_inhibit.py from v2/docs/records/w4b/tools/apply_tx_inhibit_w4b.py and apply_tx_inhibit_tests_w4b.py: "
         "the SN74LVC2G06 and SN74LV1T08 rows, the AO3400A read as an N-channel FET, U221 and J_QMX in ACCESSORIES, a "
         "VCC-band VIL field; without them the walk read board B FAIL 11, PASS 3, UNDECIDED 6 and boards A and C one "
         "UNDECIDED more each), and with them the stream's re-take in scratch read board B FAIL 1 (TX_INHIBIT_n, W3T-F1), "
         "PASS 15, UNDECIDED 4, the four UNDECIDED on three classes the walk does not read: a "
         "TPS3808 supervisor on the rail it watches (U221), a USBLC6-2's VBUS beside a USB hub's pins (U33 on +5V_LIME), and "
         "declared bench headers and CP2102N pulls on a gated rail (+3V3_ZB). The last two are also SD-EMC-2's back-feed (S-01).")
blk = "  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % (sid, wrap(title, "      ", "      ", 118))
anchor = "\n# Items that left the open list"
assert s.count(anchor) == 1
s = s.replace(anchor, "\n" + blk.rstrip("\n") + "\n" + anchor, 1)
print("added", sid)
open(P, "w", encoding="utf-8").write(s)
print("choices:", SCS, "open item:", sid, "rebinds:", len(done))
