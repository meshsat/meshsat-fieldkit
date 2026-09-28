#!/usr/bin/env python3
"""DRAFT apply script (stream energy, MESHSAT-1357, 28 September 2026): adds ONE evidence line to REQ-072 in
v2/ecad/tools/pcb_requirements.yaml, citing records/energy/ENERGY-RECONCILIATION.md. It changes nothing else:
not the statement, not the acceptance, not evidence_result (FAIL stays FAIL). For the integrator to run; NOT
executed by the stream. Any rules_status or render that follows a registry edit is the integrator's.

It finds the REQ-072 record by its `id:` line, then its `evidence:` list, inserts the new entry as the list's last
item with the list's own indentation, asserts the old text is present and the new text differs, refuses a second
run, and re-parses the file with PyYAML afterwards to check that REQ-072's evidence list grew by exactly one entry,
that the entry is the one added, and that evidence_result is still FAIL. Usage: apply_req072_evidence_note.py
[--file <path>].
"""
import argparse
import copy
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "..", "..", "..", "ecad", "tools", "pcb_requirements.yaml")
NOTE = ("records/energy/ENERGY-RECONCILIATION.md (stream energy, 28 September 2026, on the owner's instruction of that day; "
        "energy_budget.py, inputs pinned by sha256): the balance re-run hour by hour on the reference day with the loads of "
        "POWER-THERMAL.md section 4 (42.8 W, 39 loads: 20 maker figures, 8 inside a maker's bound, 8 declarations, 3 "
        "placeholders, none measured), the aged pack's usable energy from the cell sheet and the 3.00 V graceful line "
        "(107.9 Wh, against the record's 108.1) and a 100 Wp panel in the 100 W window (320 Wh a day at the node in September, "
        "90 in December). The kit stops 8 h after a 06:00 start and 2 h after an 18:00 start; a September night (11.3 h of sun "
        "down) asks 483 Wh at 42.8 W; no panel size inside the window and no panel size without it closes the 72 hours on one "
        "pack; the load would have to fall to 8.4 W or the pack grow to 2120 Wh alone. Verdict unchanged: FAIL. The options "
        "and the smallest justified changes are that record's sections 6 and 7 and its DECISION-PARAGRAPH.md.")


def find_record(lines, rec_id):
    idx = [i for i, l in enumerate(lines) if re.match(r"^\s*-?\s*id:\s*%s\s*$" % re.escape(rec_id), l)]
    assert len(idx) == 1, "id: %s found %d times" % (rec_id, len(idx))
    return idx[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT)
    a = ap.parse_args()
    path = os.path.abspath(a.file)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if "records/energy/ENERGY-RECONCILIATION.md" in text:
        sys.stderr.write("apply_req072_evidence_note: the note is already present, refusing a second run\n")
        return 2
    before = yaml.safe_load(text)
    rec_before = [r for r in before["records"] if r.get("id") == "REQ-072"]
    assert len(rec_before) == 1, "REQ-072 not found exactly once in records"
    n_before = len(rec_before[0]["evidence"])
    assert rec_before[0]["evidence_result"] == "FAIL", "REQ-072 is not FAIL before the edit: %s" % rec_before[0]["evidence_result"]
    lines = text.split("\n")
    i0 = find_record(lines, "REQ-072")
    # the evidence key of this record: the first `evidence:` line after i0 and before the next record's id line
    j = i0 + 1
    ev = None
    while j < len(lines):
        if re.match(r"^\s*-?\s*id:\s*\S+\s*$", lines[j]):
            break
        if re.match(r"^\s*evidence:\s*$", lines[j]):
            ev = j
            break
        j += 1
    assert ev is not None, "evidence: list of REQ-072 not found"
    # the list items: consecutive lines after ev that start with the item indentation and `- `; an item may wrap
    m = re.match(r"^(\s*)- ", lines[ev + 1])
    assert m, "the first evidence item does not follow the evidence: line"
    indent = m.group(1)
    k = ev + 1
    last = k
    while k < len(lines):
        l = lines[k]
        if l.startswith(indent + "- "):
            last = k
            k += 1
            continue
        if l.strip() == "" or (l.startswith(indent + " ") and not l.startswith(indent + "- ")):
            if l.strip() == "":
                break
            last = k
            k += 1
            continue
        break
    new_item = indent + "- '" + NOTE.replace("'", "''") + "'"   # a single-quoted YAML scalar on one line
    new_lines = lines[: last + 1] + [new_item] + lines[last + 1:]
    new_text = "\n".join(new_lines)
    assert new_text != text, "the new text does not differ"
    after = yaml.safe_load(new_text)
    rec_after = [r for r in after["records"] if r.get("id") == "REQ-072"][0]
    assert len(rec_after["evidence"]) == n_before + 1, "the evidence list did not grow by exactly one"
    assert rec_after["evidence"][-1] == NOTE, "the added entry does not read back as written"
    assert rec_after["evidence_result"] == "FAIL", "evidence_result changed"
    rb, ra = copy.deepcopy(rec_before[0]), copy.deepcopy(rec_after)
    rb.pop("evidence"), ra.pop("evidence")
    assert rb == ra, "REQ-072 changed in a field other than evidence"
    others_b = [r for r in before["records"] if r.get("id") != "REQ-072"]
    others_a = [r for r in after["records"] if r.get("id") != "REQ-072"]
    assert others_b == others_a, "another record changed"
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_text)
    with open(path, encoding="utf-8") as f:
        assert yaml.safe_load(f.read()) == after, "the file does not re-parse to what was checked"
    print("apply_req072_evidence_note: added one evidence line to REQ-072 in %s (evidence %d -> %d, FAIL unchanged)" % (path, n_before, n_before + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
