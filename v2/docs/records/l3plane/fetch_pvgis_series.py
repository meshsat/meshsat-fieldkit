#!/usr/bin/env python3
"""fetch_pvgis_series.py: file PVGIS's hourly series for September at the reference site and plane, the data behind SC-37's
mean day, for the INFORMATIVE weather case of energy_basis.py (stream l3plane, MESHSAT-1357, 30 September 2026).

It asks PVGIS 5.2 seriescalc (European Commission JRC, public data reused with attribution) for the hourly global
irradiance on the 40 degree south plane at Leiden, PVGIS-SARAH2 2005 to 2020 with the terrain horizon (the database, years,
site and plane of the reference day's DRcalc file), keeps the September rows exactly as answered, and writes them with the
answer's own inputs and meta and the whole answer's size and sha256 to
v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json. The whole answer (about 12
MB, every month) is not filed; re-running this script re-fetches it and compares the September rows to the filed ones.

Usage: fetch_pvgis_series.py [--check]   (--check: fetch, and refuse (exit 1) if the September rows differ from the file)"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
URL = ("https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?lat=52.160&lon=4.497&angle=40&aspect=0&raddatabase=PVGIS-SARAH2"
       "&startyear=2005&endyear=2020&usehorizon=1&pvcalculation=0&components=0&outputformat=json")
OUT = "v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    raw = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=180).read()
    ans = json.loads(raw)
    rows = [r for r in ans["outputs"]["hourly"] if r["time"][4:6] == "09"]
    years = sorted({r["time"][:4] for r in rows})
    if len(rows) != 30 * 24 * len(years) or years[0] != "2005" or years[-1] != "2020":
        sys.stderr.write("fetch_pvgis_series: %d September rows over %s; not the expected 16 Septembers\n" % (len(rows), years))
        return 1
    path = os.path.join(TOP, OUT)
    if a.check:
        old = json.load(open(path, encoding="utf-8"))
        same = old["outputs"]["hourly"] == rows
        print("fetch_pvgis_series: September rows %s the filed ones" % ("equal" if same else "DIFFER FROM"))
        return 0 if same else 1
    doc = {"source": {"url": URL, "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                      "answer_bytes": len(raw), "answer_sha256": hashlib.sha256(raw).hexdigest(),
                      "kept": "the answer's September rows (time YYYYMMDD:HHMM UTC, hourly averages), every field as answered; "
                              "the answer's inputs and meta as answered",
                      "by": "v2/docs/records/l3plane/fetch_pvgis_series.py (stream l3plane, MESHSAT-1357)",
                      "licence": "European Commission JRC PVGIS, public data reused with attribution"},
           "inputs": ans["inputs"], "meta": ans["meta"], "outputs": {"hourly": rows}}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print("fetch_pvgis_series: %d rows written to %s; answer %d bytes, sha256 %s" % (
        len(rows), OUT, len(raw), doc["source"]["answer_sha256"]))
    print("fetch_pvgis_series: file sha256 %s, %d bytes" % (hashlib.sha256(open(path, "rb").read()).hexdigest(), os.path.getsize(path)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
