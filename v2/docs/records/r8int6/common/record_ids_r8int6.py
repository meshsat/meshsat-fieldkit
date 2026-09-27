#!/usr/bin/env python3
"""r8int6 (the integrator of set 6 of the handover, 27 September 2026): each stream's decision record was written before
its registry script ran, so it names the ids the script would take on the tree it was drafted on (SC-58 and so on, now
someone else's). This reads the ids the scripts actually took in the integration tree, by each record's own markers,
writes them to <kit>/ids_r8int6.json and appends one paragraph to the stream's record naming them (corrected at
integration), so the filed record and the registry agree. Idempotent (the paragraph is replaced when present).
Usage: record_ids_r8int6.py <stream> <tree> <kit dir>"""
import json, os, re, sys
import yaml

stream, T, K = sys.argv[1:4]
d = yaml.safe_load(open(os.path.join(T, "v2/ecad/tools/pcb_requirements.yaml"), encoding="utf-8"))
recs = [r for v in d.values() if isinstance(v, list) for r in v if isinstance(r, dict) and "id" in r]


def find(prefix, field, start):
    hits = [r["id"] for r in recs if r["id"].startswith(prefix + "-") and " ".join(str(r.get(field, "")).split()).startswith(start)]
    assert len(hits) == 1, (prefix, start, hits)
    return hits[0]


if stream == "w4b":
    ids = {"W4B-D1": find("SC", "why", "W4B-D1 (stream w4b)"), "W4B-D2": find("SC", "why", "W4B-D2 (stream w4b)"),
           "W4B-D3": find("SC", "why", "W4B-D3 (stream w4b)"),
           "RF-002 instrument": find("S", "title", "RF-002's instrument after stream w4b")}
    targets = ["w4b-decisions.md"]
elif stream == "w4c":
    ids = {"EQ-25 (W4C-D1)": find("SC", "question", "EQ-25 on board C (stream w4c"),
           "PWR-001 on board C (W4C-D2)": find("SC", "question", "Which kind does each supply PWR-001 refused on board C take"),
           "W4C-F1 (W4C-D3)": find("SC", "question", "Board C's RAIL_SENSE (U3 GPIO26, ADC0)"),
           "W4C-F5": find("S", "title", "Finding W4C-F5 (stream w4c")}
    targets = ["w4c-decisions.md", "README.md"]
else:
    j = json.load(open(os.path.join(K, "ids.json"), encoding="utf-8"))
    ids = {k: v for k, v in j.items() if isinstance(v, str) and re.match(r"^(SC|S)-\d+$", v)}
    if stream == "w4ae":
        ids["S_PI_KILL"] = find(
            "S", "title", "Board B's PI_KILL conductor carries the drains of the three")
    targets = sys.argv[4:] or ["README.md"]
json.dump(ids, open(os.path.join(K, "ids_r8int6.json"), "w"), indent=1)
para = ("\n\n## Ids taken at the r8int6 integration (corrected at integration)\n\nThe registry script ran at the r8int6 "
        "integration of 27 September 2026 (set 6 of the handover), where other branches had taken the numbers this record "
        "names as drafted; the ids it took there, read back from the registry by each record's own text: "
        + "; ".join("%s is %s" % (k, v) for k, v in ids.items()) + ". Where this record names another number for one of "
        "them, the id here is the one the registry holds.\n")
for t in targets:
    p = os.path.join(K, t); s = open(p, encoding="utf-8").read()
    i = s.find("\n\n## Ids taken at the r8int6 integration")
    if i >= 0: s = s[:i].rstrip("\n") + "\n"
    open(p, "w", encoding="utf-8").write(s.rstrip("\n") + para)
print("record_ids_r8int6 (%s): %s" % (stream, ids))
