#!/usr/bin/env python3
"""r8int6: every rule-board row whose result or evidence class moved between two rule-audit directories (main's, copied
before the integration's rules_status runs, and the integration's after them), with the layout-entry reason counts.
Usage: audit_diff_r8int6.py <before rule-audit dir> <after rule-audit dir>"""
import json, os, sys
A, B = sys.argv[1:3]
tot = {"moved": 0}
for f in sorted(os.listdir(B)):
    if not f.endswith(".json") or f in ("summary.json",) or "verdict" in f: continue
    a = json.load(open(os.path.join(A, f))); b = json.load(open(os.path.join(B, f)))
    ra = {r["rule"]: r for r in a["rows"]}; rb = {r["rule"]: r for r in b["rows"]}
    lines = []
    for rule in sorted(set(ra) | set(rb)):
        x, y = ra.get(rule, {}), rb.get(rule, {})
        kx = (x.get("result"), x.get("evidence_class"), x.get("evidence_cause"))
        ky = (y.get("result"), y.get("evidence_class"), y.get("evidence_cause"))
        if kx != ky:
            lines.append("  %-8s %s %s (%s) -> %s %s (%s)" % (rule, kx[0], kx[1], kx[2], ky[0], ky[1], ky[2]))
    le_a, le_b = a.get("layout_entry") or {}, b.get("layout_entry") or {}
    print("%s: %d row(s) moved; layout entry %s reasons %d -> %s reasons %d" % (f[:-5].upper(), len(lines),
          "ready" if le_a.get("ready") else "not ready", len(le_a.get("reasons") or []),
          "ready" if le_b.get("ready") else "not ready", len(le_b.get("reasons") or [])))
    for l in lines: print(l)
    tot["moved"] += len(lines)
print("total rows moved: %d" % tot["moved"])
