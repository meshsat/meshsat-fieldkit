#!/usr/bin/env python3
"""S-117 in the requirements registry (stream s117, MESHSAT-1357, 29 September 2026). DRAFT for the integrator, two phases.

  open           AT THE MERGE, after apply_decision_s117.py (it reads the decision's number from tools/pcb_decisions.yaml):
                 opens the FET finding F1 as a new SESSION item (the next free S number), links it from REQ-015, and adds
                 S-117's layout consequence (L2's XAL1010 seat and the five new passives) to S-115's pass. S-117 stays open.
  close <commit> AFTER board A is regenerated on the box with apply_gen_sch_a_s117.py applied and the result committed at
                 <commit>: refuses unless (1) board A's committed netlist was written by this tree's generator
                 (sch_prov.current), (2) readback_s117.check() reads every check PASS on it, (3) the EMC sheet's U3 row reads
                 400 kHz with the 191 kOhm basis, (4) HW-FW-CONTRACT.md carries FW-A17 on PWM_FREQ, (5) the S-117 decision is
                 ruled. Then S-117 moves to closed_items (closed by <commit>, its closing evidence naming the files, every figure
                 read from them here) and leaves REQ-015's waits_on; REQ-015 still waits on S-106, S-107, S-111 and F1.

Every text passes int7's screen (no claim word, no dash); each phase re-parses the registry and checks that only what it names
moved; each refuses a second run. --check (either phase) validates in memory and writes nothing.

Usage (anywhere in the tree): python3 apply_registry_s117.py open [--check]
                              python3 apply_registry_s117.py close <commit> [--check]"""
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
    "(stream s117, S-117's finding F1; decision %d) Board A's charger FETs Q7 to Q10 (CSD18510Q5B: Qg 58 nC at 4.5 V and 118 "
    "nC at 10 V, TI SLPS632 p.3; about 75 nC at 6 V read from its Figure 4, p.5) ask more gate current of the BQ25731's own "
    "6 V regulator than it is specified to give. REGN feeds both low-side drivers and, through the integrated bootstrap "
    "diodes, both high-side drivers (SLUSE66A pin table, printed pages 5 and 6); in buck mode Q7 and Q8 switch every cycle "
    "(Table 9-3, page 27), so REGN supplies 2 x Qg x fS: 46 to 60 mA at a typical 400 kHz and up to 69 mA at 460 kHz, "
    "against VREGN_REG's 0 to 60 mA condition and IREGN_LIM's 50 mA minimum (8.5, page 11), and 93 to 120 mA if the "
    "converter runs buck-boost with all four switching, whose threshold the maker does not state (9.3.10, page 27). TI's "
    "loss equations (10.2.2.6, pages 86 to 88) put 5.4 to 7.4 W in Q7 at the front end's 5.7 A bound and 3.3 to 4.4 W at "
    "its typical 5.0 A (the V-I overlap of a 34 to 49 nC switching charge through the driver's 6.9 Ohm turn-on path), and "
    "REGN's own drop puts 0.88 W inside U3 (v2/docs/records/s117/charger_l_f.out, sections 3 and 5). S-117's 400 kHz row "
    "is the one that asks least of REGN; it does not close this. Option A(i)'s drafted U3B "
    "(v2/docs/records/a1elec/TOPOLOGY.md) carries the same FETs as Q7B to Q10B. Owner: board A's writer. Closed when board A draws "
    "charger FETs whose gate charge at 6 V keeps 2 x Qg x 460 kHz under REGN's 50 mA minimum limit with margin in buck "
    "mode, and 4 x Qg x 460 kHz wherever a document or a bench reading places the converter in buck-boost, with the "
    "stage's losses re-read by v2/docs/records/s117/charger_l_f.py; or when a maker's document places the drawn FETs "
    "inside REGN's figures.")
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


def next_s(d):
    ids = [x["id"] for sec in ("open_items", "closed_items") for x in d.get(sec) or []]
    nums = [int(m.group(1)) for i in ids for m in [re.match(r"^S-(\d+)$", str(i))] if m]
    return "S-%d" % (max(nums) + 1)


def item_block(t, rid):
    i, j = A.span(t, rid)
    return i, j, t[i:j]


def phase_open(check):
    t = open(REG, encoding="utf-8").read()
    d = yaml.safe_load(t)
    if F1_MARK in t: refuse("F1 is already an item (a second run)")
    n = decision_n()
    new_id = next_s(d)
    title = F1_TITLE % n
    add = S115_ADD % n
    A.screen(title, "F1's title"); A.screen(add, "S-115's addition")
    # 1. S-115's title gains S-117's layout consequence (the title is the last field of its block)
    i, j, blk = item_block(t, "S-115")
    k = blk.index("    title: >-\n")
    old_title = " ".join(l.strip() for l in blk[k + len("    title: >-\n"):].split("\n") if l.strip())
    if old_title != [x for x in d["open_items"] if x["id"] == "S-115"][0]["title"]: refuse("S-115's title is not its last field")
    blk2 = blk[:k] + "    title: >-\n" + A.fold(old_title + add, 6, 120)
    t2 = t[:i] + blk2 + t[j:]
    # 2. the new item after S-117 (the last open item before closed_items)
    i2, j2, _ = item_block(t2, "S-117")
    if not t2[j2:].startswith("closed_items:\n"): refuse("S-117 is not the last open item")
    new_blk = "  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % (new_id, A.fold(title, 6, 120))
    t2 = t2[:j2] + new_blk + t2[j2:]
    # 3. REQ-015 waits on it
    ri, rj, rb = item_block(t2, "REQ-015")
    old_w = "    waits_on: [S-106, S-107, S-111, S-117]\n"
    if rb.count(old_w) != 1: refuse("REQ-015's waits_on is not as read")
    rb2 = rb.replace(old_w, "    waits_on: [S-106, S-107, S-111, S-117, %s]\n" % new_id)
    t2 = t2[:ri] + rb2 + t2[rj:]
    after = yaml.safe_load(t2)
    bo, ao = {x["id"]: x for x in d["open_items"]}, {x["id"]: x for x in after["open_items"]}
    if set(ao) != set(bo) | {new_id}: refuse("open items changed beyond %s" % new_id)
    for k2 in bo:
        if k2 == "S-115":
            if {f for f in set(bo[k2]) | set(ao[k2]) if bo[k2].get(f) != ao[k2].get(f)} != {"title"}: refuse("S-115 moved beyond its title")
        elif bo[k2] != ao[k2]: refuse("open item %s moved" % k2)
    if ao[new_id] != {"id": new_id, "class": "SESSION", "status": "OPEN", "title": title}: refuse("the new item does not read as written")
    rb_, ra_ = {r["id"]: r for r in d["records"]}, {r["id"]: r for r in after["records"]}
    for k2 in rb_:
        diff = {f for f in set(rb_[k2]) | set(ra_[k2]) if rb_[k2].get(f) != ra_[k2].get(f)}
        if diff and not (k2 == "REQ-015" and diff == {"waits_on"}): refuse("%s moved in %s" % (k2, diff))
    for sec in d:
        if sec not in ("open_items", "records") and d[sec] != after[sec]: refuse("section %s changed" % sec)
    print("apply_registry_s117 open: %s opened (F1, decision %d), REQ-015 waits on it, S-115's title carries S-117's layout "
          "consequence; S-117 stays open" % (new_id, n))
    if check:
        print("CHECK ONLY: pcb_requirements.yaml not written.")
        return 0
    open(REG, "w", encoding="utf-8").write(t2)
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
    f1 = [x["id"] for x in d["open_items"] if F1_MARK in str(x.get("title", ""))]
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
    A.screen(ev, "S-117's closing evidence")
    i, j = A.span(t, "S-117")
    blk = t[i:j]
    tm = re.search(r"(?m)^    title: >-\n", blk)
    title = blk[tm.end():].rstrip("\n")
    out = t[:i] + t[j:]
    k = out.index("\nrecords:\n")
    closed = "  - id: S-117\n    closed_by: commit %s\n    closing_evidence: >-\n%s    title: >-\n%s\n" % (commit, A.fold(ev, 6, 120), title)
    out = out[:k + 1] + closed + out[k + 1:]
    ri, rj = A.span(out, "REQ-015")
    rb = out[ri:rj]
    old_w = "    waits_on: [S-106, S-107, S-111, S-117, %s]\n" % f1[0]
    if rb.count(old_w) != 1: refuse("REQ-015's waits_on is not as the open phase left it")
    out = out[:ri] + rb.replace(old_w, "    waits_on: [S-106, S-107, S-111, %s]\n" % f1[0]) + out[rj:]
    after = yaml.safe_load(out)
    if [x["id"] for x in after["open_items"]] != [x["id"] for x in d["open_items"] if x["id"] != "S-117"]: refuse("open items changed beyond S-117")
    if [x["id"] for x in after["closed_items"]] != [x["id"] for x in d["closed_items"]] + ["S-117"]: refuse("closed items changed beyond S-117")
    rb_, ra_ = {r["id"]: r for r in d["records"]}, {r["id"]: r for r in after["records"]}
    for k2 in rb_:
        diff = {f for f in set(rb_[k2]) | set(ra_[k2]) if rb_[k2].get(f) != ra_[k2].get(f)}
        if diff and not (k2 == "REQ-015" and diff == {"waits_on"}): refuse("%s moved in %s" % (k2, diff))
    for sec in d:
        if sec not in ("open_items", "closed_items", "records") and d[sec] != after[sec]: refuse("section %s changed" % sec)
    print("apply_registry_s117 close: S-117 closed by commit %s (readback %d of %d PASS on netlist %s); REQ-015 waits on "
          "S-106, S-107, S-111 and %s" % (commit[:8], len(res), len(res), sha16(NET), f1[0]))
    if check:
        print("CHECK ONLY: pcb_requirements.yaml not written.")
        return 0
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("APPLIED. Next: python3 v2/ecad/tools/rules_lib.py requirements, then rules_render.py --requirements")
    return 0


def main(argv):
    check = "--check" in argv
    args = [x for x in argv[1:] if x != "--check"]
    if args[:1] == ["open"] and len(args) == 1: return phase_open(check)
    if args[:1] == ["close"] and len(args) == 2: return phase_close(args[1], check)
    refuse("usage: apply_registry_s117.py open [--check] | close <commit> [--check]")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
