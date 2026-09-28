#!/usr/bin/env python3
"""A KiCad netlist read by an S-expression reader (MESHSAT-1357, worker d8dec31, decision 31's review).

The review of decision 31 enumerates every connector pin of boards A, D and E from the committed netlists. It PARSES
them: this module tokenises the S-expression and builds the tree, and nothing in the review greps a netlist.

    comps, nets = read(path)
    comps[ref] = {"value", "footprint", "lib", "part", "description", "fields": {name: text}, "pins": {pin: net}}
    nets[name] = [(ref, pin, pinfunction, pintype)]
"""
import sys, json


def tokens(txt):
    i, n = 0, len(txt)
    while i < n:
        c = txt[i]
        if c in " \t\r\n":
            i += 1
        elif c in "()":
            yield c; i += 1
        elif c == '"':
            j, out = i + 1, []
            while j < n and txt[j] != '"':
                if txt[j] == "\\" and j + 1 < n:
                    out.append(txt[j + 1]); j += 2
                else:
                    out.append(txt[j]); j += 1
            yield ("s", "".join(out)); i = j + 1
        else:
            j = i
            while j < n and txt[j] not in " \t\r\n()": j += 1
            yield ("a", txt[i:j]); i = j


def parse(txt):
    stack, cur = [], None
    for t in tokens(txt):
        if t == "(":
            new = []
            if cur is not None:
                cur.append(new); stack.append(cur)
            cur = new
        elif t == ")":
            if stack: cur = stack.pop()
        else:
            cur.append(t[1])
    return cur


def _kids(node, name):
    return [k for k in node[1:] if isinstance(k, list) and k and k[0] == name]


def _one(node, name, default=""):
    k = _kids(node, name)
    if not k: return default
    return k[0][1] if len(k[0]) > 1 and not isinstance(k[0][1], list) else default


def read(path):
    tree = parse(open(path, encoding="utf-8", errors="replace").read())
    comps, nets = {}, {}
    for sec in tree[1:]:
        if not isinstance(sec, list) or not sec: continue
        if sec[0] == "components":
            for c in _kids(sec, "comp"):
                ref = _one(c, "ref")
                ls = _kids(c, "libsource")
                fields = {}
                for fs in _kids(c, "fields"):
                    for f in _kids(fs, "field"):
                        nm = _one(f, "name")
                        txt = [x for x in f[1:] if not isinstance(x, list)]
                        fields[nm] = txt[0] if txt else ""
                for pr in _kids(c, "property"):
                    fields.setdefault(_one(pr, "name"), _one(pr, "value"))
                comps[ref] = {"value": _one(c, "value"), "footprint": _one(c, "footprint"),
                              "lib": _one(ls[0], "lib") if ls else "", "part": _one(ls[0], "part") if ls else "",
                              "description": (_one(ls[0], "description") if ls else "") or _one(c, "description"),
                              "fields": fields, "pins": {}}
        elif sec[0] == "nets":
            for nt in _kids(sec, "net"):
                name = _one(nt, "name").lstrip("/")
                rows = []
                for nd in _kids(nt, "node"):
                    r, p = _one(nd, "ref"), _one(nd, "pin")
                    rows.append((r, p, _one(nd, "pinfunction"), _one(nd, "pintype")))
                    comps.setdefault(r, {"value": "", "footprint": "", "lib": "", "part": "", "description": "",
                                         "fields": {}, "pins": {}})["pins"][p] = name
                nets[name] = rows
    return comps, nets


if __name__ == "__main__":
    comps, nets = read(sys.argv[1])
    print(json.dumps({"components": len(comps), "nets": len(nets)}))
