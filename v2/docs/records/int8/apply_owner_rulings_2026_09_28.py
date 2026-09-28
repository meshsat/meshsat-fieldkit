#!/usr/bin/env python3
"""The owner's rulings of 28 September 2026 on the decision sheet (MESHSAT-1357, integration set 7): D-19 (OD-01, the case
test package: the buy route, staged) and D-20 (OD-02 as corrected the same evening: M1 and REQ-072 preserved, the energy
budget reconciled, the smallest justified changes to come back to him). Recorded in:

  the requirements registry: two owner_rulings entries; a new open item S-114 (the energy reconciliation study) that REQ-072
  and REQ-016 wait on; REQ-072 cites D-20 under rulings and gains one evidence entry (its result, statement and acceptance
  unchanged); the open items M-02 and L-07 gain one sentence each; the three records bound to CONOPS.md are rebound with an
  evidence entry naming the two sections that changed;
  v2/docs/CONOPS.md: two rows in the section 7 table and one paragraph at the end of section 3's M1;
  v2/docs/handover/ENGINEERING-QUESTIONS.md: one row in EQ-13's table.

Every old text is asserted once, the new text differs, the files are re-parsed, only the named fields change, and a second
run is refused. Run from the repository root before rules_status: python3 <this file>."""
import hashlib, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A      # span, fold, block_at, screen

REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
CON = os.path.join(TOP, "v2/docs/CONOPS.md")
EQ = os.path.join(TOP, "v2/docs/handover/ENGINEERING-QUESTIONS.md")
NEW_ITEM = "S-114"

D19 = ("OD-01 of the decision sheet of 28 September 2026: the physical-validation route is selected, with staged purchasing. The "
       "session prepares one checkout-ready list for the minimum package on one prototype case (exact compatible part numbers, VAT, "
       "shipping, total), obtains the machining quotes separately, keeps the monitor and the thermocouple logger deferred unless the "
       "test procedure shows them necessary and no existing or borrowed equipment suffices, and writes a short test brief naming the "
       "competence and the equipment required so that the owner can assign the operator. Purchasing remains the owner's: this selects "
       "the route and authorises no unpriced purchase, and buying parts closes no measurement gate. The exact case variant is confirmed "
       "before ordering (Peli states the 1450PF frame is intended for the 1450EU).")
D20 = ("OD-02 of the decision sheet of 28 September 2026, as corrected by the owner the same evening: the original mission M1 and "
       "requirement REQ-072, with their specified duration and operating conditions, are preserved; an external DC source may remain "
       "optional, but requiring it overnight is not an acceptable substitute. The session reconciles the energy budget against verified "
       "loads, usable battery energy, night duration and solar contribution, develops feasible options within the approved constraints "
       "(the case that never changes, the pack of D-06, the required mission), presents any change to battery capacity, placement or "
       "operating modes explicitly, and, if the fixed case, the pack and the mission are incompatible, demonstrates the conflict and "
       "presents the smallest justified changes for the owner's decision. Unmet criteria stay visible: REQ-072 reads FAIL until the "
       "reconciliation decides otherwise. The routes (c) to (e) of EQ-13 are not taken.")
S114 = ("(stream energy, owner ruling D-20) The energy reconciliation of mission M1 on the approved constraints: every load of the "
        "states M1 uses classed as a maker's figure, a project allocation or a bound (measured: none until the bench); the usable "
        "energy of the 4S3P pack new and aged from the cell maker's sheet and the protection and gauge windows; the dark hours at 52 N "
        "by month computed from the solar declination; the solar energy per day into the kit within REQ-016's 25 V and 100 W entry by "
        "month; an hour-by-hour balance of M1 as written for the design and the worst month with a sensitivity table; the options within "
        "the constraints (a night operating mode that still meets M1's must-hold, the usable depth of discharge, the cells the pocket "
        "admits, a second pack's location in the fixed case, the panel against the stage's ceiling, an external DC source as optional "
        "only) with their numbers; and, if M1 as written is not met, the smallest justified changes for the owner's decision. Record: "
        "v2/docs/records/energy/. Open until the study is filed and REQ-072 re-read on it; REQ-072's statement and acceptance are not "
        "rewritten.")
M02_ADD = (" Owner's instruction of 28 September 2026 (D-20): the routes (c), (d) and (e) are not chosen; the energy budget is "
           "reconciled first (S-114) and the smallest justified changes come back to the owner; M1 and REQ-072 stay as written.")
L07_ADD = (" Owner ruling D-19 (28 September 2026): the buy route is selected, staged; the checkout-ready list, the machining quotes "
           "and the operator's brief are owed by the session (READY-TO-ACT.md sections 5 and 6); purchasing remains the owner's and "
           "buying closes no measurement gate.")
REQ072_EV = ("v2/docs/CONOPS.md section 7, owner ruling D-20 of 28 September 2026: this record is preserved with its duration and its "
             "operating conditions and stays FAIL at desk; an external DC source overnight is not a substitute for the balance it "
             "states; the reconciliation study S-114 is opened and this record waits on it. This entry changes no result, statement "
             "or acceptance.")
CON_ROWS = ("| D-19 | The case test package (decision sheet OD-01) | RULED 28 Sep | the buy route, staged: one checkout-ready list for the "
            "minimum package on one prototype case, machining quotes apart, the monitor and the logger deferred unless the procedure needs "
            "them, a test brief for an operator the owner assigns; purchasing stays the owner's and no unpriced purchase is authorised; the "
            "exact case variant (1450 or 1450EU, the 1450PF frame's target) confirmed before ordering |\n"
            "| D-20 | Mission M1's energy (decision sheet OD-02, corrected) | RULED 28 Sep | M1 and REQ-072 preserved with their duration and "
            "conditions; an external DC source optional, never the overnight basis; the energy budget reconciled against verified loads, "
            "usable pack energy, night duration and solar (S-114), options within the fixed case, the D-06 pack and the mission, and the "
            "smallest justified changes presented for the owner's decision; unmet criteria stay visible |\n")
CON_M1 = ("\n**Owner's instruction of 28 September 2026 (D-20, section 7):** M1 and REQ-072 stand as written, with their duration and\n"
          "operating conditions; an external DC source may remain optional, but requiring it overnight is not a substitute. The energy\n"
          "budget is reconciled (the requirements registry's S-114, `records/energy/`) against verified loads, usable pack energy,\n"
          "night duration and solar contribution, with feasible options inside the approved constraints; any change to pack capacity,\n"
          "placement or operating modes is presented to the owner explicitly. Until then REQ-072 reads FAIL and this section is not\n"
          "restated.\n")
EQ_ROW = ("| **Owner's instruction, 28 September 2026 (D-20)** | The original M1 and REQ-072 are preserved with their duration and "
          "conditions; an external DC source may remain optional but requiring it overnight is not an acceptable substitute; the "
          "routes (c) to (e) above are not taken. The energy budget is reconciled first against verified loads, usable battery energy, "
          "night duration and solar contribution, with options inside the approved constraints, and the smallest justified changes to "
          "capacity, placement or operating modes are presented for his decision (the registry's S-114, `records/energy/`). |\n")


def refuse(msg):
    print("apply_owner_rulings_2026_09_28: REFUSED: %s" % msg); sys.exit(2)


def sha16(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]


def sections(text):
    out, cur = {}, "(head)"
    for line in text.split("\n"):
        if line.startswith("## ") or line.startswith("### "): cur = line.strip()
        out.setdefault(cur, []).append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def append_to_title(raw, add):
    """append a sentence to an item's folded title block"""
    lines = raw.split("\n")
    idx = next(n + 1 for n, l in enumerate(lines) if l == "    title: >-")
    a, b = A.block_at(raw, idx, lines, 6)
    text = " ".join(l.strip() for l in lines[a:b]) + add
    A.screen(text, "the edited title")
    new_lines = A.fold(text, 6, 120).rstrip("\n").split("\n")
    return "\n".join(lines[:a] + new_lines + lines[b:])


def add_waits(rec_text, rid, iid):
    m = re.search(r"(?m)^    waits_on: \[(.*)\]\n", rec_text)
    if not m: refuse("%s carries no waits_on line" % rid)
    have = [x.strip() for x in m.group(1).split(",") if x.strip()]
    if iid in have: refuse("%s already waits on %s" % (rid, iid))
    return rec_text[:m.start()] + "    waits_on: [%s]\n" % ", ".join(have + [iid]) + rec_text[m.end():]


def add_evidence(rec_text, rid, entry):
    m = re.search(r"(?m)^    evidence:\n", rec_text)
    if not m: refuse("%s carries no evidence list" % rid)
    # the list ends at the next 4-space key
    tail = rec_text[m.end():]
    k = re.search(r"(?m)^    [a-z_]+:", tail)
    end = m.end() + (k.start() if k else len(tail))
    block = "      - >-\n" + A.fold(entry, 10, 120)
    return rec_text[:end] + block + rec_text[end:]


def main():
    reg = open(REG, encoding="utf-8").read()
    if "\n  - id: D-19\n" in reg or "\n  - id: %s\n" % NEW_ITEM in reg: refuse("D-19 or %s exists already (a second run)" % NEW_ITEM)
    con = open(CON, encoding="utf-8").read(); eq = open(EQ, encoding="utf-8").read()
    before = yaml.safe_load(reg)
    recs = {r["id"]: r for r in before["records"]}
    items = {i["id"]: i for i in before["open_items"]}
    ids = {i["id"] for i in before["open_items"]} | {i["id"] for i in before["closed_items"]}
    if max(int(x[2:]) for x in ids if x.startswith("S-")) != int(NEW_ITEM[2:]) - 1: refuse("%s is not the next free S id" % NEW_ITEM)
    for txt, what in ((D19, "D-19"), (D20, "D-20"), (S114, NEW_ITEM), (M02_ADD, "M-02"), (L07_ADD, "L-07"), (REQ072_EV, "REQ-072 evidence")): A.screen(txt, what)
    old_con_sha = sha16(con)
    bound = [r["id"] for r in before["records"] if any(str(e).startswith("v2/docs/CONOPS.md@") for e in (r.get("evidence_bound_to") or []))]
    for rid in bound:
        e = [x for x in recs[rid]["evidence_bound_to"] if str(x).startswith("v2/docs/CONOPS.md@")][0]
        if e.split("@")[1] != old_con_sha: refuse("%s is bound to CONOPS.md@%s and the tree holds %s: rebind that first" % (rid, e.split("@")[1], old_con_sha))

    # --- CONOPS.md: two table rows after D-17's row, one paragraph before "### M2."
    m = re.search(r"(?m)^\| D-17 \|[^\n]*\n", con)
    if not m: refuse("CONOPS.md: the D-17 row is not found")
    con2 = con[:m.end()] + CON_ROWS + con[m.end():]
    k = con2.index("\n### M2. ")
    con2 = con2[:k] + CON_M1 + con2[k:]
    s0, s1 = sections(con), sections(con2)
    changed = [h for h in s1 if s0.get(h) != s1.get(h)]
    want = {"## 7. Owner questions and their rulings", "### M1. Remote site relay on pack and solar (72 hours)"}
    if set(changed) != want: refuse("CONOPS.md sections changed: %s" % changed)
    new_con_sha = sha16(con2)

    # --- ENGINEERING-QUESTIONS.md: one row after EQ-13's "Recommended next action" row
    k = eq.index("### EQ-13.")
    m = re.compile(r"(?m)^\| \*\*Recommended next action\*\* \|[^\n]*\n").search(eq, k)
    if not m: refuse("EQ-13's recommended-next-action row is not found")
    eq2 = eq[:m.end()] + EQ_ROW + eq[m.end():]

    # --- the registry
    out = reg
    k = out.index("\n# Choices the session took under the owner's standing rule")
    rulings = ("  - id: D-19\n    authority: OWNER\n    ruled_on: \"2026-09-28\"\n    title: \"the case test package: the buy route, staged\"\n"
               "    ruling: >-\n%s    source: [\"owner ruling OD-01 of 28 September 2026\", \"v2/docs/CONOPS.md section 7\", \"v2/docs/reviews/READY-TO-ACT.md sections 0, 5 and 6\"]\n"
               "  - id: D-20\n    authority: OWNER\n    ruled_on: \"2026-09-28\"\n    title: \"mission M1's energy: the requirements preserved, the budget reconciled\"\n"
               "    ruling: >-\n%s    source: [\"owner ruling OD-02 of 28 September 2026, corrected the same evening\", \"v2/docs/CONOPS.md sections 3 and 7\", \"v2/docs/handover/ENGINEERING-QUESTIONS.md EQ-13\"]\n"
               % (A.fold(D19, 6, 120), A.fold(D20, 6, 120)))
    out = out[:k + 1] + rulings + out[k + 1:]
    # the new item before closed_items
    k = out.index("\nclosed_items:\n")
    out = out[:k + 1] + "  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % (NEW_ITEM, A.fold(S114, 6, 120)) + out[k + 1:]
    for iid, add in (("M-02", M02_ADD), ("L-07", L07_ADD)):
        i, j = A.span(out, iid); out = out[:i] + append_to_title(out[i:j], add) + out[j:]
    # REQ-072: rulings, waits_on, evidence
    i, j = A.span(out, "REQ-072"); r = out[i:j]
    if "\n    rulings: [D-06]\n" not in r: refuse("REQ-072's rulings line is not [D-06]")
    r = r.replace("\n    rulings: [D-06]\n", "\n    rulings: [D-06, D-20]\n", 1)
    r = add_waits(r, "REQ-072", NEW_ITEM); r = add_evidence(r, "REQ-072", REQ072_EV)
    out = out[:i] + r + out[j:]
    i, j = A.span(out, "REQ-016"); out = out[:i] + add_waits(out[i:j], "REQ-016", NEW_ITEM) + out[j:]
    # the CONOPS-bound records
    reb = ("v2/docs/CONOPS.md re-read at integration set 7 (28 September 2026): two rows added to the section 7 table (owner rulings "
           "D-19 and D-20) and one paragraph appended to section 3's M1 (the owner's instruction that M1 and REQ-072 stand as written); "
           "every other section byte-identical by heading, the sections this record cites among them. Rebound from %s to %s; this entry "
           "changes no result." % (old_con_sha, new_con_sha))
    for rid in bound:
        i, j = A.span(out, rid); r = out[i:j]
        r = add_evidence(r, rid, reb).replace("v2/docs/CONOPS.md@%s" % old_con_sha, "v2/docs/CONOPS.md@%s" % new_con_sha, 1)
        out = out[:i] + r + out[j:]

    after = yaml.safe_load(out)
    rb = {r["id"]: r for r in after["records"]}
    if list(recs) != list(rb): refuse("the record list changed")
    for kk in recs:
        diff = {f for f in set(recs[kk]) | set(rb[kk]) if recs[kk].get(f) != rb[kk].get(f)}
        want_f = {"REQ-072": {"rulings", "waits_on", "evidence"}, "REQ-016": {"waits_on"}}
        for rid in bound: want_f[rid] = {"evidence", "evidence_bound_to"}
        if diff != want_f.get(kk, set()): refuse("record %s: fields changed %s" % (kk, sorted(diff)))
    if rb["REQ-072"]["evidence_result"] != recs["REQ-072"]["evidence_result"]: refuse("REQ-072's result moved")
    ob = {i["id"]: i for i in after["open_items"]}
    if list(ob) != list(items) + [NEW_ITEM]: refuse("the open item list changed beyond %s" % NEW_ITEM)
    for kk in items:
        d = {f for f in set(items[kk]) | set(ob[kk]) if items[kk].get(f) != ob[kk].get(f)}
        if kk in ("M-02", "L-07"):
            if d != {"title"} or not ob[kk]["title"].endswith((M02_ADD if kk == "M-02" else L07_ADD).strip()): refuse("%s: %s" % (kk, d))
        elif d: refuse("open item %s changed" % kk)
    if [x["id"] for x in after["owner_rulings"]] != [x["id"] for x in before["owner_rulings"]] + ["D-19", "D-20"]: refuse("owner_rulings changed beyond D-19 and D-20")
    for sec in before:
        if sec not in ("records", "open_items", "owner_rulings") and before[sec] != after[sec]: refuse("section %s changed" % sec)
    open(REG, "w", encoding="utf-8").write(out); open(CON, "w", encoding="utf-8").write(con2); open(EQ, "w", encoding="utf-8").write(eq2)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("the registry written does not re-parse to what was checked")
    if sha16(open(CON, encoding="utf-8").read()) != new_con_sha: refuse("CONOPS.md written differs from what was bound")
    print("apply_owner_rulings_2026_09_28: D-19 and D-20 recorded; %s opened (REQ-072 and REQ-016 wait on it); M-02 and L-07 extended; "
          "CONOPS.md section 7 and M1 written and %s rebound (%s -> %s); EQ-13's table extended" % (NEW_ITEM, ", ".join(bound), old_con_sha, new_con_sha))
    return 0


if __name__ == "__main__":
    sys.exit(main())
