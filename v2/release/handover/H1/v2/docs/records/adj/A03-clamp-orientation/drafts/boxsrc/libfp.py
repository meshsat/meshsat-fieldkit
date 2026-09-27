# KiCad 9 library footprints: pad 1 and pad 2 x, silk verticals, fab glyph apex; the land's own statement of the cathode.
import re, sys
sys.path.insert(0, "/root/r2/A03-clamp-orientation")
from sexp import parse, find, first, val
for lib, name in (("Diode_SMD", "D_SMC"), ("Diode_SMD", "D_SMB"), ("Diode_SMD", "D_SOD-123"), ("Diode_SMD", "D_SOD-123F"), ("Diode_SMD", "D_SOD-323"), ("Package_TO_SOT_SMD", "SOT-23-6")):
    p = "/usr/share/kicad/footprints/%s.pretty/%s.kicad_mod" % (lib, name)
    t = parse(open(p).read())
    pads = {q[1]: (float(first(q, "at")[1]), float(first(q, "at")[2])) for q in find(t, "pad")}
    fab = {}; silkv = []
    for g in find(t, "fp_line"):
        ly = val(g, "layer"); s = first(g, "start"); e = first(g, "end")
        s = (float(s[1]), float(s[2])); e = (float(e[1]), float(e[2]))
        if ly == "F.Fab":
            for q in (s, e): fab[q] = fab.get(q, 0) + 1
        if ly == "F.SilkS" and abs(s[0] - e[0]) < 1e-3 and abs(s[1] - e[1]) > 0.3: silkv.append(s[0])
    apex = [q for q, k in fab.items() if k >= 3]
    descr = val(t, "descr")
    print("%s:%s pads=%s silk_verticals_x=%s fab_apex=%s | %s" % (lib, name, pads, silkv, apex, descr))
