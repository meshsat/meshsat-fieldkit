#!/usr/bin/env python3
"""The registry's answers to the fresh check of the set 6 integration (MESHSAT-1357, 28 September 2026;
v2/docs/records/int7/CHECK.md, an AI review, which read the candidate 1c4235ec NOT mergeable on three findings in text
this integration wrote). Run by the registry's writer; v2/docs/records/int7/CHECK-RESPONSE.md answers every finding.

B-1  CON-010's link and S-92's text left out board A's two undecided rows, and the entry gave a reason the files do not:
     the walk reads the 30 W amplifier's and the QMX's rows UNDECIDED because TI states no gate-drive level for the
     LM5176 in shutdown (SNVSAI1D 7.4.1; tx_inhibit.py's rule for a transistor whose gate the gated switch drives;
     EMCON.md section 0a rows 2 and 3), not because it "cannot time" them. Here: S-93 is opened for that residual,
     CON-010 waits on S-92 and S-93, S-92 no longer calls itself the one dependency, and the entry's clause is corrected
     in place (the entry was written by this integration and never reached main).
B-2  Two dispositions whose reasons do not hold. S-65 (board A's +3V3 clamp above the rail's parts): EMCON.md names it
     "a registry open item" that still reaches EMCON through U30 and U40, and FEA-002 asks the inhibit to hold in every
     state of the lines' own supplies: it is LINKED from FEA-002 and REQ-030. S-86's second half corrects
     pcb_energy_chain.yaml (F1's fuse figures), a declared configuration input of energy_chain.py: it is LINKED from
     REQ-045 and FEA-004.
m5   S-81's own second closing condition is met (S-64 closed by SC-67): it is CLOSED by the commit that drew the remedy.
m6   S-13 (an order code) cannot move CON-025's capacitance constraint: the link is withdrawn and S-13 is disposed.
m7   S-61's reason names where the item is carried (decision 31's review of board D, finding D-F3).
m12  REQ-030, REQ-032 and REQ-071 stand FAIL on grounds one of which now reads 0 failed: S-94 is opened for their
     re-read by a stated predicate, and each waits on it. They are NOT re-decided here.
m2   The predicate is recomputed with a reading's VERDICT counted as well as its counts (a reading that is
     INCONCLUSIVE with no undecided count is undecided), and must give the record's result.

It changes no statement, no acceptance and no evidence_result, screens every new sentence with claims_check's CLAIM
pattern, re-parses the file, asserts that only the intended fields changed and refuses a second run."""
import json, os, re, subprocess, sys, textwrap

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import claims_check as _cc

REVIEW = "v2/docs/reviews/2026-09-28-restart-plan-review.md"
S93 = ("The LM5176 controllers' gate-drive level in shutdown, which TI does not state (SNVSAI1D 7.4.1 gives the shutdown as "
       "'VCC off, No switching' and states no level for HDRV1 and HDRV2): RF-002's walk on board A reads the 30 W power "
       "amplifier's row (A power on J_PA) and the QMX's row (A power on J_HF) UNDECIDED on it (inhibit_chain_a: 7 pass, 0 "
       "failed, 2 undecided of 9 on the set 6 netlist; v2/ecad/tools/tx_inhibit.py, the rule for a transistor whose gate is "
       "driven by the gated switch itself; v2/docs/feasibility/EMCON.md section 0a rows 2 and 3 and section 4a, which name "
       "it as the residual of board A's round 8). CON-010, whose allocated boards are D and A, cannot read PASS at the desk "
       "while these two rows are undecided. Found missing from CON-010's links by the fresh check of the set 6 integration "
       "(v2/docs/records/int7/CHECK.md, finding B-1). Open until TI states the level in a held document under v2/vendor/, "
       "or the stages are given a hardware element that holds the high-side gates off in shutdown whatever the controller "
       "does, or a bench reading on a built board gives the level (prototype verification), and RF-002 is re-taken on "
       "board A.")
S94 = ("REQ-030, REQ-032 and REQ-071 read FAIL, unchanged since before set 6, and among the grounds their evidence names is "
       "RF-002's reading of board B, which since the consolidated re-take reads 0 failed (inhibit_chain_b: 16 pass, 0 failed, "
       "4 undecided of 20; of its eleven failed rows eight were an instrument defect that 910da406 corrected in tx_inhibit.py "
       "and three were moved by circuit changes, v2/docs/records/retake6/RESULT.txt section 5). Found by the fresh check of "
       "the set 6 integration (v2/docs/records/int7/CHECK.md, m12). Each record is to be re-read by a stated predicate over "
       "the elements it rests on (RF-002 and SCH-004 on its allocated boards, and the rows of v2/docs/feasibility/EMCON.md it "
       "is bound to), as CON-010 was; until then each stands FAIL as it was set, which is the cautious reading. Open until "
       "the three are re-decided with their derivation in the evidence.")
S13_WHY = ("An order code named before an eSIM build of the RM520N-GL is bought (SC-13). CON-025's constraint is the "
           "parasitic capacitance of the TVS arrays at the SIM holders, which reads PASS on the drawn parts and which an "
           "order code of the module cannot move; the link first written at this integration was withdrawn after its fresh "
           "check (v2/docs/records/int7/CHECK.md, m6).")
S61_ADD = (" Decision 31's protection review of board D (stream d8dec31, an AI review checked on 28 September 2026 and "
           "applied after this integration) names the same port as its finding D-F3, which brings it under board D's hold "
           "before that board's layout entry.")
S81_EVIDENCE = ("v2/ecad/tools/pcb_requirements.yaml at the set 6 integration: S-64 is closed by session choice SC-67 (board C's "
                "R14 2.2 k and R50 10 k in v2/ecad/tools/gen_sch_c.py, drawn in e28f91a6), which is this item's own second "
                "closing condition ('or S-64 closes before that issue'). v2/ecad/pcb-c-display-c8/routed/inhibit_chain_c.verdict.json "
                "reads PASS of 6 and RF-002's walk reads 0 failed on every board, so CON-010 no longer reads FAIL at desk "
                "(INCONCLUSIVE, waiting on S-92 and S-93). The brief's row is still to be worded at its next issue, which is "
                "S-91's list; no layer is reopened. Closed on the fresh check's finding m5 (v2/docs/records/int7/CHECK.md).")
LINK_ADD = {"FEA-002": ["S-65"], "REQ-030": ["S-65", "S-94"], "REQ-032": ["S-94"], "REQ-071": ["S-94"],
            "REQ-045": ["S-86"], "FEA-004": ["S-86"], "CON-010": ["S-93"]}
ELEMENTS = {"inhibit_chain_d": "pcb-d-aprs-d9", "inhibit_chain_a": "pcb-a-power-a23", "safe_lines_d": "pcb-d-aprs-d9",
            "safe_lines_a": "pcb-a-power-a23"}


def refuse(msg):
    print("apply_check1_answers: REFUSED: %s" % msg); sys.exit(1)


def screen(text, what):
    hit = _cc.CLAIM.search(text)
    if hit: refuse("%s carries the claim word %r" % (what, hit.group(0)))
    if "—" in text or "–" in text: refuse("%s carries a dash" % what)


def span(t, rid):
    i = t.index("\n  - id: %s\n" % rid) + 1; j = t.find("\n  - id: ", i + 5)
    k = t.find("\nrecords:\n", i); c = t.find("\nclosed_items:\n", i)
    ends = [x + 1 for x in (j, k, c) if x > 0]
    return i, (min(ends) if ends else len(t))


def fold(text, indent, width):
    return "".join(" " * indent + l + "\n" for l in textwrap.wrap(text, width - indent, break_on_hyphens=False, break_long_words=False))


def block_at(raw, start_line_idx, lines, indent):
    """(first, last+1) line indexes of the run of lines indented `indent` that starts at start_line_idx."""
    e = start_line_idx
    while e < len(lines) and lines[e].startswith(" " * indent) and lines[e].strip(): e += 1
    return start_line_idx, e


def edit_fold(raw, header, indent, width, edits, first_words=None):
    """Replace phrases inside the folded block that follows `header` (or, for a list entry, the one whose text begins
    `first_words`) in `raw`; every old phrase must occur exactly once in the unfolded text."""
    lines = raw.split("\n")
    idx = None
    for n, l in enumerate(lines):
        if l == header and n + 1 < len(lines):
            if first_words is None or lines[n + 1].strip().startswith(first_words): idx = n + 1; break
    if idx is None: refuse("block %r (%r) not found" % (header, first_words))
    a, b = block_at(raw, idx, lines, indent)
    text = " ".join(l.strip() for l in lines[a:b])
    for old, new in edits:
        if text.count(old) != 1: refuse("%r occurs %d time(s) in the block after %r" % (old[:50], text.count(old), header))
        text = text.replace(old, new)
    screen(text if first_words is None or True else "", "the edited block after %r" % header)
    new_lines = fold(text, indent, width).rstrip("\n").split("\n")
    return "\n".join(lines[:a] + new_lines + lines[b:]), text


def main():
    t = open(P, encoding="utf-8").read()
    if "\n  - id: S-93\n" in t: refuse("S-93 is in the registry already (a second run)")
    if not os.path.exists(os.path.join(TOP, REVIEW)): refuse("%s is not filed" % REVIEW)
    before = yaml.safe_load(t)

    # m2: the predicate, verdict-aware, from the readings
    fails, und = [], []
    for name, d in ELEMENTS.items():
        p = os.path.join(TOP, "v2/ecad", d, "routed", name + ".verdict.json")
        if not os.path.exists(p): und.append(name); continue
        r = json.load(open(p, encoding="utf-8")); c = r.get("counts") or {}
        if r.get("verdict") == "FAIL" or c.get("fail"): fails.append(name)
        elif r.get("verdict") != "PASS" or c.get("undecided"): und.append(name)
    result = "FAIL" if fails else ("INCONCLUSIVE" if und else "PASS")
    rec = {r["id"]: r for r in before["records"]}
    if rec["CON-010"]["evidence_result"] != result:
        refuse("the predicate gives %s and CON-010 reads %s" % (result, rec["CON-010"]["evidence_result"]))

    out = t
    # --- B-1: CON-010's entry, history and S-92's title
    i, j = span(out, "CON-010"); r = out[i:j]
    r, _ = edit_fold(r, "      - >-", 10, 120, [
        ("(the owner's review of the restart plan, amendment XH-04)",
         "(the owner's review of the restart plan, %s, amendment XH-04)" % REVIEW),
        ("and on board A the two power-fed rows (the 30 W amplifier on J_PA and the QMX on J_HF), which the walk reaches in "
         "hardware and cannot time from a held document.",
         "and on board A the two rows fed through the LM5176 stages (the 30 W amplifier on J_PA and the QMX on J_HF), which "
         "the walk reads UNDECIDED because TI states no gate-drive level for the LM5176 in shutdown (SNVSAI1D 7.4.1; "
         "v2/docs/feasibility/EMCON.md section 0a rows 2 and 3; open item S-93)."),
        ("The record therefore waits on S-92 (opened with this entry) and no longer on S-64.",
         "The record therefore waits on S-92 and S-93 and no longer on S-64 (S-93 and this sentence's second item were added, "
         "and the clause on board A's rows corrected, after the fresh check of the merge, v2/docs/records/int7/CHECK.md "
         "finding B-1)."),
    ], first_words="v2/ecad/pcb-d-aprs-d9/routed/inhibit_chain_d.verdict.json, inhibit_chain_a")
    r, _ = edit_fold(r, "    history: >-", 6, 120, [("and waits on S-92.", "and waits on S-92 and S-93.")])
    out = out[:i] + r + out[j:]
    i, j = span(out, "S-92"); it = out[i:j]
    it, _ = edit_fold(it, "    title: >-", 6, 120, [
        ("this item is the dependency that remains.",
         "this item is one of the two dependencies that remain; the other is S-93 (the LM5176's gate drive in shutdown, "
         "behind board A's two undecided rows).")])
    out = out[:i] + it + out[j:]

    # --- B-2 and m6: dispositions withdrawn or given
    for iid in ("S-65", "S-86"):
        i, j = span(out, iid); it = out[i:j]
        m = re.search(r"(?m)^    disposition: \S+\n    disposition_why: >-\n(?:      .*\n)+", it)
        if not m: refuse("%s carries no disposition to withdraw" % iid)
        out = out[:i] + it[:m.start()] + it[m.end():] + out[j:]
    i, j = span(out, "S-13"); it = out[i:j]
    if "disposition" in it: refuse("S-13 already carries a disposition")
    screen(S13_WHY, "S-13's reason")
    it = it.replace("\n    status: OPEN\n", "\n    status: OPEN\n    disposition: PROCUREMENT\n    disposition_why: >-\n" + fold(S13_WHY, 6, 120), 1)
    out = out[:i] + it + out[j:]
    i, j = span(out, "S-61"); it = out[i:j]
    lines = it.split("\n"); n = lines.index("    disposition_why: >-") + 1
    a, b = block_at(it, n, lines, 6)
    why = " ".join(l.strip() for l in lines[a:b]) + S61_ADD
    screen(why, "S-61's reason")
    it = "\n".join(lines[:a] + fold(why, 6, 120).rstrip("\n").split("\n") + lines[b:])
    out = out[:i] + it + out[j:]

    # --- links
    i, j = span(out, "CON-025"); r = out[i:j]
    if r.count("    waits_on: [S-13]\n") != 1: refuse("CON-025 does not wait on S-13 alone")
    out = out[:i] + r.replace("    waits_on: [S-13]\n", "", 1) + out[j:]
    for rid, add in LINK_ADD.items():
        i, j = span(out, rid); r = out[i:j]
        m = re.search(r"(?m)^    waits_on: \[(.*)\]\n", r)
        if not m: refuse("%s carries no waits_on line" % rid)
        have = [x.strip() for x in m.group(1).split(",") if x.strip()]
        if set(have) & set(add): refuse("%s already waits on %s" % (rid, sorted(set(have) & set(add))))
        out = out[:i] + r[:m.start()] + "    waits_on: [%s]\n" % ", ".join(have + add) + r[m.end():] + out[j:]

    # --- m5: S-81 closed; S-93 and S-94 opened
    i, j = span(out, "S-81"); it = out[i:j]
    tm = re.search(r"(?m)^    title: >-\n((?:      .*\n)+)", it)
    if not tm or "or S-64 closes before that issue" not in " ".join(tm.group(1).split()): refuse("S-81's closing condition was not found")
    screen(S81_EVIDENCE, "S-81's closing evidence")
    closed = ("  - id: S-81\n    closed_by: commit e28f91a6\n    closing_evidence: >-\n" + fold(S81_EVIDENCE, 6, 120)
              + "    title: >-\n" + tm.group(1))
    out = out[:i] + out[j:]
    for txt, what in ((S93, "S-93"), (S94, "S-94")): screen(txt, what)
    c = out.index("\nclosed_items:\n")
    add = "".join("\n  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % (iid, fold(txt, 6, 120).rstrip("\n"))
                  for iid, txt in (("S-93", S93), ("S-94", S94)))
    out = out[:c].rstrip("\n") + add + "\n" + out[c:]
    k = out.index("\nrecords:\n")
    head = out[:k].rstrip("\n")
    tail_lines = out[:k][len(head):]
    if tail_lines.strip(): refuse("something other than blank lines stands between the closed items and the records")
    out = head + "\n" + closed.rstrip("\n") + "\n" + out[k:]

    # --- re-parse and compare
    after = yaml.safe_load(out)
    ra = rec; rb = {r["id"]: r for r in after["records"]}
    if list(ra) != list(rb): refuse("the record list changed")
    want_recs = set(LINK_ADD) | {"CON-025"}
    for k2 in ra:
        diff = {f for f in set(ra[k2]) | set(rb[k2]) if ra[k2].get(f) != rb[k2].get(f)}
        if k2 == "CON-010":
            if diff != {"evidence", "history", "waits_on"}: refuse("CON-010: fields changed %s" % diff)
            if rb[k2]["waits_on"] != ["S-92", "S-93"] or len(rb[k2]["evidence"]) != len(ra[k2]["evidence"]): refuse("CON-010's links or entry count")
            ch = [n for n, (x, y) in enumerate(zip(ra[k2]["evidence"], rb[k2]["evidence"])) if x != y]
            if len(ch) != 1 or "S-93" not in rb[k2]["evidence"][ch[0]] or "cannot time" in rb[k2]["evidence"][ch[0]]: refuse("CON-010's entry was not corrected as intended")
        elif k2 == "CON-025":
            if diff != {"waits_on"} or rb[k2].get("waits_on"): refuse("CON-025: %s" % diff)
        elif k2 in want_recs:
            if diff != {"waits_on"} or rb[k2]["waits_on"] != list(ra[k2].get("waits_on") or []) + LINK_ADD[k2]: refuse("%s: %s" % (k2, diff))
        elif diff: refuse("record %s changed: %s" % (k2, diff))
        for f in ("statement", "acceptance", "evidence_result", "status"):
            if ra[k2].get(f) != rb[k2].get(f): refuse("%s: %s changed" % (k2, f))
    oa = {x["id"]: x for x in before["open_items"]}; ob = {x["id"]: x for x in after["open_items"]}
    if list(ob) != [x for x in oa if x != "S-81"] + ["S-93", "S-94"]: refuse("open items: %s" % list(ob)[-6:])
    for k2 in ob:
        if k2 in ("S-93", "S-94"): continue
        diff = {f for f in set(oa[k2]) | set(ob[k2]) if oa[k2].get(f) != ob[k2].get(f)}
        exp = {"S-92": {"title"}, "S-65": {"disposition", "disposition_why"}, "S-86": {"disposition", "disposition_why"},
               "S-13": {"disposition", "disposition_why"}, "S-61": {"disposition_why"}}.get(k2, set())
        if diff != exp: refuse("open item %s: fields changed %s, expected %s" % (k2, diff, exp))
    if (ob["S-93"]["title"], ob["S-94"]["title"]) != (S93, S94): refuse("the new items did not round-trip")
    ca = [x["id"] for x in before["closed_items"]]; cb = {x["id"]: x for x in after["closed_items"]}
    if list(cb) != ca + ["S-81"]: refuse("closed items: %s" % list(cb)[-3:])
    if " ".join(cb["S-81"]["title"].split()) != " ".join(oa["S-81"]["title"].split()): refuse("S-81's title changed")
    for x in before["closed_items"]:
        if cb[x["id"]] != x: refuse("closed item %s changed" % x["id"])
    for sec in before:
        if sec not in ("records", "open_items", "closed_items") and before[sec] != after[sec]: refuse("section %s changed" % sec)
    waited = {x for r in after["records"] for x in (r.get("waits_on") or [])}
    left = [k2 for k2 in ob if k2 not in waited and not ob[k2].get("disposition")]
    if left: refuse("unlinked and undisposed: %s" % left)
    both = [k2 for k2 in ob if k2 in waited and ob[k2].get("disposition")]
    if both: refuse("linked and disposed at once: %s" % both)
    open(P, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(P, encoding="utf-8").read()) != after: refuse("the file written does not re-parse to what was checked")
    links = [(r["id"], w) for r in after["records"] for w in (r.get("waits_on") or []) if w in ob]
    print("apply_check1_answers: predicate (verdict-aware) %s, equal to CON-010's; CON-010 waits on S-92, S-93" % result)
    print("apply_check1_answers: open items %d (S-81 closed by commit e28f91a6; S-93, S-94 opened), closed %d" % (len(ob), len(cb)))
    print("apply_check1_answers: %d open items are linked, by %d links on %d distinct records; %d carry a disposition" % (
        len({w for _, w in links}), len(links), len({r for r, _ in links}), sum(1 for k2 in ob if ob[k2].get("disposition"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
