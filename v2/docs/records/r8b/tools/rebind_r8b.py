#!/usr/bin/env python3
"""Board B round 8 (MESHSAT-1357): rebind the requirement readings whose bound files this round changes, each with its
re-read note. Edits pcb_requirements.yaml as text (the file's own formatting kept). Usage: rebind_r8b.py <tree>"""
import re, sys, hashlib, os
T = sys.argv[1]; P = os.path.join(T, "v2/ecad/tools/pcb_requirements.yaml")
h16 = lambda p: hashlib.sha256(open(os.path.join(T, p), "rb").read()).hexdigest()[:16]
NEW = {p: h16(p) for p in ("v2/docs/ARCH-PCB-B-IOHA.md", "v2/docs/PANEL.md", "v2/docs/CONOPS.md", "v2/docs/V2-SPEC.md",
                           "v2/ecad/tools/gen_sch_b.py", "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net")}
s = open(P).read()
R8 = "at board B's round 8 of 27 September 2026 (MESHSAT-1357, stream b)"
IOHA = ("v2/docs/ARCH-PCB-B-IOHA.md re-read %s: the round's draft adds a 'Drawn in board B's round 8' paragraph to each of "
        "section 5's items 2, 3 and 4, corrects section 6's supervisor addresses to 0x34 to 0x36 and extends the "
        "break-before-make paragraph; sections 4, 15 and 15a and line 17 are byte-identical, so this reading stands on the "
        "file at %s" % (R8, NEW["v2/docs/ARCH-PCB-B-IOHA.md"]))
PANEL_KEEP = ("v2/docs/PANEL.md re-read %s: the round's draft adds a third corrections block (items 14 to 16) after item "
              "13, a sentence to section 5's display-select rule, rewrites section 6's EMCON_HW row for board B's round-8 "
              "circuit and, in section 7, the U6 row's wording, the supervisors' row (0x34 to 0x36) and the closing "
              "paragraph's finding (closed as a firmware contract); %s is byte-identical, so this reading stands on the file "
              "at %s")
CONOPS_KEEP = ("v2/docs/CONOPS.md re-read %s: the round's draft changes the M4 paragraph's 5G sentence and section 4b's "
               "introduction, five of its rows (LimeSDR, RockBLOCK, E22, E72, the 5G module, the WiFi cards and the module "
               "radios) and its closing paragraph for board B's round-8 circuit; %s is byte-identical, so this reading "
               "stands on the file at %s")
V2_KEEP = ("v2/docs/V2-SPEC.md re-read %s: the round's draft changes lines 24, 41 and 76 and adds correction 20 (the 5G "
           "supply removal, board B's EMCON stages, the key-B land's locating holes); %s is byte-identical, so this reading "
           "stands on the file at %s")
GEN_FAB = ("v2/ecad/tools/gen_sch_b.py re-read %s: the ring is still f = s %% 3 + 1, now at line 936 (the round inserted "
           "lines above it); the round moves the bank muxes' select from BSEL{b} to its locked, Schmitt-delayed copy BSEL{b}_S "
           "and qualifies their enable with the selected module's power-good (FAB-02, FAB-03), neither of which changes which "
           "neighbour adopts a bank, so this reading stands on the file at %s" % (R8, NEW["v2/ecad/tools/gen_sch_b.py"]))
NET_DIFF = ("v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net regenerated %s on the KiCad box with main's chain and "
            "compared with main's record by record (value, footprint, fields, libsource) and net by net (ref, pin, "
            "pinfunction, pintype) by the stream's own comparator (drafts/b/tools/netdiff_r8b.py): 187 parts added, 25 "
            "removed, 36 changed, 93 nets added, 20 removed and 85 changed, every one tied to a finding of the round "
            "(v2/docs/records/r8b/r8-decisions.md; the second pass's break-before-make rework included)" % R8)
EV = {
 "CFL-001": [IOHA, PANEL_KEEP % (R8, "section 1 and the ribbon table's pin 15 row (bank 1's failover host)", NEW["v2/docs/PANEL.md"]), GEN_FAB],
 "REQ-005": [IOHA,
             CONOPS_KEEP % (R8, "section 2a", NEW["v2/docs/CONOPS.md"]),
             V2_KEEP % (R8, "line 32 (correction 6)", NEW["v2/docs/V2-SPEC.md"])],
 "CFL-005": [PANEL_KEEP % (R8, "section 7's panel-absent paragraph (R102 and R58 on EMCON_HW, R145, R59 and R2 on TX_INHIBIT_n, R117, R118, the slot enables pulled low on A22), which names no value of R58", NEW["v2/docs/PANEL.md"])],
 "CFL-013": [V2_KEEP % (R8, "line 35 and correction 8", NEW["v2/docs/V2-SPEC.md"])],
 "CFL-014": [PANEL_KEEP % (R8, "section 10", NEW["v2/docs/PANEL.md"]),
             CONOPS_KEEP % (R8, "section 4's Charging row and section 5's case S4", NEW["v2/docs/CONOPS.md"])],
 "CFL-015": [PANEL_KEEP % (R8, "section 10", NEW["v2/docs/PANEL.md"])],
 "CFL-004": [
   "v2/ecad/tools/gen_sch_b.py:820-866 read %s and the regenerated netlist v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net: "
   "WL_nDIS1 reaches only the module's pin 89 (U30A) and the open-drain outputs U113 pin 6 (input EMCON_ON1, which U112 "
   "inverts from EMCON_HW) and U114 pin 6 (input WL_nDIS1_OFF, U6's request with R162 10 k to +3V3_DEV); U112 to U115 are "
   "SN74LVC1G04 and SN74LVC2G06 run from +3V3_CM1; the same for BT_nDIS (pin 91, the parts' pin 4) and slots 2 and 3; U6 "
   "pins 13 to 18 drive only the requests, never a module pin. So each pin is pulled low only, through open-drain "
   "elements, and released only when the request and EMCON_HW both release it while its gate is powered: the "
   "acceptance holds. The gate's supply is now the module's own 3.3 V, so the unpowered-gate state that REQ-032 and "
   "FEA-002 carry releases nothing while the module runs (EMCON.md section 0a, L3). This reading stands on the "
   "generator at %s and the netlist at %s" % (R8, NEW["v2/ecad/tools/gen_sch_b.py"], NEW["v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net"]),
   NET_DIFF],
 "CFL-016": [
   PANEL_KEEP.replace("so this reading stands on the file at %s", "and sections 6 and 7 as drafted describe the circuit as generated: read against the round-8 netlist, EMCON_ON1..3 from U112, U212, U312 on each module's own 3.3 V, the open drains U113 to U115, U213 to U215, U220, U313 to U315, the single gates U501 to U505, U506 on EMCON_SUP, the 5G supply removed by U215 with Q212 and R295, and the supervisors' firmware addresses 0x34 to 0x36 (ARCHITECTURE.md section 5.5), so this reading stands on the file at %s") % (R8, "section 1", NEW["v2/docs/PANEL.md"]),
   CONOPS_KEEP.replace("so this reading stands on the file at %s", "and section 4b as drafted describes board B's round-8 circuit radio by radio, read against the round-8 netlist, so this reading stands on the file at %s") % (R8, "every other section this reading cites", NEW["v2/docs/CONOPS.md"]),
   V2_KEEP.replace("so this reading stands on the file at %s", "and lines 24, 41 and 76 and correction 20 as drafted describe the round-8 circuit, so this reading stands on the file at %s") % (R8, "every other line this reading cites", NEW["v2/docs/V2-SPEC.md"]),
   NET_DIFF + "; the documents above were re-read against it, so this reading stands on the file at %s" % NEW["v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net"]],
}
def block(rid):
    m = re.search(r"^  - id: %s\n.*?(?=^  - id: |\Z)" % re.escape(rid), s, re.S | re.M); assert m, rid
    return m
for rid, notes in EV.items():
    m = block(rid); b = m.group(0)
    add = "".join("      - >-\n%s\n" % "\n".join("          " + l for l in _wrap(n)) for n in notes) if False else None
    # wrap each note at about 116 columns, the file's own habit
    lines = []
    for n in notes:
        words, cur, out = n.split(), "", []
        for w in words:
            if len(cur) + len(w) + 1 > 106: out.append(cur); cur = w
            else: cur = (cur + " " + w).strip()
        out.append(cur)
        lines.append("      - >-\n" + "".join("          %s\n" % l for l in out))
    i = b.index("    evidence_bound_to:\n")
    b2 = b[:i] + "".join(lines) + b[i:]
    for path, sha in NEW.items():
        b2 = re.sub(r'"%s@[0-9a-f]{16}"' % re.escape(path), '"%s@%s"' % (path, sha), b2)
    s = s[:m.start()] + b2 + s[m.end():]
# CFL-001's and CFL-004's source lines follow the generator
s = s.replace('      - "v2/ecad/tools/gen_sch_b.py:788"\n', '      - "v2/ecad/tools/gen_sch_b.py:936"\n', 1)
s = s.replace('      - "v2/ecad/tools/gen_sch_b.py:716-741"\n', '      - "v2/ecad/tools/gen_sch_b.py:820-866"\n', 1)
# the needs table is unchanged by the CONOPS draft: re-pin it
full = hashlib.sha256(open(os.path.join(T, "v2/docs/CONOPS.md"), "rb").read()).hexdigest()
s = re.sub(r"(needs_document_sha256: )\"?[0-9a-f]{64}\"?", lambda m: m.group(1) + ('"%s"' % full if '"' in m.group(0) else full), s, count=1)
open(P, "w").write(s)
print("rebound:", sorted(EV), NEW)
