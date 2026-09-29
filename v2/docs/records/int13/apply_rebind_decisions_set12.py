#!/usr/bin/env python3
"""Records bound to v2/ecad/tools/pcb_decisions.yaml by sha, rebound after set 12 added decisions 56 and 57 (stream s117:
board A's charger frequency row and its FETs; MESHSAT-1357, 29 September 2026). Proved by parsing, never typed: every
decision the old file holds is present and identical in the new one, and the new file adds exactly decisions 56 and 57.
One evidence entry per record, rebound. No result changes. Refuses a second run. Run from the repository root."""
import hashlib, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
DEC = "v2/ecad/tools/pcb_decisions.yaml"


def refuse(m):
    print("apply_rebind_decisions_set12: REFUSED: %s" % m); sys.exit(2)


def items(d):
    for k in ("decisions", "records", "items"):
        if isinstance(d, dict) and isinstance(d.get(k), list): return {str(x.get("id") or x.get("number") or x.get("n")): x for x in d[k]}
    if isinstance(d, list): return {str(x.get("id") or x.get("number") or x.get("n")): x for x in d}
    refuse("cannot find the decisions list")


def main():
    old_b = subprocess.run(["git", "-C", TOP, "show", "main:" + DEC], capture_output=True, check=True).stdout
    new_b = open(os.path.join(TOP, DEC), "rb").read()
    n16 = hashlib.sha256(new_b).hexdigest()[:16]
    od, nd = items(yaml.safe_load(old_b)), items(yaml.safe_load(new_b))
    changed = [k for k in od if od[k] != nd.get(k)]
    added = sorted(set(nd) - set(od))
    if changed: refuse("decisions changed beyond the additions: %s" % changed)
    if len(added) != 2: refuse("expected exactly two added decisions, found %s" % added)
    reg = open(REG, encoding="utf-8").read()
    shas = sorted(set(re.findall(r'- "' + re.escape(DEC) + r'@([0-9a-f]{16})"', reg)) - {n16})   # binding entries only, not mentions in evidence text
    if len(shas) != 1: refuse("records carry %d older bindings of the decisions file" % len(shas))
    key = "%s@%s" % (DEC, shas[0])
    before = yaml.safe_load(reg)
    bound = [r["id"] for r in before["records"] if key in (r.get("evidence_bound_to") or [])]
    out = reg
    for rid in bound:
        entry = ("%s re-read at integration set 12 (apply_rebind_decisions_set12, %s to %s): parsed against main's file, every decision "
                 "it holds is present and identical, and exactly two are added (%s: stream s117's charger frequency row and FETs, "
                 "board A); no decision this record reads changed; rebound. No result changes." % (DEC, shas[0], n16, ", ".join(added)))
        A.screen(entry, rid)
        i, j = A.span(out, rid)
        t = out[i:j]
        m = re.search(r"(?m)^    evidence:\n", t)
        tail = t[m.end():]
        k = re.search(r"(?m)^    [a-z_]+:", tail)
        end = m.end() + (k.start() if k else len(tail))
        t = t[:end] + "      - >-\n" + A.fold(entry, 10, 120) + t[end:]
        if t.count('"%s"' % key) != 1: refuse("%s: its binding entry is not found once" % rid)
        t = t.replace('"%s"' % key, '"%s@%s"' % (DEC, n16), 1)   # the quoted binding entry, not a mention in the evidence text
        out = out[:i] + t + out[j:]
    after = yaml.safe_load(out)
    rb = {r["id"]: r for r in after["records"]}
    for r in before["records"]:
        d = {f for f in set(r) | set(rb[r["id"]]) if r.get(f) != rb[r["id"]].get(f)}
        if (r["id"] in bound and d != {"evidence", "evidence_bound_to"}) or (r["id"] not in bound and d): refuse("%s: %s" % (r["id"], d))
    open(REG, "w", encoding="utf-8").write(out)
    print("apply_rebind_decisions_set12: %d record(s) rebound to %s: %s (added %s)" % (len(bound), n16, ", ".join(bound), ", ".join(added)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
