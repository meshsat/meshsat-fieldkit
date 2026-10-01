#!/usr/bin/env python3
"""l4e4_limits.py: layer 4 task L4-E4 (MESHSAT-1357, 1 October 2026). Two of the next implementable power-path choices
of v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md turned into concrete, checkable values, at desk:

  (a) item 2, current-limit coordination on board A (findings A-1, C-1, C-2, C-7, C-9): U3's (BQ25731) IIN_HOST setting
      for REQ-016's 100 W window as a register value, its board-current bounds including U3's own sense resistor R16's
      tolerance and TCR (check astra-check-l4e4-1, B1), and R11 (the LM5176 U2's average-current sense resistor) chosen
      together with it from the held part's own catalogue family so that the stacked minimum of U2's average-current limit
      lies above U3's maximum board current plus C-9's 0.079 A at -20, 25 and 62.1 C, with C-1's Kelvin tap allowance
      recomputed;
  (b) item 5's outlet part, R138 (DR-03): the USB-C outlet's current-sense resistor at TI's recommended 5 mOhm, its trip
      window against every PDO's current and the ratings of the parts it protects.

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured; no generator, registry or rendered page
is edited (the draft apply scripts beside this file are for the generator owner). Every figure carries its basis: MAKER
(document, revision, page), NETLIST (board A's committed netlist), MODELED (the energy records), INFERRED (method stated),
ASSUMPTION (a figure no document gives); a figure no held document gives is INCONCLUSIVE.

Section 0 proves, before any result (exit 4 otherwise): 0a r11_dep.py, re-run in a child process, reproduces the committed
r11_dep.out byte for byte; 0b the same main(), run in this process with its locals captured at return, prints the same
bytes, so the figures re-used below (VSNS, the ISNS offset, the TCR, U3's accuracy, the 0.079 A of other loads, the
temperatures, the stage relations, band(), lcsc_fill.py's map and the C2903468 reading) are the ones that printed the
reproduced record. The resistors' TOLERANCE is read from the HoJLR2512 sheet p.1 and each part's LCSC answer, and
r11_dep.py's band() (which types 1 % inside) is checked to equal the band at that tolerance (check astra-check-l4e4-1,
minor 1). The second round (the same check, B2) also writes the outlet's bench procedure from the maker's VBUS windows.

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

    # ------------------------------------------------------------------ the shunts' tolerance and R16 (check B1, minor 1)
    # The tolerance is READ: the HoJLR2512 sheet p.1 (F = +-1 %) and the LCSC answers of each part (C2903468 through
    # r11_dep.py's own run, R16's code by its own lcsc_fill.py lookup; the chosen R11 and R138 from inputs/). r11_dep.py's
    # band() types 1 % inside; it is checked below to equal the band at the read tolerance, so the two cannot drift apart.
    hj1, hj4 = page(M.HOJLR[0], 1), page(M.HOJLR[0], 4)
    tol = float(need(hj1, r"F=±(\d+)%", "HoJLR2512 p.1 the F tolerance").group(1)) / 100.0
    drift = float(need(hj4, r"Load Life\s+JIS-C5201-4\.25\.1\s+< ±(\d+)%", "HoJLR2512 p.4 the load-life drift").group(1)) / 100.0
    tol_s = "±%d%%" % round(tol * 100)
    rd16 = L["rd"]
    r16_codes = [c_ for (v_, f_), c_ in L["mp"].items() if re.match(v_, ca["R16"]["value"]) and f_ in ca["R16"]["footprint"]]
    if r16_codes != [rd16["code"]] or rd16["params"]["Tolerance"] != tol_s or rd16["model"] != "HoJLR2512-3W-10mR-1%":
        refuse(3, "R16 is not lcsc_fill.py's %s at %s" % (rd16["code"], tol_s))
    for r_ in (0.006, 0.008, 0.010):
        mine = ((vsns[0] - offs) / (r_ * (1 + tol) * (1 + tcr * dt_env)), vsns[1] / r_,
                (vsns[2] + offs) / (r_ * (1 - tol) * (1 - tcr * dt_env)))
        if any(abs(a_ - b_) > 1e-12 for a_, b_ in zip(mine, band(r_))):
            refuse(4, "r11_dep.py's band() does not use the sheet's tolerance")
    kel_tap = float(need(text, r"kelvin_check's\s+own (\d+) % per tap", "r11_dep.out kelvin_check's per-tap figure").group(1)) / 100.0
    # R16 (U3's RAC) at the corners: U3 regulates the voltage across R16, so its bounds in board current divide by R16's
    # factor. R16's temperature: r11_dep.py's envelope for R11, -20 C to the ASSUMED 100 C (75 K from 25 C)
    r16_lo = (1 - tol) * (1 - tcr * dt_env)        # R16 at its lowest: U3 passes the most board current
    r16_hi = (1 + tol) * (1 + tcr * dt_env)        # R16 at its highest: the least

    def u3_max(s):
        return max(s + add_max, s * (1 + acc))     # r11_dep.py's rule: the larger of p.80's 100 mA and p.1's 2.5 %

    def board_max(s):
        return u3_max(s) / r16_lo

    def board_min(s):
        return (s - margin_inf) / r16_hi           # C-7: the records' INFERRED margin, conditional

    def serv_of(s):
        return board_max(s) + loads4
    rows = []
    for lab, e1, e2, pw, req, s_print in win:
        req = float(req)
        s_old = math.ceil(round((req + margin_inf) / lsb, 6)) * lsb
        if abs(s_old - float(s_print)) > 1e-9:
            refuse(4, "the old setting rule does not reproduce l4e_replay.out's %s A" % s_print)
        s = math.ceil(round((req * r16_hi + margin_inf) / lsb, 6)) * lsb
        rows.append(dict(label=lab, eff=(float(e1), float(e2)), p_bus=float(pw), req=req, s_old=round(s_old, 4), setting=round(s, 4),
                         old_min=board_min(s_old), old_serv=serv_of(s_old), old_serv_nom=u3_max(s_old) + loads4,
                         u3max=u3_max(s), bmax=board_max(s), bmin=board_min(s), bmin_p1=s * (1 - acc) / r16_hi, serv=serv_of(s),
                         serv_replay=s_old + add_max + loads4))
    pick = rows[0]                                  # the declared efficiencies: the evidence this tree holds (C-8 open)
    code = int(round(pick["setting"] / lsb))
    R.update(window=rows, setting=pick["setting"], code=code, word=code << 8, lsb=lsb, rng=rng, add_max=add_max,
             acc5=acc5, margin_inf=margin_inf, u3max=pick["u3max"], bmax=pick["bmax"], serv=pick["serv"], v_bus_low=v_bus_low,
             req=pick["req"], u3min_ctrl=pick["setting"] - margin_inf, u3min_inf=pick["bmin"], u3min_p1=pick["bmin_p1"],
             a2_ws=a2_ws, a2_co=a2_co, r16=r16, r16_code=rd16["code"], r16_model=rd16["model"], tol=tol, tol_s=tol_s,
             drift=drift, r16_lo=r16_lo, r16_hi=r16_hi, dt_env=dt_env, r_temp_max=M.R11_TEMP_MAX, kel_tap=kel_tap,
             old_setting=pick["s_old"], old_min=pick["old_min"], old_serv=pick["old_serv"], old_serv_nom=pick["old_serv_nom"])

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
        r_par = (vsns[0] - offs) / serv - r * (1 + tol) * (1 + tcr * dt_env)
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
    if rd["code"] != best["code"] or rd["model"] != best["model"] or rd["pdf_sha256"] != M.HOJLR[1] or rd["params"]["Tolerance"] != tol_s:
        refuse(3, "the chosen R11's LCSC reading does not name %s at %s or its sheet is not the held series sheet" % (best["code"], tol_s))
    R.update(cands=cand_rows, r11=r11, r11_pick=best, r11_read=rd, alt=alt, alt_rows=alt_rows)

    def rise_of(r):
        """R11's own rise at its band minimum's current with the output ripple all through it, by the derating line's K/W
        (INFERRED, as r11_dep.py section 4)."""
        lo_ = band(r)[0]
        p_ = max((lo_ ** 2 + ic_out(s_, lo_) ** 2) * r * (1 + tol) for s_ in (stage(lo_, M.VIN_TREE), stage(lo_, M.VIN_TRACKER)))
        return p_, p_ * k_r

    def margins_for(serv, r, tap25):
        """The stacked minimum at each air temperature three ways (R11 alone, kelvin_check's own per-tap figure, the
        full tap allowance tap25 given at 25 C) and its margin over serv. R11 from the air to the air plus its rise, TCR
        on the larger excursion; the taps' copper at the upper end."""
        _p, rise_ = rise_of(r)
        out = []
        for t in temps:
            t_hi = t + rise_
            dT = max(abs(t - 25.0), abs(t_hi - 25.0))
            r_max = r * (1 + tol) * (1 + tcr * dT)
            cu = 1 + M.CU_TCR * (t_hi - 25.0)
            i_alone = (vsns[0] - offs) / r_max
            i_kel = (vsns[0] - offs) / (r_max + 2 * kel_tap * r * cu)
            i_full = (vsns[0] - offs) / (r_max + tap25 * cu)
            out.append(dict(t=t, t_hi=t_hi, dT=dT, i_alone=i_alone, i_kel=i_kel, i_full=i_full,
                            m_alone=i_alone - serv, m_kel=i_kel - serv, m_full=i_full - serv))
        return out

    serv = R["serv"]
    p_lim, rise = rise_of(r11)
    diss = []
    for vin in (M.VIN_TRACKER, M.VIN_TREE):
        s_ = stage(serv, vin)
        diss.append((vin, serv ** 2 * r11 * (1 + tol), (serv ** 2 + ic_out(s_, serv) ** 2) * r11 * (1 + tol)))
    kel = 2 * kel_tap * r11                        # kelvin_check's own 1 % of the shunt per tap, both taps
    per_t = margins_for(serv, r11, best["tap"][2])
    for t in per_t:
        p_dc = serv ** 2 * r11 * (1 + tol) * (1 + tcr * t["dT"])
        p_rip = max(d[2] for d in diss) * (1 + tcr * t["dT"])
        t.update(p_dc=p_dc, t_dc=t["t"] + p_dc * k_r, p_rip=p_rip, t_rip=t["t"] + p_rip * k_r,
                 allow=p_rated * max(0.0, min(1.0, (td1 - (t["t"] + p_rip * k_r)) / (td1 - td0))))
    # the first round's figures (R16 left out) judged with R16 in: the defect check B1 found
    old_tap = tap_rule(r11, R["old_serv_nom"])
    old_per_t = margins_for(R["old_serv"], r11, old_tap[2])
    load_life = (vsns[0] - offs) / (r11 * (1 + tol) * (1 + drift) * (1 + tcr * dt_env)) - serv
    # consequences carried to item 4 (INFERRED by r11_dep.py's own relations; nothing decided here)
    hi_env = best["band"][2]
    can_k0 = max(L["can57"][0] / 5.7, L["can50"][0] / 5.0)
    can_k2 = max(L["can57"][2] / 5.7, L["can50"][2] / 5.0)
    R.update(cu_tcr=M.CU_TCR, rise=rise, p_lim=p_lim, per_t=per_t, diss=diss, kel=kel, load_life=load_life, hi_env=hi_env,
             l1_peak9=peak_b(hi_env, M.VIN_TREE), isat=L["isat"], can=(can_k0 * hi_env, can_k2 * hi_env), can_rating=L["ripple_bulk"],
             held_band=L["held"], prop_band=L["prop"], r11_rated_i=math.sqrt(p_rated / r11), old_tap=old_tap, old_per_t=old_per_t,
             fn=dict(u3_max=u3_max, board_max=board_max, board_min=board_min, serv_of=serv_of, tap_rule=tap_rule,
                     margins_for=margins_for, band=band))

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

    tol138 = float(need(rd138["params"]["Tolerance"], r"^±(\d+)%$", "R138's LCSC tolerance").group(1)) / 100.0
    if tol138 != tol:
        refuse(3, "R138's tolerance is not the series sheet's")

    def trip(r, v, tdev):
        return v[0] / (r * (1 + tol138) * (1 + tcr * tdev)), v[1] / (r * (1 - tol138) * (1 - tcr * tdev))
    i_hi0 = trip(r138, vtrip3, 45.0)[1]
    rise138 = i_hi0 ** 2 * r138 * (1 + tol138) * k_r
    dT138 = max(abs(t_cold - 25.0), abs(t_air + rise138 - 25.0))
    w3 = trip(r138, vtrip3, dT138)
    w5 = trip(r138, vtrip5, dT138)
    drawn = trip(0.010, vtrip3, dT138)
    i_pdo = max(i for _v, i in pdo)
    tap138 = vtrip3[0] / i_pdo - r138 * (1 + tol138) * (1 + tcr * dT138)
    tap138_25 = tap138 / (1 + M.CU_TCR * (t_air + rise138 - 25.0))
    # the bench's VBUS hold window per contract (check B2, and the recheck astra-check-l4e4-2): above the slow UVP and the
    # falling VBUS threshold maxima, below the SMALLER of the fast and the slow OVP minima (MAKER SLVSDG8B p.8, 7.5,
    # TPS25740A rows; p.31: a fast OVP disables GDNG), VBUS strictly inside, so a shutdown inside it is not a voltage fault
    t8 = page(TPS25740, 8)
    ov = t8[t8.find("Over/Under Voltage Protection (VBUS)"):t8.find("V(VAUX)")]
    rws = re.findall(r"^\s*(?:V\(\w+\)\s+)?(?:Fast OVP threshold, always enabled\s+)?(5|9|15) V PD contract(?: \(TPS25740A\))?\s+"
                     r"([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V\s*$", ov, re.M)
    if [int(x[0]) for x in rws] != [5, 9, 15, 5, 9, 15, 5, 9, 15]:
        refuse(3, "SLVSDG8B p.8 the FOVP, SOVP and SUVP rows not parsed: %s" % [x[0] for x in rws])
    fth = need(t8, r"V\(VBUS_FTH\)\s+VBUS Threshold \(Falling voltage\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "p.8 V(VBUS_FTH)")
    fth_max = float(fth.group(3))
    t31v = " ".join(t31.split())
    need(t31v, r"If an over-voltage condition is sensed by the Fast OVP mechanism, GDNG is disabled within tFOVP \+ tFOVPDG",
         "p.31 a fast OVP disables GDNG")
    hold, ovrows = {}, {}
    for i, v in enumerate((5, 9, 15)):
        fovp, sovp, suvp = (tuple(float(x) for x in rws[k * 3 + i][1:]) for k in (0, 1, 2))
        ovrows[v] = dict(fovp=fovp, sovp=sovp, suvp=suvp)
        hold[v] = (max(suvp[2], fth_max), min(fovp[0], sovp[0]))

    def vbus_counts(contract, vbus):
        """A bench run counts only with VBUS strictly inside the contract's window."""
        lo_, hi_ = hold[contract]
        return lo_ < vbus < hi_
    tocp = float(need(t11, r"tOCP\s+Deglitch Filter for over-current protection\s+(\d+)\s+µs", "p.11 tOCP").group(1))
    R.update(vtrip3=vtrip3, vtrip5=vtrip5, straps=straps, pdo=pdo, pdo_max=i_pdo, t5max=all3, pd_a=pd_a, r138=r138,
             r138_read=rd138, dT138=dT138, rise138=rise138, w3=w3, w5=w5, drawn=drawn, q27_id=q27_id, rec_a=rec_a,
             r138_rated=math.sqrt(p_rated / r138), jhdr=jhdr, tap138=tap138, tap138_25=tap138_25, tol138=tol138,
             p138=(3.0 ** 2 * r138 * (1 + tol138), w3[1] ** 2 * r138 * (1 + tol138)), stage_band=band(0.010),
             hold=hold, ovrows=ovrows, fth=tuple(float(fth.group(k)) for k in (1, 2, 3)), fth_max=fth_max, tocp=tocp)
    R["fn"]["vbus_counts"] = vbus_counts
    return R


def render(R):
    o = []
    P = o.append
    P("L4-E4: BOARD A'S CURRENT-LIMIT COORDINATION (U3 IIN_HOST, R11) AND THE OUTLET'S TRIP (R138) (l4e4_limits.py,")
    P("MESHSAT-1357; second round, after check astra-check-l4e4-1). PROTOTYPE DESIGN: nothing bought, built, powered or")
    P("measured; no generator, registry or page edited.")
    P("Basis per figure: MAKER (document, page), NETLIST, MODELED, INFERRED (method stated), ASSUMPTION; INCONCLUSIVE where no")
    P("held document gives the figure.")
    P("")
    P("0. REPRODUCTIONS (refused, exit 4, if either fails)")
    P("   0a r11_dep.py re-run in a child process reproduces r11_dep.out byte for byte (sha256/16 %s): %s" % (PINS[R11DEP_OUT][:16], "yes" if R["r0a"] else "NO"))
    P("   0b r11_dep.main() run in this process, its locals taken at return, prints the same bytes: %s. Taken from that run:" % ("yes" if R["r0b"] else "NO"))
    P("      VSNS, the ISNS offset, the TCR, U3's accuracy, the other loads, the temperatures, the stage relations, band(),")
    P("      lcsc_fill.py's map and the C2903468 reading. The TOLERANCE is read, not typed: the HoJLR2512 sheet p.1 'F=%s'" % R["tol_s"])
    P("      and each part's LCSC answer (%s for C2903468, the chosen R11 and R138); r11_dep.py's band(), which types 1 %%" % R["tol_s"])
    P("      inside, is checked to equal the band at the read tolerance (exit 4 otherwise)")
    P("   pinned: r11_dep.py %s, l4e_replay.out %s; board A's netlist sha256/16 %s (r11_dep.py's 14 facts hold on it)" % (
        PINS[R11DEP_PY][:16], PINS[REPLAY_OUT][:16], R["net_sha"][:16]))
    P("")
    P("1. U3's IIN_HOST FOR REQ-016's 100 W WINDOW, R16 INCLUDED (check B1)")
    P("   U3 regulates the voltage across its RAC, R16 '%s' (NETLIST), lcsc_fill.py's %s %s (the same" % (
        R["r16"], R["r16_code"], R["r16_model"]))
    P("     HoJLR2512 series: %s, TCR %.0f ppm/K, MAKER p.1 and p.2). Its bounds in board current are U3's own bounds divided by" % (R["tol_s"], R["tcr"] * 1e6))
    P("     R16's factor. R16's temperature: r11_dep.py's envelope, -20 C to the ASSUMED %.0f C (%.0f K from 25 C); no thermal figure" % (
        R["r_temp_max"], R["dt_env"]))
    P("     is held for R16 either. R16 at its lowest: x%.5f (U3 passes the most); at its highest: x%.5f (the least)" % (R["r16_lo"], R["r16_hi"]))
    P("   board current: maximum = U3's maximum (the larger of SLUSE66A p.80's %.0f mA and p.1's +-%.1f %%) / R16 low; minimum =" % (
        R["add_max"] * 1e3, R["acc"] * 100))
    P("     (setting less the records' INFERRED %.2f A, C-7, conditional) / R16 high; through R11 the maximum plus C-9's %.6f A" % (
        R["margin_inf"], R["loads4"]))
    P("   what the window needs at VBUS20 (MODELED, l4e_replay.out 8; the lowest bus %.3f V) and the setting that covers it:" % R["v_bus_low"])
    for w in R["window"]:
        P("     %-12s %.2f x %.2f: %.1f W, at least %.3f A: setting %.2f A (minimum %.3f A, maximum %.3f A, through R11 %.3f A)" % (
            w["label"], w["eff"][0], w["eff"][1], w["p_bus"], w["req"], w["setting"], w["bmin"], w["bmax"], w["serv"]))
        P("     %-12s                    the first round's %.2f A with R16 in: minimum %.3f A (%+.3f A), through R11 %.3f A" % (
            "", w["s_old"], w["old_min"], w["old_min"] - w["req"], w["old_serv"]))
    P("   CHOSEN: IIN_HOST %.2f A. The first round's %.2f A fails with R16 in: its minimum %.3f A is under the %.3f A the window" % (
        R["setting"], R["old_setting"], R["old_min"], R["req"]))
    P("     needs, and its %.3f A through R11 exceeds the first round's hot full-tap minimum (section 2). %.2f A is the smallest" % (
        R["old_serv"], R["setting"]))
    P("     50 mA code whose minimum covers the need: %.3f A, %+.3f A. Evidence for the declared row: the declared efficiencies are" % (
        R["u3min_inf"], R["u3min_inf"] - R["req"]))
    P("     the only ones this tree holds (C-8 open). The corrected path's result is unchanged (MODELED, l4e_replay.out 8: A2")
    P("     window-sized %s / %s Wh unserved at 48 / 72 h, as at the drafted 6.2 A's %s / %s Wh): any limit at or above the need" % (
        R["a2_ws"] + R["a2_co"]))
    P("     carries all the window gives (INFERRED from that equality). U3's maximum above the need is A-2's collapse case, handled")
    P("     by A-2's rule (item 1), as for any setting")
    P("   REGISTER (MAKER SLUSE66A p.80, 9.6.22 and Figure 9-35): RSNS_RAC = 0b for the 10 mOhm R16 (p.25, 9.3.5, 'if 10-mOhm")
    P("     sensing is used please configure RSNS_RAC=0b'; the POR default is 5 mOhm); range %.0f to %.0f mA, %.0f mA resolution, a" % (
        R["rng"][0] * 1e3, R["rng"][1] * 1e3, R["lsb"] * 1e3))
    P("     7-bit code in bits 14:8: code %d (0x%02X), REG0x0F/0E() = 0x%04X; U3's own maximum %.3f A (nominal + %.0f mA = %.3f A," % (
        R["code"], R["code"], R["word"], R["u3max"], R["add_max"] * 1e3, R["setting"] + R["add_max"]))
    P("     +%.1f %% = %.3f A), in board current %.3f A. Rewritten after every adapter removal, which resets IIN_HOST to 3.25 A" % (
        R["acc"] * 100, R["setting"] * (1 + R["acc"]), R["bmax"]))
    P("     (p.26, 9.3.6): A-2's startup rule")
    P("   TI's accuracy (MAKER SLUSE66A): p.1 '+-2.5 % input current regulation' (a feature line, no conditions); p.10, 8.5")
    P("     Electrical Characteristics, IIN_DPM_REG_ACC over -40 to 105 C, rows only for the 5 mOhm RAC: " + "; ".join(
        "%.1f A: %.1f to %.1f A" % (ty, lo, hi) for _c, lo, ty, hi in R["acc5"]))
    P("     (+-0.2 A, +-1 mV of sense voltage); no row for the 10 mOhm RAC; neither includes the external resistor's tolerance")
    P("   C-7, U3's input-current MINIMUM at %.2f A: INCONCLUSIVE, the choice CONDITIONAL on it. No TI figure is held for the" % R["setting"])
    P("     10 mOhm RAC. Carried: the records' INFERRED %.2f A, %.2f A at U3, %.3f A in board current with R16 at its highest;" % (
        R["margin_inf"], R["u3min_ctrl"], R["u3min_inf"]))
    P("     p.1's 2.5 %% read as a minimum gives %.3f A (%+.3f A against %.3f A)" % (R["u3min_p1"], R["u3min_p1"] - R["req"], R["req"]))
    P("")
    P("2. R11, THE LM5176 U2's AVERAGE-CURRENT SENSE (SNVSAI1D p.17 Equation 4, ICL(AVG) = VSNS / RSNS; VSNS %.0f / %.0f / %.0f mV p.7)" % tuple(v * 1e3 for v in R["vsns"]))
    P("   the stacked band, r11_dep.py's own band(): VSNS minimum less the ISNS offset %.1f mV, R11 at +%.0f %% and its TCR %.0f ppm/K" % (
        R["offs"] * 1e3, R["tol"] * 100, R["tcr"] * 1e6))
    P("     over r11_dep.py's 75 K envelope. Must exceed %.3f A (U3 at %.2f A, %.3f A in board current with R16, plus %.3f A)." % (
        R["serv"], R["setting"], R["bmax"], R["loads4"]))
    P("     C-1's tap allowance by r11_dep.py's margin rule, chosen with the setting; the page accepted %.2f mOhm at 25 C for 6.2 mOhm" % (R["c1_prior"] * 1e3))
    P("   the held part's catalogue family (JLCPCB's public search for HoJLR2512-3W, %s; 1 %%, 3 W, in stock, 5 to 10 mOhm):" % JLC_SEARCH.rsplit("/", 1)[1])
    for c in R["cands"]:
        P("     %-22s %s stock %6d: band %.3f / %.3f / %.3f A; taps at most %+.3f mOhm working, %+.4f mOhm at 25 C: %s" % (
            c["model"], c["code"], c["stock"], c["band"][0], c["band"][1], c["band"][2], c["tap"][0] * 1e3, c["tap"][2] * 1e3,
            "eligible" if c["ok"] else "not eligible"))
    b = R["r11_pick"]
    P("   CHOSEN: R11 %.0f mOhm, %s, LCSC %s, STILL QUALIFIES at %.2f A (Milliohm; LCSC's answer %s: %s, %s, %s; its" % (
        R["r11"] * 1e3, b["model"], b["code"], R["setting"], R["r11_read"]["read_utc"], R["r11_read"]["params"]["Tolerance"],
        R["r11_read"]["params"]["Temperature Coefficient"], R["r11_read"]["params"]["Power(Watts)"]))
    P("     datasheet link returns the held series sheet byte for byte, sha256/16 %s, so C-2's 'its sheet filed' holds). Rule:" % R["r11_read"]["pdf_sha256"][:16])
    P("     the LARGEST eligible value, because the band's maximum, the highest permitted current that B-1, B-2 and B-4 must be")
    P("     closed at, falls as R11 rises; 9 mOhm leaves no tap budget")
    P("   per temperature (R11's own temperature from the air to the air plus %.1f K, its rise at the band minimum's %.3f A with" % (R["rise"], b["band"][0]))
    P("     the output ripple all through R11, %.2f W, by the derating line's %.1f K/W, INFERRED as r11_dep.py; TCR on the larger" % (R["p_lim"], R["k_r"]))
    P("     excursion from 25 C; copper of the taps at the upper end, %.5f /K; U3's bound from R16's envelope at every row):" % R["cu_tcr"])
    P("     %-8s %-11s %-30s %-34s %-34s" % ("air", "R11 C", "stacked min, R11 alone", "with kelvin_check's %.0f %% per tap" % (R["kel_tap"] * 100),
                                         "with C-1's %.4f mOhm" % (b["tap"][2] * 1e3)))
    for t in R["per_t"]:
        P("     %6.1f C %5.1f..%-5.1f %.3f A, margin %+.3f A       %.3f A, margin %+.3f A           %.3f A, margin %+.3f A" % (
            t["t"], t["t"], t["t_hi"], t["i_alone"], t["m_alone"], t["i_kel"], t["m_kel"], t["i_full"], t["m_full"]))
    P("     every margin over %.3f A is positive at all three; at r11_dep.py's 75 K envelope the stacked minimum of R11 alone is" % R["serv"])
    P("     %.3f A, margin %+.3f A, which C-1's allowance is defined to take whole" % (b["band"][0], b["band"][0] - R["serv"]))
    o_ = R["old_per_t"]
    P("   the first round judged with R16 in (%.2f A, %.3f A through R11, its %.4f mOhm allowance): full-tap margins %s: FAILS" % (
        R["old_setting"], R["old_serv"], R["old_tap"][2] * 1e3, " / ".join("%+.4f A" % t["m_full"] for t in o_)))
    P("   C-1 RECOMPUTED with the setting (r11_dep.py's margin rule at %.0f mOhm and %.3f A): the copper R11's current shares with" % (R["r11"] * 1e3, R["serv"]))
    P("     the two taps, both together, at most %.4f mOhm at its working temperature; %.4f mOhm at 25 C with the copper at %.1f C" % (
        b["tap"][0] * 1e3, b["tap"][1] * 1e3, R["t_air"]))
    P("     and %.4f mOhm with it at 100 C: the criterion is %.2f mOhm at 25 C (rounded down; 0.29 for 6.2 mOhm, 0.54 in the" % (
        b["tap"][2] * 1e3, math.floor(b["tap"][2] * 1e5) / 100))
    P("     first round). kelvin_check's own %.0f %% per tap (%.2f mOhm for both) is stricter and closes it too" % (R["kel_tap"] * 100, R["kel"] * 1e3))
    d = R["diss"]
    P("   R11's DISSIPATION at %.3f A: %.3f W DC (I2R at +%.0f %%); with the output ripple all through R11 (an upper bound) %s in" % (
        R["serv"], d[0][1], R["tol"] * 100, " and ".join("%.3f W at %.1f V" % (x[2], x[0]) for x in d)))
    P("     (r11_dep.py's stage relations). Its own temperature (INFERRED, %.1f K/W): " % R["k_r"] + "; ".join(
        "%.1f C air: %.1f to %.1f C, rating derated to %.2f W" % (t["t"], t["t_dc"], t["t_rip"], t["allow"]) for t in R["per_t"]))
    P("     (MAKER p.2: 3 W derated from 70 C to 0 at 170 C). Rated current sqrt(P/R) %.1f A (p.3); the ASSUMED 100 C holds" % R["r11_rated_i"])
    P("   sensitivity, not stacked by r11_dep.py's rule: the series' load-life drift (MAKER p.4, < +-%.0f %% after 1000 h at rated" % (R["drift"] * 100))
    P("     power and 70 C) added to R11 leaves the 75 K envelope's R11-alone margin at %+.3f A" % R["load_life"])
    P("   carried to item 4 (fault handling; INFERRED by r11_dep.py's relations, nothing decided here): the band's maximum, the")
    P("     highest permitted current, %.3f A (held 10 mOhm %.3f A, the drafted 6.2 mOhm %.3f A); L1's peak at 9 V there %.2f A" % (
        R["hi_env"], R["held_band"][2], R["prop_band"][2], R["l1_peak9"]))
    P("     with Isat's 30 %% drop on the -20 %% tolerance, against the typical Isat %.1f A; VBUS20's worst can scaled %.2f A matched," % (R["isat"], R["can"][0]))
    P("     %.2f A at a 2:1 ESR spread, against %.1f A a can. Candidate remedies (none chosen here): hiccup (B-2), a rated L1 or bank;" % (R["can"][1], R["can_rating"]))
    P("     hiccup's own peak current and ripple must pass item 4's criteria (L1 at most 90 % of Isat at its temperature; every")
    P("     can at most 2.8 A over the ESR bands)")
    a = R["alt"]
    w1 = R["window"][1]
    P("   NOT CHOSEN: the 0.97 bracket's %.2f A (%.3f A through R11 with R16) would need %s (%s): band %.3f / %.3f / %.3f A, taps" % (
        w1["setting"], w1["serv"], a["model"], a["code"], a["band"][0], a["band"][1], a["band"][2]))
    P("     %.2f mOhm at 25 C; its highest permitted current is %.3f A, %.3f A above the chosen R11's: a hardware change (R11 and" % (
        a["tap"][2] * 1e3, a["band"][2], a["band"][2] - R["hi_env"]))
    P("     the fault closures), not a register write")
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
    P("     and to 5 mOhm, which is %.1f to %.1f mV over 5 mOhm. Taken: the 3 A row (INFERRED from p.29 and p.31 together); the" % (
        R["vtrip3"][0] * 1e3, R["vtrip3"][1] * 1e3))
    P("     bench below must demonstrate it")
    P("   R138's temperature: the air from %.0f to %.1f C plus %.1f K of its own (its trip maximum's I2R, %.1f K/W INFERRED); TCR over" % (
        R["t_cold"], R["t_air"], R["rise138"], R["k_r"]))
    P("     %.1f K from 25 C; tolerance +-%.0f %% (its LCSC answer, the series sheet p.1)" % (R["dT138"], R["tol138"] * 100))
    P("   TRIP WINDOW at 5 mOhm: %.3f to %.3f A. Above every PDO: " % R["w3"] + "; ".join(
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
    P("     %.0f A" % R["rec_a"])
    P("   the stage ahead (U19, R81 10 mOhm, r11_dep.py's band at 10 mOhm, INFERRED for R81): %.3f / %.3f / %.3f A; above every PDO," % R["stage_band"])
    P("     overlapping both trip windows: under load U19 can limit first, VBUS falls, and p.31 treats VBUS below V(VBUS_FTH) as")
    P("     an OCP event. A shutdown seen with U19 in the path does not identify U18's comparator (check B2)")
    P("   R138's taps (INFERRED, C-1's margin rule applied to U18): the copper R138's current shares with ISNS and VBUS at most")
    P("     %.2f mOhm at its working temperature, %.2f mOhm at 25 C, for the trip minimum to stay at or above %.1f A; pcb_sensitive.yaml" % (
        R["tap138"] * 1e3, R["tap138_25"] * 1e3, R["pdo_max"]))
    P("     declares no R138 tap today (a layout item for the generator owner)")
    P("   THE OUTLET'S BENCH PROCEDURE (check B2; it cannot pass on U19's limit or a voltage fault):")
    P("     (a) the comparator: U19 held in shutdown (its EN/UVLO, PD_UVLO, to GND; NETLIST: U18 does not use it) and a regulated")
    P("         laboratory supply on PD_VPWR (U18's VPWR and Q27's drain), its current limit set")
    P("         above %.3f A (the higher row's trip maximum) and its no-load current read first (no back-feed); a PD sink on" % R["w5"][1])
    P("         J_USBC_OUT takes the 5 V contract (no voltage transition; 9 and 15 V likewise if the supply follows CTL1 and CTL2);")
    P("         an electronic load steps up from 3.0 A in 10 mA steps, each held at least 1 ms (tOCP %.0f us, p.11). Recorded" % R["tocp"])
    P("         together: U18's differential sense voltage V(pin 19) - V(pin 21) by a Kelvin differential probe, VBUS at pin 21 and")
    P("         at J_USBC_OUT, Q27's gate PD_GDNG, the supply's current-limit flag, the load current, and R138 four-wire at its pads")
    P("     a run COUNTS only if the supply never limits and VBUS stays STRICTLY inside the contract's hold window up to the GDNG")
    P("         falling edge: above the larger of the slow UVP maximum and V(VBUS_FTH)'s maximum (%.1f V), below the SMALLER of the" % R["fth_max"])
    P("         fast OVP and the slow OVP minima (p.31: a fast OVP disables GDNG). MAKER SLVSDG8B p.8, 7.5, TPS25740A rows, min / typ /")
    P("         max V:")
    for v, (lo, hi) in sorted(R["hold"].items()):
        rw = R["ovrows"][v]
        P("         %2d V contract: V(FOVP) %s, V(SOVP) %s, V(SUVP) %s: %.1f V < VBUS < %.1f V (the upper bound the %s minimum)" % (
            v, " / ".join("%g" % x for x in rw["fovp"]), " / ".join("%g" % x for x in rw["sovp"]), " / ".join("%g" % x for x in rw["suvp"]),
            lo, hi, "fast OVP" if rw["fovp"][0] < rw["sovp"][0] else "slow OVP"))
    P("     its CLOSURE: the last differential reading before the GDNG edge, the demonstrated threshold, lies in %.1f to %.1f mV:" % (
        R["vtrip3"][0] * 1e3, R["vtrip3"][1] * 1e3))
    P("         the 3 A row is demonstrated and the trip current lies in %.2f to %.2f A by R138 measured. A threshold in %.0f to %.0f mV" % (
        R["w3"][0], R["w3"][1], R["vtrip5"][0] * 1e3, R["vtrip5"][1] * 1e3))
    P("         demonstrates the label's row instead: R138 is then re-chosen (that window, %.2f to %.2f A, exceeds the receptacle's" % R["w5"])
    P("         %.0f A). Anything else is no result" % R["rec_a"])
    P("     (b) the delivered configuration, U19 in the path: 3.0 A held on each advertised voltage (5, 9 and 15 V, and the non-PD")
    P("         5 V) for at least one hour or to thermal steady state, with no GDNG edge and VBUS strictly inside its hold window")
    P("")
    P("4. ACCEPTANCE PREDICATES (held by v2/ecad/tools/tests/test_l4e4.py on these computed values)")
    acc_rows = [
        ("r11_dep.out reproduced byte for byte (child and in-process); band() at the read tolerance", R["r0a"] and R["r0b"]),
        ("U3's board-current minimum with R16 at its highest covers the window's need (C-7 conditional)", R["u3min_inf"] >= R["req"]),
        ("the first round's 4.65 A fails the same predicate with R16 in", R["old_min"] < R["req"]),
        ("R11 stacked minimum above U3's maximum with R16 + 0.079 A at -20, 25, 62.1 C: alone, with 1 % per tap, with C-1's allowance",
         all(t["m_alone"] > 0 and t["m_kel"] > 0 and t["m_full"] > 0 for t in R["per_t"])),
        ("R11 stacked minimum (R11 alone) above it at r11_dep.py's 75 K envelope", R["r11_pick"]["band"][0] > R["serv"]),
        ("the first round's allowance fails at 62.1 C with R16 in", R["old_per_t"][-1]["m_full"] < 0),
        ("C-1's recomputed allowance at 25 C at least the page's accepted %.2f mOhm" % (R["c1_prior"] * 1e3), R["r11_pick"]["tap"][2] >= R["c1_prior"]),
        ("R138's trip window above every PDO's current", all(R["w3"][0] > i for _v, i in R["pdo"])),
        ("R138's trip maximum below R138's, Q27's and the receptacle's ratings", R["w3"][1] < min(R["r138_rated"], R["q27_id"], R["rec_a"])),
    ]
    for lab, ok in acc_rows:
        P("   %-122s %s" % (lab, "PASS" if ok else "FAIL"))
    P("")
    P("5. INCONCLUSIVE, AND WHAT THE BENCH MUST STILL SHOW")
    P("   INCONCLUSIVE: C-7 (U3's minimum for the 10 mOhm RAC; the setting is CONDITIONAL on the INFERRED %.2f A); J_USBC_OUT's pin" % R["margin_inf"])
    P("     rating (no part); which VI(TRIP) row the strap selects (the maker's label conflict; bench (a) decides it); R11's and")
    P("     R16's actual temperatures (the 100 C stays an ASSUMPTION; the rise is the derating line's); the efficiencies (C-8)")
    P("   bench 7b.1: the front end's CC onset with an electronic load past U3, at -20, 25 and 62 C: above %.3f A at each" % R["serv"])
    P("   bench 7b.3: R11's Kelvin error, at most %.2f mOhm x I at 25 C (%.2f mV at %.3f A)" % (
        math.floor(R["r11_pick"]["tap"][2] * 1e5) / 100, math.floor(R["r11_pick"]["tap"][2] * 1e5) / 100 * R["serv"], R["serv"]))
    P("   C-7: at the %.2f A setting, the input current by a reference meter at or above %.2f A x 10 mOhm / R16 measured four-wire" % (
        R["setting"], R["u3min_ctrl"]))
    P("     (at least %.3f A over R16's envelope), and at or above the window's %.3f A" % (R["u3min_inf"], R["req"]))
    P("   the outlet: bench (a) and (b) of section 3")
    P("")
    P("END. Desk figures on the makers' pages, the committed netlist and the reproduced records; nothing measured or implemented.")
    return o


def main():
    R = compute()
    sys.stdout.write("\n".join(render(R)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
