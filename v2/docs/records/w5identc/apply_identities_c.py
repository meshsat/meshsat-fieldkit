#!/usr/bin/env python3
"""apply_identities_c.py: bind stream w5identc's reading of board C's part identities to where layer 6's exact-part
requirement is recorded (MESHSAT-1357, 29 September 2026). For the integrator; the stream edits neither file.

WHERE THE REQUIREMENT LIVES (read by this stream at b874b744, by parsing, not by memory):
  * v2/docs/handover/LAYER-STATUS.md, layer 6, item 6.1 "exact manufacturer, MPN, package and grade per fitted part",
    OPEN (and EXECUTION-PLAN.md's review D row, "exact part identities ... that board's layout entry", and EQ-21);
  * NO record of v2/ecad/tools/pcb_requirements.yaml and no rule of pcb_rules.yaml carries it: CMP-001 judges ratings,
    CMP-002 and SUP-001 judge order codes and stock, SCH-005 judges pads; no feasibility record's LAYOUT_ENTRY stage
    names part identities, so rules_status.layout_entry does not count it for any board.

WHAT IT DOES (two files, each change asserted):
  1. pcb_requirements.yaml: one open item at the end of `open_items`, at the next free S number (computed from the file,
     since set 14 may open S-124 first), class SESSION, disposition LAYOUT_STAGE with its why: board C's exact-part
     requirement read by part_identities.py check, with the reading's counts and its sha256. It closes when every
     selection of board C reads RESOLVED on the netlist the board holds.
  2. LAYER-STATUS.md, item 6.1's evidence cell: one sentence naming board C's reading and the open item.

ASSERTIONS: the reading exists and its sha256 is the one pinned below, its verdict is HOLDS on board C's netlist
c9f73945 (the one b874b744 holds), the anchors are present exactly once, the new text differs, the item id is free, the
requirements file re-parses with the item in it, and a second run is refused (the item's marker is already present).
Usage: apply_identities_c.py [--check]   (--check: assert everything, print the changes, write nothing)"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
REQ = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_requirements.yaml")
LAYER = os.path.join(ROOT, "v2", "docs", "handover", "LAYER-STATUS.md")
READING = os.path.join(HERE, "readings", "check-board-c-b874b744.json")
READING_SHA256 = "83c0d79374608634e3536c702659092ae47901d79c1b118b765421d2c4b8becb"
NETLIST_SHA256 = "c9f7394594201045be328a07284328a7eef2c2f451e35e0828a98ac3e5510609"
MARKER = "(stream w5identc, board C's part identities)"
ANCHOR_REQ = "\nclosed_items:\n"
ANCHOR_ROW = "| 6.1 | exact manufacturer, MPN, package and grade per fitted part | **OPEN** | "


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main(argv):
    check = "--check" in argv
    import yaml
    assert os.path.exists(READING), "the reading %s is not here" % READING
    assert sha(READING) == READING_SHA256, "the reading is not the one this script binds (sha256 %s)" % sha(READING)[:16]
    r = json.load(open(READING))
    assert r["verdict"] == "HOLDS" and r["scope"] == ["c"], (r["verdict"], r["scope"])
    assert r["inputs"][0]["netlist_sha256"] == NETLIST_SHA256, "the reading judged another netlist"
    st, why = r["identity_status"], r["unresolved_by_reason"]
    req_txt = open(REQ, encoding="utf-8").read()
    assert MARKER not in req_txt, "refused: the open item is already in pcb_requirements.yaml (a second run)"
    assert req_txt.count(ANCHOR_REQ) == 1, "the anchor 'closed_items:' is not present exactly once"
    reg = yaml.safe_load(req_txt)
    used = [int(m.group(1)) for x in (reg.get("open_items") or []) + (reg.get("closed_items") or [])
            for m in [re.match(r"S-(\d+)$", str(x.get("id")))] if m]
    sid = "S-%d" % (max(used) + 1)
    counts = ("%d BOM parts in %d selections: RESOLVED %d, UNRESOLVED %d (%s), NOT_A_PART %d"
              % (r["rows"], r["selections"], st.get("RESOLVED", 0), st.get("UNRESOLVED", 0),
                 ", ".join("%s %d" % kv for kv in sorted(why.items())), st.get("NOT_A_PART", 0)))
    title = ("%s Layer 6's exact-part requirement (LAYER-STATUS item 6.1; EXECUTION-PLAN review D, exact part identities "
             "before a board's layout entry; EQ-21) read on board C by tools/part_identities.py check at b874b744, netlist "
             "%s: %s. Rule D-2: a selection is RESOLVED only where its held document's cited page prints the part number, "
             "read by the tool (v2/docs/records/w5identc/readings/check-board-c-b874b744.json, sha256 %s). Owner: the parts "
             "writer and board C's author. Closed when every selection of board C reads RESOLVED by part_identities.py "
             "check on the netlist board C holds then, with the documents held (or held back by their terms and fetched "
             "by sha256) and the table re-derived by v2/docs/records/w5identc/build_table.py."
             % (MARKER, NETLIST_SHA256[:16], counts, READING_SHA256[:16]))
    dwhy = ("No registry record's verdict rests on part identities: CMP-001 judges ratings, CMP-002 and SUP-001 order "
            "codes and stock, SCH-005 pads, and no feasibility stage names identities, so rules_status.layout_entry does "
            "not count it. Board C's layout-entry packet (EXECUTION-PLAN review D) reads this item; the integrator may "
            "instead stage it on a feasibility record at LAYOUT_ENTRY, which would make it a layout-entry reason.")
    block = ("  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s\n    disposition: LAYOUT_STAGE\n"
             "    disposition_why: >-\n%s\n" % (sid, _wrap(title, 6), _wrap(dwhy, 6)))
    new_req = req_txt.replace(ANCHOR_REQ, "\n" + block + "closed_items:\n", 1)
    assert new_req != req_txt
    reg2 = yaml.safe_load(new_req)
    got = [x for x in reg2["open_items"] if x.get("id") == sid]
    assert len(got) == 1 and MARKER in got[0]["title"] and got[0]["disposition"] == "LAYOUT_STAGE", "the item does not parse back"
    assert len(reg2["open_items"]) == len(reg["open_items"]) + 1 and reg2["closed_items"] == reg["closed_items"]
    lay = open(LAYER, encoding="utf-8").read()
    assert lay.count(ANCHOR_ROW) == 1, "LAYER-STATUS item 6.1's row is not present exactly once"
    assert MARKER not in lay, "refused: LAYER-STATUS already names this reading (a second run)"
    i = lay.index(ANCHOR_ROW); j = lay.index(" |\n", i)
    sentence = ("; board C at b874b744 %s: %s (`v2/docs/records/w5identc/`, rule D-2, open item %s)" % (MARKER, counts, sid))
    new_lay = lay[:j] + sentence + lay[j:]
    assert new_lay != lay and new_lay.count(MARKER) == 1
    print("apply_identities_c: open item %s:\n%s" % (sid, block))
    print("apply_identities_c: LAYER-STATUS 6.1 gains: %s" % sentence)
    if check:
        print("apply_identities_c: --check, every assertion holds, nothing written"); return 0
    open(REQ, "w", encoding="utf-8").write(new_req)
    open(LAYER, "w", encoding="utf-8").write(new_lay)
    yaml.safe_load(open(REQ, encoding="utf-8").read())
    print("apply_identities_c: written; run rules_lib.py validate and the renderers next")
    return 0


def _wrap(text, indent, width=118):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width - indent: lines.append(cur); cur = w
        else: cur = (cur + " " + w) if cur else w
    if cur: lines.append(cur)
    return "\n".join(" " * indent + l for l in lines)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
