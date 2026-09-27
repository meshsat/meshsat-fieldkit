import json, glob, os, sys
rows = {}
for side in ("main", "cand"):
    for f in sorted(glob.glob("/root/w4c/rt-%s/*/out/*.verdict.json" % side)):
        ph = f.split("/")[4]; nm = os.path.basename(f)[:-len(".verdict.json")]
        d = json.load(open(f))
        c = d.get("counts") or {}
        brief = {k: c[k] for k in ("fail", "pass", "undecided", "undeclared", "declared_rails", "declared_nodes", "judged", "unrated_parts", "rails", "always_on", "violations", "blocking", "undecided_nets") if k in c}
        rows.setdefault((ph, nm), {})[side] = "%s of %s %s" % (d.get("verdict"), d.get("denominator"), json.dumps(brief, sort_keys=True))
for (ph, nm), v in sorted(rows.items()):
    m, c = v.get("main", "-"), v.get("cand", "-")
    print("%-3s %-18s %-24s main %s" % ("*" if m != c else "", ph, nm, m))
    if m != c: print("    %-18s %-24s cand %s" % ("", "", c))
