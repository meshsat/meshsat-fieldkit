#!/usr/bin/env python3
"""The integrator's answers to the independent integration check of set 12 (MESHSAT-1357, 29 September 2026;
`checks/check-int13-1.md`, filed from the checker's CHECK.md). Blocking B1 and minors m1, m2, m3, m6, m8 and m9 are answered
here; m4 and m7 in `README.md` beside this file; m5 by the re-take at the corrected commit with the held FET datasheets
installed (the precondition is stated in README.md).
  B1  CONOPS.md section 4b's RockBLOCK and E22 rows are corrected to board B's set 12 netlist (read here with
      tx_inhibit.parse_netlist, and each gate asserted before the text is written). CFL-016 is re-read against the corrected
      file and rebound with a correcting entry; REQ-005 and CFL-014, the other two records bound to CONOPS.md, are rebound
      with the reason that the diff touches only those two rows (asserted by parsing the diff), which neither reads.
  m1  CON-010's board A reason named "board D's L2"; the L2 of its text is EMCON.md's line-hold item. A correcting entry.
  m2  the eight board A netlist entries named stream d4emcon's change; board A's is stream s117's. A correcting entry each,
      and apply_rebind_after_circuit.py takes the change's name as REBIND_CHANGE (its default is the text it ran with).
  m3  CON-010 and REQ-044's page-rebind entries described the branch without S-117; a completing entry each.
  m6  apply_repin_bc_set12.py's docstring said it refuses a second run; it re-proves and rewrites. The sentence is corrected.
  m8  S-01's text named d4emcon's read-back at 5b89d5ef; a dated pointer to readback_chk12 on the final netlist is added.
  m9  S-117 and S-118 said "committed by 230fdd65"; the netlist was first committed at 3d3e32d6 and carried at 230fdd65.
  The reasons file keeps what set 12 wrote; its two false reasons carry a correction note beside them.
Every old text is asserted exactly once; the registry re-parses and only the fields named change. Refuses a second run.
Run from anywhere: python3 <this file>."""
import hashlib, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import apply_check1_answers as A
import tx_inhibit as TX

REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
CON = "v2/docs/CONOPS.md"
NET_B = "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net"
NET_B16, NET_A16 = "3ef9b8c49a01b728", "6c40250c47195ebb"
DASHES = ("—", "–")
TAG = "apply_check13_fixes"
REF = "v2/docs/records/int13/apply_check13_fixes.py"


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    sys.exit(2)


def sha16(p): return hashlib.sha256(open(os.path.join(TOP, p), "rb").read()).hexdigest()[:16]


def gates_hold():
    """Every gate the two new rows name, read from board B's committed netlist."""
    if sha16(NET_B) != NET_B16: refuse("board B's netlist is not set 12's %s" % NET_B16)
    nl = TX.parse_netlist(os.path.join(TOP, NET_B))
    pin = lambda r, p: nl["pin"].get((r, p))
    want = [("U504", {"1": "EMCON_HW", "2": "LORA_ON", "4": "E22_EN"}), ("U544", {"2": "E22_EN", "4": "LORA_GO", "5": "+3V3_CM3"}),
            ("U546", {"1": "LORA_TXEN", "2": "LORA_GO", "4": "LORA_TXEN_G"}), ("U545", {"1": "LORA_RXEN", "2": "LORA_GO", "4": "LORA_RXEN_G"}),
            ("U547", {"2": "LORA_GO", "4": "LORA_NRST"}), ("U548", {"2": "LORA_GO", "4": "LORA_MOSI"}),
            ("U549", {"2": "LORA_GO", "4": "LORA_SCLK"}), ("U550", {"2": "LORA_GO", "4": "LORA_NSS"}),
            ("U12", {"7": "LORA_TXEN_G", "6": "LORA_RXEN_G"}), ("R542", {"1": "LORA_TXEN_G", "2": "GND"}), ("R543", {"1": "LORA_RXEN_G", "2": "GND"}),
            ("U503", {"4": "RB_EN"}), ("U536", {"1": "EMCON_HW", "2": "RB_SW_IEN", "4": "RB_IEN_DRV"}), ("R532", {"1": "RB_IEN_DRV", "2": "RB_IEN"}),
            ("U543", {"1": "RB_IEN", "5": "+3V3_DEV"}), ("U537", {"1": "RB_IEN", "2": "RB_STATUS", "4": "RB_GO"}),
            ("J_RB9704", {"3": "RB_IEN", "7": "RB_STATUS"})]
    for ref, pins in want:
        for p, n in pins.items():
            if pin(ref, p) != n: refuse("board B %s pin %s is %r, not %s" % (ref, p, pin(ref, p), n))
    if "TPS3808G30" not in TX.value(nl, "U543"): refuse("U543 is not the TPS3808G30")


ROW_RB = ("| RockBLOCK 9704 | the enable of the eFuse that feeds its external supply pin, the only supply wired (`U503`), and "
          "its ENABLE, forced low in hardware: `U536` drives it as `EMCON_HW` AND the firmware's request `RB_SW_IEN` through "
          "`R532` (since stream w4b), `U543`, a TPS3808G30 supervisor on `+3V3_DEV`, holds it low below 2.79 V, and the "
          "module's logic inputs pass only while `RB_GO` = `RB_IEN` AND its `I_BTD` status (`U537`; since set 12, "
          "`feasibility/EMCON.md` sections 4c and 4d) | power at that pin, and the ENABLE; the module's own two 10 F "
          "supercapacitors (about 16 J) keep it powered after the gate opens, and what it does when ENABLE falls is in no "
          "held document, so its local chain stays OPEN (`feasibility/EMCON.md` sections 4.4 and 4c) | lost, at the latest "
          "once its own stored energy is spent (about 4.5 minutes idle, INFERRED, EMCON.md section 4.4) |")
ROW_E22 = ("| E22-900M30S LoRa | the enable of the load switch that feeds its VCC pins (`E22_EN` = `EMCON_HW` AND `LORA_ON`, "
           "`U504`); since set 12 its TXEN, RXEN, NRST and SPI inputs pass slot 3's lines only while that enable is high: "
           "`LORA_GO`, a copy of `E22_EN` on slot 3's own 3.3 V (`U544`), gates `LORA_TXEN` into TXEN (`U546`), `LORA_RXEN` "
           "into RXEN (`U545`) and NRST, MOSI, SCK and NSS (`U547` to `U550`), TXEN and RXEN held low by 100 k (`R542`, "
           "`R543`; `feasibility/EMCON.md` section 4d) | power; TXEN held low | lost |")


def conops():
    p = os.path.join(TOP, CON)
    lines = open(p, encoding="utf-8").read().split("\n")
    s0 = [i for i, l in enumerate(lines) if l.startswith("### 4b. What EMCON does to each radio")]
    s1 = [i for i, l in enumerate(lines) if l.startswith("### 4b.1 ")]
    if len(s0) != 1 or len(s1) != 1 or s1[0] <= s0[0]: refuse("CONOPS: section 4b's bounds")
    idx = {}
    for key, stale in (("| RockBLOCK 9704 |", "driven only by the firmware expander `U6`"), ("| E22-900M30S LoRa |", "is driven by slot 3 and is not on the line")):
        hits = [i for i in range(s0[0], s1[0]) if lines[i].startswith(key)]
        if len(hits) != 1: refuse("CONOPS: %d rows start %r" % (len(hits), key))
        if stale not in lines[hits[0]]: refuse("CONOPS: the %s row no longer carries %r" % (key, stale))
        idx[key] = hits[0]
    old = "\n".join(lines)
    lines[idx["| RockBLOCK 9704 |"]] = ROW_RB
    lines[idx["| E22-900M30S LoRa |"]] = ROW_E22
    new = "\n".join(lines)
    if any(d in ROW_RB + ROW_E22 for d in DASHES): refuse("a dash in the new rows")
    open(p, "w", encoding="utf-8").write(new)
    return sorted(idx.values())


def append(out, rid, entry, rebind=None):
    A.screen(entry, rid)
    if not re.search(r"(?:v2/|README\.md)[^\s,;()]*\.(?:py|yaml|md|pdf|net|json|txt|tsv|kicad_sch|kicad_pcb)", entry): refuse("%s: the entry names no file" % rid)
    if any(d in entry for d in DASHES): refuse("%s: a dash" % rid)
    i, j = A.span(out, rid)
    t = out[i:j]
    m = re.search(r"(?m)^    evidence:\n", t)
    tail = t[m.end():]
    k = re.search(r"(?m)^    [a-z_]+:", tail)
    end = m.end() + (k.start() if k else len(tail))
    t = t[:end] + "      - >-\n" + A.fold(entry, 10, 120) + t[end:]
    if rebind:
        if t.count(rebind[0]) != 1: refuse("%s: the binding %s found %d times" % (rid, rebind[0], t.count(rebind[0])))
        t = t.replace(rebind[0], rebind[1])
    return out[:i] + t + out[j:]


def text_edit(out, section_id, old_re, new, count=1):
    i, j = A.span(out, section_id)
    t = out[i:j]
    hits = list(re.finditer(old_re, t))
    if len(hits) != count: refuse("%s: %r found %d times" % (section_id, old_re, len(hits)))
    t2 = re.sub(old_re, new, t)
    return out[:i] + t2 + out[j:]


def main():
    reg = open(REG, encoding="utf-8").read()
    if TAG in reg: refuse("already applied")
    gates_hold()
    con_old = sha16(CON)
    rows = conops()
    con_new = sha16(CON)
    d = subprocess.run(["git", "-C", TOP, "diff", "-U0", "--", CON], capture_output=True, text=True, check=True).stdout
    touched = sorted({a for m in re.finditer(r"(?m)^@@ -(\d+)(?:,(\d+))? ", d)
                      for a in range(int(m.group(1)), int(m.group(1)) + int(m.group(2) if m.group(2) is not None else 1))})
    if touched != [r + 1 for r in rows]: refuse("CONOPS diff touches lines %s, not only the two rows %s" % (touched, [r + 1 for r in rows]))
    old_b, new_b = "%s@%s" % (CON, con_old), "%s@%s" % (CON, con_new)
    before = yaml.safe_load(reg)
    bound = sorted(r["id"] for r in before["records"] if old_b in (r.get("evidence_bound_to") or []))
    if bound != ["CFL-014", "CFL-016", "REQ-005"]: refuse("records bound to CONOPS.md: %s" % bound)
    out = reg
    np = "needs_document_sha256: %s\n" % hashlib.sha256(open(os.path.join(TOP, CON), "rb").read()).hexdigest()
    op = "needs_document_sha256: %s" % before["needs_document_sha256"]
    if out.count(op) != 1 or not con_old.startswith(before["needs_document_sha256"][:16]): refuse("the needs pin")
    if min(rows) + 1 <= 146: refuse("the diff reaches the needs table (section 2 ends before line 146)")
    out = out.replace(op + "\n", np, 1)
    diffnote = ("%s re-read at integration set 12 (%s, %s to %s): parsed as a diff, the file changed only in section 4b's "
                "RockBLOCK 9704 and E22-900M30S rows (lines %d and %d), corrected to board B's set 12 netlist %s" %
                (CON, TAG, con_old, con_new, rows[0] + 1, rows[1] + 1, NET_B16))
    out = append(out, "CFL-016", diffnote + ". Correction (the independent integration check of set 12, blocking B1): the "
                 "set 12 entry on board B's netlist (apply_rebind_after_circuit b 3ef9b8c49a01b728 and its earlier b entries) "
                 "gave as its reason that the published contracts still describe the circuit, which was false for this "
                 "section: its E22 row said TXEN is driven by slot 3 and is not on the line, where set 12 gates it "
                 "(U12 pin 7 on LORA_TXEN_G = LORA_TXEN AND LORA_GO, U546; LORA_GO a copy of E22_EN, U544; E22_EN = EMCON_HW "
                 "AND LORA_ON, U504), and its RockBLOCK row said ENABLE is driven only by the firmware expander U6, out of "
                 "date on main since stream w4b's U536 and further by set 12's U543 and U537. Both rows now name those "
                 "gates, each asserted on the netlist by this script before the text was written; the section's other rows "
                 "were read against the same netlist by the check. Re-read: every named document describes the circuit "
                 "as generated; rebound to %s. The result stands." % con_new, (old_b, new_b))
    out = append(out, "REQ-005", diffnote + ". This record reads section 2a's list of critical peripherals, which the diff "
                 "does not touch; rebound to %s. No result changes." % con_new, (old_b, new_b))
    out = append(out, "CFL-014", diffnote + ". This record reads section 4's Charging row, which the diff does not touch; "
                 "rebound to %s. No result changes." % con_new, (old_b, new_b))
    # m1
    out = append(out, "CON-010", "Correction (the independent integration check of set 12, minor m1): the reason written by "
                 "apply_rebind_after_circuit a %s says the L2 this record's evidence names is board D's. The only L2 in this "
                 "record's text is feasibility/EMCON.md's item L2, the line-hold limitation (section 7's L2 and L4 rows), not an "
                 "inductor; board A's charger inductor L2, which set 12 replaced, is not what this record rests on. The "
                 "conclusion of that entry stands (%s)." % (NET_A16, REF))
    # m2
    a_ids = sorted(r["id"] for r in before["records"]
                   if any(("apply_rebind_after_circuit a %s" % NET_A16) in " ".join(str(x).split()) for x in (r.get("evidence") or [])))
    if a_ids != sorted(["CFL-005", "CFL-014", "CFL-016", "CON-010", "CON-016", "CON-018", "CON-019", "REQ-077"]):
        refuse("board A's netlist entries are on %s" % a_ids)
    for rid in a_ids:
        out = append(out, rid, "Correction (the independent integration check of set 12, minor m2): the entry written by "
                     "apply_rebind_after_circuit a %s names the circuit change of stream d4emcon's FEA-002 remedies; board A's "
                     "change at set 12 is stream s117's (decisions 56 and 57: R219, C233 to C235 and R220 added on IADPT and the "
                     "compensation networks; C26, C27, L2, Q7 to Q10 and R25 changed). The parsed comparison and the reason in "
                     "that entry stand (%s)." % (NET_A16, REF))
    # m3
    for rid in ("CON-010", "REQ-044"):
        out = append(out, rid, "Completing the page-rebind entry of set 12 (the independent integration check of set 12, minor "
                     "m3): besides stream d4emcon's remedies and the walk's rounds, the branch carries stream s117 (decisions 56 "
                     "and 57, board A regenerated and read back 35 of 35), the census node declarations (EMCON_HW on C; IADPT and "
                     "CH_COMP1 on A; ZBA_RXD, ZBB_RXD and LED_ACT_A1 to A3 on B), the closes of S-117 and S-118 and the opening "
                     "of S-119 and S-120 (%s)." % REF)
    # m8
    i, j = A.span(out, "S-01")
    t = out[i:j]
    last = "document owed, or bench E-04) and every bench row.\n"
    if t.count(last) != 1: refuse("S-01's closing sentence")
    add = ("At set 12's final netlist (board B %s) that read-back fails the three values the set 12 check's minors changed "
           "on purpose (R238, R527, R532); stream rf2walk2's v2/docs/records/rf2walk/tools/readback_chk12.py carries them "
           "and reads every check holding on it (29 September 2026, %s)." % (NET_B16, REF))
    t = t.replace(last, last + A.fold(add, 6, 120))
    out = out[:i] + t + out[j:]
    # m9
    for sid in ("S-117", "S-118"):
        out = text_edit(out, sid, r"and committed by\n(\s+)230fdd65949524d275ea3d9dbe4d8cfd1c34c711:",
                        r"and carried at\n\g<1>230fdd65949524d275ea3d9dbe4d8cfd1c34c711 (first committed at 3d3e32d6):")
    after = yaml.safe_load(out)
    ob, ab = {r["id"]: r for r in before["records"]}, {r["id"]: r for r in after["records"]}
    changed_rec = {"CFL-016", "REQ-005", "CFL-014", "CON-010", "REQ-044"} | set(a_ids)
    for rid in ob:
        dd = {f for f in set(ob[rid]) | set(ab[rid]) if ob[rid].get(f) != ab[rid].get(f)}
        allowed = {"evidence", "evidence_bound_to"} if rid in {"CFL-016", "REQ-005", "CFL-014"} else {"evidence"}
        if (rid in changed_rec and not dd <= allowed) or (rid not in changed_rec and dd): refuse("%s: %s" % (rid, dd))
    top = {k for k in set(before) | set(after) if k not in ("records", "open_items", "closed_items") and before.get(k) != after.get(k)}
    if top != {"needs_document_sha256"}: refuse("top-level fields moved: %s" % top)
    oi = {x["id"]: x for x in before["open_items"]}; ai = {x["id"]: x for x in after["open_items"]}
    if {k for k in oi if oi[k] != ai[k]} != {"S-01"}: refuse("open items other than S-01 moved")
    oc = {x["id"]: x for x in before["closed_items"]}; ac = {x["id"]: x for x in after["closed_items"]}
    if {k for k in oc if oc[k] != ac[k]} != {"S-117", "S-118"}: refuse("closed items other than S-117 and S-118 moved")
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    # m6
    rp = os.path.join(HERE, "apply_repin_bc_set12.py")
    t = open(rp, encoding="utf-8").read()
    o = "Refuses when a proof fails or on a second run. Run from the repository root"
    if t.count(o) != 1: refuse("apply_repin_bc_set12.py's sentence")
    open(rp, "w", encoding="utf-8").write(t.replace(o, "Refuses when a proof fails; a board already pinned is re-proved and "
                                                     "left as it is, and the file is written again (the set 12 check's m6). Run from the repository root"))
    # m2, the script: the change's name as a parameter, its default the text it ran with
    ap = os.path.join(HERE, "apply_rebind_after_circuit.py")
    t = open(ap, encoding="utf-8").read()
    o = "the circuit change of stream d4emcon's FEA-002 remedies was \"\n                 \"compared"
    if t.count(o) != 1: refuse("apply_rebind_after_circuit.py's entry text")
    t = t.replace(o, "%s was \"\n                 \"compared")
    o2 = "(rel, letter, n16, o16,"
    if t.count(o2) != 1: refuse("apply_rebind_after_circuit.py's format arguments")
    t = t.replace(o2, "(rel, letter, n16, CHANGE, o16,")
    o3 = "WORD = re.compile("
    t = t.replace(o3, "# The change's name in each entry (the set 12 check's m2: board A's entries named d4emcon's); the default is the text it ran with.\n"
                      "CHANGE = os.environ.get(\"REBIND_CHANGE\", \"the circuit change of stream d4emcon's FEA-002 remedies\")\n" + o3, 1)
    import ast; ast.parse(t)
    open(ap, "w", encoding="utf-8").write(t)
    # the reasons file: a note beside the two false reasons, the text set 12 wrote kept
    rf = os.path.join(HERE, "rebind_reasons_set12.py")
    t = open(rf, encoding="utf-8").read()
    for o, note in (('B = {\n "CHO-001"', '# Board B\'s "CFL-016" reason below was FALSE for CONOPS section 4b (the set 12 check\'s B1); the entries it wrote are\n'
                                           '# corrected by apply_check13_fixes.py, and the text is kept as the record of what was written.\nB = {\n "CHO-001"'),
                    (' "CON-010": "the PA\'s VGG gate', ' # m1 of the set 12 check: the L2 below is EMCON.md\'s line-hold item, not board D\'s; corrected in the registry\n'
                                                     ' # by apply_check13_fixes.py.\n "CON-010": "the PA\'s VGG gate')):
        if t.count(o) != 1: refuse("rebind_reasons_set12.py: %r" % o[:30])
        t = t.replace(o, note)
    ast.parse(t)
    open(rf, "w", encoding="utf-8").write(t)
    print("%s: CONOPS %s to %s (rows %d and %d); registry: CFL-016, REQ-005, CFL-014 rebound; CON-010 m1; %d board A m2 "
          "entries; m3 on CON-010 and REQ-044; S-01 m8; S-117 and S-118 m9; scripts m6 and m2 corrected" %
          (TAG, con_old, con_new, rows[0] + 1, rows[1] + 1, len(a_ids)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
