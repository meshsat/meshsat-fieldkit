#!/usr/bin/env python3
"""read_catalogue.py: the public catalogue reading behind record l6r2 (MESHSAT-1357, 3 October 2026).

It asks JLCPCB's public parts search (the endpoint jlc_certify.py uses; no login, no cart, no order) for every code the design
already carries on an uncoded generic row (lcsc_fill.py's MAP, the certified table, the identity table) and for every keyword the
selector builds from a requirement (package, value, dielectric and voltage for a capacitor; value and package for a resistor;
impedance and package for a ferrite; the type for a small diode), and writes one JSON reading, inputs/jlc-parts-<date>.json:
per code the catalogue line, per keyword its first 100 lines, each with the model, brand, package, stock, library (basic or
extended), the preferred flag, the attributes, the description and the price tiers. l6r2_passives.py reads that file and never the
network. A stock figure and a price are true at their time only.
Usage: read_catalogue.py [--date YYYY-MM-DD]   (run from anywhere in the tree; about one request a second)\n       read_catalogue.py --reduce FILE   (the reduction alone, on a reading already taken)
       read_catalogue.py --date D --missing   (a supplementary reading of what the plan asks and the reading of date D lacks, merged)"""
import datetime
import json
import os
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ask(kw, size):
    body = json.dumps({"keyword": kw, "currentPage": 1, "pageSize": size, "searchSource": "search"}).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(API, data=body, headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"})
            d = json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))
            pi = ((d.get("data") or {}).get("componentPageInfo") or {})
            return [row(r) for r in (pi.get("list") or [])], pi.get("total")
        except Exception as e:
            err = str(e)[:120]; time.sleep(2 + 3 * attempt)
    return None, err


def row(r):
    return dict(code=r.get("componentCode"), model=r.get("componentModelEn"), brand=r.get("componentBrandEn"),
                package=r.get("componentSpecificationEn"), stock=r.get("stockCount"), lib=r.get("componentLibraryType"),
                preferred=bool(r.get("preferredComponentFlag")),
                attributes={a.get("attribute_name_en"): a.get("attribute_value_name") for a in (r.get("attributes") or [])},
                describe=r.get("describe"), sort="%s / %s" % (r.get("firstSortName"), r.get("secondSortName")),
                prices=[dict(**{"from": p.get("startNumber"), "to": p.get("endNumber"), "price": p.get("productPrice")}) for p in (r.get("componentPrices") or [])[:6]])


PKG = __import__("re").compile(r"\b(0201|0402|0603|0805|1206|1210|1812|2010|2512)\b")


def reduce(doc):
    """What is kept of a keyword's answer: the lines whose package is the keyword's own package (a line of another package can
    never meet a requirement whose land names the package), with their first three price tiers. A code's line is kept whole. The
    reduction is recorded in the reading's `reduced` field; it keeps the file a size a public tree can carry."""
    kept = dropped = nostock = 0
    for kw, s in doc["searches"].items():
        m = PKG.search(kw)
        rows = s["rows"]
        if m:
            keep = [r for r in rows if (r.get("package") or "") == m.group(1)]
            dropped += len(rows) - len(keep); rows = keep
        keep = [r for r in rows if r.get("stock")]
        nostock += len(rows) - len(keep); s["rows"] = keep
        for r in s["rows"]:
            r["prices"] = (r.get("prices") or [])[:2]
            r.pop("sort", None)
        kept += len(s["rows"])
    doc["reduced"] = ("per keyword, the lines whose package is the keyword's package and whose stock is not zero (%d kept; %d of other "
                      "packages and %d with no stock dropped: neither can be selected), each line's first two price tiers, the category "
                      "path dropped (the description carries it); a code's line is kept whole" % (kept, dropped, nostock))
    return doc


def main(argv):
    if "--reduce" in argv:
        p = argv[argv.index("--reduce") + 1]
        doc = reduce(json.load(open(p, encoding="utf-8")))
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=0, ensure_ascii=False, sort_keys=True); fh.write("\n")
        print("read_catalogue: reduced %s: %s" % (p, doc["reduced"])); return 0
    date = argv[argv.index("--date") + 1] if "--date" in argv else datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    plan = json.loads(subprocess.run([sys.executable, "-B", os.path.join(HERE, "l6r2_passives.py"), "--plan"], capture_output=True, check=True, text=True).stdout)
    t0 = now()
    codes, searches, errors = {}, {}, []
    prev = None
    if "--missing" in argv:
        # a supplementary reading: only the plan's codes and keywords the reading of this date does not hold, merged into it
        out = os.path.join(HERE, "inputs", "jlc-parts-%s.json" % date)
        prev = json.load(open(out, encoding="utf-8"))
        plan = dict(codes=[c for c in plan["codes"] if c not in prev["codes"]], keywords=[k for k in plan["keywords"] if k not in prev["searches"]])
        print("read_catalogue: supplementary reading of %d codes and %d keywords" % (len(plan["codes"]), len(plan["keywords"])))
    for c in plan["codes"]:
        rows, tot = ask(c, 5)
        hit = [r for r in (rows or []) if r["code"] == c]
        if hit: codes[c] = dict(hit[0], read_utc=now())
        else: errors.append("code %s: %s" % (c, "not answered" if rows is None else "no line carries the code"))
        time.sleep(0.4)
    for kw in plan["keywords"]:
        rows, tot = ask(kw, 100)
        if rows is None: errors.append("keyword %r: %s" % (kw, tot)); continue
        searches[kw] = dict(read_utc=now(), total=tot, rows=rows)
        time.sleep(0.4)
    doc = dict(what="JLCPCB public parts search (POST %s), no login, no cart: the codes the design carries on the uncoded generic rows and the "
                    "selector's keywords; per line the model, brand, package, stock, library, preferred flag, attributes, description and price tiers (USD)" % API,
               read_by="MESHSAT-1357 Layer 6 record l6r2", read_utc=t0, finished_utc=now(), codes=codes, searches=searches, errors=errors)
    if prev is not None:
        sup = reduce(dict(searches=searches))
        prev["codes"].update(codes); prev["searches"].update(sup["searches"]); prev["errors"] = prev.get("errors", []) + errors
        prev.setdefault("supplements", []).append(dict(read_utc=t0, finished_utc=now(), codes=sorted(codes), keywords=sorted(searches), reduced=sup["reduced"]))
        doc = prev
    else:
        doc = reduce(doc)
    out = os.path.join(HERE, "inputs", "jlc-parts-%s.json" % date)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=0, ensure_ascii=False, sort_keys=True); fh.write("\n")
    print("read_catalogue: %d codes, %d keywords, %d errors -> %s" % (len(codes), len(searches), len(errors), os.path.relpath(out, HERE)))
    for e in errors[:20]: print("  " + e)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
