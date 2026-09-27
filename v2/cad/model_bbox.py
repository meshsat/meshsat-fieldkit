#!/usr/bin/env python3
"""Fetch the KiCad 9 library STEP models the committed boards name and record each one's bounding box (MESHSAT-1357, 27 Sep 2026): the height
source of v2/cad/zstack.py. Every model a footprint of a current board file names (the board each routeflow profile names, and board E5) is
fetched from the KiCad library repository at a pinned tag, its sha256 recorded, and its bounding box computed with OpenCASCADE (build123d).
Where the footprint names a model file the library does not carry at that tag, SUBSTITUTES names the same package body's model, which stands
in and is labelled; a model with neither is recorded as an error, and zstack.py then gives the part a declared class height or TBD.

Needs the network (gitlab.com) and the CAD set of v2/cad/requirements-cad.txt. Usage:
    model_bbox.py <download dir> > v2/cad/zstack-models.json
The output is committed; zstack.py and everything downstream of it run from the committed file with the standard library alone."""
import sys, os, re, json, hashlib, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

TAG = "9.0.9"                                   # kicad-packages3D tag matching KiCad 9.0.9, the version the boards are generated with
BASE = "https://gitlab.com/kicad/libraries/kicad-packages3D/-/raw/%s/" % TAG
SUBSTITUTES = {   # the footprint's named file (absent at TAG) -> the library's model of the same body
    "Connector_IDC.3dshapes/IDC-Header_2x05_P2.54mm_Vertical_NarrowPad.step": "Connector_IDC.3dshapes/IDC-Header_2x05_P2.54mm_Vertical.step",
    "Connector_IDC.3dshapes/IDC-Header_2x08_P2.54mm_Vertical_NarrowPad.step": "Connector_IDC.3dshapes/IDC-Header_2x08_P2.54mm_Vertical.step",
    "Connector_IDC.3dshapes/IDC-Header_2x13_P2.54mm_Vertical_NarrowPad.step": "Connector_IDC.3dshapes/IDC-Header_2x13_P2.54mm_Vertical.step",
    "Connector_RJ.3dshapes/RJ45_Amphenol_RJHSE5380.step": "Connector_RJ.3dshapes/RJ45_Amphenol_RJHSE538X.step",
    "Connector_Coaxial.3dshapes/SMA_Amphenol_132134_Vertical.step": "Connector_Coaxial.3dshapes/SMA_Amphenol_132134-11_Vertical.step",
    "Package_DFN_QFN.3dshapes/QFN-16-1EP_3x3mm_P0.5mm_EP1.75x1.75mm.step": "Package_DFN_QFN.3dshapes/QFN-16-1EP_3x3mm_P0.5mm_EP1.7x1.7mm.step",
    "Package_DFN_QFN.3dshapes/QFN-24-1EP_4x4mm_P0.5mm_EP2.5x2.5mm.step": "Package_DFN_QFN.3dshapes/QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm.step",
    "Package_DFN_QFN.3dshapes/QFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm.step": "Package_DFN_QFN.3dshapes/QFN-32-1EP_5x5mm_P0.5mm_EP3.3x3.3mm.step",
    "Package_DFN_QFN.3dshapes/QFN-64-1EP_9x9mm_P0.5mm_EP4.7x4.7mm.step": "Package_DFN_QFN.3dshapes/QFN-64-1EP_9x9mm_P0.5mm_EP4.1x4.1mm.step",
    "Package_SO.3dshapes/HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.85x5.4mm.step": "Package_SO.3dshapes/HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP3.4x9.5mm.step",
}


def model_paths():
    import zstack
    names = set()
    for k in ("e", "e5", "a", "d", "b", "c", "p"):
        txt = open(zstack.board_file(k), encoding="utf-8").read()
        names |= set(m.replace("${KICAD9_3DMODEL_DIR}/", "") for m in re.findall(r'\(model "([^"]*)"', txt))
    return sorted(names)


def fetch(rel, root):
    dst = os.path.join(root, rel)
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        urllib.request.urlretrieve(BASE + urllib.request.quote(rel), dst)
    return dst


def bbox(path):
    from build123d import import_step
    bb = import_step(path).bounding_box()
    return [round(bb.min.X, 4), round(bb.min.Y, 4), round(bb.min.Z, 4)], [round(bb.max.X, 4), round(bb.max.Y, 4), round(bb.max.Z, 4)]


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "3dmodels"
    out = {}
    for rel in model_paths():
        try:
            dst = fetch(rel, root)
        except Exception as e:
            sub = SUBSTITUTES.get(rel)
            if not sub:
                out[rel] = dict(error="not in the library at tag %s: %s" % (TAG, repr(e)[:120])); continue
            dst = fetch(sub, root); lo, hi = bbox(dst); data = open(dst, "rb").read()
            out[rel] = dict(substitute=sub, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), min=lo, max=hi,
                            note="the footprint names a model file the library does not carry at this tag; the same package body's model stands in")
            continue
        data = open(dst, "rb").read()
        try:
            lo, hi = bbox(dst)
            out[rel] = dict(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), min=lo, max=hi)
        except Exception as e:
            out[rel] = dict(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), error=repr(e)[:200])
    json.dump(dict(library="kicad-packages3D", tag=TAG, source=BASE, models=out), sys.stdout, indent=1, sort_keys=True)
