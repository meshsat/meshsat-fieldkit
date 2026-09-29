#!/usr/bin/env python3
"""S-117 in the requirements registry (stream s117, MESHSAT-1357, 29 September 2026; second issue after the independent
check's B2). DRAFT for the integrator, three phases.

  open           AT THE MERGE, after apply_decision_s117.py and apply_decision_fets_s117.py (it reads both decisions' numbers
                 from tools/pcb_decisions.yaml): opens F1, the FETs against REGN (linked from REQ-015), and F2, the energy
                 chain's charger efficiencies for the energy record's writer (linked from REQ-072), as SESSION items with the
                 next free S numbers; adds S-117's layout consequence (L2's XAL1010 seat and the five new passives) to S-115's
                 pass. S-117 stays open.
  close <commit> AFTER board A is regenerated on the box with apply_gen_sch_a_s117.py applied and the result committed at
                 <commit>: refuses unless (1) board A's committed netlist was written by this tree's generator
                 (sch_prov.current), (2) readback_s117.check() reads every check PASS on it, (3) the EMC sheet's U3 row reads
                 400 kHz with the 191 kOhm basis, (4) HW-FW-CONTRACT.md carries FW-A17 on PWM_FREQ, (5) the S-117 decision is
                 ruled. Then S-117 moves to closed_items (closed by <commit>, its closing evidence naming the files, every figure
                 read from them here) and leaves REQ-015's waits_on.
  close-fets <commit>
                 AFTER the same regeneration with apply_gen_sch_a_fets_s117.py and apply_intent_checks_s117.py applied:
                 refuses unless (1) as above, (2) readback_s117.check_fets() reads every check PASS, (3) intent_checks'
                 PIN_ROLES names both parts, (4) the F1 decision is ruled. Then F1 moves to closed_items and leaves REQ-015's
                 waits_on. F2 stays open: it closes when the energy record's writer restates the charger rows and the lid
                 reconciliation is re-run, which this stream does not do.

Every text passes int7's screen (no claim word, no dash); each phase re-parses the registry and checks that only what it names
moved; each refuses a second run. --check (any phase) validates in memory and writes nothing.

Usage (anywhere in the tree): python3 apply_registry_s117.py open [--check]
                              python3 apply_registry_s117.py close <commit> [--check]
                              python3 apply_registry_s117.py close-fets <commit> [--check]"""
import hashlib, json, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
DEC = os.path.join(TOP, "v2/ecad/tools/pcb_decisions.yaml")
EMC = os.path.join(TOP, "v2/ecad/tools/pcb_emc.yaml")
HWFW = os.path.join(TOP, "v2/docs/HW-FW-CONTRACT.md")
NET = os.path.join(TOP, "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net")
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
sys.path.insert(0, HERE)
import apply_check1_answers as A

F1_MARK = "(stream s117, S-117's finding F1"
F1_TITLE = (
    "(stream s117, S-117's finding F1; decision %d, the remedy decision %d) Board A's charger FETs Q7 to Q10 were drawn as "
    "CSD18510Q5B (Qg 58 nC at 4.5 V and 118 nC at 10 V, TI SLPS632 p.3; about 75 nC at 6 V read from its Figure 4, p.5), "
    "which ask more gate current of the BQ25731's own 6 V regulator than it is specified to give. REGN feeds both low-side "
    "drivers and, through the integrated bootstrap diodes, both high-side drivers (SLUSE66A pin table, printed pages 5 and "
    "6); in buck mode Q7 and Q8 switch every cycle (Table 9-3, page 27), so REGN supplies 2 x Qg x fS: 60 mA at a typical "
    "400 kHz with a 6 V drive and up to 77 mA (89 mA at 460 kHz) from the makers' maxima, against VREGN_REG's 0 to 60 mA "
    "condition and IREGN_LIM's 50 mA minimum (8.5, page 11), whose switching tests assume a MOSFET Qg of 4 nC (8.5, pages "
    "11 and 12); twice that if the converter runs buck-boost with all four switching, whose threshold the maker does not "
    "state (9.3.10, page 27). TI's loss equations (10.2.2.6, pages 86 to 88) put 4.8 W in Q7 at the energy model's peak "
    "and read U3 at 0.943 there (0.924 to 0.964 across the readings, R16 and R17 counted, core loss excluded), where TI's "
    "Figure 8-4 (page 19) loses about 0.96 W in all at 4 A: less than the drawn FETs' gate drive alone "
    "(v2/docs/records/s117/efficiency.out). Option A(i)'s drafted U3B (v2/docs/records/a1elec/TOPOLOGY.md) carries the "
    "same FETs as Q7B to Q10B. The remedy is the session's decision %d: Q7 CSD17578Q5A and Q8 to Q10 CSD17577Q5A on the "
    "land they have (REGN 10.5 mA typical in buck mode, 36.5 mA at the maxima with all four switching; U3 0.979 at the "
    "peak by TI's method), drawn by v2/docs/records/s117/apply_gen_sch_a_fets_s117.py with PWR-001's pin roles "
    "(apply_intent_checks_s117.py). Owner: board A's writer. Closed when board A's regenerated netlist carries those four "
    "parts (readback_s117.py --fets reads PASS), or other FETs whose gate charge at 6 V keeps 4 x Qg x 460 kHz under 50 mA "
    "with the stage's losses re-read by v2/docs/records/s117/efficiency.py.")
F2_MARK = "(stream s117, S-117's finding F2"
F2_TITLE = (
    "(stream s117, S-117's finding F2; the independent check of stream s117, blocking item B2) The charger rows of the energy "
    "chain are not supported with the drawn CSD18510Q5B by SLUSE66A Equations 6 to 22 (printed pages 86 to 88): U3 at 0.98 "
    "(v2/docs/records/energy/energy_inputs.yaml, read from Figure 8-4, whose FETs TI does not name) and U3B at 0.975 "
    "(v2/docs/records/a1elec/energy_two_pack.py, read from Figure 8-3). With the drawn FETs U3 reads 0.943 at the model's "
    "peak hour by TI's method (0.924 with the makers' maxima to 0.964 on the most favourable reading), 0.933 to 0.948 "
    "across the pack's 12.0 to 16.8 V, 0.879 to 0.888 in the day's first and last hours, and 0.939 over the reference day "
    "weighted by energy at entry E2 (0.936 at E1); U3B as drafted reads 0.896 in buck mode and 0.802 as a buck-boost bound. "
    "With the FETs of decision %d U3 reads 0.979 at the peak (0.972 to 0.983) and 0.979 over the day at E2 (0.981 at E1), "
    "and U3B 0.961 (800 kHz, CSD17578Q5A x 4) or 0.974 (400 kHz row) at its worst mode; R16 and R17 are counted and the "
    "inductor's core loss is excluded, so every figure is high by it (v2/docs/records/s117/efficiency.out, sections 1, 2, 4 "
    "and 7). The accepted Option A(i) reconciliation (v2/docs/records/a1int/reconcile_lid_panel.py) rests on 0.98 and 0.975. "
    "Owner: the energy record's writer. Closed when both rows are restated from the drawn FETs' losses, or from FETs that "
    "meet them, and the lid reconciliation is re-run.")
S115_ADD = (
    " S-117 (decision %d, v2/docs/records/s117/apply_gen_sch_a_s117.py) adds to the same run: L2 moves to the XAL1010 land "
    "(the body 11.3 x 10.0 mm and 10.0 mm tall, where the CHQ row's fixed seat at (-101.02, 26.3) was sized for the XAL60xx "
    "part's 7.15 x 7.35 mm courtyard between Q9 and Q8), and R219, R220 and C233 to C235 need seats with the charger's "
    "passives (region CHS's list), R219 and C233 at U3 pin 8.")


def refuse(m):
    print("apply_registry_s117: REFUSED: %s" % m)
    sys.exit(2)


def sha16(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def decision_n():
    d = yaml.safe_load(open(DEC, encoding="utf-8"))
    hit = [x for x in d["decisions"] if "(S-117)" in str(x.get("title", ""))]
    if len(hit) != 1: refuse("tools/pcb_decisions.yaml holds %d S-117 decisions; run apply_decision_s117.py first" % len(hit))
    if hit[0].get("status") != "ruled" or hit[0].get("authority") != "SESSION": refuse("the S-117 decision is not ruled by the session")
    return int(hit[0]["n"])


def decision_f1():
    d = yaml.safe_load(open(DEC, encoding="utf-8"))
    hit = [x for x in d["decisions"] if "(S-117 F1)" in str(x.get("title", ""))]
    if len(hit) != 1: refuse("tools/pcb_decisions.yaml holds %d S-117 F1 decisions; run apply_decision_fets_s117.py first" % len(hit))
    if hit[0].get("status") != "ruled" or hit[0].get("authority") != "SESSION": refuse("the S-117 F1 decision is not ruled by the session")
    return int(hit[0]["n"])


def next_s(d, skip=()):
    ids = [x["id"] for sec in ("open_items", "closed_items") for x in d.get(sec) or []]
    nums = [int(m.group(1)) for i in ids for m in [re.match(r"^S-(\d+)$", str(i))] if m]
    return "S-%d" % (max(nums + [int(x[2:]) for x in skip]) + 1)


def item_block(t, rid):
    i, j = A.span(t, rid)
    return i, j, t[i:j]


def phase_open(check):
    t = open(REG, encoding="utf-8").read()
    d = yaml.safe_load(t)
    if F1_MARK in t or F2_MARK in t: refuse("F1 or F2 is already an item (a second run)")
    n, n2 = decision_n(), decision_f1()
    f1_id = next_s(d)
    f2_id = next_s(d, (f1_id,))
    f1_title, f2_title = F1_TITLE % (n, n2, n2), F2_TITLE % n2
    add = S115_ADD % n
    A.screen(f1_title, "F1's title"); A.screen(f2_title, "F2's title"); A.screen(add, "S-115's addition")
    # 1. S-115's title gains S-117's layout consequence (the title is the last field of its block)
    i, j, blk = item_block(t, "S-115")
    k = blk.index("    title: >-\n")
    old_title = " ".join(l.strip() for l in blk[k + len("    title: >-\n"):].split("\n") if l.strip())
    if old_title != [x for x in d["open_items"] if x["id"] == "S-115"][0]["title"]: refuse("S-115's title is not its last field")
    blk2 = blk[:k] + "    title: >-\n" + A.fold(old_title + add, 6, 120)
    t2 = t[:i] + blk2 + t[j:]
    # 2. the new items after S-117 (the last open item before closed_items)
    i2, j2, _ = item_block(t2, "S-117")
    if not t2[j2:].startswith("closed_items:\n"): refuse("S-117 is not the last open item")
    new_blk = "".join("  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % (x, A.fold(tt, 6, 120))
                      for x, tt in ((f1_id, f1_title), (f2_id, f2_title)))
    t2 = t2[:j2] + new_blk + t2[j2:]
    # 3. REQ-015 waits on F1, REQ-072 on F2
    for rid, old, new in (("REQ-015", "    waits_on: [S-106, S-107, S-111, S-117]\n", "    waits_on: [S-106, S-107, S-111, S-117, %s]\n" % f1_id),
                          ("REQ-072", "    waits_on: [S-53, M-02, S-114]\n", "    waits_on: [S-53, M-02, S-114, %s]\n" % f2_id)):
        ri, rj, rb = item_block(t2, rid)
        if rb.count(old) != 1: refuse("%s's waits_on is not as read" % rid)
        t2 = t2[:ri] + rb.replace(old, new) + t2[rj:]
    after = yaml.safe_load(t2)
    bo, ao = {x["id"]: x for x in d["open_items"]}, {x["id"]: x for x in after["open_items"]}
    if set(ao) != set(bo) | {f1_id, f2_id}: refuse("open items changed beyond %s and %s" % (f1_id, f2_id))
    for k2 in bo:
        if k2 == "S-115":
            if {f for f in set(bo[k2]) | set(ao[k2]) if bo[k2].get(f) != ao[k2].get(f)} != {"title"}: refuse("S-115 moved beyond its title")
        elif bo[k2] != ao[k2]: refuse("open item %s moved" % k2)
    for x, tt in ((f1_id, f1_title), (f2_id, f2_title)):
        if ao[x] != {"id": x, "class": "SESSION", "status": "OPEN", "title": tt}: refuse("%s does not read as written" % x)
    rb_, ra_ = {r["id"]: r for r in d["records"]}, {r["id"]: r for r in after["records"]}
    for k2 in rb_:
        diff = {f for f in set(rb_[k2]) | set(ra_[k2]) if rb_[k2].get(f) != ra_[k2].get(f)}
        if diff and not (k2 in ("REQ-015", "REQ-072") and diff == {"waits_on"}): refuse("%s moved in %s" % (k2, diff))
    for sec in d:
        if sec not in ("open_items", "records") and d[sec] != after[sec]: refuse("section %s changed" % sec)
    print("apply_registry_s117 open: %s opened (F1, decisions %d and %d), REQ-015 waits on it; %s opened (F2, the energy "
          "chain's charger rows), REQ-072 waits on it; S-115's title carries S-117's layout consequence; S-117 stays open"
          % (f1_id, n, n2, f2_id))
    if check:
        print("CHECK ONLY: pcb_requirements.yaml not written.")
        return 0
    open(REG, "w", encoding="utf-8").write(t2)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("APPLIED. Next: python3 v2/ecad/tools/rules_lib.py requirements, then rules_render.py --requirements")
    return 0


def close_item(t, d, item, commit, ev, req, check, what):
    """Move `item` from open_items to closed_items (closed by `commit`, `ev` its closing evidence, its title kept) and
    drop it from `req`'s waits_on (read from the parsed record, rewritten on the record's own line); nothing else moves."""
    A.screen(ev, "%s's closing evidence" % item)
    i, j = A.span(t, item)
    blk = t[i:j]
    tm = re.search(r"(?m)^    title: >-\n", blk)
    title = blk[tm.end():].rstrip("\n")
    out = t[:i] + t[j:]
    k = out.index("\nrecords:\n")
    closed = "  - id: %s\n    closed_by: commit %s\n    closing_evidence: >-\n%s    title: >-\n%s\n" % (item, commit, A.fold(ev, 6, 120), title)
    out = out[:k + 1] + closed + out[k + 1:]
    waits = [r for r in d["records"] if r["id"] == req][0].get("waits_on") or []
    if item not in waits: refuse("%s does not wait on %s" % (req, item))
    old_w = "    waits_on: [%s]\n" % ", ".join(waits)
    ri, rj = A.span(out, req)
    rb = out[ri:rj]
    if rb.count(old_w) != 1: refuse("%s's waits_on line is not as parsed" % req)
    left = [x for x in waits if x != item]
    out = out[:ri] + rb.replace(old_w, "    waits_on: [%s]\n" % ", ".join(left)) + out[rj:]
    after = yaml.safe_load(out)
    if [x["id"] for x in after["open_items"]] != [x["id"] for x in d["open_items"] if x["id"] != item]: refuse("open items changed beyond %s" % item)
    if [x["id"] for x in after["closed_items"]] != [x["id"] for x in d["closed_items"]] + [item]: refuse("closed items changed beyond %s" % item)
    rb_, ra_ = {r["id"]: r for r in d["records"]}, {r["id"]: r for r in after["records"]}
    for k2 in rb_:
        diff = {f for f in set(rb_[k2]) | set(ra_[k2]) if rb_[k2].get(f) != ra_[k2].get(f)}
        if diff and not (k2 == req and diff == {"waits_on"}): refuse("%s moved in %s" % (k2, diff))
    for sec in d:
        if sec not in ("open_items", "closed_items", "records") and d[sec] != after[sec]: refuse("section %s changed" % sec)
    print("apply_registry_s117 %s: %s closed by commit %s; %s waits on %s" % (what, item, commit[:8], req, ", ".join(left)))
    if check:
        print("CHECK ONLY: pcb_requirements.yaml not written.")
        return 0
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("APPLIED. Next: python3 v2/ecad/tools/rules_lib.py requirements, then rules_render.py --requirements")
    return 0


def phase_close(commit, check):
    if not re.match(r"^[0-9a-f]{8,40}$", commit or ""): refuse("give the commit that carries the regenerated board A")
    if subprocess.run(["git", "-C", TOP, "cat-file", "-e", commit + "^{commit}"]).returncode: refuse("%s is not in this history" % commit)
    t = open(REG, encoding="utf-8").read()
    d = yaml.safe_load(t)
    if any(x["id"] == "S-117" for x in d["closed_items"]): refuse("S-117 is already closed (a second run)")
    if not any(x["id"] == "S-117" for x in d["open_items"]): refuse("S-117 is not an open item")
    f1 = [x["id"] for sec in ("open_items", "closed_items") for x in d[sec] if F1_MARK in str(x.get("title", ""))]
    if len(f1) != 1: refuse("run the open phase first (F1 found %d times)" % len(f1))
    n = decision_n()
    # (1) the netlist is this tree's generator's
    import sch_prov
    ok, why = sch_prov.current(NET, "a")
    if not ok: refuse("board A's netlist is not this tree's generator's: %s" % why)
    # (2) the read-back
    import readback_s117 as RB
    res = RB.check(RB.N.load(NET))
    bad = [n_ for n_, ok_, _ in res if not ok_]
    if bad: refuse("readback_s117 fails on the committed netlist: %s" % "; ".join(bad))
    doc = RB.N.load(NET)
    rv = [r for r, _ in RB.members(doc, "IADPT") if r.startswith("R")][0]
    cv = [r for r, _ in RB.members(doc, "IADPT") if r.startswith("C")][0]
    val = lambda r: doc["components"][r]["value"]
    # (3) the EMC row
    e = yaml.safe_load(open(EMC, encoding="utf-8"))
    u3 = [s for s in e["boards"]["a"]["sources"] if s["ref"] == "U3"]
    if len(u3) != 1 or u3[0].get("f_khz") != 400 or "191 kOhm" not in u3[0].get("basis", ""): refuse("the EMC sheet's U3 row does not read 400 kHz with 191 kOhm")
    # (4) the firmware row, read as a table row by its first cell
    rows = [[c.strip() for c in l.strip()[1:-1].split("|")] for l in open(HWFW, encoding="utf-8").read().split("\n")
            if l.strip().startswith("|") and l.strip().endswith("|")]
    a17 = [r for r in rows if r and r[0] == "FW-A17"]
    if len(a17) != 1 or "PWM_FREQ" not in a17[0][1] or "PWM_FREQ = 1b" not in a17[0][2]: refuse("HW-FW-CONTRACT.md has no FW-A17 holding PWM_FREQ = 1b")
    ev = ("Board A regenerated with v2/docs/records/s117/apply_gen_sch_a_s117.py (decision %d) and committed by %s: "
          "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net (sha256/16 %s) is this tree's generator's by sch_prov and "
          "v2/docs/records/s117/readback_s117.py reads %d of %d checks PASS on it: L2 %s on %s between CH_SW1 and CH_SW2; "
          "IADPT holds U3 pin 8, TP19, %s %s to GND and %s %s to GND (SLUSE66A Table 9-4, printed page 27; the pin table, "
          "page 6); CH_COMP1 holds U3 pin 16, R25 %s to C26 %s and C234 %s; CH_COMP2 holds U3 pin 17, R220 %s to C235 %s "
          "and C27 %s (Table 9-5's 400 kHz row, pages 27 and 28); C121 %s across the input sense (10.2.2.2, page 84). "
          "v2/ecad/tools/pcb_emc.yaml's U3 row reads 400 kHz; v2/docs/HW-FW-CONTRACT.md's FW-A17 holds PWM_FREQ at its "
          "power-on 1b (Table 9-8, page 43) with V-A05. A schematic item closed on the netlist: the switch node's frequency, "
          "the IADPT reading and the loop are bench items (V-A05), L2's seat and the new parts' seats are S-115's, and the "
          "FETs' gate drive is %s."
          % (n, commit, sha16(NET), len(res), len(res), val("L2"), doc["components"]["L2"]["footprint"].split(":")[-1],
             rv, val(rv), cv, val(cv), val("R25"), val("C26"), val("C234"), val("R220"), val("C235"), val("C27"),
             val("C121"), f1[0]))
    return close_item(t, d, "S-117", commit, ev, "REQ-015", check, "close")


def phase_close_fets(commit, check):
    if not re.match(r"^[0-9a-f]{8,40}$", commit or ""): refuse("give the commit that carries the regenerated board A")
    if subprocess.run(["git", "-C", TOP, "cat-file", "-e", commit + "^{commit}"]).returncode: refuse("%s is not in this history" % commit)
    t = open(REG, encoding="utf-8").read()
    d = yaml.safe_load(t)
    f1 = [x["id"] for x in d["open_items"] if F1_MARK in str(x.get("title", ""))]
    if not f1 and any(F1_MARK in str(x.get("title", "")) for x in d["closed_items"]): refuse("F1 is already closed (a second run)")
    if len(f1) != 1: refuse("run the open phase first (F1 found %d times)" % len(f1))
    n2 = decision_f1()
    import sch_prov
    ok, why = sch_prov.current(NET, "a")
    if not ok: refuse("board A's netlist is not this tree's generator's: %s" % why)
    import readback_s117 as RB
    doc = RB.N.load(NET)
    res = RB.check_fets(doc)
    bad = [n_ for n_, ok_, _ in res if not ok_]
    if bad: refuse("readback_s117 --fets fails on the committed netlist: %s" % "; ".join(bad))
    import intent_checks as IC
    roles, _docs = IC.held_roles({"Q7": doc["components"]["Q7"]["value"], "Q8": doc["components"]["Q8"]["value"]})
    if any(roles.get((q, "4"), (None, None))[1] != "G" for q in ("Q7", "Q8")): refuse("intent_checks.PIN_ROLES does not name the new FETs (apply_intent_checks_s117.py)")
    val = lambda r: doc["components"][r]["value"]
    ev = ("Board A regenerated with v2/docs/records/s117/apply_gen_sch_a_fets_s117.py (decision %d) and committed by %s: "
          "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net (sha256/16 %s) is this tree's generator's by sch_prov and "
          "v2/docs/records/s117/readback_s117.py --fets reads %d of %d FET checks PASS on it: Q7 %s, Q8 %s, Q9 %s and Q10 %s, "
          "each on the PowerPAK SO-8 land with its pads on the nets it had; v2/ecad/tools/intent_checks.py's PIN_ROLES names "
          "both parts (apply_intent_checks_s117.py). With them REGN supplies 10.5 mA typical in buck mode and 36.5 mA at the "
          "makers' maxima with all four switching at 460 kHz, against its 50 mA minimum limit (SLUSE66A 8.5, printed page 11), "
          "and U3 reads 0.979 at the energy model's peak by TI's Equations 6 to 22 (v2/docs/records/s117/efficiency.out). A "
          "schematic item closed on the netlist: the order codes and the Q5A land fit are the parts stream's, the FETs' "
          "temperatures and the switch node are layout and bench items, and the energy chain's rows are F2's."
          % (n2, commit, sha16(NET), len(res), len(res), val("Q7"), val("Q8"), val("Q9"), val("Q10")))
    return close_item(t, d, f1[0], commit, ev, "REQ-015", check, "close-fets")

def main(argv):
    check = "--check" in argv
    args = [x for x in argv[1:] if x != "--check"]
    if args[:1] == ["open"] and len(args) == 1: return phase_open(check)
    if args[:1] == ["close"] and len(args) == 2: return phase_close(args[1], check)
    if args[:1] == ["close-fets"] and len(args) == 2: return phase_close_fets(args[1], check)
    refuse("usage: apply_registry_s117.py open [--check] | close <commit> [--check] | close-fets <commit> [--check]")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
