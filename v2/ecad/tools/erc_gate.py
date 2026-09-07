#!/usr/bin/env python3
"""ERC as a gate (MESHSAT-862, 8 Sep 2026, appendix 32.64): build_sch.sh used to turn kicad-cli's exit code into an echo and no chain read it.
Reads out/<name>-erc.json (kicad-cli sch erc --format json; the .rpt is kept for humans), counts every violation by type and severity, and
blocks on any error-severity violation that the project's allow-list does not cover. Warnings are printed with counts and never block.

Allow-list: <project dir>/erc-allow.txt, one rule per line  `type` or `type|substring`, a `#` reason after it (a line without a reason is
ignored, so nothing is waved through silently). Example:  power_pin_not_driven|+3V3_AB   # the gated rail comes from A22 over the harness

Usage: erc_gate.py <project dir> <name>  -> prints the counts, writes out/<name>-erc.status (clean | allowed N | BLOCK N | BLOCK no ERC output), exit 1 on BLOCK."""
import sys, os, json, collections

def violations(d):
    out = []
    if isinstance(d, dict):
        for s in d.get("sheets", []): out += s.get("violations", [])
        out += d.get("violations", [])
    return out

def allow_rules(path):
    rules = []
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if not line or line.startswith("#") or "#" not in line: continue
            rule, reason = line.split("#", 1)
            t, _, sub = rule.strip().partition("|")
            if t and reason.strip(): rules.append((t.strip(), sub.strip(), reason.strip()))
    return rules

def gate(d, rules):
    """(blocking list, allowed count, counter by (type, severity)) for a parsed ERC JSON."""
    by = collections.Counter(); block = []; allowed = 0
    for v in violations(d):
        t, sev = v.get("type", "?"), v.get("severity", "error")
        if v.get("excluded"): continue
        by[(t, sev)] += 1
        if sev != "error": continue
        text = v.get("description", "") + " " + " ".join(i.get("description", "") for i in v.get("items", []))
        if any(t == rt and (not sub or sub in text) for rt, sub, _ in rules): allowed += 1
        else: block.append("%s: %s" % (t, v.get("description", "")[:110]))
    return block, allowed, by

def main(a):
    if len(a) < 2: print(__doc__); return 2
    proj, name = a[0], a[1]; path = os.path.join(proj, "out", name + "-erc.json"); status = os.path.join(proj, "out", name + "-erc.status")
    os.makedirs(os.path.join(proj, "out"), exist_ok=True)
    try: d = json.load(open(path))
    except Exception as e:
        print("erc_gate: BLOCK no ERC output (%s: %s)" % (path, e)); open(status, "w").write("BLOCK no ERC output\n"); return 1
    rules = allow_rules(os.path.join(proj, "erc-allow.txt"))
    block, allowed, by = gate(d, rules)
    for (t, sev), n in sorted(by.items()): print("erc_gate: %-8s %-40s %d" % (sev, t, n))
    if block:
        print("erc_gate: BLOCK %d error(s) not allow-listed (of %d violations; %d allowed by %s):" % (len(block), sum(by.values()), allowed, os.path.basename(proj) + "/erc-allow.txt"))
        for line in block[:12]: print("   " + line)
        open(status, "w").write("BLOCK %d\n" % len(block)); return 1
    print("erc_gate: %s (%d violations, %d error(s) allow-listed with a reason, warnings %d)" % ("clean" if not by else "no blocking error", sum(by.values()), allowed, sum(n for (t, s), n in by.items() if s != "error")))
    open(status, "w").write(("allowed %d\n" % allowed) if allowed else "clean\n"); return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
