#!/usr/bin/env python3
"""besc1_copper.py <trial dir> <out.json>: read-only, EXPERIMENTAL (Q-B-ESC-1).

Group S3's routed copper on each arm's final board, in mm of track per copper layer, split three ways: by the DSN
class the net routed in (DIFF100_S3, USB_S3, PWR_S3, kicad_default_S3, read from the arm's run/S3/job.dsn), and within
the two pair classes by whether the net is a differential-pair member or single-ended. A pair member is a net whose
name ends in _P or _N with its partner in the same class, plus the two pairs of USB_S3 named another way:
USB_OTG_P3/USB_OTG_N3 (the slot's USB 2.0 on-the-go pair) and MUX3_A1P/MUX3_A1N (the bank mux's A1 channel, AC coupled
by C359 and C360). Also the DSN class lists themselves, so the single-ended members of the pair classes are named."""
import sys, re, json, collections
sys.path.insert(0, "/root/besc1/v2/ecad/tools")
import pcbnew

T, OUT = sys.argv[1:3]
EXTRA = {("/USB_OTG_P3", "/USB_OTG_N3"), ("/MUX3_A1P", "/MUX3_A1N")}
res = {"label": "EXPERIMENTAL (Q-B-ESC-1) S3 copper by layer, class and pair membership", "arms": {}}
for arm in ("a6", "a8"):
    s = open("%s/%s/run/S3/job.dsn" % (T, arm)).read()
    cls = {}
    members = {}
    for m in re.finditer(r"\(class ([^\s()]+)([^()]*)", s):
        if m.group(1).endswith("_S3"):
            nets = [x.strip('"') for x in m.group(2).split()]
            members[m.group(1)] = nets
            for n in nets:
                cls[n] = m.group(1)
    pair = set()
    for c, nets in members.items():
        st = set(nets)
        for n in nets:
            if (n.endswith("_P") and n[:-2] + "_N" in st) or (n.endswith("_N") and n[:-2] + "_P" in st):
                pair.add(n)
        for a, b_ in EXTRA:
            if a in st and b_ in st:
                pair.update((a, b_))
    b = pcbnew.LoadBoard("%s/%s/s3.kicad_pcb" % (T, arm))
    L = collections.defaultdict(float)
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            continue
        n = t.GetNetname()
        if n not in cls:
            continue
        c = cls[n]
        kind = ("pair" if n in pair else "single-ended") if c in ("DIFF100_S3", "USB_S3") else "-"
        L[(b.GetLayerName(t.GetLayer()), c, kind)] += t.GetLength() / 1e6
    rows = {"%s|%s|%s" % k: round(v, 1) for k, v in sorted(L.items())}
    res["arms"][arm] = {"copper_mm": rows,
                        "class_members": {c: {"pair": sorted(n for n in nets if n in pair), "single_ended": sorted(n for n in nets if n not in pair)} for c, nets in members.items()}}
    print("==", arm)
    for k, v in sorted(L.items()):
        print("  %-8s %-18s %-13s %8.1f" % (k[0], k[1], k[2], v))
for c in ("DIFF100_S3", "USB_S3"):
    m = res["arms"]["a6"]["class_members"][c]
    print(c, "nets", len(m["pair"]) + len(m["single_ended"]), "pair members", len(m["pair"]), "single-ended", m["single_ended"])
json.dump(res, open(OUT, "w"), indent=1)
