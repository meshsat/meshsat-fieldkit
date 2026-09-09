#!/usr/bin/env python3
"""Summarise a pair_preroute run (9 September 2026, MESHSAT-862): who blocked which pair, counted.

`pair_preroute.py` prints one line per pair and a summary at the end, which answers "how many" but not "why" or "where",
and a placement is corrected by where. This reads its log and groups the failures by REASON and by the PART the section
died at, so the next placement iteration is aimed rather than guessed. It is the same rule the escape prune already
follows: a gate that refuses copper must name what it hit.

Usage: pair_report.py <pair.log> [--top N]"""
import sys, re, collections

def main(a):
    if not a: print(__doc__); return 2
    top = int(a[a.index("--top") + 1]) if "--top" in a else 12
    txt = open(a[0], errors="replace").read().splitlines()
    laid = [l for l in txt if "LAID  " in l]
    fail = [l for l in txt if "FAIL  " in l]
    swap = [l for l in txt if "SWAP  " in l]
    twist = [l for l in txt if "TWIST " in l]
    reasons, parts, stems = collections.Counter(), collections.Counter(), collections.Counter()
    for l in fail:
        m = re.search(r"FAIL\s+(\S+):\s+section\s+(\S+)\s*->\s*(\S+)\s*\(([^)]*)\)", l)
        if not m:
            reasons["(unparsed)"] += 1; continue
        stem, fr, to, why = m.groups()
        stems[stem] += 1
        why_short = re.sub(r"/\S+", "<net>", why)
        reasons[why_short] += 1
        pm = re.search(r"at (\S+)$", why)
        parts[pm.group(1) if pm else to] += 1
    print("pair_report: %d laid, %d failed attempts, %d swaps, %d twists" % (len(laid), len(fail), len(swap), len(twist)))
    total = len({re.search(r"(?:LAID|FAIL)\s+(\S+):", l).group(1) for l in laid + fail if re.search(r"(?:LAID|FAIL)\s+(\S+):", l)})
    print("pair_report: %d distinct pairs appear in the log" % total)
    print("pair_report: failures by reason")
    for r, n in reasons.most_common(top): print("   %4d  %s" % (n, r[:120]))
    print("pair_report: failures by the part the section died at")
    for p, n in parts.most_common(top): print("   %4d  %s" % (n, p))
    print("pair_report: pairs that failed most often (a pair retried after a swap counts twice)")
    for st, n in stems.most_common(top): print("   %4d  %s" % (n, st))
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
