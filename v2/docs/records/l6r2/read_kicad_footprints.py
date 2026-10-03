#!/usr/bin/env python3
"""read_kicad_footprints.py: the KiCad library's four Coilcraft XAL footprints as KiCad 9.0.9 ships them (MESHSAT-1357, record
l6r2 round 3, 3 October 2026).

Board B draws its XAL4030-472ME (L1) on Inductor_SMD:L_Coilcraft_XAL4020-XXX and its XAL6030-332ME (L101, L102, L201, L202, L301,
L302) on L_Coilcraft_XAL6060-XXX; board E draws its XAL4030-472ME (L3) on the XAL4020 footprint. Whether the land changes rests on
the footprints' pads, their descriptions (the body each is drawn for) and their 3D models, read here from the library's own
repository at the tag of the project's KiCad (9.0.9), and on Coilcraft's series sheets held in the tree. This writes one reading,
inputs/kicad-xal-footprints-9.0.9.json: per footprint the URL, the file's sha256 and size, its description, its pads (number,
position, size), the extents of its courtyard, fab and silk outlines and its model path, parsed from the S-expression. The library files are not filed (the facts are; the library is
CC-BY-SA 4.0 with KiCad's exception). Usage: read_kicad_footprints.py   (run from anywhere; four requests)"""
import datetime
import hashlib
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = "9.0.9"
URL = "https://gitlab.com/kicad/libraries/kicad-footprints/-/raw/%s/Inductor_SMD.pretty/%s.kicad_mod"
NAMES = ("L_Coilcraft_XAL4020-XXX", "L_Coilcraft_XAL4030-XXX", "L_Coilcraft_XAL6030-XXX", "L_Coilcraft_XAL6060-XXX")


def parse(text):
    descr = re.search(r'\(descr "([^"]*)"', text)
    model = re.search(r'\(model "([^"]*)"', text)
    pads = []
    for m in re.finditer(r'\(pad "(\d+)" smd (\w+)\s*\(at ([-\d.]+) ([-\d.]+)(?: [-\d.]+)?\)\s*\(size ([-\d.]+) ([-\d.]+)\)', text):
        pads.append(dict(number=m.group(1), shape=m.group(2), at=[float(m.group(3)), float(m.group(4))], size=[float(m.group(5)), float(m.group(6))]))
    box = {}
    for m in re.finditer(r'\(fp_(?:line|rect)\s*\(start ([-\d.]+) ([-\d.]+)\)\s*\(end ([-\d.]+) ([-\d.]+)\).*?\(layer "([^"]+)"\)', text, re.S):
        x0, y0, x1, y1 = (float(m.group(i)) for i in range(1, 5))
        b = box.setdefault(m.group(5), [x0, y0, x0, y0])
        b[:] = [min(b[0], x0, x1), min(b[1], y0, y1), max(b[2], x0, x1), max(b[3], y0, y1)]
    return dict(descr=descr.group(1) if descr else None, model=model.group(1) if model else None, pads=pads,
                outline={k: box[k] for k in ("F.CrtYd", "F.Fab", "F.SilkS") if k in box})


def main():
    out = dict(what="KiCad footprint library %s, Inductor_SMD.pretty, the four Coilcraft XAL footprints: description, pads and 3D model "
                    "parsed from each file (the files themselves not filed)" % TAG, read_by="MESHSAT-1357 Layer 6 record l6r2 round 3",
               read_utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), footprints={})
    for n in NAMES:
        u = URL % (TAG, n)
        data = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
        text = data.decode("utf-8")
        if not text.lstrip().startswith("(footprint"): sys.exit("read_kicad_footprints: %s is not a footprint file" % u)
        out["footprints"][n] = dict(url=u, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), **parse(text))
        print("read_kicad_footprints: %s %s" % (n, out["footprints"][n]["descr"]))
    p = os.path.join(HERE, "inputs", "kicad-xal-footprints-%s.json" % TAG)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, sort_keys=True); fh.write("\n")
    print("written", os.path.relpath(p, HERE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
