#!/usr/bin/env python3
"""Re-walk every ledger in the tree and write one verdict (MESHSAT-862, stage 1, 11 September 2026).

`ledger.py verify` re-walks ONE chain and returns a tuple; `routeflow.py selftest` exercises it on three rows it
makes up. Neither produces a verdict for the channel the supervisor now decides on, and neither looks at the
ledgers this project has actually written. This does: it finds every `out/routeflow/journal.jsonl` under the
ecad directory, re-walks each, checks it against its witness when one sits beside it, and writes one
`ledger_verify` verdict with the row count as its denominator.

What each verdict means, and why the third is not a pass:

  PASS          every chain re-walks, every row hashes to what it carries, and every witness agrees.
  FAIL          a row's content changed after it was written, a prev_sha does not join, or a witness disagrees.
  INCONCLUSIVE  no ledger was found. A tree with no ledger and a tree whose ledgers are all sound look the
                same to a checker that reports "no problems", and that is the defect this channel exists for.

Usage: ledger_verify.py [<ecad dir>] [--witness]   exit 0 PASS, 1 FAIL, 3 INCONCLUSIVE
  --witness  also write/refresh a witness beside every sound ledger, so the next run can catch a whole-file rewrite
"""
import sys, os, glob, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger, verdict

WITNESS = ".witness.json"


def is_ledger(path):
    """A chained ledger, not merely a file of JSON lines.

    The first version of this globbed every .jsonl under the tree and reported
    `tools/routeflow/bench/results.jsonl` as 708 broken rows. That file is the benchmark table: plain rows with
    no chain on them, and never claimed one. A checker that calls an unchained file a broken chain is crying
    wolf at the one place a real break has to be visible (11 September 2026)."""
    try:
        for line in open(path):
            if not line.strip(): continue
            r = json.loads(line)
            return all(k in r for k in ("sha", "prev_sha", "seq"))
    except Exception:
        return False
    return False


def find(ecad):
    """Every chained ledger in the tree, project directories and phase copies alike."""
    pats = [os.path.join(ecad, "*", "out", "routeflow", "journal.jsonl"),
            os.path.join(ecad, "*", "out", "*.jsonl"),
            os.path.join(ecad, "tools", "routeflow", "bench", "*.jsonl")]
    out, skipped = [], []
    for p in pats:
        for f in glob.glob(p):
            (out if is_ledger(f) else skipped).append(f)
    for f in sorted(set(skipped) - set(out)):
        print("ledger_verify: %s carries no chain (no sha, prev_sha, seq): not a ledger, not judged"
              % os.path.relpath(f, ecad))
    return sorted(set(out))


def main(a):
    args = [x for x in a if not x.startswith("--")]
    ecad = args[0] if args else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    do_witness = "--witness" in a
    paths = find(ecad)
    rows, probs, checked, witnessed = 0, [], 0, 0
    for p in paths:
        w = p + WITNESS
        expect = None
        if os.path.exists(w):
            try: expect = json.load(open(w)).get("sha")
            except Exception as e: probs.append("%s: its witness is unreadable (%s)" % (os.path.basename(p), e))
        ok, n, pr = ledger.verify(p, expect)
        rows += n; checked += 1
        for x in pr: probs.append("%s: %s" % (os.path.relpath(p, ecad), x))
        print("ledger_verify: %-58s %4d row(s) %s%s"
              % (os.path.relpath(p, ecad), n, "OK" if ok else "PROBLEM", " (witness checked)" if expect else ""))
        if ok and do_witness and n:
            last = json.loads([l for l in open(p).read().splitlines() if l.strip()][-1])
            json.dump({"sha": last.get("sha"), "seq": last.get("seq"), "rows": n}, open(w, "w"))
            witnessed += 1
    if not checked:
        print("ledger_verify: no ledger found under %s, so nothing was re-walked" % ecad)
        return verdict.write("ledger_verify", verdict.INCONCLUSIVE, denominator=0,
                             counts={"ledgers": 0, "rows": 0}, inputs={"ecad": ecad},
                             note="no ledger under %s: an empty tree and a sound one look alike to a checker "
                                  "that reports no problems" % ecad)
    print("ledger_verify: %d ledger(s), %d row(s), %d problem(s)%s"
          % (checked, rows, len(probs), ", %d witness(es) written" % witnessed if witnessed else ""))
    for x in probs[:10]: print("   " + x)
    return verdict.write("ledger_verify", verdict.PASS if not probs else verdict.FAIL,
                         counts={"ledgers": checked, "rows": rows, "problems": len(probs), "witnessed": witnessed},
                         denominator=rows, evidence=probs[:20], inputs={"ecad": ecad},
                         note="every chain re-walked, every row re-hashed, every witness beside one checked")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
