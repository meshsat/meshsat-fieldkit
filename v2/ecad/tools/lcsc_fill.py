#!/usr/bin/env python3
"""Fill LCSC part numbers in a JLC BOM csv from a value+footprint map of JLCPCB basic/preferred parts (only entries verified from the AIOC BOM or earlier sessions).
Usage: lcsc_fill.py <out/jlc/NAME-bom.csv>"""
import csv, sys, re
MAP = {  # (value regex, footprint substring) -> LCSC
 (r"^10k$", "R_0603"): "C25804", (r"^100k$", "R_0603"): "C25803", (r"^1k$", "R_0603"): "C21190", (r"^4\.7k$", "R_0603"): "C23162", (r"^5\.1k$", "R_0603"): "C23186",
 (r"^1\.5k$", "R_0603"): "C22843", (r"^100R$", "R_0603"): "C22775", (r"^22R$", "R_0603"): "C23345", (r"^330R$", "R_0603"): "C23138", (r"^2k$", "R_0603"): "C22975",
 (r"^100n", "C_0603"): "C14663", (r"^22p", "C_0603"): "C1653", (r"^4\.7u$", "C_0603"): "C19666", (r"^4\.7n", "C_0603"): "C53987", (r"^1u$", "C_0603"): "C15849",
 (r"^10u$", "C_0805"): "C15850", (r"^green", "LED_0603"): "C2986059", (r"^red", "LED_0603"): "C2286",
 (r"^blue", "LED_0603"): "C2288",        # KT-0603B, the blue of the same Hubei KENTO series as the red above
 (r"^amber", "LED_0603"): "C165983",     # BL-HJC36G-AV-TRB 605 nm; JLCPCB stocks no amber in the KENTO series
 (r"^status\b", "LED_0603"): "C2986059",# the bare "status (GPIO25)" rows name no colour: green, like every other indicator
 (r"^SS14\b", "D_SMB"): "C51897884",     # the fan flyback diodes on E6
 (r"^0\.25R 1% 2512$", "R_2512"): "C459675",   # RLP25FEER250, 2 W current sense, 1 percent (r"^600R@100MHz", "L_0603"): "C1002", (r"^ferrite 600R$", "L_0603"): "C1002",  # the C BOM writes the value this way round
 (r"^180R?$", "R_0603"): "C22828",        # the shipped C BOM carried C25270, an 0805, on these eleven 0603 lands
 (r"^8MHz", "5032"): "C115962", (r"^USBLC6-2SC6", "SOT-23-6"): "C7519", (r"^INA219", "SOT-23-8"): "C138024", (r"^PCA9555PW", "TSSOP-24"): "C2864778", (r"^FE1\.1s", "SSOP-28"): "C2848",
 (r"^USB-C 2\.0 receptacle", "TYPE-C-31-M-12"): "C165948", (r"^BC847BS", "SOT-363"): "C8653",
 (r"^panel ribbon", "IDC-Header_2x10_P2.54mm_Vertical_SMD"): "C54803514", (r"^e-paper module lead", "PinHeader_1x08_P2.54mm_Vertical_SMD"): "C41417365",   # C5 underside SMD connectors (research note m, 4 Sep)
 # matched by the 3 Sep 2026 ordering session on PCB-D (ORDER-LOG.md section 2); the XAL6030 inductor has no JLC equivalent and is bench-fitted
 (r"^TPS61089", "VQFN-RNR0011A"): "C165129", (r"^22u (10|25)V X7R 1210", "C_1210"): "C2918511", (r"^301k", "R_0603"): "C2933194",
 (r"^17\.4k", "R_0603"): "C304711", (r"^20k 1%", "R_0603"): "C4184", (r"^105k", "R_0603"): "C2933128", (r"^100k 1%", "R_0603"): "C25803",

 # --- respin values, 4 Sep 2026: every code below was read off its own JLCPCB part page (research notes in the session scratchpad,
 # summary in appendix 32.28). Four lines carry a substitution rather than the value the design asked for, each noted inline.
 (r"^1\.02k 1%", "R_0603"): "C2998111",
 (r"^10\.0k 1%", "R_0603"): "C25804",
 (r"^10k 1%", "R_0603"): "C25804",
 (r"^100k 1%", "R_0603"): "C25803",
 (r"^102k 1%", "R_0603"): "C2933126",
 (r"^115k 1%", "R_0603"): "C22783",
 (r"^12\.0k 1%", "R_0603"): "C22790",
 (r"^13\.7k 1%", "R_0603"): "C22793",
 (r"^15\.0k 1%", "R_0603"): "C22809",
 (r"^16\.5k 1%", "R_0603"): "C22812",
 (r"^2\.7k 1%", "R_0603"): "C13167",
 (r"^20k 1%", "R_0603"): "C4184",
 (r"^215k 1%", "R_0603"): "C5713280",
 (r"^33\.2k 1%", "R_0603"): "C23003",
 (r"^34\.8k 1%", "R_0603"): "C2933204",
 (r"^4\.7k 1%", "R_0603"): "C23162",
 (r"^7\.50k 1%", "R_0603"): "C23234",
 (r"^75k 1%", "R_0603"): "C23242",
 (r"^8\.87k\b", "R_0603"): "C2998144",
 (r"^5\.23k 1%", "R_0603"): "C23068",     # the design asks 5.24k, which is not an E96 value: 5.23k is 0.19% low
 (r"^30\.1k 1%", "R_0603"): "C23000",    # the design asks 30.31k: 30.1k is 0.69% low, and both shifts together move the charger trips about a quarter of a degree
 (r"^10k NTC 0603 1%", "R_0603"): "C13564",   # Murata NCP18XH103F03RB, 1% on R and on B; B(25/85) 3434 K, B(25/50) 3380 K, so the gauge takes the table, not one beta
 (r"^0\.05R 1% 1206$", "R_1206"): "C601088",
 (r"^0\.1R 1% 1206$", "R_1206"): "C2903496",
 (r"^10R 2W 2512$", "R_2512"): "C414890",
 (r"^100p$", "C_0603"): "C14858",
 (r"^1n$", "C_0603"): "C1588",
 (r"^3\.3n$", "C_0603"): "C1613",
 (r"^10n$", "C_0603"): "C57112",
 (r"^27p$", "C_0603"): "C107045",    # NP0, 50 V, 5%: correct on the 18 pF load crystal
 (r"^33p$", "C_0603"): "C1663",       # Samsung CL10C330JB8NNNC, C0G, 50 V, 5%, a Basic part: the 20 pF load crystal on B12
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
 (r"^0\.5A hold 1812$", "Fuse_1812"): "C17313",
 (r"^2A hold 1812$", "Fuse_1812"): "C210837",
 (r"^2\.5A hold 30V 1812$", "Fuse_1812"): "C52748011",   # LUTE 1812L250/30GR: 2.5 A hold, 5 A trip, 30 V, 40 A fault; the 16 V part it replaces would not survive the clamp on that rail
 (r"^12 MHz 3225$", "Crystal_SMD_3225"): "C9002",   # 20 pF load, paired with the 33 pF caps
 (r"^24 MHz 3225$", "Crystal_SMD_3225"): "C70571",  # 18 pF load, paired with the 27 pF caps
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
 (r"^Amphenol 10164227-1004A1RLF", "CM5_Conn"): "C7435219",   # B13: the CM5 receptacles, 4.0 mm stack (BergStak sheet in vendor/cm5/)
 (r"^Ebyte E72-2G4M20S1E", "E72"): "C5352930",   # B13: CC2652P ZigBee module
 (r"^CM5 cooler fan", "JST_SH_BM04B"): "C160404",   # B13: JST BM04B-SRSS-TB fan header
 (r"^TPS22810DRV\b", "WSON-6"): "C527679",
 (r"^EL817S / PC817", "SOP-4"): "C109227",
 (r"^amber hub$", "LED_0603"): "C965802",
 (r"^47u 25V$", "C_1206"): "C403725",       # the VBAT bulk: 100 uF 25 V does not exist in 1206 with stock, 47 uF is the ceiling
 (r"^68nH 0805\b", "L_0805"): "C2044803",   # the 145 MHz LPF: 1.2 A and 2 percent, where every 68 nH in 1812 is 450 mA and out of stock
 # P3's three pack-side connectors, 11 September 2026. verify_deliverable refused the P3 folder for them: three
 # BOM lines with no code and no hand-fit declaration. Each is JST's own part on the land the footprint draws,
 # confirmed against JLCPCB's parts API with its pin count, pitch and stock read back from the same record.
 (r"cell tap sense wires.*JST-XH 1x5", "JST_XH_B5B"): "C157991",   # JST B5B-XH-A(LF)(SN), 1x5P 2.5 mm, 14.9 mm body, stock 85,826
 (r"SMBus lead.*JST-XH 1x4", "JST_XH_B4B"): "C594232",             # JST B4B-XH-A-G, 1x4P 2.5 mm, 12.4 mm body, stock 20,031
 (r"cell thermistor.*JST-PH 1x2", "JST_PH_B2B"): "C5251182",       # JST B2B-PH-K-S-GW, 1x2P 2.0 mm, stock 15,304
}
path = sys.argv[1]; rows = list(csv.DictReader(open(path))); filled = 0

# 11 September 2026 (MESHSAT-862). The MAP above is hand-maintained, 90-odd entries against several
# hundred distinct values on the set, which is why 320 of 579 BOM rows had no code. A code should
# enter a BOM because the part was CERTIFIED against JLCPCB's catalogue, not because someone typed it
# into an ic() call, so the certified table fills whatever the MAP does not. The MAP keeps priority:
# its entries carry reasons the table cannot know (a 50 V part covering two 1206 lines, the TPS2065
# package correction), and each of those reasons is a comment beside the entry.
import os as _os
CERT = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),
                     "release", "revA", "order", "JLC-CERTIFIED.tsv")
certified = {}
if _os.path.exists(CERT):
    for _row in csv.DictReader(open(CERT, errors="replace"), delimiter="\t"):
        if (_row.get("verdict") or "").strip() != "CERTIFIED":
            continue
        _c = (_row.get("code") or "").strip()
        if _c:
            certified.setdefault(((_row.get("comment") or "").strip(), (_row.get("fp") or "").strip()), _c)

from_cert = 0
for r in rows:
    if r.get("LCSC Part #"): continue
    for (vre, fsub), code in MAP.items():
        if re.match(vre, r["Comment"]) and fsub in r["Footprint"]: r["LCSC Part #"] = code; filled += 1; break
    if r.get("LCSC Part #"): continue
    code = certified.get((r["Comment"].strip(), r["Footprint"].strip()))
    if code: r["LCSC Part #"] = code; filled += 1; from_cert += 1
with open(path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Comment", "Designator", "Footprint", "LCSC Part #"]); w.writeheader(); w.writerows(rows)
blank = [r for r in rows if not r["LCSC Part #"]]
# 8 Sep 2026 (MESHSAT-862): the blank count used to be printed and read by nobody. A blank line is allowed only by <project>/lcsc-allow.txt
# (one Comment substring per line, a `#` reason after it: bench-fitted modules, connectors ordered elsewhere); the rest is an exit 1 that
# finish_board.sh records in out/jlc/<name>-bom.status and make_handoff.py refuses to build the order set on.
import os
allow = []
# the project directory is two levels above out/jlc/<name>-bom.csv; LCSC_ALLOW overrides the path
ap = os.environ.get("LCSC_ALLOW") or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(path)))), "lcsc-allow.txt")
if os.path.exists(ap):
    for line in open(ap):
        if "#" in line and line.split("#", 1)[0].strip(): allow.append(line.split("#", 1)[0].strip())
not_allowed = [r for r in blank if not any(a in r["Comment"] for a in allow)]
# An allow line that matches no row on this board is not harmless: it reads as cover that does not exist. E's
# list carried `module:` for four sensor headers and the generator writes "Geiger counter module (RadiationD",
# with a bracket and not a colon, so the line matched nothing for as long as it existed and the board's
# deliverable was refused for the five rows it was written to cover (11 September 2026). Counted and named,
# not blocking: a stale line is a defect in the declaration, not in the board.
stale_allow = [a for a in allow if not any(a in r["Comment"] for r in rows)]
print("lcsc_fill: %d lines filled (%d of them from the certified table), %d still blank of %d (%d allow-listed, %d not: %s)" % (filled, from_cert, len(blank), len(rows), len(blank) - len(not_allowed), len(not_allowed), ", ".join(r["Designator"][:24] for r in not_allowed[:8])))
if stale_allow:
    print("lcsc_fill: %d allow line(s) match no row on this board and cover nothing: %s"
          % (len(stale_allow), ", ".join(repr(a) for a in stale_allow[:6])))

# 11 September 2026 (MESHSAT-862). Until today this script ONLY ever filled blanks: the `continue` above
# skips any row that already carries a code, so a code typed into an `ic()` call was never looked at by
# anything. That is how all twenty three codes of lcsc-blocked.txt reached shipped deliverable BOMs, and
# how a BMI270 came to stand where the ATECC608B secure element is named. Every code is checked now.
HERE = os.path.dirname(os.path.abspath(__file__))
bad = []

# 1. Codes this project has already proved wrong. The authority is the hand-curated list, so this fires
#    whether or not the certified table has been regenerated since.
blocked = {}
bp = os.path.join(HERE, "lcsc-blocked.txt")
if os.path.exists(bp):
    for line in open(bp):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        f = line.split()
        if len(f) >= 2:
            blocked[f[0]] = (f[1], " ".join(f[2:]))
for r in rows:
    c = (r.get("LCSC Part #") or "").strip()
    if c in blocked:
        bad.append("%s %s is blocked, use %s (%s)" % (r["Designator"][:18], c, blocked[c][0], blocked[c][1][:60]))

# 2. Every other code against the dated certification. A row is refused when the certifier read that
#    code and found a different part or a package our land cannot take. NO_STOCK is not refused here:
#    stock is a reading of one moment and the order set, not the board, is where it binds.
cert = os.path.join(os.path.dirname(os.path.dirname(HERE)), "release", "revA", "order", "JLC-CERTIFIED.tsv")
if os.path.exists(cert):
    import csv as _csv
    # A code is wrong FOR A PART, not in general, and the certified table says so twice for C2836813: WRONG_MODEL
    # against "ATECC608B-SSHDA-T secure element", because JLCPCB's best answer for that question is a BMI270, and
    # CERTIFIED against "BMI270 six-axis IMU", because that is exactly what the code is. Keyed on the code alone
    # this refused board E's deliverable for a part whose code is right, and lcsc-blocked.txt already carried a
    # line saying so in prose that nothing read (11 September 2026).
    verdicts, certified_for = {}, set()
    for row in _csv.DictReader(open(cert, errors="replace"), delimiter="\t"):
        code = (row.get("bom_code") or "").strip()
        key = (code, (row.get("comment") or "").strip(), (row.get("fp") or "").strip())
        if not code: continue
        if row.get("verdict") in ("WRONG_MODEL", "PACKAGE_MISMATCH"):
            verdicts[key] = (row["verdict"], (row.get("note") or "")[:70])
        elif (row.get("verdict") or "").strip() == "CERTIFIED":
            certified_for.add(key)
    for r in rows:
        c = (r.get("LCSC Part #") or "").strip()
        k = (c, (r.get("Comment") or "").strip(), (r.get("Footprint") or "").strip())
        if c and k in verdicts and k not in certified_for and c not in blocked:
            bad.append("%s %s: %s, %s" % (r["Designator"][:18], c, verdicts[k][0], verdicts[k][1]))

if bad:
    print("lcsc_fill: %d row(s) carry a code this project has checked and rejected:" % len(bad))
    for b in bad[:12]:
        print("   " + b)
    print("   fix the code in the GENERATOR, not in the BOM: a finish re-exports the BOM from the board")
    print("   file it already has, so a code corrected only here comes back on the next regeneration.")
import os as _osv
sys.path.insert(0, _osv.path.dirname(_osv.path.abspath(__file__)))
import verdict as _v
sys.exit(_v.write("lcsc_fill",
                  _v.INCONCLUSIVE if not rows else (_v.FAIL if (not_allowed or bad) else _v.PASS),
                  counts={"rows": len(rows), "blank_over_allowance": len(not_allowed), "rejected_code": len(bad),
                          "stale_allow_lines": len(stale_allow)},
                  denominator=len(rows),
                  evidence=[str(x) for x in (list(not_allowed) + bad)],
                  note="" if rows else "the BOM carried no row, so no code was judged"))
