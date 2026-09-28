#!/usr/bin/env python3
"""Records bound to a board's committed netlist by sha, after a CIRCUIT change (MESHSAT-1357, integration set 9, S-99 on board A).
Unlike a re-export, the new netlist differs in content, so identity cannot be proved. This script parses main's netlist and the
tree's (tx_inhibit.parse_netlist: components with value and footprint, nets with their nodes) and computes what changed: the
parts added, removed or changed (value or footprint), and the nets whose node set changed. For every record bound to the old
netlist it collects the identifiers its statement and evidence name (part references and net names as whole words) and:
  * if none of them is a changed part or net, the record's reading rests on circuitry this change did not touch: it is rebound
    with one evidence entry naming the diff it was read against;
  * otherwise the record is NOT rebound here: it is listed with the changed identifiers it names, and must be re-read by hand
    (a JUDGED map passed on the command line as RID=reason pairs rebinds it with that reason written into the entry).
Records bound to the board's generator (--gen <path>) move with it: the generator's change IS the circuit change the
netlist shows, so the same judgement covers both bindings.
Usage (repository root): python3 <this file> <board letter> <netlist path> [--gen <generator path>] [--list] [RID="reason" ...].
--list prints each bound record with the changed identifiers it names and writes nothing. Refuses a second run."""
import hashlib, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import apply_check1_answers as A
import tx_inhibit as TX
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
WORD = re.compile(r"[A-Za-z0-9_+./-]+")


def refuse(m):
    print("apply_rebind_after_circuit: REFUSED: %s" % m)
    sys.exit(2)


def sha16(b): return hashlib.sha256(b).hexdigest()[:16]


def main():
    if len(sys.argv) < 3: refuse("usage: <letter> <netlist path> [RID=reason ...]")
    letter, rel = sys.argv[1], sys.argv[2]
    rest = sys.argv[3:]
    listing = "--list" in rest
    gen = None
    if "--gen" in rest:
        gen = rest[rest.index("--gen") + 1]
    judged = dict(a.split("=", 1) for a in rest if "=" in a)
    old_b = subprocess.run(["git", "-C", TOP, "show", "main:" + rel], capture_output=True, check=True).stdout
    new_b = open(os.path.join(TOP, rel), "rb").read()
    o16, n16 = sha16(old_b), sha16(new_b)
    if o16 == n16: refuse("the netlist is main's: nothing to rebind")
    tmp = os.path.join(TOP, ".rebind-old.net")
    open(tmp, "wb").write(old_b)
    try:
        old, new = TX.parse_netlist(tmp), TX.parse_netlist(os.path.join(TOP, rel))
    finally:
        os.remove(tmp)
    oc, nc = old["comps"], new["comps"]
    parts = sorted(set(oc) ^ set(nc)) + sorted(r for r in set(oc) & set(nc) if (oc[r]["value"], oc[r].get("fp")) != (nc[r]["value"], nc[r].get("fp")))
    on, nn = old["nets"], new["nets"]
    def nodes(d, k): return sorted((r, p) for r, p, *_ in d.get(k, []))
    nets = sorted(k for k in set(on) | set(nn) if nodes(on, k) != nodes(nn, k))
    changed = set(parts) | set(nets) | {n.lstrip("/") for n in nets}
    print("changed parts: %s" % parts)
    print("changed nets: %s" % nets)
    reg = open(REG, encoding="utf-8").read()
    if "apply_rebind_after_circuit %s %s" % (letter, n16) in reg: refuse("already applied")
    before = yaml.safe_load(reg)
    key = "%s@%s" % (rel, o16)
    keys = {key: "%s@%s" % (rel, n16)}
    if gen:
        g_old = sha16(subprocess.run(["git", "-C", TOP, "show", "main:" + gen], capture_output=True, check=True).stdout)
        g_new = sha16(open(os.path.join(TOP, gen), "rb").read())
        if g_old == g_new: refuse("the generator %s is main's" % gen)
        keys["%s@%s" % (gen, g_old)] = "%s@%s" % (gen, g_new)
    bound = [r for r in before["records"] if set(keys) & set(r.get("evidence_bound_to") or [])]
    out, done, manual = reg, [], []
    if listing:
        for r in bound:
            text = " ".join(str(x) for x in (r.get("evidence") or [])) + " " + str(r.get("statement", "")) + " " + str(r.get("acceptance", ""))
            hit = sorted(changed & set(WORD.findall(text)))
            print("%s bound to %s: names changed %s" % (r["id"], sorted(k for k in keys if k in (r.get("evidence_bound_to") or [])), hit or "nothing"))
        print("apply_rebind_after_circuit: listed %d record(s), nothing written" % len(bound))
        return 0
    for r in bound:
        text = " ".join(str(x) for x in (r.get("evidence") or [])) + " " + str(r.get("statement", "")) + " " + str(r.get("acceptance", ""))
        hit = sorted(changed & set(WORD.findall(text)))
        if hit and r["id"] not in judged:
            manual.append((r["id"], hit)); continue
        why = judged.get(r["id"]) or "none of the parts or nets this record names changed"
        moved = [k for k in keys if k in (r.get("evidence_bound_to") or [])]
        subj = " and ".join(k.split("@")[0] for k in moved)
        entry = ("%s re-read at integration set 9 (apply_rebind_after_circuit %s %s): the circuit change of S-99 (decision 55) was "
                 "compared with main's netlist %s by parsed components and net node sets; changed parts %s; changed nets %s. %s; "
                 "rebound to the new files (netlist %s). No result changes." % (subj, letter, n16, o16, ", ".join(parts) or "none",
                                                                             ", ".join(nets) or "none", why[0].upper() + why[1:], n16))
        A.screen(entry, r["id"])
        i, j = A.span(out, r["id"])
        t = out[i:j]
        m = re.search(r"(?m)^    evidence:\n", t)
        tail = t[m.end():]
        k = re.search(r"(?m)^    [a-z_]+:", tail)
        end = m.end() + (k.start() if k else len(tail))
        t = t[:end] + "      - >-\n" + A.fold(entry, 10, 120) + t[end:]
        for ok_, nk_ in keys.items():
            if ok_ in t: t = t.replace(ok_, nk_, 1)
        out = out[:i] + t + out[j:]
        done.append(r["id"])
    if manual:
        for rid, hit in manual: print("READ BY HAND: %s names changed %s" % (rid, hit))
        refuse("%d record(s) name changed parts or nets; pass RID=reason for each after reading it" % len(manual))
    after = yaml.safe_load(out)
    rb = {r["id"]: r for r in after["records"]}
    for r in before["records"]:
        d = {f for f in set(r) | set(rb[r["id"]]) if r.get(f) != rb[r["id"]].get(f)}
        if (r["id"] in done and d != {"evidence", "evidence_bound_to"}) or (r["id"] not in done and d): refuse("%s: %s" % (r["id"], d))
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("apply_rebind_after_circuit: %d record(s) rebound from %s to %s: %s" % (len(done), o16, n16, ", ".join(done)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
