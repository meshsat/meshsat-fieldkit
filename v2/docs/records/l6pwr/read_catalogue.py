#!/usr/bin/env python3
"""read_catalogue.py: the public catalogue readings behind the Layer 6 record l6pwr (MESHSAT-1357, 3 October 2026).

It asks three public sources, no login, no cart, no order, and writes one JSON reading each under inputs/:
  LCSC product detail   GET https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=<code>   -> inputs/lcsc-<date>.json
                        (model, brand, package, stock, the USD price ladder, the minimum buy, the sheet LCSC links)
  JLCPCB parts search   POST https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList
                        (the endpoint jlc_certify.py uses; keyword, page 1) for the parts whose drafts carry no code
                                                                                              -> inputs/jlc-search-<date>.json
  Samsung spec pages    GET https://weblib.samsungsem.com/mlcc/mlcc-ec-data-sheet.do?partNumber=<part without the E>
                        the properties the page prints (capacitance, tolerance, rated Vdc, TCC, size, dimensions) and what it does
                        NOT print (a temperature range); the page is date-stamped at every request and reads 'All rights reserved',
                        so its bytes are not filed and no sha256 is pinned: this excerpt is the reading -> inputs/samsung-spec-pages-<date>.json
A stock figure and a price are true at their time only; l6pwr_parts.py reads these files and never the network.
Usage: read_catalogue.py [--date YYYY-MM-DD] [--only lcsc|jlc|samsung]"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.request
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, "inputs")
UA = {"User-Agent": "Mozilla/5.0"}
LCSC = "https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=%s"
JLC = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"
SAMSUNG = "https://weblib.samsungsem.com/mlcc/mlcc-ec-data-sheet.do?partNumber=%s"

# the codes the Layer 4 drafts carry, the drawn parts they replace, and the codes the searches below found for the uncoded rows
CODES = ["C5219071", "C2871872", "C3278350", "C2846047", "C1849461", "C72264", "C17556513", "C2687963", "C473333", "C224048",
         "C135160", "C80273", "C224047", "C55151", "C138687", "C89632", "C2076144", "C844695", "C44322", "C132788", "C43698",
         "C189211", "C2904240", "C2904239", "C2904242", "C2903491", "C2903482", "C500739", "C2985708", "C278516", "C242139", "C1613"]
KEYWORDS = ["TPS16630", "SMCJ30A", "CL32B225KCJSNNE", "CL32B106KBJNNNE", "CL31B106KBHNNNE", "BUK6Y10-30P", "TPS3808G33", "EEHZK1V331P"]
SAMSUNG_PARTS = ["CL32B225KCJSNN", "CL32B106KBJNNN", "CL31B106KBHNNN"]


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get(url, data=None):
    req = urllib.request.Request(url, data=data, headers=dict(UA, **({"Content-Type": "application/json"} if data else {})))
    return urllib.request.urlopen(req, timeout=60).read()


def read_lcsc(date):
    rows = []
    for code in CODES:
        t = now()
        try:
            d = json.loads(get(LCSC % code).decode("utf-8"))
            r = d.get("result") or {}
        except Exception as e:
            rows.append(dict(code=code, read_utc=t, error=str(e)[:120]))
            continue
        params = {p.get("paramNameEn"): p.get("paramValueEn") for p in (r.get("paramVOList") or []) if p.get("paramNameEn")}
        rows.append(dict(code=code, read_utc=t, model=r.get("productModel"), brand=r.get("brandNameEn"), package=r.get("encapStandard"),
                         stock=r.get("stockNumber"), min_buy=r.get("minBuyNumber"), reel=r.get("minPacketNumber"),
                         price_usd=[[p.get("ladder"), p.get("usdPrice")] for p in (r.get("productPriceList") or [])],
                         pdf=r.get("pdfUrl"), desc=r.get("productDescEn"), params=params))
        print("lcsc %-10s %-24s %-26s stock %s" % (code, r.get("productModel"), r.get("brandNameEn"), r.get("stockNumber")))
    doc = dict(what="LCSC public product-detail answers (GET %s), no login, no cart; the codes the Layer 4 power drafts carry, the "
                    "drawn parts they replace and the codes the keyword searches found for the uncoded rows" % (LCSC % "<code>"),
               read_by="MESHSAT-1357 Layer 6 record l6pwr", rows=rows)
    write("lcsc-%s.json" % date, doc)


def read_jlc(date):
    out = []
    for kw in KEYWORDS:
        t = now()
        body = json.dumps({"keyword": kw, "currentPage": 1, "pageSize": 20, "searchSource": "search"}).encode()
        try:
            d = json.loads(get(JLC, body).decode("utf-8"))
            lst = (((d.get("data") or {}).get("componentPageInfo") or {}).get("list")) or []
        except Exception as e:
            out.append(dict(keyword=kw, read_utc=t, error=str(e)[:120], rows=[]))
            continue
        rows = [dict(code=r.get("componentCode"), model=r.get("componentModelEn"), brand=r.get("componentBrandEn"),
                     package=r.get("componentSpecificationEn"), stock=r.get("stockCount"), describe=(r.get("describe") or "")[:160])
                for r in lst]
        out.append(dict(keyword=kw, read_utc=t, count=len(rows), rows=rows))
        print("jlc  %-18s %d rows" % (kw, len(rows)))
    doc = dict(what="JLCPCB public parts search (POST %s; keyword, page 1, 20 a page), no login; code, model, brand, package, "
                    "stock and the catalogue's description kept" % JLC, read_by="MESHSAT-1357 Layer 6 record l6pwr", searches=out)
    write("jlc-search-%s.json" % date, doc)


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.t = []; self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"): self.skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style"): self.skip = False

    def handle_data(self, d):
        if not self.skip and d.strip(): self.t.append(d.strip())


def read_samsung(date):
    out = []
    for pn in SAMSUNG_PARTS:
        t = now()
        try:
            html_ = get(SAMSUNG % pn).decode("utf-8", "replace")
        except Exception as e:
            out.append(dict(part=pn + "E", page_part=pn, read_utc=t, error=str(e)[:120]))
            continue
        p = _Text(); p.feed(html_); cells = p.t
        try:
            i = cells.index("Value")
            vals = cells[i + 1:i + 9]
        except ValueError:
            vals = []
        props = {}
        if len(vals) >= 8:
            props = dict(capacitance=vals[0], tolerance=vals[1], rated_vdc=vals[2], tcc=vals[3], size=vals[4] + " " + vals[5],
                         length=vals[6], width=vals[7], thickness=(cells[i + 9] if len(cells) > i + 9 else None))
        created = next((cells[j + 1] for j, c in enumerate(cells) if c.startswith("Created") and j + 1 < len(cells)), None)
        text = " | ".join(cells)
        out.append(dict(part=pn + "E", page_part=pn, url=SAMSUNG % pn, read_utc=t, properties=props, page_created=created,
                        prints_a_temperature_range=bool(re.search(r"(?i)operating temp|temperature range|-55|125 ?(C|℃)", text)),
                        terms=[c for c in cells if "rights reserved" in c.lower() or "subject to change" in c.lower()][:2],
                        note="the page's bytes carry its creation time and change at every request; held back from the tree by its "
                             "'All rights reserved' line under the owner's rule of 27 September 2026; this excerpt is the reading"))
        print("samsung %-16s %s" % (pn, props))
    doc = dict(what="Samsung Electro-Mechanics MLCC specification pages (GET %s), the properties each page prints" % (SAMSUNG % "<part>"),
               read_by="MESHSAT-1357 Layer 6 record l6pwr", pages=out)
    write("samsung-spec-pages-%s.json" % date, doc)


def write(name, doc):
    os.makedirs(INPUTS, exist_ok=True)
    path = os.path.join(INPUTS, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False); fh.write("\n")
    print("written", os.path.relpath(path, HERE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    if a.only in ("", "lcsc"): read_lcsc(a.date)
    if a.only in ("", "jlc"): read_jlc(a.date)
    if a.only in ("", "samsung"): read_samsung(a.date)
    return 0


if __name__ == "__main__":
    sys.exit(main())
