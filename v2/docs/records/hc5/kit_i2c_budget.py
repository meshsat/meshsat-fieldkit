#!/usr/bin/env python3
"""Kit I2C bus budget: speed, pull-ups and line capacitance of the bus the panel controller masters across boards A, B,
C and D (MESHSAT-1357, layer 5 closer hc5, 27 September 2026). A desk calculation on published figures; the MeshSat
field kit V2 is a prototype design, nothing has been built, powered or measured. v2/docs/HW-FW-CONTRACT.md section 6
reports what this prints.

WHAT IT READS
  * the SDA and SCL nets of the four netlists (KiCad 9 export), so every pin on the bus is counted from the design and
    not from a list typed in: v2/ecad/pcb-{a-power-a23,b-compute-b19,c-display-c8,d-aprs-d9}/out/*.net under --root,
    board D optionally from --d-netlist (round 8's netlist adds the ADS1115 U22);
  * the copper already laid on SDA and SCL in the committed board files (A32, B21, C24, D12), as an indicator only:
    those layouts predate the corrected netlists and board B's is not fully routed;
  * nothing else: every figure below carries its source in the table that holds it.

EVIDENCE WORDS: VERIFIED = read in the maker's document or the netlist; INFERRED = arithmetic or reasoning on verified
figures; BOUND = the published maximum, or UM10204's 10 pF per pin where the maker publishes no maximum.

Usage:  python3 kit_i2c_budget.py [--root REPO] [--d-netlist PATH] [--no-copper]
Stdlib only. Read-only: it writes nothing."""
import argparse, math, os, re, sys

# ----------------------------------------------------------------------------------------------------------------------
# Sources (each held in the tree unless marked)
SRC = {
    "UM10204": "NXP UM10204 Rev. 6 (4 April 2014), I2C-bus specification: Table 9 p.47 (Ci 10 pF max per I/O pin), "
               "Table 10 p.48 (tr 1000 ns Standard-mode, 300 ns Fast-mode; Cb 400 pF), section 7.1 p.55 (T = 0.8473 RC), "
               "section 7.2 (buffers divide bus capacitance); fetched via web.archive.org id_ of nxp.com, sha256 b7619700e8bb9dd4",
    "PCA9555": "TI SCPS131J, 6.5: CI SCL 3 typ 8 max pF, Cio SDA 3 typ 9.5 max pF; IOL SDA 3 mA at VOL 0.4 V; standard-mode tr 1000 ns",
    "INA226": "TI SBOS547 (v2/vendor/ti/ti-ina226.pdf): input capacitance 3 pF (typ only); VOL 0.4 V at 3 mA; tR 1000 ns for SCLK <= 100 kHz",
    "BQ25731": "TI SLUSE66A 8.5 and 8.6 (v2/vendor/ti/bq25731-datasheet.pdf): no pin capacitance; VIN_LO 0.4 V max, VIN_HI 1.3 V min; "
               "SDA 0.4 V at 5 mA; timing requirements tr 300 ns, tf 300 ns, fSCL 10 to 400 kHz (one column, any clock); bus timeout 25 to 35 ms",
    "KSZ9897": "Microchip DS00002330E (v2/vendor/cluster/ksz9897.pdf): SCL IPU, SDA IPU/O8, internal pull-up 58 k +-30 %; external 1.0 to 4.7 k "
               "required; address fixed 0x5F; no pin capacitance published",
    "TMP117": "TI (v2/vendor/ti/ti-tmp117-temperature.pdf): input capacitance 4 pF (typ only); VOL 0.4 V at 3 mA; tR 1000 ns for SCL <= 100 kHz",
    "STM32H743": "ST DS12110 (v2/vendor/st/st-stm32h743xi-datasheet.pdf): CIO I/O pin capacitance 5 pF (typ only)",
    "TPS23861": "TI SLUSBX9I (v2/vendor/ti/tps23861-datasheet.pdf): CI2C SCL 10 pF, CI2C_SDA SDAI and SDAO 6 pF (max column); input rise "
                "time 0.8 to 2.3 V at most 300 ns (SDAI and SCL); fSCL 10 to 400 kHz",
    "ATECC608B": "Microchip DS40002239B summary (v2/vendor/microchip/microchip-atecc608b-summary-DS40002239B.pdf) Table 2-4: input rise "
                 "time 300 ns, input fall time 100 ns (characterised), fSCL 0 to 1 MHz; IOL 4 mA at VOL 0.4 V; no pin capacitance",
    "DS3231": "ADI 19-5170 Rev 10 (v2/vendor/adi/adi-ds3231.pdf): CBIN 10 pF (max); VOL 0.4 V at 3 mA; its timing table is fast mode and it "
              "is backward-compatible with standard mode (note 6)",
    "RP2040": "Raspberry Pi RP2040 datasheet (v2/vendor/rp2040/rpi-rp2040-datasheet.pdf): no pin capacitance published",
    "USBLC6": "ST USBLC6-2 (v2/vendor/st/st-usblc6-2-esd-protection.pdf): Ci/o-GND 2.5 typ 3.5 max pF at VR 1.65 V (per line)",
    "VEML7700": "Vishay VEML7700 (v2/vendor/vishay/veml7700-datasheet.pdf): no pin capacitance; Vil 0.4 V max at VDD 3.3 V; IOL 3 mA; "
                "standard-mode t(R) 1000 ns",
    "ADS1115": "TI SBAS444E (round 8, v2/vendor/ti/ti-ads1115-sbas444e.pdf on fnd/r8int1): no pin capacitance; VOL 0.4 V at 3 mA; "
               "tR 300 ns in its 0.01 to 0.4 MHz column",
    "TCA9517A": "TI SCPS245E (v2/vendor/ti/ti-tca9517a-i2c-buffer.pdf): CI and CIO 8 typ 13 max pF at 3.3 V; each side up to 400 pF; "
                "B side buffered low 0.45 to 0.6 V, VILc 0.45 V; A side hard low 0.1 to 0.2 V at 6 mA; A sides may join; never B side "
                "to B side; I/Os high impedance unpowered",
    "3M3365": "3M TS-0080-B (7 May 2009), 3365 series 0.050 in round-conductor flat cable, 28 AWG: 47.5 pF/m unbalanced (G-S-G), "
              "26.7 pF/m balanced; fetched from multimedia.3m.com, sha256 1dc900fe684bd6c2",
}

# Per-pin capacitance on ONE line, pF: (maker max or None, maker typ or None) for SDA and for SCL, and the source key.
PARTS = [
    (r"^PCA9555", "PCA9555 expander", (9.5, 3.0), (8.0, 3.0), "PCA9555"),
    (r"^INA226", "INA226 monitor", (None, 3.0), (None, 3.0), "INA226"),
    (r"^BQ25731", "BQ25731 charger", (None, None), (None, None), "BQ25731"),
    (r"KSZ9897", "KSZ9897R switch", (None, None), (None, None), "KSZ9897"),
    (r"^TMP117", "TMP117 sensor", (None, 4.0), (None, 4.0), "TMP117"),
    (r"^STM32H74", "STM32H743 supervisor", (None, 5.0), (None, 5.0), "STM32H743"),
    (r"TPS23861", "TPS23861 PoE PSE", (6.0, None), (10.0, None), "TPS23861"),
    (r"^ATECC608B", "ATECC608B secure element", (None, None), (None, None), "ATECC608B"),
    (r"^DS3231", "DS3231 clock", (10.0, None), (10.0, None), "DS3231"),
    (r"^RP2040", "RP2040 panel controller (master)", (None, None), (None, None), "RP2040"),
    (r"^USBLC6", "USBLC6-2SC6 ESD array (one line)", (3.5, 2.5), (3.5, 2.5), "USBLC6"),
    (r"VEML7700", "VEML7700 light sensor", (None, None), (None, None), "VEML7700"),
    (r"^ADS1115", "ADS1115 ADC", (None, None), (None, None), "ADS1115"),
]
UM_CI = 10.0          # pF, UM10204 Table 9: the most a compliant I/O pin may present
TP_PF = (1.0, 0.5)    # pF per test-point pad (bound, nominal): INFERRED, no held figure
CONN_PF = (2.0, 1.0)  # pF per IDC header end on the line (bound, nominal): INFERRED, no held figure
TCA_PF = (13.0, 8.0)  # pF per TCA9517A I/O (max, typ), SCPS245E
RIBBON_PF_PER_M = 47.5  # 3M 3365 unbalanced (G-S-G); SDA and SCL sit beside each other and a ground in every ribbon
RIBBONS = [("J_PANEL", "B J_PANEL to C J_PANEL", 350.0), ("J_AB1", "A J_AB1 to B J_AB1", 80.0),
           ("J_MEZZ1", "A J_MEZZ1 to D J_HARN1", 60.0)]   # lengths: v2/docs/ASSEMBLY.md section 4, pcb_interfaces.yaml
CU_PF_PER_CM = (1.0, 1.6, 2.2)  # low, nominal, high: INFERRED (IPC-2141 closed form for a 0.25 mm outer track over the
                                # 0.0994 mm 3313 prepreg gives about 1.7; 7628's 0.21 mm prepreg about 1.1; inner layers
                                # between planes toward 2.2); a solver reading (impedance_2d.py's atlc) is owed at layout
VDD = (3.20, 3.30, 3.40)        # pull-up rails, 3.3 V +-3 % (INFERRED: AP63203 0.8 V +-1 % reference, TLV75533, TPS62933 divider)
KSZ_RPU = (58e3 * 0.7, 58e3, 58e3 * 1.3)
SINK_MA = 3.0                   # the weakest sink on the bus: PCA9555, INA226, TMP117, DS3231, VEML7700, ADS1115, 3 mA at 0.4 V
TR_NS = 300.0                   # BQ25731, TPS23861, ATECC608B (and round 8's ADS1115) state 300 ns at any clock they accept

BOARDS = {"a": "pcb-a-power-a23/out/pcb-a-power.net", "b": "pcb-b-compute-b19/out/pcb-b-compute.net",
          "c": "pcb-c-display-c8/out/pcb-c-display.net", "d": "pcb-d-aprs-d9/out/pcb-d-aprs.net"}
LAYOUTS = {"a": "pcb-a-power-a23/pcb-a-power.kicad_pcb", "b": "pcb-b-compute-b19/pcb-b-compute.kicad_pcb",
           "c": "pcb-c-display-c8/pcb-c-display.kicad_pcb", "d": "pcb-d-aprs-d9/pcb-d-aprs.kicad_pcb"}


def parse_net(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    val = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt))
    nets = {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\(net \(code|\Z)', txt, re.S):
        nets[m.group(1).lstrip("/")] = sorted(set(re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2))))
    return val, nets


def copper_mm(path, name):
    """Track length (mm) and via count of net `name` in a KiCad 9 board file; None when the file is absent."""
    if not os.path.exists(path): return None
    t = open(path, encoding="utf-8", errors="replace").read()
    netmap = dict(re.findall(r'\(net (\d+) "([^"]*)"\)', t))
    def is_ours(tok):
        nm = tok.strip('"') if tok.startswith('"') else netmap.get(tok, "")
        return nm.lstrip("/") == name
    L = 0.0
    for x1, y1, x2, y2, net in re.findall(r'\(segment\s+\(start ([-\d.]+) ([-\d.]+)\)\s+\(end ([-\d.]+) ([-\d.]+)\)\s+\(width [\d.]+\)'
                                          r'\s+\(layer "[^"]+"\)\s+\(net (\d+|"[^"]*")\)', t):
        if is_ours(net): L += math.hypot(float(x2) - float(x1), float(y2) - float(y1))
    vias = sum(1 for m in re.finditer(r'\(via\b.*?\(net (\d+|"[^"]*")\)', t, re.S) if is_ours(m.group(1)))
    return L, vias


def classify(ref, value):
    for pat, name, sda, scl, src in PARTS:
        if re.search(pat, value): return name, sda, scl, src
    return None


def pin_pf(pair):
    mx, ty = pair
    return (mx if mx is not None else UM_CI, ty if ty is not None else (mx if mx is not None else UM_CI))


def inventory(root, d_override):
    """{line: [(board, ref, pin, kind, bound, nominal, what)]} and the pull-ups found."""
    inv = {"SDA": [], "SCL": []}; pulls = {"SDA": [], "SCL": []}; seen_line_parts = set()
    for b, rel in BOARDS.items():
        path = d_override if (b == "d" and d_override) else os.path.join(root, "v2/ecad", rel)
        val, nets = parse_net(path)
        for line in ("SDA", "SCL"):
            for ref, pin in nets.get(line, []):
                v = val.get(ref, "")
                if ref.startswith("TP"):
                    inv[line].append((b, ref, pin, "tp", TP_PF[0], TP_PF[1], "test point")); continue
                if ref.startswith("J"):
                    inv[line].append((b, ref, pin, "conn", CONN_PF[0], CONN_PF[1], "IDC header end")); continue
                if ref.startswith("R"):
                    other = [n for n, nodes in nets.items() if (ref, "1" if pin == "2" else "2") in nodes]
                    pulls[line].append((b, ref, v, other[0] if other else "?")); continue
                c = classify(ref, v)
                if not c:
                    inv[line].append((b, ref, pin, "unknown", UM_CI, UM_CI, v[:60])); continue
                name, sda, scl, src = c
                key = (b, ref, line)
                if src == "USBLC6" and key in seen_line_parts: continue    # flow-through pins of one line: one diode pair
                seen_line_parts.add(key)
                bound, nom = pin_pf(sda if line == "SDA" else scl)
                inv[line].append((b, ref, pin, src, bound, nom, name))
    return inv, pulls


def par(*rs): return 1.0 / sum(1.0 / r for r in rs)


def rp_window(pullups, tol=0.05):
    """(Rp for the sink check, Rp nominal, Rp for the rise check), ohm, with the KSZ9897R's internal pull-up in parallel."""
    vals = [float(v.lower().replace("k", "")) * 1e3 for _, _, v, _ in pullups]
    lo = par(*[r * (1 - tol) for r in vals], KSZ_RPU[0])
    no = par(*vals, KSZ_RPU[1])
    hi = par(*[r * (1 + tol) for r in vals], KSZ_RPU[2])
    return lo, no, hi


def cb_max(rp, vdd, metric):
    """Largest bus capacitance (pF) whose rise meets TR_NS through rp from vdd. metric 'um': 30 to 70 % of VDD (UM10204
    7.1, 0.8473 RC); 'tps': the TPS23861's fixed 0.8 V to 2.3 V."""
    k = 0.8473 if metric == "um" else math.log((vdd - 0.8) / (vdd - 2.3))
    return TR_NS * 1e-9 / (k * rp) * 1e12


def main(a):
    root = os.path.abspath(a.root)
    inv, pulls = inventory(root, a.d_netlist)
    out = []
    p = out.append
    p("KIT I2C BUS BUDGET (desk calculation, prototype design, nothing built)")
    p("netlists: " + ", ".join("%s=%s" % (b, (a.d_netlist if (b == "d" and a.d_netlist) else "v2/ecad/" + r)) for b, r in BOARDS.items()))
    p("")
    tot = {}
    for line in ("SDA", "SCL"):
        rows = inv[line]
        p("== %s: %d pins on the line" % (line, len(rows)))
        by = {}
        for b, ref, pin, kind, bd, nm, what in rows:
            by.setdefault(b, []).append((ref, pin, kind, bd, nm, what))
        for b in sorted(by):
            s_b = sum(x[3] for x in by[b]); s_n = sum(x[4] for x in by[b])
            p("   board %s: bound %.1f pF, nominal %.1f pF: %s" % (b.upper(), s_b, s_n,
              ", ".join("%s.%s %s" % (r, pn, k) for r, pn, k, _, _, _ in sorted(by[b]))))
        dev_b = sum(x[4] for x in rows); dev_n = sum(x[5] for x in rows)
        rib = sum(L for _, _, L in RIBBONS) / 1000.0 * RIBBON_PF_PER_M
        tot[line] = (dev_b, dev_n, rib)
        p("   pins total: bound %.1f pF, nominal %.1f pF; ribbons %.0f mm at %.1f pF/m = %.1f pF"
          % (dev_b, dev_n, sum(L for _, _, L in RIBBONS), RIBBON_PF_PER_M, rib))
        p("   pull-ups: " + ", ".join("%s %s %s to %s" % (b.upper(), r, v, o) for b, r, v, o in pulls[line])
          + "; plus the KSZ9897R's internal 58 k +-30 %")
    p("")
    lo, no, hi = rp_window(pulls["SDA"])
    p("== Pull-up window (SDA; SCL identical)")
    p("   effective Rp: %.0f ohm at -5 %% (sink check), %.0f nominal, %.0f at +5 %% (rise check)" % (lo, no, hi))
    rpmin = (VDD[2] - 0.4) / (SINK_MA * 1e-3)
    p("   Rp minimum for a 3 mA sink at VOL 0.4 V from %.2f V: %.0f ohm (UM10204 7.1); the drawn %.0f ohm %s"
      % (VDD[2], rpmin, lo, "meets it" if lo >= rpmin else "is BELOW it"))
    p("   pull-up current at 0.4 V: %.2f mA worst (%.2f V over %.0f ohm), %.2f mA nominal"
      % ((VDD[2] - 0.4) / lo * 1e3, VDD[2], lo, (VDD[1] - 0.4) / no * 1e3))
    cb_um = cb_max(hi, VDD[1], "um"); cb_tps = cb_max(hi, VDD[0], "tps")
    cb_um_n = cb_max(no, VDD[1], "um"); cb_tps_n = cb_max(no, VDD[1], "tps")
    p("   largest Cb for tr <= %.0f ns: %.0f pF (30-70 %%, BQ25731, ATECC608B, ADS1115) and %.0f pF (TPS23861's 0.8-2.3 V at %.2f V)"
      " at the rise-check Rp; %.0f and %.0f pF at nominal" % (TR_NS, cb_um, cb_tps, VDD[0], cb_um_n, cb_tps_n))
    p("   Standard-mode alone (tr 1000 ns, 30-70 %%) would allow %.0f pF; UM10204's Cb limit is 400 pF"
      % (1000e-9 / (0.8473 * hi) * 1e12))
    limit_b, limit_n = min(cb_um, cb_tps), min(cb_um_n, cb_tps_n)
    p("")
    # --- copper as laid on the committed (older) layouts
    cu = {}
    if not a.no_copper:
        p("== Copper already laid on SDA and SCL in the committed board files (INDICATOR: A32, B21, C24, D12 predate the")
        p("   corrected netlists; B21 is not fully routed, so board B's figure is a floor)")
        for b, rel in LAYOUTS.items():
            for line in ("SDA", "SCL"):
                r = copper_mm(os.path.join(root, "v2/ecad", rel), line)
                if r: cu[(b, line)] = r
            if (b, "SDA") in cu:
                p("   board %s: SDA %.0f mm (%d vias), SCL %.0f mm (%d vias)" % (b.upper(), cu[(b, "SDA")][0], cu[(b, "SDA")][1],
                  cu.get((b, "SCL"), (0, 0))[0], cu.get((b, "SCL"), (0, 0))[1]))
        p("")
    # --- one segment, as drawn
    p("== ONE SEGMENT, as drawn (trunk = the whole bus): fixed part and the copper it leaves")
    for line in ("SDA", "SCL"):
        dev_b, dev_n, rib = tot[line]
        fb, fn = dev_b + rib, dev_n + rib
        L = sum(cu.get((b, line), (0, 0))[0] for b in BOARDS) if cu else 0.0
        p("   %s: fixed %.0f pF bound / %.0f pF nominal against %.0f / %.0f pF allowed: copper allowance %.0f / %.0f pF"
          % (line, fb, fn, limit_b, limit_n, limit_b - fb, limit_n - fn))
        if L:
            p("       the committed layouts carry %.0f mm: %.0f to %.0f pF at %.1f to %.1f pF/cm; total %.0f to %.0f pF (nominal pins, low"
              " copper) up to %.0f pF (bound pins, high copper)" % (L, L / 10 * CU_PF_PER_CM[0], L / 10 * CU_PF_PER_CM[2],
              CU_PF_PER_CM[0], CU_PF_PER_CM[2], fn + L / 10 * CU_PF_PER_CM[0], fn + L / 10 * CU_PF_PER_CM[1],
              fb + L / 10 * CU_PF_PER_CM[2]))
    p("   RESULT: the fixed part alone uses %.0f to %.0f %% of the rise-limited capacitance, and the laid copper exceeds what"
      % ((tot["SDA"][1] + tot["SDA"][2]) / limit_n * 100, (tot["SDA"][0] + tot["SDA"][2]) / limit_b * 100))
    p("   is left at every per-length figure in the range; the bus as one segment cannot meet the 300 ns rise its own")
    p("   targets require, and the drawn pull-ups cannot be made stronger (3 mA sinks). The bound includes failure.")
    p("")
    # --- three segments (the session's choice SC-HF-02)
    p("== THREE SEGMENTS (session choice SC-HF-02): the trunk (the master, board C, and on board B the expanders, the")
    p("   secure element, the clock and the temperature sensor); SEG-A, boards A and D behind a TCA9517A on A (its A side")
    p("   local, its B side on the trunk, enabled always); SEG-S, board B's three supervisors, PoE controller and Ethernet")
    p("   switch behind a TCA9517A on B (its A side on the trunk, its B side theirs, enabled only while the panel opens it)")
    SEGS = ("U41", "U51", "U61", "U5", "U1")
    seg_def = {
        "TRUNK": lambda b, ref: (b == "c") or (b == "b" and ref not in SEGS) or ref == "J_AB1",
        "SEG-A": lambda b, ref: b in ("a", "d") and ref != "J_AB1",
        "SEG-S": lambda b, ref: b == "b" and ref in SEGS,
    }
    seg_ribbon = {"TRUNK": ["J_PANEL", "J_AB1"], "SEG-A": ["J_MEZZ1"], "SEG-S": []}
    seg_tca = {"TRUNK": 2, "SEG-A": 1, "SEG-S": 1}   # buffer I/Os on each segment's line
    # proposed pull-ups (session choice): SEG-A 1.2 k to A's +3V3, SEG-S 2.2 k to +3V3_DEV; the trunk keeps B's and C's 2.2 k
    # the KSZ9897R's internal 58 k moves with it to SEG-S; the trunk keeps B's and C's 2.2 k alone
    t_hi, t_no = par(2.2e3 * 1.05 / 2), par(2.2e3 / 2)
    s_hi, s_no = par(1.5e3 * 1.05, KSZ_RPU[2]), par(1.5e3, KSZ_RPU[1])
    seg_rp = {"TRUNK": (t_hi, t_no, "um"), "SEG-A": (1.2e3 * 1.05, 1.2e3, "um"), "SEG-S": (s_hi, s_no, "tps")}
    for line in ("SDA", "SCL"):
        for seg, member in seg_def.items():
            rows = [x for x in inv[line] if member(x[0], x[1]) and x[3] not in ("conn",)]
            conns = [x for x in inv[line] if x[3] == "conn" and member(x[0], x[1])]
            rib_mm = sum(L for n, _, L in RIBBONS if n in seg_ribbon[seg])
            fb = sum(x[4] for x in rows) + sum(x[4] for x in conns) + rib_mm / 1000 * RIBBON_PF_PER_M + seg_tca[seg] * TCA_PF[0]
            fn = sum(x[5] for x in rows) + sum(x[5] for x in conns) + rib_mm / 1000 * RIBBON_PF_PER_M + seg_tca[seg] * TCA_PF[1]
            rp_hi, rp_no, metric = seg_rp[seg]
            lb = cb_max(rp_hi, VDD[0] if metric == "tps" else VDD[1], metric); ln = cb_max(rp_no, VDD[1], metric)
            p("   %s %s: %d pins; fixed %.0f pF bound / %.0f nominal; limit %.0f / %.0f pF (Rp %.0f / %.0f ohm, %s); copper"
              " allowance %.0f pF bound, %.0f nominal = %.0f mm at %.1f pF/cm (bound) to %.0f mm at %.1f pF/cm (nominal)"
              % (seg, line, len(rows), fb, fn, lb, ln, rp_hi, rp_no, "TPS23861 0.8-2.3 V" if metric == "tps" else "30-70 %",
                 lb - fb, ln - fn, max(0.0, (lb - fb)) / CU_PF_PER_CM[2] * 10, CU_PF_PER_CM[2],
                 max(0.0, (ln - fn)) / CU_PF_PER_CM[1] * 10, CU_PF_PER_CM[1]))
    p("   Sink check: trunk 2.2 k || 2.2 k from %.2f V at -5 %% draws %.2f mA; SEG-A 1.2 k %.2f mA; SEG-S 1.5 k || 58 k %.2f mA;"
      " all under the 3 mA of the weakest sink on each segment" % (VDD[2], (VDD[2] - 0.4) / (1.1e3 * 0.95) * 1e3,
      (VDD[2] - 0.4) / (1.2e3 * 0.95) * 1e3, (VDD[2] - 0.4) / par(1.5e3 * 0.95, KSZ_RPU[0]) * 1e3))
    p("   Levels across the buffers (SCPS245E): SEG-A's BQ25731 (VIN_LO 0.4 V) sits on U_A's A side and sees hard lows;")
    p("   SEG-S's parts all read 0.9 V or more as low (TPS23861 0.9 V, KSZ9897R 0.9 V, STM32 0.3 VDD), above U_S's buffered")
    p("   0.6 V; on the trunk the ATECC608B (VIL 0.5 V) and the VEML7700 (0.4 V) see U_A's buffered low only in bits another")
    p("   target drives, never in a START, STOP or their own address (INFERRED, bench V-K03)")
    p("")
    p("SOURCES")
    for k, v in SRC.items(): p("   %s: %s" % (k, v))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
    ap.add_argument("--d-netlist", default=None, help="board D's netlist to read instead of the committed one (round 8)")
    ap.add_argument("--no-copper", action="store_true")
    sys.exit(main(ap.parse_args()))
