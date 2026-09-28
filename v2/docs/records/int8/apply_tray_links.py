#!/usr/bin/env python3
"""The records that wait on the QMX lid tray, after the r2 set (MESHSAT-1357, integration set 7, 28 September 2026).

Stream w5tray's draft (v2/docs/records/w5tray/drafts/apply_w5tray.py) records the r2 set as a session choice that closes
S-63 and opens two items: the lid harness's crossing of the sealed face, and what the desk cannot close on the r2 set.
It leaves FEA-007 waiting on the closed S-63 and the two new items with no record waiting on them, which the registry's
validator refuses. This script, run by the registry's writer after that draft, reads the three ids the draft took
(ids-taken.json beside it) and:

  FEA-007 (the kit's fit in the case) stops waiting on S-63, cites the session choice that closed it under `choices`,
  and waits on both new items: the verification item holds the two knob rows that read OPEN on the model and the checks
  T8 and T9 of the build; the crossing item holds a part of the face plate and of the case set that is not designed.
  REQ-021 (the face is built to an IP67-class construction) waits on the crossing item: a crossing of the sealed face is
  a penetration its construction has to seal.

CON-008 is not linked: it forbids an ingress claim until the seal procedure and TEST-PLAN E6 and E7 have run, and the
crossing changes what those tests cover, not whether a claim is made. No statement, acceptance, status or
evidence_result changes. The script re-parses the file, asserts that only these fields changed, and refuses a second
run. Run from the repository root before rules_status: python3 <this file>."""
import json, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
IDS = os.path.join(TOP, "v2/docs/records/w5tray/drafts/ids-taken.json")
CLOSED = "S-63"


def refuse(msg):
    print("apply_tray_links: REFUSED: %s" % msg); sys.exit(2)


def span(t, rid):
    i = t.index("\n  - id: %s\n" % rid) + 1; j = t.find("\n  - id: ", i + 5)
    return i, (j + 1 if j > 0 else len(t))


def set_list(rec_text, rid, field, new):
    m = re.search(r"(?m)^    %s: \[(.*)\]\n" % field, rec_text)
    line = "    %s: [%s]\n" % (field, ", ".join(new))
    if m: return rec_text[:m.start()] + line + rec_text[m.end():]
    if "\n    status: " not in rec_text: refuse("%s: no status line to anchor %s" % (rid, field))
    return rec_text.replace("\n    status: ", "\n" + line + "    status: ", 1)


def main():
    if not os.path.exists(IDS): refuse("the tray draft has not run: %s is missing" % os.path.relpath(IDS, TOP))
    ids = json.load(open(IDS, encoding="utf-8"))
    harness, verif, choice = ids["open_harness"], ids["open_verification"], ids["session_choice"]
    t = open(P, encoding="utf-8").read()
    before = yaml.safe_load(t)
    recs = {r["id"]: r for r in before["records"]}
    opened = {i["id"] for i in before["open_items"]}
    closed = {i["id"]: i for i in before["closed_items"]}
    choices = {c["id"]: c for c in before["session_choices"]}
    if harness in (recs["FEA-007"].get("waits_on") or []): refuse("FEA-007 already waits on %s (a second run)" % harness)
    if not {harness, verif} <= opened: refuse("%s and %s are not both open items" % (harness, verif))
    if CLOSED not in closed or closed[CLOSED].get("closed_by") != choice: refuse("%s is not closed by %s" % (CLOSED, choice))
    if CLOSED not in (choices[choice].get("closes") or []): refuse("%s does not name %s under closes" % (choice, CLOSED))
    if CLOSED not in (recs["FEA-007"].get("waits_on") or []): refuse("FEA-007 does not wait on %s" % CLOSED)

    want = {
        "FEA-007": {"waits_on": [x for x in recs["FEA-007"]["waits_on"] if x != CLOSED] + [harness, verif],
                    "choices": list(recs["FEA-007"].get("choices") or []) + [choice]},
        "REQ-021": {"waits_on": list(recs["REQ-021"].get("waits_on") or []) + [harness]},
    }
    out = t
    for rid, fields in want.items():
        for field, new in fields.items():
            i, j = span(out, rid)
            out = out[:i] + set_list(out[i:j], rid, field, new) + out[j:]
    if out == t: refuse("nothing changed")

    after = yaml.safe_load(out)
    rb = {r["id"]: r for r in after["records"]}
    if list(recs) != list(rb): refuse("the record list changed")
    for k in recs:
        diff = {f for f in set(recs[k]) | set(rb[k]) if recs[k].get(f) != rb[k].get(f)}
        if diff != set(want.get(k, {})): refuse("record %s: fields changed %s" % (k, sorted(diff)))
        for f, new in want.get(k, {}).items():
            if rb[k][f] != new: refuse("%s: %s is %s, expected %s" % (k, f, rb[k][f], new))
    for sec in before:
        if sec != "records" and before[sec] != after[sec]: refuse("section %s changed" % sec)
    waited = {x for r in after["records"] for x in (r.get("waits_on") or [])}
    left = [i["id"] for i in after["open_items"] if i["id"] not in waited and not i.get("disposition")]
    if left: refuse("still unlinked and undisposed: %s" % left)
    open(P, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(P, encoding="utf-8").read()) != after: refuse("the file written does not re-parse to what was checked")
    for rid, fields in want.items():
        for f, new in fields.items(): print("apply_tray_links: %s %s: %s" % (rid, f, new))
    return 0


if __name__ == "__main__":
    sys.exit(main())
