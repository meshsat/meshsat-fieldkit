#!/usr/bin/env python3
"""Records bound to board B's schematic generator by sha, rebound after set 12's circuit change (MESHSAT-1357, 29 September
2026; stream d4emcon's FEA-002 remedies written into gen_sch_b.py by apply_b_d4e.py). The identifiers the change touches are
computed, not typed: every token on a line that differs between main's gen_sch_b.py (asserted to be the sha the records
carry) and the tree's that is a part reference or a net of either board B netlist, together with the parts and nets that
differ between main's netlist and the tree's by parsed components and net node sets (tx_inhibit.parse_netlist). A record
whose statement, acceptance and evidence name none of them is rebound with an entry saying so; a record naming any of them
is rebound only with the integrator's reason read by hand (rebind_reasons_set12.GEN), written into the entry. No result,
status or stage changes. Refuses a second run. Run from the repository root: python3 <this file> [a|b] (board B by default)."""
import difflib, hashlib, os, re, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import apply_check1_answers as A
import tx_inhibit as TX
import rebind_reasons_set12 as R
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
BOARD = sys.argv[1] if len(sys.argv) > 1 else "b"
GEN = "v2/ecad/tools/gen_sch_%s.py" % BOARD
NET = {"a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "b": "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net"}[BOARD]
WORD = re.compile(r"[A-Za-z0-9_+./#-]+")


def refuse(m):
    print("apply_rebind_generator_b_set12: REFUSED: %s" % m)
    sys.exit(2)


def sha16(b): return hashlib.sha256(b).hexdigest()[:16]


def main():
    old_g = subprocess.run(["git", "-C", TOP, "show", "main:" + GEN], capture_output=True, check=True).stdout
    new_g = open(os.path.join(TOP, GEN), "rb").read()
    o16, n16 = sha16(old_g), sha16(new_g)
    reg = open(REG, encoding="utf-8").read()
    import re as _re
    shas = sorted(set(_re.findall(_re.escape(GEN) + r"@([0-9a-f]{16})", reg)) - {n16})
    if len(shas) != 1: refuse("records carry %d distinct older bindings of %s" % (len(shas), GEN))
    key = "%s@%s" % (GEN, shas[0])
    old_n = subprocess.run(["git", "-C", TOP, "show", "main:" + NET], capture_output=True, check=True).stdout
    with tempfile.TemporaryDirectory() as td:
        op = os.path.join(td, "old.net"); open(op, "wb").write(old_n)
        on = TX.parse_netlist(op)
    nn = TX.parse_netlist(os.path.join(TOP, NET))
    known = set(on["comps"]) | set(nn["comps"]) | set(on["nets"]) | set(nn["nets"]) | {k.lstrip("/") for k in list(on["nets"]) + list(nn["nets"])}
    a, b = old_g.decode().split("\n"), new_g.decode().split("\n")
    changed_lines = [l[1:] for l in difflib.unified_diff(a, b, lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---")]
    gen_ids = {w for l in changed_lines for w in WORD.findall(l)} & known
    oc, nc = on["comps"], nn["comps"]
    parts = set(oc) ^ set(nc) | {r for r in set(oc) & set(nc) if (oc[r]["value"], oc[r].get("fp")) != (nc[r]["value"], nc[r].get("fp"))}
    def nodes(d, k): return sorted((r, p) for r, p, *_ in d.get(k, []))
    nets = {k for k in set(on["nets"]) | set(nn["nets"]) if nodes(on["nets"], k) != nodes(nn["nets"], k)}
    changed = gen_ids | parts | nets | {n.lstrip("/") for n in nets}
    before = yaml.safe_load(reg)
    bound = [r for r in before["records"] if key in (r.get("evidence_bound_to") or [])]
    out, done, manual = reg, [], []
    for r in bound:
        text = " ".join(str(x) for x in (r.get("evidence") or [])) + " " + str(r.get("statement", "")) + " " + str(r.get("acceptance", ""))
        hit = sorted(changed & set(WORD.findall(text)))
        if hit and r["id"] not in R.GEN_BY[BOARD]:
            manual.append((r["id"], hit)); continue
        why = R.GEN_BY[BOARD].get(r["id"]) or "none of the parts or nets this record names is touched"
        entry = ("%s re-read at integration set 12 (apply_rebind_generator_b_set12, %s to %s): set 12's changes to this generator "
                 "(board B: stream d4emcon's FEA-002 remedies, the check's minors, the census nodes; board A: S-117 and the FET remedy, the census nodes); the identifiers the change touches were computed from the generator's changed lines and "
                 "both netlists (%d parts and nets). %s; rebound. No result changes." % (GEN, key.split("@")[1], n16, len(changed), why[0].upper() + why[1:]))
        A.screen(entry, r["id"])
        i, j = A.span(out, r["id"])
        t = out[i:j]
        m = re.search(r"(?m)^    evidence:\n", t)
        tail = t[m.end():]
        k = re.search(r"(?m)^    [a-z_]+:", tail)
        end = m.end() + (k.start() if k else len(tail))
        t = t[:end] + "      - >-\n" + A.fold(entry, 10, 120) + t[end:]
        t = t.replace(key, "%s@%s" % (GEN, n16), 1)
        out = out[:i] + t + out[j:]
        done.append(r["id"])
    if manual:
        for rid, hit in manual: print("READ BY HAND: %s names %s" % (rid, hit[:12]))
        refuse("%d record(s) need a reason" % len(manual))
    after = yaml.safe_load(out)
    rb = {r["id"]: r for r in after["records"]}
    for r in before["records"]:
        d = {f for f in set(r) | set(rb[r["id"]]) if r.get(f) != rb[r["id"]].get(f)}
        if (r["id"] in done and d != {"evidence", "evidence_bound_to"}) or (r["id"] not in done and d): refuse("%s: %s" % (r["id"], d))
    open(REG, "w", encoding="utf-8").write(out)
    print("apply_rebind_generator_b_set12: %d record(s) rebound from %s to %s: %s" % (len(done), o16, n16, ", ".join(done)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
