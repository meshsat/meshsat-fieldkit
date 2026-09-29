#!/usr/bin/env python3
"""Records bound to any board's committed netlist by sha, rebound after set 10's regeneration of all six schematics
(MESHSAT-1357, integration set 10, 29 September 2026; a copy of records/int9/apply_rebind_netlists_int11.py widened to six boards).
The regeneration on the KiCad box (records/int11/box_regen_all.sh) wrote every netlist anew after the decoupling tools entered
every generator's import closure; regen_compare read them PARITY_AFTER_NOISE. This script PROVES the identity itself: it reads each netlist as
main holds it and as the tree holds it, drops only the lines that carry the export's `(date ...)` and `(source ...)`, and
asserts the rest is byte-identical, so every component, value, footprint, pin and net is unchanged. It then rebinds every
record bound to the old netlist sha, with one evidence entry each that starts with the file's path and states what was
compared. No result changes; a second run is refused. Run from the repository root: python3 <this file>."""
import hashlib, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
NETS = ["v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net",
        "v2/ecad/pcb-c-display-c8/out/pcb-c-display.net", "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net",
        "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net", "v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net"]


def refuse(m):
    print("apply_rebind_netlists_int11: REFUSED: %s" % m)
    sys.exit(2)


def sha16(b): return hashlib.sha256(b).hexdigest()[:16]


def body(b):
    return b"\n".join(l for l in b.split(b"\n") if b"(date " not in l and b"(source " not in l)


def main():
    reg = open(REG, encoding="utf-8").read()
    if "apply_rebind_netlists_int11" in reg: refuse("already applied")
    shas, dropped = {}, {}
    for n in NETS:
        old = subprocess.run(["git", "-C", TOP, "show", "main:" + n], capture_output=True, check=True).stdout
        new = open(os.path.join(TOP, n), "rb").read()
        if body(old) != body(new): refuse("%s differs from main's in more than its date and source lines" % n)
        if old == new: continue   # an unchanged file keeps its bindings
        shas[n] = (sha16(old), sha16(new))
        dropped[n] = len(old.split(b"\n")) - len(body(old).split(b"\n"))
    before = yaml.safe_load(reg)
    recs = {r["id"]: r for r in before["records"]}
    touched = []
    out = reg
    for r in before["records"]:
        hits = [n for n in shas if "%s@%s" % (n, shas[n][0]) in (r.get("evidence_bound_to") or [])]
        if not hits: continue
        i, j = A.span(out, r["id"])
        t = out[i:j]
        for n in hits:
            o, nw = shas[n]
            entry = ("%s re-read at integration set 10 (29 September 2026): regenerated on the KiCad box after stream d6dec's "
                     "decoupling tools entered every generator's import closure; main's file at %s and the tree's at %s were compared with only their %d date and source "
                     "line(s) dropped and are byte-identical, so every component, value, footprint, pin and net this record's reading "
                     "rests on is unchanged; rebound (apply_rebind_netlists_int11.py). No result changes." % (n, o, nw, dropped[n]))
            m = re.search(r"(?m)^    evidence:\n", t)
            if not m: refuse("%s has no evidence list" % r["id"])
            tail = t[m.end():]
            k = re.search(r"(?m)^    [a-z_]+:", tail)
            end = m.end() + (k.start() if k else len(tail))
            t = t[:end] + "      - >-\n" + A.fold(entry, 10, 120) + t[end:]
            # the binding list only: a record's own evidence prose may quote the same path@sha (REQ-044 does)
            mb = re.search(r"(?m)^    evidence_bound_to:.*(?:\n      .*)*", t)
            if not mb or ("%s@%s" % (n, o)) not in mb.group(0): refuse("%s: the binding is not in its evidence_bound_to block" % r["id"])
            blk = mb.group(0).replace("%s@%s" % (n, o), "%s@%s" % (n, nw), 1)
            t = t[:mb.start()] + blk + t[mb.end():]
        out = out[:i] + t + out[j:]
        touched.append(r["id"])
    if not touched: refuse("no record is bound to the old netlists")
    after = yaml.safe_load(out)
    rb = {r["id"]: r for r in after["records"]}
    for k in recs:
        d = {f for f in set(recs[k]) | set(rb[k]) if recs[k].get(f) != rb[k].get(f)}
        if (k in touched and d != {"evidence", "evidence_bound_to"}) or (k not in touched and d): refuse("%s: %s" % (k, d))
        if rb[k].get("evidence_result") != recs[k].get("evidence_result"): refuse("%s's result moved" % k)
    for sec in before:
        if sec != "records" and before[sec] != after[sec]: refuse("section %s changed" % sec)
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("apply_rebind_netlists_int11: %d records rebound (%s); %s" % (len(touched), ", ".join(touched),
          "; ".join("%s %s -> %s" % (os.path.basename(n), shas[n][0], shas[n][1]) for n in shas)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
