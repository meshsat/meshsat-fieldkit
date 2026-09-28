#!/usr/bin/env python3
"""The registry's answers to the RE-CHECK of the set 6 integration (MESHSAT-1357, 28 September 2026;
v2/docs/records/int7/CHECK-2.md, an AI review, which read the corrected candidate 85ad1193 NOT mergeable on one
finding, R-1: CON-010's dependency items S-92 and S-93 each named ONE ground where RF-002's walk names up to three for
the row). It was the second failure on the same point, so the METHOD changed: the grounds are read from the walk's own
report (walk_grounds.py, walk-grounds.txt) and this script ASSERTS that every part the walk's undecided grounds name,
for every undecided row on CON-010's allocated boards, is named in an open item CON-010 waits on.

R-1  S-92 rewritten to the SA868 row's three grounds, S-93 to board A's two rows' four; the count "two" is gone; each
     closes when its row reads decided at a re-take, and a bench reading is recorded as a sample (n9); CON-010's entry
     names every ground.
n1   REQ-032 (every state of the gates' own supplies, boards A and B) waits on S-65 as FEA-002 and REQ-030 do.
n2   CFL-006 is bound to pcb_energy_chain.yaml and FEA-005 to two packet documents S-86 edits: both wait on S-86.
n4   S-81's closing evidence no longer points the brief's wording at S-91's list, which does not name it.
n5   the review of the restart plan is an outside reviewer's, pasted by the owner: CON-010's entry says so.
n6   S-61's reason says what finding D-F3 of the unmerged review asks for, and that nothing but S-61 carries its own ask.

It changes no statement, acceptance, status or evidence_result, screens every new sentence, re-parses the file,
asserts that only the intended fields changed and refuses a second run."""
import json, os, re, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import apply_check1_answers as A      # span, fold, block_at, edit_fold, screen (its main is not run on import)
import walk_grounds as WG

P, TOP = A.P, A.TOP
MARK = "on every ground its own report names"
S92 = ("RF-002's walk reads the SA868 VHF exciter's row (board D, the key on U2 pin 5) UNDECIDED, on every ground its own "
       "report names (v2/docs/records/int7/walk-grounds.txt, written by walk_grounds.py from the walk on the set 6 netlists; "
       "inhibit_chain_d: 7 pass, 0 failed, 1 undecided of 8): (1) with U13's supply +3V3_D8 down, U13 no longer drives "
       "SA_PTT_n, which sits at 2.85 V from the currents that are known, and the SA868's maker states no input threshold for "
       "U2 pin 5; (2) its maker states no input current for U2 pin 5 either; (3) with EMCON on, the open-drain output U13 pin 4 "
       "is released and SA_PTT_n is held at 2.86 V by R88 and R89 alone, and U13's sheet does not state that output's "
       "off-state current while powered. CON-010, the transmit gate on board D (KEY = PTT_ANY AND TX_INHIBIT_n), cannot read "
       "PASS at the desk while the row is undecided. S-64 (W3T-F1, TX_INHIBIT_n's fail-safe level with board C unpowered) is "
       "closed by SC-67 and that check fails on no board since set 6; what remains for CON-010 is this row and board A's two "
       "rows (S-93). Open until RF-002, re-taken on board D, reads the row decided: each ground answered by a maker's figure "
       "in a held document under v2/vendor/, or by a hardware element that makes it moot, or by a bench reading on a built "
       "board (bench E-01 of v2/docs/feasibility/EMCON.md; prototype verification), which is a sample of one board and is "
       "recorded as one.")
S93 = ("RF-002's walk reads two rows of board A UNDECIDED, on every ground its own report names "
       "(v2/docs/records/int7/walk-grounds.txt; inhibit_chain_a: 7 pass, 0 failed, 2 undecided of 9 on the set 6 netlist). The "
       "QMX HF transceiver's row (A power on J_HF), on one ground: Q24 pin 5 (CSD18510Q5B) on HF_OUT is a transistor whose "
       "type or pin map the walk cannot read, and its other pins sit on HF_HDRV2 and HF_SW2, the drive of U15, the gated "
       "LM5176 itself, for which no table states that its drive is off with its enable (TI's SNVSAI1D 7.4.1 gives the "
       "shutdown as 'VCC off, No switching' and states no level for HDRV1 and HDRV2). The 30 W power amplifier's row (A power "
       "on J_PA), on three grounds: the same for Q14 pin 5 on PA_OUT with U13's drive (PA_HDRV2, PA_SW2); U14, the INA226 on "
       "the rail (pins 8 and 9 on +13V8_PA, pin 10 on PA_OUT), a part no class of the walk reads, so whether it can feed the "
       "rail is not known (a ground of the instrument: no pin map or protection row of its maker's is held for the walk); and, "
       "with U36's supply +3V3_EMCON down, PA_UVLO sits at 0.35 V from the currents that are known while the sheet of board "
       "D's Q1 (the 2N7002 on PA_EN) states its gate leakage IGSS at 25 C only. v2/docs/feasibility/EMCON.md section 0a rows 2 "
       "and 3 and section 4a name the LM5176 residual and, for the amplifier, board D's Q1. CON-010, whose allocated boards "
       "are D and A, cannot read PASS at the desk while these rows are undecided. Found missing from CON-010's links by the "
       "fresh check of the set 6 integration (v2/docs/records/int7/CHECK.md, finding B-1) and found incomplete by its re-check "
       "(CHECK-2.md, finding R-1), after which the grounds were read from the walk itself. Open until RF-002, re-taken on "
       "board A, reads both rows decided: each ground answered by a maker's figure in a held document under v2/vendor/, by a "
       "hardware element that makes it moot (one that holds the high-side gates off in shutdown whatever the controller "
       "does), by the walk learning the part's class from its maker's document where the ground is the instrument's own "
       "(U14, Q14, Q24), or by a bench reading on a built board, which is a sample of one board and is recorded as one "
       "(prototype verification).")
ENTRY_EDITS = [
    ("(the owner's review of the restart plan, %s, amendment XH-04)" % A.REVIEW,
     "(the review of the restart plan that the owner pasted, %s, amendment XH-04)" % A.REVIEW),
    ("What stays undecided is named, not judged: the SA868 exciter's PTT receive threshold, which its maker does not state "
     "(bench E-01 of v2/docs/feasibility/EMCON.md, prototype verification), and on board A the two rows fed through the "
     "LM5176 stages (the 30 W amplifier on J_PA and the QMX on J_HF), which the walk reads UNDECIDED because TI states no "
     "gate-drive level for the LM5176 in shutdown (SNVSAI1D 7.4.1; v2/docs/feasibility/EMCON.md section 0a rows 2 and 3; open "
     "item S-93).",
     "What stays undecided is named, not judged, and is every ground the walk's own report gives for the three rows "
     "(v2/docs/records/int7/walk-grounds.txt): on board D the SA868 exciter's row, on three grounds (no input threshold and "
     "no input current stated by its maker for U2 pin 5, and the off-state current of the released open-drain output U13 "
     "pin 4, which its sheet does not state; open item S-92); on board A the QMX's row on one ground (Q24 on the drive of "
     "U15, the gated LM5176 itself, for which TI states no level in shutdown, SNVSAI1D 7.4.1) and the 30 W amplifier's row "
     "on three (the same for Q14 on U13's drive; U14, the INA226 on the rail, whose pins no class of the walk reads; and the "
     "gate of board D's Q1 on PA_EN with U36's supply down, whose sheet states IGSS at 25 C only; open item S-93)."),
    ("after the fresh check of the merge, v2/docs/records/int7/CHECK.md finding B-1).",
     "after the fresh check of the merge, v2/docs/records/int7/CHECK.md finding B-1, and the grounds were completed from "
     "the walk's own report after its re-check, CHECK-2.md finding R-1)."),
]
S81_EDIT = ("The brief's row is still to be worded at its next issue, which is S-91's list; no layer is reopened.",
            "With S-64 closed the wording this item asked of the brief is moot; no layer is reopened.")
S61_OLD = A.S61_ADD.strip()
S61_NEW = ("On the unmerged branch fnd/d8dec31 (v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md there, an AI review that "
           "is not on main yet) the same port is finding D-F3 of decision 31's review of board D, which asks for a clamp, a "
           "bulk capacitor and a ferrite on it and not for this current limit; until that review is on main and its registry "
           "items name this one, nothing but this item carries the current limit, and tools/pcb_board_holds.yaml names "
           "neither.")
LINK_ADD = {"REQ-032": ["S-65"], "CFL-006": ["S-86"], "FEA-005": ["S-86"]}


def refuse(msg):
    print("apply_check2_answers: REFUSED: %s" % msg); sys.exit(1)


def replace_fold(raw, header, indent, width, new_text):
    lines = raw.split("\n"); n = lines.index(header) + 1
    a, b = A.block_at(raw, n, lines, indent)
    return "\n".join(lines[:a] + A.fold(new_text, indent, width).rstrip("\n").split("\n") + lines[b:])


def main():
    t = open(P, encoding="utf-8").read()
    if MARK in t: refuse("the registry already carries the walk's grounds (a second run)")
    before = yaml.safe_load(t)
    rec = {r["id"]: r for r in before["records"]}
    for txt, what in ((S92, "S-92"), (S93, "S-93"), (S61_NEW, "S-61's reason")): A.screen(txt, what)

    # the predicate, verdict-aware, once more
    fails, und = [], []
    for name, d in A.ELEMENTS.items():
        r = json.load(open(os.path.join(TOP, "v2/ecad", d, "routed", name + ".verdict.json"), encoding="utf-8")); c = r.get("counts") or {}
        if r.get("verdict") == "FAIL" or c.get("fail"): fails.append(name)
        elif r.get("verdict") != "PASS" or c.get("undecided"): und.append(name)
    result = "FAIL" if fails else ("INCONCLUSIVE" if und else "PASS")
    if rec["CON-010"]["evidence_result"] != result: refuse("the predicate gives %s and CON-010 reads %s" % (result, rec["CON-010"]["evidence_result"]))

    # THE COVERAGE ASSERTION: every part the walk's undecided grounds name, on CON-010's allocated boards, is in an item it waits on
    rows, nets, tool = WG.rows()
    alloc = {str(b).upper() for b in rec["CON-010"]["allocated_to"]}
    texts = {"S-92": S92, "S-93": S93}
    waits = rec["CON-010"]["waits_on"]
    if sorted(waits) != ["S-92", "S-93"]: refuse("CON-010 waits on %s" % waits)
    mine = [x for x in rows if set(x["boards"]) & alloc]
    if len(mine) != sum(json.load(open(os.path.join(TOP, "v2/ecad", d, "routed", n + ".verdict.json")))["counts"].get("undecided", 0)
                        for n, d in A.ELEMENTS.items() if n.startswith("inhibit_chain")):
        refuse("the walk's undecided rows on boards %s (%d) are not the filed readings' count" % (sorted(alloc), len(mine)))
    cover = []
    for x in mine:
        item = "S-92" if x["boards"] == ["D"] else "S-93"
        missing = [r for r in x["refs"] if not re.search(r"\b%s\b" % re.escape(r), texts[item])]
        if missing: refuse("%s does not name %s, which the walk names for the row %r" % (item, missing, x["text"][:50]))
        cover.append("%s covers %s (%s)" % (item, x["text"].split(":")[0], ", ".join(x["refs"])))

    out = t
    i, j = A.span(out, "CON-010"); r = out[i:j]
    r, _ = A.edit_fold(r, "      - >-", 10, 120, ENTRY_EDITS, first_words="v2/ecad/pcb-d-aprs-d9/routed/inhibit_chain_d.verdict.json, inhibit_chain_a")
    out = out[:i] + r + out[j:]
    for iid, txt in (("S-92", S92), ("S-93", S93)):
        i, j = A.span(out, iid); it = out[i:j]
        out = out[:i] + replace_fold(it, "    title: >-", 6, 120, txt) + out[j:]
    i, j = A.span(out, "S-61"); it = out[i:j]
    it, _ = A.edit_fold(it, "    disposition_why: >-", 6, 120, [(S61_OLD, S61_NEW)])
    out = out[:i] + it + out[j:]
    i, j = A.span(out, "S-81"); it = out[i:j]
    it, _ = A.edit_fold(it, "    closing_evidence: >-", 6, 120, [S81_EDIT])
    out = out[:i] + it + out[j:]
    for rid, add in LINK_ADD.items():
        i, j = A.span(out, rid); r = out[i:j]
        m = re.search(r"(?m)^    waits_on: \[(.*)\]\n", r)
        if not m: refuse("%s carries no waits_on line" % rid)
        have = [x.strip() for x in m.group(1).split(",") if x.strip()]
        if set(have) & set(add): refuse("%s already waits on %s" % (rid, add))
        out = out[:i] + r[:m.start()] + "    waits_on: [%s]\n" % ", ".join(have + add) + r[m.end():] + out[j:]
    if out == t: refuse("nothing changed")

    after = yaml.safe_load(out)
    rb = {r["id"]: r for r in after["records"]}
    if list(rec) != list(rb): refuse("the record list changed")
    for k in rec:
        diff = {f for f in set(rec[k]) | set(rb[k]) if rec[k].get(f) != rb[k].get(f)}
        if k == "CON-010":
            ch = [n for n, (x, y) in enumerate(zip(rec[k]["evidence"], rb[k]["evidence"])) if x != y]
            if diff != {"evidence"} or len(ch) != 1 or len(rec[k]["evidence"]) != len(rb[k]["evidence"]): refuse("CON-010: %s, entries changed %s" % (diff, ch))
        elif k in LINK_ADD:
            if diff != {"waits_on"} or rb[k]["waits_on"] != list(rec[k].get("waits_on") or []) + LINK_ADD[k]: refuse("%s: %s" % (k, diff))
        elif diff: refuse("record %s changed: %s" % (k, diff))
        for f in ("statement", "acceptance", "evidence_result", "status"):
            if rec[k].get(f) != rb[k].get(f): refuse("%s: %s changed" % (k, f))
    oa = {x["id"]: x for x in before["open_items"]}; ob = {x["id"]: x for x in after["open_items"]}
    if list(oa) != list(ob): refuse("the open item list changed")
    for k in oa:
        diff = {f for f in set(oa[k]) | set(ob[k]) if oa[k].get(f) != ob[k].get(f)}
        exp = {"S-92": {"title"}, "S-93": {"title"}, "S-61": {"disposition_why"}}.get(k, set())
        if diff != exp: refuse("open item %s: %s" % (k, diff))
    if (ob["S-92"]["title"], ob["S-93"]["title"]) != (S92, S93): refuse("the rewritten items did not round-trip")
    ca = {x["id"]: x for x in before["closed_items"]}; cb = {x["id"]: x for x in after["closed_items"]}
    if list(ca) != list(cb): refuse("the closed item list changed")
    for k in ca:
        diff = {f for f in set(ca[k]) | set(cb[k]) if ca[k].get(f) != cb[k].get(f)}
        if diff != ({"closing_evidence"} if k == "S-81" else set()): refuse("closed item %s: %s" % (k, diff))
    for sec in before:
        if sec not in ("records", "open_items", "closed_items") and before[sec] != after[sec]: refuse("section %s changed" % sec)
    open(P, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(P, encoding="utf-8").read()) != after: refuse("the file written does not re-parse to what was checked")
    print("apply_check2_answers: predicate %s; the walk (tx_inhibit.py %s) reads %d undecided row(s) on CON-010's boards %s"
          % (result, tool, len(mine), ", ".join(sorted(alloc))))
    for c in cover: print("apply_check2_answers: " + c)
    print("apply_check2_answers: REQ-032 waits on S-65; CFL-006 and FEA-005 wait on S-86; S-61's reason and S-81's closing evidence corrected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
