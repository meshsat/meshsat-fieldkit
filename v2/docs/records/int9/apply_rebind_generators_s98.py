#!/usr/bin/env python3
"""Records bound to board A's or board B's schematic generator by sha, rebound after stream s98 (MESHSAT-1357, integration
set 8, 28 September 2026). S-98 changed gen_sch_a.py and gen_sch_b.py in their electrical-intent declarations only (the
interim alignment of the A to B power leads, and board B's M7 branch allocations) and in comments. This script PROVES that
from the code, not from the diff's words: it parses both versions of each generator (git show main:<file> and the tree's)
and asserts that every call other than an `_intent.*` declaration is identical, so no part, pin, net, value or footprint
moved; the only module-level assignment allowed to differ is board B's `_DEV_LOADS`, the +5V_DEV declaration's load map.
It then asserts that no bound record judges a declared current (each record's statement is read and must not name a
declared-current subject: the list below), writes one evidence entry per record that starts with the file's path, and
rebinds. It changes no result. Refuses a second run. Run from the repository root: python3 <this file>."""
import ast, hashlib, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
GENS = {"gen_sch_a.py": set(), "gen_sch_b.py": {"_DEV_LOADS"}}
EXPECT = ["CHO-001", "CON-017", "CFL-001", "CON-019", "CON-018", "CFL-004", "REQ-077", "REQ-052", "CON-025", "CFL-014", "CON-015"]
CURRENT_WORDS = ("typical current", "peak current", "declared current", "coincident peak", "current declaration")


def refuse(m): print("apply_rebind_generators_s98: REFUSED: %s" % m); sys.exit(2)


def sha16(b): return hashlib.sha256(b).hexdigest()[:16]


def split(src):
    tree = ast.parse(src)
    other, intent = [], []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            (intent if ast.unparse(n.func).startswith("_intent.") else other).append(ast.unparse(n))
    assigns = {}
    for n in tree.body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                assigns.setdefault(ast.unparse(t), []).append(ast.unparse(n.value))
    return sorted(other), sorted(intent), assigns


def main():
    reg = open(REG, encoding="utf-8").read()
    if "apply_rebind_generators_s98" in reg: refuse("already applied")
    facts, shas = {}, {}
    for f, allowed in GENS.items():
        p = "v2/ecad/tools/" + f
        old = subprocess.run(["git", "-C", TOP, "show", "main:" + p], capture_output=True, check=True).stdout
        new = open(os.path.join(TOP, p), "rb").read()
        oo, oi, oa = split(old.decode("utf-8")); no, ni, na = split(new.decode("utf-8"))
        if oo != no: refuse("%s: a call other than an intent declaration changed (%d differ)" % (f, len(set(oo) ^ set(no))))
        changed_assign = sorted(k for k in set(oa) | set(na) if oa.get(k) != na.get(k))
        if not set(changed_assign) <= allowed: refuse("%s: module assignments changed beyond %s: %s" % (f, sorted(allowed), changed_assign))
        facts[f] = (len(no), len(set(oi) ^ set(ni)), changed_assign)
        shas[f] = (sha16(old), sha16(new))
    before = yaml.safe_load(reg)
    recs = {r["id"]: r for r in before["records"]}
    bound = [r["id"] for r in before["records"] if any(("gen_sch_a.py@" in str(e) or "gen_sch_b.py@" in str(e)) for e in (r.get("evidence_bound_to") or []))]
    if sorted(bound) != sorted(EXPECT): refuse("bound records %s, expected %s" % (sorted(bound), sorted(EXPECT)))
    for rid in bound:
        st = str(recs[rid].get("statement", "")).lower()
        if any(wd in st for wd in CURRENT_WORDS): refuse("%s's statement names a declared current: read it by hand" % rid)
    out = reg
    for rid in bound:
        i, j = A.span(out, rid); r = out[i:j]
        for f in GENS:
            o, n = shas[f]
            if "v2/ecad/tools/%s@%s" % (f, o) not in r: continue
            nc, ni, ca = facts[f]
            entry = ("v2/ecad/tools/%s re-read at integration set 8 (28 September 2026, stream s98, S-98): the file at %s and at %s "
                     "were parsed and every call other than an electrical-intent declaration is identical (%d calls), so no part, "
                     "pin, net, value or footprint moved; %d intent declarations differ%s. This record judges no declared current, "
                     "so its reading stands; rebound (apply_rebind_generators_s98.py). No result changes."
                     % (f, o, n, nc, ni, (" and the module assignment %s (the +5V_DEV load map)" % ", ".join(ca)) if ca else ""))
            m = re.search(r"(?m)^    evidence:\n", r)
            if not m: refuse("%s has no evidence list" % rid)
            tail = r[m.end():]; k = re.search(r"(?m)^    [a-z_]+:", tail); end = m.end() + (k.start() if k else len(tail))
            r = r[:end] + "      - >-\n" + A.fold(entry, 10, 120) + r[end:]
            r = r.replace("v2/ecad/tools/%s@%s" % (f, o), "v2/ecad/tools/%s@%s" % (f, n), 1)
        out = out[:i] + r + out[j:]
    after = yaml.safe_load(out)
    rb = {r["id"]: r for r in after["records"]}
    for k in recs:
        d = {f for f in set(recs[k]) | set(rb[k]) if recs[k].get(f) != rb[k].get(f)}
        if (k in bound and d != {"evidence", "evidence_bound_to"}) or (k not in bound and d): refuse("%s: %s" % (k, d))
        if rb[k].get("evidence_result") != recs[k].get("evidence_result"): refuse("%s's result moved" % k)
    for sec in before:
        if sec != "records" and before[sec] != after[sec]: refuse("section %s changed" % sec)
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("apply_rebind_generators_s98: %d records rebound (%s); gen_sch_a.py %s -> %s, gen_sch_b.py %s -> %s; non-intent calls identical (%d and %d)"
          % (len(bound), ", ".join(bound), shas["gen_sch_a.py"][0], shas["gen_sch_a.py"][1], shas["gen_sch_b.py"][0], shas["gen_sch_b.py"][1],
             facts["gen_sch_a.py"][0], facts["gen_sch_b.py"][0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
