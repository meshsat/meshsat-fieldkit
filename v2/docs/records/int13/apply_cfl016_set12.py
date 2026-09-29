#!/usr/bin/env python3
"""CFL-016 read FAIL on set 12, with the document re-read as its own open item S-122 (MESHSAT-1357, 29 September 2026). The
answer to the targeted re-check of set 12 at 7a9f7b5b (`checks/check-int13-3.md`), blocking B1 in its third round.

A change of diagnosis, not a third patch. Three rounds found the same defect in this record's entries: each claimed a
reading that no script had made and no filed check stated (first that the section's other rows had been read, then that
the re-check had read the record's other documents). The cause is that CFL-016's PASS was being kept by hand while every
integration set changes the circuit its documents describe. So this script:
  1. appends one entry that withdraws the false sentence of the entry `apply_conops_4b_set12` wrote, corrects its two
     dates (from `git log`), and names the stale passages only in the filed check's own words;
  2. sets CFL-016's evidence_result to FAIL and makes it wait on S-122; CONOPS.md's section 4b and EMCON row stay as
     rewritten and checked;
  3. opens S-122: every document CFL-016 names re-read whole against the committed netlists by a script that asserts each
     part it names, and a filed independent check that states in its own words which documents it read.
It changes no document. Every other record and open item is asserted unchanged; the registry re-parses. It also re-files
the three checks `apply_conops_4b_set12` filed, with a path rule that keeps each path's name (minor 2 of the check).
Refuses a second run. Run: python3 <this file>."""
import os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A

TAG = "apply_cfl016_set12"
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
SCRATCH = os.path.join(os.path.expanduser("~"), "worktrees", "meshsat-fieldkit", "_scratch")
DASHES = ("—", "–")


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    sys.exit(2)


def scrub(t):
    t = re.sub(r"/(?:home|root|tmp)/[^\s`)]*?/_scratch/", "<scratch>/", t)
    t = re.sub(r"(?<![<\w/])_scratch/", "<scratch>/", t)
    t = re.sub(r"/(?:home|root|tmp)/[^\s`)]*", "<local path>", t)
    return t


def commit_subject(c):
    r = subprocess.run(["git", "-C", TOP, "log", "-1", "--format=%h %s", c], capture_output=True, text=True)
    if r.returncode: refuse("no commit %s" % c)
    return r.stdout.strip()


ENTRY = (
    "v2/docs/records/int13/checks/check-int13-3.md (the targeted re-check of set 12 at 7a9f7b5b, blocking B1 in its third "
    "round; filed by v2/docs/records/int13/apply_cfl016_set12.py): the entry written by apply_conops_4b_set12 said that the "
    "other documents this record names were read by the re-check of check-int13-2 and that it found no stale statement "
    "outside CONOPS.md. That sentence is withdrawn: check-int13-2 read CONOPS.md only, and says so. Two dates in the same "
    "entry are corrected: the back-feed item went stale with set 12's circuit change (3115fc58), not with stream w4b, and "
    "the board A rows with board A's round 8 (c0133147). In the words of check-int13-3, stale statements remain in the "
    "documents this record names: PANEL.md line 156 still lists the back-feed of SD-EMC-2 into the RockBLOCK, the E22 and "
    "the E72 as open, which set 12 draws; PANEL.md lines 155 and 156 still name U26 and board A's round 8 candidate at "
    "gen_sch_a.py:1240-1243; V2-SPEC.md line 76 still lists the RockBLOCK's ENABLE forced low as owed; and, among its "
    "minors, CONOPS.md line 883 (section 4e) still names the slots' earlier gate parts and an open L3, and PANEL.md line 63 "
    "omits R52 and D23 on board C's EMCON line. No filed reading has re-read the rest of the named documents against set "
    "12's netlists. So this record reads FAIL on set 12 and waits on S-122; CONOPS.md section 4b and section 4's EMCON row "
    "stay as rewritten, and check-int13-3 read them true pin by pin. The result is FAIL (was PASS).")

S122 = (
    "(the targeted re-check of set 12, v2/docs/records/int13/checks/check-int13-3.md, blocking B1 in its third round) The "
    "documents CFL-016 names (PANEL.md, CONOPS.md, V2-SPEC.md, OPERATING-ENVELOPE.md section 4, TEST-PLAN.md and "
    "decisions 28 and 40 of tools/pcb_decisions.yaml) have not been re-read whole against the committed netlists since the "
    "S-07 correction of 26 September 2026, and passages known from that check describe replaced circuits: PANEL.md lines "
    "63, 155 and 156; V2-SPEC.md line 76; CONOPS.md line 883 (section 4e). CONOPS.md's section 4b preamble also says its "
    "rewrite script asserted every gate, supply and net the rows name, where the script asserts 146 pin assignments of 55 "
    "parts and the check read the rest (U9, R52 and D23 pins, U214, U314, U22 to U24, and the source of LIME_HW_EN). "
    "Owner: the document writer. Closed when every statement of those documents about the EMCON line and the parts it gates "
    "is re-derived from the committed netlists of the set that carries them by a script that asserts each part it names, "
    "and a filed independent check states in its own words which documents and lines it read; CFL-016 is then re-read.")


def main():
    reg = open(REG, encoding="utf-8").read()
    if TAG in reg: refuse("already applied")
    for c in ("3115fc58", "c0133147"): commit_subject(c)
    before = yaml.safe_load(reg)
    ids = {x["id"] for x in before["open_items"]} | {x["id"] for x in before["closed_items"]}
    if "S-122" in ids or "S-121" in ids: refuse("S-121 or S-122 exists (S-121 is reserved for stream s119's U3B item)")
    r = [x for x in before["records"] if x["id"] == "CFL-016"][0]
    if (r.get("evidence_result"), r.get("status"), r.get("waits_on")) != ("PASS", "CONFLICT_RESOLVED", None): refuse("CFL-016's state")
    for txt in (ENTRY, S122):
        A.screen(txt, "CFL-016")
        if any(d in txt for d in DASHES): refuse("a dash")
    # the filed check first: the entry cites it
    src = os.path.join(SCRATCH, "chk-int13b", "CHECK-2.md")
    if not open(src, encoding="utf-8").read().startswith("mergeable: no"): refuse("the check's first line")
    open(os.path.join(HERE, "checks", "check-int13-3.md"), "w", encoding="utf-8").write(scrub(open(src, encoding="utf-8").read()))
    for s, dst in (("chk-set12/CHECK-2.md", "check-set12-2.md"), ("chk-set12/CHECK-3.md", "check-set12-3.md"),
                   ("chk-int13b/CHECK.md", "check-int13-2.md")):
        open(os.path.join(HERE, "checks", dst), "w", encoding="utf-8").write(scrub(open(os.path.join(SCRATCH, s), encoding="utf-8").read()))
    for f in os.listdir(os.path.join(HERE, "checks")):
        t = open(os.path.join(HERE, "checks", f), encoding="utf-8").read()
        if re.search(r"/(home|root|tmp)/|claude-runner", t): refuse("checks/%s holds a local path" % f)
    out = reg
    i, j = A.span(out, "CFL-016")
    t = out[i:j]
    m = re.search(r"(?m)^    evidence:\n", t)
    tail = t[m.end():]
    k = re.search(r"(?m)^    [a-z_]+:", tail)
    end = m.end() + (k.start() if k else len(tail))
    t = t[:end] + "      - >-\n" + A.fold(ENTRY, 10, 120) + t[end:]
    if t.count("\n    evidence_result: PASS\n") != 1: refuse("CFL-016's evidence_result line")
    t = t.replace("\n    evidence_result: PASS\n", "\n    evidence_result: FAIL\n", 1)
    if "\n    waits_on:" in t: refuse("CFL-016 already waits")
    t = t.replace("\n    evidence_result: FAIL\n", "\n    evidence_result: FAIL\n    waits_on:\n      - S-122\n", 1)
    out = out[:i] + t + out[j:]
    ci = out.index("\nclosed_items:\n")
    out = out[:ci] + "\n  - id: S-122\n    class: SESSION\n    status: OPEN\n    title: >-\n" + A.fold(S122, 6, 120).rstrip("\n") + out[ci:]
    after = yaml.safe_load(out)
    ob, ab = {x["id"]: x for x in before["records"]}, {x["id"]: x for x in after["records"]}
    for rid in ob:
        dd = {f for f in set(ob[rid]) | set(ab[rid]) if ob[rid].get(f) != ab[rid].get(f)}
        if (rid == "CFL-016" and dd != {"evidence", "evidence_result", "waits_on"}) or (rid != "CFL-016" and dd): refuse("%s: %s" % (rid, dd))
    oi, ai = {x["id"]: x for x in before["open_items"]}, {x["id"]: x for x in after["open_items"]}
    if set(ai) - set(oi) != {"S-122"} or any(oi[x] != ai[x] for x in oi): refuse("open items other than S-122 moved")
    if before["closed_items"] != after["closed_items"]: refuse("closed items moved")
    if " ".join(ai["S-122"]["title"].split()) != " ".join(S122.split()): refuse("S-122's title does not read back")
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("%s: CFL-016 reads FAIL and waits on S-122; the overclaim withdrawn and its dates corrected; S-122 opened; four checks (re)filed" % TAG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
