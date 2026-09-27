#!/usr/bin/env python3
"""The review's connector tables, written from the netlists and the corrected declarations (worker d8dec31).

Every connector-class part of boards A, D and E (a reference J, P, PAD or W), pin by pin: the net, whether it carries
a supply or a signal, and the entry of the corrected declaration that covers it. It stops if a pin that carries a
supply or a signal is covered by no entry, so the tables cannot leave one out. Markdown on stdout.

Usage: make_pin_tables.py <tree root>
"""
import hashlib, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netread
import apply_port_declarations as D

CONNECTOR = re.compile(r"^(J|P|PAD|W)(_|\d|$)")


def key(p):
    try: return (0, int(p))
    except ValueError: return (1, p)


def rkey(r):
    m = re.match(r"^(.*?)(\d*)$", r)
    return (m.group(1), int(m.group(2) or 0))


def runs(pins):
    """'1 to 7, 11' from a list of pin numbers."""
    ns = sorted(int(p) for p in pins); out = []; i = 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1: j += 1
        out.append(str(ns[i]) if i == j else "%d to %d" % (ns[i], ns[j]) if j > i + 1 else "%d, %d" % (ns[i], ns[j])); i = j + 1
    return ", ".join(out)


def main(root):
    for letter, internal in (("a", D.A_INTERNAL), ("d", D.D_INTERNAL), ("e", D.E_INTERNAL)):
        t = json.load(open(os.path.join(root, "v2/ecad/tools/boards/%s.json" % letter), encoding="utf-8"))
        ext = D.a_external(t["external_ports"]) if letter == "a" else t["external_ports"]
        comps, nets = netread.read(os.path.join(root, D.NETLIST[letter]))
        sha = hashlib.sha256(open(os.path.join(root, D.NETLIST[letter]), "rb").read()).hexdigest()
        cls = {}
        for e in ext: cls[e["ref"]] = ("EXTERNAL, protected off this board" if e.get("off_board") else "EXTERNAL", e)
        for e in internal: cls[e["ref"]] = ("INTERNAL", e)
        refs = sorted((r for r in comps if CONNECTOR.match(r)), key=rkey)
        print("\n### Board %s: every connector pin (%s, sha256 %s)\n" % (letter.upper(), D.NETLIST[letter].split("/")[-1], sha[:16]))
        print("%d connector-class parts, %d pins, of which %d carry a supply or a signal and %d are ground.\n"
              % (len(refs), sum(len(comps[r]["pins"]) for r in refs),
                 sum(1 for r in refs for n in comps[r]["pins"].values() if D.conductor(n)),
                 sum(1 for r in refs for n in comps[r]["pins"].values() if not D.conductor(n))))
        print("| connector | pins that carry a supply or a signal (pin: net) | ground pins | class | where the lead goes |")
        print("|---|---|---|---|---|")
        for r in refs:
            pins = comps[r]["pins"]
            live = ["%s: %s" % (p, pins[p]) for p in sorted(pins, key=key) if D.conductor(pins[p])]
            gnd = [p for p in sorted(pins, key=key) if not D.conductor(pins[p])]
            if live:
                assert r in cls, "board %s: %s carries %s and no entry covers it" % (letter.upper(), r, live)
                c, e = cls[r]; why = e["why"]
            else:
                c, why = "carries no conductor", "a return: every pin is on %s" % ", ".join(sorted({pins[p] for p in pins}))
            print("| %s | %s | %s | %s | %s |" % (r, "; ".join(live) or "none", runs(gnd) if gnd else "none", c, why))
        other = sorted((r for r in comps if re.match(r"^(TP|JP|LED|K|SW|BT|H|MP|FID)\d", r)), key=rkey)
        kinds = {}
        for r in other: kinds.setdefault(re.match(r"^[A-Z]+", r).group(0), []).append(r)
        print("\nNot connectors, and on no lead: %s.\n" % "; ".join(
            "%s (%d: %s)" % ({"TP": "test points", "JP": "solder jumpers", "LED": "indicator LEDs on the board", "K": "the relay"}.get(k, k),
                             len(v), v[0] if len(v) == 1 else "%s to %s" % (v[0], v[-1])) for k, v in kinds.items()))


if __name__ == "__main__":
    main(os.path.abspath(sys.argv[1]))
