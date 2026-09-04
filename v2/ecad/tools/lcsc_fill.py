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
 # matched by the 3 Sep 2026 ordering session on PCB-D (ORDER-LOG.md section 2); the XAL6030 inductor has no JLC equivalent and is bench-fitted
 (r"^TPS61089", "VQFN-RNR0011A"): "C165129", (r"^22u (10|25)V X7R 1210", "C_1210"): "C2918511", (r"^301k", "R_0603"): "C2933194",
 (r"^17\.4k", "R_0603"): "C304711", (r"^20k 1%", "R_0603"): "C4184", (r"^105k", "R_0603"): "C2933128", (r"^100k 1%", "R_0603"): "C25803",

 # --- respin values, 5 Sep 2026: every code below was read off its own JLCPCB part page (research notes in the session scratchpad,
 # summary in appendix 32.28). Four lines carry a substitution rather than the value the design asked for, each noted inline.
 (r"^1\.02k 1%", "R_0603"): "C2998111",
 (r"^10\.0k 1%", "R_0603"): "C25804",
 (r"^10k 1%", "R_0603"): "C25804",
 (r"^100k 1%", "R_0603"): "C25803",
 (r"^102k 1%", "R_0603"): "C2933126",
 (r"^105k 1%", "R_0603"): "C16840",
 (r"^115k 1%", "R_0603"): "C22783",
 (r"^12\.0k 1%", "R_0603"): "C22790",
 (r"^13\.7k 1%", "R_0603"): "C22793",
 (r"^15\.0k 1%", "R_0603"): "C22809",
 (r"^16\.5k 1%", "R_0603"): "C22812",
 (r"^17\.4k\b", "R_0603"): "C2930069",
 (r"^2\.7k 1%", "R_0603"): "C13167",
 (r"^20k 1%", "R_0603"): "C4184",
 (r"^215k 1%", "R_0603"): "C5713280",
 (r"^301k 1%", "R_0603"): "C2933194",
 (r"^33\.2k 1%", "R_0603"): "C23003",
 (r"^34\.8k 1%", "R_0603"): "C2933204",
 (r"^4\.7k 1%", "R_0603"): "C23162",
 (r"^7\.50k 1%", "R_0603"): "C23234",
 (r"^75k 1%", "R_0603"): "C23242",
 (r"^8\.87k\b", "R_0603"): "C2998144",
 (r"^5\.23k 1%", "R_0603"): "C23068",     # the design asks 5.24k, which is not an E96 value: 5.23k is 0.19% low
 (r"^30\.1k 1%", "R_0603"): "C23000",    # the design asks 30.31k: 30.1k is 0.69% low, and both shifts together move the charger trips about a quarter of a degree
 (r"^10k NTC 0603 B3380", "R_0603"): "C13564",
 (r"^0\.05R 1% 1206$", "R_1206"): "C601088",
 (r"^0\.1R 1% 1206$", "R_1206"): "C2903496",
 (r"^10R 2W 2512$", "R_2512"): "C414890",
 (r"^100p$", "C_0603"): "C14858",
 (r"^1n$", "C_0603"): "C1588",
 (r"^3\.3n$", "C_0603"): "C1613",
 (r"^10n$", "C_0603"): "C57112",
 (r"^27p$", "C_0603"): "C107045",
 (r"^47n$", "C_0603"): "C1622",
 (r"^470n 25V$", "C_0603"): "C1623",
 (r"^2\.2u$", "C_0603"): "C57895",
 (r"^4\.7u$", "C_0805"): "C1779",
 (r"^4\.7u 25V$", "C_1206"): "C132170",   # 50 V part, covers both 1206 4.7u lines
 (r"^4\.7u 50V$", "C_1206"): "C132170",
 (r"^10u 25V$", "C_1206"): "C89632",      # 50 V part, covers both 1206 10u lines
 (r"^10u 50V$", "C_1206"): "C89632",
 (r"^22u 25V$", "C_1206"): "C12891",
 (r"^100u 10V$", "C_1206"): "C6119961",
 (r"^10u 25V 1210$", "C_1210"): "C2918497",
 (r"^22u 10V X7R 1210$", "C_1210"): "C2918511",   # 25 V part, better bias at 10 V
 (r"^22u 25V X7R 1210$", "C_1210"): "C2918511",
 (r"^0\.5A hold 1812$", "Fuse_1812"): "C17313",
 (r"^2A hold 1812$", "Fuse_1812"): "C210837",
 (r"^2\.5A hold 1812$", "Fuse_1812"): "C210838",  # 16 V only, check the net (3.6)
 (r"^12 MHz 3225$", "Crystal_SMD_3225"): "C9002",   # 20 pF load, confirm B12 caps (3.5)
 (r"^24 MHz 3225$", "Crystal_SMD_3225"): "C70571",  # 18 pF load, suits the 27p pair
 (r"^2N7002\b", "SOT-23"): "C8545",
 (r"^BC847\b", "SOT-23"): "C20069135",
 (r"^BC857\b", "SOT-23"): "C556165",
 (r"^BAT54\b", "D_SOD-123"): "C7502705",
 (r"^SMBJ5\.0A$", "D_SMB"): "C113974",
 (r"^SMCJ33A\b", "D_SMC"): "C42371548",
 (r"^SMCJ15A$", "D_SMC"): "C42371550",    # the design asked SMBJ15A on an SMC land; the value became SMCJ15A, which also matches the other two TVS parts on that board
 (r"^AP2112K-3\.3\b", "SOT-23-5"): "C51118",
 (r"^TPS2065CDBV\b", "SOT-23-5"): "C353882",   # TI SLVSAU6I: the DBV package is a 5 pin SOT-23, the land was corrected on A19, B12 and D5
 (r"^TPS563201\b", "SOT-23-6"): "C116592",
 (r"^TPS22810DRV\b", "WSON-6"): "C527679",
 (r"^TPS61089\b", "Texas_VQFN-RNR0011A-11"): "C165129",
 (r"^EL817S / PC817", "SOP-4"): "C109227",
 (r"^amber hub$", "LED_0603"): "C965802",
}
path = sys.argv[1]; rows = list(csv.DictReader(open(path))); filled = 0
for r in rows:
    if r.get("LCSC Part #"): continue
    for (vre, fsub), code in MAP.items():
        if re.match(vre, r["Comment"]) and fsub in r["Footprint"]: r["LCSC Part #"] = code; filled += 1; break
with open(path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Comment", "Designator", "Footprint", "LCSC Part #"]); w.writeheader(); w.writerows(rows)
print("lcsc_fill: %d lines filled, %d still blank of %d" % (filled, sum(1 for r in rows if not r["LCSC Part #"]), len(rows)))
