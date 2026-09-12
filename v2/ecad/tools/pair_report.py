#!/usr/bin/env python3
"""Summarise a pair_preroute run (9 September 2026, MESHSAT-862): who blocked which pair, counted.

`pair_preroute.py` prints one line per pair and a summary at the end, which answers "how many" but not "why" or "where",
and a placement is corrected by where. This reads its log and groups the failures by REASON and by the PART the section
died at, so the next placement iteration is aimed rather than guessed. It is the same rule the escape prune already
follows: a gate that refuses copper must name what it hit.

12 September 2026: its largest bucket on B19's contention arms was `(unparsed)`, 38 and 42 lines of 74, because it
only ever understood the per-SECTION failure shape `FAIL <pair>: section A -> B (reason)`. Every WHOLE-PAIR verdict
(the legs against each other, the legs crossing, the copper on another net) fell through it, and the largest single
failure class on that board was one of those: a pair refused for its own two vias. A report whose biggest category
is "I could not parse this" answers a different question than the one asked of it, so the whole-pair shapes are read
now and anything still unread is PRINTED rather than counted.

12 September 2026, second edit: `--json <path>` writes the same counts as an artefact. Tier 2 of the agentic
system reads structured evidence and never a log, for the reason the appendix gives about logs generally (they
carry the run's prose, which is where a wrong reading comes from); the profile is the one thing it needs that
only a log holds, so the profile becomes a file with counts and a denominator, like every other verdict here.

Usage: pair_report.py <pair.log> [--top N] [--json out.json]"""
import sys, re, json, collections

def main(a):
    if not a: print(__doc__); return 2
    top = int(a[a.index("--top") + 1]) if "--top" in a else 12
    txt = open(a[0], errors="replace").read().splitlines()
    laid = [l for l in txt if "LAID  " in l]
    fail = [l for l in txt if "FAIL  " in l]
    swap = [l for l in txt if "SWAP  " in l]
    twist = [l for l in txt if "TWIST " in l]
    reasons, parts, stems, kinds = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    unread = []
    def _short(why):
        """one bucket per reason: net names and measurements vary line by line and the reason does not"""
        return re.sub(r"\d+(?:[.,]\d+)*", "N", re.sub(r"/\S+", "<net>", why)).strip()
    for l in fail:
        m = re.search(r"FAIL\s+(\S+):\s+section\s+(\S+)\s*->\s*(\S+)\s*\(([^)]*)\)", l)
        if m:
            stem, fr, to, why = m.groups()
            stems[stem] += 1; kinds["a section of the pair"] += 1
            reasons[re.sub(r"/\S+", "<net>", why)] += 1
            pm = re.search(r"at (\S+)$", why)
            parts[pm.group(1) if pm else to] += 1
            continue
        # the whole-pair verdicts: the pair was laid and then refused, so there is no section and no part
        m = re.search(r"FAIL\s+(\S+):\s+(.*)$", l)
        if not m:
            reasons["(unparsed)"] += 1; unread.append(l.strip()); continue
        stem, why = m.groups()
        stems[stem] += 1; kinds["the whole pair, after it was laid"] += 1
        reasons[_short(why.split("; rolled back")[0])] += 1
        parts["(whole pair)"] += 1
    print("pair_report: %d laid, %d failed attempts, %d swaps, %d twists" % (len(laid), len(fail), len(swap), len(twist)))
    total = len({re.search(r"(?:LAID|FAIL)\s+(\S+):", l).group(1) for l in laid + fail if re.search(r"(?:LAID|FAIL)\s+(\S+):", l)})
    print("pair_report: %d distinct pairs appear in the log" % total)
    print("pair_report: failures by what was refused")
    for k, n in kinds.most_common(): print("   %4d  %s" % (n, k))
    print("pair_report: failures by reason")
    for r, n in reasons.most_common(top): print("   %4d  %s" % (n, r[:120]))
    print("pair_report: failures by the part the section died at")
    for p, n in parts.most_common(top): print("   %4d  %s" % (n, p))
    print("pair_report: pairs that failed most often (a pair retried after a swap counts twice)")
    for st, n in stems.most_common(top): print("   %4d  %s" % (n, st))
    if unread:
        print("pair_report: %d FAIL line(s) this tool cannot read, which is a gap in the tool and not in the run:" % len(unread))
        for l in unread[:3]: print("      %s" % l[:160])
    if "--json" in a:
        prof = {"laid": len(laid), "failed_attempts": len(fail), "swaps": len(swap), "twists": len(twist),
                "distinct_pairs": total, "unparsed": len(unread),
                "by_what_was_refused": dict(kinds.most_common()),
                "by_reason": dict(reasons.most_common(top)),
                "by_part": dict(parts.most_common(top)),
                "by_pair": dict(stems.most_common(top))}
        with open(a[a.index("--json") + 1], "w") as fh: json.dump(prof, fh, indent=1, sort_keys=True)
        print("pair_report: profile written to %s" % a[a.index("--json") + 1])
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
