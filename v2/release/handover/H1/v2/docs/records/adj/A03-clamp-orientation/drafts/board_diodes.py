# Text parse of a committed .kicad_pcb: for each clamp/diode footprint, its lib id, side, value, LCSC,
# pad nets, and which pad the cathode mark (silk bracket vertical, fab bar) sits on, in footprint-local frame.
import sys, re, json, hashlib
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from sexp import parse, find, first, val
WANT = re.compile(r"TVS|Schottky|SMBJ|SMCJ|PESD|USBLC|BAT54|SS14|SS2040|1N4148|ESD", re.I)
def blocks(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith("\t(footprint "):
            j = i + 1
            while lines[j] != "\t)": j += 1
            yield i + 1, "\n".join(lines[i:j + 1])
            i = j + 1
        else:
            i += 1
def props(fp):
    return {p[1]: p[2] for p in find(fp, "property") if len(p) > 2 and isinstance(p[1], str) and isinstance(p[2], str)}
def segs(fp, layers):
    out = []
    for tag in ("fp_line", "fp_poly", "fp_rect", "fp_arc", "fp_circle"):
        for g in find(fp, tag):
            ly = val(g, "layer")
            if ly not in layers: continue
            if tag == "fp_line":
                s = first(g, "start"); e = first(g, "end")
                out.append((ly, tag, [(float(s[1]), float(s[2])), (float(e[1]), float(e[2]))]))
            elif tag == "fp_poly":
                pts = first(g, "pts"); out.append((ly, tag, [(float(x[1]), float(x[2])) for x in find(pts, "xy")]))
            elif tag == "fp_rect":
                s = first(g, "start"); e = first(g, "end")
                out.append((ly, tag, [(float(s[1]), float(s[2])), (float(e[1]), float(e[2]))]))
    return out
def analyse(fp):
    lib = fp[1]; ly = val(fp, "layer"); at = first(fp, "at")
    pr = props(fp)
    pads = {}
    for p in find(fp, "pad"):
        num = p[1]; pat = first(p, "at"); net = first(p, "net")
        netname = (net[2] if net is not None and len(net) > 2 else (net[1] if net is not None and len(net) > 1 else None))
        if num not in pads: pads[num] = dict(x=float(pat[1]), y=float(pat[2]), net=netname)
    side = "F" if ly == "F.Cu" else "B"
    g = segs(fp, {side + ".SilkS", side + ".Fab"})
    # vertical segments in local frame (x const, |dy| > 0.3)
    marks = {}
    for L, tag, pts in g:
        for a, b in zip(pts, pts[1:]):
            if abs(a[0] - b[0]) < 1e-3 and abs(a[1] - b[1]) > 0.3:
                marks.setdefault(L, []).append(round(a[0], 3))
    res = dict(lib=lib, layer=ly, at=[float(x) for x in at[1:]], ref=pr.get("Reference"), value=pr.get("Value"),
               lcsc=pr.get("LCSC"), pads=pads, vertical_marks=marks)
    # cathode inference for 2-pad axial-in-x footprints
    if set(pads) == {"1", "2"}:
        x1, x2 = pads["1"]["x"], pads["2"]["x"]
        silk = marks.get(side + ".SilkS", [])
        # silk bracket: the vertical segment(s) outside the body on the pad-1 side
        s1 = [x for x in silk if (x - (x1 + x2) / 2) * (x1 - x2) > 0]
        s2 = [x for x in silk if (x - (x1 + x2) / 2) * (x2 - x1) > 0]
        res["silk_vertical_on_pad1_side"] = s1; res["silk_vertical_on_pad2_side"] = s2
        fab = marks.get(side + ".Fab", [])
        res["fab_vertical"] = fab
    return res
if __name__ == "__main__":
    path = sys.argv[1]
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    out = {"board": path, "sha256_16": sha, "parts": {}}
    for ln, txt in blocks(path):
        fp = parse(txt)
        pr = props(fp)
        ref = pr.get("Reference", "")
        lib = fp[1]
        if WANT.search((pr.get("Value") or "") + " " + lib) and not re.match(r"^(J|R|C|L)", ref):
            a = analyse(fp); a["line"] = ln
            out["parts"][ref] = a
    print(json.dumps(out, indent=1))
