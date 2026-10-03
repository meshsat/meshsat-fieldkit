#!/usr/bin/env python3
"""candidate_guard.py: refuse a release candidate before any suite runs when it is not the frozen candidate (MESHSAT-1357, set 28,
3 October 2026, the owner's amendment after the first set 28 suite: a registry edit after the freeze and pages rendered without
the full evidence cost a 75-minute suite and a re-freeze).

A candidate is a full commit plus the gitignored evidence its checks read (readings, held makers' documents, the rule audit). The
MANIFEST names both. It is written OUTSIDE the tree, keyed by the commit, so it is never an input of a generated output and never
part of the candidate it describes.

  candidate_guard.py record --out MANIFEST [--evidence-list FILE] [--allow-unbound OUT ...]   (in the candidate's checkout)
  candidate_guard.py check  --manifest MANIFEST [--dir CHECKOUT]
  candidate_guard.py evidence --manifest MANIFEST [--dir CHECKOUT]     (the evidence half of check, before rendering)

record refuses unless, in the checkout:
  C1 no tracked file differs from HEAD (staged, modified or deleted);
  C2 every committed output under v2/docs binds to the tree: each pin it prints as "<hex> v2/<path>" or "v2/<path> ... sha256
     <hex>" (the patterns of _bin/regen_out.py's R4) equals the start of that file's sha256, except the outputs named with
     --allow-unbound (historical snapshots the integrator declares by path; each must exist and must really be unbound);
  C3 every evidence file is present (the list: sha256sum lines, from the archive; default every ignored file under v2 except
     __pycache__, *.pyc and regen_out's temporaries).
It writes the commit, its tree, the evidence list with each sha256, the declared unbound outputs, and the frozen part of every
results cache it finds (L4-E7's KEY over its source, the files it read, its scans and its solver; the interpreter and pdftotext
versions are the host's and are recorded, not frozen).

check refuses unless the checkout's HEAD is the manifest's commit (full sha) and C1, C2 (the same unbound set, no other) and the
evidence (every listed file present with its sha256) hold, and every results cache's frozen KEY part recomputes to the manifest's.
A host whose interpreter or pdftotext differs from a cache's is named, so that module runs where they match.
Exit 0: PASS; 2: REFUSED, every failed condition printed; 1: usage."""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
# the patterns of _bin/regen_out.py's R4 (kept identical; regen_out.py lives outside the repository)
PIN_A = re.compile(r"\b([0-9a-f]{16,64})\s+(v2/\S+)")
PIN_B = re.compile(r"(v2/\S+)\s+sha256\s+([0-9a-f]{16,64})\b")
SKIP_EVIDENCE = re.compile(r"(^|/)__pycache__/|\.pyc$|/\.regen-")
CACHES = {"v2/docs/records/l4e7/l4e7_stage_settings.results.json": "v2/docs/records/l4e7/l4e7_stage_settings.py"}
HOST_PARTS = ("python", "pdftotext")


def git(top, *a):
    return subprocess.run(["git", "-C", top] + list(a), capture_output=True, text=True, check=True).stdout


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def tracked_changes(top):
    return [l for l in git(top, "status", "--porcelain", "--untracked-files=no").splitlines() if l.strip()]


def unbound_outputs(top):
    """Every committed .out under v2/docs whose printed pins are not the tree's: {output: [(path, printed, tree)]}."""
    cache, res = {}, {}
    for out in sorted(p for p in git(top, "ls-files", "v2/docs").split() if p.endswith(".out")):
        text = open(os.path.join(top, out), encoding="utf-8", errors="replace").read()
        stale = []
        for rx, order in ((PIN_A, (2, 1)), (PIN_B, (1, 2))):
            for m in rx.finditer(text):
                path, hx = m.group(order[0]), m.group(order[1])
                p = os.path.join(top, path)
                if "@" in path or not os.path.isfile(p):
                    continue
                if path not in cache:
                    cache[path] = sha256(p)
                if not cache[path].startswith(hx):
                    stale.append((path, hx[:16], cache[path][:16]))
        if stale:
            res[out] = sorted(set(stale))
    return res


def evidence_default(top):
    out = git(top, "ls-files", "--others", "--ignored", "--exclude-standard", "--", "v2").splitlines()
    return sorted(p for p in out if p and not SKIP_EVIDENCE.search(p))


def read_list(path):
    rows = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line:
            continue
        hx, rel = line[:64], line[66:].lstrip("*")
        if rel.startswith("./"):
            rel = rel[2:]
        rows.append((rel, hx))
    return rows


def cache_parts(top, cache_rel, script_rel):
    """The frozen part of a results cache's KEY (everything but the host's tool versions) recomputed on this checkout, and the
    host parts of the cache and of this host."""
    data = json.load(open(os.path.join(top, cache_rel), encoding="utf-8"))
    sp = importlib.util.spec_from_file_location("cg_" + os.path.basename(script_rel)[:-3], os.path.join(top, script_rel))
    m = importlib.util.module_from_spec(sp)
    here = os.getcwd()
    try:
        os.chdir(top)
        sp.loader.exec_module(m)
        now = m.key_parts(data["parts"]["files"])
    finally:
        os.chdir(here)
    frozen = lambda parts: hashlib.sha256(json.dumps({k: v for k, v in parts.items() if k not in HOST_PARTS},
                                                      sort_keys=True).encode("utf-8")).hexdigest()
    return dict(recorded=frozen(data["parts"]), now=frozen(now),
                host_cache={k: data["parts"].get(k) for k in HOST_PARTS}, host_here={k: now.get(k) for k in HOST_PARTS})


def evidence_failures(top, rows):
    bad = []
    for rel, hx in rows:
        p = os.path.join(top, rel)
        if not os.path.isfile(p):
            bad.append("EVIDENCE missing: %s" % rel)
        elif sha256(p) != hx:
            bad.append("EVIDENCE changed: %s" % rel)
    return bad


def do_record(a):
    top = git(os.getcwd(), "rev-parse", "--show-toplevel").strip()
    bad = ["C1 tracked file differs from HEAD: %s" % l for l in tracked_changes(top)]
    allow = sorted(set(a.allow_unbound))
    ub = unbound_outputs(top)
    for o in sorted(set(ub) - set(allow)):
        bad.append("C2 %s does not bind to the tree (%s)" % (o, "; ".join("%s printed %s tree %s" % s for s in ub[o][:3])))
    for o in allow:
        if o not in ub:
            bad.append("C2 --allow-unbound %s: it binds (or does not exist), so it may not be declared unbound" % o)
    if a.evidence_list:
        rows = read_list(a.evidence_list)
        bad += ["C3 " + x for x in evidence_failures(top, rows)]
    else:
        rows = [(p, sha256(os.path.join(top, p))) for p in evidence_default(top)]
    if not rows:
        bad.append("C3 no evidence file: a candidate's checks read gitignored evidence, so an empty list is refused")
    caches = {}
    for c, s in CACHES.items():
        if os.path.isfile(os.path.join(top, c)):
            cp = cache_parts(top, c, s)
            if cp["recorded"] != cp["now"]:
                bad.append("C4 %s: its frozen KEY part does not hold for this checkout (recompute it through regen_out)" % c)
            caches[c] = cp["recorded"]
    if bad:
        for b in bad:
            print("candidate_guard: REFUSED record: %s" % b)
        return 2
    head = git(top, "rev-parse", "HEAD").strip()
    man = dict(schema=1, commit=head, tree=git(top, "rev-parse", "HEAD^{tree}").strip(), allow_unbound=allow,
               evidence=[{"path": p, "sha256": h} for p, h in rows], caches=caches)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1, sort_keys=True)
        f.write("\n")
    print("candidate_guard: recorded %s: %d evidence file(s), %d declared unbound output(s), %d results cache(s) -> %s"
          % (head, len(rows), len(allow), len(caches), a.out))
    return 0


def do_check(a, evidence_only=False):
    top = os.path.abspath(a.dir)
    man = json.load(open(a.manifest, encoding="utf-8"))
    bad = []
    if not evidence_only:
        head = git(top, "rev-parse", "HEAD").strip()
        if head != man["commit"]:
            bad.append("the checkout is at %s, the manifest's candidate is %s" % (head, man["commit"]))
        bad += ["tracked file differs from HEAD: %s" % l for l in tracked_changes(top)]
        ub = unbound_outputs(top)
        for o in sorted(set(ub) - set(man["allow_unbound"])):
            bad.append("%s does not bind to the tree (a frozen input changed: %s)" % (o, "; ".join("%s printed %s tree %s" % s for s in ub[o][:3])))
    bad += evidence_failures(top, [(e["path"], e["sha256"]) for e in man["evidence"]])
    notes = []
    if not evidence_only:
        for c, want in man.get("caches", {}).items():
            if not os.path.isfile(os.path.join(top, c)):
                bad.append("%s is missing" % c)
                continue
            cp = cache_parts(top, c, CACHES[c])
            if cp["recorded"] != want or cp["now"] != want:
                bad.append("%s: its frozen KEY part is not the manifest's (a frozen input of its solver changed)" % c)
            if cp["host_cache"] != cp["host_here"]:
                notes.append("%s was keyed on %s; this host has %s: its module runs on a host that matches"
                             % (c, cp["host_cache"], cp["host_here"]))
    for n in notes:
        print("candidate_guard: NOTE %s" % n)
    if bad:
        for b in bad:
            print("candidate_guard: REFUSED: %s" % b)
        return 2
    print("candidate_guard: PASS %s %s: %d evidence file(s) present and unchanged%s" % (
        "evidence of" if evidence_only else "candidate", man["commit"], len(man["evidence"]),
        "" if evidence_only else ", every output binds but the %d declared, %d results cache(s) frozen" % (len(man["allow_unbound"]), len(man.get("caches", {})))))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog="candidate_guard.py")
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("record"); r.add_argument("--out", required=True); r.add_argument("--evidence-list")
    r.add_argument("--allow-unbound", action="append", default=[])
    for name in ("check", "evidence"):
        c = sub.add_parser(name); c.add_argument("--manifest", required=True); c.add_argument("--dir", default=".")
    a = ap.parse_args(argv)
    if a.cmd == "record":
        return do_record(a)
    if a.cmd in ("check", "evidence"):
        return do_check(a, evidence_only=(a.cmd == "evidence"))
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
