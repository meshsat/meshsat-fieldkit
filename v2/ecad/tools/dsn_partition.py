#!/usr/bin/env python3
"""dsn_partition.py <board.kicad_pcb> <in.dsn> <out.dsn> <part.json> [--regions DEVW:-102,S1:-36,S2:34,S3:97,DEVE]
Net-partition routing (research note v2/docs/research-parallel-autorouting.md, 7 Sep 2026): rewrite the DSN's net classes so that every net sits in
<original class>_<group>, each new class carrying the original class's circuit and rule blocks, so that Freerouting 1.9.0 can route one group per job
with the other groups ignored (-inc) and still present as obstacles. Groups: the region (by case-frame x of the pads, thresholds in --regions) that holds
at least 60 percent of a net's pads when the regions holding three or more of its pads are adjacent, else GLOBAL; plane nets (GND, /+5V_*) are GLOBAL.
Writes part.json: {"groups": {group: [nets]}, "classes": {group: [class names]}, "all_classes": [...]} and prints the group sizes."""
import sys, re, json, collections
import pcbnew

board, dsn_in, dsn_out, part_json = sys.argv[1:5]
regions = [("DEVW", -102.0), ("S1", -36.0), ("S2", 34.0), ("S3", 97.0), ("DEVE", None)]
for a in sys.argv[5:]:
    if a.startswith("--regions="):
        regions = []
        for tok in a.split("=", 1)[1].split(","):
            n, _, v = tok.partition(":"); regions.append((n, float(v) if v else None))
OX = 150.0
def region(x):
    for n, lim in regions:
        if lim is None or x < lim: return n
    return regions[-1][0]
order = [n for n, _ in regions]
b = pcbnew.LoadBoard(board)
by = collections.defaultdict(list)
for p in b.GetPads():
    n = p.GetNetname()
    if n: by[n].append(p.GetPosition().x / 1e6 - OX)
def group_of(net):
    if net == "GND" or net.startswith("/+5V_"): return "GLOBAL"
    xs = by.get(net)
    if not xs: return "GLOBAL"
    c = collections.Counter(region(x) for x in xs); top, k = c.most_common(1)[0]
    regs = [r for r in order if c[r] >= 3] or [top]
    span = order.index(regs[-1]) - order.index(regs[0])
    return top if (k >= 0.6 * len(xs) and span <= 1) else "GLOBAL"

s = open(dsn_in).read()
i = s.find("(network")
assert i >= 0, "no network section"
def block_end(text, start):
    depth = 0; j = start
    while j < len(text):
        ch = text[j]
        if ch == "(": depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0: return j + 1
        j += 1
    raise SystemExit("unbalanced")
groups = collections.defaultdict(list); classes = collections.defaultdict(list); all_classes = []
out = []; pos = 0
for m in re.finditer(r"\n(\s*)\(class\s+(\S+)", s):
    if m.start() < i: continue
    start = m.start() + 1; end = block_end(s, start); indent = m.group(1); cname = m.group(2)
    body = s[start:end]
    sub = body.find("\n" + indent + "  (")                       # first sub-block (circuit / rule) at one level deeper
    if sub < 0: sub = re.search(r"\((circuit|rule)", body).start()
    head = body[:sub]; tail = body[sub:-1]                       # tail: the sub-blocks without the closing paren
    toks = head.split()[2:]                                      # after "(class" and the name
    nets = [t.strip('"') for t in toks]
    bygroup = collections.defaultdict(list)
    for n in nets:
        g = group_of(n); bygroup[g].append(n); groups[g].append(n)
    out.append(s[pos:start])
    pieces = []
    for g in ["GLOBAL"] + order:
        if g not in bygroup: continue
        newname = "%s_%s" % (cname, g); classes[g].append(newname); all_classes.append(newname)
        names = " ".join('"%s"' % n if any(ch in n for ch in "() ") else n for n in bygroup[g])
        pieces.append("%s(class %s %s%s)" % (indent, newname, names, tail))
    out.append("\n".join(pieces)); pos = end
out.append(s[pos:])
open(dsn_out, "w").write("".join(out))
conn = {g: sum(max(0, len(by.get(n, [])) - 1) for n in ns) for g, ns in groups.items()}
json.dump({"groups": groups, "classes": classes, "all_classes": all_classes, "connections": conn}, open(part_json, "w"), indent=1)
for g in ["GLOBAL"] + order:
    print("partition %-6s nets %4d connections %5d classes %s" % (g, len(groups.get(g, [])), conn.get(g, 0), classes.get(g, [])))
print("partition: DSN written", dsn_out)
