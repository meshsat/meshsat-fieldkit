#!/usr/bin/env python3
"""l4e4_limits.py: layer 4 task L4-E4 (MESHSAT-1357, 1 October 2026). Two of the next implementable power-path choices
of v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md turned into concrete, checkable values, at desk:

  (a) item 2, current-limit coordination on board A (findings A-1, C-1, C-2, C-7, C-9): U3's (BQ25731) IIN_HOST setting
      for REQ-016's 100 W window as a register value, and R11 (the LM5176 U2's average-current sense resistor) chosen from
      the held part's own catalogue family so that the stacked minimum of U2's average-current limit lies above U3's
      maximum input current plus C-9's 0.079 A at -20, 25 and 62.1 C, with C-1's Kelvin tap allowance recomputed;
  (b) item 5's outlet part, R138 (DR-03): the USB-C outlet's current-sense resistor at TI's recommended 5 mOhm, its trip
      window against every PDO's current and the ratings of the parts it protects.

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured; no generator, registry or rendered page
is edited (the draft apply scripts beside this file are for the generator owner). Every figure carries its basis: MAKER
(document, revision, page), NETLIST (board A's committed netlist), MODELED (the energy records), INFERRED (method stated),
ASSUMPTION (a figure no document gives); a figure no held document gives is INCONCLUSIVE.

Section 0 proves, before any result (exit 4 otherwise): 0a r11_dep.py, re-run in a child process, reproduces the committed
r11_dep.out byte for byte; 0b the same main(), run in this process with its locals captured at return, prints the same
bytes, so every figure re-used below (VSNS, the ISNS offset, R11's tolerance and TCR stack, U3's accuracy, the 0.079 A of
other loads, the temperatures, the stage relations) is the one that printed the reproduced record, not a retyped constant.

Run from the repository root:  python3 v2/docs/records/l4e4/l4e4_limits.py > v2/docs/records/l4e4/l4e4_limits.out
Needs pdftotext, pdftoppm and Pillow (through r11_dep.py). Deterministic for the pinned files.
Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction failed."""
import contextlib
import hashlib
import importlib.util
import io
import json
import math
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REC = os.path.join(TOP, "v2", "docs", "records")
R11DEP_PY = "v2/docs/records/r11dep/r11_dep.py"
R11DEP_OUT = "v2/docs/records/r11dep/r11_dep.out"
REPLAY_OUT = "v2/docs/records/l4e/l4e_replay.out"
PINS = {
    R11DEP_PY: "6636a7489d3d1406ec8e4ea68c48169466edeb244ce0de4c350a8aca7161fb56",
    R11DEP_OUT: "f9d2c6f23fab3edcb48ad0116366fe588a514f755aafe56ebd62a0fe9495a209",
    REPLAY_OUT: "59c6eeab16da98f8ddf16880ddcdc1d2a2c910f4256be9b69aade49dd4d2726d",
}
TPS25740 = "v2/vendor/ti/ti-tps25740.pdf"
CSD18510 = "v2/vendor/battery/ti-csd18510q5b.pdf"
BULGIN = "v2/vendor/bulgin/bulgin-4000-series-sealed-usb-c.pdf"
CASE_MARGINS = "v2/docs/CASE-MARGINS.md"
INP = "v2/docs/records/l4e4/inputs"
JLC_SEARCH = INP + "/jlc-search-hojlr2512-3w-2026-10-01.json"
R11_PICK_READING = INP + "/lcsc-C2904240-2026-10-01.json"
R11_ALT_READING = INP + "/lcsc-C2904239-2026-10-01.json"
R138_READING = INP + "/lcsc-C2903482-2026-10-01.json"
TEMPS_NAMES = ("the in-use minimum", "25 C", "the worst inside air")


def refuse(code, msg):
    sys.stderr.write("l4e4_limits: %s; refusing\n" % msg)
    sys.exit(code)


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def load_r11dep():
    """r11_dep.py as a module (its functions and constants), without running its main()."""
    sp = importlib.util.spec_from_file_location("r11_dep", os.path.join(TOP, R11DEP_PY))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def run_main_captured(m):
    """Run r11_dep.main() here with stdout captured and its locals taken at its return (CPython's profile hook)."""
    cap = {}

    def prof(frame, event, _arg):
        if event == "return" and frame.f_code is m.main.__code__:
            cap.update(frame.f_locals)
    buf = io.StringIO()
    old = sys.getprofile()
    sys.setprofile(prof)
    try:
        with contextlib.redirect_stdout(buf):
            rc = m.main()
    finally:
        sys.setprofile(old)
    return rc, buf.getvalue(), cap


def ic_out(s, i_out):
    """The front end's output capacitor current, as r11_dep.py section 4 computes it (INFERRED there): in buck the
    inductor ripple over sqrt(12), in boost I_out x sqrt(D / (1 - D))."""
    if s["mode"] == "buck":
        return s["ripple"] / math.sqrt(12.0)
    return i_out * math.sqrt(s["d"] / (1 - s["d"]))


def compute():
    """Every figure of the record, as a dict (the test module holds its predicates on these)."""
    for rel, want in PINS.items():
        if sha(rel) != want:
            refuse(2, "%s is not the pinned file" % rel)
    out_bytes = open(os.path.join(TOP, R11DEP_OUT), "rb").read()
    # ------------------------------------------------------------------ 0a: r11_dep.py again, in a child process
    ch = subprocess.run([sys.executable, "-B", os.path.join(TOP, R11DEP_PY)], cwd=TOP, capture_output=True)
    r0a = ch.returncode == 0 and ch.stdout == out_bytes
    if not r0a:
        refuse(4, "r11_dep.py's re-run does not reproduce r11_dep.out (exit %d)" % ch.returncode)
    # ------------------------------------------------------------------ 0b: the same main() here, its locals captured
    M = load_r11dep()
    rc, text, L = run_main_captured(M)
    r0b = rc == 0 and text.encode("utf-8") == out_bytes
    if not r0b:
        refuse(4, "r11_dep.main() run in this process does not print r11_dep.out")
    page = M.page

    def need(t, p, w):
        m_ = re.search(p, t, re.M)
        if not m_:
            refuse(3, "%s not found" % w)
        return m_
    vsns, offs, tcr, acc, dt_env = L["vsns"], L["offs"], L["tcr_r"], L["acc"], L["dt_r"]
    t_cold, t_air, loads4, other_i = L["t_cold"], L["t_air"], L["loads4"], L["other_i"]
    p_rated, td0, td1, k_r = L["p_rated"], L["t_derate0"], L["t_derate1"], L["k_r11"]
    band, stage, peak_b = L["band"], L["stage"], L["peak_b"]
    ca, pa = L["ca"], L["pa"]
    temps = (float(t_cold), 25.0, float(t_air))
    R = {"r0a": r0a, "r0b": r0b, "temps": temps, "loads4": loads4, "other_i": other_i, "vsns": vsns, "offs": offs,
         "tcr": tcr, "acc": acc, "t_air": t_air, "t_cold": t_cold, "net_sha": M.sha(M.NET_A), "k_r": k_r}

    def nets(ref):
        return {p: v["net"] for p, v in pa[ref].items()}
    # the C-1 criterion the page accepted for 6.2 mOhm, read from the reproduced record (not retyped)
    R["c1_prior"] = float(need(text, r"the criterion is ([\d.]+) mOhm at 25 C", "r11_dep.out the C-1 criterion").group(1)) * 1e-3

    # ================================================================== (a) U3's IIN_HOST setting
    b1, b10, b25, b26, b80 = (page(M.BQ25731, n) for n in (1, 10, 25, 26, 80))
    need(b1, r"SLUSE66A", "SLUSE66A on p.1")
    lsb = float(need(b80, r"nominal input-current limit range\s+of (\d+) mA to (\d+) mA, with (\d+)-mA resolution", "p.80 the 10 mOhm range").group(3)) * 1e-3
    rng = tuple(float(x) * 1e-3 for x in need(b80, r"nominal input-current limit range\s+of (\d+) mA to (\d+) mA", "p.80 the range").groups())
    add_max = float(need(b80, r"Additional (\d+)-mA \(10-m\S+ sense\s+resistor\)", "p.80 the 100 mA to the maximum").group(1)) * 1e-3
    need(b80, r"The lower boundary is implemented through 50-mA offset at code\s+0\. Note this offset is only applied to code 0", "p.80 code 0 only")
    rows5 = re.findall(r"REG0x0F/0E\(\) = 0x([0-9A-F]{4})H\s+(\d+)\s+(\d+)\s+(\d+)\s+mA", b10)
    need(b10, r"IIIN_DPM_REG_ACC\s+\(-40°C to 105°C\) with", "p.10 IIN_DPM accuracy over -40 to 105 C")
    need(b10, r"5-m[\u03a9\u2126] RAC sensing\s+REG0x0F/0E\(\) = 0x1C00H", "p.10 the accuracy rows are for the 5 mOhm RAC")
    if len(rows5) != 4:
        refuse(3, "SLUSE66A p.10 the four IIN_DPM accuracy rows not parsed")
    acc5 = [(int(h, 16) >> 8, float(lo) * 1e-3, float(ty) * 1e-3, float(hi) * 1e-3) for h, lo, ty, hi in rows5]
    need(b25, r"if 10-m[\u03a9\u2126] sensing is used please configure\s+RSNS_RAC=0b", "p.25 RSNS_RAC=0b for 10 mOhm")
    need(b26, r"when adapter is removed IIN_HOST will be reset\s+one time to 3\.25 A", "p.26 the reset to 3.25 A")
    r16 = ca["R16"]["value"]
    if not (r16.startswith("10mOhm 1% 2512 (RAC") and nets("R16") == {"1": "VBUS20", "2": "CH_ACN"}):
        refuse(3, "board A's R16 is not the 10 mOhm RAC on VBUS20")
    # what the window needs (MODELED, l4e_replay.out section 8) and the records' INFERRED margin under the setting
    rp = open(os.path.join(TOP, REPLAY_OUT), encoding="utf-8").read()
    need(rp, r"8\. THE CHARGE PATH REQ-016'S WINDOW NEEDS \(TYP, 100 W, the lowest bus ([\d.]+) V\)", "replay 8 heading")
    v_bus_low = float(re.search(r"the lowest bus ([\d.]+) V\)", rp).group(1))
    win = re.findall(r"^\s+(declared|high bracket|no loss),? ([\d.]+) x ([\d.]+)\s+the largest power at VBUS20 ([\d.]+) W: U3's input minimum at least"
                     r" ([\d.]+) A; the 50 mA setting at least ([\d.]+) A,", rp, re.M)
    if len(win) != 3:
        refuse(3, "l4e_replay.out section 8's three window rows not parsed")
    m_inf = need(rp, r"A2 WINDOW-SIZED, U3 ([\d.]+) A minimum \(a ([\d.]+) A setting\), HYPOTHETICAL", "replay 8 the window-sized minimum")
    margin_inf = round(float(m_inf.group(2)) - float(m_inf.group(1)), 6)       # the records' INFERRED 0.1 A
    a2_ws = need(rp, r"A2 WINDOW-SIZED, U3 [\d.]+ A minimum \(a [\d.]+ A setting\), HYPOTHETICAL\s+unserved ([\d.]+) / ([\d.]+) Wh", "replay 8 A2 window-sized").groups()
    a2_co = need(rp, r"A2 CORRECTED, U3 [\d.]+ A minimum \(the drafted 6\.2 A setting\)\s+unserved ([\d.]+) / ([\d.]+) Wh", "replay 8 A2 corrected").groups()

    def u3_max(s):
        return max(s + add_max, s * (1 + acc))     # r11_dep.py's rule: the larger of p.80's 100 mA and p.1's 2.5 %
    rows = []
    for lab, e1, e2, pw, req, s_print in win:
        s = math.ceil(round((float(req) + margin_inf) / lsb, 6)) * lsb
        if abs(s - float(s_print)) > 1e-9:
            refuse(4, "the setting rule does not reproduce l4e_replay.out's %s A" % s_print)
        rows.append(dict(label=lab, eff=(float(e1), float(e2)), p_bus=float(pw), req=float(req), setting=round(s, 4),
                         u3max=u3_max(s), serv=u3_max(s) + loads4, serv_replay=s + add_max + loads4))
    pick = rows[0]                                  # the declared efficiencies: the evidence this tree holds (C-8 open)
    code = int(round(pick["setting"] / lsb))
    R.update(window=rows, setting=pick["setting"], code=code, word=code << 8, lsb=lsb, rng=rng, add_max=add_max,
             acc5=acc5, margin_inf=margin_inf, u3max=pick["u3max"], serv=pick["serv"], v_bus_low=v_bus_low,
             req=pick["req"], u3min_inf=pick["setting"] - margin_inf, u3min_p1=pick["setting"] * (1 - acc),
             a2_ws=a2_ws, a2_co=a2_co, r16=r16)

    # ================================================================== (a) R11
    cat = json.load(open(os.path.join(TOP, JLC_SEARCH), encoding="utf-8"))
    cands = []
    for row in cat["rows"]:
        mm = re.fullmatch(r"HoJLR2512-3W-([\d.]+)mR-1%", row["model"])
        if mm and row["stock"] and 5.0 <= float(mm.group(1)) <= 10.0:
            cands.append((float(mm.group(1)) * 1e-3, row["code"], row["model"], row["stock"]))
    cands.sort()

    def tap_rule(r, serv):
        """C-1's margin rule as r11_dep.py section 3 writes it: the copper the shunt's current shares with the two taps,
        both together, at the shunt's working temperature (the 75 K envelope), then at 25 C with the copper at 62.1 C and
        at the ASSUMED 100 C (the criterion)."""
        r_par = (vsns[0] - offs) / serv - r * 1.01 * (1 + tcr * dt_env)
        return r_par, r_par / (1 + M.CU_TCR * (t_air - 25.0)), r_par / (1 + M.CU_TCR * (M.R11_TEMP_MAX - 25.0))

    def choose(serv):
        res, best = [], None
        for r, c_, model, stock in cands:
            lo, ty, hi = band(r)
            tr = tap_rule(r, serv)
            ok = lo > serv and tr[2] >= R["c1_prior"]
            res.append(dict(r=r, code=c_, model=model, stock=stock, band=(lo, ty, hi), tap=tr, ok=ok))
            if ok:
                best = res[-1]            # ascending: the last eligible is the largest value, the lowest fault current
        return res, best
    cand_rows, best = choose(R["serv"])
    alt_rows, alt = choose(rows[1]["serv"])
    if best is None:
        refuse(4, "no catalogue R11 coordinates with the chosen setting")
    r11 = best["r"]
    rd = json.load(open(os.path.join(TOP, R11_PICK_READING), encoding="utf-8"))
    if rd["code"] != best["code"] or rd["model"] != best["model"] or rd["pdf_sha256"] != M.HOJLR[1]:
        refuse(3, "the chosen R11's LCSC reading does not name %s or its sheet is not the held series sheet" % best["code"])
    R.update(cands=cand_rows, r11=r11, r11_pick=best, r11_read=rd, alt=alt, alt_rows=alt_rows)

    # per temperature: R11's own temperature bracket, its dissipation, the stacked minimum three ways
    lo_env = best["band"][0]
    s9, s15 = stage(lo_env, M.VIN_TREE), stage(lo_env, M.VIN_TRACKER)
    p_lim = max((lo_env ** 2 + ic_out(s_, lo_env) ** 2) * r11 * 1.01 for s_ in (s9, s15))
    rise = p_lim * k_r                             # INFERRED: the derating line's K/W, at the band minimum's current
    serv = R["serv"]
    diss = []
    for vin in (M.VIN_TRACKER, M.VIN_TREE):
        s_ = stage(serv, vin)
        diss.append((vin, serv ** 2 * r11 * 1.01, (serv ** 2 + ic_out(s_, serv) ** 2) * r11 * 1.01))
    kel = 2 * 0.01 * r11                           # kelvin_check's own 1 % of the shunt per tap, both taps
    per_t = []
    for t in temps:
        t_hi = t + rise
        dT = max(abs(t - 25.0), abs(t_hi - 25.0))
        r_max = r11 * 1.01 * (1 + tcr * dT)
        cu = 1 + M.CU_TCR * (t_hi - 25.0)
        i_alone = (vsns[0] - offs) / r_max
        i_kel = (vsns[0] - offs) / (r_max + kel * cu)
        i_full = (vsns[0] - offs) / (r_max + best["tap"][2] * cu)
        p_dc = serv ** 2 * r11 * 1.01 * (1 + tcr * dT)
        p_rip = max(d[2] for d in diss) * (1 + tcr * dT)
        allow = p_rated * max(0.0, min(1.0, (td1 - (t + p_rip * k_r)) / (td1 - td0)))
        per_t.append(dict(t=t, t_hi=t_hi, dT=dT, i_alone=i_alone, i_kel=i_kel, i_full=i_full,
                          m_alone=i_alone - serv, m_kel=i_kel - serv, m_full=i_full - serv,
                          p_dc=p_dc, t_dc=t + p_dc * k_r, p_rip=p_rip, t_rip=t + p_rip * k_r, allow=allow))
    load_life = (vsns[0] - offs) / (r11 * 1.01 * 1.01 * (1 + tcr * dt_env)) - serv
    # consequences carried to item 4 (INFERRED by r11_dep.py's own relations; nothing decided here)
    hi_env = best["band"][2]
    can_k0 = max(L["can57"][0] / 5.7, L["can50"][0] / 5.0)
    can_k2 = max(L["can57"][2] / 5.7, L["can50"][2] / 5.0)
    R.update(cu_tcr=M.CU_TCR, rise=rise, p_lim=p_lim, per_t=per_t, diss=diss, kel=kel, load_life=load_life, hi_env=hi_env,
             l1_peak9=peak_b(hi_env, M.VIN_TREE), isat=L["isat"], can=(can_k0 * hi_env, can_k2 * hi_env), can_rating=L["ripple_bulk"],
             held_band=L["held"], prop_band=L["prop"], r11_rated_i=math.sqrt(p_rated / r11))

    # ================================================================== (b) R138
    t4, t11, t28, t29, t31, t49 = (page(TPS25740, n) for n in (4, 11, 28, 29, 31, 49))
    need(t11, r"SLVSDG8B", "SLVSDG8B on p.11")
    vt = need(t11, r"VI\(TRIP\)\s+Current trip shunt voltage\s+HIPWR: 5 A not enabled\s+([\d.]+)\s+([\d.]+)\s+mV\s+"
                   r"HIPWR = DVDD \(5 A enabled\)\s+([\d.]+)\s+([\d.]+)\s+mV", "p.11 VI(TRIP)")
    vtrip3 = (float(vt.group(1)) * 1e-3, float(vt.group(2)) * 1e-3)
    vtrip5 = (float(vt.group(3)) * 1e-3, float(vt.group(4)) * 1e-3)
    need(t31, r"Following the recommended implementation of a 5-m[\u03a9\u2126] sense resistor, when the device is configured to deliver 3\s+"
              r"A \(via HIPWR pin\), the OCP threshold lies between 3\.8 A and 4\.5 A", "p.31 8.3.8.2 TI's 5 mOhm")
    need(t49, r"RS: TPS25740 or TPS25740A OCP set point thresholds are targeted towards a 5 m[\u03a9\u2126], ±1% sense resistor", "p.49 the 3 A example's RS")
    need(t28, r"Low\s+Connected to DVDD or GND directly\s+5, 9, 15", "p.28 Table 2's first row")
    need(t28, r"If the HIPWR pin is pulled high, then Imax = 3 A\.", "p.28 Equation 2's Imax")
    need(t28, r"If the PCTRL pin is high, then Pmax = P\(SEL\)\.", "p.28 Equation 2's Pmax")
    need(t28, r"P\(SEL\) = 93\s+Direct to DVDD", "p.28 Table 3 PSEL direct to DVDD")
    nonpd = float(need(t28, r"The power advertised to non-PD Type-C Sinks is always (\d+) W", "p.28 non-PD 15 W").group(1))
    need(t4, r"For TPS25740A:", "p.4 the EN9V row")
    blk = t29[t29.find("Table 5."):]
    need(blk, r"Max = 3 A", "p.29 Table 5's 3 A block")
    need(blk, r"DVDD through\s+.*\n.*R\(SEL\) or Direct to\s+.*\n\s+DVDD", "p.29 Table 5 HIPWR to DVDD is the 3 A block")
    t5 = re.findall(r"^\s*(Direct to GND|DVDD via R\(SEL\)|GND via ?R\(SEL\)|Direct to DVDD)\s.*?([\d.]+)\s+([\d.]+)\s*$", blk, re.M)
    if len(t5) != 12:
        refuse(3, "p.29 Table 5's twelve 3 A rows not parsed (%d)" % len(t5))
    volts = (5.0, 9.0, 15.0)
    straps = {"HIPWR": nets("U18")["5"], "EN9V": nets("U18")["8"], "PSEL": nets("U18")["12"], "PCTRL": nets("U18")["14"]}
    if straps != {"HIPWR": "PD_DVDD", "EN9V": "GND", "PSEL": "PD_DVDD", "PCTRL": "PD_VAUX"}:
        refuse(3, "U18's straps are not as recorded: %s" % straps)
    pdo = []
    for i, v in enumerate(volts):
        rr = t5[4 * i:4 * i + 4]
        if [x[0].replace("viaR", "via R") for x in rr] != ["Direct to GND", "DVDD via R(SEL)", "GND via R(SEL)", "Direct to DVDD"]:
            refuse(3, "p.29 Table 5's rows at %.0f V not in order" % v)
        pdo.append((v, float(rr[3][2])))           # PSEL direct to DVDD, PCTRL high (VAUX)
    all3 = max(max(float(x[1]), float(x[2])) for x in t5)
    pdo.append((5.0, nonpd / 5.0))                 # the Type-C current a non-PD sink is offered (15 W at 5 V)
    ga = open(os.path.join(TOP, M.GEN_A), encoding="utf-8").read()
    pd_a = float(need(ga, r"^_PD_A, _PD_V, _PD_BUDGET = ([\d.]+), ([\d.]+), ([\d.]+)$", "gen_sch_a.py _PD_A").group(1))
    if "(5, 9, 15 V at 3 A)" not in ca["U18"]["value"]:
        refuse(3, "U18's value no longer states 5, 9, 15 V at 3 A")
    if not (ca["R138"]["value"].startswith("10mOhm 1% 2512") and nets("R138") == {"1": "PD_SW", "2": "PD_VBUS"}
            and nets("U18")["19"] == "PD_SW" and nets("U18")["21"] == "PD_VBUS" and nets("J_USBC_OUT")["1"] == "PD_VBUS"
            and ca["Q27"]["value"].startswith("CSD18510Q5B") and nets("Q27")["1"] == "PD_SW" and nets("Q27")["5"] == "PD_VPWR"):
        refuse(3, "the outlet's R138, U18 sense pins, J_USBC_OUT or Q27 are not as recorded")
    rd138 = json.load(open(os.path.join(TOP, R138_READING), encoding="utf-8"))
    if rd138["model"] != "HoJLR2512-3W-5mR-1%" or rd138["pdf_sha256"] != M.HOJLR[1]:
        refuse(3, "R138's LCSC reading is not HoJLR2512-3W-5mR-1% on the held series sheet")
    r138 = 0.005
    # ratings of the parts the trip protects
    q1 = page(CSD18510, 1)
    need(q1, r"SLPS632", "SLPS632 on p.1")
    q27_id = float(need(q1, r"Continuous Drain Current\(1\)\s+(\d+)", "SLPS632 p.1 continuous drain current (1)").group(1))
    bul = page(BULGIN, 3)
    rec_a = float(need(bul, r"Current rating\s+(\d+)A", "Bulgin 4000 series p.3 current rating").group(1))
    need(open(os.path.join(TOP, CASE_MARGINS), encoding="utf-8").read(), r"\| Bulgin PXP4043/C \(4000 series C-type, rear panel mount\) \|",
         "CASE-MARGINS.md the outlet's receptacle")
    jhdr = ca["J_USBC_OUT"]["value"]

    def trip(r, v, tdev):
        return v[0] / (r * 1.01 * (1 + tcr * tdev)), v[1] / (r * 0.99 * (1 - tcr * tdev))
    i_hi0 = trip(r138, vtrip3, 45.0)[1]
    rise138 = i_hi0 ** 2 * r138 * 1.01 * k_r
    dT138 = max(abs(t_cold - 25.0), abs(t_air + rise138 - 25.0))
    w3 = trip(r138, vtrip3, dT138)
    w5 = trip(r138, vtrip5, dT138)
    drawn = trip(0.010, vtrip3, dT138)
    i_pdo = max(i for _v, i in pdo)
    tap138 = vtrip3[0] / i_pdo - r138 * 1.01 * (1 + tcr * dT138)
    tap138_25 = tap138 / (1 + M.CU_TCR * (t_air + rise138 - 25.0))
    R.update(vtrip3=vtrip3, vtrip5=vtrip5, straps=straps, pdo=pdo, pdo_max=i_pdo, t5max=all3, pd_a=pd_a, r138=r138,
             r138_read=rd138, dT138=dT138, rise138=rise138, w3=w3, w5=w5, drawn=drawn, q27_id=q27_id, rec_a=rec_a,
             r138_rated=math.sqrt(p_rated / r138), jhdr=jhdr, tap138=tap138, tap138_25=tap138_25,
             p138=(3.0 ** 2 * r138 * 1.01, w3[1] ** 2 * r138 * 1.01), stage_band=band(0.010))
    return R


def render(R):
    o = []
    P = o.append
    P("L4-E4: BOARD A'S CURRENT-LIMIT COORDINATION (U3 IIN_HOST, R11) AND THE OUTLET'S TRIP (R138) (l4e4_limits.py,")
    P("MESHSAT-1357). PROTOTYPE DESIGN: nothing bought, built, powered or measured; no generator, registry or page edited.")
    P("Basis per figure: MAKER (document, page), NETLIST, MODELED, INFERRED (method stated), ASSUMPTION; INCONCLUSIVE where no")
    P("held document gives the figure.")
    P("")
    P("0. REPRODUCTIONS (refused, exit 4, if either fails)")
    P("   0a r11_dep.py re-run in a child process reproduces r11_dep.out byte for byte (sha256/16 %s): %s" % (PINS[R11DEP_OUT][:16], "yes" if R["r0a"] else "NO"))
    P("   0b r11_dep.main() run in this process, its locals taken at return, prints the same bytes: %s; every figure below" % ("yes" if R["r0b"] else "NO"))
    P("      that r11_dep.py computes (VSNS, the ISNS offset, R11's tolerance and TCR, U3's accuracy, the other loads, the")
    P("      temperatures, the stage relations, the bands) is taken from that run, not retyped")
    P("   pinned: r11_dep.py %s, l4e_replay.out %s; board A's netlist sha256/16 %s (r11_dep.py's 14 facts hold on it)" % (
        PINS[R11DEP_PY][:16], PINS[REPLAY_OUT][:16], R["net_sha"][:16]))
    P("")
    P("1. U3's IIN_HOST FOR REQ-016's 100 W WINDOW")
    P("   what the window needs at VBUS20 (MODELED, l4e_replay.out 8; the lowest bus %.3f V), with the records' INFERRED %.2f A" % (R["v_bus_low"], R["margin_inf"]))
    P("   between a setting and U3's minimum (C-7), and U3's maximum by r11_dep.py's rule (the larger of SLUSE66A p.80's")
    P("   %.0f mA and p.1's +-%.1f %%), plus C-9's %.3f A of VBUS20's other loads through R11 (r11_dep.out 3, four FETs switching):" % (
        R["add_max"] * 1e3, R["acc"] * 100, R["loads4"]))
    for w in R["window"]:
        P("     %-12s %.2f x %.2f: %.1f W, U3's minimum at least %.3f A -> setting %.2f A, its maximum %.3f A, through R11 %.3f A" % (
            w["label"], w["eff"][0], w["eff"][1], w["p_bus"], w["req"], w["setting"], w["u3max"], w["serv"]))
    P("     (l4e_replay.out 8 prints %.3f / %.3f / %.3f A through R11 with the 100 mA alone; p.1's 2.5 %% is the larger above 4 A," % tuple(w["serv_replay"] for w in R["window"]))
    P("     so the coordination here uses %.3f A for the chosen setting)" % R["serv"])
    P("   CHOSEN: IIN_HOST %.2f A. Reason: the declared efficiencies are the only figures this tree holds for the stage and the" % R["setting"])
    P("     front end (C-8 open, no maker figure); the 0.97 bracket is a sensitivity no document establishes. At %.2f A U3's" % R["setting"])
    P("     INFERRED minimum %.2f A carries all the window gives at the declared figures (%.3f A), and the corrected path's" % (R["u3min_inf"], R["req"]))
    P("     result is unchanged (MODELED, l4e_replay.out 8: A2 window-sized %s / %s Wh unserved at 48 / 72 h, the same as the" % R["a2_ws"])
    P("     drafted 6.2 A's %s / %s Wh). A higher setting asks more than the declared window gives, which is A-2's collapse case;" % R["a2_co"])
    P("     raising it to 5.05 A is a firmware step only once C-8's bench figures reach the bracket, and needs R11 at 7 mOhm (2 below)")
    P("   REGISTER (MAKER SLUSE66A p.80, 9.6.22 and Figure 9-35): R16 is %s (NETLIST), so RSNS_RAC = 0b (p.25, 9.3.5," % R["r16"].split(" (")[0])
    P("     'if 10-mOhm sensing is used please configure RSNS_RAC=0b'; the POR default is 5 mOhm); the 10 mOhm range is %.0f to %.0f mA" % (
        R["rng"][0] * 1e3, R["rng"][1] * 1e3))
    P("     with %.0f mA resolution, a 7-bit code in bits 14:8: code %d (0x%02X), REG0x0F/0E() = 0x%04X; nominal %.2f A; maximum" % (
        R["lsb"] * 1e3, R["code"], R["code"], R["word"], R["setting"]))
    P("     nominal + %.0f mA = %.3f A (p.80), +%.1f %% = %.3f A (p.1); carried %.3f A. The host writes it again after every" % (
        R["add_max"] * 1e3, R["setting"] + R["add_max"], R["acc"] * 100, R["setting"] * (1 + R["acc"]), R["u3max"]))
    P("     adapter removal, which resets IIN_HOST to 3.25 A (p.26, 9.3.6): A-2's startup rule")
    P("   TI's accuracy (MAKER SLUSE66A): p.1 '+-2.5 % input current regulation' (a feature line, no conditions); p.10, 8.5")
    P("     Electrical Characteristics, IIN_DPM_REG_ACC over -40 to 105 C, rows only for the 5 mOhm RAC: " + "; ".join(
        "%.1f A: %.1f to %.1f A" % (ty, lo, hi) for _c, lo, ty, hi in R["acc5"]))
    P("     (+-0.2 A, that is +-1 mV of sense voltage); no row is printed for the 10 mOhm RAC")
    P("   C-7, U3's input-current MINIMUM at %.2f A: INCONCLUSIVE. No TI figure is held for the 10 mOhm RAC. Carried: the records'" % R["setting"])
    P("     INFERRED %.2f A margin, %.2f A (consistent with p.10's +-1 mV over 10 mOhm and with p.80's 100 mA / 200 mA pair for" % (
        R["margin_inf"], R["u3min_inf"]))
    P("     10 / 5 mOhm, INFERRED); read on p.1's 2.5 %% it would be %.3f A, still at or above the %.3f A the window needs" % (R["u3min_p1"], R["req"]))
    P("     (%+.3f A). Closure (the page's): the bench reading at or above %.2f A" % (R["u3min_p1"] - R["req"], R["u3min_inf"]))
    P("")
    P("2. R11, THE LM5176 U2's AVERAGE-CURRENT SENSE (SNVSAI1D p.17 Equation 4, ICL(AVG) = VSNS / RSNS; VSNS %.0f / %.0f / %.0f mV p.7)" % tuple(v * 1e3 for v in R["vsns"]))
    P("   the stacked band, r11_dep.py's own band(): VSNS minimum less the ISNS offset %.1f mV, R11 +1 %% and its TCR %.0f ppm/K" % (R["offs"] * 1e3, R["tcr"] * 1e6))
    P("     over r11_dep.py's 75 K envelope (R11 between -20 C and the ASSUMED 100 C). Must exceed %.3f A (U3 at %.2f A, its maximum" % (R["serv"], R["setting"]))
    P("     %.3f A, plus %.3f A). C-1's tap allowance by r11_dep.py's margin rule; the page accepted %.2f mOhm at 25 C for 6.2 mOhm" % (
        R["u3max"], R["loads4"], R["c1_prior"] * 1e3))
    P("   the held part's catalogue family (JLCPCB's public search for HoJLR2512-3W, %s; 1 %%, 3 W, in stock, 5 to 10 mOhm):" % JLC_SEARCH.rsplit("/", 1)[1])
    for c in R["cands"]:
        P("     %-22s %s stock %6d: band %.3f / %.3f / %.3f A; taps at most %+.3f mOhm working, %+.3f mOhm at 25 C: %s" % (
            c["model"], c["code"], c["stock"], c["band"][0], c["band"][1], c["band"][2], c["tap"][0] * 1e3, c["tap"][2] * 1e3,
            "eligible" if c["ok"] else "not eligible"))
    b = R["r11_pick"]
    P("   CHOSEN: R11 %.0f mOhm, %s, LCSC %s (Milliohm; LCSC's answer %s: %s, %s, %s; its datasheet link returns the held" % (
        R["r11"] * 1e3, b["model"], b["code"], R["r11_read"]["read_utc"], R["r11_read"]["params"]["Tolerance"],
        R["r11_read"]["params"]["Temperature Coefficient"], R["r11_read"]["params"]["Power(Watts)"]))
    P("     series sheet byte for byte, sha256/16 %s, so C-2's 'its sheet filed' holds: MAKER HoJLR2512 p.1 F = +-1 %%, 3 W for" % R["r11_read"]["pdf_sha256"][:16])
    P("     0.5 to 500 mOhm; p.2 TCR +-50 ppm/K for 2 to 500 mOhm). Rule: the LARGEST eligible value, because the band's maximum,")
    P("     the highest permitted current that B-1, B-2 and B-4 must be closed at, falls as R11 rises; 9 mOhm leaves no tap budget")
    P("   per temperature (R11's own temperature from the air to the air plus %.1f K, its rise at the band minimum's %.3f A with" % (R["rise"], b["band"][0]))
    P("     the output ripple all through R11, %.2f W, by the derating line's %.1f K/W, INFERRED as r11_dep.py; TCR on the larger" % (R["p_lim"], R["k_r"]))
    P("     excursion from 25 C; copper of the taps at the upper end, %.5f /K):" % R["cu_tcr"])
    P("     %-8s %-9s %-34s %-34s %-34s" % ("air", "R11 C", "stacked min, R11 alone", "with kelvin_check's 1 % per tap", "with C-1's full allowance"))
    for t in R["per_t"]:
        P("     %6.1f C %4.1f..%-4.1f %.3f A, margin %+.3f A           %.3f A, margin %+.3f A           %.3f A, margin %+.3f A" % (
            t["t"], t["t"], t["t_hi"], t["i_alone"], t["m_alone"], t["i_kel"], t["m_kel"], t["i_full"], t["m_full"]))
    P("     every margin over U3's maximum plus %.3f A is positive at all three; at r11_dep.py's 75 K envelope the stacked" % R["loads4"])
    P("     minimum of R11 alone is %.3f A, margin %+.3f A, which C-1's allowance is defined to take whole" % (b["band"][0], b["band"][0] - R["serv"]))
    P("   C-1 RECOMPUTED (r11_dep.py's margin rule at %.0f mOhm and %.3f A): the copper R11's current shares with the two taps, both" % (R["r11"] * 1e3, R["serv"]))
    P("     together, at most %.3f mOhm at its working temperature; %.3f mOhm at 25 C with the copper at %.1f C and %.3f mOhm with it" % (
        b["tap"][0] * 1e3, b["tap"][1] * 1e3, R["t_air"], b["tap"][2] * 1e3))
    P("     at 100 C: the criterion is %.2f mOhm at 25 C (it was %.2f for 6.2 mOhm). kelvin_check's own 1 %% per tap (%.2f mOhm for" % (
        b["tap"][2] * 1e3, R["c1_prior"] * 1e3, R["kel"] * 1e3))
    P("     both) is stricter and closes it too. Bench 7b.3: the DC voltage across U2 pins 14 and 13 exceeds I x R11 (four-wire)")
    P("     by at most %.2f mOhm x I (%.2f mV at %.3f A)" % (b["tap"][2] * 1e3, b["tap"][2] * R["serv"] * 1e3, R["serv"]))
    d = R["diss"]
    P("   R11's DISSIPATION at %.3f A (in service): %.3f W DC (I2R at +1 %%); with the output ripple all through R11 (an upper" % (
        R["serv"], d[0][1]))
    P("     bound) %s in (r11_dep.py's stage relations). Its own temperature (INFERRED, %.1f K/W):" % (
        " and ".join("%.3f W at %.1f V" % (x[2], x[0]) for x in d), R["k_r"]))
    P("     " + "; ".join("%.1f C air: %.1f C DC, %.1f C upper bound, rating derated to %.2f W" % (t["t"], t["t_dc"], t["t_rip"], t["allow"]) for t in R["per_t"]))
    P("     (MAKER p.2: 3 W derated from 70 C to 0 at 170 C). Rated current sqrt(P/R) %.1f A (p.3); the ASSUMED 100 C of r11_dep.py holds" % R["r11_rated_i"])
    P("   sensitivity, not stacked by r11_dep.py's rule: the series' load-life drift (MAKER p.4, < +-1 % after 1000 h at rated power")
    P("     and 70 C) added as a further +1 %% leaves the 75 K envelope's R11-alone margin at %+.3f A" % R["load_life"])
    P("   carried to item 4 (fault handling; INFERRED by r11_dep.py's relations, nothing decided here): the band's maximum, the")
    P("     highest permitted current, %.3f A (held 10 mOhm %.3f A, the drafted 6.2 mOhm %.3f A); L1's peak at 9 V there %.2f A" % (
        R["hi_env"], R["held_band"][2], R["prop_band"][2], R["l1_peak9"]))
    P("     with Isat's 30 %% drop on the -20 %% tolerance, against the typical Isat %.1f A; VBUS20's worst can scaled %.2f A matched," % (R["isat"], R["can"][0]))
    P("     %.2f A at a 2:1 ESR spread, against %.1f A a can (B-4 stays open at 2:1 unless hiccup bounds the fault, B-2)" % (R["can"][1], R["can_rating"]))
    a = R["alt"]
    P("   NOT CHOSEN: the 0.97 bracket's 5.05 A (%.3f A through R11) would need %s (%s): band %.3f / %.3f / %.3f A, taps %.2f mOhm" % (
        R["window"][1]["serv"], a["model"], a["code"], a["band"][0], a["band"][1], a["band"][2], a["tap"][2] * 1e3))
    P("     at 25 C; its highest permitted current is %.3f A, %.3f A above the chosen R11's; 8 mOhm leaves %.3f mOhm for the taps" % (
        a["band"][2], a["band"][2] - R["hi_env"], [c for c in R["alt_rows"] if abs(c["r"] - R["r11"]) < 1e-9][0]["tap"][2] * 1e3))
    P("     there, so the bracket is a hardware change (R11 and the fault closures), not a register write")
    P("")
    P("3. R138, THE USB-C OUTLET'S OCP SENSE (DR-03), TPS25740A U18")
    P("   NETLIST: R138 '%s' from PD_SW (U18 pin 19 ISNS, Q27's source) to PD_VBUS (U18 pin 21 VBUS, J_USBC_OUT pin 1);" % "10mOhm 1% 2512 (ISNS)")
    P("     straps: HIPWR (pin 5) on %s, EN9V (pin 8) on %s, PSEL (pin 12) on %s, PCTRL (pin 14) on %s" % (
        R["straps"]["HIPWR"], R["straps"]["EN9V"], R["straps"]["PSEL"], R["straps"]["PCTRL"]))
    P("   the PDO table (MAKER SLVSDG8B): Table 2 p.28, EN9V low and HIPWR direct, 5, 9 and 15 V; Equation 2 p.28, HIPWR high,")
    P("     Imax = 3 A, PCTRL high, Pmax = P(SEL) = 93 W (Table 3, PSEL direct to DVDD); Table 5 p.29 (TPS25740A, the 3 A block),")
    P("     PSEL direct to DVDD, PCTRL high: " + ", ".join("%.0f V %.1f A" % pq for pq in R["pdo"][:3]) + "; 8.3.6 p.28: a non-PD Type-C sink is")
    P("     offered %.0f W, %.1f A at 5 V. Every row of Table 5's 3 A block is at most %.1f A (l3batt's 18 W straps among them)." % (
        R["pdo"][3][0] * R["pdo"][3][1], R["pdo"][3][1], R["t5max"]))
    P("     The generator declares the same: U18 '5, 9, 15 V at 3 A', _PD_A %.1f A (gen_sch_a.py). Largest PDO current %.1f A" % (R["pd_a"], R["pdo_max"]))
    P("   TI's recommendation: 5 mOhm (p.31, 8.3.8.2: at 3 A via HIPWR 'the OCP threshold lies between 3.8 A and 4.5 A'; p.49,")
    P("     9.2.4.2.3, the 5, 9 and 15 V at 3 A example: 'targeted towards a 5 mOhm, +-1 % sense resistor', 45 mW at 3 A)")
    rd = R["r138_read"]
    P("   CHOSEN: R138 5 mOhm, %s, LCSC %s (Milliohm; LCSC's answer %s: %s, %s; its datasheet link returns the held HoJLR2512" % (
        rd["model"], rd["code"], rd["read_utc"], rd["params"]["Tolerance"], rd["params"]["Power(Watts)"]))
    P("     series sheet byte for byte: MAKER p.1 F = +-1 %, p.2 TCR +-50 ppm/K). Board A's other 5 mOhm parts are LR2512D-3W-5mR-1%")
    P("     C500739, whose maker sheet is not held (gen_sch_a.py); the held sheet's part is named so the window rests on MAKER figures")
    P("   VI(TRIP) (MAKER p.11, 7.5, V(ISNS) - V(VBUS), -40 to 125 C): %.1f to %.1f mV 'HIPWR: 5 A not enabled'; %.0f to %.0f mV" % (
        R["vtrip3"][0] * 1e3, R["vtrip3"][1] * 1e3, R["vtrip5"][0] * 1e3, R["vtrip5"][1] * 1e3))
    P("     'HIPWR = DVDD (5 A enabled)'. That label contradicts Tables 4 and 5, Equation 2 and 8.3.6, where HIPWR to DVDD is the")
    P("     3 A configuration (l3batt CHECK-3 minor 1 found the same); p.31 ties the 3.8 to 4.5 A threshold to the 3 A configuration")
    P("     and to 5 mOhm, which is %.1f to %.1f mV over 5 mOhm. Taken: the 3 A row (INFERRED from p.29 and p.31 together)" % (
        R["vtrip3"][0] * 1e3, R["vtrip3"][1] * 1e3))
    P("   R138's temperature: the air from %.0f to %.1f C plus %.1f K of its own (its trip maximum's I2R, %.1f K/W INFERRED); TCR over" % (
        R["t_cold"], R["t_air"], R["rise138"], R["k_r"]))
    P("     %.1f K from 25 C" % R["dT138"])
    P("   TRIP WINDOW at 5 mOhm (+-1 %%, TCR): %.3f to %.3f A. Above every PDO: " % R["w3"] + "; ".join(
        "%.0f V %.1f A %+.3f A" % (v, i, R["w3"][0] - i) for v, i in R["pdo"][:3]) + ";")
    P("     the non-PD 5 V %.1f A %+.3f A. (As drawn, 10 mOhm: %.3f to %.3f A, below every 3 A contract: DR-03 reproduced)" % (
        R["pdo"][3][1], R["w3"][0] - R["pdo"][3][1], R["drawn"][0], R["drawn"][1]))
    P("   below the ratings of what it protects (the trip maximum %.3f A):" % R["w3"][1])
    P("     R138 itself: rated current sqrt(3 W / 5 mOhm) %.1f A (MAKER HoJLR2512 p.1, p.3); %.3f W at 3 A, %.3f W at the trip maximum" % (
        R["r138_rated"], R["p138"][0], R["p138"][1]))
    P("     Q27 CSD18510Q5B (NETLIST, the VBUS switch the trip opens): %.0f A continuous (MAKER SLPS632 p.1, note 1: TA 25 C, 1 in2 2 oz)" % R["q27_id"])
    P("     the wall receptacle, Bulgin PXP4043/C (CASE-MARGINS.md): %.0f A (MAKER Bulgin 4000 series sheet p.3, 'Current rating'):" % R["rec_a"])
    P("       %s, %+.3f A" % ("below" if R["w3"][1] < R["rec_a"] else "NOT below", R["rec_a"] - R["w3"][1]))
    P("     board A's J_USBC_OUT '%s': no part number, no maker" % R["jhdr"].split(":")[0])
    P("       rating held: INCONCLUSIVE (its VBUS is one 2.54 mm pin carrying the whole outlet current)")
    P("     the user's cable: no rating held (no e-marker is read; 8.3.6 p.28 caps the advertisement at 3 A for that reason): not judged")
    P("   if the p.11 label were right (%.0f to %.0f mV with HIPWR on DVDD), the window would be %.3f to %.3f A: above the receptacle's" % (
        R["vtrip5"][0] * 1e3, R["vtrip5"][1] * 1e3, R["w5"][0], R["w5"][1]))
    P("     %.0f A. The bench must therefore find the trip current itself, not only a 3 A load without a trip" % R["rec_a"])
    P("   the stage ahead (U19, R81 10 mOhm, r11_dep.py's band at 10 mOhm, INFERRED for R81): %.3f / %.3f / %.3f A; above every PDO," % R["stage_band"])
    P("     overlapping the trip's upper end: in an overload between them the stage limits, VBUS falls, and p.31 treats VBUS below")
    P("     V(VBUS_FTH) as an OCP event")
    P("   R138's taps (INFERRED, C-1's margin rule applied to U18): the copper R138's current shares with ISNS and VBUS at most")
    P("     %.2f mOhm at its working temperature, %.2f mOhm at 25 C, for the trip minimum to stay at or above %.1f A; pcb_sensitive.yaml" % (
        R["tap138"] * 1e3, R["tap138_25"] * 1e3, R["pdo_max"]))
    P("     declares no R138 tap today (a layout item for the generator owner)")
    P("")
    P("4. ACCEPTANCE PREDICATES (held by v2/ecad/tools/tests/test_l4e4.py on these computed values)")
    acc_rows = [
        ("r11_dep.out reproduced byte for byte (child and in-process)", R["r0a"] and R["r0b"]),
        ("U3's INFERRED minimum at the setting covers the window's need at the declared efficiencies", R["u3min_inf"] >= R["req"]),
        ("R11 stacked minimum above U3's maximum + 0.079 A at -20, 25, 62.1 C, alone, with kelvin_check's 1 %, with C-1's allowance",
         all(t["m_alone"] > 0 and t["m_kel"] > 0 and t["m_full"] > 0 for t in R["per_t"])),
        ("R11 stacked minimum (R11 alone) above it at r11_dep.py's 75 K envelope", R["r11_pick"]["band"][0] > R["serv"]),
        ("C-1's recomputed allowance at 25 C at least the page's accepted %.2f mOhm" % (R["c1_prior"] * 1e3), R["r11_pick"]["tap"][2] >= R["c1_prior"]),
        ("R138's trip window above every PDO's current", all(R["w3"][0] > i for _v, i in R["pdo"])),
        ("R138's trip maximum below R138's, Q27's and the receptacle's ratings", R["w3"][1] < min(R["r138_rated"], R["q27_id"], R["rec_a"])),
    ]
    for lab, ok in acc_rows:
        P("   %-118s %s" % (lab, "PASS" if ok else "FAIL"))
    P("")
    P("5. INCONCLUSIVE, AND WHAT THE BENCH MUST STILL SHOW")
    P("   INCONCLUSIVE: C-7 (U3's minimum for the 10 mOhm RAC; carried %.2f A INFERRED); J_USBC_OUT's pin rating (no part); which" % R["margin_inf"])
    P("     VI(TRIP) row board A's strap selects (the maker's own label conflict); R11's actual temperature (the 100 C stays an")
    P("     ASSUMPTION; the INFERRED rise is the derating line's, no thermal resistance printed); the undocumented efficiencies (C-8)")
    P("   bench 7b.1: the front end's CC onset with an electronic load past U3, at -20, 25 and 62 C: above %.3f A at each" % R["serv"])
    P("   bench 7b.3: R11's Kelvin error, at most %.2f mOhm x I at 25 C" % (R["r11_pick"]["tap"][2] * 1e3))
    P("   C-7: U3's input current at the %.2f A setting read at or above %.2f A" % (R["setting"], R["u3min_inf"]))
    P("   the outlet: a 3 A load on each PDO (5, 9, 15 V and the non-PD 5 V) held without a trip; then the trip current itself")
    P("     by a slow ramp, inside %.2f to %.2f A (it would read about %.1f to %.1f A on the p.11 label's reading)" % (R["w3"][0], R["w3"][1], R["w5"][0], R["w5"][1]))
    P("")
    P("END. Desk figures on the makers' pages, the committed netlist and the reproduced records; nothing measured or implemented.")
    return o


def main():
    R = compute()
    sys.stdout.write("\n".join(render(R)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
