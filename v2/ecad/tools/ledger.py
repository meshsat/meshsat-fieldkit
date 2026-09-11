#!/usr/bin/env python3
"""The tamper-evident ledger: append-only rows, each carrying the hash of the one before (MESHSAT-862, 11 Sep 2026).

Territory Grounder's `core/audit/ledger.go:85-105` is the shape copied here, and the two things worth copying are
the ones easy to get wrong.

FIELDS ARE LENGTH-PREFIXED BEFORE HASHING. Concatenating keys and values lets two different rows hash the same:
`{"a": "bc"}` and `{"ab": "c"}` are one string once the separators are gone, and a ledger whose rows can collide is
not tamper-evident, it is decorative. Every field goes in as `len(key):key len(value):value`, sorted by key, so the
encoding is injective and the hash means something.

THE CHAIN IS VERIFIED BY RE-WALKING, NOT BY TRUSTING THE LAST ROW. `verify` recomputes every row's hash from its
own content and checks that each names the previous one. A row edited in place fails at that row; a row deleted
fails at the join; rows reordered fail at both. `witness` writes the head somewhere else so a whole-file rewrite,
which would otherwise re-chain cleanly, is caught too.

Usage:
  ledger.py append <ledger.jsonl> <json>     append one row, print its sha
  ledger.py verify <ledger.jsonl>            re-walk the chain; exit 0 intact, 1 broken, 3 nothing to verify
  ledger.py witness <ledger.jsonl> <out>     record the head's sha and length, for an off-file check later
"""
import os, sys, json, time, hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict

GENESIS = "0" * 64
FIELDS_EXCLUDED = ("sha",)   # a row cannot contain its own hash


def canonical(rec):
    """The bytes a row's hash is taken over: every field length-prefixed, sorted by key, `sha` excluded."""
    out = bytearray()
    for k in sorted(rec):
        if k in FIELDS_EXCLUDED: continue
        kb = str(k).encode(); vb = json.dumps(rec[k], sort_keys=True, separators=(",", ":")).encode()
        out += b"%d:%s%d:%s" % (len(kb), kb, len(vb), vb)
    return bytes(out)


def row_sha(rec): return hashlib.sha256(canonical(rec)).hexdigest()


def head(path):
    """(seq, sha) of the last row, or (-1, GENESIS) for an empty or absent ledger."""
    last = None
    try:
        with open(path) as f:
            for line in f:
                if line.strip(): last = line
    except FileNotFoundError:
        return -1, GENESIS
    if last is None: return -1, GENESIS
    r = json.loads(last)
    return r.get("seq", -1), r.get("sha", GENESIS)


def append(path, rec):
    """Append one row, chained to the head. Returns the row as written."""
    seq, prev = head(path)
    row = dict(rec)
    row["seq"] = seq + 1
    row["prev_sha"] = prev
    row.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    row["sha"] = row_sha(row)
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "a") as f: f.write(json.dumps(row, sort_keys=True) + "\n")
    return row


def verify(path, expect_head=None):
    """Re-walk the chain. Returns (ok, n_rows, [problems])."""
    probs, prev, n, seq = [], GENESIS, 0, -1
    try: lines = [l for l in open(path).read().splitlines() if l.strip()]
    except FileNotFoundError: return False, 0, ["no ledger at %s" % path]
    for i, line in enumerate(lines):
        try: r = json.loads(line)
        except Exception as e: probs.append("row %d is not JSON (%s)" % (i, e)); break
        n += 1
        if r.get("prev_sha") != prev:
            probs.append("row %d (seq %s) names prev %s, the row before hashes to %s"
                         % (i, r.get("seq"), str(r.get("prev_sha"))[:12], prev[:12]))
        got = row_sha(r)
        if got != r.get("sha"):
            probs.append("row %d (seq %s) hashes to %s and carries %s: its content changed after it was written"
                         % (i, r.get("seq"), got[:12], str(r.get("sha"))[:12]))
        if r.get("seq") != seq + 1:
            probs.append("row %d has seq %s after %s: a row is missing or out of order" % (i, r.get("seq"), seq))
        prev = r.get("sha", GENESIS); seq = r.get("seq", seq + 1)
    if expect_head is not None and prev != expect_head:
        probs.append("the head is %s and the witness says %s: the whole file may have been rewritten"
                     % (prev[:12], str(expect_head)[:12]))
    return not probs, n, probs


def main(a):
    if len(a) >= 3 and a[0] == "append":
        row = append(a[1], json.loads(a[2])); print("ledger: seq %d sha %s" % (row["seq"], row["sha"][:16])); return 0
    if len(a) >= 3 and a[0] == "witness":
        seq, sha = head(a[1])
        json.dump({"seq": seq, "sha": sha, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, open(a[2], "w"), indent=1)
        print("ledger: witnessed seq %d sha %s -> %s" % (seq, sha[:16], a[2])); return 0
    if len(a) >= 2 and a[0] == "verify":
        w = None
        if "--witness" in a:
            try: w = json.load(open(a[a.index("--witness") + 1]))["sha"]
            except Exception as e: print("ledger: witness unreadable (%s)" % e)
        ok, n, probs = verify(a[1], w)
        for p in probs[:20]: print("ledger: BROKEN " + p)
        print("ledger: %d row(s), %s" % (n, "chain intact" if ok else "%d problem(s)" % len(probs)))
        # An empty ledger is not an intact one: nothing was verified, and that is not the same as nothing being wrong.
        res = verdict.INCONCLUSIVE if n == 0 else (verdict.PASS if ok else verdict.FAIL)
        return verdict.write("ledger_verify", res, counts={"rows": n, "problems": len(probs)}, denominator=n,
                             evidence=probs[:30], inputs={"ledger": a[1]},
                             note="every row re-hashed from its own content and chained to the one before")
    print(__doc__); return verdict.USAGE


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
