#!/usr/bin/env python3
"""r8int6: fill a commit message template with the ids a stream's scripts took and the base commit.
Usage: fill_msg_r8int6.py <template> <ids json or -> <base> <out>"""
import json, os, sys

tmpl, idsf, base, out = sys.argv[1:5]
t = open(tmpl, encoding="utf-8").read()
ids = json.load(open(idsf)) if idsf != "-" and os.path.exists(idsf) else {}
ids["BASE"] = base
for k, v in ids.items():
    t = t.replace("{" + k + "}", v)
for k in ("{W4B-", "{EQ-25 (", "{PWR-001 on", "{W4C-", "{BASE}", "{SC_", "{S_", "{W4DP", "{W4AE"):
    assert k not in t, "an unfilled placeholder: " + k
assert "—" not in t
open(out, "w", encoding="utf-8").write(t)
print(t.split("\n")[0])
