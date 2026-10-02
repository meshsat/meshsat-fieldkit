#!/usr/bin/env python3
"""fetch_maker_curves.py: fetch the makers' characteristic data the L4-E7 record bounds its ceramics with (B6 round 2, the
external review's L4-F01, 2 October 2026) into the ignored v2/vendor/passives/held/, and keep each excerpt only when it
equals the sha256 l4e7_stage_settings.py pins. Never run by a test; it contacts only the maker's own public product pages.

Held back from the public tree by the conservative reading of the pages' terms (the owner's rule of 27 September 2026):
each page carries "Copyright. SAMSUNG ELECTRO-MECHANICS All rights reserved." and grants no right to redistribute, and
calls its contents "the typical data for design reference only". The record refuses without the three excerpts.

An excerpt samsung-<part>-2026-10-02.json carries the part, the page's URL, the bias of its bias-TCC curve (dsBiasVdc)
and the series the page serves as its chart data, each sorted (the page can serve a series' points out of order): the
DC-bias change (graphType DCBias; its first two points are the chart's maximum and minimum annotations and are dropped),
the temperature change at 0 V and under bias (graphType TCC, graphSubType TCC and BiasTCC) and the ESR against frequency
(graphType |Z|_R, graphSubType R). The page itself is dynamic (it carries its creation time), so the pin is on the
excerpt as this script writes it, not on the page.

Usage:  fetch_maker_curves.py [--root DIR]   (default: this repository's root; exit 0 when every excerpt equals its pin,
        3 otherwise, and an excerpt that differs is not kept)"""
import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
HELD = "v2/vendor/passives/held/samsung-%s-2026-10-02.json"
URL = "https://product.samsungsem.com/mlcc/%s.do"
PARTS = (
    ("CL31B106KBHNNN", "30f54366a810c7861c67ab7d87f6fa8200ecc53ed15d4fbeee38d98fef89531f"),
    ("CL32B106KBJNNN", "d7b01e5e140bac76ee1417d7c0e3e0d719873b9331e824dab23acacf675b71da"),
    ("CL32B225KCJSNN", "07f61b770da06e2d7d98011c53a9e90b5968f850d98db410b736dbcb2055b60f"),
)
METHOD = ("the page's embedded chart data (graphType DCBias, TCC with graphSubType TCC and BiasTCC, |Z|_R with graphSubType "
          "R): x/y pairs as served, each series sorted; the maker's typical characteristic data")


def series(html):
    out = {}
    for blk in re.split(r'\{\s*"graphType" : ', html)[1:]:
        gt = re.match(r'"([^"]+)"', blk).group(1)
        for sub in re.finditer(r'"graphSubType" : "([^"]+)",(.*?)\]\s*\}', blk, re.S):
            out.setdefault(gt + ":" + sub.group(1), [[float(x), float(y)] for x, y in re.findall(r'"x" : "([-\d.eE]+)",\s*"y" : "([-\d.eE]+)"', sub.group(2))])
        if not any(k.startswith(gt + ":") for k in out):
            out.setdefault(gt, [[float(x), float(y)] for x, y in re.findall(r'"x" : "([-\d.eE]+)",\s*"y" : "([-\d.eE]+)"', blk)])
    return out


def excerpt(pn, html):
    """The excerpt's bytes for part pn from its page's HTML."""
    s = series(html)
    vdc = sorted(set(float(v) for v in re.findall(r'"dsBiasVdc" : ([\d.]+)', html)))
    if len(vdc) != 1:
        raise ValueError("%s: the page names %d bias voltages for its bias-TCC curve" % (pn, len(vdc)))
    d = dict(part=pn + "E", maker="Samsung Electro-Mechanics", url=URL % pn, read="2026-10-02", method=METHOD,
             dc_bias_V_percent=sorted(s["DCBias"][2:]), tcc_degC_percent=sorted(s["TCC:TCC"]),
             bias_tcc_degC_percent=sorted(s["TCC:BiasTCC"]), bias_tcc_vdc=vdc[0], esr_MHz_ohm=sorted(s["|Z|_R:R"]))
    return (json.dumps(d, indent=1, ensure_ascii=False) + "\n").encode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args()
    bad = 0
    for pn, want in PARTS:
        req = urllib.request.Request(URL % pn, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            body = excerpt(pn, r.read().decode("utf-8", "replace"))
        got = hashlib.sha256(body).hexdigest()
        path = os.path.join(a.root, HELD % pn)
        if got != want:
            bad += 1
            print("%s: the excerpt is %s, not the pinned %s; not kept" % (pn, got, want))
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(body)
        print("%s: %s %s" % (pn, got, HELD % pn))
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
