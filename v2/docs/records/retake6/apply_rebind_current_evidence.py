#!/usr/bin/env python3
"""retake6 (MESHSAT-1357): CON-010 and REQ-044 are bound to v2/docs/CURRENT-EVIDENCE.md by sha256/16, and the consolidated
re-take on the set 6 netlists re-rendered that page. This script re-reads the rows each record rests on in the NEW page
and in the readings behind them, writes what they read into one evidence entry per record (the entry starts with the
file's path, names the sections that differ from the page the record was bound to and the rows that were re-read), and
rebinds the record to the new page. It changes nothing else in pcb_requirements.yaml: no evidence_result, no status, no
other record.

What it asserts before it writes (a claim in the entry is read from the tree, never typed from memory):
  * each record is bound to the page at OLD and the tree's page is not OLD (a second run is refused);
  * the page committed at HEAD is the page the records were bound to (OLD);
  * the rows named below are on the new page with the result and class the entry states;
  * the readings behind them (tracked, under <phase>/routed/) carry the counts the entry states.
After writing it re-parses the file with the registry's own loader and checks that only the two records changed, each
by one evidence entry and one binding.

THE ENTRY'S WORDS ARE SCREENED TOO. REQUIREMENTS-TRACE.md prints every evidence entry and claims_check.py (ENV-002)
screens that page. The first wording of REQ-044's entry named the review of D-09 by the adjective the screen counts as
a claim word, in a sentence the screen's negation pattern does not reach: claims_check, asked in a scratch verdict
directory on the final documents, read 92 claim sentences and 1 unqualified where the tree's reading says 91 and 0
(box log rebind-attempt1/claims-final.log). The entry now carries no claim word, so the documents the tree's ENV-002
reading was taken on and the final documents screen the same (91 and 0), and the script refuses an entry that the
screen's own CLAIM pattern matches.

Usage, from the repository root, after the final render and before its commit:
  python3 v2/docs/records/retake6/apply_rebind_current_evidence.py
Exit 0 written; 1 refused (already bound, or an assertion about the tree does not hold).
"""
import hashlib, json, os, re, subprocess, sys
sys.dont_write_bytecode = True

P = "v2/ecad/tools/pcb_requirements.yaml"
CE = "v2/docs/CURRENT-EVIDENCE.md"
OLD = "856a59529bb3f5a1"
CANDIDATE = "73ae2f21"


def refuse(msg):
    print("apply_rebind_current_evidence: REFUSED: %s" % msg); sys.exit(1)


def sha16(b): return hashlib.sha256(b).hexdigest()[:16]


def sections(page):
    """[(heading, body)] split on the page's own headings; the text before the first is 'the head'."""
    out = [["the head (headline and introduction)", []]]
    for line in page.split("\n"):
        if line.startswith("## ") or line.startswith("### "): out.append([line.lstrip("# ").strip(), []])
        else: out[-1][1].append(line)
    return [(h, "\n".join(b)) for h, b in out]


def row(page, start):
    hits = [" ".join(l.split()) for l in page.split("\n") if l.startswith(start)]
    if len(hits) != 1: refuse("%d row(s) begin %r on the page, one expected" % (len(hits), start))
    return hits[0]


def reading(path):
    try: return json.load(open(path, encoding="utf-8"))
    except Exception as e: refuse("%s cannot be read (%s)" % (path, e))


def layout_reasons(page):
    n = {}; on = False
    for line in page.split("\n"):
        if line.startswith("| board | rule | reading now |"): on = True; continue
        if on:
            if not line.startswith("|"):
                if n: break
                continue
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if set(c[0]) <= set("-"): continue
            n[c[0]] = n.get(c[0], 0) + 1
    return n


def wrap(s):
    words = s.split(); lines = []; cur = "         "
    for w in words:
        if len(cur) + 1 + len(w) > 120: lines.append(cur); cur = "          " + w
        else: cur += " " + w
    return "\n".join(lines + [cur]) + "\n"


def rec_span(t, rid):
    i = t.index("\n  - id: %s\n" % rid) + 1; j = t.find("\n  - id: ", i + 5)
    return i, (j + 1 if j > 0 else len(t))


def main():
    if not (os.path.exists(P) and os.path.exists(CE)): refuse("run from the repository root")
    t = open(P, encoding="utf-8").read()
    new_page = open(CE, encoding="utf-8").read()
    new = sha16(new_page.encode("utf-8"))
    old_page = subprocess.run(["git", "show", "HEAD:" + CE], capture_output=True, text=True, check=True).stdout
    if new == OLD: refuse("the tree's page is the page the records are bound to (%s): nothing was rendered" % OLD)
    if sha16(old_page.encode("utf-8")) != OLD:
        refuse("the page at HEAD is %s, not %s: this script was written against the set 6 candidate's page"
               % (sha16(old_page.encode("utf-8")), OLD))
    for rid in ("CON-010", "REQ-044"):
        i, j = rec_span(t, rid)
        if '"%s@%s"' % (CE, new) in t[i:j]: refuse("%s is already bound to %s (a second run)" % (rid, new))
        if t[i:j].count('"%s@%s"' % (CE, OLD)) != 1: refuse("%s is not bound to the page at %s" % (rid, OLD))

    # --- what differs between the two pages, by the page's own sections
    so, sn = sections(old_page), sections(new_page)
    if [h for h, _ in so] != [h for h, _ in sn]: refuse("the two pages do not carry the same headings")
    differ = [h for (h, a), (_, b) in zip(so, sn) if a != b]
    same = [h for (h, a), (_, b) in zip(so, sn) if a == b]
    lo, ln = layout_reasons(old_page), layout_reasons(new_page)
    order = ["A", "B", "C", "D", "E", "P", "E5"]
    counts = "layout-entry reasons %d to %d (%s)" % (sum(lo.values()), sum(ln.values()),
             ", ".join("%s %d to %d" % (b, lo.get(b, 0), ln.get(b, 0)) for b in order))

    # --- the rows the two records rest on, read on the new page, and the readings behind them
    want = {
        "| D | RF-002 ": "| D | RF-002 INCONCLUSIVE | CURRENT_CANDIDATE (BOUND) |",
        "| A | RF-002 ": "| A | RF-002 INCONCLUSIVE | CURRENT_CANDIDATE (BOUND) |",
        "| D | SCH-004 ": "| D | SCH-004 a safety line fails safe | SCHEMATIC | safe_lines_d: netlist 7a2c0ac2190b141a is the current candidate's |",
        "| A | SCH-004 ": "| A | SCH-004 a safety line fails safe | SCHEMATIC | safe_lines_a: netlist 0a2b59087bcc2678 is the current candidate's |",
        "| C | RF-002 ": "| C | RF-002 transmit inhibit is hardware | SCHEMATIC | inhibit_chain_c: netlist 3fddbb3edcd4248a is the current candidate's |",
        "| P | BAT-001 ": "| P | BAT-001 FAIL | CURRENT_CANDIDATE (BOUND) |",
    }
    for start, begins in want.items():
        got = row(new_page, start)
        if not got.startswith(begins): refuse("the row %r reads %r" % (start, got[:160]))
    old_rows = {k: row(old_page, k) for k in ("| D | RF-002 ", "| A | RF-002 ", "| P | BAT-001 ")}
    for k, begins in (("| D | RF-002 ", "| D | RF-002 FAIL | AWAITING_REVALIDATION (TOOL_CHANGED) |"),
                      ("| A | RF-002 ", "| A | RF-002 FAIL | AWAITING_REVALIDATION (TOOL_CHANGED) |"),
                      ("| P | BAT-001 ", "| P | BAT-001 FAIL | AWAITING_REVALIDATION (CONFIG_CHANGED) |")):
        if not old_rows[k].startswith(begins): refuse("the old page's row %r reads %r" % (k, old_rows[k][:160]))
    R = "v2/ecad/%s/routed/%s.verdict.json"
    d = reading(R % ("pcb-d-aprs-d9", "inhibit_chain_d")); a = reading(R % ("pcb-a-power-a23", "inhibit_chain_a"))
    c = reading(R % ("pcb-c-display-c8", "inhibit_chain_c")); p = reading(R % ("pcb-p-pack-p2", "pack_protection"))
    sd = reading(R % ("pcb-d-aprs-d9", "safe_lines_d")); sa = reading(R % ("pcb-a-power-a23", "safe_lines_a"))
    if (d["verdict"], d["counts"], d["denominator"]) != ("INCONCLUSIVE", {"fail": 0, "pass": 7, "undecided": 1, "unjudged": 0}, 8):
        refuse("inhibit_chain_d reads %s %s" % (d["verdict"], d["counts"]))
    if (a["verdict"], a["counts"], a["denominator"]) != ("INCONCLUSIVE", {"fail": 0, "pass": 7, "undecided": 2, "unjudged": 0}, 9):
        refuse("inhibit_chain_a reads %s %s" % (a["verdict"], a["counts"]))
    if (c["verdict"], c["denominator"]) != ("PASS", 6): refuse("inhibit_chain_c reads %s of %s" % (c["verdict"], c["denominator"]))
    if (sd["verdict"], sa["verdict"]) != ("PASS", "PASS"): refuse("safe_lines reads %s, %s" % (sd["verdict"], sa["verdict"]))
    if d["evidence"] != ["undecided: RF-002 SA868 VHF exciter: EMCON reaches it in hardware (D key on U2)"]:
        refuse("inhibit_chain_d's undecided row is %r" % d["evidence"])
    if a["evidence"] != ["undecided: RF-002 30 W VHF power amplifier (RA30H1317M1 on the plate): EMCON reaches it in hardware (A power on J_PA)",
                         "undecided: RF-002 QMX HF transceiver: EMCON reaches it in hardware (A power on J_HF)"]:
        refuse("inhibit_chain_a's undecided rows are %r" % a["evidence"])
    if (p["verdict"], p["denominator"], p["counts"].get("fail")) != ("FAIL", 63, 3):
        refuse("pack_protection reads %s, %s of %s" % (p["verdict"], p["counts"].get("fail"), p["denominator"]))
    if len(p["evidence"]) != 3: refuse("pack_protection names %d failing checks" % len(p["evidence"]))

    how = ("%s re-read at the consolidated re-take on the set 6 netlists (worker retake6, 27 September 2026): "
           "retake_schematic_phase.py --run --in-place --routed in a clean clone of the set 6 candidate %s on the KiCad box "
           "with the candidate's gitignored evidence restored, reliability.py and claims_check.py re-taken as well, then "
           "rules_status three times and rules_render (the file at %s before). Of the page's %d sections %d differ from "
           "that file (%s) and %d are byte-identical (%s); %s." % (
               CE, CANDIDATE, OLD, len(sn), len(differ), "; ".join(differ), len(same), "; ".join(same) or "none", counts))
    notes = {
        "CON-010": how + (
            " The rows this reading rests on were re-read on the new page: RF-002 reads INCONCLUSIVE on CURRENT_CANDIDATE "
            "(BOUND) evidence on board D and on board A, where the file before read FAIL awaiting revalidation "
            "(TOOL_CHANGED) on both, and SCH-004 reads PASS on the current candidate on both (safe_lines_d on netlist "
            "7a2c0ac2190b141a, safe_lines_a on netlist 0a2b59087bcc2678). The readings behind the RF-002 rows: "
            "inhibit_chain_d 7 pass, 0 failed and 1 undecided of 8, the undecided check being the SA868 exciter's (D key on "
            "U2); inhibit_chain_a 7 pass, 0 failed and 2 undecided of 9, the undecided checks being the power amplifier's (A "
            "power on J_PA) and the QMX's (A power on J_HF); and board C's inhibit_chain_c PASS of 6 on netlist "
            "3fddbb3edcd4248a, so the check that failed at the re-take of 8ea7867e (TX_INHIBIT_n's level with board C "
            "unpowered, W3T-F1) no longer fails on any board. This entry rebinds the page and does not re-decide the "
            "record: evidence_result was set to FAIL on RF-002's FAIL rows, those rows now read INCONCLUSIVE, and whether "
            "the record returns to INCONCLUSIVE is the registry writer's re-read (the re-take changes no declaration), so "
            "until then it stands FAIL as it was set, bound to the file at %s" % new),
        "REQ-044": how + (
            " The row this reading rests on was re-read on the new page: board P's BAT-001 reads FAIL on CURRENT_CANDIDATE "
            "(BOUND) evidence, where the file before read FAIL awaiting revalidation (CONFIG_CHANGED). The reading behind "
            "it: pack_protection re-taken on netlist 760ac6f74d62d194 with the table as set 6 wrote it reads FAIL, 3 of 63 "
            "checks: %s. The review D-09 asks for before the pack board is released is still not engaged, and a re-take "
            "does not change that; this entry rebinds the page and does not re-decide the record, so it stays "
            "INCONCLUSIVE, bound to the file at %s"
            % ("; ".join(str(e) for e in p["evidence"]), new)),
    }
    out = t
    for rid, note in notes.items():
        if not note.startswith(CE): refuse("the entry for %s does not start with the file's path" % rid)
        sys.path.insert(0, "v2/ecad/tools")
        import claims_check as _cc
        hit = _cc.CLAIM.search(note)
        if hit: refuse("the entry for %s carries the claim word %r, which the ENV-002 screen would count on the trace page"
                       % (rid, hit.group(0)))
        i, j = rec_span(out, rid); r = out[i:j]
        res0 = re.search(r"(?m)^    evidence_result: (\S+)", r).group(1)
        r2 = r.replace('"%s@%s"' % (CE, OLD), '"%s@%s"' % (CE, new))
        k = r2.index("    evidence_bound_to:")
        r2 = r2[:k] + "      - >-\n" + wrap(note) + r2[k:]
        assert r2 != r and re.search(r"(?m)^    evidence_result: (\S+)", r2).group(1) == res0
        out = out[:i] + r2 + out[j:]
    if out == t: refuse("the new text does not differ from the old")

    # --- re-parse both texts with the registry's loader and compare record by record
    import yaml
    A, B = yaml.safe_load(t), yaml.safe_load(out)
    ra = {r["id"]: r for r in A["records"]}; rb = {r["id"]: r for r in B["records"]}
    if list(ra) != list(rb): refuse("the record list changed")
    if {k: v for k, v in A.items() if k != "records"} != {k: v for k, v in B.items() if k != "records"}:
        refuse("something outside the records changed")
    moved = [k for k in ra if ra[k] != rb[k]]
    if sorted(moved) != ["CON-010", "REQ-044"]: refuse("records changed: %s" % moved)
    for k in moved:
        x, y = ra[k], rb[k]
        keys = [f for f in set(x) | set(y) if x.get(f) != y.get(f)]
        if sorted(keys) != ["evidence", "evidence_bound_to"]: refuse("%s: fields changed: %s" % (k, keys))
        if y["evidence"][:-1] != x["evidence"] or not str(y["evidence"][-1]).startswith(CE):
            refuse("%s: the evidence list is not the old list plus one entry that starts with the path" % k)
        if sorted(set(x["evidence_bound_to"]) ^ set(y["evidence_bound_to"])) != sorted(["%s@%s" % (CE, OLD), "%s@%s" % (CE, new)]):
            refuse("%s: the bindings changed by more than the page's" % k)
    open(P, "w", encoding="utf-8").write(out)
    chk = yaml.safe_load(open(P, encoding="utf-8").read())
    if chk != B: refuse("the file written does not re-parse to what was checked")
    for k in moved:
        print("apply_rebind_current_evidence: %s rebound from %s to %s, evidence_result %s unchanged"
              % (k, OLD, new, rb[k]["evidence_result"]))
    print("apply_rebind_current_evidence: sections that differ: %s" % "; ".join(differ))
    print("apply_rebind_current_evidence: sections byte-identical: %s" % ("; ".join(same) or "none"))
    print("apply_rebind_current_evidence: %s" % counts)


if __name__ == "__main__":
    main()
