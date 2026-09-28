#!/usr/bin/env python3
"""retake6: the audit before and after the re-take, row by row (rule and board), read from out/rule-audit/<board>.json.

Usage: audit_diff.py <audit dir before> <audit dir after> [--all]
Prints (1) the evidence classes over the required rows before and after, (2) every row whose RESULT changed, (3) every
row whose class or cause changed with the same result, (4) every row that is not current after, by cause, with the
writer files its evidence names, and (5) every current row that is not a PASS. It reads; it writes and decides nothing.
"""
import sys, os, json, collections

ORDER = ["a", "b", "c", "d", "e", "p", "e5"]
CURRENT = ("CURRENT_CANDIDATE", "VALID_HISTORICAL", "DESK_REVIEW")


def load(d):
    out = collections.OrderedDict()
    for b in ORDER:
        j = json.load(open(os.path.join(d, b + ".json"), encoding="utf-8"))
        for r in j["rows"]:
            out[(b, r["rule"])] = r
    return out


def cls(r): return "%s (%s)" % (r.get("evidence_class"), r.get("evidence_cause"))


if __name__ == "__main__":
    A, B = load(sys.argv[1]), load(sys.argv[2])
    req = lambda r: r.get("release_effect") in ("BLOCKER", "MUST_JUSTIFY")
    for lab, X in (("before", A), ("after", B)):
        c = collections.Counter(r.get("evidence_class") for r in X.values())
        res = collections.Counter(r.get("result") for r in X.values())
        cur = [r for r in X.values() if r.get("evidence_class") == "CURRENT_CANDIDATE"]
        print("%s: %d rows; classes %s; results %s; CURRENT_CANDIDATE %d of which PASS %d" % (
            lab, len(X), dict(sorted(c.items())), dict(sorted(res.items())), len(cur), sum(1 for r in cur if r.get("result") == "PASS")))
    print("\nROWS WHOSE RESULT CHANGED")
    for k in B:
        a, b = A.get(k), B[k]
        if a is None: print("  %s %s NEW ROW: %s %s" % (k[0].upper(), k[1], b.get("result"), cls(b))); continue
        if a.get("result") != b.get("result"):
            print("  %-2s %-8s %-5s %-12s %s  ->  %-12s %s\n       before: %s\n       after:  %s" % (
                k[0].upper(), k[1], b.get("verification_phase", "")[:5], a.get("result"), cls(a), b.get("result"), cls(b),
                str(a.get("why"))[:230], str(b.get("why"))[:230]))
    for k in A:
        if k not in B: print("  %s %s ROW GONE" % (k[0].upper(), k[1]))
    print("\nROWS WHOSE CLASS OR CAUSE CHANGED, SAME RESULT")
    n = collections.Counter()
    for k in B:
        a, b = A.get(k), B[k]
        if a is None or a.get("result") != b.get("result"): continue
        if cls(a) != cls(b):
            n[(cls(a), cls(b))] += 1
            if "--all" in sys.argv:
                print("  %-2s %-8s %-12s %s -> %s" % (k[0].upper(), k[1], b.get("result"), cls(a), cls(b)))
    for (x, y), c in sorted(n.items(), key=lambda t: -t[1]): print("  %3d  %s -> %s" % (c, x, y))
    print("\nROWS NOT CURRENT AFTER, BY CAUSE")
    by = collections.defaultdict(list)
    for k, b in B.items():
        if b.get("evidence_class") in CURRENT: continue
        by[cls(b)].append((k, b))
    for c in sorted(by, key=lambda c: -len(by[c])):
        print("  %3d  %s" % (len(by[c]), c))
        for k, b in by[c]:
            ws = ",".join(sorted(set(str(w.get("file") if isinstance(w, dict) else w) for w in (b.get("writers") or []))))
            print("        %-2s %-8s %-15s %-12s %-22s %s" % (k[0].upper(), k[1], b.get("verification_phase"), b.get("result"), ws, str(b.get("evidence_why"))[:200]))
    print("\nCURRENT ROWS THAT ARE NOT A PASS, AFTER")
    for k, b in B.items():
        if b.get("evidence_class") in CURRENT and b.get("result") != "PASS":
            print("  %-2s %-8s %-15s %-12s %-30s %s" % (k[0].upper(), k[1], b.get("verification_phase"), b.get("result"), cls(b), str(b.get("why"))[:260]))
