#!/usr/bin/env python3
"""OPTIONAL DRAFT for the owner of v2/ecad/tools/rules_render.py (stream w4r, MESHSAT-1357, 27 September 2026).

WHY. v2/docs/PCB-RULE-COVERAGE.md renders each rule's verification as `tool -> verdict`, from the row's `verdict` alone,
so INT-001's line would keep saying `-> interfaces_<letter>, check_contracts` while board E5 is decided by
check_contracts_e5 (`verification.verdict_by_board`). A reader of the page would not see it. This appends
`; on E5 -> interfaces_<letter>, check_contracts_<letter>` for each per-board line. Nothing that decides anything reads
the page.

Cost: rules_render.py is a writer (rules_complete when the render refreshes the audit) and is in jlc_certify.py's code
bundle, so its readings read TOOL_CHANGED until the next render (which the integrator runs anyway) and jlc_certify's
until re-taken or vouched, the same as patch_rules_status.py's cost; apply both in the same integration so they are
paid once.

Usage: patch_rules_render_coverage_page.py <tree root holding v2/ecad>"""
import os, sys

p = os.path.join(sys.argv[1], "v2", "ecad", "tools", "rules_render.py")
s = open(p, encoding="utf-8").read(); o = s
old = '''                    v.get("tool", "none") + ((" -> " + v["verdict"]) if v.get("verdict") else ""),
'''
new = '''                    v.get("tool", "none") + ((" -> " + v["verdict"]) if v.get("verdict") else "")
                    + "".join("; on %s -> %s" % (str(k).upper(), x) for k, x in sorted((v.get("verdict_by_board") or {}).items())),
'''
if s.count(old) != 1: raise SystemExit("patch_rules_render_coverage_page: the anchor is not there exactly once (%d)" % s.count(old))
s = s.replace(old, new); assert s != o
compile(s, p, "exec")
open(p, "w", encoding="utf-8").write(s)
print("patch_rules_render_coverage_page: the coverage page shows per-board verdicts")
