# From a KiCad .net file: every component that is a diode/clamp (by lib, symbol, value), with pin->net map.
import sys, re, json
sys.path.insert(0, __file__.rsplit("/",1)[0])
from sexp import parse, find, first, val
KEY = re.compile(r"TVS|Zener|Schottky|USBLC|TPD\d|PRTR|ESD|RCLAMP|PESD|SMBJ|SMCJ|SMAJ|BAT54|SS\d\d|1N\d{4}|MBR|B5819|MMSZ|BZT|diode", re.I)
def load(path):
    t = parse(open(path).read())
    comps = {}
    for c in find(first(t, "components"), "comp"):
        ref = val(c, "ref"); v = val(c, "value"); fp = val(c, "footprint")
        ls = first(c, "libsource"); lib = val(ls, "lib") if ls else None; part = val(ls, "part") if ls else None
        props = {p[1][1]: p[2][1] for p in find(c, "property") if len(p) > 2 and isinstance(p[1], list)}
        fields = {}
        fl = first(c, "fields")
        if fl:
            for f in find(fl, "field"):
                nm = [x for x in f if isinstance(x, list) and x[0] == "name"]
                if nm and len(f) > 2: fields[nm[0][1]] = f[-1] if isinstance(f[-1], str) else None
        comps[ref] = dict(value=v, footprint=fp, lib=lib, part=part, fields=fields, props=props, pins={})
    for n in find(first(t, "nets"), "net"):
        name = val(n, "name")
        for nd in find(n, "node"):
            r = val(nd, "ref"); p = val(nd, "pin"); fn = val(nd, "pinfunction")
            if r in comps: comps[r]["pins"][p] = (name, fn)
    return comps
if __name__ == "__main__":
    comps = load(sys.argv[1])
    out = {}
    for r, c in sorted(comps.items()):
        txt = " ".join(str(x) for x in (c["lib"], c["part"], c["value"], c["footprint"]))
        if ("LED" in (c["part"] or "").upper()) : continue
        if r.startswith("D") or KEY.search(txt):
            if r.startswith(("J", "C", "R")) : continue
            out[r] = c
            print(r, "|", c["lib"], c["part"], "|", c["value"], "|", c["footprint"], "|", c["fields"].get("LCSC") or c["props"].get("LCSC"), "|", {k: v[0] + ("/" + v[1] if v[1] else "") for k, v in sorted(c["pins"].items())})
    if len(sys.argv) > 2: json.dump(out, open(sys.argv[2], "w"), indent=1)
