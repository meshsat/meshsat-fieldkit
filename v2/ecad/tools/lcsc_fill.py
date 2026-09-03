#!/usr/bin/env python3
"""Fill LCSC part numbers in a JLC BOM csv from a value+footprint map of JLCPCB basic/preferred parts (only entries verified from the AIOC BOM or earlier sessions).
Usage: lcsc_fill.py <out/jlc/NAME-bom.csv>"""
import csv, sys, re
MAP = {  # (value regex, footprint substring) -> LCSC
 (r"^10k$", "R_0603"): "C25804", (r"^100k$", "R_0603"): "C25803", (r"^1k$", "R_0603"): "C21190", (r"^4\.7k$", "R_0603"): "C23162", (r"^5\.1k$", "R_0603"): "C23186",
 (r"^1\.5k$", "R_0603"): "C22843", (r"^100R$", "R_0603"): "C22775", (r"^22R$", "R_0603"): "C23345", (r"^330R$", "R_0603"): "C23138", (r"^2k$", "R_0603"): "C22975",
 (r"^100n", "C_0603"): "C14663", (r"^22p", "C_0603"): "C1653", (r"^4\.7u$", "C_0603"): "C19666", (r"^4\.7n", "C_0603"): "C53987", (r"^1u$", "C_0603"): "C15849",
 (r"^10u$", "C_0805"): "C15850", (r"^green", "LED_0603"): "C72043", (r"^red", "LED_0603"): "C2286", (r"^600R@100MHz", "L_0603"): "C1002",
 (r"^8MHz", "5032"): "C115962", (r"^USBLC6-2SC6", "SOT-23-6"): "C7519", (r"^INA219", "SOT-23-8"): "C138024", (r"^PCA9555PW", "TSSOP-24"): "C5626", (r"^FE1\.1s", "SSOP-28"): "C2848",
 (r"^USB-C 2\.0 receptacle", "TYPE-C-31-M-12"): "C165948", (r"^BC847BS", "SOT-363"): "C8653",
}
path = sys.argv[1]; rows = list(csv.DictReader(open(path))); filled = 0
for r in rows:
    if r.get("LCSC Part #"): continue
    for (vre, fsub), code in MAP.items():
        if re.match(vre, r["Comment"]) and fsub in r["Footprint"]: r["LCSC Part #"] = code; filled += 1; break
with open(path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Comment", "Designator", "Footprint", "LCSC Part #"]); w.writeheader(); w.writerows(rows)
print("lcsc_fill: %d lines filled, %d still blank of %d" % (filled, sum(1 for r in rows if not r["LCSC Part #"]), len(rows)))
