#!/usr/bin/env python3
"""Stream w3b (MESHSAT-1357, 27 September 2026): the registry changes of board B's PWR-001 declarations, decision 42 classes,
W3B-F1 (the TPS23861's RSENS and RDRAIN) and W3B-F2 (the LG290P's V_BCKP capacitors), for the integrator to run on the tree
the stream's files are committed in. Edits v2/ecad/tools/pcb_requirements.yaml as text (its own formatting kept), by record id,
with every old text asserted; the new shas are read from that tree, never typed. Usage: apply_registry.py <repo root>

What it does:
  1. Re-reads and rebinds every record bound to gen_sch_b.py@af6e5821e21b70ef (CHO-001, CON-017, CFL-001, CFL-004, CFL-010,
     CON-015) or to pcb-b-compute.net@adcc3c6736c90e9f (those four of them and CON-003, CON-016, CON-022, CFL-016, FEA-002,
     REQ-030, REQ-032, REQ-071), each with a note naming what changed and the unchanged parts its statement rests on (the
     integration recipe: a changed bound file is re-read and rebound; rules_lib.py requirements lists them).
  2. Adds CFL-010's certification reading of the SIM TVS arrays (jlc_certify's own certify(), 27 September 2026).
  3. Rewords open item S-13 to what is still open (the eSIM variant's order code).
  4. Adds three findings as open items, taking the next free S numbers of the tree it is applied to.

r8int5 INTEGRATION COPY (27 September 2026, on main 953f5658 with the w3t and w3a commits): r8int4 resolved CFL-010 on
V2-SPEC and moved the SIM TVS clause to CON-025 (bound to gen_sch_b.py) and reworded S-13, so step 2's certification
reading goes to CON-025 and step 3 is not applied; REQ-052 (bound to gen_sch_b.py since r8int4) is re-read; the new
open items go at the end of open_items (the S-47 anchor would have put them out of order); CON-017's citation is Table
122 on p.212 (the independent check); W3B-B and W3B-C carry the check's missed items (the LG290P's VCC, the TPS23861's
per-port parts, the RM520N's USIM trace width)."""
import hashlib, os, re, sys

T = sys.argv[1]; P = os.path.join(T, "v2/ecad/tools/pcb_requirements.yaml")
h16 = lambda p: hashlib.sha256(open(os.path.join(T, p), "rb").read()).hexdigest()[:16]
GEN, NET = "v2/ecad/tools/gen_sch_b.py", "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net"
OLD = {GEN: "af6e5821e21b70ef", NET: "adcc3c6736c90e9f"}
NEW = {GEN: h16(GEN), NET: h16(NET)}
import json as _json
_it = _json.load(open(os.path.join(T, "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json")))
N_RAILS, N_NODES = len(_it["rails"]) - 41, len(_it["nodes"]) - 114   # main 38dcd764's intent: 41 rails, 114 nodes
assert N_RAILS > 0 and N_NODES > 0 and all(e.get("class") and e.get("basis") for e in _it["bypass"])
assert NEW[GEN] != OLD[GEN] and NEW[NET] != OLD[NET], "the stream's files are not in this tree"
s = open(P, encoding="utf-8").read()
W3B = "at stream w3b's merge of 27 September 2026 (MESHSAT-1357, board B: PWR-001 declarations, decision 42 classes, W3B-F1, W3B-F2)"
GEN_WHAT = ("%s re-read %s: the generator gains intent declarations only (%d rails and %d nodes for PWR-001, each with its "
            "maker's figure; the +54V_POE load list names R13 and U5's own 7 mA; U11's +3V3_DEV load is the LG290P's 135 mA "
            "peak plus its antenna's 30 mA), the decision 42 class and basis on every decoupling entry, and two circuit "
            "changes: W3B-F1, RSENS R525 (22 Ohm) and RDRAIN R526 (47 Ohm) between the TPS23861's SEN1 and DRAIN1 and the port "
            "(SLUSBX9I p.5, 6.5), and W3B-F2, C72 to C74 (4.7 uF, 100 nF, 33 pF) at the LG290P's V_BCKP (hardware design V1.1 "
            "3.2.2); and W3B-R1, the coin-cell net VBAT renamed VBAT_RTC (board A's pack node is VBAT, and the contracts key "
            "a rail by its name); lines above each cited range moved" % (GEN, W3B, N_RAILS, N_NODES))
NET_WHAT = ("%s regenerated %s on the KiCad box with main's chain (main's own generator reproduces main's committed schematic, "
            "netlist, intent, provenance, BOM and ERC: PARITY or PARITY_AFTER_NOISE) and compared by the integration's own "
            "comparator (v2/docs/records/r8b/integration/indep_cmp.py) record by record and net by net: 5 parts added (R525, "
            "R526, C72, C73, C74), 1 part changed (TP6's value, the net it names), 3 nets added (POE_SEN_PIN, POE_DRAIN_PIN, "
            "VBAT_RTC), 1 removed (VBAT), 3 changed (POE_SEN and POE_DRAIN by U5 leaving and R525 or R526 joining, GND by C72 "
            "to C74 joining), 0 unexplained against v2/docs/records/w3b/expected_w3b.json and 2 unexplained when W3B-F1's parts "
            "are dropped from it; VBAT_RTC carries every node VBAT carried plus C72 to C74 pin 1 "
            "(v2/docs/records/w3b/tools/rename_check.py)" % (NET, W3B))


def line_of(pattern, occurrence=1):
    """The 1-based line of a pattern in the tree's gen_sch_b.py, so a note cites the committed file and not a typed number."""
    L = open(os.path.join(T, GEN), encoding="utf-8").read().split("\n")
    hits = [i + 1 for i, l in enumerate(L) if re.search(pattern, l)]
    assert len(hits) >= occurrence, pattern
    return hits[occurrence - 1]


RING = line_of(r"^\s+f = s % 3 \+ 1$")
EMC0, EMC1 = line_of(r"# L3 and L7 \(round 8, EMCON\.md section 3"), line_of(r"# PEWAKE# through R232")
SIM0, SIM1 = line_of(r"# S-13, 26 September 2026: each SIM per HD v1.1 Figure 18"), line_of(r'_intent\.node\(cd\(x\), 3\.3, "a SIM card line at the holder')
M2B = line_of(r'part\("J_M2C2", "Connector", "Bus_M\.2_Socket_B"')
IOC = line_of(r'synth\(U_\(1\), "STM32H743VI"')
EV = {
 "CHO-001": [GEN_WHAT + ": the device set is untouched (no device part added, removed or re-coded; the five new parts are "
             "passives), J_M2C2 is still on the key-B land at line %d and U9 is still the DS3231SN#, so the land half stays closed "
             "at desk and the certification half stands, on the file at %s" % (M2B, NEW[GEN]),
             NET_WHAT + "; no device changes, so this reading stands on the file at %s" % NEW[NET]],
 "CON-017": [GEN_WHAT + ": U41, U51 and U61 are still STM32H743VIT6 (C114409) with the same pin table (line %d); the stream "
             "adds the declarations of their VCAP (a node, VCORE at most 1.40 V, DS12110 Rev 10 p.27 and Table 122 on p.212; the generator's comment and node basis "
             "cite Table 123, a slip the independent check found) and NRST (a "
             "node at the controller's 3.3 V) and the classes of their capacitors, none of which moves a pin, so clauses (1) and "
             "(2) hold and (3) and (4) still cannot be decided, on the file at %s" % (IOC, NEW[GEN]),
             NET_WHAT + "; U41, U51 and U61's pins are on the same nets, so this reading stands INCONCLUSIVE on the file at %s"
             % NEW[NET]],
 "CFL-001": [GEN_WHAT + ": the ring is still f = s %% 3 + 1, now at line %d, and nothing of the bank fabric changed, so it "
             "stands PASS on the file at %s" % (RING, NEW[GEN])],
 "CFL-004": [GEN_WHAT + ": the block this reading cites is byte-identical and now at lines %d to %d (WL_nDIS and BT_nDIS "
             "pulled low only through U113 to U115 and their slot 2 and 3 copies, run from +3V3_CM{s}; U6 drives only the "
             "requests), so it stands PASS on the file at %s" % (EMC0, EMC1, NEW[GEN]),
             NET_WHAT + "; WL_nDIS1..3 and BT_nDIS1..3 carry the same nodes, so this reading stands PASS on the file at %s"
             % NEW[NET]],
 "CON-025": [GEN_WHAT + ": the SIM block is at lines %d to %d; the holders, the 0 Ohm links and the TVS arrays U222 and "
             "U223 are unchanged, and the stream adds only the SIM supplies' rail declarations (SIM1_VCC, SIM2_VCC, SIMC2_VCC). "
             "The arrays re-read %s: TI TPD4E001DBVR, 1.5 pF typical (CI/O, SLLS682P; v2/vendor/ti/ti-tpd4e001.pdf), and "
             "tools/jlc_certify.py's own certify() on the two BOM rows (value, SOT-23-6 land, C465736, quantity 1 each) reads "
             "CERTIFIED: model TPD4E001DBVR, Texas Instruments, SOT-23-6, stock 17,211 against 5 needed, asked 27 September 2026 "
             "(v2/docs/records/w3b/evidence/jlc-certify-w3b.txt), a catalogue reading and not a grade; so it stands PASS on the "
             "file at %s" % (SIM0, SIM1, W3B, NEW[GEN])],
 "REQ-052": [GEN_WHAT + ": the hub ports, the bank ring (f = s %% 3 + 1, now at line %d) and the LoRa module on S3's SPI (J_SPI3, "
             "U12) are unchanged; the stream moves no device between banks, so the reading stands FAIL on the file at %s"
             % (RING, NEW[GEN])],
 "CON-015": [GEN_WHAT + ": J_M2C2's socket, land and pin map are unchanged (line %d), so the land clause holds at desk and "
             "D-07's third jack still waits, on the file at %s" % (M2B, NEW[GEN]),
             NET_WHAT + "; J_M2C2's nets are unchanged, so this reading stands on the file at %s" % NEW[NET]],
}
_NET_STANDS = NET_WHAT + "; %s, so this reading stands on the file at %s"
EV.update({
 "CON-003": [_NET_STANDS % ("R480 to R500, R15 and R16 are still 10 k on it and the lock, arm and motion parts sit where "
                            "FAILOVER-FABRIC.md section 9a says; the stream touches no part or net of the fabric", NEW[NET])],
 "CON-022": [_NET_STANDS % ("PG1 to PG3, their buffers and the qualifier muxes are on it unchanged; the stream touches no "
                            "part or net of the fabric", NEW[NET])],
 "REQ-030": [_NET_STANDS % ("no EMCON or TX_INHIBIT_n net or part changed, and tools/tx_inhibit.py on it with main's A, C "
                            "and D netlists reads board B's walk as before (inhibit_chain_b FAIL 10, PASS 3, UNDECIDED 7)",
                            NEW[NET])],
 "REQ-032": [_NET_STANDS % ("no EMCON net, radio enable or radio supply switch changed (the SIM and GNSS antenna supplies "
                            "gained declarations only), and tools/tx_inhibit.py reads board B's walk as before (inhibit_chain_b "
                            "FAIL 10, PASS 3, UNDECIDED 7)", NEW[NET])],
 "REQ-071": [_NET_STANDS % ("RB_IEN still joins J_RB9704 pin 3 and U6 pin 19 only", NEW[NET])],
 "FEA-002": [_NET_STANDS % ("no transmitter's inhibit chain changed, and tools/tx_inhibit.py reads board B's walk as before "
                            "(inhibit_chain_b FAIL 10, PASS 3, UNDECIDED 7)", NEW[NET])],
 "CFL-016": [_NET_STANDS % ("the documents this reading binds describe nothing the stream changed (their VBAT is board A's "
                            "pack node; the TPS23861's sense wiring, the V_BCKP capacitors and the coin-cell net's name appear "
                            "in none of them)", NEW[NET])],
 "CON-016": [_NET_STANDS % ("board B's six one-way clamps (D1, D2, D101, D201, D301, D520) are unchanged, port_protect reads "
                            "0 reversed on it and the stream adds no rectifier, so the record stays FAIL on the rectifier "
                            "clause", NEW[NET])],
})


def wrap(n):
    out, cur = [], ""
    for w in n.split():
        if len(cur) + len(w) + 1 > 106: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    out.append(cur)
    return "      - >-\n" + "".join("          %s\n" % l for l in out)


def block(rid):
    m = re.search(r"^  - id: %s\n.*?(?=^  - id: |^[a-z_]+:\n|\Z)" % re.escape(rid), s, re.S | re.M)
    assert m, rid
    return m


for rid, notes in EV.items():
    m = block(rid); b = m.group(0)
    assert "\n    evidence_bound_to:" in b, rid   # r8int5: block or flow list
    _bound = [p_ for p_ in (GEN, NET) if ('"%s@%s"' % (p_, OLD[p_])) in b]
    assert _bound, (rid, "carries neither old binding")
    i = b.index("\n    evidence_bound_to:") + 1
    b2 = b[:i] + "".join(wrap(n) for n in notes) + b[i:]
    for path in (GEN, NET):
        b2 = b2.replace('"%s@%s"' % (path, OLD[path]), '"%s@%s"' % (path, NEW[path]))
    assert b2 != b
    s = s[:m.start()] + b2 + s[m.end():]

# 3. S-13: not applied at r8int5 (r8int4 reworded it and moved the TVS clause to CON-025)

# 4. three findings, at the next free S numbers of this tree
used = sorted(int(x) for x in re.findall(r"^  - id: S-(\d+)$", s, re.M))
nxt = iter(range(used[-1] + 1, used[-1] + 10))
FIND = [
 "Finding W3B-A (stream w3b, 27 September 2026; board B): the LG290P's active antenna feed departs from Quectel's reference "
 "(LG290P(03) hardware design V1.1 5.2, Figure 17, p.35): the bias inductor L3 is 27 nH where \"The recommended value of L1 "
 "should be at least 68 nH\"; the maker's C4 (100 pF) and C5 (100 nF) at the feed are not drawn (GNSS_BIAS and GNSS_VDD_RF carry "
 "no capacitor); no ESD device D1 (\"junction capacitance ... cannot be more than 0.6 pF and a transient voltage suppressor is "
 "recommended\") is on the antenna input; and the DC block C42 is 47 pF where the maker's C1 is 100 pF. R23 (10 Ohm, the maker's "
 "R2) is as drawn. The antenna's own current is held in no document (20 mA typical and 30 mA peak are INFERRED in gen_sch_b.py's "
 "GNSS_VDD_RF declaration). Open until board B's generator carries the feed as Figure 17 draws it, with an inductor and an ESD "
 "part whose datasheets are held and whose self-resonance and capacitance are read at L1 to L5, or a written deviation with its "
 "reason, and the kit antenna's current is read from its maker.",
 "Finding W3B-B (stream w3b, 27 September 2026; board B): W3B-F2 draws the LG290P's recommended 4.7 uF, 100 nF and 33 pF at "
 "V_BCKP but not the TVS the same sentence recommends (hardware design V1.1 3.2.2, p.25): the maker's figures feed V_BCKP from an "
 "always-on supply or an LDO, board B from its on-board CR2032 BT1, and a TVS pick needs a held datasheet and a standby leakage "
 "the cell can carry. With it, the coin cell's drain: VBAT_RTC (VBAT until W3B-R1) feeds three CM5 RTCs (6 uA each unpowered, CM5 datasheet Table 9), "
 "the DS3231SN (3.0 uA maximum, 19-5170 Rev 10) and the LG290P's backup domain (12 uA typical and 57 uA maximum in Backup mode, "
 "Table 11), about 31 uA typical and 78 uA worst with the kit stored, against a cell whose capacity no held document states. Open "
 "until the TVS is picked or ruled out with its reason and the stored life is computed from a held CR2032 datasheet and carried "
 "into CONOPS's storage scenario. The same reading's paragraph before it (3.2.1, p.24; the independent check) recommends a "
 "TVS plus 10 uF, 100 nF and 33 pF at VCC pin 23, smallest closest, advises against a switching DC-DC and asks for an "
 "MCU-controlled VCC: board B has C40 (100 nF) and C41 (10 uF) on +3V3_DEV not declared against U11 pin 23, no 33 pF, no TVS, "
 "and feeds VCC from the always-on AP63203 buck; recorded with this item.",
 "Finding W3B-C (stream w3b, 27 September 2026; board B): two TPS23861 items W3B-F1 does not close. C34 (100 nF 100 V on "
 "+54V_POE) is the capacitor TI asks at VPWR (\"Bypass VPWR to AGND using a 0.1-uF capacitor\", SLUSBX9I p.5) and is not declared "
 "against U5 pin 28, so DEC-001 will not seat it (a declaration moves the sheet layout, left to board B's next circuit round); and "
 "KSENSA (pin 18, \"Kelvin point connection for SEN1 and SEN2\") is on GND in the schematic, so its Kelvin tap at R12's ground pad "
 "is a layout constraint for v2/docs/layout-constraints/B.md. The independent check found more of the same reading (SLUSBX9I "
 "8.3.4.2, p.90): TI's per-port parts CPn (0.1 uF 100 V from VPWR to the port negative, +54V_POE to POE_DRAIN), the port TVS DPnA "
 "(58 V standoff, 95 V maximum clamp, across the port) and the port fuse FPn are absent; Q1 (CSD19532Q5B) departs from TI's QPn "
 "guidance (CISS under 2000 pF, QG under 50 nC at 12.5 V) with Ciss 3700 pF typical and Qg 48 nC at 10 V typical (62 maximum); "
 "RDRNn and RSENn go near QPn's drain and source (layout constraints); and the RM520N HD 4.1.7 asks USIM_VDD and ground traces of "
 "at least 0.5 mm, which the SIM rails' 50 mA declarations do not carry. None was introduced by w3b. Open until C34 is declared, "
 "the per-port parts are drawn or a deviation is written with its reason, and the constraints are written.",
]
anchor = "\n# Items that left the open list"          # r8int5: the end of open_items, so the new items follow the last one
assert s.count(anchor) == 1
j = s.index(anchor)
ins = ""
for t in FIND:
    n = next(nxt)
    body, cur = [], ""
    for w in t.split():
        if len(cur) + len(w) + 1 > 112: body.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    body.append(cur)
    ins += "  - id: S-%d\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % (n, "".join("      %s\n" % l for l in body))
    print("open item S-%d: %s" % (n, t[:70]))
s = s[:j] + ins + s[j:]
open(P, "w", encoding="utf-8").write(s)
print("apply_registry: %d records rebound (%s), generator %s, netlist %s" % (len(EV), ", ".join(sorted(EV)), NEW[GEN], NEW[NET]))
