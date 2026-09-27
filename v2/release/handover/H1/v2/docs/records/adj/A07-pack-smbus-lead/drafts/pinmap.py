import re, sys
def nets_of(path, ref):
    txt = open(path).read()
    out = {}
    for m in re.finditer(r'\(net \(code "(\d+)"\) \(name "([^"]+)"\)(.*?)(?=\n    \(net \(code|\n  \)\n\)|\Z)', txt, re.S):
        name, body = m.group(2), m.group(3)
        nodes = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', body)
        for r, p in nodes:
            if r == ref:
                out[p] = (name, sorted(set(x for x, _ in nodes)))
    return out
for path in sys.argv[1:]:
    print("==", path)
    for p, (n, refs) in sorted(nets_of(path, "J_SMB").items(), key=lambda kv: int(kv[0])):
        print("  pin", p, n, "| on net:", " ".join(refs[:14]), "(+%d)" % max(0, len(refs)-14) if len(refs) > 14 else "")
