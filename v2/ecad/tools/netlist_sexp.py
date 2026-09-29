#!/usr/bin/env python3
"""A KiCad netlist read as the S-expression it is (MESHSAT-1357, stream d6dec, 27 September 2026).

The decoupling reading of FEA-006 asks of each board's committed netlist which capacitor sits on which pin's net, with
what value, and what the other end of that capacitor is tied to. A pattern over the text answers the first question
and not the last two: a value that holds a bracket or a quote, a component whose fields come in another order, or a
net that is the last of the file each bend a pattern and none bends a reader. So this file PARSES: a tokenizer that
knows a quoted string with its escapes, a tree, and three views over it. It needs nothing but Python.

    doc = netlist_sexp.load(path)
    doc["components"]["C31"]   -> {"value": "2.2u 16V X5R 0402", "footprint": "Capacitor_SMD:C_0402_1005Metric",
                                   "fields": {...}, "libpart": "C"}
    doc["nets"]["HPVDD"]       -> [("C31", "1", "", "passive"), ("U7", "10", "HPVDD", "power_out")]
    doc["pin_net"][("U7", "10")] -> "HPVDD"
    doc["pins"]["U7"]          -> {"10": {"net": "HPVDD", "function": "HPVDD", "type": "power_out"}, ...}

Net names are given without their leading slash, which is how the intent files and every rule of this project name a
net. Nothing is guessed: a netlist with no `components` or no `nets` section raises, because a reader that returns an
empty board for a file it could not read makes every check after it pass on nothing."""
import re

_TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
_ESC = re.compile(r'\\(.)')


class Quoted(str):
    """A token that was written in quotes, so `(value "(")` is the string and not a bracket."""


def parse(text):
    """The tree of one S-expression file: nested lists of strings. Raises ValueError on an unbalanced file."""
    stack = [[]]
    for m in _TOK.finditer(text):
        t = m.group(0)
        if t == "(": stack.append([])
        elif t == ")":
            if len(stack) == 1: raise ValueError("netlist_sexp: a ')' with nothing open")
            x = stack.pop(); stack[-1].append(x)
        elif t.startswith('"'):
            stack[-1].append(Quoted(_ESC.sub(lambda e: e.group(1), t[1:-1])))
        else: stack[-1].append(t)
    if len(stack) != 1: raise ValueError("netlist_sexp: %d '(' never closed" % (len(stack) - 1))
    return stack[0]


def kids(node, key):
    return [x for x in node if isinstance(x, list) and x and not isinstance(x[0], list) and x[0] == key
            and not isinstance(x[0], Quoted)]


def kid(node, key):
    k = kids(node, key); return k[0] if k else None


def _val(node, key, default=""):
    k = kid(node, key)
    return str(k[1]) if k is not None and len(k) > 1 and not isinstance(k[1], list) else default


def load_text(text):
    tree = parse(text)
    top = next((x for x in tree if isinstance(x, list) and x and x[0] == "export"), None)
    if top is None: raise ValueError("netlist_sexp: no (export ...) at the top: this is not a KiCad netlist")
    comps_n, nets_n = kid(top, "components"), kid(top, "nets")
    if comps_n is None or nets_n is None:
        raise ValueError("netlist_sexp: the netlist has no %s section"
                         % ("components" if comps_n is None else "nets"))
    comps = {}
    for c in kids(comps_n, "comp"):
        ref = _val(c, "ref")
        fields = {}
        fn = kid(c, "fields")
        for f in (kids(fn, "field") if fn is not None else []):
            name = _val(f, "name")
            rest = [x for x in f[1:] if not isinstance(x, list)]
            fields[name] = str(rest[0]) if rest else ""
        props = {}
        for p in kids(c, "property"):
            props[_val(p, "name")] = _val(p, "value")
        ls = kid(c, "libsource")
        comps[ref] = {"value": _val(c, "value"), "footprint": _val(c, "footprint"), "fields": fields,
                      "properties": props, "libpart": _val(ls, "part") if ls is not None else "",
                      "description": _val(ls, "description") if ls is not None else ""}
    nets, pin_net, pins = {}, {}, {}
    for n in kids(nets_n, "net"):
        name = _val(n, "name").lstrip("/")
        nodes = []
        for nd in kids(n, "node"):
            ref, pin = _val(nd, "ref"), _val(nd, "pin")
            fn_, ty = _val(nd, "pinfunction"), _val(nd, "pintype")
            nodes.append((ref, pin, fn_, ty))
            pin_net[(ref, pin)] = name
            pins.setdefault(ref, {})[pin] = {"net": name, "function": fn_, "type": ty}
        nets[name] = nodes
    design = kid(top, "design")
    return {"components": comps, "nets": nets, "pin_net": pin_net, "pins": pins,
            "source": _val(design, "source") if design is not None else "",
            "date": _val(design, "date") if design is not None else ""}


def load(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return load_text(fh.read())


_UNIT = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "μ": 1e-6, "m": 1e-3, "": 1.0}
_VALUE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([pnuµμm]?)(?:F\b|\b|(?=\s|$))")
_VOLT = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(k?)V\b")
_DIEL = re.compile(r"\b(X5R|X6S|X7R|X7S|X7T|X8R|X8L|Y5V|Z5U|C0G|NP0|U2J)\b", re.I)


def farads(value):
    """The capacitance a value string states, in farads, or None when it states none. `10u 25V 1210` is 1e-5,
    `100n` is 1e-7; a string that does not begin with a number and a unit is not read as a capacitance."""
    m = _VALUE.match(str(value or ""))
    if not m or not m.group(2): return None
    return float(m.group(1)) * _UNIT[m.group(2)]


def rated_volts(value):
    """The voltage rating a value string states, or None. It is what the generator wrote, not what a part has."""
    m = _VOLT.search(str(value or ""))
    if not m: return None
    return float(m.group(1)) * (1000.0 if m.group(2) == "k" else 1.0)


def dielectric(value):
    m = _DIEL.search(str(value or ""))
    return m.group(1).upper() if m else None


def is_capacitor(doc, ref):
    c = doc["components"].get(ref)
    if c is None: return False
    return c["libpart"].startswith("C") and (c["libpart"] in ("C", "C_Polarized", "C_Small", "CP", "C_Polarized_US")
                                             or farads(c["value"]) is not None) and bool(re.match(r"^C\d", ref))
