#!/usr/bin/env python3
"""The integrator's answers to the integration check of set 13 (MESHSAT-1357, 29 September 2026; `checks/check-int14-1.md`).
  B1  The hand reason written for CFL-016 by apply_rebind_after_circuit_set13 said that none of the documents CFL-016 names
      describes the driver side of board C's e-paper lines; PANEL.md section 3's pin map does. This script READS those rows
      (PANEL.md, the rows for GPIO 2 to 7) and board C's committed netlist (U3 pins 4 to 7, R53 to R56) and asserts what the
      correcting entry states before writing it. The entry withdraws the clause; the rows join S-122's scope (S-122's
      closure re-reads the documents against the netlists of the set that carries it). CFL-016 stays FAIL on S-122.
  m2  return_via, ref_change and via_audit read the board table (signal classes; via_audit its two ring minimums) and
      none records it; opened as S-123 (next free), reworded after check-int14-2 (R2-B2), and CON-023 and CON-024, the
      records resting on the three tools' rules in the coverage map, wait on it.
  m4, m5, m8  The walk minors README, two docstrings, and the records index rows for csi/, walkmin/ and int14/.
  m1, m3, m6, m7  Carried, in this directory's README.
Every other record and item is asserted unchanged; the registry re-parses. Refuses a second run. Run: python3 <this file>."""
import os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import apply_check1_answers as A
import tx_inhibit as TX

TAG = "apply_check14_fixes"
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
NET_C = "v2/ecad/pcb-c-display-c8/out/pcb-c-display.net"
DASHES = ("—", "–")


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m)); sys.exit(2)


def read_facts():
    rows = [l for l in open(os.path.join(TOP, "v2/docs/PANEL.md"), encoding="utf-8").read().split("\n")
            if l.startswith("| 2, 3 | EPD_SCL, EPD_SDA |") or l.startswith("| 4, 5, 6, 7 | EPD_DC, EPD_CS, EPD_RST, EPD_BUSY |")]
    if len(rows) != 2: refuse("PANEL.md's GPIO 2 to 7 rows are not as read (%d found)" % len(rows))
    nl = TX.parse_netlist(os.path.join(TOP, NET_C))
    want = {("U3", "4"): "EPD_SCL_R", ("U3", "5"): "EPD_SDA_R", ("U3", "6"): "EPD_DC_R", ("U3", "7"): "EPD_CS_R",
            ("R53", "1"): "EPD_SCL_R", ("R53", "2"): "EPD_SCL", ("R54", "1"): "EPD_SDA_R", ("R54", "2"): "EPD_SDA",
            ("R55", "1"): "EPD_DC_R", ("R55", "2"): "EPD_DC", ("R56", "1"): "EPD_CS_R", ("R56", "2"): "EPD_CS"}
    for k, v in want.items():
        if nl["pin"].get(k) != v: refuse("board C %s pin %s is %r, not %s" % (k[0], k[1], nl["pin"].get(k), v))
    for r in ("R53", "R54", "R55", "R56"):
        if TX.value(nl, r) != "27R": refuse("%s is %r" % (r, TX.value(nl, r)))


ENTRY = (
    "v2/docs/records/int14/checks/check-int14-1.md (the integration check of set 13, blocking B1; answered by "
    "v2/docs/records/int14/apply_check14_fixes.py): the entry written by apply_rebind_after_circuit_set13 on board C's "
    "netlist said that none of the documents this record names describes the driver side of board C's e-paper lines. That "
    "clause is withdrawn. Read by that script at this commit: PANEL.md section 3's pin map gives GPIO 2 and 3 to EPD_SCL and "
    "EPD_SDA and GPIO 4 to 7 to EPD_DC, EPD_CS, EPD_RST and EPD_BUSY, and on board C's netlist c9f7394594201045 U3's pins 4 "
    "to 7 (GPIO 2 to 5) sit on EPD_SCL_R, EPD_SDA_R, EPD_DC_R and EPD_CS_R, each joined to its line by a 27R resistor (R53 to "
    "R56). So set 13 makes those rows describe a replaced circuit. The rest of that entry stands: the R53 this record's "
    "earlier evidence names is board E's. This record reads FAIL and waits on S-122, whose closure re-reads the named "
    "documents against the netlists of the set that carries it; the rows are added to S-122. The result stays FAIL.")
S122_ADD = (
    "Added at integration set 13 (v2/docs/records/int14/checks/check-int14-1.md, blocking B1): PANEL.md section 3's pin map "
    "rows for GPIO 2 to 5 name EPD_SCL, EPD_SDA, EPD_DC and EPD_CS, where board C's netlist since set 13 puts U3's pins on "
    "EPD_SCL_R, EPD_SDA_R, EPD_DC_R and EPD_CS_R through R53 to R56. S-122 closes only when these rows, like the EMCON "
    "statements, are re-derived from the committed netlists of the set that carries it.")
S123 = (
    "(the integration checks of set 13, v2/docs/records/int14/checks/check-int14-1.md minor 2 and check-int14-2.md R2-B2) "
    "tools/return_via.py and tools/ref_change.py read a board's signal classes from tools/boards/<letter>.json, and "
    "tools/via_audit.py reads its annular_min_mm and via_ring_min_mm from the same file; none of the three records that file "
    "in its readings. None of the three is in rules_status.CONFIG_INPUTS today, so their readings read CONFIG_UNDECLARED and "
    "never count as current; the gap is that when they are declared, the board table must be among their inputs. Set 13 "
    "reclassed board C's Q3_G and EMCON_HW_DRV and added the EPD_*_R classes, which return_via and ref_change read; board "
    "C's return_via and ref_change (return_stitch) readings are dated 21 September 2026 and were not re-taken (via_audit "
    "reads neither class, and its two values did not change on board C). Owner: the tools author. Closed when the three "
    "tools record the board table in their readings, rules_status declares it for them, and board C's return_via and "
    "return_stitch readings are re-taken on the box.")


def fold_append_title(out, sid, text):
    i, j = A.span(out, sid)
    t = out[i:j]
    m = re.search(r"(?m)^    title: >-\n((?:      .*\n)+)", t)
    if not m: refuse("%s's title block" % sid)
    t = t[:m.end()] + A.fold(text, 6, 120) + t[m.end():]
    return out[:i] + t + out[j:]


def main():
    reg = open(REG, encoding="utf-8").read()
    if TAG in reg: refuse("already applied")
    read_facts()
    before = yaml.safe_load(reg)
    ids = {x["id"] for x in before["open_items"]} | {x["id"] for x in before["closed_items"]}
    if "S-123" in ids or "S-122" not in {x["id"] for x in before["open_items"]}: refuse("S-122 open and S-123 free expected")
    for txt in (ENTRY, S122_ADD, S123):
        A.screen(txt, TAG)
        if any(d in txt for d in DASHES): refuse("a dash")
    out = reg
    i, j = A.span(out, "CFL-016")
    t = out[i:j]
    m = re.search(r"(?m)^    evidence:\n", t)
    tail = t[m.end():]
    k = re.search(r"(?m)^    [a-z_]+:", tail)
    end = m.end() + (k.start() if k else len(tail))
    t = t[:end] + "      - >-\n" + A.fold(ENTRY, 10, 120) + t[end:]
    out = out[:i] + t + out[j:]
    out = fold_append_title(out, "S-122", S122_ADD)
    ci = out.index("\nclosed_items:\n")
    out = out[:ci] + "\n  - id: S-123\n    class: SESSION\n    status: OPEN\n    title: >-\n" + A.fold(S123, 6, 120).rstrip("\n") + out[ci:]
    # S-123 moves the records that rest on the three tools' rules (read from the coverage map, check-int14-2's n1): RET-003,
    # RET-004, VIA-001 and VIA-002; CON-023 and CON-024, both NOT_JUDGED, are the only records resting on them
    cov = yaml.safe_load(open(os.path.join(TOP, "v2/ecad/tools/pcb_rules_coverage.yaml"), encoding="utf-8"))["coverage"]
    tools = ("return_via.py", "ref_change.py", "via_audit.py")
    hit = {rid for rid, c in cov.items() if isinstance(c, dict) and str((c.get("verification") or {}).get("tool")) in tools}
    if hit != {"RET-003", "RET-004", "VIA-001", "VIA-002"}: refuse("the coverage map gives the three tools %s" % sorted(hit))
    movers = sorted(r["id"] for r in before["records"] if set((r.get("satisfied_by") or {}).get("rules") or []) & hit)
    if movers != ["CON-023", "CON-024"]: refuse("records resting on the three tools' rules: %s" % movers)
    for rid in movers:
        if before and [x for x in before["records"] if x["id"] == rid][0].get("waits_on"): refuse("%s already waits" % rid)
        i, j = A.span(out, rid)
        t = out[i:j]
        t = t.rstrip("\n") + "\n    waits_on:\n      - S-123\n" + ("\n" if t.endswith("\n\n") else "")
        out = out[:i] + t + out[j:]
    after = yaml.safe_load(out)
    ob, ab = {x["id"]: x for x in before["records"]}, {x["id"]: x for x in after["records"]}
    for rid in ob:
        dd = {f for f in set(ob[rid]) | set(ab[rid]) if ob[rid].get(f) != ab[rid].get(f)}
        want = {"evidence"} if rid == "CFL-016" else ({"waits_on"} if rid in ("CON-023", "CON-024") else set())
        if dd != want: refuse("%s: %s" % (rid, dd))
    oi, ai = {x["id"]: x for x in before["open_items"]}, {x["id"]: x for x in after["open_items"]}
    if set(ai) - set(oi) != {"S-123"} or any(oi[x] != ai[x] for x in oi if x != "S-122"): refuse("open items moved")
    if " ".join(ai["S-122"]["title"].split()) != " ".join((oi["S-122"]["title"] + " " + S122_ADD).split()): refuse("S-122's title")
    if before["closed_items"] != after["closed_items"]: refuse("closed items moved")
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    # m4, m5, m8
    def edit(rel, pairs):
        p = os.path.join(TOP, rel); s = open(p, encoding="utf-8").read(); s0 = s
        for o, n in pairs:
            if s.count(o) != 1: refuse("%s: %r" % (rel, o[:60]))
            s = s.replace(o, n)
        if s == s0: refuse("%s unchanged" % rel)
        open(p, "w", encoding="utf-8").write(s)
    edit("v2/docs/records/walkmin/README.md", [(
        "SW-prefix contact rule) stays open and is not answered here. `apply_walk_minors.py` answers them. It asserts each\nold text once and refuses a second run.",
        "SW-prefix contact rule) stays open and is not answered here. `apply_walk_minors.py` answers items 1 and 3 (it asserts\n"
        "each old text once and refuses a second run); the two minors of this record's own check (`checks/check-walkmin-1.md`,\n"
        "items 1 and 2) were answered afterwards by direct edits in `f9bc2f6f`, and its items 3 to 6 are carried.")])
    edit("v2/docs/records/int14/apply_rebind_after_circuit_set13.py", [(
        "(MESHSAT-1357, integration set 13: stream\nd4emcon's FEA-002 remedies on boards B and C; a copy of records/int10's set 9 script with its entry text generalised).",
        "(MESHSAT-1357, integration set 13: stream\ncsi's four 27R series resistors on board C; a copy of records/int13/apply_rebind_after_circuit.py with its text for set 13).")])
    edit("v2/docs/records/int14/apply_rebind_page_set13.py", [(
        "page by sha256/16 and the integration re-rendered it (the set 6 line merged with the H3 line, the renderer's derived",
        "page by sha256/16 and the integration re-rendered it (set 13: board C's regenerated netlist on its rows; set 6's wording follows: the set 6 line merged with the H3 line, the renderer's derived")])
    edit("v2/docs/records/README.md", [(
        "| `s119/` | stream s119",
        "| `csi/` | stream csi (29 September 2026, branch `fnd/csi`, three rounds, checked three times): board C's SI-001 nets decided, allowed pending the layout, or open; the allowance method tied to its reference nets; the e-paper series resistors R53 to R56 (`apply/`), applied in set 13 |\n"
        "| `walkmin/` | the walk minors (29 September 2026, branch `fnd/walkmin`, checked): RF-002's walk takes an EMCON toggle only on its declared contact lugs, and the board key is required |\n"
        "| `int14/` | integration set 13 (29 September 2026, branch `fnd/int14`): s119, csi and walkmin merged, board C regenerated and read back, the pins, sheets, rebinds and checks |\n"
        "| `s119/` | stream s119")])
    edit("v2/docs/records/csi/README.md", [(
        "and any tool reading\n`signal_class`'s class of those nets (via_audit, per the check) reads the new class: those readings owe a re-take.",
        "and any tool reading\n`signal_class`'s class of those nets reads the new class: those readings owe a re-take (via_audit reads no signal class, only\n"
        "the board table's two ring minimums; the integration check of set 13, check-int14-2 n3).")])
    print("%s: CFL-016's clause withdrawn with the PANEL.md rows read; S-122 extended with its closing clause; S-123 opened; m4, m5, m8 and csi's README edited" % TAG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
