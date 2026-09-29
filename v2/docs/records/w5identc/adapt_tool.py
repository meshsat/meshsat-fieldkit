#!/usr/bin/env python3
"""adapt_tool.py: the edits stream w5identc made to stream w5ident's part_identities.py (MESHSAT-1357, 29 September 2026).

Run once on the file `git checkout fnd/w5ident -- v2/ecad/tools/part_identities.py` brings over (w5ident's commit
c08f4d5a). Each edit asserts its anchor is present exactly once and that the text changes, and the result is compiled.
A second run is refused (the first anchor is gone). Kept so the change from w5ident's tool is reproducible edit by edit;
`git diff fnd/w5ident -- v2/ecad/tools/part_identities.py` shows the same thing."""
import os, sys, py_compile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.normpath(os.path.join(HERE, "..", "..", "..", "ecad", "tools", "part_identities.py"))

EDITS = []


def edit(old, new):
    EDITS.append((old, new))


# 1. rows come from the committed netlist (the generator's parts), parsed; the BOM export is compared, not trusted
edit('''def netlist(path):
    """({net: {(ref, pin)}}, {ref: {pin: net}}). The last net is read too (derate.py's R4T-F1)."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    by_net, on, fn = {}, {}, {}
    for m in re.finditer(r'\\(net \\(code "?\\d+"?\\) \\(name "([^"]*)"\\)(.*?)(?=\\(net \\(code|\\Z)', txt, re.S):
        name = m.group(1).lstrip("/")
        nodes = set()
        for n in re.finditer(r'\\(node \\(ref "([^"]+)"\\) \\(pin "([^"]+)"\\)(?: \\(pinfunction "([^"]*)"\\))?', m.group(2)):
            nodes.add((n.group(1), n.group(2)))
            if n.group(3): fn[(n.group(1), n.group(2))] = n.group(3)
        by_net[name] = nodes
        for r, p in nodes: on.setdefault(r, {})[p] = name
    netlist.pinfunction = fn
    return by_net, on
''', '''def netlist(path):
    """({net: {(ref, pin)}}, {ref: {pin: net}}), read by PARSING the S-expression (netlist_sexp), never by a pattern
    over its text (stream w5identc, 29 September 2026: w5ident's reader matched the text). The parsed document is kept
    on the function for the caller (components, their fields and properties)."""
    doc = netlist_sexp.load(path)
    by_net, on, fn = {}, {}, {}
    for name, nodes in doc["nets"].items():
        by_net[name] = set()
        for ref, pin, func, _t in nodes:
            by_net[name].add((ref, pin))
            on.setdefault(ref, {})[pin] = name
            if func: fn[(ref, pin)] = func
    netlist.pinfunction = fn
    netlist.doc = doc
    return by_net, on
''')

edit('''        self.by_net, self.on = netlist(self.net_path)
        self.pinfn = dict(netlist.pinfunction)
        txt = open(self.net_path, encoding="utf-8", errors="replace").read()
        self.comps = set(re.findall(r'\\(comp \\(ref "([^"]+)"\\)', txt))
        self.values = dict(re.findall(r'\\(comp \\(ref "([^"]+)"\\)\\s*\\(value "([^"]*)"\\)', txt))
''', '''        self.by_net, self.on = netlist(self.net_path)
        self.pinfn = dict(netlist.pinfunction)
        doc = netlist.doc
        self.comps = set(doc["components"])
        self.values = {r: c["value"] for r, c in doc["components"].items()}
        self.footprints = {r: c["footprint"] for r, c in doc["components"].items()}
        self.lcsc = {r: (c["fields"].get("LCSC") or c["properties"].get("LCSC") or "").strip() for r, c in doc["components"].items()}
        # a part the schematic marks exclude_from_bom (a test point, a screw of a bought module) is not bought for the board
        self.bom_excluded = {r for r, c in doc["components"].items() if "exclude_from_bom" in c["properties"]}
''')

# 2. rule V-1 (a'): a declared return a little above 0 V is a floor, never a ceiling (the second check's W5I-C2-B1)
edit('''    def is_ground(self, net):
        return net == "GND" or net.startswith("GND") or net in ("AGND", "PGND", "DGND", "SGND")
''', '''    def is_ground(self, net):
        return net == "GND" or net.startswith("GND") or net in ("AGND", "PGND", "DGND", "SGND")

    def is_floor(self, net):
        """A net that can only set a FLOOR (rule V-1 (a) and (a')): a ground, a net declared at or below 0 V, a net the
        intent marks as a return (`returns`), or a declared net whose maximum is at most RETURN_V_MAX (the pack
        negative PACK_N at 0.05 V is a return 50 mV above ground, not a ceiling of 50 mV on every net a diode or a
        connector reaches; w5ident's second check, blocking item W5I-C2-B1)."""
        if self.is_ground(net): return True
        d = (self.rails.get(net) or self.nodes.get(net) or {})
        if d.get("returns"): return True
        w = self.declared(net)
        return bool(w) and "hi" in w and w["hi"] <= RETURN_V_MAX
''')
edit('''            if self.is_ground(o): flo[n].append((0.0, label + "->GND")); return   # (a)
''', '''            if self.is_ground(o): flo[n].append((0.0, label + "->GND")); return   # (a)
            if self.is_floor(o):                                                   # (a'): a return is a floor
                flo[n].append(((self.declared(o) or {}).get("lo", 0.0), "%s->%s (a return, a floor only)" % (label, o))); return
''')
edit('''                decl = [self.declared(o) for o in others if not self.is_ground(o)]           # (a): ground left out
''', '''                if pre in CONNECTOR and not re.search(CONDUCTS_BY_VALUE, self.values.get(ref, ""), re.I):
                    # (g) a connector's pin is set by what is on the far side of it, which this board's intent does
                    # not state: a source of unknown level unless the net is declared (w5ident's second check, W5I-C2-B1
                    # part (b): ten capacitor rows and 92 resistor rows took a bound from a connector read as an active part)
                    unk[n].append("%s pin %s (a connector: its level is set on the far side; declare the net)" % (ref, pin))
                    continue
                decl = [self.declared(o) for o in others if not self.is_floor(o)]            # (a), (a'): floors left out
''')

# 3. the constants the new rules name
edit('''SWITCH = ("Q", "D", "U")        # parts that can switch a node (rule V-1 (b): an inductor on such a node is a companion bound only)
''', '''SWITCH = ("Q", "D", "U")        # parts that can switch a node (rule V-1 (b): an inductor on such a node is a companion bound only)
CONNECTOR = ("J", "CN", "X")    # rule V-1 (g): a connector's pins are set on its far side
RETURN_V_MAX = 0.5              # rule V-1 (a'): a declared net whose maximum is at most this is a return, a floor only
''')

# 4. the imports the edits use
edit('''import csv, json, math, os, re, sys, collections, hashlib
''', '''import csv, json, math, os, re, sys, collections, hashlib, subprocess, shutil, html.parser
''')
edit('''sys.path.insert(0, HERE)
''', '''sys.path.insert(0, HERE)
import netlist_sexp
from verdict import opt
''')


def main():
    src = open(TOOL, encoding="utf-8").read()
    out = src
    for i, (old, new) in enumerate(EDITS, 1):
        n = out.count(old)
        assert n == 1, "edit %d: its anchor occurs %d times (a second run, or another file): refused" % (i, n)
        assert new != old, "edit %d changes nothing" % i
        out = out.replace(old, new)
    assert out != src
    open(TOOL, "w", encoding="utf-8").write(out)
    py_compile.compile(TOOL, doraise=True)
    print("adapt_tool: %d edits applied to %s, compiled" % (len(EDITS), os.path.relpath(TOOL)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
