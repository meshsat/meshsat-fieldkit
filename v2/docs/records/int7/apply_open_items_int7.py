#!/usr/bin/env python3
"""The open items found since set 6 was cut, added to the requirements registry at its integration onto the H3 line
(MESHSAT-1357, 28 September 2026). It appends open items at the end of open_items, each under the next free S id,
asserts that nothing else of the parsed registry changes, and refuses a second run. Run by the integrating session."""
import os, re, subprocess, sys, textwrap

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
MARK = "the independent review of handover H3, finding H3-02"

ITEMS = [
 ("TRN-001 on board A does not judge VIN_RAW's entry (" + MARK + ", v2/docs/reviews/2026-09-27-h3-independent-review.md; "
  "erratum f of v2/docs/handover/RELEASE-H3.md). v2/ecad/tools/boards/a.json still declares J_DOCK pins 1 and 2 as the "
  "power entry; both are ground since SC-55 moved VIN_RAW to J_VR1 to J_VR4, and port_protect.py skips a ground pin and "
  "never selects an undeclared one, so the reading is PASS about a population that no longer holds the entry. The clamp D2 "
  "is on VIN_RAW in the netlist: this is a defect of the declaration and the checker's boundary, not proof that the circuit "
  "lacks a clamp. Until repaired TRN-001's PASS on board A is LIMITED wherever it is quoted. Open until the declaration "
  "names the real entry, the checker refuses a declared port whose pins carry no supply or signal net and reports an "
  "exposed connector pin that no declaration covers, a regression shows that moving or omitting a declared entry demands "
  "reconciliation and never shrinks the coverage in silence, and TRN-001 is re-taken on board A (stream d8dec31, with "
  "decision 31's protection review of boards A, D and E, whose holds stand)."),
 ("REL-001's completeness can be false (the independent review of handover H3, finding H3-01, reproduced by the reviewer on "
  "four fixtures with the tool's own command line). reliability.py takes the population it inspects from twelve words in "
  "the parts' value text, so a connector whose value carries none of them leaves the denominator in silence (an undeclared "
  "'RJ45 MagJack' reads PASS; on the boards J_ETH, J_SIM1, J_SIM2, the dock's spring pins and others: 61 parts whose "
  "reference begins J, BT, H, MP, W, SW, X or P are in neither the wear set nor a class on the set 6 netlists, "
  "v2/docs/records/r8int6/fix/wear-before-after.txt); with a board's netlist absent it reads PASS of zero; it picks the "
  "newest matching netlist by file time and records no netlist, so its readings cannot be bound (they read UNBOUND after "
  "the re-take of set 6). Set 6 corrected the opposite error only (a logic gate whose description names a socket, "
  "760d7f41). Until repaired every REL-001 reading is LIMITED to the tool's twelve words. Open until the population is an "
  "explicit inventory in which every candidate is classed or excluded with a visible reason, a missing required input reads "
  "INCONCLUSIVE and reaches its consumers as such, the reading names the declared phase's netlist by content, the reviewer's "
  "four-case matrix reads as he specifies, and REL-001 is re-taken on every board (stream d6rel). REL-001 stays a desk "
  "reading: it tests nothing and replaces no physical verification."),
 ("The rule audit names its verdicts by absolute path (found at the set 6 integration, "
  "v2/docs/records/r8int6/fix/validators-760d7f41.txt): v2/ecad/out/rule-audit/<board>.json carries the path of the tree "
  "that wrote it, so an audit restored into another worktree or clone points at files that are not there, and "
  "open_pairs and stale_readings then read 17 pairs as NOT_JUDGED where they are MISSING_INPUT and drop the section "
  "'Readings owed' from PCB-OPEN-PAIRS.md. The audit is re-taken by rules_status.py in whichever tree the pages are judged "
  "in, which is why the suite passes. Open until the audit carries paths relative to v2/ecad and a test restores an audit "
  "into a second tree and renders the same pages."),
 ("The twenty-eight minor findings of handover H3's two fresh checks (v2/docs/records/handover/H3-COHERENCE-CHECK.md, "
  "H3-USABILITY-CHECK.md) and the errata g to m of v2/docs/handover/RELEASE-H3.md, answered in the pages and listed in "
  "v2/docs/handover/H3-RESPONSE.md with the commit of each. Among them: the renderer's fixed sentence in "
  "v2/docs/CURRENT-EVIDENCE.md that the requirements baseline is still open (rules_render.py; the registry reads "
  "BASELINED), the dock rows of v2/docs/layout-constraints/E.md that still name J_BLK as VIN_RAW's exit, EQ-08's list of "
  "boards against FEA-007's holds, the count behind layer 3's acceptance item 3.15 and CON-010's missing link to S-64's "
  "successor, and the short statement 'no definition change' without the two exceptions DEFINITION-STATUS.md reports. "
  "None changes the status of layers 1 to 3. Open until H3-RESPONSE.md is filed with every finding answered or carried "
  "with its reason."),
]


def main():
    t = open(P, encoding="utf-8").read()
    if MARK in t:
        print("apply_open_items_int7: the items are in the registry already; nothing written"); return 2
    before = yaml.safe_load(t)
    ids = [x["id"] for k in ("open_items", "closed_items") for x in before[k]]
    nxt = max(int(m.group(1)) for i in ids for m in [re.fullmatch(r"S-(\d+)", i)] if m) + 1
    c = t.index("\nclosed_items:\n")
    add = ""
    new_ids = []
    for title in ITEMS:
        iid = "S-%d" % nxt; nxt += 1; new_ids.append(iid)
        body = "\n".join("      " + l for l in textwrap.wrap(title, 114, break_on_hyphens=False, break_long_words=False))
        add += "\n  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % (iid, body)
    new = t[:c].rstrip("\n") + add + "\n" + t[c:]
    after = yaml.safe_load(new)
    assert [x["id"] for x in after["open_items"]] == [x["id"] for x in before["open_items"]] + new_ids
    for k in before:
        if k != "open_items":
            assert after[k] == before[k], k
    got = {x["id"]: x for x in after["open_items"]}
    for iid, title in zip(new_ids, ITEMS):
        assert got[iid]["title"] == title, iid
        assert "—" not in title
    open(P, "w", encoding="utf-8").write(new)
    print("apply_open_items_int7: added %s; open items %d to %d" % (", ".join(new_ids), len(before["open_items"]), len(after["open_items"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
